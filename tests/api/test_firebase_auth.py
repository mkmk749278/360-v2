"""Tests for src.api.firebase_auth — wraps firebase_admin.auth.

All Firebase SDK calls are mocked.  These tests verify the wrapper's
exception-to-AuthError translation, the PhoneNumberAlreadyExistsError
fall-through to ``get_user_by_phone_number``, and the bytes→str
decoding of custom tokens.

The module's ``_app`` singleton is reset between tests so each case
starts from a clean ``is_initialised() == False`` state.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.api import firebase_auth
from src.api.auth import AuthError


@pytest.fixture(autouse=True)
def _reset_firebase_module_state():
    """Each test starts from ``is_initialised() == False``."""
    firebase_auth.reset_for_test()
    yield
    firebase_auth.reset_for_test()


# ---------------------------------------------------------------------------
# verify_id_token
# ---------------------------------------------------------------------------


def _force_initialised() -> None:
    """Flip ``_app`` to a truthy sentinel so ``is_initialised`` returns True
    without actually touching firebase_admin."""
    firebase_auth._app = object()
    firebase_auth._project_id = "test-project"


def test_verify_id_token_returns_claims_dict() -> None:
    _force_initialised()
    fake_claims = {"uid": "fb-uid-1", "phone_number": "+15551234567"}
    with patch(
        "firebase_admin.auth.verify_id_token",
        return_value=fake_claims,
    ) as mock_verify:
        result = firebase_auth.verify_id_token("some.id.token")
    assert result == fake_claims
    mock_verify.assert_called_once_with("some.id.token")


def test_verify_id_token_raises_auth_error_on_firebase_failure() -> None:
    _force_initialised()
    with patch(
        "firebase_admin.auth.verify_id_token",
        side_effect=ValueError("token expired"),
    ):
        with pytest.raises(AuthError, match="firebase id-token verification failed"):
            firebase_auth.verify_id_token("bad.id.token")


def test_verify_id_token_raises_when_not_initialised() -> None:
    # No _force_initialised — _app is None.
    with pytest.raises(AuthError, match="not initialised"):
        firebase_auth.verify_id_token("any.token")


# ---------------------------------------------------------------------------
# register_user_by_phone
# ---------------------------------------------------------------------------


def test_register_user_by_phone_returns_new_uid() -> None:
    _force_initialised()
    fake_record = SimpleNamespace(uid="fb-uid-new")
    with patch(
        "firebase_admin.auth.create_user",
        return_value=fake_record,
    ) as mock_create:
        uid = firebase_auth.register_user_by_phone("+15551234567")
    assert uid == "fb-uid-new"
    mock_create.assert_called_once_with(phone_number="+15551234567")


def test_register_user_by_phone_handles_already_exists() -> None:
    """Existing Firebase user → catch PhoneNumberAlreadyExistsError and
    return the existing uid via ``get_user_by_phone_number``."""
    _force_initialised()
    import firebase_admin.auth as fb_auth_mod

    existing_record = SimpleNamespace(uid="fb-uid-existing")
    # Construct a PhoneNumberAlreadyExistsError without invoking its
    # actual constructor (signature varies across firebase-admin
    # versions) — bypass __init__ via __new__.
    err = fb_auth_mod.PhoneNumberAlreadyExistsError.__new__(
        fb_auth_mod.PhoneNumberAlreadyExistsError
    )
    with patch(
        "firebase_admin.auth.create_user", side_effect=err,
    ), patch(
        "firebase_admin.auth.get_user_by_phone_number",
        return_value=existing_record,
    ) as mock_lookup:
        uid = firebase_auth.register_user_by_phone("+15551234567")
    assert uid == "fb-uid-existing"
    mock_lookup.assert_called_once_with("+15551234567")


def test_register_user_by_phone_raises_auth_error_on_other_failure() -> None:
    _force_initialised()
    with patch(
        "firebase_admin.auth.create_user",
        side_effect=RuntimeError("boom"),
    ):
        with pytest.raises(AuthError, match="register_user_by_phone failed"):
            firebase_auth.register_user_by_phone("+15551234567")


def test_register_user_by_phone_raises_when_not_initialised() -> None:
    with pytest.raises(AuthError, match="not initialised"):
        firebase_auth.register_user_by_phone("+15551234567")


# ---------------------------------------------------------------------------
# create_custom_token
# ---------------------------------------------------------------------------


def test_create_custom_token_returns_str_from_bytes() -> None:
    _force_initialised()
    with patch(
        "firebase_admin.auth.create_custom_token",
        return_value=b"abc.def.ghi",
    ) as mock_mint:
        token = firebase_auth.create_custom_token("fb-uid-1")
    assert isinstance(token, str)
    assert token == "abc.def.ghi"
    mock_mint.assert_called_once_with("fb-uid-1")


def test_create_custom_token_handles_already_str() -> None:
    """Defensive: some firebase-admin versions return str directly."""
    _force_initialised()
    with patch(
        "firebase_admin.auth.create_custom_token",
        return_value="already.a.string",
    ):
        token = firebase_auth.create_custom_token("fb-uid-1")
    assert token == "already.a.string"


def test_create_custom_token_raises_auth_error_on_failure() -> None:
    _force_initialised()
    with patch(
        "firebase_admin.auth.create_custom_token",
        side_effect=RuntimeError("network"),
    ):
        with pytest.raises(AuthError, match="create_custom_token failed"):
            firebase_auth.create_custom_token("fb-uid-1")


def test_create_custom_token_raises_when_not_initialised() -> None:
    with pytest.raises(AuthError, match="not initialised"):
        firebase_auth.create_custom_token("fb-uid-1")


# ---------------------------------------------------------------------------
# init_firebase_admin idempotence
# ---------------------------------------------------------------------------


def test_init_is_idempotent() -> None:
    """Second call with the SDK already initialised must be a no-op
    rather than raising — callers shouldn't have to guard with
    ``is_initialised``."""
    _force_initialised()
    # The body of init_firebase_admin short-circuits when ``_app`` is
    # already set — so we don't even need to mock firebase_admin here.
    firebase_auth.init_firebase_admin("/dev/null", "test-project")
    # Still initialised, same project — no re-init.
    assert firebase_auth.is_initialised() is True


def test_is_initialised_false_before_init() -> None:
    assert firebase_auth.is_initialised() is False
