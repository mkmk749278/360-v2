"""Analyst upgrade, 2026-11-25: verified against the live ledger first.

* The walk booked a "target" at a LOSS when the market at submit was already
  past the first target (a short retest whose TP1 is the low price sits on).
  4 of the 19 setups replayed from 2026-11-24 17:37 to 11-25 08:37 did this.
* The analyst could not see its own open book (it read 3 plans and guessed),
  and the outcomes headline pooled fills with market-scored limits.
"""
from __future__ import annotations

import sqlite3

from src import analyst_charts as C
from src import analyst_plan as P
from src import analyst_walk as W
from src.historical_data import HistoricalDataStore
from tests.test_analyst_charts import _eng, _price_plan
from tests.test_analyst_snapshot import NOW as SNAP_NOW, _seed
from tests.test_analyst_walk import NOW, T0, _bucket, _ledger_with, _setup

ADMIT = lambda s: (True, "")  # noqa: E731


# ── walk: a market entry already past its own target / stop ──────────────────


def test_short_whose_market_entry_is_past_tp1_is_no_trade_not_a_losing_target():
    # Short retest: limit 105 above, stop 107, TP1 101. Price at submit is 100,
    # already below TP1. The old walk booked "target" at 101: a -1% "win".
    bars = [(100, 100.4, 99.6, 100)] * (4 * 12 + 2)
    r = W.walk_setup(_setup(side="short", entries=((105.0, 1.0),), stop=107.0,
                            target=101.0), _bucket(bars), NOW)
    m = r["market"]
    assert m["exit_reason"] == "no_valid_trade" and m["reason"] == "entry_past_target"
    assert m["net_pct"] == 0.0 and m["gross_pct"] == 0.0
    a = r["analyst"]  # the limit never filled, so it is scored at market
    assert a["unfilled"] == 1 and a["exit_reason"] == "no_valid_trade" and a["net_pct"] == 0.0
    assert W._feed_state(a) == "not_filled"


def test_long_breakout_whose_market_entry_is_below_its_stop_is_no_trade():
    # Breakout long: limit 103 above price, stop 101, target 106; price 100.
    bars = [(100, 100.4, 99.6, 100)] * 3
    m = W.walk_setup(_setup(entries=((103.0, 1.0),), stop=101.0, target=106.0),
                     _bucket(bars), NOW)["market"]
    assert m["exit_reason"] == "no_valid_trade" and m["reason"] == "entry_past_stop"


def test_a_valid_market_entry_still_walks():
    cd = _bucket([(100, 100.5, 99.5, 100), (100, 103.5, 99.6, 103)])
    m = W.walk_setup(_setup(), cd, NOW)["market"]
    assert m["exit_reason"] == "target" and m["net_pct"] > 0


def test_stored_rows_walked_before_the_fix_are_repaired_from_their_own_fields(
        tmp_path, monkeypatch):
    led = _ledger_with(tmp_path, monkeypatch, [
        ("p:0", "short", [(105.0, 1.0)], 107.0, [101.0]),
        ("p:1", "long", [(99.0, 1.0)], 97.0, [103.0]),
    ])
    con = sqlite3.connect(led.path)
    con.row_factory = sqlite3.Row
    con.execute(W._SCHEMA)
    with con:
        # p:0 market entry 100 below the short's TP1 101: the old defect.
        for sid, arm, unf, entry, exit_reason, net in (
                ("p:0", "market", 0, 100.0, "target", -1.07),
                ("p:0", "analyst", 1, 100.0, "target", -1.07),
                ("p:1", "market", 0, 100.0, "target", 2.93)):
            con.execute("INSERT INTO walks (setup_id, arm, status, unfilled, entry, "
                        "exit_reason, net_pct, gross_pct, updated_at) VALUES "
                        "(?,?,'resolved',?,?,?,?,?,0)", (sid, arm, unf, entry,
                                                           exit_reason, net, net + 0.07))
    assert W.repair_geometry(con) == 2
    got = {(r["setup_id"], r["arm"]): dict(r) for r in con.execute("SELECT * FROM walks")}
    assert got[("p:0", "market")]["net_pct"] == 0.0
    assert got[("p:0", "analyst")]["reason"] == "entry_past_target"
    assert got[("p:1", "market")]["net_pct"] == 2.93  # a valid row is untouched
    assert W.repair_geometry(con) == 0  # idempotent
    con.close()


# ── outcomes: split, three exits, the open book, the journal ───────────────────


