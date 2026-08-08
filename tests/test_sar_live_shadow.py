"""Tests for the live SAR exit mechanism (``src/sar_live_shadow.py``).

Every expected SAR level here is produced by driving the **real**
``parabolic_sar_live`` / ``parabolic_sar_levels``, never by a hand-written
constant. A number this suite invents would only assert the author's assumption
back at itself — which is how #798's mocked ``exit_reason`` key went green over
dead code for weeks.
"""
from __future__ import annotations

import pytest

from src import sar_live_shadow as live
from src.sar_exit_shadow import parabolic_sar_levels, parabolic_sar_live

STEP = 0.02
MAX_STEP = 0.2
BAR_MS = 900_000.0  # 15m


def _now_at(bar_index: int, width_sec: float = BAR_MS / 1000.0) -> float:
    """Wall-clock at which bar ``bar_index`` is the newest CLOSED bar.

    The seeded fixtures stamp bars in 2023, so a sweep run against the real clock
    would call every arm stalled by several hundred thousand bars. Tests that
    care about staleness set ``now_ts`` explicitly — which is the point: the arm's
    freshness is a comparison between its newest bar and the clock, and a test
    that cannot move the clock cannot test it.
    """
    return (1_700_000_000_000.0 + bar_index * BAR_MS) / 1000.0 + width_sec


def _series(bars):
    """Build the module's own internal series shape from (o, h, l, c) tuples."""
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


def _falling(n, start=200.0, step_dn=1.0):
    return [
        (start - i * step_dn, start - i * step_dn + 0.5, start - i * step_dn - 0.5,
         start - i * step_dn)
        for i in range(n)
    ]


def _live_of(bars):
    s = _series(bars)
    return parabolic_sar_live(
        s["high"], s["low"], STEP, MAX_STEP, last_closed_ms=s["open_time"][-1]
    )


# --------------------------------------------------------------------------- #
# parabolic_sar_live — the closed-bar vs current-bar boundary
# --------------------------------------------------------------------------- #


def test_refactor_left_the_pinned_series_untouched():
    """_sar_walk is now shared; parabolic_sar_levels must be bit-identical."""
    bars = _rising(40) + _falling(20)
    s = _series(bars)
    published, in_force = parabolic_sar_levels(s["high"], s["low"], STEP, MAX_STEP)
    assert len(published) == len(bars)
    assert any(v is not None for v in in_force)
    # in_force is populated from index 2, published from index 1 — the shape the
    # replay arms and the app's chart study are pinned against.
    assert published[0] is None and in_force[0] is None and in_force[1] is None
    assert published[1] is not None


def test_next_stop_is_past_the_end_not_the_last_closed_bar():
    """The live stop is a projection, not in_force[-1].

    This is the whole closed-bar != current-bar rule. Parking in_force[-1] would
    put the stop one bar in the past — adjacent to the right answer, and on the
    far side of price across a flip.
    """
    bars = _rising(60)
    s = _series(bars)
    _pub, in_force = parabolic_sar_levels(s["high"], s["low"], STEP, MAX_STEP)
    got = _live_of(bars)
    assert got is not None
    assert got.next_stop != in_force[-1]
    # Trend is up, SAR trails below price and ratchets upward only.
    assert got.up is True
    assert got.next_stop > in_force[-1]


def test_live_refuses_rather_than_clamping_on_short_or_mismatched_input():
    assert parabolic_sar_live([1.0, 2.0], [0.5, 1.5], STEP, MAX_STEP) is None
    assert parabolic_sar_live([1.0, 2.0, 3.0], [0.5, 1.5], STEP, MAX_STEP) is None


def test_live_carries_the_bar_time_it_was_computed_from():
    bars = _rising(60)
    got = _live_of(bars)
    assert got.last_closed_ms == _series(bars)["open_time"][-1]


# --------------------------------------------------------------------------- #
# new_arm — the governor decision, stamped where it becomes true
# --------------------------------------------------------------------------- #


def _arm(bars, side, entry, sl, tp1, tf="15m"):
    s = _series(bars)
    return live.new_arm(
        signal_id="SIG-1",
        symbol="TESTUSDT",
        side=side,
        setup_class="MOVER_TREND_PULLBACK",
        timeframe=tf,
        entry=entry,
        stop_loss=sl,
        tp1=tp1,
        sar=_live_of(bars),
        opened_ms=s["open_time"][-1],
        now_ts=1_700_000_000.0,
    )


def test_aligned_at_entry_hands_over_immediately():
    bars = _rising(60)  # SAR bullish
    arm = _arm(bars, "LONG", entry=160.0, sl=155.0, tp1=170.0)
    assert arm["aligned_at_entry"] is True
    assert arm["governor"] == live.GOV_SAR
    # Alignment and the handover are facts about entry, recorded at entry --
    # #802 put exactly this in a 48h resolve path and 261 of 277 rows blanked.
    assert arm["handover_at"] is not None
    assert arm["handover_bar_ms"] == _series(bars)["open_time"][-1]
    assert arm["sar_stop"] == _live_of(bars).next_stop


def test_opposed_at_entry_keeps_the_original_geometry():
    bars = _rising(60)  # SAR bullish, but we are SHORT
    arm = _arm(bars, "SHORT", entry=160.0, sl=165.0, tp1=150.0)
    assert arm["aligned_at_entry"] is False
    assert arm["governor"] == live.GOV_GEOMETRY
    assert arm["handover_at"] is None


def test_no_sar_at_entry_refuses_instead_of_inventing_a_governor():
    arm = live.new_arm(
        signal_id="SIG-X",
        symbol="TESTUSDT",
        side="LONG",
        setup_class="X",
        timeframe="15m",
        entry=100.0,
        stop_loss=97.0,
        tp1=106.0,
        sar=None,
        opened_ms=1.0,
    )
    assert arm["status"] == live.STATUS_INSUFFICIENT
    assert arm["governor"] is None
    assert arm["aligned_at_entry"] is None
    assert arm["exit_reason"] == "no_sar_at_entry"


def test_sl_distance_is_recorded_at_entry_for_R():
    arm = _arm(_rising(60), "LONG", entry=100.0, sl=97.0, tp1=106.0)
    assert arm["sl_distance_pct"] == pytest.approx(3.0)


# --------------------------------------------------------------------------- #
# GEOMETRY leg — SL / TP1 while SAR is opposed
# --------------------------------------------------------------------------- #


def test_geometry_leg_closes_on_the_original_stop():
    bars = _rising(60)
    arm = _arm(bars, "SHORT", entry=160.0, sl=163.0, tp1=150.0)
    assert arm["governor"] == live.GOV_GEOMETRY
    # A bar whose high takes out the stop but does not open through it.
    bars2 = bars + [(160.5, 164.0, 160.0, 161.0)]
    changed = live.step_arm(arm, _series(bars2), step=STEP, max_step=MAX_STEP,
                            now_ts=1_700_000_100.0)
    assert changed is True
    assert arm["status"] == live.STATUS_CLOSED_SL
    assert arm["exit_reason"] == live.EXIT_STATIC_SL
    assert arm["fill_level"] == 163.0            # filled at the stop
    assert arm["fill_confirm"] == 161.0          # the bar's close
    assert arm["pnl_level_pct"] == pytest.approx((160.0 - 163.0) / 160.0 * 100.0)
    assert arm["r_level"] == pytest.approx(-1.0)


def test_geometry_leg_tp1_closes_in_full_no_runner():
    """Owner's call 2026-07-30: a TP1 touch ends the trade in this arm."""
    bars = _rising(60)
    arm = _arm(bars, "SHORT", entry=160.0, sl=163.0, tp1=150.0)
    bars2 = bars + [(159.0, 159.5, 149.0, 151.0)]
    live.step_arm(arm, _series(bars2), step=STEP, max_step=MAX_STEP)
    assert arm["status"] == live.STATUS_CLOSED_TP1
    assert arm["exit_reason"] == live.EXIT_STATIC_TP1
    # A resting limit fills at its own price; a gap through it does not fill
    # better than the level.
    assert arm["fill_level"] == 150.0
    assert arm["pnl_level_pct"] > 0


