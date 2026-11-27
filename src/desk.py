"""The Desk — what the Lumin 2.0 app's Desk and Setups tabs read (2026-11-26).

The hourly AI analyst submits a plan (a ``bias``, ``notes`` and up to five
setups) into ``analyst_plan``'s ledger, and ``analyst_walk`` walks every
accepted setup forward on real bars. Both live in the ENGINE container next to
the candle stores, so in isolated mode the API process cannot build this
itself: the snapshot writer publishes it to Redis every 60s
(``snapshot:desk``), and ``GET /api/desk`` serves that one key. No Firestore
read anywhere on this path.

Display only. Nothing here places, sizes or scores anything, and nothing on
the money path reads it. Owner, 2026-11-26: engine signal paths stay the
signal source; the analyst is the Desk layer plus its own setups, labelled
as forward-measured until it has earned promotion on the record.

Three things the payload refuses to do, each a defect this repo has paid for:

* **An old plan is never "this hour's" brief.** ``brief.freshness`` is
  ``current`` / ``stale`` / ``none`` off the plan's own submit time, so the
  app can say "no new brief for 3h" instead of presenting a stale read.
* **Unknown is not a value.** Market context that could not be read says so
  (``readable: false`` + reason); macro is ``unknown``, never "no events".
* **Analyst outcomes are a dark walk, never real fills.** ``record.basis``
  says so, and nothing here is pooled with the engine's track record.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from src.utils import get_logger

log = get_logger("desk")

#: Bumped only when a field is REDEFINED. Additive fields do not bump it.
DESK_SCHEMA = 1

#: The analyst runs hourly at :35. Two missed runs and the brief is stale.
BRIEF_FRESH_SEC = 2 * 3600
#: Plans shown in the Desk log (every plan, stand-aside included).
PLAN_LOG_LIMIT = 24
#: Setups published. The feed is newest-first; older ones age out of the app.
SETUP_LIMIT = 200

#: One writer for the names the app prints. The app renders these and falls
#: back to the raw key, so a new archetype shows under its own name instead of
#: vanishing.
ARCHETYPE_LABELS: Dict[str, str] = {
    "level_reclaim": "Level Reclaim",
    "breakout_retest": "Breakout Retest",
    "range_fade": "Range Fade",
    "trend_pullback": "Trend Pullback",
    "sweep_reversal": "Sweep & Reclaim",
}
BIAS_LABELS: Dict[str, str] = {
    "risk_on": "Risk-on",
    "risk_off": "Risk-off",
    "neutral": "Balanced",
    "stand_aside": "Stand aside",
}
#: Feed state → the sentence family the app shows. ``not_filled`` is its own
#: state: its PnL is the market's, never the setup's fill.
STATE_LABELS: Dict[str, str] = {
    "not_walked": "Queued",
    "waiting_data": "Waiting for data",
    "pending": "Pending limit",
    "active": "Active",
    "tp_hit": "Target hit",
    "sl_hit": "Stopped out",
    "time_exit": "Time exit",
    "not_filled": "Never filled",
    "insufficient": "Not measurable",
}

#: Feed-row keys the app reads. Everything else stays in ops.
_SETUP_KEYS = (
    "setup_id", "plan_id", "submitted_at", "expires_at", "expired", "symbol",
    "side", "archetype", "bias", "price_at_submit", "entries", "stop", "targets",
    "stop_atr", "tp1_pct", "rr_tp1", "invalidation", "scenario", "p_target",
    "state", "analyst",
)


def _freshness(submitted_at: Optional[float], now: float) -> Dict[str, Any]:
    if submitted_at is None:
        return {"state": "none", "age_sec": None}
    age = max(0.0, now - float(submitted_at))
    return {"state": "current" if age <= BRIEF_FRESH_SEC else "stale",
            "age_sec": round(age, 1), "fresh_within_sec": BRIEF_FRESH_SEC}


def _plans(path: str) -> Dict[str, Any]:
    from src import analyst_plan

    rec = analyst_plan.Ledger(path).recent(limit=PLAN_LOG_LIMIT)
    if not rec.get("readable"):
        return {"readable": False, "reason": rec.get("reason"), "plans": []}
    out: List[Dict[str, Any]] = []
    for p in rec.get("plans") or []:
        accepted = [s for s in p.get("setups") or [] if s.get("status") == "accepted"]
        out.append({
            "plan_id": p["plan_id"], "submitted_at": p["submitted_at"],
            "bias": p.get("bias"), "notes": p.get("notes") or "",
            "n_setups": p.get("n_setups") or 0, "n_accepted": len(accepted),
            "accepted": [{"symbol": s.get("symbol"), "side": s.get("side"),
                          "archetype": s.get("archetype")} for s in accepted],
            "macro": p.get("macro") or "unknown",
        })
    return {"readable": True, "plans": out}


def _market(engine: Any, now: float) -> Dict[str, Any]:
    from src import analyst_snapshot

    try:
        ctx = analyst_snapshot.market_context(engine, now=now)
    except Exception as exc:  # noqa: BLE001 — the brief must still render
        from src import fail_open
        fail_open.record("desk.market_context", exc)
        return {"readable": False, "reason": f"{type(exc).__name__}"}
    btc = ctx.get("btc") or {}
    return {
        "readable": btc.get("price") is not None,
        "reason": None if btc.get("price") is not None else "no_btc_1h",
        "btc_price": btc.get("price"),
        "btc_state": btc.get("state_b"),
        "btc_state_status": btc.get("state_status"),
        "btc_per_tf": btc.get("per_tf") or {},
        "btc_change_pct": btc.get("change_pct") or {},
        "btc_atr_1d_pct": btc.get("atr_1d_pct"),
        "breadth": ctx.get("breadth") or {"readable": False, "reason": "absent"},
        "session_utc": ctx.get("session_utc"),
        # Never "no events": no macro feed is wired.
        "macro": {"readable": False, "state": "unknown"},
    }


def _record(path: str, now: float) -> Dict[str, Any]:
    from src import analyst_walk

    s = analyst_walk.summary(path=path, now=now)
    if not s.get("readable"):
        return {"readable": False, "reason": s.get("reason")}
    arms = s.get("by_arm") or {}
    return {
        "readable": True,
        "basis": "forward_walk",
        # Since walk v2 (2026-11-27) the analyst block is REALIZED per setup
        # posted: a limit the market never reached earned 0.00%. Before, it
        # scored unfilled limits at the market outcome — a population selected
        # for price running away — and read +0.42% while filled setups lost.
        "basis_note": ("Measured forward on real prices, net of a 0.07% round trip. "
                       "A limit that never filled counts as 0.00%. No order was placed: "
                       "these are not fills."),
        "analyst": arms.get("analyst") or {"n": 0},
        "market": arms.get("market") or {"n": 0},
        "split": s.get("analyst_split") or {},
        "calibration": s.get("calibration") or {"n": 0},
    }


def build(engine: Any, *, now: Optional[float] = None,
          path: Optional[str] = None) -> Dict[str, Any]:
    """The whole Desk payload. Never raises: each block reports its own state."""
    from src import analyst_plan, analyst_walk

    now = time.time() if now is None else now
    path = path or analyst_plan.get_ledger().path
    plans = _plans(path)
    latest = plans["plans"][0] if plans["plans"] else None

    feed = analyst_walk.feed(limit=SETUP_LIMIT, path=path, now=now)
    setups = [{k: r.get(k) for k in _SETUP_KEYS} for r in feed.get("rows") or []]

    return {
        "schema": DESK_SCHEMA,
        "generated_at": now,
        "ledger": "ok" if plans["readable"] else (plans.get("reason") or "unreadable"),
        "brief": {
            "plan": latest,
            "freshness": _freshness(latest["submitted_at"] if latest else None, now),
            "market": _market(engine, now),
        },
        "plans": plans["plans"],
        "setups": setups,
        "counts": feed.get("counts") or {},
        "n_accepted_total": feed.get("n_accepted_total", len(setups)),
        "record": _record(path, now) if plans["readable"] else
        {"readable": False, "reason": plans.get("reason")},
        "labels": {"archetype": ARCHETYPE_LABELS, "bias": BIAS_LABELS,
                   "state": STATE_LABELS},
    }


def setup(payload: Optional[Dict[str, Any]], setup_id: str) -> Optional[Dict[str, Any]]:
    """One setup out of a published payload, or None when it is not in it."""
    for s in (payload or {}).get("setups") or []:
        if s.get("setup_id") == setup_id:
            return s
    return None
