"""Tests for src.execution.kill_switch.

The Firestore SDK is mocked at the constructor.  What we pin:

* Global engage / disengage round-trips: write goes to the right doc
  path; cache is invalidated on write; reads return the latest value.
* Cache TTL: within the TTL window, subsequent reads don't hit
  Firestore; after expiry they do.
* Per-user disable / enable: writes use ``set(..., merge=True)`` so
  we don't clobber the user's other profile fields.
* Reads default to False (kill switch not engaged) for missing docs
  — so a freshly-deployed engine without any kill-switch doc yet
  doesn't accidentally treat itself as engaged.
* Singleton init is idempotent + the typed not-initialised error is
  surfaced before init.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.execution import kill_switch


@pytest.fixture(autouse=True)
def _reset_module():
    kill_switch.reset_for_test()
    yield
    kill_switch.reset_for_test()


def _make_mock_db():
    """Build a Firestore mock that supports
    db.collection(...).document(...).get / set + 4-level chain for
    user docs.

    ``doc_map`` is keyed by ``(collection, doc_id)``.  Pre-warmed
    with the well-known kill-switch and user doc paths so tests can
    configure their mock responses without triggering creation
    first."""
    db = MagicMock()

    def make_doc():
        doc = MagicMock()
        doc.get.return_value = SimpleNamespace(exists=False, to_dict=lambda: {})
        return doc

    coll_to_doc: dict = {}
    coll_to_doc[("kill_switch", "global")] = make_doc()

    coll_mocks: dict = {}

    def collection(name):
        coll = coll_mocks.setdefault(name, MagicMock())

        def get_or_make_doc(doc_id):
            key = (name, doc_id)
            if key not in coll_to_doc:
                coll_to_doc[key] = make_doc()
            return coll_to_doc[key]

        coll.document.side_effect = get_or_make_doc
        return coll

    db.collection.side_effect = collection
    return db, coll_to_doc


def _make_client_with_clock():
    """Construct a KillSwitchClient with an injectable monotonic
    clock so cache-TTL behaviour is testable without ``time.sleep``."""
    db, doc_map = _make_mock_db()
    client = kill_switch.KillSwitchClient(db)
    fake_clock = [0.0]
    client._clock = lambda: fake_clock[0]
    return client, db, doc_map, fake_clock


# ---------------------------------------------------------------------------
# Global engage / disengage
# ---------------------------------------------------------------------------


def test_global_default_is_disengaged() -> None:
    """Missing doc → False.  A fresh engine without a kill_switch
    doc yet must NOT halt itself."""
    client, _, _, _ = _make_client_with_clock()
    assert client.is_global_engaged() is False


def test_engage_global_writes_and_invalidates_cache() -> None:
    client, db, doc_map, _ = _make_client_with_clock()
    # First read populates the cache (False).
    assert client.is_global_engaged() is False
    client.engage_global(reason="test trip")
    # Write went to the kill_switch/global doc.
    kill_doc = doc_map[("kill_switch", "global")]
    kill_doc.set.assert_called_once()
    payload = kill_doc.set.call_args[0][0]
    assert payload["engaged"] is True
    assert payload["reason"] == "test trip"
    # Cache invalidated — next read fetches afresh.  Make the new
    # ``get`` return engaged=True to verify the read happens.
    kill_doc.get.return_value = SimpleNamespace(
        exists=True, to_dict=lambda: {"engaged": True}
    )
    assert client.is_global_engaged() is True


def test_disengage_global_writes_false() -> None:
    client, _, doc_map, _ = _make_client_with_clock()
    client.disengage_global()
    kill_doc = doc_map[("kill_switch", "global")]
    kill_doc.set.assert_called_once()
    payload = kill_doc.set.call_args[0][0]
    assert payload["engaged"] is False


def test_cache_ttl_within_window_skips_firestore_read() -> None:
    """The TTL property: within 5s of last read, subsequent reads
    don't hit Firestore.  This is what keeps the kill-switch check
    cheap enough to call on every order."""
    client, _, doc_map, clock = _make_client_with_clock()
    kill_doc = doc_map[("kill_switch", "global")]
    kill_doc.get.return_value = SimpleNamespace(
        exists=True, to_dict=lambda: {"engaged": False}
    )
    # Two reads back-to-back.
    client.is_global_engaged()
    client.is_global_engaged()
    # Only one Firestore get because the second was served from cache.
    assert kill_doc.get.call_count == 1


def test_cache_ttl_expires_after_window() -> None:
    """After 5s the cache is stale; next read re-fetches.  This is
    what bounds the kill-switch SLA at 5s — operator flips, all
    readers see the new value within one TTL."""
    client, _, doc_map, clock = _make_client_with_clock()
    kill_doc = doc_map[("kill_switch", "global")]
    kill_doc.get.return_value = SimpleNamespace(
        exists=True, to_dict=lambda: {"engaged": False}
    )
    client.is_global_engaged()
    clock[0] = 5.1  # advance past TTL
    client.is_global_engaged()
    assert kill_doc.get.call_count == 2


# ---------------------------------------------------------------------------
# Per-user disable
# ---------------------------------------------------------------------------


def test_user_default_is_not_disabled() -> None:
    client, _, _, _ = _make_client_with_clock()
    assert client.is_user_disabled("fb-x") is False


def test_disable_user_writes_with_merge_true_to_preserve_profile() -> None:
    """The user doc may have non-secret profile fields written by
    the user (display name, prefs, etc.) — disabling auto-trade
    must NOT clobber those.  ``merge=True`` is the critical
    detail."""
    client, _, doc_map, _ = _make_client_with_clock()
    client.disable_user("fb-x", reason="circuit breaker tripped")
    user_doc = doc_map[("users", "fb-x")]
    user_doc.set.assert_called_once()
    args, kwargs = user_doc.set.call_args
    assert kwargs.get("merge") is True
    payload = args[0]
    assert payload["auto_trade_disabled"] is True
    assert payload["auto_trade_disabled_reason"] == "circuit breaker tripped"


def test_enable_user_writes_false_with_merge_true() -> None:
    client, _, doc_map, _ = _make_client_with_clock()
    client.enable_user("fb-x")
    user_doc = doc_map[("users", "fb-x")]
    user_doc.set.assert_called_once()
    args, kwargs = user_doc.set.call_args
    assert kwargs.get("merge") is True
    assert args[0]["auto_trade_disabled"] is False


def test_is_user_disabled_reads_from_firestore() -> None:
    client, _, doc_map, _ = _make_client_with_clock()
    # Trigger doc creation, then configure + invalidate cache.
    client.is_user_disabled("fb-x")
    user_doc = doc_map[("users", "fb-x")]
    user_doc.get.return_value = SimpleNamespace(
        exists=True, to_dict=lambda: {"auto_trade_disabled": True}
    )
    client.invalidate_cache()
    assert client.is_user_disabled("fb-x") is True


def test_user_cache_per_user_isolation() -> None:
    """Each user's flag is cached independently — invalidating one
    user's entry must not affect another."""
    client, db, doc_map, clock = _make_client_with_clock()
    # Trigger doc creation by reading once.
    client.is_user_disabled("fb-A")
    client.is_user_disabled("fb-B")
    # Now configure the per-user docs.
    doc_a = doc_map[("users", "fb-A")]
    doc_a.get.return_value = SimpleNamespace(
        exists=True, to_dict=lambda: {"auto_trade_disabled": True}
    )
    doc_b = doc_map[("users", "fb-B")]
    doc_b.get.return_value = SimpleNamespace(
        exists=True, to_dict=lambda: {"auto_trade_disabled": False}
    )
    # Invalidate the cache so the configured mocks are used.
    client.invalidate_cache()
    assert client.is_user_disabled("fb-A") is True
    assert client.is_user_disabled("fb-B") is False
    # Disable A again — cache for A invalidated, B's cache survives.
    client.disable_user("fb-A", reason="x")
    # Reading B should NOT hit Firestore again (still cached).
    pre_b_calls = doc_b.get.call_count
    client.is_user_disabled("fb-B")
    assert doc_b.get.call_count == pre_b_calls


