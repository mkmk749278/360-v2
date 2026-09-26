"""The RTDN webhook's own authentication, which had no test at all.

``/api/billing/play/rtdn`` answers anyone — it has to, Google's Pub/Sub push
carries no bearer token the app minted — so its safety lives INSIDE the
handler: an unguessable path secret (404 on a miss) and Google's signed OIDC
push token (401 on a miss). ``test_billing_play.py`` drives the business
logic with neither configured, so both gates, and the other-package filter
beside them, were unexercised (2026-09-26 audit).

Every refusal here also asserts that Google was never asked: a gate that
refuses AFTER re-fetching the subscription still lets a stranger spend our
Play Developer API quota, and an unreadable ordering would hide that.
"""
from __future__ import annotations

import base64
import json
import sys
import types
from datetime import datetime, timedelta, timezone

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

import httpx  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.api import server as server_mod  # noqa: E402
from src.api.billing_play import PlayBillingVerifier  # noqa: E402
from src.api.play_purchases import PlayPurchaseStore  # noqa: E402
from src.api.server import build_app  # noqa: E402
from src.api.users import UserStore  # noqa: E402

_SECRET = "rtdn-auth-secret-" + "x" * 30
_PATH_SECRET = "p4th-s3cret"
_AUDIENCE = "https://api.luminapp.org/api/billing/play/rtdn"
_PACKAGE = "org.luminapp.lumin"


class _Http:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    async def __call__(self, method, url, **kwargs):  # noqa: ANN001
        self.calls.append((method, url))
        expiry = (datetime.now(timezone.utc) + timedelta(days=31)).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
        return httpx.Response(200, json={
            "subscriptionState": "SUBSCRIPTION_STATE_ACTIVE",
            "acknowledgementState": "ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED",
            "lineItems": [{"productId": "lumin_auto_monthly", "expiryTime": expiry}],
        })


async def _token() -> str:
    return "fake-access-token"


def _envelope(payload: dict) -> dict:
    data = base64.b64encode(json.dumps(payload).encode()).decode()
    return {"message": {"data": data, "messageId": "1"}, "subscription": "projects/x/subscriptions/y"}


def _renewal(package: str = _PACKAGE) -> dict:
    return _envelope({
        "packageName": package,
        "subscriptionNotification": {
            "notificationType": 2, "purchaseToken": "tok-known",
            "subscriptionId": "lumin_auto_monthly",
        },
    })


def _build(tmp_path, *, path_secret: str = "", audience: str = ""):
    db = str(tmp_path / "lumin.sqlite")
    users = UserStore(db)
    user = users.get_or_create_by_phone("+15550001111")
    purchases = PlayPurchaseStore(db)
    purchases.upsert(
        purchase_token="tok-known", user_id=user.user_id,
        product_id="lumin_auto_monthly", state="SUBSCRIPTION_STATE_ACTIVE", expiry=None,
    )
    http = _Http()
    verifier = PlayBillingVerifier(
        package_name=_PACKAGE,
        product_tiers={"lumin_auto_monthly": "auto"},
        token_provider=_token,
        http_send=http,
    )
    app = build_app(
        object(), jwt_secret=_SECRET, allow_static=False, user_store=users,
        play_verifier=verifier, play_purchases=purchases,
        play_rtdn_path_secret=path_secret, play_rtdn_audience=audience,
    )
    return TestClient(app, raise_server_exceptions=False), http, users, user.user_id


# ---------------------------------------------------------------------------
# Path secret
# ---------------------------------------------------------------------------


def test_wrong_path_secret_is_a_404_and_google_is_never_asked(tmp_path) -> None:
    client, http, users, uid = _build(tmp_path, path_secret=_PATH_SECRET)
    r = client.post("/api/billing/play/rtdn/not-the-secret", json=_renewal())
    assert r.status_code == 404
    assert http.calls == []
    assert users.get_by_id(uid).tier == "free"


def test_the_bare_path_is_refused_once_a_secret_is_configured(tmp_path) -> None:
    """Configuring a secret must close the secret-less route too, or the
    secret protects nothing."""
    client, http, *_ = _build(tmp_path, path_secret=_PATH_SECRET)
    r = client.post("/api/billing/play/rtdn", json=_renewal())
    assert r.status_code == 404
    assert http.calls == []


