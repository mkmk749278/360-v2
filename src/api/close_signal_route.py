"""``POST /api/admin/close-signal`` — owner force-close of ONE active signal.

For the "some signals don't close, we need to close them" case: a signal stuck
OPEN that the normal exit path (TP / SL / expiry / pre-TP) never resolved.  The
ops "Close" button calls this; the engine reuses the expiry-close primitives
(realise-or-zero PnL, record outcome, flatten any broker position, drop from the
active book) — no new exit path, no fabricated outcome.

Flow mirrors the manual-take bridge:

    this route ──LPUSH(kind=close)──▶ snapshot:cmd:take ──BRPOP──▶ ManualTakeConsumer
        ▲                                                              │
        └─────── poll snapshot:take_result:<request_id> ◀──────────────┘

Single-process mode calls ``engine.close_signal_admin`` directly.  Owner-gated
(Bearer / Firebase owner tier); the ops dashboard audits every call.
"""
from __future__ import annotations

import asyncio
import uuid
from typing import Any, Callable

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.utils import get_logger

log = get_logger("api.close_signal_route")

_RESULT_POLL_TIMEOUT_S = 8.0
_RESULT_POLL_INTERVAL_S = 0.25


class CloseSignalRequest(BaseModel):
    signal_id: str = Field(min_length=1, max_length=128)


def register(app: FastAPI, *, engine: Any, owner_required: Callable) -> None:
    """Register ``POST /api/admin/close-signal`` on the given app."""

    @app.post(
        "/api/admin/close-signal",
        tags=["admin"],
        dependencies=[Depends(owner_required)],
    )
    async def admin_close_signal(req: CloseSignalRequest) -> dict:
        """Force-close one active signal. Idempotent — a signal already gone
        returns ``closed=False, reason="not_found"`` (the button did its job)."""
        signal_id = req.signal_id.strip()
        is_facade = type(engine).__name__ == "RedisEngineFacade"

        if not is_facade:
            # Single-process mode — the live engine is in-process.
            result = await engine.close_signal_admin(signal_id)
            log.info(
                "close_signal: direct signal_id={} closed={}",
                signal_id, result.get("closed"),
            )
            return result

        # Isolated mode — queue the close for the engine container and poll.
        request_id = uuid.uuid4().hex
        enqueued = await engine.enqueue_close_signal(
            request_id=request_id, signal_id=signal_id,
        )
        if not enqueued:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Engine bridge unavailable — try again in a moment.",
            )
        log.info(
            "close_signal: queued signal_id={} request_id={}",
            signal_id, request_id,
        )
        deadline = asyncio.get_running_loop().time() + _RESULT_POLL_TIMEOUT_S
        while asyncio.get_running_loop().time() < deadline:
            await asyncio.sleep(_RESULT_POLL_INTERVAL_S)
            result = await engine.read_manual_take_result(request_id)
            if result is not None:
                log.info(
                    "close_signal: resolved signal_id={} closed={}",
                    signal_id, result.get("closed"),
                )
                return result

        log.warning(
            "close_signal: poll timeout signal_id={} request_id={}",
            signal_id, request_id,
        )
        return {
            "closed": None,
            "signal_id": signal_id,
            "detail": (
                "The engine is taking longer than usual — refresh the Signals "
                "tab shortly to confirm the close."
            ),
        }
