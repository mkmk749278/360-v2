"""Tests for the per-setup trigger-timeframe correction.

``Scanner._get_primary_timeframe`` was::

    @staticmethod
    def _get_primary_timeframe(chan_name: str) -> str:
        \"\"\"Return the primary timeframe interval string for a given channel.\"\"\"
        return "5m"

— a constant wearing a lookup's docstring, read by six money-path consumers, on
a book that is ~59% ``MOVER_TREND_PULLBACK`` (15m).

The defect class is the same as the structural snap's: a thing that *reads*
correct and *is* inert.  So the tests that matter are the ones about
reachability and about the correction staying dark, not the ones about the map's
contents.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from src import setup_timeframes as stf

_REPO = Path(__file__).resolve().parents[1]
_SCANNER = _REPO / "src" / "scanner" / "__init__.py"


@pytest.fixture(autouse=True)
def _fresh():
    stf.reset_counters()
    yield
    stf.reset_counters()


# ---------------------------------------------------------------------------
# Reachability — the defect class
# ---------------------------------------------------------------------------

def test_the_resolver_is_no_longer_a_constant():
    """Pinned against the exact prior body.

    If someone re-simplifies this to ``return "5m"`` the six consumers go back
    to reading the wrong series, silently and with no test failing anywhere
    else — which is precisely how it survived this long.
    """
    tree = ast.parse(_SCANNER.read_text())
    fn = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "_get_primary_timeframe"
    )
    body = [s for s in fn.body if not isinstance(s, ast.Expr)]  # drop docstring
    assert not (
        len(body) == 1
        and isinstance(body[0], ast.Return)
        and isinstance(body[0].value, ast.Constant)
    ), "_get_primary_timeframe is a constant again — the six consumers are back on 5m"


def test_every_call_site_passes_a_setup_class():
    """A caller that omits it silently resolves to the legacy 5m.

    That is the correct *fallback* and the wrong *default*: an unmapped
    resolution is counted, but a call site that simply forgot the argument
    would read as an unmapped setup rather than as a wiring bug. Pin the call
    sites so the two cannot be confused.
    """
    tree = ast.parse(_SCANNER.read_text())
    calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and ast.unparse(n.func).endswith("_get_primary_timeframe")
    ]
    assert len(calls) >= 6, f"expected the six known consumers, found {len(calls)}"
    bare = [ast.unparse(c) for c in calls if len(c.args) + len(c.keywords) < 2]
    assert not bare, f"call sites with no setup_class: {bare}"


def test_the_map_has_exactly_one_definition():
    """``structural_snap`` re-exports rather than copying.

    Two consumers of the same map means two copies unless something stops it,
    and ``MEASUREMENT_SUFFIXES`` drifted for a week the last time nothing did.
    """
    from src import structural_snap as ss
    assert ss.SNAP_TF_BY_SETUP is stf.TF_BY_SETUP


def test_every_live_setup_class_is_declared():
    """Derived from the evaluators' own ``setup_class=`` arguments, so a new
    evaluator fails CI rather than silently inheriting 5m."""
    tree = ast.parse((_REPO / "src" / "channels" / "scalp.py").read_text())
    declared = {
        kw.value.value
        for n in ast.walk(tree) if isinstance(n, ast.Call)
        for kw in n.keywords
        if kw.arg == "setup_class"
        and isinstance(kw.value, ast.Constant)
        and isinstance(kw.value.value, str) and kw.value.value
    }
    missing = sorted(declared - set(stf.TF_BY_SETUP))
    assert not missing, f"setup classes with no declared trigger timeframe: {missing}"


# ---------------------------------------------------------------------------
# The correction stays dark until it is flipped
# ---------------------------------------------------------------------------

def test_dark_by_default_returns_the_legacy_timeframe_byte_identically():
    """The whole safety property. With the flag off, every consumer sees
    exactly what it saw before this module existed."""
    for setup in ("MOVER_TREND_PULLBACK", "MEAN_REVERT", "WHALE_MOMENTUM",
                  "MA_CROSS_TREND_SHIFT", "SR_FLIP_RETEST", ""):
        assert stf.resolve(setup, live=False) == "5m"


def test_live_returns_the_setups_own_timeframe():
    assert stf.resolve("MOVER_TREND_PULLBACK", live=True) == "15m"
    assert stf.resolve("WHALE_MOMENTUM", live=True) == "1m"
    assert stf.resolve("MA_CROSS_TREND_SHIFT", live=True) == "1h"
    # Already 5m — live or dark makes no difference, and that is an agreement
    # rather than an application.
    assert stf.resolve("SR_FLIP_RETEST", live=True) == "5m"


def test_an_unmapped_setup_falls_back_but_is_counted_apart():
    """Unmapped is not agreement. A new evaluator inheriting 5m must be
    visible as unmapped, not as a path that happens to trade 5m."""
    assert stf.resolve("BRAND_NEW_PATH", live=True) == "5m"
    c = stf.get_counters().as_dict()
    assert c["unmapped"] == 1
    assert c["agreed"] == 0
    assert c["mismatched"] == 0


def test_declared_for_distinguishes_absent_from_five_minutes():
    """``None`` is deliberately not ``"5m"`` — a caller that cannot tell them
    apart cannot report a new evaluator as unmapped."""
    assert stf.declared_for("SR_FLIP_RETEST") == "5m"
    assert stf.declared_for("BRAND_NEW_PATH") is None


def test_the_census_counts_all_three_states():
    stf.resolve("MOVER_TREND_PULLBACK", live=False)   # mismatched
    stf.resolve("SR_FLIP_RETEST", live=False)         # agreed
    stf.resolve("NOPE", live=False)                   # unmapped
    c = stf.get_counters().as_dict()
    assert (c["resolved"], c["mismatched"], c["agreed"], c["unmapped"]) == (3, 1, 1, 1)
    # Dark, so nothing was applied even though one row disagrees.
    assert c["applied"] == 0


def test_applied_only_counts_a_real_change():
    stf.resolve("MOVER_TREND_PULLBACK", live=True)    # 5m -> 15m: applied
    stf.resolve("SR_FLIP_RETEST", live=True)          # already 5m: not applied
    c = stf.get_counters().as_dict()
    assert c["applied"] == 1


def test_the_census_denominator_is_resolutions_not_signals():
    """Six consumers call resolve() per candidate, so this counter is ~6x the
    signal count. Pinned because a book fraction computed from it would be
    inflated sixfold while looking entirely plausible — the per-signal fact
    lives on the structural-snap row instead."""
    for _ in range(6):
        stf.resolve("MOVER_TREND_PULLBACK", live=False)
    assert stf.get_counters().as_dict()["resolved"] == 6


def test_the_snap_row_carries_the_per_signal_census():
    """One row per signal — the denominator an ops panel can divide by."""
    from src import structural_snap as ss

    ss.reset_ledger(ss.SnapLedger(path=""))
    ss.reset_counters()
    try:
        class _Sig:
            signal_id = "TF-1"
            symbol = "TESTUSDT"
            setup_class = "MOVER_TREND_PULLBACK"
            channel = "SCALP"
            direction = "LONG"
            entry = 100.0
            stop_loss = 97.0
            tp1 = 103.0

        row = ss.stamp_and_apply(_Sig(), candles=None, min_sl_distance=0.0)
        assert row["score_tf_declared"] == "15m"
        assert row["score_tf_used"] == "5m"          # dark
        assert row["score_tf_mismatch"] is True
        assert row["score_tf_correction_live"] is False
    finally:
        ss.reset_ledger(None)
        ss.reset_counters()


def test_an_unmapped_setup_stamps_mismatch_none_not_false():
    """False means "checked, agrees". None means "cannot be checked". Folding
    them makes an unmapped evaluator read as a healthy 5m path forever."""
    from src import structural_snap as ss

    ss.reset_ledger(ss.SnapLedger(path=""))
    ss.reset_counters()
    try:
        class _Sig:
            signal_id = "TF-2"
            symbol = "TESTUSDT"
            setup_class = "BRAND_NEW_PATH"
            channel = "SCALP"
            direction = "LONG"
            entry = 100.0
            stop_loss = 97.0
            tp1 = 103.0

        row = ss.stamp_and_apply(_Sig(), candles=None, min_sl_distance=0.0)
        assert row["score_tf_declared"] is None
        assert row["score_tf_mismatch"] is None
    finally:
        ss.reset_ledger(None)
        ss.reset_counters()


def test_the_correction_is_reachable_because_the_context_carries_those_bars():
    """A correction to a timeframe the scanner never loads would be inert —
    ``_resolve_candles`` would fall straight back to 5m and every column would
    read healthy. Every declared timeframe must be in SEED_TIMEFRAMES."""
    from config import SEED_TIMEFRAMES

    seeded = {tf.interval for tf in SEED_TIMEFRAMES}
    missing = sorted(set(stf.TF_BY_SETUP.values()) - seeded)
    assert not missing, (
        f"declared timeframes the scanner never loads: {missing} — the "
        "correction would silently fall back to 5m"
    )
