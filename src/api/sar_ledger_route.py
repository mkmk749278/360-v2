"""Owner-only purge of the SAR exit shadow ledger.

``POST /api/admin/sar-ledger/clear`` — drops every stamped/resolved record in
``sar_exit_shadow``'s dedicated store and persists the empty ledger.

**Why a manual purge exists.** The ledger is forward-measurement, and a defect
in how records are *resolved* makes every row evidence of the bug rather than
of the exit method — the 2026-07-26 case, where the walker located the entry
bar by counting elapsed time and so replayed a different bar than the trade,
producing 172 rows averaging −4.4R that described nothing. There is no field
that can rescue a row whose candles were wrong, so the only honest repair is to
throw the window away and re-measure. That defect's history is purged
automatically by the v2 path bump; this endpoint is for the next one, so the
owner never has to wait on a deploy to stop a poisoned window from feeding the
edge matrix.

Deliberately NOT part of ``/api/admin/reset-signals``: that clears the *live*
signal feed, and conflating "wipe what users see" with "wipe a measurement
window" makes the safe action look dangerous and the dangerous one routine.

**Isolated mode.** The engine container owns the in-memory buffer and the
persist file, so the API container queues a Redis command rather than clearing
the file underneath it — the engine would otherwise persist its buffer straight
back over the top. Single-process clears inline.

Owner-gated (Bearer / Firebase owner tier). The ops dashboard audits every call.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from fastapi import Depends, FastAPI

from src.utils import get_logger

log = get_logger("api.sar_ledger_route")


def register(
    app: FastAPI,
    *,
    engine: Any,
    owner_required: Callable,
) -> None:
    """Register ``POST /api/admin/sar-ledger/clear`` on the given app."""

    @app.post(
        "/api/admin/sar-ledger/clear",
        tags=["admin"],
        dependencies=[Depends(owner_required)],
    )
    async def admin_clear_sar_ledger() -> dict:
        """Purge the SAR exit shadow ledger. Idempotent on an empty ledger."""
        result: dict = {
            "cleared_at": datetime.now(timezone.utc).isoformat(),
            "cleared_records": 0,
            "queued": False,
        }
        if type(engine).__name__ == "RedisEngineFacade":
            try:
                ok, msg = engine.request_sar_ledger_clear()
                result["queued"] = bool(ok)
                result["note"] = msg
                log.info("admin_clear_sar_ledger: queued for engine container")
            except Exception:
                log.exception("admin_clear_sar_ledger: failed to queue clear")
            return result
        try:
            from src import sar_exit_shadow as _sar

            result["cleared_records"] = _sar.get_sar_store().clear()
            log.info(
                "admin_clear_sar_ledger: cleared {} records", result["cleared_records"]
            )
        except Exception:
            log.exception("admin_clear_sar_ledger: direct clear failed")
        return result
