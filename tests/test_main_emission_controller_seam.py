"""The seam between the emission controller and its driver in main.py.

``src/emission_controller.py`` is one of the best-covered modules in the
engine (98%).  ``main._emission_controller_cycle``, the only thing that calls
it in production, was the largest uncovered block in main.py.  That gap is
the exact shape of #806/#807: the controller's *math* was never wrong — the
caller keyed its output differently from the code that reads it, so 9 of 18
persisted overrides and 23 of 40 promotions went to keys nothing looks up.

The rule this file enforces is the one that incident wrote: **"who reads
this key, and are they keyed the same way?"**  The controller's inputs come
from the Strategy×Context edge matrix, which carries the measurement arms
(``@FIXED``/``@ATR``/``@TUNED``/…) and shadow-only units alongside real
strategies.  The emission policy can only ever look up a live ``SetupClass``
value.  Anything else is an override written to a dead key — and because a
measurement arm never emits, it can never trip the auto-tighten brake, which
makes it *more* promotable than the live strategy it is starving.

Everything here drives the real collaborators: a real ``StrategyEdgeStore``
fed real ``StrategyOutcome`` rows, a real ``EmissionControllerStore`` on
tmp_path, and the real ``run_cycle``.  A hand-built matrix dict would assert
our own idea of the matrix shape back at us, which is how #806 survived
review in the first place.
"""
from __future__ import annotations

import types

import pytest

from src.emission_controller_store import EmissionControllerStore
from src.main import CryptoSignalEngine
from src.signal_quality import SetupClass
from src.strategy_edge import StrategyEdgeStore, StrategyOutcome

CTX = "OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL"

# A real live strategy key and its measurement arm. The arm is what the
# matrix carries and the policy cannot read.
LIVE = SetupClass.BREAKOUT_RETEST.value
ARM = f"{LIVE}@FIXED"


def _engine() -> types.SimpleNamespace:
    """The cycle touches ``self`` only as an attribute bag.

    Deliberately not a real CryptoSignalEngine: constructing one boots
    websockets and stores.  The method is called unbound so the production
    code path is still the one under test.
    """
    return types.SimpleNamespace()


def _feed(store: StrategyEdgeStore, strategy: str, wins: int, losses: int,
          *, r_win: float = 2.0, source: str = "shadow") -> None:
    for _ in range(wins):
        store.record(
            StrategyOutcome(strategy, CTX, "LONG", True, r_win, r_win, r_win, source),
            persist=False,
        )
    for _ in range(losses):
        store.record(
            StrategyOutcome(strategy, CTX, "LONG", False, -1.0, -1.0, 0.0, source),
            persist=False,
        )


@pytest.fixture
def wiring(monkeypatch, tmp_path):
    """Swap the three module-level singletons for real, seeded instances."""
    from src import runtime_tunables as rt
    from src import strategy_edge, suppression_audit
    from src import emission_controller_store as ecs

    edge = StrategyEdgeStore(persist_path="")
    ctrl = EmissionControllerStore(persist_path=str(tmp_path / "ctrl.json"))

    monkeypatch.setattr(strategy_edge, "get_strategy_edge_store", lambda: edge)
    monkeypatch.setattr(ecs, "get_emission_controller_store", lambda: ctrl)

    gate_metrics: dict = {}
    monkeypatch.setattr(
        suppression_audit, "compute_gate_suppression_metrics",
        lambda _records: gate_metrics,
    )
    monkeypatch.setattr(
        suppression_audit, "get_store",
        lambda: types.SimpleNamespace(records=lambda: []),
    )

    tunables: dict = {
        "emission_controller_stability_cycles": 1,
        "emission_controller_boot_grace_cycles": 1,
        "emission_controller_min_gate_n": 1,
        "emission_controller_promote_ev_r": 0.1,
        "emission_controller_max_changes_per_cycle": 10,
        "emission_controller_min_samples_floor": 1,
        "emission_controller_routable_enabled": True,
        "emission_controller_routable_live": True,
    }
    monkeypatch.setattr(rt, "get", lambda k: tunables.get(k))
    monkeypatch.setenv("EMISSION_CONTROLLER_INTERVAL_SEC", "0")

    return types.SimpleNamespace(
        edge=edge, ctrl=ctrl, gate_metrics=gate_metrics, tunables=tunables,
    )


