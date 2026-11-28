"""Judgement scoring for the hourly analyst — Phase 3 (2026-11-28).

Plan: ``docs/ANALYST_DESK_PLAN_2026_11_28.md``. A trader is more than a list
of setups: they decide how much to put on each idea, and they hold a view of
where the market goes next. Neither was measured. This module scores both,
and fixes how every result is judged.

* **Size.** Each setup may carry ``size`` in ``SIZES``. ``0`` means "the desk
  would pass": the setup is still walked, so the passed ideas are measured
  beside the taken ones on the same days. Three populations, never pooled:
  ``active`` (size > 0, weighted by size), ``passed`` (size 0) and
  ``unsized`` (a prompt that did not state one).
* **Forecast.** A plan may carry a BTC forecast for 4h and 12h: ``up``,
  ``down`` or ``range`` against a fixed band (``FORECAST_BANDS``), with a
  probability and an invalidation price. It is scored against BTC's close at
  the horizon, by multi-class Brier against the base rate of the outcomes
  observed. The bands are stamped on each plan, so changing them starts a new
  population.
* **Day-clustered confidence.** Alts move with BTC, so twenty same-day
  setups are close to one bet. Every arm's per-setup average gets a 95%
  interval from resampling whole UTC days, not setups.
* **Stop diagnostics.** On the analyst arm: the share of stops hit on a bar
  that also touched the target (the walk books the stop on such a bar, which
  is the conservative guess); the share whose target was reached later inside
  the hold window (stop too tight, or direction right but early); and the
  result by entry distance in ATR.

Nothing here reaches a subscriber, signal or order. Pure functions over the
analyst's own ledger, plus BTC's stored 5m bars for the forecast.
"""
from __future__ import annotations

import json
import random
import sqlite3
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

SIZES = (0.0, 0.5, 1.0, 1.5, 2.0)
#: horizon name -> (seconds, band in % that separates up / down from range)
FORECAST_BANDS: Dict[str, Tuple[float, float]] = {"btc_4h": (4 * 3600.0, 0.7),
                                                  "btc_12h": (12 * 3600.0, 1.2)}
FORECAST_DIRS = ("up", "down", "range")
P_RANGE = (0.34, 0.95)
BOOT_N = 2000
BOOT_SEED = 7
MIN_DAYS_FOR_CI = 5
DIST_BUCKETS = ((0.0, 0.25), (0.25, 0.6), (0.6, 1.2), (1.2, float("inf")))


# ── forecast: parse, stamp, score ───────────────────────────────────────────


def parse_forecast(raw: Any) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """``(forecast, dropped)``. A bad forecast is named and dropped; it never
    rejects the plan's setups."""
    if raw is None:
        return None, []
    if not isinstance(raw, dict):
        return None, ["forecast must be an object with btc_4h and/or btc_12h"]
    out: Dict[str, Any] = {}
    dropped: List[str] = []
    for h, v in raw.items():
        if h not in FORECAST_BANDS:
            dropped.append(f"{h}: horizon must be one of {sorted(FORECAST_BANDS)}")
            continue
        if not isinstance(v, dict) or v.get("dir") not in FORECAST_DIRS:
            dropped.append(f"{h}: dir must be one of {FORECAST_DIRS}")
            continue
        p = v.get("p")
        if (not isinstance(p, (int, float)) or isinstance(p, bool)
                or not P_RANGE[0] <= float(p) <= P_RANGE[1]):
            dropped.append(f"{h}: p must be in {list(P_RANGE)}")
            continue
        inv = v.get("invalidation")
        if inv is not None and (not isinstance(inv, (int, float)) or isinstance(inv, bool)
                                or inv <= 0):
            dropped.append(f"{h}: invalidation must be a positive price")
            continue
        secs, band = FORECAST_BANDS[h]
        out[h] = {"dir": v["dir"], "p": float(p),
                  "invalidation": float(inv) if inv is not None else None,
                  "horizon_s": secs, "band_pct": band}
    return (out or None), dropped


def btc_last_price(engine: Any) -> Optional[float]:
    """BTC's newest print in the store (forming bar included), or None."""
    from src import analyst_snapshot as A

    raw = A._store_candles(engine, "BTCUSDT", closed_only=False)
    for tf in ("1m", "5m", "15m", "1h"):
        c = A._arr(raw.get(tf), "close")
        if c is not None and len(c):
            return float(c[-1])
    return None


def outcome(ret_pct: float, band: float) -> str:
    return "up" if ret_pct > band else "down" if ret_pct < -band else "range"


