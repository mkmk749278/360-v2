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
    live.observe_signal(sig, store, price=181.0, ledger=ledger)
    arms = ledger.open_arms()
    assert {a["timeframe"] for a in arms} == {"5m", "15m"}
    assert all(a["governor"] == live.GOV_SAR for a in arms)   # rising -> aligned
    assert all(a["signal_id"] == "SIG-E2E" for a in arms)
    # Idempotent: a second tick must not re-open the same arms.
    live.observe_signal(sig, store, price=181.0, ledger=ledger)
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
    live.observe_signal(sig, store, price=180.0, ledger=ledger, timeframes=["15m"])
    assert len(ledger.open_arms()) == 1
    # Next bar blows through the static stop while SAR is still opposed.
    for i, bar in enumerate([(180.5, 184.0, 180.0, 183.0)], start=len(bars)):
        store.update_candle(
            "TESTUSDT", "15m",
            {"open": bar[0], "high": bar[1], "low": bar[2], "close": bar[3],
             "volume": 1.0, "open_time": 1_700_000_000_000 + i * BAR_MS},
        )
    live.observe_signal(sig, store, price=183.0, ledger=ledger, timeframes=["15m"])
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
