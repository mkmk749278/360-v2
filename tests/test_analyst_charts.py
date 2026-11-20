"""The analyst's own market view, and plan v2 (2026-11-20)."""
from __future__ import annotations

import json
import sqlite3

import pytest

from src import analyst_charts as C
from src import analyst_plan as P
from src import analyst_snapshot as A
from src import analyst_walk as W
from src import diag_catalog
from tests.test_analyst_snapshot import NOW, TF_STEP, _engine, _seed

ADMIT = lambda s: (True, "")  # noqa: E731


def _eng():
    e = _engine()
    for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT"):  # 8 days of 1h for the 7d stats
        e.data_store.candles[s].pop("1h", None)
        _seed(e.data_store, s, "1h", 200, {"BTCUSDT": 90000.0, "ETHUSDT": 3000.0}.get(s, 150.0),
              {"ETHUSDT": 0.001}.get(s, 0.0))
    return e


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    led = P.Ledger(str(tmp_path / "plans.sqlite"))
    monkeypatch.setattr(P, "_ledger", led)
    return led


def test_scan_covers_the_universe_and_says_unknown_not_zero():
    out = C.scan(_eng(), now=NOW)
    assert out["n"] == 3
    eth = next(r for r in out["rows"] if r["symbol"] == "ETHUSDT")
    assert eth["chg_pct"]["24h"] > 0 and 0 <= eth["pos_in_7d_range"] <= 1
    assert eth["funding_rate"] is None and eth["oi_chg_24h_pct"] is None


def test_chart_returns_closed_raw_bars_with_bounds():
    out = C.chart(_eng(), "ETHUSDT", "1h", 50, now=NOW)
    assert out["readable"] and len(out["bars"]) == 50 and out["columns"][1] == "open"
    assert C.chart(_eng(), "ETHUSDT", "3m", now=NOW)["readable"] is False
    assert len(C.chart(_eng(), "ETHUSDT", "1h", 9999, now=NOW)["bars"]) <= C.MAX_BARS


def test_catalog_chart_refuses_a_non_symbol():
    out = diag_catalog.run("read.analyst_chart", _eng(), {"symbol": "../x"})
    assert out["ok"] and out["result"]["readable"] is False


def _price_plan(eng, **over):
    snap = A.pair_snapshot(eng, "ETHUSDT", now=NOW)
    atr = snap["atr"]["1h"]
    # Anchor on the 1h close: the range check reads 1h bars.
    p = float(A._arr(A._store_candles(eng, "ETHUSDT", now_ms=NOW * 1000)["1h"], "close")[-1])
    s = {"symbol": "ETHUSDT", "side": "long", "archetype": "trend_pullback",
         "entry_prices": [p - 0.5 * atr], "stop_price": p - 1.7 * atr,
         "target_prices": [p + 0.8 * atr], "invalidation": "1h close below stop",
         "scenario": "pullback to the 1h higher low holds", "p_target": 0.45}
    s.update(over)
    return {"bias": "risk_on", "setups": [s]}, p, atr


def test_the_analyst_can_name_its_own_prices(ledger):
    eng = _eng()
    plan, p, atr = _price_plan(eng)
    out = P.submit(plan, eng, now=NOW, admission=ADMIT)
    assert out["setups"][0]["status"] == "accepted", out
    row = sqlite3.connect(ledger.path).execute(
        "SELECT plan_mode, scenario, p_target, stop_price FROM setups").fetchone()
    assert row[0] == "prices" and row[1].startswith("pullback") and row[2] == 0.45
    assert abs(row[3] - (p - 1.7 * atr)) < 1e-6  # no extra buffer on its own stop


def test_an_invented_price_outside_the_traded_range_is_refused(ledger):
    eng = _eng()
    plan, p, _ = _price_plan(eng, target_prices=[p_far := 10 * 3000.0])
    out = P.submit(plan, eng, now=NOW, admission=ADMIT)
    assert out["setups"][0]["reason"] == "price_out_of_range" and p_far


def test_p_target_must_be_a_probability(ledger):
    eng = _eng()
    plan, _, _ = _price_plan(eng, p_target=1.4)
    assert P.submit(plan, eng, now=NOW, admission=ADMIT)["setups"][0]["reason"] == "schema"


def test_calibration_scores_filled_forecasts_only(ledger):
    con = ledger._connect()
    with con:
        for i, (p, reason, unfilled) in enumerate([(0.8, "target", 0), (0.6, "stop", 0),
                                                    (0.5, "target", 1)]):
            con.execute("INSERT INTO setups (setup_id, plan_id, idx, status, submitted_at,"
                        " p_target) VALUES (?, 'p', ?, 'accepted', 0, ?)", (f"s{i}", i, p))
    con.close()
    con = W._connect(ledger.path)
    with con:
        for i, (_, reason, unfilled) in enumerate([(0.8, "target", 0), (0.6, "stop", 0),
                                                    (0.5, "target", 1)]):
            con.execute("INSERT INTO walks (setup_id, arm, status, exit_reason, unfilled,"
                        " updated_at) VALUES (?, 'analyst', 'resolved', ?, ?, 0)",
                        (f"s{i}", reason, unfilled))
    con.close()
    cal = W.summary(path=ledger.path)["calibration"]
    assert cal["n"] == 2 and cal["excluded_unfilled"] == 1
    assert cal["brier"] == round(((0.8 - 1) ** 2 + (0.6 - 0) ** 2) / 2, 4)
    _ = json, TF_STEP


def test_a_continuation_target_beyond_the_range_is_allowed(ledger):
    # ZRO 2026-11-20: a breakdown's target sits under the old low by design.
    eng = _eng()
    plan, p, atr = _price_plan(eng)
    h1 = A._store_candles(eng, "ETHUSDT", now_ms=NOW * 1000)["1h"]
    hi = float(A._arr(h1, "high")[-168:].max())
    plan["setups"][0]["target_prices"] = [hi + 2.0 * atr]
    assert P.submit(plan, eng, now=NOW, admission=ADMIT)["setups"][0]["status"] == "accepted"
    plan["setups"][0]["target_prices"] = [hi + 4.0 * atr]
    out = P.submit(plan, eng, now=NOW, admission=ADMIT)["setups"][0]
    assert out["reason"] == "price_out_of_range" and "target" in out["detail"]


def test_an_entry_beyond_the_range_is_still_refused(ledger):
    eng = _eng()
    plan, p, atr = _price_plan(eng)
    h1 = A._store_candles(eng, "ETHUSDT", now_ms=NOW * 1000)["1h"]
    hi = float(A._arr(h1, "high")[-168:].max())
    plan["setups"][0].update(entry_prices=[hi + 2 * atr], stop_price=hi + 0.8 * atr,
                             target_prices=[hi + 2.9 * atr])
    plan["setups"][0]["side"] = "long"
    out = P.submit(plan, eng, now=NOW, admission=ADMIT)["setups"][0]
    assert out["reason"] == "price_out_of_range" and not out["detail"].startswith("target")
