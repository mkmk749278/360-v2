"""Tests for the Level Book — multi-TF S/R level discovery, scoring, and lookup."""

from __future__ import annotations

import time

import numpy as np
import pytest

from src.level_book import (
    AGE_DECAY_BUCKETS,
    AGE_DECAY_FLOOR,
    CONFLUENCE_TOLERANCE_PCT,
    Level,
    LevelBook,
    MAX_LEVELS_PER_SYMBOL,
    ROUND_NUMBER_BONUS,
    _age_decay,
    _cluster_levels,
    _count_touches,
    _round_number_levels,
    _score_level,
)


# ---------------------------------------------------------------------------
# Round-number generation
# ---------------------------------------------------------------------------


class TestRoundNumberLevels:
    def test_btc_scale(self):
        levels = _round_number_levels(78000.0)
        assert all(price > 0 for price in levels)
        # 78000 is itself a round number at step 1000.
        assert any(abs(price - 78000.0) < 0.01 for price in levels)
        # Default range_pct=20% → band 62400–93600 at step 1000.
        assert 62000 <= min(levels) <= 65000
        assert 90000 <= max(levels) <= 95000

    def test_eth_scale(self):
        levels = _round_number_levels(2500.0)
        # Step at 2500 should be 100.  Levels every 100.
        sorted_levels = sorted(levels)
        diffs = [sorted_levels[i + 1] - sorted_levels[i] for i in range(len(sorted_levels) - 1)]
        # All adjacent diffs should be ~100.
        assert all(abs(d - 100.0) < 0.01 for d in diffs)

    def test_low_priced_token(self):
        levels = _round_number_levels(0.0023)
        # Step ≈ 0.0001.  Should still produce a positive level set.
        assert len(levels) > 0
        assert all(price > 0 for price in levels)

    def test_zero_or_negative_returns_empty(self):
        assert _round_number_levels(0.0) == []
        assert _round_number_levels(-1.0) == []

    def test_range_pct_respected(self):
        levels = _round_number_levels(1000.0, range_pct=10.0)
        # Should be in [900, 1100] approximately.
        assert all(900 <= p <= 1100 for p in levels)


# ---------------------------------------------------------------------------
# Touch counting
# ---------------------------------------------------------------------------


class TestCountTouches:
    def test_no_touches(self):
        # Candles all far below the level.
        highs = np.array([100.0, 101.0, 102.0])
        lows = np.array([99.0, 100.0, 101.0])
        touches, last_idx = _count_touches(110.0, highs, lows)
        assert touches == 0
        assert last_idx is None

    def test_within_tolerance_counts_touch(self):
        # Level at 100.  Tolerance 0.15% → band 99.85–100.15.
        # Candle 0: high 100.10, low 99.90 → wicks into band ✓
        # Candle 1: high 99.50, low 99.20 → entirely below band ✗
        # Candle 2: high 100.05, low 99.95 → wicks into band ✓
        highs = np.array([100.10, 99.50, 100.05])
        lows = np.array([99.90, 99.20, 99.95])
        touches, last_idx = _count_touches(100.0, highs, lows, tolerance_pct=0.15)
        assert touches == 2
        assert last_idx == 2

    def test_just_outside_tolerance_excluded(self):
        # Level 100.  Tolerance 0.15 → band is 99.85–100.15.
        # Candle entirely above 100.15 (high=100.50, low=100.20).
        highs = np.array([100.50])
        lows = np.array([100.20])
        touches, _ = _count_touches(100.0, highs, lows, tolerance_pct=0.15)
        assert touches == 0


# ---------------------------------------------------------------------------
# Age decay
# ---------------------------------------------------------------------------


class TestAgeDecay:
    def test_recent_full_weight(self):
        now = time.time()
        assert _age_decay(now - 3600, now_ts=now) == pytest.approx(1.0)

    def test_one_day_full_weight(self):
        now = time.time()
        assert _age_decay(now - 23 * 3600, now_ts=now) == pytest.approx(1.0)

    def test_three_days_half_weight(self):
        now = time.time()
        assert _age_decay(now - 3 * 86400, now_ts=now) == pytest.approx(0.5)

    def test_two_weeks_quarter_weight(self):
        now = time.time()
        assert _age_decay(now - 14 * 86400, now_ts=now) == pytest.approx(0.25)

    def test_very_old_floor(self):
        now = time.time()
        assert _age_decay(now - 365 * 86400, now_ts=now) == AGE_DECAY_FLOOR

    def test_no_test_ts_returns_floor(self):
        assert _age_decay(None) == AGE_DECAY_FLOOR


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


