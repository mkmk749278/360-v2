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

Why the sweep is keyed on the ledger, not on the live signal list (#835)
-----------------------------------------------------------------------
The first cut stepped an arm only from ``observe_signal``, called once per
**active** signal per monitor tick. Two consequences, both owner-caught on
2026-07-30 within hours of the deploy:

* The moment ``trade_monitor`` closed the signal, the router popped it from
  ``active_signals`` and nothing ever touched the arm again. It sat RUNNING
  forever with the stop it happened to hold at that instant — and the arm's
  whole premise is that it exits on *its own* SAR flip, which is normally
  **later** than the signal's SL. Truncating the population at the live exit
  and then never resolving it is worse than not measuring it.
* Even while the signal was live, stepping needs the store's candles to
  advance. A surge-promoted symbol that rotates back out of the scan universe
  stops receiving klines (the Session 44/45/46 frozen-candle class), so the
  newest closed bar never changes and the step loop is a clean no-op. KORUUSDT
  SHORT: 2h19m open, ``bars_seen: 0``, SAR direction still the one read at
  entry, parked 5m stop blown through by 5.45% of price.

Both failures were invisible for the same reason: ``record_step`` counted a
*present* series as a healthy step, so the liveness probe read "2 arms stepped,
no candle misses" while neither arm had advanced a single bar. A probe keyed on
the arms whose signal is still active cannot see an arm whose signal is gone —
#815's lesson, one file over.

So: ``observe_signal`` **opens** arms (it needs the signal for entry/SL/TP), and
``sweep`` **advances** them, iterating the ledger's own open set. An arm is
stepped for as long as it is owed a verdict, whether or not its signal, or even
its symbol, is still in the engine's live universe.
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

#: Health is per **lane**, not global. Two ledgers are swept — arms on delivered
#: signals and arms on dark-feed rows — and pooling their counters would let a
#: stall in the dark lane page as though the live arms had frozen, or a healthy
#: dark lane dilute a real live failure. Same rule the ledgers themselves follow:
#: a number is only readable if you can say which population it describes.
LANE_LIVE = "live"
LANE_DARK = "dark"


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

#: Why an arm stopped being measurable. These are not exits — nothing filled,
#: and every one of them is excluded from the verdict rather than scored.
EXIT_NO_SAR_AT_ENTRY = "no_sar_at_entry"
EXIT_BAR_ROLLED_OUT = "bar_rolled_out_of_window"
EXIT_FEED_STALLED = "candle_feed_stalled"
EXIT_OPEN_AT_HORIZON = "still_open_at_horizon"

#: A stall is described, never guessed at: "the store has no series for this
#: symbol/timeframe" and "the series exists but its newest closed bar is hours
#: old" are different faults with different fixes.
STALL_NO_SERIES = "no_series"
STALL_BARS_BEHIND = "bars_behind"

#: Why an arm was not opened at all. Refusing to open is not a stall — no arm
#: exists, so nothing is owed a verdict — but it is a *measurement* we declined
#: to take and it is counted where the owner can see it.
OPEN_REFUSED_STALE_ANCHOR = "stale_anchor"

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


def timeframe_seconds(timeframe: str) -> Optional[float]:
    """Bar width in seconds, or None when we do not know the timeframe.

    Ported from ``historical_data._INTERVAL_SECONDS`` rather than re-tabulated:
    a second table of bar widths is a mirror, and the fix for a drifting mirror
    is not a second mirror. None means *refuse* — an unknown bar width cannot
    support a staleness judgement, and guessing 60s would silently declare every
    15m arm stalled.
    """
    try:
        from src.historical_data import _INTERVAL_SECONDS

        width = _INTERVAL_SECONDS.get(str(timeframe or ""))
        return float(width) if width else None
    except Exception as exc:
        fail_open.record("sar_live_shadow.timeframe_seconds", exc)
        return None


def bars_behind(
    latest_bar_ms: Optional[float], timeframe: str, now: float
) -> Optional[float]:
    """How many bar-widths the store's newest CLOSED bar lags *now*.

    Zero means the newest closed bar is the one that should be newest: the bar
    now trading has not finished, so there is genuinely nothing to step. That is
    the healthy quiet case, and it is the one the old code could not tell apart
    from a feed that stopped two hours ago.

    ``update_candle`` appends on ``k["x"]`` only, so a bar opening at ``t``
    becomes the newest closed bar at ``t + width``; the lag is measured from
    there, not from the open.
    """
    if latest_bar_ms is None:
        return None
    width = timeframe_seconds(timeframe)
    if width is None or width <= 0:
        return None
    closed_at = float(latest_bar_ms) / 1000.0 + width
    return max(0.0, (now - closed_at) / width)


def _note_series_state(
    arm: Dict[str, Any],
    *,
    now: float,
    latest_bar_ms: Optional[float],
    stall_reason: str = "",
    stall_bars: float,
    abandon_sec: float,
) -> bool:
    """Record whether this arm can be advanced right now. Returns True if it was
    retired as unmeasurable.

    **This is the fix for the bug that made #832 unreadable.** An arm's stop is
    only as current as the last bar it consumed, and nothing published that
    fact — so a 2h19m-old parked stop rendered identically to one computed a
    minute ago, beside a live price, under the words "right now". The staleness
    lives on the row so ops cannot fail to see it, and it is stamped here where
    it becomes true rather than derived by a reader.

    A stall is not immediately fatal: a rotated-out mover may be re-promoted and
    resume. Past ``abandon_sec`` the gap is unrecoverable, and a fill computed
    across bars we never saw would be #800 again — so the arm refuses.
    """
    arm["series_bar_ms"] = latest_bar_ms
    behind = bars_behind(latest_bar_ms, str(arm.get("timeframe") or ""), now)
    arm["bars_behind"] = behind
    stalled = bool(stall_reason) or (behind is not None and behind > float(stall_bars))
    if not stalled:
        arm["stalled"] = False
        arm["stalled_since"] = None
        arm["stall_reason"] = None
        return False
    arm["stalled"] = True
    arm["stall_reason"] = stall_reason or STALL_BARS_BEHIND
    if arm.get("stalled_since") is None:
        arm["stalled_since"] = now
    if now - float(arm["stalled_since"]) < float(abandon_sec):
        return False
    arm["status"] = STATUS_INSUFFICIENT
    arm["exit_reason"] = EXIT_FEED_STALLED
    arm["closed_at"] = now
    arm["current_price"] = None
    arm["unrealized_pct"] = None
    return True


def _is_long(side: str) -> bool:
    return str(side or "").upper() == "LONG"


def _aligned(sar_up: bool, side: str) -> bool:
    """Does SAR sit on the trade's side? One definition, used everywhere."""
    return bool(sar_up) if _is_long(side) else (not bool(sar_up))


def _risk_pct(entry: float, stop: float, side: str) -> Optional[float]:
    """How much of the entry a stop puts at risk, as a positive percentage.

    Negative would mean the stop sits on the *profitable* side of entry — a
    locked-in gain, not a risk — and that is a real state once SAR trails past
    break-even, so the sign is kept rather than clamped to zero.
    """
    if entry <= 0 or stop <= 0:
        return None
    raw = (stop - entry) if not _is_long(side) else (entry - stop)
    return raw / entry * 100.0


def _apply_stop(arm: Dict[str, Any], stop: Optional[float]) -> None:
    """Park a stop on the arm and keep its risk stamps with it.

    **Why the risk is stamped and not derived later.** When SAR agrees at entry
    it governs and the signal's own SL is never used — so the risk the arm
    actually carries is the SAR stop's distance, which can be *wider* than the
    stop the evaluator sized the trade for. The first two live arms showed both
    directions on one signal: MUUUSDT SHORT, designed SL 3.00%, 5m SAR at 1.60%
    and 15m SAR at **3.77%** (owner-caught 2026-07-30). A stop-out on that 15m
    arm scores −1.26R, and reading it as "SAR did worse" would be reading the
    risk difference rather than the exit quality.

    ``max_sar_risk_pct`` is tracked per bar rather than assumed equal to the
    handover value: SAR's two-bar clamp (``max(sar, highs[i-1], highs[i-2])``)
    can move the level *away* from price, so the stop is not monotonically
    favourable and the widest point is not knowable in advance.

    Stamp only — nothing here changes which stop the arm uses.
    """
    arm["sar_stop"] = stop
    if stop is None:
        arm["sar_risk_pct"] = None
        return
    risk = _risk_pct(float(arm["entry"]), float(stop), arm["side"])
    arm["sar_risk_pct"] = risk
    if risk is None:
        return
    prior = arm.get("max_sar_risk_pct")
    arm["max_sar_risk_pct"] = risk if prior is None else max(float(prior), risk)


def _stamp_handover(arm: Dict[str, Any], *, now: float, bar_ms: Any) -> None:
    """Record the handover, and the risk being taken at the moment it happens.

    The handover is the decision point — it is where the signal's SL stops
    governing — so the comparison against that SL is a fact about *this
    instant*, recorded here rather than reconstructed from a later pass. That
    is #802's lesson: a value derivable at stamp time but computed later does
    not merely arrive late, it silently shrinks every population that reads it.
    """
    arm["handover_at"] = now
    arm["handover_bar_ms"] = bar_ms
    risk = arm.get("sar_risk_pct")
    sl_d = float(arm.get("sl_distance_pct") or 0.0)
    arm["handover_risk_pct"] = risk
    arm["handover_wider_than_sl"] = (
        None if (risk is None or sl_d <= 0) else bool(float(risk) > sl_d)
    )


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
    anchor_bars_behind: Optional[float] = None,
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
        # How stale the bar this arm anchored to was, at the moment it anchored.
        # Zero is the healthy case: the newest closed bar is the one that should
        # be newest. Anything above it means the arm started life behind the
        # clock, and ``first_step_bars`` records what that cost. Stamped here,
        # where it becomes true — a reader cannot recover it later.
        "anchor_bars_behind": anchor_bars_behind,
        # Bars consumed by the arm's FIRST advance. On a live arm this is 1: one
        # bar closes, the arm steps once. Anything larger is history the arm
        # walked through *after* it was created, i.e. a replay wearing a
        # forward-stepped row's clothes. The guard in ``observe_signal`` stops it
        # happening; this stamp is the detector that says so on the row itself.
        "first_step_bars": None,
        # Freshness of the measurement itself, not of the price beside it. An
        # open row is only as live as ``last_advance_at``: the parked stop was
        # computed on the bar consumed then and cannot have moved since.
        "last_swept_at": now,
        "last_advance_at": now,
        "series_bar_ms": opened_ms,
        "bars_behind": 0.0,
        "stalled": False,
        "stalled_since": None,
        "stall_reason": None,
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
        # Risk stamps — what the SAR stop actually puts at risk, beside the
        # SL distance the evaluator sized the trade for. Stamp only.
        "sar_risk_pct": None,
        "max_sar_risk_pct": None,
        "handover_risk_pct": None,
        "handover_wider_than_sl": None,
    }
    if sar is None:
        # Refuse. An arm that cannot read SAR at entry does not get a governor
        # invented for it — it measures nothing and says so.
        arm["status"] = STATUS_INSUFFICIENT
        arm["exit_reason"] = EXIT_NO_SAR_AT_ENTRY
        arm["aligned_at_entry"] = None
        arm["governor"] = None
        arm["sar_stop"] = None
        arm["sar_up"] = None
        arm["closed_at"] = now
        return arm
    aligned = _aligned(sar.up, side)
    arm["aligned_at_entry"] = aligned
    arm["governor"] = GOV_SAR if aligned else GOV_GEOMETRY
    _apply_stop(arm, sar.next_stop)
    arm["sar_up"] = bool(sar.up)
    if aligned:
        # The handover is immediate, so it is stamped at entry rather than left
        # blank — "SAR governed from bar one" is a fact about this arm.
        _stamp_handover(arm, now=now, bar_ms=opened_ms)
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
            arm["exit_reason"] = EXIT_BAR_ROLLED_OUT
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
        if arm.get("first_step_bars") is None and n > idx + 1:
            arm["first_step_bars"] = n - idx - 1
        for i in range(idx + 1, n):
            hi, lo, op, cl = highs[i], lows[i], opens[i], closes[i]
            arm["last_bar_ms"] = times[i]
            arm["bars_seen"] = int(arm.get("bars_seen") or 0) + 1
            # When the arm last actually moved. ``last_swept_at`` says we looked;
            # this says we advanced. Ops leads its rows with the difference.
            arm["last_advance_at"] = now
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
                        _apply_stop(arm, live.next_stop)
                        _stamp_handover(arm, now=now, bar_ms=times[i])
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
                    _apply_stop(arm, live.next_stop)
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
                _apply_stop(arm, live.next_stop)
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
    #: ``tests/test_sar_live_shadow.py::OPS_CONTRACT_KEYS`` pins them on this,
    #: the producing, side — #817's ``entry_regime`` was read by ops for months
    #: while nothing wrote it, and the page looked full the whole time.
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

    def flush(
        self,
        min_interval_sec: float = 15.0,
        force: bool = False,
        heartbeat_sec: float = 60.0,
    ) -> bool:
        """Persist the ledger. Throttled on change, and written on a heartbeat.

        **The heartbeat is not an optimisation — it is what makes the file's
        mtime mean something.** The first cut wrote only when an arm changed, so
        with no open signals the file was never created at all, and ops rendered
        UNAVAILABLE: *"the engine is not writing it — check the flag and the
        container"*. That is a fault message, and a healthy engine with a quiet
        market produced it (owner-caught 2026-07-30, minutes after deploy). It is
        this repo's own lesson — **"blank" needs a cause before it gets a
        caption** — reintroduced one file over.

        The three states a reader needs are only separable if a live loop keeps
        touching the file:

        ===================  ==========================================
        File missing         the monitor loop is not running the arms
        File current, empty  running, nothing open — the quiet case
        File stale           the loop stopped stepping
        ===================  ==========================================

        So a write happens when the ledger changed (bounded by
        ``min_interval_sec``) **or** when ``heartbeat_sec`` has elapsed
        regardless. ``_last_write`` starts at 0, so the first tick after boot
        always writes and the file exists within one poll.

        Cost: one small local write per minute when idle. No network, no
        Firestore — this is nowhere near the hot-path budget the cost rules
        guard.
        """
        try:
            with self._lock:
                now = time.time()
                since = now - self._last_write
                due = self._dirty and since >= float(min_interval_sec)
                beat = since >= float(heartbeat_sec)
                if not (force or due or beat):
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


