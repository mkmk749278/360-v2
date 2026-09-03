"""Candidate levels the model may CHOOSE from — never levels it may invent.

`docs/PLAN_AI_TRADE_GOVERNOR.md` §5. This is the module that makes the whole
design safe, and it is a direct port of two properties this repo already relies
on:

* `trail_governor` *"computes nothing about SAR"* — the mechanism is
  deterministic and reconciled bit-exact against the exchange's own candles, and
  the governor answers only *"given that level, what order should exist right
  now"*.
* `diag_catalog` accepts a **key** selected from a registry, never a command —
  which is what made an ops-driven engine action admissible at all.

So the engine builds the candidate set and validates every member **before it is
offered**, and the model returns an index into it. A hallucinated float is
unbounded; a hallucinated key is bounded by a menu we wrote, is a counted
refusal, and is replayable — the same snapshot and the same menu can be
re-scored months later, which a free float never can.

Every candidate is signed toward the trade
------------------------------------------
`dist_pct` is positive when the level is in the direction the trade wants and
negative when it is behind. That is not cosmetic: `cvd_slope` and
`book_imbalance` shipped raw once and were split with a single "higher is
better" rule, which scored every SHORT backwards and made both features look
like noise for a month. A menu where "nearer" means the opposite thing on a
SHORT would be the same defect on the one path that moves real orders.

What is NOT here
----------------
No round-number generator. `structural_levels.find_round_numbers` steps by 0.01
below $1, which is 1% at $1 and **20% at $0.05**, and much of the delivered book
is sub-$1 movers — so on exactly the pairs this lane sees most, the round grid
cannot fall inside any plausible band. The snap lane records `round_step_pct`
and lets ops read an all-`swing` column as the grid being inert. Here the
levels become **orders**, so an inert generator is not worth the parse surface;
`swing` and the mechanical anchors are what is offered, and the source rides on
every candidate so a reader can see the mix rather than assume it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from src import fail_open
from src.structural_levels import find_swing_levels
from src.utils import get_logger

log = get_logger("ai_governor_menu")

#: Menu key prefixes. The model returns one of these strings and nothing else.
TP_PREFIX = "tp_"
SL_PREFIX = "sl_"

#: Candidate kinds, named so an all-`current` menu reads as "nothing structural
#: was on offer" rather than as the generator being broken.
KIND_CURRENT = "current"        # the level the position already has
KIND_SWING = "swing"            # a price the market traded and rejected
KIND_BREAKEVEN = "breakeven"    # the entry fill — mechanical, always available
KIND_LOCK = "lock"              # a fraction of the move already banked
#: A level from the engine's own Level Book — multi-timeframe S/R with touch
#: counts and a score, not a pivot this module found on the trigger series.
#: Offered BESIDE the swing candidates rather than instead of them: a 1h/4h/1d
#: level and a recent trigger-timeframe swing answer different questions, and
#: collapsing them would hide which source the model is actually choosing.
KIND_LEVEL = "level"

#: How many structural candidates to offer per side, beyond `current`. Small on
#: purpose: a menu of twelve invites twelve thresholds, and twelve cells against
#: a book this size guarantees a spurious winner (the entry-feature lesson).
MAX_STRUCTURAL = 2

#: Swing detection needs 2*window+1 bars to return anything at all; below this
#: the answer is "we could not look", which is a refusal and not an empty menu.
MIN_BARS = 20

#: Fractions of the open move offered as `lock` stops. Chosen mechanically
#: (they are the move, not a fitted threshold) so nothing here is a number this
#: window generated.
LOCK_FRACTIONS = (0.25, 0.5)

REFUSE_NO_SERIES = "no_series"
REFUSE_SHORT_SERIES = "short_series"
REFUSE_BAD_GEOMETRY = "bad_geometry"


@dataclass(frozen=True)
class Candidate:
    """One offer. ``price`` is what would actually be placed."""

    key: str
    kind: str
    price: float
    #: SIGNED TOWARD THE TRADE. For a TP, positive = further away (more
    #: ambitious); the menu only ever offers nearer ones, so every non-current
    #: TP candidate has a smaller value than `tp_0`. For an SL, positive =
    #: tighter (closer to entry, less risk at stake).
    dist_pct: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "kind": self.kind,
            "dist_pct": round(self.dist_pct, 4),
        }


@dataclass(frozen=True)
class Menu:
    """Both sides, plus why either is short.

    ``refusal`` is not an error: a position on a symbol whose candles stopped
    has no structural candidates and that is a fact worth counting, not an
    exception worth raising. The governor stamps it and moves on.
    """

    tp: Tuple[Candidate, ...]
    sl: Tuple[Candidate, ...]
    refusal: str = ""

    def lookup(self, key: str) -> Optional[Candidate]:
        """Resolve a key the model returned — **only** within this menu.

        A key from another position's menu resolves to None here by
        construction, because each menu is built per position and never shared.
        That is the cross-wire the governor's apply path refuses and counts.
        """
        for cand in self.tp + self.sl:
            if cand.key == key:
                return cand
        return None

    def as_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "tp_candidates": [c.as_dict() for c in self.tp],
            "sl_candidates": [c.as_dict() for c in self.sl],
        }
        if self.refusal:
            out["menu_refusal"] = self.refusal
        return out


def _pct_from(entry: float, price: float, is_long: bool) -> float:
    """Signed move from entry to price, in the trade's favour."""
    if entry <= 0:
        return 0.0
    raw = (price - entry) / entry * 100.0
    return raw if is_long else -raw


