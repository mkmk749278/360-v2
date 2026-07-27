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


# ---- build_inputs (store → controller inputs) ------------------------------


def test_build_inputs_maps_gates_and_cells():
    from src.emission_controller import build_inputs
    by_gate = {
        "context_floor:MOVER_TREND_PULLBACK": {"n": 100, "ev_per_suppression_r": -0.38, "verdict": "DROP"},
        "context_floor:FAILED_AUCTION_RECLAIM": {"n": 80, "ev_per_suppression_r": 0.12, "verdict": "KEEP"},
        "min_confidence": {"n": 50, "ev_per_suppression_r": 0.6, "verdict": "KEEP"},  # not a context_floor gate
    }
    matrix = {
        "QUIET_COMPRESSION_BREAK|A": {"strategy": "QUIET_COMPRESSION_BREAK", "n": 29, "verdict": "STRONG", "edge_r": 2.21, "avg_r": 0.3, "n_emitted": 2},
        "QUIET_COMPRESSION_BREAK|B": {"strategy": "QUIET_COMPRESSION_BREAK", "n": 12, "verdict": "STRONG", "edge_r": 1.9, "avg_r": 0.1, "n_emitted": 0},
        "MOVER_TREND_PULLBACK|A": {"strategy": "MOVER_TREND_PULLBACK", "n": 50, "verdict": "NEGATIVE", "edge_r": -0.5, "avg_r": -0.2, "n_emitted": 5},
    }
    out = build_inputs(by_gate=by_gate, matrix=matrix)
    assert set(out["gate_metrics"]) == {"MOVER_TREND_PULLBACK", "FAILED_AUCTION_RECLAIM"}  # min_confidence dropped
    assert out["gate_metrics"]["MOVER_TREND_PULLBACK"]["verdict"] == "DROP"
    # largest-n STRONG cell wins (n=29 over n=12); NEGATIVE cell is not a strong candidate
    assert out["best_strong_cell"]["QUIET_COMPRESSION_BREAK"] == {"n": 29, "edge": 2.21}
    assert "MOVER_TREND_PULLBACK" not in out["best_strong_cell"]
    # health R is sample-weighted; MTP negative
    assert out["strategy_health"]["MOVER_TREND_PULLBACK"]["emitted_avg_r"] == -0.2
    assert out["strategy_health"]["QUIET_COMPRESSION_BREAK"]["emitted_n"] == 2


def test_unlocked_cell_r_triggers_tighten_even_when_aggregate_healthy():
    # Strategy aggregate looks fine (no strategy_health), but the specific
    # unlocked cell's own edge has gone negative → per-cell reversal tightens.
    b = _bounds(boot_grace_cycles=1, stability_cycles=2)
    start = ControllerState(overrides={"QCB": StrategyOverride(min_samples=20)})
    cell = {"QCB": {"n": 25, "edge": 2.2}}
    unlocked = {"QCB": -0.5}  # the cell we unlocked now measures NEGATIVE
    state = start
    cs = 0
    applied = []
    for _ in range(2):
        cs += 1
        dec = run_cycle(gate_metrics={}, best_strong_cell=cell, strategy_health={},
                        global_params=GLOBAL, prior=state, bounds=b, cycles_since_start=cs,
                        unlocked_cell_r=unlocked)
        state = dec.state
        applied = [a for a in dec.adjustments if a.applied and a.param == "min_samples"]
    assert len(applied) == 1 and applied[0].new == 25  # 20 -> 25, tightened back
    assert state.overrides["QCB"].min_samples == 25


def test_unlocked_cell_r_none_is_backward_compatible():
    # Omitting unlocked_cell_r reproduces the pre-port behaviour exactly.
    b = _bounds(boot_grace_cycles=1, stability_cycles=2)
    cell = {"QCB": {"n": 25, "edge": 2.2}}
    decs, state = _drive([(({}), cell, {}), (({}), cell, {})], b)
    applied = [a for a in decs[1].adjustments if a.applied and a.param == "min_samples"]
    assert len(applied) == 1 and applied[0].new == 25  # still lowers to unlock (30->25)


