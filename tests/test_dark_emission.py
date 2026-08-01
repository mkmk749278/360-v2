"""The dark emission lane — the silent paths emitting, owner-only.

The safety property is the point of these tests, not a side note. A dark signal
that reaches ``SignalRouter`` reaches the paid Telegram channel, the FCM
``signals`` topic, the free channel, the app feed, ``_position_lock`` (which
would block a *real* signal on that symbol), and
``signal_dispatch.dispatch_signal_to_active_users`` — **real orders on real
users' keys**.

That is why the design is structural rather than conditional: a dark candidate
is diverted at the single ``signal_queue.put`` site, and the queue is the only
route to any of the six. The tests below pin exactly that, including the
inverse — that a *live* candidate still enqueues, because a safety property that
also blocks the money path is a bug, not a guarantee.
"""
from __future__ import annotations

import time

import pytest

from src import dark_emission as de


class _Sig:
    signal_id = "SIG-DARK-1"
    symbol = "MEANUSDT"
    channel = "360_SCALP"
    setup_class = "MEAN_REVERT"
    entry = 100.0
    stop_loss = 97.0
    tp1 = 106.0
    confidence = 71.5
    entry_regime = "TRENDING_UP"
    mc_context_key = "NY/MARKUP/NORMAL/BTC_NEUTRAL"
    valid_for_minutes = 60.0
    pair_admission = "CORE"

    class direction:
        value = "LONG"


@pytest.fixture(autouse=True)
def _on(monkeypatch):
    from src import runtime_tunables as rt

    monkeypatch.setattr(rt, "get", lambda key, *a, **k: True)
    de.reset_ledger(de.DarkLedger(path=""))
    yield
    de.reset_ledger(None)


# --------------------------------------------------------------------------- #
# Admission
# --------------------------------------------------------------------------- #


def test_a_loosened_gate_admits_an_enrolled_path():
    sig = _Sig()
    assert de.should_mark(sig, "setup_compat:regime_STRONG_TREND") is True
    assert de.should_mark(sig, "execution:overextended") is True


def test_a_gate_we_do_not_loosen_is_not_admitted():
    """min_confidence and the context floors stay live — they already carry
    KEEP/TUNE/DROP verdicts, and they are the last thing between a scored
    candidate and a feed."""
    assert de.should_mark(_Sig(), "min_confidence") is False
    assert de.should_mark(_Sig(), "context_floor:QUIET_COMPRESSION_BREAK") is False
    assert de.should_mark(_Sig(), "level_still_in_play") is False


def test_mover_trend_pullback_is_excluded():
    """Owner, 2026-07-31. It owns 64% of the delivered book and 24,327 of the
    37,782 pre-scoring rejects — admitting it makes the dark feed a second MTP
    feed, and is why no per-path budget was needed."""
    sig = _Sig()
    sig.setup_class = "MOVER_TREND_PULLBACK"
    assert de.should_mark(sig, "setup_compat:regime_STRONG_TREND") is False


def test_the_first_gate_to_catch_it_is_the_one_recorded():
    """A candidate can be caught by both loosened gates; the first is the one
    that would have killed it live, so the second must not overwrite it."""
    sig = _Sig()
    de.mark(sig, "setup_compat:regime_STRONG_TREND")
    assert de.should_mark(sig, "execution:overextended") is False
    assert getattr(sig, de.DARK_ATTR) == "setup_compat:regime_STRONG_TREND"


def test_nothing_is_admitted_while_the_lane_is_off(monkeypatch):
    from src import runtime_tunables as rt

    monkeypatch.setattr(rt, "get", lambda key, *a, **k: False)
    assert de.should_mark(_Sig(), "setup_compat:regime_STRONG_TREND") is False


# --------------------------------------------------------------------------- #
# The safety property — verified through the REAL scanner method
# --------------------------------------------------------------------------- #


def _scanner_source() -> str:
    import inspect

    import src.scanner as _scanner

    return inspect.getsource(_scanner)


def test_the_divert_sits_before_the_only_enqueue_site_in_the_real_scanner():
    """Asserted against the real source, not a re-implementation of it.

    A hand-written copy of this branch in a test would assert the author's
    assumption back at itself and go green over dead code (#798) — and the
    thing being asserted here is the one that keeps a dark signal away from
    real users' capital, so a test that could pass over a broken branch is
    worse than no test.

    ``signal_queue.put`` is the only route to ``SignalRouter``, and therefore
    the only route to the paid channel, FCM, the free channel, the app feed,
    ``_position_lock`` and ``signal_dispatch``. The divert must come first and
    must return.
    """
    src = _scanner_source()
    assert src.count("await self.signal_queue.put(sig)") == 1, (
        "a second enqueue site appeared — the dark divert now guards only one "
        "of them, and the other reaches real users"
    )
    divert = src.index("if dark_emission.is_dark(sig):")
    enqueue = src.index("await self.signal_queue.put(sig)")
    assert divert < enqueue, "the dark divert must precede the enqueue"
    branch = src[divert:enqueue]
    assert "return" in branch, "the dark branch must return, not fall through"
    assert "dark_emission.publish(sig)" in branch


