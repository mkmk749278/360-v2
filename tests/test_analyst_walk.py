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
    assert out["result"]["arms_not_built"] == ["existing_signals"]
    assert by["fixed_rule"]["insufficient"] == 1  # a row with no stamped menu
    # Resolved on every arm → not walked again.
    # Settled on every arm → not walked again. Here the ladder's runner (no TP2
    # in this fixture) is still riding to the horizon, so the setup is owed one.
    assert W.step(eng, now=NOW)["setups"] == 0 or by["market"]["open"] or by["ladder"]["open"]


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


# ── fixed-rule arm (2026-11-20) ───────────────────────────────────────────

MENU = [  # price 100, ATR 1.0
    {"id": "a", "price": 99.0, "side": "below", "distance_atr": -1.0, "score": 70},
    {"id": "b", "price": 99.6, "side": "below", "distance_atr": -0.4, "score": 40},
    {"id": "c", "price": 97.9, "side": "below", "distance_atr": -2.1, "score": 60},
    {"id": "d", "price": 103.0, "side": "above", "distance_atr": 3.0, "score": 80},
    {"id": "e", "price": 100.1, "side": "above", "distance_atr": 0.1, "score": 90},
]


def test_fixed_rule_picks_levels_mechanically():
    lv, why = W.fixed_rule_levels(MENU, 100.0, 1.0, "long")
    # entry: best score within 1.5 ATR below (a, 70); stop: nearest level beyond
    # a giving 0.8-2.5 ATR (c: 99-97.8=1.2); target: best score clearing the
    # cost floor (e at +1.1% beats d's score? e=90 but 1.1% >= 0.21% → e).
    assert why == "" and lv["entry"] == 99.0 and abs(lv["stop"] - 97.8) < 1e-9
    assert lv["target"] == 100.1


def test_fixed_rule_without_a_valid_stop_is_no_setup():
    menu = [m for m in MENU if m["id"] != "c"]
    assert W.fixed_rule_levels(menu, 100.0, 1.0, "long") == (None, "no_stop_level")


def test_fixed_rule_arm_scores_zero_when_no_setup_and_flags_why():
    s = _setup()
    s.update(menu_json=json.dumps([m for m in MENU if m["id"] != "c"]),
             price_at_submit=100.0, atr_1h=1.0)
    r = W.walk_setup(s, _bucket([(100, 100.5, 99.5, 100)]), NOW)["fixed_rule"]
    assert r == {"status": "resolved", "gross_pct": 0.0, "net_pct": 0.0, "fees_pct": 0.0,
                 "exit_reason": "no_rule_setup", "reason": "no_stop_level"}


def test_fixed_rule_arm_walks_its_own_geometry():
    s = _setup()
    s.update(menu_json=json.dumps(MENU), price_at_submit=100.0, atr_1h=1.0)
    cd = _bucket([(100, 100.5, 98.9, 99.5), (99.5, 100.2, 99.4, 100.1)])
    r = W.walk_setup(s, cd, NOW)["fixed_rule"]
    assert r["entry"] == 99.0 and r["exit_reason"] == "target" and r["exit"] == 100.1


def test_a_row_stamped_before_the_menu_is_insufficient_not_guessed():
    r = W.walk_setup(_setup(), _bucket([(100, 100.5, 99.5, 100)]), NOW)["fixed_rule"]
    assert r == {"status": "insufficient", "reason": "no_menu_stamped"}


def test_menu_is_stamped_at_submit_and_old_ledgers_migrate(tmp_path):
    import sqlite3 as _sq

    from src import analyst_plan as P
    p = tmp_path / "old.sqlite"
    con = _sq.connect(p)
    con.executescript(P._SCHEMA.replace(",\n    menu_json     TEXT", ""))
    con.close()
    con = P.Ledger(str(p))._connect()
    assert "menu_json" in {r[1] for r in con.execute("PRAGMA table_info(setups)")}
    con.close()


# ── the feed: setups read as signals (2026-11-22) ─────────────────────────


