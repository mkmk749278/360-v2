"""``POST /api/auto-trade/close`` — a user closing their OWN live position.

Owner, 2026-09-01, over the Trade tab beside the Binance app: *"user can close
that trade from our app too without visiting binance to close signals
manually"*.

Until now the app could OPEN a position server-side (``/api/auto-trade/take``)
and could not close one.  Every exit was the engine's: a TP, a stop, an
invalidation, or the reconciler's 2h stale backstop.  A subscriber who wanted
out early had to leave the app, open Binance, find the position and close it
there — and the engine then learned about it a reconciler cycle later, as a
"MANUAL" close it had to infer from a flat positionRisk read.

Scope, and it is deliberate: this closes the CALLER'S POSITION.  The signal
stays in the engine's book and every other subscriber keeps their trade.  The
owner-gated ``/api/admin/close-signal`` beside it is the other thing entirely
— it closes the signal for everyone — and the two are kept apart at the route,
the queue envelope (``kind="close_position"`` vs ``kind="close"``) and the
engine method, because a blast radius that depends on a flag is one somebody
will eventually pass wrong.

Flow (isolated mode, live on the VPS) mirrors the take bridge, because the api
container has no signing socket mounted and therefore cannot place or cancel an
order itself:

    this route ──LPUSH──▶ snapshot:cmd:take ──BRPOP──▶ ManualTakeConsumer
        ▲                                                    │
        └────── poll snapshot:take_result:<request_id> ◀─────┘

Two shape rules it inherits from the take route and one it does not:

* business refusals (nothing open, already closed, Binance said no) answer
  **200** with ``outcome="rejected"`` — they are outcomes, not transport
  errors, and the app renders them in the same card it already has;
* transport refusals (no auth, Redis down) use HTTP status codes;
* and unlike a take there is **no staleness gate on the queued request**.
  Firing a market ENTRY minutes late enters at a price the user never saw;
  closing late still does what they asked, and a request that sat in the queue
  is exactly the case where they most want out.
"""
from __future__ import annotations

import asyncio
import uuid
from typing import Any, Callable, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.utils import get_logger

log = get_logger("api.close_position_route")

#: How long the route waits for the engine's answer before returning 202.
#: Longer than the take's 8s on purpose: a close places a market order AND
#: cancels up to five bracket orders first, so it costs more round trips, and
#: a user watching a spinner over their own money would rather wait than be
#: told to go and look somewhere else.
_RESULT_POLL_TIMEOUT_S = 12.0
_RESULT_POLL_INTERVAL_S = 0.25


class ClosePositionRequest(BaseModel):
    signal_id: str = Field(min_length=1, max_length=128)


def _extract_firebase_uid(identity: Any) -> Optional[str]:
    """Same logic as take_signal_route / auto_trade_status_routes."""
    if identity is None:
        return None
    firebase_uid = getattr(identity, "firebase_uid", None)
    if isinstance(firebase_uid, str) and firebase_uid:
        return firebase_uid
    return None


def register(
    app: FastAPI,
    *,
    engine: Any,
    auth: Callable,
    identity_dep: Callable,
) -> None:
    """Wire ``POST /api/auto-trade/close`` onto the given app."""

    @app.post(
        "/api/auto-trade/close",
        tags=["auto-mode"],
        dependencies=[Depends(auth)],
    )
    async def close_position(
        req: ClosePositionRequest,
        identity: Any = Depends(identity_dep),
    ) -> dict:
        firebase_uid = _extract_firebase_uid(identity)
        if firebase_uid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Closing a position requires Firebase sign-in.",
            )

        signal_id = req.signal_id.strip()

        # No tier gate, and that is not an oversight.  Every gate on this
        # engine decides whether a user may ENTER a trade.  A position that
        # exists was already permitted; refusing to let its owner out because
        # their plan lapsed since would strand real money behind a paywall.
        # The engine's own check is ownership: the document is read at
        # ``users/{uid}/positions/{signal_id}``, so a user can only ever
        # address their own.

        is_facade = type(engine).__name__ == "RedisEngineFacade"
        if not is_facade:
            # Single-process mode: the live engine is in-process.
            result = await engine.close_position_for_user(
                firebase_uid, signal_id
            )
            log.info(
                "close_position: direct uid={} signal_id={} outcome={}",
                firebase_uid, signal_id, result.get("outcome"),
            )
            return result

        request_id = uuid.uuid4().hex
        enqueued = await engine.enqueue_close_position(
            request_id=request_id, uid=firebase_uid, signal_id=signal_id,
        )
        if not enqueued:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Engine bridge unavailable — your position is untouched. "
                    "Try again in a moment, or close it in the Binance app."
                ),
            )
        log.info(
            "close_position: queued uid={} signal_id={} request_id={}",
            firebase_uid, signal_id, request_id,
        )

        deadline = asyncio.get_running_loop().time() + _RESULT_POLL_TIMEOUT_S
        while asyncio.get_running_loop().time() < deadline:
            await asyncio.sleep(_RESULT_POLL_INTERVAL_S)
            result = await engine.read_manual_take_result(request_id)
            if result is not None:
                log.info(
                    "close_position: resolved uid={} signal_id={} outcome={}",
                    firebase_uid, signal_id, result.get("outcome"),
                )
                return result

        # The engine has not answered inside the window.  The close is very
        # likely still in flight, so this must NOT read as a failure — that
        # would invite a second tap, and a second close on a flat position is
        # how a user opens the opposite side by accident.
        log.warning(
            "close_position: poll timeout uid={} signal_id={} request_id={}",
            firebase_uid, signal_id, request_id,
        )
        return {
            "outcome": "queued",
            "signal_id": signal_id,
            "detail": (
                "The engine is taking longer than usual. Your close is "
                "queued — do not tap again; the result will appear in your "
                "positions and in Recent Activity."
            ),
        }
