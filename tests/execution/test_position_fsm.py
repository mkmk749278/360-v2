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

import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution import events as events_mod
from src.execution import order_placer
from src.execution import position_fsm
from src.execution import position_state


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch: pytest.MonkeyPatch):
    position_state.reset_for_test()
    # PR-14 follow-up wires safety gates into place_signal.  Tests
    # that exercise place_signal need the symbol allowlist set AND
    # the tripwire singletons reset between tests so per-test state
    # doesn't bleed.
    monkeypatch.setenv("TRIPWIRE_SYMBOL_ALLOWLIST", "BTCUSDT,ETHUSDT,SOLUSDT")
    from src.execution import tripwires as _tripwires
    from src.execution import kill_switch as _kill_switch
    _tripwires.reset_singletons_for_test()
    _kill_switch.reset_for_test()
    yield
    position_state.reset_for_test()
    _tripwires.reset_singletons_for_test()
    _kill_switch.reset_for_test()


def _stub_placer_factory():
    """Return a (factory, placer) pair.  The factory returns the same
    mock placer instance so tests can assert against it.  All placer
    methods are AsyncMocks that return successful OrderPlacementResults
    by default — override per test if needed."""
    placer = MagicMock()
    placer.cancel_order = AsyncMock(return_value=None)
    placer.ensure_cross_margin = AsyncMock(return_value=True)
    placer.place_market_close = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=9001, client_order_id="lumin_sig-1_close",
            status="FILLED", avg_price=0.0, binance_body={},
        )
    )
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
async def test_pretp_full_close_transitions_to_closed_no_be_shift() -> None:
    """Full-close pre-TP (grab_fraction == 1.00, or a MIN_NOTIONAL upgrade
    to full close): the fill closes 100% of qty so there is NO residual.
    The position must go straight to CLOSED with close_reason="PRE_TP",
    cancel ALL legs (SL + TP1 + TP2 + TP3), and must NOT place a break-even
    SL.  Regression for the orphan bug: previously this stranded the
    position in non-terminal PRE_TP_FIRED with a BE-SL + live TP1 against
    zero residual, so the app showed it ACTIVE forever while Binance was
    already flat.
    """
    factory, placer = _stub_placer_factory()
    fsm = position_fsm.PositionFSM("fb-x", order_placer_factory=factory)
    position = _pending_position()
    position.state = position_state.PositionState.OPEN
    position.entry_price_filled = 29000.0
    position.sl_order_id = 2001
    position.tp1_order_id = 3001
    position.tp2_order_id = 3002
    position.tp3_order_id = 3003
    captured: list = []
    with patch.object(position_state, "get_position", return_value=position), patch.object(
        position_state, "put_position", side_effect=lambda p: captured.append(p)
    ):
        await fsm.handle_event(
            _otu(
                client_order_id=position_state.coid_pretp("sig-1"),
                last_filled_qty=1.0,  # == total_qty → full close
                realized_pnl=40.0,
            )
        )
    assert captured[0].state == position_state.PositionState.CLOSED
    assert captured[0].close_reason == "PRE_TP"
    assert captured[0].closed_qty == 1.0
    assert captured[0].closed_at is not None
    # All four legs cancelled — nothing left to ride to TP1.
    assert placer.cancel_order.await_count == 4
    cancelled_ids = {
        call.kwargs["order_id"] for call in placer.cancel_order.call_args_list
    }
    assert cancelled_ids == {2001, 3001, 3002, 3003}
    # No break-even SL placed — there is no residual to protect.
    placer.place_stop_loss.assert_not_called()
    assert captured[0].sl_order_id == 0
    assert captured[0].tp1_order_id == 0
    assert captured[0].tp2_order_id == 0
    assert captured[0].tp3_order_id == 0


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
    # PR-C: native pre-TP LIMIT placed at dispatch time.
    placer.place_pretp_limit = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=4001, client_order_id="lumin_sig-1_pretp",
            status="NEW", avg_price=0.0, binance_body={},
        )
    )
    # 2026-06-01: margin enforcement + force-close backstop.
    placer.ensure_cross_margin = AsyncMock(return_value=True)
    placer.place_market_close = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=9001, client_order_id="lumin_sig-1_close",
            status="FILLED", avg_price=0.0, binance_body={},
        )
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
    placer.place_pretp_limit.assert_awaited_once()
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
    assert final.pretp_order_id == 4001


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
async def test_place_signal_force_closes_on_sl_failure() -> None:
    """SL placement failure is NO LONGER tolerated (JTOUSDT 2026-06-01).

    A deterministic Binance rejection of the SL means the position would
    otherwise sit OPEN with no stop.  The FSM force-closes the entry at
    market and marks the position CLOSED (reason SL_PLACEMENT_FAILED)
    rather than leave it naked.  TPs are NOT placed (we exit early)."""
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
    assert result.sl_order_id == 0  # SL didn't land
    # Force-close fired for the full entry qty.
    placer.place_market_close.assert_awaited_once()
    _, close_kwargs = placer.place_market_close.await_args
    assert close_kwargs["quantity"] == 1.0
    # Position marked terminal with the diagnostic close reason.
    assert result.state == position_state.PositionState.CLOSED
    assert result.close_reason == "SL_PLACEMENT_FAILED"
    # We exit before the TP bracket — no TP legs attempted.
    assert placer.place_take_profit.await_count == 0