def score_forecasts(con: sqlite3.Connection, btc_cd: Any, now: float,
                    limit: int = 200) -> int:
    """Score every plan forecast whose horizon has passed. Idempotent.

    The price at the horizon is the close of the last CLOSED 5m bar ending at
    or before it. A horizon whose bar the store does not hold (gap, or rolled
    off) is scored ``insufficient`` with that reason, never guessed.
    """
    rows = [dict(r) for r in con.execute(
        "SELECT plan_id, submitted_at, forecast_json, btc_at_submit FROM plans "
        "WHERE forecast_json IS NOT NULL AND forecast_scored_json IS NULL "
        "ORDER BY submitted_at LIMIT ?", (int(limit),))]
    if not rows:
        return 0
    t = c = None
    if isinstance(btc_cd, dict) and btc_cd.get("open_time") is not None:
        t = np.asarray(btc_cd["open_time"], dtype=np.float64) / 1000.0
        c = np.asarray(btc_cd["close"], dtype=np.float64)
        if len(t) != len(c) or not np.all(np.diff(t) > 0):
            t = c = None
    n = 0
    for r in rows:
        fc = json.loads(r["forecast_json"])
        due = max(float(v["horizon_s"]) for v in fc.values())
        if now < r["submitted_at"] + due + 300.0:
            continue
        res: Dict[str, Any] = {}
        for h, v in fc.items():
            end = r["submitted_at"] + float(v["horizon_s"])
            if r.get("btc_at_submit") is None or t is None:
                res[h] = {"status": "insufficient", "reason": "no_btc_price"}
                continue
            i = int(np.searchsorted(t + 300.0, end, side="right")) - 1
            if i < 0 or end - (t[i] + 300.0) > 600.0:
                res[h] = {"status": "insufficient", "reason": "no_bar_at_horizon"}
                continue
            ret = (float(c[i]) / float(r["btc_at_submit"]) - 1.0) * 100.0
            res[h] = {"status": "scored", "ret_pct": round(ret, 4),
                      "outcome": outcome(ret, float(v["band_pct"])),
                      "dir": v["dir"], "p": v["p"]}
        con.execute("UPDATE plans SET forecast_scored_json=? WHERE plan_id=?",
                    (json.dumps(res), r["plan_id"]))
        n += 1
    return n


def forecast_summary(con: sqlite3.Connection) -> Dict[str, Any]:
    try:
        rows = [dict(r) for r in con.execute(
            "SELECT forecast_scored_json FROM plans WHERE forecast_scored_json IS NOT NULL")]
        pending = con.execute("SELECT COUNT(*) FROM plans WHERE forecast_json IS NOT NULL "
                              "AND forecast_scored_json IS NULL").fetchone()[0]
    except sqlite3.OperationalError:
        return {"n": 0, "reason": "ledger predates the forecast"}
    out: Dict[str, Any] = {"pending": int(pending)}
    for h in FORECAST_BANDS:
        sc = [json.loads(r["forecast_scored_json"]).get(h) for r in rows]
        sc = [x for x in sc if x and x.get("status") == "scored"]
        if not sc:
            out[h] = {"n": 0}
            continue
        obs = {d: sum(x["outcome"] == d for x in sc) / len(sc) for d in FORECAST_DIRS}

        def probs(x: Dict[str, Any]) -> Dict[str, float]:
            rest = (1.0 - x["p"]) / 2.0
            return {d: (x["p"] if d == x["dir"] else rest) for d in FORECAST_DIRS}

        brier = sum(sum((probs(x)[d] - (x["outcome"] == d)) ** 2 for d in FORECAST_DIRS)
                    for x in sc) / len(sc)
        base = sum(obs[d] * (1 - obs[d]) for d in FORECAST_DIRS)
        out[h] = {"n": len(sc), "hit_rate": round(sum(x["dir"] == x["outcome"]
                                                      for x in sc) / len(sc), 4),
                  "mean_p": round(sum(x["p"] for x in sc) / len(sc), 4),
                  "observed": {d: round(v, 4) for d, v in obs.items()},
                  "brier": round(brier, 4), "brier_of_base_rate": round(base, 4),
                  "band_pct": FORECAST_BANDS[h][1]}
    out["note"] = ("Each forecast: its direction gets p, the other two share 1-p. Scored "
                   "against BTC's close at the horizon vs the band. Beat the base rate or "
                   "the forecast carries no information.")
    return out


# ── day-clustered confidence ────────────────────────────────────────────────


