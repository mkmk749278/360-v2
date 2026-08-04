"""The edge matrix is a 50-outcome ring, and until now it never said so.

``StrategyEdgeStore`` keeps ``deque(maxlen=STRATEGY_EDGE_WINDOW)`` per
``(strategy, context_key)`` cell, default **50**.  On the 2026-08-04 export
**1,569 of 8,538 cells were pinned at that cap**, so ``n`` was ``min(seen, 50)``
and a cell reading ``n=50`` could stand for fifty outcomes or five thousand.
Nothing counted the difference and nothing published it — while Layer C's
per-context emission floor and Layer G's promotions route on these cells.

This is the Suppression Quality Audit's ring problem one subsystem over.
``CLAUDE.md``: *"when a bounded buffer feeds a statistic, persist the eviction
count with the data and put the denominator beside the verdict."*  That store
got the treatment at a window of 400; this one never did, at 50.

Four properties are pinned here:

1. **Evictions are counted**, and counted at the moment they happen — once a
   record leaves the ring nothing downstream can tell it existed.
2. **The count survives a restart.**  A counter that resets on deploy reports
   every cell as unsampled afterwards — the reassuring answer, on the schedule
   that makes it hardest to notice.
3. **The persisted file stays loadable by the previous build.**  The counts ride
   in a reserved key rather than an envelope, so a rollback loses the counts
   rather than the store (#842's blast-radius lesson).
4. **An unsaturated cell reads as unsampled**, so ``sampled`` means what it says
   and is not merely "we started counting".
"""
from __future__ import annotations

import json
import os

import pytest

from src.strategy_edge import (
    _EVICTED_KEY,
    SOURCE_SUPPRESSED,
    StrategyEdgeStore,
    StrategyOutcome,
)


def _outcome(i: int) -> StrategyOutcome:
    return StrategyOutcome(
        strategy="LIQUIDITY_SWEEP_REVERSAL",
        context_key="NY/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN",
        side="LONG",
        won=(i % 2 == 0),
        pnl_pct=1.0,
        r_multiple=0.5,
        mfe_pct=1.0,
        source=SOURCE_SUPPRESSED,
    )


@pytest.fixture()
def store(tmp_path):
    return StrategyEdgeStore(
        window=5, min_samples=2, persist_path=str(tmp_path / "edge.json")
    )


CELL = ("LIQUIDITY_SWEEP_REVERSAL", "NY/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN")


class TestEvictionsAreCounted:
    def test_an_unsaturated_cell_is_not_sampled(self, store):
        """``sampled`` must mean "this ring has dropped records", not "the
        counter exists" — otherwise every cell reads sampled from day one and
        the flag carries no information."""
        for i in range(3):
            store.record(_outcome(i), persist=False)
        assert store.sampling(*CELL) == {
            "held": 3, "evicted": 0, "seen": 3, "sampled": 0
        }

    def test_a_full_ring_counts_what_it_drops(self, store):
        for i in range(12):
            store.record(_outcome(i), persist=False)
        s = store.sampling(*CELL)
        assert s["held"] == 5, "the ring still holds only maxlen"
        assert s["evicted"] == 7, "and 7 outcomes were pushed out of it"
        assert s["seen"] == 12
        assert s["sampled"] == 1

    def test_the_boundary_append_is_not_counted_early(self, store):
        """Filling the ring exactly to maxlen evicts nothing.  Off by one here
        would report a sample where there is a population."""
        for i in range(5):
            store.record(_outcome(i), persist=False)
        assert store.sampling(*CELL)["evicted"] == 0
        store.record(_outcome(99), persist=False)
        assert store.sampling(*CELL)["evicted"] == 1


class TestTheDenominatorReachesTheMatrix:
    def test_the_cell_publishes_seen_beside_n(self, store):
        for i in range(12):
            store.record(_outcome(i), persist=False)
        cell = store.matrix()["LIQUIDITY_SWEEP_REVERSAL|NY/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN"]
        assert cell["n"] == 5
        assert cell["n_evicted"] == 7
        assert cell["n_seen"] == 12
        assert cell["sampled"] is True

    def test_an_unsaturated_cell_reports_n_seen_equal_to_n(self, store):
        store.record(_outcome(0), persist=False)
        cell = store.matrix()["LIQUIDITY_SWEEP_REVERSAL|NY/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN"]
        assert cell["n"] == cell["n_seen"] == 1
        assert cell["sampled"] is False


