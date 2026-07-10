"""REST seeds must stamp kline freshness (2026-07-10).

Regression for the MVLLUSDT frozen-price case: promoted MOVER pairs have no
WS kline subscription, so the one-time promotion seed was their only candle
write — and seeds never stamped ``_last_kline_update_ts``.  With
``last_kline_age_seconds() is None`` forever, BOTH staleness protections
(the scanner's dispatch gate and trade_monitor's #706 mark-feed fallback)
failed open: the store served the last seeded close (38.1800) for 11+ hours
while the open signal's PnL, MFE, TP2/TP3 detection, trail, and SL backstop
all ran blind.

Three properties are locked here:

1. ``seed_symbol`` stamps ``_last_kline_update_ts`` for every timeframe it
   writes, so seeded symbols carry a REAL age from the moment they have data.
2. ``_gap_fetch_and_merge`` stamps on merge writes too.
3. ``TradeMonitor._candle_stale`` treats a never-stamped symbol as STALE once
   the monitor is past its post-boot grace window (mark-feed pricing takes
   over), while keeping the fresh-boot behaviour (no diversion) intact.
"""
from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.execution import mark_price_feed as _mpf
from src.historical_data import HistoricalDataStore
from src.trade_monitor import TradeMonitor

_SYMBOL = "MVLLUSDT"
_FROZEN_CLOSE = 38.18
_FRESH_MARK = 39.42


def _candle_payload(n: int = 30) -> dict:
    return {
        "open": [_FROZEN_CLOSE] * n,
        "high": [_FROZEN_CLOSE] * n,
        "low": [_FROZEN_CLOSE] * n,
        "close": [_FROZEN_CLOSE] * n,
        "volume": [1000.0] * n,
    }


async def test_seed_symbol_stamps_freshness_for_every_timeframe():
    store = HistoricalDataStore()
    store.fetch_candles = AsyncMock(return_value=_candle_payload())
    store.fetch_recent_trades = AsyncMock(return_value=[])

    before = time.time()
    await store.seed_symbol(_SYMBOL, "futures")

    # Every timeframe the seed wrote must now report a real (small) age.
    assert store.candles[_SYMBOL], "seed wrote no candles"
    for interval in store.candles[_SYMBOL]:
        age = store.last_kline_age_seconds(_SYMBOL, interval)
        assert age is not None, f"{interval}: seed did not stamp freshness"
        assert age <= time.time() - before + 5.0


async def test_gap_fetch_and_merge_stamps_freshness():
    store = HistoricalDataStore()
    store.candles[_SYMBOL] = {"1m": _candle_payload()}
    store.fetch_candles = AsyncMock(return_value=_candle_payload(5))

    await store._gap_fetch_and_merge(_SYMBOL, "1m", gap=5, limit=500, market="futures")

    assert store.last_kline_age_seconds(_SYMBOL, "1m") is not None


async def test_seed_failure_does_not_stamp():
    store = HistoricalDataStore()
    store.fetch_candles = AsyncMock(return_value=None)  # REST returned nothing
    store.fetch_recent_trades = AsyncMock(return_value=[])

    await store.seed_symbol(_SYMBOL, "futures")

    assert store.last_kline_age_seconds(_SYMBOL, "1m") is None


# ---------------------------------------------------------------------------
# TradeMonitor: never-stamped symbols go stale after the post-boot grace
# ---------------------------------------------------------------------------


@pytest.fixture
def mark_feed():
    prev = _mpf.get_instance()
    feed = MagicMock()
    feed.get_price.side_effect = lambda s: _FRESH_MARK if s == _SYMBOL else None
    _mpf.set_instance(feed)
    try:
        yield feed
    finally:
        _mpf.set_instance(prev)  # type: ignore[arg-type]


def _monitor(age_seconds):
    data_store = MagicMock()
    data_store.get_candles.return_value = _candle_payload(1)
    data_store.last_kline_age_seconds.return_value = age_seconds
    data_store.ticks = {}
    return TradeMonitor(
        data_store=data_store,
        send_telegram=MagicMock(),
        get_active_signals=lambda: {},
        remove_signal=MagicMock(),
        update_signal=MagicMock(),
    )


def test_unstamped_symbol_goes_stale_after_boot_grace(mark_feed):
    """age=None past the grace window → the frozen close is abandoned and the
    signal prices off the live mark feed (the MVLLUSDT fix)."""
    monitor = _monitor(age_seconds=None)
    monitor._started_at_monotonic = time.monotonic() - 10_000  # long-lived engine
    assert monitor._latest_price(_SYMBOL) == pytest.approx(_FRESH_MARK)
    high, low = monitor._candle_extremes(_SYMBOL)
    assert high == pytest.approx(_FRESH_MARK)
    assert low == pytest.approx(_FRESH_MARK)


def test_unstamped_symbol_fresh_during_boot_grace(mark_feed):
    """Right after boot, age=None must NOT divert (WS frames still arriving)."""
    monitor = _monitor(age_seconds=None)  # _started_at_monotonic = now
    assert monitor._latest_price(_SYMBOL) == pytest.approx(_FROZEN_CLOSE)


def test_stamped_fresh_symbol_still_uses_candles(mark_feed):
    monitor = _monitor(age_seconds=5.0)
    monitor._started_at_monotonic = time.monotonic() - 10_000
    assert monitor._latest_price(_SYMBOL) == pytest.approx(_FROZEN_CLOSE)
