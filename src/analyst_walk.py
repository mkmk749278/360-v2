"""Dark forward walk of accepted analyst setups — spec step 4 (2026-11-20).

Every setup the validator ACCEPTED (``src/analyst_plan.py``) is walked forward
on the engine's own dated 5m bars, under several arms over the same
opportunity. Nothing here reaches a subscriber, the signal queue or an order;
it reads the candle store and the analyst ledger and writes a ``walks`` table
beside them.

Arms built here (one row per setup per arm):

* ``analyst`` — full size, a limit at the FIRST entry level, filled if price
  trades through it before the setup expires.
* ``tranche`` — the plan's own tranches (one or two levels, their weights);
  the weighted average of what filled. Identical to ``analyst`` for one level.
* ``market``  — full size at the open of the first bar after submit.
* ``fixed_rule`` — the analyst's symbol and side, but levels picked mechanically
  from the menu stamped at submit (:func:`fixed_rule_levels`). No setup the
  rule can build scores 0.00% as ``no_rule_setup``.
* ``none``    — no trade, 0.00%, so "the model said stand aside" has a number.

Not built yet, and named so nobody reads its absence as zero: the
**existing signals** comparison.

Scoring rules, each one a rule this repo has already paid for:

* **Unfilled is scored, not dropped.** A limit the market never reached is
  scored at the ``market`` outcome and flagged ``unfilled`` (spec §3 step 4,
  limit-order adverse selection). Dropping it would keep only the setups the
  market came back to.
* **Stop first on an ambiguous bar.** A bar touching both stop and target
  books the stop: 5m OHLC carries no ordering, and the flattering guess is the
  one this lane must never make. The fill bar counts for the stop too.
* **Exit at the first target or the stop, else close after
  ``HOLD_HORIZON_S``.** The target is the analyst's own first level.
* **Net of the round trip** (0.07%, the figure ``/track-record`` uses), with
  gross beside it.
* **Refuse, don't clamp.** Bars that do not reach back to the submit (history
  rolled off, undated bucket) make the row ``insufficient`` with its reason,
  never a walk over the bars that remain.
* **A market entry already past its own target or stop is no trade.** When the
  limit sits away from price, the market at submit can already be beyond the
  first target (a short retest whose TP1 is the low price is sitting on) or
  beyond the stop. Walking it books a "target" at a loss, or a "stop" at a
  gain, on the first bar. Such a row scores 0.00% as ``no_valid_trade`` with
  ``entry_past_target`` / ``entry_past_stop``, and is counted per arm. Before
  2026-11-25 these rows were booked as walked; :func:`repair_geometry`
  corrects stored rows from their own fields (no bars needed).

Measurement integrity, walk version 2 (2026-11-27):

* **The headline is what a posted order earned.** An unfilled limit earns
  0.00%, and a filled one earns its net times ``filled_frac``. Before this, a
  limit's headline scored unfilled rows at the MARKET outcome. That population
  is selected: a limit goes unfilled because price ran away from it, so its
  market outcome is conditionally good (+1.42% over 86 rows on 2026-11-27,
  against +0.098% for the unconditional market arm). Pooled, it put the
  analyst arm at +0.42% while its filled setups lost -0.20%. The market-scored
  figure is still published, as ``with_unfilled_at_market``, and the unfilled
  rows on their own as ``missed_market``, a counterfactual.
* **Tranche legs are walked from their own fill bars.** A leg whose fill comes
  after the position has already exited is cancelled. Before v2, every leg
  that filled at any time before expiry was blended into one entry walked from
  the FIRST fill. A second leg reached on a reversal hours after the target
  had been hit was booked as if it had been held from the start. Stored v1
  tranche rows with both legs filled are re-walked while their bars exist, and
  marked ``insufficient`` / ``blend_defect_history_rolled_off`` when the bars
  have rolled off. They are never left in an average.
* **Costs by order type, beside the flat 0.07%.** A limit fill pays maker
  (0.02%). A market entry pays taker (0.05%). A target exit is a resting limit
  (maker), while a stop or a time exit is a taker exit. Funding is charged
  from the derivatives recorder's hourly rates at the symbol's OWN settlement
  times (``next_funding_ms``), never a fixed 00/08/16 grid. A hold the recorder
  does not cover reads unknown, never 0.00%. Slippage is not modelled.
* **What-ifs that only remove fills, so they are exact under the walk's own
  rules:** a shorter expiry (a fill later than 2h or 4h would not have
  happened), and cancelling a limit once price touched TP1 before the fill
  (``tp1_before_fill``).
* **``ladder`` arm:** half at TP1, half held to TP2 (the analyst's own second
  target), with the original stop and no break-even move. With no TP2, the
  runner is held to the stop or the time exit.
* **Day-clustered:** per arm, the realized result summed per UTC submit day.
  Alts move with BTC, so twenty same-day setups are close to one bet.

Measurement flag: ``ANALYST_WALK_ENABLED`` (default ON — no vendor, no
Firestore; local candles and local SQLite files only).
"""
from __future__ import annotations

import json
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.utils import get_logger

log = get_logger("analyst_walk")

TF = "5m"
STEP_S = 300.0
HOLD_HORIZON_S = 12 * 3600.0
ROUND_TRIP_PCT = 0.07
#: Binance USD-M base tier. The flat ROUND_TRIP_PCT is maker in + taker out.
FEE_MAKER_PCT = 0.02
FEE_TAKER_PCT = 0.05
#: Bumped when the walk's rules change. v2: tranche legs walked per fill,
#: per-row fees by order type, tp1_before_fill, the ladder arm.
WALK_VERSION = 2
#: Share closed at TP1 on the ladder arm; the rest rides to TP2.
LADDER_SPLIT = 0.5
#: Expiry caps the what-if tests (hours). A fill later than the cap is dropped.
WHATIF_EXPIRY_H = (2, 4)
ARMS = ("analyst", "tranche", "ladder", "market", "fixed_rule", "none")
#: Arms that post a limit, so an unfilled row earns 0.00% when realized.
LIMIT_ARMS = ("analyst", "tranche", "ladder", "fixed_rule")
#: Exit reasons that mean no trade was taken: zero fees, zero funding.
NO_TRADE_EXITS = ("no_trade", "no_valid_trade", "no_rule_setup")
#: Arms named by the spec and deliberately not built in this module yet.
#: ``existing_signals`` is built (2026-11-27) as a WINDOW comparison, not a
#: per-setup arm: see :func:`existing_signals`.
ARMS_NOT_BUILT: Tuple[str, ...] = ()

# The fixed rule (spec §1: "if a fixed rule on the same level menu matches the
# analyst net of fees, the model added nothing"). Fixed before any data, and
# deliberately NOT tuned on outcomes. It takes the analyst's own symbol and
# side, so it isolates LEVEL CHOICE, and picks from the menu stamped at submit.
RULE_ENTRY_MAX_ATR = 1.5
RULE_STOP_BUFFER_ATR = 0.1
RULE_STOP_ATR = (0.8, 2.5)
RULE_COST_FLOOR_PCT = 3 * ROUND_TRIP_PCT

_SCHEMA = """
CREATE TABLE IF NOT EXISTS walks (
    setup_id     TEXT NOT NULL,
    arm          TEXT NOT NULL,
    status       TEXT NOT NULL,
    reason       TEXT,
    unfilled     INTEGER,
    filled_frac  REAL,
    entry        REAL,
    entry_at     REAL,
    exit         REAL,
    exit_at      REAL,
    exit_reason  TEXT,
    gross_pct    REAL,
    net_pct      REAL,
    mfe_pct      REAL,
    mae_pct      REAL,
    updated_at   REAL NOT NULL,
    PRIMARY KEY (setup_id, arm)
)
"""

#: Additive columns (v2). Rows walked before them read NULL, which every
#: reader treats as "not known", never as zero.
_WALK_COLS = (("walk_v", "INTEGER"), ("tp1_before_fill", "INTEGER"),
              ("fees_pct", "REAL"), ("funding_pct", "REAL"), ("funding_reason", "TEXT"))
