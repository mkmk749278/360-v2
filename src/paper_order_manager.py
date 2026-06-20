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

import json
import math
import os
import types
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from config import (
    BINANCE_FUTURES_MAKER_FEE_PCT,
    BINANCE_FUTURES_TAKER_FEE_PCT,
    MAX_POSITION_USD,
    POSITION_SIZE_PCT,
)
from src.auto_trade import pnl_history, trade_records
from src.utils import get_logger


def _entry_fee(notional: float) -> float:
    """Taker-side fee on opening a market position."""
    return abs(notional) * (BINANCE_FUTURES_TAKER_FEE_PCT / 100.0)


def _tp_exit_fee(notional: float) -> float:
    """Maker-side fee — TP fills are limit orders that rest on the book."""
    return abs(notional) * (BINANCE_FUTURES_MAKER_FEE_PCT / 100.0)


def _sl_exit_fee(notional: float) -> float:
    """Taker-side fee — SL / invalidation / expiry exits use stop-market
    or market orders that cross the book."""
    return abs(notional) * (BINANCE_FUTURES_TAKER_FEE_PCT / 100.0)

log = get_logger("paper_order_manager")

# Match the partial-TP fractions used by the live OrderManager so paper and
# live behave identically from TradeMonitor's perspective.
_TP_FRACTIONS: Dict[int, float] = {1: 0.33, 2: 0.33, 3: 0.34}

# Minimum tradable notional in USD.  Below this the simulated fill is
# meaningless — owner reported (2026-05-16) seeing qty=0 trades in
# pnl_history because depleted equity + tiny position_size_pct yielded
# sub-cent notionals that round to nothing.  Set conservatively at $1
# notional ($0.10 of margin at 10x) so the guard rail trips well before
# the row becomes useless to a subscriber reading the dashboard.
_MIN_PAPER_NOTIONAL_USD: float = 1.0

# Cumulative paper-realised PnL persistence (2026-05-08).
#
# Doctrine: paper mode is the dashboard data source for free-tier
# subscribers — its "Today's P&L" / "Paper total since boot" surface only
# makes sense if the number SURVIVES engine restarts and mode switches.
# Pre-fix, the cumulative paper total reset to $0.00 on every redeploy
# and on every paper↔live toggle (RiskManager + PaperOrderManager are
# rebuilt by ``main.set_auto_execution_mode``), so the figure that drives
# the new ``_ModePnlCard`` (lumin v0.0.13) was effectively transient.
#
# Persistence is intentionally narrow: only the cumulative ``_realised_pnl_total``
# is written to disk.  Open positions stay ephemeral — TradeMonitor +
# signal-history persistence are the right layer for in-flight lifecycle
# state, not the paper broker.  On boot with persisted PnL, the broker
# initialises ``_available_equity = starting_equity + persisted_pnl`` so
# subsequent position sizing reflects the paper account's true balance.
_PAPER_PNL_PATH_DEFAULT = Path("data") / "paper_pnl_state.json"


def _resolve_paper_pnl_path(override: Optional[Path] = None) -> Path:
    """Resolve the on-disk ledger path.

    Priority: explicit ``override`` arg → ``PAPER_PNL_STATE_PATH`` env var
    → default ``data/paper_pnl_state.json``.  Resolved per call so test
    fixtures that monkeypatch the env var after module import still take
    effect (the autouse conftest fixture relies on this).
    """
    if override is not None:
        return override
    return Path(
        os.getenv("PAPER_PNL_STATE_PATH", str(_PAPER_PNL_PATH_DEFAULT))
    )


def _load_paper_pnl_state(path: Optional[Path] = None) -> float:
    """Load cumulative paper-realised PnL from disk.

    Fail-soft: returns 0.0 on any error (missing file, malformed JSON,
    permission denied).  A clean-slate paper session is the safe default.
    """
    resolved = _resolve_paper_pnl_path(path)
    try:
        with resolved.open("r") as fp:
            data = json.load(fp)
    except FileNotFoundError:
        return 0.0
    except (json.JSONDecodeError, OSError) as exc:
        log.warning(
            "Paper PnL ledger corrupt at %s — starting from $0.00 (%s)",
            resolved, exc,
        )
        return 0.0
    raw = data.get("realised_pnl_usd", 0.0) if isinstance(data, dict) else 0.0
    try:
        return float(raw)
    except (TypeError, ValueError):
        log.warning(
            "Paper PnL ledger value not numeric at %s (got %r) — resetting",
            resolved, raw,
        )
        return 0.0


