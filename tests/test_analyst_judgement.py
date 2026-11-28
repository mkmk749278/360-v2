"""Phase 3: size, the BTC forecast, day-clustered confidence, stop diagnostics."""
from __future__ import annotations

import json
import sqlite3

import numpy as np
import pytest

from src import analyst_judgement as J
from src import analyst_plan as P
from src import analyst_walk as W
from src import diag_catalog
from tests.test_analyst_plan import ADMIT, NOW as PNOW, _plan, _setup_engine
from tests.test_analyst_walk import NOW, _bucket, _setup


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    led = P.Ledger(str(tmp_path / "plans.sqlite"))
    monkeypatch.setattr(P, "_ledger", led)
    return led


# ── size ────────────────────────────────────────────────────────────────────

def test_size_is_stored_and_a_size_off_the_scale_is_a_named_reject(ledger):
    eng, ids = _setup_engine()
    assert P.submit(_plan(ids, size=0), eng, now=PNOW, admission=ADMIT)["n_accepted"] == 1
    con = sqlite3.connect(ledger.path)
    assert con.execute("SELECT size FROM setups").fetchone()[0] == 0.0
    bad = P.submit(_plan(ids, size=0.7), eng, now=PNOW + 60, admission=ADMIT)["setups"][0]
    assert bad["reason"] == "schema" and "size" in bad["detail"]


def test_three_size_populations_never_pool():
    pairs = ([(2.0, "2026-11-01", 1.0), (1.0, "2026-11-01", -1.0)]
             + [(0.0, "2026-11-01", 3.0)] + [(None, "2026-11-01", -2.0)])
    out = J.size_split(pairs)
    assert out["active"]["n"] == 2 and out["active"]["units"] == 3.0
    assert out["active"]["size_weighted_avg_pct"] == pytest.approx((2 - 1) / 3, abs=1e-4)
    assert out["active"]["unweighted_avg_pct"] == 0.0
    assert out["passed"] == {"n": 1, "avg_pct": 3.0, "day_clustered": out["passed"]["day_clustered"]}
    assert out["unsized"]["n"] == 1


# ── forecast ────────────────────────────────────────────────────────────────

def test_forecast_parse_keeps_good_horizons_and_names_bad_ones():
    fc, dropped = J.parse_forecast({"btc_4h": {"dir": "down", "p": 0.6, "invalidation": 61000},
                                    "btc_12h": {"dir": "sideways", "p": 0.5},
                                    "btc_1d": {"dir": "up", "p": 0.5}})
    assert list(fc) == ["btc_4h"] and fc["btc_4h"]["band_pct"] == 0.7
    assert len(dropped) == 2
    assert J.parse_forecast({"btc_4h": {"dir": "up", "p": 0.99}})[0] is None


def test_a_forecast_is_stored_with_the_btc_price_and_never_blocks_setups(ledger):
    eng, ids = _setup_engine()
    plan = _plan(ids)
    plan["forecast"] = {"btc_12h": {"dir": "up", "p": 0.55}, "btc_4h": {"dir": "x"}}
    out = P.submit(plan, eng, now=PNOW, admission=ADMIT)
    assert out["n_accepted"] == 1 and out["forecast_stored"] == ["btc_12h"]
    assert out["forecast_dropped"]
    con = sqlite3.connect(ledger.path)
    fj, = con.execute("SELECT forecast_json FROM plans").fetchone()
    assert json.loads(fj)["btc_12h"]["dir"] == "up"


def _btc(t0, closes):
    t = (t0 + 300.0 * np.arange(len(closes))) * 1000.0
    return {"open_time": t, "close": np.asarray(closes, dtype=float)}


def test_forecasts_are_scored_at_the_horizon_close(ledger):
    con = ledger._connect()
    t0 = 1_800_000_000.0
    fc = {"btc_4h": {"dir": "down", "p": 0.6, "horizon_s": 14400.0, "band_pct": 0.7,
                     "invalidation": None}}
    with con:
        con.execute("INSERT INTO plans (plan_id, submitted_at, bias, forecast_json, "
                    "btc_at_submit) VALUES ('p', ?, 'risk_off', ?, 60000)",
                    (t0, json.dumps(fc)))
    closes = [60000.0] * 60                  # 5h of 5m bars
    closes[47] = 59400.0                     # the bar closing at t0 + 4h: -1.0%
    assert J.score_forecasts(con, _btc(t0, closes), t0 + 3 * 3600) == 0, "not due yet"
    with con:
        assert J.score_forecasts(con, _btc(t0, closes), t0 + 5 * 3600) == 1
    sc = json.loads(con.execute("SELECT forecast_scored_json FROM plans").fetchone()[0])
    assert sc["btc_4h"]["outcome"] == "down" and sc["btc_4h"]["ret_pct"] == -1.0
    s = J.forecast_summary(con)["btc_4h"]
    assert s["n"] == 1 and s["hit_rate"] == 1.0
    # p 0.6 on the right call: (0.4)^2 + 2 x (0.2)^2
    assert s["brier"] == pytest.approx(0.24)


