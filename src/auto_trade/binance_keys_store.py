"""Per-user Binance API key store — VPS-side encrypted persistence.

Each Lumin user keeps their Binance Futures API keys on the VPS so that
all signed Binance calls go out from the VPS's IP-allowlisted address
(``194.163.141.135``).  The phone never calls ``fapi.binance.com``
directly — cellular IP rotation would break the allowlist on every
tower change, and Binance auto-deletes Futures-enabled keys without
an IP restriction.

Threat model
------------

The VPS is a single-tenant operator-owned server with the engine
process as the only trusted reader.  Keys are stored encrypted at
rest so a one-shot DB exfil (e.g. accidental backup leak) doesn't
expose plaintext secrets.  Decryption happens in-process per request
and is never persisted to disk or logs.

Encryption
----------

AES-128-GCM (NIST SP 800-38D).  The master key is derived from the
``BINANCE_KEY_ENCRYPTION_SECRET`` env var via SHA-256 → first 16 bytes
of digest.  Per-record: random 12-byte nonce, additional authenticated
data (AAD) = user_id encoded big-endian — this binds the ciphertext
to the row so swapping rows between users invalidates the tag.

Layout of the stored ``api_key_enc`` / ``api_secret_enc`` BLOBs:

    nonce(12 bytes) || ciphertext+tag(16+N bytes)

Schema
------

::

    user_binance_keys(
        user_id           INTEGER PRIMARY KEY,
        api_key_enc       BLOB NOT NULL,
        api_secret_enc    BLOB NOT NULL,
        testnet           INTEGER NOT NULL DEFAULT 0,
        last_verified_at  TEXT,                -- ISO-8601 UTC
        last_used_at      TEXT,                -- ISO-8601 UTC
        created_at        TEXT NOT NULL,
        updated_at        TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
"""

from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.utils import get_logger

log = get_logger("api.binance_keys")


