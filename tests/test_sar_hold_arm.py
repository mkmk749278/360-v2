"""The held-to-stop arm and the stop-management rules on the SAR live lane.

Two things are being tested and they are different. The **held arm** answers
"how much profit was on the table before the original stop caught this", which
``mfe_pct`` structurally cannot because the SAR loop stops advancing it at its
own exit (#869). The **rules** answer "what if the stop had moved once the trade
was up N%".

The load-bearing tests are the ones that would have caught the seam this change
was most likely to introduce: :func:`test_hold_arm_keeps_walking_after_sar_closes`
and :func:`test_sweep_does_not_retire_while_the_hold_arm_is_open`. A second arm
that freezes when the first finishes is #835's shape, and it is silent — the row
looks correctly complete.

Every series here is built from the module's own fixtures and every arm from
``live.new_arm``; nothing hand-writes a level or a state dict.
"""

from __future__ import annotations

import pytest

from src import sar_exit_strategies as strat
from src import sar_live_shadow as live
from src import trail_mechanisms

STEP, MAX_STEP = 0.02, 0.2
BAR_MS = 900_000.0


def _series(bars):
    return {
        "open": [b[0] for b in bars],
        "high": [b[1] for b in bars],
        "low": [b[2] for b in bars],
        "close": [b[3] for b in bars],
        "open_time": [1_700_000_000_000.0 + i * BAR_MS for i in range(len(bars))],
    }


def _rising(n, start=100.0, step_up=1.0):
    return [
        (start + i * step_up, start + i * step_up + 0.5, start + i * step_up - 0.5,
         start + i * step_up)
        for i in range(n)
    ]


def _live_of(bars, side="LONG"):
    """Anchor point from the real producer, never a hand-built shape."""
    s = _series(bars)
    return trail_mechanisms.point(
        trail_mechanisms.MECH_SAR,
        None,
        s["high"],
        s["low"],
        s["close"],
        len(s["high"]) - 1,
        side=side,
        state={},
        params={"step": STEP, "max_step": MAX_STEP},
    )


def _arm(bars, side, entry, sl, tp1, tf="15m"):
    s = _series(bars)
    return live.new_arm(
        signal_id="SIG-H",
        symbol="TESTUSDT",
        side=side,
        setup_class="MOVER_TREND_PULLBACK",
        timeframe=tf,
        entry=entry,
        stop_loss=sl,
        tp1=tp1,
        point=_live_of(bars, side),
        opened_ms=s["open_time"][-1],
        now_ts=1_700_000_000.0,
    )


def _now_at(bar_index: int) -> float:
    return (1_700_000_000_000.0 + bar_index * BAR_MS) / 1000.0 + BAR_MS / 1000.0


# The series that separates the two arms, verified bar-by-bar against the real
# ``parabolic_sar`` rather than assumed:
#
#   bars 0-59   rising; the arm opens on bar 59 at entry 160, SAR parked 155.5
#   bar  61     low 155.0 breaches it — the SAR ARM EXITS here, at a small loss
#   bars 62-70  price rallies to 186.5 — everything the SAR arm never saw
#   bar  72     low 138.0 takes out the ORIGINAL stop at 140 — the held arm exits
#
# So `mfe_pct` (truncated at bar 61) is ~0 while `hold_mfe_pct` is ~16.6%. A
# fixture where both arms exit on the same bar would let a frozen second arm
# pass every assertion here, which is exactly the seam being tested.
_FLIP = [(159.0, 159.5, 157.0, 157.5), (157.5, 158.0, 155.0, 155.5)]
_RALLY = [(155.5, 160.0, 155.0, 159.5)] + [
    (159.5 + i * 3, 163.0 + i * 3, 158.5 + i * 3, 162.5 + i * 3) for i in range(8)
]
_CRASH = [(186.0, 186.5, 150.0, 152.0), (152.0, 153.0, 138.0, 139.0)]


# --------------------------------------------------------------------------- #
# The arm exists and starts in a sane state
# --------------------------------------------------------------------------- #


def test_a_new_arm_opens_both_arms_and_every_rule():
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=155.0, tp1=170.0)
    assert arm["hold_status"] == live.HOLD_OPEN
    assert live.owed_verdict(arm) is True
    assert set(arm["strategies"]) == set(strat.CATALOG_ORDER)
    assert all(s["status"] == strat.ST_OPEN for s in arm["strategies"].values())


def test_a_schema_1_row_is_not_resurrected_as_open():
    """A row with no ``hold_status`` predates the arm and is owed nothing.

    Reading a missing field as "open" would drag every historical row back into
    the open set forever — and it would look like the lane suddenly had hundreds
    of live arms.
    """
    assert live.hold_arm_open({"status": live.STATUS_CLOSED_SL}) is False
    assert live.owed_verdict({"status": live.STATUS_CLOSED_SL}) is False


# --------------------------------------------------------------------------- #
# The seam: the held arm must outlive the SAR arm
# --------------------------------------------------------------------------- #


