"""The reads that grow with subscribers, and the indexes that stopped them.

The owner's auto-trade target is 1,000 members.  Every test here asserts a
COUNT of Firestore document reads, because that is the quantity that was never
measured: on 2026-09-02 the project spent 53,000 reads against a 50,000/day
allowance and every Firestore-backed path failed together — the keystore (so
every signal fanned out to zero users), the kill switch (so the emergency stop
503'd), the tunables and the dispatch log.

A read count is exactly the kind of property a unit test can pin and a code
review cannot: ``worker_manager`` called an uncached ``collection_group`` scan
once a minute for months, in a repo whose CLAUDE.md has a Cost Discipline
section, because nobody had counted it.
"""
from __future__ import annotations

import pytest

from src import control_generation as gen
from src import firestore_reads as reads
from src.execution import kill_switch as ks
from src.security import firestore_keystore as fk


# ---------------------------------------------------------------------------
# A minimal Firestore double that COUNTS reads the way Firestore bills them
# ---------------------------------------------------------------------------


class _Snap:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.exists = data is not None
        self.reference = None

    def to_dict(self):
        return dict(self._data or {})


class _Query:
    def __init__(self, db, docs):
        self._db = db
        self._docs = docs

    def where(self, field, op, value):
        return _Query(
            self._db,
            [d for d in self._docs if d.to_dict().get(field) == value],
        )

    def stream(self):
        self._db.docs_returned += len(self._docs)
        for d in self._docs:
            yield d


class _Doc:
    def __init__(self, db, path):
        self._db = db
        self._path = path

    def get(self):
        self._db.gets += 1
        self._db.docs_returned += 1
        return _Snap(self._path[-1], self._db.data.get(self._path))

    def set(self, payload, merge=False):
        self._db.writes += 1
        cur = dict(self._db.data.get(self._path) or {}) if merge else {}
        cur.update(payload)
        self._db.data[self._path] = cur

    def collection(self, name):
        return _Coll(self._db, self._path + (name,))


class _Coll:
    def __init__(self, db, path):
        self._db = db
        self._path = path

    def document(self, doc_id):
        return _Doc(self._db, self._path + (doc_id,))

    def where(self, field, op, value):
        docs = [
            _Snap(p[-1], d)
            for p, d in self._db.data.items()
            if len(p) == len(self._path) + 1 and p[:-1] == self._path
        ]
        return _Query(self._db, docs).where(field, op, value)


class _DB:
    """Counts ``docs_returned`` — Firestore's actual billing unit."""

    def __init__(self):
        self.data: dict = {}
        self.gets = 0
        self.writes = 0
        self.docs_returned = 0
        self.group_docs: list = []

    def collection(self, name):
        return _Coll(self, (name,))

    def collection_group(self, name):
        self.docs_returned += len(self.group_docs)
        return _Query(self, [])  # scan cost billed, no matches needed here


@pytest.fixture(autouse=True)
def _clean():
    reads.reset_for_test()
    gen.reset_for_test()
    gen.set_client_for_test(None)
    ks.reset_for_test()
    fk.reset_for_test()
    yield
    reads.reset_for_test()
    gen.reset_for_test()
    ks.reset_for_test()
    fk.reset_for_test()


# ---------------------------------------------------------------------------
# The kill-switch document: four flags, one read
# ---------------------------------------------------------------------------


def test_every_flag_on_the_document_shares_one_read():
    """Four accessors used to be able to take four reads of the same document.

    ``signal_expiry`` had its own cache slot with its own 5s TTL against a 5.0s
    monitor poll, and ``play_billing`` read straight through on every call —
    ~34,000 reads a day between them, on one document nobody was editing.
    """
    db = _DB()
    db.data[("kill_switch", "global")] = {
        "engaged": False,
        "auto_trade_globally_enabled": True,
        "signal_expiry_enabled": False,
        "play_billing_enabled": True,
    }
    c = ks.KillSwitchClient(db)
    assert c.is_global_engaged() is False
    assert c.is_globally_enabled() is True
    assert c.is_signal_expiry_enabled(True) is False
    assert c.is_billing_enabled(False) is True
    assert db.gets == 1, "four flags on one document must cost one read"


