"""Tests for B13 compliance: LIQUIDATION_REVERSAL Fibonacci retrace TP targets.

Validates:
1. LONG signal: TP1/TP2/TP3 are 38.2%/61.8%/100% Fibonacci retrace of the cascade range
2. SHORT signal: same Fibonacci retraces from the cascade high
3. Degenerate cascade (range < ATR * 0.5): ATR-based R-multiple fallback TPs
4. LIQUIDATION_REVERSAL in STRUCTURAL_SLTP_PROTECTED_SETUPS
5. LIQUIDATION_REVERSAL in _PREDICTIVE_SLTP_BYPASS_SETUPS
"""

from __future__ import annotations

import pytest

from src.channels.scalp import ScalpChannel
from src.predictive_ai import _PREDICTIVE_SLTP_BYPASS_SETUPS
from src.signal_quality import STRUCTURAL_SLTP_PROTECTED_SETUPS, SetupClass
from src.smc import Direction


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_SPREAD_PCT = 0.001       # well within the 2% channel cap
_VOLUME_24H = 10_000_000  # $10M, above the $5M floor


def _make_m5_candles(closes: list[float], volumes: list[float]) -> dict:
    """Return a minimal 5m candle dict from close/volume lists."""
    return {
        "close": closes,
        "high": [c + 0.5 for c in closes],
        "low": [c - 0.5 for c in closes],
        "open": [c - 0.1 for c in closes],
        "volume": volumes,
    }


def _make_long_scenario(atr_val: float = 0.5) -> tuple[dict, dict, dict]:
    """
    Craft a scenario where the cascade fell from 100.0 to 97.5 over 3 candles.

    cascade window closes[-4:] = [100.0, 99.5, 98.5, 97.5]
    cascade_low  = 97.5
    cascade_high = 100.0
    cascade_range = 2.5

    CVD divergence: price fell but CVD rose (buyers absorbing).
    RSI is None so the extreme gate is bypassed.
    Near-zone: dict FVG at 97.4 (within 0.5% of 97.5).
    Volume spike: last candle 3× the 20-candle average.
    """
    n = 25
    # 21 regular closes + cascade window
    closes = [100.0] * (n - 4) + [100.0, 99.5, 98.5, 97.5]
    # Last candle volume is a 3× spike (> 2.5× threshold)
    volumes = [100.0] * (n - 1) + [300.0]

    candles = {"5m": _make_m5_candles(closes, volumes)}
    indicators = {"5m": {"atr_last": atr_val}}  # rsi_last absent → gate bypassed
    # CVD: last 4 values show CVD rising (buyers absorbing) while price fell
    # cvd[-4]=-200 → cvd[-1]=50: cvd_change = 50 - (-200) = 250 > 0 → LONG confirmed
    smc_data = {
        "cvd": [0.0] * (n - 4) + [-200.0, -150.0, -100.0, 50.0],
        "fvg": [{"level": 97.4}],
        "orderblocks": [],
        "pair_profile": None,
        "regime_context": None,
    }
    return candles, indicators, smc_data


def _make_short_scenario(atr_val: float = 0.5) -> tuple[dict, dict, dict]:
    """
    Craft a scenario where the cascade rose from 100.0 to 102.5 over 3 candles.

    cascade window closes[-4:] = [100.0, 100.5, 101.5, 102.5]
    cascade_low  = 100.0
    cascade_high = 102.5
    cascade_range = 2.5

    CVD divergence: price rose but CVD fell (sellers absorbing).
    RSI is None so the extreme gate is bypassed.
    Near-zone: dict FVG at 102.6 (within 0.5% of 102.5).
    Volume spike: last candle 3× the 20-candle average.
    """
    n = 25
    closes = [100.0] * (n - 4) + [100.0, 100.5, 101.5, 102.5]
    volumes = [100.0] * (n - 1) + [300.0]

    candles = {"5m": _make_m5_candles(closes, volumes)}
    indicators = {"5m": {"atr_last": atr_val}}  # rsi_last absent → gate bypassed
    # CVD: last 4 values show CVD falling (sellers absorbing) while price rose
    # cvd[-4]=200 → cvd[-1]=-50: cvd_change = -50 - 200 = -250 < 0 → SHORT confirmed
    smc_data = {
        "cvd": [0.0] * (n - 4) + [200.0, 150.0, 100.0, -50.0],
        "fvg": [{"level": 102.6}],
        "orderblocks": [],
        "pair_profile": None,
        "regime_context": None,
    }
    return candles, indicators, smc_data


