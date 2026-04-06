"""Scheduler — fires scheduled content tasks at configured UTC times.

All times are UTC. Uses asyncio — no external dependencies.

The scheduler runs as a background asyncio task. Every 60 seconds it checks:
1. Are any scheduled posts due?
2. Has it been > 3 hours since last post during active hours?
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple

from config import (
    CONTENT_ENGINE_ENABLED,
    SILENCE_BREAKER_ENABLED,
    SILENCE_BREAKER_HOURS,
)
from src import content_engine
from src.utils import get_logger

log = get_logger("scheduler")

# ---------------------------------------------------------------------------
# Schedule definition
# ---------------------------------------------------------------------------
# (hour_utc, minute_utc, task_name, channels)
SCHEDULED_TASKS: List[Tuple[int, int, str, List[str]]] = [
    (7,  0,  "morning_brief",  ["free"]),
    (8,  0,  "london_open",    ["free"]),
    (13, 30, "ny_open",        ["free"]),
    (21, 0,  "eod_wrap",       ["free"]),
    # Weekly — Monday only (weekday check inside task runner)
    (9,  0,  "weekly_card",    ["active", "free"]),
]

SILENCE_BREAKER_ACTIVE_START: int = 8   # UTC hour — start checking
SILENCE_BREAKER_ACTIVE_END: int = 22    # UTC hour — stop checking

# How long to wait between scheduler tick checks (seconds)
_TICK_INTERVAL: int = 60


class ContentScheduler:
    """Async scheduler for content engine tasks.

    Parameters
    ----------
    post_to_free:
        Coroutine-function that sends text to the free channel.
    post_to_active:
        Coroutine-function that sends text to the active channel.
    engine_context_fn:
        Zero-argument callable that returns the current engine context dict.
        Called fresh on each scheduled task so data is always up to date.
    """

    def __init__(
        self,
        post_to_free: Callable[[str], Coroutine],
        post_to_active: Callable[[str], Coroutine],
        engine_context_fn: Callable[[], Dict[str, Any]],
    ) -> None:
        self._post_free = post_to_free
        self._post_active = post_to_active
        self._engine_context_fn = engine_context_fn

        # Track which tasks have already been fired today (key = "HH:MM_task")
        self._fired_today: Dict[str, str] = {}  # key → date string "YYYY-MM-DD"
        # Timestamp of the last post sent to any channel (used by silence breaker)
        self.last_post_timestamp: float = time.monotonic()

    # ------------------------------------------------------------------
    # Public API — call from main.py
    # ------------------------------------------------------------------

    async def run(self) -> None:
        """Run the scheduler loop indefinitely (call with asyncio.create_task)."""
        if not CONTENT_ENGINE_ENABLED:
            log.info("Content engine disabled — scheduler not running")
            return

        log.info("Content scheduler started")
        while True:
            try:
                await self._tick()
            except Exception as exc:
                log.error("Scheduler tick error: %s", exc)
            await asyncio.sleep(_TICK_INTERVAL)

    def update_last_post(self) -> None:
        """Call this whenever a signal or content post is sent to reset the silence breaker."""
        self.last_post_timestamp = time.monotonic()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _tick(self) -> None:
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")

        # --- Scheduled tasks ---
        for hour, minute, task_name, channels in SCHEDULED_TASKS:
            fire_key = f"{hour:02d}:{minute:02d}_{task_name}"

            # Already fired today?
            if self._fired_today.get(fire_key) == date_str:
                continue

            # Is it time? (within the current minute)
            if now.hour == hour and now.minute == minute:
                # Weekly card only on Mondays (weekday 0 = Monday)
                if task_name == "weekly_card" and now.weekday() != 0:
                    self._fired_today[fire_key] = date_str
                    continue

                log.info("Scheduler firing task: %s", task_name)
                await self._run_task(task_name, channels)
                self._fired_today[fire_key] = date_str

        # --- Silence breaker ---
        if SILENCE_BREAKER_ENABLED:
            await self._check_silence_breaker(now)

    async def _check_silence_breaker(self, now: datetime) -> None:
        """Post a market watch message if the channel has been silent too long."""
        if now.hour < SILENCE_BREAKER_ACTIVE_START or now.hour >= SILENCE_BREAKER_ACTIVE_END:
            return

        elapsed_hours = (time.monotonic() - self.last_post_timestamp) / 3600.0
        if elapsed_hours >= SILENCE_BREAKER_HOURS:
            log.info(
                "Silence breaker triggered — %.1f hours since last post", elapsed_hours
            )
            await self._run_task("market_watch", ["free"])
            self.update_last_post()

    async def _run_task(self, task_name: str, channels: List[str]) -> None:
        """Execute a named content task and post to the specified channels."""
        try:
            engine_ctx = self._engine_context_fn()
            text = await self._generate(task_name, engine_ctx)
            if not text:
                log.warning("Scheduler: empty content for task %s — skipping post", task_name)
                return

            if "free" in channels:
                await self._post_free(text)
            if "active" in channels:
                await self._post_active(text)
            self.update_last_post()
        except Exception as exc:
            log.error("Scheduler task %s failed: %s", task_name, exc)

    async def _generate(self, task_name: str, engine_ctx: Dict[str, Any]) -> str:
        """Dispatch to content_engine based on task name."""
        generators = {
            "morning_brief": content_engine.generate_morning_brief,
            "london_open":   content_engine.generate_london_open,
            "ny_open":       content_engine.generate_ny_open,
            "eod_wrap":      content_engine.generate_eod_wrap,
            "market_watch":  content_engine.generate_market_watch,
            "weekly_card":   content_engine.generate_weekly_card,
        }
        gen_fn = generators.get(task_name)
        if gen_fn is None:
            log.warning("Scheduler: no generator for task %s", task_name)
            return ""
        return await gen_fn(engine_ctx)
