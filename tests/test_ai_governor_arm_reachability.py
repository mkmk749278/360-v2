"""Armed arms against the arms the model actually asks for.

`AI_GOV_ARMS_ENABLED` defaults to ``tp`` alone and the reasoning is sound on
its own terms: the TP arm is the only one fully decidable from the
closed-signal record, because the adjustment moves the target NEARER and
``max_favorable_excursion_pct`` settles it with no ordering ambiguity.

What nothing checked is whether the model ever chooses it. Live on 2026-09-08,
480 ledger rows and 90 verdicts: **MAINTAIN 56, ADJUST_SL 34, ADJUST_TP zero.**
Every actionable verdict this lane has ever produced belongs to an arm that is
not armed, and the armed arm has never fired — so arming the effect flag today
would change nothing at all. Of the 34 ``ADJUST_SL``, 16 already die
``stale_verdict`` and the other 18 would move from ``apply_off`` to
``arm_off``.

The reason no counter could show it is worth keeping: `by_action` creates a
key when it is first incremented, so an arm that has never been chosen has no
row rather than a zero one. The fault is an ABSENCE in one table read against
a config echo in another, and a reader has to hold both and notice something
missing. This publishes the join instead.
"""
from __future__ import annotations

import pytest

from src import ai_governor_ledger, llm_client
from src.execution import ai_governor as gov

from tests.test_ai_governor_provider_failures import _Client, _batch


@pytest.fixture(autouse=True)
def _isolate(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-a-real-secret")
    gov.reset_state_for_test()
    gov.reset_health_for_test()
    ai_governor_ledger.reset_ledger(ai_governor_ledger.GovernorLedger(path=""))
    yield
    gov.reset_state_for_test()
    gov.reset_health_for_test()
    ai_governor_ledger.reset_ledger(None)


def _by_arm(out):
    return {row["arm"]: row for row in out["arms"]}


async def _record(action: str, n: int = 1) -> None:
    """Drive the REAL recording path, not `_count_in` with a key I chose.

    A mock whose keys the test author picked asserts an assumption back at
    itself; `by_action` is written inside `evaluate` after `parse_verdicts`
    accepts the model's reply, so that is what runs here. Only the network is
    faked, through the same `_Client` the provider-failure tests use.
    """
    for i in range(n):
        batch = _batch()
        sid, (_snapshot, m) = next(iter(batch.items()))
        choice = None
        if action == gov.ADJUST_SL:
            choice = next(c.key for c in m.sl if c.key != "sl_0")
        elif action == gov.ADJUST_TP:
            choice = next(c.key for c in m.tp if c.key != "tp_0")
        ok = llm_client.LLMResult(
            status=llm_client.OK,
            data={"verdicts": [{
                "signal_id": sid, "verdict": action, "choice": choice,
                "confidence": 0.8, "rationale": "test", "premise_broken": [],
            }]},
            requested_model="gemini-3.7-flash",
            served_model="gemini-3.7-flash-002",
            latency_ms=900, usage={"input_tokens": 100, "output_tokens": 40},
        )
        await gov.evaluate(batch, now=1000.0 + i, client=_Client([ok]))


async def test_the_live_shape_is_named_a_fault(monkeypatch):
    """tp armed, every verdict an ADJUST_SL: arming apply would act on nothing."""
    monkeypatch.setattr(gov, "armed_arms", lambda: (gov.ARM_TP,))
    await _record(gov.ADJUST_SL, n=3)

    out = gov.arm_reachability()
    rows = _by_arm(out)
    assert rows[gov.ARM_SL]["verdicts_seen"] == 3
    assert rows[gov.ARM_TP]["verdicts_seen"] == 0
    assert rows[gov.ARM_TP]["armed_and_never_chosen"] is True
    assert rows[gov.ARM_SL]["armed"] is False
    assert out["actionable_verdicts"] == 3
    assert out["reachable_verdicts"] == 0, (
        "the number that says what arming the effect flag would do today"
    )
    assert out["all_armed_arms_unchosen"] is True


def test_an_arm_that_was_never_chosen_still_gets_a_ROW(monkeypatch):
    """`by_action` has no zero rows — a key appears when first incremented.

    So the fault is an absence, and an absence cannot be read off a table of
    counts. Every arm renders whether or not it has ever fired.
    """
    monkeypatch.setattr(gov, "armed_arms", lambda: (gov.ARM_TP,))
    rows = _by_arm(gov.arm_reachability())
    assert set(rows) == set(gov.ARMS), "all three arms, always"
    assert all(r["verdicts_seen"] == 0 for r in rows.values())


async def test_a_reachable_verdict_clears_the_flag(monkeypatch):
    """Not an alarm that can never go green: arm the arm the model uses and
    the fault clears without anything else changing."""
    monkeypatch.setattr(gov, "armed_arms", lambda: (gov.ARM_SL,))
    await _record(gov.ADJUST_SL)

    out = gov.arm_reachability()
    assert out["reachable_verdicts"] == 1
    assert out["all_armed_arms_unchosen"] is False
    assert _by_arm(out)[gov.ARM_SL]["armed_and_never_chosen"] is False


def test_no_verdicts_at_all_is_not_a_fault():
    """A lane that has not spoken yet is quiet, not broken. Reporting a fault
    on an empty population is how a real one stops standing out."""
    out = gov.arm_reachability()
    assert out["actionable_verdicts"] == 0
    assert out["all_armed_arms_unchosen"] is False


def test_reachability_is_published_where_the_armed_list_is():
    """Ops renders `armed_arms` as a config echo. The join has to travel with
    it or the page keeps showing two numbers nobody puts together."""
    diag = gov.build_diag()
    assert "arm_reachability" in diag
    assert "armed_arms" in diag
    assert {r["arm"] for r in diag["arm_reachability"]["arms"]} == set(gov.ARMS)
