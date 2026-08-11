"""Live trailing-exit governor — the mechanism placing real orders.

Owner, 2026-08-10: *"can we enable auto trading for this SAR Signals to test
in real only for me not for us not for users"*.

Everything before this module **measured** a trailing exit.  ``sar_live_shadow``
steps an arm forward inside the monitor loop and records where the stop *would*
have been parked; its own copy says, in as many words, *"these arms place no
orders and change no exit"*.  That answers "would this have been profitable"
and — since #832 — "could the level have been computed in time".  It cannot
answer whether the stop is **placeable**: whether Binance accepts it, whether
the amend keeps up with the bars, and what the exit actually fills at.  This
module is that last step, and it is the only one that spends money.

Why it is a governor and not a second measurement lane
------------------------------------------------------
The mechanism is already a solved problem.  ``trail_mechanisms.point()``
returns the level in force for the bar now forming, projected from closed bars
only — knowable *before* the bar trades, which is precisely what a resting stop
needs — and it has been reconciled bit-exact against Binance's own candles over
5,400 bars (``scripts/reconcile_sar_arms.py``, 349/349 recorded fills).  So this
module computes nothing about SAR or the chandelier.  It answers one question
per bar: *given that level, what order should exist right now, and how do I get
there without ever leaving the position unprotected?*

Place-then-cancel, and why the BE-shift's ordering is not reusable
-------------------------------------------------------------------
``pretp_dispatcher.maybe_fire_be_shift`` cancels the old stop and then places
the new one, and its own error path says what that costs: *"the original SL was
already canceled; if the retry also fails the reconciler will catch the naked
position and close it."*  That is a defensible trade **once** per position.  This
governor re-parks on **every closed bar**, so the same ordering would open a
naked window every bar of every governed trade — dozens per position — against
a hard limit that has no exceptions.

It is avoidable, and the reason is a detail of how the stop is placed: two
protective orders may rest at once, so the new one can go up before the old one
comes down.

**The first cut got the mechanism of that right and the vendor wrong, and it
cost the whole feature.**  It placed the governor's stop with
``closePosition=true``, reasoning that such an order carries no quantity, so two
of them cannot double-fill: the nearer level triggers, the position goes to
zero, the other finds nothing to close.  Every word of that is true about
*fills* and silent about *acceptance* — Binance answers a second
``closePosition`` order in the same direction with

    -4130 "An open stop or take profit order with GTE and closePosition in the
           direction is existing."

and by the naked-position invariant a governed position **always** has a stop
resting, so the first step of every handover collided with the protection it
was replacing.  `handovers` sat at 0 with `place_failed` climbing, for every
position, from the day this shipped (owner-caught 2026-08-10, #913/#915).

The fix keeps the ordering and changes the order *shape*: the governor's stop is
``reduceOnly`` with the position's own quantity.  That is what the entire TP
ladder already uses, and those coexist with the ``closePosition`` SL on every
live position — the evidence is the running system, not the documentation.  It
is equally safe on a double trigger, because ``reduceOnly`` cannot open or flip
a position: whichever level triggers first closes it and the exchange rejects
the remainder.

**What that fix got wrong, and it is the same class a third time.**  This
docstring went on to claim Binance *"auto-cancels reduce-only orders once the
position closes"* — borrowed from ``place_trailing_stop``'s docstring, which
describes a native ``TRAILING_STOP_MARKET``, a different order type.  Nobody
asked the exchange about a CONDITIONAL ``STOP_MARKET``.  It does not: on
2026-08-11 PROMUSDT closed at 10:16:51 and its governor stop was still resting
28 minutes later, while ``grep -rn trail_stop_order_id src/`` matched nothing
outside this module and the dataclass.  A vendor claim inherited from a
neighbouring order type is not a measurement — the depth-stream path
(2026-08-05) and the -4130 collision above are the same mistake.  Cancellation
is owned explicitly now: ``_exit_at_market`` retires the stop with the position,
and ``signal_dispatch._PROTECTIVE_ORDER_ATTRS`` covers every other close path,
derived from the dataclass rather than typed out.

So the order of operations is:

1. compute the level for the bar now forming;
2. **place** the new stop (new sequence in the coid — Binance rejects a
   duplicate id);
3. only on success, **cancel** the one it replaces.

A failure at (2) leaves the previous stop exactly where it was and the governor
retries next bar.  A failure at (3) leaves two live stops and is counted as
``orphan_cancel``, retried next bar.  Neither branch is ever naked, and that is
a property of the ordering rather than of the retry working.

The exit leg, and why a trail alone could never be the mechanism
-----------------------------------------------------------------
Both mechanisms exit on something a resting stop cannot express.  SAR
*reverses*: when it flips, its level jumps to the far side of price, which is
an instruction to be out — not a stop to park, and Binance answers -2021
"Order would immediately trigger" if you try.  Until 2026-08-11 this module had
no verb for it, because ``decide`` asked ``point.onside`` at the handover and
never again; the flipped level was waved through ``tightens`` (trivially
"tighter" for a LONG), rejected, and then the retry gate declined to re-ask.
The position sat on the last pre-flip stop while the measured arm had already
booked the trade closed.

``_exit_at_market`` is that leg, and it is what makes the two fills the arm
records reachable live: the resting stop is ``fill @level``, the offside close
is ``fill @confirm``.  Whichever happens first is what the account gets, which
is exactly the bracket the measurement publishes.

What it refuses to do
---------------------
* **Govern a position whose ladder has already been touched.**  The measured
  mechanism runs from entry with the evaluator's SL and TP1 cancelled at
  handover.  A position that has already fired pre-TP, filled TP1 or shifted to
  BE is a different trade, and adopting it mid-flight would measure neither the
  mechanism nor the FSM.  Counted as ``ladder_touched``, never silently skipped.
* **Park a level off a stale bar.**  #836's rule — a freshness check at one end
  of an object's life is not a check of the object — arrives here with money
  behind it: a promoted mover on REST re-seed can hand back a bar hours old, and
  a stop parked off it is a stop nobody computed for this market.  The governor
  refuses (``stale_series``) and leaves the existing protection alone.
* **Widen after handover.**  A trail only tightens.  Both mechanisms move the
  stop toward price by construction (a SAR flip is an *exit* here, not a
  reversal, so it never resets to the far side), and enforcing it anyway means
  risk after handover is monotonically non-increasing whatever the mechanism
  does.  The handover itself may widen — the owner chose the uncapped mechanism
  on 2026-08-10, knowing SAR's stop was wider than the designed SL on 54% of
  measured handovers — and that one step is the only place widening is allowed.
* **Answer at all when the position index is cold.**  ``index_open_positions``
  returns None rather than falling back to a collection-group query, because
  this sweep runs on the monitor clock and that query on that clock is the
  Session-24 billing incident.  A cold index is counted and paged, never read
  as an empty book.

Scoping
-------
Per **user**, from ``user_auto_trade_settings.exit_mechanism``, stamped onto the
position at placement so no bar re-reads SQLite and no mid-flight settings
change re-governs a running trade.  B17's pre-TP and invalidation settings
already establish exit behaviour as a per-user column; a global flag could not
express "my account only", which is the whole request.
"""
from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional, Tuple

