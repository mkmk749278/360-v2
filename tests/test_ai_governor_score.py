"""The scorecard — graded against records the REAL tracker wrote.

`docs/PLAN_AI_TRADE_GOVERNOR_V2.md` §7. These tests exist because a manual
thesis on four open signals was wrong on three of them and nothing in the repo
would have said so. The join that catches it already existed; what was missing
was anything calling it.

Two of this repo's rules shape the file:

* **Never hand-write a collaborator's return shape.** The join is driven against
  a real `PerformanceTracker`, writing a real file through its real serializer.
  A mock whose keys you chose asserts your assumption back at you and goes green
  over dead code — `classify_pending` and `zone_distance_atr` each cost a session
  to exactly that.
* **Verify a fix by reverting it.** The additive-schema test fails against a bare
  `!=` loader, and the no-blended-figure test fails the moment somebody adds the
  convenient key.
"""
from __future__ import annotations

import os
import tempfile
from typing import Any, Dict, List, Optional

import pytest

from src import ai_governor_ledger as led
from src import ai_governor_score as sc
from src.execution import ai_governor as gov


# ---------------------------------------------------------------------------
# Helpers — verdict rows are OURS, so they are built here; outcome records are
# the collaborator's, so they are driven through the real producer.
# ---------------------------------------------------------------------------


def _verdict(
    sid: str,
    action: str,
    *,
    choice: Optional[str] = None,
    tp_dist: Optional[float] = None,
    book_readable: bool = True,
    flow_readable: bool = True,
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "signal_id": sid,
        "action": action,
        "choice": choice,
        # Mirrors `Snapshot.blind_fraction`: the share of the two optional
        # context fields we could not read, so book-only-blind is 0.5 and not
        # 1.0. Computed rather than hardcoded, because a helper that invents its
        # own convention asserts that convention back at you.
        "unknown_frac": (0 if book_readable else 1) / 2.0 + (0 if flow_readable else 1) / 2.0,
        "book_readable": book_readable,
        "book_reason": "ok" if book_readable else "not_subscribed",
        "flow_readable": flow_readable,
        "flow_reason": "ok" if flow_readable else "not_subscribed",
        "snapshot": {"tp_candidates": [], "sl_candidates": []},
    }
    if choice and tp_dist is not None:
        row["snapshot"]["tp_candidates"] = [
            {"key": "tp_0", "kind": "current", "dist_pct": 9.0},
            {"key": choice, "kind": "swing", "dist_pct": tp_dist},
        ]
    return row


