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


class FakeReferralRewards:
    """Stands in for ReferralRewardsService — records the hook calls."""

    def __init__(self, *, eligible: bool = False):
        self.eligible = eligible
        self.paid_calls: list[dict] = []

    async def discount_eligible(self, user_id: int) -> bool:
        return self.eligible

    async def on_paid_period(self, user_id: int, **kwargs) -> None:
        self.paid_calls.append({"user_id": user_id, **kwargs})

    async def compose_entitlement(self, user_id: int, tier: str, paid_until):
        return tier, paid_until


def _build_app(
    *,
    user_store: FakeUserStore,
    identity: Any = None,
    allow_auth: bool = True,
    invoice_creator=_fake_invoice_ok,
    idempotency: Optional[billing_web.InMemoryIdempotencyStore] = None,
    referral_rewards: Any = None,
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
        referral_rewards=referral_rewards,
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
    assert billing_web.decode_order_id(oid) == (42, "auto", False)


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
    assert billing_web.decode_order_id(body["order_id"]) == (7, "auto", False)


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


# ---------------------------------------------------------------------------
# _create_invoice_http — provider failures surface cleanly (not a bare 500)
# ---------------------------------------------------------------------------


class _FakeResp:
    def __init__(self, status_code: int, payload: Optional[dict] = None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload


class _FakeAsyncClient:
    def __init__(self, behavior):
        self._behavior = behavior

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def post(self, url, json=None, headers=None):
        return self._behavior()


def _patch_httpx(monkeypatch, behavior):
    monkeypatch.setattr(
        billing_web.httpx, "AsyncClient", lambda *a, **k: _FakeAsyncClient(behavior)
    )


async def test_create_invoice_success(monkeypatch):
    _patch_httpx(monkeypatch, lambda: _FakeResp(200, {"invoice_url": "u", "id": "i"}))
    out = await billing_web._create_invoice_http({"price_amount": 25})
    assert out["invoice_url"] == "u"


async def test_create_invoice_surfaces_provider_status(monkeypatch):
    # A provider 403 (key/environment/IP) becomes a clean 502 that NAMES the
    # status — previously it was hidden behind a bare "retry later".
    _patch_httpx(monkeypatch, lambda: _FakeResp(403))
    from fastapi import HTTPException as _HTTPExc

    with pytest.raises(_HTTPExc) as ei:
        await billing_web._create_invoice_http({})
    assert ei.value.status_code == 502
    assert "403" in ei.value.detail


async def test_create_invoice_handles_unreachable_provider(monkeypatch):
    # A network error must NOT escape as an unhandled 500 (which the browser
    # reports as a bare "failed to fetch") — it becomes a 502.
    def _raise():
        raise billing_web.httpx.ConnectError("boom")

    _patch_httpx(monkeypatch, _raise)
    from fastapi import HTTPException as _HTTPExc

    with pytest.raises(_HTTPExc) as ei:
        await billing_web._create_invoice_http({})
    assert ei.value.status_code == 502
    assert "unreachable" in ei.value.detail


# ---------------------------------------------------------------------------
# Referral Phase 2 (2026-07-21) — discounted checkout + commission hooks
# ---------------------------------------------------------------------------


def test_checkout_applies_referral_discount_for_eligible_referee(
    enable_crypto, monkeypatch,
):
    monkeypatch.setattr(config, "REFERRAL_DISCOUNT_PERCENT", 50)
    captured: dict = {}

    async def _capturing_invoice(payload: dict) -> dict:
        captured.update(payload)
        return {"invoice_url": "https://nowpayments.example/pay/d", "id": "inv_d"}

    store = FakeUserStore(by_uid={"u1": SimpleNamespace(user_id=7)})
    client = TestClient(
        _build_app(
            user_store=store,
            identity={"firebase_uid": "u1"},
            invoice_creator=_capturing_invoice,
            referral_rewards=FakeReferralRewards(eligible=True),
        )
    )
    body = client.post("/api/billing/web/checkout", json={"tier": "auto"}).json()
    assert body["amount_usd"] == 12.5
    assert body["discounted"] is True and body["discount_percent"] == 50
    assert captured["price_amount"] == 12.5
    assert billing_web.decode_order_id(body["order_id"]) == (7, "auto", True)


def test_checkout_full_price_when_not_eligible(enable_crypto):
    store = FakeUserStore(by_uid={"u1": SimpleNamespace(user_id=7)})
    client = TestClient(
        _build_app(
            user_store=store,
            identity={"firebase_uid": "u1"},
            referral_rewards=FakeReferralRewards(eligible=False),
        )
    )
    body = client.post("/api/billing/web/checkout", json={"tier": "auto"}).json()
    assert body["amount_usd"] == 25.0 and body["discounted"] is False
    assert billing_web.decode_order_id(body["order_id"]) == (7, "auto", False)


def test_webhook_accepts_discounted_amount_only_on_flagged_order(
    enable_crypto, monkeypatch,
):
    monkeypatch.setattr(config, "REFERRAL_DISCOUNT_PERCENT", 50)
    store = FakeUserStore(by_id={3: SimpleNamespace(user_id=3, paid_until=None)})
    rewards = FakeReferralRewards()
    client = TestClient(_build_app(user_store=store, referral_rewards=rewards))

    # Discount-flagged order at the discounted price → grant.
    body = {
        "payment_status": "finished",
        "payment_id": "pd1",
        "order_id": billing_web.encode_order_id(3, "auto", discounted=True),
        "price_amount": 12.5,
    }
    assert _post_ipn(client, body).json()["granted"] is True

    # UNflagged order at the discounted price → amount defence rejects.
    body2 = {
        "payment_status": "finished",
        "payment_id": "pd2",
        "order_id": billing_web.encode_order_id(3, "auto"),
        "price_amount": 12.5,
    }
    assert _post_ipn(client, body2).status_code == 422


def test_webhook_grant_fires_commission_hook_with_actual_amount(enable_crypto):
    store = FakeUserStore(by_id={3: SimpleNamespace(user_id=3, paid_until=None)})
    rewards = FakeReferralRewards()
    client = TestClient(_build_app(user_store=store, referral_rewards=rewards))
    body = {
        "payment_status": "finished",
        "payment_id": "pay_c",
        "order_id": billing_web.encode_order_id(3, "auto"),
        "price_amount": 25.0,
    }
    assert _post_ipn(client, body).json()["granted"] is True
    assert len(rewards.paid_calls) == 1
    call = rewards.paid_calls[0]
    assert call["user_id"] == 3
    assert call["amount"] == 25.0 and call["currency"] == "USD"
    assert call["purchase_token"] == "npw:pay_c"
    assert call["period_expiry"] is not None