#: Arms opened on **dark-feed** rows, in their own file (owner, 2026-07-31:
#: "observe this dark feed too with SAR exit along with regular").
#:
#: A separate ledger rather than a `lane` column in the live one, and the
#: distinction is not cosmetic: `sar_live_arms_v1.json` is the population
#: `/signals/sar-live` presents as the evidence for adopting SAR on the money
#: path, and every row in it reached a subscriber. A dark row reached nobody.
#: Pooling them would inflate that evidence with signals that were never sent,
#: and it would do so silently — a consumer that has not heard of the dark lane
#: cannot filter for it, whereas a consumer pointed at a file it does not open
#: cannot see it at all. Same reasoning as the ledgers being per-path rather
#: than one ring: a number is readable only when its population is nameable.
DARK_PATH = os.getenv("SAR_LIVE_SHADOW_DARK_PATH", "data/dark_sar_arms_v1.json")

_dark_ledger: Optional[SarLiveLedger] = None


def get_dark_ledger() -> SarLiveLedger:
    global _dark_ledger
    with _ledger_lock:
        if _dark_ledger is None:
            from config import SAR_LIVE_SHADOW_MAX_RESOLVED

            _dark_ledger = SarLiveLedger(
                path=DARK_PATH, max_resolved=SAR_LIVE_SHADOW_MAX_RESOLVED
            )
            _dark_ledger.load()
        return _dark_ledger


