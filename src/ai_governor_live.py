"""The AI governor's counterfactual — paired against the engine's own exit.

Owner, 2026-09-09, after reading `/signals/ai-governor` from a guest session:
*"how can we edge AI governor vs engine now exits"*.

The page could not answer it, and the reason is structural rather than a
missing panel. While ``AI_GOV_APPLY_ENABLED`` is off **every recorded outcome
is the MAINTAIN counterfactual** — nothing the model said was carried out — so
for the intervention arms the closed-signal record says what happened *without*
the intervention and is silent on what acting would have produced.
``ai_governor_score`` says exactly that and refuses to guess
(``arm_undecidable_while_dark``, 47 of 47 theses on the live window).

What the page *could* offer was a **selection** statistic: the population the
governor wanted to touch ran +2.499% net against −0.521% for the one it left
alone. That number is real and it is not an effect estimate, and read as one it
points the wrong way — the only arm the model ever chooses is ``ADJUST_SL``,
the menu enforces tighter-only, and 37 of those 47 were winners. Tightening a
stop on a winner can only clip it. That is `OWNER_BRIEF` §3.2 exactly: the
pre-TP and invalidation machinery netted −25.79% where a plain TP1-full exit
netted −6.65% on the same 494 signals, because sophisticated exit logic gives
the edge back by cutting winners short.

So the comparison has to stop being between two populations and become one
**within a signal**: what did this trade do under the engine's own geometry,
and what would it have done under the geometry the governor edited, over the
same bars. That is a paired delta, it removes market conditions from the
estimate rather than averaging over them, and it is the only shape in which
this question is answerable at all before apply is armed.

Why this file is thin, again
----------------------------
``sar_live_shadow`` is not the SAR mechanism — it is the **arm engine**, and it
carries six sessions of guards that have nothing to do with trailing: the
stale-anchor refusal (#836), the per-advance replay guard (#846), the
regressed-vs-rolled-off split, the stall stamps (#835), the
timestamp-monotonicity refusal (#842/#844), the horizon rule (#839), the two
fills and the two denominators. ``atr_trail_live`` added a second mechanism and
nothing else; this adds a third. A private resolver here would be the seventh
instance of the one defect shape this repo keeps naming — and every lane that
grew its own cost a session.

The governor does not TAKE OVER the exit — it EDITS it
------------------------------------------------------
SAR and the chandelier replace the whole exit: once they govern, the arm tests
their stop and stops testing TP1. A governor verdict does not say that.
``ADJUST_SL`` moves the stop and leaves the ladder; ``ADJUST_TP`` moves the
target and leaves the stop. So ``trail_mechanisms._governor_point`` is
permanently **not onside**, the arm stays on ``GOV_GEOMETRY`` for its whole
life, and :func:`record_verdict` edits ``stop_loss`` / ``tp1`` on the row.
Against it, unmoved, runs the arm engine's ``geom_*`` control — the *original*
levels, frozen at open, walked on the same bars under the same fill rules.

``pnl_level_pct − geom_pnl_pct`` is therefore the governor's effect on that
signal, computed by one walk, with no population to select.

Delivered signals only — and that is a refusal, not an omission
---------------------------------------------------------------
SAR and the chandelier each run a dark lane, because a dark row still has bars
and a mechanism derived from bars still produces a level on it. **The governor
has no such lane and must not be given an empty one.** It evaluates signals
with open positions; a diverted row has none, so no verdict would ever arrive,
every arm would sit on unedited geometry, and the file would fill with rows
whose treatment and control are identical by construction. That is not a
measurement of anything — it is a page reporting a mechanism that was never
applied, which is precisely the artifact `/track-record`'s own rule forbids.

Three invariants, each of which is a rule this repo has already paid for
-----------------------------------------------------------------------
* **The edit obeys the menu's own direction.** SL tighter-only, TP1
  nearer-only. Not politeness: the arm engine will not widen a stop it has
  parked either, and a counterfactual allowed to move a level the live path
  would have refused measures a mechanism nobody could ship.
* **A refused edit is counted, never dropped.** A verdict that proposed a wider
  stop is evidence about the model, and a silent no-op would read as the model
  never having spoken.
* **``MAINTAIN`` edits nothing**, so the arm and its control must agree to the
  last decimal. That is a free self-check across the whole ledger and
  ``tests/test_ai_governor_live.py`` asserts it — a second computation of the
  same quantity is a detector, not a duplicate, provided it never overwrites
  the first.
"""
from __future__ import annotations

