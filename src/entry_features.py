"""Entry-time features for every path the dark feed measures — stamped here, consumed next door.

**2026-08-02: this lane now has a consumer.** ``src/entry_quality.py`` is a real
gate in the scanner's post-scoring chain that can suppress a candidate on what
these stamps say, and the owner's directive was exactly that — *"make entry
features live, not only measurement"*.  The division of labour is deliberate and
worth keeping: **this module records, that one decides.**  Nothing below applies
anything, every helper still refuses rather than clamps, and the row a rule reads
is the row that was written at signal creation.

What changed here is only that a row is now *findable and annotatable*
(``row_for`` / ``annotate``): the gate runs later than the stamp, in the scanner,
because that is where suppression and its audit stamp live.  Its verdict is
merged back onto the row under ``eq_*`` keys so the ops page joins one artifact
rather than two.  The schema is deliberately **not** bumped for those keys — a
bump drops the population, and this lane finally has one; a row stamped before
the gate existed simply carries no ``eq_*``, which ops renders as "not
evaluated" and never as "passed".  A missing stamp is not a pass.

Everything below this line describes the stamping half, unchanged.


Owner, 2026-08-01: *"taking entry is matter, how we are taking entry based on
only EMA or what, what if we add some more data to that"*, and then, on the dark
feed: *"we need to concentrate on entry, on which bases entry is confirming
especially on Trend pullback EMA and mover AVWAP"*.

The answer to the first half is: essentially yes, on every path.

* ``_evaluate_mover_trend_pullback`` decides direction from ``SMA25 vs SMA99`` on
  15m and triggers on the previous bar tagging ``SMA7``.
* ``_evaluate_trend_pullback`` (TREND_PULLBACK_EMA) sources trend from 1H
  EMA21/50 and triggers on a 5m EMA21 tag plus an EMA9/21 reclaim close, with an
  RSI 40–60 band and a close-position-in-range test.
* ``_evaluate_mover_avwap_scalp`` anchors a VWAP at the leg origin and triggers
  on a pullback into it reclaimed on the next close, volume-confirmed.

All three decide on **price against a moving reference, plus one ATR**.  Meanwhile
``smc_data`` is built once per symbol per scan and handed to every evaluator
carrying ``cvd`` / ``cvd_15m``, ``order_book``, ``funding_rate``,
``liquidation_clusters``, ``orderblocks``, ``sweeps``, ``mss``, ``fvg``,
``level_book_levels`` and ``recent_ticks``.  These paths touch at most
``pair_profile`` and ``regime_context``, and use both only for display stamps on
the outgoing signal.  A pullback on collapsing bid into a liquidation cluster is,
to any of them, the same object as a pullback being absorbed at a level.

This module records what those inputs *said* at the moment each signal was
created, and applies none of it.

A small shared core, and per-path features that are the actual point
--------------------------------------------------------------------
The first cut of this generalisation copied MVRTP's feature list onto every path
and was wrong for a reason worth writing down: **that list was chosen for
MVRTP's particular blindness**, which is a three-SMA pullback trigger that never
looks at volume.  TPE and MVAVW are blind in different places, so the same
columns measure nothing on them while the variables their entries actually turn
on go unrecorded.  A feature set is not portable just because the code that
computes it is.

So there are two layers:

* **Core** — true of every path by construction, not by hypothesis: the designed
  geometry (``tp1_r_multiple``, ``sl_dist_pct``), where the entry sat relative to
  the level the trigger is defined against (``entry_ref_dist_atr``), and the
  trigger bar's own shape.  These are comparable across paths because they are
  facts about the trade, not readings of the market.
* **Extras** — supplied by each evaluator from variables already in its scope,
  and different per path because the mechanisms are different.  TPE's entry
  hinges on the maturity of a 1H trend, how much of the impulse leg the pullback
  gave back, and where in the 40–60 RSI band it fired.  MVAVW's hinges on how old
  the leg is, how far it has already travelled, and how many times price has
  already come back to the anchor.  Neither list means anything on the other
  path.

What is **not** shared is the series the features are read from: TPE triggers on
5m, the mover paths on 15m.  A volume ratio over 5m bars and one over 15m bars
are different measurements, so every row carries ``tf_name`` and no surface may
pool them without splitting on it.  Two arms named for the same mechanism can
measure different mechanisms (``CLAUDE.md``), and the cheapest place to prevent
that is the row itself.

One gate is stamped because its comment and its code disagree — and the
measurement then cleared the gate
---------------------------------------------------------------------------
``_evaluate_trend_pullback``'s SMC check reads *"require at least one FVG or
orderblock in the pullback zone"* and is implemented as
``bool(fvgs) or bool(orderblocks)`` — a global existence test.  On paper any
symbol carrying any fair-value gap anywhere passes it, so it was stamped on the
expectation that it admits structure far from the entry.

**It does not.**  Measured on the first 89 TPE signals after
``zone_distance_atr`` was repaired (2026-08-02 — until then this feature
returned ``None`` on every row and could answer nothing): median **0.13 ATR**,
p90 0.42, **max 0.52**, 88 of 89 inside half an ATR, no tail.  The cause is
``detect_fvg``'s ``lookback=10`` — it only finds gaps in the last ~12 bars, and
a gap that recent is still near price.  The narrow lookback is what makes the
loose gate behave like the strict one its comment describes.

So the gate is doing roughly what it claims: it rejects symbols with no recent
gap, and when it passes, the structure is at the entry.  The candidate rule
built on this feature (``entry_quality.tpe_smc_zone``) was retired the same day
— no threshold can discriminate on that distribution.

The feature stays stamped.  It is what settled the question, and it is what
would show the gate drifting if ``lookback`` or the detector ever changed.

Why stamping rather than filtering
----------------------------------
The 2026-07-29→08-01 window is 46 closed MVRTP signals.  Nineteen cells were
tested across six candidate discriminators; exactly one 95% CI excluded zero, in
the *backwards* direction, against a ~62% familywise probability of at least one
doing so by chance.  That window cannot choose a filter, and choosing one from it
would be the FAILED_AUCTION_RECLAIM mistake at larger n (``CLAUDE.md``: *two
winners are not a promotion*).  So: stamp every candidate input, wait for a
population that can decide, and let the measurement pick.

The geometry feature is the one to read first
---------------------------------------------
``tp1_r_multiple`` is the designed reward-to-risk of the trade as the evaluator
shaped it, and it is not a candidate discriminator like the others — it is a
property of the setup rather than of the market, knowable with certainty at
stamp time, and it bounds what every other feature can achieve.

Dark-feed data 2026-08-01, 65 rows over 23.8h: TREND_PULLBACK_EMA ran a **median
designed R:R of 0.79** — TP1 nearer than the stop — needing a 54% win rate to
break even and posting 35% over 17 decided rows.  MOVER_AVWAP_SCALP sets
``tp1 = close ± sl_dist``, exactly 1.0R by construction, needing 52% and posting
42%.  Reading the code confirms the mechanism for TPE: TP1 is the nearest 5m
swing extreme, then *capped* by ATR percentile
(``_tp1_cap_tpe``), and ``_enforce_tp_ladder_monotonicity`` floors tp2 at 2.0R
and tp3 at 4.0R — **but nothing floors tp1**.

**Do not read that as "raise TP1".**  It was written here as though it were, and
it is wrong — checked against the same data hours later, in one query that could
have been run first.  Raising the target makes the book *worse*, on the
2026-08-01 11:00 dark window (55 decided rows) under both bounds:

===================  =========  ==========================
TP1 floored at       Win rate   Result per decided trade
===================  =========  ==========================
left as-is              47%     −0.081R
1.0R                    25%     −0.186R to −0.404R
1.5R                    18%     −0.245R to −0.536R
2.0R                     5%     −0.436R to −0.836R
===================  =========  ==========================

It reproduces on the earlier 08:26 window (48 rows: −0.135R as-is, falling to
−0.252R…−0.460R at a 1.0R floor), so the direction is not an artefact of one
export.

The winners barely clear their targets — TPE's hit at a median 0.59R against a
0.89R median peak — and only 27% of decided trades ever moved 1R in our favour at
all.  The low target is not a defect; it is the only thing harvesting a move this
small.  Median MFE across the decided book is **0.53R**, and 26 of 55 trades
never got 0.5R in favour.

So ``tp1_r_multiple`` is still the first row to read, but as a **description of
what the book can possibly earn**, not as a lever.  It says the trades are small
relative to the risk they are sized for — which points at entry quality and at
loss size, and away from the targets.

Recording it here changes nothing either way.  TP/SL shape is an owner-sign-off
item (``CLAUDE.md`` § Change-management), so the number goes on the row, the
split goes on the ops page, and any geometry decision waits for the owner and a
population — which is the whole point of having a lane that can produce one.

Design decisions worth keeping
------------------------------
**No second resolver.**  Every other measurement lane in this repo carries its
own forward-resolution machinery, and each one has cost a session to
``INSUFFICIENT`` rows, stalled arms, stale anchors or undatable windows.  This
lane has no resolver at all: it stamps a row keyed by ``signal_id``, and the
outcome is joined from ``signal_performance.json`` — the closed-signal record
``trade_monitor`` already writes at the terminal transition, which since #848
carries the entry risk the trade was actually sized for.  A row that never
delivered simply never joins, and the surface says how many did not rather than
quietly shrinking its own denominator.

**Free by construction.**  Every value here is already in memory at the call
site.  No Firestore read, no network call, no extra candle fetch — the cost rules
forbid adding any of those to a per-scan path, and this adds none.

**Refuse, don't clamp.**  A feature whose inputs are absent is ``None`` with its
reason recorded in ``missing``, never a zero or a midpoint.  A zero here would be
a *reading*, and a reading nobody took is worse than an admitted gap: it would
make an absent order book look like perfectly balanced depth.

Nothing **in this module** changes what emits: the signal an evaluator returns is
identical with the stamping on or off, and tests drive the real evaluators both
ways to pin that.  What emits is now decided one module over, by
``entry_quality``, reading these rows — and only through rules the owner has
flipped live from ops.
"""
from __future__ import annotations