class TestTheCountSurvivesARestart:
    def test_evictions_persist_and_reload(self, tmp_path):
        path = str(tmp_path / "edge.json")
        s1 = StrategyEdgeStore(window=5, min_samples=2, persist_path=path)
        for i in range(12):
            s1.record(_outcome(i), persist=False)
        s1.save()

        s2 = StrategyEdgeStore(window=5, min_samples=2, persist_path=path)
        assert s2.sampling(*CELL)["evicted"] == 7, (
            "a count that resets on restart reports every cell as unsampled "
            "after each deploy"
        )
        assert s2.sampling(*CELL)["seen"] == 12

    def test_the_reserved_key_cannot_collide_with_a_cell(self, tmp_path):
        """Cell keys are ``STRATEGY|context`` and ``_key`` upper-cases the
        strategy, so a key with no ``|`` is unreachable as a real cell."""
        path = str(tmp_path / "edge.json")
        s = StrategyEdgeStore(window=5, min_samples=2, persist_path=path)
        for i in range(12):
            s.record(_outcome(i), persist=False)
        s.save()
        raw = json.load(open(path))
        assert _EVICTED_KEY in raw
        assert "|" not in _EVICTED_KEY
        assert all("|" in k for k in raw if k != _EVICTED_KEY)


class TestBackwardCompatibility:
    def test_a_pre_2026_08_04_flat_file_still_loads(self, tmp_path):
        """The old format is a bare ``{cell_key: [records]}`` map.  It must load
        with the records intact and simply no eviction knowledge."""
        path = str(tmp_path / "old.json")
        json.dump(
            {
                "FAILED_AUCTION_RECLAIM|ASIA/ACCUMULATION": [
                    {
                        "won": True, "pnl_pct": 1.0, "r": 0.5, "gr": 0.5,
                        "nr": 0.5, "mfe": 1.0,
                        "ts": "2026-08-04T00:00:00+00:00", "src": "suppressed",
                    }
                ]
            },
            open(path, "w"),
        )
        s = StrategyEdgeStore(window=5, min_samples=1, persist_path=path)
        assert s.sample_count("FAILED_AUCTION_RECLAIM", "ASIA/ACCUMULATION") == 1
        assert s.sampling("FAILED_AUCTION_RECLAIM", "ASIA/ACCUMULATION")["evicted"] == 0

    def test_a_new_file_is_still_readable_as_cells_by_old_code(self, tmp_path):
        """The rollback contract, asserted the way old code reads it: every key
        other than the reserved one splits into exactly two parts, so a build
        without this change skips the counts and keeps every cell.  An envelope
        (``{"schema":…, "cells":…}``) would have made all of them unreadable."""
        path = str(tmp_path / "edge.json")
        s = StrategyEdgeStore(window=5, min_samples=2, persist_path=path)
        for i in range(12):
            s.record(_outcome(i), persist=False)
        s.save()
        raw = json.load(open(path))
        recovered = {
            k: v for k, v in raw.items() if len(k.split("|", 1)) == 2
        }
        assert len(recovered) == 1
        assert all(isinstance(v, list) for v in recovered.values())


class TestNoDiskWriteWhenPersistenceIsDisabled:
    def test_empty_persist_path_never_touches_the_filesystem(self, tmp_path, monkeypatch):
        """``path=""`` means in-memory.  A ledger that wrote a ``.tmp`` under
        this hook cost two months of false ``fail_open`` records once already
        (CLAUDE.md) — pinned here because this change touches ``_save``."""
        monkeypatch.chdir(tmp_path)
        s = StrategyEdgeStore(window=5, min_samples=2, persist_path="")
        for i in range(12):
            s.record(_outcome(i), persist=True)
        s.save()
        assert os.listdir(tmp_path) == [], "in-memory store must not write to disk"
        assert s.sampling(*CELL)["evicted"] == 7, "…but must still count"
