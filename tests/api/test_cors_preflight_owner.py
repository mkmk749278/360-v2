"""CORS preflight has ONE writer — the FastAPI app — and it covers every route.

2026-09-27: choosing CoinDCX in the web app came back "no reply arrived in
time", every time, even after ops opened CoinDCX to everyone.  The engine never
saw the request.  nginx (``tools/setup-vps-api.sh``) answered every ``OPTIONS``
itself with ``GET, POST, OPTIONS``, so the browser refused to send any PUT or
DELETE — platform, margin, leverage, key removal.  FastAPI already allowed
them; it was never reached.  A second hand-written method list in front of
the one that is derived from the routes is the drift this repo keeps paying
for.  Three guards:

* the app's CORS allow-list covers every method a real route serves —
  derived from ``build_app``'s own routes, so a new PATCH route fails here;
* a real preflight for each of those methods succeeds against ``build_app``;
* the nginx setup script does not answer preflight at all, and the live-box
  reconciler removes the old block (driven on the exact text the old script
  wrote) and is idempotent.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("fastapi")
from fastapi.routing import APIRoute  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.api.server import build_app  # noqa: E402
from tests.api.test_api_smoke import _StubEngine  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def app():
    return build_app(_StubEngine(), jwt_secret="cors-" + "x" * 40, allow_static=False)


def _route_methods(app) -> set[str]:
    out: set[str] = set()
    for r in app.routes:
        if isinstance(r, APIRoute):
            out |= set(r.methods) - {"HEAD", "OPTIONS"}
    return out


def test_every_route_method_passes_a_browser_preflight(app) -> None:
    methods = _route_methods(app)
    assert {"GET", "POST", "PUT", "DELETE"} <= methods  # the app really serves these
    c = TestClient(app)
    for m in sorted(methods):
        r = c.options(
            "/api/venue",
            headers={
                "Origin": "https://app.luminapp.org",
                "Access-Control-Request-Method": m,
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )
        assert r.status_code == 200, (m, r.status_code, r.text)
        allowed = {x.strip() for x in r.headers["access-control-allow-methods"].split(",")}
        assert m in allowed, (m, allowed)


def test_setup_script_does_not_answer_preflight() -> None:
    s = (REPO / "tools" / "setup-vps-api.sh").read_text()
    assert "request_method = 'OPTIONS'" not in s
    assert "Access-Control-Allow-Methods" not in s


# The block the pre-fix setup script wrote, verbatim as it lands in the file
# (the heredoc's \$ escapes resolved).  Driving the reconciler on this text is
# the point: a regex tested on a block of my own invention proves nothing.
_OLD_SITE = """server {
    listen 80;
    server_name api.luminapp.org;

    location / {
        limit_req zone=lumin_api burst=30 nodelay;
        proxy_pass http://lumin_api_upstream;
        proxy_read_timeout 30s;
        proxy_connect_timeout 5s;

        # CORS preflight for the Lumin app.  GET/POST only — same as the
        # FastAPI app's CORS allow-list.  Browsers / WebView clients send
        # OPTIONS first; we answer them at the proxy layer to keep the
        # FastAPI handler chain short.
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
            add_header 'Access-Control-Max-Age' 86400;
            add_header 'Content-Length' 0;
            return 204;
        }
    }

    location ~* \\.(php|asp|aspx|jsp)$ { return 444; }
}
"""


def test_reconciler_removes_the_block_and_nothing_else() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "nginx_cors_passthrough", REPO / "tools" / "nginx_cors_passthrough.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # certbot copies the server block for 443, so the block can appear twice.
    doubled = _OLD_SITE + _OLD_SITE.replace("listen 80;", "listen 443 ssl;")
    new, removed = mod.strip_preflight(doubled)
    assert removed == 2
    assert "OPTIONS" not in new and "Access-Control" not in new
    assert "CORS preflight for the Lumin app" not in new
    for kept in ("proxy_pass http://lumin_api_upstream;", "limit_req zone=lumin_api",
                 "listen 443 ssl;", "return 444;"):
        assert kept in new
    # braces still balance — an unbalanced file is an nginx that will not start
    assert new.count("{") == new.count("}")
    # idempotent: a second deploy changes nothing
    again, removed_again = mod.strip_preflight(new)
    assert removed_again == 0 and again == new


def test_reconciler_leaves_an_unrelated_options_block_alone() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "nginx_cors_passthrough", REPO / "tools" / "nginx_cors_passthrough.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    other = "    if ($request_method = 'OPTIONS') {\n        return 444;\n    }\n"
    new, removed = mod.strip_preflight(other)
    assert removed == 0 and new == other


def test_deploy_runs_the_reconciler() -> None:
    wf = (REPO / ".github" / "workflows" / "deploy.yml").read_text()
    assert "tools/nginx_cors_passthrough.py" in wf