import json
import os
import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional, Tuple

from src import fail_open
from src.utils import get_logger

log = get_logger("entry_features")

#: Ledger schema. Readers gate on this, never on a date (#802) — a migration
#: keyed on a timestamp that predicts a future deploy trusted 88 rows of
#: old-code stamps once already.
#:
#: 2 (2026-08-01): generalised from MVRTP-only to every dark-feed path. Rows gain
#: ``setup_class`` as a first-class split, ``tf_name`` (a 5m volume ratio and a
#: 15m one are different features), ``entry_ref_*`` in place of the SMA-specific
#: extension, and ``tp1_r_multiple``. Bumping drops the schema-1 rows, which cost
#: about an hour of MVRTP stamps — redefining a live measurement is only cheap
#: while its population is nearly empty, and this was the last moment it was.
SCHEMA = 2

_DEFAULT_PATH: str = os.getenv("ENTRY_FEATURES_PATH", "data/entry_features_v1.json")

#: Ring size. A storage bound, not a cap on what stamps.
_MAX_ROWS: int = int(os.getenv("ENTRY_FEATURES_MAX_ROWS", "4000"))

#: Bars of pullback context to measure over. The trigger looks at exactly two
#: bars (``prev`` and ``close``); the pullback that produced them is longer, and
#: its shape is the thing we have never recorded.
_PULLBACK_LOOKBACK: int = int(os.getenv("ENTRY_FEATURES_PULLBACK_BARS", "6"))

#: Baseline window for the volume ratio — what "normal" volume is for this pair
#: right now, so the ratio is self-normalising across pairs of any size.
_VOL_BASELINE_BARS: int = int(os.getenv("ENTRY_FEATURES_VOL_BASELINE_BARS", "20"))

#: Bars defining "the impulse leg" for the retrace measurement. Long enough to
#: contain the move a pullback is pulling back from, short enough that it is
#: still the current leg rather than the last three.
_LEG_LOOKBACK: int = int(os.getenv("ENTRY_FEATURES_LEG_BARS", "24"))


# --------------------------------------------------------------------------- #
# Feature extraction
# --------------------------------------------------------------------------- #


def _f(value: Any) -> Optional[float]:
    """Coerce to float, or None. Never raises, never invents a default."""
    try:
        if value is None:
            return None
        out = float(value)
        if out != out or out in (float("inf"), float("-inf")):  # NaN / inf
            return None
        return out
    except (TypeError, ValueError):
        return None


def _align(value: Optional[float], is_long: bool) -> Optional[float]:
    """Re-sign a directional reading so positive always means "favours this trade".

    ``None`` stays ``None`` — an absent reading has no sign, and returning 0.0
    would turn a missing order book into perfectly balanced depth.
    """
    if value is None:
        return None
    return value if is_long else -value


def _series(tf: Any, key: str) -> Optional[List[float]]:
    """A candle series as floats, or None.

    Never boolean-tests the array: the data store holds numpy arrays and their
    truthiness raises (``CLAUDE.md`` hard limit — eight features died silently
    to this on 2026-07-14).
    """
    if tf is None:
        return None
    raw = tf.get(key) if isinstance(tf, dict) else None
    if raw is None:
        return None
    try:
        if len(raw) == 0:
            return None
        return [float(v) for v in raw]
    except (TypeError, ValueError):
        return None


def pullback_volume_ratio(
    volumes: Optional[List[float]],
    *,
    lookback: int = _PULLBACK_LOOKBACK,
    baseline: int = _VOL_BASELINE_BARS,
) -> Optional[float]:
    """Volume across the pullback, against this pair's own recent baseline.

    The question the trigger never asks: was the dip sold, or did it just drift?
    A pullback on 0.4× normal volume is participants stepping back; the same
    shape on 2× is distribution. Both currently emit identically.

    Returns mean(pullback bars) / mean(baseline bars). ``None`` when either
    window is short or the baseline is zero — a ratio against no baseline is
    not a small number, it is not a number.
    """
    if volumes is None or len(volumes) < baseline + lookback:
        return None
    recent = volumes[-lookback:]
    prior = volumes[-(baseline + lookback):-lookback]
    if len(prior) == 0 or len(recent) == 0:
        return None
    base = sum(prior) / len(prior)
    if base <= 0:
        return None
    return (sum(recent) / len(recent)) / base


def cvd_slope(cvd: Any, *, lookback: int = _PULLBACK_LOOKBACK) -> Optional[float]:
    """Net cumulative-volume-delta change across the pullback window.

    Sign is what matters: on a LONG pullback a *positive* slope means the dip
    was being absorbed, a negative one means it was being sold into. The
    evaluator has never distinguished those.

    Deliberately returns the raw delta, not a normalised score — normalising
    would need a scale nobody has measured yet, and inventing one now would bake
    an unexamined assumption into the first population this lane ever produces.
    """
    if cvd is None:
        return None
    try:
        if len(cvd) < lookback + 1:
            return None
        head = _f(cvd[-(lookback + 1)])
        tail = _f(cvd[-1])
    except (TypeError, ValueError, IndexError):
        return None
    if head is None or tail is None:
        return None
    return tail - head


