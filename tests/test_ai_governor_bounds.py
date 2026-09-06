"""The bounds. These are the tests that would have caught the real incidents.

Session 137, in one sentence: the orphan sweep's budget was named for what it
DOES (cancel) and only decremented on that branch; production takes the other
branch, so it spent nothing, ran unbounded, got the box rate-limited off
Binance and took auto-trade down for every paid user for roughly four hours.
Its test covered the cancel path only, so it passed against code that was
unbounded in the case that actually runs.

So: a bound needs a test on the path that does NOT do the work, and a per-user
path needs a test that COUNTS at the target member number rather than at the
one member a developer has.
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

import pytest

from src import ai_governor_ledger
from src.execution import ai_governor as gov
from src.execution import ai_governor_menu as menu
from src.execution import ai_governor_snapshot as snap

from tests.test_ai_governor import FakePosition, FakeSignal, _series


@pytest.fixture(autouse=True)
def _isolate():
    gov.reset_state_for_test()
    gov.reset_health_for_test()
    ai_governor_ledger.reset_ledger(ai_governor_ledger.GovernorLedger(path=""))
    yield
    gov.reset_state_for_test()
    gov.reset_health_for_test()
    ai_governor_ledger.reset_ledger(None)


class _Store:
    """Stands in for the candle store, returning the real series shape."""

    def __init__(self, series: Optional[Dict[str, Any]] = None) -> None:
        self._series = series if series is not None else _series()

    def get_candles(self, symbol: str, timeframe: str):
        return self._series


def _menu_and_snapshot(signal_id: str = "sig-1"):
    s = _series()
    m = menu.build_menu(
        side="LONG", entry=100.0, current_sl=98.0, current_tp1=104.0,
        highs=s["high"], lows=s["low"], closes=s["close"], last_price=101.0,
    )
    sig = FakeSignal(signal_id=signal_id)
    sn = snap.with_menu(
        snap.build_snapshot(
            signal=sig, trigger_tf="15m", as_of_bar_ms=1, bars_since_entry=2,
            last_price=101.0, menu=m,
        ),
        m,
    )
    return m, sn


def _verdict(action: str, choice: Optional[str], signal_id: str = "sig-1",
             issued_at: float = 1000.0,
             queued_at: Optional[float] = None) -> gov.Verdict:
    return gov.Verdict(
        signal_id=signal_id, action=action, choice=choice, confidence=0.8,
        rationale="test", premise_broken=(), served_model="gemini-3.7-flash-002",
        requested_model="gemini-3.7-flash", prompt_schema=gov.PROMPT_SCHEMA,
        snapshot_digest="abc", as_of_bar_ms=1, issued_at=issued_at,
        latency_ms=100, usage={}, cost_usd=0.0, queued_at=queued_at,
    )


# ── The budget bounds the branch that does NOTHING ──────────────────────────

async def test_the_call_guard_runs_before_any_per_signal_work(monkeypatch):
    """An arm with no calls left must cost a dict lookup and nothing else.

    Session 137's rule: the do-nothing branch is the one production takes, so
    it is the one that has to be cheap. If the guard ran after the menu was
    built, an exhausted arm would still burn swing detection on every tick of
    every open signal, forever.
    """
    built: List[str] = []

    def _spy(sig, series, price):
        built.append(sig.signal_id)
        return _menu_and_snapshot()[0]

    monkeypatch.setattr(gov, "_build_menu_for", _spy)
    monkeypatch.setattr(gov, "_trigger_tf_for", lambda sig: "15m")

    sig = FakeSignal()
    gov.observe_signal(sig, trigger_tf="15m", now=0.0)
    with gov._arms_lock:
        gov._arms["sig-1"].calls_made = 999  # budget spent

    await (gov.sweep({"sig-1": sig}, _Store(), price_fn=lambda s: 101.0))

    assert built == [], "menu was built for an arm with no budget left"
    assert gov.health()["refusals"][gov.REFUSE_BUDGET_CALLS] == 1


async def test_no_new_bar_is_not_counted_as_a_refusal(monkeypatch):
    """Between bar closes there is genuinely nothing to decide. Counting that
    as a failure is how a real one stops standing out."""
    monkeypatch.setattr(gov, "_trigger_tf_for", lambda sig: "15m")
    sig = FakeSignal()
    store = _Store()
    await (gov.sweep({"sig-1": sig}, store, price_fn=lambda s: 101.0,
                          task_factory=lambda coro: coro.close()))
    res = await (gov.sweep({"sig-1": sig}, store, price_fn=lambda s: 101.0,
                                task_factory=lambda coro: coro.close()))
    assert res["outcomes"].get(gov.REFUSE_NO_BAR) == 1
    assert gov.REFUSE_NO_BAR not in gov.health()["refusals"]


async def test_an_unknown_trigger_timeframe_is_refused_never_defaulted(monkeypatch):
    """`_get_primary_timeframe` returned the literal "5m" for every channel
    under a docstring claiming it was a lookup, and six money-path consumers
    read it. A hand-maintained map is a floor; the miss has to be counted."""
    monkeypatch.setattr(gov, "_trigger_tf_for", lambda sig: "")
    res = await (gov.sweep({"sig-1": FakeSignal()}, _Store(),
                                price_fn=lambda s: 101.0))
    assert res["outcomes"][gov.REFUSE_TF_UNKNOWN] == 1
    assert gov.health()["refusals"][gov.REFUSE_TF_UNKNOWN] == 1


# ── MAINTAIN costs nothing, at any member count ─────────────────────────────

async def test_maintain_touches_no_position_and_no_exchange(monkeypatch):
    """MAINTAIN is most of every window. Any per-user work on it is pure waste
    multiplied by the member count (§2.2)."""
    reads: List[str] = []
    monkeypatch.setattr(
        gov, "_open_positions_for",
        lambda sid: (reads.append(sid), [])[1],
    )
    m, sn = _menu_and_snapshot()
    out = await (gov.apply_verdict(_verdict(gov.MAINTAIN, None), sn, m, now=1000.0))
    assert out == gov.MAINTAIN
    assert reads == [], "MAINTAIN read the position index"


# ── The apply path is bounded AT THE TARGET MEMBER COUNT ────────────────────

async def test_panic_refuses_outright_while_its_ceiling_is_unset(monkeypatch):
    """An owner-set blast-radius cap that falls back to unbounded is not a cap.

    This is the one arm that cannot be paced, so the absence of a number must
    not read as permission.
    """
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    monkeypatch.setattr(gov, "armed_arms", lambda: ("tp", "sl", "panic"))
    monkeypatch.setattr(
        gov, "_open_positions_for",
        lambda sid: [FakePosition(firebase_uid=f"u{i}") for i in range(1000)],
    )
    closed: List[Any] = []

    m, sn = _menu_and_snapshot()
    out = await (gov.apply_verdict(_verdict(gov.PANIC_CLOSE, None), sn, m, now=1000.0))
    assert out == gov.REFUSE_PANIC_CEILING_UNSET
    assert closed == []
    assert gov.health()["refusals"][gov.REFUSE_PANIC_CEILING_UNSET] == 1


async def test_panic_over_its_ceiling_is_refused_not_truncated(monkeypatch):
    """Closing an arbitrary subset of a correlated book is a DIFFERENT action
    from the one that was asked for, and picking the subset by iteration order
    is order-dependent by construction."""
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    monkeypatch.setattr(gov, "armed_arms", lambda: ("panic",))
    monkeypatch.setattr(
        gov, "_open_positions_for",
        lambda sid: [FakePosition(firebase_uid=f"u{i}") for i in range(1000)],
    )
    import config
    monkeypatch.setattr(config, "AI_GOV_PANIC_MAX_POSITIONS", 50, raising=False)

    m, sn = _menu_and_snapshot()
    out = await (gov.apply_verdict(_verdict(gov.PANIC_CLOSE, None), sn, m, now=1000.0))
    assert out == gov.REFUSE_PANIC_CEILING_HIT
    assert gov.health()["refusals"][gov.REFUSE_PANIC_CEILING_HIT] == 1


async def test_a_level_move_at_1000_members_is_paced_not_burst(monkeypatch):
    """One ADJUST_TP at the member target is ~2,000 signed Binance calls in a
    burst, from an IP that has been rate-limited before. The pacing bound is
    what stops that being the 2026-09-01 shape again.

    Asserting a COUNT is the point: reading the loop tells you nothing, and at
    the one member a developer has, unbounded and bounded look identical.
    """
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    monkeypatch.setattr(gov, "armed_arms", lambda: ("tp",))
    positions = [FakePosition(firebase_uid=f"u{i}") for i in range(1000)]
    monkeypatch.setattr(gov, "_open_positions_for", lambda sid: positions)

    touched: List[str] = []

    async def _never_called(position, price, placer):
        touched.append(position.firebase_uid)
        return True

    monkeypatch.setattr(gov, "_move_tp", _never_called)
    import config
    monkeypatch.setattr(config, "AI_GOV_APPLY_MAX_POS_PER_MIN", 60, raising=False)

    m, sn = _menu_and_snapshot()
    choice = next(c.key for c in m.tp if c.key != "tp_0")
    out = await (gov.apply_verdict(_verdict(gov.ADJUST_TP, choice), sn, m, now=1000.0))

    assert out == gov.REFUSE_APPLY_PACED
    assert touched == [], "1000 positions were touched inside a 60/min budget"
    assert gov.health()["refusals"][gov.REFUSE_APPLY_PACED] == 1


async def test_the_sl_arm_never_fights_the_trail_governor(monkeypatch):
    """Two modules must never move one stop. `trail_governor` owns the stop of
    any position carrying an exit mechanism."""
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    monkeypatch.setattr(gov, "armed_arms", lambda: ("sl",))
    monkeypatch.setattr(
        gov, "_open_positions_for",
        lambda sid: [FakePosition(exit_mechanism="sar")],
    )
    moved: List[Any] = []

    async def _spy(position, price, placer):
        moved.append(position)
        return True

    monkeypatch.setattr(gov, "_move_sl", _spy)
    m, sn = _menu_and_snapshot()
    choice = next((c.key for c in m.sl if c.key != "sl_0"), None)
    assert choice is not None
    out = await (gov.apply_verdict(_verdict(gov.ADJUST_SL, choice), sn, m, now=1000.0))
    assert out == gov.REFUSE_TRAIL_GOVERNED
    assert moved == []


async def test_a_stale_verdict_is_refused_never_applied(monkeypatch):
    """The requester stopped waiting. Applying a minutes-old exit decision from
    a world that has moved on is worse than doing nothing."""
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    m, sn = _menu_and_snapshot()
    out = await (
        gov.apply_verdict(_verdict(gov.PANIC_CLOSE, None, issued_at=0.0), sn, m, now=10_000.0)
    )
    assert out == gov.REFUSE_STALE_VERDICT


async def test_apply_off_is_a_named_refusal_and_the_verdict_is_still_recorded():
    """Dark means the measurement runs and the effect does not. A verdict that
    was refused must be visible as refused, not absent."""
    m, sn = _menu_and_snapshot()
    out = await (gov.apply_verdict(_verdict(gov.PANIC_CLOSE, None), sn, m, now=1000.0))
    assert out == gov.REFUSE_APPLY_OFF
    assert gov.health()["refusals"][gov.REFUSE_APPLY_OFF] == 1


async def test_a_paced_verdict_waits_for_the_next_tick_instead_of_live_locking(monkeypatch):
    """`_requeue` puts a paced verdict back on the queue the drain is reading.

    An unbounded `while _queue` would pop it, find the pacing budget unchanged
    within the same instant, requeue it, and pop it again — a live-lock inside
    the monitor tick, on the loop that owns SL/TP monitoring for every open
    position. The drain is bounded by the depth at ENTRY, so a requeued verdict
    is next tick's work.

    This test hangs forever against the pre-fix drain, which is how it was
    found.
    """
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    monkeypatch.setattr(gov, "armed_arms", lambda: ("tp",))
    monkeypatch.setattr(
        gov, "_open_positions_for",
        lambda sid: [FakePosition(firebase_uid=f"u{i}") for i in range(500)],
    )
    import config
    monkeypatch.setattr(config, "AI_GOV_APPLY_MAX_POS_PER_MIN", 10, raising=False)

    m, sn = _menu_and_snapshot()
    choice = next(c.key for c in m.tp if c.key != "tp_0")
    with gov._queue_lock:
        gov._queue.append((_verdict(gov.ADJUST_TP, choice), sn, m))

    async def _run():
        return await asyncio.wait_for(gov.drain_verdicts(now=1000.0), timeout=5.0)

    handled = await (_run())
    assert handled == 1, "the drain processed the requeued verdict in the same tick"
    with gov._queue_lock:
        assert len(gov._queue) == 1, "the paced verdict should be waiting, not dropped"


async def test_a_cooldown_is_a_throttle_not_a_refusal(monkeypatch):
    """`cooldown` means the lane found an arm it was willing to evaluate and
    deliberately did not — positive evidence it is working.

    Bucketed with the refusals it reads as the governor being blocked when it
    was us throttling, which is the mistake #816 cost a session over, arriving
    from the display side.
    """
    monkeypatch.setattr(gov, "_trigger_tf_for", lambda sig: "15m")
    sig = FakeSignal()
    gov.observe_signal(sig, trigger_tf="15m", now=1000.0)
    with gov._arms_lock:
        gov._arms["sig-1"].last_call_at = 1000.0  # just called

    await (gov.sweep({"sig-1": sig}, _Store(), price_fn=lambda s: 101.0,
                          now_ts=1001.0))

    h = gov.health()
    assert h["throttles"][gov.THROTTLE_COOLDOWN] == 1
    assert gov.THROTTLE_COOLDOWN not in h["refusals"]


# ── A counter is not a cause: how LATE, not just that it was late ───────────
#
# The first live window refused 6 of 6 `ADJUST_SL` verdicts as `stale_verdict`
# and no surface could say by how much. One second and ninety seconds are the
# same integer there and have opposite fixes — widen the bound, or fix the
# drain cadence — so the counter alone cannot decide anything. This is
# `trail_governor.place_failed` arriving one lane over, and these tests pin the
# instrument rather than the fix, because the fix needs evidence this produces.


async def test_a_stale_refusal_records_how_late_it_was(monkeypatch):
    """The refusal must carry its age, or nobody can tell which fix it needs."""
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    m, sn = _menu_and_snapshot()
    out = await (
        gov.apply_verdict(_verdict(gov.PANIC_CLOSE, None, issued_at=0.0), sn, m, now=10_000.0)
    )
    assert out == gov.REFUSE_STALE_VERDICT

    age = gov.health()["verdict_age"]
    assert age["n"] == 1
    assert age["stale_n"] == 1
    assert age["max_sec"] == pytest.approx(10_000.0)
    assert age["samples"][-1]["action"] == gov.PANIC_CLOSE
    assert age["samples"][-1]["stale"] is True


async def test_maintain_is_measured_too_so_the_stale_rate_has_a_denominator():
    """MAINTAIN returns BEFORE the staleness check, so the refusal is only ever
    observable on the arms that would have acted.

    Measured only there, "6 of 6 stale" is a fact about those six and says
    nothing about the lane's clock. The age is therefore taken for every
    action, and a late MAINTAIN is still counted late — while still being
    applied, because nothing about its behaviour changes.
    """
    m, sn = _menu_and_snapshot()
    out = await (
        gov.apply_verdict(_verdict(gov.MAINTAIN, None, issued_at=0.0), sn, m, now=10_000.0)
    )
    assert out == gov.MAINTAIN, "behaviour is unchanged: MAINTAIN still applies"

    age = gov.health()["verdict_age"]
    assert age["n"] == 1, "a MAINTAIN verdict is in the denominator"
    assert age["stale_n"] == 1, "and it is counted as late when it is late"


async def test_the_age_ring_is_bounded_and_the_count_beside_it_is_not():
    """The newest few must never read as the whole population."""
    m, sn = _menu_and_snapshot()
    for i in range(gov._VERDICT_AGE_RING + 10):
        await (
            gov.apply_verdict(
                _verdict(gov.MAINTAIN, None, issued_at=float(i)), sn, m, now=float(i) + 1.0
            )
        )

    age = gov.health()["verdict_age"]
    assert len(age["samples"]) == gov._VERDICT_AGE_RING
    assert age["n"] == gov._VERDICT_AGE_RING + 10
    assert age["stale_n"] == 0, "one second is not stale against a ten-second bound"


def test_the_bound_is_published_beside_the_age():
    """A duration with no threshold beside it cannot be read.

    The page must not re-derive `AI_GOV_VERDICT_MAX_AGE_SEC` from its own copy
    of the config — the drifting-mirror defect this repo has paid for under
    several names.
    """
    from config import AI_GOV_VERDICT_MAX_AGE_SEC

    diag = gov.build_diag()
    assert diag["bounds"]["verdict_max_age_sec"] == pytest.approx(
        float(AI_GOV_VERDICT_MAX_AGE_SEC)
    )
    assert "verdict_age" in diag["health"]


# ── The age has two halves with opposite fixes ──────────────────────────────
#
# Measured live 2026-09-06 through a guest session, on the instrument the
# previous session shipped: 139 verdicts, **58 aged out (41.7%)**, oldest
# 26.2s, against a bound of 10.0s — and of the 20-row ring, the FASTEST
# verdict was 7.3s and the median 9.85s. Nothing can arrive sooner than the
# model's round trip plus one sweep interval, so a 10s bound sits at the
# median of its own pipeline and refuses whichever half jitter puts on the far
# side. These tests pin the two halves and the floor; the bound itself is the
# owner's number and is deliberately not changed here.


async def test_the_age_is_split_into_model_and_queue_wait():
    """One integer cannot say which wait spent the budget, and they differ.

    A slow model is fixed by a faster model, a smaller batch or a longer
    bound; a slow drain is fixed by the sweep cadence and no model change
    touches it. `place_failed` one lane over: a counter is not a cause.
    """
    m, sn = _menu_and_snapshot()
    # Launched at t=0, model answered at t=4.4, drained at t=9.6.
    await gov.apply_verdict(
        _verdict(gov.MAINTAIN, None, issued_at=0.0, queued_at=4.4), sn, m, now=9.6
    )

    age = gov.health()["verdict_age"]
    sample = age["samples"][-1]
    assert sample["age_sec"] == pytest.approx(9.6)
    assert sample["model_sec"] == pytest.approx(4.4), "the round trip"
    assert sample["queue_wait_sec"] == pytest.approx(5.2), "waiting for the next sweep"
    assert sample["model_sec"] + sample["queue_wait_sec"] == pytest.approx(
        sample["age_sec"]
    ), "the halves must account for the whole, or one of them is being hidden"
    assert age["split_n"] == 1
    assert age.get("split_missing_n", 0) == 0, "this row carried both stamps"


async def test_a_verdict_written_before_the_stamp_is_counted_apart_not_imputed():
    """A missing stamp is not a zero.

    Imputing `queued_at = issued_at` would put the entire age on the queue and
    point the fix at the drain cadence for every pre-split row in the ledger —
    the flattering direction for the model and the wrong one for the reader.
    """
    m, sn = _menu_and_snapshot()
    await gov.apply_verdict(
        _verdict(gov.MAINTAIN, None, issued_at=0.0, queued_at=None), sn, m, now=9.6
    )

    age = gov.health()["verdict_age"]
    sample = age["samples"][-1]
    assert sample["age_sec"] == pytest.approx(9.6), "the pooled age still records"
    assert "model_sec" not in sample and "queue_wait_sec" not in sample
    assert age["split_missing_n"] == 1
    assert age.get("split_n", 0) == 0, "it must not enter the split's denominator"


# ── The floor: what the pipeline can achieve, against what the bound allows ──


def test_the_floor_is_unmeasurable_until_both_terms_exist():
    """"Not enough samples" is not "the floor is zero".

    Rendering an unmeasured floor as a clean one is the flattering direction of
    the same error, and it would make the bound look like it had headroom it
    has never been shown to have.
    """
    floor = gov.verdict_age_floor()
    assert floor["measurable"] is False
    assert floor["reason"] == "no_split_samples"
    assert "floor_sec" not in floor, "no number is offered where none was measured"


async def test_a_bound_at_or_below_the_floor_is_named_as_such():
    """The defect this whole change exists to make visible.

    `issued_at` is stamped at the tick that launches the request, the model
    answers seconds later, and `drain_verdicts` runs once per sweep — so the
    floor is the round trip plus one sweep interval and no verdict can be
    younger. Nothing computed it, so a bound underneath it could not be
    checked against anything. This is `_HEARTBEAT_MAX_AGE_SECONDS` — a comment
    asserting the bound exceeds a worst-case cycle over a value that did not —
    arriving at the governor.
    """
    m, sn = _menu_and_snapshot()
    # Two sweeps, five seconds apart: the achieved cadence.
    gov._record_sweep_period(100.0)
    gov._record_sweep_period(105.0)
    # A verdict whose round trip alone was 6s.
    await gov.apply_verdict(
        _verdict(gov.MAINTAIN, None, issued_at=0.0, queued_at=6.0), sn, m, now=11.0
    )

    floor = gov.verdict_age_floor()
    assert floor["measurable"] is True
    assert floor["model_mean_sec"] == pytest.approx(6.0)
    assert floor["sweep_p50_sec"] == pytest.approx(5.0)
    assert floor["floor_sec"] == pytest.approx(11.0), "6s round trip + one 5s sweep"
    assert floor["bound_sec"] == pytest.approx(10.0)
    assert floor["bound_below_floor"] is True, (
        "a 10s bound against an 11s floor can never pass — that is not a "
        "staleness rule, it is a rename of 'always refuse'"
    )
    assert floor["headroom_sec"] == pytest.approx(-1.0)


def test_the_floor_is_published_where_the_bound_is_read():
    """A threshold with no floor beside it is the second half of the defect.

    The first was a duration with no threshold. Both have to be on the page or
    the reader cannot tell a lane that is late from a bound that is impossible.
    """
    gov._record_sweep_period(100.0)
    gov._record_sweep_period(105.0)
    diag = gov.build_diag()
    assert "verdict_age_floor" in diag
    assert diag["verdict_age_floor"]["bound_sec"] == diag["bounds"][
        "verdict_max_age_sec"
    ], "one writer, one reader — the page must not carry a second copy"


# ── The achieved cadence, not the one the loop asks for ─────────────────────


def test_the_sweep_period_is_measured_and_nonsense_is_refused_not_clamped():
    """`MONITOR_POLL_INTERVAL` is a sleep, not a period.

    The same cycle carries the signal fan-out, four measurement lanes and the
    trail governor. And a clock that went backwards is not a period: clamping
    it would quietly drag the floor toward whatever the outlier was, which is
    the clamp-is-not-a-guard rule at a measurement.
    """
    for t in (0.0, 5.0, 10.2, 15.0):
        gov._record_sweep_period(t)
    period = gov.health()["sweep_period"]
    assert period["n"] == 3
    assert period["p50_sec"] == pytest.approx(5.0)
    assert period["max_sec"] == pytest.approx(5.2)

    gov._record_sweep_period(14.0)      # backwards
    gov._record_sweep_period(9_000.0)   # a restart, not a period
    assert gov.health()["sweep_period"]["n"] == 3, "both refused, neither clamped"
