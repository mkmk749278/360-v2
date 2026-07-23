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


# Capture the production level-rearm methods at module import — BEFORE the
# autouse conftest fixture replaces them with no-ops.  TestLevelRearmStateMachine
# uses these references via the ``_real_level_rearm`` fixture to opt back in.
_REAL_IS_LEVEL_IN_PLAY = Scanner._is_level_in_play
_REAL_RECORD_LEVEL_IN_PLAY = Scanner._record_level_in_play


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
        monkeypatch.setattr(
            Scanner, "_is_entry_fresh", lambda self, sig, current_price=None: True
        )
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
        monkeypatch.setattr(
            Scanner, "_is_entry_fresh", lambda self, sig, current_price=None: True
        )
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
        monkeypatch.setattr(
            Scanner, "_is_entry_fresh", lambda self, sig, current_price=None: True
        )
        scanner = _make_scanner_for_lifecycle()
        await scanner._enqueue_signal(_make_signal(symbol="BTCUSDT"))
        ok = await scanner._enqueue_signal(_make_signal(symbol="ETHUSDT"))
        assert ok is True

    @pytest.mark.asyncio
    async def test_different_direction_not_blocked(self, monkeypatch):
        monkeypatch.setattr(_scanner_mod, "DISPATCH_COOLDOWN_SEC", 1800.0)
        monkeypatch.setattr(
            Scanner, "_is_entry_fresh", lambda self, sig, current_price=None: True
        )
        scanner = _make_scanner_for_lifecycle()
        await scanner._enqueue_signal(_make_signal(direction=Direction.LONG))
        ok = await scanner._enqueue_signal(_make_signal(direction=Direction.SHORT))
        assert ok is True

    @pytest.mark.asyncio
    async def test_different_setup_class_not_blocked(self, monkeypatch):
        monkeypatch.setattr(_scanner_mod, "DISPATCH_COOLDOWN_SEC", 1800.0)
        monkeypatch.setattr(
            Scanner, "_is_entry_fresh", lambda self, sig, current_price=None: True
        )
        scanner = _make_scanner_for_lifecycle()
        await scanner._enqueue_signal(_make_signal(setup_class="FAILED_AUCTION_RECLAIM"))
        ok = await scanner._enqueue_signal(_make_signal(setup_class="SR_FLIP_RETEST"))
        assert ok is True

    @pytest.mark.asyncio
    async def test_after_cooldown_elapses_re_fires(self, monkeypatch):
        monkeypatch.setattr(_scanner_mod, "DISPATCH_COOLDOWN_SEC", 1800.0)
        monkeypatch.setattr(
            Scanner, "_is_entry_fresh", lambda self, sig, current_price=None: True
        )
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


def _real_is_entry_fresh(self, sig, current_price=None):
    """Inlined copy of the production Scanner._is_entry_fresh logic so
    the staleness tests can run the real algorithm without disturbing
    other conftest monkeypatches (no module reload here).  Accepts (and
    ignores) the ``current_price`` short-circuit the production signature
    grew for the V2 shadow evaluation — this copy always re-derives the
    price from the store, which is the behaviour under test."""
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

    def test_never_updated_fails_open(self):
        """No kline timestamp stamped yet — fail-OPEN (post-boot pattern).

        After every engine restart there's a window where the seed
        path has loaded candles into the store via REST but no live
        ``update_candle`` call from a WS frame has stamped
        ``_last_kline_update_ts`` yet.  Blocking dispatch during
        that window kept the engine completely silent for ~15 minutes
        after each restart (2026-05-12 — the WS subscription returned
        zero frames until the watchdog force-closed at 903s, and the
        data-staleness gate killed every dispatch attempt in the
        meantime).  Matches the fail-open doctrine used by
        ``_is_pair_structurally_aged`` on missing accessor.

        The QUSDT-class frozen-feed pathology PR #359 was designed to
        catch is still detected via the
        ``age > MAX_KLINE_STALENESS_SEC`` branch once a single live
        frame has been observed.
        """
        scanner = _make_scanner_with_kline_age({})  # empty age map
        sig = _make_signal(symbol="NEWUSDT")
        assert scanner._is_kline_data_fresh(sig) is True

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
            # Mover continuation — price-driven (MA stack), young-pair-safe.
            "_evaluate_mover_trend_pullback",
            # Anchored-VWAP mover scalp — same, young-pair-safe.
            "_evaluate_mover_avwap_scalp",
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


