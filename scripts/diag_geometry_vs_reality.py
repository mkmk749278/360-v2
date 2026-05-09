"""Geometry-vs-reality diagnostic for closed scalp signals.

Answers the question raised by truth-report 2026-05-09: "Of the 0% win rate
across 27 closed signals, is TP1 set too far for the actual move sizes
this market is producing?"

For each setup_class, dumps:

* Per-signal: TP1 distance from entry (% favorable), MFE %, MAE %, terminal
  status, time-to-terminal.
* Per-path summary: mean / median TP1 distance, mean MFE, mean MFE/TP1
  ratio (the key diagnostic — if avg ≪ 0.5, TP1 is geometrically too
  far for the realised move sizes), terminal status mix.

Reads ``data/signal_history.json`` (atomic-write JSON store; #346) so it
does not require Redis or a running engine.  Safe to run on the VPS via
``docker compose exec engine python /app/scripts/diag_geometry_vs_reality.py``.

Usage:
    python scripts/diag_geometry_vs_reality.py [--limit N] [--path PATH]
        [--history PATH]

    --limit:  only consider the most recent N closed signals per path
              (default: 50, matching the truth-report focus window).
    --path:   filter to one setup_class (e.g. SR_FLIP_RETEST).
    --history: override the on-disk history path.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from collections import defaultdict, Counter
from datetime import datetime
from typing import Any, Dict, List, Optional


_DEFAULT_HISTORY_PATH = os.environ.get("SIGNAL_HISTORY_PATH", "data/signal_history.json")

# Statuses that count as "closed" — every status that means the lifecycle
# is over.  Mirror of ``trade_monitor._TERMINAL_STATUSES`` minus TP1_HIT/
# TP2_HIT (those signals stay active for higher-TP progression and are
# only fully closed at SL/TP3/EXPIRED).
_TERMINAL_STATUSES = frozenset({
    "SL_HIT",
    "BREAKEVEN_EXIT",
    "PROFIT_LOCKED",
    "INVALIDATED",
    "EXPIRED",
    "CANCELLED",
    "FULL_TP_HIT",
    "TP3_HIT",
    "CLOSED",
})


def _load_history(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        print(f"history file not found at {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        print(f"unexpected history format (not a list)", file=sys.stderr)
        sys.exit(1)
    return raw


def _is_closed(rec: Dict[str, Any]) -> bool:
    status = str(rec.get("status") or "").upper()
    return status in _TERMINAL_STATUSES


def _direction_value(rec: Dict[str, Any]) -> str:
    d = rec.get("direction")
    if isinstance(d, dict) and "value" in d:
        return str(d["value"]).upper()
    return str(d or "").upper()


def _signed_pct(entry: float, target: float, direction: str) -> Optional[float]:
    """% favorable distance from entry to target.  Positive when target is
    in the signal's direction; negative if target is on the wrong side."""
    if entry <= 0 or target <= 0:
        return None
    raw = (target - entry) / entry * 100.0
    return raw if direction == "LONG" else -raw


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _terminal_age_sec(rec: Dict[str, Any]) -> Optional[float]:
    created = _parse_dt(rec.get("timestamp"))
    closed = _parse_dt(rec.get("terminal_outcome_timestamp"))
    if created is None or closed is None:
        return None
    return (closed - created).total_seconds()


def _format_pct(value: Optional[float], width: int = 7) -> str:
    if value is None:
        return "n/a".rjust(width)
    return f"{value:+.2f}%".rjust(width)


def _format_ratio(value: Optional[float], width: int = 6) -> str:
    if value is None:
        return "n/a".rjust(width)
    return f"{value:.2f}".rjust(width)


def _format_sec(value: Optional[float], width: int = 7) -> str:
    if value is None:
        return "n/a".rjust(width)
    return f"{value/60.0:.1f}m".rjust(width)


