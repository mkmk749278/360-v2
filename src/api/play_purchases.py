"""Google Play purchase → user mapping (B16 entitlement plumbing).

Why this exists
───────────────
A Play subscription is identified by an opaque ``purchaseToken``.  At
**verify** time the request is authenticated with the user's JWT, so we
know the ``user_id`` — but **RTDN** (Real-Time Developer Notifications,
the renew/cancel/expire push) carries only the ``purchaseToken`` and
``subscriptionId``, no user identity.  To apply a renewal or revocation
to the right account we must remember which user a token belongs to.

This module is that memory: a tiny SQLite table, ``play_purchases``,
keyed by ``purchase_token`` → ``user_id`` (+ the latest product / state /
expiry we observed, purely for observability and idempotency).

It lives in the **same** ``lumin.sqlite`` file as :class:`UserStore` so a
verify can map-then-grant without a cross-database transaction, following
the established one-file / one-connection-per-store convention
(``UserStore`` + ``UserOverridesStore`` already share the file).

No secret material is stored here — only the (already opaque) purchase
token and bookkeeping.  The token alone grants nothing; entitlement is
always re-derived from the Play Developer API.
"""

from __future__ import annotations

import asyncio
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.utils import get_logger

log = get_logger("api.play_purchases")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


@dataclass(frozen=True)
class PlayPurchase:
    """One row of ``play_purchases`` — a token we've seen for a user."""

    purchase_token: str
    user_id: int
    product_id: str
    state: str            # last observed Play subscriptionState, e.g. ACTIVE
    expiry: Optional[datetime]
    created_at: datetime
    updated_at: datetime


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS play_purchases (
    purchase_token  TEXT PRIMARY KEY,
    user_id         INTEGER NOT NULL,
    product_id      TEXT    NOT NULL,
    state           TEXT    NOT NULL DEFAULT '',
    expiry          TEXT,
    created_at      TEXT    NOT NULL,
    updated_at      TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_play_purchases_user ON play_purchases(user_id);
"""


class PlayPurchaseStore:
    """Thread-safe SQLite store mapping Play purchase tokens to users.

    Mirrors :class:`~src.api.users.UserStore`'s connection model: one
    long-lived autocommit connection shared across FastAPI's thread pool,
    serialised by an ``RLock``; WAL + ``busy_timeout`` so it coexists with
    the other stores holding the same file open.
    """

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            str(self._path),
            check_same_thread=False,
            isolation_level=None,  # autocommit
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._conn.executescript(_SCHEMA_SQL)
        log.info("PlayPurchaseStore opened at {}", self._path)

    # ---- helpers --------------------------------------------------------

    @staticmethod
    def _row_to_purchase(row: sqlite3.Row) -> PlayPurchase:
        return PlayPurchase(
            purchase_token=str(row["purchase_token"]),
            user_id=int(row["user_id"]),
            product_id=str(row["product_id"]),
            state=str(row["state"]),
            expiry=_parse_iso(row["expiry"]),
            created_at=_parse_iso(row["created_at"]) or datetime.now(timezone.utc),
            updated_at=_parse_iso(row["updated_at"]) or datetime.now(timezone.utc),
        )

    # ---- writes ---------------------------------------------------------

    def upsert(
        self,
        *,
        purchase_token: str,
        user_id: int,
        product_id: str,
        state: str,
        expiry: Optional[datetime],
    ) -> PlayPurchase:
        """Record (or refresh) a token→user mapping.

        Idempotent: re-verifying the same token updates the observed
        state/expiry and ``updated_at`` but never re-binds the token to a
        different user (the ``user_id`` from the FIRST verify wins; a
        token belongs to exactly one Google account / one of our users).
        """
        expiry_iso = (
            expiry.astimezone(timezone.utc).isoformat() if expiry is not None else None
        )
        with self._lock:
            now = _now_iso()
            self._conn.execute(
                """
                INSERT INTO play_purchases
                    (purchase_token, user_id, product_id, state, expiry,
                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(purchase_token) DO UPDATE SET
                    product_id = excluded.product_id,
                    state      = excluded.state,
                    expiry     = excluded.expiry,
                    updated_at = excluded.updated_at
                """,
                (purchase_token, int(user_id), product_id, state, expiry_iso,
                 now, now),
            )
            row = self._conn.execute(
                "SELECT * FROM play_purchases WHERE purchase_token = ?",
                (purchase_token,),
            ).fetchone()
        return self._row_to_purchase(row)

    def relink(self, *, old_token: str, new_token: str) -> None:
        """Carry a user binding from a superseded token to its replacement.

        Google issues a fresh ``purchaseToken`` on upgrade / downgrade /
        re-signup and reports the previous one as ``linkedPurchaseToken``.
        If we've never seen ``new_token`` but know ``old_token``'s user,
        seed the new row so a later RTDN on the new token still resolves
        the right account.  No-op when the new token is already mapped or
        the old one is unknown.
        """
        with self._lock:
            existing_new = self._conn.execute(
                "SELECT 1 FROM play_purchases WHERE purchase_token = ?",
                (new_token,),
            ).fetchone()
            if existing_new is not None:
                return
            old = self._conn.execute(
                "SELECT * FROM play_purchases WHERE purchase_token = ?",
                (old_token,),
            ).fetchone()
            if old is None:
                return
            now = _now_iso()
            self._conn.execute(
                """
                INSERT INTO play_purchases
                    (purchase_token, user_id, product_id, state, expiry,
                     created_at, updated_at)
                VALUES (?, ?, ?, '', NULL, ?, ?)
                """,
                (new_token, int(old["user_id"]), str(old["product_id"]), now, now),
            )
            log.info(
                "PlayPurchaseStore relinked token (upgrade/resignup): user_id={}",
                int(old["user_id"]),
            )

    # ---- reads ----------------------------------------------------------

    def get(self, purchase_token: str) -> Optional[PlayPurchase]:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM play_purchases WHERE purchase_token = ?",
                (purchase_token,),
            ).fetchone()
        return self._row_to_purchase(row) if row is not None else None

    def list_for_user(self, user_id: int) -> list[PlayPurchase]:
        """All tokens ever seen for a user (indexed; event-time only —
        referral-reward entitlement re-resolution, never a hot loop)."""
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM play_purchases WHERE user_id = ?",
                (int(user_id),),
            ).fetchall()
        return [self._row_to_purchase(row) for row in rows]

    # ---- async variants -------------------------------------------------

    async def aupsert(
        self,
        *,
        purchase_token: str,
        user_id: int,
        product_id: str,
        state: str,
        expiry: Optional[datetime],
    ) -> PlayPurchase:
        return await asyncio.to_thread(
            lambda: self.upsert(
                purchase_token=purchase_token,
                user_id=user_id,
                product_id=product_id,
                state=state,
                expiry=expiry,
            )
        )

    async def aget(self, purchase_token: str) -> Optional[PlayPurchase]:
        return await asyncio.to_thread(self.get, purchase_token)

    async def alist_for_user(self, user_id: int) -> list[PlayPurchase]:
        return await asyncio.to_thread(self.list_for_user, user_id)

    async def arelink(self, *, old_token: str, new_token: str) -> None:
        await asyncio.to_thread(
            lambda: self.relink(old_token=old_token, new_token=new_token)
        )
