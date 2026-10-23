"""Every timeframe the Backtester hands an evaluator must be aligned in TIME.

WHY (2026-10-23). `_backtest_channel` sliced every timeframe in `candles_by_tf`
at the primary index `i`. With the shape a real store has (5m, 1h, 4h, 1d of
different lengths, each with `open_time`), index `i` of the 1h series is a
different date from index `i` of the 5m series, so a 5m evaluator read hourly
bars from weeks away. `/backtest` passes the live data store straight in.
Found while building the market-first Phase-1 replay, which had to align on
close time itself (`scripts/research/market_first_2026_10_23/replay.py`).
"""
from __future__ import annotations

import numpy as np

from src.backtester import Backtester, _tf_closed_counts

_MIN5 = 300_000
_HOUR = 3_600_000
_T0 = 1_780_000_000_000 - (1_780_000_000_000 % _HOUR)


def _series(n: int, period_ms: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    close = np.abs(100.0 + np.cumsum(rng.normal(0, 0.25, n))) + 1.0
    return {
        "open": np.concatenate([[close[0]], close[:-1]]),
        "high": close * 1.004,
        "low": close * 0.996,
        "close": close,
        "volume": rng.lognormal(10, 1.2, n),
        "open_time": _T0 + np.arange(n) * period_ms,
    }


class _Spy:
    """A channel that records what it was handed and never signals."""

    class config:  # noqa: N801 — mirrors ChannelConfig's attribute access
        name = "SPY"
        timeframes = ["5m", "1h"]

    def __init__(self) -> None:
        self.seen: list = []

    def evaluate(self, symbol, candles, indicators, smc_data, spread_pct, volume_24h_usd):
        m5, h1 = candles["5m"], candles.get("1h")
        self.seen.append((m5["open_time"][-1], None if h1 is None else h1["open_time"][-1]))
        return []


def _run(candles_by_tf: dict) -> _Spy:
    spy = _Spy()
    Backtester(channels=[spy], min_window=60, lookahead_candles=5).run(candles_by_tf, symbol="X")
    return spy


def test_hourly_window_has_closed_by_the_5m_bar_and_is_the_latest_that_has():
    m5 = _series(2000, _MIN5, 1)    # ~7 days of 5m
    h1 = _series(400, _HOUR, 2)     # ~17 days of 1h — different length, as in a real store
    spy = _run({"5m": m5, "1h": h1})
    assert spy.seen, "the spy channel was never called"
    for last_5m_open, last_1h_open in spy.seen:
        decision_time = last_5m_open + _MIN5  # the 5m bar just closed
        assert last_1h_open + _HOUR <= decision_time, "evaluator saw an hourly bar not yet closed"
        assert last_1h_open + 2 * _HOUR > decision_time, "evaluator saw a stale hourly bar"


def test_equal_length_series_without_timestamps_keep_identity_alignment():
    """The synthetic flat shape (one series for every timeframe) is unchanged."""
    s = {k: v for k, v in _series(300, _MIN5, 3).items() if k != "open_time"}
    counts = _tf_closed_counts({"5m": s, "1h": s}, "5m", 300)
    assert (counts["1h"] == np.arange(301)).all()


def test_unalignable_timeframe_is_refused_not_guessed():
    """Different length and no timestamps: no honest alignment exists."""
    a = {k: v for k, v in _series(300, _MIN5, 4).items() if k != "open_time"}
    b = {k: v for k, v in _series(120, _HOUR, 5).items() if k != "open_time"}
    assert "1h" not in _tf_closed_counts({"5m": a, "1h": b}, "5m", 300)
