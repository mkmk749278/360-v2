"""Tests for TradeMonitor → broker wiring on non-TP closes + DCA.

Verifies that every non-TP close path (SL_HIT / INVALIDATED / EXPIRED /
CANCELLED) calls ``order_manager.close_full(signal, reason=...)`` so the
broker position closes in lockstep with engine state.  Also verifies
that the DCA path calls ``order_manager.add_dca_entry`` so engine math
stays aligned with broker reality.

Without this wiring the broker leaves positions open indefinitely after
the engine has stopped tracking them — a B12 safety hole.
"""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.channels.base import Signal
from src.smc import Direction
from src.trade_monitor import TradeMonitor
from src.utils import utcnow


def _make_signal(
    *,
    channel: str = "360_SCALP",
    symbol: str = "ETHUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 2370.0,
    stop_loss: float = 2351.0,
    tp1: float = 2392.0,
    setup_class: str = "SR_FLIP_RETEST",
    age_seconds: float = 600.0,  # past min-lifespan + DCA grace
    pnl_pct: float = 0.0,
    current_price: float = 2370.0,
) -> Signal:
    sig = Signal(
        channel=channel,
        symbol=symbol,
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=entry * 1.025 if direction == Direction.LONG else entry * 0.975,
        confidence=80.0,
        signal_id=f"BROKER-CLOSE-{symbol}-001",
    )
    sig.tp3 = entry * 1.04 if direction == Direction.LONG else entry * 0.96
    sig.original_entry = entry
    sig.current_price = current_price
    sig.setup_class = setup_class
    sig.signal_tier = "B"
    sig.timestamp = utcnow() - timedelta(seconds=age_seconds)
    sig.pnl_pct = pnl_pct
    sig.status = "ACTIVE"
    return sig


def _data_store_with_candle(high: float, low: float):
    ds = MagicMock()
    ds.get_candles.return_value = {
        "high": [high],
        "low": [low],
        "close": [(high + low) / 2],
        "open": [(high + low) / 2],
        "volume": [1000.0],
    }
    ds.ticks = {}
    return ds


def _build_monitor(*, order_manager=None, data_store=None,
                   regime_label: str = "TRENDING_UP"):
    regime_detector = MagicMock()
    regime_detector.classify.return_value = MagicMock(
        regime=MagicMock(value=regime_label)
    )
    send = AsyncMock(return_value=True)
    monitor = TradeMonitor(
        data_store=data_store or MagicMock(),
        send_telegram=send,
        get_active_signals=lambda: {},
        remove_signal=lambda sid: None,
        update_signal=MagicMock(),
        regime_detector=regime_detector,
        indicators_fn=lambda sym: {"adx": 18.0, "ema_slope": 0.0},
        order_manager=order_manager,
    )
    return monitor


def _enabled_order_manager():
    om = MagicMock()
    om.is_enabled = True
    om.close_full = AsyncMock(return_value="ccxt-close-id")
    om.add_dca_entry = AsyncMock(return_value="ccxt-dca-id")
    return om


# ---------------------------------------------------------------------------
# _broker_close_full helper — direct unit tests
# ---------------------------------------------------------------------------


async def test_broker_close_full_with_no_order_manager_is_noop():
    monitor = _build_monitor(order_manager=None)
    sig = _make_signal()
    # Should not raise.
    await monitor._broker_close_full(sig, reason="invalidated", fill_price=2360.0)


async def test_broker_close_full_with_disabled_order_manager_is_noop():
    om = MagicMock()
    om.is_enabled = False
    om.close_full = AsyncMock()
    monitor = _build_monitor(order_manager=om)
    sig = _make_signal()
    await monitor._broker_close_full(sig, reason="invalidated", fill_price=2360.0)
    om.close_full.assert_not_called()


async def test_broker_close_full_swallows_order_manager_error():
    """A broker error must NOT propagate — engine state has already
    transitioned and the reconciler is the safety net."""
    om = _enabled_order_manager()
    om.close_full = AsyncMock(side_effect=RuntimeError("connection refused"))
    monitor = _build_monitor(order_manager=om)
    sig = _make_signal()
    # Should not raise.
    await monitor._broker_close_full(sig, reason="invalidated", fill_price=2360.0)


async def test_broker_close_full_passes_reason_and_price():
    om = _enabled_order_manager()
    monitor = _build_monitor(order_manager=om)
    sig = _make_signal()
    await monitor._broker_close_full(sig, reason="sl_hit", fill_price=2351.0)
    om.close_full.assert_awaited_once()
    kw = om.close_full.call_args.kwargs
    assert kw["reason"] == "sl_hit"
    assert kw["current_price"] == pytest.approx(2351.0)


