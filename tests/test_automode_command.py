"""Tests for the /automode runtime control flow.

Covers the command handler (`/automode`) plus the message-formatting
helper.  The engine-side ``set_auto_execution_mode`` method itself is
exercised end-to-end via integration with the command — direct unit
tests of the engine method live in ``test_main_auto_mode.py`` (kept
separate to avoid pulling the full Telegram fixture set into engine
tests).
"""
from __future__ import annotations

from typing import List
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.commands.engine import _format_auto_status, handle_automode
from src.commands.registry import CommandContext


def _make_ctx(
    *,
    set_fn=None,
    get_fn=None,
    chat_id: str = "admin",
    is_admin: bool = True,
):
    """Minimal CommandContext for handle_automode tests."""
    telegram = MagicMock()
    telegram.send_message = AsyncMock()
    ctx = CommandContext(
        chat_id=chat_id,
        is_admin=is_admin,
        telegram=telegram,
        router=MagicMock(),
        scanner=MagicMock(),
        pair_mgr=MagicMock(),
        data_store=MagicMock(),
        signal_queue=MagicMock(),
        telemetry=MagicMock(),
        signal_history=[],
        paused_channels=set(),
        confidence_overrides={},
        tasks=[],
        boot_time=0.0,
        set_auto_execution_mode_fn=set_fn,
        get_auto_execution_status_fn=get_fn,
    )
    return ctx, telegram


# ---------------------------------------------------------------------------
# _format_auto_status
# ---------------------------------------------------------------------------


def test_format_status_off_shows_neutral_emoji():
    msg = _format_auto_status({"mode": "off", "open_positions": 0})
    assert "⚪" in msg
    assert "OFF" in msg


def test_format_status_paper_includes_simulated_pnl():
    msg = _format_auto_status({
        "mode": "paper",
        "open_positions": 2,
        "daily_pnl_usd": 12.5,
        "daily_loss_pct": 1.25,
        "current_equity_usd": 1012.5,
        "simulated_pnl_usd": 12.5,
    })
    assert "🧪" in msg
    assert "PAPER" in msg
    assert "Open positions:    2" in msg
    assert "Paper session PnL: $+12.5000" in msg


def test_format_status_live_with_kill_switch_warns():
    msg = _format_auto_status({
        "mode": "live",
        "open_positions": 0,
        "daily_pnl_usd": -35.0,
        "daily_loss_pct": -3.5,
        "current_equity_usd": 965.0,
        "daily_kill_tripped": True,
    })
    assert "🔴" in msg
    assert "Daily-loss kill TRIPPED" in msg


def test_format_status_manual_pause_warns():
    msg = _format_auto_status({
        "mode": "paper",
        "manual_paused": True,
    })
    assert "Manual pause active" in msg


# ---------------------------------------------------------------------------
# /automode handler — show + change paths
# ---------------------------------------------------------------------------


async def test_automode_no_args_shows_status():
    get_fn = MagicMock(return_value={"mode": "paper", "open_positions": 0})
    set_fn = MagicMock()
    ctx, telegram = _make_ctx(set_fn=set_fn, get_fn=get_fn)
    await handle_automode([], ctx)
    get_fn.assert_called_once()
    set_fn.assert_not_called()
    telegram.send_message.assert_awaited_once()
    msg = telegram.send_message.call_args.args[1]
    assert "PAPER" in msg


async def test_automode_invalid_mode_rejected():
    set_fn = MagicMock()
    get_fn = MagicMock(return_value={"mode": "off"})
    ctx, telegram = _make_ctx(set_fn=set_fn, get_fn=get_fn)
    await handle_automode(["invalid"], ctx)
    set_fn.assert_not_called()
    msg = telegram.send_message.call_args.args[1]
    assert "Mode must be one of" in msg


async def test_automode_change_to_paper_calls_set_fn():
    set_fn = MagicMock(return_value=(True, "OFF → PAPER"))
    get_fn = MagicMock(return_value={"mode": "paper"})
    ctx, telegram = _make_ctx(set_fn=set_fn, get_fn=get_fn)
    await handle_automode(["paper"], ctx)
    set_fn.assert_called_once_with("paper")
    msg = telegram.send_message.call_args.args[1]
    assert "OFF → PAPER" in msg
    assert "✅" in msg


async def test_automode_change_to_off_calls_set_fn():
    set_fn = MagicMock(return_value=(True, "PAPER → OFF"))
    get_fn = MagicMock(return_value={"mode": "off"})
    ctx, telegram = _make_ctx(set_fn=set_fn, get_fn=get_fn)
    await handle_automode(["off"], ctx)
    set_fn.assert_called_once_with("off")


async def test_automode_change_failure_surfaces_message():
    """Engine-side rejection (e.g. open positions) flows through cleanly."""
    set_fn = MagicMock(return_value=(False, "refused: 2 open position(s) — close them first"))
    get_fn = MagicMock(return_value={"mode": "paper"})
    ctx, telegram = _make_ctx(set_fn=set_fn, get_fn=get_fn)
    await handle_automode(["off"], ctx)
    msg = telegram.send_message.call_args.args[1]
    assert "❌" in msg
    assert "refused" in msg
    assert "open position" in msg


# ---------------------------------------------------------------------------
# Live-mode confirmation guard — extra friction before real money
# ---------------------------------------------------------------------------


async def test_automode_live_without_confirm_rejected():
    """`/automode live` alone must NOT flip to live — owner must type
    `/automode live confirm` to proceed."""
    set_fn = MagicMock()
    get_fn = MagicMock(return_value={"mode": "paper"})
    ctx, telegram = _make_ctx(set_fn=set_fn, get_fn=get_fn)
    await handle_automode(["live"], ctx)
    set_fn.assert_not_called()
    msg = telegram.send_message.call_args.args[1]
    assert "Live-mode confirmation required" in msg
    assert "/automode live confirm" in msg


async def test_automode_live_with_confirm_calls_set_fn():
    set_fn = MagicMock(return_value=(True, "PAPER → LIVE"))
    get_fn = MagicMock(return_value={"mode": "live"})
    ctx, telegram = _make_ctx(set_fn=set_fn, get_fn=get_fn)
    await handle_automode(["live", "confirm"], ctx)
    set_fn.assert_called_once_with("live")


# ---------------------------------------------------------------------------
# Resilience
# ---------------------------------------------------------------------------


async def test_automode_no_callbacks_wired_replies_gracefully():
    """If the engine instance didn't wire the callbacks (e.g. tests),
    the command should reply with a clear message rather than crash."""
    ctx, telegram = _make_ctx(set_fn=None, get_fn=None)
    await handle_automode([], ctx)
    msg = telegram.send_message.call_args.args[1]
    assert "not wired" in msg


async def test_automode_get_fn_exception_surfaces_error():
    get_fn = MagicMock(side_effect=RuntimeError("redis down"))
    set_fn = MagicMock()
    ctx, telegram = _make_ctx(set_fn=set_fn, get_fn=get_fn)
    await handle_automode([], ctx)
    msg = telegram.send_message.call_args.args[1]
    assert "Failed" in msg
    assert "redis down" in msg


async def test_automode_set_fn_exception_surfaces_error():
    set_fn = MagicMock(side_effect=RuntimeError("teardown failed"))
    get_fn = MagicMock(return_value={"mode": "off"})
    ctx, telegram = _make_ctx(set_fn=set_fn, get_fn=get_fn)
    await handle_automode(["paper"], ctx)
    msg = telegram.send_message.call_args.args[1]
    assert "failed" in msg.lower()
    assert "teardown failed" in msg
