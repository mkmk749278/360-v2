"""Tests for user_overrides.resolve_pretp_threshold_uid (2026-06-01).

The per-user pre-TP threshold ("close at 0.3% vs 0.5%") was stored in
``user_pretp_settings.threshold_pct`` and surfaced in the app, but the
execution path never read it — every user's pre-TP rested at the engine
default.  This resolver closes that gap.  What we pin:

* A stored in-band threshold is returned verbatim.
* An unset threshold falls back to the supplied engine default.
* An out-of-band stored value (≤0, or absurdly large) falls back to the
  default rather than placing a pre-TP at a nonsensical price.
* Per-user isolation: user 1's 0.30 doesn't leak into user 2's 0.50.
"""
from __future__ import annotations

import pytest

from src.api import user_overrides as _uo
from src.api.user_overrides import UserOverridesStore
from src.api import users as _users
from src.api.users import UserStore


@pytest.fixture
def stores(tmp_path, monkeypatch):
    """Wire a UserStore + UserOverridesStore singleton pair sharing one
    SQLite file, with two firebase-linked users."""
    db_path = tmp_path / "lumin.sqlite"
    user_store = UserStore(db_path)
    user_store.get_or_create_by_firebase_uid("fb-user-1", "+10000000001")
    user_store.get_or_create_by_firebase_uid("fb-user-2", "+10000000002")
    # users.get_singleton() reads the module global ``_store``.
    monkeypatch.setattr(_users, "_store", user_store, raising=False)

    ov_store = UserOverridesStore(db_path)
    monkeypatch.setattr(_uo, "_SINGLETON", ov_store, raising=False)
    return user_store, ov_store


def _uid_of(user_store, firebase_uid: str) -> int:
    return int(user_store.get_by_firebase_uid(firebase_uid).user_id)


def test_returns_stored_in_band_threshold(stores):
    user_store, ov_store = stores
    ov_store.update_pretp(_uid_of(user_store, "fb-user-1"), {"threshold_pct": 0.30})
    assert _uo.resolve_pretp_threshold_uid("fb-user-1", default=0.35) == 0.30


def test_unset_falls_back_to_default(stores):
    # User exists but never set a threshold.
    assert _uo.resolve_pretp_threshold_uid("fb-user-2", default=0.35) == 0.35


def test_out_of_band_low_falls_back_to_default(stores):
    user_store, ov_store = stores
    # 0.0 is below the 0.05 floor — would rest the LIMIT inside the spread.
    ov_store.update_pretp(_uid_of(user_store, "fb-user-1"), {"threshold_pct": 0.0})
    assert _uo.resolve_pretp_threshold_uid("fb-user-1", default=0.35) == 0.35


def test_out_of_band_high_falls_back_to_default(stores):
    user_store, ov_store = stores
    # 12% is above the 5% ceiling — not a scalp pre-TP.
    ov_store.update_pretp(_uid_of(user_store, "fb-user-1"), {"threshold_pct": 12.0})
    assert _uo.resolve_pretp_threshold_uid("fb-user-1", default=0.35) == 0.35


def test_per_user_isolation(stores):
    user_store, ov_store = stores
    ov_store.update_pretp(_uid_of(user_store, "fb-user-1"), {"threshold_pct": 0.30})
    ov_store.update_pretp(_uid_of(user_store, "fb-user-2"), {"threshold_pct": 0.50})
    assert _uo.resolve_pretp_threshold_uid("fb-user-1", default=0.35) == 0.30
    assert _uo.resolve_pretp_threshold_uid("fb-user-2", default=0.35) == 0.50


def test_unknown_user_falls_back_to_default(stores):
    assert _uo.resolve_pretp_threshold_uid("fb-nonexistent", default=0.35) == 0.35


def test_no_singleton_returns_default(monkeypatch):
    monkeypatch.setattr(_uo, "_SINGLETON", None, raising=False)
    assert _uo.resolve_pretp_threshold_uid("fb-user-1", default=0.42) == 0.42
