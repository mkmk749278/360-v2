#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.runtime_truth_report import (
    build_snapshot,
    format_truth_report_markdown,
    load_json_file,
    parse_path_funnel_from_logs,
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
    parser.add_argument("--current-log", required=True)
    parser.add_argument("--previous-log", default="")
    parser.add_argument("--truth-report-md", required=True)
    parser.add_argument("--truth-snapshot-json", required=True)
    parser.add_argument("--window-comparison-json", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    runtime_health = load_json_file(Path(args.runtime_health_json), default={})
    heartbeat_text = Path(args.heartbeat_text).read_text(encoding="utf-8") if Path(args.heartbeat_text).exists() else ""
    records = load_json_file(Path(args.performance_json), default=[])
    if not isinstance(records, list):
        records = []

    current_text = Path(args.current_log).read_text(encoding="utf-8") if Path(args.current_log).exists() else ""
    previous_text = Path(args.previous_log).read_text(encoding="utf-8") if args.previous_log and Path(args.previous_log).exists() else ""

    current_funnel = parse_path_funnel_from_logs(current_text, args.channel)
    previous_funnel = parse_path_funnel_from_logs(previous_text, args.channel)

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
        now_ts=time.time(),
    )

    report_md = format_truth_report_markdown(snapshot, comparison)

    Path(args.truth_report_md).write_text(report_md, encoding="utf-8")
    Path(args.truth_snapshot_json).write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
    Path(args.window_comparison_json).write_text(json.dumps(comparison, indent=2, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
