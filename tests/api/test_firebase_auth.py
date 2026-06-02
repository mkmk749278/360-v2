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


# ---------------------------------------------------------------------------
# JWKS pre-warm — boot-time cert cache seeding + measurement
# ---------------------------------------------------------------------------


def test_build_prewarm_token_carries_valid_claims() -> None:
    """The probe token must pass firebase_admin's claim gate (correct iss,
    aud, sub, exp) so the SDK proceeds to the cert fetch before failing on
    the garbage signature.  A malformed-claims probe (the old server.py bug)
    fails claim validation FIRST and never fetches — a silent no-op."""
    import base64
    import json

    token = firebase_auth._build_prewarm_token("test-project")
    header_b64, payload_b64, sig = token.split(".")

    def _decode(seg: str) -> dict:
        seg += "=" * (-len(seg) % 4)  # restore base64url padding
        return json.loads(base64.urlsafe_b64decode(seg))

    header = _decode(header_b64)
    payload = _decode(payload_b64)
    assert header["alg"] == "RS256"
    assert header["kid"]  # a kid must be present or the SDK rejects pre-fetch
    # The claims that must be correct for the SDK to reach the cert fetch:
    assert payload["iss"] == "https://securetoken.google.com/test-project"
    assert payload["aud"] == "test-project"
    assert payload["sub"]
    assert payload["exp"] > payload["iat"]
    assert sig  # signature segment present (garbage is fine — fetch precedes verify)


def test_prewarm_jwks_once_returns_negative_when_not_initialised() -> None:
    """Nothing to warm when Firebase isn't wired — return the -1.0 sentinel
    so the caller's log distinguishes 'skipped' from 'warmed in 0ms'."""
    assert firebase_auth.is_initialised() is False
    assert firebase_auth.prewarm_jwks_once() == -1.0


def test_prewarm_jwks_once_measures_and_swallows_verify_failure() -> None:
    """When initialised, the warm calls the SDK verify (which fails on the
    garbage signature — expected) and returns a non-negative measured
    duration.  The failure must NOT propagate; the cert fetch side effect is
    the point, not the verification result."""
    _force_initialised()
    with patch(
        "firebase_admin.auth.verify_id_token",
        side_effect=ValueError("garbage signature — expected"),
    ) as mock_verify:
        dur = firebase_auth.prewarm_jwks_once()
    mock_verify.assert_called_once()
    assert dur >= 0.0  # measured, not the -1.0 not-initialised sentinel


def test_verify_id_token_warns_on_slow_cold_fetch() -> None:
    """A verify call slower than the cold-fetch bar must emit a WARNING — the
    instrument that reveals a JWKS cold fetch landing on a live request.

    loguru's pytest bridge is sticky (see test_geoblock), so rather than
    asserting on captured records we patch the module logger and assert the
    warning verb fired.  time.monotonic is patched to advance past the
    threshold deterministically (no real sleep)."""
    from unittest.mock import MagicMock

    _force_initialised()
    fake_claims = {"uid": "fb-slow", "phone_number": "+15550000000"}

    # verify_id_token reads time.monotonic three times: cache-check (now),
    # verify_start, verify_end.  Make (verify_end - verify_start) exceed the
    # cold-fetch bar so the WARNING branch is taken.
    over = firebase_auth._COLD_FETCH_WARN_S + 0.05
    ticks = iter([100.0, 100.0, 100.0 + over])
    fake_log = MagicMock()
    with patch("firebase_admin.auth.verify_id_token", return_value=fake_claims), \
            patch("src.api.firebase_auth.time.monotonic", side_effect=lambda: next(ticks)), \
            patch("src.api.firebase_auth.log", fake_log):
        result = firebase_auth.verify_id_token("slow.cold.token")

    assert result == fake_claims  # instrumentation must not alter the result
    assert fake_log.warning.called, "expected a cold-fetch WARNING when verify is slow"
    warn_msg = fake_log.warning.call_args[0][0]
    assert "slow" in warn_msg.lower()


def test_verify_id_token_no_warn_on_fast_verify() -> None:
    """A warm (sub-threshold) verify must stay silent — keeps the cold-fetch
    WARNING high-signal on a busy engine instead of firing every request."""
    from unittest.mock import MagicMock

    _force_initialised()
    fake_claims = {"uid": "fb-fast", "phone_number": "+15551112222"}
    ticks = iter([100.0, 100.0, 100.0 + 0.001])  # 1ms — well under the bar
    fake_log = MagicMock()
    with patch("firebase_admin.auth.verify_id_token", return_value=fake_claims), \
            patch("src.api.firebase_auth.time.monotonic", side_effect=lambda: next(ticks)), \
            patch("src.api.firebase_auth.log", fake_log):
        firebase_auth.verify_id_token("fast.warm.token")

    assert not fake_log.warning.called, "fast verify must not emit the cold-fetch WARNING"
