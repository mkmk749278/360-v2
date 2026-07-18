"""``POST /api/push/subscribe`` / ``/api/push/unsubscribe`` — web-push topic proxy.

Why this exists (2026-07-18, web/PWA channel): FCM on the web **cannot**
subscribe to topics client-side — ``subscribeToTopic`` is an Admin-SDK-only
API.  The Android app never needed the server for this; the web app does.
These endpoints let an authenticated client hand over its registration
token and have the engine perform the topic subscribe on its behalf.

Doctrine preserved (``push_notifications.py`` header): the engine stays
**topic-only with no token registry**.

* **Stateless.**  The token is used for the one Admin-SDK call and
  discarded — never persisted, never logged in full.  Token rotation is
  the client's problem: the web app re-subscribes on every boot exactly
  like the Android boot loop re-arms its topic subscriptions.
* **Allow-listed.**  Only the two consumer topics (``alerts`` /
  ``signals``) are reachable — a client cannot subscribe itself to an
  arbitrary topic name.
* **Rate-limited.**  Per-identity sliding window
  (``FCM_TOPIC_PROXY_MAX_PER_MIN``); normal traffic is ≤2 calls per topic
  per boot.
* **Send path unchanged.**  ``push_alert`` / ``push_signal_published`` /
  ``push_signal_outcome`` still address topics; web tokens subscribed
  here simply receive those sends.

Wiring follows the ``binance_connect_routes`` register() convention.
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from typing import Any, Callable, Deque, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

import config
from src.utils import get_logger

log = get_logger("api.push_topic_routes")

#: FCM registration tokens are ~140-160 chars today; bounds are deliberately
#: loose so a Firebase format change doesn't brick web push, while still
#: rejecting obviously-not-a-token payloads before they reach the Admin SDK.
_TOKEN_MIN_LEN = 20
_TOKEN_MAX_LEN = 4096

# Per-identity sliding-window rate limiter (in-memory; the API runs as a
# single process per container, mirroring push_notifications' global cap).
_calls_by_identity: Dict[str, Deque[float]] = {}


def _rate_ok(identity_key: str) -> bool:
    now = time.time()
    window = _calls_by_identity.setdefault(identity_key, deque())
    while window and now - window[0] > 60.0:
        window.popleft()
    if len(window) >= config.FCM_TOPIC_PROXY_MAX_PER_MIN:
        return False
    window.append(now)
    return True


def _reset_rate_limiter() -> None:
    """Test hook — clear the in-memory windows between cases."""
    _calls_by_identity.clear()


def _allowed_topics() -> Dict[str, str]:
    """Client-facing topic name → actual FCM topic.

    The app subscribes by the *canonical* names (``alerts``/``signals``);
    ops can remap the underlying FCM topic via env without an app change,
    same as the send path does.
    """
    return {"alerts": config.FCM_ALERTS_TOPIC, "signals": config.FCM_SIGNALS_TOPIC}


def _identity_key(identity: Any) -> str:
    """Stable rate-limit key for any of the three auth identities."""
    uid = getattr(identity, "firebase_uid", None)
    if uid:
        return f"fb:{uid}"
    user_id = getattr(identity, "user_id", None) or getattr(identity, "id", None)
    if user_id is not None:
        return f"uid:{user_id}"
    # Static-token bypass resolves to None → owner.
    return "owner"


class TopicRequest(BaseModel):
    token: str = Field(..., min_length=_TOKEN_MIN_LEN, max_length=_TOKEN_MAX_LEN)
    topic: str


def register(
    app: FastAPI,
    *,
    auth: Callable,
    identity_dep: Callable,
) -> None:
    """Wire the two topic-proxy endpoints onto the given app."""

    async def _handle(body: TopicRequest, identity: Any, *, subscribe: bool) -> dict:
        topics = _allowed_topics()
        if body.topic not in topics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"unknown topic {body.topic!r} — allowed: "
                    f"{sorted(topics)}"
                ),
            )
        token = body.token.strip()
        if len(token) < _TOKEN_MIN_LEN or any(c.isspace() for c in token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="malformed registration token",
            )
        if not _rate_ok(_identity_key(identity)):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="too many push subscription requests — retry in a minute",
            )

        try:
            import firebase_admin  # type: ignore[import-not-found]

            if not firebase_admin._apps:
                raise RuntimeError("firebase_admin not initialised")
            from firebase_admin import messaging  # type: ignore[import-not-found]
        except Exception:
            # Same operator posture as binance_connect's unwired refusal:
            # clean 503 with an actionable message, never a route failure.
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Push service unavailable — Firebase Admin is not "
                    "initialised on this deployment."
                ),
            )

        fcm_topic = topics[body.topic]
        op = (
            messaging.subscribe_to_topic
            if subscribe
            else messaging.unsubscribe_from_topic
        )
        try:
            # Admin SDK call is blocking HTTP — keep it off the event loop.
            response = await asyncio.to_thread(op, [token], fcm_topic)
        except Exception as exc:
            log.warning(
                "push topic proxy: {} failed for topic={} token_first8={}: {}",
                "subscribe" if subscribe else "unsubscribe",
                fcm_topic,
                token[:8],
                exc,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="FCM topic management call failed — retry later",
            )

        # TopicManagementResponse: per-token success/failure detail.  With
        # exactly one token, failure_count>0 means FCM rejected it
        # (expired/invalid registration) — surface that as a client error
        # so the web app knows to mint a fresh token and retry.
        if getattr(response, "failure_count", 0):
            errors = getattr(response, "errors", None) or []
            reason = getattr(errors[0], "reason", "unknown") if errors else "unknown"
            log.info(
                "push topic proxy: FCM rejected token_first8={} topic={} reason={}",
                token[:8],
                fcm_topic,
                reason,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"FCM rejected the registration token ({reason})",
            )

        log.debug(
            "push topic proxy: {} ok topic={} token_first8={}",
            "subscribe" if subscribe else "unsubscribe",
            fcm_topic,
            token[:8],
        )
        return {"ok": True, "topic": body.topic, "subscribed": subscribe}

    @app.post(
        "/api/push/subscribe",
        tags=["push"],
        dependencies=[Depends(auth)],
    )
    async def push_subscribe(
        body: TopicRequest,
        identity: Optional[Any] = Depends(identity_dep),
    ) -> dict:
        """Subscribe the presented FCM registration token to a topic."""
        return await _handle(body, identity, subscribe=True)

    @app.post(
        "/api/push/unsubscribe",
        tags=["push"],
        dependencies=[Depends(auth)],
    )
    async def push_unsubscribe(
        body: TopicRequest,
        identity: Optional[Any] = Depends(identity_dep),
    ) -> dict:
        """Unsubscribe the presented FCM registration token from a topic."""
        return await _handle(body, identity, subscribe=False)
