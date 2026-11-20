"""Analyst plan validator + ledger (spec step 3, 2026-11-19)."""
from __future__ import annotations

import sqlite3

import pytest

from src import analyst_plan as P
from src import analyst_snapshot as A
from src import diag_catalog
from src.level_book import Level
from tests.test_analyst_snapshot import NOW, _engine

ADMIT = lambda s: (True, "")  # noqa: E731


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    led = P.Ledger(str(tmp_path / "plans.sqlite"))
    monkeypatch.setattr(P, "_ledger", led)
    return led


def _setup_engine():
    base = A.pair_snapshot(_engine(), "ETHUSDT", now=NOW)
    price, atr = base["price"], base["atr"]["1h"]
    lv = [Level(price=price - 1.0 * atr, type="support", source_tf="4h", touches=2),
          Level(price=price - 2.0 * atr, type="support", source_tf="1d", touches=3),
          Level(price=price + 1.5 * atr, type="resistance", source_tf="4h", touches=2),
          Level(price=price + 3.0 * atr, type="resistance", source_tf="1d", touches=2)]
    eng = _engine(levels={"ETHUSDT": lv})
    menu = A.pair_snapshot(eng, "ETHUSDT", now=NOW, per_side=P.MENU_DEPTH)["levels"]["levels"]

    def lid(p):
        return min(menu, key=lambda x: abs(x["price"] - p))["id"]
    ids = {"entry": lid(price - atr), "stop": lid(price - 2 * atr),
           "t1": lid(price + 1.5 * atr), "t2": lid(price + 3 * atr)}
    return eng, ids


def _plan(ids, **over):
    s = {"symbol": "ETHUSDT", "side": "long", "archetype": "trend_pullback",
         "entry_level_ids": [ids["entry"]], "stop_level_id": ids["stop"],
         "target_level_ids": [ids["t1"], ids["t2"]], "expiry_hours": 4,
         "invalidation": "4h close below the 1d swing"}
    s.update(over)
    return {"bias": "risk_on", "notes": "test", "setups": [s]}


def test_a_well_formed_setup_is_accepted_and_recorded_with_resolved_prices(ledger):
    eng, ids = _setup_engine()
    out = P.submit(_plan(ids), eng, source="test", now=NOW, admission=ADMIT)
    assert out["accepted"] and out["n_accepted"] == 1, out
    s = out["setups"][0]
    assert s["status"] == "accepted" and 0.8 <= s["stop_atr"] <= 2.5
    con = sqlite3.connect(ledger.path)
    (stop_level, stop, status) = con.execute(
        "SELECT stop_level_price, stop_price, status FROM setups").fetchone()
    assert status == "accepted" and stop < stop_level  # placed beyond structure
    import json as _json
    menu = _json.loads(con.execute("SELECT menu_json FROM setups").fetchone()[0])
    assert {ids["entry"], ids["stop"], ids["t1"]} <= {m["id"] for m in menu}


def test_a_price_is_never_accepted_in_place_of_a_level_id(ledger):
    eng, ids = _setup_engine()
    out = P.submit(_plan(ids, stop_level_id="3700.0"), eng, now=NOW, admission=ADMIT)
    assert out["setups"][0]["reason"] == "unknown_level"


def test_stop_on_the_wrong_side_is_geometry(ledger):
    eng, ids = _setup_engine()
    out = P.submit(_plan(ids, side="short"), eng, now=NOW, admission=ADMIT)
    assert out["setups"][0]["reason"] == "geometry"


def test_stop_too_wide_is_named(ledger):
    eng, ids = _setup_engine()
    # Stop at the far support with entry at the near RESISTANCE side reversed:
    out = P.submit(_plan(ids, entry_level_ids=[ids["t1"]], target_level_ids=[ids["t2"]]),
                   eng, now=NOW, admission=ADMIT)
    assert out["setups"][0]["reason"] == "stop_distance"


def test_admission_is_fail_closed_and_first(ledger):
    eng, ids = _setup_engine()
    out = P.submit(_plan(ids), eng, now=NOW, admission=lambda s: (False, "tradfi_perp"))
    assert out["setups"][0]["reason"] == "admission"
    assert out["setups"][0]["detail"] == "tradfi_perp"


def test_a_symbol_outside_the_universe_is_refused(ledger):
    eng, ids = _setup_engine()
    out = P.submit(_plan(ids, symbol="DOGEUSDT"), eng, now=NOW, admission=ADMIT)
    assert out["setups"][0]["reason"] == "not_in_universe"


def test_one_setup_per_symbol(ledger):
    eng, ids = _setup_engine()
    plan = _plan(ids)
    plan["setups"].append(dict(plan["setups"][0]))
    out = P.submit(plan, eng, now=NOW, admission=ADMIT)
    assert [s["status"] for s in out["setups"]] == ["accepted", "rejected"]
    assert out["setups"][1]["reason"] == "caps"


def test_a_malformed_plan_is_refused_whole_and_not_recorded(ledger):
    eng, _ = _setup_engine()
    out = P.submit({"bias": "yolo", "setups": []}, eng, now=NOW, admission=ADMIT)
    assert out == {"accepted": False, "reason": "schema",
                   "detail": f"bias must be one of {P.BIASES}"}
    assert ledger.recent()["readable"] is False


def test_a_bad_setup_is_rejected_alone_with_a_schema_reason(ledger):
    eng, ids = _setup_engine()
    out = P.submit(_plan(ids, invalidation=""), eng, now=NOW, admission=ADMIT)
    assert out["accepted"] and out["setups"][0]["reason"] == "schema"


def test_plans_are_rate_limited_per_hour(ledger):
    eng, ids = _setup_engine()
    for _ in range(P.MAX_PLANS_PER_HOUR):
        assert P.submit({"bias": "stand_aside", "setups": []}, eng, now=NOW)["accepted"]
    out = P.submit({"bias": "stand_aside", "setups": []}, eng, now=NOW)
    assert out["reason"] == "rate_limited"


def test_stand_aside_with_no_setups_is_a_valid_plan(ledger):
    eng, _ = _setup_engine()
    out = P.submit({"bias": "stand_aside", "setups": []}, eng, now=NOW)
    assert out["accepted"] and out["n_accepted"] == 0
    rec = ledger.recent()
    assert rec["plans"][0]["bias"] == "stand_aside" and rec["plans"][0]["macro"] == "unknown"


def test_catalog_round_trip(ledger, monkeypatch):
    monkeypatch.setattr(diag_catalog, "actions_enabled", lambda: True)
    eng, _ = _setup_engine()
    out = diag_catalog.run("action.analyst_submit_plan", eng,
                           {"plan": {"bias": "neutral", "setups": []}, "source": "mcp"})
    assert out["ok"] and out["result"]["accepted"], out
    read = diag_catalog.run("read.analyst_plans", eng, {})
    assert read["ok"] and read["result"]["plans"][0]["source"] == "mcp"
