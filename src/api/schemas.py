"""Pydantic schemas for the Lumin app API.

Schema names mirror the Dart classes in ``lib/data/mock_data.dart`` so the
client can deserialize without a translation layer.  When a field's name
has to differ from the engine's internal attribute (for example to match
the Dart camelCase or a more user-friendly label), the difference is
documented inline.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

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
    original_stop_loss: float = Field(
        0.0,
        description=(
            "The protective stop the signal was issued with, before any "
            "break-even / trailing shift. ``stop_loss`` is mutated in place as "
            "the trade progresses (→ entry on TP1/BE, → tp1 later), so consumers "
            "that need the *original* risk geometry — e.g. a held-to-stop "
            "replay — must use this. Falls back to the current stop_loss when "
            "the original distance was never recorded (0.0)."
        ),
    )
    tp1: float
    tp2: float
    tp3: Optional[float] = None
    confidence: float
    quality_tier: str
    setup_class: str
    agent_name: str = Field(..., description="Display name of the evaluator")
    status: str
    is_open: bool = Field(
        False,
        description=(
            "True while the signal is genuinely in-flight (still in the "
            "engine's active book with a non-terminal status). The status "
            "string alone can no longer distinguish open from closed: under "
            "the BE-then-TP1 default a non-mover CLOSES with status TP1_HIT, "
            "while under the mover runner exit (2026-07-09) a mover with "
            "status TP1_HIT/TP2_HIT is still OPEN with the trail riding the "
            "remainder. Clients must use this field for open/closed "
            "rendering, sorting, and 'held vs open' labels."
        ),
    )
    current_price: float
    pnl_pct: float
    max_favorable_excursion_pct: float = Field(
        0.0,
        description=(
            "Peak unrealised profit %, measured from entry, that this signal "
            "reached at any point in its life (max favorable excursion). For "
            "closed signals this is the best the trade ever showed before its "
            "terminal exit; for active signals it tracks the running peak."
        ),
    )
    max_adverse_excursion_pct: float = Field(
        0.0,
        description=(
            "Worst unrealised drawdown %, measured from entry, the signal "
            "reached (max adverse excursion). Reported as a signed value "
            "matching pnl_pct's sign convention (negative = against the trade)."
        ),
    )
    best_tp_pnl_pct: float = Field(
        0.0,
        description=(
            "Locked profit % at the highest TP level hit so far, calculated at "
            "the exact TP price (not the current price). After TP1 this holds the "
            "TP1 result; after TP2 it holds the TP2 result. 0.0 when no TP has "
            "been hit yet. Use this to display the 'banked' result for TP-hit "
            "signals while max_favorable_excursion_pct tracks the continuing peak."
        ),
    )
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
    minutes_ago: int = Field(
        ...,
        description=(
            "Recency of the signal's LAST event, for an 'N ago' label — NOT its "
            "age. Closed signals measure from the terminal event, active ones "
            "from dispatch. Never reconstruct a point in time from this: "
            "``now - minutes_ago`` lands on the exit for every closed signal. "
            "Use ``timestamp`` / ``dispatch_timestamp`` / "
            "``terminal_outcome_timestamp`` — the app drew its chart ENTRY "
            "marker at the exit for months on exactly this mistake "
            "(owner-caught 2026-07-29)."
        ),
    )
    dispatch_timestamp: Optional[datetime] = Field(
        None,
        description=(
            "When the signal was dispatched to subscribers — the moment a "
            "reader could have acted on it. None on records that predate the "
            "stamp."
        ),
    )
    terminal_outcome_timestamp: Optional[datetime] = Field(
        None,
        description=(
            "When the signal reached its terminal state (SL_HIT / TP / "
            "invalidation). None while the signal is still open, and on "
            "closed records that predate the stamp — the two are different "
            "states and a consumer must not pool them."
        ),
    )
    hold_mins: Optional[int] = Field(
        None,
        description=(
            "Closed signals: dispatch→terminal duration in minutes (actual hold time). "
            "Active signals: minutes since dispatch (trade age). "
            "None when dispatch_timestamp is unavailable."
        ),
    )
    entry_regime: str = Field(
        "",
        description=(
            "5m regime label stamped on the signal at entry (TRENDING_UP / "
            "TRENDING_DOWN / RANGING / VOLATILE / QUIET). Empty when the regime "
            "context was unavailable. Surfaced so analytics (Profit-Lab regime "
            "breakdown + the combo analyzer, §3.2b regime-per-exit research) can "
            "slice performance by the same regime the FSM uses to route exits."
        ),
    )
    entry_regime_15m: str = Field(
        "",
        description="15m stateless regime label at entry (HTF confirmation for runners).",
    )
    pair_admission: str = Field(
        "",
        description=(
            "How the pair entered the scan set when this signal fired: CORE "
            "(top-N by 24h volume), MOVER_IGNITION (real-time !ticker@arr "
            "burst), MOVER_TOP24H (sustained 24h %-move), SURGE (volume-surge "
            "promotion). Empty for signals stamped before 2026-07-30. Promoted "
            "pairs are the majority of the delivered book and this is the only "
            "field that says so — the promotion expires long before the signal "
            "closes, so it cannot be recovered later."
        ),
    )
    market_phase: str = Field(
        "",
        description=(
            "Human-readable regime context at entry "
            "(e.g. 'TRENDING_UP | ATR%ile=72 | Vol=expanding'). "
            "Leading token is the regime label."
        ),
    )


class SignalsResponse(BaseModel):
    items: List[SignalDetail]
    total: int


# ---------------------------------------------------------------------------
# Market Alerts (Pulse → Alerts feed)
# ---------------------------------------------------------------------------


class AlertItem(BaseModel):
    """One informational detector event — mirrors Dart ``MarketAlert``."""

    alert_id: str
    alert_type: str = Field(
        ...,
        description=(
            "Detector taxonomy value (RSI_OVERBOUGHT / RSI_OVERSOLD / "
            "RSI_BULLISH_DIVERGENCE / RSI_BEARISH_DIVERGENCE / "
            "ABNORMAL_VOLATILITY / VOLUME_SPIKE / NEAR_SUPPORT / "
            "NEAR_RESISTANCE). The app maps these to icons/colours."
        ),
    )
    symbol: str
    timeframe: str = Field(..., description="Natural detector timeframe (15m / 1h / 4h).")
    price: float = Field(..., description="Close price when the alert fired.")
    title: str
    message: str
    bias: str = Field("NEUTRAL", description="Directional lean: BULLISH / BEARISH / NEUTRAL.")
    metrics: dict = Field(default_factory=dict)
    created_at: str


class AlertsResponse(BaseModel):
    items: List[AlertItem]
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


class TrackRecordSummary(BaseModel):
    """Aggregate over one selected population — the whole window, or one day.

    Two denominators, deliberately both present. ``n`` is every trade the
    window selected; ``n_pnl`` is those carrying a readable ``pnl_pct``, and it
    is what every figure below divides by. They are normally identical, and a
    client that shows one figure without the other cannot say when they are
    not — which is exactly how R described 6% of the ops track record for six
    days while looking like the book.

    There is deliberately **no R anywhere in this response**. ``signal_dispatch``
    sizes at a fixed notional, so the stop distance is absent from the sizing
    and R equalises nothing; and it silently drops every row with no entry-risk
    stamp, which is most of them. PnL needs no denominator.
    """

    n: int = Field(0, description="Trades selected")
    moves: int = Field(
        0,
        description="Distinct moves those trades describe. Overlapping entries "
        "into one move exit at the same price and are not independent "
        "evidence. Disclosure only — nothing is de-duplicated.",
    )
    n_pnl: int = Field(0, description="Trades with a readable pnl_pct — the denominator")
    no_pnl: int = Field(0, description="Trades excluded from every money figure")
    wins: int = Field(0, description="Trades profitable NET of the round-trip fee")
    losses: int = 0
    win_rate: Optional[float] = Field(None, description="wins / n_pnl, 0..1")
    gross_usd: Optional[float] = Field(None, description="At amount_usdt, before fees")
    fee_usd: Optional[float] = None
    net_usd: Optional[float] = None
    total_pnl_pct: Optional[float] = Field(
        None, description="Sum of per-trade gross %. Fixed size, no compounding."
    )
    avg_pnl_pct: Optional[float] = None
    total_net_pct: Optional[float] = None
    avg_net_pct: Optional[float] = None
    best_pnl_pct: Optional[float] = Field(None, description="Gross — fee not charged twice")
    worst_pnl_pct: Optional[float] = None


class TrackRecordDay(TrackRecordSummary):
    """One UTC calendar day of closed trades, plus the running curve.

    ``partial_reason`` is ``in_progress`` on the day containing "now" and null
    on every finished day. A part-period rendering as a whole one flipped a
    sign on the ops page once; a client must be able to badge the live day
    rather than let it read as a finished one.
    """

    date: str = Field(..., description="UTC date, YYYY-MM-DD")
    partial_reason: Optional[str] = Field(
        None, description="'in_progress' for today; null for a finished day"
    )
    cum_net_usd: float = Field(0.0, description="Running net from the window's start")
    cum_net_pct: float = 0.0


class TrackRecordResponse(BaseModel):
    """The recorded delivered-signal book — NOT the caller's own paper book.

    Every row behind this is a signal the router confirmed and ``trade_monitor``
    tracked forward in real time. Nothing is replayed or reconstructed.

    It is pooled across every subscriber and sized at one fixed notional, so it
    is a different population from ``/api/pnl/history`` (per-user, per-user
    preferences, compounding, TP partials booked separately). The two are not
    reconcilable and a client must never present them as the same book.
    """

    enabled: bool = Field(
        True, description="False when the owner has switched the public record off"
    )
    unavailable_reason: str = Field(
        "",
        description="'' when the book rendered. 'disabled' | 'missing' | "
        "'unreadable' | 'unexpected_shape' otherwise — a blank needs a cause, "
        "and these have different fixes.",
    )
    days: int
    amount_usdt: float = Field(
        ..., description="The notional every dollar figure assumes — an input, never hidden"
    )
    fee_pct: float = Field(..., description="Round trip, both legs, % of notional")
    range_start: str = Field(..., description="First UTC day included, YYYY-MM-DD")
    generated_at: str
    total_records: int = Field(0, description="Whole ledger, before the window")
    undateable: int = Field(0, description="Ledger rows with no usable close time")
    summary: TrackRecordSummary
    items: List[TrackRecordDay] = Field(
        default_factory=list,
        description="Oldest first. Days with no close are ABSENT, not zero — "
        "nothing closed is not a flat day.",
    )


class TrackRecordSignal(BaseModel):
    """One closed signal behind the daily buckets — the drill-down row.

    A headline nobody can open is a claim rather than a record, so a reader who
    sees a red day can ask which signals made it red.

    ``pnl_pct`` is null where the outcome could not be read. The row is still
    listed: it is part of what closed that day, and dropping it would make the
    list disagree with the count above it.
    """

    signal_id: str = ""
    symbol: str = ""
    direction: str = ""
    setup: str = ""
    regime: str = Field(
        "", description="Regime at ENTRY. 'UNPLACED' where the engine had not "
        "yet stamped it — knowable only at entry, so never backfilled."
    )
    outcome: str = Field("", description="Terminal label, e.g. TP1_HIT / SL_HIT")
    entry: Optional[float] = None
    closed_at: str = Field("", description="ISO-8601 UTC")
    pnl_pct: Optional[float] = Field(None, description="Gross move")
    net_pct: Optional[float] = Field(None, description="After the round trip")
    net_usd: Optional[float] = Field(None, description="At amount_usdt")


class TrackRecordSignalsResponse(BaseModel):
    """The per-signal list for a window, or for one UTC day.

    ``truncated`` says the render cap bit. The cap is applied **after**
    filtering: truncating first starves the rarest population hardest, which is
    how "delivered to users" once silently meant "delivered, within the newest
    300" of a 2,000-row ledger.
    """

    enabled: bool = True
    unavailable_reason: str = ""
    days: int = 30
    date: str = Field("", description="YYYY-MM-DD when narrowed to one day")
    amount_usdt: float = 100.0
    fee_pct: float = 0.07
    matched: int = Field(0, description="Rows the filter selected, before the cap")
    truncated: bool = False
    items: List[TrackRecordSignal] = Field(default_factory=list)


class AutoModeChangeRequest(BaseModel):
    mode: Literal["off", "paper", "live"]


class AutoModeChangeResponse(BaseModel):
    success: bool
    message: str
    mode: Literal["off", "paper", "live"]


class AutoModeResumeMineResponse(BaseModel):
    """Response shape for ``POST /api/auto-mode/resume-mine``.

    ``resumed`` is True when an auto-pause was actually cleared,
    False when the user wasn't paused (idempotent no-op path).
    The app uses the bool to decide whether to show a success
    toast vs a silent dismiss.
    """

    resumed: bool


class KillSwitchState(BaseModel):
    """Global kill-switch state (OWNER_BRIEF B18 emergency halt).

    ``engaged`` True = ALL auto-trade is halted engine-wide until
    manually disengaged.  ``initialised`` False means the kill-switch
    client never booted (no Firestore / GCP creds) — the control plane
    renders an "unavailable" state rather than a misleading "off".
    """

    engaged: bool
    reason: Optional[str] = None
    initialised: bool = True


class KillSwitchSetRequest(BaseModel):
    """Owner request to flip the global kill switch.

    ``engaged`` True engages (halts everything); False disengages
    (resumes).  ``reason`` is recorded on engage for operator
    visibility (shown in the ops control plane + status reads)."""

    engaged: bool
    reason: Optional[str] = Field(
        default=None,
        max_length=280,
        description="Operator note recorded on engage (why we halted).",
    )


class AutoTradeGlobalState(BaseModel):
    """Global ``auto_trade_globally_enabled`` flag (OWNER_BRIEF §3.9 / B18).

    Distinct from the kill switch: ``enabled`` False halts *new* order
    placement engine-wide (existing Binance positions are untouched —
    that's the kill switch's job).  Default ships False (#431 blast-radius
    cap).  ``initialised`` False = the flag's Firestore client never booted.
    """

    enabled: bool
    initialised: bool = True


class AutoTradeGlobalSetRequest(BaseModel):
    """Owner request to flip the global auto-trade-enabled flag."""

    enabled: bool


class SignalExpiryState(BaseModel):
    """Time-based signal-expiry backstop toggle (owner decision 2026-06-26).

    When ``enabled`` is False (default), signals run to TP or SL only — the
    MAX_SIGNAL_HOLD_SECONDS max-hold force-close is disabled, so a signal
    never expires mid-move. The 2h auto-trade reconciler stale-close safety
    net is independent and unaffected. ``initialised`` False = the
    kill-switch Firestore client (which stores the flag) never booted, so
    the engine is running on the env boot default.
    """

    enabled: bool
    initialised: bool = True


class SignalExpirySetRequest(BaseModel):
    """Owner request to flip the signal-expiry backstop."""

    enabled: bool


class PlayBillingEnabledState(BaseModel):
    """Google Play subscription paywall master switch (ops control, 2026-07-16).

    ``enabled`` False → the verify + RTDN endpoints 503 ("play billing
    disabled"); existing tiers in UserStore are untouched (they expire
    naturally at ``paid_until``). ``configured`` False → no package /
    service account, so billing 503s regardless of ``enabled``.
    ``initialised`` False = the flag's Firestore client never booted, so the
    engine runs on the GOOGLE_PLAY_BILLING_ENABLED env default.
    """

    enabled: bool
    configured: bool = False
    initialised: bool = True


class PlayBillingEnabledSetRequest(BaseModel):
    """Owner request to turn the Play billing paywall on/off engine-wide."""

    enabled: bool


class TunableEntry(BaseModel):
    """One runtime tunable: registry metadata + current effective value."""

    key: str
    label: str
    description: str
    type: str
    default: Any
    value: Any
    min: Optional[float] = None
    max: Optional[float] = None
    unit: str = ""
    category: str
    #: Closed set of valid values for a ``str`` tunable, or None for free text.
    #: Ops renders a select when present — a two-valued setting shipped as a
    #: text box is how ``trail_governor_timeframe`` got stored as "5".
    choices: Optional[list[str]] = None


class TunablesState(BaseModel):
    """Runtime-tunables snapshot for the ops panel.

    ``initialised`` False = Firestore isn't wired in this process, so the
    engine is running on env boot defaults and writes are unavailable.
    """

    initialised: bool
    tunables: List[TunableEntry]


class TunablesSetRequest(BaseModel):
    """Owner request to update one or more runtime tunables."""

    values: Dict[str, Any]


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
    engine_connected: bool = Field(
        True,
        description=(
            "Isolated mode: whether this API container has heard from the "
            "engine recently (``snapshot:engine_state`` refreshed within "
            "API_ENGINE_STALE_SEC). False means the engine container is dead, "
            "wedged, or cut off from Redis — everything this API serves is "
            "then last-known-good, not live. Always true in single-process "
            "mode, where the engine IS this process. This is the field the "
            "ops agent pages on: it is derived from *when Redis last "
            "answered*, so unlike every other engine-derived value it cannot "
            "be faked by a frozen snapshot."
        ),
    )
    engine_state_age_seconds: Optional[float] = Field(
        None,
        description=(
            "Seconds since this container last read a decodable "
            "``snapshot:engine_state``. ``null`` in single-process mode (the "
            "question does not apply) and when the engine has never been "
            "reachable since API start — ``engine_connected`` disambiguates."
        ),
    )


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
        ge=0.0,
        le=1.00,
        description=(
            "OWNER_BRIEF B17 — fraction of the position to close at market when "
            "Pre-TP threshold hits.  Session 34: 0.0 = pre-TP DISABLED (the "
            "engine default — exit is TP1-full + fixed SL).  Any positive opt-in "
            "is clamped server-side into the B17 [0.30, 1.00] band (no user "
            "sits in the dead 0<x<0.30 zone).  100% = fully bank, nothing "
            "riding.  A non-zero residual has its SL ratcheted to entry."
        ),
    )
    protect_manual_entries: Optional[bool] = Field(
        default=None,
        description=(
            "OWNER_BRIEF B17 (2026-05-17) — when True, the app-side "
            "AutoTradeWatcher keeps polling for pre-TP partial closes on "
            "manually-taken entries even when auto-trade ``mode == 'off'``.  "
            "Default True extends capital-preservation doctrine to manual "
            "operators (the most engaged subscriber cohort).  False respects "
            "'off means off' for users who want pure manual control with no "
            "background broker activity.  NULL = use engine default (True)."
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

    mode: Optional[Literal["off", "paper", "live", "both"]] = Field(
        default=None,
        description=(
            "Execution mode.  ``'live'`` dispatches real Binance Futures orders. "
            "``'paper'`` runs simulated fills only.  ``'both'`` does both "
            "simultaneously — live orders fire AND paper simulation runs for "
            "side-by-side comparison.  ``'off'`` disables everything."
        ),
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
    symbol_preference: Optional[list[str]] = Field(
        default=None,
        description=(
            "User-chosen subset of the engine-wide symbol allowlist.  "
            "``None`` means 'all engine-allowed symbols' (default — no "
            "narrowing).  Non-empty list means 'only these symbols may "
            "auto-trade for me'.  The engine intersects this with its "
            "own ``TRIPWIRE_SYMBOL_ALLOWLIST`` cap — per-user values can "
            "only narrow, never widen, per OWNER_BRIEF B18."
        ),
    )
    path_preference: Optional[list[str]] = Field(
        default=None,
        description=(
            "User-chosen subset of evaluator paths (setup classes) eligible "
            "to auto-trade LIVE for this user — the path analogue of "
            "``symbol_preference``.  ``None`` = all paths (default, no "
            "narrowing).  Non-empty list = 'only these paths may auto-trade "
            "for me'.  Empty list = block all.  Consumed at live dispatch "
            "(``dispatch_signal_to_active_users``); the signal is still "
            "delivered to Telegram / Pulse regardless."
        ),
    )
    regime_preference: Optional[list[str]] = Field(
        default=None,
        description=(
            "User-chosen subset of entry regimes eligible to auto-trade "
            "LIVE.  Accepts the UI tokens TRENDING / RANGING / CHOPPY, which "
            "the server normalises onto backend regime labels "
            "(TRENDING_UP/DOWN, RANGING, VOLATILE, QUIET).  ``None`` = all "
            "regimes (default).  Non-empty list = 'only these regimes may "
            "auto-trade for me'.  Empty list = block all."
        ),
    )
    paper_symbol_preference: Optional[list[str]] = Field(
        default=None,
        description=(
            "PAPER counterpart of ``symbol_preference`` — the user-chosen "
            "subset of symbols eligible to auto-trade in PAPER simulation. "
            "Independent of the live triple, so a user can paper-test one "
            "symbol set while live-trading another.  ``None`` = all symbols "
            "(default); non-empty list = only these; ``[]`` = block all. "
            "Consumed by the per-user paper book fan-out "
            "(``PaperBookFanout._eligible``) when ``PAPER_PER_USER_BOOKS`` "
            "is enabled."
        ),
    )
    paper_path_preference: Optional[list[str]] = Field(
        default=None,
        description=(
            "PAPER counterpart of ``path_preference`` — evaluator paths "
            "(setup classes) eligible to auto-trade in PAPER.  ``None`` = "
            "all paths; non-empty = only these; ``[]`` = block all.  "
            "Independent of the live ``path_preference``."
        ),
    )
    paper_regime_preference: Optional[list[str]] = Field(
        default=None,
        description=(
            "PAPER counterpart of ``regime_preference`` — entry regimes "
            "eligible to auto-trade in PAPER.  Accepts the UI tokens "
            "TRENDING / RANGING / CHOPPY (server normalises onto backend "
            "regime labels).  ``None`` = all regimes; non-empty = only "
            "these; ``[]`` = block all.  Independent of the live "
            "``regime_preference``."
        ),
    )
    notional_usd: Optional[float] = Field(
        default=None,
        ge=5.0,
        le=2000.0,
        description=(
            "Per-user live-trading notional in USD.  Engine places each "
            "signal as a ``notional_usd``-USD position (qty = notional / "
            "entry_price).  Binance MIN_NOTIONAL floor is ~$5; B18 per-"
            "user position cap ceiling is $2000.  ``null`` means use the "
            "engine default ($500).  Lower this when your Futures wallet "
            "balance is small to avoid -2019 'Margin is insufficient' "
            "rejections — e.g. $20 notional at 10× requires $2 margin."
        ),
    )
    exit_mechanism: Optional[Literal["default", "sar", "chandelier"]] = Field(
        default=None,
        description=(
            "Which mechanism owns the EXIT for this user's live positions "
            "(2026-08-10). ``'default'`` (and null) is the SL/TP FSM every "
            "account has always run. ``'sar'`` / ``'chandelier'`` hand the "
            "exit to the live trail governor: once the mechanism comes onside "
            "it cancels the evaluator's SL and TP ladder and re-parks a stop "
            "at the mechanism's level on every closed bar. "
            "Requires the engine-wide ``trail_governor_enabled`` tunable to "
            "be ON as well — this field alone changes nothing. "
            "The mechanism's stop is frequently WIDER than the stop the trade "
            "was sized for (54% of measured SAR handovers), so a position can "
            "carry more risk than its designed SL implies."
        ),
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


class SymbolManagementUpdate(BaseModel):
    """Per-(user, symbol) management mode set from the Signals tab.

    ``full`` = engine manages entry + SL + pre-TP + TP ladder +
    invalidation (default).  ``entry`` = engine places entry + protective
    SL only, then hands the position to the user (no pre-TP, no TP ladder,
    engine invalidation does not force-close).  Setting ``full`` clears any
    stored override (absence == full)."""

    symbol: str = Field(..., description="USDT-M futures symbol, e.g. BTCUSDT.")
    mode: Literal["full", "entry"] = Field(
        ..., description="'full' (engine-managed) or 'entry' (entry+SL only)."
    )


class ReferralCommissionTotal(BaseModel):
    """Accrued/paid commission totals in one currency.  Currencies never
    sum across each other (Play accrues in INR from configured prices, the
    web rail in USD from actual payments)."""

    currency: str = Field(..., description="ISO currency code, e.g. INR.")
    accrued: float = Field(..., description="Total awaiting payout.")
    paid: float = Field(..., description="Total already paid out.")


class ReferralStatsResponse(BaseModel):
    """A user's referral state — code + join counter (Phase 1) and the
    reward / commission / discount picture (Phase 2, 2026-07-21).

    Every Phase-2 field is defaulted so pre-upgrade clients (and a
    rewards-disabled engine) keep working against the Phase-1 shape."""

    code: str = Field(..., description="This user's stable referral code.")
    referred_count: int = Field(
        ..., description="Number of accounts that have redeemed this code."
    )
    rewards_enabled: bool = Field(
        default=False,
        description="Whether the incentive programme is live on the engine. "
        "False = the fields below are inert and the app renders Phase-1 UX.",
    )
    reward_days_per_invite: int = Field(
        default=0, description="Free-tier days banked per friend who joins."
    )
    reward_tier: Optional[str] = Field(
        default=None, description="Tier the join reward grants (e.g. 'auto')."
    )
    reward_days_earned: int = Field(
        default=0, description="Lifetime reward days this user has banked."
    )
    reward_active_tier: Optional[str] = Field(
        default=None, description="Tier of the currently-running reward, if any."
    )
    reward_active_until: Optional[str] = Field(
        default=None,
        description="ISO-8601 UTC end of the currently-running reward window.",
    )
    paid_referred_count: int = Field(
        default=0,
        description="How many referred friends have become paid subscribers.",
    )
    commission_rate: float = Field(
        default=0.0, description="Commission fraction per qualifying period."
    )
    commission_max_periods: int = Field(
        default=0,
        description="Commission is earned on a referred user's first N "
        "billing periods only.",
    )
    commission_totals: List[ReferralCommissionTotal] = Field(
        default_factory=list,
        description="Per-currency accrued/paid commission totals.",
    )
    discount_eligible: bool = Field(
        default=False,
        description="True while THIS user (as a referee) still holds the "
        "one-time 50%-off first billing cycle.",
    )
    discount_offer_id: Optional[str] = Field(
        default=None,
        description="Play Console offer id the app should purchase when "
        "discount_eligible (e.g. 'referral50').",
    )
    discount_percent: int = Field(
        default=0, description="Display discount percentage (web rail actual)."
    )


class TrialStateResponse(BaseModel):
    """Body of ``GET /api/trial`` and ``POST /api/trial/claim``.

    The signup free trial (2026-07-25): 7 days of the full ``auto`` tier,
    granted server-side with no payment method, activated only when the user
    taps the welcome offer.

    The app renders this and decides nothing itself — the engine is the
    source of truth for anything money-adjacent the UI shows.  In particular
    the welcome sheet appears **iff** ``offer_available`` is true, which is
    false for every user while the offer is dark, even though those users are
    already being counted in the ops cohort.

    Every field is defaulted so a pre-upgrade client, or an engine with the
    trial unwired, keeps deserialising.
    """

    offer_available: bool = Field(
        default=False,
        description="True when this user can activate a trial right now. "
        "The ONLY signal the app uses to show the welcome offer.",
    )
    days: int = Field(
        default=0, description="Length of the trial window being offered."
    )
    tier: Optional[str] = Field(
        default=None,
        description="Tier the trial grants (e.g. 'auto' — full automation).",
    )
    claimed: bool = Field(
        default=False,
        description="True once this user has activated their one trial "
        "(stays true after it lapses — a trial is one-shot per user).",
    )
    active: bool = Field(
        default=False,
        description="True while the claimed trial window is still running.",
    )
    claimed_at: Optional[str] = Field(
        default=None, description="ISO-8601 UTC activation time."
    )
    expires_at: Optional[str] = Field(
        default=None,
        description="ISO-8601 UTC end of the trial window; null if unclaimed.",
    )
    seconds_remaining: Optional[int] = Field(
        default=None, description="Seconds left in the window; null if unclaimed."
    )
    days_remaining: Optional[int] = Field(
        default=None,
        description="Whole days left, rounded up — what the countdown chip "
        "renders ('3 days left').",
    )
    converted: bool = Field(
        default=False,
        description="True once this user paid for a subscription after "
        "trialling.",
    )
    ineligible_reason: Optional[str] = Field(
        default=None,
        description="Why no offer is available: 'offer_not_available' | "
        "'already_trialled' | 'already_subscribed' | 'account_too_old' | "
        "'not_onboarded'.  Null when the offer IS available.",
    )


class TrialClaimResponse(TrialStateResponse):
    """Result of ``POST /api/trial/claim`` — the post-claim state plus the
    verdict, so one round trip both activates and refreshes the UI."""

    ok: bool = Field(
        default=False, description="True when the trial was activated."
    )
    reason: Optional[str] = Field(
        default=None,
        description="Set when ok=False; same vocabulary as "
        "``ineligible_reason``.",
    )


class TrialFunnelItem(BaseModel):
    """One user's row in the trial funnel (owner admin surface)."""

    user_id: int
    tier: str
    days: int
    eligible_at: str
    offered_at: Optional[str] = None
    claimed_at: Optional[str] = None
    expires_at: Optional[str] = None
    converted_at: Optional[str] = None
    shadow: int = Field(
        default=0,
        description="1 = the user entered the cohort while the offer was "
        "dark, i.e. they were measured but never actually offered anything.",
    )


