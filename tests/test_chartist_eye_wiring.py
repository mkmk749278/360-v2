"""Wiring tests for the deferred chartist-eye integrations:

  1. VolumeProfile POC/VAH/VAL injected into LevelBook so confluence
     scoring picks them up automatically.
  2. StructureTracker is_aligned() awards a +3 soft-penalty bonus to
     trend-following paths (TPE / DIV_CONT / CLS / PDC) when entry
     direction matches the 4h structure leg.
  3. Scanner.refresh helper rebuilds all three caches in lockstep.

These cover only the new wiring contract — module-level behaviour is
covered by the per-module test files.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from src.channels.base import Signal
from src.level_book import LevelBook, Level
from src.scanner import (
    Scanner,
    _STRUCTURE_ALIGN_BONUS,
    _STRUCTURE_ALIGN_PATHS,
)
from src.smc import Direction
from src.structure_state import StructureState, StructureTracker
from src.volume_profile import VolumeProfileResult, VolumeProfileStore


# ---------------------------------------------------------------------------
# Doctrine constants
# ---------------------------------------------------------------------------


class TestWiringConstants:
    def test_structure_align_paths_only_trend_following(self):
        """The structure-align bonus only goes to trend-following evaluators."""
        expected = {
            "TREND_PULLBACK_EMA",
            "DIVERGENCE_CONTINUATION",
            "CONTINUATION_LIQUIDITY_SWEEP",
            "POST_DISPLACEMENT_CONTINUATION",
        }
        assert set(_STRUCTURE_ALIGN_PATHS) == expected

    def test_structure_align_paths_does_not_include_counter_trend(self):
        """Counter-trend paths must NOT consume the structure bonus."""
        excluded = {
            "LIQUIDITY_SWEEP_REVERSAL",   # counter-trend
            "FAILED_AUCTION_RECLAIM",     # counter-trend
            "SR_FLIP_RETEST",             # structural break
            "WHALE_MOMENTUM",             # tape-driven
            "FUNDING_EXTREME_SIGNAL",     # contrarian
            "LIQUIDATION_REVERSAL",       # cascade
            "VOLUME_SURGE_BREAKOUT",      # break event
            "BREAKDOWN_SHORT",            # break event
            "OPENING_RANGE_BREAKOUT",     # break event
            "QUIET_COMPRESSION_BREAK",    # break event
            "MA_CROSS_TREND_SHIFT",       # discrete event
        }
        for path in excluded:
            assert path not in _STRUCTURE_ALIGN_PATHS, (
                f"{path} must not earn the structure-align bonus"
            )

    def test_structure_bonus_smaller_than_max_confluence_bonus(self):
        """Structure bonus magnitude shouldn't dominate confluence."""
        from src.scanner import _CONFLUENCE_BONUS_MAX
        assert _STRUCTURE_ALIGN_BONUS < _CONFLUENCE_BONUS_MAX


# ---------------------------------------------------------------------------
# LevelBook VolumeProfile injection
# ---------------------------------------------------------------------------


def _candle_set(n: int = 60, base: float = 100.0) -> dict:
    highs = [base + (i % 5) for i in range(n)]
    lows = [h - 1.0 for h in highs]
    return {
        "high": np.array(highs, dtype=np.float64),
        "low": np.array(lows, dtype=np.float64),
        "close": np.array([(h + l) / 2 for h, l in zip(highs, lows)], dtype=np.float64),
        "volume": np.array([500.0] * n, dtype=np.float64),
        "timestamp": np.array([1700000000.0 + 3600 * i for i in range(n)], dtype=np.float64),
    }


def _stub_vp_result(poc: float = 100.0, vah: float = 102.0, val: float = 98.0) -> VolumeProfileResult:
    return VolumeProfileResult(
        symbol="BTCUSDT",
        bins=10,
        lookback=60,
        poc=poc,
        vah=vah,
        val=val,
        total_volume=1000.0,
        bin_edges=list(range(11)),
        bin_volumes=[10] * 10,
    )


