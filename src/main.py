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

from src.performance_tracker import (
    PerformanceTracker,
    entry_sl_distance_pct,
    shipped_sl_distance_pct,
)
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
from src.footprint import get_store as get_footprint_store
from src.depth_book import get_store as get_depth_store
from src.live_ticks import get_store as get_live_tick_store
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
        # Live aggressive-trade pool (price-action program, Phase 2a). Its own
        # connection pool because @aggTrade is the highest-rate stream we take.
        self._ws_futures_aggtrade: Optional[WebSocketManager] = None
        # Live order-book depth pool (price-action program, Phase 2c). Its own
        # pool because depth publishes on a fixed clock — silence on it is a
        # fault, where silence on aggTrade is often just a quiet symbol.
        self._ws_futures_depth: Optional[WebSocketManager] = None
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
                    # Same stamp as the main terminal path in trade_monitor: the
                    # risk the trade was sized for, which ``stop_loss`` is not
                    # once BE/trail has moved it (2026-08-01).
                    sl_distance_pct_at_entry=entry_sl_distance_pct(sig),
                    # ...and the stop that was actually in the market, which
                    # the line above is NOT: predictive scaling and the noise
                    # floor both move it before emit (2026-08-04).
                    shipped_sl_distance_pct=shipped_sl_distance_pct(sig),
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
                    # Stamped where it becomes true: the regime at entry is
                    # knowable only from the Signal, and no later pass can
                    # recover it (2026-07-28).
                    entry_regime=str(getattr(sig, "entry_regime", "") or ""),
                    entry_regime_15m=str(getattr(sig, "entry_regime_15m", "") or ""),
                    pair_admission=str(getattr(sig, "pair_admission", "") or ""),
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
                # "t" = kline open time (ms).  Stored so consumers can locate
                # the bar covering a wall clock rather than inferring an index
                # from elapsed time (see fetch_ohlc_15m_since).
                "open_time": float(k.get("t", 0) or 0) or float("nan"),
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

        elif event == "aggTrade":
            # The subscription the engine never had. Folded into its OWN store
            # rather than into `data_store.ticks`, because five live consumers
            # read that one — including a $500k cumulative-tick-volume gate —
            # and a gate that has been reading seed-time trades for months must
            # not silently start reading current ones in the deploy that makes
            # them current. `TICKS_LIVE_FOR_CONSUMERS` is the handover.
            #
            # One dict, one deque append, no logging and no async hop: this runs
            # once per message at thousands a second across the book.
            _row = get_live_tick_store().add(symbol, data)
            if _row is not None:
                # Same parse, second store: per-bar, per-price volume (Phase
                # 2b). The tick ring answers "what just traded"; the footprint
                # answers "at which price, and which side was aggressive" —
                # the layer the published evidence actually supports and the
                # one a single per-bar delta is structurally silent on.
                get_footprint_store().add_row(symbol, _row)

        elif event == "depthUpdate":
            # Partial book depth (Phase 2c). Every message is a complete top-N
            # snapshot, so this REPLACES state rather than amending it — there
            # is no sequence to chain and therefore nothing that can desync.
            # Two lists allocated and stored; no logging and no async hop.
            get_depth_store().update(symbol, data)

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

        def fetch_ohlc_1m_dark(symbol: str, since_ts: float):
            """1m OHLC since a dark signal was emitted, located **by timestamp**.

            ``fetch_ohlc_since`` above slices ``elapsed // 60`` bars off the end
            of the array, which assumes the array is gap-free and that its last
            bar is the current one.  Neither holds — feeds drop frames, and a
            frozen feed keeps serving its last bar — and when the assumption
            breaks the slice silently walks *different bars than the trade*.
            That is the class that produced 172 confident fabricated rows on the
            SAR arm (2026-07-26, #800); the dark lane must not inherit it,
            because its rows are the ones the owner reads to decide whether a
            silenced path deserves a live feed.

            So: locate the entry bar by ``open_time``, refuse a window whose
            timestamps are missing or non-finite, and hand the times back so the
            resolver can stamp *which* bar it last consumed.  A refusal leaves
            the row OPEN and counted rather than scored on bars nobody saw.

            The window is deliberately **not** contiguity-checked the way the
            15m SAR window is: this walk only asks "was a level touched", which
            a missing bar can only make more conservative, whereas the SAR walk
            steps a trailing level bar by bar and a gap would mis-date every
            exit after it.

            The slicing itself lives in ``dark_emission.slice_window`` so a test
            can drive it against the store's real shape — a windowing bug that
            returns plausible bars is not visible from its output.
            """
            from src import dark_emission as _de

            return _de.slice_window(self.data_store.get_candles(symbol, "1m"), since_ts)

        def _ohlc_15m_detail(symbol: str, since_ts: float):
            """15m OHLC for the SAR exit ledger, with a pre-entry warmup prefix.

            Returns ``(window, reason)``.  ``window`` is None when the record
            cannot be honestly replayed, and ``reason`` then names *which*
            precondition failed — see ``fetch_ohlc_15m_since`` for why a bare
            None was not enough (2026-07-28).

            A trailing exit is only meaningful on the bars it trails, so this
            ledger reads 15m rather than the 1m the static audits use.  Two
            things differ from ``fetch_ohlc_since``:

            * **Warmup prefix** — ``SAR_EXIT_SHADOW_WARMUP_BARS`` bars *before*
              the stamp are included so the SAR has converged by the time the
              trade starts, and ``entry_index`` marks the trade's first bar.
              Both the trail walk and the static control arm slice from there.
            * **Hard post-entry cap** — the window is capped at
              ``SAR_EXIT_SHADOW_WINDOW_BARS``, the same bound the trail walk
              uses.  Without it a backlogged record would hand the control arm
              a longer window than the trail and quietly re-introduce the
              hold-time confound this pair exists to remove.

            **The entry bar is found by timestamp, never by counting elapsed
            time** (2026-07-26 fix).  The first cut located it arithmetically —
            ``n_post = elapsed // bar_seconds``, index counted back from the end
            of the array — which silently assumes the array is gap-free and its
            last bar is the current one.  Neither holds: feeds drop frames, and
            a frozen feed keeps serving its last bar (``last_kline_age_seconds``
            exists because of an 11-hour MVLLUSDT freeze).  When the assumption
            broke, ``min()``/``max(0, …)`` clamped the index instead of failing,
            so the walk replayed a *different bar than the trade* and still
            returned a confident verdict.  Owner-caught 2026-07-26 on the ops
            export: exit price was a pure function of (symbol, side) —
            TRUMPUSDT signals stamped three hours apart all "exited" at 1.598 —
            41% of one-bar moves exceeded 5%, and the arm read −4.4R average on
            172 fabricated rows.

            So: locate the bar by ``open_time``, verify the slice is contiguous
            and real, and return ``None`` when it isn't.  A record that cannot
            be honestly replayed must produce no verdict — ``classify_pending``
            leaves it pending and eventually marks it INSUFFICIENT, which is a
            truthful "we don't know" rather than an invented number.

            Reads the already-warm in-memory store: no network, no Firestore.
            """
            import numpy as np

            from config import (
                SAR_EXIT_SHADOW_BAR_MINUTES,
                SAR_EXIT_SHADOW_WARMUP_BARS,
                SAR_EXIT_SHADOW_WINDOW_BARS,
            )

            candles = self.data_store.get_candles(symbol, "15m")
            if not candles:
                return None, "no 15m array (symbol left the scanned universe?)"
            highs = candles.get("high")
            lows = candles.get("low")
            closes = candles.get("close")
            opens = candles.get("open")
            open_time = candles.get("open_time")
            if highs is None or lows is None or closes is None or open_time is None:
                return None, "15m array missing a required series"
            n = len(highs)
            if n == 0 or len(lows) != n or len(closes) != n or len(open_time) != n:
                return None, "15m array empty or ragged"

            bar_ms = max(1.0, float(SAR_EXIT_SHADOW_BAR_MINUTES) * 60_000.0)
            since_ms = float(since_ts) * 1000.0
            # The entry bar is the last one that had already opened at stamp time.
            idx = int(np.searchsorted(np.asarray(open_time), since_ms, side="right")) - 1
            if idx < 0:
                # array begins after the stamp — history already rolled off
                return None, "15m history rolled off before the stamp"

            warmup = max(0, int(SAR_EXIT_SHADOW_WARMUP_BARS))
            start = idx - warmup
            if start < 0:
                # not enough pre-entry bars for the SAR to converge
                return None, f"fewer than {warmup} warmup bars before entry"
            end = min(n, idx + 1 + int(SAR_EXIT_SHADOW_WINDOW_BARS))

            ot = np.asarray(open_time[start:end], dtype=np.float64)
            if not np.all(np.isfinite(ot)):
                # padded/unknown timestamps in the window
                return None, "non-finite bar timestamps in the window"
            # Contiguity: the SAR walk steps bar by bar, so a gap would silently
            # compress real time and mis-date every exit after it.
            if len(ot) > 1 and not np.all(np.abs(np.diff(ot) - bar_ms) < 1.0):
                return None, "gap or duplicate bar in the 15m window"
            # The entry bar must actually contain the stamp, not merely precede it.
            if not (0.0 <= since_ms - float(ot[idx - start]) < bar_ms):
                return None, "located bar does not contain the stamp"

            out = {
                "high": list(highs[start:end]),
                "low": list(lows[start:end]),
                "close": list(closes[start:end]),
                "entry_index": idx - start,
            }
            # Opens are optional: without them a gap through the stop fills at
            # the stop (the optimistic read) instead of at the worse open.
            if opens is not None and len(opens) == n:
                out["open"] = list(opens[start:end])
            return out, ""

        def fetch_ohlc_15m_since(symbol: str, since_ts: float):
            """``_ohlc_15m_detail``, with the miss counted and its cause kept.

            ``classify_pending`` reads a None here as "not yet" and moves on —
            correct mid-window, but silent, so a record whose candles will never
            arrive looks exactly like one stamped a minute ago for two days.  The
            cause is knowable at exactly this point and nowhere later, so it is
            recorded here (2026-07-28).
            """
            from src import sar_exit_shadow as _sar_shadow

            window, reason = _ohlc_15m_detail(symbol, since_ts)
            _sar_shadow.record_candle_fetch(symbol, window is not None, reason)
            return window

        async def _refresh_sar_ledger_candles() -> None:
            """Keep 15m candles alive for symbols the ledger still owes a verdict.

            The resolver reads the warm in-memory store and nothing else.  For a
            promoted mover that store has exactly one writer —
            ``scanner._refresh_stale_mover_candles``, which runs only for
            *actively scanned* movers — so a rotated-out mover's 15m array simply
            stops advancing.  The walker then sees a window ending before the
            exit, returns a WINDOW verdict, ``classify_pending`` rightly refuses
            it as "ran out of candles", and the record sits RUNNING until it ages
            into INSUFFICIENT.  Four such rows were showing −6% to −10% marks on
            /signals/sar for trades that had already stopped out at their 3% cap
            (owner-caught 2026-07-28).

            Bounded work, mirroring the mover refresher: at most
            ``SAR_EXIT_SHADOW_CANDLE_REFRESH_MAX_PER_CYCLE`` symbols per audit
            cycle, one attempt per ``SAR_EXIT_SHADOW_CANDLE_REFRESH_SEC`` per
            symbol regardless of outcome, oldest-unresolved first.  Public
            klines only — no Firestore, and this is the 5-minute audit loop, not
            a hot path.
            """
            from config import (
                SAR_EXIT_SHADOW_BAR_MINUTES as _bm,
                SAR_EXIT_SHADOW_CANDLE_REFRESH_MAX_PER_CYCLE as _max_per_cycle,
                SAR_EXIT_SHADOW_CANDLE_REFRESH_SEC as _refresh_sec,
                SAR_EXIT_SHADOW_WINDOW_BARS as _wb,
                SEED_TIMEFRAMES,
            )

            from src import sar_exit_shadow as _sar_shadow

            if int(_max_per_cycle) <= 0:
                return
            symbols = _sar_shadow.unresolved_symbols(
                window_sec=float(_wb) * float(_bm) * 60.0
            )
            if not symbols:
                return
            depth = next(
                (tf.limit for tf in SEED_TIMEFRAMES if tf.interval == "15m"), 500
            )
            now_mono = time.monotonic()
            # Selection lives in the ledger module as a pure function so it can
            # be driven directly by a test rather than through this loop's I/O.
            # It counts what the cap turns away instead of ``break``ing at it:
            # the old loop stopped, so a budget too small for the ledger was
            # indistinguishable from one that fit — the starved symbols were
            # never fetched, therefore never counted as a fetch miss either, and
            # the candle-health probe read a clean 100% while most of the ledger
            # got no candles at all (owner-caught 2026-07-29).
            due, starved = _sar_shadow.plan_refresh_batch(
                symbols,
                last_refresh_at=_sar_candle_refresh_at,
                age_seconds=lambda s: self.data_store.last_kline_age_seconds(s, "15m"),
                now_mono=now_mono,
                refresh_sec=float(_refresh_sec),
                max_per_cycle=int(_max_per_cycle),
            )
            _sar_shadow.record_refresh_budget(
                due=len(due) + starved,
                served=len(due),
                starved=starved,
                pending=len(symbols),
            )
            if starved:
                log.warning(
                    "SAR ledger candle refresh STARVED: {} of {} due symbols "
                    "turned away by the per-cycle cap ({}); {} symbols still "
                    "await a verdict. Records on the starved symbols cannot "
                    "resolve until they are served — raise "
                    "SAR_EXIT_SHADOW_CANDLE_REFRESH_MAX_PER_CYCLE.",
                    starved, len(due) + starved, int(_max_per_cycle), len(symbols),
                )
            if not due:
                return
            for sym in due:
                _sar_candle_refresh_at[sym] = now_mono
            # Drop throttle entries for symbols with nothing left to resolve.
            if len(_sar_candle_refresh_at) > 512:
                keep = set(symbols)
                for stale in [s for s in _sar_candle_refresh_at if s not in keep]:
                    _sar_candle_refresh_at.pop(stale, None)

            async def _one(sym: str) -> bool:
                info = self.pair_mgr.pairs.get(sym)
                market = getattr(info, "market", None) or "futures"
                return await self.data_store.refresh_timeframe(
                    sym, "15m", int(depth), str(market)
                )

            results = await asyncio.gather(
                *[_one(s) for s in due], return_exceptions=True
            )
            refreshed = sum(1 for r in results if r is True)
            log.info(
                "SAR ledger candle refresh: {}/{} symbols refreshed "
                "({} unresolved symbols pending)",
                refreshed, len(due), len(symbols),
            )

        # Per-symbol refresh throttle.  Loop-scoped rather than an instance
        # attribute: it is meaningless outside this loop's lifetime.
        _sar_candle_refresh_at: Dict[str, float] = {}

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
                        # A pre-scoring reject never reached the scoring engine,
                        # so it carries the evaluator's confidence and no scored
                        # one.  It is audited (did setup_compat / execution save
                        # or cost us?) and deliberately kept OUT of the matrix:
                        # Layer C's context_emission_policy reads these cells
                        # LIVE to set per-context emission floors, so admitting
                        # ~38k unscored rows per window would move what the
                        # money path emits.  Measurement ON, money path OFF —
                        # the audit is the surface, the matrix is not.
                        if not _sa.feeds_edge_matrix(rec):
                            return
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
                                net_r_multiple=outcome.get("net_r_multiple"),
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

            # ── Dark emission lane: resolve the owner-only feed ────────────
            # These rows are signals the scanner was willing to send on a path
            # the gates normally silence. Unlike a suppression stamp they went
            # through the full chain, so their outcomes are the closest thing
            # to "what would the feed have looked like" we can measure without
            # putting them in front of a user. Resolved off the loop thread for
            # the same reason as the batches above: a backlog on the loop
            # starves the scanner and trade-monitor heartbeats.
            try:
                from src import dark_emission as _de
                if _de.enabled():
                    # The timestamped fetch, not the elapsed-time one: these
                    # rows carry an unrealized PnL on the ops page, and a mark
                    # is only honest beside bars we can date.
                    _dark_counters = await asyncio.to_thread(
                        _de.resolve_open, fetch_ohlc_1m_dark
                    )
                    if any(_dark_counters.values()):
                        log.info("Dark emission resolved: {}", _dark_counters)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.warning("Dark emission resolve error (fail-open): {}", exc)

            # ── SAR exit arms on the dark rows ────────────────────────────
            # The same mechanism the live arms measure, run over the dark feed
            # so each row has two outcomes: what its own SL/TP1 geometry did,
            # and what a SAR handover would have done. Owner, 2026-07-31.
            #
            # Swept here rather than in the monitor loop because these arms
            # belong to this lane's clock — and the sweep is keyed on the arms
            # owed a verdict, so an arm outlives its dark row exactly as a live
            # arm outlives its signal (#835). The lane's health is rolled here
            # too: the monitor loop rolls `live` on its own period, and one roll
            # covering both would report a window neither lane ran.
            try:
                from src import dark_emission as _de_sar
                from src import sar_live_shadow as _sarlive
                if _de_sar.enabled():
                    _dark_sar = await asyncio.to_thread(
                        _sarlive.sweep,
                        self.data_store,
                        ledger=_sarlive.get_dark_ledger(),
                        lane=_sarlive.LANE_DARK,
                    )
                    _sarlive.get_dark_ledger().flush(force=True)
                    _sarlive.roll_health_cycle(_sarlive.LANE_DARK)
                    if any(_dark_sar.values()):
                        log.info("Dark SAR arms swept: {}", _dark_sar)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.warning("Dark SAR sweep error (fail-open): {}", exc)

            # ── Entry-feature stamps: persist the ring ─────────────────────
            # Stamping happens in the evaluator, where the facts become true.
            # This only writes them down. Forced every cycle so an idle lane
            # still refreshes the file's mtime — ops cannot tell "no MVRTP
            # signals fired" from "the engine stopped stamping" otherwise, and
            # that exact ambiguity made the dark page report a fault that was
            # not happening (2026-07-31).
            #
            # There is deliberately NO resolver here: outcomes are joined from
            # signal_performance.json by signal_id. Every lane in this repo that
            # grew its own forward-resolution machinery cost a session to
            # unresolvable rows, and this one needs none.
            try:
                from src import entry_features as _ef
                if _ef.enabled():
                    _ef.get_ledger().flush(force=True)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.warning("Entry-feature flush error (fail-open): {}", exc)

            # ── Structural SL/TP1 snap ledger ─────────────────────────────
            # force=True for the same reason: an idle lane that stops writing
            # renders as STALE, and "quiet market" and "the lane stopped" are
            # the two states an ops page cannot tell apart without a heartbeat.
            # No resolver here either — outcomes join from
            # signal_performance.json by signal_id.
            try:
                from src import structural_snap as _ss
                if _ss.measure_enabled():
                    _ss.get_ledger().flush(force=True)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.warning("Structural-snap flush error (fail-open): {}", exc)

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
                                net_r_multiple=outcome.get("net_r_multiple"),
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

            # ── Exit-method A/B: classify the SARBASE/SAREXIT pair ledger ──
            # Same forward measure on a LONGER window (the bake-off's 192 ×
            # 15m = 48h) and a 15m fetcher, because a trailing exit is only
            # meaningful on the bars it trails.  Both arms ride the identical
            # window and the identical R denominator, so the pair answers
            # "does SAR beat our live geometry" without the hold-time
            # confound the backtest's baseline comparison carried.
            try:
                from src import runtime_tunables as _rt
                if bool(_rt.get("sar_exit_shadow_enabled")):
                    from src import sar_exit_shadow as _sar
                    from src import suppression_audit as _sa
                    from src.strategy_edge import (
                        SOURCE_SHADOW,
                        StrategyOutcome,
                        get_strategy_edge_store,
                    )

                    def _feed_sar_edge(rec: dict) -> None:
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
                                net_r_multiple=outcome.get("net_r_multiple"),
                            ),
                            persist=False,
                        )

                    # Refresh first, classify second: a symbol that rotated out
                    # of the mover set has no other 15m writer, and classifying
                    # against its frozen array would just re-book the same
                    # unresolvable verdict for another cycle.
                    await _refresh_sar_ledger_candles()

                    def _classify_sar_batch() -> dict:
                        from config import SAR_EXIT_SHADOW_WINDOW_BARS as _wb
                        from config import SAR_EXIT_SHADOW_BAR_MINUTES as _bm
                        counters = _sar.get_sar_store().classify_pending(
                            fetch_ohlc_since=fetch_ohlc_15m_since,
                            window_sec=float(_wb) * float(_bm) * 60.0,
                            on_classified=_feed_sar_edge,
                            trail_classifier=_sar.classify_sar_record,
                        )
                        get_strategy_edge_store().save()
                        return counters

                    sar_counters = await asyncio.to_thread(_classify_sar_batch)
                    # Progress, not just fetch health: a window that exists but
                    # ends before the trade's exit is a *successful* fetch and
                    # still resolves nothing, so the candle probe reads 100%
                    # while the ledger produces no verdicts at all (the
                    # 2026-07-29 freeze).  Count verdicts against the backlog.
                    from config import SAR_EXIT_SHADOW_BAR_MINUTES as _sar_bm
                    from config import SAR_EXIT_SHADOW_WINDOW_BARS as _sar_wb
                    from src.suppression_audit import STALLED as _SAR_STALLED
                    _sar.record_resolution_cycle(
                        resolved=sum(
                            int(v) for k, v in sar_counters.items()
                            if k != _SAR_STALLED
                        ),
                        stalled=int(sar_counters.get(_SAR_STALLED, 0) or 0),
                        pending=_sar.unresolved_record_count(
                            window_sec=float(_sar_wb) * float(_sar_bm) * 60.0
                        ),
                    )
                    # Publish this cycle's fetch counters for the liveness probe.
                    # Rolled after the batch, and only after it: the probe must
                    # read a completed cycle, never one still filling.
                    _sar.roll_candle_fetch_cycle()
                    _sar.roll_refresh_budget_cycle()
                    _sar.roll_resolution_cycle()
                    _candle_health = _sar.candle_fetch_health()
                    if int(_candle_health.get("miss") or 0):
                        log.warning(
                            "SAR ledger candle misses this cycle: {} (ok={}) reasons={}",
                            _candle_health["miss"],
                            _candle_health["ok"],
                            _candle_health["reasons"],
                        )
                    if sar_counters:
                        log.info("SAR exit A/B classified: {}", sar_counters)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.warning("SAR exit A/B classify error (fail-open): {}", exc)

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
        # Routability: the only strategy keys the emission policy can look up are
        # the live SetupClass values — both scanner callsites pass
        # ``sig.setup_class``. The controller's inputs are keyed by *matrix*
        # strategy, which also carries the measurement arms and shadow-only units,
        # so overrides land under keys nothing reads. ``SetupClass`` is the
        # authoritative set and is read here (not inside the pure core) so
        # ``emission_controller`` stays import-free.
        routable = None
        enforce_routable = False
        if bool(_rt.get("emission_controller_routable_enabled")):
            from src.signal_quality import SetupClass

            routable = {c.value for c in SetupClass}
            enforce_routable = bool(_rt.get("emission_controller_routable_live"))
        decision = run_cycle(
            gate_metrics=inputs["gate_metrics"],
            best_strong_cell=inputs["best_strong_cell"],
            strategy_health=inputs["strategy_health"],
            global_params={"suppress_negative": gp.suppress_negative, "min_samples": gp.min_samples},
            prior=store.state,
            bounds=bounds,
            cycles_since_start=cycles,
            unlocked_cell_r=unlocked_cell_r,
            routable=routable,
            enforce_routable=enforce_routable,
        )
        rep = decision.routability
        store.commit(
            decision.state,
            decision.adjustments,
            routability=rep.to_dict() if rep is not None else None,
        )
        if rep is not None:
            self._emission_controller_routability = rep
            # WARN, not INFO: a promotion spent on a key nothing reads is budget
            # taken from a live strategy, and it must not be discoverable only by
            # reading a panel nobody opened.
            if rep.promoted_unroutable:
                log.warning(
                    "[EMISSION_CONTROLLER:ROUTABILITY] {} promotion(s) went to unroutable "
                    "keys {} — live candidates starved this cycle: {} (enforced={})",
                    len(rep.promoted_unroutable), rep.promoted_unroutable,
                    rep.starved_routable or "none", rep.enforced,
                )
            log.info(
                "[EMISSION_CONTROLLER:ROUTABILITY] enforced={} routable_cand={} "
                "unroutable_cand={} dead_overrides={} pruned={}",
                rep.enforced, rep.routable_candidates, rep.unroutable_candidates,
                len(rep.dead_overrides), len(rep.pruned),
            )
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
        def _sar_total():
            if not bool(_rt.get("sar_exit_shadow_enabled")):
                return None
            from src import sar_exit_shadow as _sar
            return float(_sar.get_sar_store().stamped_total)

        # Exit-method A/B: same event stream as the geometry pairs, so the same
        # subtraction catches the same failure — suppression events flowing
        # while zero SAR pairs land means the stamp broke.  This is the probe
        # the geometry A/B did not have when it stamped nothing for 25 hours.
        fl.add_rate(RateProbe(
            name="sar_exit_shadow",
            counter=_sar_total,
            upstream=_supp_total_raw,
            min_upstream_delta=10.0,
            min_streak=6,          # 30 min sustained
        ))
        def _sar_alignment_crosscheck() -> Tuple[bool, str]:
            """Stamp-time vs resolve-time SAR agreement must never diverge.

            The two paths compute the same quantity — the indicator's side on
            the last bar closed at entry — from different candle windows. They
            are allowed to be seeded differently (the resolver walks a 50-bar
            warmup, the scanner a much longer history) because SAR re-seeds on
            every flip, so convergence is the norm and a stray disagreement is
            noise. A *sustained* one is not: it means the replay window is not
            reconstructing the bar the scanner saw, which is precisely how #800
            published 172 confident rows describing nothing.

            Passes while the arm is off or before anything has resolved: this
            probe answers "are the two paths diverging", and with no data the
            honest answer is "no evidence of divergence". Whether the arm is
            *stamping at all* is already covered by the ``sar_exit_shadow``
            rate probe above, so nothing is hidden by not paging here.

            Deliberately does NOT raise to signal those states — ``PredicateProbe``
            turns an exception into a ``fail_open.record``, and a feature that is
            merely idle is not a swallowed failure. Filling that counter with
            non-failures is how a real one stops standing out.
            """
            if not bool(_rt.get("sar_exit_shadow_enabled")):
                return True, "disabled by tunable"
            from src import sar_exit_shadow as _sar
            counts = _sar.alignment_crosscheck()
            checked = counts["agree"] + counts["disagree"]
            if checked == 0:
                return True, "no alignment cross-checks yet"
            bad = counts["disagree"] / checked
            detail = f"{counts['disagree']}/{checked} disagreed ({bad:.1%})"
            # Tolerates isolated seed-boundary cases; catches a systematic
            # off-by-one, which would push this straight toward 100%.
            return bad <= 0.05, detail

        fl.add_predicate(PredicateProbe(
            name="sar_alignment_crosscheck",
            fn=_sar_alignment_crosscheck,
            min_streak=6,          # 30 min sustained
        ))

        def _aggtrade_feed() -> Tuple[bool, str]:
            """Is the live aggressive-trade feed actually delivering?

            The whole reason Phase 2a exists is that a complete trade handler
            sat in this file for months with nothing subscribed to feed it, and
            nothing anywhere reported the absence — an unfed store returns
            plausible rows of the right shape.

            Keyed on **subscribed-but-silent**, not on total rows: a subscription
            that did not take has no key in any arrival-keyed count, and a ring
            left full by a stream that stopped an hour ago looks identical to a
            healthy one. `quiet` is deliberately NOT a failure — an illiquid
            perp can genuinely go a minute without an aggressive trade, and
            paging on that reports a fault that is not happening.

            Returns True when disabled rather than raising: ``PredicateProbe``
            converts an exception into a ``fail_open.record``, and filling that
            counter with non-failures is how a real one stops standing out.
            """
            from config import AGGTRADE_STREAM_ENABLED
            if not AGGTRADE_STREAM_ENABLED:
                return True, "disabled by tunable"
            from src.live_ticks import get_store as _live
            h = _live().health()
            if h["subscribed"] == 0:
                return True, "no symbols subscribed yet"
            silent = h["subscribed_silent"]
            frac = silent / h["subscribed"]
            detail = (
                f"{h['fed']} fed / {h['quiet']} quiet / {silent} never delivered "
                f"of {h['subscribed']} subscribed; {h['total_accepted']} accepted, "
                f"{h['total_rejected']} rejected"
            )
            # A third of the subscription never delivering is a subscription
            # that did not take, not a quiet market.
            return frac < 0.34, detail

        fl.add_predicate(PredicateProbe(
            name="aggtrade_feed",
            fn=_aggtrade_feed,
            min_streak=6,          # 30 min sustained
        ))

        def _footprint_bars() -> Tuple[bool, str]:
            """Is the footprint sealing bars, and are they usable?

            Keyed on **sealed** bars, never on the open one: an open bar exists
            the instant a single trade arrives, so a store that accepts one
            trade and then stalls looks identical to a working one on any count
            that includes it.

            ``incomplete`` is not a failure by itself — a reconnect legitimately
            spoils a bar and the bar says so. It becomes a failure when it is
            most of the book, because a lane whose every bar carries a cause has
            no usable population left however healthy its counters read.
            """
            from config import AGGTRADE_STREAM_ENABLED
            if not AGGTRADE_STREAM_ENABLED:
                return True, "disabled by tunable"
            from src.footprint import get_store as _fp
            h = _fp().health()
            if h["symbols"] == 0:
                # Nothing has sealed a bar yet. Within the first minute of a
                # restart that is expected, and the aggtrade_feed probe above
                # already covers "no messages at all" — so this abstains
                # rather than paging for a second time on one cause.
                return True, "no sealed bars yet"
            sealed = h["sealed_bars"]
            if sealed == 0:
                return True, "symbols seen, no bar sealed yet"
            bad = h["incomplete_bars_held"] / sealed
            detail = (
                f"{sealed} sealed bars over {h['symbols']} symbols; "
                f"{h['incomplete_bars_held']} incomplete, "
                f"{h['capped_bars_total']} shape-capped"
            )
            return bad < 0.5, detail

        fl.add_predicate(PredicateProbe(
            name="footprint_bars",
            fn=_footprint_bars,
            min_streak=6,          # 30 min sustained
        ))

        def _depth_feed() -> Tuple[bool, str]:
            """Are the subscribed books actually being refreshed?

            Keyed on the population **owed** a book — the symbols we subscribed
            — and not on the symbols currently delivering, which is the shape
            that let a watchdog read 100% while every rotated-out symbol was
            unresolvable (#815). Here the difference bites immediately: a feed
            that dies leaves the store full of snapshots, so any probe counting
            what it holds sees a healthy book of stale prices.

            Silence is a fault on this stream and is not one on aggTrade. Depth
            publishes on a fixed clock whether or not anything trades, so a
            symbol with no message is a stopped feed, never a quiet market —
            which is why `depth_book` derives its staleness bound from the
            configured speed rather than guessing one.
            """
            from config import DEPTH_STREAM_ENABLED
            if not DEPTH_STREAM_ENABLED:
                # Not a failure. Raising here would convert to a fail_open
                # record and fill the counter whose whole purpose is making a
                # real failure stand out.
                return True, "disabled by tunable"
            h = get_depth_store().health()
            subscribed = h["symbols_subscribed"]
            if subscribed == 0:
                return True, "no symbols subscribed yet"
            live = h["delivering"]
            detail = (
                f"{live}/{subscribed} books fresh "
                f"(stale {h['stale']}, never {h['never_delivered']}, "
                f"thin {h['thin_books']}); {h['messages_total']} msgs, "
                f"{h['messages_rejected']} rejected"
            )
            # Two thirds rather than all: a genuinely thin or newly-subscribed
            # symbol can lag, and paging on the first one would make the probe
            # noise. A majority going dark is the fault worth waking someone.
            return live >= (subscribed * 2 // 3), detail

        fl.add_predicate(PredicateProbe(
            name="depth_feed",
            fn=_depth_feed,
            min_streak=6,          # 30 min sustained
        ))

        def _structural_veto_lane() -> Tuple[bool, str]:
            """Is the veto lane computing its features, or only its rows?

            Total blindness is a fault in EITHER mode, not just when enforcing.
            The tempting reasoning — abstaining costs nothing while nothing is
            enforced — is wrong: a rule that never reads its feature can never
            accumulate the evidence its own promotion depends on, which is a
            measurement flat-lining without paging. That is exactly how
            `smc_zone_dist_atr` returned None on 57 of 57 rows for its whole
            life while looking like agreement.

            Keyed on the fraction of stamped rows where the level book had
            NOTHING readable. `no_opposing` is deliberately not a fault — a
            populated book with clear air ahead is the finding, not a fault, and
            counting it here would page on the market being quiet.
            """
            from config import STRUCTURAL_VETO_MEASURE
            if not STRUCTURAL_VETO_MEASURE:
                return True, "disabled by tunable"
            from src.structural_veto import counters as _vc
            c = _vc()
            stamped = c.get("stamped", 0)
            if stamped < 20:
                return True, f"only {stamped} rows stamped yet"
            blind = c.get("refused_no_levels", 0) / max(1, stamped)
            detail = (
                f"{stamped} stamped; {c.get('refused_no_levels', 0)} with no "
                f"readable level book, {c.get('refused_no_opposing', 0)} with "
                f"clear air ahead, {c.get('would_reject', 0)} would-reject, "
                f"{c.get('enforced_reject', 0)} enforced"
            )
            return blind < 0.8, detail

        fl.add_predicate(PredicateProbe(
            name="structural_veto_lane",
            fn=_structural_veto_lane,
            min_streak=6,          # 30 min sustained
        ))

        def _price_action_lane() -> Tuple[bool, str]:
            """Is the lane evaluating, and is it refusing for a readable reason?

            Emission is NOT the health signal. This trigger is deliberately rare
            — a level swept and reclaimed with delta behind it — so zero rows in
            an hour is a quiet market, not a fault, and paging on it would train
            the reader to ignore the probe.

            What IS a fault is the lane never getting far enough to refuse for a
            market reason: if every evaluation dies on `no_levels` or
            `short_series`, the lane is blind rather than selective, and those
            are upstream faults with upstream fixes.
            """
            from config import PRICE_ACTION_LANE_MEASURE
            if not PRICE_ACTION_LANE_MEASURE:
                return True, "disabled by tunable"
            from src.price_action_lane import census as _pc
            c = _pc()
            n = c.get("evaluated", 0)
            if n < 50:
                return True, f"only {n} evaluations yet"
            refusals = c.get("refusals", {})
            blind = refusals.get("no_levels", 0) + refusals.get("short_series", 0)
            detail = (
                f"{n} evaluated, {c.get('emitted', 0)} emitted; "
                + ", ".join(f"{k}={v}" for k, v in sorted(refusals.items()))
            )
            # Blind on nearly everything means the LevelBook or the candle store
            # is not delivering — not that the market is quiet.
            return (blind / max(1, n)) < 0.9, detail

        fl.add_predicate(PredicateProbe(
            name="price_action_lane",
            fn=_price_action_lane,
            min_streak=6,          # 30 min sustained
        ))

        def _sar_ledger_candles() -> Tuple[bool, str]:
            """Can the resolver still fetch candles for the trades it owes?

            ``candle_coverage`` cannot answer this. It walks
            ``pair_mgr.pairs`` — the *current* universe — and the population at
            risk here is precisely the symbols that have left it: a promoted
            mover has no WS subscription, its only 15m writer runs for actively
            scanned movers, and when it rotates out its array freezes. Every
            ledger record on that symbol is then unresolvable forever, while
            coverage reads a healthy 100%. That is how four rows sat at RUNNING
            on /signals/sar showing −6% to −10% marks for trades that had
            already stopped out at their 3% cap (owner-caught 2026-07-28).

            So this probe reads the population that matters: fetches attempted
            for records we still owe a verdict on, counted per classify cycle.
            A miss is not fatal on its own — a symbol can be mid-refresh — so
            it pages on a *rate*, sustained across cycles by ``min_streak``.

            Returns True when idle rather than raising: ``PredicateProbe``
            converts an exception into a ``fail_open.record``, and an arm with
            nothing to resolve is not a swallowed failure.
            """
            if not bool(_rt.get("sar_exit_shadow_enabled")):
                return True, "disabled by tunable"
            from src import sar_exit_shadow as _sar
            health = _sar.candle_fetch_health()
            ok = int(health.get("ok") or 0)
            miss = int(health.get("miss") or 0)
            attempted = ok + miss
            if attempted == 0:
                return True, "no records awaited a verdict last cycle"
            rate = miss / attempted
            if miss == 0:
                return True, f"{ok}/{attempted} resolvable"
            reasons = health.get("reasons") or {}
            top = max(reasons.items(), key=lambda kv: kv[1])[0] if reasons else "unknown"
            syms = sorted(health.get("symbols") or {})
            detail = (
                f"{miss}/{attempted} unfetchable ({rate:.0%}); "
                f"top cause: {top}; symbols: {', '.join(syms[:5])}"
                + (f" +{len(syms) - 5} more" if len(syms) > 5 else "")
            )
            # A refresh takes one cycle to land, so a single stale symbol is
            # normal. A third of the population failing is the freeze.
            return rate <= 0.33, detail

        fl.add_predicate(PredicateProbe(
            name="sar_ledger_candles",
            fn=_sar_ledger_candles,
            min_streak=6,          # 30 min sustained
        ))

        def _candle_series_integrity() -> Tuple[bool, str]:
            """Is the store handing consumers bars in order?

            Two writers can disorder a bucket and they need different fixes, so
            the counters are read apart rather than summed:

            * ``candle_appends_out_of_order`` — a WebSocket bar arriving behind
              the bucket's newest, which is the ``refresh_timeframe`` REPLACE
              racing the socket. A trickle is normal operation; a flood means a
              symbol is being re-seeded continuously.
            * ``_series`` refusals — SAR declining a window it cannot walk. SAR
              is path-dependent, so a duplicated bar corrupts every level after
              it; refusing costs a measurement, walking would cost the answer.

            Returns True while the lane is merely degraded, because a refusal is
            the guard working. It fails when refusals are *sustained*, which
            means the store is not recovering and the arms have stopped
            measuring rather than paused.
            """
            try:
                from src import sar_live_shadow as _sls
                refusals = _sls.series_refusals()
                corrupt = int(refusals.get("duplicate_bar", 0)) + int(
                    refusals.get("out_of_order", 0)
                )
                store = getattr(self, "data_store", None)
                ooo = int(getattr(store, "candle_appends_out_of_order", 0) or 0)
                inplace = int(getattr(store, "candle_updates_in_place", 0) or 0)
                undedupable = int(getattr(store, "merge_undedupable", 0) or 0)
                dropped = int(getattr(store, "merge_duplicate_bars_dropped", 0) or 0)
                detail = (
                    f"merge dropped {dropped} dup bars, {undedupable} undedupable; "
                    f"ws {ooo} out-of-order, {inplace} in-place; "
                    f"SAR refused {corrupt} series"
                )
                # The guards absorb ordinary racing. A series still being
                # refused after they have had time to work is the store failing
                # to recover, and SAR is measuring nothing while it does.
                prev = getattr(self, "_last_series_refusals", None)
                self._last_series_refusals = corrupt
                if prev is None:
                    return True, detail
                return corrupt <= prev, detail
            except Exception as exc:  # noqa: BLE001
                return True, f"probe unavailable ({type(exc).__name__})"

        fl.add_predicate(PredicateProbe(
            name="candle_series_integrity",
            fn=_candle_series_integrity,
            min_streak=6,          # 30 min of *rising* refusals, not a blip
        ))

        def _entry_feature_inputs() -> Tuple[bool, str]:
            """Are the inputs MVRTP ignores actually arriving?

            The failure this catches is specific and silent: the lane keeps
            stamping rows, the file keeps refreshing, the ops panel keeps
            rendering — and every value inside is None because an upstream
            (OrderFlowStore, the level book, the depth snapshot) went dark.
            A feature absent on every row looks exactly like a feature nobody
            uses, and the whole point of this lane is deciding which of them
            carries signal.  So the probe keys on the *content* of the stamps,
            not on whether stamping happened.

            Two things it must not do, both paid for on 2026-08-03.  It must not
            judge a path on features that path never declared — `capture` emits
            one flat block for every setup, so an input only some paths supply
            is structurally absent on the rest and reads as a dead upstream
            forever.  And it must not *assert* a cause: `level_dist_r` returns
            None for a dark LevelBook, for a level shape this reader cannot
            parse, and for a working read whose answer is "nothing overhead",
            and the old message called all three "upstream is dark".

            Keyed on the population that would be harmed — the rows we intend
            to analyse — not on the convenient one (#815).  A lane with no rows
            yet returns True: an empty ledger is a quiet market or a fresh
            deploy, and signalling "idle" by failing is how a real failure stops
            standing out.  Do not raise here; a PredicateProbe exception becomes
            a fail_open record, and filling that counter with non-events is the
            same mistake one layer down.
            """
            try:
                from src import entry_features as _ef
                if not _ef.enabled():
                    return True, "entry-feature stamping disabled"
                s = _ef.summary()
                rows = int(s.get("rows") or 0)
                if rows < 20:
                    return True, f"only {rows} stamps so far — too few to judge"

                # Per path, not per ledger.  Since 2026-08-01 this lane covers
                # several setups with *different* feature sets, and the paths are
                # wildly uneven — MVRTP alone is ~94% of the delivered book.  A
                # TPE-only input that has gone dark shows up as `n` Nones against
                # a denominator dominated by mover rows, so `n >= rows` can never
                # be true and the probe reports healthy forever.  That is #815's
                # shape exactly: key on the population that would be harmed, not
                # on the one that happens to be convenient.
                # `missing_by_setup` counts only what each path DECLARES, which
                # is load-bearing: `capture` computes one flat block for every
                # path, so a feature whose input only some paths supply is
                # structurally None on the rest.  `extension_pct` needs
                # `ma_slow` — the two pullback paths pass it, MEAN_REVERT /
                # MOVER_AVWAP_SCALP / RANGE_FADE do not — and unscoped it read
                # "absent on EVERY stamp" on those three forever.  That is the
                # 'unused' this probe exists to tell dark apart from, arriving
                # as the alert itself (2026-08-03: 3 of 8 flagged items).
                per_setup = _ef.missing_by_setup()
                dead: List[str] = []
                for setup, (n_rows, missing) in sorted(per_setup.items()):
                    if n_rows < 10:
                        continue          # too few of this path to judge yet
                    for k, n in sorted(missing.items()):
                        if n < n_rows:
                            continue
                        # Name the cause instead of asserting one.  A feature
                        # that records why it is absent gets its histogram on
                        # screen — an empty LevelBook and a working read whose
                        # answer is "nothing overhead" are opposite findings
                        # that used to arrive as the same None.
                        why = _ef.absence_reasons(k, setup)
                        if why:
                            causes = "/".join(
                                f"{r}×{c}" for r, c in sorted(
                                    why.items(), key=lambda kv: (-kv[1], kv[0])
                                )
                            )
                            dead.append(f"{setup}.{k}[{causes}]")
                        else:
                            dead.append(f"{setup}.{k}[cause unrecorded]")
                # Counted, not silent: the scoping above is a judgement, and a
                # narrowed mode that leaves no trace is how the next reader
                # concludes the probe watched something it did not.
                undeclared = _ef.undeclared_absences()
                aside = (
                    f"; set aside {len(undeclared)} undeclared "
                    f"({','.join(sorted(undeclared))})"
                    if undeclared else ""
                )
                if dead:
                    return False, (
                        f"{len(dead)} declared feature(s) absent on EVERY stamp "
                        f"of their path: {','.join(dead)}{aside}"
                    )
                counts = ", ".join(
                    f"{k}={v}" for k, v in sorted((s.get("rows_by_setup") or {}).items())
                )
                return True, (
                    f"{rows} stamps ({counts}), no declared feature wholly "
                    f"absent{aside}"
                )
            except Exception as exc:  # noqa: BLE001
                return True, f"probe unavailable ({type(exc).__name__})"

        fl.add_predicate(PredicateProbe(
            name="entry_feature_inputs",
            fn=_entry_feature_inputs,
            min_streak=6,          # 30 min sustained
        ))

        def _structural_snap() -> Tuple[bool, str]:
            """The snap must be able to SEE structure, not merely run.

            This lane's characteristic failure is not a crash — it is a book of
            rows all reading "no level nearby", which is indistinguishable on
            every counter you would naturally look at from a market with no
            structure near price.  It has already happened once in this repo:
            ``smc_zone_dist_atr`` returned ``None`` on 57 of 57 rows for its
            whole life because it read a zone's edges by guessing key names, and
            nothing challenged the story written over it because nothing could.

            So the failure conditions are the ones that look healthy:

            * **refusal-dominated** — most rows carry no measurement at all, so
              the panel above them describes a fraction of the book while
              looking complete;
            * **structurally blind** — the walk runs, but finds no swing on
              either side, which means the series is arriving and the detector
              is not working on it;
            * **applying while blind** — the money-path half is on for a path
              whose rows cannot compute, i.e. an inert gate wearing a live
              gate's label.

            Returns True on an empty or tiny ledger: a fresh deploy and a quiet
            market are not faults, and signalling "idle" by failing is how a
            real failure stops standing out.  Never raises — a PredicateProbe
            exception becomes a fail_open record, and filling that counter with
            non-events is the same mistake one layer down.
            """
            try:
                from src import structural_snap as _ss
                if not _ss.measure_enabled():
                    return True, "structural-snap stamping disabled"
                s = _ss.summary()
                rows = int(s.get("rows") or 0)
                if rows < 20:
                    return True, f"only {rows} stamps so far — too few to judge"

                refused = int(s.get("refused") or 0)
                computed = int(s.get("computed") or 0)
                counters = s.get("counters") or {}
                top = sorted(
                    (counters.get("refused") or {}).items(),
                    key=lambda kv: -kv[1],
                )[:3]
                cause = ", ".join(f"{k}={v}" for k, v in top) or "none"
                if refused > rows * 0.5:
                    return False, (
                        f"{refused}/{rows} rows carry no measurement "
                        f"(top causes: {cause})"
                    )

                # Blind = the walk produced neither a swing high nor a swing
                # low.  Counted over rows that DID compute, so a refusal spike
                # cannot mask it and cannot double-count as it.
                blind = 0
                for r in _ss.get_ledger().rows():
                    if r.get("refused"):
                        continue
                    if not (r.get("n_swing_highs") or 0) and not (r.get("n_swing_lows") or 0):
                        blind += 1
                if computed and blind > computed * 0.8:
                    return False, (
                        f"{blind}/{computed} computed rows found NO swing on "
                        "either side — series arriving, detector silent"
                    )

                applied = int(counters.get("applied_sl") or 0) + int(
                    counters.get("applied_tp1") or 0
                )
                return True, (
                    f"{computed}/{rows} measured, {blind} blind, "
                    f"{applied} levels moved (refusals: {cause})"
                )
            except Exception as exc:  # noqa: BLE001
                return True, f"probe unavailable ({type(exc).__name__})"

        fl.add_predicate(PredicateProbe(
            name="structural_snap",
            fn=_structural_snap,
            min_streak=6,          # 30 min sustained
        ))

        def _setup_tf_resolver() -> Tuple[bool, str]:
            """The per-setup timeframe resolver must be REACHED, and must know
            the setups it is being asked about.

            ``_get_primary_timeframe`` was ``return "5m"`` for every channel
            since it was written — a constant wearing a lookup's docstring —
            and six money-path consumers read it.  The failure mode that
            replaces it is quieter than the bug it fixes: if the resolver stops
            being called, or is called with an empty ``setup_class``, it answers
            5m for everything again and nothing anywhere looks wrong.

            Two faults, both of which read as healthy on any obvious counter:

            * **unreached** — the census is empty while the scanner is plainly
              producing signals, i.e. the call sites were refactored away;
            * **unmapped-dominated** — the resolver is being called without a
              setup class, or a new evaluator has no declared timeframe, so the
              correction silently cannot apply to most of the book.

            Never raises: a PredicateProbe exception becomes a fail_open record,
            and filling that counter with non-events is how a real one stops
            standing out.
            """
            try:
                from src import setup_timeframes as _stf
                s = _stf.summary()
                resolved = int(s.get("resolved") or 0)
                if resolved < 50:
                    return True, f"only {resolved} resolutions so far — too few to judge"

                unmapped = int(s.get("unmapped") or 0)
                mismatched = int(s.get("mismatched") or 0)
                live = bool(s.get("correction_live"))
                if unmapped > resolved * 0.5:
                    return False, (
                        f"{unmapped}/{resolved} resolutions carried no declared "
                        "timeframe — the resolver is being called without a "
                        "setup class, or a new evaluator is unmapped; either "
                        "way the correction cannot apply"
                    )
                applied = int(s.get("applied") or 0)
                if live and mismatched > 0 and applied == 0:
                    return False, (
                        f"correction is LIVE and {mismatched} resolutions "
                        "disagree with 5m, yet none was applied"
                    )
                mode = "LIVE" if live else "dark"
                return True, (
                    f"{resolved} resolutions, {mismatched} would move off 5m, "
                    f"{unmapped} unmapped, correction {mode}"
                )
            except Exception as exc:  # noqa: BLE001
                return True, f"probe unavailable ({type(exc).__name__})"

        fl.add_predicate(PredicateProbe(
            name="setup_tf_resolver",
            fn=_setup_tf_resolver,
            min_streak=6,          # 30 min sustained
        ))

        def _entry_quality_effective() -> Tuple[bool, str]:
            """An ENFORCING rule must be able to see the feature it enforces on.

            The failure this exists for is not a crash and not an empty page: a
            rule whose feature stops computing **abstains on every candidate**,
            passes everything, and reads exactly like a rule that is working.
            An inert gate wearing a live gate's label is the shape of half the
            defects in ``CLAUDE.md`` — a probe reading healthy over a population
            it cannot see.

            So this checks the two states that are indistinguishable from
            healthy on any counter you would naturally look at:

            * an enforcing rule that is ``unknown`` on most of its population —
              the input died, the gate is decorative;
            * a gate parked over its blast-radius cap — it *wanted* to suppress,
              the cap held it back, and every downstream count looks like a gate
              that simply chose not to fire.

            Shadow rules are deliberately not judged: abstaining costs nothing
            when nothing is being enforced, and paging on it would fill the
            counter that is supposed to make a real fault stand out.  Same
            reason this returns True rather than raising when the lane is off or
            too young — a ``PredicateProbe`` exception becomes a
            ``fail_open.record``, and a non-event must never land there.
            """
            try:
                from src import entry_quality as _eq
                params = _eq.EntryQualityParams.from_config()
                if not params.enabled:
                    return True, "entry-quality evaluation disabled"
                snap = _eq.snapshot(params)
                totals = snap.get("totals") or {}
                evaluated = int(totals.get("evaluated_total") or 0)
                if evaluated < 20:
                    return True, f"only {evaluated} candidates evaluated — too few to judge"

                # Two thresholds, because a blind rule is a different fault
                # depending on whether it is enforcing.
                #
                # An ENFORCING rule mostly-abstaining is an inert gate wearing a
                # live gate's label — 0.8 catches it while it still has some
                # sight left.
                #
                # A SHADOW rule at *totally* blind is not a money-path fault at
                # all, and the first cut of this probe skipped shadow rules for
                # exactly that reason. That was wrong, and `smc_zone_dist_atr`
                # is why: `zone_distance_atr` read key names `FVGZone` does not
                # have, so the feature was uncomputable from the day it shipped
                # and `tpe_smc_zone` abstained on 100% of its population. A
                # shadow rule that never reads its feature can never accumulate
                # the evidence its own promotion depends on — it is a
                # measurement flat-lining without paging, which this repo bans.
                # Only 1.0 is judged there: a shadow rule with any sight is
                # working, and paging on it would fill the counter whose job is
                # making a real fault stand out.
                blind: List[str] = []
                for rule in snap.get("rules") or []:
                    stats = rule.get("stats") or {}
                    seen = int(stats.get("seen") or 0)
                    if seen < 20:
                        continue
                    frac = stats.get("unknown_frac")
                    if frac is None:
                        continue
                    live = bool(rule.get("live"))
                    limit = 0.8 if live else 1.0
                    if float(frac) >= limit:
                        blind.append(
                            f"{rule.get('key')} ({'enforcing' if live else 'shadow'}, "
                            f"feature {rule.get('feature')}) = {float(frac):.0%} unknown "
                            f"over {seen}"
                        )
                if blind:
                    return False, (
                        "entry-quality rule(s) cannot read their own feature: "
                        + "; ".join(blind)
                        + " — an enforcing rule in this state is inert and reads "
                        "as passing; a shadow one can never earn its promotion"
                    )

                budget = snap.get("budget") or {}
                if not _eq.get_budget().allows() and int(budget.get("suspended_total") or 0) > 0:
                    return False, (
                        "entry-quality gate is over its blast-radius cap "
                        f"({budget.get('recent_rejected')}/{budget.get('recent_decisions')} "
                        f"recent decisions rejected, cap {budget.get('max_reject_frac')}) "
                        "— suppression is held back and the rule reads as passing"
                    )
                live_rules = [r.get("key") for r in (snap.get("rules") or []) if r.get("live")]
                return True, (
                    f"{evaluated} evaluated, "
                    f"{totals.get('enforced_total')} suppressed, "
                    f"{totals.get('shadow_reject_total')} shadow-rejected; "
                    f"live rules: {','.join(str(k) for k in live_rules) or 'none'}"
                )
            except Exception as exc:  # noqa: BLE001
                return True, f"probe unavailable ({type(exc).__name__})"

        fl.add_predicate(PredicateProbe(
            name="entry_quality_effective",
            fn=_entry_quality_effective,
            min_streak=6,          # 30 min sustained
        ))

        def _sar_resolution_progress() -> Tuple[bool, str]:
            """The ledger must actually produce verdicts, not merely fetch data.

            ``sar_ledger_candles`` above asks whether the fetch returned a
            window.  A frozen or too-short window is still a window, so a record
            that can never resolve is counted there as a *success* — which is
            how, on 2026-07-29, 395 of 401 rows sat at RUNNING describing trades
            that had already closed while every probe read green.  Checked
            against real Binance candles, DEXEUSDT had hit its stop 1 minute
            after entry and sat unresolved for 19.2h.

            Deliberately not a stall *rate*: mid-window stalling is the healthy
            steady state, and a ledger holding 400 open trades stalls on nearly
            all of them every cycle, forever.  Paging on that would page on a
            working arm.  The signal is **progress against a non-empty backlog** —
            zero verdicts for an hour while records are owed one.  A quiet
            market cannot trip it, because a non-empty backlog is the
            precondition.

            Returns True when idle rather than raising: ``PredicateProbe``
            converts an exception into a ``fail_open.record``, and an arm with
            nothing to resolve is not a swallowed failure.
            """
            if not bool(_rt.get("sar_exit_shadow_enabled")):
                return True, "disabled by tunable"
            from src import sar_exit_shadow as _sar
            h = _sar.resolution_health()
            pending = int(h.get("pending") or 0)
            resolved = int(h.get("resolved") or 0)
            stalled = int(h.get("stalled") or 0)
            if pending == 0:
                return True, "no records await a verdict"
            if resolved > 0:
                return True, f"{resolved} resolved, {stalled} still mid-window"
            return False, (
                f"0 verdicts produced while {pending} records await one "
                f"({stalled} had candles and still resolved nothing). The "
                f"ledger is not advancing — check resolver candle freshness."
            )

        fl.add_predicate(PredicateProbe(
            name="sar_resolution_progress",
            fn=_sar_resolution_progress,
            min_streak=12,         # 1 hour sustained — healthy is 6-25/hour
        ))

        def _sar_refresh_budget() -> Tuple[bool, str]:
            """The per-cycle refresh cap must not be smaller than the ledger.

            The cap sustains ``max_per_cycle × (refresh_sec / loop_sec)``
            distinct symbols.  Below the ledger's symbol count the surplus is
            starved every cycle and its records can never resolve — 63 of 85
            symbols resolved 0% of their rows on 2026-07-29 for exactly this
            reason.  The starved count is published by the refresh loop (#825);
            nothing read it until now.

            A single starved cycle is not a fault: the ledger can spike. Half an
            hour of sustained starvation means the budget is genuinely too
            small.
            """
            if not bool(_rt.get("sar_exit_shadow_enabled")):
                return True, "disabled by tunable"
            from config import SAR_EXIT_SHADOW_CANDLE_REFRESH_MAX_PER_CYCLE as _cap
            from src import sar_exit_shadow as _sar
            if int(_cap) <= 0:
                return True, "refresh disabled by config"
            h = _sar.refresh_budget_health()
            pending = int(h.get("pending") or 0)
            starved = int(h.get("starved") or 0)
            served = int(h.get("served") or 0)
            if pending == 0:
                return True, "no symbols await a verdict"
            if starved == 0:
                return True, f"{served} refreshed, none turned away"
            return False, (
                f"{starved} due symbols turned away by the per-cycle cap "
                f"({_cap}); {pending} symbols await a verdict. Their records "
                f"cannot resolve — raise "
                f"SAR_EXIT_SHADOW_CANDLE_REFRESH_MAX_PER_CYCLE."
            )

        fl.add_predicate(PredicateProbe(
            name="sar_refresh_budget",
            fn=_sar_refresh_budget,
            min_streak=6,          # 30 min sustained
        ))

        def _sar_live_arms() -> Tuple[bool, str]:
            """The live SAR mechanism must be able to step the arms it holds.

            Keyed on **the arms owed a verdict**, not on the live pair universe.
            That distinction is the whole point: #815's ``candle_coverage``
            walked ``pair_mgr.pairs`` and scored 100% while every record on a
            rotated-out mover was permanently unresolvable, because a
            rotated-out symbol is by definition not in that map.  An open arm
            stays in this population whether or not its symbol is still scanned,
            so a rotation shows up here the cycle it happens.

            ``no_series`` counts arms whose candles the store could not supply
            this cycle.  A few is normal churn — a symbol seeding, a fresh
            listing.  Sustained misses mean arms are frozen: their stop is not
            being advanced, so the mechanism is not being measured on them and
            any number they later produce describes a gap.

            ``stalled`` counts the case this probe used to *pass* on (#835): the
            store returned a series, so the old predicate called it a healthy
            step, but its newest closed bar was hours old.  Presence of data is
            not currency of data.  Two frozen KORUUSDT arms read as "2 arms
            stepped, no candle misses" for 2h19m under the old rule.

            Returns True when idle rather than raising — an arm-less ledger is
            not a swallowed failure, and filling ``fail_open`` with non-failures
            is how a real one stops standing out.
            """
            from config import SAR_LIVE_SHADOW_ENABLED as _live_on
            if not _live_on:
                return True, "disabled by config"
            from src import sar_live_shadow as _live
            h = _live.step_health()
            stepped = int(h.get("stepped") or 0)
            no_series = int(h.get("no_series") or 0)
            stalled = int(h.get("stalled") or 0)
            missed = no_series + stalled
            # Arms we declined to open because the store's newest closed bar was
            # itself bars old.  Reported, never paged on: no arm exists, so
            # nothing is owed a verdict, and the refusal is the guard working.
            # It still has to be *visible* — a silent skip is how the opposite
            # failure (an arm anchoring to a 40h-old bar and back-replaying the
            # gap) survived long enough to publish a row.
            refused = int(h.get("refused_open") or 0)
            tail = f"; {refused} arms not opened (stale anchor)" if refused else ""
            if stepped == 0 and missed == 0:
                return True, f"no open arms{tail}"
            if missed == 0:
                return True, f"{stepped} arms current, none stalled{tail}"
            symbols = ", ".join(sorted(h.get("symbols") or {})[:6])
            return False, (
                f"{missed} live SAR arms could not be advanced this cycle "
                f"({no_series} no candles, {stalled} bars behind; {stepped} "
                f"current): {symbols}. Their stops are frozen, so the mechanism "
                f"is not being measured on those trades."
            )

        fl.add_predicate(PredicateProbe(
            name="sar_live_arms",
            fn=_sar_live_arms,
            min_streak=12,         # 1 min sustained (monitor ticks every 5s)
        ))

        def _dark_sar_arms() -> Tuple[bool, str]:
            """Are the SAR arms on the DARK rows still being advanced?

            Its own probe reading its own lane's counters, because a stall here
            and a stall on the delivered-signal arms need different responses:
            one is a measurement of a mechanism we might adopt, the other is a
            measurement riding the loop that carries real exits.  Pooling them
            would let a quiet dark-lane failure hide behind a busy live lane —
            and, worse, page about the live arms when nothing is wrong with
            them.

            Same shape as ``sar_live_arms`` deliberately: refusals are reported
            and never paged on, idle answers True with a reason.
            """
            from config import SAR_LIVE_SHADOW_ENABLED as _live_on

            from src import dark_emission as _de_p
            if not _live_on or not _de_p.enabled():
                return True, "disabled by config"
            from src import sar_live_shadow as _live

            h = _live.step_health(_live.LANE_DARK)
            stepped = int(h.get("stepped") or 0)
            no_series = int(h.get("no_series") or 0)
            stalled = int(h.get("stalled") or 0)
            missed = no_series + stalled
            refused = int(h.get("refused_open") or 0)
            tail = f"; {refused} arms not opened (stale anchor)" if refused else ""
            if stepped == 0 and missed == 0:
                return True, f"no open dark arms{tail}"
            if missed == 0:
                return True, f"{stepped} dark arms current, none stalled{tail}"
            symbols = ", ".join(sorted(h.get("symbols") or {})[:6])
            return False, (
                f"{missed} dark SAR arms could not be advanced this cycle "
                f"({no_series} no candles, {stalled} bars behind; {stepped} "
                f"current): {symbols}. The SAR comparison on those dark rows is "
                f"frozen, so their two outcomes are no longer measured together."
            )

        fl.add_predicate(PredicateProbe(
            name="dark_sar_arms",
            fn=_dark_sar_arms,
            min_streak=3,          # the dark lane sweeps on its own slower loop
        ))

        def _dark_resolution() -> Tuple[bool, str]:
            """Are the dark lane's open rows still being advanced?

            The lane shipped without a probe, which left its only failure mode
            silent: a row whose candles stop arriving keeps its last ``mfe_pct``
            and renders as a live trade forever.  Keyed on the rows owed a
            verdict, never on the scan universe — a rotated-out symbol is by
            definition absent from the latter and is exactly the row at risk
            (#815).  A disabled lane and an empty book answer True with a
            reason, because filling the fail-open counter with non-failures is
            how a real one stops standing out.
            """
            from src import dark_emission as _de

            ok, detail = _de.resolution_health()
            return bool(ok), str(detail)

        fl.add_predicate(PredicateProbe(
            name="dark_resolution",
            fn=_dark_resolution,
            # The resolve loop runs every ~5 min; this ticks far faster, so the
            # streak has to outlast a cycle rather than fire between two of them.
            min_streak=120,
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
        def _prescoring_audit() -> Tuple[bool, str]:
            """Are the pre-scoring gates measurable, and is the sample fair?

            Two failures this has to tell apart, because they look identical in
            a per-gate table and need opposite fixes:

            * **No rows** — the stamp is not reaching the audit.  That is the
              state `cohort_edge` was in for 23 days and it reads exactly like a
              quiet market (#834).
            * **Rows, but almost all evicted** — the gate is so loud that its
              400-row ring turns over faster than the measurement window, so the
              verdict beside it describes a sample nobody sized.  The rate is
              still honest; the reader has to know the denominator.

            Reports the eviction pressure rather than paging on it: a loud gate
            is not a fault, and filling this counter with non-failures is how a
            real one stops standing out.
            """
            if not bool(_rt.get("prescoring_audit_enabled")):
                return True, "disabled by tunable"
            sampling = _sa.get_store().sampling()
            pre = {
                g: v for g, v in sampling.items()
                if g.startswith("setup_compat:") or g.startswith("execution:")
            }
            if not pre:
                # Only a fault once the scanner has actually rejected some.
                rejects = sum(
                    v for k, v in getattr(
                        self._scanner, "_path_funnel_counters", {}
                    ).items()
                    if "gate_reject:setup_compat" in str(k)
                    or "gate_reject:execution" in str(k)
                )
                if rejects < 50:
                    return True, "no pre-scoring rejects yet"
                return False, (
                    f"{rejects} pre-scoring gate rejects and zero rows in the "
                    "audit — the stamp is not reaching the store, so "
                    "setup_compat / execution stay the only unmeasurable live "
                    "gates."
                )
            held = sum(v["held"] for v in pre.values())
            eviction = sum(v["evicted"] for v in pre.values())
            hot = sorted(pre.items(), key=lambda kv: -kv[1]["evicted"])[:3]
            detail = ", ".join(f"{g} {v['held']}/{v['held'] + v['evicted']}" for g, v in hot)
            return True, (
                f"{len(pre)} pre-scoring gates measured, {held} rows held, "
                f"{eviction} evicted (sampled: {detail})"
            )

        fl.add_predicate(PredicateProbe(
            name="prescoring_audit",
            fn=_prescoring_audit,
            min_streak=72,         # ~6 h — suppressions can be sparse
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

        def _gate_counter_sum(prefixes) -> Optional[float]:
            # Snapshot before summing — the scanner's event loop mutates the
            # Counter concurrently with this worker thread; a resize mid-read
            # skips the cycle (None) rather than crashing the registry.
            c = getattr(self._scanner, "_suppression_counters", None)
            if c is None:
                return None
            try:
                snap = dict(c)
            except RuntimeError:
                return None
            return float(sum(
                v for k, v in snap.items()
                if any(str(k).startswith(p) for p in prefixes)
            ))

        def _dsv2_evaluated():
            if not bool(_rt.get("dispatch_staleness_v2_enabled")):
                return None
            return _gate_counter_sum(("dsv2:evaluated",))

        # Staleness-V2 shadow: candidates keep reaching the staleness gate
        # (emitted or staleness-suppressed) while V2 evaluates none of them →
        # the shadow measurement died (import broke / params never build) and
        # the @DSV2 evidence the owner will sign off on silently stops
        # accumulating.  Dispatch attempts are sparse, hence the long streak.
        fl.add_rate(RateProbe(
            name="staleness_v2_shadow",
            counter=_dsv2_evaluated,
            upstream=lambda: _gate_counter_sum(
                ("enqueue_stage:emitted:", "enqueue_stage:dispatch_staleness")
            ),
            min_upstream_delta=5.0,
            min_streak=36,         # ~3 h
        ))

        def _gov_evaluated():
            if not bool(_rt.get("context_emission_gate_override_enabled")):
                return None
            return _gate_counter_sum(("gov:evaluated:",))

        # W5 gate-override shadow: the two overridable gates keep suppressing
        # while the override evaluated none of the blocks → the @GOV
        # measurement flat-lined.  Same bar as staleness_v2_shadow.
        fl.add_rate(RateProbe(
            name="gate_override_shadow",
            counter=_gov_evaluated,
            upstream=lambda: _gate_counter_sum(
                ("enqueue_stage:dispatch_staleness", "enqueue_stage:level_still_in_play:")
            ),
            min_upstream_delta=5.0,
            min_streak=36,         # ~3 h
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

        def _ec_routability_health():
            # The routability measurement must actually be producing a report once
            # enabled — an empty report is indistinguishable from "no problem
            # found" on the ops panel, which is precisely how the dead-key waste
            # went unnoticed for 279 cycles. Returns True with a reason when idle
            # or off: signalling "disabled" by raising converts to a
            # fail_open.record, and filling that counter with non-failures is how a
            # real failure stops standing out.
            if not bool(_rt.get("emission_controller_enabled")):
                return True, "controller disabled by tunable"
            if not bool(_rt.get("emission_controller_routable_enabled")):
                return True, "routability measurement disabled by tunable"
            rep = getattr(self, "_emission_controller_routability", None)
            if rep is None:
                return True, "no cycle yet (boot)"
            enforced = "enforcing" if rep.enforced else "measuring"
            dead = len(rep.dead_overrides)
            # While measuring, a standing dead-override footprint is the finding,
            # not a fault — report it loudly but do not page on it. Under
            # enforcement it should trend to zero, and staying non-zero means the
            # prune is not doing its job.
            if rep.enforced and dead:
                return False, f"enforcing yet {dead} dead override(s) persist: {sorted(rep.dead_overrides)}"
            return True, (
                f"{enforced}; dead_overrides={dead} wasted_promotions={rep.wasted_promotions} "
                f"pruned={len(rep.pruned)}"
            )

        fl.add_predicate(PredicateProbe(
            name="emission_controller_routability", fn=_ec_routability_health, min_streak=6,
        ))

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
            # Counts bars AND their age.  Counting alone is what let a 500-bar
            # 15m array frozen at boot score 100% for 2.5 days (2026-07-27): no
            # ``@kline_15m`` stream existed, nothing re-seeded a core pair, and
            # this probe — the one thing whose job is to notice a feature
            # flat-lining — asserted only that the bars were *there*.  Depth is
            # not liveness; ``last_kline_age_seconds`` is the freshness fact and
            # the store has always exposed it.
            from config import CANDLE_COVERAGE_MAX_AGE_SEC as _max_age

            pairs = getattr(self.pair_mgr, "pairs", {}) or {}
            syms = list(pairs.keys())
            if not syms:
                return False, "no universe symbols"
            ok_n = 0
            fresh_n = 0
            for s in syms:
                cd = self.data_store.get_candles(s, "15m") or {}
                closes = cd.get("close")
                if closes is None or len(closes) < 20:
                    continue
                ok_n += 1
                age = self.data_store.last_kline_age_seconds(s, "15m")
                # ``None`` = never stamped, which is not evidence of freshness.
                if age is not None and float(age) <= float(_max_age):
                    fresh_n += 1
            n = len(syms)
            healthy = (ok_n / n) >= 0.7 and (fresh_n / n) >= 0.7
            return healthy, (
                f"{ok_n}/{n} symbols with ≥20 15m candles, "
                f"{fresh_n}/{n} updated within {int(float(_max_age) // 60)}m"
            )

        fl.add_predicate(PredicateProbe(name="candle_coverage", fn=_coverage, min_streak=6))

        def _promoted_pair_integrity():
            """Is every pair we believe we are scanning actually in the universe?

            The scanner holds a promoted mover for 6 h, and `pair_manager`'s
            prune paths used to delete it out from under that hold on the 6 h
            refresh — after which the scan-set builder dropped it on a
            ``.get(...) is not None`` guard with no else-branch, while the
            symbol went on consuming promotion budget until its TTL expired.
            Mean ~50% of every mover's window, invisible by construction
            (2026-07-30).

            Keyed on the population that would be harmed — the pairs still
            under promotion — not on the universe map, which is exactly the
            place a rotated-out symbol is guaranteed not to be (#815's rule).
            """
            sc = getattr(self, "_scanner", None)
            if sc is None:
                return True, "scanner not constructed"
            promoted = dict(getattr(sc, "_mover_promoted_pairs", {}) or {})
            if not promoted:
                # Quiet market, nothing promoted.  Not a fault — and saying so
                # is the difference between "empty" and "broken".
                return True, "no pairs under promotion"
            pairs = getattr(self.pair_mgr, "pairs", {}) or {}
            missing = [s for s in promoted if s not in pairs]
            held = set(getattr(self.pair_mgr, "held_symbols", list)())
            unheld = [
                s for s in promoted
                if s in getattr(sc, "_synthetic_mover_pairs", set()) and s not in held
            ]
            detail = (
                f"{len(promoted) - len(missing)}/{len(promoted)} promoted pairs "
                f"present in universe"
            )
            if missing:
                detail += f"; missing={missing[:5]}"
            if unheld:
                detail += f"; synthetic-but-unheld={unheld[:5]}"
            return (not missing and not unheld), detail

        fl.add_predicate(PredicateProbe(
            name="promoted_pair_integrity", fn=_promoted_pair_integrity, min_streak=3,
        ))

        def _mover_admission_metadata():
            """Is the structural TradFi gate deciding, or just refusing?

            ``crypto_perp_admission`` is fail-CLOSED: with no exchangeInfo
            metadata it rejects every candidate.  That is the right default on
            a path that reaches the whole ~600-pair board, but a permanently
            empty cache would then starve mover promotion completely and look
            exactly like a quiet market.  A fail-closed gate needs a probe on
            the reason it is closing, or the safe default becomes a silent
            outage.
            """
            from src.execution import symbol_filters as _sf

            n_known = len(_sf.all_cached_symbols())
            if n_known == 0:
                return False, (
                    "exchangeInfo symbol cache EMPTY — every mover admission "
                    "is being refused for metadata_unavailable"
                )
            return True, (
                f"{n_known} symbols known, {len(_sf.tradfi_perp_symbols())} "
                f"marked TRADIFI_PERPETUAL"
            )

        fl.add_predicate(PredicateProbe(
            name="mover_admission_metadata", fn=_mover_admission_metadata, min_streak=3,
        ))

        def _cohort_edge_gate():
            """Is the cohort gate still able to change its mind?

            The gate suppresses on MEASURED expectancy, and the only thing that
            feeds that measurement is a DELIVERED signal resolving.  So a
            suppressed cohort produces no new evidence about itself — before
            the evidence-expiry window (2026-07-30) the verdict that armed the
            gate was the verdict permanently, and cohorts locked when STEP 2
            went ACTIVE on 2026-07-07 were still being judged on that day's
            data 23 days later.

            Two things are worth paging on, and neither is "the gate is
            suppressing" — that is the gate working:

            * expiry switched off while the gate is on — the absorbing state
              is back, and nothing else in the system would say so;
            * every cohort sharing one ``macro_dir`` — the key's 4th component
              was DECLINE on all 29 live cohorts on 2026-07-30, so a BTC macro
              flip resets every cohort to n=0 at once and fully disarms the
              gate in a single step.  Not a fault, but never discover it from
              a P&L chart.
            """
            from src import runtime_tunables as _rt
            from src.scanner import _cohort_edge_store as _ces

            stats = _ces.all_stats()
            if not stats:
                return True, "no cohort outcomes recorded yet"
            frozen = _ces.frozen_cohorts()
            macros = {k.split("/")[3] for k in stats if len(k.split("/")) >= 4}
            gate_on = bool(_rt.get("cohort_edge_gate_enabled"))
            try:
                max_age = float(_rt.get("cohort_edge_max_age_days"))
            except Exception:
                max_age = 0.0
            detail = (
                f"{len(stats)} cohorts, {len(frozen)} holding stale-only evidence, "
                f"expiry={max_age:g}d, macro_dirs={sorted(macros)}"
            )
            if gate_on and max_age <= 0:
                return False, "gate ON with evidence expiry DISABLED — " + detail
            if len(macros) == 1 and len(stats) >= 10:
                return False, (
                    f"all {len(stats)} cohorts share macro_dir={macros.pop()} — a "
                    f"macro flip resets every cohort at once; " + detail
                )
            return True, detail

        fl.add_predicate(PredicateProbe(
            name="cohort_edge_gate", fn=_cohort_edge_gate, min_streak=6,
        ))

        def _stale_tf_scoring():
            """Did any signal get scored on a *known-stale* timeframe?

            ``candle_coverage`` above answers "is the feed alive"; this answers
            "did we size geometry off a dead bar anyway", which is the question
            the 2.5-day 15m freeze needed and nobody could ask.  It is also the
            ops surface for the dark half of the guard: while
            ``stale_tf_refuse_enabled`` is off the counters show what *would*
            have been withheld, which is what the activation decision reads.

            Returns True when idle — never raises to signal "nothing happened"
            (that would fill the fail_open counter with non-failures).
            """
            from src import data_freshness as _df

            snap = _df.snapshot()
            counts = snap.get("counts") or {}
            scored = sum(v for k, v in counts.items() if k.startswith("scoring:"))
            gated = sum(v for k, v in counts.items() if k.startswith("gate:"))
            if not scored and not gated:
                return True, "no known-stale timeframe reached scoring"
            withheld = sum(v for k, v in counts.items() if k.startswith("withheld:"))
            last = (snap.get("last") or {}).get("scoring:15m") or {}
            return False, (
                f"scored on stale TF {scored}x (gate reads {gated}x, "
                f"withheld {withheld}x — refusal "
                f"{'ARMED' if _df.refusal_enabled() else 'dark'}); "
                f"last {last.get('symbol', '?')} age={last.get('age_sec', '?')}s"
            )

        fl.add_predicate(
            PredicateProbe(name="stale_tf_scoring", fn=_stale_tf_scoring, min_streak=6)
        )

        def _optimism_tax_health():
            # W2: the counterfactual net-R we steer on must track the net-R real
            # emitted trades actually realise.  A sustained gap on adequate sample
            # means the idealised counterfactual (or the cost constants) is wrong —
            # page rather than let the whole autonomous brain drift on a bad number.
            try:
                from config import (
                    EDGE_RECONCILIATION_ALERT_DELTA_R as _bound,
                    EDGE_RECONCILIATION_MIN_N as _min_n,
                )
                from src.strategy_edge import get_strategy_edge_store, reconcile_matrix
                recon = reconcile_matrix(get_strategy_edge_store().matrix())
            except Exception as _rex:
                from src import fail_open
                fail_open.record("main.optimism_tax_probe", _rex)
                return True, "reconciliation unavailable (fail-open)"
            worst_strat, worst_delta = None, 0.0
            for strat, r in recon.items():
                d = r.get("delta_r")
                if (
                    d is not None
                    and int(r.get("realized_n", 0)) >= _min_n
                    and int(r.get("counterfactual_n", 0)) >= _min_n
                    and abs(d) > abs(worst_delta)
                ):
                    worst_strat, worst_delta = strat, float(d)
            if worst_strat is None:
                return True, "no strategy past reconciliation sample floor yet"
            if abs(worst_delta) >= _bound:
                return False, f"{worst_strat} realized−counterfactual={worst_delta:+.2f}R (bound {_bound})"
            return True, f"max divergence {worst_strat} {worst_delta:+.2f}R (< {_bound})"

        fl.add_predicate(PredicateProbe(name="edge_reconciliation", fn=_optimism_tax_health, min_streak=6))

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
        def _gated_path_verdict_for(strategy: str, backlog: float, emitted: float):
            """Shared verdict for 'generates candidates, emits none' (#781).

            Both emission probes paged identically whether the gating was
            correct or costly. On real data those were opposite cases —
            RANGE_FADE's blocked candidates measure −0.98R (gating is right),
            MEAN_REVERT's measure positive (gating is expensive) — so a single
            undifferentiated alert made both unactionable and trained us to
            ignore the pager. The edge measurement was there the whole time.
            """
            from src.feature_liveness import gated_path_verdict
            from src.strategy_edge import get_strategy_edge_store, pooled_suppressed_edge

            try:
                edge = pooled_suppressed_edge(
                    get_strategy_edge_store().matrix(), strategy
                )
            except Exception as _pex:
                from src import fail_open
                fail_open.record("main.gated_path_edge", _pex)
                edge = None
            return gated_path_verdict(
                backlog=backlog, emitted_total=emitted, edge=edge, label=strategy
            )

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
                return _gated_path_verdict_for("MEAN_REVERT", backlog, emit)
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
                return _gated_path_verdict_for("RANGE_FADE", backlog, emitted)
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
            # Four distinct faults produce a residue and they need four
            # different responses, so the alert names which one rather than
            # calling the whole thing "unexplained" (2026-08-03).
            breakdown = _tv.residue_breakdown()
            named = sum(breakdown.values())
            causes = (
                ", ".join(
                    f"{k}={v}" for k, v in sorted(
                        breakdown.items(), key=lambda kv: (-kv[1], kv[0])
                    )
                )
                or "none recorded"
            )
            # Two counts of the same quantity are a detector: a gap means some
            # path returns without accounting for itself, which is the older,
            # quieter version of this same bug.
            gap = residue - named
            unaccounted = f", {gap} unaccounted" if gap else ""
            if residue >= 10:
                return False, (
                    f"{residue} non-stamps — {causes}{unaccounted} ({detail})"
                )
            return True, f"{detail}, residue {residue} ({causes}){unaccounted}"

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
