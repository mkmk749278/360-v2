"""The apply funnel, and the two constants that described a lane they were not in.

Three defects, found by reading the live panel on 2026-09-10 rather than by any
test in this suite:

* `apply_verdict` had nine terminal states and `no_positions` counted nothing.
  By elimination over the counted branches that is where twelve actionable
  ADJUST_SL verdicts went while the page read `applied 0` with no refusal — and
  *nobody was in this trade* and *the apply path is dead* produce the identical
  reading.
* `_dark_arm` stamped `arm_undecidable_while_dark` unconditionally, on a lane
  whose apply flag was ON with that arm armed.
* `shadow_note` asserted "Apply is OFF" as a hardcoded string, rendered directly
  beneath a header reading `Apply: ON`.

Every test here fails against the pre-fix tree; that is the point of the file.
The suite was fully green over all three.
"""
from __future__ import annotations

import ast
import inspect
from typing import Any, Dict, List, Optional

import pytest

from src import ai_governor_score as sc
from src.execution import ai_governor as gov
from src.execution import ai_governor_menu as menu_mod
from src.execution import ai_governor_snapshot as snap_mod


# ---------------------------------------------------------------------------
# Real producers, never a hand-written shape
# ---------------------------------------------------------------------------


class _Sig:
    def __init__(self, sid: str = "S1") -> None:
        self.signal_id = sid
        self.symbol = "BRUSDT"
        self.direction = "LONG"
        self.setup_class = "MOVER_TREND_PULLBACK"
        self.entry_regime = "TRENDING_UP"
        self.entry = 100.0
        self.stop_loss = 97.0
        self.tp1 = 103.0
        self.original_sl_distance = 3.0
        self.max_favorable_excursion_pct = 1.0
        self.max_adverse_excursion_pct = -0.5


def _real_snapshot_and_menu():
    """Drive the REAL menu and snapshot builders, then hand back what they made."""
    closes = [100.0 + (i % 7) * 0.2 for i in range(60)]
    highs = [c + 0.3 for c in closes]
    lows = [c - 0.3 for c in closes]
    m = menu_mod.build_menu(
        side="LONG", entry=100.0, current_sl=97.0, current_tp1=103.0,
        highs=highs, lows=lows, closes=closes, last_price=101.0,
        round_price=None, book_levels=None,
    )
    s = snap_mod.build_snapshot(
        signal=_Sig(), trigger_tf="15m", as_of_bar_ms=1_789_000_000_000,
        bars_since_entry=4, last_price=101.0, menu=m, now=1_789_000_100.0,
    )
    return snap_mod.with_menu(s, m), m


_ISSUED = 1_789_000_100.0


def _verdict(action: str, *, choice: Optional[str] = None) -> gov.Verdict:
    return gov.Verdict(
        signal_id="S1", action=action, choice=choice, confidence=0.7,
        rationale="t", premise_broken=(), served_model="m", requested_model="m",
        prompt_schema=gov.PROMPT_SCHEMA, snapshot_digest="d",
        as_of_bar_ms=1_789_000_000_000, issued_at=_ISSUED,
        latency_ms=10, usage={}, cost_usd=None,
    )


@pytest.fixture(autouse=True)
def _clean():
    gov.reset_health_for_test()
    sc.reset_cache()
    yield
    gov.reset_health_for_test()
    sc.reset_cache()


# ---------------------------------------------------------------------------
# 1. The funnel is total BY CONSTRUCTION
# ---------------------------------------------------------------------------


