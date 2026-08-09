"""The trailing-exit mechanisms the live arm engine can run, behind one seam.

**Why this module exists.** ``sar_live_shadow`` is the most carefully guarded
lane in this repo — six sessions bought the anchor check (#836), the per-advance
replay guard (#846), the regressed-vs-rolled-off split, the stall stamps (#835),
the timestamp-monotonicity refusal (#842/#844), the two fills and the two
denominators. The owner asked (2026-08-09) for *"exactly the same"* measurement
of an ATR trail, and the one thing that must not happen is a second two-thousand
line module carrying a second copy of those guards. **The fix for a drifting
mirror is not a second mirror** — this repo has paid for that under six names.

So the arm engine stays exactly where it is and gains a *mechanism* dimension.
Everything mechanism-specific — "given the bars closed so far, where would the
stop be parked for the bar now forming, and can it govern this trade yet" — is
here, and it is the only thing either mechanism gets to decide. The anchor,
the walk, the fills, the held arm, the stop-management rules, the ledger, the
sweep and every guard above are shared, once.

The two mechanisms
------------------
``sar``
    Wilder's Parabolic SAR, delegated verbatim to
    :func:`sar_exit_shadow.parabolic_sar_live` — the same function the replay
    arm, the reconciler and the Lumin chart study read, pinned across three
    repos. SAR carries its **own direction**, so "can it govern" is the
    indicator's direction agreeing with the trade's side.

``chandelier``
    Chuck LeBeau's Chandelier Exit: the running favourable extreme since the arm
    opened, less ``mult`` ATRs. **Position-scoped, not indicator-scoped**, and
    that choice is load-bearing. TradingView's popular Chandelier study is
    indicator-scoped (highest high of the last N bars, with a close-cross
    direction flip); ops' exit bake-off — the surface that has printed the words
    *"ATR-trail (Chandelier)"* since long before this module — ratchets from the
    **entry bar**. Two arms named for the same mechanism measuring different
    mechanisms is a defect this repo already paid for on 2026-07-31, when the
    dark ``sar_*`` replay and the live SAR arm agreed on the easy 79% and
    diverged by +0.73pp on the 21% where their definitions differed. So this is
    the bake-off's definition, and ``tests/test_trail_mechanisms.py`` pins the
    level series against a vector shared with ops.

What a mechanism may and may not do
-----------------------------------
* It returns a level for the bar that has **not closed yet**. Reading a level
  off the last closed bar parks the stop one bar in the past — adjacent to the
  right answer and, across a flip, on the far side of price.
* It **refuses** rather than clamps. Fewer bars than the walk needs returns
  ``None``, and the arm records that it does not know. ``INSUFFICIENT`` is a
  state; a guessed level is a wrong answer with no signal (#800).
* It never widens a stop it has already parked. A trailing stop that can move
  away from price hands the trade more risk than it was sized for.
* It carries no I/O, no logging and no clock. Every guard about *when* a bar
  closed lives in the arm engine, which is the only place that can see the
  arm's history.

Why ``onside`` is a mechanism decision and not a shared one
-----------------------------------------------------------
The arm engine asks one question at the anchor and again on every bar while the
original geometry is still governing: *may this mechanism take over?* For SAR
that is the indicator's own direction — a bearish SAR sits above price, so a
LONG taken into one is behind its own trailing stop from bar zero. A chandelier
has no direction of its own, so the equivalent question is whether the level it
would park is already breached by the bar's close. Sharing one definition would
force one of the two mechanisms to answer a question it cannot ask.
"""
from __future__ import annotations

from typing import Any, Dict, List, NamedTuple, Optional, Sequence, Tuple

from src.sar_exit_shadow import parabolic_sar_live

#: Mechanism keys. These are written onto every arm row and into the ledger's
#: manifest, so they are a cross-repo contract — ops labels a row from the
#: manifest and renders an unknown key under its raw name rather than guessing.
MECH_SAR = "sar"
MECH_CHANDELIER = "chandelier"

MECHANISMS: Tuple[str, ...] = (MECH_SAR, MECH_CHANDELIER)


class TrailPoint(NamedTuple):
    """What a live trailing mechanism needs to hand the arm engine.

    ``next_stop``
        The level in force during the bar now forming, projected from closed
        bars only. This is the price a live stop order would be parked at, and
        it is knowable before the bar trades.
    ``up``
        The mechanism's own direction, where it has one (SAR). ``None`` for a
        mechanism that has none — never ``False``, because "this mechanism does
        not answer that" and "this mechanism says down" are different facts and
        a surface that pools them reports a direction nobody computed.
    ``onside``
        May this mechanism govern the trade right now. See the module docstring
        for why each mechanism answers it differently.
    """

    next_stop: float
    up: Optional[bool]
    onside: bool


