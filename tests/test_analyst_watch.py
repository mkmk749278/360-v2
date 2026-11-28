"""Phase 2: watch, confirm, then enter — and immediate entries.

docs/ANALYST_DESK_PLAN_2026_11_28.md. A watch enters only on a confirming
CLOSED bar after price reached its zone, and is judged against a plain resting
limit at the same zone (``zone_limit``) on the same setup.
"""
from __future__ import annotations

import json
import sqlite3

import numpy as np
import pytest

from src import analyst_plan as P
from src import analyst_walk as W
from src import diag_catalog
from tests.test_analyst_plan import ADMIT, NOW as PNOW, _setup_engine
from tests.test_analyst_walk import NOW, T0, _bucket


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    led = P.Ledger(str(tmp_path / "plans.sqlite"))
    monkeypatch.setattr(P, "_ledger", led)
    return led


def _watch_plan(**watch_over):
    watch = {"zone": [3770.0, 3780.0],
             "confirm": {"rule": "close_beyond_zone", "tf": "5m"},
             "cancel": [{"rule": "btc_beyond", "price": 50000.0, "dir": "below"}]}
    watch.update(watch_over)
    return {"bias": "risk_on", "setups": [{
        "symbol": "ETHUSDT", "side": "long", "archetype": "trend_pullback",
        "entry_type": "watch", "watch": watch, "stop_price": 3740.0,
        "target_prices": [3830.0, 3860.0], "expiry_hours": 6,
        "invalidation": "1h close below 3740"}]}


# ── validator ───────────────────────────────────────────────────────────────

def test_a_watch_is_accepted_and_stored_whole(ledger):
    eng, _ = _setup_engine()
    out = P.submit(_watch_plan(), eng, now=PNOW, admission=ADMIT)
    assert out["n_accepted"] == 1, out
    con = sqlite3.connect(ledger.path)
    et, wj, entries = con.execute(
        "SELECT entry_type, watch_json, entries_json FROM setups").fetchone()
    assert et == "watch"
    w = json.loads(wj)
    assert w["zone"] == [3770.0, 3780.0] and w["confirm"]["rule"] == "close_beyond_zone"
    assert json.loads(entries)[0]["price"] == 3775.0, "geometry is checked from the zone's middle"


@pytest.mark.parametrize("over,reason", [
    ({"confirm": {"rule": "vibes"}}, "watch.confirm.rule"),
    ({"cancel": [{"rule": "news"}]}, "watch.cancel rules"),
    ({"zone": [3780.0, 3770.0]}, "low must be below high"),
    ({"confirm": {"rule": "rejection_wick", "min_wick_ratio": 0.05}}, "min_wick_ratio"),
    ({"cancel": [{"rule": "btc_beyond", "price": 1.0, "dir": "sideways"}]}, "dir"),
])
def test_a_condition_outside_the_vocabulary_is_a_named_reject(ledger, over, reason):
    eng, _ = _setup_engine()
    s = P.submit(_watch_plan(**over), eng, now=PNOW, admission=ADMIT)["setups"][0]
    assert s["status"] == "rejected" and s["reason"] == "schema" and reason in s["detail"]


def test_the_stop_and_targets_must_clear_the_whole_zone(ledger):
    eng, _ = _setup_engine()
    s = P.submit(_watch_plan(zone=[3735.0, 3780.0]), eng, now=PNOW,
                 admission=ADMIT)["setups"][0]
    assert s["reason"] == "geometry" and "whole watch zone" in s["detail"]


def test_an_immediate_entry_is_the_price_at_submit(ledger):
    eng, _ = _setup_engine()
    plan = {"bias": "risk_on", "setups": [{
        "symbol": "ETHUSDT", "side": "long", "archetype": "breakout_retest",
        "entry_type": "immediate", "stop_price": 3760.0, "target_prices": [3860.0],
        "expiry_hours": 4, "invalidation": "back under 3760"}]}
    out = P.submit(plan, eng, now=PNOW, admission=ADMIT)
    assert out["n_accepted"] == 1, out
    con = sqlite3.connect(ledger.path)
    et, entries, mode = con.execute(
        "SELECT entry_type, entries_json, plan_mode FROM setups").fetchone()
    assert et == "immediate" and mode == "market"
    assert json.loads(entries)[0]["price"] == pytest.approx(3805.2230336151756)


