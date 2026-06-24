"""Tests for the B16 two-tier entitlement model.

* ``auth`` tier hierarchy helpers (can_assist / can_auto / tier_rank).
* The ``signal_dispatch`` money-path gate — only ``auto`` users get
  hands-off server-side auto-execution.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.api import auth


def test_tier_rank_hierarchy():
    assert auth.tier_rank("free") == 0
    assert auth.tier_rank("assist") == 1
    assert auth.tier_rank("auto") == 2
    assert auth.tier_rank("paid") == 2          # legacy == full automation
    assert auth.tier_rank("all-access") >= 2
    assert auth.tier_rank("owner") >= 2
    assert auth.tier_rank(None) == 0
    assert auth.tier_rank("nonsense") == 0


def test_can_assist_and_can_auto():
    assert not auth.can_assist("free")
    assert auth.can_assist("assist")
    assert auth.can_assist("auto")
    assert not auth.can_auto("free")
    assert not auth.can_auto("assist")          # assist is one-tap, not hands-off
    assert auth.can_auto("auto")
    assert auth.can_auto("owner")
    assert auth.can_auto("all-access")


def _mk_user(tier, paid_until):
    """Minimal stand-in for users.User with the fields the gate reads."""
    class _U:
        pass
    u = _U()
    u.tier = tier
    u.paid_until = paid_until
    return u


@pytest.fixture
def dispatch(monkeypatch):
    """signal_dispatch with a stubbed UserStore singleton + clean cache."""
    from src.execution import signal_dispatch as sd
    from src.api import users as users_mod

    sd._TIER_CACHE.clear()

    store = {}

    class _Store:
        def get_by_firebase_uid(self, uid):
            return store.get(uid)

    monkeypatch.setattr(users_mod, "get_singleton", lambda: _Store())
    return sd, store


def test_resolve_tier_unknown_user_is_free(dispatch):
    sd, store = dispatch
    assert sd._resolve_user_tier("nobody") == "free"


def test_resolve_tier_auto_user(dispatch):
    sd, store = dispatch
    store["u1"] = _mk_user("auto", datetime.now(timezone.utc) + timedelta(days=10))
    assert sd._resolve_user_tier("u1") == "auto"


def test_resolve_tier_expired_paid_downgrades_to_free(dispatch):
    sd, store = dispatch
    store["u2"] = _mk_user("auto", datetime.now(timezone.utc) - timedelta(days=1))
    assert sd._resolve_user_tier("u2") == "free"


def test_resolve_tier_assist_user_kept(dispatch):
    sd, store = dispatch
    store["u3"] = _mk_user("assist", datetime.now(timezone.utc) + timedelta(days=5))
    # assist is a valid tier, just not auto — resolve returns it faithfully;
    # the dispatch gate (can_auto) is what blocks hands-off execution.
    assert sd._resolve_user_tier("u3") == "assist"
    assert not auth.can_auto(sd._resolve_user_tier("u3"))


def test_resolve_tier_fails_closed_on_error(dispatch, monkeypatch):
    sd, store = dispatch
    from src.api import users as users_mod

    def _boom():
        raise RuntimeError("db down")

    monkeypatch.setattr(users_mod, "get_singleton", _boom)
    sd._TIER_CACHE.clear()
    assert sd._resolve_user_tier("u4") == "free"   # fail closed
