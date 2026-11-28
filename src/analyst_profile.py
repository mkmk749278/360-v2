"""``pair_profile``: how a coin behaves, computed from the candles the engine holds.

Plan: ``docs/ANALYST_DESK_PLAN_2026_11_28.md`` Phase 1c. A trader keeps a book
on each coin: how hard it moves with BTC, how violent its candles are, whether
it trends or snaps back. This computes that book from stored bars (500 each of
1h, 4h and 1d: ~21 days, ~83 days, ~16 months). The model never writes any of
it.

Every figure carries the n it rests on, and refuses (``None`` with a reason)
when the bars cannot support it. Dropped on purpose, after a second opinion:
session and weekday patterns (21 days of 1h is too thin, and it invites
stories) and per-coin win/loss history (that belongs in the pair book, stamped,
never as a rule).

Cached per symbol, keyed on the newest closed 1h bar of the coin and of BTC,
so a call inside the same hour costs nothing and a new bar recomputes. That is
an invalidation signal, not a TTL. Read-only.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple

import numpy as np

from src import analyst_snapshot as A

BTC = "BTCUSDT"
MIN_ALIGNED = 60
DECOUPLE_BARS = 48          # 1h bars: "right now" = the last two days
WICK_BARS = 120             # 1h bars
PERSIST_BARS_4H = 180       # 30 days of 4h
BREAKOUT_LOOKBACK = 20      # 4h bars
BREAKOUT_HOLD = 3           # 4h bars after the break
DAILY_RANGE_DAYS = 30
VOL_PCTL_DAYS = 90
REGIME_DAYS = 180
_CACHE: Dict[str, Tuple[Tuple[Any, Any], Dict[str, Any]]] = {}
_CACHE_MAX = 300


def _series(engine: Any, symbol: str, tf: str, now_ms: float) -> Optional[Dict[str, np.ndarray]]:
    cd = A._store_candles(engine, symbol, now_ms=now_ms).get(tf)
    out = {k: A._arr(cd, k) for k in ("open_time", "open", "high", "low", "close",
                                       "volume")}
    c = out["close"]
    if c is None or out["open_time"] is None or len(out["open_time"]) != len(c):
        return None
    for k in ("open", "high", "low"):
        if out[k] is None or len(out[k]) != len(c):
            return None
    if out["volume"] is not None and len(out["volume"]) != len(c):
        out["volume"] = None
    return out


def _aligned_returns(a: Dict[str, np.ndarray], b: Dict[str, np.ndarray]
                     ) -> Tuple[np.ndarray, np.ndarray]:
    """Log returns of a and b on the bars both hold (matched by open time)."""
    ta, tb = a["open_time"].astype(np.int64), b["open_time"].astype(np.int64)
    common, ia, ib = np.intersect1d(ta, tb, return_indices=True)
    if len(common) < 3:
        return np.array([]), np.array([])
    ca, cb = a["close"][ia], b["close"][ib]
    ok = (ca > 0) & (cb > 0)
    ca, cb = ca[ok], cb[ok]
    # consecutive only: a gap in either series would make a "return" span hours
    gaps = np.diff(common[ok]) != np.median(np.diff(common[ok])) if ok.sum() > 2 else None
    ra, rb = np.diff(np.log(ca)), np.diff(np.log(cb))
    if gaps is not None:
        ra, rb = ra[~gaps], rb[~gaps]
    return ra, rb


def _beta(ra: np.ndarray, rb: np.ndarray, min_n: int = MIN_ALIGNED) -> Dict[str, Any]:
    if len(ra) < min_n:
        return {"beta": None, "corr": None, "n": int(len(ra)), "reason": "too_few_bars"}
    vb = float(np.var(rb))
    if vb <= 0:
        return {"beta": None, "corr": None, "n": int(len(ra)), "reason": "btc_flat"}
    beta = float(np.cov(ra, rb, ddof=0)[0, 1] / vb)
    corr = float(np.corrcoef(ra, rb)[0, 1])
    return {"beta": round(beta, 3), "corr": round(corr, 3), "n": int(len(ra))}


def btc_relationship(c1h, b1h, c4h, b4h) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if c1h is None or b1h is None:
        return {"readable": False, "reason": "no_1h_series"}
    ra, rb = _aligned_returns(c1h, b1h)
    out["1h"] = _beta(ra, rb)
    out["now_48h"] = _beta(ra[-DECOUPLE_BARS:], rb[-DECOUPLE_BARS:], min_n=DECOUPLE_BARS - 4)
    if c4h is not None and b4h is not None:
        a4, b4 = _aligned_returns(c4h, b4h)
        out["4h"] = _beta(a4, b4)
        up, dn = b4 > 0, b4 < 0
        out["4h_btc_up_bars"] = _beta(a4[up], b4[up], min_n=40)
        out["4h_btc_down_bars"] = _beta(a4[dn], b4[dn], min_n=40)
    full = out["1h"].get("corr")
    now = out["now_48h"].get("corr")
    out["decoupled_now"] = (None if full is None or now is None
                            else bool(full >= 0.5 and now < full - 0.3))
    out["readable"] = True
    out["note"] = ("beta: % move per 1% BTC move. Down-bar beta above up-bar beta = falls "
                   "harder than it rises with BTC. decoupled_now: last-48h correlation "
                   "is 0.3+ below its usual, from a usually-correlated coin.")
    return out


def volatility(c1h, c1d) -> Dict[str, Any]:
    out: Dict[str, Any] = {"readable": True}
    if c1d is not None and len(c1d["close"]) >= DAILY_RANGE_DAYS:
        rng = (c1d["high"] - c1d["low"]) / np.where(c1d["close"] > 0, c1d["close"], np.nan) * 100
        rng = rng[np.isfinite(rng)]
        last30 = rng[-DAILY_RANGE_DAYS:]
        out["daily_range_pct_median_30d"] = round(float(np.median(last30)), 3)
        hist = rng[-VOL_PCTL_DAYS:]
        if len(hist) >= 20:
            recent = float(np.mean(rng[-3:]))
            out["daily_range_percentile_90d"] = round(float((hist < recent).mean() * 100), 1)
            out["daily_range_pct_last_3d"] = round(recent, 3)
            out["percentile_n"] = int(len(hist))
    else:
        out["daily_range_pct_median_30d"] = None
        out["reason_daily"] = "too_few_daily_bars"
    if c1h is not None and len(c1h["close"]) >= 20:
        o, h, lo, c = (c1h[k][-WICK_BARS:] for k in ("open", "high", "low", "close"))
        span = h - lo
        ok = span > 0
        wick = (span - np.abs(c - o))[ok] / span[ok]
        out["wick_share_median_1h"] = round(float(np.median(wick)), 3) if len(wick) else None
        out["wick_n"] = int(ok.sum())
        out["wick_note"] = ("share of each 1h candle's range that is wick. Above ~0.6 = "
                            "wick-heavy: stops near obvious levels get swept.")
    return out


def character(c4h) -> Dict[str, Any]:
    if c4h is None or len(c4h["close"]) < PERSIST_BARS_4H // 2:
        return {"readable": False, "reason": "too_few_4h_bars"}
    c = c4h["close"][-PERSIST_BARS_4H:]
    r = np.diff(np.log(c[c > 0]))
    out: Dict[str, Any] = {"readable": True, "n_bars_4h": int(len(r))}
    if len(r) > 10 and np.var(r) > 0:
        ac1 = float(np.corrcoef(r[:-1], r[1:])[0, 1])
        k = 4
        rk = np.log(c[k:] / c[:-k])
        vr = float(np.var(rk) / (k * np.var(r))) if len(rk) > 5 else None
        out["autocorr_lag1"] = round(ac1, 3)
        out["variance_ratio_4"] = round(vr, 3) if vr is not None else None
        label = "neutral"
        if vr is not None and vr > 1.15:
            label = "trending"
        elif vr is not None and vr < 0.85:
            label = "mean_reverting"
        out["behaviour"] = label
    h, lo, cl = c4h["high"][-PERSIST_BARS_4H:], c4h["low"][-PERSIST_BARS_4H:], c
    held = fail = 0
    for i in range(BREAKOUT_LOOKBACK, len(cl) - BREAKOUT_HOLD):
        hi_prev = h[i - BREAKOUT_LOOKBACK:i].max()
        lo_prev = lo[i - BREAKOUT_LOOKBACK:i].min()
        nxt = cl[i + 1:i + 1 + BREAKOUT_HOLD]
        if cl[i] > hi_prev:
            held, fail = (held + 1, fail) if nxt.min() > hi_prev else (held, fail + 1)
        elif cl[i] < lo_prev:
            held, fail = (held + 1, fail) if nxt.max() < lo_prev else (held, fail + 1)
    n = held + fail
    out["breakouts"] = {"n": n, "held_share": round(held / n, 3) if n else None,
                        "rule": (f"4h close beyond the prior {BREAKOUT_LOOKBACK}-bar extreme; "
                                 f"held = the next {BREAKOUT_HOLD} closes stay beyond it")}
    out["note"] = ("variance_ratio_4 > 1.15 = moves tend to extend (trending), < 0.85 = "
                   "tend to snap back (mean-reverting), over the last 30 days of 4h bars. "
                   "Pick the archetype that fits; read n.")
    return out


def btc_regimes(c1d, b1d) -> Dict[str, Any]:
    if c1d is None or b1d is None:
        return {"readable": False, "reason": "no_daily_series"}
    if int(c1d["open_time"][-1]) != int(b1d["open_time"][-1]):
        # The regime labels are BTC's latest days; a coin whose daily series
        # ends elsewhere would be scored against the wrong days.
        return {"readable": False, "reason": "daily_series_not_aligned_to_btc"}
    ra, rb = _aligned_returns(c1d, b1d)
    bc = b1d["close"]
    if len(rb) < 40 or len(bc) < 40:
        return {"readable": False, "reason": "too_few_daily_bars"}
    sma = np.convolve(bc, np.ones(20) / 20, mode="valid")
    slope = np.diff(sma)
    # label the last len(slope) BTC days, then line up with the aligned returns' tail
    lab = np.where((bc[-len(slope):] > sma[-len(slope):]) & (slope > 0), "btc_uptrend",
                   np.where((bc[-len(slope):] < sma[-len(slope):]) & (slope < 0),
                            "btc_downtrend", "btc_range"))
    m = min(len(lab), len(ra), REGIME_DAYS)
    lab, ra, rb = lab[-m:], ra[-m:], rb[-m:]
    out: Dict[str, Any] = {"readable": True, "days": int(m)}
    for name in ("btc_uptrend", "btc_downtrend", "btc_range"):
        sel = lab == name
        n = int(sel.sum())
        if n < 10:
            out[name] = {"n_days": n, "reason": "too_few_days"}
            continue
        out[name] = {"n_days": n,
                     "avg_daily_pct": round(float(np.mean(np.expm1(ra[sel]))) * 100, 3),
                     "vs_btc_daily_pct": round(float(np.mean(np.expm1(ra[sel])
                                                              - np.expm1(rb[sel]))) * 100, 3)}
    out["note"] = ("BTC uptrend = close above a rising 20-day SMA; downtrend = below a "
                   "falling one; otherwise range. vs_btc = average daily return minus "
                   "BTC's on those days.")
    return out


def liquidity(c1h) -> Dict[str, Any]:
    """24h and 7-day traded value in USD.

    Quote volume (``volume_usd``) exists only on REST-seeded bars: the live
    kline path appends base volume alone, so after the first live bar the two
    arrays differ in length. Base volume x close is used instead, and the
    source is named.
    """
    if c1h is None or len(c1h["close"]) < 24:
        return {"readable": False, "reason": "too_few_1h_bars"}
    cd_vol = c1h.get("volume")
    if cd_vol is None:
        return {"readable": False, "reason": "no_volume"}
    v = cd_vol * c1h["close"]
    day = float(np.sum(v[-24:]))
    week = float(np.sum(v[-168:])) / max(1.0, min(len(v), 168) / 24)
    return {"readable": True, "volume_usd_24h": round(day, 0),
            "volume_usd_daily_avg_7d": round(week, 0),
            "surge_24h_vs_7d": round(day / week, 3) if week > 0 else None,
            "source": "base volume x bar close (an estimate of quote volume)"}


def funding_context(symbol: str, now: float) -> Dict[str, Any]:
    from src import analyst_charts

    rows = analyst_charts._deriv_rows(symbol, int((now - 7 * 86400) * 1000))
    fr = np.array([r["funding_rate"] for r in rows if r.get("funding_rate") is not None],
                  dtype=float)
    oi = [r["oi_coin"] for r in rows if r.get("oi_coin")]
    out: Dict[str, Any] = {"readable": bool(len(fr) or oi), "hours": len(rows)}
    if len(fr) >= 24 and np.std(fr) > 0:
        out["funding_now"] = float(fr[-1])
        out["funding_z_7d"] = round(float((fr[-1] - fr.mean()) / fr.std()), 2)
    if len(oi) >= 25:
        out["oi_change_24h_pct"] = round((oi[-1] / oi[-25] - 1) * 100, 2) if oi[-25] else None
    if not out["readable"]:
        out["reason"] = "no_recorder_history"
    return out


def pair_profile(engine: Any, symbol: str, *, now: Optional[float] = None) -> Dict[str, Any]:
    now = time.time() if now is None else now
    now_ms = now * 1000.0
    s = {tf: _series(engine, symbol, tf, now_ms) for tf in ("1h", "4h", "1d")}
    b = {tf: _series(engine, BTC, tf, now_ms) for tf in ("1h", "4h", "1d")} if symbol != BTC else s
    if s["1h"] is None:
        return {"symbol": symbol, "readable": False, "reason": "no_1h_candles"}
    key = (int(s["1h"]["open_time"][-1]),
           int(b["1h"]["open_time"][-1]) if b["1h"] is not None else None)
    hit = _CACHE.get(symbol)
    if hit is not None and hit[0] == key:
        return {**hit[1], "cached": True}
    out: Dict[str, Any] = {
        "symbol": symbol, "readable": True, "as_of": now,
        "bars_held": {tf: (len(v["close"]) if v is not None else 0) for tf, v in s.items()},
        "btc": (btc_relationship(s["1h"], b["1h"], s["4h"], b["4h"]) if symbol != BTC
                else {"readable": False, "reason": "is_btc"}),
        "volatility": volatility(s["1h"], s["1d"]),
        "character": character(s["4h"]),
        "btc_regimes": (btc_regimes(s["1d"], b["1d"]) if symbol != BTC
                        else {"readable": False, "reason": "is_btc"}),
        "liquidity": liquidity(s["1h"]),
        "funding_oi": funding_context(symbol, now),
        "unlocks": A._unlocks_for(symbol, now),
        "note": ("Computed by the engine from stored candles; every figure carries its n "
                 "and None means it could not be computed. Use it for decisions: beta "
                 "sizes the BTC bet, wick share sets the stop buffer, behaviour picks "
                 "the archetype, decoupled_now permits a counter-BTC idea."),
    }
    if len(_CACHE) >= _CACHE_MAX:
        _CACHE.pop(next(iter(_CACHE)))
    _CACHE[symbol] = (key, out)
    return {**out, "cached": False}
