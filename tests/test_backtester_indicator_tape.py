"""Indicator-tape regression tests — the fix for the ops bake-off timeout.

WHY (2026-07-25).  ``Backtester._backtest_channel`` used to call
``_compute_indicators(window[:i])`` on every candle, recomputing all eight
indicators over the whole prefix each time.  That made a run Theta(n^2) —
measured at 14.6 us * n^2, i.e. ~11 h for one symbol over 6 months of 5m bars
and ~219 h for the 20-pair universe — which is the real reason the ops
exit-method bake-off could only ever report "timeout after 1800s".

``_IndicatorTape`` computes each (causal) indicator once and reads it back by
index.  These tests lock the two properties that make that safe and lasting:

1. **Equivalence** — the tape returns bit-identical values to the per-prefix
   recomputation it replaced, including at every length gate.
2. **Complexity** — indicators are computed a bounded number of times per run
   (once per timeframe), not once per candle.  This is asserted structurally by
   counting indicator calls rather than by timing, so it cannot flake in CI, and
   it fails loudly if anyone reintroduces per-candle recomputation.
"""
from __future__ import annotations

import numpy as np
import pytest

import src.backtester as bt_mod
from src.backtester import Backtester, _compute_indicators, _IndicatorTape


def _series(n: int, seed: int = 9) -> dict:
    rng = np.random.default_rng(seed)
    close = np.abs(100.0 + np.cumsum(rng.normal(0, 0.12, n))) + 1.0
    return {
        "open": np.concatenate([[close[0]], close[:-1]]),
        "high": close * 1.0015,
        "low": close * 0.9985,
        "close": close,
        "volume": rng.uniform(1e3, 1e5, n),
    }


def _same(a, b) -> bool:
    """Old/new agreement, treating None and NaN as their own equals."""
    if a is None or b is None:
        return a is b
    if np.isnan(a) and np.isnan(b):
        return True
    return a == b


class TestIndicatorTapeEquivalence:
    """The tape must reproduce _compute_indicators exactly, gate for gate."""

    # Every length gate in _compute_indicators, plus both sides of each.
    GATES = [1, 3, 4, 5, 14, 15, 16, 19, 20, 21, 22, 29, 30, 31, 199, 200, 201]

    @pytest.mark.parametrize("i", GATES)
    def test_matches_at_every_length_gate(self, i):
        data = _series(400)
        tape = _IndicatorTape(data)
        old = _compute_indicators({k: v[:i] for k, v in data.items()})
        new = tape.at(i)
        assert set(old) == set(new), f"key set differs at prefix {i}"
        for k in old:
            assert _same(old[k], new[k]), f"{k} differs at prefix {i}"

    def test_matches_across_a_long_sweep(self):
        data = _series(4000)
        tape = _IndicatorTape(data)
        for i in range(1, 4000, 37):
            old = _compute_indicators({k: v[:i] for k, v in data.items()})
            new = tape.at(i)
            assert set(old) == set(new), f"key set differs at prefix {i}"
            for k in old:
                assert _same(old[k], new[k]), f"{k} differs at prefix {i}"

    def test_series_shorter_than_every_gate(self):
        data = _series(3)
        tape = _IndicatorTape(data)
        assert tape.at(3) == _compute_indicators({k: v[:3] for k, v in data.items()})

    def test_empty_series_is_safe(self):
        empty = {k: np.array([]) for k in ("open", "high", "low", "close", "volume")}
        assert _IndicatorTape(empty).at(0) == {}

    def test_prefix_longer_than_series_clamps(self):
        """A window can't exceed its series; asking beyond it reads the tail."""
        data = _series(300)
        tape = _IndicatorTape(data)
        assert tape.at(10_000) == tape.at(300)


class TestIndicatorTapeIsNotQuadratic:
    """Indicators are computed per *timeframe*, never per candle."""

    def _count_indicator_calls(self, monkeypatch, n: int) -> int:
        calls = {"n": 0}

        def wrap(fn):
            def inner(*a, **kw):
                calls["n"] += 1
                return fn(*a, **kw)
            return inner

        for name in ("ema", "adx", "atr", "rsi", "bollinger_bands", "momentum"):
            monkeypatch.setattr(bt_mod, name, wrap(getattr(bt_mod, name)))

        Backtester(lookahead_candles=20, fee_pct=0.07).run(
            _series(n), symbol="BTCUSDT", tag_regimes=True
        )
        return calls["n"]

    def test_indicator_calls_do_not_grow_with_candle_count(self, monkeypatch):
        """4x the candles must not mean ~4x (let alone n^2) the indicator work.

        Pre-fix this scaled with the number of candles evaluated; the tape makes
        it a small constant (a handful of calls per timeframe).
        """
        short = self._count_indicator_calls(monkeypatch, 600)
        long_ = self._count_indicator_calls(monkeypatch, 2400)
        assert short > 0, "indicators were never computed — test is not exercising the path"
        assert long_ == short, (
            f"indicator work grew with series length ({short} -> {long_} calls): "
            "the per-candle recomputation is back, and a full bake-off will time out"
        )

    def test_call_count_is_bounded_and_small(self, monkeypatch):
        """Sanity floor/ceiling: once per indicator per timeframe, not per bar."""
        n = 2400
        count = self._count_indicator_calls(monkeypatch, n)
        # ScalpChannel declares 2 timeframes; 8 indicator calls each (ema x3,
        # adx, atr, rsi, bollinger, momentum) = well under 50 either way.
        assert count < 50, f"expected a handful of indicator calls, got {count}"
        assert count < n / 10, "call count is scaling with candles"
