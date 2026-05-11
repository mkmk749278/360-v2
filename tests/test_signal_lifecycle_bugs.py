"""Tests for the 2026-05-07 signal-lifecycle bug fixes.

Three bugs surfaced when MIN_CONFIDENCE_SCALP was lowered from 80 → 65:

1. **Duplicate dispatches** — same setup re-fired every cycle on the same
   symbol+direction.  Fix: per-(symbol, setup, direction) cooldown.
2. **Stale entry vs current price** — signal proposes entry at 626.85 but
   current price is already at SL (631.86).  Fix: pre-dispatch staleness
   check.
3. **Limit-order treated as filled** — trade_monitor evaluated SL/TP
   against the unfilled mid as if the limit had triggered.  Fix:
   ``entry_zone_filled`` flag gating SL/TP checks.

Tests bypass the conftest's autouse cooldown disable for the cooldown
suite (re-enable to assert the contract).
"""

from __future__ import annotations

import time
from types import SimpleNamespace
from unittest.mock import MagicMock

import numpy as np
import pytest

import src.scanner as _scanner_mod
from src.channels.base import Signal
from src.scanner import (
    DISPATCH_STALENESS_MAX_DRIFT_PCT,
    Scanner,
)
from src.smc import Direction


def _make_scanner_for_lifecycle() -> Scanner:
    """Bare scanner with everything mocked except the cooldown logic."""
    queue = MagicMock()

    async def _put(sig):
        return True

    queue.put = _put

    data_store = MagicMock()
    # Configure data_store.candles to behave like a dict for staleness lookup.
    data_store.candles = {}

    return Scanner(
        pair_mgr=MagicMock(),
        data_store=data_store,
        channels=[],
        smc_detector=MagicMock(),
        regime_detector=MagicMock(),
        predictive=MagicMock(),
        exchange_mgr=MagicMock(),
        spot_client=None,
        telemetry=MagicMock(),
        signal_queue=queue,
        router=MagicMock(active_signals={}),
    )


def _make_signal(
    *,
    symbol: str = "BTCUSDT",
    setup_class: str = "FAILED_AUCTION_RECLAIM",
    direction: Direction = Direction.SHORT,
    entry: float = 100.0,
    stop_loss: float = 101.0,
) -> Signal:
    return Signal(
        channel="360_SCALP",
        symbol=symbol,
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp1=99.0,
        tp2=98.0,
        confidence=70.0,
        setup_class=setup_class,
    )


# ---------------------------------------------------------------------------
# Bug #1: dispatch cooldown
# ---------------------------------------------------------------------------