from src import fail_open, sar_live_shadow, trail_mechanisms
from src.execution import order_placer as _order_placer
from src.execution import position_state as _position_state
from src.execution import symbol_filters as _sf
from src.utils import get_logger

log = get_logger(__name__)

#: Mechanisms a user may select.  Mirrors ``trail_mechanisms.MECHANISMS`` and
#: is asserted equal to it in the tests — one writer, one reader.
GOVERNABLE = frozenset(trail_mechanisms.MECHANISMS)

#: A position is only adopted while its ladder is untouched (see the module
#: docstring).  Each reason is counted separately because the next move
#: differs: ``ladder_touched`` is expected and benign, ``stale_series`` is a
#: data fault, ``no_series`` is a feed fault.
REFUSE_LADDER = "ladder_touched"
REFUSE_STALE = "stale_series"
REFUSE_NO_SERIES = "no_series"
REFUSE_NOT_ONSIDE = "not_onside"
REFUSE_NO_LEVEL = "no_level"
REFUSE_INDEX_COLD = "index_cold"
REFUSE_KILL_SWITCH = "kill_switch"
REFUSE_DISABLED = "disabled"
#: The configured governing timeframe is not one the candle store carries.
#: Named apart from ``no_series`` deliberately: that one means "this symbol has
#: no window", which sends a reader to the feed. This means "the setting is not
#: a timeframe", which is one character in ops — and on 2026-08-10 the two were
#: indistinguishable while the governor sat permanently inert reporting a feed
#: fault that was not happening.
REFUSE_BAD_TF = "bad_timeframe"
#: Nothing left to protect — the position's remaining size is zero or unreadable.
#: Named apart from every placement failure because no order was attempted and
#: the exchange was never asked: this is our own book saying there is nothing to
#: park a stop over.
REFUSE_NO_QUANTITY = "no_quantity"

#: How far behind the clock the newest closed bar may sit before the governor
#: refuses to park a level off it, in multiples of the bar width.  Two bars of
#: slack absorbs an ordinary late close; beyond that the series is not
#: describing this market.  Deliberately the same slack the measurement lane
#: uses (``sar_live_shadow._ADVANCE_SLACK_BARS``) so the live arm and the arm it
#: is validated against do not disagree about what "current" means.
STALE_SLACK_BARS = sar_live_shadow._ADVANCE_SLACK_BARS

#: Trigger series for the governor's own stop.  **Not** the ``MARK_PRICE``
#: default every other protective order in this engine uses, and the difference
#: is the whole point: ``sar_live_shadow.step_arm`` decides a touch with
#: ``lo <= parked`` on kline lows, so an order resting on the mark fires on a
#: series the measurement never looks at.  Measured 2026-08-11 — the INXUSDT 5m
#: arm booked a closed fill at 0.008689 while the live order at that exact
#: level was still resting.  A canary whose executor and whose measurement
#: disagree about what "touched" means cannot answer the question it exists for.
GOVERNOR_WORKING_TYPE = "CONTRACT_PRICE"

#: Post-handover, the mechanism has come offside — SAR flipped, or the
#: chandelier's level is already past the close.  This is the mechanism's own
#: **exit**, and until 2026-08-11 the governor had no verb for it: ``decide``
#: checked ``onside`` only *before* handover, so a flipped level (which sits on
#: the far side of price by construction) was waved through ``tightens`` and
#: sent as a stop, where Binance answered -2021 "Order would immediately
#: trigger" and the deferral gate then declined to re-ask.  The measured arm
#: closes here; the live position sat on the last pre-flip stop with the
#: governor inert.  See ``_exit_at_market``.
DECIDE_EXIT = "exit"


def _now() -> float:
    import time

    return time.time()


# --------------------------------------------------------------------------- #
# Health — keyed on the population owed a decision (#815), not on what is easy
# --------------------------------------------------------------------------- #

_health_lock = threading.Lock()


#: How many placement rejections to keep, newest last.  Bounded because this
#: rides in a snapshot written every ~15s; the count beside it is unbounded, so
#: the ring never becomes the denominator (the Suppression Quality Audit's
#: lesson — when a bounded buffer feeds a display, publish the total too).
PLACE_FAILURE_RING = 8

#: How many realized governed exits to keep, newest last.  Same bounded-ring
#: rule as above: ``exits`` and ``stops_filled`` are the unbounded totals and
#: ride beside it, so a reader can never mistake the sample for the population.
OUTCOME_RING = 40


