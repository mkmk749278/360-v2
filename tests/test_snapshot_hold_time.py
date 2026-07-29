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


# ---------------------------------------------------------------------------
# original_stop_loss — the pre-BE/trailing protective stop (PR: held-to-stop)
# ---------------------------------------------------------------------------

class _Sig:
    """Minimal explicit signal stand-in (avoids MagicMock's __float__=1.0)."""

    def __init__(self, **kw):
        self.signal_id = "S1"
        self.symbol = "BTCUSDT"
        self.setup_class = "SR_FLIP_RETEST"
        self.timestamp = datetime.now(timezone.utc)
        self.dispatch_timestamp = None
        self.terminal_outcome_timestamp = None
        self.status = "ACTIVE"
        self.tp1 = self.tp2 = 0.0
        self.tp3 = None
        self.confidence = 70.0
        self.quality_tier = "A"
        self.current_price = 0.0
        self.pnl_pct = 0.0
        self.max_favorable_excursion_pct = 0.0
        self.max_adverse_excursion_pct = 0.0
        self.__dict__.update(kw)


class TestOriginalStopLoss:
    def test_long_reconstructs_original_below_entry_after_be_shift(self):
        # TP1/BE shifted the live stop up to entry; original was 2.0 below.
        sig = _Sig(direction="LONG", entry=100.0, stop_loss=100.0,
                   original_sl_distance=2.0, status="PROFIT_LOCKED")
        d = _signal_to_detail(sig)
        assert d.stop_loss == 100.0            # live (shifted) stop unchanged
        assert d.original_stop_loss == 98.0    # original protective stop

    def test_short_reconstructs_original_above_entry(self):
        sig = _Sig(direction="SHORT", entry=100.0, stop_loss=100.0,
                   original_sl_distance=1.5, status="PROFIT_LOCKED")
        assert _signal_to_detail(sig).original_stop_loss == 101.5

    def test_falls_back_to_current_stop_when_distance_unrecorded(self):
        sig = _Sig(direction="LONG", entry=50.0, stop_loss=49.5,
                   original_sl_distance=0.0)
        assert _signal_to_detail(sig).original_stop_loss == 49.5

    def test_untouched_stop_round_trips(self):
        # Active signal never shifted: original == live stop.
        sig = _Sig(direction="LONG", entry=100.0, stop_loss=98.0,
                   original_sl_distance=2.0)
        d = _signal_to_detail(sig)
        assert d.stop_loss == d.original_stop_loss == 98.0


# ---------------------------------------------------------------------------
# Lifecycle instants — the cross-repo contract the Lumin chart plots on
# ---------------------------------------------------------------------------

