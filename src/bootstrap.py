"""Bootstrap – engine boot, shutdown, and WebSocket initialisation.

Extracted from :class:`src.main.CryptoSignalEngine` for modularity.
The :class:`Bootstrap` class handles the engine startup sequence,
WebSocket connection setup, pre-flight checks, and graceful shutdown.
"""

from __future__ import annotations

import asyncio
import datetime
import os
import time
from typing import Any, List

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_ACTIVE_CHANNEL_ID,
    TOP50_FUTURES_ONLY,
)
from src.ai_engine import close_shared_session
from src.binance import BinanceClient
from src.rate_limiter import futures_rate_limiter, spot_rate_limiter
from src.utils import get_logger
from src.websocket_manager import WebSocketManager

log = get_logger("bootstrap")

# Higher weight budget during boot — no competing scan traffic yet, so we
# can safely use more of Binance's 6,000/min Spot allowance for fast seeding.
_BOOT_BUDGET: int = 5_500
# Normal steady-state Spot budget — leaves ~500 headroom for WS reconnects.
_STEADY_BUDGET: int = 5_500

# Futures budgets — Binance Futures hard cap is 2,400/min.
_BOOT_BUDGET_FUTURES: int = 2_200
_STEADY_BUDGET_FUTURES: int = 2_200


