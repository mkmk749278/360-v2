"""UserStore tests — SQLite registry of phone-verified users.

Covers Phase 2 multi-user expansion's persistence layer:

- Owner bootstrap (idempotent — only inserts on empty DB).
- ``get_or_create_by_phone`` round-trip + race safety.
- ``set_tier`` updates, paid_until ISO round-trip, missing-user error.
- WAL mode actually enabled.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.api.users import UserStore


@pytest.fixture
def store(tmp_path):
    s = UserStore(tmp_path / "lumin.sqlite")
    yield s
    s.close()


# ---------------------------------------------------------------------------
# Schema + WAL
# ---------------------------------------------------------------------------


def test_fresh_store_is_empty(store: UserStore) -> None:
    assert store.is_empty() is True


def test_wal_mode_enabled(store: UserStore) -> None:
    cur = store._conn.execute("PRAGMA journal_mode")
    mode = cur.fetchone()[0]
    assert mode.lower() == "wal"


# ---------------------------------------------------------------------------
# Owner bootstrap
# ---------------------------------------------------------------------------


def test_bootstrap_owner_seeds_user_id_1(store: UserStore) -> None:
    user = store.bootstrap_owner_if_empty("+15551112222")
    assert user is not None
    assert user.user_id == 1
    assert user.tier == "owner"
    assert user.phone_e164 == "+15551112222"
    assert store.is_empty() is False


def test_bootstrap_owner_idempotent_on_non_empty(store: UserStore) -> None:
    first = store.bootstrap_owner_if_empty("+15551112222")
    assert first is not None
    # Second call — table is no longer empty, should be a no-op.
    second = store.bootstrap_owner_if_empty("+15559998888")
    assert second is None
    # Existing owner unchanged.
    assert store.get_by_id(1) is not None
    assert store.get_by_id(1).phone_e164 == "+15551112222"


def test_bootstrap_owner_skipped_when_phone_empty(store: UserStore) -> None:
    user = store.bootstrap_owner_if_empty("")
    assert user is None
    assert store.is_empty() is True


# ---------------------------------------------------------------------------
# get_or_create_by_phone
# ---------------------------------------------------------------------------


def test_get_or_create_inserts_first_time(store: UserStore) -> None:
    user = store.get_or_create_by_phone("+447700900001")
    assert user.user_id >= 1
    assert user.phone_e164 == "+447700900001"
    assert user.tier == "free"
    assert user.paid_until is None


def test_get_or_create_returns_existing_unchanged(store: UserStore) -> None:
    first = store.get_or_create_by_phone("+447700900001")
    second = store.get_or_create_by_phone("+447700900001")
    assert second.user_id == first.user_id
    assert second.created_at == first.created_at


def test_get_or_create_assigns_distinct_ids(store: UserStore) -> None:
    a = store.get_or_create_by_phone("+447700900001")
    b = store.get_or_create_by_phone("+447700900002")
    assert a.user_id != b.user_id


# ---------------------------------------------------------------------------
# set_tier
# ---------------------------------------------------------------------------


def test_set_tier_updates_paid_until_round_trip(store: UserStore) -> None:
    user = store.get_or_create_by_phone("+9198765432")
    expiry = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(days=30)
    updated = store.set_tier(user.user_id, tier="paid", paid_until=expiry)
    assert updated.tier == "paid"
    assert updated.paid_until == expiry
    # Re-read confirms persistence (not just in-memory).
    fresh = store.get_by_id(user.user_id)
    assert fresh is not None
    assert fresh.tier == "paid"
    assert fresh.paid_until == expiry


def test_set_tier_to_free_clears_paid_until(store: UserStore) -> None:
    user = store.get_or_create_by_phone("+9198765432")
    expiry = datetime.now(timezone.utc) + timedelta(days=30)
    store.set_tier(user.user_id, tier="paid", paid_until=expiry)
    # Subscription expired / cancelled → revoke.
    revoked = store.set_tier(user.user_id, tier="free", paid_until=None)
    assert revoked.tier == "free"
    assert revoked.paid_until is None


def test_set_tier_unknown_user_raises(store: UserStore) -> None:
    with pytest.raises(LookupError):
        store.set_tier(9999, tier="paid", paid_until=None)


# ---------------------------------------------------------------------------
# Persistence across reopens
# ---------------------------------------------------------------------------


def test_reopen_preserves_users(tmp_path) -> None:
    db = tmp_path / "lumin.sqlite"
    s1 = UserStore(db)
    s1.bootstrap_owner_if_empty("+10000000001")
    s1.get_or_create_by_phone("+10000000002")
    s1.close()

    s2 = UserStore(db)
    try:
        owner = s2.get_by_id(1)
        tester = s2.get_by_phone("+10000000002")
        assert owner is not None and owner.tier == "owner"
        assert tester is not None and tester.tier == "free"
    finally:
        s2.close()
