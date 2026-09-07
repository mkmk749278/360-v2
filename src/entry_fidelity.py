"""Entry fidelity — the gap between the entry we stamp and the price that existed.

Every number this engine publishes about a trade divides by ``Signal.entry``:
``pnl_pct``, MFE, MAE, R, the app's signal card, ``/track-record``, the edge
matrix and every dark lane. ``entry`` is the close of the candle the evaluator
triggered on. The order goes out a few seconds later, and on a continuation or
momentum setup price has usually kept moving in the signal's direction over
those seconds. So the stamped entry is systematically BETTER than the price
that was actually available, and the difference is booked as profit.

Measured 2026-09-07 against Binance's own USD-M 1m tape
(``data.binance.vision``), 605 of the 652 delivered rows closed in the 30 days
to 2026-09-06 reconstructed bar by bar:

* mean drift **+0.226%**, median **+0.162%**, and the market had already moved
  WITH the trade by dispatch on **67%** of rows — a bias, not noise.
* the recorded book reads **+0.342% / trade (+207.1% total)**; scored from the
  price on the tape at dispatch it is **+0.118% / trade (+71.1% total)**, or
  **+0.048%** net of a 0.07% round trip.
* ``+0.342 − 0.226 = +0.116`` against a measured ``+0.118``. The arithmetic
  closes to two thousandths of a percent: the entire gap between the book and
  reality is this drift, and there is nothing else in it.
* on **9%** of stop-outs price never traded at the stamped entry after dispatch
  at all. Every one of those rows carries ``max_favorable_excursion_pct ==
  0.0``, because an excursion measured from a price that never existed cannot
  be anything else.

Robust to the fill assumption: pricing the fill at the dispatch minute's open,
its close, or the next bar's open gives +0.129% / +0.119% / +0.119%. Spread and
slippage are NOT modelled, so the rebased figure is if anything optimistic.

**This module changes no order and no gate.** It stamps what the monitor first
observed and does the arithmetic; the rebased book is published BESIDE the
recorded one and never replaces it (owner, 2026-09-07). Whether to *act* on the
gap is a separate, unpriced question — and one obvious action was measured and
withdrawn the same day: refusing signals whose mark had already moved >0.5%
past the stamped entry drops 11% of rows carrying **−91.4% of book PnL** and
**+20.0% of real PnL**. It would have thrown away money while every ops page
showed a triumph. Nothing here is a gate.

The direction convention is fixed once, here, because a signed feature split
the wrong way scores every SHORT backwards and reads exactly like noise:
**positive drift means the market had already moved in the TRADE's favour.**
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence

__all__ = [
    "REFUSAL_NO_ENTRY",
    "REFUSAL_NO_OBSERVATION",
    "REFUSAL_STALE_OBSERVATION",
    "Rebased",
    "signed_drift_pct",
    "implied_exit_price",
    "rebased_pnl_pct",
    "rebase",
    "record_fields",
    "summarise",
]

#: Refusal reasons. Named rather than pooled into one "no data", because the
#: operator's next move differs for each: a missing entry is a producer fault, a
#: missing observation is a monitor that never got a price, and a stale one is
#: the promoted-mover feed gap. Same rule the mover-admission census carries.
REFUSAL_NO_ENTRY = "no_entry"
REFUSAL_NO_OBSERVATION = "no_observation"
REFUSAL_STALE_OBSERVATION = "stale_observation"


def _is_long(direction: Any) -> bool:
    """True for a LONG, taking either a string or a Direction enum."""
    value = getattr(direction, "value", direction)
    return str(value).upper() == "LONG"


def signed_drift_pct(
    entry: float, observed: float, direction: Any
) -> Optional[float]:
    """Percent the market had already moved, **signed toward the trade**.

    Positive means price was already past the stamped entry in the direction
    the trade wanted — the move we booked but never had. Negative means the
    market sat on the losing side of the entry before we started.

    Returns ``None`` rather than 0.0 when either price is unusable: zero is a
    reading and this is the absence of one.
    """
    if not entry or entry <= 0 or not observed or observed <= 0:
        return None
    raw = (observed - entry) / entry * 100.0
    return raw if _is_long(direction) else -raw


def implied_exit_price(
    entry: float, pnl_pct: float, direction: Any
) -> Optional[float]:
    """Recover the exit LEVEL from a book row's entry and percentage.

    The exit is a real price — a stop, a target, a parked BE — so it survives
    rebasing untouched; only the entry is in question. This is what lets a
    historical record be re-scored without storing a second exit field.
    """
    if not entry or entry <= 0:
        return None
    factor = 1.0 + (pnl_pct / 100.0) if _is_long(direction) else 1.0 - (pnl_pct / 100.0)
    price = entry * factor
    return price if price > 0 else None


def rebased_pnl_pct(
    observed: float, exit_price: float, direction: Any
) -> Optional[float]:
    """PnL of the same exit measured from the price that actually existed."""
    if not observed or observed <= 0 or not exit_price or exit_price <= 0:
        return None
    raw = (exit_price - observed) / observed * 100.0
    return raw if _is_long(direction) else -raw


@dataclass(frozen=True)
class Rebased:
    """One row's recorded and rebased numbers, or a named refusal.

    ``refusal`` and the numbers are mutually exclusive by construction: a row
    either priced or said why it could not. A caller that reads ``drift_pct``
    without checking ``refusal`` gets ``None``, never a plausible zero.
    """

    refusal: Optional[str] = None
    drift_pct: Optional[float] = None
    book_pnl_pct: Optional[float] = None
    rebased_pnl_pct: Optional[float] = None
    observed_entry: Optional[float] = None
    exit_price: Optional[float] = None

    @property
    def ok(self) -> bool:
        return self.refusal is None


def rebase(
    *,
    entry: float,
    pnl_pct: float,
    direction: Any,
    observed_entry: Optional[float],
    observation_stale: bool = False,
    allow_stale: bool = False,
) -> Rebased:
    """Re-score one closed row from the observed price instead of the stamp.

    A stale observation is refused by default rather than used: the promoted-
    mover path serves a frozen candle close for symbols that have left the scan
    universe, and rebasing onto a frozen price would manufacture a drift that
    is a fact about our feed rather than about the market. ``allow_stale``
    exists so a surface can show the count it is refusing, never so it can
    quietly fold those rows into the total.
    """
    if not entry or entry <= 0:
        return Rebased(refusal=REFUSAL_NO_ENTRY)
    if not observed_entry or observed_entry <= 0:
        return Rebased(refusal=REFUSAL_NO_OBSERVATION)
    if observation_stale and not allow_stale:
        return Rebased(refusal=REFUSAL_STALE_OBSERVATION)
    exit_price = implied_exit_price(entry, pnl_pct, direction)
    drift = signed_drift_pct(entry, observed_entry, direction)
    rebased = (
        rebased_pnl_pct(observed_entry, exit_price, direction)
        if exit_price is not None
        else None
    )
    if exit_price is None or rebased is None or drift is None:
        return Rebased(refusal=REFUSAL_NO_ENTRY)
    return Rebased(
        drift_pct=drift,
        book_pnl_pct=float(pnl_pct),
        rebased_pnl_pct=rebased,
        observed_entry=float(observed_entry),
        exit_price=float(exit_price),
    )


def _median(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def summarise(rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Census over closed rows: coverage first, then the two books.

    ``rows`` are plain dicts so this serves the engine's own records and an
    ops-side replay of the same file without either side re-implementing the
    arithmetic — ops ports the engine's math, it does not invent it.

    Coverage leads because it is the number that decides whether the rest may
    be read at all: rows written before the stamp shipped carry no observation
    and are counted under their own refusal, never averaged in as zero drift.
    """
    priced: List[Rebased] = []
    refusals: Dict[str, int] = {}
    total = 0
    for row in rows:
        total += 1
        result = rebase(
            entry=float(row.get("entry") or 0.0),
            pnl_pct=float(row.get("pnl_pct") or 0.0),
            direction=row.get("direction") or "",
            observed_entry=row.get("first_observed_price"),
            observation_stale=bool(row.get("first_observed_stale") or False),
        )
        if result.ok:
            priced.append(result)
        else:
            refusals[result.refusal or "unknown"] = (
                refusals.get(result.refusal or "unknown", 0) + 1
            )
    n = len(priced)
    if not n:
        return {
            "rows": total,
            "priced": 0,
            "coverage_pct": 0.0,
            "refusals": refusals,
            "note": (
                "No row carries a first-observation stamp yet. Rows written "
                "before this shipped cannot be rebased and are not guesses — "
                "the window has to accumulate behind the stamp."
            ),
        }
    drifts = [r.drift_pct for r in priced if r.drift_pct is not None]
    book = [r.book_pnl_pct for r in priced if r.book_pnl_pct is not None]
    real = [r.rebased_pnl_pct for r in priced if r.rebased_pnl_pct is not None]
    return {
        "rows": total,
        "priced": n,
        "coverage_pct": round(100.0 * n / total, 1) if total else 0.0,
        "refusals": refusals,
        "drift_mean_pct": round(sum(drifts) / len(drifts), 4) if drifts else None,
        "drift_median_pct": (
            round(_median(drifts), 4) if _median(drifts) is not None else None
        ),
        "drift_positive_share_pct": (
            round(100.0 * sum(1 for d in drifts if d > 0) / len(drifts), 1)
            if drifts
            else None
        ),
        "book_avg_pct": round(sum(book) / len(book), 4) if book else None,
        "rebased_avg_pct": round(sum(real) / len(real), 4) if real else None,
        "book_total_pct": round(sum(book), 2) if book else None,
        "rebased_total_pct": round(sum(real), 2) if real else None,
    }


