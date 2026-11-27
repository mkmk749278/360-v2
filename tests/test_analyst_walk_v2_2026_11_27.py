"""Analyst walk v2 — measurement integrity (2026-11-27).

Each test pins one claim from the walk's v2 docstring: what a posted order
earned (unfilled = 0.00%), tranche legs walked from their own fills, costs by
order type, funding at the symbol's own settlements, the ladder arm, the
what-ifs, and the rule that a settled row is never overwritten.
"""
from __future__ import annotations

import json
import sqlite3

import pytest

from src import analyst_plan as P
from src import analyst_walk as W
from src.historical_data import HistoricalDataStore
from tests.test_analyst_walk import NOW, T0, _bucket, _setup

FLAT = [(100, 100.5, 99.5, 100)]


def _store(bars, symbol="X"):
    st = HistoricalDataStore()
    for i, (o, h, lo, c) in enumerate(bars):
        st.update_candle(symbol, "5m", {"open": o, "high": h, "low": lo, "close": c,
                                        "volume": 1.0, "open_time": (T0 + 300 * i) * 1000})
    return st


def _ledger(tmp_path, monkeypatch, setups):
    """setups: list of dicts merged over a default accepted long on X."""
    led = P.Ledger(str(tmp_path / "plans.sqlite"))
    monkeypatch.setattr(P, "_ledger", led)
    con = led._connect()
    with con:
        con.execute("INSERT INTO plans (plan_id, submitted_at) VALUES ('p', ?)", (T0,))
        for i, over in enumerate(setups):
            s = _setup(**over.pop("_setup", {}))
            row = {"setup_id": f"p:{i}", "plan_id": "p", "idx": i, "symbol": "X",
                   "side": s["side"], "status": "accepted", "entries_json": s["entries_json"],
                   "stop_price": s["stop_price"], "targets_json": s["targets_json"],
                   "expires_at": s["expires_at"], "submitted_at": T0, **over}
            con.execute(f"INSERT INTO setups ({', '.join(row)}) VALUES "
                        f"({', '.join('?' * len(row))})", tuple(row.values()))
    con.close()
    return led


# ── tranche: each leg from its own fill ──────────────────────────────────


def test_a_leg_filling_after_the_exit_is_cancelled_not_blended():
    # Leg 1 (99) fills on bar 1, the target (103) is hit on bar 2; price then
    # falls back through leg 2 (98) on bar 3. v1 blended 99/98 and booked the
    # target off the better average; the position was already out.
    bars = [(100, 100.5, 99.5, 100), (100, 100, 98.9, 99.2), (99.5, 103.5, 99.4, 103),
            (103, 103, 97.9, 98.5)]
    r = W.walk_setup(_setup(entries=((99.0, 0.4), (98.0, 0.6))), _bucket(bars), NOW)["tranche"]
    assert r["status"] == "resolved" and r["exit_reason"] == "target"
    assert r["entry"] == 99.0 and r["filled_frac"] == 0.4
    assert r["reason"] == "legs_cancelled_after_exit:1"
    assert abs(r["gross_pct"] - (103 - 99) / 99 * 100) < 1e-3


def test_legs_filled_before_the_exit_are_each_walked():
    bars = [(100, 100.5, 99.5, 100), (100, 100, 98.9, 99.2), (99, 99.2, 97.9, 98.5),
            (98.5, 103.5, 98.4, 103)]
    r = W.walk_setup(_setup(entries=((99.0, 0.4), (98.0, 0.6))), _bucket(bars), NOW)["tranche"]
    assert r["filled_frac"] == 1.0 and r["exit_reason"] == "target"
    want = 0.4 * (103 - 99) / 99 * 100 + 0.6 * (103 - 98) / 98 * 100
    assert abs(r["gross_pct"] - want) < 1e-3


# ── realized per setup posted ────────────────────────────────────────────


def test_an_unfilled_limit_earns_zero_and_its_market_outcome_is_kept_apart(tmp_path,
                                                                           monkeypatch):
    # Limit at 90 never trades; market runs to the target. Old headline: the
    # market's win. Realized: 0.00%.
    _ledger(tmp_path, monkeypatch, [{"_setup": {"entries": ((90.0, 1.0),), "stop": 88.0,
                                                "target": 103.0, "expiry_h": 1}}])
    bars = FLAT * 13 + [(100, 103.5, 100, 103)]
    W.step(type("E", (), {"data_store": _store(bars)})(), now=NOW, deriv_path="")
    a = W.summary(now=NOW)["by_arm"]["analyst"]
    assert a["n"] == 1 and a["avg_net_pct"] == 0.0 and a["win_rate"] == 0.0
    assert a["with_unfilled_at_market"]["avg_net_pct"] > 2.0
    assert a["missed_market"]["n"] == 1 and a["filled"]["n"] == 0
    assert a["basis"].startswith("realized")


