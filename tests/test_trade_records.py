"""Tests for the SQLite-backed per-trade ledger.

Doctrine: paper-trade visibility (2026-05-16).  This store powers the
Lumin app's per-trade history list and the ROI%-on-margin metric.  Each
test below maps to one row of the spec in the PR body so a future
review can verify coverage at a glance.

Tests use the autouse ``PAPER_TRADES_DB_PATH`` env override (added to
tests/conftest.py) so each test gets a fresh SQLite file under
``tmp_path``.  The module-level connection cache is reset between
tests so the new env var actually takes effect.
"""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _reset_conn_cache():
    """Drop the module-level connection cache before each test.

    The store caches a sqlite3.Connection per resolved path.  When the
    autouse conftest fixture rotates ``PAPER_TRADES_DB_PATH`` to a new
    tmp_path between tests, the cache would otherwise hand out the
    prior test's stale connection on first access.  Resetting before
    the test runs forces the next ``_get_conn()`` call to honour the
    fresh env override.
    """
    from src.auto_trade import trade_records
    trade_records.reset_for_test()
    yield
    trade_records.reset_for_test()


# ---------------------------------------------------------------------------
# open_trade
# ---------------------------------------------------------------------------


class TestOpenTrade:
    def test_open_creates_row_with_snapshotted_fields(self):
        from src.auto_trade import trade_records
        trade_id = trade_records.open_trade(
            signal_id="SIG-1",
            symbol="BTCUSDT",
            side="long",
            entry=30000.0,
            qty=0.01,
            leverage=10.0,
            position_size_pct=2.0,
        )
        assert trade_id is not None
        row = trade_records.get_trade("SIG-1")
        assert row is not None
        assert row["symbol"] == "BTCUSDT"
        assert row["side"] == "long"
        assert row["entry"] == pytest.approx(30000.0)
        assert row["qty"] == pytest.approx(0.01)
        assert row["leverage"] == pytest.approx(10.0)
        # notional = 30000 * 0.01 = 300, margin = 300 / 10 = 30
        assert row["notional_usd"] == pytest.approx(300.0)
        assert row["margin_usd"] == pytest.approx(30.0)
        assert row["partial_fills"] == []
        assert row["closed_at"] is None

    def test_open_is_idempotent_on_signal_id(self):
        from src.auto_trade import trade_records
        first = trade_records.open_trade(
            signal_id="SIG-2", symbol="ETHUSDT", side="short",
            entry=2000.0, qty=0.5, leverage=5.0, position_size_pct=2.0,
        )
        second = trade_records.open_trade(
            signal_id="SIG-2", symbol="ETHUSDT", side="short",
            entry=2000.0, qty=0.5, leverage=5.0, position_size_pct=2.0,
        )
        assert first == second  # same row id returned

    def test_open_rejects_degenerate_inputs(self):
        from src.auto_trade import trade_records
        # Zero qty → guard rail trip → None returned, no row created.
        assert trade_records.open_trade(
            signal_id="SIG-3", symbol="B", side="long",
            entry=100.0, qty=0.0, leverage=10.0, position_size_pct=2.0,
        ) is None
        assert trade_records.get_trade("SIG-3") is None
        # Zero entry — same.
        assert trade_records.open_trade(
            signal_id="SIG-4", symbol="B", side="long",
            entry=0.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        ) is None
        # Empty signal_id — same.
        assert trade_records.open_trade(
            signal_id="", symbol="B", side="long",
            entry=1.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        ) is None


# ---------------------------------------------------------------------------
# record_partial_fill
# ---------------------------------------------------------------------------


class TestRecordPartialFill:
    def test_partial_fill_appends_to_json_column(self):
        from src.auto_trade import trade_records
        trade_records.open_trade(
            signal_id="SIG-A", symbol="B", side="long",
            entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        )
        trade_records.record_partial_fill(
            signal_id="SIG-A", tp_level=1, fraction=0.33,
            fill_price=101.0, pnl_usd=0.33, fee_usd=0.04,
        )
        trade_records.record_partial_fill(
            signal_id="SIG-A", tp_level=2, fraction=0.33,
            fill_price=102.0, pnl_usd=0.66, fee_usd=0.04,
        )
        row = trade_records.get_trade("SIG-A")
        assert len(row["partial_fills"]) == 2
        assert row["partial_fills"][0]["tp_level"] == 1
        assert row["partial_fills"][1]["fill_price"] == pytest.approx(102.0)
        # Every fill record carries an ISO-8601 ts string.
        assert "T" in row["partial_fills"][0]["ts"]

    def test_partial_fill_noop_on_unknown_signal(self):
        """No row → no exception, just a warning log."""
        from src.auto_trade import trade_records
        trade_records.record_partial_fill(
            signal_id="DOES-NOT-EXIST", tp_level=1, fraction=0.5,
            fill_price=1.0, pnl_usd=0.0, fee_usd=0.0,
        )  # Must not raise.


# ---------------------------------------------------------------------------
# close_trade + ROI calculation
# ---------------------------------------------------------------------------


