"""The premise block — the question the prompt asks, finally in the payload.

Until 2026-09-10 the governor's system prompt asked whether *reality still
supports the original premise* while the payload named `setup_class` and said
nothing about what that setup required. Measured through the real producers:
27 scalar fields, 1,042 bytes, no bar of price history, no entry conditions,
and a `macro` block that was the empty object because `sweep`'s own parameter
had no caller.

Every test here fails against the pre-fix tree.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Dict, List

import pytest

from src import entry_features as ef
from src.execution import ai_governor_premise as prem
from src.execution import ai_governor_snapshot as snap_mod


# ---------------------------------------------------------------------------
# The thesis map is a FLOOR, and a miss is a refusal
# ---------------------------------------------------------------------------


def test_every_live_setup_class_has_a_thesis():
    """Derived from the evaluators' own `setup_class=` arguments.

    A hand-maintained per-setup map is a floor and is silent by construction on
    the next member — `SNAP_TF_BY_SETUP` bought that lesson and this test is the
    same guard. Tomorrow's evaluator fails CI here rather than landing in the
    refusal bucket forever.
    """
    source = Path("src/channels/scalp.py").read_text()
    declared = set()
    for match in re.finditer(r"setup_class\s*=\s*SetupClass\.([A-Z_0-9]+)", source):
        declared.add(match.group(1))
    for match in re.finditer(r'setup_class\s*=\s*["\']([A-Z_0-9]+)["\']', source):
        declared.add(match.group(1))
    assert declared, "the parser found no setup classes — it has drifted"
    missing = sorted(d for d in declared if d not in prem.THESIS_BY_SETUP)
    assert not missing, (
        f"no thesis for {missing}. Add one to THESIS_BY_SETUP rather than "
        "letting the path fall into the no_thesis refusal."
    )


def test_an_unknown_setup_is_refused_never_given_a_generic_sentence():
    out = prem.build(setup_class="NOT_A_PATH", signal=None, entry_row=None, series=None)
    assert out["refusal"] == prem.REFUSE_NO_THESIS
    assert "thesis" not in out


def test_no_thesis_is_a_model_written_or_external_string():
    """Every thesis is an engine-authored constant.

    A prompt whose output can close a live position is a money-path injection
    surface; the structural defence is that nothing here is interpolated from
    anywhere a user, a vendor or a model can reach.
    """
    tree = ast.parse(Path("src/execution/ai_governor_premise.py").read_text())
    assign = next(
        n for n in tree.body
        if isinstance(n, ast.AnnAssign) and getattr(n.target, "id", "") == "THESIS_BY_SETUP"
    )
    for value in assign.value.values:
        # A plain literal, or an implicit concatenation of literals. Anything
        # else — an f-string, a .format, a name — is a way in.
        assert isinstance(value, ast.Constant) and isinstance(value.value, str)


# ---------------------------------------------------------------------------
# The condition list is DERIVED, and unknown is always named
# ---------------------------------------------------------------------------


def test_conditions_come_from_the_real_feature_registry():
    """Never a second hand-kept list — the drift this repo has paid for."""
    out = prem.build(
        setup_class="MOVER_TREND_PULLBACK", signal=None,
        entry_row={"ef_rsi_at_entry": 50.0}, series=None,
    )
    got = [c["name"] for c in out["conditions"]]
    assert got == list(ef.features_for("MOVER_TREND_PULLBACK"))


def test_a_missing_reading_always_carries_a_cause():
    """Blank needs a cause before it gets a caption — three states, not two."""
    stamped = prem.build(
        setup_class="MOVER_TREND_PULLBACK", signal=None,
        entry_row={"ef_stack_sep_pct": 3.4}, series=None,
    )
    by_name = {c["name"]: c for c in stamped["conditions"]}
    # `stack_sep_pct` is a feature MVRTP actually declares. The first cut of
    # this test used `rsi_at_entry`, which belongs to TREND_PULLBACK_EMA - a
    # feature set is not portable just because the code that computes it is.
    assert by_name["stack_sep_pct"]["at_entry"] == 3.4
    assert by_name["stack_sep_pct"]["at_entry_reason"] is None
    # Present stamp, absent column — its own reason, not a bare null.
    other = next(c for c in stamped["conditions"] if c["at_entry"] is None)
    assert other["at_entry_reason"] == prem.WHY_FEATURE_NOT_STAMPED

    unstamped = prem.build(
        setup_class="MOVER_TREND_PULLBACK", signal=None, entry_row=None, series=None,
    )
    assert all(
        c["at_entry_reason"] == prem.WHY_NO_ENTRY_STAMP for c in unstamped["conditions"]
    )
    assert unstamped["entry_stamp"] is False


def test_no_entry_reason_and_no_stamp_are_different_facts():
    """One means the lane never saw this signal; the other that it could not
    read one column. Pooling them reports the wrong fault."""
    assert prem.WHY_NO_ENTRY_STAMP != prem.WHY_FEATURE_NOT_STAMPED


# ---------------------------------------------------------------------------
# Nothing here judges
# ---------------------------------------------------------------------------


def _series(closes: List[float]) -> Dict[str, Any]:
    return {
        "open": closes, "high": [c * 1.002 for c in closes],
        "low": [c * 0.998 for c in closes], "close": closes,
        "volume": [100.0] * len(closes),
        "open_time": [1_789_000_000_000 + i * 900_000 for i in range(len(closes))],
    }


def test_moved_is_a_change_not_a_verdict():
    out = prem.build(
        setup_class="TREND_PULLBACK_EMA", signal=None,
        entry_row={"ef_rsi_at_entry": 60.0},
        series=_series([100.0 + i * 0.1 for i in range(120)]),
    )
    rsi = next(c for c in out["conditions"] if c["name"] == "rsi_at_entry")
    assert rsi["now"] is not None, "RSI is recomputable from the trigger series"
    assert rsi["moved"] == pytest.approx(rsi["now"] - 60.0, abs=1e-6)
    # And there is deliberately no boolean verdict on a numeric condition.
    assert "still_true" not in rsi


def test_no_condition_carries_a_threshold_fitted_here():
    """A rule whose threshold comes from the window it is measured on is the
    defect `entry_quality` was built to avoid. This module has no thresholds."""
    src = Path("src/execution/ai_governor_premise.py").read_text()
    tree = ast.parse(src)
    build_fn = next(
        n for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "build"
    )
    compares = [n for n in ast.walk(build_fn) if isinstance(n, ast.Compare)]
    for node in compares:
        for comparator in node.comparators:
            # No numeric literal comparison anywhere in the block builder.
            assert not (
                isinstance(comparator, ast.Constant)
                and isinstance(comparator.value, (int, float))
                and not isinstance(comparator.value, bool)
            ), "a numeric threshold appeared in the premise builder"


def test_a_bool_never_becomes_a_number():
    """True→False is a fact to read, not `-1.0`."""
    assert prem._moved(True, False) is None
    assert prem._moved(1.0, 2.0) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# The snapshot actually carries it — the seam, checked at both ends
# ---------------------------------------------------------------------------


class _Sig:
    signal_id = "S1"
    symbol = "BRUSDT"
    direction = "LONG"
    setup_class = "MOVER_TREND_PULLBACK"
    entry_regime = "TRENDING_UP"
    entry_regime_15m = "TRENDING_UP"
    entry = 100.0
    stop_loss = 97.0
    tp1 = 103.0
    original_sl_distance = 3.0
    max_favorable_excursion_pct = 1.0
    max_adverse_excursion_pct = -0.5
    breakeven_set = False
    trailing_stage = 0
    partial_close_pct = 0.0
    status = "ACTIVE"
    geo_atr_stop = 1.2
    btc_state = -0.2
    btc_state_factor = 0.9
    mc_pair_cohort = "K"


def _built(series=None, premise=None):
    from src.execution import ai_governor_menu as menu_mod
    closes = [100.0 + (i % 9) * 0.15 for i in range(80)]
    m = menu_mod.build_menu(
        side="LONG", entry=100.0, current_sl=97.0, current_tp1=103.0,
        highs=[c + 0.3 for c in closes], lows=[c - 0.3 for c in closes],
        closes=closes, last_price=101.0, round_price=None, book_levels=None,
    )
    return snap_mod.build_snapshot(
        signal=_Sig(), trigger_tf="15m", as_of_bar_ms=1_789_000_000_000,
        bars_since_entry=4, last_price=101.0, menu=m,
        series=series, premise=premise,
        macro=snap_mod.macro_for_signal(_Sig(), opposes=True, oppose_reason="r",
                                        same_direction_open=2),
        now=1_789_000_100.0,
    ), m


def test_the_snapshot_publishes_the_new_blocks():
    s, m = _built(series=_series([100.0 + i * 0.05 for i in range(80)]),
                  premise={"thesis": "t", "conditions": []})
    d = snap_mod.with_menu(s, m).as_dict()
    for key in ("bars", "premise", "lifecycle", "macro"):
        assert key in d, f"{key} missing from the payload"
    assert d["premise"]["thesis"] == "t"
    assert d["bars"]["readable"] is True
    assert d["lifecycle"]["status"] == "ACTIVE"


def test_with_menu_preserves_every_new_block():
    """`with_menu` rebuilds the frozen dataclass field by field. A block added
    to `Snapshot` and not carried here is dropped between build and send —
    invisible at both ends, which is this repo's commonest defect shape."""
    s, m = _built(series=_series([100.0 + i * 0.05 for i in range(80)]),
                  premise={"thesis": "t", "conditions": [{"name": "x"}]})
    after = snap_mod.with_menu(s, m)
    assert after.bars == s.bars
    assert after.premise == s.premise
    assert after.lifecycle == s.lifecycle


