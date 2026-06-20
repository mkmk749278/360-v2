"""Per-user pnl_history namespacing + engine-wide aggregate (2026-06-20)."""
from __future__ import annotations

from datetime import date

import importlib

import pytest

ph = importlib.import_module("src.auto_trade.pnl_history")


@pytest.fixture
def hist(tmp_path, monkeypatch):
    monkeypatch.setenv("PNL_HISTORY_PATH", str(tmp_path / "pnl_history.json"))
    yield ph


def test_per_user_buckets_isolated_and_aggregated(hist):
    d = date(2026, 6, 20)
    hist.record_close("paper:1", 5.0, when=d)
    hist.record_close("paper:2", -2.0, when=d)
    hist.record_close("paper:1", 1.0, when=d)

    # Single-mode reader = one user's view.
    assert hist.get_daily("paper:1", on_date=d) == 6.0
    assert hist.get_daily("paper:2", on_date=d) == -2.0
    # Aggregate over paper:* = engine-wide.
    assert hist.get_daily_aggregate("paper", on_date=d) == 4.0


def test_aggregate_history_series(hist):
    d = date.today()
    hist.record_close("paper:1", 3.0, when=d)
    hist.record_close("paper:9", 4.0, when=d)
    series = hist.get_history_aggregate("paper", days=1)
    assert series[-1][1] == 7.0


def test_reset_aggregate_clears_all_user_buckets(hist):
    d = date(2026, 6, 20)
    hist.record_close("paper:1", 5.0, when=d)
    hist.record_close("paper:2", 9.0, when=d)
    hist.record_close("live", 100.0, when=d)
    cleared = hist.reset_aggregate("paper")
    assert cleared == 2
    assert hist.get_daily_aggregate("paper", on_date=d) == 0.0
    # Live untouched.
    assert hist.get_daily("live", on_date=d) == 100.0
