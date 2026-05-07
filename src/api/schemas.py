"""Pydantic schemas for the Lumin app API.

Schema names mirror the Dart classes in ``lib/data/mock_data.dart`` so the
client can deserialize without a translation layer.  When a field's name
has to differ from the engine's internal attribute (for example to match
the Dart camelCase or a more user-friendly label), the difference is
documented inline.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Pulse / engine snapshot
# ---------------------------------------------------------------------------


class PulseSnapshot(BaseModel):
    """High-level engine status — drives the Pulse tab dashboard."""

    status: Literal["Healthy", "Degraded", "Down"] = "Healthy"
    mode: Literal["off", "paper", "live"]
    regime: str = Field(..., description="BTC market regime, e.g. TRENDING_UP")
    regime_pct_trending: float = Field(
        0.0, description="Percentage of recent cycles classified as trending"
    )
    today_pnl_usd: float
    today_pnl_pct: float
    daily_loss_budget_usd: float
    daily_loss_used_usd: float
    open_positions: int
    signals_today: int
    uptime_seconds: float
    scanning_pairs: int


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------


class SignalDetail(BaseModel):
    """One signal — open or closed.  Mirrors Dart ``MockSignal``."""

    signal_id: str
    symbol: str
    direction: Literal["LONG", "SHORT"]
    entry: float
    stop_loss: float
    tp1: float
    tp2: float
    tp3: Optional[float] = None
    confidence: float
    quality_tier: str
    setup_class: str
    agent_name: str = Field(..., description="Display name of the evaluator")
    status: str
    current_price: float
    pnl_pct: float
    pre_tp_hit: bool = False
    pre_tp_threshold_pct: float = Field(
        0.0,
        description="Resolved pre-TP threshold % stamped at dispatch (0 if not eligible)",
    )
    pre_tp_trigger_price: Optional[float] = Field(
        None,
        description="Absolute price the engine watches for pre-TP fire",
    )
    timestamp: datetime
    minutes_ago: int


class SignalsResponse(BaseModel):
    items: List[SignalDetail]
    total: int


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------


class PositionDetail(BaseModel):
    """Open position — paper or live.  Mirrors Dart ``MockPosition``."""

    signal_id: str
    symbol: str
    direction: Literal["LONG", "SHORT"]
    entry: float
    current_price: float
    qty: float
    pnl_usd: float
    pnl_pct: float
    minutes_open: int


class PositionsResponse(BaseModel):
    items: List[PositionDetail]
    total: int


# ---------------------------------------------------------------------------
# Activity feed
# ---------------------------------------------------------------------------


class ActivityEvent(BaseModel):
    """Single timeline event — open, TP hit, SL hit, invalidation."""

    kind: Literal["OPEN", "TP1", "TP2", "TP3", "SL", "INVAL", "PRE_TP"]
    title: str
    subtitle: str
    timestamp: datetime
    minutes_ago: int


class ActivityResponse(BaseModel):
    items: List[ActivityEvent]
    total: int


# ---------------------------------------------------------------------------
# Auto-mode
# ---------------------------------------------------------------------------


class AutoModeStatus(BaseModel):
    mode: Literal["off", "paper", "live"]
    open_positions: int
    daily_pnl_usd: float
    daily_loss_pct: float
    daily_kill_tripped: bool
    manual_paused: bool
    current_equity_usd: float
    simulated_pnl_usd: Optional[float] = Field(
        None, description="Paper-mode only — simulated PnL since boot"
    )


class AutoModeChangeRequest(BaseModel):
    mode: Literal["off", "paper", "live"]


class AutoModeChangeResponse(BaseModel):
    success: bool
    message: str
    mode: Literal["off", "paper", "live"]


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------


class AgentStat(BaseModel):
    """Per-evaluator counters + lifecycle stats sourced from history.

    Telemetry counters (``attempts`` / ``generated`` / ``no_signal``) reset
    on each scan-cycle window — useful for "is the gate chain doing the
    right thing".  Lifecycle counters (``closed_today`` / ``tp_hits`` /
    ``sl_hits`` / ``invalidated`` / ``last_signal_age_minutes``) come from
    ``_signal_history`` and answer "what has this agent actually shipped"
    — the question the per-agent drill-down in the app needs.
    """

    evaluator: str = Field(..., description="UPPER_SNAKE token, e.g. TREND_PULLBACK")
    setup_class: str = Field(..., description="Setup-class tag of generated signals")
    display_name: str = Field(..., description="Human-readable agent persona")
    enabled: bool
    attempts: int
    generated: int
    no_signal: int
    closed_today: int = Field(
        0,
        description="Terminal-state signals from this agent in the last 24h",
    )
    tp_hits: int = Field(0, description="TP1/TP2/TP3 hits in the last 24h")
    sl_hits: int = Field(0, description="SL hits in the last 24h")
    invalidated: int = Field(
        0,
        description="INVALIDATED / EXPIRED / CANCELLED in the last 24h",
    )
    last_signal_age_minutes: Optional[int] = Field(
        None,
        description="Minutes since this agent's most recent emission (None if never)",
    )


class AgentsResponse(BaseModel):
    items: List[AgentStat]
    total: int


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    ok: bool = True
    uptime_seconds: float
    version: str = "0.0.1"


# ---------------------------------------------------------------------------
# Tickers — live prices for the Pulse top-pair strip in the app.
# ---------------------------------------------------------------------------


class TickerItem(BaseModel):
    symbol: str
    price: float
    change_pct_24h: float = 0.0


class TickersResponse(BaseModel):
    items: List[TickerItem]
    total: int