def _rejected_with_code(code: int) -> order_placer.OrderRejectedByBinance:
    """Build an OrderRejectedByBinance carrying a Binance numeric code so
    _binance_reject_code can classify it transient vs fatal."""
    resp = SimpleNamespace(binance_body={"code": code, "msg": "rejected"})
    return order_placer.OrderRejectedByBinance("rejected", signing_response=resp)


@pytest.mark.asyncio
async def test_place_signal_retries_sl_on_transient_then_succeeds(
    monkeypatch,
) -> None:
    """A transient (unreachable) SL failure is retried; once it lands the
    position keeps its TP bracket and is NOT force-closed."""
    import config
    monkeypatch.setattr(config, "SL_RETRY_BACKOFF_SEC", 0.0, raising=False)
    placer = _placer_with_mock_results()
    placer.place_stop_loss = AsyncMock(
        side_effect=[
            order_placer.OrderPlacementUnreachable("signing socket blip"),
            order_placer.OrderPlacementResult(
                order_id=2001, client_order_id="lumin_sig-1_sl",
                status="NEW", avg_price=0.0, binance_body={},
            ),
        ]
    )
    with patch.object(position_state, "put_position", new=MagicMock()):
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
    assert placer.place_stop_loss.await_count == 2  # retried once
    assert result.sl_order_id == 2001  # landed on attempt 2
    placer.place_market_close.assert_not_awaited()  # not force-closed
    assert placer.place_take_profit.await_count == 3  # bracket intact


@pytest.mark.asyncio
async def test_place_signal_retries_sl_on_2021_then_succeeds(monkeypatch) -> None:
    """2026-06-01 regression fix: -2021 'would immediately trigger' is a
    TRANSIENT mark-price wick right after entry, not a fatal reject.  It is
    retried (after backoff) and once the SL lands the position is NOT
    force-closed — the IDUSDT/AIAUSDT 4-second-close bug is gone."""
    import config
    monkeypatch.setattr(config, "SL_RETRY_BACKOFF_SEC", 0.0, raising=False)
    placer = _placer_with_mock_results()
    placer.place_stop_loss = AsyncMock(
        side_effect=[
            _rejected_with_code(-2021),  # transient wick on attempt 1
            order_placer.OrderPlacementResult(
                order_id=2001, client_order_id="lumin_sig-1_sl",
                status="NEW", avg_price=0.0, binance_body={},
            ),
        ]
    )
    with patch.object(position_state, "put_position", new=MagicMock()):
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
    assert placer.place_stop_loss.await_count == 2  # -2021 retried
    assert result.sl_order_id == 2001
    placer.place_market_close.assert_not_awaited()  # NOT force-closed
    assert result.state != position_state.PositionState.CLOSED


