"""Technical indicators used across all channels.

All functions accept numpy arrays (or lists) and return numpy arrays.
They are pure-compute, no I/O.

Performance, and why it is a correctness constraint here (2026-08-19)
────────────────────────────────────────────────────────────────────
This module is the engine's single largest CPU consumer.  ``_load_candles``
hands the scanner up to 1,000 bars per timeframe and
``compute_indicators_for_candle_dict`` runs the whole set over all seven, per
symbol, per scan cycle.  Profiled at **512 ms per symbol** — ×79 symbols is
40s of one scan cycle, against a 15s target and a 120s healthcheck deadline
past which autoheal restarts the container.  So a slow indicator is not a
tuning question; it is what was killing the engine.

The cost was never where it looked.  ``ema`` accounted for 3% of a profile;
**rolling max/min written as Python loops calling ``np.max`` on a slice per
bar** accounted for most of it — ``ichimoku`` alone issued 195,000 ufunc calls
per symbol.  ``_rolling_max`` / ``_rolling_min`` below replace those with one
strided reduction.

**Every rewrite in this module is bit-identical to the implementation it
replaced, and that is asserted rather than asserted-to.**
``tests/test_indicator_vectorisation.py`` carries the pre-2026-08-19 code
verbatim as its reference and compares with ``array_equal(..., equal_nan=True)``
over randomised inputs.  Two rules follow from it, and both are load-bearing
because these values size live SL/TP geometry:

* **Reductions that are exact may be reordered; sums may not.**  ``max`` and
  ``min`` over a window are order-independent in IEEE-754, so a strided
  reduction returns the same bits as a Python loop.  A *sum* does not —
  numpy pairwise-sums anything over 8 elements — so every running total here
  keeps its original accumulation order and is sped up by running the same
  arithmetic on Python floats instead of numpy scalars (3-10x, same bits).
* **A first-order recurrence stays a recurrence.**  The closed form for
  ``y[i] = a·y[i-1] + b[i]`` needs ``a**-i`` and overflows on the shorter
  periods, and it reassociates.  ``.tolist()`` then a plain loop is the win
  that costs nothing.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray


# ---------------------------------------------------------------------------
# Rolling-window extrema
# ---------------------------------------------------------------------------

def _rolling_max(arr: NDArray, period: int) -> NDArray:
    """Max over every trailing window of ``period``, right-aligned.

    ``out[i] = max(arr[i - period + 1 : i + 1])`` for ``i >= period - 1``, NaN
    before that — the exact contract of the per-bar ``np.max(slice)`` loops
    this replaces, and bit-identical to them because ``max`` is exact and
    order-independent.

    One strided reduction instead of ``n`` ufunc dispatches: measured ~150x on
    a 1,000-bar array, which is where most of this module's cost lived.
    """
    n = len(arr)
    out = np.full(n, np.nan)
    if period <= 0 or n < period:
        return out
    windows = np.lib.stride_tricks.sliding_window_view(arr, period)
    out[period - 1:] = windows.max(axis=-1)
    return out


def _rolling_min(arr: NDArray, period: int) -> NDArray:
    """Min over every trailing window of ``period``, right-aligned.

    Mirror of :func:`_rolling_max`; see its docstring for why this is safe to
    vectorise where a rolling *sum* would not be.
    """
    n = len(arr)
    out = np.full(n, np.nan)
    if period <= 0 or n < period:
        return out
    windows = np.lib.stride_tricks.sliding_window_view(arr, period)
    out[period - 1:] = windows.min(axis=-1)
    return out


def _wilder_smooth(src: NDArray, period: int) -> NDArray:
    """Wilder's smoothing: ``y[i] = (y[i-1]·(p-1) + x[i]) / p``.

    Seeded with the simple mean of the first ``period`` values, zeros before
    that — the shape ADX and ATR both wrote inline three times over.

    Deliberately *not* vectorised into a closed form.  This is a first-order
    IIR whose analytic solution needs ``((p-1)/p)**-i``, which overflows well
    inside a 1,000-bar window, and which reassociates the arithmetic — and
    these values size live SL/TP geometry, so a last-bit difference is a
    different stop.  The win is running the identical recurrence on Python
    floats instead of numpy scalars: same bits, ~3.5x less time.
    """
    n = len(src)
    out = np.zeros(n)
    if n < period or period <= 0:
        return out
    seed = float(np.mean(src[:period]))
    out[period - 1] = seed
    values = src.tolist()
    prev = seed
    smoothed = []
    for i in range(period, n):
        prev = (prev * (period - 1) + values[i]) / period
        smoothed.append(prev)
    if smoothed:
        out[period:] = smoothed
    return out


# ---------------------------------------------------------------------------
# Moving averages
# ---------------------------------------------------------------------------

def ema(close: NDArray, period: int) -> NDArray:
    """Exponential Moving Average."""
    arr = np.asarray(close, dtype=np.float64)
    out = np.full_like(arr, np.nan)
    if len(arr) < period:
        return out
    k = 2.0 / (period + 1)
    one_minus_k = 1 - k
    # Same recurrence, same operation order, on Python floats rather than
    # numpy scalars — every `arr[i]` above allocated a 0-d array. Bit-identical
    # (both are IEEE-754 doubles and nothing is reassociated), ~3.5x faster.
    src = arr.tolist()
    prev = float(np.mean(arr[:period]))
    vals = [prev]
    for i in range(period, len(arr)):
        prev = src[i] * k + prev * one_minus_k
        vals.append(prev)
    out[period - 1:] = vals
    return out


def sma(close: NDArray, period: int) -> NDArray:
    """Simple Moving Average."""
    arr = np.asarray(close, dtype=np.float64)
    out = np.full_like(arr, np.nan)
    if len(arr) < period:
        return out
    cumsum = np.cumsum(arr)
    cumsum[period:] = cumsum[period:] - cumsum[:-period]
    out[period - 1:] = cumsum[period - 1:] / period
    return out


# ---------------------------------------------------------------------------
# ADX (Average Directional Index)
# ---------------------------------------------------------------------------

def adx(high: NDArray, low: NDArray, close: NDArray, period: int = 14) -> NDArray:
    """Average Directional Index (Wilder smoothing)."""
    h = np.asarray(high, dtype=np.float64)
    l = np.asarray(low, dtype=np.float64)
    c = np.asarray(close, dtype=np.float64)
    n = len(c)
    out = np.full(n, np.nan)
    if n < period * 2:
        return out

    tr = np.maximum(h[1:] - l[1:],
                     np.maximum(np.abs(h[1:] - c[:-1]),
                                np.abs(l[1:] - c[:-1])))
    up_move = h[1:] - h[:-1]
    dn_move = l[:-1] - l[1:]
    plus_dm = np.where((up_move > dn_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((dn_move > up_move) & (dn_move > 0), dn_move, 0.0)

    # Three Wilder recurrences, same arithmetic, on Python floats — see `ema`.
    atr_val = _wilder_smooth(tr, period)
    sm_plus = _wilder_smooth(plus_dm, period)
    sm_minus = _wilder_smooth(minus_dm, period)

    with np.errstate(divide="ignore", invalid="ignore"):
        di_plus = np.where(atr_val > 0, 100 * sm_plus / atr_val, 0.0)
        di_minus = np.where(atr_val > 0, 100 * sm_minus / atr_val, 0.0)
        di_sum = di_plus + di_minus
        dx = np.where(di_sum > 0, 100 * np.abs(di_plus - di_minus) / di_sum, 0.0)

    adx_val = np.zeros(len(dx))
    start = 2 * period - 1
    if start < len(dx):
        adx_val[start] = np.mean(dx[period:start + 1])
        _dx = dx.tolist()
        _prev = float(adx_val[start])
        _vals = []
        for i in range(start + 1, len(dx)):
            _prev = (_prev * (period - 1) + _dx[i]) / period
            _vals.append(_prev)
        if _vals:
            adx_val[start + 1:] = _vals

    out[2 * period:] = adx_val[2 * period - 1: len(dx)]
    return out


# ---------------------------------------------------------------------------
# ATR (Average True Range)
# ---------------------------------------------------------------------------

def atr(high: NDArray, low: NDArray, close: NDArray, period: int = 14) -> NDArray:
    """Average True Range (Wilder smoothing)."""
    h = np.asarray(high, dtype=np.float64)
    l = np.asarray(low, dtype=np.float64)
    c = np.asarray(close, dtype=np.float64)
    n = len(c)
    out = np.full(n, np.nan)
    if n < period + 1:
        return out

    tr = np.maximum(h[1:] - l[1:],
                     np.maximum(np.abs(h[1:] - c[:-1]),
                                np.abs(l[1:] - c[:-1])))
    atr_arr = _wilder_smooth(tr, period)

    out[period:] = atr_arr[period - 1:]
    return out


# ---------------------------------------------------------------------------
# RSI (Relative Strength Index)
# ---------------------------------------------------------------------------

def rsi(close: NDArray, period: int = 14) -> NDArray:
    """Relative Strength Index (Wilder smoothing)."""
    arr = np.asarray(close, dtype=np.float64)
    n = len(arr)
    out = np.full(n, np.nan)
    if n < period + 1:
        return out

    deltas = np.diff(arr)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            out[i + 1] = 100.0
        else:
            rs = avg_gain / avg_loss
            out[i + 1] = 100.0 - 100.0 / (1.0 + rs)
    # First valid RSI value
    if avg_loss == 0:
        out[period] = 100.0
    else:
        out[period] = 100.0 - 100.0 / (1.0 + np.mean(gains[:period]) / max(np.mean(losses[:period]), 1e-10))
    return out


# ---------------------------------------------------------------------------
# MACD (Moving Average Convergence Divergence)
# ---------------------------------------------------------------------------

def macd(
    close: NDArray,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> tuple[NDArray, NDArray, NDArray]:
    """MACD (Moving Average Convergence Divergence).

    Computes the MACD line (fast EMA − slow EMA), the signal line (EMA of
    the MACD line), and the histogram (MACD − signal).

    Parameters
    ----------
    close:
        Array of closing prices.
    fast_period:
        Period for the fast EMA (default 12).
    slow_period:
        Period for the slow EMA (default 26).
    signal_period:
        Period for the signal-line EMA (default 9).

    Returns
    -------
    tuple[NDArray, NDArray, NDArray]
        ``(macd_line, signal_line, histogram)`` – all the same length as
        *close*.  Elements are ``NaN`` until enough data is available.
    """
    arr = np.asarray(close, dtype=np.float64)
    n = len(arr)
    nan_out = np.full(n, np.nan)

    if n < slow_period:
        return nan_out.copy(), nan_out.copy(), nan_out.copy()

    fast_ema = ema(arr, fast_period)
    slow_ema = ema(arr, slow_period)
    macd_line = fast_ema - slow_ema  # NaN wherever slow_ema is NaN

    # Compute signal line as EMA of the valid portion of macd_line
    signal_line = np.full(n, np.nan)
    valid_mask = ~np.isnan(macd_line)
    valid_macd = macd_line[valid_mask]
    if len(valid_macd) >= signal_period:
        sig = ema(valid_macd, signal_period)
        # Map back to original indices
        indices = np.where(valid_mask)[0]
        signal_line[indices] = sig

    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


# ---------------------------------------------------------------------------
# Bollinger Bands
# ---------------------------------------------------------------------------

def bollinger_bands(
    close: NDArray, period: int = 20, num_std: float = 2.0
) -> tuple[NDArray, NDArray, NDArray]:
    """Return (upper, middle, lower) Bollinger Bands."""
    mid = sma(close, period)
    arr = np.asarray(close, dtype=np.float64)
    # One strided reduction instead of ~1,000 `np.std` dispatches per call.
    # Unlike a rolling SUM this is safe to vectorise only because numpy runs
    # the identical per-window algorithm either way — asserted bit-for-bit in
    # tests/test_indicator_vectorisation.py against the loop below, so a numpy
    # version that ever reduced a strided row differently fails CI rather than
    # silently moving a band.
    std = np.full_like(arr, np.nan)
    if len(arr) >= period:
        _w = np.lib.stride_tricks.sliding_window_view(arr, period)
        std[period - 1:] = _w.std(axis=-1, ddof=0)
    upper = mid + num_std * std
    lower = mid - num_std * std
    return upper, mid, lower


# ---------------------------------------------------------------------------
# Volume Delta (simple tick-level approximation)
# ---------------------------------------------------------------------------

def volume_delta(buy_vol: NDArray, sell_vol: NDArray) -> NDArray:
    """Cumulative Volume Delta."""
    return np.cumsum(np.asarray(buy_vol, dtype=np.float64)
                     - np.asarray(sell_vol, dtype=np.float64))


# ---------------------------------------------------------------------------
# Momentum (% change over N candles)
# ---------------------------------------------------------------------------

def momentum(close: NDArray, n: int = 3) -> NDArray:
    """Percentage change over *n* candles."""
    arr = np.asarray(close, dtype=np.float64)
    out = np.full_like(arr, np.nan)
    if len(arr) <= n:
        return out
    with np.errstate(divide="ignore", invalid="ignore"):
        out[n:] = (arr[n:] - arr[:-n]) / arr[:-n] * 100.0
    return out


# ---------------------------------------------------------------------------
# Stochastic RSI
# ---------------------------------------------------------------------------

def stochastic_rsi(
    close: NDArray,
    rsi_period: int = 14,
    stoch_period: int = 14,
    k_period: int = 3,
    d_period: int = 3,
) -> tuple[NDArray, NDArray]:
    """Stochastic RSI oscillator.

    Computes RSI first, then applies the stochastic oscillator formula
    on the RSI values.

    Parameters
    ----------
    close : NDArray
        Array of closing prices.
    rsi_period : int
        Look-back for the RSI calculation (default 14).
    stoch_period : int
        Look-back for the stochastic min/max window (default 14).
    k_period : int
        SMA smoothing period for the %K line (default 3).
    d_period : int
        SMA smoothing period for the %D line (default 3).

    Returns
    -------
    tuple[NDArray, NDArray]
        ``(k_line, d_line)`` scaled 0-100.
    """
    arr = np.asarray(close, dtype=np.float64)
    n = len(arr)
    nan_out = np.full(n, np.nan)
    if n < rsi_period + stoch_period:
        return nan_out.copy(), nan_out.copy()

    rsi_arr = rsi(arr, rsi_period)

    # Stochastic on RSI values
    # RSI's NaNs are a contiguous PREFIX — Wilder smoothing produces a value
    # for every bar after its seed — so "the window holds stoch_period non-NaN
    # values" is exactly "the window starts at or after the first valid RSI".
    # That equivalence is what makes the per-bar min/max loop replaceable by
    # two strided reductions over the valid tail; it would NOT hold for a
    # series with interior gaps, which is why the guard below is explicit
    # rather than assumed.
    stoch_raw = np.full(n, np.nan)
    _valid_idx = np.flatnonzero(~np.isnan(rsi_arr))
    if len(_valid_idx) >= stoch_period:
        _first = int(_valid_idx[0])
        _tail = rsi_arr[_first:]
        if np.isnan(_tail).any():
            # Interior NaN: fall back to the original per-bar scan rather than
            # answer a question the vectorised form cannot ask.
            for i in range(n):
                if np.isnan(rsi_arr[i]):
                    continue
                start = max(0, i - stoch_period + 1)
                window = rsi_arr[start: i + 1]
                window = window[~np.isnan(window)]
                if len(window) < stoch_period:
                    continue
                rsi_low = np.min(window)
                rsi_high = np.max(window)
                if rsi_high - rsi_low == 0:
                    stoch_raw[i] = 100.0
                else:
                    stoch_raw[i] = (rsi_arr[i] - rsi_low) / (rsi_high - rsi_low) * 100.0
        else:
            _hi = _rolling_max(_tail, stoch_period)
            _lo = _rolling_min(_tail, stoch_period)
            _rng = _hi - _lo
            with np.errstate(divide="ignore", invalid="ignore"):
                _vals = np.where(
                    _rng == 0, 100.0, (_tail - _lo) / _rng * 100.0
                )
            _vals[: stoch_period - 1] = np.nan
            stoch_raw[_first:] = _vals

    # SMA smoothing on the valid portion, mapped back to original indices
    k_line = np.full(n, np.nan)
    valid_mask = ~np.isnan(stoch_raw)
    valid_stoch = stoch_raw[valid_mask]
    if len(valid_stoch) >= k_period:
        k_smooth = sma(valid_stoch, k_period)
        k_line[np.where(valid_mask)[0]] = k_smooth

    d_line = np.full(n, np.nan)
    valid_k_mask = ~np.isnan(k_line)
    valid_k = k_line[valid_k_mask]
    if len(valid_k) >= d_period:
        d_smooth = sma(valid_k, d_period)
        d_line[np.where(valid_k_mask)[0]] = d_smooth

    return k_line, d_line


# ---------------------------------------------------------------------------
# Supertrend
# ---------------------------------------------------------------------------

def supertrend(
    high: NDArray,
    low: NDArray,
    close: NDArray,
    period: int = 10,
    multiplier: float = 3.0,
) -> tuple[NDArray, NDArray]:
    """Supertrend indicator.

    Parameters
    ----------
    high, low, close : NDArray
        Price arrays.
    period : int
        ATR look-back period (default 10).
    multiplier : float
        ATR multiplier for band width (default 3.0).

    Returns
    -------
    tuple[NDArray, NDArray]
        ``(supertrend_line, direction)`` where direction is 1.0 (UP)
        or -1.0 (DOWN).
    """
    h = np.asarray(high, dtype=np.float64)
    l = np.asarray(low, dtype=np.float64)
    c = np.asarray(close, dtype=np.float64)
    n = len(c)
    st_line = np.full(n, np.nan)
    direction = np.full(n, np.nan)
    if n < period + 1:
        return st_line, direction

    atr_arr = atr(h, l, c, period)
    hl2 = (h + l) / 2.0

    # Elementwise, and NaN propagates on its own where ATR has none — the
    # skip-if-NaN loop this replaces produced the identical array.
    upper_band = hl2 + multiplier * atr_arr
    lower_band = hl2 - multiplier * atr_arr

    # Band flip logic
    _valid = np.flatnonzero(~np.isnan(upper_band))
    if len(_valid) == 0:
        return st_line, direction
    first_valid = int(_valid[0])

    # Initialize at first valid index
    direction[first_valid] = 1.0
    st_line[first_valid] = lower_band[first_valid]

    for i in range(first_valid + 1, n):
        if np.isnan(upper_band[i]):
            continue

        # Adjust bands based on previous bands
        if lower_band[i] > lower_band[i - 1] or c[i - 1] < lower_band[i - 1]:
            pass  # keep current lower_band[i]
        else:
            lower_band[i] = lower_band[i - 1]

        if upper_band[i] < upper_band[i - 1] or c[i - 1] > upper_band[i - 1]:
            pass  # keep current upper_band[i]
        else:
            upper_band[i] = upper_band[i - 1]

        # Direction logic
        prev_dir = direction[i - 1] if not np.isnan(direction[i - 1]) else 1.0
        if prev_dir == 1.0:
            if c[i] < lower_band[i]:
                direction[i] = -1.0
                st_line[i] = upper_band[i]
            else:
                direction[i] = 1.0
                st_line[i] = lower_band[i]
        else:
            if c[i] > upper_band[i]:
                direction[i] = 1.0
                st_line[i] = lower_band[i]
            else:
                direction[i] = -1.0
                st_line[i] = upper_band[i]

    return st_line, direction


# ---------------------------------------------------------------------------
# Ichimoku Cloud
# ---------------------------------------------------------------------------

def ichimoku(
    high: NDArray,
    low: NDArray,
    close: NDArray,
    tenkan: int = 9,
    kijun: int = 26,
    senkou_b: int = 52,
) -> dict[str, NDArray]:
    """Ichimoku Cloud components.

    Parameters
    ----------
    high, low, close : NDArray
        Price arrays.
    tenkan : int
        Tenkan-sen (conversion line) period (default 9).
    kijun : int
        Kijun-sen (base line) period (default 26).
    senkou_b : int
        Senkou Span B period (default 52).

    Returns
    -------
    dict
        Keys: ``tenkan_sen``, ``kijun_sen``, ``senkou_span_a``,
        ``senkou_span_b``.  All same length as input.
    """
    h = np.asarray(high, dtype=np.float64)
    l = np.asarray(low, dtype=np.float64)
    _c = np.asarray(close, dtype=np.float64)
    n = len(_c)

    def _donchian_mid(src_h: NDArray, src_l: NDArray, period: int) -> NDArray:
        # Was a per-bar `np.max(slice)` + `np.min(slice)` loop — three calls
        # here at periods 9/26/52 issued ~195,000 ufunc dispatches per symbol
        # and were the single largest cost in this module. Bit-identical:
        # extrema are exact and order-independent.
        return (_rolling_max(src_h, period) + _rolling_min(src_l, period)) / 2.0

    tenkan_sen = _donchian_mid(h, l, tenkan)
    kijun_sen = _donchian_mid(h, l, kijun)

    # Senkou Span A = (tenkan + kijun) / 2, shifted forward kijun periods
    span_a_raw = np.full(n, np.nan)
    valid = ~(np.isnan(tenkan_sen) | np.isnan(kijun_sen))
    span_a_raw[valid] = (tenkan_sen[valid] + kijun_sen[valid]) / 2.0
    senkou_span_a = np.full(n, np.nan)
    for i in range(n):
        if not np.isnan(span_a_raw[i]) and i + kijun < n:
            senkou_span_a[i + kijun] = span_a_raw[i]

    # Senkou Span B = donchian mid over senkou_b, shifted forward kijun periods
    span_b_raw = _donchian_mid(h, l, senkou_b)
    senkou_span_b = np.full(n, np.nan)
    for i in range(n):
        if not np.isnan(span_b_raw[i]) and i + kijun < n:
            senkou_span_b[i + kijun] = span_b_raw[i]

    return {
        "tenkan_sen": tenkan_sen,
        "kijun_sen": kijun_sen,
        "senkou_span_a": senkou_span_a,
        "senkou_span_b": senkou_span_b,
    }


# ---------------------------------------------------------------------------
# Heikin-Ashi
# ---------------------------------------------------------------------------

def heikin_ashi(
    open_arr: NDArray,
    high: NDArray,
    low: NDArray,
    close: NDArray,
) -> tuple[NDArray, NDArray, NDArray, NDArray]:
    """Heikin-Ashi candlestick values.

    Parameters
    ----------
    open_arr, high, low, close : NDArray
        Standard OHLC arrays.

    Returns
    -------
    tuple[NDArray, NDArray, NDArray, NDArray]
        ``(ha_open, ha_high, ha_low, ha_close)``
    """
    o = np.asarray(open_arr, dtype=np.float64)
    h = np.asarray(high, dtype=np.float64)
    l = np.asarray(low, dtype=np.float64)
    c = np.asarray(close, dtype=np.float64)
    n = len(c)

    ha_close = (o + h + l + c) / 4.0
    ha_open = np.empty(n, dtype=np.float64)
    ha_open[0] = o[0]
    for i in range(1, n):
        ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0

    ha_high = np.maximum(h, np.maximum(ha_open, ha_close))
    ha_low = np.minimum(l, np.minimum(ha_open, ha_close))

    return ha_open, ha_high, ha_low, ha_close


# ---------------------------------------------------------------------------
# Volume Profile
# ---------------------------------------------------------------------------

def volume_profile(
    close: NDArray,
    volume: NDArray,
    num_bins: int = 20,
) -> dict[str, Any]:
    """Volume Profile with Point of Control and Value Area.

    Parameters
    ----------
    close : NDArray
        Array of closing prices.
    volume : NDArray
        Array of volume values.
    num_bins : int
        Number of price bins (default 20).

    Returns
    -------
    dict
        Keys: ``poc`` (float), ``vah`` (float), ``val`` (float),
        ``profile`` (NDArray), ``bin_edges`` (NDArray).
    """
    c = np.asarray(close, dtype=np.float64)
    v = np.asarray(volume, dtype=np.float64)
    n = len(c)

    if n == 0 or np.all(v == 0):
        return {
            "poc": np.nan,
            "vah": np.nan,
            "val": np.nan,
            "profile": np.array([], dtype=np.float64),
            "bin_edges": np.array([], dtype=np.float64),
        }

    price_min, price_max = float(np.nanmin(c)), float(np.nanmax(c))
    if price_min == price_max:
        return {
            "poc": price_min,
            "vah": price_min,
            "val": price_min,
            "profile": np.array([float(np.nansum(v))], dtype=np.float64),
            "bin_edges": np.array([price_min, price_max], dtype=np.float64),
        }

    bin_edges = np.linspace(price_min, price_max, num_bins + 1)
    profile = np.zeros(num_bins, dtype=np.float64)
    bin_indices = np.digitize(c, bin_edges) - 1
    bin_indices = np.clip(bin_indices, 0, num_bins - 1)
    for i in range(n):
        profile[bin_indices[i]] += v[i]

    # Point of Control – price level (bin mid) with highest volume
    poc_idx = int(np.argmax(profile))
    poc = (bin_edges[poc_idx] + bin_edges[poc_idx + 1]) / 2.0

    # Value Area – 70 % of total volume centered around POC
    total_vol = float(np.sum(profile))
    target_vol = total_vol * 0.70
    va_vol = profile[poc_idx]
    lo_idx, hi_idx = poc_idx, poc_idx
    while va_vol < target_vol and (lo_idx > 0 or hi_idx < num_bins - 1):
        expand_lo = profile[lo_idx - 1] if lo_idx > 0 else 0.0
        expand_hi = profile[hi_idx + 1] if hi_idx < num_bins - 1 else 0.0
        if expand_lo >= expand_hi and lo_idx > 0:
            lo_idx -= 1
            va_vol += profile[lo_idx]
        elif hi_idx < num_bins - 1:
            hi_idx += 1
            va_vol += profile[hi_idx]
        else:
            lo_idx -= 1
            va_vol += profile[lo_idx]

    val = (bin_edges[lo_idx] + bin_edges[lo_idx + 1]) / 2.0
    vah = (bin_edges[hi_idx] + bin_edges[hi_idx + 1]) / 2.0

    return {
        "poc": float(poc),
        "vah": float(vah),
        "val": float(val),
        "profile": profile,
        "bin_edges": bin_edges,
    }


# ---------------------------------------------------------------------------
# Keltner Channels
# ---------------------------------------------------------------------------

def keltner_channels(
    high: NDArray,
    low: NDArray,
    close: NDArray,
    ema_period: int = 20,
    atr_period: int = 10,
    multiplier: float = 2.0,
) -> tuple[NDArray, NDArray, NDArray]:
    """Keltner Channels (EMA ± multiplier × ATR).

    Parameters
    ----------
    high, low, close : NDArray
        Price arrays.
    ema_period : int
        Period for the middle EMA line (default 20).
    atr_period : int
        Period for ATR (default 10).
    multiplier : float
        ATR multiplier for channel width (default 2.0).

    Returns
    -------
    tuple[NDArray, NDArray, NDArray]
        ``(upper, middle, lower)``
    """
    c = np.asarray(close, dtype=np.float64)
    h = np.asarray(high, dtype=np.float64)
    l = np.asarray(low, dtype=np.float64)
    n = len(c)
    nan_out = np.full(n, np.nan)
    if n < max(ema_period, atr_period + 1):
        return nan_out.copy(), nan_out.copy(), nan_out.copy()

    middle = ema(c, ema_period)
    atr_arr = atr(h, l, c, atr_period)
    upper = middle + multiplier * atr_arr
    lower = middle - multiplier * atr_arr
    return upper, middle, lower


# ---------------------------------------------------------------------------
# Williams %R
# ---------------------------------------------------------------------------

def williams_r(
    high: NDArray,
    low: NDArray,
    close: NDArray,
    period: int = 14,
) -> NDArray:
    """Williams %R oscillator (range -100 to 0).

    Parameters
    ----------
    high, low, close : NDArray
        Price arrays.
    period : int
        Look-back period (default 14).

    Returns
    -------
    NDArray
        Williams %R values, NaN-padded for insufficient data.
    """
    h = np.asarray(high, dtype=np.float64)
    l = np.asarray(low, dtype=np.float64)
    c = np.asarray(close, dtype=np.float64)
    n = len(c)
    out = np.full(n, np.nan)
    if n < period:
        return out

    # Same per-bar extrema loop as ichimoku's, same fix. The zero-range branch
    # is preserved exactly: a flat window scores 0.0, not a divide-by-zero.
    hh = _rolling_max(h, period)
    ll = _rolling_min(l, period)
    rng = hh - ll
    with np.errstate(divide="ignore", invalid="ignore"):
        vals = np.where(rng == 0, 0.0, (hh - c) / rng * -100.0)
    out[period - 1:] = vals[period - 1:]
    return out


# ---------------------------------------------------------------------------
# Money Flow Index (MFI)
# ---------------------------------------------------------------------------

def mfi(
    high: NDArray,
    low: NDArray,
    close: NDArray,
    volume: NDArray,
    period: int = 14,
) -> NDArray:
    """Money Flow Index (volume-weighted RSI).

    Parameters
    ----------
    high, low, close, volume : NDArray
        Price and volume arrays.
    period : int
        Look-back period (default 14).

    Returns
    -------
    NDArray
        MFI values (0-100), NaN-padded for insufficient data.
    """
    h = np.asarray(high, dtype=np.float64)
    l = np.asarray(low, dtype=np.float64)
    c = np.asarray(close, dtype=np.float64)
    v = np.asarray(volume, dtype=np.float64)
    n = len(c)
    out = np.full(n, np.nan)
    if n < period + 1:
        return out

    tp = (h + l + c) / 3.0
    raw_mf = tp * v

    # The window sums keep their original left-to-right accumulation order —
    # a strided `.sum(axis=-1)` would pairwise-sum and change the last bits.
    # What is removed is the numpy-scalar indexing: `tp[j]` allocated a 0-d
    # array on every one of the n x period inner steps. Same arithmetic, same
    # order, Python floats; measured ~8x.
    _tp = tp.tolist()
    _mf = raw_mf.tolist()
    for i in range(period, n):
        pos_flow = 0.0
        neg_flow = 0.0
        for j in range(i - period + 1, i + 1):
            if _tp[j] > _tp[j - 1]:
                pos_flow += _mf[j]
            elif _tp[j] < _tp[j - 1]:
                neg_flow += _mf[j]
        if neg_flow == 0:
            out[i] = 100.0
        else:
            ratio = pos_flow / neg_flow
            out[i] = 100.0 - 100.0 / (1.0 + ratio)
    return out


# ---------------------------------------------------------------------------
# Hurst exponent (rescaled-range / R/S analysis)
# ---------------------------------------------------------------------------

def hurst_exponent(close: NDArray, min_lag: int = 2, max_lag: int = 20) -> float:
    """Estimate the Hurst exponent of a price series via the lag-variance method.

    The Hurst exponent ``H`` distinguishes *persistence* from *mean reversion*,
    which ADX cannot: ADX measures trend strength but rises in choppy markets
    with large alternating candles, so a high-ADX reading can be a reversal in
    progress rather than a real trend.

    Interpretation:

    * ``H > 0.55`` — persistent / trending (moves tend to continue)
    * ``0.45 <= H <= 0.55`` — random walk (no edge either way)
    * ``H < 0.45`` — mean-reverting / ranging (moves tend to reverse)

    Implementation uses the generalised-Hurst lag method: for a set of lags,
    measure the standard deviation of lagged differences and fit a line in
    log-log space.  The slope is the Hurst exponent.  This is O(n·k) for ``k``
    lags and runs in well under a millisecond for the 50-bar windows used on
    the 15s scan cycle.

    Parameters
    ----------
    close:
        Array of closing prices.  At least ``2 * max_lag`` samples are needed
        for a stable estimate; fewer returns ``0.5`` (random-walk / no-signal).
    min_lag, max_lag:
        Range of lags to regress over.  Defaults (2..20) suit intraday 5m data.

    Returns
    -------
    float
        Estimated Hurst exponent, clamped to ``[0.0, 1.0]``.  Returns ``0.5``
        when the series is too short or degenerate (flat / NaN), so callers can
        treat ``0.5`` as "no regime opinion".
    """
    arr = np.asarray(close, dtype=np.float64)
    arr = arr[~np.isnan(arr)]
    n = len(arr)
    if n < 2 * max_lag or n < 4:
        return 0.5
    # Clamp max_lag so we always have at least a few points per lag.
    hi = min(max_lag, n // 2)
    lo = max(2, min_lag)
    if hi <= lo:
        return 0.5

    lags = np.arange(lo, hi)
    tau = []
    valid_lags = []
    for lag in lags:
        diff = arr[lag:] - arr[:-lag]
        sd = float(np.std(diff))
        if sd > 0.0:
            tau.append(sd)
            valid_lags.append(int(lag))
    if len(valid_lags) < 2:
        return 0.5

    log_lags = np.log(np.asarray(valid_lags, dtype=np.float64))
    log_tau = np.log(np.asarray(tau, dtype=np.float64))
    # Slope of log(tau) vs log(lag) is the Hurst exponent.
    try:
        slope = float(np.polyfit(log_lags, log_tau, 1)[0])
    except (np.linalg.LinAlgError, ValueError):
        return 0.5
    if not np.isfinite(slope):
        return 0.5
    return max(0.0, min(1.0, slope))
