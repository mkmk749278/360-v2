"""Tests for src.trade_monitor – minimum lifespan and SL/TP evaluation."""

from __future__ import annotations

from datetime import timedelta
from typing import Dict
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.channels.base import Signal
from src.smc import Direction
from src.trade_monitor import TradeMonitor
from src.utils import utcnow


def _make_signal(
    channel: str = "360_SCALP",
    symbol: str = "BTCUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 30000.0,
    stop_loss: float = 29850.0,
    tp1: float = 30150.0,
    tp2: float = 30300.0,
    tp3: float = 30450.0,
    signal_id: str = "TEST-SIG-001",
    age_seconds: float = 0.0,
) -> Signal:
    sig = Signal(
        channel=channel,
        symbol=symbol,
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=tp2,
        confidence=85.0,
        signal_id=signal_id,
    )
    sig.tp3 = tp3
    # Backdate the timestamp to simulate a signal of `age_seconds` old
    if age_seconds > 0:
        sig.timestamp = utcnow() - timedelta(seconds=age_seconds)
    return sig


def _make_get_candles_from_active(active: Dict[str, "Signal"]):
    """Build a `data_store.get_candles` side_effect that returns a synthetic
    1m candle reflecting each active signal's `current_price`.

    The trade monitor evaluates SL/TP against 1m candle high/low (per the
    audit-2 fix in `_check_sl_tp`).  Pre-cleanup the test mocks returned
    `None` and the monitor fell back to `_latest_price` → empty ticks → 0.0
    high/low → SL/TP checks short-circuited because of the `_c_low > 0`
    guard.  This helper makes the mock 1m candle reflect the test's intent
    via `sig.current_price` so SL/TP tests trigger correctly.
    """
    def _get_candles(symbol: str, interval: str):
        if interval != "1m":
            return None
        # Find the signal whose symbol matches.
        matching = next(
            (s for s in active.values() if getattr(s, "symbol", None) == symbol),
            None,
        )
        if matching is None:
            return None
        p = float(getattr(matching, "current_price", 0.0))
        if p <= 0:
            return None
        # Synthetic 1m candle: high/low/close/open all = current_price so any
        # SL/TP check resolves to "candle reached current_price".
        return {
            "high": [p],
            "low": [p],
            "close": [p],
            "open": [p],
            "volume": [1000.0],
        }
    return _get_candles


class TestMinimumLifespan:
    """The monitor must NOT trigger SL/TP checks for very new signals."""

    def _build_monitor(self, active: Dict[str, Signal]):
        removed = []
        sent = []

        async def mock_send(chat_id, text):
            sent.append((chat_id, text))

        data_store = MagicMock()
        data_store.get_candles.side_effect = _make_get_candles_from_active(active)
        data_store.ticks = {}

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.append(sid),
            update_signal=MagicMock(),
        )
        return monitor, removed, sent

    @pytest.mark.asyncio
    async def test_sl_not_triggered_within_min_lifespan(self):
        """Brand-new SCALP signal (age=0) below SL should NOT be removed."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=0.0,  # just created
        )
        # Set current price below stop loss to simulate SL condition
        sig.current_price = 29800.0

        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor(active)

        await monitor._evaluate_signal(sig)

        # Signal must NOT be removed because the min lifespan hasn't passed
        assert sig.signal_id not in removed
        assert sig.status == "ACTIVE"

    @pytest.mark.asyncio
    async def test_sl_triggered_after_min_lifespan(self):
        """A SCALP signal older than 180s whose price is below SL SHOULD be removed."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=200.0,  # past the 180s SCALP minimum
        )
        sig.current_price = 29800.0  # below SL

        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor(active)

        await monitor._evaluate_signal(sig)

        assert sig.signal_id in removed
        assert sig.status == "SL_HIT"
        assert sig.current_price == pytest.approx(29850.0)

    @pytest.mark.asyncio
    async def test_scalp_fvg_min_lifespan_is_respected(self):
        """A SCALP_FVG signal at age=15s (< 180s min) should NOT trigger SL."""
        sig = _make_signal(
            channel="360_SCALP_FVG",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=15.0,  # below the 300s SWING minimum
        )
        sig.current_price = 29800.0  # below SL

        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor(active)

        await monitor._evaluate_signal(sig)

        assert sig.signal_id not in removed
        assert sig.status == "ACTIVE"

    @pytest.mark.asyncio
    async def test_tp_not_triggered_within_min_lifespan(self):
        """TP1 should NOT fire on a brand-new signal even if price reaches TP."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            age_seconds=0.0,
        )
        sig.current_price = 30200.0  # above TP1

        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor(active)

        await monitor._evaluate_signal(sig)

        assert sig.status == "ACTIVE"


class TestOutcomeRecording:
    """TradeMonitor must call performance_tracker and circuit_breaker on final outcomes."""

    def _build_monitor_with_mocks(self, active: Dict[str, Signal]):
        """Build a TradeMonitor wired with mock performance_tracker and circuit_breaker."""
        removed = []
        sent = []

        async def mock_send(chat_id, text):
            sent.append((chat_id, text))

        data_store = MagicMock()
        data_store.get_candles.side_effect = _make_get_candles_from_active(active)
        data_store.ticks = {}

        performance_tracker = MagicMock()
        circuit_breaker = MagicMock()

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.append(sid),
            update_signal=MagicMock(),
            performance_tracker=performance_tracker,
            circuit_breaker=circuit_breaker,
        )
        return monitor, removed, sent, performance_tracker, circuit_breaker

    def _build_monitor_with_wick_candles(
        self,
        active: Dict[str, Signal],
        *,
        high: float,
        low: float,
        close: float,
    ):
        """Build a monitor whose ``get_candles('1m')`` returns a synthetic
        candle with explicit high/low/close — used to reproduce the
        wick-through-TP scenario."""
        removed = []
        sent = []

        async def mock_send(chat_id, text):
            sent.append((chat_id, text))

        candle = {
            "open": [close],
            "high": [high],
            "low": [low],
            "close": [close],
            "volume": [1000.0],
        }

        data_store = MagicMock()
        data_store.get_candles.side_effect = (
            lambda symbol, interval: candle if interval == "1m" else None
        )
        data_store.ticks = {}

        # Set sig.current_price to the candle CLOSE so MFE/PnL use close;
        # this matches production: ``current_price`` is fed by ``_latest_price``
        # which returns the last 1m close.
        for sig in active.values():
            sig.current_price = close

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.append(sid),
            update_signal=MagicMock(),
            performance_tracker=MagicMock(),
            circuit_breaker=MagicMock(),
        )
        return monitor, removed, sent

    # ------------------------------------------------------------------
    # Wick-aware TP1 / TP2 fills (regression for 2026-05-09 bug:
    # TP1 / TP2 used 1m candle CLOSE while TP3 + SL used 1m HIGH/LOW —
    # bars where price wicked through TP1 then retraced were marked
    # EXPIRED instead of TP1_HIT, contributing to the 0% win rate).
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_long_tp1_fires_on_wick_even_when_close_below_tp1(self):
        """LONG: 1m bar high wicks through TP1, close back below.  TP1 must
        fire — Binance limit orders fill on wicks regardless of close."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,    # +0.5%
            tp2=30300.0,    # +1.0%
            tp3=30450.0,    # +1.5%
            age_seconds=200.0,
        )
        active = {sig.signal_id: sig}
        # Bar wicks to $30200 (well above TP1 = $30150) but closes back at
        # $30100 (below TP1).  Pre-fix: TP1 missed; post-fix: TP1 fires.
        monitor, _, _ = self._build_monitor_with_wick_candles(
            active, high=30200.0, low=29980.0, close=30100.0
        )
        await monitor._evaluate_signal(sig)
        assert sig.status == "TP1_HIT", (
            f"Wick-through-TP1 must fire TP1 (status was {sig.status})"
        )
        assert sig.best_tp_hit == 1

    @pytest.mark.asyncio
    async def test_long_tp2_fires_on_wick_even_when_close_below_tp2(self):
        """LONG: 1m bar high wicks through TP2, close back below TP2 but
        above TP1.  TP2 must fire."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=200.0,
        )
        active = {sig.signal_id: sig}
        # high $30350 (above TP2), close $30200 (between TP1 and TP2).
        monitor, _, _ = self._build_monitor_with_wick_candles(
            active, high=30350.0, low=30100.0, close=30200.0
        )
        await monitor._evaluate_signal(sig)
        assert sig.status == "TP2_HIT", (
            f"Wick-through-TP2 must fire TP2 (status was {sig.status})"
        )
        assert sig.best_tp_hit == 2

    @pytest.mark.asyncio
    async def test_short_tp1_fires_on_wick_even_when_close_above_tp1(self):
        """SHORT: 1m bar low wicks through TP1, close back above TP1."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.SHORT,
            entry=30000.0,
            stop_loss=30150.0,
            tp1=29850.0,    # -0.5%
            tp2=29700.0,    # -1.0%
            tp3=29550.0,    # -1.5%
            age_seconds=200.0,
        )
        active = {sig.signal_id: sig}
        # Bar wicks down to $29800 (below TP1) but closes back at $29900
        # (above TP1).  Pre-fix: TP1 missed; post-fix: TP1 fires.
        monitor, _, _ = self._build_monitor_with_wick_candles(
            active, high=30000.0, low=29800.0, close=29900.0
        )
        await monitor._evaluate_signal(sig)
        assert sig.status == "TP1_HIT", (
            f"Wick-through-TP1 must fire TP1 (status was {sig.status})"
        )
        assert sig.best_tp_hit == 1

    @pytest.mark.asyncio
    async def test_short_tp2_fires_on_wick_even_when_close_above_tp2(self):
        """SHORT: 1m bar low wicks through TP2, close back above TP2."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.SHORT,
            entry=30000.0,
            stop_loss=30150.0,
            tp1=29850.0,
            tp2=29700.0,
            tp3=29550.0,
            age_seconds=200.0,
        )
        active = {sig.signal_id: sig}
        # low $29650 (below TP2), close $29800 (between TP1 and TP2).
        monitor, _, _ = self._build_monitor_with_wick_candles(
            active, high=30000.0, low=29650.0, close=29800.0
        )
        await monitor._evaluate_signal(sig)
        assert sig.status == "TP2_HIT", (
            f"Wick-through-TP2 must fire TP2 (status was {sig.status})"
        )
        assert sig.best_tp_hit == 2

    @pytest.mark.asyncio
    async def test_long_tp1_does_not_fire_when_no_wick_reaches_tp1(self):
        """Sanity: when neither high nor close reaches TP1, no TP fires."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=200.0,
        )
        active = {sig.signal_id: sig}
        monitor, _, _ = self._build_monitor_with_wick_candles(
            active, high=30100.0, low=29980.0, close=30050.0
        )
        await monitor._evaluate_signal(sig)
        assert sig.status not in ("TP1_HIT", "TP2_HIT", "TP3_HIT")

    @pytest.mark.asyncio
    async def test_sl_takes_priority_over_tp_wick_in_same_bar(self):
        """If a single 1m bar wicks BOTH SL and TP1 (LONG: low <= SL AND
        high >= TP1), SL fires first — preserves the existing SL-first
        semantic and prevents fake TP wins on volatile spike-and-revert
        bars."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            age_seconds=200.0,
        )
        active = {sig.signal_id: sig}
        # Both barriers tagged in one candle.  Close > entry so the
        # zero-PnL guard at ``_evaluate_signal`` doesn't short-circuit.
        monitor, _, _ = self._build_monitor_with_wick_candles(
            active, high=30200.0, low=29800.0, close=30050.0
        )
        await monitor._evaluate_signal(sig)
        # SL is checked before TP in `_evaluate_signal`.
        assert sig.status in ("SL_HIT", "BREAKEVEN_EXIT", "PROFIT_LOCKED")

    @pytest.mark.asyncio
    async def test_sl_hit_calls_performance_tracker(self):
        """Losing stop exits must record a semantic SL_HIT outcome."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=200.0,
        )
        sig.setup_class = "BREAKOUT_RETEST"
        sig.market_phase = "STRONG_TREND"
        sig.quality_tier = "A"
        sig.pre_ai_confidence = 78.0
        sig.post_ai_confidence = 84.0
        sig.spread_pct = 0.008
        sig.volume_24h_usd = 12_000_000.0
        sig.current_price = 29800.0  # below SL

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        assert sig.status == "SL_HIT"
        pt.record_outcome.assert_called_once()
        call_kwargs = pt.record_outcome.call_args.kwargs
        assert call_kwargs["hit_sl"] is True
        assert call_kwargs["hit_tp"] == 0
        assert call_kwargs["signal_id"] == sig.signal_id
        assert call_kwargs["pnl_pct"] == pytest.approx(-0.5)
        assert call_kwargs["outcome_label"] == "SL_HIT"
        assert call_kwargs["setup_class"] == "BREAKOUT_RETEST"
        assert call_kwargs["market_phase"] == "STRONG_TREND"
        assert call_kwargs["quality_tier"] == "A"
        assert call_kwargs["pre_ai_confidence"] == 78.0
        assert call_kwargs["post_ai_confidence"] == 84.0
        assert call_kwargs["first_sl_touch_timestamp"] is not None
        assert call_kwargs["terminal_outcome_timestamp"] is not None
        assert call_kwargs["create_to_terminal_sec"] is not None
        assert call_kwargs["create_to_first_breach_sec"] is not None
        create_to_terminal_sec = call_kwargs["create_to_terminal_sec"]
        create_to_first_breach_sec = call_kwargs["create_to_first_breach_sec"]
        assert create_to_terminal_sec >= create_to_first_breach_sec

    @pytest.mark.asyncio
    async def test_lifecycle_outcome_callback_receives_signal_and_outcome(self):
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=200.0,
        )
        sig.setup_class = "FAILED_AUCTION_RECLAIM"
        sig.current_price = 29800.0  # below SL

        active = {sig.signal_id: sig}
        monitor, *_rest = self._build_monitor_with_mocks(active)
        monitor.on_lifecycle_outcome_callback = MagicMock()

        await monitor._evaluate_signal(sig)

        monitor.on_lifecycle_outcome_callback.assert_called_once_with(sig, "SL_HIT")

    @pytest.mark.asyncio
    async def test_sl_hit_calls_circuit_breaker(self):
        """SL_HIT must also notify circuit_breaker.record_outcome."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=200.0,
        )
        sig.current_price = 29800.0  # below SL

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        cb.record_outcome.assert_called_once()
        call_kwargs = cb.record_outcome.call_args.kwargs
        assert call_kwargs["hit_sl"] is True
        assert call_kwargs["signal_id"] == sig.signal_id

    @pytest.mark.asyncio
    async def test_tp3_hit_calls_performance_tracker(self):
        """Full TP completion must record a semantic FULL_TP_HIT outcome."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=200.0,
        )
        sig.current_price = 30500.0  # above TP3

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        assert sig.status == "FULL_TP_HIT"
        pt.record_outcome.assert_called_once()
        call_kwargs = pt.record_outcome.call_args.kwargs
        assert call_kwargs["hit_sl"] is False
        assert call_kwargs["hit_tp"] == 3
        assert call_kwargs["pnl_pct"] == pytest.approx(1.5)
        assert call_kwargs["outcome_label"] == "FULL_TP_HIT"
        assert sig.current_price == pytest.approx(30450.0)

    @pytest.mark.asyncio
    async def test_tp1_hit_does_not_call_record_outcome(self):
        """TP1_HIT must NOT call record_outcome — signal is still active."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=200.0,
        )
        sig.current_price = 30200.0  # above TP1 but below TP2

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        assert sig.status == "TP1_HIT"
        pt.record_outcome.assert_not_called()
        cb.record_outcome.assert_not_called()

    @pytest.mark.asyncio
    async def test_cancelled_invalid_sl_does_not_call_record_outcome(self):
        """CANCELLED (invalid SL) must NOT call record_outcome — not a real trade outcome."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=30100.0,  # invalid: SL above entry for LONG
            age_seconds=200.0,
        )
        sig.current_price = 30000.0

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        assert sig.status == "CANCELLED"
        pt.record_outcome.assert_not_called()
        cb.record_outcome.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_performance_tracker_does_not_raise(self):
        """Monitor without performance_tracker/circuit_breaker must not raise on SL_HIT."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=200.0,
        )
        sig.current_price = 29800.0

        removed = []
        sent = []

        async def mock_send(chat_id, text):
            sent.append((chat_id, text))

        active = {sig.signal_id: sig}
        data_store = MagicMock()
        data_store.get_candles.side_effect = _make_get_candles_from_active(active)
        data_store.ticks = {}

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.append(sid),
            update_signal=MagicMock(),
            # No performance_tracker or circuit_breaker — must not raise
        )

        await monitor._evaluate_signal(sig)

        assert sig.status == "SL_HIT"
        assert sig.signal_id in removed

    @pytest.mark.asyncio
    async def test_short_sl_uses_stop_price_for_realized_pnl(self):
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.SHORT,
            entry=30000.0,
            stop_loss=30150.0,
            tp1=29850.0,
            tp2=29700.0,
            tp3=29550.0,
            age_seconds=200.0,
        )
        sig.current_price = 30250.0

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        call_kwargs = pt.record_outcome.call_args.kwargs
        assert call_kwargs["pnl_pct"] == pytest.approx(-0.5)
        assert sig.current_price == pytest.approx(30150.0)
        assert sig.status == "SL_HIT"
        assert call_kwargs["outcome_label"] == "SL_HIT"

    @pytest.mark.asyncio
    async def test_short_tp3_uses_take_profit_price_for_realized_pnl(self):
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.SHORT,
            entry=30000.0,
            stop_loss=30150.0,
            tp1=29850.0,
            tp2=29700.0,
            tp3=29550.0,
            age_seconds=200.0,
        )
        sig.current_price = 29400.0

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        call_kwargs = pt.record_outcome.call_args.kwargs
        assert call_kwargs["pnl_pct"] == pytest.approx(1.5)
        assert call_kwargs["outcome_label"] == "FULL_TP_HIT"
        assert sig.current_price == pytest.approx(29550.0)
        assert sig.status == "FULL_TP_HIT"

    @pytest.mark.asyncio
    async def test_trailing_stop_break_even_records_zero_pnl(self):
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=200.0,
        )
        sig.status = "TP2_HIT"
        sig.stop_loss = sig.entry
        sig.current_price = 29900.0

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        call_kwargs = pt.record_outcome.call_args.kwargs
        assert call_kwargs["hit_sl"] is True
        assert call_kwargs["pnl_pct"] == pytest.approx(0.0)
        assert call_kwargs["outcome_label"] == "BREAKEVEN_EXIT"
        assert sig.status == "BREAKEVEN_EXIT"

    @pytest.mark.asyncio
    async def test_invalidated_close_records_outcome_label_as_invalidated(self, monkeypatch):
        """Regression for the historical "CLOSED" mis-labelling: when the
        invalidation gate fires, ``_record_outcome`` must stamp
        ``outcome_label="INVALIDATED"`` on the perf-tracker record — NOT
        derive ``"CLOSED"`` from ``(hit_tp=0, hit_sl=False)``.  Without
        this, the historical perf JSON labels every invalidation
        ``CLOSED`` and the Lumin app's Invalidated sub-filter shows
        empty.
        """
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=600.0,
        )
        sig.current_price = 29920.0  # mid-trade, not at SL

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)
        # Force invalidation — bypass the regime/indicators-driven trigger.
        monkeypatch.setattr(
            TradeMonitor, "_check_invalidation",
            lambda self, s: "momentum_loss test",
        )

        await monitor._evaluate_signal(sig)

        assert sig.status == "INVALIDATED"
        pt.record_outcome.assert_called_once()
        call_kwargs = pt.record_outcome.call_args.kwargs
        assert call_kwargs["outcome_label"] == "INVALIDATED"
        # hit_tp / hit_sl stay zero / False — they describe the close
        # *mechanism*, not the doctrinal classification.
        assert call_kwargs["hit_tp"] == 0
        assert call_kwargs["hit_sl"] is False

    @pytest.mark.asyncio
    async def test_expired_close_records_outcome_label_as_expired(self):
        """Companion regression — the expiry path also sets ``sig.status``
        explicitly, so the perf record must round-trip ``EXPIRED``.
        Uses ``age_seconds`` well past any plausible MAX_SIGNAL_HOLD so
        the test isn't fragile to other tests' monkeypatches of that
        config dict.
        """
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=100_000.0,  # ~28h, well past 3600s SCALP hold cap
        )
        sig.current_price = 30000.0

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        assert sig.status == "EXPIRED"
        call_kwargs = pt.record_outcome.call_args.kwargs
        assert call_kwargs["outcome_label"] == "EXPIRED"

    @pytest.mark.asyncio
    async def test_trailing_stop_profit_lock_is_not_reported_as_sl_hit(self):
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=200.0,
        )
        sig.status = "TP2_HIT"
        sig.stop_loss = 30120.0
        sig.current_price = 30090.0

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        call_kwargs = pt.record_outcome.call_args.kwargs
        assert call_kwargs["hit_sl"] is True
        assert call_kwargs["pnl_pct"] == pytest.approx(0.4)
        assert call_kwargs["outcome_label"] == "PROFIT_LOCKED"
        assert sig.status == "PROFIT_LOCKED"

    @pytest.mark.asyncio
    async def test_first_favorable_touch_is_preserved_separately_from_terminal_close(self, monkeypatch):
        base_time = utcnow()
        tick = {"n": 0}

        def _fake_utcnow():
            current = base_time + timedelta(seconds=tick["n"] * 5)
            tick["n"] += 1
            return current

        monkeypatch.setattr("src.trade_monitor.utcnow", _fake_utcnow)

        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=0.0,
        )
        sig.timestamp = base_time - timedelta(seconds=220)
        sig.dispatch_timestamp = base_time - timedelta(seconds=210)

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        sig.current_price = 30200.0  # TP1 touch (non-terminal)
        await monitor._evaluate_signal(sig)
        assert sig.status == "TP1_HIT"

        sig.current_price = 29900.0  # retrace to moved stop (terminal)
        await monitor._evaluate_signal(sig)

        call_kwargs = pt.record_outcome.call_args.kwargs
        assert call_kwargs["first_tp_touch_timestamp"] is not None
        assert call_kwargs["first_sl_touch_timestamp"] is not None
        assert call_kwargs["first_breach_timestamp"] == call_kwargs["first_tp_touch_timestamp"]
        assert call_kwargs["first_breach_to_terminal_sec"] is not None
        assert call_kwargs["first_breach_to_terminal_sec"] > 0.0
        assert call_kwargs["create_to_first_breach_sec"] is not None
        assert call_kwargs["create_to_terminal_sec"] is not None
        create_to_first_breach_sec = call_kwargs["create_to_first_breach_sec"]
        create_to_terminal_sec = call_kwargs["create_to_terminal_sec"]
        assert create_to_first_breach_sec < create_to_terminal_sec


class TestTrailingStopAfterTP2:
    """Trailing stop must continue to advance after TP2 moves SL to break-even."""

    def _build_monitor(self, active: Dict[str, Signal]):
        removed = []
        sent = []

        async def mock_send(chat_id, text):
            sent.append((chat_id, text))

        data_store = MagicMock()
        data_store.get_candles.side_effect = _make_get_candles_from_active(active)
        data_store.ticks = {}

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.append(sid),
            update_signal=MagicMock(),
        )
        return monitor, removed

    @pytest.mark.asyncio
    async def test_trailing_stop_advances_after_tp2(self):
        """After TP2 sets SL to TP1, the trailing stop should still move up with price."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,  # original SL → original_sl_distance = 150
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=60.0,
        )
        # Simulate what happens after TP2 is hit: SL moves to TP1
        sig.status = "TP2_HIT"
        sig.stop_loss = sig.tp1  # SL at TP1 price
        sig.original_sl_distance = 150.0  # 30000 - 29850
        sig.trailing_active = True

        # Price has moved up to 30400 (between TP2 and TP3)
        sig.current_price = 30400.0

        active = {sig.signal_id: sig}
        monitor, removed = self._build_monitor(active)

        # Invoke trailing adjustment directly
        monitor._adjust_trailing(sig)

        # trail_dist = 150 * 0.75 = 112.5
        # new_sl = 30400 - 112.5 = 30287.5
        # 30287.5 > 30000 (break-even), so stop should advance
        assert sig.stop_loss == pytest.approx(30287.5)

    @pytest.mark.asyncio
    async def test_trailing_stop_does_not_regress(self):
        """Trailing stop should never move backwards (lower for LONG)."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=60.0,
        )
        sig.status = "TP2_HIT"
        sig.stop_loss = 30200.0  # already advanced above break-even
        sig.original_sl_distance = 150.0
        sig.trailing_active = True
        # Price dips slightly – trailing should NOT regress
        sig.current_price = 30250.0  # new_sl would be 30175, below current 30200

        monitor, _ = self._build_monitor({sig.signal_id: sig})
        monitor._adjust_trailing(sig)

        assert sig.stop_loss == pytest.approx(30200.0)  # unchanged

    @pytest.mark.asyncio
    async def test_on_sl_callback_triggered_on_sl_hit(self):
        """on_sl_callback must be called with the symbol when a stop-loss is hit."""
        sl_callbacks: list = []

        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=200.0,
        )
        sig.current_price = 29800.0  # below SL

        active = {sig.signal_id: sig}
        removed = []
        sent = []

        async def mock_send(chat_id, text):
            sent.append((chat_id, text))

        data_store = MagicMock()
        data_store.get_candles.side_effect = _make_get_candles_from_active(active)
        data_store.ticks = {}

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.append(sid),
            update_signal=MagicMock(),
        )
        monitor.on_sl_callback = sl_callbacks.append

        await monitor._evaluate_signal(sig)

        assert sig.status == "SL_HIT"
        assert sl_callbacks == ["BTCUSDT"]


class TestSignalExpiry:
    """Auto-expiry: signals older than MAX_SIGNAL_HOLD_SECONDS are closed at market."""

    def _build_monitor(self, active: Dict[str, Signal]):
        removed = []
        sent = []

        async def mock_send(chat_id, text):
            sent.append((chat_id, text))

        data_store = MagicMock()
        data_store.get_candles.side_effect = _make_get_candles_from_active(active)
        data_store.ticks = {}

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.append(sid),
            update_signal=MagicMock(),
        )
        return monitor, removed, sent

    @pytest.mark.asyncio
    async def test_scalp_signal_expired_after_3600s(self):
        """A SCALP signal older than 3600s must be auto-expired at market price."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=3601.0,  # just over 1 hour
        )
        market_price = 30100.0
        sig.current_price = market_price

        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor(active)

        await monitor._evaluate_signal(sig)

        assert sig.signal_id in removed
        assert sig.status == "EXPIRED"
        # PnL should reflect the market exit price
        assert sig.current_price == pytest.approx(market_price)

    @pytest.mark.asyncio
    async def test_scalp_signal_not_expired_before_3600s(self):
        """A SCALP signal younger than 3600s must NOT be auto-expired."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            age_seconds=3599.0,  # just under 1 hour
        )
        sig.current_price = 30050.0  # price in range (no TP/SL triggered)

        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor(active)

        await monitor._evaluate_signal(sig)

        assert sig.signal_id not in removed
        assert sig.status != "EXPIRED"

    @pytest.mark.asyncio
    async def test_expiry_records_correct_pnl(self):
        """On expiry, PnL must be calculated at the current market price."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            age_seconds=3700.0,
        )
        market_price = 30200.0  # price moved up, expect positive PnL
        sig.current_price = market_price

        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor(active)

        await monitor._evaluate_signal(sig)

        assert sig.signal_id in removed
        assert sig.status == "EXPIRED"
        expected_pnl = (market_price - 30000.0) / 30000.0 * 100.0
        assert sig.pnl_pct == pytest.approx(expected_pnl, rel=1e-4)

    @pytest.mark.asyncio
    async def test_expiry_posts_telegram_update(self):
        """An expired signal must attempt to post a Telegram update with EXPIRED text."""
        from unittest.mock import AsyncMock, patch

        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            age_seconds=4000.0,
        )
        sig.current_price = 30050.0

        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor(active)

        with patch.object(monitor, "_post_update", new_callable=AsyncMock) as mock_post:
            await monitor._evaluate_signal(sig)
            mock_post.assert_called_once()
            # The event argument (second positional arg) must contain "EXPIRED"
            call_args = mock_post.call_args
            event_text = call_args[0][1] if call_args[0] else call_args.kwargs.get("event", "")
            assert "EXPIRED" in event_text