def _blank_health() -> Dict[str, Any]:
    return {
        "governed": 0,
        "handovers": 0,
        "replaced": 0,
        "unchanged": 0,
        "place_failed": 0,
        "retry_deferred": 0,
        "orphan_cancel": 0,
        #: The mechanism's own exit fired and the position was market-closed
        #: (``exits``), or the close itself was refused (``exit_failed``).
        #: Counted apart from ``replaced`` because they are opposite events: one
        #: moves protection, the other ends the trade, and pooling them would
        #: make a governor that never exits look identical to one that does.
        "exits": 0,
        "exit_failed": 0,
        #: Realized outcomes of governed exits, newest last — the answer to
        #: "did the canary make money", which no surface in either repo could
        #: give before 2026-08-11.  `handovers`/`replaced` say the machine is
        #: turning; they cannot say what it earned.  Bounded, with
        #: ``exits``/``stops_filled`` beside it as the unbounded totals.
        "outcomes": [],
        "stops_filled": 0,
        "refusals": {},
        #: The last few rejections, with the exchange's own words.  A bare
        #: counter here is "blank needs a cause before it gets a caption" on
        #: the one path that spends money: -2021 (the level is already through
        #: the mark), -1111 (rounding), -4015 (duplicate id) and a dead key
        #: all read as the identical integer, and they have four different
        #: fixes.  Not a log line, because the log needs `docker exec` and the
        #: owner reads the panel (2026-08-10, #911).
        "place_failures": [],
        "cycles": 0,
    }


_health: Dict[str, Any] = _blank_health()


def _count(bucket: str, n: int = 1) -> None:
    with _health_lock:
        _health[bucket] = int(_health.get(bucket, 0)) + n


def _refuse(reason: str) -> None:
    with _health_lock:
        refusals = _health.setdefault("refusals", {})
        refusals[reason] = int(refusals.get(reason, 0)) + 1


def _binance_code(exc: Exception) -> Optional[int]:
    """The exchange's own error code, when it gave one.

    ``None`` means *the rejection did not come from Binance* (signing service
    down, key not connected, a bug on our side) — a different next move, so it
    is never rendered as a zero.
    """
    resp = getattr(exc, "signing_response", None)
    body = getattr(resp, "binance_body", None)
    if isinstance(body, dict):
        code = body.get("code")
        if isinstance(code, (int, float)):
            return int(code)
    return None


def _record_place_failure(
    *,
    symbol: str,
    side: str,
    signal_id: str,
    seq: int,
    level: float,
    exc: Exception,
    ts: float,
) -> None:
    """Keep the last few rejections so the panel can say *why*.

    ``str(exc)`` is already self-contained — ``_raise_for`` formats
    ``code=… status=… message=…`` — and carries no key material: the signing
    service never returns a secret and the message is the exchange's own
    response text.  It is truncated anyway, because an unbounded string in a
    snapshot written every 15s is a cost decision, not a display one.
    """
    entry = {
        "ts": ts,
        "symbol": symbol,
        "side": side,
        "signal_id": signal_id,
        "seq": seq,
        "level": float(level),
        "kind": type(exc).__name__,
        "binance_code": _binance_code(exc),
        "error": str(exc)[:300],
    }
    with _health_lock:
        ring = _health.setdefault("place_failures", [])
        ring.append(entry)
        del ring[:-PLACE_FAILURE_RING]


def record_outcome(
    position: Any,
    *,
    exit_price: float,
    exit_kind: str,
    ts: Optional[float] = None,
) -> None:
    """Book a governed position's realized exit, so the canary can be read.

    **This is the gap #908 and #160 left.**  Both shipped counters —
    ``handovers``, ``replaced``, ``place_failed`` — which say the machine is
    turning and are silent on what it earned.  ``/signals/sar-live`` is the
    shadow, and ``/track-record`` reads the *signal* record, so the realized
    result of a governed exit landed on no surface in either repo: the one
    number the owner's own-capital test exists to produce could not be read
    anywhere.  "Dark work must be observable" applied to the money leg.

    ``exit_kind`` separates the mechanism's two fills, which the measured arm
    has always kept apart and which must not be pooled here either:

    ``trail_stop``
        The parked level was touched — the arm's ``fill @level``.
    ``flip_close``
        The mechanism came offside and the position was closed at market —
        the arm's ``fill @confirm``.  Their difference is the cost of
        confirmation, and blending them picks the flattering one.

    ``pnl_pct`` is gross and signed toward the trade, matching the arm's
    ``pnl_level_pct`` exactly so the two are comparable without a conversion
    nobody would remember to apply.
    """
    entry_price = float(
        getattr(position, "entry_price_filled", 0.0)
        or getattr(position, "entry_price_target", 0.0)
        or 0.0
    )
    pnl_pct: Optional[float] = None
    if entry_price > 0 and exit_price > 0:
        raw = (exit_price - entry_price) / entry_price * 100.0
        pnl_pct = raw if str(position.side).upper() == "LONG" else -raw
    entry = {
        "ts": _now() if ts is None else float(ts),
        "signal_id": getattr(position, "signal_id", ""),
        "symbol": getattr(position, "symbol", ""),
        "side": getattr(position, "side", ""),
        "mechanism": str(getattr(position, "exit_mechanism", "") or "").lower(),
        "exit_kind": exit_kind,
        "entry": entry_price,
        "exit": float(exit_price),
        # None rather than 0.0 when the entry price is unreadable: a zero here
        # would average into the book as a flat trade, which is a claim.
        "pnl_pct": pnl_pct,
        "designed_sl": float(getattr(position, "sl_price", 0.0) or 0.0),
        "parked_stop": float(getattr(position, "trail_stop_price", 0.0) or 0.0),
        "seq": int(getattr(position, "trail_stop_seq", 0) or 0),
    }
    with _health_lock:
        if exit_kind == "trail_stop":
            _health["stops_filled"] = int(_health.get("stops_filled", 0)) + 1
        ring = _health.setdefault("outcomes", [])
        ring.append(entry)
        del ring[:-OUTCOME_RING]


