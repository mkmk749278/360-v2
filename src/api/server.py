"""FastAPI app + uvicorn launcher.

The app instance is built lazily by ``build_app(engine)`` so tests can
construct one against a stub engine without booting the runtime.  In
production, ``serve_api(engine)`` is awaited as a long-running asyncio
task spawned from ``Bootstrap.launch_runtime_tasks``.

Auth model: every protected endpoint accepts a JWT in the Authorization
header.  The app's first request mints an anonymous JWT via
``/api/auth/anonymous``; tokens are silently refreshed via
``/api/auth/refresh`` before expiry.  When the JWT secret is rotated
server-side every existing JWT becomes invalid; clients catch the
resulting 401 and silently re-mint.

Admin escape hatch: when ``API_ALLOW_STATIC_TOKEN=true`` AND a static
``API_AUTH_TOKEN`` is configured, that exact bearer string is accepted
as if it were a valid JWT.  This is for owner / CTE debugging only —
clients don't use it.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.utils import get_logger

from .auth import (
    ALL_ACCESS_TIER,
    OWNER_TIER,
    AuthError,
    TokenClaims,
    decode_token,
    mint_token,
    mint_user_token,
    refresh_token,
)
from .billing_callback import SIGNATURE_HEADER, BillingWebhookVerifier
from .otp import IssueStatus, OtpStore, VerifyStatus
from .otp_delivery import (
    DeliveryStatus,
    LogOnlyOtpProvider,
    OtpDeliveryProvider,
)
from .schemas import (
    ActivityResponse,
    AgentsResponse,
    AutoModeChangeRequest,
    AutoModeChangeResponse,
    AutoModeStatus,
    AutoTradeSettings,
    BillingGrantRequest,
    BillingGrantResponse,
    HealthResponse,
    OtpRequest,
    OtpRequestResponse,
    OtpVerify,
    PnlHistoryResponse,
    PositionsResponse,
    PretpSettings,
    ProfileResponse,
    ProfileUpdate,
    PulseSnapshot,
    SignalDetail,
    SignalsResponse,
    TickersResponse,
    UserAutoTradeSettings,
    UserPretpSettings,
)
from src import user_settings as _user_settings
from .user_overrides import UserOverridesStore
from .snapshot import (
    build_activity,
    build_agents,
    build_pnl_history,
    build_auto_mode,
    build_positions,
    build_pulse,
    build_signals,
    build_tickers,
)
from .users import UserStore
from src.auto_trade.binance_keys_store import BinanceKeysStore, BinanceKeysStoreError
from src.auto_trade.binance_proxy import BinanceProxyClient, BinanceProxyError
from .schemas import (
    BinanceClosePositionRequest,
    BinanceCloseResponse,
    BinanceEquityResponse,
    BinanceKeysStatusResponse,
    BinanceKeysUploadRequest,
    BinanceKeysVerifyResponse,
    BinanceOrderRequest,
    BinanceOrderResponse,
    BinancePositionResponse,
    BinancePositionsResponse,
)

log = get_logger("api.server")

_API_VERSION = "0.0.2"


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------


class _TokenResponse(BaseModel):
    """JSON body returned by every mint / refresh path.

    ``needs_onboarding`` is true when the caller doesn't have a
    completed profile yet (``users.onboarded_at IS NULL``).  The app
    reads this and pushes ``SignupPage`` instead of ``NavShell`` on the
    next route decision.  Always true for anonymous / device-id tokens
    (no profile = needs onboarding), but the anonymous flow is debug-
    only post-Phase-2 so the practical signal is on user-id tokens.
    """

    token: str
    tier: str
    sub: str
    exp_seconds: int
    needs_onboarding: bool = True


class _RefreshRequest(BaseModel):
    token: str


def _compute_needs_onboarding(
    sub: str, user_store: Optional["UserStore"]
) -> bool:
    """Resolve ``needs_onboarding`` for a JWT subject.

    ``user-<id>`` subjects consult the UserStore; everything else
    (``device-*`` anonymous, missing store) defaults to True because
    they have no profile to onboard from.  Errors fall through to True
    rather than 500 — the signal is non-load-bearing for protected
    endpoints (only routes the signup page).
    """
    if user_store is None or not sub.startswith("user-"):
        return True
    try:
        uid = int(sub[len("user-"):])
    except ValueError:
        return True
    user = user_store.get_by_id(uid)
    if user is None:
        return True
    return user.needs_onboarding


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------


_bearer = HTTPBearer(auto_error=False)


def _make_auth_dep(
    jwt_secret: str,
    static_token: str,
    allow_static: bool,
    *,
    required_tier: Optional[str] = None,
):
    """Return a FastAPI dependency that verifies a bearer credential.

    ``required_tier`` (optional): if set, JWT-authed requests must carry
    that tier in their claims or 403.  Static-token bypass is treated as
    owner — an admin presenting the configured static token can hit any
    endpoint regardless of ``required_tier``.

    Read endpoints use this with ``required_tier=None`` (any auth OK);
    write endpoints (settings PUT, auto-mode POST) use
    ``required_tier=OWNER_TIER`` so testers' anonymous JWTs can read
    state but can't mutate engine config.
    """

    async def _verify(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    ) -> None:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="missing bearer token",
            )
        presented = credentials.credentials
        # Admin escape hatch — static token bypass is treated as the
        # highest-privilege caller (owner).  Skips both JWT verification
        # and the tier check below.
        if allow_static and static_token and presented == static_token:
            return
        # Standard path: verify the JWT signature + expiry.
        try:
            claims = decode_token(presented, secret=jwt_secret)
        except AuthError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            )
        # Tier check (only enforced when required_tier is set).
        if required_tier is not None and claims.tier != required_tier:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"insufficient privilege: endpoint requires "
                    f"tier={required_tier!r}, token has tier={claims.tier!r}"
                ),
            )
        return

    return _verify


def _make_user_claims_dep(
    jwt_secret: str,
    static_token: str,
    allow_static: bool,
):
    """Dependency that resolves to the caller's :class:`TokenClaims`.

    Differs from :func:`_make_auth_dep` in that the endpoint receives
    the decoded claims (or None for static-token bypass — which is
    treated as owner / user_id=1 by the endpoint).  Used by per-user
    endpoints (profile, future per-user settings + PnL) that need
    ``sub`` to look up the right user row.
    """

    async def _resolve(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    ) -> Optional[TokenClaims]:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="missing bearer token",
            )
        presented = credentials.credentials
        if allow_static and static_token and presented == static_token:
            return None  # owner / user_id=1
        try:
            return decode_token(presented, secret=jwt_secret)
        except AuthError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            )

    return _resolve


def _resolve_user_id(
    claims: Optional[TokenClaims], *, owner_id: int = 1
) -> int:
    """Map JWT claims → user_id.  Static-token bypass → owner_id.

    Anonymous device-id JWTs raise 404 — they aren't users, they can't
    have a profile.  The signup flow happens AFTER OTP verify so the
    only legitimate caller here is a user-id JWT (or static-token).
    """
    if claims is None:
        return owner_id
    sub = claims.sub
    if not sub.startswith("user-"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "no profile for anonymous device tokens — "
                "sign in with phone first"
            ),
        )
    try:
        return int(sub[len("user-"):])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"invalid user id in token subject: {sub!r}",
        )


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


def build_app(
    engine: Any,
    *,
    jwt_secret: str = "",
    static_token: str = "",
    allow_static: bool = True,
    cors_origins: Optional[List[str]] = None,
    user_store: Optional[UserStore] = None,
    user_overrides: Optional[UserOverridesStore] = None,
    otp_store: Optional[OtpStore] = None,
    otp_delivery: Optional[OtpDeliveryProvider] = None,
    billing_verifier: Optional[BillingWebhookVerifier] = None,
    binance_keys_store: Optional[BinanceKeysStore] = None,
    binance_proxy: Optional[BinanceProxyClient] = None,
) -> FastAPI:
    """Build the FastAPI app bound to a live engine instance.

    Phase-2 additions:

    * ``user_store`` (UserStore): SQLite-backed user registry.  When
      ``None``, the OTP and billing endpoints return 503 — the
      pre-Phase-2 endpoints continue to work normally.
    * ``otp_store`` (OtpStore): in-memory OTP issuer/verifier; auto-
      created when ``user_store`` is set and this is ``None``.
    * ``otp_delivery`` (OtpDeliveryProvider): defaults to LogOnly when
      not provided — owner-mediated forwarding for the closed beta.
    * ``billing_verifier`` (BillingWebhookVerifier): when ``None`` or
      ``not is_configured()``, ``/internal/billing/grant`` returns 503.

    Phase-4 (auto-trade VPS proxy):

    * ``binance_keys_store`` (BinanceKeysStore): per-user encrypted
      Binance credentials.  Required for the ``/api/auto-trade/*``
      endpoints — when ``None`` they return 503.
    * ``binance_proxy`` (BinanceProxyClient): server-side signed
      Binance Futures client.  Auto-created when ``binance_keys_store``
      is set and this is ``None``.
    """
    app = FastAPI(
        title="360 Crypto Eye API",
        version=_API_VERSION,
        description="HTTP adapter for the Lumin app.",
    )
    app.state.engine = engine
    app.state.boot_monotonic = time.monotonic()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins or ["*"],
        allow_credentials=False,
        # POST/PUT include the OTP + billing-grant endpoints; OPTIONS is
        # autoplay'd by browsers for any non-trivial CORS preflight.
        allow_methods=["GET", "POST", "PUT", "OPTIONS"],
        allow_headers=["*"],
    )

    auth = _make_auth_dep(jwt_secret, static_token, allow_static)
    # Owner-tier dep — enforced on write endpoints so testers' anonymous
    # JWTs can READ state but can't mutate engine config (mode flip,
    # settings PUT).  Static-token bypass still works for admin tooling.
    owner_required = _make_auth_dep(
        jwt_secret, static_token, allow_static, required_tier=OWNER_TIER,
    )
    # User-claims dep — for per-user endpoints (profile, future per-user
    # settings + PnL).  Returns the decoded JWT claims; static-token
    # bypass returns None (caller treats as owner / user_id=1).
    user_claims = _make_user_claims_dep(jwt_secret, static_token, allow_static)

    # Auto-construct the OTP defaults so callers (and existing tests)
    # don't have to plumb every Phase 2 dep through.  When ``user_store``
    # is None we leave them as None too — the endpoints will 503.
    if user_store is not None and otp_store is None:
        otp_store = OtpStore()
    if user_store is not None and otp_delivery is None:
        otp_delivery = LogOnlyOtpProvider()
    # Auto-construct the Binance proxy client once the keys store is
    # provided so callers don't have to wire both in lock-step.
    if binance_keys_store is not None and binance_proxy is None:
        binance_proxy = BinanceProxyClient(binance_keys_store)
    # Stash on app.state so the shutdown hook can close the aiohttp
    # session cleanly (avoid leaked-connection warnings on reload).
    app.state.binance_proxy = binance_proxy

    @app.on_event("shutdown")
    async def _shutdown_binance_proxy() -> None:  # pragma: no cover — uvicorn hook
        proxy = getattr(app.state, "binance_proxy", None)
        if proxy is not None:
            await proxy.close()

    def _require_binance_proxy() -> BinanceProxyClient:
        if binance_keys_store is None or binance_proxy is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "auto-trade proxy not configured: "
                    "set BINANCE_KEY_ENCRYPTION_SECRET and restart"
                ),
            )
        return binance_proxy

    # ---- Health (no auth — used by Docker/k8s probes + first-launch reachability) ----

    @app.get("/api/health", response_model=HealthResponse, tags=["meta"])
    async def health() -> HealthResponse:
        boot = getattr(engine, "_boot_time", 0.0) or 0.0
        uptime = time.monotonic() - boot if boot else 0.0
        return HealthResponse(uptime_seconds=max(0.0, uptime), version=_API_VERSION)

    # ---- Auth endpoints (no auth required to mint; refresh requires a current valid JWT) ----

    @app.post(
        "/api/auth/anonymous",
        response_model=_TokenResponse,
        tags=["auth"],
    )
    async def auth_anonymous() -> _TokenResponse:
        if not jwt_secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="auth not configured: API_JWT_SECRET unset",
            )
        # Every anonymous mint gets a fresh device id and the all-access
        # tier during the testing phase.  Once subscriptions ship, this
        # path will mint tier=free; tier=paid will come from a separate
        # subscription-confirmation endpoint.
        token = mint_token(secret=jwt_secret, tier=ALL_ACCESS_TIER)
        claims = decode_token(token, secret=jwt_secret)
        return _TokenResponse(
            token=token,
            tier=claims.tier,
            sub=claims.sub,
            exp_seconds=int((claims.exp - claims.iat).total_seconds()),
            needs_onboarding=_compute_needs_onboarding(claims.sub, user_store),
        )

    @app.post(
        "/api/auth/refresh",
        response_model=_TokenResponse,
        tags=["auth"],
    )
    async def auth_refresh(req: _RefreshRequest) -> _TokenResponse:
        if not jwt_secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="auth not configured",
            )
        try:
            new_token = refresh_token(req.token, secret=jwt_secret)
        except AuthError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            )
        claims = decode_token(new_token, secret=jwt_secret)
        return _TokenResponse(
            token=new_token,
            tier=claims.tier,
            sub=claims.sub,
            exp_seconds=int((claims.exp - claims.iat).total_seconds()),
            needs_onboarding=_compute_needs_onboarding(claims.sub, user_store),
        )

    # ---- Phone OTP auth (Phase 2) ----

    @app.post(
        "/api/auth/request-otp",
        response_model=OtpRequestResponse,
        tags=["auth"],
    )
    async def auth_request_otp(req: OtpRequest) -> OtpRequestResponse:
        if user_store is None or otp_store is None or otp_delivery is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="phone auth not configured",
            )
        # Issue first — burns the rate-limit slot before we hit the
        # paid delivery channel, so an attacker can't burn the WhatsApp
        # balance by triggering rate-limit faster than they hit it.
        result = otp_store.issue(req.phone)
        if result.status is IssueStatus.RATE_LIMITED:
            # 429 + Retry-After lets the app render a countdown.
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="too many OTP requests; try again later",
                headers={"Retry-After": str(result.retry_after_seconds)},
            )
        # status==OK → forward to delivery provider chain.
        assert result.code is not None
        delivery = await otp_delivery.send(req.phone, result.code)
        if delivery.status is DeliveryStatus.PROVIDER_ERROR:
            log.warning(
                "OTP delivery error for {}: {}", req.phone, delivery.detail,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="failed to deliver OTP",
            )
        if delivery.status is DeliveryStatus.UNSUPPORTED_CHANNEL:
            # No fallback configured (or fallback also unsupported).
            # Caller can't reach the user — return a clear error rather
            # than confirm "OTP sent" they'll never receive.
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="recipient unreachable on configured channels",
            )
        return OtpRequestResponse(
            channel_used=delivery.channel_used,
            expires_in_seconds=result.expires_in_seconds,
        )

    @app.post(
        "/api/auth/verify-otp",
        response_model=_TokenResponse,
        tags=["auth"],
    )
    async def auth_verify_otp(req: OtpVerify) -> _TokenResponse:
        if user_store is None or otp_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="phone auth not configured",
            )
        if not jwt_secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="auth not configured: API_JWT_SECRET unset",
            )
        verify = otp_store.verify(req.phone, req.code)
        if verify.status is not VerifyStatus.OK:
            # 401 (not 403): "this credential isn't valid for any user"
            # — the same code never works as a generic auth failure.
            detail_map = {
                VerifyStatus.NO_RECORD: "no pending OTP for this phone",
                VerifyStatus.EXPIRED: "OTP expired; request a new one",
                VerifyStatus.WRONG_CODE: "incorrect OTP",
                VerifyStatus.TOO_MANY_ATTEMPTS: (
                    "too many incorrect attempts; request a new OTP"
                ),
            }
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=detail_map.get(verify.status, "OTP verification failed"),
            )
        # Get-or-create.  First-time signin → tier=free; returning user
        # keeps their existing tier (paid, owner, etc.).
        user = user_store.get_or_create_by_phone(req.phone)
        token = mint_user_token(
            secret=jwt_secret,
            user_id=user.user_id,
            tier=user.tier,
            paid_until=user.paid_until,
        )
        claims = decode_token(token, secret=jwt_secret)
        return _TokenResponse(
            token=token,
            tier=claims.tier,
            sub=claims.sub,
            exp_seconds=int((claims.exp - claims.iat).total_seconds()),
            needs_onboarding=user.needs_onboarding,
        )

    # ---- Billing webhook (Phase 2; bot/billing-platform → engine) ----

    @app.post(
        "/internal/billing/grant",
        response_model=BillingGrantResponse,
        tags=["internal"],
    )
    async def billing_grant(request: Request) -> BillingGrantResponse:
        # HMAC verifies the RAW body bytes.  Pydantic parses afterwards.
        if user_store is None or billing_verifier is None or not billing_verifier.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="billing webhook not configured",
            )
        raw = await request.body()
        presented = request.headers.get(SIGNATURE_HEADER)
        result = billing_verifier.verify(raw, presented)
        if not result.ok:
            log.warning("Billing webhook rejected: {}", result.detail)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"signature verification failed: {result.detail}",
            )
        # Parse the body now that it's authenticated.
        try:
            payload = BillingGrantRequest.model_validate_json(raw)
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"invalid grant body: {exc}",
            )
        # Get-or-create the user.  The bot legitimately reaches us
        # before the user has signed in via OTP — pre-paying a tier on
        # behalf of an invited tester is a valid flow.
        user = user_store.get_or_create_by_phone(payload.phone)
        paid_until_dt = None
        if payload.paid_until_iso is not None:
            try:
                paid_until_dt = datetime.fromisoformat(payload.paid_until_iso)
            except ValueError as exc:
                raise HTTPException(
                    status_code=422,
                    detail=f"paid_until_iso not valid ISO-8601: {exc}",
                )
        try:
            updated = user_store.set_tier(
                user.user_id,
                tier=payload.tier,
                paid_until=paid_until_dt,
            )
        except LookupError as exc:  # pragma: no cover — get_or_create above
            raise HTTPException(status_code=404, detail=str(exc))
        return BillingGrantResponse(
            ok=True,
            user_id=updated.user_id,
            tier=updated.tier,
        )

    # ---- Profile (Phase 3 — per-user expansion) ----

    def _profile_response(user) -> ProfileResponse:  # type: ignore[no-untyped-def]
        return ProfileResponse(
            user_id=user.user_id,
            phone_e164=user.phone_e164,
            tier=user.tier,
            paid_until=(
                user.paid_until.isoformat() if user.paid_until else None
            ),
            display_name=user.display_name,
            country_code=user.country_code,
            timezone=user.timezone,
            currency=user.currency,
            terms_accepted_at=(
                user.terms_accepted_at.isoformat()
                if user.terms_accepted_at else None
            ),
            onboarded_at=(
                user.onboarded_at.isoformat() if user.onboarded_at else None
            ),
            needs_onboarding=user.needs_onboarding,
        )

    @app.get(
        "/api/profile",
        response_model=ProfileResponse,
        tags=["profile"],
    )
    async def profile_get(
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> ProfileResponse:
        if user_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="user store not configured",
            )
        uid = _resolve_user_id(claims)
        user = user_store.get_by_id(uid)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user_id={uid} not found",
            )
        return _profile_response(user)

    @app.put(
        "/api/profile",
        response_model=ProfileResponse,
        tags=["profile"],
    )
    async def profile_put(
        body: ProfileUpdate,
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> ProfileResponse:
        if user_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="user store not configured",
            )
        uid = _resolve_user_id(claims)
        try:
            updated = user_store.update_profile(
                uid,
                display_name=body.display_name,
                country_code=body.country_code,
                timezone=body.timezone,
                currency=body.currency,
                accept_terms=body.accept_terms,
            )
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        return _profile_response(updated)

    # ---- Pulse ----

    @app.get(
        "/api/pulse",
        response_model=PulseSnapshot,
        tags=["pulse"],
        dependencies=[Depends(auth)],
    )
    async def pulse() -> PulseSnapshot:
        return build_pulse(engine)

    @app.get(
        "/api/pulse/tickers",
        response_model=TickersResponse,
        tags=["pulse"],
        dependencies=[Depends(auth)],
    )
    async def pulse_tickers() -> TickersResponse:
        items = build_tickers(engine)
        return TickersResponse(items=items, total=len(items))

    # ---- Signals ----

    @app.get(
        "/api/signals",
        response_model=SignalsResponse,
        tags=["signals"],
        dependencies=[Depends(auth)],
    )
    async def signals(
        status: str = Query("all", pattern="^(all|open|closed)$"),
        limit: int = Query(50, ge=1, le=500),
        setup_class: Optional[str] = Query(
            None,
            description="Filter to one evaluator's signals (e.g. SR_FLIP_RETEST)",
        ),
    ) -> SignalsResponse:
        items = build_signals(
            engine,
            status=status,
            limit=limit,
            setup_class=setup_class,
        )
        return SignalsResponse(items=items, total=len(items))

    @app.get(
        "/api/signals/{signal_id}",
        response_model=SignalDetail,
        tags=["signals"],
        dependencies=[Depends(auth)],
    )
    async def signal_detail(signal_id: str) -> SignalDetail:
        # Search all known signals — small cost (≤500 history + active).
        items = build_signals(engine, status="all", limit=1000)
        for it in items:
            if it.signal_id == signal_id:
                return it
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"signal {signal_id!r} not found",
        )

    # ---- Positions ----

    @app.get(
        "/api/positions",
        response_model=PositionsResponse,
        tags=["positions"],
        dependencies=[Depends(auth)],
    )
    async def positions() -> PositionsResponse:
        # Defensive logging (2026-05-08): the Trade tab fans out to three
        # endpoints (auto-mode + positions + activity) and a single 500 on
        # any of them shows the user "Could not load Trade state" with
        # zero diagnostic context.  Wrapping each endpoint catches the
        # exception, logs a full traceback for the VPS-side diagnosis,
        # and returns an empty list so the rest of the page can render.
        try:
            items = build_positions(engine)
        except Exception:
            log.exception("/api/positions failed — returning empty list")
            items = []
        return PositionsResponse(items=items, total=len(items))

    # ---- Activity ----

    @app.get(
        "/api/activity",
        response_model=ActivityResponse,
        tags=["activity"],
        dependencies=[Depends(auth)],
    )
    async def activity(
        limit: int = Query(50, ge=1, le=500),
        setup_class: Optional[str] = Query(
            None,
            description="Filter to one evaluator's lifecycle events",
        ),
    ) -> ActivityResponse:
        try:
            items = build_activity(engine, limit=limit, setup_class=setup_class)
        except Exception:
            log.exception("/api/activity failed — returning empty list")
            items = []
        return ActivityResponse(items=items, total=len(items))

    # ---- Auto-mode ----

    @app.get(
        "/api/auto-mode",
        response_model=AutoModeStatus,
        tags=["auto-mode"],
        dependencies=[Depends(auth)],
    )
    async def auto_mode_get() -> AutoModeStatus:
        try:
            return build_auto_mode(engine)
        except Exception:
            log.exception(
                "/api/auto-mode failed — returning safe default off-mode status"
            )
            # Fail-soft: return a synthetic off-mode status so the Trade
            # tab renders the off-mode card instead of a 500.  The
            # subscriber sees a valid (if empty) page; we get the full
            # traceback in logs for diagnosis.
            return AutoModeStatus(
                mode="off",
                open_positions=0,
                daily_pnl_usd=0.0,
                daily_loss_pct=0.0,
                daily_kill_tripped=False,
                manual_paused=False,
                current_equity_usd=0.0,
            )

    @app.get(
        "/api/pnl/history",
        response_model=PnlHistoryResponse,
        tags=["pulse"],
        dependencies=[Depends(auth)],
    )
    async def pnl_history_get(
        days: int = Query(30, ge=1, le=365),
        mode: Optional[str] = Query(
            None,
            pattern="^(off|paper|live)$",
            description="Override the engine's current mode — useful for "
            "viewing the other ledger (e.g. paper history while in live).",
        ),
    ) -> PnlHistoryResponse:
        payload = build_pnl_history(engine, mode=mode, days=days)
        return PnlHistoryResponse(**payload)

    @app.post(
        "/api/auto-mode",
        response_model=AutoModeChangeResponse,
        tags=["auto-mode"],
        dependencies=[Depends(owner_required)],
    )
    async def auto_mode_set(req: AutoModeChangeRequest) -> AutoModeChangeResponse:
        ok, msg = engine.set_auto_execution_mode(req.mode)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=msg,
            )
        return AutoModeChangeResponse(
            success=True,
            message=msg,
            mode=req.mode,
        )

    # ---- Settings: Pre-TP page ----

    def _build_pretp_view() -> PretpSettings:
        """Compose the engine's effective Pre-TP view: user overrides where
        set, config defaults otherwise.  Mirrors what the app needs to
        render the page in its current state — no separate "defaults" call."""
        from config import (
            PRE_TP_ATR_MULTIPLIER,
            PRE_TP_ENABLED,
            PRE_TP_FEE_FLOOR_PCT,
            PRE_TP_MAX_AGE_SEC,
            PRE_TP_MIN_AGE_SEC,
            PRE_TP_SETUP_BLACKLIST,
            PRE_TP_THRESHOLD_PCT,
        )
        stored = _user_settings.get_pretp()
        # Resolve each field — user-set if present, else config default.
        return PretpSettings(
            enabled=stored.get("enabled", PRE_TP_ENABLED),
            regime_allowlist=sorted(_user_settings.pretp_regime_allowlist()),
            setup_allowlist=stored.get(
                "setup_allowlist",
                # Engine default exposes a blacklist; the UI is allowlist-shaped.
                # Until the setup wiring lands, return None so the app shows
                # "use engine default" rather than a derived list that would
                # diverge from the active blacklist on the next config change.
                None,
            ),
            threshold_pct=stored.get("threshold_pct", PRE_TP_THRESHOLD_PCT),
            atr_multiplier=stored.get("atr_multiplier", PRE_TP_ATR_MULTIPLIER),
            fee_floor_pct=stored.get("fee_floor_pct", PRE_TP_FEE_FLOOR_PCT),
            min_age_sec=stored.get("min_age_sec", PRE_TP_MIN_AGE_SEC),
            max_age_sec=stored.get("max_age_sec", PRE_TP_MAX_AGE_SEC),
        )

    @app.get(
        "/api/settings/pretp",
        response_model=PretpSettings,
        tags=["settings"],
        dependencies=[Depends(auth)],
    )
    async def pretp_settings_get() -> PretpSettings:
        return _build_pretp_view()

    @app.put(
        "/api/settings/pretp",
        response_model=PretpSettings,
        tags=["settings"],
        dependencies=[Depends(owner_required)],
    )
    async def pretp_settings_put(payload: PretpSettings) -> PretpSettings:
        # ``model_dump(exclude_unset=True)`` gives us only the fields the
        # client actually sent, so a PUT with one field doesn't wipe the
        # others.  Pydantic validation has already enforced types/ranges.
        partial = payload.model_dump(exclude_unset=True)
        if partial:
            _user_settings.update_pretp(partial)
        return _build_pretp_view()

    # ---- Settings: Auto-trade page ----

    def _build_auto_trade_view() -> AutoTradeSettings:
        """Compose the engine's effective auto-trade view: user overrides
        where set, config defaults otherwise.  The ``mode`` field is sourced
        from the engine's live execution state when available so this single
        endpoint can populate the whole settings page."""
        stored = _user_settings.get_auto_trade()
        # Live mode resolution: prefer the engine's actual execution state
        # so the page always shows reality, not just last-saved preference.
        live_mode: Optional[str] = None
        try:
            current = getattr(engine, "auto_execution_mode", None)
            if isinstance(current, str):
                live_mode = current.lower()
        except Exception:
            pass
        return AutoTradeSettings(
            mode=live_mode or stored.get("mode"),
            position_size_pct=_user_settings.auto_trade_position_size_pct(),
            leverage_cap=_user_settings.auto_trade_leverage_cap(),
            max_concurrent_positions=_user_settings.auto_trade_max_concurrent(),
        )

    @app.get(
        "/api/settings/auto-trade",
        response_model=AutoTradeSettings,
        tags=["settings"],
        dependencies=[Depends(auth)],
    )
    async def auto_trade_settings_get() -> AutoTradeSettings:
        return _build_auto_trade_view()

    @app.put(
        "/api/settings/auto-trade",
        response_model=AutoTradeSettings,
        tags=["settings"],
        dependencies=[Depends(owner_required)],
    )
    async def auto_trade_settings_put(payload: AutoTradeSettings) -> AutoTradeSettings:
        partial = payload.model_dump(exclude_unset=True)
        # If ``mode`` is in the partial, route it through the engine's
        # ``set_auto_execution_mode`` (same path as POST /api/auto-mode) so
        # the live state actually changes.  Other fields persist via
        # ``user_settings`` and take effect on the next sizing / risk check.
        mode = partial.pop("mode", None)
        if mode is not None:
            ok, msg = engine.set_auto_execution_mode(mode)
            if not ok:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=msg,
                )
        if partial:
            _user_settings.update_auto_trade(partial)
        return _build_auto_trade_view()

    # ---- Settings: Per-user Pre-TP overrides (Phase 2) ----

    def _build_user_pretp_view(user_id: int) -> UserPretpSettings:
        """Compose per-user Pre-TP view: user-row override where set,
        engine default (config + engine-wide ``user_settings``) otherwise.

        Engine doesn't yet consume per-user values — Phase 3 wires
        execution.  Until then, these reads/writes are pure storage so
        the app's settings UI is functional and we accumulate the data
        we'll need at the user-side execution path.
        """
        defaults = _build_pretp_view()
        if user_overrides is None:
            return UserPretpSettings(
                **defaults.model_dump(),
                using_defaults=True,
            )
        overrides = user_overrides.get_pretp(user_id)
        resolved = defaults.model_dump()
        for key, val in overrides.items():
            resolved[key] = val
        return UserPretpSettings(
            **resolved,
            using_defaults=not bool(overrides),
        )

    @app.get(
        "/api/settings/user/pretp",
        response_model=UserPretpSettings,
        tags=["settings"],
    )
    async def user_pretp_get(
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> UserPretpSettings:
        if user_overrides is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        uid = _resolve_user_id(claims)
        return _build_user_pretp_view(uid)

    @app.put(
        "/api/settings/user/pretp",
        response_model=UserPretpSettings,
        tags=["settings"],
    )
    async def user_pretp_put(
        payload: PretpSettings,
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> UserPretpSettings:
        if user_overrides is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        uid = _resolve_user_id(claims)
        # ``exclude_unset=True`` mirrors the engine-wide endpoint's
        # partial-update semantics — the user can change one toggle
        # without re-sending every other field.
        partial = payload.model_dump(exclude_unset=True)
        if partial:
            user_overrides.update_pretp(uid, partial)
        return _build_user_pretp_view(uid)

    # ---- Settings: Per-user auto-trade overrides (Phase 2) ----

    def _build_user_auto_trade_view(user_id: int) -> UserAutoTradeSettings:
        defaults = _build_auto_trade_view()
        if user_overrides is None:
            return UserAutoTradeSettings(
                **defaults.model_dump(),
                using_defaults=True,
            )
        overrides = user_overrides.get_auto_trade(user_id)
        resolved = defaults.model_dump()
        for key, val in overrides.items():
            resolved[key] = val
        return UserAutoTradeSettings(
            **resolved,
            using_defaults=not bool(overrides),
        )

    @app.get(
        "/api/settings/user/auto-trade",
        response_model=UserAutoTradeSettings,
        tags=["settings"],
    )
    async def user_auto_trade_get(
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> UserAutoTradeSettings:
        if user_overrides is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        uid = _resolve_user_id(claims)
        return _build_user_auto_trade_view(uid)

    @app.put(
        "/api/settings/user/auto-trade",
        response_model=UserAutoTradeSettings,
        tags=["settings"],
    )
    async def user_auto_trade_put(
        payload: AutoTradeSettings,
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> UserAutoTradeSettings:
        if user_overrides is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        uid = _resolve_user_id(claims)
        partial = payload.model_dump(exclude_unset=True)
        # Note: per-user mode flips do NOT trigger the engine-wide
        # ``set_auto_execution_mode`` — the engine continues to operate
        # in whatever mode the operator set via /api/settings/auto-trade.
        # Per-user mode is stored for Phase 3 when the user's app
        # decides whether to fire their own Binance order.
        if partial:
            user_overrides.update_auto_trade(uid, partial)
        return _build_user_auto_trade_view(uid)

    # ---- Agents ----

    @app.get(
        "/api/agents",
        response_model=AgentsResponse,
        tags=["agents"],
        dependencies=[Depends(auth)],
    )
    async def agents() -> AgentsResponse:
        items = build_agents(engine)
        return AgentsResponse(items=items, total=len(items))

    # ------------------------------------------------------------------
    # Auto-trade VPS proxy — per-user Binance keys + signed Futures calls
    # ------------------------------------------------------------------
    #
    # Replaces direct ``api.binance.com`` calls that the Flutter app used
    # to make from ``binance_client.dart``.  Cellular IPs change on every
    # tower handoff and Binance auto-deletes Futures-enabled keys without
    # an IP restriction — so the only viable architecture is to route all
    # signed Binance traffic through the VPS (whose IP is allowlisted).

    def _resolve_proxy_user_id(claims: Optional[TokenClaims]) -> int:
        """Map JWT claims → user_id for proxy endpoints.  Re-uses the
        same resolver as the profile endpoints — anonymous device JWTs
        raise 401 (they can't have Binance keys; sign in first)."""
        if claims is None:
            return 1  # static-token bypass = owner
        sub = claims.sub
        if not sub.startswith("user-"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="anonymous JWT cannot use auto-trade — sign in first",
            )
        try:
            return int(sub.split("-", 1)[1])
        except (IndexError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="malformed JWT subject",
            ) from exc

    def _proxy_error_to_http(exc: BinanceProxyError) -> HTTPException:
        """Translate Binance-side errors into clean HTTP responses for
        the app.  We preserve the upstream code so the app can branch
        UX (e.g. -2015 → "IP not whitelisted, contact admin")."""
        payload = {
            "detail": str(exc).split(" | ", 1)[0],
            "code": exc.code,
            "http_status": exc.http_status,
            "request_ip": exc.request_ip,
        }
        # Map common Binance error classes to sensible HTTP statuses.
        if exc.code in (-2015, -2014, -2008):
            http_status = status.HTTP_401_UNAUTHORIZED  # invalid key / perms / IP
        elif exc.code in (-1021,):
            http_status = status.HTTP_502_BAD_GATEWAY   # clock skew
        elif exc.code == -9001:
            http_status = status.HTTP_404_NOT_FOUND     # no keys stored (our code)
        elif exc.http_status and 400 <= exc.http_status < 500:
            http_status = exc.http_status
        else:
            http_status = status.HTTP_502_BAD_GATEWAY
        return HTTPException(status_code=http_status, detail=payload)

    @app.post(
        "/api/auto-trade/keys",
        response_model=BinanceKeysVerifyResponse,
        tags=["auto-trade"],
    )
    async def auto_trade_keys_upload(
        body: BinanceKeysUploadRequest,
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> BinanceKeysVerifyResponse:
        if binance_keys_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="BINANCE_KEY_ENCRYPTION_SECRET not set",
            )
        proxy = _require_binance_proxy()
        user_id = _resolve_proxy_user_id(claims)
        try:
            binance_keys_store.set(
                user_id,
                body.api_key.strip(),
                body.api_secret.strip(),
                testnet=body.testnet,
            )
        except BinanceKeysStoreError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc),
            ) from exc
        # Verify inline so the app can decide whether to flip auto-trade
        # to Live based on a single round-trip.  On failure the row is
        # kept (user may want to retry verify later) and the error
        # surfaces with full detail.
        try:
            await proxy.verify(user_id)
        except BinanceProxyError as exc:
            return BinanceKeysVerifyResponse(
                verified=False,
                error_code=exc.code,
                error_message=str(exc).split(" | ", 1)[0],
                request_ip_seen_by_binance=exc.request_ip,
            )
        status_dict = binance_keys_store.status(user_id) or {}
        return BinanceKeysVerifyResponse(
            verified=True,
            last_verified_at=status_dict.get("last_verified_at"),
        )

    @app.get(
        "/api/auto-trade/keys/status",
        response_model=BinanceKeysStatusResponse,
        tags=["auto-trade"],
    )
    async def auto_trade_keys_status(
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> BinanceKeysStatusResponse:
        if binance_keys_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="BINANCE_KEY_ENCRYPTION_SECRET not set",
            )
        user_id = _resolve_proxy_user_id(claims)
        info = binance_keys_store.status(user_id)
        if info is None:
            return BinanceKeysStatusResponse(stored=False)
        return BinanceKeysStatusResponse(**info)

    @app.delete(
        "/api/auto-trade/keys",
        tags=["auto-trade"],
    )
    async def auto_trade_keys_clear(
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> Dict[str, Any]:
        if binance_keys_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="BINANCE_KEY_ENCRYPTION_SECRET not set",
            )
        user_id = _resolve_proxy_user_id(claims)
        removed = binance_keys_store.clear(user_id)
        return {"cleared": removed}

    @app.post(
        "/api/auto-trade/keys/verify",
        response_model=BinanceKeysVerifyResponse,
        tags=["auto-trade"],
    )
    async def auto_trade_keys_verify(
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> BinanceKeysVerifyResponse:
        proxy = _require_binance_proxy()
        user_id = _resolve_proxy_user_id(claims)
        try:
            await proxy.verify(user_id)
        except BinanceProxyError as exc:
            return BinanceKeysVerifyResponse(
                verified=False,
                error_code=exc.code,
                error_message=str(exc).split(" | ", 1)[0],
                request_ip_seen_by_binance=exc.request_ip,
            )
        assert binance_keys_store is not None
        info = binance_keys_store.status(user_id) or {}
        return BinanceKeysVerifyResponse(
            verified=True,
            last_verified_at=info.get("last_verified_at"),
        )

    @app.get(
        "/api/auto-trade/equity",
        response_model=BinanceEquityResponse,
        tags=["auto-trade"],
    )
    async def auto_trade_equity(
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> BinanceEquityResponse:
        proxy = _require_binance_proxy()
        user_id = _resolve_proxy_user_id(claims)
        try:
            account = await proxy.get_account(user_id)
        except BinanceProxyError as exc:
            raise _proxy_error_to_http(exc) from exc
        return BinanceEquityResponse(
            total_wallet_balance=account.total_wallet_balance,
            total_unrealized_profit=account.total_unrealized_profit,
            total_margin_balance=account.total_margin_balance,
            available_balance=account.available_balance,
            max_withdraw_amount=account.max_withdraw_amount,
            open_position_count=account.open_position_count,
        )

    @app.get(
        "/api/auto-trade/positions",
        response_model=BinancePositionsResponse,
        tags=["auto-trade"],
    )
    async def auto_trade_positions(
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> BinancePositionsResponse:
        proxy = _require_binance_proxy()
        user_id = _resolve_proxy_user_id(claims)
        try:
            positions = await proxy.get_positions(user_id)
        except BinanceProxyError as exc:
            raise _proxy_error_to_http(exc) from exc
        return BinancePositionsResponse(
            positions=[
                BinancePositionResponse(
                    symbol=p.symbol,
                    side=p.side,  # type: ignore[arg-type]
                    position_amt=p.position_amt,
                    entry_price=p.entry_price,
                    mark_price=p.mark_price,
                    unrealized_profit=p.unrealized_profit,
                    leverage=p.leverage,
                    isolated=p.isolated,
                )
                for p in positions
            ]
        )

    @app.post(
        "/api/auto-trade/order",
        response_model=BinanceOrderResponse,
        tags=["auto-trade"],
    )
    async def auto_trade_order(
        body: BinanceOrderRequest,
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> BinanceOrderResponse:
        proxy = _require_binance_proxy()
        user_id = _resolve_proxy_user_id(claims)
        try:
            order = await proxy.place_order(
                user_id,
                symbol=body.symbol,
                side=body.side,
                type=body.type,
                quantity=body.quantity,
                price=body.price,
                reduce_only=body.reduce_only,
                time_in_force=body.time_in_force,
                client_order_id=body.client_order_id,
            )
        except BinanceProxyError as exc:
            raise _proxy_error_to_http(exc) from exc
        return BinanceOrderResponse(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            type=order.type,
            status=order.status,
            executed_qty=order.executed_qty,
            avg_price=order.avg_price,
            reduce_only=order.reduce_only,
        )

    @app.post(
        "/api/auto-trade/close",
        response_model=BinanceCloseResponse,
        tags=["auto-trade"],
    )
    async def auto_trade_close(
        body: BinanceClosePositionRequest,
        claims: Optional[TokenClaims] = Depends(user_claims),
    ) -> BinanceCloseResponse:
        proxy = _require_binance_proxy()
        user_id = _resolve_proxy_user_id(claims)
        try:
            order = await proxy.close_position(user_id, symbol=body.symbol)
        except BinanceProxyError as exc:
            raise _proxy_error_to_http(exc) from exc
        if order is None:
            return BinanceCloseResponse(closed=False, symbol=body.symbol.upper())
        return BinanceCloseResponse(
            closed=True,
            symbol=order.symbol,
            order=BinanceOrderResponse(
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side,
                type=order.type,
                status=order.status,
                executed_qty=order.executed_qty,
                avg_price=order.avg_price,
                reduce_only=order.reduce_only,
            ),
        )

    return app


# ---------------------------------------------------------------------------
# Server entry-point (used by Bootstrap)
# ---------------------------------------------------------------------------


async def serve_api(
    engine: Any,
    *,
    host: str,
    port: int,
    jwt_secret: str = "",
    static_token: str = "",
    allow_static: bool = True,
    cors_origins: Optional[List[str]] = None,
    user_store: Optional[UserStore] = None,
    user_overrides: Optional[UserOverridesStore] = None,
    otp_store: Optional[OtpStore] = None,
    otp_delivery: Optional[OtpDeliveryProvider] = None,
    billing_verifier: Optional[BillingWebhookVerifier] = None,
    binance_keys_store: Optional[BinanceKeysStore] = None,
    binance_proxy: Optional[BinanceProxyClient] = None,
) -> None:
    """Run the API server forever.  Cancellation stops it cleanly."""
    import uvicorn  # imported lazily so optional dep stays optional

    app = build_app(
        engine,
        jwt_secret=jwt_secret,
        static_token=static_token,
        allow_static=allow_static,
        cors_origins=cors_origins,
        user_store=user_store,
        user_overrides=user_overrides,
        otp_store=otp_store,
        otp_delivery=otp_delivery,
        billing_verifier=billing_verifier,
        binance_keys_store=binance_keys_store,
        binance_proxy=binance_proxy,
    )
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="warning",
        access_log=False,
        loop="asyncio",
    )
    server = uvicorn.Server(config)
    log.info("API server listening on http://{}:{}", host, port)
    try:
        await server.serve()
    except asyncio.CancelledError:
        log.info("API server cancelled — shutting down")
        server.should_exit = True
        raise