def _tracker_records(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Write outcomes through the REAL tracker and read them back off disk."""
    from src.performance_tracker import PerformanceTracker

    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "signal_performance.json")
        tracker = PerformanceTracker(storage_path=path)
        for r in rows:
            tracker.record_outcome(
                signal_id=r["signal_id"],
                channel="360_SCALP",
                symbol=r.get("symbol", "BULLAUSDT"),
                direction="LONG",
                entry=100.0,
                hit_tp=r.get("hit_tp", 0),
                hit_sl=r.get("hit_sl", False),
                pnl_pct=r["pnl_pct"],
                outcome_label=r.get("outcome_label", "TP1_HIT"),
                max_favorable_excursion_pct=r.get("mfe", 0.0),
                max_adverse_excursion_pct=r.get("mae", 0.0),
                sl_distance_pct_at_entry=r.get("sl_dist", 2.0),
            )
        sc.reset_cache()
        records, err = sc.load_records(path)
        assert err is None, err
        return records


@pytest.fixture(autouse=True)
def _clean_cache():
    sc.reset_cache()
    yield
    sc.reset_cache()


# ---------------------------------------------------------------------------
# The join, against the real producer
# ---------------------------------------------------------------------------


def test_join_reads_the_fields_the_real_tracker_actually_writes():
    """A fixture chooses a shape and then agrees with you about it."""
    records = _tracker_records([
        {"signal_id": "s1", "pnl_pct": 7.31, "mfe": 8.0, "sl_dist": 2.0},
    ])
    assert records[0]["signal_id"] == "s1"
    # The four fields the scorer depends on must survive the real serializer.
    assert records[0]["pnl_pct"] == pytest.approx(7.31)
    assert records[0]["max_favorable_excursion_pct"] == pytest.approx(8.0)
    assert records[0]["sl_distance_pct_at_entry"] == pytest.approx(2.0)
    assert "outcome_label" in records[0]


def test_coverage_names_open_signals_rather_than_dropping_them():
    records = _tracker_records([{"signal_id": "closed", "pnl_pct": 1.0}])
    out = sc.score([_verdict("closed", gov.MAINTAIN), _verdict("open", gov.MAINTAIN)], records)
    cov = out["coverage"]
    assert cov["theses"] == 2
    assert cov["joined"] == 1
    assert cov[sc.WHY_STILL_OPEN] == 1


# ---------------------------------------------------------------------------
# One thesis per signal
# ---------------------------------------------------------------------------


def test_a_chatty_signal_counts_once():
    """Scoring per row lets one signal outvote the rest — #816 at a scorecard."""
    rows = [_verdict("s1", gov.MAINTAIN) for _ in range(8)]
    theses = sc.thesis_per_signal(rows)
    assert len(theses) == 1
    assert theses["s1"]["n_verdicts"] == 8
    assert theses["s1"]["action"] == gov.MAINTAIN


def test_any_intervention_makes_the_signal_intervened():
    rows = [
        _verdict("s1", gov.MAINTAIN),
        _verdict("s1", "ADJUST_TP", choice="tp_1", tp_dist=1.0),
        _verdict("s1", gov.MAINTAIN),
    ]
    theses = sc.thesis_per_signal(rows)
    assert theses["s1"]["intervened"] is True
    assert theses["s1"]["action"] == "ADJUST_TP"


def test_flip_flop_is_its_own_state_not_evidence_for_either_arm():
    rows = [_verdict("s1", gov.MAINTAIN), _verdict("s1", "ADJUST_TP", choice="tp_1", tp_dist=1.0)]
    theses = sc.thesis_per_signal(rows)
    assert theses["s1"]["flip_flopped"] is True

    steady = sc.thesis_per_signal([_verdict("s2", gov.MAINTAIN)])
    assert steady["s2"]["flip_flopped"] is False


# ---------------------------------------------------------------------------
# The TP arm — the one the record can decide
# ---------------------------------------------------------------------------


def test_clipping_a_winner_scores_a_negative_delta():
    """The BULLA case, quantified.

    A +7.31% winner whose nearer target sat at +5.0% would have booked 5.0
    instead of 7.31 — the arm cost 2.31 points. If this test ever reads positive,
    the sign convention has inverted and every adoption reading with it.
    """
    records = _tracker_records([
        {"signal_id": "bulla", "pnl_pct": 7.31, "mfe": 7.5, "sl_dist": 2.0},
    ])
    out = sc.score([_verdict("bulla", "ADJUST_TP", choice="tp_2", tp_dist=5.0)], records)
    arm = out["arms"]["ADJUST_TP"]
    assert arm["decidable"] == 1
    assert arm["reached"] == 1
    assert arm["avg_delta_pct"] == pytest.approx(5.0 - 7.31, abs=1e-6)
    assert arm["avg_delta_pct"] < 0


def test_a_target_never_reached_scores_zero_and_that_is_a_measurement():
    """Nearer-only means an unreached target changes nothing — a real zero."""
    records = _tracker_records([
        {"signal_id": "s1", "pnl_pct": -1.11, "mfe": 0.09, "outcome_label": "SL_HIT"},
    ])
    out = sc.score([_verdict("s1", "ADJUST_TP", choice="tp_1", tp_dist=2.0)], records)
    arm = out["arms"]["ADJUST_TP"]
    assert arm["decidable"] == 1
    assert arm["reached"] == 0
    assert arm["unreached"] == 1
    assert arm["avg_delta_pct"] == pytest.approx(0.0)


def test_an_unstamped_excursion_is_refused_by_name_never_counted_as_unreached():
    """Unreached and unknown remove opposite ends of the distribution."""
    out = sc.score(
        [_verdict("s1", "ADJUST_TP", choice="tp_1", tp_dist=2.0)],
        [{"signal_id": "s1", "pnl_pct": 1.0, "max_favorable_excursion_pct": None}],
    )
    arm = out["arms"]["ADJUST_TP"]
    assert arm["decidable"] == 0
    assert arm["unreached"] == 0
    assert arm["undecidable"] == {sc.WHY_NO_MFE: 1}


def test_a_choice_outside_its_own_menu_is_refused():
    row = _verdict("s1", "ADJUST_TP", choice="tp_9")
    row["snapshot"]["tp_candidates"] = [{"key": "tp_1", "dist_pct": 1.0}]
    out = sc.score([row], [{"signal_id": "s1", "pnl_pct": 1.0, "max_favorable_excursion_pct": 5.0}])
    assert out["arms"]["ADJUST_TP"]["undecidable"] == {sc.WHY_CHOICE_UNRESOLVED: 1}


# ---------------------------------------------------------------------------
# What must NOT appear
# ---------------------------------------------------------------------------


def test_there_is_no_blended_cross_arm_figure():
    """One number over four arms moves with the undecidable fraction rather
    than with the mechanism. Assert the key does not exist."""
    records = _tracker_records([{"signal_id": "s1", "pnl_pct": 1.0, "mfe": 2.0}])
    out = sc.score([_verdict("s1", "ADJUST_TP", choice="tp_1", tp_dist=1.0)], records)
    forbidden = {"avg_delta_pct", "overall", "combined", "governor_edge", "total_delta_pct"}
    assert not (forbidden & set(out)), f"blended key at top level: {forbidden & set(out)}"
    assert not (forbidden & set(out["arms"])), "blended key beside the arms"


def test_dark_arms_render_as_counted_states_rather_than_absent():
    """A missing arm reads as one that never fired; those are opposite facts."""
    records = _tracker_records([{"signal_id": "s1", "pnl_pct": -1.0}])
    out = sc.score([_verdict("s1", "ADJUST_SL", choice="sl_1")], records)
    sl = out["arms"]["ADJUST_SL"]
    assert sl["n"] == 1
    assert sl["decidable"] == 0
    assert sl["undecidable"] == {sc.WHY_ARM_UNDECIDABLE: 1}
    assert "PANIC_CLOSE" in out["arms"], "an arm with no rows must still render"


def test_selection_is_labelled_as_selection_and_carries_both_populations():
    records = _tracker_records([
        {"signal_id": "touched", "pnl_pct": -2.0},
        {"signal_id": "left", "pnl_pct": 3.0},
    ])
    out = sc.score(
        [
            _verdict("touched", "ADJUST_TP", choice="tp_1", tp_dist=1.0),
            _verdict("left", gov.MAINTAIN),
        ],
        records,
    )
    sel = out["selection"]
    assert sel["intervened"]["n"] == 1
    assert sel["maintain_only"]["n"] == 1
    # The fee is charged to BOTH sides, or the cost of trading becomes an edge.
    assert sel["intervened"]["avg_pnl_pct"] != sel["intervened"]["net_avg_pnl_pct"]
    assert sel["maintain_only"]["avg_pnl_pct"] != sel["maintain_only"]["net_avg_pnl_pct"]
    assert "counterfactual" in out["shadow_note"].lower()


def test_a_row_with_no_pnl_is_counted_and_excluded_rather_than_clamped():
    out = sc.score(
        [_verdict("s1", gov.MAINTAIN)],
        [{"signal_id": "s1", "pnl_pct": None}],
    )
    book = out["selection"]["maintain_only"]
    assert book["n"] == 1 and book["n_pnl"] == 0 and book["no_pnl"] == 1
    assert book["avg_pnl_pct"] is None, "no readable PnL must be None, never 0.0"


# ---------------------------------------------------------------------------
# The record loader states its cause
# ---------------------------------------------------------------------------


def test_a_missing_record_file_is_named_not_silently_empty():
    with tempfile.TemporaryDirectory() as d:
        rows, err = sc.load_records(os.path.join(d, "nope.json"))
    assert rows == [] and err == "missing"


def test_an_unparseable_record_file_is_named_apart_from_a_missing_one():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "signal_performance.json")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("{not json")
        sc.reset_cache()
        rows, err = sc.load_records(path)
    assert rows == [] and err == "unreadable"