_ROW_COLS = ("setup_id", "arm", "status", "reason", "unfilled", "filled_frac", "entry",
             "entry_at", "exit", "exit_at", "exit_reason", "gross_pct", "net_pct",
             "mfe_pct", "mae_pct", "updated_at", "walk_v", "tp1_before_fill", "fees_pct")


# ── pure walk ─────────────────────────────────────────────────────────────


def window(cd: Any, since_s: float) -> Tuple[Optional[Dict[str, np.ndarray]], str]:
    """Dated bars opening at or after ``since_s``, or (None, reason)."""
    if not isinstance(cd, dict):
        return None, "no_candles"
    ot = cd.get("open_time")
    if ot is None or len(ot) == 0:
        return None, "undated"
    ot = np.asarray(ot, dtype=np.float64) / 1000.0
    if not np.all(np.isfinite(ot)) or np.any(np.diff(ot) <= 0):
        return None, "undated"
    if ot[0] > since_s:
        return None, "history_rolled_off"
    i = int(np.searchsorted(ot, since_s, side="left"))
    out = {k: np.asarray(cd[k], dtype=np.float64)[i:] for k in ("open", "high", "low", "close")}
    out["t"] = ot[i:]
    return out, ""


def _exit_walk(bars: Dict[str, np.ndarray], start: int, long: bool, entry: float,
               stop: float, target: Optional[float], now: float, *,
               target_on_fill_bar: bool = True,
               t0: Optional[float] = None) -> Dict[str, Any]:
    """Walk from bar ``start`` (the fill bar) to stop / first target / horizon.

    ``target_on_fill_bar=False`` for a limit fill: the bar that reached the
    limit may have touched the target BEFORE the fill, and OHLC cannot say, so
    on that bar only the stop counts. ``target=None`` holds to the stop or the
    horizon. ``t0`` anchors the horizon (default: the fill bar); a position
    built in legs times out from its FIRST fill.
    """
    t0 = float(bars["t"][start]) if t0 is None else t0
    mfe = mae = 0.0
    for j in range(start, len(bars["t"])):
        hi, lo = float(bars["high"][j]), float(bars["low"][j])
        fav = (hi - entry) if long else (entry - lo)
        adv = (entry - lo) if long else (hi - entry)
        mfe, mae = max(mfe, fav / entry * 100), max(mae, adv / entry * 100)
        hit_stop = lo <= stop if long else hi >= stop
        hit_tgt = target is not None and (hi >= target if long else lo <= target) and (
            target_on_fill_bar or j != start)
        if hit_stop:  # stop first on an ambiguous bar
            return {"status": "resolved", "exit": stop, "exit_at": float(bars["t"][j]),
                    "exit_reason": "stop", "mfe": mfe, "mae": mae, "idx": j}
        if hit_tgt:
            return {"status": "resolved", "exit": target, "exit_at": float(bars["t"][j]),
                    "exit_reason": "target", "mfe": mfe, "mae": mae, "idx": j}
        if float(bars["t"][j]) + STEP_S - t0 >= HOLD_HORIZON_S:
            return {"status": "resolved", "exit": float(bars["close"][j]),
                    "exit_at": float(bars["t"][j]) + STEP_S,
                    "exit_reason": "horizon", "mfe": mfe, "mae": mae, "idx": j}
    return {"status": "open", "mfe": mfe, "mae": mae}


def market_geometry(long: bool, entry: float, stop: float, target: float) -> str:
    """'' if a trade entered at ``entry`` has the target ahead and the stop
    behind; otherwise which side it is already past."""
    sign = 1.0 if long else -1.0
    if sign * (target - entry) <= 0:
        return "entry_past_target"
    if sign * (entry - stop) <= 0:
        return "entry_past_stop"
    return ""


def _no_valid_trade(entry: float, entry_at: float, why: str, **extra: Any) -> Dict[str, Any]:
    out = {"status": "resolved", "gross_pct": 0.0, "net_pct": 0.0,
           "exit_reason": "no_valid_trade", "reason": why, "entry": entry,
           "entry_at": entry_at}
    out.update(extra)
    return out


def _limit_fill(bars, long: bool, level: float, expires_at: float) -> Optional[int]:
    for j in range(len(bars["t"])):
        if float(bars["t"][j]) >= expires_at:
            return None
        if (float(bars["low"][j]) <= level) if long else (float(bars["high"][j]) >= level):
            return j
    return None


def _touched(bars, end: int, long: bool, level: Optional[float]) -> bool:
    """Did any bar BEFORE index ``end`` reach ``level`` (a target)?"""
    if level is None:
        return False
    for j in range(min(end, len(bars["t"]))):
        if (float(bars["high"][j]) >= level) if long else (float(bars["low"][j]) <= level):
            return True
    return False


def _expiry_index(bars, expires_at: float) -> int:
    return int(np.searchsorted(bars["t"], expires_at, side="left"))


def exit_fee(exit_reason: Optional[str]) -> float:
    """A target is a resting limit (maker); a stop or a time exit is taker."""
    return FEE_MAKER_PCT if exit_reason == "target" else FEE_TAKER_PCT


def _gross(long: bool, entry: float, exit_px: float) -> float:
    return ((exit_px - entry) if long else (entry - exit_px)) / entry * 100.0


def _score(long: bool, entry: float, ex: Dict[str, Any],
           entry_fee: float = FEE_MAKER_PCT) -> Dict[str, Any]:
    out = {"status": ex["status"], "mfe_pct": round(ex["mfe"], 4), "mae_pct": round(ex["mae"], 4)}
    if ex["status"] == "resolved":
        g = _gross(long, entry, ex["exit"])
        out.update(exit=ex["exit"], exit_at=ex["exit_at"], exit_reason=ex["exit_reason"],
                   gross_pct=round(g, 4), net_pct=round(g - ROUND_TRIP_PCT, 4),
                   fees_pct=round(entry_fee + exit_fee(ex["exit_reason"]), 4))
    return out


def _combine(long: bool, legs: List[Tuple[float, float, Dict[str, Any]]],
             entry_fee: float) -> Dict[str, Any]:
    """Several exits of one position into one row, weighted by size.

    ``legs``: (weight, entry price, exit walk). Returns per FILLED unit, like
    every other row; ``filled_frac`` is set by the caller.
    """
    w = sum(x[0] for x in legs)
    head = legs[0][2]
    if any(ex["status"] != "resolved" for _, _, ex in legs):
        return {"status": "open", "mfe_pct": round(head["mfe"], 4),
                "mae_pct": round(head["mae"], 4)}
    g = sum(wt * _gross(long, e, ex["exit"]) for wt, e, ex in legs) / w
    fee = entry_fee + sum(wt * exit_fee(ex["exit_reason"]) for wt, _, ex in legs) / w
    reasons = sorted({ex["exit_reason"] for _, _, ex in legs})
    return {"status": "resolved", "exit": sum(wt * ex["exit"] for wt, _, ex in legs) / w,
            "exit_at": max(ex["exit_at"] for _, _, ex in legs),
            "exit_reason": reasons[0] if len(reasons) == 1 else "+".join(reasons),
            "gross_pct": round(g, 4), "net_pct": round(g - ROUND_TRIP_PCT, 4),
            "fees_pct": round(fee, 4), "mfe_pct": round(max(ex["mfe"] for _, _, ex in legs), 4),
            "mae_pct": round(max(ex["mae"] for _, _, ex in legs), 4)}


