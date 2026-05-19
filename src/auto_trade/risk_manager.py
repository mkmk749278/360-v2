"""Risk gates for auto-trade execution — Phase A2.

Doctrine: B12 (auto-trade safety) requires the following non-negotiable
gates before any signal can be auto-executed in either paper or live mode:

  1. Daily loss kill   — auto-pause when realised PnL ≤ -DAILY_LOSS_LIMIT_PCT
                         of starting equity.  Resets at UTC midnight.
  2. Concurrent cap    — reject when open position count ≥ MAX_CONCURRENT.
  3. Per-symbol cap    — reject when an open position already exists on
                         the same symbol (no doubling up).
  4. Leverage cap      — reject when configured leverage > MAX_LEVERAGE
                         (default 30x — Walbi-style 200x is irresponsible).
  5. Min equity floor  — reject when account equity < MIN_EQUITY_USD.
  6. Setup whitelist   — env-driven enable/disable per evaluator path.

The RiskManager is consulted by both OrderManager (live) and
PaperOrderManager (paper) via the same ``check(signal)`` coroutine — the
gates apply identically in both modes.  Each rejection emits a parseable
``risk_gate_block`` log marker for truth-report attribution and returns
the trip reason so callers can surface it to subscribers.

Out of scope (separate concerns)
--------------------------------
* Restart reconciliation (Phase A3)
* Order audit log (Phase A4)
* Per-user risk profiles (multi-user, future)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional, Set

from src.utils import get_logger

log = get_logger("risk_manager")


@dataclass
class RiskGateResult:
    """Outcome of a single ``RiskManager.check()`` call.

    ``allowed`` is True when every gate passes.  When False, ``reason``
    holds a short snake_case token (e.g. ``daily_loss_kill``) and
    ``detail`` carries a human-readable string for telemetry / UI.
    """
    allowed: bool
    reason: str = ""
    detail: str = ""


@dataclass
class _DailyLossState:
    """Tracks running daily loss against today's UTC date."""
    date_utc: str = ""
    realised_pnl_usd: float = 0.0

    def reset_if_new_day(self, now: datetime) -> None:
        today = now.strftime("%Y-%m-%d")
        if today != self.date_utc:
            self.date_utc = today
            self.realised_pnl_usd = 0.0