def reset_dark_ledger(ledger: Optional[SarLiveLedger] = None) -> None:
    """Test hook."""
    global _dark_ledger
    with _ledger_lock:
        _dark_ledger = ledger


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
#
# Two entry points, deliberately split (#835):
#
#   ``observe_signal(sig, store)``  — OPEN arms. Needs the signal, because entry,
#                                     SL, TP1 and side come from it. Called once
#                                     per active signal per monitor tick.
#   ``sweep(store, price_fn=...)``  — ADVANCE arms. Needs only the ledger and the
#                                     store, so an arm keeps being measured after
#                                     its signal closes and after its symbol
#                                     leaves the scan universe. Called once per
#                                     monitor cycle.
#
# Before the split, advancing was a side-effect of the signal still being active,
# which quietly made "the arm exits when SAR flips" mean "…or when the live SL
# fired, whichever came first, and then it never resolves at all".


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
    stall_bars: Optional[float] = None,
    ledger: Optional[SarLiveLedger] = None,
    lane: str = LANE_LIVE,
    now_ts: Optional[float] = None,
) -> None:
    """Open this signal's arms on first sight. Advancing is ``sweep``'s job.

    This function reads the signal and nothing else reads the signal — entry, SL,
    TP1, side and setup class are only knowable here. Once the arms exist they
    are the ledger's, and the ledger is swept independently, because an arm
    outlives the signal that created it (see the module docstring).

    Fail-open throughout: this is a measurement riding the monitor loop, and a
    measurement must never be able to break the loop that carries real exits.
    """
    try:
        from config import (
            SAR_EXIT_SHADOW_MAX_STEP,
            SAR_EXIT_SHADOW_STEP,
            SAR_LIVE_SHADOW_ENABLED,
            SAR_LIVE_SHADOW_STALL_BARS,
            SAR_LIVE_SHADOW_TIMEFRAMES,
            SAR_LIVE_SHADOW_WARMUP_BARS,
        )

        if not SAR_LIVE_SHADOW_ENABLED:
            return
        tfs = timeframes if timeframes is not None else SAR_LIVE_SHADOW_TIMEFRAMES
        sb = SAR_LIVE_SHADOW_STALL_BARS if stall_bars is None else stall_bars
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
                    # Not counted in arm health: no arm exists yet, so nothing is
                    # owed a verdict. The probe's population is arms, and mixing
                    # "could not open" into it would let a quiet failure to
                    # *advance* hide behind a busy failure to *open*.
                    continue
                # An arm anchors to "the newest closed bar the store holds right
                # now" and steps from there. When that bar is *itself* hours old
                # the anchor is not the entry bar, and the arm's first advance
                # walks the whole gap in one pass — computing SAR levels and
                # fills over bars that closed before the arm existed. That is a
                # replay, published under a page that says it is not one:
                # ACHUSDT 15m consumed 158 bars (39.5h) in 10 bars of life on
                # 2026-07-31, and its SAR-at-entry was read off a 40h-old bar.
                # Presence of data is not currency of data (#835) — and the
                # answer to an anchor we cannot trust is to refuse, not to clamp
                # it forward to now, because "now" is not the entry bar either.
                anchor_behind = bars_behind(series["open_time"][-1], tf, now)
                if anchor_behind is not None and anchor_behind > float(sb):
                    record_open_refusal(
                        symbol, tf, OPEN_REFUSED_STALE_ANCHOR, anchor_behind, lane=lane
                    )
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
                _arm = new_arm(
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
                        anchor_bars_behind=anchor_behind,
                        now_ts=now,
                )
                # Stamped on the row, not only implied by which file it landed
                # in. A row that cannot say which population it belongs to
                # becomes unattributable the moment it is exported, copied into
                # a comparison, or read beside rows from the other lane.
                _arm["lane"] = str(lane)
                book.add(_arm)
                continue
            # The arm already exists — ``sweep`` advances it. Marking it here as
            # well would only duplicate what the sweep does moments later, and
            # counting it here is what made the liveness probe read healthy over
            # frozen arms.
            mark_arm(arm, price)
    except Exception as exc:
        fail_open.record("sar_live_shadow.observe_signal", exc)


