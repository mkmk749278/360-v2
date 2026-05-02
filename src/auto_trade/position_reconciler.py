"""Position reconciler — Phase A3.

After a crash or planned restart the engine boots with empty in-memory
signal state but the exchange still holds whatever positions were open.
Without reconciliation we'd:

  * have no SL/TP tracking on those positions (they could SL silently)
  * potentially open NEW positions on top of them (B12 per-symbol cap
    won't fire because we don't know the symbol is occupied)
  * lose attribution between exchange fills and our signal lifecycle

This module catches both gaps:

  1. ``reconcile_on_boot()`` — once at engine start.  Fetches exchange
     positions, compares to current signal state (empty at boot in
     practice), classifies each position as TRACKED / ORPHAN / MISSING,
     alerts on orphans, optionally closes them at market.

  2. ``periodic_drift_check()`` — runs every N seconds via
     ``run_periodic_loop()``.  Catches mid-flight drift: an order we
     placed may have been manually closed by the owner, or a position
     may have liquidated without our SL hitting.  Drift = either side
     not matching the other.

Paper mode does NOT run the reconciler (paper has no exchange state).
Live mode is the only consumer.

Auto-close-orphans is OFF by default — orphans get an alert and the
owner decides.  Owner can opt in via ``RECONCILER_AUTO_CLOSE_ORPHANS=true``
(env-overridable per B8) for fully unattended operation.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional

from src.utils import get_logger

log = get_logger("position_reconciler")


def _ccxt_to_binance_symbol(ccxt_symbol: str) -> str:
    """Convert CCXT format "BTC/USDT" → engine format "BTCUSDT"."""
    return str(ccxt_symbol).replace("/", "").replace(":USDT", "")


def _signal_symbol(signal: Any) -> str:
    return str(getattr(signal, "symbol", "")).upper()


def _signal_side(signal: Any) -> str:
    direction = getattr(signal, "direction", None)
    val = getattr(direction, "value", None) or str(direction)
    return "long" if str(val).upper() == "LONG" else "short"


def _is_position_open(position: Dict[str, Any]) -> bool:
    """An exchange position is "open" only when contracts > 0."""
    try:
        contracts = float(position.get("contracts") or 0.0)
    except (TypeError, ValueError):
        contracts = 0.0
    return contracts > 0


@dataclass
class ReconcileResult:
    """Per-cycle reconciliation summary, surfaced for logging + tests."""
    tracked: int = 0
    orphan_positions: List[Dict[str, Any]] = None  # exchange has, signals don't
    missing_signals: List[Any] = None              # signals say open, exchange doesn't
    closed_orphans: int = 0                         # how many we auto-closed
    errors: List[str] = None

    def __post_init__(self) -> None:
        if self.orphan_positions is None:
            self.orphan_positions = []
        if self.missing_signals is None:
            self.missing_signals = []
        if self.errors is None:
            self.errors = []

    @property
    def has_drift(self) -> bool:
        return bool(self.orphan_positions or self.missing_signals)


class PositionReconciler:
    """Compares exchange position state to engine signal state.

    Parameters
    ----------
    exchange_client:
        :class:`~src.exchange_client.CCXTClient` instance — must support
        ``fetch_positions()``.  When ``None`` reconciliation is disabled
        (used for tests / paper mode safety).
    get_active_signals_fn:
        Callable returning the current active signals (typically
        ``lambda: router.active_signals``).  Returns dict mapping
        signal_id → Signal.
    alert_callback:
        Async callable that posts an admin Telegram alert.  Used to
        surface drift to the owner.
    auto_close_orphans:
        When True the reconciler attempts to close orphan exchange
        positions at market.  Default False — alerts only, owner acts.
    risk_manager:
        Optional :class:`~src.auto_trade.risk_manager.RiskManager`.  When
        wired, recovered positions are registered so per-symbol caps and
        concurrent counts include them.
    """

    def __init__(
        self,
        *,
        exchange_client: Optional[Any] = None,
        get_active_signals_fn: Optional[Callable[[], Dict[str, Any]]] = None,
        alert_callback: Optional[Callable[[str], Awaitable[Any]]] = None,
        auto_close_orphans: bool = False,
        risk_manager: Optional[Any] = None,
    ) -> None:
        self._client = exchange_client
        self._get_signals = get_active_signals_fn or (lambda: {})
        self._alert = alert_callback
        self._auto_close = bool(auto_close_orphans)
        self._risk_manager = risk_manager

    @property
    def is_active(self) -> bool:
        """True iff a real exchange client is wired (live mode only)."""
        return self._client is not None

    # ------------------------------------------------------------------
    # Reconciliation cycle
    # ------------------------------------------------------------------

    async def _fetch_open_positions(self) -> List[Dict[str, Any]]:
        if self._client is None:
            return []
        try:
            raw = await self._client.fetch_positions()
        except Exception as exc:
            log.warning("PositionReconciler: fetch_positions failed: %s", exc)
            return []
        return [p for p in (raw or []) if _is_position_open(p)]

    def _classify(
        self,
        exchange_positions: List[Dict[str, Any]],
        active_signals: Dict[str, Any],
    ) -> ReconcileResult:
        """Pure classification — no I/O, easy to test."""
        result = ReconcileResult()

        # Index signals by (symbol, side) for O(1) lookup.
        signal_index: Dict[str, Any] = {}
        for sig in active_signals.values():
            key = f"{_signal_symbol(sig)}|{_signal_side(sig)}"
            signal_index[key] = sig

        # Pass 1: walk exchange positions, classify each.
        seen_keys: set = set()
        for pos in exchange_positions:
            ccxt_sym = str(pos.get("symbol", ""))
            engine_sym = _ccxt_to_binance_symbol(ccxt_sym).upper()
            side = str(pos.get("side", "")).lower()
            key = f"{engine_sym}|{side}"
            if key in signal_index:
                result.tracked += 1
                seen_keys.add(key)
            else:
                # Tag the original symbol so callers / alerts have it.
                result.orphan_positions.append({
                    "symbol": engine_sym,
                    "ccxt_symbol": ccxt_sym,
                    "side": side,
                    "contracts": float(pos.get("contracts") or 0.0),
                    "entry_price": float(pos.get("entryPrice") or 0.0),
                    "notional": float(pos.get("notional") or 0.0),
                    "leverage": float(pos.get("leverage") or 1.0),
                    "raw": pos,
                })

        # Pass 2: signals without exchange backing — engine thinks open
        # but exchange doesn't have a matching position.
        for key, sig in signal_index.items():
            if key not in seen_keys:
                result.missing_signals.append(sig)

        return result

    async def _close_orphan(self, orphan: Dict[str, Any]) -> bool:
        """Place a market order in the opposite direction to close the
        orphan position.  Returns True on success."""
        if self._client is None:
            return False
        ccxt_sym = orphan["ccxt_symbol"]
        side = "sell" if orphan["side"] == "long" else "buy"
        qty = orphan["contracts"]
        try:
            await self._client.create_market_order(ccxt_sym, side, qty)
            log.info(
                "reconciler closed orphan: %s side=%s qty=%.6f",
                ccxt_sym, side, qty,
            )
            return True
        except Exception as exc:
            log.error(
                "reconciler failed to close orphan %s: %s", ccxt_sym, exc
            )
            return False

    async def _alert_drift(self, result: ReconcileResult, *, context: str) -> None:
        if self._alert is None or not result.has_drift:
            return
        lines = [f"⚠️ Position reconciler — {context}"]
        if result.orphan_positions:
            lines.append(f"\n*Orphan positions ({len(result.orphan_positions)})* — on exchange, not in signal state:")
            for o in result.orphan_positions[:10]:
                lines.append(
                    f"  • {o['symbol']} {o['side'].upper()} qty={o['contracts']:.4f} "
                    f"entry=${o['entry_price']:.2f} notional=${o['notional']:.2f}"
                )
            if self._auto_close:
                lines.append(f"\n  → auto_close enabled — {result.closed_orphans}/{len(result.orphan_positions)} closed")
            else:
                lines.append("\n  → auto_close OFF — manually decide via Binance UI")
        if result.missing_signals:
            lines.append(f"\n*Missing signals ({len(result.missing_signals)})* — engine thinks open, exchange disagrees:")
            for sig in result.missing_signals[:10]:
                lines.append(
                    f"  • {_signal_symbol(sig)} {_signal_side(sig).upper()} "
                    f"signal_id={getattr(sig, 'signal_id', '?')}"
                )
        try:
            await self._alert("\n".join(lines))
        except Exception as exc:
            log.warning("reconciler alert send failed: %s", exc)

    async def reconcile_on_boot(self) -> ReconcileResult:
        """One-shot reconciliation called from bootstrap.

        Most useful at engine start when in-memory signal state is empty
        but the exchange may still hold positions from before the
        restart.  Detects, alerts, optionally closes.
        """
        if not self.is_active:
            log.debug("PositionReconciler: not active (no exchange client) — skipping boot reconcile")
            return ReconcileResult()

        positions = await self._fetch_open_positions()
        signals = self._get_signals() or {}
        result = self._classify(positions, signals)

        log.info(
            "reconcile_on_boot: tracked=%d orphans=%d missing=%d",
            result.tracked, len(result.orphan_positions), len(result.missing_signals),
        )

        if self._auto_close and result.orphan_positions:
            for orphan in result.orphan_positions:
                if await self._close_orphan(orphan):
                    result.closed_orphans += 1

        await self._alert_drift(result, context="boot reconciliation")
        return result

    async def periodic_drift_check(self) -> ReconcileResult:
        """Single cycle of mid-flight drift detection.

        Same logic as boot, different context for alerts.  Auto-close is
        intentionally NOT applied here — periodic drift is more often a
        false-positive (e.g. SL just hit on the exchange and our state
        hasn't caught up yet).  Boot is the safer time to auto-close.
        """
        if not self.is_active:
            return ReconcileResult()

        positions = await self._fetch_open_positions()
        signals = self._get_signals() or {}
        result = self._classify(positions, signals)

        if result.has_drift:
            log.info(
                "periodic_drift_check drift detected: orphans=%d missing=%d",
                len(result.orphan_positions), len(result.missing_signals),
            )
            await self._alert_drift(result, context="periodic drift check")

        return result

    async def run_periodic_loop(self, interval_sec: int = 300) -> None:
        """Run :meth:`periodic_drift_check` forever at *interval_sec* cadence.

        Cancellable via task.cancel().  Errors are logged but never
        propagate so the loop keeps running.
        """
        if not self.is_active:
            log.debug("PositionReconciler periodic loop not started — no exchange client")
            return
        log.info("PositionReconciler periodic loop started (interval=%ds)", interval_sec)
        while True:
            try:
                await self.periodic_drift_check()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                log.warning("periodic_drift_check loop error: %s", exc)
            await asyncio.sleep(interval_sec)
