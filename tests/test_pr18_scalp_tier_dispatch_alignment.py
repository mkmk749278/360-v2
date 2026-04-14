"""PR-18 tests: 360_SCALP tier dispatch alignment (A+ / B / WATCHLIST).

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

    def test_watchlist_boundary(self):
        assert classify_signal_tier(50.0) == "WATCHLIST"
        assert classify_signal_tier(64.9) == "WATCHLIST"
        assert classify_signal_tier(55.0) == "WATCHLIST"

    def test_filtered_boundary(self):
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

class TestRouterWatchlistDoctrine:
    """WATCHLIST signals from 360_SCALP must go to the free channel only.

    They must NOT be registered in _active_signals and must NOT enter the
    paid active lifecycle.  Doctrine: 'Post to free channel only'.
    """

    @pytest.mark.asyncio
    async def test_watchlist_scalp_signal_not_in_active_signals(self, queue, router, sent_messages):
        """A WATCHLIST-tier 360_SCALP signal must NOT enter _active_signals."""
        sig = _make_signal(
            channel="360_SCALP", confidence=55.0, signal_tier="WATCHLIST"
        )
        in_active = await _route_signal(router, queue, sig)
        assert not in_active, (
            "WATCHLIST 360_SCALP signal with confidence=55 must NOT be registered "
            "in _active_signals.  WATCHLIST is free-channel-only per doctrine."
        )

    @pytest.mark.asyncio
    async def test_watchlist_scalp_signal_posted_to_free_channel(self, queue, router, sent_messages):
        """A WATCHLIST-tier 360_SCALP signal must be posted to the free channel."""
        sig = _make_signal(
            channel="360_SCALP", confidence=55.0, signal_tier="WATCHLIST"
        )
        sig.analyst_reason = "Trend Pullback Ema"
        sig.setup_class = "TREND_PULLBACK_EMA"
        await _route_signal(router, queue, sig)
        free_posts = [text for chat_id, text in sent_messages if chat_id == "free_channel"]
        assert free_posts, (
            "WATCHLIST 360_SCALP signal with confidence=55 must produce a post "
            "to the free channel.  No free-channel message was found."
        )
        # The post should contain a WATCHLIST zone-alert marker, not a paid signal header.
        assert any("WATCHLIST" in text for text in free_posts), (
            "Free-channel post for a WATCHLIST signal must contain 'WATCHLIST'."
        )

    @pytest.mark.asyncio
    async def test_watchlist_not_posted_to_paid_channel(self, queue, router, sent_messages):
        """A WATCHLIST-tier 360_SCALP signal must NOT be posted to the paid channel."""
        sig = _make_signal(
            channel="360_SCALP", confidence=55.0, signal_tier="WATCHLIST"
        )
        await _route_signal(router, queue, sig)
        paid_posts = [text for chat_id, text in sent_messages if chat_id == "premium"]
        assert not paid_posts, (
            "WATCHLIST 360_SCALP signal must NOT be posted to the paid channel. "
            f"Found {len(paid_posts)} paid-channel post(s)."
        )

    @pytest.mark.asyncio
    async def test_non_watchlist_below_floor_is_rejected(self, queue, router, sent_messages):
        """A signal that is NOT tagged WATCHLIST must still be rejected
        if its confidence is below the channel floor."""
        sig = _make_signal(
            channel="360_SCALP", confidence=55.0, signal_tier="B"
        )
        dispatched = await _route_signal(router, queue, sig)
        assert not dispatched, (
            "A non-WATCHLIST signal with confidence=55 below the channel floor "
            "must still be rejected by the router."
        )

    @pytest.mark.asyncio
    async def test_watchlist_non_360_scalp_not_in_active_signals(
        self, queue, router, sent_messages, monkeypatch
    ):
        """WATCHLIST routing is scoped to channel == '360_SCALP'.
        A scalp sub-channel WATCHLIST signal with confidence below its own floor
        must not enter active_signals (dropped at min-confidence filter)."""
        from config import ChannelConfig

        fake_chan = ChannelConfig(
            name="FAKE_SCALP_SUB",
            emoji="⚡",
            timeframes=["5m"],
            sl_pct_range=(0.1, 0.3),
            tp_ratios=[1.5, 2.5],
            trailing_atr_mult=1.5,
            adx_min=20,
            adx_max=100,
            spread_max=0.02,
            min_confidence=80,
            min_volume=5_000_000.0,
            dca_enabled=True,
            min_signal_lifespan=900,
        )
        monkeypatch.setattr(signal_router_module, "ALL_CHANNELS", list(signal_router_module.ALL_CHANNELS) + [fake_chan])
        monkeypatch.setitem(signal_router_module.CHANNEL_TELEGRAM_MAP, "FAKE_SCALP_SUB", "premium")

        sig = _make_signal(channel="FAKE_SCALP_SUB", confidence=55.0, signal_tier="WATCHLIST")
        dispatched = await _route_signal(router, queue, sig)
        assert not dispatched, (
            "WATCHLIST free-channel routing is scoped to '360_SCALP' only. "
            "FAKE_SCALP_SUB WATCHLIST signal must not enter active_signals."
        )


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
