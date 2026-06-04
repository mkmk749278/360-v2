"""Tests for trail_atr_multiplier — ATR-percentile → trail-width mapping (Fix B)."""

from __future__ import annotations

from config import (
    TRAIL_ATR_MULT_NORMAL,
    TRAIL_ATR_MULT_HIGH,
    TRAIL_ATR_MULT_EXTREME,
    TRAIL_ATR_PCTILE_HIGH,
    TRAIL_ATR_PCTILE_EXTREME,
    trail_atr_multiplier,
)


def test_normal_volatility_uses_normal_multiplier():
    assert trail_atr_multiplier(50.0) == TRAIL_ATR_MULT_NORMAL
    assert trail_atr_multiplier(0.0) == TRAIL_ATR_MULT_NORMAL


def test_high_volatility_band():
    assert trail_atr_multiplier(TRAIL_ATR_PCTILE_HIGH) == TRAIL_ATR_MULT_HIGH
    assert trail_atr_multiplier(TRAIL_ATR_PCTILE_EXTREME - 0.01) == TRAIL_ATR_MULT_HIGH


def test_extreme_volatility_band():
    assert trail_atr_multiplier(TRAIL_ATR_PCTILE_EXTREME) == TRAIL_ATR_MULT_EXTREME
    assert trail_atr_multiplier(100.0) == TRAIL_ATR_MULT_EXTREME


def test_monotonic_non_decreasing():
    prev = 0.0
    for pct in range(0, 101, 5):
        mult = trail_atr_multiplier(float(pct))
        assert mult >= prev
        prev = mult


def test_invalid_input_falls_back_to_normal():
    assert trail_atr_multiplier(None) == TRAIL_ATR_MULT_NORMAL  # type: ignore[arg-type]
    assert trail_atr_multiplier("nan") == TRAIL_ATR_MULT_NORMAL  # type: ignore[arg-type]