@pytest.mark.asyncio
async def test_place_signal_force_closes_on_persistent_2021(monkeypatch) -> None:
    """If -2021 persists across every attempt (price genuinely sits at the
    stop), force-close is correct — closing at the stop is the right exit."""
    import config
    monkeypatch.setattr(config, "SL_RETRY_BACKOFF_SEC", 0.0, raising=False)
    # Pin the attempt count so this asserts the exhaustion path deterministically
    # regardless of the SL_PLACEMENT_MAX_ATTEMPTS default (raised to 6 on
    # 2026-06-01 to widen the transient-wick retry window).
    monkeypatch.setattr(config, "SL_PLACEMENT_MAX_ATTEMPTS", 3, raising=False)
    placer = _placer_with_mock_results()
    placer.place_stop_loss = AsyncMock(side_effect=_rejected_with_code(-2021))
    with patch.object(position_state, "put_position", new=MagicMock()):
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
    # Exhausted all attempts → force-close (invariant holds).
    assert placer.place_stop_loss.await_count == 3
    placer.place_market_close.assert_awaited_once()
    assert result.state == position_state.PositionState.CLOSED


@pytest.mark.asyncio
async def test_place_signal_force_closes_on_fatal_reject_without_retry() -> None:
    """A deterministic reject (tick size -4014) is NOT retried — retrying the
    same request can't fix it — so it force-closes after a single attempt."""
    placer = _placer_with_mock_results()
    placer.place_stop_loss = AsyncMock(side_effect=_rejected_with_code(-4014))
    with patch.object(position_state, "put_position", new=MagicMock()):
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
    assert placer.place_stop_loss.await_count == 1  # not retried
    placer.place_market_close.assert_awaited_once()
    assert result.close_reason == "SL_PLACEMENT_FAILED"


# ---------------------------------------------------------------------------
# PR-C: native pre-TP LIMIT placement at dispatch time
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_place_signal_places_native_pretp_limit() -> None:
    """step 6: LIMIT placed at pretp_threshold_price for
    pretp_fraction of total_qty.  pretp_order_id is captured on the
    returned position."""
    placer = _placer_with_mock_results()
    persisted: list = []
    with patch.object(
        position_state, "put_position", side_effect=lambda p: persisted.append(p)
    ):
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
            pretp_fraction=0.5,
            order_placer_factory=lambda uid: placer,
        )
    placer.place_pretp_limit.assert_awaited_once()
    kw = placer.place_pretp_limit.call_args.kwargs
    assert kw["signal_id"] == "sig-1"
    assert kw["symbol"] == "BTCUSDT"
    assert kw["direction"] == "LONG"
    # limit_price is the computed threshold (entry * 1.0032 default)
    assert kw["limit_price"] > 29000.0
    # quantity = total_qty * pretp_fraction = 0.5
    assert abs(kw["quantity"] - 0.5) < 1e-6
    assert result.pretp_order_id == 4001


@pytest.mark.asyncio
async def test_place_signal_skips_pretp_limit_when_fraction_zero() -> None:
    """PR-F allowlist suppression: pretp_fraction=0 must skip the
    native LIMIT entirely.  pretp_order_id stays 0."""
    placer = _placer_with_mock_results()
    with patch.object(position_state, "put_position"):
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
            pretp_fraction=0.0,
            order_placer_factory=lambda uid: placer,
        )
    placer.place_pretp_limit.assert_not_called()
    assert result.pretp_order_id == 0
    # Verify clamping fix: pretp_fraction stored as 0.0, not 0.30.
    assert result.pretp_fraction == 0.0


@pytest.mark.asyncio
async def test_place_signal_profile_a_full_grab_skips_tp_bracket() -> None:
    """Profile A ('close all at threshold'): grab_fraction=1.0 → pre-TP
    LIMIT covers the FULL position, so the native TP bracket would just be
    redundant reduce-only orders cancelled on the pre-TP fill.  The FSM
    skips them.  The pre-TP LIMIT is still placed for the full qty."""
    placer = _placer_with_mock_results()
    with patch.object(position_state, "put_position"):
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
            pretp_fraction=1.0,
            order_placer_factory=lambda uid: placer,
        )
    # No native TP bracket — pre-TP grabs everything.
    assert placer.place_take_profit.await_count == 0
    # SL still placed (protects until the pre-TP LIMIT fills).
    placer.place_stop_loss.assert_awaited_once()
    # pre-TP LIMIT placed for the FULL position.
    placer.place_pretp_limit.assert_awaited_once()
    assert abs(placer.place_pretp_limit.call_args.kwargs["quantity"] - 1.0) < 1e-6
    assert result.pretp_fraction == 1.0


