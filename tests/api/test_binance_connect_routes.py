"""Tests for src.api.binance_connect_routes.

What we pin here:

* Auth is required (no token → 401).
* US geoblock fires before any Binance call (saves a RTT + protects
  US users from accidental connect attempts that would persist their
  IP-attempt in our logs).
* Static-token bypass is REJECTED on this route — keys are per-
  Firebase-uid; owner-token cannot connect on behalf of a user.
* Missing ``ENGINE_VPS_PUBLIC_IP`` env var → 500 with an operator-
  facing message (we cannot give users an accurate whitelist IP
  without knowing our own).
* On Binance validation success: provisioning chain runs end-to-end
  — encrypt + KMS-wrap + Firestore-put — and the route returns a
  ``BinanceConnectResponse`` with the truncated key id.
* Each validator-raised exception maps to the expected HTTP status +
  ``X-Connect-Error-Code`` header so the app can render targeted
  fix-up UI.

The Binance call is mocked at the validator boundary (same as the
unit tests for the validator).  KMS + Firestore are mocked at the
module boundary.
"""
from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Test fixtures — build a minimal FastAPI app wired to the route
# ---------------------------------------------------------------------------


def _build_app(*, identity: object = None, allow_auth: bool = True) -> FastAPI:
    """Construct a minimal FastAPI app that registers our route with
    stub auth + stub identity-dep so each test can swap them without
    touching the full ``build_app`` factory."""
    from src.api import binance_connect_routes

    app = FastAPI()

    def _auth_stub() -> None:
        if not allow_auth:
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="missing token")
        return None

    def _identity_stub() -> object:
        return identity

    binance_connect_routes.register(
        app, auth=_auth_stub, identity_dep=_identity_stub
    )
    return app


def _firebase_user(uid: str = "fb-uid-test") -> object:
    """Build a stub identity that looks like a UserStore ``User`` row
    with a populated ``firebase_uid``.  The route reads ``.firebase_uid``
    via getattr — anything truthy with that attribute works."""
    return SimpleNamespace(firebase_uid=uid, user_id=99)


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reset module state + env between tests so order-of-test
    contamination can't mask bugs."""
    from src.security import firestore_keystore, kms_client

    monkeypatch.setenv("ENGINE_VPS_PUBLIC_IP", "203.0.113.42")
    kms_client.reset_for_test()
    firestore_keystore.reset_for_test()
    yield
    kms_client.reset_for_test()
    firestore_keystore.reset_for_test()


# ---------------------------------------------------------------------------
# Auth + geoblock
# ---------------------------------------------------------------------------


def test_no_auth_returns_401() -> None:
    """The auth dependency is the first thing FastAPI evaluates;
    failing it must short-circuit before any other check."""
    app = _build_app(allow_auth=False)
    client = TestClient(app)
    r = client.post(
        "/api/binance/connect",
        json={"api_key": "k" * 16, "api_secret": "s" * 16},
    )
    assert r.status_code == 401


def test_us_geoblock_returns_403_before_binance_call() -> None:
    """The geoblock check runs before the validator, so a US-origin
    request never touches Binance — saves a RTT and prevents us from
    holding the user's secret in memory at all for a request we're
    going to reject."""
    from src.security import binance_connect_validator

    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    with patch.object(
        binance_connect_validator, "_signed_get", new_callable=AsyncMock
    ) as mock_signed:
        r = client.post(
            "/api/binance/connect",
            json={"api_key": "k" * 16, "api_secret": "s" * 16},
            headers={"CF-IPCountry": "US"},
        )
    assert r.status_code == 403
    mock_signed.assert_not_called()


def test_static_token_bypass_rejected_with_401() -> None:
    """The connect route requires a Firebase identity (it needs the
    Firebase uid to key the Firestore blob).  Static-token bypass
    surfaces as ``identity=None`` from the identity dep — must reject
    rather than fall back to a default user."""
    app = _build_app(identity=None)  # static-token bypass returns None
    client = TestClient(app)
    r = client.post(
        "/api/binance/connect",
        json={"api_key": "k" * 16, "api_secret": "s" * 16},
        headers={"CF-IPCountry": "IN"},
    )
    assert r.status_code == 401
    assert "Firebase" in r.json()["detail"]


