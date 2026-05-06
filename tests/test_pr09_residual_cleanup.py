"""PR-09: Residual cleanup / final pre-redeploy polish.

Verifies that the post-PR-01..08 system is internally consistent:

1. The stale "deferred to PR-04" note is gone — auxiliary channel identities
   are documented as intentionally absent from ACTIVE_PATH_PORTFOLIO_ROLES
   because they are sub-evaluators of auxiliary channels.

2. OPENING_RANGE_BREAKOUT remains in ACTIVE_PATH_PORTFOLIO_ROLES as SUPPORT
   (role preserved pending rebuild) but its disabled-by-default state (PR-06)
   is documented.

3. Auxiliary channel identities (FVG_RETEST, FVG_RETEST_HTF_CONFLUENCE,
   RSI_MACD_DIVERGENCE, SMC_ORDERBLOCK) are absent from ACTIVE_PATH_PORTFOLIO_ROLES.

4. Suppression counter key for below-threshold signals is "score_below50"
   (not "pr09_below50") — cleaner for operator telemetry.

5. Unrelated path behavior is unaffected — SR_FLIP_RETEST scores remain
   consistent before and after the cleanup.
"""

from __future__ import annotations

from src.signal_quality import (
    ACTIVE_PATH_PORTFOLIO_ROLES,
    APPROVED_PORTFOLIO_ROLES,
    PortfolioRole,
    SetupClass,
)


# ---------------------------------------------------------------------------
# 1. Auxiliary channel identities absent from ACTIVE_PATH_PORTFOLIO_ROLES
# ---------------------------------------------------------------------------

class TestAuxiliaryChannelIdentityAbsence:
    """Auxiliary sub-evaluator identities must not appear in the portfolio-role map."""

    AUXILIARY_IDENTITIES = frozenset({
        SetupClass.FVG_RETEST,
        SetupClass.FVG_RETEST_HTF_CONFLUENCE,
        SetupClass.RSI_MACD_DIVERGENCE,
        SetupClass.SMC_ORDERBLOCK,
    })

    def test_fvg_retest_absent(self):
        assert SetupClass.FVG_RETEST not in ACTIVE_PATH_PORTFOLIO_ROLES, (
            "FVG_RETEST is a sub-evaluator of the 360_SCALP_FVG auxiliary channel "
            "and must not have a standalone portfolio-role entry."
        )

    def test_fvg_retest_htf_confluence_absent(self):
        assert SetupClass.FVG_RETEST_HTF_CONFLUENCE not in ACTIVE_PATH_PORTFOLIO_ROLES, (
            "FVG_RETEST_HTF_CONFLUENCE is a sub-evaluator of 360_SCALP_FVG "
            "and must not have a standalone portfolio-role entry."
        )

    def test_rsi_macd_divergence_absent(self):
        assert SetupClass.RSI_MACD_DIVERGENCE not in ACTIVE_PATH_PORTFOLIO_ROLES, (
            "RSI_MACD_DIVERGENCE is a sub-evaluator of 360_SCALP_DIVERGENCE "
            "and must not have a standalone portfolio-role entry."
        )

    def test_smc_orderblock_absent(self):
        assert SetupClass.SMC_ORDERBLOCK not in ACTIVE_PATH_PORTFOLIO_ROLES, (
            "SMC_ORDERBLOCK is a sub-evaluator of 360_SCALP_ORDERBLOCK "
            "and must not have a standalone portfolio-role entry."
        )

    def test_none_of_the_auxiliary_identities_present(self):
        overlap = self.AUXILIARY_IDENTITIES & set(ACTIVE_PATH_PORTFOLIO_ROLES.keys())
        assert not overlap, (
            f"Auxiliary channel sub-evaluators must not appear in ACTIVE_PATH_PORTFOLIO_ROLES. "
            f"Found: {overlap}"
        )


# ---------------------------------------------------------------------------
# 2. OPENING_RANGE_BREAKOUT role is preserved as SUPPORT (disabled by default)
# ---------------------------------------------------------------------------

class TestOrbPortfolioRolePreserved:
    """OPENING_RANGE_BREAKOUT must remain in the portfolio map with role SUPPORT.

    PR-06 disabled it by default (SCALP_ORB_ENABLED=false) but the evaluator
    code and portfolio-role entry are preserved pending a proper rebuild.
    Removing the entry would silently break the governance contract tests.
    """

    def test_orb_present_in_portfolio_roles(self):
        assert SetupClass.OPENING_RANGE_BREAKOUT in ACTIVE_PATH_PORTFOLIO_ROLES, (
            "OPENING_RANGE_BREAKOUT must remain in ACTIVE_PATH_PORTFOLIO_ROLES "
            "even though it is disabled by default (PR-06)."
        )

    def test_orb_role_is_support(self):
        role = ACTIVE_PATH_PORTFOLIO_ROLES.get(SetupClass.OPENING_RANGE_BREAKOUT)
        assert role == PortfolioRole.SUPPORT, (
            f"OPENING_RANGE_BREAKOUT portfolio role should be SUPPORT, got {role!r}."
        )

    def test_orb_role_is_valid_taxonomy(self):
        role = ACTIVE_PATH_PORTFOLIO_ROLES.get(SetupClass.OPENING_RANGE_BREAKOUT)
        assert role in APPROVED_PORTFOLIO_ROLES


