"""Real-time multi-channel signal monitoring.

Continuously tracks all 9 signal channels, detects issues (inactive channels,
conflicts, API failures, risk events), and generates actionable diagnostics.

Integrates with:
  - TelemetryCollector for system-level metrics
  - CircuitBreaker for risk/safety monitoring
  - SignalRouter for signal flow tracking
  - WebSocket / API health checks
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Deque, Dict, List, Optional, Set, Tuple

from src.utils import get_logger

log = get_logger("channel_monitor")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# How long (seconds) a channel can go without signals before flagged inactive.
_CHANNEL_INACTIVE_THRESHOLD_S: float = 600.0  # 10 minutes

# Rolling window size for per-channel signal history.
_SIGNAL_HISTORY_MAXLEN: int = 500

# Maximum age (seconds) of entries kept in duplicate detection cache.
_DEDUP_WINDOW_S: float = 120.0

# Confidence threshold below which we flag a signal as low-confidence.
_LOW_CONFIDENCE_THRESHOLD: float = 50.0


# ---------------------------------------------------------------------------
# Channel definitions matching the 9-channel architecture
# ---------------------------------------------------------------------------

class ChannelStatus(str, Enum):
    """Operational status of a monitored channel."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DISABLED = "disabled"


# The 9 channel names tracked by the monitor (from config ALL_CHANNELS).
MONITORED_CHANNELS: Tuple[str, ...] = (
    "360_SCALP",             # Range Fade / base scalp
    "360_SCALP_FVG",         # Fair Value Gap
    "360_SCALP_CVD",         # Cumulative Volume Delta
    "360_SCALP_VWAP",        # VWAP
    "360_SCALP_OBI",         # Order Block Invalidation
    "360_SCALP_DIVERGENCE",  # Divergence
    "360_SCALP_SUPERTREND",  # Supertrend
    "360_SCALP_ICHIMOKU",    # Ichimoku Cloud
    "360_SCALP_ORDERBLOCK",  # Order Block
)

# Mapping of logical module groups for dependency monitoring.
MODULE_GROUPS: Dict[str, List[str]] = {
    "range_fade": [
        "detector", "confidence", "confidence_calibration",
        "confidence_decay", "filters", "feedback_loop",
    ],
    "smc": ["smc", "structural_levels", "regime"],
    "fvg": ["chart_patterns", "volatility_metrics", "vwap"],
    "kill_zone": ["kill_zone"],
    "tape": ["order_flow", "order_book"],
    "cornix": ["cornix_formatter", "feedback_loop"],
    "cross_asset": ["cross_asset", "correlation", "cvd"],
    "confluence": ["confluence_detector"],
    "predictive_ai": ["predictive_ai", "openai_evaluator"],
}

