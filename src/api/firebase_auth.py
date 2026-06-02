"""Firebase Admin SDK integration — ID token verification + custom token minting.

Initialised once at boot.  Verifies Firebase ID tokens for end-user
requests; mints custom tokens for the Telegram-OTP fallback path.

Match the style of :mod:`src.api.auth`: stdlib + loguru + threading.RLock,
no surprises.  All Firebase SDK calls are funnelled through this module
so the rest of the engine can stay ignorant of ``firebase_admin``'s
exception taxonomy — failures surface as :class:`src.api.auth.AuthError`
with a human-readable message.

Lifecycle:

* ``init_firebase_admin(service_account_path, project_id)`` is called
  once from :mod:`src.bootstrap` after :class:`UserStore` is up.  It is
  idempotent: a second call is a no-op rather than an error so callers
  don't have to guard with :func:`is_initialised`.
* ``is_initialised()`` lets the request-time auth dependency probe
  whether Firebase is wired without raising.  When False the dependency
  falls back to the legacy HS256 path.
* ``verify_id_token`` / ``register_user_by_phone`` /
  ``create_custom_token`` are the three public verbs the engine needs.

Threading: the module-level state (the Firebase ``App``) is set once at
boot and read many times per request.  An :class:`threading.RLock`
guards :func:`init_firebase_admin` so concurrent boot races (test
harnesses spawning multiple engines) don't race on the singleton, but
the read-side helpers acquire the lock only briefly to load the flag.
"""

from __future__ import annotations

import base64
import json
import threading
import time
from typing import Any, Dict, Optional, Tuple

from src.utils import get_logger

from .auth import AuthError

log = get_logger("api.firebase_auth")


# ---------------------------------------------------------------------------
# Module-level state — set once by ``init_firebase_admin``
# ---------------------------------------------------------------------------


_lock = threading.RLock()
_app: Any = None  # firebase_admin.App once initialised
_project_id: Optional[str] = None

# ---------------------------------------------------------------------------
# Short-lived token-verification cache.
#
# Both the ``auth`` dependency and the ``user_claims`` dependency call
# ``verify_id_token`` on the same bearer token for each request that uses
# both (e.g. /api/pulse, /api/settings/user/pretp).  Without a cache that
# means two sequential JWKS-verified RSA checks per request, and if the
# JWKS cache in the Firebase Admin SDK is cold (engine restart, ~1-hour
# expiry) each check can stall 0.5–3 s on a round-trip to googleapis.com.
# Two stalls back-to-back reliably push past the app's 4-second timeout.
#
# Fix: cache the decoded claims dict keyed on the raw token string for
# _VERIFY_CACHE_TTL seconds.  The second call within that window returns
# the cached dict without a network round-trip.
#
# Security notes:
# * Firebase ID tokens expire in 1 hour; a 60-second cache is far shorter
#   than the token lifetime, so an expired token is never accepted from cache.
# * Token revocation is not supported by the current engine (no call to
#   ``check_revoked=True``), so caching does not weaken the revocation story.
# * The cache is bounded at _VERIFY_CACHE_MAX entries; old entries are
#   pruned lazily when the size threshold is crossed.
# ---------------------------------------------------------------------------

_VERIFY_CACHE_TTL: float = 60.0       # seconds
_VERIFY_CACHE_MAX: int = 512          # entries before lazy pruning
_verify_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

# Above this wall-clock duration, an SDK ``verify_id_token`` call almost
# certainly paid for a cold JWKS cert fetch (a warm RSA verify is sub-ms).
# Crossing it means a real user request hit the googleapis.com round-trip —
# the exact symptom the boot pre-warm is meant to prevent.  We log it at
# WARNING so production logs reveal whether (and how often) the SDK cert
# cache expires under us, which is the data that decides if a periodic
# re-warm is worth building.  Pure instrumentation — no behaviour change.
_COLD_FETCH_WARN_S: float = 0.25
_verify_cache_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------


def _build_prewarm_token(project_id: str) -> str:
    """Build a syntactically valid but cryptographically invalid Firebase JWT.

    The token passes header/claims validation (correct iss, aud, sub, exp) so
    the SDK proceeds to fetch JWKS from googleapis.com before failing on the
    garbage signature.  That fetch is all we need — it warms the in-process
    JWKS cache for the next hour.
    """
    def _b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    header = _b64url(json.dumps({"alg": "RS256", "kid": "prewarm"}).encode())
    now = int(time.time())
    payload = _b64url(json.dumps({
        "iss": f"https://securetoken.google.com/{project_id}",
        "aud": project_id,
        "sub": "prewarm",
        "iat": now,
        "exp": now + 3600,
    }).encode())
    return f"{header}.{payload}.AAAA"