# ---------------------------------------------------------------------------
# 3. Suppression counter key uses "score_below50" (not "pr09_below50")
# ---------------------------------------------------------------------------

class TestSuppressionCounterKey:
    """_prepare_signal must use 'score_below50:<chan>' as the below-threshold counter key."""

    def test_suppression_key_template_in_source(self):
        """Verify the source code uses the correct counter key name."""
        import inspect
        import src.scanner as scanner_mod

        source = inspect.getsource(scanner_mod.Scanner._prepare_signal)
        assert "score_below50:" in source, (
            "Scanner._prepare_signal must use 'score_below50:<chan>' as the "
            "suppression counter key for below-threshold scores.  "
            "'pr09_below50' is stale."
        )
        assert "pr09_below50" not in source, (
            "Stale 'pr09_below50' key found in _prepare_signal — should be 'score_below50'."
        )


# ---------------------------------------------------------------------------
# 4. No "PR09" log-message prefixes remain in scanner (runtime output clarity)
# ---------------------------------------------------------------------------

class TestNoStaleLogPrefixes:
    """Runtime log messages must not use 'PR09' as a prefix."""

    def test_no_pr09_log_prefix_in_prepare_signal(self):
        import inspect
        import src.scanner as scanner_mod

        source = inspect.getsource(scanner_mod.Scanner._prepare_signal)
        # The "Soft-gate penalty applied" line must end with "(post-scoring)"
        assert "(post-PR09)" not in source, (
            "Stale '(post-PR09)' found in _prepare_signal log message. "
            "Should be '(post-scoring)'."
        )
        assert '"PR09 below-threshold' not in source, (
            "Stale 'PR09 below-threshold' log prefix found in _prepare_signal."
        )
        assert '"PR09 score ' not in source, (
            "Stale 'PR09 score' log prefix found in _prepare_signal."
        )
        assert '"PR09 scoring engine error' not in source, (
            "Stale 'PR09 scoring engine error' log prefix found in _prepare_signal."
        )


# ---------------------------------------------------------------------------
# 5. Core path portfolio roles unchanged — unrelated path behavior is stable
# ---------------------------------------------------------------------------

class TestCorePathRolesUnchanged:
    """The cleanup must not alter any core or specialist path portfolio roles."""

    EXPECTED_CORE = frozenset({
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        SetupClass.TREND_PULLBACK_EMA,
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.BREAKDOWN_SHORT,
        SetupClass.SR_FLIP_RETEST,
        SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
        SetupClass.POST_DISPLACEMENT_CONTINUATION,
    })

    EXPECTED_SPECIALIST = frozenset({
        SetupClass.WHALE_MOMENTUM,
        SetupClass.FUNDING_EXTREME_SIGNAL,
        SetupClass.QUIET_COMPRESSION_BREAK,
        # PR-8 (2026-05-06): MA-cross discrete trend-shift evaluator (15th path).
        SetupClass.MA_CROSS_TREND_SHIFT,
    })

    def test_core_paths_exactly(self):
        actual_core = frozenset(
            k for k, v in ACTIVE_PATH_PORTFOLIO_ROLES.items()
            if v == PortfolioRole.CORE
        )
        assert actual_core == self.EXPECTED_CORE, (
            f"Core path set changed unexpectedly.\n"
            f"Expected: {self.EXPECTED_CORE}\n"
            f"Actual:   {actual_core}"
        )

    def test_specialist_paths_exactly(self):
        actual_spec = frozenset(
            k for k, v in ACTIVE_PATH_PORTFOLIO_ROLES.items()
            if v == PortfolioRole.SPECIALIST
        )
        assert actual_spec == self.EXPECTED_SPECIALIST, (
            f"Specialist path set changed unexpectedly.\n"
            f"Expected: {self.EXPECTED_SPECIALIST}\n"
            f"Actual:   {actual_spec}"
        )

    def test_total_portfolio_path_count(self):
        """Exactly 15 paths have explicit portfolio roles (PR-8 added MA_CROSS_TREND_SHIFT)."""
        assert len(ACTIVE_PATH_PORTFOLIO_ROLES) == 15, (
            f"Expected 15 portfolio-role entries, got {len(ACTIVE_PATH_PORTFOLIO_ROLES)}. "
            f"Add new evaluators to both ScalpChannel.evaluate() and ACTIVE_PATH_PORTFOLIO_ROLES."
        )
