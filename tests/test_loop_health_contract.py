"""Cross-process contract for the engine-loop health block.

The block travels engine container -> Redis -> API container -> ops, and every
hop in that chain has already broken this repo once:

* a field one repo writes and no repo reads (#817, and again with the
  price-action lane card),
* a diag assembled in the API container that could not see the engine's
  in-process state (the trail-governor INDEX COLD page),
* a fixture that chose a payload location and then agreed with the author
  about it.

So these tests drive the REAL assembler and the REAL facade rather than a
hand-written dict, and they assert *where* the block lands, not just that a
function returns something shaped like it.
"""
from __future__ import annotations

import json


from src.api import snapshot_writer as sw


class _Scanner:
    def cycle_health(self):
        return {
            "cycles": 12, "last_sec": 41.0, "worst_sec": 402.5,
            "over_warn": 7, "over_kill": 2, "warn_sec": 60.0,
            "kill_sec": 120.0, "last_cycle_at": 1.0, "executor_workers": 2,
        }

    def indicator_cache_health(self):
        return {"capped_hits": 3, "stale_avoided": 1, "undatable": 0,
                "undatable_at_cap": 0, "bucket_cap": 1000}


class _Writer:
    def health(self):
        return {"cycles": 113, "overruns": 63, "last_cycle_sec": 1.8,
                "worst_cycle_sec": 134.5, "last_completed_at": 2.0,
                "ttl_sec": 900, "write_times": {}}


class _Engine:
    _scanner = _Scanner()
    _snapshot_writer = _Writer()


def test_loop_health_carries_all_three_producers():
    block = sw._loop_health(_Engine())
    assert set(block) == {"scan_cycle", "indicator_cache", "snapshot_writer", "strategy_edge"}
    assert block["indicator_cache"]["stale_avoided"] == 1
    assert block["scan_cycle"]["worst_sec"] == 402.5
    assert block["snapshot_writer"]["overruns"] == 63
    assert isinstance(block["strategy_edge"], dict)


def test_a_missing_producer_reads_as_not_reported_never_as_zero():
    """`None` and `0` are different claims, and only one of them is true.

    A zero scan-cycle count reads as a healthy loop — the reassuring answer, on
    the surface built to stop exactly that.
    """
    class _Bare:
        pass

    block = sw._loop_health(_Bare())
    assert block["scan_cycle"] is None
    assert block["snapshot_writer"] is None


def test_a_raising_producer_does_not_take_the_snapshot_down():
    class _Angry:
        class _S:
            def cycle_health(self):
                raise RuntimeError("boom")
        _scanner = _S()

    block = sw._loop_health(_Angry())
    assert block["scan_cycle"] is None


def test_the_block_lands_under_loop_health_in_the_real_engine_state_payload():
    """Drive the real builder and assert the PATH, not just the shape.

    A fixture that puts the block where the reader expects it will agree with
    the reader and disagree with the engine — the failure that cost a session
    on `zone_distance_atr` and again on the price-action lane card.
    """
    writer = sw.SnapshotWriter(_Engine(), redis_client=None)
    state = writer._build_engine_state(["scanner", "trade_monitor"])
    assert "loop_health" in state, (
        "ops reads engine_state['loop_health']; moving it silently empties the page"
    )
    assert state["loop_health"]["scan_cycle"]["over_kill"] == 2
    # Round-trips through the same encoder the writer uses for Redis.
    assert json.loads(json.dumps(state["loop_health"]))["snapshot_writer"]["cycles"] == 113


def test_the_facade_reads_the_same_key_the_writer_wrote():
    """One writer, one reader — asserted across the process boundary.

    In isolated mode the API container serves /internal/diag/loop-health and
    cannot see the scanner, so it reads what the engine published. A key name
    that drifts here empties the page in production and nowhere else.
    """
    from src.api.redis_engine import RedisEngineFacade

    facade = RedisEngineFacade.__new__(RedisEngineFacade)
    written = sw._loop_health(_Engine())
    facade._state = {"loop_health": written}
    assert facade.get_loop_health() == written

    facade._state = {}
    assert facade.get_loop_health() == {}, "absent must be empty, never zeros"
