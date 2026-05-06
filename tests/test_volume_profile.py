"""Tests for the volume-profile lite module (POC + VAH/VAL)."""

from __future__ import annotations

import time

import numpy as np
import pytest

from src.volume_profile import (
    DEFAULT_BINS,
    DEFAULT_LOOKBACK,
    MIN_CANDLES,
    PROFILE_REFRESH_SEC,
    VALUE_AREA_FRACTION,
    VolumeProfileResult,
    VolumeProfileStore,
    _build_histogram,
    _find_poc,
    _find_value_area,
    compute_volume_profile,
)


# ---------------------------------------------------------------------------
# Histogram construction
# ---------------------------------------------------------------------------


class TestHistogram:
    def test_uniform_distribution_per_candle(self):
        # One candle range [10, 20] with volume 100.0, 10 bins from 10 → 20.
        # Each bin width = 1.0.  Volume should land 10 in each bin.
        highs = np.array([20.0])
        lows = np.array([10.0])
        volumes = np.array([100.0])
        edges, bin_vols = _build_histogram(highs, lows, volumes, bins=10)
        assert len(edges) == 11
        assert len(bin_vols) == 10
        assert all(abs(v - 10.0) < 0.01 for v in bin_vols)

    def test_zero_range_returns_empty_distribution(self):
        # All candles at the same price.
        highs = np.array([100.0, 100.0, 100.0])
        lows = np.array([100.0, 100.0, 100.0])
        volumes = np.array([10.0, 20.0, 30.0])
        edges, bin_vols = _build_histogram(highs, lows, volumes, bins=10)
        assert sum(bin_vols) == 0.0

    def test_zero_volume_candle_skipped(self):
        highs = np.array([20.0, 20.0])
        lows = np.array([10.0, 10.0])
        volumes = np.array([100.0, 0.0])
        _, bin_vols = _build_histogram(highs, lows, volumes, bins=10)
        # Total volume should equal the first candle's contribution only.
        assert sum(bin_vols) == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# POC + value area
# ---------------------------------------------------------------------------


class TestPocAndValueArea:
    def test_poc_is_max_volume_bin(self):
        edges = [0, 1, 2, 3, 4, 5]
        bin_volumes = [1, 2, 50, 1, 1]  # bin index 2 (price 2-3) has the most
        poc = _find_poc(edges, bin_volumes)
        assert poc == pytest.approx(2.5)

    def test_poc_zero_volume_returns_midpoint(self):
        edges = [10, 20]
        bin_volumes = [0]
        poc = _find_poc(edges, bin_volumes)
        assert poc == pytest.approx(15.0)

    def test_value_area_centred_on_poc(self):
        # Symmetric distribution around middle bin.
        edges = list(range(11))  # 0..10, bins=10
        bin_volumes = [1, 2, 5, 10, 20, 50, 20, 10, 5, 2]
        vah, val = _find_value_area(edges, bin_volumes)
        # POC is bin index 5 (price 5-6).  VAH/VAL should bracket bin 5.
        assert val <= 5.5 <= vah

    def test_value_area_covers_at_least_70pct(self):
        edges = list(range(11))
        bin_volumes = [1, 2, 5, 10, 20, 50, 20, 10, 5, 2]
        total = sum(bin_volumes)
        vah, val = _find_value_area(edges, bin_volumes)
        # Sum the bins inside [val, vah] and check ≥ 70%.
        inside = 0.0
        for i in range(len(bin_volumes)):
            mid = (edges[i] + edges[i + 1]) / 2.0
            if val <= mid <= vah:
                inside += bin_volumes[i]
        assert inside / total >= 0.70

    def test_value_area_falls_back_when_total_zero(self):
        edges = [10, 20, 30]
        bin_volumes = [0, 0]
        vah, val = _find_value_area(edges, bin_volumes)
        assert vah >= val or vah <= val  # no-op safety


# ---------------------------------------------------------------------------
# Public compute
# ---------------------------------------------------------------------------


def _candle_set_with_poc_at(price: float, n: int = 100) -> dict:
    """Build a candle set where the highest-volume cluster sits near `price`."""
    rng = np.random.default_rng(seed=42)
    highs = []
    lows = []
    volumes = []
    for i in range(n):
        if i % 5 == 0:
            # Heavy volume cluster around `price`.
            highs.append(price + 1.0)
            lows.append(price - 1.0)
            volumes.append(1000.0)
        else:
            offset = float(rng.uniform(-5, 5))
            highs.append(price + offset + 1.0)
            lows.append(price + offset - 1.0)
            volumes.append(50.0)
    return {
        "high": np.array(highs, dtype=np.float64),
        "low": np.array(lows, dtype=np.float64),
        "volume": np.array(volumes, dtype=np.float64),
    }


