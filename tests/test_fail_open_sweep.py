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


# ---------------------------------------------------------------------------
# 2026-07-16 audit sweep — the gate-chain half #727/S58 skipped
# ---------------------------------------------------------------------------


def test_structural_sltp_snap_records_and_falls_back_to_atr_levels():
    """channels/base.py structural snap is shared by EVERY evaluator that
    passes candle arrays — a find_swing_levels regression would silently
    revert all signals to raw ATR geometry.  Pin: fail open + counted."""
    from src.channels.base import ChannelConfig, build_channel_signal
    from src.smc import Direction

    cfg = ChannelConfig(
        name="360_SCALP", emoji="s", timeframes=["5m"], sl_pct_range=(0.5, 3.0),
        tp_ratios=[1.0, 2.0, 3.0], trailing_atr_mult=1.0, adx_min=0.0,
        adx_max=100.0, spread_max=0.1, min_confidence=0.0,
    )
    sig = build_channel_signal(
        cfg, "BTCUSDT", Direction.LONG,
        close=100.0, sl=99.0, tp1=101.0, tp2=102.0, tp3=103.0,
        sl_dist=1.0, id_prefix="t",
        candle_highs={"bad": 1}, candle_lows={"bad": 1}, candle_closes={"bad": 1},
    )
    assert sig is not None  # fail open — ATR-based levels survive
    assert sig.stop_loss == pytest.approx(99.0)
    assert _count("channels.structural_sltp_snap") == 1


def test_shadow_unit_errors_are_counted_not_swallowed():
    """The MEAN_REVERT shadow unit is the ungated control arm for the live
    evaluator — if it silently stops stamping, the live-vs-shadow drift
    check is blind.  Pin: unit errors count while staying fail-neutral."""
    from src import shadow_strategies as ss

    out = ss.evaluate_all(
        highs=["x"] * 400, lows=["x"] * 400, closes=["x"] * 400,
        funding_rate=0.001,
    )
    assert out == []  # fail-neutral: no candidates, no raise
    assert _count("shadow_strategies.unit_eval") >= 1


def test_scanner_gate_chain_has_no_silent_exception_pass():
    """AST pin: no NEW bare ``except Exception: pass`` in the scanner.

    The 2026-07-16 audit converted every data/measurement swallow in the
    gate chain to fail_open.record.  The survivors are messaging/heartbeat
    best-effort sends and warmup-normal attribute fallbacks — allowlisted
    by count.  If this fails after your change: call
    ``fail_open.record("scanner.<site>", exc)`` instead of ``pass``
    (data/measurement path), or update the count WITH justification here
    (genuinely-benign best-effort side channel)."""
    import ast as _ast
    import pathlib

    src = (
        pathlib.Path(__file__).resolve().parent.parent
        / "src" / "scanner" / "__init__.py"
    ).read_text(encoding="utf-8")
    bare = []
    for node in _ast.walk(_ast.parse(src)):
        if not isinstance(node, _ast.ExceptHandler):
            continue
        if len(node.body) == 1 and isinstance(node.body[0], _ast.Pass):
            # Only Exception-typed (or untyped) handlers count — typed
            # narrow handlers (OSError, TypeError/ValueError coercion
            # contract) are deliberate.
            t = node.type
            if t is None or (isinstance(t, _ast.Name) and t.id == "Exception"):
                bare.append(node.lineno)
    # 8 allowlisted survivors (2026-07-16): 6 admin-alert/free-channel
    # message best-effort sends, 1 protective-mode broadcast wrapper,
    # 1 radar-pass regime-string warmup fallback.
    assert len(bare) <= 8, (
        f"new silent 'except Exception: pass' in scanner at lines {bare} — "
        "data/measurement paths must call fail_open.record"
    )
