"""The bridge between :mod:`mark_price_feed` and :mod:`pretp_controller`.

This is the missing piece for §3.2a doctrine to ACTUALLY fire:

* PR-7's :func:`pretp_controller.maybe_fire_pretp` knows WHEN to
  fire (threshold logic) but needs SOMEONE to call it per tick.
* PR-5's :class:`PositionWorker` knows ABOUT the position (via the
  Firestore Position doc) but doesn't subscribe to mark prices.
* PR-9's :class:`MarkPriceFeed` knows ABOUT prices but doesn't know
  about positions.

This module wires the three together: on every mark-price tick for
symbol X, iterate over all open positions with symbol=X across all
active users, and call :func:`maybe_fire_pretp` for each.

The subscription model is "subscribe per-symbol-once for the entire
engine": when the first user opens a position on BTCUSDT, we
subscribe to BTCUSDT mark-price updates; the subscription handler
fans out to every BTCUSDT position across users.  When the LAST
position on BTCUSDT closes, we unsubscribe.

Position discovery: this PR uses a simple "query Firestore for open
positions" approach (which is O(N) per tick).  A future hardening
would maintain an in-memory index of open positions per symbol —
trivial work for solo + small users, but worth noting in case the
volume grows.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, List, Optional, Set

from src.utils import get_logger

from . import mark_price_feed as _mark_price_feed
from . import order_placer as _order_placer
from . import position_state as _position_state
from . import pretp_controller as _pretp_controller

log = get_logger("execution.pretp_dispatcher")

# Module-level singleton — set by bootstrap, called by position_fsm
# to track/untrack symbols as positions open/close.
_instance: Optional["PretpDispatcher"] = None


def set_instance(d: "PretpDispatcher") -> None:
    global _instance
    _instance = d


def get_instance() -> Optional["PretpDispatcher"]:
    return _instance


class PretpDispatcher:
    """Per-engine dispatcher that bridges mark prices to pre-TP firing.

    One instance per engine process.  Subscribes to the
    :class:`MarkPriceFeed` for the symbols of currently-open
    positions.  On every tick, iterates the matching positions and
    calls :func:`pretp_controller.maybe_fire_pretp`.

    Tracks which symbols are currently subscribed so we don't double-
    subscribe.  Symbol set is mutated by ``track`` /
    ``untrack`` which the FSM calls at position open / close.
    """

    def __init__(
        self,
        feed: _mark_price_feed.MarkPriceFeed,
        *,
        positions_for_symbol: Optional[
            Callable[[str], List[_position_state.Position]]
        ] = None,
        order_placer_factory: Optional[
            Callable[[str], _order_placer.OrderPlacer]
        ] = None,
    ) -> None:
        self._feed = feed
        self._subscribed: Set[str] = set()
        self._subscribed_lock = asyncio.Lock()
        # Pluggable so tests don't need a live Firestore.  Default
        # production wiring queries Firestore by symbol.
        self._positions_for_symbol = (
            positions_for_symbol or _default_positions_for_symbol
        )
        self._order_placer_factory = (
            order_placer_factory or _default_order_placer_factory
        )

    async def track(self, symbol: str) -> None:
        """Register interest in ``symbol`` so we'll receive ticks for
        it.  Idempotent — called by the FSM at every position open;
        no-op if already subscribed.
        """
        sym = symbol.upper()
        async with self._subscribed_lock:
            if sym in self._subscribed:
                return
            self._subscribed.add(sym)
        await self._feed.subscribe(sym, self._on_tick)
        log.info("pretp_dispatcher: tracking symbol={}", sym)

    async def untrack(self, symbol: str) -> None:
        """Drop subscription for ``symbol``.  Called when the LAST
        open position for that symbol closes — leaving the
        subscription on would waste cycles dispatching to no
        positions.  Idempotent.
        """
        sym = symbol.upper()
        async with self._subscribed_lock:
            if sym not in self._subscribed:
                return
            self._subscribed.discard(sym)
        await self._feed.unsubscribe(sym, self._on_tick)
        log.info("pretp_dispatcher: untracked symbol={}", sym)

    async def _on_tick(self, symbol: str, mark_price: float) -> None:
        """Mark-price update arrived.  Find all open positions on
        ``symbol`` and dispatch the pre-TP check to each.

        Exception policy: each per-position check is wrapped so one
        bad position doesn't poison the dispatch loop for the others
        on the same symbol.  ``maybe_fire_pretp`` already swallows
        placement failures itself (per PR-7), so this layer's
        try/except catches only programming bugs.
        """
        try:
            positions = self._positions_for_symbol(symbol)
        except Exception:
            log.exception(
                "pretp_dispatcher: positions_for_symbol failed sym={}",
                symbol,
            )
            return
        for position in positions:
            placer = self._order_placer_factory(position.firebase_uid)
            try:
                await _pretp_controller.maybe_fire_pretp(
                    position, mark_price=mark_price, placer=placer
                )
            except Exception:
                log.exception(
                    "pretp_dispatcher: maybe_fire_pretp raised "
                    "uid={} signal_id={}",
                    position.firebase_uid, position.signal_id,
                )


def _default_positions_for_symbol(symbol: str) -> List[_position_state.Position]:
    """Query Firestore for open positions on ``symbol`` across all
    users.  Production wiring; tests inject a different impl.

    Uses a collection-group query so we don't need to iterate users
    individually.  Filters to ``state == OPEN`` (pre-TP only fires
    from OPEN; PRE_TP_FIRED + later states don't need ticks).
    """
    from src.security.firestore_keystore import _db  # shared client

    if _db is None:
        return []
    query = (
        _db.collection_group("positions")
        .where("symbol", "==", symbol)
        .where("state", "==", "OPEN")
    )
    out: List[_position_state.Position] = []
    for snap in query.stream():
        data = snap.to_dict() or {}
        try:
            out.append(_position_state._from_firestore_dict(data))
        except Exception:
            log.exception(
                "pretp_dispatcher: failed to parse position doc"
            )
    return out


def _default_order_placer_factory(
    firebase_uid: str,
) -> _order_placer.OrderPlacer:
    return _order_placer.OrderPlacer(firebase_uid)
