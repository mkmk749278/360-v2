"""Per-``(setup_class, side)`` verdict on the **delivered** book, standing.

Why this exists
---------------

The 2026-08-13 retirements (`src/path_retirement.py`) were decided off exactly
this analysis — n, distinct symbols, net %, a symbol-clustered 95% interval,
and the one bucket whose interval excluded zero — and it was run **by hand,
once**. Nothing in either repo has computed it since, so between then and now
the only per-path number anywhere was an unqualified mean on a page.

That gap became expensive on 2026-08-30, when the same-direction and
per-channel caps came off so every path could reach the feed rather than
`MOVER_TREND_PULLBACK` holding the slots by arithmetic. It worked — MVRTP's
share of the delivered book fell 76% → 59% and every other path is running
3–7x its old delivery rate. Over the ten days that followed, the delivered
book also went from **+0.506%/trade** (310 trades, 21 days) to
**−0.113%/trade** (374 trades, 10 days).

Three explanations were tested against the delivered export and **all three
refuted**, which is why this module publishes evidence rather than a gate:

* *The marginal same-direction entries are the loss.* The removed cap created
  a "3+ same-direction already open" bucket — 177 rows, 47% of the book — at
  −0.108%, no worse than the "2 open" bucket (−0.173%) that existed while the
  cap was on.
* *More volume means worse signals.* Pearson r between a day's MVRTP count and
  that day's mean net is **+0.177** over 31 days: if anything the busy days
  are the better ones.
* *It is the newly-unblocked paths.* They are negative in aggregate, but MVRTP
  — never suppressed, never the marginal path — carries −20.6% of a −42.2%
  book on its own.

So the owner's question, *"we need to produce good signals from every path"*,
cannot be answered by naming paths today. On the ten days since diversification
there are 1–37 delivered trades per cell and **not one interval excludes zero**
except a three-trade cell out of eighteen drawn. This module is what turns that
into a decision when the evidence arrives, instead of another hand-run query.

The sample floor is applied BEFORE the interval
-----------------------------------------------

This is the one design decision worth arguing, because the naive ordering
produces exactly the mistake this repo has already paid for. Ranked by mean,
the worst cell in the current window is ``MA_CROSS_TREND_SHIFT:LONG`` — three
trades, three symbols, −3.830%, interval **[−5.567, −2.873]**, which excludes
zero and looks decisive. It is `FAILED_AUCTION_RECLAIM`'s +0.846R with the
sign flipped: a cell that thin, drawn from eighteen, says nothing about the
path and everything about three bad days.

A cell under the floor is therefore ``INSUFFICIENT`` **whatever its interval
does** — the interval is still published, because hiding it would leave a
reader wondering, but it cannot produce a verdict. And ``cells_drawn`` rides
on every payload: "best of N" is not a fact about the winner until N is on
screen, and here the winner is a path somebody might retire.

What it does not do
-------------------

Nothing. No gate reads this, no candidate is suppressed by it, and it names
retirement candidates rather than retiring them — `path_retirement` is the
arming surface and it is the owner's, exactly as it was in August.

Two honesty properties it has to carry:

* **A retired cell's delivered evidence is FROZEN, not zero.** Retirement
  diverts to the dark lane, so a retired path stops producing delivered rows
  the moment it is armed. Its n stops growing and its verdict stops being a
  reading about today. That is stamped per cell rather than left for a reader
  to infer, because a stale verdict and a fresh one look identical in a table.
* **The window is bounded by AGE, never by count.** A count-bounded ring on a
  low-volume path holds evidence from whenever that path last emitted, which
  on a retired or throttled path is unboundedly old — the `cohort_edge`
  absorbing state arriving through the denominator instead of through the gate.

Cost: no I/O of its own. It reads the rows `performance_tracker` already holds
in memory and is called only from the diagnostic channel, never from a loop.
"""
from __future__ import annotations

import time
import zlib
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import numpy as np

#: Rows younger than this are the window. Age, never count — see the module
#: docstring. 30 days is the same window `/track-record` leads with, so a
#: reader moving between them is looking at the same book.
DEFAULT_WINDOW_DAYS = 30.0