# ---------------------------------------------------------------------------
# Server misconfiguration paths
# ---------------------------------------------------------------------------


def test_missing_engine_vps_ip_returns_500(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without ENGINE_VPS_PUBLIC_IP we cannot tell the user which IP
    to whitelist on Binance — refuse rather than ship a partial
    answer.  500 + operator-facing message so on-call sees this in
    logs immediately."""
    monkeypatch.delenv("ENGINE_VPS_PUBLIC_IP", raising=False)
    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    r = client.post(
        "/api/binance/connect",
        json={"api_key": "k" * 16, "api_secret": "s" * 16},
        headers={"CF-IPCountry": "IN"},
    )
    assert r.status_code == 500
    assert "ENGINE_VPS_PUBLIC_IP" in r.json()["detail"]


def test_kms_not_initialised_returns_500() -> None:
    """KMS init failed at boot → connect refuses cleanly rather than
    crashing.  Required for clean error surfacing during operator
    setup before all GCP plumbing is wired."""
    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    r = client.post(
        "/api/binance/connect",
        json={"api_key": "k" * 16, "api_secret": "s" * 16},
        headers={"CF-IPCountry": "IN"},
    )
    assert r.status_code == 500
    assert "KMS" in r.json()["detail"]


# ---------------------------------------------------------------------------
# Happy path — full provisioning chain
# ---------------------------------------------------------------------------


def test_happy_path_validates_encrypts_persists_returns_truncated_key() -> None:
    """End-to-end success: validator passes → DEK generated → secret
    encrypted → DEK KMS-wrapped → Firestore put.  Verify each step
    fired AND the response carries the truncated key id (which the
    app uses to confirm-back to the user)."""
    from src.security import (
        binance_connect_validator,
        envelope_crypto,
        firestore_keystore,
        kms_client,
    )

    # Force KMS + Firestore to look initialised; the actual operations
    # are stubbed below.
    fake_kms = MagicMock()
    fake_kms.encrypt.return_value = b"wrapped-dek-bytes"
    kms_client._client = MagicMock(
        wraps=fake_kms,
        spec=kms_client.KmsClient,
    )
    # Easier: install the fake directly.
    kms_client._client = type(
        "FakeKms", (), {"encrypt": lambda self, x: b"wrapped-dek-bytes"}
    )()

    firestore_keystore._db = MagicMock()
    put_blob_mock = MagicMock()
    with patch.object(
        binance_connect_validator, "_signed_get", new_callable=AsyncMock
    ) as mock_signed, patch.object(
        firestore_keystore, "put_key_blob", side_effect=put_blob_mock
    ):
        mock_signed.side_effect = [
            {
                "ipRestrict": True,
                "enableWithdrawals": False,
                "enableFutures": True,
            },
            [{"asset": "USDT", "balance": "0"}],
        ]
        app = _build_app(identity=_firebase_user(uid="fb-success-uid"))
        client = TestClient(app)
        r = client.post(
            "/api/binance/connect",
            json={
                "api_key": "ABCDEFGH" + "x" * 56,
                "api_secret": "s" * 64,
            },
            headers={"CF-IPCountry": "IN"},
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is True
    assert body["key_public_id_first8"] == "ABCDEFGH"
    assert body["withdraw_disabled_ok"] is True
    assert body["futures_enabled_ok"] is True
    assert body["ip_whitelist_ok"] is True
    # Verify the Firestore put happened with the right shape.
    put_blob_mock.assert_called_once()
    call_kwargs = put_blob_mock.call_args.kwargs
    assert call_kwargs["encrypted_dek"] == b"wrapped-dek-bytes"
    assert call_kwargs["key_public_id_first8"] == "ABCDEFGH"
    assert call_kwargs["ip_whitelist_ok"] is True
    assert call_kwargs["withdraw_disabled_ok"] is True
    # Verify the encrypted secret is NOT the plaintext (the encryption
    # step actually ran).
    assert call_kwargs["encrypted_secret"] != b"s" * 64
    # Positional first arg = firebase_uid.
    assert put_blob_mock.call_args.args[0] == "fb-success-uid"


# ---------------------------------------------------------------------------
# Each validator failure mode → mapped HTTP status + error code header
# ---------------------------------------------------------------------------


def _setup_kms_and_firestore_stubs() -> None:
    """Make KMS + Firestore look initialised so the route reaches the
    validator without bailing on the dependency check."""
    from src.security import firestore_keystore, kms_client

    kms_client._client = type(
        "FakeKms", (), {"encrypt": lambda self, x: b"wrapped"}
    )()
    firestore_keystore._db = MagicMock()


@pytest.mark.parametrize(
    "exc_factory, expected_status, expected_code_header",
    [
        (
            lambda v: v.WithdrawEnabledError(v.WithdrawEnabledError.user_message),
            400,
            "WITHDRAW_ENABLED",
        ),
        (
            lambda v: v.FuturesDisabledError(v.FuturesDisabledError.user_message),
            400,
            "FUTURES_DISABLED",
        ),
        (
            lambda v: v.IpRestrictDisabledError(
                v.IpRestrictDisabledError.user_message
            ),
            400,
            "IP_RESTRICT_DISABLED",
        ),
        (
            lambda v: v.IpNotWhitelistedError(v.IpNotWhitelistedError.user_message),
            400,
            "IP_NOT_WHITELISTED",
        ),
        (
            lambda v: v.KeyInvalidError(v.KeyInvalidError.user_message),
            400,
            "KEY_INVALID",
        ),
        (
            lambda v: v.BinanceUnreachableError("Binance returned 503"),
            503,
            "BINANCE_UNREACHABLE",
        ),
    ],
)
def test_each_validator_failure_maps_to_expected_http_status_and_header(
    exc_factory, expected_status, expected_code_header
) -> None:
    """The app uses the ``X-Connect-Error-Code`` header to render
    targeted fix-up UI (per-error-code deep links to Binance settings).
    Pinning the exact header value here is what protects that
    contract from silent drift."""
    from src.security import binance_connect_validator as validator

    _setup_kms_and_firestore_stubs()
    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    with patch.object(
        validator, "validate_binance_key", new_callable=AsyncMock
    ) as mock_validate:
        mock_validate.side_effect = exc_factory(validator)
        r = client.post(
            "/api/binance/connect",
            json={"api_key": "k" * 16, "api_secret": "s" * 16},
            headers={"CF-IPCountry": "IN"},
        )
    assert r.status_code == expected_status, r.text
    assert r.headers.get("X-Connect-Error-Code") == expected_code_header


def test_ip_failures_include_engine_vps_ip_in_response_for_app_display() -> None:
    """IP-related failures must carry the engine VPS IP in both the
    ``X-Engine-VPS-IP`` header AND the detail message — the app
    displays this IP so the user knows exactly what to add to their
    Binance whitelist."""
    from src.security import binance_connect_validator as validator

    _setup_kms_and_firestore_stubs()
    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    with patch.object(
        validator, "validate_binance_key", new_callable=AsyncMock
    ) as mock_validate:
        mock_validate.side_effect = validator.IpNotWhitelistedError(
            validator.IpNotWhitelistedError.user_message
        )
        r = client.post(
            "/api/binance/connect",
            json={"api_key": "k" * 16, "api_secret": "s" * 16},
            headers={"CF-IPCountry": "IN"},
        )
    assert r.status_code == 400
    assert r.headers.get("X-Engine-VPS-IP") == "203.0.113.42"
    assert "203.0.113.42" in r.json()["detail"]