def test_a_horizon_with_no_bar_is_insufficient_not_guessed(ledger):
    con = ledger._connect()
    t0 = 1_800_000_000.0
    fc = {"btc_4h": {"dir": "up", "p": 0.5, "horizon_s": 14400.0, "band_pct": 0.7,
                     "invalidation": None}}
    with con:
        con.execute("INSERT INTO plans (plan_id, submitted_at, bias, forecast_json, "
                    "btc_at_submit) VALUES ('p', ?, 'neutral', ?, 60000)", (t0, json.dumps(fc)))
        J.score_forecasts(con, _btc(t0, [60000.0] * 10), t0 + 5 * 3600)
    sc = json.loads(con.execute("SELECT forecast_scored_json FROM plans").fetchone()[0])
    assert sc["btc_4h"] == {"status": "insufficient", "reason": "no_bar_at_horizon"}


# ── day-clustered confidence ────────────────────────────────────────────────

def test_the_interval_resamples_days_and_refuses_too_few():
    assert J.day_clustered_ci([("d1", 1.0), ("d2", 2.0)])["reason"].startswith("fewer")
    pairs = [(f"d{i}", v) for i in range(10) for v in (i - 4.5, i - 4.5)]
    out = J.day_clustered_ci(pairs)
    lo, hi = out["ci95_pct"]
    assert out["n_days"] == 10 and lo < out["mean_per_setup_pct"] < hi
    # One day of 20 identical setups is one observation, not twenty.
    one_day = [("d0", 5.0)] * 20 + [(f"d{i}", -1.0) for i in range(1, 6)]
    wide = J.day_clustered_ci(one_day)["ci95_pct"]
    assert wide[1] - wide[0] > 3.0


# ── stop diagnostics ────────────────────────────────────────────────────────

def test_a_stop_on_a_bar_that_also_touched_the_target_is_flagged():
    cd = _bucket([(100, 100, 98.9, 99.5), (99.5, 104, 96, 100)])
    a = W.walk_setup(_setup(), cd, NOW)["analyst"]
    assert a["exit_reason"] == "stop" and a["stop_ambiguous"] == 1


def test_target_after_stop_is_known_only_when_the_bars_cover_the_window():
    bars = [(100, 100, 98.9, 99.5), (99.5, 99.6, 96.5, 97.0)] + [(97, 97.5, 96.8, 97)] * 5
    a = W.walk_setup(_setup(), _bucket(bars + [(97, 103.5, 97, 103)]), NOW)["analyst"]
    assert a["exit_reason"] == "stop" and a["target_after_stop"] == 1
    a = W.walk_setup(_setup(), _bucket(bars), NOW)["analyst"]
    assert a["target_after_stop"] is None, "bars end before the 12h window: unknown, not no"
    long_flat = bars + [(97, 97.5, 96.8, 97)] * 150
    a = W.walk_setup(_setup(), _bucket(long_flat), NOW)["analyst"]
    assert a["target_after_stop"] == 0


def test_the_outcomes_carry_the_judgement_block(ledger):
    eng, ids = _setup_engine()
    P.submit(_plan(ids, size=1.5), eng, now=PNOW, admission=ADMIT)
    res = diag_catalog.run("read.analyst_outcomes", eng, {})["result"]
    j = res["judgement"]
    assert set(j) == {"size", "forecast", "stop_diagnostics"}
    assert "day_clustered" in res["by_arm"]["analyst"]


def test_a_resubmitted_plan_scores_one_forecast_not_two(ledger):
    con = ledger._connect()
    t0 = 1_800_000_000.0
    fc = json.dumps({"btc_4h": {"dir": "range", "p": 0.55, "horizon_s": 14400.0,
                                "band_pct": 0.7, "invalidation": None}})
    with con:
        for pid, t in (("first", t0), ("resubmit", t0 + 120), ("next_hour", t0 + 3600)):
            con.execute("INSERT INTO plans (plan_id, submitted_at, source, bias, forecast_json, "
                        "btc_at_submit) VALUES (?, ?, 'mcp:a', 'neutral', ?, 60000)",
                        (pid, t, fc))
        J.score_forecasts(con, _btc(t0, [60000.0] * 70), t0 + 5.5 * 3600)
    sup = {r[0]: r[1] for r in con.execute("SELECT plan_id, forecast_superseded FROM plans")}
    assert sup == {"first": 1, "resubmit": None, "next_hour": None}
    assert J.forecast_summary(con)["btc_4h"]["n"] == 2


def test_the_open_book_counts_units_and_keeps_history_apart():
    now = 1_800_000_000.0
    rows = [{"symbol": s, "side": side, "state": "pending", "submitted_at": now - 600,
             "entries": [{"price": 1.0}], "stop": 0.9, "targets": [1.1], "size": size}
            for s, side, size in (("A", "long", None), ("B", "long", None),
                                  ("C", "long", 1.5), ("D", "short", 0.0),
                                  ("E", "short", 0.5))]
    b = W.book(rows, now)
    assert b["by_side"] == {"long": 3, "short": 2}
    assert b["units_by_side"] == {"long": 1.5, "short": 0.5}
    assert b["unsized_by_side"] == {"long": 2, "short": 0}
    assert b["passed_by_side"] == {"long": 0, "short": 1}
