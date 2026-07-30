"""Parabolic-SAR exit shadow arm (``@SAREXIT``) — forward-measuring the
2026-07-25 bake-off's verdict on live signals, dark and observe-only.

The large-sample exit-method bake-off (``scripts/exit_method_backtest.py``,
102,496 klines-derived entries over 6 months) ranked four exits and only one
was profitable: **Parabolic SAR trailing on 15m bars**, PF 1.60, positive in
7/7 months, all 4 regimes, both directions, 20/20 symbols, and not
outlier-driven (dropping the top 3 trades leaves PF at 1.60).  The other two
trails lost on the identical window (SuperTrend 0.93, ATR 0.72).

**Nothing here changes an exit.**  Per the production dark-first doctrine a
backtest verdict is not a promotion: the next step is forward measurement on
*real live signals* in *real market context*, and that is all this module does.
For every post-scoring candidate the scanner already stamps geometry arms for,
this stamps a second counterfactual **pair** into its own ledger:

    ``SETUP@SARBASE``  — the live evaluator geometry (entry / SL / TP1), static
    ``SETUP@SAREXIT``  — the same entry under a **conditional handover** exit

**What the trail arm does (owner design, 2026-07-27).**  It is not
trail-from-bar-zero.  If the SAR is already onside when the signal fires, the
trail governs immediately.  If the SAR *opposes*, the trade runs on its live
SL/TP1 — bar for bar the control arm — and only if the SAR later comes onside
are those levels dropped and the trail handed control.  If it never comes
onside, the live geometry closes the trade and the two arms agree exactly.

The first cut applied the trail unconditionally, which meant an opposed entry
began behind its own stop and was closed on the first testable bar at that
bar's open.  Measured on 2026-07-27's real feed that was 84% of the opposed
cohort — 119 of 297 candidates whose "exit" was a ~7-minute drift measurement
wearing an exit method's name, dragging a pooled headline that then moved with
the alignment mix rather than with the exit.  Handover also sharpens the A/B:
a trade that never hands over contributes exactly 0 to ``delta_r``, so the
comparison is decided only by trades where SAR actually took over.

Both arms are forward-measured over the **identical window**, which is the
point of the pair.  The bake-off's headline "SAR beats our current exit" was
confounded: the engine baseline got a 100-minute lookahead while the trails got
48 hours — 29× longer.  The trail-vs-trail ranking was clean, the
trail-vs-baseline comparison was not.  Here the control arm gets exactly the
window the trail gets, so the comparison the owner actually has to sign off on
is measured honestly from the first record.

Why the math is a verbatim port:  ``parabolic_sar`` and the trail walk below
are copied from the bake-off script rather than re-derived.  If the shadow arm
and the backtest ever disagreed, we would not know which one was lying — and
the entire value of this arm is that it either confirms or kills a number we
already have.  ``tests/test_sar_exit_shadow.py`` locks the two implementations
together on shared fixtures, so a future edit to either side fails CI.

R normalization: both arms divide by the **live** ``sl_distance``, so the trail
is scored in the same risk units as the stop it would replace.  A trail that
rides further must still pay more R per unit of risk taken to win the A/B.

Cost discipline: stamps are O(1) in-memory appends on suppression/emission
events only (never per scanned symbol); candles are the already-warm in-memory
15m arrays; classification batches on the existing 5-min audit loop.  No
network read, no Firestore read, nothing on a hot path.

Observe-only end to end: evaluator geometry ownership (B7) is untouched, no
record here can reach the signal queue or the position FSM, and *activating* a
SAR exit live remains a separate dark-first, owner-signed change.
"""
from __future__ import annotations

import os
import threading
import time
from typing import (
    Any,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
)

from src.suppression_audit import (
    EXIT_STATIC,
    EXIT_TRAILING,
    PROVENANCE_EMITTED,
    PROVENANCE_ENQUEUED,
    PROVENANCE_SUPPRESSED,
    WOULD_EXPIRE,
    WOULD_LOSE,
    WOULD_WIN,
    SuppressedCandidateStore,
    stamp_candidate,
)
from src.utils import get_logger

log = get_logger("sar_exit_shadow")

# Arm suffixes.  The edge matrix keys on the suffixed strategy name, so each arm
# appears as its own row per context cell.  Registered in
# ``geometry_ab._VARIANT_SUFFIXES`` so the allocator can never *recommend* one —
# a measurement arm is evidence about how to exit a strategy, not an
# activatable strategy.
SARBASE_SUFFIX = "@SARBASE"
SAREXIT_SUFFIX = "@SAREXIT"

GATE_SARBASE = "sar_exit_shadow:base"
GATE_SAREXIT = "sar_exit_shadow:trail"

# v2 (2026-07-26): every record written before this point was resolved by a
# walker that located the entry bar by counting elapsed time, so it replayed a
# different bar than the trade — see ``main.fetch_ohlc_15m_since``.  The whole
# file is evidence of a bug, not of an exit method, so the ledger starts over on
# a new path rather than migrating: there is no field that could rescue a row
# whose candles were wrong.  The v1 file is left on disk for forensics and is
# never read again.
#
# v3 (2026-07-28, owner-approved): same reasoning, different bug.  Every v2 row
# took its trail fill from the *published* SAR level, which on a reversal bar is
# the prior trend's extreme — so the exit landed on the right bar at the bar's
# open instead of at the level price breached.  Measured over 820 real 15m flips
# that overstated each trail exit by a mean **+0.222%**, in the trade's favour
# 95% of the time, which is more than the entire edge the arm was reporting.
# ``r_multiple`` / ``pnl_pct`` / ``delta_r`` on a v2 row are all downstream of
# that fill, so no field can rescue one and a mixed population cannot be pooled.
# Starts over on a new path; v2 is left on disk for forensics and never read.
_DEFAULT_PATH: str = os.getenv("SAR_EXIT_SHADOW_PATH", "data/sar_exit_candidates_v3.json")
_MAX_RECORDS: int = int(os.getenv("SAR_EXIT_SHADOW_MAX_RECORDS", "4000"))

# Exit reasons recorded on the trail arm (diagnostic only).
# Re-exported from the ledger module, which owns them: ``classify_pending``
# needs the same two values to decide whether a mid-window verdict is a real
# exit or just the end of the available candles.  One definition, imported here,
# so the two can never drift.
from src.suppression_audit import (  # noqa: E402
    REASON_STATIC_SL,
    REASON_STATIC_TP1,
    REASON_TRAIL,
    REASON_WINDOW,
)


# ---------------------------------------------------------------------------
# Pure SAR math — ported verbatim from scripts/exit_method_backtest.py
# ---------------------------------------------------------------------------


def parabolic_sar_levels(
    highs: Sequence[float], lows: Sequence[float], step: float, max_step: float
) -> Tuple[List[Optional[float]], List[Optional[float]]]:
    """Parabolic SAR (Wilder), returning **two** series that are not the same thing.

    ``published[i]`` — the indicator value at bar ``i``, i.e. what a chart draws
    and what "which side of price is the SAR on" reads. On a reversal bar this
    is the *post-flip* level: the prior trend's extreme point, which sits on the
    far side of price.

    ``in_force[i]`` — the stop that was actually **live during** bar ``i``: the
    projected-and-clamped level, computed from bars ``< i`` only and therefore
    knowable before the bar trades. This is the price a position is stopped at.

    They are identical on every bar except a reversal, and that exception is the
    whole reason this function exists (2026-07-28). Both simulators previously
    read ``published[i]`` as the stop in force. On a flip bar that is the trend's
    extreme, sitting on the wrong side of price, so ``lows[i] <= stop`` was
    trivially true and the gap-through branch filled at **the bar's open**
    instead of at the level price actually breached. The exit landed on the right
    bar at the wrong price — and because a flip bar normally opens on the
    profitable side of the stop and wicks through it, the error was
    one-directional: measured over 820 real 15m flips across 10 symbols, mean
    **+0.222%** per trail exit, flattering the trade in **95%** of cases (only 1%
    were genuine gap-throughs where filling at the open is correct). That is
    larger than the entire edge the arm was reporting — Session 88's +0.197%
    net/trade corrects to roughly +0.02%.

    *Counterfactuals are optimistic; do not add a third way to flatter them.*

    Implemented on ``_sar_walk`` so the live mechanism (``parabolic_sar_live``)
    and this replay share one walk. Two SAR loops in one module is the drifting
    mirror this repo has already paid for twice.
    """
    published, in_force, _state = _sar_walk(highs, lows, step, max_step)
    return published, in_force


