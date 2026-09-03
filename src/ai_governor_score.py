"""Grade every governor thesis against what the signal actually did.

`docs/PLAN_AI_TRADE_GOVERNOR_V2.md` §7. This is the **first** deliverable of the
deep-lane program and it ships ahead of any deep analysis, for a reason recorded
in that document's §1: a manual thesis on four open signals was wrong on three of
them and was falsified in four hours by a join that already existed in this repo.
Doing that by hand is not a system. Until it is automatic, this lane is the
sophisticated exit machinery that already cost 19.14 points against a plain TP1
exit (`OWNER_BRIEF` §3.2), with nothing pointed at it.

Do not build a resolver
-----------------------
Outcomes are joined from ``signal_performance.json``, which ``trade_monitor``
already writes at the terminal transition and which carries #848's corrected
``sl_distance_pct_at_entry``. Every forward-measurement arm in this repo that
grew its own resolver cost a session — `INSUFFICIENT` rows, stalled arms, stale
anchors, over-walked series, undatable windows. `entry_features` is the pattern
that avoided all of it, and this module copies it.

The subtlety that decides what may be reported
----------------------------------------------
**While the apply flag is OFF, every recorded outcome IS the `MAINTAIN`
counterfactual**, because no verdict was ever applied. That has a sharp
consequence: for the intervention arms the record says what happened *without*
the intervention, so it cannot on its own say what the intervention would have
produced. Exactly one arm escapes this, and only because of its own geometry:
``ADJUST_TP`` moves the target **nearer only**, so "would the nearer level have
been reached" is answered outright by the recorded excursion, with no ordering
ambiguity (v1 §8).

Therefore this module publishes two different kinds of number and never lets
them read as one:

* **Selection** — how the population the governor chose to touch compares with
  the population it left alone. Real, useful, and *not* an effect estimate.
* **Effect** — only for ``ADJUST_TP``, and only on the rows where the recorded
  excursion can decide it. Every other row is a **named** refusal.

There is deliberately no combined figure
----------------------------------------
One number over all four arms would move with the undecidable fraction rather
than with the mechanism. A test asserts the key does not exist.

One thesis per SIGNAL, not per verdict
--------------------------------------
An arm may issue up to ``AI_GOV_MAX_CALLS_PER_SIGNAL`` verdicts. Scoring per row
lets a chatty signal outvote a quiet one and counts one outcome several times —
which is #816 (*a throttle on rate is not a throttle on evidence*) arriving at a
scorecard. Rows collapse to one thesis per signal, and both counts are published
so the collapse ratio is visible rather than implied.
"""
from __future__ import annotations

import json
import os
import threading
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from src import fail_open
from src.utils import get_logger

log = get_logger("ai_governor_score")

MAINTAIN = "MAINTAIN"

#: The arms that can intervene. `MAINTAIN` is not an arm anybody arms, so it is
#: the baseline rather than a member.
INTERVENTION_ACTIONS = ("ADJUST_TP", "ADJUST_SL", "PANIC_CLOSE")

#: Round trip, both legs, as a percentage of notional — the same default the
#: track record uses. Charged to **both** sides of every comparison: charging it
#: to the intervention and not to the baseline manufactures an edge out of the
#: fee, and charging it to neither hides the cost that dominates this book.
DEFAULT_FEE_PCT = 0.07

#: Why a thesis could not be graded. Named rather than pooled, because the next
#: move differs for each: an open signal is a wait, a missing excursion is an
#: engine-stamp question, and an unresolved choice key is a ledger fault.
WHY_STILL_OPEN = "still_open_or_undelivered"
WHY_NO_PNL = "no_pnl"
WHY_NO_MFE = "no_excursion_stamp"
WHY_CHOICE_UNRESOLVED = "choice_not_in_menu"
WHY_NO_DISTANCE = "candidate_has_no_distance"
WHY_ARM_UNDECIDABLE = "arm_undecidable_while_dark"


