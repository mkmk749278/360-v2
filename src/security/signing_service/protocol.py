"""Wire protocol for the signing service.

Single-sourced request/response dataclasses + JSON codec so the
client and server use identical shapes.  The wire format is
line-delimited JSON over Unix socket — one JSON object per line,
``\\n`` terminator.  This is debuggable (``socat - UNIX-CONNECT:...``
to poke it manually) and trivially compatible across process
restarts (no shared schema registry needed).

Stability contract: any field added here must be **optional** with
a default, so an older client/server can round-trip with a newer
counterpart.  Field renames are a breaking change and require both
processes to redeploy together.

Verbs supported (the union of what engine workers will need across
PR-5 → PR-9):

* ``ping`` — health check, returns ``ok=True`` without touching KMS.
* ``binance_signed_get`` — sign + GET a Binance endpoint, return body.
* ``binance_signed_post`` — sign + POST a Binance endpoint, return body.
* ``binance_signed_delete`` — sign + DELETE a Binance endpoint
  (needed for order cancels when modifying SL on TP1 fill).

The ``firebase_uid`` field identifies which user's key to use.  The
signing service reads ``users/{firebase_uid}/binance_key/current``
from Firestore via the Admin SDK + unwraps the DEK via KMS — see
:mod:`src.security.signing_service.handler` for the chain.

Error codes are stable strings (not numeric) so callers switch on
them without dragging in a shared enum module.  Treat them like the
``X-Connect-Error-Code`` header values in PR-2: contract surface
that changes only with a roadmap-tier owner discussion.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Literal


# ---------------------------------------------------------------------------
# Verbs + bases
# ---------------------------------------------------------------------------


Verb = Literal[
    "ping",
    "binance_signed_get",
    "binance_signed_post",
    "binance_signed_delete",
]


# Binance base URL selector — strings rather than full URLs so a future
# pivot to testnet / regional endpoints touches only the handler, not
# every call site.
BinanceBase = Literal["spot", "futures"]


# ---------------------------------------------------------------------------
# Error codes — stable contract for callers to switch on
# ---------------------------------------------------------------------------


# No user key blob on file — the user hasn't completed connect yet.
ERR_KEY_BLOB_NOT_FOUND = "KEY_BLOB_NOT_FOUND"

# KMS rejected the Decrypt call (key disabled, IAM revoked, KMS outage).
# Distinct from CRYPTO_DECRYPT_FAILED so callers can decide retry vs
# user-disable: KMS failures are transient, crypto failures are not.
ERR_KMS_DECRYPT_FAILED = "KMS_DECRYPT_FAILED"

# AES-GCM tag verification failed — encrypted blob was tampered or
# the DEK mismatches.  Hard failure: user must reconnect.
ERR_CRYPTO_DECRYPT_FAILED = "CRYPTO_DECRYPT_FAILED"

# Binance returned a 4xx/5xx.  The HTTP status + Binance error code
# are returned in the response body so the caller can map to its
# own retry / user-disable policy (this is what PR-9's drift
# detector consumes).
ERR_BINANCE_HTTP_ERROR = "BINANCE_HTTP_ERROR"

# Network / timeout / aiohttp ClientError reaching Binance.
ERR_BINANCE_UNREACHABLE = "BINANCE_UNREACHABLE"

# Wire-format error: malformed JSON, missing required field, unknown
# verb, unknown base.  Indicates a programming bug, not user state.
ERR_BAD_REQUEST = "BAD_REQUEST"

# Catch-all for unexpected handler exceptions.  Caller treats as
# transient and may retry once.
ERR_INTERNAL_ERROR = "INTERNAL_ERROR"


# ---------------------------------------------------------------------------
# Request / response dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SignRequest:
    """One RPC request from the engine to the signing service.

    ``id`` is a caller-chosen correlation id (typically a uuid).  The
    server echoes it on the response so callers using non-blocking
    sockets can match replies to requests.  For the v1 sync client
    that doesn't strictly matter, but keeping the field on the wire
    means an async client can be dropped in later without protocol
    changes.

    ``firebase_uid`` is the Firestore document key — see
    :func:`src.security.firestore_keystore.get_key_blob`.

    ``params`` are the request parameters (excluding ``timestamp`` +
    ``signature`` which the signing service adds).  For GET they go
    in the query string; for POST/DELETE they go in the body per
    Binance's convention.

    ``recv_window_ms`` is Binance's ``recvWindow`` knob — how many ms
    Binance accepts clock skew on the timestamp.  Default 5000 (5s),
    plenty for engine VPS → Binance latency.
    """

    id: str
    verb: Verb
    firebase_uid: str = ""
    base: BinanceBase = "futures"
    path: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    recv_window_ms: int = 5_000

    def to_json_line(self) -> bytes:
        """Serialise to a single-line JSON byte string with ``\\n`` terminator."""
        return (json.dumps(asdict(self), separators=(",", ":"))).encode("utf-8") + b"\n"

    @classmethod
    def from_json_line(cls, raw: bytes) -> "SignRequest":
        """Parse a line of JSON back into a request.

        Raises :class:`ValueError` on malformed JSON or missing required
        fields — server wraps this into a :class:`SignResponse` with
        ``ERR_BAD_REQUEST`` rather than crashing.
        """
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("request payload must be a JSON object")
        if "id" not in data or "verb" not in data:
            raise ValueError("request missing required fields id / verb")
        return cls(
            id=str(data["id"]),
            verb=data["verb"],
            firebase_uid=str(data.get("firebase_uid", "")),
            base=data.get("base", "futures"),
            path=str(data.get("path", "")),
            params=dict(data.get("params") or {}),
            recv_window_ms=int(data.get("recv_window_ms", 5_000)),
        )


@dataclass(frozen=True)
class SignResponse:
    """One RPC response from the signing service.

    On success (``ok=True``):
      * ``binance_status`` carries the Binance HTTP status code.
      * ``binance_body`` carries the parsed Binance JSON body.
        Already a dict / list — the wire codec handles serialisation.

    On failure (``ok=False``):
      * ``error_code`` is one of the stable ``ERR_*`` constants above.
      * ``error_message`` is a human-readable detail.  May include the
        Binance error code as a string fragment ("Binance returned
        -2014: ...") so caller-side logs are self-contained.
      * ``binance_status`` / ``binance_body`` are populated for
        :data:`ERR_BINANCE_HTTP_ERROR` so the caller can inspect.
        Empty otherwise.
    """

    id: str
    ok: bool
    binance_status: int = 0
    binance_body: Any = None  # dict | list | None
    error_code: str = ""
    error_message: str = ""

    def to_json_line(self) -> bytes:
        return (json.dumps(asdict(self), separators=(",", ":"))).encode("utf-8") + b"\n"

    @classmethod
    def from_json_line(cls, raw: bytes) -> "SignResponse":
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("response payload must be a JSON object")
        return cls(
            id=str(data.get("id", "")),
            ok=bool(data.get("ok", False)),
            binance_status=int(data.get("binance_status", 0)),
            binance_body=data.get("binance_body"),
            error_code=str(data.get("error_code", "")),
            error_message=str(data.get("error_message", "")),
        )

    @classmethod
    def ok_reply(
        cls,
        request_id: str,
        *,
        binance_status: int,
        binance_body: Any,
    ) -> "SignResponse":
        """Construct a success response — terse helper for handler code."""
        return cls(
            id=request_id,
            ok=True,
            binance_status=binance_status,
            binance_body=binance_body,
        )

    @classmethod
    def error_reply(
        cls,
        request_id: str,
        *,
        code: str,
        message: str,
        binance_status: int = 0,
        binance_body: Any = None,
    ) -> "SignResponse":
        """Construct an error response — terse helper for handler code."""
        return cls(
            id=request_id,
            ok=False,
            error_code=code,
            error_message=message,
            binance_status=binance_status,
            binance_body=binance_body,
        )
