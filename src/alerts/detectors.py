"""Pure alert detectors — numpy in, ``Optional[Alert]`` out.

Every detector reads ONLY closed-candle arrays already held by
``HistoricalDataStore`` (the store appends klines exclusively on
``x=True``), so a sweep over the whole universe costs zero network I/O.

Each detector runs on its natural timeframe, mirroring how 100eyes
stamps its cards: RSI extremes on 15m/1h/4h, RSI divergence on 1h/4h,
abnormal volatility + volume on 15m, near horizontal S/R on 1h.
"""

from __future__ import annotations

from typing import Any, List, Optional

import numpy as np

from config import (
    ALERTS_DIVERGENCE_LOOKBACK,
    ALERTS_DIVERGENCE_PIVOT_K,
    ALERTS_DIVERGENCE_ZONE_HIGH,
    ALERTS_DIVERGENCE_ZONE_LOW,
    ALERTS_NEAR_LEVEL_LOOKBACK,
    ALERTS_NEAR_LEVEL_MAX_IN_BAND_FRAC,
    ALERTS_NEAR_LEVEL_MIN_LEAVE_PCT,
    ALERTS_NEAR_LEVEL_MIN_SEPARATION_BARS,
    ALERTS_NEAR_LEVEL_MIN_TOUCHES,
    ALERTS_NEAR_LEVEL_PCT,
    ALERTS_NEAR_LEVEL_TOUCH_TOLERANCE_PCT,
    ALERTS_RSI_OVERBOUGHT,
    ALERTS_RSI_OVERSOLD,
    ALERTS_RSI_PERIOD,
    ALERTS_VOLATILITY_TR_MULT,
    ALERTS_VOLUME_SPIKE_MULT,
)
from src.indicators import atr as _atr
from src.indicators import rsi as _rsi

from .models import Alert, AlertType, make_alert

#: Minimum closed candles a detector needs before it will evaluate.
MIN_CANDLES = 60

#: Which timeframes each detector family sweeps (natural cadence per
#: 100eyes' behaviour — not one fixed timeframe for everything).
RSI_EXTREME_TIMEFRAMES = ("15m", "1h", "4h")
DIVERGENCE_TIMEFRAMES = ("1h", "4h")
VOLATILITY_TIMEFRAME = "15m"
VOLUME_TIMEFRAME = "15m"
NEAR_LEVEL_TIMEFRAME = "1h"


def _valid(candles: Optional[dict], need: int = MIN_CANDLES) -> bool:
    if not candles:
        return False
    close = candles.get("close")
    return close is not None and len(close) >= need


def detect_rsi_extreme(symbol: str, timeframe: str, candles: dict) -> Optional[Alert]:
    """RSI(14) beyond the extreme bands on the last closed candle."""
    if not _valid(candles):
        return None
    close = np.asarray(candles["close"], dtype=np.float64)
    values = _rsi(close, ALERTS_RSI_PERIOD)
    last = float(values[-1])
    if not np.isfinite(last):
        return None
    price = float(close[-1])
    if last >= ALERTS_RSI_OVERBOUGHT:
        return make_alert(
            AlertType.RSI_OVERBOUGHT, symbol, timeframe, price,
            f"RSI({ALERTS_RSI_PERIOD}) at {last:.1f} — extremely overbought",
            {"rsi": round(last, 2)},
        )
    if last <= ALERTS_RSI_OVERSOLD:
        return make_alert(
            AlertType.RSI_OVERSOLD, symbol, timeframe, price,
            f"RSI({ALERTS_RSI_PERIOD}) at {last:.1f} — extremely oversold",
            {"rsi": round(last, 2)},
        )
    return None


def _pivot_indices(arr: np.ndarray, k: int, find_high: bool) -> List[int]:
    """Indices of fractal pivots: STRICTLY the max (or min) of their
    ±k-candle neighbourhood — plateaus produce no pivot (a flat series
    would otherwise mark every candle).  The trailing k candles can't
    confirm a pivot yet and are excluded by construction."""
    out: List[int] = []
    n = len(arr)
    for i in range(k, n - k):
        window = arr[i - k : i + k + 1]
        centre = arr[i]
        if not np.isfinite(centre):
            continue
        if find_high and int((window < centre).sum()) == 2 * k:
            out.append(i)
        elif not find_high and int((window > centre).sum()) == 2 * k:
            out.append(i)
    return out


