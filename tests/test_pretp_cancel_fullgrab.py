"""Tests for the CANCEL-path pre-TP full-grab fee optimisation (session 19).

Closing the full position at the pre-TP LIMIT (grab=1.0) on CANCEL-bound
entry regimes removes the residual market close (a 3rd fee + slippage on
every win).  Ships dark; these tests cover the off/on gating and the
regime / grab preconditions via the pure ``_apply_cancel_fullgrab`` helper.
"""
from __future__ import annotations

import pytest

from src.execution.signal_dispatch import _apply_cancel_fullgrab


@pytest.fixture
def _flag_on(monkeypatch):
    monkeypatch.setattr("config.PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED", True)


@pytest.fixture
def _flag_off(monkeypatch):
    monkeypatch.setattr("config.PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED", False)


def test_noop_when_flag_off(_flag_off):
    assert _apply_cancel_fullgrab(0.5, "RANGING") == 0.5
    assert _apply_cancel_fullgrab(0.5, "QUIET") == 0.5


@pytest.mark.parametrize("regime", ["RANGING", "QUIET", "ranging", "quiet"])
def test_fullgrab_on_cancel_bound_regimes(_flag_on, regime):
    assert _apply_cancel_fullgrab(0.5, regime) == 1.0


@pytest.mark.parametrize("regime", ["TRENDING_UP", "TRENDING_DOWN", "VOLATILE", "", None])
def test_unchanged_on_non_cancel_regimes(_flag_on, regime):
    assert _apply_cancel_fullgrab(0.5, regime) == 0.5


def test_noop_when_pretp_disabled(_flag_on):
    # grab 0 means pre-TP is off for this position — nothing to optimise.
    assert _apply_cancel_fullgrab(0.0, "RANGING") == 0.0


def test_already_full_grab_stays_full(_flag_on):
    assert _apply_cancel_fullgrab(1.0, "RANGING") == 1.0
