"""Tests for FundingExitWatcher and helpers.

The watcher reads real per-symbol funding info (rate + next-funding-time)
from the MarkPriceFeed and exits positions that would pay material funding
within the pre-funding window.
"""
from __future__ import annotations

import asyncio
import time
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution.funding_exit_watcher import (
    FundingExitWatcher,
    _close_for_funding,
    _position_pays_funding,
)


# ---------------------------------------------------------------------------
# _position_pays_funding
# ---------------------------------------------------------------------------


class TestPositionPaysFunding:
    def test_long_pays_when_rate_positive(self):
        assert _position_pays_funding("LONG", 0.0005) is True

    def test_long_does_not_pay_when_rate_negative(self):
        assert _position_pays_funding("LONG", -0.0005) is False

    def test_short_pays_when_rate_negative(self):
        assert _position_pays_funding("SHORT", -0.0005) is True

    def test_short_does_not_pay_when_rate_positive(self):
        assert _position_pays_funding("SHORT", 0.0005) is False

    def test_zero_rate_nobody_pays(self):
        assert _position_pays_funding("LONG", 0.0) is False
        assert _position_pays_funding("SHORT", 0.0) is False

    def test_case_insensitive(self):
        assert _position_pays_funding("long", 0.0005) is True
        assert _position_pays_funding("short", -0.0005) is True

    def test_unknown_side(self):
        assert _position_pays_funding("", 0.0005) is False


# ---------------------------------------------------------------------------
# FundingExitWatcher._check
# ---------------------------------------------------------------------------


