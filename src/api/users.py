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
        user_id            INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_e164         TEXT NOT NULL UNIQUE,
        tier               TEXT NOT NULL DEFAULT 'free',
        paid_until         TEXT,                -- ISO-8601 UTC; NULL when not paid
        telegram_chat_id   TEXT,
        -- Profile (Phase 3 — per-user expansion).  All NULL on a fresh
        -- post-OTP row; the app routes to its SignupPage to collect them
        -- and then PUTs /api/profile to mark ``onboarded_at``.  Owner is
        -- pre-onboarded by :meth:`bootstrap_owner_if_empty`.
        display_name       TEXT,
        country_code       TEXT,                -- ISO 3166-1 alpha-2
        timezone           TEXT,                -- IANA tz database name
        currency           TEXT,                -- ISO 4217 ("USD")
        terms_accepted_at  TEXT,                -- ISO-8601 UTC
        onboarded_at       TEXT,                -- NULL = needs signup flow
        firebase_uid       TEXT,                -- Phase 4 Firebase migration; UNIQUE when set
        created_at         TEXT NOT NULL,       -- ISO-8601 UTC
        updated_at         TEXT NOT NULL        -- ISO-8601 UTC
    );

Owner bootstrap: on first boot of a fresh ``data/lumin.sqlite`` the
caller (Bootstrap.boot) invokes :meth:`bootstrap_owner_if_empty` which
inserts ``user_id=1`` for the configured ``OWNER_PHONE_E164``.  After
that, the static admin token continues to work in parallel for tooling.

Migration: pre-Phase-3 deployments have a ``users`` table without the
profile columns.  :meth:`_migrate_schema` adds them in-place via
``ALTER TABLE ... ADD COLUMN`` (SQLite-safe, in-place, no row rewrite).
Existing rows get NULL for every profile column → they're routed back
through the SignupPage on next login.  Phase-4 ``firebase_uid`` follows
the same pattern — added via ``ALTER TABLE`` for existing dbs, populated
on first Firebase sign-in by phone-match-and-backfill (see
:meth:`get_or_create_by_firebase_uid`).
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
    # Profile fields (Phase 3).  All NULL on a freshly-created post-OTP
    # row; populated by ``PUT /api/profile`` from the app's SignupPage.
    display_name: Optional[str] = None
    country_code: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    terms_accepted_at: Optional[datetime] = None
    onboarded_at: Optional[datetime] = None
    # Firebase identity (Phase 4).  NULL on legacy / unmigrated rows;
    # populated either on first Firebase sign-in (via phone-match
    # backfill in ``get_or_create_by_firebase_uid``) or by the
    # Telegram-OTP-verify endpoint after registering the user with
    # Firebase Admin and calling ``set_firebase_uid``.
    firebase_uid: Optional[str] = None

    @property
    def needs_onboarding(self) -> bool:
        """True when the SignupPage hasn't completed for this user yet.

        The app routes to SignupPage iff this is True.  Owner bootstrap
        sets ``onboarded_at`` so the operator never sees the signup
        flow.
        """
        return self.onboarded_at is None


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
    # Tolerate pre-migration rows (Phase-2 dbs) by looking up the profile
    # columns defensively — sqlite3.Row raises IndexError for unknown
    # keys but tests open fresh tmp-path stores so this rarely fires in
    # practice.  The defensive ``in row.keys()`` guard keeps the prod
    # migration path safe.
    keys = set(row.keys())
    def _get(name: str):
        return row[name] if name in keys else None
    return User(
        user_id=int(row["user_id"]),
        phone_e164=str(row["phone_e164"]),
        tier=str(row["tier"]),
        paid_until=_parse_iso(row["paid_until"]),
        telegram_chat_id=row["telegram_chat_id"],
        created_at=_parse_iso(row["created_at"]),  # type: ignore[arg-type]
        updated_at=_parse_iso(row["updated_at"]),  # type: ignore[arg-type]
        display_name=_get("display_name"),
        country_code=_get("country_code"),
        timezone=_get("timezone"),
        currency=_get("currency"),
        terms_accepted_at=_parse_iso(_get("terms_accepted_at")),
        onboarded_at=_parse_iso(_get("onboarded_at")),
        firebase_uid=_get("firebase_uid"),
    )


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------