def build_menu(
    *,
    side: str,
    entry: float,
    current_sl: float,
    current_tp1: float,
    highs: Optional[Sequence[float]],
    lows: Optional[Sequence[float]],
    closes: Optional[Sequence[float]],
    last_price: float,
    round_price: Optional[Any] = None,
    book_levels: Optional[Sequence[Any]] = None,
) -> Menu:
    """Build both candidate sets, pre-validated.

    ``round_price`` is the symbol-filter rounder, injected rather than imported
    so the caller decides whether a level is exchange-legal. A candidate that
    cannot be placed must never be offered — the model choosing an unplaceable
    level would be *our* defect surfacing as its mistake.

    ``book_levels`` are `level_book.Level` objects — the engine's own
    multi-timeframe S/R, which this module was documented as reading and did
    not: v1's module map said it reads `level_book`, and it ran a private pivot
    scan over the raw high/low arrays instead. Fixed here, and offered
    **alongside** the pivots rather than replacing them, because a 1h/4h/1d
    level and a recent trigger-timeframe swing are different facts. Their
    fields are read **by name** off the real dataclass (`price`, `type`,
    `source_tf`, `score`) — a reader that guesses at several possible shapes is
    the `zone_distance_atr` defect, which was uncomputable from the day it
    shipped because no producer carried any of the five keys it tried.
    """

    is_long = str(side).upper() == "LONG"
    if entry <= 0 or current_sl <= 0 or current_tp1 <= 0:
        return Menu(tp=(), sl=(), refusal=REFUSE_BAD_GEOMETRY)

    rounder = round_price or (lambda price: price)

    def _mk(key: str, kind: str, price: float) -> Optional[Candidate]:
        try:
            px = float(rounder(price))
        except Exception as exc:  # noqa: BLE001
            fail_open.record("ai_governor_menu.round_price", exc)
            return None
        if not np.isfinite(px) or px <= 0:
            return None
        return Candidate(key=key, kind=kind, price=px,
                         dist_pct=_pct_from(entry, px, is_long))

    tp: List[Candidate] = []
    sl: List[Candidate] = []

    cur_tp = _mk(f"{TP_PREFIX}0", KIND_CURRENT, current_tp1)
    cur_sl = _mk(f"{SL_PREFIX}0", KIND_CURRENT, current_sl)
    if cur_tp is None or cur_sl is None:
        return Menu(tp=(), sl=(), refusal=REFUSE_BAD_GEOMETRY)
    tp.append(cur_tp)
    sl.append(cur_sl)

    # ── SL: mechanical candidates, always available ─────────────────────────
    # Breakeven and lock levels need no candle series, so a symbol whose
    # candles stopped still gets a usable SL menu. That matters because the
    # blind case is exactly when a governor is most likely to want out.
    be = _mk(f"{SL_PREFIX}be", KIND_BREAKEVEN, entry)
    if be is not None and _tightens(is_long, cur_sl.price, be.price):
        sl.append(be)

    if last_price > 0:
        move = _pct_from(entry, last_price, is_long)
        if move > 0:
            for i, frac in enumerate(LOCK_FRACTIONS, start=1):
                locked = entry * (1 + (move * frac / 100.0) * (1 if is_long else -1))
                cand = _mk(f"{SL_PREFIX}lock{i}", KIND_LOCK, locked)
                if cand is not None and _tightens(is_long, cur_sl.price, cand.price):
                    sl.append(cand)

    # ── Structural candidates, when the series supports them ────────────────
    refusal = ""
    series_ok = (
        highs is not None and lows is not None and closes is not None
        and len(closes) >= MIN_BARS
    )
    if highs is None or lows is None or closes is None:
        refusal = REFUSE_NO_SERIES
    elif len(closes) < MIN_BARS:
        refusal = REFUSE_SHORT_SERIES

    if series_ok:
        try:
            swings = find_swing_levels(
                np.asarray(highs, dtype=float),
                np.asarray(lows, dtype=float),
                np.asarray(closes, dtype=float),
            )
            tp.extend(_swing_tps(swings, is_long, entry, cur_tp, _mk))
            sl.extend(_swing_sls(swings, is_long, cur_sl, _mk))
        except Exception as exc:  # noqa: BLE001 — a menu is never worth a raise
            fail_open.record("ai_governor_menu.swings", exc)
            refusal = refusal or REFUSE_BAD_GEOMETRY

    # Level Book candidates, offered BESIDE the pivots above. Appended rather
    # than merged so the swing candidates keep their nearest-first order and
    # their keys, and so an all-`swing` menu reads as the Level Book being
    # empty for this symbol rather than as this module having ignored it.
    try:
        tp.extend(_book_tps(book_levels, is_long, entry, cur_tp, _mk, len(tp)))
        sl.extend(_book_sls(book_levels, is_long, cur_sl, _mk, len(sl)))
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor_menu.book_levels", exc)

    # ── The last gate: placeability ─────────────────────────────────────────
    # A stop already through the mark is not a tight stop, it is an order
    # Binance rejects (-2021, "order would immediately trigger"). Offering one
    # would make OUR defect surface as the model's mistake, so it is dropped
    # here rather than discovered at the placement.
    #
    # Note what this deliberately is NOT: a minimum-distance floor. That guard
    # belongs to the enqueue path, where the geometry is chosen and the
    # designed risk is known; re-applying it here would mean inventing a
    # fraction-of-risk threshold from nothing, and a bounded adjustment that
    # widens back to a floor books a stop nobody chose
    # (`structural_snap.REFUSE_MIN_DISTANCE`, the same reasoning from the other
    # side). What bounds this arm is monotonicity plus the apply-path budget.
    if last_price > 0:
        sl = [c for c in sl if c.kind == KIND_CURRENT or _protective(is_long, last_price, c.price)]

    return Menu(tp=tuple(tp), sl=tuple(sl), refusal=refusal)


