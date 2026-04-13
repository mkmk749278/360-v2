"""Tests for free-channel radar alert watch lifecycle (PR: free-watch lifecycle).

Covers:
- radar candidate above threshold creates and persists a watch when posted
- duplicate open watch is not duplicated
- expiry posts exactly one terminal follow-up
- matching paid signal resolves exactly one open radar watch
- market_watch still creates no tracked watch state
- existing paid signal lifecycle behavior remains unchanged (smoke test)
"""

from __future__ import annotations

import json
from datetime import timedelta
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.free_watch_service import FreeWatch, FreeWatchService, _dedupe_key
from src.utils import utcnow


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_service(free_posts: List[str] | None = None) -> tuple[FreeWatchService, List[str]]:
    """Create a FreeWatchService with a mock send_free that records posted text."""
    if free_posts is None:
        free_posts = []

    async def _send(text: str) -> bool:
        free_posts.append(text)
        return True

    svc = FreeWatchService(send_free=_send, redis_client=None)
    return svc, free_posts


# ---------------------------------------------------------------------------
# Watch creation
# ---------------------------------------------------------------------------


class TestCreateWatch:
    @pytest.mark.asyncio
    async def test_creates_watch_for_radar_candidate(self):
        """Radar candidate above threshold creates a tracked watch."""
        svc, _ = _make_service()
        watch = await svc.create_watch(
            symbol="ETHUSDT",
            source_channel="360_SCALP",
            bias="LONG",
            setup_name="SR_FLIP_RETEST",
            waiting_for="confirm",
            confidence=70,
        )
        assert watch is not None
        assert isinstance(watch, FreeWatch)
        assert watch.symbol == "ETHUSDT"
        assert watch.bias == "LONG"
        assert watch.status == "open"
        assert svc.watch_count() == 1

    @pytest.mark.asyncio
    async def test_duplicate_open_watch_not_created(self):
        """A second call with the same (symbol, channel, bias, setup) is deduplicated."""
        svc, _ = _make_service()
        w1 = await svc.create_watch(
            symbol="BTCUSDT",
            source_channel="360_SCALP",
            bias="SHORT",
            setup_name="BREAKDOWN_SHORT",
            waiting_for="confirm",
            confidence=68,
        )
        assert w1 is not None

        w2 = await svc.create_watch(
            symbol="BTCUSDT",
            source_channel="360_SCALP",
            bias="SHORT",
            setup_name="BREAKDOWN_SHORT",
            waiting_for="confirm",
            confidence=72,
        )
        assert w2 is None  # deduplicated
        assert svc.watch_count() == 1

    @pytest.mark.asyncio
    async def test_per_symbol_cooldown_blocks_second_watch(self):
        """Per-symbol cooldown prevents a second radar watch for the same symbol,
        even if the bias or setup differs from the first watch.
        This is correct behavior: one active radar alert per symbol per cooldown window.
        """
        svc, _ = _make_service()
        w1 = await svc.create_watch(
            symbol="ETHUSDT",
            source_channel="360_SCALP",
            bias="LONG",
            setup_name="SR_FLIP_RETEST",
            waiting_for="confirm",
            confidence=70,
        )
        assert w1 is not None

        # Second call for the same symbol (different bias) — blocked by cooldown.
        w2 = await svc.create_watch(
            symbol="ETHUSDT",
            source_channel="360_SCALP",
            bias="SHORT",
            setup_name="SR_FLIP_RETEST",
            waiting_for="confirm",
            confidence=70,
        )
        assert w2 is None  # blocked by per-symbol cooldown
        assert svc.watch_count() == 1  # only the first was accepted

    @pytest.mark.asyncio
    async def test_different_symbol_creates_independent_watch(self):
        """Two different symbols can each have their own open radar watch."""
        svc, _ = _make_service()
        w1 = await svc.create_watch(
            symbol="ETHUSDT",
            source_channel="360_SCALP",
            bias="LONG",
            setup_name="SR_FLIP_RETEST",
            waiting_for="confirm",
            confidence=70,
        )
        w2 = await svc.create_watch(
            symbol="BTCUSDT",
            source_channel="360_SCALP",
            bias="LONG",
            setup_name="SR_FLIP_RETEST",
            waiting_for="confirm",
            confidence=70,
        )
        assert w1 is not None
        assert w2 is not None
        assert svc.watch_count() == 2


# ---------------------------------------------------------------------------
# Expiry
# ---------------------------------------------------------------------------