# ---------------------------------------------------------------------------
# Bug #6: level-rearm state machine (2026-05-13 stuck-level repeat-fire)
# ---------------------------------------------------------------------------
#
# Level-anchored evaluators (SR_FLIP_RETEST / VSB / BDS / FAR) anchor signal
# `entry` to a historical structural level.  When price chops within the
# retest zone for hours, the detector keeps re-finding the same level and
# the dispatch cooldown only spaces out the refires.  Bug data: ETHUSDT
# SR_FLIP SHORT dispatched 13× over 26h at identical entry 2305.32, every
# dispatch expired at +0.11% MFE.  Fix: per-(symbol, direction,
# level_bucket) "in-play" registry that blocks additional dispatches at the
# same level until price has travelled the SL-distance-derived excursion
# threshold (LEVEL_REARM_SL_MULTIPLIER × SL distance, clamped to floor /
# ceiling).  Re-arms automatically on genuine excursion so the next real
# retest fires normally.


def _make_scanner_with_candle(symbol: str, current_close: float) -> Scanner:
    """Bare scanner with `data_store.candles[symbol]["1m"]` seeded so the
    level-excursion tick can read a current price."""
    queue = MagicMock()

    async def _put(sig):
        return True

    queue.put = _put

    data_store = MagicMock()
    data_store.candles = {
        symbol: {
            "1m": {
                "close": np.array([current_close - 0.5, current_close]),
                "high": np.array([current_close + 0.1, current_close + 0.1]),
                "low": np.array([current_close - 0.6, current_close - 0.05]),
            }
        }
    }

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


@pytest.fixture
def _real_level_rearm(monkeypatch):
    """Restore the production ``_is_level_in_play`` and
    ``_record_level_in_play`` methods (captured at module import, before
    the autouse conftest fixture no-ops them).  TestLevelRearmStateMachine
    opts back into the real behaviour so unrelated tests dispatching the
    same entry repeatedly don't trip the gate.

    Also re-pins ``_is_entry_fresh`` to always-True: the level-rearm
    tests simulate price moving 1-2% past the level to verify re-arm
    semantics, but that same movement would otherwise trip the
    ``DISPATCH_STALENESS_MAX_DRIFT_PCT`` gate (0.5% default).  The
    conftest patches ``_is_entry_fresh`` to True by default but the
    patch is sometimes lost across module reloads driven by other
    tests (e.g. ``test_pr04_portfolio_governance.py`` reloads
    ``src.scanner`` mid-suite, leaving stale class references on the
    test module).  Pinning it here makes the test contract explicit
    and reload-safe.
    """
    monkeypatch.setattr(Scanner, "_is_level_in_play", _REAL_IS_LEVEL_IN_PLAY)
    monkeypatch.setattr(Scanner, "_record_level_in_play", _REAL_RECORD_LEVEL_IN_PLAY)
    monkeypatch.setattr(
            Scanner, "_is_entry_fresh", lambda self, sig, current_price=None: True
        )
    yield


