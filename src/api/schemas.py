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


class PositionDiagDetail(BaseModel):
    """Operator-facing position diagnostic — superset of ``PositionDetail``.

    Surfaces what ``TradeMonitor._evaluate_signal`` is *actually* comparing
    against (the engine's view of the 1m candle wick + last tick) so the
    operator can confirm whether a position that hit SL on Binance but still
    reads ACTIVE in the engine is (a) a stale candle feed, (b) a monitor
    evaluation bug, or (c) a state-store sync gap.
    """

    signal_id: str
    symbol: str
    direction: Literal["LONG", "SHORT"]
    status: str
    setup_class: str
    channel: str

    # Stored geometry at signal creation
    entry: float
    stop_loss: float
    tp1: float
    tp2: float
    tp3: Optional[float] = None

    # Engine's live view
    current_price: float
    pnl_pct: float
    max_favorable_excursion_pct: float
    max_adverse_excursion_pct: float
    best_tp_hit: int
    pre_tp_hit: bool

    # What the monitor evaluates against
    candle_1m_high: float
    candle_1m_low: float
    candle_1m_age_sec: Optional[float] = None

    # Diag-derived: distance from worst-side wick to SL (signed, in %-of-entry).
    # LONG:  (candle_1m_low  - stop_loss) / entry * 100  → negative means wick already past SL
    # SHORT: (stop_loss - candle_1m_high) / entry * 100  → negative means wick already past SL
    # A row with status == "ACTIVE" and sl_breach_distance_pct <= 0 is a smoking gun
    # that the monitor failed to mark the signal SL_HIT.
    sl_breach_distance_pct: Optional[float] = None

    # Lifecycle stamps
    minutes_open: int
    timestamp: Optional[datetime] = None
    dispatch_timestamp: Optional[datetime] = None
    first_sl_touch_timestamp: Optional[datetime] = None
    first_tp_touch_timestamp: Optional[datetime] = None
    terminal_outcome_timestamp: Optional[datetime] = None


class PositionsDiagResponse(BaseModel):
    items: List[PositionDiagDetail]
    total: int
    monitor_running: bool
    generated_at: datetime


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
    grab_fraction: Optional[float] = Field(
        default=None,
        ge=0.30,
        le=1.00,
        description=(
            "OWNER_BRIEF B17 — fraction of the position to close at market when "
            "Pre-TP threshold hits.  Hard floor 30% (no user can collapse to the "
            "pre-2026-05-17 SL-to-BE-only behaviour); 100% ceiling (fully bank "
            "the partial, leave nothing riding).  Engine default 50%.  The "
            "residual position has SL ratcheted to entry."
        ),
    )


# ---------------------------------------------------------------------------
# User settings — Invalidation page (OWNER_BRIEF B17, 2026-05-17)
# ---------------------------------------------------------------------------


class InvalidationSettings(BaseModel):
    """User-controllable invalidation aggressiveness parameters (B17).

    Three preset modes (``loose`` / ``standard`` / ``tight``) cover the
    common cases.  The remaining fields are advanced-section overrides for
    users who want fine control without committing to a preset; NULL means
    "use the preset's value for this knob".

    Tight mode adds an ATR-trailing kill at ``MFE >= trailing_mfe_r_threshold``
    that closes the signal at market when price retraces ``trailing_retrace_pct``
    of the MFE peak — the capital-preservation engine that prevents the
    cohort of MFE-positive signals from sliding all the way to full SL.

    All fields optional on PUT — the API merges into the stored partial.
    """

    mode: Optional[str] = Field(
        default=None,
        description=(
            "Preset aggressiveness.  ``loose`` = only kill when thesis is "
            "irrefutably broken (regime flip AND EMA crossover both fire); "
            "``standard`` = current engine behaviour + MFE-protection on "
            "momentum kills (default); ``tight`` = standard + ATR-trailing "
            "kill at MFE >= 0.3R."
        ),
    )
    min_age_sec: Optional[int] = Field(
        default=None,
        ge=0,
        description="Earliest signal age at which invalidation may fire.",
    )
    momentum_threshold_mult: Optional[float] = Field(
        default=None,
        ge=0.0,
        description=(
            "Multiplier applied to the engine's ATR-adaptive momentum threshold. "
            "<1.0 = more sensitive (kill earlier); >1.0 = less sensitive."
        ),
    )
    ema_crossover_enabled: Optional[bool] = Field(
        default=None,
        description="Whether 5m EMA9/EMA21 cross-against-thesis triggers a kill.",
    )
    regime_shift_enabled: Optional[bool] = Field(
        default=None,
        description="Whether a regime flip opposing direction triggers a kill.",
    )
    trailing_kill_enabled: Optional[bool] = Field(
        default=None,
        description=(
            "Whether the ATR-trailing kill is active (tight-mode signature)."
        ),
    )
    trailing_mfe_r_threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        description=(
            "MFE threshold (as a multiple of SL distance) above which the "
            "ATR-trailing kill becomes armed.  Default 0.3R per B17."
        ),
    )
    trailing_retrace_pct: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Retracement fraction of the MFE peak at which the trailing kill "
            "fires.  Default 0.50 (50% retrace) per B17."
        ),
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
# Per-user setting overrides (Phase 2 of per-user expansion)
# ---------------------------------------------------------------------------


