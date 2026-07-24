"""Unit tests for the pure core of scripts/exit_method_backtest.py.

The heavy pipeline (Binance fetch + engine ``Backtester``) is validated on the
VPS; here we lock down the *deterministic* parts that don't need network or numpy:
the ported trailing-exit simulator, the candle_index -> timestamp mapping, and the
robustness aggregation (profit factor, drop-top-N, median, per-regime). These are
the numbers a promote/kill decision rests on, so they get real tests.

Importing the module must NOT pull numpy or the engine — those imports are lazy
inside ``run_entries_for_symbol``. If this import ever starts failing on numpy,
that laziness has regressed.
"""
from __future__ import annotations

import importlib.util
import os
import sys

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "exit_method_backtest",
    os.path.join(os.path.dirname(__file__), "..", "scripts", "exit_method_backtest.py"),
)
ex = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
# Register before exec: dataclasses under `from __future__ import annotations`
# resolve field types via sys.modules[cls.__module__] during class creation.
sys.modules[_SPEC.name] = ex
_SPEC.loader.exec_module(ex)


# --------------------------------------------------------------------------- #
# Bars helpers
# --------------------------------------------------------------------------- #
def _rows_from_ohlc(seq, start_ms=0, step_min=15):
    """(open_ms, o, h, l, c, vol) tuples from a list of (o,h,l,c)."""
    step = step_min * 60_000
    return [(start_ms + i * step, o, h, lo, c, 1000.0)
            for i, (o, h, lo, c) in enumerate(seq)]


# --------------------------------------------------------------------------- #
# profit_factor
# --------------------------------------------------------------------------- #
def test_profit_factor_basic():
    assert ex.profit_factor([2.0, -1.0, 3.0, -1.0]) == pytest.approx(2.5)


def test_profit_factor_no_losers_is_inf():
    assert ex.profit_factor([1.0, 2.0]) == float("inf")


def test_profit_factor_no_winners_is_zero():
    assert ex.profit_factor([-1.0, -2.0]) == 0.0
    assert ex.profit_factor([]) == 0.0


# --------------------------------------------------------------------------- #
# method_stats + drop-top-N robustness
# --------------------------------------------------------------------------- #
def _rec(pnl_engine, symbol="BTCUSDT", regime="RANGING", ms=0):
    return ex.SignalRecord(
        symbol=symbol, entry_ms=ms, direction="LONG", setup_class="SR_FLIP_RETEST",
        regime=regime, entry=100.0, pnl={"engine": pnl_engine},
    )


def test_method_stats_totals_and_median():
    recs = [_rec(v) for v in (10.0, -1.0, -1.0, -1.0)]
    s = ex.method_stats(recs, "engine")
    assert s.n == 4
    assert s.total == pytest.approx(7.0)
    assert s.avg == pytest.approx(1.75)
    assert s.median == pytest.approx(-1.0)          # median is negative — the tell
    assert s.win_rate == pytest.approx(25.0)
    assert s.pf == pytest.approx(10.0 / 3.0)


def test_drop_top_n_kills_a_single_outlier_edge():
    # One winner carries the whole book — exactly the SAR-15m fragility pattern.
    recs = [_rec(v) for v in (30.0, -1.0, -1.0, -1.0, -1.0)]
    s = ex.method_stats(recs, "engine")
    assert s.pf > 1.0                                # looks like an edge...
    d1_total, d1_pf = s.drop_top[1]
    assert d1_total == pytest.approx(-4.0)           # ...gone after dropping top 1
    assert d1_pf == 0.0                              # no winners left


def test_method_stats_ignores_none_pnls():
    recs = [_rec(5.0), _rec(None), _rec(-2.0)]  # type: ignore[arg-type]
    s = ex.method_stats(recs, "engine")
    assert s.n == 2
    assert s.total == pytest.approx(3.0)


# --------------------------------------------------------------------------- #
# per_regime_pf
# --------------------------------------------------------------------------- #
def test_per_regime_pf_buckets_by_regime():
    recs = [
        _rec(2.0, regime="RANGING"),
        _rec(-1.0, regime="RANGING"),
        _rec(-5.0, regime="TRENDING_UP"),
    ]
    out = ex.per_regime_pf(recs, "engine")
    assert out["RANGING"] == (2, pytest.approx(1.0), pytest.approx(2.0))
    assert out["TRENDING_UP"][0] == 1
    assert out["TRENDING_UP"][2] == 0.0              # only a loser -> PF 0