def health() -> Dict[str, Any]:
    """A snapshot for the liveness probe and the ops panel.

    Includes the refusal mix, because a governor that governs nothing looks
    identical to a quiet book unless it can say *why* — the lesson the
    price-action lane card paid for one repo over.
    """
    with _health_lock:
        out = dict(_health)
        out["refusals"] = dict(out.get("refusals", {}))
        out["place_failures"] = [dict(e) for e in out.get("place_failures", [])]
        out["outcomes"] = [dict(e) for e in out.get("outcomes", [])]
        return out


def reset_health_for_test() -> None:
    global _health
    with _health_lock:
        _health = _blank_health()


# --------------------------------------------------------------------------- #
# Mechanism state — per position, never shared
# --------------------------------------------------------------------------- #

#: ``(firebase_uid, signal_id) -> mechanism state dict``.  In memory only, and
#: deliberately per position: the chandelier's ratchet is anchored to the arm's
#: own first bar, so sharing a cache entry between two positions on the same
#: symbol and bar would hand the second one the first's history — #846 arriving
#: through a cache instead of through a store, and just as silent.
#:
#: Lost on restart by design.  It is rebuilt by re-walking from the position's
#: own entry, and the *parked* stop is persisted on the position, so the
#: ratchet guard still holds across a deploy even before the walk catches up.
_mech_state: Dict[Tuple[str, str], Dict[str, Any]] = {}
_mech_state_lock = threading.Lock()


def _state_for(uid: str, signal_id: str) -> Dict[str, Any]:
    key = (uid, signal_id)
    with _mech_state_lock:
        return _mech_state.setdefault(key, {})


#: ``(firebase_uid, signal_id) -> the bar whose level the exchange refused``.
#:
#: The retry cadence is a property of ``trail_last_bar_ms``, which is advanced
#: only on a SUCCESSFUL park — so before this existed a rejected level was
#: re-submitted on **every sweep**, not on every bar.  The sweep rides the
#: monitor clock, so "retrying next bar" in the docstring above was in fact ~12
#: attempts a minute per position, indefinitely, against an exchange this box
#: has already been IP-banned by once.  Measured on the owner's account
#: 2026-08-10: two positions, +24 rejected placements per minute, forever.
#:
#: Deferring costs nothing: a rejection leaves the previous protection resting
#: untouched, so the position is covered for the whole wait, and the level is
#: fixed for the bar — re-asking the same question of the same bar cannot get a
#: different answer.  In memory, so a restart re-tries immediately, which is the
#: right direction for a transient fault.
_failed_bar: Dict[Tuple[str, str], float] = {}


def _mark_failed_bar(uid: str, signal_id: str, bar_ms: float) -> None:
    with _mech_state_lock:
        _failed_bar[(uid, signal_id)] = float(bar_ms)


def _bar_already_refused(uid: str, signal_id: str, bar_ms: float) -> bool:
    with _mech_state_lock:
        return _failed_bar.get((uid, signal_id)) == float(bar_ms)


def forget(uid: str, signal_id: str) -> None:
    """Drop a closed position's mechanism state."""
    with _mech_state_lock:
        _mech_state.pop((uid, signal_id), None)
        _failed_bar.pop((uid, signal_id), None)


def reset_state_for_test() -> None:
    with _mech_state_lock:
        _mech_state.clear()
        _failed_bar.clear()


# --------------------------------------------------------------------------- #
# Pure decision half — no I/O, so it is testable without Binance
# --------------------------------------------------------------------------- #


def ladder_untouched(position: Any) -> bool:
    """True when the evaluator's exit is still fully intact.

    The measured mechanism governs from entry.  Anything that has already
    modified the exit — pre-TP fired, BE shifted, a TP leg filled, or a stop
    that is simply no longer there — makes this a different trade from the one
    the ledger scored, so the governor declines rather than adopting it.
    """
    if getattr(position, "pretp_fired", False):
        return False
    if getattr(position, "be_shift_fired", False):
        return False
    if float(getattr(position, "closed_qty", 0.0) or 0.0) > 0.0:
        return False
    if int(getattr(position, "sl_be_order_id", 0) or 0) != 0:
        return False
    if int(getattr(position, "trail_order_id", 0) or 0) != 0:
        # The regime-per-exit TRAIL path (Binance TRAILING_STOP_MARKET) already
        # owns this exit.  Two trailing mechanisms on one position is not a
        # measurement, it is a race.
        return False
    return True


def tightens(side: str, old_stop: float, new_stop: float) -> bool:
    """Does ``new_stop`` move protection toward price for this side?

    Equal is not tighter — an unchanged level must not spend an order.
    """
    if old_stop <= 0:
        return True
    if str(side or "").upper() == "LONG":
        return new_stop > old_stop
    return new_stop < old_stop


def _bar_is_current(
    last_bar_ms: float, timeframe: str, now_ts: float
) -> bool:
    """Is the newest closed bar recent enough to park a live stop against?"""
    width = sar_live_shadow.timeframe_seconds(timeframe)
    if width is None or width <= 0:
        return False
    age_bars = ((now_ts * 1000.0) - float(last_bar_ms)) / (width * 1000.0)
    # One full bar has always elapsed for a *closed* bar, hence the +1.
    return age_bars <= (STALE_SLACK_BARS + 1.0)


