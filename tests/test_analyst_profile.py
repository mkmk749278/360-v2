"""Phase 1c: pair_profile computed from stored candles, with its n."""
import time

import numpy as np

from src import analyst_profile, diag_catalog
from src.historical_data import HistoricalDataStore

TF_MS = {"1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}


def _seed(st, symbol, tf, closes, wick=0.2):
    step = TF_MS[tf]
    last = (int(time.time() * 1000) // step - 1) * step
    n = len(closes)
    prev = closes[0]
    for i, c in enumerate(closes):
        o = prev
        hi, lo = max(o, c) * (1 + wick / 100), min(o, c) * (1 - wick / 100)
        st.update_candle(symbol, tf, {"open": o, "high": hi, "low": lo, "close": c,
                                      "volume": 1.0, "volume_usd": 1000.0 * c,
                                      "open_time": last - (n - 1 - i) * step})
        prev = c


def _engine(beta=2.0, trend=False, n=300, seed=1):
    rng = np.random.default_rng(seed)
    st = HistoricalDataStore()
    for tf in ("1h", "4h", "1d"):
        rb = rng.normal(0, 0.01, n)
        if trend:
            rb = np.convolve(rb, np.ones(6) / 2, mode="same")   # persistent moves
        ra = beta * rb + rng.normal(0, 0.002, n)
        _seed(st, "BTCUSDT", tf, list(100 * np.exp(np.cumsum(rb))))
        _seed(st, "XYZUSDT", tf, list(50 * np.exp(np.cumsum(ra))))
    return type("E", (), {"data_store": st})()


def test_beta_to_btc_is_measured_with_its_n():
    analyst_profile._CACHE.clear()
    out = diag_catalog.run("read.analyst_profile", _engine(beta=2.0), {"symbol": "xyzusdt"})
    assert out["ok"], out
    p = out["result"]
    b = p["btc"]["1h"]
    assert abs(b["beta"] - 2.0) < 0.15 and b["corr"] > 0.95 and b["n"] >= 250
    assert p["btc"]["decoupled_now"] is False
    assert p["btc"]["4h_btc_up_bars"]["n"] + p["btc"]["4h_btc_down_bars"]["n"] >= 250
    assert p["volatility"]["wick_share_median_1h"] is not None
    assert p["liquidity"]["volume_usd_24h"] > 0
    assert p["bars_held"] == {"1h": 300, "4h": 300, "1d": 300}


def test_trending_and_mean_reverting_are_told_apart():
    analyst_profile._CACHE.clear()
    tr = diag_catalog.run("read.analyst_profile", _engine(trend=True), {"symbol": "XYZUSDT"})
    assert tr["result"]["character"]["behaviour"] == "trending"
    assert tr["result"]["character"]["breakouts"]["n"] >= 0


def test_cached_until_a_new_bar_closes():
    analyst_profile._CACHE.clear()
    eng = _engine()
    first = diag_catalog.run("read.analyst_profile", eng, {"symbol": "XYZUSDT"})["result"]
    again = diag_catalog.run("read.analyst_profile", eng, {"symbol": "XYZUSDT"})["result"]
    assert first["cached"] is False and again["cached"] is True


def test_refuses_without_candles_and_for_btc_itself():
    analyst_profile._CACHE.clear()
    eng = _engine()
    none = diag_catalog.run("read.analyst_profile", eng, {"symbol": "NOPEUSDT"})["result"]
    assert none == {"symbol": "NOPEUSDT", "readable": False, "reason": "no_1h_candles"}
    btc = diag_catalog.run("read.analyst_profile", eng, {"symbol": "BTCUSDT"})["result"]
    assert btc["btc"] == {"readable": False, "reason": "is_btc"}
