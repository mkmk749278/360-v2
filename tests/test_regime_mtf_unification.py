"""Locks the multi-timeframe regime unification (Option 2).

Two coordinated fixes so the 5m entry regime and the 15m confirmation regime
mean the *same thing* by "trend":

1. ``AdaptiveRegimeDetector._decide_adaptive`` (the production 5m path) no
   longer stamps TRENDING in the weak ADX zone (between the tier's ranging and
   trending floors) on a *fading* move.  A weak-zone trend now requires ADX to
   be rising (``adx_slope > 0``); when the slope is unknown it stays RANGING.

2. ``detect_regime_from_arrays`` (the 15m stamp) is tier-aware and applies the
   same weak-zone confirmation, instead of a flat ADX>=25 floor with no weak
   zone — which previously made a midcap at ADX 22 read TRENDING on 5m and
   RANGING on 15m purely by construction.
"""

from __future__ import annotations

import numpy as np

from src.regime import (
    AdaptiveRegimeDetector,
    MarketRegime,
    detect_regime_from_arrays,
)


# ---------------------------------------------------------------------------
# Part A — weak-zone ADX confirmation in the production 5m path
# ---------------------------------------------------------------------------


def _midcap_detector() -> AdaptiveRegimeDetector:
    # MIDCAP: ranging_max=20, trending_min=25 → weak zone is ADX 20..25.
    return AdaptiveRegimeDetector(pair_tier="MIDCAP")


# Compare regime labels by ``.value`` (string) rather than enum identity:
# other tests in the suite reload ``src.regime``, which yields a distinct
# ``MarketRegime`` class object and breaks ``is`` comparisons.


def test_weak_zone_falling_adx_is_ranging():
    det = _midcap_detector()
    # ADX 22 (weak zone), EMAs separated upward, but ADX is FALLING.
    regime = det._decide_adaptive(
        adx=22.0, ema_slope=0.10, bb_width_pct=2.0, adx_slope=-0.5
    )
    assert regime.value == MarketRegime.RANGING.value


def test_weak_zone_rising_adx_is_trending():
    det = _midcap_detector()
    regime = det._decide_adaptive(
        adx=22.0, ema_slope=0.10, bb_width_pct=2.0, adx_slope=0.5
    )
    assert regime.value == MarketRegime.TRENDING_UP.value

    regime_down = det._decide_adaptive(
        adx=22.0, ema_slope=-0.10, bb_width_pct=2.0, adx_slope=0.5
    )
    assert regime_down.value == MarketRegime.TRENDING_DOWN.value


def test_weak_zone_unknown_slope_stays_ranging():
    det = _midcap_detector()
    regime = det._decide_adaptive(
        adx=22.0, ema_slope=0.10, bb_width_pct=2.0, adx_slope=None
    )
    assert regime.value == MarketRegime.RANGING.value


def test_confirmed_trend_unaffected_by_slope():
    # ADX above the trending floor is a confirmed trend regardless of slope.
    det = _midcap_detector()
    regime = det._decide_adaptive(
        adx=30.0, ema_slope=0.10, bb_width_pct=2.0, adx_slope=-1.0
    )
    assert regime.value == MarketRegime.TRENDING_UP.value


# ---------------------------------------------------------------------------
# Part B — 15m stamp is tier-aware and shares the trend definition
# ---------------------------------------------------------------------------


def _strong_uptrend(n: int = 120) -> tuple:
    # Monotonic ramp with mild noise → high ADX, ema9 > ema21.
    rng = np.random.default_rng(7)
    closes = np.linspace(100.0, 140.0, n) + rng.normal(0, 0.05, n)
    highs = closes + 0.1
    lows = closes - 0.1
    vols = np.full(n, 1000.0)
    return closes, highs, lows, vols


def _choppy_flat(n: int = 120) -> tuple:
    rng = np.random.default_rng(3)
    closes = 100.0 + rng.normal(0, 0.05, n)
    highs = closes + 0.08
    lows = closes - 0.08
    vols = np.full(n, 1000.0)
    return closes, highs, lows, vols


def test_15m_strong_trend_is_trending_up_all_tiers():
    closes, highs, lows, vols = _strong_uptrend()
    idx = len(closes) - 1
    for tier in ("MAJOR", "MIDCAP", "ALTCOIN"):
        label = detect_regime_from_arrays(
            closes, highs, lows, vols, idx=idx, pair_tier=tier
        )
        assert label == MarketRegime.TRENDING_UP.value, tier


def test_15m_choppy_is_not_trending():
    closes, highs, lows, vols = _choppy_flat()
    idx = len(closes) - 1
    label = detect_regime_from_arrays(
        closes, highs, lows, vols, idx=idx, pair_tier="MIDCAP"
    )
    assert label not in (
        MarketRegime.TRENDING_UP.value,
        MarketRegime.TRENDING_DOWN.value,
    )


def test_15m_accepts_missing_tier_and_defaults_midcap():
    closes, highs, lows, vols = _strong_uptrend()
    idx = len(closes) - 1
    # No pair_tier → MIDCAP default, must not raise and must classify the trend.
    label = detect_regime_from_arrays(closes, highs, lows, vols, idx=idx)
    assert label == MarketRegime.TRENDING_UP.value
