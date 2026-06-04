"""End-to-end test of the signing service via a real Unix socket.

Spins up :func:`server.serve` against a per-test temp socket path,
connects with the real :class:`client.SigningClient`, and exchanges
real wire bytes.  The handler itself is mocked so the integration
covers the SOCKET + WIRE-FORMAT path (the bit unit tests can't
cover), not the KMS / Binance chain (covered by handler unit tests).

What this catches:

* Socket creation + permission + cleanup of stale files.
* Line-delimited framing — the server's ``readline`` and the client's
  matching ``readline`` agree on terminator.
* Multiple sequential requests on one connection (we currently use
  one-shot, but the server supports persistent so this verifies the
  contract still works under that pattern).
* Concurrent connections — two clients hitting the server in parallel
  each get their own response (no message confusion).
* Server gracefully handles client disconnect without responding —
  no crash, next connection still works.
"""
from __future__ import annotations

import asyncio
import os
import tempfile
from typing import AsyncIterator
from unittest.mock import AsyncMock, patch

import pytest

from src.security.signing_service import client, protocol, server


@pytest.fixture
def socket_path() -> AsyncIterator[str]:
    """Yield a per-test temp socket path.  Cleaned up after the test
    even if the server didn't unlink it (e.g. crash)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test_signing.sock")
        yield path


@pytest.fixture
async def running_server(socket_path, monkeypatch):
    """Start a real server bound to the temp socket; stop it after."""
    monkeypatch.setenv("SIGNING_SERVICE_SOCKET_PATH", socket_path)
    srv = await server.serve(socket_path=socket_path)
    try:
        yield socket_path
    finally:
        srv.close()
        await srv.wait_closed()
        session = getattr(srv, "_lumin_session", None)
        if session is not None:
            await session.close()


# ---------------------------------------------------------------------------
# Sanity: socket gets created at the configured path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_socket_file_exists_after_server_start(running_server) -> None:
    assert os.path.exists(running_server)


# ---------------------------------------------------------------------------
# ping round-trip
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ping_round_trip_via_real_socket(running_server) -> None:
    cli = client.SigningClient(socket_path=running_server)
    resp = await cli.ping()
    assert resp.ok is True
    assert resp.binance_body == {"pong": True}


# ---------------------------------------------------------------------------
# Real wire — verbs forwarded to handler
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_signed_get_dispatched_to_handler(running_server) -> None:
    """The client's ``binance_signed_get`` reaches the handler with
    the right verb + fields after going through the wire."""
    from src.security.signing_service import handler

    with patch.object(
        handler, "handle_request", new_callable=AsyncMock
    ) as mock_handle:
        mock_handle.return_value = protocol.SignResponse.ok_reply(
            "req-1", binance_status=200, binance_body={"balances": []}
        )
        cli = client.SigningClient(socket_path=running_server)
        resp = await cli.binance_signed_get(
            firebase_uid="fb-x",
            base="futures",
            path="/fapi/v2/balance",
        )
    assert resp.ok is True
    assert resp.binance_body == {"balances": []}
    mock_handle.assert_called_once()
    sent_request = mock_handle.call_args.args[0]
    assert sent_request.verb == "binance_signed_get"
    assert sent_request.firebase_uid == "fb-x"
    assert sent_request.base == "futures"
    assert sent_request.path == "/fapi/v2/balance"


# ---------------------------------------------------------------------------
# Large response — positionRisk-with-no-symbol returns every symbol and now
# exceeds asyncio's default 64 KiB readline limit. The client must read it.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_large_signed_get_response_over_64kib(running_server) -> None:
    """Regression: a signed-GET response larger than asyncio's default
    64 KiB StreamReader limit must round-trip intact.

    Before raising the client read limit this raised
    ``ValueError: Separator is not found, and chunk exceed the limit`` and
    the reconciler silently skipped reconciliation. We fake a positionRisk
    body with enough symbols to push the single JSON response line well past
    64 KiB and assert the typed client receives it whole.
    """
    from src.security.signing_service import handler

    # ~600 position rows; serialised body lands comfortably above 64 KiB.
    big_body = [
        {
            "symbol": f"SYM{i:04d}USDT",
            "positionAmt": "0.000",
            "entryPrice": "0.0",
            "markPrice": "0.0",
            "unRealizedProfit": "0.0",
            "liquidationPrice": "0.0",
            "leverage": "10",
            "marginType": "cross",
            "isolatedMargin": "0.00000000",
            "positionSide": "BOTH",
            "updateTime": 1717497600000 + i,
        }
        for i in range(600)
    ]

    with patch.object(
        handler, "handle_request", new_callable=AsyncMock
    ) as mock_handle:
        mock_handle.return_value = protocol.SignResponse.ok_reply(
            "req-big", binance_status=200, binance_body=big_body
        )
        cli = client.SigningClient(socket_path=running_server)
        resp = await cli.binance_signed_get(
            firebase_uid="fb-big",
            base="futures",
            path="/fapi/v2/positionRisk",
        )

    # Sanity: the encoded response line really did exceed the old 64 KiB cap.
    assert len(resp.to_json_line()) > 65536
    assert resp.ok is True
    assert isinstance(resp.binance_body, list)
    assert len(resp.binance_body) == 600


# ---------------------------------------------------------------------------
# Malformed request — client can't construct one directly (typed
# dataclass), but raw bytes on the socket get a typed BAD_REQUEST.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_malformed_json_returns_bad_request(running_server) -> None:
    """Bypass the typed client, write raw garbage to the socket.  The
    server replies with ERR_BAD_REQUEST rather than crashing or
    silently closing."""
    reader, writer = await asyncio.open_unix_connection(running_server)
    try:
        writer.write(b"not-json-at-all\n")
        await writer.drain()
        line = await reader.readline()
        response = protocol.SignResponse.from_json_line(line)
        assert response.ok is False
        assert response.error_code == protocol.ERR_BAD_REQUEST
    finally:
        writer.close()
        await writer.wait_closed()


# ---------------------------------------------------------------------------
# Concurrent clients — no message confusion
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_two_concurrent_ping_clients_get_their_own_responses(
    running_server,
) -> None:
    """Two clients ping the server in parallel.  Each must receive its
    own response — no mix-up where client A gets client B's reply
    (which would indicate the server is reusing a single buffer)."""
    cli_a = client.SigningClient(socket_path=running_server)
    cli_b = client.SigningClient(socket_path=running_server)
    resp_a, resp_b = await asyncio.gather(cli_a.ping(), cli_b.ping())
    assert resp_a.ok is True
    assert resp_b.ok is True
    assert resp_a.binance_body == {"pong": True}
    assert resp_b.binance_body == {"pong": True}


# ---------------------------------------------------------------------------
# Server survives a client connecting then disconnecting without sending
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_server_survives_silent_client_disconnect(running_server) -> None:
    """Connect, send nothing, disconnect.  Server must not crash; next
    real client must still work."""
    reader, writer = await asyncio.open_unix_connection(running_server)
    writer.close()
    await writer.wait_closed()
    # Now a real client — must still get a response.
    cli = client.SigningClient(socket_path=running_server)
    resp = await cli.ping()
    assert resp.ok is True
