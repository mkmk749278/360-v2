"""Tests for ``POST /api/auth/telegram-otp/verify`` — the Phase-4
Telegram-OTP → Firebase custom-token bridge.

The endpoint chains:

  1. ``OtpStore.verify`` against the engine-side OTP record
  2. ``UserStore.get_or_create_by_phone`` to materialise the user row
  3. (first-time path) ``firebase_auth.register_user_by_phone`` +
     ``set_firebase_uid`` to record the Firebase identity
  4. ``firebase_auth.create_custom_token`` to mint the bridge token

All Firebase calls are mocked.  OTP store + UserStore are real (tmp_path
sqlite) so the test exercises the real ``get_or_create_by_phone`` and
``set_firebase_uid`` SQL paths.
"""
from __future__ import annotations

import time
from datetime import timedelta
from unittest.mock import patch

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from src.api import firebase_auth  # noqa: E402
from src.api.otp import OtpStore  # noqa: E402
from src.api.server import build_app  # noqa: E402
from src.api.users import UserStore  # noqa: E402


_SECRET = "x" * 64


class _MinimalStubEngine:
    """Lean stub — the telegram-otp-verify endpoint doesn't touch any
    engine state, but build_app expects an engine object."""

    def __init__(self) -> None:
        self._boot_time = time.monotonic()


@pytest.fixture(autouse=True)
def _reset_firebase_module_state():
    firebase_auth.reset_for_test()
    yield
    firebase_auth.reset_for_test()


@pytest.fixture
def user_store(tmp_path) -> UserStore:
    s = UserStore(tmp_path / "lumin.sqlite")
    yield s
    s.close()


@pytest.fixture
def otp_store() -> OtpStore:
    # Generous limits so the test doesn't trip rate-limit / attempt
    # ceilings during setup.
    return OtpStore(max_attempts_per_code=5, max_issues_per_hour=10)


@pytest.fixture
def client(user_store: UserStore, otp_store: OtpStore) -> TestClient:
    app = build_app(
        _MinimalStubEngine(),
        jwt_secret=_SECRET,
        allow_static=False,
        user_store=user_store,
        otp_store=otp_store,
    )
    return TestClient(app)


def _flip_firebase_initialised() -> None:
    """Make :func:`firebase_auth.is_initialised` return True without
    actually loading the Admin SDK."""
    firebase_auth._app = object()
    firebase_auth._project_id = "test-project"


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_happy_path_returns_custom_token(
    client: TestClient, otp_store: OtpStore,
) -> None:
    _flip_firebase_initialised()
    phone = "+15551234567"
    issued = otp_store.issue(phone)
    assert issued.code is not None

    with patch(
        "src.api.firebase_auth.register_user_by_phone",
        return_value="fb-uid-happy",
    ) as mock_register, patch(
        "src.api.firebase_auth.create_custom_token",
        return_value="custom.token.value",
    ) as mock_mint:
        r = client.post(
            "/api/auth/telegram-otp/verify",
            json={"phone_e164": phone, "code": issued.code},
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["custom_token"] == "custom.token.value"
    assert body["tier"] == "free"
    assert body["paid_until"] is None
    assert body["needs_onboarding"] is True
    assert body["user_id"] >= 1
    mock_register.assert_called_once_with(phone)
    mock_mint.assert_called_once_with("fb-uid-happy")


def test_returning_user_skips_firebase_register(
    client: TestClient, otp_store: OtpStore, user_store: UserStore,
) -> None:
    """Second sign-in: ``firebase_uid`` already set on the user row —
    skip ``register_user_by_phone`` and go straight to custom-token
    minting."""
    _flip_firebase_initialised()
    phone = "+15552223333"
    # Pre-seed the user with a firebase_uid.
    existing = user_store.get_or_create_by_phone(phone)
    user_store.set_firebase_uid(existing.user_id, "fb-uid-returning")

    issued = otp_store.issue(phone)
    assert issued.code is not None

    with patch(
        "src.api.firebase_auth.register_user_by_phone",
    ) as mock_register, patch(
        "src.api.firebase_auth.create_custom_token",
        return_value="custom.token.returning",
    ) as mock_mint:
        r = client.post(
            "/api/auth/telegram-otp/verify",
            json={"phone_e164": phone, "code": issued.code},
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["custom_token"] == "custom.token.returning"
    assert body["user_id"] == existing.user_id
    # Already-mapped user → no register call.
    mock_register.assert_not_called()
    mock_mint.assert_called_once_with("fb-uid-returning")


# ---------------------------------------------------------------------------
# Error paths
# ---------------------------------------------------------------------------


def test_wrong_code_returns_400_with_wrong_code(
    client: TestClient, otp_store: OtpStore,
) -> None:
    _flip_firebase_initialised()
    phone = "+15554445555"
    issued = otp_store.issue(phone)
    assert issued.code is not None
    bad_code = "000000" if issued.code != "000000" else "999999"

    with patch(
        "src.api.firebase_auth.register_user_by_phone",
    ) as mock_register, patch(
        "src.api.firebase_auth.create_custom_token",
    ) as mock_mint:
        r = client.post(
            "/api/auth/telegram-otp/verify",
            json={"phone_e164": phone, "code": bad_code},
        )
    assert r.status_code == 400
    assert r.json()["detail"] == "wrong_code"
    # Firebase never consulted on a failed verify.
    mock_register.assert_not_called()
    mock_mint.assert_not_called()


def test_expired_code_returns_400_with_expired(
    user_store: UserStore,
) -> None:
    """Use a sub-second TTL OTP store so we can deterministically
    expire the code without sleeping for the production 5-min TTL."""
    _flip_firebase_initialised()
    phone = "+15556667777"
    short_ttl_store = OtpStore(
        ttl=timedelta(milliseconds=50),
        max_attempts_per_code=5,
        max_issues_per_hour=10,
    )
    app = build_app(
        _MinimalStubEngine(),
        jwt_secret=_SECRET,
        allow_static=False,
        user_store=user_store,
        otp_store=short_ttl_store,
    )
    client = TestClient(app)
    issued = short_ttl_store.issue(phone)
    assert issued.code is not None
    time.sleep(0.1)  # let it expire

    r = client.post(
        "/api/auth/telegram-otp/verify",
        json={"phone_e164": phone, "code": issued.code},
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "expired"


def test_no_record_returns_400(client: TestClient) -> None:
    _flip_firebase_initialised()
    r = client.post(
        "/api/auth/telegram-otp/verify",
        json={"phone_e164": "+15558889999", "code": "123456"},
    )
    assert r.status_code == 400
    assert r.json()["detail"] == "no_record"


def test_firebase_disabled_returns_503(
    client: TestClient, otp_store: OtpStore,
) -> None:
    """OTP verifies cleanly but the Firebase Admin SDK isn't initialised
    → 503 with detail=firebase_disabled."""
    # Note: _reset_firebase_module_state fixture left is_initialised() False.
    phone = "+15550009999"
    issued = otp_store.issue(phone)
    assert issued.code is not None

    r = client.post(
        "/api/auth/telegram-otp/verify",
        json={"phone_e164": phone, "code": issued.code},
    )
    assert r.status_code == 503
    assert r.json()["detail"] == "firebase_disabled"
