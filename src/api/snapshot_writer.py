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
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor as _TPE
from datetime import datetime, timezone
from typing import Any

from src.utils import get_logger

from . import snapshot_store as _store

log = get_logger("api.snapshot_writer")

_CYCLE_INTERVAL_S   = 15   # ≈ one scan cycle
_ACTIVITY_INTERVAL_S = 30
_AGENTS_INTERVAL_S   = 60

#: A cycle slower than this has started eating its own margin. The feed-critical
#: keys carry ``TTL_SIGNALS`` = 60s against a 15s interval — **four** cycles of
#: slack, not the two ``snapshot_store``'s own docstring claims ("TTL is 2x that
#: interval"; the values are 3-4x. Left alone here: more margin than advertised
#: is the safe direction, and the number to trust is the constant, not the
#: sentence). Four cycles is why this took ~45s of work per cycle to bite rather
#: than ~15s. Counted, never fatal — see ``overrun_count``.
_OVERRUN_BUDGET_S = _CYCLE_INTERVAL_S


def _host_resources() -> dict[str, Any]:
    """CPU / memory / disk headroom and the config the process is really using.

    Fail-open with a named reason: a snapshot that cannot be written because a
    ``/sys`` read raised would take the dashboard and the app feed down to
    answer a diagnostic question, which is the wrong trade in both directions.
    """
    try:
        from src.host_resources import sample

        return sample()
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}"}