def test_both_loosened_gates_carry_instead_of_rejecting_in_the_real_scanner():
    src = _scanner_source()
    for token in ("setup_compat:{_compat_token}", "execution:{_exec_token}"):
        assert f'dark_emission.should_mark(sig, f"{token}")' in src
        assert f'dark_emission.mark(sig, f"{token}")' in src


def test_no_other_module_can_route_a_dark_signal():
    """The router, the dispatcher and the push path must not have learned
    about dark signals — if they had, the property would be conditional
    (six correct skips) rather than structural (one branch)."""
    import inspect

    from src import push_notifications, signal_router
    from src.execution import signal_dispatch

    for mod in (signal_router, signal_dispatch, push_notifications):
        assert "dark_emission" not in inspect.getsource(mod), (
            f"{mod.__name__} references the dark lane — the safety property is "
            "supposed to be that it never has to"
        )


def test_is_dark_is_false_for_an_ordinary_signal():
    assert de.is_dark(_Sig()) is False


# --------------------------------------------------------------------------- #
# The ledger
# --------------------------------------------------------------------------- #


def test_a_published_row_carries_the_gate_that_would_have_killed_it():
    sig = _Sig()
    de.mark(sig, "setup_compat:regime_STRONG_TREND")
    assert de.publish(sig) is True
    (row,) = de.get_ledger().rows()
    assert row["dark_gate"] == "setup_compat:regime_STRONG_TREND"
    assert row["setup_class"] == "MEAN_REVERT"
    assert row["status"] == de.STATUS_OPEN
    # Scored confidence — a dark signal has been through the scoring engine and
    # every gate but the loosened one, which is what makes it different in kind
    # from a suppression stamp.
    assert row["confidence"] == pytest.approx(71.5)


def test_geometry_that_cannot_be_measured_is_refused_not_stored():
    """Refuse, don't clamp: a row with no tradeable geometry can never resolve,
    and storing it would show as a permanently-open dark trade."""
    sig = _Sig()
    sig.tp1 = 0.0
    de.mark(sig, "execution:overextended")
    assert de.publish(sig) is False
    assert de.get_ledger().rows() == []


def test_one_loud_path_cannot_evict_another_paths_rows():
    """Same lesson the suppression store just paid for: a shared ring makes the
    loudest population the only readable one."""
    ledger = de.DarkLedger(path="", per_path_max=3)
    de.reset_ledger(ledger)
    quiet = _Sig()
    quiet.setup_class = "RANGE_FADE"
    de.mark(quiet, "setup_compat:regime_WEAK_TREND")
    de.publish(quiet)
    for _ in range(50):
        loud = _Sig()
        loud.setup_class = "LIQUIDITY_SWEEP_REVERSAL"
        de.mark(loud, "execution:trigger_not_confirmed")
        de.publish(loud)
    setups = [r["setup_class"] for r in ledger.rows()]
    assert "RANGE_FADE" in setups
    assert setups.count("LIQUIDITY_SWEEP_REVERSAL") == 3


def test_a_schema_bump_drops_rows_rather_than_reinterpreting_them(tmp_path):
    import json

    path = str(tmp_path / "dark.json")
    with open(path, "w") as fh:
        json.dump(
            {"schema": de.LEDGER_SCHEMA + 1, "rows": [{"setup_class": "X"}]}, fh
        )
    ledger = de.DarkLedger(path=path)
    ledger.load()
    assert ledger.rows() == []


def test_the_ledger_writes_even_with_nothing_to_say(tmp_path):
    """An idle engine that writes no file reads to ops as 'the lane is not
    running' — a fault that is not happening (#832, caught minutes after
    deploy)."""
    path = str(tmp_path / "dark.json")
    ledger = de.DarkLedger(path=path)
    assert ledger.flush(force=True) is True
    import json

    payload = json.load(open(path))
    assert payload["schema"] == de.LEDGER_SCHEMA
    assert payload["rows"] == []


def test_publish_never_raises_into_the_scan_loop(monkeypatch):
    monkeypatch.setattr(de, "get_ledger", lambda: (_ for _ in ()).throw(RuntimeError()))
    sig = _Sig()
    de.mark(sig, "execution:overextended")
    assert de.publish(sig) is False


# --------------------------------------------------------------------------- #
# What the gate was holding up
# --------------------------------------------------------------------------- #


