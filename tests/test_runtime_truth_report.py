from __future__ import annotations

from src.runtime_truth_report import (
    build_lifecycle_summary,
    build_snapshot,
    classify_path,
    compare_windows,
    parse_channel_funnel_from_logs,
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
    assert "post_correction_window_delta" in comparison


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


def test_parse_path_funnel_from_logs_handles_stage_tokens_with_colons() -> None:
    stage_changed = "geometry:final_live:changed:360_SCALP:reclaim_retest:SR_FLIP_RETEST"
    stage_rejected = (
        "geometry:final_live:rejected_reason:risk_plan:360_SCALP:trend_following:TREND_PULLBACK_EMA"
    )
    logs = "\n".join(
        [
            f"Path funnel (last 100 cycles): path={{'{stage_changed}': 2, '{stage_rejected}': 1}} channel={{}}",
        ]
    )

    parsed = parse_path_funnel_from_logs(logs, "360_SCALP")

    assert parsed[stage_changed] == 2
    assert parsed[stage_rejected] == 1


def test_parse_channel_funnel_from_logs_extracts_dependency_metrics_for_channel() -> None:
    logs = "\n".join(
        [
            "Path funnel (last 100 cycles): path={} channel={'dependency_presence:360_SCALP:cvd:absent': 4, 'dependency_bucket:360_SCALP:cvd:none': 4, 'dependency_presence:360_SWING:cvd:present': 2}",
        ]
    )
    parsed = parse_channel_funnel_from_logs(logs, "360_SCALP")
    assert parsed["dependency_presence:360_SCALP:cvd:absent"] == 4
    assert parsed["dependency_bucket:360_SCALP:cvd:none"] == 4
    assert "dependency_presence:360_SWING:cvd:present" not in parsed


def test_build_snapshot_includes_post_correction_focus_geometry_and_timing() -> None:
    now_ts = 1_000_000.0
    records = [
        {
            "timestamp": now_ts - 80,
            "channel": "360_SCALP",
            "symbol": "BTCUSDT",
            "setup_class": "SR_FLIP_RETEST",
            "outcome_label": "SL_HIT",
            "pnl_pct": -0.9,
            "create_to_first_breach_sec": 55.0,
            "create_to_terminal_sec": 190.0,
        },
        {
            "timestamp": now_ts - 60,
            "channel": "360_SCALP",
            "symbol": "ETHUSDT",
            "setup_class": "SR_FLIP_RETEST",
            "outcome_label": "TP1_HIT",
            "pnl_pct": 0.7,
            "create_to_first_breach_sec": 75.0,
            "create_to_terminal_sec": 230.0,
        },
        {
            "timestamp": now_ts - 40,
            "channel": "360_SCALP",
            "symbol": "BTCUSDT",
            "setup_class": "TREND_PULLBACK_EMA",
            "outcome_label": "SL_HIT",
            "pnl_pct": -0.4,
            "create_to_first_breach_sec": 95.0,
            "create_to_terminal_sec": 260.0,
        },
    ]

    current_funnel = {
        "evaluator_attempted:360_SCALP:reclaim_retest:SR_FLIP_RETEST": 5,
        "generated:360_SCALP:reclaim_retest:SR_FLIP_RETEST": 3,
        "emitted:360_SCALP:reclaim_retest:SR_FLIP_RETEST": 2,
        "geometry:final_live:changed:360_SCALP:reclaim_retest:SR_FLIP_RETEST": 2,
        "geometry:final_live:rejected:360_SCALP:reclaim_retest:SR_FLIP_RETEST": 1,
        "geometry:final_live:rejected_reason:risk_plan:360_SCALP:reclaim_retest:SR_FLIP_RETEST": 1,
        "evaluator_attempted:360_SCALP:trend_following:TREND_PULLBACK_EMA": 4,
        "generated:360_SCALP:trend_following:TREND_PULLBACK_EMA": 2,
        "emitted:360_SCALP:trend_following:TREND_PULLBACK_EMA": 1,
        "geometry:final_live:preserved:360_SCALP:trend_following:TREND_PULLBACK_EMA": 2,
    }

    snapshot, _comparison = build_snapshot(
        channel="360_SCALP",
        lookback_hours=24,
        compare_previous_window=True,
        include_raw_json=False,
        symbol_filter="",
        setup_filter="",
        runtime_health={"running": True, "status": "running", "health": "healthy"},
        heartbeat_text="Heartbeat age: 10s",
        records=records,
        current_funnel=current_funnel,
        previous_funnel={},
        now_ts=now_ts,
    )

    sr_focus = snapshot["post_correction_focus"]["SR_FLIP_RETEST"]
    trend_focus = snapshot["post_correction_focus"]["TREND_PULLBACK_EMA"]
    assert sr_focus["geometry_final_changed"] == 2
    assert sr_focus["geometry_final_rejected"] == 1
    assert sr_focus["geometry_rejected_reasons"]["risk_plan"] == 1
    assert sr_focus["median_first_breach_sec"] == 65.0
    assert sr_focus["median_terminal_duration_sec"] == 210.0
    assert trend_focus["geometry_final_preserved"] == 2


def test_build_snapshot_classifies_dependency_missing_and_emits_readiness() -> None:
    now_ts = 1_000_000.0
    current_funnel = {
        "evaluator_attempted:360_SCALP:other:EVAL::FUNDING_EXTREME": 7,
        "evaluator_no_signal:360_SCALP:other:EVAL::FUNDING_EXTREME": 7,
        "evaluator_no_signal_reason:missing_funding_rate:360_SCALP:other:EVAL::FUNDING_EXTREME": 6,
        "dependency_missing:missing_funding_rate:360_SCALP:other:EVAL::FUNDING_EXTREME": 6,
    }
    current_channel_funnel = {
        "dependency_presence:360_SCALP:funding_rate:absent": 5,
        "dependency_bucket:360_SCALP:funding_rate:absent": 5,
    }
    snapshot, _ = build_snapshot(
        channel="360_SCALP",
        lookback_hours=24,
        compare_previous_window=False,
        include_raw_json=False,
        symbol_filter="",
        setup_filter="",
        runtime_health={"running": True, "status": "running", "health": "healthy"},
        heartbeat_text="Heartbeat age: 10s",
        records=[],
        current_funnel=current_funnel,
        previous_funnel={},
        current_channel_funnel=current_channel_funnel,
        previous_channel_funnel={},
        now_ts=now_ts,
    )
    metrics = snapshot["path_funnel_truth"]["EVAL::FUNDING_EXTREME"]
    assert metrics["classification"] == "dependency-missing"
    assert metrics["no_signal_reasons"]["missing_funding_rate"] == 6
    assert metrics["dependency_missing_reasons"]["missing_funding_rate"] == 6
    assert snapshot["dependency_readiness"]["funding_rate"]["presence"]["absent"] == 5
