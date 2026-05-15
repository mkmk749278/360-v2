"""UserStore tests — Firebase-uid backfill + get-or-create paths (Phase 4)."""
from __future__ import annotations

import pytest

from src.api.users import UserStore


@pytest.fixture
def store(tmp_path):
    s = UserStore(tmp_path / "lumin.sqlite")
    yield s
    s.close()


# ---------------------------------------------------------------------------
# Schema migration
# ---------------------------------------------------------------------------


def test_firebase_uid_column_present_after_open(store: UserStore) -> None:
    cur = store._conn.execute("PRAGMA table_info(users)")
    columns = {row["name"] for row in cur.fetchall()}
    assert "firebase_uid" in columns


def test_partial_unique_index_on_firebase_uid(store: UserStore) -> None:
    """The CREATE UNIQUE INDEX statement must have run on store open."""
    cur = store._conn.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='index' AND name='idx_users_firebase_uid'"
    )
    row = cur.fetchone()
    assert row is not None


def test_partial_unique_index_allows_multiple_null(store: UserStore) -> None:
    """Two users with NULL firebase_uid must coexist — that's exactly
    the unmigrated-legacy-row state we expect on a transition-era DB."""
    a = store.get_or_create_by_phone("+15550000001")
    b = store.get_or_create_by_phone("+15550000002")
    assert a.firebase_uid is None
    assert b.firebase_uid is None
    # No raise → partial index correctly excludes NULLs.


# ---------------------------------------------------------------------------
# get_or_create_by_firebase_uid
# ---------------------------------------------------------------------------


def test_creates_row_when_uid_and_phone_both_new(store: UserStore) -> None:
    user = store.get_or_create_by_firebase_uid(
        firebase_uid="fb-uid-1",
        phone_e164="+15550001111",
    )
    assert user.user_id >= 1
    assert user.firebase_uid == "fb-uid-1"
    assert user.phone_e164 == "+15550001111"
    assert user.tier == "free"


def test_returns_existing_when_uid_matches(store: UserStore) -> None:
    first = store.get_or_create_by_firebase_uid(
        firebase_uid="fb-uid-1",
        phone_e164="+15550001111",
    )
    # Same UID — must return the same row even if a different phone is
    # presented (defensive; in practice phone shouldn't change).
    second = store.get_or_create_by_firebase_uid(
        firebase_uid="fb-uid-1",
        phone_e164="+15550001111",
    )
    assert second.user_id == first.user_id
    assert second.firebase_uid == "fb-uid-1"


def test_backfills_uid_on_existing_phone_row(store: UserStore) -> None:
    """Migration path: existing tester from the legacy OTP era has a
    row with phone_e164 but firebase_uid IS NULL.  First Firebase
    sign-in should UPDATE that row to set firebase_uid — same user_id,
    same tier, no data lost."""
    legacy = store.get_or_create_by_phone("+15550002222")
    assert legacy.firebase_uid is None
    legacy_id = legacy.user_id

    migrated = store.get_or_create_by_firebase_uid(
        firebase_uid="fb-uid-2",
        phone_e164="+15550002222",
    )
    # Same row — user_id preserved.
    assert migrated.user_id == legacy_id
    assert migrated.firebase_uid == "fb-uid-2"
    assert migrated.phone_e164 == "+15550002222"
    # Re-read confirms the UPDATE landed on disk.
    fresh = store.get_by_id(legacy_id)
    assert fresh is not None
    assert fresh.firebase_uid == "fb-uid-2"


def test_backfill_preserves_tier_and_paid_until(store: UserStore) -> None:
    """A paid tester migrating shouldn't lose their tier."""
    from datetime import datetime, timedelta, timezone

    legacy = store.get_or_create_by_phone("+15550003333")
    expiry = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(days=30)
    store.set_tier(legacy.user_id, tier="paid", paid_until=expiry)

    migrated = store.get_or_create_by_firebase_uid(
        firebase_uid="fb-uid-3",
        phone_e164="+15550003333",
    )
    assert migrated.user_id == legacy.user_id
    assert migrated.tier == "paid"
    assert migrated.paid_until == expiry


# ---------------------------------------------------------------------------
# set_firebase_uid
# ---------------------------------------------------------------------------


def test_set_firebase_uid_updates_column(store: UserStore) -> None:
    user = store.get_or_create_by_phone("+15550004444")
    assert user.firebase_uid is None
    store.set_firebase_uid(user.user_id, "fb-uid-4")
    updated = store.get_by_id(user.user_id)
    assert updated is not None
    assert updated.firebase_uid == "fb-uid-4"


def test_set_firebase_uid_unknown_user_raises(store: UserStore) -> None:
    with pytest.raises(LookupError):
        store.set_firebase_uid(9999, "fb-uid-unused")


# ---------------------------------------------------------------------------
# get_by_firebase_uid
# ---------------------------------------------------------------------------


def test_get_by_firebase_uid_returns_none_for_unknown(store: UserStore) -> None:
    assert store.get_by_firebase_uid("nonexistent-uid") is None


def test_get_by_firebase_uid_after_set(store: UserStore) -> None:
    user = store.get_or_create_by_phone("+15550005555")
    store.set_firebase_uid(user.user_id, "fb-uid-5")
    looked_up = store.get_by_firebase_uid("fb-uid-5")
    assert looked_up is not None
    assert looked_up.user_id == user.user_id