# ── the watch walk, pure ────────────────────────────────────────────────────

def _bars(rows, t0=T0):
    a = np.array(rows, dtype=float)
    return {"open": a[:, 0], "high": a[:, 1], "low": a[:, 2], "close": a[:, 3],
            "t": t0 + 300.0 * np.arange(len(a))}


SHORT = {"zone": [101.0, 102.0], "confirm": {"rule": "close_beyond_zone", "tf": "5m"},
         "cancel": []}


def test_no_entry_until_price_reaches_the_zone_then_a_close_back_out():
    b = _bars([(100, 100.5, 99.8, 100.2),   # below the zone: watching
               (100.2, 101.4, 100.1, 101.2),  # tags the zone, closes inside
               (101.2, 101.6, 100.6, 100.7)])  # closes back below 101: confirm
    r = W.watch_walk(b, False, SHORT, 103.0, T0 + 6 * 3600)
    assert r == {"state": "entered", "j": 2, "price": 100.7}
    assert W.watch_walk(_bars([(100, 100.5, 99.8, 100.2)]), False, SHORT, 103.0,
                        T0 + 3600)["state"] == "watching"


def test_a_close_below_the_zone_before_a_tag_is_not_a_confirmation():
    b = _bars([(100, 100.5, 99.8, 100.2), (100.2, 100.4, 99.0, 99.2)])
    assert W.watch_walk(b, False, SHORT, 103.0, T0 + 3600)["state"] == "watching"


def test_cancels_run_before_confirmation():
    btc = {T0 + 300.0: 61000.0}
    w = dict(SHORT, cancel=[{"rule": "btc_beyond", "price": 60500.0, "dir": "above"}])
    b = _bars([(100, 101.5, 99.8, 101.1), (101.1, 101.6, 100.4, 100.6)])
    r = W.watch_walk(b, False, w, 103.0, T0 + 3600, btc)
    assert r["state"] == "cancelled" and r["why"] == "btc_beyond"
    b = _bars([(100, 101.5, 99.8, 101.1), (101.1, 103.5, 101.0, 103.2)])
    assert W.watch_walk(b, False, SHORT, 103.0, T0 + 3600)["why"] == "closed_beyond_stop"


def test_a_15m_confirmation_waits_for_the_15m_close():
    w = dict(SHORT, confirm={"rule": "close_beyond_zone", "tf": "15m"})
    # T0 is a 15m boundary; bars 0,1,2 form the first 15m period.
    b = _bars([(100, 101.5, 99.8, 101.2),   # tag
               (101.2, 101.3, 100.5, 100.6),  # 5m close below the zone: NOT a 15m close
               (100.6, 101.4, 100.6, 101.3),  # the 15m period closes back inside
               (101.3, 101.4, 100.4, 100.5),
               (100.5, 100.8, 100.2, 100.3),
               (100.3, 100.5, 100.1, 100.2)])  # the second 15m period closes below
    assert T0 % 900 == 0
    assert W.watch_walk(b, False, w, 103.0, T0 + 3600) == {"state": "entered", "j": 5,
                                                          "price": 100.2}


def test_rejection_wick():
    w = dict(SHORT, confirm={"rule": "rejection_wick", "tf": "5m", "min_wick_ratio": 0.5})
    b = _bars([(100.8, 102.0, 100.7, 101.0)])  # long upper wick, closes below the middle
    assert W.watch_walk(b, False, w, 103.0, T0 + 3600)["state"] == "entered"
    b = _bars([(100.8, 101.2, 100.7, 101.1)])  # small wick
    assert W.watch_walk(b, False, w, 103.0, T0 + 3600)["state"] == "in_zone"


# ── the arms ───────────────────────────────────────────────────────────────

def _watch_setup(side="short", stop=103.0, target=98.0, watch=SHORT):
    return {"setup_id": "p:0", "side": side, "stop_price": stop, "entry_type": "watch",
            "watch_json": json.dumps(watch), "price_at_submit": 100.0,
            "entries_json": json.dumps([{"id": "z", "price": 101.5, "weight": 1.0}]),
            "targets_json": json.dumps([{"id": "t", "price": target}]),
            "submitted_at": T0, "expires_at": T0 + 6 * 3600}