def test_realized_weights_a_partial_tranche_by_what_filled():
    r = {"arm": "tranche", "status": "resolved", "net_pct": 2.0, "filled_frac": 0.4,
         "unfilled": 0, "exit_reason": "target"}
    assert abs(W.realized_pct(r) - 0.8) < 1e-12


def test_the_market_arm_is_never_zeroed_as_unfilled():
    r = {"arm": "market", "status": "resolved", "net_pct": 1.5, "filled_frac": 1.0,
         "unfilled": 0, "exit_reason": "target"}
    assert W.realized_pct(r) == 1.5


# ── fees by order type ───────────────────────────────────────────────────


def test_fees_follow_the_order_type():
    cd = _bucket([(100, 100.5, 99.5, 100), (100, 100, 98.8, 99.2), (99.5, 103.5, 99.4, 103)])
    out = W.walk_setup(_setup(), cd, NOW)
    assert out["analyst"]["fees_pct"] == 0.04  # maker in, target is a resting limit
    cd = _bucket([(100, 100, 96.5, 97)])
    out = W.walk_setup(_setup(entries=((99.0, 1.0),)), cd, NOW)
    assert out["market"]["fees_pct"] == 0.10  # taker in, stop is taker
    assert out["none"]["fees_pct"] == 0.0


def test_repair_fees_derives_v1_rows_exactly(tmp_path):
    con = W._connect(str(tmp_path / "w.sqlite"))
    with con:
        for arm, unf, ex in (("analyst", 0, "target"), ("analyst", 1, "stop"),
                             ("market", 0, "horizon"), ("fixed_rule", 0, "no_rule_setup")):
            con.execute("INSERT INTO walks (setup_id, arm, status, unfilled, exit_reason,"
                        " updated_at) VALUES (?,?,?,?,?,0)", (f"{arm}{unf}", arm, "resolved",
                                                              unf, ex))
    assert W.repair_fees(con) == 4
    got = {r[0]: r[1] for r in con.execute("SELECT setup_id, fees_pct FROM walks")}
    assert got == {"analyst0": 0.04, "analyst1": 0.10, "market0": 0.10, "fixed_rule0": 0.0}
    assert W.repair_fees(con) == 0


# ── funding from the recorder ────────────────────────────────────────────

H = 3_600_000


def _deriv(tmp_path, rows):
    p = str(tmp_path / "d.sqlite")
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE deriv_hourly (hour_ms INTEGER, symbol TEXT, funding_rate REAL,"
                " next_funding_ms INTEGER)")
    con.executemany("INSERT INTO deriv_hourly VALUES (?,?,?,?)", rows)
    con.commit()
    return con


