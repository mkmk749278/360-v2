"""Every engine API route is authenticated, derived from the app itself.

Auth is attached per route (``dependencies=[Depends(owner_required)]``,
a ``user_claims`` parameter …), not by a router-wide gate. So a new route
that forgets its dependency is PUBLIC, silently: nothing fails, the route
answers anyone, and the only record is the diff. Measured 2026-09-26: ~95
routes, every one of them refusing an anonymous caller — held by habit, not
by a test (test-suite audit).

This file turns that habit into a guard with three parts, all read off the
REAL ``build_app`` rather than a list of routes (a hand-kept route list is
silent by construction on the next route — the ``is_tradfi_perp`` rule):

* **anonymous refusal** — every route not in ``ANONYMOUS_OK`` answers an
  unauthenticated request with 401/403. ``ANONYMOUS_OK`` carries a written
  reason per entry, and a stale entry fails.
* **owner routes refuse a user** — every route whose dependency tree
  requires ``OWNER_TIER`` answers a valid NON-owner token with 403.
* **what must be owner-only, is** — a route under ``/admin/`` or
  ``/internal/diag``, or one of the engine-wide control writes, must carry
  the owner dependency. Without this the second check is circular: a route
  that LOST its owner dependency would simply drop out of the derived set.
"""
from __future__ import annotations

import inspect
import re

import pytest

pytest.importorskip("fastapi")
from fastapi.routing import APIRoute  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.api.auth import OWNER_TIER, mint_token  # noqa: E402
from src.api.server import build_app  # noqa: E402
from src.api.users import UserStore  # noqa: E402

from tests.api.test_api_smoke import _StubEngine  # noqa: E402

_SECRET = "route-auth-guard-secret-" + "x" * 24

#: (METHOD, path template) → why an anonymous caller may reach it.
ANONYMOUS_OK: dict[tuple[str, str], str] = {
    ("GET", "/api/health"): "liveness probe for Cloudflare, the watchdog and deploy",
    ("GET", "/api/region"): "the geo verdict is needed before any sign-in exists",
    ("GET", "/api/billing/web/config"): "plan prices render on the paywall before sign-in",
    ("GET", "/api/track-record"): "the recorded track record is public (guests read closed signals)",
    ("GET", "/api/track-record/signals"): "the recorded track record is public (guests read closed signals)",
    # Self-authenticating: the credential is not a bearer token.
    ("POST", "/api/auth/anonymous"): "mints a guest identity; the Firebase token is in the body",
    ("POST", "/api/auth/refresh"): "the token being refreshed is in the body",
    ("POST", "/api/auth/request-otp"): "sign-in: no identity exists yet",
    ("POST", "/api/auth/verify-otp"): "sign-in: the OTP is the credential",
    ("POST", "/api/auth/telegram-otp/issue"): "sign-in: no identity exists yet",
    ("POST", "/api/auth/telegram-otp/verify"): "sign-in: the OTP is the credential",
    ("POST", "/api/billing/play/rtdn"): "Google Pub/Sub push; OIDC-verified in the handler",
    ("POST", "/api/billing/play/rtdn/{secret}"): "Pub/Sub push; path secret + OIDC in the handler",
    ("POST", "/api/billing/web/crypto/webhook"): "NOWPayments IPN; HMAC-SHA512 verified in the handler",
    ("POST", "/internal/billing/grant"): "billing webhook; signature verified in the handler",
}

#: Engine-wide control writes. Each changes what EVERY user's money path does,
#: so each must be owner-only whatever its path looks like.
ENGINE_WIDE_WRITES: frozenset[tuple[str, str]] = frozenset({
    ("POST", "/api/kill-switch"),
    ("POST", "/api/auto-mode"),
    ("POST", "/api/auto-trade-global"),
    ("POST", "/api/tunables"),
    ("POST", "/api/signal-expiry"),
    ("POST", "/api/billing/play/enabled"),
    ("PUT", "/api/settings/auto-trade"),
    ("PUT", "/api/settings/pretp"),
    ("POST", "/api/auto-mode/paper/close-all"),
    ("POST", "/api/auto-mode/paper/reset"),
})


def _must_be_owner(method: str, path: str) -> bool:
    if (method, path) in ANONYMOUS_OK:
        return False
    return (
        "/admin/" in path
        or path.startswith("/internal/diag")
        or (method, path) in ENGINE_WIDE_WRITES
    )


@pytest.fixture(scope="module")
def app(tmp_path_factory):
    store = UserStore(str(tmp_path_factory.mktemp("route-auth") / "users.db"))
    return build_app(_StubEngine(), jwt_secret=_SECRET, allow_static=False, user_store=store)


def _routes(app) -> list[tuple[str, str, APIRoute]]:
    out = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        for method in sorted(route.methods - {"HEAD", "OPTIONS"}):
            out.append((method, route.path, route))
    return out


