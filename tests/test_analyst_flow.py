"""Phase 1b: pair_flow serves the engine's order-flow data with its coverage."""
import time

import pytest

from src import depth_book, diag_catalog, footprint
from src.historical_data import HistoricalDataStore
from src.order_flow import LiquidationEvent, OrderFlowStore


@pytest.fixture(autouse=True)
def _fresh_stores():
    footprint.reset_store()
    depth_book.reset_store()
    yield
    footprint.reset_store()
    depth_book.reset_store()


def _engine(symbol="XYZUSDT", price=100.0):
    st = HistoricalDataStore()
    st.update_candle(symbol, "5m", {"open": price, "high": price, "low": price,
                                    "close": price, "volume": 1,
                                    "open_time": int(time.time() * 1000) - 600_000})
    flow = OrderFlowStore()
    return type("E", (), {"data_store": st, "_order_flow_store": flow})(), flow


def test_every_block_reports_whether_it_could_be_read():
    eng, flow = _engine()
    out = diag_catalog.run("read.analyst_flow", eng, {"symbol": "xyzusdt"})
    assert out["ok"], out
    r = out["result"]
    assert r["symbol"] == "XYZUSDT" and r["last_price"] == 100.0
    # Nothing recorded: liquidations still READABLE (the stream covers every pair,
    # so zero is a fact), footprint and depth are NOT (not covered is unknown).
    assert r["liquidations"]["readable"] is True
    assert r["liquidations"]["windows"]["1h"]["longs_liquidated_usd"] == 0.0
    assert r["footprint"] == {"readable": False, "reason": "not_covered_or_no_bars",
                              "note": r["footprint"]["note"]}
    assert r["depth"]["readable"] is False and r["depth"]["reason"] == "not_covered"
    assert r["coverage"]["footprint"] is False and r["coverage"]["liquidations"] is True


def test_liquidations_split_longs_from_shorts():
    eng, flow = _engine()
    now = time.monotonic()
    flow.add_liquidation(LiquidationEvent(now - 60, "XYZUSDT", "SELL", 10.0, 100.0))
    flow.add_liquidation(LiquidationEvent(now - 30, "XYZUSDT", "BUY", 2.0, 101.0))
    flow.add_liquidation(LiquidationEvent(now - 7200, "XYZUSDT", "SELL", 5.0, 99.0))
    liq = diag_catalog.run("read.analyst_flow", eng, {"symbol": "XYZUSDT"})["result"]["liquidations"]
    assert liq["windows"]["15m"] == {"longs_liquidated_usd": 1000.0,
                                     "shorts_liquidated_usd": 202.0}
    assert liq["windows"]["4h"]["longs_liquidated_usd"] == 1495.0
    assert liq["clusters_1h"], "recent events cluster by price"


def test_footprint_ladder_and_depth_from_the_real_stores():
    eng, _ = _engine()
    fp = footprint.get_store()
    t0 = (int(time.time() * 1000) // 60_000 - 5) * 60_000
    for m in range(4):                       # 3 sealed bars, sellers at 100.4
        ts = t0 + m * 60_000 + 1000
        fp.add_row("XYZUSDT", {"price": 100.4, "quote": 5000.0, "time": ts,
                             "aggressor": "SELL"})
        fp.add_row("XYZUSDT", {"price": 99.6, "quote": 1000.0, "time": ts + 10,
                             "aggressor": "BUY"})
    depth_book.get_store().update("XYZUSDT", {"b": [["99.9", "10"], ["99.8", "10"]],
                                            "a": [["100.1", "2"], ["100.2", "2"]],
                                            "E": 1})
    r = diag_catalog.run("read.analyst_flow", eng, {"symbol": "XYZUSDT"})["result"]
    f = r["footprint"]
    assert f["readable"] and f["bars"] == 3
    assert f["delta_usd"]["all"] == pytest.approx(3 * (1000.0 - 5000.0))
    top = max(f["ladder"], key=lambda row: abs(row["delta_usd"]))
    assert top["sell_usd"] == pytest.approx(15000.0) and top["price_from"] <= 100.4 < top["price_to"]
    d = r["depth"]
    assert d["readable"] and d["best_bid"] == 99.9 and d["best_ask"] == 100.1
    assert d["top_5"]["imbalance"] > 0, "more resting bids than asks"
    assert d["spread_bps"] == pytest.approx(20.0, abs=0.01)


def test_a_dead_block_is_reported_and_does_not_hide_the_rest(monkeypatch):
    from src import analyst_flow, fail_open

    eng, _ = _engine()
    seen = []
    monkeypatch.setattr(fail_open, "record", lambda site, exc: seen.append(site))
    monkeypatch.setattr(analyst_flow, "depth", lambda s: 1 / 0)
    r = diag_catalog.run("read.analyst_flow", eng, {"symbol": "XYZUSDT"})["result"]
    assert r["depth"] == {"readable": False, "reason": "error: ZeroDivisionError"}
    assert r["liquidations"]["readable"] is True
    assert seen == ["analyst_flow.depth"]
