"""Tests for the shadow-only strategy units (src/shadow_strategies.py)."""
from __future__ import annotations

import math

from src import shadow_strategies as ss
from src.strategy_portfolio import (
    SHADOW_CASCADE_REVERSAL,
    SHADOW_FUNDING_FADE,
    SHADOW_MEAN_REVERT,
    SHADOW_RANGE_FADE,
)


def _flat(n: int = 100, price: float = 100.0, noise: float = 0.1):
    closes = [price + noise * ((-1) ** i) for i in range(n)]
    highs = [c + noise for c in closes]
    lows = [c - noise for c in closes]
    return highs, lows, closes


def _range_market(n: int = 100, mid: float = 105.0, amp: float = 5.0, period: int = 24):
    """Slow sine oscillation — a real, repeatedly-tested range."""
    closes = [mid + amp * math.sin(2 * math.pi * i / period) for i in range(n)]
    highs = [c + 0.2 for c in closes]
    lows = [c - 0.2 for c in closes]
    return highs, lows, closes


class TestRangeFade:
    def test_fires_short_at_range_high(self):
        highs, lows, closes = _range_market()
        # Park the last close at the top of the range.
        top = max(highs[:-1])
        closes[-1] = top - 0.05
        highs[-1] = closes[-1] + 0.1
        lows[-1] = closes[-1] - 0.1
        cand = ss.evaluate_range_fade(highs, lows, closes)
        assert cand is not None and cand.strategy == SHADOW_RANGE_FADE
        assert cand.side == "SHORT"
        assert cand.stop_loss > cand.entry > cand.tp1  # stop beyond the high, TP at mid

    def test_abstains_mid_range(self):
        highs, lows, closes = _range_market()
        closes[-1] = 105.0  # mid
        assert ss.evaluate_range_fade(highs, lows, closes) is None

    def test_abstains_when_range_is_noise_width(self):
        highs, lows, closes = _flat()  # width ≈ ATR — not a tradeable range
        assert ss.evaluate_range_fade(highs, lows, closes) is None


class TestMeanRevert:
    def test_fires_short_on_upside_extension(self):
        highs, lows, closes = _flat()
        closes[-1] = 103.0
        highs[-1], lows[-1] = 103.2, 102.8
        cand = ss.evaluate_mean_revert(highs, lows, closes)
        assert cand is not None and cand.strategy == SHADOW_MEAN_REVERT
        assert cand.side == "SHORT"
        assert cand.tp1 < cand.entry < cand.stop_loss

    def test_abstains_at_the_mean(self):
        highs, lows, closes = _flat()
        assert ss.evaluate_mean_revert(highs, lows, closes) is None


class TestFundingFade:
    def test_fades_crowded_longs(self):
        highs, lows, closes = _flat()
        cand = ss.evaluate_funding_fade(highs, lows, closes, funding_rate=0.002)
        assert cand is not None and cand.strategy == SHADOW_FUNDING_FADE
        assert cand.side == "SHORT"

    def test_fades_crowded_shorts(self):
        highs, lows, closes = _flat()
        cand = ss.evaluate_funding_fade(highs, lows, closes, funding_rate=-0.002)
        assert cand is not None and cand.side == "LONG"

    def test_abstains_on_normal_funding_or_missing(self):
        highs, lows, closes = _flat()
        assert ss.evaluate_funding_fade(highs, lows, closes, funding_rate=0.0004) is None
        assert ss.evaluate_funding_fade(highs, lows, closes, funding_rate=None) is None


class TestCascadeReversal:
    def test_fires_long_on_reclaimed_down_wick(self):
        highs, lows, closes = _flat()
        # Bar -2: cascade — breaks the prior low hard, closes reclaiming >50%.
        highs[-2], lows[-2], closes[-2] = 100.3, 92.0, 97.0
        closes[-1] = 97.2
        highs[-1], lows[-1] = 97.4, 97.0
        cand = ss.evaluate_cascade_reversal(highs, lows, closes)
        assert cand is not None and cand.strategy == SHADOW_CASCADE_REVERSAL
        assert cand.side == "LONG"
        assert cand.stop_loss < 92.0  # beyond the wick extreme, not inside it

    def test_abstains_without_recovery(self):
        highs, lows, closes = _flat()
        highs[-2], lows[-2], closes[-2] = 100.3, 92.0, 92.5  # no reclaim
        assert ss.evaluate_cascade_reversal(highs, lows, closes) is None

    def test_abstains_on_normal_bars(self):
        highs, lows, closes = _flat()
        assert ss.evaluate_cascade_reversal(highs, lows, closes) is None


class TestEvaluateAll:
    def test_returns_only_valid_geometry(self):
        highs, lows, closes = _flat()
        for cand in ss.evaluate_all(highs, lows, closes, funding_rate=0.002):
            assert cand.entry > 0 and cand.stop_loss > 0 and cand.tp1 > 0
            assert cand.side in ("LONG", "SHORT")
            assert cand.valid_for_minutes > 0

    def test_fail_neutral_on_garbage(self):
        assert ss.evaluate_all([], [], []) == []
        assert ss.evaluate_all([1], [1], [1], funding_rate="bad") == []

    def test_no_emit_capable_objects(self):
        """Shadow candidates must never look like dispatchable Signals."""
        highs, lows, closes = _flat()
        for cand in ss.evaluate_all(highs, lows, closes, funding_rate=0.002):
            assert not hasattr(cand, "signal_id")
            assert not hasattr(cand, "channel")
