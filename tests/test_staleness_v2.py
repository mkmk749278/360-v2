"""Tests for the geometry-aware dispatch-staleness V2 gate (src/staleness_v2.py).

Pins the truth table: drift toward the stop is bounded as a fraction of the
entry→SL distance, drift toward the target as a fraction of the entry→TP1
distance, and every degenerate-geometry path fails OPEN (fresh) — V2 must never
be stricter than V1 merely because an input was unreadable.
"""
from __future__ import annotations

from src.staleness_v2 import (
    DRIFT_NONE,
    DRIFT_TOWARD_SL,
    DRIFT_TOWARD_TP,
    StalenessV2Params,
    evaluate,
)

# Explicit params so tests never depend on config/tunable state.
P = StalenessV2Params(
    enabled=True, live=False, toward_sl_max_frac=0.40, toward_tp_max_frac=0.35
)

# LONG geometry: entry 100, SL 98 (distance 2), TP1 103 (distance 3).
LONG = dict(side="LONG", entry=100.0, stop_loss=98.0, tp1=103.0)
# SHORT mirror: entry 100, SL 102, TP1 97.
SHORT = dict(side="SHORT", entry=100.0, stop_loss=102.0, tp1=97.0)


def test_no_drift_is_fresh() -> None:
    d = evaluate(current_price=100.0, params=P, **LONG)
    assert d.fresh and d.drift_direction == DRIFT_NONE


def test_long_drift_toward_sl_within_budget() -> None:
    # 0.6 adverse on a 2.0 stop distance = 30% consumed < 40% budget.
    d = evaluate(current_price=99.4, params=P, **LONG)
    assert d.fresh
    assert d.drift_direction == DRIFT_TOWARD_SL
    assert abs(d.drift_frac - 0.30) < 1e-9


def test_long_drift_toward_sl_over_budget_blocks() -> None:
    # 1.0 adverse on a 2.0 stop = 50% consumed > 40% budget.
    d = evaluate(current_price=99.0, params=P, **LONG)
    assert not d.fresh
    assert d.drift_direction == DRIFT_TOWARD_SL


def test_long_chase_toward_tp_within_budget() -> None:
    # +0.9 favourable on a 3.0 TP distance = 30% < 35% budget.
    d = evaluate(current_price=100.9, params=P, **LONG)
    assert d.fresh
    assert d.drift_direction == DRIFT_TOWARD_TP


def test_long_chase_toward_tp_over_budget_blocks() -> None:
    # +1.2 favourable on 3.0 = 40% > 35%.
    d = evaluate(current_price=101.2, params=P, **LONG)
    assert not d.fresh
    assert d.drift_direction == DRIFT_TOWARD_TP


def test_short_mirror_toward_sl() -> None:
    # SHORT adverse drift = price UP toward the 102 stop; 101.0 = 50% > 40%.
    d = evaluate(current_price=101.0, params=P, **SHORT)
    assert not d.fresh
    assert d.drift_direction == DRIFT_TOWARD_SL


def test_short_mirror_toward_tp() -> None:
    # SHORT favourable = price DOWN toward the 97 target; 98.8 = 40% > 35%.
    d = evaluate(current_price=98.8, params=P, **SHORT)
    assert not d.fresh
    assert d.drift_direction == DRIFT_TOWARD_TP


def test_v1_incident_case_price_at_stop_blocks() -> None:
    # The 2026-05-07 pathology: current price already AT the stop.
    d = evaluate(current_price=98.0, params=P, **LONG)
    assert not d.fresh
    assert d.drift_frac >= 1.0


def test_geometry_awareness_wide_stop_tolerates_v1_fatal_drift() -> None:
    # 0.5% drift — V1's flat kill line — on a wide mover stop (5% away) is
    # only 10% of the stop budget: V2 keeps it fresh.  The point of V2.
    d = evaluate(
        side="LONG", entry=100.0, stop_loss=95.0, tp1=107.5,
        current_price=99.5, params=P,
    )
    assert d.fresh
    assert abs(d.drift_frac - 0.10) < 1e-9


def test_degenerate_sl_fails_open() -> None:
    # Inverted stop (LONG with SL above entry) on the adverse side → fresh.
    d = evaluate(
        side="LONG", entry=100.0, stop_loss=101.0, tp1=103.0,
        current_price=99.0, params=P,
    )
    assert d.fresh and d.reason == "degenerate_sl_geometry"


def test_degenerate_tp_fails_open() -> None:
    d = evaluate(
        side="LONG", entry=100.0, stop_loss=98.0, tp1=0.0,
        current_price=101.0, params=P,
    )
    assert d.fresh and d.reason == "degenerate_tp_geometry"


def test_unreadable_side_fails_open() -> None:
    d = evaluate(
        side="", entry=100.0, stop_loss=98.0, tp1=103.0,
        current_price=99.0, params=P,
    )
    assert d.fresh and d.reason == "unreadable_inputs"


def test_zero_prices_fail_open() -> None:
    d = evaluate(
        side="LONG", entry=0.0, stop_loss=98.0, tp1=103.0,
        current_price=99.0, params=P,
    )
    assert d.fresh
    d = evaluate(current_price=0.0, params=P, **LONG)
    assert d.fresh


def test_params_from_config_defaults_dark() -> None:
    # The live flag must default OFF (dark-first); measurement defaults ON.
    p = StalenessV2Params.from_config()
    assert p.enabled is True
    assert p.live is False
    assert p.toward_sl_max_frac > 0
    assert p.toward_tp_max_frac > 0