def sweep(
    store: Any,
    *,
    price_fn: Optional[Any] = None,
    step: Optional[float] = None,
    max_step: Optional[float] = None,
    warmup: Optional[int] = None,
    stall_bars: Optional[float] = None,
    abandon_sec: Optional[float] = None,
    max_open_hours: Optional[float] = None,
    ledger: Optional[SarLiveLedger] = None,
    lane: str = LANE_LIVE,
    now_ts: Optional[float] = None,
) -> Dict[str, int]:
    """Advance every open arm in the ledger. Returns a per-cycle tally.

    Keyed on **the arms owed a verdict**, which is the population that gets
    harmed when this stops working — not on the live signal list and not on the
    pair universe, both of which drop a symbol precisely when its arm most needs
    watching (#815, #835).

    Every arm lands in exactly one bucket each cycle, and the bucket is recorded:

    ``advanced``   consumed at least one new closed bar (or closed)
    ``current``    up to date; the bar now trading has not finished — the quiet case
    ``stalled``    the series exists but its newest closed bar is bars behind
    ``no_series``  the store cannot supply candles for this symbol/timeframe
    ``retired``    stopped being measurable this cycle and left the open set

    ``current`` and ``stalled`` are the two the old code merged into one silent
    no-op, and the merge is why 2h19m of frozen arms read as healthy.
    """
    tally = {"advanced": 0, "current": 0, "stalled": 0, "no_series": 0, "retired": 0}
    try:
        from config import (
            SAR_EXIT_SHADOW_MAX_STEP,
            SAR_EXIT_SHADOW_STEP,
            SAR_LIVE_SHADOW_ABANDON_SEC,
            SAR_LIVE_SHADOW_ENABLED,
            SAR_LIVE_SHADOW_MAX_OPEN_HOURS,
            SAR_LIVE_SHADOW_STALL_BARS,
            SAR_LIVE_SHADOW_WARMUP_BARS,
        )

        if not SAR_LIVE_SHADOW_ENABLED:
            return tally
        s = SAR_EXIT_SHADOW_STEP if step is None else step
        ms = SAR_EXIT_SHADOW_MAX_STEP if max_step is None else max_step
        wu = SAR_LIVE_SHADOW_WARMUP_BARS if warmup is None else warmup
        sb = SAR_LIVE_SHADOW_STALL_BARS if stall_bars is None else stall_bars
        ab = SAR_LIVE_SHADOW_ABANDON_SEC if abandon_sec is None else abandon_sec
        mo = (
            SAR_LIVE_SHADOW_MAX_OPEN_HOURS
            if max_open_hours is None
            else max_open_hours
        )
        book = ledger if ledger is not None else get_ledger()
        now = time.time() if now_ts is None else float(now_ts)

        for snapshot in book.open_arms():
            arm_id = str(snapshot.get("arm_id") or "")
            arm = book.get(arm_id)
            if arm is None:
                continue
            symbol = str(arm.get("symbol") or "")
            tf = str(arm.get("timeframe") or "")
            arm["last_swept_at"] = now
            changed = False

            # A healthy arm that simply never flips. The mechanism specifies no
            # time stop and the owner disabled signal expiry, so rather than
            # invent a market close, the arm refuses and is excluded from the
            # verdict — visibly, with its own reason.
            opened_at = float(arm.get("opened_at") or now)
            if mo > 0 and (now - opened_at) > float(mo) * 3600.0:
                arm["status"] = STATUS_INSUFFICIENT
                arm["exit_reason"] = EXIT_OPEN_AT_HORIZON
                arm["closed_at"] = now
                arm["current_price"] = None
                arm["unrealized_pct"] = None
                book.retire(arm_id)
                tally["retired"] += 1
                # Deliberately NOT a health miss. The arm reached a bound we
                # chose; nothing failed, and paging on it would fill the probe
                # with non-failures until a real one stopped standing out.
                log.info(
                    "SAR live arm {} retired at the {}h horizon without a flip",
                    arm_id, mo,
                )
                continue

            series = _series(store, symbol, tf, wu)
            if series is None:
                tally["no_series"] += 1
                record_step(symbol, False, f"{STALL_NO_SERIES}:{tf}", lane=lane)
                if _note_series_state(
                    arm,
                    now=now,
                    latest_bar_ms=None,
                    stall_reason=STALL_NO_SERIES,
                    stall_bars=sb,
                    abandon_sec=ab,
                ):
                    book.retire(arm_id)
                    tally["retired"] += 1
                else:
                    book.mark_dirty()
                continue

            before = int(arm.get("bars_seen") or 0)
            changed = step_arm(arm, series, step=s, max_step=ms, now_ts=now)
            advanced = int(arm.get("bars_seen") or 0) > before

            # Only a still-running arm has a "how current am I" question; a
            # closed one already carries its verdict.
            if arm.get("status") == STATUS_RUNNING:
                _note_series_state(
                    arm,
                    now=now,
                    latest_bar_ms=series["open_time"][-1],
                    stall_bars=sb,
                    abandon_sec=ab,
                )

            if advanced:
                tally["advanced"] += 1
                record_step(symbol, True, lane=lane)
            elif arm.get("stalled"):
                tally["stalled"] += 1
                record_step(symbol, False, f"{STALL_BARS_BEHIND}:{tf}", lane=lane)
            else:
                tally["current"] += 1
                record_step(symbol, True, lane=lane)

            if arm.get("status") == STATUS_RUNNING:
                mark_arm(arm, _price_of(price_fn, symbol))
                book.mark_dirty()
            else:
                # Closed by ``step_arm`` (a real exit) or retired by
                # ``_note_series_state`` (unmeasurable). Either way it leaves the
                # open set, and ``retire`` marks the ledger dirty itself.
                book.retire(arm_id)
                tally["retired"] += 1
                continue
            if changed:
                book.mark_dirty()
        return tally
    except Exception as exc:
        fail_open.record("sar_live_shadow.sweep", exc)
        return tally


