"""Every persisted measurement ledger must have a caller that flushes it.

Owner-caught 2026-08-06: `structural_veto` stamped rows into an in-memory ring
and **nothing ever wrote them to disk**. `/engine-data/structural_veto_v1.json`
never existed, so the ops page read `UNREADABLE` with 0 stamped rows from the day
it shipped — while that page is the one measuring ~97% of the book, and the
session had pointed at it three times as the highest-value surface available.

Its own `flush()` even carries the `force=True` docstring about idle lanes
rendering STALE. #839's rule, verbatim: **a docstring describing a heartbeat is
not a heartbeat — find the caller.** There was none.

The requirement is DERIVED, not listed: any module exposing `get_ledger()` and a
`flush()` on it must appear in the maintenance loop. A hand-kept list of lanes is
a floor, silent by construction on the fourth one — which is exactly how this one
was missed while two siblings beside it were wired.
"""
from __future__ import annotations

import ast
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Modules with a persisted ledger that are deliberately flushed elsewhere.
#: Each entry names WHERE, so an exemption cannot hide a missing caller.
FLUSH_EXEMPT: dict[str, str] = {
    # `dark_emission` is flushed by its own resolver loop, which must run on the
    # money-path clock rather than on the slow maintenance tick.
    "dark_emission": "resolve loop",
    # Written through by the router on delivery, not on a tick.
    "sar_exit_shadow": "router promote path",
    "sar_live_shadow": "monitor loop",
}


def _modules_with_a_persisted_ledger() -> set[str]:
    """`src/*.py` exposing `get_ledger()` whose ledger class defines `flush`."""
    out: set[str] = set()
    for f in (REPO / "src").glob("*.py"):
        tree = ast.parse(f.read_text())
        has_get = any(
            isinstance(n, ast.FunctionDef) and n.name == "get_ledger"
            for n in tree.body
        )
        has_flush = any(
            isinstance(n, ast.ClassDef)
            and any(
                isinstance(b, ast.FunctionDef) and b.name == "flush" for b in n.body
            )
            for n in tree.body
        )
        if has_get and has_flush:
            out.add(f.stem)
    return out


def test_every_persisted_ledger_has_a_flush_caller():
    """A ledger nobody flushes is a measurement that does not survive a restart
    and a file the ops page can never find."""
    src = (REPO / "src" / "main.py").read_text()
    missing = []
    for mod in sorted(_modules_with_a_persisted_ledger()):
        if mod in FLUSH_EXEMPT:
            continue
        # The import and the flush must both be present — importing a module and
        # never flushing it is the state this test exists to catch.
        if f"from src import {mod} as " not in src or ".flush(" not in src:
            missing.append(mod)
            continue
        alias = src.split(f"from src import {mod} as ", 1)[1].split("\n", 1)[0].strip()
        if f"{alias}.get_ledger().flush(" not in src:
            missing.append(mod)
    assert not missing, (
        f"persisted ledgers with no flush caller in main.py: {missing}. "
        "Wire them into the maintenance loop, or add to FLUSH_EXEMPT naming "
        "where they are flushed instead."
    )


def test_the_structural_veto_is_flushed_with_force():
    """`force=True` because an idle lane that stops writing renders STALE, and
    "quiet market" and "the lane stopped" are the two states an ops page cannot
    tell apart without a heartbeat."""
    src = (REPO / "src" / "main.py").read_text()
    assert "_sv.get_ledger().flush(force=True)" in src


def test_the_veto_exposes_measure_enabled_like_its_siblings():
    """The loop gates every flush on one, and not having one is how this module
    was left out of the loop in the first place."""
    from src import structural_snap, structural_veto

    assert callable(structural_veto.measure_enabled)
    assert callable(structural_snap.measure_enabled)
    assert isinstance(structural_veto.measure_enabled(), bool)