import os
import threading
from typing import Any, Dict, List, Optional

from src import fail_open, sar_live_shadow as arms
from src import trail_mechanisms as _tm
from src.trail_mechanisms import GOV_STOP_KEY, MECH_GOVERNOR
from src.utils import get_logger

log = get_logger("ai_governor_live")

#: Ledger path. **A cross-repo contract** — ops mounts the engine's ``data/``
#: read-only at ``/engine-data`` and opens this by name. Pinned on this, the
#: producing, side: #817's ``entry_regime`` was read by ops for months while
#: nothing wrote it, and the page looked full the whole time.
#:
#: There is deliberately no ``DARK_PATH`` beside it — see the module docstring.
LIVE_PATH = os.getenv("AI_GOV_LIVE_ARMS_PATH", "data/ai_gov_arms_v1.json")

#: Verdict actions this lane can express as an edit to the arm's geometry.
ACTION_SL = "ADJUST_SL"
ACTION_TP = "ADJUST_TP"
ACTION_PANIC = "PANIC_CLOSE"
ACTION_MAINTAIN = "MAINTAIN"

#: Why an edit did not land. Named rather than pooled, because the next move
#: differs for every one of them: ``no_arm`` is a coverage question (the arm
#: never opened, and ``record_open_refusal`` already says why), ``wrong_way`` is
#: a fact about the model, ``closed`` is ordinary lateness, and ``bad_level`` is
#: a menu fault.
EDIT_APPLIED = "applied"
EDIT_NO_ARM = "no_arm"
EDIT_ARM_CLOSED = "arm_closed"
EDIT_WRONG_WAY = "wrong_way"
EDIT_BAD_LEVEL = "bad_level"
EDIT_UNSUPPORTED = "unsupported_action"
EDIT_MAINTAIN = "maintain_noop"

_ledger: Optional[arms.SarLiveLedger] = None
_lock = threading.Lock()

#: Edit outcomes since boot, per action. A counter rather than a log line: the
#: owner reads a panel, and `trail_governor.place_failed` is the standing
#: reminder that a reason living only in a container log is a reason nobody has.
_edits: Dict[str, int] = {}
_edits_lock = threading.Lock()


def _count(action: str, outcome: str) -> None:
    key = f"{action.lower()}:{outcome}"
    with _edits_lock:
        _edits[key] = _edits.get(key, 0) + 1


def edit_counters() -> Dict[str, int]:
    """What every verdict did to its arm, since boot."""
    with _edits_lock:
        return dict(_edits)


def reset_counters() -> None:
    """Test hook."""
    with _edits_lock:
        _edits.clear()


def enabled() -> bool:
    """Is the governor's counterfactual running.

    Read at call time, never captured at import: a module-level snapshot of a
    config flag is how a restart becomes the only way to change a measurement.

    This is a **measurement** flag and it ships ON, per `CLAUDE.md § Project
    Phase`. The effect flag beside it (``AI_GOV_APPLY_ENABLED``) stays OFF and
    is the owner's. Shipping a measurement default-OFF is what left the SAR exit
    arm with an empty ops panel and a decision nobody could take.
    """
    try:
        from config import AI_GOV_LIVE_ARMS_ENABLED

        return bool(AI_GOV_LIVE_ARMS_ENABLED)
    except Exception:
        return False