def _price_of(price_fn: Optional[Any], symbol: str) -> Optional[float]:
    """Mark price for a symbol, or None. Never raises into the sweep.

    The caller supplies this because the engine's price chain (1m close, falling
    back to the all-symbols mark feed) already handles the rotated-out symbol
    case that a frozen candle store does not — and an arm on a rotated-out symbol
    is exactly the arm that needs a real mark beside its stalled stop.
    """
    if price_fn is None:
        return None
    try:
        return price_fn(symbol)
    except Exception as exc:
        fail_open.record("sar_live_shadow.price_fn", exc)
        return None


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
#
# #835: the first cut got the population right and the *predicate* wrong. It
# recorded a step as OK whenever a series came back, so an arm whose candles had
# not moved for 2h19m counted as healthy and the probe reported "2 arms stepped,
# no candle misses" over two frozen arms. Presence of data is not currency of
# data, and the two are only distinguishable by comparing the newest closed bar
# against the clock — which is what ``bars_behind`` now does. A stalled arm is a
# miss, and it is named separately from a missing series because they have
# different fixes.


def _blank_health() -> Dict[str, Any]:
    return {
        "stepped": 0,
        "no_series": 0,
        "stalled": 0,
        "refused_open": 0,
        "symbols": {},
        "refused": {},
    }


