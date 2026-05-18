"""Tests for src.execution.pretp_controller.

The pure threshold math + the firing-decision logic are easy to
unit-test.  The order-placement path uses a mocked OrderPlacer.

What we pin:

* ``compute_pretp_threshold_price`` math: LONG threshold is above
  entry, SHORT threshold is below, by the configured percent.
* ``should_fire_pretp`` returns True only in the right state +
  threshold-crossed combination.  Idempotency: once
  ``pretp_fired=True``, returns False forever.
* ``fire_pretp`` actually places the partial-close order, marks
  the position fired, persists.
* ``fire_pretp`` is double-call protected (raises typed exception).
* ``maybe_fire_pretp`` (the verb the mark-price feed calls) is the
  short-circuit composite.
* Order placement failure in ``maybe_fire_pretp`` is logged but does
  NOT mark pretp_fired (so the next tick can retry).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution import order_placer
from src.execution import position_state
from src.execution import pretp_controller


# ---------------------------------------------------------------------------
# Threshold math
# ---------------------------------------------------------------------------


def test_compute_threshold_long() -> None:
    """LONG: threshold is ABOVE entry by ``threshold_pct``."""
    p = pretp_controller.compute_pretp_threshold_price(
        entry_price=29000.0, direction="LONG", threshold_pct=0.32
    )
    # 29000 * 1.0032 = 29092.8
    assert abs(p - 29092.8) < 0.001


def test_compute_threshold_short() -> None:
    """SHORT: threshold is BELOW entry by ``threshold_pct``."""
    p = pretp_controller.compute_pretp_threshold_price(
        entry_price=29000.0, direction="SHORT", threshold_pct=0.32
    )
    # 29000 * 0.9968 = 28907.2
    assert abs(p - 28907.2) < 0.001


def test_compute_threshold_zero_or_negative_returns_entry() -> None:
    """Defensive: a 0 or negative threshold_pct must NOT compute a
    threshold equal to entry (which would fire pre-TP immediately).
    Returns entry_price unchanged so the position stays open."""
    p = pretp_controller.compute_pretp_threshold_price(
        entry_price=29000.0, direction="LONG", threshold_pct=0.0
    )
    assert p == 29000.0
    p = pretp_controller.compute_pretp_threshold_price(
        entry_price=29000.0, direction="LONG", threshold_pct=-1.0
    )
    assert p == 29000.0


def test_compute_threshold_rejects_unknown_direction() -> None:
    with pytest.raises(ValueError):
        pretp_controller.compute_pretp_threshold_price(
            entry_price=29000.0, direction="MAYBE", threshold_pct=0.32
        )


# ---------------------------------------------------------------------------
# should_fire_pretp
# ---------------------------------------------------------------------------


def _open_long_position(
    *, threshold: float = 29092.8, fired: bool = False
) -> position_state.Position:
    return position_state.Position(
        signal_id="sig-1",
        firebase_uid="fb-x",
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
        filled_qty=1.0,
        pretp_threshold_price=threshold,
        pretp_fraction=0.5,
        pretp_fired=fired,
    )


def test_should_fire_long_when_mark_crosses_threshold() -> None:
    pos = _open_long_position(threshold=29092.8)
    assert pretp_controller.should_fire_pretp(position=pos, mark_price=29093.0)
    assert pretp_controller.should_fire_pretp(position=pos, mark_price=29092.8)  # equal counts


def test_should_not_fire_long_when_mark_below_threshold() -> None:
    pos = _open_long_position(threshold=29092.8)
    assert not pretp_controller.should_fire_pretp(position=pos, mark_price=29050.0)


def test_should_fire_short_when_mark_below_threshold() -> None:
    pos = _open_long_position()
    pos.side = "SHORT"
    pos.pretp_threshold_price = 28907.2
    assert pretp_controller.should_fire_pretp(position=pos, mark_price=28907.0)


def test_should_not_fire_after_already_fired() -> None:
    """Idempotency canary: once pretp_fired=True, never fire again
    regardless of mark price.  Critical because the mark-price feed
    will keep calling maybe_fire_pretp on every tick."""
    pos = _open_long_position(fired=True)
    assert not pretp_controller.should_fire_pretp(position=pos, mark_price=999999.0)


def test_should_not_fire_when_not_open() -> None:
    """Only OPEN can pre-TP.  PENDING means entry isn't filled yet;
    PRE_TP_FIRED / TP*_HIT / CLOSED mean we've moved past."""
    for state in (
        position_state.PositionState.PENDING,
        position_state.PositionState.PRE_TP_FIRED,
        position_state.PositionState.TP1_HIT,
        position_state.PositionState.CLOSED,
    ):
        pos = _open_long_position()
        pos.state = state
        assert not pretp_controller.should_fire_pretp(
            position=pos, mark_price=29200.0
        ), f"expected no-fire in state {state}"


def test_should_not_fire_when_threshold_zero() -> None:
    """Signal placed without pre-TP (e.g. user disabled) has
    pretp_threshold_price = 0.  Must NOT fire."""
    pos = _open_long_position(threshold=0.0)
    assert not pretp_controller.should_fire_pretp(position=pos, mark_price=29200.0)


