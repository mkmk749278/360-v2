"""Tests for src.security.kms_client.

The GCP KMS SDK is mocked end-to-end — we never reach Google's
service in tests.  What we pin here:

* :class:`KmsKeyRef` builds the GCP-canonical resource name string
  that the SDK expects.
* :class:`KmsClient.encrypt` / ``.decrypt`` pass the correct
  ``name`` + ``plaintext`` / ``ciphertext`` to the SDK and return
  the response bytes.
* Init is idempotent: a second ``init_kms_client`` call doesn't
  rebuild the GCP client (no double-import, no leaked credentials).
* :func:`get_client` raises a clear, typed error before init.
* :func:`is_initialised` reports the state correctly across init
  and reset.
* ``reset_for_test`` truly drops the singleton (without this,
  cross-test contamination from a stub client would silently let
  subsequent tests "pass" even with broken init).
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.security import kms_client


@pytest.fixture(autouse=True)
def _reset_kms_module_state():
    """Each test starts from ``is_initialised() == False``."""
    kms_client.reset_for_test()
    yield
    kms_client.reset_for_test()


# ---------------------------------------------------------------------------
# KmsKeyRef
# ---------------------------------------------------------------------------


def test_key_ref_resource_name_format() -> None:
    """Pinning the exact GCP resource-name format — the SDK rejects
    any deviation, so it's worth a unit test rather than discovering
    it only at the first real ``encrypt`` call."""
    ref = kms_client.KmsKeyRef(
        project_id="lumin-prod-123",
        location="us-central1",
        keyring="binance-keys",
        key_name="user-secret-kek",
    )
    assert ref.resource_name == (
        "projects/lumin-prod-123/locations/us-central1/"
        "keyRings/binance-keys/cryptoKeys/user-secret-kek"
    )


# ---------------------------------------------------------------------------
# KmsClient — encrypt / decrypt
# ---------------------------------------------------------------------------


def _make_client_with_stub_gcp() -> tuple[kms_client.KmsClient, MagicMock]:
    """Build a KmsClient wrapping a mock GCP client.  Used by every
    encrypt/decrypt test to avoid duplicating the boilerplate."""
    gcp = MagicMock()
    ref = kms_client.KmsKeyRef(
        project_id="p", location="loc", keyring="kr", key_name="k"
    )
    return kms_client.KmsClient(key_ref=ref, client=gcp), gcp


def test_encrypt_calls_gcp_with_correct_name_and_plaintext() -> None:
    client, gcp = _make_client_with_stub_gcp()
    gcp.encrypt.return_value = SimpleNamespace(ciphertext=b"\xaa\xbb\xcc")
    result = client.encrypt(b"plaintext-dek-bytes")
    assert result == b"\xaa\xbb\xcc"
    gcp.encrypt.assert_called_once_with(
        request={
            "name": "projects/p/locations/loc/keyRings/kr/cryptoKeys/k",
            "plaintext": b"plaintext-dek-bytes",
        }
    )


def test_decrypt_calls_gcp_with_correct_name_and_ciphertext() -> None:
    client, gcp = _make_client_with_stub_gcp()
    gcp.decrypt.return_value = SimpleNamespace(plaintext=b"recovered-dek")
    result = client.decrypt(b"opaque-kms-ciphertext")
    assert result == b"recovered-dek"
    gcp.decrypt.assert_called_once_with(
        request={
            "name": "projects/p/locations/loc/keyRings/kr/cryptoKeys/k",
            "ciphertext": b"opaque-kms-ciphertext",
        }
    )


def test_encrypt_returns_bytes_even_when_gcp_returns_bytestring_subtype() -> None:
    """Some grpc protobuf responses return a custom bytestring type;
    we want callers to always see plain ``bytes`` so downstream
    base64 codecs don't trip on the subtype."""
    client, gcp = _make_client_with_stub_gcp()
    gcp.encrypt.return_value = SimpleNamespace(ciphertext=bytearray(b"abc"))
    result = client.encrypt(b"x")
    assert isinstance(result, bytes)
    assert result == b"abc"


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------