def test_funding_uses_the_symbols_own_settlements(tmp_path):
    # A 4h symbol: settlements at 04:00 and 08:00. Hold 02:30 → 09:30 crosses both.
    day = 1_800_000_000 // 86400 * 86400 * 1000
    rows = [(day + h * H, "X", 0.0001 * (h + 1), day + ((h // 4) + 1) * 4 * H)
            for h in range(0, 12)]
    con = _deriv(tmp_path, rows)
    t0, t1 = (day + 2.5 * H) / 1000, (day + 9.5 * H) / 1000
    v, why = W.funding_cost_pct(con, "X", "long", t0, t1)
    # 04:00 charged at the 03:00 row's rate (0.0004), 08:00 at 07:00's (0.0008).
    assert why == "charged" and abs(v - (0.04 + 0.08)) < 1e-9
    vs, _ = W.funding_cost_pct(con, "X", "short", t0, t1)
    assert abs(vs + v) < 1e-12, "a short receives what a long pays"
    assert W.funding_cost_pct(con, "X", "long", t0, t0 + 600) == (0.0, "none_crossed")


def test_a_recorder_gap_is_unknown_never_zero(tmp_path):
    day = 1_800_000_000 // 86400 * 86400 * 1000
    rows = [(day + h * H, "X", 0.0001, day + 8 * H) for h in (0, 1, 3)]  # 02:00 missing
    con = _deriv(tmp_path, rows)
    assert W.funding_cost_pct(con, "X", "long", day / 1000, (day + 3.5 * H) / 1000) == (
        None, "recorder_gap")
    assert W.funding_cost_pct(con, "Y", "long", day / 1000, (day + H) / 1000) == (
        None, "symbol_not_recorded")


def test_cost_model_stays_unknown_until_funding_is_stamped():
    r = {"arm": "analyst", "status": "resolved", "net_pct": 1.93, "gross_pct": 2.0,
         "fees_pct": 0.04, "funding_pct": None, "filled_frac": 1.0, "unfilled": 0,
         "exit_reason": "target"}
    assert W.realized_pct(r, cost_model=True) is None
    r["funding_pct"] = 0.01
    assert abs(W.realized_pct(r, cost_model=True) - 1.95) < 1e-12


# ── ladder ───────────────────────────────────────────────────────────────


def test_ladder_takes_half_at_tp1_and_rides_half_to_tp2():
    s = _setup()
    s["targets_json"] = json.dumps([{"id": "t1", "price": 103.0}, {"id": "t2", "price": 106.0}])
    cd = _bucket([(100, 100.5, 99.5, 100), (100, 100, 98.8, 99.2), (99.5, 103.5, 99.4, 103),
                  (103, 106.5, 102.5, 106)])
    r = W.walk_setup(s, cd, NOW)["ladder"]
    want = 0.5 * (103 - 99) / 99 * 100 + 0.5 * (106 - 99) / 99 * 100
    assert r["status"] == "resolved" and abs(r["gross_pct"] - want) < 1e-3
    assert r["exit_reason"] == "target" and r["fees_pct"] == 0.04


def test_ladder_runner_keeps_the_original_stop():
    s = _setup()
    s["targets_json"] = json.dumps([{"id": "t1", "price": 103.0}, {"id": "t2", "price": 106.0}])
    cd = _bucket([(100, 100.5, 99.5, 100), (100, 100, 98.8, 99.2), (99.5, 103.5, 99.4, 103),
                  (103, 103, 96.5, 97)])
    r = W.walk_setup(s, cd, NOW)["ladder"]
    want = 0.5 * (103 - 99) / 99 * 100 + 0.5 * (97 - 99) / 99 * 100
    assert abs(r["gross_pct"] - want) < 1e-3 and r["exit_reason"] == "stop+target"


# ── tp1 before fill, and the what-ifs ────────────────────────────────────


def test_tp1_before_fill_is_stamped():
    # Price tags the target first, then comes back to fill the limit.
    cd = _bucket([(100, 103.5, 99.5, 103), (103, 103, 98.8, 99.2), (99.2, 99.5, 96.5, 97)])
    r = W.walk_setup(_setup(), cd, NOW)["analyst"]
    assert r["tp1_before_fill"] == 1 and r["exit_reason"] == "stop"


def test_expiry_whatif_drops_only_late_fills(tmp_path, monkeypatch):
    # Fill after 2.5h, then the target. Under a 2h expiry that fill never happens.
    _ledger(tmp_path, monkeypatch, [{"_setup": {"expiry_h": 4}}])
    bars = FLAT * 30 + [(100, 100, 98.8, 99.2), (99.5, 103.5, 99.4, 103)]
    W.step(type("E", (), {"data_store": _store(bars)})(), now=NOW, deriv_path="")
    wi = W.summary(now=NOW)["analyst_whatif"]
    assert wi["baseline"]["avg_net_pct"] > 0
    assert wi["expiry_2h"]["fills_dropped"] == 1 and wi["expiry_2h"]["avg_net_pct"] == 0.0
    assert wi["expiry_4h"]["fills_dropped"] == 0


# ── the step never overwrites a settled row; v1 tranche rows re-walk ───────


def test_a_settled_row_is_not_overwritten_when_bars_roll_off(tmp_path, monkeypatch):
    _ledger(tmp_path, monkeypatch, [{}])
    con = P.get_ledger()._connect()
    W._migrate(con)
    with con:
        con.execute("INSERT INTO walks (setup_id, arm, status, exit_reason, net_pct, "
                    "updated_at) VALUES ('p:0','analyst','resolved','target',3.0,0)")
    con.close()
    st = HistoricalDataStore()
    st.update_candle("X", "5m", {"open": 1, "high": 1, "low": 1, "close": 1, "volume": 1,
                                 "open_time": (T0 + 3600) * 1000})  # history rolled off
    W.step(type("E", (), {"data_store": st})(), now=NOW, deriv_path="")
    con = sqlite3.connect(P.get_ledger().path)
    got = con.execute("SELECT status, net_pct FROM walks WHERE arm='analyst'").fetchone()
    assert got == ("resolved", 3.0)


@pytest.mark.parametrize("bars_exist", [True, False])
def test_a_v1_blended_tranche_row_is_rewalked_or_refused(tmp_path, monkeypatch, bars_exist):
    _ledger(tmp_path, monkeypatch, [{"_setup": {"entries": ((99.0, 0.4), (98.0, 0.6))}}])
    con = P.get_ledger()._connect()
    W._migrate(con)
    with con:  # the v1 shape: both legs counted, blended
        con.execute("INSERT INTO walks (setup_id, arm, status, unfilled, filled_frac, entry,"
                    " exit_reason, gross_pct, net_pct, updated_at) VALUES "
                    "('p:0','tranche','resolved',0,1.0,98.4,'target',4.67,4.6,0)")
    con.close()
    s0 = W.summary(now=NOW)["by_arm"]["tranche"]
    assert s0["excluded_blend_defect"] == 1 and s0["n"] == 0, "never in an average"
    if bars_exist:
        st = _store([(100, 100.5, 99.5, 100), (100, 100, 98.9, 99.2), (99.5, 103.5, 99.4, 103),
                     (103, 103, 97.9, 98.5)])
    else:
        st = HistoricalDataStore()
        st.update_candle("X", "5m", {"open": 1, "high": 1, "low": 1, "close": 1, "volume": 1,
                                     "open_time": (T0 + 3600) * 1000})
    counts = W.step(type("E", (), {"data_store": st})(), now=NOW, deriv_path="")
    con = sqlite3.connect(P.get_ledger().path)
    row = con.execute("SELECT status, reason, walk_v, filled_frac FROM walks "
                      "WHERE arm='tranche'").fetchone()
    if bars_exist:
        assert counts["tranche_rewalked"] == 1
        assert row == ("resolved", "legs_cancelled_after_exit:1", 2, 0.4)
    else:
        assert counts["tranche_unrewalkable"] == 1
        assert row[:2] == ("insufficient", "blend_defect_history_rolled_off")


def test_step_stamps_funding_from_the_recorder(tmp_path, monkeypatch):
    _ledger(tmp_path, monkeypatch, [{}])
    day0 = int(T0 // 3600) * H
    _deriv(tmp_path, [(day0 + h * H, "X", 0.0001, day0 + 100 * H) for h in range(-1, 3)])
    bars = [(100, 100.5, 99.5, 100), (100, 100, 98.8, 99.2), (99.5, 103.5, 99.4, 103)]
    W.step(type("E", (), {"data_store": _store(bars)})(), now=NOW,
           deriv_path=str(tmp_path / "d.sqlite"))
    con = sqlite3.connect(P.get_ledger().path)
    got = con.execute("SELECT funding_pct, funding_reason FROM walks WHERE arm='analyst'"
                      ).fetchone()
    assert got == (0.0, "none_crossed")
    a = W.summary(now=NOW)["by_arm"]["analyst"]["cost_model"]
    assert a["n"] == 1 and a["unknown"] == 0
    assert abs(a["avg_net_pct"] - ((103 - 99) / 99 * 100 - 0.04)) < 1e-3


# ── the three-outcome forecast ───────────────────────────────────────────


def test_p_stop_is_validated_beside_p_target():
    base = {"symbol": "BTCUSDT", "side": "long", "archetype": "trend_pullback",
            "entry_level_ids": ["a"], "stop_level_id": "s", "target_level_ids": ["t"],
            "invalidation": "x", "p_target": 0.4}
    assert P._parse_setup({**base, "p_stop": 0.35})["p_stop"] == 0.35
    assert P._parse_setup(base)["p_stop"] is None
    for bad in ({**base, "p_stop": 0.7}, {**base, "p_stop": 1.2},
                {k: v for k, v in {**base, "p_stop": 0.3}.items() if k != "p_target"}):
        with pytest.raises(P.Reject):
            P._parse_setup(bad)


def test_three_outcome_brier_scores_target_stop_and_time_exit():
    rows = [{"p_target": 0.5, "p_stop": 0.3, "exit_reason": "target"},
            {"p_target": 0.5, "p_stop": 0.3, "exit_reason": "horizon"},
            {"p_target": 0.5, "p_stop": None, "exit_reason": "stop"}]
    out = W._three_outcome(rows)
    assert out["n"] == 2
    # (0.5-1)^2+0.3^2+0.2^2 = 0.38 ; 0.5^2+0.3^2+(0.2-1)^2 = 0.98 → mean 0.68
    assert out["brier"] == 0.68
    assert out["observed"] == {"target": 0.5, "stop": 0.0, "horizon": 0.5}


def test_cost_model_is_paired_with_the_flat_fee_on_the_same_rows():
    filled = {"arm": "analyst", "status": "resolved", "net_pct": 1.93, "gross_pct": 2.0,
              "fees_pct": 0.04, "funding_pct": None, "filled_frac": 1.0, "unfilled": 0,
              "exit_reason": "target"}
    missed = {"arm": "analyst", "status": "resolved", "net_pct": 3.0, "gross_pct": 3.07,
              "fees_pct": 0.10, "funding_pct": None, "filled_frac": 0.0, "unfilled": 1,
              "exit_reason": "target"}
    c = W._arm_block("analyst", [filled, missed])["cost_model"]
    # Only the miss is priceable (0.00%); the filled row's funding is unknown.
    assert c["n"] == 1 and c["unknown"] == 1 and c["known_filled"] == 0
    assert c["flat_fee_same_rows_avg_pct"] == 0.0
