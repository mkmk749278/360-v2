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

import threading
from typing import Any, Dict, Optional

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
# Init
# ---------------------------------------------------------------------------


def init_firebase_admin(service_account_path: str, project_id: str) -> None:
    """Initialise the Firebase Admin SDK against the configured project.

    Idempotent — a second call with the same args is a no-op.  Errors
    while loading the credential JSON or calling ``initialize_app``
    propagate to the caller, which is expected to wrap this in a
    try/except so a missing / bad service-account file doesn't crash
    engine boot (the engine should still be able to serve via the
    legacy HS256 path).
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
    """
    if not is_initialised():
        raise AuthError("firebase admin not initialised")
    # Lazy import here too — the module-level path stays cheap for
    # processes that never call ``verify_id_token`` (e.g. the test
    # harness that mocks this function).
    from firebase_admin import auth as fb_auth  # type: ignore[import-not-found]

    try:
        return fb_auth.verify_id_token(id_token)
    except Exception as exc:
        # firebase_admin.auth raises a number of distinct exception
        # types (ExpiredIdTokenError, RevokedIdTokenError,
        # InvalidIdTokenError, …).  Collapse them all to AuthError
        # with the underlying message — the caller doesn't care WHY
        # the token failed, only that it did.
        raise AuthError(f"firebase id-token verification failed: {exc}")


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
