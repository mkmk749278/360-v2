"""Tests for src.api.billing_web — the PWA crypto (NOWPayments) billing rail.

What we pin (the doctrine the module header promises):

* Dark-flag-first: disabled → checkout/webhook 503, config shows manual only.
* The client never sets the price — the engine reads WEB_BILLING_TIER_USD.
* The webhook is authoritative: entitlement is granted ONLY on a
  signature-verified ``finished`` IPN, mapped to the one aset_tier path.
* Signature verification (HMAC-SHA512 over sorted JSON) accepts a correctly
  signed body and rejects a tampered one / missing header / bad secret.
* order_id carries (user_id, tier) and a foreign order_id is rejected.
* Amount defence: a signed IPN for less than the tier price never upgrades.
* Idempotency: a redelivered payment_id grants exactly once.
* Renewal stacking: an early renewal extends from the current expiry.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any, Optional

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import config
from src.api import billing_web


IPN_SECRET = "test-ipn-secret-value"


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class FakeUserStore:
    def __init__(self, *, by_uid: Optional[dict] = None, by_id: Optional[dict] = None):
        self._by_uid = by_uid or {}
        self._by_id = by_id or {}
        self.set_tier_calls: list[dict] = []

    async def aget_by_firebase_uid(self, uid: str):
        return self._by_uid.get(uid)

    async def aget_by_id(self, user_id: int):
        return self._by_id.get(user_id)

    async def aset_tier(self, user_id: int, *, tier: str, paid_until):
        self.set_tier_calls.append(
            {"user_id": user_id, "tier": tier, "paid_until": paid_until}
        )
        return SimpleNamespace(user_id=user_id, tier=tier, paid_until=paid_until)


async def _fake_invoice_ok(payload: dict) -> dict:
    return {"invoice_url": "https://nowpayments.example/pay/abc", "id": "inv_123"}


def _build_app(
    *,
    user_store: FakeUserStore,
    identity: Any = None,
    allow_auth: bool = True,
    invoice_creator=_fake_invoice_ok,
    idempotency: Optional[billing_web.InMemoryIdempotencyStore] = None,
) -> FastAPI:
    app = FastAPI()

    def _auth() -> None:
        if not allow_auth:
            raise HTTPException(status_code=401, detail="missing token")

    def _identity_dep():
        return identity

    billing_web.register(
        app,
        user_store=user_store,
        auth=_auth,
        identity_dep=_identity_dep,
        verifier=billing_web.NowPaymentsIpnVerifier(IPN_SECRET),
        idempotency=idempotency or billing_web.InMemoryIdempotencyStore(),
        invoice_creator=invoice_creator,
    )
    return app


def _sign(body: dict, secret: str = IPN_SECRET) -> str:
    canon = billing_web._sorted_json_bytes(body)
    return hmac.new(secret.encode(), canon, hashlib.sha512).hexdigest()


@pytest.fixture
def enable_crypto(monkeypatch):
    """Turn the crypto rail fully live with a configured API key."""
    monkeypatch.setattr(config, "WEB_BILLING_ENABLED", True)
    monkeypatch.setattr(config, "WEB_BILLING_CRYPTO_ENABLED", True)
    monkeypatch.setattr(config, "NOWPAYMENTS_API_KEY", "test-api-key")
    monkeypatch.setattr(config, "WEB_BILLING_TIER_USD", {"assist": 15.0, "auto": 25.0})


# ---------------------------------------------------------------------------
# order_id + verifier units
# ---------------------------------------------------------------------------


def test_order_id_roundtrip():
    oid = billing_web.encode_order_id(42, "auto")
    assert billing_web.decode_order_id(oid) == (42, "auto")


@pytest.mark.parametrize(
    "bad",
    ["", "notours:42:auto:xx", "luminweb:notanint:auto:xx", "luminweb:42:free:xx", "luminweb:42:auto"],
)
def test_decode_rejects_foreign_order_id(bad):
    assert billing_web.decode_order_id(bad) is None


def test_verifier_accepts_correct_signature():
    v = billing_web.NowPaymentsIpnVerifier(IPN_SECRET)
    body = {"b": 2, "a": 1, "payment_status": "finished"}
    raw = json.dumps(body).encode()
    assert v.verify(raw, _sign(body)).ok


def test_verifier_rejects_tamper_and_missing_and_unconfigured():
    v = billing_web.NowPaymentsIpnVerifier(IPN_SECRET)
    body = {"a": 1}
    raw = json.dumps(body).encode()
    assert not v.verify(raw, _sign({"a": 2})).ok       # signature over different body
    assert not v.verify(raw, None).ok                   # missing header
    assert not billing_web.NowPaymentsIpnVerifier("").verify(raw, _sign(body)).ok  # no secret


# ---------------------------------------------------------------------------
# GET /api/billing/web/config
# ---------------------------------------------------------------------------


def test_config_disabled_shows_manual_only(monkeypatch):
    monkeypatch.setattr(config, "WEB_BILLING_ENABLED", False)
    monkeypatch.setattr(config, "WEB_BILLING_CRYPTO_ENABLED", False)
    client = TestClient(_build_app(user_store=FakeUserStore()))
    body = client.get("/api/billing/web/config").json()
    assert body["enabled"] is False
    rail_ids = [r["id"] for r in body["rails"]]
    assert rail_ids == ["manual"]


def test_config_enabled_shows_crypto_prices(enable_crypto):
    client = TestClient(_build_app(user_store=FakeUserStore()))
    body = client.get("/api/billing/web/config").json()
    crypto = next(r for r in body["rails"] if r["id"] == "crypto")
    assert crypto["tiers"]["assist"]["amount"] == 15.0
    assert crypto["tiers"]["auto"]["amount"] == 25.0
    assert "manual" in [r["id"] for r in body["rails"]]


# ---------------------------------------------------------------------------
# POST /api/billing/web/checkout
# ---------------------------------------------------------------------------


def test_checkout_503_when_disabled(monkeypatch):
    monkeypatch.setattr(config, "WEB_BILLING_ENABLED", False)
    client = TestClient(_build_app(user_store=FakeUserStore(), identity={"firebase_uid": "u1"}))
    assert client.post("/api/billing/web/checkout", json={"tier": "auto"}).status_code == 503


def test_checkout_503_when_no_api_key(enable_crypto, monkeypatch):
    monkeypatch.setattr(config, "NOWPAYMENTS_API_KEY", "")
    client = TestClient(_build_app(user_store=FakeUserStore(), identity={"firebase_uid": "u1"}))
    assert client.post("/api/billing/web/checkout", json={"tier": "auto"}).status_code == 503


def test_checkout_400_unknown_tier(enable_crypto):
    store = FakeUserStore(by_uid={"u1": SimpleNamespace(user_id=1)})
    client = TestClient(_build_app(user_store=store, identity={"firebase_uid": "u1"}))
    assert client.post("/api/billing/web/checkout", json={"tier": "gold"}).status_code == 400


def test_checkout_401_without_firebase_uid(enable_crypto):
    client = TestClient(_build_app(user_store=FakeUserStore(), identity={}))
    assert client.post("/api/billing/web/checkout", json={"tier": "auto"}).status_code == 401


def test_checkout_404_when_user_missing(enable_crypto):
    client = TestClient(_build_app(user_store=FakeUserStore(), identity={"firebase_uid": "ghost"}))
    assert client.post("/api/billing/web/checkout", json={"tier": "auto"}).status_code == 404


def test_checkout_happy_path_sets_price_and_order(enable_crypto):
    captured: dict = {}

    async def _capturing_invoice(payload: dict) -> dict:
        captured.update(payload)
        return {"invoice_url": "https://nowpayments.example/pay/xyz", "id": "inv_9"}

    store = FakeUserStore(by_uid={"u1": SimpleNamespace(user_id=7)})
    client = TestClient(
        _build_app(user_store=store, identity={"firebase_uid": "u1"}, invoice_creator=_capturing_invoice)
    )
    resp = client.post("/api/billing/web/checkout", json={"tier": "auto"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["amount_usd"] == 25.0
    assert body["invoice_url"].endswith("/pay/xyz")
    # engine set the money, not the client:
    assert captured["price_amount"] == 25.0
    assert billing_web.decode_order_id(body["order_id"]) == (7, "auto")


# ---------------------------------------------------------------------------
# POST /api/billing/web/crypto/webhook
# ---------------------------------------------------------------------------


def _post_ipn(client: TestClient, body: dict, *, sig: Optional[str] = None):
    raw = json.dumps(body).encode()
    headers = {billing_web.NOWPAYMENTS_SIG_HEADER: sig if sig is not None else _sign(body)}
    return client.post("/api/billing/web/crypto/webhook", content=raw, headers=headers)


def test_webhook_401_on_bad_signature(enable_crypto):
    client = TestClient(_build_app(user_store=FakeUserStore()))
    body = {"payment_status": "finished", "payment_id": "p1", "order_id": billing_web.encode_order_id(1, "auto"), "price_amount": 25.0}
    assert _post_ipn(client, body, sig="deadbeef").status_code == 401


def test_webhook_non_grant_status_grants_nothing(enable_crypto):
    store = FakeUserStore()
    client = TestClient(_build_app(user_store=store))
    body = {"payment_status": "waiting", "payment_id": "p1", "order_id": billing_web.encode_order_id(1, "auto"), "price_amount": 25.0}
    resp = _post_ipn(client, body)
    assert resp.status_code == 200 and resp.json()["granted"] is False
    assert store.set_tier_calls == []


def test_webhook_unrecognised_order_id_422(enable_crypto):
    client = TestClient(_build_app(user_store=FakeUserStore()))
    body = {"payment_status": "finished", "payment_id": "p1", "order_id": "someoneelse:1:auto:xx", "price_amount": 25.0}
    assert _post_ipn(client, body).status_code == 422


def test_webhook_amount_mismatch_rejected(enable_crypto):
    store = FakeUserStore(by_id={1: SimpleNamespace(user_id=1, paid_until=None)})
    client = TestClient(_build_app(user_store=store))
    body = {"payment_status": "finished", "payment_id": "p1", "order_id": billing_web.encode_order_id(1, "auto"), "price_amount": 5.0}
    assert _post_ipn(client, body).status_code == 422
    assert store.set_tier_calls == []


def test_webhook_grants_tier_on_finished(enable_crypto):
    store = FakeUserStore(by_id={3: SimpleNamespace(user_id=3, paid_until=None)})
    client = TestClient(_build_app(user_store=store))
    body = {"payment_status": "finished", "payment_id": "pay_a", "order_id": billing_web.encode_order_id(3, "auto"), "price_amount": 25.0}
    resp = _post_ipn(client, body)
    assert resp.status_code == 200 and resp.json()["granted"] is True
    assert len(store.set_tier_calls) == 1
    call = store.set_tier_calls[0]
    assert call["user_id"] == 3 and call["tier"] == "auto"
    # ~30 days out from now
    delta = call["paid_until"] - datetime.now(timezone.utc)
    assert timedelta(days=29) < delta < timedelta(days=31)


def test_webhook_idempotent_on_duplicate_payment_id(enable_crypto):
    store = FakeUserStore(by_id={1: SimpleNamespace(user_id=1, paid_until=None)})
    dedup = billing_web.InMemoryIdempotencyStore()
    client = TestClient(_build_app(user_store=store, idempotency=dedup))
    body = {"payment_status": "finished", "payment_id": "dup1", "order_id": billing_web.encode_order_id(1, "assist"), "price_amount": 15.0}
    first = _post_ipn(client, body)
    second = _post_ipn(client, body)
    assert first.json()["granted"] is True
    assert second.json()["granted"] is False
    assert len(store.set_tier_calls) == 1


def test_webhook_renewal_stacks_from_current_expiry(enable_crypto):
    future = datetime.now(timezone.utc) + timedelta(days=10)
    store = FakeUserStore(by_id={5: SimpleNamespace(user_id=5, paid_until=future)})
    client = TestClient(_build_app(user_store=store))
    body = {"payment_status": "finished", "payment_id": "renew1", "order_id": billing_web.encode_order_id(5, "auto"), "price_amount": 25.0}
    _post_ipn(client, body)
    paid_until = store.set_tier_calls[0]["paid_until"]
    # extends from the existing expiry (~40 days out), not from now (~30)
    delta = paid_until - datetime.now(timezone.utc)
    assert timedelta(days=39) < delta < timedelta(days=41)


def test_webhook_503_when_ipn_unconfigured():
    app = FastAPI()
    billing_web.register(
        app,
        user_store=FakeUserStore(),
        auth=lambda: None,
        identity_dep=lambda: None,
        verifier=billing_web.NowPaymentsIpnVerifier(""),  # unconfigured
    )
    client = TestClient(app)
    body = {"payment_status": "finished"}
    assert _post_ipn(client, body, sig="x").status_code == 503
