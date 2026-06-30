"""Graded BTC-State soft-confirmation — the engine for the counter-trend-long fix.

Doctrine (OWNER_BRIEF §2.1, ACTIVE_CONTEXT Session 38): alts couple to BTC
*harder on the downside than the upside*.  When BTC is in a macro downtrend a
counter-trend LONG on a BTC-led alt gets steamrolled, while the same setup on the
SHORT side works.  Live data (305-signal window): LONG −25.1% (34% win) vs SHORT
+9.65% (46% win); cutting the three counter-trend reversal-LONG cohorts flipped the
book from −15% to +29% on the same window.

This module SUBSUMES two coarser predecessors:
  * ``src.btc_direction.check_btc_direction_gate`` — binary, fires only when BTC 1H
    AND 4H *both* oppose, so it is silent during relief bounces / TRENDING_UP where
    our longs actually bled.
  * ``src.correlation.correlation_confidence_penalty`` — correlation *magnitude*
    only, direction-blind (penalises high-corr regardless of which way BTC moves).

The replacement is a **graded** read, three layers:

  1. ``compute_btc_state``  → ``b ∈ [−1, +1]`` — how hostile BTC is *right now*
     (−1 = falling hard, +1 = rising hard), from a multi-TF EMA stack + ATR-
     normalised slope + RSI, vol-shrunk in chop.
  2. ``compute_downside_coupling`` → ``w_pair ∈ [0, 1]`` — how hard *this pair*
     follows BTC *down* (downside-beta × downside-corr).  Decoupled pairs ≈ 0
     and are auto-exempt; the exemption is revoked the instant BTC dumps because
     ``w_pair`` is recomputed every dispatch.
  3. ``compute_haircut_factor`` → ``factor ∈ [floor, 1]`` — a confidence multiplier
     applied **only to the side that is counter to BTC-State**
     (``factor = 1 − k·|b|·w_pair·A_side``), with the counter-trend LONG penalised
     ~2× the counter-trend SHORT (the downside asymmetry) and the worst reversal
     setups weighted hardest.  Floored so it never zeroes a signal, and — because
     it is recomputed from ``b`` every dispatch — it **auto-restores longs the
     moment BTC turns up**.

PURE + SELF-CONTAINED: every function computes its own EMA / RSI / ATR from raw
candle arrays so the whole module is deterministically unit-testable with no
network and no indicator-engine dependency.  All functions fail toward the neutral
no-op (``b=0`` / ``w_pair=0`` / ``factor=1``) on missing or degenerate data — a
graded soft-confirmation never blocks on thin data.

STEP 1 (dark): the scanner *computes and stamps* ``b`` / ``w_pair`` / ``factor`` on
every signal and shadow-logs the would-be effect, but only *applies* the haircut
when ``BTC_STATE_HAIRCUT_ENABLED`` is true (default OFF).  Activation is owner-
sign-off after the shadow window + backfill confirm.
"""
from __future__ import annotations

from typing import Dict, Optional, Sequence

import numpy as np

# Counter-trend reversal/continuation setups that carry the bleed on the LONG side
# (ACTIVE_CONTEXT S37/S38): SR_FLIP_RETEST long −21.75%, MOVER_TREND_PULLBACK long
# −12.78%, LIQUIDITY_SWEEP_REVERSAL long −10.19%.  These get the full haircut weight;
# other setups that happen to sit counter to BTC-State get a gentler one.
DEFAULT_SEVERE_SETUPS: frozenset[str] = frozenset({
    "SR_FLIP_RETEST",
    "LIQUIDITY_SWEEP_REVERSAL",
    "MOVER_TREND_PULLBACK",
})

# Per-timeframe weight in the composite BTC-State (1h dominates; 5m is the noisy
# refinement).  Only TFs actually present + warm contribute; weights renormalise.
DEFAULT_TF_WEIGHTS: Dict[str, float] = {"5m": 0.2, "15m": 0.3, "1h": 0.5}


