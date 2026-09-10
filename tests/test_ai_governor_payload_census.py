"""What the model was SHOWN, aggregated — so ops never has to reduce the rows.

PROMPT_SCHEMA 3 put the premise, the bars, the macro block and the FSM
lifecycle in front of the model, and every one of them lives per-row inside
`snapshot`. Without this census the only surface able to say whether any of it
is arriving would be one that parsed the ledger itself — and ops must not: the
api container has never evaluated a candidate, so a locally-assembled version
reports a healthy zero. `INDEX COLD`, and the promotion census before it.

Every test fails against the pre-census tree.
"""
from __future__ import annotations

from typing import Any, Dict

import pytest

from src import ai_governor_ledger as led
from src.execution import ai_governor as gov


@pytest.fixture(autouse=True)
def _ledger():
    led.reset_ledger(led.GovernorLedger(path=""))
    yield
    led.reset_ledger(led.GovernorLedger(path=""))


def _row(sid: str, snapshot: Dict[str, Any], action: str = "MAINTAIN") -> None:
    led.get_ledger().add({"signal_id": sid, "action": action, "snapshot": snapshot})


_SCHEMA2 = {"tp_candidates": [{"key": "tp_0"}], "sl_candidates": [{"key": "sl_0"}]}

_SCHEMA3 = {
    "premise": {
        "thesis": "t",
        "conditions": [
            {"name": "a", "at_entry": 1.0, "at_entry_reason": None, "now": 2.0},
            {"name": "b", "at_entry": None, "at_entry_reason": "feature_not_stamped",
             "now": None},
        ],
    },
    "bars": {"readable": True, "n": 12},
    "macro": {"btc_opposes_now": True},
    "tp_candidates": [{"key": "tp_0"}, {"key": "tp_1"}],
    "sl_candidates": [{"key": "sl_0"}, {"key": "sl_be"}],
}


def test_an_empty_ledger_is_not_measured_rather_than_zero():
    """A caller rendering 0% over an empty lane reports a healthy one."""
    out = gov.payload_census()
    assert out == {"rows": 0, "measured": False}
    assert "premise" not in out


def test_a_missing_block_is_an_old_row_not_a_broken_feed():
    """`bars` absent means a row written before schema 3; `readable: False`
    means the series was not there. Pooling them reports an old ledger as a
    broken feed — the caption naming a cause the page cannot observe."""
    _row("old", _SCHEMA2)
    _row("new", _SCHEMA3)
    out = gov.payload_census()
    assert out["bars"]["rows_without_block"] == 1
    assert out["bars"]["rows_with_block"] == 1
    assert out["bars"]["readable"] == 1
    assert out["bars"]["reasons"] == {}


def test_an_unreadable_block_names_its_reason():
    _row("s", dict(_SCHEMA3, bars={"readable": False, "reason": "stale"}))
    out = gov.payload_census()
    assert out["bars"]["readable"] == 0
    assert out["bars"]["reasons"] == {"stale": 1}


def test_a_refused_premise_is_counted_apart_from_one_with_a_thesis():
    """A live path with no thesis and a row predating the lane are different
    facts with different fixes."""
    _row("ok", _SCHEMA3)
    _row("bad", {"premise": {"refusal": "no_thesis", "setup_class": "NEW_PATH"}})
    out = gov.payload_census()["premise"]
    assert out["rows_with_thesis"] == 1
    assert out["refusals"] == {"no_thesis": 1}
    assert out["rows_with_block"] == 2


def test_the_two_entry_reasons_never_pool():
    """`no_entry_stamp` means the lane never saw this signal;
    `feature_not_stamped` means it saw it and could not read one column."""
    _row("s", {"premise": {"thesis": "t", "conditions": [
        {"name": "a", "at_entry": None, "at_entry_reason": "no_entry_stamp"},
        {"name": "b", "at_entry": None, "at_entry_reason": "feature_not_stamped"},
    ]}})
    reasons = gov.payload_census()["premise"]["at_entry_reasons"]
    assert reasons == {"no_entry_stamp": 1, "feature_not_stamped": 1}


