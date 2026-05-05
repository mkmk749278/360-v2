"""Order manager – SCALP market-order execution (V3).

This module provides the :class:`OrderManager` interface for direct exchange
execution scoped to SCALP strategies only.

When ``AUTO_EXECUTION_ENABLED=true`` and a real :class:`~src.exchange_client.CCXTClient`
is passed, the manager executes market orders directly on the exchange using CCXT.

The stubs log the intent and return ``None`` when the CCXT client is absent.
The calling code in :class:`src.trade_monitor.TradeMonitor` does not need to change.

Design notes
------------
* Market orders are used exclusively — SCALP strategies require immediate fill
  certainty over maker-fee optimisation.
* Auto-execution is **off by default** (``AUTO_EXECUTION_ENABLED=false``).
  The engine still publishes to Telegram as normal; the order stubs simply
  no-op until the feature flag is enabled.
* Position sizing: ``POSITION_SIZE_PCT`` (default 2%) of available USDT balance,
  capped at ``MAX_POSITION_USD`` (default $100).
* Partial take-profit: ``close_partial()`` sells a fraction of the open
  position at each TP level (TP1: 33%, TP2: 33%, TP3: 34%).
* Risk gates (Phase A2): when a :class:`RiskManager` is wired in,
  ``place_market_order`` consults ``risk_manager.check()`` before placing
  any order.  Blocked signals emit a ``risk_gate_block`` log marker and
  return ``None``.  Both paper and live modes share the same gate chain.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from config import MAX_POSITION_USD, POSITION_SIZE_PCT
from src.utils import get_logger

log = get_logger("order_manager")

# Partial TP fractions (must sum to 1.0)
_TP_FRACTIONS: Dict[int, float] = {1: 0.33, 2: 0.33, 3: 0.34}


def _symbol_to_ccxt(symbol: str) -> str:
    """Convert Binance-style symbol (BTCUSDT) to CCXT format (BTC/USDT)."""
    for quote in ("USDT", "BTC", "ETH", "BNB", "BUSD"):
        if symbol.upper().endswith(quote):
            base = symbol.upper()[: -len(quote)]
            return f"{base}/{quote}"
    return symbol


class OrderManager:
    """Manages direct exchange order placement for SCALP strategies.

    Parameters
    ----------
    auto_execution_enabled:
        Master toggle.  When ``False`` all methods are no-ops; signals are
        still routed to Telegram as usual.
    exchange_client:
        A :class:`~src.exchange_client.CCXTClient` instance (or any object with
        ``create_market_order``, ``cancel_order``, and ``fetch_balance``
        coroutines).  Pass ``None`` until the real client is available.
    position_size_pct:
        Percentage of available balance to risk per trade (default 2.0).
    max_position_usd:
        Hard cap on position size in USD (default 100.0).
    """

    def __init__(
        self,
        auto_execution_enabled: bool = False,
        exchange_client: Optional[Any] = None,
        position_size_pct: float = POSITION_SIZE_PCT,
        max_position_usd: float = MAX_POSITION_USD,
        risk_manager: Optional[Any] = None,
    ) -> None:
        self._enabled = auto_execution_enabled
        self._client = exchange_client
        self._position_size_pct = position_size_pct
        self._max_position_usd = max_position_usd
        # Optional RiskManager (Phase A2).  When None, no gates are applied —
        # callers building OrderManager without risk gates get the legacy
        # behaviour for backwards compatibility.  Production wiring should
        # always pass a configured RiskManager.
        self._risk_manager = risk_manager
        # Track open position sizes for partial TP execution: signal_id → quantity
        self._open_quantities: Dict[str, float] = {}
        # Track which TP levels have had partial closes executed to prevent
        # duplicate closes if price oscillates around a TP level.
        # Maps signal_id → set of TP level numbers already closed (1, 2, 3).
        self._partial_closed_tps: Dict[str, set] = {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def is_enabled(self) -> bool:
        """Return ``True`` when auto-execution is active."""
        return self._enabled

    async def _compute_quantity(self, entry_price: float) -> float:
        """Compute order quantity based on available balance and position sizing.

        Uses ``POSITION_SIZE_PCT`` of free USDT balance, capped at
        ``MAX_POSITION_USD``.  Falls back to ``MAX_POSITION_USD / entry_price``
        when balance fetch fails.
        """
        if self._client is None or entry_price <= 0:
            return self._max_position_usd / max(entry_price, 1e-12)

        try:
            balance = await self._client.fetch_balance()
            free_usdt = float(
                (balance.get("USDT") or balance.get("usdt") or {}).get("free", 0.0)
            )
            position_usd = min(
                free_usdt * self._position_size_pct / 100.0,
                self._max_position_usd,
            )
        except Exception as exc:
            log.warning("Balance fetch failed, using MAX_POSITION_USD: %s", exc)
            position_usd = self._max_position_usd

        return position_usd / entry_price

    async def place_market_order(
        self,
        signal: Any,
        *,
        quantity: Optional[float] = None,
    ) -> Optional[str]:
        """Place a market (taker) order on the exchange.

        All SCALP strategies use market orders for immediate fill certainty.

        Parameters
        ----------
        signal:
            The :class:`src.channels.base.Signal` driving the order.
        quantity:
            Order size in base currency.

        Returns
        -------
        str or None
            Exchange order-ID on success; ``None`` when disabled / stub.
        """
        if not self._enabled:
            return None

        # Phase A2 — risk gates.  When wired, check before placing.
        if self._risk_manager is not None:
            gate = self._risk_manager.check(signal)
            if not gate.allowed:
                # RiskManager already emitted the structured marker; we just
                # short-circuit the placement.
                return None

        direction = getattr(signal.direction, "value", str(signal.direction))
        side = "buy" if direction == "LONG" else "sell"

        if quantity is None:
            quantity = await self._compute_quantity(signal.entry)

        if self._client is not None:
            try:
                ccxt_symbol = _symbol_to_ccxt(signal.symbol)
                order = await self._client.create_market_order(
                    ccxt_symbol, side, quantity
                )
                order_id = str(order.get("id", ""))
                self._open_quantities[signal.signal_id] = quantity
                if self._risk_manager is not None:
                    self._risk_manager.register_open(signal)
                log.info(
                    "[OrderManager] market order placed: %s %s %s qty=%s id=%s",
                    signal.symbol, signal.channel, side, quantity, order_id,
                )
                return order_id
            except Exception as exc:
                log.error(
                    "[OrderManager] market order failed for %s: %s",
                    signal.symbol, exc,
                )
                return None

        log.info(
            "[OrderManager] STUB place_market_order: {} {} {} (qty={})",
            signal.symbol,
            signal.channel,
            side,
            quantity,
        )
        return None

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an open exchange order.

        Parameters
        ----------
        order_id:
            The exchange-assigned order identifier returned by
            :meth:`place_market_order`.
        symbol:
            Trading-pair symbol (e.g. ``"BTCUSDT"``).

        Returns
        -------
        bool
            ``True`` when the cancellation was confirmed; ``False`` when
            execution is disabled or the operation failed.
        """
        if not self._enabled:
            return False

        if self._client is not None:
            try:
                ccxt_symbol = _symbol_to_ccxt(symbol)
                result = await self._client.cancel_order(order_id, ccxt_symbol)
                cancelled = result.get("status") == "canceled"
                log.info(
                    "[OrderManager] cancel_order: id=%s symbol=%s status=%s",
                    order_id, symbol, result.get("status"),
                )
                return cancelled
            except Exception as exc:
                log.error(
                    "[OrderManager] cancel_order failed for %s id=%s: %s",
                    symbol, order_id, exc,
                )
                return False

        log.info(
            "[OrderManager] STUB cancel_order: order_id={} symbol={}",
            order_id,
            symbol,
        )
        return False

    async def close_partial(
        self,
        signal: Any,
        fraction: float,
        tp_level: int = 0,
    ) -> Optional[str]:
        """Close a fraction of an open position (partial take-profit execution).

        Called by :class:`~src.trade_monitor.TradeMonitor` on TP1/TP2/TP3 hits:

        * TP1: ``fraction=0.33, tp_level=1``
        * TP2: ``fraction=0.33, tp_level=2``
        * TP3: ``fraction=0.34, tp_level=3``

        Each TP level can only be closed once per signal.  If price oscillates
        around a TP level, subsequent calls with the same *tp_level* are
        no-ops to prevent closing more than the original position.

        Parameters
        ----------
        signal:
            The active :class:`~src.channels.base.Signal`.
        fraction:
            Fraction of the **original** position size to close (0.0–1.0).
        tp_level:
            TP level number (1, 2, or 3). When non-zero, used to guard against
            duplicate partial closes at the same TP level.

        Returns
        -------
        str or None
            Exchange order-ID on success; ``None`` when disabled or stub.
        """
        if not self._enabled:
            return None

        # Guard against duplicate partial closes at the same TP level
        if tp_level > 0:
            closed_tps = self._partial_closed_tps.setdefault(signal.signal_id, set())
            if tp_level in closed_tps:
                log.debug(
                    "[OrderManager] close_partial: TP%d already closed for %s — skipping",
                    tp_level, signal.signal_id,
                )
                return None
            closed_tps.add(tp_level)

        original_qty = self._open_quantities.get(signal.signal_id, 0.0)
        if original_qty <= 0:
            log.debug(
                "[OrderManager] close_partial: no tracked quantity for %s",
                signal.signal_id,
            )
            return None

        close_qty = original_qty * fraction
        direction = getattr(signal.direction, "value", str(signal.direction))
        # To close a LONG we sell; to close a SHORT we buy.
        side = "sell" if direction == "LONG" else "buy"

        if self._client is not None:
            try:
                ccxt_symbol = _symbol_to_ccxt(signal.symbol)
                order = await self._client.create_market_order(
                    ccxt_symbol, side, close_qty
                )
                order_id = str(order.get("id", ""))
                log.info(
                    "[OrderManager] partial close TP%d: %s %s %.2f%% of original qty=%.6f id=%s",
                    tp_level, signal.symbol, side, fraction * 100,
                    close_qty, order_id,
                )
                return order_id
            except Exception as exc:
                log.error(
                    "[OrderManager] close_partial failed for %s: %s",
                    signal.symbol, exc,
                )
                return None

        log.info(
            "[OrderManager] STUB close_partial TP{}: {} {} {}% (qty={})",
            tp_level, signal.symbol, side, fraction * 100, close_qty,
        )
        return None

    async def execute_signal(self, signal: Any) -> Optional[str]:
        """Execute a market order for *signal*.

        All SCALP signals use market orders for immediate fill certainty.

        Parameters
        ----------
        signal:
            The :class:`src.channels.base.Signal` to execute.

        Returns
        -------
        str or None
            Exchange order-ID, or ``None`` when disabled / stub.
        """
        if not self._enabled:
            return None

        return await self.place_market_order(signal)

    # ------------------------------------------------------------------
    # DCA Entry-2 (auto-trade alignment with engine DCA path)
    # ------------------------------------------------------------------

    async def add_dca_entry(
        self,
        signal: Any,
        *,
        current_price: Optional[float] = None,
    ) -> Optional[str]:
        """Place the 2nd entry of a DCA-enabled signal at the broker.

        Reads ``signal.entry_2`` and ``signal.position_weight_1/2`` —
        already populated by :func:`src.dca.recalculate_after_dca` —
        and places an additional market order on the same side as
        Entry 1 so the resulting position's weighted average price
        matches the engine's ``avg_entry``.

        Algorithm
        ---------
        ``additional_qty = existing_qty × (weight_2 / weight_1)``

        Both the open-tracking quantity and the partial-TP guard map
        are updated to reflect the larger position.  Subsequent
        ``close_partial`` / ``close_full`` calls round-trip against
        the new total.

        Idempotency
        -----------
        If no Entry-1 quantity is tracked (open was refused by the risk
        gate, or the signal hasn't been opened yet), this is a no-op
        that surfaces a warning so admins see the engine ↔ broker drift.
        Callers must NOT retry on failure — engine state has already
        moved past DCA-not-fired and a retry would double-stamp.
        """
        if not self._enabled:
            return None

        signal_id = getattr(signal, "signal_id", "")
        existing_qty = self._open_quantities.get(signal_id, 0.0)
        if existing_qty <= 0:
            log.warning(
                "[OrderManager] add_dca_entry: no Entry-1 qty tracked for "
                "%s (open refused or never placed) — broker has no Entry 2",
                signal_id,
            )
            return None

        if self._risk_manager is not None:
            gate = self._risk_manager.check(signal)
            if not gate.allowed:
                log.warning(
                    "[OrderManager] add_dca_entry: blocked by risk gate "
                    "(%s) for %s — broker has no Entry 2 even though "
                    "engine math assumes DCA filled",
                    gate.reason or "unknown", signal_id,
                )
                return None

        _w1 = getattr(signal, "position_weight_1", None)
        _w2 = getattr(signal, "position_weight_2", None)
        weight_1 = float(_w1) if _w1 is not None else 0.6
        weight_2 = float(_w2) if _w2 is not None else 0.4
        if weight_1 <= 0:
            log.warning(
                "[OrderManager] add_dca_entry: invalid weight_1=%.4f for %s",
                weight_1, signal_id,
            )
            return None

        additional_qty = existing_qty * (weight_2 / weight_1)
        if additional_qty <= 0:
            return None

        direction = getattr(signal.direction, "value", str(signal.direction))
        side = "buy" if direction == "LONG" else "sell"

        if self._client is not None:
            try:
                ccxt_symbol = _symbol_to_ccxt(signal.symbol)
                order = await self._client.create_market_order(
                    ccxt_symbol, side, additional_qty
                )
                order_id = str(order.get("id", ""))
                self._open_quantities[signal_id] = existing_qty + additional_qty
                log.info(
                    "[OrderManager] DCA Entry 2: %s %s qty=%.6f "
                    "(weight_2/weight_1=%.3f × existing) id=%s",
                    signal.symbol, side, additional_qty,
                    weight_2 / weight_1, order_id,
                )
                return order_id
            except Exception as exc:
                log.error(
                    "[OrderManager] add_dca_entry failed for %s: %s",
                    signal.symbol, exc,
                )
                return None

        log.info(
            "[OrderManager] STUB add_dca_entry: {} {} qty={}",
            signal.symbol, side, additional_qty,
        )
        return None

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
        """Close any remaining position for *signal* on the exchange.

        Called by :class:`~src.trade_monitor.TradeMonitor` whenever a
        non-TP close path fires (SL hit, INVALIDATED, EXPIRED,
        CANCELLED).  Without this, the broker leaves the position open
        after the engine has stopped tracking it — a B12 safety hole.

        Idempotent: re-calling on a signal whose tracked qty is zero
        (e.g. after TP3 closed everything) returns ``None`` silently.

        ``reason`` is logged as part of the audit marker so the truth
        report can attribute closes by cause.
        """
        if not self._enabled:
            return None

        signal_id = getattr(signal, "signal_id", "")
        original_qty = self._open_quantities.get(signal_id, 0.0)
        if original_qty <= 0:
            return None

        # Sum closed-fraction across recorded partial closes.  TP fractions
        # are 0.33 / 0.33 / 0.34; if all three fired the remaining is ~0.
        closed_tps = self._partial_closed_tps.get(signal_id, set())
        closed_fraction = sum(
            _TP_FRACTIONS.get(tp, 0.0) for tp in closed_tps
        )
        remaining_fraction = max(0.0, 1.0 - closed_fraction)
        remaining_qty = original_qty * remaining_fraction
        if remaining_qty <= 1e-9:
            # Nothing left — drop tracking and exit.
            self._open_quantities.pop(signal_id, None)
            self._partial_closed_tps.pop(signal_id, None)
            return None

        direction = getattr(signal.direction, "value", str(signal.direction))
        # To close a LONG we sell; to close a SHORT we buy.
        side = "sell" if direction == "LONG" else "buy"

        if self._client is not None:
            try:
                ccxt_symbol = _symbol_to_ccxt(signal.symbol)
                order = await self._client.create_market_order(
                    ccxt_symbol, side, remaining_qty
                )
                order_id = str(order.get("id", ""))
                log.info(
                    "[OrderManager] close_full reason=%s: %s %s qty=%.6f id=%s",
                    reason, signal.symbol, side, remaining_qty, order_id,
                )
                # Drop tracking — subsequent calls are no-ops.
                self._open_quantities.pop(signal_id, None)
                self._partial_closed_tps.pop(signal_id, None)
                if self._risk_manager is not None:
                    pnl_estimate = (
                        float(getattr(signal, "pnl_pct", 0.0) or 0.0)
                        * 0.01
                        * float(getattr(signal, "entry", 0.0) or 0.0)
                        * remaining_qty
                    )
                    self._risk_manager.register_close(
                        signal, realised_pnl_usd=pnl_estimate
                    )
                return order_id
            except Exception as exc:
                log.error(
                    "[OrderManager] close_full failed for %s (reason=%s): %s",
                    signal.symbol, reason, exc,
                )
                return None

        log.info(
            "[OrderManager] STUB close_full reason={}: {} {} qty={}",
            reason, signal.symbol, side, remaining_qty,
        )
        return None