def test_geometry_leg_hands_over_when_sar_comes_onside():
    """SL and TP1 are cancelled at handover and never consulted again."""
    bars = _rising(60)
    arm = _arm(bars, "SHORT", entry=160.0, sl=200.0, tp1=100.0)  # untouchable
    assert arm["governor"] == live.GOV_GEOMETRY
    # Drive price down hard enough to flip SAR bearish, i.e. onside for a SHORT.
    bars2 = bars + _falling(25, start=158.0, step_dn=2.0)
    live.step_arm(arm, _series(bars2), step=STEP, max_step=MAX_STEP)
    assert arm["governor"] == live.GOV_SAR
    assert arm["handover_at"] is not None
    assert arm["handover_bar_ms"] is not None
    assert arm["status"] == live.STATUS_RUNNING
    assert arm["sar_stop"] is not None


def test_both_sl_and_tp_in_one_bar_is_flagged_not_silently_averaged():
    bars = _rising(60)
    arm = _arm(bars, "SHORT", entry=160.0, sl=163.0, tp1=150.0)
    bars2 = bars + [(160.0, 164.0, 149.0, 155.0)]  # takes out both
    live.step_arm(arm, _series(bars2), step=STEP, max_step=MAX_STEP)
    assert arm["ambiguous_bar"] is True
    # Resolved pessimistically — OHLC cannot order two touches inside one bar.
    assert arm["status"] == live.STATUS_CLOSED_SL


# --------------------------------------------------------------------------- #
# SAR leg — the flip, and the two fills
# --------------------------------------------------------------------------- #


def test_sar_leg_records_both_fills_and_the_cost_of_confirmation():
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=155.0, tp1=175.0)
    assert arm["governor"] == live.GOV_SAR
    parked = arm["sar_stop"]
    # A bar that breaches the parked stop intrabar and closes below it.
    breach = (parked + 0.4, parked + 0.5, parked - 2.0, parked - 1.5)
    live.step_arm(arm, _series(bars + [breach]), step=STEP, max_step=MAX_STEP)
    assert arm["status"] == live.STATUS_CLOSED_SAR_FLIP
    assert arm["exit_reason"] == live.EXIT_SAR_FLIP
    assert arm["fill_level"] == pytest.approx(parked)
    assert arm["fill_confirm"] == pytest.approx(parked - 1.5)
    # Waiting for the close cost us; the arm says so rather than picking one.
    assert arm["confirm_slippage_pct"] < 0
    assert arm["pnl_confirm_pct"] < arm["pnl_level_pct"]


def test_gap_through_fills_at_the_open_worse_never_better():
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=155.0, tp1=175.0)
    parked = arm["sar_stop"]
    gap = (parked - 3.0, parked - 2.5, parked - 5.0, parked - 4.0)
    live.step_arm(arm, _series(bars + [gap]), step=STEP, max_step=MAX_STEP)
    assert arm["fill_level"] == pytest.approx(parked - 3.0)  # the open, not the level
    assert arm["fill_level"] < parked


def test_sar_leg_ratchets_the_stop_while_the_trade_runs():
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=155.0, tp1=999.0)
    first = arm["sar_stop"]
    bars2 = bars + _rising(10, start=161.0)
    live.step_arm(arm, _series(bars2), step=STEP, max_step=MAX_STEP)
    assert arm["status"] == live.STATUS_RUNNING
    assert arm["sar_stop"] > first          # trails up, never down
    assert arm["sar_stop"] == _live_of(bars2).next_stop
    assert arm["bars_seen"] == 10


def test_R_divides_by_the_entry_stop_even_when_sar_governed():
    """Comparability: the edge matrix and /track-record divide by the same thing."""
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=152.0, tp1=999.0)  # 5% SL distance
    parked = arm["sar_stop"]
    breach = (parked + 0.2, parked + 0.3, parked - 1.0, parked - 0.5)
    live.step_arm(arm, _series(bars + [breach]), step=STEP, max_step=MAX_STEP)
    assert arm["sl_distance_pct"] == pytest.approx(5.0)
    assert arm["r_level"] == pytest.approx(arm["pnl_level_pct"] / 5.0)


# --------------------------------------------------------------------------- #
# Refusals — a clamp is not a guard
# --------------------------------------------------------------------------- #


def test_bar_rolled_out_of_window_refuses_instead_of_restarting():
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=155.0, tp1=175.0)
    # A series whose timestamps no longer contain the arm's last processed bar.
    moved_on = _series(_rising(60))
    moved_on["open_time"] = [t + 10_000 * BAR_MS for t in moved_on["open_time"]]
    changed = live.step_arm(arm, moved_on, step=STEP, max_step=MAX_STEP)
    assert changed is True
    assert arm["status"] == live.STATUS_INSUFFICIENT
    assert arm["exit_reason"] == "bar_rolled_out_of_window"


def test_series_refuses_a_store_whose_bars_cannot_say_when_they_are():
    """The conftest fixture omits open_time, so the slots are NaN by design."""
    from src.historical_data import HistoricalDataStore

    store = HistoricalDataStore()
    for _ in range(80):
        store.update_candle(
            "NOTIMEUSDT", "15m",
            {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 1.0},
        )
    assert live._series(store, "NOTIMEUSDT", "15m", 50) is None


def test_series_refuses_when_the_window_is_shorter_than_warmup():
    from src.historical_data import HistoricalDataStore

    store = HistoricalDataStore()
    for i in range(10):
        store.update_candle(
            "SHORTUSDT", "15m",
            {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0,
             "volume": 1.0, "open_time": 1_700_000_000_000 + i * BAR_MS},
        )
    assert live._series(store, "SHORTUSDT", "15m", 50) is None


# --------------------------------------------------------------------------- #
# Marks never touch realized columns
# --------------------------------------------------------------------------- #


def test_mark_writes_only_unrealized_columns():
    arm = _arm(_rising(60), "LONG", entry=160.0, sl=155.0, tp1=175.0)
    live.mark_arm(arm, 165.0)
    assert arm["unrealized_pct"] == pytest.approx(3.125)
    assert arm["pnl_level_pct"] is None
    assert arm["pnl_confirm_pct"] is None
    assert arm["r_level"] is None


def test_mark_is_a_noop_on_a_closed_arm():
    bars = _rising(60)
    arm = _arm(bars, "SHORT", entry=160.0, sl=163.0, tp1=150.0)
    live.step_arm(arm, _series(bars + [(160.5, 164.0, 160.0, 161.0)]),
                  step=STEP, max_step=MAX_STEP)
    assert arm["status"] == live.STATUS_CLOSED_SL
    live.mark_arm(arm, 999.0)
    assert arm["current_price"] is None
    assert arm["unrealized_pct"] is None


# --------------------------------------------------------------------------- #
# End to end, through the real store and a real Signal
# --------------------------------------------------------------------------- #


def _seed_store(symbol, bars, intervals=("5m", "15m")):
    from src.historical_data import HistoricalDataStore

    store = HistoricalDataStore()
    for interval in intervals:
        for i, (o, h, lo, c) in enumerate(bars):
            store.update_candle(
                symbol, interval,
                {"open": o, "high": h, "low": lo, "close": c, "volume": 1.0,
                 "open_time": 1_700_000_000_000 + i * BAR_MS},
            )
    return store


def test_observe_opens_one_arm_per_timeframe_from_a_real_signal():
    from src.channels.base import Signal
    from src.smc import Direction

    live.reset_sar_cache()
    ledger = live.SarLiveLedger(path="/tmp/sar_live_test_ledger.json")
    store = _seed_store("TESTUSDT", _rising(80))
    sig = Signal(
        channel="scalp", symbol="TESTUSDT", direction=Direction.LONG,
        entry=180.0, stop_loss=175.0, tp1=190.0, tp2=195.0,
        signal_id="SIG-E2E", setup_class="MOVER_TREND_PULLBACK",
    )
    live.observe_signal(sig, store, price=181.0, ledger=ledger, now_ts=_now_at(79))
    arms = ledger.open_arms()
    assert {a["timeframe"] for a in arms} == {"5m", "15m"}
    assert all(a["governor"] == live.GOV_SAR for a in arms)   # rising -> aligned
    assert all(a["signal_id"] == "SIG-E2E" for a in arms)
    # Idempotent: a second tick must not re-open the same arms.
    live.observe_signal(sig, store, price=181.0, ledger=ledger, now_ts=_now_at(79))
    assert len(ledger.open_arms()) == 2


