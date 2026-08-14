"""Tests for the pair-cohort dimension (src/pair_cohort.py) and cohort-aware emission."""
from __future__ import annotations

from dataclasses import replace

from src.context_emission_policy import PolicyParams, effective_floor
from src.pair_cohort import (
    COHORT_ALTCOIN,
    COHORT_MAJOR,
    COHORT_MIDCAP,
    classify_cohort,
    cohort_context_key,
)
from src.strategy_edge import StrategyEdgeStore, StrategyOutcome

CTX = "OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL"
BASE = 65.0


def test_classify_cohort_by_volume() -> None:
    # Unknown symbol → volume thresholds decide.
    assert classify_cohort("ZZZUNKNOWNUSDT", 600_000_000) == COHORT_MAJOR
    assert classify_cohort("ZZZUNKNOWNUSDT", 80_000_000) == COHORT_MIDCAP
    assert classify_cohort("ZZZUNKNOWNUSDT", 1_000_000) == COHORT_ALTCOIN
    assert classify_cohort("ZZZUNKNOWNUSDT", 0.0) == COHORT_ALTCOIN


def test_cohort_context_key_composition() -> None:
    assert cohort_context_key(CTX, COHORT_MAJOR) == f"{CTX}/MAJOR"
    assert cohort_context_key(CTX, "") == CTX  # empty cohort → base key
    assert cohort_context_key("", COHORT_MAJOR) == ""


def _store() -> StrategyEdgeStore:
    return StrategyEdgeStore(persist_path="")


def _feed(store, strat, ctx, wins, losses) -> None:
    for _ in range(wins):
        store.record(StrategyOutcome(strat, ctx, "LONG", True, 1.0, 1.0, 2.0, "emitted"), persist=False)
    for _ in range(losses):
        store.record(StrategyOutcome(strat, ctx, "LONG", False, -1.0, -1.0, 0.0, "emitted"), persist=False)


_P_COHORT = PolicyParams(True, True, 60.0, 5.0, 3.0, 30, True, cohort_aware=True)
_P_BASE = PolicyParams(True, True, 60.0, 5.0, 3.0, 30, True, cohort_aware=False)


def test_cohort_aware_prefers_cohort_cell() -> None:
    st = _store()
    cohort_ctx = cohort_context_key(CTX, COHORT_MAJOR)
    # Base cell NEGATIVE, but the MAJOR-cohort cell is STRONG → cohort wins.
    _feed(st, "SR_FLIP_RETEST", CTX, wins=5, losses=25)
    _feed(st, "SR_FLIP_RETEST", cohort_ctx, wins=30, losses=0)
    d = effective_floor("SR_FLIP_RETEST", CTX, BASE, cohort=COHORT_MAJOR, store=st, params=_P_COHORT)
    assert d.verdict == "STRONG"
    assert d.suppressed is False
    assert d.effective_floor == 60.0


def test_cohort_thin_falls_back_to_base_cell() -> None:
    st = _store()
    # Cohort cell has no data; base cell STRONG → falls back to base, still relaxes.
    _feed(st, "QUIET_COMPRESSION_BREAK", CTX, wins=30, losses=0)
    d = effective_floor(
        "QUIET_COMPRESSION_BREAK", CTX, BASE, cohort=COHORT_ALTCOIN, store=st, params=_P_COHORT
    )
    assert d.verdict == "STRONG"
    assert d.effective_floor == 60.0


def test_cohort_ignored_when_not_cohort_aware() -> None:
    st = _store()
    cohort_ctx = cohort_context_key(CTX, COHORT_MAJOR)
    # MAJOR-cohort STRONG, base cell absent — with cohort_aware OFF, the base
    # lookup finds nothing → no relaxation.
    _feed(st, "SR_FLIP_RETEST", cohort_ctx, wins=30, losses=0)
    # Warmup off: this test is about which CELL is consulted, and the warmup
    # allowance would relax the floor for the resulting unmeasured lookup —
    # true, deliberate, and nothing to do with cohort awareness.
    d = effective_floor(
        "SR_FLIP_RETEST", CTX, BASE, cohort=COHORT_MAJOR, store=st,
        params=replace(_P_BASE, warmup_enabled=False),
    )
    assert d.effective_floor == BASE  # cohort cell not consulted
    assert d.verdict != "STRONG"      # the cohort's STRONG never leaked in