def test_recomputed_is_counted_against_declared():
    """A premise nothing could re-read is a fact about the monitor's
    one-timeframe budget, not a fault — so both halves are published."""
    _row("s", _SCHEMA3)
    p = gov.payload_census()["premise"]
    assert p["conditions_declared"] == 2
    assert p["conditions_recomputed_now"] == 1


def test_the_menu_sizes_make_an_all_zero_adjust_tp_attributable():
    """ADJUST_TP has been chosen zero times in every window this lane has run,
    and nothing could say whether that is the model declining or the menu never
    offering. Measured over 234 real signals against real bars, 29% of TP menus
    carry no alternative to tp_0."""
    _row("a", _SCHEMA3)                       # 2 tp candidates
    _row("b", _SCHEMA2)                       # 1 tp candidate — no alternative
    _row("c", _SCHEMA2)
    menu = gov.payload_census()["menu"]
    assert menu["tp_sizes"] == {"2": 1, "1": 2}
    assert menu["tp_only_current"] == 2
    assert menu["tp_only_current_pct"] == pytest.approx(66.7, abs=0.1)


def test_btc_readability_is_tri_state_at_the_source():
    """None is 'could not ask', never 'no'."""
    _row("known", _SCHEMA3)
    _row("unknown", dict(_SCHEMA3, macro={"btc_opposes_now": None}))
    out = gov.payload_census()["macro"]
    assert out["rows_with_block"] == 2
    assert out["btc_opposes_readable"] == 1


def test_the_census_is_published_on_the_diag_ops_actually_reads():
    """A block the engine computes and no surface reads is #817 with the arrow
    reversed — and the producing side's test passes either way."""
    _row("s", _SCHEMA3)
    diag = gov.build_diag()
    assert "payload_census" in diag, "ops reads build_diag, not payload_census()"
    assert diag["payload_census"]["rows"] == 1
    assert diag["payload_census"]["measured"] is True


# ---------------------------------------------------------------------------
# Token headroom — the instrument for a claim already published
# ---------------------------------------------------------------------------


def test_token_usage_is_deduplicated_to_calls_not_rows():
    """One request answers a whole batch, so every verdict it produced carries
    the SAME usage dict. Averaging over rows weights a batch of six six times
    and reports a per-call figure no call ever had."""
    for sid in ("a", "b", "c"):
        led.get_ledger().add({
            "signal_id": sid, "action": "MAINTAIN", "issued_at": 1000.0,
            "usage": {"output_tokens": 40, "thinking_tokens": 1500}, "snapshot": {},
        })
    led.get_ledger().add({
        "signal_id": "d", "action": "MAINTAIN", "issued_at": 2000.0,
        "usage": {"output_tokens": 60, "thinking_tokens": 2500}, "snapshot": {},
    })
    tokens = gov.payload_census()["tokens"]
    assert tokens["calls"] == 2, "four rows, two calls"
    # Per call: (1500 + 2500) / 2. Rows-weighted would be 1750.
    assert tokens["thinking_mean"] == pytest.approx(2000.0)
    assert tokens["thinking_max"] == 2500


def test_the_refutation_condition_is_measurable_on_SUCCESSFUL_calls():
    """`thinking_tokens` is stamped on every call and was rendered only on the
    failure ring, so 'watch whether thinking climbs toward the ceiling' could be
    checked on exactly the population that did not matter."""
    led.get_ledger().add({
        "signal_id": "ok", "action": "MAINTAIN", "issued_at": 1.0,
        "usage": {"output_tokens": 40, "thinking_tokens": 1570}, "snapshot": {},
    })
    tokens = gov.payload_census()["tokens"]
    assert tokens["thinking_mean"] == pytest.approx(1570.0)
    assert tokens["calls_with_thinking_stamp"] == 1


def test_a_missing_thinking_stamp_is_not_zero_thinking():
    """An older row, or a vendor that did not report thoughts, is its own fact."""
    led.get_ledger().add({
        "signal_id": "nostamp", "action": "MAINTAIN", "issued_at": 1.0,
        "usage": {"output_tokens": 40}, "snapshot": {},
    })
    tokens = gov.payload_census()["tokens"]
    assert tokens["calls"] == 1
    assert tokens["calls_with_thinking_stamp"] == 0
    assert tokens["thinking_mean"] is None
    assert tokens["output_mean"] == pytest.approx(40.0)
