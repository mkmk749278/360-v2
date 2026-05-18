"""Tests for src.security.firestore_keystore.

The Firestore Admin SDK is mocked — the keystore module is thin
CRUD scaffolding so the tests pin:

* The document path is exactly ``users/{uid}/binance_key/current``
  (security rules will be wired to this exact path; a drift would
  silently bypass them).
* ``put_key_blob`` base64-encodes the encrypted bytes before
  persisting (so the bytes survive Firestore's string field type).
* ``get_key_blob`` round-trips: bytes in → bytes out, identical.
* ``KeyBlobNotFoundError`` is raised when the doc doesn't exist,
  rather than a generic SDK exception or a silent ``None``.
* ``delete_key_blob`` is idempotent (no error on missing doc).
* Init is idempotent and the not-init error path is typed.
"""
from __future__ import annotations

import base64
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.security import firestore_keystore


@pytest.fixture(autouse=True)
def _reset_module_state():
    firestore_keystore.reset_for_test()
    yield
    firestore_keystore.reset_for_test()


def _install_fake_db() -> MagicMock:
    """Inject a mock Firestore client + return the doc-level mock so
    individual tests can pin ``set`` / ``get`` / ``delete`` calls
    against it.

    The Firestore SDK chain we're emulating:
    ``db.collection(...).document(...).collection(...).document(...)``
    returns a *document reference* with ``.set / .get / .update /
    .delete`` methods.  ``_install_fake_db`` builds that chain so the
    keystore module sees a working object."""
    fake_doc = MagicMock(name="doc_ref")
    fake_binance_key_coll = MagicMock()
    fake_binance_key_coll.document.return_value = fake_doc
    fake_user_doc = MagicMock()
    fake_user_doc.collection.return_value = fake_binance_key_coll
    fake_users_coll = MagicMock()
    fake_users_coll.document.return_value = fake_user_doc
    fake_db = MagicMock()
    fake_db.collection.return_value = fake_users_coll
    firestore_keystore._db = fake_db
    return fake_doc


def _capture_doc_path() -> list[str]:
    """Helper — returns the path components passed through the
    chain so tests can assert the exact ``users/{uid}/binance_key/current``
    structure."""
    path: list[str] = []
    fake_doc = MagicMock(name="doc_ref")

    def collection_2(name: str) -> MagicMock:
        path.append(name)
        coll = MagicMock()
        coll.document.side_effect = lambda n: (path.append(n), fake_doc)[1]
        return coll

    def document_1(uid: str) -> MagicMock:
        path.append(uid)
        m = MagicMock()
        m.collection.side_effect = collection_2
        return m

    def collection_1(name: str) -> MagicMock:
        path.append(name)
        coll = MagicMock()
        coll.document.side_effect = document_1
        return coll

    fake_db = MagicMock()
    fake_db.collection.side_effect = collection_1
    firestore_keystore._db = fake_db
    # Trigger the chain via a no-op delete to capture the path.
    firestore_keystore.delete_key_blob("test-uid")
    return path


# ---------------------------------------------------------------------------
# Init lifecycle
# ---------------------------------------------------------------------------


def test_is_initialised_false_before_init() -> None:
    assert firestore_keystore.is_initialised() is False


def test_init_then_is_initialised_true() -> None:
    with patch("google.cloud.firestore.Client") as mock_ctor:
        mock_ctor.return_value = MagicMock()
        firestore_keystore.init_keystore()
        assert firestore_keystore.is_initialised() is True


def test_init_is_idempotent_second_call_does_not_rebuild() -> None:
    with patch("google.cloud.firestore.Client") as mock_ctor:
        mock_ctor.return_value = MagicMock()
        firestore_keystore.init_keystore()
        firestore_keystore.init_keystore()
        assert mock_ctor.call_count == 1


def test_init_with_service_account_path_loads_credentials_from_file() -> None:
    with patch("google.cloud.firestore.Client") as mock_ctor, patch(
        "google.oauth2.service_account.Credentials.from_service_account_file"
    ) as mock_creds_loader:
        mock_creds_loader.return_value = "fake-creds"
        firestore_keystore.init_keystore(service_account_path="/sa.json")
        mock_creds_loader.assert_called_once_with("/sa.json")
        mock_ctor.assert_called_once_with(credentials="fake-creds")


def test_put_before_init_raises_typed_error() -> None:
    """Without init, CRUD calls surface ``FirestoreKeystoreNotInitialisedError``
    rather than an opaque ``AttributeError`` from the ``None`` db."""
    with pytest.raises(firestore_keystore.FirestoreKeystoreNotInitialisedError):
        firestore_keystore.put_key_blob(
            "uid",
            encrypted_secret=b"x",
            encrypted_dek=b"y",
            key_public_id_first8="abcd1234",
            ip_whitelist_ok=True,
            withdraw_disabled_ok=True,
        )