class TestDispatchCooldown:
    @pytest.mark.asyncio
    async def test_first_dispatch_succeeds(self, monkeypatch):
        """Without prior fire, dispatch goes through."""
        monkeypatch.setattr(_scanner_mod, "DISPATCH_COOLDOWN_SEC", 1800.0)
        monkeypatch.setattr(Scanner, "_is_entry_fresh", lambda self, sig: True)
        scanner = _make_scanner_for_lifecycle()
        sig = _make_signal()
        ok = await scanner._enqueue_signal(sig)
        assert ok is True
        # Cooldown stamped after success.
        key = ("BTCUSDT", "FAILED_AUCTION_RECLAIM", "SHORT")
        assert key in scanner._dispatch_cooldown

    @pytest.mark.asyncio
    async def test_duplicate_within_cooldown_blocked(self, monkeypatch):
        """Same (symbol, setup, direction) within cooldown returns False."""
        monkeypatch.setattr(_scanner_mod, "DISPATCH_COOLDOWN_SEC", 1800.0)
        monkeypatch.setattr(Scanner, "_is_entry_fresh", lambda self, sig: True)
        scanner = _make_scanner_for_lifecycle()
        sig1 = _make_signal()
        await scanner._enqueue_signal(sig1)
        # Identical setup, different signal_id — should be blocked.
        sig2 = _make_signal()
        ok = await scanner._enqueue_signal(sig2)
        assert ok is False

    @pytest.mark.asyncio
    async def test_different_symbol_not_blocked(self, monkeypatch):
        monkeypatch.setattr(_scanner_mod, "DISPATCH_COOLDOWN_SEC", 1800.0)
        monkeypatch.setattr(Scanner, "_is_entry_fresh", lambda self, sig: True)
        scanner = _make_scanner_for_lifecycle()
        await scanner._enqueue_signal(_make_signal(symbol="BTCUSDT"))
        ok = await scanner._enqueue_signal(_make_signal(symbol="ETHUSDT"))
        assert ok is True

    @pytest.mark.asyncio
    async def test_different_direction_not_blocked(self, monkeypatch):
        monkeypatch.setattr(_scanner_mod, "DISPATCH_COOLDOWN_SEC", 1800.0)
        monkeypatch.setattr(Scanner, "_is_entry_fresh", lambda self, sig: True)
        scanner = _make_scanner_for_lifecycle()
        await scanner._enqueue_signal(_make_signal(direction=Direction.LONG))
        ok = await scanner._enqueue_signal(_make_signal(direction=Direction.SHORT))
        assert ok is True

    @pytest.mark.asyncio
    async def test_different_setup_class_not_blocked(self, monkeypatch):
        monkeypatch.setattr(_scanner_mod, "DISPATCH_COOLDOWN_SEC", 1800.0)
        monkeypatch.setattr(Scanner, "_is_entry_fresh", lambda self, sig: True)
        scanner = _make_scanner_for_lifecycle()
        await scanner._enqueue_signal(_make_signal(setup_class="FAILED_AUCTION_RECLAIM"))
        ok = await scanner._enqueue_signal(_make_signal(setup_class="SR_FLIP_RETEST"))
        assert ok is True

    @pytest.mark.asyncio
    async def test_after_cooldown_elapses_re_fires(self, monkeypatch):
        monkeypatch.setattr(_scanner_mod, "DISPATCH_COOLDOWN_SEC", 1800.0)
        monkeypatch.setattr(Scanner, "_is_entry_fresh", lambda self, sig: True)
        scanner = _make_scanner_for_lifecycle()
        await scanner._enqueue_signal(_make_signal())
        # Forge expiry (1801s ago).
        key = ("BTCUSDT", "FAILED_AUCTION_RECLAIM", "SHORT")
        scanner._dispatch_cooldown[key] = time.time() - 1801.0
        ok = await scanner._enqueue_signal(_make_signal())
        assert ok is True


# ---------------------------------------------------------------------------
# Bug #2: pre-dispatch staleness check
# ---------------------------------------------------------------------------


def _seed_data_store_close(scanner: Scanner, symbol: str, close: float):
    """Inject a 1m candle close so _is_entry_fresh has data."""
    scanner.data_store.candles = {
        symbol: {
            "1m": {
                "close": np.array([close - 0.5, close - 0.2, close]),
                "high": np.array([close + 0.1, close + 0.1, close + 0.1]),
                "low": np.array([close - 0.6, close - 0.3, close - 0.05]),
            }
        }
    }


def _real_is_entry_fresh(self, sig):
    """Inlined copy of the production Scanner._is_entry_fresh logic so
    the staleness tests can run the real algorithm without disturbing
    other conftest monkeypatches (no module reload here)."""
    try:
        entry = float(getattr(sig, "entry", 0.0) or 0.0)
        if entry <= 0:
            return True
        symbol = getattr(sig, "symbol", "")
        if not symbol:
            return True
        data_store = getattr(self, "data_store", None)
        if data_store is None:
            return True
        symbol_candles = (
            data_store.candles.get(symbol)
            if hasattr(data_store, "candles") else None
        )
        if not symbol_candles:
            return True
        for tf in ("1m", "5m", "15m", "1h"):
            cd = symbol_candles.get(tf)
            if not cd or "close" not in cd:
                continue
            closes = cd["close"]
            if closes is None or len(closes) == 0:
                continue
            current_price = float(closes[-1])
            if current_price <= 0:
                continue
            drift_pct = abs(current_price - entry) / entry * 100.0
            return drift_pct <= DISPATCH_STALENESS_MAX_DRIFT_PCT
    except Exception:
        return True
    return True


