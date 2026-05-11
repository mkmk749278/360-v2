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
    # Rolling-window aggregates from the persistent pnl_history ledger.
    # Default to 0.0 when no history exists yet (clean install) so the
    # client can render zeros without conditional null handling.
    weekly_pnl_usd: float = Field(
        0.0, description="Realised PnL over last 7 UTC days (rolling)"
    )
    monthly_pnl_usd: float = Field(
        0.0, description="Realised PnL over last 30 UTC days (rolling)"
    )


class PnlPoint(BaseModel):
    date: str = Field(..., description="UTC date in YYYY-MM-DD")
    pnl_usd: float


class PnlHistoryResponse(BaseModel):
    mode: Literal["off", "paper", "live"]
    days: int
    items: List[PnlPoint]
    weekly_pnl_usd: float
    monthly_pnl_usd: float


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


# ---------------------------------------------------------------------------
# User settings — Pre-TP grab page
# ---------------------------------------------------------------------------


class PretpSettings(BaseModel):
    """User-controllable Pre-TP grab parameters.

    All fields optional on PUT — the API merges the partial payload into
    the stored state.  GET returns the engine's effective view (user
    overrides where set, config defaults otherwise) so the app renders
    the live state without separate calls.
    """

    enabled: Optional[bool] = Field(
        default=None,
        description="Master toggle for the Pre-TP grab feature.",
    )
    regime_allowlist: Optional[List[str]] = Field(
        default=None,
        description=(
            "Regimes in which Pre-TP may fire.  Accepts UI tokens "
            "(TRENDING / RANGING / CHOPPY) or backend tokens "
            "(TRENDING_UP / TRENDING_DOWN / RANGING / VOLATILE / QUIET); "
            "the server normalises to the backend set on write and on read."
        ),
    )
    setup_allowlist: Optional[List[str]] = Field(
        default=None,
        description=(
            "Setup classes for which Pre-TP may fire.  Reserved — "
            "the engine read-path is wired in a follow-up PR."
        ),
    )
    threshold_pct: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Static fall-back threshold for Pre-TP fire (% favourable).",
    )
    atr_multiplier: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="ATR-adaptive threshold multiplier.",
    )
    fee_floor_pct: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Minimum profit (%) before SL → breakeven.",
    )
    min_age_sec: Optional[int] = Field(
        default=None,
        ge=0,
        description="Earliest signal age (seconds) at which Pre-TP may fire.",
    )
    max_age_sec: Optional[int] = Field(
        default=None,
        ge=0,
        description="Latest signal age at which Pre-TP may still fire.",
    )


# ---------------------------------------------------------------------------
# User settings — Auto-trade page
# ---------------------------------------------------------------------------


class AutoTradeSettings(BaseModel):
    """User-controllable auto-execution and sizing parameters.

    All fields optional on PUT — the API merges the partial payload into
    the stored state.  GET returns the engine's effective view (user
    overrides where set, config defaults otherwise).
    """

    mode: Optional[Literal["off", "paper", "live"]] = Field(
        default=None,
        description="Execution mode.  Mirrors `/api/auto-mode`'s POST shape; "
        "this endpoint is the settings-page counterpart that GET-bundles "
        "mode with sizing params.",
    )
    position_size_pct: Optional[float] = Field(
        default=None,
        gt=0.0,
        le=100.0,
        description="Position size as % of paper equity per trade.",
    )
    leverage_cap: Optional[float] = Field(
        default=None,
        gt=0.0,
        le=30.0,  # B12 hard cap.
        description="Hard leverage cap (RiskManager).  Server clamps to ≤ 30.",
    )
    max_concurrent_positions: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum concurrent open positions across all symbols.",
    )


# ---------------------------------------------------------------------------
# Phone-OTP auth (Phase 2)
# ---------------------------------------------------------------------------


class OtpRequest(BaseModel):
    """Body of ``POST /api/auth/request-otp``."""

    phone: str = Field(
        ...,
        min_length=8,
        max_length=18,
        description="E.164 phone number, including leading ``+``.",
    )


class OtpRequestResponse(BaseModel):
    """Response from ``POST /api/auth/request-otp``.

    ``channel_used`` lets the app render the right UI hint ("check
    WhatsApp" vs "check SMS").  ``expires_in_seconds`` drives the
    countdown on the verify screen.  Don't leak which providers the
    user lacks beyond the single channel hint.
    """

    channel_used: Literal["whatsapp", "sms", "log"]
    expires_in_seconds: int


class OtpVerify(BaseModel):
    """Body of ``POST /api/auth/verify-otp``."""

    phone: str = Field(..., min_length=8, max_length=18)
    code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6-digit numeric code.",
    )


# ---------------------------------------------------------------------------
# User profile (Phase 3 — per-user expansion)
# ---------------------------------------------------------------------------


class ProfileResponse(BaseModel):
    """Body of ``GET /api/profile``.

    Mirrors the user row + a derived ``needs_onboarding`` so the app
    doesn't have to interpret ``onboarded_at`` directly.  ``phone_e164``
    is included so the SignupPage can pre-fill the country chip from
    the leading prefix as a sanity check against the auto-detect.
    """

    user_id: int
    phone_e164: str
    tier: str
    paid_until: Optional[str] = None  # ISO-8601 UTC; null when not paid
    display_name: Optional[str] = None
    country_code: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    terms_accepted_at: Optional[str] = None
    onboarded_at: Optional[str] = None
    needs_onboarding: bool


class ProfileUpdate(BaseModel):
    """Body of ``PUT /api/profile``.

    All fields optional — partial updates are allowed.  First update
    with ``display_name`` set and ``accept_terms=True`` flips the
    user's ``onboarded_at`` to NOW(), which is the single signal the
    app reads to decide whether to route to SignupPage on next signin.

    Country / timezone / currency are user-editable on the signup form
    (auto-detected from device locale, but the user can change).  The
    server treats them as opaque strings and persists what the client
    sends — validation lives on the client where the picker enforces
    the ISO alphabets.  Server-side defence is acceptable to skip:
    these values feed only the user's own display, not engine logic.
    """

    display_name: Optional[str] = Field(default=None, min_length=1, max_length=64)
    country_code: Optional[str] = Field(default=None, min_length=2, max_length=2)
    timezone: Optional[str] = Field(default=None, max_length=64)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    accept_terms: bool = False


# ---------------------------------------------------------------------------
# Billing webhook (Phase 2 — bot/billing-platform → engine)
# ---------------------------------------------------------------------------


class BillingGrantRequest(BaseModel):
    """Body of ``POST /internal/billing/grant``.

    ``paid_until_iso`` is an ISO-8601 UTC timestamp; ``None`` means the
    grant is being **revoked** (tier downgraded to free).  The server
    parses this to a datetime and stores it in the user row.  HMAC
    verification on the raw body happens before this schema is applied.
    """

    phone: str = Field(..., min_length=8, max_length=18)
    tier: Literal["free", "paid", "owner"]
    paid_until_iso: Optional[str] = Field(
        default=None,
        description="ISO-8601 UTC; null when revoking (downgrade to free).",
    )


class BillingGrantResponse(BaseModel):
    ok: bool
    user_id: int
    tier: str
