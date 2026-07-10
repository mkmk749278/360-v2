"""TradeMonitor._publish_pricing_freshness — the F-07 detector's data source.

The publisher turns the trade monitor's own staleness view (candle age +
mark-feed availability) into ``data/pricing_freshness.json`` for the
watchdog and the hourly liveness probe. These tests pin the contract those
consumers parse: the ``blind`` flag, the not-yet-filled exclusion, the
throttle, and the never-raise guarantee.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from src.execution import mark_price_feed as _mpf
from src.trade_monitor import TradeMonitor


@pytest.fixture
def no_mark_feed():
    """No mark-price feed price for any symbol — the blind half of F-07."""
    prev = _mpf.get_instance()
    feed = MagicMock()
    feed.get_price.return_value = None
    _mpf.set_instance(feed)
    try:
        yield feed
    finally:
        _mpf.set_instance(prev)  # type: ignore[arg-type]


@pytest.fixture
def fresh_mark_feed():
    prev = _mpf.get_instance()
    feed = MagicMock()
    feed.get_price.return_value = 1.23
    _mpf.set_instance(feed)
    try:
        yield feed
    finally:
        _mpf.set_instance(prev)  # type: ignore[arg-type]


def _monitor(tmp_path, age_seconds):
    data_store = MagicMock()
    data_store.get_candles.return_value = {
        "high": [1.0], "low": [1.0], "close": [1.0], "open": [1.0], "volume": [1.0],
    }
    data_store.last_kline_age_seconds.return_value = age_seconds
    data_store.ticks = {}
    monitor = TradeMonitor(
        data_store=data_store,
        send_telegram=MagicMock(),
        get_active_signals=lambda: {},
        remove_signal=MagicMock(),
        update_signal=MagicMock(),
    )
    monitor._PRICING_FRESHNESS_PATH = str(tmp_path / "pricing_freshness.json")
    return monitor


def _signal(signal_id="s1", symbol="MVLLUSDT", status="TP1_HIT", never_filled=False):
    sig = MagicMock()
    sig.signal_id = signal_id
    sig.symbol = symbol
    sig.status = status
    sig.entry_never_filled = never_filled
    return sig


def _read(tmp_path):
    with open(tmp_path / "pricing_freshness.json") as fh:
        return json.load(fh)


def test_blind_position_flagged(tmp_path, no_mark_feed):
    # Stale candle (11h, the MVLLUSDT case) + nothing on the mark feed.
    monitor = _monitor(tmp_path, age_seconds=40_000.0)
    monitor._publish_pricing_freshness({"s1": _signal()})
    snap = _read(tmp_path)
    assert snap["positions"][0]["blind"] is True
    assert snap["positions"][0]["symbol"] == "MVLLUSDT"
    assert snap["positions"][0]["candle_stale"] is True
    assert snap["positions"][0]["mark_price_available"] is False


def test_stale_candle_with_mark_fallback_is_not_blind(tmp_path, fresh_mark_feed):
    # The #706 fallback still has a price → degraded but protected.
    monitor = _monitor(tmp_path, age_seconds=40_000.0)
    monitor._publish_pricing_freshness({"s1": _signal()})
    pos = _read(tmp_path)["positions"][0]
    assert pos["candle_stale"] is True
    assert pos["blind"] is False


def test_fresh_candle_is_not_blind(tmp_path, no_mark_feed):
    monitor = _monitor(tmp_path, age_seconds=5.0)
    monitor._publish_pricing_freshness({"s1": _signal()})
    pos = _read(tmp_path)["positions"][0]
    assert pos["candle_stale"] is False
    assert pos["blind"] is False


def test_unfilled_signal_excluded(tmp_path, no_mark_feed):
    # No capital priced off the symbol yet — never an invariant breach.
    monitor = _monitor(tmp_path, age_seconds=40_000.0)
    monitor._publish_pricing_freshness(
        {"s1": _signal(never_filled=True), "s2": _signal(signal_id="s2")}
    )
    snap = _read(tmp_path)
    assert [p["signal_id"] for p in snap["positions"]] == ["s2"]


def test_publish_is_throttled(tmp_path, no_mark_feed):
    monitor = _monitor(tmp_path, age_seconds=5.0)
    monitor._publish_pricing_freshness({"s1": _signal()})
    first = _read(tmp_path)["updated_at"]
    # Immediately again → inside PRICING_FRESHNESS_PUBLISH_SEC, no rewrite.
    monitor._publish_pricing_freshness({"s1": _signal()})
    assert _read(tmp_path)["updated_at"] == first


def test_publish_failure_never_raises(tmp_path, no_mark_feed):
    monitor = _monitor(tmp_path, age_seconds=5.0)
    # Unwritable target — publisher must swallow it (backstop loop safety).
    monitor._PRICING_FRESHNESS_PATH = "/proc/definitely/not/writable.json"
    monitor._publish_pricing_freshness({"s1": _signal()})
