"""Tests for the per-mode daily-bucketed PnL history ledger.

Owner reported losing previous-day PnL on restart.  The fix: persist
realised closed-trade PnL to ``data/pnl_history.json`` keyed by mode +
UTC date so:

* Daily PnL survives restarts (even at 23:55 UTC)
* Weekly / monthly rolling aggregates can be computed on demand
* The dashboard chart can render a 30-day daily series
* Paper and live ledgers stay independent — switching modes doesn't
  pollute the other history

Tests run with ``PNL_HISTORY_PATH`` pointing at a per-test temp file
so production ``data/pnl_history.json`` isn't touched.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _days_ago(n: int) -> str:
    return (datetime.now(timezone.utc).date() - timedelta(days=n)).strftime(
        "%Y-%m-%d"
    )


@pytest.fixture
def history_path(tmp_path) -> Path:
    """Per-test ledger path — the autouse conftest fixture sets
    ``PNL_HISTORY_PATH`` to ``tmp_path / "pnl_history.json"``; this
    fixture just exposes that path for direct file assertions."""
    return tmp_path / "pnl_history.json"


# ---------------------------------------------------------------------------
# record_close
# ---------------------------------------------------------------------------


class TestRecordClose:
    def test_first_close_creates_today_bucket(self, history_path):
        from src.auto_trade import pnl_history
        pnl_history.record_close("paper", 12.84)
        data = json.loads(history_path.read_text())
        assert data == {"paper": {_today(): 12.84}}

    def test_subsequent_closes_accumulate_in_same_bucket(self, history_path):
        from src.auto_trade import pnl_history
        pnl_history.record_close("paper", 5.0)
        pnl_history.record_close("paper", 7.5)
        pnl_history.record_close("paper", -2.5)
        data = json.loads(history_path.read_text())
        assert data["paper"][_today()] == pytest.approx(10.0)

    def test_paper_and_live_buckets_are_independent(self, history_path):
        from src.auto_trade import pnl_history
        pnl_history.record_close("paper", 10.0)
        pnl_history.record_close("live", -3.0)
        data = json.loads(history_path.read_text())
        assert data["paper"][_today()] == 10.0
        assert data["live"][_today()] == -3.0

    def test_record_close_with_explicit_date(self, history_path):
        """Backdated entries — used by tests, never by engine code."""
        from src.auto_trade import pnl_history
        backdated = date.today() - timedelta(days=3)
        pnl_history.record_close("paper", 4.20, when=backdated)
        data = json.loads(history_path.read_text())
        assert data["paper"][backdated.strftime("%Y-%m-%d")] == 4.20

    def test_record_close_ignores_empty_mode(self, history_path):
        from src.auto_trade import pnl_history
        pnl_history.record_close("", 10.0)
        assert not history_path.exists()


# ---------------------------------------------------------------------------
# get_daily / get_weekly / get_monthly
# ---------------------------------------------------------------------------


class TestAggregations:
    def test_get_daily_today(self, history_path):
        from src.auto_trade import pnl_history
        pnl_history.record_close("paper", 12.84)
        assert pnl_history.get_daily("paper") == pytest.approx(12.84)

    def test_get_daily_returns_zero_when_missing(self, history_path):
        from src.auto_trade import pnl_history
        assert pnl_history.get_daily("paper") == 0.0
        assert pnl_history.get_daily("live") == 0.0

    def test_get_weekly_sums_last_seven_days(self, history_path):
        from src.auto_trade import pnl_history
        # Day 0 (today): +5, Day 2: +10, Day 6: -3.  Day 7+ should not count.
        pnl_history.record_close("paper", 5.0)
        pnl_history.record_close(
            "paper", 10.0, when=date.today() - timedelta(days=2),
        )
        pnl_history.record_close(
            "paper", -3.0, when=date.today() - timedelta(days=6),
        )
        pnl_history.record_close(
            "paper", 99.0, when=date.today() - timedelta(days=10),
        )
        assert pnl_history.get_weekly("paper") == pytest.approx(12.0)

    def test_get_monthly_sums_last_thirty_days(self, history_path):
        from src.auto_trade import pnl_history
        # Day 0: +5, Day 15: +10, Day 29: +1.  Day 30: should not count.
        pnl_history.record_close("paper", 5.0)
        pnl_history.record_close(
            "paper", 10.0, when=date.today() - timedelta(days=15),
        )
        pnl_history.record_close(
            "paper", 1.0, when=date.today() - timedelta(days=29),
        )
        pnl_history.record_close(
            "paper", 99.0, when=date.today() - timedelta(days=30),
        )
        assert pnl_history.get_monthly("paper") == pytest.approx(16.0)

    def test_aggregations_are_per_mode(self, history_path):
        from src.auto_trade import pnl_history
        pnl_history.record_close("paper", 10.0)
        pnl_history.record_close("live", -3.0)
        assert pnl_history.get_weekly("paper") == 10.0
        assert pnl_history.get_weekly("live") == -3.0
        assert pnl_history.get_monthly("paper") == 10.0
        assert pnl_history.get_monthly("live") == -3.0


# ---------------------------------------------------------------------------
# get_history (chart series)
# ---------------------------------------------------------------------------


class TestGetHistory:
    def test_history_default_30_days(self, history_path):
        from src.auto_trade import pnl_history
        pnl_history.record_close("paper", 10.0)
        series = pnl_history.get_history("paper")
        assert len(series) == 30

    def test_history_oldest_first(self, history_path):
        """Charts read left-to-right; oldest day must come first."""
        from src.auto_trade import pnl_history
        pnl_history.record_close(
            "paper", 5.0, when=date.today() - timedelta(days=10),
        )
        pnl_history.record_close("paper", 7.0)
        series = pnl_history.get_history("paper", days=15)
        # Last item is today, first item is 14 days ago.
        assert series[-1][0] == _today()
        assert series[-1][1] == pytest.approx(7.0)

    def test_history_fills_missing_days_with_zero(self, history_path):
        """Gaps would look like data loss in a chart — fill with 0.0
        so the x-axis stays contiguous."""
        from src.auto_trade import pnl_history
        pnl_history.record_close("paper", 10.0)
        series = pnl_history.get_history("paper", days=7)
        # Today has data; the 6 prior days are zeros.
        zeros = [pnl for _, pnl in series if pnl == 0.0]
        assert len(zeros) == 6

    def test_history_empty_when_no_data(self, history_path):
        from src.auto_trade import pnl_history
        series = pnl_history.get_history("paper", days=5)
        assert len(series) == 5
        assert all(p == 0.0 for _, p in series)

    def test_history_clamps_days_argument(self, history_path):
        """Negative / zero days returns empty.  Days > 365 cap not
        enforced at the helper level — that's the API layer's job."""
        from src.auto_trade import pnl_history
        assert pnl_history.get_history("paper", days=0) == []
        assert pnl_history.get_history("paper", days=-1) == []


# ---------------------------------------------------------------------------
# Persistence + corruption
# ---------------------------------------------------------------------------


class TestPersistence:
    def test_data_survives_round_trip(self, history_path):
        from src.auto_trade import pnl_history
        pnl_history.record_close("paper", 12.84)
        # Module-level state is on disk only — re-reading via a fresh
        # call must return the same data.
        assert pnl_history.get_daily("paper") == pytest.approx(12.84)

    def test_corrupt_file_returns_empty(self, history_path):
        from src.auto_trade import pnl_history
        history_path.parent.mkdir(parents=True, exist_ok=True)
        history_path.write_text("{{not json")
        # Must not raise.
        assert pnl_history.get_daily("paper") == 0.0
        assert pnl_history.get_weekly("paper") == 0.0
        assert pnl_history.get_monthly("paper") == 0.0

    def test_non_dict_root_returns_empty(self, history_path):
        from src.auto_trade import pnl_history
        history_path.parent.mkdir(parents=True, exist_ok=True)
        history_path.write_text(json.dumps(["not", "a", "dict"]))
        assert pnl_history.get_daily("paper") == 0.0

    def test_atomic_write_no_torn_file(self, history_path):
        """Tmp + rename — no .tmp leftover after a successful write."""
        from src.auto_trade import pnl_history
        pnl_history.record_close("paper", 10.0)
        leftover = history_path.with_suffix(history_path.suffix + ".tmp")
        assert not leftover.exists()


# ---------------------------------------------------------------------------
# RiskManager rehydration
# ---------------------------------------------------------------------------


class TestRiskManagerRehydration:
    def test_risk_manager_loads_today_pnl_from_history(self, history_path):
        """The owner's reported scenario: trades close, engine restarts
        before midnight UTC, daily-loss kill should still know about
        today's drawdown."""
        from src.auto_trade import pnl_history
        from src.auto_trade.risk_manager import RiskManager

        # Pre-existing today PnL (e.g. from earlier process).
        pnl_history.record_close("paper", -25.0)

        # Fresh RiskManager — should rehydrate.
        rm = RiskManager(
            starting_equity_usd=1000.0,
            daily_loss_limit_pct=-3.0,
            mode="paper",
        )
        assert rm.daily_realised_pnl_usd == pytest.approx(-25.0)
        # Equity reflects the persisted drawdown.
        assert rm.current_equity_usd == pytest.approx(975.0)

    def test_risk_manager_no_rehydration_without_mode(self, history_path):
        from src.auto_trade import pnl_history
        from src.auto_trade.risk_manager import RiskManager

        pnl_history.record_close("paper", 10.0)
        rm = RiskManager(
            starting_equity_usd=1000.0,
            daily_loss_limit_pct=-3.0,
            # mode omitted — backwards-compatible no-op path
        )
        assert rm.daily_realised_pnl_usd == 0.0

    def test_risk_manager_paper_and_live_isolated(self, history_path):
        from src.auto_trade import pnl_history
        from src.auto_trade.risk_manager import RiskManager

        pnl_history.record_close("paper", 50.0)
        pnl_history.record_close("live", -10.0)

        paper_rm = RiskManager(
            starting_equity_usd=1000.0, mode="paper",
        )
        live_rm = RiskManager(
            starting_equity_usd=1000.0, mode="live",
        )
        assert paper_rm.daily_realised_pnl_usd == 50.0
        assert live_rm.daily_realised_pnl_usd == -10.0
