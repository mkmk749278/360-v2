"""Tests for FundingExitWatcher and helpers."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution.funding_exit_watcher import (
    FUNDING_PERIOD_SEC,
    FundingExitWatcher,
    _close_for_funding,
    seconds_until_next_funding,
)


# ---------------------------------------------------------------------------
# seconds_until_next_funding
# ---------------------------------------------------------------------------


class TestSecondsUntilNextFunding:
    def test_at_boundary_zero(self):
        # Exactly on a funding timestamp: full period remaining
        result = seconds_until_next_funding(now=0.0)
        assert result == float(FUNDING_PERIOD_SEC)

    def test_one_second_after_boundary(self):
        result = seconds_until_next_funding(now=1.0)
        assert abs(result - (FUNDING_PERIOD_SEC - 1)) < 0.01

    def test_inside_window(self):
        # 60 s before a funding event
        ts = FUNDING_PERIOD_SEC - 60.0
        result = seconds_until_next_funding(now=ts)
        assert abs(result - 60.0) < 0.01

    def test_half_period(self):
        result = seconds_until_next_funding(now=float(FUNDING_PERIOD_SEC) / 2)
        assert abs(result - float(FUNDING_PERIOD_SEC) / 2) < 0.01

    def test_uses_time_time_when_no_arg(self):
        now = time.time()
        result = seconds_until_next_funding()
        expected = FUNDING_PERIOD_SEC - (now % FUNDING_PERIOD_SEC)
        # Allow 1 s tolerance for test execution time
        assert abs(result - expected) < 1.0


# ---------------------------------------------------------------------------
# FundingExitWatcher._check
# ---------------------------------------------------------------------------


def _make_position(
    *,
    signal_id: str = "sig1",
    symbol: str = "BTCUSDT",
    side: str = "LONG",
    entry_regime: str = "TRENDING_UP",
    state_name: str = "OPEN",
    sl_order_id: int = 1001,
    tp1_order_id: int = 2001,
    total_qty: float = 0.01,
    closed_qty: float = 0.0,
) -> MagicMock:
    from src.execution.position_state import PositionState

    pos = MagicMock()
    pos.signal_id = signal_id
    pos.symbol = symbol
    pos.side = side
    pos.entry_regime = entry_regime
    pos.state = getattr(PositionState, state_name)
    pos.sl_order_id = sl_order_id
    pos.sl_be_order_id = 0
    pos.tp1_order_id = tp1_order_id
    pos.tp2_order_id = 0
    pos.tp3_order_id = 0
    pos.total_qty = total_qty
    pos.closed_qty = closed_qty
    return pos


class TestFundingExitWatcherCheck:
    """Unit tests for FundingExitWatcher._check with mocked dependencies."""

    def _make_watcher(self) -> FundingExitWatcher:
        return FundingExitWatcher()

    async def test_no_action_when_outside_window(self):
        watcher = self._make_watcher()
        with (
            patch(
                "src.execution.funding_exit_watcher.seconds_until_next_funding",
                return_value=300.0,
            ),
            patch("config.PRE_FUNDING_EXIT_WINDOW_SEC", 120),
            patch(
                "src.execution.funding_exit_watcher._close_for_funding",
                new_callable=AsyncMock,
            ) as mock_close,
        ):
            await watcher._check()
            mock_close.assert_not_called()

    async def test_no_action_when_position_state_not_initialised(self):
        watcher = self._make_watcher()
        with (
            patch(
                "src.execution.funding_exit_watcher.seconds_until_next_funding",
                return_value=60.0,
            ),
            patch("config.PRE_FUNDING_EXIT_WINDOW_SEC", 120),
            patch(
                "src.execution.position_state.is_initialised", return_value=False
            ),
            patch(
                "src.execution.funding_exit_watcher._close_for_funding",
                new_callable=AsyncMock,
            ) as mock_close,
        ):
            await watcher._check()
            mock_close.assert_not_called()

    async def test_closes_trending_up_long_within_window(self):
        watcher = self._make_watcher()
        pos = _make_position(entry_regime="TRENDING_UP", side="LONG", state_name="OPEN")

        mock_placer = MagicMock()
        with (
            patch(
                "src.execution.funding_exit_watcher.seconds_until_next_funding",
                return_value=90.0,
            ),
            patch("config.PRE_FUNDING_EXIT_WINDOW_SEC", 120),
            patch(
                "src.execution.position_state.is_initialised", return_value=True
            ),
            patch(
                "src.execution.signal_dispatch._active_uids",
                return_value=["uid1"],
            ),
            patch(
                "src.execution.position_state.list_positions_for_user",
                return_value=[pos],
            ),
            patch(
                "src.execution.position_state.is_terminal", return_value=False
            ),
            patch(
                "src.execution.order_placer.OrderPlacer",
                return_value=mock_placer,
            ),
            patch(
                "src.execution.funding_exit_watcher._close_for_funding",
                new_callable=AsyncMock,
            ) as mock_close,
        ):
            await watcher._check()
            mock_close.assert_awaited_once_with("uid1", pos, mock_placer)

    async def test_skips_non_trending_up_positions(self):
        watcher = self._make_watcher()
        pos_ranging = _make_position(entry_regime="RANGING", side="LONG")
        pos_quiet = _make_position(entry_regime="QUIET", side="LONG")

        with (
            patch(
                "src.execution.funding_exit_watcher.seconds_until_next_funding",
                return_value=90.0,
            ),
            patch("config.PRE_FUNDING_EXIT_WINDOW_SEC", 120),
            patch(
                "src.execution.position_state.is_initialised", return_value=True
            ),
            patch(
                "src.execution.signal_dispatch._active_uids",
                return_value=["uid1"],
            ),
            patch(
                "src.execution.position_state.list_positions_for_user",
                return_value=[pos_ranging, pos_quiet],
            ),
            patch(
                "src.execution.position_state.is_terminal", return_value=False
            ),
            patch(
                "src.execution.funding_exit_watcher._close_for_funding",
                new_callable=AsyncMock,
            ) as mock_close,
        ):
            await watcher._check()
            mock_close.assert_not_called()

    async def test_skips_short_positions(self):
        watcher = self._make_watcher()
        pos = _make_position(entry_regime="TRENDING_UP", side="SHORT")

        with (
            patch(
                "src.execution.funding_exit_watcher.seconds_until_next_funding",
                return_value=90.0,
            ),
            patch("config.PRE_FUNDING_EXIT_WINDOW_SEC", 120),
            patch(
                "src.execution.position_state.is_initialised", return_value=True
            ),
            patch(
                "src.execution.signal_dispatch._active_uids",
                return_value=["uid1"],
            ),
            patch(
                "src.execution.position_state.list_positions_for_user",
                return_value=[pos],
            ),
            patch(
                "src.execution.position_state.is_terminal", return_value=False
            ),
            patch(
                "src.execution.funding_exit_watcher._close_for_funding",
                new_callable=AsyncMock,
            ) as mock_close,
        ):
            await watcher._check()
            mock_close.assert_not_called()

    async def test_skips_trailing_state(self):
        """TRAILING positions are managed by Binance native trailing stop — skip."""
        watcher = self._make_watcher()
        pos = _make_position(
            entry_regime="TRENDING_UP", side="LONG", state_name="TRAILING"
        )

        with (
            patch(
                "src.execution.funding_exit_watcher.seconds_until_next_funding",
                return_value=90.0,
            ),
            patch("config.PRE_FUNDING_EXIT_WINDOW_SEC", 120),
            patch(
                "src.execution.position_state.is_initialised", return_value=True
            ),
            patch(
                "src.execution.signal_dispatch._active_uids",
                return_value=["uid1"],
            ),
            patch(
                "src.execution.position_state.list_positions_for_user",
                return_value=[pos],
            ),
            patch(
                "src.execution.position_state.is_terminal", return_value=False
            ),
            patch(
                "src.execution.funding_exit_watcher._close_for_funding",
                new_callable=AsyncMock,
            ) as mock_close,
        ):
            await watcher._check()
            mock_close.assert_not_called()

    async def test_case_insensitive_regime_and_side(self):
        watcher = self._make_watcher()
        pos = _make_position(entry_regime="trending_up", side="long")

        with (
            patch(
                "src.execution.funding_exit_watcher.seconds_until_next_funding",
                return_value=90.0,
            ),
            patch("config.PRE_FUNDING_EXIT_WINDOW_SEC", 120),
            patch(
                "src.execution.position_state.is_initialised", return_value=True
            ),
            patch(
                "src.execution.signal_dispatch._active_uids",
                return_value=["uid1"],
            ),
            patch(
                "src.execution.position_state.list_positions_for_user",
                return_value=[pos],
            ),
            patch(
                "src.execution.position_state.is_terminal", return_value=False
            ),
            patch(
                "src.execution.order_placer.OrderPlacer", return_value=MagicMock()
            ),
            patch(
                "src.execution.funding_exit_watcher._close_for_funding",
                new_callable=AsyncMock,
            ) as mock_close,
        ):
            await watcher._check()
            mock_close.assert_awaited_once()

    async def test_skips_pre_tp_fired_is_still_closed(self):
        """PRE_TP_FIRED positions (VOLATILE path) should also be exited."""
        watcher = self._make_watcher()
        pos = _make_position(
            entry_regime="TRENDING_UP", side="LONG", state_name="PRE_TP_FIRED"
        )

        with (
            patch(
                "src.execution.funding_exit_watcher.seconds_until_next_funding",
                return_value=90.0,
            ),
            patch("config.PRE_FUNDING_EXIT_WINDOW_SEC", 120),
            patch(
                "src.execution.position_state.is_initialised", return_value=True
            ),
            patch(
                "src.execution.signal_dispatch._active_uids",
                return_value=["uid1"],
            ),
            patch(
                "src.execution.position_state.list_positions_for_user",
                return_value=[pos],
            ),
            patch(
                "src.execution.position_state.is_terminal", return_value=False
            ),
            patch(
                "src.execution.order_placer.OrderPlacer", return_value=MagicMock()
            ),
            patch(
                "src.execution.funding_exit_watcher._close_for_funding",
                new_callable=AsyncMock,
            ) as mock_close,
        ):
            await watcher._check()
            mock_close.assert_awaited_once()


# ---------------------------------------------------------------------------
# FundingExitWatcher.run lifecycle
# ---------------------------------------------------------------------------


class TestFundingExitWatcherRun:
    async def test_disabled_when_window_zero(self):
        watcher = FundingExitWatcher()
        with (
            patch("config.PRE_FUNDING_EXIT_WINDOW_SEC", 0),
            patch.object(watcher, "_check", new_callable=AsyncMock) as mock_check,
        ):
            await watcher.run()
            mock_check.assert_not_called()

    async def test_stops_cleanly(self):
        watcher = FundingExitWatcher()
        check_calls: List[int] = []

        async def fake_check():
            check_calls.append(1)

        with (
            patch("config.PRE_FUNDING_EXIT_WINDOW_SEC", 120),
            patch.object(watcher, "_check", side_effect=fake_check),
            patch.object(watcher, "_POLL_INTERVAL_S", 0.01),
        ):
            task = asyncio.create_task(watcher.run())
            await asyncio.sleep(0.05)
            await watcher.stop()
            await task
        assert len(check_calls) >= 1


# ---------------------------------------------------------------------------
# _close_for_funding integration
# ---------------------------------------------------------------------------


class TestCloseForFunding:
    def _make_placer(self) -> MagicMock:
        from src.execution.order_placer import OrderPlacer, OrderPlacementResult

        placer = MagicMock(spec=OrderPlacer)
        placer.cancel_algo_order = AsyncMock()
        placer.place_funding_market_close = AsyncMock(
            return_value=MagicMock(spec=OrderPlacementResult)
        )
        return placer

    async def test_cancels_orders_and_places_market_close(self):
        from src.execution.position_state import Position, PositionState

        pos = MagicMock(spec=Position)
        pos.signal_id = "sig1"
        pos.symbol = "BTCUSDT"
        pos.side = "LONG"
        pos.state = PositionState.OPEN
        pos.sl_order_id = 1001
        pos.sl_be_order_id = 0
        pos.tp1_order_id = 2001
        pos.tp2_order_id = 3001
        pos.tp3_order_id = 0
        pos.total_qty = 0.01
        pos.closed_qty = 0.0

        placer = self._make_placer()
        await _close_for_funding("uid1", pos, placer)

        # Should cancel sl + tp1 + tp2 (sl_be=0, tp3=0 skipped)
        assert placer.cancel_algo_order.await_count == 3
        cancelled_ids = {
            call.kwargs["algo_id"]
            for call in placer.cancel_algo_order.await_args_list
        }
        assert cancelled_ids == {1001, 2001, 3001}

        placer.place_funding_market_close.assert_awaited_once_with(
            signal_id="sig1",
            symbol="BTCUSDT",
            direction="LONG",
            quantity=pytest.approx(0.01),
        )

    async def test_surviving_qty_when_partially_closed(self):
        from src.execution.position_state import Position, PositionState

        pos = MagicMock(spec=Position)
        pos.signal_id = "sig2"
        pos.symbol = "ETHUSDT"
        pos.side = "LONG"
        pos.state = PositionState.PRE_TP_FIRED
        pos.sl_order_id = 0
        pos.sl_be_order_id = 5001
        pos.tp1_order_id = 0
        pos.tp2_order_id = 6001
        pos.tp3_order_id = 0
        pos.total_qty = 0.10
        pos.closed_qty = 0.05  # half already closed (pre-TP)

        placer = self._make_placer()
        await _close_for_funding("uid1", pos, placer)

        placer.place_funding_market_close.assert_awaited_once_with(
            signal_id="sig2",
            symbol="ETHUSDT",
            direction="LONG",
            quantity=pytest.approx(0.05),
        )

    async def test_market_close_failure_is_logged_not_raised(self):
        from src.execution.order_placer import OrderPlacementError
        from src.execution.position_state import Position, PositionState

        pos = MagicMock(spec=Position)
        pos.signal_id = "sig3"
        pos.symbol = "BTCUSDT"
        pos.side = "LONG"
        pos.state = PositionState.OPEN
        pos.sl_order_id = 0
        pos.sl_be_order_id = 0
        pos.tp1_order_id = 0
        pos.tp2_order_id = 0
        pos.tp3_order_id = 0
        pos.total_qty = 0.01
        pos.closed_qty = 0.0

        placer = self._make_placer()
        placer.place_funding_market_close = AsyncMock(
            side_effect=OrderPlacementError("network error")
        )

        # Must not raise — fail-soft
        await _close_for_funding("uid1", pos, placer)


# ---------------------------------------------------------------------------
# FSM routing: "funding_close" phase → FUNDING_EXIT close_reason
# ---------------------------------------------------------------------------


class TestFsmFundingClosePhase:
    """Verify the FSM dispatch table routes funding_close fills correctly."""

    async def test_funding_close_fill_sets_funding_exit_reason(self):
        import pytest
        from unittest.mock import MagicMock, AsyncMock, patch

        from src.execution import events as events_mod
        from src.execution import order_placer as _op
        from src.execution import position_state
        from src.execution.position_fsm import PositionFSM
        from src.execution.position_state import coid_funding_close

        signal_id = "sig-fund1"

        pos = position_state.Position(
            signal_id=signal_id,
            firebase_uid="uid-test",
            symbol="BTCUSDT",
            side="LONG",
            state=position_state.PositionState.OPEN,
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
            entry_regime="TRENDING_UP",
        )

        placer = MagicMock()
        placer.cancel_order = AsyncMock(return_value=None)
        placer.cancel_algo_order = AsyncMock(return_value=None)
        placer.place_stop_loss = AsyncMock(
            return_value=_op.OrderPlacementResult(
                order_id=4001, client_order_id="x", status="NEW",
                avg_price=0.0, binance_body={},
            )
        )

        placer_factory = lambda uid: placer  # noqa: E731

        event = events_mod.OrderTradeUpdate(
            symbol="BTCUSDT",
            client_order_id=coid_funding_close(signal_id),
            side="SELL",
            order_type="MARKET",
            time_in_force="GTC",
            original_qty=1.0,
            original_price=0.0,
            average_price=29100.0,
            stop_price=0.0,
            execution_type="TRADE",
            order_status="FILLED",
            order_id=9999,
            last_filled_qty=1.0,
            cumulative_filled_qty=1.0,
            last_filled_price=29100.0,
            commission=0.0,
            commission_asset="USDT",
            trade_time_ms=0,
            trade_id=0,
            bids_notional=0.0,
            asks_notional=0.0,
            is_maker=False,
            reduce_only=True,
            working_type="MARK_PRICE",
            original_order_type="MARKET",
            position_side="BOTH",
            close_position=False,
            activation_price=0.0,
            callback_rate=0.0,
            realized_pnl=12.5,
        )

        saved: list = []

        with patch.object(
            position_state, "get_position", return_value=pos
        ), patch.object(
            position_state, "put_position", side_effect=lambda p: saved.append(p)
        ):
            fsm = PositionFSM(
                firebase_uid="uid-test",
                order_placer_factory=placer_factory,
            )
            await fsm.handle_event(event)

        assert pos.state == position_state.PositionState.CLOSED
        assert pos.close_reason == "FUNDING_EXIT"
