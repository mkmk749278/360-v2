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

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status

from src.utils import get_logger

from .schemas import (
    AdminAutoTradeEnableRequest,
    AdminAutoTradeEnableResponse,
    AdminExitMechanismRequest,
    AdminExitMechanismResponse,
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
    user_overrides: Any = None,
) -> None:
    """Register the admin user-lookup + tier-grant routes on the given app."""

    @app.post(
        "/api/admin/users/exit-mechanism",
        response_model=AdminExitMechanismResponse,
        tags=["admin"],
        dependencies=[Depends(owner_required)],
    )
    async def admin_set_exit_mechanism(
        req: AdminExitMechanismRequest,
    ) -> AdminExitMechanismResponse:
        """Opt one account into (or out of) the live trail governor.

        The owner-facing path for a setting that otherwise has none: the
        Lumin app has no control for ``exit_mechanism``, so without this
        endpoint the column could only be written by hand-minting the
        account holder's own Firebase token.

        Two things it deliberately does:

        * **Reads the value back from the store** rather than echoing the
          request.  ``_coerce_auto_trade`` silently drops an unrecognised
          mechanism, so an echo would report success for a write that did
          not happen.
        * **Publishes the engine-wide master switch beside it.**  The
          per-user value alone changes nothing, and an operator who sets one
          without the other must not read ``ok: true`` as "it is running".
        """
        if user_overrides is None or user_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        if (req.phone is None) == (req.firebase_uid is None):
            raise HTTPException(
                status_code=422,
                detail="provide exactly one of 'phone' or 'firebase_uid'",
            )
        if req.phone is not None:
            user = await user_store.aget_by_phone(req.phone)
        else:
            user = await asyncio.to_thread(
                user_store.get_by_firebase_uid, req.firebase_uid
            )
        if user is None:
            raise HTTPException(
                status_code=404,
                detail=f"no user matching {req.phone or req.firebase_uid}",
            )

        await user_overrides.aupdate_auto_trade(
            int(user.user_id), {"exit_mechanism": req.exit_mechanism}
        )
        stored = await user_overrides.aget_auto_trade(int(user.user_id))
        effective = str(stored.get("exit_mechanism") or "default")

        governor_on = False
        try:
            from src import runtime_tunables as _rt

            governor_on = bool(_rt.get("trail_governor_enabled"))
        except Exception:  # pragma: no cover — tunables optional
            from config import TRAIL_GOVERNOR_ENABLED as _cfg

            governor_on = bool(_cfg)

        log.info(
            "admin_set_exit_mechanism: user_id={} phone={} requested={} "
            "stored={} governor_enabled={} reason={!r}",
            user.user_id, getattr(user, "phone_e164", None),
            req.exit_mechanism, effective, governor_on, req.reason,
        )
        return AdminExitMechanismResponse(
            ok=(effective == req.exit_mechanism),
            user_id=int(user.user_id),
            phone=getattr(user, "phone_e164", None),
            exit_mechanism=effective,
            governor_enabled=governor_on,
        )

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

    @app.post(
        "/api/admin/users/auto-trade-enable",
        response_model=AdminAutoTradeEnableResponse,
        tags=["admin"],
        dependencies=[Depends(owner_required)],
    )
    async def admin_auto_trade_enable(
        req: AdminAutoTradeEnableRequest,
    ) -> AdminAutoTradeEnableResponse:
        """Operator re-enable (or manual disable) of a user's auto-trade.

        The per-user circuit breaker persists its disable in Firestore
        (``kill_switch.disable_user``), which survives restarts by design
        — but the documented recovery verb (``/enable_user``) was never
        implemented on any surface, so a tripped user (e.g. the -4411
        Futures-agreement storm pre-#740) stayed disabled with the app
        showing "Paused by a safety check — email support" and support
        having no switch to flip.  This is that switch: same
        ``kill_switch`` write path the breaker uses, owner-gated,
        audited via the engine log, response read back from Firestore.

        The breaker's in-memory rejection window (5 min) is engine-local
        and self-expires, so no engine-side reset is needed — a
        re-enabled user only re-trips on NEW qualifying failures.
        """
        from src.execution import kill_switch as _kill_switch

        if (req.phone is None) == (req.firebase_uid is None):
            raise HTTPException(
                status_code=422,
                detail="provide exactly one of 'phone' or 'firebase_uid'",
            )
        if not _kill_switch.is_initialised():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="kill switch not initialised (no Firestore in this "
                "process — check GCP env)",
            )

        phone: Optional[str] = None
        firebase_uid = req.firebase_uid
        if req.phone is not None:
            if user_store is None:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="user store not configured",
                )
            user = await user_store.aget_by_phone(req.phone)
            if user is None:
                raise HTTPException(
                    status_code=404, detail=f"no user with phone {req.phone}"
                )
            phone = user.phone_e164
            firebase_uid = getattr(user, "firebase_uid", None)
            if not firebase_uid:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"user {req.phone} has no firebase_uid yet (pre-"
                        "migration row) — pass firebase_uid directly"
                    ),
                )

        ks = _kill_switch.get_client()
        if firebase_uid is None:  # unreachable: XOR check + 409 above
            raise HTTPException(
                status_code=422, detail="firebase_uid could not be resolved"
            )
        if req.enabled:
            await asyncio.to_thread(ks.enable_user, firebase_uid)
        else:
            await asyncio.to_thread(
                ks.disable_user, firebase_uid,
                req.reason or "manual operator disable",
            )
        # Engine-truth doctrine: read the flag back rather than echoing
        # the request (also proves the Firestore write landed).
        disabled_now = bool(
            await asyncio.to_thread(ks.is_user_disabled, firebase_uid)
        )
        log.warning(
            "admin_auto_trade_enable: uid={} phone={} enabled={} reason={!r} "
            "read_back_disabled={}",
            firebase_uid, phone, req.enabled, req.reason, disabled_now,
        )
        return AdminAutoTradeEnableResponse(
            ok=(disabled_now is (not req.enabled)),
            firebase_uid=firebase_uid,
            phone=phone,
            auto_trade_disabled=disabled_now,
        )