def test_observe_retires_an_arm_once_it_closes():
    from src.channels.base import Signal
    from src.smc import Direction

    live.reset_sar_cache()
    ledger = live.SarLiveLedger(path="/tmp/sar_live_test_ledger2.json")
    bars = _rising(80)
    store = _seed_store("TESTUSDT", bars, intervals=("15m",))
    sig = Signal(
        channel="scalp", symbol="TESTUSDT", direction=Direction.SHORT,
        entry=180.0, stop_loss=182.0, tp1=170.0, tp2=165.0,
        signal_id="SIG-CLOSE", setup_class="X",
    )
    live.observe_signal(
        sig, store, price=180.0, ledger=ledger, timeframes=["15m"],
        now_ts=_now_at(len(bars) - 1),
    )
    assert len(ledger.open_arms()) == 1
    # Next bar blows through the static stop while SAR is still opposed.
    for i, bar in enumerate([(180.5, 184.0, 180.0, 183.0)], start=len(bars)):
        store.update_candle(
            "TESTUSDT", "15m",
            {"open": bar[0], "high": bar[1], "low": bar[2], "close": bar[3],
             "volume": 1.0, "open_time": 1_700_000_000_000 + i * BAR_MS},
        )
    # Advancing is the sweep's job, not ``observe_signal``'s (#835).
    live.sweep(
        store, price_fn=lambda _s: 183.0, ledger=ledger, now_ts=_now_at(len(bars))
    )
    assert ledger.open_arms() == []
    resolved = ledger.resolved_arms()
    assert len(resolved) == 1
    assert resolved[0]["status"] == live.STATUS_CLOSED_SL


# --------------------------------------------------------------------------- #
# Cross-repo contract — pinned on the producing side (#817)
# --------------------------------------------------------------------------- #

#: ops reads these off ``/engine-data/<DEFAULT_PATH basename>``. Renaming any of
#: them here without changing ops empties the panel silently, which is exactly
#: how ``entry_regime`` bucketed every signal into UNKNOWN for months.
OPS_CONTRACT_KEYS = frozenset({
    "arm_id", "signal_id", "symbol", "side", "setup_class", "timeframe",
    "entry", "stop_loss", "tp1", "sl_distance_pct",
    "opened_at", "opened_bar_ms", "last_bar_ms", "bars_seen",
    "aligned_at_entry", "governor", "handover_at", "handover_bar_ms",
    "sar_stop", "sar_up",
    "status", "exit_reason", "closed_at",
    "fill_level", "fill_confirm", "pnl_level_pct", "pnl_confirm_pct",
    "r_level", "r_confirm", "confirm_slippage_pct",
    "mfe_pct", "current_price", "unrealized_pct", "ambiguous_bar",
    "sar_risk_pct", "max_sar_risk_pct", "handover_risk_pct",
    "handover_wider_than_sl",
    # Freshness of the measurement, not of the price beside it (#835). Ops leads
    # every open row with these: without them a two-hour-old parked stop renders
    # identically to one computed a minute ago.
    "last_swept_at", "last_advance_at", "series_bar_ms", "bars_behind",
    "stalled", "stalled_since", "stall_reason",
    # Anchor integrity (#836). Ops grades every resolved row on these: an arm
    # that anchored to a stale bar walked history in its first advance, and
    # every freshness column above reads healthy on it because by then it was.
    "anchor_bars_behind", "first_step_bars",
    # …and the per-advance version of the same question. `first_step_bars`
    # guards only the arm's first step; these are set when a LATER advance tried
    # to cross more bars than the clock allows, which is how an arm stamped
    # `anchor=clean` consumed 466 bars in a 17-bar lifetime (2026-07-31).
    "advance_replay_bars", "advance_allowed_bars",
})


def test_arm_rows_carry_every_field_ops_reads():
    arm = _arm(_rising(60), "LONG", entry=160.0, sl=155.0, tp1=175.0)
    missing = OPS_CONTRACT_KEYS - set(arm)
    assert not missing, f"ops reads these and the engine stopped writing them: {missing}"


def test_ledger_filename_is_the_one_ops_mounts():
    assert live.SarLiveLedger.DEFAULT_PATH == "data/sar_live_arms_v1.json"


def test_ledger_roundtrips_through_disk(tmp_path):
    path = str(tmp_path / "arms.json")
    ledger = live.SarLiveLedger(path=path)
    ledger.add(_arm(_rising(60), "LONG", entry=160.0, sl=155.0, tp1=175.0))
    assert ledger.flush(force=True) is True
    restored = live.SarLiveLedger(path=path)
    restored.load()
    assert len(restored.open_arms()) == 1
    assert restored.open_arms()[0]["governor"] == live.GOV_SAR


def test_a_schema_bump_drops_rows_rather_than_reinterpreting_them(tmp_path):
    import json

    path = str(tmp_path / "arms.json")
    with open(path, "w") as fh:
        json.dump({"schema": live.LEDGER_SCHEMA + 1, "open": [{"arm_id": "x"}],
                   "resolved": []}, fh)
    ledger = live.SarLiveLedger(path=path)
    ledger.load()
    assert ledger.open_arms() == []


# --------------------------------------------------------------------------- #
# Health probe population
# --------------------------------------------------------------------------- #


def test_health_counts_arms_not_the_live_universe():
    """#815: a probe keyed on the scan universe cannot see what left it."""
    live.reset_health()
    live.record_step("ROTATEDUSDT", False, "no_series:15m")
    live.record_step("LIVEUSDT", True)
    live.roll_health_cycle()
    h = live.step_health()
    assert h["stepped"] == 1
    assert h["no_series"] == 1
    assert "ROTATEDUSDT" in h["symbols"]


def test_health_counters_are_per_cycle_not_cumulative():
    live.reset_health()
    live.record_step("A", False, "x")
    live.roll_health_cycle()
    live.record_step("A", True)
    live.roll_health_cycle()
    assert live.step_health()["no_series"] == 0


def test_a_stalled_arm_is_a_miss_named_apart_from_a_missing_series():
    """#835: presence of data is not currency of data.

    The old predicate had one failure bucket, so a stalled arm — series present,
    newest closed bar hours old — had nowhere to land and was counted as a
    healthy step. Missing candles and stale candles have different fixes and are
    counted separately.
    """
    live.reset_health()
    live.record_step("GONEUSDT", False, f"{live.STALL_NO_SERIES}:15m")
    live.record_step("FROZENUSDT", False, f"{live.STALL_BARS_BEHIND}:5m")
    live.record_step("OKUSDT", True)
    live.roll_health_cycle()
    h = live.step_health()
    assert (h["stepped"], h["no_series"], h["stalled"]) == (1, 1, 1)
    assert h["symbols"]["FROZENUSDT"].startswith(live.STALL_BARS_BEHIND)


# --------------------------------------------------------------------------- #
# A frozen arm is not a quiet one (#835)
# --------------------------------------------------------------------------- #
#
# The bug the owner caught on 2026-07-30: KORUUSDT SHORT sat RUNNING for 2h19m
# with ``bars_seen: 0``, its SAR direction still the one read at entry, and a
# parked 5m stop the live price had blown through by 5.45% — while ops rendered
# it as "the stop the mechanism would have parked right now" and the liveness
# probe read "2 arms stepped, no candle misses".
#
# Two causes, both here:
#   1. stepping rode the *live signal list*, so a closed signal orphaned its arm;
#   2. stepping is a no-op when no new bar has closed, which is indistinguishable
#      from a feed that stopped hours ago unless someone checks the clock.