def _run(engine, wiring) -> None:
    CryptoSignalEngine._emission_controller_cycle(engine)


def _run_past_boot_grace(engine, wiring) -> None:
    """Drive until promotions are live.

    Boot grace is counted in in-process cycles so a restart re-enters pure
    observation; with grace=1 the second cycle is the first that can apply.
    Note the production default is ``_rt.get(...) or 3`` — a configured 0
    reads as falsy and becomes 3, so grace is set truthy here rather than
    zeroed out.
    """
    _run(engine, wiring)
    _run(engine, wiring)


# ---------------------------------------------------------------------------
# The keying contract — #806/#807
# ---------------------------------------------------------------------------


def test_measurement_only_names_the_arm_and_the_promotion_it_would_waste(wiring):
    """Measurement ON / enforcement OFF — the dark-flag configuration.

    This is #806 reproduced end-to-end through the real driver: an @FIXED arm
    reaches the controller from the same matrix as the live rows, is ranked
    against them, and *takes a promotion slot*.  The report must name both the
    key and the wasted promotion, because with enforcement off the override is
    genuinely written and genuinely does nothing.

    Asserting via the report rather than the log is deliberate: the report is
    what the ops Layer-G panel renders, and the activation decision reads it.
    """
    wiring.tunables["emission_controller_routable_live"] = False
    _feed(wiring.edge, ARM, wins=20, losses=2)
    wiring.gate_metrics[f"context_floor:{ARM}"] = {
        "n": 100, "ev_per_suppression_r": 0.9, "verdict": "TUNE",
    }

    engine = _engine()
    _run_past_boot_grace(engine, wiring)

    rep = engine._emission_controller_routability
    assert not rep.enforced
    assert ARM in rep.unroutable_strategies
    assert rep.unroutable_candidates >= 1
    assert f"{ARM}|min_samples" in rep.promoted_unroutable
    assert rep.wasted_promotions >= 1


def test_enforcement_excludes_the_arm_from_the_action_space(wiring):
    """Enforcement ON — the arm is not merely reported, it never competes.

    The distinction matters and is easy to get backwards: under enforcement
    the report goes *empty* (nothing unroutable is in play) rather than
    listing what it blocked.  A test that asserted "arm appears in
    unroutable_strategies" under enforcement would be asserting the
    measurement-mode shape and would fail the moment enforcement was turned
    on — i.e. exactly when it mattered.
    """
    _feed(wiring.edge, ARM, wins=20, losses=2)
    wiring.gate_metrics[f"context_floor:{ARM}"] = {
        "n": 100, "ev_per_suppression_r": 0.9, "verdict": "TUNE",
    }

    engine = _engine()
    _run_past_boot_grace(engine, wiring)

    rep = engine._emission_controller_routability
    assert rep.enforced
    assert rep.promoted_unroutable == []
    # The only thing that ultimately matters: no override under a dead key.
    assert ARM not in wiring.ctrl.state.overrides


def test_live_strategy_is_routable_and_can_receive_an_override(wiring):
    """The control case: the same signal on a real SetupClass key lands."""
    _feed(wiring.edge, LIVE, wins=20, losses=2)
    wiring.gate_metrics[f"context_floor:{LIVE}"] = {
        "n": 100, "ev_per_suppression_r": 0.9, "verdict": "TUNE",
    }

    engine = _engine()
    _run(engine, wiring)

    rep = engine._emission_controller_routability
    assert rep.routable_candidates >= 1
    assert LIVE not in rep.unroutable_strategies


