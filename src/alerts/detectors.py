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
    ALERTS_NEAR_LEVEL_MIN_TOUCHES,
    ALERTS_NEAR_LEVEL_PCT,
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


def detect_near_level(
    symbol: str, timeframe: str, candles: dict, level_book: Any
) -> Optional[Alert]:
    """Price within ``ALERTS_NEAR_LEVEL_PCT`` of the best-scored LevelBook
    level.  Resistance sits above price, support below — a level the
    price has already crossed is the other kind and is skipped."""
    if not _valid(candles, need=2) or level_book is None:
        return None
    close = np.asarray(candles["close"], dtype=np.float64)
    price = float(close[-1])
    try:
        level = level_book.nearest_level(
            symbol, price, max_distance_pct=ALERTS_NEAR_LEVEL_PCT
        )
    except Exception:
        return None
    if level is None:
        return None
    if level.touches < ALERTS_NEAR_LEVEL_MIN_TOUCHES:
        return None  # one or two touches is a visited price, not a level
    is_resistance = level.price >= price
    if (level.type == "resistance") != is_resistance:
        return None
    distance_pct = abs(level.price - price) / price * 100.0
    alert_type = AlertType.NEAR_RESISTANCE if is_resistance else AlertType.NEAR_SUPPORT
    kind = "resistance" if is_resistance else "support"
    return make_alert(
        alert_type, symbol, timeframe, price,
        (
            f"Price {distance_pct:.2f}% from {kind} at {level.price:g} "
            f"({level.touches} touches)"
        ),
        {
            "level_price": level.price,
            "distance_pct": round(distance_pct, 3),
            "touches": level.touches,
            "level_tfs": list(level.source_tfs),
        },
    )