def test_a_none_anchor_no_longer_raises_into_the_scan_loop():
    """Found by carrying a candidate past the gate that had always killed it.

    ``getattr(signal, "far_reclaim_level", signal.entry)`` looks defensive and
    is not: the attribute is declared on ``Signal`` and defaults to None, so
    the default never fires and the comparison raises. It was unreachable while
    ``setup_compat`` killed every FAILED_AUCTION_RECLAIM candidate in a VOLATILE
    regime before scoring — a gate holding a bug up. Loosening a gate exposes
    the code it was protecting, which is a cost of this lane worth naming.
    """
    from src.signal_quality import (
        MarketState,
        SetupClass,
        execution_quality_check,
    )
    from src.smc import Direction

    class _S:
        entry = 100.0
        stop_loss = 97.0
        tp1 = 106.0
        direction = Direction.LONG
        far_reclaim_level = None
        pdc_breakout_level = None

    for setup in (SetupClass.FAILED_AUCTION_RECLAIM,
                  SetupClass.POST_DISPLACEMENT_CONTINUATION):
        # Would raise TypeError on the None anchor before the fix.
        result = execution_quality_check(
            _S(), {}, {}, setup, MarketState.VOLATILE_UNSUITABLE
        )
        assert result is not None


# --------------------------------------------------------------------------- #
# Forward resolution
# --------------------------------------------------------------------------- #


def _published(side="LONG", entry=100.0, sl=97.0, tp1=106.0, ts=1_700_000_000.0):
    sig = _Sig()
    sig.entry, sig.stop_loss, sig.tp1 = entry, sl, tp1
    sig.direction = type("_D", (), {"value": side})
    de.mark(sig, "setup_compat:regime_STRONG_TREND")
    de.publish(sig, now_ts=ts)
    return de.get_ledger()


def test_a_dark_row_resolves_to_tp1_with_an_R():
    ledger = _published()
    ohlc = {"high": [101.0, 107.0], "low": [99.5, 100.0], "close": [100.5, 106.5]}
    de.resolve_open(lambda *_: ohlc, now_ts=1_700_000_600.0, ledger=ledger)
    (row,) = ledger.rows()
    assert row["status"] == de.STATUS_TP1
    assert row["r_multiple"] == pytest.approx(6.0 / 3.0)
    assert row["ambiguous_bar"] is False


def test_a_same_bar_touch_resolves_pessimistically_and_is_flagged():
    """OHLC cannot order two touches inside one bar — so the row says it is a
    judgement rather than being averaged in as a fact."""
    ledger = _published()
    ohlc = {"high": [107.0], "low": [96.0], "close": [100.0]}
    de.resolve_open(lambda *_: ohlc, now_ts=1_700_000_600.0, ledger=ledger)
    (row,) = ledger.rows()
    assert row["status"] == de.STATUS_SL
    assert row["ambiguous_bar"] is True


def _quiet_window(bars: int):
    """A walked window in which nothing touched either level."""
    return {"high": [101.0] * bars, "low": [99.0] * bars, "close": [100.0] * bars}


def test_a_row_past_the_horizon_expires_at_0R_not_as_a_loss():
    """An expiry is the mechanism doing nothing, not losing. Counting it as a
    loss is the #685 fabrication class.

    The window here is the ~420 bars a 7-hour lifetime actually produces. The
    original fixture passed one bar, which no production path ever hands the
    resolver and which the coverage guard below now correctly refuses to call an
    expiry.
    """
    ledger = _published()
    de.resolve_open(
        lambda *_: _quiet_window(420),
        now_ts=1_700_000_000.0 + 7 * 3600.0,
        ledger=ledger,
    )
    (row,) = ledger.rows()
    assert row["status"] == de.STATUS_EXPIRED
    assert row["r_multiple"] == 0.0
    assert row["window_coverage"] >= de.MIN_WINDOW_COVERAGE


def test_an_untouched_row_whose_walk_missed_the_window_is_not_an_expiry():
    """0R on an expiry is a claim that the window was walked and nothing
    happened, and that claim is only as good as the walk.

    Owner data 2026-08-01: ROBOUSDT expired on 309 bars of a 362-minute window
    and ARBUSDT on 329 of 365 — 89 minutes of unexamined bars reported as "the
    setup did nothing". A touch inside them would have been booked as a zero,
    which is the fabrication class arriving as a rate rather than as a number.
    Terminal and unscored is the honest end.
    """
    ledger = _published()
    de.resolve_open(
        lambda *_: _quiet_window(300),          # 300 bars of a 420-bar window
        now_ts=1_700_000_000.0 + 7 * 3600.0,
        ledger=ledger,
    )
    (row,) = ledger.rows()
    assert row["status"] == de.STATUS_INSUFFICIENT
    assert row["insufficient_reason"] == de.INSUFFICIENT_PARTIAL_WINDOW
    # Unscored, so no rate anywhere can be divided by it.
    assert row.get("r_multiple") is None
    assert row["window_coverage"] < de.MIN_WINDOW_COVERAGE


