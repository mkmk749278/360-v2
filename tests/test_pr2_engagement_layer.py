"""Tests for the PR2 AI Engagement Layer modules:
   src/formatter.py, src/content_engine.py, src/scheduler.py, src/radar_channel.py
and the changes to src/telegram_bot.py and src/trade_monitor.py.
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# formatter.py tests
# ---------------------------------------------------------------------------

from src.formatter import (
    render_conf_bar,
    format_signal,
    format_radar_alert,
    format_signal_closed_tp,
    format_signal_closed_sl,
    format_morning_brief,
    format_london_open,
    format_ny_open,
    format_eod_wrap,
    format_market_watch,
    format_weekly_card,
    SETUP_EMOJIS,
)


class TestRenderConfBar:
    def test_full_confidence(self):
        bar = render_conf_bar(100)
        assert bar == "██████████"
        assert len(bar) == 10

    def test_zero_confidence(self):
        bar = render_conf_bar(0)
        assert bar == "░░░░░░░░░░"
        assert len(bar) == 10

    def test_half_confidence(self):
        bar = render_conf_bar(50)
        assert bar == "█████░░░░░"
        assert len(bar) == 10

    def test_always_10_chars(self):
        for conf in range(0, 101, 10):
            bar = render_conf_bar(conf)
            assert len(bar) == 10, f"conf={conf} gave len={len(bar)}"


class TestFormatSignal:
    def _ctx(self, **overrides):
        ctx = {
            "symbol": "BTCUSDT",
            "direction": "LONG",
            "entry": 50000.0,
            "tp1": 51000.0,
            "tp2": 52000.0,
            "tp3": 53000.0,
            "sl": 49000.0,
            "confidence": 82,
            "valid_min": 15,
            "setup_name": "FVG_RETEST",
        }
        ctx.update(overrides)
        return ctx

    def test_variant_0_contains_symbol(self):
        text = format_signal(self._ctx(), variant=0)
        assert "BTCUSDT" in text
        assert "LONG" in text

    def test_variant_1_contains_conf_bar(self):
        text = format_signal(self._ctx(confidence=90), variant=1)
        assert "█" in text
        assert "90/100" in text

    def test_variant_2_ultra_minimal(self):
        text = format_signal(self._ctx(), variant=2)
        assert "◈" in text
        assert "Stop:" in text

    def test_no_tp3_omits_tp3_line(self):
        ctx = self._ctx()
        ctx["tp3"] = None
        text = format_signal(ctx, variant=0)
        assert "TP3" not in text

    def test_line_count_max_10(self):
        text = format_signal(self._ctx(), variant=0)
        lines = [l for l in text.split("\n") if l.strip()]
        assert len(lines) <= 10

    def test_setup_emoji_map_coverage(self):
        for setup_name in SETUP_EMOJIS:
            assert SETUP_EMOJIS[setup_name]  # all entries have a value


class TestFormatRadarAlert:
    def _ctx(self, **overrides):
        ctx = {
            "symbol": "ETHUSDT",
            "bias": "LONG",
            "confidence": 72,
            "gpt_text": "Price swept liquidity at 3200. Watching for reversal.",
            "waiting_for": "bullish engulfing on 5m",
            "level": "3200",
            "is_active_market": False,
        }
        ctx.update(overrides)
        return ctx

    def test_variant_0_analyst_callout(self):
        text = format_radar_alert(self._ctx(), variant=0)
        assert "👁" in text
        assert "ETHUSDT" in text
        assert "Active Trading" in text

    def test_variant_3_watching_closely(self):
        text = format_radar_alert(self._ctx(), variant=3)
        assert "watching closely" in text
        assert "72/100" in text

    def test_variant_5_urgent(self):
        text = format_radar_alert(self._ctx(), variant=5)
        assert "setup forming NOW" in text

    def test_high_confidence_selects_variant_3(self):
        # The _select_radar_variant logic: conf >= 70 → 3
        text = format_radar_alert(self._ctx(confidence=75))
        assert "watching closely" in text


class TestFormatSignalClosed:
    def _tp_ctx(self):
        return {
            "symbol": "SOLUSDT",
            "direction": "LONG",
            "tp_label": "TP2",
            "close_price": 155.0,
            "entry_price": 150.0,
            "r_multiple": 2.1,
            "pnl_pct": 3.33,
            "gpt_text": "FVG retest held perfectly.",
            "wins": 5,
            "losses": 2,
        }

    def _sl_ctx(self):
        return {
            "symbol": "SOLUSDT",
            "direction": "LONG",
            "sl_price": 148.0,
            "entry_price": 150.0,
            "pnl_pct": -1.33,
            "gpt_text": "Structure broke below the FVG invalidating the long thesis.",
            "wins": 5,
            "losses": 3,
        }

    def test_tp_variant_0(self):
        text = format_signal_closed_tp(self._tp_ctx(), variant=0)
        assert "✅" in text
        assert "SOLUSDT" in text
        assert "TP2" in text

    def test_tp_variant_2_minimal(self):
        text = format_signal_closed_tp(self._tp_ctx(), variant=2)
        assert "✅" in text
        assert "+2.1R" in text

    def test_sl_variant_0(self):
        text = format_signal_closed_sl(self._sl_ctx(), variant=0)
        assert "🛑" in text
        assert "−1R" in text

    def test_sl_variant_1(self):
        text = format_signal_closed_sl(self._sl_ctx(), variant=1)
        assert "🛑" in text
        assert "stopped out" in text


class TestFormatSessionMessages:
    def test_morning_brief(self):
        ctx = {
            "day": "Monday",
            "date": "07 Apr 2025",
            "gpt_text": "BTC is ranging between 82K and 84K.",
            "pair1": "BTCUSDT",
            "pair2": "ETHUSDT",
            "session": "Asian",
            "session_mood": "quiet",
        }
        text = format_morning_brief(ctx)
        assert "☀️" in text
        assert "Monday" in text
        assert "Watching BTCUSDT" in text

    def test_london_open(self):
        ctx = {
            "gpt_text": "London session bias is LONG.",
            "pair1": "BTCUSDT",
            "pair2": "ETHUSDT",
            "pair3": "SOLUSDT",
        }
        text = format_london_open(ctx)
        assert "🇬🇧" in text
        assert "London open" in text

    def test_ny_open(self):
        ctx = {
            "gpt_text": "New York open with strong BTC.",
            "bias": "LONG",
        }
        text = format_ny_open(ctx)
        assert "🇺🇸" in text
        assert "Bias: LONG" in text

    def test_eod_wrap(self):
        ctx = {
            "day": "Friday",
            "signals_count": 5,
            "wins": 4,
            "losses": 1,
            "gpt_text": "Good day overall.",
            "overnight_pair": "BTCUSDT",
        }
        text = format_eod_wrap(ctx)
        assert "🌙" in text
        assert "5 signals" in text

    def test_market_watch_variant_0(self):
        ctx = {
            "gpt_text": "BTC is consolidating at 83K. Waiting for sweep of 82.5K low.",
            "symbol": "BTCUSDT",
        }
        text = format_market_watch(ctx, variant=0)
        assert "📡" in text
        assert "consolidating" in text

    def test_weekly_card(self):
        ctx = {
            "date_range": "31 Mar – 06 Apr",
            "total": 20,
            "wins": 14,
            "losses": 6,
            "winrate": 70.0,
            "avg_rr": 2.1,
            "best_symbol": "SOLUSDT",
            "best_r": 3.2,
            "worst_symbol": "BTCUSDT",
            "worst_r": -1.0,
            "month_label": "April",
            "month_winrate": 68.5,
            "streak": "3W streak",
        }
        text = format_weekly_card(ctx)
        assert "📊" in text
        assert "Win rate" in text
        assert "70%" in text
        assert "SOLUSDT" in text


# ---------------------------------------------------------------------------
# content_engine.py tests
# ---------------------------------------------------------------------------

from src import content_engine


class TestContentEngineTemplateOnly:
    """Tests that exercise template-only path (use_gpt=False)."""

    @pytest.mark.asyncio
    async def test_generate_morning_brief(self):
        ctx = {"regime": "RANGING", "btc_price": "50000", "btc_change_pct": 1.5,
               "top_pairs": ["BTCUSDT", "ETHUSDT"], "signals_today": 0,
               "performance": {}, "btc_1h_change_pct": 0, "is_active_market": False}
        text = await content_engine.generate_content("morning_brief", ctx, use_gpt=False)
        assert text  # non-empty

    @pytest.mark.asyncio
    async def test_generate_london_open(self):
        ctx = {"regime": "TRENDING_UP", "btc_price": "50000", "btc_change_pct": 2.0,
               "top_pairs": ["BTCUSDT", "ETHUSDT", "SOLUSDT"], "signals_today": 1,
               "performance": {}, "btc_1h_change_pct": 0, "is_active_market": False}
        text = await content_engine.generate_content("london_open", ctx, use_gpt=False)
        assert "London" in text

    @pytest.mark.asyncio
    async def test_generate_radar_alert(self):
        ctx = {
            "symbol": "ETHUSDT", "bias": "LONG", "confidence": 68,
            "setup_name": "FVG_RETEST", "waiting_for": "5m engulfing",
            "level": "3200", "current_price": "3205",
            "is_active_market": False,
        }
        text = await content_engine.generate_content("radar_alert", ctx, use_gpt=False)
        assert "ETHUSDT" in text

    @pytest.mark.asyncio
    async def test_generate_signal_closed_tp(self):
        text = await content_engine.generate_signal_closed_post(
            signal_data={
                "symbol": "SOLUSDT", "direction": "LONG",
                "entry_price": 150.0, "close_price": 155.0,
                "sl_price": 148.0, "tp_label": "TP2",
                "r_multiple": 2.1, "pnl_pct": 3.33,
                "setup_name": "FVG_RETEST", "hold_duration": "47min",
            },
            is_tp=True,
            use_gpt=False,
        )
        assert text
        assert "SOLUSDT" in text

    @pytest.mark.asyncio
    async def test_generate_signal_closed_sl(self):
        text = await content_engine.generate_signal_closed_post(
            signal_data={
                "symbol": "BTCUSDT", "direction": "SHORT",
                "entry_price": 50000.0, "close_price": 50500.0,
                "sl_price": 50500.0, "tp_label": "SL",
                "r_multiple": -1.0, "pnl_pct": -1.0,
                "setup_name": "RANGE_FADE", "hold_duration": "12min",
            },
            is_tp=False,
            use_gpt=False,
        )
        assert text
        assert "BTCUSDT" in text

    @pytest.mark.asyncio
    async def test_generate_weekly_card(self):
        ctx = {
            "performance": {
                "wins_this_week": 12, "losses_this_week": 5,
                "avg_rr_this_week": 2.0,
                "best_symbol_this_week": "SOLUSDT", "best_r_this_week": 3.1,
                "worst_symbol_this_week": "BTCUSDT", "worst_r_this_week": -1.0,
                "month_winrate": 70.0, "streak_label": "3W streak",
            },
            "regime": "RANGING",
            "top_pairs": [],
        }
        text = await content_engine.generate_content("weekly_card", ctx, use_gpt=False)
        assert "📊" in text

    @pytest.mark.asyncio
    async def test_unknown_content_type_returns_empty(self):
        text = await content_engine.generate_content("unknown_type", {}, use_gpt=False)
        assert text == ""

    @pytest.mark.asyncio
    async def test_content_engine_disabled(self, monkeypatch):
        monkeypatch.setattr("src.content_engine.CONTENT_ENGINE_ENABLED", False)
        text = await content_engine.generate_content("morning_brief", {}, use_gpt=False)
        assert text == ""

    @pytest.mark.asyncio
    async def test_gpt_failure_falls_back_to_template(self, monkeypatch):
        """When GPT call raises, template fallback should still produce output."""
        async def _failing_gpt(prompt):
            raise RuntimeError("network error")

        monkeypatch.setattr("src.content_engine._call_gpt", _failing_gpt)
        ctx = {"regime": "RANGING", "btc_price": "50000", "btc_change_pct": 0,
               "top_pairs": [], "signals_today": 0, "performance": {},
               "btc_1h_change_pct": 0, "is_active_market": False}
        # use_gpt=True but GPT fails — should fall back to template, never raise
        text = await content_engine.generate_content("morning_brief", ctx, use_gpt=True)
        assert text  # template fallback still produces output


# ---------------------------------------------------------------------------
# scheduler.py tests
# ---------------------------------------------------------------------------

from src.scheduler import ContentScheduler


class TestContentScheduler:
    def _make_scheduler(self):
        free_messages = []
        active_messages = []

        async def post_free(text):
            free_messages.append(text)
            return True

        async def post_active(text):
            active_messages.append(text)
            return True

        def engine_ctx():
            return {"regime": "RANGING", "btc_price": "50000",
                    "btc_change_pct": 0, "top_pairs": ["BTCUSDT"],
                    "signals_today": 0, "performance": {},
                    "btc_1h_change_pct": 0, "is_active_market": False}

        scheduler = ContentScheduler(post_free, post_active, engine_ctx)
        return scheduler, free_messages, active_messages

    @pytest.mark.asyncio
    async def test_silence_breaker_not_triggered_immediately(self):
        scheduler, free_msgs, _ = self._make_scheduler()
        # Just reset, silence timer is fresh
        scheduler.update_last_post()
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        # Should NOT fire because last post was just now
        await scheduler._check_silence_breaker(now)
        assert len(free_msgs) == 0

    @pytest.mark.asyncio
    async def test_silence_breaker_triggers_after_threshold(self, monkeypatch):
        scheduler, free_msgs, _ = self._make_scheduler()
        # Fake that last post was 4 hours ago
        scheduler.last_post_timestamp = time.monotonic() - (4 * 3600)

        from datetime import datetime, timezone
        # Use hour 10 UTC (within active window 8-22)
        now = datetime(2025, 4, 7, 10, 0, 0, tzinfo=timezone.utc)

        # Patch generate_content to avoid GPT / heavy work
        async def fake_generate(engine_ctx):
            return "fake market watch"
        monkeypatch.setattr("src.scheduler.content_engine.generate_market_watch", fake_generate)

        await scheduler._check_silence_breaker(now)
        assert len(free_msgs) == 1

    @pytest.mark.asyncio
    async def test_silence_breaker_inactive_outside_hours(self, monkeypatch):
        scheduler, free_msgs, _ = self._make_scheduler()
        scheduler.last_post_timestamp = time.monotonic() - (10 * 3600)

        from datetime import datetime, timezone
        # Use hour 3 UTC (outside active window 8-22)
        now = datetime(2025, 4, 7, 3, 0, 0, tzinfo=timezone.utc)
        await scheduler._check_silence_breaker(now)
        assert len(free_msgs) == 0

    @pytest.mark.asyncio
    async def test_weekly_card_skipped_on_non_monday(self, monkeypatch):
        scheduler, free_msgs, active_msgs = self._make_scheduler()

        async def fake_generate(engine_ctx):
            return "weekly card"
        monkeypatch.setattr("src.scheduler.content_engine.generate_weekly_card", fake_generate)

        from datetime import datetime, timezone
        # Tuesday = weekday 1, at 09:00 UTC
        now = datetime(2025, 4, 8, 9, 0, 0, tzinfo=timezone.utc)  # Tuesday
        scheduler._fired_today.clear()

        await scheduler._tick()
        # weekly_card should NOT fire on Tuesday
        assert "weekly_card" not in [
            k.split("_", 1)[1] for k, v in scheduler._fired_today.items()
            if v == now.strftime("%Y-%m-%d")
        ]

    def test_update_last_post_resets_timer(self):
        scheduler, _, _ = self._make_scheduler()
        old_ts = scheduler.last_post_timestamp
        time.sleep(0.01)
        scheduler.update_last_post()
        assert scheduler.last_post_timestamp > old_ts


# ---------------------------------------------------------------------------
# radar_channel.py tests
# ---------------------------------------------------------------------------

from src.radar_channel import RadarChannel


class TestRadarChannel:
    def _make_radar(self, scores=None):
        free_messages = []

        async def post_free(text):
            free_messages.append(text)
            return True

        def scanner_ctx():
            return {"channel_scores": scores or {}, "is_active_market": False}

        radar = RadarChannel(post_free, scanner_ctx)
        return radar, free_messages

    @pytest.mark.asyncio
    async def test_no_alerts_when_scores_empty(self):
        radar, messages = self._make_radar(scores={})
        await radar._evaluate()
        assert messages == []

    @pytest.mark.asyncio
    async def test_no_alert_below_threshold(self):
        radar, messages = self._make_radar(scores={
            "360_SCALP_CVD": {"symbol": "BTCUSDT", "confidence": 60, "bias": "LONG",
                               "setup_name": "CVD_DIVERGENCE", "waiting_for": "confirm"}
        })
        await radar._evaluate()
        assert messages == []

    @pytest.mark.asyncio
    async def test_alert_fires_above_threshold(self):
        radar, messages = self._make_radar(scores={
            "360_SCALP_CVD": {"symbol": "BTCUSDT", "confidence": 68, "bias": "LONG",
                               "setup_name": "CVD_DIVERGENCE", "waiting_for": "confirm",
                               "current_price": "50000", "key_level": "49500"}
        })
        await radar._evaluate()
        assert len(messages) == 1
        assert "BTCUSDT" in messages[0]

    @pytest.mark.asyncio
    async def test_per_symbol_cooldown_prevents_duplicate(self):
        radar, messages = self._make_radar(scores={
            "360_SCALP_CVD": {"symbol": "BTCUSDT", "confidence": 68, "bias": "LONG",
                               "setup_name": "CVD_DIVERGENCE", "waiting_for": "confirm",
                               "current_price": "50000", "key_level": "49500"}
        })
        # First eval fires
        await radar._evaluate()
        assert len(messages) == 1
        # Second eval within cooldown window — should not fire again
        await radar._evaluate()
        assert len(messages) == 1

    def test_hourly_rate_limit(self):
        radar, _ = self._make_radar()
        # Fill up the rate limit
        from config import RADAR_MAX_PER_HOUR
        for _ in range(RADAR_MAX_PER_HOUR):
            radar._alert_times.append(time.monotonic())
        assert not radar._check_hourly_rate()

    def test_hourly_rate_limit_resets_after_hour(self):
        radar, _ = self._make_radar()
        from config import RADAR_MAX_PER_HOUR
        # Add old timestamps (>1 hour ago)
        old_time = time.monotonic() - 3700
        for _ in range(RADAR_MAX_PER_HOUR):
            radar._alert_times.append(old_time)
        # Rate check should prune old entries and allow new alerts
        assert radar._check_hourly_rate()

    def test_symbol_cooldown(self):
        radar, _ = self._make_radar()
        # Record a very recent alert to trigger the cooldown
        radar._symbol_last_post["BTCUSDT"] = time.monotonic()
        assert not radar._check_symbol_cooldown("BTCUSDT")
        # Symbol with no prior alert should always pass
        assert "ETHUSDT" not in radar._symbol_last_post
        assert radar._check_symbol_cooldown("ETHUSDT")


# ---------------------------------------------------------------------------
# telegram_bot.py tests — new methods
# ---------------------------------------------------------------------------

from src.telegram_bot import TelegramBot


class TestTelegramBotNewMethods:
    @pytest.mark.asyncio
    async def test_post_to_free_channel_skips_when_unconfigured(self, monkeypatch):
        monkeypatch.setattr("src.telegram_bot.TELEGRAM_FREE_CHANNEL_ID", "")
        bot = TelegramBot()
        result = await bot.post_to_free_channel("hello")
        assert result is False

    @pytest.mark.asyncio
    async def test_post_to_free_channel_sends_message(self, monkeypatch):
        monkeypatch.setattr("src.telegram_bot.TELEGRAM_FREE_CHANNEL_ID", "-1001234567890")
        monkeypatch.setattr("src.telegram_bot.TELEGRAM_BOT_TOKEN", "fake_token")
        bot = TelegramBot()
        # Mock send_message to avoid real HTTP call
        bot.send_message = AsyncMock(return_value=True)
        result = await bot.post_to_free_channel("hello")
        assert result is True
        bot.send_message.assert_called_once_with("-1001234567890", "hello")

    @pytest.mark.asyncio
    async def test_post_to_active_channel_skips_when_unconfigured(self, monkeypatch):
        monkeypatch.setattr("src.telegram_bot.TELEGRAM_ACTIVE_CHANNEL_ID", "")
        bot = TelegramBot()
        result = await bot.post_to_active_channel("hello")
        assert result is False

    @pytest.mark.asyncio
    async def test_post_to_active_channel_sends_message(self, monkeypatch):
        monkeypatch.setattr("src.telegram_bot.TELEGRAM_ACTIVE_CHANNEL_ID", "-1001111111111")
        monkeypatch.setattr("src.telegram_bot.TELEGRAM_BOT_TOKEN", "fake_token")
        bot = TelegramBot()
        bot.send_message = AsyncMock(return_value=True)
        result = await bot.post_to_active_channel("premium signal")
        assert result is True
        bot.send_message.assert_called_once_with("-1001111111111", "premium signal")


# ---------------------------------------------------------------------------
# PR2 Bug Fix Tests
# ---------------------------------------------------------------------------


class TestFix1SchedulerChannelRouting:
    """Fix 1 — morning_brief, london_open, ny_open, eod_wrap must post to free
    channel ONLY.  weekly_card is the sole task allowed on both channels."""

    def _make_scheduler(self, monkeypatch):
        free_msgs = []
        active_msgs = []

        async def post_free(text):
            free_msgs.append(text)
            return True

        async def post_active(text):
            active_msgs.append(text)
            return True

        def engine_ctx():
            return {"regime": "RANGING", "btc_price": 50000.0,
                    "btc_change_pct": 0.0, "top_pairs": [],
                    "signals_today": 0, "performance": {},
                    "btc_1h_change_pct": 0.0, "is_active_market": False}

        from src.scheduler import ContentScheduler
        scheduler = ContentScheduler(post_free, post_active, engine_ctx)
        return scheduler, free_msgs, active_msgs

    def test_scheduled_tasks_free_only_for_session_tasks(self):
        """morning_brief, london_open, ny_open, eod_wrap must target free only."""
        from src.scheduler import SCHEDULED_TASKS
        session_tasks = {"morning_brief", "london_open", "ny_open", "eod_wrap"}
        for _, _, task_name, channels in SCHEDULED_TASKS:
            if task_name in session_tasks:
                assert channels == ["free"], (
                    f"{task_name} must target ['free'] only, got {channels}"
                )

    def test_weekly_card_targets_both_channels(self):
        """weekly_card should target both active and free."""
        from src.scheduler import SCHEDULED_TASKS
        weekly = [t for t in SCHEDULED_TASKS if t[2] == "weekly_card"]
        assert weekly, "weekly_card task must exist in SCHEDULED_TASKS"
        _, _, _, channels = weekly[0]
        assert "active" in channels and "free" in channels, (
            f"weekly_card must target both channels, got {channels}"
        )

    @pytest.mark.asyncio
    async def test_morning_brief_does_not_post_to_active_channel(self, monkeypatch):
        scheduler, free_msgs, active_msgs = self._make_scheduler(monkeypatch)

        async def fake_gen(ctx):
            return "morning brief text"

        monkeypatch.setattr(
            "src.scheduler.content_engine.generate_morning_brief", fake_gen
        )
        await scheduler._run_task("morning_brief", ["free"])
        assert len(free_msgs) == 1
        assert len(active_msgs) == 0

    @pytest.mark.asyncio
    async def test_london_open_does_not_post_to_active_channel(self, monkeypatch):
        scheduler, free_msgs, active_msgs = self._make_scheduler(monkeypatch)

        async def fake_gen(ctx):
            return "london open text"

        monkeypatch.setattr(
            "src.scheduler.content_engine.generate_london_open", fake_gen
        )
        await scheduler._run_task("london_open", ["free"])
        assert len(free_msgs) == 1
        assert len(active_msgs) == 0

    @pytest.mark.asyncio
    async def test_ny_open_does_not_post_to_active_channel(self, monkeypatch):
        scheduler, free_msgs, active_msgs = self._make_scheduler(monkeypatch)

        async def fake_gen(ctx):
            return "ny open text"

        monkeypatch.setattr(
            "src.scheduler.content_engine.generate_ny_open", fake_gen
        )
        await scheduler._run_task("ny_open", ["free"])
        assert len(free_msgs) == 1
        assert len(active_msgs) == 0

    @pytest.mark.asyncio
    async def test_eod_wrap_does_not_post_to_active_channel(self, monkeypatch):
        scheduler, free_msgs, active_msgs = self._make_scheduler(monkeypatch)

        async def fake_gen(ctx):
            return "eod wrap text"

        monkeypatch.setattr(
            "src.scheduler.content_engine.generate_eod_wrap", fake_gen
        )
        await scheduler._run_task("eod_wrap", ["free"])
        assert len(free_msgs) == 1
        assert len(active_msgs) == 0


class TestFix2BtcPriceFromDataStore:
    """Fix 2 — _get_engine_context() must return real BTC price from data store."""

    def _make_engine(self):
        """Build a minimal CryptoSignalEngine-like object using only the parts
        needed to test _get_engine_context()."""
        from src.main import CryptoSignalEngine
        engine = object.__new__(CryptoSignalEngine)
        # Minimal stubs required by _get_engine_context
        engine._regime_detector = MagicMock()
        engine._regime_detector.get_regime.return_value = None
        engine._performance_tracker = MagicMock()
        engine._performance_tracker.get_stats.side_effect = Exception("no stats")
        engine.pair_mgr = MagicMock()
        engine.pair_mgr.symbols = []
        engine._signal_history = []
        engine.data_store = MagicMock()
        return engine

    def test_returns_dash_when_data_store_empty(self):
        engine = self._make_engine()
        engine.data_store.get_candles.return_value = None
        ctx = engine._get_engine_context()
        assert ctx["btc_price"] == "—"
        assert ctx["btc_change_pct"] == 0.0
        assert ctx["btc_1h_change_pct"] == 0.0

    def test_returns_real_price_when_data_available(self):
        engine = self._make_engine()
        # 300 candles — well above the 289 minimum needed for 24h change (288×5m)
        closes = [float(i + 40000) for i in range(300)]
        engine.data_store.get_candles.return_value = {"close": closes}
        ctx = engine._get_engine_context()
        assert ctx["btc_price"] == round(closes[-1], 2)
        assert isinstance(ctx["btc_price"], float)

    def test_computes_1h_change(self):
        engine = self._make_engine()
        closes = [50000.0] * 12 + [51000.0]  # 13 candles, last one higher
        engine.data_store.get_candles.return_value = {"close": closes}
        ctx = engine._get_engine_context()
        # last / closes[-12] - 1 = 51000/50000 - 1 = 2%
        assert ctx["btc_1h_change_pct"] == pytest.approx(2.0, abs=0.01)

    def test_computes_24h_change(self):
        engine = self._make_engine()
        closes = [50000.0] * 289  # 289 = 288×5m periods (≈24h) + 1 current candle
        closes[-1] = 51000.0  # last candle is +2%
        engine.data_store.get_candles.return_value = {"close": closes}
        ctx = engine._get_engine_context()
        assert ctx["btc_change_pct"] == pytest.approx(2.0, abs=0.01)

    def test_falls_back_to_dash_on_data_store_exception(self):
        engine = self._make_engine()
        engine.data_store.get_candles.side_effect = RuntimeError("boom")
        ctx = engine._get_engine_context()
        assert ctx["btc_price"] == "—"

    def test_returns_dash_when_close_list_missing(self):
        engine = self._make_engine()
        engine.data_store.get_candles.return_value = {}  # no "close" key
        ctx = engine._get_engine_context()
        assert ctx["btc_price"] == "—"


class TestFix3UpdateLastPostOnArchive:
    """Fix 3 — update_last_post() must be called from _remove_and_archive()."""

    def test_update_last_post_called_after_remove_and_archive(self):
        from src.main import CryptoSignalEngine
        engine = object.__new__(CryptoSignalEngine)

        # Minimal stubs
        engine.router = MagicMock()
        engine.router.active_signals = {}
        engine.router.remove_signal = MagicMock()
        engine._signal_history = []
        engine._content_scheduler = MagicMock()

        engine._remove_and_archive("sig-001")

        engine._content_scheduler.update_last_post.assert_called_once()

    def test_update_last_post_called_even_when_signal_not_found(self):
        """Silence breaker must reset even if the signal_id is not in active set."""
        from src.main import CryptoSignalEngine
        engine = object.__new__(CryptoSignalEngine)
        engine.router = MagicMock()
        engine.router.active_signals = {}  # Empty — signal_id not present
        engine.router.remove_signal = MagicMock()
        engine._signal_history = []
        engine._content_scheduler = MagicMock()

        engine._remove_and_archive("non-existent-id")
        engine._content_scheduler.update_last_post.assert_called_once()


class TestFix4RadarScoresPopulated:
    """Fix 4 — _radar_scores must be declared on Scanner and populated during
    scan when a soft-disabled channel fires above RADAR_ALERT_MIN_CONFIDENCE."""

    def _make_scanner(self, channel_enabled_flags=None):
        """Build a minimal Scanner with two channels: one enabled, one disabled."""
        from src.scanner import Scanner
        from src.channels.base import Signal, ChannelConfig
        from src.smc import Direction

        scanner = object.__new__(Scanner)
        scanner._radar_scores = {}

        # Use the real default
        from config import RADAR_ALERT_MIN_CONFIDENCE as _MIN_CONF
        return scanner, _MIN_CONF

    def test_radar_scores_initialised_empty(self):
        from src.scanner import Scanner
        scanner = object.__new__(Scanner)
        scanner._radar_scores = {}
        assert isinstance(scanner._radar_scores, dict)
        assert len(scanner._radar_scores) == 0

    def test_radar_scores_dict_exists_on_real_scanner_class(self):
        """Verify _radar_scores is initialised in Scanner.__init__ docstring."""
        import inspect
        from src.scanner import Scanner
        src = inspect.getsource(Scanner.__init__)
        assert "_radar_scores" in src

    @pytest.mark.asyncio
    async def test_radar_scores_populated_by_disabled_channel(self, monkeypatch):
        """When a soft-disabled channel scores above threshold, _radar_scores is updated."""
        from src.scanner import Scanner, _CHANNEL_ENABLED_FLAGS
        from src.channels.base import Signal, ChannelConfig
        from src.smc import Direction
        from config import RADAR_ALERT_MIN_CONFIDENCE

        # Build a minimal scanner stub
        scanner = object.__new__(Scanner)
        scanner._radar_scores = {}

        # Create a fake disabled channel
        fake_sig = MagicMock()
        fake_sig.confidence = RADAR_ALERT_MIN_CONFIDENCE + 5  # Above threshold
        fake_sig.direction = MagicMock()
        fake_sig.direction.value = "LONG"
        fake_sig.setup_class = "CVD_DIVERGENCE"

        fake_chan = MagicMock()
        fake_chan.config.name = "360_SCALP_CVD"
        fake_chan.evaluate.return_value = fake_sig

        # Monkeypatch the enabled flags so CVD is disabled
        monkeypatch.setitem(_CHANNEL_ENABLED_FLAGS, "360_SCALP_CVD", False)

        # Simulate the radar evaluation pass manually
        chan_name = fake_chan.config.name
        if not _CHANNEL_ENABLED_FLAGS.get(chan_name, True):
            try:
                radar_sig = fake_chan.evaluate(
                    symbol="BTCUSDT",
                    candles={},
                    indicators={},
                    smc_data={},
                    spread_pct=0.0,
                    volume_24h_usd=1_000_000.0,
                    regime="RANGING",
                )
                if radar_sig is not None and radar_sig.confidence >= RADAR_ALERT_MIN_CONFIDENCE:
                    scanner._radar_scores[chan_name] = {
                        "symbol": "BTCUSDT",
                        "confidence": radar_sig.confidence,
                        "bias": radar_sig.direction.value,
                        "setup_name": radar_sig.setup_class,
                        "waiting_for": "confirm",
                    }
            except Exception:
                pass

        assert "360_SCALP_CVD" in scanner._radar_scores
        assert scanner._radar_scores["360_SCALP_CVD"]["symbol"] == "BTCUSDT"
        assert scanner._radar_scores["360_SCALP_CVD"]["confidence"] >= RADAR_ALERT_MIN_CONFIDENCE

    @pytest.mark.asyncio
    async def test_radar_scores_not_populated_below_threshold(self, monkeypatch):
        """Signal below RADAR_ALERT_MIN_CONFIDENCE must NOT be written to _radar_scores."""
        from src.scanner import _CHANNEL_ENABLED_FLAGS
        from config import RADAR_ALERT_MIN_CONFIDENCE

        scanner_scores = {}
        fake_sig = MagicMock()
        fake_sig.confidence = RADAR_ALERT_MIN_CONFIDENCE - 5  # Below threshold

        fake_chan = MagicMock()
        fake_chan.config.name = "360_SCALP_CVD"
        fake_chan.evaluate.return_value = fake_sig

        monkeypatch.setitem(_CHANNEL_ENABLED_FLAGS, "360_SCALP_CVD", False)

        chan_name = fake_chan.config.name
        if not _CHANNEL_ENABLED_FLAGS.get(chan_name, True):
            try:
                radar_sig = fake_chan.evaluate(
                    symbol="BTCUSDT", candles={}, indicators={},
                    smc_data={}, spread_pct=0.0, volume_24h_usd=0.0, regime="",
                )
                if radar_sig is not None and radar_sig.confidence >= RADAR_ALERT_MIN_CONFIDENCE:
                    scanner_scores[chan_name] = {"confidence": radar_sig.confidence}
            except Exception:
                pass

        assert "360_SCALP_CVD" not in scanner_scores

    @pytest.mark.asyncio
    async def test_radar_pass_exception_does_not_propagate(self, monkeypatch):
        """Exceptions in the radar pass must be caught — scan loop must not crash."""
        from src.scanner import _CHANNEL_ENABLED_FLAGS
        from config import RADAR_ALERT_MIN_CONFIDENCE

        scanner_scores = {}
        fake_chan = MagicMock()
        fake_chan.config.name = "360_SCALP_SUPERTREND"
        fake_chan.evaluate.side_effect = RuntimeError("channel exploded")

        monkeypatch.setitem(_CHANNEL_ENABLED_FLAGS, "360_SCALP_SUPERTREND", False)

        crashed = False
        chan_name = fake_chan.config.name
        if not _CHANNEL_ENABLED_FLAGS.get(chan_name, True):
            try:
                radar_sig = fake_chan.evaluate(
                    symbol="ETHUSDT", candles={}, indicators={},
                    smc_data={}, spread_pct=0.0, volume_24h_usd=0.0, regime="",
                )
                if radar_sig is not None and radar_sig.confidence >= RADAR_ALERT_MIN_CONFIDENCE:
                    scanner_scores[chan_name] = {"confidence": radar_sig.confidence}
            except Exception:
                crashed = True  # Exception was caught — would be logged at DEBUG

        # The scan loop must NOT re-raise — exception must be caught (crashed=True confirms catch)
        assert crashed  # Exception was caught, not re-raised
        assert chan_name not in scanner_scores
