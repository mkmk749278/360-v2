"""An additive schema bump must not destroy the ledger it extends.

This exists because it already happened. `sar_live_shadow.LEDGER_SCHEMA` went
1 → 2 to add the held-to-stop arm — purely additive, and the constant's own
comment said *"nothing is purged and every schema-1 row keeps its full standing
in the SAR verdict"*. `load()` compared `!=` and returned, so the first flush
after the deploy overwrote **371 rows**: the entire SAR measurement window.

Nothing crashed. Every panel rendered correctly over zero rows, which reads
exactly like a quiet lane.

:func:`test_the_bump_that_destroyed_the_window_now_loads` is the regression, and
it fails against the pre-fix loader — which is the only thing that makes it a
test of the fix rather than of the author's intentions.
"""

from __future__ import annotations

import json

import pytest

from src import ledger_schema


# --------------------------------------------------------------------------- #
# The decision itself
# --------------------------------------------------------------------------- #


def test_the_current_schema_always_loads():
    assert ledger_schema.accepts(2, 2, frozenset()) == (True, None)


def test_an_additive_predecessor_loads():
    ok, why = ledger_schema.accepts(1, 2, frozenset({1}))
    assert ok is True and why is None


def test_an_undeclared_predecessor_is_refused_as_redefined():
    """Silence is treated as "this bump redefined something" — the safe way.

    Losing a window is recoverable by waiting; silently pooling two populations
    that mean different things is not detectable at all.
    """
    ok, why = ledger_schema.accepts(1, 2, frozenset())
    assert ok is False and why == ledger_schema.REFUSE_REDEFINED


def test_a_newer_schema_is_always_refused_even_if_listed():
    """Reading forward means guessing what a field the writer added will mean.

    This is the rollback case: an old build meeting a file a newer one wrote.
    """
    ok, why = ledger_schema.accepts(3, 2, frozenset({1, 2, 3}))
    assert ok is False and why == ledger_schema.REFUSE_NEWER


@pytest.mark.parametrize("bad", [None, 0, "", "abc", {}, -1])
def test_an_unreadable_schema_is_its_own_refusal(bad):
    """Named apart from the others because the next move differs: a missing or
    corrupt schema is a writer fault, not a version decision."""
    ok, why = ledger_schema.accepts(bad, 2, frozenset({1}))
    assert ok is False
    assert why in (ledger_schema.REFUSE_UNREADABLE,)


# --------------------------------------------------------------------------- #
# The regression, on the real ledger
# --------------------------------------------------------------------------- #


def test_the_bump_that_destroyed_the_window_now_loads(tmp_path):
    """A schema-1 SAR ledger must survive a schema-2 build.

    Fails against the pre-fix `load()`, which is the point. The rows load with
    no `hold_status`, which is correct rather than incomplete — a schema-1 arm
    was never offered a held arm, so it is owed nothing and every reader already
    buckets it as `pre_arm`.
    """
    from src import sar_live_shadow as live

    path = tmp_path / "arms.json"
    path.write_text(json.dumps({
        "schema": 1,
        "written_at": 1_700_000_000.0,
        "open": [{"arm_id": "a:15m", "symbol": "X", "status": "RUNNING"}],
        "resolved": [
            {"arm_id": "b:15m", "symbol": "Y", "status": "CLOSED_SAR_FLIP",
             "pnl_level_pct": -1.5},
            {"arm_id": "c:5m", "symbol": "Z", "status": "CLOSED_SL",
             "pnl_level_pct": 2.0},
        ],
    }))

    ledger = live.SarLiveLedger(path=str(path))
    ledger.load()

    assert len(ledger.open_arms()) == 1, "the schema-1 window was discarded"
    assert len(ledger.resolved_arms()) == 2, "the schema-1 window was discarded"
    # …and the rows are usable, not merely present.
    assert {r["arm_id"] for r in ledger.resolved_arms()} == {"b:15m", "c:5m"}
    assert ledger.get("a:15m") is not None


def test_a_schema_1_row_carries_no_held_arm_and_is_owed_nothing(tmp_path):
    """Loading old rows must not resurrect them into the open measurement set."""
    from src import sar_live_shadow as live

    path = tmp_path / "arms.json"
    path.write_text(json.dumps({
        "schema": 1,
        "open": [{"arm_id": "a:15m", "status": "RUNNING"}],
        "resolved": [{"arm_id": "b:15m", "status": "CLOSED_SL"}],
    }))
    ledger = live.SarLiveLedger(path=str(path))
    ledger.load()

    old = ledger.resolved_arms()[0]
    assert live.hold_arm_open(old) is False
    assert live.owed_verdict(old) is False


def test_a_genuinely_incompatible_schema_still_drops(tmp_path):
    """The fix must not become "load anything" — that is the opposite failure."""
    from src import sar_live_shadow as live

    path = tmp_path / "arms.json"
    path.write_text(json.dumps({
        "schema": 99,  # newer than this build
        "open": [{"arm_id": "a:15m", "status": "RUNNING"}],
        "resolved": [],
    }))
    ledger = live.SarLiveLedger(path=str(path))
    ledger.load()
    assert ledger.open_arms() == []


# --------------------------------------------------------------------------- #
# Derived: every schema-gated ledger must declare its intent
# --------------------------------------------------------------------------- #


def test_every_schema_gated_ledger_declares_what_it_can_read():
    """Derived from the tree, not written as a list.

    Five modules carried the identical `!=` loader, so this was one mistake
    waiting in five places for whoever bumped next. A new ledger that gates on a
    schema must say which older ones it reads — even if the answer is "none" —
    so the choice is made rather than inherited.
    """
    import importlib
    import pathlib
    import re

    src = pathlib.Path(__file__).resolve().parents[1] / "src"
    offenders = []
    for path in sorted(src.glob("*.py")):
        text = path.read_text()
        if "def load(" not in text:
            continue
        if not re.search(r'\bget\("schema"\)', text):
            continue
        mod = importlib.import_module(f"src.{path.stem}")
        if not hasattr(mod, "ADDITIVE_FROM_SCHEMAS"):
            offenders.append(path.name)
    assert not offenders, (
        f"schema-gated ledger(s) with no ADDITIVE_FROM_SCHEMAS declaration: "
        f"{offenders}. Declare which older schemas the build can read — "
        f"frozenset() is a valid answer, an absent one is not."
    )


def test_no_schema_gated_loader_still_compares_with_bare_inequality():
    """Pin the shape, so the old form cannot come back by 'simplification'."""
    import pathlib
    import re

    src = pathlib.Path(__file__).resolve().parents[1] / "src"
    offenders = []
    for path in sorted(src.glob("*.py")):
        text = path.read_text()
        if re.search(r'int\(\s*\w+\.get\("schema"\)[^)]*\)\s*!=', text):
            offenders.append(path.name)
    assert not offenders, (
        f"{offenders} still drop a ledger on bare schema inequality — that is "
        f"what destroyed 371 SAR rows on 2026-08-09. Use ledger_schema.accepts()."
    )
