"""Tests for worker_manager's boot-task dedup (2026-07-16 audit F14).

A startup reconcile slower than the 60s tick used to let the next tick
schedule a SECOND _reconcile_and_start for the same uid → two
PositionWorkers / two user-data streams for one user.  _boot_tasks now
marks uids with an in-flight boot; it also strong-references the task so
it can't be garbage-collected mid-flight.
"""
from __future__ import annotations

import asyncio
from contextlib import ExitStack
from unittest.mock import MagicMock, patch

import pytest

from src.execution import worker_manager


@pytest.fixture(autouse=True)
def _clean_state():
    worker_manager._workers.clear()
    worker_manager._boot_tasks.clear()
    yield
    for t in worker_manager._boot_tasks.values():
        t.cancel()
    worker_manager._workers.clear()
    worker_manager._boot_tasks.clear()


def _patches(uids):
    fk = MagicMock()
    fk.is_initialised.return_value = True
    fk.list_active_uids.return_value = uids
    return [
        patch("src.security.firestore_keystore.is_initialised", fk.is_initialised),
        patch("src.security.firestore_keystore.list_active_uids", fk.list_active_uids),
        patch(
            "src.api.user_overrides.resolve_user_mode_uid",
            lambda uid: "live",
        ),
    ]


@pytest.mark.asyncio
async def test_tick_does_not_double_boot_while_reconcile_in_flight():
    release = asyncio.Event()
    started = 0

    async def _slow_boot(uid):
        nonlocal started
        started += 1
        await release.wait()

    with ExitStack() as stack:
        for p in _patches(["uid-slow"]):
            stack.enter_context(p)
        stack.enter_context(
            patch.object(worker_manager, "_reconcile_and_start", _slow_boot)
        )
        worker_manager._tick()
        await asyncio.sleep(0)  # let the boot task start
        # Second tick fires while the first reconcile is still running —
        # pre-fix this scheduled a second boot for the same uid.
        worker_manager._tick()
        await asyncio.sleep(0)
        assert started == 1
        release.set()
        await asyncio.gather(*worker_manager._boot_tasks.values())
    # Done callback dropped the guard entry.
    assert "uid-slow" not in worker_manager._boot_tasks


@pytest.mark.asyncio
async def test_tick_reboots_after_previous_boot_finished():
    calls = []

    async def _fast_boot(uid):
        calls.append(uid)

    with ExitStack() as stack:
        for p in _patches(["uid-a"]):
            stack.enter_context(p)
        stack.enter_context(
            patch.object(worker_manager, "_reconcile_and_start", _fast_boot)
        )
        worker_manager._tick()
        await asyncio.sleep(0.01)  # boot completes (no worker registered)
        # Worker never landed in _workers (mocked boot) — the next tick
        # must be allowed to retry now that no boot is in flight.
        worker_manager._tick()
        await asyncio.sleep(0.01)
    assert calls == ["uid-a", "uid-a"]
