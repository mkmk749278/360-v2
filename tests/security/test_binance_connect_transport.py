"""Transport-layer tests for the Binance connect-time signed request.

``tests/security/test_binance_connect_validator.py`` covers the B18 rule
enforcement by mocking at the ``_signed_get`` boundary — a deliberate choice,
and the right one for that file.  The consequence is that ``_signed_get``
itself had NO automated coverage: its own docstring pointed at a manual
operator smoke-test as the verification story.  That left the Binance
error-code mapping untested, and this repo has a standing rule about exactly
this failure mode — a test that hand-writes a collaborator's return shape
asserts your assumption back at you (#798).

So these tests drive the real collaborator.  A real ``aiohttp`` server on a
real socket, a real ``aiohttp.ClientSession``, real response objects, real
JSON decoding.  Nothing about the HTTP layer is faked, which is what makes
the assertions below mean anything.

What this pins:

* **The -2014 disambiguation.**  Binance overloads -2014 for both "API-key
  format invalid" and "IP not whitelisted", and the two get told apart by
  message text.  That branch decides whether a paying user is told to
  whitelist an IP (fixable in 30 seconds) or to re-enter their key (a
  dead end if the key was fine).  Getting it backwards is a support
  nightmare that looks like a working system.
* **The signature Binance would actually receive validates.**  The test
  server recomputes the HMAC over the query it was sent and compares.  A
  mocked session can never catch a signing bug; this does.
* **The secret and the signature never reach a log sink** — the B18 hard
  limit ("never log a Binance API secret at any level"), asserted on the
  failure paths too, since those are where a naive fix would start
  dumping the URL to debug it.
* **Session ownership.**  ``_signed_get`` closes a session it created and
  must NOT close one passed in — leaking a session per connect attempt, or
  closing the caller's, are both silent production faults.
"""
from __future__ import annotations

import hashlib
import hmac
import urllib.parse

import aiohttp
import pytest
from aiohttp import web

from src.security import binance_connect_validator as validator


# ---------------------------------------------------------------------------
# A real Binance-shaped server
# ---------------------------------------------------------------------------


class _FakeBinance:
    """A real HTTP server that answers like Binance does.

    Not a mock: it parses the query string, verifies the HMAC signature the
    client sent, and records what it received so tests can assert on the
    wire format rather than on an intercepted call object.
    """

    def __init__(self, secret: str) -> None:
        self.secret = secret
        self.requests: list[dict] = []
        self.status = 200
        self.body: object = {}
        # (text, content_type) to return instead of JSON — for the edge-proxy
        # HTML case, where the point is that the body does NOT parse as JSON.
        self.raw: tuple[str, str] | None = None
        self._runner: web.AppRunner | None = None
        self.base_url = ""

    async def _handle(self, request: web.Request) -> web.Response:
        query = request.rel_url.query_string
        # Binance verifies the signature over everything before "&signature=".
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
        if self.raw is not None:
            text, content_type = self.raw
            return web.Response(
                text=text, status=self.status, content_type=content_type
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


_SECRET = "test-secret-do-not-log-me-9f3a2b"
_API_KEY = "test-api-key-abcdef123456"


@pytest.fixture
async def binance():
    server = _FakeBinance(secret=_SECRET)
    await server.start()
    try:
        yield server
    finally:
        await server.stop()


async def _call(server: _FakeBinance, path: str = "/sapi/v1/account/apiRestrictions"):
    """Drive the real ``_signed_get`` against the real server."""
    return await validator._signed_get(
        api_key=_API_KEY,
        api_secret=_SECRET,
        base_url=server.base_url,
        path=path,
    )


# ---------------------------------------------------------------------------
# Wire format — what Binance actually receives
# ---------------------------------------------------------------------------


async def test_signed_get_sends_a_signature_binance_would_accept(binance) -> None:
    """The HMAC is computed over the exact query string that is sent.

    Verified by the server recomputing it, not by re-deriving the same
    expression the implementation uses — otherwise a signing bug would be
    reproduced identically on both sides and the test would pass.
    """
    binance.body = {"ipRestrict": True}
    await _call(binance)

    assert len(binance.requests) == 1
    req = binance.requests[0]
    assert req["signature_valid"], "Binance would have rejected this signature"
    assert req["api_key_header"] == _API_KEY
    assert req["method"] == "GET"


async def test_signed_get_sends_timestamp_and_recv_window(binance) -> None:
    """Binance rejects signed calls with no timestamp / stale recvWindow."""
    binance.body = {}
    await _call(binance)

    params = binance.requests[0]["params"]
    assert "timestamp" in params
    assert int(params["timestamp"]) > 0
    assert int(params["recvWindow"]) == validator._RECV_WINDOW_MS


async def test_signed_get_returns_parsed_json_on_200(binance) -> None:
    binance.body = {"ipRestrict": True, "enableFutures": True}
    out = await _call(binance)
    assert out == {"ipRestrict": True, "enableFutures": True}


# ---------------------------------------------------------------------------
# The -2014 overload — the branch that decides what the user is told
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "msg",
    [
        "Invalid API-key, IP, or permissions for action.",
        "Request IP is not in the whitelist.",
        "This IP is not on the API key whitelist.",
    ],
)
async def test_2014_naming_an_ip_maps_to_ip_not_whitelisted(binance, msg) -> None:
    """-2014 whose message mentions IP/whitelist → the fixable error.

    Mapping this to KeyInvalidError instead would tell a user with a
    perfectly good key to re-enter it, forever.
    """
    binance.status = 401
    binance.body = {"code": -2014, "msg": msg}

    with pytest.raises(validator.IpNotWhitelistedError):
        await _call(binance)