class _SarState(NamedTuple):
    """Wilder's running state after the last closed bar."""

    up: bool
    af: float
    ep: float
    sar: float


def _sar_walk(
    highs: Sequence[float], lows: Sequence[float], step: float, max_step: float
) -> Tuple[List[Optional[float]], List[Optional[float]], Optional[_SarState]]:
    """The one Wilder SAR walk. See ``parabolic_sar_levels`` for the semantics.

    Returns the two series plus the terminal state, which is what a *live*
    reader needs and a replay throws away: the projection of the next bar's
    stop is only computable from ``(up, af, ep, sar)`` as of the last closed
    bar. ``None`` state means the walk never ran (fewer than 2 bars).
    """
    n = len(highs)
    published: List[Optional[float]] = [None] * n
    in_force: List[Optional[float]] = [None] * n
    if n < 2:
        return published, in_force, None
    up = highs[1] >= highs[0]
    af = step
    ep = highs[1] if up else lows[1]
    sar = lows[0] if up else highs[0]
    published[1] = sar
    for i in range(2, n):
        sar = sar + af * (ep - sar)
        if up:
            sar = min(sar, lows[i - 1], lows[i - 2])
            # Clamped, still pre-flip: the level this bar can breach.
            in_force[i] = sar
            if lows[i] < sar:
                up = False
                sar = ep
                ep = lows[i]
                af = step
            else:
                if highs[i] > ep:
                    ep = highs[i]
                    af = min(af + step, max_step)
        else:
            sar = max(sar, highs[i - 1], highs[i - 2])
            in_force[i] = sar
            if highs[i] > sar:
                up = True
                sar = ep
                ep = highs[i]
                af = step
            else:
                if lows[i] < ep:
                    ep = lows[i]
                    af = min(af + step, max_step)
        published[i] = sar
    return published, in_force, _SarState(up=up, af=af, ep=ep, sar=sar)


class SarLive(NamedTuple):
    """What a live SAR mechanism needs to act on the bar that has not closed.

    ``up`` — the direction as of the last **closed** bar.
    ``next_stop`` — the level in force during the bar now forming, projected
    and clamped from closed bars only. This is the price a live stop order
    would be parked at, and it is knowable before the bar trades.
    ``last_closed_ms`` — open time of the last closed bar, so a caller can tell
    a fresh read from a frozen one without wall-clock arithmetic.
    """

    up: bool
    next_stop: float
    last_closed_ms: Optional[float]


def parabolic_sar_live(
    highs: Sequence[float],
    lows: Sequence[float],
    step: float,
    max_step: float,
    last_closed_ms: Optional[float] = None,
) -> Optional[SarLive]:
    """Direction and next-bar stop for a **live** position. Refuses, never clamps.

    ``parabolic_sar_levels`` answers "where was the stop during bar i", which is
    a question only a replay can ask — every bar it reports has already closed.
    A live mechanism has to park a stop on the bar that is *currently trading*,
    and that level is a projection from the closed bars, not an entry in either
    published series.

    This is the **closed bar ≠ current bar** rule made explicit: the store's
    newest bar is the last completed one (``update_candle`` appends on ``k["x"]``
    only), so ``next_stop`` is deliberately one step past the end of the arrays.
    Reading ``in_force[-1]`` instead would park the stop one bar in the past —
    adjacent to the right answer, and on the far side of price across a flip.

    Returns ``None`` when the walk cannot support the projection (fewer than 3
    bars). A caller that cannot get a level must record that it does not know;
    there is no defensible clamp here.
    """
    n = len(highs)
    if n < 3 or len(lows) != n:
        return None
    _published, _in_force, state = _sar_walk(highs, lows, step, max_step)
    if state is None:
        return None
    raw = state.sar + state.af * (state.ep - state.sar)
    nxt = (
        min(raw, lows[n - 1], lows[n - 2])
        if state.up
        else max(raw, highs[n - 1], highs[n - 2])
    )
    return SarLive(up=state.up, next_stop=float(nxt), last_closed_ms=last_closed_ms)


def parabolic_sar(
    highs: Sequence[float], lows: Sequence[float], step: float, max_step: float
) -> List[Optional[float]]:
    """Parabolic SAR (Wilder). Returns the stop-and-reverse level per bar.

    Verbatim port of the bake-off script's implementation — see the module
    docstring for why this is a copy and not a re-derivation. This is the
    **published** series: the indicator, unchanged, pinned across three repos by
    ``tests/test_sar_chart_contract.py``. A simulator that needs the stop a bar
    could actually be filled at wants ``parabolic_sar_levels``' second return
    value instead — they differ on reversal bars.
    """
    return parabolic_sar_levels(highs, lows, step, max_step)[0]


# The SAR needs at least two bars before it produces a level at all
# (``parabolic_sar`` leaves index 0 as None), and a level read off a barely-seeded
# recursion is not worth stamping.  Refuse below this rather than emit a verdict
# nobody should trust.
_MIN_ALIGNMENT_BARS = 10


def _aligned_at(
    series: Sequence[Optional[float]], idx: int, entry: float, side: str
) -> Optional[bool]:
    """Which side of the entry the SAR sat on, at one bar.  Refuses, never clamps.

    The single definition of "agreement", shared by the stamp path and the
    resolve-path cross-check.  Two copies of this comparison is how the two
    silently drift into measuring different things, so there is exactly one.

    A bearish SAR sits ABOVE price, so a LONG taken into one is behind its own
    trailing stop from bar zero.  Returns ``None`` — never ``False`` — when the
    bar cannot answer: out of range, no level yet, or unusable prices.  *A clamp
    is not a guard*: "this input cannot support the computation" must stay
    distinguishable from "the indicator opposed us".
    """
    if idx < 0 or idx >= len(series):
        return None
    level = series[idx]
    if level is None:
        return None
    level = float(level)
    if level <= 0.0 or entry <= 0.0:
        return None
    return (level < entry) if str(side or "").upper() == "LONG" else (level > entry)


def alignment_at_entry(
    *,
    highs: Optional[Sequence[float]],
    lows: Optional[Sequence[float]],
    entry: float,
    side: str,
    step: Optional[float] = None,
    max_step: Optional[float] = None,
) -> Optional[bool]:
    """Was the SAR on our side when the signal fired?  Decided at stamp time.

    This is the whole point of the 2026-07-27 change: the comparison consumes
    **no future candle**.  It reads the indicator level on the last closed bar
    and the entry price, both of which the scanner is holding when it stamps.
    Nothing here needs a resolution 48h later, and nothing here infers an index
    from wall-clock arithmetic — the bug class that produced #800.

    ``highs``/``lows`` are the scanner's warm 15m arrays, which by contract hold
    **closed bars only** (``main.py``: ``if k.get("x")``).  So the last element
    is the last completed bar — the newest SAR level that existed when the
    evaluator decided.  That is deliberately *not* the bar containing the stamp:
    that bar was still forming at entry, so its level is only knowable in
    hindsight and cannot be what "we knew at entry" means.

    Fail-open and refusing: any problem returns ``None``, the record carries no
    verdict, and ops renders "not yet decided" rather than a guess.
    """
    try:
        # Never boolean-test these — they arrive as numpy arrays and truthiness
        # raises (hard limit; tests/test_no_numpy_truthiness_regression.py).
        if highs is None or lows is None:
            return None
        n = len(highs)
        if n < _MIN_ALIGNMENT_BARS or len(lows) != n:
            return None
        entry = float(entry or 0.0)
        if entry <= 0.0:
            return None
        side_u = str(side or "").upper()
        if side_u not in ("LONG", "SHORT"):
            return None
        from config import SAR_EXIT_SHADOW_MAX_STEP, SAR_EXIT_SHADOW_STEP

        series = parabolic_sar(
            [float(h) for h in highs],
            [float(low) for low in lows],
            SAR_EXIT_SHADOW_STEP if step is None else float(step),
            SAR_EXIT_SHADOW_MAX_STEP if max_step is None else float(max_step),
        )
        return _aligned_at(series, n - 1, entry, side_u)
    except Exception as exc:
        from src import fail_open
        fail_open.record("sar_exit_shadow.alignment_at_entry", exc)
        return None