def test_partial_window_is_counted_apart_from_a_missing_series():
    """Different causes, different fixes: a series that never arrived and a
    series with holes must never be pooled into one number."""
    ledger = _published()
    tally = de.resolve_open(
        lambda *_: _quiet_window(300),
        now_ts=1_700_000_000.0 + 7 * 3600.0,
        ledger=ledger,
    )
    assert tally["partial_window"] == 1
    assert tally["insufficient"] == 1
    assert tally["expired"] == 0

    rollup = de.summary(ledger=ledger)
    (agg,) = rollup.values()
    assert agg["insufficient_partial_window"] == 1
    assert agg["insufficient_no_walk"] == 0
    # Kept out of `resolved` so no rate is divided by a row nobody scored.
    assert agg["resolved"] == 0


def test_a_touched_row_is_scored_however_short_its_walk():
    """Coverage gates the *expiry* verdict only. A row that hit a level was
    decided by the market, and the bars after the touch are irrelevant — the
    walk stops there by design, so its bar count is where the outcome was, not
    how much was examined."""
    ledger = _published()
    ohlc = {"high": [107.0] * 3, "low": [99.0] * 3, "close": [100.0] * 3}
    de.resolve_open(
        lambda *_: ohlc, now_ts=1_700_000_000.0 + 7 * 3600.0, ledger=ledger
    )
    (row,) = ledger.rows()
    assert row["status"] == de.STATUS_TP1
    assert row["r_multiple"] is not None


def test_a_row_with_no_candles_stays_open_and_is_counted():
    """An unresolved row must never be scored: a loss-selected sample is worse
    than no sample, because it looks like an answer (#832)."""
    ledger = _published()
    tally = de.resolve_open(lambda *_: None, now_ts=1_700_000_600.0, ledger=ledger)
    (row,) = ledger.rows()
    assert row["status"] == de.STATUS_OPEN
    assert row["r_multiple"] is None
    assert tally["no_candles"] == 1


def test_the_summary_reports_win_rate_over_decided_rows_only():
    ledger = de.DarkLedger(path="")
    de.reset_ledger(ledger)
    for tp in (True, True, False):
        sig = _Sig()
        sig.direction = type("_D", (), {"value": "LONG"})
        de.mark(sig, "setup_compat:regime_STRONG_TREND")
        de.publish(sig, now_ts=1_700_000_000.0)
    rows = ledger.rows()
    rows[0].update({"status": de.STATUS_TP1, "r_multiple": 2.0})
    rows[1].update({"status": de.STATUS_SL, "r_multiple": -1.0})
    rows[2].update({"status": de.STATUS_EXPIRED, "r_multiple": 0.0})
    agg = de.summary(ledger)["MEAN_REVERT"]
    assert agg["resolved"] == 3 and agg["expired"] == 1
    # 1 win of 2 DECIDED, not 1 of 3 — the expiry is neither.
    assert agg["win_rate"] == pytest.approx(0.5)
    assert agg["avg_r"] == pytest.approx((2.0 - 1.0 + 0.0) / 3.0)


def test_an_open_row_is_not_pooled_into_the_verdict():
    ledger = _published()
    agg = de.summary(ledger)["MEAN_REVERT"]
    assert agg["open"] == 1 and agg["resolved"] == 0
    assert agg["avg_r"] is None and agg["win_rate"] is None


# --------------------------------------------------------------------------- #
# Currency of the measurement — which bar was last consumed, and when
#
# A dark row's ops page prints a live price beside an open row. That is only
# honest if the row can say when it was last advanced: the file's age, the row's
# age and the price feed's age are three clocks, and #108 was this repo
# collapsing them into one on the SAR live tab.
# --------------------------------------------------------------------------- #


def _stamped_window(start_ms, bars):
    """A window in the shape ``slice_window`` produces: bars plus their times."""
    return {
        "high": [b[0] for b in bars],
        "low": [b[1] for b in bars],
        "close": [b[2] for b in bars],
        "open_time": [start_ms + i * 60_000.0 for i in range(len(bars))],
    }


def test_an_advanced_row_stamps_the_bar_it_last_consumed():
    ts = 1_700_000_000.0
    ledger = _published(ts=ts)
    now = ts + 180.0
    window = _stamped_window(ts * 1000.0, [(101.0, 99.5, 100.5), (101.5, 99.8, 101.0)])
    de.resolve_open(lambda *_: window, now_ts=now, ledger=ledger)
    (row,) = ledger.rows()
    assert row["status"] == de.STATUS_OPEN
    assert row["last_bar_ms"] == pytest.approx(ts * 1000.0 + 60_000.0)
    assert row["last_resolved_at"] == now
    assert row["resolve_misses"] == 0
    # Two bars consumed, three minutes elapsed: one bar behind, not stalled.
    assert row["bars_behind"] == pytest.approx(1.0)
    assert row["stalled"] is False


