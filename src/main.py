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
from src.regime import MarketRegimeDetector
from src.scanner import Scanner
from src.signal_history_backfill import backfill_from_legacy_sources
from src.signal_history_store import load_history, save_history
from src.signal_router import SignalRouter
from src.telegram_bot import TelegramBot
from src.telemetry import TelemetryCollector
from src.trade_monitor import TradeMonitor
from src.trade_observer import TradeObserver
from src.exchange_client import CCXTClient
from src.order_manager import OrderManager
from src.paper_order_manager import PaperOrderManager
from src.auto_trade.risk_manager import RiskManager
from src.auto_trade.position_reconciler import PositionReconciler
from src.utils import get_logger
from src.websocket_manager import WebSocketManager
from src.redis_client import RedisClient
from src.signal_queue import SignalQueue
from src.state_cache import StateCache
from src.scheduler import ContentScheduler
from src.free_watch_service import FreeWatchService
from config import (
    CIRCUIT_BREAKER_MAX_CONSECUTIVE_SL,
    CIRCUIT_BREAKER_MAX_HOURLY_SL,
    CIRCUIT_BREAKER_MAX_DAILY_DRAWDOWN_PCT,
    CIRCUIT_BREAKER_COOLDOWN_SECONDS,
    CIRCUIT_BREAKER_STARTUP_GRACE_SECONDS,
    CHANNEL_TELEGRAM_MAP,
    ONCHAIN_API_KEY,
    PERFORMANCE_TRACKER_PATH,
    AUTO_EXECUTION_ENABLED,
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
        self.data_store = HistoricalDataStore()
        self.telegram = TelegramBot()
        self.telemetry = TelemetryCollector()

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
        if AUTO_EXECUTION_MODE != "off":
            self._risk_manager = RiskManager(
                starting_equity_usd=RISK_STARTING_EQUITY_USD,
                daily_loss_limit_pct=RISK_DAILY_LOSS_LIMIT_PCT,
                max_concurrent=RISK_MAX_CONCURRENT,
                max_leverage=RISK_MAX_LEVERAGE,
                min_equity_usd=RISK_MIN_EQUITY_USD,
                setup_blacklist=set(RISK_SETUP_BLACKLIST),
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
            self._order_manager = PaperOrderManager(
                position_size_pct=POSITION_SIZE_PCT,
                max_position_usd=MAX_POSITION_USD,
                starting_equity_usd=RISK_STARTING_EQUITY_USD,
                risk_manager=self._risk_manager,
            )
            log.info(
                "Auto-execution mode: PAPER (simulated fills, zero real-money risk)"
            )
        elif AUTO_EXECUTION_MODE == "live":
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
            alert_callback=self.telegram.send_admin_alert,
        )

        # Performance tracker (must be created before TradeMonitor)
        self._performance_tracker = PerformanceTracker(
            storage_path=PERFORMANCE_TRACKER_PATH
        )

        self.monitor = TradeMonitor(
            data_store=self.data_store,
            send_telegram=self.telegram.send_message,
            get_active_signals=lambda: self.router.active_signals,
            remove_signal=self._remove_and_archive,
            update_signal=self.router.update_signal,
            performance_tracker=self._performance_tracker,
            circuit_breaker=self._circuit_breaker,
            order_manager=self._order_manager,
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

        # SMC detector and market regime classifier
        self._smc_detector = SMCDetector()
        self._regime_detector = MarketRegimeDetector()

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
        self._ws_spot: Optional[WebSocketManager] = None
        self._ws_futures: Optional[WebSocketManager] = None
        # Dedicated liquidation WebSocket manager — forceOrder streams run in
        # their own connection pool so that liquidation floods during Extreme
        # Fear events cannot stall the kline WebSocket connections.
        self._ws_futures_liq: Optional[WebSocketManager] = None
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
        self._boot_time: float = 0.0
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
            ws_spot=None,
            ws_futures=None,
            tasks=self._tasks,
            boot_time=self._boot_time,
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
            )
        elif new_mode == "paper":
            self._risk_manager = RiskManager(
                starting_equity_usd=RISK_STARTING_EQUITY_USD,
                daily_loss_limit_pct=RISK_DAILY_LOSS_LIMIT_PCT,
                max_concurrent=RISK_MAX_CONCURRENT,
                max_leverage=RISK_MAX_LEVERAGE,
                min_equity_usd=RISK_MIN_EQUITY_USD,
                setup_blacklist=set(RISK_SETUP_BLACKLIST),
            )
            self._order_manager = PaperOrderManager(
                position_size_pct=POSITION_SIZE_PCT,
                max_position_usd=MAX_POSITION_USD,
                starting_equity_usd=RISK_STARTING_EQUITY_USD,
                risk_manager=self._risk_manager,
            )
        else:  # new_mode == "live"
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
            )
            self._order_manager = OrderManager(
                auto_execution_enabled=True,
                exchange_client=self._exchange_client,
                position_size_pct=POSITION_SIZE_PCT,
                max_position_usd=MAX_POSITION_USD,
                risk_manager=self._risk_manager,
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
            btc_cd = self.data_store.get_candles("BTCUSDT", "5m")
            if btc_cd and btc_cd.get("close"):
                closes = btc_cd["close"]
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
        # Sync boot_time to command handler after boot sets it
        self._command_handler.boot_time = self._boot_time
        # Sync WS managers to command handler after boot starts them
        self._command_handler.ws_spot = self._ws_spot
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
        """Handle a raw WebSocket message (kline, trade, or forceOrder)."""
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
        if self._ws_spot:
            await self._ws_spot.stop()
            self._ws_spot = None
        if self._ws_futures:
            await self._ws_futures.stop()
            self._ws_futures = None
        if self._ws_futures_liq:
            await self._ws_futures_liq.stop()
            self._ws_futures_liq = None

        await self._bootstrap.start_websockets()
        self._command_handler.ws_spot = self._ws_spot
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
                counters = classify_pending_records(fetch_ohlc_since=fetch_ohlc_since)
                if counters:
                    log.info("Invalidation audit classified: {}", counters)
                prune_old_records(retention_sec=7 * 24 * 3600)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.warning("Invalidation audit loop error: %s", exc)

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
            if self._ws_spot:
                await self._ws_spot.stop()
                self._ws_spot = None
            if self._ws_futures:
                await self._ws_futures.stop()
                self._ws_futures = None
            await self._bootstrap.start_websockets()
            self._command_handler.ws_spot = self._ws_spot
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
