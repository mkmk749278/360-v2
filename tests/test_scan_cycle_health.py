"""Guards for the 2026-08-19 engine-stability work.

Three separate defects, each with its own section:

1. The indicator/SMC cache key was the candle COUNT, which stops changing at
   the store's 1,000-bar bucket cap — so a full bucket's indicators froze while
   its bars kept arriving.
2. Scan-cycle wall-time was computed every cycle and read by nothing, while it
   is the exact quantity ``healthcheck.py`` kills the container on.
3. The Layer-C edge store persisted synchronously from the money path.

Every one of them was invisible to the suite before this file, which is the
point: none crashed and none left an empty screen.
"""
from __future__ import annotations

import asyncio as _asyncio
import os as _os
import time as _time

import healthcheck

import pytest

from src.historical_data import _MAX_CANDLES_PER_BUCKET
from src.scanner import _CANDLE_BUCKET_CAP, Scanner


# ---------------------------------------------------------------------------
# 1. The cache key
# ---------------------------------------------------------------------------

def _bucket(n: int, *, dated: bool = True, start: float = 0.0) -> dict:
    cd = {
        "open": [1.0] * n,
        "high": [1.0] * n,
        "low": [1.0] * n,
        "close": [1.0] * n,
        "volume": [1.0] * n,
    }
    if dated:
        cd["open_time"] = [start + i * 60_000.0 for i in range(n)]
    return cd


def test_bucket_cap_is_imported_not_retyped():
    """One writer for the cap, or the guard drifts from the thing it guards."""
    assert _CANDLE_BUCKET_CAP is _MAX_CANDLES_PER_BUCKET


def test_fingerprint_changes_when_a_bar_lands_on_a_full_bucket():
    """The defect, stated directly.

    A capped bucket that rolls a bar forward has the SAME length and different
    content. Under the old count-only key these two states were identical, so
    the cache hit forever and the indicators froze.
    """
    n = _CANDLE_BUCKET_CAP
    before = _bucket(n, start=0.0)
    after = _bucket(n, start=60_000.0)  # one bar rolled off the front
    assert len(before["close"]) == len(after["close"]) == n, "the cap must hold"
    assert Scanner._series_fingerprint(before) != Scanner._series_fingerprint(after)


def test_fingerprint_is_stable_when_nothing_changed():
    """A correct key must also not thrash — a permanent miss is its own cost."""
    cd = _bucket(500)
    assert Scanner._series_fingerprint(cd) == Scanner._series_fingerprint(cd)
    assert Scanner._series_fingerprint(cd) == Scanner._series_fingerprint(_bucket(500))


def test_fingerprint_tracks_growth_below_the_cap():
    assert Scanner._series_fingerprint(_bucket(100)) != Scanner._series_fingerprint(_bucket(101))


def test_undatable_below_the_cap_keeps_the_count_only_key():
    """Sound: the length still advances on every appended bar down here."""
    a = Scanner._series_fingerprint(_bucket(100, dated=False))
    b = Scanner._series_fingerprint(_bucket(100, dated=False))
    assert a == b
    assert a != Scanner._series_fingerprint(_bucket(101, dated=False))


def test_undatable_at_the_cap_forces_a_recompute():
    """The one case where neither "changed" nor "unchanged" is provable.

    It must never compare equal — that is the frozen-indicator bug — and the
    mechanism must not rely on NaN's self-inequality, which a later
    simplification to a shared constant would silently break.
    """
    n = _CANDLE_BUCKET_CAP
    a = Scanner._series_fingerprint(_bucket(n, dated=False))
    b = Scanner._series_fingerprint(_bucket(n, dated=False))
    assert a != b, "a capped undatable bucket must always miss the cache"
    marker = a[1]
    assert not isinstance(marker, float), (
        "the forced miss must be a deliberate sentinel, not NaN — a reader "
        "replacing NaN with a shared constant would reintroduce the freeze"
    )
    assert marker is not None, "None would compare equal and restore the bug"


def test_fingerprint_ignores_a_timestamp_array_of_the_wrong_length():
    """A misaligned open_time array cannot name the newest bar."""
    cd = _bucket(50)
    cd["open_time"] = cd["open_time"][:10]
    n, marker = Scanner._series_fingerprint(cd)
    assert n == 50
    assert marker is None  # below the cap → count-only, not a guess


def test_fingerprint_ignores_a_nan_newest_timestamp():
    cd = _bucket(50)
    cd["open_time"][-1] = float("nan")
    assert Scanner._series_fingerprint(cd)[1] is None


