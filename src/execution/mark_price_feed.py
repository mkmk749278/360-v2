"""Binance Futures mark-price WebSocket feed.

Subscribes to the public ``!markPrice@arr@1s`` stream which broadcasts
mark prices for ALL Futures symbols every 1 second.  Maintains an
in-memory ``Dict[symbol, mark_price]`` and dispatches per-symbol
updates to registered subscribers.

This is the missing piece for §3.2a doctrine to actually fire: the
:mod:`src.execution.pretp_controller` knows WHEN to fire (when mark
price crosses the threshold) but needs SOMEONE to call it on every
price tick.  The :class:`PretpDispatcher` (separate module — bridges
this feed to the FSM) is the someone.

Why all-symbols stream (not per-symbol)?  Solo + small users means
~10 active symbols max from the engine's signal-channel allowlist.
One global subscription is simpler than spinning up + tearing down
per-symbol streams as positions open + close, and the message
volume (~10 messages/sec for 10 symbols) is trivial to process.

The feed is PUBLIC — no signing required, no per-user authentication.
That's a clean separation from the signed User Data Stream (PR-5);
this module has no GCP dependency.

Lifecycle: ``MarkPriceFeed.run()`` is the main loop, run as one
asyncio task per engine process.  On WS disconnect it reconnects
with exponential backoff (same pattern as PR-5's PositionWorker).
``stop()`` requests a clean shutdown.

Subscribers register via ``subscribe(symbol, callback)`` where
``callback(symbol, mark_price)`` is async.  Subscriber exceptions are
caught + logged — one buggy subscriber can't tear down the feed (the
defence-in-depth pattern from PR-5 applied at the dispatch boundary).
"""

from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, List, Optional

from src.utils import get_logger

log = get_logger("execution.mark_price_feed")


_WS_URL = "wss://fstream.binance.com/ws/!markPrice@arr@1s"
_MIN_BACKOFF_S = 1.0
_MAX_BACKOFF_S = 60.0


# Subscriber callback signature.  ``symbol`` is uppercase (Binance
# convention); ``mark_price`` is the float parsed from Binance's
# string-encoded number.
MarkPriceCallback = Callable[[str, float], Awaitable[None]]


class MarkPriceFeed:
    """Async-context manager / runnable that maintains a live mark-
    price map for all Binance Futures symbols.

    Concurrent subscriber callbacks are dispatched as separate
    asyncio tasks so a slow subscriber doesn't block other
    subscribers for the same symbol.  Callback exceptions are caught
    + logged at the dispatch boundary.

    Tests inject ``ws_factory`` to replace the real WebSocket with a
    deterministic fake.
    """

    def __init__(
        self,
        *,
        ws_factory: Optional[Callable[[str], Any]] = None,
    ) -> None:
        self._ws_factory = ws_factory
        self._stop_event = asyncio.Event()
        self._prices: Dict[str, float] = {}
        self._subscribers: Dict[str, List[MarkPriceCallback]] = defaultdict(
            list
        )
        self._lock = asyncio.Lock()

    # ---- Subscriber API ----------------------------------------------

    async def subscribe(
        self, symbol: str, callback: MarkPriceCallback
    ) -> None:
        """Register a callback that fires every time ``symbol`` gets
        a fresh mark price.  Callbacks are dispatched concurrently
        (one task per callback per tick) so slow subscribers don't
        block fast ones.
        """
        sym = symbol.upper()
        async with self._lock:
            self._subscribers[sym].append(callback)

    async def unsubscribe(
        self, symbol: str, callback: MarkPriceCallback
    ) -> None:
        """Remove a previously-registered callback.  No-op when the
        callback isn't registered (defensive)."""
        sym = symbol.upper()
        async with self._lock:
            if sym in self._subscribers:
                try:
                    self._subscribers[sym].remove(callback)
                except ValueError:
                    pass

    def get_price(self, symbol: str) -> Optional[float]:
        """Return the most-recent mark price for ``symbol`` or None
        if we haven't received an update for it yet.  Synchronous —
        callers reading occasionally rather than reacting to ticks."""
        return self._prices.get(symbol.upper())

    # ---- Lifecycle ----------------------------------------------------

    async def stop(self) -> None:
        """Request shutdown.  Next reconnect-loop iteration exits."""
        self._stop_event.set()

    async def run(self) -> None:
        """Main loop with exponential-backoff reconnect.

        Identical structure to PR-5's PositionWorker: each iteration
        is wrapped so a single WS disconnect doesn't end the feed.
        Exits cleanly when :meth:`stop` is called.
        """
        backoff_s = _MIN_BACKOFF_S
        while not self._stop_event.is_set():
            try:
                await self._consume_once()
                # Clean WS close (no exception) — reset backoff.
                backoff_s = _MIN_BACKOFF_S
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("mark_price_feed: error in main loop")
            if self._stop_event.is_set():
                break
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(), timeout=backoff_s
                )
                break  # stop fired during sleep
            except asyncio.TimeoutError:
                pass
            backoff_s = min(backoff_s * 2.0, _MAX_BACKOFF_S)
        log.info("mark_price_feed: stopped")

    async def _consume_once(self) -> None:
        """One WS connection lifetime — open, consume until close."""
        factory = self._ws_factory or _default_ws_factory
        async with factory(_WS_URL) as ws:
            async for raw in ws:
                try:
                    payload = json.loads(raw)
                except (TypeError, ValueError) as exc:
                    log.warning("mark_price_feed: malformed JSON: {}", exc)
                    continue
                # The ``!markPrice@arr@1s`` stream sends a JSON array
                # of per-symbol updates per tick.  Earlier "single
                # symbol" streams send a dict; handle both shapes.
                if isinstance(payload, list):
                    for entry in payload:
                        await self._handle_update(entry)
                elif isinstance(payload, dict):
                    await self._handle_update(payload)
                else:
                    log.warning(
                        "mark_price_feed: unexpected payload type: {}",
                        type(payload).__name__,
                    )

    async def _handle_update(self, entry: Any) -> None:
        """One per-symbol update.

        Binance's mark-price update shape: ``{ "e": "markPriceUpdate",
        "E": ..., "s": "BTCUSDT", "p": "29005.5", ... }``.  We only
        care about ``s`` (symbol) and ``p`` (mark price).
        """
        if not isinstance(entry, dict):
            return
        symbol = str(entry.get("s", "")).upper()
        if not symbol:
            return
        try:
            mark_price = float(entry.get("p", "0"))
        except (TypeError, ValueError):
            return
        if mark_price <= 0:
            return
        self._prices[symbol] = mark_price
        async with self._lock:
            subscribers = list(self._subscribers.get(symbol, ()))
        if not subscribers:
            return
        # Dispatch concurrently — one task per subscriber.  Slow
        # subscriber doesn't block the rest.
        for cb in subscribers:
            asyncio.create_task(_safe_dispatch(cb, symbol, mark_price))


async def _safe_dispatch(
    cb: MarkPriceCallback, symbol: str, mark_price: float
) -> None:
    """Wrap callback dispatch in a try/except so subscriber bugs
    don't tear down the feed.  Mirrors the bounded-blast-radius
    pattern from PR-5's user_data_stream."""
    try:
        await cb(symbol, mark_price)
    except Exception:
        log.exception(
            "mark_price_feed: subscriber raised on {}={}",
            symbol, mark_price,
        )


def _default_ws_factory(url: str) -> Any:
    """Production WS factory.  Tests inject a different factory."""
    import websockets

    return websockets.connect(
        url, ping_interval=30, ping_timeout=15, close_timeout=5
    )
