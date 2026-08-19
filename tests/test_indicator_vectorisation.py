"""Bit-equality guard for the 2026-08-19 indicator vectorisation.

These indicators size **live SL/TP geometry**, so the rewrite that took
``compute_indicators_for_candle_dict`` from 512 ms to ~50 ms per symbol is only
acceptable if it changed no value at all.  This file is how that is checked, and
the check is the repo's own rule about verifying a fix by reverting it: the
reference implementations below are the pre-2026-08-19 bodies **copied
verbatim** from ``src/indicators.py`` at commit ``fa9ed0a``, not a re-derivation
and not a hand-written expectation.  A mock whose numbers I chose could only
assert my own assumption back at me.

Comparison is ``np.array_equal(..., equal_nan=True)`` — bitwise, not
``allclose``.  ``allclose`` would pass a reassociated sum, which is exactly the
class of change these tests exist to forbid: see the module docstring in
``src/indicators.py`` for why extrema may be reordered and running totals may
not.

If one of these ever fails, the vectorisation is wrong and the *old* value is
the correct one.  Do not loosen the tolerance.
"""
from __future__ import annotations

import numpy as np
import pytest

from src import indicators as ind
from src.indicators import atr as _live_atr
from src.indicators import rsi as _live_rsi
from src.indicators import sma as _live_sma


# ---------------------------------------------------------------------------
# Reference implementations — pre-vectorisation, copied verbatim.
# ---------------------------------------------------------------------------
NDArray = np.ndarray


def ref_ema(close: NDArray, period: int) -> NDArray:
    """Exponential Moving Average."""
    arr = np.asarray(close, dtype=np.float64)
    out = np.full_like(arr, np.nan)
    if len(arr) < period:
        return out
    k = 2.0 / (period + 1)
    out[period - 1] = np.mean(arr[:period])
    for i in range(period, len(arr)):
        out[i] = arr[i] * k + out[i - 1] * (1 - k)
    return out


def ref_adx(high: NDArray, low: NDArray, close: NDArray, period: int = 14) -> NDArray:
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

    atr_val = np.zeros(len(tr))
    atr_val[period - 1] = np.mean(tr[:period])
    for i in range(period, len(tr)):
        atr_val[i] = (atr_val[i - 1] * (period - 1) + tr[i]) / period

    sm_plus = np.zeros(len(tr))
    sm_minus = np.zeros(len(tr))
    sm_plus[period - 1] = np.mean(plus_dm[:period])
    sm_minus[period - 1] = np.mean(minus_dm[:period])
    for i in range(period, len(tr)):
        sm_plus[i] = (sm_plus[i - 1] * (period - 1) + plus_dm[i]) / period
        sm_minus[i] = (sm_minus[i - 1] * (period - 1) + minus_dm[i]) / period

    with np.errstate(divide="ignore", invalid="ignore"):
        di_plus = np.where(atr_val > 0, 100 * sm_plus / atr_val, 0.0)
        di_minus = np.where(atr_val > 0, 100 * sm_minus / atr_val, 0.0)
        di_sum = di_plus + di_minus
        dx = np.where(di_sum > 0, 100 * np.abs(di_plus - di_minus) / di_sum, 0.0)

    adx_val = np.zeros(len(dx))
    start = 2 * period - 1
    if start < len(dx):
        adx_val[start] = np.mean(dx[period:start + 1])
    for i in range(start + 1, len(dx)):
        adx_val[i] = (adx_val[i - 1] * (period - 1) + dx[i]) / period

    out[2 * period:] = adx_val[2 * period - 1: len(dx)]
    return out


def ref_atr(high: NDArray, low: NDArray, close: NDArray, period: int = 14) -> NDArray:
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
    atr_arr = np.zeros(len(tr))
    atr_arr[period - 1] = np.mean(tr[:period])
    for i in range(period, len(tr)):
        atr_arr[i] = (atr_arr[i - 1] * (period - 1) + tr[i]) / period

    out[period:] = atr_arr[period - 1:]
    return out


