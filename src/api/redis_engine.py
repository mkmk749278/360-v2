"""Redis-backed engine facade for the isolated API container.

``RedisEngineFacade`` presents the same attribute interface that the
snapshot builder functions (``build_pulse``, ``build_auto_mode``,
``build_positions``) access on a live ``CryptoSignalEngine``.  All state
is read from the ``snapshot:engine_state`` Redis key written by
``SnapshotWriter`` every ~15 s.

Only the attributes that the snapshot functions actually read are
implemented — anything else returns a safe default rather than raising.
``set_auto_execution_mode`` queues a Redis command for the engine container
to pick up on its next ``SnapshotWriter._apply_pending_mode_cmd`` check.
"""
from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, Optional

from src.utils import get_logger

from . import snapshot_store as _store

log = get_logger("api.redis_engine")


# ── Lightweight mock objects ────────────────────────────────────────────────


class _MockSignal:
    """Minimal signal stub used in per-user window-filter reads."""
    __slots__ = ("signal_id", "dispatch_timestamp", "timestamp")

    def __init__(self, signal_id: str, dispatch_ts: Optional[str]) -> None:
        self.signal_id = signal_id
        # Parse the ISO-8601 string back to datetime for _minutes_since / window filters.
        dt: Optional[datetime] = None
        if dispatch_ts:
            try:
                dt = datetime.fromisoformat(dispatch_ts.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass
        self.dispatch_timestamp = dt
        self.timestamp = dt


class _MockPosition:
    """Minimal broker-position stub."""
    __slots__ = ("quantity", "closed_quantity")

    def __init__(self, quantity: float, closed_quantity: float) -> None:
        self.quantity = quantity
        self.closed_quantity = closed_quantity


class _MockRouter:
    """Router stub — exposes only ``active_signals``."""

    def __init__(self, active_signals: Dict[str, _MockSignal]) -> None:
        self.active_signals = active_signals


class _MockRiskManager:
    """RiskManager stub — surfaces the pre-computed scalars."""

    def __init__(self, rm_state: dict) -> None:
        self.open_position_count    = int(rm_state.get("open_position_count", 0) or 0)
        self.daily_realised_pnl_usd = float(rm_state.get("daily_realised_pnl_usd", 0.0) or 0.0)
        self.current_equity_usd     = float(rm_state.get("current_equity_usd", 0.0) or 0.0)
        self.daily_kill_tripped     = bool(rm_state.get("daily_kill_tripped", False))


class _MockOrderManager:
    """OrderManager stub — exposes ``_positions`` and ``current_equity_usd``."""

    def __init__(self, broker_positions: dict, paper_equity: float) -> None:
        self._positions: Dict[str, _MockPosition] = {
            sid: _MockPosition(
                float(p.get("quantity", 0.0) or 0.0),
                float(p.get("closed_quantity", 0.0) or 0.0),
            )
            for sid, p in broker_positions.items()
        }
        self.current_equity_usd = paper_equity


class _MockRegimeResult:
    def __init__(self, regime_str: str) -> None:
        self.regime = type("_R", (), {"value": regime_str})()


class _MockRegimeDetector:
    def __init__(self, regime_str: str) -> None:
        self._regime_str = regime_str

    def get_regime(self, symbol: str) -> _MockRegimeResult:
        return _MockRegimeResult(self._regime_str)


class _MockPairMgr:
    def __init__(self, pair_count: int) -> None:
        self.symbols = range(pair_count)


# ── Facade ──────────────────────────────────────────────────────────────────


class RedisEngineFacade:
    """Engine facade backed by Redis snapshots.

    Call ``await facade.refresh_state()`` before serving a request so the
    facade's properties reflect the latest engine state.  The ``start()``
    helper runs a background refresh loop; for direct use in tests, call
    ``refresh_state()`` once manually.
    """

    def __init__(self, redis_client: Any) -> None:
        self._redis = redis_client
        self._state: dict = {}
        self._positions_diag: Optional[dict] = None
        self._alerts: Optional[list] = None
        self._refreshed_at: float = 0.0

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Background loop: refresh state every 10 s so facades are warm."""
        while True:
            await self.refresh_state()
            await asyncio.sleep(10)

    async def refresh_state(self) -> None:
        """Pull the latest engine state from Redis."""
        if not self._redis.available:
            return
        try:
            raw = await self._redis.client.get(_store.KEY_ENGINE_STATE)
            state = _store.decode(raw)
            if state is not None:
                self._state = state
                self._refreshed_at = time.monotonic()
            diag_raw = await self._redis.client.get(_store.KEY_POSITIONS_DIAG)
            self._positions_diag = _store.decode(diag_raw)
            alerts_raw = await self._redis.client.get(_store.KEY_ALERTS)
            self._alerts = _store.decode(alerts_raw)
        except Exception:
            log.exception("redis_engine: failed to refresh state from Redis")

    def published_positions_diag(self) -> Optional[dict]:
        """Return the engine-computed positions-diag X-ray published to Redis,
        or ``None`` if the engine hasn't written one (key absent / expired).

        Present only on the facade — the single-process engine builds the diag
        live, so the ``/internal/diag/positions`` handler only consults this in
        isolated mode and falls back to a live build otherwise.
        """
        return self._positions_diag

    def published_alerts(self) -> Optional[list]:
        """Return the market-alerts feed the engine published to Redis, or
        ``None`` when absent (engine down / key expired).  Present only on
        the facade — the single-process engine serves alerts straight from
        ``engine._alert_service``."""
        return self._alerts

    def published_pairs(self) -> Optional[dict]:
        """Return the pairs X-ray (regular + promoting) the engine published to
        ``engine_state``, or ``None`` if absent. ``build_pairs`` uses this in
        isolated mode so the promoting list reflects the engine container's live
        in-memory scanner state rather than this facade's empty mock pair_mgr.
        """
        if isinstance(self._state, dict):
            return self._state.get("pairs")
        return None

    @property
    def state_age_seconds(self) -> float:
        if self._refreshed_at == 0.0:
            return float("inf")
        return time.monotonic() - self._refreshed_at

    # ------------------------------------------------------------------
    # Engine-compatible properties
    # ------------------------------------------------------------------

    @property
    def _current_auto_mode(self) -> str:
        return self._state.get("current_auto_mode", "off")

    @property
    def _risk_manager(self) -> Optional[_MockRiskManager]:
        rm_state = self._state.get("risk_manager")
        return _MockRiskManager(rm_state) if rm_state else None

    @property
    def _order_manager(self) -> _MockOrderManager:
        return _MockOrderManager(
            self._state.get("broker_positions", {}),
            float(self._state.get("paper_equity_usd", 0.0) or 0.0),
        )

    @property
    def router(self) -> _MockRouter:
        dispatch_map: dict = self._state.get("active_signal_dispatch", {})
        active_signals = {
            sid: _MockSignal(sid, dispatch_ts)
            for sid, dispatch_ts in dispatch_map.items()
        }
        return _MockRouter(active_signals)

    @property
    def _regime_detector(self) -> _MockRegimeDetector:
        return _MockRegimeDetector(self._state.get("regime_btcusdt", "RANGING"))

    @property
    def _boot_time(self) -> float:
        # uptime is pre-computed in engine_state; we expose a synthetic boot time.
        uptime = float(self._state.get("uptime_seconds", 0.0) or 0.0)
        return time.monotonic() - uptime

    @property
    def pair_mgr(self) -> _MockPairMgr:
        return _MockPairMgr(int(self._state.get("scanning_pairs_count", 0) or 0))

    @property
    def _signal_history(self) -> list:
        # History is not needed for per-user pulse/auto-mode/positions reads;
        # signals_today_count is pre-computed in engine_state.
        return []

    @property
    def _channels(self) -> list:
        # Not used in isolated API mode — agents are read from snapshot:agents_all.
        return []

    @property
    def data_store(self) -> None:
        # Not available in isolated mode — tickers are read from snapshot:tickers.
        return None

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def get_background_task_census(self) -> list:
        """Live engine task names, read from the snapshot the engine published.

        In isolated mode the API process cannot see the engine container's
        asyncio tasks, so the engine's SnapshotWriter writes them into
        ``engine_state`` and we surface them here. Returns the last-known
        census; if the engine has stopped writing, the snapshot key expires
        (TTL 60s) and this serves the stale list until then — full engine
        death is covered separately by snapshot-freshness monitoring.
        """
        tasks = self._state.get("background_tasks")
        return list(tasks) if isinstance(tasks, list) else []

    def get_auto_execution_status(self) -> dict:
        return dict(self._state.get("auto_execution_status", {
            "mode": self._current_auto_mode,
            "open_positions": 0,
            "daily_pnl_usd": 0.0,
            "daily_loss_pct": 0.0,
            "daily_kill_tripped": False,
            "manual_paused": False,
            "current_equity_usd": 0.0,
        }))

    def set_auto_execution_mode(self, new_mode: str):
        """Queue a mode-change command to Redis.

        The ``SnapshotWriter`` running in the engine container picks it up on
        the next ``_apply_pending_mode_cmd`` check (≤ ``_CYCLE_INTERVAL_S`` s).
        Returns ``(True, queued_message)`` so the route handler path is identical
        to the direct-engine path.
        """
        new_mode = (new_mode or "").strip().lower()
        if new_mode not in {"off", "paper", "live"}:
            return False, f"invalid mode {new_mode!r} — must be off / paper / live"
        current = self._current_auto_mode
        if new_mode == current:
            return False, f"already in {new_mode.upper()} mode — nothing to do"

        # Write command to Redis asynchronously — we're inside an async route handler
        # so asyncio.get_running_loop() is available.
        loop = asyncio.get_running_loop()

        async def _write_cmd() -> None:
            if self._redis.available:
                await self._redis.client.set(
                    _store.KEY_CMD_SET_MODE, new_mode, ex=_store.TTL_CMD
                )
            else:
                log.warning("redis_engine.set_auto_execution_mode: Redis unavailable — command lost")

        loop.create_task(_write_cmd())
        return True, (
            f"auto-execution mode change queued: "
            f"{current.upper()} → {new_mode.upper()} "
            f"(takes effect on next engine scan cycle)"
        )

    @property
    def auto_execution_mode(self) -> str:
        return self._current_auto_mode

    def full_signal_reset(self) -> dict:
        """Direct-call stub — NOT used in isolated mode.

        In isolated mode the API container calls ``request_full_signal_reset()``
        (which queues the Redis command), not this method. The stub exists only so
        single-process paths that call ``engine.full_signal_reset()`` work on both
        engine types without isinstance checks.
        """
        return {
            "cleared_active_signals": 0,
            "cleared_history": 0,
            "cleared_perf_stats": 0,
            "cleared_invalidation_records": 0,
            "note": "facade stub — command queued via request_full_signal_reset() in isolated mode",
        }

    def request_full_signal_reset(self) -> tuple:
        """Queue a full-signal-reset command to Redis for the engine container.

        Returns (True, message) always — the engine container processes it
        asynchronously on the next SnapshotWriter cycle (≤15s). The API endpoint
        should treat 'queued' as success and return a 202-style response.
        """
        loop = asyncio.get_running_loop()

        async def _write_cmd() -> None:
            if self._redis.available:
                await self._redis.client.set(
                    _store.KEY_CMD_RESET_SIGNALS, "1", ex=_store.TTL_CMD_RESET
                )
            else:
                log.warning("redis_engine.request_full_signal_reset: Redis unavailable — command lost")

        loop.create_task(_write_cmd())
        return True, "full signal reset queued (takes effect on next engine cycle, ≤15s)"