_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_binance_keys (
    user_id           INTEGER PRIMARY KEY,
    api_key_enc       BLOB NOT NULL,
    api_secret_enc    BLOB NOT NULL,
    testnet           INTEGER NOT NULL DEFAULT 0,
    last_verified_at  TEXT,
    last_used_at      TEXT,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@dataclass(frozen=True)
class BinanceKeys:
    """Decrypted per-user Binance credentials returned by :meth:`BinanceKeysStore.get`."""

    user_id: int
    api_key: str
    api_secret: str
    testnet: bool
    last_verified_at: Optional[datetime]
    last_used_at: Optional[datetime]


class BinanceKeysStoreError(Exception):
    """Raised when encryption setup is invalid or a stored row can't be decrypted."""


class BinanceKeysStore:
    """SQLite-backed encrypted store for per-user Binance API keys."""

    def __init__(self, db_path: str, encryption_secret: str) -> None:
        if not encryption_secret:
            raise BinanceKeysStoreError(
                "BINANCE_KEY_ENCRYPTION_SECRET is not set — refusing to start "
                "the per-user key store without an encryption secret"
            )
        # Derive a stable 16-byte AES-128 key from the secret.  SHA-256 →
        # take the first half; the second half is reserved for future
        # rotation (KDF version 2 could XOR-derive a different subkey).
        self._aes_key = hashlib.sha256(encryption_secret.encode("utf-8")).digest()[:16]
        self._cipher = AESGCM(self._aes_key)

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False, isolation_level=None)
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock:
            self._conn.executescript(_SCHEMA)

    # ------------------------------------------------------------------
    # Encryption helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _aad(user_id: int) -> bytes:
        """Per-user AAD binds ciphertext to the row — swapping rows fails the auth tag."""
        return user_id.to_bytes(8, "big", signed=False)

    def _encrypt(self, plaintext: str, user_id: int) -> bytes:
        nonce = secrets.token_bytes(12)
        ct = self._cipher.encrypt(nonce, plaintext.encode("utf-8"), self._aad(user_id))
        return nonce + ct

    def _decrypt(self, blob: bytes, user_id: int) -> str:
        if len(blob) < 12 + 16:
            raise BinanceKeysStoreError("stored blob too short to be a valid AESGCM payload")
        nonce, ct = blob[:12], blob[12:]
        try:
            pt = self._cipher.decrypt(nonce, ct, self._aad(user_id))
        except InvalidTag as exc:
            raise BinanceKeysStoreError(
                f"AESGCM tag invalid for user {user_id} — wrong key or tampered row"
            ) from exc
        return pt.decode("utf-8")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set(
        self,
        user_id: int,
        api_key: str,
        api_secret: str,
        *,
        testnet: bool = False,
    ) -> None:
        """Upsert encrypted credentials for ``user_id``.

        Resets ``last_verified_at`` / ``last_used_at`` so the verify
        flag must be re-set explicitly after the next successful Binance
        call (e.g. an inline ``/fapi/v2/account`` probe).
        """
        if not api_key or not api_secret:
            raise BinanceKeysStoreError("api_key and api_secret are both required")
        api_key_enc = self._encrypt(api_key, user_id)
        api_secret_enc = self._encrypt(api_secret, user_id)
        now = _now_iso()
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO user_binance_keys
                    (user_id, api_key_enc, api_secret_enc, testnet,
                     last_verified_at, last_used_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, NULL, NULL, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    api_key_enc      = excluded.api_key_enc,
                    api_secret_enc   = excluded.api_secret_enc,
                    testnet          = excluded.testnet,
                    last_verified_at = NULL,
                    last_used_at     = NULL,
                    updated_at       = excluded.updated_at
                """,
                (user_id, api_key_enc, api_secret_enc, 1 if testnet else 0, now, now),
            )

    def get(self, user_id: int) -> Optional[BinanceKeys]:
        """Return decrypted ``BinanceKeys`` for ``user_id``, or ``None`` if not set."""
        with self._lock:
            row = self._conn.execute(
                """
                SELECT user_id, api_key_enc, api_secret_enc, testnet,
                       last_verified_at, last_used_at
                  FROM user_binance_keys
                 WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return BinanceKeys(
            user_id=int(row["user_id"]),
            api_key=self._decrypt(row["api_key_enc"], user_id),
            api_secret=self._decrypt(row["api_secret_enc"], user_id),
            testnet=bool(row["testnet"]),
            last_verified_at=_parse_iso(row["last_verified_at"]),
            last_used_at=_parse_iso(row["last_used_at"]),
        )

    def has(self, user_id: int) -> bool:
        """Cheap existence check that does NOT decrypt anything."""
        with self._lock:
            row = self._conn.execute(
                "SELECT 1 FROM user_binance_keys WHERE user_id = ? LIMIT 1",
                (user_id,),
            ).fetchone()
        return row is not None

    def clear(self, user_id: int) -> bool:
        """Delete the row for ``user_id``.  Returns True if a row was removed."""
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM user_binance_keys WHERE user_id = ?",
                (user_id,),
            )
            return cur.rowcount > 0

    def mark_verified(self, user_id: int) -> None:
        """Stamp ``last_verified_at`` to now.  Call after a successful
        ``/fapi/v2/account`` probe so the "Verified Xm ago" indicator
        on the app drives off ground truth."""
        now = _now_iso()
        with self._lock:
            self._conn.execute(
                "UPDATE user_binance_keys SET last_verified_at = ?, updated_at = ? WHERE user_id = ?",
                (now, now, user_id),
            )

    def mark_used(self, user_id: int) -> None:
        """Stamp ``last_used_at`` to now.  Called after every successful
        Binance proxy call so observability can show key activity."""
        now = _now_iso()
        with self._lock:
            self._conn.execute(
                "UPDATE user_binance_keys SET last_used_at = ?, updated_at = ? WHERE user_id = ?",
                (now, now, user_id),
            )

    # ------------------------------------------------------------------
    # Diagnostic helpers (non-secret)
    # ------------------------------------------------------------------

    def status(self, user_id: int) -> Optional[dict]:
        """Return non-secret status (presence flags + timestamps) for
        the app's API-keys settings page.  Returns ``None`` when no
        row exists.  Never returns key material."""
        with self._lock:
            row = self._conn.execute(
                """
                SELECT testnet, last_verified_at, last_used_at, created_at, updated_at
                  FROM user_binance_keys WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "stored": True,
            "testnet": bool(row["testnet"]),
            "last_verified_at": row["last_verified_at"],
            "last_used_at": row["last_used_at"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def close(self) -> None:
        with self._lock:
            self._conn.close()


# ---------------------------------------------------------------------------
# Helper: resolve encryption secret from env with deterministic fallback
# for unit tests.  The env var is mandatory in production — the bootstrap
# refuses to start without it set to a non-empty value.
# ---------------------------------------------------------------------------


def resolve_encryption_secret() -> str:
    """Read ``BINANCE_KEY_ENCRYPTION_SECRET`` from env.  Empty → empty
    return (caller decides whether to fail-closed or fail-open)."""
    return os.getenv("BINANCE_KEY_ENCRYPTION_SECRET", "")