def pullback_depth_atr(
    closes: Optional[List[float]],
    lows: Optional[List[float]],
    highs: Optional[List[float]],
    atr: Optional[float],
    is_long: bool,
    *,
    lookback: int = _PULLBACK_LOOKBACK,
) -> Optional[float]:
    """How far the pullback actually retraced, in ATR.

    A one-ATR dip and a three-ATR dip both "tag SMA7 and reclaim". They are not
    the same trade, and nothing downstream can tell them apart today.
    """
    if atr is None or atr <= 0 or closes is None or len(closes) < lookback + 1:
        return None
    ref = closes[-(lookback + 1)]
    if is_long:
        arr = lows
        if arr is None or len(arr) < lookback:
            return None
        extreme = min(arr[-lookback:])
        return (ref - extreme) / atr
    arr = highs
    if arr is None or len(arr) < lookback:
        return None
    extreme = max(arr[-lookback:])
    return (extreme - ref) / atr


def extension_pct(close: Optional[float], ma_slow: Optional[float]) -> Optional[float]:
    """How far price sits from its own slow MA, signed, in percent.

    ``consol_break`` guards against chasing an extended move; ``fast_pullback``
    and ``deep_pullback`` — the two that carry the volume — do not.
    """
    if close is None or ma_slow is None or ma_slow <= 0:
        return None
    return (close - ma_slow) / ma_slow * 100.0


#: Why ``level_distance_r`` produced no number. Four causes, and the response to
#: each is different: ``no_geometry`` is a broken stamp, ``no_levels`` is the
#: LevelBook handing us nothing (a dark upstream — go look at the refresh),
#: ``unreadable_levels`` is a shape this reader does not understand (a defect
#: *here*, and the one that made ``smc_zone_dist_atr`` uncomputable for its
#: whole life), and ``none_ahead`` is a fully working read whose answer is
#: "nothing opposing between the entry and the target" — not a fault at all.
#:
#: They existed before as one ``None``, which is why the liveness probe could
#: only assert a cause and never name one.
LEVEL_DIST_NO_GEOMETRY = "no_geometry"
LEVEL_DIST_NO_LEVELS = "no_levels"
LEVEL_DIST_UNREADABLE_LEVELS = "unreadable_levels"
LEVEL_DIST_NONE_AHEAD = "none_ahead"


def reason_key(feature: str) -> str:
    """The row key carrying *why* ``feature`` is absent, when it records one.

    One naming rule, so a reader can ask the question of any feature without
    the module having to enumerate which ones answer. A feature that records no
    reason simply has no such key, and the caller says "cause unrecorded"
    rather than inventing one.
    """
    return f"{feature}_absence_reason"


def level_distance_r_with_reason(
    levels: Any,
    entry: Optional[float],
    tp1: Optional[float],
    sl_dist: Optional[float],
    is_long: bool,
) -> Tuple[Optional[float], Optional[str]]:
    """``(distance_in_R, reason_it_is_absent)`` — exactly one of the two is set.

    The value half is ``level_distance_r``'s, unchanged. The reason half exists
    because "blank needs a cause before it gets a caption": an empty LevelBook
    and a book with nothing overhead are opposite findings that both used to
    arrive as ``None``, so the feature-liveness probe watching this column had
    to guess, and it guessed "upstream is dark" every time.

    ``levels`` is produced by ``LevelBook.get_levels`` — a list of ``Level``
    dataclasses carrying ``price`` and ``type`` (``"support"``/``"resistance"``).
    Those are the fields read. The mapping branch is kept for the ledger's own
    round-trip and for tests, and a level this reader cannot price is counted
    rather than skipped in silence — an unreadable shape is indistinguishable
    from an empty book otherwise, which is precisely how ``zone_distance_atr``
    returned ``None`` on 57 of 57 rows without anyone being able to tell.
    """
    if entry is None or sl_dist is None or sl_dist <= 0:
        return None, LEVEL_DIST_NO_GEOMETRY
    if not levels:
        return None, LEVEL_DIST_NO_LEVELS
    want = "resistance" if is_long else "support"
    best: Optional[float] = None
    readable = 0
    for lvl in levels:
        if isinstance(lvl, dict):
            price = _f(lvl.get("price"))
            ltype = lvl.get("type", "")
        else:
            price = _f(getattr(lvl, "price", None))
            ltype = getattr(lvl, "type", "")
        if price is None:
            continue  # a shape we cannot price — the `readable` count catches it
        readable += 1
        if str(ltype) != want:
            continue
        gap = (price - entry) if is_long else (entry - price)
        if gap <= 0:
            continue  # already behind us
        if best is None or gap < best:
            best = gap
    if best is None:
        return None, (
            LEVEL_DIST_NONE_AHEAD if readable else LEVEL_DIST_UNREADABLE_LEVELS
        )
    return best / sl_dist, None


def level_distance_r(
    levels: Any,
    entry: Optional[float],
    tp1: Optional[float],
    sl_dist: Optional[float],
    is_long: bool,
) -> Optional[float]:
    """Distance to the nearest opposing level, in units of the trade's own risk.

    TP1 sits at exactly 1.0R by construction. If a resistance level sits at
    0.4R above a long's entry, that target is behind a wall and the geometry
    never knew. Expressed in R so it is directly comparable to the target.

    ``None`` when the level book has nothing for this symbol — an empty book is
    "we do not know what is overhead", which must not read as "nothing is".
    Use ``level_distance_r_with_reason`` when you need to tell those apart.
    """
    return level_distance_r_with_reason(levels, entry, tp1, sl_dist, is_long)[0]


def tp1_r_multiple(
    entry: Optional[float], tp1: Optional[float], sl_dist: Optional[float]
) -> Optional[float]:
    """The trade's designed reward:risk — distance to TP1 over the stop distance.

    Not a market reading: this is what the evaluator *chose*, known exactly at
    stamp time and never revised. It is the ceiling on everything else, because a
    path whose TP1 sits inside 1R needs a win rate above 50% before any entry
    filter has done anything at all.

    Divided by the stop distance the trade is **sized** for, which is the same
    denominator ``sl_distance_pct_at_entry`` carries on the closed-signal record
    (#848) — so this is directly comparable with the realised R it will be
    joined to, rather than being a second definition wearing the same letter.
    """
    e, t, d = _f(entry), _f(tp1), _f(sl_dist)
    if e is None or t is None or d is None or d <= 0:
        return None
    return abs(t - e) / d


def entry_ref_distance_atr(
    entry: Optional[float], reference: Optional[float], atr: Optional[float]
) -> Optional[float]:
    """How far the entry was taken from the level it is defined against, in ATR.

    Every path in this lane enters against a moving reference — TPE's EMA21,
    MVAVW's anchored VWAP, MVRTP's SMA99, MEAN_REVERT's rolling mean,
    RANGE_FADE's faded edge. "Price reclaimed the level" is true one tick past it
    and true again two ATR past it, and only one of those is the setup the path
    is named for. Unsigned: the question is how far, not which side — the trigger
    already fixed the side.
    """
    e, r, a = _f(entry), _f(reference), _f(atr)
    if e is None or r is None or a is None or a <= 0:
        return None
    return abs(e - r) / a


