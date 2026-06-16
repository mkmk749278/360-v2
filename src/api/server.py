"""FastAPI app + uvicorn launcher.

The app instance is built lazily by ``build_app(engine)`` so tests can
construct one against a stub engine without booting the runtime.  In
production, ``serve_api(engine)`` is awaited as a long-running asyncio
task spawned from ``Bootstrap.launch_runtime_tasks``.

Auth model (post-Phase-4 migration — transition window):

The auth dependency tries three credential types in order on every
protected request:

1. **Static** — Bearer matches ``API_AUTH_TOKEN`` literally → treated
   as the owner.  Ops tooling, CI, 360 CE Ops.  Permanent.
2. **Firebase ID token** (RS256) — verified via ``firebase_admin``,
   resolved to a ``User`` via phone-match-and-backfill in
   :meth:`UserStore.get_or_create_by_firebase_uid`.  Only consulted
   when ``FIREBASE_AUTH_ENABLED=true`` AND the Firebase Admin SDK has
   been initialised.  Permanent post-cutover.
3. **HS256 JWT** (local) — verified via :func:`decode_token`.  The
   pre-Phase-4 path; the app's first request to ``/api/auth/anonymous``
   minted one of these.  Kept alive during the transition window so
   pre-migration Lumin app versions keep working until every tester
   is on the post-migration APK.

When all three reject, the dependency raises 401.

Telegram-OTP → Firebase bridge: ``POST /api/auth/telegram-otp/issue``
asks the engine to mint a 6-digit code and deliver it via
@LuminProBot only (no SMS / WhatsApp fall-through — the architectural
free fallback for users in regions where Firebase SMS Phone Auth
isn't viable).  The companion ``POST /api/auth/telegram-otp/verify``
takes the code, validates it via the existing :class:`OtpStore`,
registers the user with Firebase Admin (idempotent on phone), and
returns a Firebase custom token.  The app exchanges it via
``signInWithCustomToken`` to land a real Firebase session — same
post-state as the SMS path.
"""

from __future__ import annotations

import asyncio
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.utils import get_logger

from . import firebase_auth
from .auth import (
    OWNER_TIER,
    AuthError,
    TokenClaims,
    decode_token,
    mint_user_token,
)
from .billing_callback import SIGNATURE_HEADER, BillingWebhookVerifier
from .otp import IssueStatus, OtpStore, VerifyStatus
from .otp_delivery import (
    ChainedOtpProvider,
    DeliveryStatus,
    LogOnlyOtpProvider,
    OtpDeliveryProvider,
    TelegramOtpProvider,
)
from .schemas import (
    ActivityResponse,
    AgentsResponse,
    AutoModeChangeRequest,
    AutoModeChangeResponse,
    AutoModeResumeMineResponse,
    AutoModeStatus,
    AutoTradeSettings,
    BillingGrantRequest,
    BillingGrantResponse,
    HealthResponse,
    OtpRequest,
    OtpRequestResponse,
    OtpVerify,
    PnlHistoryResponse,
    PositionsDiagResponse,
    PositionsResponse,
    InvalidationSettings,
    PretpSettings,
    ProfileResponse,
    ProfileUpdate,
    PulseSnapshot,
    SignalDetail,
    SignalsResponse,
    TelegramOtpIssueRequest,
    TelegramOtpIssueResponse,
    TelegramOtpVerifyRequest,
    TelegramOtpVerifyResponse,
    TickersResponse,
    UserAutoTradeSettings,
    UserInvalidationSettings,
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
    build_positions_diag,
    build_pulse,
    build_signals,
    build_tickers,
)
from .users import User, UserStore

log = get_logger("api.server")

_API_VERSION = "0.0.2"

# Request-latency log thresholds.  A request slower than the INFO bar is
# worth a line; one slower than the WARNING bar is a subscriber-visible
# stall on the trust surface and we want it loud.  Tuned for a 1-vCPU VPS
# where a healthy cached read is sub-100ms.
_SLOW_REQUEST_INFO_S: float = 0.20
_SLOW_REQUEST_WARN_S: float = 1.00


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