def decide(
    position: Any,
    series: Dict[str, List[float]],
    *,
    mechanism: str,
    params: Dict[str, float],
    state: Dict[str, Any],
    timeframe: str,
    now_ts: float,
) -> Tuple[Optional[float], str]:
    """The whole decision, with no I/O: ``(level_to_park, reason)``.

    ``level_to_park`` is None when nothing should be done, and ``reason`` says
    which of the several quite different "nothings" it is — with one exception
    that is not a nothing: ``DECIDE_EXIT`` also carries no level, because the
    action is a market close rather than a stop.  Separated from the placement
    half so every branch here is testable without an exchange.
    """
    times = series["open_time"]
    highs = series["high"]
    lows = series["low"]
    closes = series["close"]
    upto = len(closes) - 1
    if upto < 0:
        return None, REFUSE_NO_SERIES

    last_bar_ms = times[upto]
    if not _bar_is_current(last_bar_ms, timeframe, now_ts):
        return None, REFUSE_STALE

    # Idempotent across sweeps: the governor acts once per closed bar, and the
    # monitor loop runs several times per bar on every timeframe we trade.
    if float(getattr(position, "trail_last_bar_ms", 0.0) or 0.0) >= last_bar_ms:
        return None, "same_bar"

    ctx = trail_mechanisms.prepare(mechanism, highs, lows, closes, params)
    point = trail_mechanisms.point(
        mechanism,
        ctx,
        highs,
        lows,
        closes,
        upto,
        side=position.side,
        state=state,
        params=params,
        last_closed_ms=last_bar_ms,
    )
    if point is None or not (point.next_stop == point.next_stop):  # NaN-safe
        return None, REFUSE_NO_LEVEL

    governing = bool(getattr(position, "trail_governing", False))
    if not governing:
        # Handover only once the mechanism is onside.  Until then the
        # evaluator's SL and TP1 govern, exactly as the measurement lane models
        # it — and this is the one step allowed to widen risk.
        if not point.onside:
            return None, REFUSE_NOT_ONSIDE
        return float(point.next_stop), "handover"

    # Governing, and the mechanism has come offside: this is its EXIT, not a
    # level to park.  Checked BEFORE `tightens`, which is what let the bug
    # through — a flipped SAR sits on the far side of price by construction, so
    # it is trivially "tighter" than the old stop for a LONG and was sent as a
    # stop the exchange can only reject (-2021).  `onside` was asked at the
    # handover and never again: a mechanism decision applied at one end of a
    # position's life is not applied to the position (#836's rule, arriving on
    # the leg that spends money).
    if not point.onside:
        return None, DECIDE_EXIT

    parked = float(getattr(position, "trail_stop_price", 0.0) or 0.0)
    if not tightens(position.side, parked, float(point.next_stop)):
        # Includes the equal case: re-placing an identical level would spend
        # two API calls to change nothing.
        return None, "unchanged"
    return float(point.next_stop), "replace"


# --------------------------------------------------------------------------- #
# Placement half
# --------------------------------------------------------------------------- #


async def _exit_at_market(position: Any, *, placer: Any) -> bool:
    """The mechanism's own exit: close at market, then retire the resting stop.

    Returns True when the position is closed.  This is the leg the measured arm
    has always modelled as ``fill @confirm`` — "wait for the bar to close and
    exit at market" — and which had no implementation at all until 2026-08-11.
    Without it the mechanism's *definition* ("the trade exits when SAR flips")
    was unreachable: the governor's only verb was moving a resting stop, so a
    flip produced an un-placeable level and then silence.

    **Close first, cancel second — the opposite of ``_park``, and for the same
    reason.**  ``_park`` places before cancelling so the position is never
    naked while protection is *replaced*.  Here protection is being *retired*
    along with the position, and the market close is ``reduceOnly``, so it can
    neither open nor flip anything: closing first means the trade is out at the
    price the decision was made on, and the stop that outlives it by a few
    hundred milliseconds is over-protection on a flat book.  Cancelling first
    would open a naked window for exactly as long as the close takes.

    A failed cancel here is the orphan that PROMUSDT demonstrated on
    2026-08-11 — a reduce-only stop resting on a closed position, which Binance
    does **not** clean up for this order type — so it is counted rather than
    logged, and the FSM's own close path cancels it again from
    ``_PROTECTIVE_ORDER_ATTRS``.  Two writers on that cancel is deliberate:
    this one is timely, that one is total.
    """
    qty = remaining_qty(position)
    if qty <= 0:
        _refuse(REFUSE_NO_QUANTITY)
        return False
    fill = 0.0
    try:
        result = await placer.place_market_close(
            signal_id=position.signal_id,
            symbol=position.symbol,
            direction=position.side,
            quantity=qty,
        )
        fill = float(getattr(result, "avg_price", 0.0) or 0.0)
    except _order_placer.OrderPlacementError as exc:
        if _binance_code(exc) != -2022:
            # Any other refusal — including one that never reached Binance —
            # leaves the position exactly as it was: the parked stop is still
            # resting, so it is protected, and the exit is retried next bar.
            # Handled in this one handler rather than re-raised into a sibling
            # `except`, which Python does not re-enter: the first cut did that
            # and a -1001 escaped the function entirely.
            _count("exit_failed")
            _record_place_failure(
                symbol=position.symbol,
                side=position.side,
                signal_id=position.signal_id,
                seq=int(getattr(position, "trail_stop_seq", 0) or 0),
                level=float(getattr(position, "trail_stop_price", 0.0) or 0.0),
                exc=exc,
                ts=_now(),
            )
            log.warning(
                "trail_governor: mechanism exit FAILED uid={} signal_id={} {} "
                "exc={} — the parked stop is still resting, so the position "
                "keeps its protection and the exit is retried next bar",
                position.firebase_uid, position.signal_id, position.symbol, exc,
            )
            return False
        # -2022 ReduceOnly rejected: the book is already flat — the parked
        # stop filled between the decision and this call.  The exit happened;
        # only the leg that reports it lost the race.  Treated as success so
        # the position goes terminal, exactly as `close_fsm_positions_for_signal`
        # does, and stamped `trail_stop` because that is what actually filled:
        # booking it as a flip_close would credit the market leg with a fill
        # the resting stop took.
        log.info(
            "trail_governor: mechanism exit found the book already flat "
            "uid={} signal_id={} {} — the parked stop filled first",
            position.firebase_uid, position.signal_id, position.symbol,
        )
        record_outcome(
            position,
            exit_price=float(getattr(position, "trail_stop_price", 0.0) or 0.0),
            exit_kind="trail_stop",
        )
        _finish_exit(position)
        _count("exits")
        return True

    # `avg_price` is 0 on a MARKET order Binance has accepted but not yet
    # reported a fill for.  Recorded as-is: `record_outcome` writes `pnl_pct
    # = None` for a non-positive price rather than inventing one, and the FSM's
    # own close-fill event carries the real average.  A fabricated fill is the
    # one thing an outcome ledger must never contain.
    record_outcome(position, exit_price=fill, exit_kind="flip_close")

    oid = int(getattr(position, "trail_stop_order_id", 0) or 0)
    if oid:
        try:
            await placer.cancel_algo_order(symbol=position.symbol, algo_id=oid)
            position.trail_stop_order_id = 0
        except _order_placer.OrderPlacementError as exc:
            _count("orphan_cancel")
            log.warning(
                "trail_governor: cancel of the parked stop after a mechanism "
                "exit FAILED uid={} signal_id={} algo_id={} exc={} — a "
                "reduce-only stop is resting on a flat position and Binance "
                "will not retire it; the FSM close path cancels it again",
                position.firebase_uid, position.signal_id, oid, exc,
            )
    _finish_exit(position)
    return True