def test_bars_are_signed_toward_the_trade_on_a_short():
    """A raw block would be the one place direction has to be re-derived, which
    is how `cvd_slope` scored every SHORT backwards for a month."""
    rising = [100.0 + i * 0.2 for i in range(80)]
    block = snap_mod.bars_block(_series(rising), entry=100.0, is_long=False,
                                trigger_tf="15m")
    # Price rose; on a SHORT every close is AGAINST the trade, so negative.
    closes = [r[4] for r in block["rows"]]
    assert all(c < 0 for c in closes), closes
    assert block["closes_against_streak"] > 0


def test_an_absent_series_is_named_not_zeroed():
    block = snap_mod.bars_block(None, entry=100.0, is_long=True, trigger_tf="15m")
    assert block["readable"] is False and block["reason"]
    assert "rows" not in block


def test_macro_keeps_entry_time_and_now_apart():
    """`btc_state` is stamped by the scanner at scoring time. Publishing it as a
    present-tense reading is the `entry_regime` defect, and the whole point of
    this lane is comparing then with now."""
    block = snap_mod.macro_for_signal(_Sig(), opposes=True, oppose_reason="1h4h",
                                      same_direction_open=3)
    assert block["btc_state_at_entry"] == pytest.approx(-0.2)
    assert block["btc_opposes_now"] is True
    assert "btc_state" not in block, "an entry-time value must not wear a bare name"


def test_btc_unreadable_is_none_never_false():
    block = snap_mod.macro_for_signal(_Sig(), opposes=None, oppose_reason="")
    assert block["btc_opposes_now"] is None
