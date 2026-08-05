"""Live aggressive-trade store, fed from ``@aggTrade``.

Phase 2a of ``docs/PRICE_ACTION_PROGRAM.md``. The engine has had a complete
``trade`` event handler, a tick store, a rolling cap, five consumers and gate
telemetry since before this module — and **no subscription**. There are exactly
three ``.start()`` calls in ``bootstrap.py`` (klines, forceOrder, ``!ticker@arr``)
and none is a trade stream, so ``HistoricalDataStore.ticks`` has always held
whatever ``/fapi/v1/trades?limit=1000`` returned at seed time and nothing since.

Five call sites read it as live, including a ``$500k cumulative tick volume``
gate. An absent input rejects loudly; a stale one returns plausible numbers of
the right shape, which is why this survived.

Why a second store and not a fix in place
-----------------------------------------
Because five live consumers read the old one. Switching what they see in the
same deploy that makes it fresh would change money-path behaviour with no
measurement behind it — a gate that has been reading seed-time trades for
months must not silently start reading current ones. So the live series lands
**here**, under its own key, both are stamped, ops renders the disagreement,
and ``TICKS_LIVE_FOR_CONSUMERS`` is the flag that hands the consumers over once
the disagreement has been read. Measurement ON, effect OFF — § Project Phase.

Why ``@aggTrade`` rather than ``@trade``
----------------------------------------
``aggTrade`` collapses every fill of one taker order into a single message. That
is both lower volume and the semantically correct unit: a sweep filled across
fifty resting orders is **one** aggressive act, not fifty. Both streams carry
``m`` (buyer is maker), so the aggressor split is exact either way — this is not
a tick-rule inference.

Hot-path cost
-------------
``HistoricalDataStore.append_tick`` appends to a list and re-slices it whenever
it passes the cap — O(n) per message on a 1,000-element list. That is free at
its actual call volume (zero) and would be a real cost at aggTrade volume, which
runs to thousands of messages a second across the book. This store uses a
``deque(maxlen=…)``: eviction is O(1), the memory ceiling is fixed per symbol,
and the handler allocates one small dict per message and nothing else. No
logging, no locking, no async hop on the message path.
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional

from src.utils import get_logger

log = get_logger("live_ticks")

#: Per-symbol ring depth. Matched to ``SEED_TICK_LIMIT`` so the live series and
#: the seeded one are directly comparable — a disagreement between them must be
#: about the data, never about how much of it each side kept.
DEFAULT_MAXLEN = 1_000

#: A symbol with no aggTrade in this long is treated as not-currently-fed.
#: Deliberately generous: an illiquid perp can genuinely go a minute without a
#: single aggressive trade, and calling that "stale" would report a fault that
#: is not happening. The distinction this store must draw is *subscribed and
#: quiet* versus *not arriving at all*, and only the second is actionable.
QUIET_AFTER_S = 90.0


@dataclass
class SymbolTicks:
    """One symbol's live aggressive trades."""

    ticks: Deque[Dict[str, Any]] = field(default_factory=lambda: deque(maxlen=DEFAULT_MAXLEN))
    #: Wall-clock of the most recent message we accepted.
    last_msg_at: float = 0.0
    #: Total accepted since process start — not bounded by the ring, so a
    #: symbol whose ring has fully rotated still reports its true throughput.
    total: int = 0
    #: Messages rejected because their payload could not be read. Counted
    #: rather than swallowed: a shape change at the vendor would otherwise
    #: present as a quiet feed, which is the wrong diagnosis entirely.
    rejected: int = 0


