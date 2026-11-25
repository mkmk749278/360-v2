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

Measurement flag: ``ANALYST_WALK_ENABLED`` (default ON — no vendor, no
Firestore; local candles and a local SQLite file only).
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
ARMS = ("analyst", "tranche", "market", "fixed_rule", "none")
#: Arms named by the spec and deliberately not built in this module yet.
ARMS_NOT_BUILT = ("existing_signals",)

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
               stop: float, target: float, now: float, *,
               target_on_fill_bar: bool = True) -> Dict[str, Any]:
    """Walk from bar ``start`` (the fill bar) to stop / first target / horizon.

    ``target_on_fill_bar=False`` for a limit fill: the bar that reached the
    limit may have touched the target BEFORE the fill, and OHLC cannot say, so
    on that bar only the stop counts.
    """
    t0 = float(bars["t"][start])
    mfe = mae = 0.0
    for j in range(start, len(bars["t"])):
        hi, lo = float(bars["high"][j]), float(bars["low"][j])
        fav = (hi - entry) if long else (entry - lo)
        adv = (entry - lo) if long else (hi - entry)
        mfe, mae = max(mfe, fav / entry * 100), max(mae, adv / entry * 100)
        hit_stop = lo <= stop if long else hi >= stop
        hit_tgt = (hi >= target if long else lo <= target) and (
            target_on_fill_bar or j != start)
        if hit_stop:  # stop first on an ambiguous bar
            return {"status": "resolved", "exit": stop, "exit_at": float(bars["t"][j]),
                    "exit_reason": "stop", "mfe": mfe, "mae": mae}
        if hit_tgt:
            return {"status": "resolved", "exit": target, "exit_at": float(bars["t"][j]),
                    "exit_reason": "target", "mfe": mfe, "mae": mae}
        if float(bars["t"][j]) + STEP_S - t0 >= HOLD_HORIZON_S:
            return {"status": "resolved", "exit": float(bars["close"][j]),
                    "exit_at": float(bars["t"][j]) + STEP_S,
                    "exit_reason": "horizon", "mfe": mfe, "mae": mae}
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


def _score(long: bool, entry: float, ex: Dict[str, Any]) -> Dict[str, Any]:
    out = {"status": ex["status"], "mfe_pct": round(ex["mfe"], 4), "mae_pct": round(ex["mae"], 4)}
    if ex["status"] == "resolved":
        g = ((ex["exit"] - entry) if long else (entry - ex["exit"])) / entry * 100.0
        out.update(exit=ex["exit"], exit_at=ex["exit_at"], exit_reason=ex["exit_reason"],
                   gross_pct=round(g, 4), net_pct=round(g - ROUND_TRIP_PCT, 4))
    return out


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
        for arm in ("analyst", "tranche", "market", "fixed_rule"):
            out[arm] = {"status": "insufficient" if gone else "open", "reason": why}
        return out

    m_entry = float(bars["open"][0])
    m_at = float(bars["t"][0])

    def at_market(stop: float, target: float, **extra: Any) -> Dict[str, Any]:
        why = market_geometry(long, m_entry, stop, target)
        if why:
            return _no_valid_trade(m_entry, m_at, why, **extra)
        r = _score(long, m_entry, _exit_walk(bars, 0, long, m_entry, stop, target, now))
        r.update(entry=m_entry, entry_at=m_at, **extra)
        return r

    out["market"] = at_market(stop, target, filled_frac=1.0, unfilled=0)

    def limit_arm(legs: List[Dict[str, Any]], stop: float = stop,
                  target: float = target) -> Dict[str, Any]:
        fills = [(leg, _limit_fill(bars, long, float(leg["price"]), expires)) for leg in legs]
        got = [(leg, j) for leg, j in fills if j is not None]
        if not got:
            window_closed = float(bars["t"][-1]) + STEP_S >= expires
            if not window_closed:
                return {"status": "open", "reason": "awaiting_fill"}
            # Scored at market — with THIS arm's own stop and target.
            r = at_market(stop, target, unfilled=1, filled_frac=0.0)
            r.setdefault("reason", "scored_at_market")
            return r
        w = sum(float(leg["weight"]) for leg, _ in got)
        entry = sum(float(leg["price"]) * float(leg["weight"]) for leg, _ in got) / w
        start = min(j for _, j in got)
        r = _score(long, entry, _exit_walk(bars, start, long, entry, stop, target, now,
                                           target_on_fill_bar=False))
        r.update(entry=entry, entry_at=float(bars["t"][start]), filled_frac=round(w, 4),
                 unfilled=0)
        return r

    first = dict(entries[0])
    first["weight"] = 1.0
    out["analyst"] = limit_arm([first])
    out["tranche"] = limit_arm(entries)

    menu_raw = setup.get("menu_json")
    if not menu_raw:
        out["fixed_rule"] = {"status": "insufficient", "reason": "no_menu_stamped"}
    else:
        lv, why_not = fixed_rule_levels(json.loads(menu_raw), float(setup.get("price_at_submit")
                                                                    or 0.0),
                                        float(setup.get("atr_1h") or 0.0), setup["side"])
        if lv is None:
            out["fixed_rule"] = {"status": "resolved", "gross_pct": 0.0, "net_pct": 0.0,
                                 "exit_reason": "no_rule_setup", "reason": why_not}
        else:
            out["fixed_rule"] = limit_arm([{"price": lv["entry"], "weight": 1.0}],
                                          stop=lv["stop"], target=lv["target"])
    return out


