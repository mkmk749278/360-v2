"""Tests for the context-adaptive emission policy (src/context_emission_policy.py).

The Layer-C → emission consumer: the measured edge matrix drives a per-(strategy,
context) confidence floor.  These pin the truth table (relax STRONG/POSITIVE,
suppress NEGATIVE, base floor on cold/thin), the quality-anchor clamp, the
control-arm alias for graduated paths, and the divergence classifier.
"""
from __future__ import annotations

import pytest

from src.context_emission_policy import (
    DIV_AGREE_EMIT,
    DIV_AGREE_SUPPRESS,
    DIV_RELAX,
    DIV_TIGHTEN,
    EmissionDecision,
    PolicyParams,
    classify_divergence,
    effective_floor,
)
from src.strategy_edge import StrategyEdgeStore, StrategyOutcome

CTX = "OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL"
BASE = 65.0

# Explicit params so the tests never depend on config/tunable state.
P = PolicyParams(
    enabled=True,
    live=True,
    quality_anchor=60.0,
    strong_relax=5.0,
    positive_relax=3.0,
    min_samples=30,
    suppress_negative=True,
)


def _store() -> StrategyEdgeStore:
    return StrategyEdgeStore(persist_path="")  # empty path → no disk I/O


def _feed(store, strategy, ctx, wins, losses, *, source="emitted") -> None:
    for _ in range(wins):
        store.record(
            StrategyOutcome(strategy, ctx, "LONG", True, 1.0, 1.0, 2.0, source),
            persist=False,
        )
    for _ in range(losses):
        store.record(
            StrategyOutcome(strategy, ctx, "LONG", False, -1.0, -1.0, 0.0, source),
            persist=False,
        )


def test_strong_cell_relaxes_to_anchor() -> None:
    st = _store()
    _feed(st, "QUIET_COMPRESSION_BREAK", CTX, wins=30, losses=0)  # STRONG, n=30
    d = effective_floor("QUIET_COMPRESSION_BREAK", CTX, BASE, store=st, params=P)
    assert d.verdict == "STRONG"
    assert d.suppressed is False
    assert d.relaxed == 5.0
    assert d.effective_floor == 60.0  # 65 - 5, at the anchor


def test_relax_clamped_at_quality_anchor() -> None:
    st = _store()
    _feed(st, "SR_FLIP_RETEST", CTX, wins=30, losses=0)
    params = PolicyParams(True, True, 60.0, 10.0, 4.0, 30, True)  # strong_relax > gap
    d = effective_floor("SR_FLIP_RETEST", CTX, BASE, store=st, params=params)
    assert d.effective_floor == 60.0  # clamped, never below the anchor
    assert d.relaxed == 5.0


def test_positive_cell_relaxes_less() -> None:
    st = _store()
    _feed(st, "DIVERGENCE_CONTINUATION", CTX, wins=20, losses=10)  # POSITIVE
    d = effective_floor("DIVERGENCE_CONTINUATION", CTX, BASE, store=st, params=P)
    assert d.verdict == "POSITIVE"
    assert d.effective_floor == 62.0  # 65 - 3
    assert d.relaxed == 3.0


def test_negative_cell_suppresses() -> None:
    st = _store()
    _feed(st, "MOVER_AVWAP_SCALP", CTX, wins=5, losses=25)  # NEGATIVE
    d = effective_floor("MOVER_AVWAP_SCALP", CTX, BASE, store=st, params=P)
    assert d.verdict == "NEGATIVE"
    assert d.suppressed is True
    assert d.effective_floor == BASE  # floor is moot; suppressed overrides


def test_negative_not_suppressed_when_disabled() -> None:
    st = _store()
    _feed(st, "MOVER_AVWAP_SCALP", CTX, wins=5, losses=25)
    params = PolicyParams(True, True, 60.0, 5.0, 3.0, 30, False)  # suppress off
    d = effective_floor("MOVER_AVWAP_SCALP", CTX, BASE, store=st, params=params)
    assert d.suppressed is False
    assert d.effective_floor == BASE


def test_thin_strong_cell_does_not_relax() -> None:
    st = _store()
    _feed(st, "LIQUIDITY_SWEEP_REVERSAL", CTX, wins=20, losses=0)  # STRONG but n=20<30
    d = effective_floor("LIQUIDITY_SWEEP_REVERSAL", CTX, BASE, store=st, params=P)
    assert d.verdict == "STRONG"
    assert d.relaxed == 0.0
    assert d.effective_floor == BASE  # too few samples to lower the bar


def test_cold_cell_uses_base_floor() -> None:
    st = _store()
    _feed(st, "WHALE_MOMENTUM", CTX, wins=3, losses=2)  # n=5 < matrix floor
    d = effective_floor("WHALE_MOMENTUM", CTX, BASE, store=st, params=P)
    assert d.verdict == "INSUFFICIENT_DATA"
    assert d.suppressed is False
    assert d.effective_floor == BASE


def test_missing_context_or_setup_is_base() -> None:
    st = _store()
    assert effective_floor("", CTX, BASE, store=st, params=P).effective_floor == BASE
    assert effective_floor("X", "", BASE, store=st, params=P).effective_floor == BASE


def test_control_arm_alias_used_when_own_cell_thin() -> None:
    st = _store()
    # RANGE_FADE has no own outcomes; its shadow control arm is STRONG.
    _feed(st, "SHADOW_RANGE_FADE", CTX, wins=30, losses=0)
    d = effective_floor("RANGE_FADE", CTX, BASE, store=st, params=P)
    assert d.matrix_strategy == "SHADOW_RANGE_FADE"
    assert d.verdict == "STRONG"
    assert d.effective_floor == 60.0


