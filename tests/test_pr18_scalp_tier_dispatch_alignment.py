"""PR-18 tests: 360_SCALP tier dispatch alignment (A+ / B / FILTERED).

WATCHLIST tier was removed in the app-era doctrine reset.  Sub-65 signals
drop cleanly at the scanner gate; the free Telegram channel keeps macro /
regime-shift / signal-close storytelling but no preview signals.  Tests
below assert sub-65 drop, not WATCHLIST routing.

Original docstring (kept for context):

Verifies the governance correction that aligns 360_SCALP dispatch behavior
with the declared tier policy:
  A+  = 80-100  → dispatched to paid channel (unchanged)
  B   = 65-79   → dispatched to paid channel
  WATCHLIST = 50-64 → routed to FREE CHANNEL ONLY as a zone-alert preview;
                       never registered in _active_signals, never managed by
                       TradeMonitor (doctrine: "Post to free channel only")

Covered invariants
──────────────────
1. B-tier (65-79) candidate is NOT blocked by a legacy floor in scanner config.
2. WATCHLIST signal is NOT registered in _active_signals (not a paid active trade).
3. WATCHLIST signal is posted to the free channel as a zone-alert preview.
4. A+ behavior is unchanged.
5. Non-360_SCALP channels' min-confidence behavior is unchanged.
6. Non-WATCHLIST signals below chan floor are still rejected by the router.
7. WATCHLIST on a non-360_SCALP channel is not posted to any channel.
"""

from __future__ import annotations

import asyncio

import pytest

import src.signal_router as signal_router_module
from src.channels.base import Signal
from src.scanner import classify_signal_tier
from src.signal_router import SignalRouter
from src.smc import Direction
from src.utils import utcnow

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _make_signal(
    *,
    channel: str = "360_SCALP",
    confidence: float = 85.0,
    signal_tier: str = "A+",
    direction: Direction = Direction.LONG,
) -> Signal:
    sig = Signal(
        channel=channel,
        symbol="BTCUSDT",
        direction=direction,
        entry=32_000.0,
        stop_loss=31_900.0,
        tp1=32_200.0,
        tp2=32_400.0,
        confidence=confidence,
        signal_id=f"TEST-{channel}-{confidence}",
        timestamp=utcnow(),
    )
    sig.signal_tier = signal_tier
    return sig


@pytest.fixture
def sent_messages() -> list:
    return []


@pytest.fixture
def queue() -> asyncio.Queue:
    return asyncio.Queue()


@pytest.fixture
def router(queue, sent_messages, monkeypatch):
    for channel in (
        "360_SCALP", "360_SCALP_FVG", "360_SCALP_CVD", "360_SCALP_VWAP",
        "360_SCALP_DIVERGENCE", "360_SCALP_SUPERTREND",
        "360_SCALP_ICHIMOKU", "360_SCALP_ORDERBLOCK",
    ):
        monkeypatch.setitem(signal_router_module.CHANNEL_TELEGRAM_MAP, channel, "premium")
    monkeypatch.setitem(signal_router_module.CHANNEL_TELEGRAM_MAP, "360_SWING", "premium")

    # Set up a free channel ID so WATCHLIST posts can be captured.
    monkeypatch.setattr(signal_router_module, "TELEGRAM_FREE_CHANNEL_ID", "free_channel")

    async def mock_send(chat_id: str, text: str) -> bool:
        sent_messages.append((chat_id, text))
        return True

    def mock_format(sig: Signal) -> str:
        return f"Signal: {sig.channel} {sig.symbol} {sig.direction.value}"

    return SignalRouter(queue=queue, send_telegram=mock_send, format_signal=mock_format)


# ---------------------------------------------------------------------------
# Helper: run router for a single signal and return whether the signal
# entered _active_signals (i.e. was registered in the paid active lifecycle).
# ---------------------------------------------------------------------------

async def _is_in_active_signals(router: SignalRouter, queue: asyncio.Queue, sig: Signal) -> bool:
    """Enqueue *sig*, run the router briefly, return True if signal_id is in active_signals.

    Returns True when the signal was registered in ``router.active_signals``,
    which happens only for signals that completed the paid dispatch path.
    WATCHLIST signals that are routed to the free channel will return False.
    """
    await queue.put(sig)
    task = asyncio.create_task(router.start())
    await asyncio.sleep(0.2)
    await router.stop()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    return sig.signal_id in router.active_signals