def test_fingerprint_of_an_empty_bucket():
    assert Scanner._series_fingerprint({}) == (0, None)


# ---------------------------------------------------------------------------
# 2. Scan-cycle timing
# ---------------------------------------------------------------------------

class _CycleRecorder:
    """The timing half of Scanner, exercised without booting the engine.

    Borrows the REAL methods rather than reimplementing them — a
    reimplementation would assert my own arithmetic back at me and go green
    over whatever the scanner actually does.
    """

    _init_cycle_timing = Scanner._init_cycle_timing
    _record_cycle_time = Scanner._record_cycle_time
    _uptime_sec = Scanner._uptime_sec
    cycle_health = Scanner.cycle_health
    _touch_heartbeat = Scanner._touch_heartbeat
    _touch_heartbeat_progress = Scanner._touch_heartbeat_progress
    _heartbeat_file_age_sec = Scanner._heartbeat_file_age_sec

    def __init__(self) -> None:
        # Borrow the DECLARATION too, not only the readers. Typing the counter
        # set out here is a hand-kept second list, and it fell behind the real
        # one twice — once on the boot-grace split, once on the stage
        # breakdown — each time as an AttributeError inside a borrowed method
        # rather than as a statement about what changed.
        self._init_cycle_timing()
        # The scanner's live per-stage accumulator. Borrowed as a plain
        # dict because `cycle_health` only ever reads it.
        self._stage_timing: dict = {}
        # Far enough in the past that every cycle is steady-state unless a
        # test says otherwise: the boot split must not silently swallow the
        # breaches the older tests are asserting on.
        self._scanner_started_at = _time.monotonic() - 10_000.0
        # Borrowed reader, borrowed declaration — `cycle_health` now stats the
        # heartbeat file. Pointed at a path that does not exist so the default
        # is the hermetic one; `_Beater` below overrides it with a real temp
        # file. The class attribute on Scanner is the repo's `data/` path, and
        # a test reading that would pass or fail on whether someone had run the
        # engine locally.
        self._HEARTBEAT_PATH = "/nonexistent/scanner_heartbeat"


def test_cycle_health_splits_pressure_from_a_earned_restart():
    """Two thresholds, never one.

    A cycle over the warn bound is pressure; a cycle over the healthcheck
    deadline has already earned a container restart. Pooling them would let a
    book of merely-slow cycles hide the ones that killed the engine.
    """
    from config import SCAN_CYCLE_KILL_SEC, SCAN_CYCLE_WARN_SEC

    rec = _CycleRecorder()
    rec._record_cycle_time(5.0)                       # healthy
    rec._record_cycle_time(SCAN_CYCLE_WARN_SEC + 1)   # pressure
    rec._record_cycle_time(SCAN_CYCLE_KILL_SEC + 1)   # a restart, earned

    h = rec.cycle_health()
    assert h["cycles"] == 3
    assert h["over_warn"] == 2, "a cycle past kill is also past warn"
    assert h["over_kill"] == 1
    assert h["worst_sec"] == pytest.approx(SCAN_CYCLE_KILL_SEC + 1)
    assert h["last_sec"] == pytest.approx(SCAN_CYCLE_KILL_SEC + 1)


def test_the_warn_bound_sits_below_the_deadline_it_warns_about():
    """A warning that fires at the deadline is not a warning."""
    from config import SCAN_CYCLE_KILL_SEC, SCAN_CYCLE_WARN_SEC

    assert 0 < SCAN_CYCLE_WARN_SEC < SCAN_CYCLE_KILL_SEC


def test_the_kill_bound_matches_the_healthcheck_that_enforces_it():
    """Two copies of a deadline is how one of them goes stale.

    ``healthcheck.py`` owns the real number — it is what the container runs.
    This reads it out of that file rather than trusting a comment, so moving
    one without the other fails here instead of in production.
    """
    import re
    from pathlib import Path

    from config import SCAN_CYCLE_KILL_SEC

    src = (Path(__file__).resolve().parents[1] / "healthcheck.py").read_text()
    m = re.search(r"_HEARTBEAT_MAX_AGE_SECONDS\s*=\s*([0-9.]+)", src)
    assert m, "healthcheck.py no longer declares _HEARTBEAT_MAX_AGE_SECONDS"
    assert float(m.group(1)) == SCAN_CYCLE_KILL_SEC


