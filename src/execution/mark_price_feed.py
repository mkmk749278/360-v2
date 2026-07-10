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
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set

from config import (
    MARK_PRICE_FEED_SILENCE_TIMEOUT_SEC,
    MARK_PRICE_FEED_WS_URL,
)
from src.utils import get_logger

log = get_logger("execution.mark_price_feed")

# Strong-reference set for fire-and-forget dispatch tasks.  asyncio keeps
# tasks in a WeakSet; without an external strong reference a task can be
# garbage-collected before it completes.  Tasks remove themselves on done.
_background_tasks: Set[asyncio.Task[None]] = set()

# Module-level singleton — set by bootstrap, read by anything that needs
# live mark prices (pretp_dispatcher, future risk monitors, etc.).
_instance: Optional["MarkPriceFeed"] = None


def set_instance(feed: "MarkPriceFeed") -> None:
    global _instance
    _instance = feed


def get_instance() -> Optional["MarkPriceFeed"]:
    return _instance


_MIN_BACKOFF_S = 1.0
_MAX_BACKOFF_S = 60.0

# Legacy (pre-2026-04-23) unrouted prefix.  Mark-price streams belong to the
# ``/market`` category; on an unrouted ``/ws/...`` connection the handshake
# still succeeds but Binance never pushes a frame — the feed sat "connected"
# with an empty price map while the SL/TP backstop went blind on every
# out-of-universe symbol (TAIKOUSDT/APEUSDT/POWERUSDT, 2026-07-10, F-07).
_LEGACY_PREFIX = "wss://fstream.binance.com/ws/"
_ROUTED_PREFIX = "wss://fstream.binance.com/market/ws/"


def _normalized_ws_url() -> str:
    """Return the configured feed URL, auto-correcting a legacy unrouted
    override so an old ``.env`` value can't silently re-break the feed —
    the same defence ``websocket_manager._build_combined_stream_url``
    applies to ``BINANCE_FUTURES_WS_BASE`` (2026-05-14 env-override trap).
    """
    url = MARK_PRICE_FEED_WS_URL
    if url.startswith(_LEGACY_PREFIX):
        corrected = _ROUTED_PREFIX + url[len(_LEGACY_PREFIX):]
        log.warning(
            "mark_price_feed: MARK_PRICE_FEED_WS_URL ({}) uses the "
            "pre-2026-04-23 legacy unrouted path — auto-correcting to {} "
            "(market-category streams never push data on unrouted "
            "connections).  Update .env to silence this warning.",
            url, corrected,
        )
        return corrected
    return url


# Subscriber callback signature.  ``symbol`` is uppercase (Binance
# convention); ``mark_price`` is the float parsed from Binance's
# string-encoded number.
MarkPriceCallback = Callable[[str, float], Awaitable[None]]


class FeedSilentError(Exception):
    """Connection open but no frame within the silence timeout —
    treat as a failed connection so the reconnect loop cycles it."""


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
        # Per-symbol funding info from the same stream: (funding_rate,
        # next_funding_time_ms).  The markPrice stream carries ``r``
        # (funding rate) and ``T`` (next funding time) for every symbol
        # every second — the funding-exit watcher reads these directly
        # so it never needs a hardcoded funding interval (Binance uses
        # 4h / 8h / 1h depending on the pair) or a separate REST poll.
        self._funding: Dict[str, tuple[float, int]] = {}
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

    def get_funding_info(self, symbol: str) -> Optional[tuple[float, int]]:
        """Return ``(funding_rate, next_funding_time_ms)`` for ``symbol``
        or None if no update has been seen yet.

        ``funding_rate`` is the current rate that will be applied at the
        next settlement: positive → longs pay shorts; negative → shorts
        pay longs.  ``next_funding_time_ms`` is the authoritative next
        settlement timestamp (Unix ms) for THIS symbol — already correct
        for whatever funding interval Binance uses for the pair (4h / 8h /
        1h), so callers must not assume a fixed interval.
        """
        return self._funding.get(symbol.upper())

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
            except FeedSilentError:
                # Already logged at ERROR in _consume_once — just cycle
                # the connection through the backoff below.
                pass
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
        """One WS connection lifetime — open, consume until close.

        A healthy ``!markPrice@arr@1s`` connection ticks every second, so
        a connection that stays silent for
        ``MARK_PRICE_FEED_SILENCE_TIMEOUT_SEC`` is dead-but-open (the
        legacy-URL decommission presented exactly this way: clean
        handshake, zero frames, forever).  Raise so :meth:`run`
        reconnects with backoff instead of trusting it indefinitely —
        silence must never look like health on the SL/TP price path.
        """
        factory = self._ws_factory or _default_ws_factory
        first_frame_logged = False
        async with factory(_normalized_ws_url()) as ws:
            messages = ws.__aiter__()
            while True:
                try:
                    raw = await asyncio.wait_for(
                        messages.__anext__(),
                        timeout=MARK_PRICE_FEED_SILENCE_TIMEOUT_SEC,
                    )
                except StopAsyncIteration:
                    break
                except asyncio.TimeoutError:
                    log.error(
                        "mark_price_feed: connected but received no frame "
                        "for {}s — dead-but-open connection (wrong/legacy "
                        "URL or upstream outage); reconnecting",
                        MARK_PRICE_FEED_SILENCE_TIMEOUT_SEC,
                    )
                    raise FeedSilentError(
                        f"no frame in {MARK_PRICE_FEED_SILENCE_TIMEOUT_SEC}s"
                    )
                try:
                    payload = json.loads(raw)
                except (TypeError, ValueError) as exc:
                    log.warning("mark_price_feed: malformed JSON: {}", exc)
                    continue
                if not first_frame_logged:
                    first_frame_logged = True
                    log.info(
                        "mark_price_feed: receiving ({} symbols in first "
                        "frame)",
                        len(payload) if isinstance(payload, list) else 1,
                    )
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
        "E": ..., "s": "BTCUSDT", "p": "29005.5", "r": "0.0001",
        "T": 1562306400000, ... }``.  We capture ``s`` (symbol),
        ``p`` (mark price), and — for the funding-exit watcher — ``r``
        (funding rate) and ``T`` (next funding time, ms).
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
        # Capture funding info when present.  ``r``/``T`` are absent on
        # the legacy single-symbol stream shape used by some tests, so
        # only update when both parse cleanly — never clobber a good
        # value with a bad one.
        try:
            funding_rate = float(entry["r"])
            next_funding_ms = int(entry["T"])
        except (KeyError, TypeError, ValueError):
            pass
        else:
            self._funding[symbol] = (funding_rate, next_funding_ms)
        async with self._lock:
            subscribers = list(self._subscribers.get(symbol, ()))
        if not subscribers:
            return
        # Dispatch concurrently — one task per subscriber.  Slow
        # subscriber doesn't block the rest.  Each task is added to
        # _background_tasks so the event loop's WeakSet doesn't GC it
        # before it finishes; the done callback removes the reference.
        for cb in subscribers:
            task = asyncio.create_task(_safe_dispatch(cb, symbol, mark_price))
            _background_tasks.add(task)
            task.add_done_callback(_background_tasks.discard)


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