def _ema(values: np.ndarray, period: int) -> Optional[np.ndarray]:
    """Standard EMA (alpha = 2/(period+1)), seeded on the first value.

    Returns ``None`` when there are too few points for a meaningful read.
    """
    n = len(values)
    if period < 1 or n < period:
        return None
    alpha = 2.0 / (period + 1.0)
    out = np.empty(n, dtype=np.float64)
    out[0] = values[0]
    for i in range(1, n):
        out[i] = alpha * values[i] + (1.0 - alpha) * out[i - 1]
    return out


def _rsi(closes: np.ndarray, period: int = 14) -> Optional[float]:
    """Wilder RSI on the last ``period`` deltas.  ``None`` if too short."""
    if len(closes) < period + 1:
        return None
    deltas = np.diff(closes[-(period + 1):])
    gains = np.clip(deltas, 0.0, None)
    losses = np.clip(-deltas, 0.0, None)
    avg_gain = float(np.mean(gains))
    avg_loss = float(np.mean(losses))
    if avg_loss == 0.0:
        return 100.0 if avg_gain > 0.0 else 50.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def _atr(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 14) -> Optional[float]:
    """Average true range over the last ``period`` candles.  ``None`` if short."""
    n = len(closes)
    if n < period + 1 or len(highs) != n or len(lows) != n:
        return None
    prev_close = closes[:-1]
    h = highs[1:]
    low = lows[1:]
    tr = np.maximum.reduce([
        h - low,
        np.abs(h - prev_close),
        np.abs(low - prev_close),
    ])
    if len(tr) < period:
        return None
    atr = float(np.mean(tr[-period:]))
    return atr if atr > 0.0 else None


def _clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def _tf_state(
    candles: Dict[str, np.ndarray],
    *,
    ema_periods: Sequence[int],
    rsi_period: int,
    atr_period: int,
    slope_lookback: int,
    chop_fan_pct: float,
    w_stack: float,
    w_slope: float,
    w_rsi: float,
) -> Optional[float]:
    """Single-timeframe directional score in ``[−1, +1]`` (None if not warm).

    Combines: EMA-stack ordering, ATR-normalised EMA-fast slope, and RSI tilt;
    shrunk toward zero when the fast/slow EMAs are tangled (chop).
    """
    closes = candles.get("close")
    highs = candles.get("high")
    lows = candles.get("low")
    if closes is None:
        return None
    closes = np.asarray(closes, dtype=np.float64)
    fast_p, mid_p, slow_p = ema_periods
    if len(closes) < slow_p + slope_lookback + 1:
        return None
    ema_fast = _ema(closes, fast_p)
    ema_mid = _ema(closes, mid_p)
    ema_slow = _ema(closes, slow_p)
    if ema_fast is None or ema_mid is None or ema_slow is None:
        return None

    f, m, s = ema_fast[-1], ema_mid[-1], ema_slow[-1]
    # Stack: mean of the two adjacent pair-orderings → {−1, 0, +1} (0 = tangled).
    stack = (np.sign(f - m) + np.sign(m - s)) / 2.0

    # Slope of the fast EMA over the lookback, normalised by ATR so it is
    # comparable across pairs/regimes; ATR-less data falls back to a price-pct norm.
    d = float(ema_fast[-1] - ema_fast[-1 - slope_lookback])
    atr = None
    if highs is not None and lows is not None:
        atr = _atr(
            np.asarray(highs, dtype=np.float64),
            np.asarray(lows, dtype=np.float64),
            closes,
            atr_period,
        )
    denom = atr if atr is not None else (abs(s) * 0.01 or 1.0)
    slope = _clamp(d / denom, -1.0, 1.0)

    rsi = _rsi(closes, rsi_period)
    rsi_tilt = _clamp(((rsi - 50.0) / 50.0), -1.0, 1.0) if rsi is not None else 0.0

    tf_b = _clamp(w_stack * stack + w_slope * slope + w_rsi * rsi_tilt, -1.0, 1.0)

    # Chop shrink: a narrow fast/slow fan means no real trend → damp conviction.
    if s != 0.0:
        fan = abs(f - s) / abs(s)
        if fan < chop_fan_pct:
            tf_b *= _clamp(fan / chop_fan_pct, 0.0, 1.0)
    return tf_b