def test_scan_executor_is_sized_for_concurrency_not_for_the_quota():
    """The corrected premise, and why the first one was wrong.

    This test used to assert ``SCAN_EXECUTOR_WORKERS <= cpu_budget()`` — that
    the pool is sized off the cgroup rather than the host — on the reasoning
    that "the threads all contend for one GIL, so over-subscription buys
    switching cost and no throughput". Right for pure-Python work, wrong here,
    and wrong *because of the change that shipped beside it*: the indicators
    were vectorised into numpy in the same PR, and **numpy releases the GIL**.
    The pool that runs exactly that work shrank 8 -> 3 at the moment its work
    became parallelisable.

    Live evidence (2026-08-19): ``_MAX_CONCURRENT_SCANS`` is 20 and each scan
    awaits ``run_in_executor``, so the ``indicators`` stage timer spans a wait —
    461.7s of it inside a 91.15s cycle, ~5x concurrency of *waiting*, while the
    container used **1.2 of 3.2 allotted cores**. Queueing with two cores idle
    is what thread starvation looks like; a GIL ceiling looks like one core
    pinned.

    So the property is that the pool is big enough to keep concurrent scans off
    a queue, bounded, and NOT clamped to the quota. `cpu_budget()` is untouched
    and still correct for what it is actually for — reporting the quota.
    """
    from config import SCAN_EXECUTOR_WORKERS, cpu_budget

    assert cpu_budget() >= 1.0, "the quota reader still works; it is just not this knob"
    assert 2 <= SCAN_EXECUTOR_WORKERS <= 20, "bounded at both ends"
    assert SCAN_EXECUTOR_WORKERS > int(cpu_budget()), (
        "the executor must NOT be clamped to the cgroup quota — the work it "
        "runs releases the GIL, so a pool the size of the quota starves it"
    )


def test_the_executor_can_absorb_a_meaningful_share_of_concurrent_scans():
    """A pool far smaller than the concurrency limit turns into a queue.

    Not a demand that they be equal — 20 threads on a 3-core box is its own
    problem — but a floor, so a future 'tidy this up' cannot quietly return the
    pool to a size that serialises 20 concurrent scans.
    """
    from config import SCAN_EXECUTOR_WORKERS
    from src.scanner import _MAX_CONCURRENT_SCANS

    assert SCAN_EXECUTOR_WORKERS >= _MAX_CONCURRENT_SCANS // 4, (
        f"{SCAN_EXECUTOR_WORKERS} workers behind {_MAX_CONCURRENT_SCANS} "
        "concurrent scans is a queue, and the queue shows up as indicator "
        "wall-time rather than as anything named 'waiting'"
    )


def test_cpu_budget_reads_a_cgroup_v2_quota(tmp_path, monkeypatch):
    """Driven through the real file format, not a mocked return value."""
    import builtins
    import config as cfg

    real_open = builtins.open
    quota = tmp_path / "cpu.max"
    quota.write_text("250000 100000\n")   # 2.5 cores

    def fake_open(path, *a, **kw):
        if str(path) == "/sys/fs/cgroup/cpu.max":
            return real_open(quota, *a, **kw)
        raise OSError("not the file under test")

    monkeypatch.setattr(builtins, "open", fake_open)
    assert cfg.cpu_budget() == pytest.approx(2.5)


def test_cpu_budget_falls_back_to_the_host_when_unlimited(tmp_path, monkeypatch):
    import builtins
    import os as _os

    import config as cfg

    real_open = builtins.open
    quota = tmp_path / "cpu.max"
    quota.write_text("max 100000\n")

    def fake_open(path, *a, **kw):
        if str(path) == "/sys/fs/cgroup/cpu.max":
            return real_open(quota, *a, **kw)
        raise OSError("not the file under test")

    monkeypatch.setattr(builtins, "open", fake_open)
    assert cfg.cpu_budget() == float(_os.cpu_count() or 4)


# ---------------------------------------------------------------------------
# Current scan-cycle liveness verdict
# ---------------------------------------------------------------------------


def _scan_cycle_probe(rec):
    """Return the real engine predicate while keeping scanner state controlled."""
    from types import SimpleNamespace

    from src.main import CryptoSignalEngine

    stub = SimpleNamespace(_scanner=rec)
    liveness = CryptoSignalEngine._build_feature_liveness(stub)
    return next(p for p in liveness._predicate_probes if p.name == "scan_cycle")


