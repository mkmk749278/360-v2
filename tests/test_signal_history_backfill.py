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

from src.signal_history_backfill import (
    backfill_from_legacy_sources,
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