class TestCloseTrade:
    def test_close_computes_roi_on_margin(self):
        """ROI on margin = net_pnl_usd / margin_usd * 100.

        With 10x leverage and a +1% favourable move, the ROI is +10%
        even though the underlying only moved +1%.  This is the
        headline metric the dashboard surfaces.
        """
        from src.auto_trade import trade_records
        # notional = 100, margin = 100 / 10 = 10
        trade_records.open_trade(
            signal_id="SIG-C", symbol="B", side="long",
            entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        )
        row = trade_records.close_trade(
            signal_id="SIG-C",
            close_reason="tp3",
            close_price=101.0,
            gross_pnl_usd=1.0,
            fees_usd=0.06,
            net_pnl_usd=0.94,
        )
        assert row is not None
        # 0.94 / 10 * 100 = 9.4%
        assert row["roi_pct_on_margin"] == pytest.approx(9.4, rel=1e-6)
        assert row["close_reason"] == "tp3"
        assert row["closed_at"] is not None

    def test_close_is_idempotent(self):
        from src.auto_trade import trade_records
        trade_records.open_trade(
            signal_id="SIG-D", symbol="B", side="short",
            entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        )
        first = trade_records.close_trade(
            signal_id="SIG-D", close_reason="sl_hit",
            close_price=101.0, gross_pnl_usd=-1.0, fees_usd=0.06,
            net_pnl_usd=-1.06,
        )
        # Re-close — should return the same closed view, not overwrite.
        second = trade_records.close_trade(
            signal_id="SIG-D", close_reason="tp1",
            close_price=999.0, gross_pnl_usd=10.0, fees_usd=0.0,
            net_pnl_usd=10.0,
        )
        assert second["close_reason"] == first["close_reason"] == "sl_hit"
        assert second["net_pnl_usd"] == pytest.approx(-1.06)

    def test_close_returns_none_for_unknown_signal(self):
        from src.auto_trade import trade_records
        assert trade_records.close_trade(
            signal_id="GHOST", close_reason="tp1", close_price=1.0,
            gross_pnl_usd=0.0, fees_usd=0.0, net_pnl_usd=0.0,
        ) is None


# ---------------------------------------------------------------------------
# list_trades pagination + filters
# ---------------------------------------------------------------------------


class TestListTrades:
    def _seed(self, n: int, base_symbol: str = "BTCUSDT"):
        from src.auto_trade import trade_records
        for i in range(n):
            sid = f"SEED-{i:03d}"
            trade_records.open_trade(
                signal_id=sid, symbol=base_symbol if i % 2 == 0 else "ETHUSDT",
                side="long", entry=100.0 + i, qty=1.0,
                leverage=10.0, position_size_pct=2.0,
            )
            trade_records.close_trade(
                signal_id=sid, close_reason="tp1",
                close_price=101.0, gross_pnl_usd=1.0,
                fees_usd=0.05, net_pnl_usd=0.95,
            )

    def test_list_returns_closed_trades_newest_first(self):
        from src.auto_trade import trade_records
        self._seed(5)
        items = trade_records.list_trades(limit=10)
        assert len(items) == 5
        # newest-first ordering by closed_at — seeding order goes 0..4,
        # so newest (most recently closed) is SEED-004.
        assert items[0]["signal_id"] == "SEED-004"

    def test_list_pagination_offset(self):
        from src.auto_trade import trade_records
        self._seed(10)
        page1 = trade_records.list_trades(limit=3, offset=0)
        page2 = trade_records.list_trades(limit=3, offset=3)
        assert len(page1) == 3
        assert len(page2) == 3
        # No overlap
        ids = {r["signal_id"] for r in page1}
        ids.update({r["signal_id"] for r in page2})
        assert len(ids) == 6

    def test_list_filters_by_symbol(self):
        from src.auto_trade import trade_records
        self._seed(6)
        btc = trade_records.list_trades(symbol="BTCUSDT")
        eth = trade_records.list_trades(symbol="ETHUSDT")
        assert all(r["symbol"] == "BTCUSDT" for r in btc)
        assert all(r["symbol"] == "ETHUSDT" for r in eth)

    def test_list_excludes_open_by_default(self):
        from src.auto_trade import trade_records
        trade_records.open_trade(
            signal_id="OPEN-1", symbol="B", side="long",
            entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        )
        # No close — row is "open".
        closed_only = trade_records.list_trades()
        assert all(r["closed_at"] is not None for r in closed_only)
        with_open = trade_records.list_trades(include_open=True)
        assert any(r["signal_id"] == "OPEN-1" for r in with_open)

    def test_count_matches_list_total(self):
        from src.auto_trade import trade_records
        self._seed(7)
        total = trade_records.count_trades()
        assert total == 7
        # With symbol filter — count must agree with the filtered list len.
        eth_count = trade_records.count_trades(symbol="ETHUSDT")
        eth_rows = trade_records.list_trades(symbol="ETHUSDT", limit=500)
        assert eth_count == len(eth_rows)


# ---------------------------------------------------------------------------
# archive_all (used by POST /api/auto-mode/paper/reset)
# ---------------------------------------------------------------------------


class TestArchive:
    def test_archive_renames_table_and_recreates_empty(self):
        from src.auto_trade import trade_records
        trade_records.open_trade(
            signal_id="ARCH-1", symbol="B", side="long",
            entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        )
        trade_records.close_trade(
            signal_id="ARCH-1", close_reason="tp1",
            close_price=101.0, gross_pnl_usd=1.0,
            fees_usd=0.05, net_pnl_usd=0.95,
        )
        count = trade_records.archive_all()
        assert count == 1
        # Live table is empty post-archive.
        assert trade_records.count_trades() == 0
        assert trade_records.list_trades() == []
        # Archive table exists and carries the original row.
        conn = trade_records._get_conn()
        tables = [
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]
        archive_tables = [t for t in tables if t.startswith("paper_trades_archive_")]
        assert len(archive_tables) == 1
        archived_rows = conn.execute(
            f"SELECT signal_id FROM {archive_tables[0]}"
        ).fetchall()
        assert archived_rows[0][0] == "ARCH-1"

    def test_archive_noop_on_empty_table(self):
        from src.auto_trade import trade_records
        assert trade_records.archive_all() == 0
