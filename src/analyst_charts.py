"""The analyst's own market view: a whole-universe scan and raw charts (2026-11-20).

Owner, 2026-11-20: the analyst must analyse the market itself (its own charts,
movements, structure, levels), as a real analyst does but across more coins in
less time, rather than choose from a menu the engine pre-digested.

This module gives it the raw material and nothing more:

* :func:`scan` is one compact row per universe pair, so the analyst triages
  every coin each hour. Each row has price, change over 1h/4h/24h/7d, 1h-ATR %,
  volume surge (last 24h vs the 7-day hourly mean), position in the 7-day
  range, funding and 24h OI change (both from the derivatives recorder's own
  data, ``None`` when it has none).
* :func:`chart` returns the actual CLOSED bars for one pair and timeframe
  (OHLCV + taker-buy share), plus up to 48h of the recorder's hourly OI,
  funding and premium history. No indicator is computed for the analyst; the
  structure read is its job.

Both are pure reads of the engine's own candle store and local SQLite. They
make no vendor or Firestore call and reach no order. Every field that could not
be computed is ``None`` with the bucket's freshness beside it, never a guess.
"""
from __future__ import annotations

import os
import sqlite3
import time
from typing import Any, Dict, List, Optional

import numpy as np

from src import analyst_snapshot as A

TIMEFRAMES = ("15m", "1h", "4h", "1d")
MAX_BARS = 300
DEFAULT_BARS = 120


def _sig(x: Any, digits: int = 6) -> Optional[float]:
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(f):
        return None
    return float(f"{f:.{digits}g}")


def _deriv_rows(symbol: str, since_ms: int) -> List[Dict[str, Any]]:
    from src import derivatives_recorder as D

    path = D.get_recorder().path
    if not os.path.exists(path):
        return []
    con = sqlite3.connect(path, timeout=5)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(
            "SELECT hour_ms, oi_coin, funding_rate, premium_pct, taker_ratio "
            "FROM deriv_hourly WHERE symbol=? AND hour_ms>=? ORDER BY hour_ms",
            (symbol, int(since_ms)))]
    finally:
        con.close()


def _deriv_index(since_ms: int) -> Dict[str, List[Dict[str, Any]]]:
    """All symbols' recorder rows since ``since_ms``, one query."""
    from src import derivatives_recorder as D

    path = D.get_recorder().path
    out: Dict[str, List[Dict[str, Any]]] = {}
    if not os.path.exists(path):
        return out
    con = sqlite3.connect(path, timeout=5)
    con.row_factory = sqlite3.Row
    try:
        for r in con.execute(
                "SELECT symbol, hour_ms, oi_coin, funding_rate FROM deriv_hourly "
                "WHERE hour_ms>=? ORDER BY hour_ms", (int(since_ms),)):
            out.setdefault(r["symbol"], []).append(dict(r))
    finally:
        con.close()
    return out


def _oi_change_24h(rows: List[Dict[str, Any]]) -> Optional[float]:
    pts = [r for r in rows if r.get("oi_coin")]
    if len(pts) < 2:
        return None
    first, last = pts[0], pts[-1]
    if last["hour_ms"] - first["hour_ms"] < 20 * 3_600_000:
        return None  # not 24h of history yet: unknown, not zero
    return round((float(last["oi_coin"]) / float(first["oi_coin"]) - 1) * 100, 3)