# Stamp-vs-resolve agreement counters.  Not decoration: the two paths compute
# the same quantity from different candle windows, and a persistent disagreement
# means the walker is not reconstructing the bar the scanner saw.  Surfaced by
# the feature-liveness probe so it pages instead of sitting in a file.
_alignment_agree = 0
_alignment_disagree = 0
_alignment_lock = threading.Lock()


def _record_alignment_check(agreed: bool) -> None:
    global _alignment_agree, _alignment_disagree
    with _alignment_lock:
        if agreed:
            _alignment_agree += 1
        else:
            _alignment_disagree += 1


def alignment_crosscheck() -> Dict[str, int]:
    """Agreement counters for the stamp-vs-resolve cross-check (pure read)."""
    with _alignment_lock:
        return {"agree": _alignment_agree, "disagree": _alignment_disagree}


def reset_alignment_crosscheck() -> None:
    """Test hook — the counters are process-lifetime and module-global."""
    global _alignment_agree, _alignment_disagree
    with _alignment_lock:
        _alignment_agree = 0
        _alignment_disagree = 0


def simulate_sar_exit(
    *,
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    opens: Optional[Sequence[float]],
    entry_idx: int,
    entry: float,
    side: str,
    step: float,
    max_step: float,
    max_bars: int,
    bar_minutes: float,
    stop_loss: float = 0.0,
    tp1: float = 0.0,
) -> Optional[Dict[str, Any]]:
    """Replay one signal under the **conditional-handover** SAR exit.

    Owner design, 2026-07-27 — and it is not the same experiment as the
    trail-from-bar-zero arm it replaces:

    * **SAR already onside at entry** → the trail governs immediately, exactly
      as before.
    * **SAR opposed at entry** → the trade runs on its *live* geometry (SL /
      TP1), identical to the ``@SARBASE`` control, and only **if** the SAR
      later comes onside are those levels dropped and the trail handed control
      from the next bar.  If it never comes onside, the live SL/TP1 closes the
      trade and this arm's result equals the control's **by construction**.

    Why the change: the old arm applied the trail from bar zero regardless, so
    an opposed entry sat behind its own stop before it began and was closed on
    the first testable bar at that bar's open.  Measured on 2026-07-27's real
    feed, 84% of the opposed cohort exited in one bar — that population was a
    ~7-minute drift measurement wearing an exit method's name, and pooling it
    with the rides made the arm's headline move with the alignment mix instead
    of with the exit.  Under handover the same trades measure the thing the
    owner actually wants to know: *does letting SAR take over once it agrees
    beat holding the original geometry?*  It also sharpens the A/B — a trade
    that never hands over contributes exactly 0 to ``delta_r``, so the
    comparison isolates the handover decision instead of diluting it.

    Two intrabar rules, both deliberately unflattering (counterfactuals are
    optimistic; do not add a third way to flatter them):

    * A bar that takes out the static stop **and** flips SAR onside is a stop —
      the stop was live at that bar's open.
    * A TP1 touch before handover closes the trade at TP1.  While the static
      leg governs, it governs fully.

    Pure.  Returns ``{exit_price, exit_reason, mfe_pct, hold_min, exit_idx,
    handover_idx, handover_bars, sar_aligned_at_resolve}`` or ``None`` when the
    inputs can't support an honest replay.  Refuses rather than guesses: an
    undecidable entry alignment means we do not know which leg governs, and an
    opposed entry without usable geometry has no static leg to run.

    The exit-fill model is the bake-off's: when a bar *gaps through* a level,
    the fill is the bar's open (worse than the level), not the level itself.
    Without opens the level is used, which is the optimistic read — hence the
    caller supplies opens whenever the data store has them.
    """
    try:
        is_long = str(side or "").upper() == "LONG"
        if str(side or "").upper() not in ("LONG", "SHORT"):
            return None
        entry = float(entry or 0.0)
        n = min(len(highs), len(lows), len(closes))
        if entry <= 0 or n < 3 or entry_idx < 0 or entry_idx >= n:
            return None
        # Two series, deliberately.  ``series`` is the published indicator and
        # answers "which side of price is the SAR on" — alignment, handover.
        # ``stops`` is the level live *during* each bar and is the only thing a
        # fill may be taken at.  Reading the published value as a stop is what
        # filled every trail exit at the bar's open and flattered this arm by
        # ~0.222%/trade (see ``parabolic_sar_levels``).
        series, stops = parabolic_sar_levels(highs, lows, step, max_step)
        if series[entry_idx] is None:
            return None

        # Which leg governs at entry.  Read at ``entry_idx - 1`` — the last bar
        # CLOSED when the signal fired — so this is the same quantity the
        # scanner stamps as ``sar_aligned_at_entry``.  ``None`` means the bar
        # cannot answer, and "which leg governs" is not a question to guess at.
        aligned = _aligned_at(series, entry_idx - 1, entry, side)
        if aligned is None:
            return None
        stop_loss = float(stop_loss or 0.0)
        tp1 = float(tp1 or 0.0)
        static_usable = stop_loss > 0.0 and tp1 > 0.0
        if not aligned and not static_usable:
            return None  # opposed entry with no live geometry to run

        # The walk is bounded to the measurement window; `end` is exclusive.
        end = n if max_bars <= 0 else min(n, entry_idx + 1 + int(max_bars))
        best_fav = entry
        exit_price: Optional[float] = None
        exit_idx: Optional[int] = None
        reason = REASON_WINDOW
        # Handover at the entry bar itself when SAR already agrees: the trail is
        # then testable from the next bar, which is the pre-2026-07-27 behaviour
        # for this cohort, bar for bar.
        handover_idx: Optional[int] = entry_idx if aligned else None

        def _fill(level: float, bar_open: Optional[float]) -> float:
            """Gap-through fill: the worse of the level and the bar's open."""
            if bar_open is None:
                return level
            if is_long:
                return bar_open if bar_open < level else level
            return bar_open if bar_open > level else level

        for i in range(entry_idx, end):
            # The stop that was live during this bar — NOT the published level,
            # which on a reversal bar is the prior trend's extreme sitting on the
            # far side of price.
            stop_level = stops[i]
            # No same-bar exit: the entry bar's levels are what the trade starts
            # behind, not levels it can already have breached.
            if i > entry_idx:
                bar_open = (
                    float(opens[i])
                    if opens is not None and i < len(opens) and float(opens[i] or 0.0) > 0
                    else None
                )
                if handover_idx is None:
                    # ── Static leg: the live geometry, SL before TP1 ──────────
                    if is_long and float(lows[i]) <= stop_loss:
                        exit_price = _fill(stop_loss, bar_open)
                        exit_idx, reason = i, REASON_STATIC_SL
                        break
                    if (not is_long) and float(highs[i]) >= stop_loss:
                        exit_price = _fill(stop_loss, bar_open)
                        exit_idx, reason = i, REASON_STATIC_SL
                        break
                    if is_long and float(highs[i]) >= tp1:
                        exit_price = tp1
                        exit_idx, reason = i, REASON_STATIC_TP1
                        break
                    if (not is_long) and float(lows[i]) <= tp1:
                        exit_price = tp1
                        exit_idx, reason = i, REASON_STATIC_TP1
                        break
                    # Still open — did the indicator come onside on this bar?
                    # Same definition of "onside" as at entry, read against this
                    # bar's close rather than the entry price.  One definition,
                    # two reference prices — never two definitions.
                    if _aligned_at(series, i, float(closes[i]), side) is True:
                        handover_idx = i
                elif stop_level is not None and i > handover_idx:
                    # ── Trail leg: the SAR is the only exit from here ─────────
                    if is_long and float(lows[i]) <= stop_level:
                        exit_price = _fill(stop_level, bar_open)
                        exit_idx, reason = i, REASON_TRAIL
                        break
                    if (not is_long) and float(highs[i]) >= stop_level:
                        exit_price = _fill(stop_level, bar_open)
                        exit_idx, reason = i, REASON_TRAIL
                        break
            if is_long:
                best_fav = max(best_fav, float(highs[i]))
            else:
                best_fav = min(best_fav, float(lows[i]))

        if exit_price is None:
            exit_idx = end - 1
            exit_price = float(closes[exit_idx])
            reason = REASON_WINDOW
        if exit_price <= 0:
            return None

        if is_long:
            mfe = max(0.0, (best_fav - entry) / entry * 100.0)
        else:
            mfe = max(0.0, (entry - best_fav) / entry * 100.0)
        hold_min = max(0.0, float((exit_idx or entry_idx) - entry_idx) * float(bar_minutes))
        # ``aligned`` (computed above, at ``entry_idx - 1``) is the resolve-path
        # cross-check of the value the scanner stamped at entry — the authority
        # remains the stamp.  Read at the last bar CLOSED when the signal fired,
        # not at ``entry_idx``: the resolver's entry bar is the one *containing*
        # the stamp, which was still forming at entry, so its level only exists
        # in hindsight.  Aligning both paths on the last closed bar is what makes
        # the two the same quantity, and therefore what makes a disagreement mean
        # something (2026-07-27).
        return {
            "exit_price": float(exit_price),
            "exit_reason": reason,
            "mfe_pct": float(mfe),
            "hold_min": hold_min,
            "exit_idx": int(exit_idx if exit_idx is not None else entry_idx),
            "sar_aligned_at_resolve": aligned,
            # When control passed to the trail — the fact the whole redesign
            # exists to measure.  ``None`` means it never did, and such a trade
            # is the control arm bar for bar.
            "handover_idx": (None if handover_idx is None else int(handover_idx)),
            "handover_bars": (
                None if handover_idx is None else int(handover_idx - entry_idx)
            ),
        }
    except Exception as exc:
        from src import fail_open
        fail_open.record("sar_exit_shadow.simulate", exc)
        return None