class TestATRBasedTrailing:
    """TradeMonitor._adjust_trailing must use ATR-based distance when data is available."""

    def _build_monitor(self, active: Dict[str, Signal], candles=None):
        removed = []
        sent = []

        async def mock_send(chat_id, text):
            sent.append((chat_id, text))

        data_store = MagicMock()
        data_store.get_candles.return_value = candles
        data_store.ticks = {}

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.append(sid),
            update_signal=MagicMock(),
        )
        return monitor, removed

    def _make_candles_with_atr(self, n: int = 50, price: float = 30000.0, noise: float = 50.0):
        """Generate synthetic candles that will produce a non-zero ATR(14)."""
        rng = np.random.default_rng(7)
        close = np.cumsum(rng.normal(0, noise, n)) + price
        high = close + abs(rng.normal(0, noise * 0.3, n))
        low = close - abs(rng.normal(0, noise * 0.3, n))
        return {
            "open": close,
            "high": high,
            "low": low,
            "close": close,
            "volume": np.ones(n) * 1000.0,
        }

    def test_atr_based_trailing_advances_stop(self):
        """When ATR data is available the trailing stop must advance with price."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=60.0,
        )
        sig.status = "TP1_HIT"
        sig.trailing_active = True
        sig.original_sl_distance = 150.0

        # Price well above entry
        sig.current_price = 30500.0

        candles = self._make_candles_with_atr(n=50, price=30000.0)
        monitor, _ = self._build_monitor({sig.signal_id: sig}, candles=candles)

        original_sl = sig.stop_loss
        monitor._adjust_trailing(sig)

        # SL must have moved above the original level
        assert sig.stop_loss > original_sl

    def test_fallback_when_no_candles(self):
        """When get_candles returns None, fall back to base_dist * 0.75."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=60.0,
        )
        sig.status = "TP1_HIT"
        sig.trailing_active = True
        sig.original_sl_distance = 150.0
        sig.current_price = 30400.0

        # No candles available → fallback
        monitor, _ = self._build_monitor({sig.signal_id: sig}, candles=None)
        monitor._adjust_trailing(sig)

        # trail_dist = 150 * 0.75 = 112.5  → new_sl = 30400 - 112.5 = 30287.5
        assert sig.stop_loss == pytest.approx(30287.5)

    def test_fallback_when_insufficient_candles(self):
        """When fewer than 15 candles are available, fall back to base_dist * 0.75."""
        short_candles = {
            "open": np.ones(5) * 30000.0,
            "high": np.ones(5) * 30010.0,
            "low": np.ones(5) * 29990.0,
            "close": np.ones(5) * 30000.0,
            "volume": np.ones(5) * 100.0,
        }
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=60.0,
        )
        sig.status = "TP1_HIT"
        sig.trailing_active = True
        sig.original_sl_distance = 150.0
        sig.current_price = 30400.0

        monitor, _ = self._build_monitor({sig.signal_id: sig}, candles=short_candles)
        monitor._adjust_trailing(sig)

        # Fallback: trail_dist = 150 * 0.75 = 112.5 → new_sl = 30287.5
        assert sig.stop_loss == pytest.approx(30287.5)

    def test_atr_trailing_short_direction(self):
        """For SHORT positions the ATR-based trailing stop must move down with price."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.SHORT,
            entry=30000.0,
            stop_loss=30150.0,
            tp1=29850.0,
            tp2=29700.0,
            age_seconds=60.0,
        )
        sig.status = "TP1_HIT"
        sig.trailing_active = True
        sig.original_sl_distance = 150.0
        # Price has fallen
        sig.current_price = 29600.0

        candles = self._make_candles_with_atr(n=50, price=30000.0)
        monitor, _ = self._build_monitor({sig.signal_id: sig}, candles=candles)

        original_sl = sig.stop_loss
        monitor._adjust_trailing(sig)

        # SL for SHORT must decrease (move closer to price from above)
        assert sig.stop_loss < original_sl

    def test_channel_atr_multiplier_used(self):
        """The trailing distance should reflect the channel's trailing_atr_mult config."""
        candles = self._make_candles_with_atr(n=50)
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=60.0,
        )
        sig.status = "TP1_HIT"
        sig.trailing_active = True
        sig.original_sl_distance = 150.0
        sig.current_price = 30500.0

        monitor, _ = self._build_monitor({sig.signal_id: sig}, candles=candles)
        # Run once to capture the SL after adjustment
        sig_copy_1 = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            age_seconds=60.0,
        )
        sig_copy_1.status = "TP1_HIT"
        sig_copy_1.trailing_active = True
        sig_copy_1.original_sl_distance = 150.0
        sig_copy_1.current_price = 30500.0

        monitor._adjust_trailing(sig_copy_1)
        sl_after = sig_copy_1.stop_loss

        # The SL must be above entry and above original stop
        assert sl_after > 29850.0