class TestScoreLevel:
    def test_4h_pivot_with_three_recent_touches(self):
        now = time.time()
        lv = Level(
            price=100.0, type="support", source_tf="4h",
            touches=3, last_test_ts=now - 3600,
        )
        # base 10 + 3*5 = 25.  TF 1.5.  Age 1.0.  → 37.5
        assert _score_level(lv, now_ts=now) == pytest.approx(37.5)

    def test_round_number_bonus_applied(self):
        now = time.time()
        lv = Level(
            price=100.0, type="support", source_tf="round",
            touches=1, last_test_ts=now - 3600, is_round_number=True,
        )
        # base 10 + 1*5 = 15.  TF 1.5 (round weight).  Age 1.0.  → 22.5  + 5 bonus = 27.5
        assert _score_level(lv, now_ts=now) == pytest.approx(22.5 + ROUND_NUMBER_BONUS)

    def test_touches_capped(self):
        """20 touches doesn't keep adding score linearly — capped at TOUCH_SCORE_CAP."""
        now = time.time()
        lv6 = Level(
            price=100.0, type="support", source_tf="1h",
            touches=6, last_test_ts=now - 3600,
        )
        lv20 = Level(
            price=100.0, type="support", source_tf="1h",
            touches=20, last_test_ts=now - 3600,
        )
        assert _score_level(lv6, now_ts=now) == _score_level(lv20, now_ts=now)

    def test_higher_tf_outscores_lower_tf(self):
        now = time.time()
        lv_1d = Level(price=100.0, type="support", source_tf="1d", touches=2, last_test_ts=now)
        lv_1h = Level(price=100.0, type="support", source_tf="1h", touches=2, last_test_ts=now)
        assert _score_level(lv_1d, now_ts=now) > _score_level(lv_1h, now_ts=now)

    def test_old_level_outscored_by_recent(self):
        now = time.time()
        lv_recent = Level(price=100.0, type="support", source_tf="4h", touches=3, last_test_ts=now)
        lv_old = Level(price=100.0, type="support", source_tf="4h", touches=3, last_test_ts=now - 14 * 86400)
        assert _score_level(lv_recent, now_ts=now) > _score_level(lv_old, now_ts=now)


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------


class TestClusterLevels:
    def test_levels_within_tolerance_merge(self):
        levels = [
            Level(price=100.0, type="support", source_tf="1h", touches=2),
            Level(price=100.20, type="support", source_tf="4h", touches=1),  # 0.2% above
        ]
        out = _cluster_levels(levels, tolerance_pct=0.30)
        assert len(out) == 1
        merged = out[0]
        assert merged.touches == 3
        # Touch-weighted: (100*2 + 100.2*1) / 3 ≈ 100.067
        assert merged.price == pytest.approx(100.067, abs=0.01)
        assert "1h" in merged.source_tfs
        assert "4h" in merged.source_tfs

    def test_levels_outside_tolerance_stay_separate(self):
        levels = [
            Level(price=100.0, type="support", source_tf="1h", touches=2),
            Level(price=105.0, type="support", source_tf="4h", touches=1),  # 5% away
        ]
        out = _cluster_levels(levels, tolerance_pct=0.30)
        assert len(out) == 2

    def test_round_number_propagates_into_cluster(self):
        levels = [
            Level(price=100.0, type="support", source_tf="1h", touches=1, is_round_number=True),
            Level(price=100.05, type="support", source_tf="4h", touches=2),
        ]
        out = _cluster_levels(levels, tolerance_pct=0.30)
        assert len(out) == 1
        assert out[0].is_round_number is True


# ---------------------------------------------------------------------------
# LevelBook integration
# ---------------------------------------------------------------------------


def _candle_set(prices_high, prices_low, *, base_ts: float = 1700000000.0, step: float = 3600.0) -> dict:
    n = len(prices_high)
    return {
        "high": np.array(prices_high, dtype=np.float64),
        "low": np.array(prices_low, dtype=np.float64),
        "close": np.array([(h + l) / 2 for h, l in zip(prices_high, prices_low)], dtype=np.float64),
        "timestamp": np.array([base_ts + step * i for i in range(n)], dtype=np.float64),
    }


def _make_swinging_candles(n: int = 50, swing_high: float = 105.0, swing_low: float = 95.0) -> dict:
    """Generate candles with regular swing highs/lows so detector finds pivots."""
    highs = []
    lows = []
    for i in range(n):
        if i % 10 == 5:
            highs.append(swing_high)
            lows.append(swing_high - 1.0)
        elif i % 10 == 0:
            highs.append(swing_low + 1.0)
            lows.append(swing_low)
        else:
            highs.append(100.0 + (i % 3))
            lows.append(99.0 + (i % 3))
    return _candle_set(highs, lows)


