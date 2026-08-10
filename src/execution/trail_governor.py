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

It is avoidable, and the reason is a detail of how the stop is placed:
``place_stop_loss`` submits a CONDITIONAL algo order with
``closePosition=true``.  Such an order carries **no quantity** — it closes
whatever the position is when it triggers — so two of them resting at once
cannot double-fill or flip the position: the nearer level triggers, the
position goes to zero, and the second is left with nothing to close.  Two
stops is an over-protected state, not a dangerous one.  So the order of
operations is inverted:

1. compute the level for the bar now forming;
2. **place** the new stop (new sequence in the coid — Binance rejects a
   duplicate id);
3. only on success, **cancel** the one it replaces.

A failure at (2) leaves the previous stop exactly where it was and the governor
retries next bar.  A failure at (3) leaves two live stops and is counted as
``orphan_cancel``, retried next bar.  Neither branch is ever naked, and that is
a property of the ordering rather than of the retry working.

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

#: How far behind the clock the newest closed bar may sit before the governor
#: refuses to park a level off it, in multiples of the bar width.  Two bars of
#: slack absorbs an ordinary late close; beyond that the series is not
#: describing this market.  Deliberately the same slack the measurement lane
#: uses (``sar_live_shadow._ADVANCE_SLACK_BARS``) so the live arm and the arm it
#: is validated against do not disagree about what "current" means.
STALE_SLACK_BARS = sar_live_shadow._ADVANCE_SLACK_BARS


def _now() -> float:
    import time

    return time.time()


# --------------------------------------------------------------------------- #
# Health — keyed on the population owed a decision (#815), not on what is easy
# --------------------------------------------------------------------------- #

_health_lock = threading.Lock()


def _blank_health() -> Dict[str, Any]:
    return {
        "governed": 0,
        "handovers": 0,
        "replaced": 0,
        "unchanged": 0,
        "place_failed": 0,
        "orphan_cancel": 0,
        "refusals": {},
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


def health() -> Dict[str, Any]:
    """A snapshot for the liveness probe and the ops panel.

    Includes the refusal mix, because a governor that governs nothing looks
    identical to a quiet book unless it can say *why* — the lesson the
    price-action lane card paid for one repo over.
    """
    with _health_lock:
        out = dict(_health)
        out["refusals"] = dict(out.get("refusals", {}))
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


def forget(uid: str, signal_id: str) -> None:
    """Drop a closed position's mechanism state."""
    with _mech_state_lock:
        _mech_state.pop((uid, signal_id), None)


def reset_state_for_test() -> None:
    with _mech_state_lock:
        _mech_state.clear()


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
    which of the several quite different "nothings" it is.  Separated from the
    placement half so every branch here is testable without an exchange.
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

    parked = float(getattr(position, "trail_stop_price", 0.0) or 0.0)
    if not tightens(position.side, parked, float(point.next_stop)):
        # Includes the equal case: re-placing an identical level would spend
        # two API calls to change nothing.
        return None, "unchanged"
    return float(point.next_stop), "replace"


# --------------------------------------------------------------------------- #
# Placement half
# --------------------------------------------------------------------------- #


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
    try:
        placed = await placer.place_stop_loss(
            signal_id=position.signal_id,
            symbol=position.symbol,
            direction=position.side,
            stop_price=rounded,
            coid_override=_position_state.coid_trail(position.signal_id, seq),
        )
    except _order_placer.OrderPlacementError as exc:
        _count("place_failed")
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
                "signal_id={} exc={} — two stops resting (both closePosition, "
                "so the nearer one wins); retrying next bar",
                attr, oid, position.firebase_uid, position.signal_id, exc,
            )
    return True


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
    if level is None:
        if decision in (REFUSE_STALE, REFUSE_NO_SERIES, REFUSE_NO_LEVEL, REFUSE_NOT_ONSIDE):
            _refuse(decision)
        elif decision == "unchanged":
            _count("unchanged")
        return decision

    placer = placer_factory(position.firebase_uid)
    ok = await _park(
        position, level, placer=placer, handover=(decision == "handover")
    )
    if not ok:
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
