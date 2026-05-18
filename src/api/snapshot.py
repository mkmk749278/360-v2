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

from src.utils import get_logger

from .schemas import (
    ActivityEvent,
    AgentStat,
    AutoModeStatus,
    PositionDetail,
    PositionDiagDetail,
    PositionsDiagResponse,
    PulseSnapshot,
    SignalDetail,
    TickerItem,
)

log = get_logger("api.snapshot")


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
    # Open-position count: prefer the paper broker's ``_positions`` dict
    # when wired (paper mode) because that's the same source ``/api/positions``
    # filters by — so the Pulse header always agrees with the OPEN
    # POSITIONS list below it.  Falls back to ``RiskManager`` for live
    # mode (where the broker has no in-process positions dict — real
    # positions live on Binance) and for unwired test fixtures.
    #
    # Owner-reported bug 2026-05-18: header showed "Open positions: 4"
    # while the list rendered "No open positions" — the two reads were
    # off different counters that had drifted.  Reading from the same
    # source eliminates the visible inconsistency regardless of
    # whether the underlying drift is fully healed.
    open_positions = 0
    if rm is not None:
        open_positions = rm.open_position_count
    broker = getattr(engine, "_order_manager", None)
    if broker is not None:
        _bp = getattr(broker, "_positions", None)
        if isinstance(_bp, dict):
            open_positions = sum(
                1
                for p in _bp.values()
                if (
                    float(getattr(p, "quantity", 0.0) or 0.0)
                    - float(getattr(p, "closed_quantity", 0.0) or 0.0)
                )
                > 1e-9
            )

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

    # Defensive filter — ``router.active_signals`` can briefly hold signals
    # that hit a terminal status (INVALIDATED / SL_HIT / TP_HIT / EXPIRED /
    # CANCELLED) before TradeMonitor pops them, AND the persistent
    # active-router-state JSON loader (PR #337) restores any signal that
    # was in the map at shutdown — including ones that closed mid-shutdown.
    # Owner reported INVALIDATED + SL_HIT signals showing in the app's
    # "Open" tab; this filter guarantees the API contract matches the
    # subscriber's mental model: "Open" = currently in-flight only.
    if status == "open":
        signals = [
            s for s in active
            if str(getattr(s, "status", "")).upper() == "ACTIVE"
        ]
    elif status == "closed":
        # Symmetric — anything in active_signals that has a terminal
        # status belongs in the closed bucket too, not orphaned between
        # the two views.
        terminal_active = [
            s for s in active
            if str(getattr(s, "status", "")).upper() != "ACTIVE"
        ]
        signals = history + terminal_active
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

    Per-signal exceptions are caught and logged so a single corrupted
    entry in ``router.active_signals`` (e.g. from a partial restore where
    a field has gone out of sync with the schema) doesn't 500 the whole
    Trade tab.

    Broker-state enrichment (2026-05-17, owner-reported bug): when a
    paper ``_order_manager`` is wired AND has a ``_positions`` dict,
    cross-reference each router signal with the broker's view.  Signals
    where the broker has no current position (e.g., ``qty_zero_guard``
    from PR #401 caught a degenerate input and ``open_position``
    returned None, OR the broker already fully closed but the router
    is still tracking the signal for terminal SL/TP/INVALIDATED) are
    excluded from the positions display.  Without this filter the
    OPEN POSITIONS card showed phantom rows at ``qty 0.0`` — owner
    saw 4-5 ghost positions alongside the one real one
    (AIAUSDT/qty 248.08) in trade_records.

    Live-mode broker has no in-process ``_positions`` dict (real
    positions live on Binance, queried app-side via BinanceClient);
    in that case we skip the cross-reference and fall back to the
    pre-2026-05-17 behaviour where every router signal renders.
    """
    router = getattr(engine, "router", None)
    if router is None:
        return []

    # Broker-state lookup (paper-mode only).  Treat the broker's
    # ``_positions`` dict as the source of truth for "is there an
    # active position for this signal_id?" — even when ``sig.qty``
    # is zero (because nothing ever sets it on the Signal class).
    broker = getattr(engine, "_order_manager", None)
    broker_positions: Optional[dict] = None
    if broker is not None:
        _bp = getattr(broker, "_positions", None)
        if isinstance(_bp, dict):
            broker_positions = _bp

    out: List[PositionDetail] = []
    for sig in router.active_signals.values():
        try:
            signal_id = getattr(sig, "signal_id", "") or ""
            # Broker-state filter — skip phantom entries.  When a paper
            # broker is wired but has no record of this signal_id,
            # ``open_position`` either rejected (qty_zero_guard,
            # notional_floor, risk gate) or already fully closed.  Either
            # way the OPEN POSITIONS card should not display a row.
            if broker_positions is not None and signal_id not in broker_positions:
                continue

            direction = getattr(sig, "direction", None)
            direction_str = (
                direction.value
                if direction is not None and hasattr(direction, "value")
                else str(direction or "LONG")
            ).upper()
            # Pydantic Literal["LONG", "SHORT"] rejects anything else —
            # default to LONG if a corrupted signal has a stray value
            # rather than failing the whole response.
            if direction_str not in ("LONG", "SHORT"):
                log.warning(
                    "build_positions: signal %s has invalid direction %r — "
                    "defaulting to LONG",
                    getattr(sig, "signal_id", "?"), direction_str,
                )
                direction_str = "LONG"
            entry = float(getattr(sig, "entry", 0.0) or 0.0)
            current_price = float(getattr(sig, "current_price", entry) or entry)
            pnl_pct = float(getattr(sig, "pnl_pct", 0.0) or 0.0)

            # Quantity sourcing — prefer the broker's truthful number over
            # the (always-zero, never-set) ``sig.qty`` attribute.  The
            # broker also knows the residual after partial closes via
            # ``quantity - closed_quantity``, which is the right value
            # for an OPEN position display (closed_quantity is what's
            # already realised; the residual is what's still riding).
            qty = float(getattr(sig, "qty", 0.0) or 0.0)
            pnl_usd = float(getattr(sig, "pnl_usd", 0.0) or 0.0)
            if broker_positions is not None and signal_id in broker_positions:
                _bp_pos = broker_positions[signal_id]
                _total_qty = float(getattr(_bp_pos, "quantity", 0.0) or 0.0)
                _closed_qty = float(getattr(_bp_pos, "closed_quantity", 0.0) or 0.0)
                _residual = max(_total_qty - _closed_qty, 0.0)
                if _residual > 0:
                    qty = _residual
            if pnl_usd == 0.0 and entry > 0:
                pnl_usd = round(qty * entry * pnl_pct / 100.0, 2)
            ts = getattr(sig, "timestamp", None)
            out.append(
                PositionDetail(
                    signal_id=signal_id,
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
        except Exception:
            log.exception(
                "build_positions: skipping malformed signal %s",
                getattr(sig, "signal_id", "?"),
            )
            continue
    return out


def _candle_1m_extremes_and_age(engine: Any, symbol: str) -> tuple:
    """Read (high, low, age_sec) for the last 1m candle of ``symbol``.

    Mirrors ``TradeMonitor._candle_extremes`` but also returns the WS-update
    age so the diag caller can tell stale-feed-vs-monitor-bug apart.  Returns
    ``(0.0, 0.0, None)`` when no store / no candle data is available.
    """
    store = getattr(getattr(engine, "monitor", None), "_store", None)
    if store is None:
        return 0.0, 0.0, None
    high = 0.0
    low = 0.0
    try:
        candles = store.get_candles(symbol, "1m")
        if candles and len(candles.get("high", [])) > 0 and len(candles.get("low", [])) > 0:
            high = float(candles["high"][-1])
            low = float(candles["low"][-1])
    except Exception:
        pass
    age: Optional[float] = None
    try:
        age_fn = getattr(store, "last_kline_age_seconds", None)
        if callable(age_fn):
            raw = age_fn(symbol, "1m")
            if raw is not None:
                age = float(raw)
    except Exception:
        pass
    return high, low, age


def _sl_breach_distance_pct(
    direction: str, entry: float, stop_loss: float, candle_high: float, candle_low: float
) -> Optional[float]:
    """Signed distance from the worst-side wick to SL, in %-of-entry.

    Negative result means the 1m wick has already broken through SL — if the
    signal is still ACTIVE that's a smoking gun for monitor evaluation failure.
    Returns ``None`` when the inputs are not usable (zero entry, no candle).
    """
    if entry <= 0 or stop_loss <= 0 or (candle_high == 0.0 and candle_low == 0.0):
        return None
    if direction == "LONG":
        return round((candle_low - stop_loss) / entry * 100.0, 4)
    if direction == "SHORT":
        return round((stop_loss - candle_high) / entry * 100.0, 4)
    return None


def build_positions_diag(engine: Any) -> PositionsDiagResponse:
    """Operator-facing diag view of the active-signals dict.

    Same source as ``build_positions`` (``router.active_signals``) but
    surfaces the fields ``TradeMonitor._evaluate_signal`` reads — stored
    SL/TP, current 1m candle wick, candle age — so the operator can tell
    apart stale-feed, monitor-bug, and state-sync-gap failure modes when
    a position closes on Binance but stays ACTIVE in the engine.

    Per-signal exceptions are caught and logged; a corrupted entry in
    ``active_signals`` is skipped rather than 500-ing the whole response.
    """
    router = getattr(engine, "router", None)
    monitor = getattr(engine, "monitor", None)
    monitor_running = bool(getattr(monitor, "_running", False)) if monitor is not None else False
    generated_at = datetime.now(timezone.utc)

    if router is None:
        return PositionsDiagResponse(
            items=[], total=0, monitor_running=monitor_running, generated_at=generated_at,
        )

    out: List[PositionDiagDetail] = []
    for sig in router.active_signals.values():
        try:
            direction = getattr(sig, "direction", None)
            direction_str = (
                direction.value
                if direction is not None and hasattr(direction, "value")
                else str(direction or "LONG")
            ).upper()
            if direction_str not in ("LONG", "SHORT"):
                direction_str = "LONG"

            symbol = getattr(sig, "symbol", "") or ""
            entry = float(getattr(sig, "entry", 0.0) or 0.0)
            stop_loss = float(getattr(sig, "stop_loss", 0.0) or 0.0)
            tp1 = float(getattr(sig, "tp1", 0.0) or 0.0)
            tp2 = float(getattr(sig, "tp2", 0.0) or 0.0)
            tp3_raw = getattr(sig, "tp3", None)
            tp3 = float(tp3_raw) if tp3_raw is not None else None
            current_price = float(getattr(sig, "current_price", entry) or entry)

            candle_high, candle_low, candle_age = _candle_1m_extremes_and_age(engine, symbol)
            sl_breach = _sl_breach_distance_pct(
                direction_str, entry, stop_loss, candle_high, candle_low
            )

            out.append(
                PositionDiagDetail(
                    signal_id=getattr(sig, "signal_id", "") or "",
                    symbol=symbol,
                    direction=direction_str,  # type: ignore[arg-type]
                    status=str(getattr(sig, "status", "ACTIVE") or "ACTIVE"),
                    setup_class=str(getattr(sig, "setup_class", "UNCLASSIFIED") or "UNCLASSIFIED"),
                    channel=str(getattr(sig, "channel", "") or ""),
                    entry=entry,
                    stop_loss=stop_loss,
                    tp1=tp1,
                    tp2=tp2,
                    tp3=tp3,
                    current_price=current_price,
                    pnl_pct=float(getattr(sig, "pnl_pct", 0.0) or 0.0),
                    max_favorable_excursion_pct=float(
                        getattr(sig, "max_favorable_excursion_pct", 0.0) or 0.0
                    ),
                    max_adverse_excursion_pct=float(
                        getattr(sig, "max_adverse_excursion_pct", 0.0) or 0.0
                    ),
                    best_tp_hit=int(getattr(sig, "best_tp_hit", 0) or 0),
                    pre_tp_hit=bool(getattr(sig, "pre_tp_hit", False)),
                    candle_1m_high=candle_high,
                    candle_1m_low=candle_low,
                    candle_1m_age_sec=candle_age,
                    sl_breach_distance_pct=sl_breach,
                    minutes_open=_minutes_since(getattr(sig, "timestamp", None)),
                    timestamp=getattr(sig, "timestamp", None),
                    dispatch_timestamp=getattr(sig, "dispatch_timestamp", None),
                    first_sl_touch_timestamp=getattr(sig, "first_sl_touch_timestamp", None),
                    first_tp_touch_timestamp=getattr(sig, "first_tp_touch_timestamp", None),
                    terminal_outcome_timestamp=getattr(sig, "terminal_outcome_timestamp", None),
                )
            )
        except Exception:
            log.exception(
                "build_positions_diag: skipping malformed signal %s",
                getattr(sig, "signal_id", "?"),
            )
            continue

    return PositionsDiagResponse(
        items=out,
        total=len(out),
        monitor_running=monitor_running,
        generated_at=generated_at,
    )


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

    # OPEN events from every signal we know about.  Per-signal try/except
    # so a single corrupted entry doesn't fail the whole feed.
    for sig in pool:
        try:
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
        except Exception:
            log.exception(
                "build_activity: skipping malformed signal %s",
                getattr(sig, "signal_id", "?"),
            )
            continue

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
    # Augment with rolling-window aggregates from the pnl_history ledger.
    # ``mode`` here is the engine's current mode — the ledger keys are
    # paper / live, so for ``off`` we surface zeros (subscribers see
    # no aggregates until they switch to paper or live).
    try:
        from src.auto_trade import pnl_history
        active_mode = info.get("mode", "off")
        if active_mode in ("paper", "live"):
            info["weekly_pnl_usd"] = pnl_history.get_weekly(active_mode)
            info["monthly_pnl_usd"] = pnl_history.get_monthly(active_mode)
    except Exception:
        # Fail-soft — zeros are the right default.
        pass

    # Equity-resets-daily fix (Phase paper-trade visibility, 2026-05-16).
    #
    # ``engine.get_auto_execution_status`` sources ``current_equity_usd``
    # from ``RiskManager.current_equity_usd``, which is computed as
    # ``starting_equity + daily_realised_pnl_usd`` (see
    # ``src/auto_trade/risk_manager.py`` line ~186/189).  Daily PnL only
    # contains today's bucket — so the dashboard "appears to reset to
    # starting_equity at UTC midnight" every day even though the broker's
    # persisted cumulative PnL is intact.  Owner reported this as
    # "paper equity resets daily" (2026-05-16).
    #
    # Fix: in paper mode, prefer the broker's true cumulative equity
    # (``PaperOrderManager.current_equity_usd``) which carries
    # ``_starting_equity + _realised_pnl_total`` and survives restarts /
    # mode toggles via ``data/paper_pnl_state.json``.  Live mode keeps
    # the existing source (exchange-pushed equity), so we touch only the
    # paper read-path.
    try:
        active_mode = info.get("mode", "off")
        om = getattr(engine, "_order_manager", None)
        if (
            active_mode == "paper"
            and om is not None
            and hasattr(om, "current_equity_usd")
        ):
            info["current_equity_usd"] = float(om.current_equity_usd)
    except Exception:
        # Fail-soft — the daily-only figure is still a valid number to
        # render, just stale-feeling at UTC rollover.  Don't 500 the
        # whole Trade tab on a stray broker-attribute issue.
        log.exception(
            "build_auto_mode: failed to override current_equity_usd "
            "from broker — falling back to engine status value"
        )
    return AutoModeStatus(**info)


def build_pnl_history(
    engine: Any, *, mode: Optional[str] = None, days: int = 30
) -> Dict[str, Any]:
    """Daily-bucketed realised PnL series + rolling aggregates.

    Returns a dict matching ``PnlHistoryResponse``.  ``mode`` defaults to
    the engine's current auto-execution mode.
    """
    if mode is None:
        mode = getattr(engine, "_current_auto_mode", "off")
    days = max(1, min(int(days), 365))
    if mode in ("paper", "live"):
        from src.auto_trade import pnl_history
        series = pnl_history.get_history(mode, days=days)
        weekly = pnl_history.get_weekly(mode)
        monthly = pnl_history.get_monthly(mode)
    else:
        # Off-mode: surface an empty series rather than 404.  Client
        # renders an "auto-trade off — no history" empty state.
        from datetime import datetime, timedelta, timezone
        today = datetime.now(timezone.utc).date()
        series = [
            ((today - timedelta(days=offset)).strftime("%Y-%m-%d"), 0.0)
            for offset in range(days - 1, -1, -1)
        ]
        weekly = 0.0
        monthly = 0.0
    return {
        "mode": mode,
        "days": days,
        "items": [{"date": d, "pnl_usd": p} for d, p in series],
        "weekly_pnl_usd": weekly,
        "monthly_pnl_usd": monthly,
    }


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
