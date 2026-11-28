"""Phase 4: exit arms on the analyst's own fills (runner_24h, btc_invalidated_exit)."""
from __future__ import annotations

import json
import sqlite3

import numpy as np

from src import analyst_walk as W
from tests.test_analyst_walk import T0, _bucket, _setup


def _bars(rows, t0=T0):
    a = np.array(rows, dtype=float)
    return {"open": a[:, 0], "high": a[:, 1], "low": a[:, 2], "close": a[:, 3],
            "t": t0 + 300.0 * np.arange(len(a))}


def _hourly(lows, base=100.0):
    """One 1h bar per entry: 12 flat 5m bars at that low (high = low + 1)."""
    rows = []
    for lo in lows:
        rows += [(lo + 0.5, lo + 1, lo, lo + 0.5)] * 12
    return rows


def test_a_1h_swing_is_confirmed_only_after_two_later_hours_close():
    b = _bars(_hourly([105, 104, 100, 103, 104, 106]))   # swing low at hour 2
    sw = W._swings_1h(b, long=True)
    assert sw == [(T0 + 5 * 3600.0, 100.0)], "confirmed when hour 4 closes, not before"
    b = _bars(_hourly([105, 104, 100, 103]))             # only one later hour
    assert W._swings_1h(b, long=True) == []


def test_the_runner_trails_behind_confirmed_swings_and_keeps_the_move():
    # Long from 100: TP1 at 103 is hit in hour 1, the trend keeps going with a
    # pullback low at 105 (hour 4, confirmed when hour 6 closes), then price
    # falls back through it.
    path = (_hourly([99.5, 103, 108, 109, 105, 110, 112, 113])
            + [(113, 113, 102.5, 103.0)])
    cd = _bucket(path)
    s = _setup(entries=((100.0, 1.0),), stop=98.0, target=103.0)
    s["submitted_at"] = T0
    arms = W.walk_setup(s, cd, T0 + len(path) * 300)
    r = arms["runner_24h"]
    assert r["status"] == "resolved" and r["exit_reason"] == "target+trail"
    # Half at 103, half trailed to the 104 swing: better than TP1 alone.
    assert r["exit"] == (103.0 + 105.0) / 2
    assert r["net_pct"] > arms["analyst"]["net_pct"]


def test_the_runner_without_a_fill_mirrors_the_analyst_arm():
    cd = _bucket([(100, 100.5, 99.5, 100.0)] * 200)
    s = _setup(entries=((95.0, 1.0),), stop=93.0, target=103.0)
    arms = W.walk_setup(s, cd, T0 + 200 * 300)
    assert arms["runner_24h"]["unfilled"] == arms["analyst"]["unfilled"] == 1


def _fc(direction="up", inv=60000.0):
    return json.dumps({"btc_4h": {"dir": direction, "p": 0.6, "invalidation": inv,
                                  "horizon_s": 14400.0, "band_pct": 0.7}})


def test_the_forecast_exit_only_applies_to_setups_trading_with_the_forecast():
    base = {"entry_type": "pullback"}
    assert "btc_invalidated_exit" in W.arms_for({**base, "side": "long",
                                                 "plan_forecast_json": _fc("up")})
    assert "btc_invalidated_exit" not in W.arms_for({**base, "side": "short",
                                                     "plan_forecast_json": _fc("up")})
    assert "btc_invalidated_exit" not in W.arms_for({**base, "side": "long"})
    assert "btc_invalidated_exit" not in W.arms_for(
        {**base, "side": "long", "plan_forecast_json": _fc("up", inv=None)})


def test_a_long_leaves_when_btc_closes_below_the_invalidation():
    rows = [(100, 100.5, 99.5, 100.0), (100, 101, 100, 100.8), (100.8, 101.2, 100.5, 101.0),
            (101.0, 101.5, 100.7, 101.1)]
    cd = _bucket(rows)
    btc = {"open_time": (T0 + 300.0 * np.arange(4)) * 1000.0,
           "close": np.array([61000.0, 60500.0, 59900.0, 59800.0])}
    s = _setup(entries=((100.0, 1.0),), stop=98.0, target=105.0)
    s.update(side="long", plan_forecast_json=_fc("up", 60000.0))
    r = W.walk_setup(s, cd, T0 + 4 * 300, btc_cd=btc)["btc_invalidated_exit"]
    assert r["exit_reason"] == "btc_invalidated" and r["exit"] == 101.0


def test_the_owed_arm_count_in_sql_matches_arms_for_in_every_case():
    """A settled setup must never read as owing an arm: with the LIMIT ordered
    oldest first, it would crowd every new setup out of the walk."""
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE setups (setup_id TEXT, side TEXT, entry_type TEXT, plan_id TEXT)")
    con.execute("CREATE TABLE plans (plan_id TEXT, forecast_json TEXT)")
    cases = []
    i = 0
    for et in (None, "pullback", "immediate", "watch"):
        for side in ("long", "short"):
            for fc in (None, _fc("up"), _fc("down"), _fc("up", None), "{}"):
                sid, pid = f"s{i}", f"p{i}"
                con.execute("INSERT INTO setups VALUES (?,?,?,?)", (sid, side, et, pid))
                con.execute("INSERT INTO plans VALUES (?,?)", (pid, fc))
                cases.append((sid, {"side": side, "entry_type": et, "plan_forecast_json": fc}))
                i += 1
    for sid, setup in cases:
        n = con.execute(f"SELECT {W._REQUIRED_ARMS_SQL} FROM setups s LEFT JOIN plans p "
                        "ON p.plan_id = s.plan_id WHERE s.setup_id=?", (sid,)).fetchone()[0]
        assert n == len(W.arms_for(setup)), (setup, n)
