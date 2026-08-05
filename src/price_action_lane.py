"""The standalone price-action lane — a level, swept and reclaimed, delta-confirmed.

Phase 5 of ``docs/PRICE_ACTION_PROGRAM.md``, and the first thing in this repo
where **structure generates the signal** rather than scoring it or filtering it.

Why this trigger and no other
------------------------------
§2 of the program surveys what the published evidence actually supports, and the
answer is narrow. **Stop clustering at swing levels and round numbers** is among
the most replicated microstructure findings (Osler 2000/2003/2005, Harris 1991,
Bhattacharya 2012); **signed order imbalance moves price** is direct and
measurable. Fair value gaps have *no* peer-reviewed validation of the
three-candle construct, and order blocks are not distinguishable in the
literature from ordinary support/resistance.

So the trigger is built from the supported column only:

    a confirmed level from the LevelBook, SWEPT and RECLAIMED,
    with delta confirmation from the footprint,
    sized and targeted from structure.

Not "an order block exists". Not "an FVG exists". Those would spend a quarter
reproducing a null — and the standing warning is the controlled test of **54
mechanical SMC rule variants over 2.5M bars**: best win rate 56.3%, **zero
profitable after costs**. Our own book already loses ~10x its edge to fees, so a
lane that produces 56% is a losing lane. **This lane is instrumented to return
"no edge" and that is a successful outcome.**

The mechanism
-------------
A *sweep* is a failed break: price trades through a level and closes back on the
side it came from. That is the event stop-clustering predicts — the cluster is
taken, the move fails, and the traders who were stopped are now on the wrong
side. The *reclaim* close is the entry.

* **LONG** — within the sweep window a bar's low went **below** a support level
  by more than the tolerance, and the newest closed bar closed back **above** it.
* **SHORT** — the mirror: a high above a resistance level, and a close back below.

Geometry comes from structure, not from a multiplier. The stop sits beyond the
**sweep extreme** (the wick that took the liquidity — if price returns there the
read was wrong), and TP1 is the **next opposing level**. A candidate with no
opposing level ahead is **refused and named**, never given a fixed R-multiple:
fixed multiples off the stop distance are exactly what §5 found the rest of the
book doing, and inventing one here would make this lane a moving-average path
wearing a structural name.

Delta confirmation is **required**, not a bonus. It is the layer §2 says is
supported and the one Phases 2a/2b built. A sweep with no aggression behind the
reclaim is a wick, and the footprint is what tells them apart. The footprint
covers a bounded symbol set, so most symbols refuse on ``no_footprint`` — that
is honest and the census shows it, rather than the lane silently widening itself
to whatever data happens to exist.

Where it goes
-------------
``dark_emission.publish`` — a real signal, diverted before the queue, walked
forward on the money-path clock for a real outcome. It reaches no channel, no
push, no app feed and no order.

It rides that ledger for its **resolver**, which is correct and was paid for over
six sessions of defects (``INSUFFICIENT`` rows, stalled arms, stale anchors,
over-walked series, undatable windows). Building a seventh resolver to own would
be repeating all of them. The rows stay separable by ``dark_gate``, and the
per-path ring gives the lane its **own row budget** — a dark lane whose budget is
consumed by the two highest-volume paths starves exactly the rare paths it exists
to measure, which has already happened once (the snap ledger filled with 211
re-detections of one RIFUSDT setup).

**These rows are not the same kind of thing as the rest of that ledger**, and the
pages must not pool them. A gate-loosened dark row cleared the full scoring
engine and every gate but one. A row from this lane has been through **none** of
that — no scoring, no MTF policy, no confidence floor, no context gate. It is
therefore stamped ``confidence=0.0`` rather than given an invented number, and
``/signals/dark-live`` filters it out while ``/signals/price-action`` is where it
is read.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Sequence, Tuple

import numpy as np

from src import fail_open
from src.utils import get_logger

log = get_logger("price_action_lane")

#: The lane's own setup class. Distinct from every scanner path so the rows can
#: never be pooled into a per-strategy rollup by accident.
SETUP_CLASS = "PA_SWEEP_RECLAIM"

#: Written into ``dark_gate``. On the gate-loosened rows that field names the
#: gate that was relaxed; here it names the *lane*, because nothing was relaxed —
#: this candidate never entered the scanner's chain at all.
DARK_GATE = "price_action_lane"

#: Bars of the trigger timeframe searched for the sweep. Deliberately tight: a
#: sweep six hours ago and a reclaim now are not one event, and a wide window
#: would let any level that was ever poked qualify.
SWEEP_WINDOW_BARS = 6

#: How far through the level price must trade for it to count as swept, as a
#: fraction of price. Below this it is noise around the level rather than a
#: liquidity take.
SWEEP_TOLERANCE_PCT = 0.05

#: Buffer beyond the sweep extreme for the stop, in ATR. The stop's job is to be
#: beyond the wick that took the liquidity — if price returns there, the read was
#: wrong — so the buffer only has to clear noise, not to size the trade.
SL_BUFFER_ATR = 0.25

#: Minimum reward:risk for the structural target. A candidate whose next
#: opposing level sits nearer than this is refused rather than retargeted — the
#: level is the target, and moving it to satisfy a ratio is how a structural lane
#: quietly becomes an R-multiple lane.
MIN_RR = 1.2

# ── Refusal reasons, each its own state ────────────────────────────────────
REFUSE_NO_LEVELS = "no_levels"
REFUSE_NO_SWEEP = "no_sweep"
REFUSE_NO_FOOTPRINT = "no_footprint"
REFUSE_DELTA_OPPOSED = "delta_opposed"
REFUSE_NO_TARGET = "no_opposing_target"
REFUSE_RR_TOO_LOW = "rr_below_floor"
REFUSE_BAD_GEOMETRY = "bad_geometry"
REFUSE_SHORT_SERIES = "short_series"
REFUSE_COOLDOWN = "cooldown"


@dataclass
class LaneCensus:
    """Counters. Every refusal named, because pooling them into "no data" is how
    a page reports a fault that is not happening."""

    evaluated: int = 0
    emitted: int = 0
    refusals: Dict[str, int] = field(default_factory=dict)

    def refuse(self, reason: str) -> None:
        self.refusals[reason] = self.refusals.get(reason, 0) + 1

    def as_dict(self) -> Dict[str, Any]:
        return {
            "evaluated": self.evaluated,
            "emitted": self.emitted,
            "refusals": dict(self.refusals),
        }


_census = LaneCensus()
#: symbol -> last emission time. A sweep persists for several bars, so without
#: this one move produces a row per scan — the re-detection failure that made
#: SLXUSDT buy 10 rows in 2h10m inside a 0.37% entry spread and inverted the
#: sign of a whole population's verdict. The unit of evidence is the MOVE.
_last_emit: Dict[str, float] = {}
EMIT_COOLDOWN_S = 1800.0


def census() -> Dict[str, Any]:
    return _census.as_dict()


def reset_census() -> None:
    global _census, _last_emit
    _census = LaneCensus()
    _last_emit = {}


@dataclass
class LaneSignal:
    """A signal-shaped object ``dark_emission.publish`` can read.

    Deliberately **not** a `Signal`: this never enters the queue, never reaches
    the router and never becomes a position, so constructing the real thing
    would invite exactly the confusion the lane exists to avoid.
    """

    signal_id: str
    symbol: str
    channel: str
    setup_class: str
    direction: Any
    entry: float
    stop_loss: float
    tp1: float
    tp2: float = 0.0
    tp3: float = 0.0
    dark_gate: str = DARK_GATE
    #: Zero, and honestly so. This candidate has been through no scoring engine,
    #: no MTF policy and no confidence floor. An invented number here would be
    #: fabricated performance data on a surface an adoption decision reads.
    confidence: float = 0.0
    entry_regime: str = ""
    mc_context_key: str = ""
    valid_for_minutes: float = 0.0
    pair_admission: str = ""
    # Lane-specific provenance, carried so the page can split by what actually
    # differs between rows.
    level_price: float = 0.0
    level_type: str = ""
    level_source_tf: str = ""
    level_score: float = 0.0
    sweep_extreme: float = 0.0
    sweep_depth_pct: float = 0.0
    delta_quote: float = 0.0
    rr: float = 0.0


def _f(v: Any) -> Optional[float]:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if x == x and abs(x) != float("inf") else None


def _lvl_attr(lvl: Any, name: str, default: Any = None) -> Any:
    if isinstance(lvl, dict):
        return lvl.get(name, default)
    return getattr(lvl, name, default)


def find_sweep_reclaim(
    levels: Sequence[Any],
    high: Any,
    low: Any,
    close: Any,
    *,
    window: int = SWEEP_WINDOW_BARS,
    tolerance_pct: float = SWEEP_TOLERANCE_PCT,
) -> Tuple[Optional[Any], str, Optional[float]]:
    """``(level, side, sweep_extreme)`` for the nearest swept-and-reclaimed level.

    O(levels), not O(levels x bars): the window's extremes are computed once and
    every level is then a constant-time test. This runs per symbol per scan, so
    a nested loop over 60 levels x 6 bars x 75 symbols every 15s would be a real
    cost for no gain.

    Reads ``price`` / ``type`` off the real ``Level`` by name. A reader that
    guesses across several plausible shapes cannot fail loudly — skipping an
    unreadable level is indistinguishable from having none, which is how
    ``zone_distance_atr`` returned None on 57 of 57 rows for its whole life.
    """
    h = np.asarray(high, dtype=np.float64).ravel()
    lo = np.asarray(low, dtype=np.float64).ravel()
    c = np.asarray(close, dtype=np.float64).ravel()
    n = len(c)
    if n < window + 1 or len(h) != n or len(lo) != n:
        return None, "", None

    w_high = float(np.max(h[-window:]))
    w_low = float(np.min(lo[-window:]))
    last_close = float(c[-1])

    best = None
    best_side = ""
    best_extreme: Optional[float] = None
    best_gap: Optional[float] = None

    for lvl in levels or []:
        price = _f(_lvl_attr(lvl, "price"))
        ltype = str(_lvl_attr(lvl, "type", "") or "")
        if price is None or price <= 0:
            continue
        tol = price * (tolerance_pct / 100.0)

        # Bullish: support taken from above and reclaimed.
        if ltype == "support" and w_low < (price - tol) and last_close > price:
            gap = last_close - price
            if best_gap is None or gap < best_gap:
                best, best_side, best_extreme, best_gap = lvl, "LONG", w_low, gap
        # Bearish: resistance taken from below and reclaimed.
        elif ltype == "resistance" and w_high > (price + tol) and last_close < price:
            gap = price - last_close
            if best_gap is None or gap < best_gap:
                best, best_side, best_extreme, best_gap = lvl, "SHORT", w_high, gap

    return best, best_side, best_extreme


def next_opposing_level(
    levels: Sequence[Any], entry: float, is_long: bool,
) -> Optional[float]:
    """The nearest level ahead of the trade — the structural target.

    Signed toward the trade: resistance above for a long, support below for a
    short. This is the same question `structural_veto` asks, from the other
    side: there it is an obstacle, here it is the target.
    """
    want = "resistance" if is_long else "support"
    best: Optional[float] = None
    for lvl in levels or []:
        price = _f(_lvl_attr(lvl, "price"))
        if price is None or price <= 0:
            continue
        if str(_lvl_attr(lvl, "type", "") or "") != want:
            continue
        gap = (price - entry) if is_long else (entry - price)
        if gap <= 0:
            continue
        if best is None or gap < (abs(best - entry)):
            best = price
    return best


def evaluate(
    *,
    symbol: str,
    levels: Sequence[Any],
    high: Any,
    low: Any,
    close: Any,
    atr: Optional[float],
    footprint_bar: Optional[Dict[str, Any]],
    now_ts: Optional[float] = None,
) -> Tuple[Optional[LaneSignal], str]:
    """``(signal, refusal_reason)`` — exactly one is set.

    Pure: no I/O, mutates nothing but the census.
    """
    now = float(now_ts if now_ts is not None else time.time())
    _census.evaluated += 1

    if not levels:
        _census.refuse(REFUSE_NO_LEVELS)
        return None, REFUSE_NO_LEVELS

    lvl, side, extreme = find_sweep_reclaim(levels, high, low, close)
    if lvl is None or not side or extreme is None:
        _census.refuse(REFUSE_NO_SWEEP)
        return None, REFUSE_NO_SWEEP

    # One move, one row. A sweep persists for several bars, so without this the
    # lane emits once per scan for the same event and the population's verdict
    # becomes an artefact of re-detection rather than of the setup.
    last = _last_emit.get(symbol, 0.0)
    if last and (now - last) < EMIT_COOLDOWN_S:
        _census.refuse(REFUSE_COOLDOWN)
        return None, REFUSE_COOLDOWN

    is_long = side == "LONG"
    entry = _f(np.asarray(close, dtype=np.float64).ravel()[-1])
    level_price = _f(_lvl_attr(lvl, "price"))
    if entry is None or entry <= 0 or level_price is None:
        _census.refuse(REFUSE_BAD_GEOMETRY)
        return None, REFUSE_BAD_GEOMETRY

    # Delta confirmation is REQUIRED. A sweep with no aggression behind the
    # reclaim is a wick, and the footprint is the only thing that tells them
    # apart. Refused by name rather than waived — the footprint covers a bounded
    # symbol set, and a lane that silently drops its own confirmation on symbols
    # that lack it is measuring a different mechanism there.
    if not isinstance(footprint_bar, dict):
        _census.refuse(REFUSE_NO_FOOTPRINT)
        return None, REFUSE_NO_FOOTPRINT
    delta = _f(footprint_bar.get("delta_quote"))
    if delta is None:
        _census.refuse(REFUSE_NO_FOOTPRINT)
        return None, REFUSE_NO_FOOTPRINT
    if (delta <= 0) if is_long else (delta >= 0):
        _census.refuse(REFUSE_DELTA_OPPOSED)
        return None, REFUSE_DELTA_OPPOSED

    # Geometry from structure. The stop sits beyond the sweep extreme — the wick
    # that took the liquidity — because if price returns there the read was
    # wrong. The buffer clears noise; it does not size the trade.
    buf = (atr or 0.0) * SL_BUFFER_ATR
    sl = (extreme - buf) if is_long else (extreme + buf)
    risk = abs(entry - sl)
    if risk <= 0:
        _census.refuse(REFUSE_BAD_GEOMETRY)
        return None, REFUSE_BAD_GEOMETRY

    tp1 = next_opposing_level(levels, entry, is_long)
    if tp1 is None:
        # No structural target. Refused rather than given a fixed R-multiple:
        # that is what the rest of the book does and it is the thing this lane
        # exists to be an alternative to.
        _census.refuse(REFUSE_NO_TARGET)
        return None, REFUSE_NO_TARGET

    reward = abs(tp1 - entry)
    rr = reward / risk
    if rr < MIN_RR:
        _census.refuse(REFUSE_RR_TOO_LOW)
        return None, REFUSE_RR_TOO_LOW

    from src.smc import Direction

    sig = LaneSignal(
        signal_id=f"pa-{uuid.uuid4().hex[:16]}",
        symbol=str(symbol),
        channel=SETUP_CLASS,
        setup_class=SETUP_CLASS,
        direction=Direction.LONG if is_long else Direction.SHORT,
        entry=entry,
        stop_loss=sl,
        tp1=tp1,
        level_price=level_price,
        level_type=str(_lvl_attr(lvl, "type", "") or ""),
        level_source_tf=str(_lvl_attr(lvl, "source_tf", "") or ""),
        level_score=_f(_lvl_attr(lvl, "score")) or 0.0,
        sweep_extreme=float(extreme),
        sweep_depth_pct=abs(level_price - extreme) / level_price * 100.0,
        delta_quote=delta,
        rr=rr,
    )
    return sig, ""


def scan_symbol(
    *,
    symbol: str,
    levels: Sequence[Any],
    candles: Any,
    atr: Optional[float],
    now_ts: Optional[float] = None,
) -> bool:
    """Evaluate one symbol and publish a dark row if it triggers.

    Returns True when a row was published. Fail-open throughout: a measurement
    lane must never break a scan.
    """
    try:
        from config import PRICE_ACTION_LANE_MEASURE
        if not PRICE_ACTION_LANE_MEASURE:
            return False
        if not isinstance(candles, dict):
            _census.refuse(REFUSE_SHORT_SERIES)
            return False
        high, low, close = candles.get("high"), candles.get("low"), candles.get("close")
        if high is None or low is None or close is None:
            _census.refuse(REFUSE_SHORT_SERIES)
            return False

        from src.footprint import get_store as _fp
        fp_bar = _fp().sample(symbol)

        sig, reason = evaluate(
            symbol=symbol, levels=levels, high=high, low=low, close=close,
            atr=atr, footprint_bar=fp_bar, now_ts=now_ts,
        )
        if sig is None:
            return False

        from src import dark_emission
        if dark_emission.publish(sig):
            _census.emitted += 1
            _last_emit[symbol] = float(now_ts if now_ts is not None else time.time())
            log.info(
                "[PA-LANE] {} {} swept {} @ {} reclaimed to {} — SL {} TP1 {} "
                "(RR {:.2f}, delta {:+.0f}) — owner-only, no user, no order",
                sig.symbol, sig.direction.value, sig.level_type, sig.level_price,
                sig.entry, sig.stop_loss, sig.tp1, sig.rr, sig.delta_quote,
            )
            return True
        return False
    except Exception as exc:  # noqa: BLE001
        fail_open.record("price_action_lane.scan_symbol", exc)
        return False


def is_lane_row(row: Dict[str, Any]) -> bool:
    """Does this dark row come from the lane rather than a loosened gate?

    The discriminator every reader must use. A gate-loosened row cleared the
    full scoring engine and every gate but one; a lane row has been through
    none of it, and pooling the two is how 15 rows disappear into 2,418.
    """
    return str(row.get("dark_gate") or "") == DARK_GATE
