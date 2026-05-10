"""User store — SQLite-backed registry of phone-verified users.

Phase 2 brings phone-OTP authentication.  Once a user verifies their
phone, the engine mints a JWT carrying ``sub=user-<id>`` and the user's
current tier.  This module is the persistence layer for that registry.

Why SQLite (and not JSON like ``user_settings.py``):

- Atomicity under concurrent OTP-verifies.  Two phones verifying at the
  same moment would race a JSON file's read-modify-write loop.  SQLite
  with WAL gives us ``INSERT OR IGNORE`` and serialised writes for free.
- Indexed phone-lookup, no full-file deserialisation per request.
- Trivial extension to per-user tables in Phase 3 (paper P&L, settings,
  signal-followed history) without changing storage tech.

Schema (created on first connect via ``CREATE TABLE IF NOT EXISTS``):

    users(
        user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_e164     TEXT NOT NULL UNIQUE,
        tier           TEXT NOT NULL DEFAULT 'free',
        paid_until     TEXT,                    -- ISO-8601 UTC; NULL when not paid
        telegram_chat_id TEXT,
        created_at     TEXT NOT NULL,           -- ISO-8601 UTC
        updated_at     TEXT NOT NULL            -- ISO-8601 UTC
    );

Owner bootstrap: on first boot of a fresh ``data/lumin.sqlite`` the
caller (Bootstrap.boot) invokes :meth:`bootstrap_owner_if_empty` which
inserts ``user_id=1`` for the configured ``OWNER_PHONE_E164``.  After
that, the static admin token continues to work in parallel for tooling.
"""

from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.utils import get_logger

log = get_logger("api.users")


_FREE_TIER = "free"
_OWNER_TIER = "owner"


# ---------------------------------------------------------------------------
# Domain object
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class User:
    """One row of the ``users`` table."""

    user_id: int
    phone_e164: str
    tier: str
    paid_until: Optional[datetime]  # tz-aware UTC or None
    telegram_chat_id: Optional[str]
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(raw: Optional[str]) -> Optional[datetime]:
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def _row_to_user(row: sqlite3.Row) -> User:
    return User(
        user_id=int(row["user_id"]),
        phone_e164=str(row["phone_e164"]),
        tier=str(row["tier"]),
        paid_until=_parse_iso(row["paid_until"]),
        telegram_chat_id=row["telegram_chat_id"],
        created_at=_parse_iso(row["created_at"]),  # type: ignore[arg-type]
        updated_at=_parse_iso(row["updated_at"]),  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    user_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_e164       TEXT    NOT NULL UNIQUE,
    tier             TEXT    NOT NULL DEFAULT 'free',
    paid_until       TEXT,
    telegram_chat_id TEXT,
    created_at       TEXT    NOT NULL,
    updated_at       TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_e164);