class TrialFunnelSummary(BaseModel):
    """Aggregate trial funnel counters for ops → Trials."""

    cohort: int = Field(default=0, description="Users ever seen trial-eligible.")
    cohort_dark: int = Field(
        default=0, description="Of those, measured while the offer was off."
    )
    cohort_live: int = Field(
        default=0, description="Of those, seen while the offer was live."
    )
    offered: int = Field(default=0, description="Users actually shown the offer.")
    claimed: int = Field(default=0, description="Users who activated a trial.")
    active: int = Field(default=0, description="Trials running right now.")
    lapsed: int = Field(default=0, description="Trials that have ended.")
    converted: int = Field(
        default=0, description="Trialists who went on to pay."
    )
    claim_rate: Optional[float] = Field(
        default=None,
        description="claimed / offered; null when nobody has been offered "
        "yet — an unmeasured rate must not render as a real 0%.",
    )
    conversion_rate: Optional[float] = Field(
        default=None,
        description="converted / claimed; null when nobody has trialled yet.",
    )


class TrialFunnelResponse(BaseModel):
    """Owner admin view of the signup trial — flag state beside the numbers.

    The flags travel with the counters on purpose: a cohort of 400 means
    something entirely different depending on whether those users were ever
    actually offered anything.
    """

    offer_live: bool = Field(
        ..., description="SIGNUP_TRIAL_ENABLED — the user-visible flag."
    )
    measuring: bool = Field(
        ..., description="SIGNUP_TRIAL_MEASUREMENT_ENABLED — the cohort stamp."
    )
    days: int
    tier: str
    max_account_age_days: int = Field(
        default=0, description="0 = no age limit on eligibility."
    )
    summary: TrialFunnelSummary
    trials: List[TrialFunnelItem] = Field(default_factory=list)


