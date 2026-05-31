"""Trade monitor – continuously checks active signals for TP/SL/trailing updates.

Runs as an async loop, polling the latest price for each active signal and
updating status, PnL, trailing stop, and posting updates to Telegram.
"""

from __future__ import annotations

import asyncio
import os
import numpy as np
from typing import Any, Callable, Coroutine, Dict, Optional

from config import (
    ALL_CHANNELS,
    CHANNEL_TELEGRAM_MAP,
    INVALIDATION_ADVERSE_EXCURSION_FRACTION,
    INVALIDATION_ADVERSE_EXCURSION_FRACTION_BY_SETUP,
    INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_BY_SETUP,
    INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC,
    INVALIDATION_CONSECUTIVE_THRESHOLD,
    INVALIDATION_MIN_AGE_SECONDS,
    INVALIDATION_MOMENTUM_THRESHOLD,
    MAX_SIGNAL_HOLD_SECONDS,
    MIN_SIGNAL_LIFESPAN_SECONDS,
    MONITOR_POLL_INTERVAL,
    PRE_TP_ATR_MULTIPLIER,
    PRE_TP_ENABLED,
    PRE_TP_FEE_FLOOR_PCT,
    INVALIDATION_MODE_DEFAULT,
    INVALIDATION_TRAILING_MFE_R_DEFAULT,
    INVALIDATION_TRAILING_RETRACE_PCT_DEFAULT,
    PRE_TP_FEE_PCT_ROUND_TRIP,
    PRE_TP_GRAB_FRACTION,
    PRE_TP_LEVERAGE,
    PRE_TP_MAX_AGE_SEC,
    PRE_TP_MIN_AGE_SEC,
    PRE_TP_REGIME_ALLOWLIST,
    PRE_TP_SETUP_BLACKLIST,
    PRE_TP_THRESHOLD_PCT,
    TRAILING_ATR_MULTIPLIER,
)
from src.channels.base import Signal, TrailingStopState
from src.dca import check_dca_entry, recalculate_after_dca
from src import user_settings as _user_settings
from src.historical_data import HistoricalDataStore
from src.indicators import atr as _compute_atr
from src.indicators import ema as _compute_ema
from src.indicators import momentum as _compute_momentum
from src.performance_metrics import calculate_trade_pnl_pct, classify_trade_outcome
from src.smc import Direction
from src.stat_filter import SignalOutcome
from src.utils import fmt_price, fmt_ts, get_logger, utcnow

log = get_logger("trade_monitor")

# Minimum absolute PnL (%) before SL/TP evaluation is allowed.
# Prevents false stops from stale prices or floating-point noise.
_ZERO_PNL_THRESHOLD_PCT = 0.01
_STOP_OUTCOME_MESSAGES = {
    "SL_HIT": "🔴 SL HIT",
    "BREAKEVEN_EXIT": "⚪ BREAKEVEN EXIT",
    "PROFIT_LOCKED": "🟢 PROFIT LOCKED",
    "EXPIRED": "⏰ EXPIRED",
}
# Seconds of grace after a DCA entry before invalidation checks are allowed.
# Gives the averaged position time to develop without being killed prematurely.
_DCA_GRACE_SECONDS = 600

# Retry cooldown for paper-mode open attempts that were gate-rejected
# (qty_zero / notional_floor / risk-gate concurrent-cap).  Without
# this, the 5s monitor tick re-attempts a rejected open every cycle
# until the signal goes terminal — gate-rejection chatter that gives
# the broker no useful information.  60s lets transient rejections
# (equity recovering, concurrent slot freed) resolve at the rate
# they realistically can, without storming the gate chain on every
# tick.  Env-overridable per B8.
_ORDER_RETRY_COOLDOWN_SEC: float = float(
    os.getenv("ORDER_RETRY_COOLDOWN_SEC", "60")
)

# OWNER_BRIEF B17 / §3.2a — per-user invalidation aggressiveness modes.
# Engine-side TradeMonitor uses ``INVALIDATION_MODE_DEFAULT`` from config
# (default ``standard``); per-user app-side execution reads
# ``user_invalidation_settings.mode`` directly when Phase 4 lands.
_VALID_INVALIDATION_MODES: frozenset = frozenset({"loose", "standard", "tight"})


def _compute_trailing_stop(
    signal: Signal,
    current_price: float,
    current_atr: float,
    trailing_state: TrailingStopState,
    atr_percentile: float = 50.0,
) -> float:
    """Compute the new trailing stop level based on current stage and ATR.

    Parameters
    ----------
    signal:
        Active signal with direction, entry, current stop_loss.
    current_price:
        Latest market price.
    current_atr:
        ATR computed from the most recent candles (updated each lifecycle poll).
    trailing_state:
        Mutable state tracking the trailing stop stage.
    atr_percentile:
        Rolling ATR percentile 0–100 (from RegimeContext).

    Returns
    -------
    float
        New stop-loss level. Will only ratchet tighter (never widen) for the
        direction of the trade.
    """
    # Update the trailing state with current ATR
    trailing_state.current_atr = current_atr

    # ATR-percentile adjustment: wider buffer in high-vol, tighter in low-vol
    if atr_percentile >= 80:
        vol_adj = 1.3
    elif atr_percentile <= 20:
        vol_adj = 0.7
    else:
        vol_adj = 1.0

    trail_dist = trailing_state.trail_distance * vol_adj

    if signal.direction == Direction.LONG:
        candidate_sl = current_price - trail_dist
        # Never move SL backwards (lower) for a long trade
        new_sl = max(signal.stop_loss, candidate_sl)
    else:
        candidate_sl = current_price + trail_dist
        # Never move SL backwards (higher) for a short trade
        new_sl = min(signal.stop_loss, candidate_sl)

    return round(new_sl, 8)


def _update_trailing_stage(
    signal: Signal,
    current_price: float,
    trailing_state: TrailingStopState,
) -> None:
    """Check if TP levels have been hit and advance trailing stage.

    Mutates both signal and trailing_state in place.
    """
    if trailing_state.stage >= 2:
        return  # Already at final stage

    if trailing_state.stage == 0:
        # Check for TP1 hit
        if signal.direction == Direction.LONG and current_price >= signal.tp1:
            trailing_state.stage = 1
            trailing_state.breakeven_set = True
            signal.trailing_stage = 1
            signal.partial_close_pct = 0.4
            signal.best_tp_hit = max(signal.best_tp_hit, 1)
            signal.execution_note += " | TP1 hit → 40% closed, SL→breakeven"
            # Move SL to breakeven (entry price)
            signal.stop_loss = signal.entry
        elif signal.direction == Direction.SHORT and current_price <= signal.tp1:
            trailing_state.stage = 1
            trailing_state.breakeven_set = True
            signal.trailing_stage = 1
            signal.partial_close_pct = 0.4
            signal.best_tp_hit = max(signal.best_tp_hit, 1)
            signal.execution_note += " | TP1 hit → 40% closed, SL→breakeven"
            signal.stop_loss = signal.entry

    if trailing_state.stage == 1:
        # Check for TP2 hit
        if signal.direction == Direction.LONG and current_price >= signal.tp2:
            trailing_state.stage = 2
            trailing_state.tight_trail_active = True
            signal.trailing_stage = 2
            signal.partial_close_pct = 0.7  # Cumulative: 40% at TP1 + 30% at TP2
            signal.best_tp_hit = max(signal.best_tp_hit, 2)
            signal.execution_note += " | TP2 hit → 70% closed, tight 0.5×ATR trail"
        elif signal.direction == Direction.SHORT and current_price <= signal.tp2:
            trailing_state.stage = 2
            trailing_state.tight_trail_active = True
            signal.trailing_stage = 2
            signal.partial_close_pct = 0.7
            signal.best_tp_hit = max(signal.best_tp_hit, 2)
            signal.execution_note += " | TP2 hit → 70% closed, tight 0.5×ATR trail"


def _escape_md(text: str) -> str:
    """Escape Telegram MarkdownV1 special characters in dynamic text fields."""
    for ch in ("\\", "*", "_", "`", "["):
        text = text.replace(ch, f"\\{ch}")
    return text


# Terminal lifecycle states — once a signal hits one of these, ``_evaluate_signal``
# must NOT re-fire the close event.  Owner reported (2026-05-08) duplicate
# Telegram messages for the same signal lifecycle event (e.g. INVALIDATED
# ZECUSDT posted twice at the same timestamp; same FLOCKUSDT SL HIT posted
# 6 minutes apart).  Root cause: an asyncio race in ``_check_all`` /
# ``asyncio.gather`` could re-evaluate the same Signal object twice in the
# same poll cycle (e.g. via duplicate ``_active_signals`` keys after a
# disk-restore edge case from PR #337), and there was no defensive
# top-of-function check to short-circuit re-evaluation of an already-closed
# signal.
#
# TP1_HIT and TP2_HIT are NOT in this set — those signals stay active for
# higher-TP progression.  Only states that mean "fully closed, lifecycle
# complete" go here.
_TERMINAL_STATUSES: frozenset = frozenset({
    "SL_HIT",
    "BREAKEVEN_EXIT",
    "PROFIT_LOCKED",
    "INVALIDATED",
    "EXPIRED",
    "CANCELLED",
    "FULL_TP_HIT",
    "TP3_HIT",
    "CLOSED",
})

# Counter-trend-by-design setups exempted from the EMA9/EMA21 crossover
# invalidation rule.  Per CLAUDE.md HTF-policy doctrine, LSR and FAR fade an
# existing move by design — they are dispatched with EMAs intentionally
# misaligned to the signal direction.  The crossover check at ``_check_invalidation``
# only inspects the CURRENT alignment (``ema9 < ema21`` for LONG), not whether
# alignment changed since dispatch, so it fires on the very condition the setup
# was born under.  Audit data (truth report 2026-05-09) shows LSR with 1
# PROTECTIVE / 2 PREMATURE / 2 NEUTRAL kills — the rule is net-hurting on this
# path.  The pre-existing ``_counter_trend`` regime-based exemption only fires
# when the creation regime is the OPPOSING trend; an LSR LONG fired in
# TRENDING_UP regime (LSR fading the up-move's exhaustion) is not regime-counter
# but IS thesis-counter, and was incorrectly killed.
_EMA_CROSSOVER_EXEMPT_SETUPS: frozenset = frozenset({
    "LIQUIDITY_SWEEP_REVERSAL",
    "FAILED_AUCTION_RECLAIM",
})


def _resolved_regime_allowlist() -> frozenset:
    """Pre-TP regime allowlist with the user-settings override applied.

    Centralised so tests can monkeypatch a single function instead of
    threading the indirection through the call site.  Returns the
    user-set value when present, else falls back to the config default.
    """
    return _user_settings.pretp_regime_allowlist()


