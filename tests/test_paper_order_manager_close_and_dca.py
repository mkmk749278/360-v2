"""Tests for ``PaperOrderManager.close_full`` and ``.add_dca_entry``.

Phase A4 alignment between engine state and broker state — without these,
non-TP closes (SL_HIT / INVALIDATED / EXPIRED / CANCELLED) leave paper
positions stranded and DCA entries don't propagate into the simulated
position book, so the engine's weighted-avg-entry math diverges from the
paper book.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from src.paper_order_manager import PaperOrderManager
from src.smc import Direction


def _make_signal(
    *,
    signal_id: str = "PAPER-DCA-001",
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
    return sig


# ---------------------------------------------------------------------------
# close_full
# ---------------------------------------------------------------------------


async def test_close_full_books_pnl_and_drops_position():
    """LONG closed at +1% should book positive realised PnL."""
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(direction=Direction.LONG, entry=2370.0)
    await pm.place_market_order(sig)
    assert pm.open_position_count == 1

    order_id = await pm.close_full(sig, reason="invalidated", current_price=2393.7)
    assert order_id is not None
    assert "close_invalidated" in order_id
    assert pm.open_position_count == 0
    assert pm.simulated_pnl_total > 0  # closed +1% above entry


async def test_close_full_short_books_pnl_when_price_below_entry():
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(direction=Direction.SHORT, entry=2370.0)
    await pm.place_market_order(sig)
    order_id = await pm.close_full(sig, reason="sl_hit", current_price=2346.3)
    assert order_id is not None
    assert pm.simulated_pnl_total > 0  # SHORT profits on price below entry


async def test_close_full_books_loss_for_long_below_entry():
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(direction=Direction.LONG, entry=2370.0)
    await pm.place_market_order(sig)
    await pm.close_full(sig, reason="invalidated", current_price=2350.0)
    assert pm.simulated_pnl_total < 0  # LONG loses on price below entry


async def test_close_full_idempotent_when_already_closed():
    """Calling on a position that's already closed is a silent no-op."""
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal()
    await pm.place_market_order(sig)
    first = await pm.close_full(sig, reason="invalidated", current_price=2380.0)
    assert first is not None
    second = await pm.close_full(sig, reason="invalidated", current_price=2380.0)
    assert second is None  # idempotent


async def test_close_full_no_op_when_no_position():
    """Signal that was never opened (e.g. risk gate refused Entry 1)."""
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal()
    result = await pm.close_full(sig, reason="invalidated", current_price=2380.0)
    assert result is None


async def test_close_full_falls_back_to_signal_stop_loss_when_no_price():
    """SL hit close where TradeMonitor doesn't pass current_price —
    we use sig.stop_loss as a sane fill price (matches engine's PnL math)."""
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(direction=Direction.LONG, entry=2370.0, stop_loss=2351.0)
    sig.current_price = 0.0  # force fallback
    await pm.place_market_order(sig)
    order_id = await pm.close_full(sig, reason="sl_hit")
    assert order_id is not None
    assert pm.simulated_pnl_total < 0  # SL hit, LONG → loss


async def test_close_full_after_partial_closes_only_closes_remainder():
    """TP1 + TP2 fired (66% closed), close_full should only close the 34%
    remainder — total realised PnL adds the remaining 34%, not 100%."""
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(direction=Direction.LONG, entry=30000.0)
    await pm.place_market_order(sig)
    await pm.close_partial(sig, fraction=0.33, tp_level=1, current_price=30450.0)
    await pm.close_partial(sig, fraction=0.33, tp_level=2, current_price=30750.0)
    pnl_after_partials = pm.simulated_pnl_total

    order_id = await pm.close_full(sig, reason="invalidated", current_price=29800.0)
    assert order_id is not None
    # Remaining 34% closed at a loss → total PnL drops below post-partial level
    assert pm.simulated_pnl_total < pnl_after_partials
    assert pm.open_position_count == 0


async def test_close_full_notifies_risk_manager():
    """Risk-manager concurrent-cap must reclaim the slot."""
    rm = MagicMock()
    rm.check.return_value = MagicMock(allowed=True, reason="", detail="")
    pm = PaperOrderManager(starting_equity_usd=10000.0, risk_manager=rm)
    sig = _make_signal()
    await pm.place_market_order(sig)
    rm.register_open.assert_called_once()

    await pm.close_full(sig, reason="invalidated", current_price=2380.0)
    rm.register_close.assert_called_once()


# ---------------------------------------------------------------------------
# add_dca_entry
# ---------------------------------------------------------------------------


