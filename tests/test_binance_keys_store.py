"""Tests for the per-user Binance key store (AESGCM-encrypted at rest)."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.auto_trade.binance_keys_store import (
    BinanceKeysStore,
    BinanceKeysStoreError,
)


@pytest.fixture
def store(tmp_path: Path) -> BinanceKeysStore:
    """Fresh store backed by a per-test SQLite file."""
    db = tmp_path / "lumin.sqlite"
    # users(user_id, ...) is the FK target.  For these unit tests we
    # disable foreign keys so we don't need to bootstrap a users row
    # — the FK clause is still in the schema for production safety.
    # SQLite FK enforcement is per-connection so the store's own
    # connection has PRAGMA foreign_keys=ON, but inserts won't fail
    # in tests because no users row is referenced by anything else.
    s = BinanceKeysStore(str(db), encryption_secret="unit-test-secret-32-chars-aaaaaaaa")
    # Drop the FK constraint on the bare test schema by recreating
    # the table without it — keeps unit tests pure (no users-table seed).
    s._conn.execute("DROP TABLE user_binance_keys")
    s._conn.execute(
        """
        CREATE TABLE user_binance_keys (
            user_id           INTEGER PRIMARY KEY,
            api_key_enc       BLOB NOT NULL,
            api_secret_enc    BLOB NOT NULL,
            testnet           INTEGER NOT NULL DEFAULT 0,
            last_verified_at  TEXT,
            last_used_at      TEXT,
            created_at        TEXT NOT NULL,
            updated_at        TEXT NOT NULL
        )
        """
    )
    return s


class TestEncryptionSecret:
    def test_missing_secret_refuses_to_start(self, tmp_path: Path):
        with pytest.raises(BinanceKeysStoreError, match="encryption secret"):
            BinanceKeysStore(str(tmp_path / "x.sqlite"), encryption_secret="")


class TestSetGet:
    def test_set_then_get_round_trips_plaintext(self, store: BinanceKeysStore):
        store.set(42, "key-abc", "secret-xyz", testnet=False)
        keys = store.get(42)
        assert keys is not None
        assert keys.user_id == 42
        assert keys.api_key == "key-abc"
        assert keys.api_secret == "secret-xyz"
        assert keys.testnet is False
        assert keys.last_verified_at is None
        assert keys.last_used_at is None

    def test_get_missing_user_returns_none(self, store: BinanceKeysStore):
        assert store.get(999) is None

    def test_testnet_flag_persists(self, store: BinanceKeysStore):
        store.set(1, "k", "s", testnet=True)
        keys = store.get(1)
        assert keys is not None and keys.testnet is True

    def test_set_rejects_empty_inputs(self, store: BinanceKeysStore):
        with pytest.raises(BinanceKeysStoreError, match="required"):
            store.set(1, "", "secret")
        with pytest.raises(BinanceKeysStoreError, match="required"):
            store.set(1, "key", "")

    def test_upsert_overwrites_existing(self, store: BinanceKeysStore):
        store.set(1, "old-key", "old-secret")
        store.set(1, "new-key", "new-secret")
        keys = store.get(1)
        assert keys is not None
        assert keys.api_key == "new-key"
        assert keys.api_secret == "new-secret"


class TestEncryptionAtRest:
    def test_stored_blob_is_not_plaintext(self, store: BinanceKeysStore):
        store.set(7, "PLAINTEXT-KEY", "PLAINTEXT-SECRET")
        row = store._conn.execute(
            "SELECT api_key_enc, api_secret_enc FROM user_binance_keys WHERE user_id = 7"
        ).fetchone()
        assert row is not None
        assert b"PLAINTEXT-KEY" not in row["api_key_enc"]
        assert b"PLAINTEXT-SECRET" not in row["api_secret_enc"]
        # AESGCM ciphertext is at minimum nonce(12) + tag(16) + len(pt) bytes.
        # Our payloads are 13 bytes plaintext, so ≥ 41 bytes total.
        assert len(row["api_key_enc"]) >= 12 + 16 + len("PLAINTEXT-KEY")

    def test_aad_binds_ciphertext_to_user_id(self, store: BinanceKeysStore):
        """Swapping a ciphertext blob between two user rows must fail
        the AESGCM auth tag — proves the per-user AAD is enforced."""
        store.set(1, "alice-key", "alice-secret")
        store.set(2, "bob-key", "bob-secret")
        # Manually swap Alice's ciphertext into Bob's row.  Bypass the
        # public API to construct the corrupted state.
        alice_row = store._conn.execute(
            "SELECT api_key_enc FROM user_binance_keys WHERE user_id = 1"
        ).fetchone()
        store._conn.execute(
            "UPDATE user_binance_keys SET api_key_enc = ? WHERE user_id = 2",
            (alice_row["api_key_enc"],),
        )
        with pytest.raises(BinanceKeysStoreError, match="tag invalid"):
            store.get(2)

    def test_wrong_master_key_fails_decrypt(self, tmp_path: Path):
        """Rotating the encryption secret renders all stored rows
        un-decryptable — caller (app) sees an error and re-prompts."""
        db = str(tmp_path / "z.sqlite")
        s1 = BinanceKeysStore(db, encryption_secret="secret-A" * 4)
        s1._conn.execute("DROP TABLE user_binance_keys")
        s1._conn.execute(
            """
            CREATE TABLE user_binance_keys (
                user_id INTEGER PRIMARY KEY,
                api_key_enc BLOB NOT NULL,
                api_secret_enc BLOB NOT NULL,
                testnet INTEGER NOT NULL DEFAULT 0,
                last_verified_at TEXT, last_used_at TEXT,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            )
            """
        )
        s1.set(1, "k", "s")
        s1.close()
        # Re-open with a different secret.
        s2 = BinanceKeysStore(db, encryption_secret="secret-B" * 4)
        with pytest.raises(BinanceKeysStoreError):
            s2.get(1)


class TestLifecycle:
    def test_has_does_not_decrypt(self, store: BinanceKeysStore):
        store.set(1, "k", "s")
        assert store.has(1) is True
        assert store.has(2) is False

    def test_clear_removes_row(self, store: BinanceKeysStore):
        store.set(1, "k", "s")
        assert store.clear(1) is True
        assert store.get(1) is None
        assert store.clear(1) is False  # idempotent

    def test_mark_verified_stamps_timestamp(self, store: BinanceKeysStore):
        store.set(1, "k", "s")
        assert store.get(1).last_verified_at is None  # type: ignore[union-attr]
        store.mark_verified(1)
        keys = store.get(1)
        assert keys is not None and keys.last_verified_at is not None

    def test_set_clears_verified_timestamp(self, store: BinanceKeysStore):
        """Re-uploading keys must invalidate the prior verify so the
        app shows 'Verify needed' until the next ``/keys/verify``."""
        store.set(1, "k", "s")
        store.mark_verified(1)
        assert store.get(1).last_verified_at is not None  # type: ignore[union-attr]
        store.set(1, "k2", "s2")
        assert store.get(1).last_verified_at is None  # type: ignore[union-attr]

    def test_status_never_returns_secret_material(self, store: BinanceKeysStore):
        store.set(1, "very-secret-key", "very-secret-secret", testnet=True)
        info = store.status(1)
        assert info is not None
        # Status must expose presence + timestamps, NOTHING else.
        assert "api_key" not in info
        assert "api_secret" not in info
        assert info["stored"] is True
        assert info["testnet"] is True

    def test_status_missing_user(self, store: BinanceKeysStore):
        assert store.status(99) is None
