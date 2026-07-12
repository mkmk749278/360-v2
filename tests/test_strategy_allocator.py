"""Tests for the allocator's recommendation math (src/strategy_allocator.py, Layer D)."""
from __future__ import annotations

from src.strategy_allocator import (
    AllocatorLimits,
    build_recommendation_payload,
    recommend,
)

CTX = "OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL"


def _cell(strategy: str, edge_r, verdict: str, n: int = 20, ctx: str = CTX) -> dict:
    return {
        "strategy": strategy,
        "context_key": ctx,
        "n": n,
        "n_emitted": n // 2,
        "edge_r": edge_r,
        "verdict": verdict,
    }


def test_empty_matrix_recommends_nothing() -> None:
    rec = recommend(CTX, {}, limits=AllocatorLimits(6, 0.35))
    assert rec["activate"] == [] and rec["demote"] == []


def test_max_concurrent_cap_binds() -> None:
    matrix = {
        f"S{i}|{CTX}": _cell(f"S{i}", 0.10 + i * 0.01, "POSITIVE") for i in range(8)
    }
    rec = recommend(CTX, matrix, limits=AllocatorLimits(3, 0.9))
    assert len(rec["activate"]) == 3
    # Highest score first.
    scores = [r["score"] for r in rec["activate"]]
    assert scores == sorted(scores, reverse=True)


def test_max_weight_cap_binds_and_surplus_stays_unallocated() -> None:
    matrix = {f"ONLY|{CTX}": _cell("ONLY", 0.30, "STRONG")}
    payload = build_recommendation_payload(
        context_key=CTX, matrix=matrix, limits=AllocatorLimits(6, 0.35)
    )
    assert payload["activate"][0]["weight"] == 0.35  # capped, not 1.0
    assert payload["unallocated_weight"] == 0.65  # flat is a position


def test_negative_cells_flagged_for_demotion_not_activation() -> None:
    matrix = {
        f"GOOD|{CTX}": _cell("GOOD", 0.20, "STRONG"),
        f"BAD|{CTX}": _cell("BAD", -0.15, "NEGATIVE"),
    }
    rec = recommend(CTX, matrix, limits=AllocatorLimits(6, 0.35))
    assert [r["strategy"] for r in rec["activate"]] == ["GOOD"]
    assert [r["strategy"] for r in rec["demote"]] == ["BAD"]


def test_insufficient_and_flat_cells_are_ignored() -> None:
    matrix = {
        f"THIN|{CTX}": _cell("THIN", None, "INSUFFICIENT_DATA", n=3),
        f"MEH|{CTX}": _cell("MEH", 0.01, "FLAT"),
    }
    rec = recommend(CTX, matrix, limits=AllocatorLimits(6, 0.35))
    assert rec["activate"] == [] and rec["demote"] == []


def test_other_context_cells_do_not_leak() -> None:
    matrix = {
        "ELSEWHERE|ASIA/QUIET/COMPRESSED/BTC_NEUTRAL": _cell(
            "ELSEWHERE", 0.5, "STRONG", ctx="ASIA/QUIET/COMPRESSED/BTC_NEUTRAL"
        ),
    }
    rec = recommend(CTX, matrix, limits=AllocatorLimits(6, 0.35))
    assert rec["activate"] == []


def test_alignment_bonus_ranks_in_context_strategy_first() -> None:
    # Equal measured edge; BREAKOUT_RETEST is designed for OVERLAP/MARKUP,
    # RANGE_REJECTION is not — the aligned one must rank first.
    matrix = {
        f"BREAKOUT_RETEST|{CTX}": _cell("BREAKOUT_RETEST", 0.10, "POSITIVE"),
        f"RANGE_REJECTION|{CTX}": _cell("RANGE_REJECTION", 0.10, "POSITIVE"),
    }
    rec = recommend(CTX, matrix, limits=AllocatorLimits(6, 0.9))
    assert [r["strategy"] for r in rec["activate"]] == [
        "BREAKOUT_RETEST",
        "RANGE_REJECTION",
    ]
    assert rec["activate"][0]["aligned"] is True
    assert rec["activate"][1]["aligned"] is False


def test_payload_is_recommendation_only_and_carries_limits() -> None:
    payload = build_recommendation_payload(
        context_key=CTX, matrix={}, limits=AllocatorLimits(4, 0.25)
    )
    assert payload["mode"] == "RECOMMENDATION_ONLY"
    assert payload["context_key"] == CTX
    assert payload["limits"] == {
        "max_concurrent_strategies": 4,
        "max_strategy_weight": 0.25,
    }
    assert payload["generated_at_iso"].endswith("Z")