def day_clustered_ci(pairs: Sequence[Tuple[Optional[str], float]]) -> Dict[str, Any]:
    """Mean per setup with a 95% interval from resampling whole days."""
    days: Dict[str, List[float]] = {}
    for d, v in pairs:
        if d is not None:
            days.setdefault(d, []).append(float(v))
    if len(days) < MIN_DAYS_FOR_CI:
        return {"n_days": len(days), "reason": f"fewer than {MIN_DAYS_FOR_CI} days"}
    sums = [sum(v) for v in days.values()]
    cnts = [len(v) for v in days.values()]
    rng = random.Random(BOOT_SEED)
    k = len(sums)
    stats = []
    for _ in range(BOOT_N):
        idx = [rng.randrange(k) for _ in range(k)]
        stats.append(sum(sums[i] for i in idx) / sum(cnts[i] for i in idx))
    stats.sort()
    return {"n_days": k, "n": sum(cnts),
            "mean_per_setup_pct": round(sum(sums) / sum(cnts), 4),
            "ci95_pct": [round(stats[int(0.025 * BOOT_N)], 4),
                         round(stats[int(0.975 * BOOT_N) - 1], 4)],
            "method": f"{BOOT_N} resamples of whole UTC days (seed {BOOT_SEED})"}


# ── size ────────────────────────────────────────────────────────────────────


def size_split(pairs: Sequence[Tuple[Optional[float], Optional[str], float]]
               ) -> Dict[str, Any]:
    """``pairs``: (size, day, realized %). Three populations, never pooled."""
    act = [(s, d, v) for s, d, v in pairs if s is not None and s > 0]
    pas = [(d, v) for s, d, v in pairs if s is not None and s == 0]
    uns = [(d, v) for s, d, v in pairs if s is None]
    out: Dict[str, Any] = {}
    if act:
        w = sum(s for s, _, _ in act)
        out["active"] = {"n": len(act), "units": round(w, 2),
                         "size_weighted_avg_pct": round(sum(s * v for s, _, v in act) / w, 4),
                         "unweighted_avg_pct": round(sum(v for _, _, v in act) / len(act), 4),
                         "day_clustered": day_clustered_ci([(d, v) for _, d, v in act])}
    else:
        out["active"] = {"n": 0}
    for name, rows in (("passed", pas), ("unsized", uns)):
        out[name] = ({"n": len(rows), "avg_pct": round(sum(v for _, v in rows) / len(rows), 4),
                      "day_clustered": day_clustered_ci(rows)} if rows else {"n": 0})
    out["note"] = ("passed = setups the analyst sized 0 (the desk would not take them), "
                   "walked anyway. active beating passed on the same days is what "
                   "selectivity adding value looks like. unsized = prompts before size.")
    return out


# ── stop diagnostics ────────────────────────────────────────────────────────


def stop_diagnostics(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """On the analyst arm's filled, resolved rows."""
    filled = [r for r in rows if r["status"] == "resolved" and not r.get("unfilled")
              and r.get("exit_reason") in ("target", "stop", "horizon")]
    stops = [r for r in filled if r["exit_reason"] == "stop"]
    amb = [r for r in stops if r.get("stop_ambiguous") is not None]
    later = [r for r in stops if r.get("target_after_stop") is not None]
    out: Dict[str, Any] = {
        "filled": len(filled), "stops": len(stops),
        "stop_share": round(len(stops) / len(filled), 4) if filled else None,
        "ambiguous_bar": {"known": len(amb),
                          "share": (round(sum(r["stop_ambiguous"] for r in amb) / len(amb), 4)
                                    if amb else None)},
        "target_after_stop": {"known": len(later),
                              "share": (round(sum(r["target_after_stop"] for r in later)
                                              / len(later), 4) if later else None)},
    }
    buckets = []
    for lo, hi in DIST_BUCKETS:
        sel = [r for r in filled if r.get("s_entry_dist_atr") is not None
               and lo <= float(r["s_entry_dist_atr"]) < hi]
        buckets.append({"entry_dist_atr": [lo, None if hi == float("inf") else hi],
                        "n": len(sel),
                        "stop_share": (round(sum(r["exit_reason"] == "stop" for r in sel)
                                             / len(sel), 4) if sel else None),
                        "avg_net_pct": (round(sum(float(r["net_pct"]) for r in sel)
                                              / len(sel), 4) if sel else None)})
    out["by_entry_distance"] = buckets
    out["note"] = ("ambiguous_bar: the stop bar also touched the target; the walk books "
                   "the stop. target_after_stop: the target was reached later inside the "
                   "12h hold (stop too tight, or right but early). Both are recorded from "
                   "2026-11-28 on; 'known' counts the rows that carry them.")
    return out
