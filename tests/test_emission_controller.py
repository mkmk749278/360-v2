"""Tests for the Layer-G autonomous emission controller decision core.

Deterministic — plain-dict inputs, no I/O. Pins the safety envelope: nothing
promotes on first sight, boot-grace and stability hold, the EV bar gates only the
risky (loosen) direction, blast radius is bounded, and a promotion clears history
so a reversal needs fresh evidence.
"""
from __future__ import annotations

from src.emission_controller import (
    ControllerBounds,
    ControllerState,
    StrategyOverride,
    run_cycle,
)

GLOBAL = {"suppress_negative": True, "min_samples": 30}


def _bounds(**kw):
    base = dict(stability_cycles=2, boot_grace_cycles=1, min_gate_n=40,
                promote_ev_r=0.25, max_changes_per_cycle=2,
                min_samples_floor=15, min_samples_ceiling=30, min_samples_step=5)
    base.update(kw)
    return ControllerBounds(**base)


def _drive(cycles, bounds, state=None, start_since=0):
    """Feed a list of (gate_metrics, best_strong_cell, strategy_health) tuples."""
    state = state or ControllerState()
    cs = start_since
    decisions = []
    for gm, cell, health in cycles:
        cs += 1
        dec = run_cycle(
            gate_metrics=gm, best_strong_cell=cell, strategy_health=health,
            global_params=GLOBAL, prior=state, bounds=bounds, cycles_since_start=cs,
        )
        state = dec.state
        decisions.append(dec)
    return decisions, state


def _drop(ev=-0.38, n=100):
    return {"MTP": {"n": n, "ev_per_suppression_r": ev, "verdict": "DROP"}}


def _keep(ev=0.15, n=100):
    return {"MTP": {"n": n, "ev_per_suppression_r": ev, "verdict": "KEEP"}}


# ---- boot grace + stability ------------------------------------------------


def test_nothing_promotes_during_boot_grace():
    b = _bounds(boot_grace_cycles=3, stability_cycles=2)
    decs, state = _drive([( _drop(), {}, {})] * 3, b)  # cs 1,2,3 all within grace
    # stable DROP by cycle 2, but grace covers cycles 1..3 → never applied
    assert all(not a.applied for d in decs for a in d.adjustments)
    assert any("boot_grace" in a.reason for a in decs[-1].adjustments)
    assert state.overrides.get("MTP", StrategyOverride()).suppress_negative is None


def test_single_drop_does_not_promote_then_stable_drop_does():
    b = _bounds(boot_grace_cycles=1, stability_cycles=2)
    # cs1: one DROP (not stable). cs2: two DROP (stable) + past grace → promote.
    decs, state = _drive([(_drop(), {}, {}), (_drop(), {}, {})], b)
    assert not any(a.applied for a in decs[0].adjustments)   # first sight: never
    applied = [a for a in decs[1].adjustments if a.applied]
    assert len(applied) == 1
    assert applied[0].param == "suppress_negative" and applied[0].new is False
    assert state.overrides["MTP"].suppress_negative is False


# ---- EV bar gates only the risky direction ---------------------------------


def test_loosen_blocked_when_ev_below_bar():
    b = _bounds(boot_grace_cycles=1, stability_cycles=2, promote_ev_r=0.25)
    decs, state = _drive([(_drop(ev=-0.10), {}, {}), (_drop(ev=-0.10), {}, {})], b)
    pend = [a for a in decs[1].adjustments if a.param == "suppress_negative"]
    assert pend and not pend[0].applied
    assert "ev_below_bar" in pend[0].reason
    assert state.overrides.get("MTP", StrategyOverride()).suppress_negative is None


def test_reprotect_does_not_require_ev_bar():
    b = _bounds(boot_grace_cycles=1, stability_cycles=2, promote_ev_r=0.25)
    # start already loosened (suppress OFF); a low-EV KEEP should still re-protect
    start = ControllerState(overrides={"MTP": StrategyOverride(suppress_negative=False)})
    decs, state = _drive([(_keep(ev=0.05), {}, {}), (_keep(ev=0.05), {}, {})], b, state=start)
    applied = [a for a in decs[1].adjustments if a.applied]
    assert len(applied) == 1 and applied[0].new is True
    # reverting to the global default stores None (follow global)
    assert state.overrides["MTP"].suppress_negative is None