def detect_rsi_divergence(symbol: str, timeframe: str, candles: dict) -> Optional[Alert]:
    """Classic (regular) RSI divergence between the last two price pivots.

    Bearish: price higher high + RSI lower high, first RSI pivot in the
    overbought zone.  Bullish: price lower low + RSI higher low, first
    RSI pivot in the oversold zone.  The most recent pivot must be
    near the right edge so the alert is timely, not archaeology.
    """
    if not _valid(candles, need=ALERTS_DIVERGENCE_LOOKBACK + 20):
        return None
    k = ALERTS_DIVERGENCE_PIVOT_K
    close = np.asarray(candles["close"], dtype=np.float64)[-ALERTS_DIVERGENCE_LOOKBACK:]
    high = np.asarray(candles["high"], dtype=np.float64)[-ALERTS_DIVERGENCE_LOOKBACK:]
    low = np.asarray(candles["low"], dtype=np.float64)[-ALERTS_DIVERGENCE_LOOKBACK:]
    rsi_full = _rsi(
        np.asarray(candles["close"], dtype=np.float64), ALERTS_RSI_PERIOD
    )[-ALERTS_DIVERGENCE_LOOKBACK:]
    price = float(close[-1])
    n = len(close)
    recent_edge = n - 1 - (k + 1)  # newest pivot must confirm at the edge

    # ── Bearish: higher high in price, lower high in RSI ──
    highs = _pivot_indices(high, k, find_high=True)
    if len(highs) >= 2:
        a, b = highs[-2], highs[-1]
        if (
            b >= recent_edge
            and b - a >= 3
            and high[b] > high[a]
            and np.isfinite(rsi_full[a])
            and np.isfinite(rsi_full[b])
            and rsi_full[b] < rsi_full[a]
            and rsi_full[a] >= ALERTS_DIVERGENCE_ZONE_HIGH
        ):
            return make_alert(
                AlertType.RSI_BEARISH_DIVERGENCE, symbol, timeframe, price,
                (
                    f"Price made a higher high while RSI fell "
                    f"{rsi_full[a]:.0f}→{rsi_full[b]:.0f}"
                ),
                {
                    "rsi_first": round(float(rsi_full[a]), 2),
                    "rsi_second": round(float(rsi_full[b]), 2),
                    # Pivot geometry so the app can draw the divergence
                    # line on its chart: bars back from the latest
                    # closed candle + the pivot prices.
                    "pivot_a_bars_ago": int(n - 1 - a),
                    "pivot_b_bars_ago": int(n - 1 - b),
                    "pivot_a_price": float(high[a]),
                    "pivot_b_price": float(high[b]),
                },
            )

    # ── Bullish: lower low in price, higher low in RSI ──
    lows = _pivot_indices(low, k, find_high=False)
    if len(lows) >= 2:
        a, b = lows[-2], lows[-1]
        if (
            b >= recent_edge
            and b - a >= 3
            and low[b] < low[a]
            and np.isfinite(rsi_full[a])
            and np.isfinite(rsi_full[b])
            and rsi_full[b] > rsi_full[a]
            and rsi_full[a] <= ALERTS_DIVERGENCE_ZONE_LOW
        ):
            return make_alert(
                AlertType.RSI_BULLISH_DIVERGENCE, symbol, timeframe, price,
                (
                    f"Price made a lower low while RSI rose "
                    f"{rsi_full[a]:.0f}→{rsi_full[b]:.0f}"
                ),
                {
                    "rsi_first": round(float(rsi_full[a]), 2),
                    "rsi_second": round(float(rsi_full[b]), 2),
                    "pivot_a_bars_ago": int(n - 1 - a),
                    "pivot_b_bars_ago": int(n - 1 - b),
                    "pivot_a_price": float(low[a]),
                    "pivot_b_price": float(low[b]),
                },
            )
    return None