async def _compute_needs_onboarding(
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
    user = await user_store.aget_by_id(uid)
    if user is None:
        return True
    return user.needs_onboarding


def _resolve_telegram_provider(
    delivery: Optional[OtpDeliveryProvider],
) -> Optional[TelegramOtpProvider]:
    """Pull the :class:`TelegramOtpProvider` out of the configured chain.

    The Telegram-OTP issue endpoint forces Telegram-only delivery — no
    SMS / WhatsApp fall-through — because the user explicitly tapped
    "Send via Telegram" in the app.  Rather than re-instantiate the
    provider here (which would require re-reading env + the live
    ``TelegramBot`` + ``UserStore`` instances), we walk the existing
    delivery chain and surface whichever ``TelegramOtpProvider``
    instance the bootstrap layer already wired up.

    Returns ``None`` if no Telegram provider is configured — the caller
    raises 503 so the app surfaces a clean error rather than silently
    falling through to SMS (which would defeat the point of the
    endpoint).
    """
    if delivery is None:
        return None
    if isinstance(delivery, TelegramOtpProvider):
        return delivery
    if isinstance(delivery, ChainedOtpProvider):
        primary = getattr(delivery, "_primary", None)
        if isinstance(primary, TelegramOtpProvider):
            return primary
        fallback = getattr(delivery, "_fallback", None)
        if isinstance(fallback, TelegramOtpProvider):
            return fallback
    return None


# ---------------------------------------------------------------------------
# Firebase env flag — read at request time so an .env flip takes effect on
# the next request without restarting the engine.  The function is small
# and cheap; reading os.environ is a dict lookup.
# ---------------------------------------------------------------------------


def _firebase_enabled() -> bool:
    """True iff ``FIREBASE_AUTH_ENABLED=true`` in the environment.

    Read at request time so the operator can flip the flag in
    ``.env`` and have the next request honour it without engine
    restart — the design doc's roll-back mechanism (flip false,
    revert to HS256-only).  Case-insensitive on the value side.
    """
    return os.environ.get("FIREBASE_AUTH_ENABLED", "false").lower() == "true"


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------


_bearer = HTTPBearer(auto_error=False)


def _make_auth_dep(
    jwt_secret: str,
    static_token: str,
    allow_static: bool,
    *,
    user_store: Optional[UserStore] = None,
    required_tier: Optional[str] = None,
):
    """Return a FastAPI dependency that verifies a bearer credential.

    Validation order (Phase 4 — Firebase migration):

    1. **Static token** (when ``allow_static=True`` and
       ``presented == static_token``) → treated as owner; bypasses
       both Firebase and HS256 checks and ignores ``required_tier``.
    2. **Firebase ID token** (when ``FIREBASE_AUTH_ENABLED=true`` AND
       :func:`firebase_auth.is_initialised`) → verified via Firebase
       Admin; resolved to a ``User`` via
       :meth:`UserStore.get_or_create_by_firebase_uid` (backfills
       ``firebase_uid`` on the existing row when the user's phone is
       already known from the legacy OTP path).
    3. **HS256 JWT** (transition window) → verified via
       :func:`decode_token`.

    ``required_tier`` (optional): if set, JWT-authed and Firebase-authed
    requests must carry that tier in their resolved User / claims.
    Static-token bypass is always treated as owner.

    Read endpoints use this with ``required_tier=None`` (any auth OK);
    write endpoints (settings PUT, auto-mode POST) use
    ``required_tier=OWNER_TIER``.
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
        # 1. Static-token bypass — owner-equivalent privilege.
        if allow_static and static_token and presented == static_token:
            return
        # 2. Firebase ID token path — only when enabled AND wired.
        if (
            user_store is not None
            and _firebase_enabled()
            and firebase_auth.is_initialised()
        ):
            try:
                # verify_id_token fetches Google JWKS on cache-miss — run
                # off the event loop so a slow network call doesn't freeze
                # all concurrent requests.
                claims = await asyncio.to_thread(
                    firebase_auth.verify_id_token, presented
                )
            except AuthError:
                claims = None
            if claims is not None:
                uid = str(claims.get("uid") or claims.get("user_id") or "")
                phone = str(claims.get("phone_number") or "")
                if uid and phone:
                    user = await user_store.aget_or_create_by_firebase_uid(uid, phone)
                    if required_tier is not None and user.tier != required_tier:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=(
                                f"insufficient privilege: endpoint requires "
                                f"tier={required_tier!r}, user has tier={user.tier!r}"
                            ),
                        )
                    return
                # Firebase token verified but missing uid/phone — fall
                # through to HS256 path rather than 401 immediately.
                # An ID token without a phone_number claim shouldn't
                # happen in production but is harmless to skip.
        # 3. HS256 JWT — legacy path during the transition window.
        try:
            jwt_claims = decode_token(presented, secret=jwt_secret)
        except AuthError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            )
        if required_tier is not None and jwt_claims.tier != required_tier:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"insufficient privilege: endpoint requires "
                    f"tier={required_tier!r}, token has tier={jwt_claims.tier!r}"
                ),
            )
        return

    return _verify


def _make_user_claims_dep(
    jwt_secret: str,
    static_token: str,
    allow_static: bool,
    *,
    user_store: Optional[UserStore] = None,
):
    """Dependency that resolves to the caller's identity.

    Returns:
      * ``None`` for static-token bypass — caller treats as owner /
        user_id=1.
      * A :class:`User` for Firebase-authed requests — the user row
        is materialised by phone-match-backfill in
        :meth:`UserStore.get_or_create_by_firebase_uid`.
      * A :class:`TokenClaims` for legacy HS256-JWT-authed requests.

    Used by per-user endpoints (profile, per-user settings + PnL) that
    need ``user_id`` to look up the right row.  :func:`_resolve_user_id`
    maps any of these to an int.
    """

    async def _resolve(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    ) -> Optional[Union[TokenClaims, User]]:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="missing bearer token",
            )
        presented = credentials.credentials
        # 1. Static-token bypass → None (caller resolves to owner).
        if allow_static and static_token and presented == static_token:
            return None
        # 2. Firebase ID token — return the resolved User row.
        if (
            user_store is not None
            and _firebase_enabled()
            and firebase_auth.is_initialised()
        ):
            try:
                claims = await asyncio.to_thread(
                    firebase_auth.verify_id_token, presented
                )
            except AuthError:
                claims = None
            if claims is not None:
                uid = str(claims.get("uid") or claims.get("user_id") or "")
                phone = str(claims.get("phone_number") or "")
                if uid and phone:
                    return await user_store.aget_or_create_by_firebase_uid(uid, phone)
        # 3. HS256 JWT — legacy path.
        try:
            return decode_token(presented, secret=jwt_secret)
        except AuthError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            )

    return _resolve


def _resolve_user_id(
    identity: Optional[Union[TokenClaims, User]],
    *,
    owner_id: int = 1,
) -> int:
    """Map an auth-resolved identity to a ``user_id``.

    * ``None`` (static-token bypass) → ``owner_id``.
    * :class:`User` (Firebase-authed) → ``user.user_id``.
    * :class:`TokenClaims` with ``user-<id>`` sub → parsed int.
    * Anonymous ``device-*`` HS256 tokens → 404 (they aren't users;
      the signup flow happens AFTER OTP verify so the only legitimate
      caller is a user-id JWT, a Firebase token, or static-token).
    """
    if identity is None:
        return owner_id
    if isinstance(identity, User):
        return identity.user_id
    # TokenClaims path
    sub = identity.sub
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
    """
    from .snapshot_cache import snapshot_cache as _snapshot_cache

    @asynccontextmanager
    async def _lifespan(_app: FastAPI):
        # In isolated mode (API_PROCESS_ISOLATED=true) the engine object is a
        # RedisEngineFacade; start the cache in Redis-backed mode so the
        # background refresh loops read from snapshot:* keys rather than
        # calling build_signals(engine) against an in-memory stub.
        from .redis_engine import RedisEngineFacade as _REF
        if isinstance(engine, _REF):
            await _snapshot_cache.start_redis_mode(engine._redis)
        else:
            await _snapshot_cache.start(engine)
        # NOTE: Firebase JWKS is pre-warmed synchronously at engine boot in
        # ``firebase_auth.init_firebase_admin`` (called from src.bootstrap)
        # using a correctly-claimed probe token that reaches the cert fetch.
        # The previous lifespan task here used a malformed probe that failed
        # claim validation *before* the fetch — a no-op — so it was removed.
        # Whether the SDK cert cache later expires under a live request is now
        # measured by the cold-fetch WARNING in ``firebase_auth.verify_id_token``.
        yield
        await _snapshot_cache.stop()

    app = FastAPI(
        title="360 Crypto Eye API",
        version=_API_VERSION,
        description="HTTP adapter for the Lumin app.",
        lifespan=_lifespan,
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

    # Response compression — kicks in only for payloads >= 1 KiB so the
    # cheap health/auth-token endpoints don't pay the gzip CPU cost,
    # while ``/api/signals`` (typically 30-80 KiB JSON) and
    # ``/api/activity`` (10-40 KiB) shrink ~65-75% on the wire.  Big lift
    # for Lumin subscribers on flaky 4G: the AutoTradeWatcher polls
    # ``/api/signals`` every 15s, Pulse and Signals tabs each refetch
    # on open, so the engine ships this payload 200-300x/hour per active
    # device — bandwidth + first-paint win compounds.
    app.add_middleware(GZipMiddleware, minimum_size=1024)

    # Request-latency observability.  Registered LAST so it is the OUTERMOST
    # layer — it measures the full request as the subscriber experiences it
    # (routing + auth deps + handler + gzip), not just the handler body.
    #
    # We have flown blind on per-endpoint latency: every "the app is slow /
    # blank on open" report has been diagnosed by theory, and at least one
    # documented "fix" turned out to be a no-op.  This is the instrument that
    # ends the guessing — structured per-request timing in the existing log
    # stream, no external collector needed.  Healthy cached reads stay silent;
    # only requests past the INFO/WARNING bars emit, so the signal-to-noise
    # stays high on a busy engine.
    @app.middleware("http")
    async def _timing_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        start = time.monotonic()
        try:
            response = await call_next(request)
        except Exception:
            # Time even the failures — a slow 500 is still a slow request the
            # subscriber waited on.  Re-raise so error handling is unchanged.
            dur_ms = (time.monotonic() - start) * 1000.0
            log.warning(
                "api.request.error: {} {} dur_ms={:.0f}",
                request.method, request.url.path, dur_ms,
            )
            raise
        dur_s = time.monotonic() - start
        if dur_s >= _SLOW_REQUEST_WARN_S:
            log.warning(
                "api.request.slow: {} {} status={} dur_ms={:.0f}",
                request.method, request.url.path,
                response.status_code, dur_s * 1000.0,
            )
        elif dur_s >= _SLOW_REQUEST_INFO_S:
            log.info(
                "api.request: {} {} status={} dur_ms={:.0f}",
                request.method, request.url.path,
                response.status_code, dur_s * 1000.0,
            )
        # Surface the server-measured time to the client/CDN for correlation
        # with Cloudflare logs without needing log access on both sides.
        response.headers["X-Response-Time-Ms"] = f"{dur_s * 1000.0:.0f}"
        return response

    auth = _make_auth_dep(
        jwt_secret, static_token, allow_static, user_store=user_store,
    )
    # Owner-tier dep — enforced on write endpoints so testers' anonymous
    # JWTs can READ state but can't mutate engine config (mode flip,
    # settings PUT).  Static-token bypass still works for admin tooling.
    owner_required = _make_auth_dep(
        jwt_secret, static_token, allow_static,
        user_store=user_store, required_tier=OWNER_TIER,
    )
    # User-claims dep — for per-user endpoints (profile, future per-user
    # settings + PnL).  Returns the decoded JWT claims / resolved User /
    # None depending on the credential type; :func:`_resolve_user_id`
    # maps any of these to an int.
    user_claims = _make_user_claims_dep(
        jwt_secret, static_token, allow_static, user_store=user_store,
    )

    # Auto-construct the OTP defaults so callers (and existing tests)
    # don't have to plumb every Phase 2 dep through.  When ``user_store``
    # is None we leave them as None too — the endpoints will 503.
    if user_store is not None and otp_store is None:
        otp_store = OtpStore()
    if user_store is not None and otp_delivery is None:
        otp_delivery = LogOnlyOtpProvider()

    # ---- Health (no auth — used by Docker/k8s probes + first-launch reachability) ----

    @app.get("/api/health", response_model=HealthResponse, tags=["meta"])
    async def health() -> HealthResponse:
        boot = getattr(engine, "_boot_time", 0.0) or 0.0
        uptime = time.monotonic() - boot if boot else 0.0
        return HealthResponse(uptime_seconds=max(0.0, uptime), version=_API_VERSION)

    # ---- Auth endpoints (legacy JWT — replaced by Firebase Phone Auth) ----
    # POST /api/auth/anonymous and /api/auth/refresh were retired when the
    # Lumin app migrated to Firebase Phone Auth (Phase 4).  They return
    # 410 Gone so old app builds surface a clear "update required" path
    # instead of a confusing auth failure.  The Telegram-OTP → Firebase
    # bridge (/api/auth/telegram-otp/*) and the HS256 fallback inside
    # the ``auth`` dependency are preserved for the transition window.

    @app.post(
        "/api/auth/anonymous",
        response_model=_TokenResponse,
        tags=["auth"],
    )
    async def auth_anonymous() -> _TokenResponse:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=(
                "legacy JWT auth has been replaced by Firebase Phone Auth; "
                "please update to the latest version of the Lumin app"
            ),
        )

    @app.post(
        "/api/auth/refresh",
        response_model=_TokenResponse,
        tags=["auth"],
    )
    async def auth_refresh(req: _RefreshRequest) -> _TokenResponse:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=(
                "legacy JWT refresh has been replaced by Firebase Phone Auth; "
                "please update to the latest version of the Lumin app"
            ),
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
        user = await user_store.aget_or_create_by_phone(req.phone)
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

    # ---- Telegram-OTP → Firebase custom-token bridge (Phase 4) ----

    @app.post(
        "/api/auth/telegram-otp/issue",
        response_model=TelegramOtpIssueResponse,
        tags=["auth"],
    )
    async def telegram_otp_issue(
        req: TelegramOtpIssueRequest,
    ) -> TelegramOtpIssueResponse:
        """Issue an OTP for ``phone_e164`` and deliver via @LuminProBot only.

        Mirrors ``POST /api/auth/request-otp`` (the SMS / WhatsApp /
        Telegram-chain issue endpoint) but forces Telegram-only
        delivery — no SMS / WhatsApp fall-through.  Used by the Lumin
        app's "Send via Telegram" button, the architectural free
        fallback for users in regions where Firebase SMS Phone Auth
        isn't viable (cost or Play Store sideload).

        Pairs with :func:`telegram_otp_verify` to complete the
        Telegram-OTP → Firebase custom-token bridge described in
        ``docs/firebase_auth_migration.md``.  Error shape matches
        :func:`auth_request_otp` so the Lumin app's existing OTP error
        handler covers both endpoints.
        """
        if user_store is None or otp_store is None or otp_delivery is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="phone auth not configured",
            )
        telegram = _resolve_telegram_provider(otp_delivery)
        if telegram is None:
            # No Telegram provider wired — the user tapped "Send via
            # Telegram" but the engine isn't configured to deliver
            # there.  503 (not 500): this is a config gap, not a bug.
            log.warning(
                "Telegram OTP issue requested for {} but no "
                "TelegramOtpProvider is configured in the delivery chain",
                req.phone_e164,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="telegram delivery not configured",
            )
        # Issue first — burns the rate-limit slot before we hit the
        # delivery channel, matching the safety pattern of the legacy
        # /api/auth/request-otp endpoint.
        result = otp_store.issue(req.phone_e164)
        if result.status is IssueStatus.RATE_LIMITED:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="too many OTP requests; try again later",
                headers={"Retry-After": str(result.retry_after_seconds)},
            )
        if result.status is not IssueStatus.OK or result.code is None:
            # Defensive — OtpStore.issue contract guarantees a code on
            # OK; reaching here means the contract has been violated.
            log.error(
                "OtpStore.issue returned unexpected status {} (code={}) for {}",
                result.status, result.code, req.phone_e164,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.status.value,
            )
        # Telegram-only delivery — bypass the chain (and any SMS /
        # WhatsApp fall-through it would normally apply).
        delivery = await telegram.send(req.phone_e164, result.code)
        if delivery.status is DeliveryStatus.UNSUPPORTED_CHANNEL:
            # User's phone isn't bound to a Telegram chat_id (no /start
            # in @LuminProBot yet).  502 with a structured detail so
            # the app can render "Open @LuminProBot, tap Start, then
            # try again" rather than a generic failure.
            log.info(
                "Telegram OTP unsupported for {}: {}",
                req.phone_e164, delivery.detail,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="telegram_chat_not_linked",
            )
        if delivery.status is not DeliveryStatus.OK:
            log.warning(
                "Telegram OTP delivery failed for {}: {}",
                req.phone_e164, delivery.detail,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="telegram_delivery_failed",
            )
        return TelegramOtpIssueResponse(
            status="ok",
            expires_in_seconds=result.expires_in_seconds,
        )

    @app.post(
        "/api/auth/telegram-otp/verify",
        response_model=TelegramOtpVerifyResponse,
        tags=["auth"],
    )
    async def telegram_otp_verify(
        req: TelegramOtpVerifyRequest,
    ) -> TelegramOtpVerifyResponse:
        if user_store is None or otp_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="phone auth not configured",
            )
        result = otp_store.verify(req.phone_e164, req.code)
        if result.status is not VerifyStatus.OK:
            # Match the OTP store's status tokens directly — the app
            # already handles "wrong_code" / "expired" / etc. in the UI.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.status.value,
            )
        # OTP validated — get-or-create the user row.
        user = await user_store.aget_or_create_by_phone(req.phone_e164)
        if user.firebase_uid is None:
            if not firebase_auth.is_initialised():
                # Firebase Admin not wired — engine can't mint a custom
                # token.  503 so the app's retry / fall-back UX kicks in.
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="firebase_disabled",
                )
            # register_user_by_phone + create_custom_token hit the
            # Firebase Admin SDK (network) — run off the event loop so a
            # slow Google round-trip doesn't freeze concurrent requests.
            firebase_uid = await asyncio.to_thread(
                firebase_auth.register_user_by_phone, req.phone_e164
            )
            await user_store.aset_firebase_uid(user.user_id, firebase_uid)
            # Reload the row with the backfilled uid so the response
            # carries the freshly-set value.
            reloaded = await user_store.aget_by_id(user.user_id)
            assert reloaded is not None
            user = reloaded
        assert user.firebase_uid is not None
        custom_token = await asyncio.to_thread(
            firebase_auth.create_custom_token, user.firebase_uid
        )
        return TelegramOtpVerifyResponse(
            custom_token=custom_token,
            user_id=user.user_id,
            tier=user.tier,
            paid_until=user.paid_until.isoformat() if user.paid_until else None,
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
        user = await user_store.aget_or_create_by_phone(payload.phone)
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
            updated = await user_store.aset_tier(
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
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> ProfileResponse:
        if user_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="user store not configured",
            )
        uid = _resolve_user_id(identity)
        user = await user_store.aget_by_id(uid)
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
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> ProfileResponse:
        if user_store is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="user store not configured",
            )
        uid = _resolve_user_id(identity)
        try:
            updated = await user_store.aupdate_profile(
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
    )
    async def pulse(
        response: Response,
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> PulseSnapshot:
        # Per-user paper visibility (PR #503, 2026-05-26) — paper-mode
        # today_pnl_usd + open_positions are filtered by the caller's
        # subscription windows. Anonymous device-token holders fall
        # through to engine-wide (legitimate fallback for callers who
        # haven't completed signup yet — they shouldn't see PnL anyway).
        try:
            user_id = _resolve_user_id(identity)
        except HTTPException:
            user_id = None
        # Fall back to the singleton when build_app didn't wire one
        # explicitly — same pattern as paper_trade_routes so the
        # existing fixture wiring (set_singleton in test bootstrap)
        # works for the new endpoint too.
        effective_uo = user_overrides
        if effective_uo is None:
            from .user_overrides import get_singleton as _get_uo_singleton
            effective_uo = _get_uo_singleton()
        response.headers["Cache-Control"] = "private, max-age=5, stale-while-revalidate=10"
        return await build_pulse(
            engine, user_id=user_id, user_overrides=effective_uo,
        )

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
        response: Response,
        status: str = Query("all", pattern="^(all|open|closed)$"),
        limit: int = Query(50, ge=1, le=500),
        setup_class: Optional[str] = Query(
            None,
            description="Filter to one evaluator's signals (e.g. SR_FLIP_RETEST)",
        ),
    ) -> SignalsResponse:
        items = _snapshot_cache.filter_signals(
            status=status, limit=limit, setup_class=setup_class,
        )
        if items is None:
            # Cache cold (first 5 s after startup) — fall back to live build.
            items = build_signals(
                engine, status=status, limit=limit, setup_class=setup_class,
            )
        response.headers["Cache-Control"] = "public, max-age=10, stale-while-revalidate=30"
        return SignalsResponse(items=items, total=len(items))

    @app.get(
        "/api/signals/{signal_id}",
        response_model=SignalDetail,
        tags=["signals"],
        dependencies=[Depends(auth)],
    )
    async def signal_detail(signal_id: str) -> SignalDetail:
        # Serve from the 5s background cache when warm (avoids building
        # 1000+ Pydantic models synchronously on every request).  The
        # cache cap is 500; fall back to a live 1000-item build for very
        # old signals not yet evicted from the engine's active_signals
        # + _signal_history.
        cached = _snapshot_cache.filter_signals(status="all", limit=500)
        pool = cached if cached is not None else build_signals(engine, status="all", limit=1000)
        for it in pool:
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
    )
    async def positions(
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> PositionsResponse:
        # Defensive logging (2026-05-08): the Trade tab fans out to three
        # endpoints (auto-mode + positions + activity) and a single 500 on
        # any of them shows the user "Could not load Trade state" with
        # zero diagnostic context.  Wrapping each endpoint catches the
        # exception, logs a full traceback for the VPS-side diagnosis,
        # and returns an empty list so the rest of the page can render.
        #
        # Per-user paper visibility (PR #503, 2026-05-26) — open
        # positions filtered by the caller's subscription windows in
        # paper mode. Anonymous tokens fall through to engine-wide.
        try:
            user_id = _resolve_user_id(identity)
        except HTTPException:
            user_id = None
        effective_uo = user_overrides
        if effective_uo is None:
            from .user_overrides import get_singleton as _get_uo_singleton
            effective_uo = _get_uo_singleton()
        try:
            items = await build_positions(
                engine, user_id=user_id, user_overrides=effective_uo,
            )
        except Exception:
            log.exception("/api/positions failed — returning empty list")
            items = []
        return PositionsResponse(items=items, total=len(items))

    # ---- Internal diag: position-state X-ray for the ops dashboard ----
    #
    # Owner-only (gated by ``owner_required``) — exposes stored SL/TP, the
    # 1m candle wick the monitor is comparing against, candle-feed age, and
    # the signed sl_breach_distance_pct per active signal.  Designed so the
    # 360 CE Ops dashboard's /positions view can tell apart stale-feed,
    # monitor-evaluation-bug, and state-sync-gap failure modes when a
    # position closes on Binance but stays ACTIVE in the engine.
    #
    # First step of the docker.sock removal noted in
    # ``ACTIVE_CONTEXT.md`` — future ``/internal/diag/*`` endpoints replace
    # the ``docker exec ... diag_*.py`` path the dashboard uses today.
    @app.get(
        "/internal/diag/positions",
        response_model=PositionsDiagResponse,
        tags=["internal-diag"],
        dependencies=[Depends(owner_required)],
    )
    async def positions_diag() -> PositionsDiagResponse:
        try:
            # Isolated mode: the engine container computes the full X-ray
            # (SL-breach / candle wicks need live data_store) and publishes it.
            # The facade's active_signals are skeletal stubs, so building the
            # diag against the facade would yield blank rows — consult the
            # published snapshot first, fall back to a live build otherwise.
            published = getattr(engine, "published_positions_diag", None)
            if callable(published):
                raw = published()
                if raw is not None:
                    return PositionsDiagResponse(**raw)
            return build_positions_diag(engine)
        except Exception:
            log.exception(
                "/internal/diag/positions failed — returning empty diag set",
            )
            from datetime import datetime as _dt, timezone as _tz
            return PositionsDiagResponse(
                items=[], total=0, monitor_running=False,
                generated_at=_dt.now(_tz.utc),
            )

    @app.get(
        "/internal/diag/position_counters",
        tags=["internal-diag"],
        dependencies=[Depends(owner_required)],
    )
    async def position_counters() -> Dict[str, Any]:
        """Drift x-ray for the three open-position counters.

        Owner-reported 2026-05-18 bug: Pulse header showed "Open
        positions: 4" while the list rendered "No open positions" —
        the two reads were off different sources that had drifted.
        This endpoint surfaces all three counters side-by-side so
        future drift is detectable in one place instead of inferred
        from a UI inconsistency.
        """
        rm = getattr(engine, "_risk_manager", None)
        router = getattr(engine, "router", None)
        broker = getattr(engine, "_order_manager", None)

        risk_ids: set = set(getattr(rm, "_open_signal_ids", set()) or set())
        router_ids: set = set(
            getattr(router, "active_signals", {}).keys()
            if router is not None else set()
        )
        broker_positions = getattr(broker, "_positions", None)
        if not isinstance(broker_positions, dict):
            broker_positions = {}
        broker_ids: set = {
            sid
            for sid, p in broker_positions.items()
            if (
                float(getattr(p, "quantity", 0.0) or 0.0)
                - float(getattr(p, "closed_quantity", 0.0) or 0.0)
            )
            > 1e-9
        }

        return {
            "risk_manager_count": len(risk_ids),
            "broker_open_count": len(broker_ids),
            "router_active_count": len(router_ids),
            # Drift sets — non-empty = a real bug to fix, not just a
            # transient race.
            "in_risk_but_not_broker": sorted(risk_ids - broker_ids),
            "in_broker_but_not_risk": sorted(broker_ids - risk_ids),
            "in_broker_but_not_router": sorted(broker_ids - router_ids),
            "in_router_but_not_broker": sorted(router_ids - broker_ids),
            # Sample of broker entries with zero residual — should be
            # empty if close_partial/close_full pops correctly.
            "broker_drained_not_popped": sorted(
                sid
                for sid, p in broker_positions.items()
                if (
                    float(getattr(p, "quantity", 0.0) or 0.0)
                    - float(getattr(p, "closed_quantity", 0.0) or 0.0)
                )
                <= 1e-9
            ),
        }

    @app.get(
        "/internal/diag/tasks",
        tags=["internal-diag"],
        dependencies=[Depends(owner_required)],
    )
    async def diag_tasks() -> Dict[str, Any]:
        """Owner-tier read-only census of live engine asyncio tasks.

        Used by the 360 CE Ops monitoring agent (D2 — BackgroundTaskDetector)
        to verify the critical engine loops are still running:
        ``trade_monitor``, ``reconciler``, ``mark_price_feed``,
        ``funding_exit_watcher``.

        Mode-agnostic: in single-process mode ``engine`` is the real
        ``CryptoSignalEngine`` and returns its live ``asyncio.all_tasks()``;
        in isolated mode ``engine`` is the ``RedisEngineFacade`` and returns
        the census the engine container published into ``engine_state``. A
        bare ``asyncio.all_tasks()`` here was wrong under isolation — it saw
        the API container's own tasks, never the engine's.
        """
        getter = getattr(engine, "get_background_task_census", None)
        if callable(getter):
            names = list(getter())
        else:  # defensive fallback — neither engine type should hit this
            names = sorted(
                t.get_name() for t in asyncio.all_tasks() if not t.done()
            )
        return {"tasks": names, "count": len(names)}

    # ---- Activity ----

    @app.get(
        "/api/activity",
        response_model=ActivityResponse,
        tags=["activity"],
        dependencies=[Depends(auth)],
    )
    async def activity(
        response: Response,
        limit: int = Query(50, ge=1, le=500),
        setup_class: Optional[str] = Query(
            None,
            description="Filter to one evaluator's lifecycle events",
        ),
    ) -> ActivityResponse:
        try:
            cached = _snapshot_cache.filter_activity(limit=limit, setup_class=setup_class)
            if cached is not None:
                items = cached
            else:
                items = build_activity(engine, limit=limit, setup_class=setup_class)
        except Exception:
            log.exception("/api/activity failed — returning empty list")
            items = []
        response.headers["Cache-Control"] = "public, max-age=30, stale-while-revalidate=60"
        return ActivityResponse(items=items, total=len(items))

    # ---- Auto-mode ----

    @app.get(
        "/api/auto-mode",
        response_model=AutoModeStatus,
        tags=["auto-mode"],
    )
    async def auto_mode_get(
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> AutoModeStatus:
        # Per-user paper visibility (PR #503, 2026-05-26) — Trade-tab
        # header rolling counters (daily / weekly / monthly / total /
        # equity / open_positions) filtered to the caller's
        # subscription windows in paper mode. A fresh user enabling
        # paper sees equity=$1000 and zeros across every PnL window.
        # Anonymous device-token holders raise HTTPException 404 in
        # _resolve_user_id; catch and pass user_id=None so the
        # endpoint falls back to engine-wide rather than 404'ing
        # (matches the pattern in /api/pnl/history).
        try:
            user_id = _resolve_user_id(identity)
        except HTTPException:
            user_id = None
        effective_uo = user_overrides
        if effective_uo is None:
            from .user_overrides import get_singleton as _get_uo_singleton
            effective_uo = _get_uo_singleton()
        try:
            return await build_auto_mode(
                engine, user_id=user_id, user_overrides=effective_uo,
            )
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
    )
    async def pnl_history_get(
        days: int = Query(30, ge=1, le=365),
        mode: Optional[str] = Query(
            None,
            pattern="^(off|paper|live)$",
            description="Override the engine's current mode — useful for "
            "viewing the other ledger (e.g. paper history while in live).",
        ),
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> PnlHistoryResponse:
        # Per-user paper PnL filter (2026-05-24). Resolve identity → user_id
        # → subscription windows → filtered ledger. Anonymous device-token
        # holders raise HTTPException 404 in _resolve_user_id; catch and
        # pass user_id=None so the endpoint falls back to engine-wide
        # (pre-2026-05-24 behaviour) rather than 404'ing the whole call.
        try:
            user_id = _resolve_user_id(identity)
        except HTTPException:
            user_id = None
        payload = await build_pnl_history(
            engine,
            mode=mode,
            days=days,
            user_id=user_id,
            user_overrides=user_overrides,
        )
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

    # ---- Per-user auto-pause resume (2026-05-24) ----
    #
    # When signal_dispatch sees N consecutive Binance -2019 (insufficient
    # margin) rejects for a user, it stamps ``paused_reason='insufficient_
    # margin'`` on the user's auto-trade row so the dispatcher stops
    # spamming their Recent Activity feed. This endpoint clears that
    # pause so the user can resume after topping up their wallet.
    #
    # User-callable (any tier). Idempotent — calling on a not-paused
    # user returns ``resumed=False`` with no side effects.

    @app.post(
        "/api/auto-mode/resume-mine",
        response_model=AutoModeResumeMineResponse,
        tags=["auto-mode"],
    )
    async def auto_mode_resume_mine(
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> AutoModeResumeMineResponse:
        if user_overrides is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        user_id = _resolve_user_id(identity)
        resumed = await user_overrides.aresume_user_auto_trade(user_id)
        return AutoModeResumeMineResponse(resumed=resumed)

    # ---- Paper-trade-visibility endpoints (2026-05-16) ----
    # Registered via register() in paper_trade_routes.py so the
    # GET /api/trades + POST /api/auto-mode/paper/reset routes live in
    # their own module.  Same dep wiring as the inline routes above —
    # auth covers read access, owner_required gates the reset.
    from . import paper_trade_routes as _paper_trade_routes
    _paper_trade_routes.register(
        app,
        engine=engine,
        auth=auth,
        owner_required=owner_required,
        user_claims=user_claims,
        resolve_user_id=_resolve_user_id,
    )

    # ---- Binance connect flow (server-side execution, B18 + §3.9) ----
    # Registers POST /api/binance/connect.  Validates the user's
    # Binance key against B18 rules (withdraw=off, futures=on,
    # IP=engine VPS) and persists the encrypted blob to Firestore.
    # The route refuses at runtime if KMS / Firestore aren't wired,
    # so it's safe to register unconditionally (test harnesses + dev
    # boots without GCP env vars still get a clean 500 with a clear
    # operator message rather than a route registration failure).
    from . import binance_connect_routes as _binance_connect_routes
    _binance_connect_routes.register(
        app,
        auth=auth,
        identity_dep=user_claims,
    )

    # ---- Auto-trade status (server-side execution stack, PR-14 follow-up 3/3) ----
    # Lightweight GET endpoint that surfaces the user's auto-trade
    # enablement state.  Powers the Lumin app's "your auto-trade is
    # disabled" banner.  Cached 5s server-side via KillSwitchClient.
    from . import auto_trade_status_routes as _auto_trade_status_routes
    _auto_trade_status_routes.register(
        app,
        auth=auth,
        identity_dep=user_claims,
    )

    # ``GET /api/region`` (Play Store A6 / E2, 2026-05-20) — client
    # region detection for the Play Store launch.  Public endpoint
    # (no auth) so the client can call it before sign-in.  Reads
    # CF-IPCountry / X-Country-Code headers; soft-fail open to
    # ``"unknown"`` when no header is present.
    from . import region_routes as _region_routes
    _region_routes.register(app)

    # ``DELETE /api/account`` (Play Store E1, 2026-05-20) — in-app
    # account deletion + Binance key revocation.  Required by Play's
    # User Data policy (answer/13327111); without it, the Data
    # Safety review stage rejects the listing.  Orchestrates:
    # Firestore key-blob delete → SQLite user row delete (cascades
    # per-user override tables) → user-roster cache invalidation.
    from . import account_routes as _account_routes
    _account_routes.register(
        app,
        auth=auth,
        identity_dep=user_claims,
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
            PRE_TP_GRAB_FRACTION,
            PRE_TP_MAX_AGE_SEC,
            PRE_TP_MIN_AGE_SEC,
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
            # OWNER_BRIEF B17 — engine default 50%; engine-wide overrides
            # not stored in ``user_settings`` yet (only per-user via the
            # user_pretp_settings table).  Surfaces the config default
            # so the app can render an authoritative starting value.
            grab_fraction=PRE_TP_GRAB_FRACTION,
            # OWNER_BRIEF B17 (2026-05-17) — default True extends pre-TP
            # capital preservation to manual entries via the app-side
            # watcher running in passive mode when auto-trade is off.
            # Pure engine-side action; doesn't depend on app state here.
            protect_manual_entries=True,
        )

    def _build_invalidation_view() -> InvalidationSettings:
        """Compose the engine's effective Invalidation view (OWNER_BRIEF B17).

        Engine-wide invalidation settings live in `config/__init__.py` as
        the ``INVALIDATION_*`` constants.  This view returns the defaults
        only — there is no engine-wide settings page for invalidation
        (PR #4 will add one if/when the operator needs to flip the global
        mode).  Per-user overrides are composed in ``_build_user_invalidation_view``.
        """
        from config import (
            INVALIDATION_MODE_DEFAULT,
            INVALIDATION_TRAILING_MFE_R_DEFAULT,
            INVALIDATION_TRAILING_RETRACE_PCT_DEFAULT,
        )
        return InvalidationSettings(
            mode=INVALIDATION_MODE_DEFAULT,
            min_age_sec=None,  # Per-channel in `INVALIDATION_MIN_AGE_SECONDS`; no global scalar
            momentum_threshold_mult=1.0,
            ema_crossover_enabled=True,
            regime_shift_enabled=True,
            trailing_kill_enabled=(INVALIDATION_MODE_DEFAULT == "tight"),
            trailing_mfe_r_threshold=INVALIDATION_TRAILING_MFE_R_DEFAULT,
            trailing_retrace_pct=INVALIDATION_TRAILING_RETRACE_PCT_DEFAULT,
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

    async def _build_user_pretp_view(user_id: int) -> UserPretpSettings:
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
        overrides = await user_overrides.aget_pretp(user_id)
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
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> UserPretpSettings:
        if user_overrides is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        uid = _resolve_user_id(identity)
        return await _build_user_pretp_view(uid)

    @app.put(
        "/api/settings/user/pretp",
        response_model=UserPretpSettings,
        tags=["settings"],
    )
    async def user_pretp_put(
        payload: PretpSettings,
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> UserPretpSettings:
        if user_overrides is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        uid = _resolve_user_id(identity)
        # ``exclude_unset=True`` mirrors the engine-wide endpoint's
        # partial-update semantics — the user can change one toggle
        # without re-sending every other field.
        partial = payload.model_dump(exclude_unset=True)
        if partial:
            await user_overrides.aupdate_pretp(uid, partial)
        return await _build_user_pretp_view(uid)

    @app.delete(
        "/api/settings/user/pretp",
        response_model=UserPretpSettings,
        tags=["settings"],
    )
    async def user_pretp_delete(
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> UserPretpSettings:
        """Reset the user's pre-TP settings to engine defaults by deleting
        their override row.  Returns the rebuilt view, which now reports
        ``using_defaults=True``.  Idempotent — a reset with no prior overrides
        is a no-op that still returns the defaults view."""
        if user_overrides is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        uid = _resolve_user_id(identity)
        await user_overrides.aclear_pretp(uid)
        return await _build_user_pretp_view(uid)

    # ---- Settings: Per-user invalidation overrides (OWNER_BRIEF B17, 2026-05-17) ----

    async def _build_user_invalidation_view(user_id: int) -> UserInvalidationSettings:
        """Compose per-user Invalidation view: user-row override where set,
        engine default otherwise.

        Engine doesn't yet consume per-user values — PR #4 wires the read
        path in ``_check_invalidation``.  Until then, these reads/writes
        are pure storage so the Lumin invalidation-settings page (PR L2)
        can be built in parallel against the live wire schema.
        """
        defaults = _build_invalidation_view()
        if user_overrides is None:
            return UserInvalidationSettings(
                **defaults.model_dump(),
                using_defaults=True,
            )
        overrides = await user_overrides.aget_invalidation(user_id)
        resolved = defaults.model_dump()
        for key, val in overrides.items():
            resolved[key] = val
        return UserInvalidationSettings(
            **resolved,
            using_defaults=not bool(overrides),
        )

    @app.get(
        "/api/settings/user/invalidation",
        response_model=UserInvalidationSettings,
        tags=["settings"],
    )
    async def user_invalidation_get(
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> UserInvalidationSettings:
        if user_overrides is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        uid = _resolve_user_id(identity)
        return await _build_user_invalidation_view(uid)

    @app.put(
        "/api/settings/user/invalidation",
        response_model=UserInvalidationSettings,
        tags=["settings"],
    )
    async def user_invalidation_put(
        payload: InvalidationSettings,
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> UserInvalidationSettings:
        if user_overrides is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        uid = _resolve_user_id(identity)
        # ``exclude_unset=True`` mirrors the pre-TP endpoint's partial-update
        # semantics — the user can flip a single toggle without re-sending
        # every other field.  ``UserOverridesStore.update_invalidation``
        # silently drops invalid mode tokens and ill-typed values; the
        # Pydantic validator already enforces gt=0/le=1 on the bounded floats.
        partial = payload.model_dump(exclude_unset=True)
        if partial:
            await user_overrides.aupdate_invalidation(uid, partial)
        return await _build_user_invalidation_view(uid)

    @app.delete(
        "/api/settings/user/invalidation",
        response_model=UserInvalidationSettings,
        tags=["settings"],
    )
    async def user_invalidation_delete(
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> UserInvalidationSettings:
        """Reset the user's invalidation settings to engine defaults by
        deleting their override row.  Returns the rebuilt view, which now
        reports ``using_defaults=True``.  Idempotent."""
        if user_overrides is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        uid = _resolve_user_id(identity)
        await user_overrides.aclear_invalidation(uid)
        return await _build_user_invalidation_view(uid)

    # ---- Settings: Per-user auto-trade overrides (Phase 2) ----

    async def _build_user_auto_trade_view(user_id: int) -> UserAutoTradeSettings:
        defaults = _build_auto_trade_view()
        # ``mode`` is per-user opt-in, NOT a field that should inherit
        # the engine-wide default the way ``position_size_pct`` /
        # ``leverage_cap`` / ``max_concurrent_positions`` do.  Those
        # three are legitimate operator-set baselines that take effect
        # on every user until they customise; ``mode`` is whether the
        # *user* wants paper, live, or no auto-trade at all — letting
        # it default to the engine's running mode (currently 'paper')
        # is the same per-user-isolation leak fixed for the runtime-
        # status endpoint earlier: every new signed-in user appeared to
        # already be opted into paper because they inherited the
        # engine's mode.  Owner-reported 2026-05-23: "trade > paper
        # there it's still showing default on" + "many owner changes
        # are applying to all users".
        #
        # Resolution: strip ``mode`` from the engine-wide baseline and
        # set it from the per-user row only.  If the row has no
        # ``mode`` key (user never opted in), the response carries
        # ``mode = None`` and the Lumin app renders the Paper tab in
        # its off-state.
        defaults_dict = defaults.model_dump()
        defaults_dict["mode"] = None
        if user_overrides is None:
            return UserAutoTradeSettings(
                **defaults_dict,
                using_defaults=True,
            )
        overrides = await user_overrides.aget_auto_trade(user_id)
        resolved = defaults_dict
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
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> UserAutoTradeSettings:
        if user_overrides is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        uid = _resolve_user_id(identity)
        return await _build_user_auto_trade_view(uid)

    @app.put(
        "/api/settings/user/auto-trade",
        response_model=UserAutoTradeSettings,
        tags=["settings"],
    )
    async def user_auto_trade_put(
        payload: AutoTradeSettings,
        identity: Optional[Union[TokenClaims, User]] = Depends(user_claims),
    ) -> UserAutoTradeSettings:
        if user_overrides is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="per-user overrides not configured",
            )
        uid = _resolve_user_id(identity)
        partial = payload.model_dump(exclude_unset=True)
        # Note: per-user mode flips do NOT trigger the engine-wide
        # ``set_auto_execution_mode`` — the engine continues to operate
        # in whatever mode the operator set via /api/settings/auto-trade.
        # Per-user mode is stored for Phase 3 when the user's app
        # decides whether to fire their own Binance order.
        #
        # Auto-resume on explicit live re-enable (2026-05-25): if the
        # user explicitly sets mode='live', clear any outstanding auto-
        # pause so they don't have to separately navigate to the Trade
        # tab to tap "Resume".  Root cause: after ≥3 consecutive -2019
        # rejections the dispatcher auto-pauses the user; changing
        # notional in Settings and re-saving mode='live' is the natural
        # recovery path, and it should implicitly resume dispatch.
        if partial.get("mode") in ("live", "both"):
            await user_overrides.aresume_user_auto_trade(uid)
        if partial:
            await user_overrides.aupdate_auto_trade(uid, partial)
        # Invalidate the per-user runtime-status cache so a mode toggle
        # is reflected on the app's next status poll without waiting for
        # the 10 s TTL to expire.  Firebase UID needed; map from user_id.
        try:
            from .auto_trade_status_routes import invalidate_runtime_cache as _irc
            from src.api import users as _users_mod
            _us = _users_mod.get_singleton()
            if _us is not None:
                identity_for_uid = identity  # may be User or TokenClaims
                if isinstance(identity_for_uid, _users_mod.User):
                    _irc(identity_for_uid.firebase_uid or "")
        except Exception:
            pass  # Cache invalidation is best-effort — stale data expires anyway
        return await _build_user_auto_trade_view(uid)

    # ---- Agents ----

    @app.get(
        "/api/agents",
        response_model=AgentsResponse,
        tags=["agents"],
        dependencies=[Depends(auth)],
    )
    async def agents() -> AgentsResponse:
        cached = _snapshot_cache.get_agents()
        items = cached if cached is not None else build_agents(engine)
        return AgentsResponse(items=items, total=len(items))

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
    )
    # Expand the default asyncio thread-pool so concurrent authenticated
    # requests don't queue behind each other's ``asyncio.to_thread`` calls.
    # Default = min(32, cpu_count + 4) which is ~6 on a 2-CPU VPS — too
    # small when each request does 2-4 threaded ops (auth verify + DB reads).
    # 32 gives headroom for 8+ concurrent users without exhausting the pool.
    import concurrent.futures as _cf
    _loop = asyncio.get_running_loop()
    _loop.set_default_executor(
        _cf.ThreadPoolExecutor(max_workers=32, thread_name_prefix="api-io")
    )

    # NOTE on ``loop``: serve_api runs ``await server.serve()`` on the engine's
    # already-running event loop (main.py: asyncio.run(_run())).  uvicorn only
    # installs a loop policy when it OWNS the process, so a ``loop=`` setting
    # here is a no-op — adopting uvloop is an engine-wide change at the
    # top-level runner (and touches the FSM money-path loop), tracked
    # separately.  The settings below ARE applied by uvicorn's protocol/server
    # layer regardless of loop ownership, so they take effect here.
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="warning",
        access_log=False,
        # Mobile clients idle between tab navigations.  The uvicorn default
        # (5s) drops the keep-alive connection in that gap, forcing a fresh
        # TCP+TLS handshake (120-450ms on 4G) on the next request.  65s holds
        # the connection across normal navigation pauses — one past the 60s
        # idle most mobile carriers/NATs enforce.
        timeout_keep_alive=65,
        # Explicit ceiling so a traffic spike sheds load (503) instead of
        # exhausting the 1-vCPU VPS and stalling every in-flight request.
        # Well above realistic concurrent load at current subscriber scale.
        limit_concurrency=200,
        # Give in-flight requests a bounded window to drain on the ~45s
        # deploy restart instead of being cut mid-response.
        timeout_graceful_shutdown=30,
    )
    server = uvicorn.Server(config)
    log.info("API server listening on http://{}:{}", host, port)
    try:
        await server.serve()
    except asyncio.CancelledError:
        log.info("API server cancelled — shutting down")
        server.should_exit = True
        raise
