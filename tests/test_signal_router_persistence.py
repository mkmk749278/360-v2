"""Tests for SignalRouter active-state persistence with JSON fallback.

Owner reported losing 3-4 in-flight signals per engine restart, with
admin alerts "⚠️ Engine shutting down with N active signal(s).  Please
monitor open positions manually."

Root cause: ``SignalRouter.restore`` and ``_persist_state`` returned
early when Redis was unavailable.  Default deployment topology runs
without Redis (per ``CLAUDE.md``: "Redis is optional. RedisClient +
SignalQueue fall back to in-memory") so every restart silently dropped
``_active_signals`` / ``_position_lock`` / ``_cooldown_timestamps``.

Fix: when Redis is unavailable, persist to / restore from
``data/active_router_state.json`` (path overridable via
``ACTIVE_ROUTER_STATE_PATH`` env var for test isolation).

These tests verify the fallback path end-to-end.  Redis-backed paths are
covered by ``test_signal_router*.py``.
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.channels.base import Signal
from src.signal_router import SignalRouter
from src.smc import Direction


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_signal(
    *,
    signal_id: str = "TEST-001",
    symbol: str = "BTCUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 30000.0,
    setup_class: str = "SR_FLIP_RETEST",
) -> Signal:
    return Signal(
        channel="360_SCALP",
        symbol=symbol,
        direction=direction,
        entry=entry,
        stop_loss=entry * 0.99,
        tp1=entry * 1.015,
        tp2=entry * 1.025,
        confidence=70.0,
        signal_id=signal_id,
        setup_class=setup_class,
        timestamp=datetime.now(timezone.utc),
    )


def _make_router_no_redis() -> SignalRouter:
    """Construct a router without Redis — exercises the JSON fallback path."""
    return SignalRouter(
        queue=MagicMock(),
        send_telegram=MagicMock(),
        format_signal=lambda sig: "stub",
        redis_client=None,
    )


@pytest.fixture
def state_path(tmp_path) -> Path:
    """Per-test path for the JSON fallback ledger.

    The autouse conftest fixture (``_isolate_disk_backed_registries``) sets
    ``ACTIVE_ROUTER_STATE_PATH`` to ``tmp_path / "active_router_state.json"``
    for every test — this fixture just returns that same path so tests can
    assert against the file directly.
    """
    return tmp_path / "active_router_state.json"


# ---------------------------------------------------------------------------
# Persist contract (Redis-less mode)
# ---------------------------------------------------------------------------


class TestPersistJsonFallback:
    async def test_persist_writes_active_signals_to_disk(self, state_path):
        router = _make_router_no_redis()
        sig = _make_signal()
        router._active_signals[sig.signal_id] = sig

        await router._persist_state()

        assert state_path.exists()
        data = json.loads(state_path.read_text())
        assert sig.signal_id in data["active_signals"]
        assert data["active_signals"][sig.signal_id]["symbol"] == "BTCUSDT"
        assert data["active_signals"][sig.signal_id]["direction"] == "LONG"

    async def test_persist_writes_position_lock(self, state_path):
        router = _make_router_no_redis()
        router._position_lock["ETHUSDT"] = Direction.SHORT
        router._position_lock["BTCUSDT"] = Direction.LONG

        await router._persist_state()

        data = json.loads(state_path.read_text())
        assert data["position_lock"] == {
            "ETHUSDT": "SHORT",
            "BTCUSDT": "LONG",
        }

    async def test_persist_writes_cooldown_timestamps(self, state_path):
        router = _make_router_no_redis()
        ts = datetime(2026, 5, 8, 12, 30, 0, tzinfo=timezone.utc)
        router._cooldown_timestamps[("BTCUSDT", "360_SCALP")] = ts

        await router._persist_state()

        data = json.loads(state_path.read_text())
        assert data["cooldown_timestamps"]["BTCUSDT|360_SCALP"] == ts.isoformat()

    async def test_persist_atomic_replace(self, state_path):
        """Tmp + rename so a crash mid-write doesn't leave a torn file."""
        router = _make_router_no_redis()
        # Pre-existing valid file.
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({"active_signals": {"OLD": {}}}))

        sig = _make_signal(signal_id="NEW-001")
        router._active_signals[sig.signal_id] = sig
        await router._persist_state()

        # No leftover .tmp file.
        leftover = state_path.with_suffix(state_path.suffix + ".tmp")
        assert not leftover.exists()
        # New value written, old gone.
        data = json.loads(state_path.read_text())
        assert "NEW-001" in data["active_signals"]
        assert "OLD" not in data["active_signals"]


# ---------------------------------------------------------------------------
# Restore contract
# ---------------------------------------------------------------------------


