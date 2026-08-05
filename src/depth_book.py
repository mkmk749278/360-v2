"""Live order-book depth, fed from ``@depth<N>@<speed>ms``.

Phase 2c of ``docs/PRICE_ACTION_PROGRAM.md``. Phase 2a/2b answered *who is
aggressive* — aggTrade is executed aggression, and the footprint puts it at a
price. This answers the other half: *who is resting*. Neither substitutes for
the other, which is why they are separate phases and separate rollbacks.

What we had instead
-------------------
``scanner._fetch_global_book_tickers`` builds the order book from
``/fapi/v1/ticker/bookTicker`` — **one** bid and **one** ask::

    {"bids": [[best_bid, qty]], "asks": [[best_ask, qty]],
     "source": "book_ticker", "depth_quality": "top_of_book_only"}

That was the right call for a spread check and ``binance.py`` says so. It is
not a book, and the snapshot is honest about it: it carries its own
``depth_quality`` badge. What makes it worth a phase is that **four consumers
were written for a book and have been reading one quote**:

* ``order_book.check_order_book_execution`` — the final execution gate in
  ``risk.calculate_risk``, whose own ``OBI_DEFAULT_LEVELS`` is **20**. It has
  been summing ``bids[:20]`` over a list of length one for its whole life.
* ``entry_features.book_imbalance`` — sums ``bids[:10]`` / ``asks[:10]``.
* ``channels/scalp.py``'s WHALE path — the only consumer that *noticed*: it
  checks for ``depth_quality == "top_of_book_only"`` and applies a 10-point
  penalty rather than trusting the number.
* ``ai_engine/predictor.py`` — weights ``order_book`` at 0.25 of its score.

None of them was broken in the sense of raising. A one-level book returns a
perfectly well-formed imbalance; it just cannot see a wall, a refill, or
absorption, because the quantity at the touch is not the quantity behind it.

Why the partial-depth stream and not the diff stream
----------------------------------------------------
``@depth`` (the diff stream) is the one that gives a *full* book, and it costs
a REST snapshot plus sequence reconciliation: every message carries ``U`` /
``u`` / ``pu``, and a consumer must chain them, detect a gap, and resynchronise
from ``/fapi/v1/depth`` when the chain breaks. A local book that misses that
resync **does not fail** — it drifts, and keeps answering with confident,
well-shaped, wrong numbers. That is the exact failure class this program was
written against, and it would be self-inflicted.

``@depth<N>@<speed>`` sends a complete top-N **snapshot** every interval. A
dropped message costs one interval of staleness and cannot corrupt anything,
because the next message replaces the state wholesale rather than amending it.
We need the top of the book, not all of it — every consumer above reads 10 or
20 levels — so the stream that cannot desync is strictly the better trade.

Why silence is a fault here and is not one for aggTrade
--------------------------------------------------------
``live_ticks.QUIET_AFTER_S`` is 90 seconds because an illiquid perp can
genuinely go a minute without a single aggressive trade — *subscribed and
quiet* is a market fact there. Depth is different in kind: the stream is on a
**fixed clock** and publishes whether or not anything traded, so a symbol with
no depth message is not a quiet market, it is a feed that stopped. The
threshold is therefore tight and derived from the configured speed rather than
guessed (:func:`stale_after_s`).

Cost
----
One snapshot per symbol, **replaced** rather than accumulated: memory is
``symbols x levels x 2`` floats and does not grow with time. The handler
allocates two lists per message and returns — no logging, no locking, no async
hop. At 500ms x 40 symbols that is 80 messages/sec, against aggTrade's
thousands. WebSocket market streams cost no REQUEST_WEIGHT at any rate, so the
bound here is our own read loop, and the whole-universe decision comes from the
measured rate on ``/diagnostics/data-intake`` rather than from this docstring.

Dark-first
----------
``DEPTH_STREAM_ENABLED`` is the measurement flag and defaults ON.
``DEPTH_LIVE_FOR_CONSUMERS`` is the effect flag and defaults OFF — the four
consumers keep reading the one-level book until the measured disagreement has
been read and signed off. Handing a live execution gate a twenty-fold wider
input in the same deploy that first produces it is exactly what § Project Phase
forbids, and the OBI gate is the *final* filter before dispatch.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from src.utils import get_logger

log = get_logger("depth_book")

#: Levels requested from Binance. The vendor offers 5 / 10 / 20 for the partial
#: book stream and nothing between, so this is a choice from a fixed menu, not a
#: tunable. 20 because ``order_book.OBI_DEFAULT_LEVELS`` is 20 — the consumer
#: that already declares a depth is the one that should set it.
DEFAULT_LEVELS = 20

#: Update speed in ms. The vendor offers 100 / 250 / 500.
#:
#: 500 is the default deliberately, against the program document's own
#: ``@depth20@100ms``. Every consumer of this book reads it at **scan cadence**
#: (15s) or at dispatch, so a 100ms book is ~150x fresher than the fastest thing
#: that will ever look at it and costs 5x the messages to be so. If a later
#: phase grows a consumer that reads between scans, this is one env var.
DEFAULT_SPEED_MS = 500

#: Speeds the vendor actually serves. A value outside this set produces a
#: subscription that silently never delivers, which reads exactly like a dead
#: feed — so it is rejected at construction instead.
VALID_SPEEDS_MS = (100, 250, 500)

#: Levels the vendor actually serves, same reasoning.
VALID_LEVELS = (5, 10, 20)


def stale_after_s(speed_ms: int = DEFAULT_SPEED_MS) -> float:
    """How long without a message before a symbol's book is a fault.

    Derived from the stream's own clock rather than picked: at ``speed_ms`` the
    vendor publishes unconditionally, so twenty missed intervals is not a quiet
    market under any interpretation. Floored at 5s so that a fast speed cannot
    produce a threshold tight enough to fire on ordinary scheduling jitter.
    """
    return max(5.0, (speed_ms / 1000.0) * 20.0)


@dataclass
class DepthSnapshot:
    """One symbol's most recent top-N book. Replaced, never amended."""

    #: Highest price first, as the vendor sends it.
    bids: List[Tuple[float, float]] = field(default_factory=list)
    #: Lowest price first.
    asks: List[Tuple[float, float]] = field(default_factory=list)
    #: Vendor event time (ms). Their clock, for measuring our lag against it.
    event_ms: int = 0
    #: Our monotonic receive time, for measuring staleness without trusting
    #: either clock's absolute value or their agreement.
    recv_at: float = 0.0

    @property
    def levels(self) -> int:
        """Levels actually held, which is ``min(bids, asks)`` and may be under
        the requested depth on a thin book. Reported, never assumed."""
        return min(len(self.bids), len(self.asks))

    def best_bid(self) -> Optional[float]:
        return self.bids[0][0] if self.bids else None

    def best_ask(self) -> Optional[float]:
        return self.asks[0][0] if self.asks else None

    def notional(self, levels: int) -> Optional[Tuple[float, float, int]]:
        """``(bid_notional, ask_notional, levels_used)`` over the top *levels*.

        Notional (price x qty), because that is what three of the four
        consumers already use and mixing units across a handover would make the
        disagreement unreadable.

        ``None`` when either side is empty — a missing book is not a balanced
        one. ``levels_used`` is returned rather than assumed: a book that holds
        3 levels answers over 3 and **says 3**, because a 3-level number
        labelled 20 is the kind of quiet mislabelling this lane exists to stop.
        """
        if not self.bids or not self.asks or levels <= 0:
            return None
        b = sum(p * q for p, q in self.bids[:levels])
        a = sum(p * q for p, q in self.asks[:levels])
        if b <= 0 or a <= 0:
            return None
        used = min(levels, len(self.bids), len(self.asks))
        return b, a, used

    def imbalance(self, levels: int) -> Optional[float]:
        """``(bids - asks) / (bids + asks)`` in [-1, 1], positive favours bid.

        Same sign convention as ``entry_features.book_imbalance`` so the two are
        directly comparable; that function's caller signs it toward the trade.
        """
        n = self.notional(levels)
        if n is None:
            return None
        b, a, _ = n
        return (b - a) / (b + a)

    def as_order_book(self, *, stale: bool = False) -> Dict[str, Any]:
        """The shape existing consumers already read.

        ``depth_quality`` is the field the WHALE path branches on, so it must
        name what this actually is. It reports the levels **held**, not the
        levels requested.
        """
        return {
            "bids": [[p, q] for p, q in self.bids],
            "asks": [[p, q] for p, q in self.asks],
            "source": "depth_stream",
            "depth_quality": f"top_{self.levels}" if not stale else "stale",
            "levels": self.levels,
            "event_ms": self.event_ms,
        }