# ---- routability: the action space vs what the policy can read --------------
#
# Layer G keys its inputs by *matrix* strategy (measurement arms `X@ATR`,
# shadow-only `SHADOW_*`) but its output is read under a live `SetupClass` key,
# so overrides on the other keys are unreachable. Measured on production
# 2026-07-27 (cycle 279): 9 of 18 persisted overrides were dead, 23 of 40
# lifetime promotions had gone to them.
#
# `routable` turns on measurement (always safe); `enforce_routable` acts on it.


def _routable_drive(cycles, bounds, state=None, start_since=0, routable=None,
                    enforce=False):
    """Same driver as ``_drive`` but with the routability parameters supplied."""
    state = state or ControllerState()
    cs = start_since
    decisions = []
    for gm, cell, health in cycles:
        cs += 1
        dec = run_cycle(
            gate_metrics=gm, best_strong_cell=cell, strategy_health=health,
            global_params=GLOBAL, prior=state, bounds=bounds, cycles_since_start=cs,
            routable=routable, enforce_routable=enforce,
        )
        state = dec.state
        decisions.append(dec)
    return decisions, state


def test_routable_omitted_leaves_behaviour_and_report_untouched():
    # The whole feature is opt-in: no `routable`, no classification, no report.
    b = _bounds(boot_grace_cycles=1, stability_cycles=2)
    cell = {"QCB@ATR": {"n": 25, "edge": 2.2}}
    decs, state = _drive([({}, cell, {}), ({}, cell, {})], b)
    assert decs[1].routability is None
    assert all(a.routable is None for d in decs for a in d.adjustments)
    # ...and the arm still promotes, exactly as it does in production today.
    assert state.overrides["QCB@ATR"].min_samples == 25


def test_measurement_reports_dead_overrides_without_changing_anything():
    # Measurement must be safe to ship ON: it names the dead keys and touches
    # nothing. This is the "dark means invisible to users, live to the owner"
    # half of the doctrine.
    b = _bounds(boot_grace_cycles=1, stability_cycles=2)
    start = ControllerState(overrides={
        "QCB@ATR": StrategyOverride(min_samples=15),      # unroutable, dead
        "SHADOW_FUNDING_FADE": StrategyOverride(min_samples=15),   # unroutable, dead
        "RANGE_FADE": StrategyOverride(min_samples=20),    # routable, real
    })
    decs, state = _routable_drive(
        [({}, {}, {})], b, state=start, start_since=5, routable={"RANGE_FADE"},
    )
    rep = decs[0].routability
    assert rep is not None and rep.enforced is False
    assert sorted(rep.dead_overrides) == ["QCB@ATR", "SHADOW_FUNDING_FADE"]
    assert rep.dead_overrides["QCB@ATR"] == {"min_samples": 15}
    assert rep.pruned == []
    # nothing removed, nothing promoted — measurement is inert
    assert set(state.overrides) == {"QCB@ATR", "SHADOW_FUNDING_FADE", "RANGE_FADE"}
    assert state.overrides["RANGE_FADE"].min_samples == 20


def test_measurement_names_the_live_candidates_that_phantoms_starve():
    # The decision-relevant counterfactual. Budget of 1; both an unroutable arm
    # and a live strategy are promotable. All min_samples candidates tie at sort
    # key 0.0 (ev is None), so the stable sort falls back to alphabetical and
    # "QCB@ATR" < "RANGE_FADE" — the phantom wins the slot.
    b = _bounds(boot_grace_cycles=1, stability_cycles=2, max_changes_per_cycle=1)
    cell = {"QCB@ATR": {"n": 25, "edge": 2.2}, "RANGE_FADE": {"n": 25, "edge": 1.1}}
    decs, state = _routable_drive(
        [({}, cell, {}), ({}, cell, {})], b, routable={"RANGE_FADE"},
    )
    rep = decs[1].routability
    # the wasted promotion is named, and so is what it displaced
    assert rep.promoted_unroutable == ["QCB@ATR|min_samples"]
    assert rep.starved_routable == ["RANGE_FADE|min_samples"]
    assert rep.wasted_promotions == 1
    # measurement did not intervene: the phantom really did take the slot
    assert state.overrides["QCB@ATR"].min_samples == 25
    assert "RANGE_FADE" not in state.overrides


