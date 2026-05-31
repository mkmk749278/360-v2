"""Tests for ``src.auto_trade.position_reconciler`` — Phase A3.

Covers the classification logic, boot reconciliation, periodic drift
checks, alerting, optional auto-close-orphans, and the inactive (no
exchange client) fail-open behaviour.
"""
from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.auto_trade.position_reconciler import (
    PositionReconciler,
    ReconcileResult,
    _ccxt_to_binance_symbol,
    _is_position_open,
    _signal_side,
    _signal_symbol,
)
from src.smc import Direction


# ---------------------------------------------------------------------------
# Helpers + fixtures
# ---------------------------------------------------------------------------


def _make_signal(*, signal_id: str, symbol: str, direction: Direction = Direction.LONG):
    sig = MagicMock()
    sig.signal_id = signal_id
    sig.symbol = symbol
    sig.direction = direction
    return sig


def _ccxt_position(
    *,
    symbol: str,
    side: str = "long",
    contracts: float = 0.01,
    entry: float = 30000.0,
    notional: float = 300.0,
    leverage: float = 10.0,
) -> Dict[str, Any]:
    """Match CCXT's fetch_positions() return shape."""
    return {
        "symbol": symbol,
        "side": side,
        "contracts": contracts,
        "entryPrice": entry,
        "notional": notional,
        "leverage": leverage,
    }


def _make_reconciler(
    *,
    positions: List[Dict[str, Any]] = None,
    active_signals: Dict[str, Any] = None,
    auto_close: bool = False,
    close_signal_fn=None,
):
    client = MagicMock()
    client.fetch_positions = AsyncMock(return_value=positions or [])
    client.create_market_order = AsyncMock(return_value={"id": "close-1"})
    alert = AsyncMock()
    rec = PositionReconciler(
        exchange_client=client,
        get_active_signals_fn=lambda: active_signals or {},
        alert_callback=alert,
        auto_close_orphans=auto_close,
        close_signal_fn=close_signal_fn,
    )
    return rec, client, alert


# ---------------------------------------------------------------------------
# Helpers tested in isolation
# ---------------------------------------------------------------------------


def test_ccxt_to_binance_symbol_strips_slash_and_settle():
    assert _ccxt_to_binance_symbol("BTC/USDT") == "BTCUSDT"
    assert _ccxt_to_binance_symbol("ETH/USDT:USDT") == "ETHUSDT"


def test_is_position_open_true_when_contracts_positive():
    assert _is_position_open({"contracts": 0.01}) is True
    assert _is_position_open({"contracts": 0.0}) is False
    assert _is_position_open({"contracts": None}) is False
    assert _is_position_open({"contracts": "0.05"}) is True


def test_signal_helpers_pull_canonical_fields():
    sig = _make_signal(signal_id="X", symbol="BTCUSDT", direction=Direction.SHORT)
    assert _signal_symbol(sig) == "BTCUSDT"
    assert _signal_side(sig) == "short"


# ---------------------------------------------------------------------------
# Active / inactive states
# ---------------------------------------------------------------------------


def test_inactive_when_no_exchange_client():
    rec = PositionReconciler(exchange_client=None)
    assert rec.is_active is False


async def test_inactive_reconciler_returns_empty_result_no_io():
    rec = PositionReconciler(exchange_client=None)
    result = await rec.reconcile_on_boot()
    assert isinstance(result, ReconcileResult)
    assert result.tracked == 0
    assert not result.has_drift


# ---------------------------------------------------------------------------
# Classification (pure)
# ---------------------------------------------------------------------------


def test_tracked_when_signal_matches_exchange_position():
    rec, _, _ = _make_reconciler()
    sig = _make_signal(signal_id="A", symbol="BTCUSDT", direction=Direction.LONG)
    pos = _ccxt_position(symbol="BTC/USDT", side="long")
    result = rec._classify([pos], {"A": sig})
    assert result.tracked == 1
    assert not result.orphan_positions
    assert not result.missing_signals