# ---------------------------------------------------------------------------
# The additive schema bump — this test fails against a bare `!=` loader
# ---------------------------------------------------------------------------


def test_schema_2_reads_schema_1_rows_through_the_real_serializer():
    """Schema 2 only ADDS the readability split, so schema-1 rows keep their
    standing. A loader that dropped them would delete the window on the first
    flush after deploy — 371 SAR rows, and the rule was already written down."""
    assert led.SCHEMA == 2
    assert 1 in led.ADDITIVE_FROM_SCHEMAS

    import json

    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "ai_governor_v1.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "schema": 1,
                    "written_at": 0.0,
                    "max_rows": 4000,
                    "evicted": 0,
                    "rows": [{"signal_id": "old-1", "action": gov.MAINTAIN, "unknown_frac": 0.5}],
                },
                fh,
            )
        ledger = led.GovernorLedger(path=path)
        ledger.load()
        assert ledger.count() == 1, "a schema-1 row must survive an additive bump"
        assert ledger.rows()[0]["signal_id"] == "old-1"


def test_a_newer_schema_is_still_refused():
    """Reading forward means guessing what a field we have never seen means."""
    import json

    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "ai_governor_v1.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"schema": led.SCHEMA + 1, "rows": [{"signal_id": "future"}]}, fh)
        ledger = led.GovernorLedger(path=path)
        ledger.load()
        assert ledger.count() == 0


# ---------------------------------------------------------------------------
# Blindness — the block v1 §3 specified and nothing published
# ---------------------------------------------------------------------------


def test_blindness_on_an_empty_ledger_reports_unmeasured_not_zero_percent():
    """A caller rendering 0% here would report a fully-informed lane on one
    that has never been asked anything."""
    led.reset_ledger(led.GovernorLedger(path=""))
    try:
        out = gov.blindness()
    finally:
        led.reset_ledger(None)
    assert out["rows"] == 0
    assert out["measured"] is False
    assert "avg_unknown_frac" not in out, "an unmeasured lane must publish no fraction"