def test_enforcement_gives_the_slot_to_the_live_strategy():
    # Same inputs as the test above, enforcement ON: the live strategy promotes
    # instead, and the counterfactual collapses to empty (nothing left to waste).
    b = _bounds(boot_grace_cycles=1, stability_cycles=2, max_changes_per_cycle=1)
    cell = {"QCB@ATR": {"n": 25, "edge": 2.2}, "RANGE_FADE": {"n": 25, "edge": 1.1}}
    decs, state = _routable_drive(
        [({}, cell, {}), ({}, cell, {})], b, routable={"RANGE_FADE"}, enforce=True,
    )
    rep = decs[1].routability
    assert rep.enforced is True
    assert rep.promoted_unroutable == [] and rep.starved_routable == []
    assert state.overrides["RANGE_FADE"].min_samples == 25
    assert "QCB@ATR" not in state.overrides


def test_enforcement_prunes_dead_overrides_and_their_history():
    b = _bounds(boot_grace_cycles=1, stability_cycles=2)
    start = ControllerState(
        overrides={
            "QCB@ATR": StrategyOverride(min_samples=15),
            "RANGE_FADE": StrategyOverride(min_samples=20),
        },
        history={"QCB@ATR|min_samples": ["LOWER", "LOWER"]},
        last_change_cycle={"QCB@ATR|min_samples": 3},
    )
    decs, state = _routable_drive(
        [({}, {}, {})], b, state=start, start_since=5,
        routable={"RANGE_FADE"}, enforce=True,
    )
    pruned = [a for a in decs[0].adjustments if a.status == "PRUNED"]
    assert [(a.strategy, a.param, a.old, a.new) for a in pruned] == [
        ("QCB@ATR", "min_samples", 15, None)
    ]
    assert pruned[0].applied and pruned[0].routable is False
    # state, history and rate-limit bookkeeping all cleared for the dead key
    assert "QCB@ATR" not in state.overrides
    assert "QCB@ATR|min_samples" not in state.history
    assert "QCB@ATR|min_samples" not in state.last_change_cycle
    # the real override is untouched
    assert state.overrides["RANGE_FADE"].min_samples == 20


def test_prunes_do_not_consume_the_promotion_budget():
    # A prune removes dead state; it must not cost a live strategy its slot.
    # With budget=1 and one prune due, the live promotion still lands.
    b = _bounds(boot_grace_cycles=1, stability_cycles=2, max_changes_per_cycle=1)
    start = ControllerState(overrides={"QCB@ATR": StrategyOverride(min_samples=15)})
    cell = {"RANGE_FADE": {"n": 25, "edge": 1.1}}
    decs, state = _routable_drive(
        [({}, cell, {}), ({}, cell, {})], b, state=start, start_since=5,
        routable={"RANGE_FADE"}, enforce=True,
    )
    statuses = {(a.strategy, a.status) for a in decs[0].adjustments} | {
        (a.strategy, a.status) for a in decs[1].adjustments
    }
    assert ("QCB@ATR", "PRUNED") in statuses
    assert state.overrides["RANGE_FADE"].min_samples == 25   # promotion not starved


def test_enforcement_is_idempotent_across_cycles():
    # Pruning is re-derived every cycle rather than run as a one-shot migration,
    # so a second cycle must be a no-op rather than re-emitting the same prune.
    b = _bounds(boot_grace_cycles=1, stability_cycles=2)
    start = ControllerState(overrides={"QCB@ATR": StrategyOverride(min_samples=15)})
    decs, state = _routable_drive(
        [({}, {}, {}), ({}, {}, {})], b, state=start, start_since=5,
        routable={"RANGE_FADE"}, enforce=True,
    )
    assert len([a for a in decs[0].adjustments if a.status == "PRUNED"]) == 1
    assert [a for a in decs[1].adjustments if a.status == "PRUNED"] == []
    assert decs[1].routability.dead_overrides == {}
    assert "QCB@ATR" not in state.overrides


def test_routable_matching_is_case_insensitive():
    # The policy upper-cases its lookup key; the filter must agree or it would
    # prune live strategies.
    b = _bounds(boot_grace_cycles=1, stability_cycles=2)
    start = ControllerState(overrides={"RANGE_FADE": StrategyOverride(min_samples=20)})
    decs, state = _routable_drive(
        [({}, {}, {})], b, state=start, start_since=5,
        routable={"range_fade"}, enforce=True,
    )
    assert decs[0].routability.dead_overrides == {}
    assert state.overrides["RANGE_FADE"].min_samples == 20
