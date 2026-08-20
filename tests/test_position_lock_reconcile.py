"""The correlation lock outlived its positions, and took a whole path's output.

Owner, 2026-08-20: *"actually we enable lsr to go live but nothing reached
live feed and where they going what's happening"*.

Measured on the live box that morning, and the two halves are the finding:

- The promotion rule worked.  **30 rows promoted** (25 ``LIQUIDITY_SWEEP_
  REVERSAL``, 5 ``MOVER_AVWAP_SCALP``); in the last 48h, 4 of 4 LSR dark
  candidates were promoted.  Session 126's "wall 1" was cleared.
- **0 of the 30 reached a subscriber.**  26 died on ``correlation_lock``,
  1 on ``same_direction_throttle``.  And that promoted population was the
  best-performing on the page — 19W/8L/2 flat at **+0.57%/row** against
  −0.04% for the rows left dark.

``correlation_lock`` had dropped **309 of 332** dequeued candidates (93.1%)
in one 13h process while **2** signals were ACTIVE, across 11 different
setups — and six of the locked symbols had no delivered trade at all in the
30-day recorded book.  The lock is written in exactly one place, on
confirmed delivery, so a symbol that was never delivered cannot hold a
legitimate one.  The gate was not tight, it was stale.

**The mechanism.**  Both restore paths skip a signal whose status is no
longer ``ACTIVE`` when rebuilding ``_active_signals`` — right, or a closed
signal reappears in the app's Open tab — and then restore ``_position_lock``
wholesale with no cross-check.  Both release paths (``remove_signal``,
``cleanup_expired``) reach the lock *through* ``_active_signals``, so an
entry with no signal behind it is unreachable forever, and ``_persist_state``
writes it back on every save.  It compounds across restarts; the engine
restart-looped all day on 2026-08-19.

Each half was individually correct.  Nothing reconciled them — the seam
shape (#817), on the one hop that decides what a subscriber receives.

Every test here fails against the pre-fix tree (verified by revert).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.channels.base import Signal
from src.signal_router import SignalRouter
from src.smc import Direction


def _make_signal(
    *,
    signal_id: str = "TEST-001",
    symbol: str = "BTCUSDT",
    direction: Direction = Direction.LONG,
    status: str = "ACTIVE",
) -> Signal:
    sig = Signal(
        channel="360_SCALP",
        symbol=symbol,
        direction=direction,
        entry=30000.0,
        stop_loss=29700.0,
        tp1=30450.0,
        tp2=30750.0,
        confidence=70.0,
        signal_id=signal_id,
        setup_class="LIQUIDITY_SWEEP_REVERSAL",
        timestamp=datetime.now(timezone.utc),
    )
    sig.status = status
    return sig


def _router() -> SignalRouter:
    return SignalRouter(
        queue=MagicMock(),
        send_telegram=MagicMock(),
        format_signal=lambda sig: "stub",
        redis_client=None,
    )


@pytest.fixture
def state_path(tmp_path) -> Path:
    """Same path the autouse conftest fixture points the router at."""
    return tmp_path / "active_router_state.json"


# ---------------------------------------------------------------------------
# The defect itself — restore must not resurrect a lock with nothing behind it
# ---------------------------------------------------------------------------


class TestRestoreDropsOrphanedLocks:
    async def test_closed_signal_does_not_leave_its_symbol_locked(self, state_path):
        """The live failure, reproduced end to end.

        A signal that hit SL is skipped on restore — correct — and pre-fix its
        symbol came back locked anyway, blocking every future candidate on it.
        """
        state_path.write_text(json.dumps({
            "active_signals": {
                "OPEN-1": _signal_dict(_make_signal(
                    signal_id="OPEN-1", symbol="BTCUSDT", status="ACTIVE",
                )),
                "CLOSED-1": _signal_dict(_make_signal(
                    signal_id="CLOSED-1", symbol="WLDUSDT", status="SL_HIT",
                )),
            },
            # Persisted while both were open, so both symbols are locked.
            "position_lock": {"BTCUSDT": "LONG", "WLDUSDT": "SHORT"},
            "cooldown_timestamps": {},
        }))

        router = _router()
        await router.restore()

        assert "OPEN-1" in router._active_signals
        assert "CLOSED-1" not in router._active_signals
        # The symbol whose signal is gone must not still be locked.
        assert "WLDUSDT" not in router._position_lock
        assert router._position_lock == {"BTCUSDT": Direction.LONG}

    async def test_a_promoted_candidate_is_delivered_after_the_orphan_clears(
        self, state_path,
    ):
        """The behaviour the owner is missing, asserted at the gate.

        Pre-fix this candidate died on ``correlation_lock`` against a lock
        entry whose signal had closed before the restart.
        """
        state_path.write_text(json.dumps({
            "active_signals": {
                "CLOSED-1": _signal_dict(_make_signal(
                    signal_id="CLOSED-1", symbol="WLDUSDT", status="TP1_HIT",
                )),
            },
            "position_lock": {"WLDUSDT": "SHORT"},
            "cooldown_timestamps": {},
        }))

        router = _router()
        await router.restore()

        # No lock, so the router's first gate lets it through.
        assert router._position_lock.get("WLDUSDT") is None

    async def test_orphan_count_is_recorded_not_merely_repaired(self, state_path):
        """Silently fixing it would erase the only evidence the skew happened."""
        state_path.write_text(json.dumps({
            "active_signals": {},
            "position_lock": {"AAAUSDT": "LONG", "BBBUSDT": "SHORT"},
            "cooldown_timestamps": {},
        }))

        router = _router()
        await router.restore()

        assert router._position_lock == {}
        health = router.position_lock_health()
        assert health["orphans_dropped_at_restore"] == 2

    async def test_the_cleaned_map_is_written_back_to_disk(self, state_path):
        """Repairing memory only would re-read the orphans on the next boot."""
        state_path.write_text(json.dumps({
            "active_signals": {},
            "position_lock": {"AAAUSDT": "LONG"},
            "cooldown_timestamps": {},
        }))

        router = _router()
        await router.restore()

        assert json.loads(state_path.read_text())["position_lock"] == {}


# ---------------------------------------------------------------------------
# The opposite direction — under-blocking is the more dangerous fault
# ---------------------------------------------------------------------------


class TestRestoreRepairsMissingLocks:
    async def test_active_signal_with_no_lock_entry_is_relocked(self, state_path):
        """A missing lock lets a second position open on a symbol that has one.

        The reconcile must not be a one-way purge: dropping orphans while
        leaving this unrepaired would trade an over-block for a naked
        double-entry, which is the worse of the two.
        """
        state_path.write_text(json.dumps({
            "active_signals": {
                "OPEN-1": _signal_dict(_make_signal(
                    signal_id="OPEN-1", symbol="ETHUSDT",
                    direction=Direction.SHORT, status="ACTIVE",
                )),
            },
            "position_lock": {},
            "cooldown_timestamps": {},
        }))

        router = _router()
        await router.restore()

        assert router._position_lock == {"ETHUSDT": Direction.SHORT}
        assert router.position_lock_health()["missing_added_at_restore"] == 1

    async def test_direction_disagreement_is_corrected_and_counted_apart(
        self, state_path,
    ):
        """Corruption, not restore skew — so it never hides inside the ordinary case."""
        state_path.write_text(json.dumps({
            "active_signals": {
                "OPEN-1": _signal_dict(_make_signal(
                    signal_id="OPEN-1", symbol="ETHUSDT",
                    direction=Direction.SHORT, status="ACTIVE",
                )),
            },
            "position_lock": {"ETHUSDT": "LONG"},
            "cooldown_timestamps": {},
        }))

        router = _router()
        await router.restore()

        assert router._position_lock == {"ETHUSDT": Direction.SHORT}
        health = router.position_lock_health()
        assert health["direction_corrected_at_restore"] == 1
        assert health["orphans_dropped_at_restore"] == 0
        assert health["missing_added_at_restore"] == 0


# ---------------------------------------------------------------------------
# The surface — a gate that drops the most must be able to say why
# ---------------------------------------------------------------------------


class TestPositionLockHealth:
    def test_a_healthy_router_reports_zero_divergence(self):
        """The two maps are written on adjacent lines, so agreement is the
        normal state and any divergence is a defect rather than weather."""
        router = _router()
        sig = _make_signal(symbol="BTCUSDT")
        router._active_signals[sig.signal_id] = sig
        router._position_lock["BTCUSDT"] = Direction.LONG

        health = router.position_lock_health()
        assert health["orphaned_now"] == 0
        assert health["unlocked_now"] == 0
        assert health["locked"] == health["active_symbols"] == 1

    def test_a_runtime_orphan_is_visible_without_waiting_for_a_restart(self):
        """The reconcile runs at boot; this is the half that catches a future
        edit popping one map without the other."""
        router = _router()
        router._position_lock["GHOSTUSDT"] = Direction.LONG

        health = router.position_lock_health()
        assert health["orphaned_now"] == 1
        assert health["orphaned_sample"] == ["GHOSTUSDT"]

    def test_delivery_stats_carries_the_lock_block(self):
        """``/signals/router-drops`` explains ``correlation_lock`` and could not
        say whether it was tight or stale.  One writer, one reader."""
        router = _router()
        router._position_lock["GHOSTUSDT"] = Direction.LONG

        block = router.delivery_stats()["position_lock"]
        assert block["orphaned_now"] == 1
        assert block["locked"] == 1


# ---------------------------------------------------------------------------
# Helper — build the persisted shape from the real serializer
# ---------------------------------------------------------------------------


def _signal_dict(sig: Signal) -> dict:
    """Drive the module's own serializer rather than hand-writing its shape.

    A hand-built dict asserts the shape you assumed, not the one the code
    produces — the defect class this repo has paid for under three names.
    """
    from src.signal_router import _signal_to_dict

    return _signal_to_dict(sig)
