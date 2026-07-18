"""Manual trade builder — FSM limit-entry fill handler + protection.

Covers the async entry-fill path added for LIMIT entries
(``docs/MANUAL_TRADE_BUILDER_DESIGN.md``): a PENDING_ENTRY position that
fills transitions to OPEN and lays SL/TP via
``PositionFSM.place_protection_on_limit_fill``, with the owner rule that
compulsory SL applies only to auto-dispatch — ``user_owned`` manual takes may
be entry-only and are never force-closed for a missing/failed SL. MARKET
entries (PENDING) must NOT re-place protection (already placed in place_signal).
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution import events as events_mod
from src.execution import order_placer
from src.execution import position_fsm
from src.execution import position_state


@pytest.fixture(autouse=True)
def _reset_state():
    position_state.reset_for_test()
    yield
    position_state.reset_for_test()


def _placer():
    p = MagicMock()
    p.cancel_order = AsyncMock(return_value=None)
    p.cancel_algo_order = AsyncMock(return_value=None)
    p.place_market_close = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=9001, client_order_id="lumin_s_close",
            status="FILLED", avg_price=0.0, binance_body={},
        )
    )
    p.place_stop_loss = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=4001, client_order_id="lumin_s_sl",
            status="NEW", avg_price=0.0, binance_body={},
        )
    )
    p.place_take_profit = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=6001, client_order_id="lumin_s_tp",
            status="NEW", avg_price=0.0, binance_body={},
        )
    )
    p.place_limit_entry = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=1001, client_order_id="lumin_s_entry",
            status="NEW", avg_price=0.0, binance_body={},
        )
    )
    return p


def _factory(placer):
    return lambda uid: placer


def _entry_fill_event(coid="lumin_s_entry", qty=1.0, price=29000.0):
    return events_mod.OrderTradeUpdate(
        symbol="BTCUSDT", client_order_id=coid, side="BUY",
        order_type="LIMIT", time_in_force="GTC", original_qty=qty,
        original_price=price, average_price=price, stop_price=0.0,
        execution_type="TRADE", order_status="FILLED", order_id=1001,
        last_filled_qty=qty, cumulative_filled_qty=qty, last_filled_price=price,
        commission=0.0, commission_asset="USDT", trade_time_ms=0, trade_id=1,
        bids_notional=0.0, asks_notional=0.0, is_maker=True, reduce_only=False,
        working_type="MARK_PRICE", original_order_type="LIMIT",
        position_side="BOTH", close_position=False, activation_price=0.0,
        callback_rate=0.0, realized_pnl=0.0,
    )


def _position(
    *,
    state=position_state.PositionState.PENDING_ENTRY,
    protection_mode="managed",
    sl_price=28500.0,
    tp1_qty=0.3,
    tp2_qty=0.4,
    tp3_qty=0.3,
    pretp_fraction=0.5,
):
    return position_state.Position(
        signal_id="s", firebase_uid="uid", symbol="BTCUSDT", side="LONG",
        state=state, entry_price_target=29000.0, entry_price_filled=0.0,
        sl_price=sl_price, tp1_price=29500.0, tp2_price=30000.0, tp3_price=30500.0,
        total_qty=1.0, tp1_qty=tp1_qty, tp2_qty=tp2_qty, tp3_qty=tp3_qty,
        entry_order_id=1001, pretp_fraction=pretp_fraction,
        protection_mode=protection_mode,
    )


async def _drive_fill(position, placer):
    """Run the entry-fill event through the FSM, capturing the persisted state."""
    captured = []
    fsm = position_fsm.PositionFSM("uid", order_placer_factory=_factory(placer))
    with patch.object(position_state, "get_position", return_value=position), \
         patch.object(position_state, "put_position",
                      side_effect=lambda p: captured.append(p)), \
         patch("src.execution.dispatch_log.record_rejected", MagicMock()), \
         patch("src.execution.dispatch_log.record_placed", MagicMock()):
        await fsm.handle_event(_entry_fill_event())
    return captured[-1] if captured else position


@pytest.mark.asyncio
async def test_limit_fill_places_sl_and_tp():
    placer = _placer()
    pos = await _drive_fill(_position(), placer)
    assert pos.state == position_state.PositionState.OPEN
    placer.place_stop_loss.assert_awaited_once()
    assert pos.sl_order_id == 4001
    # three TP legs (tp1/tp2/tp3 all > 0)
    assert placer.place_take_profit.await_count == 3


@pytest.mark.asyncio
async def test_user_owned_entry_only_places_no_sl_and_stays_open():
    placer = _placer()
    pos = await _drive_fill(
        _position(protection_mode="user_owned", sl_price=0.0,
                  tp1_qty=0.0, tp2_qty=0.0, tp3_qty=0.0),
        placer,
    )
    assert pos.state == position_state.PositionState.OPEN
    placer.place_stop_loss.assert_not_called()
    placer.place_take_profit.assert_not_called()
    placer.place_market_close.assert_not_called()  # never force-closed


@pytest.mark.asyncio
async def test_user_owned_sl_failure_leaves_position_open():
    placer = _placer()
    placer.place_stop_loss = AsyncMock(side_effect=RuntimeError("sl reject"))
    pos = await _drive_fill(
        _position(protection_mode="user_owned", sl_price=28500.0), placer
    )
    # user owns the exit — SL failure does NOT force-close
    assert pos.state == position_state.PositionState.OPEN
    placer.place_market_close.assert_not_called()


@pytest.mark.asyncio
async def test_managed_sl_failure_force_closes():
    placer = _placer()
    placer.place_stop_loss = AsyncMock(side_effect=RuntimeError("sl reject"))
    pos = await _drive_fill(_position(protection_mode="managed"), placer)
    # managed: never OPEN without a stop → force-close
    placer.place_market_close.assert_awaited_once()
    assert pos.state == position_state.PositionState.CLOSED
    assert pos.close_reason == "SL_PLACEMENT_FAILED"


@pytest.mark.asyncio
async def test_market_entry_fill_does_not_replace_protection():
    """A PENDING (market) entry already had SL/TP placed in place_signal —
    the fill handler must NOT place them again."""
    placer = _placer()
    pos = await _drive_fill(
        _position(state=position_state.PositionState.PENDING), placer
    )
    assert pos.state == position_state.PositionState.OPEN
    placer.place_stop_loss.assert_not_called()
    placer.place_take_profit.assert_not_called()


@pytest.mark.asyncio
async def test_full_grab_pretp_skips_tp_ladder():
    placer = _placer()
    pos = await _drive_fill(_position(pretp_fraction=1.0), placer)
    assert pos.state == position_state.PositionState.OPEN
    placer.place_stop_loss.assert_awaited_once()  # SL still placed
    placer.place_take_profit.assert_not_called()  # no residual to ride