async def test_add_dca_entry_updates_avg_entry_and_quantity():
    """LONG opened at 2370, DCA at 2360 with 60/40 weights → avg_entry 2366."""
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(direction=Direction.LONG, entry=2370.0, entry_2=2360.0)
    await pm.place_market_order(sig)
    qty_before = pm._positions[sig.signal_id].quantity

    order_id = await pm.add_dca_entry(sig)
    assert order_id is not None
    assert "dca" in order_id

    pos = pm._positions[sig.signal_id]
    # weight_2/weight_1 = 0.4/0.6 = 0.667 → qty grows by 67%
    assert pos.quantity == pytest.approx(qty_before * (1 + 0.4 / 0.6), rel=1e-6)
    # New avg = (2370 × qty + 2360 × 0.667 × qty) / (qty × 1.667) = 2366
    assert pos.entry == pytest.approx(2366.0, rel=1e-3)


async def test_add_dca_entry_short_uses_below_entry_dca_price():
    pm = PaperOrderManager(starting_equity_usd=100000.0)
    sig = _make_signal(direction=Direction.SHORT, entry=78240.0, entry_2=78400.0)
    await pm.place_market_order(sig)
    qty_before = pm._positions[sig.signal_id].quantity

    order_id = await pm.add_dca_entry(sig)
    assert order_id is not None
    pos = pm._positions[sig.signal_id]
    assert pos.quantity > qty_before
    # avg should be between 78240 and 78400 weighted 60/40 → 78304
    assert pos.entry == pytest.approx(78304.0, rel=1e-3)


async def test_add_dca_entry_no_op_when_no_position():
    """Engine-DCA fires but the broker has no Entry 1 (risk gate refused)."""
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(entry_2=2360.0)
    result = await pm.add_dca_entry(sig)
    assert result is None
    assert sig.signal_id not in pm._positions


async def test_add_dca_entry_blocked_by_risk_gate_at_dca_time():
    """Daily-loss kill trips between Entry 1 and DCA → DCA refused."""
    rm = MagicMock()
    rm.check.side_effect = [
        MagicMock(allowed=True, reason="", detail=""),       # Entry 1
        MagicMock(allowed=False, reason="daily_loss_kill",   # DCA
                  detail="kill switch tripped"),
    ]
    pm = PaperOrderManager(starting_equity_usd=10000.0, risk_manager=rm)
    sig = _make_signal(entry_2=2360.0)
    await pm.place_market_order(sig)
    qty_before = pm._positions[sig.signal_id].quantity

    result = await pm.add_dca_entry(sig)
    assert result is None  # blocked
    # Position untouched.
    assert pm._positions[sig.signal_id].quantity == qty_before


async def test_add_dca_entry_uses_current_price_when_entry_2_unset():
    """Defensive — if recalculate_after_dca didn't run yet but caller has
    a price, use it.  (Not the production path, but covers edge cases.)"""
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(direction=Direction.LONG, entry=2370.0, entry_2=0.0)
    await pm.place_market_order(sig)

    order_id = await pm.add_dca_entry(sig, current_price=2360.0)
    assert order_id is not None
    pos = pm._positions[sig.signal_id]
    assert pos.entry == pytest.approx(2366.0, rel=1e-3)


async def test_add_dca_entry_invalid_weights_no_op():
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(entry_2=2360.0, weight_1=0.0)  # invalid
    await pm.place_market_order(sig)
    result = await pm.add_dca_entry(sig)
    assert result is None


async def test_close_full_after_dca_closes_the_full_averaged_position():
    """End-to-end: open Entry 1 at 2370, DCA at 2360 → avg 2366, qty 1.667×.
    Invalidate → close_full closes the FULL averaged position (not just
    Entry-1's slice) at the avg-entry-based PnL.

    Math symmetry note: at price 2360, Entry-1-only loss-per-unit is 10
    while DCA'd loss-per-unit is 6 (against avg 2366); but DCA'd qty is
    1.667× larger so total losses match coincidentally.  We verify the
    DCA position is fully drained — not the absolute PnL magnitudes —
    so the test isn't fragile to that arithmetic coincidence.
    """
    pm = PaperOrderManager(starting_equity_usd=10000.0)
    sig = _make_signal(direction=Direction.LONG, entry=2370.0, entry_2=2360.0)
    await pm.place_market_order(sig)
    qty_before_dca = pm._positions[sig.signal_id].quantity
    await pm.add_dca_entry(sig)
    qty_after_dca = pm._positions[sig.signal_id].quantity
    # DCA increased size by 67% (weight_2/weight_1 = 0.4/0.6).
    assert qty_after_dca > qty_before_dca * 1.5

    await pm.close_full(sig, reason="invalidated", current_price=2360.0)
    # Position fully closed.
    assert sig.signal_id not in pm._positions
    assert pm.open_position_count == 0
    # Booked a loss (closed below avg of 2366).
    assert pm.simulated_pnl_total < 0