def test_bars_behind_separates_a_quiet_bar_from_a_dead_feed():
    latest = 1_700_000_000_000.0
    # The bar that opened at ``latest`` closes one width later; at that instant
    # it IS the newest closed bar and nothing is owed.
    assert live.bars_behind(latest, "15m", latest / 1000.0 + 900.0) == 0.0
    # Two hours later, eight bars should have closed and none has.
    assert live.bars_behind(latest, "15m", latest / 1000.0 + 900.0 + 7200.0) == 8.0
    # An unknown timeframe refuses rather than guessing 60s and calling every
    # 15m arm stalled.
    assert live.bars_behind(latest, "7m", latest / 1000.0) is None
    assert live.bars_behind(None, "15m", latest / 1000.0) is None


def test_the_sweep_advances_an_arm_whose_signal_is_gone():
    """The orphan case. No signal is passed to ``sweep`` at all — by design.

    An arm exits on *its own* SAR flip, which is normally later than the live
    SL. Tying its stepping to the signal's lifetime truncated the population at
    the live exit and then never resolved it, which is worse than not measuring.
    """
    live.reset_sar_cache()
    ledger = live.SarLiveLedger(path="/tmp/sar_live_test_orphan.json")
    bars = _falling(80)
    store = _seed_store("GONEUSDT", bars, intervals=("15m",))
    sar = parabolic_sar_live(
        [b[1] for b in bars], [b[2] for b in bars], STEP, MAX_STEP,
        last_closed_ms=1_700_000_000_000.0 + (len(bars) - 1) * BAR_MS,
    )
    ledger.add(live.new_arm(
        signal_id="SIG-ORPHAN", symbol="GONEUSDT", side="SHORT",
        setup_class="BREAKDOWN_SHORT", timeframe="15m",
        entry=100.0, stop_loss=103.0, tp1=97.0, sar=sar,
        opened_ms=1_700_000_000_000.0 + (len(bars) - 1) * BAR_MS,
        now_ts=_now_at(len(bars) - 1),
    ))
    # A new bar closes. The signal that created this arm is long gone.
    store.update_candle("GONEUSDT", "15m", {
        "open": bars[-1][3], "high": bars[-1][3] * 1.05, "low": bars[-1][2],
        "close": bars[-1][3] * 1.04, "volume": 1.0,
        "open_time": 1_700_000_000_000.0 + len(bars) * BAR_MS,
    })
    tally = live.sweep(
        store, price_fn=lambda _s: 104.0, ledger=ledger, now_ts=_now_at(len(bars))
    )
    assert tally["advanced"] == 1
    arm = (ledger.open_arms() + ledger.resolved_arms())[0]
    assert arm["bars_seen"] == 1


def test_a_stalled_arm_says_so_instead_of_publishing_a_stale_stop_as_current():
    """The KORUUSDT row. No new bar for hours, arm still RUNNING.

    It stays open — a rotated-out mover can be re-promoted — but it is flagged,
    the lag is on the row in bar-widths, and ``last_advance_at`` does not move.
    Without that, a two-hour-old level renders identically to a fresh one.
    """
    live.reset_sar_cache()
    ledger = live.SarLiveLedger(path="/tmp/sar_live_test_stall.json")
    bars = _falling(80)
    store = _seed_store("KORUUSDT", bars, intervals=("15m",))
    last_ms = 1_700_000_000_000.0 + (len(bars) - 1) * BAR_MS
    sar = parabolic_sar_live(
        [b[1] for b in bars], [b[2] for b in bars], STEP, MAX_STEP,
        last_closed_ms=last_ms,
    )
    opened = _now_at(len(bars) - 1)
    ledger.add(live.new_arm(
        signal_id="SIG-STALL", symbol="KORUUSDT", side="SHORT",
        setup_class="BREAKDOWN_SHORT", timeframe="15m",
        entry=11.77, stop_loss=12.1231, tp1=11.26, sar=sar,
        opened_ms=last_ms, now_ts=opened,
    ))
    frozen_stop = ledger.get("SIG-STALL:15m")["sar_stop"]

    # 2h19m of wall-clock, no new bar: exactly the owner's export.
    later = opened + 2 * 3600 + 19 * 60
    tally = live.sweep(
        store, price_fn=lambda _s: 12.47, ledger=ledger, now_ts=later
    )

    assert tally == {
        "advanced": 0, "current": 0, "stalled": 1, "no_series": 0,
        # A series the store refuses as corrupt is counted apart from one that
        # is simply absent (2026-08-01) — opposite fixes, so never one number.
        "series_corrupt": 0, "retired": 0,
    }
    arm = ledger.get("SIG-STALL:15m")
    assert arm["status"] == live.STATUS_RUNNING
    assert arm["stalled"] is True
    assert arm["stall_reason"] == live.STALL_BARS_BEHIND
    assert arm["bars_behind"] == pytest.approx(9.27, abs=0.02)
    # The stop is unchanged and openly not current: it was computed on a bar
    # over two hours old and nothing pretends otherwise.
    assert arm["sar_stop"] == frozen_stop
    assert arm["last_advance_at"] == opened
    assert arm["last_swept_at"] == later
    # The mark is still real — a working price feed is not evidence the
    # measurement is running, which is why both facts sit on the row.
    assert arm["current_price"] == 12.47


def test_a_stall_past_the_abandon_bound_refuses_rather_than_filling():
    """Past the bound the gap in bars is unrecoverable — so no fill is invented.

    #800 published 172 confident rows describing bars it never saw. An arm that
    cannot be advanced is INSUFFICIENT and excluded from every R figure, not
    scored against whatever price happens to be on screen.
    """
    live.reset_sar_cache()
    ledger = live.SarLiveLedger(path="/tmp/sar_live_test_abandon.json")
    bars = _falling(80)
    store = _seed_store("KORUUSDT", bars, intervals=("15m",))
    last_ms = 1_700_000_000_000.0 + (len(bars) - 1) * BAR_MS
    sar = parabolic_sar_live(
        [b[1] for b in bars], [b[2] for b in bars], STEP, MAX_STEP,
        last_closed_ms=last_ms,
    )
    opened = _now_at(len(bars) - 1)
    ledger.add(live.new_arm(
        signal_id="SIG-ABANDON", symbol="KORUUSDT", side="SHORT",
        setup_class="BREAKDOWN_SHORT", timeframe="15m",
        entry=11.77, stop_loss=12.1231, tp1=11.26, sar=sar,
        opened_ms=last_ms, now_ts=opened,
    ))
    live.sweep(store, ledger=ledger, now_ts=opened + 3600, abandon_sec=1800)
    tally = live.sweep(store, ledger=ledger, now_ts=opened + 7200, abandon_sec=1800)
    assert tally["retired"] == 1
    assert ledger.open_arms() == []
    arm = ledger.resolved_arms()[0]
    assert arm["status"] == live.STATUS_INSUFFICIENT
    assert arm["exit_reason"] == live.EXIT_FEED_STALLED
    assert arm["fill_level"] is None and arm["r_level"] is None


def test_a_current_arm_between_bars_is_not_a_stall():
    """The quiet case must stay quiet, or the fix pages on healthy engines.

    This is the mirror of the heartbeat lesson one file over: "nothing to do" is
    not a fault, and a detector that cannot say so gets muted.
    """
    live.reset_sar_cache()
    ledger = live.SarLiveLedger(path="/tmp/sar_live_test_current.json")
    bars = _falling(80)
    store = _seed_store("LIVEUSDT", bars, intervals=("15m",))
    last_ms = 1_700_000_000_000.0 + (len(bars) - 1) * BAR_MS
    sar = parabolic_sar_live(
        [b[1] for b in bars], [b[2] for b in bars], STEP, MAX_STEP,
        last_closed_ms=last_ms,
    )
    opened = _now_at(len(bars) - 1)
    ledger.add(live.new_arm(
        signal_id="SIG-QUIET", symbol="LIVEUSDT", side="SHORT",
        setup_class="BREAKDOWN_SHORT", timeframe="15m",
        entry=100.0, stop_loss=103.0, tp1=97.0, sar=sar,
        opened_ms=last_ms, now_ts=opened,
    ))
    # Mid-bar: the bar now trading has not closed. Nothing is owed.
    tally = live.sweep(store, ledger=ledger, now_ts=opened + 400.0)
    assert tally["current"] == 1 and tally["stalled"] == 0
    assert ledger.get("SIG-QUIET:15m")["stalled"] is False


