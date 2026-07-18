"""Tests for src.api.push_topic_routes — the web-push topic proxy.

What we pin (the doctrine the module's header promises):

* Auth dep gates both endpoints (401 without it)
* Topic allow-list: only alerts/signals reachable; anything else 400s
  and never touches the Admin SDK
* Token hygiene: too-short / whitespace tokens 400 before the SDK call
* Firebase Admin not initialised → clean 503 (operator posture)
* subscribe/unsubscribe route to the matching Admin-SDK call with
  exactly [token] and the env-mapped FCM topic
* FCM-rejected token (failure_count>0) → 400 with the reason
* Admin-SDK throw → 502 (client retries later)
* Per-identity rate limit: cap enforced per identity, separate
  identities isolated
* Statelessness: the module holds no token registry — nothing about
  the token survives the request
"""
from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.api import push_topic_routes


VALID_TOKEN = "f" * 152  # realistic FCM registration-token length


def _build_app(*, identity: object = None, allow_auth: bool = True) -> FastAPI:
    app = FastAPI()

    def _auth_stub() -> None:
        if not allow_auth:
            raise HTTPException(status_code=401, detail="missing token")
        return None

    def _identity_stub() -> object:
        return identity

    push_topic_routes.register(app, auth=_auth_stub, identity_dep=_identity_stub)
    return app


def _firebase_user(uid: str = "fb-push") -> object:
    return SimpleNamespace(firebase_uid=uid, user_id=7)


@pytest.fixture(autouse=True)
def _clean_rate_limiter():
    push_topic_routes._reset_rate_limiter()
    yield
    push_topic_routes._reset_rate_limiter()


@pytest.fixture
def fake_fcm(monkeypatch):
    """Install a fake firebase_admin with an initialised app + messaging.

    Returns the messaging mock so tests can assert on the topic calls.
    """
    messaging = MagicMock()
    ok = SimpleNamespace(success_count=1, failure_count=0, errors=[])
    messaging.subscribe_to_topic.return_value = ok
    messaging.unsubscribe_from_topic.return_value = ok
    fake_admin = SimpleNamespace(_apps={"[DEFAULT]": object()}, messaging=messaging)
    monkeypatch.setitem(sys.modules, "firebase_admin", fake_admin)
    monkeypatch.setitem(sys.modules, "firebase_admin.messaging", messaging)
    return messaging


# ---------------------------------------------------------------------------
# Auth + validation (no Admin SDK involvement)
# ---------------------------------------------------------------------------


def test_requires_auth() -> None:
    app = _build_app(identity=None, allow_auth=False)
    r = TestClient(app).post(
        "/api/push/subscribe", json={"token": VALID_TOKEN, "topic": "alerts"}
    )
    assert r.status_code == 401


def test_unknown_topic_rejected(fake_fcm) -> None:
    app = _build_app(identity=_firebase_user())
    r = TestClient(app).post(
        "/api/push/subscribe", json={"token": VALID_TOKEN, "topic": "owner-alerts"}
    )
    assert r.status_code == 400
    assert "unknown topic" in r.json()["detail"]
    fake_fcm.subscribe_to_topic.assert_not_called()


def test_short_token_rejected_by_schema(fake_fcm) -> None:
    app = _build_app(identity=_firebase_user())
    r = TestClient(app).post(
        "/api/push/subscribe", json={"token": "short", "topic": "alerts"}
    )
    assert r.status_code == 422  # pydantic min_length
    fake_fcm.subscribe_to_topic.assert_not_called()


def test_whitespace_token_rejected(fake_fcm) -> None:
    app = _build_app(identity=_firebase_user())
    bad = "a" * 60 + " " + "b" * 60
    r = TestClient(app).post(
        "/api/push/subscribe", json={"token": bad, "topic": "alerts"}
    )
    assert r.status_code == 400
    assert "malformed" in r.json()["detail"]
    fake_fcm.subscribe_to_topic.assert_not_called()


# ---------------------------------------------------------------------------
# Firebase Admin unavailable
# ---------------------------------------------------------------------------


def test_uninitialised_firebase_503(monkeypatch) -> None:
    fake_admin = SimpleNamespace(_apps={})  # imported but not initialised
    monkeypatch.setitem(sys.modules, "firebase_admin", fake_admin)
    app = _build_app(identity=_firebase_user())
    r = TestClient(app).post(
        "/api/push/subscribe", json={"token": VALID_TOKEN, "topic": "alerts"}
    )
    assert r.status_code == 503
    assert "not" in r.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Happy paths — the Admin SDK call shape