def test_historical_cycle_breach_ages_out_of_the_liveness_verdict(tmp_path):
    from config import SCAN_CYCLE_KILL_SEC
    from src.scanner import _CYCLE_HEALTH_WINDOW

    rec = _CycleRecorder()
    rec._HEARTBEAT_PATH = str(tmp_path / "scanner_heartbeat")
    rec._touch_heartbeat()
    rec._record_cycle_time(SCAN_CYCLE_KILL_SEC + 1)
    for _ in range(_CYCLE_HEALTH_WINDOW):
        rec._record_cycle_time(5.0)

    healthy, detail = _scan_cycle_probe(rec).fn()
    assert healthy is True
    assert rec.cycle_health()["over_kill"] == 1, "lifetime evidence must remain"
    assert rec.cycle_health()["recent_over_kill"] == 0
    assert "lifetime" in detail and "recent" in detail


def test_stale_progress_heartbeat_fails_current_liveness(tmp_path):
    from config import SCAN_CYCLE_KILL_SEC

    rec = _CycleRecorder()
    rec._HEARTBEAT_PATH = str(tmp_path / "scanner_heartbeat")
    rec._touch_heartbeat()
    _os.utime(
        rec._HEARTBEAT_PATH,
        (_time.time() - SCAN_CYCLE_KILL_SEC - 1,) * 2,
    )
    rec._record_cycle_time(5.0)

    healthy, detail = _scan_cycle_probe(rec).fn()
    assert healthy is False
    assert "progress heartbeat is stale" in detail


def test_recent_sustained_cycle_pressure_fails_liveness(tmp_path):
    from config import SCAN_CYCLE_WARN_SEC

    rec = _CycleRecorder()
    rec._HEARTBEAT_PATH = str(tmp_path / "scanner_heartbeat")
    rec._touch_heartbeat()
    for _ in range(6):
        rec._record_cycle_time(SCAN_CYCLE_WARN_SEC + 1)
    for _ in range(4):
        rec._record_cycle_time(5.0)

    healthy, detail = _scan_cycle_probe(rec).fn()
    assert healthy is False
    assert "over half of the recent completed cycles" in detail


# ---------------------------------------------------------------------------
# 3. Deferred edge-store persistence
# ---------------------------------------------------------------------------

def test_record_marks_dirty_without_writing_and_flush_writes_once(tmp_path):
    """The property the money path depends on, driven end to end."""
    from src.strategy_edge import StrategyEdgeStore, StrategyOutcome

    path = tmp_path / "edge.json"
    store = StrategyEdgeStore(persist_path=str(path))

    store.record(
        StrategyOutcome(strategy="S", context_key="K", side="LONG", won=True,
                        pnl_pct=1.0, r_multiple=1.0),
        persist=False,
    )
    assert not path.exists(), "persist=False must not touch the disk"

    assert store.flush_if_dirty() is True
    assert path.exists(), "the flusher is what makes persist=False safe"

    # Clean now: a second flush must cost nothing, or the background loop
    # simply reschedules the stall it was built to remove.
    before = store.saves_total
    assert store.flush_if_dirty() is False
    assert store.saves_total == before
    assert store.skipped_clean_flushes >= 1


def test_a_failed_save_leaves_the_store_dirty(tmp_path, monkeypatch):
    """Otherwise one transient disk error silently drops the window."""
    from src import strategy_edge as se

    path = tmp_path / "edge.json"
    store = se.StrategyEdgeStore(persist_path=str(path))
    store.record(
        se.StrategyOutcome(strategy="S", context_key="K", side="LONG", won=True,
                           pnl_pct=1.0, r_multiple=1.0),
        persist=False,
    )

    def boom(*a, **kw):
        raise OSError("disk full")

    monkeypatch.setattr(se.os, "replace", boom)
    store.flush_if_dirty()
    monkeypatch.undo()

    assert store.flush_if_dirty() is True, "a failed save must be retried"
    assert path.exists()


