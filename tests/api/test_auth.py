"""Smoke tests for the JWT auth module + auth endpoints."""
from __future__ import annotations

import time
from datetime import timedelta

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from src.api.auth import (  # noqa: E402
    ALL_ACCESS_TIER,
    AuthError,
    decode_token,
    mint_token,
    refresh_token,
)
from src.api.server import build_app  # noqa: E402

# Re-use the stub engine from the existing smoke tests
from tests.api.test_api_smoke import _StubEngine  # noqa: E402


_SECRET = "x" * 64


# ---------------------------------------------------------------------------
# Pure auth module
# ---------------------------------------------------------------------------


def test_mint_returns_decodable_token() -> None:
    t = mint_token(secret=_SECRET)
    c = decode_token(t, secret=_SECRET)
    assert c.tier == ALL_ACCESS_TIER
    assert c.sub.startswith("device-")
    assert c.is_paid is True


def test_mint_with_custom_sub_and_tier() -> None:
    t = mint_token(secret=_SECRET, sub="user-42", tier="paid")
    c = decode_token(t, secret=_SECRET)
    assert c.sub == "user-42"
    assert c.tier == "paid"


def test_decode_rejects_wrong_secret() -> None:
    t = mint_token(secret=_SECRET)
    with pytest.raises(AuthError):
        decode_token(t, secret="other" * 12)


def test_decode_rejects_garbage() -> None:
    with pytest.raises(AuthError):
        decode_token("not.a.jwt", secret=_SECRET)


def test_decode_rejects_expired_token() -> None:
    t = mint_token(secret=_SECRET, ttl=timedelta(seconds=-1))
    with pytest.raises(AuthError, match="expired"):
        decode_token(t, secret=_SECRET)


def test_refresh_preserves_sub_and_tier() -> None:
    t1 = mint_token(secret=_SECRET, sub="device-abc", tier="paid")
    time.sleep(1)  # ensure exp moves forward
    t2 = refresh_token(t1, secret=_SECRET)
    c1 = decode_token(t1, secret=_SECRET)
    c2 = decode_token(t2, secret=_SECRET)
    assert c2.sub == c1.sub
    assert c2.tier == c1.tier
    assert c2.exp >= c1.exp


def test_refresh_rejects_expired_token() -> None:
    t = mint_token(secret=_SECRET, ttl=timedelta(seconds=-1))
    with pytest.raises(AuthError):
        refresh_token(t, secret=_SECRET)


# ---------------------------------------------------------------------------
# /api/auth/* endpoints
# ---------------------------------------------------------------------------


@pytest.fixture
def client() -> TestClient:
    return TestClient(build_app(_StubEngine(), jwt_secret=_SECRET, allow_static=False))


def test_anonymous_endpoint_mints_token(client: TestClient) -> None:
    r = client.post("/api/auth/anonymous")
    assert r.status_code == 200
    body = r.json()
    assert body["tier"] == ALL_ACCESS_TIER
    assert body["sub"].startswith("device-")
    assert body["exp_seconds"] > 0
    # Token validates against the same secret
    decode_token(body["token"], secret=_SECRET)


def test_refresh_endpoint_issues_new_token(client: TestClient) -> None:
    minted = client.post("/api/auth/anonymous").json()["token"]
    time.sleep(1)  # so refresh's iat/exp differ from the original
    r = client.post("/api/auth/refresh", json={"token": minted})
    assert r.status_code == 200
    new = r.json()["token"]
    assert new != minted  # new exp → different signature
    decode_token(new, secret=_SECRET)


def test_refresh_endpoint_rejects_invalid_token(client: TestClient) -> None:
    r = client.post("/api/auth/refresh", json={"token": "not.a.jwt"})
    assert r.status_code == 401


def test_protected_endpoint_requires_valid_jwt(client: TestClient) -> None:
    r = client.get("/api/pulse")
    assert r.status_code == 401

    r = client.get("/api/pulse", headers={"Authorization": "Bearer not.a.jwt"})
    assert r.status_code == 401


def test_protected_endpoint_accepts_minted_jwt(client: TestClient) -> None:
    token = client.post("/api/auth/anonymous").json()["token"]
    r = client.get("/api/pulse", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Static admin token escape hatch
# ---------------------------------------------------------------------------


def test_static_token_accepted_when_allow_flag_true() -> None:
    app = build_app(
        _StubEngine(),
        jwt_secret=_SECRET,
        static_token="admin-token",
        allow_static=True,
    )
    c = TestClient(app)
    r = c.get("/api/pulse", headers={"Authorization": "Bearer admin-token"})
    assert r.status_code == 200


def test_static_token_rejected_when_allow_flag_false() -> None:
    app = build_app(
        _StubEngine(),
        jwt_secret=_SECRET,
        static_token="admin-token",
        allow_static=False,
    )
    c = TestClient(app)
    r = c.get("/api/pulse", headers={"Authorization": "Bearer admin-token"})
    assert r.status_code == 401


def test_health_does_not_require_auth() -> None:
    app = build_app(_StubEngine(), jwt_secret=_SECRET, allow_static=False)
    c = TestClient(app)
    assert c.get("/api/health").status_code == 200


def test_anonymous_endpoint_503_when_secret_missing() -> None:
    app = build_app(_StubEngine(), jwt_secret="", allow_static=False)
    c = TestClient(app)
    r = c.post("/api/auth/anonymous")
    assert r.status_code == 503
