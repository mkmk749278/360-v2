from __future__ import annotations

from src.runtime_truth_report import (
    build_lifecycle_summary,
    build_snapshot,
    classify_path,
    compare_windows,
    count_log_markers,
    format_truth_report_markdown,
    parse_channel_funnel_from_logs,
    parse_confidence_gate_components_from_logs,
    parse_confidence_gate_decisions_from_logs,
    parse_path_funnel_from_logs,
    parse_quiet_scalp_block_from_logs,
    parse_regime_distribution_from_logs,
    summarize_invalidation_audit,
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
            "Path funnel (last 100 cycles): path={} channel={'dependency_presence:360_SCALP:cvd:absent': 4, 'dependency_state:360_SCALP:cvd:unavailable': 4, 'dependency_bucket:360_SCALP:cvd:none': 4, 'dependency_presence:360_SWING:cvd:present': 2}",
        ]
    )
    parsed = parse_channel_funnel_from_logs(logs, "360_SCALP")
    assert parsed["dependency_presence:360_SCALP:cvd:absent"] == 4
    assert parsed["dependency_state:360_SCALP:cvd:unavailable"] == 4
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
        "dependency_state:360_SCALP:funding_rate:unavailable": 5,
        "dependency_bucket:360_SCALP:funding_rate:none": 5,
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
    assert snapshot["dependency_readiness"]["funding_rate"]["states"]["unavailable"] == 5
    assert snapshot["dependency_readiness"]["funding_rate"]["buckets"]["none"] == 5


def test_build_snapshot_includes_dependency_source_and_quality_dimensions() -> None:
    now_ts = 1_000_000.0
    current_channel_funnel = {
        "dependency_presence:360_SCALP:order_book:present": 3,
        "dependency_state:360_SCALP:order_book:populated": 3,
        "dependency_bucket:360_SCALP:order_book:few": 3,
        "dependency_source:360_SCALP:order_book:book_ticker": 3,
        "dependency_quality:360_SCALP:order_book:top_of_book_only": 3,
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
        current_funnel={},
        previous_funnel={},
        current_channel_funnel=current_channel_funnel,
        previous_channel_funnel={},
        now_ts=now_ts,
    )
    dep = snapshot["dependency_readiness"]["order_book"]
    assert dep["sources"]["book_ticker"] == 3
    assert dep["quality"]["top_of_book_only"] == 3


# ────────────────────────────────────────────────────────────────────────
# Tier-1 monitor upgrade: regime / QUIET_SCALP_BLOCK / confidence_gate /
# log-parse diagnostics parsers and end-to-end snapshot/markdown wiring.
# ────────────────────────────────────────────────────────────────────────


def test_parse_regime_distribution_from_logs_aggregates_across_emissions() -> None:
    log_text = "\n".join([
        "2026-04-30T10:00:00 | INFO | Regime distribution (last 100 cycles): {'QUIET': 75, 'RANGING': 22, 'TRENDING_UP': 3}",
        "noise line that should be ignored",
        "2026-04-30T10:01:40 | INFO | Regime distribution (last 100 cycles): {'QUIET': 80, 'RANGING': 18, 'VOLATILE': 2}",
    ])
    counts = parse_regime_distribution_from_logs(log_text)
    assert counts == {"QUIET": 155, "RANGING": 40, "TRENDING_UP": 3, "VOLATILE": 2}


def test_parse_regime_distribution_from_logs_handles_empty_and_malformed() -> None:
    assert parse_regime_distribution_from_logs("") == {}
    # Malformed dict literal must not crash the parser.
    log_text = "Regime distribution (last 100 cycles): {garbage"
    assert parse_regime_distribution_from_logs(log_text) == {}


