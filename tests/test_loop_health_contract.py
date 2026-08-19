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
import time as _time

import pytest


from src.api import snapshot_writer as sw
from src.scanner import Scanner


class _Scanner:
    """The REAL readers over the REAL declarations, driven by real cycles.

    The first cut of this stub returned a hand-written dict for both health
    calls — a mock asserting my own assumption back at me, one hop short of the
    reader, which is precisely how `zone_distance_atr` shipped uncomputable for
    its whole life on two tests that passed. A stub that hand-writes its
    collaborator's return shape cannot notice a field the collaborator gained,
    so the contract it claims to pin quietly stops covering the newest half of
    the payload — which is always the half nobody has read yet.

    Borrowing the declarations (`_init_*`) as well as the readers means a
    counter added to the scanner tomorrow travels through this contract without
    anyone editing this file.
    """

    _init_cycle_timing = Scanner._init_cycle_timing
    _init_indicator_cache_counters = Scanner._init_indicator_cache_counters
    _record_cycle_time = Scanner._record_cycle_time
    _uptime_sec = Scanner._uptime_sec
    cycle_health = Scanner.cycle_health
    indicator_cache_health = Scanner.indicator_cache_health
    # `cycle_health` stats the heartbeat file, so its reader is borrowed too.
    # This stub caught the omission on the day the progress beat shipped, which
    # is the whole point of it borrowing rather than hand-writing the payload.
    _heartbeat_file_age_sec = Scanner._heartbeat_file_age_sec

    def __init__(self):
        self._init_cycle_timing()
        self._init_indicator_cache_counters()
        # Not the repo's data/ path: a contract test that passed or failed on
        # whether someone had run the engine locally is not a contract test.
        self._HEARTBEAT_PATH = "/nonexistent/scanner_heartbeat"
        # Steady state, so the cycles below land in the graded buckets rather
        # than in the boot-warm-up ones that are deliberately kept out of them.
        self._scanner_started_at = _time.monotonic() - 10_000.0
        self.indicator_cache_capped_hits = 3
        self.indicator_cache_stale_avoided = 1
        # A real slow cycle with a real breakdown, recorded through the real
        # recorder — the stage split has to survive the whole chain, and it is
        # the one thing on the page that says WHERE a 402s cycle went.
        self._record_cycle_time(41.0, {"smc_detect": 20.0})
        self._record_cycle_time(402.5, {"smc_detect": 380.1, "indicators": 91.4})


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
    # Assert against what the REAL scanner computed, never against a literal.
    # The first cut of this file hand-wrote `over_kill: 2` in a stub and then
    # asserted the 2 back — a number no scanner had ever produced, pinning the
    # author's arithmetic instead of the transport.
    expected = _Engine._scanner.cycle_health()
    # Two keys are AGES and advance between the two calls, so they are compared
    # by presence and approximately rather than exactly — pinning a clock to the
    # millisecond is a flaky test, not a contract. Every other key is compared
    # by value, and the KEY SETS are compared exactly, which is what "nothing
    # may be dropped in transit" actually means.
    _ages = {"heartbeat_age_sec", "cycle_completed_age_sec", "in_flight_sec"}
    got = state["loop_health"]["scan_cycle"]
    assert set(got) == set(expected), "nothing may be dropped in transit"
    assert {k: v for k, v in got.items() if k not in _ages} == {
        k: v for k, v in expected.items() if k not in _ages
    }, "nothing may be altered in transit"
    for k in _ages & set(expected):
        if expected[k] is None:
            assert got[k] is None, f"{k}: absent must not become a number in transit"
        else:
            assert got[k] == pytest.approx(expected[k], abs=5.0)
    assert expected["over_kill"] == 1, "one cycle past the deadline was recorded"

    # The stage breakdown specifically: it is the only thing on the page that
    # answers WHERE a 402s cycle went, and until 2026-08-19 it went to a log
    # line and nowhere else. On the owner's VPS that grep returned nothing at
    # all while the deadline warnings beside it came through.
    stages = state["loop_health"]["scan_cycle"]["worst_stages"]
    assert stages == {"smc_detect": 380.1, "indicators": 91.4}
    assert list(stages) == ["smc_detect", "indicators"], "worst stage leads"

    # Round-trips through the same encoder the writer uses for Redis — a dict
    # of floats keyed by str survives it, and asserting so is cheap: `open_time`
    # was added to the candle store and dropped by its serializer for weeks.
    round_tripped = json.loads(json.dumps(state["loop_health"]))
    assert round_tripped["snapshot_writer"]["cycles"] == 113
    assert round_tripped["scan_cycle"]["worst_stages"] == stages


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