def test_orphan_when_exchange_has_position_no_signal():
    rec, _, _ = _make_reconciler()
    pos = _ccxt_position(symbol="BTC/USDT", side="long", contracts=0.5)
    result = rec._classify([pos], {})
    assert result.tracked == 0
    assert len(result.orphan_positions) == 1
    orphan = result.orphan_positions[0]
    assert orphan["symbol"] == "BTCUSDT"
    assert orphan["side"] == "long"
    assert orphan["contracts"] == 0.5


def test_missing_when_signal_open_no_exchange_position():
    rec, _, _ = _make_reconciler()
    sig = _make_signal(signal_id="A", symbol="ETHUSDT", direction=Direction.SHORT)
    result = rec._classify([], {"A": sig})
    assert result.tracked == 0
    assert not result.orphan_positions
    assert len(result.missing_signals) == 1
    assert result.missing_signals[0].signal_id == "A"


def test_classification_distinguishes_long_vs_short_on_same_symbol():
    """A LONG signal on BTC and a SHORT exchange position on BTC are NOT a match."""
    rec, _, _ = _make_reconciler()
    sig = _make_signal(signal_id="A", symbol="BTCUSDT", direction=Direction.LONG)
    pos = _ccxt_position(symbol="BTC/USDT", side="short")
    result = rec._classify([pos], {"A": sig})
    assert result.tracked == 0
    assert len(result.orphan_positions) == 1   # short on exchange — orphan
    assert len(result.missing_signals) == 1    # long signal — no exchange backing


def test_classification_filters_closed_positions_via_caller():
    """The fetch step filters contracts==0; classifier sees only open ones."""
    rec, _, _ = _make_reconciler()
    # Even if a closed position slipped through, classifier doesn't filter
    # (caller's job).  We just verify it'd be flagged as orphan.
    pos = _ccxt_position(symbol="BTC/USDT", contracts=0.0)
    result = rec._classify([pos], {})
    assert len(result.orphan_positions) == 1


# ---------------------------------------------------------------------------
# reconcile_on_boot — end-to-end
# ---------------------------------------------------------------------------


async def test_boot_reconcile_alerts_on_orphan():
    pos = _ccxt_position(symbol="BTC/USDT", side="long", contracts=0.5)
    rec, _, alert = _make_reconciler(positions=[pos])
    result = await rec.reconcile_on_boot()
    assert len(result.orphan_positions) == 1
    alert.assert_awaited_once()
    msg = alert.call_args.args[0]
    assert "Orphan positions" in msg
    assert "BTCUSDT" in msg


async def test_boot_reconcile_no_alert_when_clean():
    """No exchange positions, no signals → no alert (no drift)."""
    rec, _, alert = _make_reconciler(positions=[])
    result = await rec.reconcile_on_boot()
    assert not result.has_drift
    alert.assert_not_awaited()


async def test_boot_reconcile_filters_closed_positions():
    closed = _ccxt_position(symbol="BTC/USDT", contracts=0.0)
    open_pos = _ccxt_position(symbol="ETH/USDT", contracts=0.1)
    rec, _, _ = _make_reconciler(positions=[closed, open_pos])
    result = await rec.reconcile_on_boot()
    # Only the open ETH position should appear as orphan
    assert len(result.orphan_positions) == 1
    assert result.orphan_positions[0]["symbol"] == "ETHUSDT"


async def test_boot_reconcile_auto_close_orphans_when_enabled():
    pos1 = _ccxt_position(symbol="BTC/USDT", side="long", contracts=0.5)
    pos2 = _ccxt_position(symbol="ETH/USDT", side="short", contracts=0.2)
    rec, client, _ = _make_reconciler(positions=[pos1, pos2], auto_close=True)
    result = await rec.reconcile_on_boot()
    assert result.closed_orphans == 2
    # Verify market orders placed in opposite direction
    calls = client.create_market_order.await_args_list
    assert len(calls) == 2
    sides = sorted(c.args[1] for c in calls)
    assert sides == ["buy", "sell"]  # close long → sell, close short → buy


