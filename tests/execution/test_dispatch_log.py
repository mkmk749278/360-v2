"""Tests for src.execution.dispatch_log.

Pins:

* ``init_dispatch_log`` is idempotent + singleton-style.
* ``record_placed`` writes a doc shape readable by the API layer.
* ``record_rejected`` carries the typed exception class + the
  Binance code/msg extracted from the SignResponse body.
* Soft-fail: a Firestore exception inside record_* must NEVER
  bubble up to the caller (FSM's placed/rejected outcome is
  what matters; visibility is best-effort).
* ``list_recent_events`` returns DESC by timestamp + caps at the
  ``_MAX_LIMIT`` constant + skips malformed docs.
* Pre-init reads + writes are safe no-ops.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.execution import dispatch_log


@pytest.fixture(autouse=True)
def _reset():
    dispatch_log.reset_for_test()
    yield
    dispatch_log.reset_for_test()


# ---------------------------------------------------------------------------
# init / singleton
# ---------------------------------------------------------------------------


def test_init_is_idempotent() -> None:
    fake_db1 = MagicMock(name="db1")
    fake_db2 = MagicMock(name="db2")
    dispatch_log.init_dispatch_log(fake_db1)
    assert dispatch_log.is_initialised()
    # Second call doesn't replace the first.
    dispatch_log.init_dispatch_log(fake_db2)
    assert dispatch_log._db is fake_db1


def test_uninitialised_writes_are_safe_noops() -> None:
    """No Firestore client wired — record_* must not raise."""
    dispatch_log.record_placed(
        firebase_uid="fb-x", signal_id="s1", symbol="BTCUSDT",
        direction="LONG", entry_price=29000.0, total_qty=0.017,
    )
    dispatch_log.record_rejected(
        firebase_uid="fb-x", signal_id="s1", symbol="BTCUSDT",
        direction="LONG", entry_price=29000.0,
        reject_class="OrderRejectedByBinance",
        reject_detail="something went wrong",
    )


def test_uninitialised_reads_return_empty() -> None:
    assert dispatch_log.list_recent_events("fb-x") == []


# ---------------------------------------------------------------------------
# Write path — record_placed + record_rejected
# ---------------------------------------------------------------------------


def _install_fake_db() -> MagicMock:
    """Build the Firestore 4-level mock chain — same shape as
    test_position_state's helper.  Returns the leaf doc mock so
    individual tests can inspect ``.set.call_args``."""
    fake_doc = MagicMock(name="event_doc")
    fake_events = MagicMock()
    fake_events.document.return_value = fake_doc
    fake_user_doc = MagicMock()
    fake_user_doc.collection.return_value = fake_events
    fake_users = MagicMock()
    fake_users.document.return_value = fake_user_doc
    fake_db = MagicMock()
    fake_db.collection.return_value = fake_users
    dispatch_log.init_dispatch_log(fake_db)
    return fake_doc


def test_record_placed_writes_minimal_shape() -> None:
    doc = _install_fake_db()
    dispatch_log.record_placed(
        firebase_uid="fb-x", signal_id="sig-A", symbol="BTCUSDT",
        direction="LONG", entry_price=29000.0, total_qty=0.017,
    )
    doc.set.assert_called_once()
    payload = doc.set.call_args[0][0]
    assert payload["firebase_uid"] == "fb-x"
    assert payload["signal_id"] == "sig-A"
    assert payload["symbol"] == "BTCUSDT"
    assert payload["direction"] == "LONG"
    assert payload["outcome"] == "placed"
    assert payload["entry_price"] == 29000.0
    assert payload["total_qty"] == 0.017
    assert "timestamp" in payload
    assert isinstance(payload["timestamp"], datetime)


def test_record_rejected_carries_binance_code_and_msg() -> None:
    doc = _install_fake_db()
    dispatch_log.record_rejected(
        firebase_uid="fb-x", signal_id="sig-B", symbol="PROMUSDT",
        direction="SHORT", entry_price=0.1278,
        reject_class="OrderRejectedByBinance",
        reject_detail=(
            "order placement failed (phase=entry): "
            "code=BINANCE_HTTP_ERROR status=400 "
            "message=Binance returned 400 (code=-2019 msg='Margin is insufficient.')"
        ),
        reject_binance_code=-2019,
        reject_binance_msg="Margin is insufficient.",
    )
    payload = doc.set.call_args[0][0]
    assert payload["outcome"] == "rejected"
    assert payload["reject_class"] == "OrderRejectedByBinance"
    assert payload["reject_binance_code"] == -2019
    assert payload["reject_binance_msg"] == "Margin is insufficient."
    # Detail preserves the full str(exc) so engine-side debugging
    # still has the original message.
    assert "-2019" in payload["reject_detail"]


def test_record_rejected_handles_missing_binance_code() -> None:
    """Tripwire rejections (SymbolNotAllowed, etc.) don't come from
    Binance — they have no binance_code/msg.  Doc should still
    write cleanly with those fields set to None."""
    doc = _install_fake_db()
    dispatch_log.record_rejected(
        firebase_uid="fb-x", signal_id="sig-C", symbol="DOGEUSDT",
        direction="LONG", entry_price=0.08,
        reject_class="SymbolNotInUserPreference",
        reject_detail="symbol 'DOGEUSDT' is not in user fb-x's symbol preference (pref size: 3)",
    )
    payload = doc.set.call_args[0][0]
    assert payload["outcome"] == "rejected"
    assert payload["reject_class"] == "SymbolNotInUserPreference"
    assert payload["reject_binance_code"] is None
    assert payload["reject_binance_msg"] is None


def test_record_placed_soft_fails_on_firestore_exception() -> None:
    """A Firestore write exception MUST NOT raise to the caller —
    the dispatch path's success contract is what matters; visibility
    is best-effort."""
    doc = _install_fake_db()
    doc.set.side_effect = RuntimeError("firestore offline")
    # No raise expected.
    dispatch_log.record_placed(
        firebase_uid="fb-x", signal_id="s1", symbol="BTCUSDT",
        direction="LONG", entry_price=29000.0, total_qty=0.017,
    )


def test_record_rejected_soft_fails_on_firestore_exception() -> None:
    doc = _install_fake_db()
    doc.set.side_effect = RuntimeError("firestore offline")
    dispatch_log.record_rejected(
        firebase_uid="fb-x", signal_id="s1", symbol="BTCUSDT",
        direction="LONG", entry_price=29000.0,
        reject_class="X", reject_detail="boom",
    )


# ---------------------------------------------------------------------------
# Read path — list_recent_events
# ---------------------------------------------------------------------------


def _install_fake_db_with_stream(snaps: list) -> MagicMock:
    """Build the 3-level mock chain for read queries.  ``snaps`` is
    a list of doc-snapshot mocks the ``stream()`` call returns."""
    fake_query = MagicMock()
    fake_query.stream.return_value = iter(snaps)
    fake_events = MagicMock()
    fake_events.order_by.return_value.limit.return_value = fake_query
    fake_events.limit.return_value = fake_query
    fake_user_doc = MagicMock()
    fake_user_doc.collection.return_value = fake_events
    fake_users = MagicMock()
    fake_users.document.return_value = fake_user_doc
    fake_db = MagicMock()
    fake_db.collection.return_value = fake_users
    dispatch_log.init_dispatch_log(fake_db)
    return fake_query


def _make_snap(event_id: str, outcome: str, ts: datetime, symbol: str = "BTCUSDT"):
    return SimpleNamespace(
        id=event_id,
        to_dict=lambda: {
            "event_id": event_id,
            "firebase_uid": "fb-x",
            "signal_id": "sig-" + event_id,
            "symbol": symbol,
            "direction": "LONG",
            "outcome": outcome,
            "timestamp": ts,
            "entry_price": 29000.0,
            "total_qty": 0.017 if outcome == "placed" else 0.0,
        },
    )


def test_list_recent_events_returns_in_desc_timestamp_order() -> None:
    now = datetime.now(timezone.utc)
    _install_fake_db_with_stream([
        _make_snap("a", "placed", now - timedelta(minutes=3)),
        _make_snap("b", "rejected", now - timedelta(minutes=1)),
        _make_snap("c", "placed", now - timedelta(minutes=10)),
    ])
    events = dispatch_log.list_recent_events("fb-x", limit=10)
    assert [e.event_id for e in events] == ["b", "a", "c"]


def test_list_recent_events_caps_limit() -> None:
    """Even when caller passes limit=1000, the read is capped at
    _MAX_LIMIT.  Test by checking the query.limit was called with
    the cap, not 1000."""
    now = datetime.now(timezone.utc)
    fake_query = _install_fake_db_with_stream([
        _make_snap("a", "placed", now),
    ])
    # Re-grab the limit mock so we can inspect the args passed in.
    coll = dispatch_log._db.collection.return_value.document.return_value.collection.return_value
    dispatch_log.list_recent_events("fb-x", limit=1000)
    # The order_by().limit(cap) path is the production path; assert
    # the cap-value passed to ``.limit`` is _MAX_LIMIT (not 1000).
    coll.order_by.return_value.limit.assert_called_with(dispatch_log._MAX_LIMIT)


def test_list_recent_events_skips_empty_docs() -> None:
    """A doc with no payload is silently skipped — the rest still
    surface."""
    now = datetime.now(timezone.utc)
    empty = SimpleNamespace(id="empty", to_dict=lambda: None)
    good = _make_snap("a", "placed", now)
    _install_fake_db_with_stream([empty, good])
    events = dispatch_log.list_recent_events("fb-x")
    assert len(events) == 1
    assert events[0].event_id == "a"


def test_list_recent_events_soft_fails_on_query_exception() -> None:
    """A Firestore query exception returns [], not 5xx — matches
    the soft-failure stance of every other server-side read."""
    fake_query = MagicMock()
    fake_query.stream.side_effect = RuntimeError("firestore offline")
    fake_events = MagicMock()
    fake_events.order_by.return_value.limit.return_value = fake_query
    fake_user_doc = MagicMock()
    fake_user_doc.collection.return_value = fake_events
    fake_users = MagicMock()
    fake_users.document.return_value = fake_user_doc
    fake_db = MagicMock()
    fake_db.collection.return_value = fake_users
    dispatch_log.init_dispatch_log(fake_db)
    assert dispatch_log.list_recent_events("fb-x") == []
