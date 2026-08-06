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


def _ledger_class(mod_name: str):
    """The ledger class in `src/<mod>.py` that defines `flush`."""
    tree = ast.parse((REPO / "src" / f"{mod_name}.py").read_text())
    for n in tree.body:
        if isinstance(n, ast.ClassDef) and any(
            isinstance(b, ast.FunctionDef) and b.name == "flush" for b in n.body
        ):
            return n
    return None


def test_every_ledger_that_flushes_also_loads():
    """A round trip is a contract, and this is the return leg.

    `structural_snap` and `structural_veto` both persisted every cycle and had
    **no `load()` at all**, so each restart began with an empty ring and the
    first flush after boot OVERWROTE the file with whatever had accumulated
    since. The snap ledger went 12 rows to 8 across one afternoon's deploys
    while its own panel read "nothing evicted" — because nothing was: the
    previous window was destroyed, not rotated (owner data, 2026-08-06).

    **Flush without load is worse than neither.** Without flush the data is
    merely in memory; with flush and no load it is actively deleted on every
    deploy, while a file on disk makes the lane look persistent.

    #842's class — "follow it all the way to disk and back" — where the back
    half did not exist.
    """
    missing = []
    for mod in sorted(_modules_with_a_persisted_ledger()):
        cls = _ledger_class(mod)
        if cls is None:
            continue
        if not any(
            isinstance(b, ast.FunctionDef) and b.name == "load" for b in cls.body
        ):
            missing.append(f"{mod}.{cls.name}")
    assert not missing, (
        f"ledgers that flush but never load: {missing} — every restart "
        "silently destroys the window they wrote"
    )


def test_get_ledger_actually_calls_load():
    """Defining `load` is not calling it. `get_ledger` is the one construction
    site, so the call belongs there — pin the call site, not the method."""
    missing = []
    for mod in sorted(_modules_with_a_persisted_ledger()):
        tree = ast.parse((REPO / "src" / f"{mod}.py").read_text())
        fn = next(
            (n for n in tree.body
             if isinstance(n, ast.FunctionDef) and n.name == "get_ledger"),
            None,
        )
        if fn is None:
            continue
        calls_load = any(
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == "load"
            for n in ast.walk(fn)
        )
        if not calls_load:
            missing.append(mod)
    assert not missing, (
        f"get_ledger() does not call load() in: {missing} — the ledger comes "
        "back empty and the next flush overwrites the file"
    )