def test_parse_quiet_scalp_block_from_logs_counts_and_computes_gap() -> None:
    log_text = "\n".join([
        "QUIET_SCALP_BLOCK BTCUSDT 360_SCALP conf=58.2 < min=60.0",
        "QUIET_SCALP_BLOCK ETHUSDT 360_SCALP conf=55.0 < min=60.0",
        "QUIET_SCALP_BLOCK BTCUSDT 360_SCALP conf=59.5 < min=60.0",
        # Other channel — must be filtered out.
        "QUIET_SCALP_BLOCK DOGEUSDT 360_SWING conf=58.0 < min=60.0",
    ])
    result = parse_quiet_scalp_block_from_logs(log_text, "360_SCALP")
    assert result["total"] == 3
    assert result["by_symbol"] == {"BTCUSDT": 2, "ETHUSDT": 1}
    # Average gap = ((60-58.2) + (60-55) + (60-59.5)) / 3 = (1.8 + 5.0 + 0.5) / 3 ≈ 2.43
    assert abs(result["average_gap_to_min"] - 2.43) < 0.01
    assert result["samples"] == 3


def test_parse_quiet_scalp_block_from_logs_handles_empty() -> None:
    result = parse_quiet_scalp_block_from_logs("", "360_SCALP")
    assert result == {"total": 0, "by_symbol": {}, "average_gap_to_min": 0.0, "samples": 0}


def test_parse_confidence_gate_decisions_from_logs_groups_by_setup_decision_reason() -> None:
    log_text = "\n".join([
        "confidence_gate BTCUSDT 360_SCALP [QUIET_COMPRESSION_BREAK]: decision=filtered reason=quiet_scalp_min_confidence raw=58.0 composite=58.0 pre_soft=58.0 final=58.0 threshold=60.0 penalties(eval=0.0,gate=0.0,total=0.0,pair_analysis=0.0) adjustments(feedback=+0.0,stat_filter=+0.0,regime_transition=+0.0) components(market=0.0,execution=0.0,risk=0.0,thesis_adj=0.0)",
        "confidence_gate ETHUSDT 360_SCALP [QUIET_COMPRESSION_BREAK]: decision=filtered reason=quiet_scalp_min_confidence raw=55.0",
        "confidence_gate ADAUSDT 360_SCALP [FAILED_AUCTION_RECLAIM]: decision=accepted reason=above_threshold raw=82.0",
        # Wrong channel filtered out.
        "confidence_gate FOO 360_SWING [BAR]: decision=filtered reason=other raw=70.0",
    ])
    result = parse_confidence_gate_decisions_from_logs(log_text, "360_SCALP")
    assert "QUIET_COMPRESSION_BREAK" in result
    assert result["QUIET_COMPRESSION_BREAK"]["filtered"] == {"quiet_scalp_min_confidence": 2}
    assert result["FAILED_AUCTION_RECLAIM"]["accepted"] == {"above_threshold": 1}
    assert "BAR" not in result  # other channel correctly excluded


def test_count_log_markers_returns_per_marker_counts() -> None:
    log_text = "\n".join([
        "Path funnel (last 100 cycles): path={} channel={}",
        "Regime distribution (last 100 cycles): {'QUIET': 100}",
        "Regime distribution (last 100 cycles): {'QUIET': 100}",
        "QUIET_SCALP_BLOCK BTCUSDT 360_SCALP conf=58.0 < min=60.0",
        "confidence_gate BTCUSDT 360_SCALP [SETUP]: decision=filtered reason=other",
        "unrelated line",
    ])
    counts = count_log_markers(log_text)
    assert counts["path_funnel"] == 1
    assert counts["regime_distribution"] == 2
    assert counts["quiet_scalp_block"] == 1
    assert counts["confidence_gate"] == 1
    assert counts["total_lines"] == 6


def test_parse_free_channel_posts_groups_by_source_and_severity() -> None:
    from src.runtime_truth_report import parse_free_channel_posts_from_logs
    log_text = "\n".join([
        "free_channel_post source=signal_close severity=HIGH symbol=BTCUSDT",
        "free_channel_post source=signal_close severity=HIGH symbol=ETHUSDT",
        "free_channel_post source=btc_move severity=CRITICAL symbol=-",
        "free_channel_post source=regime_shift severity=HIGH symbol=-",
        "free_channel_post source=fear_greed severity=HIGH symbol=-",
        "unrelated line",
        "free_channel_post source=signal_highlight severity=HIGH symbol=SOLUSDT",
    ])
    result = parse_free_channel_posts_from_logs(log_text)
    assert result["total"] == 6
    assert result["by_source"]["signal_close"] == 2
    assert result["by_source"]["btc_move"] == 1
    assert result["by_source"]["regime_shift"] == 1
    assert result["by_source"]["fear_greed"] == 1
    assert result["by_source"]["signal_highlight"] == 1
    assert result["by_severity"]["HIGH"] == 5
    assert result["by_severity"]["CRITICAL"] == 1
    assert result["by_source_severity"]["signal_close"]["HIGH"] == 2