async def test_boot_reconcile_auto_close_off_by_default():
    pos = _ccxt_position(symbol="BTC/USDT", side="long")
    rec, client, _ = _make_reconciler(positions=[pos], auto_close=False)
    await rec.reconcile_on_boot()
    client.create_market_order.assert_not_awaited()


async def test_boot_reconcile_handles_close_failure_gracefully():
    """One close failing must not stop the reconciler from trying the next."""
    pos1 = _ccxt_position(symbol="BTC/USDT", side="long")
    pos2 = _ccxt_position(symbol="ETH/USDT", side="long")
    rec, client, _ = _make_reconciler(positions=[pos1, pos2], auto_close=True)
    # First close raises, second succeeds
    client.create_market_order = AsyncMock(
        side_effect=[RuntimeError("network blip"), {"id": "ok"}]
    )
    result = await rec.reconcile_on_boot()
    assert result.closed_orphans == 1


# ---------------------------------------------------------------------------
# periodic_drift_check
# ---------------------------------------------------------------------------


async def test_periodic_drift_alerts_only_on_drift():
    """Periodic check is silent when nothing's drifting."""
    rec, _, alert = _make_reconciler(positions=[])
    await rec.periodic_drift_check()
    alert.assert_not_awaited()


async def test_periodic_drift_alerts_on_orphan():
    pos = _ccxt_position(symbol="BTC/USDT", side="long")
    rec, _, alert = _make_reconciler(positions=[pos])
    result = await rec.periodic_drift_check()
    assert result.has_drift
    alert.assert_awaited_once()


async def test_periodic_drift_does_not_auto_close_even_when_enabled():
    """Auto-close fires only on boot, never on periodic — too risky to act
    on transient drift mid-flight."""
    pos = _ccxt_position(symbol="BTC/USDT", side="long")
    rec, client, _ = _make_reconciler(positions=[pos], auto_close=True)
    await rec.periodic_drift_check()
    client.create_market_order.assert_not_awaited()


# ---------------------------------------------------------------------------
# Resilience
# ---------------------------------------------------------------------------


async def test_fetch_positions_failure_does_not_raise():
    client = MagicMock()
    client.fetch_positions = AsyncMock(side_effect=RuntimeError("API down"))
    alert = AsyncMock()
    rec = PositionReconciler(
        exchange_client=client,
        get_active_signals_fn=lambda: {},
        alert_callback=alert,
    )
    result = await rec.reconcile_on_boot()
    # No drift surfaced (couldn't fetch), no alert
    assert isinstance(result, ReconcileResult)
    assert not result.has_drift
    alert.assert_not_awaited()


async def test_alert_callback_failure_does_not_raise():
    pos = _ccxt_position(symbol="BTC/USDT", side="long")
    client = MagicMock()
    client.fetch_positions = AsyncMock(return_value=[pos])
    alert = AsyncMock(side_effect=RuntimeError("telegram down"))
    rec = PositionReconciler(
        exchange_client=client,
        get_active_signals_fn=lambda: {},
        alert_callback=alert,
        auto_close_orphans=False,
    )
    # Must not raise even though alert fails
    result = await rec.reconcile_on_boot()
    assert len(result.orphan_positions) == 1


# ---------------------------------------------------------------------------
# Missing-signal two-cycle confirmation + close_signal_fn
# ---------------------------------------------------------------------------


async def test_missing_signal_cycle1_queued_not_closed():
    """Cycle 1: signal appears missing → queued in _pending_missing, no close yet."""
    close_fn = AsyncMock()
    sig = _make_signal(signal_id="A", symbol="ETHUSDT", direction=Direction.LONG)
    rec, _, _ = _make_reconciler(
        positions=[],
        active_signals={"A": sig},
        close_signal_fn=close_fn,
    )
    await rec.periodic_drift_check()
    close_fn.assert_not_awaited()
    assert "A" in rec._pending_missing


