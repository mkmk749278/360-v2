"""Tests for PR-14: RANGE_FADE dead code removal + FUNDING_EXTREME_SIGNAL protection.

Covers:
1. _RANGING_RANGE_FADE_CONF_BOOST constant is removed from scanner (dead code).
2. _apply_regime_channel_adjustments no longer exists in Scanner (dead method removed).
3. SetupClass.FUNDING_EXTREME_SIGNAL is in STRUCTURAL_SLTP_PROTECTED_SETUPS.
4. "FUNDING_EXTREME_SIGNAL" is in _PREDICTIVE_SLTP_BYPASS_SETUPS.
5. No regression: existing protected setups remain in both protection sets.
6. build_risk_plan preserves evaluator SL/TP for FUNDING_EXTREME_SIGNAL signals.
7. predictive_ai.adjust_tp_sl is a no-op for FUNDING_EXTREME_SIGNAL signals.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from src.predictive_ai import PredictiveEngine, PredictionResult, _PREDICTIVE_SLTP_BYPASS_SETUPS
from src.signal_quality import STRUCTURAL_SLTP_PROTECTED_SETUPS, SetupClass, build_risk_plan
from src.smc import Direction


# ---------------------------------------------------------------------------
# Shared helpers (modelled on test_pr02_structural_sltp_preservation.py)
# ---------------------------------------------------------------------------

def _signal_long(
    *,
    entry: float = 2000.0,
    stop_loss: float = 1975.0,   # 1.25% below entry — within 1.5% max SL cap
    tp1: float = 2100.0,
    tp2: float = 2300.0,
    tp3: float = 2500.0,
    setup_class: str = "FUNDING_EXTREME_SIGNAL",
    channel: str = "360_SCALP",
    symbol: str = "ETHUSDT",
) -> SimpleNamespace:
    return SimpleNamespace(
        channel=channel,
        direction=Direction.LONG,
        entry=entry,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=tp2,
        tp3=tp3,
        setup_class=setup_class,
        symbol=symbol,
        far_reclaim_level=0.0,
    )


def _indicators() -> dict:
    return {
        "5m": {
            "ema9_last": 2005.0,
            "ema21_last": 1990.0,
            "atr_last": 15.0,
            "momentum_last": 0.4,
            "bb_upper_last": 2050.0,
            "bb_mid_last": 2000.0,
            "bb_lower_last": 1950.0,
        },
    }


def _candles(base: float = 2000.0, n: int = 60) -> dict:
    close = [base + 0.2 * i for i in range(n)]
    return {
        "high": [c + 1.5 for c in close],
        "low":  [c - 1.5 for c in close],
        "close": close,
        "volume": [10_000.0] * n,
    }


def _smc() -> dict:
    return {
        "sweeps": [SimpleNamespace(direction=Direction.LONG, sweep_level=1920.0)],
        "mss": None,
        "fvg": [],
        "whale_alert": None,
        "volume_delta_spike": False,
    }


def _build(signal: SimpleNamespace, setup: SetupClass):
    return build_risk_plan(
        signal=signal,
        indicators=_indicators(),
        candles={"5m": _candles(base=signal.entry)},
        smc_data=_smc(),
        setup=setup,
        spread_pct=0.05,
        channel=signal.channel,
    )


# ---------------------------------------------------------------------------
# 1. Dead constant removed from scanner
# ---------------------------------------------------------------------------

class TestRangeFadeDeadConstantRemoved:
    """_RANGING_RANGE_FADE_CONF_BOOST must no longer be present in src.scanner."""

    def test_constant_not_exported(self):
        """_RANGING_RANGE_FADE_CONF_BOOST must be absent from src.scanner (PR-14)."""
        import src.scanner as scanner_mod
        assert not hasattr(scanner_mod, "_RANGING_RANGE_FADE_CONF_BOOST"), (
            "_RANGING_RANGE_FADE_CONF_BOOST is dead code for the permanently removed "
            "RANGE_FADE evaluator and must not exist in src.scanner (PR-14)."
        )


# ---------------------------------------------------------------------------
# 2. Dead method removed from Scanner class
# ---------------------------------------------------------------------------

class TestRangeFadeDeadMethodRemoved:
    """_apply_regime_channel_adjustments only existed to boost RANGE_FADE confidence.
    It must be removed entirely since RANGE_FADE is permanently gone."""

    def test_method_not_on_scanner_class(self):
        """Scanner must not have _apply_regime_channel_adjustments (PR-14)."""
        from src.scanner import Scanner
        assert not hasattr(Scanner, "_apply_regime_channel_adjustments"), (
            "_apply_regime_channel_adjustments only served the permanently removed "
            "RANGE_FADE evaluator and must be deleted (PR-14)."
        )


# ---------------------------------------------------------------------------
# 3. FUNDING_EXTREME_SIGNAL in STRUCTURAL_SLTP_PROTECTED_SETUPS
# ---------------------------------------------------------------------------

class TestFundingExtremeInStructuralProtection:
    """FUNDING_EXTREME_SIGNAL must be in STRUCTURAL_SLTP_PROTECTED_SETUPS (PR-14)."""

    def test_funding_extreme_in_structural_sltp_protected(self):
        assert SetupClass.FUNDING_EXTREME_SIGNAL in STRUCTURAL_SLTP_PROTECTED_SETUPS, (
            "SetupClass.FUNDING_EXTREME_SIGNAL must be in STRUCTURAL_SLTP_PROTECTED_SETUPS. "
            "Its liquidation-cluster SL and structural FVG/OB TP1 must not be overwritten "
            "by build_risk_plan's generic R-multiples (PR-14 audit finding)."
        )

    def test_structural_set_size_is_10(self):
        """STRUCTURAL_SLTP_PROTECTED_SETUPS must contain exactly 10 paths after PR-14."""
        assert len(STRUCTURAL_SLTP_PROTECTED_SETUPS) == 10, (
            f"Expected 10 protected setup classes, got {len(STRUCTURAL_SLTP_PROTECTED_SETUPS)}: "
            f"{STRUCTURAL_SLTP_PROTECTED_SETUPS}. "
            "If a new path was added, update this assertion and add a rationale."
        )


# ---------------------------------------------------------------------------
# 4. FUNDING_EXTREME_SIGNAL in _PREDICTIVE_SLTP_BYPASS_SETUPS
# ---------------------------------------------------------------------------

class TestFundingExtremeInPredictiveBypass:
    """'FUNDING_EXTREME_SIGNAL' must be in _PREDICTIVE_SLTP_BYPASS_SETUPS (PR-14)."""

    def test_funding_extreme_in_predictive_bypass(self):
        assert "FUNDING_EXTREME_SIGNAL" in _PREDICTIVE_SLTP_BYPASS_SETUPS, (
            "'FUNDING_EXTREME_SIGNAL' must be in _PREDICTIVE_SLTP_BYPASS_SETUPS. "
            "The predictive engine must not scale its liquidation-cluster SL and "
            "structural TP1 with generic volatility-based adjustments (PR-14 audit finding)."
        )

    def test_predictive_bypass_set_size_is_11(self):
        """_PREDICTIVE_SLTP_BYPASS_SETUPS must contain exactly 11 paths after PR-14."""
        assert len(_PREDICTIVE_SLTP_BYPASS_SETUPS) == 11, (
            f"Expected 11 bypass setup strings, got {len(_PREDICTIVE_SLTP_BYPASS_SETUPS)}: "
            f"{_PREDICTIVE_SLTP_BYPASS_SETUPS}. "
            "If a new path was added, update this assertion and add a rationale."
        )


# ---------------------------------------------------------------------------
# 5. Regression: existing protected setups must still be covered
# ---------------------------------------------------------------------------

class TestExistingProtectedSetupsUnchanged:
    """All paths that were in the protection sets before PR-14 must still be there."""

    _LEGACY_STRUCTURAL = {
        SetupClass.POST_DISPLACEMENT_CONTINUATION,
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.BREAKDOWN_SHORT,
        SetupClass.QUIET_COMPRESSION_BREAK,
        SetupClass.TREND_PULLBACK_EMA,
        SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
        SetupClass.SR_FLIP_RETEST,
        SetupClass.LIQUIDATION_REVERSAL,
        SetupClass.DIVERGENCE_CONTINUATION,
    }

    _LEGACY_PREDICTIVE_BYPASS = {
        "POST_DISPLACEMENT_CONTINUATION",
        "VOLUME_SURGE_BREAKOUT",
        "BREAKDOWN_SHORT",
        "QUIET_COMPRESSION_BREAK",
        "TREND_PULLBACK_EMA",
        "CONTINUATION_LIQUIDITY_SWEEP",
        "SR_FLIP_RETEST",
        "FAILED_AUCTION_RECLAIM",
        "LIQUIDATION_REVERSAL",
        "DIVERGENCE_CONTINUATION",
    }

    def test_all_legacy_structural_paths_still_present(self):
        missing = self._LEGACY_STRUCTURAL - STRUCTURAL_SLTP_PROTECTED_SETUPS
        assert not missing, (
            f"PR-14 must not weaken existing protections. Missing from "
            f"STRUCTURAL_SLTP_PROTECTED_SETUPS: {missing}"
        )

    def test_all_legacy_predictive_bypass_paths_still_present(self):
        missing = self._LEGACY_PREDICTIVE_BYPASS - _PREDICTIVE_SLTP_BYPASS_SETUPS
        assert not missing, (
            f"PR-14 must not weaken existing protections. Missing from "
            f"_PREDICTIVE_SLTP_BYPASS_SETUPS: {missing}"
        )


# ---------------------------------------------------------------------------
# 6. build_risk_plan preserves SL/TP for FUNDING_EXTREME_SIGNAL
# ---------------------------------------------------------------------------

class TestBuildRiskPlanPreservesFundingExtreme:
    """build_risk_plan must preserve evaluator SL/TP for FUNDING_EXTREME_SIGNAL."""

    def test_funding_extreme_sl_preserved(self):
        """build_risk_plan must preserve evaluator stop_loss for FUNDING_EXTREME_SIGNAL."""
        sig = _signal_long()
        risk = _build(sig, SetupClass.FUNDING_EXTREME_SIGNAL)
        assert risk.passed, f"FUNDING_EXTREME_SIGNAL risk plan failed: {risk.reason}"
        assert risk.stop_loss == pytest.approx(sig.stop_loss, rel=1e-6), (
            "build_risk_plan must preserve evaluator SL for FUNDING_EXTREME_SIGNAL "
            "(structural liquidation-cluster anchor must not be overwritten)."
        )

    def test_funding_extreme_tp1_preserved(self):
        """build_risk_plan must preserve evaluator TP1 for FUNDING_EXTREME_SIGNAL."""
        sig = _signal_long()
        risk = _build(sig, SetupClass.FUNDING_EXTREME_SIGNAL)
        assert risk.passed, f"FUNDING_EXTREME_SIGNAL risk plan failed: {risk.reason}"
        assert risk.tp1 == pytest.approx(sig.tp1, rel=1e-6), (
            "build_risk_plan must preserve evaluator TP1 for FUNDING_EXTREME_SIGNAL "
            "(structural FVG/OB target must not be overwritten by generic R-multiples)."
        )

    def test_funding_extreme_tp2_preserved(self):
        """build_risk_plan must preserve evaluator TP2 for FUNDING_EXTREME_SIGNAL."""
        sig = _signal_long()
        risk = _build(sig, SetupClass.FUNDING_EXTREME_SIGNAL)
        assert risk.passed, f"FUNDING_EXTREME_SIGNAL risk plan failed: {risk.reason}"
        assert risk.tp2 == pytest.approx(sig.tp2, rel=1e-6), (
            "build_risk_plan must preserve evaluator TP2 for FUNDING_EXTREME_SIGNAL."
        )

    def test_funding_extreme_tp3_preserved(self):
        """build_risk_plan must preserve evaluator TP3 for FUNDING_EXTREME_SIGNAL."""
        sig = _signal_long()
        risk = _build(sig, SetupClass.FUNDING_EXTREME_SIGNAL)
        assert risk.passed, f"FUNDING_EXTREME_SIGNAL risk plan failed: {risk.reason}"
        assert risk.tp3 == pytest.approx(sig.tp3, rel=1e-6), (
            "build_risk_plan must preserve evaluator TP3 for FUNDING_EXTREME_SIGNAL."
        )


# ---------------------------------------------------------------------------
# 7. predictive_ai.adjust_tp_sl is a no-op for FUNDING_EXTREME_SIGNAL
# ---------------------------------------------------------------------------

class TestPredictiveBypassFundingExtreme:
    """adjust_tp_sl must not modify SL/TP for FUNDING_EXTREME_SIGNAL signals."""

    def test_adjust_tp_sl_no_op_for_funding_extreme(self):
        """adjust_tp_sl must be a no-op when setup_class == FUNDING_EXTREME_SIGNAL."""
        sig = SimpleNamespace(
            symbol="ETHUSDT",
            setup_class="FUNDING_EXTREME_SIGNAL",
            direction=Direction.LONG,
            entry=2000.0,
            tp1=2100.0,
            tp2=2300.0,
            tp3=2500.0,
            stop_loss=1900.0,
        )
        engine = PredictiveEngine()
        pred = PredictionResult(
            suggested_tp_adjustment=1.5,
            suggested_sl_adjustment=0.7,
        )
        engine.adjust_tp_sl(sig, pred)
        assert sig.stop_loss == pytest.approx(1900.0, rel=1e-6), (
            "PredictiveEngine.adjust_tp_sl must not modify stop_loss for "
            "FUNDING_EXTREME_SIGNAL (bypass set must prevent scaling)."
        )
        assert sig.tp1 == pytest.approx(2100.0, rel=1e-6), (
            "PredictiveEngine.adjust_tp_sl must not modify tp1 for "
            "FUNDING_EXTREME_SIGNAL (bypass set must prevent scaling)."
        )
        assert sig.tp2 == pytest.approx(2300.0, rel=1e-6), (
            "PredictiveEngine.adjust_tp_sl must not modify tp2 for "
            "FUNDING_EXTREME_SIGNAL (bypass set must prevent scaling)."
        )