def test_parse_free_channel_posts_handles_empty() -> None:
    from src.runtime_truth_report import parse_free_channel_posts_from_logs
    result = parse_free_channel_posts_from_logs("")
    assert result == {
        "by_source": {},
        "by_severity": {},
        "by_source_severity": {},
        "total": 0,
    }


def test_count_log_markers_includes_free_channel_post() -> None:
    log_text = "\n".join([
        "free_channel_post source=signal_close severity=HIGH symbol=BTCUSDT",
        "free_channel_post source=btc_move severity=CRITICAL symbol=-",
        "unrelated line",
    ])
    counts = count_log_markers(log_text)
    assert counts["free_channel_post"] == 2


def test_format_truth_report_renders_free_channel_section() -> None:
    from src.runtime_truth_report import format_truth_report_markdown
    snapshot = {
        "executive_summary": {},
        "runtime_health": {"running": True, "status": "running", "health": "healthy"},
        "path_funnel_truth": {},
        "dependency_readiness": {},
        "lifecycle_truth": {},
        "quality_by_setup": {},
        "regime_distribution": {},
        "quiet_scalp_block": {},
        "confidence_gate_decisions": {},
        "confidence_gate_components": {},
        "invalidation_audit": {},
        "log_parse_diagnostics": {},
        "free_channel_posts": {
            "by_source": {"signal_close": 3, "btc_move": 1},
            "by_severity": {"HIGH": 3, "CRITICAL": 1},
            "by_source_severity": {},
            "total": 4,
        },
        "post_correction_focus": {},
        "recommended_operator_focus": {},
    }
    md = format_truth_report_markdown(snapshot, {})
    assert "## Free-channel post attribution" in md
    assert "Total posts in window: **4**" in md
    assert "| signal_close | 3 |" in md
    assert "| btc_move | 1 |" in md
    assert "HIGH=3" in md
    assert "CRITICAL=1" in md


def test_format_truth_report_renders_empty_free_channel_section() -> None:
    """When no free-channel posts fired in window, render the placeholder line."""
    from src.runtime_truth_report import format_truth_report_markdown
    snapshot = {
        "executive_summary": {},
        "runtime_health": {"running": True, "status": "running", "health": "healthy"},
        "path_funnel_truth": {},
        "dependency_readiness": {},
        "lifecycle_truth": {},
        "quality_by_setup": {},
        "regime_distribution": {},
        "quiet_scalp_block": {},
        "confidence_gate_decisions": {},
        "confidence_gate_components": {},
        "invalidation_audit": {},
        "log_parse_diagnostics": {},
        "free_channel_posts": {},
        "post_correction_focus": {},
        "recommended_operator_focus": {},
    }
    md = format_truth_report_markdown(snapshot, {})
    assert "## Free-channel post attribution" in md
    assert "no free-channel posts in this window" in md


def test_count_log_markers_handles_empty() -> None:
    counts = count_log_markers("")
    assert counts == {
        "path_funnel": 0,
        "regime_distribution": 0,
        "quiet_scalp_block": 0,
        "confidence_gate": 0,
        "free_channel_post": 0,
        "total_lines": 0,
    }


def test_build_snapshot_surfaces_tier1_keys() -> None:
    snapshot, _ = build_snapshot(
        channel="360_SCALP",
        lookback_hours=24,
        compare_previous_window=False,
        include_raw_json=False,
        symbol_filter="",
        setup_filter="",
        runtime_health={"running": True, "status": "running", "health": "healthy"},
        heartbeat_text="",
        records=[],
        current_funnel={},
        previous_funnel={},
        regime_distribution={"QUIET": 950, "RANGING": 50},
        quiet_scalp_block={"total": 12, "by_symbol": {"BTCUSDT": 5}, "average_gap_to_min": 2.4, "samples": 12},
        confidence_gate_decisions={"FOO": {"filtered": {"reason_x": 3}}},
        log_parse_diagnostics={"path_funnel": 5, "regime_distribution": 5, "quiet_scalp_block": 12, "confidence_gate": 30, "total_lines": 1200},
        now_ts=1_777_500_000.0,
    )
    assert snapshot["regime_distribution"]["QUIET"] == 950
    assert snapshot["quiet_scalp_block"]["total"] == 12
    assert snapshot["confidence_gate_decisions"]["FOO"]["filtered"]["reason_x"] == 3
    assert snapshot["log_parse_diagnostics"]["path_funnel"] == 5