def test_the_right_path_secret_is_processed(tmp_path) -> None:
    client, http, users, uid = _build(tmp_path, path_secret=_PATH_SECRET)
    r = client.post(f"/api/billing/play/rtdn/{_PATH_SECRET}", json=_renewal())
    assert r.status_code == 200, r.text
    assert r.json()["handled"] == "RENEWED"
    assert len(http.calls) == 1
    assert users.get_by_id(uid).tier == "auto"


# ---------------------------------------------------------------------------
# Pub/Sub OIDC
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("header", [None, "", "Basic Zm9vOmJhcg==", "Bearer "])
def test_missing_or_non_bearer_oidc_is_a_401(tmp_path, monkeypatch, header) -> None:
    async def _never(token, audience):  # pragma: no cover - must not be reached
        raise AssertionError("verifier called without a bearer token")

    monkeypatch.setattr(server_mod, "_verify_pubsub_oidc", _never)
    client, http, users, uid = _build(tmp_path, audience=_AUDIENCE)
    headers = {} if header is None else {"Authorization": header}
    r = client.post("/api/billing/play/rtdn", json=_renewal(), headers=headers)
    assert r.status_code == 401
    assert http.calls == []
    assert users.get_by_id(uid).tier == "free"


def test_an_invalid_oidc_token_is_a_401(tmp_path, monkeypatch) -> None:
    seen: list = []

    async def _reject(token, audience):
        seen.append((token, audience))
        return False

    monkeypatch.setattr(server_mod, "_verify_pubsub_oidc", _reject)
    client, http, *_ = _build(tmp_path, audience=_AUDIENCE)
    r = client.post(
        "/api/billing/play/rtdn", json=_renewal(),
        headers={"Authorization": "Bearer forged.jwt.token"},
    )
    assert r.status_code == 401
    assert seen == [("forged.jwt.token", _AUDIENCE)]  # checked against OUR audience
    assert http.calls == []


def test_a_valid_oidc_token_is_processed(tmp_path, monkeypatch) -> None:
    async def _accept(token, audience):
        return True

    monkeypatch.setattr(server_mod, "_verify_pubsub_oidc", _accept)
    client, http, users, uid = _build(tmp_path, audience=_AUDIENCE)
    r = client.post(
        "/api/billing/play/rtdn", json=_renewal(),
        headers={"Authorization": "Bearer good.jwt.token"},
    )
    assert r.status_code == 200, r.text
    assert users.get_by_id(uid).tier == "auto"


def test_another_apps_notification_is_ignored_without_asking_google(tmp_path) -> None:
    client, http, users, uid = _build(tmp_path)
    r = client.post("/api/billing/play/rtdn", json=_renewal(package="com.someone.else"))
    assert r.status_code == 200
    assert r.json()["handled"] == "ignored:other-package"
    assert http.calls == []
    assert users.get_by_id(uid).tier == "free"


# ---------------------------------------------------------------------------
# _verify_pubsub_oidc itself — Google's verifier stubbed, so no network
# ---------------------------------------------------------------------------


def _stub_google(monkeypatch, verify):
    id_token = types.SimpleNamespace(verify_oauth2_token=verify)
    transport = types.SimpleNamespace(requests=types.SimpleNamespace(Request=lambda: object()))
    oauth2 = types.ModuleType("google.oauth2")
    oauth2.id_token = id_token
    auth = types.ModuleType("google.auth")
    auth.transport = transport
    monkeypatch.setitem(sys.modules, "google.oauth2", oauth2)
    monkeypatch.setitem(sys.modules, "google.oauth2.id_token", id_token)
    monkeypatch.setitem(sys.modules, "google.auth.transport", transport)
    monkeypatch.setitem(sys.modules, "google.auth.transport.requests", transport.requests)


@pytest.mark.parametrize("iss,expected", [
    ("accounts.google.com", True),
    ("https://accounts.google.com", True),
    ("https://evil.example", False),
    (None, False),
])
async def test_oidc_accepts_only_googles_issuer(monkeypatch, iss, expected) -> None:
    captured: dict = {}

    def _verify(token, request, audience):
        captured["audience"] = audience
        return {"iss": iss} if iss is not None else {}

    _stub_google(monkeypatch, _verify)
    assert await server_mod._verify_pubsub_oidc("t", _AUDIENCE) is expected
    assert captured["audience"] == _AUDIENCE


async def test_oidc_verifier_failure_is_a_refusal_not_a_crash(monkeypatch) -> None:
    def _boom(token, request, audience):
        raise ValueError("Token expired")

    _stub_google(monkeypatch, _boom)
    assert await server_mod._verify_pubsub_oidc("t", _AUDIENCE) is False
