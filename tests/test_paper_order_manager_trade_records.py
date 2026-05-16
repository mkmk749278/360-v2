"""Tests that PaperOrderManager calls into ``trade_records`` correctly
on every lifecycle event.

Spec (paper-trade visibility, 2026-05-16):

* ``place_market_order`` → ``trade_records.open_trade`` with leverage +
  position_size_pct snapshotted at open
* ``close_partial`` (TP1/TP2) → ``trade_records.record_partial_fill``
* ``close_partial`` (TP3 — last fraction) → record_partial_fill PLUS
  ``trade_records.close_trade`` (the trade is fully closed via TPs)
* ``close_full`` → ``trade_records.close_trade``
* ROI on margin is computed from the cumulative net PnL across all
  partial fills
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.paper_order_manager import PaperOrderManager
from src.smc import Direction


def _make_signal(
    *,
    signal_id: str = "TR-001",
    symbol: str = "BTCUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 100.0,
    current_price: float = 100.0,
):
    sig = MagicMock()
    sig.signal_id = signal_id
    sig.symbol = symbol
    sig.direction = direction
    sig.entry = entry
    sig.current_price = current_price
    return sig


class TestOpenWritesRow:
    async def test_open_creates_trade_records_row(self):
        from src.auto_trade import trade_records
        pm = PaperOrderManager(
            starting_equity_usd=10000.0, max_position_usd=1000.0
        )
        sig = _make_signal(signal_id="TR-OPEN-1")
        await pm.place_market_order(sig)
        row = trade_records.get_trade("TR-OPEN-1")
        assert row is not None
        assert row["symbol"] == "BTCUSDT"
        assert row["side"] == "long"
        assert row["closed_at"] is None

    async def test_open_snapshots_leverage_from_user_settings(
        self, monkeypatch
    ):
        from src import user_settings
        from src.auto_trade import trade_records
        # Force a known leverage value via the settings accessor — the
        # broker reads it at open time.
        monkeypatch.setattr(
            user_settings, "auto_trade_leverage_cap", lambda: 5.0
        )
        pm = PaperOrderManager(
            starting_equity_usd=10000.0, max_position_usd=1000.0
        )
        sig = _make_signal(signal_id="TR-LEV-5x")
        await pm.place_market_order(sig)
        row = trade_records.get_trade("TR-LEV-5x")
        assert row["leverage"] == pytest.approx(5.0)

    async def test_open_snapshots_position_size_pct(self, monkeypatch):
        from src import user_settings
        from src.auto_trade import trade_records
        monkeypatch.setattr(
            user_settings, "auto_trade_position_size_pct", lambda: 3.5
        )
        pm = PaperOrderManager(
            starting_equity_usd=10000.0, max_position_usd=1000.0
        )
        sig = _make_signal(signal_id="TR-PCT")
        await pm.place_market_order(sig)
        row = trade_records.get_trade("TR-PCT")
        assert row["position_size_pct"] == pytest.approx(3.5)


class TestPartialFillsAppend:
    async def test_partial_close_appends_fill(self):
        from src.auto_trade import trade_records
        pm = PaperOrderManager(
            starting_equity_usd=10000.0, max_position_usd=1000.0
        )
        sig = _make_signal(signal_id="TR-PARTIAL", entry=100.0)
        await pm.place_market_order(sig)
        await pm.close_partial(
            sig, fraction=0.33, tp_level=1, current_price=101.0,
        )
        row = trade_records.get_trade("TR-PARTIAL")
        assert len(row["partial_fills"]) == 1
        fill = row["partial_fills"][0]
        assert fill["tp_level"] == 1
        assert fill["fraction"] == pytest.approx(0.33)
        assert fill["fill_price"] == pytest.approx(101.0)

    async def test_three_partials_then_close(self):
        """Standard TP1/TP2/TP3 sequence — the row carries every fill
        and is closed when TP3 takes the last fraction."""
        from src.auto_trade import trade_records
        pm = PaperOrderManager(
            starting_equity_usd=10000.0, max_position_usd=1000.0
        )
        sig = _make_signal(signal_id="TR-FULLTP", entry=100.0)
        await pm.place_market_order(sig)
        await pm.close_partial(sig, fraction=0.33, tp_level=1, current_price=101.0)
        await pm.close_partial(sig, fraction=0.33, tp_level=2, current_price=102.0)
        await pm.close_partial(sig, fraction=0.34, tp_level=3, current_price=103.0)
        row = trade_records.get_trade("TR-FULLTP")
        assert len(row["partial_fills"]) == 3
        assert row["closed_at"] is not None
        assert row["close_reason"] == "tp3"
        # ROI on margin > 0 since every fill was favourable.
        assert row["roi_pct_on_margin"] > 0


class TestCloseFullWritesRow:
    async def test_sl_close_writes_negative_roi(self):
        from src.auto_trade import trade_records
        pm = PaperOrderManager(
            starting_equity_usd=10000.0, max_position_usd=1000.0
        )
        sig = _make_signal(signal_id="TR-SL", entry=100.0)
        sig.stop_loss = 99.0
        await pm.place_market_order(sig)
        await pm.close_full(sig, reason="sl_hit", current_price=99.0)
        row = trade_records.get_trade("TR-SL")
        assert row["close_reason"] == "sl_hit"
        assert row["closed_at"] is not None
        assert row["roi_pct_on_margin"] < 0  # loss → negative ROI


class TestRoiMathOnMargin:
    async def test_10x_leverage_1pct_move_is_10pct_roi(self, monkeypatch):
        """Headline contract: ROI on margin is leverage × underlying %.

        Notional $100 × 10x leverage means $10 of margin.  A +$1
        net PnL on the trade is +10% ROI on the user's $10 of
        risk-capital.  This is the metric subscribers care about.

        Approximation note: paper fees subtract ~$0.06 from the gross
        $1 PnL at this notional, so we tolerate a small relative
        delta below the ideal +10%.  Fees are real — the dashboard
        shows the fee-net number.
        """
        from src import user_settings
        from src.auto_trade import trade_records
        monkeypatch.setattr(
            user_settings, "auto_trade_leverage_cap", lambda: 10.0
        )
        pm = PaperOrderManager(
            starting_equity_usd=10000.0, max_position_usd=100.0
        )
        sig = _make_signal(
            signal_id="TR-ROI-10X", entry=100.0, current_price=101.0,
        )
        await pm.place_market_order(sig)
        # Full close at +1% — close_full uses taker exit fee.
        await pm.close_full(sig, reason="tp_full", current_price=101.0)
        row = trade_records.get_trade("TR-ROI-10X")
        # Margin = $100 / 10 = $10.  Gross PnL ~ $1.  Net after maker
        # exit + taker entry fees roughly $0.93 → ROI ~ 9.3%.
        assert 8.0 < row["roi_pct_on_margin"] < 10.1


class TestFailureIsolation:
    async def test_trade_records_failure_does_not_break_open(
        self, monkeypatch
    ):
        """A SQLite IO failure inside ``trade_records.open_trade`` must
        not propagate up and break the simulated fill — the broker
        state must remain consistent so the engine's lifecycle keeps
        working even when the visibility layer is down."""
        from src.auto_trade import trade_records
        monkeypatch.setattr(
            trade_records, "open_trade", MagicMock(side_effect=RuntimeError("boom"))
        )
        pm = PaperOrderManager(
            starting_equity_usd=10000.0, max_position_usd=1000.0
        )
        sig = _make_signal(signal_id="TR-FAIL")
        # Must not raise.
        oid = await pm.place_market_order(sig)
        assert oid is not None  # broker still opened the position
        assert pm.open_position_count == 1
