"""Engine-side snapshot writer.

``SnapshotWriter`` runs as a long-running asyncio task (launched by
``bootstrap.launch_runtime_tasks`` when ``API_PROCESS_ISOLATED=true``).
After every scan cycle it serialises the engine's live state to Redis so the
isolated ``api`` container can serve requests without touching engine memory.

Write strategy
──────────────
* Signals, tickers, engine-state: every ``_CYCLE_INTERVAL_S`` seconds (≈ one scan cycle).
* Activity: every ``_ACTIVITY_INTERVAL_S`` seconds (event list changes slowly).
* Agents: every ``_AGENTS_INTERVAL_S`` seconds (telemetry resets are long-period).
* Pending mode command (``snapshot:cmd:set_mode``): checked on every cycle;
  applied via ``engine.set_auto_execution_mode`` and deleted immediately.

All writes are best-effort: failures are logged but never raise so a Redis hiccup
cannot stall the scan cycle.
"""
from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor as _TPE
from datetime import datetime, timezone
from typing import Any

from src.utils import get_logger

from . import snapshot_store as _store

log = get_logger("api.snapshot_writer")

_CYCLE_INTERVAL_S   = 15   # ≈ one scan cycle
_ACTIVITY_INTERVAL_S = 30
_AGENTS_INTERVAL_S   = 60