def _summarise(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate stats for a list of closed signals belonging to one path."""
    tp1_dists: List[float] = []
    mfe_pcts: List[float] = []
    mae_pcts: List[float] = []
    mfe_over_tp1: List[float] = []
    durations: List[float] = []
    status_counter: Counter = Counter()

    for rec in records:
        entry = float(rec.get("entry") or 0.0)
        tp1 = float(rec.get("tp1") or 0.0)
        direction = _direction_value(rec)
        tp1_dist = _signed_pct(entry, tp1, direction) if entry > 0 and tp1 > 0 else None
        mfe = float(rec.get("max_favorable_excursion_pct") or 0.0)
        mae = float(rec.get("max_adverse_excursion_pct") or 0.0)
        if tp1_dist is not None and tp1_dist > 0:
            tp1_dists.append(tp1_dist)
            mfe_over_tp1.append(mfe / tp1_dist if tp1_dist > 0 else 0.0)
        mfe_pcts.append(mfe)
        mae_pcts.append(mae)
        age = _terminal_age_sec(rec)
        if age is not None:
            durations.append(age)
        status_counter[str(rec.get("status") or "?").upper()] += 1

    def _mean(seq):
        return statistics.fmean(seq) if seq else None

    def _median(seq):
        return statistics.median(seq) if seq else None

    return {
        "n": len(records),
        "tp1_dist_mean": _mean(tp1_dists),
        "tp1_dist_median": _median(tp1_dists),
        "mfe_mean": _mean(mfe_pcts),
        "mfe_median": _median(mfe_pcts),
        "mae_mean": _mean(mae_pcts),
        "mae_median": _median(mae_pcts),
        "mfe_over_tp1_mean": _mean(mfe_over_tp1),
        "mfe_over_tp1_median": _median(mfe_over_tp1),
        "duration_mean": _mean(durations),
        "duration_median": _median(durations),
        "status_mix": dict(status_counter),
    }


def _print_path(path_name: str, records: List[Dict[str, Any]]) -> None:
    summary = _summarise(records)
    print(f"\n=== {path_name} (n={summary['n']}) ===")
    print(
        "  TP1 dist:  mean {} | median {}".format(
            _format_pct(summary["tp1_dist_mean"]),
            _format_pct(summary["tp1_dist_median"]),
        )
    )
    print(
        "  MFE:       mean {} | median {}".format(
            _format_pct(summary["mfe_mean"]),
            _format_pct(summary["mfe_median"]),
        )
    )
    print(
        "  MAE:       mean {} | median {}".format(
            _format_pct(summary["mae_mean"]),
            _format_pct(summary["mae_median"]),
        )
    )
    # The killer diagnostic: if avg MFE/TP1 << 0.5, TP1 is geometrically
    # unreachable in the move sizes this market is producing.
    print(
        "  MFE/TP1:   mean {} | median {}   <-- if << 0.50, TP1 too far".format(
            _format_ratio(summary["mfe_over_tp1_mean"]),
            _format_ratio(summary["mfe_over_tp1_median"]),
        )
    )
    print(
        "  Duration:  mean {} | median {}".format(
            _format_sec(summary["duration_mean"]),
            _format_sec(summary["duration_median"]),
        )
    )
    mix = summary["status_mix"]
    if mix:
        mix_str = " ".join(f"{k}={v}" for k, v in sorted(mix.items()))
        print(f"  Status:    {mix_str}")

    # Per-signal table — newest first.
    print("\n  Per-signal (most recent first):")
    print(
        "  {:<14} {:<8} {:>7} {:>7} {:>7} {:>7} {:>14}".format(
            "symbol", "dir", "tp1_d%", "mfe%", "mae%", "ratio", "status"
        )
    )
    sorted_records = sorted(
        records,
        key=lambda r: r.get("terminal_outcome_timestamp") or r.get("timestamp") or "",
        reverse=True,
    )
    for rec in sorted_records[:20]:
        symbol = str(rec.get("symbol") or "?")[:14]
        direction = _direction_value(rec)[:5]
        entry = float(rec.get("entry") or 0.0)
        tp1 = float(rec.get("tp1") or 0.0)
        tp1_dist = _signed_pct(entry, tp1, direction)
        mfe = float(rec.get("max_favorable_excursion_pct") or 0.0)
        mae = float(rec.get("max_adverse_excursion_pct") or 0.0)
        ratio = (mfe / tp1_dist) if tp1_dist and tp1_dist > 0 else None
        status = str(rec.get("status") or "?")[:14]
        print(
            "  {:<14} {:<8} {} {} {} {}   {}".format(
                symbol, direction,
                _format_pct(tp1_dist),
                _format_pct(mfe),
                _format_pct(mae),
                _format_ratio(ratio),
                status,
            )
        )
    if len(sorted_records) > 20:
        print(f"  ... ({len(sorted_records) - 20} older signals not shown)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limit", type=int, default=50,
        help="most recent N closed signals per path (default: 50)",
    )
    parser.add_argument(
        "--path", type=str, default=None,
        help="filter to one setup_class (e.g. SR_FLIP_RETEST)",
    )
    parser.add_argument(
        "--history", type=str, default=_DEFAULT_HISTORY_PATH,
        help=f"history file path (default: {_DEFAULT_HISTORY_PATH})",
    )
    args = parser.parse_args()

    raw = _load_history(args.history)
    closed = [r for r in raw if isinstance(r, dict) and _is_closed(r)]

    print(f"Loaded {len(raw)} records from {args.history}; {len(closed)} closed.")
    if not closed:
        print("No closed signals to analyse.")
        return

    # Group by setup_class.
    by_path: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in closed:
        path = str(rec.get("setup_class") or "UNCLASSIFIED").upper()
        if args.path and path != args.path.upper():
            continue
        by_path[path].append(rec)

    if not by_path:
        print(f"No closed signals matched --path={args.path}")
        return

    # Cap each path to the most recent ``--limit``.
    for path, recs in by_path.items():
        recs.sort(
            key=lambda r: r.get("terminal_outcome_timestamp") or r.get("timestamp") or "",
            reverse=True,
        )
        by_path[path] = recs[: args.limit]

    # Print paths sorted by sample count desc.
    for path in sorted(by_path.keys(), key=lambda p: -len(by_path[p])):
        _print_path(path, by_path[path])


if __name__ == "__main__":
    main()