def _make_position(
    *,
    signal_id: str = "sig1",
    symbol: str = "BTCUSDT",
    side: str = "LONG",
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
    pos.state = getattr(PositionState, state_name)
    pos.sl_order_id = sl_order_id
    pos.sl_be_order_id = 0
    pos.tp1_order_id = tp1_order_id
    pos.tp2_order_id = 0
    pos.tp3_order_id = 0
    pos.total_qty = total_qty
    pos.closed_qty = closed_qty
    return pos


def _make_feed(funding_info):
    """Return a mock MarkPriceFeed whose get_funding_info returns
    ``funding_info`` (a (rate, next_ms) tuple) for any symbol, or a dict
    keyed by symbol."""
    feed = MagicMock()
    if isinstance(funding_info, dict):
        feed.get_funding_info.side_effect = lambda sym: funding_info.get(sym.upper())
    else:
        feed.get_funding_info.return_value = funding_info
    return feed


# A next-funding-time 60 s in the future (inside a 120 s window).
def _next_funding_ms(seconds_ahead: float) -> int:
    return int((time.time() + seconds_ahead) * 1000.0)


class TestFundingExitWatcherCheck:
    def _make_watcher(self) -> FundingExitWatcher:
        return FundingExitWatcher()

    def _common_patches(self, *, positions, feed, window=120, min_rate=0.0005):
        """Return a list of context managers for the common patch set."""
        return [
            patch("config.PRE_FUNDING_EXIT_WINDOW_SEC", window),
            patch("config.PRE_FUNDING_MIN_RATE", min_rate),
            patch("src.execution.position_state.is_initialised", return_value=True),
            patch("src.execution.mark_price_feed.get_instance", return_value=feed),
            patch("src.execution.signal_dispatch._active_uids", return_value=["uid1"]),
            patch(
                "src.execution.position_state.list_positions_for_user",
                return_value=positions,
            ),
            patch("src.execution.position_state.is_terminal", return_value=False),
        ]

    async def _run_check(self, watcher, ctxs, close_mock):
        from contextlib import ExitStack

        with ExitStack() as stack:
            for c in ctxs:
                stack.enter_context(c)
            stack.enter_context(
                patch(
                    "src.execution.order_placer.OrderPlacer",
                    return_value=MagicMock(),
                )
            )
            stack.enter_context(
                patch(
                    "src.execution.funding_exit_watcher._close_for_funding",
                    close_mock,
                )
            )
            await watcher._check()

    async def test_no_feed_no_action(self):
        watcher = self._make_watcher()
        close_mock = AsyncMock()
        ctxs = [
            patch("config.PRE_FUNDING_EXIT_WINDOW_SEC", 120),
            patch("config.PRE_FUNDING_MIN_RATE", 0.0005),
            patch("src.execution.position_state.is_initialised", return_value=True),
            patch("src.execution.mark_price_feed.get_instance", return_value=None),
        ]
        await self._run_check(watcher, ctxs, close_mock)
        close_mock.assert_not_called()

    async def test_position_state_not_initialised_no_action(self):
        watcher = self._make_watcher()
        close_mock = AsyncMock()
        ctxs = [
            patch("config.PRE_FUNDING_EXIT_WINDOW_SEC", 120),
            patch("config.PRE_FUNDING_MIN_RATE", 0.0005),
            patch("src.execution.position_state.is_initialised", return_value=False),
        ]
        await self._run_check(watcher, ctxs, close_mock)
        close_mock.assert_not_called()

    async def test_exits_long_paying_material_funding_in_window(self):
        watcher = self._make_watcher()
        pos = _make_position(side="LONG")
        feed = _make_feed((0.00075, _next_funding_ms(60)))
        close_mock = AsyncMock()
        await self._run_check(
            watcher,
            self._common_patches(positions=[pos], feed=feed),
            close_mock,
        )
        close_mock.assert_awaited_once()
        assert close_mock.await_args.args[1] is pos

    async def test_exits_short_paying_material_funding(self):
        watcher = self._make_watcher()
        pos = _make_position(side="SHORT")
        feed = _make_feed((-0.00075, _next_funding_ms(60)))
        close_mock = AsyncMock()
        await self._run_check(
            watcher,
            self._common_patches(positions=[pos], feed=feed),
            close_mock,
        )
        close_mock.assert_awaited_once()

    async def test_skips_long_when_funding_negative(self):
        """LONG does not pay when funding is negative — no exit."""
        watcher = self._make_watcher()
        pos = _make_position(side="LONG")
        feed = _make_feed((-0.00075, _next_funding_ms(60)))
        close_mock = AsyncMock()
        await self._run_check(
            watcher,
            self._common_patches(positions=[pos], feed=feed),
            close_mock,
        )
        close_mock.assert_not_called()

    async def test_skips_short_when_funding_positive(self):
        watcher = self._make_watcher()
        pos = _make_position(side="SHORT")
        feed = _make_feed((0.00075, _next_funding_ms(60)))
        close_mock = AsyncMock()
        await self._run_check(
            watcher,
            self._common_patches(positions=[pos], feed=feed),
            close_mock,
        )
        close_mock.assert_not_called()

    async def test_skips_immaterial_funding_below_threshold(self):
        """Funding below PRE_FUNDING_MIN_RATE is not worth the taker fee."""
        watcher = self._make_watcher()
        pos = _make_position(side="LONG")
        feed = _make_feed((0.0001, _next_funding_ms(60)))  # baseline 0.01%
        close_mock = AsyncMock()
        await self._run_check(
            watcher,
            self._common_patches(positions=[pos], feed=feed, min_rate=0.0005),
            close_mock,
        )
        close_mock.assert_not_called()

    async def test_skips_when_outside_window(self):
        watcher = self._make_watcher()
        pos = _make_position(side="LONG")
        feed = _make_feed((0.00075, _next_funding_ms(300)))  # 5 min away
        close_mock = AsyncMock()
        await self._run_check(
            watcher,
            self._common_patches(positions=[pos], feed=feed, window=120),
            close_mock,
        )
        close_mock.assert_not_called()

    async def test_skips_when_funding_already_passed(self):
        """Negative time-to-funding (settlement just passed) — wait for roll."""
        watcher = self._make_watcher()
        pos = _make_position(side="LONG")
        feed = _make_feed((0.00075, _next_funding_ms(-5)))
        close_mock = AsyncMock()
        await self._run_check(
            watcher,
            self._common_patches(positions=[pos], feed=feed),
            close_mock,
        )
        close_mock.assert_not_called()

    async def test_skips_trailing_state(self):
        watcher = self._make_watcher()
        pos = _make_position(side="LONG", state_name="TRAILING")
        feed = _make_feed((0.00075, _next_funding_ms(60)))
        close_mock = AsyncMock()
        await self._run_check(
            watcher,
            self._common_patches(positions=[pos], feed=feed),
            close_mock,
        )
        close_mock.assert_not_called()

    async def test_skips_when_no_funding_info_for_symbol(self):
        watcher = self._make_watcher()
        pos = _make_position(side="LONG")
        feed = _make_feed(None)  # get_funding_info returns None
        close_mock = AsyncMock()
        await self._run_check(
            watcher,
            self._common_patches(positions=[pos], feed=feed),
            close_mock,
        )
        close_mock.assert_not_called()

    async def test_pre_tp_fired_position_is_exited(self):
        watcher = self._make_watcher()
        pos = _make_position(side="LONG", state_name="PRE_TP_FIRED")
        feed = _make_feed((0.00075, _next_funding_ms(60)))
        close_mock = AsyncMock()
        await self._run_check(
            watcher,
            self._common_patches(positions=[pos], feed=feed),
            close_mock,
        )
        close_mock.assert_awaited_once()


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
        pos.side = "SHORT"
        pos.state = PositionState.PRE_TP_FIRED
        pos.sl_order_id = 0
        pos.sl_be_order_id = 5001
        pos.tp1_order_id = 0
        pos.tp2_order_id = 6001
        pos.tp3_order_id = 0
        pos.total_qty = 0.10
        pos.closed_qty = 0.05

        placer = self._make_placer()
        await _close_for_funding("uid1", pos, placer)

        placer.place_funding_market_close.assert_awaited_once_with(
            signal_id="sig2",
            symbol="ETHUSDT",
            direction="SHORT",
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

        await _close_for_funding("uid1", pos, placer)  # must not raise


# ---------------------------------------------------------------------------
# FSM routing: "funding_close" phase → FUNDING_EXIT close_reason
# ---------------------------------------------------------------------------


class TestFsmFundingClosePhase:
    async def test_funding_close_fill_sets_funding_exit_reason(self):
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
        )

        placer = MagicMock()
        placer.cancel_order = AsyncMock(return_value=None)
        placer.cancel_algo_order = AsyncMock(return_value=None)

        def placer_factory(uid):
            return placer

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


# ---------------------------------------------------------------------------
# Re-fire suppression (2026-07-16 audit fix)
# ---------------------------------------------------------------------------


class TestFiredSuppression(TestFundingExitWatcherCheck):
    """A successfully-placed funding close must not be re-issued on
    every 30s poll while the (possibly dropped) fill event is pending —
    pre-fix this produced -2022 cancel/close spam until the reconciler
    healed the position."""

    def _in_window_setup(self):
        pos = _make_position(side="LONG")
        feed = _make_feed((0.001, _next_funding_ms(60)))
        return pos, feed

    async def test_successful_close_not_refired_next_poll(self):
        watcher = self._make_watcher()
        pos, feed = self._in_window_setup()
        close_mock = AsyncMock(return_value=True)
        ctxs = self._common_patches(positions=[pos], feed=feed)
        await self._run_check(watcher, ctxs, close_mock)
        # Second poll, same still-non-terminal position in the window.
        ctxs = self._common_patches(positions=[pos], feed=feed)
        await self._run_check(watcher, ctxs, close_mock)
        assert close_mock.await_count == 1

    async def test_failed_close_is_retried_next_poll(self):
        watcher = self._make_watcher()
        pos, feed = self._in_window_setup()
        close_mock = AsyncMock(return_value=False)
        ctxs = self._common_patches(positions=[pos], feed=feed)
        await self._run_check(watcher, ctxs, close_mock)
        ctxs = self._common_patches(positions=[pos], feed=feed)
        await self._run_check(watcher, ctxs, close_mock)
        assert close_mock.await_count == 2

    async def test_suppression_expires_after_ttl(self):
        watcher = self._make_watcher()
        pos, feed = self._in_window_setup()
        close_mock = AsyncMock(return_value=True)
        ctxs = self._common_patches(positions=[pos], feed=feed)
        await self._run_check(watcher, ctxs, close_mock)
        # Simulate the TTL elapsing.
        watcher._fired_at[pos.signal_id] -= (
            FundingExitWatcher._FIRED_SUPPRESS_S + 1.0
        )
        ctxs = self._common_patches(positions=[pos], feed=feed)
        await self._run_check(watcher, ctxs, close_mock)
        assert close_mock.await_count == 2


class TestCloseForFundingResidual:
    async def test_zero_residual_sends_nothing_and_reports_success(self):
        """Pre-fix the ``or pos.total_qty`` fallback re-sent the FULL
        quantity when the residual was exactly zero, relying on
        reduceOnly to save it."""
        from src.execution.order_placer import OrderPlacer, OrderPlacementResult
        from src.execution.position_state import Position, PositionState

        pos = MagicMock(spec=Position)
        pos.signal_id = "sig-z"
        pos.symbol = "BTCUSDT"
        pos.side = "LONG"
        pos.state = PositionState.PRE_TP_FIRED
        pos.sl_order_id = 0
        pos.sl_be_order_id = 0
        pos.tp1_order_id = 0
        pos.tp2_order_id = 0
        pos.tp3_order_id = 0
        pos.total_qty = 0.01
        pos.closed_qty = 0.01  # fully closed, state transition lagging

        placer = MagicMock(spec=OrderPlacer)
        placer.cancel_algo_order = AsyncMock()
        placer.place_funding_market_close = AsyncMock(
            return_value=MagicMock(spec=OrderPlacementResult)
        )
        assert await _close_for_funding("uid1", pos, placer) is True
        placer.place_funding_market_close.assert_not_awaited()
