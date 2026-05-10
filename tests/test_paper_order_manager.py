"""Tests for ``PaperOrderManager`` — Phase A1 paper-trade simulation.

Verifies the simulated-execution surface that powers Lumin's Demo mode and
our own auto-trade testing.  These tests are interface-shaped — anything
that breaks here would also break ``TradeMonitor``'s integration with the
manager.

Coverage:
* ``place_market_order`` opens an in-memory position with synthetic order ID
* Idempotent open — second call for the same signal_id is a no-op
* ``close_partial`` realises PnL and accumulates ``simulated_pnl_total``
* TP-level dedup — TP1 fired twice closes only once
* ``cancel_order`` is a no-op that returns True
* ``execute_signal`` mirrors ``place_market_order``
* SHORT-side PnL math (entry - fill) × qty
* Quantity computation respects ``MAX_POSITION_USD`` cap
* Skips when entry price is invalid / signal_id is missing
"""
from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from src.paper_order_manager import PaperOrderManager
from src.smc import Direction


def _make_signal(
    *,
    signal_id: str = "PAPER-001",
    symbol: str = "BTCUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 30000.0,
    current_price: float = 30000.0,
):
    sig = MagicMock()
    sig.signal_id = signal_id
    sig.symbol = symbol
    sig.direction = direction
    sig.entry = entry
    sig.current_price = current_price
    return sig


# ---------------------------------------------------------------------------
# Open
# ---------------------------------------------------------------------------


async def test_place_market_order_opens_long_position():
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(direction=Direction.LONG, entry=30000.0)
    order_id = await pm.place_market_order(sig)
    assert order_id is not None
    assert order_id.startswith("paper-PAPER-001-open-")
    assert pm.open_position_count == 1


async def test_place_market_order_opens_short_position():
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(direction=Direction.SHORT, entry=30000.0)
    order_id = await pm.place_market_order(sig)
    assert order_id is not None
    assert pm.open_position_count == 1


async def test_place_market_order_is_idempotent():
    """Second call for the same signal_id is a no-op (returns None)."""
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal()
    first = await pm.place_market_order(sig)
    second = await pm.place_market_order(sig)
    assert first is not None
    assert second is None
    assert pm.open_position_count == 1


async def test_place_market_order_skips_when_entry_zero():
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(entry=0.0)
    result = await pm.place_market_order(sig)
    assert result is None
    assert pm.open_position_count == 0


async def test_place_market_order_skips_when_signal_id_missing():
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(signal_id="")
    result = await pm.place_market_order(sig)
    assert result is None


async def test_quantity_capped_at_max_position_usd():
    """With huge starting equity, quantity should still cap at MAX_POSITION_USD/entry."""
    pm = PaperOrderManager(
        starting_equity_usd=1_000_000.0,
        position_size_pct=2.0,
        max_position_usd=100.0,
    )
    qty = await pm._compute_quantity(entry_price=10.0)
    # 2% of 1M = $20K, capped at $100, so $100/$10 = 10 units
    assert qty == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# Partial close + PnL
# ---------------------------------------------------------------------------


async def test_long_partial_close_realises_positive_pnl():
    """Realised PnL after Binance fees (entry taker 0.04% + TP-fill maker
    0.02%, both proportional to closed fraction).  Post-fix the engine
    deducts fees on every paper fill so paper P&L matches what live
    execution would book (owner-flagged 2026-05-10)."""
    from config import (
        BINANCE_FUTURES_MAKER_FEE_PCT,
        BINANCE_FUTURES_TAKER_FEE_PCT,
    )
    pm = PaperOrderManager(starting_equity_usd=10000.0, max_position_usd=1000.0)
    entry = 30000.0
    fill = 30300.0  # +1% favourable for long
    sig = _make_signal(direction=Direction.LONG, entry=entry, current_price=fill)
    await pm.place_market_order(sig)
    qty_before = pm._positions["PAPER-001"].quantity
    order_id = await pm.close_partial(sig, fraction=0.33, tp_level=1, current_price=fill)
    assert order_id is not None
    close_qty = qty_before * 0.33
    gross_pnl = (fill - entry) * close_qty
    entry_fee_share = (entry * qty_before) * (BINANCE_FUTURES_TAKER_FEE_PCT / 100.0) * (close_qty / qty_before)
    exit_fee = (fill * close_qty) * (BINANCE_FUTURES_MAKER_FEE_PCT / 100.0)
    expected_pnl = gross_pnl - entry_fee_share - exit_fee
    # Compare against the raw float — ``simulated_pnl_total`` rounds to 4dp
    # which masks sub-cent precision once fees enter the math.
    assert pm._realised_pnl_total == pytest.approx(expected_pnl, rel=1e-6)
    # Sanity: post-fee PnL is strictly less than gross (fees > 0).
    assert pm._realised_pnl_total < gross_pnl