class TestSignalQualityPnL:
    """TradeMonitor must correctly compute signal_quality_pnl when TP1/TP2 is hit before SL."""

    def _build_monitor_with_mocks(self, active: Dict[str, Signal]):
        """Build a TradeMonitor wired with mock performance_tracker and circuit_breaker."""
        removed = []
        sent = []

        async def mock_send(chat_id, text):
            sent.append((chat_id, text))

        data_store = MagicMock()
        data_store.get_candles.side_effect = _make_get_candles_from_active(active)
        data_store.ticks = {}

        performance_tracker = MagicMock()
        circuit_breaker = MagicMock()

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.append(sid),
            update_signal=MagicMock(),
            performance_tracker=performance_tracker,
            circuit_breaker=circuit_breaker,
        )
        return monitor, removed, sent, performance_tracker, circuit_breaker

    @pytest.mark.asyncio
    async def test_tp1_then_sl_signal_quality_uses_tp1_pnl(self):
        """TP1 hit followed by SL: signal_quality_pnl_pct uses TP1 price, pnl_pct uses SL price."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=200.0,
        )
        # Simulate TP1 having been hit previously
        sig.best_tp_hit = 1
        sig.best_tp_pnl_pct = 0.5  # (30150 - 30000) / 30000 * 100
        sig.status = "TP1_HIT"
        sig.stop_loss = 29850.0  # SL not yet moved
        sig.current_price = 29800.0  # below SL

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        assert sig.status == "SL_HIT"
        pt.record_outcome.assert_called_once()
        call_kwargs = pt.record_outcome.call_args.kwargs
        # Actual PnL = SL price
        assert call_kwargs["pnl_pct"] == pytest.approx(-0.5)
        assert call_kwargs["hit_sl"] is True
        # Signal quality PnL = TP1 price
        assert call_kwargs["signal_quality_pnl_pct"] == pytest.approx(0.5)
        assert call_kwargs["signal_quality_hit_tp"] == 1
        # Circuit breaker must use actual (SL) PnL
        cb_kwargs = cb.record_outcome.call_args.kwargs
        assert cb_kwargs["pnl_pct"] == pytest.approx(-0.5)
        assert cb_kwargs["hit_sl"] is True

    @pytest.mark.asyncio
    async def test_tp2_then_sl_signal_quality_uses_tp2_pnl(self):
        """TP2 hit followed by SL: signal_quality_pnl_pct uses TP2 price."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=30000.0,  # break-even after TP2
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=200.0,
        )
        # Simulate TP2 having been hit previously
        sig.best_tp_hit = 2
        sig.best_tp_pnl_pct = 1.0  # (30300 - 30000) / 30000 * 100
        sig.status = "TP2_HIT"
        sig.current_price = 29900.0  # below break-even SL

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        assert sig.status == "BREAKEVEN_EXIT"
        pt.record_outcome.assert_called_once()
        call_kwargs = pt.record_outcome.call_args.kwargs
        # Actual PnL = 0 (break-even at entry)
        assert call_kwargs["pnl_pct"] == pytest.approx(0.0, abs=0.05)
        # Signal quality PnL = TP2 price
        assert call_kwargs["signal_quality_pnl_pct"] == pytest.approx(1.0)
        assert call_kwargs["signal_quality_hit_tp"] == 2
        # Circuit breaker uses actual PnL (not signal quality)
        cb_kwargs = cb.record_outcome.call_args.kwargs
        assert cb_kwargs["pnl_pct"] == pytest.approx(0.0, abs=0.05)

    @pytest.mark.asyncio
    async def test_no_tp_hit_then_sl_signal_quality_equals_actual(self):
        """No TP hit, then SL: signal_quality_pnl_pct equals actual pnl_pct."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=200.0,
        )
        sig.current_price = 29800.0  # below SL

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        assert sig.status == "SL_HIT"
        pt.record_outcome.assert_called_once()
        call_kwargs = pt.record_outcome.call_args.kwargs
        # Both actual and signal quality should be the SL PnL
        assert call_kwargs["pnl_pct"] == pytest.approx(-0.5)
        assert call_kwargs["signal_quality_pnl_pct"] == pytest.approx(-0.5)
        assert call_kwargs["signal_quality_hit_tp"] == 0

    @pytest.mark.asyncio
    async def test_tp1_hit_snapshots_best_tp_fields(self):
        """When TP1 is hit, best_tp_hit and best_tp_pnl_pct must be set on the signal."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=200.0,
        )
        sig.current_price = 30200.0  # above TP1 but below TP2

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        assert sig.status == "TP1_HIT"
        assert sig.best_tp_hit == 1
        assert sig.best_tp_pnl_pct == pytest.approx(0.5)  # (30150 - 30000) / 30000 * 100

    @pytest.mark.asyncio
    async def test_tp2_hit_upgrades_best_tp_fields(self):
        """When TP2 is hit, best_tp_hit upgrades to 2 and best_tp_pnl_pct uses TP2 price."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=200.0,
        )
        sig.current_price = 30350.0  # above TP2 but below TP3

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        assert sig.status == "TP2_HIT"
        assert sig.best_tp_hit == 2
        assert sig.best_tp_pnl_pct == pytest.approx(1.0)  # (30300 - 30000) / 30000 * 100

    @pytest.mark.asyncio
    async def test_tp1_expiry_signal_quality_uses_tp1_pnl(self):
        """TP1 hit then signal expires: signal quality uses TP1 PnL, actual uses market price."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=3700.0,  # expired
        )
        # TP1 was hit before expiry
        sig.best_tp_hit = 1
        sig.best_tp_pnl_pct = 0.5
        sig.status = "TP1_HIT"
        market_price = 30050.0  # price at expiry (lower than TP1)
        sig.current_price = market_price

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        assert sig.status == "EXPIRED"
        pt.record_outcome.assert_called_once()
        call_kwargs = pt.record_outcome.call_args.kwargs
        # Actual PnL = market price at expiry
        expected_actual = (market_price - 30000.0) / 30000.0 * 100.0
        assert call_kwargs["pnl_pct"] == pytest.approx(expected_actual, rel=1e-4)
        # Signal quality PnL = TP1 price (best TP reached)
        assert call_kwargs["signal_quality_pnl_pct"] == pytest.approx(0.5)
        assert call_kwargs["signal_quality_hit_tp"] == 1

    @pytest.mark.asyncio
    async def test_short_tp1_then_sl_signal_quality_uses_tp1_pnl(self):
        """SHORT: TP1 hit followed by SL uses TP1 for signal quality PnL."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.SHORT,
            entry=30000.0,
            stop_loss=30150.0,
            tp1=29850.0,
            tp2=29700.0,
            tp3=29550.0,
            age_seconds=200.0,
        )
        # Simulate TP1 having been hit
        sig.best_tp_hit = 1
        sig.best_tp_pnl_pct = 0.5  # (30000 - 29850) / 30000 * 100
        sig.status = "TP1_HIT"
        sig.current_price = 30250.0  # above SL for SHORT

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        assert sig.status == "SL_HIT"
        pt.record_outcome.assert_called_once()
        call_kwargs = pt.record_outcome.call_args.kwargs
        # Actual PnL = SL price (30150) for SHORT: (30000 - 30150) / 30000 * 100 = -0.5%
        assert call_kwargs["pnl_pct"] == pytest.approx(-0.5)
        # Signal quality PnL = TP1 price
        assert call_kwargs["signal_quality_pnl_pct"] == pytest.approx(0.5)
        assert call_kwargs["signal_quality_hit_tp"] == 1
        # Circuit breaker uses actual PnL
        cb_kwargs = cb.record_outcome.call_args.kwargs
        assert cb_kwargs["pnl_pct"] == pytest.approx(-0.5)
        assert cb_kwargs["hit_sl"] is True

    @pytest.mark.asyncio
    async def test_circuit_breaker_always_uses_actual_pnl(self):
        """Circuit breaker must always receive the real exit PnL regardless of signal quality."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            age_seconds=200.0,
        )
        # Simulate TP2 having been hit (signal quality would be +1%)
        sig.best_tp_hit = 2
        sig.best_tp_pnl_pct = 1.0
        sig.status = "TP2_HIT"
        sig.stop_loss = 30000.0  # break-even after TP2
        sig.current_price = 29900.0  # below break-even

        active = {sig.signal_id: sig}
        monitor, removed, sent, pt, cb = self._build_monitor_with_mocks(active)

        await monitor._evaluate_signal(sig)

        # Signal quality shows positive, but circuit breaker sees the actual (breakeven/loss)
        cb_kwargs = cb.record_outcome.call_args.kwargs
        assert cb_kwargs["pnl_pct"] == pytest.approx(0.0, abs=0.05)
        # Not a loss from circuit breaker's perspective (break-even)
        assert cb_kwargs["hit_sl"] is True


# ---------------------------------------------------------------------------
# Signal Invalidation Tests
# ---------------------------------------------------------------------------