async def test_2014_without_ip_wording_maps_to_key_invalid(binance) -> None:
    """-2014 with no IP wording is a genuine bad-key: the other branch."""
    binance.status = 401
    binance.body = {"code": -2014, "msg": "API-key format invalid."}

    with pytest.raises(validator.KeyInvalidError):
        await _call(binance)


async def test_2015_maps_to_key_invalid(binance) -> None:
    binance.status = 401
    binance.body = {"code": -2015, "msg": "Invalid API-key, IP, or permissions."}

    with pytest.raises(validator.KeyInvalidError):
        await _call(binance)


# ---------------------------------------------------------------------------
# Transient vs user-error — the 503-vs-400 decision
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("status", [500, 502, 503])
async def test_5xx_is_unreachable_not_user_error(binance, status) -> None:
    """5xx must be retryable, never surfaced as "fix your key"."""
    binance.status = status
    binance.body = {}

    with pytest.raises(validator.BinanceUnreachableError):
        await _call(binance)


async def test_network_failure_is_unreachable(binance) -> None:
    """Connection refused → BinanceUnreachableError, not a crash."""
    await binance.stop()  # port now dead

    with pytest.raises(validator.BinanceUnreachableError):
        await _call(binance)


async def test_unmapped_4xx_surfaces_the_raw_code(binance) -> None:
    """An unrecognised code stays diagnosable — the code reaches the message."""
    binance.status = 400
    binance.body = {"code": -1121, "msg": "Invalid symbol."}

    with pytest.raises(validator.BinanceConnectValidationError) as exc:
        await _call(binance)
    assert "-1121" in str(exc.value)
    # Not one of the specific subclasses — those imply a known fix-up.
    assert not isinstance(exc.value, (validator.KeyInvalidError,
                                      validator.IpNotWhitelistedError,
                                      validator.BinanceUnreachableError))


async def test_html_error_body_from_an_edge_proxy_does_not_crash(binance) -> None:
    """A real text/html 502 — unparseable as JSON — stays a typed error."""
    binance.status = 502
    binance.body = None
    binance.raw = ("<html>502 Bad Gateway</html>", "text/html")

    with pytest.raises(validator.BinanceUnreachableError):
        await _call(binance)


@pytest.mark.parametrize("body", [None, [{"asset": "USDT"}]])
async def test_non_dict_json_error_body_stays_inside_the_taxonomy(binance, body) -> None:
    """A parsed-but-not-a-dict error body must not escape as AttributeError.

    Regression for a bug this file found on first run: ``body.get("code")``
    assumed a dict, so a bare ``null`` or an array (the shape
    /fapi/v2/balance itself returns) raised AttributeError straight out of
    ``_signed_get``.  AttributeError is not a BinanceConnectValidationError,
    so the connect route's error mapping never saw it — the user got a 500
    with no instruction instead of a 503 telling them to retry.

    Verified against the pre-fix code: both parameters raised
    AttributeError before the isinstance guard was added.
    """
    binance.status = 502
    binance.body = body

    with pytest.raises(validator.BinanceUnreachableError):
        await _call(binance)


async def test_non_dict_json_on_4xx_maps_to_generic_validation_error(binance) -> None:
    """Same guard on the 4xx side: typed error, not AttributeError."""
    binance.status = 400
    binance.body = None

    with pytest.raises(validator.BinanceConnectValidationError) as exc:
        await _call(binance)
    assert not isinstance(exc.value, validator.BinanceUnreachableError)


