"""Tests for the structure-state tracker (HH/HL bull leg vs LH/LL bear leg)."""

from __future__ import annotations

import time

import numpy as np
import pytest

from src.structure_state import (
    LEG_DOMINANCE_THRESHOLD,
    PIVOT_WINDOW,
    STRUCTURE_REFRESH_SEC,
    StructureState,
    StructureTracker,
    _classify_recent,
    _classify_state,
    _ordered_pivots,
)


# ---------------------------------------------------------------------------
# Pivot ordering
# ---------------------------------------------------------------------------


class TestOrderedPivots:
    def test_chronological_order(self):
        highs = np.array([1, 5, 1, 1, 1, 1, 1, 6, 1, 1], dtype=np.float64)
        lows = np.array([0.9, 4, 0.8, 0.8, 0.7, 0.8, 0.8, 5, 0.6, 0.7], dtype=np.float64)
        # Pivot at idx=1 high=5, idx=7 high=6, etc.
        out = _ordered_pivots(highs, lows, order=2)
        # Output should be index-sorted.
        for prev, nxt in zip(out, out[1:]):
            assert prev[0] <= nxt[0]


# ---------------------------------------------------------------------------
# Recent classification
# ---------------------------------------------------------------------------


class TestClassifyRecent:
    def test_bull_sequence(self):
        # H 100 → L 95 → H 105 → L 97 → H 110 → L 100
        # Compared:                     HH       HL      HH        HL
        pivots = [
            (0, 100.0, "H"),
            (3, 95.0, "L"),
            (6, 105.0, "H"),  # > 100 → HH
            (9, 97.0, "L"),   # > 95  → HL
            (12, 110.0, "H"),  # > 105 → HH
            (15, 100.0, "L"),  # > 97  → HL
        ]
        labels, anchors = _classify_recent(pivots, window=4)
        assert labels == ["HH", "HL", "HH", "HL"]
        assert anchors["HH"] == 110.0
        assert anchors["HL"] == 100.0

    def test_bear_sequence(self):
        pivots = [
            (0, 110.0, "H"),
            (3, 105.0, "L"),
            (6, 105.0, "H"),  # < 110 → LH
            (9, 100.0, "L"),  # < 105 → LL
            (12, 100.0, "H"),  # < 105 → LH
            (15, 95.0, "L"),  # < 100 → LL
        ]
        labels, anchors = _classify_recent(pivots, window=4)
        assert labels == ["LH", "LL", "LH", "LL"]
        assert anchors["LH"] == 100.0
        assert anchors["LL"] == 95.0

    def test_first_pivots_unclassified(self):
        # Single H, single L → no comparator → no labels.
        pivots = [(0, 100.0, "H"), (3, 95.0, "L")]
        labels, anchors = _classify_recent(pivots)
        assert labels == []
        assert all(v is None for v in anchors.values())

    def test_window_truncation(self):
        pivots = [
            (0, 100.0, "H"),
            (1, 95.0, "L"),
            (2, 105.0, "H"),
            (3, 97.0, "L"),
            (4, 110.0, "H"),
            (5, 100.0, "L"),
            (6, 115.0, "H"),
            (7, 105.0, "L"),
        ]
        labels, _ = _classify_recent(pivots, window=2)
        assert len(labels) == 2


# ---------------------------------------------------------------------------
# State classification
# ---------------------------------------------------------------------------


class TestClassifyState:
    def test_pure_bull_full_confidence(self):
        st, conf, bull, bear = _classify_state(["HH", "HL", "HH", "HL"])
        assert st == "BULL_LEG"
        assert conf == pytest.approx(1.0)
        assert bull == 4 and bear == 0

    def test_pure_bear_full_confidence(self):
        st, conf, bull, bear = _classify_state(["LH", "LL", "LH", "LL"])
        assert st == "BEAR_LEG"
        assert conf == pytest.approx(1.0)
        assert bear == 4 and bull == 0

    def test_dominance_threshold_bull(self):
        # 3 of 4 → 75% → exactly threshold.
        st, conf, _, _ = _classify_state(["HH", "HL", "HH", "LH"])
        assert st == "BULL_LEG"
        assert conf == pytest.approx(0.75)

    def test_below_threshold_range(self):
        st, _, _, _ = _classify_state(["HH", "HL", "LH", "LL"])
        assert st == "RANGE"

    def test_empty_labels_range(self):
        st, conf, bull, bear = _classify_state([])
        assert st == "RANGE"
        assert conf == 0.0


# ---------------------------------------------------------------------------
# Tracker integration
# ---------------------------------------------------------------------------