async def test_short_partial_close_realises_positive_pnl_when_price_drops():
    """Symmetric SHORT case with fee accounting."""
    from config import (
        BINANCE_FUTURES_MAKER_FEE_PCT,
        BINANCE_FUTURES_TAKER_FEE_PCT,
    )
    pm = PaperOrderManager(starting_equity_usd=10000.0, max_position_usd=1000.0)
    entry = 30000.0
    fill = 29700.0  # -1% favourable for short
    sig = _make_signal(direction=Direction.SHORT, entry=entry, current_price=fill)
    await pm.place_market_order(sig)
    qty_before = pm._positions["PAPER-001"].quantity
    await pm.close_partial(sig, fraction=0.33, tp_level=1, current_price=fill)
    close_qty = qty_before * 0.33
    gross_pnl = (entry - fill) * close_qty
    entry_fee_share = (entry * qty_before) * (BINANCE_FUTURES_TAKER_FEE_PCT / 100.0) * (close_qty / qty_before)
    exit_fee = (fill * close_qty) * (BINANCE_FUTURES_MAKER_FEE_PCT / 100.0)
    expected_pnl = gross_pnl - entry_fee_share - exit_fee
    assert pm._realised_pnl_total == pytest.approx(expected_pnl, rel=1e-6)
    assert pm._realised_pnl_total < gross_pnl


async def test_partial_close_negative_pnl_when_unfavourable():
    """SL-equivalent partial close — fill below entry for long → loss."""
    pm = PaperOrderManager(starting_equity_usd=10000.0, max_position_usd=1000.0)
    sig = _make_signal(direction=Direction.LONG, entry=30000.0)
    await pm.place_market_order(sig)
    await pm.close_partial(sig, fraction=1.0, tp_level=0, current_price=29850.0)
    # Full close at -0.5%: PnL should be negative
    assert pm.simulated_pnl_total < 0


async def test_tp_level_dedup_prevents_double_close():
    """TP1 fired twice closes only once (matches OrderManager guard)."""
    pm = PaperOrderManager(starting_equity_usd=10000.0, max_position_usd=1000.0)
    sig = _make_signal()
    await pm.place_market_order(sig)
    first = await pm.close_partial(sig, fraction=0.33, tp_level=1, current_price=30300.0)
    second = await pm.close_partial(sig, fraction=0.33, tp_level=1, current_price=30300.0)
    assert first is not None
    assert second is None  # idempotent on tp_level


async def test_close_partial_no_op_without_open_position():
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(signal_id="UNTRACKED")
    result = await pm.close_partial(sig, fraction=0.5, tp_level=1)
    assert result is None
    assert pm.simulated_pnl_total == 0.0


async def test_full_close_drops_position_from_active_map():
    pm = PaperOrderManager(starting_equity_usd=10000.0, max_position_usd=1000.0)
    sig = _make_signal()
    await pm.place_market_order(sig)
    assert pm.open_position_count == 1
    # Three partials totalling 100%
    await pm.close_partial(sig, fraction=0.33, tp_level=1, current_price=30100.0)
    await pm.close_partial(sig, fraction=0.33, tp_level=2, current_price=30200.0)
    await pm.close_partial(sig, fraction=0.34, tp_level=3, current_price=30300.0)
    assert pm.open_position_count == 0


# ---------------------------------------------------------------------------
# Compatibility surface
# ---------------------------------------------------------------------------


async def test_is_enabled_is_true():
    """Paper mode is "active" by definition — TradeMonitor relies on this."""
    pm = PaperOrderManager()
    assert pm.is_enabled is True


async def test_cancel_order_is_no_op_returns_true():
    pm = PaperOrderManager()
    assert await pm.cancel_order("paper-foo", "BTCUSDT") is True


async def test_execute_signal_mirrors_place_market_order():
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal()
    order_id = await pm.execute_signal(sig)
    assert order_id is not None
    assert pm.open_position_count == 1


# ---------------------------------------------------------------------------
# Binance fee deduction (owner-flagged 2026-05-10).  Pre-fix paper P&L was
# gross; post-fix every fill includes maker/taker fees so paper output
# matches what live execution would actually book.
# ---------------------------------------------------------------------------


async def test_open_deducts_taker_fee_from_available_equity():
    """At open time the simulator pays Binance taker fee in cash — the
    fee is removed from ``_available_equity`` so the equity bookkeeping
    accounts for it."""
    from config import BINANCE_FUTURES_TAKER_FEE_PCT
    pm = PaperOrderManager(starting_equity_usd=10000.0, max_position_usd=500.0)
    sig = _make_signal(direction=Direction.LONG, entry=100.0)
    starting_equity = pm._available_equity
    await pm.place_market_order(sig)
    pos = pm._positions["PAPER-001"]
    expected_fee = (pos.entry * pos.quantity) * (BINANCE_FUTURES_TAKER_FEE_PCT / 100.0)
    assert pos.entry_fee_paid == pytest.approx(expected_fee, rel=1e-9)
    # Available equity = starting - notional - entry_fee.
    expected_equity = starting_equity - (pos.entry * pos.quantity) - expected_fee
    assert pm._available_equity == pytest.approx(expected_equity, rel=1e-9)