# Mapping of API / infra module groups.
INFRA_MODULES: Dict[str, List[str]] = {
    "api": ["binance", "exchange", "exchange_client", "api_limits", "rate_limiter"],
    "websocket": ["websocket_manager"],
    "risk": ["dca", "circuit_breaker", "cluster_suppression", "risk"],
    "logging": ["logger", "logging_utils", "healthcheck", "telemetry"],
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class SignalEvent:
    """Lightweight record of a signal observed by the monitor."""

    channel: str
    symbol: str
    direction: str  # "LONG" or "SHORT"
    confidence: float
    entry: float
    tp1: float
    stop_loss: float
    timestamp: float = field(default_factory=time.monotonic)
    signal_id: str = ""
    latency_ms: float = 0.0
    quality_tier: str = ""
    status: str = "OK"  # OK | CONFLICT | DUPLICATE | LOW_CONFIDENCE | STALE


@dataclass
class ChannelSnapshot:
    """Point-in-time snapshot of a single channel's health."""

    name: str
    status: ChannelStatus = ChannelStatus.INACTIVE
    signal_count: int = 0
    last_signal_time: float = 0.0
    avg_confidence: float = 0.0
    avg_latency_ms: float = 0.0
    error_count: int = 0
    duplicate_count: int = 0
    conflict_count: int = 0
    low_confidence_count: int = 0
    last_error: str = ""

    @property
    def seconds_since_last_signal(self) -> float:
        if self.last_signal_time == 0.0:
            return float("inf")
        return time.monotonic() - self.last_signal_time


@dataclass
class InfraHealth:
    """Infrastructure component health snapshot."""

    api_healthy: bool = True
    api_error_count: int = 0
    api_last_error: str = ""
    rate_limit_remaining: int = -1
    rate_limit_breaches: int = 0

    ws_healthy: bool = True
    ws_connections: int = 0
    ws_reconnects: int = 0
    ws_last_error: str = ""

    circuit_breaker_tripped: bool = False
    circuit_breaker_reason: str = ""
    per_symbol_tripped: List[str] = field(default_factory=list)


@dataclass
class ConflictRecord:
    """Record of two conflicting signals."""

    signal_a_id: str
    signal_b_id: str
    symbol: str
    channel_a: str
    channel_b: str
    direction_a: str
    direction_b: str
    conflict_type: str  # "direction" or "duplicate"
    timestamp: float = field(default_factory=time.monotonic)


@dataclass
class MonitorDiagnostic:
    """Actionable diagnostic generated by the monitor."""

    severity: str  # "critical" | "warning" | "info"
    module: str
    issue: str
    recommendation: str
    timestamp: float = field(default_factory=time.monotonic)


# ---------------------------------------------------------------------------
# ChannelMonitor
# ---------------------------------------------------------------------------

class ChannelMonitor:
    """Real-time multi-channel signal monitoring engine.

    Tracks signal flow across all 9 channels, detects conflicts/duplicates,
    monitors API and WebSocket health, and generates diagnostics.
    """

    def __init__(
        self,
        inactive_threshold_s: float = _CHANNEL_INACTIVE_THRESHOLD_S,
        dedup_window_s: float = _DEDUP_WINDOW_S,
    ) -> None:
        self._inactive_threshold_s = inactive_threshold_s
        self._dedup_window_s = dedup_window_s

        # Per-channel signal history.
        self._channel_history: Dict[str, Deque[SignalEvent]] = {
            ch: deque(maxlen=_SIGNAL_HISTORY_MAXLEN) for ch in MONITORED_CHANNELS
        }

        # Per-channel error counters.
        self._channel_errors: Dict[str, int] = defaultdict(int)
        self._channel_last_error: Dict[str, str] = {}

        # Conflict / duplicate tracking.
        self._conflicts: Deque[ConflictRecord] = deque(maxlen=200)
        self._duplicate_count: int = 0
        self._conflict_count: int = 0

        # Diagnostics log.
        self._diagnostics: Deque[MonitorDiagnostic] = deque(maxlen=500)

        # Infrastructure health (updated externally).
        self._infra = InfraHealth()

        # Dedup cache: (symbol, direction, channel) -> latest timestamp.
        self._recent_signals: Deque[SignalEvent] = deque(maxlen=2000)

        # Started timestamp for uptime tracking.
        self._started_at: float = time.monotonic()

    # ------------------------------------------------------------------
    # Signal ingestion
    # ------------------------------------------------------------------

    def record_signal(self, event: SignalEvent) -> SignalEvent:
        """Record a new signal event and run inline checks.

        Returns the event with its ``status`` field updated to reflect
        any detected issues (DUPLICATE, CONFLICT, LOW_CONFIDENCE, etc.).
        """
        channel = event.channel

        # Accept signals from unregistered channels gracefully.
        if channel not in self._channel_history:
            self._channel_history[channel] = deque(maxlen=_SIGNAL_HISTORY_MAXLEN)

        # --- Duplicate detection ---
        if self._is_duplicate(event):
            event.status = "DUPLICATE"
            self._duplicate_count += 1
            snap = self._get_or_create_snapshot(channel)
            log.debug(
                "Duplicate signal detected: %s %s on %s",
                event.symbol, event.direction, channel,
            )

        # --- Conflict detection ---
        conflict = self._find_conflict(event)
        if conflict is not None:
            event.status = "CONFLICT"
            self._conflict_count += 1
            self._conflicts.append(conflict)
            self._add_diagnostic(
                severity="warning",
                module=channel,
                issue=(
                    f"Conflicting signals for {event.symbol}: "
                    f"{conflict.channel_a}={conflict.direction_a} vs "
                    f"{conflict.channel_b}={conflict.direction_b}"
                ),
                recommendation=(
                    "Review channel prioritization rules. Consider suppressing "
                    "the lower-confidence signal or adding correlation-aware "
                    "filtering."
                ),
            )

        # --- Low confidence ---
        if event.confidence < _LOW_CONFIDENCE_THRESHOLD and event.status == "OK":
            event.status = "LOW_CONFIDENCE"

        # --- TP/SL sanity ---
        if not self._validate_tp_sl(event) and event.status == "OK":
            event.status = "INVALID_LEVELS"
            self._channel_errors[channel] += 1
            self._channel_last_error[channel] = (
                f"Invalid TP/SL levels for {event.symbol}"
            )
            self._add_diagnostic(
                severity="warning",
                module=channel,
                issue=f"Invalid TP/SL: {event.symbol} {event.direction}",
                recommendation=(
                    "Check detector logic and entry/TP/SL computation in "
                    "the channel's evaluate() method."
                ),
            )

        # Store in channel history.
        self._channel_history[channel].append(event)
        self._recent_signals.append(event)
        return event

    def record_error(self, channel: str, error_msg: str) -> None:
        """Record an error event for a channel."""
        self._channel_errors[channel] += 1
        self._channel_last_error[channel] = error_msg
        self._add_diagnostic(
            severity="warning",
            module=channel,
            issue=error_msg,
            recommendation="Investigate the error and check module logs.",
        )
        log.warning("Channel error [%s]: %s", channel, error_msg)

    # ------------------------------------------------------------------
    # Infrastructure health updates
    # ------------------------------------------------------------------

    def update_api_health(
        self,
        healthy: bool,
        error_count: int = 0,
        last_error: str = "",
        rate_limit_remaining: int = -1,
        rate_limit_breaches: int = 0,
    ) -> None:
        """Update API health metrics."""
        self._infra.api_healthy = healthy
        self._infra.api_error_count = error_count
        self._infra.api_last_error = last_error
        self._infra.rate_limit_remaining = rate_limit_remaining
        self._infra.rate_limit_breaches = rate_limit_breaches

        if not healthy:
            self._add_diagnostic(
                severity="critical",
                module="api",
                issue=f"API unhealthy: {last_error}",
                recommendation=(
                    "Check Binance API connectivity. Review rate_limiter.py "
                    "throttling and api_limits.py weight tracking. Consider "
                    "enabling failover or increasing retry backoff."
                ),
            )

        if rate_limit_breaches > 0:
            self._add_diagnostic(
                severity="warning",
                module="api",
                issue=f"Rate limit breaches: {rate_limit_breaches}",
                recommendation=(
                    "Reduce API call frequency in binance.py. Increase "
                    "rate_limiter.py cooldown or enable request batching."
                ),
            )

    def update_ws_health(
        self,
        healthy: bool,
        connections: int = 0,
        reconnects: int = 0,
        last_error: str = "",
    ) -> None:
        """Update WebSocket health metrics."""
        self._infra.ws_healthy = healthy
        self._infra.ws_connections = connections
        self._infra.ws_reconnects = reconnects
        self._infra.ws_last_error = last_error

        if not healthy:
            self._add_diagnostic(
                severity="critical",
                module="websocket",
                issue=f"WebSocket unhealthy: {last_error}",
                recommendation=(
                    "Check websocket_manager.py connection pool. Verify "
                    "network connectivity and Binance WS endpoint status. "
                    "Consider increasing reconnect backoff."
                ),
            )

    def update_circuit_breaker(
        self,
        tripped: bool,
        reason: str = "",
        per_symbol_tripped: Optional[List[str]] = None,
    ) -> None:
        """Update circuit breaker status."""
        self._infra.circuit_breaker_tripped = tripped
        self._infra.circuit_breaker_reason = reason
        self._infra.per_symbol_tripped = per_symbol_tripped or []

        if tripped:
            self._add_diagnostic(
                severity="critical",
                module="circuit_breaker",
                issue=f"Circuit breaker tripped: {reason}",
                recommendation=(
                    "Review recent SL hits and drawdown in circuit_breaker.py. "
                    "Consider adjusting max_consecutive_sl, max_daily_drawdown_pct, "
                    "or cooldown_seconds. Check risk.py position sizing."
                ),
            )

    # ------------------------------------------------------------------
    # Channel snapshots and overall report
    # ------------------------------------------------------------------

    def get_channel_snapshot(self, channel: str) -> ChannelSnapshot:
        """Build a point-in-time snapshot for a single channel."""
        history = self._channel_history.get(channel, deque())

        snap = ChannelSnapshot(name=channel)
        snap.signal_count = len(history)
        snap.error_count = self._channel_errors.get(channel, 0)
        snap.last_error = self._channel_last_error.get(channel, "")

        if history:
            snap.last_signal_time = history[-1].timestamp
            confidences = [e.confidence for e in history]
            snap.avg_confidence = sum(confidences) / len(confidences)
            latencies = [e.latency_ms for e in history if e.latency_ms > 0]
            snap.avg_latency_ms = (
                sum(latencies) / len(latencies) if latencies else 0.0
            )
            snap.duplicate_count = sum(
                1 for e in history if e.status == "DUPLICATE"
            )
            snap.conflict_count = sum(
                1 for e in history if e.status == "CONFLICT"
            )
            snap.low_confidence_count = sum(
                1 for e in history if e.status == "LOW_CONFIDENCE"
            )

        # Determine status.
        if snap.error_count > 0 and snap.signal_count == 0:
            snap.status = ChannelStatus.ERROR
        elif snap.seconds_since_last_signal > self._inactive_threshold_s:
            snap.status = ChannelStatus.INACTIVE
        else:
            snap.status = ChannelStatus.ACTIVE

        return snap

    def get_all_snapshots(self) -> Dict[str, ChannelSnapshot]:
        """Build snapshots for all monitored channels."""
        return {ch: self.get_channel_snapshot(ch) for ch in MONITORED_CHANNELS}

    def get_inactive_channels(self) -> List[str]:
        """Return names of channels that have gone silent."""
        inactive = []
        for ch in MONITORED_CHANNELS:
            snap = self.get_channel_snapshot(ch)
            if snap.status in (ChannelStatus.INACTIVE, ChannelStatus.ERROR):
                inactive.append(ch)
        return inactive

    def get_infra_health(self) -> InfraHealth:
        """Return current infrastructure health snapshot."""
        return self._infra

    def get_conflicts(self, limit: int = 50) -> List[ConflictRecord]:
        """Return recent conflict records."""
        records = list(self._conflicts)
        return records[-limit:]

    def get_diagnostics(self, limit: int = 100) -> List[MonitorDiagnostic]:
        """Return recent diagnostics, newest first."""
        items = list(self._diagnostics)
        items.reverse()
        return items[:limit]

    def get_critical_diagnostics(self) -> List[MonitorDiagnostic]:
        """Return only critical-severity diagnostics."""
        return [d for d in self._diagnostics if d.severity == "critical"]

    # ------------------------------------------------------------------
    # Summary / dashboard text
    # ------------------------------------------------------------------

    def summary_text(self) -> str:
        """Generate a human-readable monitoring summary for dashboard/Telegram."""
        lines: List[str] = ["📡 *Multi-Channel Monitor*\n"]
        snapshots = self.get_all_snapshots()

        # Channel status table.
        for ch, snap in snapshots.items():
            status_icon = {
                ChannelStatus.ACTIVE: "🟢",
                ChannelStatus.INACTIVE: "🔴",
                ChannelStatus.ERROR: "🟡",
                ChannelStatus.DISABLED: "⚪",
            }.get(snap.status, "❓")

            line = (
                f"{status_icon} {ch}: {snap.signal_count} signals | "
                f"conf={snap.avg_confidence:.0f} | "
                f"lat={snap.avg_latency_ms:.0f}ms"
            )
            if snap.error_count > 0:
                line += f" | err={snap.error_count}"
            lines.append(line)

        # Infrastructure.
        lines.append("")
        api_icon = "🟢" if self._infra.api_healthy else "🔴"
        ws_icon = "🟢" if self._infra.ws_healthy else "🔴"
        cb_icon = "🔴" if self._infra.circuit_breaker_tripped else "🟢"
        lines.append(
            f"API {api_icon} | WS {ws_icon} ({self._infra.ws_connections} conn) "
            f"| CB {cb_icon}"
        )

        # Conflicts & duplicates.
        if self._conflict_count > 0 or self._duplicate_count > 0:
            lines.append(
                f"⚠️ Conflicts={self._conflict_count} | "
                f"Duplicates={self._duplicate_count}"
            )

        # Critical diagnostics.
        criticals = self.get_critical_diagnostics()
        if criticals:
            lines.append(f"\n🚨 {len(criticals)} critical issue(s):")
            for diag in criticals[-3:]:
                lines.append(f"  • {diag.module}: {diag.issue}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Full report as dict (JSON-serializable)
    # ------------------------------------------------------------------

    def full_report(self) -> Dict[str, Any]:
        """Generate a comprehensive JSON-serializable report."""
        snapshots = self.get_all_snapshots()
        return {
            "timestamp": time.time(),
            "uptime_s": time.monotonic() - self._started_at,
            "channels": {
                ch: {
                    "status": snap.status.value,
                    "signal_count": snap.signal_count,
                    "seconds_since_last_signal": (
                        round(snap.seconds_since_last_signal, 1)
                        if snap.seconds_since_last_signal != float("inf")
                        else None
                    ),
                    "avg_confidence": round(snap.avg_confidence, 1),
                    "avg_latency_ms": round(snap.avg_latency_ms, 1),
                    "error_count": snap.error_count,
                    "duplicate_count": snap.duplicate_count,
                    "conflict_count": snap.conflict_count,
                    "low_confidence_count": snap.low_confidence_count,
                    "last_error": snap.last_error,
                }
                for ch, snap in snapshots.items()
            },
            "infrastructure": {
                "api_healthy": self._infra.api_healthy,
                "api_error_count": self._infra.api_error_count,
                "api_last_error": self._infra.api_last_error,
                "rate_limit_remaining": self._infra.rate_limit_remaining,
                "rate_limit_breaches": self._infra.rate_limit_breaches,
                "ws_healthy": self._infra.ws_healthy,
                "ws_connections": self._infra.ws_connections,
                "ws_reconnects": self._infra.ws_reconnects,
                "ws_last_error": self._infra.ws_last_error,
                "circuit_breaker_tripped": self._infra.circuit_breaker_tripped,
                "circuit_breaker_reason": self._infra.circuit_breaker_reason,
                "per_symbol_tripped": self._infra.per_symbol_tripped,
            },
            "conflicts_total": self._conflict_count,
            "duplicates_total": self._duplicate_count,
            "diagnostics": [
                {
                    "severity": d.severity,
                    "module": d.module,
                    "issue": d.issue,
                    "recommendation": d.recommendation,
                }
                for d in list(self._diagnostics)[-50:]
            ],
        }

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset all monitoring state."""
        for ch in self._channel_history:
            self._channel_history[ch].clear()
        self._channel_errors.clear()
        self._channel_last_error.clear()
        self._conflicts.clear()
        self._diagnostics.clear()
        self._recent_signals.clear()
        self._duplicate_count = 0
        self._conflict_count = 0
        self._infra = InfraHealth()
        self._started_at = time.monotonic()
        log.info("Channel monitor reset")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_duplicate(self, event: SignalEvent) -> bool:
        """Check if a near-identical signal was recently recorded."""
        cutoff = event.timestamp - self._dedup_window_s
        for prev in reversed(self._recent_signals):
            if prev.timestamp < cutoff:
                break
            if (
                prev.symbol == event.symbol
                and prev.direction == event.direction
                and prev.channel == event.channel
                and abs(prev.entry - event.entry) / max(event.entry, 1e-9) < 0.001
            ):
                return True
        return False

    def _find_conflict(self, event: SignalEvent) -> Optional[ConflictRecord]:
        """Find a conflicting signal for the same symbol from another channel."""
        cutoff = event.timestamp - self._dedup_window_s
        for prev in reversed(self._recent_signals):
            if prev.timestamp < cutoff:
                break
            if (
                prev.symbol == event.symbol
                and prev.channel != event.channel
                and prev.direction != event.direction
            ):
                return ConflictRecord(
                    signal_a_id=prev.signal_id,
                    signal_b_id=event.signal_id,
                    symbol=event.symbol,
                    channel_a=prev.channel,
                    channel_b=event.channel,
                    direction_a=prev.direction,
                    direction_b=event.direction,
                    conflict_type="direction",
                )
        return None

    @staticmethod
    def _validate_tp_sl(event: SignalEvent) -> bool:
        """Validate that TP and SL levels are on the correct side of entry."""
        if event.direction == "LONG":
            return event.tp1 > event.entry and event.stop_loss < event.entry
        if event.direction == "SHORT":
            return event.tp1 < event.entry and event.stop_loss > event.entry
        return True  # unknown direction, skip validation

    def _add_diagnostic(
        self, severity: str, module: str, issue: str, recommendation: str
    ) -> None:
        self._diagnostics.append(
            MonitorDiagnostic(
                severity=severity,
                module=module,
                issue=issue,
                recommendation=recommendation,
            )
        )

    def _get_or_create_snapshot(self, channel: str) -> ChannelSnapshot:
        """Internal helper – ensures channel history deque exists."""
        if channel not in self._channel_history:
            self._channel_history[channel] = deque(maxlen=_SIGNAL_HISTORY_MAXLEN)
        return self.get_channel_snapshot(channel)