def test_is_initialised_false_before_init() -> None:
    assert kms_client.is_initialised() is False


def test_get_client_raises_before_init() -> None:
    """The signing service calls ``get_client`` on every order; this
    typed error makes the failure mode obvious in tracebacks."""
    with pytest.raises(kms_client.KmsNotInitialisedError):
        kms_client.get_client()


def test_init_then_get_client_returns_singleton() -> None:
    """After init, ``get_client`` returns the registered instance —
    and successive calls return the SAME instance (no rebuilding
    of the GCP client per call)."""
    with patch("google.cloud.kms_v1.KeyManagementServiceClient") as mock_ctor:
        mock_ctor.return_value = MagicMock()
        kms_client.init_kms_client(
            project_id="p",
            location="loc",
            keyring="kr",
            key_name="k",
        )
        assert kms_client.is_initialised() is True
        first = kms_client.get_client()
        second = kms_client.get_client()
        assert first is second
        assert first.key_ref.resource_name == (
            "projects/p/locations/loc/keyRings/kr/cryptoKeys/k"
        )


def test_init_is_idempotent_second_call_does_not_rebuild() -> None:
    """A second init call must not rebuild the GCP client (it would
    leak the previous credentials and double the auth load).  Verify
    by counting constructor invocations."""
    with patch("google.cloud.kms_v1.KeyManagementServiceClient") as mock_ctor:
        mock_ctor.return_value = MagicMock()
        kms_client.init_kms_client(
            project_id="p", location="loc", keyring="kr", key_name="k"
        )
        kms_client.init_kms_client(
            project_id="p", location="loc", keyring="kr", key_name="k"
        )
        assert mock_ctor.call_count == 1


def test_init_with_service_account_path_loads_credentials_from_file() -> None:
    """When an explicit service-account path is provided, the GCP
    client is built with those credentials rather than ADC.  This
    mirrors the Firebase Admin init pattern."""
    with patch("google.cloud.kms_v1.KeyManagementServiceClient") as mock_ctor, patch(
        "google.oauth2.service_account.Credentials.from_service_account_file"
    ) as mock_creds_loader:
        mock_creds_loader.return_value = "fake-credentials-object"
        kms_client.init_kms_client(
            project_id="p",
            location="loc",
            keyring="kr",
            key_name="k",
            service_account_path="/path/to/sa.json",
        )
        mock_creds_loader.assert_called_once_with("/path/to/sa.json")
        mock_ctor.assert_called_once_with(credentials="fake-credentials-object")


def test_init_without_service_account_path_falls_back_to_adc() -> None:
    """When the path arg is omitted, the GCP client is built with no
    explicit credentials and uses Application Default Credentials.
    This is the production path on the engine VPS where the JSON
    is on disk and ``GOOGLE_APPLICATION_CREDENTIALS`` is set."""
    with patch("google.cloud.kms_v1.KeyManagementServiceClient") as mock_ctor, patch(
        "google.oauth2.service_account.Credentials.from_service_account_file"
    ) as mock_creds_loader:
        kms_client.init_kms_client(
            project_id="p", location="loc", keyring="kr", key_name="k"
        )
        mock_creds_loader.assert_not_called()
        # Called with no credentials arg — ADC discovery.
        mock_ctor.assert_called_once_with()


def test_reset_for_test_drops_singleton() -> None:
    with patch("google.cloud.kms_v1.KeyManagementServiceClient") as mock_ctor:
        mock_ctor.return_value = MagicMock()
        kms_client.init_kms_client(
            project_id="p", location="loc", keyring="kr", key_name="k"
        )
        assert kms_client.is_initialised() is True
        kms_client.reset_for_test()
        assert kms_client.is_initialised() is False
        with pytest.raises(kms_client.KmsNotInitialisedError):
            kms_client.get_client()