def prewarm_jwks_once() -> float:
    """Force-fetch Google's Firebase signing certs into the SDK's cert cache.

    Builds a token with valid ``iss``/``aud``/``sub``/``exp`` claims so the SDK
    proceeds *past* claim validation to the cert fetch (``google.oauth2.
    id_token.verify_token``) before failing on the garbage signature.  That
    fetch — and the in-process cache it populates — is the entire point; the
    signature failure is expected and swallowed.

    Returns the measured wall-clock duration of the warm in seconds, or
    ``-1.0`` when Firebase is not initialised (nothing to warm).  The caller
    logs the duration so production logs show, on every boot, *how long* the
    JWKS fetch actually took — the number that tells us whether the cold-start
    penalty is real on this VPS and whether it ever lands on a user request.

    Idempotent and safe to call repeatedly.  A second call within the SDK's
    cert cache-control window returns from cache without a network round-trip;
    a call after the cache expires re-fetches.  Whether a *periodic* re-warm
    is needed to defeat the ~1 h cache TTL is an open question pending the
    cold-fetch instrumentation in :func:`verify_id_token` — we measure the
    real recurrence in production before building (and tuning) a re-warm loop.
    """
    if not is_initialised():
        return -1.0
    pid = _project_id or ""
    start = time.monotonic()
    try:
        from firebase_admin import auth as _fb_auth  # type: ignore[import-not-found]

        _fb_auth.verify_id_token(_build_prewarm_token(pid))
    except Exception:
        # Expected — the garbage signature fails verification, but the cert
        # fetch (the side effect we want) already happened before that point.
        pass
    return time.monotonic() - start


def init_firebase_admin(service_account_path: str, project_id: str) -> None:
    """Initialise the Firebase Admin SDK against the configured project.

    Idempotent — a second call with the same args is a no-op.  Errors
    while loading the credential JSON or calling ``initialize_app``
    propagate to the caller, which is expected to wrap this in a
    try/except so a missing / bad service-account file doesn't crash
    engine boot (the engine should still be able to serve via the
    legacy HS256 path).

    After SDK init this function synchronously pre-warms the JWKS cache by
    verifying a dummy token.  The verify call fails (expected — the dummy
    token has a garbage signature) but forces the 2-3 s googleapis.com round
    trip to happen at boot time, so the first real user request is never the
    one that pays the cold-JWKS penalty.
    """
    global _app, _project_id
    with _lock:
        if _app is not None:
            log.info(
                "Firebase Admin already initialised: project={}",
                _project_id,
            )
            return
        # Lazy import — firebase-admin pulls in google-auth + JWKS
        # caching; installs that don't enable Firebase shouldn't pay
        # the import cost on every engine start.
        import firebase_admin  # type: ignore[import-not-found]
        from firebase_admin import credentials  # type: ignore[import-not-found]

        cred = credentials.Certificate(service_account_path)
        _app = firebase_admin.initialize_app(cred, {"projectId": project_id})
        _project_id = project_id
        log.info(
            "Firebase Admin initialised: project={}, service_account={}",
            project_id, service_account_path,
        )
    # Pre-warm JWKS outside the lock so the 2-3 s network call doesn't block
    # concurrent boot-time readers.  The server isn't accepting requests yet
    # at this point so racing is not a concern — we just want the cache warm
    # before the first authenticated HTTP request arrives.
    log.info("Firebase JWKS pre-warm: fetching googleapis.com certs...")
    warm_s = prewarm_jwks_once()
    log.info("Firebase JWKS pre-warm complete in {:.0f}ms", warm_s * 1000.0)


def is_initialised() -> bool:
    """Return True iff :func:`init_firebase_admin` has been called successfully."""
    with _lock:
        return _app is not None


# ---------------------------------------------------------------------------
# ID token verification
# ---------------------------------------------------------------------------