# --------------------------------------------------------------------------- #
# find_entry_idx + resample
# --------------------------------------------------------------------------- #
def test_resample_aggregates_within_bucket():
    # Three 5m rows inside one 15m bucket -> one bar with OHLC aggregated.
    rows = [(0, 100.0, 105.0, 99.0, 101.0, 1.0),
            (5 * 60_000, 101.0, 108.0, 100.0, 107.0, 1.0),
            (10 * 60_000, 107.0, 107.5, 95.0, 96.0, 1.0)]
    bars = ex.resample(rows, 15)
    assert len(bars) == 1
    b = bars[0]
    assert (b.open, b.high, b.low, b.close) == (100.0, 108.0, 95.0, 96.0)


def test_find_entry_idx_picks_bucket_covering_dispatch():
    bars = [ex.Bar(0, 1, 1, 1, 1), ex.Bar(15 * 60_000, 1, 1, 1, 1),
            ex.Bar(30 * 60_000, 1, 1, 1, 1)]
    # dispatch at 20 min falls inside the [15m, 30m) bucket -> index 1.
    assert ex.find_entry_idx(bars, 20 * 60_000, 15) == 1
    # dispatch beyond the last bucket -> None.
    assert ex.find_entry_idx(bars, 99 * 60_000, 15) is None


# --------------------------------------------------------------------------- #
# simulate_trailing_exit — behavioural invariants
# --------------------------------------------------------------------------- #
def test_trailing_exit_no_data_when_entry_past_series():
    bars = [ex.Bar(0, 1, 1, 1, 1)]
    tr = ex.simulate_trailing_exit(
        bars, 5, 1.0, "LONG", "sar",
        period=10, mult=3.0, sar_step=0.02, sar_max=0.2,
        tf_min=15, fee_pct=0.07, funding_bps_per_8h=1.0)
    assert tr.reason == "no-data"
    assert tr.result_pct is None


def test_trailing_exit_long_runs_open_in_monotonic_uptrend():
    # Steady uptrend: a trailing long is never stopped -> still open, gross > 0.
    seq = [(100 + i, 100 + i + 0.5, 100 + i - 0.2, 100 + i + 0.4) for i in range(40)]
    bars = ex.resample(_rows_from_ohlc(seq), 15)
    tr = ex.simulate_trailing_exit(
        bars, 20, bars[20].close, "LONG", "sar",
        period=10, mult=3.0, sar_step=0.02, sar_max=0.2,
        tf_min=15, fee_pct=0.07, funding_bps_per_8h=1.0)
    assert tr.reason == "open"
    assert tr.gross_pct is not None and tr.gross_pct > 0


def test_trailing_exit_long_stops_out_on_sharp_reversal():
    up = [(100 + i, 100 + i + 0.5, 100 + i - 0.2, 100 + i + 0.4) for i in range(25)]
    # Hard drop after bar 25 forces any trailing long to stop out.
    down = [(120 - i * 3, 120 - i * 3 + 0.2, 110 - i * 3, 111 - i * 3)
            for i in range(8)]
    bars = ex.resample(_rows_from_ohlc(up + down), 15)
    tr = ex.simulate_trailing_exit(
        bars, 20, bars[20].close, "LONG", "atr",
        period=10, mult=3.0, sar_step=0.02, sar_max=0.2,
        tf_min=15, fee_pct=0.07, funding_bps_per_8h=1.0)
    assert tr.exited is True
    assert tr.reason == "trail"
    assert tr.fee_pct == pytest.approx(0.07)         # round-trip fee counted


# --------------------------------------------------------------------------- #
# taxonomy guard — order-flow setups stay excluded
# --------------------------------------------------------------------------- #
def test_order_flow_setups_are_excluded():
    assert "LIQUIDITY_SWEEP_REVERSAL" in ex.ORDER_FLOW_SETUPS
    assert "WHALE_MOMENTUM" in ex.ORDER_FLOW_SETUPS
    # price-action families must NOT be excluded
    assert "SR_FLIP_RETEST" not in ex.ORDER_FLOW_SETUPS
    assert "FVG_RETEST" not in ex.ORDER_FLOW_SETUPS
