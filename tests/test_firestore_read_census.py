"""The Firestore read census, and the three cuts made on 2026-09-02.

Context: Firestore answered ``RESOURCE_EXHAUSTED: Quota exceeded.`` at 00:41
UTC and auto-trade went down for every user.  53,000 document reads against a
50,000/day allowance, on **25 writes**.  These tests pin the census that says
where the reads go, and the three reductions — each of which must fail against
the pre-fix tree, or it is not testing the fix.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from src import firestore_reads


ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _clean_census():
    firestore_reads.reset_for_test()
    yield
    firestore_reads.reset_for_test()


# ---------------------------------------------------------------------------
# The census itself
# ---------------------------------------------------------------------------


def test_counts_documents_not_calls():
    """A collection-group query returning 40 docs costs 40 reads, not one.

    Counting calls would have made ``list_active_uids`` — the read that grows
    linearly with subscribers — indistinguishable from a single-document get,
    which is exactly the read we most needed to see.
    """
    firestore_reads.record("keystore.list_active_uids", 40)
    firestore_reads.record("keystore.list_active_uids", 12)
    snap = firestore_reads.snapshot()
    row = next(r for r in snap["sites"] if r["site"] == "keystore.list_active_uids")
    assert row["docs"] == 52
    assert row["calls"] == 2
    assert row["docs_per_call"] == 26.0
    assert snap["total_docs"] == 52


def test_snapshot_names_the_process_it_describes(monkeypatch):
    """Engine and api hold separate counters; a census that could not say which
    would repeat the INDEX COLD defect at the moment somebody hunts a hot loop."""
    monkeypatch.setenv("API_PROCESS_ISOLATED", "true")
    monkeypatch.setenv("PROCESS_ROLE", "api")
    assert firestore_reads.snapshot()["process_role"] == "api"
    monkeypatch.setenv("API_PROCESS_ISOLATED", "false")
    assert firestore_reads.snapshot()["process_role"] == "single"


def test_short_uptime_is_flagged_beside_the_extrapolation():
    """per_day from ninety seconds of data is an extrapolation, not a
    measurement — the reader is told which."""
    snap = firestore_reads.snapshot()
    assert snap["uptime_is_short"] is True
    assert snap["free_tier_reads_per_day"] == 50000


def test_record_never_raises_on_bad_input():
    firestore_reads.record("x", None)      # type: ignore[arg-type]
    firestore_reads.record("y", -5)
    assert firestore_reads.snapshot()["total_docs"] == 0


# ---------------------------------------------------------------------------
# Cut 1 — runtime_status asks whether a key EXISTS, and used to fetch the blob
# ---------------------------------------------------------------------------


def _status_source() -> str:
    return (ROOT / "src" / "api" / "auto_trade_status_routes.py").read_text()


def test_runtime_status_uses_has_key_not_get_key_blob():
    """Fails against the pre-fix tree, which fetched the blob once per 10s
    per polling user purely to answer binance_key_connected — fetching and
    discarding an encrypted secret ~8,600 times a day per open Trade tab."""
    tree = ast.parse(_status_source())
    attrs = {
        n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)
    }
    assert "has_key" in attrs
    assert "get_key_blob" not in attrs, (
        "the status route must not fetch key material to answer an "
        "existence question"
    )


# ---------------------------------------------------------------------------
# NOT cut: worker_manager's roster query — priced, deferred, and why
# ---------------------------------------------------------------------------


def test_worker_manager_roster_query_is_still_uncached_and_that_is_recorded():
    """``worker_manager._tick`` runs every 60s and calls ``list_active_uids``,
    a collection-group query, with no cache — 1,440 x keyed-users reads a day,
    which at 50 subscribers exceeds the whole 50,000/day allowance on its own.

    It is deliberately NOT fixed here.  The obvious repair — share
    ``signal_dispatch``'s cached roster — saves nothing, because that cache's
    TTL is 30s and this loop runs at 60s, so every call still misses; and
    widening the TTL changes how quickly a newly-connected user starts trading
    and how quickly a disconnected one stops, which is a money-path freshness
    decision that should be made on the census numbers rather than on an
    estimate.  Today it is ~1,440 reads (2.9% of the allowance); the growth is
    the problem, not the level.

    This test pins the shape so the deferral is visible rather than forgotten,
    and it is expected to be REPLACED — not deleted — when the cut is made.
    """
    src = (ROOT / "src" / "execution" / "worker_manager.py").read_text()
    tree = ast.parse(src)
    calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == "list_active_uids"
    ]
    assert len(calls) == 1
    assert "_ACTIVE_UIDS" not in src, (
        "if this loop gains a cache, replace this test with one asserting the "
        "TTL actually covers the loop interval"
    )


# ---------------------------------------------------------------------------
# Cut 3 — the tunables TTL was a spend floor, not a staleness bound
# ---------------------------------------------------------------------------


def test_tunables_ttl_is_not_five_seconds(monkeypatch):
    """5s x continuous scanner access = 17,280 reads/day on one document, 35%
    of the whole allowance, for ops knobs.  Fails against the pre-fix tree."""
    import importlib

    from src import runtime_tunables

    monkeypatch.delenv("RUNTIME_TUNABLES_CACHE_TTL_SEC", raising=False)
    importlib.reload(runtime_tunables)
    assert runtime_tunables._CACHE_TTL_S >= 30.0


def test_tunables_ttl_env_override_and_floor(monkeypatch):
    import importlib

    from src import runtime_tunables

    monkeypatch.setenv("RUNTIME_TUNABLES_CACHE_TTL_SEC", "120")
    importlib.reload(runtime_tunables)
    assert runtime_tunables._CACHE_TTL_S == 120.0

    monkeypatch.setenv("RUNTIME_TUNABLES_CACHE_TTL_SEC", "0.01")
    importlib.reload(runtime_tunables)
    assert runtime_tunables._CACHE_TTL_S == 1.0, "a sub-second TTL is a hot-loop read"

    monkeypatch.setenv("RUNTIME_TUNABLES_CACHE_TTL_SEC", "not-a-number")
    importlib.reload(runtime_tunables)
    assert runtime_tunables._CACHE_TTL_S == 30.0

    monkeypatch.delenv("RUNTIME_TUNABLES_CACHE_TTL_SEC", raising=False)
    importlib.reload(runtime_tunables)


# ---------------------------------------------------------------------------
# The census must be readable, or it is the defect this repo names most often
# ---------------------------------------------------------------------------


def test_census_is_reachable_from_the_diag_catalog():
    from src import diag_catalog

    keys = {row["key"] for row in diag_catalog.catalog()}
    assert "read.firestore_reads" in keys, (
        "a census nobody can reach is exactly as useful as no census"
    )


# ---------------------------------------------------------------------------
# has_key — the cache's actual behaviour, not just its call site
# ---------------------------------------------------------------------------


def _install_fake_keystore(exists: bool):
    """Wire a fake Firestore doc into the keystore and return (doc, reset)."""
    from unittest.mock import MagicMock

    from src.security import firestore_keystore as fk

    snap = MagicMock()
    snap.exists = exists
    doc = MagicMock(name="doc_ref")
    doc.get.return_value = snap
    key_coll = MagicMock()
    key_coll.document.return_value = doc
    user_doc = MagicMock()
    user_doc.collection.return_value = key_coll
    users = MagicMock()
    users.document.return_value = user_doc
    db = MagicMock()
    db.collection.return_value = users
    fk.reset_for_test()
    fk._db = db
    return fk, doc


def test_has_key_reads_once_then_serves_the_cached_answer():
    fk, doc = _install_fake_keystore(exists=True)
    try:
        assert fk.has_key("uid-1") is True
        assert fk.has_key("uid-1") is True
        assert fk.has_key("uid-1") is True
        assert doc.get.call_count == 1, (
            "the polling path must not re-read Firestore every call"
        )
    finally:
        fk.reset_for_test()


def test_has_key_is_invalidated_by_connect_and_disconnect():
    """A user who has just linked a key must not be told for another minute
    that they have not — every writer drops the cached answer."""
    fk, doc = _install_fake_keystore(exists=False)
    try:
        assert fk.has_key("uid-2") is False
        assert doc.get.call_count == 1

        doc.get.return_value.exists = True
        assert fk.has_key("uid-2") is False, "still cached"

        fk._invalidate_has_key("uid-2")
        assert fk.has_key("uid-2") is True
        assert doc.get.call_count == 2

        fk.delete_key_blob("uid-2")
        doc.get.return_value.exists = False
        assert fk.has_key("uid-2") is False
    finally:
        fk.reset_for_test()


def test_has_key_refuses_rather_than_answering_false_when_uninitialised():
    """"We could not ask" and "the user has no key" are different facts — the
    app told a subscriber whose key IS connected to go and connect one because
    the runtime-status payload rendered them identically."""
    from src.security import firestore_keystore as fk

    fk.reset_for_test()
    with pytest.raises(fk.FirestoreKeystoreNotInitialisedError):
        fk.has_key("uid-3")


def test_get_key_blob_still_reads_through():
    """Key material is not cached: the order path runs a few times a day, and
    holding an encrypted secret in memory for a TTL buys nothing."""
    fk, doc = _install_fake_keystore(exists=False)
    try:
        for _ in range(3):
            with pytest.raises(fk.KeyBlobNotFoundError):
                fk.get_key_blob("uid-4")
        assert doc.get.call_count == 3
    finally:
        fk.reset_for_test()