def get_ledger() -> arms.SarLiveLedger:
    """Arms on delivered signals. ``load()`` is CALLED here, not merely defined.

    Flush without load is worse than neither: it *deletes* the window on every
    deploy while the page reports a healthy ledger. Two structural lanes shipped
    without one and erased four windows before anyone noticed the row count
    going down, and there is a derived test in this repo asserting that a module
    with ``get_ledger()`` and ``flush()`` calls ``load()`` here rather than
    owning an uncalled one.
    """
    global _ledger
    with _lock:
        if _ledger is None:
            from config import SAR_LIVE_SHADOW_MAX_RESOLVED

            _ledger = arms.SarLiveLedger(
                path=LIVE_PATH,
                max_resolved=SAR_LIVE_SHADOW_MAX_RESOLVED,
                mechanism=MECH_GOVERNOR,
            )
            _ledger.load()
        return _ledger


def reset_ledger(ledger: Optional[arms.SarLiveLedger] = None) -> None:
    """Test hook."""
    global _ledger
    with _lock:
        _ledger = ledger


def lane() -> str:
    """This lane's health key. Never the bare ``live`` one — that belongs to SAR
    and is what ``main.py``'s probes read; sharing it would let a stalled
    governor lane page as a SAR failure and a healthy SAR lane dilute a real
    governor one."""
    return arms.lane_of(MECH_GOVERNOR, dark=False)


# --------------------------------------------------------------------------- #
# Orchestration — the same two entry points, for the same reason (#835)
# --------------------------------------------------------------------------- #


def _trigger_tf(sig: Any) -> str:
    """The setup's declared trigger timeframe — the governor's own bar clock.

    **One arm per signal, not one per timeframe.** SAR and the chandelier open
    on 5m *and* 15m because each is a genuinely separate measurement of a
    mechanism derived from those bars. A governor verdict is one thesis about
    one signal (``ai_governor_score`` collapses rows to exactly that, so a
    chatty signal cannot outvote a quiet one), and copying it onto two arms
    would count one recommendation twice — #816 arriving at a counterfactual.

    A setup with no declared timeframe is **refused**, never defaulted to 5m.
    ``Scanner._get_primary_timeframe`` returned the literal ``"5m"`` for every
    channel under a docstring claiming it was a lookup, and six money-path
    consumers read it.
    """
    try:
        from src import setup_timeframes as _stf

        return str(_stf.declared_for(str(getattr(sig, "setup_class", "") or "")) or "")
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor_live.trigger_tf", exc)
        return ""


def observe_signal(
    sig: Any,
    store: Any,
    *,
    price: Optional[float] = None,
    ledger: Optional[arms.SarLiveLedger] = None,
    now_ts: Optional[float] = None,
) -> None:
    """Open this signal's governor arm on first sight."""
    if not enabled():
        return
    tf = _trigger_tf(sig)
    if not tf:
        # A counted refusal, in the same census every other open refusal lands
        # in, so "the lane produced nothing" can be told apart from "the lane
        # refused everything it was offered".
        arms.record_open_refusal(
            str(getattr(sig, "symbol", "") or ""), "", "tf_unknown", lane=lane()
        )
        return
    book = ledger if ledger is not None else get_ledger()
    stop = float(getattr(sig, "stop_loss", 0.0) or 0.0)
    arms.observe_signal(
        sig,
        store,
        price=price,
        timeframes=[tf],
        ledger=book,
        lane=lane(),
        mechanism=MECH_GOVERNOR,
        # The level in force at the anchor is the stop the trade actually has.
        # Without this seed the mechanism cannot state a level and `new_arm`
        # marks the arm INSUFFICIENT — which is the correct refusal, and is why
        # the seed is passed rather than defaulted inside the mechanism.
        mech_state={GOV_STOP_KEY: stop} if stop > 0 else {},
        now_ts=now_ts,
    )


