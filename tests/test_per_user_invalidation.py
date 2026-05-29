"""Tests for per-user invalidation mode enforcement (F4).

Three invariants:

* Loose-mode users are NOT closed when the engine fires an INVALIDATED kill —
  their native SL/TP bracket stays live.
* Tight-mode users get the ATR-trailing kill BEFORE the engine's standard check
  fires for them — their position is closed individually.
* Standard-mode users are closed as normal by the engine.
"""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.channels.base import Signal
from src.execution import signal_dispatch
from src.smc import Direction
from src.trade_monitor import TradeMonitor
from src.utils import utcnow


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_signal(
    *,
    signal_id: str = "INV-F4-001",
    symbol: str = "ETHUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 2370.0,
    stop_loss: float = 2351.0,
    tp1: float = 2392.0,
    age_seconds: float = 600.0,
    current_price: float = 2360.0,
    mfe_pct: float = 0.0,
) -> Signal:
    sig = Signal(
        channel="360_SCALP",
        symbol=symbol,
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=entry * 1.025 if direction == Direction.LONG else entry * 0.975,
        confidence=80.0,
        signal_id=signal_id,
    )
    sig.tp3 = entry * 1.04 if direction == Direction.LONG else entry * 0.96
    sig.original_entry = entry
    sig.current_price = current_price
    sig.setup_class = "SR_FLIP_RETEST"
    sig.signal_tier = "B"
    sig.timestamp = utcnow() - timedelta(seconds=age_seconds)
    sig.pnl_pct = 0.0
    sig.status = "ACTIVE"
    sig.max_favorable_excursion_pct = mfe_pct
    return sig


def _make_position(
    uid: str,
    signal_id: str,
    *,
    invalidation_mode: str = "standard",
):
    from dataclasses import dataclass
    from src.execution.position_state import Position, PositionState
    from datetime import datetime, timezone

    return Position(
        signal_id=signal_id,
        firebase_uid=uid,
        symbol="ETHUSDT",
        side="LONG",
        state=PositionState.OPEN,
        entry_price_target=2370.0,
        entry_price_filled=2370.0,
        sl_price=2351.0,
        tp1_price=2392.0,
        tp2_price=2432.25,
        tp3_price=2464.8,
        total_qty=0.2,
        tp1_qty=0.06,
        tp2_qty=0.14,
        tp3_qty=0.0,
        invalidation_mode=invalidation_mode,
    )


def _build_monitor(*, regime_label: str = "TRENDING_DOWN") -> TradeMonitor:
    regime_detector = MagicMock()
    regime_detector.classify.return_value = MagicMock(
        regime=MagicMock(value=regime_label)
    )
    ds = MagicMock()
    ds.get_candles.return_value = {
        "high": [2362.0], "low": [2358.0],
        "close": [2360.0], "open": [2360.0], "volume": [1000.0],
    }
    ds.ticks = {}
    return TradeMonitor(
        data_store=ds,
        send_telegram=AsyncMock(return_value=True),
        get_active_signals=lambda: {},
        remove_signal=lambda sid: None,
        update_signal=MagicMock(),
        regime_detector=regime_detector,
        indicators_fn=lambda sym: {"adx": 18.0, "ema_slope": 0.0},
        order_manager=None,
    )


# ---------------------------------------------------------------------------
# 1. close_fsm_positions_for_signal — excluded_modes skips loose users
# ---------------------------------------------------------------------------


