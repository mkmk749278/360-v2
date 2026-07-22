"""360-Crypto-Eye-Scalping – main orchestrator.

Boots the engine:
  1. Fetch top pairs from Binance
  2. Seed historical OHLCV + tick data
  3. Open WebSocket connections
  4. Run scanner → queue → router → Telegram pipeline
  5. Start trade monitor, telemetry, command handler

Usage:
    python -m src.main
"""

from __future__ import annotations

import asyncio
import collections
import os
import signal
import time
from datetime import datetime
from typing import Any, Dict, Deque, List, Optional, Set, Tuple, Union

from config import (
    PAIR_FETCH_INTERVAL_HOURS,
    TOP50_FUTURES_ONLY,
)
from src.ai_engine import get_ai_insight
from src.bootstrap import Bootstrap
from src.macro_watchdog import MacroWatchdog
from src.channels.base import Signal
from src.channels.scalp import ScalpChannel
from src.channels.scalp_fvg import ScalpFVGChannel
from src.channels.scalp_cvd import ScalpCVDChannel
from src.channels.scalp_vwap import ScalpVWAPChannel
from src.channels.scalp_divergence import ScalpDivergenceChannel
from src.channels.scalp_supertrend import ScalpSupertrendChannel
from src.channels.scalp_ichimoku import ScalpIchimokuChannel
from src.channels.scalp_orderblock import ScalpOrderblockChannel
from src.circuit_breaker import CircuitBreaker

from src.commands import CommandHandler
from src.detector import SMCDetector
from src.exchange import ExchangeManager
from src.historical_data import HistoricalDataStore
from src.onchain import OnChainClient
from src.openai_evaluator import OpenAIEvaluator
from src.order_flow import LiquidationEvent, OrderFlowStore, OIPoller
from src.pair_manager import PairManager

from src.performance_tracker import PerformanceTracker
from src.predictive_ai import PredictiveEngine
from src.regime import RegimeService
from src.scanner import Scanner, _cohort_edge_store as _scanner_cohort_edge_store, _stat_filter as _scanner_stat_filter
from src.strategy_edge import get_strategy_edge_store as _strategy_edge_store
from src.mover_ignition import MoverIgnitionDetector
from src.signal_history_backfill import (
    backfill_from_legacy_sources,
    reconcile_invalidation_status,
    reconcile_missing_tps,
)
from src.signal_history_store import load_history, save_history
from src.signal_router import SignalRouter
from src.telegram_bot import TelegramBot
from src.telemetry import TelemetryCollector
from src.trade_monitor import TradeMonitor
from src.trade_observer import TradeObserver
from src.exchange_client import CCXTClient
from src.order_manager import OrderManager
from src.paper_order_manager import PaperOrderManager
from src.execution.paper_book_registry import PaperBookFanout, PaperBookRegistry
from src.auto_trade.risk_manager import RiskManager
from config import PAPER_BOOKS_DIR, PAPER_PER_USER_BOOKS
from src.auto_trade.position_reconciler import PositionReconciler
from src.utils import get_logger
from src.websocket_manager import WebSocketManager
from src.redis_client import RedisClient
from src.signal_queue import SignalQueue
from src.state_cache import StateCache
from src.scheduler import ContentScheduler
from src.free_watch_service import FreeWatchService
from config import (
    MOVER_IGNITION_ENABLED,
    MOVER_IGNITION_WINDOW_SEC,
    MOVER_IGNITION_MOVE_FLOOR_PCT,
    MOVER_IGNITION_BURST_MULT,
    MOVER_IGNITION_MIN_NOTIONAL_USD,
    MOVER_IGNITION_COOLDOWN_SEC,
    MOVER_IGNITION_BASELINE_ALPHA,
    MOVER_IGNITION_MIN_BASELINE_SAMPLES,
    MOVER_IGNITION_MAX_GAP_SEC,
    CIRCUIT_BREAKER_MAX_CONSECUTIVE_SL,
    CIRCUIT_BREAKER_MAX_HOURLY_SL,
    CIRCUIT_BREAKER_MAX_DAILY_DRAWDOWN_PCT,
    CIRCUIT_BREAKER_COOLDOWN_SECONDS,
    CIRCUIT_BREAKER_STARTUP_GRACE_SECONDS,
    CIRCUIT_BREAKER_RESUME_AFTER_COOLDOWN,
    CHANNEL_TELEGRAM_MAP,
    ONCHAIN_API_KEY,
    PERFORMANCE_TRACKER_PATH,
    AUTO_EXECUTION_MODE,
    EXCHANGE_ID,
    EXCHANGE_API_KEY,
    EXCHANGE_API_SECRET,
    EXCHANGE_SANDBOX,
    POSITION_SIZE_PCT,
    MAX_POSITION_USD,
    RISK_DAILY_LOSS_LIMIT_PCT,
    RISK_MAX_CONCURRENT,
    RISK_MAX_LEVERAGE,
    RISK_MIN_EQUITY_USD,
    RISK_SETUP_BLACKLIST,
    RISK_STARTING_EQUITY_USD,
    RECONCILER_AUTO_CLOSE_ORPHANS,
    RECONCILER_PERIODIC_INTERVAL_SEC,
)

log = get_logger("main")

# Interval between automatic disk snapshots of historical data (seconds)
_SNAPSHOT_INTERVAL_SECONDS: int = 300  # 5 minutes
_WS_SYMBOL_LIMIT: int = 50