# Backward-compatible alias used by tests that pre-date the rename.
_route_signal = _is_in_active_signals


# ---------------------------------------------------------------------------
# Invariant 1: classify_signal_tier agrees with intended mapping
# ---------------------------------------------------------------------------

class TestClassifySignalTier:
    """Tier boundaries are declared explicitly and match doctrine."""

    def test_a_plus_boundary(self):
        assert classify_signal_tier(80.0) == "A+"
        assert classify_signal_tier(100.0) == "A+"
        assert classify_signal_tier(95.5) == "A+"

    def test_b_tier_boundary(self):
        assert classify_signal_tier(65.0) == "B"
        assert classify_signal_tier(79.9) == "B"
        assert classify_signal_tier(72.0) == "B"

    def test_sub_paid_threshold_filtered(self):
        """WATCHLIST tier removed in app-era reset; sub-65 → FILTERED (drop)."""
        assert classify_signal_tier(64.9) == "FILTERED"
        assert classify_signal_tier(55.0) == "FILTERED"
        assert classify_signal_tier(50.0) == "FILTERED"
        assert classify_signal_tier(49.9) == "FILTERED"
        assert classify_signal_tier(0.0) == "FILTERED"


# ---------------------------------------------------------------------------
# Invariant 2: CHANNEL_SCALP.min_confidence is aligned with B-tier (65)
# ---------------------------------------------------------------------------

class TestScalpMinConfidenceConfig:
    """360_SCALP.min_confidence must be 65, matching B-tier threshold."""

    def test_min_confidence_equals_65(self):
        from config import CHANNEL_SCALP
        assert CHANNEL_SCALP.min_confidence == 65, (
            f"360_SCALP.min_confidence is {CHANNEL_SCALP.min_confidence}; "
            "expected 65 (B-tier threshold). "
            "B-tier signals (65-79) must not be structurally blocked by a legacy floor of 80."
        )

    def test_b_tier_confidence_not_below_scalp_floor(self):
        """Any B-tier confidence (65-79) must pass the scanner's min_confidence check."""
        from config import CHANNEL_SCALP
        for conf in (65.0, 70.0, 72.5, 79.9):
            assert conf >= CHANNEL_SCALP.min_confidence, (
                f"B-tier confidence {conf} is below CHANNEL_SCALP.min_confidence "
                f"({CHANNEL_SCALP.min_confidence}). B-tier signals would be dead-zoned."
            )

    def test_other_scalp_channels_unchanged(self):
        """Other scalp sub-channels retain their existing min_confidence values."""
        from config import (
            CHANNEL_SCALP_FVG,
            CHANNEL_SCALP_CVD,
            CHANNEL_SCALP_VWAP,
            CHANNEL_SCALP_DIVERGENCE,
            CHANNEL_SCALP_SUPERTREND,
            CHANNEL_SCALP_ICHIMOKU,
            CHANNEL_SCALP_ORDERBLOCK,
        )
        # All other channels must remain above 65 (their own existing floors)
        for chan in (
            CHANNEL_SCALP_FVG,
            CHANNEL_SCALP_CVD,
            CHANNEL_SCALP_VWAP,
            CHANNEL_SCALP_DIVERGENCE,
            CHANNEL_SCALP_SUPERTREND,
            CHANNEL_SCALP_ICHIMOKU,
            CHANNEL_SCALP_ORDERBLOCK,
        ):
            assert chan.min_confidence >= 65, (
                f"{chan.name}.min_confidence={chan.min_confidence} unexpectedly changed."
            )


# ---------------------------------------------------------------------------
# Invariant 3: Router — WATCHLIST doctrine (free channel only, not active_signals)
# ---------------------------------------------------------------------------

