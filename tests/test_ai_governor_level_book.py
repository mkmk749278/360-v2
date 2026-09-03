"""The governor's menu reads the engine's Level Book — and the wire is pinned.

v1's module map said `ai_governor_menu` *"reads `level_book`,
`volume_profile`, `structural_levels`"*. It read none of them: it ran a private
pivot scan over the raw high/low arrays. That is the eighth recurrence in these
repos of a description asserting a property the code beneath it does not have,
checkable in one command.

Repairing it by adding a parameter would be the *other* defect in the same
family — `build_channel_signal` accepted `candle_highs` and gated a structural
snap on `if candle_highs is not None`, under a docstring saying every evaluator
passed it, while `grep` matched only the parameter's own definition. So the
wire is asserted here from both ends: the menu produces Level Book candidates
when given real `Level` objects, and `main.py` actually hands the scanner's
book to the monitor.
"""
from __future__ import annotations

import ast
import inspect
import pathlib
from typing import Any, Dict, List

import numpy as np
import pytest

from src.execution import ai_governor as gov
from src.execution import ai_governor_menu as menu
from src.level_book import Level


def _series(n: int = 120) -> Dict[str, Any]:
    """A series that actually oscillates, so the pivot detector finds pivots.

    A monotonic ramp has none — which is a fixture that quietly asserts nothing
    about the swing half of the menu while looking like it does.

    Chosen against the REAL detector rather than by eye: `find_swing_levels`
    scans only the last 20 candles with a +/-3 window, so a slow oscillation
    produces none there — the first two versions of this fixture asserted
    nothing about the swing half of the menu while appearing to.
    """
    x = np.arange(n, dtype=float)
    base = 104.0 + 3.0 * np.sin(2 * np.pi * x / 8.0)
    return {"high": base + 0.4, "low": base - 0.4, "close": base}


def _menu_with(levels: List[Level], **kw: Any) -> menu.Menu:
    s = _series()
    args = dict(
        side="LONG", entry=100.0, current_sl=98.0, current_tp1=110.0,
        highs=s["high"], lows=s["low"], closes=s["close"],
        last_price=104.0, book_levels=levels,
    )
    args.update(kw)
    return menu.build_menu(**args)


# ---------------------------------------------------------------------------
# The menu reads the REAL dataclass
# ---------------------------------------------------------------------------


def test_a_real_level_becomes_a_candidate():
    """Driven with `level_book.Level`, not a dict this test invented.

    `zone_distance_atr` read a zone's edges by guessing five key names, none of
    which its only producer carried, and its tests passed on a shape nothing
    has ever emitted. So the producer's own type is what goes in here.
    """
    out = _menu_with([Level(price=106.0, type="resistance", source_tf="4h", score=9.0)])
    kinds = {c.kind for c in out.tp}
    assert menu.KIND_LEVEL in kinds, "a Level Book resistance must reach the TP menu"
    picked = [c for c in out.tp if c.kind == menu.KIND_LEVEL]
    assert any(abs(c.price - 106.0) < 1e-9 for c in picked)


def test_the_side_decides_which_level_type_is_a_target():
    """A long takes profit into resistance; a short into support. Reading the
    wrong side is the `cvd_slope` sign error, which scored every SHORT
    backwards for a month without producing an empty column."""
    long_menu = _menu_with([Level(price=106.0, type="support", source_tf="1h")])
    assert not [c for c in long_menu.tp if c.kind == menu.KIND_LEVEL], (
        "support is not a LONG's take-profit"
    )
    short_menu = _menu_with(
        [Level(price=94.0, type="support", source_tf="1h")],
        side="SHORT", current_sl=102.0, current_tp1=90.0, last_price=96.0,
    )
    assert [c for c in short_menu.tp if c.kind == menu.KIND_LEVEL], (
        "support IS a SHORT's take-profit"
    )


def test_level_candidates_obey_nearer_only_and_tighter_only():
    """The invariants do not relax because the price came from the book."""
    out = _menu_with([
        Level(price=130.0, type="resistance", source_tf="1d", score=99.0),  # further
        Level(price=90.0, type="support", source_tf="1d", score=99.0),      # looser
    ])
    assert not [c for c in out.tp if c.kind == menu.KIND_LEVEL], "TP moved further"
    assert not [c for c in out.sl if c.kind == menu.KIND_LEVEL], "SL widened"


def test_no_book_is_not_the_book_saying_none():
    """Absence of knowledge is not a reading — and neither is an exception."""
    assert not [c for c in _menu_with([]).tp if c.kind == menu.KIND_LEVEL]
    assert not [c for c in _menu_with(None).tp if c.kind == menu.KIND_LEVEL]
    # A shape the book never produces is skipped, not raised on.
    junk = _menu_with([object(), {"price": 106.0}])
    assert junk.tp, "the swing candidates must survive an unreadable book entry"


def test_swing_candidates_survive_alongside_book_candidates():
    """Offered BESIDE the pivots, never instead of them: a trigger-timeframe
    swing and a 4h level are different facts."""
    out = _menu_with([Level(price=106.0, type="resistance", source_tf="4h", score=9.0)])
    kinds = {c.kind for c in out.tp}
    assert menu.KIND_SWING in kinds and menu.KIND_LEVEL in kinds
    keys = [c.key for c in out.tp]
    assert len(keys) == len(set(keys)), "candidate keys must stay unique"


# ---------------------------------------------------------------------------
# The wire — pinned at the call site, not at the import
# ---------------------------------------------------------------------------


def test_the_governor_passes_book_levels_to_the_menu():
    """`_build_menu_for` must actually forward them.

    Asserted on the AST rather than by reading: a parameter that is accepted
    and dropped is exactly the defect this file exists to prevent.
    """
    tree = ast.parse(inspect.getsource(gov._build_menu_for).lstrip())
    kwargs = {
        kw.arg
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        for kw in node.keywords
        if kw.arg
    }
    assert "book_levels" in kwargs, "_build_menu_for must pass book_levels"


def test_the_sweep_forwards_the_level_getter():
    src = inspect.getsource(gov.sweep)
    assert "level_getter" in src, "sweep must thread the getter to the menu builder"


def test_main_hands_the_scanners_level_book_to_the_monitor():
    """The end of the wire, parsed out of `main.py`.

    Without this the parameter above would be real and unreachable — accepted
    by everything and passed by nothing, which is how a repair reads as done and
    changes nothing at all.
    """
    source = (pathlib.Path(__file__).resolve().parents[1] / "src" / "main.py").read_text()
    tree = ast.parse(source)
    assigns = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        for t in node.targets
        if isinstance(t, ast.Attribute) and t.attr == "_level_getter"
    ]
    assert assigns, "main.py must set monitor._level_getter"
    wired = ast.unparse(assigns[0])
    assert "level_book" in wired and "get_levels" in wired, (
        f"the getter must read the scanner's LevelBook, got: {wired}"
    )


def test_the_monitor_passes_its_getter_into_the_sweep():
    from src import trade_monitor

    src = inspect.getsource(trade_monitor)
    assert "level_getter=self._level_getter" in src, (
        "trade_monitor must forward its getter to ai_governor.sweep"
    )
