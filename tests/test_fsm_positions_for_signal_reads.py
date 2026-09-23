"""``get_fsm_positions_for_signal`` is a per-tick sweep, so it is pinned by a
COUNT of Firestore document reads, not by its return value alone.

TradeMonitor calls it once per open signal on every 5s tick.  It used to ask
``position_state.get_position`` once per active uid, and ``get_position`` can
only serve a HIT from the in-memory live index: every uid WITHOUT a live
position on the signal — every paper user, every user the signal never placed
for, i.e. the common case — fell through to a billed Firestore read.  The
engine's own census measured that at 102,882 reads/day at ONE member on
2026-09-23, twice the 50,000/day ceiling behind the 2 Sep outage.

The index holds every live position write-through, so an absent uid there is
an authoritative "no live position".  These tests assert zero reads while the
index serves, over a 1,000-member roster, and that the old per-uid path is
still the fallback (with its failures counted) while it does not.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src import fail_open
from src import firestore_reads
from src.execution import position_state as ps
from src.execution import signal_dispatch as sd


class _CountingDb:
    """Firestore double: counts every single-document ``.get()`` (one billed
    read each) and serves a fixed collection-group hydration."""

    def __init__(self, cg_docs, *, get_raises: Exception | None = None):
        self.doc_gets = 0
        self._get_raises = get_raises
        cg_query = MagicMock()
        cg_query.where.return_value = cg_query
        cg_query.stream.side_effect = lambda: iter(cg_docs)
        self.collection_group = MagicMock(return_value=cg_query)

    def collection(self, _name):
        return self

    def document(self, _id):
        return self

    def set(self, _data):
        return None

    def get(self):
        self.doc_gets += 1
        if self._get_raises is not None:
            raise self._get_raises
        return SimpleNamespace(exists=False, to_dict=lambda: {})


def _cg(uid: str, sid: str, state: str):
    return SimpleNamespace(
        id=sid,
        to_dict=lambda: {
            "signal_id": sid,
            "firebase_uid": uid,
            "symbol": "BTCUSDT",
            "state": state,
            "total_qty": 1.0,
            "created_at": datetime.now(timezone.utc),
            "last_event_at": datetime.now(timezone.utc),
        },
    )


ROSTER = [f"uid-{i:04d}" for i in range(1000)]


@pytest.fixture(autouse=True)
def _clean(monkeypatch):
    ps.reset_for_test()
    firestore_reads.reset_for_test()
    monkeypatch.setattr(sd, "_active_uids", lambda: list(ROSTER))
    yield
    ps.reset_for_test()


def _install(db) -> None:
    ps._db = db


def test_index_active_answers_a_thousand_member_roster_with_zero_reads():
    db = _CountingDb([_cg("uid-0007", "sig-1", "OPEN")])
    _install(db)
    ps.enable_position_index()
    assert ps.index_active()

    got = sd.get_fsm_positions_for_signal("sig-1")

    assert [(uid, pos.signal_id) for uid, pos in got] == [("uid-0007", "sig-1")]
    # The whole point: 999 members with no live position cost nothing.
    assert db.doc_gets == 0
    sites = {r["site"]: r for r in firestore_reads.snapshot()["sites"]}
    assert "position_state.get_position" not in sites


def test_every_non_terminal_state_is_returned_and_terminal_is_not():
    db = _CountingDb([
        _cg("uid-0001", "sig-1", "OPEN"),
        _cg("uid-0002", "sig-1", "PRE_TP_FIRED"),
        _cg("uid-0003", "sig-1", "CLOSED"),       # never enters the index
        _cg("uid-0004", "sig-other", "OPEN"),     # a different signal
    ])
    _install(db)
    ps.enable_position_index()

    got = {uid for uid, _ in sd.get_fsm_positions_for_signal("sig-1")}

    assert got == {"uid-0001", "uid-0002"}
    assert db.doc_gets == 0


def test_a_live_position_for_a_user_no_longer_active_is_excluded(monkeypatch):
    """Same filter the per-uid path applied: only users with a connected key."""
    db = _CountingDb([_cg("uid-gone", "sig-1", "OPEN"), _cg("uid-0005", "sig-1", "OPEN")])
    _install(db)
    ps.enable_position_index()

    got = [uid for uid, _ in sd.get_fsm_positions_for_signal("sig-1")]

    assert got == ["uid-0005"]


def test_result_order_follows_the_active_roster():
    db = _CountingDb([_cg("uid-0900", "sig-1", "OPEN"), _cg("uid-0002", "sig-1", "OPEN")])
    _install(db)
    ps.enable_position_index()

    got = [uid for uid, _ in sd.get_fsm_positions_for_signal("sig-1")]

    assert got == ["uid-0002", "uid-0900"]


def test_a_position_written_after_hydration_is_seen_without_a_read():
    db = _CountingDb([])
    _install(db)
    ps.enable_position_index()
    ps.put_position(ps.Position(
        signal_id="sig-2", firebase_uid="uid-0042", symbol="ETHUSDT", side="LONG",
        state=ps.PositionState.OPEN, entry_price_target=1.0, entry_price_filled=1.0,
        sl_price=0.9, tp1_price=1.1, tp2_price=1.2, tp3_price=1.3,
        total_qty=1.0, tp1_qty=1.0, tp2_qty=0.0, tp3_qty=0.0,
    ))

    got = [uid for uid, _ in sd.get_fsm_positions_for_signal("sig-2")]

    assert got == ["uid-0042"]
    assert db.doc_gets == 0


def test_index_inactive_falls_back_to_the_per_uid_read():
    """Boot hydration failed or a process never enabled the index: the old
    path is the only way to answer, and it still bills one read per uid."""
    db = _CountingDb([])
    _install(db)
    assert not ps.index_active()

    got = sd.get_fsm_positions_for_signal("sig-1")

    assert got == []
    assert db.doc_gets == len(ROSTER)


def test_a_failed_fallback_read_is_counted_not_swallowed(monkeypatch):
    """A quota refusal on this path used to vanish at log.debug."""
    db = _CountingDb([], get_raises=RuntimeError("429 Quota exceeded"))
    _install(db)
    monkeypatch.setattr(sd, "_active_uids", lambda: ["uid-0001", "uid-0002"])
    recorded = []
    monkeypatch.setattr(fail_open, "record", lambda site, exc, **_: recorded.append(site))

    assert sd.get_fsm_positions_for_signal("sig-1") == []
    assert recorded == [
        "signal_dispatch.get_fsm_positions_for_signal",
        "signal_dispatch.get_fsm_positions_for_signal",
    ]


def test_index_lookup_returns_none_while_inactive():
    """None means "cannot answer" — never "none live"."""
    _install(_CountingDb([]))
    assert ps.index_live_positions_for_signal("sig-1") is None


# ---------------------------------------------------------------------------
# firestore_read_budget — the probe that would have paged on this
# ---------------------------------------------------------------------------


def _age_census(monkeypatch, seconds: float) -> None:
    monkeypatch.setattr(firestore_reads, "_started_at", firestore_reads._started_at - seconds)


def test_budget_probe_pages_past_eighty_percent_of_the_ceiling(monkeypatch):
    _age_census(monkeypatch, 86400)
    firestore_reads.record("position_state.get_position", 102_882)

    ok, detail = firestore_reads.budget_health()

    assert ok is False
    assert "position_state.get_position" in detail
    assert "50,000/day" in detail


def test_budget_probe_is_quiet_under_the_line(monkeypatch):
    _age_census(monkeypatch, 86400)
    firestore_reads.record("keystore.roster_doc", 300)

    ok, _ = firestore_reads.budget_health()

    assert ok is True


def test_budget_probe_does_not_extrapolate_a_short_uptime(monkeypatch):
    """Ninety seconds of reads is not a daily rate; report OK and say why."""
    firestore_reads.record("position_state.get_position", 5_000)

    ok, detail = firestore_reads.budget_health()

    assert ok is True
    assert "uptime" in detail