def _finish_exit(position: Any) -> None:
    """Retire a governed position after its mechanism exit.

    Marked terminal **here** rather than waiting for the FSM's close-fill
    event, mirroring ``close_fsm_positions_for_signal``.  The sweep re-reads
    the open index every cycle, so a position left non-terminal because a WS
    frame was dropped would be exited again on the next bar — and a second
    market close on a flat book is exactly the -2022 path above, forever.  The
    FSM's handler already guards a late event on a terminal position.
    """
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    position.trail_governing = False
    position.trail_stop_price = 0.0
    position.state = _position_state.PositionState.CLOSED
    if not getattr(position, "close_reason", ""):
        position.close_reason = "TRAIL_EXIT"
    position.closed_at = now
    position.last_event_at = now
    try:
        _position_state.put_position(position)
    except Exception as exc:
        # The exchange position is already flat; losing the write means the
        # next sweep re-derives from a stale doc and tries once more, which
        # -2022 absorbs.  Wasteful, not dangerous.
        fail_open.record("trail_governor.finish_exit", exc)
    try:
        from src.execution import pretp_dispatcher as _pd

        _pd.spawn_untrack(position.symbol)
    except Exception as exc:
        fail_open.record("trail_governor.finish_exit:untrack", exc)


async def _park(
    position: Any,
    level: float,
    *,
    placer: Any,
    handover: bool,
) -> bool:
    """Place the new stop, then retire what it replaces.  Never naked.

    Returns True when the new stop is live.  On a placement failure the old
    protection is untouched and still resting — nothing has been given up, so
    the caller simply tries again on the next bar.
    """
    seq = int(getattr(position, "trail_stop_seq", 0) or 0) + 1
    rounded = _sf.round_price(position.symbol, level)
    qty = remaining_qty(position)
    if qty <= 0:
        # Nothing left to protect. Refused rather than sent as a zero — a stop
        # for no quantity would be accepted and protect nothing, which is the
        # one failure this module exists to make impossible.
        _refuse(REFUSE_NO_QUANTITY)
        log.warning(
            "trail_governor: no remaining quantity uid={} signal_id={} "
            "total={} closed={} — not parking",
            position.firebase_uid, position.signal_id,
            getattr(position, "total_qty", None),
            getattr(position, "closed_qty", None),
        )
        return False
    try:
        placed = await placer.place_stop_loss(
            signal_id=position.signal_id,
            symbol=position.symbol,
            direction=position.side,
            stop_price=rounded,
            coid_override=_position_state.coid_trail(position.signal_id, seq),
            # reduceOnly + size, NOT closePosition — see the module docstring
            # and #915: Binance refuses a second closePosition stop in the same
            # direction, which made the handover impossible.
            quantity=qty,
            # ...and on the candle series the measurement lane scores against,
            # not the mark. See GOVERNOR_WORKING_TYPE.
            working_type=GOVERNOR_WORKING_TYPE,
        )
    except _order_placer.OrderPlacementError as exc:
        _count("place_failed")
        _record_place_failure(
            symbol=position.symbol,
            side=position.side,
            signal_id=position.signal_id,
            seq=seq,
            level=float(rounded),
            exc=exc,
            ts=_now(),
        )
        log.warning(
            "trail_governor: park FAILED uid={} signal_id={} seq={} level={} "
            "exc={} — previous protection left in place, retrying next bar",
            position.firebase_uid, position.signal_id, seq, rounded, exc,
        )
        return False

    superseded: List[Tuple[str, int]] = []
    if handover:
        # The mechanism now owns the exit: the evaluator's stop and its whole
        # TP ladder come down.  This is what the measured arm models — "the
        # original SL and TP1 are never used; the trade exits when the
        # mechanism does".
        for attr in ("sl_order_id", "tp1_order_id", "tp2_order_id", "tp3_order_id"):
            oid = int(getattr(position, attr, 0) or 0)
            if oid:
                superseded.append((attr, oid))
    else:
        oid = int(getattr(position, "trail_stop_order_id", 0) or 0)
        if oid:
            superseded.append(("trail_stop_order_id", oid))

    # New stop is live from here — the position is over-protected until each
    # cancel lands, which is the safe direction.
    position.trail_stop_order_id = placed.order_id
    position.trail_stop_price = float(rounded)
    position.trail_stop_seq = seq
    position.trail_governing = True

    for attr, oid in superseded:
        try:
            await placer.cancel_algo_order(symbol=position.symbol, algo_id=oid)
            if attr != "trail_stop_order_id":
                setattr(position, attr, 0)
        except _order_placer.OrderPlacementError as exc:
            _count("orphan_cancel")
            log.warning(
                "trail_governor: cancel of superseded {}={} FAILED uid={} "
                "signal_id={} exc={} — two stops resting; the new one is "
                "reduceOnly for the position's size, so whichever level "
                "triggers first closes the position and the exchange rejects "
                "the remainder rather than opening or flipping anything. "
                "Retrying the cancel next bar",
                attr, oid, position.firebase_uid, position.signal_id, exc,
            )
    return True