def fixed_rule_levels(menu: List[Dict[str, Any]], price: float, atr: float,
                      side: str) -> Tuple[Optional[Dict[str, float]], str]:
    """Entry / stop / target picked mechanically, or (None, reason).

    * entry  — best-scoring level on the entry side within RULE_ENTRY_MAX_ATR;
    * stop   — the NEAREST level beyond the entry whose stop (level ∓ buffer)
               sits RULE_STOP_ATR × ATR from the entry;
    * target — best-scoring level on the profit side clearing the cost floor.
    """
    if not menu or not price or not atr:
        return None, "no_menu"
    long = side == "long"
    below = [lv for lv in menu if lv["side"] == "below"]
    above = [lv for lv in menu if lv["side"] == "above"]
    entry_side, profit_side = (below, above) if long else (above, below)
    cands = [lv for lv in entry_side if abs(float(lv["distance_atr"])) <= RULE_ENTRY_MAX_ATR]
    if not cands:
        return None, "no_entry_level"
    e = max(cands, key=lambda lv: (lv["score"], -abs(float(lv["distance_atr"]))))
    entry = float(e["price"])
    stops = []
    for lv in entry_side:
        p = float(lv["price"])
        if (p >= entry) if long else (p <= entry):
            continue
        stop = p - RULE_STOP_BUFFER_ATR * atr if long else p + RULE_STOP_BUFFER_ATR * atr
        d = abs(entry - stop) / atr
        if RULE_STOP_ATR[0] <= d <= RULE_STOP_ATR[1]:
            stops.append((abs(entry - p), stop))
    if not stops:
        return None, "no_stop_level"
    stop = min(stops)[1]
    tgts = [lv for lv in profit_side
            if abs(float(lv["price"]) - entry) / entry * 100 >= RULE_COST_FLOOR_PCT]
    if not tgts:
        return None, "no_target_level"
    t = max(tgts, key=lambda lv: (lv["score"], -abs(float(lv["distance_atr"]))))
    return {"entry": entry, "stop": stop, "target": float(t["price"])}, ""


def walk_setup(setup: Dict[str, Any], cd: Any, now: float) -> Dict[str, Dict[str, Any]]:
    """All arms for one accepted setup. Pure: the setup row + its 5m bucket."""
    long = setup["side"] == "long"
    entries = json.loads(setup["entries_json"] or "[]")
    targets = json.loads(setup["targets_json"] or "[]")
    stop = float(setup["stop_price"])
    target = float(targets[0]["price"])
    expires = float(setup["expires_at"])
    bars, why = window(cd, float(setup["submitted_at"]))
    out: Dict[str, Dict[str, Any]] = {"none": {"status": "resolved", "gross_pct": 0.0,
                                               "net_pct": 0.0, "exit_reason": "no_trade"}}
    if bars is None or len(bars["t"]) == 0:
        why = why or "no_bars_yet"
        # History that rolled off cannot come back. A missing or undated series
        # can, so it waits until the setup could no longer have resolved.
        gone = why == "history_rolled_off" or now > expires + HOLD_HORIZON_S
        for arm in ARMS:
            if arm != "none":
                out[arm] = {"status": "insufficient" if gone else "open", "reason": why}
        return out

    m_entry = float(bars["open"][0])
    m_at = float(bars["t"][0])
    tp2 = float(targets[1]["price"]) if len(targets) > 1 else None
    exp_i = _expiry_index(bars, expires)
    window_closed = float(bars["t"][-1]) + STEP_S >= expires

    def at_market(stop: float, target: float, **extra: Any) -> Dict[str, Any]:
        why = market_geometry(long, m_entry, stop, target)
        if why:
            return _no_valid_trade(m_entry, m_at, why, fees_pct=0.0, **extra)
        r = _score(long, m_entry, _exit_walk(bars, 0, long, m_entry, stop, target, now),
                   entry_fee=FEE_TAKER_PCT)
        r.update(entry=m_entry, entry_at=m_at, **extra)
        return r

    out["market"] = at_market(stop, target, filled_frac=1.0, unfilled=0)

    def unfilled(scored: Dict[str, Any], target: float) -> Dict[str, Any]:
        """A limit the market never reached: the market outcome, flagged. It is
        a counterfactual and earns 0.00% when realized (see ``summary``)."""
        scored.setdefault("reason", "scored_at_market")
        scored["tp1_before_fill"] = int(_touched(bars, exp_i, long, target))
        return scored

    def limit_arm(legs: List[Dict[str, Any]], stop: float = stop,
                  target: float = target) -> Dict[str, Any]:
        """Each leg from its OWN fill bar; a leg filling after the position
        exited is cancelled; the horizon runs from the first fill."""
        fills = [(leg, _limit_fill(bars, long, float(leg["price"]), expires)) for leg in legs]
        got: List[Tuple[Dict[str, Any], int]] = sorted(
            ((leg, j) for leg, j in fills if j is not None), key=lambda x: x[1])
        if not got:
            if not window_closed:
                return {"status": "open", "reason": "awaiting_fill"}
            return unfilled(at_market(stop, target, unfilled=1, filled_frac=0.0), target)
        j0 = got[0][1]
        t0 = float(bars["t"][j0])
        first = _exit_walk(bars, j0, long, float(got[0][0]["price"]), stop, target, now,
                           target_on_fill_bar=False)
        kept: List[Tuple[float, float, Dict[str, Any]]] = []
        cancelled = 0
        for k, (leg, j) in enumerate(got):
            if k and first["status"] == "resolved" and j > first["idx"]:
                cancelled += 1  # the position was already out when this level traded
                continue
            ex = first if k == 0 else _exit_walk(bars, j, long, float(leg["price"]), stop,
                                                 target, now, target_on_fill_bar=False, t0=t0)
            kept.append((float(leg["weight"]), float(leg["price"]), ex))
        # A later leg that has not filled yet while the first is still open
        # needs no special case: the first leg's walk is open, so the row is.
        r = _combine(long, kept, FEE_MAKER_PCT)
        w = sum(x[0] for x in kept)
        r.update(entry=sum(x[0] * x[1] for x in kept) / w, entry_at=t0,
                 filled_frac=round(w, 4), unfilled=0,
                 tp1_before_fill=int(_touched(bars, j0, long, target)))
        if cancelled:
            r["reason"] = f"legs_cancelled_after_exit:{cancelled}"
        return r

    first_leg = dict(entries[0])
    first_leg["weight"] = 1.0
    out["analyst"] = limit_arm([first_leg])
    out["tranche"] = limit_arm(entries)

    def ladder_from(start: int, entry: float, fee: float, on_fill: bool) -> Dict[str, Any]:
        t0 = float(bars["t"][start])
        legs = [(LADDER_SPLIT, entry, _exit_walk(bars, start, long, entry, stop, target, now,
                                                 target_on_fill_bar=on_fill, t0=t0)),
                (1.0 - LADDER_SPLIT, entry, _exit_walk(bars, start, long, entry, stop, tp2,
                                                       now, target_on_fill_bar=on_fill, t0=t0))]
        r = _combine(long, legs, fee)
        r.update(entry=entry, entry_at=t0)
        if tp2 is None:
            r["reason"] = "no_tp2_runner_to_stop_or_horizon"
        return r

    e1 = float(entries[0]["price"])
    j = _limit_fill(bars, long, e1, expires)
    if j is not None:
        lad = ladder_from(j, e1, FEE_MAKER_PCT, on_fill=False)
        lad.update(filled_frac=1.0, unfilled=0, tp1_before_fill=int(_touched(bars, j, long,
                                                                              target)))
    elif not window_closed:
        lad = {"status": "open", "reason": "awaiting_fill"}
    elif market_geometry(long, m_entry, stop, target):
        lad = unfilled(_no_valid_trade(m_entry, m_at, market_geometry(long, m_entry, stop, target),
                                       fees_pct=0.0, unfilled=1, filled_frac=0.0), target)
    else:
        lad = ladder_from(0, m_entry, FEE_TAKER_PCT, on_fill=True)
        lad.update(filled_frac=0.0, unfilled=1)
        lad = unfilled(lad, target)
    out["ladder"] = lad

    menu_raw = setup.get("menu_json")
    if not menu_raw:
        out["fixed_rule"] = {"status": "insufficient", "reason": "no_menu_stamped"}
    else:
        lv, why_not = fixed_rule_levels(json.loads(menu_raw), float(setup.get("price_at_submit")
                                                                    or 0.0),
                                        float(setup.get("atr_1h") or 0.0), setup["side"])
        if lv is None:
            out["fixed_rule"] = {"status": "resolved", "gross_pct": 0.0, "net_pct": 0.0,
                                 "fees_pct": 0.0, "exit_reason": "no_rule_setup",
                                 "reason": why_not}
        else:
            out["fixed_rule"] = limit_arm([{"price": lv["entry"], "weight": 1.0}],
                                          stop=lv["stop"], target=lv["target"])
    out["none"]["fees_pct"] = 0.0
    return out


