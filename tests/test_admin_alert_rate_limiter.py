"""Tests for the global admin-alert rate limiter.

Owner reported bursts of 40-50 identical admin alerts for a single
underlying event 2026-05-08.  Each caller (WS manager, telemetry,
circuit breaker, scanner, signal router) implements its own per-source
cooldown — bugs in any one bypass the rate-limit and spam Telegram.

The fix is a last-line defense inside ``TelegramBot.send_admin_alert``:
keyed by the first ``ADMIN_ALERT_DEDUP_KEY_LEN`` characters of the
message so duplicates with rolling counters (e.g. "total drops: 7"
then "8") share a key and coalesce.

These tests verify:
* Identical alerts within the cooldown window are suppressed
* Different alerts are NOT suppressed
* After cooldown expires, the next alert fires with a "(N suppressed)"
  suffix counting the silenced ones
* Setting the cooldown to 0 disables the limiter (test escape hatch)
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.telegram_bot import TelegramBot


@pytest.fixture
def bot():
    """Bot with a mocked send_message so tests don't hit the network."""
    b = TelegramBot()
    b.send_message = AsyncMock(return_value=True)  # type: ignore[assignment]
    return b


class TestAdminAlertRateLimiter:
    @pytest.mark.asyncio
    async def test_first_alert_fires(self, bot):
        with patch("src.telegram_bot.TELEGRAM_ADMIN_CHAT_ID", "TEST-CHAT"):
            ok = await bot.send_admin_alert("⚠️ REST fallback active (futures)")
        assert ok is True
        assert bot.send_message.await_count == 1

    @pytest.mark.asyncio
    async def test_duplicate_within_cooldown_suppressed(self, bot):
        """Same prefix → suppressed inside the cooldown window."""
        with patch("src.telegram_bot.TELEGRAM_ADMIN_CHAT_ID", "TEST-CHAT"), \
             patch(
                 "src.telegram_bot.ADMIN_ALERT_GLOBAL_COOLDOWN_SECONDS", 300,
             ):
            await bot.send_admin_alert("⚠️ REST fallback active (futures, total drops: 1)")
            await bot.send_admin_alert("⚠️ REST fallback active (futures, total drops: 2)")
            await bot.send_admin_alert("⚠️ REST fallback active (futures, total drops: 3)")
            await bot.send_admin_alert("⚠️ REST fallback active (futures, total drops: 4)")
        # First fires, the next 3 share the same prefix and are suppressed.
        assert bot.send_message.await_count == 1

    @pytest.mark.asyncio
    async def test_different_alerts_not_suppressed(self, bot):
        """Different prefixes → both fire, no cross-pollination."""
        with patch("src.telegram_bot.TELEGRAM_ADMIN_CHAT_ID", "TEST-CHAT"), \
             patch(
                 "src.telegram_bot.ADMIN_ALERT_GLOBAL_COOLDOWN_SECONDS", 300,
             ):
            await bot.send_admin_alert("⚠️ REST fallback active (futures)")
            await bot.send_admin_alert("🚨 Signal Lost — BTCUSDT")
        assert bot.send_message.await_count == 2

    @pytest.mark.asyncio
    async def test_suppressed_count_surfaces_after_cooldown(self, bot, monkeypatch):
        """When cooldown expires, the next alert includes a "(+N suppressed)"
        suffix counting the silenced duplicates.  No silent dropping."""
        # Use a tiny cooldown so the test can advance time cheaply.
        with patch("src.telegram_bot.TELEGRAM_ADMIN_CHAT_ID", "TEST-CHAT"), \
             patch(
                 "src.telegram_bot.ADMIN_ALERT_GLOBAL_COOLDOWN_SECONDS", 60,
             ):
            # Frozen time at T=0 for the first 3 calls.
            current_t = [1000.0]
            monkeypatch.setattr(
                "src.telegram_bot.time.monotonic", lambda: current_t[0],
            )
            await bot.send_admin_alert("⚠️ REST fallback active (futures, total drops: 1)")
            await bot.send_admin_alert("⚠️ REST fallback active (futures, total drops: 2)")
            await bot.send_admin_alert("⚠️ REST fallback active (futures, total drops: 3)")
            assert bot.send_message.await_count == 1
            # Advance past cooldown and fire again.
            current_t[0] = 1100.0  # +100s, past the 60s cooldown
            await bot.send_admin_alert("⚠️ REST fallback active (futures, total drops: 4)")

        assert bot.send_message.await_count == 2
        # Inspect the second call — it must include the suppression suffix.
        second_call_text = bot.send_message.await_args_list[1].args[1]
        assert "(+2 suppressed during last 60s)" in second_call_text

    @pytest.mark.asyncio
    async def test_zero_cooldown_disables_limiter(self, bot):
        """Test escape hatch: ADMIN_ALERT_GLOBAL_COOLDOWN_SECONDS=0 →
        every call fires, no rate limiting."""
        with patch("src.telegram_bot.TELEGRAM_ADMIN_CHAT_ID", "TEST-CHAT"), \
             patch(
                 "src.telegram_bot.ADMIN_ALERT_GLOBAL_COOLDOWN_SECONDS", 0,
             ):
            for _ in range(5):
                await bot.send_admin_alert("⚠️ same text")
        assert bot.send_message.await_count == 5

    @pytest.mark.asyncio
    async def test_no_admin_chat_returns_false(self, bot):
        """No admin chat configured → returns False without hitting the limiter."""
        with patch("src.telegram_bot.TELEGRAM_ADMIN_CHAT_ID", ""):
            ok = await bot.send_admin_alert("⚠️ test")
        assert ok is False
        assert bot.send_message.await_count == 0

    @pytest.mark.asyncio
    async def test_dedup_key_only_uses_prefix(self, bot):
        """Long divergent suffixes share the same prefix → suppressed.
        This is what coalesces "total drops: 7" with "total drops: 80"."""
        with patch("src.telegram_bot.TELEGRAM_ADMIN_CHAT_ID", "TEST-CHAT"), \
             patch(
                 "src.telegram_bot.ADMIN_ALERT_GLOBAL_COOLDOWN_SECONDS", 300,
             ), patch(
                 "src.telegram_bot.ADMIN_ALERT_DEDUP_KEY_LEN", 30,
             ):
            await bot.send_admin_alert("⚠️ Same prefix here — variation A blah blah")
            await bot.send_admin_alert("⚠️ Same prefix here — variation B different tail")
            await bot.send_admin_alert("⚠️ Same prefix here — variation C yet another")
        assert bot.send_message.await_count == 1