def compute_btc_state(
    btc_candles_by_tf: Dict[str, Dict[str, np.ndarray]],
    *,
    tf_weights: Optional[Dict[str, float]] = None,
    ema_periods: Sequence[int] = (8, 21, 55),
    rsi_period: int = 14,
    atr_period: int = 14,
    slope_lookback: int = 3,
    chop_fan_pct: float = 0.003,
    w_stack: float = 0.5,
    w_slope: float = 0.3,
    w_rsi: float = 0.2,
) -> Dict[str, object]:
    """Composite BTC-State score ``b ∈ [−1, +1]`` across timeframes.

    ``b < 0`` = BTC hostile (falling) → counter-trend LONGs at risk.
    ``b > 0`` = BTC supportive (rising) → counter-trend SHORTs at risk.
    Returns ``{"b", "per_tf", "status"}``; ``status="insufficient_data"`` (b=0)
    when no timeframe is warm enough — callers treat that as a no-op.
    """
    weights = tf_weights or DEFAULT_TF_WEIGHTS
    per_tf: Dict[str, float] = {}
    num = 0.0
    wsum = 0.0
    for tf, w in weights.items():
        candles = btc_candles_by_tf.get(tf)
        if not candles:
            continue
        tf_b = _tf_state(
            candles,
            ema_periods=ema_periods,
            rsi_period=rsi_period,
            atr_period=atr_period,
            slope_lookback=slope_lookback,
            chop_fan_pct=chop_fan_pct,
            w_stack=w_stack,
            w_slope=w_slope,
            w_rsi=w_rsi,
        )
        if tf_b is None:
            continue
        per_tf[tf] = tf_b
        num += w * tf_b
        wsum += w
    if wsum <= 0.0:
        return {"b": 0.0, "per_tf": {}, "status": "insufficient_data"}
    return {"b": _clamp(num / wsum, -1.0, 1.0), "per_tf": per_tf, "status": "ok"}


def compute_downside_coupling(
    pair_closes: Sequence[float],
    btc_closes: Sequence[float],
    *,
    lookback: int = 200,
    min_samples: int = 20,
    min_down: int = 8,
    beta_ref: float = 1.0,
) -> Dict[str, object]:
    """Per-pair downside coupling ``w_pair ∈ [0, 1]`` on aligned returns.

    Measures how hard the pair falls *when BTC falls* — downside correlation ×
    normalised downside beta.  A pair that ignores BTC on the way down (memecoin /
    own-catalyst mover) lands near 0 and is effectively exempt.  Returns
    ``{"w_pair", "down_corr", "down_beta", "n_down", "status"}``; ``w_pair=0`` (no
    haircut) when there are too few samples or too few down-BTC bars to measure.
    """
    pc = np.asarray(pair_closes, dtype=np.float64)
    bc = np.asarray(btc_closes, dtype=np.float64)
    n = min(len(pc), len(bc))
    if n < min_samples + 1:
        return {"w_pair": 0.0, "down_corr": 0.0, "down_beta": 0.0, "n_down": 0, "status": "insufficient_data"}
    pc = pc[-min(n, lookback + 1):]
    bc = bc[-min(n, lookback + 1):]
    pr = np.diff(pc) / np.where(pc[:-1] == 0.0, np.nan, pc[:-1])
    br = np.diff(bc) / np.where(bc[:-1] == 0.0, np.nan, bc[:-1])
    mask = np.isfinite(pr) & np.isfinite(br) & (br < 0.0)
    n_down = int(np.count_nonzero(mask))
    if n_down < min_down:
        return {"w_pair": 0.0, "down_corr": 0.0, "down_beta": 0.0, "n_down": n_down, "status": "insufficient_data"}
    prd = pr[mask]
    brd = br[mask]
    var_b = float(np.var(brd))
    std_p = float(np.std(prd))
    if var_b <= 0.0 or std_p <= 0.0:
        return {"w_pair": 0.0, "down_corr": 0.0, "down_beta": 0.0, "n_down": n_down, "status": "degenerate"}
    corr = float(np.corrcoef(prd, brd)[0, 1])
    down_corr = _clamp(corr if np.isfinite(corr) else 0.0, 0.0, 1.0)  # negative corr = hedge, not coupling
    down_beta = float(np.cov(prd, brd)[0, 1] / var_b)
    beta_n = _clamp(down_beta / beta_ref if beta_ref > 0 else 0.0, 0.0, 1.0)
    w_pair = _clamp(down_corr * beta_n, 0.0, 1.0)
    return {
        "w_pair": w_pair,
        "down_corr": down_corr,
        "down_beta": down_beta,
        "n_down": n_down,
        "status": "ok",
    }