async def test_loose_user_skipped_by_excluded_modes():
    """When excluded_modes={'loose'}, loose-mode users are not closed."""
    from src.execution import position_state as _ps

    loose_pos = _make_position("uid-loose", "INV-F4-001", invalidation_mode="loose")
    std_pos = _make_position("uid-std", "INV-F4-001", invalidation_mode="standard")

    def _get_pos(uid, signal_id):
        if uid == "uid-loose":
            return loose_pos
        if uid == "uid-std":
            return std_pos
        raise _ps.PositionNotFoundError(f"not found: {uid}")

    with (
        patch.object(signal_dispatch, "_active_uids", return_value=["uid-loose", "uid-std"]),
        patch("src.execution.position_state.is_initialised", return_value=True),
        patch("src.execution.position_state.get_position", side_effect=_get_pos),
        patch("src.execution.position_state.is_terminal", return_value=False),
        patch("src.execution.position_state.put_position"),
        patch("src.execution.order_placer.OrderPlacer") as MockPlacer,
    ):
        placer_inst = AsyncMock()
        placer_inst.cancel_order = AsyncMock()
        placer_inst.place_market_close = AsyncMock()
        MockPlacer.return_value = placer_inst

        closed = await signal_dispatch.close_fsm_positions_for_signal(
            "INV-F4-001",
            symbol="ETHUSDT",
            direction="LONG",
            reason="invalidated",
            excluded_modes=frozenset({"loose"}),
        )

    # Only the standard-mode user should be closed.
    assert closed == 1
    # place_market_close called once (for uid-std), not twice.
    assert placer_inst.place_market_close.await_count == 1


async def test_loose_user_closed_when_excluded_modes_absent():
    """Without excluded_modes, loose-mode users ARE closed (e.g. SL_HIT path)."""
    from src.execution import position_state as _ps

    loose_pos = _make_position("uid-loose2", "INV-F4-002", invalidation_mode="loose")

    with (
        patch.object(signal_dispatch, "_active_uids", return_value=["uid-loose2"]),
        patch("src.execution.position_state.is_initialised", return_value=True),
        patch("src.execution.position_state.get_position", return_value=loose_pos),
        patch("src.execution.position_state.is_terminal", return_value=False),
        patch("src.execution.position_state.put_position"),
        patch("src.execution.order_placer.OrderPlacer") as MockPlacer,
    ):
        placer_inst = AsyncMock()
        placer_inst.cancel_order = AsyncMock()
        placer_inst.place_market_close = AsyncMock()
        MockPlacer.return_value = placer_inst

        closed = await signal_dispatch.close_fsm_positions_for_signal(
            "INV-F4-002",
            symbol="ETHUSDT",
            direction="LONG",
            reason="sl_hit",
        )

    assert closed == 1
    placer_inst.place_market_close.assert_awaited_once()


# ---------------------------------------------------------------------------
# 2. broker_close_full passes excluded_modes only for "invalidated" reason
# ---------------------------------------------------------------------------


async def test_broker_close_full_excludes_loose_on_invalidated():
    """_broker_close_full passes excluded_modes={'loose'} when reason='invalidated'."""
    monitor = _build_monitor()
    sig = _make_signal()

    with patch("src.execution.signal_dispatch.close_fsm_positions_for_signal",
               new_callable=AsyncMock) as mock_close:
        await monitor._broker_close_full(sig, reason="invalidated", fill_price=2355.0)

    mock_close.assert_awaited_once()
    kw = mock_close.call_args.kwargs
    assert kw.get("excluded_modes") == frozenset({"loose"})


async def test_broker_close_full_no_exclusion_on_sl_hit():
    """For SL_HIT, excluded_modes must be None — everyone closes."""
    monitor = _build_monitor()
    sig = _make_signal()

    with patch("src.execution.signal_dispatch.close_fsm_positions_for_signal",
               new_callable=AsyncMock) as mock_close:
        await monitor._broker_close_full(sig, reason="sl_hit", fill_price=2351.0)

    kw = mock_close.call_args.kwargs
    assert kw.get("excluded_modes") is None


# ---------------------------------------------------------------------------
# 3. _check_per_user_invalidation — tight-mode early kill
# ---------------------------------------------------------------------------


