"""Tests for the background snapshot pre-computation cache.

``snapshot_cache`` sits on every app-facing read (``/api/signals``,
``/api/activity``, ``/api/agents``): route handlers serve from it when
warm and fall back to live builders when it returns ``None``.  Until now
it was only ever exercised implicitly (and the TestClient without a
lifespan never even started it — see the note in test_billing_play.py),
so a regression in warm/stale detection or the ``is_open`` filter split
would reach the Lumin app unseen.

What we pin here:

* cold / stale caches return ``None`` (fall back to live build) for all
  three payloads, each honouring its own max-age;
* ``filter_signals`` splits open/closed on the authoritative ``is_open``
  field — including the mover-runner case where status ``TP1_HIT`` is
  still OPEN — and only falls back to the legacy status heuristic for
  payloads that pre-date the field (stale Redis snapshot across a deploy);
* setup-class filtering is case-insensitive and ``limit`` applies last;
* the Redis-backed refreshers tolerate a down Redis, a missing key and a
  malformed item without ever raising into the loop;
* ``start`` / ``stop`` lifecycle: pre-warm fills the cache, background
  tasks exist, ``stop`` cancels them.

No network, no real Redis — fakes only.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Optional
from unittest.mock import MagicMock

import pytest

pytest.importorskip("pydantic")

from src.api.schemas import ActivityEvent, SignalDetail
from src.api.snapshot_cache import SnapshotCache
from src.api.snapshot_store import KEY_SIGNALS_ALL, encode


def _signal_payload(**overrides: Any) -> dict:
    """Minimal valid SignalDetail payload; overrides win."""
    base = dict(
        signal_id="sig-1",
        symbol="BTCUSDT",
        direction="LONG",
        entry=100.0,
        stop_loss=99.0,
        tp1=101.0,
        tp2=102.0,
        confidence=80.0,
        quality_tier="A+",
        setup_class="BREAKOUT",
        agent_name="Breakout Hunter",
        status="ACTIVE",
        current_price=100.5,
        pnl_pct=0.5,
        timestamp=datetime.now(timezone.utc),
        minutes_ago=5,
    )
    base.update(overrides)
    return base


def _detail(**overrides: Any) -> SignalDetail:
    return SignalDetail(**_signal_payload(**overrides))


def _warm_signals(cache: SnapshotCache, items: list) -> None:
    cache._signals_all = items
    cache._cached_at = time.monotonic()


class TestFilterSignalsWarmth:
    def test_cold_cache_returns_none(self):
        cache = SnapshotCache()
        assert cache.filter_signals() is None
        assert not cache.is_warm

    def test_stale_cache_returns_none(self):
        cache = SnapshotCache()
        cache._signals_all = [_detail()]
        cache._cached_at = time.monotonic() - 31.0
        assert cache.filter_signals() is None

    def test_warm_cache_returns_items(self):
        cache = SnapshotCache()
        _warm_signals(cache, [_detail()])
        items = cache.filter_signals()
        assert items is not None
        assert len(items) == 1

    def test_age_seconds_infinite_when_cold(self):
        cache = SnapshotCache()
        assert cache.age_seconds == float("inf")

    def test_age_seconds_finite_when_warm(self):
        cache = SnapshotCache()
        _warm_signals(cache, [])
        assert cache.age_seconds < 1.0


class TestFilterSignalsIsOpen:
    """``is_open`` is authoritative (2026-07-10) — the status string alone
    can no longer split open from closed views."""

    def test_mover_runner_at_tp1_hit_is_open(self):
        # A mover riding the runner trail has status TP1_HIT but is OPEN.
        cache = SnapshotCache()
        _warm_signals(
            cache,
            [_detail(signal_id="mover", status="TP1_HIT", is_open=True)],
        )
        open_items = cache.filter_signals(status="open")
        closed_items = cache.filter_signals(status="closed")
        assert [s.signal_id for s in open_items] == ["mover"]
        assert closed_items == []

    def test_non_mover_at_tp1_hit_is_closed(self):
        # BE-then-TP1 non-mover CLOSES at TP1_HIT.
        cache = SnapshotCache()
        _warm_signals(
            cache,
            [_detail(signal_id="done", status="TP1_HIT", is_open=False)],
        )
        assert cache.filter_signals(status="open") == []
        assert [s.signal_id for s in cache.filter_signals(status="closed")] == [
            "done"
        ]

    def test_legacy_payload_without_is_open_uses_status_heuristic(self):
        # Stale Redis snapshot across the deploy that introduced is_open:
        # the field is absent from model_fields_set, so ACTIVE→open and
        # anything else→closed.
        cache = SnapshotCache()
        legacy_open = SignalDetail(
            **{
                k: v
                for k, v in _signal_payload(
                    signal_id="legacy-open", status="ACTIVE"
                ).items()
                if k != "is_open"
            }
        )
        legacy_closed = SignalDetail(
            **{
                k: v
                for k, v in _signal_payload(
                    signal_id="legacy-closed", status="TP1_HIT"
                ).items()
                if k != "is_open"
            }
        )
        assert "is_open" not in legacy_open.model_fields_set
        _warm_signals(cache, [legacy_open, legacy_closed])
        assert [s.signal_id for s in cache.filter_signals(status="open")] == [
            "legacy-open"
        ]
        assert [s.signal_id for s in cache.filter_signals(status="closed")] == [
            "legacy-closed"
        ]

    def test_status_all_returns_everything(self):
        cache = SnapshotCache()
        _warm_signals(
            cache,
            [
                _detail(signal_id="a", is_open=True),
                _detail(signal_id="b", status="SL_HIT", is_open=False),
            ],
        )
        assert len(cache.filter_signals(status="all")) == 2


class TestFilterSignalsSetupClassAndLimit:
    def test_setup_class_filter_is_case_insensitive(self):
        cache = SnapshotCache()
        _warm_signals(
            cache,
            [
                _detail(signal_id="a", setup_class="BREAKOUT"),
                _detail(signal_id="b", setup_class="RANGE_FADE"),
            ],
        )
        items = cache.filter_signals(setup_class="breakout")
        assert [s.signal_id for s in items] == ["a"]

    def test_limit_applies_after_filtering(self):
        cache = SnapshotCache()
        _warm_signals(
            cache,
            [_detail(signal_id=f"s{i}") for i in range(10)],
        )
        assert len(cache.filter_signals(limit=3)) == 3


class TestFilterActivity:
    def _event(self) -> ActivityEvent:
        return ActivityEvent(
            kind="OPEN",
            title="BTCUSDT LONG",
            subtitle="entry 100.0",
            timestamp=datetime.now(timezone.utc),
            minutes_ago=1,
        )

    def test_cold_returns_none(self):
        assert SnapshotCache().filter_activity() is None

    def test_respects_60s_max_age(self):
        cache = SnapshotCache()
        cache._activity_all = [self._event()]
        cache._activity_cached_at = time.monotonic() - 45.0
        # 45 s old — stale for signals (30 s) but warm for activity (60 s).
        assert cache.filter_activity() is not None
        cache._activity_cached_at = time.monotonic() - 61.0
        assert cache.filter_activity() is None

    def test_setup_class_query_falls_back_to_live_build(self):
        # ActivityEvent carries no setup_class field, so the cache cannot
        # answer a per-evaluator filter.  Regression pin for 2026-07-17:
        # this used to raise AttributeError into the route's catch-all,
        # returning an EMPTY activity list whenever the cache was warm.
        cache = SnapshotCache()
        cache._activity_all = [self._event(), self._event()]
        cache._activity_cached_at = time.monotonic()
        assert cache.filter_activity(setup_class="breakout") is None

    def test_limit_applies(self):
        cache = SnapshotCache()
        cache._activity_all = [self._event() for _ in range(5)]
        cache._activity_cached_at = time.monotonic()
        assert len(cache.filter_activity(limit=2)) == 2


class TestGetAgents:
    def test_cold_returns_none(self):
        assert SnapshotCache().get_agents() is None

    def test_respects_90s_max_age(self):
        cache = SnapshotCache()
        cache._agents_all = []
        cache._agents_cached_at = time.monotonic() - 75.0
        assert cache.get_agents() is not None
        cache._agents_cached_at = time.monotonic() - 91.0
        assert cache.get_agents() is None


class _FakeRedis:
    """Duck-typed stand-in for the RedisClient the cache reads through."""

    def __init__(self, data: Optional[dict] = None, available: bool = True):
        self.available = available
        self._data = data or {}
        self.client = self

    async def get(self, key: str):
        return self._data.get(key)


class TestRedisRefreshers:
    async def test_refresh_from_redis_parses_items(self):
        cache = SnapshotCache()
        cache._redis = _FakeRedis(
            {KEY_SIGNALS_ALL: encode([_signal_payload(signal_id="r1")])}
        )
        await cache._refresh_signals_from_redis()
        items = cache.filter_signals()
        assert [s.signal_id for s in items] == ["r1"]

    async def test_malformed_item_is_skipped_not_fatal(self):
        # One rotten dict must not poison the whole snapshot.
        cache = SnapshotCache()
        cache._redis = _FakeRedis(
            {
                KEY_SIGNALS_ALL: encode(
                    [
                        {"signal_id": "broken"},  # missing required fields
                        _signal_payload(signal_id="ok"),
                    ]
                )
            }
        )
        await cache._refresh_signals_from_redis()
        items = cache.filter_signals()
        assert [s.signal_id for s in items] == ["ok"]

    async def test_missing_key_keeps_cache_cold(self):
        cache = SnapshotCache()
        cache._redis = _FakeRedis({})
        await cache._refresh_signals_from_redis()
        assert cache.filter_signals() is None

    async def test_unavailable_redis_is_a_noop(self):
        cache = SnapshotCache()
        cache._redis = _FakeRedis(available=False)
        await cache._refresh_signals_from_redis()
        assert cache.filter_signals() is None

    async def test_corrupt_json_keeps_cache_cold(self):
        cache = SnapshotCache()
        cache._redis = _FakeRedis({KEY_SIGNALS_ALL: "{not json"})
        await cache._refresh_signals_from_redis()
        assert cache.filter_signals() is None


class TestLifecycle:
    async def test_start_prewarms_and_stop_cancels(self, monkeypatch):
        import src.api.snapshot as snapshot_mod

        monkeypatch.setattr(
            snapshot_mod, "build_signals", lambda engine, **kw: [_detail()]
        )
        monkeypatch.setattr(snapshot_mod, "build_activity", MagicMock())
        monkeypatch.setattr(snapshot_mod, "build_agents", MagicMock())

        cache = SnapshotCache()
        await cache.start(engine=MagicMock())
        try:
            # Pre-warm ran synchronously inside start() — cache is warm
            # before the first 5 s interval elapses.
            assert cache.is_warm
            assert cache.filter_signals() is not None
            assert cache._task is not None and not cache._task.done()
            assert (
                cache._activity_task is not None
                and not cache._activity_task.done()
            )
            assert (
                cache._agents_task is not None and not cache._agents_task.done()
            )
        finally:
            await cache.stop()
        assert cache._task is None
        assert cache._activity_task is None
        assert cache._agents_task is None

    async def test_start_survives_prewarm_failure(self, monkeypatch):
        # A failing pre-warm must leave the cache cold but the loops running
        # (first request falls back to the live builder — no request fails).
        import src.api.snapshot as snapshot_mod

        def _boom(engine, **kw):
            raise RuntimeError("engine not ready")

        monkeypatch.setattr(snapshot_mod, "build_signals", _boom)
        cache = SnapshotCache()
        await cache.start(engine=MagicMock())
        try:
            assert not cache.is_warm
            assert cache.filter_signals() is None
            assert cache._task is not None and not cache._task.done()
        finally:
            await cache.stop()

    async def test_start_redis_mode_prewarms_from_redis(self):
        cache = SnapshotCache()
        redis = _FakeRedis(
            {KEY_SIGNALS_ALL: encode([_signal_payload(signal_id="warm")])}
        )
        await cache.start_redis_mode(redis)
        try:
            assert cache.is_warm
            assert [s.signal_id for s in cache.filter_signals()] == ["warm"]
        finally:
            await cache.stop()
