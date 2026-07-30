"""Live SAR exit mechanism — measured forward, in real time, on open signals.

**Why this exists, and why it is not the third copy of something we already had.**

Two SAR surfaces preceded this one, and the owner's 2026-07-30 export showed why
neither can ever justify enabling a SAR exit for users:

* ``sar_exit_shadow`` (``@SARBASE`` / ``@SAREXIT``) stamps a candidate and then
  *replays* candles 15 minutes to 48 hours later. On that export, 8 of 19 rows
  were still unresolved — including **all four** of the window's winners — so the
  arm's verdict was an artefact of which symbols the resolver's refresh budget
  happened to reach. Two more rows carried an entry 0.4–0.6% away from the one
  the router actually dispatched.
* The ops Performance tab's dark-signals bake-off replays Binance klines *after*
  the engine has already closed the trade. It resolves everything and it is
  honest, but it is still hindsight: it has never once computed a stop while a
  position was open.

Both answer "what would SAR have done, looking back". Neither answers the only
question that gates a live rollout: **can we compute the stop in time, park it,
and act on the flip, on the money-path clock, before the outcome is known.**
That is what this module measures, and it is why it lives in the monitor loop
rather than in a resolver.

The mechanism (owner-specified, 2026-07-30)
-------------------------------------------
At signal generation, read SAR's direction on the last **closed** bar:

* **SAR agrees with the signal** → SAR governs from bar one. The original SL and
  TP1 are never used. The trade exits when SAR flips.
* **SAR opposes the signal** → the original SL and TP1 stay live. Each bar we
  re-check: the moment SAR comes onside, SL and TP1 are cancelled and SAR takes
  over. If SAR never comes onside, the trade closes on its original SL or TP1 —
  a TP1 touch closes it **in full** (owner's call; no runner in this arm).

Measured on **5m and 15m in parallel**, as two independent arms per signal, so
the timeframe question is answered by the same window that answers the
mechanism question.

Two fills, and why both are recorded
------------------------------------
The owner's rule says "when SAR flips, close at market". Read literally that
leaves no resting stop between bars, which would violate
``Never let a position sit OPEN without a stop`` the moment it went live — we
would be measuring a mechanism we could not ship. So the arm models a stop
**parked at the SAR level and amended each bar**, and records both prices:

``fill_level``   — the parked stop is touched intrabar (gap-through fills at the
                   bar's open: worse, never better).
``fill_confirm`` — the flip is confirmed at the bar's close and exited at market.

``confirm_slippage_pct`` is the difference. That number is the cost of waiting
for confirmation, it has never been measured here, and it is exactly what an
adoption decision needs. Neither fill is "the" answer; the panel shows both.

What this module refuses to do
------------------------------
* **No index arithmetic from wall-clock time.** #800 died inferring an entry bar
  from elapsed seconds and clamping when the array disagreed. Here the arm opens
  on "the newest closed bar the store holds right now", records that bar's
  ``open_time``, and advances only when a *different* bar becomes newest. There
  is nothing to clamp.
* **No transition on an unclosed bar.** ``update_candle`` appends on ``k["x"]``
  only, so the newest bar is the last completed one; the stop for the bar now
  trading is a projection past the end of the array
  (``sar_exit_shadow.parabolic_sar_live``). Marks update every tick, state
  transitions only on a new closed bar.
* **No guessing when data is short.** Fewer than the warm-up bars, or a
  mismatched high/low pair, marks the arm ``INSUFFICIENT`` and it measures
  nothing. A clamp here would publish confident rows describing a bar we never
  saw.
* **No silent excepts.** Every fail-open path calls ``fail_open.record``.
"""
from __future__ import annotations

import json
import os
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from src import fail_open
from src.sar_exit_shadow import SarLive, parabolic_sar_live
from src.utils import get_logger

log = get_logger(__name__)

# --------------------------------------------------------------------------- #
# Vocabulary
# --------------------------------------------------------------------------- #

#: Which leg is running the trade right now.
GOV_SAR = "SAR"
GOV_GEOMETRY = "GEOMETRY"

STATUS_RUNNING = "RUNNING"
STATUS_CLOSED_SAR_FLIP = "CLOSED_SAR_FLIP"
STATUS_CLOSED_SL = "CLOSED_SL"
STATUS_CLOSED_TP1 = "CLOSED_TP1"
STATUS_INSUFFICIENT = "INSUFFICIENT"