def detect_abnormal_volatility(symbol: str, timeframe: str, candles: dict) -> Optional[Alert]:
    """Last closed candle's true range ≥ N × the ATR of the candles before it."""
    if not _valid(candles):
        return None
    high = np.asarray(candles["high"], dtype=np.float64)
    low = np.asarray(candles["low"], dtype=np.float64)
    close = np.asarray(candles["close"], dtype=np.float64)
    # Baseline ATR from everything BEFORE the candle being judged, so the
    # spike can't inflate its own yardstick.
    baseline = _atr(high[:-1], low[:-1], close[:-1], 14)
    base = float(baseline[-1])
    if not np.isfinite(base) or base <= 0:
        return None
    prev_close = float(close[-2])
    tr = max(
        float(high[-1] - low[-1]),
        abs(float(high[-1]) - prev_close),
        abs(float(low[-1]) - prev_close),
    )
    if tr < ALERTS_VOLATILITY_TR_MULT * base:
        return None
    price = float(close[-1])
    move_pct = (price - prev_close) / prev_close * 100.0 if prev_close else 0.0
    return make_alert(
        AlertType.ABNORMAL_VOLATILITY, symbol, timeframe, price,
        f"Candle range {tr / base:.1f}× normal — {move_pct:+.2f}% move",
        {"tr_mult": round(tr / base, 2), "move_pct": round(move_pct, 2)},
    )


def detect_volume_spike(symbol: str, timeframe: str, candles: dict) -> Optional[Alert]:
    """Last closed candle's volume ≥ N × the prior 20-candle mean."""
    if not _valid(candles):
        return None
    volume = np.asarray(candles["volume"], dtype=np.float64)
    close = np.asarray(candles["close"], dtype=np.float64)
    baseline = volume[-21:-1]
    mean = float(baseline.mean()) if len(baseline) == 20 else 0.0
    if mean <= 0:
        return None
    mult = float(volume[-1]) / mean
    if mult < ALERTS_VOLUME_SPIKE_MULT:
        return None
    prev_close = float(close[-2])
    price = float(close[-1])
    move_pct = (price - prev_close) / prev_close * 100.0 if prev_close else 0.0
    return make_alert(
        AlertType.VOLUME_SPIKE, symbol, timeframe, price,
        f"Volume {mult:.1f}× the 20-candle average — {move_pct:+.2f}% move",
        {"volume_mult": round(mult, 2), "move_pct": round(move_pct, 2)},
    )


def _distinct_touch_events(
    level_price: float,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    *,
    tol_pct: float,
    min_sep_bars: int,
    min_leave_pct: float,
) -> tuple[List[int], int, float, float]:
    """Count DISTINCT touch events of ``level_price`` over the arrays.

    The LevelBook counts every straddling candle, so a chop range reads
    as a "523-touch level".  Here a run of consecutive in-band bars is
    ONE event, and a new event only arms after price has (a) stayed out
    of the band for ``min_sep_bars`` consecutive bars AND (b) closed at
    least ``min_leave_pct`` % away from the level in between.

    Returns ``(touch_start_indices, in_band_bar_count, zone_low, zone_high)``
    where the zone bounds are the traded extremes across touch bars,
    clipped to the tolerance band and widened to contain the level.
    """
    lo = level_price * (1.0 - tol_pct / 100.0)
    hi = level_price * (1.0 + tol_pct / 100.0)
    events: List[int] = []
    in_band_count = 0
    zone_low = level_price
    zone_high = level_price
    prev_in_band = False
    armed = True            # first touch needs no prior excursion
    out_run = 0             # consecutive out-of-band bars since last touch
    left_far_enough = False  # closed >= min_leave_pct away since last touch
    for i in range(len(close)):
        in_band = high[i] >= lo and low[i] <= hi
        if in_band:
            in_band_count += 1
            if not prev_in_band and armed:
                events.append(i)
                armed = False
            if events:  # only bars belonging to counted events shape the zone
                zone_low = min(zone_low, max(float(low[i]), lo))
                zone_high = max(zone_high, min(float(high[i]), hi))
            out_run = 0
            left_far_enough = False
        else:
            out_run += 1
            if abs(float(close[i]) - level_price) / level_price * 100.0 >= min_leave_pct:
                left_far_enough = True
            if out_run >= min_sep_bars and left_far_enough:
                armed = True
        prev_in_band = in_band
    return events, in_band_count, zone_low, zone_high