async def test_missing_signal_cycle2_confirmed_close_called():
    """Cycle 2: signal still missing → close_signal_fn called with correct args."""
    close_fn = AsyncMock()
    sig = _make_signal(signal_id="A", symbol="ETHUSDT", direction=Direction.LONG)
    # Simulate signals dict that always returns the signal
    active = {"A": sig}
    client = MagicMock()
    client.fetch_positions = AsyncMock(return_value=[])
    rec = PositionReconciler(
        exchange_client=client,
        get_active_signals_fn=lambda: active,
        alert_callback=AsyncMock(),
        close_signal_fn=close_fn,
    )
    # Cycle 1: queued
    await rec.periodic_drift_check()
    close_fn.assert_not_awaited()
    # Cycle 2: confirmed
    await rec.periodic_drift_check()
    close_fn.assert_awaited_once()
    call_sig, call_reason = close_fn.await_args.args
    assert call_sig is sig
    assert call_reason == "reconciler_confirmed_close"
    # Cleared from pending after confirmation
    assert "A" not in rec._pending_missing


async def test_missing_signal_cleared_if_broker_reconnects():
    """If broker position reappears between cycles, pending entry is discarded."""
    close_fn = AsyncMock()
    sig = _make_signal(signal_id="A", symbol="ETHUSDT", direction=Direction.LONG)
    active = {"A": sig}
    pos = _ccxt_position(symbol="ETH/USDT", side="long")

    positions_holder = [[]]  # mutable so we can change between cycles

    client = MagicMock()
    client.fetch_positions = AsyncMock(side_effect=lambda: positions_holder[0][:])
    rec = PositionReconciler(
        exchange_client=client,
        get_active_signals_fn=lambda: active,
        alert_callback=AsyncMock(),
        close_signal_fn=close_fn,
    )
    # Cycle 1: no broker position → queued
    await rec.periodic_drift_check()
    assert "A" in rec._pending_missing
    # Broker position reappears before cycle 2
    positions_holder[0] = [pos]
    # Cycle 2: now tracked (not missing) → pending cleared
    await rec.periodic_drift_check()
    assert "A" not in rec._pending_missing
    close_fn.assert_not_awaited()


async def test_missing_signal_no_close_fn_wired_alert_only():
    """Without close_signal_fn the reconciler only alerts — backward compat."""
    sig = _make_signal(signal_id="A", symbol="ETHUSDT")
    rec, _, alert = _make_reconciler(
        positions=[],
        active_signals={"A": sig},
    )
    # Two cycles — still no close, just alert
    await rec.periodic_drift_check()
    await rec.periodic_drift_check()
    # _pending_missing stays empty when no close_signal_fn
    assert rec._pending_missing == {}
    # Alert was called (drift detected)
    alert.assert_awaited()


async def test_close_fn_exception_does_not_propagate():
    """If close_signal_fn raises, the periodic loop must not crash."""
    close_fn = AsyncMock(side_effect=RuntimeError("engine gone"))
    sig = _make_signal(signal_id="A", symbol="ETHUSDT")
    active = {"A": sig}
    client = MagicMock()
    client.fetch_positions = AsyncMock(return_value=[])
    rec = PositionReconciler(
        exchange_client=client,
        get_active_signals_fn=lambda: active,
        alert_callback=AsyncMock(),
        close_signal_fn=close_fn,
    )
    # Prime cycle 1
    await rec.periodic_drift_check()
    # Cycle 2 — close_fn raises; must not propagate
    result = await rec.periodic_drift_check()
    assert isinstance(result, ReconcileResult)
    close_fn.assert_awaited_once()


async def test_close_fn_not_called_for_orphan_positions():
    """close_signal_fn is only for missing signals, never for orphan positions."""
    close_fn = AsyncMock()
    pos = _ccxt_position(symbol="BTC/USDT", side="long")
    rec, _, _ = _make_reconciler(
        positions=[pos],
        active_signals={},
        close_signal_fn=close_fn,
    )
    await rec.periodic_drift_check()
    await rec.periodic_drift_check()
    close_fn.assert_not_awaited()