def compute_haircut_factor(
    b: float,
    w_pair: float,
    side: str,
    setup_class: str,
    *,
    k: float = 0.40,
    floor: float = 0.55,
    ct_long_mult: float = 1.0,
    ct_short_mult: float = 0.5,
    severe_setup_weight: float = 1.0,
    mild_setup_weight: float = 0.5,
    severe_setups: frozenset[str] = DEFAULT_SEVERE_SETUPS,
) -> Dict[str, object]:
    """Confidence multiplier ``factor ∈ [floor, 1]`` for a signal.

    Haircut applies ONLY to the side that is counter to BTC-State:
      * LONG when ``b < 0`` (BTC hostile to longs), OR
      * SHORT when ``b > 0`` (BTC hostile to shorts).
    Aligned signals get ``factor = 1.0`` (no haircut).  The counter-trend LONG is
    penalised ``ct_long_mult / ct_short_mult`` (≈2×) harder than the counter-trend
    SHORT — the downside-asymmetry doctrine — and the worst reversal setups
    (``severe_setups``) get full weight while others get a gentler one.

    ``factor = clamp(1 − k·|b|·w_pair·A_side·setup_weight, floor, 1)``.
    Returns ``{"factor", "applied", "side_mult", "setup_weight", "reason"}``.
    """
    s = (side or "").upper()
    counter = (s == "LONG" and b < 0.0) or (s == "SHORT" and b > 0.0)
    if not counter or w_pair <= 0.0:
        return {"factor": 1.0, "applied": False, "side_mult": 0.0, "setup_weight": 0.0, "reason": "aligned_or_decoupled"}
    side_mult = ct_long_mult if s == "LONG" else ct_short_mult
    setup_weight = severe_setup_weight if (setup_class or "").upper() in severe_setups else mild_setup_weight
    raw = 1.0 - k * abs(b) * _clamp(w_pair, 0.0, 1.0) * side_mult * setup_weight
    factor = _clamp(raw, floor, 1.0)
    return {
        "factor": factor,
        "applied": True,
        "side_mult": side_mult,
        "setup_weight": setup_weight,
        "reason": f"counter_{s.lower()}_b{b:+.2f}_w{w_pair:.2f}",
    }


# ===========================================================================
# Directional macro-regime (S39 fix) — "direction, not a fence"
# ===========================================================================
# The binary "below the 200-week MA" gate got both macro turns backwards (it
# missed the fall from the cycle top while price was still above the line, and
# kept longs off through the whole recovery while price was still below it).
# Research (multi-source) + the owner's weekly charts both say the same thing:
# trend is read from SLOPE + price-vs-the-FAST-MA + higher-low/lower-low
# STRUCTURE, not a static line.  This classifier is **quick to de-risk** (suppress
# the moment price loses the fast MA on the way down) and **patient to re-risk**
# (restore only once price reclaims the fast MA AND a higher low has formed) — the
# asymmetry the sources prescribe for counter-trend longs.  Recomputed every scan,
# so it auto-restores as the trend turns — earlier than the slow line on both ends.