async def test_partial_close_pays_maker_exit_fee_plus_proportional_entry_share():
    """TP partial closes pay maker fee on the exit notional plus the
    proportional share of the entry-time taker fee."""
    from config import (
        BINANCE_FUTURES_MAKER_FEE_PCT,
        BINANCE_FUTURES_TAKER_FEE_PCT,
    )
    pm = PaperOrderManager(starting_equity_usd=10000.0, max_position_usd=500.0)
    entry = 100.0
    fill = 105.0
    sig = _make_signal(direction=Direction.LONG, entry=entry, current_price=fill)
    await pm.place_market_order(sig)
    pos = pm._positions["PAPER-001"]
    qty = pos.quantity
    fee_at_open = pos.entry_fee_paid

    await pm.close_partial(sig, fraction=0.5, tp_level=1, current_price=fill)
    close_qty = qty * 0.5
    gross_pnl = (fill - entry) * close_qty
    expected_exit_fee = (fill * close_qty) * (BINANCE_FUTURES_MAKER_FEE_PCT / 100.0)
    expected_entry_share = fee_at_open * 0.5
    expected_pnl = gross_pnl - expected_exit_fee - expected_entry_share

    assert pm._realised_pnl_total == pytest.approx(expected_pnl, rel=1e-9)


async def test_full_close_sl_reason_pays_taker_exit_fee():
    """SL/expired/invalidated/cancelled exits use stop-market or market
    orders → taker fee on the exit notional."""
    from config import BINANCE_FUTURES_TAKER_FEE_PCT
    pm = PaperOrderManager(starting_equity_usd=10000.0, max_position_usd=500.0)
    entry = 100.0
    fill = 99.0
    sig = _make_signal(direction=Direction.LONG, entry=entry)
    await pm.place_market_order(sig)
    pos = pm._positions["PAPER-001"]
    qty = pos.quantity
    fee_at_open = pos.entry_fee_paid

    await pm.close_full(sig, current_price=fill, reason="sl_hit")
    gross_pnl = (fill - entry) * qty
    expected_exit_fee = (fill * qty) * (BINANCE_FUTURES_TAKER_FEE_PCT / 100.0)
    # Full close — entry fee share is the whole entry fee.
    expected_pnl = gross_pnl - expected_exit_fee - fee_at_open

    assert pm._realised_pnl_total == pytest.approx(expected_pnl, rel=1e-9)
    # SL took us a hair below entry — gross was already negative; with
    # fees subtracted, realised is even more negative.
    assert pm._realised_pnl_total < gross_pnl


async def test_full_close_tp_reason_uses_maker_exit_fee():
    """A full close with a TP-style reason (test-style; production uses
    close_partial for TPs) uses maker fee."""
    from config import BINANCE_FUTURES_MAKER_FEE_PCT
    pm = PaperOrderManager(starting_equity_usd=10000.0, max_position_usd=500.0)
    entry = 100.0
    fill = 105.0
    sig = _make_signal(direction=Direction.LONG, entry=entry)
    await pm.place_market_order(sig)
    pos = pm._positions["PAPER-001"]
    qty = pos.quantity
    fee_at_open = pos.entry_fee_paid

    await pm.close_full(sig, current_price=fill, reason="TP1_HIT")
    gross_pnl = (fill - entry) * qty
    expected_exit_fee = (fill * qty) * (BINANCE_FUTURES_MAKER_FEE_PCT / 100.0)
    expected_pnl = gross_pnl - expected_exit_fee - fee_at_open
    assert pm._realised_pnl_total == pytest.approx(expected_pnl, rel=1e-9)


async def test_position_size_pct_reads_from_user_settings(tmp_path, monkeypatch):
    """``_compute_quantity`` resolves position size via ``user_settings`` —
    the Auto-trade page can change sizing live without an engine restart."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )
    user_settings.update_auto_trade({"position_size_pct": 4.0})  # 4% override

    pm = PaperOrderManager(
        starting_equity_usd=10000.0,
        max_position_usd=10000.0,
        # Constructor default is 2.0 — user override should win.
        position_size_pct=2.0,
    )
    sig = _make_signal(direction=Direction.LONG, entry=100.0)
    await pm.place_market_order(sig)
    pos = pm._positions["PAPER-001"]
    # Expect notional = 4% × $10000 = $400 (vs constructor 2% = $200).
    assert pos.entry * pos.quantity == pytest.approx(400.0, rel=1e-6)
