"""Fail-open telemetry sweep regression (2026-07-15).

PR #727 hardened the data-store consumers against numpy truthiness but left
the evaluator/feature files with silent ``except`` handlers (DEBUG-only or
bare ``pass``) — the exact invisibility that hid the 8-dead-features
incident.  This suite pins that every converted site actually lands a
counter in ``fail_open.snapshot()`` when fed corrupt input, so the
feature-liveness burst pager can see it.

Behavior contract: every site still fails OPEN exactly as before — these
tests assert the fallback value AND the telemetry, never a raise.
"""
from __future__ import annotations

import numpy as np
import pytest

from src import fail_open


@pytest.fixture(autouse=True)
def _clean_fail_open():
    fail_open.reset()
    yield
    fail_open.reset()


def _count(site: str) -> int:
    snap = fail_open.snapshot()
    return int(snap.get(site, {}).get("count", 0))


def test_regime_hurst_records_on_corrupt_closes():
    from src.regime import _hurst_from_candles, _HURST_MIN_SAMPLES

    corrupt = {"close": ["not-a-number"] * max(_HURST_MIN_SAMPLES, 40)}
    assert _hurst_from_candles(corrupt) is None
    assert _count("regime.hurst") == 1


def test_chart_patterns_detect_patterns_records_on_corrupt_candles():
    from src.chart_patterns import detect_patterns

    corrupt = {"high": ["x"] * 30, "low": ["x"] * 30, "close": ["x"] * 30}
    assert detect_patterns(corrupt) == []
    assert _count("chart_patterns.detect_patterns") == 1


def test_level_book_candle_ts_records_on_unparseable_timestamp():
    from src.level_book import _candle_ts

    assert _candle_ts({"timestamp": ["not-a-ts"]}, 0) is None
    assert _count("level_book.candle_ts") == 1
    # Normal absence (no timestamp key) is NOT a failure — no counter.
    assert _candle_ts({}, 0) is None
    assert _count("level_book.candle_ts") == 1


def test_structure_state_candle_ts_and_refresh_record():
    from src.structure_state import _candle_ts, StructureTracker

    assert _candle_ts({"timestamp": ["bogus"]}, 0) is None
    assert _count("structure_state.candle_ts") == 1

    tracker = StructureTracker()
    corrupt = {"high": [{"nested": 1}] * 40, "low": [{"nested": 1}] * 40}
    assert tracker.refresh("TESTUSDT", "1h", corrupt) is None
    assert _count("structure_state.refresh_arrays") == 1


def test_volume_profile_records_on_corrupt_arrays():
    from src.volume_profile import compute_volume_profile

    corrupt = {
        "high": [{"a": 1}] * 40,
        "low": [{"a": 1}] * 40,
        "volume": [{"a": 1}] * 40,
    }
    assert compute_volume_profile("TESTUSDT", corrupt) is None
    assert _count("volume_profile.compute_arrays") == 1


def test_signal_quality_regime_parse_records_on_unknown_label():
    from src.signal_quality import classify_market_state

    class _FakeRegimeResult:
        regime = "NOT_A_REGIME"

    # Falls back to RANGING handling, never raises.
    classify_market_state(_FakeRegimeResult(), {}, None, spread_pct=0.0)
    assert _count("signal_quality.regime_parse") == 1


def test_mtf_confluence_records_on_corrupt_tf_data_but_not_missing_keys():
    from src.mtf import compute_mtf_confluence

    # Present-but-corrupt data → recorded.
    compute_mtf_confluence(
        "LONG", {"1h": {"ema_fast": "x", "ema_slow": 1.0, "close": 1.0}}
    )
    assert _count("mtf.confluence_tf_parse") == 1
    # Missing keys = normal warmup on young pairs → silent skip, no counter.
    compute_mtf_confluence("LONG", {"1h": {"ema_fast": 1.0}})
    assert _count("mtf.confluence_tf_parse") == 1


def test_mtf_cvd_delta_records_on_corrupt_volume():
    from src.mtf import compute_cross_tf_volume_delta

    compute_cross_tf_volume_delta({"1h": {"buy_volume": "x", "sell_volume": 1.0}})
    assert _count("mtf.cvd_delta_parse") == 1


def test_scalp_path_live_tunable_records_on_unregistered_key():
    from src.channels.scalp import ScalpChannel

    # An unregistered tunable key must fall back to the boot default AND
    # count — a typo'd key silently pinning a path is the failure mode.
    assert ScalpChannel._mover_path_live("no_such_tunable_key_xyz", True) is True
    assert _count("scalp.path_live_tunable") == 1


def test_numpy_arrays_do_not_false_positive():
    """Healthy numpy-shaped inputs must not increment any counter."""
    from src.regime import _hurst_from_candles
    from src.level_book import _candle_ts
    from src.mtf import compute_mtf_confluence

    closes = np.linspace(100.0, 110.0, 60)
    _hurst_from_candles({"close": closes})
    _candle_ts({"timestamp": np.array([1.7e12, 1.7e12 + 60_000])}, 1)
    compute_mtf_confluence(
        "LONG", {"1h": {"ema_fast": 2.0, "ema_slow": 1.0, "close": 2.1}}
    )
    assert fail_open.snapshot() == {}
