"""Tests for Google Play Billing entitlement (B16).

Covers, with no network and no real service-account key:

* ``billing_play`` units — RFC-3339 parse, entitlement state machine,
  subscription parsing, acknowledge, RTDN envelope decoding.
* ``PlayPurchaseStore`` — token→user mapping + relink on upgrade.
* The ``/api/billing/play/verify`` + ``/api/billing/play/rtdn`` endpoints
  against a stub engine, with the Play verifier's HTTP transport mocked.
"""
from __future__ import annotations

import base64
import json
from datetime import datetime, timedelta, timezone

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

import httpx  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.api.billing_play import (  # noqa: E402
    PlayBillingError,
    PlayBillingVerifier,
    PlaySubscriptionState,
    _parse_rfc3339,
)
from src.api.play_purchases import PlayPurchaseStore  # noqa: E402
from src.api.server import build_app  # noqa: E402
from src.api.users import UserStore  # noqa: E402
from src.api.auth import mint_user_token  # noqa: E402

# A bare engine stub — the billing endpoints never touch the engine, and
# (unlike ``tests.api.test_api_smoke._StubEngine``) this avoids dragging in
# the scanner/numpy stack just to exercise the HTTP surface.  ``TestClient``
# used non-context-manager does not run the lifespan, so snapshot_cache is
# never started against it.
_TEST_SECRET = "billing-test-secret-x" * 4


class _StubEngine:  # noqa: D401 - trivial
    pass


def _future(days: int = 30) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)


def _past(days: int = 1) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


def _iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


# ---------------------------------------------------------------------------
# Helpers — a fake httpx transport for the verifier
# ---------------------------------------------------------------------------


def _resp(status_code: int, body: dict | None = None) -> httpx.Response:
    return httpx.Response(status_code, json=body if body is not None else {})