def test_format_truth_report_markdown_renders_tier1_sections() -> None:
    snapshot, _ = build_snapshot(
        channel="360_SCALP",
        lookback_hours=24,
        compare_previous_window=False,
        include_raw_json=False,
        symbol_filter="",
        setup_filter="",
        runtime_health={"running": True, "status": "running", "health": "healthy"},
        heartbeat_text="",
        records=[],
        current_funnel={},
        previous_funnel={},
        regime_distribution={"QUIET": 950, "RANGING": 50},
        quiet_scalp_block={"total": 12, "by_symbol": {"BTCUSDT": 5}, "average_gap_to_min": 2.4, "samples": 12},
        confidence_gate_decisions={"QCB": {"filtered": {"quiet_scalp_min_confidence": 3}}},
        log_parse_diagnostics={"path_funnel": 5, "regime_distribution": 5, "quiet_scalp_block": 12, "confidence_gate": 30, "total_lines": 1200},
        now_ts=1_777_500_000.0,
    )
    md = format_truth_report_markdown(snapshot, {})
    assert "## Regime distribution" in md
    assert "QUIET" in md and "950" in md
    assert "## QUIET_SCALP_BLOCK gate" in md
    assert "Total blocks in window: **12**" in md
    assert "## Confidence gate decisions" in md
    assert "QCB" in md and "quiet_scalp_min_confidence" in md
    assert "## Log parse diagnostics" in md
    assert "Total log lines in window" in md


def test_format_truth_report_markdown_handles_missing_tier1_data() -> None:
    snapshot, _ = build_snapshot(
        channel="360_SCALP",
        lookback_hours=24,
        compare_previous_window=False,
        include_raw_json=False,
        symbol_filter="",
        setup_filter="",
        runtime_health={"running": True, "status": "running", "health": "healthy"},
        heartbeat_text="",
        records=[],
        current_funnel={},
        previous_funnel={},
        now_ts=1_777_500_000.0,
    )
    md = format_truth_report_markdown(snapshot, {})
    # Sections render with helpful "no data" hints rather than crashing.
    assert "## Regime distribution" in md
    assert "no regime data parsed" in md
    assert "## QUIET_SCALP_BLOCK gate" in md
    assert "no QUIET_SCALP_BLOCK events" in md


# ────────────────────────────────────────────────────────────────────────
# Tier-2 monitor upgrade: confidence component-score histogram.
# Answers "where are the 14.83 confidence-gap points being lost" by
# breaking the score into market / execution / risk / thesis_adj +
# penalties, per setup × decision.
# ────────────────────────────────────────────────────────────────────────


_SAMPLE_CONFIDENCE_LINE = (
    "2026-04-30 12:00:00 | scanner | INFO | "
    "confidence_gate BTCUSDT 360_SCALP [QUIET_COMPRESSION_BREAK]: "
    "decision=filtered reason=min_confidence raw=58.0 "
    "composite=58.0 pre_soft=58.0 final=58.0 threshold=65.0 "
    "penalties(eval=2.0,gate=1.0,total=3.0,pair_analysis=0.0) "
    "adjustments(feedback=+0.0,stat_filter=+0.0,regime_transition=+0.0) "
    "components(market=20.0,execution=18.0,risk=15.0,thesis_adj=5.0)"
)


