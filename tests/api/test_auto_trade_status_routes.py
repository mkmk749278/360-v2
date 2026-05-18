"""Tests for src.api.auto_trade_status_routes.

Same wiring pattern as test_binance_connect_routes (PR-2):
auth stub + identity stub + a FastAPI app that registers the route.
KillSwitchClient is mocked at the module boundary.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


def _build_app(*, identity: object = None, allow_auth: bool = True) -> FastAPI:
    from src.api import auto_trade_status_routes

    app = FastAPI()

    def _auth_stub() -> None:
        if not allow_auth:
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="missing token")
        return None

    def _identity_stub() -> object:
        return identity

    auto_trade_status_routes.register(
        app, auth=_auth_stub, identity_dep=_identity_stub
    )
    return app


def _firebase_user(uid: str = "fb-uid-test") -> object:
    return SimpleNamespace(firebase_uid=uid, user_id=99)


@pytest.fixture(autouse=True)
def _reset_kill_switch():
    from src.execution import kill_switch
    kill_switch.reset_for_test()
    yield
    kill_switch.reset_for_test()


# ---------------------------------------------------------------------------
# Auth + identity
# ---------------------------------------------------------------------------


def test_no_auth_returns_401() -> None:
    app = _build_app(allow_auth=False)
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    assert r.status_code == 401


def test_static_token_bypass_rejected_with_401() -> None:
    """The status endpoint requires a Firebase identity — static-
    token bypass (identity=None) should return 401 with a 'sign in'
    message rather than serving a default response."""
    app = _build_app(identity=None)
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    assert r.status_code == 401
    assert "Firebase" in r.json()["detail"]


# ---------------------------------------------------------------------------
# Kill switch not initialised (dev path) → safe default
# ---------------------------------------------------------------------------


def test_kill_switch_not_initialised_returns_safe_default() -> None:
    """When the server-side execution stack isn't wired (no GCP env
    vars), the endpoint returns a default-safe response rather than
    500 — keeps the Lumin app's banner UI functional in dev /
    pre-deploy contexts."""
    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    assert r.status_code == 200
    body = r.json()
    # Default state: globally NOT enabled, user not specifically
    # disabled.  Matches the doctrine default-deny on fresh deploy.
    assert body["auto_trade_globally_enabled"] is False
    assert body["auto_trade_user_disabled"] is False
    assert body["disabled_reason"] == ""
    assert body["disabled_at"] is None


# ---------------------------------------------------------------------------
# Kill switch initialised — reads from Firestore (mocked)
# ---------------------------------------------------------------------------


def _install_kill_switch_with_flags(
    *, enabled: bool, user_disabled: bool
) -> None:
    """Inject a KillSwitchClient that returns the given flags."""
    from src.execution import kill_switch

    fake = MagicMock()
    fake.is_globally_enabled = MagicMock(return_value=enabled)
    fake.is_user_disabled = MagicMock(return_value=user_disabled)
    kill_switch._client = fake


def test_returns_both_flags_when_initialised() -> None:
    _install_kill_switch_with_flags(enabled=True, user_disabled=False)
    app = _build_app(identity=_firebase_user(uid="fb-x"))
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    assert r.status_code == 200
    body = r.json()
    assert body["auto_trade_globally_enabled"] is True
    assert body["auto_trade_user_disabled"] is False


def test_user_disabled_state_returned() -> None:
    """User-specific disable returns True on the response."""
    _install_kill_switch_with_flags(enabled=True, user_disabled=True)
    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    body = r.json()
    assert body["auto_trade_user_disabled"] is True


def test_globally_disabled_state_returned() -> None:
    """Pre-flip global state returns enabled=False — the Lumin app
    surfaces "auto-trade globally paused" in this case."""
    _install_kill_switch_with_flags(enabled=False, user_disabled=False)
    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    body = r.json()
    assert body["auto_trade_globally_enabled"] is False


def test_firestore_failure_returns_safe_default_with_reason() -> None:
    """A Firestore read failure (transient outage) returns the
    default-safe response with a diagnostic ``disabled_reason``
    rather than 500.  The Lumin app's banner UI keeps working;
    only the precision of the state is degraded."""
    from src.execution import kill_switch

    fake = MagicMock()
    fake.is_globally_enabled = MagicMock(
        side_effect=RuntimeError("Firestore unreachable")
    )
    fake.is_user_disabled = MagicMock(return_value=False)
    kill_switch._client = fake
    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    assert r.status_code == 200
    body = r.json()
    assert body["auto_trade_globally_enabled"] is False
    assert "RuntimeError" in body["disabled_reason"]