@pytest.fixture
def _real_staleness_check(monkeypatch):
    """Restore ONLY the real ``Scanner._is_entry_fresh`` for staleness tests.

    Replaces the conftest's no-op lambda with the inlined production
    implementation (above) — narrow patch that doesn't disturb the
    cooldown / persist no-ops.
    """
    monkeypatch.setattr(Scanner, "_is_entry_fresh", _real_is_entry_fresh)
    yield


class TestEntryStaleness:
    @pytest.mark.asyncio
    async def test_fresh_entry_passes(self, monkeypatch, _real_staleness_check):
        """Entry within DRIFT_PCT of current price → passes."""
        monkeypatch.setattr(_scanner_mod, "DISPATCH_COOLDOWN_SEC", 0.0)
        scanner = _make_scanner_for_lifecycle()
        _seed_data_store_close(scanner, "BTCUSDT", 100.0)
        sig = _make_signal(entry=100.2)  # 0.2% drift, well under 0.5%
        ok = await scanner._enqueue_signal(sig)
        assert ok is True

    @pytest.mark.asyncio
    async def test_stale_entry_rejected(self, monkeypatch, _real_staleness_check):
        """The 2026-05-07 BNBUSDT bug: entry=626.85 but current=631.86 (0.8% drift)."""
        monkeypatch.setattr(_scanner_mod, "DISPATCH_COOLDOWN_SEC", 0.0)
        scanner = _make_scanner_for_lifecycle()
        _seed_data_store_close(scanner, "BNBUSDT", 631.86)
        sig = _make_signal(symbol="BNBUSDT", entry=626.85, stop_loss=631.86)
        ok = await scanner._enqueue_signal(sig)
        assert ok is False

    @pytest.mark.asyncio
    async def test_no_data_store_fails_open(self, monkeypatch, _real_staleness_check):
        """No candle data → fail-open (don't block the signal)."""
        monkeypatch.setattr(_scanner_mod, "DISPATCH_COOLDOWN_SEC", 0.0)
        scanner = _make_scanner_for_lifecycle()
        # No candles seeded.
        ok = await scanner._enqueue_signal(_make_signal())
        assert ok is True

    def test_drift_threshold_is_reasonable(self):
        # 0.5% is a sensible default — gentle enough to allow normal
        # mid-candle drift, strict enough to catch the price-already-at-SL
        # pathology from the bug.
        assert 0.1 <= DISPATCH_STALENESS_MAX_DRIFT_PCT <= 1.5


# ---------------------------------------------------------------------------
# Bug #4: data-staleness gate (2026-05-11 QUSDT carbon-copy emissions)
# ---------------------------------------------------------------------------
#
# When a pair is promoted to the active universe but its 1m WS subscription
# hasn't caught up (or the stream died and never recovered), the engine
# kept dispatching signals against frozen kline data — producing 5+
# identical SR_FLIP emissions on QUSDT, all closing at the same
# deterministic -0.10358%.  The new ``_is_kline_data_fresh`` gate rejects
# dispatch when the most-recent 1m kline for the symbol is older than
# ``MAX_KLINE_STALENESS_SEC``.


class _FakeDataStoreWithKlineAge:
    """Minimal data store stub exposing the new ``last_kline_age_seconds``
    accessor.  Replaces the MagicMock default which would auto-attr the
    method and return a non-controllable Mock.
    """

    def __init__(self, age_by_key=None) -> None:
        # age_by_key: dict mapping (symbol, interval) -> seconds-since-update
        # (or None to mean "never updated").
        self._ages = age_by_key or {}
        self.candles = {}
        self.ticks = {}

    def last_kline_age_seconds(self, symbol, interval):
        return self._ages.get((symbol, interval))


def _make_scanner_with_kline_age(age_by_key=None):
    queue = MagicMock()

    async def _put(sig):
        return True

    queue.put = _put
    data_store = _FakeDataStoreWithKlineAge(age_by_key)
    return Scanner(
        pair_mgr=MagicMock(),
        data_store=data_store,
        channels=[],
        smc_detector=MagicMock(),
        regime_detector=MagicMock(),
        predictive=MagicMock(),
        exchange_mgr=MagicMock(),
        spot_client=None,
        telemetry=MagicMock(),
        signal_queue=queue,
        router=MagicMock(active_signals={}),
    )