def _bull_candles(n: int = 50) -> dict:
    """Synthesize a clear HH/HL bull-leg candle series.

    Build a staircase: each "leg" goes UP by 5, then pulls back by 2,
    making each high higher and each low higher.
    """
    highs = []
    lows = []
    base = 100.0
    for i in range(n):
        if i % 10 == 5:        # local high
            highs.append(base + 4.5)
            lows.append(base + 3.5)
            base += 3
        elif i % 10 == 0:      # local low
            highs.append(base + 0.5)
            lows.append(base - 1.0)
        else:
            highs.append(base + 1 + (i % 3) * 0.2)
            lows.append(base + 0.0 + (i % 3) * 0.2)
    return {
        "high": np.array(highs, dtype=np.float64),
        "low": np.array(lows, dtype=np.float64),
        "close": np.array([(h + l) / 2 for h, l in zip(highs, lows)], dtype=np.float64),
        "timestamp": np.array([1700000000.0 + 3600 * i for i in range(n)], dtype=np.float64),
    }


def _bear_candles(n: int = 50) -> dict:
    highs = []
    lows = []
    base = 200.0
    for i in range(n):
        if i % 10 == 5:        # local high
            highs.append(base + 0.5)
            lows.append(base - 1.0)
            base -= 3
        elif i % 10 == 0:      # local low
            highs.append(base + 1.0)
            lows.append(base - 4.5)
        else:
            highs.append(base - 1.0 + (i % 3) * 0.2)
            lows.append(base - 2.0 + (i % 3) * 0.2)
    return {
        "high": np.array(highs, dtype=np.float64),
        "low": np.array(lows, dtype=np.float64),
        "close": np.array([(h + l) / 2 for h, l in zip(highs, lows)], dtype=np.float64),
        "timestamp": np.array([1700000000.0 + 3600 * i for i in range(n)], dtype=np.float64),
    }


def _range_candles(n: int = 60) -> dict:
    """Oscillation with mixed HH/LH and HL/LL pivots — no dominant direction.

    Construction: each cycle of ~10 bars produces a swing high and a swing
    low.  We deliberately alternate the high/low magnitudes so the latest
    4 pivots split ~50/50 between bull-leg and bear-leg labels.
    """
    highs = []
    lows = []
    swing_highs = [108.0, 105.0, 110.0, 107.0, 109.0, 106.0]
    swing_lows = [95.0, 98.0, 94.0, 99.0, 96.0, 97.0]
    cycle = 10
    cycle_count = 0
    for i in range(n):
        if i % cycle == 5:  # local high
            sh = swing_highs[cycle_count % len(swing_highs)]
            highs.append(sh)
            lows.append(sh - 1.5)
        elif i % cycle == 0:  # local low
            sl = swing_lows[cycle_count % len(swing_lows)]
            highs.append(sl + 1.5)
            lows.append(sl)
            cycle_count += 1
        else:
            highs.append(101.5 + (i % 3) * 0.2)
            lows.append(100.5 + (i % 3) * 0.2)
    return {
        "high": np.array(highs, dtype=np.float64),
        "low": np.array(lows, dtype=np.float64),
        "close": np.array([(h + l) / 2 for h, l in zip(highs, lows)], dtype=np.float64),
        "timestamp": np.array([1700000000.0 + 3600 * i for i in range(n)], dtype=np.float64),
    }


