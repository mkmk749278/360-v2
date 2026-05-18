"""Tests for src.execution.user_data_stream.

The WS factory is injected so we never open a real socket.  What we
pin:

* Messages parse + dispatch to the handler in order.
* Unknown event types log + skip (don't crash the stream).
* Malformed JSON logs + skip.
* Handler exceptions don't tear down the WS — the FSM (PR-6) can
  bug-out on one event without blocking subsequent events.
* The URL includes the listenKey path.
"""
from __future__ import annotations

import json
from typing import Any, List
from unittest.mock import AsyncMock

import pytest

from src.execution import events as events_mod
from src.execution import user_data_stream


# ---------------------------------------------------------------------------
# Helpers: fake WS factory + collecting handler
# ---------------------------------------------------------------------------


class _FakeWs:
    """Async-iterable fake WS that yields the messages it was given."""

    def __init__(self, messages: List[str]) -> None:
        self._messages = list(messages)
        self.connect_url: str = ""

    def __aiter__(self):
        async def gen():
            for m in self._messages:
                yield m
        return gen()


class _FakeWsContextManager:
    """async-context-manager wrapping a :class:`_FakeWs`."""

    def __init__(self, ws: _FakeWs, url: str) -> None:
        self._ws = ws
        self._ws.connect_url = url

    async def __aenter__(self) -> _FakeWs:
        return self._ws

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


def _factory_returning(messages: List[Any]):
    """Return a ws_factory callable that yields the given messages.

    Messages may be raw JSON strings OR dicts (auto-serialised to JSON
    strings for convenience)."""

    serialised = [
        m if isinstance(m, str) else json.dumps(m) for m in messages
    ]

    def _make(url: str) -> _FakeWsContextManager:
        return _FakeWsContextManager(_FakeWs(serialised), url)

    return _make


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_consume_dispatches_each_message_to_handler() -> None:
    received: List[events_mod.Event] = []

    async def handler(event):
        received.append(event)

    messages = [
        {
            "e": "ORDER_TRADE_UPDATE",
            "E": 0,
            "o": {"s": "BTCUSDT", "X": "FILLED", "x": "TRADE", "l": "1.0"},
        },
        {
            "e": "ACCOUNT_UPDATE",
            "E": 0,
            "T": 0,
            "a": {"m": "ORDER", "B": [], "P": []},
        },
    ]
    await user_data_stream.consume(
        "fake-listen-key",
        handler,
        ws_factory=_factory_returning(messages),
    )
    assert len(received) == 2
    assert isinstance(received[0], events_mod.OrderTradeUpdate)
    assert isinstance(received[1], events_mod.AccountUpdate)


@pytest.mark.asyncio
async def test_consume_skips_unknown_event_types_without_crashing() -> None:
    """Binance pushes event types we don't subscribe to alongside the
    ones we do (ACCOUNT_CONFIG_UPDATE, STRATEGY_UPDATE, etc.).
    Consumer must skip them rather than crash."""
    received: List[events_mod.Event] = []

    async def handler(event):
        received.append(event)

    messages = [
        {"e": "ACCOUNT_CONFIG_UPDATE", "E": 0},  # unknown — should skip
        {
            "e": "ORDER_TRADE_UPDATE",
            "E": 0,
            "o": {"s": "BTCUSDT", "X": "FILLED", "l": "1.0"},
        },  # known — should be dispatched
    ]
    await user_data_stream.consume(
        "fake-listen-key",
        handler,
        ws_factory=_factory_returning(messages),
    )
    # Only the known event reaches the handler.
    assert len(received) == 1
    assert isinstance(received[0], events_mod.OrderTradeUpdate)


@pytest.mark.asyncio
async def test_consume_skips_malformed_json() -> None:
    received: List[events_mod.Event] = []

    async def handler(event):
        received.append(event)

    # Raw strings — first one is bad JSON, second one is a valid event.
    messages = [
        "not-json-at-all",
        json.dumps(
            {
                "e": "listenKeyExpired",
                "E": 123,
            }
        ),
    ]
    await user_data_stream.consume(
        "fake-listen-key",
        handler,
        ws_factory=_factory_returning(messages),
    )
    assert len(received) == 1
    assert isinstance(received[0], events_mod.ListenKeyExpired)


@pytest.mark.asyncio
async def test_handler_exception_does_not_tear_down_stream() -> None:
    """A handler bug on one event must NOT prevent subsequent events
    from being processed.  The blast radius of a handler bug is
    bounded to that one event."""
    received: List[events_mod.Event] = []

    async def handler(event):
        if isinstance(event, events_mod.OrderTradeUpdate):
            raise RuntimeError("buggy handler")
        received.append(event)

    messages = [
        {
            "e": "ORDER_TRADE_UPDATE",
            "E": 0,
            "o": {"s": "BTCUSDT", "X": "FILLED", "l": "1.0"},
        },  # handler raises
        {"e": "listenKeyExpired", "E": 999},  # handler succeeds
    ]
    await user_data_stream.consume(
        "fake-listen-key",
        handler,
        ws_factory=_factory_returning(messages),
    )
    # The second event (listenKeyExpired) reached the handler despite
    # the first one raising.
    assert len(received) == 1
    assert isinstance(received[0], events_mod.ListenKeyExpired)


@pytest.mark.asyncio
async def test_consume_url_includes_listen_key() -> None:
    """Verify the consumer hits ``wss://fstream.binance.com/ws/<listenKey>``."""
    seen_url: List[str] = []

    def _factory(url: str):
        seen_url.append(url)
        return _FakeWsContextManager(_FakeWs([]), url)

    async def handler(event):
        pass

    await user_data_stream.consume(
        "my-listen-key-123", handler, ws_factory=_factory
    )
    assert seen_url == ["wss://fstream.binance.com/ws/my-listen-key-123"]