def test_the_flags_cache_is_not_bounded_by_the_monitor_poll_period():
    """The old TTL was 5.0s and ``MONITOR_POLL_INTERVAL`` is 5.0s, so the entry
    expired one tick before every read — a cache that could never hit.

    The floor is asserted against the poll period rather than against a
    literal, so lowering one without the other fails here instead of on a bill.
    """
    from config import MONITOR_POLL_INTERVAL

    assert ks._CACHE_TTL_S > MONITOR_POLL_INTERVAL * 10


def test_a_flip_bumps_the_generation_so_the_other_container_sees_it():
    """B18 requires under five seconds.  It used to be met by re-reading
    Firestore every 5s; it is now met by the write announcing itself."""

    class _R:
        def __init__(self):
            self.keys = []

        def incr(self, key):
            self.keys.append(key)
            return len(self.keys)

    r = _R()
    gen.set_client_for_test(r)
    db = _DB()
    c = ks.KillSwitchClient(db)
    c.engage_global(reason="test")
    assert gen.KEY_PREFIX + gen.DOC_KILL_SWITCH in r.keys


def test_a_read_failure_is_named_rather_than_rendered_as_not_engaged():
    """``initialised: false`` carried three worlds and ops turned it into a
    confident sentence about this deployment's credentials."""

    class _Boom(_DB):
        def collection(self, name):
            raise RuntimeError("429 RESOURCE_EXHAUSTED: Quota exceeded.")

    ks.init_kill_switch(_Boom())
    with pytest.raises(RuntimeError):
        ks.get_client().is_global_engaged()
    state, detail = ks.availability()
    assert state == ks.AVAIL_READ_FAILED
    assert "RESOURCE_EXHAUSTED" in (detail or "")


def test_no_client_is_a_different_state_from_a_failed_read():
    assert ks.availability() == (ks.AVAIL_NOT_CONFIGURED, None)


# ---------------------------------------------------------------------------
# Per-user disable: one document, not one per member
# ---------------------------------------------------------------------------


def test_the_disable_gate_costs_one_read_for_a_thousand_members():
    """This gate is consulted once per user per order attempt.  Per-user it is
    millions of reads a day at the target, for a field that is false for almost
    everybody almost always."""
    db = _DB()
    db.data[("control", "disabled_uids")] = {"uids": ["u7"]}
    c = ks.KillSwitchClient(db)
    for i in range(1000):
        assert c.is_user_disabled(f"u{i}") is (i == 7)
    assert db.gets == 1


def test_a_mirror_that_was_never_written_falls_back_and_does_not_answer_no():
    """An absent index and an index saying nobody is disabled are different
    facts.  Reading the first as the second would silently un-disable every
    tripped user — absence of knowledge is not permission."""
    db = _DB()
    db.data[("users", "u1")] = {"auto_trade_disabled": True}
    c = ks.KillSwitchClient(db)
    assert c.is_user_disabled("u1") is True, "must fall back to the user doc"


def test_a_truncated_mirror_is_treated_as_absent_not_as_empty():
    db = _DB()
    db.data[("control", "disabled_uids")] = {"updated_at": 1}   # no uids list
    db.data[("users", "u1")] = {"auto_trade_disabled": True}
    c = ks.KillSwitchClient(db)
    assert c.is_user_disabled("u1") is True


def test_disabling_a_user_updates_both_the_record_and_the_index():
    db = _DB()
    db.data[("control", "disabled_uids")] = {"uids": []}
    c = ks.KillSwitchClient(db)
    c.disable_user("u1", reason="breaker")
    assert db.data[("users", "u1")]["auto_trade_disabled"] is True
    assert db.data[("control", "disabled_uids")]["uids"] == ["u1"]
    assert c.is_user_disabled("u1") is True
    c.enable_user("u1")
    assert db.data[("control", "disabled_uids")]["uids"] == []
    assert c.is_user_disabled("u1") is False


# ---------------------------------------------------------------------------
# The active-key roster: the 1.44-million-reads-a-day line
# ---------------------------------------------------------------------------


