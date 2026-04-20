from __future__ import annotations

import ast
import json
import re
import statistics
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

TP_LABELS = {"TP", "TP1", "TP2", "TP3", "TP_HIT", "TP1_HIT", "TP2_HIT", "TP3_HIT", "TAKE_PROFIT", "WIN"}
SL_LABELS = {"SL", "SL_HIT", "STOP_LOSS", "LOSS"}
_POST_CORRECTION_TARGET_SETUPS = ("SR_FLIP_RETEST", "TREND_PULLBACK_EMA")


def _median(values: Iterable[Optional[float]]) -> Optional[float]:
    nums = [float(v) for v in values if isinstance(v, (int, float))]
    if not nums:
        return None
    return float(statistics.median(nums))


def _pct(num: int, den: int) -> float:
    if den <= 0:
        return 0.0
    return round((num / den) * 100.0, 1)


def _outcome_label(record: Dict[str, Any]) -> str:
    return str(
        record.get("outcome_label") or record.get("outcome") or record.get("status") or ""
    ).upper()


def _parse_funnel_key_for_channel(key: str, channel: str) -> Optional[Tuple[str, str, str]]:
    """Parse a funnel key and return (stage, family, setup) for one channel.

    Key contract: stage:channel:family:setup.
    Stage can include nested tokens (for example ``geometry:final_live:changed``),
    and setup can include ``:``, so parsing is anchored around ``:<channel>:``.
    """
    key_text = str(key)
    channel_token = f":{channel}:"
    if channel_token not in key_text:
        return None
    stage, rest = key_text.split(channel_token, 1)
    family_setup = rest.split(":", 1)
    if len(family_setup) != 2:
        return None
    family, setup = family_setup
    return stage, family, setup


