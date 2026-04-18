from __future__ import annotations

from src.runtime_truth_report import (
    build_lifecycle_summary,
    build_snapshot,
    classify_path,
    compare_windows,
    parse_path_funnel_from_logs,
)


def test_classify_path_non_generating_and_generated_but_gated() -> None:
    assert (
        classify_path(
            {
                "evaluator_attempted": 10,
                "evaluator_generated": 0,
                "generated": 0,
                "gated": 0,
                "emitted": 0,
            }
        )
        == "non-generating"
    )

    assert (
        classify_path(
            {
                "evaluator_attempted": 12,
                "evaluator_generated": 4,
                "generated": 2,
                "gated": 6,
                "emitted": 0,
            }
        )
        == "generated-but-gated"
    )


def test_build_lifecycle_summary_fast_failure_buckets() -> None:
    records = [
        {"create_to_first_breach_sec": 20, "create_to_terminal_sec": 170},
        {"create_to_first_breach_sec": 55, "create_to_terminal_sec": 181},
        {"create_to_first_breach_sec": 130, "create_to_terminal_sec": 260},
        {"create_to_first_breach_sec": 175, "create_to_terminal_sec": 210},
    ]
    summary = build_lifecycle_summary(records)

    assert summary["fast_failure_buckets"]["under_30s"]["count"] == 1
    assert summary["fast_failure_buckets"]["under_60s"]["count"] == 2
    assert summary["fast_failure_buckets"]["under_180s"]["count"] == 4
    assert summary["terminal_close_around_3m"]["count"] == 3


def test_compare_windows_quality_and_flow_deltas() -> None:
    current_paths = {
        "A": {"emitted": 5, "gated": 4, "evaluator_no_signal": 3},
        "B": {"emitted": 1, "gated": 2, "evaluator_no_signal": 1},
    }
    previous_paths = {
        "A": {"emitted": 2, "gated": 6, "evaluator_no_signal": 1},
    }

    current_lifecycle = {"fast_failure_buckets": {"under_180s": {"count": 6}}}
    previous_lifecycle = {"fast_failure_buckets": {"under_180s": {"count": 4}}}

    current_quality = {
        "A": {"closed": 6, "win_rate": 50.0, "average_pnl_pct": 0.5},
    }
    previous_quality = {
        "A": {"closed": 6, "win_rate": 35.0, "average_pnl_pct": -0.3},
    }

    comparison = compare_windows(
        current_paths,
        previous_paths,
        current_lifecycle,
        previous_lifecycle,
        current_quality,
        previous_quality,
    )

    assert comparison["emissions_delta"] == 4
    assert comparison["gating_delta"] == 0
    assert comparison["no_generation_delta"] == 3
    assert comparison["fast_failures_delta"] == 2
    assert comparison["quality_changes"]["A"]["win_rate_delta"] == 15.0


def test_build_snapshot_handles_missing_optional_data() -> None:
    now_ts = 1_000_000.0
    records = [
        {
            "timestamp": now_ts - 100,
            "channel": "360_SCALP",
            "symbol": "BTCUSDT",
            "setup_class": "SR_FLIP_RETEST",
            "outcome_label": "SL_HIT",
            "pnl_pct": -1.2,
        },
    ]

    snapshot, comparison = build_snapshot(
        channel="360_SCALP",
        lookback_hours=24,
        compare_previous_window=False,
        include_raw_json=False,
        symbol_filter="",
        setup_filter="",
        runtime_health={"running": True, "status": "running", "health": "healthy"},
        heartbeat_text="Heartbeat age: 300s",
        records=records,
        current_funnel={},
        previous_funnel={},
        now_ts=now_ts,
    )

    assert snapshot["runtime_health"]["overall"] == "stale"
    assert snapshot["path_funnel_truth"] == {}
    assert comparison == {"enabled": False}


def test_parse_path_funnel_from_logs_extracts_channel_only() -> None:
    logs = "\n".join(
        [
            "Path funnel (last 100 cycles): path={'evaluator_attempted:360_SCALP:scalp:EVAL::A': 3, 'emitted:360_SCALP:scalp:A': 1} channel={}",
            "Path funnel (last 100 cycles): path={'evaluator_attempted:360_SWING:other:B': 7} channel={}",
        ]
    )

    parsed = parse_path_funnel_from_logs(logs, "360_SCALP")

    assert parsed["evaluator_attempted:360_SCALP:scalp:EVAL::A"] == 3
    assert parsed["emitted:360_SCALP:scalp:A"] == 1
    assert "evaluator_attempted:360_SWING:other:B" not in parsed
