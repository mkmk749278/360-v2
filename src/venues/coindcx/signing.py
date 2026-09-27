"""CoinDCX request signing — pure functions, no I/O, no logging.

CoinDCX authenticates a private call with two headers:

* ``X-AUTH-APIKEY`` — the public key;
* ``X-AUTH-SIGNATURE`` — hex HMAC-SHA256 of the **exact** JSON body sent,
  keyed by the secret.

The body must carry a millisecond ``timestamp`` (CoinDCX rejects an order
more than 10 seconds late), and it must be serialised once and sent as those
same bytes: re-serialising after signing (key order, spaces) invalidates the
signature.  :func:`signed_request` therefore returns the body *as text*.

The private stream authenticates with an HMAC of the constant payload
``{"channel":"coindcx"}``.  That signature never changes for a key, so it is a
long-lived credential for **reading** the user's own futures events (it cannot
place or cancel anything).  It is produced only inside the signing service,
never logged, and held in memory by the stream task alone.

The secret is a parameter of these functions and nothing here stores,
returns or formats it.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Mapping, Optional

BASE_URL = "https://api.coindcx.com"
STREAM_URL = "wss://stream.coindcx.com"

#: The only private endpoints any caller may reach through the signing
#: service, with the HTTP method each takes.  An allow-list, not a prefix: a
#: path added here is a decision about what our custody of a user's key may
#: do, and it is made in a diff a reviewer reads.  There is no wallet-transfer,
#: no withdrawal and no spot path in it.
PRIVATE_ENDPOINTS: Mapping[str, str] = {
    "/exchange/v1/derivatives/futures/orders/create": "POST",
    "/exchange/v1/derivatives/futures/orders/cancel": "POST",
    "/exchange/v1/derivatives/futures/orders": "POST",
    "/exchange/v1/derivatives/futures/positions": "POST",
    "/exchange/v1/derivatives/futures/positions/create_tpsl": "POST",
    "/exchange/v1/derivatives/futures/positions/exit": "POST",
    "/exchange/v1/derivatives/futures/positions/update_leverage": "POST",
    "/exchange/v1/derivatives/futures/positions/margin_type": "POST",
    "/exchange/v1/derivatives/futures/positions/cancel_all_open_orders_for_position": "POST",
    "/exchange/v1/derivatives/futures/trades": "POST",
    "/exchange/v1/derivatives/futures/wallets": "GET",
}

_STREAM_AUTH_BODY = json.dumps({"channel": "coindcx"}, separators=(",", ":"))


def is_allowed(path: str, method: str) -> bool:
    """True iff ``method path`` is on :data:`PRIVATE_ENDPOINTS`."""
    return PRIVATE_ENDPOINTS.get(path) == method.upper()


def hmac_hex(secret: str, payload: str) -> str:
    """Hex HMAC-SHA256 of ``payload`` keyed by ``secret``."""
    return hmac.new(
        secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def canonical_body(body: Optional[Mapping[str, Any]], *, now_ms: Optional[int] = None) -> str:
    """Serialise ``body`` with a fresh millisecond ``timestamp``.

    Compact separators, insertion order preserved — the text returned is the
    text that must be both signed and sent.  A caller-supplied ``timestamp``
    is overwritten: a stale one is exactly what CoinDCX's 10-second rule
    refuses, and only the signer knows when the request actually leaves.
    """
    out = dict(body or {})
    out["timestamp"] = int(now_ms if now_ms is not None else time.time() * 1000)
    return json.dumps(out, separators=(",", ":"))


def signed_request(
    api_key: str,
    api_secret: str,
    body: Optional[Mapping[str, Any]],
    *,
    now_ms: Optional[int] = None,
) -> tuple[str, dict]:
    """Return ``(body_text, headers)`` for one private call."""
    text = canonical_body(body, now_ms=now_ms)
    headers = {
        "Content-Type": "application/json",
        "X-AUTH-APIKEY": api_key,
        "X-AUTH-SIGNATURE": hmac_hex(api_secret, text),
    }
    return text, headers


def stream_auth_signature(api_secret: str) -> str:
    """The ``authSignature`` for joining the private ``coindcx`` channel."""
    return hmac_hex(api_secret, _STREAM_AUTH_BODY)
