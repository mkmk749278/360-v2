"""The per-path verdict, and the ordering that keeps it honest.

The caps came off on 2026-08-30 so every path could reach the feed rather
than `MOVER_TREND_PULLBACK` holding the slots by arithmetic. It worked —
MVRTP's share fell 76% to 59% and every other path is running 3-7x its old
delivery rate — and over the ten days that followed the delivered book went
from +0.506%/trade to -0.113%/trade.

The owner's question is *"we need to produce good signals from every path"*,
and the answer this module has to be able to give is **"not yet decidable"**
without that reading like a failure. Eighteen cells over those ten days, and
the only interval excluding zero belongs to a cell with **three trades**.

That cell is why the sample floor is applied BEFORE the interval, and it is
what most of this file pins.
"""
from __future__ import annotations

import subprocess
import sys
import textwrap
import time

import pytest

from src import path_scorecard as ps


def _rows(setup, side, symbols, pnl, *, now, n_per_symbol=1, age_sec=3600.0):
    out = []
    for sym in symbols:
        for i in range(n_per_symbol):
            out.append({
                "setup_class": setup, "direction": side, "symbol": sym,
                "pnl_pct": pnl,
                "terminal_outcome_timestamp": now - age_sec,
            })
    return out


# ── The ordering IS the guard ───────────────────────────────────────────────

def test_a_thin_cell_with_a_zero_excluding_interval_is_still_INSUFFICIENT():
    """The live case, verbatim.

    `MA_CROSS_TREND_SHIFT:LONG` — three trades, three symbols, -3.830%,
    symbol-clustered interval [-5.567, -2.873]. It excludes zero and it looks
    decisive, and it is `FAILED_AUCTION_RECLAIM`'s +0.846R on three rows with
    the sign flipped: drawn from eighteen cells, it says nothing about the
    path and everything about three bad days.

    Interval-first ordering returns LOSES here and puts a path one click from
    retirement. Floor-first returns INSUFFICIENT and names which bound failed.
    """
    now = time.time()
    rows = _rows("MA_CROSS_TREND_SHIFT", "LONG", ["AUSDT", "BUSDT", "CUSDT"],
                 -3.83, now=now)
    out = ps.summarise(rows, now=now)
    cell = out["cells"][0]
    assert cell["ci_high"] is not None and cell["ci_high"] < 0, (
        "the interval really does exclude zero — this test is about the "
        "ORDERING, not about the arithmetic being different"
    )
    assert cell["verdict"] == ps.VERDICT_INSUFFICIENT
    assert "3/25 trades" in cell["verdict_why"]
    assert "3/12 symbols" in cell["verdict_why"]
    assert out["retirement_candidates"] == []


def test_a_cell_that_clears_the_floor_can_be_decided():
    """Not a floor nothing can ever clear: with enough evidence it answers."""
    now = time.time()
    rows = _rows("SOME_PATH", "LONG", [f"S{i}USDT" for i in range(15)], -2.0,
                 now=now, n_per_symbol=2)
    out = ps.summarise(rows, now=now)
    cell = out["cells"][0]
    assert cell["n"] == 30 and cell["symbols"] == 15
    assert cell["verdict"] == ps.VERDICT_LOSES
    assert out["retirement_candidates"][0]["setup_class"] == "SOME_PATH"


def test_one_instrument_cannot_convict_a_path_however_many_trades():
    """`MIN_SYMBOLS` and `MIN_TRADES` answer different failures. Thirty trades
    on one symbol is one instrument's week wearing a path's name — and the
    symbol-clustered interval cannot even be computed from a single cluster."""
    now = time.time()
    rows = _rows("SOME_PATH", "LONG", ["ONLYUSDT"], -2.0, now=now, n_per_symbol=30)
    out = ps.summarise(rows, now=now)
    cell = out["cells"][0]
    assert cell["n"] == 30
    assert cell["verdict"] == ps.VERDICT_INSUFFICIENT
    assert "1/12 symbols" in cell["verdict_why"]


def test_the_number_of_cells_drawn_rides_on_the_payload():
    """"Best of N" is not a fact about the winner until N is on screen, and
    here the winner is a path somebody might retire."""
    now = time.time()
    rows = (_rows("A", "LONG", ["XUSDT"], 1.0, now=now)
            + _rows("B", "SHORT", ["YUSDT"], -1.0, now=now))
    out = ps.summarise(rows, now=now)
    assert out["cells_drawn"] == 2
    assert out["cells_decidable"] == 0


# ── The window is bounded by AGE ────────────────────────────────────────────

def test_the_window_is_bounded_by_age_never_by_count():
    """A count-bounded ring on a low-volume path holds evidence from whenever
    that path last emitted — the `cohort_edge` absorbing state arriving
    through the denominator instead of through the gate."""
    now = time.time()
    fresh = _rows("A", "LONG", ["XUSDT"], 1.0, now=now, age_sec=3600.0)
    stale = _rows("A", "LONG", ["XUSDT"], -9.0, now=now, age_sec=60 * 86400.0)
    out = ps.summarise(fresh + stale, now=now, window_days=30.0)
    assert out["cells"][0]["n"] == 1
    assert out["cells"][0]["net_avg_pct"] == pytest.approx(1.0 - ps.DEFAULT_FEE_PCT)