def _loop_health(engine: Any) -> dict[str, Any]:
    """Engine-loop health for ``snapshot:engine_state``.

    Three producers, each keyed under its own name and each independently
    absent when its subsystem has not started.  ``None`` means *this engine did
    not report it* — an older build, or a subsystem not running — and is never
    collapsed to a zero, because a zero here reads as a healthy loop and would
    be the reassuring answer on exactly the surface built to stop that.

    Pure reads of in-memory counters; no network, no disk, and it runs inside
    the snapshot writer's executor thread rather than on the loop.
    """
    out: dict[str, Any] = {
        "scan_cycle": None,
        "indicator_cache": None,
        "snapshot_writer": None,
        "strategy_edge": None,
    }
    scanner = getattr(engine, "_scanner", None)
    if scanner is not None and hasattr(scanner, "cycle_health"):
        try:
            out["scan_cycle"] = scanner.cycle_health()
        except Exception:
            pass
    if scanner is not None and hasattr(scanner, "indicator_cache_health"):
        try:
            out["indicator_cache"] = scanner.indicator_cache_health()
        except Exception:
            pass
    writer = getattr(engine, "_snapshot_writer", None)
    if writer is not None and hasattr(writer, "health"):
        try:
            out["snapshot_writer"] = writer.health()
        except Exception:
            pass
    try:
        from src.strategy_edge import get_strategy_edge_store

        out["strategy_edge"] = get_strategy_edge_store().flush_health()
    except Exception:
        pass
    return out


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
        # Writer health, read by the `snapshot_writer` liveness probe. These are
        # in-memory counters: no network, no cost, and they are the LEADING
        # indicator. The lagging one is the keys vanishing, and by then the app
        # has already shown a subscriber an empty feed.
        self.cycle_count: int = 0
        self.overrun_count: int = 0
        self.last_cycle_sec: float = 0.0
        self.worst_cycle_sec: float = 0.0
        self.last_completed_at: float = 0.0
        #: Per-payload cost of the last cycle, so the 75s total can be attributed.
        self.write_times: dict[str, float] = {}
        # Dedicated 1-thread pool for Pydantic serialisation — keeps heavy
        # model-construction off the engine's main asyncio event loop.
        self._executor = _TPE(max_workers=1, thread_name_prefix="snapshot-writer")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Long-running task: write snapshots on a FIXED period.

        The loop used to be ``sleep(15); write_cycle()``, which makes the real
        period ``15s + however long the write took`` — while every key it writes
        carries a TTL of *twice the interval* on the stated contract that the
        interval is 15s (``snapshot_store``: "Writer interval -> TTL is 2x that
        interval so one missed write never evicts a warm cache").

        That contract silently assumed the write itself is free. It is not: one
        cycle serialises eight payloads, the first of which is 500 signals,
        through a single-thread executor — on a box where the engine has been
        measured at 124-208% of a 2.5-core cap. The real slack is four cycles
        (``TTL_SIGNALS`` is 60s, not the 2x the store's docstring claims), so it
        takes ~45s of work per cycle before the period reaches 60s — at which
        point the keys reach their TTL and evict.

        And the blast radius is not the dashboard. In isolated mode the api
        container serves from these keys and nothing else, so an expired
        ``snapshot:signals_all`` is a **subscriber** opening the Lumin app and
        reading "No signals yet" (owner-reported 2026-08-18, alongside the
        ``snapshot_key_missing`` page at 10:08 UTC). The rows came back when the
        keys did — nothing was lost, and every user who looked in that window
        saw an empty product.

        So: sleep the REMAINDER of the interval, not the whole of it. A cycle
        that overruns starts the next one immediately rather than adding its
        cost to the period, and the overrun is counted so the liveness probe can
        page on it *before* anything expires.
        """
        log.info(
            "SnapshotWriter started — writing to Redis every {}s (fixed period)",
            _CYCLE_INTERVAL_S,
        )
        try:
            while True:
                started = time.monotonic()
                await self._write_cycle()
                elapsed = time.monotonic() - started

                self.cycle_count += 1
                self.last_cycle_sec = elapsed
                self.worst_cycle_sec = max(self.worst_cycle_sec, elapsed)
                self.last_completed_at = time.time()
                if elapsed > _OVERRUN_BUDGET_S:
                    self.overrun_count += 1
                    log.warning(
                        "snapshot_writer: cycle took {:.1f}s, over the {}s budget — "
                        "keys carry a {}s TTL, so sustained overruns expire them "
                        "and the app feed reads empty",
                        elapsed, _OVERRUN_BUDGET_S, _store.TTL_SIGNALS,
                    )
                # Never negative: an overrunning cycle re-enters immediately
                # instead of adding its own duration to the period.
                await asyncio.sleep(max(0.0, _CYCLE_INTERVAL_S - elapsed))
        finally:
            self._executor.shutdown(wait=False)

    def health(self) -> dict[str, Any]:
        """Counters for the ``snapshot_writer`` liveness probe.

        In-memory only, by the same rule every other probe here follows: a
        probe that costs a network read cannot run on a per-cycle clock.
        """
        return {
            "cycles": self.cycle_count,
            "overruns": self.overrun_count,
            "last_cycle_sec": round(self.last_cycle_sec, 2),
            "worst_cycle_sec": round(self.worst_cycle_sec, 2),
            "last_completed_at": self.last_completed_at,
            "budget_sec": _OVERRUN_BUDGET_S,
            # Read from the store rather than recomputed. The first cut derived
            # it as ``2 * _CYCLE_INTERVAL_S`` from the store's own docstring and
            # was wrong by half — the constants say 60s, the sentence says 2x.
            # A number a reader can check beats a number a comment asserts.
            "ttl_sec": _store.TTL_SIGNALS,
            # Slowest first — the reader's next question after "the cycle is
            # slow" is always "slow where".
            "write_times": dict(sorted(
                self.write_times.items(), key=lambda kv: kv[1], reverse=True
            )),
        }

    # ------------------------------------------------------------------
    # Per-cycle orchestrator
    # ------------------------------------------------------------------

    @contextmanager
    def _timing(self, name: str):
        """Record what one payload write cost, without changing how it is called.

        The cycle total said 75s and could not say *which* of eight payloads
        spent it. "The 500-signal serialisation is obviously the expensive one"
        is a hypothesis about behaviour, not a measurement of it — and this repo
        has paid repeatedly for shipping the first as if it were the second. So
        the next change to the writer's cost gets aimed rather than guessed.

        **A context manager rather than a wrapper, and that is the whole point.**
        The first cut was ``await self._timed("signals", self._write_signals)``,
        which turns every dispatch from a *call* into an *argument* — and two
        derived guards (``test_dark_promotion``, ``test_signal_router``) parse
        this function's AST and assert each payload writer appears as a call,
        because "defining a writer is not calling it" is a seam this repo has
        paid for under several names. CI caught it immediately, which is the
        guards working.

        The right response was not to teach both guards a second shape. It was
        to keep the shape they pin: ``with self._timing(...): await
        self._write_x()`` leaves the call exactly where it was, so those guards
        go on protecting every payload added later without anyone remembering
        to update them. An invariant that survives a refactor unchanged is worth
        more than one that has to be renegotiated with it.

        Timed in a ``finally``: the write that raised is exactly the one whose
        cost you want.
        """
        started = time.monotonic()
        try:
            yield
        finally:
            self.write_times[name] = round(time.monotonic() - started, 2)

    async def _write_cycle(self) -> None:
        now = time.monotonic()
        with self._timing("signals"):
            await self._write_signals()
        with self._timing("tickers"):
            await self._write_tickers()
        with self._timing("engine_state"):
            await self._write_engine_state()
        with self._timing("positions_diag"):
            await self._write_positions_diag()
        with self._timing("data_intake"):
            await self._write_data_intake()
        with self._timing("trail_governor"):
            await self._write_trail_governor()
        with self._timing("router_delivery"):
            await self._write_router_delivery()
        with self._timing("dark_promotion"):
            await self._write_dark_promotion()
        if now - self._last_activity >= _ACTIVITY_INTERVAL_S:
            with self._timing("activity"):
                await self._write_activity()
            with self._timing("alerts"):
                await self._write_alerts()
            self._last_activity = now
        if now - self._last_agents >= _AGENTS_INTERVAL_S:
            with self._timing("agents"):
                await self._write_agents()
            self._last_agents = now
        # Check for a pending mode-change command from the API container.
        await self._apply_pending_mode_cmd()
        # Check for a pending full-signal-reset command from the API container.
        await self._apply_pending_reset_cmd()
        await self._apply_pending_sar_clear_cmd()
        # Diagnostic-catalog requests from ops. Drained here because this
        # loop runs IN the engine container, which is the only process that
        # can see the scanner, the stores and the executor.
        await self._apply_pending_diag_cmds()

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

    async def _write_trail_governor(self) -> None:
        """Publish the live trail-governor X-ray computed engine-side.

        Same reason as the two above, and this one is the sharpest case: the
        governor's counters and the open-position index are **in-process state
        of the engine container**. The API container's facade cannot see
        either, so a handler that built this locally would report
        ``index_cold`` and zeroed counters forever while the governor ran
        perfectly here — a panel describing the wrong process, on the one
        mechanism in the system that places real orders.
        """
        try:
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(
                self._executor, self._build_trail_governor
            )
            await self._set(
                _store.KEY_TRAIL_GOVERNOR, data, _store.TTL_TRAIL_GOVERNOR
            )
        except Exception:
            log.exception("snapshot_writer: failed to write trail_governor")

    def _build_trail_governor(self) -> dict:
        from src.execution.trail_governor import build_diag
        return build_diag()

    async def _write_dark_promotion(self) -> None:
        """Publish the dark→live promotion runtime block computed engine-side.

        ``dark_promotion.decide`` runs at the scanner's divert site, so its
        counters, the refusal census that says *which condition* is refusing,
        and the daily cap's tally are in-process state of **this** container.
        The ops control panel is served by the API container, whose own
        snapshot loads the rules from the shared volume and reports every one
        of those numbers as zero.

        That is the sharpest form of the trail-governor defect: zero is also
        what a correctly-armed rule reads before it fires, so the panel is
        wrong in a way that looks exactly right — and only starts looking wrong
        once the rule begins working, which is the moment the owner most needs
        to believe it.
        """
        try:
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(
                self._executor, self._build_dark_promotion
            )
            await self._set(
                _store.KEY_DARK_PROMOTION, data, _store.TTL_DARK_PROMOTION
            )
        except Exception:
            log.exception("snapshot_writer: failed to write dark_promotion")

    def _build_dark_promotion(self) -> dict:
        from src import dark_promotion
        return dark_promotion.runtime_report()

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

        # Signals today.  This container HOLDS the history, so this is the
        # authoritative count — and it is the only one, because the api
        # container's facade has no history to walk (see
        # ``RedisEngineFacade.signals_today_count``).  Published under
        # ``signals_today_count`` below; ``build_pulse`` prefers it.
        #
        # Dated through ``snapshot._signal_date`` rather than
        # ``s.timestamp.date()`` so the writer and the reader answer the same
        # question about the same row: a restart-restored record can carry an
        # ISO **string**, on which ``is not None`` passes and ``.date()``
        # raises.  Two implementations of "which day is this signal" is how
        # the two ends silently disagree.
        from src.api.snapshot import _signal_date

        history = getattr(engine, "_signal_history", []) or []
        today = datetime.now(timezone.utc).date()
        signals_today = sum(1 for s in history if _signal_date(s) == today)

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
            # Engine-loop health, published so ops can render the numbers that
            # decide whether this container survives (2026-08-19).  Scan-cycle
            # wall-time is heartbeat age — the scanner touches its heartbeat
            # once per cycle and healthcheck.py kills the container when that
            # file goes stale — and it had lived only in a log line.  The
            # snapshot writer's own counters ride alongside because a slow
            # writer and a slow scan loop have the same cause and different
            # fixes, and a reader comparing them needs both on one payload.
            "loop_health": _loop_health(engine),
            # What the BOX is giving this process. Measured here, in the engine
            # container, precisely because the API container that serves the
            # diag would otherwise measure its own near-idle cgroup and report
            # it as the engine's load — the trail-governor INDEX COLD defect,
            # on the number the owner asked about first.
            "host_resources": _host_resources(),
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
    # Diagnostic-catalog channel
    # ------------------------------------------------------------------

    #: Bounded per cycle so a flood of queued requests cannot starve the writes
    #: this loop exists to make. The queue keeps its tail for the next pass.
    _DIAG_MAX_PER_CYCLE = 4

    async def _apply_pending_diag_cmds(self) -> None:
        """Drain queued diagnostic requests, run them, publish each result.

        The API container cannot see the scanner, the data store or the executor
        in isolated mode — the trail-governor ``INDEX COLD`` defect — so a
        diagnostic assembled there would describe the wrong process. It queues a
        catalog KEY here instead and this loop, inside the engine container,
        runs it.

        What may run is decided entirely by ``src/diag_catalog.py``: an unknown
        key is refused there, and no entry can reach an order, a secret or the
        kill switch (asserted structurally in ``tests/test_diag_catalog.py``).
        This function chooses nothing.
        """
        if not self._redis.available:
            return
        import json as _json

        from src import diag_catalog

        for _ in range(self._DIAG_MAX_PER_CYCLE):
            try:
                raw = await self._redis.client.rpop(_store.KEY_CMD_DIAG)
            except Exception:
                log.exception("snapshot_writer: diag queue read failed")
                return
            if raw is None:
                return
            try:
                env = _json.loads(raw)
                req_id = str(env.get("request_id") or "")
                key = str(env.get("key") or "")
                args = env.get("args") if isinstance(env.get("args"), dict) else {}
                queued_at = float(env.get("ts") or 0.0)
            except Exception:
                log.warning("snapshot_writer: unparseable diag envelope, dropped")
                continue
            if not req_id:
                continue
            # A stale envelope is one the caller stopped waiting for — running it
            # spends engine time on an answer nobody will read, and for an action
            # it applies a change whose requester is long gone.
            if queued_at and (time.time() - queued_at) > _store.DIAG_CMD_STALE_S:
                out = {"ok": False, "key": key, "error": "stale request — not run"}
            else:
                out = diag_catalog.run(key, self._engine, args)
            try:
                await self._redis.client.set(
                    _store.KEY_DIAG_RESULT_PREFIX + req_id,
                    _json.dumps(out, default=str),
                    ex=_store.TTL_DIAG_RESULT,
                )
            except Exception:
                log.exception("snapshot_writer: could not publish diag result")

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
