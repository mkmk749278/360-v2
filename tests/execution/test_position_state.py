"""Tests for src.execution.position_state.

Pinned:

* PositionState enum stores as string (Firestore-compatible).
* Terminal-state detection is precise (only CLOSED is terminal in v1).
* coid_* builders + parse_coid round-trip across all 5 phases.
* parse_coid returns None for foreign orders (the "user trades
  manually alongside Lumin" case must not crash the FSM).
* Firestore CRUD round-trip preserves every field including enum +
  timestamps.
* PositionNotFoundError raised on missing doc (typed for caller).
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from src.execution import position_state


@pytest.fixture(autouse=True)
def _reset_state():
    position_state.reset_for_test()
    yield
    position_state.reset_for_test()


# ---------------------------------------------------------------------------
# PositionState enum + terminal helpers
# ---------------------------------------------------------------------------


def test_position_state_values_are_stable_strings() -> None:
    """Enum values are persisted to Firestore.  Renaming one would
    silently break every existing position doc on disk."""
    assert position_state.PositionState.PENDING.value == "PENDING"
    assert position_state.PositionState.OPEN.value == "OPEN"
    assert position_state.PositionState.TP1_HIT.value == "TP1_HIT"
    assert position_state.PositionState.TP2_HIT.value == "TP2_HIT"
    assert position_state.PositionState.CLOSED.value == "CLOSED"


@pytest.mark.parametrize(
    "state, expected",
    [
        (position_state.PositionState.PENDING, False),
        (position_state.PositionState.OPEN, False),
        (position_state.PositionState.TP1_HIT, False),
        (position_state.PositionState.TP2_HIT, False),
        (position_state.PositionState.CLOSED, True),
    ],
)
def test_is_terminal_only_closed(state, expected) -> None:
    """Only CLOSED is terminal.  TP*_HIT states still receive events
    (the next TP or the SL); they're not stopping points."""
    assert position_state.is_terminal(state) is expected


# ---------------------------------------------------------------------------
# clientOrderId builders + parser
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "builder, phase",
    [
        (position_state.coid_entry, "entry"),
        (position_state.coid_sl, "sl"),
        (position_state.coid_tp1, "tp1"),
        (position_state.coid_tp2, "tp2"),
        (position_state.coid_tp3, "tp3"),
    ],
)
def test_coid_builders_round_trip_through_parse(builder, phase) -> None:
    """coid_X(s) → parse_coid → (s, phase) — round-trips so the FSM
    can map an event's clientOrderId back to its (signal_id, phase).
    Critical because the FSM has no other way to identify which
    phase an ORDER_TRADE_UPDATE belongs to."""
    signal_id = "sig-12345"
    coid = builder(signal_id)
    parsed = position_state.parse_coid(coid)
    assert parsed == (signal_id, phase)


def test_parse_coid_returns_none_for_foreign_order() -> None:
    """Orders placed via Binance UI / other tools don't have the
    ``lumin_`` prefix.  FSM uses None as the signal to log + skip
    rather than crash."""
    assert position_state.parse_coid("user-manual-order-xyz") is None
    assert position_state.parse_coid("") is None
    assert position_state.parse_coid("lumin_") is None  # malformed


def test_parse_coid_rejects_unknown_phase() -> None:
    """A coid with the right prefix but unknown phase suffix
    (e.g. ``lumin_sig_unknown``) is foreign — log + skip."""
    assert position_state.parse_coid("lumin_sig_unknown") is None


# ---------------------------------------------------------------------------
# Firestore CRUD
# ---------------------------------------------------------------------------


def _install_fake_db() -> MagicMock:
    """Build the Firestore mock chain (4 levels deep:
    db.collection.document.collection.document)."""
    fake_doc = MagicMock(name="position_doc")
    fake_positions = MagicMock()
    fake_positions.document.return_value = fake_doc
    fake_user_doc = MagicMock()
    fake_user_doc.collection.return_value = fake_positions
    fake_users = MagicMock()
    fake_users.document.return_value = fake_user_doc
    fake_db = MagicMock()
    fake_db.collection.return_value = fake_users
    position_state._db = fake_db
    return fake_doc