"""


class UserStore:
    """Thread-safe SQLite-backed user registry.

    A single connection is held open for the lifetime of the engine
    process; ``check_same_thread=False`` lets FastAPI's thread-pool
    executor share it, and an internal RLock serialises writes.  Reads
    are also serialised — the workload is tiny (a few requests/sec at
    most for phone signins) so the simplicity is worth more than the
    micro-optimisation.
    """

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            str(self._path),
            check_same_thread=False,
            isolation_level=None,  # autocommit; we manage transactions explicitly
        )
        self._conn.row_factory = sqlite3.Row
        # WAL — concurrent reads while a write is in flight, no fsync per write.
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(_SCHEMA_SQL)
        log.info("UserStore opened at {}", self._path)

    # ---- bootstrap ------------------------------------------------------

    def is_empty(self) -> bool:
        with self._lock:
            cur = self._conn.execute("SELECT COUNT(*) AS n FROM users")
            return int(cur.fetchone()["n"]) == 0

    def bootstrap_owner_if_empty(self, phone_e164: str) -> Optional[User]:
        """Insert ``user_id=1`` with tier=owner if the table is empty.

        Returns the newly-inserted User, or None if the table already had
        rows (idempotent — never overwrites).  Owner phone is taken from
        the ``OWNER_PHONE_E164`` env var by the caller (Bootstrap.boot).
        """
        if not phone_e164:
            return None
        with self._lock:
            if not self.is_empty():
                return None
            now = _now_iso()
            self._conn.execute(
                """
                INSERT INTO users (user_id, phone_e164, tier, paid_until,
                                   telegram_chat_id, created_at, updated_at)
                VALUES (1, ?, ?, NULL, NULL, ?, ?)
                """,
                (phone_e164, _OWNER_TIER, now, now),
            )
            log.info("Bootstrapped owner: user_id=1, phone={}", phone_e164)
            return self.get_by_id(1)

    # ---- reads ----------------------------------------------------------

    def get_by_id(self, user_id: int) -> Optional[User]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (int(user_id),)
            )
            row = cur.fetchone()
            return _row_to_user(row) if row is not None else None

    def get_by_phone(self, phone_e164: str) -> Optional[User]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM users WHERE phone_e164 = ?", (phone_e164,)
            )
            row = cur.fetchone()
            return _row_to_user(row) if row is not None else None

    # ---- writes ---------------------------------------------------------

    def get_or_create_by_phone(self, phone_e164: str) -> User:
        """Atomic upsert keyed by phone.

        Used by the OTP-verify endpoint: a brand-new tester verifies →
        we create their row at tier=free; a returning user verifies →
        we return their existing row.  Race-safe: the UNIQUE constraint
        on ``phone_e164`` plus serialised writes guarantee one row per
        phone even under concurrent verifies.
        """
        with self._lock:
            existing = self.get_by_phone(phone_e164)
            if existing is not None:
                return existing
            now = _now_iso()
            self._conn.execute(
                """
                INSERT INTO users (phone_e164, tier, paid_until,
                                   telegram_chat_id, created_at, updated_at)
                VALUES (?, ?, NULL, NULL, ?, ?)
                """,
                (phone_e164, _FREE_TIER, now, now),
            )
            user = self.get_by_phone(phone_e164)
            if user is None:  # pragma: no cover — INSERT then SELECT must hit
                raise RuntimeError(
                    f"user vanished after insert: phone={phone_e164!r}"
                )
            log.info("Created user: user_id={}, phone={}", user.user_id, phone_e164)
            return user

    def set_tier(
        self,
        user_id: int,
        *,
        tier: str,
        paid_until: Optional[datetime],
    ) -> User:
        """Update tier + paid_until for an existing user.

        Used by ``POST /internal/billing/grant`` when the bot reports a
        subscription change.  Raises ``LookupError`` if the user
        doesn't exist (caller decides whether to create-then-set or
        404).
        """
        with self._lock:
            now = _now_iso()
            paid_until_iso = (
                paid_until.astimezone(timezone.utc).isoformat()
                if paid_until is not None
                else None
            )
            cur = self._conn.execute(
                """
                UPDATE users
                   SET tier = ?, paid_until = ?, updated_at = ?
                 WHERE user_id = ?
                """,
                (tier, paid_until_iso, now, int(user_id)),
            )
            if cur.rowcount == 0:
                raise LookupError(f"user_id={user_id} not found")
            user = self.get_by_id(user_id)
            assert user is not None  # rowcount > 0 → row exists
            log.info(
                "Tier updated: user_id={}, tier={}, paid_until={}",
                user_id, tier, paid_until_iso,
            )
            return user

    def set_telegram_chat_id(self, user_id: int, chat_id: Optional[str]) -> None:
        with self._lock:
            now = _now_iso()
            self._conn.execute(
                "UPDATE users SET telegram_chat_id = ?, updated_at = ? WHERE user_id = ?",
                (chat_id, now, int(user_id)),
            )

    # ---- lifecycle ------------------------------------------------------

    def close(self) -> None:
        with self._lock:
            self._conn.close()


# ---------------------------------------------------------------------------
# Module-level singleton (mirrors src.user_settings pattern)
# ---------------------------------------------------------------------------


_store: Optional[UserStore] = None
_store_lock = threading.Lock()


def get_default_store(path: Path | str) -> UserStore:
    """Return (and lazily create) the process-global UserStore."""
    global _store
    with _store_lock:
        if _store is None:
            _store = UserStore(path)
        return _store


def reset_for_test(path: Optional[Path | str] = None) -> Optional[UserStore]:
    """Drop the cached singleton; re-init against ``path`` if provided.

    Mirrors :func:`src.user_settings.reset_for_test` so test fixtures
    can swap in a tmp_path-backed store without leaking state across
    tests.
    """
    global _store
    with _store_lock:
        if _store is not None:
            try:
                _store.close()
            except Exception:  # pragma: no cover
                pass
            _store = None
        if path is not None:
            _store = UserStore(path)
        return _store