def test_parse_confidence_gate_components_aggregates_per_setup_and_decision() -> None:
    second_line = _SAMPLE_CONFIDENCE_LINE.replace("BTCUSDT", "ETHUSDT").replace(
        "raw=58.0 composite=58.0 pre_soft=58.0 final=58.0",
        "raw=62.0 composite=62.0 pre_soft=62.0 final=62.0",
    ).replace(
        "components(market=20.0,execution=18.0,risk=15.0,thesis_adj=5.0)",
        "components(market=22.0,execution=20.0,risk=14.0,thesis_adj=6.0)",
    )
    log_text = "\n".join([_SAMPLE_CONFIDENCE_LINE, second_line])
    result = parse_confidence_gate_components_from_logs(log_text, "360_SCALP")
    assert "QUIET_COMPRESSION_BREAK" in result
    bucket = result["QUIET_COMPRESSION_BREAK"]["filtered"]
    assert bucket["samples"] == 2
    # Avg final = (58 + 62) / 2 = 60; avg threshold = 65; gap = 5
    assert bucket["avg_final"] == 60.0
    assert bucket["avg_threshold"] == 65.0
    assert bucket["avg_gap_to_threshold"] == 5.0
    # Component averages.
    assert bucket["components"]["avg_market"] == 21.0
    assert bucket["components"]["avg_execution"] == 19.0
    assert bucket["components"]["avg_risk"] == 14.5
    assert bucket["components"]["avg_thesis_adj"] == 5.5


def test_parse_confidence_gate_components_filters_other_channels() -> None:
    other_chan = _SAMPLE_CONFIDENCE_LINE.replace("360_SCALP", "360_SWING")
    log_text = "\n".join([_SAMPLE_CONFIDENCE_LINE, other_chan])
    result = parse_confidence_gate_components_from_logs(log_text, "360_SCALP")
    assert result["QUIET_COMPRESSION_BREAK"]["filtered"]["samples"] == 1


def test_parse_confidence_gate_components_handles_empty_and_malformed() -> None:
    assert parse_confidence_gate_components_from_logs("", "360_SCALP") == {}
    # Lines that match the marker but not the full regex are silently skipped
    # (matches the existing parser's robustness contract).
    log_text = "confidence_gate BTCUSDT 360_SCALP [SETUP]: decision=filtered reason=foo"
    assert parse_confidence_gate_components_from_logs(log_text, "360_SCALP") == {}


def test_format_truth_report_markdown_renders_component_breakdown() -> None:
    components = {
        "QUIET_COMPRESSION_BREAK": {
            "filtered": {
                "samples": 100,
                "avg_final": 58.4,
                "avg_threshold": 65.0,
                "avg_gap_to_threshold": 6.6,
                "avg_raw": 58.4,
                "avg_composite": 58.4,
                "avg_total_penalty": 3.0,
                "components": {
                    "avg_market": 20.5,
                    "avg_execution": 18.2,
                    "avg_risk": 14.8,
                    "avg_thesis_adj": 4.9,
                },
            }
        }
    }
    snapshot, _ = build_snapshot(
        channel="360_SCALP", lookback_hours=24, compare_previous_window=False,
        include_raw_json=False, symbol_filter="", setup_filter="",
        runtime_health={"running": True, "status": "running", "health": "healthy"},
        heartbeat_text="", records=[], current_funnel={}, previous_funnel={},
        confidence_gate_components=components,
        now_ts=1_777_500_000.0,
    )
    assert snapshot["confidence_gate_components"] == components
    md = format_truth_report_markdown(snapshot, {})
    assert "## Confidence component breakdown" in md
    # Header + the QCB row should both render.
    assert "Avg final" in md
    assert "QUIET_COMPRESSION_BREAK" in md
    assert "20.50" in md  # market component
    assert "6.60" in md   # gap to threshold


# ────────────────────────────────────────────────────────────────────────
# Invalidation Quality Audit — summarize + markdown render.
# ────────────────────────────────────────────────────────────────────────


def _audit_record(setup, family, classification):
    return {
        "signal_id": "X", "symbol": "BTCUSDT", "channel": "360_SCALP",
        "setup_class": setup, "kill_reason_family": family,
        "classification": classification,
    }