def _opt_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def record_fields(sig: Any) -> Dict[str, Any]:
    """The entry-fidelity kwargs for ``record_signal_outcome``, from a Signal.

    There are TWO terminal writers of the closed-signal record — the monitor's
    own path and the expiry path in ``main.py`` — and a field carried by one
    and not the other is populated on some rows and silently absent on others,
    which reads as missing data rather than as a missing writer. Deriving the
    shape once here means neither call site holds a hand-kept list, and
    ``tests/test_entry_fidelity.py`` pins that both of them splat this.
    """
    at = getattr(sig, "first_observed_at", None)
    observed_at: Optional[float] = None
    if at is not None:
        try:
            observed_at = float(at.timestamp())
        except (AttributeError, TypeError, ValueError, OSError):
            observed_at = None
    return {
        "first_observed_price": float(
            getattr(sig, "first_observed_price", 0.0) or 0.0
        ),
        "first_observed_at": observed_at,
        "first_observed_source": str(getattr(sig, "first_observed_source", "") or ""),
        "first_observed_stale": bool(getattr(sig, "first_observed_stale", False)),
        "peak_pnl_pct": _opt_float(getattr(sig, "peak_pnl_pct", None)),
        "trough_pnl_pct": _opt_float(getattr(sig, "trough_pnl_pct", None)),
    }