# ---------------------------------------------------------------------------
# Host resources — the same chain, and the same trap one container over.
# ---------------------------------------------------------------------------

def test_host_resources_ride_the_same_published_block():
    """Measured in the ENGINE container, or it measures the wrong container.

    In isolated mode the API process serves `/internal/diag/host-resources`.
    If that handler sampled its own cgroup it would report a near-idle HTTP
    server as the engine's CPU load — a full-looking answer about the wrong
    process, which is the trail-governor INDEX COLD defect on the one number
    the owner asked about first.
    """
    writer = sw.SnapshotWriter(_Engine(), redis_client=None)
    state = writer._build_engine_state(["scanner", "trade_monitor"])
    assert "host_resources" in state, (
        "ops reads engine_state['host_resources']; moving it empties the page"
    )
    block = state["host_resources"]
    assert "cpu" in block and "effective_config" in block
    # Survives the encoder the writer uses for Redis.
    assert json.loads(json.dumps(block))["cpu"]["quota_cores"] is not None


def test_the_facade_never_samples_its_own_cgroup():
    """It returns what was published, and {} when nothing was."""
    from src.api.redis_engine import RedisEngineFacade

    facade = RedisEngineFacade.__new__(RedisEngineFacade)
    facade._state = {"host_resources": {"cpu": {"cores_used": 3.9}}}
    assert facade.get_host_resources()["cpu"]["cores_used"] == 3.9

    facade._state = {}
    assert facade.get_host_resources() == {}, "absent must be empty, never zeros"


def test_the_effective_config_is_the_running_module_not_a_literal():
    """A deploy that did not take must be distinguishable from a bad fix.

    These are read out of the module the scanner is using, so they move when
    the process's config moves. Asserting them against `config` rather than
    against numbers pins that they are not a second hand-typed copy.
    """
    import config

    cfg = sw._host_resources()["effective_config"]
    assert cfg["scan_executor_workers"] == config.SCAN_EXECUTOR_WORKERS
    assert cfg["scan_cycle_kill_sec"] == config.SCAN_CYCLE_KILL_SEC
    assert cfg["indicator_cache_content_key"] == bool(config.INDICATOR_CACHE_CONTENT_KEY)


def test_an_unreadable_cgroup_is_named_never_zeroed():
    """A 0.0% CPU reading over a pinned engine is worse than a blank."""
    import src.host_resources as hr

    hr._last_cpu = None
    original = hr._cpu_seconds_used
    try:
        hr._cpu_seconds_used = lambda: (None, "no_cgroup_cpu_accounting")
        cpu = hr.sample()["cpu"]
        assert cpu["cores_used"] is None, "unknown must not render as idle"
        assert cpu["pct_of_quota"] is None
        assert cpu["reason"], "and it must say why"
    finally:
        hr._cpu_seconds_used = original
        hr._last_cpu = None


def test_the_first_sample_refuses_a_rate_rather_than_inventing_one():
    """A rate needs two readings. The first one says so instead of printing 0."""
    import src.host_resources as hr

    hr._last_cpu = None
    first = hr.sample()["cpu"]
    if first["source"] == "no_cgroup_cpu_accounting":
        pytest.skip("no cgroup CPU accounting in this environment")
    assert first["cores_used"] is None
    assert "first sample" in first["reason"]
    second = hr.sample()["cpu"]
    assert second["cores_used"] is not None, "the second reading measures"
    hr._last_cpu = None


def test_a_counter_that_went_backwards_is_refused_not_published():
    """A replaced container resets the counter; a negative delta is not load."""
    import src.host_resources as hr

    hr._last_cpu = None
    original = hr._cpu_seconds_used
    try:
        hr._cpu_seconds_used = lambda: (500.0, "cgroup_v2")
        hr.sample()
        hr._cpu_seconds_used = lambda: (1.0, "cgroup_v2")   # container replaced
        cpu = hr.sample()["cpu"]
        assert cpu["cores_used"] is None
        assert "reset" in cpu["reason"]
    finally:
        hr._cpu_seconds_used = original
        hr._last_cpu = None