class TradeMonitor:
    """Watches active signals and emits updates."""

    def __init__(
        self,
        data_store: HistoricalDataStore,
        send_telegram: Callable[[str, str], Coroutine],
        get_active_signals: Callable[[], Dict[str, Signal]],
        remove_signal: Callable[[str], None],
        update_signal: Callable[[str], None],
        performance_tracker: Optional[Any] = None,
        circuit_breaker: Optional[Any] = None,
        regime_detector: Optional[Any] = None,
        indicators_fn: Optional[Callable] = None,
        order_manager: Optional[Any] = None,
        stat_filter: Optional[Any] = None,
    ) -> None:
        self._store = data_store
        self._send = send_telegram
        self._get_signals = get_active_signals
        self._remove = remove_signal
        self._update = update_signal
        self._performance_tracker = performance_tracker
        self._circuit_breaker = circuit_breaker
        self._regime_detector = regime_detector
        self._indicators_fn = indicators_fn
        # Optional OrderManager for direct exchange execution (V3 groundwork).
        # When provided and auto-execution is enabled, confirmed signals are
        # forwarded to the exchange instead of (or alongside) Telegram.
        self._order_manager = order_manager
        # Track signal IDs for which an order has already been placed
        # SUCCESSFULLY so we don't double-fire across consecutive poll
        # cycles.  Previously this also accumulated gate-rejected
        # signals (qty_zero, notional_floor, risk-gate concurrent-cap)
        # because ``add()`` ran unconditionally after ``execute_signal``
        # — those signals never retried even when the rejection cause
        # could have cleared (equity recovered, position slot freed).
        # 2026-05-18 fix: only mark as placed on a non-None order_id.
        self._order_placed_ids: set = set()
        # Last open-attempt timestamp per signal_id.  Used as a retry
        # cooldown so a rejected signal doesn't get re-attempted every
        # 5s monitor tick (which would spam the broker with no-op gate
        # rejections).  Cleared in ``_record_outcome`` alongside
        # ``_order_placed_ids``.
        self._last_open_attempt_at: Dict[str, Any] = {}
        self._running = False
        # Optional callback invoked with the symbol whenever a stop-loss is hit.
        # Set after construction (e.g. to scanner.set_symbol_sl_cooldown).
        self.on_sl_callback: Optional[Any] = None
        # Optional callback invoked with (symbol, channel, direction) on invalidation.
        # Set after construction (e.g. to scanner.set_invalidation_cooldown).
        self.on_invalidation_callback: Optional[Any] = None
        # Optional callback invoked with (symbol, channel, direction, setup_class,
        # hold_duration_seconds) when a stop-loss is hit.  Used to set thesis-based
        # cooldowns in the scanner.
        self.on_thesis_sl_callback: Optional[Any] = None
        # Optional callback invoked with (signal, tp_level, tp_pnl_pct) when TP2+ is hit.
        # Used to post highlights to the free channel.
        self.on_highlight_callback: Optional[Any] = None
        # Optional callback invoked with (signal, outcome_label) for every final
        # lifecycle resolution (SL/TP/expired). Used for path-level observability.
        self.on_lifecycle_outcome_callback: Optional[Any] = None
        # Optional AI Trade Observer — captures full trade lifecycle data.
        # Set after construction (e.g. in main.py after router.observer is wired).
        self.observer: Optional[Any] = None
        # Optional StatisticalFilter — records resolved signal outcomes so the
        # rolling win-rate store can adapt confidence gating over time.
        self._stat_filter = stat_filter
        # Optional content engine context provider — when set, signal-closed posts
        # are generated by content_engine and sent to the active channel.
        # Set after construction (e.g. in main.py: monitor.engine_context_fn = ...).
        self.engine_context_fn: Optional[Any] = None

    def _record_outcome(self, sig: Signal, hit_tp: int, hit_sl: bool, expired: bool = False) -> None:
        """Notify performance tracker and circuit breaker of a completed signal.

        Called only on final outcomes (semantic stop/TP completion). Intermediate hits
        (TP1/TP2) and configuration-error cancellations are intentionally
        excluded because the signal is still active or was never a real trade.

        Parameters
        ----------
        sig:
            The completed :class:`src.channels.base.Signal`.
        hit_tp:
            Which TP was hit (0 if SL was hit, 3 if TP3 was hit).
        hit_sl:
            ``True`` when the stop-loss was triggered.
        """
        # Actual PnL = the real exit price PnL (used for circuit breaker)
        actual_pnl = sig.pnl_pct

        # Signal quality PnL = best TP PnL if a TP was previously reached and is
        # better than the final outcome; otherwise same as actual PnL
        signal_quality_pnl = actual_pnl
        signal_quality_hit_tp = hit_tp
        if sig.best_tp_hit > 0 and sig.best_tp_hit > hit_tp:
            signal_quality_pnl = sig.best_tp_pnl_pct
            signal_quality_hit_tp = sig.best_tp_hit

        terminal_ts = utcnow()
        if hit_sl and sig.first_sl_touch_timestamp is None:
            sig.first_sl_touch_timestamp = terminal_ts
        if hit_tp > 0 and sig.first_tp_touch_timestamp is None:
            sig.first_tp_touch_timestamp = terminal_ts
        sig.terminal_outcome_timestamp = terminal_ts

        create_ts = sig.timestamp if sig.timestamp is not None else None
        dispatch_ts_epoch = None
        if sig.dispatch_timestamp is not None:
            dispatch_ts_epoch = sig.dispatch_timestamp.timestamp()
        elif sig.posted_at is not None:
            dispatch_ts_epoch = float(sig.posted_at)

        create_ts_epoch = create_ts.timestamp() if create_ts is not None else None
        first_sl_ts_epoch = (
            sig.first_sl_touch_timestamp.timestamp()
            if sig.first_sl_touch_timestamp is not None
            else None
        )
        first_tp_ts_epoch = (
            sig.first_tp_touch_timestamp.timestamp()
            if sig.first_tp_touch_timestamp is not None
            else None
        )
        terminal_ts_epoch = terminal_ts.timestamp()
        breach_candidates = [ts for ts in (first_sl_ts_epoch, first_tp_ts_epoch) if ts is not None]
        first_breach_ts_epoch = min(breach_candidates) if breach_candidates else None

        def _duration(start_ts: Optional[float], end_ts: Optional[float]) -> Optional[float]:
            if start_ts is None or end_ts is None:
                return None
            return max(end_ts - start_ts, 0.0)

        hold_duration_sec = _duration(create_ts_epoch, terminal_ts_epoch) or 0.0
        # Honour explicit terminal-state classification when the trade-monitor
        # has already stamped one on ``sig.status`` (e.g. the invalidation /
        # expiry close paths set ``sig.status = "INVALIDATED"`` /
        # ``"EXPIRED"`` before calling here).  ``classify_trade_outcome`` is
        # derived from (hit_tp, hit_sl, expired) and will mis-label
        # invalidations as ``"CLOSED"`` because it has no signal that the
        # close was thesis-driven, not stop-driven.  Perf-tracker records
        # have been stamping these wrongly ever since the invalidation gate
        # shipped — see #304's backfill reconciliation for the historical
        # cleanup; this prevents future records from accumulating the same
        # bug.
        sig_status = (getattr(sig, "status", "") or "").upper()
        if sig_status in {"INVALIDATED", "EXPIRED"}:
            outcome_label = sig_status
        else:
            outcome_label = classify_trade_outcome(
                pnl_pct=actual_pnl,
                hit_tp=hit_tp,
                hit_sl=hit_sl,
                expired=expired,  # BUG FIX
            )
        if self.on_lifecycle_outcome_callback is not None:
            try:
                self.on_lifecycle_outcome_callback(sig, outcome_label)
            except Exception as exc:
                log.debug("on_lifecycle_outcome_callback failed (non-critical): {}", exc)
        if self._performance_tracker is not None:
            self._performance_tracker.record_outcome(
                signal_id=sig.signal_id,
                channel=sig.channel,
                symbol=sig.symbol,
                direction=sig.direction.value,
                entry=sig.entry,
                hit_tp=hit_tp,
                hit_sl=hit_sl,
                pnl_pct=actual_pnl,
                outcome_label=outcome_label,
                confidence=sig.confidence,
                pre_ai_confidence=sig.pre_ai_confidence,
                post_ai_confidence=sig.post_ai_confidence,
                setup_class=sig.setup_class,
                market_phase=sig.market_phase,
                quality_tier=sig.quality_tier,
                spread_pct=sig.spread_pct,
                volume_24h_usd=sig.volume_24h_usd,
                hold_duration_sec=hold_duration_sec,
                create_timestamp=create_ts_epoch,
                dispatch_timestamp=dispatch_ts_epoch,
                first_sl_touch_timestamp=first_sl_ts_epoch,
                first_tp_touch_timestamp=first_tp_ts_epoch,
                first_breach_timestamp=first_breach_ts_epoch,
                terminal_outcome_timestamp=terminal_ts_epoch,
                create_to_dispatch_sec=_duration(create_ts_epoch, dispatch_ts_epoch),
                dispatch_to_first_adverse_sec=_duration(dispatch_ts_epoch, first_sl_ts_epoch),
                dispatch_to_first_favorable_sec=_duration(dispatch_ts_epoch, first_tp_ts_epoch),
                create_to_first_breach_sec=_duration(create_ts_epoch, first_breach_ts_epoch),
                create_to_terminal_sec=_duration(create_ts_epoch, terminal_ts_epoch),
                first_breach_to_terminal_sec=_duration(first_breach_ts_epoch, terminal_ts_epoch),
                max_favorable_excursion_pct=sig.max_favorable_excursion_pct,
                max_adverse_excursion_pct=sig.max_adverse_excursion_pct,
                stop_loss=float(sig.stop_loss),
                signal_quality_pnl_pct=signal_quality_pnl,
                signal_quality_hit_tp=signal_quality_hit_tp,
            )
        # Circuit breaker ALWAYS uses actual PnL (real exit price)
        if self._circuit_breaker is not None:
            self._circuit_breaker.record_outcome(
                signal_id=sig.signal_id,
                hit_sl=hit_sl,
                pnl_pct=actual_pnl,
                symbol=sig.symbol,
            )
        if hit_sl:
            # Notify the scanner to apply a short per-symbol cooldown so no other
            # channel fires on the same symbol immediately after a stop-loss.
            if self.on_sl_callback is not None:
                self.on_sl_callback(sig.symbol)
            # Notify the scanner about the thesis that failed so it can apply a
            # longer thesis-based cooldown to prevent repeat entries.
            if self.on_thesis_sl_callback is not None:
                self.on_thesis_sl_callback(
                    sig.symbol,
                    sig.channel,
                    sig.direction.value,
                    sig.setup_class or "",
                    hold_duration_sec,
                )
        # Release order-placement tracking for this closed signal so that the
        # set does not grow without bound across many completed signals.
        self._order_placed_ids.discard(sig.signal_id)
        # Same cleanup for the retry-cooldown map (PR B, 2026-05-18) so it
        # doesn't grow without bound as signals complete.
        self._last_open_attempt_at.pop(sig.signal_id, None)

        # Notify the AI Trade Observer with exit analysis (fail-open)
        if self.observer is not None:
            try:
                self.observer.capture_exit_analysis(sig, outcome_label, actual_pnl)
            except Exception as exc:
                log.debug("TradeObserver.capture_exit_analysis failed (non-critical): {}", exc)

        # Statistical filter outcome recording — updates rolling win-rate store
        # so the filter can penalise or suppress future signals from poor
        # (channel, pair, regime) combinations.
        if self._stat_filter is not None:
            try:
                won = signal_quality_hit_tp >= 1
                _sf_outcome = SignalOutcome(
                    signal_id=sig.signal_id,
                    channel=sig.channel,
                    pair=sig.symbol,
                    regime=getattr(sig, "entry_regime", "") or "",
                    setup_class=sig.setup_class or "",
                    won=won,
                    pnl_pct=signal_quality_pnl,
                )
                self._stat_filter.record(_sf_outcome)
            except Exception as exc:
                log.debug("stat_filter.record failed (non-critical): {}", exc)

    @staticmethod
    def _set_realized_pnl(sig: Signal, exit_price: float) -> None:
        """Freeze final trade PnL at the executed exit level.

        When pre-TP fired and a broker partial actually executed (PR #411 /
        OWNER_BRIEF §3.2a doctrine), the signal's terminal ``pnl_pct`` is
        the size-weighted blend of:

          * ``partial_close_pct`` of the position at ``pre_tp_pct`` (the
            raw % move at which pre-TP fired and the partial was filled)
          * ``(1 - partial_close_pct)`` of the position at the final
            exit-vs-entry % (the residual that rode under BE-stop)

        Pre-PR #411 the pnl_pct was residual-only — a BE-stop exit reported
        0.00% regardless of how much was banked at the partial.  The
        Signals tab on Lumin showed BREAKEVEN_EXIT +0.00% on signals that
        actually netted +0.15% for the subscriber, and the classifier
        (``performance_metrics.classify_trade_outcome``) then mis-labelled
        them BREAKEVEN_EXIT instead of PROFIT_LOCKED.  This honest weighted
        computation fixes both layers: pnl_pct reports the user's actual
        realised return, and the classifier naturally re-labels signals
        to PROFIT_LOCKED because pnl_pct is now > 0.01.

        Backward-compat: signals without a partial fill
        (``partial_close_pct == 0`` OR ``pre_tp_pct == 0``) compute exactly
        as before — entry → exit_price only — so SL_HIT / EXPIRED / TP1+
        paths and pre-PR #411 signals are unchanged.
        """
        sig.current_price = exit_price
        residual_pnl = calculate_trade_pnl_pct(
            entry_price=sig.entry,
            exit_price=exit_price,
            direction=sig.direction.value,
        )
        partial_pct = float(getattr(sig, "partial_close_pct", 0.0) or 0.0)
        pre_tp_pct = float(getattr(sig, "pre_tp_pct", 0.0) or 0.0)
        if partial_pct > 0 and pre_tp_pct > 0:
            # Cap the partial fraction at 1.0 defensively (TP1/TP2 partials
            # can compound partial_close_pct beyond grab_fraction via the
            # 0.4 / 0.7 stages — when that happens, pre-TP no longer owns
            # the whole closed slice, so we cap the blend at 1.0 to avoid
            # > 100% allocation).
            partial_pct = min(partial_pct, 1.0)
            residual_fraction = 1.0 - partial_pct
            sig.pnl_pct = (
                partial_pct * pre_tp_pct + residual_fraction * residual_pnl
            )
        else:
            sig.pnl_pct = residual_pnl

    @staticmethod
    def _apply_final_outcome(sig: Signal, hit_tp: int, hit_sl: bool) -> str:
        """Apply the semantic final outcome label to the signal and return it."""
        outcome_label = classify_trade_outcome(
            pnl_pct=sig.pnl_pct,
            hit_tp=hit_tp,
            hit_sl=hit_sl,
        )
        sig.status = outcome_label
        return outcome_label

    async def start(self) -> None:
        self._running = True
        log.info("Trade monitor started")
        while self._running:
            try:
                await self._check_all()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.error("Monitor error: %s", exc)
            await asyncio.sleep(MONITOR_POLL_INTERVAL)

    async def stop(self) -> None:
        self._running = False
        log.info("Trade monitor stopped")

    async def _check_all(self) -> None:
        signals = self._get_signals()

        async def _process_signal(sig: Signal) -> None:
            price = self._latest_price(sig.symbol)
            if price is None:
                # Fallback: the mark-price feed covers every Binance USDT-M
                # futures symbol via !markPrice@arr@1s — including symbols that
                # fell out of the scan universe after dispatch (surge-promoted
                # or Tier-3 pairs that aren't continuously re-scanned).  Without
                # this, a signal on a stale symbol gets `price = None` on every
                # 5s tick and returns early here forever — SL never fires, PnL
                # grinds without bound.  BEATUSDT SHORT at -6.52% while SL was
                # blown through is the canonical example.
                try:
                    from src.execution import mark_price_feed as _mpf
                    _feed = _mpf.get_instance()
                    if _feed is not None:
                        price = _feed.get_price(sig.symbol)
                except Exception:
                    pass
            if price is None:
                return
            sig.current_price = price
            # Auto-execution: attempt to place an order the first time we see
            # this signal (status == "ACTIVE" and no order has been placed yet).
            # The OrderManager is a no-op when auto-execution is disabled.
            #
            # 2026-05-18 fix: previously ``_order_placed_ids.add()`` ran
            # unconditionally after ``execute_signal`` returned, so a
            # gate-rejected open (qty_zero / notional_floor / risk-gate
            # concurrent-cap → execute_signal returns None) was marked
            # as "placed" and never retried.  Owner-visible symptom:
            # ACTIVE signals sitting on the Signals tab with no
            # corresponding paper position, ever.  Now we mark as
            # placed only on a non-None order_id, and add a per-signal
            # cooldown so failed retries don't hammer the broker on
            # every 5s monitor tick.
            if (
                self._order_manager is not None
                and self._order_manager.is_enabled
                and sig.status == "ACTIVE"
                and sig.signal_id not in self._order_placed_ids
            ):
                _last = self._last_open_attempt_at.get(sig.signal_id)
                _now = utcnow()
                _should_retry = (
                    _last is None
                    or (_now - _last).total_seconds() >= _ORDER_RETRY_COOLDOWN_SEC
                )
                if _should_retry:
                    self._last_open_attempt_at[sig.signal_id] = _now
                    try:
                        order_id = await self._order_manager.execute_signal(sig)
                        if order_id:
                            self._order_placed_ids.add(sig.signal_id)
                            log.info(
                                "Auto-execution order placed for {} {}: order_id={}",
                                sig.symbol,
                                sig.channel,
                                order_id,
                            )
                    except Exception as exc:
                        log.warning(
                            "Auto-execution failed for {} {}: {}",
                            sig.symbol,
                            sig.channel,
                            exc,
                        )
            # Per-user tight-mode early kill (F4): run BEFORE engine-wide
            # evaluation so tight-mode users get ATR-trailing closure even
            # when INVALIDATION_MODE_DEFAULT is "standard".  Loose-mode
            # users are excluded from the engine invalidation close inside
            # _broker_close_full; nothing to do for them here.
            await self._check_per_user_invalidation(sig)
            await self._evaluate_signal(sig)

        await asyncio.gather(*[_process_signal(sig) for sig in signals.values()])

    def _latest_price(self, symbol: str) -> Optional[float]:
        """Return last 1m candle close — used for PnL and general price display."""
        candles = self._store.get_candles(symbol, "1m")
        if candles and len(candles.get("close", [])) > 0:
            return float(candles["close"][-1])
        ticks = self._store.ticks.get(symbol)
        if ticks:
            tick_price = ticks[-1].get("price")
            if tick_price is not None:
                return float(tick_price)
        return None

    def _candle_extremes(self, symbol: str) -> tuple:
        """Return (high, low) of last 1m candle.

        Used for SL/TP evaluation:
        - LONG  SL: low  <= SL  (wick hit stop → stop order filled on Binance)
        - SHORT SL: high >= SL  (wick hit stop → stop order filled)
        - LONG  TP: high >= TP  (wick or close reached TP → limit fill)
        - SHORT TP: low  <= TP

        Using 1m candle high/low instead of single ticks eliminates ultra-thin
        single-order spikes (1-2 contracts) that move last trade price
        but do not represent real sustained price discovery.
        """
        candles = self._store.get_candles(symbol, "1m")
        if candles and len(candles.get("high", [])) > 0 and len(candles.get("low", [])) > 0:
            return float(candles["high"][-1]), float(candles["low"][-1])
        # Fallback: treat close as both high and low
        close = self._latest_price(symbol)
        if close:
            return close, close
        return 0.0, 0.0

    def _check_trailing_invalidation(self, sig: Signal) -> Optional[str]:
        """Return a kill reason when the ATR-trailing invalidation fires.

        OWNER_BRIEF B17 (tight-mode signature, 2026-05-17 doctrine):

        - Arms when MFE >= ``INVALIDATION_TRAILING_MFE_R_DEFAULT`` × SL distance
          (default 0.3R — small enough that the trailing kicks in once the
          signal has proven any meaningful direction, large enough to filter
          noise wicks).
        - Fires when current price has retraced ``INVALIDATION_TRAILING_RETRACE_PCT_DEFAULT``
          of the MFE peak back toward entry (default 0.50 = 50%).

        Pre-2026-05-17 the engine had no equivalent — MFE-positive signals
        could slide all the way to full SL after peaking.  The audit on 654
        closed signals found 22 INVALIDATED entries with MFE >= 0.5R that
        proceeded to retrace and (in many cases) hit SL.  This kill closes
        the residual before that happens.

        Pure function on signal state — independent of regime / EMA /
        momentum gates above.  Returns ``None`` when not armed or not
        retraced enough; returns a structured reason string otherwise.
        """
        is_long = sig.direction == Direction.LONG
        entry = float(getattr(sig, "entry", 0.0) or 0.0)
        sl_px = float(getattr(sig, "stop_loss", 0.0) or 0.0)
        mfe_pct = float(getattr(sig, "max_favorable_excursion_pct", 0.0) or 0.0)
        if entry <= 0 or sl_px <= 0 or mfe_pct <= 0:
            return None

        # SL distance as a percentage of entry (so MFE_R can be computed in
        # the same pct units without re-deriving prices).  Guard against
        # an inverted SL (BE-stop after pre-TP can land at exactly entry,
        # which yields zero SL distance — no trailing in that case).
        sl_dist_pct = abs(entry - sl_px) / entry * 100.0
        if sl_dist_pct <= 0:
            return None

        mfe_r = mfe_pct / sl_dist_pct
        if mfe_r < INVALIDATION_TRAILING_MFE_R_DEFAULT:
            return None  # Not armed yet — MFE hasn't reached the trigger band

        # Current excursion in the favourable direction (negative if reversed
        # past entry).  Compute in pct space so the comparison with mfe_pct
        # is unit-consistent.
        if is_long:
            current_excursion_pct = (sig.current_price - entry) / entry * 100.0
        else:
            current_excursion_pct = (entry - sig.current_price) / entry * 100.0

        # Retracement as a fraction of the MFE peak.  A reversal past entry
        # (current_excursion_pct < 0) yields retrace > 1.0 — captured by the
        # >= threshold check the same way; SL itself would also fire in
        # that band, but the trailing kill exits first to lock the residual.
        retrace_fraction = (mfe_pct - current_excursion_pct) / mfe_pct
        if retrace_fraction < INVALIDATION_TRAILING_RETRACE_PCT_DEFAULT:
            return None  # Still close enough to peak; not retraced enough

        return (
            f"trailing invalidation (MFE peak +{mfe_pct:.2f}%, current "
            f"+{current_excursion_pct:.2f}%, retraced {retrace_fraction*100:.0f}% "
            f"of peak at MFE_R={mfe_r:.2f}) – capital preserved"
        )

    def _check_invalidation(
        self, sig: Signal, *, mode_override: Optional[str] = None
    ) -> Optional[str]:
        """Return an invalidation reason string if the signal's thesis is no longer valid.

        Mode-gated per OWNER_BRIEF B17 / §3.2a (capital preservation doctrine):

        * ``loose``    — only hard structural break (skip momentum / EMA /
                         regime checks).  For users who want signals to
                         develop fully before any non-SL exit fires.
        * ``standard`` — engine baseline.  Regime-flip, EMA crossover, and
                         momentum-loss checks all active, plus MFE
                         protection on pre-TP'd signals (default).
        * ``tight``    — standard + ATR-trailing kill at MFE >=
                         ``INVALIDATION_TRAILING_MFE_R_DEFAULT`` (default
                         0.3R).  Closes at ``trailing_retrace_pct``
                         retracement of the MFE peak.  Capital-preservation
                         mode that prevents MFE-positive signals from
                         sliding all the way to full SL.

        ``mode_override``: when provided, uses this mode instead of
        ``INVALIDATION_MODE_DEFAULT``.  Used by the per-user tight/loose
        enforcement path so each user's stored ``invalidation_mode`` is
        applied rather than the engine-wide default.

        Returns ``None`` if the signal is still valid.
        """
        is_long = sig.direction == Direction.LONG

        # Metadata used by every check below.
        _setup_class = getattr(sig, "setup_class", "") or ""
        _setup_key = f"{sig.channel}::{_setup_class}"
        min_age = INVALIDATION_MIN_AGE_SECONDS.get(
            _setup_key, INVALIDATION_MIN_AGE_SECONDS.get(sig.channel, 120)
        )
        age_secs = (utcnow() - sig.timestamp).total_seconds()

        # DCA grace period — give the averaged position time to develop before
        # allowing invalidation to close it prematurely.
        if sig.entry_2_filled and sig.dca_timestamp is not None:
            dca_age = (utcnow() - sig.dca_timestamp).total_seconds()
            if dca_age < _DCA_GRACE_SECONDS:
                return None

        _raw_mode = (mode_override or INVALIDATION_MODE_DEFAULT or "standard").strip().lower()
        mode = _raw_mode if _raw_mode in _VALID_INVALIDATION_MODES else "standard"

        # MFE protection (OWNER_BRIEF §3.2a, 2026-05-17) — applies to standard
        # and tight modes.  Skip ALL kill checks below when the signal has
        # already proved its direction via pre-TP (so SL is at BE on the
        # residual) AND current price is still on the favourable side of entry.
        # Doctrine: once pre-TP fires and the residual has BE-stop, the
        # downside is structurally capped at fees.  Killing the residual on
        # a momentum dip / EMA wobble during normal post-pre-TP consolidation
        # destroys the optionality on TP1+.  The 2026-05-17 audit found
        # 22 PREMATURE kills (~9% of INV cohort) where MFE was ≥ 0.5R at
        # kill time — most of those would have been protected by this rule.
        if mode != "loose" and getattr(sig, "pre_tp_hit", False):
            _entry_px = sig.entry if sig.entry > 0 else sig.current_price
            if _entry_px > 0:
                still_in_profit = (
                    (is_long and sig.current_price >= _entry_px)
                    or (not is_long and sig.current_price <= _entry_px)
                )
                if still_in_profit:
                    return None

        # Loose mode short-circuits here — only the SL itself + max-hold guard
        # (handled outside this function) can close the signal.  No regime,
        # EMA, or momentum kill.
        if mode == "loose":
            return None

        # ---- EARLY PRICE-BASED GATES (before main patience gate) ----
        # Profit-protection and adverse excursion only need current price —
        # no candle indicators required.  They run HERE, before the main
        # patience gate, so that fast-moving losing signals (SR_FLIP hitting
        # SL in < 4 min, LSR in < 5 min) are caught even while the regime /
        # EMA / momentum checks are still in their patience window.
        _entry_px = sig.entry if sig.entry > 0 else sig.current_price
        _sl_px = getattr(sig, "stop_loss", 0.0) or 0.0
        _sl_dist = abs(_entry_px - _sl_px) if (_sl_px > 0 and _entry_px > 0) else 0.0

        # Profit-protection (early gate): already > 0.5×SL_dist in profit.
        # A dip from this depth is consolidation noise, not thesis failure.
        # This gate sits BEFORE the patience window so tight-mode trailing
        # (which runs after the patience gate) is not blocked here — signals
        # in shallow profit (0–0.5×SL_dist) still flow to the trailing check.
        if _sl_dist > 0 and sig.current_price > 0:
            _favorable = (sig.current_price - _entry_px) if is_long else (_entry_px - sig.current_price)
            if _favorable > _sl_dist * 0.5:
                sig.momentum_invalidation_count = 0
                return None

        # Early adverse excursion — fires at a per-setup min-age that is
        # shorter than the main patience gate (90s SR_FLIP / 120s LSR vs
        # 240s / 300s respectively).  When price is already past the adverse
        # fraction and we are NOT in positive territory, the signal thesis
        # is structurally broken — exit unconditionally (no momentum rescue).
        _adv_exc_early_age = INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_BY_SETUP.get(
            _setup_key, INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC
        )
        if (
            _sl_dist > 0
            and sig.current_price > 0
            and sig.status not in ("TP1_HIT", "TP2_HIT")
            and not getattr(sig, "pretp_fired", False)
            and age_secs >= _adv_exc_early_age
        ):
            _adv_exc_fraction = INVALIDATION_ADVERSE_EXCURSION_FRACTION_BY_SETUP.get(
                _setup_key, INVALIDATION_ADVERSE_EXCURSION_FRACTION
            )
            _adverse = (_entry_px - sig.current_price) if is_long else (sig.current_price - _entry_px)
            if _adverse >= _sl_dist * _adv_exc_fraction:
                _adv_pct = (_adverse / _entry_px) * 100.0 if _entry_px > 0 else 0.0
                _adv_frac = _adverse / _sl_dist
                return (
                    f"adverse excursion ({_adv_pct:+.2f}% against, "
                    f"{_adv_frac:.2f}×SL_dist) – early invalidation"
                )

        # ---- MAIN PATIENCE GATE (regime / EMA / momentum checks) ----
        # Reversal and flip-structure setups (SR_FLIP=240s, LSR=300s) need
        # the post-entry reversal to establish before pattern-reading checks
        # are allowed to fire.  Price-based gates already ran above.
        if age_secs < min_age:
            return None

        # Build an indicators dict for regime detection and EMA/momentum checks.
        # Priority: caller-supplied indicators_fn → data-store fallback.
        indicators: Optional[dict] = None
        if self._indicators_fn is not None:
            try:
                indicators = self._indicators_fn(sig.symbol)
            except Exception as exc:
                log.debug("indicators_fn failed for %s: %s", sig.symbol, exc)

        # Fallback: derive EMA9/EMA21 and momentum from candles in data store.
        if indicators is None and self._store is not None:
            candles = self._store.get_candles(sig.symbol, "5m")
            if not (candles and len(candles.get("close", [])) >= 21):
                candles = self._store.get_candles(sig.symbol, "1m")
            if candles and len(candles.get("close", [])) >= 21:
                closes = np.asarray(candles["close"], dtype=np.float64)
                ema9_arr = _compute_ema(closes, 9)
                ema21_arr = _compute_ema(closes, 21)
                mom_arr = _compute_momentum(closes, 3) if len(closes) >= 4 else np.array([])
                indicators = {
                    "ema9_last": float(ema9_arr[-1]) if len(ema9_arr) else None,
                    "ema21_last": float(ema21_arr[-1]) if len(ema21_arr) else None,
                    "momentum": float(mom_arr[-1]) if len(mom_arr) and not np.isnan(mom_arr[-1]) else None,
                }

        # Tight-mode ATR-trailing kill (OWNER_BRIEF B17, 2026-05-17) — fires
        # when MFE has reached ``trailing_mfe_r_threshold`` (in multiples of
        # SL distance) AND price has retraced ``trailing_retrace_pct`` of
        # the MFE peak.  Closes the residual position before it slides back
        # to full SL.  Independent of regime / EMA / momentum gates — fires
        # purely off price-action retracement so noise-driven kills can't
        # contaminate it.
        if mode == "tight":
            trailing_kill = self._check_trailing_invalidation(sig)
            if trailing_kill is not None:
                return trailing_kill

        # INV-1 audit fix: extract the regime captured at signal CREATION from
        # `sig.market_phase` (formatted as "REGIME | ATR=... | Vol=...").  The
        # rules below were buggy when applied to counter-trend setups
        # (SR_FLIP_RETEST, FAILED_AUCTION_RECLAIM, LIQUIDATION_REVERSAL,
        # FUNDING_EXTREME_SIGNAL) because those signals are intentionally born
        # with regime opposing direction — the existing checks fired immediately
        # at the channel min-age gate even though nothing had changed.
        # Defensive fallback: when market_phase is missing/N-A, preserve the
        # pre-existing behaviour so older signals in flight don't regress.
        _created_regime = (sig.market_phase or "").split("|")[0].strip().upper()
        _has_creation_regime = _created_regime not in ("", "N/A")
        _counter_trend = (
            _has_creation_regime
            and (
                (is_long and _created_regime == "TRENDING_DOWN")
                or (not is_long and _created_regime == "TRENDING_UP")
            )
        )

        # 1. Market regime flip – use regime_detector.classify() with indicators.
        # INV-1: only invalidate when the regime has CHANGED from the creation
        # regime (a true "flip"), not when the current regime simply matches
        # the killer condition.
        if self._regime_detector is not None and indicators is not None:
            try:
                result = self._regime_detector.classify(indicators)
                regime_label = result.regime.value if result and result.regime else None
                if regime_label is not None:
                    if (
                        is_long
                        and regime_label == "TRENDING_DOWN"
                        and (not _has_creation_regime or _created_regime != "TRENDING_DOWN")
                    ):
                        return f"regime shift to {regime_label} – LONG thesis no longer valid"
                    if (
                        not is_long
                        and regime_label == "TRENDING_UP"
                        and (not _has_creation_regime or _created_regime != "TRENDING_UP")
                    ):
                        return f"regime shift to {regime_label} – SHORT thesis no longer valid"
            except Exception as exc:
                log.debug("Regime detection failed for %s: %s", sig.symbol, exc)

        # Profit-protection gate + adverse-excursion are evaluated here —
        # BEFORE the `indicators is None` early-return — because both only
        # need sig.current_price / sl_price / entry_price, not candle data.
        # The old placement AFTER the early-return meant that when 1m candle
        # data was unavailable for a symbol (store miss, new listing, WS gap),
        # adverse excursion was silently skipped even with price 3–4× past SL.
        _entry_px = sig.entry if sig.entry > 0 else sig.current_price
        _sl_px = getattr(sig, "stop_loss", 0.0) or 0.0
        _sl_dist = abs(_entry_px - _sl_px) if (_sl_px > 0 and _entry_px > 0) else 0.0

        # Profit-protection gate: signal is on the right side of entry → skip
        # regime / EMA / momentum kills.  In positive territory the thesis is
        # proved; only tight-mode trailing (above) and the native SL manage exit.
        if _sl_dist > 0:
            _favorable = (sig.current_price - _entry_px) if is_long else (_entry_px - sig.current_price)
            if _favorable > 0:
                sig.momentum_invalidation_count = 0
                return None

        # Adverse-excursion: price grinding toward SL without completing a
        # structural kill.  Fires unconditionally at the fraction threshold —
        # no momentum rescue.  If price is in negative territory at this depth,
        # the thesis is wrong regardless of a 3-candle momentum blip; waiting
        # for momentum confirmation only delays the inevitable and costs more PnL.
        if (
            _sl_dist > 0
            and sig.current_price > 0
            and sig.status not in ("TP1_HIT", "TP2_HIT")
            and not getattr(sig, "pretp_fired", False)
            and age_secs >= INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC
        ):
            _adverse = (
                (_entry_px - sig.current_price) if is_long
                else (sig.current_price - _entry_px)
            )
            _adv_exc_key = f"{sig.channel}::{_setup_class}"
            _adv_exc_fraction = INVALIDATION_ADVERSE_EXCURSION_FRACTION_BY_SETUP.get(
                _adv_exc_key, INVALIDATION_ADVERSE_EXCURSION_FRACTION
            )
            _adverse_threshold = _sl_dist * _adv_exc_fraction
            if _adverse >= _adverse_threshold:
                _adverse_pct = (_adverse / _entry_px) * 100.0 if _entry_px > 0 else 0.0
                _adverse_frac = _adverse / _sl_dist
                return (
                    f"adverse excursion ({_adverse_pct:+.2f}% against, "
                    f"{_adverse_frac:.2f}×SL_dist) – signal thesis invalidated"
                )

        # No candle data → can't evaluate EMA crossover or momentum-loss.
        # Adverse excursion and profit-protection already ran above.
        if indicators is None:
            return None

        ema9 = indicators.get("ema9_last")
        ema21 = indicators.get("ema21_last")
        momentum = indicators.get("momentum")

        # 2. EMA crossover against signal direction
        # After TP1 has been hit, let trailing stop manage the exit — don't kill
        # a profitable trade just because the 1m EMA crosses (common noise).
        # Age gate for EMA crossover: don't apply until signal is at least 300s old
        # to prevent killing a valid signal before price even moves.
        # INV-1: skip the EMA-crossover rule entirely for counter-trend setups —
        # their EMAs were misaligned at creation, so a "crossover" detection here
        # is a false positive: nothing crossed, the alignment is unchanged.
        # Setup-class exemption (2026-05-09): LSR / FAR fade an existing move
        # by design and are routinely dispatched in trending regimes that the
        # regime-based ``_counter_trend`` flag does not catch.  See
        # ``_EMA_CROSSOVER_EXEMPT_SETUPS`` rationale.
        _setup_class = str(getattr(sig, "setup_class", "") or "").upper()
        _setup_exempt = _setup_class in _EMA_CROSSOVER_EXEMPT_SETUPS
        _crossover_min_age = 300  # seconds
        if (
            not _counter_trend
            and not _setup_exempt
            and ema9 is not None
            and ema21 is not None
            and sig.status not in ("TP1_HIT", "TP2_HIT")
            and age_secs >= _crossover_min_age
        ):
            if is_long and ema9 < ema21:
                return "EMA bearish crossover (EMA9 < EMA21) – LONG thesis invalidated"
            if not is_long and ema9 > ema21:
                return "EMA bullish crossover (EMA9 > EMA21) – SHORT thesis invalidated"

        # 3. Momentum loss — direction-aware (2026-05-07 fix).
        #
        # Previously this was ``abs(momentum) < threshold`` which killed any
        # signal during normal consolidation (price meandering near zero
        # momentum is NOT a thesis failure for a continuation setup —
        # it's just the market resting before the next leg).
        #
        # Owner-flagged 2026-05-07 case:
        #   SOLUSDT CONTINUATION_LIQUIDITY_SWEEP LONG @ 88.57 — invalidated
        #   10 min after dispatch with ``|momentum|=0.090`` while price
        #   was effectively flat at 88.58 (+0.01%).  Within the same hour
        #   price recovered above entry and would have hit TP1.
        #
        # Direction-aware check:
        #   LONG  invalidates only when momentum is significantly NEGATIVE
        #         (price actively falling against the trade).
        #   SHORT invalidates only when momentum is significantly POSITIVE
        #         (price actively rising against the trade).
        #   Near-zero momentum is consolidation, not failure — the trailing
        #   stop / SL handles those exits.
        #
        # Threshold per-channel; per-channel for TAPE 1m noise reasons.
        # ATR-adaptive scaling unchanged.  Micro-cap (entry < 0.001) scaling
        # unchanged.  Consecutive-readings requirement unchanged.
        mom_threshold = INVALIDATION_MOMENTUM_THRESHOLD.get(sig.channel, 0.15)
        # ATR-adaptive threshold: scale by ATR/entry_price so volatile pairs
        # (ETH, SOL) get wider thresholds and stable pairs (BTC) get tighter ones.
        # Floor: 0.05, Cap: 0.25. Fall back to fixed threshold if ATR unavailable.
        _atr_val = indicators.get("atr_last") if indicators else None
        entry_price = sig.entry if sig.entry > 0 else sig.current_price
        if _atr_val is not None and entry_price > 0:
            _atr_threshold = 0.1 * float(_atr_val) / entry_price * 100.0
            mom_threshold = max(0.05, min(0.25, _atr_threshold))
        # Prefer entry price; fall back to current_price only if entry is unset (0).
        # The current_price check guards against a zero fallback.
        if 0 < entry_price < 0.001:
            mom_threshold *= 0.1
        # Direction-aware: positive momentum = price rising, negative = falling.
        # LONG signals only invalidate when momentum is strongly negative;
        # SHORT signals only when momentum is strongly positive.
        _momentum_against_thesis = (
            momentum is not None
            and (
                (is_long and momentum < -mom_threshold)
                or (not is_long and momentum > mom_threshold)
            )
        )
        if _momentum_against_thesis:
            sig.momentum_invalidation_count += 1
            consecutive_required = INVALIDATION_CONSECUTIVE_THRESHOLD.get(sig.channel, 1)
            if sig.momentum_invalidation_count >= consecutive_required:
                _direction_label = "LONG" if is_long else "SHORT"
                _direction_test = (
                    f"< -{mom_threshold:.3f}" if is_long
                    else f"> {mom_threshold:.3f}"
                )
                return (
                    f"momentum against thesis (momentum={momentum:.3f} {_direction_test} "
                    f"for {_direction_label}, {sig.momentum_invalidation_count} "
                    f"consecutive readings) – signal thesis invalidated"
                )
            # Not enough consecutive readings yet — don't invalidate
        else:
            sig.momentum_invalidation_count = 0  # Reset on recovery / consolidation

        return None

    async def _check_per_user_invalidation(self, sig: Signal) -> None:
        """Enforce per-user invalidation mode for FSM positions that differ from
        the engine-wide default.

        Two enforcement paths:

        * **Tight** users (``invalidation_mode="tight"``) get the ATR-trailing
          kill that standard mode skips.  When the engine default is not
          "tight", we run ``_check_invalidation`` with ``mode_override="tight"``
          for each tight-mode user and close just their position if it fires.
          The engine signal is not touched — other users are unaffected.

        * **Loose** users are NOT closed here.  They are excluded from the
          engine-wide close in ``_broker_close_full`` via ``excluded_modes``
          when reason is "invalidated".

        Called from ``_process_signal`` BEFORE the engine's global invalidation
        check so tight-mode users always get the most protective treatment.
        """
        _global_mode = (INVALIDATION_MODE_DEFAULT or "standard").strip().lower()
        if _global_mode not in _VALID_INVALIDATION_MODES:
            _global_mode = "standard"

        # Nothing to do for tight users when the engine already runs tight.
        if _global_mode == "tight":
            return

        try:
            from src.execution import signal_dispatch as _sd
            user_positions = _sd.get_fsm_positions_for_signal(sig.signal_id)
        except Exception as exc:
            log.debug(
                "_check_per_user_invalidation: get_fsm_positions_for_signal "
                "failed signal_id={} exc={}",
                sig.signal_id, exc,
            )
            return

        for uid, pos in user_positions:
            if pos.invalidation_mode != "tight":
                continue
            tight_reason = self._check_invalidation(sig, mode_override="tight")
            if not tight_reason:
                continue
            log.info(
                "_check_per_user_invalidation: tight-mode early kill "
                "uid={} signal_id={} symbol={} reason={}",
                uid, sig.signal_id, sig.symbol, tight_reason,
            )
            try:
                await _sd.close_single_fsm_position(
                    uid, sig.signal_id,
                    symbol=sig.symbol,
                    direction=sig.direction.value,
                    reason="inv_tight",
                )
            except Exception as exc:
                log.warning(
                    "_check_per_user_invalidation: close_single_fsm_position "
                    "failed uid={} signal_id={} exc={}",
                    uid, sig.signal_id, exc,
                )

    async def _evaluate_signal(self, sig: Signal) -> None:
        # Terminal-status guard (2026-05-08): if the signal already reached
        # a terminal lifecycle state, return immediately — re-evaluating
        # would re-fire the SL_HIT / INVALIDATED / EXPIRED / FULL_TP_HIT
        # close event and post a duplicate Telegram message.
        #
        # Owner reported duplicates of the same lifecycle event posted at
        # identical timestamps (e.g. two INVALIDATED ZECUSDT messages at
        # 04:10:11) plus 6-minute-apart re-fires of the same SL_HIT
        # (FLOCKUSDT @ 04:10:11 and 04:16:29 with identical PnL).  Root
        # cause: ``_check_all`` builds a snapshot of ``router.active_signals``
        # via ``dict(...)`` then ``gather``s ``_process_signal`` over its
        # values, and any duplicate keys in the underlying dict (or any
        # subsequent re-add path) would yield the same Signal object
        # multiple times within a single tick.  Without this guard, both
        # tasks raced through the SL/invalidation handlers and both
        # awaited ``_post_update`` before either reached ``_remove``.
        #
        # Note: TP1_HIT and TP2_HIT are NOT terminal — those signals stay
        # active for TP2 / TP3 progression.  Only fully-closed states are
        # in ``_TERMINAL_STATUSES``.
        if sig.status in _TERMINAL_STATUSES:
            return

        price = sig.current_price
        is_long = sig.direction == Direction.LONG

        # Minimum lifespan guard – don't trigger SL/TP checks on very new
        # signals to protect against noise-driven instant stops
        min_lifespan = MIN_SIGNAL_LIFESPAN_SECONDS.get(sig.channel, 10)
        age_secs = (utcnow() - sig.timestamp).total_seconds()
        if age_secs < min_lifespan:
            log.debug(
                "Signal %s %s too new (%.1fs < %ds min lifespan) – skipping SL/TP eval",
                sig.symbol, sig.channel, age_secs, min_lifespan,
            )
            return

        # Max hold duration guard – auto-expire signals that have been open too long
        max_hold = MAX_SIGNAL_HOLD_SECONDS.get(sig.channel, 86400)
        if age_secs >= max_hold:
            self._set_realized_pnl(sig, price)
            sig.status = "EXPIRED"
            await self._post_update(sig, "⏰ EXPIRED (max hold time reached)")
            self._record_outcome(sig, hit_tp=0, hit_sl=False, expired=True)  # BUG FIX
            await self._broker_close_full(sig, reason="expired", fill_price=price)
            self._remove(sig.signal_id)
            return

        # Notify AI Trade Observer with a mid-trade snapshot (fail-open)
        if self.observer is not None:
            try:
                self.observer.observe_trade(sig, price)
            except Exception as exc:
                log.debug("TradeObserver.observe_trade failed (non-critical): {}", exc)

        # DCA (Double Entry) check — only on ACTIVE signals before TP1 is hit
        if sig.status == "ACTIVE" and not sig.entry_2_filled:
            chan_cfg = next(
                (c for c in ALL_CHANNELS if c.name == sig.channel), None
            )
            if chan_cfg is not None and chan_cfg.dca_enabled:
                dca_price = check_dca_entry(
                    sig=sig,
                    current_price=price,
                    indicators=None,
                    smc_data=None,
                    channel_config=chan_cfg,
                )
                if dca_price is not None:
                    recalculate_after_dca(
                        sig=sig,
                        entry_2_price=dca_price,
                        tp_ratios=list(chan_cfg.tp_ratios),
                        weight_1=chan_cfg.dca_weight_1,
                        weight_2=chan_cfg.dca_weight_2,
                    )
                    # Push the DCA Entry-2 to the broker so the auto-trade
                    # position matches the engine's weighted-avg-entry math.
                    # Without this, engine assumes 60/40 weighted entry but
                    # broker has only Entry-1 size — P&L attribution diverges.
                    if (
                        self._order_manager is not None
                        and self._order_manager.is_enabled
                    ):
                        try:
                            await self._order_manager.add_dca_entry(
                                sig, current_price=dca_price
                            )
                        except Exception as exc:
                            log.warning(
                                "add_dca_entry failed for %s: %s",
                                sig.symbol, exc,
                            )
                    await self._post_dca_update(sig)

        # SL direction sanity check – catch misconfigured signals
        protective_stop_active = sig.status in ("TP1_HIT", "TP2_HIT")
        if is_long and sig.stop_loss > sig.entry and not protective_stop_active:
            log.warning(
                "Signal %s %s has invalid SL (LONG SL %.8f > entry %.8f) – cancelling",
                sig.symbol, sig.signal_id, sig.stop_loss, sig.entry,
            )
            sig.status = "CANCELLED"
            await self._post_update(sig, "⚠️ CANCELLED (invalid SL)")
            await self._broker_close_full(sig, reason="cancelled", fill_price=price)
            self._remove(sig.signal_id)
            return
        if not is_long and sig.stop_loss < sig.entry and not protective_stop_active:
            log.warning(
                "Signal %s %s has invalid SL (SHORT SL %.8f < entry %.8f) – cancelling",
                sig.symbol, sig.signal_id, sig.stop_loss, sig.entry,
            )
            sig.status = "CANCELLED"
            await self._post_update(sig, "⚠️ CANCELLED (invalid SL)")
            await self._broker_close_full(sig, reason="cancelled", fill_price=price)
            self._remove(sig.signal_id)
            return

        # PnL
        if sig.entry != 0:
            sig.pnl_pct = calculate_trade_pnl_pct(
                entry_price=sig.entry,
                exit_price=price,
                direction=sig.direction.value,
            )
        sig.max_favorable_excursion_pct = max(sig.max_favorable_excursion_pct, sig.pnl_pct)
        sig.max_adverse_excursion_pct = min(sig.max_adverse_excursion_pct, sig.pnl_pct)

        # Zero-PnL guard – don't trigger SL when price hasn't moved from entry
        # This prevents false stops from stale prices or floating-point noise
        if abs(sig.pnl_pct) < _ZERO_PNL_THRESHOLD_PCT:
            log.debug(
                "Signal %s %s PnL near zero (%.4f%%) – skipping SL/TP eval",
                sig.symbol, sig.signal_id, sig.pnl_pct,
            )
            return

        # Stop-loss hit — checked BEFORE invalidation so that a price gap
        # through the SL is never exited at a worse price via invalidation.
        # Get 1m candle high/low for accurate SL/TP evaluation.
        # Correct behavior matches real Binance stop orders:
        #   LONG  SL: candle LOW  reaches SL → stop order triggered (even if close above)
        #   SHORT SL: candle HIGH reaches SL → stop order triggered (even if close below)
        #   LONG  TP: candle HIGH reaches TP → take profit triggered
        #   SHORT TP: candle LOW  reaches TP → take profit triggered
        # Using 1m candle vs individual ticks eliminates ultra-thin single-order
        # price spikes that don't represent real sustained price movement.
        _c_high, _c_low = self._candle_extremes(sig.symbol)

        # Limit-order entry-zone fill check (2026-05-07 fix).
        # Signals dispatched as "Execution: LIMIT ORDER" carry an
        # ``entry_zone_low``/``entry_zone_high`` band; the subscriber's
        # limit order only fills if price actually enters the band.
        # Skip SL/TP/invalidation monitoring entirely until that has
        # happened — otherwise a fast-moving setup can ship "instant SL"
        # signals where price was already past the SL at dispatch time.
        # Market-order signals (no entry_zone_low/high) are treated as
        # filled immediately on first eval.
        if not getattr(sig, "entry_zone_filled", False):
            zone_low = getattr(sig, "entry_zone_low", None)
            zone_high = getattr(sig, "entry_zone_high", None)
            if zone_low is None or zone_high is None:
                # No entry zone defined — market-order semantics, treat as filled.
                sig.entry_zone_filled = True
            else:
                # Has the 1m candle range overlapped [zone_low, zone_high]?
                if (
                    _c_high > 0
                    and _c_low > 0
                    and _c_high >= float(zone_low)
                    and _c_low <= float(zone_high)
                ):
                    sig.entry_zone_filled = True
                    log.debug(
                        "Entry zone visited for {} {}: zone=[{:.6f},{:.6f}], "
                        "candle=[{:.6f},{:.6f}] — flipping entry_zone_filled=True",
                        sig.symbol, sig.signal_id,
                        float(zone_low), float(zone_high), _c_low, _c_high,
                    )
                else:
                    # Limit order hasn't filled yet.  Don't run SL/TP checks
                    # — they would fire against the un-filled mid as if real.
                    # Expiry handling lives in `cleanup_expired` and will
                    # mark this as EXPIRED if validity elapses.
                    return

        # Pre-TP grab (Phase A) — fire BEFORE the SL check so that if the same
        # candle whipped up to the threshold and back down to entry we still
        # bank the symbolic win and the SL→breakeven move converts what would
        # have been a small NET LOSS at 10x leverage into a clean breakeven.
        await self._check_pre_tp_grab(sig, _c_high, _c_low)

        # A full-close (100%) pre-TP finalizes the signal in-handler and removes
        # it from the Open book — there is no residual left to run SL/TP
        # against.  Detect that via active-book membership (NOT status, since
        # TP1_HIT/TP2_HIT are legitimate open states that must keep processing)
        # and stop here, so we don't fire the SL path against the just-ratcheted
        # breakeven stop on a flat position (which would double-post a close and
        # overwrite the banked outcome).
        # Guard fires only when the book is non-empty AND the signal is absent —
        # an empty book (e.g. direct test calls to _evaluate_signal) should not
        # prematurely abort SL/TP evaluation.
        _active_book = self._get_signals()
        if _active_book and sig.signal_id not in _active_book:
            return

        _sl_triggered = (
            (is_long and _c_low > 0 and _c_low <= sig.stop_loss) or
            (not is_long and _c_high > 0 and _c_high >= sig.stop_loss)
        )

        # Mark-price SL backstop: when _candle_extremes returns (0, 0) because
        # the data store has no 1m candle for this symbol (new listing, WS gap,
        # store miss), the wick-filter guard above silently misses a crossed SL.
        # Fall back to the mark price only when candle data is absent — so the
        # existing wick-filter still applies for all normally-tracked symbols.
        if not _sl_triggered and price > 0 and (_c_low <= 0 or _c_high <= 0):
            _sl_triggered = (
                (is_long and price <= sig.stop_loss) or
                (not is_long and price >= sig.stop_loss)
            )
            if _sl_triggered:
                log.warning(
                    "SL backstop via mark price (no candle data) "
                    "symbol={} signal_id={} mark={:.8f} stop={:.8f}",
                    sig.symbol, sig.signal_id, price, sig.stop_loss,
                )

        if _sl_triggered:
            if sig.first_sl_touch_timestamp is None:
                sig.first_sl_touch_timestamp = utcnow()
            self._set_realized_pnl(sig, sig.stop_loss)
            outcome_label = self._apply_final_outcome(sig, hit_tp=0, hit_sl=True)
            outcome_event = _STOP_OUTCOME_MESSAGES.get(outcome_label, "🔴 EXIT")
            await self._post_update(sig, outcome_event)
            self._record_outcome(sig, hit_tp=0, hit_sl=True)
            await self._post_signal_closed(sig, is_tp=False)
            await self._broker_close_full(
                sig, reason="sl_hit", fill_price=sig.stop_loss
            )
            self._remove(sig.signal_id)
            return

        # Market-structure invalidation – close stale signals whose thesis no
        # longer holds (regime flip, momentum loss, EMA crossover).  Checked
        # AFTER the SL check so that a price gap through the SL is always
        # caught at the SL level, not at the (potentially worse) current price.
        invalidation_reason = self._check_invalidation(sig)
        if invalidation_reason:
            # Cap the exit price — invalidation must never produce a worse exit
            # than the SL would have given.  For a LONG that gapped down, the
            # capped price is the SL; for a SHORT that gapped up, it is the SL.
            if is_long:
                capped_price = max(price, sig.stop_loss)
            else:
                capped_price = min(price, sig.stop_loss)
            self._set_realized_pnl(sig, capped_price)
            sig.status = "INVALIDATED"
            # Invalidation Quality Audit: record the kill so a periodic classifier
            # can later mark it PROTECTIVE / PREMATURE / NEUTRAL by examining the
            # post-kill price action.  Without this we have no ground truth on
            # whether the invalidation gate is helping or hurting.
            try:
                from src.invalidation_audit import record_invalidation
                record_invalidation(
                    signal_id=sig.signal_id,
                    symbol=sig.symbol,
                    channel=sig.channel,
                    setup_class=sig.setup_class or "",
                    direction=sig.direction.value,
                    entry=sig.entry,
                    stop_loss=sig.stop_loss,
                    tp1=sig.tp1,
                    kill_price=capped_price,
                    kill_reason=invalidation_reason,
                    pnl_pct_at_kill=sig.pnl_pct,
                )
            except Exception as exc:  # noqa: BLE001 — audit must never break the close
                log.debug("invalidation_audit.record_invalidation failed for {}: {}", sig.symbol, exc)
            await self._post_update(sig, f"🔄 INVALIDATED ({invalidation_reason})")
            self._record_outcome(sig, hit_tp=0, hit_sl=False)
            await self._broker_close_full(
                sig, reason="invalidated", fill_price=capped_price
            )
            self._remove(sig.signal_id)
            if self.on_invalidation_callback is not None:
                self.on_invalidation_callback(sig.symbol, sig.channel, sig.direction.value)
            return

        # TP hits (progressive)
        _tp_hit_price = _c_high if is_long else _c_low

        if is_long:
            if sig.tp3 and _c_high > 0 and _c_high >= sig.tp3 and sig.status != "TP3_HIT":
                if sig.first_tp_touch_timestamp is None:
                    sig.first_tp_touch_timestamp = utcnow()
                tp3_pnl = calculate_trade_pnl_pct(
                    entry_price=sig.entry, exit_price=sig.tp3, direction=sig.direction.value
                )
                if self.on_highlight_callback is not None:
                    self.on_highlight_callback(sig, 3, tp3_pnl)
                # Partial TP3 execution: close 34% of original position size
                if self._order_manager is not None and self._order_manager.is_enabled:
                    try:
                        await self._order_manager.close_partial(sig, 0.34, tp_level=3)
                    except Exception as _exc:
                        log.warning("Partial TP3 close failed for {}: {}", sig.symbol, _exc)
                # FSM positions: close any remaining qty at market.  Native TP3 orders
                # on Binance already filled → -2022 ReduceOnly rejected → treated as
                # success.  Positions opened without native TP orders (pre-#488 bug)
                # still have open qty → MARKET close fires here instead.
                await self._broker_close_full(sig, reason="full_tp_hit", fill_price=sig.tp3)
                self._set_realized_pnl(sig, sig.tp3)
                self._apply_final_outcome(sig, hit_tp=3, hit_sl=False)
                await self._post_update(sig, "🎯🎯🎯 FULL TP HIT")
                self._record_outcome(sig, hit_tp=3, hit_sl=False)
                await self._post_signal_closed(sig, is_tp=True, tp_label="TP3", close_price=sig.tp3)
                self._remove(sig.signal_id)
                return
            if _c_high > 0 and _c_high >= sig.tp2 and sig.status not in ("TP2_HIT", "TP3_HIT"):
                if sig.first_tp_touch_timestamp is None:
                    sig.first_tp_touch_timestamp = utcnow()
                sig.status = "TP2_HIT"
                await self._post_update(sig, "🎯🎯 TP2 HIT")
                # Snapshot best-TP PnL for signal quality stats
                sig.best_tp_hit = 2
                sig.best_tp_pnl_pct = calculate_trade_pnl_pct(
                    entry_price=sig.entry, exit_price=sig.tp2, direction=sig.direction.value
                )
                if self.on_highlight_callback is not None:
                    self.on_highlight_callback(sig, 2, sig.best_tp_pnl_pct)
                # Trailing: move SL to TP1 price to protect banked profit while giving TP3 room
                sig.stop_loss = sig.tp1
                # Partial TP2 execution: close 33% of original position size
                if self._order_manager is not None and self._order_manager.is_enabled:
                    try:
                        await self._order_manager.close_partial(sig, 0.33, tp_level=2)
                    except Exception as _exc:
                        log.warning("Partial TP2 close failed for {}: {}", sig.symbol, _exc)
            if _c_high > 0 and _c_high >= sig.tp1 and sig.status not in ("TP1_HIT", "TP2_HIT", "TP3_HIT"):
                if sig.first_tp_touch_timestamp is None:
                    sig.first_tp_touch_timestamp = utcnow()
                sig.status = "TP1_HIT"
                await self._post_update(sig, "🎯 TP1 HIT ✅")
                # Snapshot best-TP PnL for signal quality stats (only if TP2 not already hit)
                if sig.best_tp_hit < 1:
                    sig.best_tp_hit = 1
                    sig.best_tp_pnl_pct = calculate_trade_pnl_pct(
                        entry_price=sig.entry, exit_price=sig.tp1, direction=sig.direction.value
                    )
                # Move SL to breakeven + small buffer (15% of TP1 distance) so that a
                # retrace between TP1 and TP2 never produces a full loss after the thesis
                # has already been proven by TP1.  Only move SL upward for longs.
                tp1_dist = abs(sig.tp1 - sig.entry)
                be_buffer = tp1_dist * 0.15
                new_be_sl = sig.entry + be_buffer
                sig.stop_loss = max(sig.stop_loss, new_be_sl)
                # Partial TP1 execution: close 33% of original position size
                if self._order_manager is not None and self._order_manager.is_enabled:
                    try:
                        await self._order_manager.close_partial(sig, 0.33, tp_level=1)
                    except Exception as _exc:
                        log.warning("Partial TP1 close failed for {}: {}", sig.symbol, _exc)
        else:
            if sig.tp3 and _c_low > 0 and _c_low <= sig.tp3 and sig.status != "TP3_HIT":
                if sig.first_tp_touch_timestamp is None:
                    sig.first_tp_touch_timestamp = utcnow()
                tp3_pnl = calculate_trade_pnl_pct(
                    entry_price=sig.entry, exit_price=sig.tp3, direction=sig.direction.value
                )
                if self.on_highlight_callback is not None:
                    self.on_highlight_callback(sig, 3, tp3_pnl)
                # Partial TP3 execution: close 34% of original position size
                if self._order_manager is not None and self._order_manager.is_enabled:
                    try:
                        await self._order_manager.close_partial(sig, 0.34, tp_level=3)
                    except Exception as _exc:
                        log.warning("Partial TP3 close failed for {}: {}", sig.symbol, _exc)
                # FSM positions: close any remaining qty at market.  Native TP3 orders
                # on Binance already filled → -2022 ReduceOnly rejected → treated as
                # success.  Positions opened without native TP orders (pre-#488 bug)
                # still have open qty → MARKET close fires here instead.
                await self._broker_close_full(sig, reason="full_tp_hit", fill_price=sig.tp3)
                self._set_realized_pnl(sig, sig.tp3)
                self._apply_final_outcome(sig, hit_tp=3, hit_sl=False)
                await self._post_update(sig, "🎯🎯🎯 FULL TP HIT")
                self._record_outcome(sig, hit_tp=3, hit_sl=False)
                await self._post_signal_closed(sig, is_tp=True, tp_label="TP3", close_price=sig.tp3)
                self._remove(sig.signal_id)
                return
            if _c_low > 0 and _c_low <= sig.tp2 and sig.status not in ("TP2_HIT", "TP3_HIT"):
                if sig.first_tp_touch_timestamp is None:
                    sig.first_tp_touch_timestamp = utcnow()
                sig.status = "TP2_HIT"
                await self._post_update(sig, "🎯🎯 TP2 HIT")
                # Snapshot best-TP PnL for signal quality stats
                sig.best_tp_hit = 2
                sig.best_tp_pnl_pct = calculate_trade_pnl_pct(
                    entry_price=sig.entry, exit_price=sig.tp2, direction=sig.direction.value
                )
                if self.on_highlight_callback is not None:
                    self.on_highlight_callback(sig, 2, sig.best_tp_pnl_pct)
                sig.stop_loss = sig.tp1
                # Partial TP2 execution: close 33% of original position size
                if self._order_manager is not None and self._order_manager.is_enabled:
                    try:
                        await self._order_manager.close_partial(sig, 0.33, tp_level=2)
                    except Exception as _exc:
                        log.warning("Partial TP2 close failed for {}: {}", sig.symbol, _exc)
            if _c_low > 0 and _c_low <= sig.tp1 and sig.status not in ("TP1_HIT", "TP2_HIT", "TP3_HIT"):
                if sig.first_tp_touch_timestamp is None:
                    sig.first_tp_touch_timestamp = utcnow()
                sig.status = "TP1_HIT"
                await self._post_update(sig, "🎯 TP1 HIT ✅")
                # Snapshot best-TP PnL for signal quality stats (only if TP2 not already hit)
                if sig.best_tp_hit < 1:
                    sig.best_tp_hit = 1
                    sig.best_tp_pnl_pct = calculate_trade_pnl_pct(
                        entry_price=sig.entry, exit_price=sig.tp1, direction=sig.direction.value
                    )
                # Move SL to breakeven - small buffer (15% of TP1 distance) so that a
                # retrace between TP1 and TP2 never produces a full loss after the thesis
                # has already been proven by TP1.  Only move SL downward for shorts.
                tp1_dist = abs(sig.tp1 - sig.entry)
                be_buffer = tp1_dist * 0.15
                new_be_sl = sig.entry - be_buffer
                sig.stop_loss = min(sig.stop_loss, new_be_sl)
                # Partial TP1 execution: close 33% of original position size
                if self._order_manager is not None and self._order_manager.is_enabled:
                    try:
                        await self._order_manager.close_partial(sig, 0.33, tp_level=1)
                    except Exception as _exc:
                        log.warning("Partial TP1 close failed for {}: {}", sig.symbol, _exc)

        # Trailing stop adjustment
        if sig.trailing_active and sig.status in ("TP1_HIT", "TP2_HIT"):
            self._adjust_trailing(sig)

    def _adjust_trailing(self, sig: Signal) -> None:
        """Move the trailing stop behind the price using an ATR-based distance.

        The trailing distance is ``atr_value * atr_multiplier`` where
        ``atr_multiplier`` comes from the channel's ``trailing_atr_mult``
        config field (or the global ``TRAILING_ATR_MULTIPLIER`` constant when
        the channel config cannot be found).

        Phase-based tightening: after TP1 the multiplier is reduced to 55% of
        the base, and after TP2 to 35%, locking progressively more profit.

        Regime-aware adjustment: in trending markets the trail is kept loose
        (×1.2) to let winners run; in ranging markets it is tightened (×0.7)
        to protect profit before a range-edge reversal.

        Falls back to ``original_sl_distance * 0.75`` when ATR data is
        unavailable (e.g. candles not yet loaded for this symbol).
        """
        price = sig.current_price
        # Use the original SL distance (stored at signal creation) so that the
        # trailing buffer doesn't collapse to zero after TP2 moves SL to break-even.
        # Fall back to the live distance only for legacy signals where the field is unset.
        base_dist = sig.original_sl_distance or abs(sig.entry - sig.stop_loss)

        # ------------------------------------------------------------------
        # Attempt ATR-based trailing distance
        # ------------------------------------------------------------------
        trail_dist: Optional[float] = None
        candles = self._store.get_candles(sig.symbol, "1m")
        if candles is not None and len(candles.get("close", [])) >= 15:
            try:
                highs = np.asarray(candles["high"], dtype=np.float64)
                lows = np.asarray(candles["low"], dtype=np.float64)
                closes = np.asarray(candles["close"], dtype=np.float64)
                atr_arr = _compute_atr(highs, lows, closes, 14)
                valid = atr_arr[~np.isnan(atr_arr)]
                if len(valid) > 0:
                    atr_value = float(valid[-1])
                    # Use per-channel multiplier when available, otherwise the global default
                    chan_cfg = next(
                        (c for c in ALL_CHANNELS if c.name == sig.channel), None
                    )
                    base_mult = (
                        chan_cfg.trailing_atr_mult if chan_cfg is not None else TRAILING_ATR_MULTIPLIER
                    )

                    # Phase-based tightening: lock more profit as each TP is cleared
                    if sig.status == "TP2_HIT":
                        effective_mult = base_mult * 0.35  # Very tight – profit protection
                    elif sig.status == "TP1_HIT":
                        effective_mult = base_mult * 0.55  # Tighter after first target
                    else:
                        effective_mult = base_mult  # Default for ACTIVE signals

                    # Regime-aware adjustment: loose in trends, tight in ranges
                    if self._regime_detector is not None:
                        try:
                            indicators_for_regime: dict = {}
                            if self._indicators_fn is not None:
                                indicators_for_regime = self._indicators_fn(sig.symbol) or {}
                            elif candles and len(candles.get("close", [])) >= 21:
                                regime_closes = np.asarray(candles["close"], dtype=np.float64)
                                ema9_arr = _compute_ema(regime_closes, 9)
                                ema21_arr = _compute_ema(regime_closes, 21)
                                indicators_for_regime = {
                                    "ema9_last": float(ema9_arr[-1]) if len(ema9_arr) else None,
                                    "ema21_last": float(ema21_arr[-1]) if len(ema21_arr) else None,
                                }
                            regime_result = self._regime_detector.classify(indicators_for_regime)
                            regime_label = regime_result.regime.value if regime_result else "RANGING"
                            regime_trail_mult = {
                                "TRENDING_UP": 1.2,
                                "TRENDING_DOWN": 1.2,
                                "RANGING": 0.7,
                                "VOLATILE": 0.9,
                                "QUIET": 0.8,
                            }.get(regime_label, 1.0)
                            effective_mult *= regime_trail_mult
                        except Exception:
                            pass  # Fall back to non-regime-adjusted multiplier

                    trail_dist = atr_value * effective_mult
            except Exception:
                trail_dist = None

        # Fall back to fixed 75 % of original SL distance when ATR is unavailable
        if trail_dist is None:
            trail_dist = base_dist * 0.75

        if sig.direction == Direction.LONG:
            new_sl = price - trail_dist
            if new_sl > sig.stop_loss:
                sig.stop_loss = round(new_sl, 8)
        else:
            new_sl = price + trail_dist
            if new_sl < sig.stop_loss:
                sig.stop_loss = round(new_sl, 8)

    async def _post_dca_update(self, sig: Signal) -> None:
        """Post a Telegram notification when DCA Entry 2 is taken."""
        channel_id = CHANNEL_TELEGRAM_MAP.get(sig.channel, "")
        if not channel_id:
            return

        chan_emojis = {
            "360_SCALP": "⚡",
        }
        chan_emoji = chan_emojis.get(sig.channel, "📡")
        dir_emoji = "🚀" if sig.direction == Direction.LONG else "⬇️"
        chan_cfg = next((c for c in ALL_CHANNELS if c.name == sig.channel), None)
        rr_str = ""
        if chan_cfg is not None:
            rr_parts = [f"{r}R" for r in chan_cfg.tp_ratios]
            rr_str = " / ".join(rr_parts)

        lines = [
            "📊 DCA ENTRY 2",
            f"{chan_emoji} *{_escape_md(sig.channel)}* | {_escape_md(sig.symbol)} *{sig.direction.value}* {dir_emoji}",
            f"💰 Entry 1: `{fmt_price(sig.original_entry)}` → Entry 2: `{fmt_price(sig.entry_2 if sig.entry_2 is not None else 0.0)}`",
            f"📊 Avg Entry: `{fmt_price(sig.avg_entry)}`",
            f"🎯 New TP1: `{fmt_price(sig.tp1)}` | TP2: `{fmt_price(sig.tp2)}`",
            f"🛑 SL: `{fmt_price(sig.stop_loss)}` (unchanged)",
        ]
        if rr_str:
            lines.append(f"📏 New R:R preserved at {rr_str}")
        lines.append(f"⏰ {fmt_ts()}")

        text = "\n".join(lines)
        await self._send(channel_id, text)

    async def _broker_close_full(
        self,
        sig: Signal,
        *,
        reason: str,
        fill_price: Optional[float] = None,
    ) -> None:
        """Best-effort full close on the broker (paper or live).

        Called from every non-TP close path (SL_HIT, INVALIDATED,
        EXPIRED, CANCELLED) to make sure the broker position closes
        in lockstep with engine state — the B12 safety guarantee.

        Two independent close paths run here:

        1. Legacy CCXT OrderManager — only active when
           AUTO_EXECUTION_MODE=live on the engine level (owner's own
           keys via CCXT).  No-ops when is_enabled=False.

        2. Server-side FSM (per-user Binance keys via signing service)
           — cancels native SL/TP bracket orders then places a MARKET
           REDUCE_ONLY close for each user who has an open FSM position
           for this signal_id.  This is the path that covers positions
           opened by signal_dispatch → position_fsm.place_signal().

        Always fail-soft: an error in either path logs but never blocks
        the engine state transition.  PositionReconciler's drift check
        (Phase A3) is the safety net for any close that slips through.
        Idempotent — calling on an already-closed position is a no-op.
        """
        # ── Path 1: legacy CCXT OrderManager ─────────────────────────
        if self._order_manager is not None and self._order_manager.is_enabled:
            try:
                await self._order_manager.close_full(
                    sig, reason=reason, current_price=fill_price
                )
            except Exception as exc:
                log.warning(
                    "broker close_full failed for %s (reason=%s): %s",
                    sig.symbol, reason, exc,
                )

        # ── Path 2: server-side FSM positions (per-user signing svc) ──
        # Cancel native bracket orders + MARKET-close for every user
        # who has a non-terminal FSM position for this signal_id.
        # Exception: loose-mode users survive engine invalidations — their
        # native SL/TP bracket is still live and they want to ride it out.
        # Other close reasons (sl_hit, expired, cancelled) close everyone.
        try:
            from src.execution import signal_dispatch as _sd
            _excl = frozenset({"loose"}) if reason == "invalidated" else None
            await _sd.close_fsm_positions_for_signal(
                sig.signal_id,
                symbol=sig.symbol,
                direction=sig.direction.value,
                reason=reason,
                excluded_modes=_excl,
            )
        except Exception as exc:
            log.warning(
                "FSM close_fsm_positions_for_signal failed for %s "
                "(reason=%s): %s",
                sig.symbol, reason, exc,
            )

    async def _post_update(self, sig: Signal, event: str) -> None:
        channel_id = CHANNEL_TELEGRAM_MAP.get(sig.channel, "")
        if not channel_id:
            return

        chan_emojis = {
            "360_SCALP": "⚡",
        }
        chan_emoji = chan_emojis.get(sig.channel, "📡")
        dir_emoji = "🚀" if sig.direction == Direction.LONG else "⬇️"

        lines = [
            f"{event}",
            f"{chan_emoji} *{_escape_md(sig.channel)}* | {_escape_md(sig.symbol)} *{sig.direction.value}* {dir_emoji}",
            f"💰 Entry: `{fmt_price(sig.entry)}` → Current: `{fmt_price(sig.current_price)}`",
            f"📊 PnL: *{sig.pnl_pct:+.2f}%*",
            f"🛡️ SL: `{fmt_price(sig.stop_loss)}`",
            f"🤖 Confidence: *{sig.confidence:.0f}%*",
        ]
        if sig.trailing_active and sig.trailing_desc:
            lines.append(f"💹 Trailing Active ({_escape_md(sig.trailing_desc)})")
        lines.append(f"⏰ {fmt_ts()}")

        text = "\n".join(lines)
        await self._send(channel_id, text)

    async def _post_pre_tp_alert(
        self,
        sig: Signal,
        favourable_pct: float,
        net_pct: float,
        *,
        partial_fraction: float = 0.0,
        partial_executed: bool = False,
    ) -> None:
        """Dedicated, eye-catching Pre-TP alert — bypasses the generic update
        template so subscribers don't scroll past it as a routine status post.

        Doctrine (OWNER_BRIEF §3.2 / §3.2a, 2026-05-17): Pre-TP is the PRIMARY
        exit mechanism, not a safety net.  When the auto-trader is enabled
        and the broker accepted a partial close, the alert reports the
        realised fraction *and* the residual SL-to-breakeven move.  When the
        broker is disabled (signal-only mode) or the partial close didn't
        execute, the alert falls back to the pre-2026-05-17 SL-to-breakeven
        framing — but never with the misleading "Banked +X%" wording from
        before this PR.
        """
        channel_id = CHANNEL_TELEGRAM_MAP.get(sig.channel, "")
        if not channel_id:
            return
        dir_emoji = "🚀" if sig.direction == Direction.LONG else "⬇️"
        sep = "━" * 24
        if partial_executed and partial_fraction > 0:
            pct_closed = int(round(partial_fraction * 100))
            pct_residual = 100 - pct_closed
            text = "\n".join([
                "⚡ *PRE-TP PARTIAL CLOSE* ⚡",
                sep,
                f"{_escape_md(sig.symbol)} *{sig.direction.value}* {dir_emoji}",
                "",
                f"💰 Closed *{pct_closed}%* of position at *+{favourable_pct:.2f}%* raw",
                f"💵 Realised net @ {PRE_TP_LEVERAGE:.0f}x: *{net_pct * partial_fraction:+.2f}%* on margin",
                f"🛡️ Residual {pct_residual}% rides to TP1 — SL → breakeven `{fmt_price(sig.entry)}`",
                "",
                "✅ Risk-managed — banked profit + remaining position protected",
                f"⏰ {fmt_ts()}",
            ])
        else:
            text = "\n".join([
                "⚡ *PRE-TP TRIGGER* ⚡",
                sep,
                f"{_escape_md(sig.symbol)} *{sig.direction.value}* {dir_emoji}",
                "",
                f"💰 Favourable move: *+{favourable_pct:.2f}%* raw",
                f"💵 Net @ {PRE_TP_LEVERAGE:.0f}x: *{net_pct:+.2f}%* (after fees, if exited now)",
                f"🛡️ SL → breakeven `{fmt_price(sig.entry)}`",
                "",
                "_Signal-only mode — auto-trade not enabled; close manually to bank._",
                f"⏰ {fmt_ts()}",
            ])
        await self._send(channel_id, text)

    async def _check_pre_tp_grab(
        self, sig: Signal, c_high: float, c_low: float
    ) -> bool:
        """Pre-TP grab — bank a small symbolic win and move SL to breakeven.

        Triggered when an active signal moves favourably by an ATR-adaptive
        threshold within ``PRE_TP_MAX_AGE_SEC`` (default 30 min) of dispatch,
        in a non-TRENDING regime, and on a non-breakout setup.

        Threshold resolution (B11 fee-aware):
          ``threshold = max(PRE_TP_FEE_FLOOR_PCT,
                            PRE_TP_ATR_MULTIPLIER × atr_pct)``
        where ``atr_pct = atr_last / entry × 100`` from the latest 5m
        candle.  Falls back to the static ``PRE_TP_THRESHOLD_PCT`` when
        ATR is unavailable.  The fee floor (default 0.20%) guarantees
        ≥+1.3% net @ 10x even on low-vol pairs; the ATR term scales up
        to capture larger wins on volatile alts without capping winners.

        Why this exists: at typical subscriber leverage (10x) with 0.07%
        round-trip fees the breakeven price move is ~0.07% raw.  Most
        invalidation kills today close at "neutral" which is actually a
        ~0.7% NET LOSS on margin.  Pre-TP turns those would-be-losses
        into net-positive trades by banking the ATR-adaptive minimum and
        ratcheting SL to entry so the rest of the position is free.

        Returns True iff pre-TP fired this cycle.  Best-effort — exceptions
        are logged and swallowed so the surrounding SL/TP loop is never
        disrupted.
        """
        if not PRE_TP_ENABLED:
            return False
        if getattr(sig, "pre_tp_hit", False):
            return False
        if sig.status != "ACTIVE":
            return False
        # Setup gate — exclude breakout family (their thesis depends on bigger moves)
        setup_class = str(getattr(sig, "setup_class", ""))
        if setup_class in PRE_TP_SETUP_BLACKLIST:
            return False
        # Age gate
        try:
            age_secs = (utcnow() - sig.timestamp).total_seconds() if sig.timestamp else 0.0
        except Exception:
            age_secs = 0.0
        if age_secs < PRE_TP_MIN_AGE_SEC or age_secs > PRE_TP_MAX_AGE_SEC:
            return False

        is_long = sig.direction == Direction.LONG
        entry = float(sig.entry)
        if entry <= 0:
            return False

        # Fetch indicators once — used for the regime gate below.  When the
        # signal was dispatched after pre-TP stamping shipped, ATR is also
        # already on the signal so we don't need indicators for threshold
        # resolution.  Fail-open if the indicators_fn raises or returns nil.
        indicators: Optional[Dict[str, Any]] = None
        if self._indicators_fn is not None:
            try:
                indicators = self._indicators_fn(sig.symbol)
            except Exception as exc:
                log.debug("Pre-TP indicators_fn failed for %s: %s", sig.symbol, exc)
                indicators = None

        # Prefer the dispatch-time stamp (B11 fee-aware doctrine — locks the
        # promise shown in the Telegram post against ATR drift between
        # dispatch and fire).  Legacy in-flight signals from before stamping
        # shipped lack the stamp; backfill via the stamping helper using
        # ATR fetched here.
        from src.pre_tp_stamping import is_stamped, resolve_pre_tp_threshold

        atr_last: Optional[float] = None
        if is_stamped(sig):
            threshold_pct = float(sig.pre_tp_threshold_pct)
            target = float(sig.pre_tp_trigger_price)
            threshold_source = "stamped"
        else:
            if indicators is not None:
                raw_atr = indicators.get("atr_last")
                try:
                    if raw_atr is not None:
                        atr_last = float(raw_atr)
                except (TypeError, ValueError):
                    atr_last = None
            threshold_pct, threshold_source = resolve_pre_tp_threshold(
                entry, atr_last
            )
            if is_long:
                target = entry * (1.0 + threshold_pct / 100.0)
            else:
                target = entry * (1.0 - threshold_pct / 100.0)
            # Backfill so subsequent ticks (and any persistence flush) see
            # the same trigger.  Cheap — eligibility was already enforced
            # above (PRE_TP_ENABLED + setup blacklist).
            sig.pre_tp_threshold_pct = round(threshold_pct, 4)
            sig.pre_tp_trigger_price = round(target, 8)

        # Threshold check — use the favourable extreme of the last 1m candle.
        if is_long:
            if c_high <= 0 or c_high < target:
                return False
        else:
            if c_low <= 0 or c_low > target:
                return False

        # Regime gate — only fire in non-trending regimes.  Fail-open if we
        # can't classify (per soft-penalty doctrine).
        regime_label: Optional[str] = None
        if self._regime_detector is not None and indicators is not None:
            try:
                result = self._regime_detector.classify(indicators)
                if result and getattr(result, "regime", None) is not None:
                    regime_label = result.regime.value
            except Exception as exc:
                log.debug("Pre-TP regime classify failed for %s: %s", sig.symbol, exc)
        if regime_label is not None and regime_label.upper() not in _resolved_regime_allowlist():
            return False

        # All gates passed — fire pre-TP at the resolved threshold
        favourable_pct = threshold_pct  # raw % move from entry to threshold

        # Resolve the grab fraction (OWNER_BRIEF B17, 2026-05-17 doctrine).
        # Engine-side TradeMonitor is owner-only auto-trade today; uses the
        # engine default from config.  Per-user execution (Phase 4, app-side
        # with user's own Binance keys) reads ``user_pretp_settings.grab_fraction``
        # directly — that wiring sits in the Lumin OrderExecutor, not here.
        grab_fraction = float(PRE_TP_GRAB_FRACTION)
        # Clamp into the B17 bounds defensively even though config validation
        # should already guarantee this.
        grab_fraction = max(0.30, min(1.00, grab_fraction))

        # Subscriber-facing math: show raw and net-of-fees at the assumed leverage.
        gross_pct = favourable_pct * PRE_TP_LEVERAGE
        fee_burn_pct = PRE_TP_FEE_PCT_ROUND_TRIP * PRE_TP_LEVERAGE
        net_pct = gross_pct - fee_burn_pct

        # Real partial close on the broker (OWNER_BRIEF §3.2a — capital
        # preservation requires REAL banked profit, not a SL-to-BE move
        # dressed up as a fill).  Records the partial via the same path TP1
        # partials use; the residual position keeps SL at entry so the
        # remaining (1 - grab_fraction) rides toward TP1 with floor at
        # breakeven.
        partial_executed = False
        if (
            self._order_manager is not None
            and getattr(self._order_manager, "is_enabled", False)
        ):
            try:
                # tp_level=0 distinguishes pre-TP partials from TP1/TP2/TP3
                # partials in the trade_records telemetry — same store, new
                # bucket.  The broker's close_partial is idempotent on
                # (signal_id, tp_level) so a duplicate-fire across the
                # 5s poll window is a no-op.
                fill = await self._order_manager.close_partial(
                    sig, grab_fraction, tp_level=0
                )
                if fill is not None:
                    partial_executed = True
            except Exception as exc:
                log.warning(
                    "Pre-TP partial close failed for %s (signal_id=%s, "
                    "fraction=%.2f): %s — falling back to SL→breakeven only",
                    sig.symbol, sig.signal_id, grab_fraction, exc,
                )

        # FSM path — server-side execution users whose positions were opened via
        # the signing service (not CCXT).  The CCXT close_partial above is a
        # no-op for them because _open_quantities is never populated by the FSM
        # entry path.  Includes LOT_SIZE rounding + MIN_NOTIONAL guard with
        # full-position fallback for small notionals (e.g. 10 USDT / FET where
        # 50% = $4.80 < $5 Binance floor — closes full position instead so the
        # pre-TP banking actually executes rather than silently failing).
        if not partial_executed:
            try:
                from src.execution import signal_dispatch as _sd
                direction_str = (
                    sig.direction.value
                    if hasattr(sig.direction, "value")
                    else str(sig.direction)
                )
                mark_price = self._latest_price(sig.symbol) or 0.0
                placed = await _sd.close_fsm_partial_for_signal(
                    sig.signal_id,
                    symbol=sig.symbol,
                    direction=direction_str,
                    fraction=grab_fraction,
                    mark_price=mark_price,
                )
                if placed > 0:
                    partial_executed = True
            except Exception as exc:
                log.warning(
                    "Pre-TP FSM partial close failed for %s (signal_id=%s): %s",
                    sig.symbol, sig.signal_id, exc,
                )

        # Full-close pre-TP: the engine closed 100% (PRE_TP_GRAB_FRACTION=1.0).
        # There is NO residual riding to TP1, so the signal must be finalized
        # below rather than left ACTIVE waiting for a TP1/BE-SL fill that can
        # never arrive (the orphan that showed signals ACTIVE forever).
        full_close = partial_executed and grab_fraction >= 1.0 - 1e-9

        sig.pre_tp_hit = True
        sig.pre_tp_pct = favourable_pct
        sig.pre_tp_timestamp = utcnow()
        if partial_executed:
            # Reflect the partial close on the signal so downstream telemetry
            # (signal_history, performance tracker) sees the realised
            # fraction.  ``partial_close_pct`` is also consumed by the TP1
            # partial path; pre-TP firing first means TP1 will close the
            # remaining (1 - grab_fraction) × 33% of the original size.
            sig.partial_close_pct = max(
                getattr(sig, "partial_close_pct", 0.0) or 0.0,
                grab_fraction,
            )
            if full_close:
                sig.execution_note += (
                    f" | Pre-TP closed 100% at +{favourable_pct:.2f}% raw — "
                    f"position fully banked"
                )
            else:
                sig.execution_note += (
                    f" | Pre-TP closed {grab_fraction*100:.0f}% at +{favourable_pct:.2f}% raw, "
                    f"residual SL→breakeven"
                )
        else:
            # Broker-disabled fallback — preserve the pre-2026-05-17 behaviour
            # (SL ratchet only) so signal-only subscribers still get the
            # protection, but with honest messaging that distinguishes
            # "trigger fired, no fill happened" from "banked + closed."
            #
            # Stamp ``partial_close_pct`` even on this path: the signal-level
            # ``pnl_pct`` blend in ``_set_realized_pnl`` is doctrine-true
            # (size-weighted blend of pre-TP-banked % and residual %), and
            # it short-circuits to residual-only when partial_close_pct == 0.
            # That short-circuit was reporting ~0.00% on signals that, per
            # doctrine, locked +0.15% (50% × +0.30% banked + 50% × 0% BE
            # exit on the residual).  The fee math sits below this layer
            # (trade_records.roi_pct_on_margin); pnl_pct represents the
            # gross blended move and must reflect what the doctrine actually
            # executed (SL→BE ratchet IS the residual exit modelled here).
            sig.partial_close_pct = max(
                getattr(sig, "partial_close_pct", 0.0) or 0.0,
                grab_fraction,
            )
            sig.execution_note += (
                f" | Pre-TP threshold hit at +{favourable_pct:.2f}% raw, "
                f"SL→breakeven (no broker partial)"
            )

        # Move SL to breakeven (entry) on the residual.  Ratchet only — never
        # widen.  Applies even when the broker partial failed, so the residual
        # protection holds regardless of execution path.
        if is_long:
            sig.stop_loss = max(sig.stop_loss, entry)
        else:
            sig.stop_loss = min(sig.stop_loss, entry)

        try:
            await self._post_pre_tp_alert(
                sig,
                favourable_pct,
                net_pct,
                partial_fraction=grab_fraction,
                partial_executed=partial_executed,
            )
        except Exception as exc:
            log.warning("Pre-TP active-channel post failed for %s: %s", sig.symbol, exc)

        # Free-channel storytelling — paid-tier only.  WATCHLIST tier was
        # removed in the app-era doctrine reset; every signal that reaches
        # trade_monitor is now paid (≥65 confidence).  Message reflects what
        # actually happened on the broker — no "banked" wording when nothing
        # was banked.
        try:
            from config import TELEGRAM_FREE_CHANNEL_ID
            if TELEGRAM_FREE_CHANNEL_ID:
                if partial_executed:
                    pct_closed = int(round(grab_fraction * 100))
                    pct_residual = 100 - pct_closed
                    realised_net = net_pct * grab_fraction
                    if full_close:
                        free_msg = (
                            f"⚡ *Quick Win — {_escape_md(sig.symbol)} {sig.direction.value}*\n\n"
                            f"Closed 100% at +{favourable_pct:.2f}% raw "
                            f"\\({net_pct:+.2f}% realised net @ {PRE_TP_LEVERAGE:.0f}x after fees\\)\n"
                            f"_Position fully banked._"
                        )
                    else:
                        free_msg = (
                            f"⚡ *Quick Win — {_escape_md(sig.symbol)} {sig.direction.value}*\n\n"
                            f"Closed {pct_closed}% at +{favourable_pct:.2f}% raw "
                            f"\\({realised_net:+.2f}% realised net @ {PRE_TP_LEVERAGE:.0f}x after fees\\)\n"
                            f"_{pct_residual}% rides to TP1 — SL at breakeven._"
                        )
                else:
                    free_msg = (
                        f"⚡ *Quick Move — {_escape_md(sig.symbol)} {sig.direction.value}*\n\n"
                        f"Hit +{favourable_pct:.2f}% raw "
                        f"\\({net_pct:+.2f}% net @ {PRE_TP_LEVERAGE:.0f}x if exited now\\)\n"
                        f"_SL moved to breakeven — auto-trader off, exit manually to bank._"
                    )
                await self._send(TELEGRAM_FREE_CHANNEL_ID, free_msg)
                log.info(
                    "free_channel_post source=pre_tp severity=HIGH symbol=%s",
                    sig.symbol,
                )
        except Exception as exc:
            log.warning("Pre-TP free-channel post failed for %s: %s", sig.symbol, exc)

        log.info(
            "pre_tp_fire %s %s [%s] threshold=%.3f source=%s atr_last=%s "
            "leverage=%.1fx net=%.2f age=%.0fs partial_executed=%s "
            "grab_fraction=%.2f",
            sig.symbol,
            sig.direction.value,
            setup_class,
            favourable_pct,
            threshold_source,
            f"{atr_last:.6f}" if atr_last is not None else "-",
            PRE_TP_LEVERAGE,
            net_pct,
            age_secs,
            partial_executed,
            grab_fraction,
        )

        # Finalize the engine-wide Signal when the pre-TP was a 100% close.
        # With no residual, no TP1/BE-SL fill will ever arrive, so without
        # this the Signal would sit ACTIVE forever (orphaned on the Signals
        # tab).  Mark realized PnL at the banked threshold, apply the terminal
        # outcome label, and drop it from the Open book.  The pre-TP alert +
        # free-channel post above are the close notification — we deliberately
        # do NOT call _post_signal_closed here to avoid a duplicate close post.
        # The caller (_process_signal) guards on ``sig.status != "ACTIVE"`` so
        # it won't run the SL/TP path against this now-flat position.
        if full_close:
            self._set_realized_pnl(sig, target)
            self._apply_final_outcome(sig, hit_tp=0, hit_sl=False)
            self._remove(sig.signal_id)

        return True

    async def _post_signal_closed(
        self,
        sig: Signal,
        is_tp: bool,
        tp_label: str = "TP",
        close_price: Optional[float] = None,
    ) -> None:
        """Generate and send an AI-written signal-closed post.

        Posts to the active (paid) channel and mirrors to the free channel as
        social-proof storytelling (Phase 5).  WATCHLIST tier was removed in
        the app-era doctrine reset; every signal that reaches here is paid
        (≥65 confidence).  SL hits get equal visibility per B3.

        Best-effort fire-and-forget — failures are logged but never raise.
        """
        if self.engine_context_fn is None:
            return
        try:
            from src import content_engine  # local import to avoid circular at module level
            from config import (
                TELEGRAM_ACTIVE_CHANNEL_ID,
                TELEGRAM_FREE_CHANNEL_ID,
                CONTENT_ENGINE_ENABLED,
            )
            if not CONTENT_ENGINE_ENABLED or not TELEGRAM_ACTIVE_CHANNEL_ID:
                return

            engine_ctx = self.engine_context_fn()
            hold_sec = (utcnow() - sig.timestamp).total_seconds() if hasattr(sig, "timestamp") and sig.timestamp else 0
            entry = sig.original_entry if hasattr(sig, "original_entry") and sig.original_entry else sig.entry
            actual_close = close_price if close_price is not None else sig.current_price

            # Calculate R multiple
            risk = abs(entry - sig.stop_loss)
            if is_tp and risk > 0:
                r_multiple = abs(actual_close - entry) / risk
            else:
                r_multiple = -1.0

            signal_data = {
                "symbol": sig.symbol,
                "direction": sig.direction.value,
                "entry_price": entry,
                "close_price": actual_close,
                "sl_price": sig.stop_loss,
                "tp_label": tp_label,
                "r_multiple": round(r_multiple, 2),
                "pnl_pct": round(sig.pnl_pct, 2),
                "setup_name": getattr(sig, "setup_class", ""),
                "hold_duration": f"{int(hold_sec // 60)}min",
            }

            text = await content_engine.generate_signal_closed_post(
                signal_data=signal_data,
                is_tp=is_tp,
                engine_context=engine_ctx,
            )
            if not text:
                return
            await self._send(TELEGRAM_ACTIVE_CHANNEL_ID, text)

            # Phase 5 — mirror paid-tier closes to free channel for social proof.
            if (
                TELEGRAM_FREE_CHANNEL_ID
                and TELEGRAM_FREE_CHANNEL_ID != TELEGRAM_ACTIVE_CHANNEL_ID
            ):
                header = (
                    "📣 *Paid Signal Result*\n"
                    "_Live trade just closed on the paid channel:_\n\n"
                )
                try:
                    await self._send(TELEGRAM_FREE_CHANNEL_ID, header + text)
                    log.info(
                        "free_channel_post source=signal_close severity=HIGH symbol=%s",
                        sig.symbol,
                    )
                except Exception as exc:
                    log.warning(
                        "Free-channel close mirror failed for %s: %s", sig.symbol, exc
                    )
        except Exception as exc:
            log.warning("Signal-closed post failed for %s: %s", sig.symbol, exc)