#: Binance USD-M maker in + taker out, the rate `/track-record` defaults to.
#: Published as a parameter on every payload rather than folded in silently:
#: a net figure whose fee nobody can see is a gross figure with a caption.
DEFAULT_FEE_PCT = 0.07

#: The floor a cell must clear before its interval may produce a verdict.
#: Both bounds matter and they answer different failures: ``MIN_TRADES``
#: against a handful of outcomes, ``MIN_SYMBOLS`` against one instrument's
#: week wearing a path's name.
MIN_TRADES = 25
MIN_SYMBOLS = 12

#: Resamples. Enough that the interval is stable to ~0.01% between reads at
#: this book size, cheap enough to run every one of ~20 cells on demand.
BOOTSTRAP_ITERS = 4000

#: Fixed, and published on the payload. Two reads of an unchanged ledger must
#: return the same interval — a reader comparing a panel against the one he
#: opened an hour ago cannot tell resampling noise from the book moving.
BOOTSTRAP_SEED = 20260908

VERDICT_EARNS = "EARNS"
VERDICT_LOSES = "LOSES"
VERDICT_UNDECIDED = "UNDECIDED"
VERDICT_INSUFFICIENT = "INSUFFICIENT"


def _f(value: Any) -> Optional[float]:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if out == out else None  # NaN is not a reading


def _cell_seed(seed: int, setup: str, side: str) -> int:
    """A per-cell seed that is stable ACROSS PROCESSES.

    ``hash()`` on a str is salted per interpreter unless ``PYTHONHASHSEED`` is
    pinned, so seeding from it would move every published interval on each
    restart — noise a reader cannot tell from the book changing, in the one
    column a retirement decision is read from. CRC32 is not a hash function
    for security purposes and is not being used as one; it is here because it
    is deterministic and in the standard library.
    """
    return (seed + zlib.crc32(f"{setup}:{side}".encode())) % (2 ** 31)


def _cluster_ci(
    by_symbol: Dict[str, List[float]],
    *,
    iters: int,
    seed: int,
) -> Tuple[Optional[float], Optional[float]]:
    """Percentile 95% interval, resampling SYMBOLS rather than trades.

    Overlapping entries into one instrument's move are not independent
    evidence — they resolve at correlated prices and a trade-level bootstrap
    treats them as if they were, which narrows the interval toward whatever
    that instrument did. Resampling the cluster is the same correction the
    August retirement analysis used, and it is why ``symbols`` is published
    beside ``n`` rather than behind it.

    Vectorised, and that is not a micro-optimisation. `diag_catalog.run`
    executes **synchronously on the snapshot writer's event loop** — the
    engine's own loop, whose achieved period sets the governor's staleness
    floor and whose snapshot keys carry a 60s TTL. The obvious implementation
    (rebuild the pooled list once per resample) measured **0.475s** at 2,000
    in-window rows and grows with the book: a half-second stall on the loop a
    43-MB serialisation already cost 1.85s of. Resampling the per-symbol SUMS
    and COUNTS is arithmetically identical to concatenating the picks — the
    mean of a cluster resample is the total of the picked sums over the total
    of the picked counts — and turns the inner loop into two array reductions.

    Deterministic across processes and numpy versions: PCG64 with an explicit
    seed, which is the whole reason the seed is published on the payload.
    """
    symbols = sorted(by_symbol)
    if len(symbols) < 2:
        return None, None
    sums = np.array([sum(by_symbol[s]) for s in symbols], dtype=np.float64)
    counts = np.array([len(by_symbol[s]) for s in symbols], dtype=np.float64)
    size = len(symbols)
    rng = np.random.default_rng(seed)
    picks = rng.integers(0, size, size=(iters, size))
    totals = sums[picks].sum(axis=1)
    n_total = counts[picks].sum(axis=1)
    # A resample can only be empty if every cluster is, which cannot happen —
    # a symbol is only a key here because it carries at least one trade.
    means = np.sort(totals / n_total)
    lo = float(means[int(0.025 * iters)])
    hi = float(means[min(int(0.975 * iters), iters - 1)])
    return round(lo, 4), round(hi, 4)