# ── ledger I/O ────────────────────────────────────────────────────────────


def _migrate(con: sqlite3.Connection) -> None:
    con.execute(_SCHEMA)
    cols = {r[1] for r in con.execute("PRAGMA table_info(walks)")}
    for col, typ in _WALK_COLS:
        if col not in cols:
            con.execute(f"ALTER TABLE walks ADD COLUMN {col} {typ}")


def _connect(path: str) -> sqlite3.Connection:
    con = sqlite3.connect(path, timeout=10)
    con.row_factory = sqlite3.Row
    _migrate(con)
    return con


def repair_fees(con: sqlite3.Connection) -> int:
    """Per-row order-type fees for rows walked before ``fees_pct`` existed.

    Exact from the row's own fields: the entry was taker when the row entered
    at market (the market arm, or an unfilled limit scored at market) and maker
    otherwise; the exit is maker at a target and taker at a stop or a time
    exit; a row with no trade pays nothing. v1 never booked a mixed exit, so
    one exit reason per row is the whole story. Idempotent.
    """
    rows = [dict(r) for r in con.execute(
        "SELECT setup_id, arm, unfilled, exit_reason FROM walks "
        "WHERE status='resolved' AND fees_pct IS NULL")]
    with con:
        for r in rows:
            if r["exit_reason"] in NO_TRADE_EXITS:
                fee = 0.0
            else:
                taker_in = r["arm"] == "market" or bool(r["unfilled"])
                fee = (FEE_TAKER_PCT if taker_in else FEE_MAKER_PCT) + exit_fee(r["exit_reason"])
            con.execute("UPDATE walks SET fees_pct=? WHERE setup_id=? AND arm=?",
                        (round(fee, 4), r["setup_id"], r["arm"]))
    return len(rows)


# ── funding, from the derivatives recorder ─────────────────────────────────