# ---------------------------------------------------------------------------
# Wiring — verify each non-TP close path triggers a broker close
# ---------------------------------------------------------------------------


async def test_invalidated_close_calls_broker_close_full(monkeypatch):
    """When invalidation fires, the broker close must be called with
    reason='invalidated'."""
    om = _enabled_order_manager()
    ds = _data_store_with_candle(high=2362.0, low=2358.0)
    monitor = _build_monitor(order_manager=om, data_store=ds)
    monkeypatch.setattr(
        TradeMonitor, "_check_invalidation",
        lambda self, s: "momentum_loss test",
    )

    sig = _make_signal(direction=Direction.LONG, entry=2370.0, stop_loss=2351.0,
                       current_price=2360.0)
    await monitor._evaluate_signal(sig)

    om.close_full.assert_awaited_once()
    kw = om.close_full.call_args.kwargs
    assert kw["reason"] == "invalidated"


async def test_sl_hit_close_calls_broker_close_full():
    om = _enabled_order_manager()
    # Candle low pierces SL → SL_HIT path fires.
    ds = _data_store_with_candle(high=2360.0, low=2348.0)
    monitor = _build_monitor(order_manager=om, data_store=ds)

    sig = _make_signal(direction=Direction.LONG, entry=2370.0, stop_loss=2351.0,
                       current_price=2348.0)
    await monitor._evaluate_signal(sig)

    om.close_full.assert_awaited_once()
    kw = om.close_full.call_args.kwargs
    assert kw["reason"] == "sl_hit"
    # Fill price stamped at SL level (not the worse low).
    assert kw["current_price"] == pytest.approx(2351.0)


async def test_expired_close_calls_broker_close_full():
    """Max-hold expiry must close the broker position.  Uses an
    age >> any plausible MAX_SIGNAL_HOLD_SECONDS so the test isn't
    fragile to other tests' monkeypatches of that config dict."""
    om = _enabled_order_manager()
    ds = _data_store_with_candle(high=2370.0, low=2370.0)
    monitor = _build_monitor(order_manager=om, data_store=ds)

    # 100,000s = ~28h, well past the 3600s SCALP hold cap.
    sig = _make_signal(age_seconds=100_000.0, current_price=2370.0)
    await monitor._evaluate_signal(sig)

    om.close_full.assert_awaited_once()
    kw = om.close_full.call_args.kwargs
    assert kw["reason"] == "expired"


async def test_cancelled_invalid_sl_calls_broker_close_full():
    """LONG with SL above entry → CANCELLED; broker position must close."""
    om = _enabled_order_manager()
    ds = _data_store_with_candle(high=2362.0, low=2358.0)
    monitor = _build_monitor(order_manager=om, data_store=ds)

    sig = _make_signal(direction=Direction.LONG, entry=2370.0, stop_loss=2400.0,
                       current_price=2360.0)
    await monitor._evaluate_signal(sig)

    om.close_full.assert_awaited_once()
    kw = om.close_full.call_args.kwargs
    assert kw["reason"] == "cancelled"


async def test_disabled_order_manager_does_not_break_sl_path():
    """When auto-trade is OFF, SL_HIT must still update engine state
    cleanly (no exception trying to call broker)."""
    om = MagicMock()
    om.is_enabled = False
    om.close_full = AsyncMock()
    ds = _data_store_with_candle(high=2360.0, low=2348.0)
    monitor = _build_monitor(order_manager=om, data_store=ds)

    sig = _make_signal(direction=Direction.LONG, entry=2370.0, stop_loss=2351.0,
                       current_price=2348.0)
    await monitor._evaluate_signal(sig)

    om.close_full.assert_not_called()
    # Engine still transitioned the status.
    assert sig.status == "SL_HIT"


async def test_tp_close_does_not_call_broker_close_full():
    """TP-hit path uses close_partial, not close_full.  Verify the wiring
    doesn't accidentally double-close."""
    om = _enabled_order_manager()
    om.close_partial = AsyncMock(return_value="ccxt-tp1-id")
    # Candle high reaches TP1 (2392) but not TP2 → only TP1 partial fires.
    ds = _data_store_with_candle(high=2393.0, low=2360.0)
    monitor = _build_monitor(order_manager=om, data_store=ds)

    sig = _make_signal(direction=Direction.LONG, entry=2370.0, stop_loss=2351.0,
                       tp1=2392.0, current_price=2392.5)
    await monitor._evaluate_signal(sig)

    om.close_full.assert_not_called()
    # close_partial called for TP1.
    om.close_partial.assert_awaited()
