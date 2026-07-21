"""Integration of Layer G into the emission policy + the controller store.

Pins the two hot-path-critical contracts:
  * the store's per-strategy override read is in-memory and round-trips to disk;
  * ``effective_floor`` honours the controller's per-strategy overrides — a
    strategy with suppress OFF stops suppressing its NEGATIVE cell, and a lowered
    per-strategy ``min_samples`` unlocks a thin-but-STRONG cell — while other
    strategies keep the global behaviour.
"""
from __future__ import annotations

from src.context_emission_policy import PolicyParams, effective_floor
from src.emission_controller import Adjustment, ControllerState, StrategyOverride
from src.emission_controller_store import EmissionControllerStore
from src.strategy_edge import StrategyEdgeStore, StrategyOutcome

CTX = "OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL"
BASE = 65.0


def _params(per_strategy=None) -> PolicyParams:
    return PolicyParams(
        enabled=True, live=True, quality_anchor=60.0, strong_relax=5.0,
        positive_relax=3.0, min_samples=30, suppress_negative=True,
        per_strategy=per_strategy or {},
    )


def _store() -> StrategyEdgeStore:
    return StrategyEdgeStore(persist_path="")


def _feed(store, strategy, ctx, wins, losses, *, source="emitted") -> None:
    for _ in range(wins):
        store.record(StrategyOutcome(strategy, ctx, "LONG", True, 1.0, 1.0, 2.0, source), persist=False)
    for _ in range(losses):
        store.record(StrategyOutcome(strategy, ctx, "LONG", False, -1.0, -1.0, 0.0, source), persist=False)


# ---- store -----------------------------------------------------------------


def test_store_override_read_and_persist_roundtrip(tmp_path):
    p = str(tmp_path / "ec.json")
    st = EmissionControllerStore(persist_path=p)
    assert st.override_for("MTP") == StrategyOverride()  # empty by default

    state = ControllerState(overrides={"MTP": StrategyOverride(suppress_negative=False, min_samples=25)})
    adj = Adjustment("MTP", "suppress_negative", True, False, applied=True,
                     status="PROMOTED", reason="x", verdict="DROP", ev_per_suppression_r=-0.4, n=100)
    st.commit(state, [adj])

    assert st.override_for("mtp").suppress_negative is False  # case-insensitive
    assert st.active_overrides() == {"MTP": {"suppress_negative": False, "min_samples": 25}}
    assert st.ledger()[-1]["applied"] is True

    # persisted + reloaded by a fresh instance
    st2 = EmissionControllerStore(persist_path=p)
    assert st2.override_for("MTP").min_samples == 25
    assert st2.ledger()[-1]["strategy"] == "MTP"


def test_store_shadow_pending_is_observable_and_persisted(tmp_path):
    import os
    p = str(tmp_path / "ec.json")
    st = EmissionControllerStore(persist_path=p)
    pend = Adjustment("MTP", "suppress_negative", True, False, applied=False,
                      status="PENDING", reason="boot_grace", verdict="DROP", ev_per_suppression_r=-0.4, n=100)
    st.commit(ControllerState(), [pend])
    # pending (would-be) candidates go to pending(), NOT the durable ledger
    assert st.ledger() == [] or all(x["applied"] for x in st.ledger())
    assert st.pending() and st.pending()[-1]["strategy"] == "MTP"
    assert st.pending()[-1]["applied"] is False
    # persisted every cycle (even with nothing applied) so the dark period is visible
    assert os.path.exists(p)
    reloaded = EmissionControllerStore(persist_path=p)
    assert reloaded.pending() and reloaded.pending()[-1]["strategy"] == "MTP"


def test_store_ledger_holds_only_applied_no_shadow_eviction(tmp_path):
    p = str(tmp_path / "ec.json")
    st = EmissionControllerStore(persist_path=p)
    applied = Adjustment("MTP", "suppress_negative", True, False, applied=True,
                         status="PROMOTED", reason="promote", verdict="DROP", ev_per_suppression_r=-0.4, n=100)
    st.commit(ControllerState(overrides={"MTP": StrategyOverride(suppress_negative=False)}), [applied])
    # many subsequent shadow-only cycles must NOT evict the real promotion
    for _ in range(300):
        pend = Adjustment("SRF", "suppress_negative", True, False, applied=False,
                          status="PENDING", reason="boot_grace", verdict="DROP", ev_per_suppression_r=-0.3, n=100)
        st.commit(st.state, [pend])
    led = st.ledger(limit=500)
    assert any(x["strategy"] == "MTP" and x["applied"] for x in led)  # promotion survived
    assert all(x["applied"] for x in led)                             # ledger is applied-only


# ---- policy honours per-strategy overrides ---------------------------------


def test_suppress_override_off_stops_suppressing_negative_cell():
    st = _store()
    _feed(st, "MOVER_TREND_PULLBACK", CTX, wins=2, losses=40)  # NEGATIVE cell
    # global suppress ON → suppressed
    d_global = effective_floor("MOVER_TREND_PULLBACK", CTX, BASE, store=st, params=_params())
    assert d_global.verdict == "NEGATIVE" and d_global.suppressed is True

    # controller override suppress OFF for this strategy → not suppressed
    over = {"MOVER_TREND_PULLBACK": {"suppress_negative": False, "min_samples": None}}
    d_over = effective_floor("MOVER_TREND_PULLBACK", CTX, BASE, store=st, params=_params(over))
    assert d_over.verdict == "NEGATIVE" and d_over.suppressed is False
    assert d_over.effective_floor == BASE  # falls through to the global floor


def test_min_samples_override_unlocks_thin_strong_cell():
    st = _store()
    _feed(st, "QUIET_COMPRESSION_BREAK", CTX, wins=25, losses=0)  # STRONG but n=25 < global 30
    # global min_samples 30 → thin, no relax
    d_global = effective_floor("QUIET_COMPRESSION_BREAK", CTX, BASE, store=st, params=_params())
    assert d_global.relaxed == 0.0 and "thin" in d_global.reason

    # controller lowered this strategy's floor to 20 → the n=25 cell now relaxes
    over = {"QUIET_COMPRESSION_BREAK": {"suppress_negative": None, "min_samples": 20}}
    d_over = effective_floor("QUIET_COMPRESSION_BREAK", CTX, BASE, store=st, params=_params(over))
    assert d_over.verdict == "STRONG" and d_over.relaxed > 0.0


def test_override_is_scoped_to_its_strategy():
    st = _store()
    _feed(st, "MOVER_TREND_PULLBACK", CTX, wins=2, losses=40)
    _feed(st, "SR_FLIP_RETEST", CTX, wins=2, losses=40)
    # only MTP is loosened; SR_FLIP keeps the global suppress
    over = {"MOVER_TREND_PULLBACK": {"suppress_negative": False}}
    p = _params(over)
    assert effective_floor("MOVER_TREND_PULLBACK", CTX, BASE, store=st, params=p).suppressed is False
    assert effective_floor("SR_FLIP_RETEST", CTX, BASE, store=st, params=p).suppressed is True