def bar_range_atr(
    high: Optional[float], low: Optional[float], atr: Optional[float]
) -> Optional[float]:
    """The trigger bar's own range, in ATR. A proxy for entering into a spike."""
    h, low_v, a = _f(high), _f(low), _f(atr)
    if h is None or low_v is None or a is None or a <= 0:
        return None
    return (h - low_v) / a


def close_position_in_bar(
    close: Optional[float],
    high: Optional[float],
    low: Optional[float],
    is_long: bool,
) -> Optional[float]:
    """Where the trigger bar closed within its own range, 0…1 in trade direction.

    TREND_PULLBACK_EMA already gates on exactly this at 0.50 and calls it
    ``body_conviction``; no other path tests it and nothing records it. Stamping
    it lets the existing threshold be checked against outcomes instead of being
    trusted — a live gate parameter nobody has ever measured is the same risk as
    a gate that stamps no suppression (``CLAUDE.md``).
    """
    c, h, low_v = _f(close), _f(high), _f(low)
    if c is None or h is None or low_v is None:
        return None
    rng = h - low_v
    if rng <= 0:
        return None
    return (c - low_v) / rng if is_long else (h - c) / rng


def retrace_fraction(
    highs: Optional[List[float]],
    lows: Optional[List[float]],
    entry: Optional[float],
    is_long: bool,
    *,
    leg_bars: int = _LEG_LOOKBACK,
) -> Optional[float]:
    """How much of the recent impulse leg the pullback gave back, 0…1+.

    This is the question a pullback entry actually rests on and no path in this
    lane asks it. A 30% retrace into a rising trend is the setup; a 90% retrace
    is a trend that has already failed and is about to be bought at the worst
    price in the leg. Both satisfy "price tagged the EMA and closed back above
    it", which is all TREND_PULLBACK_EMA checks.

    Measured against the leg extreme over *leg_bars*: for a LONG, the leg runs
    from its low to its high and the retrace is how far back down from the high
    the entry sits. Values above 1.0 are possible and meaningful — the entry is
    below where the leg began.

    ``None`` when the leg has no height; a retrace of a flat leg is a division
    by nothing, not a zero.
    """
    if highs is None or lows is None or entry is None:
        return None
    if len(highs) < leg_bars or len(lows) < leg_bars:
        return None
    hi = max(highs[-leg_bars:])
    lo = min(lows[-leg_bars:])
    height = hi - lo
    if height <= 0:
        return None
    return (hi - entry) / height if is_long else (entry - lo) / height


def zone_distance_atr(
    zones: Any,
    entry: Optional[float],
    atr: Optional[float],
) -> Optional[float]:
    """Distance from entry to the nearest FVG / orderblock edge, in ATR.

    The measurement ``_evaluate_trend_pullback``'s SMC gate says it makes. That
    gate tests ``bool(fvgs) or bool(orderblocks)`` — whether the symbol has any
    such zone at all, anywhere, at any price — so it passes on structure that may
    be 20 ATR away and unrelated to the pullback being entered.

    **The only real producer today is** ``smc.FVGZone``, whose edges are
    ``gap_high`` / ``gap_low``.  The first cut of this function did not read
    those two names — it guessed at ``top`` / ``bottom`` / ``high`` / ``low`` /
    ``price``, none of which that dataclass has — so **every** zone yielded no
    edges, was skipped, and the function returned ``None`` on a full book.
    ``smc_zone_dist_atr`` was therefore uncomputable from the day it shipped:
    0 of 57 TPE rows on the VPS (owner-run, 2026-08-02), which reads exactly
    like "no structure near these entries" and is instead a broken reader.

    The tests went green over it because they hand-wrote the zone shape
    (``{"top": 105.0, "bottom": 95.0}``) — keys chosen by the test author, never
    produced by anything. ``CLAUDE.md`` already carried the rule: *a mock whose
    keys you chose cannot verify a contract you got wrong; it asserts your
    assumption back at you and goes green over dead code.* The regression test
    now drives ``detect_fvg`` and passes its real output straight in.

    ``orderblocks`` are mappings by declaration (``List[Dict[str, Any]]``) and
    have **no writer at all** — ``SMCResult.orderblocks_detector_status`` is
    ``"not_implemented"`` and the VPS truth report counts 474,467 observations,
    100% empty. The mapping keys below are kept for whenever that detector
    lands, and they are a guess until it does; ``gap_high``/``gap_low`` are not
    a guess, so they are read first and named for what produces them.
    """
    e, a = _f(entry), _f(atr)
    if e is None or a is None or a <= 0 or not zones:
        return None
    best: Optional[float] = None
    for zone in zones:
        if isinstance(zone, dict):
            get = zone.get
        else:
            def get(key: str, _z: Any = zone) -> Any:
                return getattr(_z, key, None)
        edges: List[float] = [
            v
            for v in (
                # FVGZone — the real shape, the one that actually arrives.
                _f(get("gap_high")), _f(get("gap_low")),
                # Shapes an orderblock detector might use, if one is ever built.
                _f(get("top")), _f(get("bottom")),
                _f(get("high")), _f(get("low")),
                _f(get("price")),
            )
            if v is not None
        ]
        if len(edges) == 0:
            continue
        # Inside the zone is distance zero, which is the strongest reading there
        # is and must not be reported as the gap to its nearer edge.
        lo, hi = min(edges), max(edges)
        gap = 0.0 if lo <= e <= hi else min(abs(e - lo), abs(e - hi))
        if best is None or gap < best:
            best = gap
    if best is None:
        return None
    return best / a


def anchor_touch_count(
    highs: Optional[List[float]],
    lows: Optional[List[float]],
    anchor: Optional[float],
    *,
    band_pct: float,
) -> Optional[int]:
    """How many bars of this leg already came back to the anchor.

    MOVER_AVWAP_SCALP treats every pullback into the anchored VWAP identically.
    The first return to it is the reload the strategy is named for; the fourth is
    a level that keeps failing to hold, which is distribution wearing the same
    shape. Nothing in the path distinguishes them.

    Counts bars whose range intersects the same band the trigger uses, so this
    is the count of prior *trigger-eligible* touches rather than a looser notion
    of "near".
    """
    a = _f(anchor)
    if a is None or a <= 0 or highs is None or lows is None:
        return None
    n = min(len(highs), len(lows))
    if n == 0:
        return None
    band = a * (band_pct / 100.0)
    lo_edge, hi_edge = a - band, a + band
    return sum(
        1 for i in range(n) if float(lows[i]) <= hi_edge and float(highs[i]) >= lo_edge
    )


def book_imbalance(order_book: Any) -> Optional[float]:
    """Top-of-book depth imbalance: (bids - asks) / (bids + asks), in [-1, 1].

    Positive favours the bid. ``None`` when either side is absent — a missing
    book is not a balanced one, and returning 0.0 would say the opposite of
    what we know.
    """
    if not isinstance(order_book, dict):
        return None
    bids, asks = order_book.get("bids"), order_book.get("asks")
    if not bids or not asks:
        return None
    try:
        b = sum(float(lvl[1]) for lvl in bids[:10])
        a = sum(float(lvl[1]) for lvl in asks[:10])
    except (TypeError, ValueError, IndexError):
        return None
    if b + a <= 0:
        return None
    return (b - a) / (b + a)