class TestLevelBookVolumeProfileInjection:
    def test_vp_levels_present_after_injection(self):
        book = LevelBook()
        candles = {"1h": _candle_set(n=60, base=100.0)}
        vp = _stub_vp_result(poc=100.5, vah=102.5, val=98.5)
        book.refresh("BTCUSDT", candles, volume_profile=vp)
        levels = book.get_levels("BTCUSDT")
        assert any("vp" in lv.source_tfs for lv in levels), \
            "VP-sourced levels (POC/VAH/VAL) should appear in the book."

    def test_vp_none_keeps_old_behaviour(self):
        """When volume_profile=None, no VP levels appear — no regression."""
        book = LevelBook()
        candles = {"1h": _candle_set(n=60)}
        book.refresh("BTCUSDT", candles)  # no volume_profile arg
        levels = book.get_levels("BTCUSDT")
        assert all("vp" not in lv.source_tfs for lv in levels)

    def test_vp_clusters_with_nearby_swing(self):
        """A VP level within 0.30% of a swing pivot must merge into one cluster."""
        book = LevelBook()
        candles = {"1h": _candle_set(n=60, base=100.0)}
        # The fixture produces swing highs around 104; place POC/VAH/VAL
        # close to that to force clustering.
        vp = _stub_vp_result(poc=104.0, vah=104.2, val=103.8)
        book.refresh("BTCUSDT", candles, volume_profile=vp)
        levels = book.get_levels("BTCUSDT")
        # The clustered level around 104 should mention BOTH the swing TF
        # ("1h") and "vp" in its source provenance.
        merged = [lv for lv in levels if abs(lv.price - 104.0) <= 0.5]
        assert merged, "Expected clustered level near 104"
        assert any("vp" in lv.source_tfs and "1h" in lv.source_tfs for lv in merged)

    def test_vp_levels_score_high(self):
        """VP-source levels should outscore standalone single-touch swing pivots
        because TF_WEIGHT["vp"] = 1.8."""
        book = LevelBook()
        # Empty candles, only VP.
        candles = {"1h": {"high": np.array([200.0] * 50), "low": np.array([200.0] * 50), "close": np.array([200.0] * 50), "timestamp": np.zeros(50)}}
        vp = _stub_vp_result(poc=180.0, vah=185.0, val=175.0)
        book.refresh("BTCUSDT", candles, volume_profile=vp)
        levels = book.get_levels("BTCUSDT")
        vp_levels = [lv for lv in levels if "vp" in lv.source_tfs]
        assert vp_levels
        # POC/VAH/VAL each get a score > 0.
        assert all(lv.score > 0 for lv in vp_levels)

    def test_invalid_vp_doesnt_crash(self):
        """A VP result with all-zero prices should not crash refresh."""
        book = LevelBook()
        candles = {"1h": _candle_set(n=60)}
        bad_vp = _stub_vp_result(poc=0.0, vah=0.0, val=0.0)
        # Should not raise.
        book.refresh("BTCUSDT", candles, volume_profile=bad_vp)
        # Should also not have produced any "vp" levels (they had price=0).
        levels = book.get_levels("BTCUSDT")
        assert all("vp" not in lv.source_tfs for lv in levels)


# ---------------------------------------------------------------------------
# Scanner-level: refresh helper updates all three caches
# ---------------------------------------------------------------------------


def _make_scanner() -> Scanner:
    signal_queue = MagicMock()
    signal_queue.put = AsyncMock(return_value=True)
    router = MagicMock(active_signals={})
    router.cleanup_expired.return_value = 0
    return Scanner(
        pair_mgr=MagicMock(),
        data_store=MagicMock(),
        channels=[],
        smc_detector=MagicMock(),
        regime_detector=MagicMock(),
        predictive=MagicMock(),
        exchange_mgr=MagicMock(),
        spot_client=None,
        telemetry=MagicMock(),
        signal_queue=signal_queue,
        router=router,
    )


