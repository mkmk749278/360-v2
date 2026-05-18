"""Binance connect-time validation — the security-critical gate for B18.

Run once per user when they POST their Binance API key + secret to
``/api/binance/connect`` (see :mod:`src.api.binance_connect_routes`).
The validator enforces ``OWNER_BRIEF B18``'s non-negotiable rules:

1. Withdraw permission must be DISABLED.  Auto-reject if enabled —
   no permissive mode, no admin override.
2. Futures permission must be ENABLED (otherwise the user can't
   trade futures with us).
3. IP whitelist must be enabled AND the engine VPS IP must be on it.
   Verified indirectly: if ``ipRestrict=true`` AND a signed call from
   the engine VPS succeeds, then by definition our IP is on the list
   (otherwise Binance would have returned ``-2014/IP not whitelisted``).
4. The key must actually work for Futures — verified by a no-op
   signed call to ``/fapi/v2/balance``.

The plaintext secret arrives via the connect endpoint (HTTPS only),
flows into this validator's signing helper, and is dropped as soon as
this function returns.  It is NEVER logged, NEVER persisted in the
clear, NEVER returned to a caller outside the connect flow.  The
encryption + storage happens in the route handler AFTER this validator
returns success — see :mod:`src.api.binance_connect_routes` for the
provisioning chain.

Failure taxonomy: each connect-time check raises a specific exception
subclass so the route can map it to a precise HTTP 400 detail.  Users
need to know *which* setting on Binance to fix, not just "invalid key."
"""

from __future__ import annotations

import hashlib
import hmac
import time
import urllib.parse
from dataclasses import dataclass
from typing import Any, Dict, Optional

import aiohttp

from src.utils import get_logger

log = get_logger("security.binance_connect_validator")


_SPOT_BASE = "https://api.binance.com"
_FUTURES_BASE = "https://fapi.binance.com"
_REQUEST_TIMEOUT_S = 8.0
_RECV_WINDOW_MS = 5_000


# ---------------------------------------------------------------------------
# Errors — each maps to a precise user-facing connect-flow message
# ---------------------------------------------------------------------------


class BinanceConnectValidationError(Exception):
    """Base class for connect-time validation failures.

    Subclasses map to specific HTTP 400 detail strings the route
    surfaces to the user so they know which Binance setting to fix.
    """

    user_message: str = "Binance API key validation failed."


class WithdrawEnabledError(BinanceConnectValidationError):
    user_message = (
        "Your Binance API key has WITHDRAWAL permission enabled. "
        "Lumin requires withdrawal to be DISABLED on connected keys "
        "(this is the core safety property — even in a worst-case "
        "breach an attacker cannot drain your wallet). Edit your key "
        "in Binance → API Management, uncheck 'Enable Withdrawals', "
        "save, and try again."
    )


class FuturesDisabledError(BinanceConnectValidationError):
    user_message = (
        "Your Binance API key does not have FUTURES permission enabled. "
        "Edit your key in Binance → API Management, check 'Enable Futures', "
        "save, and try again."
    )


class IpRestrictDisabledError(BinanceConnectValidationError):
    user_message = (
        "Your Binance API key does not have IP whitelist enabled. "
        "Binance requires IP whitelist on any Futures-trade-enabled key. "
        "Edit your key in Binance → API Management, select 'Restrict access "
        "to trusted IPs only', add Lumin's engine IP, save, and try again."
    )


class IpNotWhitelistedError(BinanceConnectValidationError):
    """Engine VPS IP is not on the user's whitelist.

    Surfaced when a signed request from the engine VPS returns
    ``-2014`` (IP not whitelisted).  The route adds the engine VPS IP
    to the user message so the user knows exactly what to whitelist.
    """

    user_message = (
        "Your Binance API key's IP whitelist does not include Lumin's "
        "engine IP. Add the IP shown in the connect flow to your key's "
        "whitelist in Binance → API Management, save, and try again."
    )


class KeyInvalidError(BinanceConnectValidationError):
    user_message = (
        "Your Binance API key or secret is invalid. Double-check both "
        "values were copied without leading/trailing whitespace, then "
        "try again. If the key was recently regenerated on Binance, "
        "ensure you copied the NEW key, not the old one."
    )


class BinanceUnreachableError(BinanceConnectValidationError):
    """Binance API unreachable (network / timeout / 5xx).

    Distinct from key-invalid — caller should retry rather than ask
    the user to fix anything.  Surfaced as HTTP 503 by the route.
    """

    user_message = (
        "Could not reach Binance to validate your key. Please try again "
        "in a moment. If this persists, Binance may be having an outage."
    )


# ---------------------------------------------------------------------------
# Validation result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BinanceKeyValidation:
    """Successful validation result returned to the route handler.

    Persisted alongside the encrypted secret (see
    :func:`src.security.firestore_keystore.put_key_blob`) so future
    drift-detection runs can compare against the at-connect baseline.
    """

    # All three are True on a successful validation — they're flags
    # rather than implied because the route may want to display them
    # back to the user as a confirmation summary ("✓ Futures enabled,
    # ✓ Withdrawals disabled, ✓ IP whitelist OK").
    withdraw_disabled_ok: bool
    futures_enabled_ok: bool
    ip_whitelist_ok: bool


# ---------------------------------------------------------------------------
# Signed-request helper
# ---------------------------------------------------------------------------


