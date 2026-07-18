"""``POST /api/manual-trade/take`` — server-side manual trade builder
(owner-approved 2026-07-18, ``docs/MANUAL_TRADE_BUILDER_DESIGN.md``).

A signed-in assist-or-higher user builds a trade on the chart — MARKET entry or
a resting LIMIT at a slid entry price, with OPTIONAL user-set SL/TP — and the
ENGINE places it on their server-connected Binance key (KMS, IP-whitelisted to
the VPS). This replaces the client-side (device-key, IP-locked) alert take that
is unusable on mobile networks.

Flow mirrors ``take_signal_route`` exactly:

    this route ──LPUSH──▶ snapshot:cmd:take ──BRPOP──▶ ManualTakeConsumer
        ▲            (kind="manual_trade")               │
        └────── poll snapshot:take_result:<id> ◀─────────┘

Single-process mode calls ``engine.build_manual_trade_for_user`` directly.
Business rejections (tier, dup, NotionalTooSmall, Binance -2019, …) return
**200** with ``outcome="rejected"``; transport refusals (flag off, no auth, no
key, Redis down) use HTTP status codes.
"""
from __future__ import annotations

import asyncio
import uuid
from typing import Any, Callable, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src.utils import get_logger

log = get_logger("api.manual_trade_route")

_RESULT_POLL_TIMEOUT_S = 8.0
_RESULT_POLL_INTERVAL_S = 0.25


class ManualTradeRequest(BaseModel):
    ref_id: str = Field(min_length=1, max_length=128)
    symbol: str = Field(min_length=1, max_length=32)
    direction: str = Field(pattern="^(LONG|SHORT|long|short)$")
    entry_type: str = Field(default="market", pattern="^(market|limit)$")
    entry_price: float = Field(gt=0)
    sl_price: float = Field(default=0.0, ge=0)
    tp_prices: List[float] = Field(default_factory=list, max_length=3)
    valid_for_minutes: int = Field(default=0, ge=0, le=1440)


def _extract_firebase_uid(identity: Any) -> Optional[str]:
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
    """Wire ``POST /api/manual-trade/take`` onto the given app."""

    @app.post(
        "/api/manual-trade/take",
        tags=["manual-trade"],
        dependencies=[Depends(auth)],
    )
    async def manual_trade_take(
        req: ManualTradeRequest,
        identity: Any = Depends(identity_dep),
    ) -> dict:
        from config import MANUAL_TRADE_BUILDER_ENABLED
        if not MANUAL_TRADE_BUILDER_ENABLED:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The manual trade builder is not enabled on this engine yet.",
            )

        firebase_uid = _extract_firebase_uid(identity)
        if firebase_uid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Building a trade requires Firebase sign-in.",
            )

        # Tier pre-check — same can_assist rule the engine applies
        # authoritatively at placement.
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
                            f"Building a trade requires the Assist plan or "
                            f"higher (your plan: {tier})."
                        ),
                    )
            except HTTPException:
                raise
            except Exception:
                log.exception(
                    "manual_trade: tier pre-check failed uid={} — deferring "
                    "to the engine's authoritative gate", firebase_uid,
                )

        # Server-connected key pre-check — a trade without a key would only
        # fail later inside the signing chain; refuse up-front instead.
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
                "manual_trade: keystore pre-check failed uid={} — deferring "
                "to the engine", firebase_uid,
            )

        payload = {
            "ref_id": req.ref_id.strip(),
            "symbol": req.symbol.strip().upper(),
            "direction": req.direction.upper(),
            "entry_type": req.entry_type.lower(),
            "entry_price": float(req.entry_price),
            "sl_price": float(req.sl_price),
            "tp_prices": [float(p) for p in req.tp_prices],
            "valid_for_minutes": int(req.valid_for_minutes),
        }
        is_facade = type(engine).__name__ == "RedisEngineFacade"

        if not is_facade:
            # Single-process mode — the live engine is in-process.
            result = await engine.build_manual_trade_for_user(firebase_uid, payload)
            log.info(
                "manual_trade: direct uid={} ref_id={} outcome={}",
                firebase_uid, payload["ref_id"], result.get("outcome"),
            )
            return result

        # Isolated mode — enqueue for the engine's consumer and poll the result.
        request_id = uuid.uuid4().hex
        enqueued = await engine.enqueue_manual_trade(
            request_id=request_id, uid=firebase_uid, payload=payload,
        )
        if not enqueued:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Engine bridge unavailable — try again in a moment.",
            )
        log.info(
            "manual_trade: queued uid={} ref_id={} request_id={}",
            firebase_uid, payload["ref_id"], request_id,
        )

        deadline = asyncio.get_running_loop().time() + _RESULT_POLL_TIMEOUT_S
        while asyncio.get_running_loop().time() < deadline:
            await asyncio.sleep(_RESULT_POLL_INTERVAL_S)
            result = await engine.read_manual_take_result(request_id)
            if result is not None:
                log.info(
                    "manual_trade: resolved uid={} ref_id={} outcome={}",
                    firebase_uid, payload["ref_id"], result.get("outcome"),
                )
                return result

        log.warning(
            "manual_trade: poll timeout uid={} ref_id={} request_id={}",
            firebase_uid, payload["ref_id"], request_id,
        )
        return {
            "outcome": "queued",
            "ref_id": payload["ref_id"],
            "detail": (
                "The engine is taking longer than usual — the result will "
                "appear in Recent Activity on the Trade tab."
            ),
        }
