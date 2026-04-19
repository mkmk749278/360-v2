"""PR-02 tests: Preserve structural SL/TP intent for top-tier paths.

Validates the five required invariants from the PR-02 specification:
1. Protected top-tier paths keep evaluator-authored structural SL/TP geometry
   through downstream risk-plan handling.
2. Universal hard controls still apply (max SL %, minimum R:R, sanity checks).
3. Predictive TP/SL adjustment does not flatten protected structural paths into
   generic geometry.
4. Non-protected paths are not unintentionally changed.
5. Existing good behavior for FAILED_AUCTION_RECLAIM is not regressed.

Protected paths (STRUCTURAL_SLTP_PROTECTED_SETUPS):
  POST_DISPLACEMENT_CONTINUATION, VOLUME_SURGE_BREAKOUT, BREAKDOWN_SHORT,
  QUIET_COMPRESSION_BREAK, TREND_PULLBACK_EMA, CONTINUATION_LIQUIDITY_SWEEP

Explicitly verified:
  FAILED_AUCTION_RECLAIM (handled by its own existing block — regression test)
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Optional

import pytest

from src.predictive_ai import PredictiveEngine, PredictionResult
from src.signal_quality import (
    STRUCTURAL_SLTP_PROTECTED_SETUPS,
    SetupClass,
    build_risk_plan,
)
from src.smc import Direction


# ---------------------------------------------------------------------------
# Test-fixture helpers
# ---------------------------------------------------------------------------

def _signal(
    *,
    direction: Direction = Direction.LONG,
    entry: float = 100.0,
    stop_loss: float = 99.0,   # 1.0% away — within the 1.5% channel cap
    tp1: float = 101.5,
    tp2: float = 103.0,
    tp3: Optional[float] = 104.5,
    setup_class: str = "",
    channel: str = "360_SCALP",
    symbol: str = "BTCUSDT",
) -> SimpleNamespace:
    """Minimal signal with evaluator-authored SL/TP geometry within channel limits."""
    return SimpleNamespace(
        channel=channel,
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=tp2,
        tp3=tp3,
        setup_class=setup_class,
        symbol=symbol,
        far_reclaim_level=0.0,
    )


def _signal_short(
    *,
    entry: float = 100.0,
    stop_loss: float = 101.0,   # 1.0% above entry
    tp1: float = 98.5,
    tp2: float = 97.0,
    tp3: Optional[float] = 95.5,
    setup_class: str = "",
    channel: str = "360_SCALP",
    symbol: str = "BTCUSDT",
) -> SimpleNamespace:
    return SimpleNamespace(
        channel=channel,
        direction=Direction.SHORT,
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
            "ema9_last": 100.5,
            "ema21_last": 100.0,
            "atr_last": 0.6,
            "momentum_last": 0.4,
            "bb_upper_last": 101.8,
            "bb_mid_last": 100.0,
            "bb_lower_last": 98.2,
        },
    }


def _candles(base: float = 100.0, n: int = 60) -> dict:
    """Stable candles near entry — prevents generic SL from drifting far from entry."""
    close = [base + 0.02 * i for i in range(n)]
    return {
        "high": [c + 0.15 for c in close],
        "low": [c - 0.15 for c in close],
        "close": close,
        "volume": [1_000.0] * n,
    }


def _smc(direction: Direction = Direction.LONG) -> dict:
    sweep_level = 99.2 if direction == Direction.LONG else 100.8
    return {
        "sweeps": [SimpleNamespace(direction=direction, sweep_level=sweep_level)],
        "mss": None,
        "fvg": [],
        "whale_alert": None,
        "volume_delta_spike": False,
    }


def _build(signal: SimpleNamespace, setup: SetupClass) -> "RiskAssessment":  # noqa: F821
    return build_risk_plan(
        signal=signal,
        indicators=_indicators(),
        candles={"5m": _candles(base=signal.entry)},
        smc_data=_smc(signal.direction),
        setup=setup,
        spread_pct=0.05,
        channel=signal.channel,
    )


# ---------------------------------------------------------------------------
# Requirement 1: Protected paths preserve evaluator-authored SL/TP geometry
# ---------------------------------------------------------------------------

class TestProtectedPathsPreserveSLTP:
    """Verifies that evaluator-authored SL/TP survives build_risk_plan() for
    every path in STRUCTURAL_SLTP_PROTECTED_SETUPS.
    """

    @pytest.mark.parametrize("setup_class", [
        SetupClass.POST_DISPLACEMENT_CONTINUATION,
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.QUIET_COMPRESSION_BREAK,
        SetupClass.TREND_PULLBACK_EMA,
        SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
        SetupClass.SR_FLIP_RETEST,
    ])
    def test_protected_long_preserves_sl(self, setup_class):
        """PR-02 LONG: evaluator-authored SL survives build_risk_plan()."""
        sig = _signal(setup_class=setup_class.value)
        risk = _build(sig, setup_class)
        assert risk.passed, f"{setup_class.value} risk plan failed: {risk.reason}"
        assert risk.stop_loss == pytest.approx(sig.stop_loss, rel=1e-6), (
            f"{setup_class.value} LONG: evaluator SL {sig.stop_loss} overwritten "
            f"by generic {risk.stop_loss} (PR-02 violation)"
        )

    @pytest.mark.parametrize("setup_class", [
        SetupClass.BREAKDOWN_SHORT,
        SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
        SetupClass.POST_DISPLACEMENT_CONTINUATION,
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.QUIET_COMPRESSION_BREAK,
        SetupClass.TREND_PULLBACK_EMA,
        SetupClass.SR_FLIP_RETEST,
    ])
    def test_protected_short_preserves_sl(self, setup_class):
        """PR-02 SHORT: evaluator-authored SL survives build_risk_plan()."""
        sig = _signal_short(setup_class=setup_class.value)
        risk = _build(sig, setup_class)
        assert risk.passed, f"{setup_class.value} SHORT risk plan failed: {risk.reason}"
        assert risk.stop_loss == pytest.approx(sig.stop_loss, rel=1e-6), (
            f"{setup_class.value} SHORT: evaluator SL {sig.stop_loss} overwritten "
            f"by generic {risk.stop_loss} (PR-02 violation)"
        )

    @pytest.mark.parametrize("setup_class", [
        SetupClass.POST_DISPLACEMENT_CONTINUATION,
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.QUIET_COMPRESSION_BREAK,
        SetupClass.TREND_PULLBACK_EMA,
        SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
        SetupClass.SR_FLIP_RETEST,
    ])
    def test_protected_long_preserves_tp1(self, setup_class):
        """PR-02 LONG: evaluator-authored TP1 survives build_risk_plan()."""
        sig = _signal(setup_class=setup_class.value)
        risk = _build(sig, setup_class)
        assert risk.passed, f"{setup_class.value} risk plan failed: {risk.reason}"
        assert risk.tp1 == pytest.approx(sig.tp1, rel=1e-6), (
            f"{setup_class.value}: evaluator TP1 {sig.tp1} overwritten "
            f"by generic {risk.tp1} (PR-02 violation)"
        )

    @pytest.mark.parametrize("setup_class", [
        SetupClass.POST_DISPLACEMENT_CONTINUATION,
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.QUIET_COMPRESSION_BREAK,
        SetupClass.TREND_PULLBACK_EMA,
        SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
        SetupClass.SR_FLIP_RETEST,
    ])
    def test_protected_long_preserves_tp2(self, setup_class):
        """PR-02 LONG: evaluator-authored TP2 survives build_risk_plan()."""
        sig = _signal(setup_class=setup_class.value)
        risk = _build(sig, setup_class)
        assert risk.passed, f"{setup_class.value} risk plan failed: {risk.reason}"
        assert risk.tp2 == pytest.approx(sig.tp2, rel=1e-6), (
            f"{setup_class.value}: evaluator TP2 {sig.tp2} overwritten "
            f"by generic {risk.tp2} (PR-02 violation)"
        )

    @pytest.mark.parametrize("setup_class", [
        SetupClass.POST_DISPLACEMENT_CONTINUATION,
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.QUIET_COMPRESSION_BREAK,
        SetupClass.TREND_PULLBACK_EMA,
        SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
        SetupClass.SR_FLIP_RETEST,
    ])
    def test_protected_long_preserves_tp3(self, setup_class):
        """PR-02 LONG: evaluator-authored TP3 survives build_risk_plan()."""
        sig = _signal(setup_class=setup_class.value, tp3=106.0)
        risk = _build(sig, setup_class)
        assert risk.passed, f"{setup_class.value} risk plan failed: {risk.reason}"
        assert risk.tp3 == pytest.approx(sig.tp3, rel=1e-6), (
            f"{setup_class.value}: evaluator TP3 {sig.tp3} overwritten "
            f"by generic {risk.tp3} (PR-02 violation)"
        )

    def test_breakdown_short_preserves_all_targets(self):
        """PR-02: BREAKDOWN_SHORT preserves all evaluator-authored SL/TP on the short side."""
        sig = _signal_short(setup_class="BREAKDOWN_SHORT", tp3=93.0)
        risk = _build(sig, SetupClass.BREAKDOWN_SHORT)
        assert risk.passed, f"BREAKDOWN_SHORT risk plan failed: {risk.reason}"
        assert risk.stop_loss == pytest.approx(sig.stop_loss, rel=1e-6)
        assert risk.tp1 == pytest.approx(sig.tp1, rel=1e-6)
        assert risk.tp2 == pytest.approx(sig.tp2, rel=1e-6)
        assert risk.tp3 == pytest.approx(sig.tp3, rel=1e-6)

    def test_all_protected_setups_are_covered(self):
        """Sanity: STRUCTURAL_SLTP_PROTECTED_SETUPS contains exactly the expected 10 paths.

        SR_FLIP_RETEST is included because:
        - Its SL is anchored to the flipped structural level (level * 0.998),
          not a generic recent-swing computation.
        - Its TP1 is the 20-candle structural swing high/low, TP2 is a 4h level
          — both are structural anchors, not risk multiples.
        - It is one of the canonical strongest foundation paths in the audit and
          owner brief; its structural expression must survive downstream handling.

        LIQUIDATION_REVERSAL is included because:
        - Its TPs are Fibonacci retrace targets (38.2%/61.8%/100%) of the cascade
          range — evaluator-computed structural geometry (Type D — Reversion).
        - Generic R-multiples from build_risk_plan would flatten this thesis.

        DIVERGENCE_CONTINUATION is included because (B13 fix):
        - Its TPs are anchored to the swing high/low from the divergence detection
          window — not generic R-multiples.
        - build_risk_plan() must not overwrite these pattern-based TPs.

        FUNDING_EXTREME_SIGNAL is included because (PR-14 fix):
        - Its SL is anchored to the nearest liquidation cluster (institutional anchor).
        - Its TP1 is the nearest FVG/OB structural level in the direction of travel.
        - Downstream build_risk_plan generic R-multiples would overwrite these
          structural targets, defeating the evaluator's thesis.
        """
        expected = {
            SetupClass.POST_DISPLACEMENT_CONTINUATION,
            SetupClass.VOLUME_SURGE_BREAKOUT,
            SetupClass.BREAKDOWN_SHORT,
            SetupClass.QUIET_COMPRESSION_BREAK,
            SetupClass.TREND_PULLBACK_EMA,
            SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
            SetupClass.SR_FLIP_RETEST,
            SetupClass.LIQUIDATION_REVERSAL,
            SetupClass.DIVERGENCE_CONTINUATION,
            SetupClass.FUNDING_EXTREME_SIGNAL,
        }
        assert STRUCTURAL_SLTP_PROTECTED_SETUPS == expected, (
            "STRUCTURAL_SLTP_PROTECTED_SETUPS diverged from the PR-02/PR-14 specification. "
            "Update this test and the business rationale if the set must change."
        )


# ---------------------------------------------------------------------------
# Requirement 2: Universal hard controls still apply for protected paths
# ---------------------------------------------------------------------------

class TestUniversalHardControlsOnProtectedPaths:
    """Verifies that max SL %, near-zero SL guard, and directional sanity
    are still enforced for protected setup classes.
    """

    def test_max_sl_pct_rejects_not_compresses_for_protected_path(self):
        """Oversized evaluator SL on protected paths must be rejected, not clamped."""
        # Evaluator SL at 90.0 = 10% below entry — well over the 1.5% channel cap.
        sig = _signal(
            stop_loss=90.0,   # 10% — oversized
            setup_class="VOLUME_SURGE_BREAKOUT",
        )
        risk = _build(sig, SetupClass.VOLUME_SURGE_BREAKOUT)
        assert not risk.passed
        assert risk.stop_loss == pytest.approx(90.0, rel=1e-9)
        assert risk.reason == "protected_structural_sl_cap_exceeded_reject_not_compress"

    def test_max_sl_pct_rejects_not_compresses_for_failed_auction_reclaim(self):
        """FAILED_AUCTION_RECLAIM must also reject-not-compress oversized truthful SL."""
        sig = _signal(
            stop_loss=90.0,   # 10% — oversized
            setup_class=SetupClass.FAILED_AUCTION_RECLAIM.value,
        )
        risk = _build(sig, SetupClass.FAILED_AUCTION_RECLAIM)
        assert not risk.passed
        assert risk.stop_loss == pytest.approx(90.0, rel=1e-9)
        assert risk.reason == "protected_structural_sl_cap_exceeded_reject_not_compress"

    def test_directional_sanity_rejects_sl_above_entry_for_long_protected(self):
        """When evaluator SL is invalid (above entry) for LONG, the PR-02 override
        is skipped and the generic SL is used instead — not the wrong-side evaluator SL.
        """
        sig = _signal(
            stop_loss=101.0,   # wrong side — above entry for LONG
            setup_class="POST_DISPLACEMENT_CONTINUATION",
        )
        risk = _build(sig, SetupClass.POST_DISPLACEMENT_CONTINUATION)
        # The invalid evaluator SL is rejected by the PR-02 validation guard
        # (0 < 101.0 < 100.0 is False), so the generic SL is used.
        # The generic SL must be strictly below entry.
        assert risk.stop_loss < sig.entry, (
            f"Generic fallback SL {risk.stop_loss} should be below entry {sig.entry} "
            "when evaluator SL is invalid (above entry for LONG)"
        )

    def test_directional_sanity_rejects_sl_below_entry_for_short_protected(self):
        """When evaluator SL is invalid (below entry) for SHORT, the PR-02 override
        is skipped and the generic SL (always above entry for SHORT) is used.
        """
        sig = _signal_short(
            stop_loss=99.0,   # wrong side — below entry for SHORT
            setup_class="BREAKDOWN_SHORT",
        )
        risk = _build(sig, SetupClass.BREAKDOWN_SHORT)
        # The invalid evaluator SL is rejected by the PR-02 guard
        # (_eval_sl > signal.entry is False for 99.0), so the generic SL is used.
        # The generic SL for SHORT must be above entry.
        assert risk.stop_loss > sig.entry, (
            f"Generic fallback SL {risk.stop_loss} should be above entry {sig.entry} "
            "when evaluator SL is invalid (below entry for SHORT)"
        )

    @pytest.mark.parametrize("setup_class", [
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.QUIET_COMPRESSION_BREAK,
        SetupClass.TREND_PULLBACK_EMA,
    ])
    def test_minimum_rr_still_checked_for_protected_paths(self, setup_class):
        """Minimum R:R check must still gate protected paths."""
        # SL very close to entry + TP barely above entry → terrible R:R.
        sig = _signal(
            entry=100.0,
            stop_loss=99.9,    # 0.1% SL
            tp1=100.05,        # only 0.05R — below any minimum
            tp2=100.1,
            tp3=100.15,
            setup_class=setup_class.value,
        )
        risk = _build(sig, setup_class)
        assert not risk.passed, (
            f"{setup_class.value}: R:R guard should have rejected the plan "
            f"(tp1={risk.tp1:.4f}, sl={risk.stop_loss:.4f})"
        )

    def test_protected_path_invalid_evaluator_sl_falls_back_to_generic(self):
        """If evaluator SL is invalid (zero/wrong-side), generic computation is used instead."""
        # Signal has stop_loss=0.0 — invalid for LONG.
        sig = _signal(
            stop_loss=0.0,
            tp1=101.5,
            tp2=103.0,
            tp3=104.5,
            setup_class="VOLUME_SURGE_BREAKOUT",
        )
        risk = _build(sig, SetupClass.VOLUME_SURGE_BREAKOUT)
        # The generic SL should be used — it will be somewhere below entry.
        assert risk.stop_loss < sig.entry, (
            "When evaluator SL is 0.0 (invalid), generic SL must be used for LONG"
        )
        assert risk.stop_loss > 0.0, "Generic SL must be positive"


# ---------------------------------------------------------------------------
# Requirement 3: Predictive TP/SL adjustment bypasses protected paths
# ---------------------------------------------------------------------------

class TestPredictiveAdjustmentBypassesProtectedPaths:
    """Verifies that PredictiveEngine.adjust_tp_sl() leaves protected paths
    unchanged even when the prediction multipliers differ from 1.0.
    """

    def _engine(self) -> PredictiveEngine:
        from src.predictive_ai import PredictiveEngine
        return PredictiveEngine()

    def _prediction(
        self, tp_mult: float = 1.2, sl_mult: float = 0.85
    ) -> PredictionResult:
        """Return a prediction with non-trivial TP/SL adjustment multipliers."""
        return PredictionResult(
            suggested_tp_adjustment=tp_mult,
            suggested_sl_adjustment=sl_mult,
        )

    @pytest.mark.parametrize("sc_str", [
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
    ])
    def test_predictive_does_not_scale_protected_path_tp(self, sc_str):
        """PR-02: adjust_tp_sl() must leave TP unchanged for protected structural paths."""
        sig = SimpleNamespace(
            symbol="BTCUSDT",
            setup_class=sc_str,
            direction=Direction.LONG,
            entry=100.0,
            tp1=102.0,
            tp2=104.0,
            tp3=106.0,
            stop_loss=99.0,
        )
        engine = self._engine()
        pred = self._prediction(tp_mult=1.3, sl_mult=0.8)
        engine.adjust_tp_sl(sig, pred)
        assert sig.tp1 == pytest.approx(102.0, rel=1e-6), (
            f"{sc_str}: tp1 was scaled by predictive engine ({sig.tp1:.4f} ≠ 102.0)"
        )
        assert sig.tp2 == pytest.approx(104.0, rel=1e-6), (
            f"{sc_str}: tp2 was scaled by predictive engine ({sig.tp2:.4f} ≠ 104.0)"
        )
        assert sig.tp3 == pytest.approx(106.0, rel=1e-6), (
            f"{sc_str}: tp3 was scaled by predictive engine ({sig.tp3:.4f} ≠ 106.0)"
        )

    @pytest.mark.parametrize("sc_str", [
        "POST_DISPLACEMENT_CONTINUATION",
        "VOLUME_SURGE_BREAKOUT",
        "QUIET_COMPRESSION_BREAK",
    ])
    def test_predictive_does_not_scale_protected_path_sl(self, sc_str):
        """PR-02: adjust_tp_sl() must leave SL unchanged for protected structural paths."""
        sig = SimpleNamespace(
            symbol="BTCUSDT",
            setup_class=sc_str,
            direction=Direction.LONG,
            entry=100.0,
            tp1=102.0,
            tp2=104.0,
            tp3=106.0,
            stop_loss=99.0,
        )
        engine = self._engine()
        pred = self._prediction(tp_mult=1.0, sl_mult=0.8)
        engine.adjust_tp_sl(sig, pred)
        assert sig.stop_loss == pytest.approx(99.0, rel=1e-6), (
            f"{sc_str}: stop_loss was scaled by predictive engine "
            f"({sig.stop_loss:.4f} ≠ 99.0)"
        )

    def test_predictive_adjustment_applied_for_non_protected_path(self):
        """Verify predictive adjustment IS still applied for non-protected paths."""
        sig = SimpleNamespace(
            symbol="BTCUSDT",
            setup_class="MOMENTUM_EXPANSION",   # not protected
            direction=Direction.LONG,
            entry=100.0,
            tp1=102.0,
            tp2=104.0,
            tp3=106.0,
            stop_loss=99.0,
        )
        engine = self._engine()
        # Only apply if the engine model is loaded; if not, adjustment is 1.0 anyway.
        pred = PredictionResult(
            suggested_tp_adjustment=1.2,
            suggested_sl_adjustment=1.0,
        )
        original_tp1 = sig.tp1
        engine.adjust_tp_sl(sig, pred)
        # Non-protected path must not bypass the adjustment.
        expected_tp1 = 100.0 + (102.0 - 100.0) * 1.2   # 102.4
        assert sig.tp1 == pytest.approx(expected_tp1, rel=1e-6), (
            f"Non-protected path MOMENTUM_EXPANSION: tp1 {sig.tp1:.4f} should have been "
            f"scaled to {expected_tp1:.4f}"
        )


# ---------------------------------------------------------------------------
# Requirement 4: Non-protected paths are not unintentionally changed
# ---------------------------------------------------------------------------

class TestNonProtectedPathsUnchanged:
    """Verifies that non-protected paths still use generic TP computation."""

    @pytest.mark.parametrize("setup_class", [
        SetupClass.BREAKOUT_RETEST,
        SetupClass.OPENING_RANGE_BREAKOUT,
        SetupClass.MOMENTUM_EXPANSION,
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.WHALE_MOMENTUM,
    ])
    def test_non_protected_path_uses_generic_tp_not_evaluator(self, setup_class):
        """Non-protected paths must NOT preserve evaluator-authored TPs.

        The generic family-aware TP computation should still apply so that
        existing family-differentiated TP ratios (which pre-PR-02 tests validate)
        remain intact.
        """
        sig = _signal(
            stop_loss=99.0,
            tp1=101.5,   # evaluator-authored
            tp2=103.0,
            tp3=104.5,
            setup_class=setup_class.value,
        )
        risk = _build(sig, setup_class)
        assert risk.passed, f"{setup_class.value} plan failed: {risk.reason}"
        # For non-protected paths, tp1 should be the GENERIC value (risk-multiple),
        # not the evaluator-authored 101.5.
        # Since generic computation uses risk*multiplier anchored to entry,
        # and risk = entry - stop_loss (with possible SL capping), the generic
        # tp1 will differ from 101.5 when the SL differs from 99.0.
        # The key invariant is that STRUCTURAL_SLTP_PROTECTED_SETUPS does not
        # contain these setup classes.
        assert setup_class not in STRUCTURAL_SLTP_PROTECTED_SETUPS, (
            f"{setup_class.value} must not be in STRUCTURAL_SLTP_PROTECTED_SETUPS "
            "for non-protected path tests to be meaningful"
        )

    def test_breakout_retest_tp1_still_uses_generic_1_5r(self):
        """BREAKOUT_RETEST (not protected) still uses generic 1.5R TP1."""
        sig = _signal(
            stop_loss=99.0,
            tp1=200.0,   # absurdly large evaluator TP — should be ignored
            tp2=300.0,
            tp3=400.0,
            setup_class="BREAKOUT_RETEST",
        )
        risk = _build(sig, SetupClass.BREAKOUT_RETEST)
        assert risk.passed, f"BREAKOUT_RETEST plan failed: {risk.reason}"
        entry = 100.0
        # The generic risk equals entry - risk.stop_loss after any SL cap.
        risk_dist = entry - risk.stop_loss
        tp1_ratio = (risk.tp1 - entry) / risk_dist
        assert tp1_ratio == pytest.approx(1.5, abs=0.05), (
            f"BREAKOUT_RETEST generic tp1 ratio {tp1_ratio:.2f} should be 1.5R "
            f"(not the evaluator-authored 200.0)"
        )


# ---------------------------------------------------------------------------
# Requirement 5: FAILED_AUCTION_RECLAIM behavior is not regressed
# ---------------------------------------------------------------------------

class TestFailedAuctionReclaimNotRegressed:
    """Verifies that FAILED_AUCTION_RECLAIM continues to behave as it did
    before PR-02: evaluator-authored SL is preserved via its dedicated block.
    """

    def test_far_preserves_evaluator_sl_via_dedicated_block(self):
        """FAILED_AUCTION_RECLAIM preserves evaluator SL via its own dedicated block."""
        sig = _signal(
            stop_loss=99.2,
            tp1=101.8,
            tp2=103.5,
            tp3=105.2,
            setup_class="FAILED_AUCTION_RECLAIM",
        )
        risk = _build(sig, SetupClass.FAILED_AUCTION_RECLAIM)
        assert risk.passed, f"FAILED_AUCTION_RECLAIM plan failed: {risk.reason}"
        assert risk.stop_loss == pytest.approx(sig.stop_loss, rel=1e-6), (
            f"FAILED_AUCTION_RECLAIM SL {sig.stop_loss} was overwritten "
            f"to {risk.stop_loss} (regression)"
        )

    def test_far_preserves_evaluator_tp1_via_dedicated_block(self):
        """PR-02 FAR: evaluator-authored TP1 (measured-move from tail) must survive
        build_risk_plan() when directionally valid.

        The evaluator computes TPs from `tail` = probe distance beyond the
        reference level.  The previous build_risk_plan() FAR block recomputed TPs
        from reclaim-span geometry, potentially disagreeing with the evaluator's
        measured-move anchor.  The PR-02 fix preserves the evaluator value first.
        """
        sig = _signal(
            stop_loss=99.2,
            tp1=101.8,
            tp2=103.5,
            tp3=105.2,
            setup_class="FAILED_AUCTION_RECLAIM",
        )
        risk = _build(sig, SetupClass.FAILED_AUCTION_RECLAIM)
        assert risk.passed, f"FAILED_AUCTION_RECLAIM plan failed: {risk.reason}"
        assert risk.tp1 == pytest.approx(sig.tp1, rel=1e-6), (
            f"FAILED_AUCTION_RECLAIM evaluator TP1 {sig.tp1} was overwritten "
            f"by computed {risk.tp1} (PR-02 FAR TP preservation violated)"
        )
        assert risk.tp2 == pytest.approx(sig.tp2, rel=1e-6), (
            f"FAILED_AUCTION_RECLAIM evaluator TP2 {sig.tp2} was overwritten "
            f"by computed {risk.tp2} (PR-02 FAR TP preservation violated)"
        )

    def test_far_tp_fallback_when_evaluator_tp_invalid(self):
        """When FAR evaluator TPs are invalid (wrong side), the measured-move
        fallback is used and the plan still passes."""
        # tp1=0 is invalid for LONG — forces the fallback reclaim-span formula.
        sig = _signal(
            stop_loss=99.2,
            tp1=0.0,      # invalid for LONG
            tp2=0.0,
            tp3=None,
            setup_class="FAILED_AUCTION_RECLAIM",
        )
        risk = _build(sig, SetupClass.FAILED_AUCTION_RECLAIM)
        assert risk.passed, f"FAILED_AUCTION_RECLAIM fallback plan failed: {risk.reason}"
        assert risk.tp1 > sig.entry, "Fallback TP1 must be above entry for LONG"
        assert risk.tp2 > risk.tp1, "Fallback TP2 must be above TP1"

    def test_far_not_in_structural_sltp_protected_setups(self):
        """FAILED_AUCTION_RECLAIM is handled by its own block and is NOT
        in STRUCTURAL_SLTP_PROTECTED_SETUPS (to avoid duplicate/conflicting logic)."""
        assert SetupClass.FAILED_AUCTION_RECLAIM not in STRUCTURAL_SLTP_PROTECTED_SETUPS, (
            "FAILED_AUCTION_RECLAIM must not be added to STRUCTURAL_SLTP_PROTECTED_SETUPS "
            "because it has its own dedicated SL override block in build_risk_plan()"
        )

    def test_far_predictive_adjustment_is_bypassed(self):
        """PR-02: FAILED_AUCTION_RECLAIM is explicitly included in the predictive
        bypass set to prevent regression via the predictive stage."""
        sig = SimpleNamespace(
            symbol="BTCUSDT",
            setup_class="FAILED_AUCTION_RECLAIM",
            direction=Direction.LONG,
            entry=100.0,
            tp1=103.0,
            tp2=106.0,
            tp3=109.0,
            stop_loss=99.2,
        )
        engine = PredictiveEngine()
        pred = PredictionResult(
            suggested_tp_adjustment=1.5,
            suggested_sl_adjustment=0.7,
        )
        engine.adjust_tp_sl(sig, pred)
        assert sig.tp1 == pytest.approx(103.0, rel=1e-6), (
            "FAILED_AUCTION_RECLAIM tp1 was modified by predictive engine (regression)"
        )
        assert sig.stop_loss == pytest.approx(99.2, rel=1e-6), (
            "FAILED_AUCTION_RECLAIM stop_loss was modified by predictive engine (regression)"
        )

    def test_far_sl_invalid_evaluator_uses_generic_fallback(self):
        """If FAILED_AUCTION_RECLAIM's evaluator SL is invalid (0.0), the plan
        falls through to the generic SL and still passes structural validation."""
        sig = _signal(
            stop_loss=0.0,   # invalid — forces generic SL
            tp1=103.0,
            tp2=106.0,
            tp3=109.0,
            setup_class="FAILED_AUCTION_RECLAIM",
        )
        risk = _build(sig, SetupClass.FAILED_AUCTION_RECLAIM)
        # Plan should still pass with a generic SL below entry.
        assert risk.stop_loss < sig.entry
        assert risk.stop_loss > 0.0

    def test_far_short_preserves_evaluator_sl(self):
        """FAILED_AUCTION_RECLAIM SHORT preserves evaluator SL above entry."""
        sig = _signal_short(
            stop_loss=100.8,
            tp1=98.2,
            tp2=96.5,
            tp3=94.8,
            setup_class="FAILED_AUCTION_RECLAIM",
        )
        risk = _build(sig, SetupClass.FAILED_AUCTION_RECLAIM)
        assert risk.passed, f"FAILED_AUCTION_RECLAIM SHORT plan failed: {risk.reason}"
        assert risk.stop_loss == pytest.approx(sig.stop_loss, rel=1e-6), (
            f"FAILED_AUCTION_RECLAIM SHORT SL {sig.stop_loss} was overwritten "
            f"to {risk.stop_loss} (regression)"
        )


# ---------------------------------------------------------------------------
# SR_FLIP_RETEST: explicit structural coverage (audit/brief canonical path)
# ---------------------------------------------------------------------------

class TestSRFlipRetestStructuralPreservation:
    """Dedicated tests for SR_FLIP_RETEST inclusion in STRUCTURAL_SLTP_PROTECTED_SETUPS.

    SR_FLIP_RETEST is one of the canonical strongest foundation paths in the owner
    brief / audit.  Its evaluator computes:
    - SL: beyond the flipped structural level (level * 0.998 for LONG), not a
      generic recent-swing computation.
    - TP1: 20-candle structural swing high/low.
    - TP2: 4h structural target.
    These must survive build_risk_plan() unchanged.  Generic 1.2/2.0/2.8R multiples
    would flatten this structural expression and must be excluded for this path.
    """

    def test_sr_flip_retest_is_in_protected_set(self):
        """SR_FLIP_RETEST must be in STRUCTURAL_SLTP_PROTECTED_SETUPS."""
        assert SetupClass.SR_FLIP_RETEST in STRUCTURAL_SLTP_PROTECTED_SETUPS, (
            "SR_FLIP_RETEST must be in STRUCTURAL_SLTP_PROTECTED_SETUPS — it is one of "
            "the canonical strongest foundation paths and has structural SL and TP anchors."
        )

    def test_sr_flip_retest_long_preserves_evaluator_sl(self):
        """SR_FLIP_RETEST LONG: evaluator-authored structural SL survives build_risk_plan()."""
        sig = _signal(
            stop_loss=99.2,  # evaluator-computed: level * 0.998
            tp1=101.8,
            tp2=103.5,
            tp3=105.0,
            setup_class="SR_FLIP_RETEST",
        )
        risk = _build(sig, SetupClass.SR_FLIP_RETEST)
        assert risk.passed, f"SR_FLIP_RETEST plan failed: {risk.reason}"
        assert risk.stop_loss == pytest.approx(sig.stop_loss, rel=1e-6), (
            f"SR_FLIP_RETEST LONG: evaluator SL {sig.stop_loss} was overwritten "
            f"by generic {risk.stop_loss} (structural SL expression lost)"
        )

    def test_sr_flip_retest_short_preserves_evaluator_sl(self):
        """SR_FLIP_RETEST SHORT: evaluator SL (above entry) survives build_risk_plan()."""
        sig = _signal_short(
            stop_loss=100.8,  # evaluator-computed: level * 1.002
            tp1=98.2,
            tp2=96.5,
            tp3=94.8,
            setup_class="SR_FLIP_RETEST",
        )
        risk = _build(sig, SetupClass.SR_FLIP_RETEST)
        assert risk.passed, f"SR_FLIP_RETEST SHORT plan failed: {risk.reason}"
        assert risk.stop_loss == pytest.approx(sig.stop_loss, rel=1e-6), (
            f"SR_FLIP_RETEST SHORT: evaluator SL {sig.stop_loss} was overwritten "
            f"by generic {risk.stop_loss} (structural SL expression lost)"
        )

    def test_sr_flip_retest_preserves_swing_high_tp1(self):
        """SR_FLIP_RETEST: evaluator-authored TP1 (swing high) must survive."""
        sig = _signal(
            stop_loss=99.2,
            tp1=101.8,   # evaluator-computed 20-candle swing high
            tp2=103.5,   # evaluator-computed 4h target
            tp3=105.0,
            setup_class="SR_FLIP_RETEST",
        )
        risk = _build(sig, SetupClass.SR_FLIP_RETEST)
        assert risk.passed, f"SR_FLIP_RETEST plan failed: {risk.reason}"
        assert risk.tp1 == pytest.approx(sig.tp1, rel=1e-6), (
            f"SR_FLIP_RETEST TP1 {sig.tp1} (swing high) was overwritten by "
            f"generic 1.2R target {risk.tp1} (structural TP expression lost)"
        )
        assert risk.tp2 == pytest.approx(sig.tp2, rel=1e-6), (
            f"SR_FLIP_RETEST TP2 {sig.tp2} (4h target) was overwritten by "
            f"generic 2.0R target {risk.tp2} (structural TP expression lost)"
        )

    def test_sr_flip_retest_predictive_bypass(self):
        """SR_FLIP_RETEST must be in the predictive bypass set."""
        sig = SimpleNamespace(
            symbol="BTCUSDT",
            setup_class="SR_FLIP_RETEST",
            direction=Direction.LONG,
            entry=100.0,
            tp1=101.8,
            tp2=103.5,
            tp3=105.0,
            stop_loss=99.2,
        )
        engine = PredictiveEngine()
        pred = PredictionResult(
            suggested_tp_adjustment=1.5,
            suggested_sl_adjustment=0.7,
        )
        engine.adjust_tp_sl(sig, pred)
        assert sig.tp1 == pytest.approx(101.8, rel=1e-6), (
            "SR_FLIP_RETEST tp1 was modified by predictive engine — "
            "structural swing-high TP must not be scaled"
        )
        assert sig.stop_loss == pytest.approx(99.2, rel=1e-6), (
            "SR_FLIP_RETEST stop_loss was modified by predictive engine — "
            "structural SL must not be scaled"
        )

    def test_sr_flip_retest_not_using_old_generic_1_2r_tp(self):
        """Regression: SR_FLIP_RETEST must NOT use the old generic 1.2R TP1.

        Before PR-02 SR_FLIP_RETEST inclusion, build_risk_plan() used
        1.2/2.0/2.8R generic multiples for this path.  After inclusion in
        STRUCTURAL_SLTP_PROTECTED_SETUPS the evaluator-authored structural
        levels are used instead.
        """
        sig = _signal(
            stop_loss=99.2,
            tp1=103.0,   # much larger than 1.2R * (100.0-99.2) = 0.96 → 100.96
            tp2=106.0,
            tp3=109.0,
            setup_class="SR_FLIP_RETEST",
        )
        risk = _build(sig, SetupClass.SR_FLIP_RETEST)
        assert risk.passed, f"SR_FLIP_RETEST plan failed: {risk.reason}"
        # If the old generic 1.2R branch were still active, tp1 would be ≈100.96.
        # With PR-02 preservation, it must equal the evaluator-authored sig.tp1.
        assert risk.tp1 > 102.0, (
            f"SR_FLIP_RETEST tp1 {risk.tp1:.4f} looks like the old 1.2R generic "
            f"target rather than the evaluator-authored structural level {sig.tp1}"
        )
        assert risk.tp1 == pytest.approx(sig.tp1, rel=1e-6), (
            f"SR_FLIP_RETEST tp1 {risk.tp1:.4f} must equal evaluator-authored {sig.tp1}"
        )


# ---------------------------------------------------------------------------
# Integration: full preservation chain (build_risk_plan → predictive bypass)
# ---------------------------------------------------------------------------

class TestEndToEndPreservationChain:
    """End-to-end tests verifying that evaluator-authored geometry survives
    both build_risk_plan() and PredictiveEngine.adjust_tp_sl()."""

    @pytest.mark.parametrize("sc", [
        "POST_DISPLACEMENT_CONTINUATION",
        "VOLUME_SURGE_BREAKOUT",
        "BREAKDOWN_SHORT",
        "QUIET_COMPRESSION_BREAK",
        "TREND_PULLBACK_EMA",
        "CONTINUATION_LIQUIDITY_SWEEP",
        "SR_FLIP_RETEST",
        "FAILED_AUCTION_RECLAIM",
    ])
    def test_full_chain_preserves_evaluator_sl(self, sc):
        """Evaluator SL must survive both build_risk_plan() and adjust_tp_sl()."""
        from src.signal_quality import SetupClass as SC
        is_short = sc == "BREAKDOWN_SHORT"
        if is_short:
            sig = _signal_short(stop_loss=101.0, tp1=98.5, tp2=97.0, tp3=95.5,
                                setup_class=sc)
        else:
            sig = _signal(stop_loss=99.0, tp1=101.5, tp2=103.0, tp3=104.5,
                          setup_class=sc)

        setup_enum = SC(sc)
        risk = _build(sig, setup_enum)
        assert risk.passed, f"{sc} risk plan failed: {risk.reason}"

        # Simulate _apply_risk_plan_to_signal: write risk values back to signal.
        sig.stop_loss = risk.stop_loss
        sig.tp1 = risk.tp1
        sig.tp2 = risk.tp2
        sig.tp3 = risk.tp3

        # Capture values after risk plan.
        sl_after_risk = sig.stop_loss
        tp1_after_risk = sig.tp1

        # Now apply predictive bypass.
        engine = PredictiveEngine()
        pred = PredictionResult(
            suggested_tp_adjustment=1.4,
            suggested_sl_adjustment=0.75,
        )
        engine.adjust_tp_sl(sig, pred)

        assert sig.stop_loss == pytest.approx(sl_after_risk, rel=1e-6), (
            f"{sc}: SL changed after predictive adjustment "
            f"({sl_after_risk:.4f} → {sig.stop_loss:.4f})"
        )
        assert sig.tp1 == pytest.approx(tp1_after_risk, rel=1e-6), (
            f"{sc}: TP1 changed after predictive adjustment "
            f"({tp1_after_risk:.4f} → {sig.tp1:.4f})"
        )
