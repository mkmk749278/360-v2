"""``list_recent_closed_positions_for_user`` — bounded closed history.

The positions collection is never pruned, and this module's own comment
calls an unfiltered stream of it the dominant Firestore cost for the
collection.  ``list_positions_for_user(include_closed=True)`` is exactly
that stream, so the closed-outcome read the app needs could not reuse it.

Pinned:

* the query is ORDERED and LIMITED (never an unfiltered stream), and the
  ordering is on ``closed_at`` DESC — a single-field index, so it needs
  no composite index to be deployed alongside it;
* the limit is capped, because a "limited" query with no ceiling can
  still ask for the whole history;
* open positions (``closed_at is None``, which Firestore sorts last
  under DESC) are dropped by the terminal guard rather than reported as
  closed trades;
* a malformed document is skipped, not fatal.
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.execution import position_state as ps

NOW = datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _reset():
    ps.reset_for_test()
    yield
    ps.reset_for_test()


def _doc(signal_id: str, state: ps.PositionState, closed_at):
    pos = ps.Position(
        signal_id=signal_id,
        firebase_uid="fb-h",
        symbol="BTCUSDT",
        side="LONG",
        state=state,
        entry_price_target=100.0,
        entry_price_filled=101.0,
        sl_price=95.0,
        tp1_price=105.0,
        tp2_price=110.0,
        tp3_price=115.0,
        total_qty=1.0,
        tp1_qty=0.3,
        tp2_qty=0.4,
        tp3_qty=0.3,
        filled_qty=1.0,
        created_at=NOW,
        closed_at=closed_at,
        close_reason="TP1" if closed_at else "",
        realized_pnl_total=3.5 if closed_at else 0.0,
    )
    snap = MagicMock()
    snap.id = signal_id
    snap.to_dict.return_value = ps._to_firestore_dict(pos)
    return snap


def _install(snaps):
    """Firestore chain that records the query the caller built."""
    calls: dict = {}
    query = MagicMock()
    query.stream.return_value = list(snaps)

    def _limit(n):
        calls["limit"] = n
        return query

    ordered = MagicMock()
    ordered.limit.side_effect = _limit

    coll = MagicMock()

    def _order_by(field, **kw):
        calls["order_by"] = field
        calls["direction"] = kw.get("direction")
        return ordered

    coll.order_by.side_effect = _order_by
    user_doc = MagicMock()
    user_doc.collection.return_value = coll
    users = MagicMock()
    users.document.return_value = user_doc
    db = MagicMock()
    db.collection.return_value = users
    ps._db = db
    return calls, coll


def test_query_is_ordered_and_limited_never_an_unfiltered_stream() -> None:
    calls, coll = _install([_doc("a", ps.PositionState.CLOSED, NOW)])
    out = ps.list_recent_closed_positions_for_user("fb-h", limit=5)
    assert calls["order_by"] == "closed_at"
    assert calls["limit"] == 5
    coll.stream.assert_not_called()
    assert [p.signal_id for p in out] == ["a"]
    assert out[0].close_reason == "TP1"
    assert out[0].realized_pnl_total == 3.5


def test_limit_is_capped() -> None:
    calls, _ = _install([])
    ps.list_recent_closed_positions_for_user("fb-h", limit=10_000)
    assert calls["limit"] == ps._MAX_CLOSED_HISTORY


def test_limit_floor_is_one() -> None:
    calls, _ = _install([])
    ps.list_recent_closed_positions_for_user("fb-h", limit=0)
    assert calls["limit"] == 1


def test_open_positions_in_the_window_are_dropped_not_reported_closed() -> None:
    _install([
        _doc("open-1", ps.PositionState.OPEN, None),
        _doc("closed-1", ps.PositionState.CLOSED, NOW),
    ])
    out = ps.list_recent_closed_positions_for_user("fb-h")
    assert [p.signal_id for p in out] == ["closed-1"]


def test_malformed_doc_is_skipped_not_fatal() -> None:
    bad = MagicMock()
    bad.id = "bad"
    bad.to_dict.return_value = {"signal_id": "bad", "state": "NOT_A_STATE"}
    _install([bad, _doc("good", ps.PositionState.CLOSED, NOW)])
    out = ps.list_recent_closed_positions_for_user("fb-h")
    assert [p.signal_id for p in out] == ["good"]


def test_uninitialised_raises_rather_than_reading_empty() -> None:
    with pytest.raises(ps.PositionStateNotInitialisedError):
        ps.list_recent_closed_positions_for_user("fb-h")