# ---------------------------------------------------------------------------
# Pair ledger — dedicated store so trail volume can't evict gate records
# ---------------------------------------------------------------------------

_sar_store: Optional[SuppressedCandidateStore] = None
_store_lock = threading.Lock()

# Per-(symbol, setup, side) pair cooldown.  ``None`` sentinel, never 0.0 — a
# 0.0 default swallows every stamp for the first COOLDOWN seconds after boot,
# because monotonic() starts near zero on a fresh host (bug class caught in S53
# and re-checked here).
_last_pair_stamp: Dict[Tuple[str, str, str, str], float] = {}

# Stamp-rule generation written onto every row this module produces.  Bumped
# 2026-07-28 with the same-move gate below: rows either side of the bump are
# sampled differently and pooling them silently would repeat the mistake the
# gate exists to fix.  See ``SuppressedCandidateRecord.stamp_schema``.
STAMP_SCHEMA: int = 1

# Last stamp per (symbol, setup, side) — provenance-FREE, unlike the cooldown
# key above.  This is what makes "the same move" a thing the stamp path can
# recognise: entry price, monotonic time, and which provenance last claimed it.
_last_pair_move: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

# Ordering over provenance, used only to decide whether a re-stamp on a move we
# already have carries *new* information.  EMITTED never arrives through the
# stamp path (``promote_to_emitted`` owns it) but is ranked for completeness.
_PROV_RANK: Dict[str, int] = {
    PROVENANCE_SUPPRESSED: 0,
    PROVENANCE_ENQUEUED: 1,
    PROVENANCE_EMITTED: 2,
}


def reset_pair_throttles() -> None:
    """Test hook — both throttle maps are process-lifetime and module-global."""
    _last_pair_stamp.clear()
    _last_pair_move.clear()


def get_sar_store() -> SuppressedCandidateStore:
    global _sar_store
    with _store_lock:
        if _sar_store is None:
            _sar_store = SuppressedCandidateStore(
                persist_path=_DEFAULT_PATH, maxlen=_MAX_RECORDS
            )
        return _sar_store


def is_sar_variant(strategy: str) -> bool:
    """True for ``X@SARBASE`` / ``X@SAREXIT`` measurement rows."""
    s = str(strategy or "")
    return s.endswith(SARBASE_SUFFIX) or s.endswith(SAREXIT_SUFFIX)


