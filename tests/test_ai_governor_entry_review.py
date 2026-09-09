"""The entry review — "was this trade worth taking" — and why it is a REDEFINITION.

Owner, 2026-09-09: *"Signal fired / live continues as usual / but AI reviews it,
make adjustment if needed and also cancels signal if not worthy."*

The mechanism for cancelling already existed (`PANIC_CLOSE` → the shadow arm
exits at the next bar's open). What did not exist is the model ever being
**asked**. The schema-1 system prompt said *"you are a risk critic for an
already-open scalp … prefer MAINTAIN … reserve PANIC_CLOSE for a genuine regime
break"*, and under it the model chose `PANIC_CLOSE` **zero** times in 480 rows.
An all-zero column is a claim about the prompt before it is a claim about the
market.

So the FIRST review of a trade now asks whether it deserved to be taken, and
every later review stays the conservative critic it already was. Two questions,
one call, stamped apart — because pooling them would let a cancel rate mean
"the governor rejects 8% of signals" without being able to say when.

The load-bearing test in this file is
`test_the_stamp_comes_from_the_prompt_not_from_a_re_read`: `evaluate` increments
`calls_made` immediately after building the payload, so anything that re-derives
the review afterwards stamps every entry row as ongoing — emptying the exact
population this change exists to create, silently, with the prompt still asking
the right question.
"""
from __future__ import annotations

import json
from typing import Any, Dict

from src import ai_governor_live as cf
from src import llm_client
from src import sar_live_shadow as arms
from src import trail_mechanisms as tm
from src.execution import ai_governor as gov
from src.execution import ai_governor_snapshot as snap

from tests.test_ai_governor import FakeSignal, _menu_for  # noqa: E402


def _result(payload: Dict[str, Any]) -> llm_client.LLMResult:
    return llm_client.LLMResult(
        status=llm_client.OK, data=payload, served_model="m-002",
        requested_model="m", latency_ms=900,
        usage={"input_tokens": 10, "output_tokens": 10},
    )


def _batch(signal_id: str = "sig-1") -> Dict[str, Any]:
    m = _menu_for()
    s = snap.with_menu(
        snap.build_snapshot(
            signal=FakeSignal(), trigger_tf="15m", as_of_bar_ms=1,
            bars_since_entry=2, last_price=101.0, menu=m,
        ),
        m,
    )
    return {signal_id: (s, m)}


def _register(signal_id: str, calls_made: int) -> None:
    with gov._arms_lock:
        gov._arms[signal_id] = gov.Arm(
            signal_id=signal_id, symbol="TESTUSDT", trigger_tf="15m",
            opened_at=0.0, calls_made=calls_made,
        )


# --------------------------------------------------------------------------- #
# Which question is asked
# --------------------------------------------------------------------------- #


def test_an_arm_that_has_never_been_evaluated_is_at_its_entry_review():
    gov.reset_state_for_test()
    _register("sig-1", calls_made=0)
    assert gov._review_kind_for("sig-1") == gov.REVIEW_ENTRY


def test_every_review_after_the_first_is_ongoing():
    gov.reset_state_for_test()
    _register("sig-1", calls_made=1)
    assert gov._review_kind_for("sig-1") == gov.REVIEW_ONGOING


def test_an_arm_the_registry_has_lost_reads_ongoing():
    """The conservative side on purpose: an unknown arm is filed with the
    population that is NOT allowed to justify a cancel."""
    gov.reset_state_for_test()
    assert gov._review_kind_for("never-registered") == gov.REVIEW_ONGOING


def test_the_stamp_comes_from_the_prompt_not_from_a_re_read():
    """The one that matters.

    `evaluate` increments `calls_made` immediately after building the payload,
    so a `parse_verdicts` that re-derived the review would stamp every entry row
    as ongoing — the population emptied silently while the prompt still asked
    the right question, and nothing on any page would look wrong.

    Driven by handing `parse_verdicts` the mapping the prompt was built from
    while the arm has ALREADY been incremented, which is exactly production's
    ordering.
    """
    gov.reset_state_for_test()
    _register("sig-1", calls_made=1)  # already incremented, as after `evaluate`
    out = gov.parse_verdicts(
        {"verdicts": [{"signal_id": "sig-1", "verdict": "MAINTAIN",
                       "rationale": "x"}]},
        result=_result({}), batch=_batch(), now=1000.0,
        reviews={"sig-1": gov.REVIEW_ENTRY},
    )
    assert len(out) == 1
    assert out[0][0].review_kind == gov.REVIEW_ENTRY
    assert out[0][0].as_row()["review_kind"] == gov.REVIEW_ENTRY


def test_a_verdict_with_no_review_mapping_defaults_to_ongoing():
    """A missing stamp is not an entry review. Schema-1 rows were all asked the
    ongoing question, so that is where an unmapped verdict belongs."""
    gov.reset_state_for_test()
    _register("sig-1", calls_made=0)
    out = gov.parse_verdicts(
        {"verdicts": [{"signal_id": "sig-1", "verdict": "MAINTAIN",
                       "rationale": "x"}]},
        result=_result({}), batch=_batch(), now=1000.0,
    )
    assert out[0][0].review_kind == gov.REVIEW_ONGOING


# --------------------------------------------------------------------------- #
# The prompt itself
# --------------------------------------------------------------------------- #


