"""Every response the web app can receive carries CORS headers.

Owner, 2026-09-27: choosing CoinDCX on app.luminapp.org failed with "no reply
arrived in time" and nothing anywhere said why.  A browser hides any response
without ``Access-Control-Allow-Origin`` and reports it as a network failure,
and two kinds of response left without one:

* an unhandled exception — Starlette's outermost error handler answered it,
  outside the CORS layer;
* a rate-limit 429 — the limiter was added after CORS, so it sat outside it.

So the web app could never show what actually went wrong.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.server import build_app
from tests.api.test_api_smoke import _StubEngine

_ORIGIN = "https://app.luminapp.org"


def _app():
    app = build_app(_StubEngine(), static_token="tok", allow_static=True)

    @app.get("/api/__boom")
    async def _boom() -> dict:
        raise RuntimeError("secret request detail")

    return app


def test_an_unhandled_error_is_a_named_500_the_browser_can_read() -> None:
    client = TestClient(_app(), raise_server_exceptions=False)
    r = client.get("/api/__boom", headers={"Origin": _ORIGIN})
    assert r.status_code == 500
    assert r.headers.get("access-control-allow-origin") in ("*", _ORIGIN)
    body = r.json()
    assert "RuntimeError" in body["detail"] and "ref " in body["detail"]
    # The class names the cause; the message never leaves the server.
    assert "secret request detail" not in r.text
    assert r.headers["X-Error-Class"] == "RuntimeError"


def test_a_rate_limit_429_reaches_the_browser(monkeypatch) -> None:
    monkeypatch.setenv("API_RATE_LIMIT_PER_MIN", "2")
    client = TestClient(_app(), raise_server_exceptions=False)
    codes = []
    for _ in range(4):
        r = client.get("/api/__boom", headers={"Origin": _ORIGIN})
        codes.append(r.status_code)
        assert r.headers.get("access-control-allow-origin") in ("*", _ORIGIN), r.status_code
    assert 429 in codes


def test_cors_is_the_outermost_middleware() -> None:
    from starlette.middleware.cors import CORSMiddleware

    app = _app()
    # user_middleware[0] is the outermost layer Starlette builds.
    assert app.user_middleware[0].cls is CORSMiddleware