# ---------------------------------------------------------------------------
# B18 hard limit: the secret never reaches a log sink
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status,body",
    [
        (200, {"ipRestrict": True}),
        (401, {"code": -2014, "msg": "Request IP is not in the whitelist."}),
        (401, {"code": -2015, "msg": "Invalid API-key."}),
        (500, {}),
        (400, {"code": -1121, "msg": "Invalid symbol."}),
    ],
)
async def test_secret_and_signature_never_logged(binance, status, body) -> None:
    """No log record may contain the secret or the signature — on ANY path.

    Asserted across the failure paths specifically: those are where someone
    debugging a connect problem would be tempted to log the URL, and the
    URL carries the signature.
    """
    from loguru import logger

    captured: list[str] = []
    sink = logger.add(lambda m: captured.append(str(m)), level="TRACE")
    try:
        binance.status = status
        binance.body = body
        try:
            await _call(binance)
        except validator.BinanceConnectValidationError:
            pass
    finally:
        logger.remove(sink)

    blob = "\n".join(captured)
    assert _SECRET not in blob
    if binance.requests:
        assert binance.requests[0]["signature"] not in blob


# ---------------------------------------------------------------------------
# Session ownership
# ---------------------------------------------------------------------------


async def test_injected_session_is_not_closed(binance) -> None:
    """The caller owns a session it passed in — closing it breaks reuse."""
    binance.body = {}
    async with aiohttp.ClientSession() as session:
        await validator._signed_get(
            api_key=_API_KEY,
            api_secret=_SECRET,
            base_url=binance.base_url,
            path="/sapi/v1/account/apiRestrictions",
            session=session,
        )
        assert not session.closed
        # Still usable for the second B18 call in the same connect flow.
        await validator._signed_get(
            api_key=_API_KEY,
            api_secret=_SECRET,
            base_url=binance.base_url,
            path="/fapi/v2/balance",
            session=session,
        )
        assert not session.closed
    assert len(binance.requests) == 2


async def test_injected_session_not_closed_on_error_path(binance) -> None:
    """A failed validation must not close the caller's session either."""
    binance.status = 401
    binance.body = {"code": -2015, "msg": "Invalid API-key."}

    async with aiohttp.ClientSession() as session:
        with pytest.raises(validator.KeyInvalidError):
            await validator._signed_get(
                api_key=_API_KEY,
                api_secret=_SECRET,
                base_url=binance.base_url,
                path="/sapi/v1/account/apiRestrictions",
                session=session,
            )
        assert not session.closed


# ---------------------------------------------------------------------------
# End-to-end: the public entry point over real HTTP
# ---------------------------------------------------------------------------


@pytest.fixture
def local_binance(binance, monkeypatch):
    """Point the validator's hardcoded Binance hosts at the local server.

    Without this the end-to-end tests would call the real api.binance.com.
    """
    monkeypatch.setattr(validator, "_SPOT_BASE", binance.base_url)
    monkeypatch.setattr(validator, "_FUTURES_BASE", binance.base_url)
    return binance


async def test_validate_binance_key_end_to_end_over_real_http(local_binance) -> None:
    """The full B18 sequence with nothing mocked at all.

    Both round-trips hit the socket, both signatures verify server-side.
    """
    binance = local_binance
    binance.body = {
        "ipRestrict": True,
        "enableWithdrawals": False,
        "enableFutures": True,
        "enableReading": True,
    }

    result = await validator.validate_binance_key(
        api_key=_API_KEY,
        api_secret=_SECRET,
    )

    assert result.withdraw_disabled_ok
    assert result.futures_enabled_ok
    assert result.ip_whitelist_ok
    # Step 1 then step 3 — the futures-wallet probe is not skippable.
    assert [r["path"] for r in binance.requests] == [
        "/sapi/v1/account/apiRestrictions",
        "/fapi/v2/balance",
    ]
    assert all(r["signature_valid"] for r in binance.requests)


async def test_withdraw_enabled_rejected_before_any_futures_call(local_binance) -> None:
    """The withdraw hard limit short-circuits — no second round-trip.

    B18 is auto-reject with no override; a second call would mean the
    validator kept working with a key it had already disqualified.
    """
    binance = local_binance
    binance.body = {
        "ipRestrict": True,
        "enableWithdrawals": True,
        "enableFutures": True,
    }

    with pytest.raises(validator.WithdrawEnabledError):
        await validator.validate_binance_key(
            api_key=_API_KEY,
            api_secret=_SECRET,
        )

    assert [r["path"] for r in binance.requests] == [
        "/sapi/v1/account/apiRestrictions"
    ]