class TestLevelBook:
    def test_empty_book_returns_no_levels(self):
        book = LevelBook()
        assert book.get_levels("BTCUSDT") == []
        assert book.last_refresh_ts("BTCUSDT") is None

    def test_refresh_populates_levels(self):
        book = LevelBook()
        candles = {"1h": _make_swinging_candles(n=60)}
        out = book.refresh("BTCUSDT", candles)
        assert len(out) > 0
        assert book.last_refresh_ts("BTCUSDT") is not None

    def test_refresh_includes_round_numbers(self):
        book = LevelBook()
        # Price scale with obvious round numbers (100, 110, 120…)
        highs = np.linspace(95, 105, 50).tolist()
        lows = (np.array(highs) - 1.0).tolist()
        candles = {"1h": _candle_set(highs, lows)}
        book.refresh("BTCUSDT", candles)
        levels = book.get_levels("BTCUSDT")
        assert any(lv.is_round_number for lv in levels), \
            "At least one round-number level should be discovered."

    def test_levels_sorted_by_score(self):
        book = LevelBook()
        candles = {"1h": _make_swinging_candles(n=80)}
        book.refresh("BTCUSDT", candles)
        levels = book.get_levels("BTCUSDT")
        scores = [lv.score for lv in levels]
        assert scores == sorted(scores, reverse=True), \
            "get_levels output should be score-descending."

    def test_capped_at_max_levels(self):
        book = LevelBook()
        # Many synthetic highs to overflow the cap.
        highs = list(np.linspace(50, 200, 300))
        lows = [h - 1.0 for h in highs]
        candles = {"1h": _candle_set(highs, lows)}
        book.refresh("BTCUSDT", candles)
        assert len(book.get_levels("BTCUSDT")) <= MAX_LEVELS_PER_SYMBOL

    def test_nearest_level_returns_within_band(self):
        book = LevelBook()
        candles = {"1h": _make_swinging_candles(n=60, swing_high=105.0, swing_low=95.0)}
        book.refresh("BTCUSDT", candles)
        # Looking just above the swing high.
        lv = book.nearest_level("BTCUSDT", 104.95, max_distance_pct=0.5)
        assert lv is not None
        assert abs(lv.price - 105.0) <= 105.0 * 0.005

    def test_nearest_level_outside_band_returns_none(self):
        book = LevelBook()
        candles = {"1h": _make_swinging_candles(n=60)}
        book.refresh("BTCUSDT", candles)
        # 50% away from any reasonable level.
        assert book.nearest_level("BTCUSDT", 200.0, max_distance_pct=0.1) is None

    def test_nearest_level_type_filter(self):
        book = LevelBook()
        candles = {"1h": _make_swinging_candles(n=60)}
        book.refresh("BTCUSDT", candles)
        sup = book.nearest_level("BTCUSDT", 95.0, type_filter="support", max_distance_pct=2.0)
        if sup is not None:
            assert sup.type == "support"

    def test_confluence_count_zero_for_unknown_symbol(self):
        book = LevelBook()
        assert book.confluence_count("NEWPAIR", 100.0) == 0

    def test_confluence_count_aggregates(self):
        book = LevelBook()
        candles = {"1h": _make_swinging_candles(n=60)}
        book.refresh("BTCUSDT", candles)
        # Within the band should hit at least the swing-high cluster + nearby
        # round-number cluster.  Asserts non-zero rather than exact count
        # since clustering is data-dependent.
        assert book.confluence_count("BTCUSDT", 105.0, tolerance_pct=2.0) >= 1

    def test_stats_reports_counts(self):
        book = LevelBook()
        candles = {"1h": _make_swinging_candles(n=60)}
        book.refresh("BTCUSDT", candles)
        s = book.stats("BTCUSDT")
        assert s["total"] == len(book.get_levels("BTCUSDT"))
        assert s["support"] + s["resistance"] == s["total"]
        assert s["from_1h"] >= 0

    def test_refresh_replaces_previous(self):
        book = LevelBook()
        candles_a = {"1h": _make_swinging_candles(n=60, swing_high=105.0, swing_low=95.0)}
        candles_b = {"1h": _make_swinging_candles(n=60, swing_high=205.0, swing_low=195.0)}
        book.refresh("BTCUSDT", candles_a)
        levels_a = book.get_levels("BTCUSDT")
        book.refresh("BTCUSDT", candles_b)
        levels_b = book.get_levels("BTCUSDT")
        # Different price scales → different level sets.
        a_prices = {round(lv.price, 1) for lv in levels_a}
        b_prices = {round(lv.price, 1) for lv in levels_b}
        assert a_prices != b_prices

    def test_skip_tf_with_too_few_candles(self):
        book = LevelBook()
        candles = {"1h": _candle_set([100.0] * 5, [99.0] * 5)}  # only 5 bars
        out = book.refresh("BTCUSDT", candles)
        # Round numbers may still seed levels even with no swings.
        # We just verify no crash.
        assert isinstance(out, list)

    def test_multi_tf_cluster_keeps_higher_tf_provenance(self):
        """A 1d swing and a 1h swing at nearly the same price should cluster
        and preserve both source TFs."""
        book = LevelBook()
        # Same swing pattern at both TFs but with 1h having more candles.
        candles = {
            "1h": _make_swinging_candles(n=60, swing_high=105.0, swing_low=95.0),
            "4h": _make_swinging_candles(n=60, swing_high=105.0, swing_low=95.0),
        }
        book.refresh("BTCUSDT", candles)
        levels = book.get_levels("BTCUSDT")
        # At least one level should have both TFs in its provenance.
        assert any("1h" in lv.source_tfs and "4h" in lv.source_tfs for lv in levels)


# ---------------------------------------------------------------------------
# Confluence-tolerance default sanity (downstream callers depend on it)
# ---------------------------------------------------------------------------


def test_confluence_tolerance_default_is_reasonable():
    # Anything > 1% would be too loose; < 0.1% too tight for crypto noise.
    assert 0.1 <= CONFLUENCE_TOLERANCE_PCT <= 1.0
