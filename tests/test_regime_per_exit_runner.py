"""Tests for the regime-per-exit trend-aligned runner profile (§3.2b, Session 31).

Owner-signed-off 2026-06-21 ("raised threshold + trailing"): for a trend-aligned
entry the FSM already routes a pre-TP fill to the trailing runner
(``_pretp_trail_path``); this dispatch-side profile FEEDS it better — bank a small
partial (30%) at a raised pre-TP threshold (1.0R of the stop) and let the residual
ride the trail, instead of banking 50% at the flat +0.35% (TRENDING_UP capture was
−10% in the all-time Raw Edge).

Covers the pure ``_would_fsm_trail`` predicate (kept in lock-step with the FSM's
``_regime_exit_path``) and ``_apply_regime_trend_runner``.
"""
from __future__ import annotations

import pytest

from src.execution.signal_dispatch import (
    _apply_regime_trend_runner,
    _would_fsm_trail,
)


@pytest.fixture
def _on(monkeypatch):
    monkeypatch.setattr("config.REGIME_PER_EXIT_ENABLED", True)
    monkeypatch.setattr("config.REGIME_TREND_PRETP_R_FACTOR", 1.0)
    monkeypatch.setattr("config.REGIME_TREND_GRAB_FRACTION", 0.30)


# ── _would_fsm_trail predicate ───────────────────────────────────────────────

@pytest.mark.parametrize(
    "r5,r15,direction,expected",
    [
        ("TRENDING_UP", "TRENDING_UP", "LONG", True),     # clean aligned long
        ("TRENDING_DOWN", "TRENDING_DOWN", "SHORT", True),  # clean aligned short
        ("TRENDING_UP", "TRENDING_UP", "SHORT", False),   # 5m counter-trade
        ("TRENDING_UP", "RANGING", "LONG", False),        # 15m not trending
        ("TRENDING_UP", "TRENDING_DOWN", "LONG", False),  # 15m counter
        ("RANGING", "TRENDING_UP", "LONG", False),        # 5m not trending
        ("VOLATILE", "TRENDING_UP", "LONG", False),       # VOLATILE → own path
        ("", "", "LONG", False),                          # no regime data
    ],
)
def test_would_fsm_trail(r5, r15, direction, expected):
    assert _would_fsm_trail(r5, r15, direction) is expected


def test_would_fsm_trail_matches_fsm_regime_exit_path():
    """Lock-step guard: the dispatch predicate must agree with the FSM's
    ``_regime_exit_path`` returning 'TRAIL' for every regime/side combination.
    If the FSM routing changes, this fails and forces the predicate to follow."""
    from src.execution import position_state
    from src.execution.position_fsm import _regime_exit_path

    regimes = ["TRENDING_UP", "TRENDING_DOWN", "RANGING", "QUIET", "VOLATILE", ""]
    for r5 in regimes:
        for r15 in regimes:
            for side in ("LONG", "SHORT"):
                pos = position_state.Position(
                    signal_id="s", firebase_uid="u", symbol="BTCUSDT",
                    side=side, state=position_state.PositionState.OPEN,
                    entry_price_target=100.0, entry_price_filled=100.0,
                    sl_price=98.0, tp1_price=101.0, tp2_price=102.0, tp3_price=0.0,
                    total_qty=1.0, tp1_qty=0.3, tp2_qty=0.7, tp3_qty=0.0,
                    entry_regime=r5, entry_regime_15m=r15,
                )
                fsm_trails = _regime_exit_path(pos) == "TRAIL"
                assert _would_fsm_trail(r5, r15, side) is fsm_trails, (
                    f"predicate/FSM disagree for r5={r5} r15={r15} side={side}"
                )


# ── _apply_regime_trend_runner profile ───────────────────────────────────────

def test_runner_banks_small_and_later_when_aligned(_on):
    # sl_dist 2.0% → 1.0R floor raises a 0.35% threshold to 2.0%; grab → 0.30.
    grab, thr, applied = _apply_regime_trend_runner(
        0.50, 0.35, sl_dist_pct=2.0,
        regime_5m="TRENDING_UP", regime_15m="TRENDING_UP", direction="LONG",
    )
    assert applied is True
    assert grab == 0.30
    assert thr == pytest.approx(2.0)


def test_runner_keeps_higher_existing_threshold(_on):
    # A user/setup threshold already above 1.0R is not lowered.
    grab, thr, applied = _apply_regime_trend_runner(
        0.50, 3.0, sl_dist_pct=2.0,
        regime_5m="TRENDING_DOWN", regime_15m="TRENDING_DOWN", direction="SHORT",
    )
    assert applied is True
    assert grab == 0.30
    assert thr == pytest.approx(3.0)  # max(3.0, 2.0)


def test_runner_noop_when_not_trail_aligned(_on):
    # RANGING → FSM CANCEL path; must NOT apply (else bank-then-cancel).
    grab, thr, applied = _apply_regime_trend_runner(
        0.50, 0.35, sl_dist_pct=2.0,
        regime_5m="RANGING", regime_15m="RANGING", direction="LONG",
    )
    assert applied is False
    assert (grab, thr) == (0.50, 0.35)


def test_runner_noop_on_counter_trend(_on):
    grab, thr, applied = _apply_regime_trend_runner(
        0.50, 0.35, sl_dist_pct=2.0,
        regime_5m="TRENDING_UP", regime_15m="TRENDING_UP", direction="SHORT",
    )
    assert applied is False


def test_runner_respects_suppressed_pretp(_on):
    # grab already 0 (entry-only / user-OFF / allowlist) — never resurrect pre-TP.
    grab, thr, applied = _apply_regime_trend_runner(
        0.0, 0.35, sl_dist_pct=2.0,
        regime_5m="TRENDING_UP", regime_15m="TRENDING_UP", direction="LONG",
    )
    assert applied is False
    assert grab == 0.0


def test_runner_noop_when_disabled(monkeypatch):
    monkeypatch.setattr("config.REGIME_PER_EXIT_ENABLED", False)
    grab, thr, applied = _apply_regime_trend_runner(
        0.50, 0.35, sl_dist_pct=2.0,
        regime_5m="TRENDING_UP", regime_15m="TRENDING_UP", direction="LONG",
    )
    assert applied is False
    assert (grab, thr) == (0.50, 0.35)


def test_runner_handles_zero_sl_dist(_on):
    # Defensive: missing SL distance → threshold unchanged, grab still banked small.
    grab, thr, applied = _apply_regime_trend_runner(
        0.50, 0.35, sl_dist_pct=0.0,
        regime_5m="TRENDING_UP", regime_15m="TRENDING_UP", direction="LONG",
    )
    assert applied is True
    assert grab == 0.30
    assert thr == pytest.approx(0.35)