def test_a_row_whose_bars_stopped_arriving_is_marked_stalled_on_the_row():
    """The tally says the population is fine; only the row can say that THIS
    one stopped advancing (#815)."""
    ts = 1_700_000_000.0
    ledger = _published(ts=ts)
    # Bars exist but end 40 minutes ago — the frozen-feed / rotated-out shape.
    window = _stamped_window(ts * 1000.0, [(101.0, 99.5, 100.5)])
    de.resolve_open(lambda *_: window, now_ts=ts + 2400.0, ledger=ledger)
    (row,) = ledger.rows()
    assert row["stalled"] is True
    assert row["bars_behind"] > de.STALE_BARS


def test_a_missed_cycle_counts_on_the_row_and_leaves_the_verdict_alone():
    ts = 1_700_000_000.0
    ledger = _published(ts=ts)
    for _ in range(2):
        de.resolve_open(lambda *_: None, now_ts=ts + 600.0, ledger=ledger)
    (row,) = ledger.rows()
    assert row["resolve_misses"] == 2
    assert row["resolve_miss_reason"] == de.MISS_NO_CANDLES
    assert row["last_resolved_at"] is None      # never advanced, never pretended to
    assert row["stalled"] is True
    assert row["status"] == de.STATUS_OPEN and row["r_multiple"] is None


def test_a_fetch_that_raises_is_named_apart_from_an_empty_series():
    """Different causes, different fixes — pooling them is how one hides."""
    ledger = _published()

    def _boom(*_):
        raise RuntimeError("store went away")

    de.resolve_open(_boom, now_ts=1_700_000_600.0, ledger=ledger)
    (row,) = ledger.rows()
    assert row["resolve_miss_reason"] == de.MISS_FETCH_ERROR


def test_a_row_that_can_never_be_walked_retires_as_insufficient_not_expired():
    """The horizon test lives behind a successful walk, so a row whose candles
    die never reached it and sat OPEN forever. INSUFFICIENT is terminal and
    deliberately unscored: an expiry is a walked window where nothing happened,
    this is the absence of a measurement."""
    ts = 1_700_000_000.0
    ledger = _published(ts=ts)
    tally = de.resolve_open(lambda *_: None, now_ts=ts + 7 * 3600.0, ledger=ledger)
    (row,) = ledger.rows()
    assert row["status"] == de.STATUS_INSUFFICIENT
    assert tally["insufficient"] == 1
    # Not 0R — that is the expiry's honest score, and this row earned no score.
    assert row["r_multiple"] is None and row["pnl_pct"] is None


def test_insufficient_rows_are_counted_apart_from_resolved_ones():
    ledger = _published()
    (row,) = ledger.rows()
    row.update({"status": de.STATUS_INSUFFICIENT})
    agg = de.summary(ledger)["MEAN_REVERT"]
    assert agg["insufficient"] == 1
    assert agg["resolved"] == 0 and agg["win_rate"] is None


def test_the_resolve_cycle_writes_the_file_even_when_nothing_changed(tmp_path):
    """`flush()` only persisted when something changed, so a lane with no open
    rows stopped writing and ops read STALE — a fault that was not happening.
    The ledger's own docstring claimed this was fixed; it was not."""
    path = str(tmp_path / "dark.json")
    ledger = de.DarkLedger(path=path)
    de.reset_ledger(ledger)
    de.resolve_open(lambda *_: None, now_ts=1_700_000_600.0, ledger=ledger)
    import os

    assert os.path.exists(path)


def test_the_sl_denominator_is_stamped_where_it_becomes_true():
    """Any reader turning an unrealized move into R divides by this. Stamping it
    at publish keeps the denominator the engine's rather than one ops re-derived
    from a rounded entry."""
    ledger = _published(entry=100.0, sl=97.0)
    (row,) = ledger.rows()
    assert row["sl_distance_pct"] == pytest.approx(3.0)


def test_a_window_without_timestamps_is_walked_but_stamps_nothing():
    """A missing stamp is not a pass: the row reads `unknown`, never `current`."""
    ledger = _published()
    ohlc = {"high": [101.0], "low": [99.0], "close": [100.0]}
    de.resolve_open(lambda *_: ohlc, now_ts=1_700_000_600.0, ledger=ledger)
    (row,) = ledger.rows()
    assert row["bars_seen"] == 1                 # walked
    assert row["last_bar_ms"] is None            # but undatable
    assert row["stalled"] is None                # unknown, not False