def _ledger_with(tmp_path, monkeypatch, rows):
    """rows: (setup_id, side, entries, stop, targets) — all accepted, symbol X."""
    from src import analyst_plan as P
    led = P.Ledger(str(tmp_path / "plans.sqlite"))
    monkeypatch.setattr(P, "_ledger", led)
    con = led._connect()
    with con:
        con.execute("INSERT INTO plans (plan_id, submitted_at, bias, notes) "
                    "VALUES ('p', ?, 'neutral', 'n')", (T0,))
        for i, (sid, side, entries, stop, targets) in enumerate(rows):
            con.execute(
                "INSERT INTO setups (setup_id, plan_id, idx, symbol, side, status,"
                " entries_json, stop_price, targets_json, expires_at, submitted_at,"
                " scenario, p_target) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (sid, "p", i, "X", side, "accepted",
                 json.dumps([{"id": "e", "price": p, "weight": w} for p, w in entries]),
                 stop, json.dumps([{"id": "t", "price": t} for t in targets]),
                 T0 + 4 * 3600, T0, "primary", 0.4))
        con.execute(
            "INSERT INTO setups (setup_id, plan_id, idx, symbol, side, status, reason,"
            " submitted_at) VALUES ('p:rej','p',9,'X','long','rejected','geometry',?)", (T0,))
    con.close()
    return led


def test_feed_reads_each_setup_as_a_signal(tmp_path, monkeypatch):
    _ledger_with(tmp_path, monkeypatch, [
        ("p:0", "long", [(99.0, 1.0)], 97.0, [103.0, 105.0]),   # fills, hits TP1
        ("p:1", "long", [(90.0, 1.0)], 88.0, [95.0]),            # never reached
    ])
    st = HistoricalDataStore()
    for i, b in enumerate([(100, 100.5, 99.5, 100), (100, 100, 98.8, 99.2),
                           (99.5, 103.5, 99.4, 103)]):
        st.update_candle("X", "5m", {"open": b[0], "high": b[1], "low": b[2], "close": b[3],
                                     "volume": 1, "open_time": (T0 + 300 * i) * 1000})
    eng = type("E", (), {"data_store": st})()
    W.step(eng, now=NOW)
    out = diag_catalog.run("read.analyst_feed", eng, {"limit": 10})
    assert out["ok"], out
    res = out["result"]
    by = {r["setup_id"]: r for r in res["rows"]}
    assert set(by) == {"p:0", "p:1"}, "rejected setups are not signals"
    hit = by["p:0"]
    assert hit["state"] == "tp_hit" and hit["targets"] == [103.0, 105.0]
    assert hit["rr_tp1"] == 2.0 and hit["analyst"]["net_pct"] > 0
    assert hit["market"] is not None and hit["fixed_rule"] is not None
    # Inside its window an unreached limit is pending — never a fill.
    assert by["p:1"]["state"] == "pending"
    assert res["counts"]["tp_hit"] == 1 and res["counts"]["pending"] == 1
    assert set(res["counts"]) == set(W.FEED_STATES)


def test_feed_states_are_a_closed_set():
    cases = [
        (None, "not_walked"),
        ({"status": "insufficient"}, "insufficient"),
        ({"status": "open", "reason": "awaiting_fill"}, "pending"),
        ({"status": "open", "entry": 1.0}, "active"),
        ({"status": "open", "reason": "no_bars_yet"}, "waiting_data"),
        ({"status": "resolved", "unfilled": 1, "exit_reason": "target"}, "not_filled"),
        ({"status": "open", "unfilled": 1}, "not_filled"),
        ({"status": "resolved", "exit_reason": "target"}, "tp_hit"),
        ({"status": "resolved", "exit_reason": "stop"}, "sl_hit"),
        ({"status": "resolved", "exit_reason": "horizon"}, "time_exit"),
    ]
    for w, want in cases:
        assert W._feed_state(w) == want, (w, want)
        assert want in W.FEED_STATES


def test_feed_without_a_ledger_says_so(tmp_path):
    out = W.feed(path=str(tmp_path / "none.sqlite"))
    assert out == {"readable": False, "reason": "no_ledger_yet", "rows": []}
