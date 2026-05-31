"""Tests for ``OrderManager.close_full`` and ``.add_dca_entry``.

The live-mode CCXT path that closes broker positions on non-TP exits
(SL_HIT / INVALIDATED / EXPIRED / CANCELLED) and adds the DCA Entry-2
when the engine fires DCA.  Mirrors the paper-mode coverage in
``test_paper_order_manager_close_and_dca.py``.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.order_manager import OrderManager
from src.smc import Direction


def _make_signal(
    *,
    signal_id: str = "LIVE-DCA-001",
    symbol: str = "ETHUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 2370.0,
    current_price: float = 2370.0,
    stop_loss: float = 2351.0,
    pnl_pct: float = 0.0,
    entry_2: float = 0.0,
    weight_1: float = 0.6,
    weight_2: float = 0.4,
):
    sig = MagicMock()
    sig.signal_id = signal_id
    sig.symbol = symbol
    sig.direction = direction
    sig.entry = entry
    sig.current_price = current_price
    sig.stop_loss = stop_loss
    sig.pnl_pct = pnl_pct
    sig.entry_2 = entry_2
    sig.position_weight_1 = weight_1
    sig.position_weight_2 = weight_2
    sig.channel = "360_SCALP"
    return sig


def _ccxt_client():
    """Mock CCXT client with the methods OrderManager touches."""
    client = MagicMock()
    client.create_market_order = AsyncMock(return_value={"id": "ccxt-12345"})
    client.fetch_balance = AsyncMock(return_value={"USDT": {"free": 10000.0}})
    client.cancel_order = AsyncMock(return_value={"status": "canceled"})
    return client


# ---------------------------------------------------------------------------
# close_full
# ---------------------------------------------------------------------------


async def test_close_full_disabled_returns_none():
    om = OrderManager(auto_execution_enabled=False, exchange_client=None)
    sig = _make_signal()
    assert await om.close_full(sig, reason="invalidated") is None


async def test_close_full_with_no_tracked_qty_is_noop():
    """Risk gate refused the open — no qty to close."""
    om = OrderManager(auto_execution_enabled=True, exchange_client=_ccxt_client())
    sig = _make_signal()
    assert await om.close_full(sig, reason="invalidated") is None


async def test_close_full_long_sells_remaining_qty():
    client = _ccxt_client()
    om = OrderManager(auto_execution_enabled=True, exchange_client=client)
    sig = _make_signal(direction=Direction.LONG)
    await om.place_market_order(sig, quantity=1.0)
    client.create_market_order.reset_mock()

    order_id = await om.close_full(sig, reason="invalidated")
    assert order_id == "ccxt-12345"
    # LONG close → sell side
    args, kwargs = client.create_market_order.call_args
    assert args[1] == "sell"
    assert args[2] == pytest.approx(1.0)


async def test_close_full_short_buys_remaining_qty():
    client = _ccxt_client()
    om = OrderManager(auto_execution_enabled=True, exchange_client=client)
    sig = _make_signal(direction=Direction.SHORT)
    await om.place_market_order(sig, quantity=0.5)
    client.create_market_order.reset_mock()

    await om.close_full(sig, reason="sl_hit")
    args, _ = client.create_market_order.call_args
    assert args[1] == "buy"
    assert args[2] == pytest.approx(0.5)


async def test_close_full_after_partial_closes_only_closes_remainder():
    """TP1+TP2 fired → 66% closed → close_full closes 34% remaining."""
    client = _ccxt_client()
    om = OrderManager(auto_execution_enabled=True, exchange_client=client)
    sig = _make_signal()
    await om.place_market_order(sig, quantity=1.0)
    await om.close_partial(sig, fraction=0.33, tp_level=1)
    await om.close_partial(sig, fraction=0.33, tp_level=2)
    client.create_market_order.reset_mock()

    await om.close_full(sig, reason="invalidated")
    args, _ = client.create_market_order.call_args
    assert args[2] == pytest.approx(1.0 * (1.0 - 0.33 - 0.33), rel=1e-3)


async def test_close_full_idempotent_after_full_close():
    client = _ccxt_client()
    om = OrderManager(auto_execution_enabled=True, exchange_client=client)
    sig = _make_signal()
    await om.place_market_order(sig, quantity=1.0)
    first = await om.close_full(sig, reason="invalidated")
    assert first is not None
    # Tracking dict now empty — second call is a no-op.
    second = await om.close_full(sig, reason="invalidated")
    assert second is None


async def test_close_full_after_tp3_full_close_is_noop():
    """All three TPs fire → 100% closed → close_full is a no-op."""
    client = _ccxt_client()
    om = OrderManager(auto_execution_enabled=True, exchange_client=client)
    sig = _make_signal()
    await om.place_market_order(sig, quantity=1.0)
    await om.close_partial(sig, fraction=0.33, tp_level=1)
    await om.close_partial(sig, fraction=0.33, tp_level=2)
    await om.close_partial(sig, fraction=0.34, tp_level=3)
    # 100% closed; TPs are tracked so close_full sees 0 remaining and bails.
    result = await om.close_full(sig, reason="expired")
    assert result is None


async def test_close_full_handles_ccxt_error_returns_none():
    client = _ccxt_client()
    client.create_market_order.side_effect = RuntimeError("connection refused")
    om = OrderManager(auto_execution_enabled=True, exchange_client=client)
    sig = _make_signal()
    om._open_quantities[sig.signal_id] = 1.0
    result = await om.close_full(sig, reason="invalidated")
    assert result is None
    # Tracking remains so PositionReconciler can pick up the orphan on its
    # next sweep — close_full failure must not silently drop the qty.
    assert om._open_quantities.get(sig.signal_id, 0.0) == 1.0


async def test_close_full_calls_register_close_on_risk_manager():
    rm = MagicMock()
    rm.check.return_value = MagicMock(allowed=True, reason="", detail="")
    client = _ccxt_client()
    om = OrderManager(
        auto_execution_enabled=True,
        exchange_client=client,
        risk_manager=rm,
    )
    sig = _make_signal()
    await om.place_market_order(sig, quantity=1.0)
    rm.register_open.assert_called_once()

    await om.close_full(sig, reason="invalidated")
    rm.register_close.assert_called_once()


# ---------------------------------------------------------------------------
# add_dca_entry
# ---------------------------------------------------------------------------


async def test_add_dca_entry_disabled_returns_none():
    om = OrderManager(auto_execution_enabled=False)
    sig = _make_signal(entry_2=2360.0)
    assert await om.add_dca_entry(sig) is None


async def test_add_dca_entry_no_existing_position_warns_and_noops():
    om = OrderManager(auto_execution_enabled=True, exchange_client=_ccxt_client())
    sig = _make_signal(entry_2=2360.0)
    assert await om.add_dca_entry(sig) is None


async def test_add_dca_entry_long_buys_additional_qty():
    client = _ccxt_client()
    om = OrderManager(auto_execution_enabled=True, exchange_client=client)
    sig = _make_signal(direction=Direction.LONG, entry_2=2360.0)
    await om.place_market_order(sig, quantity=1.0)
    client.create_market_order.reset_mock()

    order_id = await om.add_dca_entry(sig)
    assert order_id == "ccxt-12345"
    args, _ = client.create_market_order.call_args
    assert args[1] == "buy"  # LONG DCA → same side as Entry 1
    # weight_2/weight_1 = 0.4/0.6 = 0.667
    assert args[2] == pytest.approx(1.0 * (0.4 / 0.6), rel=1e-3)


async def test_add_dca_entry_updates_tracked_quantity():
    client = _ccxt_client()
    om = OrderManager(auto_execution_enabled=True, exchange_client=client)
    sig = _make_signal(entry_2=2360.0)
    await om.place_market_order(sig, quantity=1.0)

    await om.add_dca_entry(sig)
    # Subsequent close_full must close the LARGER tracked qty.
    client.create_market_order.reset_mock()
    await om.close_full(sig, reason="invalidated")
    args, _ = client.create_market_order.call_args
    assert args[2] == pytest.approx(1.0 * (1.0 + 0.4 / 0.6), rel=1e-3)


async def test_add_dca_entry_blocked_by_risk_gate_at_dca_time():
    rm = MagicMock()
    rm.check.side_effect = [
        MagicMock(allowed=True, reason="", detail=""),
        MagicMock(allowed=False, reason="daily_loss_kill", detail="kill switch tripped"),
    ]
    client = _ccxt_client()
    om = OrderManager(
        auto_execution_enabled=True,
        exchange_client=client,
        risk_manager=rm,
    )
    sig = _make_signal(entry_2=2360.0)
    await om.place_market_order(sig, quantity=1.0)
    client.create_market_order.reset_mock()

    result = await om.add_dca_entry(sig)
    assert result is None
    # No additional CCXT order placed.
    client.create_market_order.assert_not_called()
    # Tracked qty unchanged.
    assert om._open_quantities[sig.signal_id] == pytest.approx(1.0)


async def test_add_dca_entry_handles_ccxt_error_returns_none():
    client = _ccxt_client()
    om = OrderManager(auto_execution_enabled=True, exchange_client=client)
    sig = _make_signal(entry_2=2360.0)
    await om.place_market_order(sig, quantity=1.0)
    client.create_market_order.side_effect = RuntimeError("connection refused")

    result = await om.add_dca_entry(sig)
    assert result is None
    # Tracked qty NOT incremented on failure — engine math will assume
    # DCA filled but close_full will only close the original Entry 1.
    assert om._open_quantities[sig.signal_id] == pytest.approx(1.0)


async def test_add_dca_entry_invalid_weight_1_no_op():
    client = _ccxt_client()
    om = OrderManager(auto_execution_enabled=True, exchange_client=client)
    sig = _make_signal(entry_2=2360.0, weight_1=0.0)
    await om.place_market_order(sig, quantity=1.0)
    client.create_market_order.reset_mock()
    result = await om.add_dca_entry(sig)
    assert result is None
    client.create_market_order.assert_not_called()


# ---------------------------------------------------------------------------
# Redis persistence — Fix B (fix/dca-broker-sync)
# ---------------------------------------------------------------------------


def _make_redis_client(*, available: bool = True, data: dict | None = None) -> MagicMock:
    """Build a mock RedisClient that behaves like the real one."""
    store = dict(data or {})
    rc = MagicMock()
    rc.available = available

    async def _set(key, value):
        store[key] = value

    async def _delete(*keys):
        for k in keys:
            store.pop(k, None)

    async def _get(key):
        return store.get(key)

    async def _keys(pattern):
        # Naive prefix match: "om:open_qty:*" → all keys starting with "om:open_qty:"
        prefix = pattern.rstrip("*")
        return [k for k in store if k.startswith(prefix)]

    inner = MagicMock()
    inner.set = AsyncMock(side_effect=_set)
    inner.delete = AsyncMock(side_effect=_delete)
    inner.get = AsyncMock(side_effect=_get)
    inner.keys = AsyncMock(side_effect=_keys)
    rc.client = inner
    rc.mark_unavailable = MagicMock()
    return rc, store


async def test_place_market_order_writes_qty_to_redis():
    """Successful place_market_order → qty written to Redis."""
    client = _ccxt_client()
    redis_mock, store = _make_redis_client()
    om = OrderManager(
        auto_execution_enabled=True,
        exchange_client=client,
        redis_client=redis_mock,
    )
    sig = _make_signal()
    await om.place_market_order(sig, quantity=1.5)
    assert store.get(f"om:open_qty:{sig.signal_id}") == repr(1.5)


async def test_add_dca_entry_updates_qty_in_redis():
    """Successful add_dca_entry → updated total qty written to Redis."""
    client = _ccxt_client()
    redis_mock, store = _make_redis_client()
    om = OrderManager(
        auto_execution_enabled=True,
        exchange_client=client,
        redis_client=redis_mock,
    )
    sig = _make_signal(entry_2=2360.0)
    await om.place_market_order(sig, quantity=1.0)
    await om.add_dca_entry(sig)
    expected_total = pytest.approx(1.0 + 1.0 * (0.4 / 0.6), rel=1e-3)
    stored_qty = float(store[f"om:open_qty:{sig.signal_id}"])
    assert stored_qty == expected_total


async def test_close_full_deletes_qty_from_redis():
    """Successful close_full → Redis keys are deleted."""
    client = _ccxt_client()
    redis_mock, store = _make_redis_client()
    om = OrderManager(
        auto_execution_enabled=True,
        exchange_client=client,
        redis_client=redis_mock,
    )
    sig = _make_signal()
    await om.place_market_order(sig, quantity=1.0)
    assert f"om:open_qty:{sig.signal_id}" in store
    await om.close_full(sig, reason="invalidated")
    assert f"om:open_qty:{sig.signal_id}" not in store


async def test_restore_open_quantities_from_redis():
    """restore_open_quantities_from_redis loads prior session's open qtys."""
    _signal_id = "BTCUSDT-restore-001"
    redis_mock, _ = _make_redis_client(
        data={
            f"om:open_qty:{_signal_id}": repr(2.5),
            f"om:partial_tps:{_signal_id}": "1",
        }
    )
    om = OrderManager(
        auto_execution_enabled=True,
        exchange_client=None,
        redis_client=redis_mock,
    )
    restored = await om.restore_open_quantities_from_redis()
    assert restored == 1
    assert om._open_quantities[_signal_id] == pytest.approx(2.5)
    assert om._partial_closed_tps[_signal_id] == {1}


async def test_restore_returns_zero_when_redis_unavailable():
    """No crash and returns 0 when Redis is not available."""
    redis_mock, _ = _make_redis_client(available=False)
    om = OrderManager(
        auto_execution_enabled=True,
        exchange_client=None,
        redis_client=redis_mock,
    )
    result = await om.restore_open_quantities_from_redis()
    assert result == 0
    assert om._open_quantities == {}


async def test_add_dca_entry_fires_after_restore():
    """After restore_open_quantities_from_redis, add_dca_entry can fire
    for a signal that was open before the engine restart."""
    _signal_id = "ETHUSDT-restart-001"
    client = _ccxt_client()
    redis_mock, _ = _make_redis_client(
        data={f"om:open_qty:{_signal_id}": repr(1.0)}
    )
    om = OrderManager(
        auto_execution_enabled=True,
        exchange_client=client,
        redis_client=redis_mock,
    )
    await om.restore_open_quantities_from_redis()

    sig = _make_signal(signal_id=_signal_id, entry_2=2360.0)
    order_id = await om.add_dca_entry(sig)
    assert order_id == "ccxt-12345", (
        "add_dca_entry must succeed when qty was restored from Redis"
    )
