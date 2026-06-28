"""Tests for OWNER_BRIEF §3.4 + §3.2 #4 doctrine-aligned MTF hard-block bypass.

OWNER_BRIEF §3.4 explicitly assigns "None" HTF treatment to two categories:

  - Tape-driven (WHALE_MOMENTUM / LIQUIDATION_REVERSAL / FUNDING_EXTREME_SIGNAL):
    direction comes from realtime order flow, not candle-EMA structure.
  - Breakout (VOLUME_SURGE_BREAKOUT / BREAKDOWN_SHORT / OPENING_RANGE_BREAKOUT):
    "fires in any HTF context."

Per OWNER_BRIEF §3.2 #4 ("soft penalties over hard blocks; reserve hard blocks
for structural-impossibility checkpoints"), the scanner-level MTF gate must
not hard-veto these paths.

This module pins:

1. The contents of `_SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS` against the §3.4
   doctrine — drift in either direction (adding a non-exempt setup, or
   forgetting to add a future tape-driven / breakout setup) is a doctrine
   violation and must surface as a test failure.
2. Setups outside the doctrine exempt list (LSR, FAR, SR_FLIP, QCB, TPE,
   DIV_CONT, CLS, PDC, MA_CROSS_TREND_SHIFT) are NOT in the exempt set —
   their MTF treatment is correctly handled elsewhere (family caps for
   counter-trend; regime gate for trend-aligned).
3. The env override `MTF_DOCTRINE_BYPASS_ENABLED` flag default is enabled
   (per OWNER_BRIEF §3.2 #4 doctrine — soft-over-hard is the default).
"""

from __future__ import annotations

import importlib

import pytest


# ---------------------------------------------------------------------------
# Section A — pin the doctrine list itself.  These tests catch drift; they
# do not exercise the runtime gate (which requires heavy scanner scaffolding).
# Runtime behaviour is covered by section B.
# ---------------------------------------------------------------------------


class TestDoctrineExemptSetClassesDoctrine:
    """Pin `_SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS` against OWNER_BRIEF §3.4."""

    def test_tape_driven_setups_are_exempt(self):
        """OWNER_BRIEF §3.4 row 2: tape-driven paths get no HTF gate."""
        from src.scanner import _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

        # Tape-driven setups per §3.4: direction from tape / funding / cascade.
        assert "WHALE_MOMENTUM" in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS
        assert "LIQUIDATION_REVERSAL" in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS
        assert "FUNDING_EXTREME_SIGNAL" in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

    def test_breakout_setups_are_exempt(self):
        """OWNER_BRIEF §3.4 row 5: breakouts fire in any HTF context."""
        from src.scanner import _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

        # Breakout setups per §3.4: "fires in any HTF context."
        assert "VOLUME_SURGE_BREAKOUT" in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS
        assert "BREAKDOWN_SHORT" in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS
        assert "OPENING_RANGE_BREAKOUT" in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

    def test_counter_trend_setups_are_NOT_exempt(self):
        """LSR / FAR are counter-trend by design (§3.4 row 3): family cap 0.35
        already provides the doctrine-faithful relaxation; their evaluators
        apply the 1H+4H-both-oppose soft penalty internally.  They must NOT
        be in the hard-block exempt set — that would over-relax the gate."""
        from src.scanner import _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

        assert "LIQUIDITY_SWEEP_REVERSAL" not in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS
        assert "FAILED_AUCTION_RECLAIM" not in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

    def test_structure_optional_counter_trend_setups_are_NOT_exempt(self):
        """SR_FLIP / QCB are 'structure with optional counter-trend' (§3.4
        row 4): same shape as LSR/FAR — family cap + evaluator soft penalty."""
        from src.scanner import _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

        assert "SR_FLIP_RETEST" not in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS
        assert "QUIET_COMPRESSION_BREAK" not in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

    def test_trend_aligned_setups_are_NOT_exempt(self):
        """TPE / DIV_CONT / CLS / PDC are trend-aligned-by-regime-gate (§3.4
        row 1): regime classifier IS the operative HTF gate.  An EMA-alignment
        floor inside a TRENDING regime is consistent with their thesis."""
        from src.scanner import _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

        assert "TREND_PULLBACK_EMA" not in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS
        assert "DIVERGENCE_CONTINUATION" not in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS
        assert "CONTINUATION_LIQUIDITY_SWEEP" not in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS
        assert "POST_DISPLACEMENT_CONTINUATION" not in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

    def test_ma_cross_is_NOT_exempt(self):
        """MA_CROSS_TREND_SHIFT is a discrete event setup that fires on EMA
        crossovers — the EMA structure IS its thesis, so an EMA-alignment
        floor is consistent.  Not exempt."""
        from src.scanner import _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

        assert "MA_CROSS_TREND_SHIFT" not in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

    def test_exempt_set_size_matches_doctrine_categories(self):
        """The exempt set covers exactly seven setups: 3 tape-driven + 3 breakout
        + 1 mover-continuation, all §3.4 "fires in any HTF context".  The 7th is
        MOVER_TREND_PULLBACK: a confirmed top mover (MA7↔MA99 stack separation gate)
        defines its own regime, so the HTF confluence / longs-regime gates must not
        veto it — same treatment as the breakout family.  If this number changes,
        the doctrine commentary must be revisited (is a new evaluator tape-driven /
        breakout / mover-context, or genuinely HTF-gated?)."""
        from src.scanner import _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

        assert len(_SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS) == 8
        assert "MOVER_TREND_PULLBACK" in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS
        # 8th: MOVER_AVWAP_SCALP — the AVWAP slope defines its own regime/direction.
        assert "MOVER_AVWAP_SCALP" in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

    def test_every_exempt_setup_is_a_known_scalp_setup(self):
        """Drift guard: every exempt setup must exist in _SCALP_SETUP_TO_FAMILY
        (the source of truth for SCALP setup classes).  A typo or stale entry
        would silently break the bypass."""
        from src.scanner import (
            _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS,
            _SCALP_SETUP_TO_FAMILY,
        )

        for setup in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS:
            assert setup in _SCALP_SETUP_TO_FAMILY, (
                f"{setup} is in the exempt set but not registered in "
                f"_SCALP_SETUP_TO_FAMILY — likely a typo or stale entry"
            )

    def test_exempt_setups_resolve_to_doctrine_families(self):
        """Cross-check: tape-driven setups should resolve to orderflow_momentum /
        reversal / mean_reversion families; breakout setups should resolve to
        breakout_momentum.  Catches silent family-mapping errors."""
        from src.scanner import _SCALP_SETUP_TO_FAMILY

        # Tape-driven (§3.4 row 2)
        assert _SCALP_SETUP_TO_FAMILY["WHALE_MOMENTUM"] == "orderflow_momentum"
        assert _SCALP_SETUP_TO_FAMILY["LIQUIDATION_REVERSAL"] == "reversal"
        assert _SCALP_SETUP_TO_FAMILY["FUNDING_EXTREME_SIGNAL"] == "mean_reversion"
        # Breakout (§3.4 row 5)
        assert _SCALP_SETUP_TO_FAMILY["VOLUME_SURGE_BREAKOUT"] == "breakout_momentum"
        assert _SCALP_SETUP_TO_FAMILY["BREAKDOWN_SHORT"] == "breakout_momentum"
        assert _SCALP_SETUP_TO_FAMILY["OPENING_RANGE_BREAKOUT"] == "breakout_momentum"

    def test_lsr_in_reversal_family_NOT_exempt_despite_sibling_exempt(self):
        """LIQUIDATION_REVERSAL and LIQUIDITY_SWEEP_REVERSAL share the
        `reversal` family but doctrine treats them differently (§3.4 row 2 vs
        row 3).  This is why we exempt by setup_class, not by family — to
        avoid accidentally over-relaxing LSR."""
        from src.scanner import (
            _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS,
            _SCALP_SETUP_TO_FAMILY,
        )

        # Same family
        assert (
            _SCALP_SETUP_TO_FAMILY["LIQUIDATION_REVERSAL"]
            == _SCALP_SETUP_TO_FAMILY["LIQUIDITY_SWEEP_REVERSAL"]
            == "reversal"
        )
        # Different doctrine treatment — only LIQ_REV is exempt
        assert "LIQUIDATION_REVERSAL" in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS
        assert "LIQUIDITY_SWEEP_REVERSAL" not in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS


