"""Autonomous strategy allocator (Layer D) — RECOMMENDATION MODE ONLY.

Reads the current market context (Layer A) × the measured Strategy×Context
edge matrix (Layer C) and decides which strategies it WOULD activate and how
it would weight them right now.  In this phase the decision is **persisted
for ops and consumed by nothing** — the owner watches the allocator's
judgement track real context/edge shifts before ever arming live promotion
(Phase 4, single owner master-arm).

The safety envelope (Layer E) is baked into the recommendation math itself,
not bolted on at promotion time: the allocator can never *recommend* more
than ``ALLOCATOR_MAX_CONCURRENT_STRATEGIES`` strategies nor a single-strategy
weight above ``ALLOCATOR_MAX_STRATEGY_WEIGHT``, so what the owner observes in
recommendation mode is exactly what live mode would be allowed to do.

Eligibility reuses the edge store's own Wilson-bounded verdict bands — a cell
must be POSITIVE/STRONG on real measured data to be recommended, and a
NEGATIVE cell is flagged for demotion.  Unknown/thin cells are un-promotable
by construction (verdict INSUFFICIENT_DATA), so a cold matrix recommends
nothing rather than guessing.

Pure functions over plain data — no I/O, no singletons; unit-testable.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from src.strategy_edge import (
    VERDICT_NEGATIVE,
    VERDICT_POSITIVE,
    VERDICT_STRONG,
)
from src.strategy_portfolio import is_context_aligned

# Alignment multipliers: a strategy recommended inside its design context gets
# a modest scoring boost; one measured-positive *outside* it is still eligible
# (the data outranks the tag) but ranked with a haircut.
_ALIGNED_MULT = 1.2
_MISALIGNED_MULT = 0.8


@dataclass(frozen=True)
class AllocatorLimits:
    """Safety-envelope bounds enforced inside the recommendation math."""

    max_concurrent: int
    max_weight: float

    @staticmethod
    def from_config() -> "AllocatorLimits":
        from config import (
            ALLOCATOR_MAX_CONCURRENT_STRATEGIES,
            ALLOCATOR_MAX_STRATEGY_WEIGHT,
        )

        return AllocatorLimits(
            max_concurrent=max(1, int(ALLOCATOR_MAX_CONCURRENT_STRATEGIES)),
            max_weight=min(1.0, max(0.01, float(ALLOCATOR_MAX_STRATEGY_WEIGHT))),
        )


def recommend(
    context_key: str,
    matrix: Dict[str, Dict],
    *,
    limits: Optional[AllocatorLimits] = None,
) -> Dict[str, List[Dict]]:
    """Rank the strategies the allocator would run in ``context_key`` now.

    Returns ``{"activate": [...], "demote": [...]}`` where each activate row is
    ``{strategy, weight, score, edge_r, n, verdict, aligned, reason}`` sorted by
    weight desc.  Weights are proportional to the alignment-adjusted edge,
    individually capped at ``limits.max_weight`` — capped surplus is left
    UNALLOCATED (flat is a position; the allocator never redistributes risk to
    weaker strategies just to sum to 1).
    """
    lim = limits or AllocatorLimits.from_config()
    eligible: List[Dict] = []
    demote: List[Dict] = []
    for cell in matrix.values():
        if cell.get("context_key") != context_key:
            continue
        verdict = cell.get("verdict")
        strategy = str(cell.get("strategy", ""))
        edge_r = cell.get("edge_r")
        row = {
            "strategy": strategy,
            "edge_r": edge_r,
            "n": int(cell.get("n", 0)),
            "n_emitted": int(cell.get("n_emitted", 0)),
            "verdict": verdict,
            "aligned": is_context_aligned(strategy, context_key),
        }
        if verdict in (VERDICT_STRONG, VERDICT_POSITIVE) and edge_r is not None:
            aligned = row["aligned"]
            mult = (
                _ALIGNED_MULT
                if aligned is True
                else _MISALIGNED_MULT
                if aligned is False
                else 1.0
            )
            row["score"] = float(edge_r) * mult
            row["reason"] = (
                f"{verdict} edge {float(edge_r):+.3f}R over n={row['n']}"
                + (
                    " (in design context)"
                    if aligned is True
                    else " (outside design context)"
                    if aligned is False
                    else ""
                )
            )
            eligible.append(row)
        elif verdict == VERDICT_NEGATIVE:
            row["reason"] = (
                f"NEGATIVE edge {float(edge_r):+.3f}R over n={row['n']} — "
                "would demote in this context"
                if edge_r is not None
                else "NEGATIVE verdict — would demote in this context"
            )
            demote.append(row)

    eligible.sort(key=lambda r: r["score"], reverse=True)
    active = eligible[: lim.max_concurrent]
    total_score = sum(r["score"] for r in active)
    for r in active:
        raw = (r["score"] / total_score) if total_score > 0 else 0.0
        r["weight"] = round(min(raw, lim.max_weight), 4)
    demote.sort(key=lambda r: (r["edge_r"] if r["edge_r"] is not None else 0.0))
    return {"activate": active, "demote": demote}


def build_recommendation_payload(
    *,
    context_key: str,
    matrix: Dict[str, Dict],
    limits: Optional[AllocatorLimits] = None,
    now_ts: Optional[float] = None,
) -> Dict:
    """The ``data/strategy_allocations.json`` payload ops renders."""
    lim = limits or AllocatorLimits.from_config()
    rec = recommend(context_key, matrix, limits=lim)
    ts = now_ts if now_ts is not None else time.time()
    cells_in_context = sum(
        1 for c in matrix.values() if c.get("context_key") == context_key
    )
    return {
        "generated_at": ts,
        "generated_at_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
        "mode": "RECOMMENDATION_ONLY",
        "context_key": context_key,
        "activate": rec["activate"],
        "demote": rec["demote"],
        "unallocated_weight": round(
            max(0.0, 1.0 - sum(r.get("weight", 0.0) for r in rec["activate"])), 4
        ),
        "cells_in_context": cells_in_context,
        "limits": {
            "max_concurrent_strategies": lim.max_concurrent,
            "max_strategy_weight": lim.max_weight,
        },
    }
