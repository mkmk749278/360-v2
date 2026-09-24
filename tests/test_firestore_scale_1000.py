"""Firestore at the 1,000-member target (2026-09-24).

Owner: *"50k is not the hard stop, that's the free per-day reads — but
maximise the efficiency, make it for 1000 users in the future."*

Four reads grew with members and none of them was visible in the census the
engine's diag console reads:

* the signing service read the key blob from Firestore on EVERY signed call —
  every order, cancel, keepalive and reconciler poll — in a process whose own
  census nothing read;
* the position-index resync re-read every live position every five minutes to
  re-confirm an index its only writer keeps exact;
* the active-key roster rebuild re-scanned every key document every half hour;
* and a failed roster scan was persisted as an EMPTY roster — on a day when
  reads are refused and writes are not (2 Sep exactly), every signal would fan
  out to zero users until the next good rebuild.

Every test counts documents the way Firestore bills them.  The invalidation
tests matter more than the savings: a stale key blob is a signature under a
rotated key, and a stale index hides a live position from the pre-TP
dispatcher.
"""
from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src import control_generation as gen
from src import fail_open
from src import firestore_reads as reads
from src.execution import position_state as ps
from src.security import envelope_crypto, firestore_keystore as fk, kms_client
from src.security.signing_service import handler, protocol


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class _FakeRedis:
    """Enough redis-py for the generation channel and the census peers."""

    def __init__(self) -> None:
        self.store: dict = {}
        self.fail = False
        self.ttls: dict = {}

    def _check(self) -> None:
        if self.fail:
            raise RuntimeError("redis down")

    def get(self, key):
        self._check()
        v = self.store.get(key)
        return None if v is None else str(v)

    def set(self, key, value, nx=False, ex=None):
        self._check()
        if nx and key in self.store:
            return None
        self.store[key] = value
        if ex is not None:
            self.ttls[key] = ex
        return True

    def incr(self, key):
        self._check()
        self.store[key] = int(self.store.get(key, 0)) + 1
        return self.store[key]

    def mget(self, keys):
        self._check()
        return [None if self.store.get(k) is None else str(self.store[k]) for k in keys]

    def scan_iter(self, match="*", count=None):
        self._check()
        prefix = match.rstrip("*")
        return [k for k in list(self.store) if str(k).startswith(prefix)]

    def flushall(self):
        self.store.clear()
        self.ttls.clear()


class _Agg:
    def __init__(self, value):
        self.value = value


class _Ref:
    """A document reference: ``.id`` and ``.parent`` (a collection ref whose
    ``.parent`` is the owning document) — the shape the roster scan walks."""

    def __init__(self, path):
        self.path = path
        self.id = path[-1]

    @property
    def parent(self):
        coll = SimpleNamespace(id=self.path[-2])
        coll.parent = _Ref(self.path[:-2]) if len(self.path) > 2 else None
        return coll


class _Snap:
    def __init__(self, path, data):
        self.id = path[-1]
        self._data = data
        self.exists = data is not None
        self.reference = _Ref(path)

    def to_dict(self):
        return dict(self._data or {})


class _Doc:
    def __init__(self, db, path):
        self._db, self._path = db, path

    def get(self):
        self._db.docs_returned += 1
        return _Snap(self._path, self._db.data.get(self._path))

    def set(self, payload, merge=False):
        self._db.writes += 1
        cur = dict(self._db.data.get(self._path) or {}) if merge else {}
        cur.update(payload)
        self._db.data[self._path] = cur

    def delete(self):
        self._db.writes += 1
        self._db.data.pop(self._path, None)

    def collection(self, name):
        return _Coll(self._db, self._path + (name,))


class _Coll:
    def __init__(self, db, path):
        self._db, self._path = db, path

    def document(self, doc_id):
        return _Doc(self._db, self._path + (doc_id,))


