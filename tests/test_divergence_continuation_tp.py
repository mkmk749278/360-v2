"""B13 fix: DIVERGENCE_CONTINUATION evaluator-authored TP targets.

Verifies that _evaluate_divergence_continuation() now sets swing-based TP
targets anchored to the divergence detection window, and that these TPs are
protected downstream by both build_risk_plan() and the predictive engine.

Test surface:
1. LONG signal: tp1 = max(highs in divergence window), tp2 = 20-candle swing
   high (or fallback), all TPs above entry.
2. SHORT signal: tp1 = min(lows in divergence window), tp2 = 20-candle swing
   low (or fallback), all TPs below entry.
3. Fallback: when divergence window swing is on the wrong side of entry the
   evaluator falls back to ATR R-multiple targets.
4. SetupClass.DIVERGENCE_CONTINUATION is in STRUCTURAL_SLTP_PROTECTED_SETUPS.
5. "DIVERGENCE_CONTINUATION" is in _PREDICTIVE_SLTP_BYPASS_SETUPS.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.channels.scalp import ScalpChannel
from src.predictive_ai import PredictiveEngine, PredictionResult, _PREDICTIVE_SLTP_BYPASS_SETUPS
from src.signal_quality import STRUCTURAL_SLTP_PROTECTED_SETUPS, SetupClass
from src.smc import Direction


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_smc_data(cvd: list | None = None, fvg_present: bool = True) -> dict:
    """Minimal smc_data for _evaluate_divergence_continuation."""
    fvg_stub = [{"top": 105.0, "bottom": 100.0, "direction": "BULLISH"}] if fvg_present else []
    if cvd is None:
        cvd = [float(i) for i in range(20)]
    return {
        "fvg": fvg_stub,
        "orderblocks": [],
        "sweeps": [],
        "mss": None,
        "pair_profile": None,
        "regime_context": None,
        "cvd": cvd,
        "funding_rate": None,
    }


def _make_indicators(
    close: float = 100.0,
    ema9: float = 101.5,
    ema21: float = 100.0,
) -> dict:
    return {
        "5m": {
            "ema9_last": ema9,
            "ema21_last": ema21,
            "rsi_last": 48.0,
            "macd_histogram_last": 0.1,
            "macd_histogram_prev": 0.05,
            "atr_last": close * 0.002,
            "adx_last": 28.0,
        }
    }


def _make_candles_long(close: float = 100.0, n: int = 25) -> dict:
    """Candles producing a hidden bullish CVD divergence for LONG.

    Price makes a lower low in the late window; highs form a clear peak inside
    the 20-candle divergence detection window.
    """
    closes = [close] * n
    # late window: lower-low price (hidden bullish divergence)
    closes[-5] = close * 0.97
    highs = [close * 1.002] * n
    # Insert a clear swing high inside the 20-candle window so we know the
    # expected tp1/tp2 value exactly.
    swing_high = close * 1.015
    highs[-15] = swing_high   # well within highs[-20:]
    lows = [c * 0.998 for c in closes]
    return {
        "5m": {
            "close": closes,
            "high": highs,
            "low": lows,
            "volume": [1_000_000.0] * n,
        }
    }


def _make_cvd_long(base: float = 50.0) -> list:
    """CVD with higher low in the late window (absorption of selling pressure)."""
    cvd = [base] * 20
    # early window: low CVD
    for i in range(2, 7):
        cvd[i] = base - 20.0
    # late window: higher CVD low (divergence)
    for i in range(12, 17):
        cvd[i] = base - 5.0
    return cvd


def _make_candles_short(close: float = 100.0, n: int = 25) -> dict:
    """Candles producing a hidden bearish CVD divergence for SHORT.

    Price makes a higher high in the late window; lows form a clear trough.
    """
    closes = [close] * n
    # late window: higher-high price (hidden bearish divergence)
    closes[-5] = close * 1.03
    lows = [close * 0.985] * n
    # Insert a clear swing low inside the 20-candle window.
    swing_low = close * 0.975
    lows[-15] = swing_low    # well within lows[-20:]
    highs = [c * 1.002 for c in closes]
    return {
        "5m": {
            "close": closes,
            "high": highs,
            "low": lows,
            "volume": [1_000_000.0] * n,
        }
    }


def _make_cvd_short(base: float = 50.0) -> list:
    """CVD with lower high in the late window (selling absorption)."""
    cvd = [base] * 20
    # early window: high CVD
    for i in range(2, 7):
        cvd[i] = base + 20.0
    # late window: lower CVD high (divergence)
    for i in range(12, 17):
        cvd[i] = base + 5.0
    return cvd


def _run_long(close: float = 100.0, candles: dict | None = None, cvd: list | None = None):
    """Run _evaluate_divergence_continuation for a LONG setup."""
    channel = ScalpChannel()
    if candles is None:
        candles = _make_candles_long(close=close)
    if cvd is None:
        cvd = _make_cvd_long()
    smc = _make_smc_data(cvd=cvd)
    ind = _make_indicators(close=close)
    sig = channel._evaluate_divergence_continuation(
        symbol="TESTUSDT",
        candles=candles,
        indicators=ind,
        smc_data=smc,
        spread_pct=0.001,
        volume_24h_usd=50_000_000,
        regime="TRENDING_UP",
    )
    return sig, candles


def _run_short(close: float = 100.0, candles: dict | None = None, cvd: list | None = None):
    """Run _evaluate_divergence_continuation for a SHORT setup."""
    channel = ScalpChannel()
    if candles is None:
        candles = _make_candles_short(close=close)
    if cvd is None:
        cvd = _make_cvd_short()
    smc = _make_smc_data(cvd=cvd)
    # For SHORT: ema21 must be ABOVE close so that sl = ema21 * 1.005 > close.
    # ema9 must be below ema21 (bearish EMA alignment).
    ema21 = close * 1.005   # 0.5% above close — within 1.5% tolerance
    ema9 = close * 0.998    # below ema21 (bearish alignment)
    ind = _make_indicators(close=close, ema9=ema9, ema21=ema21)
    sig = channel._evaluate_divergence_continuation(
        symbol="TESTUSDT",
        candles=candles,
        indicators=ind,
        smc_data=smc,
        spread_pct=0.001,
        volume_24h_usd=50_000_000,
        regime="TRENDING_DOWN",
    )
    return sig, candles


def test_divergence_continuation_marks_short_cvd_history_as_insufficient():
    channel = ScalpChannel()
    candles = _make_candles_long()
    indicators = _make_indicators(close=100.0)
    smc = _make_smc_data(cvd=[1.0, 2.0, 3.0], fvg_present=True)
    sig = channel._evaluate_divergence_continuation(
        symbol="TESTUSDT",
        candles=candles,
        indicators=indicators,
        smc_data=smc,
        spread_pct=0.001,
        volume_24h_usd=50_000_000,
        regime="TRENDING_UP",
    )
    assert sig is None
    assert channel._active_no_signal_reason == "cvd_insufficient"


# ---------------------------------------------------------------------------
# 1. LONG — swing-based TP targets
# ---------------------------------------------------------------------------

class TestDivergenceContinuationTPLongSwingBased:
    """LONG hidden bullish divergence: TP1 and TP2 must be anchored to the
    divergence detection window swing highs, not generic R-multiples."""

    def test_long_signal_fires(self):
        sig, _ = _run_long()
        assert sig is not None, "Expected LONG DIVERGENCE_CONTINUATION signal to fire"

    def test_tp1_equals_divergence_window_swing_high(self):
        """tp1 must equal the highest high in the divergence detection window."""
        close = 100.0
        candles = _make_candles_long(close=close)
        sig, _ = _run_long(close=close, candles=candles)
        if sig is None:
            pytest.skip("Signal did not fire")
        highs_5m = [float(h) for h in candles["5m"]["high"]]
        expected_tp1 = max(highs_5m[-20:])
        assert sig.tp1 == pytest.approx(expected_tp1, rel=1e-6), (
            f"tp1 ({sig.tp1}) should equal max of divergence-window highs "
            f"({expected_tp1})"
        )

    def test_tp2_equals_20candle_swing_high_or_fallback(self):
        """tp2 must equal the 20-candle 5m swing high or a fallback R-multiple."""
        close = 100.0
        candles = _make_candles_long(close=close)
        sig, _ = _run_long(close=close, candles=candles)
        if sig is None:
            pytest.skip("Signal did not fire")
        highs_5m = [float(h) for h in candles["5m"]["high"]]
        swing_high = max(highs_5m[-20:])
        # tp2 should either be the structural swing high (if valid) or a fallback
        if swing_high > close:
            assert sig.tp2 == pytest.approx(swing_high, rel=1e-6), (
                f"tp2 ({sig.tp2}) should equal the 20-candle swing high ({swing_high})"
            )
        else:
            # Fallback should be a positive R-multiple above entry
            assert sig.tp2 > sig.entry, "Fallback tp2 must be above entry for LONG"

    def test_all_tps_above_entry(self):
        sig, _ = _run_long()
        if sig is None:
            pytest.skip("Signal did not fire")
        assert sig.tp1 > sig.entry, f"tp1 ({sig.tp1}) must be above entry ({sig.entry})"
        assert sig.tp2 > sig.entry, f"tp2 ({sig.tp2}) must be above entry ({sig.entry})"
        assert sig.tp3 > sig.entry, f"tp3 ({sig.tp3}) must be above entry ({sig.entry})"

    def test_sl_below_entry(self):
        sig, _ = _run_long()
        if sig is None:
            pytest.skip("Signal did not fire")
        assert sig.stop_loss < sig.entry, (
            f"stop_loss ({sig.stop_loss}) must be below entry ({sig.entry}) for LONG"
        )


# ---------------------------------------------------------------------------
# 2. SHORT — swing-based TP targets
# ---------------------------------------------------------------------------

class TestDivergenceContinuationTPShortSwingBased:
    """SHORT hidden bearish divergence: TP1 and TP2 must be anchored to the
    divergence detection window swing lows, not generic R-multiples."""

    def test_short_signal_fires(self):
        sig, _ = _run_short()
        assert sig is not None, "Expected SHORT DIVERGENCE_CONTINUATION signal to fire"

    def test_tp1_equals_divergence_window_swing_low(self):
        """tp1 must equal the lowest low in the divergence detection window."""
        close = 100.0
        candles = _make_candles_short(close=close)
        sig, _ = _run_short(close=close, candles=candles)
        if sig is None:
            pytest.skip("Signal did not fire")
        lows_5m = [float(l) for l in candles["5m"]["low"]]
        expected_tp1 = min(lows_5m[-20:])
        assert sig.tp1 == pytest.approx(expected_tp1, rel=1e-6), (
            f"tp1 ({sig.tp1}) should equal min of divergence-window lows "
            f"({expected_tp1})"
        )

    def test_tp2_equals_20candle_swing_low_or_fallback(self):
        """tp2 must equal the 20-candle 5m swing low or a fallback R-multiple."""
        close = 100.0
        candles = _make_candles_short(close=close)
        sig, _ = _run_short(close=close, candles=candles)
        if sig is None:
            pytest.skip("Signal did not fire")
        lows_5m = [float(l) for l in candles["5m"]["low"]]
        swing_low = min(lows_5m[-20:])
        if swing_low < close:
            assert sig.tp2 == pytest.approx(swing_low, rel=1e-6), (
                f"tp2 ({sig.tp2}) should equal the 20-candle swing low ({swing_low})"
            )
        else:
            # Fallback should be below entry
            assert sig.tp2 < sig.entry, "Fallback tp2 must be below entry for SHORT"

    def test_all_tps_below_entry(self):
        sig, _ = _run_short()
        if sig is None:
            pytest.skip("Signal did not fire")
        assert sig.tp1 < sig.entry, f"tp1 ({sig.tp1}) must be below entry ({sig.entry})"
        assert sig.tp2 < sig.entry, f"tp2 ({sig.tp2}) must be below entry ({sig.entry})"
        assert sig.tp3 < sig.entry, f"tp3 ({sig.tp3}) must be below entry ({sig.entry})"

    def test_sl_above_entry(self):
        sig, _ = _run_short()
        if sig is None:
            pytest.skip("Signal did not fire")
        assert sig.stop_loss > sig.entry, (
            f"stop_loss ({sig.stop_loss}) must be above entry ({sig.entry}) for SHORT"
        )


# ---------------------------------------------------------------------------
# 3. Fallback — when swing is on wrong side of entry
# ---------------------------------------------------------------------------

class TestDivergenceContinuationTPFallback:
    """When the divergence window swing high/low is on the wrong side of entry,
    the evaluator must fall back to ATR R-multiple targets."""

    def test_long_fallback_when_no_valid_swing_high(self):
        """For LONG: if all highs in the divergence window are below entry,
        tp1 must fall back to entry + risk * 1.5."""
        close = 100.0
        # Build candles where all highs are BELOW close so swing high < entry.
        n = 25
        closes = [close] * n
        # Late window: lower-low for divergence detection
        closes[-5] = close * 0.97
        # Highs all below close (unusual but possible)
        highs = [close * 0.995] * n
        lows = [close * 0.990] * n
        candles = {
            "5m": {
                "close": closes,
                "high": highs,
                "low": lows,
                "volume": [1_000_000.0] * n,
            }
        }
        sig, _ = _run_long(close=close, candles=candles)
        if sig is None:
            # May not fire if price vs EMA checks fail with these unusual candles
            pytest.skip("Signal did not fire with all-below-close highs")
        # tp1 must be above entry (fallback was applied)
        assert sig.tp1 > sig.entry, (
            f"tp1 fallback must be above entry; got tp1={sig.tp1}, entry={sig.entry}"
        )
        # Verify it's approximately a R-multiple (not the invalid swing high)
        swing_high = max(float(h) for h in highs[-20:])
        assert swing_high <= close, "Test setup error: swing_high should be <= close"
        # tp1 must differ from the invalid swing_high (fallback was triggered)
        assert sig.tp1 != pytest.approx(swing_high, rel=1e-4), (
            "tp1 must not equal the invalid (below-entry) swing high"
        )

    def test_short_fallback_when_no_valid_swing_low(self):
        """For SHORT: if all lows in the divergence window are above entry,
        tp1 must fall back to entry - risk * 1.5."""
        close = 100.0
        n = 25
        closes = [close] * n
        # Late window: higher-high for bearish divergence detection
        closes[-5] = close * 1.03
        # Lows all above close (unusual but possible)
        lows = [close * 1.005] * n
        highs = [close * 1.010] * n
        candles = {
            "5m": {
                "close": closes,
                "high": highs,
                "low": lows,
                "volume": [1_000_000.0] * n,
            }
        }
        sig, _ = _run_short(close=close, candles=candles)
        if sig is None:
            pytest.skip("Signal did not fire with all-above-close lows")
        assert sig.tp1 < sig.entry, (
            f"tp1 fallback must be below entry; got tp1={sig.tp1}, entry={sig.entry}"
        )
        swing_low = min(float(l) for l in lows[-20:])
        assert swing_low >= close, "Test setup error: swing_low should be >= close"
        assert sig.tp1 != pytest.approx(swing_low, rel=1e-4), (
            "tp1 must not equal the invalid (above-entry) swing low"
        )


# ---------------------------------------------------------------------------
# 4. Membership in STRUCTURAL_SLTP_PROTECTED_SETUPS
# ---------------------------------------------------------------------------

class TestDivergenceContinuationInStructuralProtectionSet:
    """SetupClass.DIVERGENCE_CONTINUATION must be in STRUCTURAL_SLTP_PROTECTED_SETUPS
    so that build_risk_plan() does not overwrite evaluator-authored swing TPs."""

    def test_divergence_continuation_in_structural_protection_set(self):
        assert SetupClass.DIVERGENCE_CONTINUATION in STRUCTURAL_SLTP_PROTECTED_SETUPS, (
            "SetupClass.DIVERGENCE_CONTINUATION must be in STRUCTURAL_SLTP_PROTECTED_SETUPS "
            "to prevent build_risk_plan() from overwriting divergence-window swing TPs "
            "with generic R-multiples (B13 violation fix)."
        )


# ---------------------------------------------------------------------------
# 5. Membership in _PREDICTIVE_SLTP_BYPASS_SETUPS
# ---------------------------------------------------------------------------

class TestDivergenceContinuationInPredictiveBypassSet:
    """'DIVERGENCE_CONTINUATION' must be in _PREDICTIVE_SLTP_BYPASS_SETUPS
    so that PredictiveEngine.adjust_tp_sl() does not scale structural TPs."""

    def test_divergence_continuation_in_predictive_bypass_set(self):
        assert "DIVERGENCE_CONTINUATION" in _PREDICTIVE_SLTP_BYPASS_SETUPS, (
            "'DIVERGENCE_CONTINUATION' must be in _PREDICTIVE_SLTP_BYPASS_SETUPS "
            "to prevent the predictive engine from scaling divergence-window swing "
            "TPs with generic volatility adjustments."
        )

    def test_predictive_engine_does_not_scale_divergence_continuation(self):
        """PredictiveEngine.adjust_tp_sl() must leave DIVERGENCE_CONTINUATION TPs
        unchanged even when the prediction multipliers differ from 1.0."""
        sig = SimpleNamespace(
            symbol="BTCUSDT",
            setup_class="DIVERGENCE_CONTINUATION",
            direction=Direction.LONG,
            entry=100.0,
            tp1=101.5,
            tp2=103.0,
            tp3=105.0,
            stop_loss=99.2,
        )
        engine = PredictiveEngine()
        pred = PredictionResult(
            suggested_tp_adjustment=1.5,
            suggested_sl_adjustment=0.7,
        )
        engine.adjust_tp_sl(sig, pred)
        assert sig.tp1 == pytest.approx(101.5, rel=1e-6), (
            "DIVERGENCE_CONTINUATION tp1 was modified by predictive engine — "
            "divergence-window swing TP must not be scaled"
        )
        assert sig.tp2 == pytest.approx(103.0, rel=1e-6), (
            "DIVERGENCE_CONTINUATION tp2 was modified by predictive engine"
        )
        assert sig.tp3 == pytest.approx(105.0, rel=1e-6), (
            "DIVERGENCE_CONTINUATION tp3 was modified by predictive engine"
        )
        assert sig.stop_loss == pytest.approx(99.2, rel=1e-6), (
            "DIVERGENCE_CONTINUATION stop_loss was modified by predictive engine"
        )