def test_outcomes_split_fills_from_market_scores_and_show_the_open_book(tmp_path, monkeypatch):
    _ledger_with(tmp_path, monkeypatch, [
        ("p:0", "long", [(99.0, 1.0)], 97.0, [103.0]),   # fills, hits TP1
        ("p:1", "long", [(90.0, 1.0)], 88.0, [95.0]),     # never reached: pending
        ("p:2", "short", [(104.0, 1.0)], 106.0, [98.0]),  # short, still pending
    ])
    st = HistoricalDataStore()
    for i, b in enumerate([(100, 100.5, 99.5, 100), (100, 100, 98.8, 99.2),
                           (99.5, 103.5, 99.4, 103)]):
        st.update_candle("X", "5m", {"open": b[0], "high": b[1], "low": b[2], "close": b[3],
                                     "volume": 1, "open_time": (T0 + 300 * i) * 1000})
    W.step(type("E", (), {"data_store": st})(), now=NOW)
    out = W.summary(now=T0 + 3 * 300)
    sp = out["analyst_split"]
    assert sp["filled"]["n"] == 1 and sp["filled_by_exit"]["target"]["n"] == 1
    bk = out["active_book"]
    assert bk["by_side"] == {"long": 1, "short": 1}, bk
    assert {i["state"] for i in bk["setups"]} <= set(W.OPEN_STATES)
    rc = out["recent_closed"]
    assert len(rc) == 1 and rc[0]["state"] == "tp_hit" and rc[0]["net_pct"] > 0


# ── submit: stamps, the book count, the prompt version ─────────────────────────


def test_submit_stamps_range_position_entry_distance_and_the_book(tmp_path, monkeypatch):
    led = P.Ledger(str(tmp_path / "plans.sqlite"))
    monkeypatch.setattr(P, "_ledger", led)
    eng = _eng()
    plan, p, atr = _price_plan(eng)
    plan["prompt_version"] = "v2-2026-11-25"
    out = P.submit(plan, eng, source="t", now=SNAP_NOW, admission=ADMIT)
    s = out["setups"][0]
    assert s["status"] == "accepted", s
    from src import analyst_snapshot as A
    snap = A.pair_snapshot(eng, "ETHUSDT", now=SNAP_NOW)
    assert abs(s["entry_dist_atr"] - abs(p - 0.5 * atr - snap["price"]) / atr) < 1e-3
    # Not clamped: price above the closed-bar 7d high reads > 1.
    assert isinstance(s["pos_in_7d"], float) and s["book_same_side"] == 0
    assert out["open_book_after"] == {"long": 1, "short": 0}
    # A second plan an hour later sees the first as still open on its side.
    plan2, _, _ = _price_plan(eng)
    out2 = P.submit(plan2, eng, source="t", now=SNAP_NOW + 60, admission=ADMIT)
    assert out2["setups"][0]["book_same_side"] == 1
    con = sqlite3.connect(led.path)
    assert con.execute("SELECT prompt_version FROM plans ORDER BY submitted_at").fetchall() \
        == [("v2-2026-11-25",), (None,)]
    con.close()


def test_open_book_drops_setups_the_walk_has_resolved(tmp_path, monkeypatch):
    led = _ledger_with(tmp_path, monkeypatch, [
        ("p:0", "long", [(99.0, 1.0)], 97.0, [103.0]),
        ("p:1", "short", [(101.0, 1.0)], 103.0, [97.0]),
    ])
    assert led.open_book(T0 + 60) == {"long": 1, "short": 1}  # no walks table yet
    con = sqlite3.connect(led.path)
    con.execute(W._SCHEMA)
    with con:
        con.execute("INSERT INTO walks (setup_id, arm, status, updated_at) "
                    "VALUES ('p:0','analyst','resolved',0)")
    con.close()
    assert led.open_book(T0 + 60) == {"long": 0, "short": 1}
    # The stub check must not have created a walks table the walker can't use.
    W.step(type("E", (), {"data_store": HistoricalDataStore()})(), now=T0 + 60)


# ── scan: stale pairs listed apart ────────────────────────────────────────────


def test_scan_lists_stale_pairs_apart_instead_of_in_rows():
    eng = _eng()
    eng.data_store.candles["SOLUSDT"].pop("1h", None)
    _seed(eng.data_store, "SOLUSDT", "1h", 200, 150.0, 0.0, stale_bars=12)
    out = C.scan(eng, now=SNAP_NOW)
    assert "SOLUSDT" not in {r["symbol"] for r in out["rows"]}
    assert out["stale"] == [{"symbol": "SOLUSDT", "bars_behind": 12}]


def test_no_summary_key_shadows_a_dict_method(tmp_path, monkeypatch):
    """Ops renders these through Jinja, where ``x.items`` is dict.items before
    the key: ops paid for this on ``keys``, ``copy`` and ``values``."""
    _ledger_with(tmp_path, monkeypatch, [("p:0", "long", [(99.0, 1.0)], 97.0, [103.0])])
    out = W.summary(now=T0 + 60)
    methods = set(dir({}))
    for block in (out, out["analyst_split"], out["active_book"]):
        assert not set(block) & methods, set(block) & methods