def sweep(
    store: Any,
    *,
    price_fn: Optional[Any] = None,
    ledger: Optional[arms.SarLiveLedger] = None,
    now_ts: Optional[float] = None,
) -> Dict[str, int]:
    """Advance every open governor arm."""
    if not enabled():
        return {
            "advanced": 0, "current": 0, "stalled": 0,
            "no_series": 0, "series_corrupt": 0, "retired": 0,
        }
    book = ledger if ledger is not None else get_ledger()
    return arms.sweep(
        store, price_fn=price_fn, ledger=book, lane=lane(), now_ts=now_ts
    )


# --------------------------------------------------------------------------- #
# The edit — where a verdict becomes a counterfactual
# --------------------------------------------------------------------------- #


def _open_arm_for(book: arms.SarLiveLedger, signal_id: str) -> Optional[Dict[str, Any]]:
    """This signal's open arm, or ``None``.

    ``open_arms()`` hands back snapshots; the edit has to land on the ledger's
    own object or it is written to a copy and lost — which would be a lane that
    records every verdict and changes nothing, indistinguishable from one that
    is working.
    """
    for candidate in book.open_arms():
        if str(candidate.get("signal_id") or "") == signal_id:
            return book.get(str(candidate.get("arm_id") or ""))
    return None


def _tightens(side: str, old: float, new: float) -> bool:
    """Does ``new`` move the stop toward price for this side."""
    return new > old if str(side).upper() == "LONG" else new < old


def _nearer(side: str, old: float, new: float) -> bool:
    """Does ``new`` move the target toward price for this side."""
    return new < old if str(side).upper() == "LONG" else new > old