def _persist_paper_pnl_state(
    realised_pnl_usd: float, path: Optional[Path] = None
) -> None:
    """Write cumulative paper-realised PnL to disk.

    Best-effort: any IO failure is logged at WARNING and swallowed —
    persistence is a UX nicety, not a safety-critical invariant, so a
    full disk should never break a paper close.
    """
    resolved = _resolve_paper_pnl_path(path)
    try:
        resolved.parent.mkdir(parents=True, exist_ok=True)
        tmp = resolved.with_suffix(resolved.suffix + ".tmp")
        with tmp.open("w") as fp:
            json.dump({"realised_pnl_usd": float(realised_pnl_usd)}, fp)
        tmp.replace(resolved)
    except OSError as exc:
        log.warning(
            "Paper PnL ledger persist failed at %s: %s — continuing in-memory",
            resolved, exc,
        )


def reset_paper_pnl_state(path: Optional[Path] = None) -> None:
    """Wipe the on-disk paper-PnL ledger back to $0.00.

    Used by the ``POST /api/auto-mode/paper/reset`` endpoint so a fresh
    paper session starts from the configured starting equity rather than
    inheriting the prior session's drawdown.  Writes atomically (tmp +
    rename), mirroring ``_persist_paper_pnl_state``.
    """
    _persist_paper_pnl_state(0.0, path=path)
    log.info("paper_pnl_state ledger reset to $0.00")


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
    # Total taker fee paid at open (USD), retained on the position so each
    # close event can attribute its proportional share back into pnl.
    entry_fee_paid: float = 0.0
    closed_tp_levels: set = field(default_factory=set)
    # Per-trade lifecycle accounting (Phase: paper-trade visibility) —
    # tally gross/fees so close_full can pass the right totals to
    # ``trade_records.close_trade`` without re-computing.  Both reset
    # to zero on every open; populated incrementally by close_partial
    # and finalised by close_full.
    total_gross_pnl_usd: float = 0.0
    total_fees_usd: float = 0.0


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
        pnl_path: Optional[Path] = None,
    ) -> None:
        self._position_size_pct = position_size_pct
        self._max_position_usd = max_position_usd
        self._starting_equity = starting_equity_usd
        # Per-user paper book persistence (2026-06-20): when a ``pnl_path``
        # is supplied (by ``PaperBookRegistry``), this book loads/persists
        # its own ledger so each user's paper PnL is isolated.  ``None`` =
        # the legacy single shared ledger path (``_resolve_paper_pnl_path``).
        self._pnl_path = pnl_path
        # Persistence (2026-05-08) — load any prior cumulative paper-PnL
        # so the dashboard "Paper total since boot" survives engine
        # restarts and paper↔live mode toggles.  Available equity is
        # reseeded from starting + persisted PnL so position sizing
        # reflects the paper account's true balance on resume.  Open
        # positions stay ephemeral (signal-history layer owns lifecycle).
        _persisted = _load_paper_pnl_state(self._pnl_path)
        self._available_equity = starting_equity_usd + _persisted
        self._positions: Dict[str, _PaperPosition] = {}
        # Cumulative realised PnL — seeded from disk (see comment above).
        self._realised_pnl_total: float = _persisted
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
    def current_equity_usd(self) -> float:
        """Cumulative paper equity: starting + realised PnL since the
        first paper session.

        Phase paper-trade-visibility (2026-05-16): owner reported that
        ``current_equity_usd`` "resets daily" on the dashboard.  Root
        cause is on the RiskManager side — ``_current_equity =
        starting_equity + daily_realised_pnl_usd`` so the equity
        figure only carries today's bucket and forgets every prior
        day.  This property is the broker-side truth (starting +
        cumulative since boot) and the engine's
        ``get_auto_execution_status`` now reads from here in paper
        mode so the dashboard surfaces the right number.
        """
        return round(self._starting_equity + self._realised_pnl_total, 4)

    @property
    def open_position_count(self) -> int:
        return sum(
            1
            for p in self._positions.values()
            if (p.quantity - p.closed_quantity) > 0
        )

    def reset_state(self) -> None:
        """Zero out cumulative PnL + available equity back to starting.

        Owner-mediated wipe used by ``POST /api/auto-mode/paper/reset``.
        Open positions are NOT cleared — those are live in-flight trades
        with active engine signals; clearing them would orphan the
        engine's state machine.  In practice the reset endpoint is
        invoked only when the operator has verified no positions are
        open (the endpoint refuses otherwise).

        Persistence: writes the zeroed cumulative PnL through to the
        on-disk ledger so a subsequent restart doesn't re-load the old
        drawdown.
        """
        self._realised_pnl_total = 0.0
        self._available_equity = self._starting_equity
        reset_paper_pnl_state(self._pnl_path)
        log.info(
            "PaperOrderManager.reset_state: equity → ${:.2f}, cumulative PnL → $0.00",
            self._starting_equity,
        )

    def _next_order_id(self, signal_id: str, event: str) -> str:
        self._order_seq += 1
        return f"paper-{signal_id}-{event}-{self._order_seq}"

    def _resolved_position_size_pct(self) -> float:
        """Read the user-set position-size % from per-user overrides first,
        then ``user_settings`` engine-global, then the constructor default.

        Per-user override priority (2026-05-19): the Auto-trade settings
        page writes to ``user_auto_trade_settings`` (per-user SQLite),
        not to the engine-global ``user_settings.json`` — so prior to
        this fix, the paper trader silently ignored the user's app-side
        slider and used ``POSITION_SIZE_PCT`` config default.  We now
        consult the operator's per-user row first via
        ``operator_auto_trade_override()`` (single-user MVP — most-recently-
        updated row is "the operator").  Falls through to user_settings
        and the constructor value when no override has been saved yet."""
        try:
            from src.api import user_overrides as _uo
            override = _uo.operator_auto_trade_override()
            v = override.get("position_size_pct")
            if isinstance(v, (int, float)) and float(v) > 0:
                return float(v)
        except Exception:
            pass
        try:
            from src import user_settings as _us
            return float(_us.auto_trade_position_size_pct())
        except Exception:
            return float(self._position_size_pct)

    def _resolved_leverage(self) -> float:
        """Read the user-set leverage cap from per-user overrides first,
        then ``user_settings`` engine-global, then the 10x dashboard default.

        Paper-trade visibility (2026-05-16): the per-trade ROI%-on-margin
        metric needs to know the leverage the user is conceptually
        trading at.  The engine has no per-signal leverage parameter
        today (the broker treats every paper signal as 1x for fill math),
        so we adopt ``auto_trade_leverage_cap`` as the implicit leverage
        the dashboard math runs against.

        Per-user override priority (2026-05-19): the Auto-trade settings
        page writes leverage_cap to the per-user SQLite row.  Pre-fix the
        paper trader read only from ``user_settings.auto_trade_leverage_cap()``
        which falls back to ``RISK_MAX_LEVERAGE=30`` — so a user setting
        the slider to 10x in-app still saw paper margin sized at 30x.
        Now we consult the operator's per-user row first via
        ``operator_auto_trade_override()`` (single-user MVP — most-recently-
        updated row is the operator).  Falls through to user_settings
        and the 10x default ``PRE_TP_LEVERAGE`` has assumed for months.
        """
        try:
            from src.api import user_overrides as _uo
            override = _uo.operator_auto_trade_override()
            v = override.get("leverage_cap")
            if isinstance(v, (int, float)) and float(v) > 0:
                return float(v)
        except Exception:
            pass
        try:
            from src import user_settings as _us
            v = float(_us.auto_trade_leverage_cap())
            return v if v > 0 else 10.0
        except Exception:
            return 10.0

    async def _compute_quantity(self, entry_price: float) -> float:
        """Compute position size from configured percentage of paper equity.

        Returns 0.0 on any degenerate input so ``place_market_order`` can
        skip the open cleanly via the qty-zero guard rail rather than
        silently entering a position with meaningless size.  Pre-fix
        callsites (2026-05-16) returned ``MAX_POSITION_USD / 1e-12`` on a
        zero-entry price — an astronomical qty that broke every
        downstream calculation.  Post-fix, every degenerate path
        funnels through the explicit zero-return + parent-method skip.
        """
        if entry_price <= 0 or not math.isfinite(entry_price):
            log.debug(
                "_compute_quantity: invalid entry_price=%r — returning 0", entry_price,
            )
            return 0.0
        equity = self._available_equity
        if not math.isfinite(equity) or equity <= 0:
            log.debug(
                "_compute_quantity: depleted/non-finite equity=%r — returning 0",
                equity,
            )
            return 0.0
        pct = self._resolved_position_size_pct()
        if not math.isfinite(pct) or pct <= 0:
            log.debug(
                "_compute_quantity: invalid position_size_pct=%r — returning 0", pct,
            )
            return 0.0
        position_usd = min(equity * (pct / 100.0), self._max_position_usd)
        if position_usd <= 0:
            return 0.0
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

        Skip-with-marker conditions (return ``None`` and log
        ``paper_trade_skip``; **never** create a degenerate position):

        * Missing ``signal_id`` — caller didn't pass a real signal
        * Invalid entry price (≤ 0 or NaN)
        * Idempotent re-open of an already-tracked signal
        * Risk gate refusal (when a RiskManager is wired)
        * Depleted equity / zero position_size_pct (caught by
          :meth:`_compute_quantity` → qty == 0)
        * Sub-floor notional (notional < ``_MIN_PAPER_NOTIONAL_USD``)
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
        if entry <= 0 or not math.isfinite(entry):
            log.info(
                "paper_trade_skip reason=invalid_entry signal_id=%s entry=%r",
                signal_id, entry,
            )
            return None

        if quantity is None:
            quantity = await self._compute_quantity(entry)

        # Quantity guard rail (Phase: paper-trade visibility, 2026-05-16).
        # Owner reported qty=0 paper trades polluting the per-trade ledger
        # — pre-fix the broker would open a position with quantity==0,
        # accumulate zero PnL on every close, and emit dashboard rows that
        # made no sense.  Guard exhaustively so every "garbage qty" path
        # surfaces a single parseable marker.
        if (
            quantity is None
            or not math.isfinite(quantity)
            or quantity <= 0
        ):
            log.info(
                "paper_trade_skip reason=qty_zero signal_id=%s symbol=%s "
                "entry=%.6f available_equity=$%.2f pos_pct=%.2f%%",
                signal_id, getattr(signal, "symbol", "?"), entry,
                self._available_equity, self._resolved_position_size_pct(),
            )
            return None

        notional = entry * quantity
        if notional < _MIN_PAPER_NOTIONAL_USD:
            log.info(
                "paper_trade_skip reason=notional_floor signal_id=%s "
                "notional=$%.4f floor=$%.2f",
                signal_id, notional, _MIN_PAPER_NOTIONAL_USD,
            )
            return None
        # Entry as a market order pays the taker fee (Binance VIP 0: 0.04%).
        # We deduct it from available equity immediately (real cash leaves
        # the account at fill) but defer attribution into ``realised_pnl``
        # to the close event, where each partial close pays its proportional
        # share alongside its exit fee.  This keeps the daily PnL ledger
        # one entry per trade close (fees included) instead of split across
        # open/close days.
        entry_fee = _entry_fee(notional)
        order_id = self._next_order_id(signal_id, "open")
        self._positions[signal_id] = _PaperPosition(
            signal_id=signal_id,
            symbol=getattr(signal, "symbol", "?"),
            side=side,
            entry=entry,
            quantity=quantity,
            entry_fee_paid=entry_fee,
        )
        # Margin reservation — naive: subtract notional + entry fee from available.
        self._available_equity -= notional + entry_fee
        if self._risk_manager is not None:
            self._risk_manager.register_open(signal)

        # Per-trade row in the SQLite ledger (Phase: paper-trade visibility,
        # 2026-05-16).  Snapshot leverage + position_size_pct AT OPEN so a
        # later settings-page change doesn't retroactively rewrite the row.
        leverage_at_open = self._resolved_leverage()
        pos_pct_at_open = self._resolved_position_size_pct()
        try:
            trade_records.open_trade(
                signal_id=signal_id,
                symbol=self._positions[signal_id].symbol,
                side=side,
                entry=entry,
                qty=quantity,
                leverage=leverage_at_open,
                position_size_pct=pos_pct_at_open,
            )
        except Exception:
            # The per-trade ledger is a visibility feature — failures here
            # must NOT break the simulated fill path.  Log and continue.
            log.exception(
                "trade_records.open_trade failed for signal_id=%s — "
                "broker state intact, dashboard row missing", signal_id,
            )

        log.info(
            "paper_trade_fill event=open signal_id=%s symbol=%s side=%s "
            "entry=%.6f qty=%.6f notional=%.2f leverage=%.1fx order_id=%s",
            signal_id, self._positions[signal_id].symbol,
            side, entry, quantity, notional, leverage_at_open, order_id,
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
        gross_pnl = (
            (fill_price - position.entry) * close_qty
            if position.side == "long"
            else (position.entry - fill_price) * close_qty
        )
        # TP fills are limit orders → maker fee.  Plus this close's
        # proportional share of the entry-time taker fee.
        exit_fee = _tp_exit_fee(fill_price * close_qty)
        entry_fee_share = (
            position.entry_fee_paid * (close_qty / position.quantity)
            if position.quantity > 0 else 0.0
        )
        pnl = gross_pnl - exit_fee - entry_fee_share
        total_fee_this_fill = exit_fee + entry_fee_share

        position.closed_quantity += close_qty
        position.realised_pnl_usd += pnl
        position.total_gross_pnl_usd += gross_pnl
        position.total_fees_usd += total_fee_this_fill
        self._realised_pnl_total += pnl
        # Free up margin proportional to closed quantity (entry fee
        # already deducted at open, exit fee deducted from pnl above).
        self._available_equity += position.entry * close_qty + pnl
        # Persist cumulative PnL so the dashboard "Paper total since boot"
        # survives engine restarts and paper↔live mode toggles.
        _persist_paper_pnl_state(self._realised_pnl_total, self._pnl_path)
        # Append to the daily-bucketed history ledger powering the
        # weekly / monthly aggregates and the dashboard PnL chart.
        pnl_history.record_close("paper", pnl)
        # Per-trade SQLite store — append a fill event so the dashboard's
        # trade-detail view can show the TP-by-TP breakdown.
        try:
            trade_records.record_partial_fill(
                signal_id=signal_id,
                tp_level=tp_level,
                fraction=fraction,
                fill_price=fill_price,
                pnl_usd=pnl,
                fee_usd=total_fee_this_fill,
            )
        except Exception:
            log.exception(
                "trade_records.record_partial_fill failed for signal_id=%s — "
                "broker state intact, fill telemetry missing", signal_id,
            )

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
            # Per-trade row close — fully-via-TPs path (e.g. TP3 took the
            # last fraction).  Pass the running totals accumulated across
            # every partial fill so ROI%-on-margin is computed correctly.
            close_reason = f"tp{tp_level}" if tp_level else "tp_full"
            try:
                trade_records.close_trade(
                    signal_id=signal_id,
                    close_reason=close_reason,
                    close_price=fill_price,
                    gross_pnl_usd=position.total_gross_pnl_usd,
                    fees_usd=position.total_fees_usd,
                    net_pnl_usd=position.realised_pnl_usd,
                )
            except Exception:
                log.exception(
                    "trade_records.close_trade (TP path) failed for "
                    "signal_id=%s", signal_id,
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
            # Position drained by prior partial closes but the entry was
            # never popped (floating-point edge or partial-close path that
            # didn't reach the pop branch).  Drop the entry AND notify
            # the risk manager — otherwise ``_open_signal_ids`` keeps the
            # signal_id forever and ``open_position_count`` reports
            # stale state, the visible symptom of the 2026-05-18
            # "Open positions: 4 / No open positions" UI bug.
            self._positions.pop(signal_id, None)
            if self._risk_manager is not None:
                self._risk_manager.register_close(
                    signal,
                    realised_pnl_usd=position.realised_pnl_usd,
                )
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
        gross_pnl = (
            (fill_price - position.entry) * remaining_qty
            if position.side == "long"
            else (position.entry - fill_price) * remaining_qty
        )
        # Fee model: production close_full reasons are "sl_hit" / "expired"
        # / "invalidated" / "cancelled" — all stop-market or market orders
        # that take liquidity → taker fee.  TP-style reasons (e.g. tests
        # closing a full position at TP) are limit orders → maker.
        _reason_lower = (reason or "").lower()
        _is_tp_close = "tp" in _reason_lower
        exit_fee = (
            _tp_exit_fee(fill_price * remaining_qty) if _is_tp_close
            else _sl_exit_fee(fill_price * remaining_qty)
        )
        entry_fee_share = (
            position.entry_fee_paid * (remaining_qty / position.quantity)
            if position.quantity > 0 else 0.0
        )
        pnl = gross_pnl - exit_fee - entry_fee_share
        total_fee_this_fill = exit_fee + entry_fee_share

        position.closed_quantity += remaining_qty
        position.realised_pnl_usd += pnl
        position.total_gross_pnl_usd += gross_pnl
        position.total_fees_usd += total_fee_this_fill
        self._realised_pnl_total += pnl
        self._available_equity += position.entry * remaining_qty + pnl
        # Persist cumulative PnL so the dashboard "Paper total since boot"
        # survives engine restarts and paper↔live mode toggles.
        _persist_paper_pnl_state(self._realised_pnl_total, self._pnl_path)
        # Append to the daily-bucketed history ledger powering the
        # weekly / monthly aggregates and the dashboard PnL chart.
        pnl_history.record_close("paper", pnl)
        # Per-trade row close — see open_trade comment for why we wrap
        # in try/except: a SQLite IO failure here must never break the
        # broker's lifecycle.
        try:
            trade_records.close_trade(
                signal_id=signal_id,
                close_reason=reason,
                close_price=fill_price,
                gross_pnl_usd=position.total_gross_pnl_usd,
                fees_usd=position.total_fees_usd,
                net_pnl_usd=position.realised_pnl_usd,
            )
        except Exception:
            log.exception(
                "trade_records.close_trade (full path) failed for "
                "signal_id=%s", signal_id,
            )

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

    # ------------------------------------------------------------------
    # User-facing "close every paper position now"
    # ------------------------------------------------------------------

    async def close_all_open_positions(
        self,
        reason: str = "user_close_all",
    ) -> Dict[str, Any]:
        """Flatten the paper book — close every open simulated position.

        Why this exists
        ---------------
        ``POST /api/auto-mode/paper/reset`` (PR #401) deliberately leaves
        ``_positions`` untouched: the reset doctrine preserves in-flight
        signals so the live-mode counterpart (whose broker positions
        live on the exchange) doesn't get orphaned by a careless
        equity-wipe.  But users running paper-only sessions still want a
        one-shot "flatten my book" action they can fire before
        ``/reset`` — without it the reset endpoint refuses (open-positions
        guard) and users are stuck closing positions one-by-one through
        whatever surface happens to expose ``close_full``.

        This method is the dedicated user-facing action.  It closes every
        currently-open paper position at a **zero-move fill** (fill price
        == entry) so the close itself books no price PnL — just the
        round-trip fee cost.  Zero-move is the right semantic: the user
        is choosing to flatten, not exit at mark, and we have no live
        market data dependency to take here.

        Implementation
        --------------
        * Snapshot keys upfront — :meth:`close_full` mutates
          ``self._positions`` so iterating it directly would either skip
          entries or raise ``RuntimeError: dictionary changed size
          during iteration``.
        * Build a minimal signal-like object via :class:`types.SimpleNamespace`
          carrying just the attributes ``close_full`` reads
          (``signal_id`` and ``current_price``; ``stop_loss`` defaulted
          to 0.0 so the fallback chain never trips).
        * Sum realised PnL across every close so the caller can surface a
          single aggregate in the response.  Returned PnL totals are
          **per-close** (not cumulative since boot) — the dashboard's
          existing ``simulated_pnl_total`` continues to be the cumulative
          source of truth.
        * Risk manager is notified via the normal :meth:`close_full`
          path — no separate bookkeeping.

        Idempotent — calling on an empty book returns ``{closed_count:
        0, realised_pnl_total: 0.0}`` without side effects.

        Returns
        -------
        dict
            ``{"closed_count": int, "realised_pnl_total": float}``
        """
        # Snapshot keys before iteration — close_full pops from
        # self._positions on success.
        snapshot_ids = list(self._positions.keys())

        closed_count = 0
        realised_total = 0.0

        for sid in snapshot_ids:
            position = self._positions.get(sid)
            if position is None:
                # Defensive — concurrent close from another task between
                # snapshot and now.
                continue
            # Zero-move close: fill_price == entry.  close_full prefers an
            # explicit ``current_price`` arg when > 0, so passing
            # position.entry pins the fill price exactly.
            stub_signal = types.SimpleNamespace(
                signal_id=sid,
                symbol=position.symbol,
                current_price=position.entry,
                # stop_loss kept on the namespace so close_full's
                # getattr fallback chain doesn't surface AttributeError
                # under any path.
                stop_loss=0.0,
            )
            pnl_before = self._realised_pnl_total
            order_id = await self.close_full(
                stub_signal,
                reason=reason,
                current_price=position.entry,
            )
            if order_id is not None:
                closed_count += 1
                realised_total += (self._realised_pnl_total - pnl_before)

        log.info(
            "paper_close_all: closed %d open paper positions (reason=%s)",
            closed_count, reason,
        )
        return {
            "closed_count": closed_count,
            "realised_pnl_total": round(realised_total, 4),
        }
