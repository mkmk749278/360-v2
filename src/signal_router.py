"""Signal router – queue-based decoupled architecture.

Scanner → queue → Router → Telegram

The router:
  1. Consumes signals from an asyncio.Queue
  2. Enriches them with AI/predictive, confidence, risk
  3. Applies channel-specific min-confidence filter
  4. Posts to the appropriate Telegram channel
  5. Selects top 1–2 for the free channel
"""

from __future__ import annotations

import asyncio
import dataclasses
import inspect
import json
import os
import time
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple

from config import (
    ALL_CHANNELS,
    CHANNEL_COOLDOWN_SECONDS,
    CHANNEL_TELEGRAM_MAP,
    MAX_CONCURRENT_SIGNALS_PER_CHANNEL,
    MAX_SAME_DIRECTION_GLOBAL,
    MAX_SAME_DIRECTION_PER_PATH,
    MAX_SAME_DIRECTION_CUMULATIVE,
    DIRECTION_CAP_MODE,
    MAX_SIGNAL_HOLD_SECONDS,
    SIGNAL_EXPIRY_ENABLED,
    SIGNAL_TYPE_LABELS,
    TELEGRAM_ACTIVE_CHANNEL_ID,
    TELEGRAM_FREE_CHANNEL_ID,
)
from src.channels.base import Signal
from src.correlation import check_correlation_limit
from src.push_notifications import push_signal_published
from src.redis_client import RedisClient
from src.risk import RiskManager
from src.smc import Direction
from src.utils import get_logger
from src.ai_engine.predictor import SignalPredictor, PredictionFeatures
from src.ai_engine.scorer import AIConfidenceScorer
from src.cornix_formatter import format_cornix_signal

log = get_logger("signal_router")

# Max highlights posted to the free channel per calendar day.
_FREE_HIGHLIGHT_MAX_PER_DAY: int = 4
# Minimum TP level required to trigger a free-channel highlight.
_FREE_HIGHLIGHT_MIN_TP: int = 2

# SCALP channel names — used by the stale-signal gate and latency warnings.
# All eight scalp-family channels are included so that the tight 120 s stale
# threshold and latency warnings apply consistently across the full family.
_SCALP_CHANNEL_NAMES: frozenset = frozenset({
    "360_SCALP", "360_SCALP_FVG", "360_SCALP_CVD", "360_SCALP_VWAP",
    "360_SCALP_DIVERGENCE", "360_SCALP_SUPERTREND",
    "360_SCALP_ICHIMOKU", "360_SCALP_ORDERBLOCK",
})

# Stale-signal gate: maximum seconds a signal may spend between detection and
# posting before it is considered stale and suppressed.  For SCALP channels the
# window is tight (120 s) because micro-cap moves complete in 2-3 minutes.
# For all other channels the window is generous (used only as a safety net).
_SCALP_STALE_THRESHOLD_SECONDS: float = 120.0
_DEFAULT_STALE_THRESHOLD_SECONDS: float = 3600.0

# Latency WARNING threshold for SCALP signals (2 minutes per problem statement).
_SCALP_LATENCY_WARNING_SECONDS: float = 120.0

# Delivery-retry sleep callable – replaced in tests to avoid real waits.
async def _delivery_sleep(secs: float) -> None:
    await asyncio.sleep(secs)


def _signal_from_dict(data: dict) -> Optional[Signal]:
    """Reconstruct a Signal from a Redis-deserialized dict."""
    try:
        d = data.copy()
        if isinstance(d.get("direction"), str):
            d["direction"] = Direction(d["direction"])
        # Restore all datetime fields that were serialized as ISO strings
        for field in ("timestamp", "last_lifecycle_check", "dca_timestamp"):
            if isinstance(d.get(field), str):
                d[field] = datetime.fromisoformat(d[field])
        return Signal(**d)
    except Exception as exc:
        log.warning("Failed to reconstruct Signal from dict: {}", exc)
        return None


def _signal_to_dict(sig: Signal) -> dict:
    """Serialize a Signal to a JSON-serializable dict."""
    d = dataclasses.asdict(sig)
    d["direction"] = sig.direction.value  # Direction enum → string
    # Convert ALL datetime fields to ISO strings for JSON compatibility
    for k in list(d.keys()):
        if isinstance(d[k], datetime):
            d[k] = d[k].isoformat()
    return d


# Redis keys used for state persistence
_REDIS_KEY_SIGNALS = "signal_router:active_signals"
_REDIS_KEY_POSITION_LOCK = "signal_router:position_lock"
_REDIS_KEY_COOLDOWNS = "signal_router:cooldown_timestamps"

# JSON fallback for engines without Redis (the default deployment topology
# per CLAUDE.md: "Redis is optional. RedisClient + SignalQueue fall back to
# in-memory.").  Pre-fix, Redis-less engines persisted no state at all —
# every restart silently dropped active signals (owner reported losing
# 3-4 in-flight trades per restart with the admin-alert "Engine shutting
# down with N active signal(s). Please monitor open positions manually.").
#
# Path is env-overridable so tests can isolate per-fixture.  Default
# matches the doctrine of other persistence files
# (signal_dispatch_cooldown.json, ma_cross_cooldown.json,
# paper_pnl_state.json).
_ACTIVE_STATE_PATH_DEFAULT = "data/active_router_state.json"


def _resolve_active_state_path() -> Path:
    """Resolve the JSON-fallback path lazily so test fixtures can override
    via env var after module import."""
    return Path(os.getenv("ACTIVE_ROUTER_STATE_PATH", _ACTIVE_STATE_PATH_DEFAULT))


def _load_active_state_from_disk() -> Optional[Dict[str, Any]]:
    """Load persisted active-router state from JSON file.

    Returns ``None`` on missing / corrupt / unreadable file (fail-soft —
    a clean-slate session is the safe default for any IO failure).
    """
    path = _resolve_active_state_path()
    try:
        with path.open("r") as fp:
            data = json.load(fp)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, OSError) as exc:
        log.warning(
            "Active-router state file corrupt at %s — starting fresh (%s)",
            path, exc,
        )
        return None
    if not isinstance(data, dict):
        return None
    return data


def _persist_active_state_to_disk(payload: Dict[str, Any]) -> None:
    """Atomic write of router state to JSON file (tmp + rename so a crash
    mid-write doesn't leave a torn file).  Best-effort: any IO failure is
    logged at WARNING and swallowed."""
    path = _resolve_active_state_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w") as fp:
            json.dump(payload, fp)
        tmp.replace(path)
    except OSError as exc:
        log.warning(
            "Active-router state persist failed at %s: %s — continuing in-memory",
            path, exc,
        )


@dataclasses.dataclass(frozen=True)
class _DirectionCap:
    """One candidate's same-direction verdict under BOTH modes.

    Carried as a value rather than a tuple of bools so the gate, the log line
    and the counterfactual all read the same fields — a second reading of
    "would this have been blocked" is how the panel that justifies a switch
    ends up disagreeing with the gate that performs it.
    """

    mode: str
    key: str
    direction: str
    blocked: bool
    reason: str
    count: int
    limit: int
    same_dir_total: int
    same_dir_path: int
    would_block_global: bool
    would_block_per_path: bool


