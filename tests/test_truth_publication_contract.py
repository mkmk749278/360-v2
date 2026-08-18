"""The truth report's cadence must travel WITH the report.

2026-08-18: ops graded this artifact against a hard-coded one-hour bound while
it is published once a day, so `/truth` read **STALE** for ~23 hours out of
every 24 — over a workflow whose last six scheduled runs all succeeded. The
caption went further and named a cause the page could not observe: *"the engine
has not published a newer report"*. The engine does not publish it at all; a
scheduled GitHub Action collects from the engine and commits to `monitor-logs`.

An alarming caption over a healthy subsystem is worse than a blank, because it
sends the owner to debug something that works. This repo paid for exactly that
on `/invalidations` (2026-08-07, WRITER STALE) and it recurred one surface over.

So the cadence is stamped by the producer and read by the consumer, and these
tests derive the stamp from the workflow that actually schedules it — a number
copied into a second place drifts the first time the schedule changes.
"""
from __future__ import annotations

import pathlib
import re

import pytest

from src.runtime_truth_report import (
    PUBLISH_GRACE_SEC,
    PUBLISH_INTERVAL_SEC,
    PUBLISHER,
    _publication_contract,
)

REPO = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = REPO / ".github" / "workflows" / "vps-monitor.yml"


def _cron_expressions() -> list[str]:
    text = WORKFLOW.read_text()
    return re.findall(r'-\s*cron:\s*"([^"]+)"', text)


class TestDerivedFromTheWorkflow:
    def test_the_workflow_that_publishes_it_still_exists(self):
        assert WORKFLOW.exists(), (
            "the publisher named in PUBLISHER must be a real file — if this "
            "workflow is renamed, the stamp sends the owner to nothing"
        )
        assert WORKFLOW.name in PUBLISHER

    def test_the_declared_interval_matches_the_actual_cron(self):
        """A daily cron and a daily interval, checked against each other.

        This is the assertion that would have failed before the fix — ops was
        grading a `30 0 * * *` artifact on a 3600s bound.
        """
        crons = _cron_expressions()
        assert crons, "no cron schedule found in the publishing workflow"
        for expr in crons:
            fields = expr.split()
            assert len(fields) == 5, expr
            minute, hour, dom, month, dow = fields
            # A daily schedule: a fixed minute and hour, every day.
            assert (dom, month, dow) == ("*", "*", "*"), (
                f"schedule {expr!r} is no longer daily — PUBLISH_INTERVAL_SEC "
                f"({PUBLISH_INTERVAL_SEC}s) must be updated to match"
            )
            assert "*" not in (minute, hour) and "/" not in expr, (
                f"schedule {expr!r} fires more than once a day — "
                "PUBLISH_INTERVAL_SEC must be updated to match"
            )
        assert PUBLISH_INTERVAL_SEC == 86_400


class TestTheContractItself:
    def test_it_rides_on_every_snapshot_key_a_reader_needs(self):
        contract = _publication_contract()
        for key in ("interval_sec", "grace_sec", "stale_after_sec",
                    "publisher", "schedule"):
            assert key in contract, key
            assert contract[key] not in (None, ""), key

    def test_stale_after_is_the_interval_plus_the_grace(self):
        contract = _publication_contract()
        assert contract["stale_after_sec"] == (
            contract["interval_sec"] + contract["grace_sec"]
        )

    def test_the_grace_covers_the_observed_scheduler_delay(self):
        """GitHub's scheduler is best-effort. Measured start times over six
        consecutive days ran 87–159 minutes past the nominal 00:30. A grace
        under that would re-create the false-alarm this whole change removes."""
        worst_observed_delay_sec = 159 * 60
        assert PUBLISH_GRACE_SEC > worst_observed_delay_sec

    @pytest.mark.parametrize("age_sec, expected_stale", [
        (0, False),
        (3600, False),               # one hour — the OLD bound would fail here
        (86_400, False),             # a full day, still inside the grace
        (86_400 + 4 * 3600 + 1, True),
    ])
    def test_a_daily_artifact_is_not_stale_after_an_hour(self, age_sec, expected_stale):
        bound = _publication_contract()["stale_after_sec"]
        assert (age_sec > bound) is expected_stale