class TestSignalInvalidation:
    """Tests for TradeMonitor._check_invalidation() and its integration with
    _evaluate_signal()."""

    def _build_monitor(
        self,
        active: Dict[str, Signal],
        candles_close=None,
        regime_detector=None,
        indicators_fn=None,
    ):
        removed = []
        sent = []

        async def mock_send(chat_id, text):
            sent.append((chat_id, text))

        data_store = MagicMock()
        data_store.ticks = {}
        if candles_close is not None:
            closes = list(candles_close)
            candles_dict = {
                "close": closes,
                "open": closes,
                "high": closes,
                "low": closes,
                "volume": [1.0] * len(closes),
            }
            data_store.get_candles.return_value = candles_dict
        else:
            data_store.get_candles.side_effect = _make_get_candles_from_active(active)

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.append(sid),
            update_signal=MagicMock(),
            regime_detector=regime_detector,
            indicators_fn=indicators_fn,
        )
        # Set current_price so _evaluate_signal can proceed
        for sig in active.values():
            if sig.current_price == 0.0:
                sig.current_price = sig.entry
        return monitor, removed, sent

    # ------------------------------------------------------------------
    # _check_invalidation unit tests
    # ------------------------------------------------------------------

    def test_no_invalidation_when_no_data(self):
        """When no indicators are available, _check_invalidation returns None."""
        sig = _make_signal(age_seconds=200.0)
        monitor, _, _ = self._build_monitor({sig.signal_id: sig})
        assert monitor._check_invalidation(sig) is None

    def test_regime_flip_invalidates_long(self):
        """LONG signal must be invalidated when regime detector returns TRENDING_DOWN."""
        sig = _make_signal(direction=Direction.LONG, age_seconds=700.0)

        regime_detector = MagicMock()
        regime_result = MagicMock()
        regime_result.regime.value = "TRENDING_DOWN"
        regime_detector.classify.return_value = regime_result

        closes = [30000.0] * 25  # enough data
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            candles_close=closes,
            regime_detector=regime_detector,
        )
        reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "TRENDING_DOWN" in reason
        assert "LONG" in reason

    def test_regime_flip_invalidates_short(self):
        """SHORT signal must be invalidated when regime detector returns TRENDING_UP."""
        sig = _make_signal(
            direction=Direction.SHORT,
            entry=30000.0,
            stop_loss=30150.0,
            tp1=29850.0,
            age_seconds=700.0,
        )

        regime_detector = MagicMock()
        regime_result = MagicMock()
        regime_result.regime.value = "TRENDING_UP"
        regime_detector.classify.return_value = regime_result

        closes = [30000.0] * 25
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            candles_close=closes,
            regime_detector=regime_detector,
        )
        reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "TRENDING_UP" in reason
        assert "SHORT" in reason

    def test_ema_bearish_crossover_invalidates_long(self):
        """LONG signal invalidated when EMA9 < EMA21 (bearish crossover)."""
        sig = _make_signal(direction=Direction.LONG, age_seconds=700.0)

        # Create a falling price sequence: EMA9 will be lower than EMA21
        closes = [30000.0 - i * 10 for i in range(25)]  # descending
        monitor, _, _ = self._build_monitor({sig.signal_id: sig}, candles_close=closes)
        reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "EMA" in reason
        assert "LONG" in reason

    def test_ema_bullish_crossover_invalidates_short(self):
        """SHORT signal invalidated when EMA9 > EMA21 (bullish crossover)."""
        sig = _make_signal(
            direction=Direction.SHORT,
            entry=30000.0,
            stop_loss=30150.0,
            tp1=29850.0,
            age_seconds=700.0,
        )

        # Rising prices: EMA9 > EMA21
        closes = [30000.0 + i * 10 for i in range(25)]
        monitor, _, _ = self._build_monitor({sig.signal_id: sig}, candles_close=closes)
        reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "EMA" in reason
        assert "SHORT" in reason

    def test_ema_crossover_exempts_lsr_long(self):
        """LSR LONG must NOT be EMA-cross-invalidated even with ema9 < ema21.

        LIQUIDITY_SWEEP_REVERSAL is counter-trend by design (CLAUDE.md HTF
        policy): it fades an existing up-move's exhaustion sweep, so its EMAs
        are routinely misaligned to the LONG direction at dispatch.  The
        regime-based ``_counter_trend`` flag does not catch this case (a LONG
        in TRENDING_UP regime is regime-aligned but thesis-counter-trend).
        Truth-report 2026-05-09 audit: LSR had 1 PROTECTIVE / 2 PREMATURE / 2
        NEUTRAL ema-crossover kills — the rule is net-hurting on this path.
        """
        sig = _make_signal(direction=Direction.LONG, age_seconds=700.0)
        sig.setup_class = "LIQUIDITY_SWEEP_REVERSAL"

        # Falling closes → EMA9 < EMA21 (the exact "bearish crossover" trigger).
        closes = [30000.0 - i * 10 for i in range(25)]
        monitor, _, _ = self._build_monitor({sig.signal_id: sig}, candles_close=closes)
        reason = monitor._check_invalidation(sig)
        assert reason is None or "EMA" not in reason, (
            f"LSR LONG must be exempt from EMA-crossover invalidation, got: {reason!r}"
        )

    def test_ema_crossover_exempts_far_short(self):
        """FAR SHORT must NOT be EMA-cross-invalidated even with ema9 > ema21.

        Symmetric counter-trend exemption for FAILED_AUCTION_RECLAIM SHORT —
        thesis is to fade an exhausted up-auction.
        """
        sig = _make_signal(
            direction=Direction.SHORT,
            entry=30000.0,
            stop_loss=30150.0,
            tp1=29850.0,
            age_seconds=700.0,
        )
        sig.setup_class = "FAILED_AUCTION_RECLAIM"

        # Rising closes → EMA9 > EMA21 (the bullish-crossover trigger for SHORT).
        closes = [30000.0 + i * 10 for i in range(25)]
        monitor, _, _ = self._build_monitor({sig.signal_id: sig}, candles_close=closes)
        reason = monitor._check_invalidation(sig)
        assert reason is None or "EMA" not in reason, (
            f"FAR SHORT must be exempt from EMA-crossover invalidation, got: {reason!r}"
        )

    def test_ema_crossover_still_kills_non_exempt_setup(self):
        """A non-exempt setup (e.g. TREND_PULLBACK_EMA) must still be killed by
        EMA-crossover, ensuring the exemption is narrow and not a regression."""
        sig = _make_signal(direction=Direction.LONG, age_seconds=700.0)
        sig.setup_class = "TREND_PULLBACK_EMA"

        closes = [30000.0 - i * 10 for i in range(25)]
        monitor, _, _ = self._build_monitor({sig.signal_id: sig}, candles_close=closes)
        reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "EMA" in reason
        assert "LONG" in reason

    def test_momentum_loss_invalidates_after_min_age(self):
        """Signal with momentum AGAINST direction is invalidated after min age.

        2026-05-07 fix: invalidation is now direction-aware.  Flat-price
        consolidation (momentum ≈ 0) is NOT a thesis failure for a
        continuation signal — only momentum *against* the trade direction
        triggers the kill.
        """
        from config import INVALIDATION_MIN_AGE_SECONDS
        channel = "360_SCALP"
        min_age = INVALIDATION_MIN_AGE_SECONDS[channel]
        sig = _make_signal(channel=channel, age_seconds=min_age + 10)
        # LONG signal — closes rise for 22 bars (so EMA9 > EMA21, no
        # EMA-crossover invalidation), then sharp drop on last 3 bars
        # produces strongly negative momentum that triggers the
        # direction-aware momentum check.
        closes = [30000.0 + 50.0 * i for i in range(22)] + [
            30000.0 + 50.0 * 22 - 200.0,
            30000.0 + 50.0 * 22 - 400.0,
            30000.0 + 50.0 * 22 - 600.0,
        ]
        monitor, _, _ = self._build_monitor({sig.signal_id: sig}, candles_close=closes)
        # SCALP requires 2 consecutive below-threshold readings before invalidating.
        reason = monitor._check_invalidation(sig)
        assert reason is None, "First reading should not invalidate yet (consecutive guard)"
        reason = monitor._check_invalidation(sig)
        # Falling prices on a LONG → momentum < -threshold → invalidates.
        assert reason is not None
        assert "momentum" in reason.lower()

    def test_momentum_loss_NOT_triggered_by_flat_consolidation(self):
        """Direction-aware invalidation: flat prices = consolidation, NOT thesis failure.

        Owner-flagged 2026-05-07: SOLUSDT CONTINUATION_LIQUIDITY_SWEEP LONG
        was killed at +0.01% with ``|momentum|=0.090`` while price meandered
        around the entry.  Within the same hour price recovered and would
        have hit TP.  After this fix, flat momentum should NOT invalidate.
        """
        from config import INVALIDATION_MIN_AGE_SECONDS
        channel = "360_SCALP"
        min_age = INVALIDATION_MIN_AGE_SECONDS[channel]
        sig = _make_signal(channel=channel, age_seconds=min_age + 10)
        closes = [30000.0] * 25  # Flat → momentum ≈ 0
        monitor, _, _ = self._build_monitor({sig.signal_id: sig}, candles_close=closes)
        # Multiple readings of flat momentum should NOT invalidate.
        for _ in range(5):
            reason = monitor._check_invalidation(sig)
            assert reason is None, (
                "Flat consolidation must not invalidate a continuation signal."
            )

    def test_short_with_flat_prices_not_invalidated(self):
        """Symmetric: SHORT signal during flat consolidation must also survive."""
        from config import INVALIDATION_MIN_AGE_SECONDS
        from src.smc import Direction
        channel = "360_SCALP"
        min_age = INVALIDATION_MIN_AGE_SECONDS[channel]
        sig = _make_signal(
            channel=channel,
            age_seconds=min_age + 10,
            direction=Direction.SHORT,
            stop_loss=30150.0,  # SL above for SHORT
            tp1=29800.0,        # TP below for SHORT
        )
        closes = [30000.0] * 25
        monitor, _, _ = self._build_monitor({sig.signal_id: sig}, candles_close=closes)
        for _ in range(5):
            reason = monitor._check_invalidation(sig)
            assert reason is None, (
                "Flat consolidation must not invalidate a SHORT continuation signal."
            )

    def test_short_invalidates_on_rising_prices(self):
        """SHORT signal: momentum strongly POSITIVE = price rising = thesis fails."""
        from config import INVALIDATION_MIN_AGE_SECONDS
        from src.smc import Direction
        channel = "360_SCALP"
        min_age = INVALIDATION_MIN_AGE_SECONDS[channel]
        sig = _make_signal(
            channel=channel,
            age_seconds=min_age + 10,
            direction=Direction.SHORT,
            stop_loss=30150.0,
            tp1=29800.0,
        )
        # Fall for 22 bars (so EMA9 < EMA21 → no EMA-cross invalidation
        # for SHORT), then sharp rally on last 3 bars → strongly positive
        # momentum that triggers direction-aware invalidation.
        closes = [30000.0 - 50.0 * i for i in range(22)] + [
            30000.0 - 50.0 * 22 + 200.0,
            30000.0 - 50.0 * 22 + 400.0,
            30000.0 - 50.0 * 22 + 600.0,
        ]
        monitor, _, _ = self._build_monitor({sig.signal_id: sig}, candles_close=closes)
        first = monitor._check_invalidation(sig)
        assert first is None, "First reading: consecutive guard not yet hit"
        reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "momentum" in reason.lower()

    def test_momentum_not_invalidated_before_min_age(self):
        """Momentum-loss check must NOT fire before INVALIDATION_MIN_AGE_SECONDS."""
        from config import INVALIDATION_MIN_AGE_SECONDS
        channel = "360_SCALP"
        min_age = INVALIDATION_MIN_AGE_SECONDS[channel]
        # Signal is 10s younger than the minimum age (always positive for min_age >= 10)
        sig = _make_signal(channel=channel, age_seconds=min_age - 10)

        closes = [30000.0] * 25  # flat → zero momentum, but EMA9 == EMA21 (no EMA invalidation)
        monitor, _, _ = self._build_monitor({sig.signal_id: sig}, candles_close=closes)

        # Regime detector is None → no regime check
        # EMA9 == EMA21 for flat prices → no EMA crossover invalidation
        # Momentum check is age-gated → must NOT fire before min_age
        reason = monitor._check_invalidation(sig)
        # Momentum invalidation must not occur before the minimum age
        assert reason is None, (
            f"Expected no invalidation before min_age ({min_age}s), got: {reason!r}"
        )

    # ------------------------------------------------------------------
    # Integration tests: _check_invalidation called inside _evaluate_signal
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_invalidated_signal_is_removed_and_slot_freed(self):
        """An invalidated signal must be removed from active signals."""
        sig = _make_signal(
            channel="360_SCALP",
            age_seconds=700.0,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
        )
        # Price below entry so signal is in negative territory — profit
        # protection does not apply and the regime flip can fire.  Not deep
        # enough to reach the adverse-excursion fraction (0.55 × 150 = 82.5).
        sig.current_price = 29960.0

        regime_detector = MagicMock()
        regime_result = MagicMock()
        regime_result.regime.value = "TRENDING_DOWN"
        regime_detector.classify.return_value = regime_result

        closes = [30000.0] * 25
        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor(
            active, candles_close=closes, regime_detector=regime_detector
        )

        await monitor._evaluate_signal(sig)

        assert sig.signal_id in removed
        assert sig.status == "INVALIDATED"
        # Telegram send is skipped in tests (no CHANNEL_TELEGRAM_MAP entry),
        # but the signal must be removed and status must be INVALIDATED.

    @pytest.mark.asyncio
    async def test_invalidated_signal_not_counted_as_sl_for_circuit_breaker(self):
        """Invalidated signals must NOT count as stop-losses in the circuit breaker."""
        sig = _make_signal(
            channel="360_SCALP",
            age_seconds=700.0,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
        )
        # Price below entry so signal is in negative territory — profit
        # protection does not apply and the regime flip can fire.
        sig.current_price = 29960.0

        cb = MagicMock()

        regime_detector = MagicMock()
        regime_result = MagicMock()
        regime_result.regime.value = "TRENDING_DOWN"
        regime_detector.classify.return_value = regime_result

        closes = [30000.0] * 25
        active = {sig.signal_id: sig}

        async def mock_send(chat_id, text):
            pass

        data_store = MagicMock()
        data_store.ticks = {}
        candles_dict = {
            "close": closes, "open": closes, "high": closes, "low": closes,
            "volume": [1.0] * len(closes),
        }
        data_store.get_candles.return_value = candles_dict

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=MagicMock(),
            update_signal=MagicMock(),
            circuit_breaker=cb,
            regime_detector=regime_detector,
        )

        await monitor._evaluate_signal(sig)

        # circuit_breaker.record_outcome must be called with hit_sl=False
        assert cb.record_outcome.called
        call_kwargs = cb.record_outcome.call_args.kwargs
        assert call_kwargs.get("hit_sl") is False

    # ------------------------------------------------------------------
    # New tests for the reordered evaluation and age-gating
    # ------------------------------------------------------------------

    def test_regime_not_invalidated_before_min_age(self):
        """Regime flip must NOT fire before INVALIDATION_MIN_AGE_SECONDS (global gate)."""
        from config import INVALIDATION_MIN_AGE_SECONDS
        channel = "360_SCALP"
        min_age = INVALIDATION_MIN_AGE_SECONDS[channel]
        sig = _make_signal(channel=channel, direction=Direction.LONG, age_seconds=min_age - 10)

        regime_detector = MagicMock()
        regime_result = MagicMock()
        regime_result.regime.value = "TRENDING_DOWN"
        regime_detector.classify.return_value = regime_result

        closes = [30000.0] * 25
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            candles_close=closes,
            regime_detector=regime_detector,
        )
        reason = monitor._check_invalidation(sig)
        assert reason is None, (
            f"Regime invalidation must not fire before min_age ({min_age}s), got: {reason!r}"
        )

    def test_ema_not_invalidated_before_min_age(self):
        """EMA crossover must NOT fire before INVALIDATION_MIN_AGE_SECONDS (global gate)."""
        from config import INVALIDATION_MIN_AGE_SECONDS
        channel = "360_SCALP"
        min_age = INVALIDATION_MIN_AGE_SECONDS[channel]
        sig = _make_signal(channel=channel, direction=Direction.LONG, age_seconds=min_age - 10)

        # Falling prices → EMA9 < EMA21 (bearish crossover)
        closes = [30000.0 - i * 10 for i in range(25)]
        monitor, _, _ = self._build_monitor({sig.signal_id: sig}, candles_close=closes)
        reason = monitor._check_invalidation(sig)
        assert reason is None, (
            f"EMA invalidation must not fire before min_age ({min_age}s), got: {reason!r}"
        )

    @pytest.mark.asyncio
    async def test_sl_fires_before_invalidation(self):
        """When price is below SL and regime flips, SL must fire (not invalidation).

        Trade-monitor SL check now uses 1m candle low (audit-2 fix), not
        sig.current_price.  The candles fixture's LAST element drives the gap
        — set it to the gap-down price so candle.low ≤ SL triggers SL_HIT.
        Pre-cleanup the test relied on `sig.current_price` directly which the
        new code no longer reads for SL/TP.
        """
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            age_seconds=400.0,
        )
        # Price has gapped BELOW the stop-loss
        sig.current_price = 29700.0

        regime_detector = MagicMock()
        regime_result = MagicMock()
        regime_result.regime.value = "TRENDING_DOWN"
        regime_detector.classify.return_value = regime_result

        # Last candle reflects the gap-down: low = 29700 < SL = 29850 → SL fires.
        closes = [30000.0] * 24 + [29700.0]
        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor(
            active, candles_close=closes, regime_detector=regime_detector
        )

        await monitor._evaluate_signal(sig)

        # SL must have fired, not invalidation
        assert sig.signal_id in removed
        assert sig.status != "INVALIDATED", "Should be SL_HIT, not INVALIDATED"
        assert "SL" in sig.status or sig.status in ("SL_HIT", "BREAKEVEN_EXIT", "PROFIT_LOCKED")

    @pytest.mark.asyncio
    async def test_invalidation_exit_price_capped_at_sl_long(self):
        """LONG: when invalidation fires, exit price must be capped at the SL (not below)."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            age_seconds=700.0,
        )
        # Price is above SL so SL doesn't fire; invalidation will fire instead
        sig.current_price = 29900.0

        regime_detector = MagicMock()
        regime_result = MagicMock()
        regime_result.regime.value = "TRENDING_DOWN"
        regime_detector.classify.return_value = regime_result

        closes = [30000.0] * 25
        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor(
            active, candles_close=closes, regime_detector=regime_detector
        )

        await monitor._evaluate_signal(sig)

        assert sig.status == "INVALIDATED"
        # Exit PnL must be computed at the capped price (max(29900, 29850) = 29900 for LONG)
        # which is the current price since price > SL
        from src.performance_metrics import calculate_trade_pnl_pct
        expected_pnl = calculate_trade_pnl_pct(30000.0, 29900.0, "LONG")
        assert sig.pnl_pct == pytest.approx(expected_pnl, abs=1e-4)

    @pytest.mark.asyncio
    async def test_invalidation_exit_price_never_worse_than_sl_long(self):
        """LONG: invalidation with price below SL must exit at SL, not current price."""
        # This scenario: price has gapped, but SL check runs first and catches it.
        # However, if the reorder means SL fires first, we verify that pathway.
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            age_seconds=400.0,
        )
        # Price is below SL — SL check fires first.  Last candle reflects the
        # gap-down; SL/TP eval uses 1m candle low/high (audit-2), not
        # sig.current_price directly.
        sig.current_price = 29700.0

        closes = [30000.0] * 24 + [29700.0]
        active = {sig.signal_id: sig}
        monitor, removed, _ = self._build_monitor(active, candles_close=closes)

        await monitor._evaluate_signal(sig)

        # Must be removed via SL, not invalidation
        assert sig.signal_id in removed
        # Exit price frozen at SL, not at the worse 29700
        assert sig.current_price == pytest.approx(29850.0)

    @pytest.mark.asyncio
    async def test_invalidation_exit_price_capped_at_sl_short(self):
        """SHORT: when invalidation fires, exit price must be capped at the SL (not above)."""
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.SHORT,
            entry=30000.0,
            stop_loss=30150.0,
            tp1=29850.0,
            age_seconds=700.0,
        )
        # Price is below SL so SL doesn't fire; invalidation will fire instead
        sig.current_price = 30100.0

        regime_detector = MagicMock()
        regime_result = MagicMock()
        regime_result.regime.value = "TRENDING_UP"
        regime_detector.classify.return_value = regime_result

        closes = [30000.0] * 25
        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor(
            active, candles_close=closes, regime_detector=regime_detector
        )

        await monitor._evaluate_signal(sig)

        assert sig.status == "INVALIDATED"
        # Exit PnL must use min(30100, 30150) = 30100 — current price since price < SL
        from src.performance_metrics import calculate_trade_pnl_pct
        expected_pnl = calculate_trade_pnl_pct(30000.0, 30100.0, "SHORT")
        assert sig.pnl_pct == pytest.approx(expected_pnl, abs=1e-4)

    def test_dca_grace_period_prevents_invalidation(self):
        """Invalidation must return None within 600s of a DCA entry being filled."""
        from datetime import timedelta
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            age_seconds=400.0,
        )
        # Mark DCA as just filled (1 minute ago — within grace period)
        sig.entry_2_filled = True
        sig.dca_timestamp = utcnow() - timedelta(seconds=60)

        regime_detector = MagicMock()
        regime_result = MagicMock()
        regime_result.regime.value = "TRENDING_DOWN"
        regime_detector.classify.return_value = regime_result

        closes = [30000.0] * 25
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            candles_close=closes,
            regime_detector=regime_detector,
        )
        reason = monitor._check_invalidation(sig)
        assert reason is None, (
            f"Invalidation must be suppressed during DCA grace period, got: {reason!r}"
        )

    def test_dca_grace_period_expires(self):
        """Invalidation is allowed after the DCA grace period (>600s since DCA)."""
        from datetime import timedelta
        sig = _make_signal(
            channel="360_SCALP",
            direction=Direction.LONG,
            age_seconds=700.0,
        )
        # Mark DCA as filled 610 seconds ago — grace period has expired
        sig.entry_2_filled = True
        sig.dca_timestamp = utcnow() - timedelta(seconds=610)

        regime_detector = MagicMock()
        regime_result = MagicMock()
        regime_result.regime.value = "TRENDING_DOWN"
        regime_detector.classify.return_value = regime_result

        closes = [30000.0] * 25
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            candles_close=closes,
            regime_detector=regime_detector,
        )
        reason = monitor._check_invalidation(sig)
        assert reason is not None, "Invalidation must fire after DCA grace period expires"
        assert "TRENDING_DOWN" in reason

    def test_microcap_momentum_threshold_scaled_down(self):
        """Micro-cap tokens (entry < 0.001) use a 10× smaller momentum threshold.

        2026-05-07 fix: invalidation is direction-aware, so we drive a
        decisively-against-direction price series instead of flat prices
        to confirm the threshold is applied to the scaled value.
        """
        from config import INVALIDATION_MIN_AGE_SECONDS
        channel = "360_SCALP"
        min_age = INVALIDATION_MIN_AGE_SECONDS[channel]
        micro_entry = 0.0000064  # BONK-like price

        sig = _make_signal(
            channel=channel,
            entry=micro_entry,
            stop_loss=micro_entry * 0.95,
            tp1=micro_entry * 1.05,
            age_seconds=min_age + 10,
        )
        # Rise for 22 bars (EMA9 stays above EMA21), then sharp drop on
        # the last 3 bars — produces strongly negative momentum without
        # flipping the EMA stack (EMA lag).  This isolates the
        # momentum-invalidation path from the EMA-crossover path.
        closes = [30000.0 + 50.0 * i for i in range(22)] + [
            30000.0 + 50.0 * 22 - 200.0,
            30000.0 + 50.0 * 22 - 400.0,
            30000.0 + 50.0 * 22 - 600.0,
        ]
        monitor, _, _ = self._build_monitor({sig.signal_id: sig}, candles_close=closes)
        first_reason = monitor._check_invalidation(sig)
        assert first_reason is None, "First reading should not invalidate yet (consecutive guard)"
        reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "momentum" in reason.lower()

    def test_normal_cap_momentum_threshold_not_scaled(self):
        """Standard-price tokens (entry >= 0.001) use the base momentum threshold.

        2026-05-07 fix: same as above — drive against-direction prices
        to confirm direction-aware invalidation fires at the base threshold.
        """
        from config import INVALIDATION_MIN_AGE_SECONDS
        channel = "360_SCALP"
        min_age = INVALIDATION_MIN_AGE_SECONDS[channel]
        standard_entry = 1.5  # normal price like XRPUSDT

        sig = _make_signal(
            channel=channel,
            entry=standard_entry,
            stop_loss=standard_entry * 0.95,
            tp1=standard_entry * 1.05,
            age_seconds=min_age + 10,
        )
        # Same shape as the micro-cap test: rise then sharp drop, so
        # EMA9 > EMA21 (no crossover invalidation) but momentum is
        # strongly negative and triggers the direction-aware check.
        closes = [30000.0 + 50.0 * i for i in range(22)] + [
            30000.0 + 50.0 * 22 - 200.0,
            30000.0 + 50.0 * 22 - 400.0,
            30000.0 + 50.0 * 22 - 600.0,
        ]
        monitor, _, _ = self._build_monitor({sig.signal_id: sig}, candles_close=closes)
        first_reason = monitor._check_invalidation(sig)
        assert first_reason is None, "First reading should not invalidate yet (consecutive guard)"
        reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "momentum" in reason.lower()

    # ------------------------------------------------------------------
    # Adverse-excursion rule (2026-05-20 — truth-report follow-up)
    # ------------------------------------------------------------------
    #
    # Catches the full-SL pattern that the other three rules miss:
    # price grinding from entry → SL with momentum, regime, and EMA
    # structure all intact the whole way down.  Fires when:
    #   - age ≥ INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC (default 300s)
    #   - adverse excursion ≥ INVALIDATION_ADVERSE_EXCURSION_FRACTION
    #     × SL_dist (default 0.70 — saves ~30% of SL distance)
    #   - momentum NOT strongly confirming thesis
    #   - status NOT in {TP1_HIT, TP2_HIT}
    #   - pretp_fired == False (post-pre-TP residuals are BE-protected)

    def test_adverse_excursion_fires_at_70pct_with_flat_momentum(self):
        """LONG signal: price drops to 70% of SL distance + flat
        momentum + EMA still aligned LONG → adverse_excursion fires
        even when the other rules pass.  Sample: entry=30000, SL=29850
        (150 below) → 70% threshold = drop to 29895.

        Inject EMAs aligned LONG (ema9 > ema21) so the EMA-crossover
        rule does NOT fire — this isolates the new rule's behaviour.
        This mirrors the production case: price grinding against the
        position with momentum, regime, and EMA structure all intact.
        """
        from config import INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC
        channel = "360_SCALP"
        sig = _make_signal(
            channel=channel,
            age_seconds=INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC + 30,
            entry=30000.0,
            stop_loss=29850.0,
        )
        sig.current_price = 29895.0
        # Inject indicators directly: EMA9 still above EMA21 (LONG
        # alignment intact), momentum near zero (not confirming).
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {
                "ema9_last": 30005.0, "ema21_last": 30000.0,
                "momentum": 0.0, "atr_last": 50.0,
            },
        )
        reason = monitor._check_invalidation(sig)
        assert reason is not None, (
            "Adverse excursion at 70%×SL with non-confirming "
            "momentum should fire"
        )
        assert "adverse excursion" in reason.lower()
        assert "0.70" in reason or "0.71" in reason  # adverse_frac

    def test_adverse_excursion_short_symmetric(self):
        """SHORT signal: price rises to 70% of SL distance + flat
        momentum + EMA aligned SHORT → adverse_excursion fires."""
        from config import INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC
        from src.smc import Direction
        channel = "360_SCALP"
        sig = _make_signal(
            channel=channel,
            age_seconds=INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC + 30,
            direction=Direction.SHORT,
            entry=30000.0,
            stop_loss=30150.0,
            tp1=29850.0,
            tp2=29700.0,
            tp3=29550.0,
        )
        sig.current_price = 30105.0
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {
                "ema9_last": 29995.0, "ema21_last": 30000.0,
                "momentum": 0.0, "atr_last": 50.0,
            },
        )
        reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "adverse excursion" in reason.lower()

    def test_adverse_excursion_NOT_triggered_under_threshold(self):
        """Price 50% of SL distance against → below 70% threshold →
        no kill."""
        from config import INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC
        channel = "360_SCALP"
        sig = _make_signal(
            channel=channel,
            age_seconds=INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC + 30,
            entry=30000.0,
            stop_loss=29850.0,
        )
        sig.current_price = 29925.0  # 50% of SL_dist adverse
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {
                "ema9_last": 30005.0, "ema21_last": 30000.0,
                "momentum": 0.0, "atr_last": 50.0,
            },
        )
        reason = monitor._check_invalidation(sig)
        assert reason is None or "adverse excursion" not in reason.lower()

    def test_adverse_excursion_NOT_triggered_before_min_age(self):
        """Same setup as the firing test but age below min — no kill."""
        from config import INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC
        channel = "360_SCALP"
        sig = _make_signal(
            channel=channel,
            age_seconds=INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC - 30,
            entry=30000.0,
            stop_loss=29850.0,
        )
        sig.current_price = 29895.0
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {
                "ema9_last": 30005.0, "ema21_last": 30000.0,
                "momentum": 0.0, "atr_last": 50.0,
            },
        )
        reason = monitor._check_invalidation(sig)
        assert reason is None or "adverse excursion" not in reason.lower()

    def test_adverse_excursion_triggered_regardless_of_momentum(self):
        """Price at 70% of SL_dist with strongly confirming momentum →
        adverse excursion fires unconditionally (no momentum rescue).
        When the trade is in negative territory at the threshold, the thesis
        is structurally broken; a 3-candle bounce does not change that."""
        from config import (
            INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC,
            INVALIDATION_MOMENTUM_THRESHOLD,
        )
        channel = "360_SCALP"
        sig = _make_signal(
            channel=channel,
            age_seconds=INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC + 30,
            entry=30000.0,
            stop_loss=29850.0,
        )
        sig.current_price = 29895.0
        # Momentum well above threshold (strongly confirming LONG) — previously
        # this bypassed adverse excursion.  New doctrine: threshold is decisive.
        strong_mom = INVALIDATION_MOMENTUM_THRESHOLD[channel] * 5.0
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {
                "ema9_last": 30005.0, "ema21_last": 30000.0,
                "momentum": strong_mom, "atr_last": 50.0,
            },
        )
        reason = monitor._check_invalidation(sig)
        assert reason is not None and "adverse excursion" in reason.lower()

    def test_adverse_excursion_NOT_triggered_after_pretp_fire(self):
        """Once pre-TP has fired, the residual is BE-protected per
        §3.2a — deeper hold is doctrinally correct, no kill."""
        from config import INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC
        channel = "360_SCALP"
        sig = _make_signal(
            channel=channel,
            age_seconds=INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC + 30,
            entry=30000.0,
            stop_loss=29850.0,
        )
        sig.pretp_fired = True  # BE protection in place
        sig.current_price = 29895.0
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {
                "ema9_last": 30005.0, "ema21_last": 30000.0,
                "momentum": 0.0, "atr_last": 50.0,
            },
        )
        reason = monitor._check_invalidation(sig)
        assert reason is None or "adverse excursion" not in reason.lower()

    def test_adverse_excursion_NOT_triggered_after_tp1_hit(self):
        """Post-TP1, the trailing stop manages exits per §3.2a — no
        adverse_excursion kill."""
        from config import INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC
        channel = "360_SCALP"
        sig = _make_signal(
            channel=channel,
            age_seconds=INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC + 30,
            entry=30000.0,
            stop_loss=29850.0,
        )
        sig.status = "TP1_HIT"
        sig.current_price = 29895.0
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {
                "ema9_last": 30005.0, "ema21_last": 30000.0,
                "momentum": 0.0, "atr_last": 50.0,
            },
        )
        reason = monitor._check_invalidation(sig)
        assert reason is None or "adverse excursion" not in reason.lower()

    # ── Per-setup fraction overrides (PR revert: SR_FLIP 2.5%, LSR 2.0%) ──

    def test_sr_flip_adverse_excursion_uses_0_40_fraction(self):
        """SR_FLIP_RETEST uses 0.40 fraction so exits at 40% of 2.5% SL = 1.0% adverse.

        Global fraction is 0.55 — without per-setup override, exit would wait
        until 1.375% adverse (0.55 × 2.5%) which is far too late.
        SR_FLIP patience is 240s, so signal must be at least 270s old.
        """
        channel = "360_SCALP"
        # SR_FLIP min-age = 240s; use 270s to clear both the function-level gate
        # and the adverse-excursion per-rule gate.
        sig = _make_signal(
            channel=channel,
            age_seconds=270,
            entry=100.0,
            stop_loss=97.5,  # 2.5% SL distance
        )
        sig.setup_class = "SR_FLIP_RETEST"
        sig.current_price = 99.0  # 40% of 2.5% = 1.0% adverse
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {
                "ema9_last": 100.05, "ema21_last": 100.0,
                "momentum": 0.0, "atr_last": 0.5,
            },
        )
        reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "adverse excursion" in reason.lower(), (
            f"SR_FLIP should fire at 40% of 2.5% SL (1.0% adverse), got: {reason!r}"
        )

    def test_sr_flip_does_not_fire_below_40_pct_threshold(self):
        """SR_FLIP_RETEST: adverse excursion must NOT fire when price is only
        30% of SL distance adverse (below the 0.40 threshold)."""
        channel = "360_SCALP"
        sig = _make_signal(
            channel=channel,
            age_seconds=270,
            entry=100.0,
            stop_loss=97.5,  # 2.5% SL; 40% threshold = 1.0% adverse → price 99.0
        )
        sig.setup_class = "SR_FLIP_RETEST"
        sig.current_price = 99.25  # only 0.75% adverse — below 1.0% threshold
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {
                "ema9_last": 100.05, "ema21_last": 100.0,
                "momentum": 0.0, "atr_last": 0.5,
            },
        )
        reason = monitor._check_invalidation(sig)
        assert reason is None or "adverse excursion" not in reason.lower()

    def test_lsr_adverse_excursion_uses_0_40_fraction(self):
        """LIQUIDITY_SWEEP_REVERSAL uses 0.40 fraction: exits at 40% of 2.0% SL = 0.8% adverse.
        LSR patience = 300s; signal must be at least 330s old.
        """
        channel = "360_SCALP"
        # LSR min-age = 300s; use 330s.
        sig = _make_signal(
            channel=channel,
            age_seconds=330,
            entry=100.0,
            stop_loss=98.0,  # 2.0% SL; 40% threshold = 0.8% adverse → price 99.2
        )
        sig.setup_class = "LIQUIDITY_SWEEP_REVERSAL"
        sig.current_price = 99.19  # 0.81% adverse — just above 0.8% threshold (fp-safe)
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {
                "ema9_last": 100.05, "ema21_last": 100.0,
                "momentum": 0.0, "atr_last": 0.5,
            },
        )
        reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "adverse excursion" in reason.lower(), (
            f"LSR should fire at 40% of 2.0% SL (0.8% adverse), got: {reason!r}"
        )

    def test_generic_setup_still_uses_global_055_fraction(self):
        """Non-override setups still use the global 0.55 fraction.

        TREND_PULLBACK_EMA with a 1.0% SL: global 0.55 threshold = 0.55% adverse.
        Below that (0.4% adverse) should not fire.
        """
        from config import INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC
        channel = "360_SCALP"
        # 1.0% SL: entry=100, SL=99.0 → 55% = 0.55% adverse → threshold at 99.45
        sig = _make_signal(
            channel=channel,
            age_seconds=INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC + 30,
            entry=100.0,
            stop_loss=99.0,
        )
        sig.setup_class = "TREND_PULLBACK_EMA"
        sig.current_price = 99.6  # 0.4% adverse — below 0.55 threshold, must not fire
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {
                "ema9_last": 100.05, "ema21_last": 100.0,
                "momentum": 0.0, "atr_last": 0.5,
            },
        )
        reason = monitor._check_invalidation(sig)
        assert reason is None or "adverse excursion" not in reason.lower()

    # ── Early adverse excursion (fires before main patience gate) ──

    def test_sr_flip_adverse_excursion_fires_before_patience_gate(self):
        """SR_FLIP: adverse excursion fires at 120s (< 240s patience gate).

        The early gate opens at 90s for SR_FLIP.  A signal at 120s that has
        already moved 1.0% adverse (= 40% of 2.5% SL) should be killed even
        though the main 240s patience gate is still closed.
        """
        channel = "360_SCALP"
        sig = _make_signal(
            channel=channel,
            age_seconds=120,          # past 90s early gate, before 240s patience gate
            entry=100.0,
            stop_loss=97.5,           # 2.5% SL
        )
        sig.setup_class = "SR_FLIP_RETEST"
        sig.current_price = 99.0     # 1.0% adverse = exactly 40% of 2.5% SL
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {
                "ema9_last": 100.05, "ema21_last": 100.0,
                "momentum": 0.0, "atr_last": 0.5,
            },
        )
        reason = monitor._check_invalidation(sig)
        assert reason is not None, (
            "SR_FLIP at 120s with 1.0% adverse (past 90s early gate) should "
            "be killed before the 240s patience gate opens"
        )
        assert "adverse excursion" in reason.lower()

    def test_sr_flip_too_young_for_early_adverse_excursion(self):
        """SR_FLIP: no kill when signal is younger than the 90s early gate."""
        channel = "360_SCALP"
        sig = _make_signal(
            channel=channel,
            age_seconds=60,           # below 90s early gate
            entry=100.0,
            stop_loss=97.5,
        )
        sig.setup_class = "SR_FLIP_RETEST"
        sig.current_price = 98.0     # well past threshold, but age gate blocks
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {"momentum": -0.5},
        )
        reason = monitor._check_invalidation(sig)
        assert reason is None, (
            f"SR_FLIP at 60s should not fire (early gate requires >= 90s), got: {reason!r}"
        )

    def test_lsr_adverse_excursion_fires_before_patience_gate(self):
        """LSR: adverse excursion fires at 180s (< 300s patience gate).

        The early gate opens at 120s for LSR.  A signal at 180s that has
        moved 0.81% adverse (> 40% of 2.0% SL) should be killed.
        """
        channel = "360_SCALP"
        sig = _make_signal(
            channel=channel,
            age_seconds=180,          # past 120s early gate, before 300s patience gate
            entry=100.0,
            stop_loss=98.0,           # 2.0% SL
        )
        sig.setup_class = "LIQUIDITY_SWEEP_REVERSAL"
        sig.current_price = 99.19    # 0.81% adverse > 0.8% threshold (fp-safe)
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {
                "ema9_last": 100.05, "ema21_last": 100.0,
                "momentum": 0.0, "atr_last": 0.5,
            },
        )
        reason = monitor._check_invalidation(sig)
        assert reason is not None, (
            "LSR at 180s with >0.8% adverse (past 120s early gate) should "
            "be killed before the 300s patience gate opens"
        )
        assert "adverse excursion" in reason.lower()

    def test_early_adverse_excursion_skipped_when_in_profit(self):
        """Early adverse excursion must not fire when signal is already profitable.

        If the signal has moved > 0.5 × SL_dist in the right direction, the
        profit-protection gate fires first and returns None — even if the
        current price then dips within the early-adverse window.
        """
        channel = "360_SCALP"
        sig = _make_signal(
            channel=channel,
            age_seconds=120,
            entry=100.0,
            stop_loss=97.5,
        )
        sig.setup_class = "SR_FLIP_RETEST"
        sig.current_price = 101.5    # 1.5% profit = 60% of 2.5% SL_dist — in profit zone
        monitor, _, _ = self._build_monitor(
            {sig.signal_id: sig},
            indicators_fn=lambda sym: {"momentum": 0.0},
        )
        reason = monitor._check_invalidation(sig)
        assert reason is None, (
            f"Profit-protection gate should block early adverse excursion, got: {reason!r}"
        )


class TestOnHighlightCallback:
    """TradeMonitor.on_highlight_callback is called for TP2/TP3 but not TP1 or SL."""

    def _build_monitor(self, active, channel_map=None):
        removed = []
        sent = []
        highlight_calls = []

        async def mock_send(chat_id, text):
            sent.append((chat_id, text))

        data_store = MagicMock()
        data_store.get_candles.side_effect = _make_get_candles_from_active(active)
        data_store.ticks = {}

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.append(sid),
            update_signal=MagicMock(),
        )
        monitor.on_highlight_callback = lambda sig, tp, pnl: highlight_calls.append((sig, tp, pnl))
        return monitor, removed, highlight_calls

    @pytest.mark.asyncio
    async def test_highlight_called_on_tp2_long(self):
        sig = _make_signal(
            direction=Direction.LONG,
            entry=30000.0, stop_loss=29850.0,
            tp1=30150.0, tp2=30300.0, tp3=30450.0,
            age_seconds=200.0,
        )
        active = {sig.signal_id: sig}
        monitor, _, highlight_calls = self._build_monitor(active)

        # Price hits TP2
        sig.current_price = 30300.0
        await monitor._evaluate_signal(sig)

        assert len(highlight_calls) == 1
        _, tp, pnl = highlight_calls[0]
        assert tp == 2
        assert pnl > 0

    @pytest.mark.asyncio
    async def test_highlight_called_on_tp3_long(self):
        sig = _make_signal(
            direction=Direction.LONG,
            entry=30000.0, stop_loss=29850.0,
            tp1=30150.0, tp2=30300.0, tp3=30450.0,
            age_seconds=200.0,
        )
        active = {sig.signal_id: sig}
        monitor, _, highlight_calls = self._build_monitor(active)

        # Price hits TP3
        sig.current_price = 30450.0
        await monitor._evaluate_signal(sig)

        assert len(highlight_calls) == 1
        _, tp, pnl = highlight_calls[0]
        assert tp == 3
        assert pnl > 0

    @pytest.mark.asyncio
    async def test_highlight_not_called_on_tp1(self):
        sig = _make_signal(
            direction=Direction.LONG,
            entry=30000.0, stop_loss=29850.0,
            tp1=30150.0, tp2=30300.0, tp3=30450.0,
            age_seconds=200.0,
        )
        active = {sig.signal_id: sig}
        monitor, _, highlight_calls = self._build_monitor(active)

        # Price only hits TP1
        sig.current_price = 30150.0
        await monitor._evaluate_signal(sig)

        assert highlight_calls == []

    @pytest.mark.asyncio
    async def test_highlight_not_called_on_sl(self):
        sig = _make_signal(
            direction=Direction.LONG,
            entry=30000.0, stop_loss=29850.0,
            tp1=30150.0, tp2=30300.0, tp3=30450.0,
            age_seconds=200.0,
        )
        active = {sig.signal_id: sig}
        monitor, _, highlight_calls = self._build_monitor(active)

        # Price hits SL
        sig.current_price = 29800.0
        await monitor._evaluate_signal(sig)

        assert highlight_calls == []

    @pytest.mark.asyncio
    async def test_highlight_called_on_tp2_short(self):
        sig = _make_signal(
            direction=Direction.SHORT,
            entry=30000.0, stop_loss=30150.0,
            tp1=29850.0, tp2=29700.0, tp3=29550.0,
            age_seconds=200.0,
        )
        active = {sig.signal_id: sig}
        monitor, _, highlight_calls = self._build_monitor(active)

        # Price hits TP2 for SHORT
        sig.current_price = 29700.0
        await monitor._evaluate_signal(sig)

        assert len(highlight_calls) == 1
        _, tp, pnl = highlight_calls[0]
        assert tp == 2
        assert pnl > 0

    @pytest.mark.asyncio
    async def test_highlight_called_on_tp3_short(self):
        sig = _make_signal(
            direction=Direction.SHORT,
            entry=30000.0, stop_loss=30150.0,
            tp1=29850.0, tp2=29700.0, tp3=29550.0,
            age_seconds=200.0,
        )
        active = {sig.signal_id: sig}
        monitor, _, highlight_calls = self._build_monitor(active)

        # Price hits TP3 for SHORT
        sig.current_price = 29550.0
        await monitor._evaluate_signal(sig)

        assert len(highlight_calls) == 1
        _, tp, pnl = highlight_calls[0]
        assert tp == 3
        assert pnl > 0

    @pytest.mark.asyncio
    async def test_no_highlight_when_callback_not_set(self):
        """TradeMonitor works correctly when on_highlight_callback is None."""
        sig = _make_signal(
            direction=Direction.LONG,
            entry=30000.0, stop_loss=29850.0,
            tp1=30150.0, tp2=30300.0, tp3=30450.0,
            age_seconds=200.0,
        )
        active = {sig.signal_id: sig}

        data_store = MagicMock()
        data_store.get_candles.side_effect = _make_get_candles_from_active(active)
        data_store.ticks = {}

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=MagicMock(return_value=None),
            get_active_signals=lambda: dict(active),
            remove_signal=MagicMock(),
            update_signal=MagicMock(),
        )
        # on_highlight_callback is None by default
        assert monitor.on_highlight_callback is None

        # Should not raise even when TP2 is hit
        sig.current_price = 30300.0
        await monitor._evaluate_signal(sig)  # must not raise


# ---------------------------------------------------------------------------
# Tests for stage-aware trailing stop logic (PR_08)
# ---------------------------------------------------------------------------

class TestTrailingStopStageTransitions:
    """Tests for _compute_trailing_stop and _update_trailing_stage."""

    def test_trailing_stage_0_initial_trail(self):
        """Stage 0: standard 2× ATR trailing distance."""
        from src.channels.base import TrailingStopState
        from src.trade_monitor import _compute_trailing_stop

        state = TrailingStopState(initial_atr=100.0, current_atr=100.0, stage=0)
        sig = Signal(
            channel="SCALP", symbol="BTCUSDT", direction=Direction.LONG,
            entry=50000.0, stop_loss=49800.0, tp1=50500.0, tp2=51000.0, tp3=51500.0,
        )
        new_sl = _compute_trailing_stop(sig, 50300.0, 100.0, state, atr_percentile=50.0)
        # Stage 0 → 2.0× ATR = 200; candidate = 50300 - 200 = 50100; max(49800, 50100) = 50100
        assert new_sl == 50100.0

    def test_trailing_stage_1_breakeven(self):
        """Stage 1 (TP1 hit): 1.0× ATR trailing, SL at breakeven."""
        from src.channels.base import TrailingStopState
        from src.trade_monitor import _update_trailing_stage

        state = TrailingStopState(initial_atr=100.0, current_atr=100.0, stage=0)
        sig = Signal(
            channel="SCALP", symbol="BTCUSDT", direction=Direction.LONG,
            entry=50000.0, stop_loss=49800.0, tp1=50500.0, tp2=51000.0, tp3=51500.0,
        )
        _update_trailing_stage(sig, 50600.0, state)  # Price above TP1
        assert state.stage == 1
        assert sig.trailing_stage == 1
        assert sig.stop_loss == 50000.0  # Moved to breakeven
        assert sig.partial_close_pct == 0.4

    def test_trailing_stage_2_tight_trail(self):
        """Stage 2 (TP2 hit): 0.5× ATR tight trail."""
        from src.channels.base import TrailingStopState
        from src.trade_monitor import _update_trailing_stage, _compute_trailing_stop

        state = TrailingStopState(initial_atr=100.0, current_atr=100.0, stage=1)
        sig = Signal(
            channel="SCALP", symbol="BTCUSDT", direction=Direction.LONG,
            entry=50000.0, stop_loss=50000.0, tp1=50500.0, tp2=51000.0, tp3=51500.0,
            trailing_stage=1,
        )
        _update_trailing_stage(sig, 51100.0, state)  # Price above TP2
        assert state.stage == 2
        assert sig.trailing_stage == 2
        assert sig.partial_close_pct == 0.7
        # Tight trail: 0.5 × 100 = 50; candidate = 51100 - 50 = 51050
        new_sl = _compute_trailing_stop(sig, 51100.0, 100.0, state, atr_percentile=50.0)
        assert new_sl == 51050.0

    def test_trailing_high_vol_widens_buffer(self):
        """High ATR percentile widens trailing buffer by 1.3×."""
        from src.channels.base import TrailingStopState
        from src.trade_monitor import _compute_trailing_stop

        state = TrailingStopState(initial_atr=100.0, current_atr=100.0, stage=0)
        sig = Signal(
            channel="SCALP", symbol="BTCUSDT", direction=Direction.LONG,
            entry=50000.0, stop_loss=49700.0, tp1=50500.0, tp2=51000.0, tp3=51500.0,
        )
        new_sl = _compute_trailing_stop(sig, 50300.0, 100.0, state, atr_percentile=90.0)
        # Stage 0 → 2.0× ATR = 200; vol_adj 1.3 → trail = 260; candidate = 50300 - 260 = 50040
        assert new_sl == 50040.0

    def test_trailing_low_vol_tightens_buffer(self):
        """Low ATR percentile tightens trailing buffer by 0.7×."""
        from src.channels.base import TrailingStopState
        from src.trade_monitor import _compute_trailing_stop

        state = TrailingStopState(initial_atr=100.0, current_atr=100.0, stage=0)
        sig = Signal(
            channel="SCALP", symbol="BTCUSDT", direction=Direction.LONG,
            entry=50000.0, stop_loss=49800.0, tp1=50500.0, tp2=51000.0, tp3=51500.0,
        )
        new_sl = _compute_trailing_stop(sig, 50300.0, 100.0, state, atr_percentile=10.0)
        # Stage 0 → 2.0× ATR = 200; vol_adj 0.7 → trail = 140; candidate = 50300 - 140 = 50160
        assert new_sl == 50160.0

    def test_trailing_never_widens_for_long(self):
        """SL should never move backwards (lower) for a LONG trade."""
        from src.channels.base import TrailingStopState
        from src.trade_monitor import _compute_trailing_stop

        state = TrailingStopState(initial_atr=100.0, current_atr=100.0, stage=0)
        sig = Signal(
            channel="SCALP", symbol="BTCUSDT", direction=Direction.LONG,
            entry=50000.0, stop_loss=50200.0, tp1=50500.0, tp2=51000.0, tp3=51500.0,
        )
        # Price at 50300 → candidate = 50300 - 200 = 50100 < current SL 50200
        new_sl = _compute_trailing_stop(sig, 50300.0, 100.0, state, atr_percentile=50.0)
        assert new_sl == 50200.0  # Should not move backwards

    def test_trailing_short_direction(self):
        """Trailing stop works correctly for SHORT direction."""
        from src.channels.base import TrailingStopState
        from src.trade_monitor import _compute_trailing_stop, _update_trailing_stage

        state = TrailingStopState(initial_atr=100.0, current_atr=100.0, stage=0)
        sig = Signal(
            channel="SCALP", symbol="BTCUSDT", direction=Direction.SHORT,
            entry=50000.0, stop_loss=50200.0, tp1=49500.0, tp2=49000.0, tp3=48500.0,
        )
        new_sl = _compute_trailing_stop(sig, 49700.0, 100.0, state, atr_percentile=50.0)
        # Stage 0 → 2.0× ATR = 200; candidate = 49700 + 200 = 49900; min(50200, 49900) = 49900
        assert new_sl == 49900.0

        # TP1 hit for short
        _update_trailing_stage(sig, 49400.0, state)
        assert state.stage == 1
        assert sig.stop_loss == 50000.0  # Breakeven


# ---------------------------------------------------------------------------
# Terminal-status guard (regression: duplicate Telegram messages, 2026-05-08)
# ---------------------------------------------------------------------------
# Owner reported (PDF/screenshots) the same lifecycle event posted multiple
# times for a single signal:
#   - INVALIDATED ZECUSDT @ 04:10:11 posted TWICE in same second
#   - SL HIT FLOCKUSDT @ 04:10:11 + identical SL HIT @ 04:16:29 (same PnL)
#
# Root cause: ``_evaluate_signal`` had no top-of-function check for
# already-terminal status.  An asyncio race in ``_check_all`` /
# ``asyncio.gather`` could re-evaluate the same Signal in a single tick
# (e.g. if ``_active_signals`` had duplicate keys after a disk-restore
# edge case), producing duplicate ``_post_update`` calls.  The fix adds
# a guard so any signal whose status is already in ``_TERMINAL_STATUSES``
# returns immediately.


class TestTerminalStatusGuard:
    """``_evaluate_signal`` must short-circuit on terminal-status signals."""

    @pytest.fixture
    def monitor(self):
        from unittest.mock import AsyncMock
        active: Dict[str, Signal] = {}
        send_tg = AsyncMock(return_value=True)
        data_store = MagicMock()
        data_store.get_candles.side_effect = _make_get_candles_from_active(active)
        m = TradeMonitor(
            data_store=data_store,
            send_telegram=send_tg,
            get_active_signals=lambda: active,
            remove_signal=lambda sid: active.pop(sid, None),
            update_signal=MagicMock(),
        )
        # Replace _post_update with a tracker — the production helper
        # short-circuits when CHANNEL_TELEGRAM_MAP[sig.channel] is empty
        # (which it is in test env), so counting _post_update calls
        # directly is the reliable way to assert the guard works.
        post_calls: list = []

        async def _track_post(sig, event):
            post_calls.append((sig.signal_id, sig.status, event))
            return None

        m._post_update = _track_post  # type: ignore[assignment]
        m._post_signal_closed = AsyncMock(return_value=None)  # type: ignore[assignment]
        m._broker_close_full = AsyncMock(return_value=None)  # type: ignore[assignment]
        m._active_for_test = active
        m._post_calls_for_test = post_calls
        return m

    @pytest.mark.parametrize("terminal_status", [
        "SL_HIT",
        "BREAKEVEN_EXIT",
        "PROFIT_LOCKED",
        "INVALIDATED",
        "EXPIRED",
        "CANCELLED",
        "FULL_TP_HIT",
        "TP3_HIT",
        "CLOSED",
    ])
    async def test_terminal_status_short_circuits_evaluation(
        self, monitor, terminal_status,
    ):
        """A signal whose status is already terminal must not re-fire any
        lifecycle event when ``_evaluate_signal`` is called."""
        sig = _make_signal(age_seconds=600)
        sig.status = terminal_status
        # Set price at or past SL — pre-fix this would re-trigger the SL
        # handler and post another SL HIT message.
        sig.current_price = 29800.0  # below SL of 29850

        await monitor._evaluate_signal(sig)

        # Zero Telegram sends.  The guard exited before any handler ran.
        assert len(monitor._post_calls_for_test) == 0

    @pytest.mark.parametrize("active_status", ["ACTIVE", "TP1_HIT", "TP2_HIT"])
    async def test_non_terminal_status_continues_evaluation(
        self, monitor, active_status,
    ):
        """Pre-terminal statuses (ACTIVE, TP1_HIT, TP2_HIT) must keep
        evaluating — those signals are still in flight for higher TPs
        or invalidation checks."""
        sig = _make_signal(age_seconds=600)
        sig.status = active_status
        # Don't trigger any SL/TP — just verify the guard doesn't block
        sig.current_price = 30000.0  # at entry, no SL/TP triggers

        # Should not raise; the guard must allow this through.
        await monitor._evaluate_signal(sig)

    async def test_concurrent_evaluation_only_one_fires(self, monitor):
        """Reproduce the duplicate-event race: ``asyncio.gather`` over
        the same Signal should still result in only ONE close event,
        because the second task sees the terminal status set by the
        first and short-circuits via the guard."""
        import asyncio

        sig = _make_signal(age_seconds=600)
        sig.status = "ACTIVE"
        sig.current_price = 29800.0  # below SL → SL handler fires
        monitor._active_for_test[sig.signal_id] = sig

        # Race two concurrent _evaluate_signal calls on the same sig.
        # Pre-fix, both would race through the SL handler before either
        # awaited ``_remove`` and produce two SL HIT messages.
        await asyncio.gather(
            monitor._evaluate_signal(sig),
            monitor._evaluate_signal(sig),
        )

        # Exactly ONE Telegram send for the SL_HIT — the second concurrent
        # task hit the terminal-status guard and exited.
        # (Note: signal-closed AI post is fire-and-forget via a separate
        # async task and isn't counted toward send_telegram here because
        # engine_context_fn is None in the test fixture.)
        assert len(monitor._post_calls_for_test) == 1


# ============================================================================
# Invalidation user-modes + MFE protection + ATR-trailing kill
# OWNER_BRIEF B17 + §3.2a (capital preservation doctrine, 2026-05-17)
# PR #4 — feat/invalidation-user-modes
# ============================================================================


class TestInvalidationModes:
    """Mode-gated invalidation behaviour: loose / standard / tight.

    Engine-side TradeMonitor uses ``INVALIDATION_MODE_DEFAULT`` from config
    (default ``standard``).  Per-user app-side execution reads
    ``user_invalidation_settings.mode`` directly when Phase 4 lands; for now
    we exercise the engine path via the env-overridable config constant.
    """

    def _build_monitor(self, active, regime_label="TRENDING_DOWN", **kwargs):
        """Wire a monitor with a regime detector returning the given label.

        Used by mode tests to force a regime-flip condition; combined with
        the mode patch, asserts which kills do/don't fire per mode.
        """
        removed = []
        sent = []

        async def mock_send(chat_id, text):
            sent.append((chat_id, text))

        data_store = MagicMock()
        data_store.ticks = {}
        closes = [30000.0] * 25
        data_store.get_candles.return_value = {
            "close": closes,
            "open": closes,
            "high": closes,
            "low": closes,
            "volume": [1.0] * 25,
        }

        regime_detector = MagicMock()
        regime_detector.classify.return_value = MagicMock(
            regime=MagicMock(value=regime_label)
        )

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.append(sid),
            update_signal=MagicMock(),
            regime_detector=regime_detector,
            indicators_fn=lambda sym: {
                "ema9_last": 99.0, "ema21_last": 100.0,
                "momentum": -0.5, "atr_last": 0.5,
            },
        )
        return monitor

    def test_loose_mode_skips_all_non_sl_kills(self):
        """Loose mode: regime-flip / EMA-cross / momentum-loss are all skipped.

        Capital-preservation-conservative — only SL itself + max-hold can
        close the signal.  For users who want signals to develop fully.
        """
        sig = _make_signal(direction=Direction.LONG, age_seconds=700.0)
        sig.current_price = sig.entry  # neutral position
        monitor = self._build_monitor({sig.signal_id: sig}, regime_label="TRENDING_DOWN")

        with patch("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "loose"):
            reason = monitor._check_invalidation(sig)
        assert reason is None, (
            "Loose mode must skip the regime-flip kill that standard/tight "
            f"would fire on a TRENDING_DOWN flip against a LONG signal. "
            f"Got: {reason!r}"
        )

    def test_standard_mode_fires_regime_flip_kill(self):
        """Standard mode = engine baseline: regime-flip against direction kills."""
        sig = _make_signal(direction=Direction.LONG, age_seconds=700.0)
        sig.current_price = sig.entry
        monitor = self._build_monitor({sig.signal_id: sig}, regime_label="TRENDING_DOWN")

        with patch("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "standard"):
            reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "TRENDING_DOWN" in reason

    def test_unknown_mode_falls_back_to_standard(self):
        """An invalid mode token must not skip kills — falls back to standard.

        Defense-in-depth: even if a bad env value slips through validation,
        the engine continues protecting the book by running standard kills.
        """
        sig = _make_signal(direction=Direction.LONG, age_seconds=700.0)
        sig.current_price = sig.entry
        monitor = self._build_monitor({sig.signal_id: sig}, regime_label="TRENDING_DOWN")

        with patch("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "aggressive_xyz"):
            reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "TRENDING_DOWN" in reason

    # --------------------------------------------------------------
    # MFE protection (applies to standard + tight, not loose)
    # --------------------------------------------------------------

    def test_mfe_protection_skips_regime_kill_after_pre_tp(self):
        """When pre_tp_hit=True and price still on favourable side of entry,
        regime-flip kill must NOT fire — MFE protection per §3.2a.

        Rationale: pre-TP fired → real partial banked + residual SL at BE.
        Killing the residual on a regime wobble destroys TP1 optionality.
        """
        sig = _make_signal(direction=Direction.LONG, age_seconds=700.0)
        sig.pre_tp_hit = True
        sig.current_price = sig.entry + 50  # still in favourable territory
        sig.max_favorable_excursion_pct = 0.5  # peaked at +0.5%
        monitor = self._build_monitor({sig.signal_id: sig}, regime_label="TRENDING_DOWN")

        with patch("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "standard"):
            reason = monitor._check_invalidation(sig)
        assert reason is None, (
            "MFE protection must skip the regime-flip kill on a pre-TP'd "
            f"signal still in profit.  Got: {reason!r}"
        )

    def test_mfe_protection_does_not_apply_when_price_below_entry(self):
        """If price has retraced past entry (BE-stop range), MFE protection
        no longer applies — standard kill checks resume.

        Doctrinal correctness: once price is at/below entry on a LONG,
        the residual is sitting on its BE-stop.  At that point the kill
        gates fire normally to provide an early-exit option before SL.
        """
        sig = _make_signal(direction=Direction.LONG, age_seconds=700.0)
        sig.pre_tp_hit = True
        sig.current_price = sig.entry - 50  # reversed past entry
        sig.max_favorable_excursion_pct = 0.5
        monitor = self._build_monitor({sig.signal_id: sig}, regime_label="TRENDING_DOWN")

        with patch("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "standard"):
            reason = monitor._check_invalidation(sig)
        # Regime kill should fire — MFE protection no longer applies
        assert reason is not None
        assert "TRENDING_DOWN" in reason

    def test_mfe_protection_skipped_in_loose_mode(self):
        """Loose mode short-circuits before MFE protection — no kills fire
        at all on a pre-TP'd signal in loose mode, regardless of MFE state.
        """
        sig = _make_signal(direction=Direction.LONG, age_seconds=700.0)
        sig.pre_tp_hit = True
        sig.current_price = sig.entry - 50  # reversed past entry
        sig.max_favorable_excursion_pct = 0.5
        monitor = self._build_monitor({sig.signal_id: sig}, regime_label="TRENDING_DOWN")

        with patch("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "loose"):
            reason = monitor._check_invalidation(sig)
        assert reason is None


class TestTrailingInvalidation:
    """ATR-trailing kill (tight-mode signature per B17, 2026-05-17).

    Arms when MFE >= 0.3R; fires when price retraces >= 50% of MFE peak.
    Standalone helper ``_check_trailing_invalidation`` is a pure function on
    signal state — testable independently of the wider mode dispatcher.
    """

    def _make_monitor(self):
        async def mock_send(*_a, **_kw):
            pass
        data_store = MagicMock()
        data_store.ticks = {}
        return TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: {},
            remove_signal=lambda sid: None,
            update_signal=MagicMock(),
        )

    def test_trailing_not_armed_below_mfe_r_threshold(self):
        """MFE < 0.3R → not armed → return None.

        Sig: entry 30000, SL 29400 (200 below) → SL_dist_pct ≈ 0.667%.
        MFE 0.15% → MFE_R = 0.15 / 0.667 ≈ 0.225 < 0.3 threshold.
        """
        sig = _make_signal(entry=30000.0, stop_loss=29800.0)
        sig.max_favorable_excursion_pct = 0.15
        sig.current_price = 30030.0  # currently +0.1%
        monitor = self._make_monitor()
        assert monitor._check_trailing_invalidation(sig) is None

    def test_trailing_not_fired_when_close_to_peak(self):
        """MFE >= 0.3R but retrace < 50% → not fired yet.

        SL_dist_pct ≈ 0.667%.  MFE 0.5% → MFE_R ≈ 0.75 (armed).
        Current +0.4% → retrace = (0.5 - 0.4) / 0.5 = 20% < 50% threshold.
        """
        sig = _make_signal(entry=30000.0, stop_loss=29800.0)
        sig.max_favorable_excursion_pct = 0.5
        sig.current_price = 30000.0 * 1.004  # +0.4% (20% retrace from 0.5% peak)
        monitor = self._make_monitor()
        assert monitor._check_trailing_invalidation(sig) is None

    def test_trailing_fires_at_50pct_retrace(self):
        """Armed (MFE_R >= 0.3) + retrace >= 50% → kill fires."""
        sig = _make_signal(entry=30000.0, stop_loss=29800.0)
        sig.max_favorable_excursion_pct = 0.5
        sig.current_price = 30000.0 * 1.0025  # +0.25% (50% retrace from 0.5% peak)
        monitor = self._make_monitor()
        reason = monitor._check_trailing_invalidation(sig)
        assert reason is not None
        assert "trailing invalidation" in reason.lower()
        assert "MFE peak" in reason

    def test_trailing_fires_when_reversed_past_entry(self):
        """Retrace > 100% (past entry) → still fires (capital preserved
        below BE — though typically BE-stop would have already triggered).
        """
        sig = _make_signal(entry=30000.0, stop_loss=29800.0)
        sig.max_favorable_excursion_pct = 0.5
        sig.current_price = 30000.0 * 0.999  # below entry
        monitor = self._make_monitor()
        reason = monitor._check_trailing_invalidation(sig)
        assert reason is not None

    def test_trailing_short_direction(self):
        """SHORT signal at +0.5% MFE (price 0.5% below entry), retraces
        50% back toward entry → kill fires.
        """
        sig = _make_signal(direction=Direction.SHORT, entry=30000.0, stop_loss=30200.0)
        sig.max_favorable_excursion_pct = 0.5
        sig.current_price = 30000.0 * 0.9975  # -0.25% (50% retrace)
        monitor = self._make_monitor()
        reason = monitor._check_trailing_invalidation(sig)
        assert reason is not None

    def test_trailing_skipped_when_mfe_zero(self):
        """Signal never went favourable → trailing has nothing to track."""
        sig = _make_signal(entry=30000.0, stop_loss=29800.0)
        sig.max_favorable_excursion_pct = 0.0
        sig.current_price = sig.entry
        monitor = self._make_monitor()
        assert monitor._check_trailing_invalidation(sig) is None

    def test_trailing_skipped_when_sl_at_entry(self):
        """BE-stop at exactly entry → SL_dist_pct=0 → trailing skipped.

        BE-stop already protects the residual; the trailing kill is for
        the pre-BE phase.  Returning None here prevents division-by-zero.
        """
        sig = _make_signal(entry=30000.0, stop_loss=30000.0)
        sig.max_favorable_excursion_pct = 0.5
        sig.current_price = 30000.0 * 1.001
        monitor = self._make_monitor()
        assert monitor._check_trailing_invalidation(sig) is None

    def test_trailing_kill_runs_in_tight_mode(self):
        """End-to-end: tight mode dispatches the trailing kill from
        _check_invalidation when its conditions are met.
        """
        sig = _make_signal(entry=30000.0, stop_loss=29800.0, age_seconds=700.0)
        sig.max_favorable_excursion_pct = 0.5
        sig.current_price = 30000.0 * 1.0025  # 50% retrace from 0.5% peak

        async def mock_send(*_a, **_kw):
            pass
        data_store = MagicMock()
        data_store.ticks = {}
        # Provide candles so the regime/momentum path doesn't fall through to None
        closes = [30000.0] * 25
        data_store.get_candles.return_value = {
            "close": closes, "open": closes, "high": closes, "low": closes,
            "volume": [1.0] * 25,
        }
        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: {sig.signal_id: sig},
            remove_signal=lambda sid: None,
            update_signal=MagicMock(),
            indicators_fn=lambda sym: {
                "ema9_last": 101.0, "ema21_last": 100.0,  # bullish-aligned
                "momentum": 0.5, "atr_last": 0.5,
            },
        )

        with patch("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "tight"):
            reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "trailing" in reason.lower()

    def test_trailing_kill_not_in_standard_mode(self):
        """Standard mode does NOT fire the trailing kill — that's a
        tight-mode-only signature per B17.
        """
        sig = _make_signal(entry=30000.0, stop_loss=29800.0, age_seconds=700.0)
        sig.max_favorable_excursion_pct = 0.5
        sig.current_price = 30000.0 * 1.0025  # 50% retrace condition

        async def mock_send(*_a, **_kw):
            pass
        data_store = MagicMock()
        data_store.ticks = {}
        closes = [30000.0] * 25
        data_store.get_candles.return_value = {
            "close": closes, "open": closes, "high": closes, "low": closes,
            "volume": [1.0] * 25,
        }
        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: {sig.signal_id: sig},
            remove_signal=lambda sid: None,
            update_signal=MagicMock(),
            indicators_fn=lambda sym: {
                "ema9_last": 101.0, "ema21_last": 100.0,
                "momentum": 0.5, "atr_last": 0.5,
            },
        )

        with patch("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "standard"):
            reason = monitor._check_invalidation(sig)
        # In standard mode the trailing kill is disarmed.  Other gates may
        # or may not fire depending on indicators, but specifically no
        # "trailing" reason should appear.
        if reason is not None:
            assert "trailing" not in reason.lower()


class TestCategoriseKillReason:
    """OWNER_BRIEF B17 — the new ``trailing_invalidation`` family token must
    be recognised by the invalidation audit categoriser so truth-report
    histograms surface tight-mode kills as a distinct row."""

    def test_trailing_invalidation_categorised(self):
        from src.invalidation_audit import categorise_kill_reason
        msg = (
            "trailing invalidation (MFE peak +0.42%, current +0.20%, "
            "retraced 50% of peak at MFE_R=0.63) – capital preserved"
        )
        assert categorise_kill_reason(msg) == "trailing_invalidation"

    def test_momentum_against_thesis_aliased_to_momentum_loss(self):
        """The direction-aware 'momentum against thesis' variant must
        categorise the same as the older 'momentum loss' wording.
        Pre-PR #4 the audit categoriser only matched 'momentum loss' so
        all direction-aware kills fell into 'other'.
        """
        from src.invalidation_audit import categorise_kill_reason
        msg = (
            "momentum against thesis (momentum=-0.250 < -0.100 for LONG, "
            "2 consecutive readings) – signal thesis invalidated"
        )
        assert categorise_kill_reason(msg) == "momentum_loss"

    def test_legacy_categories_unchanged(self):
        from src.invalidation_audit import categorise_kill_reason
        assert categorise_kill_reason("regime shift to TRENDING_DOWN") == "regime_shift"
        assert (
            categorise_kill_reason("EMA bearish crossover (EMA9 < EMA21)")
            == "ema_crossover"
        )
        assert categorise_kill_reason("momentum loss") == "momentum_loss"
        assert categorise_kill_reason("some other unmatched") == "other"

    def test_adverse_excursion_categorised(self):
        """New invalidation rule (2026-05-20) must land in its own
        family token so the truth-report audit table shows it as a
        distinct row (PROT / PREM / NEUTRAL / EV per kill)."""
        from src.invalidation_audit import categorise_kill_reason
        msg = (
            "adverse excursion (-0.85% against, 0.71×SL_dist, "
            "momentum=0.030 not confirming) – signal thesis invalidated"
        )
        assert categorise_kill_reason(msg) == "adverse_excursion"

    def test_adverse_excursion_does_not_collide_with_momentum_loss(self):
        """The adverse_excursion diagnostic message contains the
        substring 'momentum=' which historically would match the
        'momentum loss' / 'momentum against thesis' branches.  The
        categoriser must check 'adverse excursion' first to avoid
        misclassification — pin that ordering here so a future
        refactor can't silently re-break it."""
        from src.invalidation_audit import categorise_kill_reason
        msg_with_momentum_substring = (
            "adverse excursion (+0.91% against, 0.78×SL_dist, "
            "momentum=-0.020 not confirming) – signal thesis invalidated"
        )
        assert (
            categorise_kill_reason(msg_with_momentum_substring)
            == "adverse_excursion"
        )


