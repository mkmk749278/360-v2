"""Engine-side client for the signing service.

Hides the Unix-socket + line-delimited-JSON wire format from callers
— they get a typed ``async`` function that returns a parsed
:class:`SignResponse`.

Usage from a per-user worker (the pattern PR-5 + PR-6 will land):

    client = SigningClient()
    resp = await client.binance_signed_get(
        firebase_uid="...",
        base="futures",
        path="/fapi/v2/balance",
    )
    if resp.ok:
        balances = resp.binance_body
    else:
        log.warning("signing failed: {} {}", resp.error_code, resp.error_message)

Connection model:

* One :class:`SigningClient` per worker / call site.  Each call opens
  a fresh Unix-socket connection, sends one request, reads one
  response, closes.  Per-request connect cost on a Unix socket is
  ~50 µs — far below the cost of the Binance HTTP call the signing
  service makes inside.
* A pooled-connection mode is a follow-up if telemetry shows the
  connect cost matters; the wire protocol already supports
  request-id correlation so pooling drops in without changes.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from typing import Any, Dict, Optional

from src.utils import get_logger

from .protocol import (
    ERR_BINANCE_UNREACHABLE,
    SignRequest,
    SignResponse,
)

log = get_logger("security.signing_service.client")


_DEFAULT_SOCKET_PATH = "/var/run/lumin/signing.sock"
_DEFAULT_TIMEOUT_S = 12.0

# asyncio's StreamReader defaults to a 64 KiB line limit. Signed-GET
# responses are returned as a single JSON line, and the largest of them —
# GET /fapi/v2/positionRisk with no symbol filter — carries EVERY symbol's
# position. As Binance kept adding perpetual listings that line crossed
# 64 KiB, so the engine-side ``readline`` raised
# ``ValueError: Separator is not found, and chunk exceed the limit`` and the
# reconciler silently skipped reconciliation for affected users every cycle.
# Raise the read buffer generously. The buffer only grows to the actual line
# size, so a roomy ceiling costs nothing on normal (small) responses while
# bounding pathological ones.
_SOCKET_READ_LIMIT = 16 * 1024 * 1024  # 16 MiB


class SigningClient:
    """Thin client for the signing-service Unix socket.

    All public methods are ``async`` and return :class:`SignResponse`.
    Methods never raise on signing failure — they return a response
    with ``ok=False`` and a stable ``error_code``.  Callers switch
    on ``resp.error_code`` to decide retry / disable / propagate.

    Methods DO raise on:
      * Unix socket missing / permission denied — programming or
        deployment bug, not user state.  Surface as standard OSError.
      * Timeout — the signing service has not responded within
        ``timeout``.  Treated as transient; caller may retry.  Raised
        as :class:`asyncio.TimeoutError`.
    """

    def __init__(
        self,
        socket_path: Optional[str] = None,
        timeout: float = _DEFAULT_TIMEOUT_S,
    ) -> None:
        self.socket_path = socket_path or os.environ.get(
            "SIGNING_SERVICE_SOCKET_PATH", _DEFAULT_SOCKET_PATH
        )
        self.timeout = timeout

    async def _rpc(self, request: SignRequest) -> SignResponse:
        """One-shot request/response over a fresh Unix-socket connection."""
        async with _SignClientConn(self.socket_path) as conn:
            return await asyncio.wait_for(
                conn.send_and_receive(request), timeout=self.timeout
            )

    async def ping(self) -> SignResponse:
        """Health check.  Doesn't touch KMS / Firestore — useful for
        liveness probes."""
        return await self._rpc(SignRequest(id=_new_id(), verb="ping"))

    async def binance_signed_get(
        self,
        *,
        firebase_uid: str,
        base: str = "futures",
        path: str = "",
        params: Optional[Dict[str, Any]] = None,
    ) -> SignResponse:
        return await self._rpc(
            SignRequest(
                id=_new_id(),
                verb="binance_signed_get",
                firebase_uid=firebase_uid,
                base=base,
                path=path,
                params=dict(params or {}),
            )
        )

    async def binance_signed_post(
        self,
        *,
        firebase_uid: str,
        base: str = "futures",
        path: str = "",
        params: Optional[Dict[str, Any]] = None,
    ) -> SignResponse:
        return await self._rpc(
            SignRequest(
                id=_new_id(),
                verb="binance_signed_post",
                firebase_uid=firebase_uid,
                base=base,
                path=path,
                params=dict(params or {}),
            )
        )

    async def binance_signed_delete(
        self,
        *,
        firebase_uid: str,
        base: str = "futures",
        path: str = "",
        params: Optional[Dict[str, Any]] = None,
    ) -> SignResponse:
        return await self._rpc(
            SignRequest(
                id=_new_id(),
                verb="binance_signed_delete",
                firebase_uid=firebase_uid,
                base=base,
                path=path,
                params=dict(params or {}),
            )
        )


def _new_id() -> str:
    """Generate a fresh request id.  uuid4 is fine — the only invariant
    is uniqueness within a connection's open lifetime (which lasts one
    request)."""
    return uuid.uuid4().hex


class _SignClientConn:
    """One-shot Unix-socket conversation: open → write line → read line → close.

    Implemented as an async context manager so the close is automatic
    + the socket fd is released even on exceptions.
    """

    def __init__(self, socket_path: str) -> None:
        self.socket_path = socket_path
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None

    async def __aenter__(self) -> "_SignClientConn":
        self._reader, self._writer = await asyncio.open_unix_connection(
            self.socket_path, limit=_SOCKET_READ_LIMIT
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._writer is not None:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass

    async def send_and_receive(self, request: SignRequest) -> SignResponse:
        assert self._reader is not None and self._writer is not None
        self._writer.write(request.to_json_line())
        await self._writer.drain()
        line = await self._reader.readline()
        if not line:
            # Server closed without responding.  Treat as transient
            # unreachable; caller decides whether to retry.
            return SignResponse.error_reply(
                request_id=request.id,
                code=ERR_BINANCE_UNREACHABLE,
                message="signing service closed connection without responding",
            )
        return SignResponse.from_json_line(line)
