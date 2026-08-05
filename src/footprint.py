"""Per-bar, per-price volume — the confirmation layer.

Phase 2b of ``docs/PRICE_ACTION_PROGRAM.md``, built on the ``@aggTrade`` feed
Phase 2a opened. This is the layer the published evidence actually supports:
round-number/swing stop clustering and **signed order imbalance** are the two
components with peer-reviewed backing, and imbalance is the one we could not
see at all.

What we had, and why it is not this
-----------------------------------
``OrderFlowStore`` computes CVD from the closed kline's ``Q``/``q`` fields —
**one signed number per bar**. That answers "were takers net buying this
minute" and is structurally silent on *where in the bar* they were buying,
whether a level absorbed them, or how the aggression was sized. A bar that
grinds up on steady small buying and a bar that spikes into a wall and fails
produce the same delta.

This store keeps buy and sell volume **at each price**, which is what turns
that single number into a shape.

Magnitudes, never verdicts
--------------------------
Nothing here emits ``absorption=True``. Every derived value is a **ratio or a
magnitude** — imbalance ratio, volume at the point of control, range covered,
size distribution — because a boolean bakes in a threshold, and a threshold
chosen now would be chosen from no data at all. Phases 4 and 5 pick thresholds
from measured distributions; this phase's job is to make the distribution
exist. "Does its threshold come from code that already exists, or from this
window?" — here the honest answer is neither, so there is no threshold.

Bins are relative, and their width is stamped
---------------------------------------------
Price bins are a fraction of the bar's own opening price, not an absolute grid.
``find_round_numbers`` steps by 0.01 below $1 — 1% at $1 and **20% at $0.05** —
and is inert across much of a book dominated by sub-dollar movers. A footprint
on an absolute grid would have the same defect and would be far less visible:
every sub-dollar symbol would collapse into one or two bins and read as
perfectly balanced. ``bin_bps`` rides on every bar so a reader can see the
granularity behind a shape rather than inferring it.

Bounded by construction
-----------------------
Fixed bar ring per symbol, fixed bin cap per bar. A bar that would exceed its
bin cap **stops binning and says so** (``bins_capped``) rather than silently
widening or dropping trades — its totals stay exact, only its shape is refused.
Refuse the claim, not the measurement.

Incomplete is a state, not a small number
-----------------------------------------
If the feed drops mid-bar, that bar's volume is a fraction of the truth while
looking exactly like a quiet bar. Any bar whose symbol had a feed gap while it
was open is stamped ``incomplete`` with the reason, and every consumer is
expected to exclude it rather than average it in. A partial bar rendered as a
whole one is the fabrication class arriving as a shape.
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional, Tuple

from src.utils import get_logger

log = get_logger("footprint")

#: Bar length. 1m is the base grid — higher timeframes aggregate from it, and
#: aggregating up is lossless while splitting down is not.
BAR_MS = 60_000

#: Price-bin width, in basis points of the bar's opening price. 5bps puts ~40
#: bins across a 0.2% bar, which resolves a wall without turning a quiet bar
#: into one bin per trade.
DEFAULT_BIN_BPS = 5.0

#: Bars retained per symbol. 120 = two hours at 1m — enough for a rolling
#: volume baseline and for any consumer looking back over a setup's formation.
DEFAULT_BARS = 120

#: Hard cap on bins in one bar. A bar spanning more than this many bins is a
#: violent move; its totals stay exact and its shape is refused rather than
#: allowed to grow without bound.
MAX_BINS_PER_BAR = 400

#: Aggressive-trade size buckets, in quote (USD) terms. Fixed edges so the
#: distribution is comparable across symbols and across time — a percentile
#: basis would move under its own data and make two days incomparable.
SIZE_BUCKET_EDGES: Tuple[float, ...] = (100.0, 1_000.0, 10_000.0, 100_000.0)
SIZE_BUCKET_LABELS: Tuple[str, ...] = ("<100", "100-1k", "1k-10k", "10k-100k", ">100k")


def bar_open_ms(ts_ms: float) -> int:
    """The 1m bar containing *ts_ms*, as its open time in ms."""
    return int(ts_ms // BAR_MS * BAR_MS)


@dataclass
class BarFootprint:
    """One symbol, one minute, volume split by price and by aggressor."""

    bar_open: int
    bin_bps: float
    #: Reference price the bins are measured from — the first trade of the bar.
    #: Stored so a bin index can be turned back into a price by any reader
    #: without guessing which price the grid was anchored to.
    anchor: float = 0.0
    #: bin index -> [buy_quote, sell_quote]. Quote (USD) rather than base
    #: quantity so bars are comparable across symbols at different prices.
    bins: Dict[int, List[float]] = field(default_factory=dict)
    buy_quote: float = 0.0
    sell_quote: float = 0.0
    trades: int = 0
    high: float = 0.0
    low: float = 0.0
    first_price: float = 0.0
    last_price: float = 0.0
    size_buckets: List[int] = field(
        default_factory=lambda: [0] * len(SIZE_BUCKET_LABELS)
    )
    #: True once the bar spanned more than MAX_BINS_PER_BAR. Totals remain
    #: exact; the per-price shape stops being complete and says so.
    bins_capped: bool = False
    #: Set when the feed for this symbol was interrupted while this bar was
    #: open. The bar's volume is then a fraction of the truth while looking
    #: exactly like a quiet bar, so it carries its cause rather than a number.
    incomplete_reason: str = ""

    # ── derived, computed on read ────────────────────────────────────────
    @property
    def delta_quote(self) -> float:
        """Signed aggressive volume. The thing CVD is a running sum of."""
        return self.buy_quote - self.sell_quote

    @property
    def total_quote(self) -> float:
        return self.buy_quote + self.sell_quote

    @property
    def incomplete(self) -> bool:
        return bool(self.incomplete_reason)

    @property
    def range_pct(self) -> Optional[float]:
        """High-low range as a percent of the anchor.

        Half of what "absorption" means — volume that moved price a long way
        and volume that moved it nowhere are different events with the same
        total. Published as a component, never folded into a score.
        """
        if not self.anchor or self.high <= 0 or self.low <= 0:
            return None
        return (self.high - self.low) / self.anchor * 100.0

    def poc(self) -> Optional[Tuple[int, float]]:
        """(bin index, total quote) of the most-traded price in the bar.

        The point of control — auction theory's "magnet", and the price a
        reader wants first when asking where the bar's business was done.
        """
        if not self.bins:
            return None
        idx = max(self.bins, key=lambda k: self.bins[k][0] + self.bins[k][1])
        row = self.bins[idx]
        return idx, row[0] + row[1]

    def max_imbalance(self, *, min_quote: float = 0.0) -> Optional[Dict[str, Any]]:
        """The most one-sided price level in the bar.

        Returns the **ratio**, not a verdict: "3:1 buy at this price" is data,
        "imbalanced" is a threshold nobody has earned yet.

        ``min_quote`` exists because a level with $12 of one-sided volume has a
        spectacular ratio and means nothing; the floor is the caller's to set
        and is reported back so a reader knows what was excluded.
        """
        best: Optional[Dict[str, Any]] = None
        for idx, (buy, sell) in self.bins.items():
            total = buy + sell
            if total < min_quote:
                continue
            # A level with zero on one side is a true infinity, not a large
            # number — reported as such rather than divided by an epsilon,
            # which would manufacture a finite ratio out of an absent one.
            if buy > 0 and sell > 0:
                ratio = max(buy / sell, sell / buy)
                one_sided = False
            else:
                ratio = float("inf")
                one_sided = True
            if best is None or ratio > best["ratio"]:
                best = {
                    "bin": idx,
                    "price": self.price_of_bin(idx),
                    "ratio": ratio,
                    "one_sided": one_sided,
                    "side": "BUY" if buy >= sell else "SELL",
                    "quote": total,
                }
        if best is not None:
            best["min_quote_floor"] = min_quote
        return best

    def price_of_bin(self, idx: int) -> Optional[float]:
        if not self.anchor:
            return None
        return self.anchor * (1.0 + idx * self.bin_bps / 10_000.0)

    def as_dict(self) -> Dict[str, Any]:
        poc = self.poc()
        return {
            "bar_open": self.bar_open,
            "bin_bps": self.bin_bps,
            "anchor": self.anchor,
            "buy_quote": round(self.buy_quote, 2),
            "sell_quote": round(self.sell_quote, 2),
            "delta_quote": round(self.delta_quote, 2),
            "total_quote": round(self.total_quote, 2),
            "trades": self.trades,
            "bins": len(self.bins),
            "bins_capped": self.bins_capped,
            "incomplete": self.incomplete,
            "incomplete_reason": self.incomplete_reason,
            "range_pct": (round(self.range_pct, 4)
                          if self.range_pct is not None else None),
            "poc_price": self.price_of_bin(poc[0]) if poc else None,
            "poc_quote": round(poc[1], 2) if poc else None,
            "size_buckets": dict(zip(SIZE_BUCKET_LABELS, self.size_buckets)),
        }


class FootprintStore:
    """Per-symbol ring of 1m footprints.

    Fed from the same ``@aggTrade`` message as the live tick store, from the
    already-parsed row, so the WebSocket read loop parses each message once.
    """

    def __init__(
        self,
        *,
        bars: int = DEFAULT_BARS,
        bin_bps: float = DEFAULT_BIN_BPS,
        max_bins: int = MAX_BINS_PER_BAR,
    ) -> None:
        self._bars = int(bars)
        self._bin_bps = float(bin_bps)
        self._max_bins = int(max_bins)
        self._by_symbol: Dict[str, Deque[BarFootprint]] = {}
        self._open_bar: Dict[str, BarFootprint] = {}
        self._started_at = time.time()
        #: Bars whose shape was refused for exceeding the bin cap. Counted
        #: because a silent cap would make a violent bar read as a narrow one.
        self.capped_bars = 0
        #: Bars marked incomplete by a feed gap.
        self.incomplete_bars = 0

    # ── ingestion ─────────────────────────────────────────────────────────
    def add_row(self, symbol: str, row: Dict[str, Any]) -> bool:
        """Fold one **already-parsed** aggressive trade in.

        Takes the normalised row rather than the raw payload so the message is
        parsed exactly once on the read loop; the two stores share one parse.
        """
        try:
            price = float(row["price"])
            quote = float(row["quote"])
            ts = float(row.get("time") or 0)
            is_buy = row.get("aggressor") == "BUY"
        except (KeyError, TypeError, ValueError):
            return False
        if price <= 0 or ts <= 0:
            return False

        sym = str(symbol).upper()
        open_ms = bar_open_ms(ts)
        bar = self._open_bar.get(sym)
        if bar is None or bar.bar_open != open_ms:
            if bar is not None and bar.bar_open < open_ms:
                self._seal(sym, bar)
            elif bar is not None:
                # A trade for a bar older than the open one. Out-of-order
                # delivery across a reconnect: dropped rather than folded into
                # the wrong bar, and the current bar is marked because its own
                # completeness is now in question.
                bar.incomplete_reason = bar.incomplete_reason or "out_of_order_trade"
                return False
            bar = BarFootprint(bar_open=open_ms, bin_bps=self._bin_bps, anchor=price)
            bar.first_price = price
            bar.high = price
            bar.low = price
            self._open_bar[sym] = bar

        bar.trades += 1
        bar.last_price = price
        if price > bar.high:
            bar.high = price
        if price < bar.low or bar.low <= 0:
            bar.low = price
        if is_buy:
            bar.buy_quote += quote
        else:
            bar.sell_quote += quote

        # Size distribution — "a large aggressive buyer" becomes a measurement
        # rather than a story only if the sizes are actually counted.
        b = 0
        for edge in SIZE_BUCKET_EDGES:
            if quote < edge:
                break
            b += 1
        bar.size_buckets[b] += 1

        # Bin index relative to the bar's anchor, so the grid is scale-free.
        idx = int(round((price / bar.anchor - 1.0) * 10_000.0 / self._bin_bps))
        slot = bar.bins.get(idx)
        if slot is None:
            if len(bar.bins) >= self._max_bins:
                if not bar.bins_capped:
                    bar.bins_capped = True
                    self.capped_bars += 1
                # Totals above are already updated and stay exact — only the
                # per-price shape stops here.
                return True
            slot = [0.0, 0.0]
            bar.bins[idx] = slot
        slot[0 if is_buy else 1] += quote
        return True

    def mark_gap(self, symbol: str, reason: str = "feed_gap") -> None:
        """Record that this symbol's feed was interrupted.

        The open bar's volume is now a fraction of the truth while looking
        exactly like a quiet bar, so it carries a cause. Called on reconnect,
        not inferred from silence — an illiquid symbol is legitimately quiet
        and inferring a gap from that would report one that never happened.
        """
        sym = str(symbol).upper()
        bar = self._open_bar.get(sym)
        if bar is not None and not bar.incomplete_reason:
            bar.incomplete_reason = reason
            self.incomplete_bars += 1

    def _seal(self, sym: str, bar: BarFootprint) -> None:
        ring = self._by_symbol.get(sym)
        if ring is None:
            ring = deque(maxlen=self._bars)
            self._by_symbol[sym] = ring
        ring.append(bar)

    # ── reads ─────────────────────────────────────────────────────────────
    def bars(self, symbol: str, limit: Optional[int] = None) -> List[BarFootprint]:
        """Sealed bars, oldest first. The open bar is deliberately excluded —
        a bar still being filled is not comparable with a finished one, and
        including it would make every "latest bar" read low."""
        ring = self._by_symbol.get(str(symbol).upper())
        rows = list(ring) if ring else []
        return rows[-limit:] if limit else rows

    def open_bar(self, symbol: str) -> Optional[BarFootprint]:
        return self._open_bar.get(str(symbol).upper())

    def cvd_quote(self, symbol: str, bars: int = 60) -> Optional[float]:
        """Tick-derived cumulative delta over the last *bars* sealed bars.

        This is a **second computation** of a quantity ``OrderFlowStore``
        already produces from kline taker fields — and a second computation is
        a detector, not a duplicate, provided it never overwrites the first.
        It does not: this lives under its own key, and the disagreement between
        the two is what the liveness probe watches.

        Incomplete bars are excluded rather than summed. A partial bar's delta
        is a fraction of the truth, and a cumulative sum is exactly where that
        error stops being visible.
        """
        rows = [b for b in self.bars(symbol, bars) if not b.incomplete]
        if not rows:
            return None
        return sum(b.delta_quote for b in rows)

    def volume_baseline(self, symbol: str, bars: int = 30) -> Optional[float]:
        """Median total quote volume per bar — the reference an "exhaustion" or
        "expansion" reading needs. Median rather than mean: one liquidation
        cascade sets a mean nothing else can approach."""
        rows = [b.total_quote for b in self.bars(symbol, bars) if not b.incomplete]
        if not rows:
            return None
        rows.sort()
        return rows[len(rows) // 2]

    def health(self) -> Dict[str, Any]:
        sealed = sum(len(r) for r in self._by_symbol.values())
        bins = sum(len(b.bins) for r in self._by_symbol.values() for b in r)
        incomplete = sum(
            1 for r in self._by_symbol.values() for b in r if b.incomplete
        )
        return {
            "symbols": len(self._by_symbol),
            "open_bars": len(self._open_bar),
            "sealed_bars": sealed,
            "bins_held": bins,
            "incomplete_bars_held": incomplete,
            "capped_bars_total": self.capped_bars,
            "incomplete_bars_total": self.incomplete_bars,
            "bar_ms": BAR_MS,
            "bin_bps": self._bin_bps,
            "bars_per_symbol": self._bars,
            "max_bins_per_bar": self._max_bins,
            "uptime_s": round(time.time() - self._started_at, 1),
        }

    def sample(self, symbol: str) -> Optional[Dict[str, Any]]:
        """The newest sealed bar for *symbol*, rendered — so the ops page can
        show a real footprint rather than only a row count."""
        rows = self.bars(symbol, 1)
        if not rows:
            return None
        bar = rows[-1]
        out = bar.as_dict()
        out["symbol"] = str(symbol).upper()
        imb = bar.max_imbalance()
        out["max_imbalance"] = imb
        if imb is not None and imb["ratio"] == float("inf"):
            # JSON has no infinity. Rendered as its own state rather than as a
            # large number, because "no opposing volume at all" is a different
            # observation from "a big ratio".
            out["max_imbalance"] = {**imb, "ratio": None, "one_sided": True}
        out["cvd_quote_60"] = self.cvd_quote(symbol, 60)
        out["volume_baseline_30"] = self.volume_baseline(symbol, 30)
        return out


_store: Optional[FootprintStore] = None


def get_store() -> FootprintStore:
    global _store
    if _store is None:
        _store = FootprintStore()
    return _store


def reset_store(store: Optional[FootprintStore] = None) -> None:
    """Test hook. Returns before any side effect when given nothing."""
    global _store
    _store = store
