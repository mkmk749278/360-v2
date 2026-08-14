"""Engine → Pydantic snapshot adapters.

Pure functions: read the live ``Engine`` instance and return Pydantic
models from :mod:`src.api.schemas`.  Endpoints stay thin; all
serialization quirks live here.

No method here mutates engine state.  ``consume_generation_telemetry()``
on a channel resets its counters — we deliberately read the underlying
``_generation_telemetry`` dict directly to avoid that side-effect.
"""

from __future__ import annotations

import asyncio
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


def _per_user_book(engine: Any, user_id: Optional[int]) -> Optional[Any]:
    """When ``PAPER_PER_USER_BOOKS`` is on and the engine runs a
    :class:`PaperBookFanout`, return the caller's per-user book accessor
    surface (the fanout itself, which exposes ``positions_for_user`` and
    ``pnl_history_mode_for``).  Otherwise None — callers then fall back to
    the shared-ledger + subscription-window read path.

    Gated on the config flag AND duck-typed on the fanout so a stale flag
    against a single shared book can never mis-route reads."""
    if user_id is None:
        return None
    try:
        from config import PAPER_PER_USER_BOOKS
    except Exception:
        return None
    if not PAPER_PER_USER_BOOKS:
        return None
    broker = getattr(engine, "_order_manager", None)
    if broker is not None and hasattr(broker, "positions_for_user"):
        return broker
    return None


