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
    market = _score(long, m_entry, _exit_walk(bars, 0, long, m_entry, stop, target, now))
    market.update(entry=m_entry, entry_at=float(bars["t"][0]), filled_frac=1.0, unfilled=0)
    out["market"] = market

    def limit_arm(legs: List[Dict[str, Any]], stop: float = stop,
                  target: float = target) -> Dict[str, Any]:
        fills = [(leg, _limit_fill(bars, long, float(leg["price"]), expires)) for leg in legs]
        got = [(leg, j) for leg, j in fills if j is not None]
        if not got:
            window_closed = float(bars["t"][-1]) + STEP_S >= expires
            if not window_closed:
                return {"status": "open", "reason": "awaiting_fill"}
            # Scored at market — with THIS arm's own stop and target.
            r = _score(long, m_entry, _exit_walk(bars, 0, long, m_entry, stop, target, now))
            r.update(entry=m_entry, entry_at=float(bars["t"][0]),
                     unfilled=1, filled_frac=0.0, reason="scored_at_market")
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


def summary(path: Optional[str] = None) -> Dict[str, Any]:
    """What ``read.analyst_outcomes`` returns. Per arm, never pooled."""
    import os

    from src import analyst_plan

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
                                                        if r["status"] == "resolved")}
    return {"readable": True, "by_arm": by_arm, "arms_not_built": list(ARMS_NOT_BUILT),
            "calibration": _calibration(path),
            "note": ("Net of a 0.07% round trip. Unfilled limits are scored at the market "
                     "outcome. Stop first on an ambiguous 5m bar. Read n before any average.")}


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
