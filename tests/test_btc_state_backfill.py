"""Pure-function tests for scripts/btc_state_backfill.

Network/Binance are unreachable in CI and in the dev sandbox, so these prove the
point-in-time math (indicators, no-look-ahead indexing, BTC-State sign, downside
beta, stratification) on synthetic candles. The live kline fetch is exercised only
on the VPS, by design.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "btc_state_backfill", Path(__file__).resolve().parent.parent / "scripts" / "btc_state_backfill.py"
)
bsb = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
sys.modules[_spec.name] = bsb  # dataclasses resolve annotations via sys.modules
_spec.loader.exec_module(bsb)


def _series(closes, *, interval="15m", start_ms=1_700_000_000_000):
    """Build a Series from a close list; OHLC approximated around close, 1 candle/step."""
    step = bsb._INTERVAL_MS[interval]
    rows = []
    for i, c in enumerate(closes):
        ot = start_ms + i * step
        hi = c * 1.002
        lo = c * 0.998
        op = closes[i - 1] if i else c
        rows.append([ot, op, hi, lo, c, 0.0, ot + step - 1])
    return bsb.Series.from_rows(rows)


# ---------------- indicators ----------------
def test_ema_matches_reference():
    vals = [float(i) for i in range(1, 30)]
    e = bsb.ema(vals, 10)
    assert e is not None and 20 < e < 29  # trends up toward the latest values


def test_rsi_all_gains_is_100():
    closes = [100 + i for i in range(20)]
    assert bsb.rsi(closes, 14) == 100.0


def test_atr_positive():
    closes = [100 + (i % 3) for i in range(20)]
    highs = [c + 1 for c in closes]
    lows = [c - 1 for c in closes]
    a = bsb.atr(highs, lows, closes, 14)
    assert a is not None and a > 0


# ---------------- no-look-ahead indexing ----------------
def test_last_closed_idx_excludes_future_and_unclosed():
    s = _series([100.0] * 5, start_ms=1000, interval="5m")
    step = bsb._INTERVAL_MS["5m"]
    # close of candle i is at 1000 + (i+1)*step - 1
    assert s.last_closed_idx(1000) == -1  # nothing closed yet
    assert s.last_closed_idx(1000 + step - 1) == 0  # first candle just closed
    assert s.last_closed_idx(1000 + 3 * step) == 2  # candles 0,1,2 closed; 3 not yet


# ---------------- BTC-State sign ----------------
def test_btc_state_negative_in_downtrend():
    down = [100.0 * (0.995 ** i) for i in range(120)]  # steady decline
    btc = {"5m": _series(down, interval="5m"), "15m": _series(down, interval="15m"),
           "1h": _series(down, interval="1h")}
    ts = btc["15m"].close_ms[-1]
    b = bsb.btc_state_score(btc, ts)
    assert b is not None and b < -0.2, f"expected short-favourable, got {b}"


def test_btc_state_positive_in_uptrend():
    up = [100.0 * (1.005 ** i) for i in range(120)]
    btc = {"5m": _series(up, interval="5m"), "15m": _series(up, interval="15m"),
           "1h": _series(up, interval="1h")}
    ts = btc["15m"].close_ms[-1]
    b = bsb.btc_state_score(btc, ts)
    assert b is not None and b > 0.2, f"expected long-favourable, got {b}"


def test_btc_state_none_when_cold():
    btc = {"15m": _series([100.0] * 5)}
    assert bsb.btc_state_score(btc, btc["15m"].close_ms[-1]) is None


# ---------------- downside beta ----------------
def test_downside_weight_high_for_tracking_pair():
    # Pair = 1.5x BTC moves → downside beta ~1.5, correlation ~1 → high w_pair.
    import random

    random.seed(1)
    btc_cl = [100.0]
    pair_cl = [50.0]
    for _ in range(150):
        r = random.uniform(-0.01, 0.005)  # net-down, volatile
        btc_cl.append(btc_cl[-1] * (1 + r))
        pair_cl.append(pair_cl[-1] * (1 + 1.5 * r))
    btc15 = _series(btc_cl)
    pair = _series(pair_cl)
    res = bsb.pair_downside_weight(pair, btc15, pair.close_ms[-1])
    assert res is not None
    beta_down, corr_down, w = res
    assert 1.0 < beta_down < 2.0, beta_down
    assert corr_down > 0.9, corr_down
    assert w >= 0.6  # BTC_LED band


def test_downside_weight_low_for_decoupled_pair():
    import random

    random.seed(2)
    btc_cl = [100.0]
    pair_cl = [50.0]
    for _ in range(150):
        rb = random.uniform(-0.01, 0.005)
        rp = random.uniform(-0.01, 0.01)  # independent
        btc_cl.append(btc_cl[-1] * (1 + rb))
        pair_cl.append(pair_cl[-1] * (1 + rp))
    res = bsb.pair_downside_weight(_series(pair_cl), _series(btc_cl), 1_700_000_000_000 + 200 * bsb._INTERVAL_MS["15m"])
    # Either too-few aligned points (None) or a low correlation → low weight.
    if res is not None:
        _, corr_down, w = res
        assert w < 0.5, (corr_down, w)


def test_downside_weight_none_few_points():
    btc15 = _series([100.0, 101.0, 102.0])
    pair = _series([50.0, 50.5, 51.0])
    assert bsb.pair_downside_weight(pair, btc15, pair.close_ms[-1]) is None


# ---------------- stratification helpers ----------------
def test_bucket_and_wband_boundaries():
    assert bsb._bucket_state(-0.9) == "5_strong_short"
    assert bsb._bucket_state(-0.3) == "4_short"
    assert bsb._bucket_state(0.0) == "3_neutral"
    assert bsb._bucket_state(0.4) == "2_long"
    assert bsb._bucket_state(0.8) == "1_strong_long"
    assert bsb._wband(0.7) == "BTC_LED"
    assert bsb._wband(0.4) == "INFLUENCED"
    assert bsb._wband(0.1) == "DECOUPLED"


def test_agg_winrate_and_avg():
    rows = [
        {"real_pnl": 1.0, "is_win": True},
        {"real_pnl": -2.0, "is_win": False},
        {"real_pnl": 3.0, "is_win": True},
    ]
    n, wr, avg = bsb._agg(rows)
    assert n == 3
    assert abs(wr - 66.666) < 0.1
    assert abs(avg - (2.0 / 3.0)) < 1e-9


def test_to_ms_handles_s_ms_iso():
    assert bsb._to_ms(1_700_000_000) == 1_700_000_000_000  # seconds → ms
    assert bsb._to_ms(1_700_000_000_000) == 1_700_000_000_000  # already ms
    assert bsb._to_ms("2026-06-30T04:00:00Z") is not None


def test_load_signals_requires_timestamp(tmp_path):
    p = tmp_path / "s.csv"
    p.write_text("symbol,side,real_pnl_pct\nBTCUSDT,LONG,1.2\n")  # no ts column
    assert bsb._load_signals(str(p)) == []


def test_load_signals_prefers_dispatch_over_terminal_timestamp(tmp_path):
    # signal_performance.json shape: dispatch_timestamp = emit, timestamp = close.
    # The harness must reconstruct at dispatch, never the terminal record time.
    rec = {
        "signal_id": "SIG1",
        "symbol": "ethusdt",
        "direction": "SHORT",
        "setup_class": "SR_FLIP_RETEST",
        "dispatch_timestamp": 1_700_000_000,
        "timestamp": 1_700_009_999,  # terminal/close — must be ignored
        "pnl_pct": -0.8,
        "confidence": 72.5,
        "max_favorable_excursion_pct": 1.4,
    }
    p = tmp_path / "perf.json"
    import json as _json

    p.write_text(_json.dumps([rec]))
    sigs = bsb._load_signals(str(p))
    assert len(sigs) == 1
    s = sigs[0]
    assert s.ts_ms == 1_700_000_000_000  # dispatch, in ms — NOT the terminal time
    assert s.symbol == "ETHUSDT" and s.side == "SHORT"
    assert s.signal_id == "SIG1"
    assert s.confidence == 72.5 and s.mfe == 1.4
    assert s.is_win is False  # pnl < 0