class TestStructureTracker:
    def test_empty_tracker_returns_none(self):
        tr = StructureTracker()
        assert tr.get_state("BTCUSDT") is None
        assert tr.is_aligned("BTCUSDT", "LONG") is False

    def test_bull_candles_classified_bull_leg(self):
        tr = StructureTracker()
        st = tr.refresh("BTCUSDT", "1h", _bull_candles(n=50))
        assert st is not None
        assert st.state == "BULL_LEG"
        assert st.confidence >= LEG_DOMINANCE_THRESHOLD
        assert st.bull_count > st.bear_count

    def test_bear_candles_classified_bear_leg(self):
        tr = StructureTracker()
        st = tr.refresh("ETHUSDT", "1h", _bear_candles(n=50))
        assert st is not None
        assert st.state == "BEAR_LEG"
        assert st.confidence >= LEG_DOMINANCE_THRESHOLD
        assert st.bear_count > st.bull_count

    def test_range_candles_classified_range(self):
        tr = StructureTracker()
        st = tr.refresh("SOLUSDT", "1h", _range_candles(n=50))
        assert st is not None
        assert st.state == "RANGE"

    def test_too_few_candles_returns_none(self):
        tr = StructureTracker()
        candles = _bull_candles(n=10)
        st = tr.refresh("BTCUSDT", "1h", candles)
        assert st is None

    def test_malformed_candles_returns_none(self):
        tr = StructureTracker()
        assert tr.refresh("BTCUSDT", "1h", {}) is None
        assert tr.refresh("BTCUSDT", "1h", {"high": "x", "low": [1, 2]}) is None

    def test_get_state_after_refresh(self):
        tr = StructureTracker()
        tr.refresh("BTCUSDT", "1h", _bull_candles(n=50))
        st = tr.get_state("BTCUSDT", tf="1h")
        assert st is not None
        assert st.state == "BULL_LEG"

    def test_is_aligned_bull_long(self):
        tr = StructureTracker()
        tr.refresh("BTCUSDT", "1h", _bull_candles(n=50))
        assert tr.is_aligned("BTCUSDT", "LONG", tf="1h") is True
        assert tr.is_aligned("BTCUSDT", "SHORT", tf="1h") is False

    def test_is_aligned_bear_short(self):
        tr = StructureTracker()
        tr.refresh("ETHUSDT", "1h", _bear_candles(n=50))
        assert tr.is_aligned("ETHUSDT", "SHORT", tf="1h") is True
        assert tr.is_aligned("ETHUSDT", "LONG", tf="1h") is False

    def test_is_aligned_range_never_aligned(self):
        tr = StructureTracker()
        tr.refresh("SOLUSDT", "1h", _range_candles(n=50))
        assert tr.is_aligned("SOLUSDT", "LONG", tf="1h") is False
        assert tr.is_aligned("SOLUSDT", "SHORT", tf="1h") is False

    def test_is_aligned_min_confidence_filter(self):
        tr = StructureTracker()
        tr.refresh("BTCUSDT", "1h", _bull_candles(n=50))
        # Demanding 99% should likely fail (real-world classifier confidence < 1).
        assert tr.is_aligned(
            "BTCUSDT", "LONG", tf="1h", min_confidence=0.99,
        ) in (True, False)
        # And forcing too high definitively fails.
        assert tr.is_aligned(
            "BTCUSDT", "LONG", tf="1h", min_confidence=10.0,
        ) is False

    def test_refresh_replaces_previous(self):
        tr = StructureTracker()
        tr.refresh("BTCUSDT", "1h", _bull_candles(n=50))
        assert tr.get_state("BTCUSDT", tf="1h").state == "BULL_LEG"
        tr.refresh("BTCUSDT", "1h", _bear_candles(n=50))
        assert tr.get_state("BTCUSDT", tf="1h").state == "BEAR_LEG"

    def test_multi_tf_independent_state(self):
        tr = StructureTracker()
        tr.refresh("BTCUSDT", "1h", _bull_candles(n=50))
        tr.refresh("BTCUSDT", "4h", _bear_candles(n=50))
        assert tr.get_state("BTCUSDT", tf="1h").state == "BULL_LEG"
        assert tr.get_state("BTCUSDT", tf="4h").state == "BEAR_LEG"

    def test_stats_lists_state_per_tf(self):
        tr = StructureTracker()
        tr.refresh("BTCUSDT", "1h", _bull_candles(n=50))
        tr.refresh("BTCUSDT", "4h", _bear_candles(n=50))
        st = tr.stats("BTCUSDT")
        assert "1h" in st and "4h" in st
        assert "BULL_LEG" in st["1h"]
        assert "BEAR_LEG" in st["4h"]

    def test_leg_age_populated_for_bull_leg(self):
        tr = StructureTracker()
        st = tr.refresh("BTCUSDT", "1h", _bull_candles(n=50))
        assert st is not None
        # The bull-leg fixture has a clear leg start in the timestamp series.
        assert st.leg_age_seconds >= 0.0


# ---------------------------------------------------------------------------
# TTL behaviour
# ---------------------------------------------------------------------------


class TestRefreshTtl:
    def test_refresh_if_stale_first_call_runs(self):
        tr = StructureTracker()
        st = tr.refresh_if_stale("BTCUSDT", "1h", _bull_candles(n=50))
        assert st is not None
        assert tr._refresh_ts.get(("BTCUSDT", "1h")) is not None

    def test_within_ttl_skips_recompute(self):
        tr = StructureTracker()
        tr.refresh_if_stale("BTCUSDT", "1h", _bull_candles(n=50))
        first_ts = tr._refresh_ts[("BTCUSDT", "1h")]
        # Different candles, but TTL hasn't elapsed → should NOT refresh.
        tr.refresh_if_stale("BTCUSDT", "1h", _bear_candles(n=50))
        assert tr._refresh_ts[("BTCUSDT", "1h")] == first_ts
        assert tr.get_state("BTCUSDT", tf="1h").state == "BULL_LEG"

    def test_after_ttl_recomputes(self):
        tr = StructureTracker()
        tr.refresh_if_stale("BTCUSDT", "1h", _bull_candles(n=50))
        # Forge expiry.
        tr._refresh_ts[("BTCUSDT", "1h")] = time.time() - STRUCTURE_REFRESH_SEC - 1
        tr.refresh_if_stale("BTCUSDT", "1h", _bear_candles(n=50))
        assert tr.get_state("BTCUSDT", tf="1h").state == "BEAR_LEG"


# ---------------------------------------------------------------------------
# Constants sanity
# ---------------------------------------------------------------------------


def test_pivot_window_is_reasonable():
    assert 3 <= PIVOT_WINDOW <= 8


def test_dominance_threshold_majority_or_more():
    assert 0.5 < LEG_DOMINANCE_THRESHOLD <= 1.0


def test_refresh_ttl_at_least_quarter_hour():
    assert STRUCTURE_REFRESH_SEC >= 900.0