# ---------------------------------------------------------------------------


def test_subscribe_calls_admin_sdk_with_env_topic(fake_fcm, monkeypatch) -> None:
    import config as _config

    monkeypatch.setattr(_config, "FCM_ALERTS_TOPIC", "alerts-live")
    app = _build_app(identity=_firebase_user())
    r = TestClient(app).post(
        "/api/push/subscribe", json={"token": VALID_TOKEN, "topic": "alerts"}
    )
    assert r.status_code == 200
    assert r.json() == {"ok": True, "topic": "alerts", "subscribed": True}
    fake_fcm.subscribe_to_topic.assert_called_once_with([VALID_TOKEN], "alerts-live")
    fake_fcm.unsubscribe_from_topic.assert_not_called()


def test_unsubscribe_calls_matching_sdk_op(fake_fcm) -> None:
    app = _build_app(identity=_firebase_user())
    r = TestClient(app).post(
        "/api/push/unsubscribe", json={"token": VALID_TOKEN, "topic": "signals"}
    )
    assert r.status_code == 200
    assert r.json() == {"ok": True, "topic": "signals", "subscribed": False}
    fake_fcm.unsubscribe_from_topic.assert_called_once_with([VALID_TOKEN], "signals")
    fake_fcm.subscribe_to_topic.assert_not_called()


# ---------------------------------------------------------------------------
# FCM-side failures
# ---------------------------------------------------------------------------


def test_fcm_rejected_token_maps_to_400(fake_fcm) -> None:
    fake_fcm.subscribe_to_topic.return_value = SimpleNamespace(
        success_count=0,
        failure_count=1,
        errors=[SimpleNamespace(index=0, reason="invalid-argument")],
    )
    app = _build_app(identity=_firebase_user())
    r = TestClient(app).post(
        "/api/push/subscribe", json={"token": VALID_TOKEN, "topic": "alerts"}
    )
    assert r.status_code == 400
    assert "invalid-argument" in r.json()["detail"]


def test_sdk_throw_maps_to_502(fake_fcm) -> None:
    fake_fcm.subscribe_to_topic.side_effect = RuntimeError("FCM backend down")
    app = _build_app(identity=_firebase_user())
    r = TestClient(app).post(
        "/api/push/subscribe", json={"token": VALID_TOKEN, "topic": "alerts"}
    )
    assert r.status_code == 502


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------


def test_rate_limit_enforced_per_identity(fake_fcm, monkeypatch) -> None:
    import config as _config

    monkeypatch.setattr(_config, "FCM_TOPIC_PROXY_MAX_PER_MIN", 3)
    app = _build_app(identity=_firebase_user("fb-limited"))
    client = TestClient(app)
    payload = {"token": VALID_TOKEN, "topic": "alerts"}
    for _ in range(3):
        assert client.post("/api/push/subscribe", json=payload).status_code == 200
    r = client.post("/api/push/subscribe", json=payload)
    assert r.status_code == 429


def test_rate_limit_isolated_between_identities(fake_fcm, monkeypatch) -> None:
    import config as _config

    monkeypatch.setattr(_config, "FCM_TOPIC_PROXY_MAX_PER_MIN", 1)
    payload = {"token": VALID_TOKEN, "topic": "signals"}
    app_a = _build_app(identity=_firebase_user("fb-a"))
    app_b = _build_app(identity=_firebase_user("fb-b"))
    assert TestClient(app_a).post("/api/push/subscribe", json=payload).status_code == 200
    assert TestClient(app_a).post("/api/push/subscribe", json=payload).status_code == 429
    # A different identity still has budget.
    assert TestClient(app_b).post("/api/push/subscribe", json=payload).status_code == 200


# ---------------------------------------------------------------------------
# Statelessness — no token registry
# ---------------------------------------------------------------------------


def test_no_token_persisted_anywhere(fake_fcm) -> None:
    """The module's only mutable state is the rate-limiter windows —
    the registration token itself must not survive the request."""
    app = _build_app(identity=_firebase_user())
    TestClient(app).post(
        "/api/push/subscribe", json={"token": VALID_TOKEN, "topic": "alerts"}
    )
    module_state = vars(push_topic_routes)
    for name, value in module_state.items():
        if name.startswith("__"):
            continue
        assert VALID_TOKEN not in repr(value), f"token leaked into {name}"
