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
import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set

from config import BE_SHIFT_TRIGGER_PCT as _BE_SHIFT_TRIGGER_PCT

from src.execution import be_policy as _be_policy
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
            try:
                await maybe_fire_be_shift(position, mark_price=mark_price, placer=placer)
            except Exception:
                log.exception(
                    "pretp_dispatcher: maybe_fire_be_shift raised "
                    "uid={} signal_id={}",
                    position.firebase_uid, position.signal_id,
                )


# --- Per-symbol OPEN-positions cache -----------------------------------
#
# Mark prices tick ~1/sec/symbol, 24/7.  The original implementation ran
# a Firestore collection-group query on EVERY tick, which made Firestore
# reads — billed under the "App Engine" line — the project's dominant
# cloud cost while writes/deletes stayed inside the free tier.
#
# This cache removes Firestore from the hot path.  Correctness in a
# real-money path hinges on freshness: ``should_fire_pretp`` reads live
# fields (``state``, ``pretp_fired``, ``pretp_order_id``) off the
# position object, so a stale cache could double-fire a partial close.
# We gate the cache on :func:`position_state.get_write_generation` — a
# counter bumped on every ``put_position`` / ``delete_position``.  While
# the generation is unchanged, no position document has changed, so the
# cached query result (and the objects in it) are exactly what a fresh
# query would return.  Any FSM transition, pre-TP fire, or close bumps
# the generation and forces a re-query on the next tick.
#
# ``_QUERY_CACHE_MAX_TTL_S`` is a defensive upper bound on staleness in
# case some future code path writes a position document outside the two
# tracked writers; generation invalidation is the primary mechanism.
#
# A future optimisation (noted in this module's header) is a full
# in-memory open-positions index that avoids even the cold-path query;
# the generation-gated cache is the lower-risk first step.

_QUERY_CACHE_MAX_TTL_S = 10.0

# Injectable clock so tests can exercise TTL expiry deterministically.
_clock: Callable[[], float] = time.monotonic


@dataclass
class _SymbolPositionsCache:
    generation: int
    positions: List[_position_state.Position]
    fetched_at: float


_positions_cache: Dict[str, _SymbolPositionsCache] = {}
_positions_cache_lock = threading.Lock()


def reset_positions_cache_for_test() -> None:
    """Test-only: drop the per-symbol OPEN-positions cache."""
    with _positions_cache_lock:
        _positions_cache.clear()


