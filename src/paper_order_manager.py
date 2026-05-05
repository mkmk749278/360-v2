"""Paper-trade order manager — simulates fills without real execution.

Phase A1 of the Lumin auto-trade rollout.  Provides the same interface as
:class:`src.order_manager.OrderManager` but executes nothing on the exchange.
Instead it tracks "as-if" positions in memory, simulates fills against the
latest 1m candle close, and logs structured ``paper_trade_fill`` markers
for truth-report attribution.

Why this exists
---------------
Going straight to ``AUTO_EXECUTION_MODE=live`` with real funds is reckless.
Going straight to a fully-built backtester is over-engineering before we
know auto-execution behaviour matches signal-monitor behaviour.  Paper mode
is the middle path: it runs against the live engine on real-time price
data, exercises every code path the live mode would, but produces zero
real-money risk and zero exchange API surface area.

Three uses
----------
1. **Own-testing of auto-trade**: flip ``AUTO_EXECUTION_MODE=paper`` on the
   VPS and run for 48h.  Compare paper-trade outcomes to engine signal
   closes — they should reconcile within fee/slippage tolerance.  Once
   they do we can flip to live with confidence.
2. **Demo mode in the Lumin app**: each user can toggle Live/Demo.  Demo
   uses paper mode under the hood so subscribers can validate strategy
   behaviour for themselves without risking capital.
3. **Free-tier feature** that drives Pro conversion: free subscribers get
   demo, paid subscribers get live.

Design
------
* Same public coroutine surface as :class:`OrderManager` so
   :class:`src.trade_monitor.TradeMonitor` can hold either type without
   conditional branches.
* Internal position state ``Dict[signal_id, _PaperPosition]`` survives the
   lifetime of the process; persistence is out of scope for v1 (paper-mode
   resets on restart, live-mode reconciles via Phase A3).
* Fill price = signal entry price for opens (matches the SCALP "market
   order at signal time" assumption).  Partial-close fill price = current
   1m close (passed through ``current_price`` argument when caller has it).
* Cumulative paper PnL exposed via ``simulated_pnl_total`` for the truth
   report and the Lumin app dashboard.

Out of scope (deferred to Phase A2/A3)
--------------------------------------
* Risk gates (daily loss kill, concurrent cap) — they apply equally to
  paper and live and live in a separate ``RiskManager``.
* Reconciliation with exchange state — paper has no exchange state.
* Persistence across restarts — paper sessions are intentionally
  ephemeral so each run starts with a clean balance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from config import MAX_POSITION_USD, POSITION_SIZE_PCT
from src.utils import get_logger

log = get_logger("paper_order_manager")

# Match the partial-TP fractions used by the live OrderManager so paper and
# live behave identically from TradeMonitor's perspective.
_TP_FRACTIONS: Dict[int, float] = {1: 0.33, 2: 0.33, 3: 0.34}


@dataclass
class _PaperPosition:
    """In-memory record of a simulated open position."""
    signal_id: str
    symbol: str
    side: str  # "long" or "short"
    entry: float
    quantity: float
    closed_quantity: float = 0.0
    realised_pnl_usd: float = 0.0
    closed_tp_levels: set = field(default_factory=set)


class PaperOrderManager:
    """Simulates exchange execution for the SCALP auto-trade pipeline.

    Implements the same coroutine surface as :class:`OrderManager` so
    :class:`src.trade_monitor.TradeMonitor` is agnostic to which backend
    is wired.  Returns synthetic order IDs (``paper-<signal_id>-<event>``)
    so consumers can still track per-signal execution state.
    """

    def __init__(
        self,
        *,
        position_size_pct: float = POSITION_SIZE_PCT,
        max_position_usd: float = MAX_POSITION_USD,
        starting_equity_usd: float = 1000.0,
        risk_manager: Optional[Any] = None,
    ) -> None:
        self._position_size_pct = position_size_pct
        self._max_position_usd = max_position_usd
        self._starting_equity = starting_equity_usd
        self._available_equity = starting_equity_usd
        self._positions: Dict[str, _PaperPosition] = {}
        # Cumulative realised PnL across the paper session.
        self._realised_pnl_total: float = 0.0
        # Counter for synthetic order IDs.
        self._order_seq: int = 0
        # Phase A2 — optional risk gates.  Same interface as OrderManager.
        # When wired, paper-mode obeys the same gates as live so we can
        # validate the gate chain in zero-risk mode before flipping live.
        self._risk_manager = risk_manager

    # ------------------------------------------------------------------
    # Compatibility surface (mirrors OrderManager)
    # ------------------------------------------------------------------

    @property
    def is_enabled(self) -> bool:
        """Always True in paper mode — the manager is "active" by definition."""
        return True

    @property
    def simulated_pnl_total(self) -> float:
        """Cumulative realised PnL (USD) across all closed paper trades."""
        return round(self._realised_pnl_total, 4)

    @property
    def open_position_count(self) -> int:
        return sum(
            1
            for p in self._positions.values()
            if (p.quantity - p.closed_quantity) > 0
        )

    def _next_order_id(self, signal_id: str, event: str) -> str:
        self._order_seq += 1
        return f"paper-{signal_id}-{event}-{self._order_seq}"

    async def _compute_quantity(self, entry_price: float) -> float:
        """Compute position size from configured percentage of paper equity."""
        if entry_price <= 0:
            return self._max_position_usd / max(entry_price, 1e-12)
        position_usd = min(
            self._available_equity * (self._position_size_pct / 100.0),
            self._max_position_usd,
        )
        return position_usd / entry_price

    async def place_market_order(
        self,
        signal: Any,
        *,
        quantity: Optional[float] = None,
    ) -> Optional[str]:
        """Simulate a market-order open at ``signal.entry``.

        Returns a synthetic order ID.  Records the open position in memory
        and emits a parseable ``paper_trade_fill`` log marker.
        """
        signal_id = getattr(signal, "signal_id", "")
        if not signal_id:
            log.debug("PaperOrderManager: missing signal_id, skipping")
            return None
        if signal_id in self._positions:
            # Idempotent — already opened.
            return None

        # Phase A2 — risk gates.  When wired, check before opening.
        if self._risk_manager is not None:
            gate = self._risk_manager.check(signal)
            if not gate.allowed:
                # Marker emitted by RiskManager; nothing more to do here.
                return None

        direction = getattr(signal.direction, "value", str(signal.direction))
        side = "long" if direction == "LONG" else "short"
        entry = float(getattr(signal, "entry", 0.0) or 0.0)
        if entry <= 0:
            log.debug(
                "PaperOrderManager: invalid entry price for %s — skipping",
                signal_id,
            )
            return None

        if quantity is None:
            quantity = await self._compute_quantity(entry)

        notional = entry * quantity
        order_id = self._next_order_id(signal_id, "open")
        self._positions[signal_id] = _PaperPosition(
            signal_id=signal_id,
            symbol=getattr(signal, "symbol", "?"),
            side=side,
            entry=entry,
            quantity=quantity,
        )
        # Margin reservation — naive: subtract notional from available.
        # Sufficient for paper-mode P&L tracking; not a real margin model.
        self._available_equity -= notional
        if self._risk_manager is not None:
            self._risk_manager.register_open(signal)

        log.info(
            "paper_trade_fill event=open signal_id=%s symbol=%s side=%s "
            "entry=%.6f qty=%.6f notional=%.2f order_id=%s",
            signal_id, self._positions[signal_id].symbol,
            side, entry, quantity, notional, order_id,
        )
        return order_id

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """No-op in paper mode (no real orders to cancel).

        Returns True so callers don't treat the absence of a cancel as a
        real failure.
        """
        log.debug(
            "paper_trade_fill event=cancel order_id=%s symbol=%s (no-op)",
            order_id, symbol,
        )
        return True

    async def close_partial(
        self,
        signal: Any,
        fraction: float,
        tp_level: int = 0,
        *,
        current_price: Optional[float] = None,
    ) -> Optional[str]:
        """Simulate a partial close at ``current_price`` (or signal.entry as fallback).

        TradeMonitor passes ``tp_level`` for TP1/TP2/TP3 partials.  Each TP
        level can only fire once per signal — matching the live
        OrderManager guard.  Realised PnL is added to the running total.
        """
        signal_id = getattr(signal, "signal_id", "")
        position = self._positions.get(signal_id)
        if position is None:
            log.debug(
                "paper_trade_fill close_partial: no open position for %s",
                signal_id,
            )
            return None

        if tp_level > 0:
            if tp_level in position.closed_tp_levels:
                # Idempotent — already closed at this TP level.
                return None
            position.closed_tp_levels.add(tp_level)

        close_qty = position.quantity * fraction
        # Cap at remaining open quantity to avoid double-close edge cases.
        close_qty = min(close_qty, position.quantity - position.closed_quantity)
        if close_qty <= 0:
            return None

        # Fill price preference: caller-provided current_price → signal.current_price
        # → signal.entry as last resort.  Partial close PnL on a market order
        # is the realised price minus entry (long) or entry minus realised
        # (short), times quantity.
        fill_price = (
            current_price
            if current_price is not None and current_price > 0
            else float(getattr(signal, "current_price", 0.0) or 0.0)
            or position.entry
        )
        pnl = (
            (fill_price - position.entry) * close_qty
            if position.side == "long"
            else (position.entry - fill_price) * close_qty
        )

        position.closed_quantity += close_qty
        position.realised_pnl_usd += pnl
        self._realised_pnl_total += pnl
        # Free up margin proportional to closed quantity.
        self._available_equity += position.entry * close_qty + pnl

        order_id = self._next_order_id(signal_id, f"tp{tp_level}")
        log.info(
            "paper_trade_fill event=partial_close signal_id=%s symbol=%s "
            "tp_level=%d fraction=%.2f qty=%.6f fill=%.6f pnl=%+.4f "
            "session_pnl=%+.4f order_id=%s",
            signal_id, position.symbol, tp_level, fraction, close_qty,
            fill_price, pnl, self._realised_pnl_total, order_id,
        )

        # If position fully closed, drop it from the active map so balance
        # accounting stays clean and notify the risk manager.
        if (position.quantity - position.closed_quantity) <= 1e-9:
            self._positions.pop(signal_id, None)
            if self._risk_manager is not None:
                self._risk_manager.register_close(
                    signal, realised_pnl_usd=position.realised_pnl_usd
                )

        return order_id

    async def execute_signal(self, signal: Any) -> Optional[str]:
        """Simulate market-order execution for *signal*.

        Mirrors :meth:`OrderManager.execute_signal` — wraps
        :meth:`place_market_order` for callers that don't care about the
        underlying coroutine choice.
        """
        return await self.place_market_order(signal)

    # ------------------------------------------------------------------
    # DCA Entry-2 (Phase A4 — auto-trade alignment with engine DCA)
    # ------------------------------------------------------------------

    async def add_dca_entry(
        self,
        signal: Any,
        *,
        current_price: Optional[float] = None,
    ) -> Optional[str]:
        """Add the 2nd entry of a DCA-enabled signal to the simulated book.

        Reads ``signal.entry_2`` and ``signal.position_weight_1/2`` —
        already populated by :func:`src.dca.recalculate_after_dca` —
        and adds simulated qty so the resulting weighted avg-entry
        matches the engine's ``avg_entry`` (= ``sig.entry`` after
        recalculate).

        Algorithm
        ---------
        ``additional_qty = existing_qty × (weight_2 / weight_1)``
        ``new_avg = (existing_qty × old_entry + additional_qty × dca_price)
                    / (existing_qty + additional_qty)``

        Idempotent — if no existing position (Entry 1 was refused by the
        risk gate, or the signal hasn't been opened yet), this is a
        no-op that surfaces a warning so admins can see the engine ↔
        broker mismatch.  Failures of the risk gate at DCA time also
        surface as warnings (engine math will assume the DCA fired even
        though the broker won't reflect it — owner's call to either
        accept the divergence or pause auto-trade).
        """
        signal_id = getattr(signal, "signal_id", "")
        position = self._positions.get(signal_id)
        if position is None:
            log.warning(
                "paper_trade_fill add_dca_entry: no open position for %s "
                "(Entry 1 was refused by risk gate or never opened); "
                "engine will treat DCA as filled but broker has no Entry 2",
                signal_id,
            )
            return None

        if self._risk_manager is not None:
            gate = self._risk_manager.check(signal)
            if not gate.allowed:
                log.warning(
                    "paper_trade_fill add_dca_entry: blocked by risk gate "
                    "(%s) for %s — engine assumes DCA filled, broker won't",
                    gate.reason or "unknown", signal_id,
                )
                return None

        # Note: explicit None-fallback rather than ``or`` so a legitimate
        # weight of 0.0 (caller bug) propagates and trips the guard below.
        _w1 = getattr(signal, "position_weight_1", None)
        _w2 = getattr(signal, "position_weight_2", None)
        weight_1 = float(_w1) if _w1 is not None else 0.6
        weight_2 = float(_w2) if _w2 is not None else 0.4
        if weight_1 <= 0:
            log.warning(
                "paper_trade_fill add_dca_entry: invalid weight_1=%.4f for %s",
                weight_1, signal_id,
            )
            return None

        dca_price = float(getattr(signal, "entry_2", 0.0) or 0.0)
        if dca_price <= 0:
            # Fallback to caller-provided price (for callers that haven't
            # gone through recalculate_after_dca yet).
            dca_price = float(current_price or 0.0)
        if dca_price <= 0:
            log.warning(
                "paper_trade_fill add_dca_entry: no dca_price for %s",
                signal_id,
            )
            return None

        additional_qty = position.quantity * (weight_2 / weight_1)
        if additional_qty <= 0:
            return None

        # Update the in-memory position so the weighted avg matches the
        # engine's avg_entry.  Subsequent close_partial / close_full
        # round-trips against the new avg.
        old_entry = position.entry
        old_qty = position.quantity
        new_qty = old_qty + additional_qty
        new_avg_entry = (
            (old_entry * old_qty + dca_price * additional_qty) / new_qty
        )
        position.entry = new_avg_entry
        position.quantity = new_qty

        # Margin reservation for the additional size.
        self._available_equity -= dca_price * additional_qty

        order_id = self._next_order_id(signal_id, "dca")
        log.info(
            "paper_trade_fill event=dca_entry signal_id=%s symbol=%s "
            "existing_qty=%.6f additional_qty=%.6f dca_price=%.6f "
            "new_avg_entry=%.6f new_total_qty=%.6f order_id=%s",
            signal_id, position.symbol, old_qty, additional_qty,
            dca_price, new_avg_entry, new_qty, order_id,
        )
        return order_id

    # ------------------------------------------------------------------
    # Full close (non-TP exits — invalidation / expiry / SL / cancel)
    # ------------------------------------------------------------------

    async def close_full(
        self,
        signal: Any,
        *,
        reason: str,
        current_price: Optional[float] = None,
    ) -> Optional[str]:
        """Close any remaining position for *signal*, booking realised PnL.

        Called by :class:`~src.trade_monitor.TradeMonitor` whenever a
        non-TP close path fires (SL hit, INVALIDATED, EXPIRED,
        CANCELLED).  Without this, the broker leaves the position open
        after the engine has stopped tracking it — a B12 safety hole.

        Idempotent: re-calling on a signal whose position has already
        been closed (e.g. by TP3 partial closes) returns ``None``
        silently so callers don't have to coordinate state.

        ``reason`` is logged as part of the structured marker for
        truth-report attribution.
        """
        signal_id = getattr(signal, "signal_id", "")
        position = self._positions.get(signal_id)
        if position is None:
            # Already closed (e.g. via TP3) or never opened.  No-op.
            return None

        remaining_qty = position.quantity - position.closed_quantity
        if remaining_qty <= 1e-9:
            self._positions.pop(signal_id, None)
            return None

        # Fill price preference: caller-provided → signal.current_price →
        # signal.stop_loss (for SL fills) → position.entry as last resort.
        fill_price = (
            current_price
            if current_price is not None and current_price > 0
            else float(getattr(signal, "current_price", 0.0) or 0.0)
            or float(getattr(signal, "stop_loss", 0.0) or 0.0)
            or position.entry
        )
        pnl = (
            (fill_price - position.entry) * remaining_qty
            if position.side == "long"
            else (position.entry - fill_price) * remaining_qty
        )

        position.closed_quantity += remaining_qty
        position.realised_pnl_usd += pnl
        self._realised_pnl_total += pnl
        self._available_equity += position.entry * remaining_qty + pnl

        order_id = self._next_order_id(signal_id, f"close_{reason}")
        log.info(
            "paper_trade_fill event=close_full signal_id=%s symbol=%s "
            "reason=%s qty=%.6f fill=%.6f pnl=%+.4f session_pnl=%+.4f "
            "order_id=%s",
            signal_id, position.symbol, reason, remaining_qty, fill_price,
            pnl, self._realised_pnl_total, order_id,
        )

        # Drop the position and notify the risk manager so concurrent-cap
        # accounting reclaims the slot.
        self._positions.pop(signal_id, None)
        if self._risk_manager is not None:
            self._risk_manager.register_close(
                signal, realised_pnl_usd=position.realised_pnl_usd
            )
        return order_id