def _verdict(
    *,
    n: int,
    symbols: int,
    ci_low: Optional[float],
    ci_high: Optional[float],
    min_trades: int,
    min_symbols: int,
) -> Tuple[str, str]:
    """Floor first, interval second. Returns ``(verdict, why)``.

    The ordering IS the guard — see the module docstring. A thin cell whose
    interval excludes zero returns ``INSUFFICIENT`` and says which bound it
    failed, so the reader is told the cell is unready rather than left to
    notice that ``n`` is small underneath a confident-looking interval.
    """
    if n < min_trades or symbols < min_symbols:
        short = []
        if n < min_trades:
            short.append(f"{n}/{min_trades} trades")
        if symbols < min_symbols:
            short.append(f"{symbols}/{min_symbols} symbols")
        return VERDICT_INSUFFICIENT, "below the sample floor: " + ", ".join(short)
    if ci_low is None or ci_high is None:
        return VERDICT_INSUFFICIENT, "interval not computable"
    if ci_high < 0.0:
        return VERDICT_LOSES, "symbol-clustered 95% interval excludes zero, below it"
    if ci_low > 0.0:
        return VERDICT_EARNS, "symbol-clustered 95% interval excludes zero, above it"
    return VERDICT_UNDECIDED, "interval spans zero"


def _retired_lookup() -> Tuple[Set[Tuple[str, str]], Set[str], bool, Optional[str]]:
    """What `path_retirement` currently diverts, and whether it is acting.

    Read through that module's own ``snapshot()`` rather than its internals —
    one writer, one reader, the rule this repo has re-learned under several
    names. Imported lazily and behind a guard: this module is a reader and
    must not be the reason a diagnostic read fails.

    A retirement list we could not consult is returned with its error and an
    EMPTY map, and the caller publishes the error beside the cells. It must
    never be allowed to read as "nothing is retired": that would render every
    frozen cell as a live one, which is the flattering direction — a stale
    verdict presented as a current reading about a path somebody may act on.
    """
    try:
        from src import path_retirement

        snap = path_retirement.snapshot()
        if snap.get("error"):
            return set(), set(), False, str(snap["error"])
        pairs: Set[Tuple[str, str]] = set()
        wildcards: Set[str] = set()
        for item in snap.get("retired") or ():
            setup = str(item.get("setup_class") or "").upper()
            side = str(item.get("side") or "").upper()
            if not setup:
                continue
            # The wildcard is EXPANDED here, where the module that owns it is
            # already imported, so nothing downstream needs to know the token.
            # An unguarded second import of the same module is how a reader
            # takes down the read it was supposed to be reporting on.
            if side == path_retirement.ANY_SIDE:
                wildcards.add(setup)
            else:
                pairs.add((setup, side))
        return pairs, wildcards, bool(snap.get("enabled")), None
    except Exception as exc:  # pragma: no cover - defensive
        return set(), set(), False, f"{type(exc).__name__}: {exc}"


def _is_retired(
    pairs: Set[Tuple[str, str]], wildcards: Set[str], setup: str, side: str
) -> bool:
    return setup in wildcards or (setup, side) in pairs