class TestLifecycleInstantsArePublished:
    """``SignalDetail`` must carry the instants, not just the "N ago" label.

    The Lumin chart had no entry timestamp to draw on — ``_signalFromJson``
    read ``minutes_ago`` and dropped ``timestamp`` — so it reconstructed one as
    ``now - minutes_ago`` and captioned the result ENTRY.  For a closed signal
    ``minutes_ago`` measures from the *terminal* event, so the arrow landed on
    the exit, offset by the entire hold time: COTIUSDT stamped 03:00:33 UTC
    rendered at 04:05, sitting exactly on its own SL line (owner-caught
    2026-07-29).

    These field names are a cross-repo contract (CLAUDE.md).  Pinned here, on
    the producing side, so a rename fails loudly instead of quietly moving the
    app's markers back to a fabricated time.
    """

    def test_closed_signal_publishes_both_instants(self):
        sig = _make_sig(
            status="SL_HIT",
            created_offset_mins=125,
            dispatch_offset_mins=124,
            terminal_offset_mins=60,
        )
        d = _signal_to_detail(sig)
        assert d.dispatch_timestamp == sig.dispatch_timestamp
        assert d.terminal_outcome_timestamp == sig.terminal_outcome_timestamp

    def test_the_entry_instant_is_not_recoverable_from_minutes_ago(self):
        """The regression itself, stated as arithmetic.

        A consumer doing ``now - minutes_ago`` lands on the exit; the same
        consumer reading ``timestamp`` lands on the entry.  If this assertion
        ever flips, the app's ENTRY marker is back on the exit.
        """
        sig = _make_sig(
            status="SL_HIT",
            created_offset_mins=125,   # entry
            dispatch_offset_mins=124,
            terminal_offset_mins=60,   # exit, 65 minutes later
        )
        d = _signal_to_detail(sig)
        now = datetime.now(timezone.utc)

        reconstructed = now - timedelta(minutes=d.minutes_ago)
        # What the old app drew: the exit, ~65 minutes past the real entry.
        assert abs((reconstructed - sig.terminal_outcome_timestamp).total_seconds()) < 90
        assert (reconstructed - d.timestamp).total_seconds() > 60 * 60

        # What it can draw now: the entry itself.
        assert abs((d.timestamp - sig.timestamp).total_seconds()) < 1

    def test_open_signal_has_no_terminal_instant(self):
        """Absent because there is no exit — not because we failed to read one."""
        sig = _make_sig(status="ACTIVE", terminal_offset_mins=None)
        d = _signal_to_detail(sig)
        assert d.terminal_outcome_timestamp is None
        assert d.dispatch_timestamp == sig.dispatch_timestamp

    def test_terminal_instant_withheld_when_status_is_not_terminal(self):
        # A stray stamp on a still-open signal must not publish an exit the
        # chart would then draw.  Status is the authority.
        sig = _make_sig(status="ACTIVE", terminal_offset_mins=10)
        assert _signal_to_detail(sig).terminal_outcome_timestamp is None

    def test_iso_string_stamps_are_parsed(self):
        # The Firestore-round-trip shape _minutes_since was already hardened for.
        sig = _make_sig(status="SL_HIT", terminal_offset_mins=30)
        sig.dispatch_timestamp = "2026-07-29T05:31:03Z"
        sig.terminal_outcome_timestamp = "2026-07-29T05:37:00+00:00"
        d = _signal_to_detail(sig)
        assert d.dispatch_timestamp == datetime(2026, 7, 29, 5, 31, 3, tzinfo=timezone.utc)
        assert d.terminal_outcome_timestamp == datetime(2026, 7, 29, 5, 37, tzinfo=timezone.utc)

    def test_unreadable_stamp_refuses_rather_than_guesses(self):
        # Refuse, don't clamp: an unparseable stamp yields no instant, so the
        # consumer omits its marker instead of drawing one at epoch or at now.
        sig = _make_sig(status="SL_HIT", terminal_offset_mins=30)
        sig.dispatch_timestamp = "not-a-date"
        sig.terminal_outcome_timestamp = "not-a-date"
        d = _signal_to_detail(sig)
        assert d.dispatch_timestamp is None
        assert d.terminal_outcome_timestamp is None

    def test_naive_stamps_are_returned_utc_aware(self):
        # A naive stamp compared against a tz-aware one raises; the app would
        # see a 500 instead of a chart.
        sig = _make_sig(status="SL_HIT", terminal_offset_mins=30)
        sig.terminal_outcome_timestamp = datetime(2026, 7, 29, 4, 5, 0)
        d = _signal_to_detail(sig)
        assert d.terminal_outcome_timestamp is not None
        assert d.terminal_outcome_timestamp.tzinfo is not None

    def test_creation_stamp_is_published_tz_aware(self):
        """A naive stamp serialises without a zone and parses as *local* time.

        On an IST phone that is 5h30m of silent error, on the one field the
        chart anchors its entry marker to — a worse version of the bug being
        fixed.  Normalise at the producer.
        """
        sig = _make_sig(status="ACTIVE")
        sig.timestamp = datetime(2026, 7, 29, 6, 20, 21)  # naive, as stored
        d = _signal_to_detail(sig)
        assert d.timestamp.tzinfo is not None
        assert d.timestamp == datetime(2026, 7, 29, 6, 20, 21, tzinfo=timezone.utc)
