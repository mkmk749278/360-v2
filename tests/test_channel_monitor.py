"""Tests for channel_monitor.py – multi-channel signal monitoring."""

from __future__ import annotations

import time

import pytest

from src.channel_monitor import (
    ChannelMonitor,
    ChannelSnapshot,
    ChannelStatus,
    ConflictRecord,
    InfraHealth,
    MonitorDiagnostic,
    SignalEvent,
    MONITORED_CHANNELS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_event(
    channel: str = "360_SCALP",
    symbol: str = "BTCUSDT",
    direction: str = "LONG",
    confidence: float = 80.0,
    entry: float = 65000.0,
    tp1: float = 66000.0,
    stop_loss: float = 64000.0,
    signal_id: str = "",
    latency_ms: float = 50.0,
    quality_tier: str = "A",
    **kwargs,
) -> SignalEvent:
    return SignalEvent(
        channel=channel,
        symbol=symbol,
        direction=direction,
        confidence=confidence,
        entry=entry,
        tp1=tp1,
        stop_loss=stop_loss,
        signal_id=signal_id or f"sig-{time.monotonic()}",
        latency_ms=latency_ms,
        quality_tier=quality_tier,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# SignalEvent dataclass
# ---------------------------------------------------------------------------

class TestSignalEvent:
    def test_defaults(self):
        e = SignalEvent(
            channel="360_SCALP",
            symbol="ETHUSDT",
            direction="SHORT",
            confidence=70.0,
            entry=3000.0,
            tp1=2900.0,
            stop_loss=3100.0,
        )
        assert e.status == "OK"
        assert e.latency_ms == 0.0
        assert e.timestamp > 0

    def test_custom_fields(self):
        e = _make_event(signal_id="abc-123", quality_tier="A+")
        assert e.signal_id == "abc-123"
        assert e.quality_tier == "A+"


# ---------------------------------------------------------------------------
# ChannelMonitor – basic signal recording
# ---------------------------------------------------------------------------

class TestChannelMonitorBasic:
    def test_record_signal_ok(self):
        mon = ChannelMonitor()
        e = _make_event()
        result = mon.record_signal(e)
        assert result.status == "OK"

    def test_snapshot_after_signal(self):
        mon = ChannelMonitor()
        mon.record_signal(_make_event())
        snap = mon.get_channel_snapshot("360_SCALP")
        assert snap.signal_count == 1
        assert snap.status == ChannelStatus.ACTIVE
        assert snap.avg_confidence == 80.0

    def test_multiple_signals_avg(self):
        mon = ChannelMonitor()
        mon.record_signal(_make_event(confidence=60.0))
        mon.record_signal(_make_event(confidence=80.0, signal_id="sig-2"))
        snap = mon.get_channel_snapshot("360_SCALP")
        assert snap.signal_count == 2
        assert snap.avg_confidence == pytest.approx(70.0)

    def test_latency_avg(self):
        mon = ChannelMonitor()
        mon.record_signal(_make_event(latency_ms=100))
        mon.record_signal(_make_event(latency_ms=200, signal_id="sig-b"))
        snap = mon.get_channel_snapshot("360_SCALP")
        assert snap.avg_latency_ms == pytest.approx(150.0)

    def test_unregistered_channel_accepted(self):
        mon = ChannelMonitor()
        e = _make_event(channel="CUSTOM_CHANNEL")
        result = mon.record_signal(e)
        assert result.status == "OK"
        snap = mon.get_channel_snapshot("CUSTOM_CHANNEL")
        assert snap.signal_count == 1


# ---------------------------------------------------------------------------
# Inactive channel detection
# ---------------------------------------------------------------------------

class TestInactiveDetection:
    def test_no_signals_means_inactive(self):
        mon = ChannelMonitor(inactive_threshold_s=0.01)
        inactive = mon.get_inactive_channels()
        assert len(inactive) == len(MONITORED_CHANNELS)

    def test_active_after_signal(self):
        mon = ChannelMonitor(inactive_threshold_s=600)
        mon.record_signal(_make_event(channel="360_SCALP"))
        snap = mon.get_channel_snapshot("360_SCALP")
        assert snap.status == ChannelStatus.ACTIVE
        # Other channels remain inactive.
        assert "360_SCALP_FVG" in mon.get_inactive_channels()

    def test_inactive_after_threshold(self):
        mon = ChannelMonitor(inactive_threshold_s=0.0)
        mon.record_signal(_make_event())
        # With threshold=0 everything is immediately inactive.
        snap = mon.get_channel_snapshot("360_SCALP")
        assert snap.status == ChannelStatus.INACTIVE


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

class TestDuplicateDetection:
    def test_exact_duplicate_flagged(self):
        mon = ChannelMonitor()
        e1 = _make_event(signal_id="sig-1")
        e2 = _make_event(signal_id="sig-2")
        mon.record_signal(e1)
        result = mon.record_signal(e2)
        assert result.status == "DUPLICATE"

    def test_different_symbol_not_duplicate(self):
        mon = ChannelMonitor()
        mon.record_signal(_make_event(symbol="BTCUSDT", signal_id="s1"))
        result = mon.record_signal(
            _make_event(symbol="ETHUSDT", signal_id="s2")
        )
        assert result.status == "OK"

    def test_different_direction_not_duplicate(self):
        mon = ChannelMonitor()
        mon.record_signal(
            _make_event(direction="LONG", signal_id="s1")
        )
        result = mon.record_signal(
            _make_event(
                direction="SHORT",
                tp1=64000.0,
                stop_loss=66000.0,
                signal_id="s2",
            )
        )
        # Different direction on same channel/symbol is not a dup, but may be
        # a conflict-if from same channel it's just a reversal; conflicts only
        # flag across channels.
        assert result.status != "DUPLICATE"

    def test_different_entry_not_duplicate(self):
        mon = ChannelMonitor()
        mon.record_signal(_make_event(entry=65000, signal_id="s1"))
        result = mon.record_signal(
            _make_event(entry=66000, tp1=67000, signal_id="s2")
        )
        assert result.status == "OK"

    def test_duplicate_count_increments(self):
        mon = ChannelMonitor()
        for i in range(5):
            mon.record_signal(_make_event(signal_id=f"s-{i}"))
        snap = mon.get_channel_snapshot("360_SCALP")
        assert snap.duplicate_count == 4  # first is original, 4 are dups


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

class TestConflictDetection:
    def test_cross_channel_conflict(self):
        mon = ChannelMonitor()
        mon.record_signal(
            _make_event(
                channel="360_SCALP",
                symbol="BTCUSDT",
                direction="LONG",
                signal_id="s1",
            )
        )
        result = mon.record_signal(
            _make_event(
                channel="360_SCALP_FVG",
                symbol="BTCUSDT",
                direction="SHORT",
                tp1=64000.0,
                stop_loss=66000.0,
                signal_id="s2",
            )
        )
        assert result.status == "CONFLICT"
        conflicts = mon.get_conflicts()
        assert len(conflicts) == 1
        assert conflicts[0].symbol == "BTCUSDT"
        assert conflicts[0].conflict_type == "direction"

    def test_same_direction_no_conflict(self):
        mon = ChannelMonitor()
        mon.record_signal(
            _make_event(channel="360_SCALP", direction="LONG", signal_id="s1")
        )
        result = mon.record_signal(
            _make_event(
                channel="360_SCALP_FVG",
                direction="LONG",
                signal_id="s2",
            )
        )
        # Same direction across channels is not a conflict.
        assert result.status != "CONFLICT"

    def test_conflict_generates_diagnostic(self):
        mon = ChannelMonitor()
        mon.record_signal(
            _make_event(channel="360_SCALP", direction="LONG", signal_id="s1")
        )
        mon.record_signal(
            _make_event(
                channel="360_SCALP_CVD",
                direction="SHORT",
                tp1=64000.0,
                stop_loss=66000.0,
                signal_id="s2",
            )
        )
        diags = mon.get_diagnostics()
        assert any("Conflicting" in d.issue for d in diags)


# ---------------------------------------------------------------------------
# Low confidence
# ---------------------------------------------------------------------------

class TestLowConfidence:
    def test_low_confidence_flagged(self):
        mon = ChannelMonitor()
        result = mon.record_signal(_make_event(confidence=30.0))
        assert result.status == "LOW_CONFIDENCE"

    def test_high_confidence_ok(self):
        mon = ChannelMonitor()
        result = mon.record_signal(_make_event(confidence=80.0))
        assert result.status == "OK"

    def test_low_confidence_counted_in_snapshot(self):
        mon = ChannelMonitor()
        mon.record_signal(_make_event(confidence=30.0))
        snap = mon.get_channel_snapshot("360_SCALP")
        assert snap.low_confidence_count == 1


# ---------------------------------------------------------------------------
# TP/SL validation
# ---------------------------------------------------------------------------

class TestTpSlValidation:
    def test_valid_long(self):
        mon = ChannelMonitor()
        result = mon.record_signal(
            _make_event(direction="LONG", entry=100, tp1=110, stop_loss=95)
        )
        assert result.status == "OK"

    def test_invalid_long_tp_below_entry(self):
        mon = ChannelMonitor()
        result = mon.record_signal(
            _make_event(direction="LONG", entry=100, tp1=90, stop_loss=95)
        )
        assert result.status == "INVALID_LEVELS"

    def test_valid_short(self):
        mon = ChannelMonitor()
        result = mon.record_signal(
            _make_event(direction="SHORT", entry=100, tp1=90, stop_loss=105)
        )
        assert result.status == "OK"

    def test_invalid_short_sl_below_entry(self):
        mon = ChannelMonitor()
        result = mon.record_signal(
            _make_event(direction="SHORT", entry=100, tp1=90, stop_loss=95)
        )
        assert result.status == "INVALID_LEVELS"

    def test_invalid_levels_generate_error(self):
        mon = ChannelMonitor()
        mon.record_signal(
            _make_event(direction="LONG", entry=100, tp1=90, stop_loss=95)
        )
        snap = mon.get_channel_snapshot("360_SCALP")
        assert snap.error_count == 1


# ---------------------------------------------------------------------------
# Error recording
# ---------------------------------------------------------------------------

class TestErrorRecording:
    def test_record_error(self):
        mon = ChannelMonitor()
        mon.record_error("360_SCALP", "Timeout fetching candles")
        snap = mon.get_channel_snapshot("360_SCALP")
        assert snap.error_count == 1
        assert snap.last_error == "Timeout fetching candles"
        assert snap.status == ChannelStatus.ERROR

    def test_multiple_errors(self):
        mon = ChannelMonitor()
        mon.record_error("360_SCALP_FVG", "err1")
        mon.record_error("360_SCALP_FVG", "err2")
        snap = mon.get_channel_snapshot("360_SCALP_FVG")
        assert snap.error_count == 2
        assert snap.last_error == "err2"


# ---------------------------------------------------------------------------
# Infrastructure health updates
# ---------------------------------------------------------------------------

class TestInfraHealth:
    def test_api_unhealthy_generates_diagnostic(self):
        mon = ChannelMonitor()
        mon.update_api_health(
            healthy=False, error_count=5, last_error="429 Too Many Requests"
        )
        infra = mon.get_infra_health()
        assert not infra.api_healthy
        assert infra.api_error_count == 5
        criticals = mon.get_critical_diagnostics()
        assert len(criticals) >= 1

    def test_rate_limit_breach_warning(self):
        mon = ChannelMonitor()
        mon.update_api_health(
            healthy=True, rate_limit_breaches=3
        )
        diags = mon.get_diagnostics()
        assert any("Rate limit" in d.issue for d in diags)

    def test_ws_unhealthy(self):
        mon = ChannelMonitor()
        mon.update_ws_health(
            healthy=False, connections=0, last_error="Connection reset"
        )
        infra = mon.get_infra_health()
        assert not infra.ws_healthy
        criticals = mon.get_critical_diagnostics()
        assert len(criticals) >= 1

    def test_circuit_breaker_tripped(self):
        mon = ChannelMonitor()
        mon.update_circuit_breaker(
            tripped=True,
            reason="3 consecutive SL",
            per_symbol_tripped=["BTCUSDT"],
        )
        infra = mon.get_infra_health()
        assert infra.circuit_breaker_tripped
        assert infra.per_symbol_tripped == ["BTCUSDT"]


# ---------------------------------------------------------------------------
# Snapshots and reports
# ---------------------------------------------------------------------------

class TestSnapshots:
    def test_all_snapshots_covers_all_channels(self):
        mon = ChannelMonitor()
        snaps = mon.get_all_snapshots()
        assert set(snaps.keys()) == set(MONITORED_CHANNELS)

    def test_full_report_structure(self):
        mon = ChannelMonitor()
        mon.record_signal(_make_event())
        mon.update_api_health(healthy=True)
        report = mon.full_report()
        assert "channels" in report
        assert "infrastructure" in report
        assert "diagnostics" in report
        assert "timestamp" in report
        assert "uptime_s" in report

    def test_summary_text_format(self):
        mon = ChannelMonitor()
        mon.record_signal(_make_event())
        text = mon.summary_text()
        assert "Multi-Channel Monitor" in text
        assert "360_SCALP" in text


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------

class TestReset:
    def test_reset_clears_state(self):
        mon = ChannelMonitor()
        mon.record_signal(_make_event())
        mon.record_error("360_SCALP", "test error")
        mon.update_api_health(healthy=False, last_error="fail")
        mon.reset()
        snap = mon.get_channel_snapshot("360_SCALP")
        assert snap.signal_count == 0
        assert snap.error_count == 0
        infra = mon.get_infra_health()
        assert infra.api_healthy is True


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_zero_entry_does_not_crash_dedup(self):
        mon = ChannelMonitor()
        e = _make_event(entry=0.0, tp1=1.0)
        result = mon.record_signal(e)
        assert result is not None

    def test_large_volume_of_signals(self):
        mon = ChannelMonitor()
        for i in range(600):
            mon.record_signal(
                _make_event(
                    symbol=f"PAIR{i}USDT",
                    signal_id=f"s-{i}",
                    entry=100 + i,
                    tp1=110 + i,
                )
            )
        snap = mon.get_channel_snapshot("360_SCALP")
        # History capped at 500.
        assert snap.signal_count == 500

    def test_seconds_since_last_signal_inf(self):
        mon = ChannelMonitor()
        snap = mon.get_channel_snapshot("360_SCALP")
        assert snap.seconds_since_last_signal == float("inf")

    def test_inactive_threshold_inf(self):
        """Channel with threshold=inf should never become inactive from time."""
        mon = ChannelMonitor(inactive_threshold_s=float("inf"))
        mon.record_signal(_make_event())
        snap = mon.get_channel_snapshot("360_SCALP")
        assert snap.status == ChannelStatus.ACTIVE