async def test_no_positions_is_counted_and_not_silent(monkeypatch):
    """The exit that swallowed every actionable verdict on the live lane.

    Fails against the pre-fix tree: `no_positions` returned with no counter, so
    `apply_outcomes` did not exist and nothing anywhere recorded the outcome.
    """
    snapshot, m = _real_snapshot_and_menu()
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    monkeypatch.setattr(gov, "armed_arms", lambda: ("tp", "sl", "panic"))
    # The index ANSWERED, and the answer was "nobody holds this trade".
    monkeypatch.setattr(gov, "_open_positions_for", lambda sid: [])

    # `now` is pinned to the verdict's own issue time. The staleness check runs
    # before every other branch, so a verdict issued at a fixed epoch against a
    # wall clock refuses as `stale_verdict` and never reaches the branch under
    # test — which is what the first run of this test did, and is exactly the
    # "assert the drop REASON, not the outcome" rule arriving in a test of mine.
    out = await gov.apply_verdict(
        _verdict(gov.ADJUST_SL, choice="sl_be"), snapshot, m, now=_ISSUED
    )

    assert out == "no_positions"
    funnel = gov.health()["apply_outcomes"]
    assert funnel.get("no_positions") == 1, funnel
    # And it must NOT have been filed as a refusal: nothing failed.
    assert "no_positions" not in gov.health()["refusals"]


async def test_every_apply_outcome_lands_in_the_funnel(monkeypatch):
    """Four different terminal states, four counted outcomes, no silent path."""
    snapshot, m = _real_snapshot_and_menu()

    async def _apply(action: str, choice=None):
        return await gov.apply_verdict(
            _verdict(action, choice=choice), snapshot, m, now=_ISSUED
        )

    monkeypatch.setattr(gov, "apply_enabled", lambda: False)
    await _apply(gov.ADJUST_SL, "sl_be")

    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    monkeypatch.setattr(gov, "armed_arms", lambda: ("tp",))
    await _apply(gov.ADJUST_SL, "sl_be")

    monkeypatch.setattr(gov, "armed_arms", lambda: ("tp", "sl"))
    monkeypatch.setattr(gov, "_open_positions_for", lambda sid: None)
    await _apply(gov.ADJUST_SL, "sl_be")

    await _apply(gov.MAINTAIN)

    funnel = gov.health()["apply_outcomes"]
    assert funnel.get(gov.REFUSE_APPLY_OFF) == 1
    assert funnel.get(gov.REFUSE_ARM_OFF) == 1
    assert funnel.get(gov.REFUSE_INDEX_COLD) == 1
    assert funnel.get(gov.MAINTAIN) == 1
    # Total by construction: every call contributed exactly one outcome.
    assert sum(funnel.values()) == 4


def test_apply_verdict_is_a_counting_wrapper_not_a_list_of_counted_returns():
    """Pin the SHAPE, so a return added tomorrow cannot escape the funnel.

    A hand-kept list of counted returns is a mirror of the control flow, and
    this repo has paid for a drifting mirror under six names. The wrapper must
    contain no `return` of its own other than the counted one.
    """
    tree = ast.parse(inspect.getsource(gov.apply_verdict))
    fn = tree.body[0]
    returns = [n for n in ast.walk(fn) if isinstance(n, ast.Return)]
    assert len(returns) == 1, "the wrapper must have exactly one return"
    counted = [
        n for n in ast.walk(fn)
        if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "_count_in"
    ]
    assert counted, "the wrapper must count the outcome it returns"


# ---------------------------------------------------------------------------
# 2. The arm reason is READ, not asserted
# ---------------------------------------------------------------------------


def _row(action: str, *, armed: Optional[bool], sid: str = "s1") -> Dict[str, Any]:
    return {
        "signal_id": sid, "action": action, "choice": None, "apply_armed": armed,
        "unknown_frac": 0.0, "snapshot": {"tp_candidates": [], "sl_candidates": []},
    }


def _rec(sid: str) -> Dict[str, Any]:
    return {"signal_id": sid, "pnl_pct": 1.0, "max_favorable_excursion_pct": 2.0,
            "sl_distance_pct_at_entry": 2.0, "outcome_label": "TP1_HIT"}


_REC = [_rec("s1")]
# A mixed window is two SIGNALS, one issued dark and one armed - never two rows
# on one signal. `thesis_per_signal` collapses newest-wins per signal, so a
# same-id pair is one thesis by design and the first cut of these two tests was
# asserting against a population that cannot exist.
_REC2 = [_rec("s1"), _rec("s2")]


def test_a_dark_arm_says_dark():
    out = sc.score([_row(gov.ADJUST_SL, armed=False)], _REC)
    arm = out["arms"]["ADJUST_SL"]
    assert sc.WHY_ARM_UNDECIDABLE in arm["undecidable"]
    assert arm["rows_dark"] == 1 and arm["rows_armed"] == 0


