"""Tests for the admin manual tier-grant endpoints (owner-only comp).

Covers the ops control-plane HTTP surface added for manually granting
a subscription tier (tester/influencer comp) without a Play Billing
purchase: ``GET /api/admin/users/lookup`` and ``POST
/api/admin/grant-tier``. No network, no real GCP creds — a bare
``UserStore`` against a tmp-path SQLite file.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from src.api.auth import mint_token, mint_user_token, OWNER_TIER  # noqa: E402
from src.api.server import build_app  # noqa: E402
from src.api.users import UserStore  # noqa: E402

_TEST_SECRET = "admin-grant-test-secret-x" * 4


class _StubEngine:  # noqa: D401 - trivial
    pass


@pytest.fixture
def grant_setup(tmp_path):
    """Build the app with a real UserStore + an owner-tier client."""
    engine = _StubEngine()
    db = str(tmp_path / "lumin.sqlite")
    user_store = UserStore(db)
    user = user_store.get_or_create_by_phone("+15551230000")  # free tier
    app = build_app(
        engine,
        jwt_secret=_TEST_SECRET,
        allow_static=False,
        user_store=user_store,
    )
    owner_token = mint_token(secret=_TEST_SECRET, tier=OWNER_TIER)
    owner_client = TestClient(app, headers={"Authorization": f"Bearer {owner_token}"})
    non_owner_token = mint_user_token(
        secret=_TEST_SECRET, user_id=user.user_id, tier="free"
    )
    non_owner_client = TestClient(
        app, headers={"Authorization": f"Bearer {non_owner_token}"}
    )
    return owner_client, non_owner_client, user_store, user.user_id


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------


def test_lookup_requires_owner(grant_setup):
    _, non_owner_client, *_ = grant_setup
    r = non_owner_client.get(
        "/api/admin/users/lookup", params={"phone": "+15551230000"}
    )
    assert r.status_code in (401, 403)


def test_lookup_unknown_phone_returns_404(grant_setup):
    owner_client, *_ = grant_setup
    r = owner_client.get(
        "/api/admin/users/lookup", params={"phone": "+19998887777"}
    )
    assert r.status_code == 404


def test_lookup_known_phone_returns_current_tier(grant_setup):
    owner_client, _, user_store, uid = grant_setup
    r = owner_client.get(
        "/api/admin/users/lookup", params={"phone": "+15551230000"}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["user_id"] == uid
    assert body["tier"] == "free"
    assert body["paid_until"] is None


# ---------------------------------------------------------------------------
# Grant
# ---------------------------------------------------------------------------


def test_grant_requires_owner(grant_setup):
    _, non_owner_client, *_ = grant_setup
    r = non_owner_client.post(
        "/api/admin/grant-tier",
        json={"phone": "+15551230000", "tier": "auto"},
    )
    assert r.status_code in (401, 403)


def test_grant_unknown_phone_returns_404(grant_setup):
    owner_client, *_ = grant_setup
    r = owner_client.post(
        "/api/admin/grant-tier",
        json={"phone": "+19998887777", "tier": "auto"},
    )
    assert r.status_code == 404


def test_grant_auto_defaults_to_thirty_day_expiry(grant_setup):
    owner_client, _, user_store, uid = grant_setup
    before = datetime.now(timezone.utc)
    r = owner_client.post(
        "/api/admin/grant-tier",
        json={"phone": "+15551230000", "tier": "auto", "reason": "influencer comp"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is True
    assert body["tier"] == "auto"
    assert body["paid_until"] is not None

    paid_until = datetime.fromisoformat(body["paid_until"])
    expected = before + timedelta(days=30)
    assert abs((paid_until - expected).total_seconds()) < 60

    # Source of truth updated.
    updated = user_store.get_by_id(uid)
    assert updated.tier == "auto"
    assert updated.paid_until is not None


def test_grant_assist_with_custom_duration(grant_setup):
    owner_client, _, user_store, uid = grant_setup
    before = datetime.now(timezone.utc)
    r = owner_client.post(
        "/api/admin/grant-tier",
        json={"phone": "+15551230000", "tier": "assist", "duration_days": 7},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["tier"] == "assist"
    paid_until = datetime.fromisoformat(body["paid_until"])
    expected = before + timedelta(days=7)
    assert abs((paid_until - expected).total_seconds()) < 60


def test_grant_free_revokes_and_ignores_duration(grant_setup):
    owner_client, _, user_store, uid = grant_setup
    # First grant auto, then revoke to free.
    owner_client.post(
        "/api/admin/grant-tier",
        json={"phone": "+15551230000", "tier": "auto"},
    )
    r = owner_client.post(
        "/api/admin/grant-tier",
        json={"phone": "+15551230000", "tier": "free", "duration_days": 90},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["tier"] == "free"
    assert body["paid_until"] is None
    assert user_store.get_by_id(uid).paid_until is None


def test_grant_invalid_tier_returns_422(grant_setup):
    owner_client, *_ = grant_setup
    r = owner_client.post(
        "/api/admin/grant-tier",
        json={"phone": "+15551230000", "tier": "owner"},
    )
    assert r.status_code == 422


def test_grant_duration_out_of_range_returns_422(grant_setup):
    owner_client, *_ = grant_setup
    r = owner_client.post(
        "/api/admin/grant-tier",
        json={"phone": "+15551230000", "tier": "auto", "duration_days": 0},
    )
    assert r.status_code == 422

    r2 = owner_client.post(
        "/api/admin/grant-tier",
        json={"phone": "+15551230000", "tier": "auto", "duration_days": 400},
    )
    assert r2.status_code == 422


def test_grant_503_when_user_store_unconfigured():
    engine = _StubEngine()
    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    owner_token = mint_token(secret=_TEST_SECRET, tier=OWNER_TIER)
    client = TestClient(app, headers={"Authorization": f"Bearer {owner_token}"})
    r = client.post(
        "/api/admin/grant-tier",
        json={"phone": "+15551230000", "tier": "auto"},
    )
    assert r.status_code == 503
    r2 = client.get("/api/admin/users/lookup", params={"phone": "+15551230000"})
    assert r2.status_code == 503


# ---------------------------------------------------------------------------
# Auto-trade enable/disable (the missing /enable_user operator verb,
# 2026-07-18 — audit finding: kill_switch.enable_user had NO operator-
# facing caller on any surface, so a breaker-tripped user stayed
# disabled forever)
# ---------------------------------------------------------------------------

from unittest.mock import MagicMock  # noqa: E402


@pytest.fixture
def _fake_kill_switch(monkeypatch):
    """In-memory kill-switch double honouring the write→read-back contract."""
    from src.execution import kill_switch

    state: dict = {}

    fake = MagicMock()
    fake.enable_user = MagicMock(
        side_effect=lambda uid: state.__setitem__(uid, False)
    )
    fake.disable_user = MagicMock(
        side_effect=lambda uid, reason="": state.__setitem__(uid, True)
    )
    fake.is_user_disabled = MagicMock(
        side_effect=lambda uid: state.get(uid, False)
    )
    monkeypatch.setattr(kill_switch, "_client", fake)
    yield fake
    kill_switch.reset_for_test()


def test_auto_trade_enable_requires_owner(grant_setup, _fake_kill_switch):
    _, non_owner_client, *_ = grant_setup
    r = non_owner_client.post(
        "/api/admin/users/auto-trade-enable",
        json={"firebase_uid": "fb-someone-123", "enabled": True},
    )
    assert r.status_code in (401, 403)


def test_auto_trade_enable_by_firebase_uid_round_trip(
    grant_setup, _fake_kill_switch
):
    owner_client, *_ = grant_setup
    # Disable first (manual operator disable with an audit reason) …
    r = owner_client.post(
        "/api/admin/users/auto-trade-enable",
        json={
            "firebase_uid": "fb-breaker-victim",
            "enabled": False,
            "reason": "manual test disable",
        },
    )
    assert r.status_code == 200
    assert r.json()["auto_trade_disabled"] is True
    assert r.json()["ok"] is True
    # … then re-enable: the read-back must show the flag cleared.
    r = owner_client.post(
        "/api/admin/users/auto-trade-enable",
        json={"firebase_uid": "fb-breaker-victim", "enabled": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["auto_trade_disabled"] is False
    assert body["ok"] is True
    _fake_kill_switch.enable_user.assert_called_once_with("fb-breaker-victim")


def test_auto_trade_enable_by_phone_resolves_firebase_uid(
    grant_setup, _fake_kill_switch
):
    owner_client, _, user_store, user_id = grant_setup
    user_store.set_firebase_uid(user_id, "fb-of-15551230000")
    r = owner_client.post(
        "/api/admin/users/auto-trade-enable",
        json={"phone": "+15551230000", "enabled": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["firebase_uid"] == "fb-of-15551230000"
    assert body["phone"] == "+15551230000"
    assert body["auto_trade_disabled"] is False


def test_auto_trade_enable_phone_without_firebase_uid_is_409(
    grant_setup, _fake_kill_switch
):
    owner_client, *_ = grant_setup
    r = owner_client.post(
        "/api/admin/users/auto-trade-enable",
        json={"phone": "+15551230000", "enabled": True},
    )
    assert r.status_code == 409
    assert "firebase_uid" in r.json()["detail"]


def test_auto_trade_enable_unknown_phone_is_404(grant_setup, _fake_kill_switch):
    owner_client, *_ = grant_setup
    r = owner_client.post(
        "/api/admin/users/auto-trade-enable",
        json={"phone": "+15559999999", "enabled": True},
    )
    assert r.status_code == 404


def test_auto_trade_enable_requires_exactly_one_identifier(
    grant_setup, _fake_kill_switch
):
    owner_client, *_ = grant_setup
    for payload in (
        {"enabled": True},
        {"phone": "+15551230000", "firebase_uid": "fb-x-12345678", "enabled": True},
    ):
        r = owner_client.post("/api/admin/users/auto-trade-enable", json=payload)
        assert r.status_code == 422


def test_auto_trade_enable_503_when_kill_switch_uninitialised(grant_setup):
    from src.execution import kill_switch

    kill_switch.reset_for_test()
    owner_client, *_ = grant_setup
    r = owner_client.post(
        "/api/admin/users/auto-trade-enable",
        json={"firebase_uid": "fb-anyone-123", "enabled": True},
    )
    assert r.status_code == 503
