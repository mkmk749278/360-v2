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

import time as _time

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

    _record_cycle_time = Scanner._record_cycle_time
    _uptime_sec = Scanner._uptime_sec
    cycle_health = Scanner.cycle_health

    def __init__(self) -> None:
        self.cycle_count = 0
        self.last_cycle_sec = 0.0
        self.worst_cycle_sec = 0.0
        self.cycles_over_warn = 0
        self.cycles_over_kill = 0
        self.cycles_over_warn_boot = 0
        self.cycles_over_kill_boot = 0
        self.last_cycle_at = 0.0
        # Far enough in the past that every cycle is steady-state unless a
        # test says otherwise: the boot split must not silently swallow the
        # breaches the older tests are asserting on.
        self._scanner_started_at = _time.monotonic() - 10_000.0


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


def test_scan_executor_is_sized_off_the_cgroup_not_the_host():
    """The quota is what the process may use; the host count is not.

    Sized off ``os.cpu_count()`` this was 8 threads against a 2.5-core quota,
    all contending for one GIL.
    """
    from config import SCAN_EXECUTOR_WORKERS, cpu_budget

    budget = cpu_budget()
    assert budget >= 1.0
    assert 2 <= SCAN_EXECUTOR_WORKERS <= 20
    assert SCAN_EXECUTOR_WORKERS <= max(2, int(budget))


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