@dataclass
class SymbolDepthState:
    """Per-symbol book plus the counters that grade it."""

    snapshot: Optional[DepthSnapshot] = None
    #: Total accepted since process start — unbounded by the single-snapshot
    #: store, so throughput stays visible even though state does not accumulate.
    total: int = 0
    #: Messages whose payload could not be read. Counted rather than swallowed:
    #: a vendor shape change would otherwise present as a quiet feed, which is
    #: the wrong diagnosis and sends the next session to the wrong subsystem.
    rejected: int = 0
    #: Set when the symbol is subscribed, so "never delivered" is separable
    #: from "not subscribed". Without it an unsubscribed symbol and a broken
    #: one are the same empty row.
    subscribed_at: float = 0.0


class DepthBookStore:
    """Bounded per-symbol top-N books with their own health view.

    Deliberately **not** a drop-in for the bookTicker snapshot. The consumers
    keep reading what they read until ``DEPTH_LIVE_FOR_CONSUMERS`` is flipped,
    and this store's only job until then is to be measurable beside them.
    """

    def __init__(
        self,
        *,
        levels: int = DEFAULT_LEVELS,
        speed_ms: int = DEFAULT_SPEED_MS,
    ) -> None:
        if levels not in VALID_LEVELS:
            raise ValueError(
                f"depth levels {levels} is not one of {VALID_LEVELS}; the vendor "
                "serves only those and any other value subscribes a stream that "
                "never delivers"
            )
        if speed_ms not in VALID_SPEEDS_MS:
            raise ValueError(
                f"depth speed {speed_ms}ms is not one of {VALID_SPEEDS_MS}; the "
                "vendor serves only those and any other value subscribes a "
                "stream that never delivers"
            )
        self.levels = levels
        self.speed_ms = speed_ms
        self._stale_after = stale_after_s(speed_ms)
        self._by_symbol: Dict[str, SymbolDepthState] = {}

    # ── hot path ──────────────────────────────────────────────────────────
    def update(self, symbol: str, payload: Dict[str, Any]) -> Optional[DepthSnapshot]:
        """Fold one ``depthUpdate`` message in. Runs once per message.

        Returns the stored snapshot, or ``None`` when the payload was
        unreadable — in which case the rejection is counted, never logged: this
        is a per-message path and a vendor shape change would turn a log line
        into a flood that costs more than the fault.
        """
        if not symbol:
            return None
        st = self._by_symbol.get(symbol)
        if st is None:
            st = self._by_symbol[symbol] = SymbolDepthState()

        raw_bids = payload.get("b")
        raw_asks = payload.get("a")
        if not isinstance(raw_bids, list) or not isinstance(raw_asks, list):
            st.rejected += 1
            return None

        try:
            bids = [(float(lv[0]), float(lv[1])) for lv in raw_bids]
            asks = [(float(lv[0]), float(lv[1])) for lv in raw_asks]
        except (IndexError, TypeError, ValueError):
            st.rejected += 1
            return None

        # A level at zero quantity is a delete in the diff protocol. The partial
        # stream should not carry them, but dropping them costs one comparison
        # and keeping one would understate a side by a phantom empty level.
        bids = [lv for lv in bids if lv[1] > 0]
        asks = [lv for lv in asks if lv[1] > 0]
        if not bids or not asks:
            st.rejected += 1
            return None

        try:
            event_ms = int(payload.get("E") or 0)
        except (TypeError, ValueError):
            event_ms = 0

        snap = DepthSnapshot(
            bids=bids, asks=asks, event_ms=event_ms, recv_at=time.monotonic()
        )
        st.snapshot = snap
        st.total += 1
        return snap

    def note_subscribed(self, symbols: Any) -> None:
        """Record that these symbols were subscribed.

        Called from the subscription site so that a symbol which never delivers
        is distinguishable from one that was never asked for.
        """
        now = time.monotonic()
        for sym in symbols or []:
            s = str(sym).upper()
            st = self._by_symbol.get(s)
            if st is None:
                st = self._by_symbol[s] = SymbolDepthState()
            if not st.subscribed_at:
                st.subscribed_at = now

    # ── reads ─────────────────────────────────────────────────────────────
    def is_stale(self, symbol: str, *, now: Optional[float] = None) -> bool:
        st = self._by_symbol.get(symbol)
        if st is None or st.snapshot is None:
            return True
        return ((now or time.monotonic()) - st.snapshot.recv_at) > self._stale_after

    def get(self, symbol: str, *, allow_stale: bool = False) -> Optional[DepthSnapshot]:
        """The symbol's book, or ``None`` when absent or stale.

        Stale is refused rather than returned with a flag, because every
        consumer of this reads it to make a decision and a stale book is not a
        degraded answer — it is a book that describes a market that has moved.
        """
        st = self._by_symbol.get(symbol)
        if st is None or st.snapshot is None:
            return None
        if not allow_stale and self.is_stale(symbol):
            return None
        return st.snapshot

    def order_book(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Consumer-shaped book, or ``None`` — the handover's read side."""
        snap = self.get(symbol)
        return None if snap is None else snap.as_order_book()

    def comparison(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Top-of-book against full depth, on the *same* snapshot.

        This is the measurement the whole phase turns on, and the reason it
        reads both from one snapshot is that a comparison across two sources
        would be measuring the sources' timing as much as their depth.

        ``imb_top1`` is what a one-level book can say — arithmetically what the
        bookTicker snapshot yields, computed here from the same message so the
        two differ **only** in depth. ``imb_topN`` is what the book says. Their
        gap is the answer to "does depth change the picture", and it is a
        distribution to be read, never a threshold to be invented now.
        """
        snap = self.get(symbol)
        if snap is None:
            return None
        top1 = snap.imbalance(1)
        topn = snap.imbalance(self.levels)
        if top1 is None or topn is None:
            return None
        n = snap.notional(self.levels)
        return {
            "symbol": symbol,
            "imb_top1": top1,
            "imb_topn": topn,
            "delta": topn - top1,
            # Sign flip is the case that matters to a directional consumer: the
            # touch says one side and the book says the other. Counted apart
            # from magnitude, because a consumer comparing against a threshold
            # and one comparing against zero are harmed by different things.
            "sign_flip": (top1 > 0) != (topn > 0),
            "levels_used": n[2] if n else 0,
            "levels_held": snap.levels,
        }

    def health(self) -> Dict[str, Any]:
        """Fleet-wide view, rendered whether or not anything is wrong.

        Every count keeps its denominator. A stale *fraction* over a shrinking
        population reads healthy while the population disappears, which is the
        failure this panel exists to make visible.
        """
        now = time.monotonic()
        subscribed = 0
        delivering = 0
        stale = 0
        never = 0
        total = 0
        rejected = 0
        thin = 0
        oldest_age: Optional[float] = None
        stale_symbols: List[str] = []
        never_symbols: List[str] = []

        for sym, st in self._by_symbol.items():
            if st.subscribed_at:
                subscribed += 1
            total += st.total
            rejected += st.rejected
            if st.snapshot is None:
                never += 1
                if len(never_symbols) < 10:
                    never_symbols.append(sym)
                continue
            age = now - st.snapshot.recv_at
            if oldest_age is None or age > oldest_age:
                oldest_age = age
            if age > self._stale_after:
                stale += 1
                if len(stale_symbols) < 10:
                    stale_symbols.append(sym)
            else:
                delivering += 1
            # A book holding fewer levels than requested is a thin market, not
            # a fault — but it bounds what every consumer can see, so it is
            # counted rather than left to be inferred from a healthy row.
            if st.snapshot.levels < self.levels:
                thin += 1

        return {
            "levels": self.levels,
            "speed_ms": self.speed_ms,
            "stale_after_s": self._stale_after,
            "symbols_known": len(self._by_symbol),
            "symbols_subscribed": subscribed,
            "delivering": delivering,
            "stale": stale,
            "never_delivered": never,
            "thin_books": thin,
            "messages_total": total,
            "messages_rejected": rejected,
            "oldest_book_age_s": oldest_age,
            "stale_symbols": stale_symbols,
            "never_symbols": never_symbols,
        }

    def comparison_census(self, *, limit: int = 200) -> Dict[str, Any]:
        """The disagreement across every live book.

        The population is the books that are **fresh**, because a stale book's
        disagreement is a fact about the feed rather than about depth.
        """
        rows: List[Dict[str, Any]] = []
        for sym in list(self._by_symbol.keys())[:limit]:
            row = self.comparison(sym)
            if row is not None:
                rows.append(row)
        if not rows:
            return {"n": 0, "rows": [], "sign_flips": 0, "mean_abs_delta": None}
        flips = sum(1 for r in rows if r["sign_flip"])
        mean_abs = sum(abs(r["delta"]) for r in rows) / len(rows)
        rows.sort(key=lambda r: abs(r["delta"]), reverse=True)
        return {
            "n": len(rows),
            "sign_flips": flips,
            "mean_abs_delta": mean_abs,
            "rows": rows[:25],
        }


_store: Optional[DepthBookStore] = None


def get_store() -> DepthBookStore:
    """Process-wide store. Built on first use from config."""
    global _store
    if _store is None:
        from config import DEPTH_STREAM_LEVELS, DEPTH_STREAM_SPEED_MS
        _store = DepthBookStore(
            levels=DEPTH_STREAM_LEVELS, speed_ms=DEPTH_STREAM_SPEED_MS
        )
    return _store


def reset_store() -> None:
    """Test hook. Never called in production."""
    global _store
    _store = None