def test_an_arm_the_store_cannot_supply_is_a_miss_not_a_step():
    live.reset_sar_cache()
    ledger = live.SarLiveLedger(path="/tmp/sar_live_test_noseries.json")
    bars = _falling(80)
    store = _seed_store("LIVEUSDT", bars, intervals=("15m",))
    last_ms = 1_700_000_000_000.0 + (len(bars) - 1) * BAR_MS
    sar = parabolic_sar_live(
        [b[1] for b in bars], [b[2] for b in bars], STEP, MAX_STEP,
        last_closed_ms=last_ms,
    )
    ledger.add(live.new_arm(
        signal_id="SIG-NOSERIES", symbol="DELISTEDUSDT", side="SHORT",
        setup_class="X", timeframe="15m", entry=100.0, stop_loss=103.0,
        tp1=97.0, sar=sar, opened_ms=last_ms, now_ts=_now_at(len(bars) - 1),
    ))
    tally = live.sweep(store, ledger=ledger, now_ts=_now_at(len(bars)))
    assert tally["no_series"] == 1
    arm = ledger.get("SIG-NOSERIES:15m")
    assert arm["stalled"] is True
    assert arm["stall_reason"] == live.STALL_NO_SERIES


def test_an_arm_open_past_the_horizon_refuses_rather_than_running_forever():
    """SIGNAL_EXPIRY_ENABLED is off and the mechanism has no time stop, so an arm
    that never flips would otherwise sit in the open set indefinitely. It is
    retired unmeasured rather than handed an invented market close."""
    live.reset_sar_cache()
    ledger = live.SarLiveLedger(path="/tmp/sar_live_test_horizon.json")
    bars = _falling(80)
    store = _seed_store("LIVEUSDT", bars, intervals=("15m",))
    last_ms = 1_700_000_000_000.0 + (len(bars) - 1) * BAR_MS
    sar = parabolic_sar_live(
        [b[1] for b in bars], [b[2] for b in bars], STEP, MAX_STEP,
        last_closed_ms=last_ms,
    )
    opened = _now_at(len(bars) - 1)
    ledger.add(live.new_arm(
        signal_id="SIG-HORIZON", symbol="LIVEUSDT", side="SHORT",
        setup_class="X", timeframe="15m", entry=100.0, stop_loss=103.0,
        tp1=97.0, sar=sar, opened_ms=last_ms, now_ts=opened,
    ))
    tally = live.sweep(
        store, ledger=ledger, now_ts=opened + 49 * 3600, max_open_hours=48
    )
    assert tally["retired"] == 1
    arm = ledger.resolved_arms()[0]
    assert arm["status"] == live.STATUS_INSUFFICIENT
    assert arm["exit_reason"] == live.EXIT_OPEN_AT_HORIZON
    assert arm["r_level"] is None


# --------------------------------------------------------------------------- #
# The heartbeat — "blank" needs a cause before it gets a caption
# --------------------------------------------------------------------------- #
#
# Ops separates three states off this file: missing (loop not running), current
# but empty (running, nothing open), stale (loop stopped stepping). They are only
# separable if a live loop keeps touching the file even when nothing changes.
# Without that, an idle engine looked identical to a broken one and the panel
# reported a fault that was not happening (owner-caught 2026-07-30).


def test_an_empty_ledger_still_writes_so_idle_is_distinguishable_from_broken(tmp_path):
    path = str(tmp_path / "arms.json")
    ledger = live.SarLiveLedger(path=path)
    assert ledger.open_arms() == [] and ledger.resolved_arms() == []
    # First tick after boot: _last_write is 0, so the heartbeat is already due.
    assert ledger.flush() is True
    import json as _json

    payload = _json.loads(open(path).read())
    assert payload["open"] == []
    assert payload["written_at"] > 0


def test_the_heartbeat_advances_mtime_with_no_arm_changes(tmp_path):
    path = str(tmp_path / "arms.json")
    ledger = live.SarLiveLedger(path=path)
    ledger.flush()
    first = ledger._last_write
    # Nothing changed and the heartbeat is not due — no write.
    assert ledger.flush(heartbeat_sec=60.0) is False
    assert ledger._last_write == first
    # Heartbeat due, still nothing changed — writes anyway, which is the point.
    assert ledger.flush(heartbeat_sec=0.0) is True
    assert ledger._last_write > first


def test_a_change_still_writes_ahead_of_the_heartbeat(tmp_path):
    path = str(tmp_path / "arms.json")
    ledger = live.SarLiveLedger(path=path)
    ledger.flush(force=True)
    ledger.add(_arm(_rising(60), "LONG", entry=160.0, sl=155.0, tp1=175.0))
    # Dirty and past the change throttle, but nowhere near the heartbeat.
    assert ledger.flush(min_interval_sec=0.0, heartbeat_sec=3600.0) is True
    import json as _json

    assert len(_json.loads(open(path).read())["open"]) == 1


def test_the_change_throttle_still_bounds_write_rate(tmp_path):
    """This runs in a 5s loop; a dirty ledger must not write on every tick."""
    path = str(tmp_path / "arms.json")
    ledger = live.SarLiveLedger(path=path)
    ledger.flush(force=True)
    ledger.add(_arm(_rising(60), "LONG", entry=160.0, sl=155.0, tp1=175.0))
    assert ledger.flush(min_interval_sec=3600.0, heartbeat_sec=3600.0) is False


# --------------------------------------------------------------------------- #
# Risk stamps — what the SAR stop actually puts at risk
# --------------------------------------------------------------------------- #
#
# Owner-caught 2026-07-30 on the first two live arms: MUUUSDT SHORT, entry
# 18.67, designed SL 19.2301 (3.00%). The 5m SAR stop sat at 18.9684 — 1.60%,
# tighter than designed. The 15m sat at 19.3734 — 3.77%, *wider*, i.e. outside
# the stop the evaluator sized the trade for. A stop-out there scores -1.26R.
#
# The arm's behaviour is unchanged: these are stamps so the resolved population
# can be split, not a cap. Capping is a separate decision the owner can now make
# with data behind it.


def test_risk_is_stamped_against_the_sl_the_trade_was_sized_for():
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=152.0, tp1=999.0)  # 5% designed
    assert arm["governor"] == live.GOV_SAR
    stop = arm["sar_stop"]
    expected = (160.0 - stop) / 160.0 * 100.0
    assert arm["sar_risk_pct"] == pytest.approx(expected)
    assert arm["handover_risk_pct"] == pytest.approx(expected)
    assert arm["handover_wider_than_sl"] is (expected > 5.0)


def test_a_sar_stop_wider_than_the_designed_sl_is_flagged():
    """The 15m MUUUSDT case, reproduced from its real numbers."""
    bars = _rising(60)
    stop = _live_of(bars).next_stop
    # Designed SL deliberately tighter than where SAR parked.
    tight = 160.0 - (160.0 - stop) * 0.5
    arm = _arm(bars, "LONG", entry=160.0, sl=tight, tp1=999.0)
    assert arm["sar_risk_pct"] > arm["sl_distance_pct"]
    assert arm["handover_wider_than_sl"] is True


def test_a_sar_stop_inside_the_designed_sl_is_not_flagged():
    """The 5m MUUUSDT case — SAR tighter than the signal's own stop."""
    bars = _rising(60)
    stop = _live_of(bars).next_stop
    wide = 160.0 - (160.0 - stop) * 2.0
    arm = _arm(bars, "LONG", entry=160.0, sl=wide, tp1=999.0)
    assert arm["sar_risk_pct"] < arm["sl_distance_pct"]
    assert arm["handover_wider_than_sl"] is False


def test_short_side_risk_is_measured_above_the_entry():
    bars = _falling(60)  # SAR bearish -> a SHORT is aligned
    entry = bars[-1][3]  # enter at the last close, as a real signal does
    arm = _arm(bars, "SHORT", entry=entry, sl=entry * 1.03, tp1=entry * 0.94)
    assert arm["aligned_at_entry"] is True
    stop = arm["sar_stop"]
    assert stop > entry                      # a SHORT's stop sits above entry
    assert arm["sar_risk_pct"] == pytest.approx((stop - entry) / entry * 100.0)
    assert arm["sar_risk_pct"] > 0


