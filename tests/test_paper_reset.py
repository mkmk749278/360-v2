"""Tests for the paper-mode reset path (paper-trade visibility, 2026-05-16).

Spec: ``POST /api/auto-mode/paper/reset`` must:

* zero ``PaperOrderManager._realised_pnl_total`` and
  ``_available_equity`` back to ``_starting_equity``
* wipe the on-disk ``paper_pnl_state.json`` ledger so a restart doesn't
  re-load the prior drawdown
* clear every paper daily bucket in ``pnl_history`` (live buckets are
  untouched — paper reset must not affect live state)
* archive every per-trade row to a timestamped table (preserves history
  for ad-hoc owner queries)

These tests exercise the broker + helpers directly so they remain valid
even if the HTTP layer is rewired.  The API-level happy path is in
``tests/test_api_trades.py``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


class TestPaperOrderManagerResetState:
    def test_reset_zeros_pnl_total(self):
        from src.paper_order_manager import PaperOrderManager
        pm = PaperOrderManager(starting_equity_usd=1000.0)
        pm._realised_pnl_total = 42.0
        pm._available_equity = 1042.0
        pm.reset_state()
        assert pm._realised_pnl_total == 0.0
        assert pm._available_equity == pytest.approx(1000.0)

    def test_reset_persists_zero_to_ledger(self, tmp_path, monkeypatch):
        """Round-trip: reset → re-instantiate → see the persisted zero."""
        from src.paper_order_manager import PaperOrderManager
        # The conftest fixture already points PAPER_PNL_STATE_PATH at
        # tmp_path — this test just exercises the round-trip.
        pm = PaperOrderManager(starting_equity_usd=1000.0)
        pm._realised_pnl_total = 99.0
        # Manually persist so the ledger has content to wipe.
        from src.paper_order_manager import _persist_paper_pnl_state
        _persist_paper_pnl_state(99.0)
        # Reset wipes.
        pm.reset_state()
        # Reload from disk: a fresh broker should start at starting_equity.
        pm2 = PaperOrderManager(starting_equity_usd=1000.0)
        assert pm2._realised_pnl_total == 0.0
        assert pm2._available_equity == pytest.approx(1000.0)


class TestPnlHistoryResetMode:
    def test_reset_clears_only_target_mode(self):
        """Owner reset of paper mode must not touch live history."""
        from src.auto_trade import pnl_history
        pnl_history.record_close("paper", 10.0)
        pnl_history.record_close("live", -5.0)
        cleared = pnl_history.reset_mode("paper")
        assert cleared >= 1
        assert pnl_history.get_daily("paper") == 0.0
        # Live untouched.
        assert pnl_history.get_daily("live") == pytest.approx(-5.0)

    def test_reset_returns_bucket_count(self):
        from src.auto_trade import pnl_history
        from datetime import date, timedelta
        # Seed three days of buckets for the paper mode.
        pnl_history.record_close("paper", 1.0)
        pnl_history.record_close(
            "paper", 2.0, when=date.today() - timedelta(days=1)
        )
        pnl_history.record_close(
            "paper", 3.0, when=date.today() - timedelta(days=2)
        )
        cleared = pnl_history.reset_mode("paper")
        assert cleared == 3

    def test_reset_empty_mode_returns_zero(self):
        from src.auto_trade import pnl_history
        assert pnl_history.reset_mode("paper") == 0
        assert pnl_history.reset_mode("") == 0


class TestArchiveOnReset:
    def test_archive_preserves_rows_in_timestamped_table(self):
        from src.auto_trade import trade_records
        trade_records.open_trade(
            signal_id="ARC-1", symbol="B", side="long",
            entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        )
        trade_records.close_trade(
            signal_id="ARC-1", close_reason="sl_hit",
            close_price=99.0, gross_pnl_usd=-1.0,
            fees_usd=0.05, net_pnl_usd=-1.05,
        )
        moved = trade_records.archive_all()
        assert moved == 1
        # Re-open after reset works.
        new_id = trade_records.open_trade(
            signal_id="ARC-2", symbol="B", side="long",
            entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        )
        assert new_id is not None
        # Archive row remains queryable via SQLite directly.
        conn = trade_records._get_conn()
        archives = [
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name LIKE 'paper_trades_archive_%'"
            ).fetchall()
        ]
        assert len(archives) == 1


class TestEquityPersistenceRegression:
    """Smoke test for the owner-flagged "equity resets daily" bug
    (paper-trade visibility, 2026-05-16).

    Root cause: ``RiskManager.current_equity_usd = starting_equity +
    daily_realised_pnl_usd`` (today's bucket only).  ``snapshot.build_auto_mode``
    now prefers the broker's true cumulative ``PaperOrderManager.current_equity_usd``
    when in paper mode.  This test pins that contract on the broker
    side; the API-layer override is covered by ``test_api_trades``.
    """

    def test_broker_equity_is_cumulative_not_daily(self, monkeypatch):
        """A persisted PnL must surface as broker.current_equity_usd."""
        from src.paper_order_manager import _persist_paper_pnl_state
        from src.paper_order_manager import PaperOrderManager
        # Seed a prior session's cumulative PnL.
        _persist_paper_pnl_state(75.0)
        pm = PaperOrderManager(starting_equity_usd=1000.0)
        # broker.current_equity_usd = 1000 + 75 = 1075, regardless of
        # what daily bucket contains.
        assert pm.current_equity_usd == pytest.approx(1075.0)


class TestRiskManagerResetDailyOnPaperReset:
    """Regression for "Paper PnL Today persists after reset" (2026-05-19).

    The Trade tab's ``daily_pnl_usd`` reads from
    ``RiskManager.daily_realised_pnl_usd`` via ``engine.get_auto_execution_status``.
    Pre-fix, the paper reset endpoint cleared the PaperOrderManager + on-disk
    pnl_history but the RiskManager kept yesterday's number until UTC
    midnight, so the dashboard read stale.  Post-fix, the endpoint also
    calls ``rm.reset_daily()``.
    """

    def test_reset_daily_zeros_pnl_and_clears_kill(self):
        from src.auto_trade.risk_manager import RiskManager

        rm = RiskManager(starting_equity_usd=1000.0)
        # Simulate a losing day big enough to also trip the kill.
        from unittest.mock import MagicMock
        sig = MagicMock()
        sig.signal_id = "TEST"
        sig.symbol = "BTCUSDT"
        rm.register_open(sig)
        rm.register_close(sig, realised_pnl_usd=-40.0)
        # Force a check so the daily-loss kill flag flips sticky.
        rm.check(sig, leverage=1.0)
        assert rm.daily_realised_pnl_usd == -40.0
        assert rm.daily_kill_tripped is True
        assert rm.current_equity_usd == pytest.approx(960.0)

        rm.reset_daily()

        assert rm.daily_realised_pnl_usd == 0.0
        assert rm.daily_kill_tripped is False
        assert rm.current_equity_usd == pytest.approx(1000.0)
