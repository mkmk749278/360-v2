"""Per-pair market context for the app's chart screen (Charts redesign, part 3).

Owner, 2026-09-25: *"some users take trades manually and don't know how to
read the market structure for that pair … give a full analysis of that pair
at that situation so the user gets some idea."* The engine already holds that
read for every pair it scans — the multi-TF Level Book, the volume profile,
the 4h structure leg — and until now only its own evaluators could see it.

This module turns those stores into one small, **descriptive** summary per
pair and a checklist of what on the chart sits with a LONG and what sits with
a SHORT. Three rules, each one this repo has paid for elsewhere:

* **No verdict, no score.** The checklist lists facts on both sides and never
  weighs them. The regime label once *agreed with* eight of ten losing longs
  (BEATUSDT, 2026-08-07); a "bullish 82%" built on parts that do not predict
  would be a prediction wearing an analysis's clothes.
* **Only what the engine measured.** A pair the scanner does not track has
  no levels here, and the app says so rather than fetching candles on the
  engine's IP (the rate limit that has cost this box an IP ban before).
* **The age travels with the data.** Every pair carries when its levels were
  refreshed and the price it was read against; a stale read says so.

Built in the ENGINE container (the stores live there) by the snapshot writer,
published to Redis, read by the API container — the same route every other
engine-side block takes in isolated mode.
"""

from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Optional

SCHEMA = 1

#: Levels shown each side of price. More than three on a phone is a wall.
MAX_LEVELS_PER_SIDE = 3

#: Levels further than this from price are not "nearby" for a manual trade.
MAX_LEVEL_DISTANCE_PCT = 12.0

#: A level within this distance is called out in the checklist.
NEAR_LEVEL_PCT = 1.5


def _f(v: Any) -> Optional[float]:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _last_close(data_store: Any, symbol: str) -> Optional[float]:
    """Newest closed 5m (else 15m / 1h) close from the engine's candle store."""
    getter = getattr(data_store, "get_candles", None)
    if not callable(getter):
        return None
    for tf in ("5m", "15m", "1h"):
        try:
            c = getter(symbol, tf)
        except Exception:
            continue
        if c is None:
            continue
        close = c.get("close") if isinstance(c, dict) else None
        if close is None or len(close) == 0:
            continue
        v = _f(close[-1])
        if v and v > 0:
            return v
    return None


def _level_row(lv: Any, price: float) -> Dict[str, Any]:
    p = float(lv.price)
    return {
        "price": p,
        "dist_pct": round((p - price) / price * 100.0, 3),
        "touches": int(getattr(lv, "touches", 1) or 1),
        "timeframes": list(getattr(lv, "source_tfs", None) or [getattr(lv, "source_tf", "")]),
        "round_number": bool(getattr(lv, "is_round_number", False)),
    }


def build_one(scanner: Any, data_store: Any, symbol: str, *, now: Optional[float] = None) -> Optional[Dict[str, Any]]:
    """Context for one pair, or None when the engine holds nothing for it."""
    now = now or time.time()
    price = _last_close(data_store, symbol)
    if price is None:
        return None
    out: Dict[str, Any] = {"symbol": symbol, "price": price, "read_at": now}

    book = getattr(scanner, "level_book", None)
    supports: List[Dict[str, Any]] = []
    resistances: List[Dict[str, Any]] = []
    if book is not None:
        try:
            levels = book.get_levels(symbol)
        except Exception:
            levels = []
        for lv in levels:
            p = _f(getattr(lv, "price", None))
            if p is None or p <= 0:
                continue
            dist = (p - price) / price * 100.0
            if abs(dist) > MAX_LEVEL_DISTANCE_PCT:
                continue
            (supports if p < price else resistances).append(_level_row(lv, price))
        supports.sort(key=lambda r: -r["price"])       # nearest below first
        resistances.sort(key=lambda r: r["price"])     # nearest above first
        try:
            out["levels_refreshed_at"] = book.last_refresh_ts(symbol)
        except Exception:
            out["levels_refreshed_at"] = None
    out["supports"] = supports[:MAX_LEVELS_PER_SIDE]
    out["resistances"] = resistances[:MAX_LEVELS_PER_SIDE]

    vp_store = getattr(scanner, "volume_profile_store", None)
    vp = None
    if vp_store is not None:
        try:
            vp = vp_store.get(symbol)
        except Exception:
            vp = None
    if vp is not None and _f(getattr(vp, "poc", None)):
        vah, val, poc = float(vp.vah), float(vp.val), float(vp.poc)
        position = "in_value" if val <= price <= vah else ("above_value" if price > vah else "below_value")
        out["volume_profile"] = {
            "poc": poc, "vah": vah, "val": val, "position": position,
            "lookback": "1h × 200 bars (~8 days)",
            "refreshed_at": _f(getattr(vp, "last_update_ts", None)),
        }
    else:
        out["volume_profile"] = None

    tracker = getattr(scanner, "structure_tracker", None)
    st = None
    if tracker is not None:
        try:
            st = tracker.get_state(symbol, tf="4h")
        except Exception:
            st = None
    if st is not None:
        out["structure_4h"] = {
            "state": str(st.state),
            "confidence": round(float(st.confidence or 0.0), 2),
            "last_hh": _f(st.last_HH), "last_hl": _f(st.last_HL),
            "last_lh": _f(st.last_LH), "last_ll": _f(st.last_LL),
            "refreshed_at": _f(getattr(st, "last_update_ts", None)),
        }
    else:
        out["structure_4h"] = None
    return out