def capture(
    *,
    symbol: str,
    direction_is_long: bool,
    entry: float,
    sl_dist: float,
    tp1: float,
    trigger: str,
    tf: Any,
    tf_name: str,
    atr: Optional[float],
    smc_data: Optional[Dict[str, Any]],
    entry_ref: Optional[float] = None,
    entry_ref_name: str = "",
    ma_slow: Optional[float] = None,
    stack_sep_pct: Optional[float] = None,
    profile_would_reject: Optional[bool] = None,
    extras: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """The core entry-time facts, plus whatever *extras* this path supplies.

    Pure: no I/O, no mutation of anything passed in. Each feature independently
    degrades to ``None`` with a reason in ``missing`` rather than failing the
    whole capture — one absent order book must not cost us the volume reading
    beside it.

    ``entry_ref`` is the level this path's entry is defined against, and
    ``entry_ref_name`` says which one it is. The name is recorded rather than
    inferred because the same distance means different things against an EMA and
    against an anchored VWAP, and a reader that cannot tell them apart will
    average them.

    ``tf`` is the candle mapping the trigger fired on and ``tf_name`` its label.
    Both are required: the series features below are only comparable across rows
    that share a timeframe, and a row that cannot say which one it read is a row
    no split can safely use.

    ``extras`` carries the path-specific measurements — the ones that are the
    actual point, computed by the evaluator from variables already in its scope
    because that is the only place they exist. They are merged flat into the row
    and share the ``missing`` accounting, so a path-specific feature that stops
    computing is as visible as a core one.
    """
    smc = smc_data or {}
    closes = _series(tf, "close")
    highs = _series(tf, "high")
    lows = _series(tf, "low")
    vols = _series(tf, "volume")
    # None/len, never truthiness. `_series` returns lists so these are in fact
    # safe today — but the hard limit is written against the *pattern*, because
    # the day one of these starts arriving as a numpy array the failure is
    # silent, and eight features died to exactly that on 2026-07-14.
    last_high = highs[-1] if highs is not None and len(highs) > 0 else None
    last_low = lows[-1] if lows is not None and len(lows) > 0 else None
    last_close = closes[-1] if closes is not None and len(closes) > 0 else None

    # Resolved here rather than inline so the *reason* it is absent survives
    # onto the row. Computed once — a second call would be a second read of a
    # mutable level book, and two reads of one quantity that can disagree is
    # the shape this repo keeps paying for.
    _level_dist, _level_dist_reason = level_distance_r_with_reason(
        smc.get("level_book_levels"), _f(entry), _f(tp1), _f(sl_dist), direction_is_long
    )

    feats: Dict[str, Any] = {
        # Geometry — chosen by the evaluator, exact at stamp time, and the
        # ceiling on what any entry filter can achieve. Read this one first.
        "tp1_r_multiple": tp1_r_multiple(entry, tp1, sl_dist),
        # Where the entry sits relative to the level it is defined against.
        "entry_ref_dist_atr": entry_ref_distance_atr(entry, entry_ref, atr),
        # The trigger bar itself.
        "entry_bar_range_atr": bar_range_atr(last_high, last_low, _f(atr)),
        "close_position_in_bar": close_position_in_bar(
            last_close, last_high, last_low, direction_is_long
        ),
        # The tape, none of which any of these paths consults.
        "pullback_vol_ratio": pullback_volume_ratio(vols),
        # Signed **in favour of this trade**, not in favour of price. A CVD
        # slope of −500 is the dip being sold, which is bad for a long and
        # exactly what a short wants; storing the raw number and then splitting
        # it with one "higher is better" rule scores every short backwards. The
        # schema-1 lane did precisely that on both this and the book imbalance
        # (2026-08-01) — the delivered book is ~50/50 by side, so the error was
        # not visible as an obviously empty column, it just made both features
        # look like noise.
        "cvd_slope_aligned": _align(
            cvd_slope(smc.get("cvd_15m") or smc.get("cvd")), direction_is_long
        ),
        "pullback_depth_atr": pullback_depth_atr(
            closes, lows, highs, _f(atr), direction_is_long
        ),
        "extension_pct": extension_pct(_f(entry), _f(ma_slow)),
        "level_dist_r": _level_dist,
        "book_imbalance_aligned": _align(
            book_imbalance(smc.get("order_book")), direction_is_long
        ),
        # Raw and deliberately unsigned: funding is a market state, not a
        # directional read. "Crowded long" is not automatically good for a short
        # — inventing an alignment here would bake in a hypothesis nobody has
        # measured, which is the thing this lane exists to avoid.
        "funding_rate": _f(smc.get("funding_rate")),
        "liq_clusters_n": (
            len(smc["liquidation_clusters"])
            if isinstance(smc.get("liquidation_clusters"), (list, tuple))
            else None
        ),
    }
    # Path-specific, merged before the missing-accounting so an extra that stops
    # computing shows up in exactly the same place a core feature would.
    for key, value in (extras or {}).items():
        feats[key] = value
    feats["missing"] = sorted(k for k, v in feats.items() if v is None)
    feats.update(
        {
            "symbol": str(symbol),
            "side": "LONG" if direction_is_long else "SHORT",
            "entry_trigger": str(trigger or ""),
            "tf_name": str(tf_name or ""),
            "entry_ref_name": str(entry_ref_name or ""),
            "stack_sep_pct": _f(stack_sep_pct),
            "sl_dist_pct": (
                (_f(sl_dist) / _f(entry) * 100.0)
                if _f(entry) and _f(sl_dist) and _f(entry) > 0
                else None
            ),
            # The shadow of the argument nineteen of twenty call sites omit:
            # would the pair-tier-aware spread/volume thresholds have rejected
            # this candidate? Recorded, never enforced.
            "profile_would_reject": profile_would_reject,
            # Written AFTER the missing-accounting on purpose. It is metadata
            # about a feature, not a feature, so it must never itself count as
            # one — and on a row where the feature computed it is None, which
            # would have put a non-feature into `missing` on every healthy row.
            reason_key("level_dist_r"): _level_dist_reason,
        }
    )
    return feats


# --------------------------------------------------------------------------- #
# Ledger — stamp only; outcomes are joined from the closed-signal record
# --------------------------------------------------------------------------- #


class EntryFeatureLedger:
    """Append-only ring of entry stamps, keyed by ``signal_id``."""

    def __init__(self, path: Optional[str] = None, max_rows: Optional[int] = None) -> None:
        self._path = _DEFAULT_PATH if path is None else path
        self._rows: Deque[dict] = deque(maxlen=max_rows or _MAX_ROWS)
        self._seen: set = set()
        # signal_id -> the row object itself. The deque already holds it; this
        # is the same object, not a copy, so an annotation written through here
        # is the row ops reads. Pruned against the ring on every append —
        # a map that outlives its deque is a slow leak and a lookup that returns
        # a row nobody will ever flush.
        self._by_id: Dict[str, dict] = {}
        self._lock = threading.RLock()
        self._dirty = False
        self.duplicate_skips = 0
        self.annotate_misses = 0

    def add(self, row: dict) -> bool:
        sid = str(row.get("signal_id") or "")
        if not sid:
            return False
        with self._lock:
            if sid in self._seen:
                # A signal is stamped exactly once, at creation. A second stamp
                # would mean the evaluator ran twice on one signal_id, which is
                # a fault worth counting rather than silently overwriting.
                self.duplicate_skips += 1
                return False
            evicted = self._rows[0] if len(self._rows) == self._rows.maxlen else None
            self._seen.add(sid)
            self._rows.append(row)
            self._by_id[sid] = row
            if evicted is not None:
                old = str(evicted.get("signal_id") or "")
                if old:
                    self._by_id.pop(old, None)
                    self._seen.discard(old)
            self._dirty = True
            return True

    def row_for(self, signal_id: str) -> Optional[dict]:
        """The stamped row for one signal, or None. O(1), no I/O.

        Returns the live object rather than a copy: the entry-quality gate runs
        in the scanner, after the evaluator has already stamped, and it needs to
        read what was stamped and write back what it decided. A copy would give
        the gate a private view and leave the ledger — the thing ops reads —
        describing a decision that was never made.
        """
        sid = str(signal_id or "")
        if not sid:
            return None
        with self._lock:
            return self._by_id.get(sid)

    def annotate(self, signal_id: str, values: Dict[str, Any]) -> bool:
        """Merge *values* into an already-stamped row.

        For facts that become true *after* the evaluator returns — today, the
        entry-quality verdict, which is decided in the scanner because that is
        where suppression lives. It is still "record a fact where it becomes
        true": the gate's own moment is later than the stamp's, and the
        alternative (re-deriving the decision at read time in ops) is the
        drifting mirror this lane already refuses.

        A miss is **counted**, not swallowed. A signal whose row is gone means
        the ring rotated or the stamp never happened, and an annotation quietly
        landing nowhere is how an ops panel comes to describe a population that
        does not exist.
        """
        sid = str(signal_id or "")
        with self._lock:
            row = self._by_id.get(sid) if sid else None
            if row is None:
                self.annotate_misses += 1
                return False
            row.update(values)
            self._dirty = True
            return True

    def rows(self) -> List[dict]:
        with self._lock:
            return list(self._rows)

    def flush(self, force: bool = False) -> bool:
        """Persist. ``force`` writes even when unchanged, so an idle lane still
        proves it is alive — a heartbeat that only fires on change is not a
        heartbeat, and an ops page cannot tell "quiet" from "stopped" without it.
        """
        with self._lock:
            if not (self._dirty or force):
                return False
            # ``path=""`` means in-memory (what tests construct with). Return
            # BEFORE the side effect: a no-op that touches the disk wrote a
            # stray .tmp into the repo root for two months, and its failure
            # raised into fail_open on every test run.
            if not self._path:
                self._dirty = False
                return False
            rows = list(self._rows)
            self._dirty = False
        payload = {
            "schema": SCHEMA,
            "written_at": time.time(),
            "rows": rows,
            # Shipped with the data so ops renders the split directions rather
            # than keeping its own copy of them. Ops mirroring an engine list is
            # the drift that silently inflated the Strategy Lab rollup for a
            # week, and the lesson from it is that the fix for a drifting mirror
            # is not a second mirror — it is one writer and one reader.
            "spec": describe_features(),
        }
        tmp = f"{self._path}.tmp"
        try:
            os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, self._path)
            return True
        except Exception as exc:  # noqa: BLE001 — measurement must never break a scan
            fail_open.record("entry_features.flush", exc)
            return False

    def load(self) -> None:
        if not self._path or not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
            if int(payload.get("schema") or 0) != SCHEMA:
                log.info(
                    "entry_features: ledger schema {} != {}, starting fresh",
                    payload.get("schema"), SCHEMA,
                )
                return
            with self._lock:
                for row in payload.get("rows") or []:
                    sid = str(row.get("signal_id") or "")
                    if sid and sid not in self._seen:
                        self._seen.add(sid)
                        self._rows.append(row)
                        # Same object the deque holds — a reloaded row must be
                        # annotatable, or a restart would silently split the
                        # ledger into rows the gate can write to and rows it
                        # cannot, with nothing on screen saying which.
                        self._by_id[sid] = row
                # A payload longer than the ring evicts from the left as it is
                # appended, so the maps are rebuilt from what actually survived
                # rather than from what was read.
                self._by_id = {
                    str(r.get("signal_id") or ""): r
                    for r in self._rows
                    if r.get("signal_id")
                }
                self._seen = set(self._by_id)
        except Exception as exc:  # noqa: BLE001
            fail_open.record("entry_features.load", exc)


