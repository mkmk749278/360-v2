"""Diagnostic-catalog channel consumer — BRPOP, not the writer's cycle (2026-11-20).

The diag channel (``snapshot:cmd:diag``) was drained only inside
``SnapshotWriter``'s loop, which runs every ~15s and longer when a cycle
overruns. The API side polls for the answer for ``DIAG_POLL_TIMEOUT_SEC``
(25s), so a slow writer cycle made a call time out with "the engine did not
answer". On 2026-11-20 that was **2 of 3 calls** through the analyst's MCP
tools, the surface the hourly analyst depends on. CLAUDE.md had named the
fix and left it unbuilt: drain the queue on its own BRPOP task, as the kill
switch (``safety_switch_bridge``) and the manual-take queue already do.

This is that task. A blocked BRPOP costs nothing while idle. It runs the
**same** handler the writer uses (:func:`handle_envelope`), so the stale-request
refusal, the catalog's allow-list and the result TTL are identical whichever
consumer pops a request. The writer's bounded drain stays as a fallback: if
this task ever dies, requests are still served, just at the old latency.
Both consumers pop atomically, so no request runs twice.

What may run is decided by ``src/diag_catalog.py`` alone. This module chooses
nothing, and action entries still obey ``DIAG_ACTIONS_ENABLED``.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any

from src.api import snapshot_store as _store
from src.utils import get_logger

log = get_logger("diag_consumer")

_BRPOP_TIMEOUT_S = 5
_ERROR_BACKOFF_S = 3.0


async def handle_envelope(raw: Any, engine: Any, redis_client: Any) -> bool:
    """Run one queued diag request and publish its result. True if published.

    Shared by this consumer and ``SnapshotWriter._apply_pending_diag_cmds``,
    so the two drains cannot drift apart.
    """
    from src import diag_catalog

    try:
        env = json.loads(raw)
        req_id = str(env.get("request_id") or "")
        key = str(env.get("key") or "")
        args = env.get("args") if isinstance(env.get("args"), dict) else {}
        queued_at = float(env.get("ts") or 0.0)
    except Exception:
        log.warning("diag: unparseable envelope, dropped")
        return False
    if not req_id:
        return False
    # A stale envelope is one the caller stopped waiting for: running it spends
    # engine time on an answer nobody will read, and for an action it applies a
    # change whose requester is long gone.
    if queued_at and (time.time() - queued_at) > _store.DIAG_CMD_STALE_S:
        out = {"ok": False, "key": key, "error": "stale request — not run"}
    else:
        out = await diag_catalog.run_async(key, engine, args)
    try:
        await redis_client.client.set(
            _store.KEY_DIAG_RESULT_PREFIX + req_id,
            json.dumps(out, default=str),
            ex=_store.TTL_DIAG_RESULT,
        )
        return True
    except Exception:
        log.exception("diag: could not publish result")
        return False


class DiagConsumer:
    """Blocks on ``snapshot:cmd:diag`` and answers each request immediately."""

    def __init__(self, engine: Any, redis_client: Any) -> None:
        self._engine = engine
        self._redis = redis_client
        self.served = 0
        self.errors = 0

    async def start(self) -> None:
        log.info("DiagConsumer started — draining {} (brpop {}s)",
                 _store.KEY_CMD_DIAG, _BRPOP_TIMEOUT_S)
        while True:
            try:
                if not self._redis.available:
                    await asyncio.sleep(_ERROR_BACKOFF_S)
                    continue
                item = await self._redis.client.brpop(
                    _store.KEY_CMD_DIAG, timeout=_BRPOP_TIMEOUT_S)
                if item is None:
                    continue
                _key, raw = item
                if await handle_envelope(raw, self._engine, self._redis):
                    self.served += 1
            except asyncio.CancelledError:
                log.info("DiagConsumer stopped")
                raise
            except Exception as exc:  # noqa: BLE001 — the consumer must survive
                self.errors += 1
                from src import fail_open
                fail_open.record("diag_consumer.cycle", exc)
                await asyncio.sleep(_ERROR_BACKOFF_S)