def test_hold_arm_keeps_walking_after_sar_closes():
    """The defect this change was most likely to ship, pinned.

    The SAR arm exits on its flip; the held arm runs to the ORIGINAL stop, which
    is normally later. A loop that returns at the SAR exit freezes the second
    arm at whatever it had — silently, because the row looks complete.
    """
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=140.0, tp1=999.0)
    all_bars = bars + _FLIP + _RALLY + _CRASH
    series = _series(all_bars)
    live.step_arm(arm, series, step=STEP, max_step=MAX_STEP, now_ts=_now_at(len(all_bars)))

    assert arm["status"] != live.STATUS_RUNNING, "SAR arm should have flipped out"
    assert arm["hold_status"] == live.HOLD_SL, "held arm must reach the original stop"
    assert arm["hold_bars"] > arm["bars_seen"], (
        "the held arm must have consumed more bars than the SAR arm — if these "
        "are equal the second arm froze at the first arm's exit"
    )


def test_hold_mfe_exceeds_the_truncated_mfe_when_the_trade_ran_on():
    """The whole point: the two peaks are different measurements.

    ``mfe_pct`` is bounded by the SAR exit by construction. ``hold_mfe_pct``
    keeps walking, so on a trade that kept running after the flip it must be
    strictly larger. If they are ever equal on such a row, the held arm is not
    walking and the column is the old truncated one wearing a new name.
    """
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=140.0, tp1=999.0)
    all_bars = bars + _FLIP + _RALLY + _CRASH
    live.step_arm(arm, _series(all_bars), step=STEP, max_step=MAX_STEP,
                  now_ts=_now_at(len(all_bars)))
    assert arm["hold_status"] == live.HOLD_SL
    # The SAR arm exited into a small loss and never saw the rally at all.
    assert arm["hold_mfe_pct"] > 15.0
    assert arm["hold_mfe_pct"] > arm["mfe_pct"]


def test_sweep_does_not_retire_while_the_hold_arm_is_open():
    """Retiring on the SAR close would freeze the held arm inside a resolved row."""
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=100.0, tp1=999.0)
    # SAR flips; the original stop at 100 is never reached, so the held arm is
    # still walking when the sweep decides whether to retire the row.
    all_bars = bars + _FLIP + _RALLY
    series = _series(all_bars)

    class _Store:
        def get_candles(self, symbol, tf):
            return series

    ledger = live.SarLiveLedger(path="")
    ledger.add(arm)
    tally = live.sweep(
        _Store(), ledger=ledger,
        warmup=10, now_ts=_now_at(len(all_bars)),
    )
    assert tally["retired"] == 0
    still = ledger.get(arm["arm_id"])
    assert still is not None, "the row must stay in the open set while an arm walks"
    assert still["status"] != live.STATUS_RUNNING, "…even though SAR has closed"
    assert still["hold_status"] == live.HOLD_OPEN


# --------------------------------------------------------------------------- #
# Conservatism — every judgement leans against the arm
# --------------------------------------------------------------------------- #


def test_peak_on_the_stop_bar_is_excluded_from_hold_mfe():
    """OHLC cannot order two touches inside one bar, so the peak does not count.

    It lands in ``hold_mfe_incl_pct`` instead, and the row is flagged — the
    assumption is readable rather than embedded.
    """
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=155.0, tp1=999.0)
    # One bar that both prints a big new high and takes out the stop.
    series = _series(bars + [(160.0, 200.0, 150.0, 152.0)])
    live.step_arm(arm, series, step=STEP, max_step=MAX_STEP, now_ts=_now_at(len(bars) + 1))
    assert arm["hold_status"] == live.HOLD_SL
    assert arm["hold_ambiguous_bar"] is True
    assert arm["hold_mfe_incl_pct"] > arm["hold_mfe_pct"]


def test_a_gap_through_the_stop_fills_at_the_open_never_better():
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=155.0, tp1=999.0)
    series = _series(bars + [(140.0, 141.0, 138.0, 139.0)])  # opens below the stop
    live.step_arm(arm, series, step=STEP, max_step=MAX_STEP, now_ts=_now_at(len(bars) + 1))
    assert arm["hold_fill"] == pytest.approx(140.0), "must fill at the open, not the stop"
    assert arm["hold_pnl_pct"] < 0


def test_mae_before_the_peak_is_recorded():
    """MFE and MAE carry no ordering between them; this supplies it."""
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=100.0, tp1=999.0)
    series = _series(bars + [(160.0, 161.0, 140.0, 158.0), (158.0, 200.0, 157.0, 199.0)])
    live.step_arm(arm, series, step=STEP, max_step=MAX_STEP, now_ts=_now_at(len(bars) + 2))
    assert arm["hold_mae_pre_peak_pct"] > 0
    assert arm["hold_peak_bar"] is not None


# --------------------------------------------------------------------------- #
# Terminal states are three, and the broken ones are unscored
# --------------------------------------------------------------------------- #


