"""Tests for src.execution.mark_price_feed.

WS factory injected so tests don't need a real socket.  What we pin:

* Subscribers receive (symbol, mark_price) on every tick.
* Multiple subscribers per symbol dispatch concurrently — slow one
  doesn't block fast one.
* Subscriber exception logged but doesn't tear down the feed.
* Symbol matching is case-insensitive.
* Unsubscribe stops further callbacks.
* All-symbols array payload (the production stream shape) parses
  correctly.
* get_price() returns latest price or None.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, List, Tuple

import pytest

from src.execution import mark_price_feed


class _FakeWs:
    def __init__(self, messages: List[str]) -> None:
        self._messages = list(messages)

    def __aiter__(self):
        async def gen():
            for m in self._messages:
                yield m
        return gen()


class _FakeWsCtx:
    def __init__(self, ws: _FakeWs) -> None:
        self._ws = ws

    async def __aenter__(self):
        return self._ws

    async def __aexit__(self, exc_type, exc, tb):
        return None


def _factory_returning(messages):
    serialised = [
        m if isinstance(m, str) else json.dumps(m) for m in messages
    ]
    def _make(url: str):
        return _FakeWsCtx(_FakeWs(serialised))
    return _make


def _array_payload(symbol_prices: List[Tuple[str, str]]) -> dict:
    """Build a single payload entry for the all-symbols stream."""
    return [
        {"e": "markPriceUpdate", "E": 0, "s": s, "p": p}
        for s, p in symbol_prices
    ]


@pytest.mark.asyncio
async def test_subscriber_receives_ticks() -> None:
    received: List[Tuple[str, float]] = []

    async def cb(symbol: str, price: float):
        received.append((symbol, price))

    feed = mark_price_feed.MarkPriceFeed(
        ws_factory=_factory_returning([
            _array_payload([("BTCUSDT", "29000.5"), ("ETHUSDT", "2000.5")]),
            _array_payload([("BTCUSDT", "29005.5")]),
        ])
    )
    await feed.subscribe("BTCUSDT", cb)
    await feed._consume_once()
    # Wait briefly for the create_task dispatches to settle.
    await asyncio.sleep(0.05)
    # Subscriber should have received BTCUSDT ticks (two of them).
    btc_ticks = [t for t in received if t[0] == "BTCUSDT"]
    assert len(btc_ticks) == 2
    assert btc_ticks[0] == ("BTCUSDT", 29000.5)
    assert btc_ticks[1] == ("BTCUSDT", 29005.5)


@pytest.mark.asyncio
async def test_get_price_returns_latest() -> None:
    feed = mark_price_feed.MarkPriceFeed(
        ws_factory=_factory_returning([
            _array_payload([("BTCUSDT", "29000.5")]),
            _array_payload([("BTCUSDT", "29005.5")]),
        ])
    )
    assert feed.get_price("BTCUSDT") is None  # no data yet
    await feed._consume_once()
    assert feed.get_price("BTCUSDT") == 29005.5
    # Case-insensitive.
    assert feed.get_price("btcusdt") == 29005.5


@pytest.mark.asyncio
async def test_subscriber_exception_does_not_tear_down_feed() -> None:
    """Defence-in-depth: a buggy callback for one symbol shouldn't
    stop other symbols' callbacks (or subsequent ticks for the same
    symbol)."""
    received: List[Tuple[str, float]] = []

    async def bad_cb(symbol: str, price: float):
        raise RuntimeError("buggy callback")

    async def good_cb(symbol: str, price: float):
        received.append((symbol, price))

    feed = mark_price_feed.MarkPriceFeed(
        ws_factory=_factory_returning([
            _array_payload([("BTCUSDT", "29000.5")]),
            _array_payload([("BTCUSDT", "29005.5")]),
        ])
    )
    await feed.subscribe("BTCUSDT", bad_cb)
    await feed.subscribe("BTCUSDT", good_cb)
    await feed._consume_once()
    await asyncio.sleep(0.05)
    # Good callback fired both times despite bad callback raising.
    assert len(received) == 2


@pytest.mark.asyncio
async def test_unsubscribe_stops_further_callbacks() -> None:
    received: List[Tuple[str, float]] = []

    async def cb(symbol: str, price: float):
        received.append((symbol, price))

    feed = mark_price_feed.MarkPriceFeed(
        ws_factory=_factory_returning([
            _array_payload([("BTCUSDT", "29000.5")]),
        ])
    )
    await feed.subscribe("BTCUSDT", cb)
    await feed.unsubscribe("BTCUSDT", cb)
    await feed._consume_once()
    await asyncio.sleep(0.05)
    assert len(received) == 0


@pytest.mark.asyncio
async def test_malformed_payload_logged_and_skipped() -> None:
    received: List[Tuple[str, float]] = []

    async def cb(symbol: str, price: float):
        received.append((symbol, price))

    feed = mark_price_feed.MarkPriceFeed(
        ws_factory=_factory_returning([
            "not-json",
            _array_payload([("BTCUSDT", "29000.5")]),
        ])
    )
    await feed.subscribe("BTCUSDT", cb)
    # Must not raise; good message still processed.
    await feed._consume_once()
    await asyncio.sleep(0.05)
    assert received == [("BTCUSDT", 29000.5)]


@pytest.mark.asyncio
async def test_zero_or_negative_price_skipped() -> None:
    """Defensive: a malformed price (zero or negative) must NOT
    propagate to subscribers — could trigger a false pre-TP fire
    if it crossed the threshold direction."""
    received: List[Tuple[str, float]] = []

    async def cb(symbol: str, price: float):
        received.append((symbol, price))

    feed = mark_price_feed.MarkPriceFeed(
        ws_factory=_factory_returning([
            _array_payload([("BTCUSDT", "0")]),
            _array_payload([("BTCUSDT", "-1")]),
            _array_payload([("BTCUSDT", "29000.5")]),
        ])
    )
    await feed.subscribe("BTCUSDT", cb)
    await feed._consume_once()
    await asyncio.sleep(0.05)
    # Only the valid price reached the subscriber.
    assert received == [("BTCUSDT", 29000.5)]


@pytest.mark.asyncio
async def test_subscribe_is_case_insensitive() -> None:
    received: List[Tuple[str, float]] = []

    async def cb(symbol: str, price: float):
        received.append((symbol, price))

    feed = mark_price_feed.MarkPriceFeed(
        ws_factory=_factory_returning([
            _array_payload([("BTCUSDT", "29000.5")]),
        ])
    )
    # Subscribe with lowercase; tick arrives as uppercase.
    await feed.subscribe("btcusdt", cb)
    await feed._consume_once()
    await asyncio.sleep(0.05)
    assert received == [("BTCUSDT", 29000.5)]


@pytest.mark.asyncio
async def test_stop_breaks_main_loop() -> None:
    """stop() must release the main reconnect loop within one backoff
    cycle (1s default min backoff)."""
    # WS factory that raises so each consume_once exits quickly and
    # the loop sleeps on backoff (where stop() can take effect).
    def factory(url: str):
        raise RuntimeError("simulated WS unavailable")

    feed = mark_price_feed.MarkPriceFeed(ws_factory=factory)
    task = asyncio.create_task(feed.run())
    await asyncio.sleep(0.1)
    await feed.stop()
    await asyncio.wait_for(task, timeout=3.0)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------


def test_set_and_get_instance() -> None:
    """set_instance / get_instance round-trip."""
    original = mark_price_feed.get_instance()
    feed = mark_price_feed.MarkPriceFeed()
    try:
        mark_price_feed.set_instance(feed)
        assert mark_price_feed.get_instance() is feed
    finally:
        mark_price_feed.set_instance(original)


# ---------------------------------------------------------------------------
# Funding info capture (r / T from the markPrice stream)
# ---------------------------------------------------------------------------


def _funding_payload(entries):
    """Build an all-symbols payload that includes r (funding rate) and
    T (next funding time ms). ``entries`` is a list of
    (symbol, price, rate, next_funding_ms) tuples."""
    return [
        {"e": "markPriceUpdate", "E": 0, "s": s, "p": p, "r": r, "T": t}
        for s, p, r, t in entries
    ]


@pytest.mark.asyncio
async def test_funding_info_captured() -> None:
    feed = mark_price_feed.MarkPriceFeed(
        ws_factory=_factory_returning([
            _funding_payload([("BTCUSDT", "29000.5", "0.00075", 1562306400000)]),
        ])
    )
    assert feed.get_funding_info("BTCUSDT") is None  # no data yet
    await feed._consume_once()
    rate, next_ms = feed.get_funding_info("BTCUSDT")
    assert rate == pytest.approx(0.00075)
    assert next_ms == 1562306400000
    # Case-insensitive lookup.
    assert feed.get_funding_info("btcusdt") == (pytest.approx(0.00075), 1562306400000)


@pytest.mark.asyncio
async def test_funding_info_absent_when_fields_missing() -> None:
    """The legacy price-only payload (no r/T) must not crash and must
    leave funding info as None — price still captured."""
    feed = mark_price_feed.MarkPriceFeed(
        ws_factory=_factory_returning([
            _array_payload([("BTCUSDT", "29000.5")]),
        ])
    )
    await feed._consume_once()
    assert feed.get_price("BTCUSDT") == 29000.5
    assert feed.get_funding_info("BTCUSDT") is None


@pytest.mark.asyncio
async def test_funding_info_negative_rate() -> None:
    feed = mark_price_feed.MarkPriceFeed(
        ws_factory=_factory_returning([
            _funding_payload([("ETHUSDT", "1800.0", "-0.0012", 1562306400000)]),
        ])
    )
    await feed._consume_once()
    rate, _ = feed.get_funding_info("ETHUSDT")
    assert rate == pytest.approx(-0.0012)