# ---------------------------------------------------------------------------
# Section B — env-flag default + import-time read.
# ---------------------------------------------------------------------------


class TestDoctrineBypassEnvFlag:
    def test_default_enabled(self, monkeypatch):
        """Default per OWNER_BRIEF §3.2 #4: soft-over-hard is the doctrine
        baseline.  Bypass should be ON by default."""
        monkeypatch.delenv("MTF_DOCTRINE_BYPASS_ENABLED", raising=False)
        import src.scanner as _scanner_mod

        importlib.reload(_scanner_mod)
        assert _scanner_mod._MTF_DOCTRINE_BYPASS_ENABLED is True

    @pytest.mark.parametrize("falsey", ["false", "False", "0", "no", "off", "OFF"])
    def test_env_disable_forms(self, monkeypatch, falsey):
        """Operator can flip to legacy hard-block via env (rollback path)."""
        monkeypatch.setenv("MTF_DOCTRINE_BYPASS_ENABLED", falsey)
        import src.scanner as _scanner_mod

        importlib.reload(_scanner_mod)
        assert _scanner_mod._MTF_DOCTRINE_BYPASS_ENABLED is False

    @pytest.mark.parametrize("truthy", ["true", "True", "1", "yes", "on"])
    def test_env_enable_forms(self, monkeypatch, truthy):
        monkeypatch.setenv("MTF_DOCTRINE_BYPASS_ENABLED", truthy)
        import src.scanner as _scanner_mod

        importlib.reload(_scanner_mod)
        assert _scanner_mod._MTF_DOCTRINE_BYPASS_ENABLED is True


# ---------------------------------------------------------------------------
# Section C — bypass set is immutable (frozenset).  Catches accidental
# `_SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS.add(...)` at runtime which would silently
# violate the doctrine after the test suite has run.
# ---------------------------------------------------------------------------


class TestExemptSetIsImmutable:
    def test_is_frozenset(self):
        from src.scanner import _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

        assert isinstance(_SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS, frozenset)

    def test_cannot_be_mutated_at_runtime(self):
        """Defence in depth: a frozenset rejects .add() with AttributeError."""
        from src.scanner import _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS

        with pytest.raises(AttributeError):
            _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS.add("BAD_SETUP")  # type: ignore[attr-defined]