def test_the_prompt_carries_BOTH_rubrics_and_says_which_field_selects_them():
    """A schema bump that leaves the prompt asking one question is the old
    question wearing a new number."""
    p = gov._SYSTEM_PROMPT
    assert '"review"' in p or "review = " in p
    assert 'review = "entry"' in p
    assert 'review = "ongoing"' in p
    # The entry rubric must actually license a refusal, or the arm stays dead.
    entry = p.split('review = "entry"')[1].split('review = "ongoing"')[0]
    assert "PANIC_CLOSE" in entry
    # ...and the ongoing rubric must keep the conservatism it already had.
    ongoing = p.split('review = "ongoing"')[1]
    assert "MAINTAIN" in ongoing


def test_the_prompt_schema_was_bumped_because_the_question_changed():
    assert gov.PROMPT_SCHEMA >= 2


def test_every_position_in_the_payload_carries_its_review():
    """The model cannot apply the right rubric to a position that does not say
    which one it is. One call for a mixed batch, not two."""
    gov.reset_state_for_test()
    _register("sig-a", calls_made=0)
    _register("sig-b", calls_made=4)
    reviews = {sid: gov._review_kind_for(sid) for sid in ("sig-a", "sig-b")}
    assert reviews == {"sig-a": gov.REVIEW_ENTRY, "sig-b": gov.REVIEW_ONGOING}

    batch = {**_batch("sig-a"), **_batch("sig-b")}
    payload = {
        "schema": gov.PROMPT_SCHEMA,
        "positions": [
            dict(s.as_dict(), review=reviews[sid]) for sid, (s, _m) in batch.items()
        ],
    }
    assert {p["review"] for p in payload["positions"]} == {"entry", "ongoing"}
    json.dumps(payload)  # the real call serialises it; a non-JSON value fails here


# --------------------------------------------------------------------------- #
# The cancel, on the shadow book
# --------------------------------------------------------------------------- #


BAR_MS = 900_000.0


def _series(bars):
    return {
        "open": [b[0] for b in bars], "high": [b[1] for b in bars],
        "low": [b[2] for b in bars], "close": [b[3] for b in bars],
        "open_time": [1_700_000_000_000.0 + i * BAR_MS for i in range(len(bars))],
    }


def _flat(n, price=100.0):
    return [(price, price + 0.2, price - 0.2, price) for _ in range(n)]


def _arm(sid="SIG-R"):
    s = _series(_flat(30))
    state = {tm.GOV_STOP_KEY: 97.0}
    point = tm.point(tm.MECH_GOVERNOR, None, s["high"], s["low"], s["close"],
                     29, side="LONG", state=state, params={})
    return arms.new_arm(
        signal_id=sid, symbol="TESTUSDT", side="LONG",
        setup_class="MOVER_TREND_PULLBACK", timeframe="15m",
        entry=100.0, stop_loss=97.0, tp1=105.0, point=point,
        opened_ms=s["open_time"][-1], original_sl_distance=3.0,
        mechanism=tm.MECH_GOVERNOR, mech_params={}, mech_state=state,
        now_ts=1.0,
    )


def test_a_cancel_at_entry_is_named_apart_from_a_panic_mid_trade(monkeypatch):
    """Both close the shadow position at the next bar's open — the EVENT is the
    same. The reason is not: "we should not have sent this signal" and "the
    market turned" are different findings, and a page that cannot tell them
    apart can count cancels without saying what kind."""
    monkeypatch.setattr(cf, "enabled", lambda: True)
    for review, expected in (
        (cf.REVIEW_ENTRY, arms.EXIT_GOVERNOR_REJECT),
        (cf.REVIEW_ONGOING, arms.EXIT_GOVERNOR_PANIC),
    ):
        ledger = arms.SarLiveLedger(path="", mechanism=tm.MECH_GOVERNOR)
        cf.reset_ledger(ledger)
        cf.reset_counters()
        arm = _arm()
        ledger.add(arm)
        assert cf.record_verdict(
            "SIG-R", "PANIC_CLOSE", None, review_kind=review
        ) == cf.EDIT_APPLIED
        assert ledger.get(arm["arm_id"])["pending_close"]["reason"] == expected
        assert ledger.get(arm["arm_id"])["gov_review_at_close"] == review
    cf.reset_ledger(None)
    cf.reset_counters()


def test_an_entry_cancel_fills_at_the_next_bars_open_like_any_other(monkeypatch):
    """It is still the walk that fills it. A price written in from outside the
    walk would be the one number on the page no bar produced."""
    monkeypatch.setattr(cf, "enabled", lambda: True)
    ledger = arms.SarLiveLedger(path="", mechanism=tm.MECH_GOVERNOR)
    cf.reset_ledger(ledger)
    bars = _flat(30)
    arm = _arm()
    ledger.add(arm)
    arm["last_close"] = 100.0
    cf.record_verdict("SIG-R", "PANIC_CLOSE", None, review_kind=cf.REVIEW_ENTRY)

    nxt = (101.0, 101.4, 100.6, 101.2)
    arms.step_arm(arm, _series(bars + [nxt]), now_ts=2.0)
    assert arm["status"] == arms.STATUS_CLOSED_PANIC
    assert arm["exit_reason"] == arms.EXIT_GOVERNOR_REJECT
    assert arm["fill_level"] == 101.0
    cf.reset_ledger(None)
