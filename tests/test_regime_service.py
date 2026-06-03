"""Tests for RegimeService — per-symbol regime isolation and the get_regime API.

These lock in the fixes for three production bugs:

1. ``entry_regime`` was always empty because ``trade_observer`` called a
   non-existent ``detect()`` method.  RegimeService now exposes ``get_regime``.
2. A single shared detector cross-contaminated all 75 pairs' hysteresis and
   transition state.  RegimeService keeps one detector per symbol.
3. Volume-tier thresholds (MAJOR/MIDCAP/ALTCOIN) were never applied because the
   scan path used the base detector.  RegimeService builds an AdaptiveRegimeDetector
   per symbol with the pair's tier.
"""

from __future__ import annotations

import numpy as np

from src.regime import MarketRegime, RegimeService


def _trending_up_indicators():
    return {
        "adx_last": 35.0,
        "ema9_last": 102.0,
        "ema21_last": 100.0,
        "bb_upper_last": 104.0,
        "bb_mid_last": 100.0,
        "bb_lower_last": 96.0,
    }


def _ranging_indicators():
    return {
        "adx_last": 12.0,
        "ema9_last": 100.05,
        "ema21_last": 100.0,
        "bb_upper_last": 101.0,
        "bb_mid_last": 100.0,
        "bb_lower_last": 99.0,
    }


def _candles(n=60, base=100.0, trend=0.1):
    close = np.cumsum(np.ones(n) * trend) + base
    return {
        "open": close - 0.1,
        "high": close + 0.5,
        "low": close - 0.5,
        "close": close,
        "volume": np.ones(n) * 1000,
    }


class TestGetRegime:
    def test_get_regime_none_before_classify(self):
        svc = RegimeService()
        assert svc.get_regime("BTCUSDT") is None

    def test_get_regime_returns_last_result(self):
        svc = RegimeService()
        result = svc.classify(
            _trending_up_indicators(), _candles(), timeframe="5m",
            symbol="BTCUSDT", pair_tier="MAJOR",
        )
        cached = svc.get_regime("BTCUSDT")
        assert cached is result
        assert cached.regime == result.regime

    def test_get_regime_is_per_symbol(self):
        svc = RegimeService()
        svc.classify(_trending_up_indicators(), _candles(), symbol="BTCUSDT",
                     pair_tier="MAJOR")
        svc.classify(_ranging_indicators(), _candles(trend=0.0), symbol="DOGEUSDT",
                     pair_tier="ALTCOIN")
        btc = svc.get_regime("BTCUSDT")
        doge = svc.get_regime("DOGEUSDT")
        assert btc is not None and doge is not None
        # Independent results — the two symbols don't share a cache slot.
        assert btc is not doge


class TestPerSymbolIsolation:
    def test_hysteresis_state_is_isolated_per_symbol(self):
        """Interleaving two symbols must not clobber each other's dwell state.

        With the old shared detector, alternating classify() calls for two
        symbols reset the pending-regime dwell counter every call, so a stable
        regime could never be adopted.  Per-symbol detectors keep independent
        hysteresis so a symbol fed a consistent regime converges.
        """
        svc = RegimeService()
        # Feed BTC a consistent trending signal while interleaving a ranging
        # signal for DOGE on every other call.
        for _ in range(5):
            svc.classify(_trending_up_indicators(), _candles(), symbol="BTCUSDT",
                         pair_tier="MAJOR")
            svc.classify(_ranging_indicators(), _candles(trend=0.0),
                         symbol="DOGEUSDT", pair_tier="ALTCOIN")
        btc = svc.get_regime("BTCUSDT")
        # BTC saw 5 consecutive trending classifications on its own detector;
        # hysteresis (3 dwell) should have adopted a trending regime despite the
        # interleaved DOGE calls.
        assert btc.regime in (MarketRegime.TRENDING_UP, MarketRegime.TRENDING_DOWN)

    def test_distinct_detectors_per_symbol(self):
        svc = RegimeService()
        svc.classify(_trending_up_indicators(), _candles(), symbol="BTCUSDT",
                     pair_tier="MAJOR")
        svc.classify(_trending_up_indicators(), _candles(), symbol="ETHUSDT",
                     pair_tier="MAJOR")
        assert svc._detectors["BTCUSDT"] is not svc._detectors["ETHUSDT"]


class TestTierApplication:
    def test_tier_thresholds_applied(self):
        svc = RegimeService()
        svc.classify(_trending_up_indicators(), _candles(), symbol="BTCUSDT",
                     pair_tier="MAJOR")
        svc.classify(_trending_up_indicators(), _candles(), symbol="PEPEUSDT",
                     pair_tier="ALTCOIN")
        assert svc._detectors["BTCUSDT"]._pair_tier == "MAJOR"
        assert svc._detectors["PEPEUSDT"]._pair_tier == "ALTCOIN"

    def test_unknown_tier_falls_back_to_midcap(self):
        svc = RegimeService()
        svc.classify(_trending_up_indicators(), _candles(), symbol="XYZUSDT",
                     pair_tier="NONSENSE")
        assert svc._detectors["XYZUSDT"]._pair_tier == "MIDCAP"

    def test_none_tier_does_not_clobber_existing_detector(self):
        """A None tier hint (e.g. from get_transition_boost) must not rebuild
        an existing MAJOR detector as MIDCAP and wipe its state."""
        svc = RegimeService()
        svc.classify(_trending_up_indicators(), _candles(), symbol="BTCUSDT",
                     pair_tier="MAJOR")
        original = svc._detectors["BTCUSDT"]
        # get_transition_boost passes no pair_tier → must reuse the same detector
        svc.get_transition_boost("LONG", symbol="BTCUSDT")
        assert svc._detectors["BTCUSDT"] is original
        assert svc._detectors["BTCUSDT"]._pair_tier == "MAJOR"

    def test_tier_change_rebuilds_detector(self):
        svc = RegimeService()
        svc.classify(_trending_up_indicators(), _candles(), symbol="SURGEUSDT",
                     pair_tier="ALTCOIN")
        first = svc._detectors["SURGEUSDT"]
        # Pair's volume surged into MIDCAP — explicit new tier rebuilds.
        svc.classify(_trending_up_indicators(), _candles(), symbol="SURGEUSDT",
                     pair_tier="MIDCAP")
        assert svc._detectors["SURGEUSDT"] is not first
        assert svc._detectors["SURGEUSDT"]._pair_tier == "MIDCAP"


class TestContextAndBoost:
    def test_build_regime_context_per_symbol(self):
        svc = RegimeService()
        result = svc.classify(_trending_up_indicators(), _candles(),
                              symbol="BTCUSDT", pair_tier="MAJOR")
        ctx = svc.build_regime_context(result, _candles(), _trending_up_indicators(),
                                       vwap=100.0, symbol="BTCUSDT", pair_tier="MAJOR")
        assert ctx.label == result.regime.value

    def test_transition_boost_callable_per_symbol(self):
        svc = RegimeService()
        svc.classify(_ranging_indicators(), _candles(trend=0.0), symbol="BTCUSDT",
                     pair_tier="MAJOR")
        boost = svc.get_transition_boost("LONG", symbol="BTCUSDT")
        assert isinstance(boost, float)