class SignalRouter:
    """Consumes signals from a queue, scores, filters, and dispatches."""

    def __init__(
        self,
        queue: Any,
        send_telegram: Callable[[str, str], Coroutine],
        format_signal: Callable[[Signal], str],
        redis_client: Optional[RedisClient] = None,
    ) -> None:
        self._queue = queue
        self._send_telegram = send_telegram
        self._format_signal = format_signal
        self._redis = redis_client
        self._active_signals: Dict[str, Signal] = {}
        self._daily_best: List[Signal] = []  # for free channel
        self._position_lock: Dict[str, Direction] = {}  # symbol → direction
        # Reconcile counters — see _reconcile_position_lock.  Cumulative
        # since boot and deliberately not reset: an orphan dropped at
        # restore is the evidence that the restore skew happened, and it is
        # the only place that evidence exists.
        self._lock_orphans_dropped: int = 0
        self._lock_missing_added: int = 0
        self._lock_direction_corrected: int = 0
        # (symbol, channel) → UTC timestamp of last signal completion
        self._cooldown_timestamps: Dict[Tuple[str, str], datetime] = {}
        self._running = False
        self._free_limit: int = 2  # max daily free signals
        self._risk_mgr = RiskManager()
        # Free-channel highlight rate limiting
        self._highlight_count_today: int = 0
        self._highlight_date: Optional[date] = None
        # Free-signal daily tracking: keyed by user-facing group ("active")
        self._free_signals_today: Dict[str, bool] = {}
        self._free_signal_date: Optional[date] = None
        # Detect whether queue.get() supports a timeout keyword argument
        self._queue_has_timeout = "timeout" in inspect.signature(queue.get).parameters
        # AI Trade Observer (optional — set after construction in main.py)
        self.observer: Optional[Any] = None
        # AI Engine integration (PR: AI Engine Refactor)
        self._ai_predictor: Optional[SignalPredictor] = None
        self._ai_scorer: Optional[AIConfidenceScorer] = None
        # Signal pulse: post periodic status messages for open signals
        self._signal_pulse_enabled: bool = True

        # ── Router drop telemetry (2026-08-02) ──────────────────────────────
        # Every rejection in ``_process`` was a bare ``return`` after a
        # ``log.info``: no counter, no suppression stamp, no funnel stage, and
        # nothing in the truth report parsing those lines. Twelve live gates
        # with no row in the Suppression Quality Audit, sitting on the one hop
        # that decides what a subscriber actually receives.
        #
        # It mattered because the artifact upstream is mislabelled: the path
        # funnel's "Emitted" column is incremented right after
        # ``_enqueue_signal`` succeeds, so it counts ENQUEUES. Enqueue is not
        # dispatch — this method drops most of what it dequeues — so the only
        # numbers anyone could read stopped one layer above the layer that does
        # the work. "When output drops, list the gates and check which ones
        # have no row" (``CLAUDE.md``): all of these had no row.
        #
        # Monotonic since boot, keyed ``reason`` and ``reason:setup_class`` so a
        # path that never reaches users can be told apart from a market that is
        # quiet. Never reset — a counter the reader has to catch mid-window is
        # a counter that reports a fault which is not happening.
        self._drop_counters: Dict[str, int] = defaultdict(int)
        # What each same-direction mode WOULD have done to every candidate this
        # gate saw.  In-process integers, reset on restart; see
        # ``direction_cap_report``.
        #
        # The four outcome buckets are seeded at zero rather than created on
        # first increment: a bucket that is absent until it fires teaches the
        # reader that its absence means "none", when it equally means the
        # counting stopped — and the two disagreement buckets are exactly the
        # ones a switch decision is read from, so an absent `global_only` is
        # the worst possible blank on this panel.
        self._direction_cap_counterfactual: Dict[str, int] = defaultdict(int)
        for _bucket in (
            "evaluated", "both_block", "global_only", "per_path_only",
            "neither_blocks",
        ):
            self._direction_cap_counterfactual[_bucket] = 0
        self._delivered_total: int = 0
        self._processed_total: int = 0
        # Optional callback: called after a paid signal is successfully posted.
        # Signature: async (symbol: str, bias: str) -> None
        # Wired to FreeWatchService.on_paid_signal in main.py.
        self.on_signal_routed: Optional[Any] = None
        # Optional callback: called by ``cleanup_expired`` BEFORE the signal is
        # popped from ``_active_signals`` so the engine can compute realised
        # P&L, archive the signal in ``_signal_history``, close any open
        # broker position, and stamp a perf-tracker record with
        # ``outcome_label="EXPIRED"``.
        # Signature: (sig: Signal, now: datetime) -> None  (sync)
        # Without this callback the cleanup path would silently drop the
        # signal — broker stays open, perf-tracker gets no record, the
        # Lumin app never sees the expiry under the Closed→Expired filter.
        self.on_signal_expired: Optional[Any] = None

    # ------------------------------------------------------------------
    # AI Engine wiring
    # ------------------------------------------------------------------

    def set_ai_engine(
        self,
        predictor: Optional[Any] = None,
        scorer: Optional[Any] = None,
    ) -> None:
        """Configure AI engine components for signal enrichment.

        Parameters
        ----------
        predictor:
            :class:`~src.ai_engine.predictor.SignalPredictor` instance.
        scorer:
            :class:`~src.ai_engine.scorer.AIConfidenceScorer` instance.
        """
        self._ai_predictor = predictor
        self._ai_scorer = scorer
        log.info("AI engine configured: predictor={}, scorer={}",
                 predictor is not None, scorer is not None)

    async def _enrich_with_ai(self, signal: Signal) -> Signal:
        """Enrich a signal with AI prediction and confidence scoring.

        When the AI predictor and scorer are configured, this method:
        1. Runs the predictor to get a probability estimate
        2. Feeds the probability into the AI scorer for threshold adjustment
        3. Updates the signal's confidence metadata

        Parameters
        ----------
        signal:
            The signal to enrich.

        Returns
        -------
        Signal
            The signal with updated AI confidence fields.
        """
        if self._ai_predictor is None and self._ai_scorer is None:
            return signal

        updates: Dict[str, Any] = {}

        # Step 1: AI prediction
        if self._ai_predictor is not None:
            try:
                features = PredictionFeatures(
                    price_features={"momentum": 0.0, "ema_alignment": 0.0},
                    volume_features={"obv_trend": 0.0},
                    order_book_features={},
                    correlation_features={},
                )
                prediction = await self._ai_predictor.predict(signal.symbol, features)
                updates["pre_ai_confidence"] = signal.confidence
                log.debug(
                    "AI prediction for {}: dir={} prob={:.3f}",
                    signal.symbol, prediction.direction, prediction.probability,
                )
            except Exception as exc:
                log.debug("AI prediction failed for {}: {}", signal.symbol, exc)

        # Step 2: AI confidence scoring
        if self._ai_scorer is not None:
            try:
                score_result = self._ai_scorer.score_signal(
                    symbol=signal.symbol,
                    base_confidence=signal.confidence,
                    regime=getattr(signal, "entry_regime", ""),
                )
                updates["post_ai_confidence"] = score_result.final_confidence
                if score_result.ai_adjustment != 0.0:
                    updates["confidence"] = score_result.final_confidence
                    log.debug(
                        "AI scorer adjusted {} confidence: {:.1f} → {:.1f} (adj={:+.1f})",
                        signal.symbol, signal.confidence,
                        score_result.final_confidence, score_result.ai_adjustment,
                    )
            except Exception as exc:
                log.debug("AI scoring failed for {}: {}", signal.symbol, exc)

        if updates:
            signal = dataclasses.replace(signal, **updates)

        return signal

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def restore(self) -> None:
        """Reload active state from Redis (or JSON-file fallback) after a
        process restart.

        Should be called once before :meth:`start` to resume monitoring of
        any signals that were active when the process last exited.
        Without this, an engine restart silently drops in-flight signals —
        the admin alert "Engine shutting down with N active signal(s)"
        owners reported losing data on.

        Lookup order:
          1. Redis (if configured + reachable)
          2. JSON file at ``data/active_router_state.json`` (default
             deployment topology — Redis is optional per CLAUDE.md)
        """
        if self._redis is not None and self._redis.available:
            await self._restore_from_redis()
        else:
            # Redis unavailable — fall back to the on-disk JSON file.
            self._restore_from_disk()

        # Both restore paths above rebuild two maps that must agree, and
        # neither could check that on its own — the reconcile runs here,
        # once, after whichever one ran.  See _reconcile_position_lock.
        if self._reconcile_position_lock()["changed"]:
            await self._persist_state()

    def _reconcile_position_lock(self) -> Dict[str, int]:
        """Make :attr:`_position_lock` agree with :attr:`_active_signals`.

        **The leak this repairs, because it cost a paid path its whole
        output.**  The lock is written in exactly one place — beside
        ``_active_signals[signal_id] = signal`` on confirmed delivery — and
        released in exactly two, both of which look the symbol up *through*
        ``_active_signals``.  At runtime the two maps therefore cannot
        diverge.  Restore is the one place they can, and did: both restore
        paths skip a signal whose status is no longer ``ACTIVE`` (right — a
        closed signal must not reappear in the app's Open tab) and then
        restore the lock map **wholesale, with no cross-check**.  So a symbol
        whose signal had already closed came back locked with nothing behind
        it, ``remove_signal`` could never fire for it (its ``if sig:`` guard
        never passes), and ``_persist_state`` wrote the orphan back on every
        save.  It compounded across restarts, and the engine restart-looped
        all day on 2026-08-19.

        Measured on the live box 2026-08-20: **2** signals ACTIVE while
        ``correlation_lock`` had dropped **309 of 332** dequeued candidates
        (93.1%) in one 13h process — and every one of the 30 rows the dark
        lane promoted was killed there, 26 on this gate, **0 delivered**.
        Six of the locked symbols had no delivered trade at all in the
        30-day recorded book, which under a lock only ever written on
        delivery is not a tight gate, it is a stale one.

        Each half was individually right and nothing reconciled them — the
        seam shape this repo keeps paying for (#817).  So this repairs at
        the one site divergence is *created*; the continuous half is a
        probe, because a guard on the first moment is not a guard on the
        object (#836/#846) and a future edit that breaks the pairing must
        page rather than go quiet.

        Both directions are counted, and they are different faults:

        - ``orphans_dropped`` — a lock with no active signal.  Over-blocking:
          it silently costs candidates their delivery, which is what
          happened.
        - ``missing_added`` — an active signal with no lock.  **Under**
          -blocking, and the more dangerous of the two, since the lock is
          what stops a second position opening on a symbol that already has
          one.  Repaired rather than merely counted.
        - ``direction_corrected`` — both present, disagreeing.  Cannot arise
          from the restore skew and is therefore corruption; counted apart so
          it can never hide inside the ordinary case.
        """
        active_dir: Dict[str, Direction] = {
            sig.symbol: sig.direction for sig in self._active_signals.values()
        }

        orphans = [sym for sym in self._position_lock if sym not in active_dir]
        for sym in orphans:
            self._position_lock.pop(sym, None)

        missing = [sym for sym in active_dir if sym not in self._position_lock]
        corrected = [
            sym
            for sym, dir_ in active_dir.items()
            if sym in self._position_lock and self._position_lock[sym] is not dir_
        ]
        for sym in missing + corrected:
            self._position_lock[sym] = active_dir[sym]

        self._lock_orphans_dropped += len(orphans)
        self._lock_missing_added += len(missing)
        self._lock_direction_corrected += len(corrected)

        if orphans:
            log.warning(
                "Position lock: dropped {} orphaned entr(ies) with no active "
                "signal behind them ({}{}) — these were blocking delivery on "
                "correlation_lock",
                len(orphans),
                ", ".join(sorted(orphans)[:10]),
                "…" if len(orphans) > 10 else "",
            )
        if missing:
            log.warning(
                "Position lock: {} active signal(s) had no lock entry ({}) — "
                "restored, a second position could have opened on them",
                len(missing),
                ", ".join(sorted(missing)[:10]),
            )
        if corrected:
            log.warning(
                "Position lock: {} entr(ies) disagreed on direction with the "
                "active signal ({}) — corrected",
                len(corrected),
                ", ".join(sorted(corrected)[:10]),
            )

        return {
            "orphans_dropped": len(orphans),
            "missing_added": len(missing),
            "direction_corrected": len(corrected),
            "changed": len(orphans) + len(missing) + len(corrected),
        }

    async def _restore_from_redis(self) -> None:
        try:
            client = self._redis.client
            if client is None:
                return
            # Restore active signals — same terminal-status filter as the
            # disk-backed path.  See _restore_from_disk for rationale.
            raw = await client.get(_REDIS_KEY_SIGNALS)
            if raw:
                signals_data: Dict[str, Any] = json.loads(raw)
                skipped_terminal = 0
                for sid, data in signals_data.items():
                    if isinstance(data, dict):
                        status = str(data.get("status", "ACTIVE")).upper()
                        if status != "ACTIVE":
                            skipped_terminal += 1
                            continue
                    sig = _signal_from_dict(data)
                    if sig is not None:
                        self._active_signals[sid] = sig
                log.info(
                    "Restored {} active signal(s) from Redis",
                    len(self._active_signals),
                )
                if skipped_terminal > 0:
                    log.info(
                        "Skipped {} terminal-status signal(s) from Redis "
                        "restore (closed mid-shutdown)",
                        skipped_terminal,
                    )

            # Restore position lock
            raw = await client.get(_REDIS_KEY_POSITION_LOCK)
            if raw:
                lock_data: Dict[str, str] = json.loads(raw)
                for sym, dir_str in lock_data.items():
                    try:
                        self._position_lock[sym] = Direction(dir_str)
                    except ValueError:
                        log.warning("Unknown direction '{}' for symbol {} – skipped", dir_str, sym)

            # Restore cooldown timestamps
            raw = await client.get(_REDIS_KEY_COOLDOWNS)
            if raw:
                cooldown_data: Dict[str, str] = json.loads(raw)
                for key, ts_str in cooldown_data.items():
                    parts = key.split("|", 1)
                    if len(parts) == 2:
                        sym, chan = parts
                        self._cooldown_timestamps[(sym, chan)] = datetime.fromisoformat(ts_str)
                log.info(
                    "Restored {} cooldown timestamp(s) from Redis",
                    len(self._cooldown_timestamps),
                )
        except Exception as exc:
            log.warning("Failed to restore state from Redis: {}", exc)

    def _restore_from_disk(self) -> None:
        """Load active state from the JSON-file fallback (Redis-less mode)."""
        data = _load_active_state_from_disk()
        if data is None:
            return

        signals_data = data.get("active_signals") or {}
        skipped_terminal = 0
        if isinstance(signals_data, dict):
            for sid, sig_data in signals_data.items():
                if not isinstance(sig_data, dict):
                    continue
                # Skip signals that hit a terminal status before the
                # last persist fired.  Pre-fix, they'd reappear in the
                # app's "Open" tab tagged INVALIDATED / SL_HIT / TP1_HIT
                # because the persistence layer captures whatever's in
                # the active map at the moment of write — including
                # signals mid-removal during shutdown.
                status = str(sig_data.get("status", "ACTIVE")).upper()
                if status != "ACTIVE":
                    skipped_terminal += 1
                    continue
                sig = _signal_from_dict(sig_data)
                if sig is not None:
                    self._active_signals[sid] = sig
        if self._active_signals:
            log.info(
                "Restored {} active signal(s) from disk",
                len(self._active_signals),
            )
        if skipped_terminal > 0:
            log.info(
                "Skipped {} terminal-status signal(s) from disk restore "
                "(closed mid-shutdown)",
                skipped_terminal,
            )

        lock_data = data.get("position_lock") or {}
        if isinstance(lock_data, dict):
            for sym, dir_str in lock_data.items():
                try:
                    self._position_lock[sym] = Direction(dir_str)
                except (ValueError, TypeError):
                    continue

        cooldown_data = data.get("cooldown_timestamps") or {}
        if isinstance(cooldown_data, dict):
            for key, ts_str in cooldown_data.items():
                parts = str(key).split("|", 1)
                if len(parts) != 2:
                    continue
                sym, chan = parts
                try:
                    self._cooldown_timestamps[(sym, chan)] = datetime.fromisoformat(
                        str(ts_str)
                    )
                except ValueError:
                    continue
        if self._cooldown_timestamps:
            log.info(
                "Restored {} cooldown timestamp(s) from disk",
                len(self._cooldown_timestamps),
            )

    async def _persist_state(self) -> None:
        """Serialize and save active router state.

        Writes :attr:`_active_signals`, :attr:`_position_lock`, and
        :attr:`_cooldown_timestamps` so that state can be restored after a
        process restart via :meth:`restore`.

        Storage backend:
          1. Redis when configured + reachable (preferred)
          2. JSON file at ``data/active_router_state.json`` as fallback
             (default deployment topology — Redis is optional)
        """
        # Build the payload once, dispatch to whichever backend is wired.
        signals_payload = {
            sid: _signal_to_dict(sig)
            for sid, sig in self._active_signals.items()
        }
        lock_payload = {
            sym: dir_.value for sym, dir_ in self._position_lock.items()
        }
        cooldown_payload = {
            f"{sym}|{chan}": ts.isoformat()
            for (sym, chan), ts in self._cooldown_timestamps.items()
        }

        if self._redis is not None and self._redis.available:
            try:
                client = self._redis.client
                if client is not None:
                    await client.set(
                        _REDIS_KEY_SIGNALS, json.dumps(signals_payload)
                    )
                    await client.set(
                        _REDIS_KEY_POSITION_LOCK, json.dumps(lock_payload)
                    )
                    await client.set(
                        _REDIS_KEY_COOLDOWNS, json.dumps(cooldown_payload)
                    )
                    return
            except Exception as exc:
                log.warning("Failed to persist state to Redis: {}", exc)
                # Fall through to disk persistence so we don't lose state
                # when Redis blips temporarily.

        # Redis unavailable / errored — fall back to JSON file.
        _persist_active_state_to_disk(
            {
                "active_signals": signals_payload,
                "position_lock": lock_payload,
                "cooldown_timestamps": cooldown_payload,
            }
        )

    def _schedule_persist(self) -> None:
        """Fire-and-forget: schedule :meth:`_persist_state` on the running loop."""
        try:
            asyncio.get_running_loop().create_task(self._persist_state())
        except RuntimeError:
            pass  # called outside a running loop (e.g., during unit tests)

    # Maximum unleveraged raw PnL % considered plausible for an active signal
    # pulse.  Typical scalp signals move ±0.5–5%; swing signals rarely exceed
    # ±15%.  30% provides a conservative ceiling that catches gross cross-symbol
    # contamination or stale Redis prices (e.g. a 2× price error) without
    # producing false positives on legitimate swing winners.  Finer-grained
    # corruption (e.g. 10%) is caught by the WATCHLIST-tier guard or by the
    # live current_price > 0 requirement.
    _PULSE_MAX_REASONABLE_PNL_PCT: float = 30.0

    async def _signal_pulse_loop(self) -> None:
        """Post a one-liner status pulse for every active open signal every SIGNAL_PULSE_INTERVAL_SECONDS."""
        from config import SIGNAL_PULSE_INTERVAL_SECONDS
        while self._running:
            await asyncio.sleep(30)
            if not TELEGRAM_ACTIVE_CHANNEL_ID:
                continue
            now_ts = time.time()
            for sid, sig in list(self._active_signals.items()):
                if sig.status not in ("ACTIVE", "TP1_HIT", "TP2_HIT"):
                    continue
                last_pulse = getattr(sig, "_last_pulse_time", 0.0)
                if now_ts - last_pulse < SIGNAL_PULSE_INTERVAL_SECONDS:
                    continue
                try:
                    # Require a live current_price supplied by the trade monitor.
                    # Do NOT fall back to sig.entry: using the entry price as a
                    # proxy would always show 0% PnL and hide stale-state bugs.
                    current_price = sig.current_price
                    if current_price <= 0:
                        log.debug(
                            "Signal pulse skipped for {} – current_price not yet populated",
                            sig.symbol,
                        )
                        continue

                    direction = sig.direction

                    # Validate TP1 direction before computing distances.  If TP1
                    # is on the wrong side of entry the signal state is corrupted;
                    # emit a warning and suppress rather than post bad numbers.
                    if direction == Direction.LONG:
                        if sig.tp1 <= sig.entry:
                            log.warning(
                                "Signal pulse skipped for {} LONG – TP1 {:.8f} <= entry {:.8f} (invalid state)",
                                sig.symbol, sig.tp1, sig.entry,
                            )
                            continue
                        pnl_pct = (current_price - sig.entry) / sig.entry * 100
                        tp1_dist = (sig.tp1 - current_price) / sig.entry * 100 if sig.tp1 > 0 else 0.0
                    else:
                        if sig.tp1 >= sig.entry:
                            log.warning(
                                "Signal pulse skipped for {} SHORT – TP1 {:.8f} >= entry {:.8f} (invalid state)",
                                sig.symbol, sig.tp1, sig.entry,
                            )
                            continue
                        pnl_pct = (sig.entry - current_price) / sig.entry * 100
                        tp1_dist = (current_price - sig.tp1) / sig.entry * 100 if sig.tp1 > 0 else 0.0

                    # Sanity-check PnL magnitude.  An unleveraged raw move beyond
                    # _PULSE_MAX_REASONABLE_PNL_PCT almost certainly indicates a
                    # stale or cross-symbol current_price.  Suppress the pulse
                    # rather than post a number that contradicts the eventual
                    # close message.
                    if abs(pnl_pct) > self._PULSE_MAX_REASONABLE_PNL_PCT:
                        log.warning(
                            "Signal pulse skipped for {} {} – implausible PnL {:.2f}%"
                            " (entry={} current={}). State likely stale or corrupted.",
                            sig.symbol, direction.value, pnl_pct, sig.entry, current_price,
                        )
                        continue

                    # Clamp tp1_dist to 0 when TP1 has already been crossed.
                    # Negative "TP1 in" is meaningless to users.
                    tp1_dist = max(tp1_dist, 0.0)

                    sl_pct = abs(current_price - sig.stop_loss) / sig.entry * 100 if sig.stop_loss > 0 else 999.0
                    if sl_pct <= 0.0:
                        thesis = "broken"
                    elif sl_pct <= 0.5:
                        thesis = "weakening"
                    else:
                        thesis = "intact"
                    direction_word = "LONG" if direction == Direction.LONG else "SHORT"
                    log.debug(
                        "Signal pulse: {} {} entry={} current={} pnl={:.2f}% tp1_dist={:.2f}%",
                        sig.symbol, direction_word, sig.entry, current_price, pnl_pct, tp1_dist,
                    )
                    text = (
                        f"📡 {sig.symbol} {direction_word} — still open\n"
                        f"P&L: {pnl_pct:+.2f}% | TP1 in {tp1_dist:.2f}%\n"
                        f"Thesis: {thesis}"
                    )
                    await self._send_telegram(TELEGRAM_ACTIVE_CHANNEL_ID, text)
                    sig._last_pulse_time = now_ts
                except Exception as exc:
                    log.debug("Signal pulse failed for {}: {}", sig.symbol, exc)

    async def start(self) -> None:
        self._running = True
        log.info("Signal router started")
        asyncio.create_task(self._signal_pulse_loop())
        _cleanup_counter = 0
        while self._running:
            try:
                if self._queue_has_timeout:
                    signal = await self._queue.get(timeout=1.0)
                    if signal is None:
                        continue
                else:
                    signal = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                _cleanup_counter += 1
                if _cleanup_counter >= 60:  # roughly every 60 seconds
                    self.cleanup_expired()
                    _cleanup_counter = 0
                    self._log_delivery_stats()
                continue
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.error("Router error: {}", exc)
                continue

            # Reconstruct Signal from dict (Redis deserialization path)
            if isinstance(signal, dict):
                signal = _signal_from_dict(signal)
                if signal is None:
                    continue

            await self._process(signal)

    async def stop(self) -> None:
        self._running = False
        log.info("Signal router stopped")

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------

    def _write_dispatch_log(self, signal: Signal, text: str) -> None:
        """Append a dispatch record to data/dispatch_log.json (rolling cap)."""
        from pathlib import Path

        dispatch_log_path = Path("data/dispatch_log.json")
        dispatch_log_max = 200
        entry = {
            "dispatched_at": time.time(),
            "signal_id": signal.signal_id,
            "channel": signal.channel,
            "symbol": signal.symbol,
            "direction": signal.direction.value,
            "setup_class": getattr(signal, "setup_class", None),
            "confidence": getattr(signal, "confidence", None),
            "signal_tier": getattr(signal, "signal_tier", None),
            "entry": getattr(signal, "entry", None),
            "sl": getattr(signal, "sl", getattr(signal, "stop_loss", None)),
            "tp1": getattr(signal, "tp1", None),
            "tp2": getattr(signal, "tp2", None),
            "tp3": getattr(signal, "tp3", None),
            "market_phase": getattr(signal, "market_phase", None),
            "entry_regime": getattr(signal, "entry_regime", None) or None,
            "entry_regime_15m": getattr(signal, "entry_regime_15m", None) or None,
            "telegram_text": text,
        }
        try:
            dispatch_log_path.parent.mkdir(parents=True, exist_ok=True)
            existing: list = []
            if dispatch_log_path.exists():
                try:
                    existing = json.loads(dispatch_log_path.read_text(encoding="utf-8"))
                    if not isinstance(existing, list):
                        existing = []
                except Exception:
                    existing = []
            existing.append(entry)
            if len(existing) > dispatch_log_max:
                existing = existing[-dispatch_log_max:]
            dispatch_log_path.write_text(
                json.dumps(existing, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as exc:
            log.debug("Failed to write dispatch log: {}", exc)

    def _drop(self, signal: Signal, reason: str) -> None:
        """Count a router rejection and stamp it for forward measurement.

        Returns ``None`` so a call site reads ``return self._drop(sig, "...")``
        and stays a one-line change from the bare ``return`` it replaces.

        Two things happen, and they answer different questions:

        * **The counter** says how much this gate costs in volume. Keyed by
          reason and by ``reason:setup_class``, because "this path never reaches
          a user" and "the market was quiet" produce the same total otherwise.
        * **The suppression stamp** says whether it cost anything in money. The
          audit forward-measures the candidate on real candles and gives the
          gate a WOULD_WIN% and an EV, which is the only way a gate earns or
          loses its place (``CLAUDE.md``). Every other live gate in the engine
          stamps; none of these did.

        Fail-open and silent on error: a measurement must never be the reason a
        signal is mishandled, and ``stamp_candidate`` already refuses cleanly on
        geometry it cannot score.
        """
        setup = str(getattr(signal, "setup_class", "") or "UNKNOWN")
        self._drop_counters[reason] += 1
        self._drop_counters[f"{reason}:{setup}"] += 1
        # A promoted dark row learns here that it never reached anyone, and
        # why. Without this the promotion panel could only say "20 rows were
        # promoted" — which reads as 20 signals delivered, when the correlation
        # lock may have eaten most of them. Those two support opposite readings
        # of the same rule, and only this line can tell them apart. No-ops
        # (returns False) for every ordinary signal, which is nearly all of
        # them: the ledger is only asked about ids it might hold.
        try:
            from src import dark_emission as _de

            _de.mark_router_dropped(
                str(getattr(signal, "signal_id", "") or ""), reason
            )
        except Exception as exc:  # noqa: BLE001
            from src import fail_open as _fo
            _fo.record("signal_router.drop_promoted_stamp", exc)
        try:
            from src import runtime_tunables as _rt
            if not bool(_rt.get("suppression_audit_enabled")):
                return None
            from src import suppression_audit as _sa
            _direction = getattr(signal, "direction", None)
            _sa.stamp_candidate(
                gate_name=f"router:{reason}",
                symbol=str(getattr(signal, "symbol", "") or ""),
                channel=str(getattr(signal, "channel", "") or ""),
                setup_class=setup,
                side=(getattr(_direction, "value", None) or str(_direction or "")),
                entry=float(getattr(signal, "entry", 0.0) or 0.0),
                stop_loss=float(getattr(signal, "stop_loss", 0.0) or 0.0),
                tp1=float(getattr(signal, "tp1", 0.0) or 0.0),
                confidence=float(getattr(signal, "confidence", 0.0) or 0.0),
                context_key=str(getattr(signal, "mc_context_key", "") or ""),
                regime=str(getattr(signal, "entry_regime", "") or ""),
                valid_for_minutes=float(getattr(signal, "valid_for_minutes", 0.0) or 0.0),
                pair_cohort=str(getattr(signal, "mc_pair_cohort", "") or ""),
            )
        except Exception as exc:  # noqa: BLE001
            from src import fail_open as _fo
            _fo.record("signal_router.drop_stamp", exc)
        return None

    # ------------------------------------------------------------------
    # Same-direction cap — the budget, its key, and both modes at once
    # ------------------------------------------------------------------

    @staticmethod
    def direction_budget_key(signal: Signal) -> str:
        """Which budget this candidate spends — one writer, one answer.

        Keyed on ``origin_setup_class``, the scanner-stamped **immutable**
        identity, because ``setup_class`` can be rewritten downstream by
        arbitration and confluence.  A budget whose key can change between the
        moment a signal is admitted and the moment it is counted lets a signal
        decrement a budget it never incremented — and the count here is
        recomputed from the live book on every candidate, so the two ends must
        agree about every row or the cap drifts silently.

        A candidate with no setup identity gets its own named bucket rather
        than sharing one with a real path.  A fallback is not a default: if a
        call site stops stamping, that must be visible as an odd budget rather
        than hidden inside whichever path happens to be quiet.
        """
        origin = str(getattr(signal, "origin_setup_class", "") or "").strip()
        if origin:
            return origin.upper()
        current = str(getattr(signal, "setup_class", "") or "").strip()
        return current.upper() if current else "UNCLASSIFIED"

    def _direction_cap_decision(self, signal: Signal) -> "_DirectionCap":
        """Evaluate BOTH modes; apply the configured one.

        The counterfactual is not a second implementation — it is the same two
        counts read under two rules, so the panel that justifies switching
        cannot disagree with the gate that would do the switching.
        """
        direction = signal.direction
        key = self.direction_budget_key(signal)

        same_dir_total = 0
        same_dir_path = 0
        for s in self._active_signals.values():
            if s.direction != direction:
                continue
            same_dir_total += 1
            if self.direction_budget_key(s) == key:
                same_dir_path += 1

        would_block_global = same_dir_total >= MAX_SAME_DIRECTION_GLOBAL
        would_block_path = same_dir_path >= MAX_SAME_DIRECTION_PER_PATH
        # The cumulative ceiling is a SEPARATE dimension from the per-path
        # budget, and stays separate so the two never pool: a path at its own
        # bound is working and throttled, a book at a cumulative ceiling is a
        # different finding with a different fix.  ``0`` disables it — which is
        # what the owner asked for and what ships.
        cumulative = MAX_SAME_DIRECTION_CUMULATIVE
        would_block_cumulative = bool(cumulative) and same_dir_total >= cumulative

        if DIRECTION_CAP_MODE == "per_path":
            if would_block_path:
                blocked, reason = True, f"per-path cap for {key}"
                count, limit = same_dir_path, MAX_SAME_DIRECTION_PER_PATH
            elif would_block_cumulative:
                blocked, reason = True, "cumulative ceiling"
                count, limit = same_dir_total, cumulative
            else:
                blocked, reason = False, ""
                count, limit = same_dir_path, MAX_SAME_DIRECTION_PER_PATH
        else:
            blocked = would_block_global
            reason = "global cap" if blocked else ""
            count, limit = same_dir_total, MAX_SAME_DIRECTION_GLOBAL

        return _DirectionCap(
            mode=DIRECTION_CAP_MODE,
            key=key,
            direction=direction.value,
            blocked=blocked,
            reason=reason,
            count=count,
            limit=limit,
            same_dir_total=same_dir_total,
            same_dir_path=same_dir_path,
            would_block_global=would_block_global,
            would_block_per_path=would_block_path or would_block_cumulative,
        )

    def _record_direction_cap_counterfactual(self, cap: "_DirectionCap") -> None:
        """Count what each mode WOULD have done to this candidate.

        Four buckets rather than a single "would be delivered" total, because
        the two interesting ones are the disagreements and a total cannot show
        them.  ``global_only`` is the population the owner is asking about:
        candidates the global cap kills that a per-path budget would pass.
        """
        c = self._direction_cap_counterfactual
        c["evaluated"] += 1
        g, p = cap.would_block_global, cap.would_block_per_path
        if g and p:
            c["both_block"] += 1
        elif g:
            c["global_only"] += 1
            c[f"global_only:{cap.key}"] += 1
        elif p:
            c["per_path_only"] += 1
            c[f"per_path_only:{cap.key}"] += 1
        else:
            c["neither_blocks"] += 1

    def direction_cap_report(self) -> Dict[str, Any]:
        """What the cap is doing, and what the other mode would have done.

        Published whether or not the mode has been switched: the effect ships
        default-OFF and the measurement does not, because a decision with
        nowhere to read it is a decision that keeps getting deferred.

        **Counters are cumulative since engine start and reset on restart** —
        they are in-process integers, not a ledger, so a low number after a
        deploy is a young process rather than a quiet market.

        The counterfactual answers *how many more candidates would survive this
        hop* and is structurally incapable of answering *how many more would be
        profitable* — every one of them still faces TP/SL sanity, the staleness
        checks and the channel floor below this gate, and their outcomes are
        unknowable because they never traded.
        """
        c = self._direction_cap_counterfactual
        evaluated = int(c.get("evaluated", 0) or 0)
        flat = {k: v for k, v in c.items() if ":" not in k}
        by_key = {k: v for k, v in c.items() if ":" in k}
        # Live occupancy per (path, direction) — the budgets actually held
        # right now, which is what makes a saturated cap legible as
        # saturation rather than as an absence of candidates.
        held: Dict[str, int] = defaultdict(int)
        for s in self._active_signals.values():
            held[f"{self.direction_budget_key(s)}|{s.direction.value}"] += 1
        return {
            "mode": DIRECTION_CAP_MODE,
            "per_path_limit": MAX_SAME_DIRECTION_PER_PATH,
            "global_limit": MAX_SAME_DIRECTION_GLOBAL,
            # 0 means the cumulative ceiling is OFF, which is a decision
            # somebody made and not an unset value.
            "cumulative_limit": MAX_SAME_DIRECTION_CUMULATIVE,
            "evaluated": evaluated,
            "counterfactual": dict(sorted(flat.items())),
            "counterfactual_by_path": dict(
                sorted(by_key.items(), key=lambda kv: -kv[1])
            ),
            #: Candidates the CURRENT mode kills that the other would pass,
            #: as a share of everything this gate saw.  The number the switch
            #: decision is read from.
            "would_gain": (
                int(c.get("global_only", 0) or 0) if DIRECTION_CAP_MODE == "global"
                else int(c.get("per_path_only", 0) or 0)
            ),
            "would_gain_share": (
                (int(c.get("global_only", 0) or 0) / evaluated) if evaluated
                and DIRECTION_CAP_MODE == "global"
                else (int(c.get("per_path_only", 0) or 0) / evaluated) if evaluated
                else None
            ),
            "budgets_held": dict(sorted(held.items(), key=lambda kv: -kv[1])),
            "budgets_held_total": sum(held.values()),
        }

    def _log_delivery_stats(self) -> None:
        """One line a minute naming where the dequeued signals went.

        The truth report is built from logs by a separate script, so it cannot
        reach these counters on the live object — a log line is how the volume
        gets into the same artifact the rest of the funnel lives in. The EV side
        needs no wiring: ``_drop`` stamps the suppression audit, so each reason
        shows up as a ``router:<reason>`` gate with a KEEP/TUNE/DROP verdict
        beside every other gate.

        Silent while nothing has been processed — a router with an empty queue
        must not fill the log with a row of zeros, which is how a real drop-off
        stops standing out.
        """
        if self._processed_total <= 0:
            return
        stats = self.delivery_stats()
        rate = stats["delivery_rate"]
        log.info(
            "ROUTER_DELIVERY processed={} delivered={} ({}) dropped={} | {}",
            stats["processed"],
            stats["delivered"],
            f"{rate:.1%}" if rate is not None else "n/a",
            stats["dropped"],
            ", ".join(f"{k}={v}" for k, v in stats["drops_by_reason"].items()) or "none",
        )

    def delivery_stats(self) -> Dict[str, Any]:
        """What the router did with what it dequeued.

        The path funnel's ``emitted`` stage is incremented right after
        ``_enqueue_signal`` succeeds, so it counts **enqueues** — this method is
        the other half, and the two together are the enqueue→delivery ratio
        nobody could previously read.
        """
        drops = {k: v for k, v in self._drop_counters.items() if ":" not in k}
        by_setup = {k: v for k, v in self._drop_counters.items() if ":" in k}
        dropped = sum(drops.values())
        return {
            "processed": self._processed_total,
            "delivered": self._delivered_total,
            "dropped": dropped,
            "delivery_rate": (
                self._delivered_total / self._processed_total
                if self._processed_total else None
            ),
            "drops_by_reason": dict(sorted(drops.items(), key=lambda kv: -kv[1])),
            "drops_by_reason_setup": dict(
                sorted(by_setup.items(), key=lambda kv: -kv[1])
            ),
            "position_lock": self.position_lock_health(),
            # The same-direction cap's own X-ray, beside the counter it
            # explains.  `same_direction_throttle` took 91.6% of every drop
            # over one boot and the row above can only say that it did — this
            # says which budgets are held and what the other mode would have
            # passed.
            "direction_cap": self.direction_cap_report(),
        }

    def position_lock_health(self) -> Dict[str, Any]:
        """What ``correlation_lock`` is currently holding, and whether it
        stands behind anything.

        This exists because the gate that drops the most had no way to say
        whether it was *tight* or *stale*, and those are opposite findings
        read off the identical counter.  ``correlation_lock`` at 93% of
        dequeued is blast-radius protection working when the locked symbols
        have positions on them, and a silent outage when they do not — and
        for weeks nothing on any surface could tell them apart.

        ``divergence`` is the number that separates them, and it is live
        rather than historical: on a healthy router it is 0 by construction,
        because the two maps are written on the same line.  Anything else
        means a path has broken that pairing and the reconcile at restore
        will not see it until the next boot.
        """
        active_symbols = {sig.symbol for sig in self._active_signals.values()}
        locked = set(self._position_lock)
        orphaned = sorted(locked - active_symbols)
        unlocked = sorted(active_symbols - locked)
        return {
            "locked": len(locked),
            "active_signals": len(self._active_signals),
            "active_symbols": len(active_symbols),
            # Live divergence — an orphan here is one the reconcile has not
            # run against yet, i.e. created after boot.  Both lists are
            # bounded for the surface; the counts above are not.
            "orphaned_now": len(orphaned),
            "unlocked_now": len(unlocked),
            "orphaned_sample": orphaned[:20],
            "unlocked_sample": unlocked[:20],
            # Repaired at the last restore — the evidence that the skew
            # happened at all, which nothing else records.
            "orphans_dropped_at_restore": self._lock_orphans_dropped,
            "missing_added_at_restore": self._lock_missing_added,
            "direction_corrected_at_restore": self._lock_direction_corrected,
        }

    async def _process(self, signal: Signal) -> None:
        self._processed_total += 1
        # WATCHLIST tier was removed in the app-era doctrine reset; sub-65
        # confidence signals never reach this path because the scanner drops
        # them at the min_confidence gate.  Defensive: should anything tier
        # a signal as WATCHLIST going forward, drop it silently here too.
        if getattr(signal, "signal_tier", "") == "WATCHLIST":
            return self._drop(signal, "watchlist_tier")

        # Correlation lock – block any signal for a symbol that already has an
        # open position (regardless of direction to prevent same-dir duplicates)
        existing_dir = self._position_lock.get(signal.symbol)
        if existing_dir is not None:
            log.info(
                "Blocked {} {} – existing {} position open",
                signal.symbol, signal.direction.value, existing_dir.value,
            )
            return self._drop(signal, "correlation_lock")

        # Per-symbol + per-channel cooldown check
        cooldown_key = (signal.symbol, signal.channel)
        last_completed = self._cooldown_timestamps.get(cooldown_key)
        if last_completed is not None:
            cooldown_secs = CHANNEL_COOLDOWN_SECONDS.get(signal.channel, 60)
            elapsed = (datetime.now(timezone.utc) - last_completed).total_seconds()
            if elapsed < cooldown_secs:
                log.info(
                    "Cooldown active for {} {} – {:.1f}s remaining ({:.0f}s window)",
                    signal.symbol, signal.channel,
                    cooldown_secs - elapsed, cooldown_secs,
                )
                return self._drop(signal, "symbol_channel_cooldown")

        # Per-channel concurrent position cap
        channel_count = sum(
            1 for s in self._active_signals.values() if s.channel == signal.channel
        )
        channel_max = MAX_CONCURRENT_SIGNALS_PER_CHANNEL.get(signal.channel, 5)
        if channel_count >= channel_max:
            log.info(
                "Per-channel cap reached for {} ({}/{}) – {} {} blocked",
                signal.channel, channel_count, channel_max,
                signal.symbol, signal.direction.value,
            )
            return self._drop(signal, "per_channel_cap")

        # Correlation-aware position limiting (group-based)
        active_positions = {
            sid: (s.symbol, s.direction.value)
            for sid, s in self._active_signals.items()
        }
        corr_allowed, corr_reason = check_correlation_limit(
            symbol=signal.symbol,
            direction=signal.direction.value,
            active_positions=active_positions,
        )
        if not corr_allowed:
            log.info(
                "Blocked {} {} – {}",
                signal.symbol, signal.direction.value, corr_reason,
            )
            return self._drop(signal, "correlation_group_limit")

        # Same-direction cap (Correlation Throttle) — global or per path.
        #
        # Top-75 USDT-M alts are 0.85-0.95 correlated to BTC; when BTC
        # dumps/pumps all same-direction positions SL simultaneously.  The
        # group-based check above only covers ~25 named pairs; this catch-all
        # prevents blast-radius on the long tail of alts.
        #
        # In ``global`` mode the budget belongs to the book, which measured
        # 91.6% of every drop the router made over one 10.5h boot: three long
        # slots against a market where every candidate was long, and the
        # highest-volume path holding them by arithmetic.  In ``per_path`` mode
        # the budget belongs to each path, so a strategy cannot be starved by a
        # noisier neighbour.  Both are evaluated on every candidate whatever
        # the mode, and the counterfactual is published — the decision to
        # switch is read off what the OTHER mode would have done, not guessed.
        cap = self._direction_cap_decision(signal)
        self._record_direction_cap_counterfactual(cap)
        if cap.blocked:
            log.info(
                "correlation_throttle skip {} {} – {} ({}/{} in {} mode)",
                signal.symbol, signal.direction.value, cap.reason,
                cap.count, cap.limit, cap.mode,
            )
            return self._drop(signal, "same_direction_throttle")

        # TP direction sanity – reject signals where TP1 is on wrong side of entry
        if signal.direction == Direction.LONG and signal.tp1 <= signal.entry:
            log.warning(
                "Signal {} {} LONG has TP1 {:.8f} <= entry {:.8f} – rejected",
                signal.symbol, signal.channel, signal.tp1, signal.entry,
            )
            return self._drop(signal, "tp_sanity")
        if signal.direction == Direction.SHORT and signal.tp1 >= signal.entry:
            log.warning(
                "Signal {} {} SHORT has TP1 {:.8f} >= entry {:.8f} – rejected",
                signal.symbol, signal.channel, signal.tp1, signal.entry,
            )
            return self._drop(signal, "tp_sanity")

        # SL direction sanity – reject signals where SL is on wrong side of entry
        if signal.direction == Direction.LONG and signal.stop_loss >= signal.entry:
            log.warning(
                "Signal {} {} LONG has SL {:.8f} >= entry {:.8f} – rejected",
                signal.symbol, signal.channel, signal.stop_loss, signal.entry,
            )
            return self._drop(signal, "sl_sanity")
        if signal.direction == Direction.SHORT and signal.stop_loss <= signal.entry:
            log.warning(
                "Signal {} {} SHORT has SL {:.8f} <= entry {:.8f} – rejected",
                signal.symbol, signal.channel, signal.stop_loss, signal.entry,
            )
            return self._drop(signal, "sl_sanity")

        # ── Stale signal gate ───────────────────────────────────────────────
        # Check whether the signal is still actionable before posting.
        if signal.detected_at is not None:
            now_ts = time.time()
            elapsed_s = now_ts - signal.detected_at

            # Time-based staleness: signal exceeded its validity window.
            is_scalp = signal.channel in _SCALP_CHANNEL_NAMES
            stale_threshold = (
                _SCALP_STALE_THRESHOLD_SECONDS if is_scalp
                else _DEFAULT_STALE_THRESHOLD_SECONDS
            )
            if elapsed_s > stale_threshold:
                log.warning(
                    "STALE signal {} {} {}: detected→now {:.1f}s > {:.0f}s threshold – suppressed",
                    signal.channel, signal.symbol, signal.direction.value,
                    elapsed_s, stale_threshold,
                )
                return self._drop(signal, "stale_age")

            # Price-based staleness: check against detection-time price (current_price).
            # This catches the case where the price was already past TP1 or SL
            # at the moment the signal was detected (e.g. due to a slow scan cycle).
            if signal.current_price > 0:
                cp = signal.current_price
                if signal.direction == Direction.LONG:
                    if cp > signal.tp1:
                        log.warning(
                            "STALE signal {} {} LONG: detection-time price {:.8f} already past "
                            "TP1 {:.8f} – suppressed",
                            signal.channel, signal.symbol, cp, signal.tp1,
                        )
                        return self._drop(signal, "stale_past_tp1")
                    if cp < signal.stop_loss:
                        log.warning(
                            "STALE signal {} {} LONG: detection-time price {:.8f} already below "
                            "SL {:.8f} – suppressed",
                            signal.channel, signal.symbol, cp, signal.stop_loss,
                        )
                        return self._drop(signal, "stale_past_sl")
                else:  # SHORT
                    if cp < signal.tp1:
                        log.warning(
                            "STALE signal {} {} SHORT: detection-time price {:.8f} already past "
                            "TP1 {:.8f} – suppressed",
                            signal.channel, signal.symbol, cp, signal.tp1,
                        )
                        return self._drop(signal, "stale_past_tp1")
                    if cp > signal.stop_loss:
                        log.warning(
                            "STALE signal {} {} SHORT: detection-time price {:.8f} already above "
                            "SL {:.8f} – suppressed",
                            signal.channel, signal.symbol, cp, signal.stop_loss,
                        )
                        return self._drop(signal, "stale_past_sl")

        # ── AI enrichment ───────────────────────────────────────────────
        signal = await self._enrich_with_ai(signal)

        # Channel min-confidence filter
        chan_cfg = next(
            (c for c in ALL_CHANNELS if c.name == signal.channel), None
        )
        if chan_cfg and signal.confidence < chan_cfg.min_confidence:
            log.debug(
                "Signal {} {} confidence {:.1f} < min {:.1f} – skipped",
                signal.channel, signal.symbol,
                signal.confidence, chan_cfg.min_confidence,
            )
            return self._drop(signal, "channel_min_confidence")

        # Risk assessment: use the signal's own volume/spread fields so the risk
        # classifier has accurate data (set by the scanner before enqueuing).
        risk = self._risk_mgr.calculate_risk(
            signal, {}, volume_24h_usd=signal.volume_24h_usd,
            active_signals=self.active_signals,
        )
        if not risk.allowed:
            log.warning(
                "Signal {} {} blocked by risk manager: {}",
                signal.symbol, signal.direction.value, risk.reason,
            )
            return
        signal.risk_label = risk.risk_label

        # Format and send to premium channel
        channel_id = CHANNEL_TELEGRAM_MAP.get(signal.channel, "")
        if not channel_id:
            log.warning("No Telegram channel configured for {}", signal.channel)
            return

        text = self._format_signal(signal)

        # Append Cornix auto-execution block when enabled
        try:
            from config import CORNIX_FORMAT_ENABLED
            if CORNIX_FORMAT_ENABLED:
                cornix_block = format_cornix_signal(signal)
                if cornix_block:
                    text = text + "\n\n" + cornix_block
        except Exception as _exc:
            log.debug("Cornix format skipped: {}", _exc)

        delivered = False
        try:
            delivered = await self._send_telegram(channel_id, text)
        except Exception as exc:
            log.warning(
                "Signal delivery failed for {} {}: {}",
                signal.channel,
                signal.signal_id,
                exc,
            )
        if not delivered:
            retries = signal._delivery_retries
            if retries < 2:
                signal._delivery_retries = retries + 1
                log.info(
                    "Re-queuing {} {} (delivery attempt {}/3)",
                    signal.channel,
                    signal.signal_id,
                    retries + 2,
                )
                await _delivery_sleep(2 ** retries)  # 1 s, 2 s for retries 0, 1
                await self._queue.put(signal)
            else:
                log.error(
                    "Signal {} {} permanently lost after 3 delivery attempts",
                    signal.channel,
                    signal.signal_id,
                )
                # Notify admin about the lost signal (FINDING-023)
                try:
                    from src.telegram_bot import TelegramBot
                    bot = getattr(self._send_telegram, "__self__", None)
                    if isinstance(bot, TelegramBot):
                        await bot.send_admin_alert(
                            f"🚨 *Signal Lost*\n"
                            f"Channel: {signal.channel}\n"
                            f"Symbol: {signal.symbol}\n"
                            f"Direction: {signal.direction.value}\n"
                            f"Signal ID: {signal.signal_id}\n"
                            f"Failed after 3 delivery attempts."
                        )
                except Exception:
                    pass  # Best-effort — don't mask the original failure
            return
        self._write_dispatch_log(signal, text)
        log.info(
            "Signal posted → {} | {} {}",
            signal.channel,
            signal.symbol,
            signal.direction.value,
        )

        # ── Server-side execution dispatch (PR-A of the wiring follow-ups) ──
        # Fan the signal out to every user with a connected Binance
        # key.  Each per-user FSM call is independent: tripwire
        # rejections (symbol allowlist, position cap, etc.) and
        # transient failures (KMS outage) are logged inside the
        # dispatcher and don't propagate.  No-op when no users have
        # connected (cold deploy / legacy-only path).
        try:
            from src.execution import signal_dispatch as _sd

            await _sd.dispatch_signal_to_active_users(
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
                entry_zone_low=getattr(signal, "entry_zone_low", None),
                entry_zone_high=getattr(signal, "entry_zone_high", None),
                valid_for_minutes=int(getattr(signal, "valid_for_minutes", 0) or 0),
                current_price=float(getattr(signal, "current_price", 0.0) or 0.0),
                # Noise-floor risk-constant sizing: stop widened ×F → size ÷F.
                risk_scale=(
                    1.0 / float(getattr(signal, "noise_floor_widen_factor", 1.0) or 1.0)
                    if float(getattr(signal, "noise_floor_widen_factor", 1.0) or 1.0) > 1.0
                    else 1.0
                ),
            )
        except Exception:
            log.exception(
                "Server-side dispatch raised — Telegram delivery already "
                "succeeded; subscribers see the signal regardless"
            )

        # ── Latency tracking ─────────────────────────────────────────────────
        signal.posted_at = time.time()
        signal.dispatch_timestamp = datetime.now(timezone.utc)
        if signal.detected_at is not None:
            latency_ms = (signal.posted_at - signal.detected_at) * 1000.0
            signal.enrichment_latency_ms = latency_ms
            log.info(
                "{} {} signal: detected→posted latency = {:,.0f}ms",
                signal.symbol, signal.channel, latency_ms,
            )
            if signal.channel in _SCALP_CHANNEL_NAMES and latency_ms > _SCALP_LATENCY_WARNING_SECONDS * 1000:
                log.warning(
                    "HIGH LATENCY {} {} SCALP signal: {:.1f}s detected→posted (threshold={:.0f}s)",
                    signal.symbol, signal.channel,
                    latency_ms / 1000.0, _SCALP_LATENCY_WARNING_SECONDS,
                )

        # Register only after confirmed delivery
        self._delivered_total += 1
        self._active_signals[signal.signal_id] = signal
        self._position_lock[signal.symbol] = signal.direction
        self._schedule_persist()

        # Provenance promotion (2026-07-25) — this is the ONLY place a shadow
        # record becomes EMITTED. The scanner stamps ENQUEUED when the queue
        # accepts a candidate, but every gate above this line can still drop
        # it, so "queued" and "sent" are different populations and only this
        # one can justify changing what subscribers receive. Measurement-only:
        # re-labels a ledger row, touches no exit, FSM or dispatch behaviour.
        try:
            from src import sar_exit_shadow as _sar
            _sar.promote_to_emitted(
                symbol=signal.symbol,
                setup_class=str(getattr(signal, "setup_class", "") or ""),
                side=signal.direction.value,
                entry=float(getattr(signal, "entry", 0.0) or 0.0),
            )
        except Exception as _prom_exc:
            from src import fail_open
            fail_open.record("router.promote_sar_provenance", _prom_exc)

        # The same point, for the dark→live promotion lane, and for the same
        # reason: this is the ONLY line that knows a promoted candidate became
        # a signal a subscriber can see. `promoted_enqueued` is not a delivery
        # and the ops panel must never round it up to one — the whole rule
        # about enqueue-is-not-dispatch, arriving at the mechanism that
        # deliberately puts more rows into the queue. Keyed on `signal_id`,
        # which is exact; the SAR promotion above matches fuzzily because its
        # store is not id-keyed, and that is not inherited here.
        try:
            from src import dark_emission as _de
            _de.mark_delivered(str(getattr(signal, "signal_id", "") or ""))
        except Exception as _dp_exc:
            from src import fail_open
            fail_open.record("router.promote_dark_delivery", _dp_exc)

        # Retention by delivery (Phase 6). Same point, same reason: enqueue is
        # not delivery, and only this line knows the difference. Every
        # measurement ring is filled by enqueues of which ~0.5% get here, so
        # evict-by-recency spends the cap destroying the confirmed rows to make
        # room for the unconfirmed ones — silently, since the ledger stays
        # exactly full. This marks the row so it can never be evicted by one.
        #
        # Keyed on `signal_id`, which is exact. The SAR promotion above matches
        # on (symbol, side, setup, entry) within a time window because its store
        # is not keyed by id; that fuzziness is not inherited here.
        try:
            from src import delivery_retention as _dr
            _dr.mark_delivered(signal.signal_id)
        except Exception as _ret_exc:
            from src import fail_open
            fail_open.record("router.mark_delivered", _ret_exc)

        # FCM push to the app's `signals` topic — fire-and-forget, off the
        # dispatch path (push_notifications never blocks and never raises).
        push_signal_published(signal)

        # Track for daily free-channel picks
        self._daily_best.append(signal)
        self._daily_best.sort(key=lambda s: s.confidence, reverse=True)
        self._trim_daily_best()

        # Publish a condensed version to the free channel (Phase 4)
        await self._maybe_publish_free_signal(signal)

        # Notify AI Trade Observer — capture market state at signal publish time
        if self.observer is not None:
            try:
                self.observer.capture_entry_snapshot(signal)
            except Exception as exc:
                log.debug("TradeObserver.capture_entry_snapshot failed (non-critical): {}", exc)

        # Notify the free-watch service so any open radar watch for this
        # symbol+direction can be resolved to "rolled_into_paid_signal".
        if self.on_signal_routed is not None:
            try:
                await self.on_signal_routed(
                    symbol=signal.symbol,
                    bias=signal.direction.value,
                )
            except Exception as exc:
                log.debug("on_signal_routed callback error: {}", exc)

    async def _send_photo(self, channel_id: str, photo_bytes: bytes) -> bool:
        """Send a chart image to *channel_id*.

        Uses the TelegramBot instance if available via _send_telegram, otherwise
        calls send_photo directly on a TelegramBot instance.
        """
        try:
            from src.telegram_bot import TelegramBot
            # Retrieve the bot instance bound to _send_telegram if possible
            bot = getattr(self._send_telegram, "__self__", None)
            if isinstance(bot, TelegramBot):
                return await bot.send_photo(channel_id, photo_bytes)
            # Fall back to creating a transient bot (token taken from env)
            tmp_bot = TelegramBot()
            return await tmp_bot.send_photo(channel_id, photo_bytes)
        except Exception as exc:
            log.warning("_send_photo failed: {}", exc)
            return False

    # ------------------------------------------------------------------
    # Free-channel publication (call once/day or on demand)
    # ------------------------------------------------------------------

    def _trim_daily_best(self) -> None:
        """Trim ``_daily_best`` to the current free-signal limit."""
        self._daily_best = self._daily_best[:self._free_limit]

    def set_free_limit(self, limit: int) -> None:
        """Update the maximum number of daily free signals."""
        self._free_limit = max(0, limit)
        self._trim_daily_best()

    async def publish_free_signals(self) -> None:
        """Post the top free signals of the day to the free channel.

        .. deprecated::
            Use :meth:`publish_daily_recap` instead.  This method is kept for
            backward compatibility (tests reference it).
        """
        if not self._daily_best or not TELEGRAM_FREE_CHANNEL_ID:
            return
        for sig in self._daily_best:
            text = self._format_signal(sig)
            header = "🆓 *FREE SIGNAL OF THE DAY* 🆓\n\n"
            footer = (
                "\n\n📚 _Tip: Scalping requires discipline. "
                "Always use a stop-loss and manage risk._"
            )
            await self._send_telegram(TELEGRAM_FREE_CHANNEL_ID, header + text + footer)
        self._daily_best.clear()

    async def publish_highlight(self, sig: Signal, tp_level: int, tp_pnl_pct: float) -> None:
        """Post a winning trade highlight to the free channel.

        Called by the trade monitor when a signal hits TP2 or higher.
        Rate-limited to ``_FREE_HIGHLIGHT_MAX_PER_DAY`` highlights per day.
        """
        if not TELEGRAM_FREE_CHANNEL_ID:
            return
        if tp_level < _FREE_HIGHLIGHT_MIN_TP:
            return

        # Daily rate limit
        today = date.today()
        if self._highlight_date != today:
            self._highlight_date = today
            self._highlight_count_today = 0
        if self._highlight_count_today >= _FREE_HIGHLIGHT_MAX_PER_DAY:
            log.debug(
                "Free highlight daily limit reached ({}/{})",
                self._highlight_count_today,
                _FREE_HIGHLIGHT_MAX_PER_DAY,
            )
            return

        text = self._format_highlight(sig, tp_level, tp_pnl_pct)
        try:
            await self._send_telegram(TELEGRAM_FREE_CHANNEL_ID, text)
            self._highlight_count_today += 1
            log.info(
                "Posted free highlight: {} {} TP{} +{:.2f}%",
                sig.symbol, sig.direction.value, tp_level, tp_pnl_pct,
            )
            log.info(
                "free_channel_post source=signal_highlight severity=HIGH symbol={}",
                sig.symbol,
            )
        except Exception as exc:
            log.warning("Failed to post free highlight: {}", exc)

    def _format_highlight(self, sig: Signal, tp_level: int, tp_pnl_pct: float) -> str:
        """Delegate highlight formatting to TelegramBot."""
        from src.telegram_bot import TelegramBot
        return TelegramBot.format_highlight_message(sig, tp_level, tp_pnl_pct)

    async def publish_daily_recap(self, performance_tracker: Any) -> None:
        """Post the daily performance recap to the free channel."""
        if not TELEGRAM_FREE_CHANNEL_ID:
            return

        summary = performance_tracker.get_daily_summary(window_days=1)
        if summary["total"] == 0:
            return  # No trades today, skip

        text = self._format_daily_recap(summary)
        try:
            await self._send_telegram(TELEGRAM_FREE_CHANNEL_ID, text)
            log.info("Posted daily recap to free channel")
        except Exception as exc:
            log.warning("Failed to post daily recap: {}", exc)

    def _format_daily_recap(self, summary: Any) -> str:
        """Delegate daily recap formatting to TelegramBot."""
        from src.telegram_bot import TelegramBot
        return TelegramBot.format_daily_recap(summary)

    # ------------------------------------------------------------------
    # Free channel – condensed signal (Phase 4)
    # ------------------------------------------------------------------

    @staticmethod
    def _free_channel_group(channel: str) -> str:
        """Map a signal channel to a user-facing group name for free-signal tracking."""
        return "active"

    # ------------------------------------------------------------------
    # WATCHLIST free-channel routing (doctrine: 50-64 → free only)
    # ------------------------------------------------------------------

    # WATCHLIST routing methods removed in the app-era doctrine reset.  The
    # free Telegram channel keeps macro / regime-shift / signal-close
    # storytelling but no preview signals; signals below paid threshold
    # (65 confidence) drop cleanly at the scanner gate.

    async def _maybe_publish_free_signal(self, signal: Signal) -> None:
        """Publish a condensed version of the signal to the free channel.

        Only posts once per calendar day, and only when confidence >= 75.
        """
        if not TELEGRAM_FREE_CHANNEL_ID:
            return

        # Reset tracking on a new day
        today = date.today()
        if self._free_signal_date != today:
            self._free_signal_date = today
            self._free_signals_today = {}

        group = self._free_channel_group(signal.channel)
        if self._free_signals_today.get(group):
            return  # Already posted for this group today
        if signal.confidence < 75:
            return  # Only show high-confidence signals for free

        text = self._format_condensed_free(signal)
        try:
            await self._send_telegram(TELEGRAM_FREE_CHANNEL_ID, text)
            self._free_signals_today[group] = True
            log.info(
                "Posted free condensed signal ({} group): {} {}",
                group, signal.symbol, signal.direction.value,
            )
        except Exception as exc:
            log.warning("Failed to post condensed free signal: {}", exc)

    def _format_condensed_free(self, signal: Signal) -> str:
        """Format a condensed free-channel version of a signal (Entry/SL/TP1 only)."""
        from src.telegram_bot import TelegramBot
        from src.utils import fmt_price

        chan_emojis = {
            "360_SCALP":            "⚡",
            "360_SCALP_FVG":        "⚡",
            "360_SCALP_CVD":        "⚡",
            "360_SCALP_VWAP":       "⚡",
            "360_SCALP_DIVERGENCE": "⚡",
            "360_SCALP_SUPERTREND": "⚡",
            "360_SCALP_ICHIMOKU":   "⚡",
            "360_SCALP_ORDERBLOCK": "⚡",
        }
        emoji = chan_emojis.get(signal.channel, "📡")
        chan_name = TelegramBot._CHANNEL_DISPLAY_NAME.get(signal.channel, signal.channel)
        # Show signal type in the free-channel preview header too.
        if signal.setup_class and signal.setup_class != "UNCLASSIFIED":
            type_suffix = " │ " + signal.setup_class.replace("_", " ")
        else:
            type_suffix = ""
        dir_word = signal.direction.value

        def _pct(price: float) -> str:
            if signal.entry and signal.entry != 0:
                pct = (price - signal.entry) / signal.entry * 100
                return f"{pct:+.2f}%"
            return ""

        lines = [
            "🆓 *FREE SIGNAL PREVIEW* 🆓",
            "",
            f"{emoji} *{TelegramBot._escape_md(chan_name + type_suffix)}* │ *{TelegramBot._escape_md(signal.symbol)}* │ *{dir_word}*",
            TelegramBot._escape_md("━" * 24),
            "",
            f"📍 Entry: `{fmt_price(signal.entry)}`",
            f"🛑 SL: `{fmt_price(signal.stop_loss)}` ({TelegramBot._escape_md(_pct(signal.stop_loss))})",
            f"🎯 TP1: `{fmt_price(signal.tp1)}` ({TelegramBot._escape_md(_pct(signal.tp1))})",
            "",
            "🔒 _Premium members see TP2, TP3 and full analysis_",
            "📲 _Join our premium channel for real-time signals_",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Scoreboard (Phase 3)
    # ------------------------------------------------------------------

    async def publish_scoreboard(self, performance_tracker: Any) -> None:
        """Post the weekly win-rate scoreboard to the free channel."""
        if not TELEGRAM_FREE_CHANNEL_ID:
            return

        scoreboard = performance_tracker.get_channel_scoreboard(window_days=7)
        if not scoreboard:
            return

        text = self._format_scoreboard(scoreboard)
        try:
            await self._send_telegram(TELEGRAM_FREE_CHANNEL_ID, text)
            log.info("Posted weekly scoreboard to free channel")
        except Exception as exc:
            log.warning("Failed to post scoreboard: {}", exc)

    @staticmethod
    def _format_scoreboard(scoreboard: Dict[str, Any]) -> str:
        """Format the weekly scoreboard for Telegram."""
        chan_emojis = {
            "360_SCALP":            "⚡",
            "360_SCALP_FVG":        "⚡",
            "360_SCALP_CVD":        "⚡",
            "360_SCALP_VWAP":       "⚡",
            "360_SCALP_DIVERGENCE": "⚡",
            "360_SCALP_SUPERTREND": "⚡",
            "360_SCALP_ICHIMOKU":   "⚡",
            "360_SCALP_ORDERBLOCK": "⚡",
        }
        chan_labels = {
            "360_SCALP":            "Scalp",
            "360_SCALP_FVG":        "Scalp FVG",
            "360_SCALP_CVD":        "Scalp CVD",
            "360_SCALP_VWAP":       "Scalp VWAP",
            "360_SCALP_DIVERGENCE": "Scalp Divergence",
            "360_SCALP_SUPERTREND": "Scalp Supertrend",
            "360_SCALP_ICHIMOKU":   "Scalp Ichimoku",
            "360_SCALP_ORDERBLOCK": "Scalp Orderblock",
        }
        separator = "━" * 30
        lines = [
            "📊 *360 Crypto — Weekly Performance*",
            separator,
            "",
        ]

        total_wins = 0
        total_losses = 0

        for channel in [
            "360_SCALP", "360_SCALP_FVG", "360_SCALP_CVD",
            "360_SCALP_VWAP",
            "360_SCALP_DIVERGENCE", "360_SCALP_SUPERTREND",
            "360_SCALP_ICHIMOKU", "360_SCALP_ORDERBLOCK",
        ]:
            data = scoreboard.get(channel)
            if not data:
                continue
            emoji = chan_emojis.get(channel, "📡")
            label = chan_labels.get(channel, channel)
            wins = data["wins"]
            losses = data["losses"]
            win_rate = data["win_rate"]
            avg_pnl = data["avg_pnl"]
            total_wins += wins
            total_losses += losses
            wr_str = f"({win_rate:.0f}%)"
            lines.append(
                f"{emoji} {label}:  {wins}W / {losses}L  {wr_str}  Avg {avg_pnl:+.1f}%"
            )

        # Grand total
        grand_total = total_wins + total_losses
        grand_wr = round(total_wins / grand_total * 100, 1) if grand_total > 0 else 0.0
        lines.extend([
            separator,
            f"Total: {total_wins}W / {total_losses}L ({grand_wr:.1f}%)",
            "",
            "📈 _Join our premium channels for real-time signals._",
            "⏰ _Updated every Sunday._",
        ])

        return "\n".join(lines)

    @property
    def active_signals(self) -> Dict[str, Signal]:
        return dict(self._active_signals)

    def remove_signal(self, signal_id: str) -> None:
        sig = self._active_signals.pop(signal_id, None)
        if sig:
            self._position_lock.pop(sig.symbol, None)
            # Record cooldown timestamp so we suppress rapid re-entry
            self._cooldown_timestamps[(sig.symbol, sig.channel)] = datetime.now(timezone.utc)
            self._schedule_persist()

    def update_signal(self, signal_id: str, **kwargs) -> None:
        sig = self._active_signals.get(signal_id)
        if sig:
            for k, v in kwargs.items():
                if hasattr(sig, k):
                    setattr(sig, k, v)
            self._schedule_persist()

    async def _notify_signal_expiry(self, sig: Signal, now: datetime) -> None:
        """Post a Telegram notification when a signal expires.

        Sends to ``TELEGRAM_ACTIVE_CHANNEL_ID`` so subscribers know what happened
        to the signal instead of it silently disappearing.  When the engine's
        ``on_signal_expired`` callback has stamped a close price and realised
        P&L on the signal, surface them honestly — auto-trade users in
        particular need to see at what price the position closed.  Falls back
        to a "no P&L" line only when the entry was never filled (no
        ``current_price`` ever recorded).
        """
        if not TELEGRAM_ACTIVE_CHANNEL_ID:
            return
        try:
            direction_emoji = "🟢" if sig.direction == Direction.LONG else "🔴"
            setup_label = SIGNAL_TYPE_LABELS.get(sig.setup_class, sig.setup_class)
            age_secs = (now - sig.timestamp).total_seconds()
            hours = int(age_secs // 3600)
            minutes = int((age_secs % 3600) // 60)

            current_price = float(getattr(sig, "current_price", 0.0) or 0.0)
            entry = float(getattr(sig, "entry", 0.0) or 0.0)
            pnl_pct = float(getattr(sig, "pnl_pct", 0.0) or 0.0)
            entry_was_reached = current_price > 0 and entry > 0 and abs(
                current_price - entry
            ) > 1e-9 or pnl_pct != 0.0

            lines = [
                f"⏰ Signal Expired — {sig.symbol}",
                "",
                f"{direction_emoji} {sig.direction.value} | {setup_label}",
            ]
            if entry_was_reached:
                pnl_sign = "+" if pnl_pct >= 0 else ""
                lines += [
                    "Max-hold reached. Position auto-closed at market.",
                    "",
                    f"📍 Entry: {entry}",
                    f"🏁 Closed at: {current_price}",
                    f"📊 P&L: {pnl_sign}{pnl_pct:.2f}%",
                    f"⏱ Time held: {hours}h {minutes}m",
                    f"📊 Confidence was: {sig.confidence:.0f}",
                ]
            else:
                lines += [
                    "Entry was not reached within the validity window.",
                    "",
                    f"📍 Entry: {entry}",
                    f"⏱ Time held: {hours}h {minutes}m",
                    f"📊 Confidence was: {sig.confidence:.0f}",
                    "",
                    "No fill — no P&L recorded.",
                ]
            await self._send_telegram(TELEGRAM_ACTIVE_CHANNEL_ID, "\n".join(lines))
        except Exception as exc:
            log.debug("Signal expiry notification failed for {}: {}", sig.symbol, exc)

    def cleanup_expired(self) -> int:
        """Remove signals that have exceeded their max hold duration.

        This provides a safety net to ensure :attr:`_position_lock` entries
        are always cleaned up even when the :class:`~src.trade_monitor.TradeMonitor`
        callback is not triggered (e.g. after a process restart where Redis
        state was restored but the signal is already past its TTL).

        Returns the number of signals that were expired and removed.
        """
        # Honour the signal-expiry toggle — the same gate ``trade_monitor``
        # uses (trade_monitor.py:1533). Without this, THIS path force-closed
        # every signal at the 1h max-hold regardless of the owner's OFF
        # setting: the switch gated trade_monitor's expiry but not this
        # safety-net sweep (which the scanner runs every ~15s), so signals
        # kept expiring at 60m — surrendering +MFE the owner disabled expiry
        # to keep (2026-07-08 diagnosis). When expiry is OFF, signals run to
        # TP/SL only; position-lock cleanup for resolved signals still happens
        # in ``remove_signal`` on every normal close, so nothing leaks.
        from src.execution import kill_switch as _ks

        if not _ks.signal_expiry_enabled(SIGNAL_EXPIRY_ENABLED):
            return 0

        now = datetime.now(timezone.utc)
        expired_ids = []
        for signal_id, sig in list(self._active_signals.items()):
            max_hold = MAX_SIGNAL_HOLD_SECONDS.get(sig.channel, 86400)
            age_secs = (now - sig.timestamp).total_seconds()
            if age_secs >= max_hold:
                expired_ids.append(signal_id)

        for signal_id in expired_ids:
            sig = self._active_signals.get(signal_id)
            if sig is None:
                continue
            # Engine hook fires BEFORE we drop the signal so it can compute
            # realised P&L, archive into _signal_history, close the broker
            # position, and stamp a perf-tracker record.  Without this the
            # cleanup silently drops the signal and the app's Closed→Expired
            # sub-filter shows nothing.
            if self.on_signal_expired is not None:
                try:
                    self.on_signal_expired(sig, now)
                except Exception as exc:  # noqa: BLE001 — safety-net path
                    log.warning(
                        "on_signal_expired callback failed for {}: {}",
                        sig.signal_id, exc,
                    )
            self._active_signals.pop(signal_id, None)
            self._position_lock.pop(sig.symbol, None)
            # Record cooldown timestamp so rapid re-entry is suppressed
            self._cooldown_timestamps[(sig.symbol, sig.channel)] = now
            log.info(
                "Auto-expired signal {} {} {} (exceeded max hold)",
                signal_id, sig.symbol, sig.channel,
            )
            # Post expiry notification to Telegram (fire-and-forget).
            # Reads sig.current_price and sig.pnl_pct that on_signal_expired
            # may have just stamped, so the message includes a real outcome
            # instead of "No P&L recorded".
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._notify_signal_expiry(sig, now))
            except RuntimeError:
                pass

        if expired_ids:
            self._schedule_persist()

        return len(expired_ids)