def test_trade_monitor_does_not_persist_the_edge_store_inline():
    """Pin the CALL SITE, not the method.

    ``_record_outcome`` is synchronous and reached from ``_evaluate_signal``,
    so a ``persist=True`` here is a ~2s freeze of the whole event loop per
    closed signal. The store's own docstring has warned about this since
    2026-07-13; the batch feeders were fixed and this caller was not. Asserted
    by walking the tree, because a substring check would go green on a comment.
    """
    import ast
    import inspect

    from src import trade_monitor as tm

    tree = ast.parse(inspect.getsource(tm))
    target = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_record_outcome":
            target = node
            break
    assert target is not None, "trade_monitor._record_outcome not found"

    calls = [
        n for n in ast.walk(target)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == "record"
        and isinstance(n.func.value, ast.Attribute)
        and n.func.value.attr == "_strategy_edge_store"
    ]
    assert calls, "no edge-store record() call found — has the call site moved?"
    for call in calls:
        kw = {k.arg: k.value for k in call.keywords}
        assert "persist" in kw, (
            "an edge-store record() on the event loop must state its persist "
            "mode explicitly; the default is True and dumps ~40 MB inline"
        )
        assert isinstance(kw["persist"], ast.Constant) and kw["persist"].value is False, (
            "persist must be False here — the write happens in "
            "_strategy_edge_flush_loop, off the event loop"
        )


def test_the_kill_switch_restores_the_old_count_only_key(monkeypatch):
    """The revert path has to actually revert, or it is decoration.

    Driven through the real module attribute the fingerprint reads, and
    asserted on the property that matters: with the switch off, a capped bucket
    that rolled a bar forward compares EQUAL again — which is the old bug, and
    is exactly what an operator flipping this switch is choosing.
    """
    import src.scanner as sc

    n = _CANDLE_BUCKET_CAP
    before = _bucket(n, start=0.0)
    after = _bucket(n, start=60_000.0)

    monkeypatch.setattr(sc, "INDICATOR_CACHE_CONTENT_KEY", False)
    assert Scanner._series_fingerprint(before) == Scanner._series_fingerprint(after)

    monkeypatch.setattr(sc, "INDICATOR_CACHE_CONTENT_KEY", True)
    assert Scanner._series_fingerprint(before) != Scanner._series_fingerprint(after)


def test_the_content_key_defaults_on():
    """A correctness fix shipped OFF is a fault nobody is fixing."""
    from config import INDICATOR_CACHE_CONTENT_KEY

    assert INDICATOR_CACHE_CONTENT_KEY is True


def test_boot_warmup_breaches_are_counted_apart_from_steady_state_ones():
    """A cold start legitimately runs long, and the healthcheck knows it.

    Measured after a real deploy: 74.5s / 131.2s / 72.8s for the first three
    cycles (75 pairs re-seeded over REST, every indicator cache cold), then a
    steady state of 8-47s. Folding those into the verdict made the probe read
    violating for the whole life of a healthy boot — red that can never be
    anything but red, which this repo has already paid for once on the agent
    container's healthcheck.
    """
    from config import SCAN_CYCLE_BOOT_GRACE_SEC, SCAN_CYCLE_KILL_SEC

    rec = _CycleRecorder()

    # Inside the grace: a breach is warm-up. Driven by moving the recorder's
    # start time, so the REAL _uptime_sec decides — a stubbed uptime would test
    # the stub.
    rec._scanner_started_at = _time.monotonic() - (SCAN_CYCLE_BOOT_GRACE_SEC - 60)
    rec._record_cycle_time(SCAN_CYCLE_KILL_SEC + 11)

    # Outside it: the same cycle length is a fault.
    rec._scanner_started_at = _time.monotonic() - (SCAN_CYCLE_BOOT_GRACE_SEC + 60)
    rec._record_cycle_time(SCAN_CYCLE_KILL_SEC + 11)

    h = rec.cycle_health()
    assert h["over_kill"] == 1, "the steady-state breach must page"
    assert h["over_kill_boot"] == 1, "the boot breach must be recorded"
    assert h["cycles"] == 2, "both are real cycles and both are counted"
    assert h["worst_sec"] == pytest.approx(SCAN_CYCLE_KILL_SEC + 11), (
        "worst_sec spans everything — excluding boot from the VERDICT is not "
        "excluding it from the record"
    )


def test_the_boot_grace_matches_the_healthcheck_that_enforces_it():
    """Derived from the file that runs in the container, not from a comment."""
    import re
    from pathlib import Path

    from config import SCAN_CYCLE_BOOT_GRACE_SEC

    src = (Path(__file__).resolve().parents[1] / "healthcheck.py").read_text()
    m = re.search(r"_HEARTBEAT_GRACE_PERIOD_SECONDS\s*=\s*([0-9.]+)", src)
    assert m, "healthcheck.py no longer declares _HEARTBEAT_GRACE_PERIOD_SECONDS"
    assert float(m.group(1)) == SCAN_CYCLE_BOOT_GRACE_SEC