class _Group:
    """``collection_group(name)`` with an optional ``where(field, "in", ...)``.

    ``stream`` bills one read per document returned; ``count().get()`` bills
    nothing here (the code under test records its own census entry for it)
    but counts the call, so a test can tell a count from a scan.
    """

    def __init__(self, db, name, field=None, values=None):
        self._db, self._name = db, name
        self._field, self._values = field, values

    def where(self, field, op, values):
        return _Group(self._db, self._name, field, list(values))

    def _matches(self):
        out = []
        for path, data in list(self._db.data.items()):
            if len(path) < 2 or path[-2] != self._name:
                continue
            if self._field is not None and (data or {}).get(self._field) not in self._values:
                continue
            out.append((path, data))
        return out

    def stream(self):
        self._db.streams += 1
        if self._db.scan_fail:
            raise RuntimeError("429 Quota exceeded")
        for path, data in self._matches():
            self._db.docs_returned += 1
            if self._db.on_stream_doc is not None:
                self._db.on_stream_doc()
            yield _Snap(path, data)

    def count(self):
        group = self

        class _Q:
            def get(self_inner):
                group._db.counts += 1
                if group._db.count_fail:
                    raise RuntimeError("count unavailable")
                return [[_Agg(len(group._matches()))]]

        return _Q()


class _DB:
    def __init__(self):
        self.data: dict = {}
        self.docs_returned = 0
        self.writes = 0
        self.streams = 0
        self.counts = 0
        self.scan_fail = False
        self.count_fail = False
        self.on_stream_doc = None

    def collection(self, name):
        return _Coll(self, (name,))

    def collection_group(self, name):
        return _Group(self, name)


def _key_doc(api_key: str, dek: bytes = b"wrapped", secret: bytes = b"ct") -> dict:
    now = datetime.now(timezone.utc)
    return {
        "encrypted_secret_b64": base64.b64encode(secret).decode(),
        "encrypted_dek_b64": base64.b64encode(dek).decode(),
        "api_key_full": api_key,
        "key_public_id_first8": api_key[:8],
        "ip_whitelist_ok": True,
        "withdraw_disabled_ok": True,
        "connected_at": now,
        "last_validated_at": now,
    }


@pytest.fixture(autouse=True)
def _clean(monkeypatch):
    for mod in (reads, gen, fk, ps, kms_client):
        mod.reset_for_test()
    gen.set_client_for_test(None)
    fail_open.reset()
    monkeypatch.setattr(fk, "_BLOB_CACHE_TTL_S", 3600.0)
    yield
    for mod in (reads, gen, fk, ps, kms_client):
        mod.reset_for_test()
    fail_open.reset()


# ---------------------------------------------------------------------------
# 1. The key-blob generation: never 0 -> N twice
# ---------------------------------------------------------------------------


def test_the_key_blob_generation_starts_at_an_epoch_not_zero():
    r = _FakeRedis()
    gen.set_client_for_test(r)
    g = gen.current(gen.DOC_KEY_BLOBS)
    assert g is not None and g > 10**12, "must be seeded to epoch-ms, not 0"


def test_a_flushed_redis_cannot_replay_a_generation_the_cache_already_holds(
    monkeypatch,
):
    """The on-demand reader never sees the intermediate zero.  Counting from
    zero, a flush plus the same number of bumps would read "unchanged" and
    serve a blob signed under a rotated key.

    Seeded from epoch-ms, a collision would need more key writes before the
    flush than milliseconds between the seed and the flush — the clock is
    advanced by one second here, the fastest a Redis restart plausibly is.
    """
    clock = [1_790_000_000.0]
    monkeypatch.setattr(gen.time, "time", lambda: clock[0])
    r = _FakeRedis()
    gen.set_client_for_test(r)
    for _ in range(5):
        gen.bump(gen.DOC_KEY_BLOBS)
    held = gen.current(gen.DOC_KEY_BLOBS)
    clock[0] += 1.0
    r.flushall()
    for _ in range(5):
        gen.bump(gen.DOC_KEY_BLOBS)
    assert gen.current(gen.DOC_KEY_BLOBS) != held


def test_zero_based_counting_would_have_replayed_it():
    """The defect the seed exists for, shown on the polled documents' own
    zero-based counter: flush, same number of bumps, same value."""
    r = _FakeRedis()
    gen.set_client_for_test(r)
    for _ in range(5):
        gen.bump(gen.DOC_KILL_SWITCH)
    held = r.store[gen.KEY_PREFIX + gen.DOC_KILL_SWITCH]
    r.flushall()
    for _ in range(5):
        gen.bump(gen.DOC_KILL_SWITCH)
    assert r.store[gen.KEY_PREFIX + gen.DOC_KILL_SWITCH] == held