_health_cur: Dict[str, Dict[str, Any]] = {LANE_LIVE: _blank_health(), LANE_DARK: _blank_health()}
_health_last: Dict[str, Dict[str, Any]] = {LANE_LIVE: _blank_health(), LANE_DARK: _blank_health()}
_health_lock = threading.Lock()


def _cur(lane: str) -> Dict[str, Any]:
    return _health_cur.setdefault(str(lane or LANE_LIVE), _blank_health())


def record_step(symbol: str, ok: bool, reason: str = "", lane: str = LANE_LIVE) -> None:
    """Bucket one arm's cycle. ``reason`` is ``"<why>:<timeframe>"`` on a miss."""
    try:
        with _health_lock:
            cur = _cur(lane)
            if ok:
                cur["stepped"] = int(cur["stepped"]) + 1
                cur["symbols"].pop(symbol, None)
                return
            key = (
                "stalled"
                if str(reason or "").startswith(STALL_BARS_BEHIND)
                else "no_series"
            )
            cur[key] = int(cur[key]) + 1
            if len(cur["symbols"]) < 256:
                cur["symbols"][symbol] = reason or "unknown"
    except Exception as exc:
        fail_open.record("sar_live_shadow.record_step", exc)


def record_open_refusal(
    symbol: str,
    timeframe: str,
    reason: str,
    bars_behind_now: Optional[float] = None,
    lane: str = LANE_LIVE,
) -> None:
    """Count an arm we declined to open, and say why.

    Kept apart from ``stepped``/``stalled``: those describe arms owed a verdict,
    and this describes a measurement never started. Pooling them would let a
    burst of refusals read as healthy stepping — the exact merge that made 2h19m
    of frozen arms look fine in #835. A refusal is not a fault in the engine and
    does not page; it is a fact about the candle store, and it belongs on screen
    beside the arms it explains the absence of.
    """
    try:
        with _health_lock:
            cur = _cur(lane)
            cur["refused_open"] = int(cur["refused_open"]) + 1
            if len(cur["refused"]) < 256:
                behind = (
                    f" behind={bars_behind_now:.1f}b"
                    if bars_behind_now is not None
                    else ""
                )
                cur["refused"][f"{symbol}:{timeframe}"] = f"{reason}{behind}"
    except Exception as exc:
        fail_open.record("sar_live_shadow.record_open_refusal", exc)