def _protective(is_long: bool, last_price: float, stop: float) -> bool:
    """Would this stop still be resting, rather than already triggered?"""
    return stop < last_price if is_long else stop > last_price


def _tightens(is_long: bool, old: float, new: float) -> bool:
    """Is ``new`` a tighter stop than ``old``?  Mirrors `trail_governor.tightens`."""
    return new > old if is_long else new < old


def _swing_tps(swings: Dict[str, List[float]], is_long: bool, entry: float,
               current: Candidate, mk: Any) -> List[Candidate]:
    """Swing levels between price and the current TP — **nearer only**.

    Nearer-only is what makes this arm decidable from the record at all: a
    trade's `max_favorable_excursion_pct` settles whether a nearer target was
    reached, with no ordering ambiguity, because every recorded excursion
    precedes the close. Offering a FURTHER target would be a different trade,
    and nothing in the closed-signal record could score it.
    """
    pool = swings.get("swing_highs" if is_long else "swing_lows") or []
    out: List[Candidate] = []
    cur = current.dist_pct
    seen: List[float] = []
    # Nearest first: the model is choosing how much to give up, so the order it
    # reads should be the order of increasing concession.
    for level in sorted(pool, reverse=not is_long):
        d = _pct_from(entry, level, is_long)
        if d <= 0 or d >= cur:
            continue
        if any(abs(d - s) < 0.01 for s in seen):
            continue
        cand = mk(f"{TP_PREFIX}{len(out) + 1}", KIND_SWING, level)
        if cand is None:
            continue
        seen.append(d)
        out.append(cand)
        if len(out) >= MAX_STRUCTURAL:
            break
    return out


