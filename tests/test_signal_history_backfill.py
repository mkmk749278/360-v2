"""Tests for ``src.signal_history_backfill``.

Backfill reconstructs ``_signal_history`` from the engine's pre-existing
durable record sources (``signal_performance.json`` +
``invalidation_records.json``).  The test surface covers:

* PerformanceTracker → Signal mapping (status, timestamps, fields)
* InvalidationRecord → Signal mapping (INVALIDATED status, kill_price)
* De-duplication when a signal_id appears in both files
* Cap respected (no more than HISTORY_CAP records)
* Sort order — most recent first
* Defensive: missing files, malformed records, corrupt JSON
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from datetime import datetime, timezone

from src.channels.base import Signal
from src.signal_history_backfill import (
    backfill_from_legacy_sources,
    reconcile_invalidation_status,
    reconcile_missing_tps,
)
from src.signal_history_store import HISTORY_CAP
from src.smc import Direction


def _perf_record(
    *,
    signal_id: str = "PERF-001",
    symbol: str = "BTCUSDT",
    direction: str = "LONG",
    entry: float = 30000.0,
    stop_loss: float = 29850.0,
    tp1: float = 30450.0,
    hit_tp: int = 1,
    hit_sl: bool = False,
    pnl_pct: float = 0.50,
    setup_class: str = "SR_FLIP_RETEST",
    quality_tier: str = "B",
    confidence: float = 75.0,
    create_timestamp: float = 1714900000.0,
    dispatch_timestamp: float = 1714900005.0,
    terminal_outcome_timestamp: float = 1714903605.0,
    outcome_label: str = "",
    channel: str = "360_SCALP",
) -> dict:
    return {
        "signal_id": signal_id,
        "channel": channel,
        "symbol": symbol,
        "direction": direction,
        "entry": entry,
        "stop_loss": stop_loss,
        "tp1": tp1,
        "hit_tp": hit_tp,
        "hit_sl": hit_sl,
        "pnl_pct": pnl_pct,
        "setup_class": setup_class,
        "quality_tier": quality_tier,
        "confidence": confidence,
        "create_timestamp": create_timestamp,
        "dispatch_timestamp": dispatch_timestamp,
        "terminal_outcome_timestamp": terminal_outcome_timestamp,
        "outcome_label": outcome_label,
    }


def _inval_record(
    *,
    signal_id: str = "INVAL-001",
    symbol: str = "ETHUSDT",
    direction: str = "LONG",
    entry: float = 2370.0,
    stop_loss: float = 2351.0,
    tp1: float = 2392.0,
    kill_price: float = 2360.0,
    pnl_pct_at_kill: float = -0.42,
    setup_class: str = "FAILED_AUCTION_RECLAIM",
    kill_timestamp: float = 1714905000.0,
    kill_reason: str = "momentum_loss",
    channel: str = "360_SCALP",
) -> dict:
    return {
        "signal_id": signal_id,
        "channel": channel,
        "symbol": symbol,
        "direction": direction,
        "entry": entry,
        "stop_loss": stop_loss,
        "tp1": tp1,
        "kill_price": kill_price,
        "pnl_pct_at_kill": pnl_pct_at_kill,
        "setup_class": setup_class,
        "kill_timestamp": kill_timestamp,
        "kill_reason": kill_reason,
    }


def _write(path: Path, records: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records), encoding="utf-8")


# ---------------------------------------------------------------------------
# Empty / missing source files
# ---------------------------------------------------------------------------


def test_no_sources_returns_empty(tmp_path: Path) -> None:
    out = backfill_from_legacy_sources(
        perf_path=str(tmp_path / "perf.json"),
        invalidation_path=str(tmp_path / "inval.json"),
    )
    assert out == []


def test_empty_files_return_empty(tmp_path: Path) -> None:
    perf = tmp_path / "perf.json"
    inval = tmp_path / "inval.json"
    _write(perf, [])
    _write(inval, [])
    assert backfill_from_legacy_sources(
        perf_path=str(perf), invalidation_path=str(inval)
    ) == []


# ---------------------------------------------------------------------------
# Performance tracker → Signal mapping
# ---------------------------------------------------------------------------


def test_perf_record_mapped_to_signal(tmp_path: Path) -> None:
    perf = tmp_path / "perf.json"
    inval = tmp_path / "inval.json"
    _write(perf, [_perf_record(signal_id="P-1", hit_tp=1)])
    _write(inval, [])
    out = backfill_from_legacy_sources(
        perf_path=str(perf), invalidation_path=str(inval)
    )
    assert len(out) == 1
    sig = out[0]
    assert sig.signal_id == "P-1"
    assert sig.symbol == "BTCUSDT"
    assert sig.direction == Direction.LONG
    assert sig.entry == 30000.0
    assert sig.stop_loss == 29850.0
    assert sig.tp1 == 30450.0
    assert sig.status == "TP1_HIT"
    assert sig.setup_class == "SR_FLIP_RETEST"


@pytest.mark.parametrize(
    "hit_tp,hit_sl,expected_status",
    [
        (3, False, "FULL_TP_HIT"),
        (2, False, "TP2_HIT"),
        (1, False, "TP1_HIT"),
        (0, True, "SL_HIT"),
        (0, False, "CLOSED"),
    ],
)
def test_perf_status_classification(
    tmp_path: Path, hit_tp: int, hit_sl: bool, expected_status: str,
) -> None:
    perf = tmp_path / "perf.json"
    _write(perf, [_perf_record(hit_tp=hit_tp, hit_sl=hit_sl)])
    out = backfill_from_legacy_sources(
        perf_path=str(perf), invalidation_path=str(tmp_path / "inval.json"),
    )
    assert out[0].status == expected_status


def test_perf_explicit_outcome_label_wins_over_inferred(tmp_path: Path) -> None:
    """If perf_tracker stamped an outcome_label (e.g. 'BREAKEVEN_EXIT'), use it."""
    perf = tmp_path / "perf.json"
    _write(perf, [_perf_record(hit_sl=True, outcome_label="BREAKEVEN_EXIT")])
    out = backfill_from_legacy_sources(
        perf_path=str(perf), invalidation_path=str(tmp_path / "inval.json"),
    )
    assert out[0].status == "BREAKEVEN_EXIT"


def test_perf_short_direction(tmp_path: Path) -> None:
    perf = tmp_path / "perf.json"
    _write(perf, [_perf_record(direction="SHORT")])
    out = backfill_from_legacy_sources(
        perf_path=str(perf), invalidation_path=str(tmp_path / "inval.json"),
    )
    assert out[0].direction == Direction.SHORT


def test_perf_invalid_record_skipped(tmp_path: Path) -> None:
    """Missing signal_id, missing symbol, or zero entry → skip silently."""
    perf = tmp_path / "perf.json"
    _write(perf, [
        {"signal_id": ""},          # blank id
        {"symbol": "X"},            # missing id
        _perf_record(entry=0.0),    # zero entry
        _perf_record(signal_id="GOOD"),
    ])
    out = backfill_from_legacy_sources(
        perf_path=str(perf), invalidation_path=str(tmp_path / "inval.json"),
    )
    assert len(out) == 1
    assert out[0].signal_id == "GOOD"


# ---------------------------------------------------------------------------
# Invalidation record → Signal mapping
# ---------------------------------------------------------------------------


def test_invalidation_record_mapped_to_signal(tmp_path: Path) -> None:
    inval = tmp_path / "inval.json"
    _write(inval, [_inval_record(signal_id="I-1")])
    out = backfill_from_legacy_sources(
        perf_path=str(tmp_path / "perf.json"), invalidation_path=str(inval),
    )
    assert len(out) == 1
    sig = out[0]
    assert sig.signal_id == "I-1"
    assert sig.status == "INVALIDATED"
    assert sig.current_price == 2360.0  # kill_price
    assert sig.pnl_pct == pytest.approx(-0.42)
    assert sig.setup_class == "FAILED_AUCTION_RECLAIM"


# ---------------------------------------------------------------------------
# De-duplication: perf wins over invalidation on same signal_id
# ---------------------------------------------------------------------------


def test_dedupe_perf_wins_over_invalidation(tmp_path: Path) -> None:
    """Same signal_id in both files → keep the richer perf record (the
    closed signal eventually got classified by perf-tracker too)."""
    perf = tmp_path / "perf.json"
    inval = tmp_path / "inval.json"
    _write(perf, [_perf_record(
        signal_id="DUP-1", hit_tp=0, hit_sl=False,
        outcome_label="INVALIDATED",
        confidence=82.5,
    )])
    _write(inval, [_inval_record(signal_id="DUP-1")])
    out = backfill_from_legacy_sources(
        perf_path=str(perf), invalidation_path=str(inval),
    )
    assert len(out) == 1
    assert out[0].confidence == 82.5  # confidence is perf-only — confirms perf won


# ---------------------------------------------------------------------------
# Cap + sort
# ---------------------------------------------------------------------------


def test_capped_at_history_cap(tmp_path: Path) -> None:
    perf = tmp_path / "perf.json"
    over_cap = HISTORY_CAP + 25
    records = [
        _perf_record(signal_id=f"P-{i:04d}", terminal_outcome_timestamp=1714900000 + i)
        for i in range(over_cap)
    ]
    _write(perf, records)
    out = backfill_from_legacy_sources(
        perf_path=str(perf), invalidation_path=str(tmp_path / "inval.json"),
    )
    assert len(out) == HISTORY_CAP


def test_sorted_most_recent_first(tmp_path: Path) -> None:
    perf = tmp_path / "perf.json"
    _write(perf, [
        _perf_record(signal_id="OLD", create_timestamp=1714000000.0),
        _perf_record(signal_id="NEW", create_timestamp=1715000000.0),
        _perf_record(signal_id="MID", create_timestamp=1714500000.0),
    ])
    out = backfill_from_legacy_sources(
        perf_path=str(perf), invalidation_path=str(tmp_path / "inval.json"),
    )
    ids = [s.signal_id for s in out]
    assert ids == ["NEW", "MID", "OLD"]


# ---------------------------------------------------------------------------
# Defensive: corrupt files
# ---------------------------------------------------------------------------


def test_corrupt_perf_json_yields_empty(tmp_path: Path) -> None:
    perf = tmp_path / "perf.json"
    perf.write_text("{ this is not valid json", encoding="utf-8")
    out = backfill_from_legacy_sources(
        perf_path=str(perf), invalidation_path=str(tmp_path / "inval.json"),
    )
    assert out == []


def test_non_list_root_yields_empty(tmp_path: Path) -> None:
    perf = tmp_path / "perf.json"
    perf.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
    out = backfill_from_legacy_sources(
        perf_path=str(perf), invalidation_path=str(tmp_path / "inval.json"),
    )
    assert out == []


def test_mixed_valid_and_garbage_keeps_valid(tmp_path: Path) -> None:
    """A garbage entry alongside valid ones should not poison the whole
    backfill — emit warnings for the bad rows, keep the good."""
    perf = tmp_path / "perf.json"
    _write(perf, [
        "not a dict",
        {"truncated": True},
        _perf_record(signal_id="GOOD-1"),
        42,
        _perf_record(signal_id="GOOD-2"),
    ])
    out = backfill_from_legacy_sources(
        perf_path=str(perf), invalidation_path=str(tmp_path / "inval.json"),
    )
    ids = sorted(s.signal_id for s in out)
    assert ids == ["GOOD-1", "GOOD-2"]


# ---------------------------------------------------------------------------
# Combined sources
# ---------------------------------------------------------------------------


def test_combined_sources_merge_correctly(tmp_path: Path) -> None:
    perf = tmp_path / "perf.json"
    inval = tmp_path / "inval.json"
    _write(perf, [
        _perf_record(signal_id="P-1", hit_tp=1, create_timestamp=1714900000.0),
        _perf_record(signal_id="P-2", hit_sl=True, create_timestamp=1714905000.0),
    ])
    _write(inval, [
        _inval_record(signal_id="I-1", kill_timestamp=1714902500.0),
    ])
    out = backfill_from_legacy_sources(
        perf_path=str(perf), invalidation_path=str(inval),
    )
    by_id = {s.signal_id: s for s in out}
    assert set(by_id) == {"P-1", "P-2", "I-1"}
    assert by_id["I-1"].status == "INVALIDATED"
    assert by_id["P-1"].status == "TP1_HIT"
    assert by_id["P-2"].status == "SL_HIT"
    # Sorted by timestamp DESC: P-2 (1714905000) > I-1 (1714902500) > P-1 (1714900000)
    assert [s.signal_id for s in out] == ["P-2", "I-1", "P-1"]


# ---------------------------------------------------------------------------
# reconcile_invalidation_status — repair wrongly-labelled persisted history
# ---------------------------------------------------------------------------


def _make_signal_for_reconcile(
    *,
    signal_id: str,
    status: str = "CLOSED",
    current_price: float = 0.0,
    pnl_pct: float = 0.0,
    terminal_outcome_timestamp: datetime | None = None,
) -> Signal:
    """Construct a Signal directly for reconcile-test purposes."""
    sig = Signal(
        channel="360_SCALP",
        symbol="ETHUSDT",
        direction=Direction.LONG,
        entry=2370.0,
        stop_loss=2351.0,
        tp1=2392.0,
        tp2=2416.0,
        tp3=2436.0,
        signal_id=signal_id,
        timestamp=datetime(2026, 5, 5, 10, 0, 0, tzinfo=timezone.utc),
    )
    sig.status = status
    sig.current_price = current_price
    sig.pnl_pct = pnl_pct
    if terminal_outcome_timestamp is not None:
        sig.terminal_outcome_timestamp = terminal_outcome_timestamp
    return sig


def test_reconcile_no_invalidation_records_returns_zero(tmp_path) -> None:
    history = [_make_signal_for_reconcile(signal_id="X-1")]
    fixed = reconcile_invalidation_status(
        history, invalidation_path=str(tmp_path / "missing.json"),
    )
    assert fixed == 0
    assert history[0].status == "CLOSED"  # untouched


def test_reconcile_fixes_closed_to_invalidated(tmp_path) -> None:
    """The doctrinal core: a "CLOSED"-labelled signal whose ID lives in
    the invalidation audit gets corrected to "INVALIDATED" with the
    kill_price + kill_timestamp + pnl_pct_at_kill all synced."""
    inval = tmp_path / "inval.json"
    _write(inval, [_inval_record(
        signal_id="WRONG-1",
        kill_price=2360.0,
        kill_timestamp=1714905000.0,
        pnl_pct_at_kill=-0.42,
    )])
    sig = _make_signal_for_reconcile(
        signal_id="WRONG-1",
        status="CLOSED",
        pnl_pct=0.0,
    )
    history = [sig]

    fixed = reconcile_invalidation_status(
        history, invalidation_path=str(inval),
    )

    assert fixed == 1
    assert sig.status == "INVALIDATED"
    assert sig.current_price == pytest.approx(2360.0)
    assert sig.pnl_pct == pytest.approx(-0.42)
    assert sig.terminal_outcome_timestamp is not None


def test_reconcile_skips_already_invalidated(tmp_path) -> None:
    """No-op when status is already correct — defensive against double-flush."""
    inval = tmp_path / "inval.json"
    _write(inval, [_inval_record(signal_id="OK-1", kill_price=2360.0)])
    sig = _make_signal_for_reconcile(
        signal_id="OK-1",
        status="INVALIDATED",
        current_price=2360.0,  # already correct
    )

    fixed = reconcile_invalidation_status(
        [sig], invalidation_path=str(inval),
    )
    assert fixed == 0


def test_reconcile_leaves_non_invalidated_signals_alone(tmp_path) -> None:
    """A signal NOT in the invalidation audit (e.g. SL hit, TP1 hit) must not
    be touched even if its status looks wrong to the reconciler."""
    inval = tmp_path / "inval.json"
    _write(inval, [_inval_record(signal_id="WAS-INVAL")])
    sl_sig = _make_signal_for_reconcile(signal_id="WAS-SL", status="SL_HIT")
    tp_sig = _make_signal_for_reconcile(signal_id="WAS-TP", status="TP1_HIT")
    history = [sl_sig, tp_sig]

    fixed = reconcile_invalidation_status(
        history, invalidation_path=str(inval),
    )
    assert fixed == 0
    assert sl_sig.status == "SL_HIT"
    assert tp_sig.status == "TP1_HIT"


def test_reconcile_idempotent_across_repeat_calls(tmp_path) -> None:
    """First call fixes; second call on the same history is a no-op."""
    inval = tmp_path / "inval.json"
    _write(inval, [_inval_record(signal_id="X-1", kill_price=2360.0)])
    sig = _make_signal_for_reconcile(signal_id="X-1", status="CLOSED")
    history = [sig]

    first = reconcile_invalidation_status(history, invalidation_path=str(inval))
    second = reconcile_invalidation_status(history, invalidation_path=str(inval))

    assert first == 1
    assert second == 0
    assert sig.status == "INVALIDATED"


def test_reconcile_handles_breakeven_exit_label(tmp_path) -> None:
    """The breakeven-labelled invalidations (hit_sl=True near zero pnl)
    that classify_trade_outcome would mark BREAKEVEN_EXIT should still
    be repaired when the audit log has them as invalidations."""
    inval = tmp_path / "inval.json"
    _write(inval, [_inval_record(signal_id="BE-1", kill_price=2370.0)])
    sig = _make_signal_for_reconcile(signal_id="BE-1", status="BREAKEVEN_EXIT")
    fixed = reconcile_invalidation_status([sig], invalidation_path=str(inval))
    assert fixed == 1
    assert sig.status == "INVALIDATED"


def test_reconcile_robust_to_malformed_invalidation_records(tmp_path) -> None:
    inval = tmp_path / "inval.json"
    _write(inval, [
        "not a dict",
        {},                                   # no signal_id
        {"signal_id": ""},                    # blank signal_id
        _inval_record(signal_id="GOOD"),
    ])
    sig = _make_signal_for_reconcile(signal_id="GOOD", status="CLOSED")
    fixed = reconcile_invalidation_status([sig], invalidation_path=str(inval))
    assert fixed == 1
    assert sig.status == "INVALIDATED"


def test_reconcile_updates_only_provided_fields(tmp_path) -> None:
    """When invalidation record is missing kill_price / pnl, leave those
    fields on the sig as-is — only flip the status."""
    inval = tmp_path / "inval.json"
    # Record with kill_timestamp only — no kill_price or pnl
    record = _inval_record(signal_id="PARTIAL")
    record.pop("kill_price", None)
    record.pop("pnl_pct_at_kill", None)
    _write(inval, [record])

    sig = _make_signal_for_reconcile(
        signal_id="PARTIAL",
        status="CLOSED",
        current_price=99.0,  # would-be stale value
        pnl_pct=42.0,
    )
    fixed = reconcile_invalidation_status([sig], invalidation_path=str(inval))
    assert fixed == 1
    assert sig.status == "INVALIDATED"
    # Nothing to override → keep what was there
    assert sig.current_price == pytest.approx(99.0)
    assert sig.pnl_pct == pytest.approx(42.0)


# ---------------------------------------------------------------------------
# reconcile_missing_tps — patch TP2/TP3 from dispatch_log.json
# ---------------------------------------------------------------------------


def _dispatch_record(
    *,
    signal_id: str,
    entry: float = 100.0,
    sl: float = 99.0,
    tp1: float = 101.0,
    tp2: float = 102.0,
    tp3: float = 103.0,
) -> dict:
    return {
        "dispatched_at": 1700000000.0,
        "signal_id": signal_id,
        "channel": "360_SCALP",
        "symbol": "BTCUSDT",
        "direction": "LONG",
        "entry": entry,
        "sl": sl,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
    }


def test_backfill_uses_dispatch_log_to_fill_tp2_tp3(tmp_path: Path) -> None:
    """A perf record without TP2/TP3 should pick them up from dispatch_log."""
    perf = tmp_path / "perf.json"
    inval = tmp_path / "inval.json"
    dispatch = tmp_path / "dispatch.json"
    _write(perf, [_perf_record(signal_id="WITH-DISPATCH", tp1=101.0)])
    _write(dispatch, [_dispatch_record(
        signal_id="WITH-DISPATCH", tp1=101.5, tp2=103.0, tp3=105.5,
    )])

    out = backfill_from_legacy_sources(
        perf_path=str(perf),
        invalidation_path=str(inval),
        dispatch_path=str(dispatch),
    )
    assert len(out) == 1
    sig = out[0]
    # Perf carried tp1, dispatch fills tp2/tp3.
    assert sig.tp1 == pytest.approx(101.0)
    assert sig.tp2 == pytest.approx(103.0)
    assert sig.tp3 == pytest.approx(105.5)


def test_backfill_dispatch_fills_missing_tp1_too(tmp_path: Path) -> None:
    """When perf record has tp1=0 but dispatch has the real tp1, use dispatch."""
    perf = tmp_path / "perf.json"
    dispatch = tmp_path / "dispatch.json"
    record = _perf_record(signal_id="ZERO-TP1")
    record["tp1"] = 0.0
    _write(perf, [record])
    _write(dispatch, [_dispatch_record(
        signal_id="ZERO-TP1", tp1=101.0, tp2=102.0, tp3=104.0,
    )])

    out = backfill_from_legacy_sources(
        perf_path=str(perf),
        invalidation_path=str(tmp_path / "missing.json"),
        dispatch_path=str(dispatch),
    )
    assert len(out) == 1
    assert out[0].tp1 == pytest.approx(101.0)


def test_backfill_no_dispatch_log_keeps_old_behaviour(tmp_path: Path) -> None:
    """Absent dispatch log → tp2 stays 0, tp3 None.  No regression."""
    perf = tmp_path / "perf.json"
    _write(perf, [_perf_record(signal_id="NO-DISPATCH", tp1=101.0)])

    out = backfill_from_legacy_sources(
        perf_path=str(perf),
        invalidation_path=str(tmp_path / "missing.json"),
        dispatch_path=str(tmp_path / "missing-dispatch.json"),
    )
    assert len(out) == 1
    sig = out[0]
    assert sig.tp1 == pytest.approx(101.0)
    assert sig.tp2 == pytest.approx(0.0)
    assert sig.tp3 is None


def test_reconcile_missing_tps_patches_existing_history(tmp_path: Path) -> None:
    """An already-archived signal with tp2=0/tp3=None gets patched in place
    when its signal_id appears in dispatch_log."""
    dispatch = tmp_path / "dispatch.json"
    _write(dispatch, [_dispatch_record(
        signal_id="LEGACY-1", tp1=101.0, tp2=102.5, tp3=104.0,
    )])

    sig = _make_signal_for_reconcile(
        signal_id="LEGACY-1",
        status="CLOSED",
    )
    sig.tp1 = 101.0
    sig.tp2 = 0.0
    sig.tp3 = None

    fixed = reconcile_missing_tps([sig], dispatch_path=str(dispatch))
    assert fixed == 1
    assert sig.tp2 == pytest.approx(102.5)
    assert sig.tp3 == pytest.approx(104.0)


def test_reconcile_missing_tps_idempotent(tmp_path: Path) -> None:
    """Running reconcile twice mutates 0 the second time."""
    dispatch = tmp_path / "dispatch.json"
    _write(dispatch, [_dispatch_record(
        signal_id="ID-1", tp1=101.0, tp2=102.0, tp3=103.0,
    )])
    sig = _make_signal_for_reconcile(signal_id="ID-1", status="CLOSED")
    sig.tp1 = 101.0
    sig.tp2 = 0.0
    sig.tp3 = None

    first = reconcile_missing_tps([sig], dispatch_path=str(dispatch))
    second = reconcile_missing_tps([sig], dispatch_path=str(dispatch))
    assert first == 1
    assert second == 0


def test_reconcile_missing_tps_skips_already_populated(tmp_path: Path) -> None:
    """If TP2/TP3 are already real numbers, leave them alone."""
    dispatch = tmp_path / "dispatch.json"
    _write(dispatch, [_dispatch_record(
        signal_id="ALREADY-FULL", tp1=101.0, tp2=999.0, tp3=999.0,
    )])
    sig = _make_signal_for_reconcile(signal_id="ALREADY-FULL", status="CLOSED")
    sig.tp1 = 101.0
    sig.tp2 = 102.0  # populated, not 0
    sig.tp3 = 103.0  # populated, not None

    fixed = reconcile_missing_tps([sig], dispatch_path=str(dispatch))
    assert fixed == 0
    assert sig.tp2 == pytest.approx(102.0)
    assert sig.tp3 == pytest.approx(103.0)


def test_reconcile_missing_tps_ignores_unknown_signal_ids(tmp_path: Path) -> None:
    """A history signal not in dispatch_log is left as-is."""
    dispatch = tmp_path / "dispatch.json"
    _write(dispatch, [_dispatch_record(signal_id="ID-A")])
    sig = _make_signal_for_reconcile(signal_id="ID-B", status="CLOSED")
    sig.tp2 = 0.0
    sig.tp3 = None

    fixed = reconcile_missing_tps([sig], dispatch_path=str(dispatch))
    assert fixed == 0
    assert sig.tp2 == pytest.approx(0.0)
    assert sig.tp3 is None


def test_reconcile_missing_tps_no_dispatch_log_returns_zero(tmp_path: Path) -> None:
    """Absent dispatch log → no-op, no exception."""
    sig = _make_signal_for_reconcile(signal_id="X", status="CLOSED")
    fixed = reconcile_missing_tps(
        [sig], dispatch_path=str(tmp_path / "missing.json"),
    )
    assert fixed == 0
