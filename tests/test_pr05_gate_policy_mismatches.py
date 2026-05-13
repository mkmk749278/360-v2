"""PR-05 — Correct gate-policy mismatches.

Tests that validate the three priority gate-policy alignments:

1. TREND_PULLBACK_EMA is exempt from the SMC hard gate (EMA pullback thesis,
   not sweep-based — SMC sweep score does not measure this thesis).

2. WHALE_MOMENTUM is exempt from the SMC hard gate (order-flow / large-actor
   thesis, not sweep-based — SMC sweep score does not reflect OBI/tick-delta
   thesis).

3. FAILED_AUCTION_RECLAIM is exempt from the trend hard gate (auction
   structure / reclaim thesis, not EMA-alignment-based — EMA alignment score
   does not reflect the failed-acceptance thesis).

Additionally: unrelated sweep-dependent paths must NOT gain accidental
exemptions, and the TREND_PULLBACK_EMA path must NOT be exempt from the
trend gate (since EMA alignment IS its thesis).
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _smc_gate_would_block(
    setup_class: str,
    smc_score: float,
    regime: str = "RANGING",
    direction: str = "LONG",
) -> bool:
    """Mirror the scanner SMC hard-gate decision logic for unit testing.

    Returns True if the signal would be suppressed, False if it passes.
    """
    from src.scanner import _SMC_GATE_EXEMPT_SETUPS
    from config import SMC_HARD_GATE_MIN, SMC_SCORE_MIN_TRENDING_SHORT

    if setup_class in _SMC_GATE_EXEMPT_SETUPS:
        return False
    smc_min = (
        SMC_SCORE_MIN_TRENDING_SHORT
        if regime == "TRENDING_DOWN" and direction == "SHORT"
        else SMC_HARD_GATE_MIN
    )
    return smc_score < smc_min


def _trend_gate_would_block(
    setup_class: str,
    ind_score: float,
) -> bool:
    """Mirror the scanner trend hard-gate decision logic for unit testing.

    Returns True if the signal would be suppressed, False if it passes.
    """
    from src.scanner import _TREND_GATE_EXEMPT_SETUPS
    from config import TREND_HARD_GATE_MIN

    if setup_class in _TREND_GATE_EXEMPT_SETUPS:
        return False
    return ind_score < TREND_HARD_GATE_MIN


# ---------------------------------------------------------------------------
# SMC gate membership tests
# ---------------------------------------------------------------------------


class TestSmcGateExemptionsPR05:
    """PR-05: targeted SMC gate exemptions are present and correct."""

    @pytest.fixture
    def smc_exempt(self):
        from src.scanner import _SMC_GATE_EXEMPT_SETUPS
        return _SMC_GATE_EXEMPT_SETUPS

    # --- new PR-05 additions ------------------------------------------------

    def test_trend_pullback_ema_is_smc_exempt(self, smc_exempt):
        """TREND_PULLBACK_EMA thesis is EMA-pullback, not sweep-based.

        SMC sweep score does not measure this path's entry condition.
        The path must be in _SMC_GATE_EXEMPT_SETUPS so it is not wrongly
        suppressed for lacking a sweep event.
        """
        assert "TREND_PULLBACK_EMA" in smc_exempt, (
            "TREND_PULLBACK_EMA must be in _SMC_GATE_EXEMPT_SETUPS (PR-05 gate-policy alignment)"
        )

    def test_whale_momentum_is_smc_exempt(self, smc_exempt):
        """WHALE_MOMENTUM thesis is order-flow / large-actor impulse, not sweep-based.

        OBI / tick-delta evidence is the primary edge; SMC sweep score does not
        reflect this thesis and must not gate the path.
        """
        assert "WHALE_MOMENTUM" in smc_exempt, (
            "WHALE_MOMENTUM must be in _SMC_GATE_EXEMPT_SETUPS (PR-05 gate-policy alignment)"
        )

    # --- gate logic: low SMC score does not block exempt paths --------------

    def test_trend_pullback_ema_low_smc_not_blocked(self):
        """TREND_PULLBACK_EMA with smc_score=3.0 (no sweep) must not be blocked.

        The evaluator fires purely on EMA structure; a low SMC sweep score is
        expected and must not suppress the signal.
        """
        assert not _smc_gate_would_block("TREND_PULLBACK_EMA", smc_score=3.0), (
            "TREND_PULLBACK_EMA with smc_score=3.0 should not be blocked by the SMC hard gate"
        )

    def test_whale_momentum_low_smc_not_blocked(self):
        """WHALE_MOMENTUM with smc_score=2.0 (no sweep) must not be blocked.

        Whale signals are confirmed by OBI / tick-delta, not SMC sweep evidence.
        """
        assert not _smc_gate_would_block("WHALE_MOMENTUM", smc_score=2.0), (
            "WHALE_MOMENTUM with smc_score=2.0 should not be blocked by the SMC hard gate"
        )

    # --- pre-existing exemptions must remain unchanged ----------------------

    def test_pre_existing_smc_exemptions_unchanged(self, smc_exempt):
        """Original SMC-exempt setups must all still be present after PR-05."""
        pre_existing = {
            "OPENING_RANGE_BREAKOUT",
            "QUIET_COMPRESSION_BREAK",
            "VOLUME_SURGE_BREAKOUT",
            "BREAKDOWN_SHORT",
            "SR_FLIP_RETEST",
            "LIQUIDATION_REVERSAL",
            "FUNDING_EXTREME_SIGNAL",
            "DIVERGENCE_CONTINUATION",
            "POST_DISPLACEMENT_CONTINUATION",
            "FAILED_AUCTION_RECLAIM",
        }
        assert pre_existing.issubset(smc_exempt), (
            f"Pre-existing SMC-exempt setups missing: {pre_existing - smc_exempt}"
        )

    # --- sweep-dependent paths must NOT gain exemption ---------------------

    def test_liquidity_sweep_reversal_not_smc_exempt(self, smc_exempt):
        """LIQUIDITY_SWEEP_REVERSAL is sweep-dependent — must NOT be exempt."""
        assert "LIQUIDITY_SWEEP_REVERSAL" not in smc_exempt, (
            "LIQUIDITY_SWEEP_REVERSAL must not be in _SMC_GATE_EXEMPT_SETUPS"
        )

    def test_continuation_liquidity_sweep_not_smc_exempt(self, smc_exempt):
        """CONTINUATION_LIQUIDITY_SWEEP requires sweep — must NOT be exempt."""
        assert "CONTINUATION_LIQUIDITY_SWEEP" not in smc_exempt, (
            "CONTINUATION_LIQUIDITY_SWEEP must not be in _SMC_GATE_EXEMPT_SETUPS"
        )


# ---------------------------------------------------------------------------
# Trend gate membership tests
# ---------------------------------------------------------------------------


class TestTrendGateExemptionsPR05:
    """PR-05: targeted trend gate exemptions are present and correct."""

    @pytest.fixture
    def trend_exempt(self):
        from src.scanner import _TREND_GATE_EXEMPT_SETUPS
        return _TREND_GATE_EXEMPT_SETUPS

    # --- new PR-05 addition -------------------------------------------------

    def test_failed_auction_reclaim_is_trend_exempt(self, trend_exempt):
        """FAILED_AUCTION_RECLAIM thesis is auction-structure reclaim, not EMA-based.

        EMA trend alignment score does not measure the failed-auction thesis;
        this path must be in _TREND_GATE_EXEMPT_SETUPS so it is not suppressed
        for lacking EMA agreement.
        """
        assert "FAILED_AUCTION_RECLAIM" in trend_exempt, (
            "FAILED_AUCTION_RECLAIM must be in _TREND_GATE_EXEMPT_SETUPS (PR-05 gate-policy alignment)"
        )

    # --- gate logic: low indicator score does not block FAR -----------------

    def test_failed_auction_reclaim_low_ind_not_blocked(self):
        """FAILED_AUCTION_RECLAIM with low indicator score must not be trend-blocked.

        The path fires on auction structure; EMA alignment is not the thesis.
        """
        assert not _trend_gate_would_block("FAILED_AUCTION_RECLAIM", ind_score=20.0), (
            "FAILED_AUCTION_RECLAIM with ind_score=20.0 should not be blocked by the trend gate"
        )

    # --- TREND_PULLBACK_EMA must NOT be trend-gate exempt ------------------

    def test_trend_pullback_ema_not_trend_exempt(self, trend_exempt):
        """TREND_PULLBACK_EMA IS EMA-alignment-based — must NOT be trend-gate exempt.

        The path's entry thesis depends on EMA9/EMA21/EMA50 alignment.  Exempting
        it from the trend gate would bypass its own thesis requirement.
        """
        assert "TREND_PULLBACK_EMA" not in trend_exempt, (
            "TREND_PULLBACK_EMA must NOT be in _TREND_GATE_EXEMPT_SETUPS — EMA alignment is its thesis"
        )

    # --- pre-existing trend exemptions must remain unchanged ----------------

    def test_pre_existing_trend_exemptions_unchanged(self, trend_exempt):
        """Original trend-gate-exempt setups must all still be present after PR-05."""
        pre_existing = {
            "LIQUIDATION_REVERSAL",
            "FUNDING_EXTREME_SIGNAL",
            "WHALE_MOMENTUM",
        }
        assert pre_existing.issubset(trend_exempt), (
            f"Pre-existing trend-exempt setups missing: {pre_existing - trend_exempt}"
        )

    # --- EMA-dependent paths must NOT gain trend exemption ------------------

    def test_sr_flip_retest_not_trend_exempt(self, trend_exempt):
        """SR_FLIP_RETEST is an EMA/level-based path — must NOT be trend-gate exempt."""
        assert "SR_FLIP_RETEST" not in trend_exempt, (
            "SR_FLIP_RETEST must not be in _TREND_GATE_EXEMPT_SETUPS"
        )


# ---------------------------------------------------------------------------
# Combined: no accidental broad gate loosening
# ---------------------------------------------------------------------------


class TestNoBroadExemptionBleed:
    """Verify that PR-05 changes do not accidentally broaden gates globally."""

    def test_smc_exempt_count_matches_expected(self):
        """_SMC_GATE_EXEMPT_SETUPS must contain exactly the known canonical members.

        If this count increases without a deliberate PR, investigate immediately.
        """
        from src.scanner import _SMC_GATE_EXEMPT_SETUPS

        expected = {
            "OPENING_RANGE_BREAKOUT",
            "QUIET_COMPRESSION_BREAK",
            "VOLUME_SURGE_BREAKOUT",
            "BREAKDOWN_SHORT",
            "SR_FLIP_RETEST",
            "LIQUIDATION_REVERSAL",
            "FUNDING_EXTREME_SIGNAL",
            "DIVERGENCE_CONTINUATION",
            "POST_DISPLACEMENT_CONTINUATION",
            "FAILED_AUCTION_RECLAIM",
            "TREND_PULLBACK_EMA",
            "WHALE_MOMENTUM",
        }
        unexpected = _SMC_GATE_EXEMPT_SETUPS - expected
        assert not unexpected, (
            f"Unexpected setups gained SMC gate exemption: {unexpected}"
        )
        missing = expected - _SMC_GATE_EXEMPT_SETUPS
        assert not missing, (
            f"Expected SMC-exempt setups are missing: {missing}"
        )

    def test_trend_exempt_count_matches_expected(self):
        """_TREND_GATE_EXEMPT_SETUPS must contain exactly the known canonical members.

        If this count increases without a deliberate PR, investigate immediately.
        """
        from src.scanner import _TREND_GATE_EXEMPT_SETUPS

        expected = {
            "LIQUIDATION_REVERSAL",
            "FUNDING_EXTREME_SIGNAL",
            "WHALE_MOMENTUM",
            "FAILED_AUCTION_RECLAIM",
            # 2026-05-13 funnel-diag truth: LSR was the second-most-active
            # path but every B-tier candidate was being killed by the
            # trend hard gate (EMA alignment).  LSR is counter-trend by
            # design — EMA alignment with entry direction is *bearish*
            # for the thesis, not bullish.  See scanner comment block.
            "LIQUIDITY_SWEEP_REVERSAL",
        }
        unexpected = _TREND_GATE_EXEMPT_SETUPS - expected
        assert not unexpected, (
            f"Unexpected setups gained trend gate exemption: {unexpected}"
        )
        missing = expected - _TREND_GATE_EXEMPT_SETUPS
        assert not missing, (
            f"Expected trend-exempt setups are missing: {missing}"
        )


# ---------------------------------------------------------------------------
# 2026-05-13: LIQUIDITY_SWEEP_REVERSAL trend-gate exemption
# ---------------------------------------------------------------------------


class TestLsrTrendExemption20260513:
    """Diag-driven fix: LSR was being killed by trend_hard_gate despite
    being a counter-trend path.  Covers the new exemption + a smoke check
    that a low-indicator-score LSR signal now passes."""

    @pytest.fixture
    def trend_exempt(self):
        from src.scanner import _TREND_GATE_EXEMPT_SETUPS
        return _TREND_GATE_EXEMPT_SETUPS

    def test_liquidity_sweep_reversal_is_trend_exempt(self, trend_exempt):
        """LSR sells into long sweeps and buys into short sweeps — counter-trend
        by design.  EMA alignment with the entry direction is *bearish* for the
        LSR thesis, not bullish, so the trend hard gate must not block it."""
        assert "LIQUIDITY_SWEEP_REVERSAL" in trend_exempt, (
            "LIQUIDITY_SWEEP_REVERSAL must be in _TREND_GATE_EXEMPT_SETUPS "
            "(2026-05-13 diag fix — was killing the second-most-active path)"
        )

    def test_liquidity_sweep_reversal_low_ind_not_blocked(self):
        """A B-tier LSR candidate with low EMA alignment (ind_score=5) must
        pass the trend gate.  Pre-fix this fired in production for every
        post-deploy LSR candidate and zeroed live LSR emission."""
        assert not _trend_gate_would_block("LIQUIDITY_SWEEP_REVERSAL", ind_score=5.0), (
            "LIQUIDITY_SWEEP_REVERSAL with ind_score=5.0 should NOT be blocked "
            "by the trend hard gate — see diag 2026-05-13"
        )

    def test_liquidity_sweep_reversal_smc_gate_unchanged(self):
        """LSR is still sweep-dependent — the SMC gate must continue to
        block low-SMC LSR candidates.  Only the trend gate changed."""
        from src.scanner import _SMC_GATE_EXEMPT_SETUPS
        assert "LIQUIDITY_SWEEP_REVERSAL" not in _SMC_GATE_EXEMPT_SETUPS, (
            "LSR must remain SMC-gated — sweep is its thesis"
        )