def stamp_sar_pair(
    *,
    symbol: str,
    channel: str,
    setup_class: str,
    side: str,
    entry: float,
    stop_loss: float,
    tp1: float,
    confidence: float = 0.0,
    context_key: str = "",
    regime: str = "",
    valid_for_minutes: float = 0.0,
    provenance: str = "",
    highs: Optional[Sequence[float]] = None,
    lows: Optional[Sequence[float]] = None,
    store: Optional[SuppressedCandidateStore] = None,
    now_mono: Optional[float] = None,
) -> bool:
    """Stamp the SARBASE/SAREXIT counterfactual pair for one candidate (fail-open).

    Returns ``True`` when the pair was stamped, else ``False`` (cooldown or bad
    geometry).  Both arms always stamp together — a lone arm biases the A/B.

    ``provenance`` records where the candidate stood at stamp time —
    ``SUPPRESSED`` (a scanner gate killed it) or ``ENQUEUED`` (it passed every
    scanner gate and the queue accepted it).  Both arms of a pair carry the
    same value (they are one candidate).

    **This function never writes EMITTED.**  Whether a queued candidate is
    actually delivered is not known here: the router applies its own gate
    layer afterwards and drops most of what it dequeues.  ``EMITTED`` is
    written only by :func:`promote_to_emitted`, from the router, after
    confirmed delivery — which is what lets the measurement answer "would this
    exit have improved the signals we SENT" separately from "…every candidate
    we considered".  Only the former can justify changing what users receive.

    The trail arm carries the live SL/TP1 for two reasons now.  They have always
    supplied ``sl_distance``, the R denominator both arms share.  Since the
    conditional-handover redesign (2026-07-27) the arm also *runs* on them
    whenever SAR opposes at entry — so the stamp writes nothing new, but the
    levels stopped being "stored and never consulted" and a record missing them
    can no longer be replayed at all when its entry is opposed.
    """
    try:
        setup = str(setup_class or "").strip()
        if not setup or is_sar_variant(setup):
            return False
        entry = float(entry or 0.0)
        stop_loss = float(stop_loss or 0.0)
        tp1 = float(tp1 or 0.0)
        if entry <= 0 or stop_loss <= 0 or tp1 <= 0 or abs(entry - stop_loss) <= 0:
            return False
        side_u = str(side or "").upper()
        if side_u not in ("LONG", "SHORT"):
            return False
        prov = str(provenance or "")
        # The cooldown is keyed by provenance so a *suppressed* stamp cannot
        # swallow a real signal's stamp minutes later (2026-07-25, owner-caught):
        # suppressed candidates outnumber emissions by orders of magnitude, so
        # one shared (symbol, setup, side) budget thinned the emitted sample
        # silently and non-randomly.
        #
        # The EMITTED cooldown bypass that shipped alongside that fix has been
        # REMOVED, because its premise was false. It reasoned that "an emission
        # is a discrete dispatch event, and duplicates are already prevented
        # upstream by dispatch_cooldown" — but this stamp never fired on a
        # dispatch. It fired when ``signal_queue.put`` accepted the candidate,
        # which the router then usually rejected. So the bypass let every
        # re-detection of a persisting setup stamp as EMITTED and *amplified*
        # the very mismatch it was meant to fix (one WLFIUSDT setup produced 5
        # "emitted" rows at an identical entry inside 6.7h).
        #
        # EMITTED now arrives only via :func:`promote_to_emitted`, called by the
        # router after confirmed delivery — at which point the "discrete
        # dispatch event" premise is finally true. The stamp path handles
        # SUPPRESSED and ENQUEUED, and both take the cooldown: both are
        # scan-cycle events on a candidate that may persist for many cycles.
        cd_key = (str(symbol or ""), setup, side_u, prov)
        mono = time.monotonic() if now_mono is None else float(now_mono)
        from config import (
            SAR_EXIT_SHADOW_SAME_MOVE_MAX_SEC,
            SAR_EXIT_SHADOW_SAME_MOVE_PCT,
            SAR_EXIT_SHADOW_STAMP_COOLDOWN_SEC,
        )

        last = _last_pair_stamp.get(cd_key)
        if last is not None and mono - last < SAR_EXIT_SHADOW_STAMP_COOLDOWN_SEC:
            return False

        # ── Same-move gate (2026-07-28) ──────────────────────────────────────
        # The cooldown above bounds the stamp *rate*; it cannot bound how many
        # rows one move contributes, and on a mover setup that persists for
        # hours those are very different numbers.  SLXUSDT SHORT produced 10
        # rows in 2h10m across an entry spread of 0.37% — one setup, one move,
        # one price — and supplied 36% of a whole resolved population.  Counted
        # as written that population read 32% win / −0.364R; one row per move it
        # read 55% / +0.003R.  The sign of the arm's verdict was an artifact of
        # re-detection (owner-caught 2026-07-28).
        #
        # Two things conspired.  The cooldown period is short relative to how
        # long these setups live, AND the cooldown key carries provenance — so a
        # candidate oscillating across a gate boundary holds two budgets and can
        # stamp twice as fast.  All 21 sub-cooldown repeats in the owner's export
        # were provenance flips; zero were genuine cooldown misses.
        #
        # The provenance key is NOT removed: it exists because a suppressed
        # stamp must never swallow a real signal's stamp (2026-07-25), and that
        # reason still holds.  Instead the move itself is tracked, provenance-
        # free, and a re-stamp on a move we already have must carry *new*
        # information to earn a row.  The only new information available here is
        # a provenance upgrade — suppressed→enqueued, this candidate got further
        # than the last time we looked.  That upgrade is allowed exactly once
        # per move (it re-anchors), so the 2026-07-25 fix keeps working while
        # the ratchet stops: SLXUSDT becomes 2 rows, not 10.
        #
        # Bounded in time as well as price: after SAME_MOVE_MAX_SEC the same
        # level is no longer the same move — price can return to it by a
        # different path, and that genuinely is new evidence.
        move_key = (str(symbol or ""), setup, side_u)
        prev = _last_pair_move.get(move_key)
        if prev is not None and float(prev.get("entry") or 0.0) > 0.0:
            prev_entry = float(prev["entry"])
            drift_pct = abs(entry - prev_entry) / prev_entry * 100.0
            age = mono - float(prev.get("mono") or 0.0)
            same_move = (
                drift_pct < float(SAR_EXIT_SHADOW_SAME_MOVE_PCT)
                and age < float(SAR_EXIT_SHADOW_SAME_MOVE_MAX_SEC)
            )
            if same_move:
                prev_rank = _PROV_RANK.get(str(prev.get("prov") or ""), -1)
                if _PROV_RANK.get(prov, -1) <= prev_rank:
                    return False
        target = store or get_sar_store()
        # Computed AFTER the cooldown gate on purpose: the SAR walk is pure CPU
        # over already-warm in-memory arrays (no Firestore, no network, nothing
        # on a hot path), but it should still only run for candidates that
        # actually stamp rather than on every throttled re-detection.
        aligned = alignment_at_entry(
            highs=highs, lows=lows, entry=entry, side=side_u
        )

        def _stamp_arm(gate: str, suffix: str, exit_model: str):
            return stamp_candidate(
                gate_name=gate,
                symbol=str(symbol or ""),
                channel=str(channel or ""),
                setup_class=f"{setup}{suffix}",
                side=side_u,
                entry=entry,
                stop_loss=stop_loss,
                tp1=tp1,
                confidence=float(confidence or 0.0),
                context_key=context_key or "",
                regime=regime or "",
                valid_for_minutes=float(valid_for_minutes or 0.0),
                exit_model=exit_model,
                provenance=str(provenance or ""),
                # Both arms of a pair carry it — they are one candidate with one
                # entry, so the agreement fact is a property of the pair, and a
                # rollup that joins the arms must not have to guess which side
                # holds it.
                sar_aligned_at_entry=aligned,
                stamp_schema=STAMP_SCHEMA,
                store=target,
            )

        # Both arms stamp together or not at all — a lone arm biases the A/B.
        if _stamp_arm(GATE_SARBASE, SARBASE_SUFFIX, EXIT_STATIC) is None:
            return False
        if _stamp_arm(GATE_SAREXIT, SAREXIT_SUFFIX, EXIT_TRAILING) is None:
            return False
        _last_pair_stamp[cd_key] = mono
        # Re-anchor the move on every accepted stamp, including a provenance
        # upgrade — that is what spends the one upgrade a move is allowed.
        _last_pair_move[move_key] = {"entry": entry, "mono": mono, "prov": prov}
        # Bounded: one entry per live (symbol, setup, side), and the universe is
        # 75 pairs. The sweep is belt-and-braces against a pathological run.
        if len(_last_pair_move) > 4096:
            floor = mono - float(SAR_EXIT_SHADOW_SAME_MOVE_MAX_SEC)
            for stale in [
                k for k, v in _last_pair_move.items()
                if float(v.get("mono") or 0.0) < floor
            ]:
                _last_pair_move.pop(stale, None)
        return True
    except Exception as exc:
        from src import fail_open
        fail_open.record("sar_exit_shadow.stamp_pair", exc)
        return False


def promote_to_emitted(
    *,
    symbol: str,
    setup_class: str,
    side: str,
    entry: float,
    store: Optional[SuppressedCandidateStore] = None,
    max_age_sec: Optional[float] = None,
) -> int:
    """Mark a candidate's arms EMITTED after the router confirmed delivery.

    This is the only writer of ``PROVENANCE_EMITTED`` (2026-07-25 fix). The
    scanner stamps ``ENQUEUED`` when the queue accepts a candidate; the router
    calls this once it has actually posted the signal. Everything that never
    gets here stays ``ENQUEUED``, which is the honest label for "we considered
    it, we queued it, and our own routing caps dropped it".

    Returns the number of arm records promoted — 2 on the normal path (both
    ``@SARBASE`` and ``@SAREXIT``), 0 when no matching stamp is in the window.
    A 0 is not an error: the stamp cooldown may legitimately have throttled a
    re-detected setup, and the earlier arms for that same candidate are already
    in the ledger.

    Fail-open: a measurement re-label must never break dispatch.
    """
    try:
        setup = str(setup_class or "").strip()
        if not setup or is_sar_variant(setup):
            return 0
        from src.suppression_audit import (
            PROVENANCE_EMITTED,
            PROVENANCE_ENQUEUED,
        )

        if max_age_sec is None:
            # Generous relative to the scanner→router hop (sub-second in
            # practice) but bounded so a promotion can never reach a candidate
            # from an earlier, unrelated detection of the same setup.
            from config import SAR_EXIT_SHADOW_STAMP_COOLDOWN_SEC
            max_age_sec = max(300.0, float(SAR_EXIT_SHADOW_STAMP_COOLDOWN_SEC))
        target = store or get_sar_store()
        return target.promote_provenance(
            symbol=str(symbol or ""),
            side=str(side or ""),
            # Both arms share the base setup as their prefix, so one call
            # promotes the pair together.
            setup_prefix=setup,
            entry=float(entry or 0.0),
            from_provenance=PROVENANCE_ENQUEUED,
            to_provenance=PROVENANCE_EMITTED,
            max_age_sec=float(max_age_sec),
        )
    except Exception as exc:
        from src import fail_open
        fail_open.record("sar_exit_shadow.promote_to_emitted", exc)
        return 0


