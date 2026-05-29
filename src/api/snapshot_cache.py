"""Background snapshot pre-computation cache.

Rebuilds ``build_signals`` every 5 s in a background asyncio task so
``/api/signals`` serves a pre-computed result in <1 ms instead of
iterating all engine state and serialising Pydantic models on every
request.  Cold cache (first 5 s after startup) falls back to the live
``build_signals`` call so no request ever fails.

Singleton ``snapshot_cache`` is imported by server.py; started in the
FastAPI lifespan handler so it shares the same event loop as the app.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, List, Optional

from src.utils import get_logger

log = get_logger("api.snapshot_cache")

_REFRESH_INTERVAL_S = 5


class SnapshotCache:
    def __init__(self) -> None:
        self._signals_all: Optional[List[Any]] = None  # List[SignalDetail]
        self._cached_at: float = 0.0
        self._engine: Any = None
        self._task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self, engine: Any) -> None:
        self._engine = engine
        if self._task is not None and not self._task.done():
            return
        # Pre-warm synchronously before first request can arrive.
        try:
            self._refresh_once()
        except Exception:
            log.exception("snapshot_cache: pre-warm failed — cache is cold")
        self._task = asyncio.create_task(
            self._refresh_loop(), name="snapshot_cache_refresh"
        )
        log.info("snapshot_cache: background refresh started (interval={}s)", _REFRESH_INTERVAL_S)

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        log.info("snapshot_cache: stopped")

    # ------------------------------------------------------------------
    # Background loop
    # ------------------------------------------------------------------

    async def _refresh_loop(self) -> None:
        while True:
            await asyncio.sleep(_REFRESH_INTERVAL_S)
            try:
                self._refresh_once()
            except Exception:
                log.exception("snapshot_cache: refresh failed — keeping stale cache")

    def _refresh_once(self) -> None:
        from .snapshot import build_signals

        items = build_signals(self._engine, status="all", limit=500)
        self._signals_all = items
        self._cached_at = time.monotonic()

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @property
    def is_warm(self) -> bool:
        return self._signals_all is not None and (time.monotonic() - self._cached_at) <= 30

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

        if status == "open":
            items: List[Any] = [s for s in cached if s.status == "ACTIVE"]
        elif status == "closed":
            items = [s for s in cached if s.status != "ACTIVE"]
        else:
            items = list(cached)

        if setup_class:
            target = setup_class.strip().upper()
            items = [s for s in items if s.setup_class.upper() == target]

        return items[:limit]

    @property
    def age_seconds(self) -> float:
        if self._cached_at == 0.0:
            return float("inf")
        return time.monotonic() - self._cached_at


snapshot_cache = SnapshotCache()
