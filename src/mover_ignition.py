"""Real-time mover *ignition* detector — catch movers at minute-zero.

The legacy mover-promotion trigger (``scanner._update_movers_promotion``) keys
off Binance's **trailing 24h** ``priceChangePercent`` (``pair_manager.
volatility_24h``), refreshed only every ``PAIR_FETCH_INTERVAL_HOURS``. A single
24h-cumulative number can never say *when* the move happened, so a pair that
ran +30 % hours ago still tops the leaderboard now and gets promoted long after
the move is spent — VSB / BDS / MOVER_TREND_PULLBACK then enter a continuation
into exhaustion (the live "promote after the move, then fight it" failure).

This detector replaces that lagging trigger with a **real-time ignition signal**
derived from the USDS-M futures all-market ticker stream ``!ticker@arr`` (one
WebSocket stream, 1000 ms cadence, every changed symbol). No REST polling, no
Firestore, no per-symbol subscriptions — it is pure in-memory arithmetic over a
stream the engine now receives, so it adds **zero** hot-path reads (Cost
Discipline).

Each ``!ticker@arr`` element carries, per symbol: last price ``c``, 24h quote
volume ``q``, cumulative trade count ``n`` and event time ``E``. ``q`` and
``n`` are monotonic *within* the 24h window, so the **delta between two 1 s
pushes** yields an instantaneous quote-volume rate and trade rate; ``c`` gives a
clean price move. Ignition = a short-window price move clearing a floor **and** a
trade-rate burst well above the pair's own EWMA baseline (real-time relative
volume — ignition is volume-led) **and** a minimum traded notional so dead
micro-caps cannot trip it. Promote on that, seed candles, and the move is fresh
*by construction*.

The detector holds no engine references and does no I/O — it ingests ticker
arrays and returns newly-ignited ``(symbol, direction)`` tuples, which makes it
fully unit-testable with synthetic frames.
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List, Optional, Tuple

from src.utils import get_logger

log = get_logger("mover_ignition")

# Direction strings match the evaluator/promotion vocabulary used elsewhere.
LONG = "long"
SHORT = "short"


@dataclass
class _SymbolState:
    """Per-symbol rolling state — bounded, in-memory only."""

    # Trailing window of (event_time_ms, last_price, cum_trades, cum_quote_vol)
    # used to measure the move / rates over ``window_sec``.
    samples: Deque[Tuple[int, float, int, float]] = field(default_factory=deque)
    # EWMA of per-sample trade-rate (trades/sec) — the pair's "normal" activity
    # baseline that a burst is measured against.
    rate_ewma: Optional[float] = None
    # Number of samples folded into the baseline (warmup gate).
    baseline_samples: int = 0
    # Monotonic clock until which this symbol will not re-ignite.
    cooldown_until: float = 0.0


class MoverIgnitionDetector:
    """Detect mover ignition from successive ``!ticker@arr`` frames.

    All thresholds are injected (sourced from ``config`` at the call site) so the
    detector stays free of import-time config coupling and is trivial to drive
    from tests.
    """

    def __init__(
        self,
        *,
        enabled: bool,
        window_sec: float,
        move_floor_pct: float,
        burst_mult: float,
        min_window_notional_usd: float,
        cooldown_sec: float,
        baseline_alpha: float,
        min_baseline_samples: int,
        max_gap_sec: float,
        quote_suffix: str = "USDT",
    ) -> None:
        self.enabled = enabled
        self.window_sec = window_sec
        self.move_floor_pct = move_floor_pct
        self.burst_mult = burst_mult
        self.min_window_notional_usd = min_window_notional_usd
        self.cooldown_sec = cooldown_sec
        self.baseline_alpha = baseline_alpha
        self.min_baseline_samples = min_baseline_samples
        self.max_gap_sec = max_gap_sec
        self.quote_suffix = quote_suffix
        self._state: Dict[str, _SymbolState] = {}
        # Latest 24h (change_pct, quote_vol) per symbol from every !ticker@arr
        # frame — the FULL futures universe (~600 pairs), far beyond the engine's
        # top-75 scan set. This is the only place we see universe-wide movers, so
        # promotion sources both ignition AND the top-24h leaderboard from here.
        self._meta: Dict[str, Tuple[float, float]] = {}
        # Liveness counters — surfaced via stats() so the ops Pairs page can
        # tell "genuinely quiet" (frames flowing, no ignitions) from "stalled
        # feed" (no frames) when the promoting list is empty.
        self._frames = 0
        self._ignitions_total = 0
        self._last_ignition_at: Optional[str] = None

    # -- public API ---------------------------------------------------------

    def ingest(
        self, tickers: List[dict], *, now: Optional[float] = None
    ) -> List[Tuple[str, str]]:
        """Fold one ``!ticker@arr`` array in; return newly-ignited pairs.

        ``tickers`` is the raw Binance array (list of per-symbol dicts).
        ``now`` is a monotonic timestamp (defaults to ``time.monotonic()``) used
        only for cooldown bookkeeping — event timing itself comes from each
        ticker's ``E`` field so the detector is insensitive to processing lag.
        """
        if not self.enabled or not tickers:
            return []
        self._frames += 1
        mono = time.monotonic() if now is None else now
        ignited: List[Tuple[str, str]] = []
        for t in tickers:
            hit = self._ingest_one(t, mono)
            if hit is not None:
                ignited.append(hit)
        if ignited:
            self._ignitions_total += len(ignited)
            self._last_ignition_at = datetime.now(timezone.utc).isoformat()
        return ignited

    def tracked_symbols(self) -> int:
        """Number of symbols with live state — for telemetry."""
        return len(self._state)

    def stats(self) -> Dict[str, Any]:
        """Liveness snapshot for the ops Pairs page."""
        return {
            "enabled": self.enabled,
            "tracked_symbols": len(self._state),
            "frames_ingested": self._frames,
            "ignitions_total": self._ignitions_total,
            "last_ignition_at": self._last_ignition_at,
        }

    def meta(self, symbol: str) -> Optional[Tuple[float, float]]:
        """Latest ``(change_pct, quote_vol)`` for a symbol, or ``None`` if the
        stream hasn't carried it yet. Lets the scanner admit an igniting pair
        that isn't in the engine's top-75 ``pair_mgr`` universe."""
        return self._meta.get(symbol.upper())

    def activity(self, symbol: str) -> Optional[float]:
        """Current trade-rate burst for *symbol*, as a multiple of its own EWMA
        baseline — or ``None`` when it cannot be measured.

        The same arithmetic ``_ingest_one`` uses to decide ignition, exposed
        without the firing thresholds so a consumer can ask the opposite
        question: is this move still running, or has it settled back to the
        pair's normal rate? ``mover_retention`` reads it to release a spent
        pair's promotion slot — the "promote after the move, then fight it"
        failure this detector was built for, caught on the way OUT.

        ``None`` rather than 0.0 wherever the reading is unavailable — no
        baseline yet, a reconnect that cleared the window, a symbol the stream
        has not carried. A consumer must be able to tell "trading at baseline"
        from "we cannot see it", because one means the move is over and the
        other means our feed blinked, and dropping a pair mid-trend on the
        second would be a fault wearing the first one's clothes.
        """
        st = self._state.get(str(symbol or "").upper())
        if st is None or st.rate_ewma is None or len(st.samples) < 2:
            return None
        baseline = st.rate_ewma
        if baseline <= 1e-9:
            return None
        old_ms, _old_price, old_trades, _old_qv = st.samples[0]
        evt_ms, _price, trades, _qv = st.samples[-1]
        window_dt = (evt_ms - old_ms) / 1000.0
        if window_dt <= 0:
            return None
        return max(0.0, (trades - old_trades) / window_dt) / baseline

    def universe_movers(
        self, min_abs_pct: float, min_quote_vol: float,
    ) -> List[Tuple[str, float, float]]:
        """Full-universe top movers: ``(symbol, change_pct, quote_vol)`` for every
        streamed pair whose ``|24h %change| >= min_abs_pct`` and
        ``quote_vol >= min_quote_vol``. The sustained-trend promotion source —
        sees the whole ~600-pair futures board, not just the scanned top-75."""
        out: List[Tuple[str, float, float]] = []
        for sym, (pct, vol) in self._meta.items():
            if abs(pct) >= min_abs_pct and vol >= min_quote_vol:
                out.append((sym, pct, vol))
        out.sort(key=lambda r: -abs(r[1]))
        return out

    # -- internals ----------------------------------------------------------

    def _ingest_one(self, t: dict, mono: float) -> Optional[Tuple[str, str]]:
        symbol = str(t.get("s", "")).upper()
        if not symbol or not symbol.endswith(self.quote_suffix):
            return None
        try:
            price = float(t["c"])
            trades = int(t["n"])
            quote_vol = float(t["q"])
            evt_ms = int(t["E"])
        except (KeyError, TypeError, ValueError):
            return None
        if price <= 0:
            return None

        # Universe meta — the 24h %change (``P``) + quote volume for EVERY symbol
        # the stream carries, so promotion can reach movers outside the top-75.
        try:
            self._meta[symbol] = (float(t.get("P", 0.0)), quote_vol)
        except (TypeError, ValueError):
            pass

        st = self._state.get(symbol)
        if st is None:
            st = _SymbolState()
            self._state[symbol] = st
            st.samples.append((evt_ms, price, trades, quote_vol))
            return None

        prev_ms, _prev_price, prev_trades, _prev_qv = st.samples[-1]
        dt = (evt_ms - prev_ms) / 1000.0
        if dt <= 0:
            # Duplicate or out-of-order frame — ignore, keep prior sample.
            return None
        if dt > self.max_gap_sec:
            # Gap too large (reconnect / thin symbol): state is stale. Reset to
            # this frame and re-warm rather than measure across the hole.
            st.samples.clear()
            st.samples.append((evt_ms, price, trades, quote_vol))
            st.rate_ewma = None
            st.baseline_samples = 0
            return None

        # Per-sample trade rate feeds the slow baseline EWMA — but NOT while the
        # pair is already bursting, or a sustained surge would inflate its own
        # baseline and mask itself. Freeze the baseline once the instantaneous
        # rate exceeds the burst threshold; resume updating when it settles.
        per_sample_rate = max(0.0, (trades - prev_trades) / dt)
        if st.rate_ewma is None:
            st.rate_ewma = per_sample_rate
        elif per_sample_rate <= self.burst_mult * st.rate_ewma:
            a = self.baseline_alpha
            st.rate_ewma = a * per_sample_rate + (1.0 - a) * st.rate_ewma
        st.baseline_samples += 1

        # Append current sample, then trim to the trailing window.
        st.samples.append((evt_ms, price, trades, quote_vol))
        self._trim_window(st, evt_ms)

        # Need a baseline we trust and a window spanning real time before firing.
        if st.baseline_samples < self.min_baseline_samples:
            return None
        if mono < st.cooldown_until:
            return None

        old_ms, old_price, old_trades, old_qv = st.samples[0]
        window_dt = (evt_ms - old_ms) / 1000.0
        if window_dt <= 0 or old_price <= 0:
            return None

        move_pct = (price - old_price) / old_price * 100.0
        window_notional = quote_vol - old_qv
        window_rate = max(0.0, (trades - old_trades) / window_dt)
        baseline = st.rate_ewma or 0.0
        burst = window_rate / baseline if baseline > 1e-9 else 0.0

        if (
            abs(move_pct) >= self.move_floor_pct
            and burst >= self.burst_mult
            and window_notional >= self.min_window_notional_usd
        ):
            st.cooldown_until = mono + self.cooldown_sec
            direction = LONG if move_pct > 0 else SHORT
            log.info(
                "🔥 IGNITION {} {} move={:.2f}% burst={:.1f}× notional=${:,.0f}/{:.0f}s",
                symbol, direction, move_pct, burst, window_notional, window_dt,
            )
            return symbol, direction
        return None

    def _trim_window(self, st: _SymbolState, evt_ms: int) -> None:
        """Drop samples older than ``window_sec``, keeping at least two points."""
        cutoff = evt_ms - int(self.window_sec * 1000)
        while len(st.samples) > 2 and st.samples[0][0] < cutoff:
            st.samples.popleft()