# ---------------------------------------------------------------------------
# Resolver candle health — the ledger's data dependency, made visible
# ---------------------------------------------------------------------------
#
# ``classify_pending`` treats a mid-window candle fetch that returns nothing as
# "not yet", which is right — mid-window the bars may genuinely not exist.  But
# it is also silent: no counter, no log, no ``fail_open`` entry.  A record whose
# candles will *never* arrive is therefore indistinguishable from one stamped a
# minute ago, for two full days, after which it flips to INSUFFICIENT with no
# stated cause.  That is how four mover rows sat at RUNNING showing marks of
# −6% to −10% while the trades they describe had already stopped out at their
# 3% cap hours earlier (owner-caught 2026-07-28 on /signals/sar).
#
# The liveness probe could not have caught it either: ``candle_coverage`` walks
# ``pair_mgr.pairs``, the *current* universe, and a rotated-out mover is not in
# it.  The one watchdog whose job is noticing a feature flat-line was blind to
# this by construction.  So the ledger counts its own data dependency here, and
# ``main`` registers a probe that reads the population that actually matters:
# the symbols we still owe a verdict on.
#
# Counters are per classify-cycle, not cumulative: a cumulative miss count never
# recovers after a transient outage, so it would page forever over a fault that
# healed.  ``roll_candle_fetch_cycle`` moves the live bucket to ``last`` at the
# end of each batch; the probe reads ``last``.

_candle_cur: Dict[str, Any] = {"ok": 0, "miss": 0, "reasons": {}, "symbols": {}}
_candle_last: Dict[str, Any] = {"ok": 0, "miss": 0, "reasons": {}, "symbols": {}}
_candle_lock = threading.Lock()

# Bound the per-symbol map: one entry per symbol with an unresolved record, and
# the ledger itself is capped at _MAX_RECORDS.  The cap is belt-and-braces
# against a pathological universe, not an expected path.
_CANDLE_SYMBOL_CAP = 256


def record_candle_fetch(symbol: str, ok: bool, reason: str = "") -> None:
    """Count one resolver candle fetch.  Pure bookkeeping — never raises."""
    try:
        sym = str(symbol or "?")
        with _candle_lock:
            if ok:
                _candle_cur["ok"] = int(_candle_cur["ok"]) + 1
                _candle_cur["symbols"].pop(sym, None)
                return
            _candle_cur["miss"] = int(_candle_cur["miss"]) + 1
            why = str(reason or "unknown")
            reasons = _candle_cur["reasons"]
            reasons[why] = int(reasons.get(why, 0)) + 1
            symbols = _candle_cur["symbols"]
            if sym in symbols or len(symbols) < _CANDLE_SYMBOL_CAP:
                symbols[sym] = why
    except Exception as exc:
        from src import fail_open
        fail_open.record("sar_exit_shadow.record_candle_fetch", exc)


def roll_candle_fetch_cycle() -> None:
    """Publish this cycle's counters and start a fresh bucket."""
    global _candle_cur, _candle_last
    with _candle_lock:
        _candle_last = _candle_cur
        _candle_cur = {"ok": 0, "miss": 0, "reasons": {}, "symbols": {}}


def candle_fetch_health() -> Dict[str, Any]:
    """Last completed cycle's resolver candle health (pure read)."""
    with _candle_lock:
        last = _candle_last
        return {
            "ok": int(last["ok"]),
            "miss": int(last["miss"]),
            "reasons": dict(last["reasons"]),
            "symbols": dict(last["symbols"]),
        }


def reset_candle_fetch_health() -> None:
    """Test hook — the counters are process-lifetime and module-global."""
    global _candle_cur, _candle_last
    with _candle_lock:
        _candle_cur = {"ok": 0, "miss": 0, "reasons": {}, "symbols": {}}
        _candle_last = {"ok": 0, "miss": 0, "reasons": {}, "symbols": {}}


# ---------------------------------------------------------------------------
# Refresh-budget accounting (2026-07-29)
# ---------------------------------------------------------------------------
# ``record_candle_fetch`` above answers "could we fetch the window we asked
# for".  It cannot answer "did we ask at all", and that is the failure the
# owner's 2026-07-29 export actually caught: the refresh loop takes the first
# ``MAX_PER_CYCLE`` due symbols off an *oldest-stamp-first* list and ``break``s.
# The symbols past the cap were never fetched, so they were never counted as a
# miss either — the fetch health read a clean 100% while 61 of 85 ledger
# symbols were being starved of candles every single cycle.
#
# A truncation that discards work must say how much it discarded, or a budget
# that is too small looks exactly like a budget that is exactly right.  The
# shortfall is knowable at the truncation point and nowhere later, so it is
# counted there.
#
# Per-cycle like the fetch counters, and for the same reason: a cumulative
# starvation count never recovers after the ledger drains, so it would page
# forever over a fault that healed.

_budget_cur: Dict[str, int] = {"due": 0, "served": 0, "starved": 0, "pending": 0}
_budget_last: Dict[str, int] = {"due": 0, "served": 0, "starved": 0, "pending": 0}
_budget_lock = threading.Lock()


def record_refresh_budget(
    *, due: int, served: int, starved: int, pending: int
) -> None:
    """Record one refresh cycle's budget outcome.  Never raises.

    ``due`` — symbols eligible for a refresh this cycle (stale enough and past
    their per-symbol throttle).  ``served`` — how many the budget allowed.
    ``starved`` — eligible symbols the cap turned away.  ``pending`` — every
    symbol still owed a verdict, whether due this cycle or not.
    """
    try:
        with _budget_lock:
            _budget_cur["due"] = int(due)
            _budget_cur["served"] = int(served)
            _budget_cur["starved"] = int(starved)
            _budget_cur["pending"] = int(pending)
    except Exception as exc:
        from src import fail_open
        fail_open.record("sar_exit_shadow.record_refresh_budget", exc)


def roll_refresh_budget_cycle() -> None:
    """Publish this cycle's budget counters and start a fresh bucket."""
    global _budget_cur, _budget_last
    with _budget_lock:
        _budget_last = _budget_cur
        _budget_cur = {"due": 0, "served": 0, "starved": 0, "pending": 0}


def refresh_budget_health() -> Dict[str, int]:
    """Last completed cycle's refresh-budget outcome (pure read)."""
    with _budget_lock:
        return dict(_budget_last)


def reset_refresh_budget_health() -> None:
    """Test hook — the counters are process-lifetime and module-global."""
    global _budget_cur, _budget_last
    with _budget_lock:
        _budget_cur = {"due": 0, "served": 0, "starved": 0, "pending": 0}
        _budget_last = {"due": 0, "served": 0, "starved": 0, "pending": 0}


# ---------------------------------------------------------------------------
# Resolution-progress accounting (2026-07-29)
# ---------------------------------------------------------------------------
# The two counters above answer "could we fetch candles" and "did we ask".
# Neither answers the question an owner actually has, which is "is this ledger
# producing verdicts at all".  On 2026-07-29 the answer was no for 11.6 hours
# and every probe stayed green.
#
# A *rate* of stalled records is the wrong signal here and it is worth being
# explicit about why: mid-window stalling is the healthy steady state.  A
# ledger holding 400 open records will stall on nearly all of them every cycle,
# forever, because their trades have not closed yet.  A probe that pages on
# "most records stalled" would page constantly on a perfectly healthy arm.
#
# What separates healthy from frozen is *progress*: in a working ledger some
# records resolve every cycle (the owner's export shows 6-25 per hour).  Zero
# resolutions against a non-empty backlog, sustained for an hour, is the
# freeze — and it cannot be confused with a quiet market, because the backlog
# being non-empty is the precondition.

_resolve_cur: Dict[str, int] = {"resolved": 0, "stalled": 0, "pending": 0}
_resolve_last: Dict[str, int] = {"resolved": 0, "stalled": 0, "pending": 0}
_resolve_lock = threading.Lock()


def record_resolution_cycle(*, resolved: int, stalled: int, pending: int) -> None:
    """Record one classify cycle's progress.  Never raises.

    ``resolved`` — records that got a verdict this cycle.  ``stalled`` — records
    that had candles and still produced none.  ``pending`` — records still owed
    a verdict and still inside their window, the population at risk.
    """
    try:
        with _resolve_lock:
            _resolve_cur["resolved"] = int(resolved)
            _resolve_cur["stalled"] = int(stalled)
            _resolve_cur["pending"] = int(pending)
    except Exception as exc:
        from src import fail_open
        fail_open.record("sar_exit_shadow.record_resolution_cycle", exc)