def _book_prices(book_levels: Optional[Sequence[Any]], want: str) -> List[Tuple[float, float]]:
    """``(price, score)`` for Level Book levels of the wanted type.

    Fields are read **by name** off `level_book.Level` — ``price``, ``type``,
    ``score``. This module was documented as reading the Level Book and ran a
    private pivot scan instead; the repair is worth nothing if the reader then
    guesses at field names, which is how `zone_distance_atr` returned None on
    every row for its whole life. A level whose shape does not match is skipped
    and the menu simply carries fewer candidates — never a raise, and never a
    silently invented price.
    """
    out: List[Tuple[float, float]] = []
    for lv in book_levels or []:
        try:
            if str(getattr(lv, "type", "")) != want:
                continue
            price = float(getattr(lv, "price", 0.0) or 0.0)
        except (TypeError, ValueError):
            continue
        if price <= 0:
            continue
        try:
            score = float(getattr(lv, "score", 0.0) or 0.0)
        except (TypeError, ValueError):
            score = 0.0
        out.append((price, score))
    # Highest-scoring first: the Level Book already ranks by touches and age,
    # and re-deriving that ordering here would be a second opinion about a
    # question the book has already answered.
    out.sort(key=lambda pair: pair[1], reverse=True)
    return out


def _book_tps(book_levels: Optional[Sequence[Any]], is_long: bool, entry: float,
              current: Candidate, mk: Any, offset: int) -> List[Candidate]:
    """Level Book targets **nearer than the current TP1**, nearer-only.

    A long takes profit into resistance and a short into support, so the wanted
    side flips with the trade — the same signing discipline the snapshot's
    aligned features carry, and the reason `cvd_slope` scored every SHORT
    backwards for a month before anyone noticed.
    """
    want = "resistance" if is_long else "support"
    out: List[Candidate] = []
    cur = current.dist_pct
    for price, _score in _book_prices(book_levels, want):
        d = _pct_from(entry, price, is_long)
        if d <= 0 or d >= cur:
            continue
        cand = mk(f"{TP_PREFIX}{offset + len(out) + 1}", KIND_LEVEL, price)
        if cand is None:
            continue
        out.append(cand)
        if len(out) >= MAX_STRUCTURAL:
            break
    return out


def _book_sls(book_levels: Optional[Sequence[Any]], is_long: bool,
              current: Candidate, mk: Any, offset: int) -> List[Candidate]:
    """Level Book stops **tighter than the current one**, tighter-only."""
    want = "support" if is_long else "resistance"
    out: List[Candidate] = []
    for price, _score in _book_prices(book_levels, want):
        if not _tightens(is_long, current.price, price):
            continue
        cand = mk(f"{SL_PREFIX}{offset + len(out) + 1}", KIND_LEVEL, price)
        if cand is None:
            continue
        out.append(cand)
        if len(out) >= MAX_STRUCTURAL:
            break
    return out


def _swing_sls(swings: Dict[str, List[float]], is_long: bool,
               current: Candidate, mk: Any) -> List[Candidate]:
    """Swing levels tighter than the current stop — **tighter only**."""
    pool = swings.get("swing_lows" if is_long else "swing_highs") or []
    out: List[Candidate] = []
    for level in sorted(pool, reverse=is_long):
        if not _tightens(is_long, current.price, level):
            continue
        cand = mk(f"{SL_PREFIX}{len(out) + 1}", KIND_SWING, level)
        if cand is None:
            continue
        out.append(cand)
        if len(out) >= MAX_STRUCTURAL:
            break
    return out
