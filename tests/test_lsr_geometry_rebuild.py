"""LSR geometry rebuild (2026-06-15) — loss-side SL tighten + ships-dark guards.

Live last-100: LIQUIDITY_SWEEP_REVERSAL is the worst R:R (+0.47 win / -0.73 loss).
LSR is reject-not-compress (STRUCTURAL_SLTP_PROTECTED_SETUPS), so tightening its
max-SL cap DROPS wide-stop LSRs rather than wicking them. The win-side pre-TP
R-scaling lives in signal_dispatch (mirrors SR_FLIP change B) and ships dark.
"""
from __future__ import annotations

import importlib

import config
import src.signal_quality as sq
from src.signal_quality import _max_sl_pct_for_policy, SetupClass


def _cap_pct(monkeypatch, enabled, tight):
    monkeypatch.setattr(sq, "LSR_SL_TIGHTEN_ENABLED", enabled)
    monkeypatch.setattr(sq, "LSR_MAX_SL_PCT_TIGHT", tight)
    cap, scope, _ = _max_sl_pct_for_policy("360_SCALP", SetupClass.LIQUIDITY_SWEEP_REVERSAL)
    return cap * 100.0, scope


class TestLsrSlTighten:
    def test_off_keeps_2pct_cap(self, monkeypatch):
        pct, _ = _cap_pct(monkeypatch, False, 1.5)
        assert abs(pct - 2.0) < 1e-9

    def test_on_applies_tight_cap(self, monkeypatch):
        pct, scope = _cap_pct(monkeypatch, True, 1.5)
        assert abs(pct - 1.5) < 1e-9
        assert scope == "setup"

    def test_only_narrows_never_widens(self, monkeypatch):
        # A "tight" value above the normal 2.0% cap must be ignored.
        pct, _ = _cap_pct(monkeypatch, True, 2.8)
        assert abs(pct - 2.0) < 1e-9

    def test_other_setups_unaffected(self, monkeypatch):
        monkeypatch.setattr(sq, "LSR_SL_TIGHTEN_ENABLED", True)
        monkeypatch.setattr(sq, "LSR_MAX_SL_PCT_TIGHT", 1.5)
        cap, _, _ = _max_sl_pct_for_policy("360_SCALP", SetupClass.SR_FLIP_RETEST)
        assert abs(cap * 100 - 2.5) < 1e-9  # SR_FLIP cap untouched

    def test_lsr_is_reject_not_compress(self):
        # The safety premise: tightening drops, not wicks.
        assert SetupClass.LIQUIDITY_SWEEP_REVERSAL in sq.STRUCTURAL_SLTP_PROTECTED_SETUPS


class TestLsrShipsDark:
    def test_all_lsr_flags_default_off(self):
        assert config.LSR_PRETP_R_SCALING_ENABLED is False
        assert config.LSR_SL_TIGHTEN_ENABLED is False
        assert config.LSR_PRETP_R_FACTOR == 0.35
        assert config.LSR_MAX_SL_PCT_TIGHT == 1.5