def _sample_position() -> position_state.Position:
    return position_state.Position(
        signal_id="sig-1",
        firebase_uid="fb-x",
        symbol="BTCUSDT",
        side="LONG",
        state=position_state.PositionState.PENDING,
        entry_price_target=29000.0,
        entry_price_filled=0.0,
        sl_price=28500.0,
        tp1_price=29500.0,
        tp2_price=30000.0,
        tp3_price=30500.0,
        total_qty=1.0,
        tp1_qty=0.3,
        tp2_qty=0.4,
        tp3_qty=0.3,
        entry_order_id=12345,
    )


def test_put_position_serialises_enum_as_string() -> None:
    """The Firestore wire format wants strings; the enum gets
    serialised via ``.value`` not via repr (which would store
    ``"PositionState.PENDING"``)."""
    fake_doc = _install_fake_db()
    position_state.put_position(_sample_position())
    fake_doc.set.assert_called_once()
    payload = fake_doc.set.call_args[0][0]
    assert payload["state"] == "PENDING"  # not "PositionState.PENDING"
    assert payload["signal_id"] == "sig-1"
    assert payload["symbol"] == "BTCUSDT"
    assert payload["entry_price_target"] == 29000.0


def test_get_position_round_trips_with_enum_decoded() -> None:
    """Firestore stored ``state="PENDING"``; we want it back as the
    PositionState enum so the FSM can type-check transitions."""
    fake_doc = _install_fake_db()
    fake_doc.get.return_value = SimpleNamespace(
        exists=True,
        to_dict=lambda: {
            "signal_id": "sig-1",
            "firebase_uid": "fb-x",
            "symbol": "BTCUSDT",
            "side": "LONG",
            "state": "OPEN",
            "entry_price_target": 29000.0,
            "entry_price_filled": 29005.5,
            "sl_price": 28500.0,
            "tp1_price": 29500.0,
            "tp2_price": 30000.0,
            "tp3_price": 30500.0,
            "total_qty": 1.0,
            "tp1_qty": 0.3,
            "tp2_qty": 0.4,
            "tp3_qty": 0.3,
            "filled_qty": 1.0,
            "closed_qty": 0.0,
            "entry_order_id": 12345,
            "created_at": datetime.now(timezone.utc),
            "last_event_at": datetime.now(timezone.utc),
        },
    )
    pos = position_state.get_position("fb-x", "sig-1")
    assert pos.state == position_state.PositionState.OPEN
    assert pos.entry_price_filled == 29005.5
    assert pos.entry_order_id == 12345


def test_get_position_raises_typed_error_when_missing() -> None:
    """Caller (FSM) treats this as "event for unknown position —
    log and skip" rather than as a generic crash.  Typed exception
    keeps that branch explicit."""
    fake_doc = _install_fake_db()
    fake_doc.get.return_value = SimpleNamespace(exists=False)
    with pytest.raises(position_state.PositionNotFoundError):
        position_state.get_position("fb-x", "sig-missing")


def test_put_before_init_raises_typed_error() -> None:
    pos = _sample_position()
    with pytest.raises(position_state.PositionStateNotInitialisedError):
        position_state.put_position(pos)


# ---------------------------------------------------------------------------
# list_positions_for_user — Live-tab "your open positions" backend
# ---------------------------------------------------------------------------