def test_max_risk_tracks_the_widest_the_stop_ever_sat_not_just_the_handover():
    """SAR's two-bar clamp can move the level away from price, so the widest
    point is not knowable at handover and must be tracked per bar."""
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=140.0, tp1=999.0)
    at_handover = arm["max_sar_risk_pct"]
    live.step_arm(arm, _series(bars + _rising(10, start=161.0)),
                  step=STEP, max_step=MAX_STEP)
    # Trailing up on a LONG reduces risk; the max must not follow it down.
    assert arm["sar_risk_pct"] < at_handover
    assert arm["max_sar_risk_pct"] == pytest.approx(at_handover)


def test_risk_becomes_negative_once_the_trail_passes_break_even():
    """A stop on the profitable side is a locked gain, not a risk — the sign is
    kept rather than clamped, because 'zero risk' would be a different claim."""
    bars = _rising(60) + _rising(40, start=161.0)
    arm = _arm(_rising(60), "LONG", entry=100.0, sl=97.0, tp1=9999.0)
    live.step_arm(arm, _series(bars), step=STEP, max_step=MAX_STEP)
    assert arm["sar_stop"] > 100.0
    assert arm["sar_risk_pct"] < 0


def test_the_geometry_leg_carries_no_handover_risk_until_it_hands_over():
    bars = _rising(60)
    arm = _arm(bars, "SHORT", entry=160.0, sl=200.0, tp1=100.0)
    assert arm["governor"] == live.GOV_GEOMETRY
    assert arm["handover_risk_pct"] is None
    assert arm["handover_wider_than_sl"] is None
    live.step_arm(arm, _series(bars + _falling(25, start=158.0, step_dn=2.0)),
                  step=STEP, max_step=MAX_STEP)
    assert arm["governor"] == live.GOV_SAR
    # Stamped at the moment the SL stopped governing, not reconstructed later.
    assert arm["handover_risk_pct"] is not None
    assert arm["handover_wider_than_sl"] in (True, False)


def test_risk_stamps_do_not_change_which_stop_the_arm_uses():
    """Stamp only. The exit must be identical to the pre-stamp behaviour."""
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=152.0, tp1=999.0)
    parked = arm["sar_stop"]
    breach = (parked + 0.4, parked + 0.5, parked - 2.0, parked - 1.5)
    live.step_arm(arm, _series(bars + [breach]), step=STEP, max_step=MAX_STEP)
    assert arm["status"] == live.STATUS_CLOSED_SAR_FLIP
    assert arm["fill_level"] == pytest.approx(parked)
    # R still divides by the SL distance at entry, not by the SAR risk.
    assert arm["r_level"] == pytest.approx(arm["pnl_level_pct"] / 5.0)


# --------------------------------------------------------------------------- #
# Anchoring: an arm that starts life behind the clock replays, it does not step
# --------------------------------------------------------------------------- #
#
# Found in the owner's 2026-07-31 export.  ACHUSDT 15m carried ``bars_seen: 158``
# after 10 bars of life, and ``aligned_at_entry`` disagreed with its own 5m
# sibling on the same signal — because the 15m series the arm anchored to was
# ~40h stale at creation, so its SAR-at-entry was read off a 40h-old bar and its
# first advance walked the whole gap in one pass.  Every fill it published was a
# replay, on the one page in the system whose first sentence is "this is not a
# replay".


def _stale_signal(symbol="STALEUSDT"):
    from src.channels.base import Signal
    from src.smc import Direction

    return Signal(
        channel="scalp", symbol=symbol, direction=Direction.LONG,
        entry=180.0, stop_loss=175.0, tp1=190.0, tp2=195.0,
        signal_id="SIG-STALE", setup_class="MOVER_TREND_PULLBACK",
    )


def test_observe_refuses_to_open_an_arm_on_a_stale_anchor_bar():
    """The guard. Fails against the old code, which opened the arm regardless."""
    live.reset_sar_cache()
    live.reset_health()
    ledger = live.SarLiveLedger(path="/tmp/sar_live_test_stale.json")
    bars = _rising(80)
    store = _seed_store("STALEUSDT", bars, intervals=("15m",))
    # The newest closed bar is index 79; the clock says 40 bars have passed since.
    stale_now = _now_at(79) + 40 * (BAR_MS / 1000.0)
    live.observe_signal(
        _stale_signal(), store, price=181.0, ledger=ledger,
        timeframes=["15m"], now_ts=stale_now,
    )
    assert ledger.open_arms() == []
    live.roll_health_cycle()
    h = live.step_health()
    assert h["refused_open"] == 1
    # Named, not merely counted: "no series" and "stale anchor" have different
    # fixes, and a refusal must never be pooled with a frozen arm.
    assert live.OPEN_REFUSED_STALE_ANCHOR in h["refused"]["STALEUSDT:15m"]
    assert h["stalled"] == 0 and h["no_series"] == 0


def test_observe_opens_once_the_series_catches_up():
    """Refusing is not permanent — the arm opens on the first current anchor."""
    live.reset_sar_cache()
    live.reset_health()
    ledger = live.SarLiveLedger(path="/tmp/sar_live_test_stale2.json")
    bars = _rising(80)
    store = _seed_store("STALEUSDT", bars, intervals=("15m",))
    sig = _stale_signal()
    live.observe_signal(
        sig, store, price=181.0, ledger=ledger, timeframes=["15m"],
        now_ts=_now_at(79) + 40 * (BAR_MS / 1000.0),
    )
    assert ledger.open_arms() == []
    live.observe_signal(
        sig, store, price=181.0, ledger=ledger, timeframes=["15m"],
        now_ts=_now_at(79),
    )
    arms = ledger.open_arms()
    assert len(arms) == 1
    # Stamped where it becomes true: this arm anchored to a current bar.
    assert arms[0]["anchor_bars_behind"] == pytest.approx(0.0)


def test_first_step_bars_detects_an_arm_that_walked_history():
    """The detector, kept beside the guard rather than replacing it.

    A live arm consumes one bar per advance. Anything larger on the *first*
    advance is history the arm walked after it was created, and the row says so
    instead of leaving the reader to infer it from ``bars_seen``.
    """
    bars = _rising(60)
    arm = _arm(bars, "LONG", entry=160.0, sl=152.0, tp1=9999.0)
    assert arm["first_step_bars"] is None
    live.step_arm(arm, _series(bars + _rising(12, start=220.0)),
                  step=STEP, max_step=MAX_STEP)
    assert arm["first_step_bars"] == 12
    # Only the first advance is recorded — later steps must not overwrite it.
    before = arm["first_step_bars"]
    if arm["status"] == live.STATUS_RUNNING:
        live.step_arm(arm, _series(bars + _rising(13, start=220.0)),
                      step=STEP, max_step=MAX_STEP)
    assert arm["first_step_bars"] == before