# ---------------------------------------------------------------------------
# Singleton lifecycle
# ---------------------------------------------------------------------------


def test_is_initialised_false_before_init() -> None:
    assert kill_switch.is_initialised() is False


def test_init_then_is_initialised_true() -> None:
    kill_switch.init_kill_switch(MagicMock())
    assert kill_switch.is_initialised() is True


def test_init_idempotent_second_call_no_op() -> None:
    """Second init keeps the original client — wouldn't rebuild with
    a fresh Firestore client (which would lose any cached state)."""
    db1 = MagicMock()
    db2 = MagicMock()
    kill_switch.init_kill_switch(db1)
    first = kill_switch.get_client()
    kill_switch.init_kill_switch(db2)
    second = kill_switch.get_client()
    assert first is second


def test_get_client_raises_before_init() -> None:
    with pytest.raises(kill_switch.KillSwitchNotInitialisedError):
        kill_switch.get_client()


def test_invalidate_cache_drops_all_entries() -> None:
    client, _, doc_map, _ = _make_client_with_clock()
    kill_doc = doc_map[("kill_switch", "global")]
    kill_doc.get.return_value = SimpleNamespace(
        exists=True, to_dict=lambda: {"engaged": False}
    )
    client.is_global_engaged()
    assert kill_doc.get.call_count == 1
    client.invalidate_cache()
    client.is_global_engaged()
    assert kill_doc.get.call_count == 2
