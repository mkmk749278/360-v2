"""Asyncio Unix-socket server that hosts the signing-service handler.

One server process listens on a Unix-domain socket (path configured
via ``SIGNING_SERVICE_SOCKET_PATH`` env var; default
``/var/run/lumin/signing.sock``).  Each accepted connection is
handled by :func:`_handle_connection`, which reads line-delimited
JSON requests, dispatches each to :func:`handler.handle_request`,
and writes the JSON-encoded response back.

Concurrency: each connection gets its own asyncio task; the handler
itself shares one aiohttp session across all requests (passed via
the dispatch helper) to avoid TCP-connect churn against Binance.

Lifecycle:

* :func:`run` is the entry point.  Initialises KMS + Firestore +
  the shared aiohttp session, then ``asyncio.start_unix_server``s
  on the socket path with mode ``0660``.  On SIGTERM / SIGINT,
  closes the session + server cleanly.
* Socket permissions: created mode ``0660`` so only members of the
  socket's group can connect.  In production the socket is
  owned by ``lumin-signer:lumin-engine`` so engine workers (running
  as ``lumin-engine``) can connect but no other VPS user can.
"""

from __future__ import annotations

import asyncio
import os
import signal
from typing import Optional

import aiohttp

from src.utils import get_logger

from . import handler as _handler
from .protocol import (
    ERR_BAD_REQUEST,
    ERR_INTERNAL_ERROR,
    SignRequest,
    SignResponse,
)

log = get_logger("security.signing_service.server")


# Where the Unix socket lives.  Configurable via env so tests can
# point at a per-test tempdir and production can point at
# ``/var/run/lumin/`` without code changes.
_DEFAULT_SOCKET_PATH = "/var/run/lumin/signing.sock"


def _socket_path() -> str:
    return os.environ.get("SIGNING_SERVICE_SOCKET_PATH", _DEFAULT_SOCKET_PATH)


async def _handle_connection(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    *,
    session: aiohttp.ClientSession,
) -> None:
    """Serve one client connection until EOF.

    Reads one JSON line per request, dispatches, writes one JSON
    line per response.  Malformed input produces a typed
    :data:`ERR_BAD_REQUEST` response with no ``id`` echo (we couldn't
    parse one); the client should treat this as a programming bug.
    """
    peer = writer.get_extra_info("peername")
    log.debug("signing service: new connection peer={}", peer)
    try:
        while True:
            try:
                line = await reader.readline()
            except asyncio.IncompleteReadError:
                break
            if not line:
                break  # client closed
            try:
                request = SignRequest.from_json_line(line)
            except ValueError as exc:
                resp = SignResponse.error_reply(
                    request_id="",
                    code=ERR_BAD_REQUEST,
                    message=f"malformed request: {exc}",
                )
                writer.write(resp.to_json_line())
                await writer.drain()
                continue
            try:
                response = await _handler.handle_request(request, session=session)
            except Exception as exc:
                # Last-resort catch — the handler itself catches every
                # known failure mode; anything reaching here is a
                # programming bug.  Don't leak the exception type to
                # the client beyond its class name.
                log.exception("signing service: handler crash")
                response = SignResponse.error_reply(
                    request_id=request.id,
                    code=ERR_INTERNAL_ERROR,
                    message=f"handler crashed: {type(exc).__name__}",
                )
            writer.write(response.to_json_line())
            await writer.drain()
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass


async def serve(socket_path: Optional[str] = None) -> asyncio.AbstractServer:
    """Start the Unix-socket server and return the running server
    object.

    Tests use this entry point to spin the server up in-process; the
    production :func:`run` wrapper handles signal trapping + the
    aiohttp session lifecycle on top.
    """
    path = socket_path or _socket_path()
    # If a stale socket file exists (previous run crashed), remove it
    # so bind doesn't fail.  This is safe — we only run one signing
    # service per VPS, and an active service holds the file open via
    # bind so this delete fails fast.
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass
    # Ensure parent dir exists (production setup script creates /var/run/lumin
    # but dev/test paths may not).
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=8.0)
    )

    async def connection_handler(reader, writer):
        await _handle_connection(reader, writer, session=session)

    server = await asyncio.start_unix_server(connection_handler, path=path)
    # 0660 = rw for owner + group, no world access.  Engine user must
    # be in the socket's group to connect.
    try:
        os.chmod(path, 0o660)
    except OSError as exc:
        log.warning("could not chmod socket {}: {}", path, exc)
    log.info("signing service listening on {}", path)
    # Stash session on the server so callers can close it on shutdown.
    setattr(server, "_lumin_session", session)
    return server


async def run() -> None:
    """Production entry point.  Handles signal trapping + shutdown.

    Initialises KMS + Firestore at boot (so a misconfigured operator
    setup fails fast with a clear error rather than at first signing
    attempt).  Listens until SIGTERM / SIGINT, then cleanly closes
    the socket + aiohttp session.
    """
    from src.security import firestore_keystore, kms_client

    # Init from env — same env vars as the engine bootstrap; in a
    # systemd unit they live in /etc/lumin/signing-service.env.
    project_id = os.environ.get("GCP_KMS_PROJECT_ID", "")
    location = os.environ.get("GCP_KMS_LOCATION", "")
    keyring = os.environ.get("GCP_KMS_KEYRING", "")
    key_name = os.environ.get("GCP_KMS_KEY_NAME", "")
    sa_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH", "") or None
    if not (project_id and location and keyring and key_name):
        raise RuntimeError(
            "signing service: missing GCP_KMS_* env vars — refuse to start "
            "without KMS configuration (B18 requires KMS-backed envelope crypto)"
        )
    kms_client.init_kms_client(
        project_id=project_id,
        location=location,
        keyring=keyring,
        key_name=key_name,
        service_account_path=sa_path,
    )
    firestore_keystore.init_keystore(service_account_path=sa_path)

    server = await serve()
    session = getattr(server, "_lumin_session")

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _request_stop() -> None:
        log.info("signing service: shutdown signal received")
        stop_event.set()

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _request_stop)
        except NotImplementedError:
            # Windows / restricted env — fall through; service will
            # only stop via process kill.  Production is linux.
            pass

    try:
        await stop_event.wait()
    finally:
        server.close()
        await server.wait_closed()
        await session.close()
        log.info("signing service stopped")