def _is_long(side: str) -> bool:
    return str(side or "").upper() == "LONG"


# --------------------------------------------------------------------------- #
# ATR — one definition, cross-checked against the two that already existed
# --------------------------------------------------------------------------- #


def wilder_atr(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    period: int,
) -> List[Optional[float]]:
    """Wilder-smoothed ATR, ``None`` until the seed window has closed.

    A list-based ATR rather than ``indicators.atr``'s numpy one because this
    walk consumes the plain lists ``sar_live_shadow._series`` hands out, and
    round-tripping them through numpy per bar on the monitor loop is cost for
    nothing. It is the **same** definition — seeded with the mean of the first
    ``period`` true ranges and smoothed from there — and
    ``tests/test_trail_mechanisms.py`` asserts it element-for-element against
    ``indicators.atr`` on real candles rather than trusting this sentence.

    Two consumers already computed this: ``src/indicators.py`` (numpy, the
    engine's scoring path) and ops' ``dark_signals.wilder_atr`` (the exit
    bake-off). This is a third *implementation* and deliberately not a third
    *definition* — the test is what makes that true rather than intended.
    """
    n = len(closes)
    out: List[Optional[float]] = [None] * n
    p = int(period)
    if p < 1 or n < p + 1 or len(highs) != n or len(lows) != n:
        return out
    trs: List[float] = [0.0] * n
    for i in range(1, n):
        prev_close = closes[i - 1]
        trs[i] = max(
            highs[i] - lows[i],
            abs(highs[i] - prev_close),
            abs(lows[i] - prev_close),
        )
    atr = sum(trs[1 : p + 1]) / p
    out[p] = atr
    for i in range(p + 1, n):
        atr = (atr * (p - 1) + trs[i]) / p
        out[i] = atr
    return out


# --------------------------------------------------------------------------- #
# Parameters
# --------------------------------------------------------------------------- #


def default_params(mechanism: str) -> Dict[str, float]:
    """The tunables for one mechanism, read from config at call time.

    Read here rather than passed in from four call sites, so there is one place
    a parameter can come from — and stamped onto the arm at ``new_arm`` so a
    row can always say which parameters produced it. A ledger whose rows were
    computed under two different multipliers, with nothing on the row to say
    which, is a population that cannot be split after the fact.
    """
    from config import (
        ATR_TRAIL_MULT,
        ATR_TRAIL_PERIOD,
        SAR_EXIT_SHADOW_MAX_STEP,
        SAR_EXIT_SHADOW_STEP,
    )

    if mechanism == MECH_CHANDELIER:
        return {"period": float(ATR_TRAIL_PERIOD), "mult": float(ATR_TRAIL_MULT)}
    # One indicator, one set of parameters: the live arm reads the same
    # step/max-step as the replay arm and the app's chart study, because three
    # surfaces drawing different SAR would make them incomparable.
    return {"step": float(SAR_EXIT_SHADOW_STEP), "max_step": float(SAR_EXIT_SHADOW_MAX_STEP)}


def min_bars(mechanism: str, params: Dict[str, float]) -> int:
    """Bars the mechanism needs before it can produce a level at all.

    Separate from the arm engine's warm-up (which is about how much history a
    *measurement* deserves): this is the hard floor below which the mechanism
    returns ``None``, and the engine uses it to refuse rather than to clamp.
    """
    if mechanism == MECH_CHANDELIER:
        return int(params.get("period", 22)) + 2
    return 3


# --------------------------------------------------------------------------- #
# Per-walk context
# --------------------------------------------------------------------------- #


def prepare(
    mechanism: str,
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    params: Dict[str, float],
) -> Any:
    """Whatever the mechanism wants computed **once** per walk, not per bar.

    Wilder ATR is causal — the value at bar *i* is identical whether the series
    was cut at *i* or runs to the end — so the chandelier's ATR is computed once
    for the window and indexed, rather than re-smoothed for every bar of a walk.
    SAR has no such shortcut (its walk carries an acceleration factor forward and
    the projection is off the final state), so it prepares nothing and pays the
    full walk per bar, exactly as it always has.
    """
    if mechanism == MECH_CHANDELIER:
        return wilder_atr(highs, lows, closes, int(params.get("period", 22)))
    return None