# --------------------------------------------------------------------------- #
# The window itself — located by timestamp, never by elapsed-time arithmetic
# --------------------------------------------------------------------------- #


def _store_candles(start_ms, n, *, pad_times=False):
    """The store's real shape: numpy arrays, `open_time` in ms (NaN when the
    bucket predates timestamp tracking)."""
    import numpy as np

    times = np.arange(n, dtype=np.float64) * 60_000.0 + start_ms
    if pad_times:
        times[:] = np.nan
    return {
        "high": np.full(n, 101.0),
        "low": np.full(n, 99.0),
        "close": np.full(n, 100.0),
        "open_time": times,
    }


def test_the_window_starts_at_the_bar_containing_the_stamp():
    start_ms = 1_700_000_000_000.0
    candles = _store_candles(start_ms, 10)
    # Emitted 30s into bar 6.
    since = (start_ms + 6 * 60_000.0 + 30_000.0) / 1000.0
    window = de.slice_window(candles, since)
    assert window["open_time"][0] == pytest.approx(start_ms + 6 * 60_000.0)
    assert len(window["high"]) == 4


def test_a_frozen_series_yields_the_bars_it_has_rather_than_the_bars_it_should():
    """The elapsed-time slice this replaces would hand back `elapsed // 60` bars
    counted from the end — for a feed that stopped an hour ago, an hour of the
    wrong bars, with nothing in the result able to say so."""
    start_ms = 1_700_000_000_000.0
    candles = _store_candles(start_ms, 5)        # series ends at bar 4
    since = (start_ms + 2 * 60_000.0) / 1000.0
    window = de.slice_window(candles, since)
    assert len(window["high"]) == 3
    # And the last bar is datable, which is what lets the row be called stalled.
    assert window["open_time"][-1] == pytest.approx(start_ms + 4 * 60_000.0)


def test_a_window_whose_history_rolled_off_is_refused():
    start_ms = 1_700_000_000_000.0
    candles = _store_candles(start_ms, 5)
    since = (start_ms - 3600_000.0) / 1000.0     # stamp precedes the array
    assert de.slice_window(candles, since) is None


def test_padded_timestamps_downgrade_the_window_instead_of_blanking_it():
    """The first cut refused, and on 2026-07-31 that turned a snapshot loader
    which dropped `open_time` into a page reporting `no candles` on every row,
    core pairs included. Refuse the *claim*, not the measurement."""
    start_ms = 1_700_000_000_000.0
    candles = _store_candles(start_ms, 5, pad_times=True)
    window = de.slice_window(candles, time.time() - 120.0)
    assert window is not None
    assert "open_time" not in window, "an undated window must not claim a time"
    assert window["undated_reason"] == "all_timestamps_padded"
    assert len(window["high"]) >= 1


def test_a_bucket_with_no_timestamp_series_at_all_still_walks():
    candles = _store_candles(1_700_000_000_000.0, 5)
    candles.pop("open_time")
    window = de.slice_window(candles, time.time() - 120.0)
    assert window is not None and window["undated_reason"] == "no_timestamps"


def test_a_nan_prefix_is_searched_over_its_finite_tail_only():
    """The restored history is NaN and the bars since boot are real, so the
    array is not sorted — searchsorted over the whole of it is undefined, not
    merely imprecise."""
    import numpy as np

    start_ms = 1_700_000_000_000.0
    candles = _store_candles(start_ms, 10)
    candles["open_time"][:6] = np.nan          # restored, undatable history
    # A stamp inside the finite tail: located exactly, and dated.
    since = (start_ms + 7 * 60_000.0 + 10_000.0) / 1000.0
    window = de.slice_window(candles, since)
    assert window["open_time"][0] == pytest.approx(start_ms + 7 * 60_000.0)
    assert len(window["high"]) == 3


def test_a_stamp_inside_the_undated_prefix_walks_undated():
    """The row emitted before the restart. Its bars exist; their times do not."""
    import numpy as np

    start_ms = 1_700_000_000_000.0
    candles = _store_candles(start_ms, 10)
    candles["open_time"][:6] = np.nan
    window = de.slice_window(candles, (start_ms + 2 * 60_000.0) / 1000.0)
    assert window["undated_reason"] == "stamp_before_timestamps"
    assert "open_time" not in window


def test_a_ragged_series_is_refused_because_index_i_is_not_bar_i():
    import numpy as np

    candles = _store_candles(1_700_000_000_000.0, 5)
    candles["low"] = np.full(4, 99.0)
    assert de.slice_window(candles, 1_700_000_000.0) is None