def _sign_query(api_secret: str, query: str) -> str:
    """HMAC-SHA256-sign the query string with the user's API secret.

    Returns the hex-encoded signature.  Caller appends as ``&signature=<sig>``.
    The plaintext secret is held in this function's local scope for
    the duration of the HMAC compute and dropped on return.
    """
    return hmac.new(
        api_secret.encode("utf-8"),
        query.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


async def _signed_get(
    api_key: str,
    api_secret: str,
    base_url: str,
    path: str,
    params: Optional[Dict[str, Any]] = None,
    session: Optional[aiohttp.ClientSession] = None,
) -> Dict[str, Any]:
    """Perform a signed GET against Binance.  Returns the parsed JSON body.

    Raises:
      * :class:`BinanceUnreachableError` on network / 5xx — caller should
        treat as transient.
      * :class:`KeyInvalidError` on 401 ``-2015`` (bad signature / bad key).
      * :class:`IpNotWhitelistedError` on 401 ``-2014`` (IP not on the
        whitelist for this key — the SPECIFIC error we map to a fix-up
        message at the route layer).
      * Generic :class:`BinanceConnectValidationError` on other 4xx (e.g.
        permission missing) with the raw Binance error code in the message
        so the route can inspect.

    Does NOT log the api_key, api_secret, or the signed URL.  Logs the
    response status + error code (which is safe — no key material).
    """
    full_params: Dict[str, Any] = dict(params or {})
    full_params["timestamp"] = int(time.time() * 1000)
    full_params["recvWindow"] = _RECV_WINDOW_MS
    query = urllib.parse.urlencode(full_params)
    sig = _sign_query(api_secret, query)
    url = f"{base_url}{path}?{query}&signature={sig}"
    headers = {"X-MBX-APIKEY": api_key}

    own_session = session is None
    if session is None:
        session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=_REQUEST_TIMEOUT_S)
        )
    try:
        async with session.get(url, headers=headers) as resp:
            status_code = resp.status
            try:
                body: Dict[str, Any] = await resp.json(content_type=None)
            except (aiohttp.ContentTypeError, ValueError):
                body = {}
            if status_code == 200:
                return body
            # Binance 4xx error codes — see
            # https://binance-docs.github.io/apidocs/futures/en/#error-codes
            code = body.get("code")
            if code == -2014:
                # "API-key format invalid" OR "this IP is not in the whitelist".
                # Binance overloads -2014; the message text disambiguates.
                msg = str(body.get("msg") or "").lower()
                if "ip" in msg or "whitelist" in msg:
                    raise IpNotWhitelistedError(IpNotWhitelistedError.user_message)
                raise KeyInvalidError(KeyInvalidError.user_message)
            if code == -2015:
                raise KeyInvalidError(KeyInvalidError.user_message)
            if 500 <= status_code < 600:
                raise BinanceUnreachableError(
                    f"Binance returned {status_code} on {path}"
                )
            # Anything else: surface raw code so the route can decide.
            raise BinanceConnectValidationError(
                f"Binance rejected key validation on {path}: "
                f"status={status_code}, code={code}"
            )
    except aiohttp.ClientError as exc:
        raise BinanceUnreachableError(f"network error calling {path}: {exc}")
    finally:
        if own_session:
            await session.close()


# ---------------------------------------------------------------------------
# Public API — what the route calls
# ---------------------------------------------------------------------------


async def validate_binance_key(
    api_key: str,
    api_secret: str,
    session: Optional[aiohttp.ClientSession] = None,
) -> BinanceKeyValidation:
    """Run all B18 connect-time checks against the supplied key.

    Returns :class:`BinanceKeyValidation` on success.  Raises a
    specific :class:`BinanceConnectValidationError` subclass on any
    failure so the route can surface the precise fix-up instruction.

    The check sequence is intentional:

    1. ``/sapi/v1/account/apiRestrictions`` — single round-trip that
       returns withdraw + futures + ipRestrict flags.  If the IP isn't
       whitelisted this call itself fails with ``-2014``, which we
       surface as :class:`IpNotWhitelistedError` — saving the user a
       trip to look up the failing check.
    2. Flag checks in the order users care about: withdraw (most
       common misconfiguration), futures-enabled, ip-restrict-enabled.
    3. ``/fapi/v2/balance`` — confirms Futures-specific access works
       (some accounts have Futures enabled per the flag but the
       Futures wallet itself isn't activated).

    The api_key + api_secret are passed by reference through this
    function and the signed-request helper.  Neither is ever logged.
    Both should be wiped from caller-side variables as soon as this
    function returns — see the route handler's `finally` block.
    """
    # Step 1: read the key's permission flags.
    restrictions = await _signed_get(
        api_key=api_key,
        api_secret=api_secret,
        base_url=_SPOT_BASE,
        path="/sapi/v1/account/apiRestrictions",
        session=session,
    )

    # Step 2: enforce B18 rules in user-priority order.
    if bool(restrictions.get("enableWithdrawals", False)):
        raise WithdrawEnabledError(WithdrawEnabledError.user_message)
    if not bool(restrictions.get("enableFutures", False)):
        raise FuturesDisabledError(FuturesDisabledError.user_message)
    if not bool(restrictions.get("ipRestrict", False)):
        raise IpRestrictDisabledError(IpRestrictDisabledError.user_message)

    # Step 3: confirm Futures access actually works.  If the user
    # toggled Futures on but never activated the futures wallet,
    # the flag passes but trades will fail at execution time.  Catch
    # it now rather than at first auto-trade.
    await _signed_get(
        api_key=api_key,
        api_secret=api_secret,
        base_url=_FUTURES_BASE,
        path="/fapi/v2/balance",
        session=session,
    )

    log.info(
        "Binance key validation passed: "
        "withdraw_disabled=ok, futures_enabled=ok, ip_whitelist=ok"
    )
    return BinanceKeyValidation(
        withdraw_disabled_ok=True,
        futures_enabled_ok=True,
        ip_whitelist_ok=True,
    )