def test_a_confirmed_watch_enters_at_the_close_and_walks_from_the_next_bar():
    cd = _bucket([(100, 100.5, 99.8, 100.2), (100.2, 101.4, 100.1, 101.2),
                  (101.2, 101.6, 100.6, 100.7), (100.7, 100.8, 97.5, 97.8)])
    arms = W.walk_setup(_watch_setup(), cd, NOW)
    a = arms["analyst"]
    assert a["watch_state"] == "entered" and a["entry"] == 100.7
    assert a["exit_reason"] == "target" and a["unfilled"] == 0
    assert a["fees_pct"] == pytest.approx(W.FEE_TAKER_PCT + W.FEE_MAKER_PCT)
    # The control: a resting sell limit at the zone's near edge, same setup.
    z = arms["zone_limit"]
    assert z["entry"] == 101.0 and z["exit_reason"] == "target"


def test_a_watch_that_never_confirms_earns_zero_and_keeps_the_counterfactual():
    cd = _bucket([(100, 100.5, 99.5, 100.0)] * 200)  # never reaches the zone
    a = W.walk_setup(_watch_setup(), cd, T0 + 200 * 300)["analyst"]
    assert a["unfilled"] == 1 and a["watch_state"] == "expired"
    assert W.realized_pct({**a, "arm": "analyst"}) == 0.0


def test_an_open_watch_reads_as_pending_on_the_feed():
    cd = _bucket([(100, 101.5, 99.8, 101.2)])
    a = W.walk_setup(_watch_setup(), cd, T0 + 600)["analyst"]
    assert a["status"] == "open" and a["reason"] == "awaiting_fill"
    assert a["watch_state"] == "in_zone"
    assert W._feed_state(a) == "pending", "the Desk must not show an open watch as a fill"


def test_an_immediate_setup_is_its_own_market_entry():
    cd = _bucket([(100, 100.5, 99.5, 100.2), (100.2, 104, 100, 103.5)])
    s = dict(_watch_setup(side="long", stop=97.0, target=103.0), entry_type="immediate",
             watch_json=None)
    arms = W.walk_setup(s, cd, NOW)
    assert arms["analyst"] == arms["market"] and "zone_limit" not in arms
    assert arms["ladder"]["entry"] == 100.0


def test_only_a_watch_gets_the_zone_limit_control():
    assert "zone_limit" in W.arms_for({"entry_type": "watch"})
    assert "zone_limit" not in W.arms_for({"entry_type": "pullback"})
    assert "zone_limit" not in W.arms_for({})


def test_a_resolved_watch_is_not_walked_again_and_splits_by_entry_type(ledger):
    """Through submit, step and summary: a watch needs all its arms settled."""
    eng, _ = _setup_engine()
    P.submit(_watch_plan(), eng, now=PNOW, admission=ADMIT)
    con = sqlite3.connect(ledger.path)
    (sid,) = con.execute("SELECT setup_id FROM setups").fetchone()
    con.execute("UPDATE setups SET submitted_at=?, expires_at=? WHERE setup_id=?",
                (T0, T0 + 6 * 3600, sid))
    con.commit()
    con.close()
    st = __import__("src.historical_data", fromlist=["x"]).HistoricalDataStore()
    for i in range(200):
        st.update_candle("ETHUSDT", "5m", {"open": 3790, "high": 3795, "low": 3785,
                                           "close": 3790, "volume": 1,
                                           "open_time": (T0 + 300 * i) * 1000})
    eng2 = type("E", (), {"data_store": st})()
    first = W.step(eng2, now=T0 + 200 * 300)
    assert first["setups"] == 1
    assert W.step(eng2, now=T0 + 200 * 300)["setups"] == 0, "all 7 arms settled"
    res = diag_catalog.run("read.analyst_outcomes", eng2, {})["result"]
    assert "watch|long" in res["by_entry_type"]
    assert res["by_arm"]["zone_limit"]["n"] == 1
