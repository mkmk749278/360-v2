"""The diag channel's BRPOP consumer (2026-11-20).

The writer drained this queue on its ~15s cycle against a 25s API poll, and 2
of 3 analyst MCP calls timed out. The consumer answers on arrival and shares
the writer's handler, so the two cannot drift.
"""
from __future__ import annotations

import asyncio
import inspect
import json
import time

import pytest

from src import diag_consumer
from src.api import snapshot_store as _store


class _FakeRedis:
    def __init__(self, items=()):
        self.list = list(items)
        self.kv: dict[str, str] = {}

    async def brpop(self, _key, timeout=0):
        if self.list:
            return (_key, self.list.pop())
        await asyncio.sleep(0.01)
        return None

    async def set(self, key, val, ex=None):
        self.kv[key] = val


class _Bridge:
    def __init__(self, items=()):
        self.client = _FakeRedis(items)
        self.available = True


def _env(rid, key="read.scan_executor", age=0.0):
    return json.dumps({"request_id": rid, "key": key, "args": {}, "ts": time.time() - age})


async def _run_until_drained(consumer, bridge, n):
    task = asyncio.create_task(consumer.start())
    for _ in range(200):
        if len(bridge.client.kv) >= n:
            break
        await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_a_queued_request_is_answered_without_waiting_for_a_writer_cycle():
    bridge = _Bridge([_env("a1")])
    c = diag_consumer.DiagConsumer(object(), bridge)
    await _run_until_drained(c, bridge, 1)
    out = json.loads(bridge.client.kv[_store.KEY_DIAG_RESULT_PREFIX + "a1"])
    assert out["ok"] is False and out["error"].startswith("unavailable:")
    assert c.served == 1


async def test_stale_and_malformed_envelopes_follow_the_shared_rules():
    bridge = _Bridge(["{not json", _env("old", age=_store.DIAG_CMD_STALE_S + 30)])
    c = diag_consumer.DiagConsumer(object(), bridge)
    await _run_until_drained(c, bridge, 1)
    out = json.loads(bridge.client.kv[_store.KEY_DIAG_RESULT_PREFIX + "old"])
    assert "stale" in out["error"]


def test_writer_and_consumer_share_one_handler():
    from src.api.snapshot_writer import SnapshotWriter
    src = inspect.getsource(SnapshotWriter._apply_pending_diag_cmds)
    assert "handle_envelope" in src and "diag_catalog.run" not in src


def test_consumer_is_started_in_isolated_mode_behind_its_switch():
    from config import DIAG_CONSUMER_ENABLED
    from src import bootstrap
    src = inspect.getsource(bootstrap)
    assert "DiagConsumer(engine, engine._redis_client).start()" in src
    assert DIAG_CONSUMER_ENABLED is True
