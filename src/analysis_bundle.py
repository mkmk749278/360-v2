"""Analysis-bundle builders for the ``monitor-logs`` git dead-drop.

**Why this exists (2026-07-20):** the owner and CTE analyse the signal system
from three artefacts the ops Strategy Lab exports as CSV — the full per-cell
edge matrix, per-setup performance, and the per-gate suppression verdicts.
Getting them into an analysis session meant a manual browser export + upload
every time.

The nightly ``vps-monitor`` workflow already publishes ``truth_snapshot.json``
to the ``monitor-logs`` branch, but that snapshot only carries the *summarised*
edge matrix (per-strategy best/worst cell) — not the full ~700-cell matrix the
allocator actually routes on. This module emits the missing machine-readable
artefacts alongside it, so any session can read them straight from git
(``git show origin/monitor-logs:monitor/report/analysis/…``) with **no token
and no live network to ops**. The ops ``/api/v1/analysis-bundle`` endpoint is
the live/on-demand sibling (it can also compute the profit exit-replay, which
needs the ops-only simulator); this is the secretless scheduled channel.

Pure functions only — every input arrives as a parameter, so the tests exercise
them on plain dicts with no I/O. The per-setup outcome classification mirrors
``360ce-ops`` ``app/routes/performance.py:_classify_outcome`` verbatim so the
dead-drop's ``performance_setup`` numbers match what the ops page renders; if
one side changes, the other must change with it.
"""
from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

# Column order for the flattened edge matrix — mirrors the ops Strategy Lab
# ``export.csv`` header (minus ``aligned``, which is an ops-side affinity
# derivation the engine's edge store does not carry). Extra engine-native
# columns (mfe_capture, last_updated) trail the shared prefix.
STRATEGY_MATRIX_COLUMNS: List[str] = [
    "strategy",
    "context_key",
    "n",
    "n_emitted",
    "n_suppressed",
    "n_shadow",
    "win_rate",
    "avg_r",
    "avg_pnl_pct",
    "edge_r",
    "verdict",
    "mfe_capture",
    "last_updated",
]

PERFORMANCE_SETUP_COLUMNS: List[str] = [
    "setup",
    "n",
    "wins",
    "losses",
    "neutral",
    "win_rate_pct",
    "avg_pnl_pct",
]


def _num(value: Any) -> Optional[float]:
    """Coerce to float, or None when absent/unparseable (keeps CSV cells empty
    rather than emitting a lie like 0.0 for a genuinely-missing edge)."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def flatten_strategy_matrix(matrix: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten ``StrategyEdgeStore.matrix()`` into stable per-cell rows.

    ``matrix`` is keyed ``"STRATEGY|context_key"`` → per-cell stat dict. Output
    is one row per cell, sorted strategy asc then edge_r desc (cells without a
    scored edge sort last) so the CSV reads deterministically. ``edge_r`` /
    ``verdict`` stay ``None`` when the cell is below the sample floor — never
    coerced to a fake zero.
    """
    rows: List[Dict[str, Any]] = []
    for cell in matrix.values():
        if not isinstance(cell, dict):
            continue
        rows.append(
            {
                "strategy": str(cell.get("strategy") or ""),
                "context_key": str(cell.get("context_key") or ""),
                "n": int(cell.get("n", 0) or 0),
                "n_emitted": int(cell.get("n_emitted", 0) or 0),
                "n_suppressed": int(cell.get("n_suppressed", 0) or 0),
                "n_shadow": int(cell.get("n_shadow", 0) or 0),
                "win_rate": _num(cell.get("win_rate")),
                "avg_r": _num(cell.get("avg_r")),
                "avg_pnl_pct": _num(cell.get("avg_pnl_pct")),
                "edge_r": _num(cell.get("edge_r")),
                "verdict": str(cell.get("verdict") or ""),
                "mfe_capture": _num(cell.get("mfe_capture")),
                "last_updated": str(cell.get("last_updated") or ""),
            }
        )

    def _sort_key(row: Dict[str, Any]) -> tuple:
        edge = row.get("edge_r")
        # (strategy asc, scored-before-unscored, edge desc)
        return (row["strategy"], 0 if edge is not None else 1, -(edge or 0.0))

    rows.sort(key=_sort_key)
    return rows


def _classify_outcome(label: str) -> str:
    """Mirror of ``360ce-ops`` ``performance.py:_classify_outcome``.

    PROFIT_LOCKED is the engine's dominant positive terminal status (pre-TP
    banked + residual closed in profit); it must count as a win, matching the
    ops page. Keep this in lock-step with the ops copy.
    """
    up = (label or "").upper()
    if "TP" in up or "WIN" in up or "PROFIT" in up:
        return "win"
    if "SL" in up or "LOSS" in up or "STOP" in up:
        return "loss"
    return "neutral"


