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
             issued_at: float = 1000.0) -> gov.Verdict:
    return gov.Verdict(
        signal_id=signal_id, action=action, choice=choice, confidence=0.8,
        rationale="test", premise_broken=(), served_model="gemini-3.7-flash-002",
        requested_model="gemini-3.7-flash", prompt_schema=gov.PROMPT_SCHEMA,
        snapshot_digest="abc", as_of_bar_ms=1, issued_at=issued_at,
        latency_ms=100, usage={}, cost_usd=0.0,
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


# ── The staleness bound is DERIVED from the tick, never invented ────────────
#
# `AI_GOV_VERDICT_MAX_AGE_SEC`'s own comment read "a verdict older than one
# monitor tick is refused" and the value was 10.0 against a monitor tick
# measured live at 7-20s. So the constant asserted a property it did not have,
# and 7 of 8 verdicts aged out by construction rather than by lateness — with
# both `ADJUST_SL` verdicts in the window discarded. The tenth recurrence in
# these repos of a constant checkable in one command that nobody ran.


def test_the_bound_is_the_floor_until_a_tick_has_been_observed():
    """One sweep is not an interval. An engine that has not swept twice reports
    the configured floor rather than a number it has not measured."""
    from config import AI_GOV_VERDICT_MAX_AGE_SEC

    assert gov.observed_tick_sec() is None
    assert gov.effective_verdict_max_age() == pytest.approx(float(AI_GOV_VERDICT_MAX_AGE_SEC))

    gov._record_sweep_tick(1000.0)
    assert gov.observed_tick_sec() is None, "the first sweep has no predecessor"


def test_the_bound_follows_the_SLOWEST_recent_tick_not_the_mean():
    """A verdict is drained one tick after it is issued, so the worst tick is
    the one that decides whether it survives. A mean would pass the common case
    and refuse exactly the slow cycles the bound exists for."""
    for t in (1000.0, 1005.0, 1010.0, 1030.0, 1035.0):   # 5,5,20,5
        gov._record_sweep_tick(t)
    assert gov.observed_tick_sec() == pytest.approx(20.0)
    # 20 * 1.5 = 30, above the 10s floor and below the 60s cap
    assert gov.effective_verdict_max_age() == pytest.approx(30.0)


def test_the_cap_stops_a_pathological_loop_widening_the_bound_without_limit():
    """A bound that follows a bad tick upward for ever is not a bound."""
    gov._record_sweep_tick(0.0)
    gov._record_sweep_tick(200.0)     # 200s tick — real, not an outage
    assert gov.effective_verdict_max_age() == pytest.approx(60.0)


def test_an_outage_is_not_a_tick_and_is_counted_rather_than_used():
    """A restart or a paused loop must not widen the staleness bound for
    minutes afterwards on the strength of an outage."""
    gov._record_sweep_tick(0.0)
    gov._record_sweep_tick(10_000.0)  # way past the outlier ceiling
    assert gov.observed_tick_sec() is None, "the outage never entered the ring"
    assert gov.health()["tick"]["outlier"] == 1


async def test_a_verdict_inside_the_DERIVED_bound_is_no_longer_refused(monkeypatch):
    """The fix, stated as behaviour: at a 20s tick a 15s-old verdict is one tick
    old and must survive. Against the pre-fix 10s constant it was refused."""
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    monkeypatch.setattr(gov, "armed_arms", lambda: ("sl",))
    monkeypatch.setattr(gov, "_open_positions_for", lambda sid: [])
    for t in (0.0, 20.0):
        gov._record_sweep_tick(t)

    m, sn = _menu_and_snapshot()
    choice = next(c.key for c in m.sl if c.key != "sl_0")
    out = await (
        gov.apply_verdict(_verdict(gov.ADJUST_SL, choice, issued_at=100.0), sn, m, now=115.0)
    )
    assert out != gov.REFUSE_STALE_VERDICT
    assert gov.health()["verdict_age"]["stale_n"] == 0


async def test_a_verdict_past_the_derived_bound_is_still_refused(monkeypatch):
    """Widening is not disabling. The stale-envelope rule still protects the
    money path — it is now measured against the loop rather than a guess."""
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    for t in (0.0, 20.0):
        gov._record_sweep_tick(t)

    m, sn = _menu_and_snapshot()
    out = await (
        gov.apply_verdict(_verdict(gov.PANIC_CLOSE, None, issued_at=0.0), sn, m, now=1000.0)
    )
    assert out == gov.REFUSE_STALE_VERDICT


def test_no_arm_is_armed_by_default():
    """`ADJUST_TP` may move a target NEARER only, and on ops' MFE-aware
    simulator over 562 closed signals no cap beats doing nothing: the engine's
    real exits average +0.29% against -0.46% at a +2% cap and +0.14% at +5%.

    Decidable is not the same property as safe to arm first, and the default
    now takes no position on arming at all — which is an owner decision.
    """
    import config
    assert config.AI_GOV_ARMS_ENABLED == ""
    assert gov.armed_arms() == ()


def test_both_bounds_are_published_so_a_reader_knows_which_one_binds():
    diag = gov.build_diag()
    b = diag["bounds"]
    assert "verdict_max_age_sec" in b, "the configured floor"
    assert "verdict_max_age_effective_sec" in b, "and what is actually enforced"
    assert b["observed_tick_sec"] is None, "not measured yet is not zero"
