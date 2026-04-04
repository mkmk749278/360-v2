"""Monitor report generation – CSV/JSON logs and dashboard data.

Consumes :class:`ChannelMonitor` snapshots and produces:
  - CSV/JSON signal log lines with status flags per channel
  - Dashboard-ready data structures
  - Auto-generated implementation plans for detected issues
  - Critical failure notifications
"""

from __future__ import annotations

import csv
import io
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from src.channel_monitor import (
    ChannelMonitor,
    ChannelSnapshot,
    ChannelStatus,
    ConflictRecord,
    InfraHealth,
    MonitorDiagnostic,
    SignalEvent,
)
from src.utils import get_logger

log = get_logger("monitor_report")


# ---------------------------------------------------------------------------
# Implementation plan templates
# ---------------------------------------------------------------------------

_PLAN_TEMPLATES: Dict[str, Dict[str, str]] = {
    "inactive_channel": {
        "title": "Activate Silent Channel",
        "steps": (
            "1. Verify module configuration and feature flags in config/__init__.py\n"
            "2. Check data feed connectivity (WebSocket/REST) for required symbols\n"
            "3. Review channel min_confidence threshold – lower if too aggressive\n"
            "4. Inspect recent logs for suppressed signals or gate rejections\n"
            "5. Validate indicator computation in scanner/indicator_compute.py"
        ),
    },
    "api_failure": {
        "title": "Resolve API Failure",
        "steps": (
            "1. Check Binance API status page for outages\n"
            "2. Review rate_limiter.py weight tracking and throttle settings\n"
            "3. Inspect api_limits.py for weight consumption anomalies\n"
            "4. Increase retry backoff in binance.py (_RETRY_BACKOFF_BASE)\n"
            "5. Enable failover endpoint if available (exchange_client.py)"
        ),
    },
    "ws_failure": {
        "title": "Resolve WebSocket Disconnect",
        "steps": (
            "1. Check websocket_manager.py health_watchdog logs\n"
            "2. Verify network connectivity to Binance WS endpoints\n"
            "3. Review reconnect backoff settings\n"
            "4. Check for resource exhaustion (file descriptors, memory)\n"
            "5. Restart WebSocket manager if persistent failures"
        ),
    },
    "circuit_breaker": {
        "title": "Address Circuit Breaker Trip",
        "steps": (
            "1. Review recent signal outcomes in performance_tracker.py\n"
            "2. Analyze consecutive SL triggers for pattern (regime mismatch?)\n"
            "3. Check risk.py position sizing parameters\n"
            "4. Verify SL placement logic in channel evaluate() methods\n"
            "5. Consider widening SL or reducing confidence thresholds temporarily\n"
            "6. Wait for cooldown or manually reset after root cause fix"
        ),
    },
    "duplicate_signals": {
        "title": "Reduce Signal Duplicates",
        "steps": (
            "1. Review signal_router.py cooldown configuration\n"
            "2. Increase CHANNEL_COOLDOWN_SECONDS for affected channels\n"
            "3. Check cluster_suppression.py thresholds\n"
            "4. Verify dedup cache in signal_queue.py is functioning\n"
            "5. Consider adding entry-price proximity filter"
        ),
    },
    "conflicting_signals": {
        "title": "Resolve Signal Conflicts",
        "steps": (
            "1. Implement channel prioritization rules by confidence\n"
            "2. Add direction consistency gate in scanner common_gates.py\n"
            "3. Consider correlation-aware filtering in signal_router.py\n"
            "4. Suppress lower-confidence channel when conflict detected\n"
            "5. Log conflicts for post-session analysis"
        ),
    },
    "low_confidence": {
        "title": "Improve Signal Confidence",
        "steps": (
            "1. Review confidence.py scoring weights and thresholds\n"
            "2. Check confidence_calibration.py curve mapping\n"
            "3. Verify indicator data quality (sufficient candles, correct TF)\n"
            "4. Review regime.py classification accuracy\n"
            "5. Tune feedback_loop.py adaptive adjustments"
        ),
    },
    "high_latency": {
        "title": "Reduce Signal Latency",
        "steps": (
            "1. Profile scanner cycle time in scanner/__init__.py\n"
            "2. Check indicator_compute.py for CPU bottlenecks\n"
            "3. Verify asyncio.to_thread() is used for CPU-bound work\n"
            "4. Review WebSocket message lag in telemetry\n"
            "5. Reduce number of monitored pairs if resource-constrained"
        ),
    },
}


@dataclass
class ImplementationPlan:
    """Auto-generated plan to address a detected issue."""

    title: str
    module: str
    severity: str
    issue_description: str
    steps: str
    generated_at: float = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# MonitorReport
# ---------------------------------------------------------------------------