def point(
    mechanism: str,
    ctx: Any,
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    upto: int,
    *,
    side: str,
    state: Dict[str, Any],
    params: Dict[str, float],
    last_closed_ms: Optional[float] = None,
) -> Optional[TrailPoint]:
    """The level to park for the bar after ``upto``, or ``None`` if unknowable.

    ``upto`` is the index of the newest **closed** bar. ``state`` is the arm's
    own mutable mechanism state and is written through — the chandelier's
    ratchet lives there, because a ratchet recomputed from the window's start
    would silently re-anchor every time the store re-seeds a bucket, which is
    the frozen-then-refreshed series that cost #846.
    """
    if upto < 0 or upto >= len(highs):
        return None
    if mechanism == MECH_CHANDELIER:
        return _chandelier_point(
            ctx, highs, lows, closes, upto, side=side, state=state, params=params
        )
    return _sar_point(
        highs, lows, upto, side=side, params=params, last_closed_ms=last_closed_ms
    )


def _sar_point(
    highs: Sequence[float],
    lows: Sequence[float],
    upto: int,
    *,
    side: str,
    params: Dict[str, float],
    last_closed_ms: Optional[float],
) -> Optional[TrailPoint]:
    live = parabolic_sar_live(
        highs[: upto + 1],
        lows[: upto + 1],
        float(params.get("step", 0.02)),
        float(params.get("max_step", 0.2)),
        last_closed_ms=last_closed_ms,
    )
    if live is None:
        return None
    onside = bool(live.up) if _is_long(side) else (not bool(live.up))
    return TrailPoint(next_stop=float(live.next_stop), up=bool(live.up), onside=onside)


def _chandelier_point(
    atrs: Any,
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    upto: int,
    *,
    side: str,
    state: Dict[str, Any],
    params: Dict[str, float],
) -> Optional[TrailPoint]:
    """Running extreme since the arm opened, less ``mult`` ATRs, ratcheted.

    The two conservative choices, both of which lean against the mechanism:

    * **The extreme includes the current bar.** A stop derived from a high the
      bar has already printed is the tightest defensible reading, and the
      alternative (lag it one bar) would let the trail sit further from price
      than a live implementation would have parked it.
    * **The ratchet never loosens.** ``max`` for a long, ``min`` for a short,
      against the level already parked — so a widening ATR cannot hand the trade
      back risk it was not sized for. This is the one behaviour SAR does *not*
      share (its two-bar clamp can move the level away from price), and it is
      why ``max_sar_risk_pct`` is tracked per bar rather than assumed.
    """
    if not isinstance(atrs, list) or upto >= len(atrs):
        return None
    a = atrs[upto]
    if a is None or not (a == a) or a <= 0:  # NaN-safe
        return None
    is_long = _is_long(side)
    mult = float(params.get("mult", 3.0))
    prev_extreme = state.get("trail_extreme")
    hi, lo, cl = float(highs[upto]), float(lows[upto]), float(closes[upto])
    if prev_extreme is None:
        extreme = hi if is_long else lo
    else:
        extreme = max(float(prev_extreme), hi) if is_long else min(float(prev_extreme), lo)
    state["trail_extreme"] = extreme
    cand = (extreme - mult * a) if is_long else (extreme + mult * a)
    parked = state.get("trail_parked")
    if parked is None:
        level = cand
    else:
        level = max(float(parked), cand) if is_long else min(float(parked), cand)
    state["trail_parked"] = level
    # "May it govern" for a mechanism with no direction of its own: is the level
    # it would park already on the wrong side of the close. A stop above a
    # long's close is not a trailing stop, it is an instant exit, and handing
    # governance to it would book a fill the mechanism never legitimately took.
    onside = (level < cl) if is_long else (level > cl)
    return TrailPoint(next_stop=float(level), up=None, onside=bool(onside))


# --------------------------------------------------------------------------- #
# Manifest — one writer
# --------------------------------------------------------------------------- #


def manifest(mechanism: str, params: Dict[str, float]) -> Dict[str, Any]:
    """The mechanism as data, written once per ledger file.

    Ops renders the label and the parameters from this rather than keeping its
    own copy — the ``strategy_catalog`` pattern, for the same reason: a rule
    (here, a mechanism) the surface has never heard of must render badged rather
    than renamed, and a hand-kept second catalog is the drift this repo has paid
    for under six names.
    """
    labels = {
        MECH_SAR: "Parabolic SAR",
        MECH_CHANDELIER: "ATR-trail (Chandelier)",
    }
    return {
        "key": str(mechanism),
        "label": labels.get(str(mechanism), str(mechanism)),
        "params": {k: float(v) for k, v in (params or {}).items()},
        # What the mechanism's own direction column means on this lane. A
        # chandelier has none, and a blank with no cause is how a reader decides
        # the engine stopped stamping.
        "has_direction": str(mechanism) == MECH_SAR,
    }
