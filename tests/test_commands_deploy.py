"""Tests for the /deploy, /restart and /rollback operator commands.

These shell out to git on the production VPS, so the properties that
matter are guard-rails, not git itself:

* /rollback validates the commit ref against a strict pattern before it
  ever reaches ``subprocess`` — a ref like ``;rm -rf`` or a leading-dash
  option must be rejected (the ref is passed as an argv element, but the
  validation also stops ``git checkout --force``-style option smuggling);
* subprocess timeouts and unexpected exceptions surface in the reply
  instead of raising into the dispatcher;
* /restart uses the configured callback and degrades to a clear message
  when none is wired.

``subprocess.run`` is always patched — no real git commands execute.
"""

from __future__ import annotations

import subprocess
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.commands.deploy import (
    handle_deploy,
    handle_restart,
    handle_rollback,
)
from src.commands.registry import CommandContext


def _ctx(**overrides) -> CommandContext:
    telegram = MagicMock()
    telegram.send_message = AsyncMock()
    defaults = dict(
        chat_id="710718010",
        is_admin=True,
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
    defaults.update(overrides)
    return CommandContext(**defaults)


def _replies(ctx: CommandContext) -> str:
    return "\n".join(
        call.args[1] for call in ctx.telegram.send_message.call_args_list
    )


def _completed(stdout: str = "", stderr: str = "") -> MagicMock:
    result = MagicMock()
    result.stdout = stdout
    result.stderr = stderr
    return result


class TestDeploy:
    async def test_runs_git_pull_and_relays_output(self):
        ctx = _ctx()
        with patch(
            "src.commands.deploy.subprocess.run",
            return_value=_completed(stdout="Already up to date.\n"),
        ) as run:
            await handle_deploy([], ctx)
        assert run.call_args.args[0] == ["git", "pull"]
        assert "Already up to date." in _replies(ctx)

    async def test_timeout_is_reported(self):
        ctx = _ctx()
        with patch(
            "src.commands.deploy.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="git pull", timeout=30),
        ):
            await handle_deploy([], ctx)
        assert "timed out" in _replies(ctx)

    async def test_unexpected_error_is_reported_not_raised(self):
        ctx = _ctx()
        with patch(
            "src.commands.deploy.subprocess.run",
            side_effect=OSError("git binary missing"),
        ):
            await handle_deploy([], ctx)
        assert "error" in _replies(ctx).lower()


class TestRestart:
    async def test_invokes_configured_callback_with_chat_id(self):
        restart = AsyncMock()
        ctx = _ctx(restart_callback=restart)
        await handle_restart([], ctx)
        restart.assert_awaited_once_with(ctx.chat_id)

    async def test_missing_callback_reports_not_configured(self):
        ctx = _ctx(restart_callback=None)
        await handle_restart([], ctx)
        assert "not configured" in _replies(ctx)

    async def test_callback_failure_is_reported(self):
        restart = AsyncMock(side_effect=RuntimeError("supervisor gone"))
        ctx = _ctx(restart_callback=restart)
        await handle_restart([], ctx)
        assert "Restart error" in _replies(ctx)


class TestRollback:
    async def test_no_args_prints_usage(self):
        ctx = _ctx()
        with patch("src.commands.deploy.subprocess.run") as run:
            await handle_rollback([], ctx)
        run.assert_not_called()
        assert "Usage:" in _replies(ctx)

    @pytest.mark.parametrize(
        "bad_ref",
        [
            "; rm -rf /",          # shell metacharacters
            "$(reboot)",           # command substitution
            "-f",                  # leading dash — option smuggling
            "--force",
            "a" * 81,              # over-length
            "ref with spaces",
        ],
    )
    async def test_invalid_refs_rejected_before_subprocess(self, bad_ref):
        ctx = _ctx()
        with patch("src.commands.deploy.subprocess.run") as run:
            await handle_rollback([bad_ref], ctx)
        run.assert_not_called()
        assert "Invalid commit reference" in _replies(ctx)

    @pytest.mark.parametrize("ref", ["abc1234", "v1.2.3", "main", "HEAD"])
    async def test_valid_refs_run_git_checkout(self, ref):
        ctx = _ctx()
        with patch(
            "src.commands.deploy.subprocess.run",
            return_value=_completed(stdout="HEAD is now at abc1234"),
        ) as run:
            await handle_rollback([ref], ctx)
        assert run.call_args.args[0] == ["git", "checkout", ref]
        assert "Rollback result" in _replies(ctx)

    async def test_timeout_is_reported(self):
        ctx = _ctx()
        with patch(
            "src.commands.deploy.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="git checkout", timeout=30),
        ):
            await handle_rollback(["abc1234"], ctx)
        assert "timed out" in _replies(ctx)
