"""Phase 1d/1e: the pair book — level outcomes, notes, reads and profile stamps."""
from __future__ import annotations

import json
import sqlite3

import numpy as np
import pytest

from src import analyst_pair_book as B
from src import analyst_plan as P
from src import diag_catalog
from tests.test_analyst_plan import ADMIT, NOW, _plan, _setup_engine


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    led = P.Ledger(str(tmp_path / "plans.sqlite"))
    monkeypatch.setattr(P, "_ledger", led)
    B._reads.clear()
    return led


def _bars(highs, lows, closes, t0=0):
    n = len(closes)
    return (np.arange(n, dtype=float) * 300_000 + t0, np.array(highs, float),
            np.array(lows, float), np.array(closes, float))


# ── the classifier, pure ───────────────────────────────────────────────────

def test_resistance_that_holds_is_respected():
    t, h, lo, c = _bars([99, 100.02, 99.8, 99.6, 99.5], [98, 99, 99, 99, 99],
                        [98.5, 99.7, 99.5, 99.4, 99.2])
    assert B.classify(True, 100.0, 0.1, t, h, lo, c)["status"] == "respected"


def test_a_wick_through_and_a_close_back_is_a_sweep():
    t, h, lo, c = _bars([99, 100.6, 99.9, 99.7, 99.6], [98, 99, 99, 99, 99],
                        [98.5, 99.8, 99.6, 99.5, 99.3])
    out = B.classify(True, 100.0, 0.1, t, h, lo, c)
    assert out["status"] == "swept_reclaimed" and out["max_beyond_pct"] == pytest.approx(0.6)


def test_closing_beyond_and_staying_is_a_break():
    t, h, lo, c = _bars([99.9, 100.5, 101, 101.4], [99.5, 99.9, 100.3, 100.8],
                        [99.8, 100.4, 100.8, 101.2])
    assert B.classify(True, 100.0, 0.1, t, h, lo, c)["status"] == "broke"


def test_support_mirrors_and_undecided_waits():
    t, h, lo, c = _bars([101, 100.5, 100.2, 100.4, 100.6], [100.5, 99.98, 99.95, 100.1, 100.3],
                        [100.8, 100.3, 100.1, 100.3, 100.5])
    assert B.classify(False, 100.0, 0.1, t, h, lo, c)["status"] == "respected"
    t, h, lo, c = _bars([101, 100.5], [100.5, 99.9], [100.8, 100.3])
    assert B.classify(False, 100.0, 0.1, t, h, lo, c) is None, "needs bars after the touch"
    t, h, lo, c = _bars([102, 102], [101, 101], [101.5, 101.5])
    assert B.classify(False, 100.0, 0.1, t, h, lo, c) is None, "not yet touched"


# ── notes, reads and stamps through submit ──────────────────────────────────

def test_notes_are_stored_and_bad_ones_named_never_rejecting_the_plan(ledger):
    eng, ids = _setup_engine()
    plan = _plan(ids)
    plan["pair_notes"] = {"ethusdt": "  waiting for a 4h close back above the shelf  ",
                          "nope": "x", "SOLUSDT": ""}
    out = P.submit(plan, eng, now=NOW, admission=ADMIT)
    assert out["accepted"] and out["pair_notes_stored"] == ["ETHUSDT"]
    assert len(out["pair_notes_dropped"]) == 2
    con = sqlite3.connect(ledger.path)
    note, px = con.execute("SELECT note, price_at_note FROM pair_notes").fetchone()
    assert note == "waiting for a 4h close back above the shelf" and px > 0


def test_reads_and_profile_are_stamped_on_the_setup_at_submit(ledger):
    eng, ids = _setup_engine()
    B.note_read("ETHUSDT", "image", now=NOW - 60)
    B.note_read("ETHUSDT", "flow", now=NOW - 7200)      # too old to have informed it
    out = P.submit(_plan(ids), eng, now=NOW, admission=ADMIT)
    assert out["n_accepted"] == 1
    con = sqlite3.connect(ledger.path)
    reads, profile = con.execute("SELECT reads_json, profile_json FROM setups").fetchone()
    reads = json.loads(reads)
    assert reads["image"] is True and reads["flow"] is False and reads["book"] is False
    assert "readable" in json.loads(profile)


def test_a_catalog_read_is_what_marks_the_coin_as_read(ledger):
    eng, ids = _setup_engine()
    diag_catalog.run("read.analyst_book", eng, {"symbol": "ethusdt"})
    assert B.reads_for("ETHUSDT", __import__("time").time())["book"] is True
    bad = diag_catalog.run("read.analyst_book", eng, {"symbol": "eth"})
    assert bad["result"]["reason"] == "symbol must look like XXXUSDT"


# ── marks: synced from setups, classified by the walk, read back ────────────

def test_marks_are_created_once_per_level_and_read_back_in_the_book(ledger):
    eng, ids = _setup_engine()
    P.submit(_plan(ids), eng, now=NOW, admission=ADMIT)
    con = ledger._connect()
    with con:
        n1 = B.sync_marks(con)
        n2 = B.sync_marks(con)
    con.close()
    assert n1 == 4 and n2 == 0, "entry, stop, two targets; idempotent"
    book = diag_catalog.run("read.analyst_book", eng, {"symbol": "ETHUSDT"})["result"]
    assert book["readable"] and len(book["level_marks"]) == 4
    roles = {m["kind"]: m["role"] for m in book["level_marks"]}
    assert roles["stop"] == "support" and roles["target0"] == "resistance"
    assert all(m["status"] == "pending" for m in book["level_marks"])


def test_classify_marks_resolves_from_store_bars_and_refuses_a_dead_series(ledger):
    eng, ids = _setup_engine()
    P.submit(_plan(ids), eng, now=NOW, admission=ADMIT)
    con = ledger._connect()
    with con:
        B.sync_marks(con)
    target = con.execute("SELECT price FROM level_marks WHERE kind='target0'").fetchone()[0]
    t0 = (NOW // 300 + 1) * 300 * 1000
    t = np.arange(6, dtype=float) * 300_000 + t0
    highs = np.array([target - 5, target + 0.01, target - 1, target - 2, target - 3,
                      target - 3])
    buckets = {"ETHUSDT": {"5m": {"open_time": t, "high": highs, "low": highs - 4,
                                  "close": highs - 1}}}
    with con:
        out = B.classify_marks(con, buckets, NOW + 3600)
    status = con.execute("SELECT status FROM level_marks WHERE kind='target0'").fetchone()[0]
    assert status == "respected" and out["respected"] >= 1
    # No bars at all and past the horizon: insufficient, never "untested".
    with con:
        B.classify_marks(con, {}, NOW + B.MARK_HORIZON_S + 10)
    left = {r[0] for r in con.execute("SELECT status FROM level_marks")}
    con.close()
    assert "untested" not in left and "insufficient" in left


def test_the_walk_step_is_what_creates_the_marks(ledger):
    """Pin the call site: a classifier nothing calls is a scaffold."""
    from src import analyst_walk as W

    eng, ids = _setup_engine()
    P.submit(_plan(ids), eng, now=NOW, admission=ADMIT)
    counts = W.step(eng, now=NOW + 60)
    assert counts.get("marks_created") == 4, counts
    con = sqlite3.connect(ledger.path)
    assert con.execute("SELECT COUNT(*) FROM level_marks").fetchone()[0] == 4
