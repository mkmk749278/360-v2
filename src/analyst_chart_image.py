"""Rendered candlestick charts for the hourly analyst (2026-11-28).

Plan: ``docs/ANALYST_DESK_PLAN_2026_11_28.md`` Phase 1a. The analyst model is
multimodal, but until now it only ever saw candles as arrays of numbers: 120
rows of OHLC is a spreadsheet, not a chart. This renders the same closed bars
the ``chart`` tool returns as a PNG, so the model reads shape and context
(swings, ranges, wicks, compression, failed breaks) from the image. Exact
prices still come from the numbers, and the note says so.

Two halves, because catalog entries run on the engine's event loop:

* :func:`prepare` copies the bars out of the store. It is cheap and runs in the
  loop, so no other thread ever reads a buffer the loop is writing.
* :func:`render` draws the PNG from that copy. It is the slow half and runs in
  a worker thread (``diag_catalog.Entry.offload``). It uses an explicit
  ``Figure`` with the Agg canvas, never ``pyplot``, so no global state is
  shared between threads.

Read-only: it touches the candle store and nothing else, and reaches no
subscriber, signal or order.
"""
from __future__ import annotations

import base64
import io
import time
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from src import analyst_snapshot as A

TIMEFRAMES = ("15m", "1h", "4h", "1d")
DEFAULT_BARS = 120
MIN_BARS = 20
MAX_BARS = 200
#: Levels the analyst may ask to see drawn. Bounded so a chart stays readable.
MAX_LEVELS = 10
WIDTH_PX, HEIGHT_PX, DPI = 1100, 640, 100


def _levels(raw: Any) -> List[float]:
    if not isinstance(raw, (list, tuple)):
        return []
    out = []
    for x in raw[:MAX_LEVELS]:
        try:
            v = float(x)
        except (TypeError, ValueError):
            continue
        if np.isfinite(v) and v > 0:
            out.append(v)
    return out


def prepare(engine: Any, symbol: str, tf: str = "1h", bars: int = DEFAULT_BARS,
            levels: Optional[Sequence[Any]] = None, *,
            now: Optional[float] = None) -> Dict[str, Any]:
    """Copy the closed bars to draw. Refuses rather than drawing a guess."""
    now = time.time() if now is None else now
    now_ms = now * 1000.0
    if tf not in TIMEFRAMES:
        return {"readable": False, "reason": f"tf must be one of {TIMEFRAMES}"}
    try:
        bars = int(bars)
    except (TypeError, ValueError):
        bars = DEFAULT_BARS
    bars = max(MIN_BARS, min(bars, MAX_BARS))
    cd = A._store_candles(engine, symbol, now_ms=now_ms).get(tf)
    if not isinstance(cd, dict) or A._arr(cd, "close") is None:
        return {"symbol": symbol, "tf": tf, "readable": False, "reason": "no_candles"}
    cols = {k: A._arr(cd, k) for k in ("open_time", "open", "high", "low", "close", "volume")}
    n_all = len(cols["close"])
    for k in ("open", "high", "low"):
        if cols[k] is None or len(cols[k]) != n_all:
            return {"symbol": symbol, "tf": tf, "readable": False, "reason": f"bad_{k}_series"}
    n = min(bars, n_all)
    if n < MIN_BARS:
        return {"symbol": symbol, "tf": tf, "readable": False, "reason": "short_series",
                "bars_available": n}
    sl = slice(n_all - n, n_all)
    ot = cols["open_time"]
    vol = cols["volume"]
    return {
        "symbol": symbol, "tf": tf, "readable": True,
        "freshness": A.bar_freshness(cd, tf, now_ms),
        "open_time": ([int(x) for x in ot[sl]] if ot is not None and len(ot) == n_all
                      else None),
        "open": [float(x) for x in cols["open"][sl]],
        "high": [float(x) for x in cols["high"][sl]],
        "low": [float(x) for x in cols["low"][sl]],
        "close": [float(x) for x in cols["close"][sl]],
        "volume": ([float(x) for x in vol[sl]] if vol is not None and len(vol) == n_all
                   else None),
        "levels": _levels(levels),
    }


