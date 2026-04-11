"""Regression tests for zero-live-signal diagnosis (pre-step-9 PR).

Tests protect against the three confirmed code-level blockers:
1. Missing _evaluate_range_fade in ScalpChannel
2. Missing "mean_reversion" key in _select_indicator_weights
3. MTF hard gate silently blocking without suppression tracking

These tests ensure the identified failure modes cannot silently regress.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.channels.scalp import ScalpChannel
from src.smc import Direction


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_candles(n: int = 60, base: float = 100.0, trend: float = 0.0) -> dict:
    close = np.ones(n) * base + np.arange(n) * trend
    high = close + 0.5
    low = close - 0.5
    vol = np.ones(n) * 1000
    return {"open": close - 0.1, "high": high, "low": low, "close": close, "volume": vol}


def _make_ind(
    adx: float = 15.0,
    bb_upper: float = 103.0,
    bb_mid: float = 100.0,
    bb_lower: float = 97.0,
    rsi: float = 30.0,
    ema9: float = 100.5,
    ema21: float = 99.5,
    atr: float = 0.5,
    bb_width_pct: float | None = None,
    bb_width_prev_pct: float | None = None,
) -> dict:
    d = {
        "adx_last": adx,
        "bb_upper_last": bb_upper,
        "bb_mid_last": bb_mid,
        "bb_lower_last": bb_lower,
        "rsi_last": rsi,
        "ema9_last": ema9,
        "ema21_last": ema21,
        "atr_last": atr,
        "momentum_last": 0.2,
    }
    if bb_width_pct is not None:
        d["bb_width_pct"] = bb_width_pct
    if bb_width_prev_pct is not None:
        d["bb_width_prev_pct"] = bb_width_prev_pct
    return d


# ---------------------------------------------------------------------------
# Blocker 1 — _evaluate_range_fade existence and correctness
# ---------------------------------------------------------------------------

class TestRangeFadeExists:
    """ScalpChannel must expose _evaluate_range_fade — its absence caused zero RANGE_FADE candidates."""

    def test_method_exists(self):
        """_evaluate_range_fade must be a callable on ScalpChannel."""
        ch = ScalpChannel()
        assert callable(getattr(ch, "_evaluate_range_fade", None)), (
            "_evaluate_range_fade missing from ScalpChannel — RANGE_FADE cannot generate candidates"
        )

    def test_long_at_lower_bb_fires(self):
        """Price at/below lower BB + low ADX + oversold RSI → RANGE_FADE LONG."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60, base=100.0)}
        candles["5m"]["close"][-1] = 96.5  # below bb_lower=97.0
        ind = _make_ind(adx=15, bb_lower=97.0, rsi=28)
        sig = ch._evaluate_range_fade("BTCUSDT", candles, {"5m": ind}, {}, 0.01, 10_000_000)
        assert sig is not None, "RANGE_FADE LONG should fire at lower BB with low ADX + oversold RSI"
        assert sig.direction == Direction.LONG

    def test_short_at_upper_bb_fires(self):
        """Price at/above upper BB + low ADX + overbought RSI → RANGE_FADE SHORT."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60, base=100.0)}
        candles["5m"]["close"][-1] = 103.5  # above bb_upper=103.0
        ind = _make_ind(adx=15, bb_upper=103.0, rsi=70)
        sig = ch._evaluate_range_fade("BTCUSDT", candles, {"5m": ind}, {}, 0.01, 10_000_000)
        assert sig is not None, "RANGE_FADE SHORT should fire at upper BB with low ADX + overbought RSI"
        assert sig.direction == Direction.SHORT

    def test_high_adx_blocks(self):
        """ADX > 25 indicates a trend — RANGE_FADE must be blocked."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60, base=100.0)}
        candles["5m"]["close"][-1] = 96.5
        ind = _make_ind(adx=30, bb_lower=97.0, rsi=28)
        sig = ch._evaluate_range_fade("BTCUSDT", candles, {"5m": ind}, {}, 0.01, 10_000_000)
        assert sig is None, "RANGE_FADE must be blocked when ADX > 25 (trend active)"

    def test_trending_regime_blocks(self):
        """RANGE_FADE must not fire in TRENDING_UP/DOWN regimes."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60, base=100.0)}
        candles["5m"]["close"][-1] = 96.5
        ind = _make_ind(adx=15, bb_lower=97.0, rsi=28)
        for bad_regime in ("TRENDING_UP", "TRENDING_DOWN", "VOLATILE"):
            sig = ch._evaluate_range_fade("BTCUSDT", candles, {"5m": ind}, {}, 0.01, 10_000_000, regime=bad_regime)
            assert sig is None, f"RANGE_FADE must be blocked in {bad_regime} regime"

    def test_ranging_regime_allowed(self):
        """RANGE_FADE must be allowed in RANGING and QUIET regimes."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60, base=100.0)}
        candles["5m"]["close"][-1] = 96.5
        ind = _make_ind(adx=15, bb_lower=97.0, rsi=28)
        for good_regime in ("RANGING", "QUIET"):
            sig = ch._evaluate_range_fade("BTCUSDT", candles, {"5m": ind}, {}, 0.01, 10_000_000, regime=good_regime)
            assert sig is not None, f"RANGE_FADE should be allowed in {good_regime} regime"

    def test_rsi_recovering_long_blocked(self):
        """LONG RANGE_FADE blocked when RSI > 55 (price already recovering from oversold)."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60, base=100.0)}
        candles["5m"]["close"][-1] = 96.5
        ind = _make_ind(adx=15, bb_lower=97.0, rsi=60)
        sig = ch._evaluate_range_fade("BTCUSDT", candles, {"5m": ind}, {}, 0.01, 10_000_000)
        assert sig is None, "RANGE_FADE LONG must be blocked when RSI > 55 (entry timing missed)"

    def test_rsi_recovering_short_blocked(self):
        """SHORT RANGE_FADE blocked when RSI < 45 (price already recovering from overbought)."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60, base=100.0)}
        candles["5m"]["close"][-1] = 103.5
        ind = _make_ind(adx=15, bb_upper=103.0, rsi=40)
        sig = ch._evaluate_range_fade("BTCUSDT", candles, {"5m": ind}, {}, 0.01, 10_000_000)
        assert sig is None, "RANGE_FADE SHORT must be blocked when RSI < 45 (entry timing missed)"

    def test_bb_expanding_blocks(self):
        """BB width expanding >10% from prior bar → breakout in progress, not range fade."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60, base=100.0)}
        candles["5m"]["close"][-1] = 96.5
        ind = _make_ind(
            adx=15, bb_lower=97.0, rsi=28,
            bb_width_pct=4.5, bb_width_prev_pct=4.0,  # 4.5 > 4.0*1.1=4.4 → expanding
        )
        sig = ch._evaluate_range_fade("BTCUSDT", candles, {"5m": ind}, {}, 0.01, 10_000_000)
        assert sig is None, "RANGE_FADE must be blocked when BB is expanding >10% (squeeze breakout)"

    def test_bb_stable_allows(self):
        """BB width stable → range fade allowed."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60, base=100.0)}
        candles["5m"]["close"][-1] = 96.5
        ind = _make_ind(
            adx=15, bb_lower=97.0, rsi=28,
            bb_width_pct=4.0, bb_width_prev_pct=4.0,  # stable → allowed
        )
        sig = ch._evaluate_range_fade("BTCUSDT", candles, {"5m": ind}, {}, 0.01, 10_000_000)
        assert sig is not None, "RANGE_FADE should be allowed when BB width is stable"

    def test_bb_width_missing_fails_open(self):
        """Missing BB width data → squeeze guard skipped, range fade proceeds if other gates pass."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60, base=100.0)}
        candles["5m"]["close"][-1] = 96.5
        ind = _make_ind(adx=15, bb_lower=97.0, rsi=28)  # no bb_width_pct keys
        sig = ch._evaluate_range_fade("BTCUSDT", candles, {"5m": ind}, {}, 0.01, 10_000_000)
        assert sig is not None, "RANGE_FADE squeeze guard must fail-open when BB width data is missing"

    def test_price_not_at_extreme_blocked(self):
        """Price between the BBs → no mean-reversion edge → no signal."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60, base=100.0)}
        candles["5m"]["close"][-1] = 100.0  # inside BBs (97 < 100 < 103)
        ind = _make_ind(adx=15, rsi=28)
        sig = ch._evaluate_range_fade("BTCUSDT", candles, {"5m": ind}, {}, 0.01, 10_000_000)
        assert sig is None, "RANGE_FADE must not fire when price is not at a BB extreme"

    def test_setup_class_is_range_fade(self):
        """Signal produced by _evaluate_range_fade must carry setup_class='RANGE_FADE'."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60, base=100.0)}
        candles["5m"]["close"][-1] = 96.5
        ind = _make_ind(adx=15, bb_lower=97.0, rsi=28)
        sig = ch._evaluate_range_fade("BTCUSDT", candles, {"5m": ind}, {}, 0.01, 10_000_000)
        assert sig is not None
        assert sig.setup_class == "RANGE_FADE", (
            f"setup_class must be 'RANGE_FADE', got '{sig.setup_class}'"
        )

    def test_in_evaluate_loop(self):
        """_evaluate_range_fade must be registered in ScalpChannel.evaluate() so candidates reach the gate chain."""
        import inspect
        src = inspect.getsource(ScalpChannel.evaluate)
        assert "_evaluate_range_fade" in src, (
            "_evaluate_range_fade is not called inside evaluate() — "
            "RANGE_FADE candidates will never reach the scanner gate chain"
        )


# ---------------------------------------------------------------------------
# Blocker 2 — _select_indicator_weights completeness
# ---------------------------------------------------------------------------

class TestIndicatorWeightsCompleteness:
    """_select_indicator_weights must include 'mean_reversion' key in all regimes."""

    REQUIRED_KEYS = {"order_flow", "trend", "mean_reversion", "volume"}

    @pytest.mark.parametrize("regime", [
        "RANGING", "QUIET", "VOLATILE", "TRENDING_UP", "TRENDING_DOWN", "",
    ])
    def test_mean_reversion_key_present(self, regime):
        """All regime branches must expose 'mean_reversion' weight — missing key caused KeyError."""
        ch = ScalpChannel()
        weights = ch._select_indicator_weights(regime)
        assert "mean_reversion" in weights, (
            f"_select_indicator_weights('{regime}') missing 'mean_reversion' key — "
            "RANGE_FADE portfolio weighting will raise KeyError"
        )

    @pytest.mark.parametrize("regime", [
        "RANGING", "QUIET", "VOLATILE", "TRENDING_UP", "TRENDING_DOWN", "",
    ])
    def test_all_required_keys_present(self, regime):
        """All required weight keys must be present for all regimes."""
        ch = ScalpChannel()
        weights = ch._select_indicator_weights(regime)
        missing = self.REQUIRED_KEYS - set(weights.keys())
        assert not missing, (
            f"_select_indicator_weights('{regime}') missing keys: {missing}"
        )

    def test_ranging_boosts_mean_reversion(self):
        """RANGING regime must boost 'mean_reversion' weight (RANGE_FADE priority in range markets)."""
        ch = ScalpChannel()
        weights_ranging = ch._select_indicator_weights("RANGING")
        weights_trending = ch._select_indicator_weights("TRENDING_UP")
        assert weights_ranging["mean_reversion"] > weights_trending["mean_reversion"], (
            "RANGING regime must give higher 'mean_reversion' weight than TRENDING_UP — "
            "RANGE_FADE is the primary candidate type in ranging markets"
        )

    def test_quiet_boosts_mean_reversion(self):
        """QUIET regime must boost 'mean_reversion' weight."""
        ch = ScalpChannel()
        weights_quiet = ch._select_indicator_weights("QUIET")
        weights_trending = ch._select_indicator_weights("TRENDING_UP")
        assert weights_quiet["mean_reversion"] > weights_trending["mean_reversion"]


# ---------------------------------------------------------------------------
# Blocker 3 — RANGE_FADE in gate-exempt sets
# ---------------------------------------------------------------------------

class TestRangeFadeGateExemptions:
    """RANGE_FADE must be exempt from the SMC and trend hard gates in the scanner."""

    def test_range_fade_in_smc_gate_exempt(self):
        """RANGE_FADE must be in _SMC_GATE_EXEMPT_SETUPS — it uses BB, not sweep detection."""
        from src.scanner import _SMC_GATE_EXEMPT_SETUPS
        assert "RANGE_FADE" in _SMC_GATE_EXEMPT_SETUPS, (
            "RANGE_FADE not in _SMC_GATE_EXEMPT_SETUPS — "
            "SMC sweep score will always be 0 for mean-reversion setups, causing hard-block"
        )

    def test_range_fade_in_trend_gate_exempt(self):
        """RANGE_FADE must be in _TREND_GATE_EXEMPT_SETUPS — EMA alignment is counter to the thesis."""
        from src.scanner import _TREND_GATE_EXEMPT_SETUPS
        assert "RANGE_FADE" in _TREND_GATE_EXEMPT_SETUPS, (
            "RANGE_FADE not in _TREND_GATE_EXEMPT_SETUPS — "
            "EMA alignment gate is architecturally wrong for mean-reversion at BB extremes"
        )
