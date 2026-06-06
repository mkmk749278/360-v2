"""Tests for the TRENDING-regime pre-TP suppression (session 20).

When TRENDING_PRETP_SUPPRESSED=true, signals dispatched in a TRENDING_UP
or TRENDING_DOWN entry regime have their grab fraction zeroed so the full
position rides the trend rather than being partially banked at +0.35%.
Covers the pure ``_apply_trending_pretp_suppress`` helper.
"""
from __future__ import annotations

import pytest

from src.execution.signal_dispatch import _apply_trending_pretp_suppress


@pytest.fixture
def _flag_on(monkeypatch):
    monkeypatch.setattr("config.TRENDING_PRETP_SUPPRESSED", True)


@pytest.fixture
def _flag_off(monkeypatch):
    monkeypatch.setattr("config.TRENDING_PRETP_SUPPRESSED", False)


def test_noop_when_flag_off(_flag_off):
    assert _apply_trending_pretp_suppress(0.5, "TRENDING_UP") == 0.5
    assert _apply_trending_pretp_suppress(0.5, "TRENDING_DOWN") == 0.5


@pytest.mark.parametrize("regime", ["TRENDING_UP", "TRENDING_DOWN", "trending_up", "trending_down"])
def test_zeroes_grab_on_trending_regimes(_flag_on, regime):
    assert _apply_trending_pretp_suppress(0.5, regime) == 0.0


@pytest.mark.parametrize("regime", ["RANGING", "QUIET", "VOLATILE", "", None])
def test_unchanged_on_non_trending_regimes(_flag_on, regime):
    assert _apply_trending_pretp_suppress(0.5, regime) == 0.5


def test_noop_when_grab_already_zero(_flag_on):
    # Pre-TP already disabled for this position — nothing to suppress.
    assert _apply_trending_pretp_suppress(0.0, "TRENDING_UP") == 0.0


def test_suppresses_any_positive_grab(_flag_on):
    # Whether grab is 0.3 (floor) or 1.0 (full-grab) — both suppressed.
    assert _apply_trending_pretp_suppress(0.30, "TRENDING_UP") == 0.0
    assert _apply_trending_pretp_suppress(1.00, "TRENDING_DOWN") == 0.0


def test_cancel_regimes_unaffected(_flag_on):
    # RANGING/QUIET are CANCEL-path — suppress must not touch them
    # (the cancel-fullgrab optimisation handles those separately).
    assert _apply_trending_pretp_suppress(0.5, "RANGING") == 0.5
    assert _apply_trending_pretp_suppress(0.5, "QUIET") == 0.5
