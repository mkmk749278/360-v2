"""Tests for the chartist-eye seeding-gap fixes (2026-05-06):

1. 1w timeframe added to SEED_TIMEFRAMES (cycle-level S/R for SCALP pairs)
2. LevelBook accepts 1w candles + 1w in TF_WEIGHT (cycle-level outscores 1d)
3. LevelBook.refresh accepts a list of VolumeProfile results
4. Scanner refreshes BOTH micro (1h) and macro (1d) volume profiles
5. MA-cross cooldown registry persists to disk and reloads on init
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest

from config import SEED_TIMEFRAMES
from src.channels.scalp import ScalpChannel
from src.level_book import (
    SWING_ORDER_BY_TF,
    TF_WEIGHT,
    LevelBook,
)
from src.scanner import Scanner
from src.smc import Direction
from src.volume_profile import VolumeProfileResult


# ---------------------------------------------------------------------------
# Piece 1: 1w in SEED_TIMEFRAMES
# ---------------------------------------------------------------------------


class TestSeedTimeframes1wPresent:
    def test_seed_includes_1w(self):
        intervals = [tf.interval for tf in SEED_TIMEFRAMES]
        assert "1w" in intervals, (
            "1w must be seeded so LevelBook can discover cycle-level "
            "S/R for SCALP pairs (chartist-eye seeding-gap fix)."
        )

    def test_1w_seed_lookback_at_least_100(self):
        for tf in SEED_TIMEFRAMES:
            if tf.interval == "1w":
                # Need enough weekly candles to capture meaningful pivots
                # (at minimum 1 year + 2 swing-order on each side).
                assert tf.limit >= 100


# ---------------------------------------------------------------------------
# Piece 2: LevelBook handles 1w
# ---------------------------------------------------------------------------


class TestLevelBookWeekly:
    def test_1w_in_tf_weight(self):
        assert "1w" in TF_WEIGHT

    def test_1w_outscores_1d(self):
        """Weekly cycle pivots are MORE structurally meaningful than daily."""
        assert TF_WEIGHT["1w"] > TF_WEIGHT["1d"]

    def test_1w_in_swing_order_by_tf(self):
        assert "1w" in SWING_ORDER_BY_TF

    def test_1w_swing_order_smaller_than_1h(self):
        """Higher TFs use smaller swing-order (fewer candles needed each side)."""
        assert SWING_ORDER_BY_TF["1w"] <= SWING_ORDER_BY_TF["1h"]

    def test_levelbook_consumes_1w_candles(self):
        """A 1w candle set with clear pivots produces vp-source-aware levels."""
        book = LevelBook()
        n = 60
        # Fixture: oscillating weekly highs/lows around 100, with a clear
        # peak at index 25 hitting 120.
        highs = np.array([100.0 + (i % 5) for i in range(n)], dtype=np.float64)
        lows = np.array([99.0 + (i % 5) for i in range(n)], dtype=np.float64)
        highs[25] = 120.0
        lows[25] = 119.0
        candles_1w = {
            "high": highs,
            "low": lows,
            "close": (highs + lows) / 2,
            "timestamp": np.array([1700000000.0 + 7 * 86400 * i for i in range(n)]),
        }
        out = book.refresh("BTCUSDT", {"1w": candles_1w})
        # At minimum some level should be tagged "1w".
        assert any("1w" in lv.source_tfs for lv in out)


# ---------------------------------------------------------------------------
# Piece 3: LevelBook.refresh accepts list of VPs
# ---------------------------------------------------------------------------


def _stub_vp(symbol: str, poc: float, vah: float, val: float) -> VolumeProfileResult:
    return VolumeProfileResult(
        symbol=symbol,
        bins=10,
        lookback=200,
        poc=poc,
        vah=vah,
        val=val,
        total_volume=1000.0,
        bin_edges=list(range(11)),
        bin_volumes=[10] * 10,
    )


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


class TestLevelBookListOfVps:
    def test_single_vp_still_works(self):
        book = LevelBook()
        candles = {"1h": _candle_set(n=60)}
        single_vp = _stub_vp("BTCUSDT", 100.5, 102.5, 98.5)
        book.refresh("BTCUSDT", candles, volume_profile=single_vp)
        levels = book.get_levels("BTCUSDT")
        assert any("vp" in lv.source_tfs for lv in levels)

    def test_list_of_vps_both_inject(self):
        book = LevelBook()
        candles = {"1h": _candle_set(n=60)}
        micro = _stub_vp("BTCUSDT", 100.5, 102.5, 98.5)   # close to current
        macro = _stub_vp("BTCUSDT", 80.0, 90.0, 70.0)     # far from current
        book.refresh("BTCUSDT", candles, volume_profile=[micro, macro])
        levels = book.get_levels("BTCUSDT")
        # Both micro (~100) and macro (~80) zones should produce vp levels.
        prices = [lv.price for lv in levels if "vp" in lv.source_tfs]
        assert any(99 <= p <= 103 for p in prices)
        assert any(70 <= p <= 92 for p in prices)

    def test_empty_list_is_no_op(self):
        book = LevelBook()
        candles = {"1h": _candle_set(n=60)}
        book.refresh("BTCUSDT", candles, volume_profile=[])
        levels = book.get_levels("BTCUSDT")
        assert all("vp" not in lv.source_tfs for lv in levels)

    def test_list_with_none_entries_skipped(self):
        book = LevelBook()
        candles = {"1h": _candle_set(n=60)}
        book.refresh(
            "BTCUSDT", candles,
            volume_profile=[None, _stub_vp("BTCUSDT", 101.0, 103.0, 99.0), None],
        )
        levels = book.get_levels("BTCUSDT")
        assert any("vp" in lv.source_tfs for lv in levels)


# ---------------------------------------------------------------------------
# Piece 4: Scanner refreshes both micro and macro VPs
# ---------------------------------------------------------------------------


def _make_scanner() -> Scanner:
    queue = MagicMock()
    queue.put = AsyncMock(return_value=True)
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
        signal_queue=queue,
        router=router,
    )


class TestScannerMacroVp:
    def test_scanner_owns_two_vp_stores(self):
        scanner = _make_scanner()
        assert scanner.volume_profile_store is not None         # micro
        assert scanner.volume_profile_store_macro is not None    # macro
        assert scanner.volume_profile_store is not scanner.volume_profile_store_macro

    def test_refresh_populates_both_vp_stores(self):
        scanner = _make_scanner()
        scanner._refresh_level_book_if_stale(
            "BTCUSDT",
            {
                "1h": _candle_set(n=60, base=100.0),
                "1d": _candle_set(n=200, base=80.0),  # different price scale
                "4h": _candle_set(n=60, base=100.0),
            },
        )
        assert scanner.volume_profile_store.get("BTCUSDT") is not None
        assert scanner.volume_profile_store_macro.get("BTCUSDT") is not None

    def test_refresh_consumes_1w_when_present(self):
        scanner = _make_scanner()
        n = 60
        highs = np.array([100.0 + (i % 5) for i in range(n)], dtype=np.float64)
        lows = np.array([99.0 + (i % 5) for i in range(n)], dtype=np.float64)
        # Inject a clear 1w pivot at idx 25.
        highs[25] = 130.0
        lows[25] = 129.0
        candles_1w = {
            "high": highs, "low": lows,
            "close": (highs + lows) / 2,
            "volume": np.array([100.0] * n),
            "timestamp": np.array([1700000000.0 + 7 * 86400 * i for i in range(n)]),
        }
        scanner._refresh_level_book_if_stale(
            "BTCUSDT", {
                "1w": candles_1w,
                "1h": _candle_set(n=60),
                "4h": _candle_set(n=60),
            },
        )
        levels = scanner.level_book.get_levels("BTCUSDT")
        assert any("1w" in lv.source_tfs for lv in levels), \
            "Scanner should pass 1w candles into LevelBook."

    def test_refresh_skips_macro_when_no_1d(self):
        scanner = _make_scanner()
        scanner._refresh_level_book_if_stale(
            "BTCUSDT", {"1h": _candle_set(n=60)},
        )
        # Micro should be populated.
        assert scanner.volume_profile_store.get("BTCUSDT") is not None
        # Macro should NOT (no 1d candles passed).
        assert scanner.volume_profile_store_macro.get("BTCUSDT") is None


# ---------------------------------------------------------------------------
# Piece 5: MA-cross cooldown persistence
# ---------------------------------------------------------------------------


@pytest.fixture
def isolated_cooldown_path(tmp_path, monkeypatch):
    cd_path = tmp_path / "ma_cross_cooldown.json"
    monkeypatch.setattr(ScalpChannel, "_MA_CROSS_COOLDOWN_PATH", str(cd_path))
    return cd_path


class TestMaCrossCooldownPersistence:
    def test_load_with_no_file_starts_empty(self, isolated_cooldown_path):
        ch = ScalpChannel()
        assert ch._ma_cross_last_fire_ts == {}

    def test_persist_and_reload_round_trip(self, isolated_cooldown_path):
        ch = ScalpChannel()
        ch._ma_cross_last_fire_ts[("BTCUSDT", "LONG")] = 1700000000.0
        ch._ma_cross_last_fire_ts[("ETHUSDT", "SHORT")] = 1700001000.0
        ch._persist_ma_cross_cooldown()
        # File contains both entries.
        data = json.loads(isolated_cooldown_path.read_text(encoding="utf-8"))
        assert data["BTCUSDT|LONG"] == 1700000000.0
        assert data["ETHUSDT|SHORT"] == 1700001000.0
        # Fresh ScalpChannel reloads them.
        ch2 = ScalpChannel()
        assert ch2._ma_cross_last_fire_ts.get(("BTCUSDT", "LONG")) == 1700000000.0
        assert ch2._ma_cross_last_fire_ts.get(("ETHUSDT", "SHORT")) == 1700001000.0

    def test_corrupt_file_doesnt_crash(self, isolated_cooldown_path):
        isolated_cooldown_path.parent.mkdir(parents=True, exist_ok=True)
        isolated_cooldown_path.write_text("garbage{{{not-json", encoding="utf-8")
        # Should not raise.
        ch = ScalpChannel()
        assert ch._ma_cross_last_fire_ts == {}

    def test_malformed_keys_skipped(self, isolated_cooldown_path):
        isolated_cooldown_path.parent.mkdir(parents=True, exist_ok=True)
        isolated_cooldown_path.write_text(
            json.dumps({
                "BTCUSDT|LONG": 1700000000.0,    # valid
                "no_pipe_here": 1700000001.0,    # invalid (no |)
                "BAD|LONG": "not_a_float",       # invalid value
            }),
            encoding="utf-8",
        )
        ch = ScalpChannel()
        assert ch._ma_cross_last_fire_ts.get(("BTCUSDT", "LONG")) == 1700000000.0
        assert len(ch._ma_cross_last_fire_ts) == 1

    def test_evaluator_persists_on_successful_fire(
        self, isolated_cooldown_path, monkeypatch,
    ):
        """End-to-end: a successful MA-cross signal writes the cooldown to disk."""
        ch = ScalpChannel()

        def _candles_1m(n: int = 10, base: float = 100.0) -> dict:
            closes = np.array([base] * n, dtype=np.float64)
            return {
                "open": closes, "high": closes + 0.1, "low": closes - 0.1,
                "close": closes, "volume": np.full(n, 500.0),
            }

        def _candles_1h(n: int = 50) -> dict:
            highs = np.array([105.0 - 1.0] * n, dtype=np.float64)
            lows = np.array([95.0 + 1.0] * n, dtype=np.float64)
            highs[5] = 105.0
            lows[5] = 95.0
            return {
                "open": (highs + lows) / 2,
                "high": highs, "low": lows,
                "close": (highs + lows) / 2,
                "volume": np.full(n, 500.0),
            }

        ind = {
            "1m": {"rsi_last": 60.0, "ema9_last": 100.5, "ema21_last": 100.0, "atr_last": 0.5},
            "1h": {"rsi_last": 60.0, "atr_last": 0.5},
            "4h": {
                "ema50": [99.0, 100.5], "ema200": [99.5, 100.0],
                "ema50_last": 100.5, "ema200_last": 100.0,
            },
        }
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", {"1m": _candles_1m(), "1h": _candles_1h()},
            ind, {}, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None
        # File written; survives a fresh ScalpChannel.
        assert isolated_cooldown_path.exists()
        ch2 = ScalpChannel()
        assert ("BTCUSDT", Direction.LONG.value) in ch2._ma_cross_last_fire_ts