def test_scanner_uptime_is_monotonic_not_wall_clock():
    """A clock step must not turn a running engine back into a booting one.

    That would move a steady-state deadline breach into the bucket that does
    not page — the one direction this split must never fail in.
    """
    import ast
    import inspect
    import textwrap

    from src.scanner import Scanner

    # dedent: getsource on a method keeps its class indentation, which ast rejects.
    tree = ast.parse(textwrap.dedent(inspect.getsource(Scanner._uptime_sec)))
    names = {
        n.attr for n in ast.walk(tree)
        if isinstance(n, ast.Attribute)
    }
    assert "monotonic" in names, "uptime must come from time.monotonic()"
    assert "time" not in names or "monotonic" in names


def test_a_slow_cycle_keeps_its_stage_breakdown():
    """"Where did a 156s cycle go" must be answerable without reading a log.

    The breakdown already existed and was logged and nowhere else. On the
    owner's box on 2026-08-19 the grep for it returned NOTHING while the
    deadline warnings beside it came through, so the one question that aims the
    next fix had no answer on any surface. Keeping the dict costs a copy.
    """
    from config import SCAN_CYCLE_WARN_SEC

    rec = _CycleRecorder()
    rec._record_cycle_time(5.0, {"smc": 1.0, "indicators": 0.5})
    h = rec.cycle_health()
    assert h["worst_stages"] == {"smc": 1.0, "indicators": 0.5}
    assert h["last_slow_stages"] == {}, "a healthy cycle is not a slow one"

    rec._record_cycle_time(SCAN_CYCLE_WARN_SEC + 40, {"smc": 41.0, "predictive": 3.0})
    h = rec.cycle_health()
    assert h["worst_stages"] == {"smc": 41.0, "predictive": 3.0}
    assert h["last_slow_stages"] == {"smc": 41.0, "predictive": 3.0}
    assert h["last_slow_sec"] == pytest.approx(SCAN_CYCLE_WARN_SEC + 40)

    # A later FAST cycle must not overwrite the worst breakdown — that is the
    # one a reader needs, and it is gone the moment it is replaced by weather.
    rec._record_cycle_time(4.0, {"smc": 0.9})
    assert rec.cycle_health()["worst_stages"] == {"smc": 41.0, "predictive": 3.0}


def test_stages_are_ordered_worst_first():
    """The RATIO locates the cost, so the expensive stage leads."""
    rec = _CycleRecorder()
    rec._record_cycle_time(90.0, {"cheap": 0.2, "expensive": 55.0, "mid": 4.0})
    assert list(rec.cycle_health()["worst_stages"]) == ["expensive", "mid", "cheap"]


def test_a_cycle_with_no_stage_data_does_not_wipe_what_is_there():
    """An empty dict is "nothing recorded", not "nothing happened"."""
    rec = _CycleRecorder()
    rec._record_cycle_time(90.0, {"smc": 40.0})
    rec._record_cycle_time(200.0, {})          # no stages captured
    h = rec.cycle_health()
    assert h["worst_sec"] == pytest.approx(200.0), "the timing still counts"
    assert h["worst_stages"] == {"smc": 40.0}, "the last known breakdown survives"


# ---------------------------------------------------------------------------
# The blind spot: a cycle that has not finished.
# ---------------------------------------------------------------------------

def test_an_in_flight_cycle_is_visible_before_it_completes():
    """The defect this section exists for, stated directly.

    Every counter in `cycle_health` records a cycle at COMPLETION. But
    `healthcheck.py` kills the container on heartbeat-file age, the heartbeat is
    touched once per completed cycle, and a cycle hung past the deadline
    therefore appears in NONE of them. Live on 2026-08-19: the ops card read
    "0 past the deadline, last cycle 20.76s" while autoheal was restarting the
    engine on a failing streak of 3 — the page read healthy precisely while the
    container was being killed.
    """
    import time as _t

    rec = _CycleRecorder()
    rec._record_cycle_time(20.0)                       # a fast, FINISHED cycle
    rec._cycle_started_at = _t.time() - 200.0          # and one hung for 200s

    h = rec.cycle_health()
    assert h["over_kill"] == 0, "the finished cycle really was fast"
    assert h["last_sec"] == pytest.approx(20.0)
    assert h["in_flight_sec"] >= 199.0, (
        "a hung cycle must be visible WHILE it hangs — that is the whole point"
    )