def roll_resolution_cycle() -> None:
    """Publish this cycle's progress counters and start a fresh bucket."""
    global _resolve_cur, _resolve_last
    with _resolve_lock:
        _resolve_last = _resolve_cur
        _resolve_cur = {"resolved": 0, "stalled": 0, "pending": 0}


def resolution_health() -> Dict[str, int]:
    """Last completed cycle's resolution progress (pure read)."""
    with _resolve_lock:
        return dict(_resolve_last)


def reset_resolution_health() -> None:
    """Test hook — the counters are process-lifetime and module-global."""
    global _resolve_cur, _resolve_last
    with _resolve_lock:
        _resolve_cur = {"resolved": 0, "stalled": 0, "pending": 0}
        _resolve_last = {"resolved": 0, "stalled": 0, "pending": 0}


def unresolved_record_count(
    *, window_sec: float, now_ts: Optional[float] = None
) -> int:
    """Records still owed a verdict and still inside their window.

    The denominator ``unresolved_symbols`` does not give: a symbol carrying 40
    stuck records and one carrying 1 are the same entry there, and the harm
    scales with records, not symbols.
    """
    try:
        now = time.time() if now_ts is None else float(now_ts)
        cutoff = now - float(window_sec)
        total = 0
        for rec in get_sar_store().records():
            if rec.get("classification") is not None:
                continue
            ts = float(rec.get("suppress_timestamp") or 0.0)
            if ts <= 0.0 or ts < cutoff:
                continue
            total += 1
        return total
    except Exception as exc:
        from src import fail_open
        fail_open.record("sar_exit_shadow.unresolved_record_count", exc)
        return 0


def plan_refresh_batch(
    symbols: Sequence[str],
    *,
    last_refresh_at: Dict[str, float],
    age_seconds: Callable[[str], Optional[float]],
    now_mono: float,
    refresh_sec: float,
    max_per_cycle: int,
) -> Tuple[List[str], int]:
    """Choose this cycle's refresh batch → ``(due, starved)``.

    ``symbols`` arrives oldest-unresolved-first and that order is preserved:
    a bounded budget is spent on the records closest to ageing out of their
    window.  A symbol is skipped when it was refreshed within ``refresh_sec``
    (per-symbol throttle) or when its 15m array is already fresher than that
    (nothing new to fetch).  ``age_seconds`` returning ``None`` means "never
    stamped", which is not evidence of freshness — those are refreshed.

    ``starved`` counts symbols that were eligible but turned away by
    ``max_per_cycle``.  It exists because the loop this replaces ``break``ed at
    the cap, so a budget too small for the ledger was indistinguishable from
    one that fit — the starved symbols were never fetched and so were never
    counted as a fetch miss either.  Every caller must publish this number.

    Pure apart from ``age_seconds``, which reads the in-memory candle store.
    """
    due: List[str] = []
    starved = 0
    cap = int(max_per_cycle)
    for sym in symbols:
        if now_mono - float(last_refresh_at.get(sym, 0.0)) < float(refresh_sec):
            continue
        age = age_seconds(sym)
        if age is not None and float(age) <= float(refresh_sec):
            continue
        if len(due) >= cap:
            starved += 1
            continue
        due.append(sym)
    return due, starved


def unresolved_symbols(
    *, window_sec: float, now_ts: Optional[float] = None, limit: Optional[int] = None
) -> List[str]:
    """Symbols carrying a still-resolvable, still-unresolved ledger record.

    Ordered **oldest stamp first**, so a bounded per-cycle refresh budget is
    spent on the records closest to ageing out of their window rather than on
    whichever symbol happens to sort first.

    Records past their window are excluded: their verdict is already decided
    (``classify_pending`` marks them INSUFFICIENT on the next pass), so
    refreshing their candles would buy nothing and burn REST weight.
    """
    try:
        now = time.time() if now_ts is None else float(now_ts)
        cutoff = now - float(window_sec)
        oldest: Dict[str, float] = {}
        for rec in get_sar_store().records():
            if rec.get("classification") is not None:
                continue
            ts = float(rec.get("suppress_timestamp") or 0.0)
            if ts <= 0.0 or ts < cutoff:
                continue
            sym = str(rec.get("symbol") or "")
            if not sym:
                continue
            prev = oldest.get(sym)
            if prev is None or ts < prev:
                oldest[sym] = ts
        ordered = [s for s, _ in sorted(oldest.items(), key=lambda kv: kv[1])]
        if limit is not None and limit >= 0:
            ordered = ordered[: int(limit)]
        return ordered
    except Exception as exc:
        from src import fail_open
        fail_open.record("sar_exit_shadow.unresolved_symbols", exc)
        return []


# ---------------------------------------------------------------------------
# Trail classifier — the hook handed to SuppressedCandidateStore.classify_pending
# ---------------------------------------------------------------------------


def classify_sar_record(
    record: Dict[str, Any], ohlc: Dict[str, List[float]]
) -> Optional[Dict[str, Any]]:
    """Resolve one ``@SAREXIT`` record by walking its SAR trail (pure).

    ``ohlc`` carries a pre-entry **warmup prefix** so the SAR has converged by
    the time the trade starts; ``entry_index`` says where the trade begins.
    Without that prefix the first bars of every trade would be measured against
    a SAR still seeded from its own first two bars, which is not the indicator
    the bake-off measured.

    ``post_price_max`` / ``post_price_min`` are computed over the **post-entry**
    slice only, so the warmup bars never leak into the recorded excursion.
    """
    from config import (
        SAR_EXIT_SHADOW_BAR_MINUTES,
        SAR_EXIT_SHADOW_MAX_STEP,
        SAR_EXIT_SHADOW_STEP,
        SAR_EXIT_SHADOW_WINDOW_BARS,
    )

    highs = ohlc.get("high")
    lows = ohlc.get("low")
    closes = ohlc.get("close")
    opens = ohlc.get("open")
    if highs is None or lows is None or closes is None:
        return None
    if len(highs) == 0 or len(lows) == 0 or len(closes) == 0:
        return None
    entry_idx = int(ohlc.get("entry_index") or 0)  # type: ignore[arg-type]
    result = simulate_sar_exit(
        highs=highs,
        lows=lows,
        closes=closes,
        opens=opens,
        entry_idx=entry_idx,
        entry=float(record.get("entry") or 0.0),
        side=str(record.get("side") or ""),
        step=SAR_EXIT_SHADOW_STEP,
        max_step=SAR_EXIT_SHADOW_MAX_STEP,
        max_bars=SAR_EXIT_SHADOW_WINDOW_BARS,
        bar_minutes=SAR_EXIT_SHADOW_BAR_MINUTES,
        # The live geometry stopped being "levels it never consults" on
        # 2026-07-27: under conditional handover the trade runs on them until
        # the indicator comes onside.  They were already carried on the record
        # as the shared R denominator, so nothing new is stored — what changed
        # is that this arm now reads them.
        stop_loss=float(record.get("stop_loss") or 0.0),
        tp1=float(record.get("tp1") or 0.0),
    )
    if result is None:
        return None

    entry = float(record.get("entry") or 0.0)
    exit_price = float(result["exit_price"])
    is_long = str(record.get("side") or "").upper() == "LONG"
    move = (exit_price - entry) if is_long else (entry - exit_price)
    # The label stays in the ledger's shared vocabulary so the edge matrix and
    # every existing consumer read it without a special case.  For a trailing
    # arm it is the *sign* of the realized exit, not a TP1-vs-SL race:
    # WOULD_EXPIRE means the trail never fired inside the window.
    if str(result["exit_reason"]) == REASON_WINDOW:
        label = WOULD_EXPIRE
    else:
        label = WOULD_WIN if move > 0 else WOULD_LOSE

    post_high = max(float(h) for h in highs[entry_idx:]) if len(highs) > entry_idx else 0.0
    post_low = min(float(low) for low in lows[entry_idx:]) if len(lows) > entry_idx else 0.0
    # Cross-check, not overwrite.  ``sar_aligned_at_entry`` was decided when the
    # signal fired and is never touched here; this records what the replay
    # window thinks and counts whether the two agree.  A sustained disagreement
    # is the walker failing to reconstruct the bar the scanner saw — #800's
    # failure mode, turned into something that reports on itself.  Tri-state is
    # preserved: None means the replay could not decide, not "opposed".
    resolved_alignment = result["sar_aligned_at_resolve"]
    stamped_alignment = record.get("sar_aligned_at_entry")
    if resolved_alignment is not None and stamped_alignment is not None:
        agreed = bool(resolved_alignment) == bool(stamped_alignment)
        _record_alignment_check(agreed)
        if not agreed:
            log.warning(
                "SAR alignment cross-check disagreed: {} {} stamped={} resolved={}",
                record.get("symbol"), record.get("side"),
                stamped_alignment, resolved_alignment,
            )
    return {
        "classification": label,
        "trail_exit_price": exit_price,
        "trail_mfe_pct": float(result["mfe_pct"]),
        "trail_hold_min": float(result["hold_min"]),
        "trail_exit_reason": str(result["exit_reason"]),
        "sar_aligned_at_resolve": resolved_alignment,
        # Did control ever pass to the trail, and how late?  ``None`` = never,
        # which means this row is the control arm bar for bar and contributes
        # exactly 0 to delta_r — the population that makes the A/B readable.
        "sar_handover_bars": result.get("handover_bars"),
        "post_price_max": post_high,
        "post_price_min": post_low,
        "post_price_final": float(closes[-1]),
    }