def test_should_not_fire_when_mark_price_invalid() -> None:
    """Defensive: a stale or zero mark price must not trigger firing."""
    pos = _open_long_position()
    assert not pretp_controller.should_fire_pretp(position=pos, mark_price=0.0)
    assert not pretp_controller.should_fire_pretp(position=pos, mark_price=-1.0)


# ---------------------------------------------------------------------------
# fire_pretp — actual order placement
# ---------------------------------------------------------------------------


def _mock_placer(success: bool = True) -> MagicMock:
    placer = MagicMock()
    if success:
        placer.place_pretp_partial = AsyncMock(
            return_value=order_placer.OrderPlacementResult(
                order_id=5001, client_order_id="lumin_sig-1_pretp",
                status="FILLED", avg_price=29100.0, binance_body={},
            )
        )
    else:
        placer.place_pretp_partial = AsyncMock(
            side_effect=order_placer.OrderRejectedByBinance("rejected")
        )
    return placer


@pytest.mark.asyncio
async def test_fire_pretp_places_order_and_persists_fired_flag() -> None:
    """The doctrine in action: order placed for the configured
    fraction, position marked fired, persisted."""
    pos = _open_long_position()
    placer = _mock_placer()
    persisted: list = []
    with patch.object(
        position_state, "put_position", side_effect=lambda p: persisted.append(p)
    ):
        result = await pretp_controller.fire_pretp(pos, placer=placer)
    placer.place_pretp_partial.assert_called_once()
    kwargs = placer.place_pretp_partial.call_args.kwargs
    assert kwargs["signal_id"] == "sig-1"
    assert kwargs["symbol"] == "BTCUSDT"
    assert kwargs["direction"] == "LONG"
    assert kwargs["quantity"] == 0.5  # 0.5 fraction * 1.0 filled qty
    assert result.order_id == 5001
    assert persisted[0].pretp_fired is True
    assert persisted[0].pretp_order_id == 5001


@pytest.mark.asyncio
async def test_fire_pretp_double_call_raises_typed_error() -> None:
    """Caller-side bug: should_fire_pretp should have prevented this.
    Surface loudly with a typed exception."""
    pos = _open_long_position(fired=True)
    placer = _mock_placer()
    with pytest.raises(pretp_controller.PretpAlreadyFiredError):
        await pretp_controller.fire_pretp(pos, placer=placer)


@pytest.mark.asyncio
async def test_fire_pretp_skips_zero_qty() -> None:
    """If pretp_fraction or filled_qty are zero, nothing to close.
    Mark fired=True so we don't retry forever, but don't place an
    order."""
    pos = _open_long_position()
    pos.pretp_fraction = 0.0
    placer = _mock_placer()
    persisted: list = []
    with patch.object(
        position_state, "put_position", side_effect=lambda p: persisted.append(p)
    ):
        result = await pretp_controller.fire_pretp(pos, placer=placer)
    placer.place_pretp_partial.assert_not_called()
    assert persisted[0].pretp_fired is True
    assert result.status == "SKIPPED"


@pytest.mark.asyncio
async def test_fire_pretp_does_not_mark_fired_on_placement_failure() -> None:
    """If the order placement fails (transient), pretp_fired stays
    False so the next mark-price tick can retry.  This is the
    behaviour that keeps the doctrine functional under brief Binance
    rejections."""
    pos = _open_long_position()
    placer = _mock_placer(success=False)
    with patch.object(position_state, "put_position"):
        with pytest.raises(order_placer.OrderRejectedByBinance):
            await pretp_controller.fire_pretp(pos, placer=placer)
    # Position object's flag should NOT have been flipped.
    assert pos.pretp_fired is False


# ---------------------------------------------------------------------------
# maybe_fire_pretp — composite
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_maybe_fire_returns_false_when_threshold_not_crossed() -> None:
    """Cheap path: threshold check fails, return False without
    touching the placer."""
    pos = _open_long_position()
    placer = _mock_placer()
    fired = await pretp_controller.maybe_fire_pretp(
        pos, mark_price=29000.0, placer=placer
    )
    assert fired is False
    placer.place_pretp_partial.assert_not_called()


@pytest.mark.asyncio
async def test_maybe_fire_returns_true_and_fires_on_threshold_cross() -> None:
    pos = _open_long_position()
    placer = _mock_placer()
    with patch.object(position_state, "put_position"):
        fired = await pretp_controller.maybe_fire_pretp(
            pos, mark_price=29200.0, placer=placer
        )
    assert fired is True
    placer.place_pretp_partial.assert_called_once()


@pytest.mark.asyncio
async def test_maybe_fire_swallows_placement_failure_for_retry() -> None:
    """Transient placement failure → log + return False.  Next tick
    will retry (should_fire_pretp still returns True since
    pretp_fired wasn't flipped).  This is the retry-loop that keeps
    the doctrine functional under brief Binance hiccups."""
    pos = _open_long_position()
    placer = _mock_placer(success=False)
    fired = await pretp_controller.maybe_fire_pretp(
        pos, mark_price=29200.0, placer=placer
    )
    assert fired is False
    # pretp_fired NOT flipped — next tick can retry.
    assert pos.pretp_fired is False
