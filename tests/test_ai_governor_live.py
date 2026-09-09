"""The governor's paired counterfactual — and the guards that make it readable.

Owner, 2026-09-09: *"how can we edge AI governor vs engine now exits"*.

While ``AI_GOV_APPLY_ENABLED`` is off, the closed-signal record is the MAINTAIN
counterfactual, so it says what happened WITHOUT the intervention and cannot say
what acting would have produced. The scorecard says exactly that and refuses to
guess. This lane answers it by walking both exits on **one row over one set of
bars**: the geometry a verdict edited, and the geometry the evaluator shipped.

Three kinds of test here.

**Behaviour** — an edit lands, a wrong-way edit is refused and counted, a panic
fills at the next bar's open.

**The self-check** — a ``MAINTAIN``-only signal edits nothing, so its treatment
and its control walked identical geometry and must agree to the last decimal.
That is the property the whole comparison rests on, and it is asserted rather
than assumed: a second computation of the same quantity is a detector, not a
duplicate, provided it never overwrites the first.

**Seams** — the defect shape this repo keeps paying for is two halves that each
look complete. So these parse **call sites**: ``record_verdict`` being
importable says nothing about whether the governor calls it, and hooking it on
the apply path would record nothing at all while the lane is dark, which is
every row the measurement exists to produce.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from src import ai_governor_live as cf
from src import sar_live_shadow as arms
from src import trail_mechanisms as tm

ROOT = pathlib.Path(__file__).resolve().parents[1]
BAR_MS = 900_000.0


def _series(bars):
    return {
        "open": [b[0] for b in bars],
        "high": [b[1] for b in bars],
        "low": [b[2] for b in bars],
        "close": [b[3] for b in bars],
        "open_time": [1_700_000_000_000.0 + i * BAR_MS for i in range(len(bars))],
    }


def _flat(n, price=100.0):
    """Bars that touch nothing, so a walk advances without closing anything."""
    return [(price, price + 0.2, price - 0.2, price) for _ in range(n)]


def _now_at(bar_index, width_sec=BAR_MS / 1000.0):
    return (1_700_000_000_000.0 + bar_index * BAR_MS) / 1000.0 + width_sec


def _arm(bars, *, side="LONG", entry=100.0, sl=97.0, tp1=105.0, sid="SIG-CF"):
    s = _series(bars)
    state = {tm.GOV_STOP_KEY: sl}
    point = tm.point(
        tm.MECH_GOVERNOR, None, s["high"], s["low"], s["close"],
        len(s["high"]) - 1, side=side, state=state, params={},
        last_closed_ms=s["open_time"][-1],
    )
    return arms.new_arm(
        signal_id=sid, symbol="TESTUSDT", side=side,
        setup_class="MOVER_TREND_PULLBACK", timeframe="15m",
        entry=entry, stop_loss=sl, tp1=tp1, point=point,
        opened_ms=s["open_time"][-1], original_sl_distance=entry - sl,
        mechanism=tm.MECH_GOVERNOR, mech_params={}, mech_state=state,
        now_ts=_now_at(len(bars) - 1),
    )


@pytest.fixture(autouse=True)
def _isolated(monkeypatch):
    """An in-memory ledger and clean counters per test.

    ``path=""`` returns BEFORE the atomic write, so nothing touches the repo
    root under pytest — two structural ledgers took it to mean "in memory" and
    ran their write anyway, filling `fail_open` with non-failures for months.
    """
    ledger = arms.SarLiveLedger(path="", mechanism=tm.MECH_GOVERNOR)
    cf.reset_ledger(ledger)
    cf.reset_counters()
    monkeypatch.setattr(cf, "enabled", lambda: True)
    yield ledger
    cf.reset_ledger(None)
    cf.reset_counters()


# --------------------------------------------------------------------------- #
# The mechanism never governs — and that is the design, not a bug
# --------------------------------------------------------------------------- #


def test_the_governor_mechanism_is_never_onside():
    """SAR and the chandelier TAKE OVER the exit; the governor EDITS it.

    A handover would stop the arm testing TP1, silently deleting the half of the
    exit the verdict never mentioned — and the arm would then measure a
    mechanism nobody proposed. Two arms named for one mechanism measuring two
    already cost a session on 2026-07-31.
    """
    s = _series(_flat(10))
    point = tm.point(
        tm.MECH_GOVERNOR, None, s["high"], s["low"], s["close"], 9,
        side="LONG", state={tm.GOV_STOP_KEY: 97.0}, params={},
    )
    assert point is not None
    assert point.onside is False
    assert point.next_stop == pytest.approx(97.0)
    # No direction of its own. `None`, never `False` — "does not answer that"
    # and "says down" are different facts.
    assert point.up is None


def test_a_governor_arm_stays_on_the_engines_geometry_for_life():
    arm = _arm(_flat(30))
    assert arm["governor"] == arms.GOV_GEOMETRY
    assert arm["aligned_at_entry"] is False
    assert arm["status"] == arms.STATUS_RUNNING


def test_the_mechanism_refuses_when_no_level_was_seeded():
    """`new_arm` marks INSUFFICIENT rather than inventing a level (#800).

    This is why the seed is passed in from the lane rather than defaulted inside
    the mechanism: a default would turn "we cannot state this arm's stop" into a
    wrong answer with no signal.
    """
    s = _series(_flat(10))
    assert tm.point(
        tm.MECH_GOVERNOR, None, s["high"], s["low"], s["close"], 9,
        side="LONG", state={}, params={},
    ) is None


def test_the_governor_is_not_a_live_governable_mechanism():
    """A forward guard, and the most important line in this file.

    ``trail_governor.GOVERNABLE`` is ``frozenset(trail_mechanisms.MECHANISMS)``,
    so anything added to that tuple becomes selectable as a per-user exit
    mechanism that moves a resting stop on a real position. This mechanism's
    levels come from a model. Putting it there would let an LLM's choice reach a
    live order through a set nobody reads as a permission list.
    """
    from src.api import user_overrides
    from src.execution import trail_governor

    assert tm.MECH_GOVERNOR not in tm.MECHANISMS
    assert tm.MECH_GOVERNOR in tm.ARM_MECHANISMS
    assert tm.MECH_GOVERNOR not in trail_governor.GOVERNABLE
    assert tm.MECH_GOVERNOR not in user_overrides.EXIT_MECHANISMS


# --------------------------------------------------------------------------- #
# The geometry control — the paired baseline
# --------------------------------------------------------------------------- #


def test_the_control_walks_the_original_levels_and_the_treatment_can_diverge():
    """The whole comparison in one test.

    The stop is edited to 99.0; the control keeps 97.0. A bar to 98.0 takes the
    edited stop and leaves the control running — so one row now carries two
    different outcomes over identical bars, which is what makes the delta an
    effect estimate rather than a selection statistic.
    """
    bars = _flat(30)
    arm = _arm(bars)
    assert arm["geom_sl"] == pytest.approx(97.0)
    assert arm["geom_tp1"] == pytest.approx(105.0)

    arm["stop_loss"] = 99.0          # what an ADJUST_SL verdict does
    dip = (100.0, 100.2, 98.0, 99.5)
    arms.step_arm(arm, _series(bars + [dip]), now_ts=_now_at(len(bars)))

    assert arm["status"] == arms.STATUS_CLOSED_SL
    assert arm["fill_level"] == pytest.approx(99.0)
    # The control never saw the edit and is still walking its own geometry.
    assert arm["geom_status"] == arms.GEOM_OPEN
    assert arm["geom_pnl_pct"] is None


def test_an_unedited_arm_and_its_control_agree_exactly():
    """The self-check the whole page rests on.

    A MAINTAIN-only signal edits nothing, so treatment and control walked
    identical geometry under identical fill rules. Anything but exact agreement
    means the control is not independent of the treatment and every delta is
    suspect — which is why `paired()` publishes `agreement_violations` as rows
    rather than as a count alone.
    """
    bars = _flat(30)
    arm = _arm(bars)
    dip = (100.0, 100.2, 96.0, 97.5)
    arms.step_arm(arm, _series(bars + [dip]), now_ts=_now_at(len(bars)))

    assert arm["status"] == arms.STATUS_CLOSED_SL
    assert arm["geom_status"] == arms.GEOM_SL
    assert arm["geom_pnl_pct"] == pytest.approx(arm["pnl_level_pct"])


def test_the_control_dies_with_every_other_arm_on_a_broken_walk():
    """A broken walk terminates EVERY arm on the row, not just the mechanism.

    Terminating some would leave a row whose treatment is scored and whose
    baseline is not — which reads as a result rather than as a broken walk, and
    it is exactly how a paired population silently shrinks while every column
    still renders. The existing abandon test caught this omission on the first
    run of the geometry control.
    """
    bars = _flat(30)
    arm = _arm(bars)
    # A window whose oldest bar is newer than the arm's last: history rolled off.
    rolled = {
        k: v[5:] for k, v in _series(bars).items()
    }
    rolled["open_time"] = [t + 100 * BAR_MS for t in rolled["open_time"]]
    arms.step_arm(arm, rolled, now_ts=_now_at(len(bars)))

    assert arm["status"] == arms.STATUS_INSUFFICIENT
    assert arm["hold_status"] == arms.HOLD_INSUFFICIENT
    assert arm["geom_status"] == arms.GEOM_INSUFFICIENT
    assert arm["geom_exit_reason"] == arm["exit_reason"]


def test_a_horizon_control_is_unscored_rather_than_marked_to_the_last_close():
    """An expiry is a walked window in which nothing happened.

    Marking it to the last close would book a fill the market never gave, and
    the row would then be scored against a price nobody could have got — so the
    baseline stays blank and `paired()` excludes the row by name.
    """
    ledger = arms.SarLiveLedger(path="", mechanism=tm.MECH_GOVERNOR)
    arm = _arm(_flat(30))
    ledger.add(arm)
    arms.sweep(
        None, ledger=ledger, lane=cf.lane(),
        now_ts=_now_at(29) + 49 * 3600, max_open_hours=48,
    )
    row = ledger.resolved_arms()[0]
    assert row["geom_status"] == arms.GEOM_HORIZON
    assert row["geom_pnl_pct"] is None


# --------------------------------------------------------------------------- #
# The edit
# --------------------------------------------------------------------------- #


def test_a_tighter_stop_is_applied_and_counted(_isolated):
    arm = _arm(_flat(30))
    _isolated.add(arm)
    assert cf.record_verdict("SIG-CF", "ADJUST_SL", 99.0) == cf.EDIT_APPLIED
    assert _isolated.get(arm["arm_id"])["stop_loss"] == pytest.approx(99.0)
    assert cf.edit_counters()["adjust_sl:applied"] == 1
    # The control is untouched — that is the pairing.
    assert _isolated.get(arm["arm_id"])["geom_sl"] == pytest.approx(97.0)


def test_a_wider_stop_is_refused_and_the_refusal_is_counted(_isolated):
    """The menu is tighter-only and so is the arm engine.

    A counterfactual allowed to widen a stop would measure a mechanism the live
    path would have refused. And the refusal is COUNTED rather than silently
    dropped: "the model proposed a wider stop" is evidence about the model, and
    a silent no-op would read as the model never having spoken.
    """
    arm = _arm(_flat(30))
    _isolated.add(arm)
    assert cf.record_verdict("SIG-CF", "ADJUST_SL", 95.0) == cf.EDIT_WRONG_WAY
    assert _isolated.get(arm["arm_id"])["stop_loss"] == pytest.approx(97.0)
    assert cf.edit_counters()["adjust_sl:wrong_way"] == 1


def test_a_short_is_signed_toward_the_trade(_isolated):
    """Tighter means the opposite price direction on a SHORT.

    `cvd_slope` and `book_imbalance` shipped raw once and were split with one
    "higher is better" rule, which scored every SHORT backwards for a month. The
    delivered book is ~50/50 by side, so an error here would not empty a column
    — it would make the arm look like noise.
    """
    arm = _arm(_flat(30), side="SHORT", sl=103.0, tp1=95.0, sid="SIG-S")
    _isolated.add(arm)
    assert cf.record_verdict("SIG-S", "ADJUST_SL", 101.0) == cf.EDIT_APPLIED
    assert cf.record_verdict("SIG-S", "ADJUST_SL", 104.0) == cf.EDIT_WRONG_WAY
    assert cf.record_verdict("SIG-S", "ADJUST_TP", 97.0) == cf.EDIT_APPLIED
    assert cf.record_verdict("SIG-S", "ADJUST_TP", 94.0) == cf.EDIT_WRONG_WAY


def test_maintain_edits_nothing_and_is_still_recorded(_isolated):
    """A lane that counts only its interventions cannot compute a baseline and
    will look brilliant."""
    arm = _arm(_flat(30))
    _isolated.add(arm)
    assert cf.record_verdict("SIG-CF", "MAINTAIN", None) == cf.EDIT_MAINTAIN
    assert cf.edit_counters()["maintain:maintain_noop"] == 1
    assert _isolated.get(arm["arm_id"])["stop_loss"] == pytest.approx(97.0)


def test_a_verdict_with_no_open_arm_is_named_not_dropped(_isolated):
    """`no_arm` and `arm_closed` are different faults: the first is coverage to
    fix, the second is ordinary lateness."""
    assert cf.record_verdict("SIG-NEVER", "ADJUST_SL", 99.0) == cf.EDIT_NO_ARM
    assert cf.edit_counters()["adjust_sl:no_arm"] == 1


def test_a_panic_fills_at_the_next_bars_open_and_keeps_both_fills(_isolated):
    """A verdict lands mid-bar; the earliest price actually available is the
    next bar's open. The close the model was looking at is kept as the confirm
    fill, so the cost of not being able to act instantly is readable rather than
    collapsed into one flattering number."""
    bars = _flat(30)
    arm = _arm(bars)
    _isolated.add(arm)
    arm["last_close"] = 100.0
    assert cf.record_verdict("SIG-CF", "PANIC_CLOSE", None) == cf.EDIT_APPLIED

    nxt = (101.0, 101.4, 100.6, 101.2)
    arms.step_arm(arm, _series(bars + [nxt]), now_ts=_now_at(len(bars)))
    assert arm["status"] == arms.STATUS_CLOSED_PANIC
    assert arm["exit_reason"] == arms.EXIT_GOVERNOR_PANIC
    assert arm["fill_level"] == pytest.approx(101.0)     # the bar's open
    assert arm["fill_confirm"] == pytest.approx(100.0)   # what the model saw
    assert arm["pending_close"] is None


# --------------------------------------------------------------------------- #
# The paired reading
# --------------------------------------------------------------------------- #


def test_paired_reports_per_arm_and_never_pools_them(_isolated):
    """One number across three mechanisms would move with whichever fired most
    rather than with any of them — and two of the three have never fired."""
    out = cf.paired(_isolated)
    assert set(out["per_arm"]) == {"ADJUST_SL", "ADJUST_TP", "PANIC_CLOSE"}
    flat = str(out).lower()
    for banned in ("pooled_delta", "combined_delta", "overall_delta"):
        assert banned not in flat


def test_paired_names_every_excluded_row_rather_than_pooling_them(_isolated):
    """A baseline that stops resolving shrinks the paired population while every
    treatment column still renders. `unpairable` is the only thing that says so.
    """
    arm = _arm(_flat(30))
    _isolated.add(arm)
    out = cf.paired(_isolated)
    assert out["unpairable"] == {cf.UNPAIRED_TREATMENT_OPEN: 1}
    assert out["per_arm"]["ADJUST_SL"]["n"] == 0
    assert out["per_arm"]["ADJUST_SL"]["mean_delta_pct"] is None


def test_paired_flags_an_unedited_row_whose_walks_disagree(_isolated):
    """The detector. An untouched row is required to agree exactly; a violation
    invalidates every delta above it, so it is published as a row."""
    bars = _flat(30)
    arm = _arm(bars)
    dip = (100.0, 100.2, 96.0, 97.5)
    arms.step_arm(arm, _series(bars + [dip]), now_ts=_now_at(len(bars)))
    _isolated.add(arm)

    clean = cf.paired(_isolated)
    assert clean["agreement_violations"] == 0
    assert clean["untouched"]["n"] == 1
    assert clean["untouched"]["mean_delta_pct"] == 0.0

    # Corrupt the control and confirm the check bites.
    arm["geom_pnl_pct"] = float(arm["geom_pnl_pct"]) + 1.0
    dirty = cf.paired(_isolated)
    assert dirty["agreement_violations"] == 1
    assert dirty["agreement_violation_rows"][0]["signal_id"] == "SIG-CF"


def test_paired_scores_an_edited_row_against_its_own_control(_isolated):
    bars = _flat(30)
    arm = _arm(bars)
    _isolated.add(arm)
    cf.record_verdict("SIG-CF", "ADJUST_SL", 99.0, ledger=_isolated)
    # A bar that takes the edited stop AND the original one, so both walks score.
    dip = (100.0, 100.2, 96.0, 97.5)
    arms.step_arm(arm, _series(bars + [dip]), now_ts=_now_at(len(bars)))

    out = cf.paired(_isolated)
    sl = out["per_arm"]["ADJUST_SL"]
    assert sl["n"] == 1
    # The tighter stop got out at 99.0 against the original's 97.0, so on this
    # loser the governor saved money and the delta is positive.
    assert sl["mean_delta_pct"] > 0
    assert sl["better"] == 1
    assert out["untouched"]["n"] == 0


# --------------------------------------------------------------------------- #
# Seams — the call sites, not the definitions
# --------------------------------------------------------------------------- #


def test_the_governor_records_the_counterfactual_where_it_LOGS_a_verdict():
    """Not on the apply path, and this is the load-bearing seam.

    `apply_verdict` refuses on `apply_off` before it ever reaches an arm check,
    so a hook there would record nothing at all while the lane is dark — which
    is every row this measurement exists to produce. The hook has to sit beside
    `ledger.add`, and an AST check is what pins that rather than a comment.
    """
    src = (ROOT / "src" / "execution" / "ai_governor.py").read_text()
    tree = ast.parse(src)
    holder = None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = ast.dump(node)
        if "'ledger'" in body and "_record_counterfactual" in body:
            holder = node.name
            break
    assert holder is not None, (
        "no function both writes the verdict ledger and records the "
        "counterfactual — the hook has moved off the recording path"
    )
    assert holder != "apply_verdict"

    apply_fn = next(
        n for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and n.name == "apply_verdict"
    )
    assert "_record_counterfactual" not in ast.dump(apply_fn)


def test_the_monitor_loop_opens_sweeps_and_flushes_this_lane():
    """Defining `sweep` is not calling it. The lane rides the monitor loop
    beside SAR and the chandelier, so the call sites are parsed there."""
    src = (ROOT / "src" / "trade_monitor.py").read_text()
    for call in (
        "ai_governor_live.observe_signal(",
        "ai_governor_live.sweep(",
        "ai_governor_live.get_ledger().flush()",
        "sar_live_shadow.roll_health_cycle(ai_governor_live.lane())",
    ):
        assert call in src, f"missing call site in trade_monitor.py: {call}"


def test_get_ledger_calls_load_rather_than_merely_defining_one():
    """Flush without load DELETES the window on every deploy while the page
    reports a healthy ledger. Two structural lanes erased four windows to it."""
    tree = ast.parse((ROOT / "src" / "ai_governor_live.py").read_text())
    fn = next(
        n for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "get_ledger"
    )
    assert any(
        isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == "load"
        for n in ast.walk(fn)
    )


def test_the_lane_has_its_own_health_key():
    """Never SAR's bare `live` — `main.py`'s probes read that one, and sharing
    it would let a stalled governor lane page as a SAR failure."""
    assert cf.lane() == f"{tm.MECH_GOVERNOR}:{arms.LANE_LIVE}"
    assert cf.lane() != arms.LANE_LIVE


def test_the_diag_entry_is_registered_and_assembled_in_the_engine():
    from src import diag_catalog

    keys = {e["key"]: e for e in diag_catalog.catalog()}
    assert "read.ai_governor_paired" in keys
    assert keys["read.ai_governor_paired"]["kind"] == "read"
    # Driven, not merely listed. A registered entry whose function raises is a
    # catalog row that renders and an answer nobody gets.
    out = diag_catalog.run("read.ai_governor_paired", None)
    assert out["ok"] is True, out.get("error")
    assert "agreement_violations" in out["result"]["paired"]


def test_one_arm_per_signal_on_the_declared_trigger_timeframe(_isolated):
    """A verdict is ONE thesis about one signal. Opening 5m and 15m arms would
    copy it onto two rows and count one recommendation twice."""
    from src.channels.base import Signal
    from src.historical_data import HistoricalDataStore
    from src.smc import Direction

    store = HistoricalDataStore()
    for interval in ("5m", "15m"):
        for i, (o, h, lo, c) in enumerate(_flat(80)):
            store.update_candle(
                "TESTUSDT", interval,
                {"open": o, "high": h, "low": lo, "close": c, "volume": 1.0,
                 "open_time": 1_700_000_000_000 + i * BAR_MS},
            )
    sig = Signal(
        channel="scalp", symbol="TESTUSDT", direction=Direction.LONG,
        entry=100.0, stop_loss=97.0, tp1=105.0, tp2=110.0,
        signal_id="SIG-TF", setup_class="MOVER_TREND_PULLBACK",
    )
    cf.observe_signal(sig, store, price=100.0, ledger=_isolated, now_ts=_now_at(79))
    opened = _isolated.open_arms()
    assert len(opened) == 1
    assert opened[0]["timeframe"] == "15m"      # the setup's DECLARED clock
    assert opened[0]["mechanism"] == tm.MECH_GOVERNOR


def test_an_undeclared_setup_is_refused_rather_than_defaulted_to_5m(_isolated):
    """`Scanner._get_primary_timeframe` returned the literal "5m" for every
    channel under a docstring claiming it was a lookup, and six money-path
    consumers read it. A hand-maintained map is a floor; the miss has to be a
    counted refusal."""
    from src.channels.base import Signal
    from src.smc import Direction

    sig = Signal(
        channel="scalp", symbol="TESTUSDT", direction=Direction.LONG,
        entry=100.0, stop_loss=97.0, tp1=105.0, tp2=110.0,
        signal_id="SIG-NOTF", setup_class="NOT_A_DECLARED_SETUP",
    )
    cf.observe_signal(sig, None, ledger=_isolated, now_ts=_now_at(79))
    assert _isolated.open_arms() == []


def test_there_is_no_dark_lane_and_the_payload_says_so(_isolated):
    """A rendered state, never an absent key: a missing lane reads as a broken
    deploy and this one is a decision. A diverted row has no position, so no
    verdict would ever arrive and every arm would sit on unedited geometry —
    a file of rows whose treatment and control are identical by construction."""
    assert not hasattr(cf, "DARK_PATH")
    assert not hasattr(cf, "get_dark_ledger")
    assert "dark_lane" in cf.build_diag()
