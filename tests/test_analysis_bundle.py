"""Tests for the monitor-logs analysis-bundle builders (src/analysis_bundle.py).

Exercises the pure builders on plain dicts — no I/O — and pins the two
contracts that matter: the per-setup outcome classification stays in lock-step
with the ops Performance page, and the flattened matrix / CSV shape is stable
and deterministic.
"""
from __future__ import annotations

import csv
import io

from src.analysis_bundle import (
    PERFORMANCE_SETUP_COLUMNS,
    STRATEGY_MATRIX_COLUMNS,
    aggregate_performance_by_setup,
    build_bundle_index,
    flatten_strategy_matrix,
    rows_to_csv,
)


def _matrix() -> dict:
    return {
        "MOVER_TREND_PULLBACK|NY/VOLATILE/EXPANDED/BTC_NEUTRAL": {
            "strategy": "MOVER_TREND_PULLBACK",
            "context_key": "NY/VOLATILE/EXPANDED/BTC_NEUTRAL",
            "n": 30,
            "n_emitted": 5,
            "n_suppressed": 25,
            "n_shadow": 0,
            "win_rate": 0.6,
            "avg_pnl_pct": 0.17,
            "avg_r": 0.2,
            "mfe_capture": 0.4,
            "edge_r": 1.27,
            "verdict": "STRONG",
            "last_updated": "2026-07-20T06:00:00+00:00",
        },
        "SR_FLIP_RETEST|LONDON/MARKDOWN/EXPANDED/BTC_FALLING": {
            "strategy": "SR_FLIP_RETEST",
            "context_key": "LONDON/MARKDOWN/EXPANDED/BTC_FALLING",
            "n": 12,
            "n_emitted": 0,
            "n_suppressed": 12,
            "n_shadow": 0,
            "win_rate": 0.25,
            "avg_pnl_pct": -0.06,
            "avg_r": -1.0,
            "mfe_capture": 0.0,
            "edge_r": None,  # below sample floor — must stay None, not 0.0
            "verdict": "",
            "last_updated": "2026-07-20T05:00:00+00:00",
        },
        "SR_FLIP_RETEST|LONDON/VOL_EXP/CASCADE/BTC_NEUTRAL": {
            "strategy": "SR_FLIP_RETEST",
            "context_key": "LONDON/VOL_EXP/CASCADE/BTC_NEUTRAL",
            "n": 40,
            "n_emitted": 1,
            "n_suppressed": 39,
            "n_shadow": 0,
            "win_rate": 0.5,
            "avg_pnl_pct": 0.1,
            "avg_r": 0.3,
            "mfe_capture": 0.5,
            "edge_r": 1.29,
            "verdict": "STRONG",
            "last_updated": "2026-07-20T04:00:00+00:00",
        },
    }


def test_flatten_matrix_sorts_by_strategy_then_edge_desc_scored_first():
    rows = flatten_strategy_matrix(_matrix())
    assert [(r["strategy"], r["context_key"]) for r in rows] == [
        ("MOVER_TREND_PULLBACK", "NY/VOLATILE/EXPANDED/BTC_NEUTRAL"),
        ("SR_FLIP_RETEST", "LONDON/VOL_EXP/CASCADE/BTC_NEUTRAL"),  # edge 1.29, scored
        ("SR_FLIP_RETEST", "LONDON/MARKDOWN/EXPANDED/BTC_FALLING"),  # unscored → last
    ]


def test_flatten_matrix_preserves_none_edge():
    rows = flatten_strategy_matrix(_matrix())
    unscored = next(r for r in rows if r["context_key"] == "LONDON/MARKDOWN/EXPANDED/BTC_FALLING")
    assert unscored["edge_r"] is None
    assert unscored["verdict"] == ""


def test_flatten_matrix_ignores_non_dict_cells():
    rows = flatten_strategy_matrix({"BAD|CTX": "not-a-dict", **_matrix()})
    assert len(rows) == 3


def test_performance_aggregation_matches_ops_classifier():
    records = [
        {"setup_class": "FAR", "status": "TP1_HIT", "pnl_pct": 1.0},
        {"setup_class": "FAR", "status": "SL_HIT", "pnl_pct": -0.66},
        {"setup_class": "FAR", "status": "PROFIT_LOCKED", "pnl_pct": 3.7},  # PROFIT → win
        {"setup_class": "FAR", "status": "CLOSED", "pnl_pct": -0.1},  # neutral
        {"setup_class": "FAR", "outcome_label": "BREAKEVEN_EXIT", "pnl_pct": 0.0},  # neutral
    ]
    rows = aggregate_performance_by_setup(records)
    assert len(rows) == 1
    far = rows[0]
    assert far == {
        "setup": "FAR",
        "n": 5,
        "wins": 2,  # TP1_HIT + PROFIT_LOCKED
        "losses": 1,  # SL_HIT
        "neutral": 2,  # CLOSED + BREAKEVEN_EXIT
        "win_rate_pct": 40.0,
        "avg_pnl_pct": round((1.0 - 0.66 + 3.7 - 0.1 + 0.0) / 5, 4),
    }