def test_blindness_splits_book_from_flow_because_the_fixes_differ():
    ledger = led.GovernorLedger(path="")
    ledger.add(_verdict("s1", gov.MAINTAIN, book_readable=False, flow_readable=True))
    ledger.add(_verdict("s2", gov.MAINTAIN, book_readable=False, flow_readable=False))
    led.reset_ledger(ledger)
    try:
        out = gov.blindness()
    finally:
        led.reset_ledger(None)
    assert out["measured"] is True
    assert out["book_blind"] == 2
    assert out["flow_blind"] == 1
    assert out["book_reasons"] == {"not_subscribed": 2}
    assert out["fully_blind"] == 1, "only the row blind on BOTH is fully blind"


def test_rows_predating_the_split_are_counted_apart_not_read_as_readable():
    """A missing stamp is not a pass — the rows without one are exactly the
    rows the split cannot describe."""
    ledger = led.GovernorLedger(path="")
    ledger.add({"signal_id": "old", "action": gov.MAINTAIN, "unknown_frac": 1.0})
    ledger.add(_verdict("new", gov.MAINTAIN, book_readable=False))
    led.reset_ledger(ledger)
    try:
        out = gov.blindness()
    finally:
        led.reset_ledger(None)
    assert out["rows"] == 2
    assert out["rows_with_split"] == 1
    assert out["book_blind"] == 1, "the unstamped row must not be counted either way"


def test_snapshot_readability_names_the_reason_not_only_the_bool():
    """`not_subscribed` is a stream-budget decision and `stale` is an incident;
    a bare False cannot tell an operator which one they are looking at."""
    from src.execution import ai_governor_menu as menu
    from src.execution import ai_governor_snapshot as snap

    class _Sig:
        signal_id = "s1"
        symbol = "BULLAUSDT"
        direction = "LONG"
        entry = 100.0
        stop_loss = 98.0
        tp1 = 104.0
        setup_class = "MOVER_TREND_PULLBACK"
        entry_regime = "VOLATILE"
        original_sl_distance = 2.0

    built = snap.build_snapshot(
        signal=_Sig(),
        trigger_tf="15m",
        as_of_bar_ms=1,
        bars_since_entry=3,
        last_price=101.0,
        menu=menu.Menu(tp=(), sl=()),
        book_getter=None,
        flow_getter=None,
    )
    read = built.readability()
    assert read["book_readable"] is False
    assert read["book_reason"] == snap.WHY_NOT_SUBSCRIBED
    assert read["flow_reason"] == snap.WHY_NOT_SUBSCRIBED
    # The pooled figure stays for continuity rather than being replaced.
    assert built.blind_fraction() == pytest.approx(1.0)


def test_build_diag_does_not_carry_the_scorecard():
    """The light entry must not do the heavy entry's I/O.

    `build_diag` is the `extra` of `flush(force=True)` on the maintenance loop,
    so anything slow or raising there is charged to the ledger's HEARTBEAT, and
    it is the entry an operator hits during an incident. Neither reason is the
    one first given — the record parse was blamed for a 25s timeout that
    measurement later pinned on engine warm-up (0.145s for the parsing entry,
    0.001s for this one once settled). The property is worth pinning anyway;
    the story attached to it was not.
    """
    led.reset_ledger(led.GovernorLedger(path=""))
    try:
        diag = gov.build_diag()
    finally:
        led.reset_ledger(None)
    assert "scorecard" not in diag, "the record parse must not ride the light entry"
    for key in ("measure_enabled", "bounds", "health", "blindness"):
        assert key in diag


def test_build_diag_does_no_file_io_at_all(monkeypatch):
    """Pinned as a COUNT, not a review: reading the line tells you nothing,
    asserting the loader was never called tells you everything."""
    calls = []
    monkeypatch.setattr(sc, "load_records", lambda *a, **k: calls.append(1) or ([], None))
    led.reset_ledger(led.GovernorLedger(path=""))
    try:
        gov.build_diag()
    finally:
        led.reset_ledger(None)
    assert calls == [], "build_diag touched the closed-signal record"


def test_a_failing_scorecard_returns_a_named_error_rather_than_raising():
    """"The scorecard failed" and "the scorecard is empty" send a reader to
    different places, so the failure is a rendered state, never an exception."""
    monkey = led.GovernorLedger(path="")
    led.reset_ledger(monkey)
    try:
        import src.ai_governor_score as _sc
        real = _sc.build
        _sc.build = lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom"))
        try:
            out = gov.build_scorecard()
        finally:
            _sc.build = real
    finally:
        led.reset_ledger(None)
    assert "error" in out and "RuntimeError" in out["error"]