class UserPretpSettings(PretpSettings):
    """Per-user Pre-TP overrides — same fields as :class:`PretpSettings`
    plus a ``using_defaults`` flag so the app can render a "Custom
    settings" badge and offer a Reset-to-defaults action.

    Identical wire schema (subclass adds one field), so the app's
    existing ``PretpSettings`` data class can deserialise this with a
    single optional-field addition.
    """

    using_defaults: bool = Field(
        default=True,
        description="True when the user has no override row — every "
        "value above is the engine default.  False when at least one "
        "field has been overridden.",
    )


class UserAutoTradeSettings(AutoTradeSettings):
    """Per-user auto-trade overrides — same shape as
    :class:`AutoTradeSettings` plus ``using_defaults``.

    Phase 2: the engine itself does not consume per-user mode /
    position_size_pct / leverage_cap.  Values are stored for Phase 3
    when the user's app fires their own Binance order using these
    values for sizing.  The app surfaces this with an honest banner.
    """

    using_defaults: bool = Field(
        default=True,
        description="True when the user has no override row.",
    )


class UserInvalidationSettings(InvalidationSettings):
    """Per-user invalidation overrides (OWNER_BRIEF B17) — same shape as
    :class:`InvalidationSettings` plus ``using_defaults``.

    The engine does not consume per-user invalidation values in this PR —
    schema + API only.  PR #4 (``feat/invalidation-user-modes``) wires
    the engine read path.  Storing per-user values here unblocks the
    Lumin invalidation-settings page (PR L2) to be built in parallel.
    """

    using_defaults: bool = Field(
        default=True,
        description="True when the user has no override row.",
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

    channel_used: Literal["whatsapp", "sms", "log", "telegram"]
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


# ---------------------------------------------------------------------------
# Telegram-OTP → Firebase custom-token bridge (Phase 4)
# ---------------------------------------------------------------------------


class TelegramOtpIssueRequest(BaseModel):
    """Body of ``POST /api/auth/telegram-otp/issue``.

    Issues a fresh OTP for ``phone_e164`` and forces delivery via
    @LuminProBot — no SMS / WhatsApp fall-through.  Paired with
    :class:`TelegramOtpVerifyRequest` (added in #398) to complete the
    Telegram-OTP → Firebase custom-token bridge described in
    ``docs/firebase_auth_migration.md``.

    Field constraints match :class:`TelegramOtpVerifyRequest` and the
    legacy :class:`OtpRequest` exactly so the Lumin app can reuse a
    single client-side validator across the whole flow.
    """

    phone_e164: str = Field(
        ...,
        min_length=8,
        max_length=18,
        description="E.164 phone number, including leading ``+``.",
    )


class TelegramOtpIssueResponse(BaseModel):
    """Response from ``POST /api/auth/telegram-otp/issue``.

    ``status`` is always ``"ok"`` on a 2xx response — rate-limit and
    delivery failures surface as HTTP errors with structured ``detail``
    strings so the Lumin app's existing error handler (already wired
    against :class:`OtpRequestResponse` for the legacy SMS path) treats
    both halves of the flow the same way.  ``expires_in_seconds`` drives
    the verify-screen countdown.
    """

    status: Literal["ok"] = "ok"
    expires_in_seconds: int


class TelegramOtpVerifyRequest(BaseModel):
    """Body of ``POST /api/auth/telegram-otp/verify``.

    The Telegram-OTP fallback path: the bot already DM'd a 6-digit code
    to the user's bound chat_id; the app POSTs it here.  On success the
    engine registers the user with Firebase Admin (idempotent on phone)
    and returns a Firebase custom token the app exchanges for a real
    Firebase session via ``signInWithCustomToken``.
    """

    phone_e164: str = Field(..., min_length=8, max_length=18)
    code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6-digit numeric code from the Telegram bot DM.",
    )


class TelegramOtpVerifyResponse(BaseModel):
    """Response from ``POST /api/auth/telegram-otp/verify``.

    ``custom_token`` is single-use — the app calls
    ``signInWithCustomToken`` immediately to land a Firebase session.
    The user/tier fields let the app render the initial state without a
    second round-trip to ``/api/profile``.
    """

    custom_token: str
    user_id: int
    tier: str
    paid_until: Optional[str] = None  # ISO-8601 UTC; null when not paid
    needs_onboarding: bool