def _sma(values: Sequence[float], period: int) -> Optional[float]:
    """Simple moving average of the last ``period`` values. None if too short."""
    if period < 1 or len(values) < period:
        return None
    return sum(values[-period:]) / float(period)


def _as_close_list(closes) -> list:
    """Coerce a close series (list or numpy array) to a clean list of floats.

    Avoids ``arr or []`` (ambiguous truth value on numpy arrays).
    """
    seq = closes if closes is not None else []
    out = []
    for x in seq:
        try:
            out.append(float(x))
        except (TypeError, ValueError):
            continue
    return out


def macro_direction(
    closes,
    *,
    fast_period: int = 50,
    slow_period: int = 200,
    slope_lookback: int = 8,
    swing: int = 10,
    buffer_pct: float = 0.01,
) -> Dict[str, object]:
    """Directional macro regime: ``regime`` + ``longs_suppressed`` (the S39 gate).

    Reads SLOPE (fast-MA direction) + POSITION (price vs the fast MA) + STRUCTURE
    (recent swing-low vs the prior swing-low), on a single close series.  Used on
    BTC weekly (macro) and, separately, on a pair's own higher-TF series.

    Regimes
    -------
    * ``DECLINE``  — price has lost the fast MA on the way down (or it is falling /
      making lower lows).  Counter-trend LONGs suppressed.  Catches the "fall from
      the top to the MA" leg the static line missed.
    * ``RECOVERY`` — price has reclaimed the fast MA AND a higher low has formed,
      while the fast MA may still be turning.  Longs restored *early* — before the
      slow line is reclaimed.
    * ``BULL``     — price above a rising fast MA (and ≥ slow MA when known).
    * ``NEUTRAL``  — price hugging the fast MA inside the buffer; no suppression.

    ``buffer_pct`` is a deadband around the fast MA so chop around it doesn't
    flicker the regime.  Fails to ``NEUTRAL`` / not-suppressed on missing data.

    Returns ``{regime, longs_suppressed, direction, price, fast_ma, slow_ma,
    fast_rising, higher_low, lower_low, status}``.
    """
    c = _as_close_list(closes)
    need = max(fast_period, swing * 2) + 1
    if len(c) < need:
        return {
            "regime": "NEUTRAL", "longs_suppressed": False, "direction": "flat",
            "price": (c[-1] if c else None), "fast_ma": None, "slow_ma": None,
            "fast_rising": None, "higher_low": None, "lower_low": None,
            "status": "insufficient_data",
        }
    price = c[-1]
    fast = _sma(c, fast_period)
    slow = _sma(c, slow_period)  # may be None when history < slow_period (context only)

    # Fast-MA slope over the lookback (vs the MA `slope_lookback` bars ago).
    fast_prev = _sma(c[: len(c) - slope_lookback], fast_period)
    fast_rising = True if fast_prev is None else (fast > fast_prev)

    # Structure: most-recent swing low vs the prior one.
    recent_low = min(c[-swing:])
    prior_low = min(c[-2 * swing : -swing])
    higher_low = recent_low > prior_low
    lower_low = recent_low < prior_low

    above_fast = price > fast * (1.0 + buffer_pct)
    below_fast = price < fast * (1.0 - buffer_pct)

    # Decision — check the confirmed up-turn first so a real recovery overrides.
    if above_fast and (higher_low or fast_rising):
        bull = fast_rising and (slow is None or fast >= slow)
        regime = "BULL" if bull else "RECOVERY"
        suppressed, direction = False, "up"
    elif below_fast:
        # Lost the fast MA → down leg (deep bear, or the early fall from the top
        # while the fast MA is still rolling over).  De-risk quickly.
        regime = "DECLINE"
        suppressed, direction = True, "down"
    else:
        regime, suppressed, direction = "NEUTRAL", False, "flat"

    return {
        "regime": regime,
        "longs_suppressed": suppressed,
        "direction": direction,
        "price": price,
        "fast_ma": fast,
        "slow_ma": slow,
        "fast_rising": fast_rising,
        "higher_low": higher_low,
        "lower_low": lower_low,
        "status": "ok",
    }