@pytest.mark.usefixtures("_real_level_rearm")
class TestLevelRearmStateMachine:
    def test_threshold_derived_from_sl_distance(self):
        """Threshold = clamp(SL_MULT × sl_distance%, floor, ceiling).
        At default SL_MULT=1.5: a 0.8% SL → 1.2% threshold.
        """
        threshold = Scanner._compute_rearm_threshold_pct(
            entry=100.0, stop_loss=100.8,
        )
        assert abs(threshold - 0.012) < 1e-6

    def test_threshold_clamped_to_floor(self):
        """A tiny SL distance (0.1%) clamps to the floor (0.5% default)."""
        threshold = Scanner._compute_rearm_threshold_pct(
            entry=100.0, stop_loss=100.1,
        )
        assert abs(threshold - 0.005) < 1e-6

    def test_threshold_clamped_to_ceiling(self):
        """A huge SL distance (5%) clamps to the ceiling (3% default)."""
        threshold = Scanner._compute_rearm_threshold_pct(
            entry=100.0, stop_loss=105.0,
        )
        assert abs(threshold - 0.030) < 1e-6

    def test_threshold_fallback_on_missing_sl(self):
        """No stop_loss → fallback %."""
        threshold = Scanner._compute_rearm_threshold_pct(
            entry=100.0, stop_loss=0.0,
        )
        assert threshold > 0  # uses LEVEL_REARM_FALLBACK_PCT

    @pytest.mark.asyncio
    async def test_first_dispatch_records_state(self):
        """First dispatch at a fresh level → enqueue ok, registry has the entry."""
        scanner = _make_scanner_with_candle("ETHUSDT", 2305.32)
        sig = _make_signal(
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        ok = await scanner._enqueue_signal(sig)
        assert ok is True
        # Registry now contains the level.
        key, state = scanner._find_matching_level(sig)
        assert state is not None
        assert state.level_price == 2305.32

    @pytest.mark.asyncio
    async def test_second_dispatch_same_level_blocked(self):
        """Same entry, same direction, before price moves → rejected with counter."""
        scanner = _make_scanner_with_candle("ETHUSDT", 2305.32)
        sig1 = _make_signal(
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        sig2 = _make_signal(
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        assert await scanner._enqueue_signal(sig1) is True
        # Price still hugging the level — no excursion since dispatch.
        ok = await scanner._enqueue_signal(sig2)
        assert ok is False
        assert scanner._suppression_counters[
            "enqueue_stage:level_still_in_play:SR_FLIP_RETEST"
        ] >= 1

    @pytest.mark.asyncio
    async def test_excursion_crossing_threshold_rearms(self):
        """Price moves >= threshold away from the level → entry dropped, next dispatch passes."""
        scanner = _make_scanner_with_candle("ETHUSDT", 2305.32)
        sig1 = _make_signal(
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        assert await scanner._enqueue_signal(sig1) is True
        # Simulate price moving 2% away (well above the 1.2% threshold for
        # this signal — 0.8% SL × 1.5 = 1.2%).
        scanner.data_store.candles["ETHUSDT"]["1m"]["close"] = np.array(
            [2305.32, 2305.32 * 1.02]
        )
        sig2 = _make_signal(
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        ok = await scanner._enqueue_signal(sig2)
        # Tick during the gate check observed the excursion and dropped
        # the entry, so this dispatch goes through.
        assert ok is True

    @pytest.mark.asyncio
    async def test_ttl_expiry_rearms(self, monkeypatch):
        """24h since dispatch with no excursion → entry dropped (TTL safety net)."""
        scanner = _make_scanner_with_candle("ETHUSDT", 2305.32)
        sig1 = _make_signal(
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        assert await scanner._enqueue_signal(sig1) is True
        # Move dispatched_at into the past beyond TTL.
        key, state = scanner._find_matching_level(sig1)
        state.dispatched_at = time.time() - (24 * 3600 + 60)
        # Next dispatch passes — TTL drop fires in _tick_level_state.
        sig2 = _make_signal(
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        ok = await scanner._enqueue_signal(sig2)
        assert ok is True

    @pytest.mark.asyncio
    async def test_opposite_direction_same_level_allowed(self):
        """Same level, opposite direction → different key, dispatch allowed.
        A short rejection at L and a long bounce at L are different setups."""
        scanner = _make_scanner_with_candle("ETHUSDT", 2305.32)
        sig_short = _make_signal(
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        sig_long = _make_signal(
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.LONG,
            entry=2305.32, stop_loss=2286.88,
        )
        assert await scanner._enqueue_signal(sig_short) is True
        # Same level but LONG side — different key, allowed.
        assert await scanner._enqueue_signal(sig_long) is True

    @pytest.mark.asyncio
    async def test_different_symbol_same_level_allowed(self):
        """ETH @ 2305.32 SHORT in play does not block BTC @ 2305.32 SHORT
        (different symbol → different key)."""
        scanner = _make_scanner_with_candle("ETHUSDT", 2305.32)
        # Also seed BTC candles so _is_entry_fresh / excursion check have data
        # (the helper only seeds the first symbol).
        scanner.data_store.candles["BTCUSDT"] = scanner.data_store.candles["ETHUSDT"]
        sig_eth = _make_signal(
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        sig_btc = _make_signal(
            symbol="BTCUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        assert await scanner._enqueue_signal(sig_eth) is True
        assert await scanner._enqueue_signal(sig_btc) is True

    @pytest.mark.asyncio
    async def test_cross_evaluator_dedup_on_same_level(self):
        """If SR_FLIP dispatched at 2305.32 SHORT, then VSB detects the
        same level later — VSB should also be blocked.  The state machine
        keys on (symbol, direction, level_bucket) NOT setup_class, because
        chop is chop regardless of which detector spotted it.
        """
        scanner = _make_scanner_with_candle("ETHUSDT", 2305.32)
        sig_sr_flip = _make_signal(
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        sig_bds = _make_signal(
            symbol="ETHUSDT", setup_class="BREAKDOWN_SHORT",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        assert await scanner._enqueue_signal(sig_sr_flip) is True
        ok = await scanner._enqueue_signal(sig_bds)
        assert ok is False
        assert scanner._suppression_counters[
            "enqueue_stage:level_still_in_play:BREAKDOWN_SHORT"
        ] >= 1

    @pytest.mark.asyncio
    async def test_chop_then_real_move_then_dispatch_integration(self):
        """End-to-end: dispatch at level → 4 chop attempts blocked →
        real move past threshold → next attempt succeeds.  Models the
        ETH 2026-05-13 pattern."""
        scanner = _make_scanner_with_candle("ETHUSDT", 2305.32)
        base_sig = lambda: _make_signal(  # noqa: E731
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        # 1) First dispatch at the fresh level — passes.
        assert await scanner._enqueue_signal(base_sig()) is True
        # 2-5) Chop dispatches at the same level — all blocked.
        for _ in range(4):
            scanner.data_store.candles["ETHUSDT"]["1m"]["close"] = np.array(
                [2305.32, 2305.32 * 1.002]  # ~0.2% wobble, well under threshold
            )
            assert await scanner._enqueue_signal(base_sig()) is False
        # 6) Real move ~2% past the level → next attempt re-arms and dispatches.
        scanner.data_store.candles["ETHUSDT"]["1m"]["close"] = np.array(
            [2305.32, 2305.32 * 1.02]
        )
        assert await scanner._enqueue_signal(base_sig()) is True

    @pytest.mark.asyncio
    async def test_near_bucket_levels_treated_as_same(self):
        """2305.32 vs 2305.33 differ by ~0.4 bps — well inside the 5 bps
        default tolerance.  After dispatching at 2305.32, an attempt at
        2305.33 must be blocked even if the exact bucket key differs
        (the slow-path tolerance scan in ``_find_matching_level`` is the
        real same-level enforcement)."""
        scanner = _make_scanner_with_candle("ETHUSDT", 2305.32)
        sig1 = _make_signal(
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.32, stop_loss=2323.76,
        )
        sig2 = _make_signal(
            symbol="ETHUSDT", setup_class="SR_FLIP_RETEST",
            direction=Direction.SHORT,
            entry=2305.33,  # ~0.4 bps drift — clustering noise
            stop_loss=2323.76,
        )
        assert await scanner._enqueue_signal(sig1) is True
        ok = await scanner._enqueue_signal(sig2)
        assert ok is False
        assert scanner._suppression_counters[
            "enqueue_stage:level_still_in_play:SR_FLIP_RETEST"
        ] >= 1
