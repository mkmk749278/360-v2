"""Paper-trade-visibility endpoints (paper-trade visibility, 2026-05-16).

Carved out of ``server.py`` so the giant ``build_app`` function stays
manageable.  Endpoints registered by :func:`register` against a built
FastAPI app:

* ``GET  /api/trades`` — paginated per-trade ledger (per-user filtered
  via subscription windows since 2026-05-23)
* ``POST /api/auto-mode/paper/reset`` — owner-only paper account reset
* ``POST /api/auto-mode/paper/reset-mine`` — user-callable per-user
  visibility reset (carves a fresh subscription window for the caller)
* ``POST /api/auto-mode/paper/close-all`` — user-initiated flatten of the
  paper book (companion to reset; reset preserves in-flight signals by
  design so users need a separate explicit close-all action)

All endpoints depend on dependencies already constructed inside
``build_app`` (``auth``, ``user_claims``, ``owner_required``).  The caller
passes them in so the dep graph stays internal to ``build_app`` — same
pattern as the rest of the endpoints in this directory.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status

from src.utils import get_logger

from .paper_user_view import filter_trades_for_user
from .schemas import (
    PaperCloseAllResponse,
    PaperResetMineResponse,
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
    user_claims: Optional[Callable] = None,
    resolve_user_id: Optional[Callable] = None,
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

    # Per-user trade view requires both a user-claims dependency and an
    # identity resolver. When either is missing (legacy bootstrap paths
    # that wired register() without them) we fall back to the shared
    # engine ledger so existing deployments don't break.
    _per_user_enabled = user_claims is not None and resolve_user_id is not None
    _user_claims_dep = user_claims if _per_user_enabled else (lambda: None)

    @app.get(
        "/api/trades",
        response_model=TradeListResponse,
        tags=["auto-mode"],
        dependencies=[Depends(auth)],
    )
    async def list_paper_trades(
        identity: Any = Depends(_user_claims_dep),
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
        """Per-user-filtered paginated paper-trade history.

        Pre-2026-05-23 this endpoint returned the engine's shared ledger
        to every authenticated user — fresh signups saw the operator's
        prior paper trades. Now the engine ledger is filtered by the
        caller's ``user_paper_subscriptions`` windows so each user only
        sees trades closed while they had paper mode enabled.

        Fail-soft: any SQLite IO failure (eg. concurrent rename during
        ``POST /api/auto-mode/paper/reset``) returns an empty page
        rather than 500. The next refresh will land cleanly.
        """
        if mode != "paper":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="only paper mode supported in v1 — live trade records ship in a follow-up",
            )

        # Per-user books ON: the caller reads their OWN trades DB directly —
        # no shared ledger, no subscription-window filter (the per-user book
        # is the isolation boundary).
        om = getattr(engine, "_order_manager", None)
        if _per_user_enabled and om is not None and hasattr(om, "trades_db_path_for"):
            try:
                user_id = resolve_user_id(identity)  # type: ignore[misc]
            except HTTPException:
                return TradeListResponse(items=[], total=0)
            except Exception:
                log.exception("/api/trades: user resolve failed")
                return TradeListResponse(items=[], total=0)
            try:
                from src.auto_trade import trade_records
                rows = await asyncio.to_thread(
                    trade_records.list_trades,
                    limit=limit, offset=offset, since_ts=since_ts,
                    symbol=symbol, include_open=include_open,
                    db_path=om.trades_db_path_for(user_id),
                )
                total_rows = await asyncio.to_thread(
                    trade_records.list_trades,
                    limit=500, offset=0, since_ts=since_ts,
                    symbol=symbol, include_open=include_open,
                    db_path=om.trades_db_path_for(user_id),
                )
            except Exception:
                log.exception("/api/trades (per-user book) failed — empty page")
                return TradeListResponse(items=[], total=0)
            items = [TradeRecord(**row) for row in rows]
            return TradeListResponse(items=items, total=len(total_rows))

        try:
            from src.auto_trade import trade_records
            # Pull a generous slice from the engine ledger; filter to the
            # user's subscription windows, then re-paginate. The 500-row
            # over-fetch matches list_trades' built-in upper cap so we
            # don't lose pages. Single-operator phase keeps engine/user
            # ratio ~1; Phase 3 may need a join-pushed-into-SQL variant.
            ledger_rows = await asyncio.to_thread(
                trade_records.list_trades,
                limit=500, offset=0, since_ts=since_ts,
                symbol=symbol, include_open=include_open,
            )
        except Exception:
            log.exception("/api/trades failed — returning empty page")
            return TradeListResponse(items=[], total=0)

        if _per_user_enabled:
            try:
                user_id = resolve_user_id(identity)  # type: ignore[misc]
                from .user_overrides import get_singleton
                store = get_singleton()
                if store is None:
                    # Bootstrap should have wired the store before
                    # registering routes; if it didn't, fail safe.
                    return TradeListResponse(items=[], total=0)
                windows = await asyncio.to_thread(store.get_paper_subscriptions, user_id)
            except HTTPException:
                # Anonymous device-token holders aren't users — no
                # subscription, no visibility. Returning the shared
                # ledger here would re-introduce the leak this PR fixes.
                return TradeListResponse(items=[], total=0)
            except Exception:
                log.exception("/api/trades: subscription-window lookup failed")
                return TradeListResponse(items=[], total=0)
            visible = filter_trades_for_user(
                ledger_rows, windows, include_open=include_open,
            )
        else:
            # Legacy fallback for bootstrap paths that didn't pass the
            # auth resolvers — behaves as pre-2026-05-23 (shared ledger).
            visible = ledger_rows

        total = len(visible)
        page = visible[offset : offset + limit]
        items = [TradeRecord(**row) for row in page]
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
        # 2b. Zero the RiskManager's in-memory daily state.  Trade-tab's
        # ``daily_pnl_usd`` is sourced from ``rm.daily_realised_pnl_usd``
        # (``src/main.py``) — without this wipe, the dashboard kept
        # yesterday's number until UTC midnight even after a reset.
        rm = getattr(engine, "_risk_manager", None)
        if rm is not None and hasattr(rm, "reset_daily"):
            try:
                rm.reset_daily()
            except Exception:
                log.exception("paper reset: risk_manager.reset_daily failed")
        # 3. Wipe daily buckets.  Per-user books on → clear every
        # ``paper:<uid>`` bucket via the aggregate reset; otherwise the
        # single shared ``paper`` bucket.
        from src.auto_trade import pnl_history as _pnl_history
        if hasattr(om, "positions_for_user"):
            buckets_cleared = await asyncio.to_thread(
                _pnl_history.reset_aggregate, "paper"
            )
        else:
            buckets_cleared = await asyncio.to_thread(
                _pnl_history.reset_mode, "paper"
            )
        # 4. Archive per-trade rows (preferred over destructive delete —
        # historical data remains queryable for the owner).
        try:
            from src.auto_trade import trade_records as _trade_records
            trades_archived = await asyncio.to_thread(_trade_records.archive_all)
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

    # ---- Per-user paper visibility reset (user-callable) ----
    #
    # Companion to the owner-only ``/reset`` above. Where ``/reset`` wipes
    # the engine's shared paper ledger (and is gated on having no open
    # engine positions), this endpoint operates only on the caller's
    # ``user_paper_subscriptions`` row: closes the active subscription
    # (if any) and opens a fresh one stamped to NOW. The engine ledger
    # is untouched. From the user's perspective, ``GET /api/trades``
    # immediately returns an empty page until new trades close inside
    # the new window.
    #
    # Why this is user-callable (vs owner-only like /reset): clearing
    # one user's visibility window can't affect any other user, and
    # can't corrupt engine state. It's the same conceptual operation as
    # logging out + back in, which the user can already do.

    if _per_user_enabled:
        @app.post(
            "/api/auto-mode/paper/reset-mine",
            response_model=PaperResetMineResponse,
            tags=["auto-mode"],
            dependencies=[Depends(auth)],
        )
        async def paper_reset_mine(
            identity: Any = Depends(_user_claims_dep),
        ) -> PaperResetMineResponse:
            """Carve a fresh per-user paper visibility window for the caller.

            Idempotent in the sense that calling twice produces a new
            started_at each time — there's no useful "already-clean"
            state to short-circuit on. The user might genuinely want a
            second reset (e.g. accidentally placed a paper trade and
            wants to retry).
            """
            try:
                user_id = resolve_user_id(identity)  # type: ignore[misc]
            except HTTPException:
                # Anonymous device tokens can't own a subscription window.
                raise
            from .user_overrides import get_singleton
            store = get_singleton()
            if store is None:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="user overrides store not initialised",
                )
            new_started_at = await asyncio.to_thread(
                store.reset_paper_subscription, user_id
            )
            log.info(
                "paper_reset_mine user_id={} new_started_at={}",
                user_id, new_started_at,
            )
            return PaperResetMineResponse(
                ok=True, new_started_at=new_started_at,
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