# ── ledger I/O ────────────────────────────────────────────────────────────


def _connect(path: str) -> sqlite3.Connection:
    con = sqlite3.connect(path, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute(_SCHEMA)
    return con


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


def step(engine: Any, *, now: Optional[float] = None, path: Optional[str] = None,
         max_setups: int = 200) -> Dict[str, int]:
    """Advance every accepted setup that is still owed a verdict on any arm."""
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
        setups = [dict(r) for r in con.execute(
            "SELECT s.* FROM setups s WHERE s.status='accepted' AND ("
            " SELECT COUNT(*) FROM walks w WHERE w.setup_id=s.setup_id"
            " AND w.status IN ('resolved','insufficient')) < ? "
            "ORDER BY s.submitted_at LIMIT ?", (len(ARMS), int(max_setups)))]
        store = getattr(engine, "data_store", None)
        buckets = getattr(store, "candles", None) or {}
        for s in setups:
            counts["setups"] += 1
            arms = walk_setup(s, (buckets.get(s["symbol"]) or {}).get(TF), now)
            with con:
                for arm, r in arms.items():
                    con.execute(
                        "INSERT OR REPLACE INTO walks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (s["setup_id"], arm, r["status"], r.get("reason"), r.get("unfilled"),
                         r.get("filled_frac"), r.get("entry"), r.get("entry_at"), r.get("exit"),
                         r.get("exit_at"), r.get("exit_reason"), r.get("gross_pct"),
                         r.get("net_pct"), r.get("mfe_pct"), r.get("mae_pct"), now))
            counts[arms["tranche"]["status"]] = counts.get(arms["tranche"]["status"], 0) + 1
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
        rows = [dict(r) for r in con.execute(
            "SELECT s.p_target, w.exit_reason, w.unfilled FROM setups s JOIN walks w "
            "ON w.setup_id=s.setup_id AND w.arm='analyst' "
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
            "brier_of_base_rate": round(rate * (1 - rate), 4)}


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
                      "market_net_pct": (r.get("market") or {}).get("net_pct")})
        if len(out) >= n:
            break
    return out


def summary(path: Optional[str] = None, now: Optional[float] = None) -> Dict[str, Any]:
    """What ``read.analyst_outcomes`` returns. Per arm, never pooled."""
    import os

    from src import analyst_plan

    now = time.time() if now is None else now
    path = path or analyst_plan.get_ledger().path
    if not os.path.exists(path):
        return {"readable": False, "reason": "no_ledger_yet"}
    con = _connect(path)
    try:
        rows = [dict(r) for r in con.execute("SELECT * FROM walks")]
    finally:
        con.close()
    by_arm: Dict[str, Any] = {}
    for arm in ARMS:
        mine = [r for r in rows if r["arm"] == arm]
        res = [r["net_pct"] for r in mine if r["status"] == "resolved" and r["net_pct"] is not None]
        by_arm[arm] = {**_arm_summary(res),
                       "open": sum(r["status"] == "open" for r in mine),
                       "insufficient": sum(r["status"] == "insufficient" for r in mine),
                       "unfilled_scored_at_market": sum(bool(r.get("unfilled")) for r in mine
                                                        if r["status"] == "resolved"),
                       "no_valid_trade": sum(r.get("exit_reason") == "no_valid_trade"
                                             for r in mine)}
    fd = feed(limit=FEED_MAX, path=path, now=now)
    frows = fd.get("rows") or []
    return {"readable": True, "by_arm": by_arm, "arms_not_built": list(ARMS_NOT_BUILT),
            "analyst_split": _split([r for r in rows if r["arm"] == "analyst"]),
            "calibration": _calibration(path),
            "active_book": book(frows, now),
            "recent_closed": recent_closed(frows),
            "note": ("Net of a 0.07% round trip. Unfilled limits are scored at the market "
                     "outcome; a market entry already past its own target or stop is "
                     "no_valid_trade at 0.00%. Stop first on an ambiguous 5m bar. Read "
                     "analyst_split before the analyst arm's headline: it pools fills with "
                     "market scores. Read n before any average.")}


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
