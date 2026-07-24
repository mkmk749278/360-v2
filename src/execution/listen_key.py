"""Binance Futures User Data Stream listenKey lifecycle.

Binance gates User Data Stream access behind a per-user listenKey:

1. POST ``/fapi/v1/listenKey`` (signed) → returns ``{"listenKey": "..."}``
   valid for 60 minutes.
2. Connect WebSocket to
   ``wss://fstream.binance.com/private/ws?listenKey=<listenKey>&events=...``.
3. PUT ``/fapi/v1/listenKey`` every <60 minutes to extend.  Default
   keepalive cadence is 30 minutes to leave headroom for network
   hiccups + retries.
4. DELETE ``/fapi/v1/listenKey`` (signed) on shutdown so Binance can
   reclaim resources.

If we miss enough keepalives the stream emits ``listenKeyExpired``,
we close the WS, and we obtain a new listenKey (per-user, not per-
connection — Binance returns the same active key if there is one).

All three signed calls go through the signing service from PR-4 so
the engine main process never touches the user's API secret.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional

from src.security.signing_service import client as signing_client
from src.utils import get_logger

log = get_logger("execution.listen_key")


_LISTEN_KEY_PATH = "/fapi/v1/listenKey"
_KEEPALIVE_INTERVAL_S = 30 * 60  # 30 minutes — half of Binance's 60-min expiry


class ListenKeyError(Exception):
    """Base — caller handles by closing the worker and retrying later."""


class ListenKeyAcquireError(ListenKeyError):
    """Could not acquire a listenKey (signing service error, Binance
    error, or user key invalid).

    Carries the Binance status/code so the worker can distinguish a
    *permanent* auth failure (dead/invalid key — 401 / ``-2015``) and an
    *IP ban* (``418`` / ``-1003``) from a transient blip, and back off
    accordingly instead of hammering a dead key into a ban.
    """

    def __init__(
        self,
        message: str,
        *,
        binance_status: Optional[int] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        # ``binance_status`` is the Binance HTTP status (401/418/…), the
        # reliable classification signal. ``error_code`` is the signing
        # service's own ``ERR_*`` constant (a string, e.g.
        # "BINANCE_HTTP_ERROR"), NOT the numeric Binance code — that
        # (``-2015``/``-1003``) lives in ``error_message``, so we substring it.
        self.binance_status = binance_status
        self.error_code = error_code
        self.error_message = error_message

    @property
    def is_auth_failure(self) -> bool:
        """Dead/invalid key: HTTP 401, or Binance ``-2015`` (bad key/IP/
        permission) in the message.

        Retrying this fast is pointless and — via the resulting request
        storm — actively dangerous (it earns the IP ban below).
        """
        if self.binance_status == 401:
            return True
        return "-2015" in (self.error_message or "")

    @property
    def is_ip_ban(self) -> bool:
        """The whole box is IP-banned (HTTP 418/403, Binance ``-1003``).
        Retrying into an active ban only extends it — back off for the window."""
        if self.binance_status in (418, 403):
            return True
        return "-1003" in (self.error_message or "")


class ListenKeyKeepaliveError(ListenKeyError):
    """Keepalive PUT failed — typically transient.  Caller's reconnect
    loop should drop the WS and re-acquire on the next attempt."""


@dataclass
class ListenKeyHandle:
    """Live handle to a listenKey + its background keepalive task.

    Constructed by :func:`acquire`.  The keepalive task runs as long as
    :meth:`close` hasn't been called; close stops the task and DELETEs
    the key with Binance.
    """

    listen_key: str
    firebase_uid: str
    _keepalive_task: Optional[asyncio.Task] = None
    _client: Optional[signing_client.SigningClient] = None

    async def close(self) -> None:
        """Stop the keepalive task + DELETE the listenKey at Binance.

        Idempotent — calling twice is safe.  Errors during DELETE are
        logged but not raised; Binance will reap the key after 60min
        of inactivity anyway, so a failed cleanup is not user-visible.
        """
        if self._keepalive_task is not None and not self._keepalive_task.done():
            self._keepalive_task.cancel()
            try:
                await self._keepalive_task
            except (asyncio.CancelledError, Exception):
                pass
        self._keepalive_task = None
        if self._client is None:
            return
        try:
            resp = await self._client.binance_signed_delete(
                firebase_uid=self.firebase_uid,
                base="futures",
                path=_LISTEN_KEY_PATH,
            )
            if not resp.ok:
                log.warning(
                    "listenKey DELETE returned error: uid={} code={}",
                    self.firebase_uid,
                    resp.error_code,
                )
        except Exception as exc:
            log.warning(
                "listenKey DELETE raised: uid={} exc={}", self.firebase_uid, exc
            )


async def acquire(
    firebase_uid: str,
    *,
    client: Optional[signing_client.SigningClient] = None,
    keepalive_interval_s: float = _KEEPALIVE_INTERVAL_S,
) -> ListenKeyHandle:
    """Acquire a listenKey for ``firebase_uid`` and start its keepalive.

    Returns a :class:`ListenKeyHandle` that the caller passes to
    :func:`src.execution.user_data_stream.consume` and eventually
    closes via :meth:`ListenKeyHandle.close`.

    Raises :class:`ListenKeyAcquireError` on signing failure / Binance
    rejection / missing field in response.  The caller's worker
    treats this as a hard failure for this iteration of the
    reconnect loop and backs off before retrying.

    ``client`` injectable so tests don't need a live Unix socket.
    """
    if client is None:
        client = signing_client.SigningClient()
    resp = await client.binance_signed_post(
        firebase_uid=firebase_uid,
        base="futures",
        path=_LISTEN_KEY_PATH,
    )
    if not resp.ok:
        raise ListenKeyAcquireError(
            f"listenKey POST failed: code={resp.error_code} "
            f"binance_status={resp.binance_status} "
            f"message={resp.error_message}",
            binance_status=resp.binance_status,
            error_code=resp.error_code,
            error_message=resp.error_message,
        )
    listen_key = (resp.binance_body or {}).get("listenKey")
    if not isinstance(listen_key, str) or not listen_key:
        raise ListenKeyAcquireError(
            f"listenKey response missing 'listenKey' field: body={resp.binance_body!r}"
        )
    handle = ListenKeyHandle(
        listen_key=listen_key,
        firebase_uid=firebase_uid,
        _client=client,
    )
    # Spawn keepalive as a background task.  The caller's worker holds
    # the handle and will close it on shutdown; we don't need an
    # explicit reference here beyond the dataclass attribute.
    handle._keepalive_task = asyncio.create_task(
        _keepalive_loop(handle, keepalive_interval_s)
    )
    log.info(
        "listenKey acquired: uid={} key_prefix={}",
        firebase_uid,
        listen_key[:8],
    )
    return handle


async def _keepalive_loop(
    handle: ListenKeyHandle, interval_s: float
) -> None:
    """Periodically PUT the listenKey to extend its lifetime.

    Runs until the handle is closed.  PUT failures are logged but
    don't tear the task down — the worker's WS-disconnect handler
    will notice if the key actually expired (via the
    ``listenKeyExpired`` event from Binance) and re-acquire.
    """
    while True:
        try:
            await asyncio.sleep(interval_s)
        except asyncio.CancelledError:
            return
        if handle._client is None:
            return
        try:
            resp = await handle._client.binance_signed_post(
                firebase_uid=handle.firebase_uid,
                base="futures",
                path=_LISTEN_KEY_PATH,
            )
            if not resp.ok:
                log.warning(
                    "listenKey keepalive failed: uid={} code={}",
                    handle.firebase_uid,
                    resp.error_code,
                )
            else:
                log.debug(
                    "listenKey keepalive ok: uid={} key_prefix={}",
                    handle.firebase_uid,
                    handle.listen_key[:8],
                )
        except Exception as exc:
            log.warning(
                "listenKey keepalive raised: uid={} exc={}",
                handle.firebase_uid,
                exc,
            )
