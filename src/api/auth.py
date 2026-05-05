"""JWT auth — anonymous device-bound tokens for the Lumin app.

Goal: zero manual token entry on the client.  An app's first request
mints an anonymous JWT bound to a random device id; the JWT is stored
on-device in encrypted secure storage and silently refreshed before
expiry.  When the server's signing secret is rotated, every existing
JWT becomes invalid; the client catches the next 401 and re-mints
transparently — no APK rebuild, no token in any chat ever again.

Tier model: every JWT carries a ``tier`` claim.  In the testing phase
all clients receive ``tier="all-access"`` so every endpoint serves
full data.  Later, when the subscription path lands, paid users will
receive ``tier="paid"`` JWTs minted off a different code path; the
endpoint handlers don't change.

Implementation: pure stdlib HS256 — no third-party JWT library.  HS256
needs only ``hmac`` + ``hashlib`` + base64url + json, which removes a
dependency (``PyJWT``) and the cryptography toolchain it pulls in.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from src.utils import get_logger

log = get_logger("api.auth")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


_ALG = "HS256"
_HEADER = {"alg": _ALG, "typ": "JWT"}

# JWTs expire after this window.  Long enough that a phone left untouched
# for a few days still wakes up to a valid token; short enough that a
# stolen JWT loses value quickly.
DEFAULT_TOKEN_TTL = timedelta(days=7)

ALL_ACCESS_TIER = "all-access"
PAID_TIER = "paid"
FREE_TIER = "free"


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


@dataclass
class TokenClaims:
    """Decoded JWT payload — what every authenticated request carries."""

    sub: str  # device-<uuid> for anonymous, user-<id> when subscriptions land
    tier: str
    iat: datetime
    exp: datetime

    @property
    def is_paid(self) -> bool:
        return self.tier in (ALL_ACCESS_TIER, PAID_TIER)


class AuthError(Exception):
    """Raised by ``decode_token`` when the JWT is invalid or expired."""


# ---------------------------------------------------------------------------
# Base64url helpers (RFC 7515 — JWS uses no-padding base64url)
# ---------------------------------------------------------------------------


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _json_compact(obj: Dict[str, Any]) -> bytes:
    # Compact separators + sorted keys → deterministic encoding so the
    # signed bytes are stable regardless of insertion order.
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")


# ---------------------------------------------------------------------------
# Sign / verify
# ---------------------------------------------------------------------------


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _sign(signing_input: bytes, secret: str) -> str:
    sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return _b64url_encode(sig)


def mint_token(
    *,
    secret: str,
    sub: Optional[str] = None,
    tier: str = ALL_ACCESS_TIER,
    ttl: timedelta = DEFAULT_TOKEN_TTL,
) -> str:
    """Mint a fresh JWT.  ``sub`` defaults to a random device id."""
    if not secret:
        raise ValueError("JWT secret not configured (API_JWT_SECRET)")
    now = _now()
    sub = sub or f"device-{secrets.token_hex(8)}"
    payload = {
        "sub": sub,
        "tier": tier,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
    }
    header_b64 = _b64url_encode(_json_compact(_HEADER))
    payload_b64 = _b64url_encode(_json_compact(payload))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    sig_b64 = _sign(signing_input, secret)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_token(token: str, *, secret: str) -> TokenClaims:
    """Verify a JWT and return its claims.  Raises ``AuthError`` on failure."""
    if not secret:
        raise AuthError("JWT secret not configured")

    parts = token.split(".")
    if len(parts) != 3:
        raise AuthError("invalid token: not three parts")
    header_b64, payload_b64, sig_b64 = parts

    # Constant-time signature check
    expected = _sign(f"{header_b64}.{payload_b64}".encode("ascii"), secret)
    if not hmac.compare_digest(expected, sig_b64):
        raise AuthError("invalid token: signature mismatch")

    try:
        header = json.loads(_b64url_decode(header_b64))
        payload = json.loads(_b64url_decode(payload_b64))
    except (ValueError, json.JSONDecodeError) as exc:
        raise AuthError(f"invalid token: malformed json ({exc})")

    if header.get("alg") != _ALG:
        raise AuthError(f"invalid token: unexpected alg {header.get('alg')!r}")

    try:
        sub = str(payload["sub"])
        tier = str(payload.get("tier", FREE_TIER))
        iat = datetime.fromtimestamp(int(payload["iat"]), tz=timezone.utc)
        exp = datetime.fromtimestamp(int(payload["exp"]), tz=timezone.utc)
    except (KeyError, TypeError, ValueError) as exc:
        raise AuthError(f"malformed token payload: {exc}")

    if _now() >= exp:
        raise AuthError("token expired")

    return TokenClaims(sub=sub, tier=tier, iat=iat, exp=exp)


def refresh_token(token: str, *, secret: str, ttl: timedelta = DEFAULT_TOKEN_TTL) -> str:
    """Issue a new JWT carrying the same ``sub`` + ``tier`` for a fresh window.

    The current token must still be valid; expired tokens cannot be
    refreshed (the client must call /api/auth/anonymous instead).  This
    is the design: a leaked JWT can be used to refresh itself, but only
    until natural expiry — limiting window-of-abuse without forcing an
    explicit refresh-token round-trip on every fetch.
    """
    claims = decode_token(token, secret=secret)
    return mint_token(secret=secret, sub=claims.sub, tier=claims.tier, ttl=ttl)