# ---------------------------------------------------------------------------
# Rollup for ops / the truth report
# ---------------------------------------------------------------------------


def summarize_sar_alignment(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Split resolved ``@SAREXIT`` rows by whether SAR agreed with us at entry.

    Why this is still not one number — but for a different reason than it was
    (rewritten 2026-07-27 for the conditional-handover design).  Alignment at
    entry now decides **which leg the trade starts on**, so the two buckets
    still describe different experiments:

    * **aligned** — the trail governed from bar one.  A pure measurement of the
      exit method, and identical to what this arm always measured here.
    * **opposed** — the trade started on its live SL/TP1 and only switched if
      SAR came onside.  Its result is the control arm's *unless* a handover
      happened, so its avg-R is dominated by the live geometry, not by SAR.

    What is no longer true: the old docstring called the opposed bucket "a
    near-deterministic loss" because the trail was applied from bar zero even
    when its level sat on the wrong side of price.  Under handover that is
    simply not what happens, and the copy went with the design — a panel that
    asserts a cause its numbers no longer show is wrong on screen even when
    every figure in it is right.

    ``handover`` counts the rows where control actually passed to the trail.
    That is the population the A/B lives on: a row that never handed over
    contributes exactly 0 to ``delta_r`` by construction, so a shrinking
    handover share means the comparison is being decided by fewer trades than
    the totals suggest.

    Pure.  Returns per-bucket n / win-rate / avg-R / avg-hold, the opposed
    share, and the handover counts.
    """
    buckets: Dict[str, Dict[str, float]] = {
        k: {"n": 0.0, "wins": 0.0, "r_sum": 0.0, "hold_sum": 0.0} for k in ("aligned", "opposed")
    }
    handover_n = 0
    handover_bars_sum = 0.0
    resolved_n = 0
    for rec in records or []:
        if not str(rec.get("setup_class", "")).endswith(SAREXIT_SUFFIX):
            continue
        if rec.get("classification") is None:
            continue
        # Reads the STAMP-time value. Never falls back to the resolve-time
        # cross-check: a fallback would quietly re-introduce the resolution
        # dependency this change exists to remove, and would mix two windows in
        # one bucket the moment they ever disagreed.
        flag = rec.get("sar_aligned_at_entry")
        if flag is None:
            continue  # stamped before the entry-time flag, or undecidable then
        b = buckets["aligned" if flag else "opposed"]
        b["n"] += 1
        r = float(rec.get("r_multiple") or 0.0)
        b["r_sum"] += r
        b["wins"] += 1.0 if r > 0 else 0.0
        b["hold_sum"] += float(rec.get("trail_hold_min") or 0.0)
        resolved_n += 1
        # ``None`` = control passed to the trail never; 0 = at the entry bar.
        # Test for None explicitly: 0 is a real handover and the falsiest of
        # values, which is exactly how it would go missing.
        hb = rec.get("sar_handover_bars")
        if hb is not None:
            handover_n += 1
            handover_bars_sum += float(hb)

    def _out(b: Dict[str, float]) -> Dict[str, Any]:
        n = b["n"]
        return {
            "n": int(n),
            "win_rate": (b["wins"] / n) if n else 0.0,
            "avg_r": (b["r_sum"] / n) if n else 0.0,
            "avg_hold_min": (b["hold_sum"] / n) if n else 0.0,
        }

    aligned = _out(buckets["aligned"])
    opposed = _out(buckets["opposed"])
    total = aligned["n"] + opposed["n"]
    return {
        "aligned": aligned,
        "opposed": opposed,
        "total": total,
        "opposed_share": (opposed["n"] / total) if total else 0.0,
        # Rows where the trail actually took control — the only ones that can
        # differ from the control arm at all.
        "handover_n": handover_n,
        "handover_share": (handover_n / resolved_n) if resolved_n else 0.0,
        "avg_handover_bars": (handover_bars_sum / handover_n) if handover_n else 0.0,
    }


def summarize_sar_exit(matrix: Dict[str, Dict], *, min_sample: int = 15) -> List[Dict]:
    """Per-strategy live-geometry-vs-SAR-trail rollup from edge-matrix cells (pure).

    Pools each arm's cells across contexts (sample-weighted) and names a leader
    only when BOTH arms clear ``min_sample`` — an A/B with one thin arm is
    MEASURING, not evidence.  This is the table the owner's activation decision
    reads, so "not enough data yet" has to be a first-class answer, never an
    accidental 0-sample "SAR wins".
    """
    pooled: Dict[str, Dict[str, Dict[str, float]]] = {}
    for cell in (matrix or {}).values():
        strategy = str(cell.get("strategy", ""))
        if strategy.endswith(SAREXIT_SUFFIX):
            arm = "sar"
        elif strategy.endswith(SARBASE_SUFFIX):
            arm = "base"
        else:
            continue
        base = strategy[: -len(SAREXIT_SUFFIX if arm == "sar" else SARBASE_SUFFIX)]
        n = int(cell.get("n", 0) or 0)
        if n <= 0:
            continue
        agg = pooled.setdefault(base, {}).setdefault(
            arm, {"n": 0.0, "wins": 0.0, "r_sum": 0.0, "cells": 0.0}
        )
        agg["n"] += n
        agg["wins"] += float(cell.get("win_rate", 0.0) or 0.0) * n
        agg["r_sum"] += float(cell.get("avg_r", 0.0) or 0.0) * n
        agg["cells"] += 1

    rows: List[Dict] = []
    for base, arms in pooled.items():

        def _arm(name: str) -> Dict[str, float]:
            a = arms.get(name, {"n": 0.0, "wins": 0.0, "r_sum": 0.0, "cells": 0.0})
            n = a["n"]
            return {
                "n": int(n),
                "cells": int(a["cells"]),
                "win_rate": (a["wins"] / n) if n else 0.0,
                "avg_r": (a["r_sum"] / n) if n else 0.0,
            }

        base_arm = _arm("base")
        sar_arm = _arm("sar")
        measured = base_arm["n"] >= min_sample and sar_arm["n"] >= min_sample
        delta = sar_arm["avg_r"] - base_arm["avg_r"]
        rows.append(
            {
                "strategy": base,
                "base": base_arm,
                "sar": sar_arm,
                "delta_r": delta if measured else None,
                "leader": (
                    ("SAR" if delta > 0 else "LIVE" if delta < 0 else "TIE")
                    if measured
                    else "MEASURING"
                ),
            }
        )
    rows.sort(
        key=lambda r: abs(r["delta_r"]) if r["delta_r"] is not None else -1.0,
        reverse=True,
    )
    return rows