class SnapshotWriter:
    """Serialises engine state to Redis every scan cycle.

    Parameters
    ----------
    engine:
        The live ``CryptoSignalEngine`` instance.
    redis_client:
        The engine's ``RedisClient`` wrapper.  Writes are skipped silently when
        ``redis_client.available`` is false so Redis downtime never crashes boot.
    """

    def __init__(self, engine: Any, redis_client: Any) -> None:
        self._engine = engine
        self._redis  = redis_client
        self._last_activity: float = 0.0
        self._last_agents: float   = 0.0
        # Dedicated 1-thread pool for Pydantic serialisation — keeps heavy
        # model-construction off the engine's main asyncio event loop.
        self._executor = _TPE(max_workers=1, thread_name_prefix="snapshot-writer")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Long-running task: write snapshots on every scan cycle."""
        log.info(
            "SnapshotWriter started — writing to Redis every {}s",
            _CYCLE_INTERVAL_S,
        )
        try:
            while True:
                await asyncio.sleep(_CYCLE_INTERVAL_S)
                await self._write_cycle()
        finally:
            self._executor.shutdown(wait=False)

    # ------------------------------------------------------------------
    # Per-cycle orchestrator
    # ------------------------------------------------------------------

    async def _write_cycle(self) -> None:
        now = time.monotonic()
        await self._write_signals()
        await self._write_tickers()
        await self._write_engine_state()
        await self._write_positions_diag()
        await self._write_data_intake()
        await self._write_router_delivery()
        if now - self._last_activity >= _ACTIVITY_INTERVAL_S:
            await self._write_activity()
            await self._write_alerts()
            self._last_activity = now
        if now - self._last_agents >= _AGENTS_INTERVAL_S:
            await self._write_agents()
            self._last_agents = now
        # Check for a pending mode-change command from the API container.
        await self._apply_pending_mode_cmd()
        # Check for a pending full-signal-reset command from the API container.
        await self._apply_pending_reset_cmd()
        await self._apply_pending_sar_clear_cmd()

    # ------------------------------------------------------------------
    # Individual writers
    # ------------------------------------------------------------------

    async def _write_signals(self) -> None:
        try:
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(self._executor, self._build_signals)
            await self._set(_store.KEY_SIGNALS_ALL, data, _store.TTL_SIGNALS)
        except Exception:
            log.exception("snapshot_writer: failed to write signals")

    def _build_signals(self) -> list:
        from src.api.snapshot import build_signals
        return [i.model_dump(mode="json") for i in
                build_signals(self._engine, status="all", limit=500)]

    async def _write_positions_diag(self) -> None:
        """Publish the position-state X-ray computed engine-side.

        ``build_positions_diag`` needs live ``router.active_signals`` AND the
        ``data_store`` candle wicks to populate SL-breach / candle-age columns —
        state the API container's RedisEngineFacade cannot see in isolated mode.
        Computing it here (on the real engine) and publishing the rendered rows
        keeps the dashboard X-ray fully populated under isolation.
        """
        try:
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(self._executor, self._build_positions_diag)
            await self._set(_store.KEY_POSITIONS_DIAG, data, _store.TTL_POSITIONS_DIAG)
        except Exception:
            log.exception("snapshot_writer: failed to write positions_diag")

    def _build_positions_diag(self) -> dict:
        from src.api.snapshot import build_positions_diag
        return build_positions_diag(self._engine).model_dump(mode="json")

    async def _write_data_intake(self) -> None:
        """Publish the data-intake X-ray computed engine-side.

        Same reason as the positions diag: it reads WS connection state, the
        candle store, the order-flow store and the rate limiter — none of which
        the API container's RedisEngineFacade can see in isolated mode. Built
        here on the real engine, rendered there.
        """
        try:
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(self._executor, self._build_data_intake)
            await self._set(_store.KEY_DATA_INTAKE, data, _store.TTL_DATA_INTAKE)
        except Exception:
            log.exception("snapshot_writer: failed to write data_intake")

    def _build_data_intake(self) -> dict:
        from src.data_intake import build_data_intake
        return build_data_intake(self._engine)

    async def _write_router_delivery(self) -> None:
        """Publish the router's drop census — the last hop before a subscriber.

        `SignalRouter` lives in the ENGINE container and its counters are plain
        in-process ints, so the API container's facade cannot see them at all in
        isolated mode. Same reason as the positions diag: built here on the real
        object, rendered there.

        This exists because `delivery_stats()` had exactly one caller —
        `_log_delivery_stats`, which logs `drops_by_reason` and **not**
        `drops_by_reason_setup`. That second key is the one that says whether a
        high-volume path is consuming the concurrency caps and starving the
        others, and it was computed on every cycle and rendered nowhere: a field
        one repo writes and no repo reads, standing in front of the question it
        was built to answer (owner, 2026-08-07).
        """
        try:
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(self._executor, self._build_router_delivery)
            await self._set(_store.KEY_ROUTER_DELIVERY, data, _store.TTL_ROUTER_DELIVERY)
        except Exception:
            log.exception("snapshot_writer: failed to write router_delivery")

    def _build_router_delivery(self) -> dict:
        router = getattr(self._engine, "router", None)
        stats = getattr(router, "delivery_stats", None)
        if not callable(stats):
            # Named, not blank: "no router on this object" and "the router has
            # dropped nothing" are different states with different fixes.
            return {"schema": 0, "error": "engine has no router.delivery_stats"}
        out = dict(stats())
        out["schema"] = 1
        return out

    async def _write_activity(self) -> None:
        try:
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(self._executor, self._build_activity)
            await self._set(_store.KEY_ACTIVITY_ALL, data, _store.TTL_ACTIVITY)
        except Exception:
            log.exception("snapshot_writer: failed to write activity")

    def _build_activity(self) -> list:
        from src.api.snapshot import build_activity
        return [i.model_dump(mode="json") for i in
                build_activity(self._engine, limit=500)]

    async def _write_alerts(self) -> None:
        """Publish the market-alerts feed so the isolated API can serve
        ``/api/alerts``.  Tiny payload (≤ buffer size dicts) — no executor
        round-trip needed."""
        try:
            service = getattr(self._engine, "_alert_service", None)
            if service is None:
                return
            await self._set(_store.KEY_ALERTS, service.recent(limit=500), _store.TTL_ALERTS)
        except Exception:
            log.exception("snapshot_writer: failed to write alerts")

    async def _write_agents(self) -> None:
        try:
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(self._executor, self._build_agents)
            await self._set(_store.KEY_AGENTS_ALL, data, _store.TTL_AGENTS)
        except Exception:
            log.exception("snapshot_writer: failed to write agents")

    def _build_agents(self) -> list:
        from src.api.snapshot import build_agents
        return [i.model_dump(mode="json") for i in build_agents(self._engine)]

    async def _write_tickers(self) -> None:
        try:
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(self._executor, self._build_tickers)
            await self._set(_store.KEY_TICKERS, data, _store.TTL_TICKERS)
        except Exception:
            log.exception("snapshot_writer: failed to write tickers")

    def _build_tickers(self) -> list:
        from src.api.snapshot import build_tickers
        return [i.model_dump(mode="json") for i in build_tickers(self._engine)]

    async def _write_engine_state(self) -> None:
        try:
            # Capture the live asyncio task census HERE, on the engine's event
            # loop — this is the only place that sees the engine container's
            # real tasks. (asyncio.all_tasks() inside the executor thread has no
            # running loop.) The isolated API container reads this back via
            # RedisEngineFacade to answer /internal/diag/tasks correctly.
            task_names = sorted(
                t.get_name() for t in asyncio.all_tasks() if not t.done()
            )
            loop = asyncio.get_running_loop()
            state = await loop.run_in_executor(
                self._executor, self._build_engine_state, task_names
            )
            await self._set(_store.KEY_ENGINE_STATE, state, _store.TTL_ENGINE_STATE)
        except Exception:
            log.exception("snapshot_writer: failed to write engine_state")

    def _build_engine_state(self, task_names: list) -> dict:
        from src.api.snapshot import collect_pairs_live as _collect_pairs_live
        engine = self._engine
        rm  = getattr(engine, "_risk_manager", None)
        om  = getattr(engine, "_order_manager", None)
        router = getattr(engine, "router", None)

        # Broker positions: {signal_id: {quantity, closed_quantity}}
        broker_positions: dict = {}
        if om is not None:
            _bp = getattr(om, "_positions", None)
            if isinstance(_bp, dict):
                broker_positions = {
                    sid: {
                        "quantity": float(getattr(p, "quantity", 0.0) or 0.0),
                        "closed_quantity": float(getattr(p, "closed_quantity", 0.0) or 0.0),
                    }
                    for sid, p in _bp.items()
                }

        # Active-signal dispatch timestamps for per-user window filtering.
        active_signal_dispatch: dict = {}
        if router is not None:
            for sid, sig in router.active_signals.items():
                dispatch_ts = (
                    getattr(sig, "dispatch_timestamp", None)
                    or getattr(sig, "timestamp", None)
                )
                active_signal_dispatch[sid] = str(dispatch_ts) if dispatch_ts else None

        # BTC regime
        regime = "RANGING"
        try:
            r = engine._regime_detector.get_regime("BTCUSDT")
            regime = r.regime.value if r else regime
        except Exception:
            pass

        # Uptime
        boot_time = getattr(engine, "_boot_time", 0.0) or 0.0
        uptime_seconds = max(0.0, time.monotonic() - boot_time) if boot_time else 0.0

        # Pair count
        pair_mgr = getattr(engine, "pair_mgr", None)
        scanning_pairs = len(pair_mgr.symbols) if pair_mgr and hasattr(pair_mgr, "symbols") else 0

        # Signals today
        history = getattr(engine, "_signal_history", []) or []
        today = datetime.now(timezone.utc).date()
        signals_today = sum(
            1 for s in history
            if getattr(s, "timestamp", None) is not None
            and s.timestamp.date() == today
        )

        # Auto-execution status
        auto_status: dict = {
            "mode": getattr(engine, "_current_auto_mode", "off"),
            "open_positions": rm.open_position_count if rm else 0,
            "daily_pnl_usd": float(rm.daily_realised_pnl_usd if rm else 0.0),
            "daily_loss_pct": 0.0,
            "daily_kill_tripped": bool(rm.daily_kill_tripped if rm else False),
            "manual_paused": False,
            "current_equity_usd": float(rm.current_equity_usd if rm else 0.0),
        }
        try:
            auto_status = engine.get_auto_execution_status()
        except Exception:
            pass

        # Paper equity (prefer broker's cumulative figure)
        paper_equity: float = 0.0
        active_mode = getattr(engine, "_current_auto_mode", "off")
        if active_mode == "paper" and om is not None and hasattr(om, "current_equity_usd"):
            try:
                paper_equity = float(om.current_equity_usd)
            except Exception:
                pass

        return {
            "current_auto_mode": getattr(engine, "_current_auto_mode", "off"),
            "regime_btcusdt": regime,
            "uptime_seconds": uptime_seconds,
            "scanning_pairs_count": scanning_pairs,
            "signals_today_count": signals_today,
            "risk_manager": {
                "open_position_count": rm.open_position_count if rm else 0,
                "daily_realised_pnl_usd": float(rm.daily_realised_pnl_usd if rm else 0.0),
                "current_equity_usd": float(rm.current_equity_usd if rm else 0.0),
                "daily_kill_tripped": bool(rm.daily_kill_tripped if rm else False),
            },
            "paper_equity_usd": paper_equity,
            "broker_positions": broker_positions,
            "active_signal_dispatch": active_signal_dispatch,
            "auto_execution_status": auto_status,
            "background_tasks": list(task_names),
            # Pairs X-ray (regular universe + live mover-promoted) so the ops
            # Pairs page reflects the engine container's in-memory scanner
            # state even from the isolated API container.
            "pairs": _collect_pairs_live(engine),
        }

    # ------------------------------------------------------------------
    # Mode-change command
    # ------------------------------------------------------------------

    async def _apply_pending_mode_cmd(self) -> None:
        """Pick up a pending mode-change queued by the API container."""
        if not self._redis.available:
            return
        try:
            raw = await self._redis.client.get(_store.KEY_CMD_SET_MODE)
            if raw is None:
                return
            new_mode = (raw or "").strip().lower()
            # Always delete first so a crash below doesn't re-apply on next cycle.
            await self._redis.client.delete(_store.KEY_CMD_SET_MODE)
            if new_mode not in {"off", "paper", "live"}:
                log.warning("snapshot_writer: ignoring invalid mode command: {!r}", new_mode)
                return
            log.info("snapshot_writer: applying mode command from API: {!r}", new_mode)
            ok, msg = self._engine.set_auto_execution_mode(new_mode)
            log.info("snapshot_writer: mode command result: {}", msg)
        except Exception:
            log.exception("snapshot_writer: failed to apply mode command")

    # ------------------------------------------------------------------
    # Full-signal-reset command
    # ------------------------------------------------------------------

    async def _apply_pending_reset_cmd(self) -> None:
        """Pick up a pending full-signal-reset queued by the API container."""
        if not self._redis.available:
            return
        try:
            raw = await self._redis.client.get(_store.KEY_CMD_RESET_SIGNALS)
            if raw is None:
                return
            await self._redis.client.delete(_store.KEY_CMD_RESET_SIGNALS)
            log.info("snapshot_writer: applying full signal reset command from API")
            result = self._engine.full_signal_reset()
            log.info("snapshot_writer: full signal reset complete: {}", result)
        except Exception:
            log.exception("snapshot_writer: failed to apply reset_signals command")

    # ------------------------------------------------------------------
    # SAR shadow-ledger purge command
    # ------------------------------------------------------------------

    async def _apply_pending_sar_clear_cmd(self) -> None:
        """Pick up an owner-initiated SAR ledger purge queued by the API."""
        if not self._redis.available:
            return
        try:
            raw = await self._redis.client.get(_store.KEY_CMD_CLEAR_SAR_LEDGER)
            if raw is None:
                return
            await self._redis.client.delete(_store.KEY_CMD_CLEAR_SAR_LEDGER)
            from src import sar_exit_shadow as _sar
            n = _sar.get_sar_store().clear()
            log.info("snapshot_writer: SAR ledger cleared on owner request ({} records)", n)
        except Exception:
            log.exception("snapshot_writer: failed to apply clear_sar_ledger command")

    # ------------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------------

    async def _set(self, key: str, data: Any, ttl: int) -> None:
        """Write *data* to Redis with TTL.  No-ops silently when Redis is down."""
        if not self._redis.available:
            return
        await self._redis.client.set(key, _store.encode(data), ex=ttl)