def _query_open_positions(symbol: str) -> List[_position_state.Position]:
    """Raw Firestore collection-group query for OPEN positions on
    ``symbol`` across all users.  Filters to ``state == OPEN`` (pre-TP
    only fires from OPEN; PRE_TP_FIRED + later states don't need ticks).
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


def _default_positions_for_symbol(symbol: str) -> List[_position_state.Position]:
    """Return OPEN positions on ``symbol``, served from a
    generation-gated cache to keep Firestore off the per-tick hot path.

    Cache hit requires BOTH the position-write generation to be unchanged
    (correctness) AND the entry to be within :data:`_QUERY_CACHE_MAX_TTL_S`
    (defensive freshness bound).  Otherwise re-queries Firestore.

    When the in-memory live-position index is active (engine process), it is
    the authoritative source and is served directly — zero Firestore reads,
    no generation/TTL cache needed.  The generation-gated Firestore cache
    below is the fallback for any process/context where the index is off.
    """
    indexed = _position_state.index_open_positions_for_symbol(symbol)
    if indexed is not None:
        return indexed
    generation = _position_state.get_write_generation()
    now = _clock()
    with _positions_cache_lock:
        cached = _positions_cache.get(symbol)
        if (
            cached is not None
            and cached.generation == generation
            and (now - cached.fetched_at) < _QUERY_CACHE_MAX_TTL_S
        ):
            return cached.positions
    # Cold path — generation moved, TTL expired, or first call for symbol.
    positions = _query_open_positions(symbol)
    with _positions_cache_lock:
        _positions_cache[symbol] = _SymbolPositionsCache(
            generation=generation, positions=positions, fetched_at=now
        )
    return positions


def _default_order_placer_factory(
    firebase_uid: str,
) -> _order_placer.OrderPlacer:
    return _order_placer.OrderPlacer(firebase_uid)


# ---------------------------------------------------------------------------
# Mark-price-triggered break-even SL shift
# ---------------------------------------------------------------------------


async def maybe_fire_be_shift(
    position: _position_state.Position,
    *,
    mark_price: float,
    placer: _order_placer.OrderPlacer,
) -> None:
    """If mark price has moved BE_SHIFT_TRIGGER_PCT% in our favour, cancel
    the original SL and place a new STOP_MARKET at the entry price.

    Guards:
    - ``be_shift_fired`` — already shifted on a prior tick.
    - ``sl_order_id == 0`` — original SL already gone (pre-TP fired, or
      manually canceled); nothing to shift.
    - ``pretp_fired`` — pre-TP owns the BE shift for that path; don't
      double-shift.  (Belt-and-suspenders: PRE_TP_FIRED positions are also
      filtered out of the OPEN-state query.)

    After firing:
    - ``sl_order_id`` is zeroed.
    - ``sl_be_order_id`` and ``sl_price`` reflect the new BE stop.
    - ``be_shift_fired = True`` prevents re-entry on subsequent ticks.
    - ``put_position`` bumps the write-generation, which invalidates the
      symbol-positions cache so the updated object is used next tick.
    """
    if position.be_shift_fired:
        return
    if position.pretp_fired:
        return
    if position.sl_order_id == 0:
        return

    entry = position.entry_price_filled if position.entry_price_filled > 0 else position.entry_price_target
    if entry <= 0:
        return

    if position.side == "LONG":
        move_pct = (mark_price - entry) / entry * 100.0
    else:
        move_pct = (entry - mark_price) / entry * 100.0

    # Noise-aware arm (ACTIVE 2026-07-07, shared be_policy): the placed stop
    # already carries any noise-floor widening, so 1R of the position's own
    # stop distance IS the noise-aware threshold. Falls back to the legacy
    # flat trigger when the stop distance is unknown.
    _sl_dist_pct = 0.0
    if position.sl_price and position.sl_price > 0:
        _sl_dist_pct = abs(position.sl_price - entry) / entry * 100.0
    # TP1 cap (2026-07-10, mirrors trade_monitor): the arm must stay
    # reachable below the position's own first target — 1R of a noise-
    # widened stop could sit at/above TP1, making the BE shift dead code.
    _tp1_dist_pct = 0.0
    _tp1 = float(getattr(position, "tp1_price", 0.0) or 0.0)
    if _tp1 > 0:
        _tp1_dist_pct = abs(_tp1 - entry) / entry * 100.0
    _arm_pct = _be_policy.arm_threshold_pct(_sl_dist_pct, 0.0, _tp1_dist_pct)
    if not _be_policy.be_enabled(True) or move_pct < max(
        _arm_pct, _BE_SHIFT_TRIGGER_PCT
    ):
        return

    # Mark price crossed the trigger threshold — shift the stop to entry.
    log.info(
        "be_shift: triggering uid={} signal_id={} symbol={} side={} "
        "entry={} mark={} move_pct={:.3f}",
        position.firebase_uid, position.signal_id, position.symbol,
        position.side, entry, mark_price, move_pct,
    )
    try:
        await placer.cancel_algo_order(
            symbol=position.symbol,
            algo_id=position.sl_order_id,
        )
    except _order_placer.OrderPlacementError as exc:
        log.warning(
            "be_shift: original SL cancel failed uid={} signal_id={} exc={}",
            position.firebase_uid, position.signal_id, exc,
        )
    old_sl_order_id = position.sl_order_id
    position.sl_order_id = 0

    # Park the armed stop a tolerance on the LOSS side of entry (shared
    # be_policy) — an exact-entry wick no longer scratches the position.
    _park_price = _be_policy.park_price(entry, position.side == "LONG")
    try:
        sl_be = await placer.place_stop_loss(
            signal_id=position.signal_id,
            symbol=position.symbol,
            direction=position.side,
            stop_price=_park_price,
            coid_override=_position_state.coid_sl_be(position.signal_id),
        )
        position.sl_be_order_id = sl_be.order_id
        position.sl_price = _park_price
        position.be_shift_fired = True
        _position_state.put_position(position)
        log.info(
            "be_shift: placed BE-SL uid={} signal_id={} be_order_id={} "
            "canceled_sl_order_id={}",
            position.firebase_uid, position.signal_id,
            sl_be.order_id, old_sl_order_id,
        )
    except _order_placer.OrderPlacementError as exc:
        log.error(
            "be_shift: BE-SL placement FAILED uid={} signal_id={} exc={} — "
            "position has no stop; FSM reconciler will detect and force-close",
            position.firebase_uid, position.signal_id, exc,
        )
        # Do NOT set be_shift_fired — let next tick retry the placement.
        # The original SL was already canceled; if the retry also fails the
        # reconciler will catch the naked position and close it.
