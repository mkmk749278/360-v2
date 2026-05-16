"""Paper-trade-visibility endpoints (paper-trade visibility, 2026-05-16).

Carved out of ``server.py`` so the giant ``build_app`` function stays
manageable.  Endpoints registered by :func:`register` against a built
FastAPI app:

* ``GET  /api/trades`` — paginated per-trade ledger
* ``POST /api/auto-mode/paper/reset`` — owner-only paper account reset
* ``POST /api/auto-mode/paper/close-all`` — user-initiated flatten of the
  paper book (companion to reset; reset preserves in-flight signals by
  design so users need a separate explicit close-all action)

All endpoints depend on dependencies already constructed inside
``build_app`` (``auth``, ``owner_required``).  The caller passes them in
so the dep graph stays internal to ``build_app`` — same pattern as the
rest of the endpoints in this directory.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status

from src.utils import get_logger

from .schemas import (
    PaperCloseAllResponse,
    PaperResetResponse,
    TradeListResponse,
    TradeRecord,
)

log = get_logger("api.paper_trade_routes")


def register(
    app: FastAPI,
    *,
    engine: Any,
    auth: Callable,
    owner_required: Callable,
) -> None:
    """Wire ``GET /api/trades``, ``POST /api/auto-mode/paper/reset`` and
    ``POST /api/auto-mode/paper/close-all`` onto the given app.

    Idempotent in terms of behaviour — calling twice would register
    duplicate routes (FastAPI would raise), so the caller is expected to
    call this exactly once per ``build_app`` invocation.

    The reset / close-all endpoints read ``engine._order_manager``
    directly so the code is portable across the various engine wiring
    layouts in bootstrap.py — same lookup pattern used by ``build_pulse`` /
    ``build_auto_mode``.
    """

    # ---- Per-trade records (paper-trade visibility) ----
    #
    # Backs the Lumin app's trade-history list — every closed paper trade
    # with the leverage + position_size_pct snapshotted at open and the
    # ROI%-on-margin derived at close.  Read-only; the broker writes via
    # ``trade_records.{open,record_partial_fill,close}_trade`` inside
    # ``PaperOrderManager``.  Live mode intentionally returns 400 in
    # this PR — live per-trade records are deferred to a follow-up that
    # reconciles against the exchange's actual fills.

    @app.get(
        "/api/trades",
        response_model=TradeListResponse,
        tags=["auto-mode"],
        dependencies=[Depends(auth)],
    )
    async def list_paper_trades(
        mode: str = Query("paper", pattern="^(paper|live)$"),
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        since_ts: Optional[str] = Query(
            None,
            description="ISO-8601 UTC; return rows closed at-or-after this stamp",
        ),
        symbol: Optional[str] = Query(
            None,
            description="Exact-match symbol filter, e.g. BTCUSDT",
        ),
        include_open: bool = Query(
            False,
            description="When true, include in-flight trades that have no closed_at yet",
        ),
    ) -> TradeListResponse:
        """Paginated per-trade history for the Lumin app.

        Fail-soft: any SQLite IO failure (eg. concurrent rename during
        ``POST /api/auto-mode/paper/reset``) returns an empty page
        rather than 500.  The next refresh will land cleanly.
        """
        if mode != "paper":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="only paper mode supported in v1 — live trade records ship in a follow-up",
            )
        try:
            from src.auto_trade import trade_records
            raw = trade_records.list_trades(
                limit=limit, offset=offset, since_ts=since_ts,
                symbol=symbol, include_open=include_open,
            )
            total = trade_records.count_trades(
                since_ts=since_ts, symbol=symbol, include_open=include_open,
            )
        except Exception:
            log.exception("/api/trades failed — returning empty page")
            return TradeListResponse(items=[], total=0)
        items = [TradeRecord(**row) for row in raw]
        return TradeListResponse(items=items, total=total)

    # ---- Paper-mode manual reset (owner-only) ----
    #
    # Owner-mediated wipe of the paper account: zeros the broker's
    # ``_realised_pnl_total`` + ``_available_equity``, clears the
    # paper daily-bucket history, and archives the per-trade rows to a
    # timestamped table.  Refuses while open positions exist (would
    # orphan the engine's lifecycle state).

    @app.post(
        "/api/auto-mode/paper/reset",
        response_model=PaperResetResponse,
        tags=["auto-mode"],
        dependencies=[Depends(owner_required)],
    )
    async def paper_reset() -> PaperResetResponse:
        """Reset the paper-mode account to a clean starting balance.

        Steps (in order):

        1. Refuse if the engine has any open paper positions — clearing
           equity while in-flight trades reference it would orphan the
           engine's lifecycle state.
        2. Call ``PaperOrderManager.reset_state()`` to zero cumulative
           PnL and re-seed equity from ``starting_equity_usd``.
        3. ``pnl_history.reset_mode("paper")`` — wipe daily buckets so
           the dashboard chart starts fresh.
        4. ``trade_records.archive_all()`` — rename the live trade
           table to a timestamped archive; per-trade history remains
           queryable via SQLite ad-hoc until the owner drops it.

        Idempotent on an already-empty paper session — every step is a
        no-op on empty state.
        """
        om = getattr(engine, "_order_manager", None)
        if om is None or not hasattr(om, "reset_state"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="paper reset requires an active PaperOrderManager — "
                       "switch to paper mode first",
            )
        # Open-positions guard.  We trust the in-broker map over the
        # RiskManager view because the broker is the ground truth for
        # paper positions.
        try:
            open_count = int(getattr(om, "open_position_count", 0) or 0)
        except Exception:
            open_count = 0
        if open_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"refuse paper reset — {open_count} open positions "
                       "would be orphaned; close or let them expire first",
            )
        starting = float(getattr(om, "_starting_equity", 1000.0))
        # 2. Zero broker state.
        om.reset_state()
        # 3. Wipe daily buckets.
        from src.auto_trade import pnl_history as _pnl_history
        buckets_cleared = _pnl_history.reset_mode("paper")
        # 4. Archive per-trade rows (preferred over destructive delete —
        # historical data remains queryable for the owner).
        try:
            from src.auto_trade import trade_records as _trade_records
            trades_archived = _trade_records.archive_all()
        except Exception:
            log.exception("paper reset: trade_records.archive_all failed")
            trades_archived = 0

        # Single-line audit log so the operator can grep for reset events.
        reset_at = datetime.now(timezone.utc).isoformat()
        log.info(
            "paper_reset reset_at={} starting_equity_usd={:.2f} "
            "buckets_cleared={} trades_archived={}",
            reset_at, starting, buckets_cleared, trades_archived,
        )
        return PaperResetResponse(
            reset_at=reset_at,
            starting_equity_usd=starting,
            pnl_buckets_cleared=buckets_cleared,
            trades_archived=trades_archived,
        )

    # ---- Paper-mode close-all-positions (user-initiated) ----
    #
    # Why a separate endpoint instead of folding into /reset
    # ------------------------------------------------------
    # ``POST /api/auto-mode/paper/reset`` (PR #401) deliberately
    # preserves ``PaperOrderManager._positions`` so the live-mode
    # counterpart — whose positions live on the real exchange — can't
    # be orphaned by a careless equity-wipe.  Users running paper-only
    # sessions still want a one-shot "flatten my book" action they can
    # fire **before** ``/reset`` (the reset endpoint refuses while open
    # positions exist).  This endpoint is that action.  Two-step flow:
    # ``close-all`` → optional ``reset``.
    #
    # Auth: mirrors ``/reset`` (owner-only).  Same pattern, same
    # guard rails, same engine-lookup.  Returns 409 when no
    # PaperOrderManager is wired (live mode / off mode).

    @app.post(
        "/api/auto-mode/paper/close-all",
        response_model=PaperCloseAllResponse,
        tags=["auto-mode"],
        dependencies=[Depends(owner_required)],
    )
    async def paper_close_all() -> PaperCloseAllResponse:
        """Flatten the paper book at zero-move fills.

        Iterates every entry in ``PaperOrderManager._positions`` and
        invokes :meth:`PaperOrderManager.close_full` with
        ``current_price=position.entry`` so the fill books no price
        PnL — only round-trip fees.  Returns the count of positions
        closed and the sum of realised PnL from this batch.

        Idempotent on a flat book — returns ``closed_count=0``,
        ``realised_pnl_total=0.0`` with no side effects.
        """
        om = getattr(engine, "_order_manager", None)
        if om is None or not hasattr(om, "close_all_open_positions"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="paper close-all requires an active PaperOrderManager — "
                       "switch to paper mode first",
            )
        result = await om.close_all_open_positions("user_close_all")
        # Defensive: an unwired or stub broker may return a non-dict —
        # coerce so the response schema validation doesn't 500.
        closed_count = (
            int(result.get("closed_count", 0)) if isinstance(result, dict) else 0
        )
        realised_pnl_total = (
            float(result.get("realised_pnl_total", 0.0))
            if isinstance(result, dict) else 0.0
        )
        return PaperCloseAllResponse(
            ok=True,
            closed_count=closed_count,
            realised_pnl_total=realised_pnl_total,
        )
