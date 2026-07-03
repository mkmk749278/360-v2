"""No-fill expiry accounting — never fabricate a trade that never filled.

2026-07-03 monitor-logs sweep: 36 of the last 100 perf records were EXPIRED
signals whose limit entry zone was never visited (hold=0s, MFE=MAE=0) yet
carried nonzero mark-vs-entry P&L — phantom trades polluting win rates, the
scorer band tables, the ops Profit page, and the invalidation audit's
PREMATURE counts.  These tests pin the honest behaviour on both expiry
paths (trade_monitor max-hold + router cleanup_expired → engine handler):

* no-fill  → outcome_label="EXPIRED_NO_FILL", pnl_pct=0.0, no audit record
* filled   → unchanged EXPIRED behaviour (mark-vs-entry P&L, audited)
* market-order signals (no entry zone) are never treated as no-fill
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.channels.base import Signal
from src.smc import Direction
from src.trade_monitor import TradeMonitor


# ---------------------------------------------------------------------------
# Signal.entry_never_filled property semantics
# ---------------------------------------------------------------------------


def _make_signal(
    *,
    entry: float = 100.0,
    zone: bool = True,
    filled: bool = False,
    age_seconds: float = 4000.0,
    direction: Direction = Direction.LONG,
) -> Signal:
    sig = Signal(
        channel="360_SCALP",
        symbol="SOLUSDT",
        direction=direction,
        entry=entry,
        stop_loss=entry * 0.98,
        tp1=entry * 1.02,
        tp2=entry * 1.04,
        confidence=75.0,
        signal_id="NOFILL-1",
    )
    sig.timestamp = datetime.now(timezone.utc) - timedelta(seconds=age_seconds)
    sig.setup_class = "MOVER_TREND_PULLBACK"
    sig.status = "ACTIVE"
    sig.current_price = entry * 1.01
    if zone:
        sig.entry_zone_low = entry * 0.999
        sig.entry_zone_high = entry * 1.001
    sig.entry_zone_filled = filled
    return sig


class TestEntryNeverFilledProperty:
    def test_zone_unvisited_is_never_filled(self):
        assert _make_signal(zone=True, filled=False).entry_never_filled is True

    def test_zone_visited_is_filled(self):
        assert _make_signal(zone=True, filled=True).entry_never_filled is False

    def test_market_order_signal_is_never_no_fill(self):
        # No zone populated → market-order semantics → not a no-fill even
        # though the entry_zone_filled default is False.
        assert _make_signal(zone=False, filled=False).entry_never_filled is False


# ---------------------------------------------------------------------------
# trade_monitor max-hold expiry path
# ---------------------------------------------------------------------------


def _build_monitor(active, tracker=None):
    removed = []
    sent = []

    async def mock_send(chat_id, text):
        sent.append((chat_id, text))

    data_store = MagicMock()
    data_store.get_candles.return_value = {}
    data_store.ticks = {}
    monitor = TradeMonitor(
        data_store=data_store,
        send_telegram=mock_send,
        get_active_signals=lambda: dict(active),
        remove_signal=lambda sid: removed.append(sid),
        update_signal=MagicMock(),
        performance_tracker=tracker,
    )
    monitor._broker_close_full = AsyncMock()
    return monitor, removed, sent


class TestMonitorExpiryNoFill:
    @pytest.fixture(autouse=True)
    def _enable_signal_expiry(self, monkeypatch):
        monkeypatch.setattr("src.trade_monitor.SIGNAL_EXPIRY_ENABLED", True)

    async def test_no_fill_expiry_records_zero_pnl_and_no_fill_label(self):
        tracker = MagicMock()
        sig = _make_signal(zone=True, filled=False)
        monitor, removed, _ = _build_monitor({sig.signal_id: sig}, tracker)

        await monitor._evaluate_signal(sig)

        assert sig.signal_id in removed
        assert sig.status == "EXPIRED"
        assert sig.pnl_pct == 0.0
        kwargs = tracker.record_outcome.call_args.kwargs
        assert kwargs["outcome_label"] == "EXPIRED_NO_FILL"
        assert kwargs["pnl_pct"] == 0.0
        # Defensive close still runs — books written before the
        # entry-fill open gate may hold a dispatch-time position for
        # this never-filled signal (no-op when nothing is open).
        monitor._broker_close_full.assert_awaited_once()

    async def test_no_fill_expiry_message_says_never_filled(self, monkeypatch):
        monkeypatch.setitem(
            __import__("src.trade_monitor", fromlist=["CHANNEL_TELEGRAM_MAP"]).CHANNEL_TELEGRAM_MAP,
            "360_SCALP",
            "test-channel",
        )
        sig = _make_signal(zone=True, filled=False)
        monitor, _, sent = _build_monitor({sig.signal_id: sig})

        await monitor._evaluate_signal(sig)

        assert any("entry never filled" in text for _, text in sent)

    async def test_filled_signal_expiry_unchanged(self):
        tracker = MagicMock()
        sig = _make_signal(zone=True, filled=True, entry=100.0)
        sig.current_price = 102.0
        monitor, removed, _ = _build_monitor({sig.signal_id: sig}, tracker)

        await monitor._evaluate_signal(sig)

        assert sig.signal_id in removed
        assert sig.status == "EXPIRED"
        kwargs = tracker.record_outcome.call_args.kwargs
        assert kwargs["outcome_label"] == "EXPIRED"
        assert kwargs["pnl_pct"] == pytest.approx(2.0)
        monitor._broker_close_full.assert_awaited_once()


# ---------------------------------------------------------------------------
# Router cleanup_expired → CryptoSignalEngine._handle_signal_expiry
# ---------------------------------------------------------------------------


def _make_engine_with_mocks():
    with patch("src.main.TelegramBot"), \
         patch("src.main.TelemetryCollector"), \
         patch("src.main.RedisClient"), \
         patch("src.main.SignalQueue"), \
         patch("src.main.StateCache"), \
         patch("src.main.SignalRouter"), \
         patch("src.main.TradeMonitor"), \
         patch("src.main.PairManager"), \
         patch("src.main.HistoricalDataStore"), \
         patch("src.main.PredictiveEngine"), \
         patch("src.main.ExchangeManager"), \
         patch("src.main.SMCDetector"), \
         patch("src.main.RegimeService"), \
         patch("src.main.load_history", return_value=[]), \
         patch("src.main.backfill_from_legacy_sources", return_value=[]), \
         patch("src.main.save_history"):
        from src.main import CryptoSignalEngine
        engine = CryptoSignalEngine()
    engine._performance_tracker = MagicMock()
    engine._order_manager = MagicMock()
    engine._order_manager.is_enabled = False
    return engine


class TestEngineExpiryHandlerNoFill:
    def test_no_fill_records_no_fill_label_with_zero_pnl(self):
        engine = _make_engine_with_mocks()
        sig = _make_signal(zone=True, filled=False, entry=100.0)
        sig.current_price = 98.0  # 2% adverse — must NOT be booked as a loss

        with patch("src.invalidation_audit.record_invalidation") as audit:
            engine._handle_signal_expiry(sig, datetime.now(timezone.utc))

        assert sig.status == "EXPIRED"
        assert sig.pnl_pct == 0.0
        kwargs = engine._performance_tracker.record_outcome.call_args.kwargs
        assert kwargs["outcome_label"] == "EXPIRED_NO_FILL"
        assert kwargs["pnl_pct"] == 0.0
        # A never-filled signal is not a kill — PROTECTIVE/PREMATURE
        # classification assumes a position was open.
        audit.assert_not_called()

    def test_filled_signal_still_audited_and_marked(self):
        engine = _make_engine_with_mocks()
        sig = _make_signal(zone=True, filled=True, entry=100.0)
        sig.current_price = 102.0

        with patch("src.invalidation_audit.record_invalidation") as audit:
            engine._handle_signal_expiry(sig, datetime.now(timezone.utc))

        assert sig.status == "EXPIRED"
        assert sig.pnl_pct == pytest.approx(2.0)
        kwargs = engine._performance_tracker.record_outcome.call_args.kwargs
        assert kwargs["outcome_label"] == "EXPIRED"
        assert kwargs["pnl_pct"] == pytest.approx(2.0)
        audit.assert_called_once()

    def test_market_order_signal_keeps_legacy_expired_path(self):
        # Zones unpopulated (market-order semantics) — must not be
        # classified as no-fill even though entry_zone_filled is False.
        engine = _make_engine_with_mocks()
        sig = _make_signal(zone=False, filled=False, entry=100.0)
        sig.current_price = 101.0

        engine._handle_signal_expiry(sig, datetime.now(timezone.utc))

        kwargs = engine._performance_tracker.record_outcome.call_args.kwargs
        assert kwargs["outcome_label"] == "EXPIRED"
        assert kwargs["pnl_pct"] == pytest.approx(1.0)

    def test_record_carries_lifecycle_timestamps(self):
        # The 2026-07-03 phantom records had no create/dispatch/terminal
        # timestamps, which is what made them so hard to attribute.
        engine = _make_engine_with_mocks()
        sig = _make_signal(zone=True, filled=False)
        sig.dispatch_timestamp = datetime.now(timezone.utc) - timedelta(seconds=3900)
        now = datetime.now(timezone.utc)

        engine._handle_signal_expiry(sig, now)

        kwargs = engine._performance_tracker.record_outcome.call_args.kwargs
        assert kwargs["create_timestamp"] == pytest.approx(sig.timestamp.timestamp())
        assert kwargs["dispatch_timestamp"] == pytest.approx(
            sig.dispatch_timestamp.timestamp()
        )
        assert kwargs["terminal_outcome_timestamp"] == pytest.approx(now.timestamp())
        assert kwargs["create_to_terminal_sec"] == pytest.approx(
            now.timestamp() - sig.timestamp.timestamp()
        )

    def test_restart_restored_iso_string_dispatch_timestamp_tolerated(self):
        # A restart-restored Signal carries dispatch_timestamp as the ISO
        # string _signal_to_dict wrote (only timestamp/last_lifecycle_check/
        # dca_timestamp are converted back on restore).
        engine = _make_engine_with_mocks()
        sig = _make_signal(zone=True, filled=False)
        dispatched = datetime.now(timezone.utc) - timedelta(seconds=3900)
        sig.dispatch_timestamp = dispatched.isoformat()

        engine._handle_signal_expiry(sig, datetime.now(timezone.utc))

        kwargs = engine._performance_tracker.record_outcome.call_args.kwargs
        assert kwargs["dispatch_timestamp"] == pytest.approx(dispatched.timestamp())


# ---------------------------------------------------------------------------
# Entry-fill gate on engine-book auto-execution (paper skip fix, 2026-07-03)
# ---------------------------------------------------------------------------


class TestAutoExecutionEntryFillGate:
    """The engine-book order (paper on the VPS) must not open until the
    entry zone has actually been visited.  Opening at dispatch created
    positions nobody could have filled; with SL/TP checks fill-gated they
    could never close, eating max_concurrent slots and starving later
    signals — the owner-reported "paper skips trades" symptom."""

    def _build(self, sig, order_manager):
        data_store = MagicMock()
        data_store.get_candles.return_value = {}
        data_store.ticks = {}
        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=AsyncMock(),
            get_active_signals=lambda: {sig.signal_id: sig},
            remove_signal=MagicMock(),
            update_signal=MagicMock(),
            order_manager=order_manager,
        )
        monitor._latest_price = MagicMock(return_value=sig.entry)
        monitor._evaluate_signal = AsyncMock()
        monitor._check_per_user_invalidation = AsyncMock()
        return monitor

    async def test_unfilled_zone_signal_does_not_open_position(self):
        om = MagicMock()
        om.is_enabled = True
        om.execute_signal = AsyncMock(return_value="oid-1")
        sig = _make_signal(zone=True, filled=False, age_seconds=30.0)
        monitor = self._build(sig, om)

        await monitor._check_all()

        om.execute_signal.assert_not_awaited()

    async def test_filled_zone_signal_opens_position(self):
        om = MagicMock()
        om.is_enabled = True
        om.execute_signal = AsyncMock(return_value="oid-1")
        sig = _make_signal(zone=True, filled=True, age_seconds=30.0)
        monitor = self._build(sig, om)

        await monitor._check_all()

        om.execute_signal.assert_awaited_once()

    async def test_market_order_signal_opens_immediately(self):
        om = MagicMock()
        om.is_enabled = True
        om.execute_signal = AsyncMock(return_value="oid-1")
        sig = _make_signal(zone=False, filled=False, age_seconds=30.0)
        monitor = self._build(sig, om)

        await monitor._check_all()

        om.execute_signal.assert_awaited_once()


class TestStatFilterExclusion:
    async def test_no_fill_expiry_not_recorded_as_stat_outcome(self, monkeypatch):
        # A non-trade must not enter the rolling win-rate store as a loss —
        # it would drag cohort win rates down and trigger unearned
        # stat-filter suppression of the cohort.
        monkeypatch.setattr("src.trade_monitor.SIGNAL_EXPIRY_ENABLED", True)
        stat = MagicMock()
        sig = _make_signal(zone=True, filled=False)
        data_store = MagicMock()
        data_store.get_candles.return_value = {}
        data_store.ticks = {}
        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=AsyncMock(),
            get_active_signals=lambda: {sig.signal_id: sig},
            remove_signal=MagicMock(),
            update_signal=MagicMock(),
            stat_filter=stat,
        )
        monitor._broker_close_full = AsyncMock()

        await monitor._evaluate_signal(sig)

        stat.record.assert_not_called()

    async def test_filled_expiry_still_recorded(self, monkeypatch):
        monkeypatch.setattr("src.trade_monitor.SIGNAL_EXPIRY_ENABLED", True)
        stat = MagicMock()
        sig = _make_signal(zone=True, filled=True)
        data_store = MagicMock()
        data_store.get_candles.return_value = {}
        data_store.ticks = {}
        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=AsyncMock(),
            get_active_signals=lambda: {sig.signal_id: sig},
            remove_signal=MagicMock(),
            update_signal=MagicMock(),
            stat_filter=stat,
        )
        monitor._broker_close_full = AsyncMock()

        await monitor._evaluate_signal(sig)

        stat.record.assert_called_once()


class TestFillWindowEnforcement:
    """S41: the advertised validity window is now the fill window — the book
    must not accept a limit fill subscribers were told to abandon."""

    def _monitor(self, sig, tracker=None):
        data_store = MagicMock()
        # Candle that does NOT overlap the entry zone (price far above).
        data_store.get_candles.return_value = {
            "close": [sig.entry * 1.05], "high": [sig.entry * 1.06],
            "low": [sig.entry * 1.04], "open": [sig.entry * 1.05],
        }
        data_store.ticks = {}
        monitor = TradeMonitor(
            data_store=data_store,
            send_telegram=AsyncMock(),
            get_active_signals=lambda: {sig.signal_id: sig},
            remove_signal=MagicMock(),
            update_signal=MagicMock(),
            performance_tracker=tracker,
        )
        monitor._broker_close_full = AsyncMock()
        monitor._remove = MagicMock()
        return monitor

    async def test_unfilled_past_validity_finalises_no_fill(self, monkeypatch):
        monkeypatch.setattr("src.trade_monitor.ENTRY_FILL_WINDOW_ENFORCED", True)
        monkeypatch.setattr("src.trade_monitor.SIGNAL_EXPIRY_ENABLED", False)
        tracker = MagicMock()
        sig = _make_signal(zone=True, filled=False, age_seconds=16 * 60)
        sig.valid_for_minutes = 15
        monitor = self._monitor(sig, tracker)

        await monitor._evaluate_signal(sig)

        monitor._remove.assert_called_once_with(sig.signal_id)
        kwargs = tracker.record_outcome.call_args.kwargs
        assert kwargs["outcome_label"] == "EXPIRED_NO_FILL"
        assert kwargs["pnl_pct"] == 0.0

    async def test_unfilled_within_validity_keeps_waiting(self, monkeypatch):
        monkeypatch.setattr("src.trade_monitor.ENTRY_FILL_WINDOW_ENFORCED", True)
        monkeypatch.setattr("src.trade_monitor.SIGNAL_EXPIRY_ENABLED", False)
        tracker = MagicMock()
        sig = _make_signal(zone=True, filled=False, age_seconds=10 * 60)
        sig.valid_for_minutes = 15
        monitor = self._monitor(sig, tracker)

        await monitor._evaluate_signal(sig)

        monitor._remove.assert_not_called()
        tracker.record_outcome.assert_not_called()

    async def test_flag_off_preserves_old_wait_behaviour(self, monkeypatch):
        monkeypatch.setattr("src.trade_monitor.ENTRY_FILL_WINDOW_ENFORCED", False)
        monkeypatch.setattr("src.trade_monitor.SIGNAL_EXPIRY_ENABLED", False)
        tracker = MagicMock()
        sig = _make_signal(zone=True, filled=False, age_seconds=30 * 60)
        sig.valid_for_minutes = 15
        monitor = self._monitor(sig, tracker)

        await monitor._evaluate_signal(sig)

        monitor._remove.assert_not_called()
        tracker.record_outcome.assert_not_called()

    async def test_zero_validity_never_enforced(self, monkeypatch):
        # valid_for_minutes == 0 means "not set by an evaluator" — the window
        # must not fire on it (fail-open).
        monkeypatch.setattr("src.trade_monitor.ENTRY_FILL_WINDOW_ENFORCED", True)
        monkeypatch.setattr("src.trade_monitor.SIGNAL_EXPIRY_ENABLED", False)
        tracker = MagicMock()
        sig = _make_signal(zone=True, filled=False, age_seconds=30 * 60)
        sig.valid_for_minutes = 0
        monitor = self._monitor(sig, tracker)

        await monitor._evaluate_signal(sig)

        monitor._remove.assert_not_called()
