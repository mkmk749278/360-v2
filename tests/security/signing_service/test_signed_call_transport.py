"""Transport-layer tests for the signing service's outbound Binance call.

``test_handler.py`` covers ``handle_request``'s dispatch, unwrap and error
taxonomy by mocking ``_signed_call`` — correct for that file's purpose, and
the reason ``_signed_call`` itself carried no coverage.  It is the single
most secret-adjacent function in the codebase: it receives the decrypted
plaintext API secret, computes the HMAC, and builds a URL whose query string
contains the signature.  "Never log a Binance API secret at any level" is a
hard limit, and until now nothing enforced it here.

These tests drive the real function against a real local HTTP server, so the
request under assertion is the one that would actually go to Binance.

What this pins:

* **The verb→HTTP-method map.**  A POST silently sent as a GET would place
  no order while reporting success upstream.  Each verb is checked against
  the method the server actually received.
* **Signature validity**, recomputed server-side from the query as received.
* **The secret never reaches a log sink or the wire response** — including
  on the unreachable path, and including the signature.
* **``_base_url`` rejects an unknown label** rather than defaulting to a
  live exchange host.
"""
from __future__ import annotations

import hashlib
import hmac
import urllib.parse

import aiohttp
import pytest
from aiohttp import web

from src.security.signing_service import handler


_SECRET = "signing-secret-never-log-4c7e1d"
_API_KEY = "signing-api-key-zyxwvu987"


class _FakeBinance:
    """Real HTTP server that verifies the HMAC it receives."""

    def __init__(self, secret: str) -> None:
        self.secret = secret
        self.requests: list[dict] = []
        self.status = 200
        self.body: object = {}
        self._runner: web.AppRunner | None = None
        self.base_url = ""

    async def _handle(self, request: web.Request) -> web.Response:
        query = request.rel_url.query_string
        payload, _, sig = query.rpartition("&signature=")
        expected = hmac.new(
            self.secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        self.requests.append(
            {
                "path": request.path,
                "method": request.method,
                "api_key_header": request.headers.get("X-MBX-APIKEY"),
                "params": dict(urllib.parse.parse_qsl(payload)),
                "signature": sig,
                "signature_valid": hmac.compare_digest(sig, expected),
            }
        )
        return web.json_response(self.body, status=self.status)

    async def start(self) -> None:
        app = web.Application()
        app.router.add_route("*", "/{tail:.*}", self._handle)
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, "127.0.0.1", 0)
        await site.start()
        port = site._server.sockets[0].getsockname()[1]  # type: ignore[union-attr]
        self.base_url = f"http://127.0.0.1:{port}"

    async def stop(self) -> None:
        if self._runner is not None:
            await self._runner.cleanup()
            self._runner = None


@pytest.fixture
async def binance():
    server = _FakeBinance(secret=_SECRET)
    await server.start()
    try:
        yield server
    finally:
        await server.stop()


async def _call(server: _FakeBinance, verb: str = "binance_signed_get", **kw):
    return await handler._signed_call(
        verb=verb,
        api_key=_API_KEY,
        api_secret=_SECRET,
        base_url=server.base_url,
        path=kw.pop("path", "/fapi/v1/order"),
        params=kw.pop("params", {"symbol": "BTCUSDT"}),
        recv_window_ms=kw.pop("recv_window_ms", 5000),
        session=kw.pop("session", None),
    )


# ---------------------------------------------------------------------------
# Verb → HTTP method
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "verb,method",
    [
        ("binance_signed_get", "GET"),
        ("binance_signed_post", "POST"),
        ("binance_signed_delete", "DELETE"),
    ],
)
async def test_verb_maps_to_the_http_method_binance_receives(
    binance, verb, method
) -> None:
    """A POST sent as a GET places no order but looks like success."""
    binance.body = {"orderId": 1}
    status, body = await _call(binance, verb=verb)

    assert status == 200
    assert body == {"orderId": 1}
    assert binance.requests[0]["method"] == method


