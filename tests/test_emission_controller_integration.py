"""Integration tests for the Layer-G emission controller wiring.

Covers the pieces the pure decision-core tests don't: the persistence store +
hot-path override accessor + ledger, the per-cell reversal (review #1), the
config-driven envelope, and the ``context_emission_policy`` overlay that is
provably inert when the master flag is off.
"""
from __future__ import annotations

import json

import config
from src.context_emission_policy import PolicyParams, _apply_controller_override
from src.emission_controller import (
    Adjustment,
    ControllerBounds,
    ControllerDecision,
    ControllerState,
    EmissionControllerStore,
    StrategyOverride,
    bounds_from_config,
    run_cycle,
)


GLOBAL = {"suppress_negative": True, "min_samples": 30}


def _params(**kw) -> PolicyParams:
    base = dict(
        enabled=True, live=True, quality_anchor=60.0, strong_relax=5.0,
        positive_relax=2.0, min_samples=30, suppress_negative=True, cohort_aware=False,
    )
    base.update(kw)
    return PolicyParams(**base)


# ---------------------------------------------------------------------------
# Persistence store + hot-path accessor
# ---------------------------------------------------------------------------


def test_store_roundtrip_and_get_override(tmp_path):
    path = str(tmp_path / "state.json")
    store = EmissionControllerStore(path).load()
    # empty by default → follow-global override
    assert store.get_override("MOVER_TREND_PULLBACK").min_samples is None

    state = ControllerState(overrides={"MOVER_TREND_PULLBACK": StrategyOverride(min_samples=20)})
    store.apply_decision(ControllerDecision(state=state, adjustments=[]))
    # hot-path snapshot reflects it immediately
    assert store.get_override("MOVER_TREND_PULLBACK").min_samples == 20

    # persisted + reloaded
    reloaded = EmissionControllerStore(path).load()
    assert reloaded.get_override("MOVER_TREND_PULLBACK").min_samples == 20


def test_apply_decision_writes_ledger(tmp_path):
    path = str(tmp_path / "state.json")
    ledger = str(tmp_path / "ledger.jsonl")
    store = EmissionControllerStore(path, ledger).load()
    adj = Adjustment(
        strategy="QUIET_COMPRESSION_BREAK", param="min_samples", old=30, new=25,
        applied=True, status="PROMOTED", reason="unlock", verdict="LOWER", n=29,
    )
    state = ControllerState(overrides={"QUIET_COMPRESSION_BREAK": StrategyOverride(min_samples=25)})
    store.apply_decision(ControllerDecision(state=state, adjustments=[adj]))

    lines = [json.loads(x) for x in open(ledger).read().splitlines() if x.strip()]
    assert len(lines) == 1
    assert lines[0]["strategy"] == "QUIET_COMPRESSION_BREAK"
    assert lines[0]["applied"] is True and lines[0]["new"] == 25
    assert "ts" in lines[0]


def test_corrupt_state_file_starts_clean(tmp_path):
    path = str(tmp_path / "state.json")
    open(path, "w").write("{ this is not valid json")
    store = EmissionControllerStore(path).load()  # must not raise
    assert store.state.cycle == 0


# ---------------------------------------------------------------------------
# Review #1 — per-cell reversal
# ---------------------------------------------------------------------------


def _bounds(**kw) -> ControllerBounds:
    base = dict(stability_cycles=2, boot_grace_cycles=1, min_gate_n=40,
                promote_ev_r=0.25, max_changes_per_cycle=2, min_samples_floor=15,
                min_samples_ceiling=30, min_samples_step=5, health_raise_ev_r=-0.10,
                health_min_n=20)
    base.update(kw)
    return ControllerBounds(**base)