def test_own_cell_preferred_over_control_arm() -> None:
    st = _store()
    # RANGE_FADE has its own populated STRONG cell → judged on itself, not the alias.
    _feed(st, "RANGE_FADE", CTX, wins=30, losses=0)
    _feed(st, "SHADOW_RANGE_FADE", CTX, wins=5, losses=25)  # alias would be NEGATIVE
    d = effective_floor("RANGE_FADE", CTX, BASE, store=st, params=P)
    assert d.matrix_strategy == "RANGE_FADE"
    assert d.verdict == "STRONG"
    assert d.suppressed is False


def test_anchor_never_raises_floor_below_base() -> None:
    st = _store()
    _feed(st, "QUIET_COMPRESSION_BREAK", CTX, wins=30, losses=0)
    # Base already below the anchor → no relaxation, floor unchanged (never raised).
    d = effective_floor("QUIET_COMPRESSION_BREAK", CTX, 55.0, store=st, params=P)
    assert d.effective_floor == 55.0
    assert d.relaxed == 0.0


def test_store_error_propagates_for_caller_fail_open() -> None:
    class _Boom:
        def verdict(self, *a):  # noqa: ANN001, ANN002
            raise RuntimeError("edge store down")

        def edge_r(self, *a):  # noqa: ANN001, ANN002
            raise RuntimeError

        def sample_count(self, *a):  # noqa: ANN001, ANN002
            raise RuntimeError

    with pytest.raises(RuntimeError):
        effective_floor("X", CTX, BASE, store=_Boom(), params=P)


# ---- divergence classifier -------------------------------------------------


def _dec(floor: float, suppressed: bool = False) -> EmissionDecision:
    return EmissionDecision(floor, "STRONG", 0.3, 30, "X", suppressed, 0.0, "test")


def test_divergence_relax() -> None:
    # policy would emit (62 ≥ 60) but the global floor suppresses (62 < 65).
    assert classify_divergence(62.0, 65.0, _dec(60.0)) == DIV_RELAX


def test_divergence_tighten() -> None:
    # global floor emits (70 ≥ 65) but the policy suppresses the cell.
    assert classify_divergence(70.0, 65.0, _dec(65.0, suppressed=True)) == DIV_TIGHTEN


def test_divergence_agreement() -> None:
    assert classify_divergence(70.0, 65.0, _dec(60.0)) == DIV_AGREE_EMIT
    assert classify_divergence(50.0, 65.0, _dec(60.0)) == DIV_AGREE_SUPPRESS


def test_divergence_component_block_forces_suppress() -> None:
    # A candidate the component floors already block is never a policy divergence.
    assert (
        classify_divergence(70.0, 65.0, _dec(60.0), components_ok=False)
        == DIV_AGREE_SUPPRESS
    )


# ------------------------------------------------------------- W5 gate override
from src.context_emission_policy import OVERRIDABLE_GATES, gate_override  # noqa: E402

# Params with the override measurement on (live stays dark by default).
P_GOV = PolicyParams(
    enabled=True,
    live=True,
    quality_anchor=60.0,
    strong_relax=5.0,
    positive_relax=3.0,
    min_samples=30,
    suppress_negative=True,
    gate_override_enabled=True,
    gate_override_live=False,
)


def test_overridable_gates_are_exactly_the_audited_two() -> None:
    # Safety gates must never creep in here without a deliberate edit + owner
    # sign-off; the tuple is the contract.
    assert OVERRIDABLE_GATES == ("dispatch_staleness", "level_still_in_play")


def test_strong_cell_with_sample_overrides() -> None:
    st = _store()
    _feed(st, "MEAN_REVERT_X", CTX, wins=30, losses=0)  # STRONG, n=30
    d = gate_override("MEAN_REVERT_X", CTX, store=st, params=P_GOV)
    assert d.would_override is True
    assert d.verdict == "STRONG"
    assert d.n >= 30


def test_positive_cell_never_overrides() -> None:
    # The bar is deliberately higher than the floor-relax: POSITIVE is not enough.
    st = _store()
    _feed(st, "DIVERGENCE_X", CTX, wins=20, losses=10)  # POSITIVE
    d = gate_override("DIVERGENCE_X", CTX, store=st, params=P_GOV)
    assert d.would_override is False
    assert "not_strong" in d.reason


def test_strong_but_thin_sample_never_overrides() -> None:
    st = _store()
    _feed(st, "QCB_X", CTX, wins=20, losses=0)  # STRONG but n=20 < 30
    d = gate_override("QCB_X", CTX, store=st, params=P_GOV)
    assert d.would_override is False
    assert "strong_thin" in d.reason


def test_negative_cell_never_overrides() -> None:
    st = _store()
    _feed(st, "RF_X", CTX, wins=2, losses=40)
    d = gate_override("RF_X", CTX, store=st, params=P_GOV)
    assert d.would_override is False


def test_disabled_measurement_never_overrides() -> None:
    st = _store()
    _feed(st, "MEAN_REVERT_X", CTX, wins=30, losses=0)
    off = PolicyParams(
        enabled=True, live=True, quality_anchor=60.0, strong_relax=5.0,
        positive_relax=3.0, min_samples=30, suppress_negative=True,
        gate_override_enabled=False, gate_override_live=False,
    )
    d = gate_override("MEAN_REVERT_X", CTX, store=st, params=off)
    assert d.would_override is False
    assert d.reason == "disabled"


def test_missing_context_never_overrides() -> None:
    st = _store()
    d = gate_override("MEAN_REVERT_X", "", store=st, params=P_GOV)
    assert d.would_override is False


def test_gate_override_defaults_dark() -> None:
    # Config default: measurement ON, live application OFF (dark-first).
    p = PolicyParams.from_config()
    assert p.gate_override_live is False