class TestTheSeriesReaderRefusesACorruptedWindow:
    """SAR is path-dependent, and that changes what "degrade gracefully" means.

    The dark lane walks fixed levels, so an imprecise window costs precision in
    the *label* — walk it and mark the row. SAR carries an acceleration factor
    and an extreme point forward bar by bar, so a duplicated bar advances the AF
    one extra step and moves the stop toward price permanently. Every level after
    it is wrong and nothing recovers. Here the imprecision is in the *answer*, so
    the reader refuses.
    """

    @staticmethod
    def _store(times):
        n = len(times)

        class _S:
            def get_candles(self, symbol, tf):
                return {
                    "high": [101.0] * n, "low": [99.0] * n,
                    "open": [100.0] * n, "close": [100.0] * n,
                    "open_time": [float(t) for t in times],
                }
        return _S()

    def test_a_clean_series_is_returned(self):
        base = 1_700_000_000_000
        times = [base + i * 60_000 for i in range(30)]
        out = live._series(self._store(times), "BTCUSDT", "5m", warmup=5)
        assert out is not None
        assert len(out["open_time"]) == 30

    def test_a_duplicated_bar_is_refused_not_walked(self):
        base = 1_700_000_000_000
        times = [base + i * 60_000 for i in range(30)]
        times[17] = times[16]                      # one duplicate, mid-window
        before = live.series_refusals()["duplicate_bar"]

        out = live._series(self._store(times), "BTCUSDT", "5m", warmup=5)

        assert out is None
        assert live.series_refusals()["duplicate_bar"] == before + 1

    def test_an_out_of_order_bar_is_refused_and_named_separately(self):
        """Different cause, different fix: a duplicate points at the store's
        append path, an inversion points at the feed."""
        base = 1_700_000_000_000
        times = [base + i * 60_000 for i in range(30)]
        times[20] = base                            # far out of order
        before = live.series_refusals()["out_of_order"]

        out = live._series(self._store(times), "BTCUSDT", "5m", warmup=5)

        assert out is None
        assert live.series_refusals()["out_of_order"] == before + 1

    def test_the_endpoints_look_healthy_while_the_middle_is_corrupt(self):
        """Why the check runs over the whole window rather than the ends: a
        single interior duplicate leaves first and last timestamps perfectly
        ordered, and that is precisely the window that must be refused."""
        base = 1_700_000_000_000
        times = [base + i * 60_000 for i in range(30)]
        times[10] = times[9]

        assert times[-1] > times[0], "endpoints are fine — that is the point"
        assert live._series(self._store(times), "BTCUSDT", "5m", warmup=5) is None


class TestARegressedSeriesIsNotARolledOutBar:
    """Owner data 2026-08-02: `bar_rolled_out_of_window` killed 10 of the 15
    unmeasurable arms, at a **median of four bars**, on arms that had opened on
    a current bar and were measuring fine. Nine of the ten were mover paths.

    The cause is `seed_symbol`, which REPLACES a bucket wholesale — and promoted
    movers are re-seeded on a throttle because they carry no WS kline
    subscription. A REST pull that has not yet caught up with a bar the socket
    already delivered leaves the arm's `last_bar_ms` past the end of the array.
    Nothing is lost; the bar comes back on the next write.

    Two causes, opposite fixes, and they were one death. Declining to advance is
    not a clamp — it is exactly what the arm does on any cycle with no new bars.
    """

    @staticmethod
    def _series(times, price=100.0):
        n = len(times)
        return {
            "high": [price + 1] * n, "low": [price - 1] * n,
            "open": [price] * n, "close": [price] * n,
            "open_time": [float(t) for t in times],
        }

    @staticmethod
    def _arm(last_bar_ms):
        return {
            "arm_id": "A:5m", "symbol": "AIOUSDT", "timeframe": "5m",
            "side": "LONG", "status": live.STATUS_RUNNING,
            "entry": 100.0, "stop_loss": 97.0, "tp1": 103.0,
            "governor": live.GOV_GEOMETRY, "sar_up": True,
            "last_bar_ms": float(last_bar_ms), "bars_seen": 4,
            "mfe_pct": 0.0, "mae_pct": 0.0, "series_regressions": 0,
            "opened_at": 1_700_000_000.0, "last_advance_at": 1_700_000_000.0,
        }

    def test_a_window_ending_before_our_bar_makes_the_arm_wait(self):
        base = 1_700_000_000_000
        # Store re-seeded and came back one bar SHORT of what we consumed.
        arm = self._arm(base + 10 * 60_000)
        series = self._series([base + i * 60_000 for i in range(10)])

        changed = live.step_arm(arm, series, step=STEP, max_step=MAX_STEP, now_ts=1_700_000_600.0)

        assert changed is False
        assert arm["status"] == live.STATUS_RUNNING, "the arm must survive"
        assert arm.get("exit_reason") is None
        assert arm["series_regressions"] == 1

    def test_history_rolling_off_the_front_still_retires_the_arm(self):
        """The genuinely unrecoverable case: bars we never saw are gone, so a
        starting index would have to be invented."""
        base = 1_700_000_000_000
        arm = self._arm(base)                      # our bar is oldest
        series = self._series([base + i * 60_000 for i in range(50, 60)])

        changed = live.step_arm(arm, series, step=STEP, max_step=MAX_STEP, now_ts=1_700_000_600.0)

        assert changed is True
        assert arm["status"] == live.STATUS_INSUFFICIENT
        assert arm["exit_reason"] == live.EXIT_BAR_ROLLED_OUT

    def test_a_bar_inside_the_range_but_off_the_grid_is_named_separately(self):
        """Different fault, different fix: the history is not gone, the grid
        changed under us. Pooling it with a roll-out would send the reader to
        the wrong subsystem."""
        base = 1_700_000_000_000
        arm = self._arm(base + 5 * 60_000 + 17_000)   # between two bars
        series = self._series([base + i * 60_000 for i in range(10)])

        changed = live.step_arm(arm, series, step=STEP, max_step=MAX_STEP, now_ts=1_700_000_600.0)

        assert changed is True
        assert arm["status"] == live.STATUS_INSUFFICIENT
        assert arm["exit_reason"] == live.EXIT_BAR_NOT_ON_GRID

    def test_a_recovered_series_resumes_where_the_arm_left_off(self):
        """The whole point: the arm waited, the bar came back, and it continues
        rather than having been thrown away over a transient."""
        base = 1_700_000_000_000
        arm = self._arm(base + 9 * 60_000)

        live.step_arm(arm, self._series([base + i * 60_000 for i in range(9)]),
                      step=STEP, max_step=MAX_STEP, now_ts=1_700_000_600.0)
        assert arm["status"] == live.STATUS_RUNNING
        assert arm["series_regressions"] == 1

        # Next write brings the bar back, plus two new ones.
        live.step_arm(arm, self._series([base + i * 60_000 for i in range(12)]),
                      step=STEP, max_step=MAX_STEP, now_ts=1_700_000_900.0)

        # It resumed and consumed them. Whether it then stayed open or exited on
        # a SAR flip is the mechanism's business — the property under test is
        # that the arm was still alive to make that decision, instead of having
        # been retired as unmeasurable over a transient.
        assert arm["bars_seen"] > 4, "it consumed the new bars"
        assert arm["last_bar_ms"] == float(base + 11 * 60_000)
        assert arm["exit_reason"] != live.EXIT_BAR_ROLLED_OUT


# --------------------------------------------------------------------------- #
# Coverage — the population the verdict does NOT cover
# --------------------------------------------------------------------------- #
#
# Every guard above asks whether an arm that EXISTS measured honestly. None of
# them could see a delivered signal that never became an arm, and that was the
# largest exclusion of all: a guest-session audit on 2026-08-08 joined this
# ledger to `signal_performance.json` and found 18.4% of delivered trades with
# no arm, running -1.643%/trade at 10.7% win against +0.753% and 43.5% for the
# armed ones. The page's "+0.588%/arm" was therefore a winner-enriched subset
# reported as if it were the book.
#
# This is #815's rule ("key a probe on the population that would be harmed")
# arriving one step earlier than any previous fix in this module: not arms owed
# a verdict, but signals owed a measurement.


def _e2e_signal(signal_id="SIG-COV", symbol="TESTUSDT", **kw):
    from src.channels.base import Signal
    from src.smc import Direction

    fields = dict(
        channel="scalp", symbol=symbol, direction=Direction.LONG,
        entry=180.0, stop_loss=175.0, tp1=190.0, tp2=195.0,
        signal_id=signal_id, setup_class="MOVER_TREND_PULLBACK",
    )
    fields.update(kw)
    return Signal(**fields)


def test_a_signal_with_no_series_is_counted_not_silently_skipped():
    """The defect this whole block exists for: an unarmed signal left no trace.

    Driven through the real ``observe_signal`` against a real
    ``HistoricalDataStore`` holding candles for 15m only, so the 5m arm cannot
    open for the honest reason. Before the fix both the census and
    ``refused_open`` were untouched here and the signal vanished from every
    count in the system.
    """
    live.reset_sar_cache()
    live.reset_health()
    ledger = live.SarLiveLedger(path="")
    bars = _rising(80)
    store = _seed_store("TESTUSDT", bars, intervals=("15m",))
    sig = _e2e_signal()

    live.observe_signal(sig, store, price=181.0, ledger=ledger, now_ts=_now_at(79))

    cov = ledger.coverage()
    assert cov["signals_seen"] == 1
    assert cov["partly_armed"] == 1, "15m armed, 5m not — neither covered nor missing"
    assert cov["fully_armed"] == 0
    assert cov["reasons"].get(live.OPEN_REFUSED_NO_SERIES) == 1
    miss = cov["misses"][0]
    assert miss["armed"] == ["15m"]
    assert miss["missing"] == {"5m": live.OPEN_REFUSED_NO_SERIES}
    # …and it reaches the health counter the probe reads, too.
    assert live.step_health()["refused_open"] == 0  # rolls into `last` on cycle
    live.roll_health_cycle()
    assert live.step_health()["refused_open"] == 1