def roll_health_cycle(lane: Optional[str] = None) -> None:
    """Close the current window. ``lane=None`` rolls every lane.

    A lane is rolled by whoever sweeps it: the monitor loop rolls ``live`` on
    its cycle, the dark resolver rolls ``dark`` on its own — which are different
    periods, and pooling them under one roll would report a window neither lane
    actually ran.
    """
    global _health_cur, _health_last
    with _health_lock:
        lanes = list(_health_cur) if lane is None else [str(lane)]
        for ln in lanes:
            _health_last[ln] = _cur(ln)
            _health_cur[ln] = _blank_health()


def step_health(lane: str = LANE_LIVE) -> Dict[str, Any]:
    with _health_lock:
        last = _health_last.setdefault(str(lane or LANE_LIVE), _blank_health())
        return {
            "lane": str(lane or LANE_LIVE),
            "stepped": int(last["stepped"]),
            "no_series": int(last["no_series"]),
            "stalled": int(last["stalled"]),
            "refused_open": int(last["refused_open"]),
            "symbols": dict(last["symbols"]),
            "refused": dict(last["refused"]),
        }


def reset_health() -> None:
    global _health_cur, _health_last
    with _health_lock:
        _health_cur = {LANE_LIVE: _blank_health(), LANE_DARK: _blank_health()}
        _health_last = {LANE_LIVE: _blank_health(), LANE_DARK: _blank_health()}