def scan(engine: Any, *, now: Optional[float] = None) -> Dict[str, Any]:
    """One row per universe pair. The analyst's own triage of the whole market."""
    now = time.time() if now is None else now
    now_ms = now * 1000.0
    deriv = _deriv_index(int(now_ms - 26 * 3_600_000))
    rows: List[Dict[str, Any]] = []
    stale: List[Dict[str, Any]] = []
    refused: Dict[str, int] = {}
    for sym in A._universe(engine):
        tfc = A._store_candles(engine, sym, now_ms=now_ms)
        h1 = tfc.get("1h")
        fr = A.bar_freshness(h1, "1h", now_ms)
        closes = A._arr(h1, "close")
        if closes is None or len(closes) < 24 * 7 + 1 or not fr.get("readable"):
            refused["short_or_undated_1h"] = refused.get("short_or_undated_1h", 0) + 1
            continue
        hi = A._arr(h1, "high")[-168:]
        lo = A._arr(h1, "low")[-168:]
        vol = A._arr(h1, "volume")
        price = float(closes[-1])
        atr = A.atr_of(h1)
        rng = float(hi.max() - lo.min())
        v24 = float(vol[-24:].sum()) if vol is not None else None
        v7 = float(vol[-168:].mean()) * 24 if vol is not None else None
        if fr.get("stale"):
            # Listed apart, not in rows: the validator refuses a stale pair
            # (data_stale), so a chart read on it is a wasted call.
            stale.append({"symbol": sym, "bars_behind": fr.get("bars_behind")})
            continue
        d = deriv.get(sym, [])
        rows.append({
            "symbol": sym,
            "price": _sig(price),
            "chg_pct": {"1h": A.pct_change(closes, 1), "4h": A.pct_change(closes, 4),
                        "24h": A.pct_change(closes, 24), "7d": A.pct_change(closes, 168)},
            "atr_1h_pct": round(atr / price * 100, 3) if atr and price else None,
            "vol_surge_24h": round(v24 / v7, 2) if v24 and v7 else None,
            "pos_in_7d_range": round((price - float(lo.min())) / rng, 3) if rng > 0 else None,
            "funding_rate": _sig(d[-1]["funding_rate"]) if d and d[-1].get("funding_rate")
            is not None else None,
            "oi_chg_24h_pct": _oi_change_24h(d),
            "stale_1h": bool(fr.get("stale")),
        })
    rows.sort(key=lambda r: -abs(r["chg_pct"]["24h"] or 0.0))
    return {"as_of": now, "n": len(rows), "refused": refused, "rows": rows,
            "stale": stale,
            "note": ("Sorted by |24h change|. Changes are from closed 1h bars. Pairs whose "
                     "1h bars are stale are listed under 'stale', not in rows: a setup on "
                     "one is refused as data_stale. "
                     "funding/OI come from the hourly recorder; None = no history yet, "
                     "never zero.")}


def chart(engine: Any, symbol: str, tf: str = "1h", bars: int = DEFAULT_BARS, *,
          now: Optional[float] = None) -> Dict[str, Any]:
    """Raw closed bars for one pair and timeframe, plus derivatives history."""
    now = time.time() if now is None else now
    now_ms = now * 1000.0
    if tf not in TIMEFRAMES:
        return {"readable": False, "reason": f"tf must be one of {TIMEFRAMES}"}
    bars = max(10, min(int(bars), MAX_BARS))
    cd = A._store_candles(engine, symbol, now_ms=now_ms).get(tf)
    fr = A.bar_freshness(cd, tf, now_ms)
    if not isinstance(cd, dict) or A._arr(cd, "close") is None:
        return {"symbol": symbol, "tf": tf, "readable": False, "reason": "no_candles"}
    ot = A._arr(cd, "open_time")
    o, h, lo, c = (A._arr(cd, k) for k in ("open", "high", "low", "close"))
    v = A._arr(cd, "volume")
    vusd = A._arr(cd, "volume_usd")
    tb = A._arr(cd, "taker_buy_vol_usd")
    n = min(bars, len(c))
    out_bars = []
    for i in range(len(c) - n, len(c)):
        buy = None
        if vusd is not None and tb is not None and len(vusd) == len(c) and vusd[i] > 0:
            buy = round(float(tb[i]) / float(vusd[i]), 3)
        out_bars.append([int(ot[i]) if ot is not None and np.isfinite(ot[i]) else None,
                         _sig(o[i]), _sig(h[i]), _sig(lo[i]), _sig(c[i]),
                         _sig(v[i], 4) if v is not None else None, buy])
    deriv = [{"hour_ms": r["hour_ms"], "oi_coin": _sig(r["oi_coin"]),
              "funding_rate": _sig(r["funding_rate"]),
              "premium_pct": _sig(r["premium_pct"], 4), "taker_ratio": _sig(r["taker_ratio"], 4)}
             for r in _deriv_rows(symbol, int(now_ms - 48 * 3_600_000))]
    return {"symbol": symbol, "tf": tf, "readable": True, "freshness": fr,
            "columns": ["open_time_ms", "open", "high", "low", "close", "volume",
                        "taker_buy_share"],
            "bars": out_bars, "derivatives_48h": deriv,
            "note": ("Closed bars only, oldest first. taker_buy_share None = the bucket "
                     "carries no taker split. derivatives_48h is hourly from the recorder.")}
