"""The warmup allowance — let an unmeasured cell deliver so it can be measured.

Owner, 2026-08-14: *"let them deliver first, don't wait for 20 to 30, after
reaching desirable count then start sort out."*

The absorbing state it breaks: ``strategy_edge`` returns INSUFFICIENT while
``edge is None``, and edge is None until the sample floor is met — so a starved
path never earns the relax, rarely clears the floor, rarely delivers, and
therefore never accumulates the samples that would give it a verdict.
LIQUIDITY_SWEEP_REVERSAL sat at ~1 delivered row in 7 days against
MOVER_TREND_PULLBACK's 134 while reading +0.984%/row in the dark lane.

Note which branch this targets: the ``positive_thin n<30`` branch was the
obvious reading of "don't wait for 20 to 30" and it is the WRONG one — it only
fires for cells that already carry a verdict.  A starved path never reaches it.
"""
from __future__ import annotations

import src.context_emission_policy as cep
from src.context_emission_policy import PolicyParams, effective_floor
from src.strategy_edge import (
    VERDICT_FLAT,
    VERDICT_INSUFFICIENT,
    VERDICT_NEGATIVE,
    VERDICT_STRONG,
)


class _Store:
    """Stands in for the edge store.

    Implements the THREE methods ``_lookup_cell`` actually calls — ``verdict``,
    ``edge_r``, ``sample_count`` — rather than a shape invented here.  A mock
    whose keys you chose cannot verify a contract you got wrong; the first cut
    of this file invented ``cell()`` and a function name that does not exist.
    """

    def __init__(self, verdict, edge=None, n=0):
        self._v, self._e, self._n = verdict, edge, n

    def verdict(self, *a, **k):
        return self._v

    def edge_r(self, *a, **k):
        return self._e

    def sample_count(self, *a, **k):
        return self._n


def _params(**over):
    base = dict(
        enabled=True, live=True, quality_anchor=55.0,
        strong_relax=10.0, positive_relax=5.0, min_samples=30,
        suppress_negative=True, cohort_aware=False,
        warmup_enabled=True, warmup_target=30, warmup_daily_cap=12,
    )
    base.update(over)
    return PolicyParams(**base)


def _reset():
    cep._WARMUP_GRANTS["day"] = ""
    cep._WARMUP_GRANTS["counts"] = {}


def _decide(store, strategy="LIQUIDITY_SWEEP_REVERSAL", **over):
    return effective_floor(
        strategy, "TRENDING_DOWN|ASIA", 65.0,
        cohort="", store=store, params=_params(**over),
    )


# --------------------------------------------------------------------------- #
# The bound that matters most
# --------------------------------------------------------------------------- #

def test_a_measured_negative_cell_is_never_resurrected_by_warmup():
    """Warmup is for the UNMEASURED, never for the disproven.

    If this ever fails, the allowance has become a way to re-emit a path the
    matrix has already measured as losing — which is the opposite of what the
    owner asked for and the single most dangerous thing this file could do.
    """
    _reset()
    d = _decide(_Store(VERDICT_NEGATIVE, edge=-0.9, n=200))
    assert d.suppressed is True
    assert "warmup" not in d.reason


def test_a_measured_flat_cell_gets_no_warmup():
    """FLAT has a verdict AND the samples behind it — it is measured, not
    starved, so it is not owed an allowance."""
    _reset()
    d = _decide(_Store(VERDICT_FLAT, edge=0.01, n=120))
    assert d.relaxed == 0.0
    assert "warmup" not in d.reason


# --------------------------------------------------------------------------- #
# The allowance itself
# --------------------------------------------------------------------------- #

def test_an_unmeasured_cell_now_gets_the_relax_so_it_can_deliver():
    _reset()
    d = _decide(_Store(VERDICT_INSUFFICIENT, edge=None, n=3))
    assert d.suppressed is False
    assert d.relaxed > 0.0
    assert d.effective_floor < 65.0
    assert "warmup_relax" in d.reason


def test_past_the_desirable_count_the_allowance_stops():
    """"After reaching desirable count then start sort out" — past the target
    the cell is judged on its own edge, not carried."""
    _reset()
    d = _decide(_Store(VERDICT_INSUFFICIENT, edge=None, n=30))
    assert d.relaxed == 0.0
    assert "warmup" not in d.reason


def test_the_daily_cap_bounds_the_blast_radius():
    _reset()
    granted = 0
    for _ in range(20):
        if "warmup_relax" in _decide(_Store(VERDICT_INSUFFICIENT, None, 3)).reason:
            granted += 1
    assert granted == 12


def test_a_capped_grant_is_its_own_reason_not_neutral():
    """"The allowance is spent" and "this cell is not owed one" are different
    facts with different next moves, so they never share a caption."""
    _reset()
    for _ in range(12):
        _decide(_Store(VERDICT_INSUFFICIENT, None, 3))
    d = _decide(_Store(VERDICT_INSUFFICIENT, None, 3))
    assert "warmup_capped" in d.reason
    assert d.relaxed == 0.0


def test_the_cap_is_per_strategy_so_one_path_cannot_starve_another():
    _reset()
    for _ in range(12):
        _decide(_Store(VERDICT_INSUFFICIENT, None, 3), strategy="LIQUIDITY_SWEEP_REVERSAL")
    other = _decide(_Store(VERDICT_INSUFFICIENT, None, 3), strategy="FAILED_AUCTION_RECLAIM")
    assert "warmup_relax" in other.reason


def test_a_zero_cap_disables_the_allowance_as_surely_as_the_flag():
    _reset()
    assert "warmup" not in _decide(_Store(VERDICT_INSUFFICIENT, None, 3), warmup_enabled=False).reason
    _reset()
    assert "warmup_relax" not in _decide(_Store(VERDICT_INSUFFICIENT, None, 3), warmup_daily_cap=0).reason


def test_a_strong_measured_cell_still_takes_the_strong_path():
    """The warmup must not shadow the edge rules it hands over to."""
    _reset()
    d = _decide(_Store(VERDICT_STRONG, edge=0.8, n=200))
    assert "warmup" not in d.reason
    assert d.relaxed > 0.0