class RiskManager:
    """Pre-execution safety gates for auto-trade.

    Parameters
    ----------
    starting_equity_usd:
        The reference equity used for daily-loss percentage math.  In
        paper mode this is the synthetic starting balance; in live mode
        it should be queried from the exchange at boot and passed in.
    daily_loss_limit_pct:
        Negative percentage of starting equity that, when crossed,
        trips the kill switch.  Default ``-3.0`` (i.e. -3% of starting).
    max_concurrent:
        Hard cap on open positions across all symbols.  Default 5.
    max_leverage:
        Hard cap on configured leverage.  Default 30.
    min_equity_usd:
        Auto-pause when current equity falls below this floor (catches
        long-tail bleed even if daily loss kill hasn't tripped on a
        single day).  Default 0 (disabled by default).
    setup_blacklist:
        Setups whose signals are silently rejected at the gate.  Default
        empty.  Configurable for emergency disable of a misbehaving path.
    """

    def __init__(
        self,
        *,
        starting_equity_usd: float,
        daily_loss_limit_pct: float = -3.0,
        max_concurrent: int = 5,
        max_leverage: float = 30.0,
        min_equity_usd: float = 0.0,
        setup_blacklist: Optional[Set[str]] = None,
        mode: Optional[str] = None,
    ) -> None:
        if starting_equity_usd <= 0:
            raise ValueError("starting_equity_usd must be > 0")
        if daily_loss_limit_pct >= 0:
            raise ValueError("daily_loss_limit_pct must be negative (a loss)")
        if max_concurrent < 1:
            raise ValueError("max_concurrent must be >= 1")
        if max_leverage <= 0:
            raise ValueError("max_leverage must be > 0")

        self._starting_equity = float(starting_equity_usd)
        self._daily_loss_limit_pct = float(daily_loss_limit_pct)
        self._max_concurrent = int(max_concurrent)
        self._max_leverage = float(max_leverage)
        self._min_equity_usd = float(min_equity_usd)
        self._setup_blacklist: Set[str] = set(setup_blacklist or set())

        self._daily = _DailyLossState()
        self._mode = mode
        # Rehydrate today's realised PnL from the persistent history
        # ledger so a restart at 23:55 UTC doesn't orphan the day's
        # loss-budget tracking — pre-fix, the daily kill could be
        # silently reset by a redeploy.  No-op when ``mode`` is None
        # (test fixtures, off mode) so existing call sites keep working.
        if mode:
            try:
                from src.auto_trade import pnl_history
                today_pnl = pnl_history.get_daily(mode)
                if today_pnl != 0.0:
                    self._daily.date_utc = datetime.now(timezone.utc).strftime(
                        "%Y-%m-%d"
                    )
                    self._daily.realised_pnl_usd = today_pnl
            except Exception:
                # Fail-soft — clean-slate daily counter is the safe
                # default if persistence is broken.
                pass
        # Tracked separately from any OrderManager/PaperOrderManager so we
        # don't depend on either's internal representation.  Caller updates
        # via ``register_open()`` / ``register_close()``.
        self._open_signal_ids: Set[str] = set()
        self._open_symbols: Set[str] = set()
        self._current_equity: float = (
            float(starting_equity_usd) + self._daily.realised_pnl_usd
        )
        # Manual kill switch (e.g. owner pause via Telegram command).
        self._manual_pause: bool = False
        # Sticky kill — once tripped today, blocks further opens until
        # UTC midnight even if PnL recovers.  Prevents the "loss → small
        # bounce → re-enter → bigger loss" trap.
        self._daily_kill_tripped: bool = False

    # ------------------------------------------------------------------
    # State updates (caller-driven)
    # ------------------------------------------------------------------

    def register_open(self, signal: Any) -> None:
        """Record that a new position is open.  Caller invokes this after
        a successful order placement."""
        sid = getattr(signal, "signal_id", "")
        sym = getattr(signal, "symbol", "")
        if sid:
            self._open_signal_ids.add(sid)
        if sym:
            self._open_symbols.add(sym)

    def register_close(self, signal: Any, *, realised_pnl_usd: float = 0.0) -> None:
        """Record that a position has closed and apply realised PnL to
        the running daily total."""
        sid = getattr(signal, "signal_id", "")
        sym = getattr(signal, "symbol", "")
        if sid:
            self._open_signal_ids.discard(sid)
        # Symbol may still have other open signals (rare but possible) —
        # only release when no other open signal references it.
        if sym and not any(
            getattr(s, "symbol", None) == sym for s in self._open_signal_ids
        ):
            self._open_symbols.discard(sym)
        self._apply_realised_pnl(realised_pnl_usd)

    def _apply_realised_pnl(self, pnl_usd: float) -> None:
        now = datetime.now(timezone.utc)
        self._daily.reset_if_new_day(now)
        if self._daily.date_utc != now.strftime("%Y-%m-%d") or self._daily_kill_tripped is False:
            # If this is a new day, also reset the sticky kill flag.
            if self._daily.realised_pnl_usd == 0.0:
                self._daily_kill_tripped = False
        self._daily.realised_pnl_usd += float(pnl_usd)
        self._current_equity = self._starting_equity + self._daily.realised_pnl_usd

    def update_equity(self, equity_usd: float) -> None:
        """Live mode: caller polls the exchange and pushes equity in."""
        if equity_usd > 0:
            self._current_equity = float(equity_usd)

    def set_manual_pause(self, paused: bool) -> None:
        """Owner-driven kill switch — independent of the daily-loss kill."""
        self._manual_pause = bool(paused)

    def reset_daily(self) -> None:
        """Zero the daily-loss state and equity so a paper-balance reset
        produces a clean Trade-tab "today" reading immediately.

        The dashboard's ``daily_pnl_usd`` is sourced from
        ``daily_realised_pnl_usd`` (``src/main.py``) which delegates to
        ``_daily.realised_pnl_usd`` here.  Without this wipe, the paper
        reset endpoint cleared the PaperOrderManager + on-disk pnl_history
        but the in-memory RiskManager kept yesterday's loss number until
        UTC midnight — Trade tab read stale.  Also clears the sticky daily
        kill flag and re-anchors ``_current_equity`` to ``_starting_equity``
        (which itself stays the same — that's the configured paper
        starting balance, not equity-after-pnl).
        """
        now = datetime.now(timezone.utc)
        self._daily.date_utc = now.strftime("%Y-%m-%d")
        self._daily.realised_pnl_usd = 0.0
        self._daily_kill_tripped = False
        self._current_equity = self._starting_equity

    # ------------------------------------------------------------------
    # Gate
    # ------------------------------------------------------------------

    def check(self, signal: Any, *, leverage: Optional[float] = None) -> RiskGateResult:
        """Evaluate every gate against *signal*.  Returns the first trip.

        Parameters
        ----------
        signal:
            The :class:`Signal` candidate for execution.
        leverage:
            The leverage the caller intends to use.  When omitted we read
            ``signal.leverage`` if present, else default to 1.0 (spot-like).
        """
        now = datetime.now(timezone.utc)
        self._daily.reset_if_new_day(now)
        # New day → reset sticky kill if it wasn't tripped today.
        if self._daily.realised_pnl_usd == 0.0 and self._daily_kill_tripped:
            self._daily_kill_tripped = False

        # 0. Manual pause takes precedence over everything.
        if self._manual_pause:
            return self._block(
                signal, "manual_pause", "owner-paused via control surface"
            )

        # 1. Daily loss kill — sticky for the rest of the UTC day once tripped.
        loss_pct = (self._daily.realised_pnl_usd / self._starting_equity) * 100.0
        if self._daily_kill_tripped or loss_pct <= self._daily_loss_limit_pct:
            self._daily_kill_tripped = True
            return self._block(
                signal,
                "daily_loss_kill",
                f"daily PnL {loss_pct:+.2f}% ≤ limit {self._daily_loss_limit_pct:+.2f}%",
            )

        # 2. Min equity floor.
        if self._min_equity_usd > 0 and self._current_equity < self._min_equity_usd:
            return self._block(
                signal,
                "min_equity_floor",
                f"equity ${self._current_equity:.2f} < floor ${self._min_equity_usd:.2f}",
            )

        # 3. Concurrent-position cap.  User can lower this from the app
        # via ``/api/settings/user/auto-trade`` (per-user override) or the
        # operator via ``/api/settings/auto-trade`` (engine-global).  Per-
        # user override has priority — matches paper_order_manager's
        # resolution order.
        try:
            from src.api import user_overrides as _uo
            override = _uo.operator_auto_trade_override()
            v = override.get("max_concurrent_positions")
            if isinstance(v, int) and v >= 1:
                _max_concurrent = min(self._max_concurrent, int(v))
            else:
                from src import user_settings as _us
                _max_concurrent = min(
                    self._max_concurrent, int(_us.auto_trade_max_concurrent())
                )
        except Exception:
            _max_concurrent = self._max_concurrent
        if len(self._open_signal_ids) >= _max_concurrent:
            return self._block(
                signal,
                "max_concurrent",
                f"open count {len(self._open_signal_ids)} ≥ cap {_max_concurrent}",
            )

        # 4. Per-symbol cap (no doubling up on the same pair).
        sym = getattr(signal, "symbol", "")
        if sym and sym in self._open_symbols:
            return self._block(
                signal,
                "per_symbol_cap",
                f"already an open position on {sym}",
            )

        # 5. Leverage cap.  User-set value (clamped to engine hard cap)
        # takes precedence over constructor default.  Per-user override
        # has priority — matches paper_order_manager's resolution order
        # so paper-mode math and live-mode gate agree on "the leverage
        # the user picked in the app."
        if leverage is None:
            leverage = float(getattr(signal, "leverage", 1.0) or 1.0)
        _eff_leverage_cap = self._max_leverage
        try:
            from src.api import user_overrides as _uo
            override = _uo.operator_auto_trade_override()
            v = override.get("leverage_cap")
            if isinstance(v, (int, float)) and float(v) > 0:
                _eff_leverage_cap = min(self._max_leverage, float(v))
            else:
                from src import user_settings as _us
                _eff_leverage_cap = min(
                    self._max_leverage, float(_us.auto_trade_leverage_cap())
                )
        except Exception:
            pass
        if leverage > _eff_leverage_cap:
            return self._block(
                signal,
                "leverage_cap",
                f"requested {leverage:.0f}x > cap {_eff_leverage_cap:.0f}x",
            )

        # 6. Setup blacklist.
        setup = str(getattr(signal, "setup_class", ""))
        if setup and setup in self._setup_blacklist:
            return self._block(
                signal,
                "setup_blacklisted",
                f"setup {setup} is on the blacklist",
            )

        # All gates passed.
        return RiskGateResult(allowed=True)

    # ------------------------------------------------------------------
    # Read-only state for dashboards / truth report
    # ------------------------------------------------------------------

    @property
    def open_position_count(self) -> int:
        return len(self._open_signal_ids)

    @property
    def daily_realised_pnl_usd(self) -> float:
        return round(self._daily.realised_pnl_usd, 4)

    @property
    def daily_loss_pct(self) -> float:
        return round(
            (self._daily.realised_pnl_usd / self._starting_equity) * 100.0,
            3,
        )

    @property
    def daily_kill_tripped(self) -> bool:
        return self._daily_kill_tripped

    @property
    def current_equity_usd(self) -> float:
        return round(self._current_equity, 4)

    @property
    def manual_paused(self) -> bool:
        return self._manual_pause

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _block(self, signal: Any, reason: str, detail: str) -> RiskGateResult:
        """Emit telemetry marker and return a blocked result."""
        sym = getattr(signal, "symbol", "?")
        sid = getattr(signal, "signal_id", "?")
        log.info(
            "risk_gate_block reason=%s symbol=%s signal_id=%s detail=%s",
            reason, sym, sid, detail,
        )
        return RiskGateResult(allowed=False, reason=reason, detail=detail)