class TestRestoreJsonFallback:
    async def test_restore_returns_silently_when_file_missing(self, state_path):
        """Clean-slate boot — no errors, just empty state."""
        router = _make_router_no_redis()
        assert not state_path.exists()
        await router.restore()
        assert router._active_signals == {}
        assert router._position_lock == {}
        assert router._cooldown_timestamps == {}

    async def test_restore_loads_active_signals(self, state_path):
        # Write a state file as if the prior process had persisted.
        sig = _make_signal(signal_id="REC-001", symbol="ETHUSDT")
        from src.signal_router import _signal_to_dict
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({
            "active_signals": {"REC-001": _signal_to_dict(sig)},
            "position_lock": {},
            "cooldown_timestamps": {},
        }))

        router = _make_router_no_redis()
        await router.restore()

        assert "REC-001" in router._active_signals
        restored = router._active_signals["REC-001"]
        assert restored.symbol == "ETHUSDT"
        assert restored.direction == Direction.LONG

    async def test_restore_loads_position_lock(self, state_path):
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({
            "active_signals": {},
            "position_lock": {"BTCUSDT": "SHORT", "ETHUSDT": "LONG"},
            "cooldown_timestamps": {},
        }))

        router = _make_router_no_redis()
        await router.restore()

        assert router._position_lock == {
            "BTCUSDT": Direction.SHORT,
            "ETHUSDT": Direction.LONG,
        }

    async def test_restore_loads_cooldown_timestamps(self, state_path):
        ts = datetime(2026, 5, 8, 0, 0, 0, tzinfo=timezone.utc)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({
            "active_signals": {},
            "position_lock": {},
            "cooldown_timestamps": {"SOLUSDT|360_SCALP": ts.isoformat()},
        }))

        router = _make_router_no_redis()
        await router.restore()

        assert router._cooldown_timestamps[("SOLUSDT", "360_SCALP")] == ts

    async def test_restore_handles_corrupt_file(self, state_path):
        """Malformed JSON must not crash the engine boot — fail-soft."""
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text("{{not valid json")

        router = _make_router_no_redis()
        await router.restore()  # must not raise
        assert router._active_signals == {}

    async def test_restore_skips_invalid_direction_in_position_lock(self, state_path):
        """Garbage data in one field doesn't blow up the whole restore."""
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({
            "active_signals": {},
            "position_lock": {"BTCUSDT": "SIDEWAYS"},  # not a valid Direction
            "cooldown_timestamps": {},
        }))

        router = _make_router_no_redis()
        await router.restore()
        assert router._position_lock == {}

    async def test_restore_skips_terminal_status_signals(self, state_path):
        """Owner reported INVALIDATED + SL_HIT signals appearing in the
        app's "Open" tab post-restart.  Root cause: the persistence
        layer captures whatever's in ``_active_signals`` at the moment
        of write, including signals mid-removal during shutdown.

        Restore must skip any signal whose status has already gone
        terminal — those belong in history, not the active map.
        """
        from src.signal_router import _signal_to_dict
        active_sig = _make_signal(signal_id="ACT-1", symbol="ETHUSDT")
        invalidated_sig = _make_signal(signal_id="INV-1", symbol="ZECUSDT")
        sl_hit_sig = _make_signal(signal_id="SL-1", symbol="FLOCKUSDT")
        tp1_hit_sig = _make_signal(signal_id="TP1-1", symbol="BTCUSDT")
        # Stamp terminal statuses on the dict form so the file mirrors
        # the mid-shutdown reality.
        invalidated_dict = _signal_to_dict(invalidated_sig)
        invalidated_dict["status"] = "INVALIDATED"
        sl_hit_dict = _signal_to_dict(sl_hit_sig)
        sl_hit_dict["status"] = "SL_HIT"
        tp1_hit_dict = _signal_to_dict(tp1_hit_sig)
        tp1_hit_dict["status"] = "TP1_HIT"

        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({
            "active_signals": {
                "ACT-1": _signal_to_dict(active_sig),
                "INV-1": invalidated_dict,
                "SL-1": sl_hit_dict,
                "TP1-1": tp1_hit_dict,
            },
            "position_lock": {},
            "cooldown_timestamps": {},
        }))

        router = _make_router_no_redis()
        await router.restore()

        # Only the genuinely-active signal restored; the three terminal
        # ones dropped on the floor.
        assert set(router._active_signals.keys()) == {"ACT-1"}


# ---------------------------------------------------------------------------
# End-to-end: persist then restore on a new instance
# ---------------------------------------------------------------------------


class TestPersistRestoreCycle:
    async def test_signals_survive_router_rebuild(self, state_path):
        """The owner's reported scenario: engine restart with N active
        signals → next boot picks them up exactly."""
        # Session 1: dispatch some signals, persist.
        r1 = _make_router_no_redis()
        for i, sym in enumerate(["BTCUSDT", "ETHUSDT", "SOLUSDT"], start=1):
            sig = _make_signal(signal_id=f"S-{i}", symbol=sym)
            r1._active_signals[sig.signal_id] = sig
        r1._position_lock["BTCUSDT"] = Direction.LONG
        await r1._persist_state()

        # Session 2: brand-new router (mimics engine restart).
        r2 = _make_router_no_redis()
        assert r2._active_signals == {}  # fresh
        await r2.restore()
        assert len(r2._active_signals) == 3
        assert {s.symbol for s in r2._active_signals.values()} == {
            "BTCUSDT", "ETHUSDT", "SOLUSDT",
        }
        assert r2._position_lock == {"BTCUSDT": Direction.LONG}

    async def test_empty_state_round_trip(self, state_path):
        """No active signals → empty file, restore stays empty."""
        r1 = _make_router_no_redis()
        await r1._persist_state()
        # File written but with empty payloads.
        assert state_path.exists()
        data = json.loads(state_path.read_text())
        assert data["active_signals"] == {}

        r2 = _make_router_no_redis()
        await r2.restore()
        assert r2._active_signals == {}