CLOSED_STATUSES = frozenset(
    {STATUS_CLOSED_SAR_FLIP, STATUS_CLOSED_SL, STATUS_CLOSED_TP1}
)

EXIT_SAR_FLIP = "sar_flip"
EXIT_STATIC_SL = "static_sl"
EXIT_STATIC_TP1 = "static_tp1"

#: Bumped whenever a stored row's meaning changes. Readers gate on the schema,
#: never on a date — a migration keyed to a timestamp that predicts a future
#: deploy is how #802's first fix shipped 88 bad rows as good ones.
LEDGER_SCHEMA = 1


# --------------------------------------------------------------------------- #
# Per-(symbol, timeframe, bar) SAR cache
# --------------------------------------------------------------------------- #
#
# Cost discipline: this runs inside TradeMonitor's 5s poll, over every open
# signal, twice (5m + 15m). The SAR walk is pure CPU over in-memory arrays — no
# network, no Firestore — but recomputing 500 bars per signal per tick is still
# waste, and many open signals share a symbol.
#
# The cache is keyed on the last closed bar's open_time, which *is* the
# invalidation signal: a new bar changes the key, anything else cannot change
# the answer. That is the pattern the pre-TP dispatcher established after the
# ₹4,552/month Firestore surprise — gate on an explicit generation, not a TTL.

_sar_cache: Dict[Tuple[str, str, float], Optional[SarLive]] = {}
_sar_cache_lock = threading.Lock()
_SAR_CACHE_CAP = 4096