# ---------------------------------------------------------------------------
# Document path
# ---------------------------------------------------------------------------


def test_doc_path_is_users_uid_binance_key_current() -> None:
    """The Firestore security rules we'll wire in PR-3 will pin this
    exact path; any drift here silently bypasses the rules.  Worth a
    test."""
    path = _capture_doc_path()
    assert path == ["users", "test-uid", "binance_key", "current"]


# ---------------------------------------------------------------------------
# put_key_blob
# ---------------------------------------------------------------------------


def test_put_key_blob_base64_encodes_secret_and_dek() -> None:
    fake_doc = _install_fake_db()
    firestore_keystore.put_key_blob(
        "uid-1",
        encrypted_secret=b"\x00\x01\x02\x03",
        encrypted_dek=b"\xff\xfe\xfd",
        key_public_id_first8="abcd1234",
        ip_whitelist_ok=True,
        withdraw_disabled_ok=True,
    )
    fake_doc.set.assert_called_once()
    payload = fake_doc.set.call_args[0][0]
    # Bytes were base64-encoded so Firestore's string field type
    # accepts them losslessly.
    assert payload["encrypted_secret_b64"] == base64.b64encode(b"\x00\x01\x02\x03").decode("ascii")
    assert payload["encrypted_dek_b64"] == base64.b64encode(b"\xff\xfe\xfd").decode("ascii")
    assert payload["key_public_id_first8"] == "abcd1234"
    assert payload["ip_whitelist_ok"] is True
    assert payload["withdraw_disabled_ok"] is True
    assert isinstance(payload["connected_at"], datetime)
    assert isinstance(payload["last_validated_at"], datetime)
    # Timestamps are UTC-aware (Firestore stores them as
    # google.protobuf.Timestamp; passing naive datetimes drifts by
    # local-tz offset).
    assert payload["connected_at"].tzinfo == timezone.utc


# ---------------------------------------------------------------------------
# get_key_blob
# ---------------------------------------------------------------------------


def test_get_key_blob_round_trips_bytes_exactly() -> None:
    """Persist + load — the encrypted bytes must come back identical
    (any base64 / encoding bug would corrupt the AES-GCM blob and
    cause an InvalidTag at decrypt time, far from the bug)."""
    fake_doc = _install_fake_db()
    now = datetime.now(timezone.utc)
    secret_bytes = b"\xde\xad\xbe\xef"
    dek_bytes = b"\xca\xfe\xba\xbe"
    fake_doc.get.return_value = SimpleNamespace(
        exists=True,
        to_dict=lambda: {
            "encrypted_secret_b64": base64.b64encode(secret_bytes).decode("ascii"),
            "encrypted_dek_b64": base64.b64encode(dek_bytes).decode("ascii"),
            "key_public_id_first8": "1234abcd",
            "ip_whitelist_ok": True,
            "withdraw_disabled_ok": True,
            "connected_at": now,
            "last_validated_at": now,
        },
    )
    blob = firestore_keystore.get_key_blob("uid-1")
    assert blob.uid == "uid-1"
    assert blob.encrypted_secret == secret_bytes
    assert blob.encrypted_dek == dek_bytes
    assert blob.key_public_id_first8 == "1234abcd"
    assert blob.ip_whitelist_ok is True
    assert blob.withdraw_disabled_ok is True
    assert blob.connected_at == now
    assert blob.last_validated_at == now


def test_get_key_blob_raises_typed_error_when_missing() -> None:
    """Surface ``KeyBlobNotFoundError`` rather than ``None`` or a generic
    KeyError — callers (e.g. signing service) should treat the
    missing case as "user not connected yet" and respond with a
    specific error, not crash."""
    fake_doc = _install_fake_db()
    fake_doc.get.return_value = SimpleNamespace(exists=False)
    with pytest.raises(firestore_keystore.KeyBlobNotFoundError):
        firestore_keystore.get_key_blob("nobody")


# ---------------------------------------------------------------------------
# delete_key_blob
# ---------------------------------------------------------------------------


def test_delete_key_blob_calls_firestore_delete() -> None:
    fake_doc = _install_fake_db()
    firestore_keystore.delete_key_blob("uid-1")
    fake_doc.delete.assert_called_once_with()


# ---------------------------------------------------------------------------
# update_last_validated
# ---------------------------------------------------------------------------


def test_update_last_validated_writes_timestamp_only() -> None:
    """Drift detector calls this every cycle — it must NOT touch the
    encrypted-secret / encrypted-dek fields (those are the user's
    actual key material).  Verify the update payload is just the
    timestamp."""
    fake_doc = _install_fake_db()
    firestore_keystore.update_last_validated("uid-1")
    fake_doc.update.assert_called_once()
    payload = fake_doc.update.call_args[0][0]
    assert set(payload.keys()) == {"last_validated_at"}
    assert isinstance(payload["last_validated_at"], datetime)
    assert payload["last_validated_at"].tzinfo == timezone.utc