def test_polled_documents_keep_their_zero_based_counter():
    """Only the on-demand document is seeded; the polled ones are watched
    every 5s and see a flush as a move backwards, so they are unchanged."""
    r = _FakeRedis()
    gen.set_client_for_test(r)
    gen.bump(gen.DOC_KILL_SWITCH)
    assert r.store[gen.KEY_PREFIX + gen.DOC_KILL_SWITCH] == 1


def test_an_unreadable_generation_is_none_never_zero():
    r = _FakeRedis()
    r.fail = True
    gen.set_client_for_test(r)
    assert gen.current(gen.DOC_KEY_BLOBS) is None


def test_bump_reports_whether_it_landed():
    r = _FakeRedis()
    gen.set_client_for_test(r)
    assert gen.bump(gen.DOC_KEY_BLOBS) is True
    r.fail = True
    assert gen.bump(gen.DOC_KEY_BLOBS) is False


# ---------------------------------------------------------------------------
# 2. The ciphertext cache in the signing service
# ---------------------------------------------------------------------------


def _keyed_db(*uids: str, api_key: str = "K-OLD") -> _DB:
    db = _DB()
    for uid in uids:
        db.data[("users", uid, "binance_key", "current")] = _key_doc(api_key)
    fk._db = db
    return db


def test_repeat_signed_calls_cost_one_read_while_the_generation_holds():
    gen.set_client_for_test(_FakeRedis())
    db = _keyed_db("u1")
    for _ in range(50):
        fk.get_key_blob_cached("u1")
    assert db.docs_returned == 1, (
        "one read per SIGNED CALL is the line that grew with members; "
        "fifty calls on an unchanged key must cost one"
    )
    assert fk.blob_cache_stats()["hits"] == 49


def test_a_key_write_in_another_process_invalidates_the_signing_cache():
    """The rotation case.  The api container writes; the signing service's
    next call must read the new blob, not the one it cached."""
    r = _FakeRedis()
    gen.set_client_for_test(r)
    db = _keyed_db("u1", api_key="K-OLD")
    assert fk.get_key_blob_cached("u1").api_key_full == "K-OLD"

    # The api container: new blob + bump (a different process's cache is not
    # touched locally, so simulate it by writing the doc and bumping Redis).
    db.data[("users", "u1", "binance_key", "current")] = _key_doc("K-NEW")
    gen.bump(gen.DOC_KEY_BLOBS)

    assert fk.get_key_blob_cached("u1").api_key_full == "K-NEW"


def test_put_key_blob_bumps_the_generation():
    r = _FakeRedis()
    gen.set_client_for_test(r)
    _keyed_db()
    before = gen.current(gen.DOC_KEY_BLOBS)
    fk.put_key_blob(
        "u1", encrypted_secret=b"s", encrypted_dek=b"d", api_key_full="K-X",
        ip_whitelist_ok=True, withdraw_disabled_ok=True,
    )
    assert gen.current(gen.DOC_KEY_BLOBS) != before


def test_delete_key_blob_bumps_the_generation():
    r = _FakeRedis()
    gen.set_client_for_test(r)
    _keyed_db("u1")
    before = gen.current(gen.DOC_KEY_BLOBS)
    fk.delete_key_blob("u1")
    assert gen.current(gen.DOC_KEY_BLOBS) != before


def test_an_unreadable_generation_bypasses_the_cache_entirely():
    """Slower, never stale: with Redis down there is no way to know a key
    was rotated, so no cached blob is trusted."""
    r = _FakeRedis()
    gen.set_client_for_test(r)
    db = _keyed_db("u1")
    fk.get_key_blob_cached("u1")
    r.fail = True
    for _ in range(5):
        fk.get_key_blob_cached("u1")
    assert db.docs_returned == 6
    assert fk.blob_cache_stats()["bypassed"] == 5


def test_no_redis_configured_means_every_call_reads_through():
    db = _keyed_db("u1")
    for _ in range(3):
        fk.get_key_blob_cached("u1")
    assert db.docs_returned == 3