class CryptoSignalEngine:
    """Top-level orchestrator for the signal engine.

    Wires together all sub-components and delegates to:
    - :class:`src.bootstrap.Bootstrap` for boot/shutdown/WebSocket setup
    - :class:`src.scanner.Scanner` for the periodic scan loop
    - :class:`src.commands.CommandHandler` for Telegram command routing
    """

    def __init__(self) -> None:
        self.pair_mgr = PairManager()
        # Register the module-level singleton so engine-side modules
        # (tripwires, etc.) can read the live pair universe without
        # an engine-handle dependency.  Doctrine: blast-radius
        # allowlist auto-tracks this when ``TRIPWIRE_SYMBOL_ALLOWLIST``
        # env is unset (PR G 2026-05-19).
        from src import pair_manager as _pair_manager_module
        _pair_manager_module.set_singleton(self.pair_mgr)
        self.data_store = HistoricalDataStore()
        self.telegram = TelegramBot()
        self.telemetry = TelemetryCollector()

        # Strong refs for money-path fire-and-forget tasks (expiry broker
        # close): the event loop holds only a weak ref, so an unreferenced
        # task can be GC'd before the close lands (2026-07-16 audit; same
        # pattern as mark_price_feed._background_tasks).
        self._expiry_close_tasks: Set[asyncio.Task] = set()

        self._redis_client = RedisClient()
        self._signal_queue = SignalQueue(
            self._redis_client,
            alert_callback=self.telegram.send_admin_alert,
        )
        self._state_cache = StateCache(self._redis_client)
        self.router = SignalRouter(
            queue=self._signal_queue,
            send_telegram=self.telegram.send_message,
            format_signal=TelegramBot.format_signal,
            redis_client=self._redis_client,
        )

        # Risk gates (Phase A2) — mandatory under B12 before any live
        # execution.  Constructed eagerly so paper mode also obeys the same
        # gate chain; off-mode skips construction entirely (no auto-trade).
        self._risk_manager: Optional[RiskManager] = None
        # Set when PAPER_PER_USER_BOOKS is on — the read layer reads per-user
        # books through this registry (via the fanout on _order_manager).
        self._paper_book_registry: Optional[PaperBookRegistry] = None
        if AUTO_EXECUTION_MODE != "off":
            self._risk_manager = RiskManager(
                starting_equity_usd=RISK_STARTING_EQUITY_USD,
                daily_loss_limit_pct=RISK_DAILY_LOSS_LIMIT_PCT,
                max_concurrent=RISK_MAX_CONCURRENT,
                max_leverage=RISK_MAX_LEVERAGE,
                min_equity_usd=RISK_MIN_EQUITY_USD,
                setup_blacklist=set(RISK_SETUP_BLACKLIST),
                mode=AUTO_EXECUTION_MODE,
            )
            log.info(
                "RiskManager active: start_equity=$%.2f daily_kill=%.2f%% "
                "max_concurrent=%d max_leverage=%.0fx min_equity=$%.2f "
                "setup_blacklist=%d",
                RISK_STARTING_EQUITY_USD, RISK_DAILY_LOSS_LIMIT_PCT,
                RISK_MAX_CONCURRENT, RISK_MAX_LEVERAGE, RISK_MIN_EQUITY_USD,
                len(RISK_SETUP_BLACKLIST),
            )

        # Order execution — three modes (Phase A1):
        #   off   → no auto-trade (signals → Telegram only)
        #   paper → PaperOrderManager simulates fills, zero real-money risk
        #   live  → OrderManager via CCXT places real orders
        # AUTO_EXECUTION_ENABLED is a derived bool kept for backwards compat.
        _exchange_client: Optional[CCXTClient] = None
        if AUTO_EXECUTION_MODE == "paper":
            self._order_manager = self._build_paper_order_manager()
            log.info(
                "Auto-execution mode: PAPER (simulated fills, zero real-money risk)"
            )
        elif AUTO_EXECUTION_MODE == "live":
            # ccxt is deliberately NOT in requirements.txt (the production
            # money path is the server-side FSM via the signing service,
            # not this legacy CCXT client).  Without this guard, live mode
            # boots fine and then raises NotImplementedError on the FIRST
            # ORDER — fail at boot instead, where the operator is looking.
            from src import exchange_client as _ec_mod
            if not _ec_mod._CCXT_AVAILABLE:
                raise RuntimeError(
                    "AUTO_EXECUTION_MODE=live requires the ccxt package, "
                    "which is not installed (commented out in "
                    "requirements.txt). Install ccxt or use the server-side "
                    "auto-trade stack instead."
                )
            _exchange_client = CCXTClient(
                exchange_id=EXCHANGE_ID,
                api_key=EXCHANGE_API_KEY,
                secret=EXCHANGE_API_SECRET,
                sandbox=EXCHANGE_SANDBOX,
            )
            self._order_manager = OrderManager(
                auto_execution_enabled=True,
                exchange_client=_exchange_client,
                position_size_pct=POSITION_SIZE_PCT,
                max_position_usd=MAX_POSITION_USD,
                risk_manager=self._risk_manager,
                redis_client=self._redis_client,
            )
            log.info(
                "Auto-execution mode: LIVE (real orders via %s, sandbox=%s)",
                EXCHANGE_ID, EXCHANGE_SANDBOX,
            )
        else:
            # mode == "off"
            self._order_manager = OrderManager(
                auto_execution_enabled=False,
                exchange_client=None,
                position_size_pct=POSITION_SIZE_PCT,
                max_position_usd=MAX_POSITION_USD,
                redis_client=self._redis_client,
            )
            log.info("Auto-execution mode: OFF (signals → Telegram only)")

        # Position reconciler — Phase A3.  Live-mode only (paper has no
        # exchange state to reconcile).  reconcile_on_boot() is invoked
        # from Bootstrap once the engine has wired the router; the
        # periodic loop is started as a background task.
        self._position_reconciler: Optional[PositionReconciler] = None
        if AUTO_EXECUTION_MODE == "live" and _exchange_client is not None:
            self._position_reconciler = PositionReconciler(
                exchange_client=_exchange_client,
                # Active signals come from router — set after router init
                # below via attribute assignment to avoid forward-reference.
                get_active_signals_fn=lambda: getattr(self, "router", None)
                    and self.router.active_signals or {},
                alert_callback=self.telegram.send_admin_alert,
                auto_close_orphans=RECONCILER_AUTO_CLOSE_ORPHANS,
                risk_manager=self._risk_manager,
                close_signal_fn=self._reconciler_close_signal,
            )
            log.info(
                "PositionReconciler active: interval=%ds auto_close_orphans=%s",
                RECONCILER_PERIODIC_INTERVAL_SEC, RECONCILER_AUTO_CLOSE_ORPHANS,
            )
        # Track the currently-active auto-execution mode for runtime control.
        # Initial value comes from the env var; can be changed at runtime via
        # the /automode Telegram command (ephemeral — env still wins on
        # engine restart).
        self._exchange_client = _exchange_client
        self._current_auto_mode: str = AUTO_EXECUTION_MODE

        # Circuit breaker (must be created before TradeMonitor)
        self._circuit_breaker = CircuitBreaker(
            max_consecutive_sl=CIRCUIT_BREAKER_MAX_CONSECUTIVE_SL,
            max_hourly_sl=CIRCUIT_BREAKER_MAX_HOURLY_SL,
            max_daily_drawdown_pct=CIRCUIT_BREAKER_MAX_DAILY_DRAWDOWN_PCT,
            cooldown_seconds=CIRCUIT_BREAKER_COOLDOWN_SECONDS,
            startup_grace_seconds=CIRCUIT_BREAKER_STARTUP_GRACE_SECONDS,
            resume_after_cooldown=CIRCUIT_BREAKER_RESUME_AFTER_COOLDOWN,
            alert_callback=self.telegram.send_admin_alert,
        )

        # Performance tracker (must be created before TradeMonitor)
        self._performance_tracker = PerformanceTracker(
            storage_path=PERFORMANCE_TRACKER_PATH
        )

        # Wire the per-pair soft-penalty cache to read from the tracker —
        # doctrine-aligned replacement for the closed Tier-4 hard
        # blacklist (PR #424).  Lazy-refreshed on the scan loop via
        # ``pair_penalty.get(symbol)``; no extra timers needed.
        from src import pair_penalty as _pair_penalty_module
        _pair_penalty_module.set_tracker(self._performance_tracker)

        self.monitor = TradeMonitor(
            data_store=self.data_store,
            send_telegram=self.telegram.send_message,
            get_active_signals=lambda: self.router.active_signals,
            remove_signal=self._remove_and_archive,
            update_signal=self.router.update_signal,
            performance_tracker=self._performance_tracker,
            circuit_breaker=self._circuit_breaker,
            order_manager=self._order_manager,
            stat_filter=_scanner_stat_filter,
            cohort_edge_store=_scanner_cohort_edge_store,
            strategy_edge_store=_strategy_edge_store(),
        )

        # Channel strategies
        self._channels = [
            ScalpChannel(),
            ScalpFVGChannel(),
            ScalpCVDChannel(),
            ScalpVWAPChannel(),
            ScalpDivergenceChannel(),
            ScalpSupertrendChannel(),
            ScalpIchimokuChannel(),
            ScalpOrderblockChannel(),
        ]

        # SMC detector and market regime classifier.  RegimeService owns one
        # per-symbol detector so each pair keeps its own hysteresis/transition
        # state and its volume-tier thresholds — a single shared detector
        # cross-contaminated all 75 pairs and never applied tier profiles.
        self._smc_detector = SMCDetector()
        self._regime_detector = RegimeService()

        # Wire regime detector into trade monitor for signal invalidation checks
        self.monitor._regime_detector = self._regime_detector

        # Predictive AI engine
        self.predictive = PredictiveEngine()

        # OpenAI GPT-4 macro-event evaluator (repurposed – no longer scores trade signals)
        self._openai_evaluator = OpenAIEvaluator()

        # Macro Watchdog – async background task for global market-event alerts
        # Polls news, Fear & Greed index, and uses OpenAI to detect significant
        # macro events (FOMC, wars, token listings) and sends alerts to Telegram.
        # HIGH/CRITICAL severity events also broadcast to the free channel as
        # subscriber-visible breaking news (paid-conversion funnel content).
        # MEDIUM/LOW severity stays admin-only.
        self._macro_watchdog = MacroWatchdog(
            send_alert=self.telegram.send_admin_alert,
            send_to_free=self.telegram.post_to_free_channel,
            openai_evaluator=self._openai_evaluator,
        )

        # AI Trade Observer – captures full trade lifecycle data and generates
        # periodic AI-powered digests for the admin channel.
        self._trade_observer = TradeObserver(
            send_alert=self.telegram.send_admin_alert,
            data_store=self.data_store,
            regime_detector=self._regime_detector,
        )
        # Wire observer into router and monitor so they can call the hooks
        self.router.observer = self._trade_observer
        self.monitor.observer = self._trade_observer

        # On-chain intelligence client (optional — no-op if key is absent)
        self._onchain_client = OnChainClient(api_key=ONCHAIN_API_KEY)

        # Order flow analytics: OI tracking, liquidations, CVD divergence
        self._order_flow_store = OrderFlowStore()
        self._oi_poller = OIPoller(
            store=self._order_flow_store,
            futures_rest_base=os.getenv("BINANCE_FUTURES_REST_BASE", "https://fapi.binance.com"),
        )

        # Multi-exchange verification
        self._exchange_mgr = ExchangeManager(
            second_exchange_url=os.getenv("SECOND_EXCHANGE_URL")
        )

        # WebSocket managers (set during boot)
        # 2026-05-14: spot WS removed.  Engine is futures-only per CLAUDE.md
        # (75 USDT-M futures pairs).  The spot manager existed as dormant
        # scaffolding under ``TOP50_FUTURES_ONLY=true`` and added no runtime
        # value while adding cognitive load to every WS bug-hunt.
        self._ws_futures: Optional[WebSocketManager] = None
        # Dedicated liquidation WebSocket manager — forceOrder streams run in
        # their own connection pool so that liquidation floods during Extreme
        # Fear events cannot stall the kline WebSocket connections.
        self._ws_futures_liq: Optional[WebSocketManager] = None
        # Dedicated all-market ticker WebSocket manager — the high-throughput
        # `!ticker@arr` stream (every changed symbol, 1/sec) runs in its own
        # connection pool so its frame size cannot stall the kline connections,
        # mirroring the liquidation-pool separation above.
        self._ws_futures_mover: Optional[WebSocketManager] = None
        # Real-time mover-ignition detector — folds `!ticker@arr` frames and
        # surfaces pairs igniting *now*; drained by the scanner each cycle to
        # promote them (replaces the lagging 24h-%change trigger). Pure in-memory.
        self._mover_ignition = MoverIgnitionDetector(
            enabled=MOVER_IGNITION_ENABLED,
            window_sec=MOVER_IGNITION_WINDOW_SEC,
            move_floor_pct=MOVER_IGNITION_MOVE_FLOOR_PCT,
            burst_mult=MOVER_IGNITION_BURST_MULT,
            min_window_notional_usd=MOVER_IGNITION_MIN_NOTIONAL_USD,
            cooldown_sec=MOVER_IGNITION_COOLDOWN_SEC,
            baseline_alpha=MOVER_IGNITION_BASELINE_ALPHA,
            min_baseline_samples=MOVER_IGNITION_MIN_BASELINE_SAMPLES,
            max_gap_sec=MOVER_IGNITION_MAX_GAP_SEC,
        )
        # Ignited (symbol → direction) awaiting promotion; the scanner drains
        # this at the top of each scan cycle. Shared by reference with the
        # scanner so the WS handler stays a cheap producer.
        self._mover_ignition_pending: Dict[str, str] = {}
        # Buffer for incoming forceOrder events — drained at the top of each
        # scan cycle so that processing is never inline on the WS message loop.
        self._pending_liquidations: Deque[LiquidationEvent] = collections.deque()
        self._tasks: List[asyncio.Task] = []
        self._shutdown_started: bool = False
        self._restart_lock = asyncio.Lock()

        # Command handler state
        self._paused_channels: Set[str] = set()
        self._confidence_overrides: Dict[str, float] = {}
        self._signal_history: List[Signal] = []  # capped at 500 entries
        # Rehydrate from disk so closed-signal feed survives restarts.  Cap
        # is applied by the loader; malformed records are skipped.
        try:
            self._signal_history.extend(load_history())
        except Exception as exc:
            log.warning(f"signal_history rehydrate failed: {exc}")
        # First-boot backfill: when persistence is empty (file doesn't exist
        # yet — the case for the post-PR-#299 deploy on a long-running engine
        # whose pre-PR signals were in-memory only), reconstruct a starting
        # set from the durable PerformanceTracker + InvalidationAudit JSONs.
        # Idempotent: once save_history has flushed real records the file
        # exists and load_history populates `_signal_history`, so this
        # branch is skipped on every subsequent boot.
        if not self._signal_history:
            try:
                backfilled = backfill_from_legacy_sources()
                if backfilled:
                    self._signal_history.extend(backfilled)
                    save_history(self._signal_history)
                    log.info(
                        "signal_history backfilled from legacy sources: %d records",
                        len(backfilled),
                    )
            except Exception as exc:
                log.warning(f"signal_history backfill failed: {exc}")
        # Always reconcile invalidation labels against the audit log.  Catches
        # records persisted with the wrong "CLOSED"/"BREAKEVEN_EXIT" label
        # because trade_monitor.record_outcome historically derived from
        # (hit_tp, hit_sl) and missed the explicit sig.status="INVALIDATED".
        # Idempotent — runs every boot, only mutates if something needs fixing.
        try:
            fixed = reconcile_invalidation_status(self._signal_history)
            if fixed:
                save_history(self._signal_history)
        except Exception as exc:
            log.warning(f"signal_history reconciliation failed: {exc}")

        # Also patch missing TPs (TP2/TP3) on signals backfilled from
        # PerformanceTracker / InvalidationAudit before PR #299 — neither
        # store carries TP2/TP3, but dispatch_log.json does.  Without this,
        # the app's history rows show TP1=0/TP3=0 on every old signal.
        try:
            tp_fixed = reconcile_missing_tps(self._signal_history)
            if tp_fixed:
                save_history(self._signal_history)
        except Exception as exc:
            log.warning(f"signal_history TP reconciliation failed: {exc}")
        self._boot_time: float = 0.0          # time.monotonic() — for uptime
        self._boot_wall_time: float = 0.0     # time.time()      — for ISO display
        self._free_channel_limit: int = 2  # max free signals published per day
        self._alert_subscribers: Set[str] = set()  # admin IDs subscribed to alerts

        # Scanner (dependency-injected)
        self._scanner = Scanner(
            pair_mgr=self.pair_mgr,
            data_store=self.data_store,
            channels=self._channels,
            smc_detector=self._smc_detector,
            regime_detector=self._regime_detector,
            predictive=self.predictive,
            exchange_mgr=self._exchange_mgr,
            spot_client=None,
            telemetry=self.telemetry,
            signal_queue=self._signal_queue,
            router=self.router,
            openai_evaluator=self._openai_evaluator,
            onchain_client=self._onchain_client,
            order_flow_store=self._order_flow_store,
        )
        # Share mutable state with scanner
        self._scanner.paused_channels = self._paused_channels
        self._scanner.confidence_overrides = self._confidence_overrides
        self._scanner.circuit_breaker = self._circuit_breaker

        # Market Alerts (Pulse → Alerts feed + FCM `alerts` topic).  Reads
        # only in-memory candles + the scanner's LevelBook — zero network
        # I/O per sweep.  Launched in bootstrap when ALERTS_ENABLED.
        from src.alerts import AlertService
        from src.push_notifications import push_alert
        self._alert_service = AlertService(
            data_store=self.data_store,
            level_book_getter=lambda: self._scanner.level_book,
            symbols_getter=lambda: list(self.pair_mgr.symbols),
            on_alert=push_alert,
            volume_24h_getter=lambda s: (
                self.pair_mgr.pairs[s].volume_24h_usd
                if s in self.pair_mgr.pairs else None
            ),
        )

        # Wire the free-channel highlight callback so the monitor posts winning
        # trades (TP2+) to the free channel in real-time.
        self.monitor.on_highlight_callback = lambda sig, tp, pnl: asyncio.ensure_future(
            self.router.publish_highlight(sig, tp, pnl)
        )
        # Wire lifecycle outcome callback so scanner observability can attribute
        # final outcomes back to setup family/path.
        self.monitor.on_lifecycle_outcome_callback = self._scanner.on_signal_lifecycle_outcome

        # PR2: Wire the engine context provider into the trade monitor so that
        # signal-closed (TP/SL hit) AI posts are generated and sent automatically.
        self.monitor.engine_context_fn = self._get_engine_context

        # PR2: Content scheduler — fires daily briefings, session opens, weekly card.
        self._content_scheduler = ContentScheduler(
            post_to_free=self.telegram.post_to_free_channel,
            post_to_active=self.telegram.post_to_active_channel,
            engine_context_fn=self._get_engine_context,
        )

        # Free-channel radar watch lifecycle service.
        # Tracks radar_alert posts and resolves them when a paid signal matches
        # or when the watch TTL expires.  market_watch is NOT tracked here.
        self._free_watch_service = FreeWatchService(
            send_free=self.telegram.post_to_free_channel,
            redis_client=self._redis_client,
        )
        # Wire radar candidate callback: scanner → watch creation + free posting.
        self._scanner.on_radar_candidate = self._handle_radar_candidate
        # Wire paid-signal callback: router → watch resolution.
        self.router.on_signal_routed = self._free_watch_service.on_paid_signal
        # Wire expired-signal callback: router.cleanup_expired → engine handler.
        # Without this, expired signals get dropped from active_signals with no
        # status flip / no archive / no broker close — broker positions stay
        # open after the engine has stopped tracking them, perf-tracker gets
        # no record, and the Lumin app's Closed→Expired sub-filter shows
        # nothing.  See _handle_signal_expiry below.
        self.router.on_signal_expired = self._handle_signal_expiry

        # Command handler (delegates all Telegram commands)
        self._command_handler = CommandHandler(
            telegram=self.telegram,
            telemetry=self.telemetry,
            pair_mgr=self.pair_mgr,
            router=self.router,
            data_store=self.data_store,
            signal_queue=self._signal_queue,
            signal_history=self._signal_history,
            paused_channels=self._paused_channels,
            confidence_overrides=self._confidence_overrides,
            scanner=self._scanner,
            ws_futures=None,
            tasks=self._tasks,
            boot_time=self._boot_time,
            boot_wall_time=self._boot_wall_time,
            free_channel_limit=self._free_channel_limit,
            alert_subscribers=self._alert_subscribers,
            restart_callback=self._restart_tasks,
            ai_insight_fn=get_ai_insight,
            symbols_fn=lambda: self.pair_mgr.symbols,
            performance_tracker=self._performance_tracker,
            circuit_breaker=self._circuit_breaker,
            trade_observer=self._trade_observer,
            set_auto_execution_mode_fn=self.set_auto_execution_mode,
            get_auto_execution_status_fn=self.get_auto_execution_status,
        )

        # Bootstrap coordinates the boot/shutdown/WS sequence
        self._bootstrap = Bootstrap(self)

    async def _reconciler_close_signal(self, sig: Any, reason: str) -> None:
        """Called by PositionReconciler when a signal is confirmed missing from
        the broker for two consecutive drift cycles.

        The broker has ALREADY closed the position — do NOT issue a market
        order.  Mark the signal terminal, compute approximate P&L from the
        last-known mark price, send an admin alert, and remove from engine.
        """
        sig_id = getattr(sig, "signal_id", None)
        if sig_id is None:
            return
        if sig_id not in self.router.active_signals:
            return  # already removed by another close path — idempotent

        entry = float(getattr(sig, "entry", 0.0) or 0.0)
        current_price = float(getattr(sig, "current_price", 0.0) or 0.0)
        try:
            from src.smc import Direction
            if entry > 0 and current_price > 0:
                if sig.direction == Direction.LONG:
                    sig.pnl_pct = (current_price - entry) / entry * 100.0
                else:
                    sig.pnl_pct = (entry - current_price) / entry * 100.0
        except Exception:
            pass

        sig.status = "CANCELLED"

        try:
            symbol = getattr(sig, "symbol", "?")
            pnl = float(getattr(sig, "pnl_pct", 0.0) or 0.0)
            await self.telegram.send_admin_alert(
                f"🔄 Reconciler closed zombie signal\n"
                f"*{symbol}* `{sig_id}`\n"
                f"Broker had no matching position for 2 consecutive reconciler "
                f"cycles — engine signal was a zombie.\n"
                f"Approx P&L: `{pnl:+.2f}%` (last-known mark price)\n"
                f"Engine signal removed."
            )
        except Exception as exc:
            log.warning("reconciler_close_signal alert failed: %s", exc)

        self._remove_and_archive(sig_id)

    def _remove_and_archive(self, signal_id: str) -> None:
        """Remove a signal from active tracking and archive it in history."""
        sig = self.router.active_signals.get(signal_id)
        if sig is not None:
            self._signal_history.append(sig)
            self._signal_history = self._signal_history[-500:]
            try:
                save_history(self._signal_history)
            except Exception as exc:
                log.warning(f"signal_history flush failed: {exc}")
        self.router.remove_signal(signal_id)
        self._content_scheduler.update_last_post()

    def _handle_signal_expiry(self, sig: "Signal", now: "datetime") -> None:
        """Finalise an expired signal: P&L, status, archive, broker close, perf.

        Called by ``SignalRouter.cleanup_expired`` BEFORE the signal is popped
        from ``_active_signals`` so the engine can fully terminate it.

        Without this hook, the cleanup path used to silently drop the signal:
        ``_signal_history`` got no entry, the broker stayed open in live/paper
        mode, ``performance_tracker`` got no record, and the Lumin app's
        Closed→Expired sub-filter rendered empty even when subscribers had
        just received an "⏰ Signal Expired" Telegram post.

        Idempotent on retries: re-running on a signal whose ``status`` is
        already a terminal state is a no-op.
        """
        if sig is None:
            return
        existing_status = (getattr(sig, "status", "") or "").upper()
        if existing_status not in {"", "ACTIVE", "TP1_HIT", "TP2_HIT"}:
            # Already terminal (SL_HIT / TP3_HIT / INVALIDATED / EXPIRED /
            # CANCELLED).  cleanup_expired raced with another close path —
            # don't double-archive.
            return

        # No-fill guard: a limit-zone signal whose entry band was never
        # visited has no position — neither the engine book nor any
        # subscriber following the signal filled.  Marking mark-vs-entry
        # P&L on it fabricates a trade that never happened; 36 of the
        # last 100 perf records were such phantoms (2026-07-03 audit),
        # polluting win rates, the scorer band tables, the ops Profit
        # page, and the invalidation audit's PREMATURE counts.
        never_filled = bool(getattr(sig, "entry_never_filled", False))

        # Compute realised P&L from the last-known mark price.  Auto-trade
        # users need an honest close price even when the trade-monitor
        # didn't get to fire its own expiry path (e.g. WebSocket lost
        # the symbol or scanner cleanup_expired won the race).
        entry = float(getattr(sig, "entry", 0.0) or 0.0)
        current_price = float(getattr(sig, "current_price", 0.0) or 0.0)
        if never_filled:
            sig.pnl_pct = 0.0
        elif entry > 0 and current_price > 0:
            try:
                from src.smc import Direction
                if sig.direction == Direction.LONG:
                    sig.pnl_pct = (current_price - entry) / entry * 100.0
                else:
                    sig.pnl_pct = (entry - current_price) / entry * 100.0
            except Exception:
                pass

        sig.status = "EXPIRED"
        sig.terminal_outcome_timestamp = now

        # Invalidation-Quality Audit for the EXPIRY path: record the close so
        # the periodic classifier can later mark it PROTECTIVE / PREMATURE /
        # NEUTRAL from the post-expiry price action — i.e. *after* expiry, did
        # price go on to the would-be SL (expiry saved us) or the would-be TP
        # (expiry surrendered the move). Until now only the thesis-INVALIDATED
        # path was audited, so we had no ground truth on whether the 60-min
        # max-hold expiry nets help or hurt. Best-effort: never break the close.
        # No-fill signals are excluded — PROTECTIVE/PREMATURE semantics assume
        # a position was open to save or kill; a never-filled signal is neither.
        if never_filled:
            log.info(
                "Signal {} {} expired without fill — recorded as "
                "EXPIRED_NO_FILL with zero P&L (no position ever existed)",
                sig.signal_id, sig.symbol,
            )
        else:
            try:
                from src.invalidation_audit import record_invalidation
                record_invalidation(
                    signal_id=sig.signal_id,
                    symbol=sig.symbol,
                    channel=sig.channel,
                    setup_class=sig.setup_class or "",
                    direction=sig.direction.value,
                    entry=entry,
                    stop_loss=float(getattr(sig, "stop_loss", 0.0) or 0.0),
                    tp1=float(getattr(sig, "tp1", 0.0) or 0.0),
                    kill_price=current_price,
                    kill_reason="expired",
                    pnl_pct_at_kill=float(getattr(sig, "pnl_pct", 0.0) or 0.0),
                )
            except Exception as exc:  # noqa: BLE001 — audit must never break the close
                log.debug("invalidation_audit.record_invalidation failed (expiry) for {}: {}", sig.symbol, exc)

        # Archive into _signal_history + persist.  Mirrors the work
        # _remove_and_archive does for trade-monitor-driven closes.
        self._signal_history.append(sig)
        self._signal_history = self._signal_history[-500:]
        try:
            save_history(self._signal_history)
        except Exception as exc:
            log.warning(f"signal_history flush failed (expiry): {exc}")

        # Stamp a perf-tracker record so the win-rate / aggregate stats
        # include this expiry.  outcome_label="EXPIRED" matches what
        # trade_monitor's expiry path produces post-PR-#305; no-fill
        # signals get "EXPIRED_NO_FILL" with zero P&L so stats consumers
        # can separate real held-position expiries from non-trades.
        # Lifecycle timestamps are passed through (tolerating the ISO-string
        # form a restart-restored Signal may carry) — their absence on
        # router-swept expiries is what made the phantom records so hard
        # to attribute in the truth report.
        def _epoch(val: Any) -> Optional[float]:
            if isinstance(val, datetime):
                return val.timestamp()
            if isinstance(val, str):
                try:
                    return datetime.fromisoformat(val).timestamp()
                except ValueError:
                    return None
            return None

        try:
            if self._performance_tracker is not None:
                _create_ts = _epoch(getattr(sig, "timestamp", None))
                _dispatch_ts = _epoch(getattr(sig, "dispatch_timestamp", None))
                _terminal_ts = _epoch(now)
                self._performance_tracker.record_outcome(
                    signal_id=sig.signal_id,
                    channel=sig.channel,
                    symbol=sig.symbol,
                    direction=sig.direction.value,
                    entry=sig.entry,
                    hit_tp=0,
                    hit_sl=False,
                    pnl_pct=getattr(sig, "pnl_pct", 0.0) or 0.0,
                    outcome_label="EXPIRED_NO_FILL" if never_filled else "EXPIRED",
                    confidence=getattr(sig, "confidence", 0.0) or 0.0,
                    setup_class=getattr(sig, "setup_class", "") or "",
                    quality_tier=getattr(sig, "quality_tier", "B") or "B",
                    stop_loss=float(getattr(sig, "stop_loss", 0.0) or 0.0),
                    create_timestamp=_create_ts,
                    dispatch_timestamp=_dispatch_ts,
                    terminal_outcome_timestamp=_terminal_ts,
                    create_to_terminal_sec=(
                        max(_terminal_ts - _create_ts, 0.0)
                        if _create_ts is not None and _terminal_ts is not None
                        else None
                    ),
                    max_favorable_excursion_pct=float(
                        getattr(sig, "max_favorable_excursion_pct", 0.0) or 0.0
                    ),
                    max_adverse_excursion_pct=float(
                        getattr(sig, "max_adverse_excursion_pct", 0.0) or 0.0
                    ),
                )
        except Exception as exc:
            log.warning(f"perf_tracker record_outcome failed (expiry): {exc}")

        # Close any broker-side position so auto-trade doesn't bleed an
        # orphan after the engine has stopped tracking.  Best-effort —
        # PositionReconciler is the safety net for any failure here.
        if self._order_manager is not None and getattr(
            self._order_manager, "is_enabled", False
        ):
            try:
                import asyncio as _asyncio
                _task = _asyncio.get_running_loop().create_task(
                    self._order_manager.close_full(
                        sig, reason="expired", current_price=current_price or None
                    )
                )
                # Money path: hold a strong ref so GC can't cancel the close
                # mid-flight (the loop's WeakSet is not ownership).
                self._expiry_close_tasks.add(_task)
                _task.add_done_callback(self._expiry_close_tasks.discard)
            except RuntimeError:
                # No running loop (test path or sync caller) — skip the
                # async broker close.  The reconciler will catch the orphan.
                pass
            except Exception as exc:
                log.warning(f"order_manager.close_full failed (expiry): {exc}")

    # ------------------------------------------------------------------
    # Auto-execution mode runtime control (Telegram /automode command)
    # ------------------------------------------------------------------

    def get_auto_execution_status(self) -> Dict[str, Any]:
        """Snapshot of the current auto-trade state for the /automode command."""
        rm = self._risk_manager
        om = self._order_manager
        info: Dict[str, Any] = {
            "mode": self._current_auto_mode,
            "open_positions": rm.open_position_count if rm is not None else 0,
            "daily_pnl_usd": rm.daily_realised_pnl_usd if rm is not None else 0.0,
            "daily_loss_pct": rm.daily_loss_pct if rm is not None else 0.0,
            "daily_kill_tripped": rm.daily_kill_tripped if rm is not None else False,
            "manual_paused": rm.manual_paused if rm is not None else False,
            "current_equity_usd": rm.current_equity_usd if rm is not None else 0.0,
        }
        # Paper mode exposes simulated PnL.
        if hasattr(om, "simulated_pnl_total"):
            info["simulated_pnl_usd"] = om.simulated_pnl_total
        return info

    def get_background_task_census(self) -> List[str]:
        """Live asyncio task names in this process.

        Single-process mode serves ``/internal/diag/tasks`` straight from
        here. Mirrors :meth:`RedisEngineFacade.get_background_task_census` so
        the endpoint is mode-agnostic. Must be called from an async context
        (a running event loop) — the diag endpoint is.
        """
        return sorted(
            t.get_name() for t in asyncio.all_tasks() if not t.done()
        )

    def _build_paper_order_manager(self):
        """Construct the paper-mode order manager.

        Two fully-wired implementations selected by ``PAPER_PER_USER_BOOKS``
        (an operational kill switch, not a dark flag):

        * OFF (default) → one shared :class:`PaperOrderManager` writing the
          engine-wide ``paper`` pnl bucket — the pre-2026-06-20 behaviour.
        * ON → :class:`PaperBookFanout` over a per-user
          :class:`PaperBookRegistry`: one book per ``user_id``, each with its
          own equity, ``paper:<uid>`` pnl bucket, trades DB, and its OWN
          RiskManager so one user's daily-loss breaker never trips another's.

        Both share ``self._risk_manager`` semantics: the shared book uses the
        engine-level manager; per-user books get a fresh manager each so the
        read API can attribute risk per user.
        """
        if not PAPER_PER_USER_BOOKS:
            return PaperOrderManager(
                position_size_pct=POSITION_SIZE_PCT,
                max_position_usd=MAX_POSITION_USD,
                starting_equity_usd=RISK_STARTING_EQUITY_USD,
                risk_manager=self._risk_manager,
            )

        def _risk_manager_factory(_uid: int) -> RiskManager:
            return RiskManager(
                starting_equity_usd=RISK_STARTING_EQUITY_USD,
                daily_loss_limit_pct=RISK_DAILY_LOSS_LIMIT_PCT,
                max_concurrent=RISK_MAX_CONCURRENT,
                max_leverage=RISK_MAX_LEVERAGE,
                min_equity_usd=RISK_MIN_EQUITY_USD,
                setup_blacklist=set(RISK_SETUP_BLACKLIST),
                mode="paper",
            )

        registry = PaperBookRegistry(
            books_dir=PAPER_BOOKS_DIR,
            starting_equity_usd=RISK_STARTING_EQUITY_USD,
            position_size_pct=POSITION_SIZE_PCT,
            max_position_usd=MAX_POSITION_USD,
            risk_manager_factory=_risk_manager_factory,
        )
        self._paper_book_registry = registry
        log.info(
            "Auto-execution mode: PAPER (per-user books ON — fanout over "
            "PaperBookRegistry, books_dir=%s)",
            PAPER_BOOKS_DIR,
        )
        return PaperBookFanout(registry)

    async def take_signal_for_user(
        self, firebase_uid: str, signal_id: str
    ) -> Dict[str, Any]:
        """Manual take (owner-approved 2026-07-17): place ONE active signal
        for ONE user who explicitly tapped "Take trade" in the app.

        Resolves the live ``Signal`` from the router's active book (the
        engine is the source of truth — API-side snapshot pre-validation
        can be up to 60 s stale) and hands the geometry to
        :func:`signal_dispatch.dispatch_signal_to_uid_manual`, which runs
        the same sizing / tripwire / FSM safety-gate / dispatch-log path
        as the auto fan-out.  Returns the result dict the API relays to
        the app.  Called directly in single-process mode; via the
        ManualTakeConsumer (Redis queue) in isolated mode.
        """
        from config import AUTO_TRADE_MANUAL_TAKE_ENABLED as _take_on
        if not _take_on:
            return {
                "outcome": "rejected",
                "reject_class": "ManualTakeDisabled",
                "reject_detail": (
                    "Server-side take is disabled on this engine "
                    "(AUTO_TRADE_MANUAL_TAKE_ENABLED=false)."
                ),
                "signal_id": signal_id,
            }
        signal = self.router.active_signals.get(signal_id)
        if signal is None:
            return {
                "outcome": "rejected",
                "reject_class": "SignalNotFound",
                "reject_detail": (
                    "This signal is no longer in the active book — it "
                    "closed or expired."
                ),
                "signal_id": signal_id,
            }
        from src.api.snapshot import _TERMINAL_STATUSES
        if getattr(signal, "status", "ACTIVE") in _TERMINAL_STATUSES:
            return {
                "outcome": "rejected",
                "reject_class": "SignalClosed",
                "reject_detail": (
                    f"This signal already closed "
                    f"({getattr(signal, 'status', '?')}) — taking it now "
                    f"would enter without the setup."
                ),
                "signal_id": signal_id,
            }
        from src.execution import signal_dispatch as _sd
        return await _sd.dispatch_signal_to_uid_manual(
            uid=firebase_uid,
            signal_id=signal.signal_id,
            symbol=signal.symbol,
            direction=signal.direction.value,
            entry_price=float(signal.entry),
            sl_price=float(signal.stop_loss),
            tp1_price=float(signal.tp1),
            tp2_price=float(signal.tp2),
            tp3_price=float(signal.tp3),
            regime_label=getattr(signal, "entry_regime", None),
            regime_label_15m=getattr(signal, "entry_regime_15m", None),
            atr_percentile=getattr(signal, "atr_percentile_at_entry", 50.0),
            atr_value=getattr(signal, "atr_value_at_entry", 0.0),
            setup_class=getattr(signal, "setup_class", None),
        )

    async def close_signal_admin(self, signal_id: str) -> Dict[str, Any]:
        """Owner force-close of ONE active signal (ops "Close" button).

        For a signal stuck OPEN that the exit machinery never resolved.
        Delegates to :meth:`TradeMonitor.close_signal_manual`, which reuses the
        expiry-close primitives (realise-or-zero PnL, record outcome, flatten
        any broker position, remove from the active book).  Owner-gated at the
        route.  Called directly in single-process mode; via the shared manual
        command consumer (Redis, ``kind="close"``) in isolated mode.
        """
        signal_id = str(signal_id or "").strip()
        if not signal_id:
            return {"closed": False, "signal_id": signal_id, "reason": "missing_id"}
        try:
            return await self.monitor.close_signal_manual(
                signal_id, reason="manual_close"
            )
        except Exception as exc:  # never leak an exception to the API bridge
            log.exception("close_signal_admin failed for %s", signal_id)
            return {"closed": False, "signal_id": signal_id, "reason": f"error: {exc}"}

    async def build_manual_trade_for_user(
        self, firebase_uid: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manual trade builder — place ONE user-directed trade the user built
        on the chart (entry_type + slid entry + optional SL/TP) on their
        server-connected key.

        Hands the geometry to ``signal_dispatch.dispatch_manual_trade``, which
        runs the same sizing / tripwire / place_signal safety-gate / dispatch_log
        path as auto-trade, with ``protection_mode="user_owned"`` (SL optional).
        Called directly in single-process mode; via the ManualTakeConsumer
        (Redis queue) in isolated mode. Returns the result dict the API relays.
        """
        from src import runtime_tunables as _rt
        if not bool(_rt.get("manual_trade_builder_enabled")):
            return {
                "outcome": "rejected",
                "reject_class": "ManualTradeBuilderDisabled",
                "reject_detail": (
                    "The manual trade builder is disabled on this engine "
                    "(MANUAL_TRADE_BUILDER_ENABLED=false)."
                ),
                "ref_id": payload.get("ref_id"),
            }
        from src.execution import signal_dispatch as _sd
        return await _sd.dispatch_manual_trade(
            uid=firebase_uid,
            ref_id=str(payload.get("ref_id") or ""),
            symbol=str(payload.get("symbol") or ""),
            direction=str(payload.get("direction") or ""),
            entry_type=str(payload.get("entry_type") or "market"),
            entry_price=float(payload.get("entry_price") or 0.0),
            sl_price=float(payload.get("sl_price") or 0.0),
            tp_prices=[float(p) for p in (payload.get("tp_prices") or [])],
            valid_for_minutes=int(payload.get("valid_for_minutes") or 0),
        )

    def set_auto_execution_mode(self, new_mode: str) -> Tuple[bool, str]:
        """Switch auto-execution mode at runtime.

        Returns ``(success, message)``.  On success the engine's order_manager
        and risk_manager are torn down and rebuilt for the new mode, and the
        TradeMonitor's reference is updated so the lifecycle loop picks up
        the new manager on its next tick.

        Safety gates:
          * Mode must be one of off/paper/live
          * No mode change while open positions exist (would orphan them)
          * Live mode requires EXCHANGE_API_KEY + EXCHANGE_API_SECRET set

        Persistence: this is ephemeral.  AUTO_EXECUTION_MODE env still
        determines mode at the next engine boot; runtime changes don't
        survive a restart.
        """
        new_mode = (new_mode or "").strip().lower()
        if new_mode not in {"off", "paper", "live"}:
            return False, f"invalid mode {new_mode!r} — must be off / paper / live"
        if new_mode == self._current_auto_mode:
            return False, f"already in {new_mode.upper()} mode — nothing to do"

        # Refuse if there are open positions (would orphan tracking).
        if self._risk_manager is not None and self._risk_manager.open_position_count > 0:
            return (
                False,
                f"refused: {self._risk_manager.open_position_count} open position(s) — close them first",
            )

        # Live mode safety: require credentials.
        if new_mode == "live":
            if not EXCHANGE_API_KEY or not EXCHANGE_API_SECRET:
                return (
                    False,
                    "live mode refused: EXCHANGE_API_KEY and EXCHANGE_API_SECRET must be set in env",
                )

        previous = self._current_auto_mode
        log.info("Auto-execution mode runtime change: %s → %s", previous, new_mode)

        # Tear down exchange client + reconciler (live-only resources).
        if self._exchange_client is not None:
            try:
                # Best-effort close — schedule but don't await (not in async context here).
                asyncio.create_task(self._exchange_client.close())
            except Exception:
                pass
            self._exchange_client = None
        self._position_reconciler = None

        # Build new managers for the requested mode.
        if new_mode == "off":
            self._risk_manager = None
            self._order_manager = OrderManager(
                auto_execution_enabled=False,
                exchange_client=None,
                position_size_pct=POSITION_SIZE_PCT,
                max_position_usd=MAX_POSITION_USD,
                redis_client=self._redis_client,
            )
        elif new_mode == "paper":
            self._risk_manager = RiskManager(
                starting_equity_usd=RISK_STARTING_EQUITY_USD,
                daily_loss_limit_pct=RISK_DAILY_LOSS_LIMIT_PCT,
                max_concurrent=RISK_MAX_CONCURRENT,
                max_leverage=RISK_MAX_LEVERAGE,
                min_equity_usd=RISK_MIN_EQUITY_USD,
                setup_blacklist=set(RISK_SETUP_BLACKLIST),
                mode="paper",
            )
            self._order_manager = self._build_paper_order_manager()
        else:  # new_mode == "live"
            # Same guard as the boot path: refuse the switch loudly when
            # ccxt is absent instead of NotImplementedError on first order.
            from src import exchange_client as _ec_mod
            if not _ec_mod._CCXT_AVAILABLE:
                raise RuntimeError(
                    "auto-mode switch to 'live' requires the ccxt package, "
                    "which is not installed (commented out in "
                    "requirements.txt). Install ccxt or use the server-side "
                    "auto-trade stack instead."
                )
            self._exchange_client = CCXTClient(
                exchange_id=EXCHANGE_ID,
                api_key=EXCHANGE_API_KEY,
                secret=EXCHANGE_API_SECRET,
                sandbox=EXCHANGE_SANDBOX,
            )
            self._risk_manager = RiskManager(
                starting_equity_usd=RISK_STARTING_EQUITY_USD,
                daily_loss_limit_pct=RISK_DAILY_LOSS_LIMIT_PCT,
                max_concurrent=RISK_MAX_CONCURRENT,
                max_leverage=RISK_MAX_LEVERAGE,
                min_equity_usd=RISK_MIN_EQUITY_USD,
                setup_blacklist=set(RISK_SETUP_BLACKLIST),
                mode="live",
            )
            self._order_manager = OrderManager(
                auto_execution_enabled=True,
                exchange_client=self._exchange_client,
                position_size_pct=POSITION_SIZE_PCT,
                max_position_usd=MAX_POSITION_USD,
                risk_manager=self._risk_manager,
                redis_client=self._redis_client,
            )
            self._position_reconciler = PositionReconciler(
                exchange_client=self._exchange_client,
                get_active_signals_fn=lambda: self.router.active_signals,
                alert_callback=self.telegram.send_admin_alert,
                auto_close_orphans=RECONCILER_AUTO_CLOSE_ORPHANS,
                risk_manager=self._risk_manager,
            )

        # Wire the new order_manager into TradeMonitor so the lifecycle
        # loop picks it up on the next poll.
        self.monitor._order_manager = self._order_manager

        self._current_auto_mode = new_mode
        return True, f"auto-execution mode changed: {previous.upper()} → {new_mode.upper()}"

    def full_signal_reset(self) -> dict:
        """Clear all signal state engine-side: active signals, history, stats, invalidation records.

        Called directly in single-process mode; called by SnapshotWriter when a
        KEY_CMD_RESET_SIGNALS Redis command arrives in isolated mode.

        Does NOT touch broker positions — paper close-all is handled by the API
        container (which owns the PaperOrderManager in both modes).
        """
        import json as _json
        from pathlib import Path as _Path
        from src.signal_history_store import save_history as _save_history

        result: dict = {
            "cleared_active_signals": 0,
            "cleared_history": 0,
            "cleared_perf_stats": 0,
            "cleared_invalidation_records": 0,
        }

        # 1. Active signals — clear the router's in-flight map.
        router = getattr(self, "router", None)
        if router is not None and hasattr(router, "active_signals"):
            try:
                result["cleared_active_signals"] = len(router.active_signals)
                router.active_signals.clear()
            except Exception:
                pass

        # 2. Signal history — clear in-memory + flush empty list to disk.
        try:
            result["cleared_history"] = len(self._signal_history)
            self._signal_history.clear()
            _save_history(self._signal_history)
        except Exception:
            pass

        # 3. Performance stats.
        pt = getattr(self, "_performance_tracker", None)
        if pt is not None and hasattr(pt, "reset_stats"):
            try:
                result["cleared_perf_stats"] = pt.reset_stats(channel=None)
            except Exception:
                pass

        # 4. Invalidation records — overwrite with empty array.
        inv_path = _Path("data/invalidation_records.json")
        if inv_path.exists():
            try:
                existing = _json.loads(inv_path.read_text(encoding="utf-8"))
                result["cleared_invalidation_records"] = len(existing) if isinstance(existing, list) else 0
            except Exception:
                pass
            try:
                inv_path.write_text("[]", encoding="utf-8")
            except Exception:
                pass

        return result

    def _get_engine_context(self) -> dict:
        """Return a snapshot of current engine state for content generation."""
        regime = "RANGING"
        try:
            r = self._regime_detector.get_regime("BTCUSDT")
            regime = r.regime.value if r else "RANGING"
        except Exception:
            pass

        perf = {}
        try:
            stats = self._performance_tracker.get_stats()
            perf = {
                "wins_this_week": getattr(stats, "wins_7d", 0),
                "losses_this_week": getattr(stats, "losses_7d", 0),
                "avg_rr_this_week": getattr(stats, "avg_rr_7d", 0.0),
                "best_symbol_this_week": getattr(stats, "best_symbol_7d", "—"),
                "best_r_this_week": getattr(stats, "best_r_7d", 0.0),
                "worst_symbol_this_week": getattr(stats, "worst_symbol_7d", ""),
                "worst_r_this_week": getattr(stats, "worst_r_7d", 0.0),
                "month_winrate": getattr(stats, "winrate_30d", 0.0),
                "streak_label": "",
            }
        except Exception:
            pass

        top_pairs = list(self.pair_mgr.symbols)[:5] if self.pair_mgr.symbols else []
        signals_today = len(
            [s for s in self._signal_history if s is not None]
        )

        btc_price: Union[str, float] = "—"
        btc_change_pct: float = 0.0
        btc_1h_change_pct: float = 0.0
        try:
            btc_cd = self.data_store.get_candles("BTCUSDT", "5m") or {}
            # numpy-truthiness class (2026-07-14): `dict.get("close")` is an
            # ndarray — bool context raises, and the except below blanked the
            # BTC price in this payload forever.
            closes = btc_cd.get("close")
            if closes is not None and len(closes) > 0:
                btc_price = round(float(closes[-1]), 2)
                if len(closes) >= 12:
                    btc_1h_change_pct = round(
                        (float(closes[-1]) / float(closes[-12]) - 1) * 100, 2
                    )  # 12×5m = 1h
                if len(closes) >= 289:
                    btc_change_pct = round(
                        (float(closes[-1]) / float(closes[-289]) - 1) * 100, 2
                    )  # 288×5m ≈ 24h
        except Exception:
            pass

        return {
            "regime": regime,
            "btc_price": btc_price,
            "btc_change_pct": btc_change_pct,
            "btc_1h_change_pct": btc_1h_change_pct,
            "top_pairs": top_pairs,
            "signals_today": signals_today,
            "performance": perf,
            "key_level": "—",
            "hours_since_signal": 0,
            "is_active_market": False,
        }

    def _get_scanner_context(self) -> dict:
        """Return a scanner context snapshot for the radar channel evaluator."""
        return {
            "channel_scores": getattr(self._scanner, "_radar_scores", {}),
            "is_active_market": False,
        }

    async def _handle_radar_candidate(
        self,
        symbol: str,
        source_channel: str,
        bias: str,
        setup_name: str,
        waiting_for: str,
        confidence: int,
    ) -> None:
        """Handle a new radar candidate from the scanner.

        Generates a radar_alert message, posts it to the free channel, and
        creates a tracked watch via FreeWatchService.  This is intentionally
        only called for actual radar_alert candidates — market_watch posts
        must NOT flow through here.
        """
        from src.content_engine import generate_content

        # Attempt to create a tracked watch first; if deduplicated, skip posting.
        watch = await self._free_watch_service.create_watch(
            symbol=symbol,
            source_channel=source_channel,
            bias=bias,
            setup_name=setup_name,
            waiting_for=waiting_for,
            confidence=confidence,
        )
        if watch is None:
            # Deduplicated or cooldown — do not re-post the radar alert.
            return

        # Generate and post the free-channel radar alert.
        try:
            ctx = {
                "symbol": symbol,
                "bias": bias,
                "confidence": confidence,
                "waiting_for": waiting_for,
                "setup_name": setup_name,
                "is_active_market": False,
            }
            text = await generate_content("radar_alert", ctx, use_gpt=False)
            if text:
                await self.telegram.post_to_free_channel(text)
        except Exception as exc:
            log.debug("Radar alert post failed for {}: {}", symbol, exc)

    # ------------------------------------------------------------------
    # Pre-flight checks (delegated to Bootstrap)
    # ------------------------------------------------------------------

    async def _preflight_check(self) -> bool:
        """Run pre-flight checks (delegated to Bootstrap)."""
        return await self._bootstrap.preflight_check()

    # ------------------------------------------------------------------
    # Boot / shutdown (delegated to Bootstrap)
    # ------------------------------------------------------------------

    async def boot(self) -> None:
        # Warn operators about misconfigured Telegram channel IDs so that
        # signals are not silently dropped by the signal router.
        for chan_name, chan_id in CHANNEL_TELEGRAM_MAP.items():
            if not chan_id:
                log.warning(
                    "⚠️  STARTUP: Telegram channel ID for '%s' is not configured "
                    "(CHANNEL_TELEGRAM_MAP[%s] is empty). Signals for this channel "
                    "will be silently dropped. Set the corresponding env variable "
                    "in .env before starting the engine.",
                    chan_name, chan_name,
                )
        await self._bootstrap.boot()
        # Sync boot_time to command handler after boot sets it.
        # ``_boot_time`` is monotonic (for uptime); ``_boot_wall_time`` is
        # wall-clock (for ISO display).  Both are used by /diag.
        self._command_handler.boot_time = self._boot_time
        self._command_handler.boot_wall_time = self._boot_wall_time
        # Sync WS managers to command handler after boot starts them
        self._command_handler.ws_futures = self._ws_futures

    async def shutdown(self) -> None:
        if self._shutdown_started:
            return
        self._shutdown_started = True
        await self._bootstrap.shutdown()

    # ------------------------------------------------------------------
    # WebSocket setup (delegated to Bootstrap)
    # ------------------------------------------------------------------

    async def _start_websockets(self) -> None:
        await self._bootstrap.start_websockets()

    # ------------------------------------------------------------------
    # WebSocket message handler
    # ------------------------------------------------------------------

    async def _on_ws_message(self, data: dict) -> None:
        """Handle a WebSocket message (kline, trade, or forceOrder).

        Accepts both Binance payload shapes so the handler is callable from
        the WebSocket transport AND from the REST fallback paths:

        * **Combined-stream wrapper** (``wss://.../stream?streams=...``):
          ``{"stream": "btcusdt@kline_1m", "data": {"e": "kline", ...}}``.
          We unwrap ``data["data"]`` before dispatching.  This is the
          documented Binance format for multi-stream connections and
          what the engine has used since 2026-05-14 (Binance Futures
          tightened parsing of the unofficial ``/ws/<s1>/<s2>/...`` form).

        * **Raw payload** (REST fallback, ``_ws_futures_liq`` if it ever
          reverts to ``/ws`` single-stream, or any future inline test
          path): ``{"e": "kline", "s": "BTCUSDT", ...}`` — used directly.

        Detect by ``"stream"`` in the top level.  If the wrapper is
        present, ``data["data"]`` is the raw payload; otherwise ``data``
        IS the raw payload.
        """
        # All-market ticker array (`!ticker@arr`) — the only stream whose
        # combined-wrapper ``data`` is a *list*, not a dict. Fold it into the
        # mover-ignition detector and enqueue any newly-ignited pairs for the
        # scanner to promote. Kept deliberately cheap (pure arithmetic, no I/O)
        # since it fires once per second across the whole universe.
        if isinstance(data, dict) and isinstance(data.get("data"), list) and "stream" in data:
            ignited = self._mover_ignition.ingest(data["data"])
            for sym, direction in ignited:
                self._mover_ignition_pending[sym] = direction
            return

        # Combined-stream wrapper unwrap.  ``data.get("data")`` is a dict
        # for genuine wrapped events; we sanity-check both keys to avoid
        # mistaking a kline payload (which has no top-level ``stream``)
        # for a wrapper.
        if isinstance(data, dict) and isinstance(data.get("data"), dict) and "stream" in data:
            data = data["data"]
        event = data.get("e")
        symbol = data.get("s", "").upper()

        if event == "kline":
            k = data.get("k", {})
            interval = k.get("i", "")
            candle = {
                "open": float(k.get("o", 0)),
                "high": float(k.get("h", 0)),
                "low": float(k.get("l", 0)),
                "close": float(k.get("c", 0)),
                "volume": float(k.get("v", 0)),
            }
            if k.get("x"):  # candle closed
                self.data_store.update_candle(symbol, interval, candle)
                if interval == "1m":
                    # Drive CVD from kline taker volumes so it works during REST
                    # fallback (which sends kline events but never trade events).
                    # "Q" = taker_buy_quote_asset_volume (USD buys), "q" = total
                    # quote_asset_volume (total USD traded) for the closed candle.
                    _buy_usd = float(k.get("Q", 0.0))
                    _total_usd = float(k.get("q", 0.0))
                    self._order_flow_store.update_cvd_from_tick(
                        symbol, _buy_usd, _total_usd - _buy_usd
                    )
                elif interval == "15m":
                    # 15m CVD aggregation feeds the 15m-aligned divergence detector
                    # (OWNER_BRIEF §3.4a — HTF Structure, LTF Entry).  Each closed
                    # 15m kline carries the same Q/q split as 1m, but the resulting
                    # CVD series is genuinely on a 15m time grid rather than the
                    # interleaved mixed-TF series in `_cvd_candle`.
                    _buy_usd_15m = float(k.get("Q", 0.0))
                    _total_usd_15m = float(k.get("q", 0.0))
                    self._order_flow_store.update_cvd_15m_from_kline(
                        symbol, _buy_usd_15m, _total_usd_15m - _buy_usd_15m
                    )
                    self._order_flow_store.snapshot_cvd_15m_at_candle_close(symbol)
                # Snapshot CVD at candle close to align with OHLCV for divergence detection
                self._order_flow_store.snapshot_cvd_at_candle_close(symbol)

        elif event == "trade":
            tick = {
                "price": float(data.get("p", 0)),
                "qty": float(data.get("q", 0)),
                "isBuyerMaker": data.get("m", False),
                "time": data.get("T", 0),
            }
            self.data_store.append_tick(symbol, tick)
            # CVD is driven from 1m kline taker volumes (see kline handler above)
            # rather than individual ticks so it stays accurate during REST fallback.

        elif event == "forceOrder":
            # Buffer the liquidation event for deferred processing so that a
            # flood of forceOrder messages during a liquidation cascade (e.g.
            # Extreme Fear) does not block the WebSocket message loop and delay
            # PONG updates.  The buffer is drained at the start of each scan
            # cycle via _flush_pending_liquidations().
            order = data.get("o", {})
            liq_sym = order.get("s", "").upper()
            side = order.get("S", "")
            qty = float(order.get("q", 0))
            avg_price = float(order.get("ap") or order.get("p") or 0)
            if liq_sym and side and qty > 0 and avg_price > 0:
                self._pending_liquidations.append(
                    LiquidationEvent(
                        timestamp=time.monotonic(),
                        symbol=liq_sym,
                        side=side,
                        qty=qty,
                        price=avg_price,
                    )
                )

    # ------------------------------------------------------------------
    # Scanner loop (delegated to Scanner)
    # ------------------------------------------------------------------

    def _flush_pending_liquidations(self) -> None:
        """Drain the forceOrder buffer into the OrderFlowStore.

        Called periodically from ``_liquidation_flush_loop`` so liquidation
        events are processed in micro-batches rather than inline on the WS
        message loop.  This prevents event-loop blocking during liquidation
        cascades (e.g. Extreme Fear conditions) that would otherwise delay
        PONG updates and trigger false staleness detections.
        """
        while self._pending_liquidations:
            event = self._pending_liquidations.popleft()
            try:
                self._order_flow_store.add_liquidation(event)
            except Exception as exc:
                log.debug("Failed to add liquidation event: {}", exc)

    async def _liquidation_flush_loop(self) -> None:
        """Flush buffered forceOrder events every 100 ms."""
        while True:
            await asyncio.sleep(0.1)
            self._flush_pending_liquidations()

    async def _scan_loop(self) -> None:
        """Periodic scan over all pairs / channels (delegated to Scanner)."""
        await self._scanner.scan_loop()

    # ------------------------------------------------------------------
    # Free-channel, pair-refresh, snapshot loops
    # ------------------------------------------------------------------

    async def _free_channel_loop(self) -> None:
        """Publish daily performance recap every 24 hours."""
        while True:
            await asyncio.sleep(86_400)
            try:
                await self.router.publish_daily_recap(self._performance_tracker)
            except Exception as exc:
                log.error("Free channel publish error: %s", exc)

    async def _weekly_scoreboard_loop(self) -> None:
        """Publish weekly scoreboard every Sunday at ~00:00 UTC."""
        import datetime
        while True:
            now = datetime.datetime.now(datetime.timezone.utc)
            # Compute seconds until next Sunday 00:00 UTC (weekday 6 = Sunday)
            days_until_sunday = (6 - now.weekday()) % 7
            next_sunday = (now + datetime.timedelta(days=days_until_sunday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            wait_secs = (next_sunday - now).total_seconds()
            # If we are already past or very close to the target time (<60 s), push to
            # the following Sunday to avoid posting multiple times in the same window.
            if wait_secs < 60:
                next_sunday += datetime.timedelta(days=7)
                wait_secs = (next_sunday - now).total_seconds()
            await asyncio.sleep(max(wait_secs, 1))
            try:
                await self.router.publish_scoreboard(self._performance_tracker)
            except Exception as exc:
                log.error("Weekly scoreboard publish error: %s", exc)

    async def _daily_performance_report_loop(self) -> None:
        """Auto-generate an HTML performance report every 24 hours (feature 5)."""
        _REPORT_INTERVAL_SECONDS = 86400  # 24 hours
        while True:
            await asyncio.sleep(_REPORT_INTERVAL_SECONDS)
            try:
                from src.performance_report import generate_html_report
                path = generate_html_report(self._performance_tracker)
                log.info("Daily performance report generated: %s", path)
            except Exception as exc:
                log.error("Daily performance report generation failed: %s", exc)

    def _current_ws_symbol_sets(self) -> tuple[set[str], set[str]]:
        ws_limit = _WS_SYMBOL_LIMIT
        return (
            set(self.pair_mgr.spot_symbols[:ws_limit]),
            set(self.pair_mgr.futures_symbols[:ws_limit]),
        )

    async def _restart_websockets_if_pair_universe_changed(
        self,
        old_spot: set[str],
        old_futures: set[str],
    ) -> None:
        new_spot, new_futures = self._current_ws_symbol_sets()
        if old_spot == new_spot and old_futures == new_futures:
            return

        log.info("Tracked pair universe changed; restarting WebSocket subscriptions")
        if self._ws_futures:
            await self._ws_futures.stop()
            self._ws_futures = None
        if self._ws_futures_liq:
            await self._ws_futures_liq.stop()
            self._ws_futures_liq = None

        await self._bootstrap.start_websockets()
        self._command_handler.ws_futures = self._ws_futures

    async def _pair_refresh_loop(self) -> None:
        """Periodically refresh pairs, seed new ones, and prune removed ones."""
        while True:
            await asyncio.sleep(PAIR_FETCH_INTERVAL_HOURS * 3600)
            try:
                old_spot, old_futures = self._current_ws_symbol_sets()
                if TOP50_FUTURES_ONLY:
                    await self.pair_mgr.refresh_top50_futures(force=True)
                    new_symbols, removed_symbols = [], []
                else:
                    new_symbols, removed_symbols = await self.pair_mgr.refresh_pairs()

                # Handle removed (delisted / dropped) pairs
                if removed_symbols:
                    log.info(
                        "Pair pruning: removed %d pairs from universe",
                        len(removed_symbols),
                    )
                    for sym in removed_symbols:
                        self.data_store.candles.pop(sym, None)
                    await self.telegram.send_admin_alert(
                        f"📉 Pair universe pruned: {len(removed_symbols)} pairs removed "
                        f"(e.g. {', '.join(removed_symbols[:5])})"
                    )

                # Seed new pairs
                if new_symbols:
                    log.info(
                        "Discovered %d new pairs — seeding historical data",
                        len(new_symbols),
                    )
                for sym in new_symbols:
                    info = self.pair_mgr.pairs.get(sym)
                    if info is None:
                        continue
                    try:
                        await self.data_store.seed_symbol(sym, info.market)
                        for tf_name, data in self.data_store.candles.get(sym, {}).items():
                            self.pair_mgr.record_candles(
                                sym, tf_name, len(data.get("close", []))
                            )
                        log.info("Seeded new pair %s (%s, %s)", sym, info.market, info.tier)
                    except Exception as exc:
                        log.error("Failed to seed new pair %s: %s", sym, exc)
                await self._restart_websockets_if_pair_universe_changed(
                    old_spot, old_futures
                )
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.error("Pair refresh loop error: %s", exc)

    async def _snapshot_loop(self) -> None:
        """Periodically save historical data to disk for fast restarts."""
        while True:
            await asyncio.sleep(_SNAPSHOT_INTERVAL_SECONDS)
            try:
                await self.data_store.save_snapshot()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.error("Snapshot save error: %s", exc)

    async def _invalidation_audit_loop(self) -> None:
        """Periodically classify pending invalidation kills as PROTECTIVE /
        PREMATURE / NEUTRAL based on post-kill price action.

        See ``src/invalidation_audit.py``.  Uses 1m candles from the live data
        store; assumes each candle is exactly 60s (close enough for window
        classification — we're labelling buckets, not pricing trades).
        """
        from src.invalidation_audit import classify_pending_records, prune_old_records

        def fetch_ohlc_since(symbol: str, since_ts: float):
            candles = self.data_store.get_candles(symbol, "1m")
            if not candles:
                return None
            highs = candles.get("high")
            lows = candles.get("low")
            closes = candles.get("close")
            if highs is None or lows is None or closes is None:
                return None
            if len(highs) == 0 or len(lows) == 0:
                return None
            now_ts = time.time()
            elapsed_sec = max(0.0, now_ts - since_ts)
            n_candles = int(elapsed_sec // 60) + 1
            if n_candles <= 0:
                return None
            n_candles = min(n_candles, len(highs))
            return {
                "high": list(highs[-n_candles:]),
                "low": list(lows[-n_candles:]),
                "close": list(closes[-n_candles:]),
            }

        while True:
            await asyncio.sleep(300)  # 5 min cadence
            try:
                counters = await asyncio.to_thread(
                    classify_pending_records, fetch_ohlc_since=fetch_ohlc_since
                )
                if counters:
                    log.info("Invalidation audit classified: {}", counters)
                await asyncio.to_thread(prune_old_records, retention_sec=7 * 24 * 3600)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.warning("Invalidation audit loop error: %s", exc)
                continue

            # ── Layer C: shadow-ledger classify + edge-matrix feed ─────────
            # Forward-measures every gate-suppressed candidate (and shadow
            # strategy unit) against the same in-memory 1m candles, then feeds
            # resolved outcomes into the Strategy×Context edge matrix.
            # Observe-only; all errors fail open so the audit loop survives.
            try:
                from src import runtime_tunables as _rt
                if bool(_rt.get("suppression_audit_enabled")):
                    from src import suppression_audit as _sa
                    from src.strategy_edge import (
                        SOURCE_SHADOW,
                        SOURCE_SUPPRESSED,
                        StrategyOutcome,
                        get_strategy_edge_store,
                    )

                    def _feed_edge(rec: dict) -> None:
                        outcome = _sa.candidate_outcome(rec)
                        if not outcome:
                            return
                        _is_shadow_unit = str(
                            rec.get("gate_name", "")
                        ).startswith("shadow_unit")
                        # persist=False: hundreds of records can resolve in
                        # one cycle — one batched save() below, not one full
                        # JSON dump per record (2026-07-13 wedge contributor).
                        _src = SOURCE_SHADOW if _is_shadow_unit else SOURCE_SUPPRESSED
                        get_strategy_edge_store().record(
                            StrategyOutcome(
                                strategy=str(rec.get("setup_class", "")),
                                context_key=str(rec.get("context_key", "")),
                                side=str(rec.get("side", "")),
                                won=bool(outcome.get("won")),
                                pnl_pct=float(outcome.get("pnl_pct", 0.0)),
                                r_multiple=float(outcome.get("r_multiple", 0.0)),
                                mfe_pct=float(outcome.get("mfe_pct", 0.0)),
                                source=_src,
                                gross_r_multiple=outcome.get("gross_r_multiple"),
                            ),
                            persist=False,
                        )
                        # Phase-5 cohort cell: dual-write the same outcome under
                        # the cohort-refined key so the cohort matrix accumulates
                        # in parallel without fragmenting the base cell.
                        _cohort = str(rec.get("pair_cohort", "") or "")
                        if _cohort:
                            from src.pair_cohort import cohort_context_key
                            get_strategy_edge_store().record(
                                StrategyOutcome(
                                    strategy=str(rec.get("setup_class", "")),
                                    context_key=cohort_context_key(
                                        str(rec.get("context_key", "")), _cohort
                                    ),
                                    side=str(rec.get("side", "")),
                                    won=bool(outcome.get("won")),
                                    pnl_pct=float(outcome.get("pnl_pct", 0.0)),
                                    r_multiple=float(outcome.get("r_multiple", 0.0)),
                                    mfe_pct=float(outcome.get("mfe_pct", 0.0)),
                                    source=_src,
                                ),
                                persist=False,
                            )

                    def _classify_suppressed_batch() -> dict:
                        counters = _sa.get_store().classify_pending(
                            fetch_ohlc_since=fetch_ohlc_since,
                            on_classified=_feed_edge,
                        )
                        get_strategy_edge_store().save()
                        return counters

                    # Off the event loop: classification copies candle lists
                    # per record and both stores do sync file writes — a big
                    # backlog on the loop thread starves the scanner + trade
                    # monitor heartbeats (the 2026-07-13 incident class).
                    sa_counters = await asyncio.to_thread(_classify_suppressed_batch)
                    if sa_counters:
                        log.info("Suppression audit classified: {}", sa_counters)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.warning("Suppression audit classify error (fail-open): {}", exc)

            # ── Stop-geometry A/B: classify the FIXED/ATR pair ledger ──────
            # Same forward measure, dedicated store; both arms land in the
            # edge matrix as X@FIXED / X@ATR shadow rows so ops + the truth
            # report show which geometry wins per (strategy, context).
            try:
                from src import runtime_tunables as _rt
                if bool(_rt.get("geometry_ab_enabled")):
                    from src import geometry_ab as _gab
                    from src import suppression_audit as _sa
                    from src.strategy_edge import (
                        SOURCE_SHADOW,
                        StrategyOutcome,
                        get_strategy_edge_store,
                    )

                    def _feed_geometry_edge(rec: dict) -> None:
                        outcome = _sa.candidate_outcome(rec)
                        if not outcome:
                            return
                        get_strategy_edge_store().record(
                            StrategyOutcome(
                                strategy=str(rec.get("setup_class", "")),
                                context_key=str(rec.get("context_key", "")),
                                side=str(rec.get("side", "")),
                                won=bool(outcome.get("won")),
                                pnl_pct=float(outcome.get("pnl_pct", 0.0)),
                                r_multiple=float(outcome.get("r_multiple", 0.0)),
                                mfe_pct=float(outcome.get("mfe_pct", 0.0)),
                                source=SOURCE_SHADOW,
                                gross_r_multiple=outcome.get("gross_r_multiple"),
                            ),
                            persist=False,
                        )

                    def _classify_geometry_batch() -> dict:
                        counters = _gab.get_geometry_store().classify_pending(
                            fetch_ohlc_since=fetch_ohlc_since,
                            on_classified=_feed_geometry_edge,
                        )
                        get_strategy_edge_store().save()
                        return counters

                    gab_counters = await asyncio.to_thread(_classify_geometry_batch)
                    if gab_counters:
                        log.info("Geometry A/B classified: {}", gab_counters)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.warning("Geometry A/B classify error (fail-open): {}", exc)

            # ── Layer A: publish the current global context for ops ────────
            self._publish_market_context()
            # ── Layer D: allocator recommendation (observe-only) ───────────
            self._write_allocator_recommendation()
            # ── Layer G: autonomous emission controller ────────────────────
            # Consumes the gate verdicts + edge matrix and moves the per-strategy
            # emission overrides itself (dark-first, self-promoting). Own cadence
            # guard inside; off-thread so the audit loop never blocks on it.
            try:
                from src import runtime_tunables as _rt
                if bool(_rt.get("emission_controller_enabled")):
                    await asyncio.to_thread(self._emission_controller_cycle)
            except Exception as _ecc_exc:
                from src import fail_open
                fail_open.record("main.emission_controller_cycle", _ecc_exc)
            # ── Feature liveness: output-vs-upstream watchdog (2026-07-14) ─
            try:
                from src import runtime_tunables as _rt
                if bool(_rt.get("feature_liveness_enabled")):
                    if getattr(self, "_feature_liveness", None) is None:
                        self._feature_liveness = self._build_feature_liveness()
                    await asyncio.to_thread(self._feature_liveness.run_cycle)
            except Exception as _fl_exc:
                from src import fail_open
                fail_open.record("main.feature_liveness_cycle", _fl_exc)

    # ------------------------------------------------------------------
    # Autonomous-portfolio observe-only publishers (Layers A + D)
    # ------------------------------------------------------------------

    def _emission_controller_cycle(self) -> None:
        """One Layer-G cycle: read the measured gate verdicts + edge matrix, decide
        per-strategy emission overrides inside the envelope, and commit them to the
        controller store. Own cadence guard (EMISSION_CONTROLLER_INTERVAL_SEC, def
        30 min) so it's independent of the audit-loop tick. Boot-grace counts
        *in-process* cycles so a restart re-enters pure observation. Fail-open:
        any error leaves the last committed overrides untouched."""
        import os as _os
        import time as _t

        from src import runtime_tunables as _rt
        from src import suppression_audit as _sa
        from src.context_emission_policy import PolicyParams
        from src.emission_controller import ControllerBounds, build_inputs, run_cycle
        from src.emission_controller_store import get_emission_controller_store
        from src.strategy_edge import VERDICT_STRONG, get_strategy_edge_store

        now = _t.monotonic()
        interval = float(_os.getenv("EMISSION_CONTROLLER_INTERVAL_SEC", "1800"))
        last = getattr(self, "_emission_controller_last_run", 0.0)
        if last and (now - last) < interval:
            return
        self._emission_controller_last_run = now
        cycles = getattr(self, "_emission_controller_cycles_since_start", 0) + 1
        self._emission_controller_cycles_since_start = cycles

        by_gate = _sa.compute_gate_suppression_metrics(_sa.get_store().records())
        matrix = get_strategy_edge_store().matrix()
        inputs = build_inputs(by_gate=by_gate, matrix=matrix, strong_verdict=VERDICT_STRONG)

        gp = PolicyParams.from_config()
        bounds = ControllerBounds(
            stability_cycles=int(_rt.get("emission_controller_stability_cycles") or 3),
            boot_grace_cycles=int(_rt.get("emission_controller_boot_grace_cycles") or 3),
            min_gate_n=int(_rt.get("emission_controller_min_gate_n") or 40),
            promote_ev_r=float(_rt.get("emission_controller_promote_ev_r") or 0.25),
            max_changes_per_cycle=int(_rt.get("emission_controller_max_changes_per_cycle") or 2),
            min_samples_floor=int(_rt.get("emission_controller_min_samples_floor") or 15),
            min_samples_ceiling=int(gp.min_samples),
        )
        store = get_emission_controller_store()
        # Per-cell tighten signal: the edge of each strategy's unlock-candidate
        # cell, so a min_samples loosening auto-reverts when that specific cell's
        # edge sours (not just the coarse strategy aggregate).
        unlocked_cell_r = {
            s: c["edge"] for s, c in inputs["best_strong_cell"].items() if c.get("edge") is not None
        }
        decision = run_cycle(
            gate_metrics=inputs["gate_metrics"],
            best_strong_cell=inputs["best_strong_cell"],
            strategy_health=inputs["strategy_health"],
            global_params={"suppress_negative": gp.suppress_negative, "min_samples": gp.min_samples},
            prior=store.state,
            bounds=bounds,
            cycles_since_start=cycles,
            unlocked_cell_r=unlocked_cell_r,
        )
        store.commit(decision.state, decision.adjustments)
        self._emission_controller_last_decision_ts = _t.time()
        for a in decision.adjustments:
            tag = "APPLY" if a.applied else "SHADOW"
            log.info(
                "[EMISSION_CONTROLLER:{}] {} {} {}->{} status={} verdict={} ev={} n={} cyc={} ({})",
                tag, a.strategy, a.param, a.old, a.new, a.status, a.verdict,
                a.ev_per_suppression_r, a.n, cycles, a.reason,
            )

    def _build_feature_liveness(self):
        """Wire the feature-liveness probes (2026-07-14 incident response).

        Every probe reads in-memory counters/state only — no network, no
        Firestore, no per-scan cost; the whole registry runs once per 5-min
        audit cycle on a worker thread.  Probes whose feature is disabled by
        its tunable report ``unknown`` (counter → None) so a deliberately-off
        feature never pages.
        """
        import time as _time

        from src import geometry_ab as _gab
        from src import runtime_tunables as _rt
        from src import suppression_audit as _sa
        from src.feature_liveness import (
            FeatureLiveness,
            PredicateProbe,
            RateProbe,
        )
        from src.strategy_edge import get_strategy_edge_store

        fl = FeatureLiveness()

        def _supp_total_raw() -> float:
            return float(_sa.get_store().stamped_total)

        def _geom_total():
            if not bool(_rt.get("geometry_ab_enabled")):
                return None
            return float(_gab.get_geometry_store().stamped_total)

        def _supp_total():
            if not bool(_rt.get("suppression_audit_enabled")):
                return None
            return float(_sa.get_store().stamped_total)

        # THE incident probe: suppression events flow (the same event stream
        # geometry pairs stamp from) while zero pairs land → broken stamping.
        fl.add_rate(RateProbe(
            name="geometry_ab",
            counter=_geom_total,
            upstream=_supp_total_raw,
            min_upstream_delta=10.0,
            min_streak=6,          # 30 min sustained
        ))
        # Suppression stamps themselves vs scanner activity.  Suppressions can
        # be legitimately sparse in a dead market, so the streak is long: six
        # hours of active scanning with zero stamps is the anomaly bar.
        fl.add_rate(RateProbe(
            name="suppression_audit",
            counter=_supp_total,
            upstream=lambda: float(getattr(self._scanner, "_scan_cycle_count", 0)),
            min_upstream_delta=15.0,
            min_streak=72,         # ~6 h
        ))
        # Edge-matrix feed: outcomes lag stamps by the ~1h forward window, so
        # the streak covers 3 h of flowing stamps with zero recorded outcomes.
        fl.add_rate(RateProbe(
            name="strategy_edge",
            counter=lambda: float(get_strategy_edge_store().recorded_total),
            upstream=_supp_total_raw,
            min_upstream_delta=10.0,
            min_streak=36,         # ~3 h
        ))

        def _cep_total():
            # None when the policy is disabled by tunable → probe skips (can't
            # false-page an intentionally-off feature), mirroring _supp_total.
            try:
                if not bool(_rt.get("context_emission_enabled")):
                    return None
            except Exception:
                return None
            return float(getattr(self._scanner, "_context_floor_evaluated_total", 0))

        # Context-adaptive emission policy: candidates reach the emission gate
        # (scanning active) but the policy evaluated zero of them for ~6 h →
        # the Layer-C consumer silently stopped (import broke / params always
        # None).  A live money-path consumer that can flat-line unseen is unfinished.
        fl.add_rate(RateProbe(
            name="context_emission_policy",
            counter=_cep_total,
            upstream=lambda: float(getattr(self._scanner, "_scan_cycle_count", 0)),
            min_upstream_delta=15.0,
            min_streak=72,         # ~6 h
        ))

        def _ec_health():
            # Layer G: the controller must keep cycling once enabled. A money-path
            # tuner that silently stops (import broke / loop wedged) would freeze
            # the overrides at a stale snapshot — surfaced, never swallowed.
            if not bool(_rt.get("emission_controller_enabled")):
                return True, "disabled by tunable"
            ts = getattr(self, "_emission_controller_last_decision_ts", 0.0)
            if not ts:
                return True, "no cycle yet (boot)"
            age = _time.time() - ts
            interval = float(__import__("os").getenv("EMISSION_CONTROLLER_INTERVAL_SEC", "1800"))
            if age > 3 * interval:
                return False, f"no controller cycle in {age:.0f}s"
            try:
                from src.emission_controller_store import get_emission_controller_store
                live = len(get_emission_controller_store().active_overrides())
            except Exception:
                live = -1
            return True, f"last cycle {age:.0f}s ago; live_overrides={live}"

        fl.add_predicate(PredicateProbe(name="emission_controller", fn=_ec_health, min_streak=6))

        def _mc_health():
            if not bool(_rt.get("market_context_enabled")):
                return True, "disabled by tunable"
            ts = getattr(self, "_last_market_context_publish_ts", 0.0)
            age = _time.time() - ts
            if age > 900:
                return False, f"context publish stale {age:.0f}s"
            if getattr(self, "_last_atr_percentile", None) is None:
                # Victim #2's exact signature: publishing, but the volatility
                # input silently degraded to the fail-neutral default.
                return False, "atr_percentile None in latest build"
            return True, "publishing with ATR percentile"

        fl.add_predicate(PredicateProbe(name="market_context", fn=_mc_health, min_streak=6))

        _shadow_t0 = _time.monotonic()

        def _shadow_health():
            if not bool(_rt.get("shadow_strategies_enabled")):
                return True, "disabled by tunable"
            stamps = getattr(self._scanner, "_shadow_last_stamp", {}) or {}
            now_m = _time.monotonic()
            if not stamps:
                if now_m - _shadow_t0 < 86400:
                    return True, "no stamps yet (uptime < 24h)"
                return False, "zero shadow stamps in 24h of uptime"
            age = now_m - max(stamps.values())
            if age > 86400:
                return False, f"last shadow stamp {age / 3600:.1f}h ago"
            return True, f"last shadow stamp {age / 60:.0f}m ago"

        fl.add_predicate(PredicateProbe(name="shadow_units", fn=_shadow_health, min_streak=6))

        def _coverage():
            pairs = getattr(self.pair_mgr, "pairs", {}) or {}
            syms = list(pairs.keys())
            if not syms:
                return False, "no universe symbols"
            ok_n = 0
            for s in syms:
                cd = self.data_store.get_candles(s, "15m") or {}
                closes = cd.get("close")
                if closes is not None and len(closes) >= 20:
                    ok_n += 1
            frac = ok_n / len(syms)
            return frac >= 0.7, f"{ok_n}/{len(syms)} symbols with ≥20 15m candles"

        fl.add_predicate(PredicateProbe(name="candle_coverage", fn=_coverage, min_streak=6))

        def _btc_ref():
            cd = self.data_store.get_candles("BTCUSDT", "5m") or {}
            closes = cd.get("close")
            if closes is None or len(closes) == 0:
                return False, "BTCUSDT 5m closes missing"
            px = float(closes[-1])
            return px > 0, f"BTC ref {px:.2f}"

        fl.add_predicate(PredicateProbe(name="btc_reference", fn=_btc_ref, min_streak=6))

        # MEAN_REVERT live path (2026-07-15): the evaluator shares its
        # detection function with the SHADOW_MEAN_REVERT shadow unit, so
        # shadow stamps flowing while the evaluator detects zero = dead live
        # wiring (allowed_evaluators regression, dispatch-list drop, import
        # failure), not a quiet market.  ~6 h streak: the z-trigger fires far
        # less often than raw suppressions, so the bar is deliberately long.
        def _mean_revert_detections():
            if not bool(_rt.get("mean_revert_live")):
                return None
            total = 0.0
            for ch in getattr(self._scanner, "channels", []) or []:
                total += float(getattr(ch, "_mean_revert_detections", 0) or 0)
            return total

        def _shadow_stamp_total() -> float:
            stamps = getattr(self._scanner, "_shadow_stamp_total", None)
            if stamps is not None:
                return float(stamps)
            return float(_sa.get_store().stamped_total)

        fl.add_rate(RateProbe(
            name="mean_revert_path",
            counter=_mean_revert_detections,
            upstream=_shadow_stamp_total,
            min_upstream_delta=30.0,
            min_streak=72,         # ~6 h
        ))

        # MEAN_REVERT emissions vs detections (2026-07-16): the detection
        # probe above stayed green while execution_quality_check rejected
        # 300/300 candidates — a generated-but-fully-gated path is invisible
        # to it.  This probe tracks the detection backlog since the LAST
        # emission; once ≥60 detections accrue with zero emissions the probe
        # violates and pages after the streak window.  A page here means:
        # read the gate rejection reasons, not the evaluator.  (RateProbe is
        # unsuitable: MEAN_REVERT detections are sparse per 5-min cycle and
        # any quiet cycle would reset its streak.)
        _mr_emit_state: Dict[str, Optional[float]] = {"emit": None, "det": None}

        def _mean_revert_emission_health():
            if not bool(_rt.get("mean_revert_live")):
                return True, "disabled by tunable"
            det = _mean_revert_detections() or 0.0
            emit = float(getattr(self._scanner, "_mean_revert_emitted_total", 0) or 0)
            if _mr_emit_state["emit"] is None or emit != _mr_emit_state["emit"]:
                _mr_emit_state["emit"] = emit
                _mr_emit_state["det"] = det
                return True, f"emitted_total={emit:g}"
            backlog = det - (_mr_emit_state["det"] or 0.0)
            if backlog >= 60:
                return False, (
                    f"{backlog:g} detections since last emission "
                    f"(emitted_total={emit:g}) — check gate rejections"
                )
            return True, f"backlog {backlog:g} detections since last emission"

        fl.add_predicate(PredicateProbe(
            name="mean_revert_emission",
            fn=_mean_revert_emission_health,
            min_streak=6,
        ))

        # RANGE_FADE live path (2026-07-18): same two-probe contract as
        # MEAN_REVERT above — a detection probe against the shadow unit's
        # stamp rate (dead live wiring), and an emission-backlog probe
        # (generated-but-fully-gated).  One structural difference: the
        # context-edge gate legitimately blocks RANGE_FADE for hours at a
        # time (only STRONG-verdict context cells emit), so a context block
        # counts as path-alive in the emission probe — otherwise every long
        # non-STRONG stretch would page a healthy gate.
        def _range_fade_detections():
            if not bool(_rt.get("range_fade_live")):
                return None
            total = 0.0
            for ch in getattr(self._scanner, "channels", []) or []:
                total += float(getattr(ch, "_range_fade_detections", 0) or 0)
            return total

        fl.add_rate(RateProbe(
            name="range_fade_path",
            counter=_range_fade_detections,
            upstream=_shadow_stamp_total,
            min_upstream_delta=30.0,
            min_streak=72,         # ~6 h — edge touches are sparse
        ))

        _rf_emit_state: Dict[str, Optional[float]] = {"prog": None, "det": None}

        def _range_fade_emission_health():
            if not bool(_rt.get("range_fade_live")):
                return True, "disabled by tunable"
            det = _range_fade_detections() or 0.0
            emitted = float(
                getattr(self._scanner, "_range_fade_emitted_total", 0) or 0
            )
            blocked = float(
                getattr(self._scanner, "_range_fade_context_blocked_total", 0) or 0
            )
            progress = emitted + blocked
            if _rf_emit_state["prog"] is None or progress != _rf_emit_state["prog"]:
                _rf_emit_state["prog"] = progress
                _rf_emit_state["det"] = det
                return True, (
                    f"emitted_total={emitted:g} context_blocked={blocked:g}"
                )
            backlog = det - (_rf_emit_state["det"] or 0.0)
            if backlog >= 60:
                return False, (
                    f"{backlog:g} detections since last emission/context-block "
                    f"(emitted_total={emitted:g} context_blocked={blocked:g}) "
                    "— check gate rejections"
                )
            return True, f"backlog {backlog:g} detections since last progress"

        fl.add_predicate(PredicateProbe(
            name="range_fade_emission",
            fn=_range_fade_emission_health,
            min_streak=6,
        ))

        # Tuned-variant pipeline (2026-07-16, tune-don't-disable): the residue
        # seen − stamped − skipped grows only on silent pipeline failures
        # (uncomputable ATR arms, store rejects) — by-design skips (cooldown,
        # VSB extension filter) are excluded.  MAS/VSB candidates are rare, so
        # the bar is low but the streak requirement still filters blips.
        def _tuned_variants_health():
            if not bool(_rt.get("tuned_variants_enabled")):
                return True, "disabled by tunable"
            from src import tuned_variants as _tv
            c = _tv.counters()
            residue = c["seen"] - c["stamped"] - c["skipped"]
            detail = (
                f"seen={c['seen']} stamped={c['stamped']} skipped={c['skipped']}"
            )
            if residue >= 10:
                return False, f"{residue} unexplained non-stamps ({detail})"
            return True, detail

        fl.add_predicate(PredicateProbe(
            name="tuned_variants",
            fn=_tuned_variants_health,
            min_streak=6,
        ))

        # Auto-dispatch fan-out (2026-07-18, "auto trade not happening to
        # anyone"): every per-user gate skip in signal_dispatch is silent by
        # design, so a fleet-wide skip blackout (tier lapse for all, mode
        # resolution breakage) — or an empty keyed-user roster (keystore
        # offline) — produced zero orders AND zero telemetry.  The pure
        # predicate lives next to the counters it reads
        # (signal_dispatch.auto_dispatch_health_check); gap is measured in
        # fan-outs, not cycles, so sparse signals never page and a blackout
        # can't hide between cycles.  min_streak=3: the gap condition itself
        # already encodes "sustained".
        from src.execution import signal_dispatch as _sd_liveness
        _auto_dispatch_state: Dict[str, Optional[float]] = {}

        fl.add_predicate(PredicateProbe(
            name="auto_dispatch",
            fn=lambda: _sd_liveness.auto_dispatch_health_check(
                _auto_dispatch_state
            ),
            min_streak=3,
        ))
        return fl

    def _build_global_market_context(self):
        """Current global (BTC-anchored) MarketContext.  Every input is
        fail-neutral, so a cold feed yields a coarser vector, never an error.
        All reads are in-memory (data store / cached BTC-State) — this runs on
        the 5-min audit loop, not any hot path.
        """
        from src.market_context import build_market_context

        regime_label = None
        try:
            r = self._regime_detector.get_regime("BTCUSDT")
            regime_label = r.regime.value if r else None
        except Exception:
            pass
        htf_prior = None
        atr_pctile = None
        try:
            import numpy as _np

            from src.indicators import atr as _atr
            from src.regime import atr_percentile as _atr_pctile
            from src.regime import detect_regime_from_arrays

            # The data store holds numpy arrays — `arr or []` raises ValueError
            # on multi-element arrays and silently zeroed atr_pctile/htf_prior
            # since #721 (same defect class as the geometry-A/B stamp bug).
            c15 = self.data_store.get_candles("BTCUSDT", "15m") or {}
            closes = _np.asarray(c15.get("close", []), dtype=_np.float64)
            if len(closes) >= 30:
                highs = _np.asarray(c15.get("high", closes), dtype=_np.float64)
                lows = _np.asarray(c15.get("low", closes), dtype=_np.float64)
                atr_series = _atr(highs, lows, closes)
                valid = atr_series[~_np.isnan(atr_series)]
                if len(valid) > 0:
                    atr_pctile = _atr_pctile(valid)
            c1h = self.data_store.get_candles("BTCUSDT", "1h") or {}
            h_closes = _np.asarray(c1h.get("close", []), dtype=_np.float64)
            if len(h_closes) >= 30:
                h_highs = _np.asarray(c1h.get("high", h_closes), dtype=_np.float64)
                h_lows = _np.asarray(c1h.get("low", h_closes), dtype=_np.float64)
                h_vols = _np.asarray(
                    c1h.get("volume", _np.zeros(len(h_closes))), dtype=_np.float64
                )
                htf_prior = detect_regime_from_arrays(
                    h_closes, h_highs, h_lows, h_vols, idx=len(h_closes) - 1
                )
        except Exception as _mc_exc:
            from src import fail_open
            fail_open.record("main.global_market_context_inputs", _mc_exc)
        # Stash the raw percentile for the liveness probe + published payload —
        # a None here for 30+ min with warm candles is exactly victim #2.
        self._last_atr_percentile = atr_pctile
        funding = None
        try:
            funding = self._order_flow_store.get_funding_rate("BTCUSDT")
        except Exception:
            pass
        btc_b = None
        try:
            btc_b = float(self._scanner._get_btc_state_cached().get("b", 0.0))
        except Exception:
            pass
        return build_market_context(
            regime_label=regime_label,
            htf_trend_prior=htf_prior,
            atr_percentile=atr_pctile,
            funding_rate=funding,
            btc_state=btc_b,
        )

    @staticmethod
    def _atomic_write_json(path: str, payload: dict) -> None:
        import json

        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        os.replace(tmp, path)

    def _publish_market_context(self) -> None:
        """Write ``data/market_context.json`` — the ops Strategy Lab's context
        card + the strategy-affinity registry (single source of truth).
        One small file write per 5-min cycle; fail-open.
        """
        try:
            from src import runtime_tunables as _rt
            if not bool(_rt.get("market_context_enabled")):
                return
            from src.strategy_portfolio import build_context_payload

            payload = build_context_payload(self._build_global_market_context())
            # Raw ATR percentile rides along so the liveness probe (and ops)
            # can tell "volatility=NORMAL because calm" from "NORMAL because
            # the input silently died" — victim #2's blind spot (2026-07-14).
            payload["atr_percentile_raw"] = self._last_atr_percentile
            path = os.environ.get("MARKET_CONTEXT_PATH", "data/market_context.json")
            self._atomic_write_json(path, payload)
            self._last_market_context_publish_ts = time.time()
        except Exception as exc:
            from src import fail_open
            fail_open.record("main.publish_market_context", exc)

    def _write_allocator_recommendation(self) -> None:
        """Layer D in recommendation mode: persist what the allocator WOULD
        activate/weight in the current context, from the measured edge matrix.
        Nothing consumes this — it exists so the owner can watch the
        allocator's judgement on real data in ops before ever arming it.
        """
        try:
            from src import runtime_tunables as _rt
            if not bool(_rt.get("allocator_recommend_enabled")):
                return
            from src.strategy_allocator import build_recommendation_payload
            from src.strategy_edge import get_strategy_edge_store

            mc = self._build_global_market_context()
            payload = build_recommendation_payload(
                context_key=mc.context_key(),
                matrix=get_strategy_edge_store().matrix(),
            )
            path = os.environ.get(
                "STRATEGY_ALLOCATIONS_PATH", "data/strategy_allocations.json"
            )
            self._atomic_write_json(path, payload)
        except Exception as exc:
            from src import fail_open
            fail_open.record("main.allocator_recommendation", exc)

    # ------------------------------------------------------------------
    # Admin command handler (delegated to CommandHandler)
    # ------------------------------------------------------------------

    async def _handle_command(self, text: str, chat_id: str) -> None:
        """Route Telegram commands to CommandHandler."""
        await self._command_handler._handle_command(text, chat_id)

    async def _welcome_new_member(self, user_id: str) -> None:
        """Send a welcome DM when a user joins one of the bot's channels."""
        await self.telegram.send_message(
            user_id, self._command_handler.get_welcome_message()
        )

    async def _restart_tasks(self, chat_id: str) -> None:
        """Cancel and restart all async tasks (called by CommandHandler)."""
        async with self._restart_lock:
            old_tasks = list(self._tasks)
            for t in old_tasks:
                t.cancel()
            await asyncio.gather(*old_tasks, return_exceptions=True)
            self._tasks = []
            await self.router.stop()
            await self.monitor.stop()
            await self.telemetry.stop()
            await self.telegram.stop()
            if self._ws_futures:
                await self._ws_futures.stop()
                self._ws_futures = None
            await self._bootstrap.start_websockets()
            self._command_handler.ws_futures = self._ws_futures
            self._tasks = self._bootstrap.launch_runtime_tasks()
            # Re-sync tasks list into command handler
            self._command_handler._tasks = self._tasks
            await self.telegram.send_message(
                chat_id, "✅ Engine loops and WebSocket subscriptions restarted."
            )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def _run() -> None:
    engine = CryptoSignalEngine()
    loop = asyncio.get_running_loop()

    for sig_name in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig_name, lambda: asyncio.create_task(engine.shutdown()))

    await engine.boot()
    # Keep running until cancelled
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        await engine.shutdown()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
