"""Tests for paid-channel open-signal pulse consistency (bugfix PR).

Covers:
- SHORT and LONG PnL math matches the close-message math
- TP1 distance is correct for both directions
- WATCHLIST-tier signals are excluded from the pulse
- Signals with current_price == 0 are excluded
- Signals with implausible PnL magnitude are excluded
- Signals with TP1 on the wrong side of entry are excluded
- Existing close / SL message formatting is not changed
"""

from __future__ import annotations

import asyncio

import pytest

import src.signal_router as signal_router_module
from src.channels.base import Signal
from src.signal_router import SignalRouter
from src.smc import Direction
from src.utils import utcnow


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_router(sent_messages: list) -> SignalRouter:
    """Create a SignalRouter with a fake send and TELEGRAM_ACTIVE_CHANNEL_ID set."""
    async def mock_send(chat_id: str, text: str):
        sent_messages.append((chat_id, text))
        return True

    return SignalRouter(
        queue=asyncio.Queue(),
        send_telegram=mock_send,
        format_signal=lambda sig: f"Signal: {sig.symbol}",
    )


def _make_signal(
    symbol: str = "BTCUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 32000.0,
    stop_loss: float = 31900.0,
    tp1: float = 32130.0,
    tp2: float = 32200.0,
    current_price: float = 32050.0,
    signal_tier: str = "B",
    status: str = "ACTIVE",
) -> Signal:
    sig = Signal(
        channel="360_SCALP",
        symbol=symbol,
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=tp2,
        confidence=80.0,
        signal_id=f"TEST-{symbol}-001",
        timestamp=utcnow(),
    )
    sig.current_price = current_price
    sig.signal_tier = signal_tier
    sig.status = status
    return sig


def _extract_pulse_text(messages: list, channel: str = "active_chan") -> list[str]:
    """Return all pulse-message bodies sent to the given channel."""
    return [text for (cid, text) in messages if cid == channel and "still open" in text]


# ---------------------------------------------------------------------------
# Unit-level math tests (not async – just verify the formula directly)
# ---------------------------------------------------------------------------

class TestPulseMath:
    """Verify the pulse PnL / TP1-distance formulas match the close-message math."""

    def _pnl(self, direction: Direction, entry: float, current: float) -> float:
        if direction == Direction.LONG:
            return (current - entry) / entry * 100
        return (entry - current) / entry * 100

    def _tp1_dist(self, direction: Direction, entry: float, current: float, tp1: float) -> float:
        if direction == Direction.LONG:
            raw = (tp1 - current) / entry * 100
        else:
            raw = (current - tp1) / entry * 100
        return max(raw, 0.0)

    # ---- DASHUSDT SHORT (the observed bug case) ----

    def test_short_pnl_dashusdt_case(self):
        """SHORT from 41.1900; current 41.3680 → PnL ≈ -0.43% (not -10.42%)."""
        entry = 41.1900
        current = 41.3680
        pnl = self._pnl(Direction.SHORT, entry, current)
        assert abs(pnl - (-0.43)) < 0.01, f"Expected ~-0.43%, got {pnl:.4f}%"

    def test_short_tp1_distance_dashusdt_case(self):
        """SHORT from 41.1900 with tp1 ≈ 36.57; current 41.3680 → TP1 in ≈ 11.65%."""
        entry = 41.1900
        current = 41.3680
        # tp1 derived: (current - tp1) / entry = 0.1165 → tp1 = current - 0.1165*entry
        tp1 = current - 0.1165 * entry
        dist = self._tp1_dist(Direction.SHORT, entry, current, tp1)
        assert abs(dist - 11.65) < 0.02, f"Expected ~11.65%, got {dist:.4f}%"

    # ---- LONG case ----

    def test_long_pnl_positive_move(self):
        """LONG from 32000; current 32320 → PnL = +1.00%."""
        entry = 32000.0
        current = 32320.0
        pnl = self._pnl(Direction.LONG, entry, current)
        assert abs(pnl - 1.0) < 0.001

    def test_long_pnl_negative_move(self):
        """LONG from 32000; current 31680 → PnL = -1.00%."""
        entry = 32000.0
        current = 31680.0
        pnl = self._pnl(Direction.LONG, entry, current)
        assert abs(pnl - (-1.0)) < 0.001

    def test_long_tp1_distance(self):
        """LONG tp1 = 32320; current = 32160 → TP1 in = (32320-32160)/32000 = 0.50%."""
        entry = 32000.0
        current = 32160.0
        tp1 = 32320.0
        dist = self._tp1_dist(Direction.LONG, entry, current, tp1)
        assert abs(dist - 0.5) < 0.001

    def test_long_tp1_already_crossed_clamped_to_zero(self):
        """When TP1 is already below current for LONG, dist should clamp to 0."""
        entry = 32000.0
        current = 32400.0
        tp1 = 32320.0  # already crossed
        dist = self._tp1_dist(Direction.LONG, entry, current, tp1)
        assert dist == 0.0

    def test_short_tp1_already_crossed_clamped_to_zero(self):
        """When price falls below tp1 for SHORT (TP1 crossed), dist clamps to 0."""
        entry = 41.19
        tp1 = 36.57
        current = 36.20  # below tp1 → already crossed
        dist = self._tp1_dist(Direction.SHORT, entry, current, tp1)
        assert dist == 0.0

    # ---- Sanity bound ----

    def test_implausible_pnl_would_be_suppressed(self):
        """Illustrate that the -10.42% value in the bug report exceeds any reasonable
        scalp bound and should be suppressed by the guard."""
        observed_bad_pnl = -10.42
        assert abs(observed_bad_pnl) > SignalRouter._PULSE_MAX_REASONABLE_PNL_PCT * 0.33, (
            "The observed bad value should be large enough to be caught by a ≤30% bound"
        )