def test_performance_prefers_pnlpct_fallback_and_outcome_label():
    rows = aggregate_performance_by_setup(
        [{"setup_class": "X", "outcome_label": "FULL_TP_HIT", "pnlPct": 2.0}]
    )
    assert rows[0]["wins"] == 1
    assert rows[0]["avg_pnl_pct"] == 2.0


def test_performance_sorted_by_n_desc():
    records = (
        [{"setup_class": "A", "status": "TP1_HIT", "pnl_pct": 1}] * 2
        + [{"setup_class": "B", "status": "SL_HIT", "pnl_pct": -1}] * 5
    )
    rows = aggregate_performance_by_setup(records)
    assert [r["setup"] for r in rows] == ["B", "A"]


def test_rows_to_csv_none_becomes_empty_and_header_order_fixed():
    rows = flatten_strategy_matrix(_matrix())
    text = rows_to_csv(rows, STRATEGY_MATRIX_COLUMNS)
    parsed = list(csv.reader(io.StringIO(text)))
    assert parsed[0] == STRATEGY_MATRIX_COLUMNS
    # the unscored SR_FLIP row must render edge_r/mfe as empty cells, never "None"
    unscored = [r for r in parsed if r[1] == "LONDON/MARKDOWN/EXPANDED/BTC_FALLING"][0]
    edge_idx = STRATEGY_MATRIX_COLUMNS.index("edge_r")
    assert unscored[edge_idx] == ""


def test_performance_csv_columns():
    rows = aggregate_performance_by_setup([{"setup_class": "A", "status": "TP1_HIT", "pnl_pct": 1}])
    text = rows_to_csv(rows, PERFORMANCE_SETUP_COLUMNS)
    assert text.splitlines()[0] == ",".join(PERFORMANCE_SETUP_COLUMNS)


def test_bundle_index_rollup():
    matrix_rows = flatten_strategy_matrix(_matrix())
    perf_rows = aggregate_performance_by_setup(
        [{"setup_class": "FAR", "status": "TP1_HIT", "pnl_pct": 1.0}]
    )
    suppression_audit = {
        "by_gate": {
            "context_floor:MOVER_TREND_PULLBACK": {"verdict": "DROP", "ev_per_suppression_r": -0.76},
            "min_confidence": {"verdict": "KEEP", "ev_per_suppression_r": 0.64},
            "dispatch_cooldown": {"verdict": "DROP", "ev_per_suppression_r": -0.29},
            "level_still_in_play": {"verdict": "KEEP", "ev_per_suppression_r": 0.15},
        }
    }
    idx = build_bundle_index(
        generated_at_ts=1_784_000_000.0,
        lookback_hours=24,
        channel="360_SCALP",
        matrix_rows=matrix_rows,
        performance_rows=perf_rows,
        suppression_audit=suppression_audit,
        git_sha="abc123",
        artifacts=["analysis/strategy_lab_matrix.csv"],
    )
    assert idx["counts"]["strategy_matrix_cells"] == 3
    assert idx["counts"]["strategy_matrix_scored_cells"] == 2
    assert idx["counts"]["suppression_gates"] == 4
    assert idx["headlines"]["gate_verdict_counts"] == {"DROP": 2, "KEEP": 2}
    assert set(idx["headlines"]["drop_gates"]) == {
        "context_floor:MOVER_TREND_PULLBACK",
        "dispatch_cooldown",
    }
    # strongest cell is the +1.29R SR_FLIP scored cell
    assert idx["headlines"]["strongest_cells"][0]["edge_r"] == 1.29
    assert idx["git_sha"] == "abc123"
    assert idx["generated_at"].startswith("20")


def test_bundle_index_tolerates_missing_suppression():
    idx = build_bundle_index(
        generated_at_ts=1_784_000_000.0,
        lookback_hours=24,
        channel="360_SCALP",
        matrix_rows=[],
        performance_rows=[],
        suppression_audit={},
    )
    assert idx["counts"]["suppression_gates"] == 0
    assert idx["headlines"]["drop_gates"] == []
    assert idx["headlines"]["strongest_cells"] == []
