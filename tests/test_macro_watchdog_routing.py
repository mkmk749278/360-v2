"""Tests for src/macro_watchdog.py — verifies the broadcast routing rules.

Phase 1 free-channel content rollout: HIGH/CRITICAL severity macro events
must broadcast to BOTH admin and free channels.  MEDIUM/LOW severity
events stay admin-only (operational signal, not subscriber content).
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from src.macro_watchdog import MacroWatchdog, _FREE_CHANNEL_SEVERITIES


def _make_watchdog(send_alert=None, send_to_free=None) -> MacroWatchdog:
    """Build a watchdog with mocked alert callables — no I/O performed."""
    return MacroWatchdog(
        send_alert=send_alert or AsyncMock(return_value=True),
        send_to_free=send_to_free,
    )


# ---------------------------------------------------------------------------
# Severity routing matrix
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("severity", ["HIGH", "CRITICAL"])
async def test_high_critical_severity_broadcasts_to_both_channels(severity):
    admin = AsyncMock(return_value=True)
    free = AsyncMock(return_value=True)
    watchdog = _make_watchdog(send_alert=admin, send_to_free=free)

    await watchdog._broadcast("test msg", severity)

    admin.assert_awaited_once_with("test msg")
    free.assert_awaited_once_with("test msg")


@pytest.mark.parametrize("severity", ["LOW", "MEDIUM"])
async def test_low_medium_severity_admin_only(severity):
    admin = AsyncMock(return_value=True)
    free = AsyncMock(return_value=True)
    watchdog = _make_watchdog(send_alert=admin, send_to_free=free)

    await watchdog._broadcast("test msg", severity)

    admin.assert_awaited_once_with("test msg")
    free.assert_not_awaited()


async def test_unknown_severity_admin_only():
    """Defensive: unrecognised severity tokens (typos, future values) default
    to admin-only routing — never accidentally leak to subscribers."""
    admin = AsyncMock(return_value=True)
    free = AsyncMock(return_value=True)
    watchdog = _make_watchdog(send_alert=admin, send_to_free=free)

    await watchdog._broadcast("test msg", "UNKNOWN_SEVERITY")

    admin.assert_awaited_once()
    free.assert_not_awaited()


# ---------------------------------------------------------------------------
# Backwards compatibility — no `send_to_free` provided
# ---------------------------------------------------------------------------


async def test_no_free_callable_admin_only_for_all_severities():
    """When `send_to_free=None` (legacy admin-only construction), every
    severity routes to admin only.  This preserves the original watchdog
    behaviour for any caller that hasn't migrated yet."""
    admin = AsyncMock(return_value=True)
    watchdog = _make_watchdog(send_alert=admin, send_to_free=None)

    for severity in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        admin.reset_mock()
        await watchdog._broadcast(f"msg-{severity}", severity)
        admin.assert_awaited_once_with(f"msg-{severity}")


# ---------------------------------------------------------------------------
# Resilience — free-channel post failure must not silence admin alerts
# ---------------------------------------------------------------------------


async def test_free_channel_failure_logged_but_not_raised():
    """If the free-channel post raises, the admin alert has already been sent
    and the exception must NOT propagate (would silence future polls in the
    same cycle).  Subsequent broadcasts must still work."""
    admin = AsyncMock(return_value=True)
    free = AsyncMock(side_effect=RuntimeError("free-channel network error"))
    watchdog = _make_watchdog(send_alert=admin, send_to_free=free)

    # First call: free fails, admin succeeded — no exception bubbles
    await watchdog._broadcast("first", "HIGH")
    admin.assert_awaited_once_with("first")
    free.assert_awaited_once_with("first")

    # Second call: still works
    free.side_effect = None
    free.return_value = True
    await watchdog._broadcast("second", "HIGH")
    assert admin.await_count == 2
    assert free.await_count == 2


async def test_admin_failure_propagates():
    """If admin post fails, the exception SHOULD propagate — admin alerts are
    operational and we want to surface infrastructure issues rather than
    silently swallow them."""
    admin = AsyncMock(side_effect=RuntimeError("admin telegram error"))
    free = AsyncMock(return_value=True)
    watchdog = _make_watchdog(send_alert=admin, send_to_free=free)

    with pytest.raises(RuntimeError, match="admin telegram error"):
        await watchdog._broadcast("test", "HIGH")

    # Free-channel post should not have been attempted (admin failed first)
    free.assert_not_awaited()


# ---------------------------------------------------------------------------
# Doctrine constants
# ---------------------------------------------------------------------------


def test_free_channel_severities_are_only_high_and_critical():
    """The doctrine: HIGH/CRITICAL are subscriber content, lower severities
    are not.  Lock this in so future edits don't accidentally widen the
    subscriber-facing severity set without explicit owner discussion."""
    assert _FREE_CHANNEL_SEVERITIES == frozenset({"HIGH", "CRITICAL"})
