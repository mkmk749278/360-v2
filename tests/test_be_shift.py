"""Tests for the mark-price-triggered break-even SL shift.

Verifies that ``maybe_fire_be_shift`` in ``pretp_dispatcher``:
- Shifts the SL to entry when MFE crosses BE_SHIFT_TRIGGER_PCT% for LONG.
- Shifts the SL to entry when MFE crosses BE_SHIFT_TRIGGER_PCT% for SHORT.
- Does NOT fire when the favourable move is below the trigger threshold.
- Does NOT double-fire when ``be_shift_fired`` is already set.
- Does NOT fire when ``sl_order_id == 0`` (SL already gone).
- Does NOT fire when ``pretp_fired`` is set (pre-TP owns its own BE shift).
- Leaves position intact (no be_shift_fired) when BE-SL placement fails,
  so the next tick can retry.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution import position_state as _ps
from src.execution import pretp_dispatcher as _pd
from src.execution.order_placer import OrderPlacementError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_position(
    *,
    side: str = "LONG",
    entry: float = 100.0,
    sl_price: float = 95.0,
    sl_order_id: int = 42,
    pretp_fired: bool = False,
    be_shift_fired: bool = False,
) -> _ps.Position:
    return _ps.Position(
        signal_id="be-test-sig",
        firebase_uid="uid-be",
        symbol="BTCUSDT",
        side=side,
        state=_ps.PositionState.OPEN,
        entry_price_target=entry,
        entry_price_filled=entry,
        sl_price=sl_price,
        tp1_price=entry * 1.02,
        tp2_price=entry * 1.04,
        tp3_price=entry * 1.06,
        total_qty=1.0,
        tp1_qty=1.0,
        tp2_qty=0.0,
        tp3_qty=0.0,
        sl_order_id=sl_order_id,
        pretp_fired=pretp_fired,
        be_shift_fired=be_shift_fired,
    )


def _make_placer(be_order_id: int = 99) -> MagicMock:
    placer = MagicMock()
    placed = MagicMock()
    placed.order_id = be_order_id
    placer.cancel_algo_order = AsyncMock(return_value=None)
    placer.place_stop_loss = AsyncMock(return_value=placed)
    return placer


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_long_fires_at_trigger_threshold():
    # Noise-aware arm (2026-07-07): the arm is max(flat 1%, 1R of the stop
    # distance), so a 1%-stop position arms at the legacy 1% and the armed
    # stop parks 0.15% below entry (loss-side tolerance), not exactly at it.
    pos = _make_position(side="LONG", entry=100.0, sl_price=99.0, sl_order_id=42)
    placer = _make_placer(be_order_id=99)

    with patch("src.execution.pretp_dispatcher._BE_SHIFT_TRIGGER_PCT", 1.0), \
         patch("src.execution.position_state.put_position"):
        await _pd.maybe_fire_be_shift(pos, mark_price=101.0, placer=placer)

    placer.cancel_algo_order.assert_awaited_once_with(symbol="BTCUSDT", algo_id=42)
    placer.place_stop_loss.assert_awaited_once()
    call_kwargs = placer.place_stop_loss.call_args.kwargs
    assert call_kwargs["stop_price"] == pytest.approx(100.0 * (1 - 0.0015))
    assert call_kwargs["direction"] == "LONG"
    assert pos.be_shift_fired is True
    assert pos.sl_order_id == 0
    assert pos.sl_be_order_id == 99
    assert pos.sl_price == pytest.approx(100.0 * (1 - 0.0015))


@pytest.mark.asyncio
async def test_wide_stop_does_not_arm_at_flat_trigger():
    # R-multiple arm regression (7d study: 84% of flat-1% BE scratches were
    # winners): a 5%-stop position must NOT arm at a 1% move — its arm is 1R.
    pos = _make_position(side="LONG", entry=100.0, sl_price=95.0, sl_order_id=42)
    placer = _make_placer()

    with patch("src.execution.pretp_dispatcher._BE_SHIFT_TRIGGER_PCT", 1.0):
        await _pd.maybe_fire_be_shift(pos, mark_price=101.0, placer=placer)

    placer.cancel_algo_order.assert_not_called()
    placer.place_stop_loss.assert_not_called()
    assert pos.be_shift_fired is False


@pytest.mark.asyncio
async def test_short_fires_at_trigger_threshold():
    # SHORT: entry=100, mark drops to 98.9 → move = (100-98.9)/100 = 1.1% > 1.0%
    pos = _make_position(side="SHORT", entry=100.0, sl_price=101.0, sl_order_id=43)
    placer = _make_placer(be_order_id=88)

    with patch("src.execution.pretp_dispatcher._BE_SHIFT_TRIGGER_PCT", 1.0), \
         patch("src.execution.position_state.put_position"):
        await _pd.maybe_fire_be_shift(pos, mark_price=98.9, placer=placer)

    placer.cancel_algo_order.assert_awaited_once()
    placer.place_stop_loss.assert_awaited_once()
    call_kwargs = placer.place_stop_loss.call_args.kwargs
    assert call_kwargs["stop_price"] == pytest.approx(100.0 * (1 + 0.0015))
    assert call_kwargs["direction"] == "SHORT"
    assert pos.be_shift_fired is True
    assert pos.sl_price == pytest.approx(100.0 * (1 + 0.0015))


@pytest.mark.asyncio
async def test_does_not_fire_below_threshold():
    # Move is only 0.9% — below the 1.0% trigger.
    pos = _make_position(side="LONG", entry=100.0, sl_order_id=42)
    placer = _make_placer()

    with patch("src.execution.pretp_dispatcher._BE_SHIFT_TRIGGER_PCT", 1.0):
        await _pd.maybe_fire_be_shift(pos, mark_price=100.9, placer=placer)

    placer.cancel_algo_order.assert_not_called()
    placer.place_stop_loss.assert_not_called()
    assert pos.be_shift_fired is False


@pytest.mark.asyncio
async def test_does_not_double_fire():
    pos = _make_position(side="LONG", entry=100.0, sl_order_id=0, be_shift_fired=True)
    placer = _make_placer()

    with patch("src.execution.pretp_dispatcher._BE_SHIFT_TRIGGER_PCT", 1.0):
        await _pd.maybe_fire_be_shift(pos, mark_price=105.0, placer=placer)

    placer.cancel_algo_order.assert_not_called()
    placer.place_stop_loss.assert_not_called()


@pytest.mark.asyncio
async def test_does_not_fire_when_sl_order_id_zero():
    # sl_order_id == 0 means the SL was already canceled (e.g. pre-TP fired).
    pos = _make_position(side="LONG", entry=100.0, sl_order_id=0)
    placer = _make_placer()

    with patch("src.execution.pretp_dispatcher._BE_SHIFT_TRIGGER_PCT", 1.0):
        await _pd.maybe_fire_be_shift(pos, mark_price=105.0, placer=placer)

    placer.cancel_algo_order.assert_not_called()


@pytest.mark.asyncio
async def test_does_not_fire_when_pretp_fired():
    pos = _make_position(side="LONG", entry=100.0, sl_order_id=42, pretp_fired=True)
    placer = _make_placer()

    with patch("src.execution.pretp_dispatcher._BE_SHIFT_TRIGGER_PCT", 1.0):
        await _pd.maybe_fire_be_shift(pos, mark_price=105.0, placer=placer)

    placer.cancel_algo_order.assert_not_called()
    placer.place_stop_loss.assert_not_called()


@pytest.mark.asyncio
async def test_be_sl_placement_failure_leaves_retry_open():
    """If BE-SL placement fails, be_shift_fired stays False so next tick retries."""
    pos = _make_position(side="LONG", entry=100.0, sl_price=99.0, sl_order_id=42)
    placer = _make_placer()
    placer.place_stop_loss = AsyncMock(
        side_effect=OrderPlacementError("binance rejected", signing_response=None)
    )

    with patch("src.execution.pretp_dispatcher._BE_SHIFT_TRIGGER_PCT", 1.0), \
         patch("src.execution.position_state.put_position") as mock_put:
        await _pd.maybe_fire_be_shift(pos, mark_price=101.5, placer=placer)

    # SL was canceled but BE-SL failed — be_shift_fired must remain False so
    # the next tick can retry the placement.
    assert pos.be_shift_fired is False
    # put_position must NOT have been called (state not persisted until success).
    mock_put.assert_not_called()


@pytest.mark.asyncio
async def test_exactly_at_threshold_fires():
    # move_pct == 1.0 exactly (with floating-point tolerance).
    pos = _make_position(side="LONG", entry=100.0, sl_price=99.0, sl_order_id=42)
    placer = _make_placer()

    with patch("src.execution.pretp_dispatcher._BE_SHIFT_TRIGGER_PCT", 1.0), \
         patch("src.execution.position_state.put_position"):
        await _pd.maybe_fire_be_shift(pos, mark_price=101.0, placer=placer)

    assert pos.be_shift_fired is True
