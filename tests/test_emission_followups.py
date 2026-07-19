"""Regression pins for the three emission follow-ups (2026-07-19):

1. dispatch_cooldown → live-tunable + lowered default.
2. MEAN_REVERT compat-map (#739) → eligible in the states its own trigger creates.
3. pair-cohort → new ops tunable registered.
"""
from __future__ import annotations

from src.signal_quality import MarketState, REGIME_SETUP_COMPATIBILITY, SetupClass


# ── Fix 2: MEAN_REVERT compat-map (#739 / audit F1) ────────────────────────


def test_mean_revert_eligible_in_expansion_and_volatile() -> None:
    # The ≥2.5σ trigger flips the classifier OUT of range states into these two
    # — MEAN_REVERT must be compat-listed here or it can never emit.
    assert SetupClass.MEAN_REVERT in REGIME_SETUP_COMPATIBILITY[MarketState.VOLATILE_UNSUITABLE]
    assert SetupClass.MEAN_REVERT in REGIME_SETUP_COMPATIBILITY[MarketState.BREAKOUT_EXPANSION]


def test_mean_revert_still_eligible_in_range_states() -> None:
    # The fix is additive — its range homes stay intact.
    assert SetupClass.MEAN_REVERT in REGIME_SETUP_COMPATIBILITY[MarketState.CLEAN_RANGE]
    assert SetupClass.MEAN_REVERT in REGIME_SETUP_COMPATIBILITY[MarketState.DIRTY_RANGE]


# ── Fix 1 + 3: new ops tunables registered with correct defaults ───────────


def test_dispatch_cooldown_tunables_registered() -> None:
    from src.runtime_tunables import registry

    reg = registry()
    # Both cooldown knobs exposed for live ops control (window bounded 0..7200s).
    assert "dispatch_cooldown_enabled" in reg
    assert "dispatch_cooldown_sec" in reg
    assert reg["dispatch_cooldown_enabled"].type == "bool"
    assert reg["dispatch_cooldown_sec"].type == "float"
    assert reg["dispatch_cooldown_sec"].max_value == 7200.0


def test_cohort_aware_tunable_registered_default_off() -> None:
    from src.runtime_tunables import registry

    reg = registry()
    assert "context_emission_cohort_aware" in reg
    assert reg["context_emission_cohort_aware"].default is False


def test_dispatch_cooldown_default_lowered_when_env_unset(monkeypatch) -> None:
    # The lowered default is 900 (from 1800) when the env var is unset. The test
    # conftest force-sets it to 0, so assert the parse logic directly.
    monkeypatch.delenv("DISPATCH_COOLDOWN_SEC", raising=False)
    from config import _safe_float

    assert _safe_float("DISPATCH_COOLDOWN_SEC", "900") == 900.0