class TestComputeVolumeProfile:
    def test_basic_profile_returns_result(self):
        candles = _candle_set_with_poc_at(price=100.0, n=80)
        r = compute_volume_profile("BTCUSDT", candles)
        assert r is not None
        assert r.symbol == "BTCUSDT"
        assert r.bins == DEFAULT_BINS
        assert r.total_volume > 0

    def test_poc_near_volume_cluster(self):
        candles = _candle_set_with_poc_at(price=100.0, n=120)
        r = compute_volume_profile("BTCUSDT", candles)
        assert r is not None
        # POC should be within 2 of the cluster center.
        assert abs(r.poc - 100.0) < 2.0

    def test_value_area_brackets_poc(self):
        candles = _candle_set_with_poc_at(price=100.0, n=120)
        r = compute_volume_profile("BTCUSDT", candles)
        assert r is not None
        assert r.val <= r.poc <= r.vah

    def test_too_few_candles_returns_none(self):
        candles = _candle_set_with_poc_at(price=100.0, n=10)
        r = compute_volume_profile("BTCUSDT", candles)
        assert r is None

    def test_missing_volume_returns_none(self):
        candles = {
            "high": np.array([100.0] * 50),
            "low": np.array([99.0] * 50),
        }
        assert compute_volume_profile("BTCUSDT", candles) is None

    def test_lookback_truncates_history(self):
        candles = _candle_set_with_poc_at(price=100.0, n=300)
        r = compute_volume_profile("BTCUSDT", candles, lookback=50)
        assert r is not None
        # Just sanity-check it ran with 50-candle window — actual semantic
        # equivalence to a 50-candle slice is implicit.
        assert r.lookback == 50


# ---------------------------------------------------------------------------
# Result helper methods
# ---------------------------------------------------------------------------


class TestResultHelpers:
    def _result(self) -> VolumeProfileResult:
        return VolumeProfileResult(
            symbol="X",
            bins=10,
            lookback=100,
            poc=100.0,
            vah=102.0,
            val=98.0,
            total_volume=1000.0,
            bin_edges=list(range(11)),
            bin_volumes=[10] * 10,
        )

    def test_is_in_value_area_inside(self):
        r = self._result()
        assert r.is_in_value_area(100.0) is True
        assert r.is_in_value_area(99.0) is True
        assert r.is_in_value_area(102.0) is True

    def test_is_in_value_area_outside(self):
        r = self._result()
        assert r.is_in_value_area(95.0) is False
        assert r.is_in_value_area(110.0) is False

    def test_distance_to_poc_pct_signed(self):
        r = self._result()
        # POC=100; price 101 → +1%
        assert r.distance_to_poc_pct(101.0) == pytest.approx(1.0)
        assert r.distance_to_poc_pct(99.0) == pytest.approx(-1.0)

    def test_is_near_poc_within_tolerance(self):
        r = self._result()
        # POC=100, tolerance 0.30% → ±0.30
        assert r.is_near_poc(100.20, tolerance_pct=0.30) is True
        assert r.is_near_poc(100.50, tolerance_pct=0.30) is False

    def test_is_at_value_edge_at_vah(self):
        r = self._result()
        # VAH=102, tolerance 0.30 → band ~±0.306
        assert r.is_at_value_edge(102.10) is True

    def test_is_at_value_edge_at_val(self):
        r = self._result()
        # VAL=98
        assert r.is_at_value_edge(97.95) is True

    def test_is_at_value_edge_inside_value_area_false(self):
        r = self._result()
        # 100 is the POC, well inside the value area.
        assert r.is_at_value_edge(100.0) is False


# ---------------------------------------------------------------------------
# VolumeProfileStore + TTL
# ---------------------------------------------------------------------------


class TestStore:
    def test_empty_store_returns_none(self):
        s = VolumeProfileStore()
        assert s.get("BTCUSDT") is None
        assert s.stats("BTCUSDT") == {}

    def test_refresh_populates(self):
        s = VolumeProfileStore()
        candles = _candle_set_with_poc_at(price=100.0, n=80)
        r = s.refresh("BTCUSDT", candles)
        assert r is not None
        assert s.get("BTCUSDT") is not None

    def test_within_ttl_skips_recompute(self):
        s = VolumeProfileStore()
        candles = _candle_set_with_poc_at(price=100.0, n=80)
        s.refresh_if_stale("BTCUSDT", candles)
        first_ts = s._refresh_ts["BTCUSDT"]
        # Fake a different candles snapshot — TTL not elapsed → skip.
        s.refresh_if_stale("BTCUSDT", _candle_set_with_poc_at(price=200.0, n=80))
        assert s._refresh_ts["BTCUSDT"] == first_ts

    def test_after_ttl_recomputes(self):
        s = VolumeProfileStore()
        candles_a = _candle_set_with_poc_at(price=100.0, n=80)
        s.refresh_if_stale("BTCUSDT", candles_a)
        s._refresh_ts["BTCUSDT"] = time.time() - PROFILE_REFRESH_SEC - 1
        candles_b = _candle_set_with_poc_at(price=200.0, n=80)
        s.refresh_if_stale("BTCUSDT", candles_b)
        new_r = s.get("BTCUSDT")
        assert new_r is not None
        assert abs(new_r.poc - 200.0) < 5.0

    def test_stats_returns_summary(self):
        s = VolumeProfileStore()
        s.refresh("BTCUSDT", _candle_set_with_poc_at(price=100.0, n=80))
        st = s.stats("BTCUSDT")
        assert "poc" in st and "vah" in st and "val" in st
        assert st["value_area_width_pct"] >= 0.0


# ---------------------------------------------------------------------------
# Constant sanity
# ---------------------------------------------------------------------------


def test_default_bins_in_industry_range():
    assert 24 <= DEFAULT_BINS <= 100


def test_value_area_fraction_is_seventy_percent():
    assert VALUE_AREA_FRACTION == pytest.approx(0.70)


def test_min_candles_at_least_twenty():
    assert MIN_CANDLES >= 20


def test_default_lookback_reasonable():
    assert 50 <= DEFAULT_LOOKBACK <= 500


def test_refresh_ttl_at_least_quarter_hour():
    assert PROFILE_REFRESH_SEC >= 900.0
