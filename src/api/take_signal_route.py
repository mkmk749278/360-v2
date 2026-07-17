"""``POST /api/auto-trade/take`` — server-side manual take (owner-approved
2026-07-17).

A signed-in assist-or-higher user taps "Take trade" on an ACTIVE signal in
the app; the ENGINE places the order on their server-connected Binance key
through the exact same per-user dispatch path as auto-trade (sizing,
tripwires, FSM safety-gate chain, dispatch_log).  This replaces the legacy
client-side placement for server-connected users — their key is
IP-whitelisted to the engine VPS, so phone-originated orders would be
rejected by Binance anyway.

Flow (isolated mode, live on VPS):

    this route ──LPUSH──▶ snapshot:cmd:take ──BRPOP──▶ ManualTakeConsumer
        ▲                                                    │
        └────── poll snapshot:take_result:<request_id> ◀─────┘

The route answers synchronously in the common case (engine consumes in
<1s; we poll the result key up to ~8s) and degrades to 202 "queued — check
Recent Activity" when the engine is slow.  Single-process mode calls
``engine.take_signal_for_user`` directly.

Business rejections (tier, dup position, Binance -2019, …) return **200**
with ``outcome="rejected"`` + the same reject fields the Recent Activity
card renders — they are outcomes, not transport errors.  Transport-level
refusals (flag off, no auth, no key, Redis down) use HTTP status codes.

Scope: signals only.  Alerts carry no SL/TP geometry and the engine's
"never OPEN without a stop" hard limit forbids a stop-less server entry —
an engine-side alert-take needs a designed geometry-synthesis layer first
(owner-sign-off item, B7).
"""
from __future__ import annotations

import asyncio
import uuid
from typing import Any, Callable, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.utils import get_logger

log = get_logger("api.take_signal_route")

# How long the route waits for the engine's answer before returning 202.
_RESULT_POLL_TIMEOUT_S = 8.0
_RESULT_POLL_INTERVAL_S = 0.25


class TakeSignalRequest(BaseModel):
    signal_id: str = Field(min_length=1, max_length=128)


def _extract_firebase_uid(identity: Any) -> Optional[str]:
    """Same logic as binance_connect_routes / auto_trade_status_routes."""
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
    """Wire ``POST /api/auto-trade/take`` onto the given app."""

    @app.post(
        "/api/auto-trade/take",
        tags=["auto-mode"],
        dependencies=[Depends(auth)],
    )
    async def take_signal(
        req: TakeSignalRequest,
        identity: Any = Depends(identity_dep),
    ) -> dict:
        from config import AUTO_TRADE_MANUAL_TAKE_ENABLED
        if not AUTO_TRADE_MANUAL_TAKE_ENABLED:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Server-side take is not enabled on this engine yet."
                ),
            )

        firebase_uid = _extract_firebase_uid(identity)
        if firebase_uid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Taking a trade requires Firebase sign-in.",
            )

        # Tier pre-check — fast feedback with the SAME rule the engine
        # applies (auth.effective_tier ↔ dispatch tier resolution stay in
        # lockstep); the engine re-checks authoritatively at placement.
        import config as _config
        if getattr(_config, "AUTO_TRADE_TIER_GATE_ENABLED", True):
            tier = "free"
            try:
                from src.api import users as _users
                from src.api.auth import can_assist, effective_tier

                store = _users.get_singleton()
                if store is not None:
                    user = await store.aget_by_firebase_uid(firebase_uid)
                    if user is not None:
                        tier = effective_tier(
                            getattr(user, "tier", None),
                            getattr(user, "paid_until", None),
                        )
                if not can_assist(tier):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=(
                            f"One-tap take requires the Assist plan or "
                            f"higher (your plan: {tier})."
                        ),
                    )
            except HTTPException:
                raise
            except Exception:
                log.exception(
                    "take_signal: tier pre-check failed uid={} — deferring "
                    "to the engine's authoritative gate", firebase_uid,
                )

        # Server-connected key pre-check — a take without a key would
        # only fail later inside the signing chain; refuse up-front with
        # actionable copy instead.
        try:
            from src.security import firestore_keystore as _fk
            if _fk.is_initialised():
                try:
                    await asyncio.to_thread(_fk.get_key_blob, firebase_uid)
                except _fk.KeyBlobNotFoundError:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            "Connect your Binance key first: Settings → "
                            "Server-side auto-trade."
                        ),
                    )
        except HTTPException:
            raise
        except Exception:
            log.exception(
                "take_signal: keystore pre-check failed uid={} — deferring "
                "to the engine", firebase_uid,
            )

        signal_id = req.signal_id.strip()
        is_facade = type(engine).__name__ == "RedisEngineFacade"

        if not is_facade:
            # Single-process mode: the live engine is in-process.
            result = await engine.take_signal_for_user(firebase_uid, signal_id)
            log.info(
                "take_signal: direct uid={} signal_id={} outcome={}",
                firebase_uid, signal_id, result.get("outcome"),
            )
            return result

        # Isolated mode — pre-validate against the published snapshot
        # (up to ~60s stale; the engine re-validates against the live
        # book).  Only a *definitively closed* snapshot entry refuses
        # here; an absent snapshot lets the engine decide.
        try:
            await engine.refresh_signals_all()
            snap = engine.published_signal(signal_id)
            if snap is not None and snap.get("is_open") is False:
                return {
                    "outcome": "rejected",
                    "reject_class": "SignalClosed",
                    "reject_detail": (
                        f"This signal already closed "
                        f"({snap.get('status', '?')}) — taking it now would "
                        f"enter without the setup."
                    ),
                    "signal_id": signal_id,
                }
        except Exception:
            log.exception(
                "take_signal: snapshot pre-validation failed — deferring "
                "to the engine",
            )

        request_id = uuid.uuid4().hex
        enqueued = await engine.enqueue_manual_take(
            request_id=request_id, uid=firebase_uid, signal_id=signal_id,
        )
        if not enqueued:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Engine bridge unavailable — try again in a moment."
                ),
            )
        log.info(
            "take_signal: queued uid={} signal_id={} request_id={}",
            firebase_uid, signal_id, request_id,
        )

        deadline = (
            asyncio.get_running_loop().time() + _RESULT_POLL_TIMEOUT_S
        )
        while asyncio.get_running_loop().time() < deadline:
            await asyncio.sleep(_RESULT_POLL_INTERVAL_S)
            result = await engine.read_manual_take_result(request_id)
            if result is not None:
                log.info(
                    "take_signal: resolved uid={} signal_id={} outcome={}",
                    firebase_uid, signal_id, result.get("outcome"),
                )
                return result

        # Engine hasn't answered inside the poll window — the take may
        # still complete; the outcome lands in Recent Activity either way.
        log.warning(
            "take_signal: poll timeout uid={} signal_id={} request_id={}",
            firebase_uid, signal_id, request_id,
        )
        return {
            "outcome": "queued",
            "signal_id": signal_id,
            "detail": (
                "The engine is taking longer than usual — the result will "
                "appear in Recent Activity on the Trade tab."
            ),
        }