def remaining_qty(position: Any) -> float:
    """How much of the position a stop must still cover.

    The governor only adopts an untouched ladder, so at handover this is the
    whole entry size — but it is re-derived on **every** re-park rather than
    cached, because a stop sized from a stale number is the one way a
    ``reduceOnly`` order can under-protect: too large is harmless (the exchange
    caps a reduce-only fill at the position), too small silently leaves a
    residual naked.  Mirrors ``position_fsm``'s own arithmetic.
    """
    total = float(getattr(position, "total_qty", 0.0) or 0.0)
    closed = float(getattr(position, "closed_qty", 0.0) or 0.0)
    return max(0.0, total - closed)


def _params_for(mechanism: str) -> Dict[str, float]:
    return trail_mechanisms.default_params(mechanism)


async def step_position(
    position: Any,
    store: Any,
    *,
    timeframe: str,
    placer_factory: Any,
    now_ts: Optional[float] = None,
) -> str:
    """Advance one governed position by at most one bar.  Returns the outcome.

    Every return value is a counted, named state — there is no silent path, and
    "nothing happened" is several different facts with different fixes.
    """
    now_ts = _now() if now_ts is None else now_ts
    mechanism = str(getattr(position, "exit_mechanism", "") or "").lower()
    if mechanism not in GOVERNABLE:
        return "not_governed"

    if not ladder_untouched(position):
        _refuse(REFUSE_LADDER)
        return REFUSE_LADDER

    if sar_live_shadow.timeframe_seconds(timeframe) is None:
        # Refuse before touching the store. Asking it for a bucket keyed on a
        # string no writer ever uses returns None, which is indistinguishable
        # from a symbol with no candles.
        _refuse(REFUSE_BAD_TF)
        return REFUSE_BAD_TF

    params = _params_for(mechanism)
    warmup = trail_mechanisms.min_bars(mechanism, params)
    series, reason = sar_live_shadow._series_with_reason(
        store, position.symbol, timeframe, warmup
    )
    if series is None:
        _refuse(REFUSE_NO_SERIES)
        return REFUSE_NO_SERIES

    state = _state_for(position.firebase_uid, position.signal_id)
    level, decision = decide(
        position,
        series,
        mechanism=mechanism,
        params=params,
        state=state,
        timeframe=timeframe,
        now_ts=now_ts,
    )
    if decision == DECIDE_EXIT:
        # The mechanism's exit, and the one branch here that carries no level.
        # Deliberately NOT gated on `_bar_already_refused`: that gate exists
        # because re-asking the exchange for the same *level* on the same bar
        # cannot get a different answer, which is true of a stop and false of
        # a market close — a close that failed on a transient is worth
        # retrying, and leaving the position in a mechanism that has said exit
        # is the state this whole change exists to remove.
        placer = placer_factory(position.firebase_uid)
        if await _exit_at_market(position, placer=placer):
            _count("exits")
            log.info(
                "trail_governor: mechanism exit uid={} signal_id={} {} {} "
                "tf={} — offside, closed at market",
                position.firebase_uid, position.signal_id,
                position.symbol, position.side, timeframe,
            )
            return DECIDE_EXIT
        return "exit_failed"

    if level is None:
        if decision in (REFUSE_STALE, REFUSE_NO_SERIES, REFUSE_NO_LEVEL, REFUSE_NOT_ONSIDE):
            _refuse(decision)
        elif decision == "unchanged":
            _count("unchanged")
        return decision

    bar_ms = float(series["open_time"][-1])
    if _bar_already_refused(position.firebase_uid, position.signal_id, bar_ms):
        # The exchange has already refused this bar's level. Re-submitting it
        # every sweep cannot change the answer and spends API weight to be told
        # so; the existing protection is resting throughout. Counted, never
        # silent — a deferral and a success must not look alike.
        _count("retry_deferred")
        return "retry_deferred"

    placer = placer_factory(position.firebase_uid)
    ok = await _park(
        position, level, placer=placer, handover=(decision == "handover")
    )
    if not ok:
        _mark_failed_bar(position.firebase_uid, position.signal_id, bar_ms)
        return "place_failed"

    position.trail_last_bar_ms = series["open_time"][-1]
    _count("handovers" if decision == "handover" else "replaced")
    try:
        _position_state.put_position(position)
    except Exception as exc:
        # The order is already live; losing the write means the next sweep
        # re-derives from a stale doc and may re-place. That is wasteful, not
        # dangerous — two closePosition stops cannot double-close.
        fail_open.record("trail_governor.put_position", exc)
    log.info(
        "trail_governor: {} uid={} signal_id={} {} {} seq={} stop={} tf={}",
        decision, position.firebase_uid, position.signal_id,
        position.symbol, position.side, position.trail_stop_seq,
        position.trail_stop_price, timeframe,
    )
    return decision