class ReferralClaimRequest(BaseModel):
    """A new user redeeming someone else's referral code, typically
    captured once during onboarding."""

    code: str = Field(..., description="The referral code being redeemed.")


class ReferralClaimResponse(BaseModel):
    """Result of a referral-code redemption attempt."""

    ok: bool = Field(..., description="True if the code was accepted.")
    reason: Optional[str] = Field(
        default=None,
        description="Set when ok=False: 'invalid_code' | 'self_referral' "
        "| 'already_redeemed'.",
    )
    discount_eligible: bool = Field(
        default=False,
        description="True when the successful claim unlocked the one-time "
        "50%-off first billing cycle for this user.",
    )


class ReferralCommissionItem(BaseModel):
    """One accrued/paid commission row (owner admin surface)."""

    commission_id: int
    referrer_id: int
    referee_id: int
    referrer_phone: Optional[str] = Field(
        default=None,
        description="Referrer's phone (payout identity for manual payouts).",
    )
    product_id: str
    period_expiry: str
    amount: float
    currency: str
    rate: float
    status: str = Field(..., description="'accrued' | 'paid'.")
    created_at: str
    paid_at: Optional[str] = None


class ReferralCommissionsResponse(BaseModel):
    """Owner admin listing of referral commissions."""

    items: List[ReferralCommissionItem]


