"""Engine → Pydantic snapshot adapters.

Pure functions: read the live ``Engine`` instance and return Pydantic
models from :mod:`src.api.schemas`.  Endpoints stay thin; all
serialization quirks live here.

No method here mutates engine state.  ``consume_generation_telemetry()``
on a channel resets its counters — we deliberately read the underlying
``_generation_telemetry`` dict directly to avoid that side-effect.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .schemas import (
    ActivityEvent,
    AgentStat,
    AutoModeStatus,
    PositionDetail,
    PulseSnapshot,
    SignalDetail,
    TickerItem,
)


# Mapping: setup_class on Signal  →  display name shown in the app.
# Kept in sync with ``lib/features/agents/agent_data.dart``.
_AGENT_DISPLAY_NAMES: Dict[str, str] = {
    "SR_FLIP_RETEST": "The Architect",
    "LIQUIDITY_SWEEP_REVERSAL": "The Counter-Puncher",
    "FAILED_AUCTION_RECLAIM": "The Reclaimer",
    "QUIET_COMPRESSION_BREAK": "The Coil Hunter",
    "VOLUME_SURGE_BREAKOUT": "The Tracker",
    "BREAKDOWN_SHORT": "The Crusher",
    "FUNDING_EXTREME_SIGNAL": "The Contrarian",
    "WHALE_MOMENTUM": "The Whale Hunter",
    "LIQUIDATION_REVERSAL": "The Cascade Catcher",
    "CONTINUATION_LIQUIDITY_SWEEP": "The Continuation Specialist",
    "DIVERGENCE_CONTINUATION": "The Divergence Reader",
    "TREND_PULLBACK_EMA": "The Pullback Sniper",
    "POST_DISPLACEMENT_CONTINUATION": "The Aftermath Trader",
    "OPENING_RANGE_BREAKOUT": "The Range Breaker",
    # PR #318 (15th evaluator) — discrete EMA50/200 (4h) or EMA21/50 (1h)
    # crossover trigger.  Low-frequency, high-conviction.
    "MA_CROSS_TREND_SHIFT": "The Trend Shifter",
}

# Mapping: telemetry path token  →  setup_class string (path tokens come
# from ``ScalpChannel._generation_path_token`` which strips ``_evaluate_``
# and uppercases the rest).  Built from the channel source so changes to
# evaluator names are caught at review time, not silently in production.
_PATH_TO_SETUP: Dict[str, str] = {
    "SR_FLIP_RETEST": "SR_FLIP_RETEST",
    "LIQUIDATION_REVERSAL": "LIQUIDATION_REVERSAL",
    "WHALE_MOMENTUM": "WHALE_MOMENTUM",
    "VOLUME_SURGE_BREAKOUT": "VOLUME_SURGE_BREAKOUT",
    "BREAKDOWN_SHORT": "BREAKDOWN_SHORT",
    "OPENING_RANGE_BREAKOUT": "OPENING_RANGE_BREAKOUT",
    "FUNDING_EXTREME": "FUNDING_EXTREME_SIGNAL",
    "QUIET_COMPRESSION_BREAK": "QUIET_COMPRESSION_BREAK",
    "DIVERGENCE_CONTINUATION": "DIVERGENCE_CONTINUATION",
    "CONTINUATION_LIQUIDITY_SWEEP": "CONTINUATION_LIQUIDITY_SWEEP",
    "POST_DISPLACEMENT_CONTINUATION": "POST_DISPLACEMENT_CONTINUATION",
    "FAILED_AUCTION_RECLAIM": "FAILED_AUCTION_RECLAIM",
    "TREND_PULLBACK": "TREND_PULLBACK_EMA",
    "STANDARD": "LIQUIDITY_SWEEP_REVERSAL",
    # _generation_path_token strips "_evaluate_" and uppercases the rest.
    # _evaluate_ma_cross_trend_shift → MA_CROSS_TREND_SHIFT.
    "MA_CROSS_TREND_SHIFT": "MA_CROSS_TREND_SHIFT",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _minutes_since(ts: Optional[datetime]) -> int:
    if ts is None:
        return 0
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return max(0, int((_now() - ts).total_seconds() // 60))


def _agent_name_for(setup_class: str) -> str:
    return _AGENT_DISPLAY_NAMES.get(setup_class, "Engine")


# ---------------------------------------------------------------------------
# Pulse
# ---------------------------------------------------------------------------


def build_pulse(engine: Any) -> PulseSnapshot:
    rm = getattr(engine, "_risk_manager", None)
    open_positions = rm.open_position_count if rm is not None else 0

    today_pnl_usd = rm.daily_realised_pnl_usd if rm is not None else 0.0
    starting_equity = (
        rm.current_equity_usd - today_pnl_usd if rm is not None else 0.0
    )
    today_pnl_pct = (
        100.0 * today_pnl_usd / starting_equity if starting_equity > 0 else 0.0
    )

    # Daily-loss budget: pull from RiskManager config.
    #
    # ``RISK_DAILY_LOSS_LIMIT_PCT`` is defined as a NEGATIVE percent (e.g.
    # -3.0 for a 3% kill threshold), so the previous ``> 0`` guard always
    # zeroed the budget — owner reported "loss budget zero zero" on Pulse.
    # ``abs()`` so subscribers see the positive $-amount of risk allowed.
    from config import RISK_DAILY_LOSS_LIMIT_PCT, RISK_STARTING_EQUITY_USD

    budget_usd = (
        abs(RISK_DAILY_LOSS_LIMIT_PCT) / 100.0 * RISK_STARTING_EQUITY_USD
        if RISK_DAILY_LOSS_LIMIT_PCT != 0 and RISK_STARTING_EQUITY_USD > 0
        else 0.0
    )
    used_usd = abs(min(today_pnl_usd, 0.0))

    regime = "RANGING"
    try:
        r = engine._regime_detector.get_regime("BTCUSDT")
        regime = r.regime.value if r else regime
    except Exception:
        pass

    boot_time = getattr(engine, "_boot_time", 0.0) or 0.0
    uptime_seconds = max(0.0, time.monotonic() - boot_time) if boot_time else 0.0

    scanning_pairs = 0
    pair_mgr = getattr(engine, "pair_mgr", None)
    if pair_mgr is not None and hasattr(pair_mgr, "symbols"):
        scanning_pairs = len(pair_mgr.symbols)

    history = getattr(engine, "_signal_history", []) or []
    today = _now().date()
    signals_today = sum(
        1
        for s in history
        if getattr(s, "timestamp", None) is not None
        and s.timestamp.date() == today
    )

    status: str = "Healthy"
    if rm is not None and rm.daily_kill_tripped:
        status = "Degraded"

    return PulseSnapshot(
        status=status,  # type: ignore[arg-type]
        mode=getattr(engine, "_current_auto_mode", "off"),  # type: ignore[arg-type]
        regime=regime,
        regime_pct_trending=0.0,
        today_pnl_usd=today_pnl_usd,
        today_pnl_pct=today_pnl_pct,
        daily_loss_budget_usd=budget_usd,
        daily_loss_used_usd=used_usd,
        open_positions=open_positions,
        signals_today=signals_today,
        uptime_seconds=uptime_seconds,
        scanning_pairs=scanning_pairs,
    )


# ---------------------------------------------------------------------------
# Tickers — live prices for the Pulse top-pair strip.
# ---------------------------------------------------------------------------


# Top pairs by trading volume / brand recognition.  Hard-coded so the strip
# stays stable as PairManager promotes/demotes the universe; subscribers
# expect to see BTC/ETH first.
_PULSE_TICKER_SYMBOLS: tuple[str, ...] = (
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "DOGEUSDT",
)


def _last_close(store: Any, symbol: str, interval: str = "1m") -> Optional[float]:
    """Best-effort last-close fetch off the historical-data store."""
    if store is None:
        return None
    try:
        candles = store.get_candles(symbol, interval)
    except Exception:
        return None
    if not candles:
        return None
    closes = candles.get("close")
    if closes is None or len(closes) == 0:
        return None
    last = float(closes[-1])
    return last if last > 0 else None


def _change_pct_24h(store: Any, symbol: str) -> float:
    """24h % change from 1h candles (~24 candles back vs latest).

    Falls back to 0.0 if the store doesn't have enough history.  Best-effort
    — a missing change pct should never break the ticker strip.
    """
    if store is None:
        return 0.0
    try:
        candles = store.get_candles(symbol, "1h")
    except Exception:
        return 0.0
    if not candles:
        return 0.0
    closes = candles.get("close")
    if closes is None or len(closes) < 2:
        return 0.0
    last = float(closes[-1])
    # Use the 24-bars-ago close when available, else the oldest close in window.
    idx = max(0, len(closes) - 24)
    ref = float(closes[idx])
    if ref <= 0 or last <= 0:
        return 0.0
    return (last - ref) / ref * 100.0


def build_tickers(engine: Any) -> List[TickerItem]:
    """Live prices + 24h % change for the Pulse top-pair strip."""
    store = getattr(engine, "data_store", None) or getattr(engine, "_data_store", None)
    items: List[TickerItem] = []
    for sym in _PULSE_TICKER_SYMBOLS:
        price = _last_close(store, sym)
        if price is None:
            # Skip pairs with no seeded data — better to show a shorter list
            # than mislead with a 0.0 placeholder.
            continue
        items.append(
            TickerItem(
                symbol=sym,
                price=price,
                change_pct_24h=_change_pct_24h(store, sym),
            )
        )
    return items


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------


def _signal_to_detail(sig: Any) -> SignalDetail:
    direction = getattr(sig, "direction", None)
    direction_str = (
        direction.value
        if direction is not None and hasattr(direction, "value")
        else str(direction or "LONG")
    ).upper()
    setup_class = getattr(sig, "setup_class", "UNCLASSIFIED") or "UNCLASSIFIED"
    timestamp = getattr(sig, "timestamp", None) or _now()
    return SignalDetail(
        signal_id=getattr(sig, "signal_id", "") or "",
        symbol=getattr(sig, "symbol", ""),
        direction=direction_str,  # type: ignore[arg-type]
        entry=float(getattr(sig, "entry", 0.0) or 0.0),
        stop_loss=float(getattr(sig, "stop_loss", 0.0) or 0.0),
        tp1=float(getattr(sig, "tp1", 0.0) or 0.0),
        tp2=float(getattr(sig, "tp2", 0.0) or 0.0),
        tp3=getattr(sig, "tp3", None),
        confidence=float(getattr(sig, "confidence", 0.0) or 0.0),
        quality_tier=getattr(sig, "quality_tier", "B") or "B",
        setup_class=setup_class,
        agent_name=_agent_name_for(setup_class),
        status=getattr(sig, "status", "ACTIVE") or "ACTIVE",
        current_price=float(getattr(sig, "current_price", 0.0) or 0.0),
        pnl_pct=float(getattr(sig, "pnl_pct", 0.0) or 0.0),
        pre_tp_hit=bool(getattr(sig, "pre_tp_hit", False)),
        pre_tp_threshold_pct=float(
            getattr(sig, "pre_tp_threshold_pct", 0.0) or 0.0
        ),
        pre_tp_trigger_price=(
            float(getattr(sig, "pre_tp_trigger_price", 0.0) or 0.0) or None
        ),
        timestamp=timestamp,
        minutes_ago=_minutes_since(timestamp),
    )


def build_signals(
    engine: Any,
    *,
    status: str = "all",
    limit: int = 50,
    setup_class: Optional[str] = None,
) -> List[SignalDetail]:
    router = getattr(engine, "router", None)
    history = list(getattr(engine, "_signal_history", []) or [])
    active = list(router.active_signals.values()) if router is not None else []

    if status == "open":
        signals = active
    elif status == "closed":
        signals = history
    else:
        signals = active + history

    if setup_class:
        target = setup_class.strip().upper()
        signals = [
            s
            for s in signals
            if (getattr(s, "setup_class", "") or "").upper() == target
        ]

    signals.sort(
        key=lambda s: getattr(s, "timestamp", None) or _now(),
        reverse=True,
    )
    return [_signal_to_detail(s) for s in signals[:limit]]


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------


def build_positions(engine: Any) -> List[PositionDetail]:
    """Return open positions sourced from the active-signals dict.

    Paper / live positions are tracked at signal granularity by the router;
    that's the canonical view the app needs.  Underlying broker positions
    can drift from signals during live mode — those show up via the
    PositionReconciler's audit logs, not here.
    """
    router = getattr(engine, "router", None)
    if router is None:
        return []
    out: List[PositionDetail] = []
    for sig in router.active_signals.values():
        direction = getattr(sig, "direction", None)
        direction_str = (
            direction.value
            if direction is not None and hasattr(direction, "value")
            else str(direction or "LONG")
        ).upper()
        entry = float(getattr(sig, "entry", 0.0) or 0.0)
        current_price = float(getattr(sig, "current_price", entry) or entry)
        pnl_pct = float(getattr(sig, "pnl_pct", 0.0) or 0.0)
        # qty / pnl_usd come from the order_manager's view of the position;
        # for the v0 API we approximate pnl_usd from pnl_pct on a notional
        # 1.0-unit basis when broker info isn't available.
        qty = float(getattr(sig, "qty", 0.0) or 0.0)
        pnl_usd = float(getattr(sig, "pnl_usd", 0.0) or 0.0)
        if pnl_usd == 0.0 and entry > 0:
            pnl_usd = round(qty * entry * pnl_pct / 100.0, 2)
        ts = getattr(sig, "timestamp", None)
        out.append(
            PositionDetail(
                signal_id=getattr(sig, "signal_id", "") or "",
                symbol=getattr(sig, "symbol", ""),
                direction=direction_str,  # type: ignore[arg-type]
                entry=entry,
                current_price=current_price,
                qty=qty,
                pnl_usd=pnl_usd,
                pnl_pct=pnl_pct,
                minutes_open=_minutes_since(ts),
            )
        )
    return out


# ---------------------------------------------------------------------------
# Activity feed
# ---------------------------------------------------------------------------


def _activity_kind_for_status(status: str) -> Optional[str]:
    s = (status or "").upper()
    if s in {"TP1_HIT"}:
        return "TP1"
    if s in {"TP2_HIT"}:
        return "TP2"
    if s in {"TP3_HIT", "FULL_TP_HIT"}:
        return "TP3"
    if s in {"SL_HIT"}:
        return "SL"
    if s in {"INVALIDATED", "EXPIRED", "CANCELLED"}:
        return "INVAL"
    return None


def build_activity(
    engine: Any,
    *,
    limit: int = 50,
    setup_class: Optional[str] = None,
) -> List[ActivityEvent]:
    history = list(getattr(engine, "_signal_history", []) or [])
    router = getattr(engine, "router", None)
    active = list(router.active_signals.values()) if router is not None else []

    pool = active + history
    if setup_class:
        target = setup_class.strip().upper()
        pool = [
            s
            for s in pool
            if (getattr(s, "setup_class", "") or "").upper() == target
        ]

    events: List[ActivityEvent] = []

    # OPEN events from every signal we know about.
    for sig in pool:
        ts = getattr(sig, "dispatch_timestamp", None) or getattr(
            sig, "timestamp", None
        )
        if ts is None:
            continue
        symbol = getattr(sig, "symbol", "")
        direction = getattr(sig, "direction", None)
        direction_str = (
            direction.value if direction is not None and hasattr(direction, "value")
            else str(direction or "LONG")
        ).upper()
        agent = _agent_name_for(getattr(sig, "setup_class", "") or "")
        events.append(
            ActivityEvent(
                kind="OPEN",
                title=f"{symbol} {direction_str} opened",
                subtitle=f"entry {getattr(sig, 'entry', 0.0):.4f} — {agent}",
                timestamp=ts,
                minutes_ago=_minutes_since(ts),
            )
        )

        # Pre-TP marker
        if getattr(sig, "pre_tp_hit", False):
            pre_ts = getattr(sig, "pre_tp_timestamp", None) or ts
            events.append(
                ActivityEvent(
                    kind="PRE_TP",
                    title=f"{symbol} {direction_str} — pre-TP",
                    subtitle=f"+{getattr(sig, 'pre_tp_pct', 0.0):.2f}% — SL → breakeven",
                    timestamp=pre_ts,
                    minutes_ago=_minutes_since(pre_ts),
                )
            )

        # Terminal outcome
        terminal_ts = getattr(sig, "terminal_outcome_timestamp", None)
        kind = _activity_kind_for_status(getattr(sig, "status", ""))
        if terminal_ts is not None and kind is not None:
            pnl = getattr(sig, "pnl_pct", 0.0) or 0.0
            sign = "+" if pnl >= 0 else ""
            events.append(
                ActivityEvent(
                    kind=kind,  # type: ignore[arg-type]
                    title=f"{symbol} {direction_str} — {kind}",
                    subtitle=f"{sign}{pnl:.2f}%",
                    timestamp=terminal_ts,
                    minutes_ago=_minutes_since(terminal_ts),
                )
            )

    events.sort(key=lambda e: e.timestamp, reverse=True)
    return events[:limit]


# ---------------------------------------------------------------------------
# Auto-mode
# ---------------------------------------------------------------------------


def build_auto_mode(engine: Any) -> AutoModeStatus:
    info: Dict[str, Any]
    try:
        info = engine.get_auto_execution_status()
    except Exception:
        info = {
            "mode": getattr(engine, "_current_auto_mode", "off"),
            "open_positions": 0,
            "daily_pnl_usd": 0.0,
            "daily_loss_pct": 0.0,
            "daily_kill_tripped": False,
            "manual_paused": False,
            "current_equity_usd": 0.0,
        }
    return AutoModeStatus(**info)


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------


_TP_STATUSES = {"TP1_HIT", "TP2_HIT", "TP3_HIT", "FULL_TP_HIT"}
_SL_STATUSES = {"SL_HIT"}
_INVAL_STATUSES = {"INVALIDATED", "EXPIRED", "CANCELLED"}


def _lifecycle_stats_by_setup(
    history: List[Any],
    *,
    window_minutes: int = 24 * 60,
) -> Dict[str, Dict[str, Any]]:
    """Aggregate per-setup-class lifecycle counters from history.

    Counts terminal-state signals whose ``terminal_outcome_timestamp`` falls
    within the rolling window.  Also tracks ``last_signal_age_minutes`` —
    the minutes since the most recent emission for that setup, irrespective
    of outcome status — so the agent grid can show "fired Xm ago" cards.
    """
    out: Dict[str, Dict[str, Any]] = {}
    cutoff_minutes = window_minutes
    for sig in history:
        sc = (getattr(sig, "setup_class", "") or "").upper()
        if not sc:
            continue
        bucket = out.setdefault(
            sc,
            {
                "closed_today": 0,
                "tp_hits": 0,
                "sl_hits": 0,
                "invalidated": 0,
                "last_signal_age_minutes": None,
            },
        )
        emit_ts = getattr(sig, "timestamp", None)
        emit_age = _minutes_since(emit_ts) if emit_ts is not None else None
        if emit_age is not None:
            cur = bucket["last_signal_age_minutes"]
            if cur is None or emit_age < cur:
                bucket["last_signal_age_minutes"] = emit_age

        term_ts = getattr(sig, "terminal_outcome_timestamp", None)
        if term_ts is None:
            continue
        term_age = _minutes_since(term_ts)
        if term_age > cutoff_minutes:
            continue
        status = (getattr(sig, "status", "") or "").upper()
        if status in _TP_STATUSES:
            bucket["tp_hits"] += 1
            bucket["closed_today"] += 1
        elif status in _SL_STATUSES:
            bucket["sl_hits"] += 1
            bucket["closed_today"] += 1
        elif status in _INVAL_STATUSES:
            bucket["invalidated"] += 1
            bucket["closed_today"] += 1
    return out


def build_agents(engine: Any) -> List[AgentStat]:
    """Return per-evaluator stats sourced from ScalpChannel telemetry +
    lifecycle counters from ``_signal_history``."""
    channels = getattr(engine, "_channels", []) or []
    scalp = next(
        (c for c in channels if c.__class__.__name__ == "ScalpChannel"),
        None,
    )
    telemetry: Dict[str, Dict[str, int]] = {}
    if scalp is not None:
        # Read directly — calling consume_generation_telemetry() resets state.
        raw = getattr(scalp, "_generation_telemetry", {}) or {}
        telemetry = {stage: dict(counts) for stage, counts in raw.items()}

    attempts = telemetry.get("attempts", {})
    generated = telemetry.get("generated", {})
    no_signal = telemetry.get("no_signal", {})

    history = list(getattr(engine, "_signal_history", []) or [])
    router = getattr(engine, "router", None)
    active = list(router.active_signals.values()) if router is not None else []
    lifecycle = _lifecycle_stats_by_setup(active + history)

    items: List[AgentStat] = []
    for path_token, setup_class in _PATH_TO_SETUP.items():
        bucket = lifecycle.get(setup_class.upper(), {})
        items.append(
            AgentStat(
                evaluator=path_token,
                setup_class=setup_class,
                display_name=_AGENT_DISPLAY_NAMES.get(setup_class, setup_class),
                # Per-evaluator toggles aren't in the engine yet — every
                # evaluator runs whenever its parent channel is enabled.
                enabled=True,
                attempts=int(attempts.get(path_token, 0) or 0),
                generated=int(generated.get(path_token, 0) or 0),
                no_signal=int(no_signal.get(path_token, 0) or 0),
                closed_today=int(bucket.get("closed_today", 0) or 0),
                tp_hits=int(bucket.get("tp_hits", 0) or 0),
                sl_hits=int(bucket.get("sl_hits", 0) or 0),
                invalidated=int(bucket.get("invalidated", 0) or 0),
                last_signal_age_minutes=bucket.get("last_signal_age_minutes"),
            )
        )
    return items