def test_the_ttl_is_a_floor_for_a_dropped_bump(monkeypatch):
    gen.set_client_for_test(_FakeRedis())
    db = _keyed_db("u1")
    clock = [1000.0]
    monkeypatch.setattr(fk.time, "monotonic", lambda: clock[0])
    fk.get_key_blob_cached("u1")
    clock[0] += 3599.0
    fk.get_key_blob_cached("u1")
    assert db.docs_returned == 1
    clock[0] += 2.0
    fk.get_key_blob_cached("u1")
    assert db.docs_returned == 2


def test_a_zero_ttl_disables_the_cache(monkeypatch):
    gen.set_client_for_test(_FakeRedis())
    monkeypatch.setattr(fk, "_BLOB_CACHE_TTL_S", 0.0)
    db = _keyed_db("u1")
    for _ in range(3):
        fk.get_key_blob_cached("u1")
    assert db.docs_returned == 3


def test_a_bump_that_never_lands_is_retried_and_paged_not_swallowed(monkeypatch):
    r = _FakeRedis()
    gen.set_client_for_test(r)
    _keyed_db()
    gen.current(gen.DOC_KEY_BLOBS)          # seed while Redis is up
    r.fail = True
    monkeypatch.setattr(fk.time, "sleep", lambda _s: None)
    fk.put_key_blob(
        "u1", encrypted_secret=b"s", encrypted_dek=b"d", api_key_full="K-X",
        ip_whitelist_ok=True, withdraw_disabled_ok=True,
    )
    assert gen.stats()["bump_failures"] == 3
    snap = fail_open.snapshot()
    assert "keystore.key_blob_bump" in json.dumps(snap), (
        "a dropped key-blob bump leaves the signing service on the old key "
        "for up to a TTL — it must count and page"
    )


# ---------------------------------------------------------------------------
# 3. The signing handler: a rejected cached key is re-read once
# ---------------------------------------------------------------------------


def _blob(api_key: str, secret_ct: bytes, wrapped: bytes) -> fk.UserKeyBlob:
    now = datetime.now(timezone.utc)
    return fk.UserKeyBlob(
        uid="u1", encrypted_secret=secret_ct, encrypted_dek=wrapped,
        api_key_full=api_key, key_public_id_first8=api_key[:8],
        ip_whitelist_ok=True, withdraw_disabled_ok=True,
        connected_at=now, last_validated_at=now,
    )


def _request():
    return protocol.SignRequest(
        id="r1", verb="binance_signed_get", firebase_uid="u1",
        base="futures", path="/fapi/v2/positionRisk",
    )


def _crypto():
    dek = envelope_crypto.generate_dek()
    ct = envelope_crypto.encrypt_secret(dek, b"the-secret").raw
    fake_kms = MagicMock()
    fake_kms.decrypt.return_value = dek
    kms_client._client = fake_kms
    return ct


@pytest.mark.asyncio
async def test_a_rotated_key_served_stale_is_retried_once_with_the_fresh_blob():
    ct = _crypto()
    stale = _blob("K-OLD", ct, b"w-old")
    fresh = _blob("K-NEW", ct, b"w-new")
    signed = AsyncMock(side_effect=[
        (401, {"code": -2015, "msg": "Invalid API-key"}, None),
        (200, [{"symbol": "BTCUSDT"}], None),
    ])
    with patch.object(fk, "get_key_blob_cached", return_value=stale), \
         patch.object(fk, "get_key_blob", return_value=fresh), \
         patch.object(handler, "_signed_call", signed):
        resp = await handler.handle_request(_request())
    assert resp.ok is True
    assert signed.await_count == 2
    assert signed.await_args_list[1].kwargs["api_key"] == "K-NEW"


@pytest.mark.asyncio
async def test_a_genuinely_bad_key_is_not_retried():
    """Same blob on file: retrying would only double the rejection."""
    ct = _crypto()
    same = _blob("K-OLD", ct, b"w-old")
    signed = AsyncMock(return_value=(401, {"code": -2015, "msg": "x"}, None))
    with patch.object(fk, "get_key_blob_cached", return_value=same), \
         patch.object(fk, "get_key_blob", return_value=same), \
         patch.object(handler, "_signed_call", signed):
        resp = await handler.handle_request(_request())
    assert resp.ok is False
    assert signed.await_count == 1


