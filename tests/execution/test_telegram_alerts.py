"""Tests for src.execution.telegram_alerts.

The TelegramBot is mocked.  What we pin:

* Each ``alert_*`` verb calls ``send_admin_alert`` with the expected
  format (uid, reason, counts included for operator triage).
* Without init, alerts silently no-op + log at warn level —
  production behaviour when Telegram is offline.
* Send failures are caught + logged — alert dispatch never raises
  out into the caller.
* Init is idempotent (second call doesn't overwrite the bot).
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.execution import telegram_alerts


@pytest.fixture(autouse=True)
def _reset_module():
    telegram_alerts.reset_for_test()
    yield
    telegram_alerts.reset_for_test()


def _make_bot() -> MagicMock:
    """Fake TelegramBot with an AsyncMock send_admin_alert."""
    bot = MagicMock()
    bot.send_admin_alert = AsyncMock(return_value=True)
    return bot


# ---------------------------------------------------------------------------
# Init lifecycle
# ---------------------------------------------------------------------------


def test_is_initialised_false_before_init() -> None:
    assert telegram_alerts.is_initialised() is False


def test_init_then_is_initialised_true() -> None:
    telegram_alerts.init_telegram_alerts(_make_bot())
    assert telegram_alerts.is_initialised() is True


def test_init_idempotent_second_call_no_op() -> None:
    """Second init keeps the original bot — second registration
    must NOT replace the first (would lose any cached state)."""
    bot1 = _make_bot()
    bot2 = _make_bot()
    telegram_alerts.init_telegram_alerts(bot1)
    telegram_alerts.init_telegram_alerts(bot2)
    assert telegram_alerts._bot is bot1


# ---------------------------------------------------------------------------
# Alert verbs — without init = no-op (log only)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_alert_without_init_silently_logs() -> None:
    """Production: if Telegram isn't wired (boot failed, no
    TELEGRAM_BOT_TOKEN, etc.) the alert verbs MUST NOT raise.  Falls
    back to log-only so the operator still has a record in
    journalctl."""
    # No init — no bot.
    await telegram_alerts.alert_user_disabled(
        firebase_uid="fb-x", reason="test", rejection_count=3
    )
    await telegram_alerts.alert_global_breaker_tripped(
        rejection_count=10, window_s=60.0
    )
    await telegram_alerts.alert_kill_switch_engaged(reason="manual")
    await telegram_alerts.alert_symbol_not_allowed(
        firebase_uid="fb-x", symbol="DOGEUSDT"
    )
    await telegram_alerts.alert_binance_rejection(
        firebase_uid="fb-x", signal_id="sig-1", code="-2010", message="x"
    )
    # No exception = pass.


# ---------------------------------------------------------------------------
# Alert verbs — with init, content + dispatch
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_user_disabled_alert_includes_uid_and_count() -> None:
    bot = _make_bot()
    telegram_alerts.init_telegram_alerts(bot)
    await telegram_alerts.alert_user_disabled(
        firebase_uid="fb-x", reason="circuit breaker", rejection_count=5
    )
    bot.send_admin_alert.assert_called_once()
    text = bot.send_admin_alert.call_args.args[0]
    assert "fb-x" in text
    assert "5" in text
    assert "circuit breaker" in text
    assert "Per-user circuit breaker tripped" in text


@pytest.mark.asyncio
async def test_global_breaker_alert_includes_count_and_window() -> None:
    bot = _make_bot()
    telegram_alerts.init_telegram_alerts(bot)
    await telegram_alerts.alert_global_breaker_tripped(
        rejection_count=10, window_s=60.0
    )
    text = bot.send_admin_alert.call_args.args[0]
    assert "10" in text
    assert "60" in text
    assert "HALTED" in text


@pytest.mark.asyncio
async def test_kill_switch_alert_includes_reason() -> None:
    bot = _make_bot()
    telegram_alerts.init_telegram_alerts(bot)
    await telegram_alerts.alert_kill_switch_engaged(reason="operator panic")
    text = bot.send_admin_alert.call_args.args[0]
    assert "operator panic" in text
    assert "Kill switch ENGAGED" in text


@pytest.mark.asyncio
async def test_kill_switch_alert_handles_empty_reason() -> None:
    bot = _make_bot()
    telegram_alerts.init_telegram_alerts(bot)
    await telegram_alerts.alert_kill_switch_engaged(reason="")
    text = bot.send_admin_alert.call_args.args[0]
    # No exception + the placeholder for missing reason appears.
    assert "none provided" in text


@pytest.mark.asyncio
async def test_symbol_not_allowed_alert_includes_breach_keyword() -> None:
    """The strongest tripwire — the alert text must include the
    word 'breach' or equivalent so the operator's triage path is
    obvious in a stream of Telegram messages."""
    bot = _make_bot()
    telegram_alerts.init_telegram_alerts(bot)
    await telegram_alerts.alert_symbol_not_allowed(
        firebase_uid="fb-x", symbol="HACKUSDT"
    )
    text = bot.send_admin_alert.call_args.args[0]
    assert "HACKUSDT" in text
    assert "ALLOWLIST" in text or "breach" in text.lower()


@pytest.mark.asyncio
async def test_binance_rejection_alert_includes_code_and_message() -> None:
    bot = _make_bot()
    telegram_alerts.init_telegram_alerts(bot)
    await telegram_alerts.alert_binance_rejection(
        firebase_uid="fb-x",
        signal_id="sig-1",
        code="-2010",
        message="insufficient margin",
    )
    text = bot.send_admin_alert.call_args.args[0]
    assert "-2010" in text
    assert "insufficient margin" in text
    assert "sig-1" in text


# ---------------------------------------------------------------------------
# Send-failure swallowing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_send_failure_does_not_propagate() -> None:
    """If the bot raises during send (Telegram outage, rate-limited,
    etc.), the alert verb must NOT propagate the exception — the
    caller is inside the tripwire dispatch path and a failed alert
    must not crash the loop."""
    bot = MagicMock()
    bot.send_admin_alert = AsyncMock(side_effect=RuntimeError("rate limited"))
    telegram_alerts.init_telegram_alerts(bot)
    # Must not raise.
    await telegram_alerts.alert_kill_switch_engaged(reason="test")