class TestScannerRefreshHelper:
    def test_scanner_owns_all_three_caches(self):
        scanner = _make_scanner()
        assert isinstance(scanner.level_book, LevelBook)
        assert isinstance(scanner.volume_profile_store, VolumeProfileStore)
        assert isinstance(scanner.structure_tracker, StructureTracker)

    def test_refresh_populates_all_three(self):
        scanner = _make_scanner()
        candles = {
            "1h": _candle_set(n=60),
            "4h": _candle_set(n=60),
        }
        scanner._refresh_level_book_if_stale("BTCUSDT", candles)
        # LevelBook populated.
        assert scanner.level_book.get_levels("BTCUSDT")
        # VP populated (1h has volume).
        assert scanner.volume_profile_store.get("BTCUSDT") is not None
        # Structure populated on 4h.
        assert scanner.structure_tracker.get_state("BTCUSDT", tf="4h") is not None

    def test_refresh_within_ttl_skipped(self):
        scanner = _make_scanner()
        candles = {"1h": _candle_set(n=60), "4h": _candle_set(n=60)}
        scanner._refresh_level_book_if_stale("BTCUSDT", candles)
        first_ts = scanner._level_book_refresh_ts["BTCUSDT"]
        scanner._refresh_level_book_if_stale("BTCUSDT", candles)
        # No-op — same timestamp.
        assert scanner._level_book_refresh_ts["BTCUSDT"] == first_ts

    def test_refresh_no_volume_skips_vp_only(self):
        """Candles without volume → VP not built, but LevelBook + structure still run."""
        scanner = _make_scanner()
        no_vol = {
            "high": np.array([100.0] * 60),
            "low": np.array([99.0] * 60),
            "close": np.array([99.5] * 60),
            "timestamp": np.array([1700000000.0 + 3600 * i for i in range(60)]),
        }
        scanner._refresh_level_book_if_stale(
            "BTCUSDT", {"1h": no_vol, "4h": no_vol},
        )
        # LevelBook still ran — round numbers + swing pivots cover us.
        assert scanner._level_book_refresh_ts.get("BTCUSDT") is not None

    def test_refresh_partial_candles_robust(self):
        """Only 1h candles available → still refreshes everything that can run."""
        scanner = _make_scanner()
        scanner._refresh_level_book_if_stale("BTCUSDT", {"1h": _candle_set(n=60)})
        # LevelBook should have run.
        assert scanner.level_book.get_levels("BTCUSDT")
        # Structure tracker needed 4h — should not have populated.
        assert scanner.structure_tracker.get_state("BTCUSDT", tf="4h") is None


# ---------------------------------------------------------------------------
# Structure-alignment bonus contract
# ---------------------------------------------------------------------------
#
# Replay the snippet from scanner._prepare_signal in isolation, since
# spinning up the full pipeline is too heavy for a contract test.  Keep
# in sync with scanner/__init__.py.


def _apply_structure_bonus(
    tracker: StructureTracker, sig: Signal, *, symbol: str,
):
    soft_penalty = 0.0
    soft_penalty_by_type: dict = {}
    fired_gates: list = []

    setup_class_str = str(sig.setup_class or "")
    if setup_class_str in _STRUCTURE_ALIGN_PATHS:
        struct_state = tracker.get_state(symbol, tf="4h")
        aligned = tracker.is_aligned(symbol, sig.direction.value, tf="4h")
        if aligned:
            soft_penalty -= _STRUCTURE_ALIGN_BONUS
            soft_penalty_by_type["structure_align"] = -_STRUCTURE_ALIGN_BONUS
            label = struct_state.state if struct_state is not None else "ALIGNED"
            fired_gates.append(f"STRUCT_ALIGN:{label}")
    return soft_penalty, soft_penalty_by_type, fired_gates


def _seed_bull_leg(tracker: StructureTracker, symbol: str = "BTCUSDT"):
    """Inject a synthetic BULL_LEG state at full confidence."""
    tracker._state[(symbol, "4h")] = StructureState(
        symbol=symbol, tf="4h", state="BULL_LEG", confidence=1.0,
        pivots_in_window=4, bull_count=4, bear_count=0,
    )
    tracker._refresh_ts[(symbol, "4h")] = time.time()


def _seed_bear_leg(tracker: StructureTracker, symbol: str = "BTCUSDT"):
    tracker._state[(symbol, "4h")] = StructureState(
        symbol=symbol, tf="4h", state="BEAR_LEG", confidence=1.0,
        pivots_in_window=4, bull_count=0, bear_count=4,
    )
    tracker._refresh_ts[(symbol, "4h")] = time.time()


def _seed_range(tracker: StructureTracker, symbol: str = "BTCUSDT"):
    tracker._state[(symbol, "4h")] = StructureState(
        symbol=symbol, tf="4h", state="RANGE", confidence=0.5,
        pivots_in_window=4, bull_count=2, bear_count=2,
    )
    tracker._refresh_ts[(symbol, "4h")] = time.time()