def test_a_ragged_timestamp_series_downgrades_rather_than_refusing():
    """Ragged OHLC means the bars are unusable; ragged timestamps mean only the
    times are. Different faults, different answers."""
    import numpy as np

    candles = _store_candles(1_700_000_000_000.0, 5)
    candles["open_time"] = np.full(3, 1_700_000_000_000.0)
    window = de.slice_window(candles, time.time() - 120.0)
    assert window is not None and window["undated_reason"] == "no_timestamps"


def test_an_undated_advance_is_not_a_miss_but_never_reads_as_current():
    ts = 1_700_000_000.0
    ledger = _published(ts=ts)
    ohlc = {"high": [101.0], "low": [99.0], "close": [100.0],
            "undated_reason": "no_timestamps"}
    tally = de.resolve_open(lambda *_: ohlc, now_ts=ts + 600.0, ledger=ledger)
    (row,) = ledger.rows()
    assert row["resolve_misses"] == 0            # it advanced
    assert row["last_resolved_at"] == ts + 600.0
    assert row["window_undated_reason"] == "no_timestamps"
    assert row["stalled"] is None                # unknown, never False
    assert row["bars_behind"] is None
    assert tally["undated"] == 1


def test_the_probe_fails_when_the_whole_lane_goes_undated(monkeypatch):
    """A lane advancing on undatable windows is not stalled and is not healthy.
    Nothing watched for it, and the owner found it on a printed page."""
    monkeypatch.setattr(de, "enabled", lambda: True)
    ts = 1_700_000_000.0
    ledger = _published(ts=ts)
    ohlc = {"high": [101.0], "low": [99.0], "close": [100.0],
            "undated_reason": "no_timestamps"}
    de.resolve_open(lambda *_: ohlc, now_ts=ts + 600.0, ledger=ledger)
    ok, detail = de.resolution_health(ledger, now_ts=ts + 600.0)
    assert ok is False and "cannot be dated" in detail


def test_slice_window_never_boolean_tests_a_numpy_array():
    """`if not arr` raises on a numpy array — the class that killed 8 features
    silently on 2026-07-14. Driving it with the store's real arrays is the
    check."""
    candles = _store_candles(1_700_000_000_000.0, 3)
    assert de.slice_window(candles, 1_700_000_000.0) is not None
    assert de.slice_window({}, 1_700_000_000.0) is None
    assert de.slice_window(None, 1_700_000_000.0) is None


# --------------------------------------------------------------------------- #
# The probe: keyed on the rows owed a verdict
# --------------------------------------------------------------------------- #


def test_an_idle_or_disabled_lane_answers_true_with_a_reason(monkeypatch):
    """Not a raise: a PredicateProbe converts one into a fail_open record, and
    filling that counter with non-failures is how a real one stops standing
    out."""
    monkeypatch.setattr(de, "enabled", lambda: False)
    ok, detail = de.resolution_health(de.DarkLedger(path=""))
    assert ok is True and "disabled" in detail

    monkeypatch.setattr(de, "enabled", lambda: True)
    ok, detail = de.resolution_health(de.DarkLedger(path=""))
    assert ok is True and "owed a verdict" in detail


def test_the_probe_fails_on_a_row_that_stopped_advancing(monkeypatch):
    monkeypatch.setattr(de, "enabled", lambda: True)
    ts = 1_700_000_000.0
    ledger = _published(ts=ts)
    ok, _ = de.resolution_health(ledger, now_ts=ts + 60.0)
    assert ok is True                      # inside the first-resolve grace
    for _ in range(de.STALL_MISS_LIMIT):
        de.resolve_open(lambda *_: None, now_ts=ts + 600.0, ledger=ledger)
    ok, detail = de.resolution_health(ledger, now_ts=ts + 600.0)
    assert ok is False
    assert "not being advanced" in detail and "MEANUSDT" in detail


def test_the_probe_ignores_a_row_that_has_already_resolved(monkeypatch):
    monkeypatch.setattr(de, "enabled", lambda: True)
    ts = 1_700_000_000.0
    ledger = _published(ts=ts)
    (row,) = ledger.rows()
    row.update({"status": de.STATUS_SL, "resolve_misses": 9, "stalled": True})
    ok, _ = de.resolution_health(ledger, now_ts=ts + 10_000.0)
    assert ok is True


# --------------------------------------------------------------------------- #
# SR_FLIP longs (owner, 2026-07-31)
#
# The long side has been disabled since 2026-06-29 on a measured −21.8% / 19%
# win, leaving only a `[SHADOW] SR_FLIP_LONG_V2_WOULD_FIRE` log line — a
# candidate count with no outcome, which cannot settle a re-enable. Routing it
# through the dark lane gives it a forward-resolved TP1/SL and an R.
#
# It is also the first *evaluator-internal* disable this lane carries, and that
# is the risk: unlike setup_compat/execution it fires long before the gate
# chain, so the candidate must be CARRIED (not published there), and an unmarked
# carry would reach `signal_queue.put` and put the −21.8% path in front of paid
# subscribers with no owner sign-off.
# --------------------------------------------------------------------------- #