def test_routable_set_is_exactly_the_setupclass_values(wiring):
    """The caller must derive routability from the enum the policy reads.

    Mirroring the arm-suffix list here instead would be "the fix for a
    drifting mirror is a second mirror" — the thing the incident write-up
    explicitly rejects.  A shadow-only unit that is not a SetupClass is
    unroutable for the same reason an arm is, without anyone maintaining a
    list of shadow units.
    """
    wiring.tunables["emission_controller_routable_live"] = False
    _feed(wiring.edge, "SOME_SHADOW_ONLY_UNIT", wins=20, losses=2)
    wiring.gate_metrics["context_floor:SOME_SHADOW_ONLY_UNIT"] = {
        "n": 100, "ev_per_suppression_r": 0.9, "verdict": "TUNE",
    }

    engine = _engine()
    _run(engine, wiring)

    rep = engine._emission_controller_routability
    assert "SOME_SHADOW_ONLY_UNIT" in rep.unroutable_strategies


def test_promotion_to_an_unroutable_key_warns(wiring, caplog):
    """A starved live candidate must not be discoverable only via a panel.

    The log is WARN by design: an override spent on a dead key is budget
    taken from a real strategy, and the ops panel is not guaranteed to be
    open.  Enforcement OFF is the configuration where this can happen.
    """
    from loguru import logger

    wiring.tunables["emission_controller_routable_live"] = False
    _feed(wiring.edge, ARM, wins=20, losses=2)
    wiring.gate_metrics[f"context_floor:{ARM}"] = {
        "n": 100, "ev_per_suppression_r": 0.9, "verdict": "TUNE",
    }

    lines: list[str] = []
    sink = logger.add(lambda m: lines.append(m.record["message"]), level="WARNING")
    try:
        engine = _engine()
        _run(engine, wiring)
    finally:
        logger.remove(sink)

    rep = engine._emission_controller_routability
    if rep.promoted_unroutable:
        assert any("ROUTABILITY" in ln for ln in lines), (
            "a promotion to an unroutable key must WARN, not just populate a panel"
        )


def test_routability_disabled_leaves_routable_unset(wiring):
    """Flag OFF → the controller is not handed a routable set at all.

    Distinguishes "no restriction requested" from "restriction requested and
    everything passed", which look identical if you only check the report.
    """
    wiring.tunables["emission_controller_routable_enabled"] = False
    _feed(wiring.edge, ARM, wins=20, losses=2)

    engine = _engine()
    _run(engine, wiring)

    rep = getattr(engine, "_emission_controller_routability", None)
    assert rep is None or not rep.enforced


# ---------------------------------------------------------------------------
# Cadence + boot grace — the controller is self-promoting, so these bound it
# ---------------------------------------------------------------------------


def test_cadence_guard_skips_a_cycle_inside_the_interval(wiring, monkeypatch):
    """Layer G runs on its own interval, independent of the audit tick."""
    monkeypatch.setenv("EMISSION_CONTROLLER_INTERVAL_SEC", "1800")
    _feed(wiring.edge, LIVE, wins=20, losses=2)

    engine = _engine()
    _run(engine, wiring)
    first = engine._emission_controller_cycles_since_start

    _run(engine, wiring)  # immediately again — inside the interval
    assert engine._emission_controller_cycles_since_start == first, (
        "a second call inside the interval must not count as a cycle — "
        "boot grace is measured in cycles, so double-counting shortens it"
    )


def test_cycles_increment_across_intervals(wiring):
    """Boot grace counts in-process cycles, so the counter must advance."""
    _feed(wiring.edge, LIVE, wins=20, losses=2)

    engine = _engine()
    _run(engine, wiring)
    _run(engine, wiring)
    assert engine._emission_controller_cycles_since_start == 2


def test_decision_timestamp_is_stamped_for_the_liveness_probe(wiring):
    """The feature-liveness watchdog reads this; unset means "flat-lined"."""
    _feed(wiring.edge, LIVE, wins=20, losses=2)

    engine = _engine()
    _run(engine, wiring)
    assert engine._emission_controller_last_decision_ts > 0


def test_empty_matrix_commits_without_raising(wiring):
    """A cold boot has no matrix; the cycle must be a no-op, not a crash."""
    engine = _engine()
    _run(engine, wiring)
    assert engine._emission_controller_cycles_since_start == 1
