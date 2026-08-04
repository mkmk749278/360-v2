"""#781: a fully-gated path is only a fault when the gating is costing us.

The two emission probes (`mean_revert_emission`, `range_fade_emission`) paged
identically whether the gating was correct or expensive. On real data those
were opposite cases — RANGE_FADE's blocked candidates measured −0.98R at a 3%
win rate (the gates are right, emitting would lose money) while MEAN_REVERT's
measured positive (the gating is costing us). One undifferentiated alert made
both unactionable, and #781 sat alerting for days.

These tests pin the distinction, and pin that it is a *reclassification* — the
detection still happens and the state is always reported. Silencing it would
break the Hard Limit; the point is that a page now means money on the table.
"""
from __future__ import annotations

from src.feature_liveness import gated_path_verdict
from src.strategy_edge import pooled_suppressed_edge


class TestGatedPathVerdict:
    def test_measured_negative_is_healthy_because_the_gates_are_right(self):
        ok, detail = gated_path_verdict(
            backlog=610, emitted_total=0,
            edge={"n": 1804, "avg_r": -0.98}, label="RANGE_FADE",
        )
        assert ok is True
        assert "correctly" in detail
        # The reason must be visible, not swallowed — this is a
        # reclassification, not a mute.
        assert "-0.98R" in detail and "n=1804" in detail

    def test_measured_positive_still_pages_and_says_what_it_costs(self):
        ok, detail = gated_path_verdict(
            backlog=242, emitted_total=0,
            edge={"n": 2999, "avg_r": 0.60}, label="MEAN_REVERT",
        )
        assert ok is False
        assert "COSTING" in detail
        assert "+0.60R" in detail and "n=2999" in detail

    def test_unmeasured_still_pages(self):
        """An unmeasured silent path is the 2026-07-14 failure this module
        exists for — absence of evidence must not read as evidence."""
        ok, detail = gated_path_verdict(
            backlog=100, emitted_total=0, edge=None, label="MEAN_REVERT",
        )
        assert ok is False
        assert "cannot" in detail

    def test_thin_sample_pages_rather_than_clearing_the_path(self):
        ok, detail = gated_path_verdict(
            backlog=100, emitted_total=0,
            edge={"n": 12, "avg_r": -5.0}, label="RANGE_FADE",
        )
        assert ok is False, "12 samples must not clear a path, however negative"
        # The sample count must be stated. Asserted on the number and the noun
        # separately rather than on one phrase, because 2026-08-04 inserted the
        # population name between them ("12 POST-SCORING suppressed samples")
        # and the claim being protected here is that the count is on screen.
        assert "12" in detail and "suppressed samples" in detail

    def test_the_boundary_is_inclusive_on_the_negative_side(self):
        at_bound = gated_path_verdict(
            backlog=100, emitted_total=0,
            edge={"n": 500, "avg_r": -0.10}, label="X",
        )
        just_above = gated_path_verdict(
            backlog=100, emitted_total=0,
            edge={"n": 500, "avg_r": -0.09}, label="X",
        )
        assert at_bound[0] is True
        assert just_above[0] is False

    def test_a_flat_path_pages_because_flat_is_not_a_reason_to_block(self):
        ok, _ = gated_path_verdict(
            backlog=100, emitted_total=0,
            edge={"n": 500, "avg_r": 0.0}, label="X",
        )
        assert ok is False


class TestPooledSuppressedEdge:
    def _cell(self, strategy, ctx, n_supp, net_r, n_emit=0):
        return {
            "strategy": strategy, "context_key": ctx,
            "n_suppressed": n_supp, "n_emitted": n_emit,
            "net_r_by_source": {"suppressed": net_r},
        }

    def test_pools_sample_weighted_across_contexts(self):
        matrix = {
            "a": self._cell("MEAN_REVERT", "A", 100, 1.0),
            "b": self._cell("MEAN_REVERT", "B", 300, -1.0),
        }
        edge = pooled_suppressed_edge(matrix, "MEAN_REVERT")
        assert edge is not None
        assert edge["n"] == 400
        # (100*1.0 + 300*-1.0) / 400 — weighted, not a mean of means (which
        # would be 0.0 and would flip the verdict).
        assert edge["avg_r"] == -0.5

    def test_other_strategies_are_not_pooled_in(self):
        matrix = {
            "a": self._cell("MEAN_REVERT", "A", 100, 1.0),
            "b": self._cell("RANGE_FADE", "A", 900, -1.0),
        }
        edge = pooled_suppressed_edge(matrix, "MEAN_REVERT")
        assert edge["n"] == 100 and edge["avg_r"] == 1.0

    def test_emitted_only_cells_contribute_nothing(self):
        matrix = {
            "a": {
                "strategy": "MEAN_REVERT", "n_suppressed": 0, "n_emitted": 50,
                "net_r_by_source": {"emitted": 2.0},
            },
        }
        assert pooled_suppressed_edge(matrix, "MEAN_REVERT") is None

    def test_no_sample_returns_none_not_zero(self):
        """None ('nothing measured') and 0.0 ('measured flat') must not be
        confused — the verdict treats them differently."""
        assert pooled_suppressed_edge({}, "MEAN_REVERT") is None
        assert pooled_suppressed_edge(None, "MEAN_REVERT") is None

    def test_survives_junk_cells(self):
        matrix = {"a": None, "b": "x", "c": {"strategy": "MEAN_REVERT"}}
        assert pooled_suppressed_edge(matrix, "MEAN_REVERT") is None


# --------------------------------------------------------------------------- #
# The verdict names its population (2026-08-04)
# --------------------------------------------------------------------------- #


class TestTheVerdictNamesItsPopulation:
    """``edge`` covers post-scoring suppressions only, and the message says so.

    ``suppression_audit.feeds_edge_matrix`` returns False for every pre-scoring
    reject, so a path whose output is actually being stopped by
    ``setup_compat:*`` / ``execution:*`` gets a verdict computed on a population
    that never contained the gate doing the stopping. MEAN_REVERT is the live
    example: this edge reads +0.50R while its dark-lane rows — all pre-scoring,
    disjoint by construction — measure −0.66%. Neither is wrong; they describe
    different candidates, and a reader who takes one as a check on the other
    reaches for the wrong lever.
    """

    def _edge(self, avg_r: float, n: int = 400):
        return {"avg_r": avg_r, "n": n}

    def test_a_correctly_gated_verdict_says_post_scoring(self):
        ok, msg = gated_path_verdict(
            backlog=4000, emitted_total=0, edge=self._edge(-0.60), label="RANGE_FADE"
        )
        assert ok is True
        assert "POST-SCORING" in msg
        assert "dark lane" in msg

    def test_a_costing_verdict_says_post_scoring_and_warns_before_loosening(self):
        ok, msg = gated_path_verdict(
            backlog=4221, emitted_total=5, edge=self._edge(0.50), label="MEAN_REVERT"
        )
        assert ok is False
        assert "POST-SCORING" in msg
        # The actionable half: do not loosen on this number alone.
        assert "disjoint" in msg or "pre-scoring" in msg.lower()

    def test_an_unmeasured_verdict_points_at_the_other_population(self):
        ok, msg = gated_path_verdict(
            backlog=31169, emitted_total=0, edge=None, label="LIQUIDITY_SWEEP_REVERSAL"
        )
        assert ok is False
        assert "POST-SCORING" in msg
        assert "dark lane" in msg