def verify_id_token(id_token: str) -> Dict[str, Any]:
    """Verify a Firebase ID token and return the decoded claims dict.

    The returned dict carries the standard Firebase claims — most
    importantly ``uid`` and ``phone_number`` (E.164).  Raises
    :class:`src.api.auth.AuthError` with a human-readable message on
    any failure (invalid signature, expired, wrong audience, network
    issue fetching JWKS, etc.) — callers translate that to HTTP 401.

    Results are cached for ``_VERIFY_CACHE_TTL`` seconds so that the
    ``auth`` dependency and ``user_claims`` dependency — which both call
    this function for the same token on every ``/api/pulse``-style
    request — only pay the JWKS-round-trip cost once per minute.
    """
    if not is_initialised():
        raise AuthError("firebase admin not initialised")

    now = time.monotonic()
    with _verify_cache_lock:
        entry = _verify_cache.get(id_token)
        if entry is not None and now - entry[0] < _VERIFY_CACHE_TTL:
            return dict(entry[1])  # return a copy so callers can't mutate cache

    # Lazy import here too — the module-level path stays cheap for
    # processes that never call ``verify_id_token`` (e.g. the test
    # harness that mocks this function).
    from firebase_admin import auth as fb_auth  # type: ignore[import-not-found]

    verify_start = time.monotonic()
    try:
        claims = fb_auth.verify_id_token(id_token)
    except Exception as exc:
        # firebase_admin.auth raises a number of distinct exception
        # types (ExpiredIdTokenError, RevokedIdTokenError,
        # InvalidIdTokenError, …).  Collapse them all to AuthError
        # with the underlying message — the caller doesn't care WHY
        # the token failed, only that it did.
        raise AuthError(f"firebase id-token verification failed: {exc}")
    verify_s = time.monotonic() - verify_start
    if verify_s >= _COLD_FETCH_WARN_S:
        # Probable cold JWKS cert fetch on a live request — the boot warm
        # either hasn't run or the SDK cert cache has since expired.
        log.warning(
            "firebase verify_id_token slow: {:.0f}ms — probable cold JWKS "
            "cert fetch on a live request (boot warm expired or never ran)",
            verify_s * 1000.0,
        )

    with _verify_cache_lock:
        _verify_cache[id_token] = (now, claims)
        if len(_verify_cache) > _VERIFY_CACHE_MAX:
            cutoff = now - _VERIFY_CACHE_TTL
            stale = [k for k, (t, _) in _verify_cache.items() if t < cutoff]
            for k in stale:
                _verify_cache.pop(k, None)

    return dict(claims)


# ---------------------------------------------------------------------------
# User registration + custom tokens (Telegram-OTP fallback)
# ---------------------------------------------------------------------------


def register_user_by_phone(phone_e164: str) -> str:
    """Register (or look up) a Firebase Auth user keyed by phone number.

    Used by the Telegram-OTP-verify endpoint to mint a Firebase identity
    for a user who never went through the SMS path.  When a user with
    that phone already exists in Firebase (e.g. a returning tester),
    ``create_user`` raises ``PhoneNumberAlreadyExistsError`` — we catch
    it, look up the existing user with ``get_user_by_phone_number``,
    and return their UID.  Net behaviour: get-or-create by phone.

    Raises :class:`src.api.auth.AuthError` on any other failure (admin
    SDK not initialised, network error, malformed phone, etc.).
    """
    if not is_initialised():
        raise AuthError("firebase admin not initialised")
    from firebase_admin import auth as fb_auth  # type: ignore[import-not-found]

    try:
        record = fb_auth.create_user(phone_number=phone_e164)
        log.info(
            "Registered new Firebase user: uid={}, phone={}",
            record.uid, phone_e164,
        )
        return str(record.uid)
    except fb_auth.PhoneNumberAlreadyExistsError:
        # Already exists — look it up and return its uid.  This is the
        # normal path for returning testers whose phone is in Firebase
        # from a prior SMS sign-in.
        existing = fb_auth.get_user_by_phone_number(phone_e164)
        log.info(
            "Looked up existing Firebase user by phone: uid={}, phone={}",
            existing.uid, phone_e164,
        )
        return str(existing.uid)
    except Exception as exc:
        raise AuthError(f"firebase register_user_by_phone failed: {exc}")


def create_custom_token(firebase_uid: str) -> str:
    """Mint a Firebase custom token for ``firebase_uid``.

    The token is single-use from the app's perspective: the Lumin app
    calls ``FirebaseAuth.instance.signInWithCustomToken(token)`` to
    exchange it for a real Firebase session.  ``firebase_admin`` returns
    ``bytes``; we decode to ``str`` for JSON-friendliness.

    Raises :class:`src.api.auth.AuthError` if the SDK isn't initialised
    or minting fails.
    """
    if not is_initialised():
        raise AuthError("firebase admin not initialised")
    from firebase_admin import auth as fb_auth  # type: ignore[import-not-found]

    try:
        raw = fb_auth.create_custom_token(firebase_uid)
    except Exception as exc:
        raise AuthError(f"firebase create_custom_token failed: {exc}")
    # firebase_admin returns bytes; the JSON response body needs str.
    if isinstance(raw, bytes):
        return raw.decode("ascii")
    return str(raw)


# ---------------------------------------------------------------------------
# Test helper — reset module state between tests
# ---------------------------------------------------------------------------


def reset_for_test() -> None:
    """Drop the cached Firebase app so tests can re-initialise cleanly.

    Mirrors :func:`src.api.users.reset_for_test`.  Production code never
    calls this — the engine initialises once at boot and runs until
    shutdown.
    """
    global _app, _project_id
    with _lock:
        if _app is not None:
            try:
                import firebase_admin  # type: ignore[import-not-found]

                firebase_admin.delete_app(_app)
            except Exception:  # pragma: no cover — best-effort cleanup
                pass
        _app = None
        _project_id = None
    with _verify_cache_lock:
        _verify_cache.clear()