def aggregate_performance_by_setup(records: Sequence[Any]) -> List[Dict[str, Any]]:
    """Per-setup win/loss/neutral + avg PnL, matching the ops Performance page.

    Reads the same fields the ops ``_aggregate`` reads off
    ``data/signal_performance.json`` (``setup_class``; outcome from
    ``outcome_label`` else ``status``; ``pnl_pct`` else ``pnlPct``). Sorted by
    sample count desc.
    """
    buckets: Dict[str, Dict[str, float]] = {}
    for r in records:
        if not isinstance(r, dict):
            continue
        setup = str(r.get("setup_class") or "UNKNOWN")
        outcome = _classify_outcome(r.get("outcome_label") or r.get("status") or "")
        pnl = _num(r.get("pnl_pct") if r.get("pnl_pct") is not None else r.get("pnlPct")) or 0.0
        b = buckets.setdefault(
            setup, {"n": 0, "wins": 0, "losses": 0, "neutral": 0, "pnl_sum": 0.0}
        )
        b["n"] += 1
        b["pnl_sum"] += pnl
        b[{"win": "wins", "loss": "losses", "neutral": "neutral"}[outcome]] += 1

    rows: List[Dict[str, Any]] = []
    for setup, b in buckets.items():
        n = int(b["n"]) or 1
        rows.append(
            {
                "setup": setup,
                "n": int(b["n"]),
                "wins": int(b["wins"]),
                "losses": int(b["losses"]),
                "neutral": int(b["neutral"]),
                "win_rate_pct": round(b["wins"] / n * 100.0, 1),
                "avg_pnl_pct": round(b["pnl_sum"] / n, 4),
            }
        )
    rows.sort(key=lambda row: row["n"], reverse=True)
    return rows


def rows_to_csv(rows: Sequence[Dict[str, Any]], columns: Sequence[str]) -> str:
    """Render rows to CSV text with a fixed column order. ``None`` → empty cell."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(columns), extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({c: ("" if row.get(c) is None else row.get(c)) for c in columns})
    return buf.getvalue()


def build_bundle_index(
    *,
    generated_at_ts: float,
    lookback_hours: int,
    channel: str,
    matrix_rows: Sequence[Dict[str, Any]],
    performance_rows: Sequence[Dict[str, Any]],
    suppression_audit: Dict[str, Any],
    git_sha: str = "",
    artifacts: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Assemble the ``bundle.json`` index: metadata + a compact headline rollup
    so a reader knows what the drop contains and its top signals without
    parsing every artefact.
    """
    scored = [r for r in matrix_rows if r.get("edge_r") is not None]
    scored_sorted = sorted(scored, key=lambda r: r["edge_r"], reverse=True)

    def _cell(r: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "strategy": r["strategy"],
            "context_key": r["context_key"],
            "edge_r": r["edge_r"],
            "n": r["n"],
            "verdict": r["verdict"],
        }

    # Gate-verdict rollup from the suppression audit. ``summarize_suppression_audit``
    # returns ``by_gate`` as a dict {gate_name -> {verdict, ev_per_suppression_r, …}}
    # (see src/suppression_audit.py:compute_gate_suppression_metrics).
    by_gate = suppression_audit.get("by_gate") if isinstance(suppression_audit, dict) else None
    verdict_counts: Dict[str, int] = {}
    drop_gates: List[str] = []
    gate_count = 0
    if isinstance(by_gate, dict):
        gate_count = len(by_gate)
        for name, g in by_gate.items():
            if not isinstance(g, dict):
                continue
            v = str(g.get("verdict") or "").upper()
            if v:
                verdict_counts[v] = verdict_counts.get(v, 0) + 1
            if v == "DROP" and name:
                drop_gates.append(str(name))

    return {
        "generated_at": datetime.fromtimestamp(generated_at_ts, tz=timezone.utc).isoformat(),
        "generated_at_ts": generated_at_ts,
        "lookback_hours": lookback_hours,
        "channel": channel,
        "git_sha": git_sha,
        "source": "vps-monitor/analysis_bundle",
        "note": (
            "Secretless engine dead-drop. Live tunable values + profit exit-replay "
            "come from ops GET /api/v1/analysis-bundle (they need the ops-only simulator)."
        ),
        "artifacts": list(artifacts or []),
        "counts": {
            "strategy_matrix_cells": len(matrix_rows),
            "strategy_matrix_scored_cells": len(scored),
            "performance_setups": len(performance_rows),
            "suppression_gates": gate_count,
        },
        "headlines": {
            "strongest_cells": [_cell(r) for r in scored_sorted[:5]],
            "weakest_cells": [_cell(r) for r in scored_sorted[-5:][::-1]],
            "gate_verdict_counts": verdict_counts,
            "drop_gates": drop_gates,
        },
    }