# ============================================================================
# Pre-TP partial-close weighted PnL (fix/pretp-partial-weighted-pnl)
# ============================================================================
# OWNER_BRIEF §3.2a (capital preservation doctrine).  Pre-PR-#fix the signal
# pnl_pct on a BE-exit reported 0.00% even when 50% of the position banked
# +0.30% earlier — the Signals tab showed BREAKEVEN_EXIT +0.00% on signals
# the subscriber had actually netted positive on.  This block exercises the
# weighted-blend computation in _set_realized_pnl.


class TestPreTpPartialWeightedPnl:
    """OWNER_BRIEF §3.2a — terminal pnl_pct must blend the realised partial
    contribution with the residual exit when both ``partial_close_pct`` and
    ``pre_tp_pct`` are set (i.e., the broker actually fired a pre-TP
    partial per PR #411).  Backward-compat preserved when either field is
    zero — same residual-only math as pre-PR-#411."""

    def test_be_exit_after_50pct_partial_at_0_30_yields_weighted_pnl(self):
        """Classic case: pre-TP banked 50% at +0.30%, then BE-stop hit.
        Weighted PnL = 0.5 * 0.30 + 0.5 * 0.00 = +0.15%.  Reclassifies
        from BREAKEVEN_EXIT to PROFIT_LOCKED.
        """
        sig = _make_signal(entry=30000.0)
        sig.pre_tp_hit = True
        sig.pre_tp_pct = 0.30
        sig.partial_close_pct = 0.50
        # BE-stop exit at exactly entry
        TradeMonitor._set_realized_pnl(sig, exit_price=sig.entry)
        assert sig.pnl_pct == pytest.approx(0.15, abs=1e-6)

    def test_be_exit_after_100pct_partial_yields_full_pre_tp_pnl(self):
        """If the user picked 100% grab fraction, nothing rides; the
        residual contributes 0 weight and the whole signal's pnl_pct
        equals pre_tp_pct.
        """
        sig = _make_signal(entry=30000.0)
        sig.pre_tp_hit = True
        sig.pre_tp_pct = 0.40
        sig.partial_close_pct = 1.00
        # Even if exit_price implies a loss on the residual, residual
        # weight is zero, so signal pnl == pre_tp_pct.
        TradeMonitor._set_realized_pnl(sig, exit_price=sig.entry * 0.99)
        assert sig.pnl_pct == pytest.approx(0.40, abs=1e-6)

    def test_be_exit_after_30pct_partial_at_0_50_pct_long(self):
        """User picked B17 floor 30%; pre-TP banked +0.50%; BE-stop hit.
        Weighted: 0.30 * 0.50 + 0.70 * 0.00 = +0.15%.
        """
        sig = _make_signal(entry=30000.0, direction=Direction.LONG)
        sig.pre_tp_hit = True
        sig.pre_tp_pct = 0.50
        sig.partial_close_pct = 0.30
        TradeMonitor._set_realized_pnl(sig, exit_price=sig.entry)
        assert sig.pnl_pct == pytest.approx(0.15, abs=1e-6)

    def test_residual_loss_after_partial_still_nets_positive(self):
        """Pre-TP banked 50% at +0.30%; residual exits at -0.20% (somehow
        moved past BE-stop in test scenario).  Weighted: 0.5*0.30 +
        0.5*(-0.20) = +0.05%.  Still positive — partial cushioned the
        residual loss."""
        sig = _make_signal(entry=30000.0, direction=Direction.LONG)
        sig.pre_tp_hit = True
        sig.pre_tp_pct = 0.30
        sig.partial_close_pct = 0.50
        # Exit at -0.20% from entry
        TradeMonitor._set_realized_pnl(sig, exit_price=sig.entry * (1 - 0.002))
        # 0.5 * 0.30 + 0.5 * -0.20 = 0.15 - 0.10 = 0.05
        assert sig.pnl_pct == pytest.approx(0.05, abs=1e-6)

    def test_short_direction_weighted_pnl(self):
        """SHORT signal mirror — pre-TP banked 50% at +0.40%, BE-stop at
        entry → +0.20% weighted."""
        sig = _make_signal(entry=30000.0, direction=Direction.SHORT)
        sig.pre_tp_hit = True
        sig.pre_tp_pct = 0.40
        sig.partial_close_pct = 0.50
        TradeMonitor._set_realized_pnl(sig, exit_price=sig.entry)
        assert sig.pnl_pct == pytest.approx(0.20, abs=1e-6)

    def test_partial_close_zero_falls_back_to_residual_only(self):
        """Pre-TP fired (e.g., broker disabled, no fill) — partial_close_pct
        stays at 0.  Weighted blend must NOT kick in; signal pnl_pct equals
        residual-only computation (entry → exit_price).  Backward-compat
        with the broker-disabled signal-only mode from PR #411.
        """
        sig = _make_signal(entry=30000.0)
        sig.pre_tp_hit = True
        sig.pre_tp_pct = 0.30          # pre-TP "triggered" telemetry
        sig.partial_close_pct = 0.0    # but broker didn't fill
        TradeMonitor._set_realized_pnl(sig, exit_price=sig.entry)
        assert sig.pnl_pct == pytest.approx(0.0, abs=1e-6)

    def test_pre_tp_pct_zero_falls_back_to_residual_only(self):
        """Defensive: partial_close_pct > 0 but pre_tp_pct missing means
        we don't have enough info to blend honestly.  Fall through to
        residual-only — never fabricate a banked %."""
        sig = _make_signal(entry=30000.0)
        sig.pre_tp_hit = True
        sig.pre_tp_pct = 0.0  # missing telemetry
        sig.partial_close_pct = 0.50
        TradeMonitor._set_realized_pnl(sig, exit_price=sig.entry * 1.01)
        # Pure residual: +1.0% raw on LONG entry to exit_price
        assert sig.pnl_pct == pytest.approx(1.0, abs=1e-6)

    def test_no_partial_at_all_is_unchanged(self):
        """A signal that never hit pre-TP at all (normal SL_HIT path):
        pnl_pct must be the pure entry-to-exit math, unchanged behaviour.
        """
        sig = _make_signal(entry=30000.0, stop_loss=29700.0)  # -1% SL
        # No pre-TP fields set
        TradeMonitor._set_realized_pnl(sig, exit_price=sig.stop_loss)
        # Pure residual: -1.0% on LONG
        assert sig.pnl_pct == pytest.approx(-1.0, abs=1e-6)

    def test_partial_close_pct_capped_at_one(self):
        """If partial_close_pct somehow exceeds 1.0 (e.g., pre-TP 50% +
        TP1 40% compounding to 0.9 via the existing partial logic, then
        a tracking bug pushes it to 1.05), the blend must cap at 100%
        — never allocate > 100% to the partial slice.
        """
        sig = _make_signal(entry=30000.0)
        sig.pre_tp_hit = True
        sig.pre_tp_pct = 0.40
        sig.partial_close_pct = 1.05  # over-cap input
        TradeMonitor._set_realized_pnl(sig, exit_price=sig.entry * 0.99)
        # Capped: 1.0 * 0.40 + 0.0 * residual = +0.40
        assert sig.pnl_pct == pytest.approx(0.40, abs=1e-6)