async def sweep(
    store: Any,
    *,
    placer_factory: Any = None,
    now_ts: Optional[float] = None,
) -> Dict[str, Any]:
    """Advance every governed position by at most one bar.

    Keyed on the population **owed a decision** — open positions carrying a
    mechanism — rather than on whatever list is convenient (#815).  Returns the
    cycle's outcome mix so the caller can log it and the probe can read it.
    """
    from config import TRAIL_GOVERNOR_ENABLED as _CFG_ENABLED
    from config import TRAIL_GOVERNOR_TIMEFRAME as _CFG_TF

    enabled = _CFG_ENABLED
    timeframe = _CFG_TF
    try:
        from src import runtime_tunables as _rt

        enabled = bool(_rt.get("trail_governor_enabled"))
        timeframe = str(_rt.get("trail_governor_timeframe"))
    except Exception as exc:  # pragma: no cover — tunables optional in tests
        fail_open.record("trail_governor.sweep:tunables", exc)

    _count("cycles")
    outcomes: Dict[str, int] = {}
    if not enabled:
        _refuse(REFUSE_DISABLED)
        return {"enabled": False, "outcomes": outcomes, "timeframe": timeframe}

    try:
        from src.execution import kill_switch as _ks

        if _ks.is_initialised() and _ks.get_client().is_global_engaged():
            # The kill switch means "stop acting on this account".  Re-parking
            # a stop is acting.  The existing stop stays exactly where it is —
            # withdrawing protection would be the opposite of what it is for.
            _refuse(REFUSE_KILL_SWITCH)
            return {"enabled": True, "killed": True, "outcomes": outcomes}
    except Exception as exc:
        fail_open.record("trail_governor.sweep:kill_switch", exc)

    positions = _position_state.index_open_positions()
    if positions is None:
        # Cannot answer.  Deliberately not a Firestore fallback — see the
        # module docstring.
        _refuse(REFUSE_INDEX_COLD)
        return {"enabled": True, "index_cold": True, "outcomes": outcomes}

    governed = [
        p
        for p in positions
        if str(getattr(p, "exit_mechanism", "") or "").lower() in GOVERNABLE
        and str(getattr(p, "protection_mode", "managed")) == "managed"
    ]
    with _health_lock:
        _health["governed"] = len(governed)

    factory = placer_factory or _default_placer_factory
    for position in governed:
        try:
            outcome = await step_position(
                position,
                store,
                timeframe=timeframe,
                placer_factory=factory,
                now_ts=now_ts,
            )
        except Exception as exc:
            # Fail-open, but counted: a governed position that silently stops
            # being stepped keeps its last stop, which reads as healthy.
            fail_open.record("trail_governor.step_position", exc)
            outcome = "exception"
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
    return {
        "enabled": True,
        "timeframe": timeframe,
        "governed": len(governed),
        "outcomes": outcomes,
    }


def _default_placer_factory(firebase_uid: str) -> Any:
    from src.execution import position_fsm as _fsm

    return _fsm._default_order_placer_factory(firebase_uid)


# --------------------------------------------------------------------------- #
# The X-ray — built HERE, in the engine container, for the same reason the
# positions and data-intake diags are.
# --------------------------------------------------------------------------- #


def build_diag() -> Dict[str, Any]:
    """What the governor is doing to real orders, as a plain dict.

    **This must run in the engine container.** The position index and this
    module's counters are in-process state; in isolated mode the API
    container's ``RedisEngineFacade`` cannot see either, so an endpoint that
    built this locally would report ``index_cold`` and zeroed counters forever
    — a panel describing the API process rather than the engine.

    Caught on the deploy that shipped it (2026-08-10): the page rendered
    INDEX COLD in production while the governor itself was running fine, which
    is the "dark work must be observable" failure with the mechanism working
    and only the surface broken. Both sibling diags already carried the
    publish-then-read pattern; this one did not.
    """
    out: Dict[str, Any] = {"schema": 1}
    try:
        from config import TRAIL_GOVERNOR_ENABLED, TRAIL_GOVERNOR_TIMEFRAME

        enabled, timeframe = TRAIL_GOVERNOR_ENABLED, TRAIL_GOVERNOR_TIMEFRAME
        try:
            from src import runtime_tunables as _rt

            enabled = bool(_rt.get("trail_governor_enabled"))
            timeframe = str(_rt.get("trail_governor_timeframe"))
        except Exception as exc:
            fail_open.record("trail_governor.build_diag:tunables", exc)
        out["enabled"] = enabled
        out["timeframe"] = timeframe
        out["health"] = health()

        positions = _position_state.index_open_positions()
        if positions is None:
            out["index_cold"] = True
            out["rows"] = []
            out["open_total"] = None
            return out
        out["index_cold"] = False
        out["open_total"] = len(positions)
        now_ms = _now() * 1000.0
        rows: List[Dict[str, Any]] = []
        for p in positions:
            mech = str(getattr(p, "exit_mechanism", "") or "").lower()
            if mech not in GOVERNABLE:
                continue
            last_bar = float(getattr(p, "trail_last_bar_ms", 0.0) or 0.0)
            rows.append({
                "signal_id": p.signal_id,
                "symbol": p.symbol,
                "side": p.side,
                "mechanism": mech,
                "governing": bool(getattr(p, "trail_governing", False)),
                "entry": float(
                    p.entry_price_filled or p.entry_price_target or 0.0
                ),
                "designed_sl": float(getattr(p, "sl_price", 0.0) or 0.0),
                "parked_stop": float(getattr(p, "trail_stop_price", 0.0) or 0.0),
                "stop_order_id": int(getattr(p, "trail_stop_order_id", 0) or 0),
                "seq": int(getattr(p, "trail_stop_seq", 0) or 0),
                "last_bar_ms": last_bar or None,
                # Graded on the bar the governor consumed, stamped here in the
                # engine — a surface may not grade its own liveness on a clock
                # it supplies (#108).
                "bar_age_sec": (
                    (now_ms - last_bar) / 1000.0 if last_bar > 0 else None
                ),
                "ladder_untouched": ladder_untouched(p),
            })
        out["rows"] = rows
        out["governed"] = len(rows)
        return out
    except Exception as exc:  # noqa: BLE001
        log.exception("trail_governor.build_diag failed")
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out
