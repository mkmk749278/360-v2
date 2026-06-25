"""Admin full-signal-reset endpoint.

``POST /api/admin/reset-signals`` — owner-only nuclear reset that clears
ALL signal state across the engine:

  1. Active signals (router.active_signals) — removes ACTIVE entries from
     the app feed for every user.
  2. Signal history (data/signal_history.json + in-memory) — clears the
     closed-signal feed.
  3. Performance stats (PerformanceTracker) — zeroes win/loss counters.
  4. Invalidation records (data/invalidation_records.json) — erases the
     INVALIDATED audit trail.
  5. Paper broker (PaperOrderManager) — closes all open paper positions
     and resets equity/PnL for ALL users (paper mode only; no-op in live/off).

In single-process mode steps 1-5 execute synchronously in the request handler.
In isolated mode steps 1-4 queue a Redis command for the engine container
(≤15s propagation); step 5 runs locally since the API container owns the
PaperOrderManager.

Owner-gated (Bearer token / Firebase owner tier). Auditable — the ops
dashboard records every call to ``ops_audit.log``.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable

from fastapi import Depends, FastAPI

from src.utils import get_logger

log = get_logger("api.reset_signals_route")


def register(
    app: FastAPI,
    *,
    engine: Any,
    owner_required: Callable,
) -> None:
    """Register ``POST /api/admin/reset-signals`` on the given app."""

    @app.post(
        "/api/admin/reset-signals",
        tags=["admin"],
        dependencies=[Depends(owner_required)],
    )
    async def admin_reset_signals() -> dict:
        """Full-signal reset: clear active signals, history, stats, invalidation, paper broker.

        Idempotent on already-empty state. Returns a summary of counts cleared.
        Isolated-mode note: signal-state clearing (steps 1-4) propagates to the
        engine container asynchronously (≤15s); paper broker (step 5) applies
        immediately since the API container holds the PaperOrderManager.
        """
        result: dict = {
            "reset_at": datetime.now(timezone.utc).isoformat(),
            "cleared_active_signals": 0,
            "cleared_history": 0,
            "cleared_perf_stats": 0,
            "cleared_invalidation_records": 0,
            "paper_positions_closed": 0,
            "paper_pnl_buckets_cleared": 0,
            "paper_trades_archived": 0,
            "engine_reset_queued": False,
        }

        # ---- Engine signal state (direct or queued via Redis) ----
        is_facade = type(engine).__name__ == "RedisEngineFacade"
        if is_facade:
            # Isolated mode: queue the signal-state clear for the engine container.
            try:
                ok, msg = engine.request_full_signal_reset()
                result["engine_reset_queued"] = ok
                log.info("admin_reset_signals: queued engine reset: {}", msg)
            except Exception:
                log.exception("admin_reset_signals: failed to queue engine reset")
        else:
            # Single-process: clear directly.
            try:
                engine_result = engine.full_signal_reset()
                result.update({k: v for k, v in engine_result.items() if k in result})
                log.info("admin_reset_signals: direct engine reset: {}", engine_result)
            except Exception:
                log.exception("admin_reset_signals: direct engine reset failed")

        # ---- Paper broker (API container owns this in both modes) ----
        om = getattr(engine, "_order_manager", None)
        if om is not None and hasattr(om, "close_all_open_positions"):
            # Close all open paper positions at zero-move fills.
            try:
                close_result = await om.close_all_open_positions("admin_reset_all")
                if isinstance(close_result, dict):
                    result["paper_positions_closed"] = int(close_result.get("closed_count", 0))
            except Exception:
                log.exception("admin_reset_signals: paper close_all failed")

            # Reset paper equity and PnL history.
            if hasattr(om, "reset_state"):
                try:
                    om.reset_state()
                except Exception:
                    log.exception("admin_reset_signals: paper reset_state failed")

            # Reset RiskManager daily state.
            rm = getattr(engine, "_risk_manager", None)
            if rm is not None and hasattr(rm, "reset_daily"):
                try:
                    rm.reset_daily()
                except Exception:
                    log.exception("admin_reset_signals: risk_manager.reset_daily failed")

            # Wipe paper PnL history buckets.
            try:
                from src.auto_trade import pnl_history as _pnl_history
                if hasattr(om, "positions_for_user"):
                    buckets = await asyncio.to_thread(_pnl_history.reset_aggregate, "paper")
                else:
                    buckets = await asyncio.to_thread(_pnl_history.reset_mode, "paper")
                result["paper_pnl_buckets_cleared"] = buckets
            except Exception:
                log.exception("admin_reset_signals: pnl_history reset failed")

            # Archive trade records.
            try:
                from src.auto_trade import trade_records as _trade_records
                archived = await asyncio.to_thread(_trade_records.archive_all)
                result["paper_trades_archived"] = archived
            except Exception:
                log.exception("admin_reset_signals: trade_records.archive_all failed")

        log.info("admin_reset_signals: complete — {}", result)
        return result
