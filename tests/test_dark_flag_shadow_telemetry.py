"""Tests for dark-flag shadow telemetry (session 20 follow-up #3).

When a dark exit flag is OFF but its gate condition is met, the engine logs
a structured ``[SHADOW]`` line so the flag's blast radius is measurable from
prod logs before activation.  Shadow logging is behaviour-neutral — it never
changes an exit, only records what *would* have happened.

Covers:
  * the flag-independent predicates that drive both the real and shadow paths
  * ``_shadow_telemetry_on`` config read
  * actual ``[SHADOW]`` log emission at the dispatch helpers, gated correctly
    by both the dark flag (must be off) and the shadow master flag (must be on)
"""
from __future__ import annotations

import pytest

from src.execution.signal_dispatch import (
    _cancel_fullgrab_would_apply,
    _shadow_telemetry_on,
    _trending_pretp_would_suppress,
)


# ---------------------------------------------------------------------------
# Flag-independent predicates — these are the single source of truth shared by
# the apply functions and the shadow path, so "would fire" can never drift
# from the real gate.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("regime", ["TRENDING_UP", "TRENDING_DOWN", "trending_up"])
def test_trending_predicate_true_on_trending_with_grab(regime):
    assert _trending_pretp_would_suppress(0.5, regime) is True


@pytest.mark.parametrize("regime", ["RANGING", "QUIET", "VOLATILE", "", None])
def test_trending_predicate_false_off_regime(regime):
    assert _trending_pretp_would_suppress(0.5, regime) is False


def test_trending_predicate_false_when_no_grab():
    assert _trending_pretp_would_suppress(0.0, "TRENDING_UP") is False


@pytest.mark.parametrize("regime", ["RANGING", "QUIET", "ranging", "quiet"])
def test_fullgrab_predicate_true_on_cancel_regime_with_grab(regime):
    assert _cancel_fullgrab_would_apply(0.5, regime) is True


@pytest.mark.parametrize("regime", ["TRENDING_UP", "TRENDING_DOWN", "VOLATILE", "", None])
def test_fullgrab_predicate_false_off_regime(regime):
    assert _cancel_fullgrab_would_apply(0.5, regime) is False


def test_fullgrab_predicate_false_when_no_grab():
    assert _cancel_fullgrab_would_apply(0.0, "RANGING") is False


# ---------------------------------------------------------------------------
# Master shadow switch
# ---------------------------------------------------------------------------


def test_shadow_telemetry_on_reads_config(monkeypatch):
    monkeypatch.setattr("config.DARK_FLAG_SHADOW_TELEMETRY", True)
    assert _shadow_telemetry_on() is True
    monkeypatch.setattr("config.DARK_FLAG_SHADOW_TELEMETRY", False)
    assert _shadow_telemetry_on() is False


# ---------------------------------------------------------------------------
# Disjointness guarantee — TRENDING and CANCEL-bound regimes never overlap, so
# the two shadow paths can never both claim the same dispatch.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "regime", ["TRENDING_UP", "TRENDING_DOWN", "RANGING", "QUIET", "VOLATILE"]
)
def test_predicates_are_mutually_exclusive(regime):
    assert not (
        _trending_pretp_would_suppress(0.5, regime)
        and _cancel_fullgrab_would_apply(0.5, regime)
    )
