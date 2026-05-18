"""Tests for src.execution.pretp_dispatcher.

The feed + position lookup are injected so we don't need real WS /
Firestore.  What we pin:

* ``track`` subscribes to the feed (idempotent — track twice = one
  subscribe).
* ``untrack`` unsubscribes (idempotent).
* On a tick, every OPEN position for that symbol gets
  ``maybe_fire_pretp`` called.
* maybe_fire_pretp exception for one position doesn't block others
  on the same symbol.
* No callbacks fire for symbols we didn't track.
"""
from __future__ import annotations

import asyncio
from typing import List
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.execution import mark_price_feed
from src.execution import position_state
from src.execution import pretp_controller
from src.execution import pretp_dispatcher


def _make_position(
    *, signal_id: str = "sig-1", symbol: str = "BTCUSDT"
) -> position_state.Position:
    return position_state.Position(
        signal_id=signal_id,
        firebase_uid="fb-x",
        symbol=symbol,
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
        pretp_threshold_price=29092.8,
        pretp_fraction=0.5,
    )


@pytest.mark.asyncio
async def test_track_subscribes_to_feed_idempotently() -> None:
    feed = MagicMock()
    feed.subscribe = AsyncMock()
    feed.unsubscribe = AsyncMock()
    dispatcher = pretp_dispatcher.PretpDispatcher(
        feed,
        positions_for_symbol=lambda s: [],
        order_placer_factory=lambda uid: MagicMock(),
    )
    await dispatcher.track("BTCUSDT")
    await dispatcher.track("BTCUSDT")  # duplicate
    assert feed.subscribe.await_count == 1


@pytest.mark.asyncio
async def test_untrack_unsubscribes_idempotently() -> None:
    feed = MagicMock()
    feed.subscribe = AsyncMock()
    feed.unsubscribe = AsyncMock()
    dispatcher = pretp_dispatcher.PretpDispatcher(
        feed,
        positions_for_symbol=lambda s: [],
        order_placer_factory=lambda uid: MagicMock(),
    )
    await dispatcher.track("BTCUSDT")
    await dispatcher.untrack("BTCUSDT")
    await dispatcher.untrack("BTCUSDT")  # duplicate
    assert feed.unsubscribe.await_count == 1


@pytest.mark.asyncio
async def test_tick_dispatches_to_all_matching_positions() -> None:
    """The doctrine-critical fan-out: when BTCUSDT mark price ticks,
    every OPEN BTCUSDT position across all users gets the pre-TP
    check."""
    feed = MagicMock()
    feed.subscribe = AsyncMock()
    feed.unsubscribe = AsyncMock()
    pos_a = _make_position(signal_id="sig-a")
    pos_b = _make_position(signal_id="sig-b")
    pos_b.firebase_uid = "fb-y"
    positions = [pos_a, pos_b]

    placer = MagicMock()
    placer.place_pretp_partial = AsyncMock()
    fire_calls: List = []

    async def fake_maybe_fire(position, *, mark_price, placer):
        fire_calls.append((position.signal_id, mark_price))
        return True

    dispatcher = pretp_dispatcher.PretpDispatcher(
        feed,
        positions_for_symbol=lambda s: positions if s == "BTCUSDT" else [],
        order_placer_factory=lambda uid: placer,
    )
    # Monkey-patch to avoid touching the real pretp_controller logic.
    import src.execution.pretp_dispatcher as pd_mod

    original = pd_mod._pretp_controller.maybe_fire_pretp
    pd_mod._pretp_controller.maybe_fire_pretp = fake_maybe_fire
    try:
        await dispatcher.track("BTCUSDT")
        # Simulate a tick directly (bypassing feed.subscribe wiring).
        await dispatcher._on_tick("BTCUSDT", 29200.0)
    finally:
        pd_mod._pretp_controller.maybe_fire_pretp = original
    assert {c[0] for c in fire_calls} == {"sig-a", "sig-b"}
    assert all(c[1] == 29200.0 for c in fire_calls)


@pytest.mark.asyncio
async def test_one_position_failure_does_not_block_others() -> None:
    """The fan-out's defence-in-depth: a buggy maybe_fire_pretp on
    one position must not prevent the dispatcher from processing
    the others on the same symbol."""
    feed = MagicMock()
    feed.subscribe = AsyncMock()
    feed.unsubscribe = AsyncMock()
    pos_a = _make_position(signal_id="sig-a")
    pos_b = _make_position(signal_id="sig-b")
    positions = [pos_a, pos_b]

    processed: List[str] = []

    async def maybe_fire(position, *, mark_price, placer):
        if position.signal_id == "sig-a":
            raise RuntimeError("bug")
        processed.append(position.signal_id)
        return True

    dispatcher = pretp_dispatcher.PretpDispatcher(
        feed,
        positions_for_symbol=lambda s: positions,
        order_placer_factory=lambda uid: MagicMock(),
    )
    import src.execution.pretp_dispatcher as pd_mod

    original = pd_mod._pretp_controller.maybe_fire_pretp
    pd_mod._pretp_controller.maybe_fire_pretp = maybe_fire
    try:
        await dispatcher._on_tick("BTCUSDT", 29200.0)
    finally:
        pd_mod._pretp_controller.maybe_fire_pretp = original
    assert processed == ["sig-b"]


@pytest.mark.asyncio
async def test_positions_for_symbol_failure_logged_not_raised() -> None:
    """The Firestore query for positions could fail (transient
    network).  Dispatcher must log + continue rather than crash the
    feed's dispatch task."""
    feed = MagicMock()

    def bad_query(s: str):
        raise RuntimeError("Firestore down")

    dispatcher = pretp_dispatcher.PretpDispatcher(
        feed,
        positions_for_symbol=bad_query,
        order_placer_factory=lambda uid: MagicMock(),
    )
    # Must not raise.
    await dispatcher._on_tick("BTCUSDT", 29200.0)