class TestKlineDataStaleness:
    def test_fresh_kline_passes_gate(self):
        """A 30s-old 1m kline is fresh — gate returns True."""
        scanner = _make_scanner_with_kline_age({("BTCUSDT", "1m"): 30.0})
        sig = _make_signal(symbol="BTCUSDT")
        assert scanner._is_kline_data_fresh(sig) is True

    def test_stale_kline_blocks_gate(self):
        """A 600s-old 1m kline is stale — gate returns False (QUSDT bug)."""
        scanner = _make_scanner_with_kline_age({("QUSDT", "1m"): 600.0})
        sig = _make_signal(symbol="QUSDT")
        assert scanner._is_kline_data_fresh(sig) is False

    def test_never_updated_blocks_gate(self):
        """No kline ever recorded for the symbol — block dispatch.

        A pair with zero kline history is by definition not ready for
        trading; the data layer hasn't seen a single candle for it.
        """
        scanner = _make_scanner_with_kline_age({})  # empty age map
        sig = _make_signal(symbol="NEWUSDT")
        assert scanner._is_kline_data_fresh(sig) is False

    def test_no_data_store_attribute_fails_open(self):
        """Data store without the new accessor → fail-open (don't block).

        Protects test harnesses / legacy stubs that pre-date the
        ``last_kline_age_seconds`` API from getting silently broken.
        """

        class _LegacyDataStore:
            candles = {}
            ticks = {}

        scanner = _make_scanner_with_kline_age({})
        scanner.data_store = _LegacyDataStore()
        sig = _make_signal(symbol="BTCUSDT")
        assert scanner._is_kline_data_fresh(sig) is True

    @pytest.mark.asyncio
    async def test_stale_kline_blocks_dispatch_end_to_end(
        self, monkeypatch, _real_staleness_check,
    ):
        """End-to-end: stale kline → ``_enqueue_signal`` returns False and
        the ``data_stale:{setup_class}`` suppression counter increments.
        """
        monkeypatch.setattr(_scanner_mod, "DISPATCH_COOLDOWN_SEC", 0.0)
        scanner = _make_scanner_with_kline_age(
            {("QUSDT", "1m"): 600.0},  # 10 min stale
        )
        sig = _make_signal(symbol="QUSDT", setup_class="SR_FLIP_RETEST")
        ok = await scanner._enqueue_signal(sig)
        assert ok is False
        assert scanner._suppression_counters["data_stale:SR_FLIP_RETEST"] >= 1


# ---------------------------------------------------------------------------
# Bug #5: structure-readiness gate (2026-05-11 path-eligibility by pair age)
# ---------------------------------------------------------------------------
#
# Structure-based evaluators (SR_FLIP / FAR / QCB / TPE / DIV_CONT / CLS /
# PDC / MA_CROSS / STANDARD) need an aged multi-TF level foundation.  When
# the LevelBook has fewer than MIN_1D_LEVELS_FOR_STRUCTURE_PATHS 1d-anchored
# levels for a symbol, those paths get restricted via the
# ``_YOUNG_PAIR_EVALUATORS`` allowlist (breakout-/event-family only).


class _FakeLevelBookForAgeGate:
    """Minimal LevelBook stub exposing only ``stats`` for unit-testing
    ``Scanner._is_pair_structurally_aged``.  Real LevelBook isn't wired
    in lifecycle-test fixtures."""

    def __init__(self, from_1d_by_symbol=None) -> None:
        self._stats = from_1d_by_symbol or {}

    def stats(self, symbol):
        return {"from_1d": self._stats.get(symbol, 0), "total": 0}


def _scanner_with_level_book(from_1d_by_symbol=None) -> Scanner:
    scanner = _make_scanner_for_lifecycle()
    scanner.level_book = _FakeLevelBookForAgeGate(from_1d_by_symbol)
    return scanner