_ledger: Optional[EntryFeatureLedger] = None
_ledger_lock = threading.Lock()


def get_ledger() -> EntryFeatureLedger:
    global _ledger
    with _ledger_lock:
        if _ledger is None:
            _ledger = EntryFeatureLedger()
            _ledger.load()
        return _ledger


def reset_ledger(ledger: Optional[EntryFeatureLedger] = None) -> None:
    global _ledger
    with _ledger_lock:
        _ledger = ledger


def enabled() -> bool:
    """Measurement flag — ON by default.

    ``CLAUDE.md`` § Project Phase: a measurement shipped default-OFF produces an
    empty panel and a decision that keeps being deferred, which is exactly what
    happened to the SAR exit arm. This cannot reach a subscriber or the money
    path, so it runs from the moment it ships.
    """
    try:
        from src import runtime_tunables as _rt
        return bool(_rt.get("entry_features_enabled"))
    except Exception:
        return os.getenv("ENTRY_FEATURES_ENABLED", "true").strip().lower() != "false"


def stamp(
    sig: Any,
    features: Dict[str, Any],
    now_ts: Optional[float] = None,
    regime: str = "",
) -> bool:
    """Record one signal's entry-time features. Never raises into the scanner.

    ``regime`` is passed in rather than read off ``sig``, and that is not a
    style choice. ``sig.entry_regime`` is written by
    ``scanner._populate_signal_context``, which runs **after** the evaluator has
    returned — so at stamp time the attribute is still ``""``. Reading it here
    put an empty regime on every row and would have bucketed the whole page into
    one group (caught 2026-08-01, immediately after shipping).

    That is #817's class one caller earlier, and the comment above
    ``_populate_signal_context``'s call site already warns about it: the
    market-context stamp *"previously ran with these fields still empty, so the
    Wyckoff phase always classified AMBIGUOUS"*. The evaluator receives the
    regime as a parameter, which is where it is genuinely known at this point.

    The closed-signal record's ``entry_regime`` remains authoritative — it is
    what the scanner finalised — and ops prefers it on the join. This value is
    the evaluator's own view; where the two disagree, the scanner reclassified
    between evaluation and dispatch, and that is information rather than a
    conflict.
    """
    if not enabled():
        return False
    try:
        sid = str(getattr(sig, "signal_id", "") or "")
        if not sid:
            return False
        row = dict(features)
        row.update(
            {
                "signal_id": sid,
                "setup_class": str(getattr(sig, "setup_class", "") or ""),
                "confidence": _f(getattr(sig, "confidence", None)),
                "entry_regime": str(
                    regime or getattr(sig, "entry_regime", "") or ""
                ),
                "stamped_at": time.time() if now_ts is None else float(now_ts),
                "schema": SCHEMA,
            }
        )
        return get_ledger().add(row)
    except Exception as exc:  # noqa: BLE001 — a measurement must never kill a scan
        fail_open.record("entry_features.stamp", exc)
        return False


# --------------------------------------------------------------------------- #
# "As of now" vs "later" — the split this lane exists to produce
# --------------------------------------------------------------------------- #

#: Features where a LOWER value is the suspected problem, so a candidate rule
#: would keep rows ABOVE the threshold. Everything else keeps rows below.
#:
#: The two ``_aligned`` features are here because alignment has already put
#: "favours this trade" on the positive side for both directions — which is the
#: only reason a single rule can be correct for longs and shorts at once.
_KEEP_ABOVE = frozenset(
    {
        "pullback_vol_ratio",
        "level_dist_r",
        "cvd_slope_aligned",
        "book_imbalance_aligned",
        "tp1_r_multiple",
        "close_position_in_bar",
        "h1_trend_sep_atr",
        "prev_extreme_break_atr",
        "vol_ratio_at_trigger",
        "avwap_slope_pct",
        "stack_sep_pct",
        "sigma_at_entry",
        "range_width_atr",
    }
)