def test_a_broken_walk_terminates_the_hold_arm_unscored():
    """A series that jumped cannot be walked honestly by either arm."""
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=100.0, tp1=999.0)
    # 200 bars appear in one advance, against a clock that allows a handful.
    series = _series(bars + _rising(200, start=160.0))
    live.step_arm(arm, series, step=STEP, max_step=MAX_STEP, now_ts=1_700_000_000.0 + 900.0)
    assert arm["exit_reason"] == live.EXIT_SERIES_JUMPED
    assert arm["hold_status"] == live.HOLD_INSUFFICIENT
    assert arm["hold_pnl_pct"] is None, "an unwalkable window books no fill"


def test_a_stalled_feed_terminates_the_hold_arm_too():
    """Terminating the SAR arm alone would leave a frozen OPEN arm in a dead row."""
    arm = _arm(_rising(60), "LONG", entry=160.0, sl=100.0, tp1=999.0)
    arm["stalled_since"] = 1_700_000_000.0
    live._note_series_state(
        arm, now=1_700_000_000.0 + 10_000.0, latest_bar_ms=None,
        stall_reason=live.STALL_NO_SERIES, stall_bars=3, abandon_sec=60,
    )
    assert arm["status"] == live.STATUS_INSUFFICIENT
    assert arm["hold_status"] == live.HOLD_INSUFFICIENT


# --------------------------------------------------------------------------- #
# Stop-management rules
# --------------------------------------------------------------------------- #


def test_a_rule_that_never_arms_scores_exactly_the_baseline():
    """The property that makes "would have removed" readable at all.

    A rule whose trigger is never reached is an ordinary trade on the original
    stop. If it scored anything else, every comparison against the baseline
    would be measuring the harness rather than the rule.
    """
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=155.0, tp1=999.0)
    series = _series(bars + [(160.0, 160.2, 150.0, 151.0)])  # straight to the stop
    live.step_arm(arm, series, step=STEP, max_step=MAX_STEP, now_ts=_now_at(len(bars) + 1))
    for key, st in arm["strategies"].items():
        assert st["armed"] is False, key
        assert st["status"] == strat.ST_ORIGINAL_SL, key
        assert st["pnl_pct"] == pytest.approx(arm["hold_pnl_pct"]), key


def test_a_breakeven_rule_turns_a_loser_into_roughly_flat():
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=100.0, sl=95.0, tp1=999.0)
    series = _series(
        bars
        + [(100.0, 104.0, 99.5, 103.0)]      # +4% — arms be_1/be_2/be_3
        + [(103.0, 103.5, 94.0, 94.5)]       # collapses through entry and the stop
    )
    live.step_arm(arm, series, step=STEP, max_step=MAX_STEP, now_ts=_now_at(len(bars) + 2))
    be = arm["strategies"]["be_3"]
    assert be["armed"] is True
    assert be["status"] == strat.ST_RULE_STOP
    assert be["pnl_pct"] == pytest.approx(0.0, abs=1e-9), "BE means out at entry"
    assert arm["hold_pnl_pct"] < -4, "…while the unmanaged arm took the full stop"


def test_a_rule_is_armed_by_a_bar_and_only_protects_the_NEXT_one():
    """The single biggest way this measurement could read better than reality.

    A bar that both reaches +3% and collapses through entry must NOT be rescued
    by a rule armed on that same bar: OHLC cannot say which came first, and
    arming mid-bar lets every rule harvest moves it might never have caught.
    """
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=100.0, sl=95.0, tp1=999.0)
    # One bar: high +4%, low through the original stop.
    series = _series(bars + [(100.0, 104.0, 94.0, 94.5)])
    live.step_arm(arm, series, step=STEP, max_step=MAX_STEP, now_ts=_now_at(len(bars) + 1))
    be = arm["strategies"]["be_3"]
    assert be["status"] == strat.ST_ORIGINAL_SL, (
        "a rule armed by this bar must not protect this bar"
    )
    assert be["pnl_pct"] < -4


def test_a_trailing_rule_ratchets_and_never_widens():
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=100.0, sl=95.0, tp1=999.0)
    series = _series(
        bars
        + [(100.0, 106.0, 99.5, 105.0)]   # +6%, arms trail2_3 → stop to +4%
        + [(105.0, 110.0, 104.5, 109.0)]  # +10%, stop ratchets to +8%
        + [(109.0, 109.5, 100.0, 101.0)]  # gives back — must stop at +8%
    )
    live.step_arm(arm, series, step=STEP, max_step=MAX_STEP, now_ts=_now_at(len(bars) + 3))
    tr = arm["strategies"]["trail2_3"]
    assert tr["status"] == strat.ST_RULE_STOP
    assert tr["pnl_pct"] == pytest.approx(8.0, abs=0.01)


def test_the_catalog_manifest_ships_with_the_rules_it_describes():
    """Ops renders this rather than keeping a second catalog.

    A mirrored rule list is how ``MEASUREMENT_SUFFIXES`` drifted for a week.
    """
    manifest = strat.catalog_manifest()
    assert [m["key"] for m in manifest] == list(strat.CATALOG_ORDER)
    assert all(m["label"] and m["kind"] for m in manifest)


def test_summarize_covers_every_rule_in_the_catalog():
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=155.0, tp1=999.0)
    out = strat.summarize(arm["strategies"])
    assert list(out) == list(strat.CATALOG_ORDER)