def _sr_flip_source() -> str:
    import inspect

    import src.channels.scalp as _scalp

    return inspect.getsource(_scalp)


def test_the_long_disable_is_a_loosened_gate():
    assert de.is_loosened_gate(de.GATE_SR_FLIP_LONG) is True
    assert de.will_admit("SR_FLIP_RETEST", de.GATE_SR_FLIP_LONG) is True


def test_the_lane_being_off_means_the_long_stays_rejected(monkeypatch):
    """The tourniquet holds when the measurement is not there to catch it —
    otherwise turning the dark lane off silently re-enables a losing long."""
    from src import runtime_tunables as rt

    monkeypatch.setattr(rt, "get", lambda key, *a, **k: False)
    assert de.will_admit("SR_FLIP_RETEST", de.GATE_SR_FLIP_LONG) is False


def test_an_excluded_path_is_still_excluded_through_the_signal_free_check():
    assert de.will_admit("MOVER_TREND_PULLBACK", de.GATE_SR_FLIP_LONG) is False


def test_the_evaluator_carries_rather_than_publishing_at_the_disable():
    """Asserted against the real evaluator source. Publishing at the disable
    point would produce rows that never ran scoring, MTF, min_confidence, the
    context floors or staleness — while the page's first paragraph says every
    row did. That claim is the difference between this feed and the suppression
    audit."""
    src = _sr_flip_source()
    disable = src.index("if not SR_FLIP_LONG_ENABLED:")
    ret = src.index("if _carry_long_dark:")
    assert disable < ret
    branch = src[disable:ret]
    assert "dark_emission.publish" not in branch, (
        "a dark row published from inside the evaluator has not been through "
        "the gate chain the page says it has"
    )
    assert "will_admit" in branch


def test_an_unmarkable_carry_is_refused_rather_than_emitted():
    """The fail-closed half. `will_admit` answered sixty lines earlier and is
    not permission — the lane can be toggled off mid-evaluation, and `mark`
    records a failure rather than raising."""
    src = _sr_flip_source()
    guard = src.index("if _carry_long_dark:")
    tail = src[guard:guard + 400]
    assert "dark_emission.mark(sig, dark_emission.GATE_SR_FLIP_LONG)" in tail
    assert "if not dark_emission.is_dark(sig):" in tail
    assert 'return self._reject("long_disabled")' in tail, (
        "an unmarked carry must not fall through to the enqueue site"
    )


def test_a_marked_long_is_diverted_by_the_same_single_branch():
    """No second divert site: the enqueue guard is `is_dark`, which the mark
    satisfies, so the long side inherits the existing safety property rather
    than adding a parallel one that could drift from it."""
    sig = _Sig()
    sig.setup_class = "SR_FLIP_RETEST"
    de.mark(sig, de.GATE_SR_FLIP_LONG)
    assert de.is_dark(sig) is True
    assert de.publish(sig) is True
    (row,) = de.get_ledger().rows()
    assert row["dark_gate"] == de.GATE_SR_FLIP_LONG
    assert row["setup_class"] == "SR_FLIP_RETEST"


def test_the_short_side_is_untouched():
    """SHORT nets +5.1% and emits live. Nothing here may divert it."""
    src = _sr_flip_source()
    assert "_carry_long_dark = False" in src
    carry = src.index("_carry_long_dark = True")
    long_branch = src.rindex("if direction == Direction.LONG:", 0, carry)
    assert long_branch < carry, "the carry must sit inside the LONG branch"


def test_an_in_memory_ledger_writes_nothing_and_records_no_failure(tmp_path, monkeypatch):
    """`path=""` means "do not persist". The atomic write used to run anyway:
    it created `.tmp` in the process's cwd — the repo root under pytest, where
    it was committed on every branch and conflicted on every merge — and then
    raised into `fail_open` on `os.replace(".tmp", "")`, filling the counter
    that exists to make real failures stand out."""
    from src import fail_open

    monkeypatch.chdir(tmp_path)
    before = len(fail_open.snapshot()) if hasattr(fail_open, "snapshot") else 0
    ledger = de.DarkLedger(path="")
    ledger.add({"symbol": "AAAUSDT", "setup_class": "MEAN_REVERT", "status": "OPEN"})
    ledger.flush(force=True)
    assert list(tmp_path.iterdir()) == [], "an in-memory ledger touched the disk"
    if hasattr(fail_open, "snapshot"):
        assert len(fail_open.snapshot()) == before