def test_the_completed_cycle_age_is_reported_beside_the_beat():
    """`healthcheck.py` grades the heartbeat FILE; the page must show it.

    This test asserted the same property against `heartbeat_age_sec` until
    2026-08-19, when the beat stopped being written only at the end of a cycle.
    The assertion would still have passed — the key was computed from
    `last_cycle_at` and nothing had told it otherwise — which is precisely the
    rot case: an assertion outliving its premise at the moment somebody changes
    the premise. The completed-cycle age is still worth reporting (a cycle that
    has not finished in ten minutes is real news); it is simply no longer the
    quantity that decides whether the container lives, and it is now named for
    what it is.
    """
    import time as _t

    from config import SCAN_CYCLE_KILL_SEC

    rec = _CycleRecorder()
    rec._record_cycle_time(9.0)
    rec.last_cycle_at = _t.time() - (SCAN_CYCLE_KILL_SEC + 40)

    h = rec.cycle_health()
    assert h["cycle_completed_age_sec"] > SCAN_CYCLE_KILL_SEC
    assert h["heartbeat_age_sec"] is None, (
        "no beat file here, and an unreadable beat must never read as fresh"
    )


def test_both_ages_are_none_before_anything_has_run():
    """Absent is not zero: 0s would read as 'a cycle just completed'."""
    rec = _CycleRecorder()
    h = rec.cycle_health()
    assert h["in_flight_sec"] is None
    assert h["heartbeat_age_sec"] is None


def test_the_concurrency_limit_is_reported_beside_the_pool_it_queues_on():
    """One without the other cannot say whether the surplus is queueing."""
    from config import SCAN_EXECUTOR_WORKERS
    from src.scanner import _MAX_CONCURRENT_SCANS

    h = _CycleRecorder().cycle_health()
    assert h["max_concurrent_scans"] == _MAX_CONCURRENT_SCANS
    assert h["executor_workers"] == SCAN_EXECUTOR_WORKERS


def test_the_concurrency_limit_is_env_overridable_and_refuses_nonsense():
    """It was the one plausible lever on a live restart loop that could not be
    pulled without a deploy. Zero is not a tuning choice, it is a stopped
    scanner, so it is refused rather than honoured."""
    from src.scanner import _safe_int_env

    assert _safe_int_env("A_NAME_NOTHING_SETS", 20) == 20
    import os

    os.environ["_TEST_CONC"] = "6"
    try:
        assert _safe_int_env("_TEST_CONC", 20) == 6
        for bad in ("0", "-4", "", "abc"):
            os.environ["_TEST_CONC"] = bad
            assert _safe_int_env("_TEST_CONC", 20) == 20, bad
    finally:
        os.environ.pop("_TEST_CONC", None)


def test_the_in_flight_cycle_reports_the_stage_it_is_stuck_in():
    """The one breakdown a hung cycle can produce.

    `worst_stages` is captured at COMPLETION, so a cycle that never completes
    never contributes to it — the hung cycle is exactly the one whose stages are
    invisible. `_stage_timing` accumulates as the cycle runs and is cleared at
    its start, so mid-hang it names the stage that is stuck.

    Measured 2026-08-19: a hang published `in_flight_sec: 186.05` while the
    snapshot writer kept publishing, so the loop was not blocked — the scan was
    awaiting something that does not return. These sums say which await.
    """
    import time as _t

    rec = _CycleRecorder()
    rec._cycle_started_at = _t.time() - 186.0
    rec._stage_timing = {"smc": 3.1, "indicators": 181.4, "predictive": 0.2}

    h = rec.cycle_health()
    assert h["in_flight_sec"] >= 185.0
    assert list(h["in_flight_stages"])[0] == "indicators", "worst stage leads"
    assert h["in_flight_stages"]["indicators"] == 181.4
    assert h["worst_stages"] == {}, (
        "the hung cycle contributes nothing to the completed-cycle breakdown — "
        "which is the entire reason the in-flight one has to exist"
    )


def test_in_flight_stages_are_empty_before_any_cycle_starts():
    rec = _CycleRecorder()
    assert rec.cycle_health()["in_flight_stages"] == {}


# ---------------------------------------------------------------------------
# 4. The heartbeat: progress, not completion
# ---------------------------------------------------------------------------
#
# The 2026-08-19 restart loop. `healthcheck.py` fails when the heartbeat file
# is older than 120s, three failures flip the container unhealthy and autoheal
# restarts it — and the file's only writer was the END of a scan cycle. So
# "heartbeat age" and "cycle wall-time" were one number, and a cycle slower
# than the deadline WAS a restart however healthily the loop was advancing.
# The restart then re-seeded every pair over REST and rebuilt the indicator
# caches cold, making the next cycle slower than the one that tripped it.