class ReferralCommissionsMarkPaidRequest(BaseModel):
    """Owner marking accrued commissions as settled (manual payout done)."""

    commission_ids: List[int] = Field(..., description="Rows to flip to paid.")


class ReferralCommissionsMarkPaidResponse(BaseModel):
    ok: bool
    updated: int = Field(..., description="Rows actually transitioned.")


class UserAutoTradeSettings(AutoTradeSettings):
    """Per-user auto-trade overrides — same shape as
    :class:`AutoTradeSettings` plus ``using_defaults`` and auto-pause
    state.

    Phase 2: the engine itself does not consume per-user mode /
    position_size_pct / leverage_cap.  Values are stored for Phase 3
    when the user's app fires their own Binance order using these
    values for sizing.  The app surfaces this with an honest banner.
    """

    using_defaults: bool = Field(
        default=True,
        description="True when the user has no override row.",
    )
    paused_reason: Optional[str] = Field(
        default=None,
        description=(
            "Typed reason when the engine has auto-paused this user's "
            "dispatcher (currently only 'insufficient_margin' from the "
            "consecutive -2019 tracker, 2026-05-24). NULL when the user "
            "is not paused. App shows a 'top up + resume' banner when "
            "set."
        ),
    )
    paused_at: Optional[str] = Field(
        default=None,
        description=(
            "ISO-8601 UTC timestamp of the pause event. NULL when not "
            "paused. Pair with ``paused_reason`` to render the banner; "
            "cleared by POST /api/auto-mode/resume-mine."
        ),
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
    tier: Literal["free", "assist", "auto", "paid", "owner"]
    paid_until_iso: Optional[str] = Field(
        default=None,
        description="ISO-8601 UTC; null when revoking (downgrade to free).",
    )


class BillingGrantResponse(BaseModel):
    ok: bool
    user_id: int
    tier: str


# ---------------------------------------------------------------------------
# Admin manual tier grant (owner-only comp, ops dashboard control plane)
# ---------------------------------------------------------------------------


class AdminUserLookupResponse(BaseModel):
    """Response of ``GET /api/admin/users/lookup`` — what the ops UI shows
    before the owner decides whether/what to grant."""

    user_id: int
    phone: str
    tier: str
    paid_until: Optional[str] = None
    display_name: Optional[str] = None
    onboarded: bool
    #: The account's live exit mechanism, read from the same store
    #: ``POST /api/admin/users/exit-mechanism`` writes.  Added 2026-08-10 (#911)
    #: because the setter had no companion reader: the ops select was a static
    #: three-option list, so an account handed to SAR still rendered
    #: "default (SL/TP FSM — unchanged)" on every reload and the owner had no
    #: way to see the state he had just written.  A write surface with no
    #: read-back is #817 with the arrow reversed, and this file already carries
    #: the rule the setter was built on — *read the value back from the store
    #: rather than echoing the request*.
    #:
    #: ``None`` means the engine could not answer (no per-user override store),
    #: which is not the same fact as ``"default"`` and must not render as one.
    exit_mechanism: Optional[str] = None
    #: The engine-wide master switch, beside it for the same reason the setter
    #: returns it: the per-user value alone changes nothing, and a reader who
    #: sees SAR without seeing this cannot tell running from armed-and-inert.
    governor_enabled: Optional[bool] = None


class AdminAutoTradeEnableRequest(BaseModel):
    """Body of ``POST /api/admin/users/auto-trade-enable``.

    Owner-only operator verb for the per-user kill-switch flag
    (``users/{uid}.auto_trade_disabled`` in Firestore).  The per-user
    circuit breaker (B18 #5) auto-DISABLES a user on repeated order
    failures; until 2026-07-18 there was **no re-enable surface
    anywhere** — the S59/S62 runbooks named ``/enable_user`` but no
    Telegram command or endpoint ever existed, so a breaker-tripped
    paying subscriber stayed disabled forever.  This endpoint is that
    missing verb.  ``enabled=false`` is the symmetric manual operator
    disable (same write the breaker performs, with an audit reason).

    Identify the user by ``phone`` (ops-friendly) or ``firebase_uid``
    (as shown in breaker logs / error screenshots) — exactly one.
    """

    phone: Optional[str] = Field(default=None, min_length=8, max_length=18)
    firebase_uid: Optional[str] = Field(
        default=None, min_length=8, max_length=128
    )
    enabled: bool = Field(
        ..., description="true = re-enable auto-trade; false = disable"
    )
    reason: str = Field(
        default="", max_length=200,
        description="Audit note; stored as the disable reason when disabling.",
    )


class AdminAutoTradeEnableResponse(BaseModel):
    """Read-back state after the write — the engine (Firestore flag) is
    the source of truth, so the response re-reads rather than echoes."""

    ok: bool
    firebase_uid: str
    phone: Optional[str] = None
    auto_trade_disabled: bool


class AdminExitMechanismRequest(BaseModel):
    """Body of ``POST /api/admin/users/exit-mechanism``.

    The owner-facing way to opt one account into the live trail governor
    (2026-08-10).  It exists because the alternative was the account holder
    PUTting their own ``/api/settings/user/auto-trade`` from the Lumin app,
    and the app has no control for this field — so without this endpoint the
    per-user column could only be reached with a hand-minted Firebase token.

    This is a **money-path** write: setting anything but ``default`` means the
    engine will cancel that user's evaluator SL and TP ladder at handover and
    manage the exit itself.  It still does nothing unless the engine-wide
    ``trail_governor_enabled`` tunable is also ON — two switches, deliberately.
    """

    phone: Optional[str] = Field(default=None, min_length=8, max_length=18)
    firebase_uid: Optional[str] = Field(
        default=None, min_length=8, max_length=128
    )
    exit_mechanism: Literal["default", "sar", "chandelier"] = Field(
        ...,
        description=(
            "'default' returns the user to the ordinary SL/TP FSM exit; "
            "'sar' / 'chandelier' hand the exit to the live trail governor."
        ),
    )
    reason: str = Field(
        default="", max_length=200, description="Audit note."
    )


class AdminExitMechanismResponse(BaseModel):
    """Read back from the store rather than echoing the request — the engine
    is the source of truth, and a response that echoed would report success
    for a value the coercion layer rejected."""

    ok: bool
    user_id: int
    phone: Optional[str] = None
    exit_mechanism: str
    #: Engine-wide master switch. Published beside the per-user value because
    #: the setting alone changes nothing, and an operator who sets one and not
    #: the other must not read "ok" as "it is running".
    governor_enabled: bool


class AdminGrantTierRequest(BaseModel):
    """Body of ``POST /api/admin/grant-tier``.

    Owner-only manual comp (tester, influencer, goodwill gesture) — not a
    Play Billing purchase.  Every grant carries an expiry: there is no
    permanent comp via this endpoint, only a renewable one (call again
    before expiry to extend).  ``tier=free`` revokes any active grant
    immediately and ``duration_days`` is ignored in that case.
    """

    phone: str = Field(..., min_length=8, max_length=18)
    tier: Literal["free", "assist", "auto"]
    duration_days: int = Field(
        default=30, ge=1, le=365,
        description="Grant expires this many days from now. Ignored when tier=free.",
    )
    reason: Optional[str] = Field(default=None, max_length=200)


class AdminGrantTierResponse(BaseModel):
    ok: bool
    user_id: int
    phone: str
    tier: str
    paid_until: Optional[str] = None


# ---------------------------------------------------------------------------
# Google Play Billing (B16 — in-app subscription purchase path)
# ---------------------------------------------------------------------------


class PlayVerifyRequest(BaseModel):
    """Body of ``POST /api/billing/play/verify``.

    Sent by the app immediately after a Play Billing purchase completes.
    The request is authenticated with the user's JWT (so the server knows
    the ``user_id``); the body carries only what the Play Developer API
    needs to look the purchase up.  Nothing here is trusted — entitlement
    is re-derived server-side from Google.
    """

    product_id: str = Field(
        ..., min_length=1, max_length=128,
        description="Play subscription product id, e.g. lumin_pro_monthly.",
    )
    purchase_token: str = Field(
        ..., min_length=1, max_length=4096,
        description="Opaque purchaseToken returned by Play Billing.",
    )


class PlayVerifyResponse(BaseModel):
    """Result of verifying a Play purchase.

    ``tier`` + ``paid_until`` reflect the entitlement the server just
    persisted, so the app can update its UI without a second round-trip.
    """

    ok: bool
    tier: str
    paid_until: Optional[str] = Field(
        default=None, description="ISO-8601 UTC subscription expiry, or null."
    )
    subscription_state: str = Field(
        ..., description="Raw Play subscriptionState (for diagnostics)."
    )
    token: Optional[str] = Field(
        default=None,
        description=(
            "Freshly-minted Lumin JWT carrying the new tier + paid_until so "
            "the app unlocks immediately without re-exchanging its token."
        ),
    )
    exp_seconds: Optional[int] = Field(
        default=None, description="TTL of the returned token in seconds."
    )


class PlayRtdnResponse(BaseModel):
    """Acknowledgement returned to Google Pub/Sub for an RTDN push.

    Always 200 with ``ok: true`` once we've accepted the message — even
    for no-op events — so Pub/Sub stops redelivering.  Hard failures that
    SHOULD be retried surface as a non-2xx status instead of this body.
    """

    ok: bool
    handled: str = Field(..., description="What we did, e.g. 'RENEWED' / 'ignored'.")


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
# Per-user paper visibility reset (2026-05-23 fix for fresh-account bug)
# ---------------------------------------------------------------------------


class PaperResetMineResponse(BaseModel):
    """Response shape for ``POST /api/auto-mode/paper/reset-mine``.

    Returns the new ``started_at`` so the app can immediately update its
    local "paper since" label without re-fetching the auto-mode status.
    """

    ok: bool = True
    new_started_at: str = Field(
        ...,
        description=(
            "ISO-8601 UTC of the user's new paper-subscription window. "
            "GET /api/trades will return only rows closed at-or-after "
            "this stamp until the user disables paper or calls reset-mine "
            "again."
        ),
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


# ---------------------------------------------------------------------------
# Binance connect flow (server-side execution, OWNER_BRIEF B18)
# ---------------------------------------------------------------------------


class BinanceConnectRequest(BaseModel):
    """Request body for ``POST /api/binance/connect``.

    The user pastes their Binance API key + secret in the Lumin app.
    The app POSTs them here over HTTPS.  The endpoint validates against
    Binance, encrypts the secret with a per-user DEK, and persists the
    encrypted blob.  The plaintext secret is wiped immediately after
    validation + encryption — never logged, never returned, never
    written to disk in the clear.

    ``api_key`` and ``api_secret`` are intentionally bare ``str`` (not
    ``SecretStr``) because we never write the request model to any log
    sink — the engine's loguru config strips the request body from
    access logs for this route.  Using ``SecretStr`` here would suggest
    we sometimes log the model elsewhere, which we do not.
    """

    api_key: str = Field(..., min_length=8, description="Binance API key (public)")
    api_secret: str = Field(..., min_length=8, description="Binance API secret")


class BinanceConnectResponse(BaseModel):
    """Response body for ``POST /api/binance/connect`` on success.

    The app displays the ``key_public_id_first8`` so the user can
    confirm at-a-glance that the key they pasted is the one Lumin
    stored.  The full key is never returned (it's stored encrypted
    server-side and never round-trips back to the client).
    """

    ok: bool = True
    key_public_id_first8: str = Field(
        ...,
        description=(
            "First 8 characters of the Binance API key — non-secret, "
            "used for at-a-glance confirmation in the app's connected-key UI"
        ),
    )
    withdraw_disabled_ok: bool = Field(
        True,
        description="Validated: withdraw permission is disabled on this key",
    )
    futures_enabled_ok: bool = Field(
        True,
        description="Validated: Futures permission is enabled on this key",
    )
    ip_whitelist_ok: bool = Field(
        True,
        description=(
            "Validated: IP whitelist is enabled AND Lumin's engine IP "
            "is on the whitelist (proven by a successful signed call)"
        ),
    )


class BinanceConnectErrorResponse(BaseModel):
    """Response body for ``POST /api/binance/connect`` on validation failure.

    The ``detail`` carries the human-readable fix-up instruction (which
    Binance setting to change).  The ``code`` is a short stable token
    the app can use to render a setting-specific UI affordance — e.g.
    ``WITHDRAW_ENABLED`` could trigger a deep-link to Binance's API
    Management page with a one-tap "Open Binance" button.
    """

    ok: bool = False
    code: str = Field(
        ...,
        description=(
            "Stable error code: WITHDRAW_ENABLED | FUTURES_DISABLED | "
            "IP_RESTRICT_DISABLED | IP_NOT_WHITELISTED | KEY_INVALID | "
            "BINANCE_UNREACHABLE"
        ),
    )
    detail: str = Field(..., description="Human-readable fix-up instruction")
    engine_vps_ip: Optional[str] = Field(
        None,
        description=(
            "Returned with IP_RESTRICT_DISABLED and IP_NOT_WHITELISTED "
            "so the app can show the exact IP the user must whitelist"
        ),
    )


class BinanceConnectStatusResponse(BaseModel):
    """Response body for ``GET /api/binance/connect/status``.

    Returns the user's current connection state so the Server-side
    execution settings page can render "connected as XXXXXXXX since
    <date>" + a Replace/Disconnect affordance on revisit, instead of
    always showing the connect form (which makes the first connect
    look unsuccessful from the user's perspective — they connected,
    they revisit, the form is back, they assume the connect failed).

    ``connected = False`` is the not-yet-connected state.  No key blob
    fields are returned in that case (everything else is null).
    """

    connected: bool = Field(
        ...,
        description=(
            "True iff a Firestore key blob exists for the requesting "
            "Firebase uid (i.e. this user has connected before)."
        ),
    )
    key_public_id_first8: Optional[str] = Field(
        None,
        description=(
            "First 8 characters of the connected key.  Lets the app "
            "render 'XXXXXXXX…' on revisit so the user can confirm "
            "the stored key matches what they expect."
        ),
    )
    connected_at: Optional[str] = Field(
        None,
        description="ISO-8601 UTC timestamp of the initial connect call",
    )
    withdraw_disabled_ok: Optional[bool] = Field(
        None,
        description=(
            "Validation flag captured at connect time — withdraw "
            "permission was confirmed disabled on the key"
        ),
    )
    ip_whitelist_ok: Optional[bool] = Field(
        None,
        description=(
            "Validation flag captured at connect time — IP whitelist "
            "enabled AND engine VPS on the list, proven via signed call"
        ),
    )


class BinanceConnectInfoResponse(BaseModel):
    """Response body for ``GET /api/binance/connect/info``.

    Non-secret onboarding metadata the Server-side execution page shows
    *before* a connect attempt.  Today that is just the engine VPS IP the
    user must whitelist on their Binance key.  Served independently of
    KMS / Firestore so the IP stays retrievable even when the connect
    flow itself is 500ing on a KMS/Firestore misconfiguration.
    """

    engine_vps_ip: Optional[str] = Field(
        None,
        description=(
            "The public IP the user must add to their Binance API-key IP "
            "whitelist.  Null when the operator has not set "
            "ENGINE_VPS_PUBLIC_IP — the app then falls back to generic "
            "whitelist wording rather than showing an error."
        ),
    )


# ---------------------------------------------------------------------------
# Admin full-signal reset (owner-only) — 2026-06-25
# ---------------------------------------------------------------------------


class SignalResetResponse(BaseModel):
    """Response shape for ``POST /api/admin/reset-signals``.

    All ``cleared_*`` and ``paper_*`` counts are 0 in isolated mode for
    the signal-state portion (the engine processes the Redis command
    asynchronously); ``engine_reset_queued=True`` confirms the command
    was queued.  Paper-broker counts reflect what the API container
    processed synchronously.
    """

    reset_at: str = Field(..., description="ISO-8601 UTC of the reset request")
    cleared_active_signals: int = Field(0)
    cleared_history: int = Field(0)
    cleared_perf_stats: int = Field(0)
    cleared_invalidation_records: int = Field(0)
    paper_positions_closed: int = Field(0)
    paper_pnl_buckets_cleared: int = Field(0)
    paper_trades_archived: int = Field(0)
    engine_reset_queued: bool = Field(
        False,
        description=(
            "True in isolated mode — the engine container processes the "
            "signal-state clear asynchronously (≤15s). False in single-process "
            "mode where the clear happens synchronously."
        ),
    )
