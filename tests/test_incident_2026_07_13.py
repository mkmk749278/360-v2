"""2026-07-13 incident regressions — the event-loop-wedge class.

Three properties, each pinned so a future edit can't quietly reintroduce the
failure mode:

1. RuntimeTunables reads NEVER block on Firestore after the cold read — TTL
   expiry serves the stale cache and refreshes in a single-flight background
   thread; a failed refresh keeps last-known values.
2. StrategyEdgeStore batch feeding: ``record(persist=False)`` defers the
   full-store JSON dump; one ``save()`` persists the batch.
3. healthcheck treats a pre-restart heartbeat mtime as "warming up" inside
   the boot grace instead of flipping the container UNHEALTHY mid-boot.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from src.runtime_tunables import RuntimeTunables
from src.strategy_edge import StrategyEdgeStore, StrategyOutcome

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import healthcheck  # noqa: E402


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class _FakeDoc:
    def __init__(self, values, exists=True):
        self._values = values
        self.exists = exists

    def to_dict(self):
        return dict(self._values)


class _FakeFirestore:
    """Counts reads; can be told to fail."""

    def __init__(self, values):
        self.values = values
        self.reads = 0
        self.fail = False

    def collection(self, _name):
        return self

    def document(self, _name):
        return self

    def get(self):
        self.reads += 1
        if self.fail:
            raise ConnectionError("simulated Firestore stall/outage")
        return _FakeDoc(self.values)

    def set(self, payload, merge=False):
        self.values.update(payload)


class _Clock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


def _make(values=None):
    db = _FakeFirestore(values if values is not None else {"market_context_enabled": False})
    clock = _Clock()
    rt = RuntimeTunables(db, clock=clock)
    spawned: list[int] = []
    # Deterministic tests: capture spawn requests instead of real threads;
    # the test decides when the "background" refresh completes via _refresh().
    rt._spawn_refresh = lambda: spawned.append(1)  # type: ignore[method-assign]
    return rt, db, clock, spawned


class TestTunablesNeverBlockTheLoop:
    def test_cold_read_fetches_inline_once(self):
        rt, db, clock, spawned = _make()
        assert rt._doc_values() == {"market_context_enabled": False}
        assert db.reads == 1
        # Within TTL: served from cache, no fetch, no spawn.
        clock.t += 1.0
        rt._doc_values()
        assert db.reads == 1 and spawned == []

    def test_ttl_expiry_serves_stale_and_spawns_single_flight(self):
        rt, db, clock, spawned = _make()
        rt._doc_values()
        clock.t += 10.0  # past the 5s TTL
        db.values = {"market_context_enabled": True}
        # Stale value served immediately — the caller never waits.
        assert rt._doc_values() == {"market_context_enabled": False}
        assert db.reads == 1  # no inline fetch
        assert spawned == [1]
        # Second read while the refresh is still in flight: no second spawn.
        assert rt._doc_values() == {"market_context_enabled": False}
        assert spawned == [1]
        # "Background" refresh completes → new values served.
        rt._refresh()
        assert rt._doc_values() == {"market_context_enabled": True}
        assert db.reads == 2

    def test_failed_refresh_keeps_last_known_values(self):
        rt, db, clock, spawned = _make()
        rt._doc_values()
        clock.t += 10.0
        db.fail = True
        assert rt._doc_values() == {"market_context_enabled": False}
        rt._refresh()  # fails
        # Still last-known (an owner-set flag must survive a Firestore blip),
        # and the next expiry re-spawns a retry.
        assert rt._doc_values() == {"market_context_enabled": False}
        assert len(spawned) == 2

    def test_cold_read_failure_falls_to_env_defaults_without_reblocking(self):
        rt, db, clock, spawned = _make()
        db.fail = True
        assert rt._doc_values() == {}
        # Subsequent reads never inline-fetch again — they serve {} and retry
        # in the background.
        reads_before = db.reads
        assert rt._doc_values() == {}
        assert db.reads == reads_before
        assert spawned == [1]

    def test_set_values_merges_into_cache_without_dropping_it(self):
        rt, db, clock, spawned = _make({"market_context_enabled": False})
        rt._doc_values()
        rt.set_values({"market_context_enabled": True})
        # Fresh value visible immediately, from cache, with no inline fetch.
        reads_before = db.reads
        assert rt._doc_values() == {"market_context_enabled": True}
        assert db.reads == reads_before and spawned == []


class TestEdgeStoreBatchPersistence:
    @staticmethod
    def _outcome(i=0):
        return StrategyOutcome(
            strategy="SR_FLIP_RETEST",
            context_key="OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL",
            side="LONG",
            won=i % 2 == 0,
            pnl_pct=1.0,
            r_multiple=1.0,
            source="shadow",
        )

    def test_persist_false_defers_the_dump(self, tmp_path):
        path = tmp_path / "edge.json"
        store = StrategyEdgeStore(persist_path=str(path))
        for i in range(10):
            store.record(self._outcome(i), persist=False)
        assert not path.exists()  # nothing written record-by-record
        store.save()
        assert path.exists()
        saved = json.loads(path.read_text())
        assert sum(len(v) for v in saved.values()) == 10

    def test_default_record_still_persists(self, tmp_path):
        path = tmp_path / "edge.json"
        store = StrategyEdgeStore(persist_path=str(path))
        store.record(self._outcome())
        assert path.exists()


class TestHealthcheckWarmupGrace:
    def _hb(self, tmp_path, age):
        import os

        p = tmp_path / "scanner_heartbeat"
        p.write_text("x")
        os.utime(p, (time.time() - age, time.time() - age))
        return str(p)

    def test_pre_restart_mtime_is_warming_up_inside_grace(self, tmp_path, monkeypatch):
        monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", self._hb(tmp_path, age=2000))
        monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 90.0)
        assert healthcheck._scanner_heartbeat_fresh(engine_pid=1234) is True

    def test_stale_after_grace_fails(self, tmp_path, monkeypatch):
        # First never-beat-since-boot occurrence past grace still FAILS so
        # autoheal gets its (bounded) restart attempt. Isolate the restart-guard
        # state to a fresh file so the counter starts at 0 regardless of any
        # prior run (the loop-break only triggers after repeated restarts —
        # covered in test_healthcheck.py).
        monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", self._hb(tmp_path, age=2000))
        monkeypatch.setattr(
            healthcheck, "_RESTART_GUARD_STATE_PATH", str(tmp_path / "restart_guard")
        )
        monkeypatch.setattr(
            healthcheck,
            "_engine_uptime_seconds",
            lambda pid: healthcheck._HEARTBEAT_GRACE_PERIOD_SECONDS + 60.0,
        )
        assert healthcheck._scanner_heartbeat_fresh(engine_pid=1234) is False

    def test_wedge_younger_than_uptime_still_fails(self, tmp_path, monkeypatch):
        # Engine up 100s but heartbeat 130s old (> the 120s bound) and
        # YOUNGER than a restart boundary — a genuine in-flight wedge is
        # never excused by the grace (age <= uptime → not a warmup case).
        monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", self._hb(tmp_path, age=130))
        monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 300.0)
        assert healthcheck._scanner_heartbeat_fresh(engine_pid=1234) is False

    def test_fresh_heartbeat_passes(self, tmp_path, monkeypatch):
        monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", self._hb(tmp_path, age=5))
        assert healthcheck._scanner_heartbeat_fresh(engine_pid=1234) is True