class MonitorReport:
    """Generates reports, logs, and implementation plans from monitor data.

    Parameters
    ----------
    monitor:
        The :class:`ChannelMonitor` instance to report on.
    """

    def __init__(self, monitor: ChannelMonitor) -> None:
        self._monitor = monitor

    # ------------------------------------------------------------------
    # CSV / JSON signal logs
    # ------------------------------------------------------------------

    def signal_to_csv_row(self, event: SignalEvent) -> str:
        """Format a single signal event as a CSV line."""
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(event.timestamp)),
            event.channel,
            event.symbol,
            event.direction,
            f"{event.confidence:.1f}",
            f"{event.entry:.8g}",
            f"{event.tp1:.8g}",
            f"{event.stop_loss:.8g}",
            f"{event.latency_ms:.0f}",
            event.quality_tier,
            event.status,
            event.signal_id,
        ])
        return buf.getvalue().strip()

    def signal_to_json(self, event: SignalEvent) -> str:
        """Format a single signal event as a JSON line."""
        record = {
            "timestamp": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(event.timestamp)
            ),
            "channel": event.channel,
            "symbol": event.symbol,
            "direction": event.direction,
            "confidence": round(event.confidence, 1),
            "entry": event.entry,
            "tp1": event.tp1,
            "stop_loss": event.stop_loss,
            "latency_ms": round(event.latency_ms, 0),
            "quality_tier": event.quality_tier,
            "status": event.status,
            "signal_id": event.signal_id,
        }
        return json.dumps(record, separators=(",", ":"))

    @staticmethod
    def csv_header() -> str:
        """Return the CSV header row."""
        return ",".join([
            "timestamp", "channel", "symbol", "direction", "confidence",
            "entry", "tp1", "stop_loss", "latency_ms", "quality_tier",
            "status", "signal_id",
        ])

    # ------------------------------------------------------------------
    # Dashboard data
    # ------------------------------------------------------------------

    def dashboard_data(self) -> Dict[str, Any]:
        """Generate structured dashboard data for UI consumption."""
        report = self._monitor.full_report()

        # Compute summary stats.
        channels = report["channels"]
        active_count = sum(
            1 for c in channels.values() if c["status"] == "active"
        )
        inactive_count = sum(
            1 for c in channels.values() if c["status"] == "inactive"
        )
        error_count = sum(
            1 for c in channels.values() if c["status"] == "error"
        )
        total_signals = sum(c["signal_count"] for c in channels.values())

        return {
            "summary": {
                "active_channels": active_count,
                "inactive_channels": inactive_count,
                "error_channels": error_count,
                "total_signals": total_signals,
                "conflicts": report["conflicts_total"],
                "duplicates": report["duplicates_total"],
            },
            "channels": channels,
            "infrastructure": report["infrastructure"],
            "diagnostics": report["diagnostics"],
            "uptime_s": report["uptime_s"],
            "timestamp": report["timestamp"],
        }

    def dashboard_text(self) -> str:
        """Generate human-readable dashboard text (for Telegram/CLI)."""
        return self._monitor.summary_text()

    # ------------------------------------------------------------------
    # Implementation plans
    # ------------------------------------------------------------------

    def generate_plans(self) -> List[ImplementationPlan]:
        """Scan monitor state and generate implementation plans for issues."""
        plans: List[ImplementationPlan] = []

        # Check inactive channels.
        for ch in self._monitor.get_inactive_channels():
            tmpl = _PLAN_TEMPLATES["inactive_channel"]
            plans.append(ImplementationPlan(
                title=f"{tmpl['title']} – {ch}",
                module=ch,
                severity="warning",
                issue_description=f"Channel {ch} has no recent signals.",
                steps=tmpl["steps"],
            ))

        # Check infrastructure.
        infra = self._monitor.get_infra_health()

        if not infra.api_healthy:
            tmpl = _PLAN_TEMPLATES["api_failure"]
            plans.append(ImplementationPlan(
                title=tmpl["title"],
                module="api",
                severity="critical",
                issue_description=f"API unhealthy: {infra.api_last_error}",
                steps=tmpl["steps"],
            ))

        if not infra.ws_healthy:
            tmpl = _PLAN_TEMPLATES["ws_failure"]
            plans.append(ImplementationPlan(
                title=tmpl["title"],
                module="websocket",
                severity="critical",
                issue_description=f"WebSocket unhealthy: {infra.ws_last_error}",
                steps=tmpl["steps"],
            ))

        if infra.circuit_breaker_tripped:
            tmpl = _PLAN_TEMPLATES["circuit_breaker"]
            plans.append(ImplementationPlan(
                title=tmpl["title"],
                module="circuit_breaker",
                severity="critical",
                issue_description=(
                    f"Circuit breaker tripped: {infra.circuit_breaker_reason}"
                ),
                steps=tmpl["steps"],
            ))

        if infra.rate_limit_breaches > 0:
            tmpl = _PLAN_TEMPLATES["api_failure"]
            plans.append(ImplementationPlan(
                title="Address Rate Limit Breaches",
                module="rate_limiter",
                severity="warning",
                issue_description=(
                    f"{infra.rate_limit_breaches} rate limit breaches detected."
                ),
                steps=tmpl["steps"],
            ))

        # Check diagnostics for patterns.
        diagnostics = self._monitor.get_diagnostics(limit=200)

        dup_count = sum(1 for d in diagnostics if "duplicate" in d.issue.lower())
        if dup_count >= 3:
            tmpl = _PLAN_TEMPLATES["duplicate_signals"]
            plans.append(ImplementationPlan(
                title=tmpl["title"],
                module="signal_router",
                severity="warning",
                issue_description=f"{dup_count} duplicate signals detected.",
                steps=tmpl["steps"],
            ))

        conflict_count = sum(1 for d in diagnostics if "conflict" in d.issue.lower())
        if conflict_count >= 2:
            tmpl = _PLAN_TEMPLATES["conflicting_signals"]
            plans.append(ImplementationPlan(
                title=tmpl["title"],
                module="scanner",
                severity="warning",
                issue_description=(
                    f"{conflict_count} conflicting signals detected."
                ),
                steps=tmpl["steps"],
            ))

        # Check for low-confidence patterns.
        snapshots = self._monitor.get_all_snapshots()
        for ch, snap in snapshots.items():
            if snap.avg_confidence > 0 and snap.avg_confidence < _LOW_CONF_PLAN_THRESHOLD:
                tmpl = _PLAN_TEMPLATES["low_confidence"]
                plans.append(ImplementationPlan(
                    title=f"{tmpl['title']} – {ch}",
                    module=ch,
                    severity="warning",
                    issue_description=(
                        f"Average confidence {snap.avg_confidence:.0f} "
                        f"is below threshold."
                    ),
                    steps=tmpl["steps"],
                ))

            if snap.avg_latency_ms > _HIGH_LATENCY_PLAN_THRESHOLD_MS:
                tmpl = _PLAN_TEMPLATES["high_latency"]
                plans.append(ImplementationPlan(
                    title=f"{tmpl['title']} – {ch}",
                    module=ch,
                    severity="warning",
                    issue_description=(
                        f"Average latency {snap.avg_latency_ms:.0f}ms "
                        f"exceeds threshold."
                    ),
                    steps=tmpl["steps"],
                ))

        return plans

    def plans_text(self) -> str:
        """Generate human-readable implementation plans."""
        plans = self.generate_plans()
        if not plans:
            return "✅ No issues detected – all channels nominal."

        lines: List[str] = [f"📋 *Implementation Plans* ({len(plans)} issues)\n"]
        for i, plan in enumerate(plans, 1):
            severity_icon = {
                "critical": "🚨",
                "warning": "⚠️",
                "info": "ℹ️",
            }.get(plan.severity, "❓")
            lines.append(f"{severity_icon} *{i}. {plan.title}*")
            lines.append(f"   Module: `{plan.module}`")
            lines.append(f"   Issue: {plan.issue_description}")
            lines.append(f"   Steps:\n{plan.steps}")
            lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Notification generation
    # ------------------------------------------------------------------

    def critical_notifications(self) -> List[str]:
        """Generate notification messages for critical failures."""
        notifications: List[str] = []

        criticals = self._monitor.get_critical_diagnostics()
        for diag in criticals:
            msg = (
                f"🚨 CRITICAL – {diag.module}\n"
                f"{diag.issue}\n"
                f"Recommendation: {diag.recommendation}"
            )
            notifications.append(msg)

        inactive = self._monitor.get_inactive_channels()
        if len(inactive) >= 3:
            msg = (
                f"🔴 ALERT: {len(inactive)} channels inactive\n"
                f"Channels: {', '.join(inactive)}\n"
                f"Action: Check data feeds and module configuration."
            )
            notifications.append(msg)

        return notifications

    # ------------------------------------------------------------------
    # Full JSON report export
    # ------------------------------------------------------------------

    def export_json(self) -> str:
        """Export full monitoring report as formatted JSON."""
        data = self._monitor.full_report()
        data["implementation_plans"] = [
            {
                "title": p.title,
                "module": p.module,
                "severity": p.severity,
                "issue": p.issue_description,
                "steps": p.steps,
            }
            for p in self.generate_plans()
        ]
        return json.dumps(data, indent=2, default=str)


# Thresholds for plan generation.
_LOW_CONF_PLAN_THRESHOLD: float = 60.0
_HIGH_LATENCY_PLAN_THRESHOLD_MS: float = 5000.0
