"""Admin manual tier grant — owner-only comp for testers/influencers.

``POST /api/admin/grant-tier`` lets the owner (via the ops dashboard
control plane) manually set a user's subscription tier without a Play
Billing purchase — e.g. comping a tester or an influencer, or a
goodwill upgrade. Every grant carries an expiry (``duration_days``,
default 30); there is no permanent comp via this endpoint — extend by
calling again before expiry. ``tier=free`` revokes any active grant
immediately.

Reuses the exact same ``UserStore.aset_tier`` write path as the Play
Billing verify flow and the billing webhook (``/internal/billing/grant``)
— this is not a parallel entitlement system, just a different caller
writing through the one source of truth (the ``users`` table).

``GET /api/admin/users/lookup`` is the companion read endpoint the ops
UI calls first to show the user's current tier before granting.

Owner-gated (Bearer token / Firebase owner tier) — same dependency as
every other admin/control route (``owner_required``). Not a hot-path
call (low-frequency, owner-initiated from the ops UI), so no
caching/invalidation-gating is needed per Cost Discipline.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from fastapi import Depends, FastAPI, HTTPException, Query, status

from src.utils import get_logger

from .schemas import (
    AdminGrantTierRequest,
    AdminGrantTierResponse,
    AdminUserLookupResponse,
)

log = get_logger("api.admin_grant_route")


def register(
    app: FastAPI,
    *,
    user_store: Any,
    owner_required: Callable,
) -> None:
    """Register the admin user-lookup + tier-grant routes on the given app."""

    @app.get(
        "/api/admin/users/lookup",
        response_model=AdminUserLookupResponse,
        tags=["admin"],
        dependencies=[Depends(owner_required)],
    )
    async def admin_user_lookup(
        phone: str = Query(..., min_length=8, max_length=18),
    ) -> AdminUserLookupResponse:
        if user_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="user store not configured",
            )
        user = await user_store.aget_by_phone(phone)
        if user is None:
            raise HTTPException(
                status_code=404, detail=f"no user with phone {phone}"
            )
        return AdminUserLookupResponse(
            user_id=user.user_id,
            phone=user.phone_e164,
            tier=user.tier,
            paid_until=user.paid_until.isoformat() if user.paid_until else None,
            display_name=user.display_name,
            onboarded=user.onboarded_at is not None,
        )

    @app.post(
        "/api/admin/grant-tier",
        response_model=AdminGrantTierResponse,
        tags=["admin"],
        dependencies=[Depends(owner_required)],
    )
    async def admin_grant_tier(
        req: AdminGrantTierRequest,
    ) -> AdminGrantTierResponse:
        if user_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="user store not configured",
            )
        # Manual comps only ever target an existing, already-signed-up
        # user — unlike the billing webhook (which legitimately pre-pays
        # a tier before first OTP for an invited tester), the owner
        # grants through the ops UI after looking the user up, so a 404
        # on an unrecognised phone is the right signal (a typo), not a
        # valid pre-pay-before-signup case.
        user = await user_store.aget_by_phone(req.phone)
        if user is None:
            raise HTTPException(
                status_code=404, detail=f"no user with phone {req.phone}"
            )

        paid_until = (
            None
            if req.tier == "free"
            else datetime.now(timezone.utc) + timedelta(days=req.duration_days)
        )
        updated = await user_store.aset_tier(
            user.user_id, tier=req.tier, paid_until=paid_until,
        )
        log.info(
            "admin_grant_tier: user_id={} phone={} tier={} paid_until={} reason={!r}",
            updated.user_id,
            updated.phone_e164,
            updated.tier,
            paid_until.isoformat() if paid_until else None,
            req.reason,
        )
        return AdminGrantTierResponse(
            ok=True,
            user_id=updated.user_id,
            phone=updated.phone_e164,
            tier=updated.tier,
            paid_until=updated.paid_until.isoformat() if updated.paid_until else None,
        )