# ---- min_samples unlock + auto-tighten -------------------------------------


def test_min_samples_lowers_to_unlock_thin_strong_cell():
    b = _bounds(boot_grace_cycles=1, stability_cycles=2)
    cell = {"QCB": {"n": 25, "edge": 2.2}}   # 15 <= 25 < 30 → unlock candidate
    gm = {}  # no gate verdict for QCB
    decs, state = _drive([(gm, cell, {}), (gm, cell, {})], b)
    applied = [a for a in decs[1].adjustments if a.applied and a.param == "min_samples"]
    assert len(applied) == 1 and applied[0].new == 25
    assert state.overrides["QCB"].min_samples == 25


def test_min_samples_raises_back_when_emissions_sour():
    b = _bounds(boot_grace_cycles=1, stability_cycles=2)
    start = ControllerState(overrides={"QCB": StrategyOverride(min_samples=20)})
    # emissions from the loosened cell are losing → tighten back toward global
    health = {"QCB": {"emitted_avg_r": -0.5, "emitted_n": 30}}
    cell = {"QCB": {"n": 25, "edge": 2.2}}
    decs, state = _drive([(({}), cell, health), (({}), cell, health)], b, state=start)
    applied = [a for a in decs[1].adjustments if a.applied and a.param == "min_samples"]
    assert len(applied) == 1 and applied[0].new == 25  # 20 -> 25 (step up toward ceiling)
    assert state.overrides["QCB"].min_samples == 25


# ---- blast radius + anti-oscillation ---------------------------------------


def test_blast_radius_caps_promotions_and_prefers_larger_ev():
    b = _bounds(boot_grace_cycles=1, stability_cycles=2, max_changes_per_cycle=1)
    gm = {
        "MTP": {"n": 100, "ev_per_suppression_r": -0.38, "verdict": "DROP"},
        "SRF": {"n": 100, "ev_per_suppression_r": -0.60, "verdict": "DROP"},
    }
    decs, state = _drive([(gm, {}, {}), (gm, {}, {})], b)
    applied = [a for a in decs[1].adjustments if a.applied]
    deferred = [a for a in decs[1].adjustments if not a.applied]
    assert len(applied) == 1 and applied[0].strategy == "SRF"   # larger |EV| wins
    assert any("deferred:blast_radius" in a.reason for a in deferred)


def test_promotion_clears_history_so_reversal_needs_fresh_k():
    b = _bounds(boot_grace_cycles=1, stability_cycles=2)
    # promote suppress OFF at cs2, then immediately feed KEEP — must NOT flip back at cs3
    cycles = [(_drop(), {}, {}), (_drop(), {}, {}), (_keep(), {}, {}), (_keep(), {}, {})]
    decs, state = _drive(cycles, b)
    assert decs[1].applied and decs[1].applied[0].new is False   # loosened at cs2
    assert not decs[2].applied                                   # cs3: only 1 fresh KEEP → no flip
    assert any(a.applied and a.new is True for a in decs[3].adjustments)  # cs4: 2 fresh KEEP → re-protect


# ---- serialization ---------------------------------------------------------


def test_state_round_trips_through_dict():
    b = _bounds(boot_grace_cycles=1, stability_cycles=2)
    _, state = _drive([(_drop(), {}, {}), (_drop(), {}, {})], b)
    restored = ControllerState.from_dict(state.to_dict())
    assert restored.overrides["MTP"].suppress_negative is False
    assert restored.cycle == state.cycle
    assert restored.last_change_cycle == state.last_change_cycle


def test_insufficient_gate_sample_never_advances_stability():
    b = _bounds(boot_grace_cycles=1, stability_cycles=2, min_gate_n=40)
    # DROP verdicts but n below the gate floor → tokens are SKIP, never stable
    thin = {"MTP": {"n": 10, "ev_per_suppression_r": -0.9, "verdict": "DROP"}}
    decs, state = _drive([(thin, {}, {})] * 5, b)
    assert all(not a.applied for d in decs for a in d.adjustments)
    assert state.overrides.get("MTP", StrategyOverride()).suppress_negative is None