# ---------------------------------------------------------------------------
# Per-trade records (paper-trade visibility — 2026-05-16)
# ---------------------------------------------------------------------------


class TradePartialFill(BaseModel):
    """One TP-level fill on the way to a fully-closed trade.

    Surfaced inside ``TradeRecord.partial_fills`` so the app's trade-
    detail view can show TP1/TP2/TP3 hit prices + the proportional
    PnL each fill contributed.  Helps subscribers see "the strategy
    locked +0.5% at TP1, the rest stopped out at SL" rather than only
    the net result.
    """

    tp_level: int = Field(..., description="TP slot (1, 2, 3) or 0 for ad-hoc partial")
    fraction: float = Field(..., description="Fraction of total qty closed by this fill")
    fill_price: float
    pnl_usd: float = Field(..., description="Net PnL booked by this fill (after fees)")
    fee_usd: float = Field(..., description="Total fee paid on this fill (entry-share + exit)")
    ts: str = Field(..., description="ISO-8601 UTC timestamp of the fill")


class TradeRecord(BaseModel):
    """One paper-trade lifecycle row from ``data/paper_trades.sqlite``.

    Snapshot of leverage + position_size_pct AT OPEN so a later
    settings-page change doesn't retroactively rewrite the row.
    ``roi_pct_on_margin = net_pnl_usd / margin_usd * 100`` — the
    headline metric subscribers care about (a $1 PnL on $10 of
    margin at 10x = +10% ROI, not +0.1% on the underlying).
    """

    id: int
    signal_id: str
    symbol: str
    side: Literal["long", "short"]
    entry: float
    qty: float
    leverage: float
    position_size_pct: float
    notional_usd: float
    margin_usd: float
    partial_fills: List[TradePartialFill] = Field(default_factory=list)

    # Close-state fields — null while the trade is still open.
    close_reason: Optional[str] = None
    close_price: Optional[float] = None
    gross_pnl_usd: Optional[float] = None
    fees_usd: Optional[float] = None
    net_pnl_usd: Optional[float] = None
    roi_pct_on_margin: Optional[float] = None

    created_at: str = Field(..., description="ISO-8601 UTC at open")
    closed_at: Optional[str] = Field(
        None, description="ISO-8601 UTC at full close; null when still open"
    )


class TradeListResponse(BaseModel):
    """Response shape for ``GET /api/trades``.

    ``total`` is the count after filters but before pagination — the
    app uses it to compute total pages for the history list.
    """

    items: List[TradeRecord]
    total: int


# ---------------------------------------------------------------------------
# Paper-mode reset (owner-only) — 2026-05-16
# ---------------------------------------------------------------------------


class PaperResetResponse(BaseModel):
    """Response shape for ``POST /api/auto-mode/paper/reset``.

    ``starting_equity_usd`` echoes the configured starting balance so
    the app can render "Balance reset to $X.XX as of <reset_at>" without
    re-fetching the auto-mode status.  ``trades_archived`` is the count
    of per-trade rows moved into the timestamped archive table —
    purely informational; 0 means it was a fresh session.
    """

    reset_at: str = Field(..., description="ISO-8601 UTC of the reset event")
    starting_equity_usd: float
    pnl_buckets_cleared: int = Field(
        0, description="Daily buckets wiped from the paper pnl_history ledger"
    )
    trades_archived: int = Field(
        0, description="Per-trade rows archived to paper_trades_archive_<ts>"
    )


# ---------------------------------------------------------------------------
# Paper-mode close-all-positions (user-initiated) — follow-up to PR #401
# ---------------------------------------------------------------------------


class PaperCloseAllResponse(BaseModel):
    """Response shape for ``POST /api/auto-mode/paper/close-all``.

    The user-facing "flatten my paper book" action.  Companion to (but
    intentionally NOT part of) ``POST /api/auto-mode/paper/reset``:
    the reset doctrine preserves in-flight signals for live-broker
    safety, so users need a separate explicit action to close every
    open paper position before invoking reset.  Two-step flow:
    ``close-all`` → optional ``reset``.

    ``closed_count`` is the number of positions actually closed by this
    call — zero on a flat book (the action is idempotent).
    ``realised_pnl_total`` is the **sum of PnL booked by this batch**
    of closes only; cumulative paper PnL since boot remains exposed
    via ``AutoModeStatus.simulated_pnl_usd``.
    """

    ok: bool = True
    closed_count: int = Field(
        ..., description="Number of paper positions closed by this call"
    )
    realised_pnl_total: float = Field(
        ...,
        description=(
            "Sum of realised PnL (USD) booked by this batch of closes — "
            "fees only on a zero-move flatten; cumulative since boot lives "
            "on AutoModeStatus.simulated_pnl_usd"
        ),
    )
