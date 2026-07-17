"""Tests for the /auto_trade_global operator command.

This command is the Telegram-surface flip for
``auto_trade_globally_enabled`` — the Firestore flag the FSM gates every
order on.  It touches money controls, yet had no direct tests: a
regression that silently swapped enable/disable, or that flipped the
flag when the kill-switch client isn't initialised, would only surface
in an incident.  Pinned here:

* uninitialised kill switch → clear refusal, no client access;
* no-arg read path reports both the enable flag and kill-switch state;
* on/off (and their aliases) call exactly the matching client method;
* client failures surface in the reply instead of raising into the
  dispatcher;
* unknown argument → usage text, no flip;
* the registry's admin guard blocks non-admin chats before the handler
  ever runs.

All Firestore access is mocked at the ``kill_switch`` module seam — no
GCP, no network.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.commands.auto_trade_admin import handle_auto_trade_global, registry
from src.commands.registry import CommandContext
from src.execution import kill_switch as ks


def _ctx(is_admin: bool = True) -> CommandContext:
    telegram = MagicMock()
    telegram.send_message = AsyncMock()
    return CommandContext(
        chat_id="710718010",
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
    )


def _replies(ctx: CommandContext) -> str:
    return "\n".join(
        call.args[1] for call in ctx.telegram.send_message.call_args_list
    )


@pytest.fixture
def ks_client(monkeypatch):
    client = MagicMock()
    client.is_globally_enabled.return_value = True
    client.is_global_engaged.return_value = False
    monkeypatch.setattr(ks, "is_initialised", lambda: True)
    monkeypatch.setattr(ks, "get_client", lambda: client)
    return client


class TestUninitialised:
    async def test_refuses_without_kill_switch(self, monkeypatch):
        monkeypatch.setattr(ks, "is_initialised", lambda: False)
        get_client = MagicMock()
        monkeypatch.setattr(ks, "get_client", get_client)
        ctx = _ctx()
        await handle_auto_trade_global(["on"], ctx)
        assert "not initialised" in _replies(ctx)
        # Never even fetches a client — no flip can happen.
        get_client.assert_not_called()


class TestReadPath:
    async def test_reports_enabled_state(self, ks_client):
        ctx = _ctx()
        await handle_auto_trade_global([], ctx)
        out = _replies(ctx)
        assert "ENABLED" in out
        assert "Kill switch: off" in out

    async def test_reports_disabled_and_engaged(self, ks_client):
        ks_client.is_globally_enabled.return_value = False
        ks_client.is_global_engaged.return_value = True
        ctx = _ctx()
        await handle_auto_trade_global([], ctx)
        out = _replies(ctx)
        assert "DISABLED" in out
        assert "ENGAGED" in out

    async def test_read_failure_is_reported_not_raised(self, ks_client):
        ks_client.is_globally_enabled.side_effect = RuntimeError("firestore down")
        ctx = _ctx()
        await handle_auto_trade_global([], ctx)
        assert "Read failed" in _replies(ctx)


class TestFlipPath:
    @pytest.mark.parametrize("arg", ["on", "enable", "ENABLED", "true"])
    async def test_on_aliases_enable(self, ks_client, arg):
        ctx = _ctx()
        await handle_auto_trade_global([arg], ctx)
        ks_client.enable_global_auto_trade.assert_called_once()
        ks_client.disable_global_auto_trade.assert_not_called()
        assert "ENABLED" in _replies(ctx)

    @pytest.mark.parametrize("arg", ["off", "disable", "DISABLED", "false"])
    async def test_off_aliases_disable(self, ks_client, arg):
        ctx = _ctx()
        await handle_auto_trade_global([arg], ctx)
        ks_client.disable_global_auto_trade.assert_called_once()
        ks_client.enable_global_auto_trade.assert_not_called()
        out = _replies(ctx)
        assert "DISABLED" in out
        # The reply must warn that existing Binance positions stay open.
        assert "NOT cancelled" in out

    async def test_enable_failure_reported(self, ks_client):
        ks_client.enable_global_auto_trade.side_effect = RuntimeError("boom")
        ctx = _ctx()
        await handle_auto_trade_global(["on"], ctx)
        assert "Enable failed" in _replies(ctx)

    async def test_disable_failure_reported(self, ks_client):
        ks_client.disable_global_auto_trade.side_effect = RuntimeError("boom")
        ctx = _ctx()
        await handle_auto_trade_global(["off"], ctx)
        assert "Disable failed" in _replies(ctx)

    async def test_unknown_arg_prints_usage_and_flips_nothing(self, ks_client):
        ctx = _ctx()
        await handle_auto_trade_global(["maybe"], ctx)
        assert "Usage:" in _replies(ctx)
        ks_client.enable_global_auto_trade.assert_not_called()
        ks_client.disable_global_auto_trade.assert_not_called()


class TestAdminGuard:
    async def test_non_admin_dispatch_never_reaches_handler(self, ks_client):
        ctx = _ctx(is_admin=False)
        await registry.dispatch("/auto_trade_global", ["off"], ctx)
        # Guard fires before the handler: no flip, and the reply is the
        # restriction message rather than the DISABLED confirmation.
        ks_client.disable_global_auto_trade.assert_not_called()
        assert "DISABLED" not in _replies(ctx)