@pytest.mark.asyncio
async def test_a_non_key_rejection_is_never_retried():
    """-2019 (margin) executed nothing wrong with the key; a retry with a
    different blob would be a second order attempt."""
    ct = _crypto()
    stale = _blob("K-OLD", ct, b"w-old")
    fresh = _blob("K-NEW", ct, b"w-new")
    signed = AsyncMock(return_value=(400, {"code": -2019, "msg": "margin"}, None))
    with patch.object(fk, "get_key_blob_cached", return_value=stale), \
         patch.object(fk, "get_key_blob", return_value=fresh), \
         patch.object(handler, "_signed_call", signed):
        await handler.handle_request(_request())
    assert signed.await_count == 1


# ---------------------------------------------------------------------------
# 4. The roster: a failed scan is not an empty roster; the rebuild is gated
# ---------------------------------------------------------------------------


def test_a_failed_scan_is_never_persisted_as_an_empty_roster():
    """2 Sep: reads refused, writes allowed.  Persisting ``[]`` would have
    fanned every signal out to zero users until the next good rebuild."""
    db = _keyed_db("u1", "u2")
    db.scan_fail = True
    assert fk.list_active_uids() == []
    assert ("control", "active_uids") not in db.data
    with pytest.raises(RuntimeError):
        fk.rebuild_active_roster()
    assert ("control", "active_uids") not in db.data
    assert fk.roster_rebuild_stats()["scan_failures"] == 1


def test_a_failed_rebuild_leaves_a_good_roster_in_place():
    db = _keyed_db("u1", "u2")
    assert fk.rebuild_active_roster() == 2
    db.scan_fail = True
    with pytest.raises(RuntimeError):
        fk.rebuild_active_roster(force=True)
    assert db.data[("control", "active_uids")]["uids"] == ["u1", "u2"]


def test_the_roster_rebuild_counts_instead_of_scanning_when_nothing_moved():
    db = _keyed_db(*[f"u{i}" for i in range(1000)])
    assert fk.rebuild_active_roster() == 1000        # boot: full scan
    fk.invalidate_roster()
    scanned = db.docs_returned
    for _ in range(10):
        fk.rebuild_active_roster()
    assert db.streams == 1, "an agreeing count must not scan"
    assert db.counts == 10
    # Ten checks: ten roster-doc reads at most, never 10 x 1,000.
    assert db.docs_returned - scanned <= 10


def test_a_disagreeing_count_forces_the_full_scan():
    db = _keyed_db("u1", "u2")
    fk.rebuild_active_roster()
    # A key written without the writer (out-of-band tooling).
    db.data[("users", "u3", "binance_key", "current")] = _key_doc("K")
    fk.invalidate_roster()
    assert fk.rebuild_active_roster() == 3
    assert db.streams == 2


def test_an_unavailable_count_falls_back_to_the_scan():
    db = _keyed_db("u1")
    fk.rebuild_active_roster()
    db.count_fail = True
    fk.invalidate_roster()
    fk.rebuild_active_roster()
    assert db.streams == 2


def test_a_full_scan_is_forced_when_due_even_if_the_count_agrees(monkeypatch):
    """A swap (one key added, another removed, both bypassing the writers)
    leaves the count equal — the periodic full scan bounds how long."""
    db = _keyed_db("u1")
    clock = [0.0]
    monkeypatch.setattr(fk.time, "monotonic", lambda: clock[0])
    fk.rebuild_active_roster()
    clock[0] += fk._ROSTER_FULL_REBUILD_SEC + 1
    fk.invalidate_roster()
    fk.rebuild_active_roster()
    assert db.streams == 2


def test_the_roster_count_is_on_the_census_as_a_flat_site():
    _keyed_db("u1")
    fk.rebuild_active_roster()
    fk.invalidate_roster()
    fk.rebuild_active_roster()
    sites = {s["site"] for s in reads.snapshot()["sites"]}
    assert "keystore.roster_count" in sites
    assert reads._scales_with_members("keystore.roster_count") is False


# ---------------------------------------------------------------------------
# 5. The position-index resync: count-gated, and a write during it survives
# ---------------------------------------------------------------------------


def _pos(uid, sid, state="OPEN"):
    return ps.Position(
        signal_id=sid, firebase_uid=uid, symbol="BTCUSDT", side="LONG",
        state=ps.PositionState(state), entry_price_target=100.0,
        entry_price_filled=100.0, sl_price=95.0, tp1_price=105.0,
        tp2_price=110.0, tp3_price=115.0, total_qty=1.0, tp1_qty=0.3,
        tp2_qty=0.4, tp3_qty=0.3,
    )


