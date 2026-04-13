"""Free-channel radar alert watch lifecycle service.

Implements tracked lifecycle for real ``radar_alert`` posts only.
``market_watch`` commentary-only posts are intentionally NOT tracked here.

Lifecycle outcomes:
- ``rolled_into_paid_signal``: a later paid Signal for the same symbol/direction
  appeared within the watch TTL.
- ``expired``: TTL elapsed with no matching paid signal.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Coroutine, Dict, List, Optional

from config import (
    RADAR_PER_SYMBOL_COOLDOWN_SECONDS,
    RADAR_WATCH_TTL_SECONDS,
)
from src.redis_client import RedisClient
from src.utils import get_logger, utcnow

log = get_logger("free_watch_service")

# Redis key for persisted open watches.
_REDIS_KEY_WATCHES = "free_watch_service:open_watches"

# How often the expiry-check loop runs (seconds).
_EXPIRY_CHECK_INTERVAL = 120


@dataclass
class FreeWatch:
    """Represents a tracked radar alert posted to the free channel."""

    watch_id: str
    symbol: str
    source_channel: str  # scanner channel that produced the candidate
    bias: str  # "LONG" | "SHORT" | "NEUTRAL"
    setup_name: str
    waiting_for: str
    confidence: int
    created_at: str  # ISO-8601 UTC
    expires_at: str  # ISO-8601 UTC
    status: str = "open"  # "open" | "rolled_into_paid_signal" | "expired"
    resolved_at: Optional[str] = None  # ISO-8601 UTC when terminal


def _watch_from_dict(data: dict) -> Optional[FreeWatch]:
    try:
        return FreeWatch(**data)
    except Exception as exc:
        log.warning("Failed to reconstruct FreeWatch: {}", exc)
        return None


def _watch_to_dict(w: FreeWatch) -> dict:
    return asdict(w)


def _dedupe_key(symbol: str, source_channel: str, bias: str, setup_name: str) -> str:
    """Dedupe key: one open watch per (symbol, channel, bias, setup)."""
    return f"{symbol}|{source_channel}|{bias}|{setup_name}"


class FreeWatchService:
    """Manages the lifecycle of free-channel radar alert watches.

    The service is deliberately narrow:
    - Only ``radar_alert`` posts create a watch.
    - ``market_watch`` commentary posts must NOT call :meth:`create_watch`.
    - Watch resolution requires an exact-or-compatible match on symbol + bias.
    """

    def __init__(
        self,
        send_free: Callable[[str], Coroutine[Any, Any, bool]],
        redis_client: Optional[RedisClient] = None,
    ) -> None:
        self._send_free = send_free
        self._redis = redis_client
        # In-memory store: dedupe_key → FreeWatch
        self._open_watches: Dict[str, FreeWatch] = {}
        self._running = False
        self._task: Optional[asyncio.Task[None]] = None
        # Per-symbol cooldown tracking: symbol → last watch created_at (ISO)
        self._symbol_cooldown: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Lifecycle: start / stop / restore
    # ------------------------------------------------------------------

    async def restore(self) -> None:
        """Reload open watches from Redis after a process restart."""
        if self._redis is None or not self._redis.available:
            return
        try:
            client = self._redis.client
            if client is None:
                return
            raw = await client.get(_REDIS_KEY_WATCHES)
            if raw:
                data: Dict[str, Any] = json.loads(raw)
                for key, wdict in data.items():
                    w = _watch_from_dict(wdict)
                    if w is not None and w.status == "open":
                        self._open_watches[key] = w
                log.info(
                    "Restored {} open radar watch(es) from Redis",
                    len(self._open_watches),
                )
        except Exception as exc:
            log.warning("Failed to restore watches from Redis: {}", exc)

    async def start(self) -> None:
        """Start the background expiry-check loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._expiry_loop())

    async def stop(self) -> None:
        """Gracefully stop the expiry-check loop."""
        self._running = False
        if self._task is not None and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    # ------------------------------------------------------------------
    # Watch creation
    # ------------------------------------------------------------------

    async def create_watch(
        self,
        symbol: str,
        source_channel: str,
        bias: str,
        setup_name: str,
        waiting_for: str,
        confidence: int,
    ) -> Optional[FreeWatch]:
        """Create (or silently skip) a tracked radar watch.

        Returns the new :class:`FreeWatch` if created, or ``None`` if
        deduplicated (open watch already exists for the same key) or on error.
        """
        key = _dedupe_key(symbol, source_channel, bias, setup_name)

        # Dedupe: one open watch per (symbol, channel, bias, setup)
        existing = self._open_watches.get(key)
        if existing is not None and existing.status == "open":
            log.debug(
                "Radar watch already open for {} — skipping duplicate",
                key,
            )
            return None

        # Per-symbol cooldown guard (re-use RADAR_PER_SYMBOL_COOLDOWN_SECONDS)
        last_ts_str = self._symbol_cooldown.get(symbol)
        if last_ts_str is not None:
            try:
                last_ts = datetime.fromisoformat(last_ts_str)
                elapsed = (utcnow() - last_ts).total_seconds()
                if elapsed < RADAR_PER_SYMBOL_COOLDOWN_SECONDS:
                    log.debug(
                        "Symbol cooldown active for {} — {:.0f}s remaining",
                        symbol,
                        RADAR_PER_SYMBOL_COOLDOWN_SECONDS - elapsed,
                    )
                    return None
            except Exception:
                pass

        now = utcnow()
        expires_at = now + timedelta(seconds=RADAR_WATCH_TTL_SECONDS)
        watch = FreeWatch(
            watch_id=str(uuid.uuid4()),
            symbol=symbol,
            source_channel=source_channel,
            bias=bias,
            setup_name=setup_name,
            waiting_for=waiting_for,
            confidence=confidence,
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
        )
        self._open_watches[key] = watch
        self._symbol_cooldown[symbol] = now.isoformat()
        await self._persist()
        log.info(
            "Radar watch created: {} {} {} via {} (expires {})",
            symbol,
            bias,
            setup_name,
            source_channel,
            expires_at.strftime("%H:%M UTC"),
        )
        return watch

    # ------------------------------------------------------------------
    # Resolution: paid signal match
    # ------------------------------------------------------------------

    async def on_paid_signal(
        self,
        symbol: str,
        bias: str,
    ) -> None:
        """Called when a real paid Signal is posted.

        Resolves any open radar watch for the same symbol with a compatible
        bias to ``rolled_into_paid_signal`` and posts a free-channel follow-up
        (no premium entry/TP/SL details).
        """
        resolved: List[str] = []
        for key, watch in list(self._open_watches.items()):
            if watch.status != "open":
                continue
            if watch.symbol != symbol:
                continue
            # Bias compatibility: exact match OR watch is NEUTRAL
            if watch.bias not in (bias, "NEUTRAL"):
                continue
            await self._resolve(key, watch, "rolled_into_paid_signal")
            resolved.append(key)

        if resolved:
            await self._persist()

    # ------------------------------------------------------------------
    # Expiry loop
    # ------------------------------------------------------------------

    async def _expiry_loop(self) -> None:
        """Background loop that checks for and resolves expired watches."""
        while self._running:
            try:
                await self._check_expiry()
            except Exception as exc:
                log.warning("Expiry loop error: {}", exc)
            await asyncio.sleep(_EXPIRY_CHECK_INTERVAL)

    async def _check_expiry(self) -> None:
        now = utcnow()
        expired_keys: List[str] = []
        for key, watch in list(self._open_watches.items()):
            if watch.status != "open":
                continue
            try:
                expires_at = datetime.fromisoformat(watch.expires_at)
            except Exception:
                continue
            if now >= expires_at:
                expired_keys.append(key)

        for key in expired_keys:
            watch = self._open_watches.get(key)
            if watch is not None:
                await self._resolve(key, watch, "expired")

        if expired_keys:
            await self._persist()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _resolve(self, key: str, watch: FreeWatch, outcome: str) -> None:
        """Mark a watch as terminal and post a free-channel follow-up."""
        watch.status = outcome
        watch.resolved_at = utcnow().isoformat()

        # Remove from open watches
        self._open_watches.pop(key, None)

        # Build and post the free-channel follow-up message
        try:
            from src.formatter import (
                format_radar_watch_expired,
                format_radar_watch_resolved_paid,
            )

            if outcome == "rolled_into_paid_signal":
                text = format_radar_watch_resolved_paid(
                    symbol=watch.symbol,
                    bias=watch.bias,
                    setup_name=watch.setup_name,
                )
            else:
                text = format_radar_watch_expired(
                    symbol=watch.symbol,
                    bias=watch.bias,
                    setup_name=watch.setup_name,
                )

            if text:
                await self._send_free(text)
                log.info(
                    "Radar watch {} → {} for {} {}",
                    watch.watch_id,
                    outcome,
                    watch.symbol,
                    watch.bias,
                )
        except Exception as exc:
            log.warning("Failed to post radar watch follow-up ({}): {}", outcome, exc)

    async def _persist(self) -> None:
        """Persist all open (non-terminal) watches to Redis."""
        if self._redis is None or not self._redis.available:
            return
        try:
            client = self._redis.client
            if client is None:
                return
            payload = {
                key: _watch_to_dict(w)
                for key, w in self._open_watches.items()
                if w.status == "open"
            }
            await client.set(_REDIS_KEY_WATCHES, json.dumps(payload))
        except Exception as exc:
            log.warning("Failed to persist radar watches to Redis: {}", exc)

    # ------------------------------------------------------------------
    # Read-only helpers (for testing)
    # ------------------------------------------------------------------

    def get_open_watches(self) -> Dict[str, FreeWatch]:
        """Return a shallow copy of the in-memory open watch index."""
        return {k: v for k, v in self._open_watches.items() if v.status == "open"}

    def watch_count(self) -> int:
        return len(self.get_open_watches())
