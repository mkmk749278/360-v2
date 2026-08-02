"""The cohort-edge gate must say which of its four silences it is in.

2026-08-02, taking the feed issue: the census showed 5 armed cohorts including
**all four** ``MOVER_TREND_PULLBACK`` side×regime combinations, BTC macro
confirmed ``DECLINE`` (matching every stored cohort key), and yet MVRTP
candidates walked the whole gate chain to the confidence gate while
``cohort_edge`` had no row in the Suppression Quality Audit at all.

Four different states produce that same nothing:

* the gate is disabled,
* there is no history for the key it actually computed,
* there is history but under the sample floor,
* it raised and failed open.

The last one was invisible by construction — a bare ``log.debug`` with no
``fail_open.record``, at a level the VPS does not emit, against the hard limit
that says every fail-open ``except`` records. These pin the counters that tell
them apart, and the accounting that makes them add up.
"""
from __future__ import annotations

import src.scanner as scanner_mod


class TestTheFailOpensAreRecorded:
    """A gate raising on every candidate looked exactly like a gate passing
    every candidate. `fail_open.record` is what separates them."""

    def test_cohort_edge_records_its_fail_open(self):
        src = scanner_mod.__file__
        with open(src, encoding="utf-8") as fh:
            text = fh.read()
        idx = text.index("cohort_edge gate error for")
        window = text[idx - 500:idx]
        assert 'fail_open.record("scanner.cohort_edge"' in window, (
            "cohort_edge fails open without recording — the hard limit this "
            "repo's CLAUDE.md states, and the reason a raising gate was "
            "indistinguishable from a passing one"
        )

    def test_stat_filter_records_its_fail_open(self):
        with open(scanner_mod.__file__, encoding="utf-8") as fh:
            text = fh.read()
        idx = text.index("stat_filter error for")
        assert 'fail_open.record("scanner.stat_filter"' in text[idx - 500:idx]


class TestEveryOutcomeIsCounted:
    """The counters must partition the population, or the reader cannot tell a
    quiet gate from a broken one."""

    def _source(self) -> str:
        with open(scanner_mod.__file__, encoding="utf-8") as fh:
            return fh.read()

    def test_each_reason_a_candidate_survives_has_its_own_counter(self):
        src = self._source()
        for reason in (
            "cohort_edge:evaluated",
            "cohort_edge:disabled",
            "cohort_edge:no_history",
            "cohort_edge:below_min_n",
            "cohort_edge:positive_enough",
            "cohort_edge:error",
        ):
            assert f'"{reason}"' in src, f"{reason} is not counted"

    def test_evaluated_is_incremented_before_the_branch(self):
        """`evaluated` is the denominator. Counted inside a branch it would
        describe only the option already chosen — the same mistake as a
        selector applied to its own counts."""
        src = self._source()
        ev = src.index('"cohort_edge:evaluated"')
        branch = src.index('"cohort_edge:disabled"')
        assert ev < branch

    def test_the_suppression_itself_still_stamps_the_audit(self):
        """Counting must not have displaced the stamp: a gate that cannot be
        forward-measured cannot earn its place."""
        src = self._source()
        idx = src.index("COHORT_EDGE suppressed")
        assert '_stamp_suppressed(sig, "cohort_edge")' in src[idx:idx + 2000]