def test_summarize_invalidation_audit_groups_by_setup_and_reason() -> None:
    records = [
        _audit_record("SR_FLIP_RETEST", "momentum_loss", "PROTECTIVE"),
        _audit_record("SR_FLIP_RETEST", "momentum_loss", "PREMATURE"),
        _audit_record("SR_FLIP_RETEST", "momentum_loss", "PREMATURE"),
        _audit_record("QUIET_COMPRESSION_BREAK", "regime_shift", "PROTECTIVE"),
        _audit_record("QUIET_COMPRESSION_BREAK", "regime_shift", "NEUTRAL"),
        # Stale (no classification) — counted separately.
        {"signal_id": "Y", "setup_class": "FAR", "kill_reason_family": "ema_crossover",
         "classification": None},
    ]
    audit = summarize_invalidation_audit(records)
    assert audit["totals"]["PROTECTIVE"] == 2
    assert audit["totals"]["PREMATURE"] == 2
    assert audit["totals"]["NEUTRAL"] == 1
    assert audit["stale"] == 1
    assert audit["by_setup"]["SR_FLIP_RETEST"]["PROTECTIVE"] == 1
    assert audit["by_setup"]["SR_FLIP_RETEST"]["PREMATURE"] == 2
    assert audit["by_reason"]["regime_shift"]["NEUTRAL"] == 1


def test_summarize_invalidation_audit_handles_empty() -> None:
    audit = summarize_invalidation_audit([])
    assert audit["totals"] == {
        "PROTECTIVE": 0, "PREMATURE": 0, "NEUTRAL": 0, "INSUFFICIENT_DATA": 0,
    }
    assert audit["by_setup"] == {}
    assert audit["stale"] == 0


def test_format_truth_report_renders_audit_section_with_data() -> None:
    audit = {
        "totals": {
            "PROTECTIVE": 8, "PREMATURE": 3, "NEUTRAL": 2, "INSUFFICIENT_DATA": 1,
        },
        "by_setup": {
            "SR_FLIP_RETEST": {"PROTECTIVE": 5, "PREMATURE": 2, "NEUTRAL": 1, "INSUFFICIENT_DATA": 0},
        },
        "by_reason": {
            "momentum_loss": {"PROTECTIVE": 6, "PREMATURE": 2, "NEUTRAL": 1, "INSUFFICIENT_DATA": 0},
        },
        "stale": 4,
    }
    snapshot, _ = build_snapshot(
        channel="360_SCALP", lookback_hours=24, compare_previous_window=False,
        include_raw_json=False, symbol_filter="", setup_filter="",
        runtime_health={"running": True, "status": "running", "health": "healthy"},
        heartbeat_text="", records=[], current_funnel={}, previous_funnel={},
        invalidation_audit=audit,
        now_ts=1_777_500_000.0,
    )
    md = format_truth_report_markdown(snapshot, {})
    assert "## Invalidation Quality Audit" in md
    assert "PROTECTIVE=8" in md
    assert "PREMATURE=3" in md
    assert "Net-helping" in md  # 8 > 3
    assert "SR_FLIP_RETEST" in md
    assert "momentum_loss" in md


def test_format_truth_report_audit_section_calls_out_net_hurting() -> None:
    audit = {
        "totals": {"PROTECTIVE": 2, "PREMATURE": 7, "NEUTRAL": 1, "INSUFFICIENT_DATA": 0},
        "by_setup": {}, "by_reason": {}, "stale": 0,
    }
    snapshot, _ = build_snapshot(
        channel="360_SCALP", lookback_hours=24, compare_previous_window=False,
        include_raw_json=False, symbol_filter="", setup_filter="",
        runtime_health={"running": True, "status": "running", "health": "healthy"},
        heartbeat_text="", records=[], current_funnel={}, previous_funnel={},
        invalidation_audit=audit,
        now_ts=1_777_500_000.0,
    )
    md = format_truth_report_markdown(snapshot, {})
    assert "Net-hurting" in md  # 7 > 2 — surfaces the flag


def test_format_truth_report_audit_section_when_no_data() -> None:
    snapshot, _ = build_snapshot(
        channel="360_SCALP", lookback_hours=24, compare_previous_window=False,
        include_raw_json=False, symbol_filter="", setup_filter="",
        runtime_health={"running": True, "status": "running", "health": "healthy"},
        heartbeat_text="", records=[], current_funnel={}, previous_funnel={},
        now_ts=1_777_500_000.0,
    )
    md = format_truth_report_markdown(snapshot, {})
    assert "## Invalidation Quality Audit" in md
    assert "no classified invalidation records yet" in md
