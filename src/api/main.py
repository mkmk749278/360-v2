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

This process also owns the Binance-key **connect flow** (``POST
/api/binance/connect``): the user's API secret is envelope-encrypted with
Cloud KMS *in this process* before the blob is written to Firestore, so
the KMS client must be initialised here at boot — see
:func:`_maybe_init_kms`.  (Order *signing* stays in the dedicated
signing-service container; this container never decrypts.)
"""
from __future__ import annotations

import asyncio
import os
from datetime import timedelta

from src.utils import get_logger

log = get_logger("api.main")


def _maybe_init_kms(firebase_sa_path: str) -> bool:
    """Initialise the Cloud KMS client when the GCP_KMS_* env group is set.

    Mirror of the engine's boot path (``bootstrap.py`` KMS block): all four
    ``GCP_KMS_*`` vars must be non-empty, credentials reuse the Firebase
    service account (fall back to ADC when the path is empty), and failure
    is non-fatal — the api container must still boot for read-only users
    when KMS is unconfigured.

    Session-14's isolation sweep (#565–#569) wired ``init_keystore()`` and
    ``init_kill_switch()`` into this entry point but left KMS out, so every
    isolated-mode ``POST /api/binance/connect`` died at the KMS preflight
    with "Server misconfiguration — KMS not initialised" while
    single-process mode worked.  Returns True iff the client initialised.
    """
    gcp_kms_project_id = os.environ.get("GCP_KMS_PROJECT_ID", "")
    gcp_kms_location = os.environ.get("GCP_KMS_LOCATION", "")
    gcp_kms_keyring = os.environ.get("GCP_KMS_KEYRING", "")
    gcp_kms_key_name = os.environ.get("GCP_KMS_KEY_NAME", "")
    if not (
        gcp_kms_project_id
        and gcp_kms_location
        and gcp_kms_keyring
        and gcp_kms_key_name
    ):
        log.info(
            "KMS client skipped (GCP_KMS_* env vars not set) — "
            "POST /api/binance/connect will refuse with 500"
        )
        return False
    try:
        from src.security import kms_client as _kms_client

        _kms_client.init_kms_client(
            project_id=gcp_kms_project_id,
            location=gcp_kms_location,
            keyring=gcp_kms_keyring,
            key_name=gcp_kms_key_name,
            service_account_path=firebase_sa_path or None,
        )
        return True
    except Exception as exc:
        log.warning(
            "KMS client init failed (binance key connect will refuse): {}",
            exc,
        )
        return False


async def _run() -> None:
    from config import (
        API_ALLOW_STATIC_TOKEN,
        API_AUTH_TOKEN,
        API_CORS_ORIGINS,
        API_HOST,
        API_JWT_SECRET,
        API_PORT,
        BILLING_WEBHOOK_SECRET,
        GOOGLE_PLAY_BILLING_ENABLED,
        GOOGLE_PLAY_PACKAGE_NAME,
        GOOGLE_PLAY_PRODUCT_TIERS,
        GOOGLE_PLAY_RTDN_AUDIENCE,
        GOOGLE_PLAY_RTDN_PATH_SECRET,
        GOOGLE_PLAY_SERVICE_ACCOUNT_PATH,
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
    from src.api.billing_play import PlayBillingVerifier, load_service_account_info
    from src.api.play_purchases import PlayPurchaseStore
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
                # Runtime tunables — the ops panel writes through this
                # process's /api/tunables endpoint; same shared client.
                from src import runtime_tunables as _runtime_tunables
                _runtime_tunables.init_runtime_tunables(_fk._db)
                # Dispatch-event log — the Trade-tab Recent Activity feed
                # (GET /api/auto-trade/recent-events) reads per-user
                # dispatch history DIRECTLY from Firestore in THIS process
                # (dispatch_log.list_recent_events), not via the Redis
                # facade. Without this init the isolated api container's
                # dispatch_log._db stays None → list_recent_events short-
                # circuits to [] and the Live tab shows "NO TRADES YET"
                # even while the ENGINE container is writing placed/
                # rejected rows to the same Firestore collection (owner-
                # reported 2026-07-18: auto-trades executing on Binance,
                # zero history in the app). Share the keystore's client,
                # exactly like the engine boot path (bootstrap.py:573).
                from src.execution import dispatch_log as _dispatch_log
                _dispatch_log.init_dispatch_log(_fk._db)
                log.info("Dispatch-event log client initialised")
        except Exception as exc:
            log.warning(
                "Firestore keystore / kill switch init failed "
                "(binance_key_connected and engine_wide_enabled will show "
                "false, and Recent Activity will be empty): {}", exc
            )
    else:
        log.info("Firebase Admin skipped (env vars not set)")

    # ── Cloud KMS (B18 connect flow) ──────────────────────────────────
    # Independent of the Firebase-Admin conditional above (exactly like
    # bootstrap.py) — KMS init is gated on GCP_KMS_* alone, with the
    # service-account path reused when present, ADC otherwise.
    _maybe_init_kms(firebase_sa_path)

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

    # ── Google Play Billing (B16) ─────────────────────────────────────
    # Construct the verifier whenever a package is configured — the live
    # on/off decision is the runtime ops toggle (kill-switch Firestore doc,
    # boot default GOOGLE_PLAY_BILLING_ENABLED), checked per request in the
    # endpoints.  This lets ops flip billing without a redeploy; is_configured()
    # (needs the service account) still fails closed for real Google calls.
    play_verifier = None
    play_purchases = None
    if GOOGLE_PLAY_PACKAGE_NAME:
        sa_info = load_service_account_info(GOOGLE_PLAY_SERVICE_ACCOUNT_PATH)
        play_verifier = PlayBillingVerifier(
            package_name=GOOGLE_PLAY_PACKAGE_NAME,
            service_account_info=sa_info,
            product_tiers=GOOGLE_PLAY_PRODUCT_TIERS,
        )
        play_purchases = PlayPurchaseStore(LUMIN_DB_PATH)
        log.info(
            "Play billing wired: package={} configured={} default_enabled={}",
            GOOGLE_PLAY_PACKAGE_NAME,
            play_verifier.is_configured(),
            GOOGLE_PLAY_BILLING_ENABLED,
        )
    else:
        log.info("Play billing not wired (GOOGLE_PLAY_PACKAGE_NAME unset)")

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
        play_verifier=play_verifier,
        play_purchases=play_purchases,
        play_rtdn_audience=GOOGLE_PLAY_RTDN_AUDIENCE,
        play_rtdn_path_secret=GOOGLE_PLAY_RTDN_PATH_SECRET,
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
