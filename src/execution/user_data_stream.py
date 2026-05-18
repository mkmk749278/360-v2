"""WebSocket consumer for Binance Futures User Data Stream.

Subscribes to ``wss://fstream.binance.com/ws/<listenKey>``, parses each
incoming JSON message into a typed event from
:mod:`src.execution.events`, and dispatches to a caller-supplied
async handler.

Connection lifecycle: one WebSocket per listenKey per user.  On any
disconnect (network, server-side close, ``listenKeyExpired`` event),
:func:`consume` returns — the per-user worker (PR-5)'s outer loop is
responsible for reconnect + listenKey reacquire.

Concurrency: one asyncio task per user.  No shared state between
users at this layer — that's the point.  PR-6's FSM may share state
across handlers if needed, but the WS plumbing keeps users isolated.

Message volume: Binance pushes O(1) events per order state change.
For a paid subscriber averaging ~25 signals/day with 3-4 orders per
signal (entry + SL + multi-TP), the rate is ~100 events/day per
user → trivial CPU load.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncIterator, Awaitable, Callable, Optional

from src.utils import get_logger

from . import events as _events

log = get_logger("execution.user_data_stream")


_WS_BASE = "wss://fstream.binance.com/ws"


# Event handler: an async callable that receives one typed event.  The
# per-user worker (PR-5) wires this; PR-6's FSM will be the real
# handler that mutates state in response to fills.
EventHandler = Callable[[_events.Event], Awaitable[None]]


async def consume(
    listen_key: str,
    handler: EventHandler,
    *,
    ws_factory: Optional[Callable[[str], Any]] = None,
) -> None:
    """Connect to the User Data Stream and dispatch every message.

    Returns when the WS closes (graceful or otherwise).  Does NOT
    reconnect — that's the caller's responsibility.

    ``ws_factory`` is injectable for tests: pass a callable that takes
    the URL and returns an async-context-manager yielding an object
    with an async ``__aiter__`` over message strings.  Default uses
    the ``websockets`` library.

    Unknown event types (``UnknownEventType``) are logged + skipped —
    Binance pushes event types we don't subscribe to alongside the
    ones we do (e.g. ``ACCOUNT_CONFIG_UPDATE``); don't error on them.
    Malformed JSON is logged + skipped.  Handler exceptions are
    logged but don't tear down the stream — the FSM (PR-6) handles
    its own per-event errors.
    """
    url = f"{_WS_BASE}/{listen_key}"
    if ws_factory is None:
        ws_factory = _default_ws_factory
    log.info("user_data_stream: connecting to {}", url.replace(listen_key, "<listenKey>"))
    async with ws_factory(url) as ws:
        async for raw in ws:
            try:
                message = json.loads(raw)
            except (TypeError, ValueError) as exc:
                log.warning("user_data_stream: malformed JSON: {}", exc)
                continue
            try:
                event = _events.parse_event(message)
            except _events.UnknownEventType as exc:
                # Common — Binance pushes event types we don't subscribe
                # to.  Debug-log and move on.
                log.debug("user_data_stream: {}", exc)
                continue
            except ValueError as exc:
                log.warning("user_data_stream: event parse failed: {}", exc)
                continue
            try:
                await handler(event)
            except Exception:
                # Handler is the caller's domain — if it raises we log
                # and continue.  Tearing down the WS for a handler bug
                # would magnify the blast radius beyond the one event.
                log.exception(
                    "user_data_stream: handler raised on event type={}",
                    type(event).__name__,
                )
    log.info("user_data_stream: WS closed")


def _default_ws_factory(url: str) -> Any:
    """Production WS factory using the ``websockets`` library.

    Returns an async context manager that yields the connected
    WebSocket.  Tests inject a different factory to avoid real
    network I/O.
    """
    import websockets  # lazy import — keep startup cost off the path

    return websockets.connect(
        url,
        ping_interval=30,
        ping_timeout=15,
        close_timeout=5,
    )