async def test_unsupported_verb_raises_before_any_network_call(binance) -> None:
    with pytest.raises(ValueError, match="unsupported verb"):
        await _call(binance, verb="binance_signed_patch")
    assert binance.requests == []


# ---------------------------------------------------------------------------
# Wire format
# ---------------------------------------------------------------------------


async def test_signature_is_valid_over_the_query_as_sent(binance) -> None:
    """Recomputed by the server — a shared expression would hide a bug."""
    binance.body = {}
    await _call(binance, params={"symbol": "ETHUSDT", "side": "BUY"})

    req = binance.requests[0]
    assert req["signature_valid"], "Binance would reject this signature"
    assert req["api_key_header"] == _API_KEY
    assert req["params"]["symbol"] == "ETHUSDT"
    assert req["params"]["side"] == "BUY"


async def test_recv_window_is_forwarded_not_defaulted(binance) -> None:
    """The caller's recvWindow must reach Binance — it bounds replay risk."""
    binance.body = {}
    await _call(binance, recv_window_ms=3000)
    assert int(binance.requests[0]["params"]["recvWindow"]) == 3000


async def test_non_2xx_is_returned_not_raised(binance) -> None:
    """The handler maps status→typed code; the transport must not raise."""
    binance.status = 400
    binance.body = {"code": -2019, "msg": "Margin is insufficient."}

    status, body = await _call(binance)
    assert status == 400
    assert body["code"] == -2019


async def test_network_failure_raises_the_unreachable_sentinel(binance) -> None:
    await binance.stop()
    with pytest.raises(handler._BinanceUnreachable):
        await _call(binance)


# ---------------------------------------------------------------------------
# Hard limit: the secret does not escape
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status", [200, 400, 401, 500])
async def test_secret_and_signature_never_logged(binance, status) -> None:
    from loguru import logger

    captured: list[str] = []
    sink = logger.add(lambda m: captured.append(str(m)), level="TRACE")
    try:
        binance.status = status
        binance.body = {"code": -1, "msg": "nope"}
        await _call(binance)
    finally:
        logger.remove(sink)

    blob = "\n".join(captured)
    assert _SECRET not in blob
    assert binance.requests[0]["signature"] not in blob


async def test_secret_not_logged_on_the_unreachable_path(binance) -> None:
    """The failure path is where a debugging patch would log the URL."""
    from loguru import logger

    await binance.stop()
    captured: list[str] = []
    sink = logger.add(lambda m: captured.append(str(m)), level="TRACE")
    try:
        with pytest.raises(handler._BinanceUnreachable):
            await _call(binance)
    finally:
        logger.remove(sink)

    assert _SECRET not in "\n".join(captured)


async def test_unreachable_message_carries_path_but_not_the_signed_url(
    binance,
) -> None:
    """The exception text crosses the wire — it must not carry the query."""
    await binance.stop()
    with pytest.raises(handler._BinanceUnreachable) as exc:
        await _call(binance, path="/fapi/v1/order")

    text = str(exc.value)
    assert "/fapi/v1/order" in text          # diagnosable
    assert "signature=" not in text          # but not the signed URL
    assert _SECRET not in text


# ---------------------------------------------------------------------------
# Session ownership
# ---------------------------------------------------------------------------


async def test_injected_session_is_reused_and_not_closed(binance) -> None:
    """Production passes one process-lifetime session; closing it kills the
    signing service's ability to sign anything further."""
    binance.body = {}
    async with aiohttp.ClientSession() as session:
        await _call(binance, session=session)
        assert not session.closed
        await _call(binance, session=session)
        assert not session.closed
    assert len(binance.requests) == 2


# ---------------------------------------------------------------------------
# _base_url
# ---------------------------------------------------------------------------


def test_base_url_resolves_known_labels() -> None:
    assert handler._base_url("spot") == handler._SPOT_BASE
    assert handler._base_url("futures") == handler._FUTURES_BASE


def test_base_url_rejects_unknown_label() -> None:
    """Must raise, never fall through to a default live exchange host."""
    with pytest.raises(ValueError, match="unknown base"):
        handler._base_url("testnet")
