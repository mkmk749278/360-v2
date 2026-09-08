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


def test_a_raising_retirement_lookup_does_not_take_the_READ_down(monkeypatch):
    """This module is a reader and must not be the reason a diagnostic fails."""
    from src import path_retirement

    def _boom():
        raise RuntimeError("tunables unreachable")

    monkeypatch.setattr(path_retirement, "snapshot", _boom)
    now = time.time()
    out = ps.summarise(_rows("A", "LONG", ["XUSDT"], 1.0, now=now), now=now)
    assert out["cells"][0]["n"] == 1, "the grading still ran"
    assert "RuntimeError" in (out["retirement_error"] or "")
    assert out["already_retired"] == []


def test_path_retirement_is_imported_in_exactly_ONE_place():
    """And that place is the guarded lookup.

    Found by running the ops contract test in an environment without the
    engine's own dependencies: the lookup was wrapped in a try and
    `_is_retired` imported the same module again, unguarded, so an import
    failure raised straight out of `summarise`. The wildcard token is expanded
    inside the guarded lookup now and nothing downstream needs to know it
    exists.

    Pinned on the TREE rather than by count of a string, because the next
    unguarded import will be written by somebody who has not read this file.
    """
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(ps))
    sites = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        names = [a.name for a in node.names]
        module = getattr(node, "module", "") or ""
        if "path_retirement" not in module and "path_retirement" not in names:
            continue
        # Which function encloses it?
        for fn in ast.walk(tree):
            if isinstance(fn, ast.FunctionDef) and node in ast.walk(fn):
                sites.append(fn.name)
                break
    assert sites == ["_retired_lookup"], (
        f"path_retirement is imported from {sites}; every one of those is a "
        "path on which a reader can take down the read it reports on"
    )


# ── It runs on the ENGINE'S event loop ──────────────────────────────────────

def test_resampling_sums_and_counts_is_identical_to_concatenating():
    """The load-bearing arithmetic behind the vectorised bootstrap.

    The mean of a cluster resample is the total of the picked symbols' sums
    over the total of their counts. If that identity is ever broken the
    interval silently becomes an unweighted mean of per-symbol means — a
    different estimator, still plausible-looking, and it would quietly
    under-weight the symbols carrying most of the evidence.

    Reference built here with the same draws, by concatenating.
    """
    import numpy as np

    by_symbol = {"A": [1.0, 3.0, 5.0], "B": [-2.0], "C": [0.5, 0.5]}
    symbols = sorted(by_symbol)
    size = len(symbols)
    iters = 500
    picks = np.random.default_rng(99).integers(0, size, size=(iters, size))

    reference = []
    for row in picks:
        pool = [v for i in row for v in by_symbol[symbols[i]]]
        reference.append(sum(pool) / len(pool))
    reference.sort()

    sums = np.array([sum(by_symbol[s]) for s in symbols], dtype=np.float64)
    counts = np.array([len(by_symbol[s]) for s in symbols], dtype=np.float64)
    vectorised = np.sort(sums[picks].sum(axis=1) / counts[picks].sum(axis=1))

    assert np.allclose(vectorised, reference)


def test_the_whole_read_stays_far_inside_one_monitor_tick():
    """`diag_catalog.run` executes synchronously on the snapshot writer's event
    loop — the engine's own — whose achieved period sets the governor's
    staleness floor and whose snapshot keys carry a 60s TTL.

    The first cut rebuilt the pooled list once per resample and measured
    0.475s at 2,000 in-window rows, growing with the book. This bound is
    ~50x what the vectorised version takes and ~5x under what the loop
    version would take at this size, so it is a regression guard rather than a
    stopwatch: it catches somebody reintroducing the per-resample loop, and it
    does not fail because CI was busy.
    """
    now = time.time()
    rows = []
    for i in range(20_000):
        rows.append({
            "setup_class": f"PATH_{i % 12}", "direction": "LONG" if i % 2 else "SHORT",
            "symbol": f"S{i % 140}USDT", "pnl_pct": (i % 9) - 4.0,
            "terminal_outcome_timestamp": now - 3600,
        })
    started = time.perf_counter()
    out = ps.summarise(rows, now=now)
    elapsed = time.perf_counter() - started
    assert out["coverage"]["in_window"] == 20_000
    assert elapsed < 1.0, f"summarise took {elapsed:.2f}s on the engine's loop"