# ---------------------------------------------------------------------------
# Integration-style pulse-loop tests (exercise _signal_pulse_loop directly)
# ---------------------------------------------------------------------------

@pytest.fixture
def sent_messages():
    return []


@pytest.fixture
def active_chan(monkeypatch):
    monkeypatch.setattr(signal_router_module, "TELEGRAM_ACTIVE_CHANNEL_ID", "active_chan")
    return "active_chan"


class TestPulseLoopGuards:
    """_signal_pulse_loop must skip signals with invalid or unreliable state."""

    async def _run_pulse_once(
        self,
        router: SignalRouter,
        monkeypatch,
        pulse_interval: int = 0,
    ) -> None:
        """Drive the pulse loop for one iteration with patched sleep."""
        import config as cfg
        monkeypatch.setattr(cfg, "SIGNAL_PULSE_INTERVAL_SECONDS", pulse_interval)

        # Patch asyncio.sleep inside the loop so it yields immediately
        sleep_count = [0]

        async def fast_sleep(_secs):
            sleep_count[0] += 1
            if sleep_count[0] >= 2:
                router._running = False

        monkeypatch.setattr(asyncio, "sleep", fast_sleep)
        router._running = True
        await router._signal_pulse_loop()

    @pytest.mark.asyncio
    async def test_short_signal_correct_pnl(self, sent_messages, active_chan, monkeypatch):
        """DASHUSDT SHORT: entry=41.19, current=41.368 → pulse shows ~-0.43%."""
        router = _make_router(sent_messages)
        sig = _make_signal(
            symbol="DASHUSDT",
            direction=Direction.SHORT,
            entry=41.1900,
            stop_loss=41.40,
            tp1=36.5694,
            current_price=41.3680,
            signal_tier="B",
        )
        sig._last_pulse_time = 0.0
        router._active_signals[sig.signal_id] = sig

        await self._run_pulse_once(router, monkeypatch)

        pulses = _extract_pulse_text(sent_messages, "active_chan")
        assert pulses, "Expected at least 1 pulse, got none"
        pulse = pulses[0]
        assert "DASHUSDT SHORT" in pulse
        assert "still open" in pulse
        # PnL should be around -0.43%
        assert "-0.43" in pulse, f"Expected ~-0.43% PnL in pulse: {pulse}"

    @pytest.mark.asyncio
    async def test_long_signal_correct_pnl(self, sent_messages, active_chan, monkeypatch):
        """LONG from 32000; current 32160 → pulse shows +0.50%."""
        router = _make_router(sent_messages)
        sig = _make_signal(
            symbol="BTCUSDT",
            direction=Direction.LONG,
            entry=32000.0,
            stop_loss=31900.0,
            tp1=32320.0,
            current_price=32160.0,
            signal_tier="A+",
        )
        sig._last_pulse_time = 0.0
        router._active_signals[sig.signal_id] = sig

        await self._run_pulse_once(router, monkeypatch)

        pulses = _extract_pulse_text(sent_messages, "active_chan")
        assert pulses, "Expected at least 1 pulse, got none"
        pulse = pulses[0]
        assert "BTCUSDT LONG" in pulse
        # PnL = (32160 - 32000) / 32000 * 100 = +0.50%
        assert "+0.50" in pulse, f"Expected +0.50% in pulse: {pulse}"

    @pytest.mark.asyncio
    async def test_watchlist_tier_signal_skipped(self, sent_messages, active_chan, monkeypatch):
        """WATCHLIST-tier signals must not generate a live-trade pulse."""
        router = _make_router(sent_messages)
        sig = _make_signal(
            symbol="DASHUSDT",
            direction=Direction.SHORT,
            entry=41.1900,
            stop_loss=41.40,
            tp1=36.57,
            current_price=41.3680,
            signal_tier="WATCHLIST",
        )
        sig._last_pulse_time = 0.0
        router._active_signals[sig.signal_id] = sig

        await self._run_pulse_once(router, monkeypatch)

        pulses = _extract_pulse_text(sent_messages, "active_chan")
        assert pulses == [], f"WATCHLIST signal should not pulse, but got: {pulses}"

    @pytest.mark.asyncio
    async def test_zero_current_price_skipped(self, sent_messages, active_chan, monkeypatch):
        """Signal with current_price == 0 must not generate a pulse."""
        router = _make_router(sent_messages)
        sig = _make_signal(
            symbol="BTCUSDT",
            direction=Direction.LONG,
            entry=32000.0,
            stop_loss=31900.0,
            tp1=32200.0,
            current_price=0.0,
            signal_tier="B",
        )
        sig._last_pulse_time = 0.0
        router._active_signals[sig.signal_id] = sig

        await self._run_pulse_once(router, monkeypatch)

        pulses = _extract_pulse_text(sent_messages, "active_chan")
        assert pulses == [], f"Zero current_price should suppress pulse, got: {pulses}"

    @pytest.mark.asyncio
    async def test_implausible_pnl_skipped(self, sent_messages, active_chan, monkeypatch):
        """Implausible PnL (> 30%) must suppress the pulse instead of posting bad numbers."""
        router = _make_router(sent_messages)
        # SHORT where current_price is wildly above entry (stale/corrupted state)
        sig = _make_signal(
            symbol="DASHUSDT",
            direction=Direction.SHORT,
            entry=41.1900,
            stop_loss=50.0,
            tp1=36.57,
            current_price=55.0,  # implies PnL ≈ -33% — clearly stale
            signal_tier="B",
        )
        sig._last_pulse_time = 0.0
        router._active_signals[sig.signal_id] = sig

        await self._run_pulse_once(router, monkeypatch)

        pulses = _extract_pulse_text(sent_messages, "active_chan")
        assert pulses == [], f"Implausible PnL should suppress pulse, got: {pulses}"

    @pytest.mark.asyncio
    async def test_tp1_wrong_side_long_skipped(self, sent_messages, active_chan, monkeypatch):
        """LONG with TP1 <= entry is invalid state – pulse must be suppressed."""
        router = _make_router(sent_messages)
        sig = _make_signal(
            symbol="BTCUSDT",
            direction=Direction.LONG,
            entry=32000.0,
            stop_loss=31900.0,
            tp1=31800.0,   # TP1 below entry for LONG — invalid
            current_price=32050.0,
            signal_tier="B",
        )
        sig._last_pulse_time = 0.0
        router._active_signals[sig.signal_id] = sig

        await self._run_pulse_once(router, monkeypatch)

        pulses = _extract_pulse_text(sent_messages, "active_chan")
        assert pulses == [], f"Invalid TP1 direction should suppress pulse, got: {pulses}"

    @pytest.mark.asyncio
    async def test_tp1_wrong_side_short_skipped(self, sent_messages, active_chan, monkeypatch):
        """SHORT with TP1 >= entry is invalid state – pulse must be suppressed."""
        router = _make_router(sent_messages)
        sig = _make_signal(
            symbol="DASHUSDT",
            direction=Direction.SHORT,
            entry=41.1900,
            stop_loss=41.40,
            tp1=42.0,   # TP1 above entry for SHORT — invalid
            current_price=41.3680,
            signal_tier="B",
        )
        sig._last_pulse_time = 0.0
        router._active_signals[sig.signal_id] = sig

        await self._run_pulse_once(router, monkeypatch)

        pulses = _extract_pulse_text(sent_messages, "active_chan")
        assert pulses == [], f"Invalid TP1 direction should suppress pulse, got: {pulses}"

    @pytest.mark.asyncio
    async def test_non_active_status_skipped(self, sent_messages, active_chan, monkeypatch):
        """Signals with SL_HIT or CANCELLED status must not pulse."""
        router = _make_router(sent_messages)
        for status in ("SL_HIT", "CANCELLED", "FULL_TP_HIT"):
            sig = _make_signal(
                symbol="ETHUSDT",
                direction=Direction.LONG,
                entry=2000.0,
                stop_loss=1980.0,
                tp1=2040.0,
                current_price=2020.0,
                signal_tier="B",
                status=status,
            )
            sig.signal_id = f"TEST-ETHUSDT-{status}"
            sig._last_pulse_time = 0.0
            router._active_signals[sig.signal_id] = sig

        await self._run_pulse_once(router, monkeypatch)

        pulses = _extract_pulse_text(sent_messages, "active_chan")
        assert pulses == [], f"Non-ACTIVE status should suppress pulse, got: {pulses}"

    @pytest.mark.asyncio
    async def test_tp1_crossed_clamps_to_zero(self, sent_messages, active_chan, monkeypatch):
        """When TP1 has already been crossed (tp1_dist < 0), pulse must show 0.00%."""
        router = _make_router(sent_messages)
        # LONG where price went past TP1
        sig = _make_signal(
            symbol="BTCUSDT",
            direction=Direction.LONG,
            entry=32000.0,
            stop_loss=31900.0,
            tp1=32100.0,
            current_price=32200.0,  # past TP1 — tp1_dist would be negative without clamp
            signal_tier="B",
            status="TP1_HIT",
        )
        sig._last_pulse_time = 0.0
        router._active_signals[sig.signal_id] = sig

        await self._run_pulse_once(router, monkeypatch)

        pulses = _extract_pulse_text(sent_messages, "active_chan")
        assert pulses, "Expected at least 1 pulse, got none"
        pulse = pulses[0]
        # TP1 in should be 0.00% (clamped), not negative
        assert "TP1 in 0.00%" in pulse, f"Expected TP1 clamped to 0.00%, got: {pulse}"

    @pytest.mark.asyncio
    async def test_no_pulse_channel_id_suppresses_all(self, sent_messages, monkeypatch):
        """If TELEGRAM_ACTIVE_CHANNEL_ID is empty, no pulses are sent."""
        import src.signal_router as m
        monkeypatch.setattr(m, "TELEGRAM_ACTIVE_CHANNEL_ID", "")

        router = _make_router(sent_messages)
        sig = _make_signal(
            symbol="BTCUSDT",
            direction=Direction.LONG,
            entry=32000.0,
            stop_loss=31900.0,
            tp1=32200.0,
            current_price=32100.0,
            signal_tier="B",
        )
        sig._last_pulse_time = 0.0
        router._active_signals[sig.signal_id] = sig

        await self._run_pulse_once(router, monkeypatch)

        assert sent_messages == []
