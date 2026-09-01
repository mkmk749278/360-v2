"""A terminal close must not leave its bracket resting on Binance.

Owner screenshot, 2026-09-01, Binance Futures app: **Positions (0)** beside
**Open Orders → Conditional (24)** — every one of the 24 a reduce-only
``TAKE_PROFIT_MARKET`` against a position that no longer existed, the oldest
15 hours old, and two of them on opposite sides of the SAME symbol.

The design rested on one sentence in ``order_placer.place_pretp_trail``:
*"TP orders have reduceOnly=true and Binance auto-cancels reduce-only orders
when the position is closed by another order."*  Binance sweeps reduce-only
orders resting on the ORDER BOOK; every SL and TP here is an ALGO order
(``/fapi/v1/algoOrder``, ``algoType=CONDITIONAL``) sitting untriggered in the
conditional engine, which is not swept.  Binance's own UI files them under a
separate "Conditional" tab — which is how this became visible at all.

``signal_dispatch.close_fsm_positions_for_signal`` already knew, and swept the
same set before its market close.  The knowledge never reached the three paths
where most closes actually happen, so this is the repo's usual seam: two halves
that each look complete, nothing crashing, nothing empty on screen.

Three producers, pinned separately because they fail for different reasons:

1. every terminal transition in the FSM (``_apply_sl_fill`` is the plain case —
   the stop fires and TP1/TP2/TP3 stay parked);
2. the reconciler's 2h stale-close backstop, which fired on 39 of 140 matched
   positions in the 24 Aug – 1 Sep window and cancelled nothing;
3. the reconciler's external/manual-close heal — the catch-all every exit the
   FSM did not book itself lands in.

Verified to fail against the pre-fix tree.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.execution import order_placer
from src.execution import position_fsm
from src.execution import position_state
from src.execution import reconciler as reconciler_mod

from tests.execution.test_position_fsm import _otu, _stub_placer_factory


@pytest.fixture(autouse=True)
def _store(monkeypatch):
    """In-memory stand-in for the position document store.

    The suite's convention (``test_position_fsm``) is to patch the two
    accessors rather than stand up Firestore; a dict keeps the same
    round-trip so an assertion about the PERSISTED document still means what
    it says.
    """
    position_state.reset_for_test()
    for k in position_fsm._SWEEP_COUNTS:
        position_fsm._SWEEP_COUNTS[k] = 0
    docs: dict = {}
    monkeypatch.setattr(
        position_state, "put_position",
        lambda p: docs.__setitem__((p.firebase_uid, p.signal_id), p),
    )
    monkeypatch.setattr(
        position_state, "get_position",
        lambda uid, sid: docs[(uid, sid)],
    )
    yield docs
    position_state.reset_for_test()


def _bracketed(
    signal_id: str = "sig-1",
    state: position_state.PositionState = position_state.PositionState.OPEN,
) -> position_state.Position:
    """An open position with the whole bracket resting on Binance."""
    return position_state.Position(
        signal_id=signal_id,
        firebase_uid="fb-x",
        symbol="BTCUSDT",
        side="LONG",
        state=state,
        entry_price_target=29000.0,
        entry_price_filled=29000.0,
        sl_price=28500.0,
        tp1_price=29500.0,
        tp2_price=30000.0,
        tp3_price=30500.0,
        total_qty=1.0,
        tp1_qty=0.3,
        tp2_qty=0.4,
        tp3_qty=0.3,
        entry_order_id=1000,
        sl_order_id=2000,
        tp1_order_id=3001,
        tp2_order_id=3002,
        tp3_order_id=3003,
        created_at=datetime.now(timezone.utc),
    )


def _cancelled_ids(placer) -> set:
    return {c.kwargs["algo_id"] for c in placer.cancel_algo_order.call_args_list}


# ---------------------------------------------------------------------------
# The set itself
# ---------------------------------------------------------------------------


def test_the_protective_set_is_derived_from_the_dataclass_not_typed_twice():
    """A field added to Position is covered the day it is added.

    Two hand-kept copies of this list already existed and disagreed, which is
    how the TP ladder came to be left resting.  The exclusion set is what a
    future author has to justify in a diff, not the inclusion set.
    """
    from dataclasses import fields

    every_order_id = {
        f.name for f in fields(position_state.Position)
        if f.name.endswith("_order_id")
    }
    assert set(position_state.PROTECTIVE_ORDER_ATTRS) == (
        every_order_id - position_state._NON_PROTECTIVE_ORDER_ATTRS
    )
    # And the second reader holds no copy of its own.
    from src.execution import signal_dispatch
    assert (
        signal_dispatch._PROTECTIVE_ORDER_ATTRS
        is position_state.PROTECTIVE_ORDER_ATTRS
    )


# ---------------------------------------------------------------------------
# 1. Every terminal FSM transition
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sl_fill_cancels_the_whole_tp_ladder():
    """The plain case, and the commonest: the stop fires, the position is
    flat, and TP1/TP2/TP3 were left parked for the next position on the
    symbol to inherit."""
    factory, placer = _stub_placer_factory()
    fsm = position_fsm.PositionFSM("fb-x", order_placer_factory=factory)
    pos = _bracketed()
    position_state.put_position(pos)

    await fsm.handle_event(_otu(client_order_id="lumin_sig-1_sl"))

    stored = position_state.get_position("fb-x", "sig-1")
    assert stored.state is position_state.PositionState.CLOSED
    assert _cancelled_ids(placer) == {3001, 3002, 3003}
    # The SL is the order that FIRED — cancelling it would spend a round trip
    # to be told -2011.
    assert 2000 not in _cancelled_ids(placer)
    # The persisted document no longer claims orders that are gone.
    assert (stored.tp1_order_id, stored.tp2_order_id, stored.tp3_order_id) == (0, 0, 0)
    assert stored.sl_order_id == 0


@pytest.mark.asyncio
async def test_tp3_fill_cancels_the_resting_stop():
    """Terminal from the other direction: all profit booked, stop still
    parked.  A resting closePosition stop is what Binance answers -4130 to,
    which is the documented way the trail handover becomes impossible."""
    factory, placer = _stub_placer_factory()
    fsm = position_fsm.PositionFSM("fb-x", order_placer_factory=factory)
    pos = _bracketed(state=position_state.PositionState.TP2_HIT)
    pos.sl_be_order_id = 2100
    position_state.put_position(pos)

    await fsm.handle_event(_otu(client_order_id="lumin_sig-1_tp3"))

    assert position_state.get_position("fb-x", "sig-1").state is (
        position_state.PositionState.CLOSED
    )
    assert {2000, 2100} <= _cancelled_ids(placer)
    assert 3003 not in _cancelled_ids(placer)  # the leg that filled


@pytest.mark.asyncio
async def test_a_non_terminal_transition_cancels_nothing():
    """TP1 with a residual still riding is NOT terminal — sweeping there
    would strip the protection off a live position, which is the one thing
    worse than an orphan."""
    factory, placer = _stub_placer_factory()
    fsm = position_fsm.PositionFSM("fb-x", order_placer_factory=factory)
    pos = _bracketed()
    position_state.put_position(pos)

    await fsm.handle_event(
        _otu(client_order_id="lumin_sig-1_tp1", last_filled_qty=0.3,
             cumulative_filled_qty=0.3)
    )

    stored = position_state.get_position("fb-x", "sig-1")
    assert stored.state is position_state.PositionState.TP1_HIT
    # TP2/TP3 must still be resting: the residual rides to them.
    assert 3002 not in _cancelled_ids(placer)
    assert 3003 not in _cancelled_ids(placer)
    assert stored.tp2_order_id == 3002


@pytest.mark.asyncio
async def test_a_failed_cancel_never_aborts_the_close():
    """The position is already flat and the close already booked, so a
    cancel that fails degrades to a counted orphan — never to a transition
    that half-happened."""
    factory, placer = _stub_placer_factory()
    placer.cancel_algo_order = AsyncMock(
        side_effect=order_placer.OrderPlacementError("binance said no")
    )
    fsm = position_fsm.PositionFSM("fb-x", order_placer_factory=factory)
    position_state.put_position(_bracketed())

    await fsm.handle_event(_otu(client_order_id="lumin_sig-1_sl"))

    stored = position_state.get_position("fb-x", "sig-1")
    assert stored.state is position_state.PositionState.CLOSED
    assert position_fsm.sweep_counts()["failed"] == 3
    # The id is KEPT on a failure: it is the only record that an order is
    # still out there, and the reconciler reads the same fields.
    assert stored.tp1_order_id == 3001


# ---------------------------------------------------------------------------
# 2 + 3. Both reconciler close paths
# ---------------------------------------------------------------------------


def _reconciler(placer) -> reconciler_mod.Reconciler:
    return reconciler_mod.Reconciler(
        signing_client_factory=lambda: MagicMock(),
        order_placer_factory=lambda uid: placer,
        positions_for_user=lambda uid: [],
        max_position_age_sec=7200,
        stale_close_enabled=True,
    )


@pytest.mark.asyncio
async def test_the_2h_stale_close_cancels_the_bracket_first():
    """The backstop that force-closes a position past the age ceiling.  It
    fired on 39 of 140 matched positions in the owner's window and cancelled
    nothing — the single largest producer of the 24 orphans."""
    _factory, placer = _stub_placer_factory()
    pos = _bracketed()
    pos.created_at = datetime.now(timezone.utc) - timedelta(hours=3)

    await _reconciler(placer)._maybe_force_close_stale(pos)

    assert pos.state is position_state.PositionState.CLOSED
    assert pos.close_reason == "STALE_EXPIRY"
    assert _cancelled_ids(placer) == {2000, 3001, 3002, 3003}
    placer.place_market_close.assert_awaited_once()


@pytest.mark.asyncio
async def test_an_externally_closed_position_has_its_bracket_retired():
    """Binance shows flat.  That says nothing about the conditional orders
    still parked on the symbol — this is the catch-all path every exit the
    FSM did not book itself lands in (a missed user-data-stream event, a
    native fill we never saw, the user closing on Binance)."""
    _factory, placer = _stub_placer_factory()
    pos = _bracketed()
    position_state.put_position(pos)

    await _reconciler(placer)._diff_and_heal(pos, {"BTCUSDT": 0.0})

    assert pos.state is position_state.PositionState.CLOSED
    assert pos.close_reason == "MANUAL"
    assert _cancelled_ids(placer) == {2000, 3001, 3002, 3003}
    # Persisted with the ids already zeroed, so a later cycle re-cancels
    # nothing.
    assert position_state.get_position("fb-x", "sig-1").tp2_order_id == 0