def _indexed_db(n_users: int, per_user: int) -> _DB:
    db = _DB()
    ps._db = db
    for u in range(n_users):
        for s in range(per_user):
            p = _pos(f"u{u}", f"s{s}")
            db.data[("users", p.firebase_uid, "positions", p.signal_id)] = (
                ps._to_firestore_dict(p)
            )
    ps.enable_position_index()
    return db


def test_the_resync_counts_instead_of_rescanning_an_exact_index():
    """~860k reads a day at 1,000 members holding three each, to re-confirm
    an index its only writer keeps exact."""
    db = _indexed_db(1000, 3)
    ps.resync_index()                        # first resync is a full scan
    base_streams, base_docs = db.streams, db.docs_returned
    for _ in range(12):                      # an hour of 5-minute cycles
        ps.resync_index()
    assert db.streams == base_streams, "an agreeing count must not rescan"
    assert db.docs_returned == base_docs
    assert db.counts == 12
    assert ps.resync_stats()["count_agreed"] == 12


def test_a_drifted_index_is_rebuilt():
    db = _indexed_db(2, 1)
    ps.resync_index()
    p = _pos("u9", "s9")
    db.data[("users", "u9", "positions", "s9")] = ps._to_firestore_dict(p)
    ps.resync_index()
    assert {q.signal_id for q in ps.list_positions_for_user("u9")} == {"s9"}


def test_a_position_opened_during_the_scan_is_not_dropped_from_the_index():
    """The scan runs lock-free while the event loop keeps writing.  The old
    code replaced the index with the scan's result, so a position opened
    mid-scan vanished from it — invisible to the pre-TP dispatcher and the
    trail governor for up to a period."""
    db = _indexed_db(1, 1)
    opened = _pos("u7", "s-new")

    def _write_mid_scan():
        if db.on_stream_doc is not None:
            db.on_stream_doc = None
            ps.put_position(opened)
            # Firestore already returned its page: the new doc is not in it.

    db.on_stream_doc = _write_mid_scan
    ps.resync_index(force=True)
    assert ps.get_position("u7", "s-new") is opened


def test_a_position_closed_during_the_scan_does_not_come_back_as_live():
    db = _indexed_db(1, 2)
    victim = ps.get_position("u0", "s1")

    def _close_mid_scan():
        if db.on_stream_doc is not None:
            db.on_stream_doc = None
            victim.state = ps.PositionState.CLOSED
            ps.put_position(victim)

    db.on_stream_doc = _close_mid_scan
    ps.resync_index(force=True)
    assert {p.signal_id for p in ps.list_positions_for_user("u0")} == {"s0"}


def test_a_failed_resync_scan_keeps_the_index():
    db = _indexed_db(1, 2)
    db.scan_fail = True
    ps.resync_index(force=True)
    assert len(ps.list_positions_for_user("u0")) == 2


# ---------------------------------------------------------------------------
# 6. The census covers the project, not the process
# ---------------------------------------------------------------------------


def test_a_peer_census_is_published_and_summed():
    r = _FakeRedis()
    gen.set_client_for_test(r)
    reads.record("keystore.get_key_blob", 7)
    assert reads.publish("signing", {"blob_cache": {"hits": 3}}) is True
    key = reads.PEER_KEY_PREFIX + "signing"
    assert r.ttls[key] == reads.PEER_TTL_SEC
    got = reads.peers()
    assert got["_readable"] is True
    assert got["signing"]["blob_cache"] == {"hits": 3}
    total = reads.project_total_per_day()
    assert "signing" in total["by_process"]
    assert total["peers_readable"] is True


def test_the_budget_probe_counts_reads_in_other_processes(monkeypatch):
    """Firestore's allowance is per PROJECT.  The signing service reading
    60k/day must page even though the engine itself reads almost nothing."""
    r = _FakeRedis()
    gen.set_client_for_test(r)
    peer = {"total_per_day": 60000, "sites": [], "process_role": "signing"}
    r.set(reads.PEER_KEY_PREFIX + "signing", json.dumps(peer))
    monkeypatch.setattr(
        reads, "snapshot",
        lambda: {"total_per_day": 10, "sites": [], "process_role": "engine",
                 "uptime_is_short": False},
    )
    ok, detail = reads.budget_health()
    assert ok is False
    assert "signing" in detail