def detect_near_level(
    symbol: str, timeframe: str, candles: dict, level_book: Any
) -> Optional[Alert]:
    """Price within ``ALERTS_NEAR_LEVEL_PCT`` of a LevelBook level that
    the alert-side re-count confirms is a real, repeatedly-tested level.

    Candidates come from ``level_book.get_levels`` (read-only copy), NOT
    ``nearest_level`` — the book's best-score pick is biased toward
    chop-inflated levels, exactly the junk this detector filters out.
    Resistance sits above price, support below — a level the price has
    already crossed is the other kind and is skipped."""
    if not _valid(candles, need=30) or level_book is None:
        return None
    high = np.asarray(candles["high"], dtype=np.float64)
    low = np.asarray(candles["low"], dtype=np.float64)
    close = np.asarray(candles["close"], dtype=np.float64)
    price = float(close[-1])
    try:
        levels = list(level_book.get_levels(symbol) or [])
    except Exception:
        return None
    n = min(len(close), max(int(ALERTS_NEAR_LEVEL_LOOKBACK), 30))
    h, l, c = high[-n:], low[-n:], close[-n:]
    best = None  # (touch_events, in_band, zone_low, zone_high, level, dist)
    for lv in levels:
        distance_pct = abs(lv.price - price) / price * 100.0
        if distance_pct > ALERTS_NEAR_LEVEL_PCT:
            continue
        is_resistance = lv.price >= price
        if (lv.type == "resistance") != is_resistance:
            continue
        events, in_band, zone_low, zone_high = _distinct_touch_events(
            float(lv.price), h, l, c,
            tol_pct=ALERTS_NEAR_LEVEL_TOUCH_TOLERANCE_PCT,
            min_sep_bars=ALERTS_NEAR_LEVEL_MIN_SEPARATION_BARS,
            min_leave_pct=ALERTS_NEAR_LEVEL_MIN_LEAVE_PCT,
        )
        if len(events) < ALERTS_NEAR_LEVEL_MIN_TOUCHES:
            continue  # a visited price, not a level
        if in_band > ALERTS_NEAR_LEVEL_MAX_IN_BAND_FRAC * n:
            continue  # chop range masquerading as a level
        if best is None or (
            (-len(events), distance_pct) < (-len(best[0]), best[5])
        ):
            best = (events, in_band, zone_low, zone_high, lv, distance_pct)
    if best is None:
        return None
    events, _in_band, zone_low, zone_high, level, distance_pct = best
    touch_count = len(events)
    is_resistance = level.price >= price
    alert_type = AlertType.NEAR_RESISTANCE if is_resistance else AlertType.NEAR_SUPPORT
    kind = "resistance" if is_resistance else "support"
    return make_alert(
        alert_type, symbol, timeframe, price,
        (
            f"Price {distance_pct:.2f}% from {kind} at {level.price:g} "
            f"({touch_count} touches)"
        ),
        {
            # Back-compat keys (shipped app builds read these) — `touches`
            # now carries the honest distinct count.
            "level_price": level.price,
            "distance_pct": round(distance_pct, 3),
            "touches": touch_count,
            "level_tfs": list(level.source_tfs),
            # v3 setup geometry — the app draws the 100eyes-style zone box
            # and zooms the chart to the setup window from these.
            "touch_count": touch_count,
            "zone_low": float(zone_low),
            "zone_high": float(zone_high),
            "first_touch_bars_ago": int(n - 1 - events[0]),
            "last_touch_bars_ago": int(n - 1 - events[-1]),
        },
    )