class TestRouterSubPaidDrop:
    """Sub-65 confidence signals must drop cleanly — never enter
    ``_active_signals`` and never reach any Telegram channel.

    WATCHLIST tier was removed in the app-era doctrine reset; the previous
    "WATCHLIST → free channel zone alert" routing is gone.  These tests
    assert the post-removal contract.
    """

    @pytest.mark.asyncio
    async def test_sub_paid_scalp_signal_not_in_active_signals(self, queue, router, sent_messages):
        """Defensive: a signal tier-stamped legacy "WATCHLIST" (or any
        sub-65 confidence) must not enter the paid active lifecycle."""
        sig = _make_signal(
            channel="360_SCALP", confidence=55.0, signal_tier="WATCHLIST"
        )
        in_active = await _route_signal(router, queue, sig)
        assert not in_active

    @pytest.mark.asyncio
    async def test_sub_paid_signal_not_posted_to_paid_channel(self, queue, router, sent_messages):
        sig = _make_signal(
            channel="360_SCALP", confidence=55.0, signal_tier="WATCHLIST"
        )
        await _route_signal(router, queue, sig)
        paid_posts = [text for chat_id, text in sent_messages if chat_id == "premium"]
        assert not paid_posts

    @pytest.mark.asyncio
    async def test_sub_paid_signal_not_posted_to_free_channel(self, queue, router, sent_messages):
        """Post-removal: free channel keeps macro / signal-close storytelling
        but no preview signals."""
        sig = _make_signal(
            channel="360_SCALP", confidence=55.0, signal_tier="WATCHLIST"
        )
        sig.analyst_reason = "Trend Pullback Ema"
        sig.setup_class = "TREND_PULLBACK_EMA"
        await _route_signal(router, queue, sig)
        free_posts = [text for chat_id, text in sent_messages if chat_id == "free_channel"]
        assert not free_posts, (
            "Sub-65 signals must not produce free-channel posts after the "
            "WATCHLIST tier removal."
        )

    @pytest.mark.asyncio
    async def test_explicit_b_tier_below_floor_is_rejected(self, queue, router, sent_messages):
        """A signal stamped B tier but with sub-floor confidence is still
        rejected by the router's min-confidence check."""
        sig = _make_signal(
            channel="360_SCALP", confidence=55.0, signal_tier="B"
        )
        dispatched = await _route_signal(router, queue, sig)
        assert not dispatched


# ---------------------------------------------------------------------------
# Invariant 4: A+ behavior unchanged
# ---------------------------------------------------------------------------

class TestAPlusBehaviorUnchanged:
    """A+ signals (80+) continue to be dispatched — no regression."""

    @pytest.mark.asyncio
    async def test_a_plus_signal_dispatched(self, queue, router, sent_messages):
        sig = _make_signal(
            channel="360_SCALP", confidence=85.0, signal_tier="A+"
        )
        dispatched = await _route_signal(router, queue, sig)
        assert dispatched, "A+ signal (confidence=85) must still be dispatched."

    @pytest.mark.asyncio
    async def test_a_plus_boundary_80_dispatched(self, queue, router, sent_messages):
        sig = _make_signal(
            channel="360_SCALP", confidence=80.0, signal_tier="A+"
        )
        dispatched = await _route_signal(router, queue, sig)
        assert dispatched, "A+ signal at boundary (confidence=80) must still be dispatched."


# ---------------------------------------------------------------------------
# Invariant 5: B-tier at exact boundary (65) is dispatched
# ---------------------------------------------------------------------------

class TestBTierDispatch:
    """B-tier signals (65-79) must now be dispatched for 360_SCALP."""

    @pytest.mark.asyncio
    async def test_b_tier_at_boundary_dispatched(self, queue, router, sent_messages):
        """Confidence=65 (B-tier boundary) must now be dispatched."""
        sig = _make_signal(
            channel="360_SCALP", confidence=65.0, signal_tier="B"
        )
        dispatched = await _route_signal(router, queue, sig)
        assert dispatched, (
            "B-tier signal at confidence=65 must be dispatched. "
            "The old floor of 80 was the architecture contradiction."
        )

    @pytest.mark.asyncio
    async def test_b_tier_mid_range_dispatched(self, queue, router, sent_messages):
        """Mid-range B-tier signal (confidence=72) must be dispatched."""
        sig = _make_signal(
            channel="360_SCALP", confidence=72.0, signal_tier="B"
        )
        dispatched = await _route_signal(router, queue, sig)
        assert dispatched, "B-tier signal at confidence=72 must be dispatched."

    @pytest.mark.asyncio
    async def test_below_b_tier_not_dispatched(self, queue, router, sent_messages):
        """Confidence below 65 and not tagged WATCHLIST must be rejected."""
        sig = _make_signal(
            channel="360_SCALP", confidence=64.9, signal_tier="WATCHLIST"
        )
        # Override signal_tier to "B" to confirm it would be rejected (not bypass)
        sig.signal_tier = "B"
        dispatched = await _route_signal(router, queue, sig)
        assert not dispatched, (
            "Confidence=64.9 tagged 'B' (not WATCHLIST) must be rejected "
            "because it is below the 360_SCALP floor of 65."
        )
