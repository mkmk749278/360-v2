"""The governed-exit record — a trade history, not a measurement lane.

Owner, 2026-08-11: *"also keep traded history Trail governor (LIVE) tab not only
opened positions"*.

#916's realized-exit ring lives in `trail_governor._health`: in memory, capped
at 40, destroyed by every deploy. On a mechanism that re-deploys several times a
session that is not history, it is the last few minutes.

What makes this ledger different from every other one here is the thing most of
these tests are about: **these rows cannot be re-derived.** A destroyed
measurement window comes back by waiting; a destroyed trade record does not.
"""
from __future__ import annotations

import json
import os

import pytest

from src import ledger_schema, trail_history as th
from src.execution import position_state as ps
from src.execution import trail_governor as tg


def _row(**over):
    base = {
        "ts": 1_700_000_000.0, "signal_id": "SIG1", "uid": "UID1",
        "symbol": "BTCUSDT", "side": "LONG", "mechanism": "sar",
        "exit_kind": th.FILL_TRAIL_STOP, "entry": 100.0, "exit": 98.0,
        "pnl_pct": -2.0, "designed_sl": 97.0, "parked_stop": 98.0, "seq": 3,
    }
    base.update(over)
    return base


@pytest.fixture(autouse=True)
def _clean():
    th.reset_ledger(th.TrailExitLedger(path=""))
    yield
    th.reset_ledger(None)


# --------------------------------------------------------------------------- #
# The round trip — the leg that did not exist on two other ledgers
# --------------------------------------------------------------------------- #


def test_the_record_survives_a_restart(tmp_path):
    """GUARD. Flush without load is worse than neither: the ring starts empty
    and the first flush after a deploy OVERWRITES the file. That erased the
    structural ledgers four times in an afternoon. Here it would erase the
    trade record, which nothing regenerates."""
    path = str(tmp_path / "trail_exits_v1.json")
    a = th.TrailExitLedger(path=path)
    a.add(_row(signal_id="S1"))
    a.add(_row(signal_id="S2", exit_kind=th.FILL_FLIP_CLOSE, pnl_pct=1.5))
    assert a.flush(force=True)

    b = th.TrailExitLedger(path=path)
    b.load()
    assert [r["signal_id"] for r in b.rows()] == ["S1", "S2"]
    assert [r["pnl_pct"] for r in b.rows()] == [-2.0, 1.5]


def test_a_reload_then_flush_does_not_shrink_the_record(tmp_path):
    """The specific failure mode, stated as a sequence rather than trusted to
    the pair of tests above: boot, load, add one, flush — three rows, not one."""
    path = str(tmp_path / "trail_exits_v1.json")
    a = th.TrailExitLedger(path=path)
    a.add(_row(signal_id="S1"))
    a.add(_row(signal_id="S2"))
    a.flush(force=True)

    b = th.TrailExitLedger(path=path)
    b.load()
    b.add(_row(signal_id="S3"))
    b.flush(force=True)

    c = th.TrailExitLedger(path=path)
    c.load()
    assert [r["signal_id"] for r in c.rows()] == ["S1", "S2", "S3"]


def test_get_ledger_actually_calls_load(tmp_path, monkeypatch):
    """Defining a method is not calling it — pin the call site. Both structural
    ledgers defined `load()` and neither ran it."""
    path = str(tmp_path / "trail_exits_v1.json")
    seed = th.TrailExitLedger(path=path)
    seed.add(_row(signal_id="SEEDED"))
    seed.flush(force=True)

    monkeypatch.setattr(th, "_DEFAULT_PATH", path)
    th.reset_ledger(None)
    assert [r["signal_id"] for r in th.get_ledger().rows()] == ["SEEDED"]