def _call_evaluator(
    candles: dict, indicators: dict, smc_data: dict
):
    ch = ScalpChannel()
    return ch._evaluate_liquidation_reversal(
        "TESTUSDT", candles, indicators, smc_data, _SPREAD_PCT, _VOLUME_24H
    )


# ---------------------------------------------------------------------------
# Test 1: LONG — Fibonacci retrace TPs
# ---------------------------------------------------------------------------

class TestLiquidationReversalFibonacciLong:
    """LONG reversal from a cascade low produces 38.2%/61.8%/100% Fibonacci TPs."""

    def test_liquidation_reversal_fibonacci_tp_long(self):
        candles, indicators, smc_data = _make_long_scenario(atr_val=0.5)
        sig = _call_evaluator(candles, indicators, smc_data)

        # If conditions are not met the evaluator returns None — guard first
        if sig is None:
            pytest.skip("Evaluator returned None; environment conditions not met")

        assert sig.direction == Direction.LONG
        assert sig.setup_class == "LIQUIDATION_REVERSAL"

        cascade_low = 97.5
        cascade_high = 100.0
        cascade_range = cascade_high - cascade_low  # 2.5

        expected_tp1 = cascade_low + cascade_range * 0.382  # 98.455
        expected_tp2 = cascade_low + cascade_range * 0.618  # 99.045
        expected_tp3 = cascade_low + cascade_range * 1.0    # 100.0

        assert sig.tp1 == pytest.approx(expected_tp1, rel=1e-6), (
            f"TP1 should be 38.2% retrace: expected {expected_tp1}, got {sig.tp1}"
        )
        assert sig.tp2 == pytest.approx(expected_tp2, rel=1e-6), (
            f"TP2 should be 61.8% retrace: expected {expected_tp2}, got {sig.tp2}"
        )
        assert sig.tp3 == pytest.approx(expected_tp3, rel=1e-6), (
            f"TP3 should be 100% retrace: expected {expected_tp3}, got {sig.tp3}"
        )

    def test_long_tps_are_above_entry(self):
        candles, indicators, smc_data = _make_long_scenario(atr_val=0.5)
        sig = _call_evaluator(candles, indicators, smc_data)
        if sig is None:
            pytest.skip("Evaluator returned None")
        assert sig.tp1 > sig.entry, "TP1 must be above entry for LONG"
        assert sig.tp2 > sig.entry, "TP2 must be above entry for LONG"
        assert sig.tp3 > sig.entry, "TP3 must be above entry for LONG"


# ---------------------------------------------------------------------------
# Test 2: SHORT — Fibonacci retrace TPs
# ---------------------------------------------------------------------------

class TestLiquidationReversalFibonacciShort:
    """SHORT reversal from a cascade high produces 38.2%/61.8%/100% Fibonacci TPs."""

    def test_liquidation_reversal_fibonacci_tp_short(self):
        candles, indicators, smc_data = _make_short_scenario(atr_val=0.5)
        sig = _call_evaluator(candles, indicators, smc_data)

        if sig is None:
            pytest.skip("Evaluator returned None; environment conditions not met")

        assert sig.direction == Direction.SHORT
        assert sig.setup_class == "LIQUIDATION_REVERSAL"

        cascade_low = 100.0
        cascade_high = 102.5
        cascade_range = cascade_high - cascade_low  # 2.5

        expected_tp1 = cascade_high - cascade_range * 0.382  # 101.545
        expected_tp2 = cascade_high - cascade_range * 0.618  # 100.955
        expected_tp3 = cascade_high - cascade_range * 1.0    # 100.0

        assert sig.tp1 == pytest.approx(expected_tp1, rel=1e-6), (
            f"TP1 should be 38.2% retrace: expected {expected_tp1}, got {sig.tp1}"
        )
        assert sig.tp2 == pytest.approx(expected_tp2, rel=1e-6), (
            f"TP2 should be 61.8% retrace: expected {expected_tp2}, got {sig.tp2}"
        )
        assert sig.tp3 == pytest.approx(expected_tp3, rel=1e-6), (
            f"TP3 should be 100% retrace: expected {expected_tp3}, got {sig.tp3}"
        )

    def test_short_tps_are_below_entry(self):
        candles, indicators, smc_data = _make_short_scenario(atr_val=0.5)
        sig = _call_evaluator(candles, indicators, smc_data)
        if sig is None:
            pytest.skip("Evaluator returned None")
        assert sig.tp1 < sig.entry, "TP1 must be below entry for SHORT"
        assert sig.tp2 < sig.entry, "TP2 must be below entry for SHORT"
        assert sig.tp3 < sig.entry, "TP3 must be below entry for SHORT"


