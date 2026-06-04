"""Tests for the regime-per-exit FSM (position_fsm.py exit matrix).

Covers the three exit paths at pre-TP fill time:

  TRAIL   — TRENDING_UP/DOWN (5m) aligned with trade AND 15m confirms:
             keep TP2, place Binance TRAILING_STOP_MARKET → TRAILING state.
  VOLATILE — VOLATILE regime: keep TP2, tighten SL 20% → PRE_TP_FIRED.
  CANCEL  — RANGING, QUIET, counter-trend, or missing data: cancel all
             orders, market-close residual → PRE_TP_FIRED (→ CLOSED on fill).

Also covers:
  - _regime_exit_path() routing logic for every combination.
  - _apply_close_fill() transitioning PRE_TP_FIRED → CLOSED.
  - _apply_tp2_fill() auto-closing when tp3_qty == 0 and fully closed.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution import events as events_mod
from src.execution import order_placer
from src.execution import position_fsm
from src.execution import position_state
from src.execution.position_fsm import _regime_exit_path


# ---------------------------------------------------------------------------
# Helpers (mirrors tests/execution/test_position_fsm.py)
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch: pytest.MonkeyPatch):
    position_state.reset_for_test()
    monkeypatch.setenv("TRIPWIRE_SYMBOL_ALLOWLIST", "BTCUSDT,ETHUSDT")
    from src.execution import tripwires as _tw
    from src.execution import kill_switch as _ks
    _tw.reset_singletons_for_test()
    _ks.reset_for_test()
    yield
    position_state.reset_for_test()
    _tw.reset_singletons_for_test()
    _ks.reset_for_test()


def _make_placer():
    placer = MagicMock()
    placer.cancel_algo_order = AsyncMock(return_value=None)
    placer.cancel_order = AsyncMock(return_value=None)
    placer.ensure_cross_margin = AsyncMock(return_value=True)
    placer.place_market_close = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=9001, client_order_id="lumin_s_close",
            status="FILLED", avg_price=29100.0, binance_body={},
        )
    )
    placer.place_stop_loss = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=4001, client_order_id="lumin_s_sl_be",
            status="NEW", avg_price=0.0, binance_body={},
        )
    )
    placer.place_trailing_stop_market = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=7001, client_order_id="lumin_s_sl_be",
            status="NEW", avg_price=0.0, binance_body={},
        )
    )
    return placer


def _position(
    side="LONG",
    regime="",
    regime_15m="",
    atr_pct=50.0,
    atr_val=290.0,
    fill_price=29000.0,
    sl_price=28500.0,
):
    p = position_state.Position(
        signal_id="s",
        firebase_uid="uid",
        symbol="BTCUSDT",
        side=side,
        state=position_state.PositionState.OPEN,
        entry_price_target=fill_price,
        entry_price_filled=fill_price,
        sl_price=sl_price,
        tp1_price=29500.0,
        tp2_price=30000.0,
        tp3_price=0.0,
        total_qty=1.0,
        tp1_qty=0.3,
        tp2_qty=0.7,
        tp3_qty=0.0,
        sl_order_id=2001,
        tp1_order_id=3001,
        tp2_order_id=3002,
        tp3_order_id=0,
        entry_regime=regime,
        entry_regime_15m=regime_15m,
        atr_percentile_at_entry=atr_pct,
        atr_value_at_entry=atr_val,
    )
    return p


def _otu(*, coid: str, filled: float = 0.5, pnl: float = 10.0):
    return events_mod.OrderTradeUpdate(
        symbol="BTCUSDT",
        client_order_id=coid,
        side="SELL",
        order_type="MARKET",
        time_in_force="GTC",
        original_qty=filled,
        original_price=0.0,
        average_price=29100.0,
        stop_price=0.0,
        execution_type="TRADE",
        order_status="FILLED",
        order_id=999,
        last_filled_qty=filled,
        cumulative_filled_qty=filled,
        last_filled_price=29100.0,
        commission=0.0,
        commission_asset="USDT",
        trade_time_ms=0,
        trade_id=1,
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
        realized_pnl=pnl,
    )


# ---------------------------------------------------------------------------
# _regime_exit_path routing
# ---------------------------------------------------------------------------


class TestRegimeExitPath:
    def _pos(self, regime, regime_15m, side="LONG"):
        return _position(side=side, regime=regime, regime_15m=regime_15m)

    def test_empty_regime_is_cancel(self):
        assert _regime_exit_path(self._pos("", "")) == "CANCEL"

    def test_ranging_is_cancel(self):
        assert _regime_exit_path(self._pos("RANGING", "RANGING")) == "CANCEL"

    def test_quiet_is_cancel(self):
        assert _regime_exit_path(self._pos("QUIET", "QUIET")) == "CANCEL"

    def test_volatile_is_volatile(self):
        assert _regime_exit_path(self._pos("VOLATILE", "")) == "VOLATILE"

    def test_trending_up_long_with_15m_confirm_is_trail(self):
        assert _regime_exit_path(self._pos("TRENDING_UP", "TRENDING_UP", side="LONG")) == "TRAIL"

    def test_trending_down_short_with_15m_confirm_is_trail(self):
        assert _regime_exit_path(self._pos("TRENDING_DOWN", "TRENDING_DOWN", side="SHORT")) == "TRAIL"

    def test_trending_up_short_is_cancel(self):
        # 5m trend is counter to SHORT trade → CANCEL
        assert _regime_exit_path(self._pos("TRENDING_UP", "TRENDING_UP", side="SHORT")) == "CANCEL"

    def test_trending_down_long_is_cancel(self):
        # 5m trend is counter to LONG trade → CANCEL
        assert _regime_exit_path(self._pos("TRENDING_DOWN", "TRENDING_DOWN", side="LONG")) == "CANCEL"

    def test_trending_up_long_but_15m_ranging_is_cancel(self):
        # 15m doesn't confirm — no trail
        assert _regime_exit_path(self._pos("TRENDING_UP", "RANGING", side="LONG")) == "CANCEL"

    def test_trending_up_long_but_15m_counter_is_cancel(self):
        # 15m trend is opposite direction
        assert _regime_exit_path(self._pos("TRENDING_UP", "TRENDING_DOWN", side="LONG")) == "CANCEL"

    def test_trending_up_long_but_no_15m_data_is_cancel(self):
        # Missing 15m data → can't confirm → CANCEL
        assert _regime_exit_path(self._pos("TRENDING_UP", "", side="LONG")) == "CANCEL"

    def test_case_insensitive(self):
        # regime stored from scanner as upper, but be defensive
        p = self._pos("trending_up", "trending_up", side="LONG")
        assert _regime_exit_path(p) == "TRAIL"


# ---------------------------------------------------------------------------
# TRAIL path
# ---------------------------------------------------------------------------


class TestPretpTrailPath:
    @pytest.mark.asyncio
    async def test_trail_path_keeps_tp2_places_trailing_stop(self):
        placer = _make_placer()
        factory = lambda uid: placer  # noqa: E731
        fsm = position_fsm.PositionFSM("uid", order_placer_factory=factory)
        pos = _position(regime="TRENDING_UP", regime_15m="TRENDING_UP", atr_val=290.0)
        captured = []
        with patch.object(position_state, "get_position", return_value=pos), \
             patch.object(position_state, "put_position", side_effect=captured.append):
            await fsm.handle_event(_otu(coid=position_state.coid_pretp("s")))
        p = captured[0]
        assert p.state == position_state.PositionState.TRAILING
        assert p.tp2_order_id == 3002  # TP2 still live
        placer.place_trailing_stop_market.assert_awaited_once()
        placer.place_stop_loss.assert_not_called()
        placer.place_market_close.assert_not_called()
        # Original SL cancelled, TP2 NOT cancelled
        cancelled = {c.kwargs["algo_id"] for c in placer.cancel_algo_order.call_args_list}
        assert 2001 in cancelled
        assert 3002 not in cancelled
        assert p.sl_order_id == 0
        assert p.trail_order_id == 7001

    @pytest.mark.asyncio
    async def test_trail_callback_rate_derived_from_atr(self):
        placer = _make_placer()
        factory = lambda uid: placer  # noqa: E731
        fsm = position_fsm.PositionFSM("uid", order_placer_factory=factory)
        # atr_val=290 @ price=29000 → 1% raw, trail_atr_mult(50)=1.5x → 1.5%
        pos = _position(regime="TRENDING_UP", regime_15m="TRENDING_UP",
                        atr_val=290.0, atr_pct=50.0, fill_price=29000.0)
        with patch.object(position_state, "get_position", return_value=pos), \
             patch.object(position_state, "put_position"):
            await fsm.handle_event(_otu(coid=position_state.coid_pretp("s")))
        kw = placer.place_trailing_stop_market.call_args.kwargs
        # Expected: TRAIL_ATR_MULT_NORMAL(1.5) × 290 / 29000 × 100 = 1.5%
        assert abs(kw["callback_rate_pct"] - 1.5) < 0.01

    @pytest.mark.asyncio
    async def test_trail_fallback_to_be_sl_on_placement_failure(self):
        placer = _make_placer()
        placer.place_trailing_stop_market = AsyncMock(
            side_effect=order_placer.OrderRejectedByBinance("algo fail")
        )
        factory = lambda uid: placer  # noqa: E731
        fsm = position_fsm.PositionFSM("uid", order_placer_factory=factory)
        pos = _position(regime="TRENDING_UP", regime_15m="TRENDING_UP")
        captured = []
        with patch.object(position_state, "get_position", return_value=pos), \
             patch.object(position_state, "put_position", side_effect=captured.append):
            await fsm.handle_event(_otu(coid=position_state.coid_pretp("s")))
        p = captured[0]
        # Falls back to PRE_TP_FIRED with BE-SL
        assert p.state == position_state.PositionState.PRE_TP_FIRED
        placer.place_stop_loss.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_trailing_stop_fill_closes_position(self):
        """When the trail stop fires, it arrives as sl_be event → CLOSED."""
        placer = _make_placer()
        factory = lambda uid: placer  # noqa: E731
        fsm = position_fsm.PositionFSM("uid", order_placer_factory=factory)
        pos = _position()
        pos.state = position_state.PositionState.TRAILING
        pos.sl_be_order_id = 7001
        captured = []
        with patch.object(position_state, "get_position", return_value=pos), \
             patch.object(position_state, "put_position", side_effect=captured.append):
            await fsm.handle_event(_otu(coid=position_state.coid_sl_be("s"), pnl=-5.0))
        p = captured[0]
        assert p.state == position_state.PositionState.CLOSED
        assert p.close_reason == "SL_BE"


# ---------------------------------------------------------------------------
# VOLATILE path
# ---------------------------------------------------------------------------


class TestPretpVolatilePath:
    @pytest.mark.asyncio
    async def test_volatile_keeps_tp2_tightens_sl(self):
        placer = _make_placer()
        factory = lambda uid: placer  # noqa: E731
        fsm = position_fsm.PositionFSM("uid", order_placer_factory=factory)
        # fill=29000, sl=28500 → original dist=500, tight=400, new_sl=28600
        pos = _position(regime="VOLATILE", fill_price=29000.0, sl_price=28500.0)
        captured = []
        with patch.object(position_state, "get_position", return_value=pos), \
             patch.object(position_state, "put_position", side_effect=captured.append):
            await fsm.handle_event(_otu(coid=position_state.coid_pretp("s")))
        p = captured[0]
        assert p.state == position_state.PositionState.PRE_TP_FIRED
        assert p.tp2_order_id == 3002  # TP2 stays
        placer.place_stop_loss.assert_awaited_once()
        sl_kw = placer.place_stop_loss.call_args.kwargs
        assert abs(sl_kw["stop_price"] - 28600.0) < 1e-6
        placer.place_trailing_stop_market.assert_not_called()
        placer.place_market_close.assert_not_called()

    @pytest.mark.asyncio
    async def test_volatile_short_tightens_sl_above_entry(self):
        placer = _make_placer()
        factory = lambda uid: placer  # noqa: E731
        fsm = position_fsm.PositionFSM("uid", order_placer_factory=factory)
        # SHORT: fill=29000, sl=29500 → dist=500, tight=400, new_sl=29400
        pos = _position(side="SHORT", regime="VOLATILE",
                        fill_price=29000.0, sl_price=29500.0)
        captured = []
        with patch.object(position_state, "get_position", return_value=pos), \
             patch.object(position_state, "put_position", side_effect=captured.append):
            await fsm.handle_event(_otu(coid=position_state.coid_pretp("s")))
        sl_kw = placer.place_stop_loss.call_args.kwargs
        assert abs(sl_kw["stop_price"] - 29400.0) < 1e-6


# ---------------------------------------------------------------------------
# CANCEL path
# ---------------------------------------------------------------------------


class TestPretpCancelPath:
    @pytest.mark.asyncio
    async def test_cancel_path_cancels_all_and_closes(self):
        placer = _make_placer()
        factory = lambda uid: placer  # noqa: E731
        fsm = position_fsm.PositionFSM("uid", order_placer_factory=factory)
        pos = _position(regime="RANGING", regime_15m="RANGING")
        captured = []
        with patch.object(position_state, "get_position", return_value=pos), \
             patch.object(position_state, "put_position", side_effect=captured.append):
            await fsm.handle_event(_otu(coid=position_state.coid_pretp("s"), filled=0.5))
        p = captured[0]
        assert p.state == position_state.PositionState.PRE_TP_FIRED
        cancelled = {c.kwargs["algo_id"] for c in placer.cancel_algo_order.call_args_list}
        assert cancelled == {2001, 3001, 3002}  # SL + TP1 + TP2 (TP3=0 skipped)
        placer.place_market_close.assert_awaited_once()
        close_kw = placer.place_market_close.call_args.kwargs
        assert abs(close_kw["quantity"] - 0.5) < 1e-9  # remaining = 1.0 - 0.5
        placer.place_stop_loss.assert_not_called()
        placer.place_trailing_stop_market.assert_not_called()
        assert p.sl_order_id == 0
        assert p.tp1_order_id == 0
        assert p.tp2_order_id == 0

    @pytest.mark.asyncio
    async def test_cancel_path_fallback_to_be_sl_on_close_failure(self):
        placer = _make_placer()
        placer.place_market_close = AsyncMock(
            side_effect=order_placer.OrderRejectedByBinance("close fail")
        )
        factory = lambda uid: placer  # noqa: E731
        fsm = position_fsm.PositionFSM("uid", order_placer_factory=factory)
        pos = _position(regime="QUIET", regime_15m="")
        captured = []
        with patch.object(position_state, "get_position", return_value=pos), \
             patch.object(position_state, "put_position", side_effect=captured.append):
            await fsm.handle_event(_otu(coid=position_state.coid_pretp("s")))
        # Fallback BE-SL placed when market close fails
        placer.place_stop_loss.assert_awaited_once()


# ---------------------------------------------------------------------------
# _apply_close_fill
# ---------------------------------------------------------------------------


class TestCloseFill:
    @pytest.mark.asyncio
    async def test_close_fill_transitions_pre_tp_fired_to_closed(self):
        placer = _make_placer()
        factory = lambda uid: placer  # noqa: E731
        fsm = position_fsm.PositionFSM("uid", order_placer_factory=factory)
        pos = _position()
        pos.state = position_state.PositionState.PRE_TP_FIRED
        captured = []
        with patch.object(position_state, "get_position", return_value=pos), \
             patch.object(position_state, "put_position", side_effect=captured.append):
            await fsm.handle_event(_otu(coid=position_state.coid_close("s"), pnl=-3.0))
        p = captured[0]
        assert p.state == position_state.PositionState.CLOSED
        assert p.close_reason == "REGIME_EXIT"
        assert p.realized_pnl_total == -3.0
        assert p.closed_at is not None


# ---------------------------------------------------------------------------
# _apply_tp2_fill with tp3_qty == 0 auto-close
# ---------------------------------------------------------------------------


class TestTp2FillAutoClose:
    @pytest.mark.asyncio
    async def test_tp2_fill_closes_when_tp3_disabled_and_fully_closed(self):
        """When TP3 is disabled (tp3_qty == 0) and TP2 closes the last qty,
        the position transitions directly to CLOSED instead of stranding in
        TP2_HIT forever.
        """
        placer = _make_placer()
        factory = lambda uid: placer  # noqa: E731
        fsm = position_fsm.PositionFSM("uid", order_placer_factory=factory)
        pos = _position()
        pos.state = position_state.PositionState.TRAILING
        pos.closed_qty = 0.5  # pretp already took 50%
        pos.total_qty = 1.0
        pos.tp3_qty = 0.0     # TP3 disabled
        captured = []
        with patch.object(position_state, "get_position", return_value=pos), \
             patch.object(position_state, "put_position", side_effect=captured.append):
            await fsm.handle_event(
                _otu(coid=position_state.coid_tp2("s"), filled=0.5, pnl=50.0)
            )
        p = captured[0]
        # Should close directly since all qty is now closed
        assert p.state == position_state.PositionState.CLOSED
        assert p.close_reason == "TP2"
        assert abs(p.closed_qty - 1.0) < 1e-9

    @pytest.mark.asyncio
    async def test_tp2_fill_stays_tp2_hit_when_tp3_enabled(self):
        placer = _make_placer()
        factory = lambda uid: placer  # noqa: E731
        fsm = position_fsm.PositionFSM("uid", order_placer_factory=factory)
        pos = _position()
        pos.state = position_state.PositionState.TP1_HIT
        pos.closed_qty = 0.3
        pos.total_qty = 1.0
        pos.tp3_qty = 0.3  # TP3 enabled → don't auto-close
        captured = []
        with patch.object(position_state, "get_position", return_value=pos), \
             patch.object(position_state, "put_position", side_effect=captured.append):
            await fsm.handle_event(
                _otu(coid=position_state.coid_tp2("s"), filled=0.4, pnl=30.0)
            )
        p = captured[0]
        assert p.state == position_state.PositionState.TP2_HIT