# NB: The partial unique index on ``firebase_uid`` is INTENTIONALLY
# omitted from this script — it's created inside ``_migrate_schema``
# below, AFTER the column ADD step runs, so it works on pre-Phase-4
# dbs where the column doesn't yet exist when ``executescript`` runs.
_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    user_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_e164        TEXT    NOT NULL UNIQUE,
    tier              TEXT    NOT NULL DEFAULT 'free',
    paid_until        TEXT,
    telegram_chat_id  TEXT,
    display_name      TEXT,
    country_code      TEXT,
    timezone          TEXT,
    currency          TEXT,
    terms_accepted_at TEXT,
    onboarded_at      TEXT,
    firebase_uid      TEXT,
    created_at        TEXT    NOT NULL,
    updated_at        TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_e164);
"""


# Columns added after Phase-2 GA — kept here so ``_migrate_schema`` can
# add them to existing dbs without dropping rows.  Order matches the
# fresh-create schema above for visual consistency.
_PROFILE_COLUMNS: tuple[tuple[str, str], ...] = (
    ("display_name", "TEXT"),
    ("country_code", "TEXT"),
    ("timezone", "TEXT"),
    ("currency", "TEXT"),
    ("terms_accepted_at", "TEXT"),
    ("onboarded_at", "TEXT"),
    # Phase-4 Firebase migration — added via ALTER TABLE for pre-Phase-4
    # dbs; the partial unique index is created lazily by
    # ``_migrate_schema`` AFTER this ADD COLUMN runs.
    ("firebase_uid", "TEXT"),
)


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
        self._migrate_schema()
        log.info("UserStore opened at {}", self._path)

    def _migrate_schema(self) -> None:
        """Add post-GA columns to a pre-Phase-3 ``users`` table, then
        create the firebase_uid partial unique index.

        ``CREATE TABLE IF NOT EXISTS`` is a no-op when the table already
        exists, so any columns added after the original schema landed
        must be applied via ``ALTER TABLE``.  Idempotent: skips columns
        that already exist.

        IMPORTANT: the partial unique index on ``firebase_uid`` MUST be
        created AFTER the column ADD step.  Putting it in
        ``_SCHEMA_SQL`` (which runs via ``executescript`` BEFORE this
        method) breaks on every pre-Phase-4 db: ``CREATE UNIQUE INDEX
        ON users(firebase_uid)`` raises ``no such column: firebase_uid``
        because the column hasn't been added yet.  The original Phase-4
        implementation hit this in production and required a manual
        ``ALTER TABLE`` on the VPS to recover.  Tests didn't catch it
        because every test fixture uses ``tmp_path`` which always
        starts from a fresh CREATE TABLE that already includes the
        firebase_uid column.
        """
        cur = self._conn.execute("PRAGMA table_info(users)")
        existing = {row["name"] for row in cur.fetchall()}
        for name, decl in _PROFILE_COLUMNS:
            if name in existing:
                continue
            self._conn.execute(
                f"ALTER TABLE users ADD COLUMN {name} {decl}"
            )
            log.info("Migrated users table: added column {}", name)
        # Partial unique index on firebase_uid.  Idempotent — IF NOT
        # EXISTS makes re-runs safe on every UserStore open.  Must run
        # after the ALTER TABLE loop above so the column exists.
        self._conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_firebase_uid "
            "ON users(firebase_uid) WHERE firebase_uid IS NOT NULL"
        )

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
            # Owner is pre-onboarded — set ``onboarded_at`` so the app
            # skips the SignupPage when the operator signs in via the
            # admin-token bypass or via phone-OTP.
            self._conn.execute(
                """
                INSERT INTO users (user_id, phone_e164, tier, paid_until,
                                   telegram_chat_id, onboarded_at,
                                   terms_accepted_at,
                                   created_at, updated_at)
                VALUES (1, ?, ?, NULL, NULL, ?, ?, ?, ?)
                """,
                (phone_e164, _OWNER_TIER, now, now, now, now),
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

    def get_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM users WHERE firebase_uid = ?", (firebase_uid,)
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

    def get_or_create_by_firebase_uid(
        self,
        firebase_uid: str,
        phone_e164: str,
    ) -> User:
        """Atomic upsert keyed by Firebase UID with phone-match backfill.

        Used by the Firebase ID-token auth path (Phase 4).  Resolution:

        1. UID hit → return that row unchanged.
        2. UID miss + phone hit (existing legacy row) → ``UPDATE`` the
           row to set ``firebase_uid``, return updated User.  This is
           the migration path for the 5 testers + owner who already
           exist in SQLite from the HS256 + OTP era.
        3. UID miss + phone miss → ``INSERT`` a fresh row at tier=free
           carrying both ``phone_e164`` and ``firebase_uid``.

        Race-safe: the partial UNIQUE index on ``firebase_uid`` plus
        serialised writes guarantee one row per UID under concurrent
        verifies.
        """
        with self._lock:
            existing = self.get_by_firebase_uid(firebase_uid)
            if existing is not None:
                return existing
            # UID miss — try phone-match for backfill.
            by_phone = self.get_by_phone(phone_e164)
            now = _now_iso()
            if by_phone is not None:
                self._conn.execute(
                    """
                    UPDATE users
                       SET firebase_uid = ?, updated_at = ?
                     WHERE user_id = ?
                    """,
                    (firebase_uid, now, by_phone.user_id),
                )
                log.info(
                    "Backfilled firebase_uid on user_id={}, phone={}",
                    by_phone.user_id, phone_e164,
                )
                updated = self.get_by_id(by_phone.user_id)
                assert updated is not None  # row exists; we just UPDATE'd it
                return updated
            # No phone-match either — fresh row.
            self._conn.execute(
                """
                INSERT INTO users (phone_e164, tier, paid_until,
                                   telegram_chat_id, firebase_uid,
                                   created_at, updated_at)
                VALUES (?, ?, NULL, NULL, ?, ?, ?)
                """,
                (phone_e164, _FREE_TIER, firebase_uid, now, now),
            )
            user = self.get_by_firebase_uid(firebase_uid)
            if user is None:  # pragma: no cover — INSERT then SELECT must hit
                raise RuntimeError(
                    f"user vanished after insert: firebase_uid={firebase_uid!r}"
                )
            log.info(
                "Created user via Firebase: user_id={}, phone={}, firebase_uid={}",
                user.user_id, phone_e164, firebase_uid,
            )
            return user

    def set_firebase_uid(self, user_id: int, firebase_uid: str) -> None:
        """Set ``firebase_uid`` on an existing user.

        Used by the Telegram-OTP-verify endpoint after registering the
        user with Firebase Admin: the engine already has a row for the
        user (created on the OTP path) and now needs to record the
        Firebase identity it just minted on their behalf.  Idempotent —
        calling with an unchanged UID is a no-op write.
        """
        with self._lock:
            now = _now_iso()
            cur = self._conn.execute(
                """
                UPDATE users
                   SET firebase_uid = ?, updated_at = ?
                 WHERE user_id = ?
                """,
                (firebase_uid, now, int(user_id)),
            )
            if cur.rowcount == 0:
                raise LookupError(f"user_id={user_id} not found")
            log.info(
                "Set firebase_uid on user_id={}: uid={}",
                user_id, firebase_uid,
            )

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

    def update_profile(
        self,
        user_id: int,
        *,
        display_name: Optional[str] = None,
        country_code: Optional[str] = None,
        timezone: Optional[str] = None,
        currency: Optional[str] = None,
        accept_terms: bool = False,
    ) -> User:
        """Update profile fields on a user.  Partial updates allowed.

        First successful update with ``display_name`` set and
        ``accept_terms=True`` marks ``onboarded_at=NOW()`` if not
        already set — that's the single signal the app uses to decide
        whether to route to SignupPage on next signin.  Subsequent
        updates leave ``onboarded_at`` alone (idempotent — editing the
        profile after onboarding shouldn't un-onboard the user).

        Raises ``LookupError`` if the user doesn't exist.
        """
        with self._lock:
            existing = self.get_by_id(user_id)
            if existing is None:
                raise LookupError(f"user_id={user_id} not found")
            now = _now_iso()
            # Coalesce: keep prior value when the caller didn't supply one.
            new_display = display_name if display_name is not None else existing.display_name
            new_country = country_code if country_code is not None else existing.country_code
            new_tz = timezone if timezone is not None else existing.timezone
            new_currency = currency if currency is not None else existing.currency
            new_terms = (
                now if (accept_terms and existing.terms_accepted_at is None)
                else (existing.terms_accepted_at.isoformat() if existing.terms_accepted_at else None)
            )
            # Onboarding complete iff: name is now set AND terms have ever
            # been accepted.  Once set, never cleared by later updates.
            new_onboarded = (
                existing.onboarded_at.isoformat() if existing.onboarded_at
                else (now if (new_display and new_terms) else None)
            )
            self._conn.execute(
                """
                UPDATE users
                   SET display_name      = ?,
                       country_code      = ?,
                       timezone          = ?,
                       currency          = ?,
                       terms_accepted_at = ?,
                       onboarded_at      = ?,
                       updated_at        = ?
                 WHERE user_id = ?
                """,
                (
                    new_display, new_country, new_tz, new_currency,
                    new_terms, new_onboarded, now, int(user_id),
                ),
            )
            updated = self.get_by_id(user_id)
            assert updated is not None
            log.info(
                "Profile updated: user_id={}, display={!r}, onboarded={}",
                user_id, new_display, updated.onboarded_at is not None,
            )
            return updated

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
