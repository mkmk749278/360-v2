#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.runtime_truth_report import (
    build_snapshot,
    count_log_markers,
    format_truth_report_markdown,
    load_json_file,
    parse_channel_funnel_from_logs,
    parse_confidence_gate_components_from_logs,
    parse_confidence_gate_decisions_from_logs,
    parse_path_funnel_from_logs,
    parse_quiet_scalp_block_from_logs,
    parse_regime_distribution_from_logs,
    summarize_invalidation_audit,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build runtime truth report artifacts")
    parser.add_argument("--lookback-hours", type=int, default=24)
    parser.add_argument("--compare-previous-window", action="store_true")
    parser.add_argument("--channel", default="360_SCALP")
    parser.add_argument("--symbol-filter", default="")
    parser.add_argument("--setup-filter", default="")
    parser.add_argument("--include-raw-json", action="store_true")
    parser.add_argument("--runtime-health-json", required=True)
    parser.add_argument("--heartbeat-text", required=True)
    parser.add_argument("--performance-json", required=True)
    parser.add_argument("--dispatch-log-json", default="")
    parser.add_argument("--current-log", required=True)
    parser.add_argument("--previous-log", default="")
    parser.add_argument("--truth-report-md", required=True)
    parser.add_argument("--truth-snapshot-json", required=True)
    parser.add_argument("--window-comparison-json", required=True)
    parser.add_argument("--signals-last100-json", default="")
    parser.add_argument("--dispatch-log-out-json", default="")
    parser.add_argument("--invalidation-records-json", default="")
    return parser.parse_args()


def _timestamp_sort_key(record: object) -> tuple[int, float | str]:
    """Return sortable timestamp tuple: (priority_rank, parsed_timestamp_or_raw).

    Priority 2: valid numeric/ISO timestamp.
    Priority 1: unparseable timestamp string.
    Priority 0: missing/invalid timestamp field.
    """
    if not isinstance(record, dict):
        return (0, "")
    ts = record.get("timestamp")
    if isinstance(ts, (int, float)):
        return (2, float(ts))
    if isinstance(ts, str):
        try:
            return (2, datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp())
        except ValueError:
            return (1, ts)
    return (0, "")


def _write_json(path_str: str, payload: object) -> None:
    if not path_str:
        return
    out_path = Path(path_str)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    args = parse_args()

    runtime_health = load_json_file(Path(args.runtime_health_json), default={})
    heartbeat_text = Path(args.heartbeat_text).read_text(encoding="utf-8") if Path(args.heartbeat_text).exists() else ""
    records = load_json_file(Path(args.performance_json), default=[])
    if not isinstance(records, list):
        records = []
    latest_100_records = sorted(records, key=_timestamp_sort_key)[-100:]
    _write_json(args.signals_last100_json, latest_100_records)

    dispatch_log: list = []
    if args.dispatch_log_json:
        loaded_dispatch_log = load_json_file(Path(args.dispatch_log_json), default=[])
        if isinstance(loaded_dispatch_log, list):
            dispatch_log = loaded_dispatch_log
    _write_json(args.dispatch_log_out_json, dispatch_log[-50:])

    current_text = Path(args.current_log).read_text(encoding="utf-8") if Path(args.current_log).exists() else ""
    previous_text = Path(args.previous_log).read_text(encoding="utf-8") if args.previous_log and Path(args.previous_log).exists() else ""

    current_funnel = parse_path_funnel_from_logs(current_text, args.channel)
    previous_funnel = parse_path_funnel_from_logs(previous_text, args.channel)
    current_channel_funnel = parse_channel_funnel_from_logs(current_text, args.channel)
    previous_channel_funnel = parse_channel_funnel_from_logs(previous_text, args.channel)
    regime_distribution = parse_regime_distribution_from_logs(current_text)
    quiet_scalp_block = parse_quiet_scalp_block_from_logs(current_text, args.channel)
    confidence_gate_decisions = parse_confidence_gate_decisions_from_logs(current_text, args.channel)
    confidence_gate_components = parse_confidence_gate_components_from_logs(current_text, args.channel)
    log_parse_diagnostics = count_log_markers(current_text)

    invalidation_records: list = []
    if args.invalidation_records_json:
        loaded_records = load_json_file(Path(args.invalidation_records_json), default=[])
        if isinstance(loaded_records, list):
            invalidation_records = loaded_records
    invalidation_audit = summarize_invalidation_audit(invalidation_records)

    snapshot, comparison = build_snapshot(
        channel=args.channel,
        lookback_hours=args.lookback_hours,
        compare_previous_window=args.compare_previous_window,
        include_raw_json=args.include_raw_json,
        symbol_filter=args.symbol_filter,
        setup_filter=args.setup_filter,
        runtime_health=runtime_health,
        heartbeat_text=heartbeat_text,
        records=records,
        current_funnel=current_funnel,
        previous_funnel=previous_funnel,
        current_channel_funnel=current_channel_funnel,
        previous_channel_funnel=previous_channel_funnel,
        regime_distribution=regime_distribution,
        quiet_scalp_block=quiet_scalp_block,
        confidence_gate_decisions=confidence_gate_decisions,
        confidence_gate_components=confidence_gate_components,
        invalidation_audit=invalidation_audit,
        log_parse_diagnostics=log_parse_diagnostics,
        now_ts=time.time(),
    )

    report_md = format_truth_report_markdown(snapshot, comparison)

    Path(args.truth_report_md).write_text(report_md, encoding="utf-8")
    Path(args.truth_snapshot_json).write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
    Path(args.window_comparison_json).write_text(json.dumps(comparison, indent=2, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