def _residual_qty(pos: Any) -> float:
    return max(
        float(getattr(pos, "quantity", 0.0) or 0.0)
        - float(getattr(pos, "closed_quantity", 0.0) or 0.0),
        0.0,
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
    # Session 29 (16th evaluator) — rides a confirmed mover, buys each pullback
    # to the MA stack (long gainers, short losers).
    "MOVER_TREND_PULLBACK": "The Momentum Rider",
    # Anchored-VWAP mover scalp — pullback to the move's VWAP, with the slope.
    "MOVER_AVWAP_SCALP": "The VWAP Rider",
    # 2026-07-15 (18th evaluator) — statistical mean-reversion, graduated live
    # from the SHADOW_MEAN_REVERT shadow unit (+0.67R / 59% win / n=550).
    "MEAN_REVERT": "The Rubber Band",
    # 2026-07-18 (19th evaluator) — range-edge fade to mid, graduated dark +
    # context-gated from the SHADOW_RANGE_FADE shadow unit (allocator top pick
    # in range/quiet contexts, e.g. +0.841R n=24 ASIA/QUIET/NORMAL).
    "RANGE_FADE": "The Range Keeper",
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
    # _evaluate_mover_trend_pullback → MOVER_TREND_PULLBACK.
    "MOVER_TREND_PULLBACK": "MOVER_TREND_PULLBACK",
    # _evaluate_mover_avwap_scalp → MOVER_AVWAP_SCALP.
    "MOVER_AVWAP_SCALP": "MOVER_AVWAP_SCALP",
    # _evaluate_mean_revert → MEAN_REVERT.
    "MEAN_REVERT": "MEAN_REVERT",
    # _evaluate_range_fade → RANGE_FADE.
    "RANGE_FADE": "RANGE_FADE",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _minutes_since(ts: Optional[Any]) -> int:
    """Minutes between ``ts`` and now, naive-tz-aware (assumes UTC
    when no tzinfo is present).

    Tolerant input: accepts ``datetime``, ISO-8601 ``str`` (the
    shape stored on a few signal records that survived a Firestore
    round-trip in production), or ``None``.  An unparseable value
    returns 0 rather than crashing the API request — a stale or
    malformed timestamp shouldn't 5xx the whole snapshot endpoint.

    Hardened 2026-05-20 after a prod ``AttributeError: 'str' object
    has no attribute 'tzinfo'`` traceback on
    ``/api/snapshot`` (and friends) for a signal whose timestamp
    had been serialised through JSON at some point in its life
    cycle.  We can't fix the source (legacy records) — and even
    once we do, defensive parsing here costs us nothing and keeps
    the surface area resilient to future serialisation drift."""
    parsed = _as_datetime(ts)
    if parsed is None:
        return 0
    return max(0, int((_now() - parsed).total_seconds() // 60))


def _as_datetime(ts: Optional[Any]) -> Optional[datetime]:
    """Coerce a lifecycle stamp to a tz-aware ``datetime``, or ``None``.

    The same tolerant parse ``_minutes_since`` needs, factored out so the two
    cannot drift: a stamp that counts as unreadable for the "N ago" label must
    also be unreadable when we publish the instant itself.

    Returns ``None`` rather than a guess.  A consumer plotting this on a chart
    can then omit its marker instead of drawing one at a fabricated time —
    which is the failure this whole change exists to end.
    """
    if ts is None:
        return None
    if isinstance(ts, str):
        try:
            # Accept the common shapes: ``2026-05-20T04:25:00Z`` (Z
            # suffix → not native to ``fromisoformat`` until 3.11),
            # ``2026-05-20T04:25:00+00:00``, naive ``2026-05-20T04:25:00``.
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None
    if not isinstance(ts, datetime):
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts


def _agent_name_for(setup_class: str) -> str:
    return _AGENT_DISPLAY_NAMES.get(setup_class, "Engine")


# ---------------------------------------------------------------------------
# Pulse
# ---------------------------------------------------------------------------


async def build_pulse(
    engine: Any,
    *,
    user_id: Optional[int] = None,
    user_overrides: Any = None,
) -> PulseSnapshot:
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

    # Per-user paper visibility (PR #503, 2026-05-26) — extends PR #478's
    # ``/api/trades`` window filter to the Pulse header so a fresh user
    # who just enabled paper mode doesn't see the operator's engine-wide
    # open-position count + today's PnL on day-zero. Live mode and
    # off-mode keep the engine-wide reads (no per-user paper book exists
    # for live, and off-mode has nothing to show anyway).
    active_mode = getattr(engine, "_current_auto_mode", "off")
    _pu_book = _per_user_book(engine, user_id) if active_mode == "paper" else None
    if _pu_book is not None:
        # Per-user books ON: open count + today's PnL come straight from the
        # caller's own book + ``paper:<uid>`` bucket — no window filtering.
        from src.auto_trade import pnl_history
        mode_key = _pu_book.pnl_history_mode_for(int(user_id))
        today_pnl_usd = await asyncio.to_thread(pnl_history.get_daily, mode_key)
        today_pnl_pct = (
            100.0 * today_pnl_usd / starting_equity
            if starting_equity > 0 else 0.0
        )
        user_positions = _pu_book.positions_for_user(int(user_id))
        open_positions = sum(
            1 for _p in user_positions.values() if _residual_qty(_p) > 1e-9
        )
    elif (
        active_mode == "paper"
        and user_id is not None
        and user_overrides is not None
    ):
        try:
            windows = await asyncio.to_thread(
                user_overrides.get_paper_subscriptions, int(user_id)
            )
        except Exception:
            windows = []
        if windows:
            from src.auto_trade import trade_records
            from src.api.paper_user_view import (
                rolling_pnl_for_user,
                signal_visible_within_any_window,
            )
            try:
                ledger_rows = await asyncio.to_thread(
                    trade_records.list_trades,
                    limit=500, offset=0, include_open=False,
                )
            except Exception:
                ledger_rows = []
            counters = rolling_pnl_for_user(ledger_rows, windows)
            today_pnl_usd = counters["daily_pnl_usd"]
            today_pnl_pct = (
                100.0 * today_pnl_usd / starting_equity
                if starting_equity > 0 else 0.0
            )
            # Open positions: count router signals dispatched within
            # the user's windows that the broker still holds.
            router = getattr(engine, "router", None)
            user_open = 0
            if router is not None:
                for _sig in router.active_signals.values():
                    sig_id = getattr(_sig, "signal_id", "") or ""
                    if broker is not None and isinstance(
                        getattr(broker, "_positions", None), dict
                    ):
                        if sig_id not in broker._positions:
                            continue
                        _bp_pos = broker._positions[sig_id]
                        _residual = max(
                            float(getattr(_bp_pos, "quantity", 0.0) or 0.0)
                            - float(getattr(_bp_pos, "closed_quantity", 0.0) or 0.0),
                            0.0,
                        )
                        if _residual <= 1e-9:
                            continue
                    sig_ts = (
                        getattr(_sig, "dispatch_timestamp", None)
                        or getattr(_sig, "timestamp", None)
                    )
                    if signal_visible_within_any_window(sig_ts, windows):
                        user_open += 1
            open_positions = user_open

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


_TERMINAL_STATUSES: frozenset = frozenset({
    "SL_HIT", "BREAKEVEN_EXIT", "PROFIT_LOCKED", "INVALIDATED",
    "EXPIRED", "CANCELLED", "FULL_TP_HIT", "TP3_HIT", "CLOSED",
})


def _hold_mins(dispatch_ts: Optional[Any], terminal_ts: Optional[Any]) -> Optional[int]:
    """Actual hold duration: dispatch → terminal for closed, dispatch → now for open."""
    if dispatch_ts is None:
        return None
    if isinstance(dispatch_ts, str):
        try:
            dispatch_ts = datetime.fromisoformat(dispatch_ts.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None
    if not isinstance(dispatch_ts, datetime):
        return None
    if dispatch_ts.tzinfo is None:
        dispatch_ts = dispatch_ts.replace(tzinfo=timezone.utc)
    end_ts = terminal_ts if terminal_ts is not None else _now()
    if isinstance(end_ts, str):
        try:
            end_ts = datetime.fromisoformat(end_ts.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            end_ts = _now()
    if not isinstance(end_ts, datetime):
        end_ts = _now()
    if end_ts.tzinfo is None:
        end_ts = end_ts.replace(tzinfo=timezone.utc)
    return max(0, int((end_ts - dispatch_ts).total_seconds() // 60))


def _original_stop_loss(sig: Any, direction_str: str) -> float:
    """The protective stop the signal was issued with, before BE/trailing shift.

    TradeMonitor mutates ``sig.stop_loss`` in place as a trade progresses (→ entry
    on TP1/break-even, → tp1 later), so the live ``stop_loss`` is *not* the
    original risk geometry. The evaluators stamp ``original_sl_distance`` (entry→SL
    distance) at emit; reconstruct the absolute original stop from it. Fall back to
    the current ``stop_loss`` when the distance was never recorded.
    """
    entry = float(getattr(sig, "entry", 0.0) or 0.0)
    osd = float(getattr(sig, "original_sl_distance", 0.0) or 0.0)
    if osd > 0.0 and entry > 0.0:
        return entry - osd if direction_str == "LONG" else entry + osd
    return float(getattr(sig, "stop_loss", 0.0) or 0.0)


class UnrenderableSignal(ValueError):
    """A candidate object cannot support a signal card.

    Raised — never clamped — by :func:`_signal_to_detail` when the object it
    was handed carries no symbol or no entry price.  ``_signal_to_detail``
    reads every field through ``getattr(..., default)``, so an object that
    merely *looks* signal-shaped (a stub carrying only ``signal_id`` and
    ``dispatch_timestamp``) renders as a complete, confident card with every
    field at its dataclass default: blank symbol, entry/SL/TP1/TP2 all 0.00,
    confidence 0.0, tier "B", setup ``UNCLASSIFIED``, direction LONG, status
    ACTIVE, and an ``open Nh`` age that grows forever because nothing can ever
    close it.  Subscribers saw exactly that on the live Signals tab
    (owner-caught 2026-07-27) whenever the API fell back to building detail
    off ``RedisEngineFacade``.

    A clamp is not a guard (CLAUDE.md): where the input cannot support the
    work, refuse and let the caller record that it doesn't know.
    """


def _signal_to_detail(sig: Any, *, is_open: bool = False) -> SignalDetail:
    symbol = str(getattr(sig, "symbol", "") or "").strip()
    entry_val = float(getattr(sig, "entry", 0.0) or 0.0)
    if not symbol or entry_val <= 0.0:
        raise UnrenderableSignal(
            f"signal_id={getattr(sig, 'signal_id', '?')!r} "
            f"symbol={symbol!r} entry={entry_val!r}"
        )
    direction = getattr(sig, "direction", None)
    direction_str = (
        direction.value
        if direction is not None and hasattr(direction, "value")
        else str(direction or "LONG")
    ).upper()
    setup_class = getattr(sig, "setup_class", "UNCLASSIFIED") or "UNCLASSIFIED"
    # Normalised to tz-aware, because a naive stamp serialises without a zone
    # and a client that parses it gets *local* time: 5h30m of silent error on
    # an IST phone, on the very field a chart anchors its entry marker to.
    # Same ``or _now()`` fallback this line has always had for a missing stamp.
    timestamp = _as_datetime(getattr(sig, "timestamp", None)) or _now()
    status = getattr(sig, "status", "ACTIVE") or "ACTIVE"
    dispatch_ts = getattr(sig, "dispatch_timestamp", None)
    terminal_ts = getattr(sig, "terminal_outcome_timestamp", None)

    # For closed signals minutes_ago reflects recency of the terminal event
    # ("SL_HIT 3m ago"), not the signal's total age since creation.
    # For active signals minutes_ago reflects how long the trade has been open.
    #
    # It is a *label*, and only a label.  The Lumin chart reconstructed the
    # entry instant from it as ``now - minutes_ago``, so on every closed signal
    # the arrow captioned ENTRY was drawn at the exit — offset by the whole
    # hold time (owner-caught 2026-07-29: COTIUSDT stamped 03:00 rendered at
    # 04:05, sitting exactly on its own SL line).  The remedy is not to redefine
    # this field, which is correct for the label it feeds, but to publish the
    # instants themselves below so no consumer has to derive one.
    if status in _TERMINAL_STATUSES and terminal_ts is not None:
        minutes_ago = _minutes_since(terminal_ts)
    elif dispatch_ts is not None:
        minutes_ago = _minutes_since(dispatch_ts)
    else:
        minutes_ago = _minutes_since(timestamp)

    return SignalDetail(
        signal_id=getattr(sig, "signal_id", "") or "",
        symbol=symbol,
        direction=direction_str,  # type: ignore[arg-type]
        entry=entry_val,
        stop_loss=float(getattr(sig, "stop_loss", 0.0) or 0.0),
        original_stop_loss=_original_stop_loss(sig, direction_str),
        tp1=float(getattr(sig, "tp1", 0.0) or 0.0),
        tp2=float(getattr(sig, "tp2", 0.0) or 0.0),
        tp3=getattr(sig, "tp3", None),
        confidence=float(getattr(sig, "confidence", 0.0) or 0.0),
        quality_tier=getattr(sig, "quality_tier", "B") or "B",
        setup_class=setup_class,
        agent_name=_agent_name_for(setup_class),
        status=status,
        is_open=is_open,
        current_price=float(getattr(sig, "current_price", 0.0) or 0.0),
        pnl_pct=float(getattr(sig, "pnl_pct", 0.0) or 0.0),
        max_favorable_excursion_pct=float(
            getattr(sig, "max_favorable_excursion_pct", 0.0) or 0.0
        ),
        max_adverse_excursion_pct=float(
            getattr(sig, "max_adverse_excursion_pct", 0.0) or 0.0
        ),
        best_tp_pnl_pct=float(getattr(sig, "best_tp_pnl_pct", 0.0) or 0.0),
        pre_tp_hit=bool(getattr(sig, "pre_tp_hit", False)),
        pre_tp_threshold_pct=float(
            getattr(sig, "pre_tp_threshold_pct", 0.0) or 0.0
        ),
        pre_tp_trigger_price=(
            float(getattr(sig, "pre_tp_trigger_price", 0.0) or 0.0) or None
        ),
        timestamp=timestamp,
        minutes_ago=minutes_ago,
        # The instants themselves, so a chart plots what happened rather than
        # arithmetic on a label.  ``terminal_outcome_timestamp`` is published
        # only for a signal that has actually terminated: on an open signal it
        # is absent because there is no exit yet, which is a different state
        # from "closed but the stamp predates the field", and both must read as
        # "no marker" rather than as a guess.
        dispatch_timestamp=_as_datetime(dispatch_ts),
        terminal_outcome_timestamp=(
            _as_datetime(terminal_ts) if status in _TERMINAL_STATUSES else None
        ),
        hold_mins=_hold_mins(dispatch_ts, terminal_ts if status in _TERMINAL_STATUSES else None),
        # Regime stamps (scanner._populate_signal_context). Surfaced so the
        # Ops Profit-Lab / combo analyzer can slice by the same entry_regime
        # the FSM uses to route exits (§3.2b). Empty string when unavailable.
        entry_regime=str(getattr(sig, "entry_regime", "") or ""),
        entry_regime_15m=str(getattr(sig, "entry_regime_15m", "") or ""),
        pair_admission=str(getattr(sig, "pair_admission", "") or ""),
        promotion_age_sec=float(getattr(sig, "promotion_age_sec", -1.0) or -1.0),
        promotion_change_pct=getattr(sig, "promotion_change_pct", None),
        market_phase=str(getattr(sig, "market_phase", "") or ""),
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

    # Open/closed truth (2026-07-10): membership in the active book minus
    # terminal statuses IS the discriminator — the status string alone can't
    # be.  Under BE-then-TP1 a non-mover CLOSES with status TP1_HIT (popped
    # from the book), while under the mover runner exit (2026-07-09) a mover
    # with TP1_HIT/TP2_HIT is still OPEN, trail riding the remainder.  The
    # pre-fix ``status == "ACTIVE"`` open filter made open runner movers
    # vanish from the app's Open tab mid-trade.
    #
    # The terminal-status exclusion stays defensive: ``router.active_signals``
    # can briefly hold signals that hit a terminal status before TradeMonitor
    # pops them, AND the persistent active-router-state JSON loader (PR #337)
    # restores any signal that was in the map at shutdown — including ones
    # that closed mid-shutdown.
    def _sig_is_open(s: Any) -> bool:
        return str(getattr(s, "status", "")).upper() not in _TERMINAL_STATUSES

    open_ids = {
        id(s) for s in active if _sig_is_open(s)
    }
    if status == "open":
        signals = [s for s in active if _sig_is_open(s)]
    elif status == "closed":
        # Symmetric — anything in active_signals that has a terminal
        # status belongs in the closed bucket too, not orphaned between
        # the two views.
        terminal_active = [s for s in active if not _sig_is_open(s)]
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
    # Refuse — and count — anything that cannot support a card, rather than
    # publishing a zeroed shell.  A drop here is never routine: it means a
    # caller handed us objects that are not signals (see UnrenderableSignal),
    # so it goes through fail_open so the liveness watchdog pages instead of
    # the app quietly showing phantoms.
    out: List[SignalDetail] = []
    for s in signals[:limit]:
        try:
            out.append(_signal_to_detail(s, is_open=id(s) in open_ids))
        except UnrenderableSignal as exc:
            from src import fail_open
            fail_open.record("api.snapshot.unrenderable_signal", exc)
    return out


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------


async def build_positions(
    engine: Any,
    *,
    user_id: Optional[int] = None,
    user_overrides: Any = None,
) -> List[PositionDetail]:
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

    # Per-user paper visibility (PR #503, 2026-05-26) — fresh users in
    # paper mode see only positions opened within their subscription
    # windows. Live mode keeps engine-wide router visibility because
    # there's no per-user paper book to filter against (true per-user
    # live execution lives on Phase 3's per-user FSM workers).
    active_mode = getattr(engine, "_current_auto_mode", "off")
    user_windows: list = []
    _pu_book = _per_user_book(engine, user_id) if active_mode == "paper" else None
    if _pu_book is None and (
        active_mode == "paper"
        and user_id is not None
        and user_overrides is not None
    ):
        try:
            user_windows = await asyncio.to_thread(
                user_overrides.get_paper_subscriptions, int(user_id)
            )
        except Exception:
            user_windows = []

    # Broker-state lookup (paper-mode only).  Treat the broker's
    # ``_positions`` dict as the source of truth for "is there an
    # active position for this signal_id?" — even when ``sig.qty``
    # is zero (because nothing ever sets it on the Signal class).
    #
    # Per-user books ON: the caller's own book IS the visibility boundary —
    # only signals it holds render, so no subscription-window filter is used.
    broker = getattr(engine, "_order_manager", None)
    broker_positions: Optional[dict] = None
    if _pu_book is not None:
        broker_positions = _pu_book.positions_for_user(int(user_id))
    elif broker is not None:
        _bp = getattr(broker, "_positions", None)
        if isinstance(_bp, dict):
            broker_positions = _bp

    out: List[PositionDetail] = []
    # Lazy import — only when paper-mode + windows are wired.
    if user_windows:
        from src.api.paper_user_view import signal_visible_within_any_window
    for sig in router.active_signals.values():
        try:
            signal_id = getattr(sig, "signal_id", "") or ""
            # Per-user paper window filter (PR #503).  Skip positions
            # whose dispatch time falls outside the caller's
            # subscription windows — fresh users on day-zero see an
            # empty list even when the engine has open paper positions
            # from the operator's earlier session.
            if user_windows:
                sig_ts = (
                    getattr(sig, "dispatch_timestamp", None)
                    or getattr(sig, "timestamp", None)
                )
                if not signal_visible_within_any_window(sig_ts, user_windows):
                    continue
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
    if monitor is not None:
        # Single-process mode: the real engine exposes the live monitor object.
        monitor_running = bool(getattr(monitor, "_running", False))
    else:
        # Isolated mode: ``engine`` is the RedisEngineFacade, which has no
        # ``.monitor`` object — the TradeMonitor runs in the engine container.
        # Deriving liveness from the absent attribute always reported NO, a
        # false negative on the Positions tab since the isolation cutover.
        # Use the published task census instead: ``trade_monitor`` present in
        # ``background_tasks`` means the coroutine is alive (same source D2 uses).
        monitor_running = False
        _census = getattr(engine, "get_background_task_census", None)
        if callable(_census):
            try:
                monitor_running = any("trade_monitor" in t for t in _census())
            except Exception:
                monitor_running = False
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


async def build_auto_mode(
    engine: Any,
    *,
    user_id: Optional[int] = None,
    user_overrides: Any = None,
    starting_equity_usd: Optional[float] = None,
) -> AutoModeStatus:
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
        try:
            from config import PAPER_PER_USER_BOOKS as _PPUB
        except Exception:
            _PPUB = False
        active_mode = info.get("mode", "off")
        if active_mode == "paper" and _PPUB:
            # Engine-wide paper = SUM across every per-user ``paper:<uid>``.
            info["weekly_pnl_usd"] = await asyncio.to_thread(
                pnl_history.get_weekly_aggregate, "paper"
            )
            info["monthly_pnl_usd"] = await asyncio.to_thread(
                pnl_history.get_monthly_aggregate, "paper"
            )
        elif active_mode in ("paper", "live"):
            info["weekly_pnl_usd"] = await asyncio.to_thread(
                pnl_history.get_weekly, active_mode
            )
            info["monthly_pnl_usd"] = await asyncio.to_thread(
                pnl_history.get_monthly, active_mode
            )
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

    # Per-user paper visibility (PR #503, 2026-05-26) — extends PR #478
    # ``/api/trades`` window filter to the Trade-tab header so a fresh
    # user who just enabled paper mode sees:
    #   * equity = PAPER_STARTING_EQUITY (default $1000)
    #   * open_positions = 0
    #   * daily / weekly / monthly / total = 0.0
    # Without this, the engine's shared paper book (operator's prior
    # trades + still-open positions from before signup) leaks onto the
    # fresh subscriber's day-zero Trade tab — owner-reported 2026-05-26
    # via screenshot showing $963.97 equity + 4 open positions on a
    # brand-new install.
    #
    # Live mode is untouched — true per-user live execution PnL is a
    # Phase 3 build (per-user Binance ledgers via ``signal_dispatch``
    # + the signing service); this filter is paper-only.
    try:
        active_mode = info.get("mode", "off")
        _pu_book = (
            _per_user_book(engine, user_id) if active_mode == "paper" else None
        )
        if _pu_book is not None:
            # Per-user books ON: the Trade-tab header reads the caller's own
            # book + ``paper:<uid>`` bucket directly — no window filtering.
            from src.auto_trade import pnl_history
            mode_key = _pu_book.pnl_history_mode_for(int(user_id))
            book = _pu_book.book_for_user(int(user_id))
            if starting_equity_usd is not None:
                _baseline = float(starting_equity_usd)
            elif book is not None and hasattr(book, "_starting_equity"):
                _baseline = float(getattr(book, "_starting_equity", 1000.0))
            else:
                _baseline = 1000.0
            daily = await asyncio.to_thread(pnl_history.get_daily, mode_key)
            weekly = await asyncio.to_thread(pnl_history.get_weekly, mode_key)
            monthly = await asyncio.to_thread(pnl_history.get_monthly, mode_key)
            user_positions = _pu_book.positions_for_user(int(user_id))
            user_open = sum(
                1 for _p in user_positions.values() if _residual_qty(_p) > 1e-9
            )
            info["daily_pnl_usd"] = daily
            info["weekly_pnl_usd"] = weekly
            info["monthly_pnl_usd"] = monthly
            if book is not None and hasattr(book, "current_equity_usd"):
                info["current_equity_usd"] = float(book.current_equity_usd)
                info["simulated_pnl_usd"] = round(
                    float(book.current_equity_usd) - _baseline, 4
                )
            else:
                info["current_equity_usd"] = round(_baseline + daily, 4)
            info["open_positions"] = user_open
            info["daily_loss_pct"] = (
                round(100.0 * daily / _baseline, 4) if _baseline > 0 else 0.0
            )
            return AutoModeStatus(**info)
        if (
            active_mode == "paper"
            and user_id is not None
            and user_overrides is not None
        ):
            try:
                windows = await asyncio.to_thread(
                    user_overrides.get_paper_subscriptions, int(user_id)
                )
            except Exception:
                windows = []
            from src.api.paper_user_view import (
                rolling_pnl_for_user,
                signal_visible_within_any_window,
            )
            from src.auto_trade import trade_records
            try:
                ledger_rows = await asyncio.to_thread(
                    trade_records.list_trades,
                    limit=500, offset=0, include_open=False,
                )
            except Exception:
                ledger_rows = []
            counters = rolling_pnl_for_user(ledger_rows, windows)

            # Resolve the user's equity baseline. Default to the
            # broker's configured starting equity so per-user equity
            # mirrors the engine's paper-book starting line; allow an
            # explicit override (test fixtures, future per-user starting
            # equity from settings).
            om = getattr(engine, "_order_manager", None)
            if starting_equity_usd is not None:
                _baseline = float(starting_equity_usd)
            elif om is not None and hasattr(om, "_starting_equity"):
                _baseline = float(getattr(om, "_starting_equity", 1000.0))
            else:
                _baseline = 1000.0

            # Open positions: count router signals dispatched within
            # the user's windows that the broker still holds (matches
            # ``build_positions`` filter exactly).
            router = getattr(engine, "router", None)
            broker = om
            broker_positions: Optional[Dict[str, Any]] = None
            if broker is not None:
                _bp = getattr(broker, "_positions", None)
                if isinstance(_bp, dict):
                    broker_positions = _bp
            user_open = 0
            if router is not None:
                for _sig in router.active_signals.values():
                    sig_id = getattr(_sig, "signal_id", "") or ""
                    if broker_positions is not None:
                        if sig_id not in broker_positions:
                            continue
                        _bp_pos = broker_positions[sig_id]
                        _residual = max(
                            float(getattr(_bp_pos, "quantity", 0.0) or 0.0)
                            - float(getattr(_bp_pos, "closed_quantity", 0.0) or 0.0),
                            0.0,
                        )
                        if _residual <= 1e-9:
                            continue
                    sig_ts = (
                        getattr(_sig, "dispatch_timestamp", None)
                        or getattr(_sig, "timestamp", None)
                    )
                    if signal_visible_within_any_window(sig_ts, windows):
                        user_open += 1

            # Apply the windowed counters. Empty windows → all zeros
            # (rolling_pnl_for_user already short-circuits on empty
            # windows). The user sees $1000 starting equity + their
            # own visible PnL drift.
            info["daily_pnl_usd"] = counters["daily_pnl_usd"]
            info["weekly_pnl_usd"] = counters["weekly_pnl_usd"]
            info["monthly_pnl_usd"] = counters["monthly_pnl_usd"]
            info["simulated_pnl_usd"] = counters["total_pnl_usd"]
            info["current_equity_usd"] = round(
                _baseline + counters["total_pnl_usd"], 4
            )
            info["open_positions"] = user_open
            # Daily-loss percent recomputed against the baseline so the
            # per-user "x% of starting equity" stays consistent with the
            # rest of the per-user view. ``daily_kill_tripped`` and
            # ``manual_paused`` remain engine-wide — they're safety
            # state, not per-user accounting.
            info["daily_loss_pct"] = (
                round(100.0 * counters["daily_pnl_usd"] / _baseline, 4)
                if _baseline > 0 else 0.0
            )
    except Exception:
        # Fail-soft: any error in the per-user filter falls back to the
        # engine-wide values already set on ``info``. The right user-
        # visible state is "see the engine-wide book" rather than 500ing
        # the whole Trade tab.
        log.exception(
            "build_auto_mode: per-user paper filter failed — "
            "falling back to engine-wide values"
        )
    return AutoModeStatus(**info)


async def build_pnl_history(
    engine: Any,
    *,
    mode: Optional[str] = None,
    days: int = 30,
    user_id: Optional[int] = None,
    user_overrides: Any = None,
) -> Dict[str, Any]:
    """Daily-bucketed realised PnL series + rolling aggregates.

    Returns a dict matching ``PnlHistoryResponse``.  ``mode`` defaults to
    the engine's current auto-execution mode.

    Per-user filtering (2026-05-24): when both ``user_id`` AND
    ``user_overrides`` are supplied AND the user has paper subscription
    windows, the paper-mode series is filtered to trades closed during
    their windows (extends the per-user visibility pattern shipped in
    #478 for ``/api/trades``). Without this, every paper user saw the
    same engine-wide ``pnl_history.json`` line — owner-reported "lots
    of confusion" 2026-05-24 where the in-app "PAPER P&L TODAY" implied
    per-user but was engine-wide.

    Fall-back: any missing piece (``user_id=None``, ``user_overrides``
    not wired, no subscription windows, or live mode) returns the
    engine-wide ledger as before. Live-mode per-user PnL is a Phase 4
    build — each user has their own Binance ledger; per-user
    reconciliation against ``dispatch_log`` ships later.
    """
    if mode is None:
        mode = getattr(engine, "_current_auto_mode", "off")
    days = max(1, min(int(days), 365))
    if mode == "paper":
        _pu_book = _per_user_book(engine, user_id)
        if _pu_book is not None:
            # Per-user books ON: read the caller's own ``paper:<uid>`` series.
            from src.auto_trade import pnl_history
            mode_key = _pu_book.pnl_history_mode_for(int(user_id))
            series = await asyncio.to_thread(
                pnl_history.get_history, mode_key, days=days
            )
            weekly = await asyncio.to_thread(pnl_history.get_weekly, mode_key)
            monthly = await asyncio.to_thread(pnl_history.get_monthly, mode_key)
            return {
                "mode": mode,
                "days": days,
                "items": [{"date": d, "pnl_usd": v} for d, v in series],
                "weekly_pnl_usd": weekly,
                "monthly_pnl_usd": monthly,
            }
        windows: list = []
        if user_id is not None and user_overrides is not None:
            try:
                windows = await asyncio.to_thread(
                    user_overrides.get_paper_subscriptions, int(user_id)
                )
            except Exception:
                windows = []
        if windows:
            from src.auto_trade import trade_records
            from src.api.paper_user_view import pnl_history_for_user
            # Pull a generous slice — the filter is O(N) on
            # the result. The 500-row cap matches list_trades' own
            # built-in upper bound. Date filtering is handled inside
            # pnl_history_for_user via the day-bucket range.
            ledger_rows = await asyncio.to_thread(
                trade_records.list_trades,
                limit=500, offset=0, include_open=False,
            )
            series, weekly, monthly = pnl_history_for_user(
                ledger_rows, windows, days=days,
            )
        else:
            from src.auto_trade import pnl_history
            series = await asyncio.to_thread(pnl_history.get_history, mode, days=days)
            weekly = await asyncio.to_thread(pnl_history.get_weekly, mode)
            monthly = await asyncio.to_thread(pnl_history.get_monthly, mode)
    elif mode == "live":
        from src.auto_trade import pnl_history
        series = await asyncio.to_thread(pnl_history.get_history, mode, days=days)
        weekly = await asyncio.to_thread(pnl_history.get_weekly, mode)
        monthly = await asyncio.to_thread(pnl_history.get_monthly, mode)
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


# ---------------------------------------------------------------------------
# Pairs view — regular (scanned universe) + promoting (live mover-promoted).
# Diagnostic for "are the promoting pairs actually updating?" — surfaced on the
# ops Pairs page. Built live from pair_mgr + scanner in single-process; in
# isolated mode the engine writes the same payload into engine_state and the
# facade replays it (see RedisEngineFacade.published_pairs).
# ---------------------------------------------------------------------------


def collect_pairs_live(engine: Any) -> Dict[str, Any]:
    """Build the pairs payload directly from the live engine objects.

    ``regular`` = the scanned universe (pair_mgr.pairs) with tier + 24h volume
    and 24h % change. ``promoting`` = the scanner's currently mover-promoted
    pairs with cycles-remaining, enriched with the same volume/change. Both are
    plain dicts so the payload round-trips through Redis unchanged.
    """
    regular: List[Dict[str, Any]] = []
    promoting: List[Dict[str, Any]] = []

    scanner = getattr(engine, "_scanner", None)
    promoted = getattr(scanner, "_mover_promoted_pairs", None) if scanner is not None else None
    _promoted_keys = set(promoted) if isinstance(promoted, dict) else set()

    pair_mgr = getattr(engine, "pair_mgr", None)
    pairs = getattr(pair_mgr, "pairs", None) if pair_mgr is not None else None
    if isinstance(pairs, dict):
        for sym, info in pairs.items():
            # A synthetically-admitted mover lives in pair_mgr AND the promoted
            # set — show it only under Promoting, not Regular.
            if sym in _promoted_keys:
                continue
            tier = getattr(info, "tier", None)
            regular.append({
                "symbol": sym,
                "tier": getattr(tier, "value", str(tier)) if tier is not None else "?",
                "volume_24h_usd": float(getattr(info, "volume_24h_usd", 0.0) or 0.0),
                "change_24h_pct": float(getattr(info, "volatility_24h", 0.0) or 0.0),
                # The signed sibling.  ``change_24h_pct`` is an ABSOLUTE move
                # (it is ``volatility_24h``), which is right for ranking and
                # wrong for a column headed "24h Δ%".  None = not reported.
                "change_24h_signed_pct": getattr(info, "change_24h_signed_pct", None),
            })
        regular.sort(key=lambda r: (r["tier"], -r["volume_24h_usd"]))

    if isinstance(promoted, dict):
        # Enrich from pair_mgr directly (promoted pairs are now excluded from the
        # `regular` list, so we can't read volume/%change off those rows).
        info_pairs = pairs if isinstance(pairs, dict) else {}
        # Per-symbol "why isn't this mover firing" — the last outcome of the two
        # mover continuation paths (fired / no_reclaim / mover_run_too_small / …),
        # captured live on the ScalpChannel. Lets the ops Pairs page answer the
        # question directly instead of inferring it from cumulative truth-report
        # counters. Empty dict if the channel isn't reachable (isolated facade).
        mover_reasons: Dict[str, Any] = {}
        channels = getattr(engine, "_channels", []) or []
        scalp = next(
            (c for c in channels if c.__class__.__name__ == "ScalpChannel"), None
        )
        if scalp is not None and hasattr(scalp, "mover_last_reasons"):
            try:
                mover_reasons = scalp.mover_last_reasons() or {}
            except Exception:
                mover_reasons = {}
        # The promoted dict value is the monotonic EXPIRY time (scanner runs in
        # this same process, so time.monotonic() is comparable). Surface the
        # remaining hold as minutes so the ops Pairs page reads "expires in N min".
        _mono = time.monotonic()
        # The dynamic-retention verdict for each held pair, read off the same
        # module the promotion loop scores with — never recomputed here.  A
        # second scorer in the display layer would be a mirror, and the fix for
        # a drifting mirror is not a second mirror.  `None` on every field means
        # this build has no retention window for the pair, which is not the
        # same as a pair scored and held: the page must be able to tell them
        # apart, so the keys are present and empty rather than absent.
        _ret_rows: Dict[str, Any] = {}
        try:
            from src import mover_retention as _mr

            for _r in _mr.get_retention().report().get("pairs", []) or []:
                _ret_rows[str(_r.get("symbol") or "")] = _r
        except Exception:
            _ret_rows = {}
        for sym, expiry in promoted.items():
            info = info_pairs.get(sym)
            rj = mover_reasons.get(sym) or {}
            rt = _ret_rows.get(sym) or {}
            promoting.append({
                "symbol": sym,
                "minutes_left": round(max(0.0, (float(expiry or 0.0) - _mono) / 60.0), 1),
                "volume_24h_usd": float(getattr(info, "volume_24h_usd", 0.0) or 0.0),
                "change_24h_pct": float(getattr(info, "volatility_24h", 0.0) or 0.0),
                # The signed sibling.  ``change_24h_pct`` is an ABSOLUTE move
                # (it is ``volatility_24h``), which is right for ranking and
                # wrong for a column headed "24h Δ%".  None = not reported.
                "change_24h_signed_pct": getattr(info, "change_24h_signed_pct", None),
                "reject_reason": rj.get("reason"),
                "reject_path": rj.get("path"),
                "reject_age_sec": rj.get("age_sec"),
                # Retention: what the pair has DONE with its slot, and the
                # verdict that follows from it. `verdict` is what the promotion
                # loop would act on; whether it does is `retention.enforcing`
                # below, published once rather than repeated per row.
                "retention_verdict": rt.get("verdict"),
                "retention_reason": rt.get("reason"),
                "retention_age_sec": rt.get("age_sec"),
                "retention_scans": rt.get("scans"),
                "retention_candidates": rt.get("candidates"),
                "retention_reached_enqueue": rt.get("reached_enqueue"),
                "retention_enqueued": rt.get("enqueued"),
                "retention_dark": rt.get("dark"),
                "retention_burst": rt.get("last_burst"),
                "promotion_source": rt.get("source"),
                # Top gainer or top loser — the distinction the promotion path
                # discards (`abs(change_pct)`) and the one the delivered book
                # says matters most. `gainer` is tri-state: None means no
                # reading, never "loser".
                "promotion_change_pct": rt.get("change_pct"),
                "promotion_gainer": rt.get("gainer"),
            })
        promoting.sort(key=lambda r: -r["minutes_left"])

    # Ignition-feed health so an empty promoting list is self-explanatory:
    # frames flowing + symbols tracked but no recent ignition ⇒ genuinely quiet;
    # zero frames / not connected ⇒ stalled feed.
    ignition: Dict[str, Any] = {}
    detector = getattr(engine, "_mover_ignition", None)
    if detector is not None and hasattr(detector, "stats"):
        try:
            ignition = dict(detector.stats())
        except Exception:
            ignition = {}
    ws_mover = getattr(engine, "_ws_futures_mover", None)
    if ws_mover is not None:
        ignition["ws_connected"] = bool(getattr(ws_mover, "is_healthy", False))
        ignition["ws_streams"] = int(getattr(ws_mover, "stream_count", 0) or 0)

    # The retention lane's own health, beside the rows it scores. Published
    # whether or not anything was released: a block that appears only when it
    # acts teaches the reader that its absence means "nothing to release",
    # when it equally means the scorer stopped running.
    retention: Dict[str, Any] = {}
    try:
        from src import mover_retention as _mr

        retention = _mr.get_retention().report()
    except Exception as exc:  # noqa: BLE001
        retention = {"error": str(exc)}

    return {
        "regular": regular,
        "promoting": promoting,
        "regular_count": len(regular),
        "promoting_count": len(promoting),
        "ignition": ignition,
        "retention": retention,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def build_pairs(engine: Any) -> Dict[str, Any]:
    """Pairs payload for ``/api/pairs`` — works in both process modes.

    Single-process: builds live from the real engine. Isolated: the API's
    facade exposes ``published_pairs`` (replayed from engine_state); use it so
    the promoting list reflects the engine container's in-memory scanner state.
    """
    published = getattr(engine, "published_pairs", None)
    if callable(published):
        payload = published()
        if payload:
            return payload
    return collect_pairs_live(engine)