def funding_cost_pct(dcon: sqlite3.Connection, symbol: str, side: str, t_from: float,
                     t_to: float) -> Tuple[Optional[float], str]:
    """Funding paid over a hold, as % of notional (positive = paid), or
    (None, reason).

    Settlement times come from the recorder's ``next_funding_ms``, so a symbol
    on a 4h schedule is charged six times a day, not three. The rate charged at
    a settlement is the last recorded ``funding_rate`` before it that named that
    settlement. A long pays a positive rate; a short receives it. Every hour of
    the hold must be recorded, or the answer is unknown, never zero.
    """
    h0 = int(t_from // 3600) * 3_600_000
    h1 = int(t_to // 3600) * 3_600_000
    rows = dcon.execute(
        "SELECT hour_ms, funding_rate, next_funding_ms FROM deriv_hourly "
        "WHERE symbol=? AND hour_ms BETWEEN ? AND ? ORDER BY hour_ms",
        (symbol, h0, h1)).fetchall()
    if not rows:
        any_row = dcon.execute("SELECT 1 FROM deriv_hourly WHERE symbol=? LIMIT 1",
                               (symbol,)).fetchone()
        return None, "recorder_gap" if any_row else "symbol_not_recorded"
    have = {int(r[0]) for r in rows}
    if any(h not in have for h in range(h0, h1 + 1, 3_600_000)):
        return None, "recorder_gap"
    settles = sorted({int(r[2]) for r in rows if r[2]})
    crossed = [t for t in settles if t_from * 1000 < t <= t_to * 1000]
    sign = 1.0 if side == "long" else -1.0
    cost = 0.0
    for t in crossed:
        rates = [r[1] for r in rows if r[2] is not None and int(r[2]) == t
                 and int(r[0]) < t and r[1] is not None]
        if not rates:
            return None, "rate_missing"
        cost += sign * float(rates[-1]) * 100.0
    return round(cost, 5), ("charged" if crossed else "none_crossed")


def backfill_funding(con: sqlite3.Connection, deriv_path: Optional[str],
                     limit: int = 500) -> int:
    """Stamp funding on resolved rows that have none yet. Bounded per step.
    A row with no trade is 0.00% and known. Recorder data is persistent, so a
    row walked weeks ago is charged exactly as one walked today."""
    import os

    rows = [dict(r) for r in con.execute(
        "SELECT w.setup_id, w.arm, w.exit_reason, w.entry_at, w.exit_at, s.symbol, s.side "
        "FROM walks w JOIN setups s ON s.setup_id = w.setup_id "
        "WHERE w.status='resolved' AND w.funding_reason IS NULL LIMIT ?", (int(limit),))]
    if not rows:
        return 0
    dcon = None
    if deriv_path and os.path.exists(deriv_path):
        dcon = sqlite3.connect(deriv_path, timeout=10)
    try:
        with con:
            for r in rows:
                if r["exit_reason"] in NO_TRADE_EXITS:
                    val, why = 0.0, "no_trade"
                elif r["entry_at"] is None or r["exit_at"] is None:
                    val, why = None, "no_hold_times"
                elif dcon is None:
                    val, why = None, "no_recorder"
                else:
                    try:
                        val, why = funding_cost_pct(dcon, r["symbol"], r["side"],
                                                    float(r["entry_at"]), float(r["exit_at"]))
                    except sqlite3.Error:
                        val, why = None, "recorder_unreadable"
                if why in ("no_recorder", "recorder_unreadable"):
                    continue  # a fault on our side; retry next step, never stamp it
                con.execute("UPDATE walks SET funding_pct=?, funding_reason=? "
                            "WHERE setup_id=? AND arm=?",
                            (val, why, r["setup_id"], r["arm"]))
    finally:
        if dcon is not None:
            dcon.close()
    return len(rows)


def _deriv_path() -> Optional[str]:
    try:
        from src import derivatives_recorder
        return derivatives_recorder.get_recorder().path
    except Exception:  # noqa: BLE001 — funding is optional; reads unknown
        return None


def repair_geometry(con: sqlite3.Connection) -> int:
    """Correct stored rows walked before :func:`market_geometry` existed.

    A row entered at market (the ``market`` arm, or any limit arm scored at
    market because it never filled) whose entry was already past its own target
    or stop was booked as walked. Every input is on the row: the entry the walk
    used, and the arm's stop and target (the setup's, or the fixed rule's,
    re-derived from the menu stamped at submit). So the correction needs no
    bars and is exact. Idempotent: a repaired row no longer matches.
    """
    rows = [dict(r) for r in con.execute(
        "SELECT w.setup_id, w.arm, w.entry, s.side, s.stop_price, s.targets_json, "
        "s.menu_json, s.price_at_submit, s.atr_1h FROM walks w JOIN setups s "
        "ON s.setup_id = w.setup_id WHERE w.status = 'resolved' "
        "AND w.exit_reason IN ('target', 'stop', 'horizon') "
        "AND (w.arm = 'market' OR w.unfilled = 1) AND w.entry IS NOT NULL")]
    fixed = 0
    for r in rows:
        long = r["side"] == "long"
        try:
            if r["arm"] == "fixed_rule":
                lv, _ = fixed_rule_levels(json.loads(r["menu_json"] or "[]"),
                                          float(r["price_at_submit"] or 0.0),
                                          float(r["atr_1h"] or 0.0), r["side"])
                if lv is None:
                    continue
                stop, target = lv["stop"], lv["target"]
            else:
                stop = float(r["stop_price"])
                target = float(json.loads(r["targets_json"] or "[]")[0]["price"])
        except (TypeError, ValueError, KeyError, IndexError):
            continue
        why = market_geometry(long, float(r["entry"]), stop, target)
        if not why:
            continue
        with con:
            con.execute(
                "UPDATE walks SET exit_reason='no_valid_trade', reason=?, gross_pct=0.0, "
                "net_pct=0.0, exit=NULL, exit_at=NULL WHERE setup_id=? AND arm=?",
                (why, r["setup_id"], r["arm"]))
        fixed += 1
    return fixed


#: A v1 tranche row whose legs both filled used the blended walk; re-walk it.
_NEEDS_REWALK = ("w.arm='tranche' AND w.walk_v IS NULL AND w.status='resolved' "
                 "AND COALESCE(w.unfilled,0)=0 AND w.filled_frac >= 0.999 "
                 "AND json_array_length(s.entries_json) > 1")


def step(engine: Any, *, now: Optional[float] = None, path: Optional[str] = None,
         max_setups: int = 200, deriv_path: Optional[str] = None) -> Dict[str, int]:
    """Advance every accepted setup that is still owed a verdict on any arm.

    A row already ``resolved`` or ``insufficient`` is never overwritten. The one
    exception is a v1 tranche row with the blend defect: it is re-walked while
    its bars exist, and refused by name when they have rolled off.
    """
    import os

    from src import analyst_plan

    now = time.time() if now is None else now
    path = path or analyst_plan.get_ledger().path
    counts: Dict[str, int] = {"setups": 0, "resolved": 0, "open": 0, "insufficient": 0}
    if not os.path.exists(path):
        return counts
    con = _connect(path)
    try:
        counts["geometry_repaired"] = repair_geometry(con)
        counts["fees_backfilled"] = repair_fees(con)
        setups = [dict(r) for r in con.execute(
            "SELECT s.* FROM setups s WHERE s.status='accepted' AND (("
            " SELECT COUNT(*) FROM walks w WHERE w.setup_id=s.setup_id"
            " AND w.status IN ('resolved','insufficient')) < ? "
            f" OR EXISTS (SELECT 1 FROM walks w WHERE w.setup_id=s.setup_id AND {_NEEDS_REWALK})) "
            "ORDER BY s.submitted_at LIMIT ?", (len(ARMS), int(max_setups)))]
        store = getattr(engine, "data_store", None)
        buckets = getattr(store, "candles", None) or {}
        for s in setups:
            counts["setups"] += 1
            settled = {r["arm"]: dict(r) for r in con.execute(
                "SELECT arm, status, walk_v, unfilled, filled_frac FROM walks "
                "WHERE setup_id=? AND status IN ('resolved','insufficient')", (s["setup_id"],))}
            t = settled.get("tranche")
            rewalk = bool(t and t["walk_v"] is None and t["status"] == "resolved"
                          and not t["unfilled"] and (t["filled_frac"] or 0) >= 0.999
                          and len(json.loads(s.get("entries_json") or "[]")) > 1)
            arms = walk_setup(s, (buckets.get(s["symbol"]) or {}).get(TF), now)
            with con:
                for arm, r in arms.items():
                    if arm in settled and not (arm == "tranche" and rewalk):
                        continue
                    if arm == "tranche" and rewalk:
                        if r["status"] != "resolved":
                            if r["status"] == "insufficient":
                                con.execute(
                                    "UPDATE walks SET status='insufficient', "
                                    "reason='blend_defect_history_rolled_off', updated_at=? "
                                    "WHERE setup_id=? AND arm='tranche'", (now, s["setup_id"]))
                                counts["tranche_unrewalkable"] = counts.get(
                                    "tranche_unrewalkable", 0) + 1
                            continue
                        counts["tranche_rewalked"] = counts.get("tranche_rewalked", 0) + 1
                        con.execute("UPDATE walks SET funding_pct=NULL, funding_reason=NULL "
                                    "WHERE setup_id=? AND arm='tranche'", (s["setup_id"],))
                    vals = {**r, "setup_id": s["setup_id"], "arm": arm, "updated_at": now,
                            "walk_v": WALK_VERSION}
                    con.execute(
                        f"INSERT INTO walks ({', '.join(_ROW_COLS)}) VALUES "
                        f"({', '.join('?' * len(_ROW_COLS))}) ON CONFLICT(setup_id, arm) "
                        f"DO UPDATE SET {', '.join(f'{c}=excluded.{c}' for c in _ROW_COLS[2:])}",
                        tuple(vals.get(c) for c in _ROW_COLS))
            st = arms["tranche"]["status"]
            counts[st] = counts.get(st, 0) + 1
        counts["funding_stamped"] = backfill_funding(
            con, deriv_path if deriv_path is not None else _deriv_path())
    finally:
        con.close()
    return counts


def _arm_summary(nets: List[float]) -> Dict[str, Any]:
    if not nets:
        return {"n": 0}
    xs = sorted(nets)
    k = max(1, int(round(len(xs) * 0.01)))
    trimmed = xs[:-k] if len(xs) > k else []
    return {
        "n": len(xs), "win_rate": round(sum(x > 0 for x in xs) / len(xs), 4),
        "avg_net_pct": round(sum(xs) / len(xs), 4), "total_net_pct": round(sum(xs), 4),
        "without_top_1pct": {"dropped": k, "n": len(trimmed),
                             "avg_net_pct": round(sum(trimmed) / len(trimmed), 4)
                             if trimmed else None},
    }


def _calibration(path: str) -> Dict[str, Any]:
    """How good the analyst's forecasts are: its p_target against what happened.

    Scored on the ``analyst`` arm's FILLED, resolved setups. An unfilled limit
    never tested the forecast, so it is excluded and counted. Brier score
    (lower is better; always guessing the observed hit rate scores
    rate*(1-rate)).
    """
    con = _connect(path)
    try:
        scols = {r[1] for r in con.execute("PRAGMA table_info(setups)")}
        p_stop = "s.p_stop" if "p_stop" in scols else "NULL"
        rows = [dict(r) for r in con.execute(
            f"SELECT s.p_target, {p_stop} AS p_stop, w.exit_reason, w.unfilled FROM setups s "
            "JOIN walks w ON w.setup_id=s.setup_id AND w.arm='analyst' "
            "WHERE s.p_target IS NOT NULL AND w.status='resolved'")]
    except sqlite3.OperationalError:
        return {"n": 0, "reason": "ledger predates p_target"}
    finally:
        con.close()
    scored = [r for r in rows if not r["unfilled"]]
    if not scored:
        return {"n": 0, "excluded_unfilled": len(rows) - len(scored)}
    ps = [float(r["p_target"]) for r in scored]
    hits = [1.0 if r["exit_reason"] == "target" else 0.0 for r in scored]
    rate = sum(hits) / len(hits)
    return {"n": len(scored), "excluded_unfilled": len(rows) - len(scored),
            "mean_p_target": round(sum(ps) / len(ps), 4), "hit_rate": round(rate, 4),
            "brier": round(sum((p - h) ** 2 for p, h in zip(ps, hits)) / len(ps), 4),
            "brier_of_base_rate": round(rate * (1 - rate), 4),
            "three_outcome": _three_outcome(scored)}


def _three_outcome(scored: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Target / stop / time exit, scored together (multi-class Brier, 0–2).

    Only setups that stated ``p_stop`` count; ``p_neither`` is the remainder.
    The base rate is always forecasting the observed shares, the bar a
    forecast has to beat to say anything.
    """
    rows = [r for r in scored if r.get("p_stop") is not None
            and r.get("exit_reason") in ("target", "stop", "horizon")]
    if not rows:
        return {"n": 0, "reason": "no setup stated p_stop yet"}
    keys = ("target", "stop", "horizon")
    obs = {k: sum(r["exit_reason"] == k for r in rows) / len(rows) for k in keys}
    def probs(r):
        pt, pst = float(r["p_target"]), float(r["p_stop"])
        return {"target": pt, "stop": pst, "horizon": max(0.0, 1.0 - pt - pst)}
    brier = sum(sum((probs(r)[k] - (r["exit_reason"] == k)) ** 2 for k in keys)
                for r in rows) / len(rows)
    base = sum(obs[k] * (1 - obs[k]) for k in keys)
    return {"n": len(rows), "observed": {k: round(v, 4) for k, v in obs.items()},
            "mean_forecast": {k: round(sum(probs(r)[k] for r in rows) / len(rows), 4)
                              for k in keys},
            "brier": round(brier, 4), "brier_of_base_rate": round(base, 4)}


def _split(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """The analyst arm, taken apart: filled vs scored-at-market, and by exit.

    The headline per-arm average pools limits that filled with limits scored at
    the market outcome; read alone it is mostly the market arm. ``by_exit``
    exists because the walk has THREE outcomes, not two: a filled setup can end
    at the target, the stop, or the 12h time exit. An expectancy computed as
    p(target) x R - (1 - p) treats every non-target as a full loss.
    """
    res = [r for r in rows if r["status"] == "resolved" and r["net_pct"] is not None]
    filled = [r for r in res if not r.get("unfilled")]
    by_exit: Dict[str, Any] = {}
    for r in filled:
        b = by_exit.setdefault(str(r.get("exit_reason")), [])
        b.append(float(r["net_pct"]))
    return {
        "filled": _arm_summary([float(r["net_pct"]) for r in filled]),
        "scored_at_market": _arm_summary([float(r["net_pct"]) for r in res
                                          if r.get("unfilled")]),
        "fill_rate": round(len(filled) / len(res), 4) if res else None,
        "filled_by_exit": {k: {"n": len(v), "share": round(len(v) / len(filled), 4),
                               "avg_net_pct": round(sum(v) / len(v), 4)}
                           for k, v in sorted(by_exit.items())},
    }


#: Feed states that are still exposure: a limit waiting, a filled position, or
#: a setup the walk has not reached yet.
OPEN_STATES = ("not_walked", "waiting_data", "pending", "active")
CLOSED_STATES = ("tp_hit", "sl_hit", "time_exit", "not_filled")
RECENT_CLOSED = 10


def book(feed_rows: List[Dict[str, Any]], now: float) -> Dict[str, Any]:
    """What is still open, by side, off the feed rows. The analyst reads this
    before planning; before 2026-11-25 it had only its last three plans and
    guessed what was still open."""
    open_rows = [r for r in feed_rows if r["state"] in OPEN_STATES]
    items = []
    for r in open_rows:
        a = r.get("analyst") or {}
        items.append({
            "symbol": r["symbol"], "side": r["side"], "state": r["state"],
            "age_h": round((now - float(r["submitted_at"])) / 3600.0, 2),
            "entry": r["entries"][0]["price"] if r["entries"] else None,
            "stop": r["stop"], "tp1": r["targets"][0] if r["targets"] else None,
            "p_target": r.get("p_target"), "mfe_pct": a.get("mfe_pct"),
            "mae_pct": a.get("mae_pct")})
    side = {s: sum(i["side"] == s for i in items) for s in ("long", "short")}
    return {"n": len(items), "by_side": side,
            "active_by_side": {s: sum(i["side"] == s and i["state"] == "active"
                                      for i in items) for s in ("long", "short")},
            "symbols": sorted({i["symbol"] for i in items}), "setups": items,
            "note": ("Setups still pending (limit not reached, not expired), active "
                     "(filled, not yet stopped / targeted / timed out) or not walked yet. "
                     "Alts move with BTC: same-side setups are one bet, not several.")}


def recent_closed(feed_rows: List[Dict[str, Any]], n: int = RECENT_CLOSED) -> List[Dict[str, Any]]:
    """The last closed setups, newest first, with what each one actually did."""
    out = []
    for r in feed_rows:
        if r["state"] not in CLOSED_STATES:
            continue
        a = r.get("analyst") or {}
        out.append({k: r.get(k) for k in ("symbol", "side", "archetype", "p_target",
                                          "rr_tp1", "stop_atr", "entry_dist_atr",
                                          "pos_in_7d", "state")}
                   | {"submitted_at": r["submitted_at"], "net_pct": a.get("net_pct"),
                      "exit_reason": a.get("exit_reason"), "mfe_pct": a.get("mfe_pct"),
                      "mae_pct": a.get("mae_pct"),
                      # What the limit earned: 0.00% when it never filled.
                      "realized_net_pct": (0.0 if r["state"] == "not_filled"
                                           else a.get("net_pct")),
                      "market_net_pct": (r.get("market") or {}).get("net_pct")})
        if len(out) >= n:
            break
    return out


# ── realized, per posted setup ───────────────────────────────────────────


def blend_defect(r: Dict[str, Any]) -> bool:
    """A v1 tranche row with both legs filled: walked on a blended entry."""
    try:
        legs = len(json.loads(r.get("s_entries") or "[]"))
    except ValueError:
        legs = 0
    return (r["arm"] == "tranche" and r.get("walk_v") is None and r["status"] == "resolved"
            and not r.get("unfilled") and float(r.get("filled_frac") or 0) >= 0.999
            and legs > 1)


def realized_pct(r: Dict[str, Any], *, cost_model: bool = False) -> Optional[float]:
    """What the order earned, per setup posted, or None when not known.

    An unfilled limit earns 0.00%; a fill earns its return times
    ``filled_frac``. ``cost_model`` charges order-type fees and recorded
    funding instead of the flat 0.07%, and is None while either is unknown.
    """
    if r["status"] != "resolved" or r.get("net_pct") is None:
        return None
    if r.get("exit_reason") in NO_TRADE_EXITS:
        return 0.0
    if r["arm"] in LIMIT_ARMS and r.get("unfilled"):
        return 0.0
    ff = 1.0 if r.get("filled_frac") is None else float(r["filled_frac"])
    if not cost_model:
        return float(r["net_pct"]) * ff
    if r.get("fees_pct") is None or r.get("funding_pct") is None:
        return None
    return (float(r["gross_pct"]) - float(r["fees_pct"]) - float(r["funding_pct"])) * ff


def _day(ts: Any) -> Optional[str]:
    if ts is None:
        return None
    return time.strftime("%Y-%m-%d", time.gmtime(float(ts)))


def _by_day(pairs: List[Tuple[Optional[str], float]]) -> Dict[str, Any]:
    days: Dict[str, float] = {}
    counts: Dict[str, int] = {}
    for d, v in pairs:
        if d is None:
            continue
        days[d] = days.get(d, 0.0) + v
        counts[d] = counts.get(d, 0) + 1
    if not days:
        return {"n_days": 0}
    xs = list(days.values())
    return {"n_days": len(xs), "days_positive": sum(x > 0 for x in xs),
            "avg_day_total_pct": round(sum(xs) / len(xs), 4),
            "worst_day": min(((round(v, 4), d) for d, v in days.items()))[::-1],
            "best_day": max(((round(v, 4), d) for d, v in days.items()))[::-1],
            "rows_per_day_max": max(counts.values()),
            "days": [{"day": d, "n": counts[d], "total_pct": round(days[d], 4)}
                     for d in sorted(days)]}


def _arm_block(arm: str, mine: List[Dict[str, Any]]) -> Dict[str, Any]:
    res = [r for r in mine if r["status"] == "resolved" and r.get("net_pct") is not None]
    excluded = [r for r in res if blend_defect(r)]
    res = [r for r in res if not blend_defect(r)]
    # realized_pct is None only for an unresolved row, and ``res`` holds none.
    realized = [(r, v) for r in res if (v := realized_pct(r)) is not None]
    cost = [(r, realized_pct(r, cost_model=True)) for r in res]
    known = [v for _, v in cost if v is not None]
    # The flat-fee result over the SAME rows the cost model could price, so the
    # difference is cost alone. Without it, a filled row whose funding is
    # unknown drops out while unfilled rows stay at 0.00%, and the cost-model
    # average is pulled toward zero by selection rather than by cost.
    flat_same = [realized_pct(r) or 0.0 for r, v in cost if v is not None]
    known_filled = sum(1 for r, v in cost if v is not None
                       and not (arm in LIMIT_ARMS and r.get("unfilled"))
                       and r.get("exit_reason") not in NO_TRADE_EXITS)
    is_limit = arm in LIMIT_ARMS
    filled = [r for r in res if not (is_limit and r.get("unfilled"))
              and r.get("exit_reason") not in NO_TRADE_EXITS]
    missed = [r for r in res if is_limit and r.get("unfilled")]
    out = {
        **_arm_summary([v for _, v in realized]),
        "basis": "realized per setup posted (unfilled limit = 0.00%), flat 0.07% fee",
        "open": sum(r["status"] == "open" for r in mine),
        "insufficient": sum(r["status"] == "insufficient" for r in mine),
        "unfilled_scored_at_market": len(missed),
        "no_valid_trade": sum(r.get("exit_reason") == "no_valid_trade" for r in mine),
        "excluded_blend_defect": len(excluded),
        "filled": _arm_summary([float(r["net_pct"]) for r in filled]),
        "cost_model": {**_arm_summary(known), "unknown": len(cost) - len(known),
                       "known_filled": known_filled,
                       "flat_fee_same_rows_avg_pct": (round(sum(flat_same) / len(flat_same), 4)
                                                      if flat_same else None),
                       "basis": ("maker 0.02% / taker 0.05% by order type, plus recorded "
                                 "funding; slippage not modelled")},
        "by_day": _by_day([(_day(r.get("s_submitted_at")), v) for r, v in realized]),
    }
    if is_limit:
        out["with_unfilled_at_market"] = _arm_summary([float(r["net_pct"]) for r in res])
        out["missed_market"] = {**_arm_summary([float(r["net_pct"]) for r in missed]),
                                "note": ("Counterfactual and selected: a limit goes unfilled "
                                         "because price ran away from it. Never an expected "
                                         "result for a market entry; read the market arm.")}
    return out


def _whatif(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """The analyst arm under rules that only REMOVE fills, so each is exact
    under the walk's own rules: a dropped fill earns 0.00%."""
    res = [r for r in rows if r["status"] == "resolved" and r.get("net_pct") is not None]
    base = [realized_pct(r) or 0.0 for r in res]
    out: Dict[str, Any] = {"n": len(res), "baseline": _arm_summary(base)}
    for h in WHATIF_EXPIRY_H:
        vals, dropped = [], 0
        for r in res:
            late = (not r.get("unfilled") and r.get("entry_at") is not None
                    and r.get("s_submitted_at") is not None
                    and float(r["entry_at"]) - float(r["s_submitted_at"]) > h * 3600.0)
            dropped += late
            vals.append(0.0 if late else (realized_pct(r) or 0.0))
        out[f"expiry_{h}h"] = {**_arm_summary(vals), "fills_dropped": dropped}
    known = [r for r in res if r.get("unfilled") or r.get("tp1_before_fill") is not None]
    vals, dropped = [], 0
    for r in known:
        cancel = not r.get("unfilled") and bool(r.get("tp1_before_fill"))
        dropped += cancel
        vals.append(0.0 if cancel else (realized_pct(r) or 0.0))
    out["cancel_if_tp1_first"] = {**_arm_summary(vals), "fills_dropped": dropped,
                                  "unknown": len(res) - len(known),
                                  "note": "rows walked before v2 carry no tp1_before_fill"}
    out["unfilled_ran_to_tp1"] = sum(bool(r.get("unfilled")) and bool(r.get("tp1_before_fill"))
                                     for r in res)
    return out


# ── the comparison the spec asked for: the existing system, same window ─────


def existing_signals(since: Optional[float], now: float,
                     record_path: Optional[str] = None) -> Dict[str, Any]:
    """The engine's DELIVERED signals that closed inside the analyst's window.

    Read from the closed-signal record that ``/track-record`` and the app's
    Pulse read (``track_record.load_rows``: recorded by ``trade_monitor``,
    never reconstructed). Each row is its blended ``pnl_pct`` minus the same
    flat 0.07% the analyst arms are charged, so the two are net on one basis.

    Not a per-setup arm: the existing system trades its own symbols at its own
    times. What is comparable is the same calendar window, per trade and per
    day. Its rows are bucketed by CLOSE day and the analyst's by SUBMIT day;
    the analyst's hold is at most expiry + 12h, so the two calendars differ by
    under a day, and the note says so rather than pretending they align.
    """
    from src import track_record

    if since is None:
        return {"readable": False, "reason": "no_analyst_setup_yet"}
    rows, err = track_record.load_rows(record_path)
    if err:
        return {"readable": False, "reason": err}
    win, unreadable = [], 0
    for r in rows:
        ts = r.get("closed_at_ts")
        if ts is None or not since <= float(ts) <= now:
            continue
        try:
            win.append((r, float(r["pnl_pct"]) - ROUND_TRIP_PCT))
        except (TypeError, ValueError, KeyError):
            unreadable += 1  # counted, never scored zero
    groups: Dict[str, List[float]] = {}
    for r, v in win:
        groups.setdefault(f"{r.get('setup')} {r.get('direction')}", []).append(v)
    return {
        "readable": True, "since": since,
        "basis": "delivered closed signals in the analyst's window; pnl_pct minus 0.07%",
        **_arm_summary([v for _, v in win]),
        "no_pnl": unreadable,
        "by_day": _by_day([(_day(r.get("closed_at_ts")), v) for r, v in win]),
        "by_setup_side": sorted(
            ({"key": k, **_arm_summary(v)} for k, v in groups.items()),
            key=lambda g: -(g.get("total_net_pct") or 0.0)),
        "note": ("Recorded, not reconstructed: the signals users actually received. "
                 "Bucketed by close day; the analyst by submit day."),
    }


def _slices(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """The analyst and market arms by prompt version, and the analyst arm by
    archetype and side. A prompt change is judged on its own rows; pooling
    versions makes every new prompt look like the old one."""
    def by(arm: str, key) -> Dict[str, Any]:
        g: Dict[str, List[float]] = {}
        for r in rows:
            if r["arm"] != arm or r["status"] != "resolved" or blend_defect(r):
                continue
            v = realized_pct(r)
            if v is not None:
                g.setdefault(key(r), []).append(v)
        return {k: _arm_summary(v) for k, v in sorted(g.items())}

    pv = lambda r: r.get("s_prompt") or "unstamped (v1)"  # noqa: E731
    return {
        "by_prompt_version": {arm: by(arm, pv) for arm in ("analyst", "market", "tranche")},
        "analyst_by_archetype_side": by(
            "analyst", lambda r: f"{r.get('s_archetype') or '?'} {r.get('s_side') or '?'}"),
    }


def summary(path: Optional[str] = None, now: Optional[float] = None,
            record_path: Optional[str] = None) -> Dict[str, Any]:
    """What ``read.analyst_outcomes`` returns. Per arm, never pooled."""
    import os

    from src import analyst_plan

    now = time.time() if now is None else now
    path = path or analyst_plan.get_ledger().path
    if not os.path.exists(path):
        return {"readable": False, "reason": "no_ledger_yet"}
    con = _connect(path)
    try:
        pcols = {r[1] for r in con.execute("PRAGMA table_info(plans)")}
        pver = "p.prompt_version" if "prompt_version" in pcols else "NULL"
        rows = [dict(r) for r in con.execute(
            "SELECT w.*, s.submitted_at AS s_submitted_at, s.entries_json AS s_entries, "
            f"s.archetype AS s_archetype, s.side AS s_side, {pver} AS s_prompt "
            "FROM walks w LEFT JOIN setups s ON s.setup_id = w.setup_id "
            "LEFT JOIN plans p ON p.plan_id = s.plan_id")]
        first = con.execute("SELECT MIN(submitted_at) FROM setups "
                            "WHERE status='accepted'").fetchone()[0]
    finally:
        con.close()
    by_arm = {arm: _arm_block(arm, [r for r in rows if r["arm"] == arm]) for arm in ARMS}
    fd = feed(limit=FEED_MAX, path=path, now=now)
    frows = fd.get("rows") or []
    analyst_rows = [r for r in rows if r["arm"] == "analyst"]
    return {"readable": True, "by_arm": by_arm, "arms_not_built": list(ARMS_NOT_BUILT),
            "walk_version": WALK_VERSION,
            "analyst_split": _split(analyst_rows),
            "analyst_whatif": _whatif(analyst_rows),
            "existing_signals": existing_signals(first, now, record_path),
            **_slices(rows),
            "calibration": _calibration(path),
            "active_book": book(frows, now),
            "recent_closed": recent_closed(frows),
            "note": ("Each arm's headline is REALIZED per setup posted: an unfilled limit "
                     "earns 0.00%, a fill its net times filled_frac, net of a flat 0.07% "
                     "round trip. 'with_unfilled_at_market' is the old headline and "
                     "'missed_market' the unfilled rows alone, a selected counterfactual. "
                     "'cost_model' charges maker/taker by order type plus recorded funding. "
                     "A market entry already past its own target or stop is no_valid_trade "
                     "at 0.00%. Stop first on an ambiguous 5m bar. Read n, and by_day, "
                     "before any average.")}


# ── the feed: each accepted setup read as a signal (ops-only) ───────────────

#: Lifecycle states for one setup, read off the ``analyst`` arm (a limit at the
#: first entry, the arm a real order would be). A closed set, so ops can label
#: every one and badge anything else as unclassified.
FEED_STATES = ("not_walked", "waiting_data", "pending", "active", "tp_hit",
               "sl_hit", "time_exit", "not_filled", "insufficient")
FEED_MAX = 300


def _feed_state(w: Optional[Dict[str, Any]]) -> str:
    """One state per setup. ``not_filled`` covers a limit the market never
    reached: its PnL is the MARKET outcome and must never read as a fill."""
    if w is None:
        return "not_walked"
    st = w.get("status")
    if st == "insufficient":
        return "insufficient"
    if w.get("unfilled"):
        return "not_filled"
    if st == "open":
        if w.get("reason") == "awaiting_fill":
            return "pending"
        return "active" if w.get("entry") is not None else "waiting_data"
    return {"target": "tp_hit", "stop": "sl_hit",
            "horizon": "time_exit"}.get(str(w.get("exit_reason")), "insufficient")


def _arm_view(w: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if w is None:
        return None
    return {k: w.get(k) for k in ("status", "reason", "unfilled", "filled_frac", "entry",
                                   "entry_at", "exit", "exit_at", "exit_reason",
                                   "gross_pct", "net_pct", "mfe_pct", "mae_pct",
                                   "updated_at")}


def feed(limit: int = 100, path: Optional[str] = None,
         now: Optional[float] = None) -> Dict[str, Any]:
    """Every ACCEPTED analyst setup as a signal card, newest first.

    What ``read.analyst_feed`` returns. Ops-only: this reads the analyst ledger,
    which nothing on the money path reads, and reaches no subscriber.

    The state and PnL come from the ``analyst`` arm. The walk scores the FIRST
    target or the stop (else a 12h time exit); later targets are the analyst's
    and are shown, never booked. ``market`` and ``fixed_rule`` ride beside each
    row so a card can be read against its own controls, never pooled with them.
    """
    import os

    from src import analyst_plan

    now = time.time() if now is None else now
    path = path or analyst_plan.get_ledger().path
    if not os.path.exists(path):
        return {"readable": False, "reason": "no_ledger_yet", "rows": []}
    limit = max(1, min(int(limit or 100), FEED_MAX))
    con = analyst_plan.Ledger(path)._connect()  # runs the additive migrations
    try:
        con.execute(_SCHEMA)
        setups = [dict(r) for r in con.execute(
            "SELECT s.*, p.bias AS plan_bias, p.notes AS plan_notes FROM setups s "
            "LEFT JOIN plans p ON p.plan_id = s.plan_id WHERE s.status='accepted' "
            "ORDER BY s.submitted_at DESC, s.idx LIMIT ?", (limit,))]
        n_total = int(con.execute(
            "SELECT COUNT(*) FROM setups WHERE status='accepted'").fetchone()[0])
        walks: Dict[str, Dict[str, Dict[str, Any]]] = {}
        ids = [s["setup_id"] for s in setups]
        for i in range(0, len(ids), 500):
            chunk = ids[i:i + 500]
            q = ",".join("?" * len(chunk))
            for r in con.execute(f"SELECT * FROM walks WHERE setup_id IN ({q})", chunk):
                walks.setdefault(r["setup_id"], {})[r["arm"]] = dict(r)
    finally:
        con.close()

    rows: List[Dict[str, Any]] = []
    counts: Dict[str, int] = {k: 0 for k in FEED_STATES}
    for s in setups:
        arms = walks.get(s["setup_id"], {})
        a = arms.get("analyst")
        state = _feed_state(a)
        counts[state] = counts.get(state, 0) + 1
        try:
            entries = json.loads(s.get("entries_json") or "[]")
            targets = json.loads(s.get("targets_json") or "[]")
        except ValueError:
            entries, targets = [], []
        stop = s.get("stop_price")
        e1 = float(entries[0]["price"]) if entries else None
        t1 = float(targets[0]["price"]) if targets else None
        rr = (round(abs(t1 - e1) / abs(e1 - float(stop)), 3)
              if e1 is not None and t1 is not None and stop is not None
              and abs(e1 - float(stop)) > 0 else None)
        rows.append({
            "setup_id": s["setup_id"], "plan_id": s["plan_id"],
            "submitted_at": s["submitted_at"], "expires_at": s.get("expires_at"),
            "symbol": s.get("symbol"), "side": s.get("side"),
            "archetype": s.get("archetype"), "plan_mode": s.get("plan_mode"),
            "bias": s.get("plan_bias"), "plan_notes": s.get("plan_notes"),
            "price_at_submit": s.get("price_at_submit"), "atr_1h": s.get("atr_1h"),
            "entries": [{"price": float(e["price"]), "weight": float(e.get("weight") or 0)}
                        for e in entries],
            "stop": stop, "targets": [float(t["price"]) for t in targets],
            "stop_atr": s.get("stop_atr"), "tp1_pct": s.get("tp1_pct"), "rr_tp1": rr,
            "entry_dist_atr": (round(abs(e1 - float(s["price_at_submit"])) / float(s["atr_1h"]), 3)
                               if e1 is not None and s.get("price_at_submit")
                               and s.get("atr_1h") else None),
            "pos_in_7d": s.get("pos_in_7d"),
            "book_same_side": s.get("book_same_side"),
            "invalidation": s.get("invalidation"), "scenario": s.get("scenario"),
            "p_target": s.get("p_target"),
            "state": state,
            "analyst": _arm_view(a),
            "market": _arm_view(arms.get("market")),
            "fixed_rule": _arm_view(arms.get("fixed_rule")),
            "expired": bool(s.get("expires_at") and now >= float(s["expires_at"])),
        })
    return {"readable": True, "rows": rows, "n_accepted_total": n_total,
            "n_shown": len(rows), "limit": limit, "states": list(FEED_STATES),
            "counts": counts, "generated_at": now, "walk_step_s": STEP_S,
            "note": ("Dark, ops-only. State and PnL are the analyst arm: a limit at the "
                     "first entry, exiting at the FIRST target or the stop, else a time "
                     "exit after 12h; later targets are shown, not booked. Net of a 0.07% "
                     "round trip. A limit the market never reached is 'not_filled' and "
                     "carries the market outcome, never a fill.")}


def health(now: Optional[float] = None, path: Optional[str] = None) -> Tuple[bool, str]:
    """'Hourly plan missed': plans were arriving, then stopped for 2h+."""
    import os

    from src import analyst_plan

    now = time.time() if now is None else now
    path = path or analyst_plan.get_ledger().path
    if not os.path.exists(path):
        return True, "no analyst plans yet (scheduled sessions not started)"
    con = sqlite3.connect(path, timeout=10)
    try:
        last = con.execute("SELECT MAX(submitted_at) FROM plans").fetchone()[0]
    finally:
        con.close()
    if last is None:
        return True, "no analyst plans yet"
    age_h = (now - float(last)) / 3600.0
    if 2.0 <= age_h <= 48.0:
        return False, f"hourly plan missed: last plan {age_h:.1f}h ago"
    if age_h > 48.0:
        return True, f"analyst idle {age_h:.0f}h (treated as stopped, not missed)"
    return True, f"last plan {age_h * 60:.0f}m ago"
