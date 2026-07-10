"""BE arm TP1 cap (2026-07-10).

The noise-aware arm (max of flat 1% / 1R / 0.75×noise) double-counted the
#702 noise-floor stop WIDENING: 1R of an already-widened 2.4-2.7% stop put
the arm threshold at ≈ the stop distance — at or ABOVE TP1 for tighter
setups.  Under the TP1-full-close default that arm is unreachable: the trade
either closes at TP1 first or round-trips its full stop with the ratchet
never engaging.  Owner-reported symptom: signals ran +2% then went back to
the full −2.4-2.7% SL with no BE shift (≈5% swing peak-to-exit).

The cap: when the trade's TP1 distance is known, the arm never exceeds
``be_arm_tp1_cap_fraction`` × TP1 distance (floored at the flat trigger).
"""
from __future__ import annotations

import pytest

from src import runtime_tunables as rt
from src.execution import be_policy


@pytest.fixture(autouse=True)
def _reset_tunables():
    rt.reset_for_test()
    yield
    rt.reset_for_test()


def test_cap_keeps_arm_reachable_below_tp1():
    # The owner-reported class: noise-widened 2.5% stop, TP1 at 3.5%.
    # Pre-fix arm = 1R = 2.5% (≈ unreachable before the full-SL round-trip
    # at the +2% peaks observed). Capped: 0.5 × 3.5 = 1.75%.
    arm = be_policy.arm_threshold_pct(2.5, 0.0, 3.5)
    assert arm == pytest.approx(1.75)


def test_cap_bites_when_arm_would_sit_at_or_above_tp1():
    # Widened 3% stop, TP1 only 2.6% away → pre-fix arm 3% NEVER fires
    # under a TP1 full close. Capped to 1.3%.
    arm = be_policy.arm_threshold_pct(3.0, 0.0, 2.6)
    assert arm == pytest.approx(1.3)


def test_cap_never_drops_arm_below_flat_trigger():
    # Tiny TP1 distance: 0.5 × 1.2 = 0.6 < flat 1.0 → flat trigger wins.
    arm = be_policy.arm_threshold_pct(3.0, 0.0, 1.2)
    assert arm == pytest.approx(1.0)


def test_no_tp1_distance_keeps_existing_behaviour():
    # Unknown TP1 → identical to the pre-fix noise-aware arm.
    assert be_policy.arm_threshold_pct(2.0, 0.0) == pytest.approx(2.0)
    assert be_policy.arm_threshold_pct(2.0, 4.0) == pytest.approx(3.0)


def test_cap_leaves_small_arms_untouched():
    # Tight 1% stop, TP1 3.5% away → arm 1% already well below the 1.75%
    # cap; nothing changes.
    arm = be_policy.arm_threshold_pct(1.0, 0.0, 3.5)
    assert arm == pytest.approx(1.0)


def test_cap_disabled_by_zero_fraction(monkeypatch):
    import config
    monkeypatch.setattr(config, "BE_ARM_TP1_CAP_FRACTION", 0.0)
    # Registry uninitialised → falls back to the (patched) config value.
    arm = be_policy.arm_threshold_pct(3.0, 0.0, 2.6)
    assert arm == pytest.approx(3.0)  # pre-fix behaviour restored


def test_cap_fraction_is_a_registered_tunable():
    assert "be_arm_tp1_cap_fraction" in rt.registry()