def summarise(
    rows: Iterable[Dict[str, Any]],
    *,
    now: Optional[float] = None,
    window_days: float = DEFAULT_WINDOW_DAYS,
    fee_pct: float = DEFAULT_FEE_PCT,
    min_trades: int = MIN_TRADES,
    min_symbols: int = MIN_SYMBOLS,
    iters: int = BOOTSTRAP_ITERS,
    seed: int = BOOTSTRAP_SEED,
) -> Dict[str, Any]:
    """Grade every ``(setup_class, side)`` cell of the delivered book.

    ``rows`` are `performance_tracker.SignalRecord` dicts — the closed-signal
    record, which `trade_monitor` writes at the terminal transition and which
    already carries the correct denominators. No resolver of this module's
    own: every measurement lane in this repo that grew one paid for it in a
    later session, and the outcome needed here is already recorded by
    something that owns it.
    """
    now = float(now if now is not None else time.time())
    cutoff = now - window_days * 86400.0
    fee = float(fee_pct)

    retired_pairs, retired_all, retirement_acting, retirement_error = _retired_lookup()

    considered = 0
    undated = 0
    no_pnl = 0
    cells: Dict[Tuple[str, str], Dict[str, List[float]]] = {}

    for row in rows:
        considered += 1
        closed = _f(row.get("terminal_outcome_timestamp"))
        if closed is None:
            # Undated rather than old: a row with no terminal stamp cannot be
            # placed in or out of the window, and dropping it silently would
            # shrink the denominator by an unknown amount.
            undated += 1
            continue
        if closed < cutoff:
            continue
        pnl = _f(row.get("pnl_pct"))
        if pnl is None:
            no_pnl += 1
            continue
        setup = str(row.get("setup_class") or "").upper() or "UNCLASSIFIED"
        side = str(row.get("direction") or "").upper() or "UNKNOWN"
        symbol = str(row.get("symbol") or "") or "UNKNOWN"
        cells.setdefault((setup, side), {}).setdefault(symbol, []).append(pnl - fee)

    graded: List[Dict[str, Any]] = []
    for (setup, side), by_symbol in cells.items():
        vals = [v for group in by_symbol.values() for v in group]
        n = len(vals)
        mean = sum(vals) / n
        wins = sum(1 for v in vals if v > 0.0)
        lo, hi = _cluster_ci(by_symbol, iters=iters, seed=_cell_seed(seed, setup, side))
        verdict, why = _verdict(
            n=n,
            symbols=len(by_symbol),
            ci_low=lo,
            ci_high=hi,
            min_trades=min_trades,
            min_symbols=min_symbols,
        )
        frozen = _is_retired(retired_pairs, retired_all, setup, side)
        graded.append(
            {
                "setup_class": setup,
                "side": side,
                "n": n,
                "symbols": len(by_symbol),
                "net_avg_pct": round(mean, 4),
                "gross_avg_pct": round(mean + fee, 4),
                "net_total_pct": round(sum(vals), 3),
                "win_rate": round(wins / n, 4),
                "ci_low": lo,
                "ci_high": hi,
                "verdict": verdict,
                "verdict_why": why,
                # Frozen, not zero: a retired path stops producing delivered
                # rows, so this cell's evidence stopped accumulating when it
                # was armed and its verdict is a reading about then.
                "delivered_evidence_frozen": frozen,
            }
        )

    graded.sort(key=lambda c: c["net_avg_pct"])
    decidable = [c for c in graded if c["verdict"] in (VERDICT_LOSES, VERDICT_EARNS)]
    candidates = [
        c
        for c in graded
        if c["verdict"] == VERDICT_LOSES and not c["delivered_evidence_frozen"]
    ]

    return {
        "window_days": window_days,
        "generated_at": now,
        "cells": graded,
        # "Best of N" is not a fact about the winner until N is on screen, and
        # here the winner is a path somebody might retire.
        "cells_drawn": len(graded),
        "cells_decidable": len(decidable),
        "retirement_candidates": [
            {"setup_class": c["setup_class"], "side": c["side"], "n": c["n"],
             "net_avg_pct": c["net_avg_pct"], "ci_high": c["ci_high"]}
            for c in candidates
        ],
        "already_retired": [
            {"setup_class": st, "side": sd}
            for (st, sd) in sorted(
                list(retired_pairs) + [(w, "*") for w in retired_all]
            )
        ],
        "retirement_acting": retirement_acting,
        "retirement_error": retirement_error,
        "floor": {"min_trades": min_trades, "min_symbols": min_symbols},
        "fee_pct": fee,
        "bootstrap": {"iters": iters, "seed": seed, "cluster": "symbol"},
        "coverage": {
            "records_considered": considered,
            "in_window": sum(c["n"] for c in graded),
            "undated": undated,
            "no_pnl": no_pnl,
        },
    }