def _required_tiers(route: APIRoute) -> set:
    tiers: set = set()
    stack = list(route.dependant.dependencies)
    while stack:
        dep = stack.pop()
        stack.extend(dep.dependencies)
        try:
            nonlocals = inspect.getclosurevars(dep.call).nonlocals
        except TypeError:
            continue
        if "required_tier" in nonlocals:
            tiers.add(nonlocals["required_tier"])
    return tiers


def _is_owner_only(route: APIRoute) -> bool:
    return OWNER_TIER in _required_tiers(route)


def _concrete(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "x", path)


def _call(client: TestClient, method: str, path: str, headers=None):
    body = {} if method in ("POST", "PUT", "PATCH") else None
    return client.request(method, _concrete(path), json=body, headers=headers or {})


def test_the_app_exposes_enough_routes_to_mean_something(app) -> None:
    # A build that silently registered nothing would make every check below
    # vacuous — the empty-population grade this repo has paid for before.
    assert len(_routes(app)) > 80


def test_every_route_refuses_an_anonymous_caller(app) -> None:
    client = TestClient(app, raise_server_exceptions=False)
    public = []
    for method, path, _route in _routes(app):
        if (method, path) in ANONYMOUS_OK:
            continue
        status = _call(client, method, path).status_code
        if status not in (401, 403):
            public.append(f"{method} {path} -> {status}")
    assert not public, (
        "route(s) answer an unauthenticated caller — add the auth dependency, "
        "or, if it is deliberately public, add it to ANONYMOUS_OK with a reason:\n  "
        + "\n  ".join(public)
    )


def test_anonymous_allowlist_has_no_stale_or_unreasoned_entries(app) -> None:
    registered = {(m, p) for m, p, _ in _routes(app)}
    stale = sorted(k for k in ANONYMOUS_OK if k not in registered)
    assert not stale, f"ANONYMOUS_OK names routes that no longer exist: {stale}"
    assert all(reason.strip() for reason in ANONYMOUS_OK.values())


def test_public_reads_do_answer_anonymously(app) -> None:
    """The allowlist is a claim too: a public route that 401s strands the
    signed-out screens (paywall prices, the track record, the geo gate)."""
    client = TestClient(app, raise_server_exceptions=False)
    for (method, path), _reason in ANONYMOUS_OK.items():
        if method == "GET":
            assert _call(client, method, path).status_code == 200, path


def test_every_owner_route_refuses_a_user_tier_token(app) -> None:
    client = TestClient(app, raise_server_exceptions=False)
    token = mint_token(secret=_SECRET)  # default tier — NOT the owner
    owner_routes = [(m, p) for m, p, r in _routes(app) if _is_owner_only(r)]
    assert len(owner_routes) >= 25, "owner-only routes vanished from the dependency tree"
    leaked = []
    for method, path in owner_routes:
        status = _call(client, method, path, {"Authorization": f"Bearer {token}"}).status_code
        if status != 403:
            leaked.append(f"{method} {path} -> {status}")
    assert not leaked, "owner-only route(s) did not refuse a user token:\n  " + "\n  ".join(leaked)


def test_an_owner_token_passes_the_gate(app) -> None:
    """Control for the check above: an owner token must NOT be refused, or
    '403 for a user' would be satisfied by a route that refuses everyone."""
    client = TestClient(app, raise_server_exceptions=False)
    token = mint_token(secret=_SECRET, tier=OWNER_TIER)
    r = client.get("/internal/diag/tasks", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code not in (401, 403)


def test_control_and_admin_routes_are_owner_only(app) -> None:
    missing = sorted(
        f"{m} {p}" for m, p, r in _routes(app)
        if _must_be_owner(m, p) and not _is_owner_only(r)
    )
    assert not missing, (
        "route(s) that change engine-wide state or expose internals do not "
        f"require OWNER_TIER: {missing}"
    )


def test_every_engine_wide_write_is_still_registered(app) -> None:
    registered = {(m, p) for m, p, _ in _routes(app)}
    gone = sorted(f"{m} {p}" for m, p in ENGINE_WIDE_WRITES if (m, p) not in registered)
    assert not gone, f"ENGINE_WIDE_WRITES names routes that no longer exist: {gone}"



def test_a_non_ascii_bearer_is_refused_not_crashed_on(app) -> None:
    """Regression (2026-09-26 audit): ``Bearer a.b.é`` answered 500 on every
    authenticated route. A credential that cannot be valid is a 401."""
    client = TestClient(app, raise_server_exceptions=False)
    headers = {"Authorization": "Bearer a.b.é".encode("latin-1")}
    crashed = []
    for method, path, _route in _routes(app):
        if (method, path) in ANONYMOUS_OK:
            continue
        status = client.request(method, _concrete(path),
                                json={} if method in ("POST", "PUT", "PATCH") else None,
                                headers=headers).status_code
        if status not in (401, 403):
            crashed.append(f"{method} {path} -> {status}")
    assert not crashed, "\n  ".join(["non-ASCII bearer not refused:"] + crashed)
