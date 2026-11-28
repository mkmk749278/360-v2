"""``pair_flow``: the market data the engine collects that the analyst never saw.

Plan: ``docs/ANALYST_DESK_PLAN_2026_11_28.md`` Phase 1b. A trader at a level
asks "who is trading here": were longs or shorts just flushed, did sellers
actually show up at this price, is the book stacked on one side. The engine
already holds that data for its own gates:

* **liquidations:** forceOrder events, per symbol, every universe pair;
* **footprint:** buy/sell volume by price for each 1m bar, tick-derived,
  ``AGGTRADE_MAX_SYMBOLS`` (40) pairs only;
* **kline CVD:** a 15m taker split, every pair;
* **depth:** 20-level book, ``DEPTH_MAX_SYMBOLS`` (40) pairs only;
* **volume profile:** POC / value area, the scanner's own;
* **funding and OI:** the order-flow store.

The analyst saw none of it. This read serves each block with its coverage and
freshness. An absent feed is ``null`` with a reason, never a zero: "no
liquidations" and "this pair's liquidations are not recorded" are different
facts.

Read-only. Copies values out of in-memory stores; no network, no Firestore.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import numpy as np

#: Liquidation windows reported, in seconds.
LIQ_WINDOWS = {"15m": 900, "1h": 3600, "4h": 14400}
#: Sealed 1m footprint bars aggregated into the price ladder (~2h).
LADDER_BARS = 120
LADDER_ROWS = 12
#: The ladder's row height, as a percent of the last price.
LADDER_ROW_PCT = 0.15
DEPTH_LEVELS = (5, 20)


def _r(x: Optional[float], nd: int = 2) -> Optional[float]:
    if x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return round(v, nd) if np.isfinite(v) else None


def _scanner(engine: Any) -> Any:
    return getattr(engine, "scanner", None) or getattr(engine, "_scanner", None)


def liquidations(engine: Any, symbol: str) -> Dict[str, Any]:
    flow = getattr(engine, "_order_flow_store", None)
    if flow is None:
        return {"readable": False, "reason": "no_order_flow_store"}
    out: Dict[str, Any] = {"readable": True, "windows": {}}
    for name, secs in LIQ_WINDOWS.items():
        longs = flow.get_recent_liq_volume_usd(symbol, secs, side="SELL")
        shorts = flow.get_recent_liq_volume_usd(symbol, secs, side="BUY")
        out["windows"][name] = {"longs_liquidated_usd": _r(longs),
                                "shorts_liquidated_usd": _r(shorts)}
    out["clusters_1h"] = flow.get_liquidation_clusters(symbol, window_seconds=3600,
                                                       max_clusters=3)
    out["note"] = ("forceOrder events since the engine's last restart, at most 500 per "
                   "pair. 'longs_liquidated' = forced sells. 0 means none recorded in "
                   "the window, and the stream covers every universe pair.")
    return out


def footprint_ladder(symbol: str, last_price: Optional[float]) -> Dict[str, Any]:
    from src import footprint

    store = footprint.get_store()
    bars = [b for b in store.bars(symbol, LADDER_BARS) if not b.incomplete]
    if not bars:
        return {"readable": False,
                "reason": "not_covered_or_no_bars",
                "note": "Tick footprint covers at most 40 pairs (AGGTRADE_MAX_SYMBOLS)."}
    ref = last_price or bars[-1].last_price
    if not ref:
        return {"readable": False, "reason": "no_reference_price"}
    step = ref * LADDER_ROW_PCT / 100.0
    rows: Dict[int, List[float]] = {}
    for b in bars:
        for idx, (buy, sell) in b.bins.items():
            p = b.price_of_bin(idx)
            if p is None:
                continue
            k = int(np.floor(p / step))
            acc = rows.setdefault(k, [0.0, 0.0])
            acc[0] += buy
            acc[1] += sell
    top = sorted(rows.items(), key=lambda kv: kv[1][0] + kv[1][1], reverse=True)[:LADDER_ROWS]
    ladder = [{"price_from": _r(k * step, 8), "price_to": _r((k + 1) * step, 8),
               "buy_usd": _r(v[0]), "sell_usd": _r(v[1]), "delta_usd": _r(v[0] - v[1])}
              for k, v in sorted(top, key=lambda kv: kv[0], reverse=True)]
    delta = [b.delta_quote for b in bars]
    return {
        "readable": True, "bars": len(bars),
        "from_ms": bars[0].bar_open, "to_ms": bars[-1].bar_open,
        "delta_usd": {"last_15": _r(sum(delta[-15:])), "last_60": _r(sum(delta[-60:])),
                      "all": _r(sum(delta))},
        "median_bar_volume_usd": _r(store.volume_baseline(symbol)),
        "ladder": ladder,
        "note": (f"Aggressive buy/sell volume by price from 1m tick footprint over the "
                 f"last {len(bars)} sealed bars, in rows {LADDER_ROW_PCT}% tall; the "
                 f"{LADDER_ROWS} busiest rows, highest price first. Positive delta = "
                 "buyers lifted offers there. Incomplete bars are excluded."),
    }


def kline_cvd(engine: Any, symbol: str) -> Dict[str, Any]:
    flow = getattr(engine, "_order_flow_store", None)
    if flow is None:
        return {"readable": False, "reason": "no_order_flow_store"}
    h = flow.get_cvd_15m_history(symbol)
    if h is None or len(h) < 2:
        return {"readable": False, "reason": "no_15m_cvd_history"}
    out = {"readable": True, "bars": int(len(h))}
    for n in (4, 16, 96):
        if len(h) > n:
            out[f"change_last_{n}_bars_usd"] = _r(float(h[-1] - h[-1 - n]))
    out["note"] = ("Cumulative taker buy minus sell, one point per closed 15m bar, from "
                   "kline taker fields (not ticks). 4 bars = 1h, 16 = 4h, 96 = 24h.")
    return out


def depth(symbol: str) -> Dict[str, Any]:
    from src import depth_book

    store = depth_book.get_store()
    snap = store.get(symbol)
    if snap is None:
        stale = store.get(symbol, allow_stale=True) is not None
        return {"readable": False, "reason": "stale" if stale else "not_covered",
                "note": "Order-book depth covers at most 40 pairs (DEPTH_MAX_SYMBOLS)."}
    bid, ask = snap.best_bid(), snap.best_ask()
    out: Dict[str, Any] = {"readable": True, "best_bid": bid, "best_ask": ask,
                           "spread_bps": (_r((ask - bid) / ((ask + bid) / 2) * 1e4, 2)
                                          if bid and ask else None)}
    for lv in DEPTH_LEVELS:
        nt = snap.notional(lv)
        out[f"top_{lv}"] = ({"bid_usd": _r(nt[0]), "ask_usd": _r(nt[1]), "levels": nt[2],
                             "imbalance": _r(snap.imbalance(lv), 4)}
                            if nt is not None else None)
    out["note"] = ("Live 20-level book. imbalance > 0 = more resting bids than asks. "
                   "Resting orders can be pulled; read it as context, never a trigger.")
    return out


def volume_profile(engine: Any, symbol: str, last_price: Optional[float]) -> Dict[str, Any]:
    sc = _scanner(engine)
    out: Dict[str, Any] = {}
    for name, attr in (("session", "volume_profile_store"),
                       ("macro", "volume_profile_store_macro")):
        st = getattr(sc, attr, None)
        vp = st.get(symbol) if st is not None and hasattr(st, "get") else None
        if vp is None:
            out[name] = {"readable": False, "reason": "no_profile"}
            continue
        pos = None
        if last_price:
            pos = ("above_vah" if last_price > vp.vah else
                   "below_val" if last_price < vp.val else "inside")
        out[name] = {"readable": True, "poc": vp.poc, "vah": vp.vah, "val": vp.val,
                     "lookback_bars": vp.lookback, "price_vs_value_area": pos}
    return out


def derivatives(engine: Any, symbol: str) -> Dict[str, Any]:
    flow = getattr(engine, "_order_flow_store", None)
    if flow is None:
        return {"readable": False, "reason": "no_order_flow_store"}
    fr = flow.get_funding_rate(symbol)
    try:
        oi_chg = flow.get_oi_change_pct(symbol)
        oi_trend = getattr(flow.get_oi_trend(symbol), "value", None)
    except Exception:  # noqa: BLE001 — an absent history is reported, not raised
        oi_chg, oi_trend = None, None
    return {"readable": True, "funding_rate": fr, "oi_change_pct_recent": _r(oi_chg, 3),
            "oi_trend": oi_trend,
            "note": "Funding and OI from the live poller; 48h hourly history is on chart."}


def pair_flow(engine: Any, symbol: str, *, now: Optional[float] = None) -> Dict[str, Any]:
    """Everything the engine knows about who is trading this pair, with coverage."""
    from src import analyst_snapshot as A

    now = time.time() if now is None else now
    raw = A._store_candles(engine, symbol, closed_only=False)
    last = None
    for tf in ("1m", "5m", "15m", "1h"):
        c = A._arr(raw.get(tf), "close")
        if c is not None and len(c):
            last = float(c[-1])
            break
    blocks = {
        "liquidations": lambda: liquidations(engine, symbol),
        "footprint": lambda: footprint_ladder(symbol, last),
        "cvd_15m": lambda: kline_cvd(engine, symbol),
        "depth": lambda: depth(symbol),
        "volume_profile": lambda: volume_profile(engine, symbol, last),
        "derivatives": lambda: derivatives(engine, symbol),
    }
    out: Dict[str, Any] = {"symbol": symbol, "as_of": now, "last_price": last}
    for name, fn in blocks.items():
        try:
            out[name] = fn()
        except Exception as exc:  # noqa: BLE001 — one dead feed must not hide the rest
            from src import fail_open

            fail_open.record(f"analyst_flow.{name}", exc)
            out[name] = {"readable": False, "reason": f"error: {type(exc).__name__}"}
    out["coverage"] = {k: bool((out[k] or {}).get("readable")) for k in blocks
                       if k != "volume_profile"}
    out["note"] = ("Context at the level, never the trigger. Every block says whether it "
                   "could be read; an unreadable block is unknown, not zero.")
    return out
