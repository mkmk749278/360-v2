"""The hourly AI analyst's read model: market context, pair snapshot, level menu.

Owner, 2026-11-19: move signal generation to the disciplined-analyst process
(context first, levels marked in advance, pre-entry setups) with Claude doing
the analysis on a schedule and the engine executing deterministically. Spec:
``docs/AI_ANALYST_SPEC_2026_11_19.md``. This module is step 1 of that spec —
**the read side only.** Nothing here plans, places, sizes or gates anything.

Three rules carried from the research (both reports agree):

* **The analyst never reads raw candles.** LLMs misread numeric series (nof1
  Alpha Arena, the 2026 ACM survey), so everything here is pre-computed and
  every number carries the clock it was measured on.
* **Levels are chosen by id from a menu the engine builds.** A plan can then
  only reference a price the engine produced, and the validator (step 3) can
  check every id against the current menu instead of trusting a number a model
  typed. Ids are ``kind@price`` — stable for as long as the level exists and
  readable by a human checking a plan.
* **Unknown is never a value.** A field that could not be computed carries
  ``None`` and a reason. The macro calendar, in particular, is not wired
  (``macro_blackout`` is fed an empty list), so this module says
  ``not_available`` rather than "no events" — those are opposite facts and only
  one of them is safe to trade through.

Cost: pure assembly over state the engine already holds (data store candles,
``LevelBook``, both ``VolumeProfileStore``s, the unlock-short ledger). No new
network or Firestore read on any path. The watchlist walks the pair universe
once per call, a few hundred numpy reductions — called hourly, not per tick.

The 0–100 level score is a **v1 config, not evidence**: its weights follow the
Gemini report's suggestion and were invented there. Its parts are published
beside the total so a later tuning pass can see what moved.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np

from src.btc_state import _atr, compute_btc_state

BTC = "BTCUSDT"

#: Interval lengths in milliseconds, for bar-freshness checks.
TF_MS: Dict[str, int] = {
    "1m": 60_000, "5m": 300_000, "15m": 900_000, "1h": 3_600_000,
    "4h": 14_400_000, "1d": 86_400_000, "1w": 604_800_000,
}

#: Timeframe weight in the level score (0–35). v1 config — see module docstring.
TF_POINTS: Dict[str, float] = {"1w": 35.0, "1d": 25.0, "4h": 15.0, "1h": 8.0}
#: Points for the non-LevelBook level kinds.
KIND_POINTS: Dict[str, float] = {
    "pwh": 35.0, "pwl": 35.0,          # prior week high / low
    "pdh": 25.0, "pdl": 25.0,          # prior day high / low
    "vp_macro_poc": 25.0, "vp_macro_vah": 20.0, "vp_macro_val": 20.0,
    "vp_poc": 15.0, "vp_vah": 12.0, "vp_val": 12.0,
}
ROUND_POINTS = 10.0
CONFLUENCE_POINTS_EACH = 8.0
CONFLUENCE_POINTS_CAP = 25.0
#: Two candidates are confluent within this many 1h ATRs of each other.
CONFLUENCE_ATR = 0.25

#: Watchlist: a pair qualifies when price is within this many 1h ATRs of a
#: level scoring at least this much.
WATCH_MAX_ATR = 1.5
WATCH_MIN_SCORE = 60.0

#: Unlock veto window, from both reports: pressure begins ~30d before a
#: team/investor cliff and settles ~14d after.
UNLOCK_PRE_DAYS = 30
UNLOCK_POST_DAYS = 14

#: A bar is "stale" once the store's newest closed bar is this many intervals
#: older than the bar that should have closed by now.
STALE_INTERVALS = 2


# ---------------------------------------------------------------------------
# Small pure helpers
# ---------------------------------------------------------------------------


def _arr(cd: Optional[dict], key: str) -> Optional[np.ndarray]:
    if not isinstance(cd, dict):
        return None
    v = cd.get(key)
    if v is None:
        return None
    a = np.asarray(v, dtype=np.float64)
    return a if len(a) else None


def bar_freshness(cd: Optional[dict], tf: str, now_ms: float) -> Dict[str, Any]:
    """How current the newest CLOSED bar is.

    The store appends only completed bars, so a healthy 1h bucket's newest bar
    opened between one and two hours ago. ``bars_behind`` counts the bars that
    should have closed since and have not arrived.
    """
    ot = _arr(cd, "open_time")
    step = TF_MS.get(tf)
    if ot is None or step is None:
        return {"tf": tf, "readable": False,
                "reason": "no open_time" if step else "unknown timeframe"}
    last_open = float(ot[-1])
    if not np.isfinite(last_open):
        # update_candle fills a missing open_time with NaN rather than a guess,
        # so an undatable bar is "we cannot tell", never "fresh".
        return {"tf": tf, "readable": False, "reason": "undated_bar"}
    # Alignment-free: bars that should have CLOSED after the stored one. The
    # old ``(now // step) * step`` form assumed epoch-aligned bars, which 1w
    # is not (Binance weeks open Monday; the epoch began on a Thursday).
    behind = max(0, int((now_ms - last_open) // step) - 1)
    return {"tf": tf, "readable": True, "last_bar_open_ms": int(last_open),
            "bars_behind": behind, "stale": behind >= STALE_INTERVALS}


def pct_change(closes: Optional[np.ndarray], bars: int) -> Optional[float]:
    if closes is None or len(closes) <= bars or closes[-1 - bars] <= 0:
        return None
    return round(float(closes[-1] / closes[-1 - bars] - 1.0) * 100.0, 4)


def atr_of(cd: Optional[dict], period: int = 14) -> Optional[float]:
    h, lo, c = _arr(cd, "high"), _arr(cd, "low"), _arr(cd, "close")
    if h is None or lo is None or c is None:
        return None
    return _atr(h, lo, c, period)


def trend_score(cd: Optional[dict]) -> Optional[float]:
    """The BTC-state scorer applied to any series: [-1, +1], None if not warm."""
    if not isinstance(cd, dict):
        return None
    out = compute_btc_state({"x": cd}, tf_weights={"x": 1.0})
    b: Any = out["b"]
    return round(float(b), 3) if out.get("status") == "ok" else None


def session_utc(ts: float) -> str:
    """Coarse trading session by UTC hour. Labels, not a signal."""
    h = time.gmtime(ts).tm_hour
    if 13 <= h < 22:
        return "us"
    if 7 <= h < 13:
        return "europe"
    return "asia"


def level_id(kind: str, price: float) -> str:
    return f"{kind}@{price:.8g}"


# ---------------------------------------------------------------------------
# Level menu
# ---------------------------------------------------------------------------


def _candidates(
    levels: Iterable[Any],
    tf_candles: Dict[str, dict],
    vp: Any,
    vp_macro: Any,
) -> List[Dict[str, Any]]:
    """Every level candidate with its kind and base points, before scoring."""
    out: List[Dict[str, Any]] = []
    for lv in levels or []:
        price = float(getattr(lv, "price", 0.0) or 0.0)
        if price <= 0:
            continue
        tfs = list(getattr(lv, "source_tfs", None) or [getattr(lv, "source_tf", "")])
        is_round = bool(getattr(lv, "is_round_number", False))
        best_tf = max(tfs, key=lambda t: TF_POINTS.get(t, 0.0)) if tfs else ""
        kind = "round" if (is_round and best_tf not in TF_POINTS) else f"swing_{best_tf or 'x'}"
        out.append({
            "kind": kind, "price": price,
            "tf_points": TF_POINTS.get(best_tf, 0.0),
            "round": is_round,
            "touches": int(getattr(lv, "touches", 1) or 1),
            "sources": sorted(set(tfs)),
        })
    # Prior day / week: callers pass closed bars only (``closed_bars``), so
    # [-1] is the prior period. The store DOES hold the forming bar after a
    # REST seed; this comment used to say it never did, and PDH was today's
    # partial high whenever that was true (2026-11-19).
    for tf, hk, lk in (("1d", "pdh", "pdl"), ("1w", "pwh", "pwl")):
        h, lo = _arr(tf_candles.get(tf), "high"), _arr(tf_candles.get(tf), "low")
        if h is not None and lo is not None:
            out.append({"kind": hk, "price": float(h[-1]), "tf_points": KIND_POINTS[hk],
                        "round": False, "touches": 1, "sources": [tf]})
            out.append({"kind": lk, "price": float(lo[-1]), "tf_points": KIND_POINTS[lk],
                        "round": False, "touches": 1, "sources": [tf]})
    for prefix, res in (("vp", vp), ("vp_macro", vp_macro)):
        if res is None:
            continue
        for name in ("poc", "vah", "val"):
            p = float(getattr(res, name, 0.0) or 0.0)
            if p > 0:
                k = f"{prefix}_{name}"
                out.append({"kind": k, "price": p, "tf_points": KIND_POINTS[k],
                            "round": False, "touches": 1, "sources": [prefix]})
    return out


def _freshness_points(touches: int) -> float:
    if touches <= 1:
        return 20.0
    if touches == 2:
        return 12.0
    if touches == 3:
        return 5.0
    return -5.0


def level_menu(
    price: float,
    atr_h1: Optional[float],
    levels: Iterable[Any],
    tf_candles: Dict[str, dict],
    vp: Any = None,
    vp_macro: Any = None,
    *,
    per_side: int = 4,
) -> Dict[str, Any]:
    """Scored levels above and below ``price``, best first on each side.

    Refuses (empty menu with a reason) rather than scoring without an ATR: the
    confluence band and every distance are in ATR units, and a menu scored
    without one would look complete and describe nothing.
    """
    if price is None or price <= 0:
        return {"levels": [], "refused": "no_price"}
    if atr_h1 is None or atr_h1 <= 0:
        return {"levels": [], "refused": "no_atr_1h"}
    cands = _candidates(levels, tf_candles, vp, vp_macro)
    band = CONFLUENCE_ATR * atr_h1
    scored: List[Dict[str, Any]] = []
    for i, c in enumerate(cands):
        n_conf = sum(1 for j, o in enumerate(cands)
                     if j != i and abs(o["price"] - c["price"]) <= band)
        parts = {
            "timeframe": c["tf_points"],
            "confluence": min(CONFLUENCE_POINTS_CAP, CONFLUENCE_POINTS_EACH * n_conf),
            "round": ROUND_POINTS if c["round"] else 0.0,
            "freshness": _freshness_points(c["touches"]),
        }
        score = max(0.0, min(100.0, sum(parts.values())))
        dist = c["price"] - price
        scored.append({
            "id": level_id(c["kind"], c["price"]),
            "kind": c["kind"],
            "price": c["price"],
            "side": "above" if dist > 0 else "below",
            "distance_pct": round(dist / price * 100.0, 4),
            "distance_atr": round(dist / atr_h1, 3),
            "score": round(score, 1),
            "score_parts": parts,
            "touches": c["touches"],
            "sources": c["sources"],
            "confluent_with": n_conf,
        })
    # Collapse exact duplicate ids (a swing and a PDH at the same print).
    uniq: Dict[str, Dict[str, Any]] = {}
    for s in scored:
        if s["id"] not in uniq or s["score"] > uniq[s["id"]]["score"]:
            uniq[s["id"]] = s
    above = sorted((s for s in uniq.values() if s["side"] == "above"),
                   key=lambda s: (-s["score"], abs(s["distance_atr"])))[:per_side]
    below = sorted((s for s in uniq.values() if s["side"] == "below"),
                   key=lambda s: (-s["score"], abs(s["distance_atr"])))[:per_side]
    return {"levels": above + below, "candidates": len(uniq),
            "score_config": "v1 (weights invented; see module docstring)"}


# ---------------------------------------------------------------------------
# Engine accessors — every one returns None rather than raising
# ---------------------------------------------------------------------------


def closed_bars(cd: Optional[dict], tf: str, now_ms: float) -> Optional[dict]:
    """*cd* without a trailing bar that has not closed yet.

    A REST-seeded bucket ends with the FORMING bar (Binance returns it), and
    for 1d / 1w — which have no WS writer — that partial bar is frozen at the
    moment of the pull. Reading it as a closed period made "prior day high"
    today's partial high. Undatable last bar → returned unchanged; the
    freshness block already reports it as unreadable.
    """
    if not isinstance(cd, dict):
        return cd
    ot = _arr(cd, "open_time")
    step = TF_MS.get(tf)
    if ot is None or step is None or not np.isfinite(ot[-1]):
        return cd
    if float(ot[-1]) + step <= now_ms:
        return cd
    n = len(ot) - 1
    return {k: (v[:n] if v is not None and hasattr(v, "__len__") and len(v) == n + 1 else v)
            for k, v in cd.items()}


def _store_candles(engine: Any, symbol: str, *, now_ms: Optional[float] = None,
                   closed_only: bool = True) -> Dict[str, dict]:
    store = getattr(engine, "data_store", None)
    buckets = getattr(store, "candles", None) or {}
    raw = dict(buckets.get(symbol) or {})
    if not closed_only:
        return raw
    now_ms = time.time() * 1000.0 if now_ms is None else now_ms
    return {tf: closed_bars(cd, tf, now_ms) for tf, cd in raw.items()}


def _scanner(engine: Any) -> Any:
    return getattr(engine, "_scanner", None)


def _universe(engine: Any) -> List[str]:
    pm = getattr(engine, "pair_mgr", None)
    pairs = getattr(pm, "pairs", None) or {}
    return sorted(str(s) for s in pairs)


def _unlocks_for(symbol: str, now: float) -> Dict[str, Any]:
    """Unlocks in the veto window from the unlock-short lane's calendar rows.

    The lane only records unlocks its calendar mapped to a Binance perp and
    classified as insider; ``readable`` is False when the lane has never read
    a calendar, which is "we do not know", never "there are none".
    """
    try:
        from src import unlock_shorts
        ledger = unlock_shorts.get_ledger()
    except Exception as exc:  # noqa: BLE001
        return {"readable": False, "reason": f"ledger_unavailable: {type(exc).__name__}",
                "events": []}
    if not getattr(ledger, "calendar", None):
        return {"readable": False, "reason": "calendar_never_read", "events": []}
    lo = now - UNLOCK_POST_DAYS * 86400
    hi = now + UNLOCK_PRE_DAYS * 86400
    events = []
    for row in list(getattr(ledger, "rows", {}).values()):
        if row.get("symbol") != symbol:
            continue
        day = float(row.get("unlock_day_ts") or 0.0)
        if lo <= day <= hi:
            events.append({"unlock_date": row.get("unlock_date"),
                           "fraction_of_supply": row.get("fraction"),
                           "days_from_now": round((day - now) / 86400.0, 1)})
    return {"readable": True, "events": sorted(events, key=lambda e: e["days_from_now"])}


# ---------------------------------------------------------------------------
# Public read models
# ---------------------------------------------------------------------------


def pair_snapshot(engine: Any, symbol: str, *, now: Optional[float] = None,
                  per_side: int = 4) -> Dict[str, Any]:
    now = time.time() if now is None else now
    now_ms = now * 1000.0
    tfc = _store_candles(engine, symbol, now_ms=now_ms)
    if not tfc:
        return {"symbol": symbol, "readable": False, "reason": "no_candles_in_store"}
    fresh = {tf: bar_freshness(tfc.get(tf), tf, now_ms)
             for tf in ("15m", "1h", "4h", "1d", "1w") if tf in tfc}
    price_tf = next((tf for tf in ("5m", "15m", "1h") if _arr(tfc.get(tf), "close") is not None), None)
    # Price is the newest print, forming bar included.
    raw = _store_candles(engine, symbol, closed_only=False)
    closes_p = _arr(raw.get(price_tf), "close") if price_tf else None
    price = float(closes_p[-1]) if closes_p is not None else None
    atr_h1, atr_h4 = atr_of(tfc.get("1h")), atr_of(tfc.get("4h"))
    d1 = _arr(tfc.get("1d"), "close")
    btc_d1 = _arr(_store_candles(engine, BTC, now_ms=now_ms).get("1d"), "close")
    chg7, btc7 = pct_change(d1, 7), pct_change(btc_d1, 7)
    sc = _scanner(engine)
    lb = getattr(sc, "level_book", None)
    levels = lb.get_levels(symbol) if lb is not None else []
    vp = getattr(getattr(sc, "volume_profile_store", None), "get", lambda _s: None)(symbol)
    vp_macro = getattr(getattr(sc, "volume_profile_store_macro", None), "get", lambda _s: None)(symbol)
    value_area = None
    if vp is not None and price:
        value_area = ("above_vah" if price > vp.vah else
                      "below_val" if price < vp.val else "inside")
    return {
        "symbol": symbol,
        "readable": price is not None,
        "as_of": now,
        "price": price,
        "price_tf": price_tf,
        "bar_freshness": fresh,
        "any_stale": any(f.get("stale") for f in fresh.values()),
        "atr": {
            "1h": atr_h1, "4h": atr_h4,
            "1h_pct": round(atr_h1 / price * 100.0, 4) if atr_h1 and price else None,
            "4h_pct": round(atr_h4 / price * 100.0, 4) if atr_h4 and price else None,
        },
        "trend": {tf: trend_score(tfc.get(tf)) for tf in ("1h", "4h", "1d")},
        "change_pct": {"24h": pct_change(_arr(tfc.get("1h"), "close"), 24), "7d": chg7},
        "rel_strength_vs_btc_7d": (round(chg7 - btc7, 4)
                                   if chg7 is not None and btc7 is not None and symbol != BTC
                                   else None),
        "value_area": value_area,
        "level_book_present": lb is not None,
        "levels": level_menu(price or 0.0, atr_h1, levels, tfc, vp, vp_macro,
                             per_side=per_side),
        "unlocks": _unlocks_for(symbol, now),
    }


def altcoin_breadth(engine: Any, symbols: Sequence[str], *,
                    now_ms: Optional[float] = None) -> Dict[str, Any]:
    """Share of the universe whose 7d return beats BTC's. n and misses counted.

    A pair whose 1d bucket is stale is counted apart (``stale``), never
    compared: its "7d" ends on a different day than BTC's.
    """
    now_ms = time.time() * 1000.0 if now_ms is None else now_ms
    btc_d1 = _store_candles(engine, BTC, now_ms=now_ms).get("1d")
    if bar_freshness(btc_d1, "1d", now_ms).get("stale", True):
        return {"readable": False, "reason": "btc_1d_stale_or_undated"}
    btc7 = pct_change(_arr(btc_d1, "close"), 7)
    if btc7 is None:
        return {"readable": False, "reason": "no_btc_7d"}
    beat = n = missing = stale = 0
    for s in symbols:
        if s == BTC:
            continue
        d1 = _store_candles(engine, s, now_ms=now_ms).get("1d")
        if d1 is not None and bar_freshness(d1, "1d", now_ms).get("stale", True):
            stale += 1
            continue
        r = pct_change(_arr(d1, "close"), 7)
        if r is None:
            missing += 1
            continue
        n += 1
        beat += int(r > btc7)
    if n == 0:
        return {"readable": False, "reason": "no_pairs_with_7d", "missing": missing,
                "stale": stale}
    return {"readable": True, "share_beating_btc_7d": round(beat / n, 4),
            "n": n, "missing": missing, "stale": stale, "btc_7d_pct": btc7}


def market_context(engine: Any, *, now: Optional[float] = None) -> Dict[str, Any]:
    now = time.time() if now is None else now
    btc = _store_candles(engine, BTC, now_ms=now * 1000.0)
    state = compute_btc_state({tf: btc[tf] for tf in ("1h", "4h", "1d") if tf in btc},
                              tf_weights={"1h": 0.2, "4h": 0.35, "1d": 0.45})
    b: Any = state["b"]
    per_tf: Any = state.get("per_tf") or {}
    closes_h1 = _arr(btc.get("1h"), "close")
    price = float(closes_h1[-1]) if closes_h1 is not None else None
    atr_d1 = atr_of(btc.get("1d"))
    return {
        "as_of": now,
        "session_utc": session_utc(now),
        "btc": {
            "price": price,
            "state_b": round(float(b), 3),
            "state_status": state.get("status"),
            "per_tf": {k: round(float(v), 3) for k, v in per_tf.items()},
            "change_pct": {"24h": pct_change(closes_h1, 24),
                           "7d": pct_change(_arr(btc.get("1d"), "close"), 7)},
            "atr_1d_pct": round(atr_d1 / price * 100.0, 4) if atr_d1 and price else None,
            "bar_freshness": {tf: bar_freshness(btc.get(tf), tf, now * 1000.0)
                              for tf in ("1h", "4h", "1d") if tf in btc},
        },
        "breadth": altcoin_breadth(engine, _universe(engine), now_ms=now * 1000.0),
        "macro_calendar": {
            "readable": False,
            "reason": "not_available — no macro event feed is wired "
                      "(macro_blackout receives an empty list). Treat as UNKNOWN, "
                      "never as 'no events'.",
        },
        "universe_size": len(_universe(engine)),
    }


def watchlist(engine: Any, *, now: Optional[float] = None, limit: int = 15) -> Dict[str, Any]:
    """Pairs sitting near a strong level, best first. A shortlist, not a signal."""
    now = time.time() if now is None else now
    rows: List[Dict[str, Any]] = []
    refused: Dict[str, int] = {}
    for sym in _universe(engine):
        snap = pair_snapshot(engine, sym, now=now, per_side=3)
        menu = snap.get("levels") or {}
        if not snap.get("readable") or menu.get("refused"):
            why = snap.get("reason") or menu.get("refused") or "unreadable"
            refused[why] = refused.get(why, 0) + 1
            continue
        near = [lv for lv in menu["levels"]
                if lv["score"] >= WATCH_MIN_SCORE and abs(lv["distance_atr"]) <= WATCH_MAX_ATR]
        if not near:
            continue
        best = max(near, key=lambda lv: (lv["score"], -abs(lv["distance_atr"])))
        rows.append({"symbol": sym, "price": snap["price"], "level": best,
                     "trend": snap["trend"], "any_stale": snap["any_stale"],
                     "unlock_events": len(snap["unlocks"].get("events") or [])})
    rows.sort(key=lambda r: (-r["level"]["score"], abs(r["level"]["distance_atr"])))
    return {"as_of": now, "criteria": {"min_score": WATCH_MIN_SCORE, "max_atr": WATCH_MAX_ATR},
            "count": len(rows), "rows": rows[:limit], "refused": refused}