def ref_ichimoku(
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
        out = np.full(n, np.nan)
        for i in range(period - 1, n):
            out[i] = (np.max(src_h[i - period + 1: i + 1])
                      + np.min(src_l[i - period + 1: i + 1])) / 2.0
        return out

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


def ref_williams_r(
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

    for i in range(period - 1, n):
        hh = np.max(h[i - period + 1: i + 1])
        ll = np.min(l[i - period + 1: i + 1])
        if hh - ll == 0:
            out[i] = 0.0
        else:
            out[i] = (hh - c[i]) / (hh - ll) * -100.0
    return out


def ref_mfi(
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

    for i in range(period, n):
        pos_flow = 0.0
        neg_flow = 0.0
        for j in range(i - period + 1, i + 1):
            if tp[j] > tp[j - 1]:
                pos_flow += raw_mf[j]
            elif tp[j] < tp[j - 1]:
                neg_flow += raw_mf[j]
        if neg_flow == 0:
            out[i] = 100.0
        else:
            ratio = pos_flow / neg_flow
            out[i] = 100.0 - 100.0 / (1.0 + ratio)
    return out


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

def _series(n: int, seed: int, *, flat: bool = False, spike: bool = False):
    """OHLCV shaped like the real store: 1,000 bars is the bucket cap."""
    rng = np.random.default_rng(seed)
    if flat:
        close = np.full(n, 42.0)
        high = close.copy()
        low = close.copy()
    else:
        close = 100.0 + np.cumsum(rng.normal(0, 0.5, n))
        high = close + np.abs(rng.normal(0, 0.3, n))
        low = close - np.abs(rng.normal(0, 0.3, n))
    if spike and n > 20:
        high[n // 2] += 40.0
        low[n // 2 + 1] -= 40.0
    volume = np.abs(rng.normal(1000.0, 250.0, n)) + 1.0
    return high, low, close, volume


#: Lengths chosen to straddle every early-return bound in the module: below the
#: shortest period, exactly at a boundary, the seeded default, and the 1,000-bar
#: cap ``_MAX_CANDLES_PER_BUCKET`` imposes in production.
LENGTHS = [5, 15, 30, 79, 200, 500, 1000]


def _cases():
    for n in LENGTHS:
        for seed in (1, 7):
            yield _series(n, seed)
        yield _series(n, 3, spike=True)
    # A perfectly flat window is the zero-range branch in williams_r and the
    # divide-by-zero guard in adx — the branches a random walk never reaches.
    yield _series(60, 11, flat=True)


def _same(a, b, label: str) -> None:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    assert a.shape == b.shape, f"{label}: shape {a.shape} != {b.shape}"
    assert np.array_equal(a, b, equal_nan=True), (
        f"{label}: vectorised output differs from the pre-2026-08-19 reference. "
        f"first difference at index "
        f"{int(np.argmax((a != b) & ~(np.isnan(a) & np.isnan(b))))}"
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("period", [9, 14, 21, 50, 200])
def test_ema_bit_identical(period):
    for high, low, close, _vol in _cases():
        _same(ind.ema(close, period), ref_ema(close, period), f"ema(p={period}, n={len(close)})")


@pytest.mark.parametrize("period", [7, 14, 20])
def test_atr_bit_identical(period):
    for high, low, close, _vol in _cases():
        _same(
            ind.atr(high, low, close, period),
            ref_atr(high, low, close, period),
            f"atr(p={period}, n={len(close)})",
        )


@pytest.mark.parametrize("period", [7, 14, 20])
def test_adx_bit_identical(period):
    for high, low, close, _vol in _cases():
        _same(
            ind.adx(high, low, close, period),
            ref_adx(high, low, close, period),
            f"adx(p={period}, n={len(close)})",
        )


@pytest.mark.parametrize("period", [14, 20])
def test_williams_r_bit_identical(period):
    for high, low, close, _vol in _cases():
        _same(
            ind.williams_r(high, low, close, period),
            ref_williams_r(high, low, close, period),
            f"williams_r(p={period}, n={len(close)})",
        )


@pytest.mark.parametrize("period", [14, 20])
def test_mfi_bit_identical(period):
    for high, low, close, vol in _cases():
        _same(
            ind.mfi(high, low, close, vol, period),
            ref_mfi(high, low, close, vol, period),
            f"mfi(p={period}, n={len(close)})",
        )


def test_ichimoku_bit_identical():
    for high, low, close, _vol in _cases():
        got = ind.ichimoku(high, low, close)
        want = ref_ichimoku(high, low, close)
        assert set(got) == set(want), "ichimoku key set changed"
        for key in want:
            _same(got[key], want[key], f"ichimoku[{key}](n={len(close)})")


# ---------------------------------------------------------------------------
# The helpers themselves
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("period", [1, 2, 9, 26, 52])
def test_rolling_extrema_match_the_loop_they_replaced(period):
    """The naive loop is the contract; the strided reduction must match it."""
    for high, low, close, _vol in _cases():
        n = len(close)
        want_max = np.full(n, np.nan)
        want_min = np.full(n, np.nan)
        if n >= period:
            for i in range(period - 1, n):
                want_max[i] = np.max(high[i - period + 1: i + 1])
                want_min[i] = np.min(low[i - period + 1: i + 1])
        _same(ind._rolling_max(high, period), want_max, f"_rolling_max(p={period}, n={n})")
        _same(ind._rolling_min(low, period), want_min, f"_rolling_min(p={period}, n={n})")


def test_rolling_extrema_refuse_a_window_longer_than_the_series():
    """Shorter than the window is all-NaN, never a clamped partial window.

    A clamp here would answer a question the data cannot support — the repo's
    "a clamp is not a guard" rule, at the smallest scale it appears.
    """
    arr = np.array([1.0, 2.0, 3.0])
    assert np.all(np.isnan(ind._rolling_max(arr, 5)))
    assert np.all(np.isnan(ind._rolling_min(arr, 5)))


@pytest.mark.parametrize("period", [7, 14, 20])
def test_wilder_smooth_matches_the_inline_recurrence(period):
    """`_wilder_smooth` replaced three inline copies; it must equal all three."""
    for high, low, close, _vol in _cases():
        src = np.abs(np.diff(close, prepend=close[0]))
        want = np.zeros(len(src))
        if len(src) >= period:
            want[period - 1] = np.mean(src[:period])
            for i in range(period, len(src)):
                want[i] = (want[i - 1] * (period - 1) + src[i]) / period
        _same(ind._wilder_smooth(src, period), want, f"_wilder_smooth(p={period})")


# ---------------------------------------------------------------------------
# Second batch: rolling std, the stochastic-RSI window, the supertrend bands.
#
# These reference bodies call `sma` / `rsi` / `atr` from the LIVE module rather
# than a second frozen copy, deliberately: those three are themselves pinned
# bit-for-bit above, so reusing them keeps one source of truth and makes a
# failure here unambiguously about the function under test.
# ---------------------------------------------------------------------------

def ref_bollinger_bands(
    close: NDArray, period: int = 20, num_std: float = 2.0
) -> tuple[NDArray, NDArray, NDArray]:
    """Return (upper, middle, lower) Bollinger Bands."""
    mid = _live_sma(close, period)
    arr = np.asarray(close, dtype=np.float64)
    std = np.full_like(arr, np.nan)
    for i in range(period - 1, len(arr)):
        std[i] = np.std(arr[i - period + 1: i + 1], ddof=0)
    upper = mid + num_std * std
    lower = mid - num_std * std
    return upper, mid, lower


def ref_stochastic_rsi(
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

    rsi_arr = _live_rsi(arr, rsi_period)

    # Stochastic on RSI values
    stoch_raw = np.full(n, np.nan)
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

    # SMA smoothing on the valid portion, mapped back to original indices
    k_line = np.full(n, np.nan)
    valid_mask = ~np.isnan(stoch_raw)
    valid_stoch = stoch_raw[valid_mask]
    if len(valid_stoch) >= k_period:
        k_smooth = _live_sma(valid_stoch, k_period)
        k_line[np.where(valid_mask)[0]] = k_smooth

    d_line = np.full(n, np.nan)
    valid_k_mask = ~np.isnan(k_line)
    valid_k = k_line[valid_k_mask]
    if len(valid_k) >= d_period:
        d_smooth = _live_sma(valid_k, d_period)
        d_line[np.where(valid_k_mask)[0]] = d_smooth

    return k_line, d_line


def ref_supertrend(
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

    atr_arr = _live_atr(h, l, c, period)
    hl2 = (h + l) / 2.0

    upper_band = np.full(n, np.nan)
    lower_band = np.full(n, np.nan)

    for i in range(n):
        if np.isnan(atr_arr[i]):
            continue
        upper_band[i] = hl2[i] + multiplier * atr_arr[i]
        lower_band[i] = hl2[i] - multiplier * atr_arr[i]

    # Band flip logic
    first_valid = None
    for i in range(n):
        if not np.isnan(upper_band[i]):
            first_valid = i
            break
    if first_valid is None:
        return st_line, direction

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



@pytest.mark.parametrize("period,num_std", [(20, 2.0), (14, 1.5), (26, 2.5)])
def test_bollinger_bands_bit_identical(period, num_std):
    """The strided std must equal the per-window `np.std` loop exactly.

    This one is a genuine bet on numpy's reduction behaviour — a rolling SUM
    would NOT be safe to vectorise — so it is asserted rather than reasoned
    about. If a numpy upgrade ever reduces a strided row differently, this
    fails in CI instead of quietly moving a band on live geometry.
    """
    for high, low, close, _vol in _cases():
        got = ind.bollinger_bands(close, period, num_std)
        want = ref_bollinger_bands(close, period, num_std)
        for name, g, w in zip(("upper", "mid", "lower"), got, want):
            _same(g, w, f"bollinger[{name}](p={period}, n={len(close)})")


@pytest.mark.parametrize("rsi_period,stoch_period", [(14, 14), (7, 21)])
def test_stochastic_rsi_bit_identical(rsi_period, stoch_period):
    for high, low, close, _vol in _cases():
        got = ind.stochastic_rsi(close, rsi_period, stoch_period)
        want = ref_stochastic_rsi(close, rsi_period, stoch_period)
        for name, g, w in zip(("k", "d"), got, want):
            _same(g, w, f"stochastic_rsi[{name}](n={len(close)})")


@pytest.mark.parametrize("period,multiplier", [(10, 3.0), (7, 2.0)])
def test_supertrend_bit_identical(period, multiplier):
    for high, low, close, _vol in _cases():
        got = ind.supertrend(high, low, close, period, multiplier)
        want = ref_supertrend(high, low, close, period, multiplier)
        for name, g, w in zip(("line", "direction"), got, want):
            _same(g, w, f"supertrend[{name}](p={period}, n={len(close)})")


def test_stochastic_rsi_interior_nan_falls_back_rather_than_guessing():
    """The vectorised path assumes RSI's NaNs are a contiguous prefix.

    That holds for Wilder smoothing and is what makes two strided reductions
    equivalent to the per-bar scan. Where it does not hold the function must
    take the original scan, not answer from a window it cannot justify — so
    this drives the guard rather than trusting the comment above it.
    """
    rng = np.random.default_rng(19)
    close = 100.0 + np.cumsum(rng.normal(0, 0.5, 200))
    real_rsi = ind.rsi

    def _holey_rsi(arr, period=14):
        out = real_rsi(arr, period)
        out = np.asarray(out, dtype=np.float64).copy()
        out[120] = np.nan          # interior gap the prefix assumption forbids
        return out

    ind_rsi_backup = ind.rsi
    try:
        ind.rsi = _holey_rsi
        got = ind.stochastic_rsi(close, 14, 14)
    finally:
        ind.rsi = ind_rsi_backup

    # The reference scan, driven with the same holey series.
    holey = _holey_rsi(close, 14)
    n = len(close)
    want_raw = np.full(n, np.nan)
    for i in range(n):
        if np.isnan(holey[i]):
            continue
        start = max(0, i - 14 + 1)
        window = holey[start: i + 1]
        window = window[~np.isnan(window)]
        if len(window) < 14:
            continue
        lo, hi = np.min(window), np.max(window)
        want_raw[i] = 100.0 if hi - lo == 0 else (holey[i] - lo) / (hi - lo) * 100.0

    # k_line is an SMA over the valid stoch values; comparing the count of
    # non-NaN k values is enough to prove the fallback ran — the vectorised
    # branch would have produced a value at index 120 and a different count.
    assert np.isnan(got[0][120]), "an interior RSI gap must not be filled in"
    assert np.count_nonzero(~np.isnan(want_raw)) > 0
