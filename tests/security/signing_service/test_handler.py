"""Tests for src.security.signing_service.handler.

The security-critical signing path.  KMS + Firestore + aiohttp are
mocked at the module boundary so each error path is exercisable in
isolation.

What we pin:

* ``ping`` works without touching any GCP service (liveness probe
  must not depend on KMS).
* Happy path runs the full chain (Firestore read → KMS Decrypt →
  AES-GCM decrypt → signed HTTP → response).
* Each failure mode raises the matching ``ERR_*`` code:
  - KEY_BLOB_NOT_FOUND when Firestore says no doc.
  - KMS_DECRYPT_FAILED when KMS rejects.
  - CRYPTO_DECRYPT_FAILED on AES-GCM tag mismatch (= corrupted blob
    or wrong DEK).
  - BINANCE_HTTP_ERROR when Binance returns 4xx/5xx.
  - BINANCE_UNREACHABLE on network failure.
  - BAD_REQUEST for unknown verbs / missing fields.
* The response **never** contains the plaintext secret or DEK in
  any field — parametrised "secret/DEK string must not appear in
  serialised response" test.
* The decoded HTTP body is forwarded as-is to the response — no
  post-processing in the handler so callers can inspect the raw
  Binance response.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cryptography.exceptions import InvalidTag

from src.security import envelope_crypto, firestore_keystore, kms_client
from src.security.signing_service import handler, protocol


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_blob(
    *,
    api_key_full: str = "test-api-key",
    encrypted_secret: bytes = b"placeholder_ciphertext",
    encrypted_dek: bytes = b"placeholder_wrapped_dek",
) -> firestore_keystore.UserKeyBlob:
    return firestore_keystore.UserKeyBlob(
        uid="test-uid",
        encrypted_secret=encrypted_secret,
        encrypted_dek=encrypted_dek,
        api_key_full=api_key_full,
        key_public_id_first8=api_key_full[:8],
        ip_whitelist_ok=True,
        withdraw_disabled_ok=True,
        connected_at=datetime.now(timezone.utc),
        last_validated_at=datetime.now(timezone.utc),
    )


def _make_real_encrypted_blob(plaintext: bytes = b"my_binance_secret") -> tuple[bytes, bytes]:
    """Produce ``(encrypted_secret_raw, dek)`` so tests that exercise
    the real envelope-crypto decrypt have a valid blob to feed in."""
    dek = envelope_crypto.generate_dek()
    encrypted = envelope_crypto.encrypt_secret(dek, plaintext)
    return encrypted.raw, dek


@pytest.fixture(autouse=True)
def _reset_state():
    kms_client.reset_for_test()
    firestore_keystore.reset_for_test()
    yield
    kms_client.reset_for_test()
    firestore_keystore.reset_for_test()


# ---------------------------------------------------------------------------
# ping
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ping_returns_ok_without_touching_kms_or_firestore() -> None:
    """Liveness probe must not depend on KMS / Firestore — otherwise
    a transient GCP outage would mark the signing service unhealthy
    and the engine would stop sending requests."""
    request = protocol.SignRequest(id="ping-1", verb="ping")
    response = await handler.handle_request(request)
    assert response.ok is True
    assert response.binance_status == 200
    assert response.binance_body == {"pong": True}


# ---------------------------------------------------------------------------
# Happy path — full unwrap + signed call
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_happy_path_runs_full_unwrap_and_signed_call() -> None:
    """The end-to-end success path: Firestore → KMS → AES-GCM → signed
    HTTP → response forwarded.  Verify each link fires AND the
    response forwards the Binance status + body."""
    plaintext_secret = b"my_real_binance_secret_string_64chars_long_ABCDEFGHIJKLMNOP"
    encrypted_raw, dek = _make_real_encrypted_blob(plaintext_secret)
    blob = _make_blob(
        api_key_full="A" * 64,
        encrypted_secret=encrypted_raw,
        encrypted_dek=b"opaque-kms-ciphertext",
    )

    # Wire KMS so its decrypt returns the real DEK from above.
    fake_kms = MagicMock()
    fake_kms.decrypt.return_value = dek
    kms_client._client = fake_kms

    # Wire Firestore to return our blob.
    with patch.object(
        firestore_keystore, "get_key_blob", return_value=blob
    ), patch.object(
        handler, "_signed_call", new_callable=AsyncMock
    ) as mock_signed:
        mock_signed.return_value = (200, [{"asset": "USDT", "balance": "100"}])
        request = protocol.SignRequest(
            id="happy-1",
            verb="binance_signed_get",
            firebase_uid="test-uid",
            base="futures",
            path="/fapi/v2/balance",
        )
        response = await handler.handle_request(request)
    assert response.ok is True
    assert response.binance_status == 200
    assert response.binance_body == [{"asset": "USDT", "balance": "100"}]
    # Verify the signed-call helper received the PLAINTEXT secret that
    # AES-GCM unwrapped — proves the unwrap chain actually ran.
    assert mock_signed.call_args.kwargs["api_secret"] == plaintext_secret.decode("utf-8")
    # Verify the api_key from the blob was forwarded.
    assert mock_signed.call_args.kwargs["api_key"] == "A" * 64


# ---------------------------------------------------------------------------
# Failure: KEY_BLOB_NOT_FOUND
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_blob_returns_key_blob_not_found() -> None:
    with patch.object(
        firestore_keystore,
        "get_key_blob",
        side_effect=firestore_keystore.KeyBlobNotFoundError("no blob"),
    ):
        request = protocol.SignRequest(
            id="x",
            verb="binance_signed_get",
            firebase_uid="not-connected",
            path="/fapi/v2/balance",
        )
        response = await handler.handle_request(request)
    assert response.ok is False
    assert response.error_code == protocol.ERR_KEY_BLOB_NOT_FOUND


# ---------------------------------------------------------------------------
# Failure: KMS_DECRYPT_FAILED — distinct from crypto failure
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_kms_decrypt_failure_returns_kms_typed_code() -> None:
    """KMS rejecting Decrypt (IAM revoked, key disabled, GCP outage)
    is TRANSIENT in nature — caller may retry.  Distinguish from
    CRYPTO_DECRYPT_FAILED (hard fail, user must reconnect)."""
    blob = _make_blob()
    fake_kms = MagicMock()
    fake_kms.decrypt.side_effect = RuntimeError("PermissionDenied: ...")
    kms_client._client = fake_kms

    with patch.object(firestore_keystore, "get_key_blob", return_value=blob):
        request = protocol.SignRequest(
            id="x",
            verb="binance_signed_get",
            firebase_uid="test-uid",
            path="/fapi/v2/balance",
        )
        response = await handler.handle_request(request)
    assert response.ok is False
    assert response.error_code == protocol.ERR_KMS_DECRYPT_FAILED


# ---------------------------------------------------------------------------
# Failure: CRYPTO_DECRYPT_FAILED — AES-GCM tag mismatch
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_aes_gcm_tag_mismatch_returns_crypto_typed_code() -> None:
    """Corrupted ciphertext (Firestore tampered) or wrong DEK (rare
    if KMS is right, but defence-in-depth).  Hard failure; user must
    reconnect."""
    encrypted_raw, _real_dek = _make_real_encrypted_blob(b"original")
    wrong_dek = envelope_crypto.generate_dek()  # different from _real_dek
    blob = _make_blob(encrypted_secret=encrypted_raw, encrypted_dek=b"wrapped-but-wrong")

    fake_kms = MagicMock()
    fake_kms.decrypt.return_value = wrong_dek
    kms_client._client = fake_kms

    with patch.object(firestore_keystore, "get_key_blob", return_value=blob):
        request = protocol.SignRequest(
            id="x",
            verb="binance_signed_get",
            firebase_uid="test-uid",
            path="/fapi/v2/balance",
        )
        response = await handler.handle_request(request)
    assert response.ok is False
    assert response.error_code == protocol.ERR_CRYPTO_DECRYPT_FAILED


# ---------------------------------------------------------------------------
# Failure: BINANCE_HTTP_ERROR — Binance 4xx/5xx
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_binance_non_2xx_returns_typed_http_error_with_body() -> None:
    """Non-2xx Binance response → BINANCE_HTTP_ERROR with the Binance
    body preserved so caller can inspect the specific Binance error
    code (e.g. -2014 for IP not whitelisted; -2010 for insufficient
    margin)."""
    encrypted_raw, dek = _make_real_encrypted_blob(b"secret")
    blob = _make_blob(encrypted_secret=encrypted_raw)
    fake_kms = MagicMock()
    fake_kms.decrypt.return_value = dek
    kms_client._client = fake_kms

    with patch.object(firestore_keystore, "get_key_blob", return_value=blob), patch.object(
        handler, "_signed_call", new_callable=AsyncMock
    ) as mock_signed:
        mock_signed.return_value = (401, {"code": -2014, "msg": "Invalid API-key"})
        request = protocol.SignRequest(
            id="x",
            verb="binance_signed_get",
            firebase_uid="test-uid",
            path="/fapi/v2/balance",
        )
        response = await handler.handle_request(request)
    assert response.ok is False
    assert response.error_code == protocol.ERR_BINANCE_HTTP_ERROR
    assert response.binance_status == 401
    # Body preserved so caller can switch on Binance error code.
    assert response.binance_body == {"code": -2014, "msg": "Invalid API-key"}


# ---------------------------------------------------------------------------
# Failure: BINANCE_UNREACHABLE — network
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_network_error_returns_unreachable_typed_code() -> None:
    encrypted_raw, dek = _make_real_encrypted_blob(b"secret")
    blob = _make_blob(encrypted_secret=encrypted_raw)
    fake_kms = MagicMock()
    fake_kms.decrypt.return_value = dek
    kms_client._client = fake_kms

    with patch.object(firestore_keystore, "get_key_blob", return_value=blob), patch.object(
        handler, "_signed_call", new_callable=AsyncMock
    ) as mock_signed:
        mock_signed.side_effect = handler._BinanceUnreachable(
            "network error calling /fapi/v2/balance"
        )
        request = protocol.SignRequest(
            id="x",
            verb="binance_signed_get",
            firebase_uid="test-uid",
            path="/fapi/v2/balance",
        )
        response = await handler.handle_request(request)
    assert response.ok is False
    assert response.error_code == protocol.ERR_BINANCE_UNREACHABLE


# ---------------------------------------------------------------------------
# Failure: BAD_REQUEST — input validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unknown_verb_returns_bad_request() -> None:
    request = protocol.SignRequest(id="x", verb="hack_the_planet")  # type: ignore[arg-type]
    response = await handler.handle_request(request)
    assert response.error_code == protocol.ERR_BAD_REQUEST


@pytest.mark.asyncio
async def test_missing_firebase_uid_returns_bad_request() -> None:
    request = protocol.SignRequest(
        id="x", verb="binance_signed_get", path="/fapi/v2/balance"
    )  # firebase_uid defaults to ""
    response = await handler.handle_request(request)
    assert response.error_code == protocol.ERR_BAD_REQUEST


@pytest.mark.asyncio
async def test_missing_path_returns_bad_request() -> None:
    request = protocol.SignRequest(
        id="x", verb="binance_signed_get", firebase_uid="uid-1"
    )  # path defaults to ""
    response = await handler.handle_request(request)
    assert response.error_code == protocol.ERR_BAD_REQUEST


@pytest.mark.asyncio
async def test_unknown_base_returns_bad_request() -> None:
    request = protocol.SignRequest(
        id="x",
        verb="binance_signed_get",
        firebase_uid="uid-1",
        path="/anything",
        base="quantum",  # type: ignore[arg-type]
    )
    response = await handler.handle_request(request)
    assert response.error_code == protocol.ERR_BAD_REQUEST


# ---------------------------------------------------------------------------
# Secret-handling property: response NEVER contains plaintext secret/DEK
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_response_serialisation_does_not_leak_secret_or_dek() -> None:
    """The most security-critical test in this file.  Run a happy path
    with a known plaintext secret + DEK; verify neither appears
    ANYWHERE in the serialised SignResponse wire bytes.  Catches a
    regression where the handler accidentally surfaces secret material
    in an error message or response body."""
    plaintext_secret = b"super_secret_string_that_must_not_leak_INTO_RESPONSE_2026"
    encrypted_raw, dek = _make_real_encrypted_blob(plaintext_secret)
    blob = _make_blob(encrypted_secret=encrypted_raw)
    fake_kms = MagicMock()
    fake_kms.decrypt.return_value = dek
    kms_client._client = fake_kms

    with patch.object(firestore_keystore, "get_key_blob", return_value=blob), patch.object(
        handler, "_signed_call", new_callable=AsyncMock
    ) as mock_signed:
        mock_signed.return_value = (200, {"ok": True})
        request = protocol.SignRequest(
            id="leak-canary",
            verb="binance_signed_get",
            firebase_uid="test-uid",
            path="/fapi/v2/balance",
        )
        response = await handler.handle_request(request)

    wire = response.to_json_line()
    assert plaintext_secret not in wire, "PLAINTEXT SECRET LEAKED into response"
    assert dek not in wire, "PLAINTEXT DEK LEAKED into response"
    # Also check the string-form encoding (in case base64 / hex was
    # used somewhere downstream).
    import base64
    assert base64.b64encode(plaintext_secret) not in wire
    assert base64.b64encode(dek) not in wire
    assert plaintext_secret.hex().encode() not in wire