#: The core, true of every path by construction: geometry first (it bounds
#: everything else), then the trigger bar, then the free order-flow reads.
CORE_FEATURES: Tuple[str, ...] = (
    "tp1_r_multiple",
    "entry_ref_dist_atr",
    "entry_bar_range_atr",
    "close_position_in_bar",
    "pullback_vol_ratio",
    "cvd_slope_aligned",
    "level_dist_r",
    "book_imbalance_aligned",
)

#: What each path contributes on top, and why it is *that* path's question.
#: Ordered so the mechanism-critical ones come first — a reader scanning the
#: page should meet the variable the entry actually turns on before the
#: hypotheses.
#:
#: The lists are deliberately short. A path that stamps twelve features invites
#: twelve thresholds, and twelve cells against a book this size is a familywise
#: error rate that guarantees a spurious winner (``CLAUDE.md``: count how many
#: cells you looked at before calling one special).
PATH_FEATURES: Dict[str, Tuple[str, ...]] = {
    "TREND_PULLBACK_EMA": (
        # The pullback question the path never asks: a 30% giveback is the setup,
        # a 90% giveback is a failed trend, and "tagged EMA21 and closed back
        # above" is true of both.
        "retrace_frac_of_leg",
        # Direction comes from 1H EMA21 vs EMA50 with no notion of how far apart
        # they are. A barely-crossed pair and a widely separated one are the
        # same input to this evaluator.
        "h1_trend_sep_atr",
        # The measurement its own SMC gate claims to make and does not.
        "smc_zone_dist_atr",
        # It gates RSI to 40-60 rising; where in the band is unrecorded, so the
        # band's edges have never been checked against outcomes.
        "rsi_at_entry",
        # The trigger requires close > prev_high. By how much is the difference
        # between a break and a nudge.
        "prev_extreme_break_atr",
        # Which of the two direction mechanisms actually ran. The 1H path and the
        # legacy 5m-regime fallback are different strategies sharing a name, and
        # nothing downstream could tell which produced a given signal.
        "uses_1h_trend",
    ),
    "MOVER_AVWAP_SCALP": (
        # How old the leg is. The anchor's whole meaning depends on it and the
        # evaluator uses the anchor only to compute a VWAP.
        "anchor_age_bars",
        # How far the move has already gone. `execution:overextended` is the gate
        # carried past on 21 of the dark rows, so this is literally the question
        # the dark data is asking.
        "leg_move_pct",
        # First return to the anchor is the reload; the fourth is a level that
        # keeps failing. Identical to this path today.
        "avwap_touches_in_leg",
        # Gated against a floor only, so its magnitude has never been read.
        "avwap_slope_pct",
        # The exact ratio `vol_ok` thresholds on, so the threshold itself becomes
        # checkable rather than trusted.
        "vol_ratio_at_trigger",
    ),
    "MOVER_TREND_PULLBACK": (
        # The stack's separation is the path's own trend-strength proxy and it is
        # gated at a floor; the value is what lets the floor be tested.
        "stack_sep_pct",
        "retrace_frac_of_leg",
        "extension_pct",
    ),
    "MEAN_REVERT": (
        # The entry IS an extension measurement, so how extended is not a
        # hypothesis here — it is the setup, and the 2.5 sigma threshold has
        # never been read against outcomes.
        "sigma_at_entry",
        "retrace_frac_of_leg",
    ),
    "RANGE_FADE": (
        # A range edge is only an edge while it holds; how many times it has been
        # tested is the difference between a fade and a breakout about to happen.
        "edge_touches",
        "range_width_atr",
    ),
}


def features_for(setup_class: str) -> Tuple[str, ...]:
    """Core plus this path's own, in reading order. Unknown path → core only."""
    return CORE_FEATURES + tuple(PATH_FEATURES.get(str(setup_class or ""), ()))


def describe_features() -> Dict[str, Any]:
    """The registry, as data, written into the ledger for ops to render.

    Ops needs three things to draw a split: which features belong to a path, in
    what order, and which way a candidate rule filters. All three are decided
    here, so all three ship from here.

    The alternative — ops keeping its own copy — is the mirror that drifted on
    ``MEASUREMENT_SUFFIXES`` and inflated the Strategy Lab rollup for a week
    before anyone noticed. A reader that derives the direction itself will agree
    with this module right up until one of them changes.
    """
    return {
        "core": list(CORE_FEATURES),
        "paths": {k: list(v) for k, v in PATH_FEATURES.items()},
        "keep_above": sorted(_KEEP_ABOVE),
    }


