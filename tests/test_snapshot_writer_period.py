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


class _RedisClient:
    """Minimal stand-in for the command-consumer path.

    ``_write_cycle`` ends by draining three command keys off
    ``self._redis.client``; a fake without it makes the timing tests fail on a
    collaborator they are not testing.
    """

    async def get(self, *a, **k):
        return None

    async def delete(self, *a, **k):
        return 0


class _Redis:
    available = True
    client = _RedisClient()

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


class TestTheTTLCoversTheMeasuredPeriod:
    """Sized against what the writer actually costs, not what it intends to.

    Measured on the box 2026-08-18, minutes after the period fix shipped:
    **75.17s per cycle, 188.37s worst, 5 of 7 cycles over budget** — against a
    60s TTL. Seven of eleven keys were absent at that moment, including
    ``snapshot:signals_all``, so the Lumin app was showing a paying subscriber
    "No signals yet" while this was being read.

    Removing the drift was necessary and nowhere near sufficient: the work
    alone is 5-12x the interval, so no scheduling change can keep a 60s key
    alive. Raising the TTL does not make the writer fast — it stops a slow
    writer being a user-visible outage while the cost is measured and cut.
    """

    #: The worst cycle observed in production on the day this was written. The
    #: bound has to clear it, or the keys expire on an ordinary bad cycle.
    WORST_OBSERVED_CYCLE_SEC = 188.37

    #: How long the `snapshot_writer` liveness probe takes to report a stall:
    #: min_streak=2 against the 5-minute audit loop.
    PROBE_DETECTION_SEC = 10 * 60

    def test_the_ttl_outlives_the_probes_detection_time(self):
        """The ordering that matters, and it was backwards.

        At 60s the keys expired *nine minutes before* anything said so — the
        app went blank first and the page said second. The TTL is the LAST line
        of defence, not the first.
        """
        for name, ttl in (("signals", store.TTL_SIGNALS),
                          ("tickers", store.TTL_TICKERS),
                          ("engine_state", store.TTL_ENGINE_STATE),
                          ("positions_diag", store.TTL_POSITIONS_DIAG)):
            assert ttl > self.PROBE_DETECTION_SEC, name

    def test_the_ttl_clears_the_worst_observed_cycle(self):
        assert store.TTL_SIGNALS > self.WORST_OBSERVED_CYCLE_SEC * 2


class TestPerPayloadTiming:
    async def test_every_payload_reports_its_own_cost(self, monkeypatch):
        """"The 500-signal serialisation is obviously the expensive one" is a
        hypothesis about behaviour, not a measurement of it. The cycle total
        said 75s and could not say where.

        Drives ``_write_cycle`` directly rather than the loop. The first cut
        drove ``start()`` and read the counters after cancelling it — which
        cancels mid-cycle, so ``_timed``'s ``finally`` recorded a *partial*
        elapsed for whichever payload was in flight and the assertion compared
        two zeroes. The property under test is per-payload attribution, not the
        loop; testing it through the loop tested the cancellation instead.
        """
        writer = SnapshotWriter(engine=object(), redis_client=_Redis())

        async def _fast():
            await asyncio.sleep(0.001)

        async def _slow():
            await asyncio.sleep(0.03)

        for name in ("_write_tickers", "_write_engine_state", "_write_positions_diag",
                     "_write_data_intake", "_write_trail_governor",
                     "_write_router_delivery", "_write_dark_promotion",
                     "_write_activity", "_write_alerts", "_write_agents"):
            monkeypatch.setattr(writer, name, _fast)
        monkeypatch.setattr(writer, "_write_signals", _slow)

        await writer._write_cycle()
        times = writer.health()["write_times"]
        assert times["signals"] >= 0.03
        assert times["signals"] > times["tickers"]
        # Slowest first: the reader's next question is always "slow where".
        assert next(iter(times)) == "signals"

    async def test_a_failing_payload_still_records_its_cost(self):
        """Timed in a `finally`: the write that BLEW UP is exactly the one whose
        cost you want, and a raise must not take the measurement with it."""
        writer = SnapshotWriter(engine=object(), redis_client=_Redis())
        with pytest.raises(RuntimeError):
            with writer._timing("signals"):
                raise RuntimeError("nope")
        assert "signals" in writer.write_times

    def test_the_timing_wrapper_keeps_every_write_a_DIRECT_CALL(self):
        """The shape two other test files pin, and the reason `_timing` is a
        context manager rather than a wrapper.

        The first cut was `await self._timed("signals", self._write_signals)`,
        which turns each dispatch from a call into an argument — and
        `test_dark_promotion` / `test_signal_router` parse this function's AST
        asserting each payload writer appears as a *call*, because "defining a
        writer is not calling it" is a seam this repo has paid for under
        several names. CI caught it within minutes.

        Keeping the call shape means those guards go on protecting every
        payload added later, with nobody remembering to update them.
        """
        import ast
        import inspect
        import textwrap

        src = textwrap.dedent(inspect.getsource(SnapshotWriter._write_cycle))
        called = {
            n.func.attr for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        }
        for payload in ("_write_signals", "_write_tickers", "_write_engine_state",
                        "_write_positions_diag", "_write_data_intake",
                        "_write_trail_governor", "_write_router_delivery",
                        "_write_dark_promotion", "_write_activity",
                        "_write_alerts", "_write_agents"):
            assert payload in called, payload
