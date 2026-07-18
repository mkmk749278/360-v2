"""Manual trade builder — reconciler handling of LIMIT-entry rests + user_owned.

Pins the reconciler behaviour added for the manual trade builder
(``docs/MANUAL_TRADE_BUILDER_DESIGN.md``):

* A PENDING_ENTRY (resting LIMIT) is flat on Binance by definition and must
  NOT be misread as a manual close.
* Past its TTL → cancel the resting order + CANCELLED_NO_FILL; within TTL or
  GTC (no TTL) → left resting.
* Filled-but-unadvanced (missed fill event) → heal to OPEN + place protection.
* user_owned positions are exempt from the stale-age force-close and from
  auto re-placement of an externally-cancelled stop (the user owns the exit).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution import order_placer
from src.execution import position_state
from src.execution import reconciler
from src.security.signing_service import protocol as sig_protocol


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
    return p


def _signing_flat(symbol="BTCUSDT", amt="0"):
    mock = MagicMock()
    mock.binance_signed_get = AsyncMock(
        return_value=sig_protocol.SignResponse.ok_reply(
            "req-x", binance_status=200,
            binance_body=[{"symbol": symbol, "positionAmt": amt}],
        )
    )
    return mock


def _pending_entry(
    *,
    protection_mode="managed",
    expires_at=None,
    entry_order_id=1001,
):
    return position_state.Position(
        signal_id="sig-1", firebase_uid="fb-x", symbol="BTCUSDT", side="LONG",
        state=position_state.PositionState.PENDING_ENTRY,
        entry_price_target=29000.0, entry_price_filled=0.0, sl_price=28500.0,
        tp1_price=29500.0, tp2_price=30000.0, tp3_price=30500.0,
        total_qty=1.0, tp1_qty=0.3, tp2_qty=0.4, tp3_qty=0.3,
        entry_order_id=entry_order_id, protection_mode=protection_mode,
        entry_expires_at=expires_at,
    )


def _reconciler(pos, placer, signing):
    return reconciler.Reconciler(
        positions_for_user=lambda uid: [pos],
        signing_client_factory=lambda: signing,
        order_placer_factory=lambda uid: placer,
    )


@pytest.mark.asyncio
async def test_pending_entry_expired_is_cancelled():
    past = datetime.now(timezone.utc) - timedelta(minutes=1)
    pos = _pending_entry(expires_at=past)
    placer, signing = _placer(), _signing_flat(amt="0")
    persisted: List = []
    r = _reconciler(pos, placer, signing)
    with patch.object(position_state, "put_position",
                      side_effect=lambda p: persisted.append(p)):
        await r.reconcile_user("fb-x")
    placer.cancel_order.assert_awaited_once()
    assert placer.cancel_order.call_args.kwargs["order_id"] == 1001
    assert persisted[-1].state == position_state.PositionState.CANCELLED_NO_FILL
    assert persisted[-1].close_reason == "EXPIRED_NO_FILL"


@pytest.mark.asyncio
async def test_pending_entry_within_ttl_is_left_resting():
    future = datetime.now(timezone.utc) + timedelta(minutes=10)
    pos = _pending_entry(expires_at=future)
    placer, signing = _placer(), _signing_flat(amt="0")
    persisted: List = []
    r = _reconciler(pos, placer, signing)
    with patch.object(position_state, "put_position",
                      side_effect=lambda p: persisted.append(p)):
        await r.reconcile_user("fb-x")
    placer.cancel_order.assert_not_called()
    # Not misread as a manual close, not cancelled — nothing persisted.
    assert persisted == []
    assert pos.state == position_state.PositionState.PENDING_ENTRY


@pytest.mark.asyncio
async def test_pending_entry_gtc_no_ttl_is_left_resting():
    pos = _pending_entry(expires_at=None)  # GTC, no expiry
    placer, signing = _placer(), _signing_flat(amt="0")
    persisted: List = []
    r = _reconciler(pos, placer, signing)
    with patch.object(position_state, "put_position",
                      side_effect=lambda p: persisted.append(p)):
        await r.reconcile_user("fb-x")
    placer.cancel_order.assert_not_called()
    assert persisted == []


@pytest.mark.asyncio
async def test_pending_entry_filled_heals_to_open_and_places_protection():
    pos = _pending_entry(expires_at=None)
    placer, signing = _placer(), _signing_flat(amt="1")  # filled on Binance
    persisted: List = []
    r = _reconciler(pos, placer, signing)
    with patch.object(position_state, "put_position",
                      side_effect=lambda p: persisted.append(p)), \
         patch("src.execution.dispatch_log.record_rejected", MagicMock()), \
         patch("src.execution.dispatch_log.record_placed", MagicMock()):
        await r.reconcile_user("fb-x")
    assert persisted[-1].state == position_state.PositionState.OPEN
    placer.cancel_order.assert_not_called()   # nothing to cancel — it filled
    placer.place_stop_loss.assert_awaited_once()  # protection healed


@pytest.mark.asyncio
async def test_stale_close_exempts_user_owned():
    old = datetime.now(timezone.utc) - timedelta(days=2)
    pos = _pending_entry(protection_mode="user_owned")
    pos.state = position_state.PositionState.OPEN
    pos.created_at = old
    placer = _placer()
    r = reconciler.Reconciler(
        positions_for_user=lambda uid: [pos],
        signing_client_factory=lambda: MagicMock(),
        order_placer_factory=lambda uid: placer,
        max_position_age_sec=1,
        stale_close_enabled=True,
    )
    await r._maybe_force_close_stale(pos)
    placer.place_market_close.assert_not_called()
    assert pos.state == position_state.PositionState.OPEN


@pytest.mark.asyncio
async def test_stale_close_still_fires_for_managed():
    old = datetime.now(timezone.utc) - timedelta(days=2)
    pos = _pending_entry(protection_mode="managed")
    pos.state = position_state.PositionState.OPEN
    pos.created_at = old
    placer = _placer()
    r = reconciler.Reconciler(
        positions_for_user=lambda uid: [pos],
        signing_client_factory=lambda: MagicMock(),
        order_placer_factory=lambda uid: placer,
        max_position_age_sec=1,
        stale_close_enabled=True,
    )
    with patch.object(position_state, "put_position", MagicMock()):
        await r._maybe_force_close_stale(pos)
    placer.place_market_close.assert_awaited_once()
    assert pos.state == position_state.PositionState.CLOSED


@pytest.mark.asyncio
async def test_replace_lost_stop_exempts_user_owned():
    pos = _pending_entry(protection_mode="user_owned")
    pos.state = position_state.PositionState.OPEN
    placer = _placer()
    r = reconciler.Reconciler(
        positions_for_user=lambda uid: [pos],
        signing_client_factory=lambda: MagicMock(),
        order_placer_factory=lambda uid: placer,
    )
    await r._replace_lost_stop(pos)
    placer.place_stop_loss.assert_not_called()  # user owns the exit