def split_by_feature(
    joined: List[Dict[str, Any]],
    feature: str,
    threshold: float,
) -> Dict[str, Any]:
    """What the delivered book looks like now, versus under one candidate rule.

    *now* is every joined row — the book as it actually shipped. *keep* is the
    subset a rule on this feature would have let through; *drop* is what it
    would have removed. ``unknown`` is rows whose feature never computed, and it
    is reported rather than folded into either side: a rule cannot be credited
    with an outcome it could not have seen, and silently binning the unknowns
    with "keep" is how a filter takes credit for rows it never filtered.

    Every row carries ``r`` from the closed-signal record — the engine's
    ``sl_distance_pct_at_entry`` denominator (#848), not the stop the trade
    exited on.
    """
    keep_above = feature in _KEEP_ABOVE
    buckets: Dict[str, List[Dict[str, Any]]] = {"keep": [], "drop": [], "unknown": []}
    for row in joined or []:
        val = _f(row.get(feature))
        if val is None:
            buckets["unknown"].append(row)
        elif (val >= threshold) if keep_above else (val <= threshold):
            buckets["keep"].append(row)
        else:
            buckets["drop"].append(row)

    def _agg(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        rs = [_f(r.get("r")) for r in rows]
        rs = [v for v in rs if v is not None]
        pnls = [_f(r.get("pnl_pct")) for r in rows]
        pnls = [v for v in pnls if v is not None]
        return {
            "n": len(rows),
            "scored": len(rs),
            "win_rate": (sum(1 for v in rs if v > 0) / len(rs)) if rs else None,
            "avg_r": (sum(rs) / len(rs)) if rs else None,
            "total_r": sum(rs) if rs else None,
            # Quoted beside every R because the R-scored subset is not a random
            # sample of the book — rows closed before #848 carry no denominator.
            "avg_pnl_pct": (sum(pnls) / len(pnls)) if pnls else None,
            "total_pnl_pct": sum(pnls) if pnls else None,
        }

    now = _agg(list(joined or []))
    keep = _agg(buckets["keep"])
    delta_r = (
        keep["avg_r"] - now["avg_r"]
        if keep["avg_r"] is not None and now["avg_r"] is not None
        else None
    )
    return {
        "feature": feature,
        "threshold": threshold,
        "direction": "keep >= threshold" if keep_above else "keep <= threshold",
        "now": now,
        "keep": keep,
        "drop": _agg(buckets["drop"]),
        "unknown": _agg(buckets["unknown"]),
        "delta_avg_r": delta_r,
        # A rule that keeps almost everything has not been tested by this window,
        # whatever its delta reads.
        "kept_fraction": (keep["n"] / now["n"]) if now["n"] else None,
        # Which series these rows were read from. One entry is a clean split;
        # more than one means the threshold is being applied across timeframes
        # that do not share a scale, and the surface must say so rather than
        # letting the reader assume a single population.
        "timeframes": sorted(
            {str(r.get("tf_name") or "") for r in (joined or [])} - {""}
        ),
        "setups": sorted(
            {str(r.get("setup_class") or "") for r in (joined or [])} - {""}
        ),
    }


def select(rows: List[Dict[str, Any]], setup_class: str = "") -> List[Dict[str, Any]]:
    """Rows for one setup, or all of them when *setup_class* is empty.

    Splitting on the path is not a convenience filter — the paths do not share a
    trigger, a timeframe or a stop geometry, so a threshold that helps one can
    be meaningless on another. Pooling them would produce a number whose value
    moves with the setup mix rather than with the feature.
    """
    if not setup_class:
        return list(rows or [])
    want = str(setup_class)
    return [r for r in (rows or []) if str(r.get("setup_class") or "") == want]


def setups_present(rows: List[Dict[str, Any]]) -> List[Tuple[str, int]]:
    """``(setup_class, n)`` for every path in *rows*, most rows first.

    Drives the page's selector from the data rather than from a hardcoded list,
    so a path that starts or stops stamping is visible instead of silently
    absent — a fixed list of names shows exactly the paths someone typed.
    """
    counts: Dict[str, int] = {}
    for row in rows or []:
        key = str(row.get("setup_class") or "UNKNOWN")
        counts[key] = counts.get(key, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def join_outcomes(
    stamps: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Join entry stamps to closed-signal records on ``signal_id``.

    Returns ``(joined, coverage)``. Coverage is not decoration: a stamp with no
    record is a signal the router dropped or one still open, and a record with
    no stamp predates this lane. Both populations must be visible, because a
    join that silently keeps only what matched reports a book that is not the
    book.
    """
    by_id = {str(r.get("signal_id") or ""): r for r in records or []}
    joined: List[Dict[str, Any]] = []
    unmatched = 0
    for s in stamps or []:
        rec = by_id.get(str(s.get("signal_id") or ""))
        if rec is None:
            unmatched += 1
            continue
        pnl = _f(rec.get("pnl_pct"))
        sl_pct = _f(rec.get("sl_distance_pct_at_entry"))
        row = dict(s)
        row.update(
            {
                "pnl_pct": pnl,
                "sl_distance_pct_at_entry": sl_pct,
                "r": (pnl / sl_pct) if (pnl is not None and sl_pct and sl_pct > 0) else None,
                "outcome_label": str(rec.get("outcome_label") or ""),
                "hit_sl": bool(rec.get("hit_sl")),
            }
        )
        joined.append(row)
    return joined, {
        "stamps": len(stamps or []),
        "records": len(records or []),
        "joined": len(joined),
        "stamped_not_closed": unmatched,
        "scored": sum(1 for r in joined if r.get("r") is not None),
    }


def missing_by_setup(
    ledger: Optional[EntryFeatureLedger] = None,
) -> Dict[str, Tuple[int, Dict[str, int]]]:
    """``{setup_class: (n_rows, {declared_feature: n_missing})}``.

    The denominator a liveness probe has to use. The paths are wildly uneven —
    MVRTP alone is ~94% of the delivered book — so a TPE-only input that has
    gone dark contributes a handful of Nones against a ledger-wide row count and
    can never reach it. Keyed per path, "absent on every row of its own path" is
    reachable and means what it says.

    **Only features the path DECLARES are counted**, and that is the whole point
    rather than a tidy-up. ``capture`` computes one flat feature block for every
    path, so a value whose input only one path supplies lands on every row as
    ``None``: ``extension_pct`` needs ``ma_slow``, which the two pullback paths
    pass and MEAN_REVERT / MOVER_AVWAP_SCALP / RANGE_FADE do not. Counted raw,
    those three read "absent on every stamp" forever — which is exactly the
    "unused" this probe exists to distinguish dark from, arriving *as* the
    alert. On 2026-08-03 three of its eight flagged items were that, and the
    tell was in the alert itself: the two paths that do supply ``ma_slow`` were
    not among them.

    ``features_for`` is the authority — the same registry ``describe_features``
    ships to ops — so the probe judges a path on the columns the page actually
    draws, and a feature nothing declares is read by nobody and harms nobody if
    it goes dark. The moment a path declares it, it is judged again.
    """
    led = ledger if ledger is not None else get_ledger()
    out: Dict[str, Tuple[int, Dict[str, int]]] = {}
    for row in led.rows():
        setup = str(row.get("setup_class") or "UNKNOWN")
        declared = set(features_for(setup))
        n_rows, missing = out.get(setup, (0, {}))
        for key in row.get("missing") or []:
            if key not in declared:
                continue
            missing[key] = missing.get(key, 0) + 1
        out[setup] = (n_rows + 1, missing)
    return out


def undeclared_absences(
    ledger: Optional[EntryFeatureLedger] = None,
) -> Dict[str, int]:
    """``{feature: n_rows}`` for absences ``missing_by_setup`` deliberately drops.

    The filtering above is a judgement, so it is counted rather than silent — a
    degraded or narrowed mode that leaves no trace is how the *next* reader
    concludes the probe was watching something it was not. Nothing pages on
    this; it is here so the probe can say how much it set aside and a growing
    number can be noticed.
    """
    led = ledger if ledger is not None else get_ledger()
    out: Dict[str, int] = {}
    for row in led.rows():
        declared = set(features_for(str(row.get("setup_class") or "UNKNOWN")))
        for key in row.get("missing") or []:
            if key not in declared:
                out[key] = out.get(key, 0) + 1
    return out


def absence_reasons(
    feature: str,
    setup_class: str,
    ledger: Optional[EntryFeatureLedger] = None,
) -> Dict[str, int]:
    """``{reason: n}`` for why *feature* was absent across one path's rows.

    Empty when the feature records no reason, and the caller must then say
    "cause unrecorded" rather than asserting one — which is the bug this is
    here to retire. ``entry_feature_inputs`` had been reporting
    "upstream is dark" for a column whose ``None`` covers a dark LevelBook, a
    reader that cannot parse the level shape, and a perfectly working read
    whose answer is "nothing overhead". Three causes, three different fixes,
    one sentence asserting the first.
    """
    led = ledger if ledger is not None else get_ledger()
    key = reason_key(feature)
    want = str(setup_class or "")
    out: Dict[str, int] = {}
    for row in led.rows():
        if str(row.get("setup_class") or "UNKNOWN") != want:
            continue
        reason = row.get(key)
        if reason is None:
            continue
        out[str(reason)] = out.get(str(reason), 0) + 1
    return out


def summary(ledger: Optional[EntryFeatureLedger] = None) -> Dict[str, Any]:
    """Liveness-facing shape: is this lane stamping, and how complete is it?"""
    led = ledger if ledger is not None else get_ledger()
    rows = led.rows()
    newest = max((_f(r.get("stamped_at")) or 0.0 for r in rows), default=0.0)
    per_feature_missing: Dict[str, int] = {}
    for r in rows:
        for k in r.get("missing") or []:
            per_feature_missing[k] = per_feature_missing.get(k, 0) + 1
    return {
        "schema": SCHEMA,
        "rows": len(rows),
        "newest_stamp_ts": newest or None,
        "age_sec": (time.time() - newest) if newest else None,
        "duplicate_skips": led.duplicate_skips,
        # Which inputs are absent, and how often. A feature missing on every row
        # is a dead upstream, and it looks identical to a feature nobody uses
        # unless the count is on screen.
        "missing_by_feature": per_feature_missing,
        # Per-path, because the lane now covers several and a healthy total can
        # hide a path that stopped stamping entirely. A watchdog keyed on the
        # aggregate cannot see one path go dark (#815, the same shape).
        "rows_by_setup": dict(setups_present(rows)),
    }