@pytest.mark.asyncio
async def test_place_signal_honours_per_user_threshold() -> None:
    """The per-user pretp_threshold_pct flows into the LIMIT price.  A
    0.50% threshold rests the LIMIT further from entry than the 0.32%
    default — this is the 'close at 0.3% vs 0.5%' per-user dial."""
    placer = _placer_with_mock_results()
    with patch.object(position_state, "put_position"):
        await position_fsm.place_signal(
            firebase_uid="fb-x",
            signal_id="sig-1",
            symbol="BTCUSDT",
            direction="LONG",
            entry_price=1000.0,
            sl_price=985.0,
            tp1_price=1010.0,
            tp2_price=1020.0,
            tp3_price=1030.0,
            total_qty=1.0,
            tp1_qty=0.3,
            tp2_qty=0.4,
            tp3_qty=0.3,
            pretp_threshold_pct=0.50,
            pretp_fraction=0.5,
            order_placer_factory=lambda uid: placer,
        )
    # 0.50% above a 1000 entry → 1005.0 (vs 1003.2 at the 0.32 default).
    limit_price = placer.place_pretp_limit.call_args.kwargs["limit_price"]
    assert abs(limit_price - 1005.0) < 1e-6


@pytest.mark.asyncio
async def test_place_signal_tolerates_pretp_limit_failure() -> None:
    """Best-effort: if the native LIMIT fails, position is still
    returned with pretp_order_id=0.  The tick-based fallback will
    fire MARKET when mark price crosses threshold."""
    placer = _placer_with_mock_results()
    placer.place_pretp_limit = AsyncMock(
        side_effect=order_placer.OrderRejectedByBinance("price too far")
    )
    with patch.object(position_state, "put_position"):
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
            pretp_fraction=0.5,
            order_placer_factory=lambda uid: placer,
        )
    # Must not raise; pretp_order_id stays 0 so fallback can fire.
    assert result.pretp_order_id == 0
    assert result.entry_order_id == 1001


# ---------------------------------------------------------------------------
# Safety-gate enforcement on place_signal (PR-14 wiring follow-up)
# ---------------------------------------------------------------------------