class Bootstrap:
    """Manages the engine lifecycle: boot, shutdown, and WebSocket setup.

    Parameters
    ----------
    engine:
        The :class:`src.main.CryptoSignalEngine` instance.  All state
        (pair_mgr, data_store, etc.) is accessed via this reference so
        that Bootstrap remains a thin coordinator and avoids circular
        import issues.
    """

    def __init__(self, engine: Any) -> None:
        self._engine = engine

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def preflight_check(self) -> bool:
        """Run pre-flight checks and return True if all critical checks pass."""
        engine = self._engine
        ok = True

        if not TELEGRAM_BOT_TOKEN:
            log.warning("Pre-flight: TELEGRAM_BOT_TOKEN is not set")
            ok = False

        if not TELEGRAM_ACTIVE_CHANNEL_ID:
            log.warning("Pre-flight: TELEGRAM_ACTIVE_CHANNEL_ID is not set — signals will not be delivered")

        if not engine.pair_mgr.pairs:
            log.warning("Pre-flight: pair_mgr has no pairs loaded")
            ok = False

        if not engine.data_store.has_data():
            log.warning("Pre-flight: data_store has no seeded data")
            ok = False

        ws_healthy = (engine._ws_futures.is_healthy if engine._ws_futures else True)
        if not ws_healthy:
            log.warning("Pre-flight: WebSocket managers are not all healthy")

        if not engine._redis_client.available:
            log.warning(
                "Pre-flight: Redis not available – using in-memory fallback"
            )

        try:
            _ping_client = BinanceClient("spot")
            ping_resp = await asyncio.wait_for(
                _ping_client._get("/api/v3/ping", weight=1), timeout=5
            )
            await _ping_client.close()
            if ping_resp is None:
                log.warning("Pre-flight: Binance REST ping returned no data")
            else:
                log.info("Pre-flight: Binance REST ping OK")
        except Exception as exc:
            log.warning("Pre-flight: Binance REST ping failed: {}", exc)

        if ok:
            log.info("Pre-flight checks passed")
        return ok

    async def boot(self) -> None:
        """Execute the full engine boot sequence."""
        from config import validate_critical_env_vars

        engine = self._engine
        log.info("=== 360-Crypto-Eye-Scalping Engine BOOTING ===")
        engine._boot_time = time.monotonic()
        # Wall-clock equivalent for displaying boot timestamps (e.g. in
        # /diag's "Boot: <ISO>" line and in pre/post-deploy split logic).
        # ``_boot_time`` alone is a process-relative counter; subtracting
        # it from ``time.time()`` yields garbage (1970-ish dates).
        engine._boot_wall_time = time.time()

        # 0a. Validate critical env vars (FINDING-011)
        validate_critical_env_vars()

        # 0b. Connect to Redis (graceful fallback if unavailable)
        await engine._redis_client.connect()
        engine.telemetry.set_redis_client(engine._redis_client)

        # 0c. Restore circuit breaker state from Redis (FINDING-021)
        if hasattr(engine, "circuit_breaker"):
            restored = await engine.circuit_breaker.restore_state(engine._redis_client)
            if restored:
                log.info("Circuit breaker state restored from Redis")

        # 0d. Restore free-channel radar watch state from Redis.
        if hasattr(engine, "_free_watch_service"):
            await engine._free_watch_service.restore()

        # 0e. Restore active-signal state — Redis if available, JSON fallback
        # otherwise.  Without this, every engine restart silently dropped
        # in-flight signals (owner reported "Engine shutting down with N
        # active signal(s)" admin alerts losing 3-4 trades per redeploy).
        if hasattr(engine, "router"):
            try:
                await engine.router.restore()
            except Exception as exc:
                log.warning("Failed to restore router state: {}", exc)

        # Wire API call tracking
        BinanceClient.on_api_call = engine.telemetry.record_api_call

        # 1. Fetch pairs
        if TOP50_FUTURES_ONLY:
            await engine.pair_mgr.refresh_top50_futures()
        else:
            await engine.pair_mgr.refresh_pairs()

        if not engine.pair_mgr.pairs:
            msg = "FATAL: No trading pairs loaded — cannot start engine."
            log.critical(msg)
            await engine.telegram.send_admin_alert(f"🛑 {msg}")
            raise RuntimeError(msg)

        # 2. Smart seed — temporarily raise the rate-limit budget since there
        #    is no competing scan traffic during boot.  Spot and Futures use
        #    separate budgets matching Binance's independent per-market caps.
        spot_rate_limiter.set_budget(_BOOT_BUDGET)
        futures_rate_limiter.set_budget(_BOOT_BUDGET_FUTURES)
        cached = engine.data_store.load_snapshot()
        if cached:
            log.info("Disk cache loaded — gap-filling missing data only")
            seeded = await engine.data_store.gap_fill(engine.pair_mgr)
        else:
            log.info("No disk cache found — performing full historical seed")
            seeded = await engine.data_store.seed_all(engine.pair_mgr)
        # Restore steady-state budgets now that seeding is complete.
        spot_rate_limiter.set_budget(_STEADY_BUDGET)
        futures_rate_limiter.set_budget(_STEADY_BUDGET_FUTURES)

        if seeded == 0:
            msg = (
                "FATAL: Historical data seeded for 0 pairs — "
                "cannot start scanner without candle data."
            )
            log.critical(msg)
            await engine.telegram.send_admin_alert(f"🛑 {msg}")
            raise RuntimeError(msg)

        # 2b. Pre-populate CVD from historical 1m klines so evaluators that
        #     gate on CVD divergence are immediately unblocked after restart.
        #     Without this, CVD needs ~100 min of live trade streaming before
        #     the 20-candle lookback is satisfied.
        _cvd_seeded = 0
        _cvd_15m_seeded = 0
        for _sym, _sym_candles in engine.data_store.candles.items():
            _kl_1m = _sym_candles.get("1m", {})
            _tbv = _kl_1m.get("taker_buy_vol_usd")
            _vusd = _kl_1m.get("volume_usd")
            if _tbv is not None and _vusd is not None and len(_tbv) > 0:
                engine._order_flow_store.seed_cvd_from_klines(_sym, _tbv, _vusd)
                _cvd_seeded += 1
            # 15m CVD seed (OWNER_BRIEF §3.4a — HTF Structure, LTF Entry).
            # Same taker_buy / total split as 1m, but on the 15m TF series so
            # downstream divergence detection on 15m bars is immediately
            # unblocked post-restart (avoids ~5h warmup at 20 × 15m).
            _kl_15m = _sym_candles.get("15m", {})
            _tbv_15m = _kl_15m.get("taker_buy_vol_usd")
            _vusd_15m = _kl_15m.get("volume_usd")
            if _tbv_15m is not None and _vusd_15m is not None and len(_tbv_15m) > 0:
                engine._order_flow_store.seed_cvd_15m_from_klines(_sym, _tbv_15m, _vusd_15m)
                _cvd_15m_seeded += 1
        log.info(
            "CVD boot seed complete: 1m=%d/%d, 15m=%d/%d pairs",
            _cvd_seeded, len(engine.data_store.candles),
            _cvd_15m_seeded, len(engine.data_store.candles),
        )

        # 3. Load predictive model
        await engine.predictive.load_model()

        # 4. Start WebSockets
        await self.start_websockets()

        # 4.5 Pre-flight checks
        if not await self.preflight_check():
            log.warning(
                "Pre-flight checks had warnings — engine will start but may be degraded"
            )

        # 5. Launch async tasks
        engine._tasks = self.launch_runtime_tasks()

        await engine.telegram.send_admin_alert("✅ Engine booted successfully")

        # Send a boot test message to the active channel so operators can
        # visually confirm the bot is connected and has posting permission.
        if TELEGRAM_ACTIVE_CHANNEL_ID:
            boot_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            pair_count = len(engine.pair_mgr.pairs)
            test_msg = (
                "🧪 *ENGINE BOOT TEST*\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "✅ Bot is connected and posting to this channel\n"
                f"⏰ Booted at: {boot_utc}\n"
                f"🔍 Scanning {pair_count} pairs\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "_(This is a test message, not a trading signal)_"
            )
            try:
                await engine.telegram.send_message(TELEGRAM_ACTIVE_CHANNEL_ID, test_msg)
                log.info("Boot test message sent to active channel")
            except Exception as exc:
                log.warning("Failed to send boot test message to active channel: {}", exc)

        log.info("=== Engine RUNNING ===")

    def launch_runtime_tasks(self) -> list[asyncio.Task]:
        """Create the standard long-running tasks used after boot or restart.

        This helper is shared by the initial boot path and the admin-triggered
        restart flow so both launch the same runtime loops after one-time setup
        such as pair loading, historical seeding, and WebSocket startup.

        Returns
        -------
        list[asyncio.Task]
            The running task objects for the engine's background loops.
        """
        engine = self._engine
        tasks = [
            asyncio.create_task(engine.router.start()),
            asyncio.create_task(engine.monitor.start()),
            asyncio.create_task(engine.telemetry.start()),
            asyncio.create_task(engine._pair_refresh_loop()),
            asyncio.create_task(engine._scanner.scan_loop()),
            asyncio.create_task(engine.telegram.poll_commands(
                engine._handle_command,
                on_new_member=engine._welcome_new_member,
            )),
            asyncio.create_task(engine._free_channel_loop()),
            asyncio.create_task(engine._weekly_scoreboard_loop()),
            asyncio.create_task(engine._snapshot_loop()),
            asyncio.create_task(engine._invalidation_audit_loop()),
            asyncio.create_task(engine._macro_watchdog.start()),
            asyncio.create_task(engine._liquidation_flush_loop()),
            asyncio.create_task(engine._daily_performance_report_loop()),
            asyncio.create_task(engine._trade_observer.start()),
            asyncio.create_task(engine._content_scheduler.run(), name="content_scheduler"),
        ]

        # Free-watch lifecycle — start the background expiry-check loop.
        if hasattr(engine, "_free_watch_service"):
            tasks.append(asyncio.create_task(engine._free_watch_service.start()))

        # OI poller – background REST polling for Binance Futures Open Interest
        if getattr(engine, "_oi_poller", None) is not None:
            tasks.append(asyncio.create_task(engine._oi_poller.start()))

        # Binance symbol-filter cache (2026-05-19) — populates the
        # LOT_SIZE.stepSize / PRICE_FILTER.tickSize / MIN_NOTIONAL
        # cache used by signal_dispatch to round qty to per-symbol
        # precision.  Without this every order on a non-major pair
        # gets rejected by Binance with -1111.
        from src.execution import symbol_filters as _symbol_filters

        async def _kick_off_symbol_filters() -> None:
            # Refresh once synchronously at boot so the cache is hot
            # before the first signal fires.  Then let the periodic
            # loop take over.
            try:
                count = await _symbol_filters.refresh_filters()
                log.info(
                    "Symbol-filter cache initialised: {} symbols", count,
                )
            except Exception as exc:
                log.warning(
                    "Symbol-filter initial refresh failed: {}; "
                    "periodic loop will retry",
                    exc,
                )
            await _symbol_filters.run_periodic_refresh()

        tasks.append(
            asyncio.create_task(
                _kick_off_symbol_filters(),
                name="symbol_filters_refresh",
            )
        )

        # Lumin app HTTP API — opt-in via API_ENABLED env var.  Imported
        # lazily so engines that don't enable it don't pay the import cost
        # of FastAPI / uvicorn / pydantic-v2.
        from config import (
            API_ALLOW_STATIC_TOKEN,
            API_AUTH_TOKEN,
            API_CORS_ORIGINS,
            API_ENABLED,
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
        if API_ENABLED:
            from datetime import timedelta

            from src.api import serve_api
            from src.api import firebase_auth
            from src.api.billing_callback import BillingWebhookVerifier
            from src.api.otp import OtpStore
            from src.api.otp_delivery import build_provider_from_env
            from src.api import user_overrides as user_overrides_module
            from src.api.user_overrides import UserOverridesStore
            from src.api.users import UserStore

            origins = [o.strip() for o in API_CORS_ORIGINS.split(",") if o.strip()]

            # Phase-2 multi-user wiring.  UserStore opens (and creates if
            # absent) the SQLite file under data/.  Owner is bootstrapped
            # idempotently — only the first boot of an empty DB inserts.
            user_store = UserStore(LUMIN_DB_PATH)
            user_store.bootstrap_owner_if_empty(OWNER_PHONE_E164)
            # Module-level singleton so engine-side modules (tripwires, etc.)
            # can resolve firebase_uid → user_id without re-opening the DB.
            from src.api import users as users_module
            users_module.set_singleton(user_store)

            # Phase-4 Firebase Admin SDK — initialised after UserStore so
            # the request-time auth dependency can verify ID tokens.
            # Both env vars must be set; init failures (bad service-account
            # path, malformed JSON, network) are caught here so engine boot
            # continues via the legacy HS256 path.  Owner flips
            # ``FIREBASE_AUTH_ENABLED=true`` once the service-account JSON
            # is on disk and verified.
            firebase_project_id = os.environ.get("FIREBASE_PROJECT_ID", "")
            firebase_sa_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH", "")
            if firebase_project_id and firebase_sa_path:
                try:
                    firebase_auth.init_firebase_admin(
                        service_account_path=firebase_sa_path,
                        project_id=firebase_project_id,
                    )
                    log.info(
                        "Firebase Admin initialised: project={}",
                        firebase_project_id,
                    )
                except Exception as exc:
                    log.warning(
                        "Firebase Admin init failed (engine will serve via HS256 path): {}",
                        exc,
                    )
            else:
                log.info("Firebase Admin skipped (env vars not set)")

            # Server-side execution custody scaffolding (PR-1 of the
            # 14-PR roadmap — OWNER_BRIEF §3.9 + B18).  Wires Cloud
            # KMS for envelope encryption and Firestore for encrypted
            # key-blob storage.  None of the boot-blocking paths
            # consume these yet — they're scaffolding that downstream
            # PRs (signing service, connect flow, Position FSM) call
            # into.  Init failures here are non-fatal: the engine
            # serves signals fine; only the server-side execution
            # subsystem (which doesn't ship until PR-6+) requires
            # these to be live.
            gcp_kms_project_id = os.environ.get("GCP_KMS_PROJECT_ID", "")
            gcp_kms_location = os.environ.get("GCP_KMS_LOCATION", "")
            gcp_kms_keyring = os.environ.get("GCP_KMS_KEYRING", "")
            gcp_kms_key_name = os.environ.get("GCP_KMS_KEY_NAME", "")
            if (
                gcp_kms_project_id
                and gcp_kms_location
                and gcp_kms_keyring
                and gcp_kms_key_name
            ):
                try:
                    from src.security import kms_client as _kms_client

                    _kms_client.init_kms_client(
                        project_id=gcp_kms_project_id,
                        location=gcp_kms_location,
                        keyring=gcp_kms_keyring,
                        key_name=gcp_kms_key_name,
                        service_account_path=firebase_sa_path or None,
                    )
                except Exception as exc:
                    log.warning(
                        "KMS client init failed (server-side execution disabled): {}",
                        exc,
                    )
            else:
                log.info("KMS client skipped (GCP_KMS_* env vars not set)")

            if firebase_project_id:
                try:
                    from src.security import firestore_keystore as _firestore_keystore

                    _firestore_keystore.init_keystore(
                        service_account_path=firebase_sa_path or None,
                    )
                except Exception as exc:
                    log.warning(
                        "Firestore keystore init failed "
                        "(server-side execution disabled): {}",
                        exc,
                    )
            else:
                log.info("Firestore keystore skipped (Firebase project not set)")

            # Server-side execution stack wiring — kill switch + per-
            # position state + telegram alerts.  Each init is wrapped
            # so a missing dep doesn't crash engine boot (the
            # subsystem just stays offline; signal serving still
            # works via the legacy client-side path).
            #
            # Order matters:
            # 1. KillSwitchClient (needs Firestore client, must init
            #    BEFORE place_signal can be called by anyone).
            # 2. position_state (Firestore CRUD for FSM state).
            # 3. TelegramAlerts (uses engine.telegram, must init
            #    BEFORE any tripwire trip fires alerts).
            if firebase_project_id:
                try:
                    from src.security import firestore_keystore as _firestore_keystore
                    from src.execution import kill_switch as _kill_switch
                    from src.execution import position_state as _position_state
                    from src.execution import telegram_alerts as _telegram_alerts

                    # Share the same Firestore client as the keystore
                    # — one client per process keeps the connection
                    # budget tidy and pools the gRPC stubs.
                    fs_db = _firestore_keystore._db
                    if fs_db is not None:
                        _kill_switch.init_kill_switch(fs_db)
                        log.info("Kill switch client initialised")
                    # position_state has its own init that re-uses
                    # the same SDK; share credentials via the SA path.
                    _position_state.init_position_state(
                        service_account_path=firebase_sa_path or None,
                    )
                    log.info("Position-state Firestore client initialised")
                    # Dispatch-event log — per-user history of every
                    # order-placement attempt (placed + rejected).
                    # Shares the same Firestore client as the keystore
                    # to save quota.  Soft-init: writes are no-ops if
                    # this stays None (subsystem offline).
                    from src.execution import dispatch_log as _dispatch_log
                    _dispatch_log.init_dispatch_log(fs_db)
                    log.info("Dispatch-event log Firestore client initialised")
                    # Telegram alerts dispatcher — engine.telegram is
                    # the long-lived TelegramBot already constructed
                    # in the boot path; we share that single instance.
                    _telegram_alerts.init_telegram_alerts(engine.telegram)
                    log.info("Telegram alerts dispatcher wired")
                except Exception as exc:
                    log.warning(
                        "Server-side execution stack init failed "
                        "(subsystem offline): {}",
                        exc,
                    )

            # Per-user PositionWorker lifecycle manager — starts one
            # PositionWorker per active live-mode user so ORDER_TRADE_UPDATE
            # events (entry fills, SL/TP fires, pre-TP fills) advance the
            # FSM in real time.  Also runs startup reconciliation on boot
            # to advance any PENDING positions whose entries filled while
            # the engine was down (Binance WS does not replay missed events;
            # without this, positions stay PENDING forever and the BE-shift
            # never fires after pre-TP).
            #
            # Wired here (after execution stack init at firebase_project_id
            # scope) so Firestore + signing service are already initialised
            # before the first positionRisk query goes out.
            if firebase_project_id:
                from src.execution import worker_manager as _wm
                from src.execution import reconciler as _rec_mod
                _rec = _rec_mod.Reconciler()
                _rec_mod.set_instance(_rec)
                tasks.append(
                    asyncio.create_task(
                        _wm.start_workers_for_active_users(),
                        name="worker_manager",
                    )
                )
                tasks.append(
                    asyncio.create_task(
                        _rec.run(),
                        name="reconciler",
                    )
                )

            # Phase-2 per-user overrides — shares the same SQLite file
            # (WAL mode lets both connections coexist).  Tables are
            # added with CREATE TABLE IF NOT EXISTS, safe against any
            # pre-existing data.
            user_overrides = UserOverridesStore(LUMIN_DB_PATH)
            # Module-level singleton so engine-side modules (paper_order_manager,
            # etc.) can resolve operator overrides without a constructor-time
            # injection.  Mirrors the ``user_settings`` module-level pattern.
            user_overrides_module.set_singleton(user_overrides)
            otp_store = OtpStore(
                ttl=timedelta(seconds=OTP_TTL_SECONDS),
                max_attempts_per_code=OTP_MAX_ATTEMPTS_PER_CODE,
                max_issues_per_hour=OTP_MAX_ISSUES_PER_HOUR,
            )
            # Inject ``telegram_bot`` + ``user_store`` so the ``telegram``
            # OTP channel (OWNER_BRIEF B13) can DM users by chat_id.
            # Other channels (log/whatsapp/sms) ignore these args.
            otp_delivery = build_provider_from_env(
                telegram_bot=engine.telegram,
                user_store=user_store,
            )
            billing_verifier = BillingWebhookVerifier(BILLING_WEBHOOK_SECRET)

            # Stash on the engine so other subsystems (e.g. Phase-3
            # per-user paper P&L) can resolve the same singletons.
            engine.user_store = user_store
            engine.user_overrides = user_overrides

            tasks.append(
                asyncio.create_task(
                    serve_api(
                        engine,
                        host=API_HOST,
                        port=API_PORT,
                        jwt_secret=API_JWT_SECRET,
                        static_token=API_AUTH_TOKEN,
                        allow_static=API_ALLOW_STATIC_TOKEN,
                        cors_origins=origins,
                        user_store=user_store,
                        user_overrides=user_overrides,
                        otp_store=otp_store,
                        otp_delivery=otp_delivery,
                        billing_verifier=billing_verifier,
                    ),
                    name="api_server",
                )
            )

        return tasks

    async def shutdown(self) -> None:
        """Gracefully shut down all engine components."""
        engine = self._engine
        log.info("Shutting down …")

        # Notify admin about active signals before cleanup (FINDING-013)
        active_count = len(engine.router.active_signals)
        if active_count > 0:
            try:
                await engine.telegram.send_admin_alert(
                    f"⚠️ Engine shutting down with {active_count} active signal(s).\n"
                    "State persisted — will resume on next boot."
                )
            except Exception as exc:
                log.warning("Failed to send shutdown alert: {}", exc)

        # Force a final synchronous persist of router state so the next boot
        # picks up every in-flight signal — even ones whose ``_schedule_persist``
        # task was still in-flight when the shutdown task started.
        try:
            await engine.router._persist_state()
        except Exception as exc:
            log.warning("Failed to persist router state on shutdown: {}", exc)

        # Persist circuit breaker state to Redis (FINDING-021)
        if hasattr(engine, "circuit_breaker"):
            try:
                await engine.circuit_breaker.save_state(engine._redis_client)
            except Exception as exc:
                log.warning("Failed to save circuit breaker state: {}", exc)

        tasks = list(engine._tasks)
        for t in tasks:
            t.cancel()
        await engine.router.stop()
        await engine.monitor.stop()
        await engine.telemetry.stop()
        if engine._ws_futures:
            await engine._ws_futures.stop()
        if getattr(engine, "_ws_futures_liq", None):
            await engine._ws_futures_liq.stop()
        try:
            await engine.data_store.save_snapshot()
        except Exception as exc:
            log.error("Failed to save snapshot on shutdown: {}", exc)
        await engine.data_store.close()
        await engine.pair_mgr.close()
        await engine._exchange_mgr.close()
        if engine._scanner.spot_client:
            await engine._scanner.spot_client.close()
        try:
            await close_shared_session()
        except Exception as exc:
            log.warning("Failed to close AI engine shared session: {}", exc)
        if getattr(engine, "_openai_evaluator", None) is not None:
            try:
                await engine._openai_evaluator.close()
            except Exception as exc:
                log.warning("Failed to close OpenAI evaluator session: {}", exc)
        if getattr(engine, "_macro_watchdog", None) is not None:
            try:
                await engine._macro_watchdog.stop()
            except Exception as exc:
                log.warning("Failed to stop MacroWatchdog: {}", exc)
        if getattr(engine, "_trade_observer", None) is not None:
            try:
                await engine._trade_observer.stop()
            except Exception as exc:
                log.warning("Failed to stop TradeObserver: {}", exc)
        if getattr(engine, "_oi_poller", None) is not None:
            try:
                await engine._oi_poller.stop()
            except Exception as exc:
                log.warning("Failed to stop OIPoller: {}", exc)
        if getattr(engine, "_onchain_client", None) is not None:
            try:
                await engine._onchain_client.close()
            except Exception as exc:
                log.warning("Failed to close on-chain client session: {}", exc)
        await engine._redis_client.close()
        await engine.telegram.stop()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        engine._tasks = []
        log.info("Shutdown complete.")

    async def start_websockets(self) -> None:
        """Subscribe to WebSocket streams for Tier 1 (core) pairs only.

        Tier 2 and Tier 3 pairs use REST polling exclusively; subscribing them
        to WebSocket would exhaust the Binance stream limit and create event-loop
        pressure without proportional signal quality improvement.
        """
        engine = self._engine
        futures_kline_streams: List[str] = []
        futures_liq_streams: List[str] = []

        # 2026-05-14: spot WS removed.  Engine is futures-only per CLAUDE.md
        # (75 USDT-M futures pairs scalped via SMC + order-flow logic).  The
        # spot WS manager was already dormant under ``TOP50_FUTURES_ONLY=true``
        # but the dead scaffolding added cognitive load during the WS bug
        # hunt.  The ``TOP50_FUTURES_ONLY`` flag is retained for now in case
        # an env-level rollback is needed; the corresponding pair_manager
        # paths still exist behind it.

        # Only Tier 1 futures symbols get WebSocket subscriptions
        tier1_futures = engine.pair_mgr.tier1_futures_symbols
        for sym in tier1_futures:
            s = sym.lower()
            futures_kline_streams.append(f"{s}@kline_1m")
            futures_kline_streams.append(f"{s}@kline_5m")
            futures_kline_streams.append(f"{s}@kline_1h")
            futures_kline_streams.append(f"{s}@kline_4h")
            # Separate @forceOrder (liquidation) streams into their own pool
            # to prevent liquidation cascades from starving kline connections.
            # During Extreme Fear events, the flood of forceOrder events across
            # 50 symbols creates event-loop pressure that delays last_pong
            # updates on kline connections, causing false staleness detections.
            futures_liq_streams.append(f"{s}@forceOrder")

        engine._ws_futures = WebSocketManager(
            engine._on_ws_message,
            market="futures",
            admin_alert_callback=engine.telegram.send_admin_alert,
            data_store=engine.data_store,
        )
        # Dedicated liquidation WebSocket manager — uses a separate connection
        # pool so that forceOrder event floods cannot stall kline connections.
        # admin_alert_callback is intentionally None: drops on this manager are
        # expected during Extreme Fear liquidation cascades and should not spam
        # the admin with alerts.
        # forceOrder streams fire only during liquidations and can be silent for
        # hours in calm markets.  Use a much higher staleness multiplier so these
        # connections are not incorrectly flagged as unhealthy.
        engine._ws_futures_liq = WebSocketManager(
            engine._on_ws_message,
            market="futures",
            admin_alert_callback=None,
            data_store=engine.data_store,
            label="futures_liq",
            staleness_multiplier=100,
        )

        if futures_kline_streams:
            await engine._ws_futures.start(futures_kline_streams)
        if futures_liq_streams:
            await engine._ws_futures_liq.start(futures_liq_streams)

        # Set critical pairs for REST fallback during WS outages
        top_futures = tier1_futures[:10]
        if engine._ws_futures and top_futures:
            engine._ws_futures.set_critical_pairs(top_futures)

        # Wire WS manager into the scanner
        engine._scanner.ws_futures = engine._ws_futures

        # Register Tier 1 futures symbols with the OI poller so it knows what to poll
        if getattr(engine, "_oi_poller", None) is not None:
            engine._oi_poller.set_symbols(list(tier1_futures))