def _make_doc_snap(state_value: str, signal_id: str):
    """Build a fake Firestore doc snapshot for list_positions_for_user."""
    return SimpleNamespace(
        id=signal_id,
        to_dict=lambda: {
            "signal_id": signal_id,
            "firebase_uid": "fb-x",
            "symbol": "BTCUSDT",
            "side": "LONG",
            "state": state_value,
            "entry_price_target": 29000.0,
            "entry_price_filled": 29005.5,
            "sl_price": 28500.0,
            "tp1_price": 29500.0,
            "tp2_price": 30000.0,
            "tp3_price": 30500.0,
            "total_qty": 1.0,
            "tp1_qty": 0.3,
            "tp2_qty": 0.4,
            "tp3_qty": 0.3,
            "filled_qty": 1.0,
            "closed_qty": 0.0,
            "entry_order_id": 12345,
            "created_at": datetime.now(timezone.utc),
            "last_event_at": datetime.now(timezone.utc),
        },
    )


def _install_fake_db_for_listing(stream_returns: list) -> MagicMock:
    fake_collection = MagicMock()
    fake_collection.stream.return_value = iter(stream_returns)
    fake_user_doc = MagicMock()
    fake_user_doc.collection.return_value = fake_collection
    fake_users = MagicMock()
    fake_users.document.return_value = fake_user_doc
    fake_db = MagicMock()
    fake_db.collection.return_value = fake_users
    position_state._db = fake_db
    return fake_collection


def test_list_positions_filters_terminal_states_by_default() -> None:
    """The Live-tab card wants what's *open right now* — closed
    positions belong to the historical PnL view, not the live one."""
    _install_fake_db_for_listing([
        _make_doc_snap("OPEN", "sig-open"),
        _make_doc_snap("CLOSED", "sig-closed"),
        _make_doc_snap("PENDING", "sig-pending"),
    ])
    positions = position_state.list_positions_for_user("fb-x")
    ids = {p.signal_id for p in positions}
    assert ids == {"sig-open", "sig-pending"}


def test_list_positions_include_closed_when_requested() -> None:
    _install_fake_db_for_listing([
        _make_doc_snap("OPEN", "sig-open"),
        _make_doc_snap("CLOSED", "sig-closed"),
    ])
    positions = position_state.list_positions_for_user(
        "fb-x", include_closed=True,
    )
    assert {p.signal_id for p in positions} == {"sig-open", "sig-closed"}


def test_list_positions_returns_empty_when_collection_empty() -> None:
    """A user who has never had a position — the Live-tab card should
    render the empty-state UI without erroring."""
    _install_fake_db_for_listing([])
    assert position_state.list_positions_for_user("fb-x") == []


def test_list_positions_skips_empty_docs() -> None:
    """A doc with no payload (``to_dict()`` returns None / empty dict)
    is skipped — returning a half-built Position from defaults would
    surface a phantom signal-id="" row in the Live tab.  The dict-
    parsing layer remains tolerant for diagnostics; the listing layer
    filters at the empty-payload boundary so the user-facing card
    never shows a doc that hadn't been written yet."""
    empty = SimpleNamespace(id="empty", to_dict=lambda: None)
    good = _make_doc_snap("OPEN", "sig-good")
    _install_fake_db_for_listing([empty, good])
    positions = position_state.list_positions_for_user("fb-x")
    assert len(positions) == 1
    assert positions[0].signal_id == "sig-good"


def test_list_positions_skips_unparseable_state_string() -> None:
    """If a Firestore doc somehow carries an unknown state token (env
    drift, manual edit), the row is logged and skipped — the rest of
    the user's positions still render."""
    bad = SimpleNamespace(
        id="bad",
        to_dict=lambda: {"signal_id": "bad", "state": "NOT_A_REAL_STATE"},
    )
    good = _make_doc_snap("OPEN", "sig-good")
    _install_fake_db_for_listing([bad, good])
    positions = position_state.list_positions_for_user("fb-x")
    assert {p.signal_id for p in positions} == {"sig-good"}


def test_list_positions_raises_when_not_initialised() -> None:
    position_state.reset_for_test()
    with pytest.raises(position_state.PositionStateNotInitialisedError):
        position_state.list_positions_for_user("fb-x")
