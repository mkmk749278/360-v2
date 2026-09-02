"""Campaign state, and its two seams.

The module is small; the tests are about the joins. Two of them exist because
this repo has paid for the same defect at those exact seams before:

* the campaign key and the scanner's cooldown key must be the SAME key, driven
  off the real ``Scanner._cooldown_key_for`` rather than a hand-written tuple —
  a mock whose shape you chose asserts your assumption back at you;
* the loader must be CALLED, not merely defined — a flush with no load
  overwrites a file that looks healthy on disk, and the guard is the call site.
"""
from __future__ import annotations

import json
import time
from types import SimpleNamespace

import pytest

from src import campaign_state as cs


class _Dir:
    def __init__(self, value: str) -> None:
        self.value = value


def _sig(symbol="BTCUSDT", setup="MOVER_TREND_PULLBACK", direction="LONG", **kw):
    return SimpleNamespace(
        symbol=symbol, setup_class=setup, direction=_Dir(direction), **kw
    )


@pytest.fixture(autouse=True)
def _fresh_registry():
    """In-memory registry per test. ``path=""`` must never touch the disk."""
    cs.reset_for_tests(path="")
    yield
    cs.reset_for_tests(path="")


# --------------------------------------------------------------------------- #
# The read
# --------------------------------------------------------------------------- #


def test_first_leg_is_none_not_zero():
    """A campaign with no history is unknown, never "the last one lost"."""
    read = cs.read_for(_sig())
    assert read.leg_index == 0
    assert read.prev_won is None
    assert read.prev_age_h is None
    assert read.prev_outcome == ""
    # A blank needs a cause.
    assert read.absence_reason == "first_leg"


def test_a_win_then_a_loss_are_different_reads():
    reg = cs.get_registry()
    key = cs.key_for(_sig())
    now = time.time()

    reg.record_outcome(key, "PROFIT_LOCKED", pnl_pct=2.4, closed_at=now - 3600)
    won = reg.read(key, now=now)
    assert won.prev_won == 1.0
    assert won.leg_index == 1
    assert won.prev_outcome == "PROFIT_LOCKED"
    assert won.prev_pnl_pct == pytest.approx(2.4)
    assert won.prev_age_h == pytest.approx(1.0, abs=0.01)
    assert won.absence_reason is None

    reg.record_outcome(key, "SL_HIT", pnl_pct=-3.0, closed_at=now - 60)
    lost = reg.read(key, now=now)
    assert lost.prev_won == 0.0
    assert lost.leg_index == 2, "leg index counts closed legs, and only those"


def test_breakeven_is_neither_a_win_nor_folded_into_a_loss():
    """BREAKEVEN_EXIT scores 0.0 for `prev_won` under its own label.

    It is not in WINNING_LABELS, so it does not read as a win; it is not in
    LOSING_LABELS either, and the label survives on the row so the two remain
    separable downstream. On the delivered book their forward returns differ
    (-0.112% after a BE/expiry against -0.304% after a stop), which is exactly
    why pooling them would lose information.
    """
    reg = cs.get_registry()
    key = cs.key_for(_sig())
    reg.record_outcome(key, "BREAKEVEN_EXIT", pnl_pct=0.0)
    read = reg.read(key)
    assert read.prev_won == 0.0
    assert read.prev_outcome == "BREAKEVEN_EXIT"
    assert "BREAKEVEN_EXIT" not in cs.WINNING_LABELS
    assert "BREAKEVEN_EXIT" not in cs.LOSING_LABELS


def test_a_stale_campaign_reads_empty_and_is_not_deleted_by_the_read():
    """Past the horizon a campaign is absent, and reading never mutates.

    `read` runs on the scan path. A read that prunes is a write with a
    different name, and this repo's Cost Discipline section is about exactly
    that class of surprise.
    """
    reg = cs.get_registry()
    key = cs.key_for(_sig())
    now = time.time()
    reg.record_outcome(key, "PROFIT_LOCKED", pnl_pct=1.0, closed_at=now - 8 * 86400)

    assert reg.read(key, now=now).prev_won is None
    assert key in reg._state, "the read must not have deleted anything"
    # ...and inside the horizon the same entry is visible again.
    assert reg.read(key, now=now - 7 * 86400).prev_won == 1.0


def test_direction_and_setup_separate_campaigns():
    reg = cs.get_registry()
    reg.record_outcome(cs.key_for(_sig(direction="LONG")), "PROFIT_LOCKED", pnl_pct=1.0)
    assert reg.read(cs.key_for(_sig(direction="SHORT"))).prev_won is None
    assert reg.read(cs.key_for(_sig(setup="FAILED_AUCTION_RECLAIM"))).prev_won is None


def test_read_never_raises_on_a_broken_signal():
    """A measurement must never kill a scan."""
    assert cs.read_for(SimpleNamespace()).prev_won is None
    assert cs.key_for(SimpleNamespace(symbol="BTCUSDT", setup_class="")) is None


# --------------------------------------------------------------------------- #
# Seam 1: the key is the scanner's key
# --------------------------------------------------------------------------- #


