"""Dark forward walk of analyst setups (spec step 4, 2026-11-20)."""
from __future__ import annotations

import json
import sqlite3

from src import analyst_walk as W
from src import diag_catalog
from src.historical_data import HistoricalDataStore

T0 = 1_800_000_000.0  # submit time; bars open at T0, T0+300, ...


def _bucket(bars):
    """bars: list of (open, high, low, close) starting at T0, 5m apart."""
    st = HistoricalDataStore()
    for i, (o, h, lo, c) in enumerate(bars):
        st.update_candle("X", "5m", {"open": o, "high": h, "low": lo, "close": c,
                                     "volume": 1.0, "open_time": (T0 + 300 * i) * 1000})
    return st.candles["X"]["5m"]


def _setup(side="long", entries=((99.0, 1.0),), stop=97.0, target=103.0, expiry_h=4):
    return {"setup_id": "p:0", "side": side, "stop_price": stop,
            "entries_json": json.dumps([{"id": f"e{i}", "price": p, "weight": w}
                                        for i, (p, w) in enumerate(entries)]),
            "targets_json": json.dumps([{"id": "t", "price": target}]),
            "submitted_at": T0, "expires_at": T0 + expiry_h * 3600}


NOW = T0 + 100 * 300


def test_limit_fills_then_hits_target_net_of_fees():
    cd = _bucket([(100, 100.5, 99.5, 100), (100, 100, 98.8, 99.2), (99.5, 103.5, 99.4, 103)])
    r = W.walk_setup(_setup(), cd, NOW)["analyst"]
    assert r["status"] == "resolved" and r["exit_reason"] == "target" and r["entry"] == 99.0
    assert abs(r["net_pct"] - ((103 - 99) / 99 * 100 - W.ROUND_TRIP_PCT)) < 1e-3


def test_stop_first_on_an_ambiguous_bar():
    cd = _bucket([(100, 100, 98.9, 99.5), (99.5, 104, 96, 100)])
    assert W.walk_setup(_setup(), cd, NOW)["analyst"]["exit_reason"] == "stop"


def test_a_target_on_the_limit_fill_bar_is_not_booked():
    # One bar reaches both 99 (fill) and 103 (target): ordering unknown.
    cd = _bucket([(100, 103.5, 98.9, 100), (100, 100.5, 99.5, 100)])
    r = W.walk_setup(_setup(), cd, NOW)["analyst"]
    assert r["status"] == "open"


def test_unfilled_limit_is_scored_at_market_and_flagged():
    bars = [(100, 101, 99.5, 100.5)] * (4 * 12 + 1) + [(100.5, 103.5, 100, 103)]
    r = W.walk_setup(_setup(expiry_h=4), _bucket(bars), NOW)
    assert r["analyst"]["unfilled"] == 1 and r["analyst"]["reason"] == "scored_at_market"
    assert r["analyst"]["net_pct"] == r["market"]["net_pct"]


def test_unfilled_inside_the_window_waits_rather_than_scoring():
    cd = _bucket([(100, 101, 99.5, 100.5)] * 3)
    assert W.walk_setup(_setup(), cd, NOW)["analyst"]["status"] == "open"


def test_tranches_weight_only_what_filled():
    cd = _bucket([(100, 100, 98.9, 99.5), (99.5, 100, 99.2, 99.8)])
    r = W.walk_setup(_setup(entries=((99.0, 0.4), (98.0, 0.6))), cd, NOW)["tranche"]
    assert r["filled_frac"] == 0.4 and r["entry"] == 99.0


def test_history_that_rolled_off_is_insufficient_not_walked():
    st = HistoricalDataStore()
    st.update_candle("X", "5m", {"open": 1, "high": 1, "low": 1, "close": 1, "volume": 1,
                                 "open_time": (T0 + 3600) * 1000})
    r = W.walk_setup(_setup(), st.candles["X"]["5m"], NOW)
    assert r["market"] == {"status": "insufficient", "reason": "history_rolled_off"}


def test_short_side_mirrors():
    cd = _bucket([(100, 101.1, 99.5, 101), (101, 101.2, 96.8, 97)])
    r = W.walk_setup(_setup(side="short", entries=((101.0, 1.0),), stop=103, target=97),
                     cd, NOW)["analyst"]
    assert r["exit_reason"] == "target" and r["gross_pct"] > 0


def test_step_and_summary_over_the_real_ledger(tmp_path, monkeypatch):
    from src import analyst_plan as P
    led = P.Ledger(str(tmp_path / "plans.sqlite"))
    monkeypatch.setattr(P, "_ledger", led)
    con = led._connect()
    s = _setup()
    with con:
        con.execute("INSERT INTO plans (plan_id, submitted_at, bias) VALUES ('p',?, 'risk_on')", (T0,))
        con.execute(
            "INSERT INTO setups (setup_id, plan_id, idx, symbol, side, status, entries_json,"
            " stop_price, targets_json, expires_at, submitted_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            ("p:0", "p", 0, "X", "long", "accepted", s["entries_json"], 97.0,
             s["targets_json"], s["expires_at"], T0))
    con.close()
    st = HistoricalDataStore()
    for i, b in enumerate([(100, 100.5, 99.5, 100), (100, 100, 98.8, 99.2),
                           (99.5, 103.5, 99.4, 103)]):
        st.update_candle("X", "5m", {"open": b[0], "high": b[1], "low": b[2], "close": b[3],
                                     "volume": 1, "open_time": (T0 + 300 * i) * 1000})
    eng = type("E", (), {"data_store": st})()
    assert W.step(eng, now=NOW)["setups"] == 1
    out = diag_catalog.run("read.analyst_outcomes", eng, {})
    assert out["ok"], out
    by = out["result"]["by_arm"]
    assert by["analyst"]["n"] == 1 and by["none"]["avg_net_pct"] == 0.0
    assert out["result"]["arms_not_built"] == ["fixed_rule", "existing_signals"]
    # Resolved on every arm → not walked again.
    assert W.step(eng, now=NOW)["setups"] == 0 or by["market"]["open"]


def test_cadence_probe(tmp_path):
    p = str(tmp_path / "x.sqlite")
    assert W.health(path=p)[0] is True
    from src import analyst_plan as P
    led = P.Ledger(p)
    con = led._connect()
    with con:
        con.execute("INSERT INTO plans (plan_id, submitted_at) VALUES ('a', ?)", (T0,))
    con.close()
    assert W.health(now=T0 + 1800, path=p)[0] is True
    ok, msg = W.health(now=T0 + 3 * 3600, path=p)
    assert not ok and "missed" in msg
    assert W.health(now=T0 + 72 * 3600, path=p)[0] is True
    sqlite3.connect(p).close()