def test_per_cell_reversal_tightens_even_when_strategy_average_healthy():
    """A losing UNLOCKED cell must trigger a tighten even though the strategy's
    aggregate emitted edge is healthy — the gap review #1 flagged."""
    bounds = _bounds()
    S = "MOVER_TREND_PULLBACK"
    # strategy already loosened to 20; aggregate health is GOOD (+0.5R, n=50)
    state = ControllerState(overrides={S: StrategyOverride(min_samples=20)})
    healthy = {S: {"emitted_avg_r": 0.5, "emitted_n": 50}}
    # ...but the specific unlocked cell is bleeding (−0.30R)
    unlocked = {S: -0.30}

    cs = 0
    all_applied = []
    for _ in range(3):  # boot_grace=1, K=2 → promotes once stable
        cs += 1
        dec = run_cycle(
            gate_metrics={}, best_strong_cell={}, strategy_health=healthy,
            global_params=GLOBAL, prior=state, bounds=bounds, cycles_since_start=cs,
            unlocked_cell_r=unlocked,
        )
        state = dec.state
        all_applied.extend(dec.applied)
    raises = [a for a in all_applied if a.param == "min_samples" and a.new > a.old]
    assert raises, "losing unlocked cell should have tightened min_samples back up"
    assert raises[0].new == 25  # 20 + step(5)


def test_no_per_cell_reversal_when_cell_healthy():
    """Same setup but the unlocked cell is fine → no tighten (baseline)."""
    bounds = _bounds()
    S = "MOVER_TREND_PULLBACK"
    state = ControllerState(overrides={S: StrategyOverride(min_samples=20)})
    healthy = {S: {"emitted_avg_r": 0.5, "emitted_n": 50}}
    unlocked = {S: 0.40}  # cell is winning
    cs = 0
    dec = None
    for _ in range(3):
        cs += 1
        dec = run_cycle(
            gate_metrics={}, best_strong_cell={}, strategy_health=healthy,
            global_params=GLOBAL, prior=state, bounds=bounds, cycles_since_start=cs,
            unlocked_cell_r=unlocked,
        )
        state = dec.state
    assert not [a for a in dec.applied if a.param == "min_samples" and a.new > a.old]


# ---------------------------------------------------------------------------
# Envelope from config
# ---------------------------------------------------------------------------


def test_bounds_from_config_clamps_ceiling_to_global(monkeypatch):
    monkeypatch.setattr(config, "CONTEXT_EMISSION_MIN_SAMPLES", 30)
    monkeypatch.setattr(config, "EMISSION_CONTROLLER_MIN_SAMPLES_FLOOR", 15)
    b = bounds_from_config()
    # the controller can never raise an override above the global default
    assert b.min_samples_ceiling == 30
    assert b.min_samples_floor == 15


# ---------------------------------------------------------------------------
# Hot-path overlay — provably inert when the flag is off
# ---------------------------------------------------------------------------


def test_overlay_inert_when_disabled(monkeypatch):
    monkeypatch.setattr(config, "EMISSION_CONTROLLER_ENABLED", False)
    p = _params(min_samples=30, suppress_negative=True)
    # returns the SAME object, untouched — zero store access
    assert _apply_controller_override("MOVER_TREND_PULLBACK", p) is p


def test_overlay_applies_override_when_enabled(tmp_path, monkeypatch):
    from src import emission_controller as ec

    monkeypatch.setattr(config, "EMISSION_CONTROLLER_ENABLED", True)
    # inject a store with a min_samples override for our strategy
    store = ec.EmissionControllerStore(str(tmp_path / "s.json")).load()
    store.apply_decision(ControllerDecision(
        state=ControllerState(overrides={"MOVER_TREND_PULLBACK": StrategyOverride(min_samples=15)}),
        adjustments=[],
    ))
    monkeypatch.setattr(ec, "_store", store)  # make get_default_store() return ours

    p = _params(min_samples=30, suppress_negative=True)
    out = _apply_controller_override("MOVER_TREND_PULLBACK", p)
    assert out.min_samples == 15                 # override applied
    assert out.suppress_negative is True         # untouched (no override)
    # a strategy with no override is unchanged
    assert _apply_controller_override("OTHER_STRAT", p).min_samples == 30