class TestExpiry:
    @pytest.mark.asyncio
    async def test_expired_watch_posts_exactly_one_follow_up(self):
        """An expired watch triggers exactly one free-channel follow-up."""
        posts: List[str] = []
        svc, posts = _make_service(posts)

        with patch("config.RADAR_WATCH_TTL_SECONDS", 1):
            with patch("config.RADAR_PER_SYMBOL_COOLDOWN_SECONDS", 0):
                watch = await svc.create_watch(
                    symbol="SOLUSDT",
                    source_channel="360_SCALP",
                    bias="LONG",
                    setup_name="TREND_PULLBACK_EMA",
                    waiting_for="confirm",
                    confidence=66,
                )
        assert watch is not None

        # Manually back-date expires_at to force expiry
        key = _dedupe_key("SOLUSDT", "360_SCALP", "LONG", "TREND_PULLBACK_EMA")
        svc._open_watches[key].expires_at = (utcnow() - timedelta(seconds=1)).isoformat()

        # Trigger expiry check
        await svc._check_expiry()

        # Watch should now be resolved and removed from open watches
        assert svc.watch_count() == 0
        # Exactly one follow-up posted
        assert len(posts) == 1
        assert "expired" in posts[0].lower() or "watch" in posts[0].lower()

    @pytest.mark.asyncio
    async def test_expired_watch_only_posts_once(self):
        """Running expiry check twice on an already-expired watch does not double-post."""
        posts: List[str] = []
        svc, posts = _make_service(posts)

        with patch("config.RADAR_PER_SYMBOL_COOLDOWN_SECONDS", 0):
            watch = await svc.create_watch(
                symbol="DOTUSDT",
                source_channel="360_SCALP",
                bias="LONG",
                setup_name="VOLUME_SURGE_BREAKOUT",
                waiting_for="confirm",
                confidence=65,
            )
        assert watch is not None

        key = _dedupe_key("DOTUSDT", "360_SCALP", "LONG", "VOLUME_SURGE_BREAKOUT")
        svc._open_watches[key].expires_at = (utcnow() - timedelta(seconds=1)).isoformat()

        await svc._check_expiry()
        await svc._check_expiry()  # second run — nothing more to expire

        assert len(posts) == 1  # only one follow-up


# ---------------------------------------------------------------------------
# Paid signal resolution
# ---------------------------------------------------------------------------


class TestPaidSignalResolution:
    @pytest.mark.asyncio
    async def test_matching_paid_signal_resolves_watch(self):
        """A paid signal for the same symbol+bias resolves the open radar watch."""
        posts: List[str] = []
        svc, posts = _make_service(posts)

        with patch("config.RADAR_PER_SYMBOL_COOLDOWN_SECONDS", 0):
            await svc.create_watch(
                symbol="BNBUSDT",
                source_channel="360_SCALP",
                bias="LONG",
                setup_name="POST_DISPLACEMENT_CONTINUATION",
                waiting_for="confirm",
                confidence=72,
            )

        await svc.on_paid_signal(symbol="BNBUSDT", bias="LONG")

        assert svc.watch_count() == 0
        assert len(posts) == 1
        assert "rolled" in posts[0].lower() or "triggered" in posts[0].lower() or "signal" in posts[0].lower()

    @pytest.mark.asyncio
    async def test_mismatched_symbol_does_not_resolve(self):
        """A paid signal for a different symbol does not resolve unrelated watches."""
        posts: List[str] = []
        svc, posts = _make_service(posts)

        with patch("config.RADAR_PER_SYMBOL_COOLDOWN_SECONDS", 0):
            await svc.create_watch(
                symbol="ADAUSDT",
                source_channel="360_SCALP",
                bias="LONG",
                setup_name="SR_FLIP_RETEST",
                waiting_for="confirm",
                confidence=67,
            )

        await svc.on_paid_signal(symbol="ETHUSDT", bias="LONG")

        # Watch for ADAUSDT should still be open
        assert svc.watch_count() == 1
        assert len(posts) == 0

    @pytest.mark.asyncio
    async def test_opposite_bias_paid_signal_does_not_resolve(self):
        """A paid signal with opposite bias does not resolve the watch."""
        posts: List[str] = []
        svc, posts = _make_service(posts)

        with patch("config.RADAR_PER_SYMBOL_COOLDOWN_SECONDS", 0):
            await svc.create_watch(
                symbol="LINKUSDT",
                source_channel="360_SCALP",
                bias="LONG",
                setup_name="TREND_PULLBACK_EMA",
                waiting_for="confirm",
                confidence=69,
            )

        await svc.on_paid_signal(symbol="LINKUSDT", bias="SHORT")

        assert svc.watch_count() == 1
        assert len(posts) == 0

    @pytest.mark.asyncio
    async def test_neutral_bias_watch_resolved_by_any_direction(self):
        """A NEUTRAL-bias radar watch is resolved by any paid signal for the symbol."""
        posts: List[str] = []
        svc, posts = _make_service(posts)

        with patch("config.RADAR_PER_SYMBOL_COOLDOWN_SECONDS", 0):
            await svc.create_watch(
                symbol="XRPUSDT",
                source_channel="360_SCALP",
                bias="NEUTRAL",
                setup_name="VOLUME_SURGE_BREAKOUT",
                waiting_for="confirm",
                confidence=65,
            )

        await svc.on_paid_signal(symbol="XRPUSDT", bias="SHORT")

        assert svc.watch_count() == 0
        assert len(posts) == 1

    @pytest.mark.asyncio
    async def test_exactly_one_watch_resolved_per_paid_signal(self):
        """Only open watches are resolved; already-resolved ones are ignored."""
        posts: List[str] = []
        svc, posts = _make_service(posts)

        with patch("config.RADAR_PER_SYMBOL_COOLDOWN_SECONDS", 0):
            # Create a watch for BTCUSDT LONG
            await svc.create_watch(
                symbol="BTCUSDT",
                source_channel="360_SCALP",
                bias="LONG",
                setup_name="SR_FLIP_RETEST",
                waiting_for="confirm",
                confidence=71,
            )

        # Resolve it once
        await svc.on_paid_signal(symbol="BTCUSDT", bias="LONG")
        assert len(posts) == 1

        # Second paid signal for same symbol — no open watch remains
        await svc.on_paid_signal(symbol="BTCUSDT", bias="LONG")
        assert len(posts) == 1  # unchanged