def _common_signal_kwargs(placer):
    return dict(
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


@pytest.mark.asyncio
async def test_place_signal_refuses_when_symbol_not_in_allowlist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The doctrine canary: a signal for a symbol not on the
    tripwire allowlist must NEVER reach the order-placement chain
    no matter what.  Default-empty allowlist would block everything;
    here we explicitly set the allowlist to symbols that DON'T
    include the signal's symbol to verify the exact gate fires."""
    from src.execution import tripwires
    monkeypatch.setenv("TRIPWIRE_SYMBOL_ALLOWLIST", "ETHUSDT,SOLUSDT")
    placer = _placer_with_mock_results()
    with patch.object(position_state, "put_position"):
        with pytest.raises(tripwires.SymbolNotAllowed):
            await position_fsm.place_signal(**_common_signal_kwargs(placer))
    # CRITICAL: NO order placement attempt — verify the gate runs
    # BEFORE the entry order is sent.  A regression here would mean
    # a malicious / mistaken signal could place orders before the
    # tripwire fires.
    placer.place_market_entry.assert_not_called()
    placer.place_stop_loss.assert_not_called()
    placer.place_take_profit.assert_not_called()


@pytest.mark.asyncio
async def test_place_signal_refuses_when_globally_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The #431 no-staged-beta safety floor: when
    ``auto_trade_globally_enabled = False`` (which is the DEFAULT on
    fresh deploy), every signal is rejected.  Operator must
    explicitly flip the Firestore flag before any user can
    auto-trade."""
    from src.execution import kill_switch
    from unittest.mock import MagicMock

    # Build a KillSwitchClient with a real fake DB so init runs.
    fake_db = MagicMock()
    # Document doesn't exist → both flags default False → NOT enabled.
    fake_doc = MagicMock()
    fake_doc.get.return_value = SimpleNamespace(exists=False, to_dict=lambda: {})
    fake_db.collection.return_value.document.return_value = fake_doc
    kill_switch._client = kill_switch.KillSwitchClient(fake_db)
    monkeypatch.setenv("TRIPWIRE_SYMBOL_ALLOWLIST", "BTCUSDT")
    placer = _placer_with_mock_results()
    with patch.object(position_state, "put_position"):
        with pytest.raises(position_fsm.NotGloballyEnabledError):
            await position_fsm.place_signal(**_common_signal_kwargs(placer))
    placer.place_market_entry.assert_not_called()


@pytest.mark.asyncio
async def test_place_signal_succeeds_when_globally_enabled() -> None:
    """Counter-canary: once the operator flips
    auto_trade_globally_enabled = True, the gate stops firing.
    Confirms the gate isn't accidentally permanent."""
    from src.execution import kill_switch
    from unittest.mock import MagicMock

    fake_db = MagicMock()
    fake_doc = MagicMock()
    fake_doc.get.return_value = SimpleNamespace(
        exists=True,
        to_dict=lambda: {
            "engaged": False,
            "auto_trade_globally_enabled": True,
            "auto_trade_disabled": False,
        },
    )
    fake_db.collection.return_value.document.return_value = fake_doc
    kill_switch._client = kill_switch.KillSwitchClient(fake_db)
    placer = _placer_with_mock_results()
    with patch.object(position_state, "put_position"):
        result = await position_fsm.place_signal(**_common_signal_kwargs(placer))
    assert result.entry_order_id == 1001
    placer.place_market_entry.assert_awaited_once()


@pytest.mark.asyncio
async def test_place_signal_safety_gates_skipped_when_kill_switch_not_initialised() -> None:
    """In dev / test contexts that haven't booted the full server-
    side execution stack (no GCP wired), the KillSwitchClient stays
    uninitialised.  ``_enforce_safety_gates`` skips the Firestore-
    backed checks in this case — tripwires (symbol allowlist + rate
    limit) still fire.  Verifies dev path doesn't crash."""
    from src.execution import kill_switch
    kill_switch.reset_for_test()  # ensure not initialised
    placer = _placer_with_mock_results()
    with patch.object(position_state, "put_position"):
        # With KS not initialised but symbol on allowlist, signal
        # places normally.  This is the dev / test happy path.
        result = await position_fsm.place_signal(**_common_signal_kwargs(placer))
    assert result.entry_order_id == 1001


# ---------------------------------------------------------------------------
# PretpDispatcher track / untrack wiring
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_entry_fill_to_open_calls_track() -> None:
    """When the FSM transitions PENDING → OPEN on entry fill,
    it must call pretp_dispatcher.track(symbol) if a dispatcher
    instance is set."""
    from src.execution import pretp_dispatcher as _pd

    tracked: list = []
    mock_dispatcher = MagicMock()
    mock_dispatcher.track = AsyncMock(side_effect=lambda sym: tracked.append(sym))

    original = _pd.get_instance()
    _pd.set_instance(mock_dispatcher)
    try:
        fsm = position_fsm.PositionFSM("fb-track-test")
        position = _pending_position("sig-track")
        with patch.object(position_state, "get_position", return_value=position), \
             patch.object(position_state, "put_position"):
            await fsm.handle_event(
                _otu(
                    client_order_id=position_state.coid_entry("sig-track"),
                    cumulative_filled_qty=1.0,
                    order_status="FILLED",
                )
            )
        await asyncio.sleep(0)
        assert "BTCUSDT" in tracked
    finally:
        _pd.set_instance(original)


@pytest.mark.asyncio
async def test_sl_fill_calls_untrack() -> None:
    """SL fill → CLOSED must call pretp_dispatcher.untrack(symbol)."""
    from src.execution import pretp_dispatcher as _pd

    untracked: list = []
    mock_dispatcher = MagicMock()
    mock_dispatcher.untrack = AsyncMock(side_effect=lambda sym: untracked.append(sym))

    original = _pd.get_instance()
    _pd.set_instance(mock_dispatcher)
    try:
        fsm = position_fsm.PositionFSM("fb-untrack-sl")
        position = _pending_position("sig-sl")
        position.state = position_state.PositionState.OPEN
        with patch.object(position_state, "get_position", return_value=position), \
             patch.object(position_state, "put_position"):
            await fsm.handle_event(
                _otu(
                    client_order_id=position_state.coid_sl("sig-sl"),
                    order_status="FILLED",
                )
            )
        await asyncio.sleep(0)
        assert "BTCUSDT" in untracked
    finally:
        _pd.set_instance(original)


@pytest.mark.asyncio
async def test_no_track_when_dispatcher_not_set() -> None:
    """No crash when pretp_dispatcher singleton is None (dev / test mode
    without bootstrap having wired the mark-price feed)."""
    from src.execution import pretp_dispatcher as _pd

    original = _pd.get_instance()
    _pd.set_instance(None)
    try:
        fsm = position_fsm.PositionFSM("fb-no-dispatcher")
        position = _pending_position("sig-no-disp")
        with patch.object(position_state, "get_position", return_value=position), \
             patch.object(position_state, "put_position"):
            await fsm.handle_event(
                _otu(
                    client_order_id=position_state.coid_entry("sig-no-disp"),
                    cumulative_filled_qty=1.0,
                    order_status="FILLED",
                )
            )
        await asyncio.sleep(0)
    finally:
        _pd.set_instance(original)


# ---------------------------------------------------------------------------
# SL re-anchoring: fill slippage past the signal SL (2026-06-01 regression)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_place_signal_reanchors_sl_for_short_fill_above_sl() -> None:
    """SHORT fill ABOVE signal SL → Binance -2021 on every attempt → force-close.

    Root cause: signal_entry=2.322, SL=2.340 (+0.78%).  Price pumps to 2.376
    before the MARKET fires.  SL 2.340 < fill 2.376 for a SHORT means the
    STOP_MARKET BUY would immediately trigger — -2021 on every retry.

    Fix: re-anchor SL to fill_price * (1 + sl_fraction) so the stop is valid.
    Verify: SL placed above fill, NO force-close, position stays open-bound."""
    placer = _placer_with_mock_results()
    placer.place_market_entry = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=1001, client_order_id="lumin_sig-1_entry",
            status="FILLED", avg_price=2.376, binance_body={},
        )
    )
    with patch.object(position_state, "put_position"):
        result = await position_fsm.place_signal(
            firebase_uid="fb-x",
            signal_id="sig-1",
            symbol="SOLUSDT",
            direction="SHORT",
            entry_price=2.322,
            sl_price=2.340,    # 0.78% above signal entry — correct at generation
            tp1_price=2.270,
            tp2_price=2.220,
            tp3_price=2.170,
            total_qty=10.0,
            tp1_qty=3.0,
            tp2_qty=4.0,
            tp3_qty=3.0,
            order_placer_factory=lambda uid: placer,
        )
    # SL placed, position NOT force-closed.
    placer.place_stop_loss.assert_awaited_once()
    placer.place_market_close.assert_not_awaited()
    assert result.state != position_state.PositionState.CLOSED

    # Re-anchored SL must sit ABOVE the fill (valid STOP_MARKET BUY for SHORT).
    sl_kwargs = placer.place_stop_loss.call_args.kwargs
    assert sl_kwargs["stop_price"] > 2.376

    # Distance fraction is preserved: (2.340−2.322)/2.322 ≈ 0.00775.
    # Expected new SL ≈ 2.376 × (1 + 0.00775) ≈ 2.394.
    expected = 2.376 * (2.340 / 2.322)
    assert abs(sl_kwargs["stop_price"] - expected) < 0.001