def record_verdict(
    signal_id: str,
    action: str,
    level: Optional[float],
    *,
    ledger: Optional[arms.SarLiveLedger] = None,
    now_ts: Optional[float] = None,
) -> str:
    """Apply one verdict to this signal's arm as an edit. Returns the outcome.

    **Called where the verdict is RECORDED, not where it is applied**, and that
    placement is the whole point. ``apply_verdict`` refuses on ``apply_off``
    before it reaches an arm check, so a hook on the apply path would record
    nothing at all while the lane is dark — which is every row this measurement
    exists to produce.

    Fail-open and counted: a counterfactual must never be able to raise into the
    loop that carries real exits, and a refusal that says nothing is how a lane
    stops working without anybody noticing.
    """
    act = str(action or "").upper()
    try:
        if not enabled():
            return EDIT_UNSUPPORTED
        if act == ACTION_MAINTAIN:
            # Recorded as an outcome rather than returning early and silently.
            # MAINTAIN is most of every window and is the BASELINE: a lane that
            # counted only its interventions could not compute one and would
            # look brilliant.
            _count(act, EDIT_MAINTAIN)
            return EDIT_MAINTAIN
        book = ledger if ledger is not None else get_ledger()
        sid = str(signal_id or "")
        arm = _open_arm_for(book, sid)
        if arm is None:
            # Two different absences, told apart because the next move differs:
            # the arm never opened (no series, stale anchor, unknown timeframe —
            # each already counted by `record_open_refusal`, and a coverage
            # fault to fix), or it opened and has since closed (ordinary
            # lateness, nothing to fix). Pooling them would report a coverage
            # problem that is not happening.
            resolved = any(
                str(r.get("signal_id") or "") == sid for r in book.resolved_arms()
            )
            outcome = EDIT_ARM_CLOSED if resolved else EDIT_NO_ARM
            _count(act, outcome)
            return outcome

        side = str(arm.get("side") or "")
        if act == ACTION_PANIC:
            # Marked, never filled here. Every fill on this row belongs to the
            # walk: a price written in from outside it would be the one number
            # on the page no bar produced, and it would not be a price anybody
            # could have got either — the verdict lands mid-bar, and the arm's
            # whole premise is decisions on closed bars. `step_arm` closes it at
            # the NEXT bar's open, which is the earliest a market close was
            # actually available, and keeps the close the model was looking at
            # as the confirm fill so the gap between them is readable.
            arm["pending_close"] = {
                "reason": arms.EXIT_GOVERNOR_PANIC,
                "at": float(now_ts) if now_ts is not None else None,
                "ref_price": arm.get("last_close"),
            }
            arm["gov_panic_edits"] = int(arm.get("gov_panic_edits") or 0) + 1
            book.mark_dirty()
            _count(act, EDIT_APPLIED)
            return EDIT_APPLIED

        try:
            price = float(level)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            _count(act, EDIT_BAD_LEVEL)
            return EDIT_BAD_LEVEL
        if not (price > 0):
            _count(act, EDIT_BAD_LEVEL)
            return EDIT_BAD_LEVEL

        if act == ACTION_SL:
            old = float(arm.get("stop_loss") or 0.0)
            if old <= 0 or not _tightens(side, old, price):
                # The menu is tighter-only and so is the arm engine. A
                # counterfactual permitted to widen a stop would measure a
                # mechanism the live path would have refused — and the refusal
                # is counted because "the model proposed a wider stop" is
                # evidence about the model, not a no-op.
                _count(act, EDIT_WRONG_WAY)
                return EDIT_WRONG_WAY
            arm["stop_loss"] = price
            # Keep the mechanism's own reading of "the level in force" beside
            # it, so a row can say what stop it has parked without a surface
            # having to know which lane it is reading.
            arm.setdefault("mech_state", {})[GOV_STOP_KEY] = price
            arm["gov_sl_edits"] = int(arm.get("gov_sl_edits") or 0) + 1
        elif act == ACTION_TP:
            old = float(arm.get("tp1") or 0.0)
            if old <= 0 or not _nearer(side, old, price):
                _count(act, EDIT_WRONG_WAY)
                return EDIT_WRONG_WAY
            arm["tp1"] = price
            arm["gov_tp_edits"] = int(arm.get("gov_tp_edits") or 0) + 1
        else:
            _count(act, EDIT_UNSUPPORTED)
            return EDIT_UNSUPPORTED

        arm["gov_last_edit_at"] = float(now_ts) if now_ts is not None else None
        book.mark_dirty()
        _count(act, EDIT_APPLIED)
        return EDIT_APPLIED
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor_live.record_verdict", exc)
        return EDIT_UNSUPPORTED


# --------------------------------------------------------------------------- #
# The paired reading — the one number the ops page could not produce
# --------------------------------------------------------------------------- #

#: Why a row cannot be paired. Named rather than pooled into one "excluded"
#: count, because the next move differs for each and pooling them would put a
#: broken walk and an ordinary still-running trade under one caption.
UNPAIRED_TREATMENT_OPEN = "treatment_still_walking"
UNPAIRED_BASELINE_OPEN = "baseline_still_walking"
UNPAIRED_TREATMENT_UNSCORED = "treatment_unscored"
UNPAIRED_BASELINE_UNSCORED = "baseline_unscored"
UNPAIRED_PRE_CONTROL = "pre_control_row"