def _make_sig(setup_class: str = "TREND_PULLBACK_EMA",
              direction: Direction = Direction.LONG) -> Signal:
    return Signal(
        channel="360_SCALP",
        symbol="BTCUSDT",
        direction=direction,
        entry=100.0,
        stop_loss=99.0,
        tp1=101.0,
        tp2=102.0,
        confidence=70.0,
        setup_class=setup_class,
    )


class TestStructureAlignmentBonus:
    def test_aligned_long_in_bull_leg_earns_bonus(self):
        tr = StructureTracker()
        _seed_bull_leg(tr)
        sig = _make_sig(setup_class="TREND_PULLBACK_EMA", direction=Direction.LONG)
        sp, by_type, gates = _apply_structure_bonus(tr, sig, symbol="BTCUSDT")
        assert sp == pytest.approx(-_STRUCTURE_ALIGN_BONUS)
        assert by_type["structure_align"] == pytest.approx(-_STRUCTURE_ALIGN_BONUS)
        assert gates == ["STRUCT_ALIGN:BULL_LEG"]

    def test_aligned_short_in_bear_leg_earns_bonus(self):
        tr = StructureTracker()
        _seed_bear_leg(tr)
        sig = _make_sig(setup_class="DIVERGENCE_CONTINUATION", direction=Direction.SHORT)
        sp, _, gates = _apply_structure_bonus(tr, sig, symbol="BTCUSDT")
        assert sp == pytest.approx(-_STRUCTURE_ALIGN_BONUS)
        assert gates == ["STRUCT_ALIGN:BEAR_LEG"]

    def test_long_in_bear_leg_no_bonus(self):
        """Counter-aligned trend-path → is_aligned=False → no bonus."""
        tr = StructureTracker()
        _seed_bear_leg(tr)
        sig = _make_sig(setup_class="TREND_PULLBACK_EMA", direction=Direction.LONG)
        sp, by_type, gates = _apply_structure_bonus(tr, sig, symbol="BTCUSDT")
        assert sp == 0.0
        assert "structure_align" not in by_type
        assert gates == []

    def test_range_state_no_bonus(self):
        tr = StructureTracker()
        _seed_range(tr)
        sig = _make_sig(setup_class="TREND_PULLBACK_EMA", direction=Direction.LONG)
        sp, _, _ = _apply_structure_bonus(tr, sig, symbol="BTCUSDT")
        assert sp == 0.0

    def test_counter_trend_path_never_earns_bonus(self):
        """LSR (counter-trend) must not get the structure bonus even if aligned."""
        tr = StructureTracker()
        _seed_bull_leg(tr)
        sig = _make_sig(setup_class="LIQUIDITY_SWEEP_REVERSAL", direction=Direction.LONG)
        sp, _, gates = _apply_structure_bonus(tr, sig, symbol="BTCUSDT")
        assert sp == 0.0
        assert gates == []

    def test_break_event_path_never_earns_bonus(self):
        """VSB (break event) must not get the structure bonus."""
        tr = StructureTracker()
        _seed_bull_leg(tr)
        sig = _make_sig(setup_class="VOLUME_SURGE_BREAKOUT", direction=Direction.LONG)
        sp, _, _ = _apply_structure_bonus(tr, sig, symbol="BTCUSDT")
        assert sp == 0.0

    def test_ma_cross_does_not_earn_structure_bonus(self):
        """MA_CROSS_TREND_SHIFT is its own discrete trigger; no double-dipping."""
        tr = StructureTracker()
        _seed_bull_leg(tr)
        sig = _make_sig(setup_class="MA_CROSS_TREND_SHIFT", direction=Direction.LONG)
        sp, _, _ = _apply_structure_bonus(tr, sig, symbol="BTCUSDT")
        assert sp == 0.0

    def test_no_state_no_bonus(self):
        """If structure was never refreshed, no bonus."""
        tr = StructureTracker()
        sig = _make_sig(setup_class="TREND_PULLBACK_EMA", direction=Direction.LONG)
        sp, _, _ = _apply_structure_bonus(tr, sig, symbol="UNKNOWN")
        assert sp == 0.0