def _parse_csv_filter(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [part.strip().upper() for part in str(raw).split(",") if part.strip()]


def _matches_filter(value: str, filters: List[str], substring: bool = False) -> bool:
    if not filters:
        return True
    probe = (value or "").upper()
    if substring:
        return any(token in probe for token in filters)
    return probe in filters


def parse_path_funnel_from_logs(log_text: str, channel: str) -> Dict[str, int]:
    counters: Dict[str, int] = defaultdict(int)
    if not log_text:
        return {}
    for line in log_text.splitlines():
        if "Path funnel (last 100 cycles): path=" not in line:
            continue
        try:
            fragment = line.split("path=", 1)[1].split(" channel=", 1)[0]
            parsed = ast.literal_eval(fragment)
        except (ValueError, SyntaxError):
            continue
        if not isinstance(parsed, dict):
            continue
        for key, value in parsed.items():
            parsed_key = _parse_funnel_key_for_channel(str(key), channel)
            if parsed_key is None:
                continue
            try:
                n = int(value or 0)
            except (TypeError, ValueError):
                n = 0
            if n > 0:
                counters[str(key)] += n
    return dict(counters)


def parse_channel_funnel_from_logs(log_text: str, channel: str) -> Dict[str, int]:
    counters: Dict[str, int] = defaultdict(int)
    if not log_text:
        return {}
    channel_prefix = f":{channel}:"
    for line in log_text.splitlines():
        if "Path funnel (last 100 cycles): path=" not in line:
            continue
        try:
            fragment = line.split(" channel=", 1)[1]
            parsed = ast.literal_eval(fragment)
        except (IndexError, ValueError, SyntaxError):
            continue
        if not isinstance(parsed, dict):
            continue
        for key, value in parsed.items():
            key_text = str(key)
            if channel_prefix not in key_text:
                continue
            try:
                n = int(value or 0)
            except (TypeError, ValueError):
                n = 0
            if n > 0:
                counters[key_text] += n
    return dict(counters)


def stage_totals_by_setup(funnel_counters: Dict[str, int], channel: str) -> Dict[str, Dict[str, int]]:
    by_setup: Dict[str, Dict[str, int]] = {}
    for key, value in funnel_counters.items():
        parsed_key = _parse_funnel_key_for_channel(str(key), channel)
        if parsed_key is None:
            continue
        stage, family, setup = parsed_key
        bucket = by_setup.setdefault(setup, {"family": family})
        bucket[stage] = bucket.get(stage, 0) + int(value or 0)
    return by_setup


def classify_path(path_metrics: Dict[str, int], quality_metrics: Optional[Dict[str, Any]] = None) -> str:
    attempts = int(path_metrics.get("evaluator_attempted", 0))
    generated = int(path_metrics.get("evaluator_generated", 0)) + int(path_metrics.get("generated", 0))
    gated = int(path_metrics.get("gated", 0))
    emitted = int(path_metrics.get("emitted", 0))

    if attempts < 3 and emitted < 2:
        return "low-sample"
    if attempts > 0 and generated <= 0:
        return "non-generating"
    if generated > 0 and emitted <= 0 and gated > 0:
        return "generated-but-gated"
    if emitted <= 0:
        return "low-sample"

    quality_metrics = quality_metrics or {}
    closed = int(quality_metrics.get("closed", 0))
    if closed < 3:
        return "low-sample"
    win_rate = float(quality_metrics.get("win_rate", 0.0))
    sl_rate = float(quality_metrics.get("sl_rate", 0.0))
    if win_rate >= 45.0 and sl_rate <= 45.0:
        return "active-healthy"
    return "active-low-quality"


def build_lifecycle_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    create_to_breach = [r.get("create_to_first_breach_sec") for r in records]
    create_to_terminal = [r.get("create_to_terminal_sec") for r in records]

    fast_thresholds = [30, 60, 120, 180]
    fast_buckets = {}
    valid_breach = [float(v) for v in create_to_breach if isinstance(v, (int, float)) and v >= 0]
    for threshold in fast_thresholds:
        count = sum(1 for value in valid_breach if value <= threshold)
        fast_buckets[f"under_{threshold}s"] = {"count": count, "pct": _pct(count, len(valid_breach))}

    near_three_min = [
        float(v)
        for v in create_to_terminal
        if isinstance(v, (int, float)) and 150 <= float(v) <= 240
    ]
    valid_terminal = [float(v) for v in create_to_terminal if isinstance(v, (int, float)) and v >= 0]

    return {
        "median_create_to_dispatch_sec": _median(r.get("create_to_dispatch_sec") for r in records),
        "median_create_to_first_breach_sec": _median(create_to_breach),
        "median_create_to_terminal_sec": _median(create_to_terminal),
        "median_first_breach_to_terminal_sec": _median(
            r.get("first_breach_to_terminal_sec") for r in records
        ),
        "fast_failure_buckets": fast_buckets,
        "terminal_close_around_3m": {
            "count": len(near_three_min),
            "pct": _pct(len(near_three_min), len(valid_terminal)),
        },
    }


def build_quality_by_setup(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        setup = str(record.get("setup_class") or "UNKNOWN")
        grouped[setup].append(record)

    result: Dict[str, Dict[str, Any]] = {}
    for setup, setup_records in grouped.items():
        labels = [_outcome_label(record) for record in setup_records]
        closed = len(setup_records)
        win_count = sum(1 for label in labels if label in TP_LABELS)
        sl_count = sum(1 for label in labels if label in SL_LABELS)
        pnl_values = [
            float(record.get("pnl_pct"))
            for record in setup_records
            if isinstance(record.get("pnl_pct"), (int, float))
        ]
        result[setup] = {
            "emitted": closed,
            "closed": closed,
            "win_rate": _pct(win_count, closed),
            "tp_rate": _pct(win_count, closed),
            "sl_rate": _pct(sl_count, closed),
            "average_pnl_pct": round(sum(pnl_values) / len(pnl_values), 4) if pnl_values else None,
            "median_first_breach_sec": _median(
                record.get("create_to_first_breach_sec") for record in setup_records
            ),
            "median_terminal_duration_sec": _median(
                record.get("create_to_terminal_sec") for record in setup_records
            ),
        }
    return result


def summarize_runtime_health(
    runtime_health: Dict[str, Any],
    heartbeat_text: str,
    records: List[Dict[str, Any]],
    now_ts: float,
) -> Dict[str, Any]:
    heartbeat_age_sec: Optional[int] = None
    heartbeat_warning = False
    match = re.search(r"Heartbeat age:\s*(\d+)s", heartbeat_text or "")
    if match:
        heartbeat_age_sec = int(match.group(1))
        heartbeat_warning = heartbeat_age_sec > 120

    latest_record_ts = max(
        [float(r.get("timestamp")) for r in records if isinstance(r.get("timestamp"), (int, float))],
        default=None,
    )
    latest_record_age_sec = int(now_ts - latest_record_ts) if latest_record_ts else None
    fresh_records = latest_record_age_sec is not None and latest_record_age_sec <= 2 * 3600

    running = bool(runtime_health.get("running", False))
    health_status = str(runtime_health.get("health", "unknown"))

    overall = "healthy"
    if not running or health_status == "unhealthy":
        overall = "unhealthy"
    elif heartbeat_warning or not fresh_records:
        overall = "stale"

    return {
        "overall": overall,
        "running": running,
        "status": runtime_health.get("status", "unknown"),
        "health": health_status,
        "heartbeat_age_sec": heartbeat_age_sec,
        "heartbeat_warning": heartbeat_warning,
        "latest_record_age_sec": latest_record_age_sec,
        "records_fresh": fresh_records,
    }


def compare_windows(
    current_path_summary: Dict[str, Dict[str, int]],
    previous_path_summary: Dict[str, Dict[str, int]],
    current_lifecycle: Dict[str, Any],
    previous_lifecycle: Dict[str, Any],
    current_quality: Dict[str, Dict[str, Any]],
    previous_quality: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    def stage_total(summary: Dict[str, Dict[str, int]], stage: str) -> int:
        return sum(int(metrics.get(stage, 0)) for metrics in summary.values())

    quality_changes: Dict[str, Dict[str, Any]] = {}
    for setup in sorted(set(current_quality) | set(previous_quality)):
        curr = current_quality.get(setup, {})
        prev = previous_quality.get(setup, {})
        curr_closed = int(curr.get("closed", 0))
        prev_closed = int(prev.get("closed", 0))
        if curr_closed < 3 and prev_closed < 3:
            continue
        quality_changes[setup] = {
            "current_win_rate": curr.get("win_rate"),
            "previous_win_rate": prev.get("win_rate"),
            "win_rate_delta": round(float(curr.get("win_rate", 0.0)) - float(prev.get("win_rate", 0.0)), 2),
            "current_avg_pnl": curr.get("average_pnl_pct"),
            "previous_avg_pnl": prev.get("average_pnl_pct"),
            "avg_pnl_delta": round(
                float(curr.get("average_pnl_pct") or 0.0) - float(prev.get("average_pnl_pct") or 0.0),
                4,
            ),
        }

    current_fast = int(current_lifecycle.get("fast_failure_buckets", {}).get("under_180s", {}).get("count", 0))
    previous_fast = int(previous_lifecycle.get("fast_failure_buckets", {}).get("under_180s", {}).get("count", 0))

    return {
        "emissions_delta": stage_total(current_path_summary, "emitted") - stage_total(previous_path_summary, "emitted"),
        "gating_delta": stage_total(current_path_summary, "gated") - stage_total(previous_path_summary, "gated"),
        "no_generation_delta": stage_total(current_path_summary, "evaluator_no_signal")
        - stage_total(previous_path_summary, "evaluator_no_signal"),
        "fast_failures_delta": current_fast - previous_fast,
        "quality_changes": quality_changes,
        "post_correction_window_delta": {
            setup: {
                "emitted_delta": int(current_path_summary.get(setup, {}).get("emitted", 0))
                - int(previous_path_summary.get(setup, {}).get("emitted", 0)),
                "win_rate_delta": round(
                    float(current_quality.get(setup, {}).get("win_rate", 0.0))
                    - float(previous_quality.get(setup, {}).get("win_rate", 0.0)),
                    2,
                ),
                "sl_rate_delta": round(
                    float(current_quality.get(setup, {}).get("sl_rate", 0.0))
                    - float(previous_quality.get(setup, {}).get("sl_rate", 0.0)),
                    2,
                ),
                "median_first_breach_delta_sec": round(
                    float(current_quality.get(setup, {}).get("median_first_breach_sec") or 0.0)
                    - float(previous_quality.get(setup, {}).get("median_first_breach_sec") or 0.0),
                    2,
                ),
                "median_terminal_delta_sec": round(
                    float(current_quality.get(setup, {}).get("median_terminal_duration_sec") or 0.0)
                    - float(previous_quality.get(setup, {}).get("median_terminal_duration_sec") or 0.0),
                    2,
                ),
                "geometry_preserved_delta": int(
                    current_path_summary.get(setup, {}).get("geometry:final_live:preserved", 0)
                )
                - int(previous_path_summary.get(setup, {}).get("geometry:final_live:preserved", 0)),
                "geometry_changed_delta": int(
                    current_path_summary.get(setup, {}).get("geometry:final_live:changed", 0)
                )
                - int(previous_path_summary.get(setup, {}).get("geometry:final_live:changed", 0)),
                "geometry_rejected_delta": int(
                    current_path_summary.get(setup, {}).get("geometry:final_live:rejected", 0)
                )
                - int(previous_path_summary.get(setup, {}).get("geometry:final_live:rejected", 0)),
            }
            for setup in _POST_CORRECTION_TARGET_SETUPS
        },
    }


def build_snapshot(
    *,
    channel: str,
    lookback_hours: int,
    compare_previous_window: bool,
    include_raw_json: bool,
    symbol_filter: str,
    setup_filter: str,
    runtime_health: Dict[str, Any],
    heartbeat_text: str,
    records: List[Dict[str, Any]],
    current_funnel: Dict[str, int],
    previous_funnel: Dict[str, int],
    current_channel_funnel: Optional[Dict[str, int]] = None,
    previous_channel_funnel: Optional[Dict[str, int]] = None,
    now_ts: Optional[float] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    now_ts = now_ts or time.time()
    lookback_sec = lookback_hours * 3600
    current_start = now_ts - lookback_sec
    previous_start = current_start - lookback_sec

    symbol_filters = _parse_csv_filter(symbol_filter)
    setup_filters = _parse_csv_filter(setup_filter)

    def _record_in_scope(record: Dict[str, Any]) -> bool:
        if str(record.get("channel") or "") != channel:
            return False
        if not _matches_filter(str(record.get("symbol") or ""), symbol_filters, substring=False):
            return False
        if not _matches_filter(str(record.get("setup_class") or ""), setup_filters, substring=True):
            return False
        return True

    scoped = [record for record in records if _record_in_scope(record)]

    def _in_window(record: Dict[str, Any], start_ts: float, end_ts: float) -> bool:
        ts = record.get("timestamp")
        if not isinstance(ts, (int, float)):
            return False
        return start_ts <= float(ts) < end_ts

    current_records = [record for record in scoped if _in_window(record, current_start, now_ts + 1)]
    previous_records = [record for record in scoped if _in_window(record, previous_start, current_start)]

    current_paths = stage_totals_by_setup(current_funnel, channel)
    previous_paths = stage_totals_by_setup(previous_funnel, channel)
    current_channel_funnel = current_channel_funnel or {}
    previous_channel_funnel = previous_channel_funnel or {}

    current_quality = build_quality_by_setup(current_records)
    previous_quality = build_quality_by_setup(previous_records)

    path_funnel_truth = {}
    for setup, metrics in current_paths.items():
        quality = current_quality.get(setup, {})
        rejected_reasons = {
            stage.replace("geometry:final_live:rejected_reason:", ""): int(count or 0)
            for stage, count in metrics.items()
            if stage.startswith("geometry:final_live:rejected_reason:")
        }
        no_signal_reasons = {
            stage.replace("evaluator_no_signal_reason:", ""): int(count or 0)
            for stage, count in metrics.items()
            if stage.startswith("evaluator_no_signal_reason:")
        }
        dependency_missing_reasons = {
            stage.replace("dependency_missing:", ""): int(count or 0)
            for stage, count in metrics.items()
            if stage.startswith("dependency_missing:")
        }
        generated = int(metrics.get("evaluator_generated", 0)) + int(metrics.get("generated", 0))
        dependency_missing_total = sum(int(v or 0) for v in dependency_missing_reasons.values())
        if int(metrics.get("evaluator_attempted", 0)) > 0 and generated <= 0 and dependency_missing_total > 0:
            classification = "dependency-missing"
        else:
            classification = classify_path(metrics, quality)
        path_funnel_truth[setup] = {
            "attempts": int(metrics.get("evaluator_attempted", 0)),
            "no_signal": int(metrics.get("evaluator_no_signal", 0)),
            "generated": generated,
            "scanner_preparation": int(metrics.get("scanner_preparation", 0)),
            "gated": int(metrics.get("gated", 0)),
            "emitted": int(metrics.get("emitted", 0)),
            "geometry_final_preserved": int(metrics.get("geometry:final_live:preserved", 0)),
            "geometry_final_changed": int(metrics.get("geometry:final_live:changed", 0)),
            "geometry_final_rejected": int(metrics.get("geometry:final_live:rejected", 0)),
            "geometry_rejected_reasons": rejected_reasons,
            "no_signal_reasons": no_signal_reasons,
            "dependency_missing_reasons": dependency_missing_reasons,
            "dependency_missing_total": dependency_missing_total,
            "classification": classification,
        }

    lifecycle_summary = build_lifecycle_summary(current_records)
    runtime_summary = summarize_runtime_health(runtime_health, heartbeat_text, current_records, now_ts)

    comparison = {
        "enabled": bool(compare_previous_window),
    }
    if compare_previous_window:
        comparison.update(
            compare_windows(
                current_paths,
                previous_paths,
                lifecycle_summary,
                build_lifecycle_summary(previous_records),
                current_quality,
                previous_quality,
            )
        )

    healthiest = [
        setup
        for setup, metrics in sorted(
            path_funnel_truth.items(),
            key=lambda item: item[1].get("emitted", 0),
            reverse=True,
        )
        if metrics.get("classification") == "active-healthy"
    ]
    degraded = [
        setup
        for setup, metrics in sorted(
            path_funnel_truth.items(),
            key=lambda item: item[1].get("gated", 0),
            reverse=True,
        )
        if metrics.get("classification") in {"non-generating", "generated-but-gated", "active-low-quality"}
    ]

    likely_bottlenecks = [
        setup
        for setup, metrics in sorted(
            path_funnel_truth.items(),
            key=lambda item: (
                item[1].get("gated", 0),
                item[1].get("generated", 0) - item[1].get("emitted", 0),
            ),
            reverse=True,
        )
        if metrics.get("generated", 0) > 0 and metrics.get("emitted", 0) == 0
    ]

    recommended_target = None
    if degraded:
        recommended_target = degraded[0]
    elif likely_bottlenecks:
        recommended_target = likely_bottlenecks[0]
    elif healthiest:
        recommended_target = healthiest[0]

    dependency_readiness: Dict[str, Dict[str, Any]] = {}
    for key, count in current_channel_funnel.items():
        if key.startswith(f"dependency_presence:{channel}:"):
            _, _, dep, state = key.split(":", 3)
            dep_bucket = dependency_readiness.setdefault(dep, {"presence": {}, "buckets": {}})
            dep_bucket["presence"][state] = dep_bucket["presence"].get(state, 0) + int(count or 0)
        elif key.startswith(f"dependency_bucket:{channel}:"):
            _, _, dep, bucket = key.split(":", 3)
            dep_bucket = dependency_readiness.setdefault(dep, {"presence": {}, "buckets": {}})
            dep_bucket["buckets"][bucket] = dep_bucket["buckets"].get(bucket, 0) + int(count or 0)

    snapshot = {
        "generated_at": int(now_ts),
        "channel": channel,
        "lookback_hours": lookback_hours,
        "filters": {
            "symbol_filter": symbol_filter or "",
            "setup_filter": setup_filter or "",
        },
        "executive_summary": {
            "overall_health": runtime_summary["overall"],
            "top_anomalies": degraded[:3],
            "top_promising_paths": healthiest[:3],
            "recommended_next_investigation_target": recommended_target,
        },
        "runtime_health": runtime_summary,
        "path_funnel_truth": path_funnel_truth,
        "dependency_readiness": dependency_readiness,
        "lifecycle_truth": lifecycle_summary,
        "quality_by_setup": current_quality,
        "recommended_operator_focus": {
            "most_suspicious_degradation": degraded[0] if degraded else None,
            "most_promising_healthy_path": healthiest[0] if healthiest else None,
            "most_likely_bottleneck": likely_bottlenecks[0] if likely_bottlenecks else None,
            "suggested_next_investigation_target": recommended_target,
        },
        "post_correction_focus": {
            setup: {
                "attempts": int(path_funnel_truth.get(setup, {}).get("attempts", 0)),
                "generated": int(path_funnel_truth.get(setup, {}).get("generated", 0)),
                "emitted": int(path_funnel_truth.get(setup, {}).get("emitted", 0)),
                "gated": int(path_funnel_truth.get(setup, {}).get("gated", 0)),
                "classification": path_funnel_truth.get(setup, {}).get("classification", "low-sample"),
                "win_rate": float(current_quality.get(setup, {}).get("win_rate", 0.0)),
                "sl_rate": float(current_quality.get(setup, {}).get("sl_rate", 0.0)),
                "tp_rate": float(current_quality.get(setup, {}).get("tp_rate", 0.0)),
                "average_pnl_pct": current_quality.get(setup, {}).get("average_pnl_pct"),
                "median_first_breach_sec": current_quality.get(setup, {}).get("median_first_breach_sec"),
                "median_terminal_duration_sec": current_quality.get(setup, {}).get("median_terminal_duration_sec"),
                "geometry_final_preserved": int(path_funnel_truth.get(setup, {}).get("geometry_final_preserved", 0)),
                "geometry_final_changed": int(path_funnel_truth.get(setup, {}).get("geometry_final_changed", 0)),
                "geometry_final_rejected": int(path_funnel_truth.get(setup, {}).get("geometry_final_rejected", 0)),
                "geometry_rejected_reasons": path_funnel_truth.get(setup, {}).get(
                    "geometry_rejected_reasons", {}
                ),
            }
            for setup in _POST_CORRECTION_TARGET_SETUPS
        },
    }

    if include_raw_json:
        snapshot["raw_extracts"] = {
            "record_count_scoped": len(scoped),
            "record_count_current_window": len(current_records),
            "record_count_previous_window": len(previous_records),
            "current_path_funnel_counters": current_funnel,
            "previous_path_funnel_counters": previous_funnel,
            "current_channel_funnel_counters": current_channel_funnel,
            "previous_channel_funnel_counters": previous_channel_funnel,
        }

    return snapshot, comparison


def format_truth_report_markdown(snapshot: Dict[str, Any], comparison: Dict[str, Any]) -> str:
    executive = snapshot.get("executive_summary", {})
    runtime = snapshot.get("runtime_health", {})
    lifecycle = snapshot.get("lifecycle_truth", {})
    focus = snapshot.get("recommended_operator_focus", {})

    lines = [
        "# Runtime Truth Report",
        "",
        "## Executive summary",
        f"- Overall health/freshness: **{executive.get('overall_health', 'unknown')}**",
        f"- Top anomalies/concerns: {', '.join(executive.get('top_anomalies', []) or ['none'])}",
        f"- Top promising signals/paths: {', '.join(executive.get('top_promising_paths', []) or ['none'])}",
        f"- Recommended next investigation target: **{executive.get('recommended_next_investigation_target') or 'none'}**",
        "",
        "## Runtime health",
        f"- Engine running: `{runtime.get('running')}` (status={runtime.get('status')}, health={runtime.get('health')})",
        f"- Heartbeat age: `{runtime.get('heartbeat_age_sec')}` sec (warning={runtime.get('heartbeat_warning')})",
        f"- Latest performance record age: `{runtime.get('latest_record_age_sec')}` sec",
        "",
        "## Path funnel truth",
        "| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]

    path_truth = snapshot.get("path_funnel_truth", {})
    for setup, metrics in sorted(path_truth.items()):
        top_reason = "none"
        _reasons = metrics.get("no_signal_reasons", {}) or {}
        _positive_reasons = {k: int(v or 0) for k, v in _reasons.items() if int(v or 0) > 0}
        if _positive_reasons:
            top_reason = max(_positive_reasons.items(), key=lambda item: item[1])[0]
        lines.append(
            "| {setup} | {attempts} | {no_signal} | {generated} | {scanner_preparation} | {gated} | {emitted} | {classification} ({top_reason}) |".format(
                setup=setup,
                attempts=metrics.get("attempts", 0),
                no_signal=metrics.get("no_signal", 0),
                generated=metrics.get("generated", 0),
                scanner_preparation=metrics.get("scanner_preparation", 0),
                gated=metrics.get("gated", 0),
                emitted=metrics.get("emitted", 0),
                classification=metrics.get("classification", "unknown"),
                top_reason=top_reason,
            )
        )

    lines.extend(["", "## Evaluator no-signal reasons"])
    for setup, metrics in sorted(path_truth.items()):
        reasons = metrics.get("no_signal_reasons", {}) or {}
        if not reasons:
            continue
        top = ", ".join(f"{k}={v}" for k, v in sorted(reasons.items(), key=lambda item: item[1], reverse=True)[:3])
        lines.append(f"- {setup}: {top}")

    lines.extend(["", "## Dependency readiness"])
    dependency_readiness = snapshot.get("dependency_readiness", {}) or {}
    for dep_name, dep_metrics in sorted(dependency_readiness.items()):
        presence = dep_metrics.get("presence", {})
        buckets = dep_metrics.get("buckets", {})
        presence_text = ", ".join(f"{k}={v}" for k, v in sorted(presence.items())) or "none"
        bucket_text = ", ".join(f"{k}={v}" for k, v in sorted(buckets.items())) or "none"
        lines.append(f"- {dep_name}: presence[{presence_text}] buckets[{bucket_text}]")

    lines.extend(
        [
            "",
            "## Lifecycle truth summary",
            f"- Median create→dispatch: `{lifecycle.get('median_create_to_dispatch_sec')}` sec",
            f"- Median create→first breach: `{lifecycle.get('median_create_to_first_breach_sec')}` sec",
            f"- Median create→terminal: `{lifecycle.get('median_create_to_terminal_sec')}` sec",
            f"- Median first breach→terminal: `{lifecycle.get('median_first_breach_to_terminal_sec')}` sec",
            f"- Fast-failure buckets: `{json.dumps(lifecycle.get('fast_failure_buckets', {}), sort_keys=True)}`",
            f"- ~3 minute terminal-close behavior: `{json.dumps(lifecycle.get('terminal_close_around_3m', {}), sort_keys=True)}`",
            "",
            "## Quality-by-path/setup summary",
            "| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )

    quality = snapshot.get("quality_by_setup", {})
    for setup, metrics in sorted(quality.items()):
        lines.append(
            "| {setup} | {emitted} | {closed} | {win_rate} | {sl_rate} | {tp_rate} | {avg_pnl} | {mfb} | {mtd} |".format(
                setup=setup,
                emitted=metrics.get("emitted", 0),
                closed=metrics.get("closed", 0),
                win_rate=metrics.get("win_rate", 0.0),
                sl_rate=metrics.get("sl_rate", 0.0),
                tp_rate=metrics.get("tp_rate", 0.0),
                avg_pnl=metrics.get("average_pnl_pct"),
                mfb=metrics.get("median_first_breach_sec"),
                mtd=metrics.get("median_terminal_duration_sec"),
            )
        )

    lines.extend(
        [
            "",
            "## Post-correction focus (target setups)",
            "| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for setup, metrics in snapshot.get("post_correction_focus", {}).items():
        lines.append(
            "| {setup} | {attempts} | {generated} | {emitted} | {gated} | {win_rate} | {sl_rate} | {mfb} | {mtd} | {gp} | {gc} | {gr} |".format(
                setup=setup,
                attempts=metrics.get("attempts", 0),
                generated=metrics.get("generated", 0),
                emitted=metrics.get("emitted", 0),
                gated=metrics.get("gated", 0),
                win_rate=metrics.get("win_rate", 0.0),
                sl_rate=metrics.get("sl_rate", 0.0),
                mfb=metrics.get("median_first_breach_sec"),
                mtd=metrics.get("median_terminal_duration_sec"),
                gp=metrics.get("geometry_final_preserved", 0),
                gc=metrics.get("geometry_final_changed", 0),
                gr=metrics.get("geometry_final_rejected", 0),
            )
        )
        if metrics.get("geometry_rejected_reasons"):
            lines.append(
                f"  - `{setup}` geometry rejected reasons: `{json.dumps(metrics.get('geometry_rejected_reasons', {}), sort_keys=True)}`"
            )

    lines.extend(["", "## Window-over-window comparison"])
    if comparison.get("enabled"):
        lines.extend(
            [
                f"- Path emissions Δ: `{comparison.get('emissions_delta')}`",
                f"- Gating Δ: `{comparison.get('gating_delta')}`",
                f"- No-generation Δ: `{comparison.get('no_generation_delta')}`",
                f"- Fast failures Δ: `{comparison.get('fast_failures_delta')}`",
                f"- Quality changes: `{json.dumps(comparison.get('quality_changes', {}), sort_keys=True)}`",
                f"- Post-correction setup deltas: `{json.dumps(comparison.get('post_correction_window_delta', {}), sort_keys=True)}`",
            ]
        )
    else:
        lines.append("- Disabled")

    lines.extend(
        [
            "",
            "## Recommended operator focus",
            f"- Most suspicious degradation: **{focus.get('most_suspicious_degradation') or 'none'}**",
            f"- Most promising healthy path: **{focus.get('most_promising_healthy_path') or 'none'}**",
            f"- Most likely bottleneck: **{focus.get('most_likely_bottleneck') or 'none'}**",
            f"- Suggested next investigation target: **{focus.get('suggested_next_investigation_target') or 'none'}**",
            "",
        ]
    )

    return "\n".join(lines)


def load_json_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default
