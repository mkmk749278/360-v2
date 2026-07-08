"""Mark-feed freshness guard: the monitor must not price a signal off a frozen
1m candle once its symbol drops out of the scan universe.

Regression for the CAPUSDT SHORT case — a surge-promoted MOVER whose 1m candle
in the store went stale near entry, silently freezing sig.current_price, pnl_pct,
MFE (stored +0.05% while the pair had actually run +3.24%) and the SL/TP backstop.
``_latest_price`` returned the stale-but-non-None close, so the pre-existing
mark-feed fallback (which only fired on ``None``) never engaged.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.execution import mark_price_feed as _mpf
from src.trade_monitor import TradeMonitor

_SYMBOL = "CAPUSDT"
_STALE_CLOSE = 0.020360   # frozen near entry
_FRESH_MARK = 0.020040    # true market, ~1.6% below entry for the SHORT


@pytest.fixture
def mark_feed():
    """Install a mark-price feed singleton with one fresh price; restore after."""
    prev = _mpf.get_instance()
    feed = MagicMock()
    feed.get_price.side_effect = lambda s: _FRESH_MARK if s == _SYMBOL else None
    _mpf.set_instance(feed)
    try:
        yield feed
    finally:
        _mpf.set_instance(prev)  # type: ignore[arg-type]


def _monitor(age_seconds, candle_close=_STALE_CLOSE):
    data_store = MagicMock()
    data_store.get_candles.return_value = {
        "high": [candle_close],
        "low": [candle_close],
        "close": [candle_close],
        "open": [candle_close],
        "volume": [1000.0],
    }
    data_store.last_kline_age_seconds.return_value = age_seconds
    data_store.ticks = {}
    return TradeMonitor(
        data_store=data_store,
        send_telegram=MagicMock(),
        get_active_signals=lambda: {},
        remove_signal=MagicMock(),
        update_signal=MagicMock(),
    )


def test_latest_price_diverts_to_mark_feed_when_candle_stale(mark_feed):
    # 3h-old kline, well past the 120s default bound → use the fresh mark.
    monitor = _monitor(age_seconds=10800.0)
    assert monitor._latest_price(_SYMBOL) == pytest.approx(_FRESH_MARK)


def test_latest_price_uses_candle_when_fresh(mark_feed):
    # Kline updated 5s ago → healthy pair, never repriced off a second source.
    monitor = _monitor(age_seconds=5.0)
    assert monitor._latest_price(_SYMBOL) == pytest.approx(_STALE_CLOSE)


def test_latest_price_treats_unstamped_kline_as_fresh(mark_feed):
    # age is None (seed-loaded, pre-first-WS-frame) — mirror the scanner's
    # dispatch gate and DO NOT divert, or every symbol repriced post-boot.
    monitor = _monitor(age_seconds=None)
    assert monitor._latest_price(_SYMBOL) == pytest.approx(_STALE_CLOSE)


def test_candle_extremes_use_mark_price_when_stale(mark_feed):
    # Stale kline → SL/TP must evaluate against the fresh mark (high=low=mark),
    # not the frozen candle high/low.
    monitor = _monitor(age_seconds=10800.0)
    high, low = monitor._candle_extremes(_SYMBOL)
    assert high == pytest.approx(_FRESH_MARK)
    assert low == pytest.approx(_FRESH_MARK)


def test_candle_extremes_use_stored_range_when_fresh(mark_feed):
    monitor = _monitor(age_seconds=5.0)
    high, low = monitor._candle_extremes(_SYMBOL)
    assert high == pytest.approx(_STALE_CLOSE)
    assert low == pytest.approx(_STALE_CLOSE)


def test_guard_disabled_keeps_stale_candle(mark_feed, monkeypatch):
    # With the ops switch off, behaviour is exactly as before — stale candle.
    import src.runtime_tunables as _rt

    monkeypatch.setattr(
        _rt, "get",
        lambda key: False if key == "mark_feed_staleness_enabled" else 120.0,
    )
    monitor = _monitor(age_seconds=10800.0)
    assert monitor._latest_price(_SYMBOL) == pytest.approx(_STALE_CLOSE)


def test_stale_but_no_mark_price_falls_back_to_candle():
    # Feed running but hasn't seen this symbol → don't worsen behaviour, keep
    # the last known candle close rather than returning nothing.
    prev = _mpf.get_instance()
    feed = MagicMock()
    feed.get_price.return_value = None
    _mpf.set_instance(feed)
    try:
        monitor = _monitor(age_seconds=10800.0)
        assert monitor._latest_price(_SYMBOL) == pytest.approx(_STALE_CLOSE)
    finally:
        _mpf.set_instance(prev)  # type: ignore[arg-type]