def test_unreadable_peers_are_named_not_read_as_zero(monkeypatch):
    r = _FakeRedis()
    r.fail = True
    gen.set_client_for_test(r)
    monkeypatch.setattr(
        reads, "snapshot",
        lambda: {"total_per_day": 10, "sites": [], "process_role": "engine",
                 "uptime_is_short": False},
    )
    ok, detail = reads.budget_health()
    assert ok is True
    assert "other processes unreadable" in detail


def test_the_projection_does_not_count_its_own_process_twice(monkeypatch):
    from src import diag_catalog

    r = _FakeRedis()
    gen.set_client_for_test(r)
    own = reads.snapshot()["process_role"]
    r.set(reads.PEER_KEY_PREFIX + own, json.dumps(reads.snapshot()))
    r.set(reads.PEER_KEY_PREFIX + "signing", json.dumps(
        {**reads.snapshot(), "process_role": "signing"}))
    out = diag_catalog._firestore_projection(SimpleNamespace(args={}))
    assert set(out["other_processes"]) == {"signing"}


# ---------------------------------------------------------------------------
# 7. The deployment can actually reach the channel the cache trusts
# ---------------------------------------------------------------------------


def test_the_signing_container_is_given_the_in_network_redis_url():
    """.env's REDIS_URL is localhost, which inside the signing container is
    not Redis.  Without an explicit override the cache bypasses itself on
    every call — never stale, never saving a read — and the census never
    leaves the process.  Nothing would look broken."""
    import pathlib

    import yaml

    root = pathlib.Path(__file__).resolve().parents[1]
    compose = yaml.safe_load((root / "docker-compose.yml").read_text())
    svc = compose["services"]["signing_service"]
    env = svc.get("environment") or []
    engine_env = compose["services"]["engine"].get("environment") or []
    redis_url = [e for e in env if str(e).startswith("REDIS_URL=")]
    engine_url = [e for e in engine_env if str(e).startswith("REDIS_URL=")]
    assert redis_url and redis_url == engine_url
    assert "redis" not in (svc.get("depends_on") or []), (
        "signing must not wait on Redis — with Redis down the cache reads "
        "through, and orders must still be signable"
    )


def test_the_read_gates_are_on_the_diag_console():
    """Dark work must be observable: the owner reads whether the gates are
    saving reads on ``read.firestore_reads``, not in a PR body."""
    from src import diag_catalog

    r = _FakeRedis()
    gen.set_client_for_test(r)
    reads.publish("signing", {"gates": {"key_blob_cache": {"hits": 9}}})
    out = diag_catalog._firestore_reads(SimpleNamespace(args={}))
    gates = out["read_gates"]
    local = gates["local"]
    assert {"count_checks", "count_agreed", "full_scans"} <= set(
        local["position_index_resync"])
    assert "scan_failures" in local["active_roster_rebuild"]
    assert "bypassed" in local["key_blob_cache"]
    signing = gates["peers"]["signing"]
    assert signing["gates"] == {"key_blob_cache": {"hits": 9}}
    assert signing["published_at"] is not None
    assert gates["peers_readable"] is True


def test_an_unpublished_peer_is_absent_not_zero():
    from src import diag_catalog

    gen.set_client_for_test(_FakeRedis())
    out = diag_catalog._firestore_reads(SimpleNamespace(args={}))
    assert out["read_gates"]["peers"] == {}
    assert out["read_gates"]["peers_readable"] is True


def test_the_signing_service_publishes_its_gates_not_its_secrets():
    """The census leaves the signing container through Redis.  Pin what it
    carries: counters only — never a blob, never key material."""
    import ast
    import inspect

    from src.security.signing_service import server

    src = inspect.getsource(server.run)
    assert '"gates": _fsr.local_gates()' in src
    tree = ast.parse(src.lstrip() if src.startswith(" ") else src)
    published = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Attribute) and n.attr == "publish"
    ]
    assert len(published) == 1
    for name, fn in reads._gate_providers.items():
        out = json.dumps(fn())
        for forbidden in ("encrypted", "secret", "api_key", "dek"):
            assert forbidden not in out.lower(), (name, forbidden)