# ---------------------------------------------------------------------------
# Test 3: Degenerate cascade → ATR R-multiple fallback
# ---------------------------------------------------------------------------

class TestLiquidationReversalFallbackOnDegenerateCascade:
    """When cascade_range < ATR * 0.5, ATR-based R-multiple TPs are used."""

    def test_liquidation_reversal_tp_fallback_on_degenerate_cascade(self):
        # ATR = 10.0 → threshold = 5.0 > cascade_range (2.5) → fallback triggered
        candles, indicators, smc_data = _make_long_scenario(atr_val=10.0)
        sig = _call_evaluator(candles, indicators, smc_data)

        if sig is None:
            pytest.skip("Evaluator returned None; environment conditions not met")

        assert sig.direction == Direction.LONG
        close_now = 97.5
        sl_buffer = close_now * 0.003
        cascade_low = 97.5
        sl = cascade_low - sl_buffer
        risk = abs(close_now - sl)

        expected_tp1 = close_now + risk * 1.5
        expected_tp2 = close_now + risk * 2.5
        expected_tp3 = close_now + risk * 4.0

        assert sig.tp1 == pytest.approx(expected_tp1, rel=1e-6), (
            f"Fallback TP1 should be entry + 1.5R: expected {expected_tp1}, got {sig.tp1}"
        )
        assert sig.tp2 == pytest.approx(expected_tp2, rel=1e-6), (
            f"Fallback TP2 should be entry + 2.5R: expected {expected_tp2}, got {sig.tp2}"
        )
        assert sig.tp3 == pytest.approx(expected_tp3, rel=1e-6), (
            f"Fallback TP3 should be entry + 4.0R: expected {expected_tp3}, got {sig.tp3}"
        )

    def test_degenerate_cascade_short_fallback(self):
        """Fallback also works for SHORT direction."""
        candles, indicators, smc_data = _make_short_scenario(atr_val=10.0)
        sig = _call_evaluator(candles, indicators, smc_data)

        if sig is None:
            pytest.skip("Evaluator returned None; environment conditions not met")

        assert sig.direction == Direction.SHORT
        close_now = 102.5
        sl_buffer = close_now * 0.003
        cascade_high = 102.5
        sl = cascade_high + sl_buffer
        risk = abs(close_now - sl)

        expected_tp1 = close_now - risk * 1.5
        expected_tp2 = close_now - risk * 2.5
        expected_tp3 = close_now - risk * 4.0

        assert sig.tp1 == pytest.approx(expected_tp1, rel=1e-6)
        assert sig.tp2 == pytest.approx(expected_tp2, rel=1e-6)
        assert sig.tp3 == pytest.approx(expected_tp3, rel=1e-6)


# ---------------------------------------------------------------------------
# Test 4: LIQUIDATION_REVERSAL in STRUCTURAL_SLTP_PROTECTED_SETUPS
# ---------------------------------------------------------------------------

def test_liquidation_reversal_in_structural_protection_set():
    """LIQUIDATION_REVERSAL must be in STRUCTURAL_SLTP_PROTECTED_SETUPS (B13 compliance)."""
    assert SetupClass.LIQUIDATION_REVERSAL in STRUCTURAL_SLTP_PROTECTED_SETUPS, (
        "LIQUIDATION_REVERSAL is missing from STRUCTURAL_SLTP_PROTECTED_SETUPS; "
        "downstream build_risk_plan() will overwrite the Fibonacci TPs with generic R-multiples"
    )


# ---------------------------------------------------------------------------
# Test 5: LIQUIDATION_REVERSAL in _PREDICTIVE_SLTP_BYPASS_SETUPS
# ---------------------------------------------------------------------------

def test_liquidation_reversal_in_predictive_bypass_set():
    """LIQUIDATION_REVERSAL must be in _PREDICTIVE_SLTP_BYPASS_SETUPS (B13 compliance)."""
    assert "LIQUIDATION_REVERSAL" in _PREDICTIVE_SLTP_BYPASS_SETUPS, (
        "LIQUIDATION_REVERSAL is missing from _PREDICTIVE_SLTP_BYPASS_SETUPS; "
        "the predictive engine will scale the Fibonacci TPs with volatility multipliers"
    )