class LiveTickStore:
    """Bounded, per-symbol ring of aggressive trades with its own health view.

    Not a drop-in replacement for the seeded store and deliberately not shaped
    like one — the consumers keep reading what they read until the handover
    flag is flipped, and this store's job until then is to be *measurable*.
    """

    def __init__(self, maxlen: int = DEFAULT_MAXLEN) -> None:
        self._maxlen = int(maxlen)
        self._by_symbol: Dict[str, SymbolTicks] = {}
        #: Symbols we have subscribed for. Held separately from
        #: ``_by_symbol`` because "subscribed and silent" and "never
        #: subscribed" are different states, and a dict keyed on arrival
        #: cannot tell them apart — the second has no key at all.
        self._subscribed: set[str] = set()
        self._started_at = time.time()

    # ── ingestion ─────────────────────────────────────────────────────────
    def note_subscribed(self, symbols: List[str]) -> None:
        for s in symbols:
            self._subscribed.add(str(s).upper())

    def add(self, symbol: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fold one ``@aggTrade`` message in.

        Returns the **normalised row** on success and ``None`` on a rejected
        payload. The row is returned rather than a bool so the footprint store
        can consume the same parse — the read loop handles thousands of these
        a second and parsing each message twice to feed two stores is waste
        that grows with the universe.

        Called once per message on the WebSocket read loop, so it does the
        minimum: one dict, one deque append. A malformed payload is counted and
        dropped rather than raised — raising here would kill the read loop for
        every symbol on the connection, and the failure is already visible as a
        rejection count.
        """
        sym = str(symbol).upper()
        slot = self._by_symbol.get(sym)
        if slot is None:
            slot = SymbolTicks(ticks=deque(maxlen=self._maxlen))
            self._by_symbol[sym] = slot
        try:
            price = float(payload["p"])
            qty = float(payload["q"])
            # ``m`` is "buyer is the market maker" — so m=True means the
            # AGGRESSOR was the seller. Stored as the aggressor side rather
            # than the raw flag, because every consumer wants the aggressor
            # and re-deriving it at each call site is how a sign convention
            # gets inverted on half the book.
            is_buyer_maker = bool(payload.get("m", False))
            ts = float(payload.get("T", 0) or 0)
        except (KeyError, TypeError, ValueError):
            slot.rejected += 1
            return None

        row = {
            "price": price,
            "qty": qty,
            "quote": price * qty,
            "aggressor": "SELL" if is_buyer_maker else "BUY",
            # Kept under the same key the legacy store uses so a consumer
            # reading either series does not need two field names.
            "isBuyerMaker": is_buyer_maker,
            "time": ts,
        }
        slot.ticks.append(row)
        slot.total += 1
        slot.last_msg_at = time.time()
        return row

    # ── reads ─────────────────────────────────────────────────────────────
    def recent(self, symbol: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Newest-last list for *symbol*, or ``[]`` when nothing has arrived.

        Returns a plain list because every consumer of the legacy store expects
        one and slicing a deque does not work; the copy is bounded by the ring.
        """
        slot = self._by_symbol.get(str(symbol).upper())
        if slot is None:
            return []
        rows = list(slot.ticks)
        return rows[-limit:] if limit else rows

    def is_fed(self, symbol: str) -> bool:
        """Whether this symbol is currently receiving trades.

        Three states collapse to two here on purpose, and the third is
        available from :meth:`health`: never-subscribed and subscribed-but-
        silent both answer False, because a consumer asking "can I use the live
        series" needs one answer. A *reader* diagnosing why gets the split.
        """
        slot = self._by_symbol.get(str(symbol).upper())
        if slot is None or slot.last_msg_at == 0.0:
            return False
        return (time.time() - slot.last_msg_at) <= QUIET_AFTER_S

    # ── health ────────────────────────────────────────────────────────────
    def health(self) -> Dict[str, Any]:
        """What the feed is doing, in the three states that matter.

        ``subscribed_silent`` is the one worth having: a symbol we asked for
        and have never heard from is a subscription that did not take, and it
        is invisible in any count keyed on arrival.
        """
        now = time.time()
        fed: List[str] = []
        quiet: List[str] = []
        for sym, slot in self._by_symbol.items():
            if slot.last_msg_at and (now - slot.last_msg_at) <= QUIET_AFTER_S:
                fed.append(sym)
            else:
                quiet.append(sym)
        never = sorted(self._subscribed - set(self._by_symbol))
        return {
            "subscribed": len(self._subscribed),
            "fed": len(fed),
            "quiet": len(quiet),
            "subscribed_silent": len(never),
            "subscribed_silent_sample": never[:10],
            "quiet_sample": sorted(quiet)[:10],
            "rows": sum(len(s.ticks) for s in self._by_symbol.values()),
            "total_accepted": sum(s.total for s in self._by_symbol.values()),
            "total_rejected": sum(s.rejected for s in self._by_symbol.values()),
            "uptime_s": round(now - self._started_at, 1),
            "maxlen": self._maxlen,
            "quiet_after_s": QUIET_AFTER_S,
        }

    def compare_with_seeded(
        self, seeded: Dict[str, Any], *, sample: int = 50,
    ) -> Dict[str, Any]:
        """How far the seeded store has drifted from the live one.

        This is the measurement the handover flag is waiting on. The seeded
        store is a snapshot from whenever each symbol was seeded, so the gap
        is not noise — it is exactly the error every consumer currently
        carries, and it is reported per symbol in **age** rather than as a
        price difference, because the consumers use these rows for volume and
        recency, not for a mark.
        """
        now = time.time()
        gaps: List[Dict[str, Any]] = []
        for sym in list(self._by_symbol)[:sample]:
            live_rows = self._by_symbol[sym].ticks
            if not live_rows:
                continue
            seed_rows = (seeded or {}).get(sym) or []
            if not seed_rows:
                continue
            try:
                seed_newest = float(seed_rows[-1].get("time", 0) or 0)
                live_newest = float(live_rows[-1].get("time", 0) or 0)
            except (AttributeError, TypeError, ValueError):
                continue
            if seed_newest <= 0 or live_newest <= 0:
                continue
            gaps.append({
                "symbol": sym,
                "seeded_age_s": round(max(0.0, now - seed_newest / 1000.0), 1),
                "live_age_s": round(max(0.0, now - live_newest / 1000.0), 1),
                "gap_s": round(max(0.0, (live_newest - seed_newest) / 1000.0), 1),
            })
        gaps.sort(key=lambda g: -g["gap_s"])
        median_gap = (
            sorted(g["gap_s"] for g in gaps)[len(gaps) // 2] if gaps else None
        )
        return {
            "compared": len(gaps),
            "median_gap_s": median_gap,
            "worst": gaps[:10],
        }


_store: Optional[LiveTickStore] = None


def get_store() -> LiveTickStore:
    global _store
    if _store is None:
        _store = LiveTickStore()
    return _store


def reset_store(store: Optional[LiveTickStore] = None) -> None:
    """Test hook. Returns before any side effect when given nothing."""
    global _store
    _store = store


def resolve_recent_ticks(store: Any, symbol: str) -> tuple[List[Dict[str, Any]], str]:
    """Trades for *symbol*, with the **source that produced them**.

    The one seam both tick series are read through. Deliberately a module-level
    function taking the store rather than a method on it: the choice is
    *between* two stores, so it belongs to neither — and a method would have
    forced every existing collaborator fake to grow a new return shape, which
    is how a test ends up asserting an invented contract back at itself.

    ``store.ticks`` is a one-shot ``/fapi/v1/trades?limit=1000`` snapshot taken
    at seed time and never refreshed, because nothing ever subscribed a trade
    stream to feed ``append_tick``. Five call sites read it as live, including
    a ``$500k cumulative tick volume`` gate, and none could tell: an absent
    input rejects loudly, a stale one returns plausible numbers of the right
    shape.

    Returning the source alongside the rows is the point. Returning the rows
    alone would rebuild the exact ambiguity this function exists to remove.

    The handover is gated on ``TICKS_LIVE_FOR_CONSUMERS`` (default OFF): the
    live feed being healthy is not on its own a reason to change what a
    money-path gate sees. Sources:

    ``live``            the aggTrade series, currently being fed
    ``seed_snapshot``   the REST snapshot — stale by construction
    ``none``            neither has rows for this symbol
    """
    from config import TICKS_LIVE_FOR_CONSUMERS

    if TICKS_LIVE_FOR_CONSUMERS:
        live = get_store()
        # ``is_fed`` rather than "has any rows": a symbol whose stream stopped
        # an hour ago still has a full ring, and handing that back as ``live``
        # would be the same stale-but-plausible defect one store over.
        if live.is_fed(symbol):
            rows = live.recent(symbol)
            if rows:
                return rows, "live"

    seeded = getattr(store, "ticks", None) or {}
    try:
        rows = seeded.get(symbol) or []
    except AttributeError:
        return [], "none"
    if rows:
        return list(rows), "seed_snapshot"
    return [], "none"