class TestPreTpReclassifiesBreakevenToProfitLocked:
    """Integration: when the weighted pnl_pct lands above the breakeven
    threshold (|pnl| >= 0.01%), classify_trade_outcome correctly relabels
    the signal from BREAKEVEN_EXIT to PROFIT_LOCKED.  This is the
    classifier path that drives the Lumin Signals tab label visible in
    the owner's 2026-05-17 screenshot."""

    def test_classifier_relabels_be_to_profit_locked_with_partial(self):
        """50% banked at +0.30% → weighted +0.15% → hit_sl=True →
        PROFIT_LOCKED (not BREAKEVEN_EXIT, which would require
        |pnl| < 0.01%).
        """
        from src.performance_metrics import classify_trade_outcome
        sig = _make_signal(entry=30000.0)
        sig.pre_tp_hit = True
        sig.pre_tp_pct = 0.30
        sig.partial_close_pct = 0.50
        TradeMonitor._set_realized_pnl(sig, exit_price=sig.entry)
        outcome = classify_trade_outcome(
            pnl_pct=sig.pnl_pct, hit_tp=0, hit_sl=True,
        )
        assert outcome == "PROFIT_LOCKED"
        assert sig.pnl_pct == pytest.approx(0.15, abs=1e-6)

    def test_classifier_stays_breakeven_when_no_partial(self):
        """No partial fired → pnl_pct = 0.00 → BREAKEVEN_EXIT label is
        correct.  Regression guard: the weighted fix must not change
        the no-partial path."""
        from src.performance_metrics import classify_trade_outcome
        sig = _make_signal(entry=30000.0)
        TradeMonitor._set_realized_pnl(sig, exit_price=sig.entry)
        outcome = classify_trade_outcome(
            pnl_pct=sig.pnl_pct, hit_tp=0, hit_sl=True,
        )
        assert outcome == "BREAKEVEN_EXIT"