class TestStructureReadinessGate:
    def test_aged_pair_is_eligible(self):
        """Pair with 5+ 1d-anchored levels → structurally aged."""
        scanner = _scanner_with_level_book({"BTCUSDT": 30})
        assert scanner._is_pair_structurally_aged("BTCUSDT") is True

    def test_young_pair_is_blocked(self):
        """Pair with < 5 1d-anchored levels → structurally young."""
        scanner = _scanner_with_level_book({"QUSDT": 2})
        assert scanner._is_pair_structurally_aged("QUSDT") is False

    def test_threshold_boundary(self):
        """Threshold is inclusive at MIN_1D_LEVELS_FOR_STRUCTURE_PATHS."""
        from src.scanner import MIN_1D_LEVELS_FOR_STRUCTURE_PATHS
        at_boundary = MIN_1D_LEVELS_FOR_STRUCTURE_PATHS
        scanner = _scanner_with_level_book({
            "BTCUSDT": at_boundary,
            "QUSDT": at_boundary - 1,
        })
        assert scanner._is_pair_structurally_aged("BTCUSDT") is True
        assert scanner._is_pair_structurally_aged("QUSDT") is False

    def test_unknown_symbol_treated_as_young(self):
        """Pair never seen by LevelBook → from_1d=0 → blocked."""
        scanner = _scanner_with_level_book({})
        assert scanner._is_pair_structurally_aged("UNKNOWNUSDT") is False

    def test_no_level_book_fails_open(self):
        """Scanner without LevelBook → fail-open (don't block).

        Protects unit-test fixtures that pre-date this gate from
        getting silently broken.
        """
        scanner = _make_scanner_for_lifecycle()
        # No `level_book` attr at all.
        if hasattr(scanner, "level_book"):
            delattr(scanner, "level_book")
        assert scanner._is_pair_structurally_aged("BTCUSDT") is True

    def test_young_pair_allowlist_contains_breakout_and_event_family(self):
        """Allowlist covers paths whose thesis doesn't need aged structure."""
        from src.scanner import _YOUNG_PAIR_EVALUATORS
        expected = {
            "_evaluate_volume_surge_breakout",
            "_evaluate_breakdown_short",
            "_evaluate_opening_range_breakout",
            "_evaluate_whale_momentum",
            "_evaluate_liquidation_reversal",
            "_evaluate_funding_extreme",
        }
        assert _YOUNG_PAIR_EVALUATORS == expected
        # Structure-based paths must NOT be in the allowlist.
        for blocked in (
            "_evaluate_sr_flip_retest",
            "_evaluate_failed_auction_reclaim",
            "_evaluate_quiet_compression_break",
            "_evaluate_trend_pullback",
            "_evaluate_divergence_continuation",
            "_evaluate_continuation_liquidity_sweep",
            "_evaluate_post_displacement_continuation",
            "_evaluate_ma_cross_trend_shift",
        ):
            assert blocked not in _YOUNG_PAIR_EVALUATORS


# ---------------------------------------------------------------------------
# Bug #3: limit-order entry-zone fill flag
# ---------------------------------------------------------------------------


class TestEntryZoneFilled:
    def test_default_is_false(self):
        sig = Signal(
            channel="360_SCALP",
            symbol="X",
            direction=Direction.LONG,
            entry=100.0,
            stop_loss=99.0,
            tp1=101.0,
            tp2=102.0,
            confidence=70.0,
        )
        assert sig.entry_zone_filled is False

    def test_field_round_trips(self):
        """Persistence layers serialize/deserialize the new flag."""
        sig = Signal(
            channel="360_SCALP",
            symbol="X",
            direction=Direction.LONG,
            entry=100.0,
            stop_loss=99.0,
            tp1=101.0,
            tp2=102.0,
            confidence=70.0,
        )
        sig.entry_zone_filled = True
        # Manual serialization: dataclass → dict
        from dataclasses import asdict
        d = asdict(sig)
        assert d["entry_zone_filled"] is True


# ---------------------------------------------------------------------------
# Cooldown key construction
# ---------------------------------------------------------------------------


class TestCooldownKey:
    def test_key_for_complete_signal(self):
        sig = _make_signal(symbol="ETHUSDT", setup_class="LSR", direction=Direction.LONG)
        key = Scanner._cooldown_key_for(sig)
        assert key == ("ETHUSDT", "LSR", "LONG")

    def test_key_none_when_missing_symbol(self):
        sig = _make_signal()
        sig.symbol = ""
        assert Scanner._cooldown_key_for(sig) is None

    def test_key_none_when_missing_setup_class(self):
        sig = _make_signal()
        sig.setup_class = ""
        assert Scanner._cooldown_key_for(sig) is None