def test_coverage_is_current_state_not_first_attempt():
    """A series arriving late must clear the miss, not leave a stale one.

    Otherwise the census reports a coverage gap that has already healed, which
    is the "blank needs a cause before it gets a caption" failure pointed at a
    fraction rather than at a panel.
    """
    live.reset_sar_cache()
    ledger = live.SarLiveLedger(path="")
    bars = _rising(80)
    store = _seed_store("TESTUSDT", bars, intervals=("15m",))
    sig = _e2e_signal()
    live.observe_signal(sig, store, price=181.0, ledger=ledger, now_ts=_now_at(79))
    assert ledger.coverage()["partly_armed"] == 1

    # The 5m series shows up on a later cycle.
    store2 = _seed_store("TESTUSDT", bars, intervals=("5m", "15m"))
    live.reset_sar_cache()
    live.observe_signal(sig, store2, price=181.0, ledger=ledger, now_ts=_now_at(79))

    cov = ledger.coverage()
    assert cov["fully_armed"] == 1, "the late arm cleared the miss"
    assert cov["partly_armed"] == 0
    assert cov["misses"] == []


def test_coverage_survives_a_restart():
    """Flush without load is worse than neither.

    Coverage is a CUMULATIVE claim about the book, so a restart resetting it to
    zero would make the fraction describe only the time since the last deploy
    while reading exactly like the whole window — the same shape as the two
    structural ledgers that erased their own evidence on every deploy.
    """
    import tempfile, os as _os

    live.reset_sar_cache()
    fd, path = tempfile.mkstemp(suffix=".json")
    _os.close(fd)
    _os.unlink(path)
    try:
        ledger = live.SarLiveLedger(path=path)
        bars = _rising(80)
        store = _seed_store("TESTUSDT", bars, intervals=("15m",))
        live.observe_signal(
            _e2e_signal(), store, price=181.0, ledger=ledger, now_ts=_now_at(79)
        )
        assert ledger.flush(force=True) is True

        restored = live.SarLiveLedger(path=path)
        restored.load()
        cov = restored.coverage()
        assert cov["signals_seen"] == 1
        assert cov["partly_armed"] == 1
        assert cov["misses"][0]["missing"] == {"5m": live.OPEN_REFUSED_NO_SERIES}
        # The armed half is rebuilt from the arms themselves rather than stored
        # twice — the fix for a drifting mirror is not a second mirror.
        assert cov["misses"][0]["armed"] == ["15m"]
    finally:
        for p in (path, f"{path}.tmp"):
            if _os.path.exists(p):
                _os.unlink(p)


def test_coverage_is_bounded_and_says_how_much_it_dropped():
    """A capped ring makes every verdict on it a sample, and the cap must show."""
    live.reset_sar_cache()
    ledger = live.SarLiveLedger(path="", max_coverage=3)
    bars = _rising(80)
    store = _seed_store("TESTUSDT", bars, intervals=("15m",))
    for i in range(6):
        live.observe_signal(
            _e2e_signal(signal_id=f"SIG-{i}"), store, price=181.0,
            ledger=ledger, timeframes=["15m"], now_ts=_now_at(79) + i,
        )
    cov = ledger.coverage()
    assert cov["signals_seen"] == 3
    assert cov["evicted"] == 3
    assert cov["cap"] == 3


# --------------------------------------------------------------------------- #
# The risk denominator (#848), one lane later
# --------------------------------------------------------------------------- #


def test_sl_distance_comes_from_the_stop_the_trade_was_sized_for():
    """``TradeMonitor`` moves ``sig.stop_loss`` in place; the arm must not follow.

    An arm opening after a BE shift would divide every R by ~0. The evaluator's
    ``original_sl_distance`` is the stop the trade was SIZED for and is what
    ``snapshot._original_stop_loss`` already reads.
    """
    live.reset_sar_cache()
    ledger = live.SarLiveLedger(path="")
    bars = _rising(80)
    store = _seed_store("TESTUSDT", bars, intervals=("15m",))
    # Entry 180, designed stop 175 (2.78%), then the monitor break-even shifts
    # the live stop up to entry — which is the state that breaks the fallback.
    sig = _e2e_signal(stop_loss=180.0)
    sig.original_sl_distance = 5.0
    live.observe_signal(
        sig, store, price=181.0, ledger=ledger, timeframes=["15m"],
        now_ts=_now_at(79),
    )
    arm = ledger.open_arms()[0]
    assert arm["sl_distance_source"] == "original"
    assert arm["sl_distance_pct"] == pytest.approx(5.0 / 180.0 * 100.0)
    # The naive fallback would have produced 0.0 here, and every R on the page
    # would have divided by it.
    assert abs(arm["entry"] - arm["stop_loss"]) == 0.0


def test_sl_distance_falls_back_but_names_the_fallback():
    """Refusing outright would empty the population; a silent fallback would
    redefine a column mid-book. Neither — fall back and say so."""
    arm = _arm(_rising(60), "LONG", entry=160.0, sl=155.0, tp1=175.0)
    assert arm["sl_distance_source"] == "live_stop"
    assert arm["sl_distance_pct"] == pytest.approx(5.0 / 160.0 * 100.0)


#: The coverage block ops reads off the flushed ledger. Pinned HERE, on the
#: producing side, and pinned by **location** as well as by name: the
#: price-action lane card shipped with an ops fixture that put its block at the
#: payload's top level while the engine nested it under `derived`, and every ops
#: test passed over a card that would have rendered NOT REPORTED against the
#: real engine. Shape right, path wrong.
OPS_COVERAGE_KEYS = frozenset({
    "signals_seen", "fully_armed", "partly_armed", "unarmed",
    "reasons", "misses", "evicted", "cap",
})


def test_the_flushed_payload_carries_coverage_where_ops_looks_for_it(tmp_path):
    """Driven through the real flush, not through ``coverage()`` directly.

    ``coverage()`` returning the right dict proves nothing about the file: the
    serializer is its own seam, and a field a writer populates and a serializer
    drops is invisible at both ends (#842, where `open_time` was added to the
    store and never survived a restart).
    """
    import json

    live.reset_sar_cache()
    path = str(tmp_path / "arms.json")
    ledger = live.SarLiveLedger(path=path)
    store = _seed_store("TESTUSDT", _rising(80), intervals=("15m",))
    live.observe_signal(
        _e2e_signal(), store, price=181.0, ledger=ledger, now_ts=_now_at(79)
    )
    assert ledger.flush(force=True) is True

    payload = json.loads(open(path).read())
    assert "coverage" in payload, (
        "ops reads payload['coverage'] — if this moves, the panel silently "
        "renders NOT REPORTED against a healthy engine"
    )
    # …and it is at the TOP level, not nested. Asserting where it is NOT is the
    # half that would have caught the price-action card's fixture.
    assert "coverage" not in (payload.get("derived") or {})
    cov = payload["coverage"]
    missing = OPS_COVERAGE_KEYS - set(cov)
    assert not missing, f"ops reads these and the engine stopped writing them: {missing}"
    assert cov["signals_seen"] == 1
    assert cov["partly_armed"] == 1
    assert cov["reasons"] == {live.OPEN_REFUSED_NO_SERIES: 1}


def test_sl_distance_source_is_in_the_ops_contract():
    """A column ops renders must be pinned on the side that writes it (#817)."""
    arm = _arm(_rising(60), "LONG", entry=160.0, sl=155.0, tp1=175.0)
    assert "sl_distance_source" in arm