# ---------------------------------------------------------------------------
# PR B (2026-05-18) — gate-rejected opens stay retryable
# ---------------------------------------------------------------------------


class TestRejectedOpenRetry:
    """trade_monitor.py:572 fix — _order_placed_ids should only catch
    SUCCESSFUL opens.  When execute_signal returns None (gate rejection:
    qty_zero, notional_floor, risk-gate concurrent-cap), the signal_id
    must NOT be marked as placed so a future tick can retry once the
    rejection cause clears (equity recovered, slot freed).  Owner-
    reported symptom 2026-05-18: ACTIVE signals on the Signals tab
    with no corresponding paper position ever firing.
    """

    def _build_monitor(self, active: Dict[str, Signal]):
        async def mock_send(chat_id, text):
            pass

        data_store = MagicMock()
        data_store.get_candles.side_effect = _make_get_candles_from_active(active)
        data_store.ticks = {}

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: None,
            update_signal=MagicMock(),
        )
        return monitor

    def _active_sig(self) -> Signal:
        return Signal(
            channel="360_SCALP",
            symbol="BTCUSDT",
            direction=Direction.LONG,
            entry=30000.0,
            stop_loss=29850.0,
            tp1=30150.0,
            tp2=30300.0,
            tp3=30450.0,
            confidence=75.0,
            timestamp=utcnow() - timedelta(seconds=300),
            current_price=30000.5,
            status="ACTIVE",
        )

    @pytest.mark.asyncio
    async def test_rejected_open_is_not_marked_placed(self):
        """execute_signal returns None (gate rejection) → signal_id stays
        eligible for future retry; not added to ``_order_placed_ids``."""
        sig = self._active_sig()
        active = {sig.signal_id: sig}
        monitor = self._build_monitor(active)

        om = MagicMock()
        om.is_enabled = True

        async def _reject(_sig):
            return None  # gate rejection

        om.execute_signal.side_effect = _reject
        monitor._order_manager = om

        await monitor._check_all()

        assert sig.signal_id not in monitor._order_placed_ids, (
            "rejected open must NOT be marked as placed — was the "
            "exact bug PR B fixes"
        )
        assert sig.signal_id in monitor._last_open_attempt_at, (
            "attempt timestamp must be recorded for cooldown tracking"
        )
        assert om.execute_signal.call_count == 1

    @pytest.mark.asyncio
    async def test_cooldown_prevents_immediate_retry(self):
        """A second _check_all within the cooldown window does NOT
        re-call execute_signal — otherwise rejected opens would hammer
        the gate chain every 5s monitor tick."""
        sig = self._active_sig()
        active = {sig.signal_id: sig}
        monitor = self._build_monitor(active)

        om = MagicMock()
        om.is_enabled = True

        async def _reject(_sig):
            return None

        om.execute_signal.side_effect = _reject
        monitor._order_manager = om

        await monitor._check_all()
        await monitor._check_all()  # immediate retry — should be skipped

        assert om.execute_signal.call_count == 1, (
            "second call within cooldown must be suppressed"
        )

    @pytest.mark.asyncio
    async def test_successful_open_after_prior_rejection_marks_placed(self):
        """When the rejection cause clears (mocked: second call returns
        a real order_id), the signal_id is finally marked as placed so
        we never re-attempt after success."""
        sig = self._active_sig()
        active = {sig.signal_id: sig}
        monitor = self._build_monitor(active)

        om = MagicMock()
        om.is_enabled = True
        responses = iter([None, "paper-BTCUSDT-open-1"])

        async def _maybe(_sig):
            return next(responses)

        om.execute_signal.side_effect = _maybe
        monitor._order_manager = om

        await monitor._check_all()
        # Bypass cooldown so the second tick can retry.
        monitor._last_open_attempt_at.pop(sig.signal_id, None)
        await monitor._check_all()

        assert sig.signal_id in monitor._order_placed_ids, (
            "successful retry must finally mark the signal as placed"
        )
        assert om.execute_signal.call_count == 2