# ---------------------------------------------------------------------------
# Loading — a different projection of the same file, not a second cache of one
# ---------------------------------------------------------------------------

#: ``track_record.load_rows`` caches the **display** reduction, which drops the
#: excursion fields this module needs to decide the TP arm. So this is a second
#: consumer of one file rather than a mirror of one cache, and it is gated on
#: the same invalidation signal the writer itself produces — the file's mtime
#: and size — never on a TTL.
_cache_lock = threading.Lock()
_cache_stamp: Optional[Tuple[str, int, int]] = None
_cache_rows: Optional[List[Dict[str, Any]]] = None

#: Only the fields a grade needs. Keeping this narrow is not tidiness: the raw
#: record is multi-megabyte and every field carried here is one a reader may
#: later mistake for evidence.
_RECORD_FIELDS = (
    "signal_id",
    "symbol",
    "outcome_label",
    "pnl_pct",
    "sl_distance_pct_at_entry",
    "max_favorable_excursion_pct",
    "max_adverse_excursion_pct",
)


def _stamp(path: str) -> Optional[Tuple[str, int, int]]:
    try:
        st = os.stat(path)
    except OSError:
        return None
    return (path, st.st_mtime_ns, st.st_size)


def load_records(path: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Read the closed-signal record, keeping the excursion fields.

    Returns ``(rows, error)``. ``error`` is a short reason, never a silent empty
    list: a file the engine has not written yet and one it cannot parse have
    different fixes, and a caller that cannot tell them apart renders "no
    trades" for both.

    ``path`` resolves at call time rather than as a default argument, so a test
    can repoint the constant — a default argument binds it at import, which is
    the "read once, meant every time" shape this repo has paid for elsewhere.
    """
    global _cache_stamp, _cache_rows

    from src import track_record as _tr

    path = path or _tr.DEFAULT_RECORD_PATH
    stamp = _stamp(path)
    if stamp is None:
        with _cache_lock:
            _cache_stamp, _cache_rows = None, None
        return [], "missing"
    with _cache_lock:
        if stamp == _cache_stamp and _cache_rows is not None:
            return _cache_rows, None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, ValueError) as exc:
        log.warning("governor scorer: record unreadable at %s: %s", path, exc)
        return [], "unreadable"
    if not isinstance(raw, list):
        return [], "unexpected_shape"
    rows = [
        {k: rec.get(k) for k in _RECORD_FIELDS}
        for rec in raw
        if isinstance(rec, dict) and rec.get("signal_id")
    ]
    with _cache_lock:
        _cache_stamp, _cache_rows = stamp, rows
    return rows, None


def reset_cache() -> None:
    """Drop the loader cache. Tests only — production invalidates on mtime."""
    global _cache_stamp, _cache_rows
    with _cache_lock:
        _cache_stamp, _cache_rows = None, None


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _f(value: Any) -> Optional[float]:
    """Float or None. ``None`` means *we could not read this*, never zero — an
    em-dash and a 0.00 are different facts and only one of them is a finding."""
    if value is None or isinstance(value, bool):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if out == out else None  # NaN is not a reading


def thesis_per_signal(rows: Sequence[Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Collapse verdict rows to one thesis per signal, newest-wins.

    A signal counts as **intervened** if *any* verdict on it was not
    ``MAINTAIN``: the governor proposed acting at some point in that trade's
    life, and that is the population an intervention arm is judged on. The
    thesis is the last such verdict; where there is none it is the last verdict
    of any kind.

    ``flip_flopped`` marks a signal whose verdicts disagreed. It is its own
    state rather than evidence for either arm — a governor that says
    ``ADJUST_TP`` and then ``MAINTAIN`` on the same trade has not made one
    recommendation, and folding it into either bucket reports a decisiveness
    nobody observed.
    """
    out: Dict[str, Dict[str, Any]] = {}
    for row in rows or []:
        sid = str(row.get("signal_id") or "")
        if not sid:
            continue
        action = str(row.get("action") or "")
        slot = out.setdefault(
            sid,
            {
                "signal_id": sid,
                "n_verdicts": 0,
                "actions": {},
                "thesis": None,
                "last_any": None,
            },
        )
        slot["n_verdicts"] = int(slot["n_verdicts"]) + 1
        slot["actions"][action] = int(slot["actions"].get(action, 0)) + 1
        slot["last_any"] = row
        if action in INTERVENTION_ACTIONS:
            slot["thesis"] = row

    for slot in out.values():
        if slot["thesis"] is None:
            slot["thesis"] = slot["last_any"]
        actions = slot["actions"]
        thesis = slot["thesis"] or {}
        slot["action"] = str(thesis.get("action") or "")
        slot["intervened"] = slot["action"] in INTERVENTION_ACTIONS
        slot["flip_flopped"] = len([a for a in actions if a]) > 1
        slot["unknown_frac"] = _f(thesis.get("unknown_frac"))
        # Lifted onto the slot beside `action`, because every consumer past this
        # point works on the slot and reaching back into the nested verdict is
        # the seam that made three of this file's own tests fail first time:
        # two halves that each looked complete, and nothing between them.
        slot["choice"] = thesis.get("choice")
        slot["snapshot"] = thesis.get("snapshot") or {}
    return out


def _chosen_distance(thesis: Mapping[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    """Distance of the candidate the model actually chose, signed toward the
    trade, resolved from the menu **stored with that verdict**.

    Resolving against the stored menu rather than rebuilding one is what makes a
    choice key mean the same thing months later — and a key that is not in its
    own menu is a ledger fault worth naming, not a row to drop quietly.
    """
    choice = thesis.get("choice")
    if not choice:
        return None, WHY_CHOICE_UNRESOLVED
    snapshot = thesis.get("snapshot") or {}
    pools = list(snapshot.get("tp_candidates") or []) + list(snapshot.get("sl_candidates") or [])
    for cand in pools:
        if isinstance(cand, dict) and str(cand.get("key")) == str(choice):
            dist = _f(cand.get("dist_pct"))
            return (dist, None) if dist is not None else (None, WHY_NO_DISTANCE)
    return None, WHY_CHOICE_UNRESOLVED


def join(
    theses: Mapping[str, Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Join theses to closed-signal records on ``signal_id``.

    Coverage is not decoration. A thesis with no record is a signal still open
    or one the router never delivered; a record with no thesis predates this
    lane or was never armed. Both populations are published, because a join that
    silently keeps only what matched reports a book that is not the book.
    """
    by_id = {str(r.get("signal_id") or ""): r for r in records or []}
    joined: List[Dict[str, Any]] = []
    unmatched = 0
    for sid, slot in (theses or {}).items():
        rec = by_id.get(sid)
        if rec is None:
            unmatched += 1
            continue
        row = dict(slot)
        row["pnl_pct"] = _f(rec.get("pnl_pct"))
        row["mfe_pct"] = _f(rec.get("max_favorable_excursion_pct"))
        row["mae_pct"] = _f(rec.get("max_adverse_excursion_pct"))
        row["sl_distance_pct_at_entry"] = _f(rec.get("sl_distance_pct_at_entry"))
        row["outcome_label"] = str(rec.get("outcome_label") or "")
        row["symbol"] = str(rec.get("symbol") or "")
        joined.append(row)
    matched_ids = {str(r.get("signal_id")) for r in joined}
    return joined, {
        "theses": len(theses or {}),
        "records": len(records or []),
        "joined": len(joined),
        WHY_STILL_OPEN: unmatched,
        "records_without_thesis": max(0, len(by_id) - len(matched_ids)),
    }


def _book(rows: Sequence[Mapping[str, Any]], fee_pct: float) -> Dict[str, Any]:
    """Gross and net book over rows carrying a readable PnL.

    Two denominators, kept apart: ``n`` is every row in the bucket, ``n_pnl``
    those that could be priced. Every figure divides by the second and
    ``no_pnl`` states the gap, so a caller can say on screen when they differ.
    """
    gross = [p for p in (_f(r.get("pnl_pct")) for r in rows) if p is not None]
    net = [p - fee_pct for p in gross]
    wins = sum(1 for p in net if p > 0)
    return {
        "n": len(rows),
        "n_pnl": len(gross),
        "no_pnl": len(rows) - len(gross),
        "wins": wins,
        "losses": len(net) - wins,
        "total_pnl_pct": round(sum(gross), 4) if gross else 0.0,
        "avg_pnl_pct": round(sum(gross) / len(gross), 4) if gross else None,
        "net_total_pnl_pct": round(sum(net), 4) if net else 0.0,
        "net_avg_pnl_pct": round(sum(net) / len(net), 4) if net else None,
    }


def selection(joined: Sequence[Mapping[str, Any]], fee_pct: float) -> Dict[str, Any]:
    """How the touched population compares with the untouched one.

    **This is a selection statistic, not an effect estimate**, and the
    distinction is the whole reason it is named this way. While the apply flag
    is off nothing the governor said was carried out, so both books below record
    what happened *anyway*. A governor that reliably flags the trades that go on
    to lose is doing something useful and this panel can see it; what this panel
    cannot see is what would have happened had anyone acted.
    """
    touched = [r for r in joined if r.get("intervened")]
    left = [r for r in joined if not r.get("intervened")]
    return {
        "fee_pct": fee_pct,
        "intervened": _book(touched, fee_pct),
        "maintain_only": _book(left, fee_pct),
        "flip_flopped": sum(1 for r in joined if r.get("flip_flopped")),
    }


def tp_arm(joined: Sequence[Mapping[str, Any]], fee_pct: float) -> Dict[str, Any]:
    """The one arm the record can decide outright while the lane is dark.

    ``ADJUST_TP`` moves the target **nearer only**, so a nearer level was
    reached iff the recorded favourable excursion covers its distance — every
    excursion precedes the close, so there is no ordering ambiguity (v1 §8).
    Where it was reached the arm books the nearer distance instead of what the
    trade actually made, and the delta is signed: **negative means the arm would
    have clipped a winner**, which is precisely the mistake §1 of the v2 plan
    records a human making on BULLA.

    Two biases, stated rather than presented as exactness:

    * MFE is updated on **mark-price ticks, not intrabar**, so "reached" is
      conservative — this can under-count rescues and can never invent one.
    * A row whose excursion was never stamped is **refused by name**, not
      treated as unreached. Unreached and unknown remove opposite ends of the
      distribution.
    """
    rows = [r for r in joined if str(r.get("action") or "") == "ADJUST_TP"]
    refusals: Dict[str, int] = {}
    deltas: List[float] = []
    reached = 0
    decided = 0

    for row in rows:
        pnl = _f(row.get("pnl_pct"))
        mfe = _f(row.get("mfe_pct"))
        dist, why = _chosen_distance(row)
        if pnl is None:
            refusals[WHY_NO_PNL] = refusals.get(WHY_NO_PNL, 0) + 1
            continue
        if why:
            refusals[why] = refusals.get(why, 0) + 1
            continue
        if mfe is None:
            refusals[WHY_NO_MFE] = refusals.get(WHY_NO_MFE, 0) + 1
            continue
        decided += 1
        if dist is not None and mfe >= dist:
            reached += 1
            # The arm exits at the nearer level; the trade's own exit never
            # happens. The fee is charged to both sides and therefore cancels
            # out of the delta — which is why the delta, and not the two
            # absolute books, is the honest number here.
            deltas.append(float(dist) - pnl)
        else:
            # Never reached, so the trade ran to its own exit unchanged. A zero
            # delta is a real measurement here, not a missing one.
            deltas.append(0.0)

    return {
        "n": len(rows),
        "decidable": decided,
        "undecidable": refusals,
        "reached": reached,
        "unreached": decided - reached,
        "avg_delta_pct": round(sum(deltas) / len(deltas), 4) if deltas else None,
        "total_delta_pct": round(sum(deltas), 4) if deltas else 0.0,
        "bias_note": (
            "MFE is tick-sampled, not intrabar, so 'reached' is conservative; "
            "unstamped excursions are refused by name, never counted as unreached."
        ),
    }


def _dark_arm(joined: Sequence[Mapping[str, Any]], action: str) -> Dict[str, Any]:
    """An arm the record cannot decide while nothing is applied.

    Published as a **counted, named** state rather than omitted: an arm missing
    from this block would read as one that never fired, and the two have
    opposite meanings.
    """
    rows = [r for r in joined if str(r.get("action") or "") == action]
    return {
        "n": len(rows),
        "decidable": 0,
        "undecidable": {WHY_ARM_UNDECIDABLE: len(rows)} if rows else {},
        "why": (
            "Nothing was applied, so the record shows what happened WITHOUT this "
            "arm. Deciding it needs either a live window or a counterfactual walk, "
            "and for the SL arm two of its cases are not in the record at all."
        ),
    }


def score(
    verdict_rows: Sequence[Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]],
    *,
    fee_pct: float = DEFAULT_FEE_PCT,
    record_error: Optional[str] = None,
) -> Dict[str, Any]:
    """The whole scorecard. Pure — every input arrives as a parameter.

    Deliberately returns **no** blended across-arm figure. One number over four
    arms would move with the undecidable fraction rather than with the
    mechanism, and a test asserts no such key appears.
    """
    theses = thesis_per_signal(verdict_rows)
    joined, coverage = join(theses, records)
    coverage["verdict_rows"] = len(verdict_rows or [])
    coverage["record_error"] = record_error

    mix: Dict[str, int] = {}
    for slot in theses.values():
        action = str(slot.get("action") or "")
        if action:
            mix[action] = mix.get(action, 0) + 1

    blind = [f for f in (slot.get("unknown_frac") for slot in theses.values()) if f is not None]

    return {
        "coverage": coverage,
        # Per SIGNAL. The verdict count is beside it in coverage so the collapse
        # ratio is visible rather than implied.
        "mix": mix,
        "blindness": {
            "theses_with_stamp": len(blind),
            "avg_unknown_frac": round(sum(blind) / len(blind), 4) if blind else None,
            "fully_blind": sum(1 for f in blind if f >= 1.0),
        },
        "selection": selection(joined, fee_pct),
        "arms": {
            "ADJUST_TP": tp_arm(joined, fee_pct),
            "ADJUST_SL": _dark_arm(joined, "ADJUST_SL"),
            "PANIC_CLOSE": _dark_arm(joined, "PANIC_CLOSE"),
        },
        "shadow_note": (
            "Apply is OFF, so every recorded outcome is the MAINTAIN "
            "counterfactual. 'selection' compares the populations; only ADJUST_TP "
            "is an effect estimate, and only on its decidable rows."
        ),
    }


def build(
    verdict_rows: Sequence[Mapping[str, Any]],
    *,
    fee_pct: float = DEFAULT_FEE_PCT,
    path: Optional[str] = None,
) -> Dict[str, Any]:
    """`score` with the records loaded. The only function here that does I/O."""
    try:
        records, err = load_records(path)
    except Exception as exc:  # noqa: BLE001 — a scorecard never blocks the lane
        fail_open.record("ai_governor_score.build", exc)
        records, err = [], "unreadable"
    return score(verdict_rows, records, fee_pct=fee_pct, record_error=err)