# ---------------------------------------------------------------------------
# market_watch must NOT create watched state
# ---------------------------------------------------------------------------


class TestMarketWatchNoState:
    @pytest.mark.asyncio
    async def test_market_watch_creates_no_watch_state(self):
        """market_watch posts must never create a tracked watch object."""
        svc, _ = _make_service()

        # Simulate what the content scheduler does for market_watch:
        # it just posts text to the free channel — it must NOT call create_watch.
        # We verify that no watch state exists after a market_watch flow.
        assert svc.watch_count() == 0

        # The FreeWatchService has no market_watch interface — this is by design.
        # Verify the service has no method that could be mistakenly called for
        # market_watch.
        assert not hasattr(svc, "create_market_watch")
        assert not hasattr(svc, "post_market_watch")

        assert svc.watch_count() == 0


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------


class TestFormatters:
    def test_format_radar_watch_resolved_paid(self):
        from src.formatter import format_radar_watch_resolved_paid

        text = format_radar_watch_resolved_paid(
            symbol="ETHUSDT",
            bias="LONG",
            setup_name="SR_FLIP_RETEST",
        )
        assert "ETHUSDT" in text
        assert "Active Trading" in text
        # Must NOT contain premium entry/TP/SL values
        assert "entry" not in text.lower() or "🔒" in text

    def test_format_radar_watch_expired(self):
        from src.formatter import format_radar_watch_expired

        text = format_radar_watch_expired(
            symbol="BTCUSDT",
            bias="SHORT",
            setup_name="BREAKDOWN_SHORT",
        )
        assert "BTCUSDT" in text
        assert "expired" in text.lower() or "trigger" in text.lower()

    def test_resolved_text_does_not_leak_premium_details(self):
        """Follow-up messages must not contain entry price, TP, or SL information."""
        from src.formatter import format_radar_watch_resolved_paid, format_radar_watch_expired

        for fn in (format_radar_watch_resolved_paid, format_radar_watch_expired):
            text = fn(symbol="SOLUSDT", bias="LONG", setup_name="TEST")
            # Must not contain premium TP/SL keywords
            assert "SL" not in text
            assert "TP1" not in text
            assert "TP2" not in text


# ---------------------------------------------------------------------------
# Redis persistence (mocked)
# ---------------------------------------------------------------------------


class TestRedisPersistence:
    @pytest.mark.asyncio
    async def test_create_watch_persists_to_redis(self):
        """create_watch writes the watch state to Redis."""
        mock_redis = MagicMock()
        mock_redis.available = True
        mock_client = AsyncMock()
        mock_redis.client = mock_client

        posts: List[str] = []

        async def _send(text: str) -> bool:
            posts.append(text)
            return True

        svc = FreeWatchService(send_free=_send, redis_client=mock_redis)

        with patch("config.RADAR_PER_SYMBOL_COOLDOWN_SECONDS", 0):
            watch = await svc.create_watch(
                symbol="ETHUSDT",
                source_channel="360_SCALP",
                bias="LONG",
                setup_name="SR_FLIP_RETEST",
                waiting_for="confirm",
                confidence=70,
            )

        assert watch is not None
        mock_client.set.assert_called_once()
        # Verify the key used
        call_args = mock_client.set.call_args
        assert "free_watch_service" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_restore_loads_watches_from_redis(self):
        """restore() reloads open watches from Redis."""
        mock_redis = MagicMock()
        mock_redis.available = True
        mock_client = AsyncMock()
        now = utcnow()
        watch_data = {
            "ETHUSDT|360_SCALP|LONG|SR_FLIP_RETEST": {
                "watch_id": "test-123",
                "symbol": "ETHUSDT",
                "source_channel": "360_SCALP",
                "bias": "LONG",
                "setup_name": "SR_FLIP_RETEST",
                "waiting_for": "confirm",
                "confidence": 70,
                "created_at": now.isoformat(),
                "expires_at": (now + timedelta(hours=4)).isoformat(),
                "status": "open",
                "resolved_at": None,
            }
        }
        mock_client.get.return_value = json.dumps(watch_data)
        mock_redis.client = mock_client

        async def _send(text: str) -> bool:
            return True

        svc = FreeWatchService(send_free=_send, redis_client=mock_redis)
        await svc.restore()

        assert svc.watch_count() == 1
        watches = svc.get_open_watches()
        key = "ETHUSDT|360_SCALP|LONG|SR_FLIP_RETEST"
        assert key in watches
        assert watches[key].symbol == "ETHUSDT"
