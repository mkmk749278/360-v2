"""Background snapshot pre-computation cache.

Rebuilds ``build_signals`` every 5 s, ``build_activity`` every 30 s, and
``build_agents`` every 60 s in background asyncio tasks so the matching
endpoints serve pre-computed results in <1 ms instead of iterating all
engine state and serialising Pydantic models on every request.  Cold
cache (first interval after startup) falls back to the live builder call
so no request ever fails.

All three ``_refresh_*_once`` helpers are synchronous functions dispatched
via a dedicated ``ThreadPoolExecutor`` (``self._executor``) so the heavy
Pydantic-model construction work never competes with auth/DB calls for the
default asyncio thread pool.

Singleton ``snapshot_cache`` is imported by server.py; started in the
FastAPI lifespan handler so it shares the same event loop as the app.
"""

from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor as _TPE
from typing import Any, List, Optional

from src.utils import get_logger

log = get_logger("api.snapshot_cache")

_SIGNALS_INTERVAL_S = 5
_ACTIVITY_INTERVAL_S = 30
_AGENTS_INTERVAL_S = 60


class SnapshotCache:
    def __init__(self) -> None:
        self._signals_all: Optional[List[Any]] = None  # List[SignalDetail]
        self._cached_at: float = 0.0
        self._activity_all: Optional[List[Any]] = None  # List[ActivityEvent]
        self._activity_cached_at: float = 0.0
        self._agents_all: Optional[List[Any]] = None  # List[AgentStat]
        self._agents_cached_at: float = 0.0
        self._engine: Any = None
        self._task: Optional[asyncio.Task] = None
        self._activity_task: Optional[asyncio.Task] = None
        self._agents_task: Optional[asyncio.Task] = None
        # Dedicated pool: heavy Pydantic model builds (up to 500 signals every
        # 5 s) must not compete with auth/DB calls in the default asyncio
        # executor.  2 workers is enough — the three refresh tasks are
        # staggered in time and never need more than one thread simultaneously.
        self._executor = _TPE(max_workers=2, thread_name_prefix="snapshot-cache")
        # Redis client — set in start_redis_mode(); when set, all three
        # background loops read from Redis instead of from the engine object.
        self._redis: Any = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self, engine: Any) -> None:
        self._engine = engine
        self._redis = None
        loop = asyncio.get_running_loop()
        # Signals task
        if self._task is None or self._task.done():
            # Pre-warm off the event loop so the first 500-model build
            # doesn't stall the loop during startup.
            try:
                await loop.run_in_executor(self._executor, self._refresh_signals_once)
            except Exception:
                log.exception("snapshot_cache: signals pre-warm failed — cache is cold")
            self._task = asyncio.create_task(
                self._signals_loop(), name="snapshot_cache_signals"
            )
        # Activity task — pre-warm skipped at start; first request falls back
        # to live build_activity (cheap enough to accept once).
        if self._activity_task is None or self._activity_task.done():
            self._activity_task = asyncio.create_task(
                self._activity_loop(), name="snapshot_cache_activity"
            )
        # Agents task — same cold-cache-on-first-request policy.
        if self._agents_task is None or self._agents_task.done():
            self._agents_task = asyncio.create_task(
                self._agents_loop(), name="snapshot_cache_agents"
            )
        log.info(
            "snapshot_cache: background refresh started "
            "(signals={}s activity={}s agents={}s)",
            _SIGNALS_INTERVAL_S,
            _ACTIVITY_INTERVAL_S,
            _AGENTS_INTERVAL_S,
        )

    async def start_redis_mode(self, redis_client: Any) -> None:
        """Start the cache in Redis-backed mode (isolated API container).

        Instead of building Pydantic models from a live engine, the background
        loops read pre-serialised JSON from the Redis keys written by
        ``SnapshotWriter`` in the engine container.  The fallback path in
        route handlers (``build_signals(engine, ...)`` when cache is cold)
        still works because ``build_signals`` on a ``RedisEngineFacade`` reads
        from ``router.active_signals`` which itself is backed by Redis state.
        """
        self._redis = redis_client
        self._engine = None
        if self._task is None or self._task.done():
            # Pre-warm from Redis so the first request is served from cache.
            try:
                await self._refresh_signals_from_redis()
            except Exception:
                log.exception("snapshot_cache: Redis signals pre-warm failed — cache is cold")
            self._task = asyncio.create_task(
                self._signals_loop_redis(), name="snapshot_cache_signals_redis"
            )
        if self._activity_task is None or self._activity_task.done():
            self._activity_task = asyncio.create_task(
                self._activity_loop_redis(), name="snapshot_cache_activity_redis"
            )
        if self._agents_task is None or self._agents_task.done():
            self._agents_task = asyncio.create_task(
                self._agents_loop_redis(), name="snapshot_cache_agents_redis"
            )
        log.info(
            "snapshot_cache: Redis-backed refresh started "
            "(signals={}s activity={}s agents={}s)",
            _SIGNALS_INTERVAL_S,
            _ACTIVITY_INTERVAL_S,
            _AGENTS_INTERVAL_S,
        )

    async def stop(self) -> None:
        for task in (self._task, self._activity_task, self._agents_task):
            if task is not None:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._task = None
        self._activity_task = None
        self._agents_task = None
        self._executor.shutdown(wait=False)
        log.info("snapshot_cache: stopped")

    # ------------------------------------------------------------------
    # Background loops — engine-backed (single-process mode)
    # ------------------------------------------------------------------

    async def _signals_loop(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            await asyncio.sleep(_SIGNALS_INTERVAL_S)
            try:
                await loop.run_in_executor(self._executor, self._refresh_signals_once)
            except Exception:
                log.exception("snapshot_cache: signals refresh failed — keeping stale cache")

    async def _activity_loop(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            await asyncio.sleep(_ACTIVITY_INTERVAL_S)
            try:
                await loop.run_in_executor(self._executor, self._refresh_activity_once)
            except Exception:
                log.exception("snapshot_cache: activity refresh failed — keeping stale cache")

    async def _agents_loop(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            await asyncio.sleep(_AGENTS_INTERVAL_S)
            try:
                await loop.run_in_executor(self._executor, self._refresh_agents_once)
            except Exception:
                log.exception("snapshot_cache: agents refresh failed — keeping stale cache")

    # ------------------------------------------------------------------
    # Sync refreshers (engine-backed) — dispatched via self._executor so
    # Pydantic model construction runs on the dedicated pool.
    # ------------------------------------------------------------------

    def _refresh_signals_once(self) -> None:
        from .snapshot import build_signals

        items = build_signals(self._engine, status="all", limit=500)
        self._signals_all = items
        self._cached_at = time.monotonic()

    def _refresh_activity_once(self) -> None:
        from .snapshot import build_activity

        # Cache the full 500-item set; filter_activity slices on query.
        items = build_activity(self._engine, limit=500)
        self._activity_all = items
        self._activity_cached_at = time.monotonic()

    def _refresh_agents_once(self) -> None:
        from .snapshot import build_agents

        items = build_agents(self._engine)
        self._agents_all = items
        self._agents_cached_at = time.monotonic()

    # ------------------------------------------------------------------
    # Background loops — Redis-backed (isolated API container mode)
    # ------------------------------------------------------------------

    async def _signals_loop_redis(self) -> None:
        while True:
            await asyncio.sleep(_SIGNALS_INTERVAL_S)
            try:
                await self._refresh_signals_from_redis()
            except Exception:
                log.exception("snapshot_cache: Redis signals refresh failed — keeping stale cache")

    async def _activity_loop_redis(self) -> None:
        while True:
            await asyncio.sleep(_ACTIVITY_INTERVAL_S)
            try:
                await self._refresh_activity_from_redis()
            except Exception:
                log.exception("snapshot_cache: Redis activity refresh failed — keeping stale cache")

    async def _agents_loop_redis(self) -> None:
        while True:
            await asyncio.sleep(_AGENTS_INTERVAL_S)
            try:
                await self._refresh_agents_from_redis()
            except Exception:
                log.exception("snapshot_cache: Redis agents refresh failed — keeping stale cache")

    async def _refresh_signals_from_redis(self) -> None:
        from .snapshot_store import KEY_SIGNALS_ALL, decode
        from .schemas import SignalDetail

        if not (self._redis and self._redis.available):
            return
        raw = await self._redis.client.get(KEY_SIGNALS_ALL)
        data = decode(raw)
        if data is None:
            return
        parsed: list = []
        for d in data:
            try:
                parsed.append(SignalDetail(**d))
            except Exception:
                log.warning(
                    "snapshot_cache: skipping malformed signal from Redis sid={}",
                    d.get("signal_id", "?"),
                )
        self._signals_all = parsed
        self._cached_at = time.monotonic()

    async def _refresh_activity_from_redis(self) -> None:
        from .snapshot_store import KEY_ACTIVITY_ALL, decode
        from .schemas import ActivityEvent

        if not (self._redis and self._redis.available):
            return
        raw = await self._redis.client.get(KEY_ACTIVITY_ALL)
        data = decode(raw)
        if data is None:
            return
        self._activity_all = [ActivityEvent(**d) for d in data]
        self._activity_cached_at = time.monotonic()

    async def _refresh_agents_from_redis(self) -> None:
        from .snapshot_store import KEY_AGENTS_ALL, decode
        from .schemas import AgentStat

        if not (self._redis and self._redis.available):
            return
        raw = await self._redis.client.get(KEY_AGENTS_ALL)
        data = decode(raw)
        if data is None:
            return
        self._agents_all = [AgentStat(**d) for d in data]
        self._agents_cached_at = time.monotonic()

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def _is_warm(self, cached_at: float, max_age: float = 30.0) -> bool:
        return cached_at != 0.0 and (time.monotonic() - cached_at) <= max_age

    @property
    def is_warm(self) -> bool:
        return self._is_warm(self._cached_at)

    def filter_signals(
        self,
        *,
        status: str = "all",
        limit: int = 50,
        setup_class: Optional[str] = None,
    ) -> Optional[List[Any]]:
        """Return filtered signals from cache.

        Returns ``None`` when the cache is cold or stale (> 30 s old) so
        callers can fall back to the live ``build_signals`` path.
        """
        if not self.is_warm:
            return None
        cached = self._signals_all
        assert cached is not None  # guaranteed by is_warm check

        # ``is_open`` is authoritative (2026-07-10): a runner mover rides open
        # at status TP1_HIT/TP2_HIT while a BE-then-TP1 non-mover CLOSES at
        # TP1_HIT — the status string alone can't split the views.  Old
        # snapshots (Redis mode across a deploy) may lack the field; fall
        # back to the legacy status heuristic for those items only.
        def _is_open(s: Any) -> bool:
            fields_set = getattr(s, "model_fields_set", None)
            if fields_set is not None and "is_open" not in fields_set:
                # Pydantic item whose payload predates the field (stale Redis
                # snapshot across the deploy) — legacy heuristic.
                return s.status == "ACTIVE"
            v = getattr(s, "is_open", None)
            if v is None:
                return s.status == "ACTIVE"
            return bool(v)

        if status == "open":
            items: List[Any] = [s for s in cached if _is_open(s)]
        elif status == "closed":
            items = [s for s in cached if not _is_open(s)]
        else:
            items = list(cached)

        if setup_class:
            target = setup_class.strip().upper()
            items = [s for s in items if s.setup_class.upper() == target]

        return items[:limit]

    def filter_activity(
        self,
        *,
        limit: int = 50,
        setup_class: Optional[str] = None,
    ) -> Optional[List[Any]]:
        """Return filtered activity events from cache (max-age 60 s).

        Returns ``None`` when cold/stale so callers fall back to the live
        ``build_activity`` path.

        A ``setup_class`` query also returns ``None``: ``ActivityEvent``
        carries no setup_class field, so the cached (unfiltered) event set
        cannot answer a per-evaluator filter — before 2026-07-17 this path
        raised ``AttributeError`` into the route's catch-all and the app got
        an EMPTY activity list whenever the cache was warm.  Falling back to
        ``build_activity`` filters correctly at the signal level; the query
        is a rare user-driven filter, not a hot path, so the extra live
        build is acceptable.
        """
        if setup_class:
            return None
        if not self._is_warm(self._activity_cached_at, max_age=60.0):
            return None
        cached = self._activity_all
        assert cached is not None

        return list(cached)[:limit]

    def get_agents(self) -> Optional[List[Any]]:
        """Return cached agents list (max-age 90 s).

        Returns ``None`` when cold/stale so callers fall back to the live
        ``build_agents`` path.
        """
        if not self._is_warm(self._agents_cached_at, max_age=90.0):
            return None
        return self._agents_all

    @property
    def age_seconds(self) -> float:
        if self._cached_at == 0.0:
            return float("inf")
        return time.monotonic() - self._cached_at


snapshot_cache = SnapshotCache()
