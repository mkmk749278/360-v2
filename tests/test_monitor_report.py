"""Tests for monitor_report.py – report generation and implementation plans."""

from __future__ import annotations

import json
import time

import pytest

from src.channel_monitor import (
    ChannelMonitor,
    ChannelStatus,
    SignalEvent,
)
from src.monitor_report import (
    ImplementationPlan,
    MonitorReport,
    _HIGH_LATENCY_PLAN_THRESHOLD_MS,
    _LOW_CONF_PLAN_THRESHOLD,
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


def _make_monitor_with_signals() -> ChannelMonitor:
    """Return a monitor with a few signals across channels."""
    mon = ChannelMonitor()
    mon.record_signal(_make_event(channel="360_SCALP", signal_id="s1"))
    mon.record_signal(
        _make_event(channel="360_SCALP_FVG", signal_id="s2", symbol="ETHUSDT")
    )
    return mon


# ---------------------------------------------------------------------------
# CSV / JSON formatting
# ---------------------------------------------------------------------------

class TestSignalFormatting:
    def test_csv_header(self):
        report = MonitorReport(ChannelMonitor())
        header = report.csv_header()
        assert "timestamp" in header
        assert "channel" in header
        assert "signal_id" in header

    def test_csv_row(self):
        report = MonitorReport(ChannelMonitor())
        e = _make_event(confidence=85.5, signal_id="test-sig")
        row = report.signal_to_csv_row(e)
        assert "360_SCALP" in row
        assert "BTCUSDT" in row
        assert "LONG" in row
        assert "85.5" in row
        assert "test-sig" in row

    def test_json_row(self):
        report = MonitorReport(ChannelMonitor())
        e = _make_event(confidence=75.0, signal_id="json-sig")
        line = report.signal_to_json(e)
        data = json.loads(line)
        assert data["channel"] == "360_SCALP"
        assert data["symbol"] == "BTCUSDT"
        assert data["direction"] == "LONG"
        assert data["confidence"] == 75.0
        assert data["signal_id"] == "json-sig"

    def test_json_valid(self):
        report = MonitorReport(ChannelMonitor())
        e = _make_event()
        line = report.signal_to_json(e)
        # Must be valid JSON.
        data = json.loads(line)
        assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# Dashboard data
# ---------------------------------------------------------------------------

class TestDashboardData:
    def test_dashboard_data_structure(self):
        mon = _make_monitor_with_signals()
        report = MonitorReport(mon)
        data = report.dashboard_data()
        assert "summary" in data
        assert "channels" in data
        assert "infrastructure" in data
        assert "diagnostics" in data

    def test_summary_counts(self):
        mon = _make_monitor_with_signals()
        report = MonitorReport(mon)
        data = report.dashboard_data()
        summary = data["summary"]
        assert summary["total_signals"] >= 2
        assert summary["active_channels"] >= 2

    def test_dashboard_text(self):
        mon = _make_monitor_with_signals()
        report = MonitorReport(mon)
        text = report.dashboard_text()
        assert "Multi-Channel Monitor" in text


# ---------------------------------------------------------------------------
# Implementation plans
# ---------------------------------------------------------------------------

class TestImplementationPlans:
    def test_no_issues_no_plans(self):
        """If all channels are active and healthy, no plans should be generated."""
        mon = ChannelMonitor()
        # Feed signals to all channels so none are inactive.
        for ch in [
            "360_SCALP", "360_SCALP_FVG", "360_SCALP_CVD",
            "360_SCALP_VWAP", "360_SCALP_OBI", "360_SCALP_DIVERGENCE",
            "360_SCALP_SUPERTREND", "360_SCALP_ICHIMOKU", "360_SCALP_ORDERBLOCK",
        ]:
            mon.record_signal(
                _make_event(channel=ch, signal_id=f"s-{ch}", symbol=f"{ch}USDT")
            )
        report = MonitorReport(mon)
        plans = report.generate_plans()
        assert len(plans) == 0

    def test_inactive_channel_generates_plan(self):
        """Inactive channels should generate activation plans."""
        mon = ChannelMonitor(inactive_threshold_s=0.0)
        report = MonitorReport(mon)
        plans = report.generate_plans()
        # All channels are inactive → plans for each.
        assert len(plans) >= 9
        assert all("Activate" in p.title for p in plans)

    def test_api_failure_plan(self):
        mon = ChannelMonitor()
        mon.update_api_health(healthy=False, last_error="Connection timeout")
        report = MonitorReport(mon)
        plans = report.generate_plans()
        api_plans = [p for p in plans if p.module == "api"]
        assert len(api_plans) >= 1
        assert api_plans[0].severity == "critical"

    def test_ws_failure_plan(self):
        mon = ChannelMonitor()
        mon.update_ws_health(healthy=False, last_error="Reset by peer")
        report = MonitorReport(mon)
        plans = report.generate_plans()
        ws_plans = [p for p in plans if p.module == "websocket"]
        assert len(ws_plans) >= 1

    def test_circuit_breaker_plan(self):
        mon = ChannelMonitor()
        mon.update_circuit_breaker(tripped=True, reason="Daily drawdown exceeded")
        report = MonitorReport(mon)
        plans = report.generate_plans()
        cb_plans = [p for p in plans if p.module == "circuit_breaker"]
        assert len(cb_plans) >= 1
        assert cb_plans[0].severity == "critical"

    def test_rate_limit_breach_plan(self):
        mon = ChannelMonitor()
        mon.update_api_health(healthy=True, rate_limit_breaches=5)
        report = MonitorReport(mon)
        plans = report.generate_plans()
        rl_plans = [p for p in plans if p.module == "rate_limiter"]
        assert len(rl_plans) >= 1

    def test_low_confidence_plan(self):
        mon = ChannelMonitor()
        # Record multiple low-confidence signals.
        for i in range(5):
            mon.record_signal(
                _make_event(
                    confidence=40.0,
                    signal_id=f"lc-{i}",
                    symbol=f"PAIR{i}USDT",
                    entry=100 + i,
                    tp1=110 + i,
                )
            )
        report = MonitorReport(mon)
        plans = report.generate_plans()
        lc_plans = [p for p in plans if "Confidence" in p.title]
        assert len(lc_plans) >= 1

    def test_high_latency_plan(self):
        mon = ChannelMonitor()
        for i in range(3):
            mon.record_signal(
                _make_event(
                    latency_ms=10000.0,
                    signal_id=f"hl-{i}",
                    symbol=f"LAT{i}USDT",
                    entry=100 + i,
                    tp1=110 + i,
                )
            )
        report = MonitorReport(mon)
        plans = report.generate_plans()
        hl_plans = [p for p in plans if "Latency" in p.title]
        assert len(hl_plans) >= 1

    def test_plans_text_format(self):
        mon = ChannelMonitor()
        mon.update_api_health(healthy=False, last_error="timeout")
        report = MonitorReport(mon)
        text = report.plans_text()
        assert "Implementation Plans" in text
        assert "API" in text or "api" in text

    def test_no_issues_plans_text(self):
        mon = ChannelMonitor()
        for ch in [
            "360_SCALP", "360_SCALP_FVG", "360_SCALP_CVD",
            "360_SCALP_VWAP", "360_SCALP_OBI", "360_SCALP_DIVERGENCE",
            "360_SCALP_SUPERTREND", "360_SCALP_ICHIMOKU", "360_SCALP_ORDERBLOCK",
        ]:
            mon.record_signal(
                _make_event(channel=ch, signal_id=f"s-{ch}", symbol=f"{ch}USDT")
            )
        report = MonitorReport(mon)
        text = report.plans_text()
        assert "No issues detected" in text


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

class TestNotifications:
    def test_critical_notification_on_api_failure(self):
        mon = ChannelMonitor()
        mon.update_api_health(healthy=False, last_error="Connection refused")
        report = MonitorReport(mon)
        notifs = report.critical_notifications()
        assert len(notifs) >= 1
        assert "CRITICAL" in notifs[0]

    def test_inactive_channels_alert(self):
        mon = ChannelMonitor(inactive_threshold_s=0.0)
        report = MonitorReport(mon)
        notifs = report.critical_notifications()
        # Should alert about many inactive channels.
        assert any("inactive" in n.lower() for n in notifs)

    def test_no_notifications_when_healthy(self):
        mon = ChannelMonitor()
        # Activate all channels.
        for ch in [
            "360_SCALP", "360_SCALP_FVG", "360_SCALP_CVD",
            "360_SCALP_VWAP", "360_SCALP_OBI", "360_SCALP_DIVERGENCE",
            "360_SCALP_SUPERTREND", "360_SCALP_ICHIMOKU", "360_SCALP_ORDERBLOCK",
        ]:
            mon.record_signal(
                _make_event(channel=ch, signal_id=f"s-{ch}", symbol=f"{ch}USDT")
            )
        report = MonitorReport(mon)
        notifs = report.critical_notifications()
        assert len(notifs) == 0


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------

class TestJsonExport:
    def test_export_valid_json(self):
        mon = _make_monitor_with_signals()
        report = MonitorReport(mon)
        exported = report.export_json()
        data = json.loads(exported)
        assert "channels" in data
        assert "implementation_plans" in data

    def test_export_includes_plans(self):
        mon = ChannelMonitor()
        mon.update_api_health(healthy=False, last_error="err")
        report = MonitorReport(mon)
        exported = report.export_json()
        data = json.loads(exported)
        assert len(data["implementation_plans"]) >= 1

    def test_export_with_infra_issues(self):
        mon = ChannelMonitor()
        mon.update_ws_health(healthy=False, last_error="reset")
        mon.update_circuit_breaker(tripped=True, reason="drawdown")
        report = MonitorReport(mon)
        exported = report.export_json()
        data = json.loads(exported)
        assert data["infrastructure"]["ws_healthy"] is False
        assert data["infrastructure"]["circuit_breaker_tripped"] is True


# ---------------------------------------------------------------------------
# Conflict plan generation
# ---------------------------------------------------------------------------

class TestConflictPlans:
    def test_conflict_plan_generated(self):
        mon = ChannelMonitor()
        # Create conflicts.
        mon.record_signal(
            _make_event(
                channel="360_SCALP", direction="LONG",
                symbol="BTCUSDT", signal_id="c1",
            )
        )
        mon.record_signal(
            _make_event(
                channel="360_SCALP_FVG", direction="SHORT",
                symbol="BTCUSDT", signal_id="c2",
                tp1=64000.0, stop_loss=66000.0,
            )
        )
        mon.record_signal(
            _make_event(
                channel="360_SCALP_CVD", direction="SHORT",
                symbol="ETHUSDT", signal_id="c3",
                tp1=2900.0, stop_loss=3100.0,
                entry=3000.0,
            )
        )
        mon.record_signal(
            _make_event(
                channel="360_SCALP", direction="LONG",
                symbol="ETHUSDT", signal_id="c4",
                entry=3000.0, tp1=3100.0, stop_loss=2900.0,
            )
        )
        report = MonitorReport(mon)
        plans = report.generate_plans()
        conflict_plans = [p for p in plans if "Conflict" in p.title]
        assert len(conflict_plans) >= 1


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_monitor_dashboard(self):
        mon = ChannelMonitor()
        report = MonitorReport(mon)
        data = report.dashboard_data()
        assert data["summary"]["total_signals"] == 0

    def test_csv_special_characters(self):
        """Ensure CSV handles special chars in signal_id."""
        report = MonitorReport(ChannelMonitor())
        e = _make_event(signal_id='sig-with,"quotes')
        row = report.signal_to_csv_row(e)
        assert "sig-with" in row  # CSV should escape properly.
