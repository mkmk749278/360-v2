"""Tests for _signal_to_detail hold-time and minutes_ago fixes.

Regression suite for the "time display" bug where:
  - Active signals showed age since signal creation, not since dispatch.
  - Closed signals showed ever-growing age since creation, not terminal
    recency ("SL_HIT 3m ago") and had no hold duration.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

import pytest

from src.api.snapshot import _signal_to_detail, _hold_mins


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sig(
    *,
    status: str = "ACTIVE",
    created_offset_mins: int = 30,
    dispatch_offset_mins: int | None = 25,
    terminal_offset_mins: int | None = None,
) -> MagicMock:
    """Build a mock Signal with realistic timestamps."""
    now = datetime.now(timezone.utc)
    sig = MagicMock()
    sig.signal_id = "SIG-TEST-001"
    sig.symbol = "BTCUSDT"
    sig.direction = MagicMock(value="LONG")
    sig.setup_class = "SR_FLIP_RETEST"
    sig.timestamp = now - timedelta(minutes=created_offset_mins)
    sig.dispatch_timestamp = (
        now - timedelta(minutes=dispatch_offset_mins)
        if dispatch_offset_mins is not None
        else None
    )
    sig.terminal_outcome_timestamp = (
        now - timedelta(minutes=terminal_offset_mins)
        if terminal_offset_mins is not None
        else None
    )
    sig.status = status
    sig.entry = 50000.0
    sig.stop_loss = 49000.0
    sig.tp1 = 51000.0
    sig.tp2 = 52000.0
    sig.tp3 = None
    sig.confidence = 72.0
    sig.quality_tier = "A"
    sig.current_price = 50100.0
    sig.pnl_pct = 0.20
    sig.max_favorable_excursion_pct = 0.40
    sig.max_adverse_excursion_pct = -0.10
    sig.pre_tp_hit = False
    sig.pre_tp_threshold_pct = 0.0
    sig.pre_tp_trigger_price = None
    return sig


# ---------------------------------------------------------------------------
# _hold_mins pure function
# ---------------------------------------------------------------------------

class TestHoldMins:
    def test_none_dispatch_returns_none(self):
        assert _hold_mins(None, None) is None

    def test_active_uses_now(self):
        dispatch = datetime.now(timezone.utc) - timedelta(minutes=15)
        result = _hold_mins(dispatch, None)
        assert result is not None
        assert 14 <= result <= 16

    def test_closed_uses_terminal(self):
        now = datetime.now(timezone.utc)
        dispatch = now - timedelta(minutes=30)
        terminal = now - timedelta(minutes=10)
        result = _hold_mins(dispatch, terminal)
        assert result == 20

    def test_string_dispatch_parsed(self):
        now = datetime.now(timezone.utc)
        dispatch_str = (now - timedelta(minutes=20)).isoformat()
        result = _hold_mins(dispatch_str, None)
        assert result is not None
        assert 19 <= result <= 21

    def test_invalid_dispatch_returns_none(self):
        assert _hold_mins("not-a-date", None) is None

    def test_zero_hold_clamped_to_zero(self):
        now = datetime.now(timezone.utc)
        result = _hold_mins(now + timedelta(minutes=1), now)
        assert result == 0


# ---------------------------------------------------------------------------
# _signal_to_detail: minutes_ago
# ---------------------------------------------------------------------------

class TestSignalToDetailMinutesAgo:
    def test_active_signal_minutes_ago_uses_dispatch(self):
        """Active: minutes_ago ≈ minutes since dispatch, not since creation."""
        sig = _make_sig(
            status="ACTIVE",
            created_offset_mins=30,
            dispatch_offset_mins=20,
        )
        detail = _signal_to_detail(sig)
        # Should be ~20 (dispatch), not ~30 (creation)
        assert 19 <= detail.minutes_ago <= 21

    def test_active_signal_no_dispatch_falls_back_to_creation(self):
        """Active without dispatch_timestamp: fall back to creation time."""
        sig = _make_sig(
            status="ACTIVE",
            created_offset_mins=25,
            dispatch_offset_mins=None,
        )
        detail = _signal_to_detail(sig)
        assert 24 <= detail.minutes_ago <= 26

    def test_closed_signal_minutes_ago_uses_terminal(self):
        """Closed: minutes_ago = how long ago the terminal event happened."""
        sig = _make_sig(
            status="SL_HIT",
            created_offset_mins=40,
            dispatch_offset_mins=35,
            terminal_offset_mins=5,
        )
        detail = _signal_to_detail(sig)
        # Should be ~5 (terminal recency), not ~40 (creation age)
        assert 4 <= detail.minutes_ago <= 6

    def test_closed_no_terminal_ts_falls_back_to_dispatch(self):
        """Closed status but no terminal timestamp: use dispatch."""
        sig = _make_sig(
            status="INVALIDATED",
            created_offset_mins=30,
            dispatch_offset_mins=20,
            terminal_offset_mins=None,
        )
        detail = _signal_to_detail(sig)
        assert 19 <= detail.minutes_ago <= 21

    def test_all_terminal_statuses_use_terminal_ts(self):
        terminal_statuses = [
            "SL_HIT", "BREAKEVEN_EXIT", "PROFIT_LOCKED", "INVALIDATED",
            "EXPIRED", "CANCELLED", "FULL_TP_HIT", "TP3_HIT", "CLOSED",
        ]
        for status in terminal_statuses:
            sig = _make_sig(
                status=status,
                created_offset_mins=60,
                dispatch_offset_mins=50,
                terminal_offset_mins=3,
            )
            detail = _signal_to_detail(sig)
            assert 2 <= detail.minutes_ago <= 4, (
                f"{status}: minutes_ago={detail.minutes_ago} should be ~3"
            )


# ---------------------------------------------------------------------------
# _signal_to_detail: hold_mins
# ---------------------------------------------------------------------------

class TestSignalToDetailHoldMins:
    def test_active_hold_mins_equals_time_since_dispatch(self):
        sig = _make_sig(
            status="ACTIVE",
            created_offset_mins=30,
            dispatch_offset_mins=18,
        )
        detail = _signal_to_detail(sig)
        assert detail.hold_mins is not None
        assert 17 <= detail.hold_mins <= 19

    def test_closed_hold_mins_is_dispatch_to_terminal(self):
        """For SL_HIT: hold_mins = terminal - dispatch (the actual trade duration)."""
        # Dispatched 30m ago, SL hit 5m ago → held for 25 minutes
        sig = _make_sig(
            status="SL_HIT",
            created_offset_mins=40,
            dispatch_offset_mins=30,
            terminal_offset_mins=5,
        )
        detail = _signal_to_detail(sig)
        assert detail.hold_mins is not None
        assert 24 <= detail.hold_mins <= 26

    def test_no_dispatch_ts_hold_mins_is_none(self):
        sig = _make_sig(
            status="ACTIVE",
            dispatch_offset_mins=None,
        )
        detail = _signal_to_detail(sig)
        assert detail.hold_mins is None

    def test_hold_mins_present_on_all_terminal_statuses(self):
        for status in ("SL_HIT", "EXPIRED", "FULL_TP_HIT", "INVALIDATED"):
            sig = _make_sig(
                status=status,
                dispatch_offset_mins=20,
                terminal_offset_mins=5,
            )
            detail = _signal_to_detail(sig)
            assert detail.hold_mins is not None, f"{status} should have hold_mins"
            assert detail.hold_mins == 15

    def test_hold_mins_not_affected_by_creation_time(self):
        """hold_mins is dispatch→terminal, never creation→terminal."""
        # Created 60m ago, dispatched 10m ago, closed 2m ago → hold = 8, NOT 58
        sig = _make_sig(
            status="SL_HIT",
            created_offset_mins=60,
            dispatch_offset_mins=10,
            terminal_offset_mins=2,
        )
        detail = _signal_to_detail(sig)
        assert detail.hold_mins is not None
        assert 7 <= detail.hold_mins <= 9, (
            f"hold_mins={detail.hold_mins} should be ~8 (dispatch→terminal), not ~58"
        )