def test_a_newer_schema_is_refused_and_not_overwritten(tmp_path):
    """Reading forward means guessing what a field a newer build added is going
    to mean. Refused — and the refusal must not itself destroy the file, so the
    load leaves it alone and only a later flush rewrites it."""
    path = str(tmp_path / "trail_exits_v1.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"schema": th.SCHEMA + 1, "rows": [_row()]}, fh)
    led = th.TrailExitLedger(path=path)
    led.load()
    assert led.rows() == []
    with open(path, "r", encoding="utf-8") as fh:
        assert json.load(fh)["schema"] == th.SCHEMA + 1


def test_additive_set_is_declared_not_defaulted():
    """`accepts` takes it as a required argument so a new ledger cannot inherit
    the old `!=` behaviour by forgetting. `frozenset()` is a valid answer that
    somebody chose — there is no older schema, because this is the first."""
    assert isinstance(th.ADDITIVE_FROM_SCHEMAS, frozenset)
    ok, _ = ledger_schema.accepts(th.SCHEMA, th.SCHEMA, th.ADDITIVE_FROM_SCHEMAS)
    assert ok


def test_in_memory_path_never_touches_the_disk(tmp_path, monkeypatch):
    """`path=""` is what tests construct with. Returning AFTER the side effect
    wrote stray .tmp files into the repo root for two months and raised a
    non-failure into fail_open on every test run."""
    monkeypatch.chdir(tmp_path)
    led = th.TrailExitLedger(path="")
    led.add(_row())
    assert led.flush(force=True) is False
    assert os.listdir(tmp_path) == []


# --------------------------------------------------------------------------- #
# It is a record, not a lane
# --------------------------------------------------------------------------- #


def test_the_record_has_no_off_switch():
    """GUARD, and the reason is the point. Every other lane gates its flush on
    its own measurement switch. Gating this one on TRAIL_GOVERNOR_ENABLED would
    stop persisting exits the moment somebody switches the governor off — the
    first thing anyone does when a live mechanism misbehaves, i.e. exactly when
    the last few exits are the evidence."""
    assert th.measure_enabled() is True


def test_the_flush_caller_does_not_gate_on_the_governor_switch():
    """...and the loop must not re-introduce the gate this module refused.

    Asserted on the block's **code**, with comment lines stripped. The first cut
    matched the raw text and failed on the comment that explains *why* the gate
    is absent — a check that a word is missing cannot tell a prohibition from
    its own rationale, and the claim here was always about what executes.
    """
    import pathlib

    src = (pathlib.Path(__file__).resolve().parents[1] / "src" / "main.py").read_text()
    block = src.split("Trail-governor exit history", 1)[1].split("Stop-geometry", 1)[0]
    code = "\n".join(
        ln for ln in block.splitlines() if not ln.lstrip().startswith("#")
    )
    assert "_th.measure_enabled()" in code
    assert "_th.get_ledger().flush(force=True)" in code
    assert "TRAIL_GOVERNOR_ENABLED" not in code
    assert "trail_governor_enabled" not in code


def test_the_cap_publishes_its_eviction_count():
    """A verdict on a capped buffer is a verdict on a sample, and a reader in
    another process cannot see the cap."""
    led = th.TrailExitLedger(path="", max_rows=3)
    for i in range(5):
        led.add(_row(signal_id=f"S{i}"))
    stats = led.stats()
    assert stats == {"rows": 3, "evicted": 2, "max_rows": 3, "complete": False}
    assert [r["signal_id"] for r in led.rows()] == ["S2", "S3", "S4"]


def test_an_uncapped_record_says_it_is_complete():
    led = th.TrailExitLedger(path="", max_rows=10)
    led.add(_row())
    assert led.stats()["complete"] is True


# --------------------------------------------------------------------------- #
# One exit, two observers
# --------------------------------------------------------------------------- #


def test_the_same_fill_seen_twice_is_one_trade():
    """The FSM books a trail fill from the user-data stream; the sweep's -2022
    branch books it when it finds the book already flat. That is one exit seen
    by two observers, and counting it twice would double the book."""
    led = th.TrailExitLedger(path="")
    assert led.add(_row()) is True
    assert led.add(_row()) is False
    assert len(led.rows()) == 1


def test_the_two_fills_on_one_signal_are_not_a_duplicate():
    """Different `exit_kind` on the same signal is a genuinely different event
    — the dedupe key must not swallow it."""
    led = th.TrailExitLedger(path="")
    assert led.add(_row(exit_kind=th.FILL_TRAIL_STOP))
    assert led.add(_row(exit_kind=th.FILL_FLIP_CLOSE))
    assert len(led.rows()) == 2


def test_two_users_on_one_signal_are_two_trades():
    """The mechanism is per user, so one signal can close on several accounts."""
    led = th.TrailExitLedger(path="")
    assert led.add(_row(uid="A"))
    assert led.add(_row(uid="B"))
    assert len(led.rows()) == 2


# --------------------------------------------------------------------------- #
# The summary keeps the two fills apart
# --------------------------------------------------------------------------- #


def test_the_summary_never_blends_the_two_fills():
    """Their difference IS the cost of confirmation, which is the number the
    mechanism's design turns on. There is no pooled average, exactly as on
    `/signals/sar-live`, and a test asserts the key does not exist."""
    led = th.TrailExitLedger(path="")
    led.add(_row(signal_id="A", exit_kind=th.FILL_TRAIL_STOP, pnl_pct=-2.0))
    led.add(_row(signal_id="B", exit_kind=th.FILL_FLIP_CLOSE, pnl_pct=4.0))
    out = th.summary(led.rows())
    assert set(out["by_fill"]) == {th.FILL_TRAIL_STOP, th.FILL_FLIP_CLOSE}
    assert out["by_fill"][th.FILL_TRAIL_STOP]["avg_pnl_pct"] == pytest.approx(-2.0)
    assert out["by_fill"][th.FILL_FLIP_CLOSE]["avg_pnl_pct"] == pytest.approx(4.0)
    assert "avg_pnl_pct" not in out
    assert "total_pnl_pct" not in out


def test_an_unpriced_row_is_counted_apart_not_averaged_as_flat():
    """An accepted MARKET order reports no average until it fills. A zero
    averages in as a flat trade, which is a claim; None says it does not know."""
    led = th.TrailExitLedger(path="")
    led.add(_row(signal_id="A", pnl_pct=-2.0))
    led.add(_row(signal_id="B", pnl_pct=None))
    out = th.summary(led.rows())
    assert out["n"] == 2
    assert out["unpriced"] == 1
    assert out["by_fill"][th.FILL_TRAIL_STOP]["n"] == 1
    assert out["by_fill"][th.FILL_TRAIL_STOP]["avg_pnl_pct"] == pytest.approx(-2.0)


# --------------------------------------------------------------------------- #
# The seam: the governor must actually write to it
# --------------------------------------------------------------------------- #


def test_recording_an_outcome_reaches_the_persistent_record():
    """GUARD (fails pre-fix — #916 wrote only to the in-memory ring).

    A ledger nobody writes to is the mirror image of one nobody reads, and both
    render as a full-looking page describing nothing.
    """
    tg.reset_health_for_test()
    pos = ps.Position(
        signal_id="SIGX", firebase_uid="UIDX", symbol="ETHUSDT", side="SHORT",
        state=ps.PositionState.OPEN, entry_price_target=50.0,
        entry_price_filled=50.0, sl_price=51.5, tp1_price=48.0,
        tp2_price=46.0, tp3_price=44.0, total_qty=1.0, tp1_qty=0.3,
        tp2_qty=0.3, tp3_qty=0.4, exit_mechanism="sar",
        trail_stop_price=49.5, trail_stop_seq=2,
    )
    tg.record_outcome(pos, exit_price=49.0, exit_kind=th.FILL_TRAIL_STOP)
    rows = th.get_ledger().rows()
    assert len(rows) == 1
    assert rows[0]["symbol"] == "ETHUSDT"
    assert rows[0]["uid"] == "UIDX"
    # Signed toward the trade, same convention as the arm's `pnl_level_pct`.
    assert rows[0]["pnl_pct"] == pytest.approx(2.0)


def test_a_history_failure_never_costs_the_exit_that_produced_it(monkeypatch):
    """Fail-open, but counted. Losing the record row is bad; losing the close
    that produced it would be worse."""
    tg.reset_health_for_test()

    def _boom(row):
        raise RuntimeError("disk gone")

    monkeypatch.setattr(th, "record", _boom)
    pos = ps.Position(
        signal_id="SIGY", firebase_uid="UIDY", symbol="BTCUSDT", side="LONG",
        state=ps.PositionState.OPEN, entry_price_target=100.0,
        entry_price_filled=100.0, sl_price=97.0, tp1_price=103.0,
        tp2_price=106.0, tp3_price=110.0, total_qty=1.0, tp1_qty=0.3,
        tp2_qty=0.3, tp3_qty=0.4, exit_mechanism="sar",
    )
    tg.record_outcome(pos, exit_price=98.0, exit_kind=th.FILL_TRAIL_STOP)
    # The in-memory ring still has it, so the page is not blank either.
    assert len(tg.health()["outcomes"]) == 1


def test_the_diag_publishes_the_record_with_its_denominator():
    """`history` without `history_stats` is a sample presented as a population."""
    tg.reset_health_for_test()
    led = th.TrailExitLedger(path="", max_rows=2)
    led.add(_row(signal_id="A"))
    led.add(_row(signal_id="B"))
    led.add(_row(signal_id="C"))
    th.reset_ledger(led)
    diag = tg.build_diag()
    assert "history" in diag and "history_stats" in diag
    assert diag["history_stats"]["evicted"] == 1
    # Newest FIRST for a reader; the ledger's own order is newest last.
    assert [r["signal_id"] for r in diag["history"]] == ["C", "B"]
