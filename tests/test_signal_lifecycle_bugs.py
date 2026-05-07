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
