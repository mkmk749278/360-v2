"""Standalone API process entry point (API_PROCESS_ISOLATED=true).

Runs as ``python -m src.api.main`` inside the ``api`` Docker container.
Connects to Redis and SQLite (shared volumes), builds the FastAPI app
backed by ``RedisEngineFacade``, and serves HTTP on ``API_PORT``.

Responsibility split
────────────────────
* Engine container: scan loop, trade monitor, FSM, SnapshotWriter → Redis
* API container (this file): serve HTTP; read snapshots from Redis; write
  user settings to shared SQLite; queue mode-change commands via Redis

All per-user filtering (paper P&L windows, auto-trade settings) runs here
against the shared SQLite file — no engine object required.
"""
from __future__ import annotations

import asyncio
import os
from datetime import timedelta

from src.utils import get_logger

log = get_logger("api.main")


async def _run() -> None:
    from config import (
        API_ALLOW_STATIC_TOKEN,
        API_AUTH_TOKEN,
        API_CORS_ORIGINS,
        API_HOST,
        API_JWT_SECRET,
        API_PORT,
        BILLING_WEBHOOK_SECRET,
        LUMIN_DB_PATH,
        OTP_MAX_ATTEMPTS_PER_CODE,
        OTP_MAX_ISSUES_PER_HOUR,
        OTP_TTL_SECONDS,
        OWNER_PHONE_E164,
    )
    import uvicorn
    import concurrent.futures as _cf

    from src.redis_client import RedisClient
    from src.api.redis_engine import RedisEngineFacade
    from src.api import firebase_auth
    from src.api.billing_callback import BillingWebhookVerifier
    from src.api.otp import OtpStore
    from src.api.otp_delivery import LogOnlyOtpProvider
    from src.api import user_overrides as user_overrides_module
    from src.api.user_overrides import UserOverridesStore
    from src.api.users import UserStore
    from src.api import users as users_module
    from src.api.server import build_app

    # ── Redis ──────────────────────────────────────────────────────────
    redis = RedisClient()
    connected = await redis.connect()
    if not connected:
        log.warning(
            "api.main: Redis not available — snapshot reads will be cold until "
            "Redis recovers.  Standalone API container requires Redis."
        )

    # ── Engine facade ──────────────────────────────────────────────────
    engine = RedisEngineFacade(redis)
    # Pre-warm state before accepting traffic.
    await engine.refresh_state()

    # ── SQLite: user store ────────────────────────────────────────────
    user_store = UserStore(LUMIN_DB_PATH)
    user_store.bootstrap_owner_if_empty(OWNER_PHONE_E164)
    users_module.set_singleton(user_store)

    # ── Firebase Admin SDK ────────────────────────────────────────────
    firebase_project_id = os.environ.get("FIREBASE_PROJECT_ID", "")
    firebase_sa_path    = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH", "")
    if firebase_project_id and firebase_sa_path:
        try:
            firebase_auth.init_firebase_admin(
                service_account_path=firebase_sa_path,
                project_id=firebase_project_id,
            )
            log.info("Firebase Admin initialised: project={}", firebase_project_id)
        except Exception as exc:
            log.warning(
                "Firebase Admin init failed (falling back to HS256 path): {}", exc
            )
        # Firestore keystore + kill switch — same service account, same client.
        # Required so auto_trade_status_routes can check binance_key_connected
        # (keystore) and engine_wide_enabled (kill switch) in this process.
        # Mirrors bootstrap.py:477-488 — one Firestore client shared between both.
        try:
            from src.security import firestore_keystore as _fk
            from src.execution import kill_switch as _ks
            _fk.init_keystore(service_account_path=firebase_sa_path)
            if _fk._db is not None:
                _ks.init_kill_switch(_fk._db)
                log.info("Kill switch client initialised")
        except Exception as exc:
            log.warning(
                "Firestore keystore / kill switch init failed "
                "(binance_key_connected and engine_wide_enabled will show false): {}", exc
            )
    else:
        log.info("Firebase Admin skipped (env vars not set)")

    # ── Per-user overrides ────────────────────────────────────────────
    user_overrides = UserOverridesStore(LUMIN_DB_PATH)
    user_overrides_module.set_singleton(user_overrides)

    otp_store = OtpStore(
        ttl=timedelta(seconds=OTP_TTL_SECONDS),
        max_attempts_per_code=OTP_MAX_ATTEMPTS_PER_CODE,
        max_issues_per_hour=OTP_MAX_ISSUES_PER_HOUR,
    )
    # Telegram OTP delivery requires a live TelegramBot instance which is
    # only available in the engine container.  API container falls back to
    # LogOnly (operator-mediated forwarding) — the engine container handles
    # actual Telegram delivery via its own OTP endpoint.
    otp_delivery = LogOnlyOtpProvider()

    billing_verifier = BillingWebhookVerifier(BILLING_WEBHOOK_SECRET)

    origins = [o.strip() for o in API_CORS_ORIGINS.split(",") if o.strip()]

    # ── FastAPI app ───────────────────────────────────────────────────
    app = build_app(
        engine,
        jwt_secret=API_JWT_SECRET,
        static_token=API_AUTH_TOKEN,
        allow_static=API_ALLOW_STATIC_TOKEN,
        cors_origins=origins,
        user_store=user_store,
        user_overrides=user_overrides,
        otp_store=otp_store,
        otp_delivery=otp_delivery,
        billing_verifier=billing_verifier,
    )

    # ── Engine-state background refresh ──────────────────────────────
    # Keeps the facade's cached state warm between requests so the first
    # request after a quiet period doesn't hit a stale snapshot.
    asyncio.create_task(engine.start(), name="redis_engine_refresh")

    # ── Thread pool ───────────────────────────────────────────────────
    loop = asyncio.get_running_loop()
    loop.set_default_executor(
        _cf.ThreadPoolExecutor(max_workers=32, thread_name_prefix="api-io")
    )

    # ── Uvicorn ───────────────────────────────────────────────────────
    config = uvicorn.Config(
        app=app,
        host=API_HOST,
        port=API_PORT,
        log_level="warning",
        access_log=False,
        timeout_keep_alive=65,
        limit_concurrency=200,
        timeout_graceful_shutdown=30,
    )
    server = uvicorn.Server(config)
    log.info("API container listening on http://{}:{}", API_HOST, API_PORT)
    await server.serve()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