def test_an_undated_row_is_counted_apart_not_dropped_silently():
    """A row with no terminal stamp cannot be placed in or out of the window.
    Dropping it silently shrinks the denominator by an unknown amount."""
    now = time.time()
    rows = _rows("A", "LONG", ["XUSDT"], 1.0, now=now)
    rows.append({"setup_class": "A", "direction": "LONG", "symbol": "XUSDT",
                 "pnl_pct": 1.0, "terminal_outcome_timestamp": None})
    out = ps.summarise(rows, now=now)
    assert out["coverage"]["undated"] == 1
    assert out["coverage"]["in_window"] == 1


# ── Money, and both halves of it ────────────────────────────────────────────

def test_the_fee_is_charged_and_the_gross_stays_beside_it():
    """A net figure whose fee nobody can see is a gross figure with a caption."""
    now = time.time()
    out = ps.summarise(_rows("A", "LONG", ["XUSDT"], 1.0, now=now),
                       now=now, fee_pct=0.07)
    cell = out["cells"][0]
    assert cell["net_avg_pct"] == pytest.approx(0.93)
    assert cell["gross_avg_pct"] == pytest.approx(1.0)
    assert out["fee_pct"] == pytest.approx(0.07)


# ── A retired cell's evidence is FROZEN, not zero ───────────────────────────

def test_a_retired_cell_is_stamped_frozen_and_never_a_candidate(monkeypatch):
    """Retirement diverts to the dark lane, so a retired path stops producing
    delivered rows the moment it is armed. Its n stops growing and its verdict
    stops being a reading about today — and a frozen verdict and a fresh one
    look identical in a table unless one of them says so."""
    from src import path_retirement

    monkeypatch.setattr(path_retirement, "snapshot", lambda: {
        "enabled": True,
        "retired": [{"setup_class": "SOME_PATH", "side": "LONG"}],
    })
    now = time.time()
    rows = _rows("SOME_PATH", "LONG", [f"S{i}USDT" for i in range(15)], -2.0,
                 now=now, n_per_symbol=2)
    out = ps.summarise(rows, now=now)
    cell = out["cells"][0]
    assert cell["verdict"] == ps.VERDICT_LOSES
    assert cell["delivered_evidence_frozen"] is True
    assert out["retirement_candidates"] == [], "already retired — not a candidate"


def test_a_wildcard_retirement_covers_both_sides(monkeypatch):
    from src import path_retirement

    monkeypatch.setattr(path_retirement, "snapshot", lambda: {
        "enabled": True,
        "retired": [{"setup_class": "SOME_PATH", "side": path_retirement.ANY_SIDE}],
    })
    now = time.time()
    out = ps.summarise(_rows("SOME_PATH", "SHORT", ["XUSDT"], -2.0, now=now), now=now)
    assert out["cells"][0]["delivered_evidence_frozen"] is True


def test_an_unreadable_retirement_list_is_an_ERROR_not_an_empty_one(monkeypatch):
    """The flattering direction of this failure is the dangerous one: an empty
    list renders every frozen cell as a live one, i.e. a stale verdict shown
    as a current reading about a path somebody may act on."""
    from src import path_retirement

    monkeypatch.setattr(path_retirement, "snapshot",
                        lambda: {"error": "RuntimeError: no tunables"})
    now = time.time()
    out = ps.summarise(_rows("A", "LONG", ["XUSDT"], 1.0, now=now), now=now)
    assert out["retirement_error"] == "RuntimeError: no tunables"
    assert out["retirement_acting"] is False


# ── The interval must not move between reads ────────────────────────────────

def test_the_interval_is_stable_across_PROCESSES():
    """`hash()` on a str is salted per interpreter unless PYTHONHASHSEED is
    pinned, so seeding a bootstrap from it moves every published interval on
    each restart — noise a reader cannot tell from the book changing, in the
    one column a retirement decision is read from.

    Two subprocesses with different hash seeds, same rows, same interval.
    Fails against a `hash()`-seeded implementation and cannot be made to pass
    by running it twice in one process.
    """
    prog = textwrap.dedent(
        """
        import json, sys
        sys.path.insert(0, ".")
        from src import path_scorecard as ps

        now = 1_700_000_000.0
        rows = [
            {
                "setup_class": "A",
                "direction": "LONG",
                "symbol": "S%d" % (i % 14),
                "pnl_pct": (i % 7) - 3.0,
                "terminal_outcome_timestamp": now - 3600,
            }
            for i in range(40)
        ]
        out = ps.summarise(rows, now=now)
        print(json.dumps([[c["ci_low"], c["ci_high"]] for c in out["cells"]]))
        """
    )
    runs = []
    for seed in ("0", "12345"):
        proc = subprocess.run(
            [sys.executable, "-c", prog],
            capture_output=True, text=True, timeout=120,
            env={"PYTHONHASHSEED": seed, "PATH": "/usr/bin:/bin"},
        )
        assert proc.returncode == 0, proc.stderr
        runs.append(proc.stdout.strip())
    assert runs[0] == runs[1], (
        "the published interval moved between two processes that saw the same "
        "rows — a reader comparing this panel against the one he opened an "
        "hour ago cannot tell resampling noise from the book moving"
    )