# ---------------------------------------------------------------------------
# Stale-symbol SL orphan regression (BEATUSDT SHORT -6.52% ACTIVE bug)
#
# When a signal fires on a pair that subsequently falls out of the scan
# universe (e.g. surge-promoted Tier-3 pair), the HistoricalDataStore stops
# receiving 1m candles for that pair.  `_latest_price()` returns None,
# `_process_signal()` returned early — SL never fired, PnL ground without
# bound.  The fix: fall back to the mark-price feed singleton, which covers
# ALL Binance USDT-M futures symbols via !markPrice@arr@1s.
# ---------------------------------------------------------------------------


class TestStaleSymbolMarkPriceFallback:
    """Mark-price feed fallback rescues signals on stale-candle symbols."""

    def _build_monitor_no_candles(
        self,
        active: Dict[str, Signal],
    ):
        """Monitor whose data store has NO candle/tick data for any symbol,
        simulating a pair that fell out of the scan universe after dispatch."""
        removed = []
        sent = []

        async def mock_send(chat_id, text):
            sent.append((chat_id, text))

        data_store = MagicMock()
        data_store.get_candles.return_value = None  # no candle data at all
        data_store.ticks = {}

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.append(sid),
            update_signal=MagicMock(),
            performance_tracker=MagicMock(),
            circuit_breaker=MagicMock(),
        )
        return monitor, removed, sent

    @pytest.mark.asyncio
    async def test_short_sl_fires_via_mark_price_when_candles_stale(self) -> None:
        """BEATUSDT-style: SHORT signal, no 1m candles, mark price above SL.
        SL must fire via the mark-price fallback; signal must NOT stay ACTIVE."""
        sig = _make_signal(
            channel="360_SCALP",
            symbol="BEATUSDT",
            direction=Direction.SHORT,
            entry=0.99540,
            stop_loss=1.0068,   # 1.145% above entry
            tp1=0.98000,
            tp2=0.97000,
            age_seconds=300.0,  # well past any lifespan guard
        )
        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor_no_candles(active)

        # Inject a mock mark-price feed whose get_price returns the live
        # blown-through price (1.0603 — 5.35% above SL).
        mock_feed = MagicMock()
        mock_feed.get_price.return_value = 1.0603

        with patch(
            "src.execution.mark_price_feed.get_instance",
            return_value=mock_feed,
        ):
            await monitor._check_all()

        assert sig.signal_id in removed, (
            "SL must fire when mark price (1.0603) > SHORT SL (1.0068), "
            "even when HistoricalDataStore has no candle data for the symbol"
        )
        assert sig.status == "SL_HIT", f"expected SL_HIT, got {sig.status}"

    @pytest.mark.asyncio
    async def test_long_sl_fires_via_mark_price_when_candles_stale(self) -> None:
        """Symmetrical: LONG signal, no candles, mark price below SL → SL fires."""
        sig = _make_signal(
            channel="360_SCALP",
            symbol="EXAMPLEUSDT",
            direction=Direction.LONG,
            entry=100.0,
            stop_loss=99.0,     # 1% below entry
            tp1=101.5,
            tp2=103.0,
            age_seconds=300.0,
        )
        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor_no_candles(active)

        mock_feed = MagicMock()
        mock_feed.get_price.return_value = 98.5  # well below SL

        with patch(
            "src.execution.mark_price_feed.get_instance",
            return_value=mock_feed,
        ):
            await monitor._check_all()

        assert sig.signal_id in removed, "LONG SL must fire via mark-price fallback"
        assert sig.status == "SL_HIT", f"expected SL_HIT, got {sig.status}"

    @pytest.mark.asyncio
    async def test_no_fire_when_mark_price_feed_unavailable(self) -> None:
        """If the mark-price feed singleton is None (engine not fully booted),
        the monitor must return early rather than crash."""
        sig = _make_signal(
            channel="360_SCALP",
            symbol="BEATUSDT",
            direction=Direction.SHORT,
            entry=0.99540,
            stop_loss=1.0068,
            tp1=0.98000,
            tp2=0.97000,
            age_seconds=300.0,
        )
        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor_no_candles(active)

        with patch(
            "src.execution.mark_price_feed.get_instance",
            return_value=None,
        ):
            await monitor._check_all()  # must not raise

        # Without a fallback price the monitor returns early — signal stays ACTIVE.
        assert sig.signal_id not in removed
        assert sig.status == "ACTIVE"

    @pytest.mark.asyncio
    async def test_mark_price_within_sl_does_not_trigger(self) -> None:
        """Mark-price fallback must NOT fire SL when price is still on-side."""
        sig = _make_signal(
            channel="360_SCALP",
            symbol="BEATUSDT",
            direction=Direction.SHORT,
            entry=0.99540,
            stop_loss=1.0068,
            tp1=0.98000,
            tp2=0.97000,
            age_seconds=300.0,
        )
        active = {sig.signal_id: sig}
        monitor, removed, sent = self._build_monitor_no_candles(active)

        # Price is on-side of the trade (below SL for a SHORT) — no SL.
        mock_feed = MagicMock()
        mock_feed.get_price.return_value = 0.99000

        with patch(
            "src.execution.mark_price_feed.get_instance",
            return_value=mock_feed,
        ):
            await monitor._check_all()

        assert sig.signal_id not in removed
        assert sig.status not in ("SL_HIT",)


# ---------------------------------------------------------------------------
# Fix A (fix/dca-broker-sync) — _post_dca_update gated on broker execution
# ---------------------------------------------------------------------------


class TestDCANotificationGate:
    """_post_dca_update must only fire when the broker actually executed
    Entry 2 (add_dca_entry returns a non-None order ID).  Previously it
    fired unconditionally, sending a Telegram DCA notification even when
    no order was placed on Binance because _open_quantities was empty
    after an engine restart.

    Owner symptom: "DCA in Telegram but not on Binance."
    """

    def _build_monitor(self, active, *, om=None):
        from unittest.mock import AsyncMock

        removed = {}
        sent = {}

        async def mock_send(chat_id, text):
            sent[chat_id] = text

        data_store = MagicMock()
        data_store.get_candles.side_effect = _make_get_candles_from_active(active)
        data_store.ticks = {}

        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=mock_send,
            get_active_signals=lambda: dict(active),
            remove_signal=lambda sid: removed.update({sid: True}),
            update_signal=MagicMock(),
        )
        monitor._post_dca_update = AsyncMock()
        if om is not None:
            monitor._order_manager = om
        return monitor, removed, sent

    def _dca_ready_signal(self) -> Signal:
        """ACTIVE LONG signal with price inside DCA zone (no qty needed)."""
        entry = 30000.0
        sl = 29850.0
        sl_dist = entry - sl  # 150

        sig = Signal(
            channel="360_SCALP",
            symbol="BTCUSDT",
            direction=Direction.LONG,
            entry=entry,
            stop_loss=sl,
            tp1=30150.0,
            tp2=30300.0,
            confidence=80.0,
            timestamp=utcnow() - timedelta(seconds=300),
        )
        sig.tp3 = 30450.0
        sig.status = "ACTIVE"
        sig.entry_2_filled = False
        # Price inside DCA zone: entry - 0.50 × sl_dist = 29925
        sig.current_price = 29925.0
        sig.dca_zone_lower = entry - 0.70 * sl_dist  # 29895
        sig.dca_zone_upper = entry - 0.30 * sl_dist  # 29955
        sig.original_entry = 0.0  # triggers persist in recalculate_after_dca
        return sig

    @pytest.mark.asyncio
    async def test_post_dca_update_suppressed_when_broker_returns_none(self):
        """When add_dca_entry returns None (no tracked qty), _post_dca_update
        must NOT be called — prevents spurious Telegram DCA notification."""
        from unittest.mock import AsyncMock

        sig = self._dca_ready_signal()
        active = {sig.signal_id: sig}

        om = MagicMock()
        om.is_enabled = True
        om.add_dca_entry = AsyncMock(return_value=None)

        monitor, _, _ = self._build_monitor(active, om=om)

        await monitor._check_all()

        monitor._post_dca_update.assert_not_called()

    @pytest.mark.asyncio
    async def test_post_dca_update_fires_when_broker_succeeds(self):
        """When add_dca_entry returns an order ID, _post_dca_update fires."""
        from unittest.mock import AsyncMock

        sig = self._dca_ready_signal()
        active = {sig.signal_id: sig}

        om = MagicMock()
        om.is_enabled = True
        om.add_dca_entry = AsyncMock(return_value="ccxt-dca-99")

        monitor, _, _ = self._build_monitor(active, om=om)

        await monitor._check_all()

        monitor._post_dca_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_dca_update_fires_in_off_mode(self):
        """In off-mode (no order manager), _post_dca_update always fires so
        Telegram-only subscribers receive the DCA notification."""
        sig = self._dca_ready_signal()
        active = {sig.signal_id: sig}

        monitor, _, _ = self._build_monitor(active, om=None)

        await monitor._check_all()

        monitor._post_dca_update.assert_called_once()
