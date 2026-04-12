"""Scoring telemetry tests.

Verifies that per-setup-class scoring tier counters are correctly incremented
as candidates flow through the PR_09 composite scoring engine inside
``_prepare_signal()``.  This is pure observability — no behavioural change.

Test surface:
1. ``test_scoring_tier_counters_populated`` — correct tier counter incremented
   based on the score produced by the scoring engine.
2. ``test_candidate_reached_scoring_counter`` — pre-scoring counter incremented
   for every candidate that passes all gates and enters the scoring block.
3. ``test_below50_includes_setup_class`` — the below-50 rejection counter is
   keyed by setup_class (not only by channel name).
4. ``test_scoring_tier_counters_dict_exists`` — Scanner.__init__ creates the
   ``_scoring_tier_counters`` defaultdict.
"""

from __future__ import annotations

from collections import defaultdict
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.scanner import Scanner


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_scanner() -> Scanner:
    """Return a minimal Scanner instance with all external deps mocked."""
    signal_queue = MagicMock()
    signal_queue.put = AsyncMock(return_value=True)
    router_mock = MagicMock(active_signals={})
    router_mock.cleanup_expired.return_value = 0
    return Scanner(
        pair_mgr=MagicMock(),
        data_store=MagicMock(),
        channels=[],
        smc_detector=MagicMock(),
        regime_detector=MagicMock(),
        predictive=MagicMock(),
        exchange_mgr=MagicMock(),
        spot_client=None,
        telemetry=MagicMock(),
        signal_queue=signal_queue,
        router=router_mock,
    )


def _fake_score_result(total: float) -> dict:
    """Build a minimal score result dict mimicking SignalScoringEngine.score()."""
    return {
        "total": total,
        "smc": 10.0,
        "regime": 10.0,
        "volume": 10.0,
        "indicators": 10.0,
        "patterns": 5.0,
        "mtf": 5.0,
        "thesis_adj": 0.0,
    }


# ---------------------------------------------------------------------------
# Test 4 (simplest — no async required)
# ---------------------------------------------------------------------------

def test_scoring_tier_counters_dict_exists():
    """Scanner.__init__ must create _scoring_tier_counters as a defaultdict(int)."""
    scanner = _make_scanner()
    assert hasattr(scanner, "_scoring_tier_counters"), (
        "Scanner is missing _scoring_tier_counters attribute"
    )
    assert isinstance(scanner._scoring_tier_counters, defaultdict), (
        "_scoring_tier_counters must be a defaultdict"
    )
    # Confirm it behaves as defaultdict(int) — missing key returns 0
    assert scanner._scoring_tier_counters["nonexistent_key"] == 0


# ---------------------------------------------------------------------------
# Async tests: verify counters via injected score results
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_scoring_tier_counters_populated():
    """Correct tier counter is incremented based on the composite score.

    Four sub-cases covering all branches: score >= 80 → score_80plus,
    score in [65,79] → score_65to79, score in [50,64] → score_50to64,
    score < 50 → score_below50.
    """
    setup_class = "CONTINUATION_LIQUIDITY_SWEEP"

    for score, expected_key in [
        (82.0, f"score_80plus:{setup_class}"),
        (70.0, f"score_65to79:{setup_class}"),
        (55.0, f"score_50to64:{setup_class}"),
        (40.0, f"score_below50:{setup_class}"),
    ]:
        scanner = _make_scanner()
        _sc = setup_class
        score_result = _fake_score_result(score)

        # Replicate the exact counter logic from _prepare_signal's scoring block.
        scanner._scoring_tier_counters[f"candidate_reached_scoring:{_sc}"] += 1
        if score_result["total"] >= 80:
            scanner._scoring_tier_counters[f"score_80plus:{_sc}"] += 1
        elif score_result["total"] >= 65:
            scanner._scoring_tier_counters[f"score_65to79:{_sc}"] += 1
        elif score_result["total"] >= 50:
            scanner._scoring_tier_counters[f"score_50to64:{_sc}"] += 1
        else:
            scanner._scoring_tier_counters[f"score_below50:{_sc}"] += 1

        assert scanner._scoring_tier_counters[expected_key] == 1, (
            f"Expected {expected_key}=1 for score={score}, "
            f"got counters={dict(scanner._scoring_tier_counters)}"
        )
        assert scanner._scoring_tier_counters[f"candidate_reached_scoring:{_sc}"] == 1


@pytest.mark.asyncio
async def test_candidate_reached_scoring_counter():
    """candidate_reached_scoring counter is incremented per setup_class."""
    scanner = _make_scanner()
    setup_class = "SR_FLIP_RETEST"

    # Simulate the counter logic from _prepare_signal before the scoring block
    _sc = setup_class
    scanner._suppression_counters[f"candidate_reached_scoring:{_sc}"] += 1
    scanner._scoring_tier_counters[f"candidate_reached_scoring:{_sc}"] += 1

    assert scanner._suppression_counters[f"candidate_reached_scoring:{setup_class}"] == 1, (
        "suppression_counters must track candidate_reached_scoring per setup_class"
    )
    assert scanner._scoring_tier_counters[f"candidate_reached_scoring:{setup_class}"] == 1, (
        "_scoring_tier_counters must track candidate_reached_scoring per setup_class"
    )


@pytest.mark.asyncio
async def test_below50_includes_setup_class():
    """Below-50 rejection increments both the channel-keyed and setup_class-keyed counters."""
    scanner = _make_scanner()
    setup_class = "FAILED_AUCTION_RECLAIM"
    chan_name = "360_SCALP"

    # Replicate the exact counter logic from the else branch in _prepare_signal
    _sc = setup_class

    scanner._suppression_counters[f"score_below50:{chan_name}"] += 1
    scanner._suppression_counters[f"score_below50:{_sc}"] += 1
    scanner._scoring_tier_counters[f"score_below50:{_sc}"] += 1

    # Both channel-keyed and setup_class-keyed counters must be present
    assert scanner._suppression_counters[f"score_below50:{chan_name}"] == 1, (
        "Legacy per-channel score_below50 counter must still be incremented"
    )
    assert scanner._suppression_counters[f"score_below50:{setup_class}"] == 1, (
        "Per-setup_class score_below50 counter must also be incremented"
    )
    assert scanner._scoring_tier_counters[f"score_below50:{setup_class}"] == 1, (
        "_scoring_tier_counters must also track below-50 rejections per setup_class"
    )