class _FakeHttp:
    """Records calls and replays queued responses by (method, url-suffix)."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self._get: httpx.Response | None = None
        self._post: httpx.Response | None = None

    def queue_get(self, resp: httpx.Response) -> None:
        self._get = resp

    def queue_post(self, resp: httpx.Response) -> None:
        self._post = resp

    async def __call__(self, method, url, **kwargs):  # noqa: ANN001
        self.calls.append((method, url))
        if method == "GET":
            assert self._get is not None, "unexpected GET"
            return self._get
        assert self._post is not None, "unexpected POST"
        return self._post


def _verifier(http: _FakeHttp, *, allowed: frozenset[str] = frozenset()) -> PlayBillingVerifier:
    return PlayBillingVerifier(
        package_name="org.luminapp.lumin",
        allowed_product_ids=allowed,
        paid_tier="paid",
        token_provider=lambda: _const_token(),
        http_send=http,
    )


async def _const_token() -> str:
    return "fake-access-token"


def _sub_body(state: str, *, product="lumin_pro_monthly", expiry=None, ack="ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED", linked=None):
    body = {
        "subscriptionState": state,
        "acknowledgementState": ack,
        "lineItems": [
            {"productId": product, "expiryTime": _iso_z(expiry or _future())}
        ],
    }
    if linked:
        body["linkedPurchaseToken"] = linked
    return body


# ---------------------------------------------------------------------------
# Unit — RFC-3339 + entitlement state machine
# ---------------------------------------------------------------------------


def test_parse_rfc3339_z_suffix():
    dt = _parse_rfc3339("2026-07-23T10:00:00.000Z")
    assert dt is not None and dt.tzinfo is not None
    assert dt.year == 2026 and dt.month == 7 and dt.day == 23


def test_parse_rfc3339_bad_returns_none():
    assert _parse_rfc3339("not-a-date") is None
    assert _parse_rfc3339(None) is None


@pytest.mark.parametrize(
    "state,expiry,expected",
    [
        ("SUBSCRIPTION_STATE_ACTIVE", _future(), True),
        ("SUBSCRIPTION_STATE_IN_GRACE_PERIOD", _future(), True),
        ("SUBSCRIPTION_STATE_CANCELED", _future(), True),   # paid until expiry
        ("SUBSCRIPTION_STATE_CANCELED", _past(), False),    # lapsed
        ("SUBSCRIPTION_STATE_ON_HOLD", _future(), False),
        ("SUBSCRIPTION_STATE_PAUSED", _future(), False),
        ("SUBSCRIPTION_STATE_EXPIRED", _past(), False),
        ("SUBSCRIPTION_STATE_PENDING", _future(), False),
    ],
)
def test_is_entitled_state_machine(state, expiry, expected):
    s = PlaySubscriptionState(
        purchase_token="t", product_id="lumin_pro_monthly", raw_state=state,
        expiry=expiry, acknowledged=True, linked_purchase_token=None,
    )
    assert s.is_entitled is expected


def test_entitlement_for_maps_to_tier():
    v = _verifier(_FakeHttp())
    active = PlaySubscriptionState("t", "p", "SUBSCRIPTION_STATE_ACTIVE", _future(), True, None)
    tier, paid_until = v.entitlement_for(active)
    assert tier == "paid" and paid_until is not None

    held = PlaySubscriptionState("t", "p", "SUBSCRIPTION_STATE_ON_HOLD", _future(), True, None)
    tier, paid_until = v.entitlement_for(held)
    assert tier == "free" and paid_until is None


# ---------------------------------------------------------------------------
# Unit — get_subscription + acknowledge
# ---------------------------------------------------------------------------


async def test_get_subscription_parses_active():
    http = _FakeHttp()
    http.queue_get(_resp(200, _sub_body("SUBSCRIPTION_STATE_ACTIVE")))
    v = _verifier(http)
    state = await v.get_subscription(product_id="lumin_pro_monthly", purchase_token="tok")
    assert state.raw_state == "SUBSCRIPTION_STATE_ACTIVE"
    assert state.product_id == "lumin_pro_monthly"
    assert state.is_entitled is True


async def test_get_subscription_bad_token_is_definitive():
    http = _FakeHttp()
    http.queue_get(_resp(410))
    v = _verifier(http)
    with pytest.raises(PlayBillingError) as ei:
        await v.get_subscription(product_id="p", purchase_token="tok")
    assert ei.value.retryable is False


async def test_get_subscription_auth_error_is_retryable():
    http = _FakeHttp()
    http.queue_get(_resp(403))
    v = _verifier(http)
    with pytest.raises(PlayBillingError) as ei:
        await v.get_subscription(product_id="p", purchase_token="tok")
    assert ei.value.retryable is True


async def test_acknowledge_calls_post():
    http = _FakeHttp()
    http.queue_post(_resp(200))
    v = _verifier(http)
    await v.acknowledge(product_id="lumin_pro_monthly", purchase_token="tok")
    assert any(m == "POST" and ":acknowledge" in u for m, u in http.calls)


# ---------------------------------------------------------------------------
# Unit — RTDN parsing
# ---------------------------------------------------------------------------


def _envelope(payload: dict) -> dict:
    data = base64.b64encode(json.dumps(payload).encode()).decode()
    return {"message": {"data": data, "messageId": "1"}, "subscription": "x"}


def test_parse_rtdn_subscription_renewed():
    note = PlayBillingVerifier.parse_rtdn(_envelope({
        "packageName": "org.luminapp.lumin",
        "subscriptionNotification": {
            "notificationType": 2, "purchaseToken": "tok",
            "subscriptionId": "lumin_pro_monthly",
        },
    }))
    assert note is not None
    assert note.notification_label == "RENEWED"
    assert note.purchase_token == "tok"
    assert note.subscription_id == "lumin_pro_monthly"


def test_parse_rtdn_test_notification():
    note = PlayBillingVerifier.parse_rtdn(_envelope({
        "packageName": "org.luminapp.lumin",
        "testNotification": {"version": "1.0"},
    }))
    assert note is not None and note.is_test is True


def test_parse_rtdn_voided():
    note = PlayBillingVerifier.parse_rtdn(_envelope({
        "packageName": "org.luminapp.lumin",
        "voidedPurchaseNotification": {"purchaseToken": "tok"},
    }))
    assert note is not None and note.is_voided is True and note.purchase_token == "tok"


def test_parse_rtdn_garbage_returns_none():
    assert PlayBillingVerifier.parse_rtdn({"message": {"data": "!!!not-base64"}}) is None
    assert PlayBillingVerifier.parse_rtdn({}) is None


# ---------------------------------------------------------------------------
# Unit — PlayPurchaseStore
# ---------------------------------------------------------------------------


def test_purchase_store_upsert_and_get(tmp_path):
    store = PlayPurchaseStore(tmp_path / "lumin.sqlite")
    store.upsert(
        purchase_token="tok", user_id=7, product_id="lumin_pro_monthly",
        state="SUBSCRIPTION_STATE_ACTIVE", expiry=_future(),
    )
    got = store.get("tok")
    assert got is not None and got.user_id == 7 and got.product_id == "lumin_pro_monthly"


def test_purchase_store_upsert_is_idempotent_on_user(tmp_path):
    store = PlayPurchaseStore(tmp_path / "lumin.sqlite")
    store.upsert(purchase_token="tok", user_id=7, product_id="p", state="ACTIVE", expiry=None)
    # Re-verify with a different (bogus) user must NOT re-bind the token.
    store.upsert(purchase_token="tok", user_id=99, product_id="p", state="CANCELED", expiry=None)
    got = store.get("tok")
    assert got is not None and got.user_id == 7 and got.state == "CANCELED"


def test_purchase_store_relink_carries_user(tmp_path):
    store = PlayPurchaseStore(tmp_path / "lumin.sqlite")
    store.upsert(purchase_token="old", user_id=7, product_id="p", state="ACTIVE", expiry=None)
    store.relink(old_token="old", new_token="new")
    got = store.get("new")
    assert got is not None and got.user_id == 7


def test_purchase_store_relink_noop_when_new_exists(tmp_path):
    store = PlayPurchaseStore(tmp_path / "lumin.sqlite")
    store.upsert(purchase_token="old", user_id=7, product_id="p", state="ACTIVE", expiry=None)
    store.upsert(purchase_token="new", user_id=8, product_id="p", state="ACTIVE", expiry=None)
    store.relink(old_token="old", new_token="new")  # must not clobber user 8
    got = store.get("new")
    assert got is not None and got.user_id == 8


# ---------------------------------------------------------------------------
# Endpoint — verify + rtdn
# ---------------------------------------------------------------------------


@pytest.fixture
def billing_setup(tmp_path):
    """Build the app with a UserStore + a mocked Play verifier."""
    engine = _StubEngine()
    db = str(tmp_path / "lumin.sqlite")
    user_store = UserStore(db)
    user = user_store.get_or_create_by_phone("+15551234567")  # free tier
    purchases = PlayPurchaseStore(db)
    http = _FakeHttp()
    verifier = _verifier(http, allowed=frozenset({"lumin_pro_monthly"}))
    app = build_app(
        engine,
        jwt_secret=_TEST_SECRET,
        allow_static=False,
        user_store=user_store,
        play_verifier=verifier,
        play_purchases=purchases,
    )
    token = mint_user_token(secret=_TEST_SECRET, user_id=user.user_id, tier="free")
    client = TestClient(app, headers={"Authorization": f"Bearer {token}"})
    return client, http, user_store, purchases, user.user_id


def test_verify_grants_paid_and_returns_token(billing_setup):
    client, http, user_store, purchases, uid = billing_setup
    http.queue_get(_resp(200, _sub_body("SUBSCRIPTION_STATE_ACTIVE", ack="ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED")))
    r = client.post("/api/billing/play/verify", json={
        "product_id": "lumin_pro_monthly", "purchase_token": "tok-123",
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is True and body["tier"] == "paid"
    assert body["paid_until"] is not None
    assert body["token"]  # fresh JWT handed back
    # Source of truth updated.
    assert user_store.get_by_id(uid).tier == "paid"
    # Token mapped to the user for future RTDN.
    assert purchases.get("tok-123").user_id == uid


def test_verify_unknown_product_rejected(billing_setup):
    client, http, *_ = billing_setup
    r = client.post("/api/billing/play/verify", json={
        "product_id": "not_a_real_product", "purchase_token": "tok",
    })
    assert r.status_code == 400


def test_verify_acknowledges_when_pending(billing_setup):
    client, http, *_ = billing_setup
    http.queue_get(_resp(200, _sub_body("SUBSCRIPTION_STATE_ACTIVE", ack="ACKNOWLEDGEMENT_STATE_PENDING")))
    http.queue_post(_resp(200))
    r = client.post("/api/billing/play/verify", json={
        "product_id": "lumin_pro_monthly", "purchase_token": "tok-9",
    })
    assert r.status_code == 200
    assert any(m == "POST" and ":acknowledge" in u for m, u in http.calls)


def test_verify_503_when_not_configured(tmp_path):
    engine = _StubEngine()
    user_store = UserStore(str(tmp_path / "lumin.sqlite"))
    u = user_store.get_or_create_by_phone("+15550000000")
    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False, user_store=user_store)
    token = mint_user_token(secret=_TEST_SECRET, user_id=u.user_id, tier="free")
    client = TestClient(app, headers={"Authorization": f"Bearer {token}"})
    r = client.post("/api/billing/play/verify", json={"product_id": "p", "purchase_token": "t"})
    assert r.status_code == 503


def test_rtdn_renewal_updates_entitlement(billing_setup):
    client, http, user_store, purchases, uid = billing_setup
    # Pre-existing mapping (as if the user verified earlier).
    purchases.upsert(purchase_token="tok-r", user_id=uid, product_id="lumin_pro_monthly",
                     state="SUBSCRIPTION_STATE_ACTIVE", expiry=_future(1))
    user_store.set_tier(uid, tier="paid", paid_until=_future(1))
    # RTDN RENEWED → engine re-fetches and sees a later expiry.
    http.queue_get(_resp(200, _sub_body("SUBSCRIPTION_STATE_ACTIVE", expiry=_future(31))))
    r = client.post("/api/billing/play/rtdn", json=_envelope({
        "packageName": "org.luminapp.lumin",
        "subscriptionNotification": {
            "notificationType": 2, "purchaseToken": "tok-r",
            "subscriptionId": "lumin_pro_monthly",
        },
    }))
    assert r.status_code == 200, r.text
    assert r.json()["handled"] == "RENEWED"
    assert user_store.get_by_id(uid).tier == "paid"


def test_rtdn_expired_token_downgrades(billing_setup):
    client, http, user_store, purchases, uid = billing_setup
    purchases.upsert(purchase_token="tok-x", user_id=uid, product_id="lumin_pro_monthly",
                     state="SUBSCRIPTION_STATE_ACTIVE", expiry=_future(1))
    user_store.set_tier(uid, tier="paid", paid_until=_future(1))
    # Google reports the token as gone (410) → definitive revoke.
    http.queue_get(_resp(410))
    r = client.post("/api/billing/play/rtdn", json=_envelope({
        "packageName": "org.luminapp.lumin",
        "subscriptionNotification": {
            "notificationType": 13, "purchaseToken": "tok-x",
            "subscriptionId": "lumin_pro_monthly",
        },
    }))
    assert r.status_code == 200
    assert user_store.get_by_id(uid).tier == "free"


def test_rtdn_unknown_token_ignored(billing_setup):
    client, http, *_ = billing_setup
    r = client.post("/api/billing/play/rtdn", json=_envelope({
        "packageName": "org.luminapp.lumin",
        "subscriptionNotification": {
            "notificationType": 2, "purchaseToken": "never-seen",
            "subscriptionId": "lumin_pro_monthly",
        },
    }))
    assert r.status_code == 200
    assert r.json()["handled"] == "ignored:unknown-token"


def test_rtdn_test_notification_acked(billing_setup):
    client, http, *_ = billing_setup
    r = client.post("/api/billing/play/rtdn", json=_envelope({
        "packageName": "org.luminapp.lumin",
        "testNotification": {"version": "1.0"},
    }))
    assert r.status_code == 200 and r.json()["handled"] == "test"


def test_profile_downgrades_expired_paid_user(billing_setup):
    client, http, user_store, purchases, uid = billing_setup
    # Paid but already past expiry, and no RTDN arrived (the belt-and-braces case).
    user_store.set_tier(uid, tier="paid", paid_until=_past(1))
    r = client.get("/api/profile")
    assert r.status_code == 200, r.text
    assert r.json()["tier"] == "free"
    assert user_store.get_by_id(uid).tier == "free"  # persisted
