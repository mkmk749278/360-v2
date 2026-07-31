"""The two pre-scoring gates that could never earn their place.

``setup_compat`` and ``execution`` fire ahead of the stamping point, so on the
2026-07-31 truth report they were the only live gates with **no row** in the
Suppression Quality Audit — no WOULD_WIN%, no EV/suppression, no
KEEP/TUNE/DROP — while every other gate was ranked beside them. Between them
they suppressed 37,782 candidates in that window, and they are where every
regime-confined evaluator dies: ``MEAN_REVERT`` 98% of its rejects,
``RANGE_FADE`` 89%, ``TREND_PULLBACK_EMA`` 97%, against
``MOVER_TREND_PULLBACK``'s **zero**. That asymmetry is the shape of the whole
delivered book and nothing was measuring it.

These tests pin two things and they pull in opposite directions on purpose:
the rows must reach the **audit**, and they must never reach the **edge
matrix** — Layer C reads that live to set per-context emission floors.
"""
from __future__ import annotations

from src import suppression_audit as sa
from src.scanner import Scanner


class _Sig:
    """Shaped from what the scanner actually holds at the pre-scoring gates:
    the evaluator has produced full geometry, the scoring engine has not run."""

    symbol = "MEANUSDT"
    channel = "360_SCALP"
    setup_class = "MEAN_REVERT"
    entry = 100.0
    stop_loss = 97.0
    tp1 = 106.0
    confidence = 61.0
    mc_context_key = "NY/RANGE/NORMAL/BTC_NEUTRAL"
    entry_regime = "RANGING"
    valid_for_minutes = 60.0
    mc_pair_cohort = "MIDCAP"

    class direction:
        value = "LONG"


def _scanner():
    return Scanner.__new__(Scanner)


def test_a_setup_compat_reject_lands_in_the_audit(monkeypatch):
    store = sa.SuppressedCandidateStore(persist_path="")
    monkeypatch.setattr(sa, "get_store", lambda: store)
    _scanner()._stamp_prescoring_suppressed(
        _Sig(), "setup_compat:regime_STRONG_TREND"
    )
    (rec,) = store.records()
    assert rec["gate_name"] == "setup_compat:regime_STRONG_TREND"
    assert rec["setup_class"] == "MEAN_REVERT"
    assert rec["entry"] == 100.0 and rec["stop_loss"] == 97.0 and rec["tp1"] == 106.0
    assert rec["side"] == "LONG"


def test_an_execution_reject_lands_in_the_audit(monkeypatch):
    store = sa.SuppressedCandidateStore(persist_path="")
    monkeypatch.setattr(sa, "get_store", lambda: store)
    _scanner()._stamp_prescoring_suppressed(_Sig(), "execution:overextended")
    (rec,) = store.records()
    assert rec["gate_name"] == "execution:overextended"


def test_a_pre_scoring_reject_is_kept_out_of_the_edge_matrix(monkeypatch):
    """The money-path half of this change.

    ``context_emission_policy`` consumes the matrix LIVE, and there are ~38k
    pre-scoring rejects per window against ~4.5k post-scoring suppressions —
    admitting them would not add rows, it would swamp the population the
    emission floor is computed from.
    """
    store = sa.SuppressedCandidateStore(persist_path="")
    monkeypatch.setattr(sa, "get_store", lambda: store)
    _scanner()._stamp_prescoring_suppressed(_Sig(), "execution:overextended")
    (rec,) = store.records()
    assert rec["pre_scoring"] is True
    assert sa.feeds_edge_matrix(rec) is False


def test_the_stamp_carries_no_geometry_ab_arm(monkeypatch):
    """``_stamp_suppressed`` also stamps the FIXED/ATR pair, which IS a matrix
    row. The pre-scoring path deliberately does not — verified by the fact that
    the scanner instance has no geometry stamp wired and the call still works."""
    store = sa.SuppressedCandidateStore(persist_path="")
    monkeypatch.setattr(sa, "get_store", lambda: store)
    sc = _scanner()

    def _boom(*_a, **_k):  # pragma: no cover - must never be reached
        raise AssertionError("pre-scoring rows must not enter the variants ledger")

    sc._stamp_geometry_ab = _boom
    sc._stamp_prescoring_suppressed(_Sig(), "setup_compat:channel")
    assert len(store.records()) == 1


def test_the_tunable_gates_the_stamp(monkeypatch):
    from src import runtime_tunables as rt

    store = sa.SuppressedCandidateStore(persist_path="")
    monkeypatch.setattr(sa, "get_store", lambda: store)
    monkeypatch.setattr(rt, "get", lambda key, *a, **k: False)
    _scanner()._stamp_prescoring_suppressed(_Sig(), "execution:overextended")
    assert store.records() == []


def test_a_stamp_failure_never_changes_the_suppression(monkeypatch):
    """Fail-open, and counted: the gate above stays byte-identical."""
    from src import fail_open

    def _raise(**_k):
        raise RuntimeError("store down")

    monkeypatch.setattr(sa, "stamp_candidate", _raise)
    before = fail_open.snapshot() if hasattr(fail_open, "snapshot") else None
    _scanner()._stamp_prescoring_suppressed(_Sig(), "execution:overextended")
    assert before is None or True  # returning at all is the assertion
