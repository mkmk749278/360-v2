"""Tests for src.execution.position_fsm.

The state machine logic gets isolated unit tests (Firestore +
OrderPlacer mocked).  What we pin:

* ``handle_event`` dispatches only on ORDER_TRADE_UPDATE; other
  event types (AccountUpdate / MarginCall / ListenKeyExpired) are
  no-ops.
* Foreign clientOrderIds (no ``lumin_`` prefix) are skipped silently.
* Late events (after a position reached CLOSED) are skipped silently.
* Each fill transitions to the right next state with the right
  accounting (closed_qty, realized_pnl_total).
* ``place_signal`` places entry first, then SL + 3x TP, persisting
  twice (once after entry, again with all order ids captured).
* Entry placement failure raises but SL/TP best-effort failures are
  swallowed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
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


def _stub_placer_factory():
    """Return a (factory, placer) pair.  The factory returns the same
    mock placer instance so tests can assert against it.  All placer
    methods are AsyncMocks that return successful OrderPlacementResults
    by default — override per test if needed."""
    placer = MagicMock()
    placer.cancel_order = AsyncMock(return_value=None)
    placer.place_stop_loss = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=4001, client_order_id="lumin_sig-1_sl_be",
            status="NEW", avg_price=0.0, binance_body={},
        )
    )
    placer.place_pretp_partial = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=5001, client_order_id="lumin_sig-1_pretp",
            status="FILLED", avg_price=29100.0, binance_body={},
        )
    )

    def _factory(uid):
        return placer

    return _factory, placer


def _otu(
    *,
    client_order_id: str,
    execution_type: str = "TRADE",
    order_status: str = "FILLED",
    last_filled_qty: float = 1.0,
    cumulative_filled_qty: float = 1.0,
    average_price: float = 29000.0,
    realized_pnl: float = 0.0,
) -> events_mod.OrderTradeUpdate:
    """Build a minimal ORDER_TRADE_UPDATE event for FSM testing."""
    return events_mod.OrderTradeUpdate(
        symbol="BTCUSDT",
        client_order_id=client_order_id,
        side="BUY",
        order_type="MARKET",
        time_in_force="GTC",
        original_qty=1.0,
        original_price=0.0,
        average_price=average_price,
        stop_price=0.0,
        execution_type=execution_type,
        order_status=order_status,
        order_id=1,
        last_filled_qty=last_filled_qty,
        cumulative_filled_qty=cumulative_filled_qty,
        last_filled_price=average_price,
        commission=0.0,
        commission_asset="USDT",
        trade_time_ms=0,
        trade_id=0,
        bids_notional=0.0,
        asks_notional=0.0,
        is_maker=False,
        reduce_only=False,
        working_type="MARK_PRICE",
        original_order_type="MARKET",
        position_side="BOTH",
        close_position=False,
        activation_price=0.0,
        callback_rate=0.0,
        realized_pnl=realized_pnl,
    )


def _pending_position(signal_id: str = "sig-1") -> position_state.Position:
    return position_state.Position(
        signal_id=signal_id,
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
    )


# ---------------------------------------------------------------------------
# Top-level dispatch
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_non_otu_events_are_noops() -> None:
    """ACCOUNT_UPDATE / MARGIN_CALL / listenKeyExpired are consumed
    by other layers (PR-8 / PR-9) — FSM must not crash on them."""
    fsm = position_fsm.PositionFSM("fb-x")
    await fsm.handle_event(events_mod.ListenKeyExpired(event_time_ms=0))
    await fsm.handle_event(
        events_mod.AccountUpdate(
            event_time_ms=0, transaction_time_ms=0, event_reason="",
            balances=[], positions=[],
        )
    )
    # No exception = pass.


@pytest.mark.asyncio
async def test_foreign_coid_is_skipped() -> None:
    """Order placed via Binance UI / another tool — log + skip.  The
    FSM must NOT crash because a user trades manually alongside Lumin."""
    fsm = position_fsm.PositionFSM("fb-x")
    with patch.object(
        position_state, "get_position", new=MagicMock()
    ) as mock_get:
        await fsm.handle_event(
            _otu(client_order_id="user-manual-order-xyz")
        )
        mock_get.assert_not_called()


@pytest.mark.asyncio
async def test_event_for_unknown_position_logs_and_returns() -> None:
    """The Firestore doc was deleted between order placement and the
    fill event arriving — log warning + return; do not crash."""
    fsm = position_fsm.PositionFSM("fb-x")
    with patch.object(
        position_state,
        "get_position",
        side_effect=position_state.PositionNotFoundError("missing"),
    ):
        # Must not raise.
        await fsm.handle_event(
            _otu(client_order_id=position_state.coid_entry("sig-missing"))
        )


@pytest.mark.asyncio
async def test_late_event_for_terminal_position_is_skipped() -> None:
    """A second TP3 fill (or stray late event) after CLOSED must NOT
    re-apply transitions — that would corrupt the audit trail."""
    fsm = position_fsm.PositionFSM("fb-x")
    terminal = _pending_position()
    terminal.state = position_state.PositionState.CLOSED
    with patch.object(position_state, "get_position", return_value=terminal), patch.object(
        position_state, "put_position"
    ) as mock_put:
        await fsm.handle_event(
            _otu(client_order_id=position_state.coid_tp3("sig-1"))
        )
        mock_put.assert_not_called()


@pytest.mark.asyncio
async def test_non_trade_execution_type_is_skipped() -> None:
    """NEW / CANCELED / EXPIRED events are state updates, not fills.
    FSM only acts on TRADE events."""
    fsm = position_fsm.PositionFSM("fb-x")
    position = _pending_position()
    with patch.object(position_state, "get_position", return_value=position), patch.object(
        position_state, "put_position"
    ) as mock_put:
        await fsm.handle_event(
            _otu(
                client_order_id=position_state.coid_entry("sig-1"),
                execution_type="NEW",
                order_status="NEW",
            )
        )
        mock_put.assert_not_called()


# ---------------------------------------------------------------------------
# Per-phase transitions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_entry_fill_transitions_pending_to_open() -> None:
    fsm = position_fsm.PositionFSM("fb-x")
    position = _pending_position()
    captured: list = []
    with patch.object(position_state, "get_position", return_value=position), patch.object(
        position_state, "put_position", side_effect=lambda p: captured.append(p)
    ):
        await fsm.handle_event(
            _otu(
                client_order_id=position_state.coid_entry("sig-1"),
                cumulative_filled_qty=1.0,
                average_price=29005.5,
                order_status="FILLED",
            )
        )
    assert len(captured) == 1
    assert captured[0].state == position_state.PositionState.OPEN
    assert captured[0].filled_qty == 1.0
    assert captured[0].entry_price_filled == 29005.5


@pytest.mark.asyncio
async def test_partial_entry_fill_stays_pending() -> None:
    """Partial fill on a MARKET entry can happen on illiquid pairs.
    FSM stays PENDING until cumulative reaches total."""
    fsm = position_fsm.PositionFSM("fb-x")
    position = _pending_position()
    captured: list = []
    with patch.object(position_state, "get_position", return_value=position), patch.object(
        position_state, "put_position", side_effect=lambda p: captured.append(p)
    ):
        await fsm.handle_event(
            _otu(
                client_order_id=position_state.coid_entry("sig-1"),
                cumulative_filled_qty=0.3,
                last_filled_qty=0.3,
                order_status="PARTIALLY_FILLED",
            )
        )
    assert captured[0].state == position_state.PositionState.PENDING
    assert captured[0].filled_qty == 0.3


@pytest.mark.asyncio
async def test_tp1_fill_transitions_open_to_tp1_hit_and_does_be_shift() -> None:
    """OPEN → TP1_HIT.  Per §3.2a (PR-7), this ALSO triggers the BE
    shift: cancel original SL + place new SL at entry price.  Tests
    the path where pre-TP didn't fire first (an unusually-fast
    favourable move)."""
    factory, placer = _stub_placer_factory()
    fsm = position_fsm.PositionFSM("fb-x", order_placer_factory=factory)
    position = _pending_position()
    position.state = position_state.PositionState.OPEN
    position.entry_price_filled = 29000.0
    position.sl_order_id = 2001  # has an original SL to cancel
    captured: list = []
    with patch.object(position_state, "get_position", return_value=position), patch.object(
        position_state, "put_position", side_effect=lambda p: captured.append(p)
    ):
        await fsm.handle_event(
            _otu(
                client_order_id=position_state.coid_tp1("sig-1"),
                last_filled_qty=0.3,
                realized_pnl=15.0,
            )
        )
    assert captured[0].state == position_state.PositionState.TP1_HIT
    assert captured[0].closed_qty == 0.3
    assert captured[0].realized_pnl_total == 15.0
    # BE shift: original SL cancelled, BE-SL placed at entry price.
    placer.cancel_order.assert_called_once_with(symbol="BTCUSDT", order_id=2001)
    placer.place_stop_loss.assert_called_once()
    sl_kwargs = placer.place_stop_loss.call_args.kwargs
    assert sl_kwargs["stop_price"] == 29000.0  # entry_price_filled
    assert sl_kwargs["coid_override"] == position_state.coid_sl_be("sig-1")
    assert captured[0].sl_be_order_id == 4001
    assert captured[0].sl_order_id == 0  # original gone


@pytest.mark.asyncio
async def test_tp1_after_pretp_does_not_redo_be_shift() -> None:
    """Pre-TP already fired (state PRE_TP_FIRED) → TP1 hits on the
    residual → state TP1_HIT, but BE shift was ALREADY done at
    pre-TP fill time.  Verify the FSM doesn't redundantly cancel +
    re-place the SL."""
    factory, placer = _stub_placer_factory()
    fsm = position_fsm.PositionFSM("fb-x", order_placer_factory=factory)
    position = _pending_position()
    position.state = position_state.PositionState.PRE_TP_FIRED
    position.sl_be_order_id = 4001  # BE-SL already placed
    position.sl_order_id = 0
    captured: list = []
    with patch.object(position_state, "get_position", return_value=position), patch.object(
        position_state, "put_position", side_effect=lambda p: captured.append(p)
    ):
        await fsm.handle_event(
            _otu(
                client_order_id=position_state.coid_tp1("sig-1"),
                last_filled_qty=0.5,
                realized_pnl=25.0,
            )
        )
    assert captured[0].state == position_state.PositionState.TP1_HIT
    # No redundant BE shift — the SL was already at BE.
    placer.cancel_order.assert_not_called()
    placer.place_stop_loss.assert_not_called()


@pytest.mark.asyncio
async def test_tp2_fill_transitions_tp1_hit_to_tp2_hit() -> None:
    fsm = position_fsm.PositionFSM("fb-x")
    position = _pending_position()
    position.state = position_state.PositionState.TP1_HIT
    position.closed_qty = 0.3
    position.realized_pnl_total = 15.0
    captured: list = []
    with patch.object(position_state, "get_position", return_value=position), patch.object(
        position_state, "put_position", side_effect=lambda p: captured.append(p)
    ):
        await fsm.handle_event(
            _otu(
                client_order_id=position_state.coid_tp2("sig-1"),
                last_filled_qty=0.4,
                realized_pnl=30.0,
            )
        )
    assert captured[0].state == position_state.PositionState.TP2_HIT
    assert captured[0].closed_qty == 0.7
    assert captured[0].realized_pnl_total == 45.0


@pytest.mark.asyncio
async def test_tp3_fill_transitions_to_closed_with_reason() -> None:
    fsm = position_fsm.PositionFSM("fb-x")
    position = _pending_position()
    position.state = position_state.PositionState.TP2_HIT
    position.closed_qty = 0.7
    captured: list = []
    with patch.object(position_state, "get_position", return_value=position), patch.object(
        position_state, "put_position", side_effect=lambda p: captured.append(p)
    ):
        await fsm.handle_event(
            _otu(
                client_order_id=position_state.coid_tp3("sig-1"),
                last_filled_qty=0.3,
                realized_pnl=20.0,
            )
        )
    assert captured[0].state == position_state.PositionState.CLOSED
    assert captured[0].close_reason == "TP3"
    assert captured[0].closed_at is not None


@pytest.mark.asyncio
async def test_pretp_fill_transitions_open_to_pretp_fired_with_be_shift() -> None:
    """**The doctrine-critical transition** (§3.2a).  Pre-TP partial
    close fills → OPEN → PRE_TP_FIRED.  Side effects:
    1. Cancel original SL.
    2. Cancel TP2 + TP3 (residual too small for multi-leg TP).
    3. Place new SL at entry price (BE shift).
    """
    factory, placer = _stub_placer_factory()
    fsm = position_fsm.PositionFSM("fb-x", order_placer_factory=factory)
    position = _pending_position()
    position.state = position_state.PositionState.OPEN
    position.entry_price_filled = 29000.0
    position.sl_order_id = 2001
    position.tp1_order_id = 3001  # stays
    position.tp2_order_id = 3002  # cancelled
    position.tp3_order_id = 3003  # cancelled
    captured: list = []
    with patch.object(position_state, "get_position", return_value=position), patch.object(
        position_state, "put_position", side_effect=lambda p: captured.append(p)
    ):
        await fsm.handle_event(
            _otu(
                client_order_id=position_state.coid_pretp("sig-1"),
                last_filled_qty=0.5,
                realized_pnl=25.0,
            )
        )
    assert captured[0].state == position_state.PositionState.PRE_TP_FIRED
    assert captured[0].pretp_fired is True
    assert captured[0].closed_qty == 0.5
    assert captured[0].realized_pnl_total == 25.0
    # 3 cancels: original SL + TP2 + TP3.  TP1 stays.
    assert placer.cancel_order.await_count == 3
    cancelled_ids = {
        call.kwargs["order_id"] for call in placer.cancel_order.call_args_list
    }
    assert cancelled_ids == {2001, 3002, 3003}
    # BE-SL placed at entry price.
    placer.place_stop_loss.assert_called_once()
    assert placer.place_stop_loss.call_args.kwargs["stop_price"] == 29000.0
    assert captured[0].sl_be_order_id == 4001
    assert captured[0].sl_order_id == 0
    assert captured[0].tp2_order_id == 0
    assert captured[0].tp3_order_id == 0
    # TP1 stays — residual rides toward it.
    assert captured[0].tp1_order_id == 3001
    # SL price field updated to BE for app-display.
    assert captured[0].sl_price == 29000.0


@pytest.mark.asyncio
async def test_pretp_fill_tolerates_sl_cancel_failure() -> None:
    """Race: SL fires at the same moment as pre-TP fills.  The cancel
    returns -2011 "Unknown order sent" — already handled by
    OrderPlacer.cancel_order returning success.  But even if a real
    error fires, the pre-TP transition must still apply (don't leave
    the position in an inconsistent state)."""
    factory, placer = _stub_placer_factory()
    placer.cancel_order = AsyncMock(
        side_effect=order_placer.OrderRejectedByBinance("network glitch")
    )
    fsm = position_fsm.PositionFSM("fb-x", order_placer_factory=factory)
    position = _pending_position()
    position.state = position_state.PositionState.OPEN
    position.sl_order_id = 2001
    captured: list = []
    with patch.object(position_state, "get_position", return_value=position), patch.object(
        position_state, "put_position", side_effect=lambda p: captured.append(p)
    ):
        # Must not raise.
        await fsm.handle_event(
            _otu(
                client_order_id=position_state.coid_pretp("sig-1"),
                last_filled_qty=0.5,
            )
        )
    # Transition still applied.
    assert captured[0].state == position_state.PositionState.PRE_TP_FIRED


@pytest.mark.asyncio
async def test_sl_be_fill_closes_with_distinct_reason() -> None:
    """BE-shifted SL fill → CLOSED with close_reason="SL_BE" (not
    "SL").  Truth report classifies these differently — SL_BE is
    doctrinally healthy (banked partial + BE on residual), raw SL is
    not."""
    factory, _placer = _stub_placer_factory()
    fsm = position_fsm.PositionFSM("fb-x", order_placer_factory=factory)
    position = _pending_position()
    position.state = position_state.PositionState.PRE_TP_FIRED
    position.sl_be_order_id = 4001
    captured: list = []
    with patch.object(position_state, "get_position", return_value=position), patch.object(
        position_state, "put_position", side_effect=lambda p: captured.append(p)
    ):
        await fsm.handle_event(
            _otu(
                client_order_id=position_state.coid_sl_be("sig-1"),
                last_filled_qty=0.5,
                realized_pnl=-2.5,
            )
        )
    assert captured[0].state == position_state.PositionState.CLOSED
    assert captured[0].close_reason == "SL_BE"
    assert captured[0].closed_qty == position.total_qty


@pytest.mark.asyncio
async def test_sl_fill_closes_position_with_reason() -> None:
    """SL is closePosition=true — closes the entire remaining position
    regardless of partial fills along the way.  closed_qty = total_qty
    on the SL fill."""
    fsm = position_fsm.PositionFSM("fb-x")
    position = _pending_position()
    position.state = position_state.PositionState.OPEN
    captured: list = []
    with patch.object(position_state, "get_position", return_value=position), patch.object(
        position_state, "put_position", side_effect=lambda p: captured.append(p)
    ):
        await fsm.handle_event(
            _otu(
                client_order_id=position_state.coid_sl("sig-1"),
                last_filled_qty=1.0,
                realized_pnl=-50.0,
            )
        )
    assert captured[0].state == position_state.PositionState.CLOSED
    assert captured[0].close_reason == "SL"
    assert captured[0].closed_qty == 1.0
    assert captured[0].realized_pnl_total == -50.0


# ---------------------------------------------------------------------------
# place_signal — end-to-end order placement
# ---------------------------------------------------------------------------


def _placer_with_mock_results() -> MagicMock:
    """Build a MagicMock OrderPlacer whose methods return well-formed
    OrderPlacementResults."""
    placer = MagicMock()
    placer.place_market_entry = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=1001, client_order_id="lumin_sig-1_entry",
            status="NEW", avg_price=0.0, binance_body={},
        )
    )
    placer.place_stop_loss = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=2001, client_order_id="lumin_sig-1_sl",
            status="NEW", avg_price=0.0, binance_body={},
        )
    )
    placer.place_take_profit = AsyncMock(
        side_effect=[
            order_placer.OrderPlacementResult(
                order_id=3001, client_order_id="lumin_sig-1_tp1",
                status="NEW", avg_price=0.0, binance_body={},
            ),
            order_placer.OrderPlacementResult(
                order_id=3002, client_order_id="lumin_sig-1_tp2",
                status="NEW", avg_price=0.0, binance_body={},
            ),
            order_placer.OrderPlacementResult(
                order_id=3003, client_order_id="lumin_sig-1_tp3",
                status="NEW", avg_price=0.0, binance_body={},
            ),
        ]
    )
    return placer


@pytest.mark.asyncio
async def test_place_signal_places_entry_then_sl_then_3_tps() -> None:
    """The full chain: 1 entry + 1 SL + 3 TPs = 5 order placements.
    Persisted to Firestore twice: once after entry (so FSM can
    handle entry-fill even if SL/TP placement crashes), again after
    all order ids are captured."""
    placer = _placer_with_mock_results()
    persisted: list = []
    with patch.object(
        position_state, "put_position", side_effect=lambda p: persisted.append(p)
    ):
        await position_fsm.place_signal(
            firebase_uid="fb-x",
            signal_id="sig-1",
            symbol="BTCUSDT",
            direction="LONG",
            entry_price=29000.0,
            sl_price=28500.0,
            tp1_price=29500.0,
            tp2_price=30000.0,
            tp3_price=30500.0,
            total_qty=1.0,
            tp1_qty=0.3,
            tp2_qty=0.4,
            tp3_qty=0.3,
            order_placer_factory=lambda uid: placer,
        )
    placer.place_market_entry.assert_awaited_once()
    placer.place_stop_loss.assert_awaited_once()
    assert placer.place_take_profit.await_count == 3
    # Persisted at least twice: once after entry, once after all
    # placements complete.
    assert len(persisted) >= 2
    # Last persist captures all the order ids.
    final = persisted[-1]
    assert final.entry_order_id == 1001
    assert final.sl_order_id == 2001
    assert final.tp1_order_id == 3001
    assert final.tp2_order_id == 3002
    assert final.tp3_order_id == 3003


@pytest.mark.asyncio
async def test_place_signal_propagates_entry_failure() -> None:
    """Entry placement failure must raise — caller (orchestrator)
    decides retry / mark-user-disabled / Telegram-alert.  The
    position never opens, so no SL/TP cleanup is needed."""
    placer = _placer_with_mock_results()
    placer.place_market_entry = AsyncMock(
        side_effect=order_placer.OrderRejectedByBinance("insufficient margin")
    )
    with patch.object(position_state, "put_position"):
        with pytest.raises(order_placer.OrderRejectedByBinance):
            await position_fsm.place_signal(
                firebase_uid="fb-x",
                signal_id="sig-1",
                symbol="BTCUSDT",
                direction="LONG",
                entry_price=29000.0,
                sl_price=28500.0,
                tp1_price=29500.0,
                tp2_price=30000.0,
                tp3_price=30500.0,
                total_qty=1.0,
                tp1_qty=0.3,
                tp2_qty=0.4,
                tp3_qty=0.3,
                order_placer_factory=lambda uid: placer,
            )
    # SL + TPs should NOT be attempted after entry failure.
    placer.place_stop_loss.assert_not_called()
    placer.place_take_profit.assert_not_called()


@pytest.mark.asyncio
async def test_place_signal_tolerates_sl_failure() -> None:
    """SL placement failure is best-effort — position remains OPEN
    with TPs intact.  Operator can manually place an SL via the
    Lumin app or the position can ride to a TP / get manually closed.
    Logging captures the issue for follow-up."""
    placer = _placer_with_mock_results()
    placer.place_stop_loss = AsyncMock(
        side_effect=order_placer.OrderRejectedByBinance("stop too close")
    )
    persisted: list = []
    with patch.object(
        position_state, "put_position", side_effect=lambda p: persisted.append(p)
    ):
        # Must not raise.
        result = await position_fsm.place_signal(
            firebase_uid="fb-x",
            signal_id="sig-1",
            symbol="BTCUSDT",
            direction="LONG",
            entry_price=29000.0,
            sl_price=28500.0,
            tp1_price=29500.0,
            tp2_price=30000.0,
            tp3_price=30500.0,
            total_qty=1.0,
            tp1_qty=0.3,
            tp2_qty=0.4,
            tp3_qty=0.3,
            order_placer_factory=lambda uid: placer,
        )
    assert result.entry_order_id == 1001
    assert result.sl_order_id == 0  # didn't land
    # TPs still attempted.
    assert placer.place_take_profit.await_count == 3
