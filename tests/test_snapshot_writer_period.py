"""The snapshot writer's period, and why an empty app feed traced back to it.

2026-08-18. The owner's Lumin app showed **"No signals yet"** and **"No market
alerts yet"** while ops paged ``snapshot_key_missing``; the rows came back the
moment the keys did. In isolated mode the api container serves from
``snapshot:*`` and nothing else, so an expired key is not a dashboard problem —
it is a paying subscriber opening the product and finding it empty.

The cause is one line. The loop was::

    while True:
        await asyncio.sleep(_CYCLE_INTERVAL_S)
        await self._write_cycle()

so the real period is ``15s + however long the write took``, while every key it
writes carries a TTL of **twice the interval** on the contract stated in
``snapshot_store``: *"Writer interval -> TTL is 2x that interval so one missed
write never evicts a warm cache."* That contract silently assumed the write is
free. One cycle serialises eight payloads — the first being 500 signals —
through a single-thread executor, on a box measured at 124-208% of a 2.5-core
cap. At ~45s of work the period reaches 60s and the keys evict themselves.
"""
from __future__ import annotations

import asyncio
import time

import pytest

from src.api import snapshot_store as store
from src.api.snapshot_writer import _CYCLE_INTERVAL_S, SnapshotWriter


class _Redis:
    available = True

    async def set(self, *a, **k):
        return True


def _writer(work_sec: float) -> SnapshotWriter:
    w = SnapshotWriter(engine=object(), redis_client=_Redis())

    async def _cycle():
        await asyncio.sleep(work_sec)

    w._write_cycle = _cycle          # type: ignore[method-assign]
    return w


async def _run_cycles(writer: SnapshotWriter, n: int) -> float:
    """Drive `start()` for *n* cycles and return the wall time it took."""
    task = asyncio.create_task(writer.start())
    started = time.monotonic()
    while writer.cycle_count < n:
        await asyncio.sleep(0.005)
        if time.monotonic() - started > 10:
            pytest.fail("writer did not complete its cycles")
    elapsed = time.monotonic() - started
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    return elapsed


class TestTheContractWithTheTTL:
    def test_every_feed_critical_key_keeps_at_least_two_cycles_of_slack(self):
        """The store's docstring says "TTL is 2x that interval". It is not —
        the constants are 60s against a 15s interval, i.e. **4x**, and this
        test asserting the docstring is what caught that.

        Pinned as the stated *minimum* rather than the observed multiple: more
        margin than advertised is the safe direction, and a test demanding
        exactly 4x would fail the day somebody correctly widens one. What must
        never happen is the slack falling to one cycle, where a single slow
        write empties the app.
        """
        for name, ttl in (("signals", store.TTL_SIGNALS),
                          ("tickers", store.TTL_TICKERS),
                          ("engine_state", store.TTL_ENGINE_STATE),
                          ("positions_diag", store.TTL_POSITIONS_DIAG),
                          ("data_intake", store.TTL_DATA_INTAKE)):
            assert ttl >= 2 * _CYCLE_INTERVAL_S, name

    def test_the_writer_reports_the_stores_real_ttl_not_a_derived_one(self):
        """The first cut computed `2 * _CYCLE_INTERVAL_S` from the docstring and
        reported 30s for a key that lives 60s."""
        assert _writer(0).health()["ttl_sec"] == store.TTL_SIGNALS


class TestFixedPeriod:
    async def test_work_does_not_add_itself_to_the_period(self, monkeypatch):
        """The defect, asserted directly.

        With the old ``sleep(I); work()`` loop, three cycles of 40ms work on a
        50ms interval take 3*(50+40)=270ms. Sleeping the remainder makes it
        3*50=150ms — the work is absorbed, not added.
        """
        monkeypatch.setattr("src.api.snapshot_writer._CYCLE_INTERVAL_S", 0.05)
        monkeypatch.setattr("src.api.snapshot_writer._OVERRUN_BUDGET_S", 0.05)
        elapsed = await _run_cycles(_writer(work_sec=0.04), 3)
        assert elapsed < 3 * (0.05 + 0.04) * 0.85, (
            f"period still includes the work: {elapsed:.3f}s"
        )

    async def test_an_overrunning_cycle_re_enters_immediately(self, monkeypatch):
        """Never a negative sleep, and never an idle gap on top of an overrun —
        the writer is already behind, so it starts the next cycle at once."""
        monkeypatch.setattr("src.api.snapshot_writer._CYCLE_INTERVAL_S", 0.02)
        monkeypatch.setattr("src.api.snapshot_writer._OVERRUN_BUDGET_S", 0.02)
        writer = _writer(work_sec=0.05)
        elapsed = await _run_cycles(writer, 3)
        assert elapsed < 3 * 0.05 * 1.6
        assert writer.overrun_count == 3


class TestHealthCounters:
    async def test_a_healthy_cycle_records_no_overrun(self, monkeypatch):
        monkeypatch.setattr("src.api.snapshot_writer._CYCLE_INTERVAL_S", 0.05)
        monkeypatch.setattr("src.api.snapshot_writer._OVERRUN_BUDGET_S", 0.05)
        writer = _writer(work_sec=0.001)
        await _run_cycles(writer, 2)
        health = writer.health()
        assert health["overruns"] == 0
        assert health["cycles"] >= 2
        assert health["last_completed_at"] > 0

    async def test_an_overrun_is_counted_so_pressure_is_visible_before_an_outage(
        self, monkeypatch
    ):
        """The leading indicator. The lagging one is the keys vanishing, and by
        then a subscriber has already seen an empty feed."""
        monkeypatch.setattr("src.api.snapshot_writer._CYCLE_INTERVAL_S", 0.02)
        monkeypatch.setattr("src.api.snapshot_writer._OVERRUN_BUDGET_S", 0.02)
        writer = _writer(work_sec=0.05)
        await _run_cycles(writer, 2)
        health = writer.health()
        assert health["overruns"] >= 2
        assert health["worst_cycle_sec"] >= 0.05
        assert health["ttl_sec"] == store.TTL_SIGNALS

    def test_health_is_readable_before_a_single_cycle_runs(self):
        """The probe reads this at boot; it must not raise or lie."""
        health = _writer(work_sec=0).health()
        assert health["last_completed_at"] == 0
        assert health["cycles"] == 0