@pytest.mark.asyncio
async def test_place_signal_reanchors_sl_for_long_fill_below_sl() -> None:
    """LONG fill BELOW signal SL → same immediate-trigger problem, mirrored.

    entry_target=1000, SL=992 (0.8% below).  Market drops before execution:
    fill=990 < SL=992.  STOP_MARKET SELL at 992 when price is 990 fires
    immediately (-2021).  Re-anchor to fill * (1 − 0.008) = 982.08."""
    placer = _placer_with_mock_results()
    placer.place_market_entry = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=1001, client_order_id="lumin_sig-1_entry",
            status="FILLED", avg_price=990.0, binance_body={},
        )
    )
    with patch.object(position_state, "put_position"):
        result = await position_fsm.place_signal(
            firebase_uid="fb-x",
            signal_id="sig-1",
            symbol="SOLUSDT",
            direction="LONG",
            entry_price=1000.0,
            sl_price=992.0,    # 0.8% below signal entry
            tp1_price=1010.0,
            tp2_price=1020.0,
            tp3_price=1030.0,
            total_qty=1.0,
            tp1_qty=0.3,
            tp2_qty=0.4,
            tp3_qty=0.3,
            order_placer_factory=lambda uid: placer,
        )
    placer.place_stop_loss.assert_awaited_once()
    placer.place_market_close.assert_not_awaited()

    sl_kwargs = placer.place_stop_loss.call_args.kwargs
    # Re-anchored SL is BELOW the fill (valid STOP_MARKET SELL for LONG).
    assert sl_kwargs["stop_price"] < 990.0
    # Fraction preserved: 990 × (992/1000) = 982.08
    expected = 990.0 * (992.0 / 1000.0)
    assert abs(sl_kwargs["stop_price"] - expected) < 0.01


