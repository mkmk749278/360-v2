"""Tests for PR-6 — Multi-TF Level Book confluence-bonus wiring in scanner.

The scanner consults LevelBook.confluence_count(symbol, entry_price) at
final-scoring time and subtracts a bonus from the accumulated
soft_penalty (= raises final confidence).  This file pins the contract:

* Bonus magnitudes by count (2 → 3, 3 → 6, 4+ → 9)
* Bonus tracked under "confluence" in soft_penalty_by_type (negative value)
* "CONFLUENCE×N" appears in soft_gate_flags
* sig.confluence_count populated for telemetry even when no bonus
* Bonus is bounded — count ≥ 4 saturates at the same magnitude as count == 4
* LevelBook refresh is TTL-gated (no per-cycle rebuild)
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import numpy as np
import pytest

from src.channels.base import Signal
from src.level_book import Level, LevelBook
from src.scanner import (
    _CONFLUENCE_BONUS_BY_COUNT,
    _CONFLUENCE_BONUS_MAX,
    _CONFLUENCE_QUERY_TOLERANCE_PCT,
    LEVEL_BOOK_REFRESH_SEC,
)
from src.smc import Direction


# ---------------------------------------------------------------------------
# Tunable constants
# ---------------------------------------------------------------------------


class TestConfluenceTunables:
    def test_bonus_table_monotonic(self):
        """Higher count → higher bonus."""
        assert _CONFLUENCE_BONUS_BY_COUNT[2] < _CONFLUENCE_BONUS_BY_COUNT[3] < _CONFLUENCE_BONUS_BY_COUNT[4]

    def test_bonus_max_matches_top_bucket(self):
        assert _CONFLUENCE_BONUS_MAX == _CONFLUENCE_BONUS_BY_COUNT[4]

    def test_bonus_magnitude_bounded_below_paid_threshold(self):
        """A confluence bonus must never alone lift a sub-50 candidate to paid (65)."""
        assert _CONFLUENCE_BONUS_MAX <= 14.0

    def test_query_tolerance_reasonable(self):
        # >0% so it actually does something; <1% so it stays conservative.
        assert 0.1 <= _CONFLUENCE_QUERY_TOLERANCE_PCT <= 1.0

    def test_refresh_ttl_at_least_an_hour(self):
        assert LEVEL_BOOK_REFRESH_SEC >= 3600.0


# ---------------------------------------------------------------------------
# LevelBook population helper
# ---------------------------------------------------------------------------


def _stub_level(price: float, *, type_: str = "support", tf: str = "1h",
                touches: int = 2, score: float = 30.0,
                round_number: bool = False) -> Level:
    return Level(
        price=price,
        type=type_,
        source_tf=tf,
        touches=touches,
        last_test_ts=time.time() - 3600,
        score=score,
        is_round_number=round_number,
    )


def _seed_book_with_levels(book: LevelBook, symbol: str, levels):
    book._levels[symbol] = list(levels)
    book._refresh_ts[symbol] = time.time()


# ---------------------------------------------------------------------------
# Confluence-count contract via LevelBook (independent of scanner)
# ---------------------------------------------------------------------------


class TestConfluenceCountContract:
    def test_two_close_levels_count_two(self):
        book = LevelBook()
        _seed_book_with_levels(book, "BTCUSDT", [
            _stub_level(100.00),
            _stub_level(100.20),
        ])
        # Both within 0.30% of 100.10
        assert book.confluence_count("BTCUSDT", 100.10, tolerance_pct=0.30) == 2

    def test_three_close_levels_count_three(self):
        book = LevelBook()
        _seed_book_with_levels(book, "BTCUSDT", [
            _stub_level(99.90),
            _stub_level(100.00, round_number=True),
            _stub_level(100.20, tf="4h"),
        ])
        assert book.confluence_count("BTCUSDT", 100.10, tolerance_pct=0.30) == 3

    def test_no_levels_in_band(self):
        book = LevelBook()
        _seed_book_with_levels(book, "BTCUSDT", [_stub_level(110.00)])
        assert book.confluence_count("BTCUSDT", 100.00, tolerance_pct=0.30) == 0

    def test_unknown_symbol_zero(self):
        book = LevelBook()
        assert book.confluence_count("OTHER", 100.0) == 0


# ---------------------------------------------------------------------------
# Scanner-level wiring — directly exercise _refresh_level_book_if_stale
# ---------------------------------------------------------------------------


def _make_minimal_scanner():
    """Build the smallest Scanner that lets us hit the LevelBook helper."""
    from src.scanner import Scanner
    signal_queue = MagicMock()
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
        router=MagicMock(),
    )


def _candle_set(n: int = 60, base: float = 100.0) -> dict:
    highs = [base + (i % 5) for i in range(n)]
    lows = [h - 1.0 for h in highs]
    return {
        "high": np.array(highs, dtype=np.float64),
        "low": np.array(lows, dtype=np.float64),
        "close": np.array([(h + l) / 2 for h, l in zip(highs, lows)], dtype=np.float64),
        "timestamp": np.array([1700000000.0 + 3600 * i for i in range(n)], dtype=np.float64),
    }


class TestLevelBookRefreshTTL:
    def test_first_refresh_populates_book(self):
        scanner = _make_minimal_scanner()
        candles = {"1h": _candle_set(n=60), "4h": _candle_set(n=60)}
        scanner._refresh_level_book_if_stale("BTCUSDT", candles)
        assert scanner.level_book.get_levels("BTCUSDT")
        assert scanner._level_book_refresh_ts.get("BTCUSDT") is not None

    def test_subsequent_call_within_ttl_skipped(self):
        scanner = _make_minimal_scanner()
        candles = {"1h": _candle_set(n=60)}
        scanner._refresh_level_book_if_stale("BTCUSDT", candles)
        first_ts = scanner._level_book_refresh_ts["BTCUSDT"]
        # Same call within TTL must not bump the timestamp.
        scanner._refresh_level_book_if_stale("BTCUSDT", candles)
        assert scanner._level_book_refresh_ts["BTCUSDT"] == first_ts

    def test_refresh_after_ttl_elapsed(self):
        scanner = _make_minimal_scanner()
        candles = {"1h": _candle_set(n=60)}
        scanner._refresh_level_book_if_stale("BTCUSDT", candles)
        # Forge an old timestamp.
        scanner._level_book_refresh_ts["BTCUSDT"] = time.time() - LEVEL_BOOK_REFRESH_SEC - 1
        old_levels = scanner.level_book.get_levels("BTCUSDT")
        scanner._refresh_level_book_if_stale("BTCUSDT", candles)
        # Refreshed.
        assert scanner._level_book_refresh_ts["BTCUSDT"] > time.time() - 5
        # Same input → same level set produced.
        new_levels = scanner.level_book.get_levels("BTCUSDT")
        assert len(new_levels) == len(old_levels)

    def test_refresh_no_op_when_no_candles(self):
        scanner = _make_minimal_scanner()
        scanner._refresh_level_book_if_stale("BTCUSDT", {})
        assert scanner._level_book_refresh_ts.get("BTCUSDT") is None
        assert scanner.level_book.get_levels("BTCUSDT") == []

    def test_refresh_robust_to_partial_candles(self):
        """Missing 4h is fine; just use whatever TFs are present."""
        scanner = _make_minimal_scanner()
        scanner._refresh_level_book_if_stale("BTCUSDT", {"1h": _candle_set(n=60)})
        assert scanner.level_book.get_levels("BTCUSDT")


# ---------------------------------------------------------------------------
# Bonus contract via direct snippet replay
# ---------------------------------------------------------------------------
#
# Rather than spin up the full _prepare_signal pipeline (which has 22+
# dependencies), we replay the small confluence-bonus block exactly as it
# appears in scanner/__init__.py against a stub LevelBook + Signal.  This
# pins the contract: count → bonus, soft_penalty_by_type tracking, and
# soft_gate_flags string.


def _apply_confluence_bonus(book: LevelBook, sig: Signal, *, symbol: str):
    """Replay of the production snippet — keep in sync with scanner/__init__.py."""
    soft_penalty = 0.0
    soft_penalty_by_type: dict = {}
    fired_gates: list = []

    n = book.confluence_count(symbol, sig.entry, tolerance_pct=_CONFLUENCE_QUERY_TOLERANCE_PCT)
    if n >= 2:
        bonus = _CONFLUENCE_BONUS_BY_COUNT.get(min(n, 4), _CONFLUENCE_BONUS_MAX)
        soft_penalty -= bonus
        soft_penalty_by_type["confluence"] = soft_penalty_by_type.get("confluence", 0.0) - bonus
        fired_gates.append(f"CONFLUENCE×{n}")
    sig.confluence_count = n

    return soft_penalty, soft_penalty_by_type, fired_gates


class TestConfluenceBonusContract:
    def _make_sig(self, entry: float = 100.10) -> Signal:
        return Signal(
            channel="360_SCALP",
            symbol="BTCUSDT",
            direction=Direction.LONG,
            entry=entry,
            stop_loss=entry * 0.99,
            tp1=entry * 1.01,
            tp2=entry * 1.02,
            confidence=70.0,
        )

    def test_two_levels_three_point_bonus(self):
        book = LevelBook()
        _seed_book_with_levels(book, "BTCUSDT", [
            _stub_level(100.00),
            _stub_level(100.20),
        ])
        sig = self._make_sig(entry=100.10)
        sp, by_type, gates = _apply_confluence_bonus(book, sig, symbol="BTCUSDT")
        assert sp == pytest.approx(-3.0)
        assert by_type["confluence"] == pytest.approx(-3.0)
        assert gates == ["CONFLUENCE×2"]
        assert sig.confluence_count == 2

    def test_three_levels_six_point_bonus(self):
        book = LevelBook()
        _seed_book_with_levels(book, "BTCUSDT", [
            _stub_level(99.90),
            _stub_level(100.00, round_number=True),
            _stub_level(100.20),
        ])
        sig = self._make_sig(entry=100.10)
        sp, by_type, gates = _apply_confluence_bonus(book, sig, symbol="BTCUSDT")
        assert sp == pytest.approx(-6.0)
        assert by_type["confluence"] == pytest.approx(-6.0)
        assert gates == ["CONFLUENCE×3"]
        assert sig.confluence_count == 3

    def test_four_levels_nine_point_bonus(self):
        book = LevelBook()
        _seed_book_with_levels(book, "BTCUSDT", [
            _stub_level(99.90),
            _stub_level(100.00, round_number=True),
            _stub_level(100.10, tf="4h"),
            _stub_level(100.20),
        ])
        sig = self._make_sig(entry=100.10)
        sp, _, gates = _apply_confluence_bonus(book, sig, symbol="BTCUSDT")
        assert sp == pytest.approx(-9.0)
        assert gates == ["CONFLUENCE×4"]
        assert sig.confluence_count == 4

    def test_five_plus_levels_saturate_at_max(self):
        """count ≥ 4 must not exceed the bonus max — protects from runaway lift."""
        book = LevelBook()
        _seed_book_with_levels(book, "BTCUSDT", [
            _stub_level(99.85),
            _stub_level(99.95),
            _stub_level(100.05),
            _stub_level(100.15),
            _stub_level(100.25, round_number=True),
        ])
        sig = self._make_sig(entry=100.10)
        sp, _, gates = _apply_confluence_bonus(book, sig, symbol="BTCUSDT")
        assert sp == pytest.approx(-_CONFLUENCE_BONUS_MAX)
        assert sig.confluence_count == 5
        assert gates == ["CONFLUENCE×5"]

    def test_one_level_no_bonus(self):
        book = LevelBook()
        _seed_book_with_levels(book, "BTCUSDT", [_stub_level(100.00)])
        sig = self._make_sig(entry=100.10)
        sp, by_type, gates = _apply_confluence_bonus(book, sig, symbol="BTCUSDT")
        assert sp == 0.0
        assert "confluence" not in by_type
        assert gates == []
        # sig.confluence_count populated for telemetry even without bonus.
        assert sig.confluence_count == 1

    def test_no_levels_zero_bonus(self):
        book = LevelBook()
        sig = self._make_sig()
        sp, by_type, gates = _apply_confluence_bonus(book, sig, symbol="UNKNOWN")
        assert sp == 0.0
        assert gates == []
        assert sig.confluence_count == 0

    def test_signal_field_default_is_zero(self):
        """A freshly-built signal that hasn't gone through scoring has confluence_count=0."""
        sig = self._make_sig()
        assert sig.confluence_count == 0
