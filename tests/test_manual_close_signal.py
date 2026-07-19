"""Manual force-close of a stuck signal (ops "Close" button, 2026-07-19).

Pins:
* ``TradeMonitor.close_signal_manual`` — filled signal realises PnL at the mark,
  records the outcome, flattens the broker position, and removes it; a
  never-filled signal closes at ZERO PnL (never fabricate a never-taken trade);
  an unknown id is idempotent (closed=False, not_found).
* ``ManualTakeConsumer`` routes ``kind="close"`` to ``engine.close_signal_admin``
  and always writes a result.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.channels.base import Signal
from src.execution.manual_take import ManualTakeConsumer
from src.smc import Direction
from src.trade_monitor import TradeMonitor


def _make_signal(*, entry: float = 100.0, filled: bool = True) -> Signal:
    sig = Signal(
        channel="360_SCALP",
        symbol="SOLUSDT",
        direction=Direction.LONG,
        entry=entry,
        stop_loss=entry * 0.98,
        tp1=entry * 1.02,
        tp2=entry * 1.04,
        confidence=75.0,
        signal_id="STUCK-1",
    )
    sig.timestamp = datetime.now(timezone.utc)
    sig.setup_class = "MOVER_TREND_PULLBACK"
    sig.status = "ACTIVE"
    sig.current_price = entry * 1.01
    if filled:
        sig.entry_zone_low = entry * 0.999
        sig.entry_zone_high = entry * 1.001
        sig.entry_zone_filled = True
    return sig


def _build_monitor(active, price=None):
    removed: list[str] = []
    sent: list = []

    async def mock_send(chat_id, text):
        sent.append((chat_id, text))

    data_store = MagicMock()
    data_store.get_candles.return_value = {}
    data_store.ticks = {}
    monitor = TradeMonitor(
        data_store=data_store,
        send_telegram=mock_send,
        get_active_signals=lambda: dict(active),
        remove_signal=lambda sid: removed.append(sid),
        update_signal=MagicMock(),
        performance_tracker=MagicMock(),
    )
    monitor._broker_close_full = AsyncMock()
    monitor._latest_price = MagicMock(return_value=price)
    return monitor, removed, sent


async def test_close_filled_signal_realises_and_removes():
    sig = _make_signal(entry=100.0, filled=True)
    monitor, removed, _ = _build_monitor({sig.signal_id: sig}, price=102.0)

    result = await monitor.close_signal_manual(sig.signal_id)

    assert result["closed"] is True
    assert result["status"] == "CLOSED"
    assert result["pnl_pct"] == pytest.approx(2.0, abs=0.2)
    assert sig.status == "CLOSED"
    assert sig.signal_id in removed
    monitor._broker_close_full.assert_awaited_once()
    monitor._performance_tracker.record_outcome.assert_called_once()


async def test_close_never_filled_is_zero_pnl():
    sig = _make_signal(entry=100.0, filled=False)  # zone set below, never visited
    sig.entry_zone_low = 99.9
    sig.entry_zone_high = 100.1
    sig.entry_zone_filled = False
    monitor, removed, _ = _build_monitor({sig.signal_id: sig}, price=102.0)

    result = await monitor.close_signal_manual(sig.signal_id)

    assert result["closed"] is True
    assert result["pnl_pct"] == 0.0  # never fabricate a never-taken trade's PnL
    assert sig.pnl_pct == 0.0
    assert sig.signal_id in removed
    monitor._broker_close_full.assert_awaited_once()


async def test_close_unknown_id_is_idempotent_not_found():
    monitor, removed, _ = _build_monitor({}, price=102.0)

    result = await monitor.close_signal_manual("does-not-exist")

    assert result["closed"] is False
    assert result["reason"] == "not_found"
    assert removed == []
    monitor._broker_close_full.assert_not_awaited()


async def test_consumer_routes_close_kind_and_writes_result():
    engine = MagicMock()
    engine.close_signal_admin = AsyncMock(
        return_value={"closed": True, "signal_id": "STUCK-1", "status": "CLOSED"}
    )
    redis = MagicMock()
    redis.available = True
    redis.client = MagicMock()
    redis.client.set = AsyncMock()
    consumer = ManualTakeConsumer(engine, redis)

    envelope = json.dumps(
        {"kind": "close", "request_id": "req-1", "signal_id": "STUCK-1", "ts": 0}
    )
    await consumer._process(envelope)

    engine.close_signal_admin.assert_awaited_once_with("STUCK-1")
    redis.client.set.assert_awaited_once()
    written = json.loads(redis.client.set.call_args.args[1])
    assert written["closed"] is True


async def test_consumer_close_missing_signal_id_drops():
    engine = MagicMock()
    engine.close_signal_admin = AsyncMock()
    redis = MagicMock()
    redis.available = True
    redis.client = MagicMock()
    redis.client.set = AsyncMock()
    consumer = ManualTakeConsumer(engine, redis)

    await consumer._process(json.dumps({"kind": "close", "request_id": "req-2"}))

    engine.close_signal_admin.assert_not_awaited()
    redis.client.set.assert_not_awaited()