def _delta_book(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate a set of paired deltas.

    **The round trip is not charged here, and that is arithmetic rather than an
    omission.** Both sides of a paired delta are one entry and one exit on the
    same notional, so an identical fee lands on each and cancels exactly in the
    difference. Charging it would subtract a constant from a number it does not
    belong in; the absolute columns are where the fee matters, and they are
    published beside the delta rather than folded into it.
    """
    deltas = [float(r["delta"]) for r in rows]
    n = len(deltas)
    out: Dict[str, Any] = {
        "n": n,
        "mean_delta_pct": round(sum(deltas) / n, 4) if n else None,
        "better": sum(1 for d in deltas if d > 0),
        "worse": sum(1 for d in deltas if d < 0),
        "identical": sum(1 for d in deltas if d == 0),
        "mean_treatment_pct": round(
            sum(float(r["treatment"]) for r in rows) / n, 4
        ) if n else None,
        "mean_baseline_pct": round(
            sum(float(r["baseline"]) for r in rows) / n, 4
        ) if n else None,
    }
    if n:
        # The worst single row, because a mean over a handful of rows is one
        # episode away from meaning something else — `FAILED_AUCTION_RECLAIM`'s
        # +0.846R on three rows is the standing reminder of what reading a thin
        # cell costs, and n is printed first for the same reason.
        worst = min(rows, key=lambda r: float(r["delta"]))
        out["worst_row"] = {
            "signal_id": worst.get("signal_id"),
            "symbol": worst.get("symbol"),
            "delta_pct": round(float(worst["delta"]), 4),
        }
    return out


def paired(ledger: Optional[arms.SarLiveLedger] = None) -> Dict[str, Any]:
    """The governor's effect on the signals it touched, measured against the
    engine's own exit **on the same row**.

    Every arm here walks two exits over one set of bars under one set of fill
    rules: the geometry a verdict edited (``pnl_level_pct``) and the geometry
    the evaluator shipped, frozen at open (``geom_pnl_pct``). Their difference
    is an effect estimate rather than a selection statistic — there is no
    population to choose, because the comparison never leaves the signal.

    Three properties this publishes and never blends:

    * **Per arm, never pooled.** ``ADJUST_SL``, ``ADJUST_TP`` and
      ``PANIC_CLOSE`` are three mechanisms. One number over them would move
      with whichever fired most rather than with any of them, and today two of
      the three have never fired at all.
    * **The untouched rows are a self-check, not evidence.** A ``MAINTAIN``-only
      signal edits nothing, so its treatment and its control walked identical
      geometry and must agree to the last decimal. ``agreement_violations`` is
      the count that says the walk is sound; anything above zero means the
      control is not independent of the treatment and every delta on this page
      is suspect.
    * **Coverage before any average.** A baseline that silently stops resolving
      does not empty the page — it shrinks the paired population while every
      treatment column still renders. ``unpairable`` names why each excluded
      row is excluded.
    """
    book = ledger if ledger is not None else get_ledger()
    rows = list(book.open_arms()) + list(book.resolved_arms())
    by_arm: Dict[str, List[Dict[str, Any]]] = {
        ACTION_SL: [], ACTION_TP: [], ACTION_PANIC: []
    }
    untouched: List[Dict[str, Any]] = []
    unpairable: Dict[str, int] = {}
    violations: List[Dict[str, Any]] = []

    def _skip(reason: str) -> None:
        unpairable[reason] = unpairable.get(reason, 0) + 1

    for r in rows:
        gs = r.get("geom_status")
        if gs is None:
            _skip(UNPAIRED_PRE_CONTROL)
            continue
        status = r.get("status")
        treatment = r.get("pnl_level_pct")
        baseline = r.get("geom_pnl_pct")
        if status == arms.STATUS_RUNNING:
            _skip(UNPAIRED_TREATMENT_OPEN)
            continue
        if gs == arms.GEOM_OPEN:
            _skip(UNPAIRED_BASELINE_OPEN)
            continue
        if status not in arms.CLOSED_STATUSES or treatment is None:
            # INSUFFICIENT, or a terminal status with no fill. Unscored, never
            # imputed: a row whose walk broke has no outcome, and giving it one
            # is the fabrication class arriving as a rate.
            _skip(UNPAIRED_TREATMENT_UNSCORED)
            continue
        if baseline is None:
            # A HORIZON baseline lands here by design — it walked its window and
            # touched neither level, so it has no fill. Marking it to the last
            # close would book a price the market never gave.
            _skip(UNPAIRED_BASELINE_UNSCORED)
            continue
        edits = (
            int(r.get("gov_sl_edits") or 0),
            int(r.get("gov_tp_edits") or 0),
            int(r.get("gov_panic_edits") or 0),
        )
        row = {
            "signal_id": r.get("signal_id"),
            "symbol": r.get("symbol"),
            "setup_class": r.get("setup_class"),
            "treatment": float(treatment),
            "baseline": float(baseline),
            "delta": float(treatment) - float(baseline),
        }
        if not any(edits):
            untouched.append(row)
            if row["delta"] != 0.0:
                # The control is supposed to be walking the SAME geometry on
                # the SAME bars here. A difference means it is not independent
                # of the treatment, which invalidates every delta above it —
                # so it is published as a row, not merely counted.
                violations.append(row)
            continue
        # A signal can carry edits from more than one arm over its life. It is
        # filed under each arm that touched it and the overlap is published,
        # rather than assigned to one arm by an ordering nobody chose.
        if edits[0]:
            by_arm[ACTION_SL].append(row)
        if edits[1]:
            by_arm[ACTION_TP].append(row)
        if edits[2]:
            by_arm[ACTION_PANIC].append(row)

    multi = sum(
        1 for r in rows
        if sum(
            1 for k in ("gov_sl_edits", "gov_tp_edits", "gov_panic_edits")
            if int(r.get(k) or 0)
        ) > 1
    )
    return {
        "rows_seen": len(rows),
        "per_arm": {arm: _delta_book(v) for arm, v in by_arm.items()},
        # The baseline population, and the reason it is here: it is the only
        # thing that can say the walk is sound. Its `mean_delta_pct` must be
        # exactly 0.0 and its `n` is the size of the check, not of any finding.
        "untouched": _delta_book(untouched),
        "agreement_violations": len(violations),
        "agreement_violation_rows": violations[:5],
        "touched_by_more_than_one_arm": multi,
        "unpairable": unpairable,
        # Stated rather than left to a reader who may not know the rule.
        "no_pooled_figure": (
            "Per arm only. One number across ADJUST_SL, ADJUST_TP and "
            "PANIC_CLOSE would move with whichever fired most rather than with "
            "any of them, and two of the three have never fired."
        ),
        "fee_note": (
            "No round trip is charged to a delta: both sides are one entry and "
            "one exit on the same notional, so an identical fee cancels in the "
            "difference. It is charged nowhere else on this payload either — "
            "the absolute means are gross."
        ),
    }


def build_diag() -> Dict[str, Any]:
    """Everything ops needs to render this lane, assembled in the ENGINE.

    Never in the api container: it has never stepped an arm and cannot see the
    ledger the monitor loop writes, so a version assembled there would report a
    healthy zero — `INDEX COLD`, and the promotion census before it.
    """
    try:
        book = get_ledger()
        return {
            "enabled": enabled(),
            "lane": lane(),
            "path": LIVE_PATH,
            # The manifest travels IN the payload, exactly as
            # `strategy_catalog` and the trail lanes' do: ops looks a mechanism
            # up rather than keeping a second copy, and one it has never heard
            # of renders badged rather than renamed. The fix for a drifting
            # mirror is not a second mirror.
            "mechanism": _tm.manifest(
                MECH_GOVERNOR, _tm.default_params(MECH_GOVERNOR)
            ),
            "open": len(book.open_arms()),
            "resolved": len(book.resolved_arms()),
            "coverage": book.coverage(),
            "resolution": arms.hold_arm_health(book),
            "edits": edit_counters(),
            "paired": paired(book),
            # There is deliberately no dark lane — see the module docstring. A
            # rendered state rather than an absent key, because a missing lane
            # reads as a broken deploy and this one is a decision.
            "dark_lane": "none — a diverted row has no position, so no verdict "
                         "would ever arrive and every arm would sit on unedited "
                         "geometry",
        }
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor_live.build_diag", exc)
        return {"enabled": enabled(), "error": f"{type(exc).__name__}: {exc}"}