def _fmt_time(ms: Optional[int]) -> str:
    if ms is None:
        return "?"
    return time.strftime("%m-%d %H:%M", time.gmtime(ms / 1000.0))


def render(prep: Dict[str, Any]) -> Dict[str, Any]:
    """Draw the PNG from :func:`prepare`'s copy. Pure: no store, no network."""
    if not prep.get("readable"):
        return prep
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    o, h, lo, c = (np.asarray(prep[k], dtype=float) for k in ("open", "high", "low", "close"))
    n = len(c)
    x = np.arange(n)
    up = c >= o
    fig = Figure(figsize=(WIDTH_PX / DPI, HEIGHT_PX / DPI), dpi=DPI)
    FigureCanvasAgg(fig)
    has_vol = prep.get("volume") is not None
    if has_vol:
        gs = fig.add_gridspec(4, 1, hspace=0.05)
        ax = fig.add_subplot(gs[:3, 0])
        axv = fig.add_subplot(gs[3, 0], sharex=ax)
    else:
        ax, axv = fig.add_subplot(1, 1, 1), None
    green, red = "#1a9850", "#d73027"
    colors = np.where(up, green, red)
    ax.vlines(x, lo, h, colors=colors, linewidth=0.8)
    body_lo = np.minimum(o, c)
    body_h = np.maximum(np.abs(c - o), (h.max() - lo.min()) * 0.001)
    ax.bar(x, body_h, bottom=body_lo, width=0.7, color=colors, edgecolor=colors)
    ax.axhline(c[-1], color="#555555", linewidth=0.7, linestyle=":")
    ax.annotate(f"last {c[-1]:.6g}", xy=(n - 1, c[-1]), xytext=(4, 0),
                textcoords="offset points", fontsize=8, color="#333333", va="center")
    for lv in prep.get("levels") or []:
        ax.axhline(lv, color="#2b6cb0", linewidth=0.9, linestyle="--", alpha=0.85)
        ax.annotate(f"{lv:.6g}", xy=(0, lv), xytext=(2, 2), textcoords="offset points",
                    fontsize=8, color="#2b6cb0")
    ax.yaxis.tick_right()
    ax.grid(True, alpha=0.2)
    ax.set_xlim(-1, n + 6)
    ot = prep.get("open_time")
    ax.set_title(f"{prep['symbol']} {prep['tf']} — {n} closed bars, "
                 f"{_fmt_time(ot[0] if ot else None)} → {_fmt_time(ot[-1] if ot else None)} UTC",
                 fontsize=10)
    ticks = np.linspace(0, n - 1, 6).astype(int)
    if axv is not None:
        v = np.asarray(prep["volume"], dtype=float)
        axv.bar(x, v, width=0.7, color=colors, alpha=0.6)
        axv.yaxis.tick_right()
        axv.grid(True, alpha=0.2)
        axv.set_ylabel("vol", fontsize=8)
        tick_ax = axv
        ax.tick_params(labelbottom=False)
    else:
        tick_ax = ax
    tick_ax.set_xticks(ticks)
    tick_ax.set_xticklabels([_fmt_time(ot[i]) if ot else str(i) for i in ticks], fontsize=8)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, bbox_inches="tight")
    png = buf.getvalue()
    return {
        "symbol": prep["symbol"], "tf": prep["tf"], "readable": True,
        "freshness": prep.get("freshness"), "bars": n,
        "first_bar_ms": ot[0] if ot else None, "last_bar_ms": ot[-1] if ot else None,
        "last_close": float(c[-1]), "range": [float(lo.min()), float(h.max())],
        "levels_drawn": prep.get("levels") or [],
        "mime_type": "image/png", "png_bytes": len(png),
        "png_base64": base64.b64encode(png).decode("ascii"),
        "note": ("Closed bars only. Read shape and context from the image; take exact "
                 "prices for entries, stops and targets from the chart tool's numbers, "
                 "because reading a price off an image is imprecise. Dashed blue lines "
                 "are the levels you asked to see; the dotted line is the last close."),
    }