def test_campaign_key_is_the_scanners_cooldown_key():
    """Driven off the REAL producer, not a hand-written tuple.

    `campaign_state` is the fourth consumer of `(symbol, setup_class,
    direction)` after the dispatch cooldown, the loss-streak escalation and the
    active-duplicate guard. Keyed even slightly differently it would be a
    different campaign under the same word — and a mock of the scanner's key
    would only assert whatever shape this test's author assumed.
    """
    from src.scanner import Scanner

    for sig in (
        _sig(),
        _sig(symbol="ethusdt", setup="FAILED_AUCTION_RECLAIM", direction="short"),
        _sig(symbol="", setup="X", direction="LONG"),
        SimpleNamespace(symbol="BTCUSDT", setup_class="X", direction=None),
    ):
        assert cs.key_for(sig) == Scanner._cooldown_key_for(sig)


# --------------------------------------------------------------------------- #
# Seam 2: persistence, and the two ways it goes wrong
# --------------------------------------------------------------------------- #


def test_in_memory_registry_writes_no_file(tmp_path, monkeypatch):
    """``path=""`` returns BEFORE the atomic write, not after.

    A ledger whose "don't persist" hook still created its temp file left a
    `.tmp` in the process cwd — the repo root under pytest — and then raised
    into `fail_open` on every test run for two months (2026-08-08).
    """
    monkeypatch.chdir(tmp_path)
    reg = cs.reset_for_tests(path="")
    reg.record_outcome(cs.key_for(_sig()), "PROFIT_LOCKED", pnl_pct=1.0)
    assert list(tmp_path.iterdir()) == []


def test_round_trip_survives_a_restart(tmp_path):
    """Persist then load: the contract a restart actually exercises."""
    path = tmp_path / "campaign_state_v1.json"
    reg = cs.CampaignRegistry(path=str(path))
    key = cs.key_for(_sig())
    now = time.time()
    reg.record_outcome(key, "PROFIT_LOCKED", pnl_pct=2.0, closed_at=now - 900)

    reloaded = cs.CampaignRegistry(path=str(path))
    assert reloaded.load() == 1
    read = reloaded.read(key, now=now)
    assert read.prev_won == 1.0
    assert read.leg_index == 1
    assert read.prev_pnl_pct == pytest.approx(2.0)
    assert read.prev_age_h == pytest.approx(0.25, abs=0.01)


def test_an_unknown_schema_starts_empty_and_is_counted(tmp_path):
    """State, not evidence — but a silent refusal is still not allowed.

    A measurement ledger must accept its own additive predecessors or it
    destroys the window an adoption decision reads. This file holds current
    state with a seven-day horizon, so starting empty costs a few hours of leg
    history and no analysis at all. What it must NOT do is start empty
    silently: an unreadable file and a fresh deploy look identical otherwise.
    """
    path = tmp_path / "campaign_state_v1.json"
    path.write_text(json.dumps({"schema": 99, "rows": {"A|B|LONG": {"n": 3}}}))
    reg = cs.CampaignRegistry(path=str(path))
    assert reg.load() == 0
    assert reg.load_errors == 1
    assert reg.summary()["load_errors"] == 1


def test_load_is_called_at_first_use_not_merely_defined():
    """`get_registry` loads. *Defining* a loader is not calling one."""
    import ast
    import inspect

    src = inspect.getsource(cs.get_registry)
    tree = ast.parse(src.strip())
    calls = {
        n.func.attr
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
    }
    assert "load" in calls, "get_registry must call load(), not just construct"


def test_the_scanner_calls_the_loader_at_boot():
    """Pin the CALL SITE, not the method — the 2026-08-06 defect's own lesson."""
    import ast
    import pathlib

    src = pathlib.Path("src/scanner/__init__.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    found = any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "get_registry"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id.endswith("cs")
        for node in ast.walk(tree)
    )
    assert found, "the scanner must call campaign_state.get_registry()"


def test_the_scanner_records_the_outcome_where_it_becomes_true():
    """Pin the WRITER's call site, not just the reader's.

    The loader test above proves the registry is loaded; this one proves
    something ever writes it. Both halves of a seam look complete on their own —
    a reader with no writer produces a column that is honestly, permanently
    `first_leg` on every row, which is indistinguishable on screen from a book
    with no repeat entries. `on_signal_lifecycle_outcome` is where a terminal
    outcome becomes true, and it is the only place this may be called from.
    """
    import ast
    import pathlib

    src = pathlib.Path("src/scanner/__init__.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    writers = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "on_signal_lifecycle_outcome"
        and any(
            isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
            and call.func.attr == "record_outcome"
            for call in ast.walk(node)
        )
    ]
    assert writers, (
        "on_signal_lifecycle_outcome must call record_outcome — a campaign "
        "reader with no writer reads `first_leg` forever and looks correct"
    )


def test_pruning_bounds_the_file(tmp_path):
    reg = cs.CampaignRegistry(path=str(tmp_path / "s.json"))
    now = time.time()
    for i in range(5):
        reg.record_outcome(("SYM%d" % i, "S", "LONG"), "SL_HIT", closed_at=now - 9 * 86400)
    reg.record_outcome(("FRESH", "S", "LONG"), "SL_HIT", closed_at=now)
    assert reg.summary()["campaigns"] == 1
    assert reg.pruned >= 4
