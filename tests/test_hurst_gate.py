"""Tests for the Hurst exponent indicator and the regime Hurst gate (Fix A).

The Hurst gate demotes an ADX-driven TRENDING classification to RANGING when
price is mean-reverting (H < 0.45), so choppy markets that lift ADX don't
masquerade as trends and spawn exit-runners into reversals.
"""

from __future__ import annotations

import numpy as np

from src.indicators import hurst_exponent
from src.regime import (
    MarketRegime,
    RegimeService,
    _apply_hurst_gate,
    _HURST_MEAN_REVERT_MAX,
)


class TestHurstExponent:
    def test_flat_series_is_random_walk(self):
        # A degenerate flat series has no opinion → 0.5.
        assert hurst_exponent(np.ones(60) * 100.0) == 0.5

    def test_too_short_returns_neutral(self):
        assert hurst_exponent(np.arange(5, dtype=float)) == 0.5

    def test_persistent_trend_is_high(self):
        # Random-walk-with-drift reads H~0.5 because the lag-variance estimator
        # removes the deterministic drift; genuine persistence needs positively
        # autocorrelated increments, induced here by smoothing the noise.
        rng = np.random.default_rng(0)
        inc = np.convolve(rng.normal(0.1, 0.15, 140), np.ones(15) / 15, mode="valid")
        series = 100 + np.cumsum(inc)
        assert hurst_exponent(series) > 0.55

    def test_mean_reverting_is_low(self):
        # Oscillating series → strong mean reversion.
        series = 100 + np.sin(np.arange(120)) * 2.0
        assert hurst_exponent(series) < 0.45

    def test_clamped_to_unit_interval(self):
        rng = np.random.default_rng(2)
        series = 100 + np.cumsum(rng.normal(0.5, 0.1, 200))
        h = hurst_exponent(series)
        assert 0.0 <= h <= 1.0

    def test_nan_tolerant(self):
        series = np.array([100.0, np.nan, 101.0, np.nan] + [100.0 + i for i in range(60)])
        h = hurst_exponent(series)
        assert 0.0 <= h <= 1.0


class TestApplyHurstGate:
    def test_demotes_trending_when_mean_reverting(self):
        low_h = _HURST_MEAN_REVERT_MAX - 0.1
        assert _apply_hurst_gate(MarketRegime.TRENDING_UP, low_h) == MarketRegime.RANGING
        assert _apply_hurst_gate(MarketRegime.TRENDING_DOWN, low_h) == MarketRegime.RANGING

    def test_keeps_trending_when_persistent(self):
        high_h = 0.7
        assert _apply_hurst_gate(MarketRegime.TRENDING_UP, high_h) == MarketRegime.TRENDING_UP

    def test_no_opinion_passes_through(self):
        assert _apply_hurst_gate(MarketRegime.TRENDING_UP, None) == MarketRegime.TRENDING_UP

    def test_non_trending_unaffected(self):
        low_h = 0.1
        assert _apply_hurst_gate(MarketRegime.RANGING, low_h) == MarketRegime.RANGING
        assert _apply_hurst_gate(MarketRegime.VOLATILE, low_h) == MarketRegime.VOLATILE
        assert _apply_hurst_gate(MarketRegime.QUIET, low_h) == MarketRegime.QUIET


class TestHurstGateInClassify:
    def _trending_indicators(self):
        return {
            "adx_last": 35.0,
            "ema9_last": 102.0,
            "ema21_last": 100.0,
            "bb_upper_last": 104.0,
            "bb_mid_last": 100.0,
            "bb_lower_last": 96.0,
        }

    def test_choppy_candles_demote_trending_to_ranging(self):
        """ADX says trending but an oscillating tape (low Hurst) is demoted."""
        svc = RegimeService()
        # Oscillating closes — high ADX from the indicators, but mean-reverting.
        closes = 100 + np.sin(np.arange(60)) * 2.0
        candles = {
            "open": closes - 0.1,
            "high": closes + 0.5,
            "low": closes - 0.5,
            "close": closes,
            "volume": np.ones(60) * 1000,
        }
        result = svc.classify(
            self._trending_indicators(), candles, timeframe="5m",
            symbol="CHOPUSDT", pair_tier="MAJOR",
        )
        assert result.regime == MarketRegime.RANGING

    def test_persistent_trend_survives_gate(self):
        svc = RegimeService()
        rng = np.random.default_rng(0)
        inc = np.convolve(rng.normal(0.1, 0.15, 140), np.ones(15) / 15, mode="valid")
        closes = 100 + np.cumsum(inc)
        candles = {
            "open": closes - 0.1,
            "high": closes + 0.5,
            "low": closes - 0.5,
            "close": closes,
            "volume": np.ones(60) * 1000,
        }
        # Feed repeatedly to clear hysteresis dwell.
        result = None
        for _ in range(4):
            result = svc.classify(
                self._trending_indicators(), candles, timeframe="5m",
                symbol="TRENDUSDT", pair_tier="MAJOR",
            )
        assert result.regime in (MarketRegime.TRENDING_UP, MarketRegime.TRENDING_DOWN)