@pytest.mark.asyncio
async def test_place_signal_no_reanchor_when_fill_inside_sl() -> None:
    """Normal fill (no slippage past SL) must NOT re-anchor the SL.

    LONG: fill=29010, SL=28500 — fill is well above SL.
    Original signal SL preserved exactly."""
    placer = _placer_with_mock_results()
    placer.place_market_entry = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=1001, client_order_id="lumin_sig-1_entry",
            status="FILLED", avg_price=29010.0, binance_body={},
        )
    )
    with patch.object(position_state, "put_position"):
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
    sl_kwargs = placer.place_stop_loss.call_args.kwargs
    # Original SL preserved — no re-anchoring.
    assert abs(sl_kwargs["stop_price"] - 28500.0) < 0.001


@pytest.mark.asyncio
async def test_place_signal_pretp_limit_anchored_to_fill_not_signal_entry() -> None:
    """When fill differs from signal entry, the pre-TP LIMIT must rest at
    fill_price ± threshold%, not signal_entry ± threshold%.

    A pre-TP LIMIT anchored to a stale signal entry price sits at the wrong
    level — the user's threshold distance is measured from a price they never
    traded at.  Fill-anchored LIMIT fires at the right relative move."""
    placer = _placer_with_mock_results()
    # LONG fills 1% BELOW signal entry (1000 → 990 fill).
    placer.place_market_entry = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=1001, client_order_id="lumin_sig-1_entry",
            status="FILLED", avg_price=990.0, binance_body={},
        )
    )
    with patch.object(position_state, "put_position"):
        await position_fsm.place_signal(
            firebase_uid="fb-x",
            signal_id="sig-1",
            symbol="SOLUSDT",
            direction="LONG",
            entry_price=1000.0,
            sl_price=985.0,    # 1.5% below — NOT below fill, no SL re-anchor
            tp1_price=1010.0,
            tp2_price=1020.0,
            tp3_price=1030.0,
            total_qty=1.0,
            tp1_qty=0.3,
            tp2_qty=0.4,
            tp3_qty=0.3,
            pretp_threshold_pct=0.32,
            pretp_fraction=0.5,
            order_placer_factory=lambda uid: placer,
        )
    kw = placer.place_pretp_limit.call_args.kwargs
    # Pre-TP threshold: fill (990) × 1.0032 = 993.168
    # NOT signal entry (1000) × 1.0032 = 1003.2
    assert abs(kw["limit_price"] - 990.0 * 1.0032) < 0.01
    assert kw["limit_price"] < 1000.0  # definitely NOT signal-entry-anchored