def test_an_armed_arm_does_not_claim_nothing_was_applied():
    """The live defect: this read `arm_undecidable_while_dark` with apply ON."""
    out = sc.score([_row(gov.ADJUST_SL, armed=True)], _REC)
    arm = out["arms"]["ADJUST_SL"]
    assert sc.WHY_ARM_UNDECIDABLE_ARMED in arm["undecidable"]
    assert sc.WHY_ARM_UNDECIDABLE not in arm["undecidable"]
    assert "Nothing was applied" not in arm["why"]
    assert arm["rows_armed"] == 1


def test_a_window_armed_part_way_is_named_as_mixed_never_pooled():
    rows = [_row(gov.ADJUST_SL, armed=False, sid="s1"),
            _row(gov.ADJUST_SL, armed=True, sid="s2")]
    arm = sc.score(rows, _REC2)["arms"]["ADJUST_SL"]
    assert sc.WHY_ARM_UNDECIDABLE_MIXED in arm["undecidable"]
    assert arm["rows_armed"] == 1 and arm["rows_dark"] == 1


def test_an_unstamped_row_is_its_own_bucket_and_never_read_as_dark():
    """A missing stamp is not a pass — the rule this repo keeps re-learning."""
    arm = sc.score([_row(gov.ADJUST_SL, armed=None)], _REC)["arms"]["ADJUST_SL"]
    assert arm["rows_unstamped"] == 1
    assert arm["rows_dark"] == 0


# ---------------------------------------------------------------------------
# 3. The note follows the rows
# ---------------------------------------------------------------------------


def test_the_shadow_note_is_not_a_constant():
    dark = sc.score([_row(gov.ADJUST_SL, armed=False)], _REC)["shadow_note"]
    armed = sc.score([_row(gov.ADJUST_SL, armed=True)], _REC)["shadow_note"]
    assert dark != armed, "the note must describe the lane it is over"
    assert "MAINTAIN counterfactual" in dark
    # The exact sentence that stood over an armed lane on the live page.
    assert "Apply is OFF" not in armed
    assert "must not be read as one" in armed


def test_the_note_names_a_mixed_window_as_mixed():
    rows = [_row(gov.ADJUST_SL, armed=False, sid="s1"),
            _row(gov.ADJUST_SL, armed=True, sid="s2")]
    note = sc.score(rows, _REC2)["shadow_note"]
    assert "part-way" in note and "mixes" in note


def test_no_runtime_string_asserts_the_apply_state_as_a_literal():
    """Derived, so the next hardcoded claim about apply state fails CI here.

    Walks the AST for string CONSTANTS the module would actually emit, and
    skips docstrings — the first cut grepped raw source and flagged the
    docstring above, which quotes the removed sentence in order to explain why
    it was removed. A substring assertion over source text cannot tell prose
    about a defect from the defect.
    """
    tree = ast.parse(inspect.getsource(sc))
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", None) or []
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                docstrings.add(id(body[0].value))
    offenders = [
        n.value for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
        and id(n) not in docstrings and "Apply is OFF" in n.value
    ]
    assert not offenders, offenders


# ---------------------------------------------------------------------------
# 4. The stamp is taken where it becomes true
# ---------------------------------------------------------------------------


def test_maintain_is_tri_state_never_false(monkeypatch):
    """MAINTAIN has no arm, so `armed` is a question it cannot be asked."""
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    monkeypatch.setattr(gov, "armed_arms", lambda: ("tp", "sl"))
    assert gov._arm_is_armed_now(gov.MAINTAIN) is None
    assert gov._arm_is_armed_now(gov.ADJUST_SL) is True
    assert gov._arm_is_armed_now(gov.PANIC_CLOSE) is False


def test_the_stamp_is_per_action_not_per_lane(monkeypatch):
    """`sl` armed and `tp` not is one lane holding both worlds at once."""
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    monkeypatch.setattr(gov, "armed_arms", lambda: ("sl",))
    assert gov._arm_is_armed_now(gov.ADJUST_SL) is True
    assert gov._arm_is_armed_now(gov.ADJUST_TP) is False