def _cached_sar_live(
    symbol: str,
    timeframe: str,
    highs: List[float],
    lows: List[float],
    last_closed_ms: float,
    step: float,
    max_step: float,
) -> Optional[SarLive]:
    """SAR live state for one symbol/timeframe, computed once per closed bar."""
    key = (symbol, timeframe, float(last_closed_ms))
    with _sar_cache_lock:
        if key in _sar_cache:
            return _sar_cache[key]
    value = parabolic_sar_live(
        highs, lows, step, max_step, last_closed_ms=last_closed_ms
    )
    with _sar_cache_lock:
        if len(_sar_cache) >= _SAR_CACHE_CAP:
            # Bounded, and bar keys are monotonic — dropping the oldest keys is
            # correct, not merely convenient.
            for stale in sorted(_sar_cache, key=lambda k: k[2])[: _SAR_CACHE_CAP // 4]:
                _sar_cache.pop(stale, None)
        _sar_cache[key] = value
    return value


def reset_sar_cache() -> None:
    """Test hook — the cache is module-global and process-lifetime."""
    with _sar_cache_lock:
        _sar_cache.clear()


# --------------------------------------------------------------------------- #
# Candle access
# --------------------------------------------------------------------------- #


def _series(
    store: Any, symbol: str, timeframe: str, warmup: int
) -> Optional[Dict[str, List[float]]]:
    """Closed-bar OHLC + open_time for one symbol/timeframe, or None.

    Returns None — never a truncated or padded series — when the store cannot
    support the walk. ``open_time`` must be finite over the whole window: a
    bucket seeded before timestamp tracking fills that slot with NaN, and a
    mechanism that decides *when* something happened cannot run on bars that
    cannot say when they are.
    """
    try:
        candles = store.get_candles(symbol, timeframe)
        if candles is None:
            return None
        highs = candles.get("high")
        lows = candles.get("low")
        opens = candles.get("open")
        closes = candles.get("close")
        times = candles.get("open_time")
        for arr in (highs, lows, opens, closes, times):
            if arr is None:
                return None
        n = len(highs)
        if n < warmup or len(lows) != n or len(opens) != n or len(closes) != n:
            return None
        if len(times) != n:
            return None
        out = {
            "high": [float(x) for x in highs],
            "low": [float(x) for x in lows],
            "open": [float(x) for x in opens],
            "close": [float(x) for x in closes],
            "open_time": [float(x) for x in times],
        }
        last_t = out["open_time"][-1]
        if not (last_t == last_t) or last_t <= 0:  # NaN-safe finiteness check
            return None
        return out
    except Exception as exc:
        fail_open.record("sar_live_shadow._series", exc)
        return None


# --------------------------------------------------------------------------- #
# The arm
# --------------------------------------------------------------------------- #


def _is_long(side: str) -> bool:
    return str(side or "").upper() == "LONG"


def _aligned(sar_up: bool, side: str) -> bool:
    """Does SAR sit on the trade's side? One definition, used everywhere."""
    return bool(sar_up) if _is_long(side) else (not bool(sar_up))


def _pnl_pct(entry: float, exit_price: float, side: str) -> float:
    if entry <= 0:
        return 0.0
    raw = (exit_price - entry) / entry * 100.0
    return raw if _is_long(side) else -raw


def new_arm(
    *,
    signal_id: str,
    symbol: str,
    side: str,
    setup_class: str,
    timeframe: str,
    entry: float,
    stop_loss: float,
    tp1: float,
    sar: Optional[SarLive],
    opened_ms: Optional[float],
    now_ts: Optional[float] = None,
) -> Dict[str, Any]:
    """Open one arm, deciding its governor from SAR at generation.

    Alignment at entry is recorded **here**, where it becomes true, not in a
    later pass. #802 put exactly this fact in a 48h resolve path and 261 of 277
    rows carried no verdict as a result; the value needs no future candle, so
    there is no defensible reason for it to arrive late.
    """
    now = time.time() if now_ts is None else float(now_ts)
    sl_distance_pct = (
        abs(entry - stop_loss) / entry * 100.0 if entry > 0 and stop_loss > 0 else 0.0
    )
    arm: Dict[str, Any] = {
        "schema": LEDGER_SCHEMA,
        "arm_id": f"{signal_id}:{timeframe}",
        "signal_id": signal_id,
        "symbol": symbol,
        "side": str(side or "").upper(),
        "setup_class": setup_class,
        "timeframe": timeframe,
        "entry": float(entry),
        "stop_loss": float(stop_loss),
        "tp1": float(tp1),
        "sl_distance_pct": sl_distance_pct,
        "opened_at": now,
        "opened_bar_ms": opened_ms,
        "last_bar_ms": opened_ms,
        "bars_seen": 0,
        "status": STATUS_RUNNING,
        "exit_reason": None,
        "closed_at": None,
        "fill_level": None,
        "fill_confirm": None,
        "pnl_level_pct": None,
        "pnl_confirm_pct": None,
        "r_level": None,
        "r_confirm": None,
        "confirm_slippage_pct": None,
        "mfe_pct": 0.0,
        "current_price": None,
        "unrealized_pct": None,
        "ambiguous_bar": False,
        "handover_at": None,
        "handover_bar_ms": None,
    }
    if sar is None:
        # Refuse. An arm that cannot read SAR at entry does not get a governor
        # invented for it — it measures nothing and says so.
        arm["status"] = STATUS_INSUFFICIENT
        arm["exit_reason"] = "no_sar_at_entry"
        arm["aligned_at_entry"] = None
        arm["governor"] = None
        arm["sar_stop"] = None
        arm["sar_up"] = None
        arm["closed_at"] = now
        return arm
    aligned = _aligned(sar.up, side)
    arm["aligned_at_entry"] = aligned
    arm["governor"] = GOV_SAR if aligned else GOV_GEOMETRY
    arm["sar_stop"] = sar.next_stop
    arm["sar_up"] = bool(sar.up)
    if aligned:
        # The handover is immediate, so it is stamped at entry rather than left
        # blank — "SAR governed from bar one" is a fact about this arm.
        arm["handover_at"] = now
        arm["handover_bar_ms"] = opened_ms
    return arm


def _close(
    arm: Dict[str, Any],
    *,
    reason: str,
    status: str,
    fill_level: float,
    fill_confirm: float,
    now_ts: float,
) -> None:
    """Terminal transition. Writes both fills and both R values."""
    entry = float(arm["entry"])
    side = arm["side"]
    arm["status"] = status
    arm["exit_reason"] = reason
    arm["closed_at"] = now_ts
    arm["fill_level"] = float(fill_level)
    arm["fill_confirm"] = float(fill_confirm)
    arm["pnl_level_pct"] = _pnl_pct(entry, fill_level, side)
    arm["pnl_confirm_pct"] = _pnl_pct(entry, fill_confirm, side)
    arm["confirm_slippage_pct"] = arm["pnl_confirm_pct"] - arm["pnl_level_pct"]
    sl_d = float(arm.get("sl_distance_pct") or 0.0)
    if sl_d > 0:
        # R divides by the SL distance **at entry**, even when SAR governed and
        # that stop was never used. It keeps a number here comparable with the
        # edge matrix and /track-record, which divide by the same thing. A
        # moving-stop denominator would be honest only about itself.
        arm["r_level"] = arm["pnl_level_pct"] / sl_d
        arm["r_confirm"] = arm["pnl_confirm_pct"] / sl_d
    arm["current_price"] = None
    arm["unrealized_pct"] = None


def mark_arm(arm: Dict[str, Any], price: Optional[float]) -> None:
    """Mark a running arm to the live price. Never touches a realized column.

    The realized fields stay blank until an exit actually happens — an
    unrealized number sitting in a realized column is how a still-open trade
    gets read as a finished one.
    """
    try:
        if arm.get("status") != STATUS_RUNNING or price is None:
            return
        p = float(price)
        if p <= 0:
            return
        arm["current_price"] = p
        arm["unrealized_pct"] = _pnl_pct(float(arm["entry"]), p, arm["side"])
    except Exception as exc:
        fail_open.record("sar_live_shadow.mark_arm", exc)


def step_arm(
    arm: Dict[str, Any],
    series: Dict[str, List[float]],
    *,
    step: float,
    max_step: float,
    now_ts: Optional[float] = None,
) -> bool:
    """Advance one arm over every bar that has closed since it was last stepped.

    Returns True when the arm changed state (opened a handover, or closed), so
    the caller knows whether the ledger is worth persisting.

    Transitions happen **on closed bars only**. Between bar closes the arm's
    stop is already parked and nothing can change it — which is precisely why
    this is separable from ``mark_arm``.
    """
    now = time.time() if now_ts is None else float(now_ts)
    try:
        if arm.get("status") != STATUS_RUNNING:
            return False
        times = series["open_time"]
        last_seen = arm.get("last_bar_ms")
        if last_seen is None:
            return False
        # Locate the arm's position by the bar's own timestamp. Never by
        # elapsed-time arithmetic — that assumption (gap-free, current data) is
        # what published 172 rows describing an unrelated bar in #800.
        try:
            idx = times.index(float(last_seen))
        except ValueError:
            # The bar we last processed has rolled out of the store's window.
            # We cannot know what happened in between, and inventing a starting
            # index would be a clamp. The arm stops measuring and says why.
            arm["status"] = STATUS_INSUFFICIENT
            arm["exit_reason"] = "bar_rolled_out_of_window"
            arm["closed_at"] = now
            return True
        n = len(times)
        changed = False
        highs, lows, opens, closes = (
            series["high"],
            series["low"],
            series["open"],
            series["close"],
        )
        entry = float(arm["entry"])
        side = arm["side"]
        is_long = _is_long(side)
        for i in range(idx + 1, n):
            hi, lo, op, cl = highs[i], lows[i], opens[i], closes[i]
            arm["last_bar_ms"] = times[i]
            arm["bars_seen"] = int(arm.get("bars_seen") or 0) + 1
            # Every consumed bar is a change worth persisting. Without this the
            # file would only move on a handover or a close, and ops could not
            # tell a frozen arm from a live one — which is the exact failure
            # this whole module exists to stop being invisible.
            changed = True
            # MFE over closed bars, measured before any exit on this bar so the
            # exit bar cannot inflate it.
            fav = (hi - entry) if is_long else (entry - lo)
            if entry > 0:
                arm["mfe_pct"] = max(
                    float(arm.get("mfe_pct") or 0.0), fav / entry * 100.0
                )

            if arm.get("governor") == GOV_GEOMETRY:
                sl = float(arm["stop_loss"])
                tp1 = float(arm["tp1"])
                sl_hit = (lo <= sl) if is_long else (hi >= sl)
                tp_hit = (hi >= tp1) if is_long else (lo <= tp1)
                if sl_hit and tp_hit:
                    # OHLC cannot order two touches inside one bar. Resolve
                    # pessimistically and flag it, so the row is visibly a
                    # judgement rather than silently averaged as a fact.
                    arm["ambiguous_bar"] = True
                if sl_hit:
                    gapped = (op <= sl) if is_long else (op >= sl)
                    fill = op if gapped else sl
                    _close(
                        arm,
                        reason=EXIT_STATIC_SL,
                        status=STATUS_CLOSED_SL,
                        fill_level=fill,
                        fill_confirm=cl,
                        now_ts=now,
                    )
                    return True
                if tp_hit:
                    # A resting limit fills at its own price; a gap through it
                    # does not fill better.
                    _close(
                        arm,
                        reason=EXIT_STATIC_TP1,
                        status=STATUS_CLOSED_TP1,
                        fill_level=tp1,
                        fill_confirm=cl,
                        now_ts=now,
                    )
                    return True
                # Neither hit — has SAR come onside on this bar?
                live = parabolic_sar_live(
                    highs[: i + 1], lows[: i + 1], step, max_step, last_closed_ms=times[i]
                )
                if live is not None:
                    arm["sar_up"] = bool(live.up)
                    if _aligned(live.up, side):
                        arm["governor"] = GOV_SAR
                        arm["handover_at"] = now
                        arm["handover_bar_ms"] = times[i]
                        arm["sar_stop"] = live.next_stop
                        changed = True
                continue

            # SAR governs: the stop parked at the previous bar's close is what
            # this bar could breach.
            parked = arm.get("sar_stop")
            if parked is None:
                live = parabolic_sar_live(
                    highs[: i + 1], lows[: i + 1], step, max_step, last_closed_ms=times[i]
                )
                if live is not None:
                    arm["sar_stop"] = live.next_stop
                    arm["sar_up"] = bool(live.up)
                continue
            parked = float(parked)
            breached = (lo <= parked) if is_long else (hi >= parked)
            if breached:
                gapped = (op <= parked) if is_long else (op >= parked)
                _close(
                    arm,
                    reason=EXIT_SAR_FLIP,
                    status=STATUS_CLOSED_SAR_FLIP,
                    fill_level=op if gapped else parked,
                    fill_confirm=cl,
                    now_ts=now,
                )
                return True
            live = parabolic_sar_live(
                highs[: i + 1], lows[: i + 1], step, max_step, last_closed_ms=times[i]
            )
            if live is not None:
                arm["sar_stop"] = live.next_stop
                arm["sar_up"] = bool(live.up)
        return changed
    except Exception as exc:
        fail_open.record("sar_live_shadow.step_arm", exc)
        return False


# --------------------------------------------------------------------------- #
# Ledger
# --------------------------------------------------------------------------- #


class SarLiveLedger:
    """Open + resolved arms, persisted so a restart does not lose live state."""

    #: Relative + env-overridable, matching ``sar_exit_shadow._DEFAULT_PATH`` —
    #: ops mounts the engine's ``data/`` read-only at ``/engine-data`` and reads
    #: this file directly, so the two repos must agree on the name. The ``_v1``
    #: suffix is the schema in the filename: a bump gets a new file rather than
    #: reinterpreting rows written under different rules.
    #:
    #: **This filename and the row keys below are a cross-repo contract.**
    #: ``tests/test_sar_live_contract.py`` pins them on this, the producing,
    #: side — #817's ``entry_regime`` was read by ops for months while nothing
    #: wrote it, and the page looked full the whole time.
    DEFAULT_PATH = os.getenv("SAR_LIVE_SHADOW_PATH", "data/sar_live_arms_v1.json")

    def __init__(self, path: Optional[str] = None, max_resolved: int = 2000) -> None:
        self._path = path or self.DEFAULT_PATH
        self._max_resolved = int(max_resolved)
        self._lock = threading.RLock()
        self._open: Dict[str, Dict[str, Any]] = {}
        self._resolved: List[Dict[str, Any]] = []
        self._dirty = False
        self._last_write = 0.0

    # -- accessors ------------------------------------------------------- #

    def open_arms(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(a) for a in self._open.values()]

    def resolved_arms(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(a) for a in self._resolved]

    def get(self, arm_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._open.get(arm_id)

    def has(self, arm_id: str) -> bool:
        with self._lock:
            return arm_id in self._open or any(
                a.get("arm_id") == arm_id for a in self._resolved
            )

    def add(self, arm: Dict[str, Any]) -> None:
        with self._lock:
            if arm.get("status") == STATUS_RUNNING:
                self._open[arm["arm_id"]] = arm
            else:
                self._resolved.append(arm)
                self._trim()
            self._dirty = True

    def retire(self, arm_id: str) -> None:
        """Move a no-longer-running arm out of the open set."""
        with self._lock:
            arm = self._open.pop(arm_id, None)
            if arm is not None:
                self._resolved.append(arm)
                self._trim()
                self._dirty = True

    def _trim(self) -> None:
        if len(self._resolved) > self._max_resolved:
            self._resolved = self._resolved[-self._max_resolved :]

    # -- persistence ----------------------------------------------------- #

    def mark_dirty(self) -> None:
        with self._lock:
            self._dirty = True

    def flush(self, min_interval_sec: float = 15.0, force: bool = False) -> bool:
        """Write to disk when something changed. Throttled — this runs in a 5s loop."""
        try:
            with self._lock:
                if not self._dirty and not force:
                    return False
                now = time.time()
                if not force and (now - self._last_write) < float(min_interval_sec):
                    return False
                payload = {
                    "schema": LEDGER_SCHEMA,
                    "written_at": now,
                    "open": list(self._open.values()),
                    "resolved": self._resolved,
                }
                self._last_write = now
                self._dirty = False
            tmp = f"{self._path}.tmp"
            parent = os.path.dirname(self._path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(tmp, "w") as fh:
                json.dump(payload, fh)
            os.replace(tmp, self._path)
            return True
        except Exception as exc:
            fail_open.record("sar_live_shadow.flush", exc)
            return False

    def load(self) -> None:
        """Restore from disk. A schema mismatch drops the file rather than
        reinterpreting rows written under different rules."""
        try:
            if not os.path.exists(self._path):
                return
            with open(self._path) as fh:
                payload = json.load(fh)
            if int(payload.get("schema") or 0) != LEDGER_SCHEMA:
                log.warning(
                    "SAR live ledger schema {} != {} — starting clean",
                    payload.get("schema"),
                    LEDGER_SCHEMA,
                )
                return
            with self._lock:
                self._open = {
                    a["arm_id"]: a for a in payload.get("open", []) if a.get("arm_id")
                }
                self._resolved = list(payload.get("resolved", []))
                self._trim()
        except Exception as exc:
            fail_open.record("sar_live_shadow.load", exc)


_ledger: Optional[SarLiveLedger] = None
_ledger_lock = threading.Lock()


def get_ledger() -> SarLiveLedger:
    global _ledger
    with _ledger_lock:
        if _ledger is None:
            from config import SAR_LIVE_SHADOW_MAX_RESOLVED

            _ledger = SarLiveLedger(max_resolved=SAR_LIVE_SHADOW_MAX_RESOLVED)
            _ledger.load()
        return _ledger


def reset_ledger(ledger: Optional[SarLiveLedger] = None) -> None:
    """Test hook."""
    global _ledger
    with _ledger_lock:
        _ledger = ledger


# --------------------------------------------------------------------------- #
# Orchestration — called from the monitor loop, once per open signal per tick
# --------------------------------------------------------------------------- #


def _side_of(sig: Any) -> str:
    d = getattr(sig, "direction", "")
    return str(getattr(d, "value", d) or "").upper()


def observe_signal(
    sig: Any,
    store: Any,
    *,
    price: Optional[float] = None,
    timeframes: Optional[List[str]] = None,
    step: Optional[float] = None,
    max_step: Optional[float] = None,
    warmup: Optional[int] = None,
    ledger: Optional[SarLiveLedger] = None,
    now_ts: Optional[float] = None,
) -> None:
    """Open this signal's arms on first sight, then advance them.

    Fail-open throughout: this is a measurement riding the monitor loop, and a
    measurement must never be able to break the loop that carries real exits.
    """
    try:
        from config import (
            SAR_EXIT_SHADOW_MAX_STEP,
            SAR_EXIT_SHADOW_STEP,
            SAR_LIVE_SHADOW_ENABLED,
            SAR_LIVE_SHADOW_TIMEFRAMES,
            SAR_LIVE_SHADOW_WARMUP_BARS,
        )

        if not SAR_LIVE_SHADOW_ENABLED:
            return
        tfs = timeframes if timeframes is not None else SAR_LIVE_SHADOW_TIMEFRAMES
        # One indicator, one set of parameters. The live arm deliberately reads
        # the same step/max-step as the replay arm and the app's chart study —
        # three surfaces drawing different SAR would make them incomparable.
        s = SAR_EXIT_SHADOW_STEP if step is None else step
        ms = SAR_EXIT_SHADOW_MAX_STEP if max_step is None else max_step
        wu = SAR_LIVE_SHADOW_WARMUP_BARS if warmup is None else warmup
        book = ledger if ledger is not None else get_ledger()
        now = time.time() if now_ts is None else float(now_ts)

        signal_id = str(getattr(sig, "signal_id", "") or "")
        symbol = str(getattr(sig, "symbol", "") or "")
        if not signal_id or not symbol:
            return
        side = _side_of(sig)
        if side not in ("LONG", "SHORT"):
            return

        for tf in tfs:
            arm_id = f"{signal_id}:{tf}"
            arm = book.get(arm_id)
            if arm is None:
                if book.has(arm_id):
                    continue  # already resolved — do not re-open it
                series = _series(store, symbol, tf, wu)
                if series is None:
                    record_step(symbol, False, f"no_series:{tf}")
                    continue
                live = _cached_sar_live(
                    symbol,
                    tf,
                    series["high"],
                    series["low"],
                    series["open_time"][-1],
                    s,
                    ms,
                )
                book.add(
                    new_arm(
                        signal_id=signal_id,
                        symbol=symbol,
                        side=side,
                        setup_class=str(getattr(sig, "setup_class", "") or ""),
                        timeframe=tf,
                        entry=float(getattr(sig, "entry", 0.0) or 0.0),
                        stop_loss=float(getattr(sig, "stop_loss", 0.0) or 0.0),
                        tp1=float(getattr(sig, "tp1", 0.0) or 0.0),
                        sar=live,
                        opened_ms=series["open_time"][-1],
                        now_ts=now,
                    )
                )
                record_step(symbol, True)
                continue

            series = _series(store, symbol, tf, wu)
            if series is None:
                record_step(symbol, False, f"no_series:{tf}")
                continue
            record_step(symbol, True)
            changed = step_arm(arm, series, step=s, max_step=ms, now_ts=now)
            mark_arm(arm, price)
            if arm.get("status") != STATUS_RUNNING:
                book.retire(arm_id)
            elif changed:
                book.mark_dirty()
    except Exception as exc:
        fail_open.record("sar_live_shadow.observe_signal", exc)


# --------------------------------------------------------------------------- #
# Health — the population that would be harmed, not the convenient one
# --------------------------------------------------------------------------- #
#
# #815's lesson: ``candle_coverage`` walked the *live universe* and read 100%
# while every record on a rotated-out mover was permanently unresolvable. So
# this counts the arms that are actually owed a verdict, and how many of them
# could not be stepped this cycle — a rotated-out symbol shows up here by
# construction, because the arm is in the population whether or not the symbol
# still is.

_health_cur: Dict[str, Any] = {"stepped": 0, "no_series": 0, "symbols": {}}
_health_last: Dict[str, Any] = {"stepped": 0, "no_series": 0, "symbols": {}}
_health_lock = threading.Lock()


def record_step(symbol: str, ok: bool, reason: str = "") -> None:
    try:
        with _health_lock:
            if ok:
                _health_cur["stepped"] = int(_health_cur["stepped"]) + 1
                _health_cur["symbols"].pop(symbol, None)
                return
            _health_cur["no_series"] = int(_health_cur["no_series"]) + 1
            if len(_health_cur["symbols"]) < 256:
                _health_cur["symbols"][symbol] = reason or "unknown"
    except Exception as exc:
        fail_open.record("sar_live_shadow.record_step", exc)


def roll_health_cycle() -> None:
    global _health_cur, _health_last
    with _health_lock:
        _health_last = _health_cur
        _health_cur = {"stepped": 0, "no_series": 0, "symbols": {}}


def step_health() -> Dict[str, Any]:
    with _health_lock:
        return {
            "stepped": int(_health_last["stepped"]),
            "no_series": int(_health_last["no_series"]),
            "symbols": dict(_health_last["symbols"]),
        }


def reset_health() -> None:
    global _health_cur, _health_last
    with _health_lock:
        _health_cur = {"stepped": 0, "no_series": 0, "symbols": {}}
        _health_last = {"stepped": 0, "no_series": 0, "symbols": {}}
