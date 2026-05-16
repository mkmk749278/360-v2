"""Tests for the quantity-zero guard rails in PaperOrderManager.

Owner reported (2026-05-16) seeing paper trades with quantity == 0 in
pnl_history, making per-trade PnL meaningless.  Root causes that the
guard rails close off:

* ``_available_equity`` depleted (zero / negative / NaN) → ``_compute_quantity``
  returns 0
* User-set ``position_size_pct`` is 0 (somehow persisted as 0 via the
  settings API) → ``_compute_quantity`` returns 0
* Entry price ≤ 0 or NaN — caught earlier in ``place_market_order``
* Notional below ``_MIN_PAPER_NOTIONAL_USD`` (e.g. tiny remaining equity
  after several losses) → skip rather than open a meaningless row

Each path must emit a ``paper_trade_skip`` marker and return ``None``
from ``place_market_order`` so no degenerate row lands in the per-trade
ledger or the paper history JSON.
"""
from __future__ import annotations

import math
from unittest.mock import MagicMock

import pytest

from src.paper_order_manager import (
    PaperOrderManager,
    _MIN_PAPER_NOTIONAL_USD,
)
from src.smc import Direction


def _make_signal(
    *,
    signal_id: str = "QGUARD-001",
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
# _compute_quantity returns 0 on every degenerate path
# ---------------------------------------------------------------------------


class TestComputeQuantityGuards:
    async def test_zero_entry_returns_zero(self):
        pm = PaperOrderManager(starting_equity_usd=10000.0)
        assert await pm._compute_quantity(0.0) == 0.0

    async def test_negative_entry_returns_zero(self):
        pm = PaperOrderManager(starting_equity_usd=10000.0)
        assert await pm._compute_quantity(-100.0) == 0.0

    async def test_nan_entry_returns_zero(self):
        pm = PaperOrderManager(starting_equity_usd=10000.0)
        assert await pm._compute_quantity(float("nan")) == 0.0

    async def test_depleted_equity_returns_zero(self):
        """Owner's reported scenario: a losing streak depletes paper
        equity below zero, the next signal should NOT open a position."""
        pm = PaperOrderManager(starting_equity_usd=10000.0)
        pm._available_equity = -50.0  # post-loss drawdown into negative
        assert await pm._compute_quantity(100.0) == 0.0

    async def test_zero_position_size_pct_returns_zero(self, monkeypatch):
        from src import user_settings
        # Persist a zero override via the settings store (defensive — the
        # API layer Pydantic clamp uses gt=0 so this is theoretical, but
        # an admin could still hand-edit the JSON file).
        monkeypatch.setattr(
            user_settings, "_STORE",
            user_settings._Store(path=None),
        )
        monkeypatch.setattr(
            user_settings, "auto_trade_position_size_pct", lambda: 0.0
        )
        pm = PaperOrderManager(starting_equity_usd=10000.0)
        assert await pm._compute_quantity(100.0) == 0.0


# ---------------------------------------------------------------------------
# place_market_order skips on every degenerate path
# ---------------------------------------------------------------------------


class TestPlaceMarketOrderGuards:
    async def test_skip_when_entry_is_zero(self):
        pm = PaperOrderManager(starting_equity_usd=10000.0)
        sig = _make_signal(entry=0.0)
        assert await pm.place_market_order(sig) is None
        assert pm.open_position_count == 0

    async def test_skip_when_equity_depleted(self):
        pm = PaperOrderManager(starting_equity_usd=10000.0)
        pm._available_equity = -50.0
        sig = _make_signal()
        assert await pm.place_market_order(sig) is None
        assert pm.open_position_count == 0

    async def test_skip_when_notional_below_floor(self, monkeypatch):
        """Sub-$1 notional → skip.  Forces the path by configuring a
        tiny position_size_pct against a tiny equity."""
        from src import user_settings
        monkeypatch.setattr(
            user_settings, "auto_trade_position_size_pct", lambda: 0.001
        )
        # 0.001% of $10 = $0.0001 notional — way below the floor.
        pm = PaperOrderManager(
            starting_equity_usd=10.0, max_position_usd=10.0
        )
        sig = _make_signal(entry=100.0)
        assert await pm.place_market_order(sig) is None
        assert pm.open_position_count == 0

    async def test_guard_does_not_emit_trade_records_row(self):
        """When the guard rail trips, the per-trade SQLite ledger must
        not see an ``open_trade`` call — owner's bug was rows with
        qty=0 ending up in the dashboard list."""
        from src.auto_trade import trade_records
        pm = PaperOrderManager(starting_equity_usd=10000.0)
        pm._available_equity = -1.0  # depleted
        sig = _make_signal(signal_id="QGUARD-NOROW")
        await pm.place_market_order(sig)
        assert trade_records.get_trade("QGUARD-NOROW") is None

    async def test_legitimate_open_still_works(self):
        """Sanity: a normal open should NOT be tripped by the guards."""
        pm = PaperOrderManager(
            starting_equity_usd=10000.0, max_position_usd=1000.0
        )
        sig = _make_signal()
        oid = await pm.place_market_order(sig)
        assert oid is not None
        assert pm.open_position_count == 1


# ---------------------------------------------------------------------------
# Min-notional floor is environment-overridable via the module constant
# ---------------------------------------------------------------------------


def test_min_paper_notional_is_one_dollar_by_default():
    """The $1 notional floor is the documented default.  Tightening it
    too aggressively would skip legitimate small trades; loosening it
    too far defeats the guard's purpose."""
    assert _MIN_PAPER_NOTIONAL_USD == pytest.approx(1.0)