def test_the_roster_costs_one_read_however_many_members_there_are():
    db = _DB()
    db.data[("control", "active_uids")] = {"uids": [f"u{i}" for i in range(1000)]}
    fk._db = db
    assert len(fk.list_active_uids()) == 1000
    assert db.docs_returned == 1, (
        "a collection_group scan bills one read PER DOCUMENT RETURNED — "
        "1,000 members means 1,000 reads per call, and worker_manager made "
        "that call every 60 seconds"
    )


def test_a_missing_roster_falls_back_to_the_scan_and_repairs_itself():
    """First boot after this shipped has no index: one caller pays for a scan,
    and nobody after them does."""
    db = _DB()
    db.group_docs = [object()] * 5
    fk._db = db
    fk.list_active_uids()
    assert db.docs_returned >= 5, "the fallback scan must actually run"
    assert ("control", "active_uids") in db.data, "and must write the index"


def test_worker_manager_uses_the_roster_and_never_the_raw_scan():
    """The loop that cost 1,440 scans a day.  Pinned by AST on the CALL SITE,
    because this repo has repeatedly shipped a helper nobody calls."""
    import ast
    import inspect

    from src.execution import worker_manager

    tree = ast.parse(inspect.getsource(worker_manager._tick))
    called = {
        n.func.attr
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
    }
    assert "list_active_uids" in called
    assert "_scan_active_uids" not in called


# ---------------------------------------------------------------------------
# The projection
# ---------------------------------------------------------------------------


def test_an_unknown_call_site_is_assumed_to_scale_with_members():
    """Safe direction: a flat site wrongly scaled overstates a bill somebody
    then checks; a per-user site wrongly called flat is invisible until the
    subscribers arrive, which is the failure this exists to prevent."""
    assert reads._scales_with_members("something.nobody.classified") is True
    assert reads._scales_with_members("kill_switch.global_doc") is False


def test_the_projection_charges_only_the_excess_over_the_free_allowance():
    """The first 50,000 reads are free EVERY DAY, so charging the whole figure
    would overstate a small overage by the entire allowance.

    Note the arithmetic is driven off ``projected_per_day`` rather than a fixed
    expectation: ``per_day`` extrapolates from this process's uptime, which in a
    test is under a second, so a literal here would be pinning the test
    harness's clock rather than the cost model.  That extrapolation is why
    ``uptime_is_short`` rides beside every reading.
    """
    reads.record("keystore.list_active_uids", 100)
    out = reads.project(members=1, current_members=1)
    assert out["uptime_is_short"] is True
    expected_over = max(
        out["projected_per_day"] - reads.FREE_TIER_READS_PER_DAY, 0
    )
    assert out["projected_over_free_tier"] == expected_over
    assert out["projected_usd_per_month_regional"] == round(
        expected_over / 100_000.0 * reads.PRICE_PER_100K_READS_REGIONAL * 30, 2
    )
    # And the multi-region tier is exactly twice the regional one, published
    # side by side because the project's location is a console fact.
    assert out["projected_usd_per_month_multi_region"] == pytest.approx(
        out["projected_usd_per_month_regional"] * 2, rel=1e-6
    )


def test_a_reading_below_the_allowance_costs_nothing():
    out = reads.project(members=1, current_members=1)   # no reads recorded
    assert out["projected_per_day"] == 0
    assert out["projected_over_free_tier"] == 0
    assert out["projected_usd_per_month_regional"] == 0.0


def test_the_projection_scales_the_per_member_sites_and_not_the_flat_ones():
    reads.record("keystore.list_active_uids", 10)
    reads.record("kill_switch.global_doc", 10)
    out = reads.project(members=100, current_members=1)
    by_site = {r["site"]: r for r in out["sites"]}
    assert by_site["keystore.list_active_uids"]["projected_per_day"] == (
        by_site["keystore.list_active_uids"]["per_day"] * 100
    )
    assert by_site["kill_switch.global_doc"]["projected_per_day"] == (
        by_site["kill_switch.global_doc"]["per_day"]
    )