async def test_tight_user_gets_early_atrl_kill(monkeypatch):
    """Tight-mode user is closed individually when ATR-trailing fires, even
    when the engine default is 'standard' (so the standard check doesn't fire)."""
    monitor = _build_monitor()

    # Signal with enough MFE to arm trailing but no regime flip (standard won't kill).
    # entry=2370, sl=2351 → sl_dist_pct=(2370-2351)/2370*100=0.80%
    # mfe_pct=1.0 → mfe_r = 1.0/0.80 = 1.25 ≥ 0.3 → trailing armed
    # current_price back to 2370 from peak → retracement calculated from sig attrs
    sig = _make_signal(entry=2370.0, stop_loss=2351.0, current_price=2360.0, mfe_pct=1.0)

    tight_pos = _make_position("uid-tight", sig.signal_id, invalidation_mode="tight")

    with (
        patch.object(signal_dispatch, "get_fsm_positions_for_signal",
                     return_value=[("uid-tight", tight_pos)]),
        patch.object(signal_dispatch, "close_single_fsm_position",
                     new_callable=AsyncMock) as mock_close_single,
        patch("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "standard"),
        patch.object(monitor, "_check_invalidation",
                     wraps=monitor._check_invalidation) as spy,
    ):
        await monitor._check_per_user_invalidation(sig)

    # close_single_fsm_position must have been called for the tight user.
    mock_close_single.assert_awaited_once()
    assert mock_close_single.call_args.args[0] == "uid-tight"
    assert mock_close_single.call_args.kwargs["reason"] == "inv_tight"


async def test_tight_mode_noop_when_global_already_tight(monkeypatch):
    """When the engine already runs tight, _check_per_user_invalidation is a no-op."""
    monitor = _build_monitor()
    sig = _make_signal(mfe_pct=1.0)

    tight_pos = _make_position("uid-tight2", sig.signal_id, invalidation_mode="tight")

    with (
        patch.object(signal_dispatch, "get_fsm_positions_for_signal",
                     return_value=[("uid-tight2", tight_pos)]),
        patch.object(signal_dispatch, "close_single_fsm_position",
                     new_callable=AsyncMock) as mock_close_single,
        patch("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "tight"),
    ):
        await monitor._check_per_user_invalidation(sig)

    # No per-user close — the engine already handles all users at tight level.
    mock_close_single.assert_not_awaited()


async def test_loose_user_not_closed_by_per_user_check():
    """_check_per_user_invalidation never closes loose-mode users (they survive
    engine invalidation; this function only handles tight escalation)."""
    monitor = _build_monitor()
    sig = _make_signal(mfe_pct=1.0)

    loose_pos = _make_position("uid-loose3", sig.signal_id, invalidation_mode="loose")

    with (
        patch.object(signal_dispatch, "get_fsm_positions_for_signal",
                     return_value=[("uid-loose3", loose_pos)]),
        patch.object(signal_dispatch, "close_single_fsm_position",
                     new_callable=AsyncMock) as mock_close_single,
        patch("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "standard"),
    ):
        await monitor._check_per_user_invalidation(sig)

    mock_close_single.assert_not_awaited()


# ---------------------------------------------------------------------------
# 4. get_fsm_positions_for_signal
# ---------------------------------------------------------------------------


def test_get_fsm_positions_returns_empty_when_not_initialised():
    with patch("src.execution.position_state.is_initialised", return_value=False):
        result = signal_dispatch.get_fsm_positions_for_signal("some-signal-id")
    assert result == []


def test_get_fsm_positions_skips_terminal():
    from src.execution import position_state as _ps

    open_pos = _make_position("uid-open", "SIG-001", invalidation_mode="standard")
    closed_pos = _make_position("uid-closed", "SIG-001", invalidation_mode="standard")
    from src.execution.position_state import PositionState
    closed_pos.state = PositionState.CLOSED

    def _get(uid, sid):
        return open_pos if uid == "uid-open" else closed_pos

    with (
        patch.object(signal_dispatch, "_active_uids", return_value=["uid-open", "uid-closed"]),
        patch("src.execution.position_state.is_initialised", return_value=True),
        patch("src.execution.position_state.get_position", side_effect=_get),
        patch("src.execution.position_state.is_terminal",
              side_effect=lambda s: s == PositionState.CLOSED),
    ):
        result = signal_dispatch.get_fsm_positions_for_signal("SIG-001")

    assert len(result) == 1
    uid, pos = result[0]
    assert uid == "uid-open"
