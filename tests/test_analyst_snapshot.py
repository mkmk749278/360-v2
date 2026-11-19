"""Analyst read model (step 1 of docs/AI_ANALYST_SPEC_2026_11_19.md).

Candles go through the real ``HistoricalDataStore.update_candle`` so the module
is exercised on the production numpy shape, never hand-built lists.
"""
from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from src import analyst_snapshot as A
from src import diag_catalog
from src.historical_data import HistoricalDataStore
from src.level_book import Level

NOW = 1_800_000_000.0  # fixed clock
H = 3_600_000
TF_STEP = {"15m": 900_000, "1h": H, "4h": 4 * H, "1d": 24 * H, "1w": 168 * H}


def _seed(store, symbol, tf, n, start, drift, *, stale_bars=0):
    step = TF_STEP[tf]
    last_open = (int(NOW * 1000) // step) * step - step - stale_bars * step
    for i in range(n):
        c = start * (1 + drift) ** i
        store.update_candle(symbol, tf, {
            "open": c, "high": c * 1.004, "low": c * 0.996, "close": c,
            "volume": 10.0, "open_time": float(last_open - (n - 1 - i) * step),
        })


def _engine(symbols=("BTCUSDT", "ETHUSDT", "SOLUSDT"), levels=None, vp=None):
    store = HistoricalDataStore()
    for k, s in enumerate(symbols):
        drift = {"BTCUSDT": 0.001, "ETHUSDT": 0.002, "SOLUSDT": -0.001}.get(s, 0.0)
        start = {"BTCUSDT": 90000.0, "ETHUSDT": 3000.0}.get(s, 150.0)
        for tf, n in (("15m", 120), ("1h", 120), ("4h", 120), ("1d", 60), ("1w", 30)):
            _seed(store, s, tf, n, start, drift)
    lb = SimpleNamespace(get_levels=lambda sym: list((levels or {}).get(sym, [])))
    vps = SimpleNamespace(get=lambda sym: (vp or {}).get(sym))
    scanner = SimpleNamespace(level_book=lb, volume_profile_store=vps,
                              volume_profile_store_macro=SimpleNamespace(get=lambda s: None))
    return SimpleNamespace(data_store=store, _scanner=scanner,
                           pair_mgr=SimpleNamespace(pairs={s: object() for s in symbols}))


def test_level_menu_refuses_without_atr_rather_than_scoring_blind():
    out = A.level_menu(100.0, None, [], {})
    assert out == {"levels": [], "refused": "no_atr_1h"}


def test_level_menu_scores_confluence_and_splits_sides():
    lv = [Level(price=101.0, type="resistance", source_tf="1d", touches=1),
          Level(price=95.0, type="support", source_tf="1h", touches=5)]
    tfc = {"1d": {"high": np.array([101.1]), "low": np.array([90.0])}}
    out = A.level_menu(100.0, 1.0, lv, tfc)
    by_id = {x["id"]: x for x in out["levels"]}
    swing = by_id[A.level_id("swing_1d", 101.0)]
    # 1d swing (25) + fresh (20) + confluent with the PDH 0.1 away (8)
    assert swing["score"] == 53.0
    assert swing["side"] == "above" and swing["distance_atr"] == 1.0
    weak = by_id[A.level_id("swing_1h", 95.0)]
    assert weak["side"] == "below" and weak["score_parts"]["freshness"] == -5.0
    assert all(0 <= x["score"] <= 100 for x in out["levels"])


def test_prior_day_comes_from_the_newest_closed_bar():
    # level_menu is handed CLOSED bars (closed_bars), so [-1] IS the prior day.
    tfc = {"1d": {"high": np.array([110.0, 120.0]), "low": np.array([90.0, 80.0])}}
    out = A.level_menu(100.0, 2.0, [], tfc)
    ids = {x["id"] for x in out["levels"]}
    assert A.level_id("pdh", 120.0) in ids and A.level_id("pdl", 80.0) in ids
    assert A.level_id("pdh", 110.0) not in ids


def test_bar_freshness_flags_a_frozen_series_and_refuses_undated_bars():
    store = HistoricalDataStore()
    _seed(store, "X", "1h", 50, 1.0, 0.0, stale_bars=5)
    f = A.bar_freshness(store.candles["X"]["1h"], "1h", NOW * 1000)
    assert f["readable"] and f["bars_behind"] == 5 and f["stale"]
    store2 = HistoricalDataStore()
    store2.update_candle("Y", "1h", {"open": 1, "high": 1, "low": 1, "close": 1, "volume": 1})
    assert A.bar_freshness(store2.candles["Y"]["1h"], "1h", NOW * 1000)["readable"] is False


def test_pair_snapshot_on_the_real_store_shape():
    eng = _engine(levels={"ETHUSDT": [Level(price=3000 * 1.002 ** 119 * 1.01,
                                            type="resistance", source_tf="4h")]})
    snap = A.pair_snapshot(eng, "ETHUSDT", now=NOW)
    assert snap["readable"] and snap["any_stale"] is False
    assert snap["atr"]["1h"] and snap["atr"]["1h_pct"] > 0
    assert snap["trend"]["1h"] is not None and snap["trend"]["1h"] > 0
    assert snap["rel_strength_vs_btc_7d"] > 0  # ETH drifts faster than BTC
    assert snap["levels"]["levels"], snap["levels"]
    assert snap["unlocks"]["readable"] in (True, False)


def test_pair_snapshot_unknown_symbol_is_a_named_refusal():
    snap = A.pair_snapshot(_engine(), "NOPEUSDT", now=NOW)
    assert snap == {"symbol": "NOPEUSDT", "readable": False, "reason": "no_candles_in_store"}


def test_breadth_counts_n_and_never_includes_btc():
    b = A.altcoin_breadth(_engine(), ["BTCUSDT", "ETHUSDT", "SOLUSDT", "MISSINGUSDT"])
    assert b["readable"] and b["n"] == 2 and b["missing"] == 1
    assert b["share_beating_btc_7d"] == 0.5


def test_market_context_says_macro_is_unknown_not_empty():
    m = A.market_context(_engine(), now=NOW)
    assert m["macro_calendar"]["readable"] is False
    assert "never as 'no events'" in m["macro_calendar"]["reason"]
    assert m["btc"]["state_status"] == "ok" and m["universe_size"] == 3


def test_watchlist_counts_refusals_by_reason():
    eng = _engine()
    eng.pair_mgr.pairs["GHOSTUSDT"] = object()
    w = A.watchlist(eng, now=NOW)
    assert w["refused"].get("no_candles_in_store") == 1
    for r in w["rows"]:
        assert r["level"]["score"] >= A.WATCH_MIN_SCORE
        assert abs(r["level"]["distance_atr"]) <= A.WATCH_MAX_ATR


@pytest.mark.parametrize("key", ["read.analyst_market", "read.analyst_pair",
                                 "read.analyst_watchlist"])
def test_catalog_entries_run_against_the_engine_shape(key):
    out = diag_catalog.run(key, _engine(), {"symbol": "ETHUSDT"})
    assert out["ok"], out


def test_analyst_pair_refuses_a_non_symbol():
    out = diag_catalog.run("read.analyst_pair", _engine(), {"symbol": "ETH/USDT;"})
    assert "refused" in out["result"]


def test_candle_census_reads_the_real_store_attribute():
    # It read `_data` / `data`, which HistoricalDataStore does not have, and so
    # raised on every production run. Driven against the real store.
    out = diag_catalog.run("read.candle_census", _engine(), {})
    assert out["ok"], out
    assert out["result"]["per_timeframe"]["1h"]["buckets"] == 3


# ── 2026-11-19: frozen 1d / forming-bar fixes ─────────────────────────────


def _forming(store, symbol, tf, high):
    """Append Binance's FORMING bar, as a REST seed leaves it."""
    step = TF_STEP[tf]
    store.update_candle(symbol, tf, {
        "open": 1.0, "high": high, "low": 0.5, "close": 1.0, "volume": 1.0,
        "open_time": float((int(NOW * 1000) // step) * step)})


def test_closed_bars_drops_the_forming_bar_and_keeps_closed_ones():
    store = HistoricalDataStore()
    _seed(store, "X", "1d", 10, 1.0, 0.0)
    _forming(store, "X", "1d", 9.0)
    cd = store.candles["X"]["1d"]
    closed = A.closed_bars(cd, "1d", NOW * 1000)
    assert len(closed["close"]) == 10 and len(closed["open_time"]) == 10
    assert float(closed["high"][-1]) != 9.0
    # Already closed: untouched.
    assert A.closed_bars(closed, "1d", NOW * 1000) is closed


def test_prior_day_high_is_not_todays_partial_bar():
    # A REST seed leaves the forming bar in the store; PDH used to be its high.
    eng = _engine()
    _forming(eng.data_store, "ETHUSDT", "1d", 99999.0)
    snap = A.pair_snapshot(eng, "ETHUSDT", now=NOW)
    ids = {x["id"] for x in snap["levels"]["levels"]}
    assert A.level_id("pdh", 99999.0) not in ids
    assert snap["bar_freshness"]["1d"]["bars_behind"] == 0


def test_weekly_freshness_does_not_assume_epoch_aligned_weeks():
    # Binance weeks open Monday 00:00 UTC; the epoch began on a Thursday.
    monday = 1_799_625_600_000.0  # a Monday 00:00 UTC
    assert (monday / 86_400_000 + 3) % 7 == 0  # day 0 was Thursday
    cd = {"open_time": np.array([monday - TF_STEP["1w"]]), "close": np.array([1.0])}
    now_ms = monday + 3 * 86_400_000  # Thursday of the forming week
    f = A.bar_freshness(cd, "1w", now_ms)
    assert f["readable"] and f["bars_behind"] == 0 and not f["stale"]


def test_breadth_counts_stale_pairs_apart_instead_of_comparing_them():
    eng = _engine(symbols=("BTCUSDT", "ETHUSDT"))
    _seed(eng.data_store, "SOLUSDT", "1d", 30, 150.0, 0.01, stale_bars=16)
    out = A.altcoin_breadth(eng, ["BTCUSDT", "ETHUSDT", "SOLUSDT"], now_ms=NOW * 1000)
    assert out["readable"] and out["n"] == 1 and out["stale"] == 1


def test_breadth_refuses_when_btc_itself_is_frozen():
    eng = _engine(symbols=("ETHUSDT",))
    _seed(eng.data_store, "BTCUSDT", "1d", 30, 90000.0, 0.0, stale_bars=16)
    out = A.altcoin_breadth(eng, ["BTCUSDT", "ETHUSDT"], now_ms=NOW * 1000)
    assert out == {"readable": False, "reason": "btc_1d_stale_or_undated"}


def test_candle_census_names_frozen_buckets(monkeypatch):
    import time as _t
    monkeypatch.setattr(_t, "time", lambda: NOW)
    eng = _engine()
    _seed(eng.data_store, "FROZUSDT", "1d", 30, 1.0, 0.0, stale_bars=16)
    res = diag_catalog.run("read.candle_census", eng, {})["result"]
    assert res["per_timeframe"]["1d"]["stale"] == 1
    assert res["per_timeframe"]["1h"]["stale"] == 0
    assert res["stalest"]["1d"][0] == {"symbol": "FROZUSDT", "bars_behind": 16}