def build_snapshot(engine: Any, *, now: Optional[float] = None) -> Dict[str, Any]:
    """Every scanned pair's context, for the snapshot writer to publish."""
    now = now or time.time()
    scanner = getattr(engine, "_scanner", None)
    data_store = getattr(engine, "data_store", None) or getattr(scanner, "data_store", None)
    pair_mgr = getattr(engine, "pair_mgr", None)
    symbols = list(getattr(pair_mgr, "pairs", {}) or {})
    promoted = getattr(scanner, "_mover_promoted_pairs", None)
    if promoted:
        symbols += [s for s in promoted if s not in symbols]
    pairs: Dict[str, Any] = {}
    if scanner is not None and data_store is not None:
        for sym in symbols:
            try:
                ctx = build_one(scanner, data_store, sym, now=now)
            except Exception:
                ctx = None
            if ctx is not None:
                pairs[sym] = ctx
    return {"schema": SCHEMA, "generated_at": now, "pairs": pairs}


# ---------------------------------------------------------------------------
# The checklist — facts on each side, never weighed.
# ---------------------------------------------------------------------------

def _pct(x: float) -> str:
    return f"{abs(x):.1f}%"


def checklist(ctx: Dict[str, Any]) -> Dict[str, List[str]]:
    """What on the chart sits with a LONG and what with a SHORT.

    Deliberately symmetric: every rule that can add a LONG line has its
    mirror for SHORT, so the list cannot lean by construction. Nothing is
    scored and nothing is concluded; the reader weighs it.
    """
    long_: List[str] = []
    short_: List[str] = []
    neutral: List[str] = []

    st = ctx.get("structure_4h") or {}
    state = st.get("state")
    if state == "BULL_LEG":
        long_.append("4h structure is making higher highs and higher lows")
    elif state == "BEAR_LEG":
        short_.append("4h structure is making lower highs and lower lows")
    elif state == "RANGE":
        neutral.append("4h structure is ranging — no clear leg")

    sup = (ctx.get("supports") or [None])[0]
    res = (ctx.get("resistances") or [None])[0]
    if sup and abs(sup["dist_pct"]) <= NEAR_LEVEL_PCT:
        long_.append(f"Support {_pct(sup['dist_pct'])} below ({sup['touches']} touches)")
    if res and abs(res["dist_pct"]) <= NEAR_LEVEL_PCT:
        short_.append(f"Resistance {_pct(res['dist_pct'])} above ({res['touches']} touches)")
    if res and abs(res["dist_pct"]) > NEAR_LEVEL_PCT:
        long_.append(f"Room to the next resistance: {_pct(res['dist_pct'])}")
    if sup and abs(sup["dist_pct"]) > NEAR_LEVEL_PCT:
        short_.append(f"Room to the next support: {_pct(sup['dist_pct'])}")
    if not sup:
        neutral.append("No measured support within 12% below")
    if not res:
        neutral.append("No measured resistance within 12% above")

    vp = ctx.get("volume_profile") or {}
    pos = vp.get("position")
    if pos == "above_value":
        long_.append("Price is above the week's value area (accepted higher)")
    elif pos == "below_value":
        short_.append("Price is below the week's value area (accepted lower)")
    elif pos == "in_value":
        neutral.append("Price is inside the week's value area — the busy zone")

    return {"long": long_, "short": short_, "neutral": neutral}