class _Beater(_CycleRecorder):
    """The heartbeat half of Scanner, over a temp path. Real methods, again."""

    _scan_symbol_bounded = Scanner._scan_symbol_bounded

    def __init__(self, path: str) -> None:
        super().__init__()
        self._HEARTBEAT_PATH = path
        self.scanned: list = []
        self.raise_on: set = set()

    async def _scan_symbol(self, symbol: str, volume_24h: float) -> None:
        self.scanned.append(symbol)
        if symbol in self.raise_on:
            raise RuntimeError("evaluator blew up")


def _age(path: str) -> float:
    return _time.time() - _os.path.getmtime(path)


async def test_a_finished_symbol_beats_the_heartbeat(tmp_path):
    """A slow cycle keeps beating, because the beat means progress."""
    p = str(tmp_path / "scanner_heartbeat")
    b = _Beater(p)
    await b._scan_symbol_bounded(_asyncio.Semaphore(1), "BTCUSDT", 1.0)

    assert b.scanned == ["BTCUSDT"]
    assert _os.path.isfile(p), "no beat: a slow cycle is a restart again"
    assert b._heartbeat_progress_writes == 1


async def test_a_raising_symbol_still_counts_as_progress(tmp_path):
    """`gather` collects the exception and the cycle carries on — so the loop
    IS advancing, and a scanner that only counted clean symbols would restart
    the container over one bad pair."""
    p = str(tmp_path / "scanner_heartbeat")
    b = _Beater(p)
    b.raise_on = {"BADUSDT"}
    with pytest.raises(RuntimeError):
        await b._scan_symbol_bounded(_asyncio.Semaphore(1), "BADUSDT", 1.0)
    assert b._heartbeat_progress_writes == 1


async def test_the_beat_is_throttled_not_per_symbol(tmp_path):
    """Bounded write rate regardless of pair count — and well under the 120s
    the healthcheck allows, so the throttle can never itself cause a restart."""
    from src.scanner import _HEARTBEAT_PROGRESS_MIN_INTERVAL_SEC

    p = str(tmp_path / "scanner_heartbeat")
    b = _Beater(p)
    sem = _asyncio.Semaphore(1)
    for i in range(50):
        await b._scan_symbol_bounded(sem, f"SYM{i}USDT", 1.0)
    assert b._heartbeat_progress_writes == 1
    assert _HEARTBEAT_PROGRESS_MIN_INTERVAL_SEC < healthcheck._HEARTBEAT_MAX_AGE_SECONDS


async def test_the_progress_beat_has_an_off_switch(tmp_path, monkeypatch):
    p = str(tmp_path / "scanner_heartbeat")
    b = _Beater(p)
    monkeypatch.setattr("src.scanner.SCANNER_PROGRESS_HEARTBEAT", False)
    await b._scan_symbol_bounded(_asyncio.Semaphore(1), "BTCUSDT", 1.0)
    assert b._heartbeat_progress_writes == 0
    assert not _os.path.isfile(p)


def test_heartbeat_age_reports_the_file_the_healthcheck_stats(tmp_path):
    """The key named for the heartbeat must report the heartbeat.

    It was computed from `last_cycle_at` — the age of the last COMPLETED cycle —
    which was the same number only while the cycle end was the only writer. Ops
    grades `/system/liveness` "hanging" off this key, so with a progress beat in
    place a key still reporting completion would keep calling a healthy slow
    cycle a hang. Both are published, under the name each one is.
    """
    p = str(tmp_path / "scanner_heartbeat")
    b = _Beater(p)
    b._touch_heartbeat()
    b.last_cycle_at = _time.time() - 500.0

    h = b.cycle_health()
    assert h["heartbeat_age_sec"] < 5, "reported the cycle age, not the beat"
    assert h["cycle_completed_age_sec"] == pytest.approx(500.0, abs=5)
    assert h["progress_heartbeat_enabled"] is True


def test_heartbeat_age_is_none_when_the_file_is_unreadable(tmp_path):
    """Absent is not fresh. A missing file must not read as age 0 — that is the
    one direction in which this key can hide a real wedge."""
    b = _Beater(str(tmp_path / "never_written"))
    assert b.cycle_health()["heartbeat_age_sec"] is None
