#!/usr/bin/env python3
"""Large-sample exit-method bake-off — does SAR-15m's edge survive?

WHY THIS EXISTS (Session 2026-07-24 handoff).  The ops "Dark Signals" tab measured,
on 7 days / 75 real closed signals, that the engine's exits leak (profit factor
~0.45), that wide trailing stops (ATR / SuperTrend) are *worse*, and that Parabolic
SAR on 15m bars looked like the winner (PF 1.51).  But that edge was **fragile** —
its entire +28.9% was carried by a single trade (RIFUSDT), the *median* SAR trade
was negative, and 75 trades is far too thin to trust.  This script settles it on a
large sample: it generates ~6 months of historical entries from our price-action
strategies over a fixed (survivorship-controlled) universe, replays the same four
exits (engine-baseline / ATR / SuperTrend / SAR) over *thousands* of trades, and
reports per-regime plus **drop-top-N outlier robustness** and **median vs mean** —
the exact fragility checks that flagged the 7-day result as luck-or-edge-unknown.

WHY IT'S A VALID COMPARISON EVEN WITH IMPERFECT ENTRY FIDELITY.  We compare exits
*on the same entries*, so the relative exit ranking and its outlier-robustness are
robust to entry approximation.  Order-flow setups (liquidity sweeps, whale
momentum, CVD divergence) can't be reconstructed from klines, so this covers
**price-action families only** — which is exactly the point: RIFUSDT, the outlier
carrying SAR in the 7-day study, is a liquidity sweep and will *not* appear here.
Does SAR still win once the unreproducible outliers are gone?

FIDELITY CAVEATS (state these in any read of the output):
  * klines-only — no order-flow setups (see ``ORDER_FLOW_SETUPS``);
  * the ``Backtester`` entry path is an approximation of the full live
    scanner + gate chain, so absolute PnL is not truth;
  * the trustworthy output is the **relative exit ranking + robustness**, not
    absolute PnL.

The trailing-exit simulator (``resample`` / ``wilder_atr`` / ``supertrend`` /
``parabolic_sar`` / ``simulate_trailing_exit``) is ported **verbatim** from the
live ops Dark-Signals module (``360ce-ops:app/data_sources/dark_signals.py``) so
this large-sample run and the ops tab compute the *same* numbers on the same
inputs.  Keep them in sync if either changes.

This is an off-money-path analysis script — it never touches engine state, reads
only public Binance Futures klines, and imports the engine only to reuse the
``Backtester`` entry generator.  It is compute- and data-heavy: **run it on the
VPS**, where the engine deps and Binance reachability both exist (this sandbox's
egress IP is geo-blocked by Binance with HTTP 451):

    docker exec 360scalp-v2-engine python scripts/exit_method_backtest.py \
        --months 6 --entry-tf 5m --exit-tf 15m

A quick smoke run (few pairs, one month) validates the pipeline end to end:

    docker exec 360scalp-v2-engine python scripts/exit_method_backtest.py \
        --months 1 --pairs BTCUSDT,ETHUSDT,SOLUSDT --entry-tf 15m --exit-tf 15m
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import os
import statistics
import sys
import time
import urllib.error
import urllib.request
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Deque, Dict, List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------- #
# Universe & setup taxonomy
# --------------------------------------------------------------------------- #
# A fixed set of established, liquid USDT-M perps that existed for the whole
# 6-month window — chosen to avoid survivorship bias (no pair that listed *inside*
# the window, which would bias toward post-listing pumps).  Override with --pairs.
DEFAULT_UNIVERSE: Tuple[str, ...] = (
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT",
    "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT", "LTCUSDT", "TRXUSDT",
    "ATOMUSDT", "NEARUSDT", "APTUSDT", "ARBUSDT", "OPUSDT", "FILUSDT",
    "INJUSDT", "SUIUSDT",
)

# Setup classes we EXCLUDE because their trigger depends on order-flow / on-chain
# inputs that cannot be reconstructed from klines alone (so a klines backtest would
# fire them on the wrong bars).  Everything the backtester emits that is NOT in
# this set is treated as a price-action family and kept.  Mirrors the engine's
# ``SetupClass`` string values (src/signal_quality.py) — kept as a string set so
# this script has no hard dependency on importing that enum.
ORDER_FLOW_SETUPS: frozenset[str] = frozenset({
    "LIQUIDITY_SWEEP_REVERSAL",
    "CONTINUATION_LIQUIDITY_SWEEP",
    "WHALE_MOMENTUM",
    "LIQUIDATION_REVERSAL",
    "FUNDING_EXTREME_SIGNAL",
    "DIVERGENCE_CONTINUATION",   # CVD divergence — order-flow, not price-action
})

# Binance kline interval -> minutes.
_TF_MIN: Dict[str, int] = {
    "1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "2h": 120, "4h": 240,
}
_MINUTE_MS = 60_000
_MAX_LIMIT = 1500  # Binance klines hard cap per request (weight 10 — see below).
_FAPI = "https://fapi.binance.com/fapi/v1/klines"

# --- Rate-limit budget (2026-07-25) ---------------------------------------- #
# This script runs via `docker exec` INSIDE the engine container, so it shares
# the production IP with live trading — but as a separate *process*, so it
# cannot see the engine's in-process limiter (src/rate_limiter.py). It must
# therefore stay inside the headroom that limiter deliberately leaves free.
#
# Binance klines weight tiers (exact, mirrored from src/binance.fetch_klines):
#     limit < 100 -> 1 | 100..499 -> 2 | 500..1000 -> 5 | > 1000 -> 10
# So candles-per-weight peaks at limit=499 (249.5), NOT at the 1500 cap (150).
# Paging at 499 buys 1.66x more data for the same weight.
_PAGE_LIMIT = 499
_PAGE_WEIGHT = 2

# Binance's per-IP futures cap. src/rate_limiter.py budgets the engine 2,200 of
# it, so ~200/min is the spare this job may use without touching live trading.
_FUTURES_WEIGHT_CAP = 2_400
_DEFAULT_WEIGHT_PER_MIN = 200

# When the IP-wide used-weight header says live traffic is this deep into the
# cap, stand down entirely — the money path outranks the analysis job.
_YIELD_ABOVE_USED_WEIGHT = 2_000
_YIELD_SLEEP_SEC = 10.0

# Transient HTTP the fetch retries (with Retry-After when Binance sends it).
_RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
# A ban is NOT retryable — hammering it is what deepens the ban (cf. #778).
_BAN_STATUSES = frozenset({403, 418})
_MAX_ATTEMPTS = 5


class BinanceBanned(RuntimeError):
    """The IP is banned/blocked — abort the whole run rather than hammer it."""

# The exit methods compared, in report order. "engine" is the backtester's own
# realised pnl (baseline); the other three are trailing-only replays.
TRAIL_METHODS: Tuple[str, ...] = ("atr", "supertrend", "sar")
ALL_METHODS: Tuple[str, ...] = ("engine",) + TRAIL_METHODS
METHOD_LABELS: Dict[str, str] = {
    "engine": "Engine real (baseline)",
    "atr": "ATR-trail (Chandelier)",
    "supertrend": "SuperTrend flip",
    "sar": "Parabolic SAR",
}


# --------------------------------------------------------------------------- #
# Trailing-exit simulator — ported VERBATIM from
# 360ce-ops:app/data_sources/dark_signals.py.  Pure; stdlib only (math).  Keep in
# sync with the ops module if either changes — the two must compute identically.
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Bar:
    """One OHLC candle (tf_min-minute)."""

    open_time_ms: int
    open: float
    high: float
    low: float
    close: float


def resample(rows: Sequence[Sequence[float]], tf_min: int) -> List[Bar]:
    """Aggregate ascending (open_ms, o, h, l, c, [volume]) rows into tf_min-minute
    bars. Any trailing fields (e.g. volume) beyond the first five are ignored.

    A tf_min already equal to the source interval is a straight 1:1 map (the
    common case here, since we fetch the exit TF directly).
    """
    bucket_ms = tf_min * _MINUTE_MS
    out: List[Bar] = []
    cur_key: Optional[int] = None
    o = h = lo = c = 0.0
    o_ms = 0
    for row in rows:
        t, ro, rh, rl, rc = int(row[0]), row[1], row[2], row[3], row[4]
        key = (t // bucket_ms) * bucket_ms
        if cur_key is None or key != cur_key:
            if cur_key is not None:
                out.append(Bar(o_ms, o, h, lo, c))
            cur_key = key
            o_ms = key
            o = ro or rc
            h = rh
            lo = rl
            c = rc
        else:
            h = max(h, rh)
            lo = min(lo, rl)
            c = rc
    if cur_key is not None:
        out.append(Bar(o_ms, o, h, lo, c))
    return out


def wilder_atr(
    highs: List[float], lows: List[float], closes: List[float], period: int
) -> List[Optional[float]]:
    """Average True Range (Wilder smoothing). None until enough bars."""
    n = len(closes)
    out: List[Optional[float]] = [None] * n
    if n < period + 1:
        return out
    trs: List[float] = [0.0] * n
    for i in range(1, n):
        trs[i] = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
    atr = sum(trs[1: period + 1]) / period
    out[period] = atr
    for i in range(period + 1, n):
        atr = (atr * (period - 1) + trs[i]) / period
        out[i] = atr
    return out


def supertrend(
    highs: List[float], lows: List[float], closes: List[float], period: int, mult: float
) -> Tuple[List[Optional[float]], List[Optional[int]]]:
    """SuperTrend line + direction (1 up / -1 down). None until ATR seeds."""
    n = len(closes)
    line: List[Optional[float]] = [None] * n
    direction: List[Optional[int]] = [None] * n
    atr = wilder_atr(highs, lows, closes, period)

    upper: List[Optional[float]] = [None] * n
    lower: List[Optional[float]] = [None] * n
    for i in range(n):
        a = atr[i]
        if a is None:
            continue
        hl2 = (highs[i] + lows[i]) / 2.0
        upper[i] = hl2 + mult * a
        lower[i] = hl2 - mult * a

    first = next((i for i in range(n) if upper[i] is not None), None)
    if first is None:
        return line, direction
    direction[first] = 1
    line[first] = lower[first]
    for i in range(first + 1, n):
        if upper[i] is None:
            continue
        if not (lower[i] > lower[i - 1] or closes[i - 1] < (lower[i - 1] or -math.inf)):
            lower[i] = lower[i - 1]
        if not (upper[i] < upper[i - 1] or closes[i - 1] > (upper[i - 1] or math.inf)):
            upper[i] = upper[i - 1]
        prev_dir = direction[i - 1] if direction[i - 1] is not None else 1
        if prev_dir == 1:
            if closes[i] < (lower[i] or -math.inf):
                direction[i] = -1
                line[i] = upper[i]
            else:
                direction[i] = 1
                line[i] = lower[i]
        else:
            if closes[i] > (upper[i] or math.inf):
                direction[i] = 1
                line[i] = lower[i]
            else:
                direction[i] = -1
                line[i] = upper[i]
    return line, direction


def parabolic_sar_levels(
    highs: List[float], lows: List[float], step: float, max_step: float
) -> Tuple[List[Optional[float]], List[Optional[float]]]:
    """Parabolic SAR (Wilder) → (published indicator, stop in force per bar).

    See ``src.sar_exit_shadow.parabolic_sar_levels`` for the full reasoning —
    this is the same correction, applied here because **this script produced the
    PF 1.60 headline** that the shadow arm exists to confirm or kill, using the
    published level as the fill. On a reversal bar that level is the prior
    trend's extreme, so every SAR trail exit filled at the bar's open instead of
    the stop price breached: mean **+0.222%** per exit in the trade's favour over
    820 real 15m flips. A bake-off number carrying that bias overstates the SAR
    arm specifically, while ``atr`` (own ratcheted trail) and ``supertrend``
    (close-based flip) are unaffected — so it also skewed the ranking between
    methods, not just the level. **Re-run before quoting PF 1.60 again.**
    """
    n = len(highs)
    published: List[Optional[float]] = [None] * n
    in_force: List[Optional[float]] = [None] * n
    if n < 2:
        return published, in_force
    up = highs[1] >= highs[0]
    af = step
    ep = highs[1] if up else lows[1]
    sar = lows[0] if up else highs[0]
    published[1] = sar
    for i in range(2, n):
        sar = sar + af * (ep - sar)
        if up:
            sar = min(sar, lows[i - 1], lows[i - 2])
            in_force[i] = sar
            if lows[i] < sar:
                up = False
                sar = ep
                ep = lows[i]
                af = step
            else:
                if highs[i] > ep:
                    ep = highs[i]
                    af = min(af + step, max_step)
        else:
            sar = max(sar, highs[i - 1], highs[i - 2])
            in_force[i] = sar
            if highs[i] > sar:
                up = True
                sar = ep
                ep = highs[i]
                af = step
            else:
                if lows[i] < ep:
                    ep = lows[i]
                    af = min(af + step, max_step)
        published[i] = sar
    return published, in_force


def parabolic_sar(
    highs: List[float], lows: List[float], step: float, max_step: float
) -> List[Optional[float]]:
    """Parabolic SAR (Wilder). Returns the stop-and-reverse level per bar.

    The **published** indicator series. A simulator wants the second return of
    ``parabolic_sar_levels`` — they differ on reversal bars.
    """
    return parabolic_sar_levels(highs, lows, step, max_step)[0]


@dataclass(frozen=True)
class TrailResult:
    method: str
    exited: bool
    result_pct: Optional[float]
    gross_pct: Optional[float]
    mfe_pct: Optional[float]
    exit_price: Optional[float]
    hold_mins: Optional[int]
    fee_pct: float
    funding_pct: float
    bars: int
    reason: str


def _stop_series(
    method: str, bars: List[Bar], period: int, mult: float, sar_step: float, sar_max: float
) -> Tuple[List[Optional[float]], Optional[List[Optional[int]]]]:
    highs = [b.high for b in bars]
    lows = [b.low for b in bars]
    closes = [b.close for b in bars]
    if method == "supertrend":
        line, direction = supertrend(highs, lows, closes, period, mult)
        return line, direction
    if method == "sar":
        # The stop in force per bar, not the published level — the caller uses
        # this series as a fill price. See ``parabolic_sar_levels``.
        return parabolic_sar_levels(highs, lows, sar_step, sar_max)[1], None
    return wilder_atr(highs, lows, closes, period), None


def simulate_trailing_exit(
    bars: List[Bar],
    entry_idx: int,
    entry: float,
    direction: str,
    method: str,
    *,
    period: int,
    mult: float,
    sar_step: float,
    sar_max: float,
    tf_min: int,
    fee_pct: float,
    funding_bps_per_8h: float,
) -> TrailResult:
    """Replay one signal from entry_idx under a trailing-only exit. Pure."""
    is_long = direction.upper() == "LONG"
    n = len(bars)
    if entry_idx >= n or entry <= 0:
        return TrailResult(method, False, None, None, None, None, None, 0.0, 0.0, 0, "no-data")

    series, st_dir = _stop_series(method, bars, period, mult, sar_step, sar_max)
    if series[entry_idx] is None:
        return TrailResult(method, False, None, None, None, None, None, 0.0, 0.0, 0, "no-data")

    best_fav = entry
    run_extreme = bars[entry_idx].high if is_long else bars[entry_idx].low
    trail: Optional[float] = None
    exit_price: Optional[float] = None
    exit_idx: Optional[int] = None
    reason = "open"

    for i in range(entry_idx, n):
        b = bars[i]
        lvl = series[i]

        if method == "atr":
            if lvl is None:
                continue
            if is_long:
                run_extreme = max(run_extreme, b.high)
                cand = run_extreme - mult * lvl
                trail = cand if trail is None else max(trail, cand)
            else:
                run_extreme = min(run_extreme, b.low)
                cand = run_extreme + mult * lvl
                trail = cand if trail is None else min(trail, cand)
            stop_level = trail
        elif method == "supertrend":
            stop_level = lvl
            assert st_dir is not None
            flipped = (is_long and st_dir[i] == -1) or (not is_long and st_dir[i] == 1)
            if flipped and i > entry_idx:
                exit_price = b.close
                exit_idx = i
                reason = "trail"
                break
            if is_long:
                best_fav = max(best_fav, b.high)
            else:
                best_fav = min(best_fav, b.low)
            continue
        else:  # sar
            stop_level = lvl
            if stop_level is None:
                continue

        if stop_level is not None and i > entry_idx:
            if is_long and b.low <= stop_level:
                exit_price = min(b.open, stop_level) if b.open < stop_level else stop_level
                exit_idx = i
                reason = "trail"
                break
            if (not is_long) and b.high >= stop_level:
                exit_price = max(b.open, stop_level) if b.open > stop_level else stop_level
                exit_idx = i
                reason = "trail"
                break

        if is_long:
            best_fav = max(best_fav, b.high)
        else:
            best_fav = min(best_fav, b.low)

    exited = exit_price is not None
    if not exited:
        exit_price = bars[-1].close
        exit_idx = n - 1
        reason = "open"

    if is_long:
        gross = (exit_price - entry) / entry * 100.0
        mfe = max(0.0, (best_fav - entry) / entry * 100.0)
    else:
        gross = (entry - exit_price) / entry * 100.0
        mfe = max(0.0, (entry - best_fav) / entry * 100.0)

    hold_mins = max(0, (exit_idx - entry_idx) * tf_min) if exit_idx is not None else 0
    funding = (funding_bps_per_8h / 100.0) * (hold_mins / 480.0)
    fee = fee_pct if exited else 0.0
    net = gross - fee - funding

    return TrailResult(
        method=method,
        exited=exited,
        result_pct=net,
        gross_pct=gross,
        mfe_pct=mfe,
        exit_price=exit_price,
        hold_mins=hold_mins,
        fee_pct=fee,
        funding_pct=funding,
        bars=(exit_idx - entry_idx + 1) if exit_idx is not None else 0,
        reason=reason,
    )


def find_entry_idx(bars: List[Bar], dispatch_ms: int, tf_min: int) -> Optional[int]:
    """First bar whose bucket covers dispatch_ms (mirrors dark_signals._simulate)."""
    bucket_ms = tf_min * _MINUTE_MS
    for i, b in enumerate(bars):
        if b.open_time_ms + bucket_ms > dispatch_ms:
            return i
    return None


# --------------------------------------------------------------------------- #
# Aggregation — pure, stdlib only. The robustness checks are the whole point.
# --------------------------------------------------------------------------- #
@dataclass
class SignalRecord:
    """One backtest entry with every exit method's realised net %."""

    symbol: str
    entry_ms: int
    direction: str
    setup_class: str
    regime: str
    entry: float
    # method -> net pct (None if that method couldn't seed / replay for this row)
    pnl: Dict[str, Optional[float]] = field(default_factory=dict)

    @property
    def timestamp(self) -> str:
        return datetime.fromtimestamp(self.entry_ms / 1000, tz=timezone.utc).isoformat()


def profit_factor(pnls: Sequence[float]) -> float:
    """Gross profit / gross loss. inf if no losers, 0.0 if no winners."""
    gains = sum(p for p in pnls if p > 0)
    losses = sum(-p for p in pnls if p < 0)
    if losses == 0:
        return math.inf if gains > 0 else 0.0
    return gains / losses


@dataclass
class MethodStats:
    method: str
    n: int
    total: float
    avg: float
    median: float
    win_rate: float
    pf: float
    # drop-top-N robustness: n -> (total_after_drop, pf_after_drop)
    drop_top: Dict[int, Tuple[float, float]]


def _pnls_for(records: Sequence[SignalRecord], method: str) -> List[float]:
    return [r.pnl[method] for r in records
            if r.pnl.get(method) is not None]  # type: ignore[misc]


def method_stats(records: Sequence[SignalRecord], method: str,
                 drop_ns: Sequence[int] = (1, 2, 3)) -> MethodStats:
    pnls = _pnls_for(records, method)
    n = len(pnls)
    if n == 0:
        return MethodStats(method, 0, 0.0, 0.0, 0.0, 0.0, 0.0, {k: (0.0, 0.0) for k in drop_ns})
    total = sum(pnls)
    wins = sum(1 for p in pnls if p > 0)
    ordered = sorted(pnls, reverse=True)
    drop_top: Dict[int, Tuple[float, float]] = {}
    for k in drop_ns:
        kept = ordered[k:] if k < n else []
        drop_top[k] = (sum(kept), profit_factor(kept))
    return MethodStats(
        method=method,
        n=n,
        total=total,
        avg=total / n,
        median=statistics.median(pnls),
        win_rate=wins / n * 100.0,
        pf=profit_factor(pnls),
        drop_top=drop_top,
    )


def per_regime_pf(records: Sequence[SignalRecord], method: str) -> Dict[str, Tuple[int, float, float]]:
    """regime -> (n, total, pf) for one method."""
    buckets: Dict[str, List[float]] = {}
    for r in records:
        v = r.pnl.get(method)
        if v is None:
            continue
        buckets.setdefault(r.regime or "UNKNOWN", []).append(v)
    return {reg: (len(vs), sum(vs), profit_factor(vs)) for reg, vs in sorted(buckets.items())}


# --------------------------------------------------------------------------- #
# Kline fetch (stdlib urllib; uses env proxies automatically). Run on the VPS.
# --------------------------------------------------------------------------- #
Row = Tuple[int, float, float, float, float, float]


class WeightPacer:
    """Self-throttle to a weight/min budget, and yield to live trading.

    Two mechanisms, because one is not enough here:

    * **Own budget** — a rolling-60s token bucket capped at ``per_min``. This is
      what keeps the job inside the headroom ``src/rate_limiter.py`` leaves free
      (it budgets the engine 2,200 of Binance's 2,400/min futures cap).
    * **Cooperation** — the engine's limiter lives in another process, so its
      counter is invisible here. But ``X-MBX-USED-WEIGHT-1M`` on every response
      is server-authoritative and covers *all* traffic from this IP, engine
      included. Reading it lets this job notice live trading eating the budget
      and stand down, without any shared memory.
    """

    def __init__(self, per_min: int = _DEFAULT_WEIGHT_PER_MIN, *,
                 yield_above: int = _YIELD_ABOVE_USED_WEIGHT,
                 now: Optional[Any] = None, sleep: Optional[Any] = None) -> None:
        self.per_min = max(_PAGE_WEIGHT, per_min)
        self.yield_above = yield_above
        # Clock injected so the throttling logic is testable without patching the
        # global time module (and without real multi-second sleeps in CI).
        self._now = now or time.monotonic
        self._sleep = sleep or time.sleep
        self._spent: Deque[Tuple[float, int]] = deque()
        self._last: Optional[float] = None
        self.waited_sec = 0.0
        self.yielded_sec = 0.0

    def _used(self, now: float) -> int:
        while self._spent and now - self._spent[0][0] >= 60.0:
            self._spent.popleft()
        return sum(w for _, w in self._spent)

    def spend(self, weight: int) -> None:
        """Block until ``weight`` fits — smoothly, never in a burst.

        Two guards. The **spacing** guard is the important one: a plain token
        bucket would let the job fire a whole minute's budget instantly and then
        idle, and ``src/rate_limiter.py`` records that burning the budget in a
        burst is precisely what trips Binance's hard 429 lockout (~42s at 100%
        usage) — which is why the engine's own limiter carries burst protection.
        Spacing requests at ``60 * weight / per_min`` spends the same budget as a
        flat trickle. The **window** guard then backstops it against drift.
        """
        gap = 60.0 * weight / float(self.per_min)
        now = self._now()

        # Spacing. Computed against the *scheduled* slot, then advanced to it —
        # never re-measured in a loop. Looping on `now - last < gap` spins
        # forever once the remainder rounds below a float ulp.
        if self._last is not None:
            target = self._last + gap
            if now < target:
                self.nap(target - now)
                now = max(self._now(), target)

        # Window backstop. Each pass sleeps >= 0.05s, so it always terminates.
        while self._spent and self._used(now) + weight > self.per_min:
            nap = min(60.0, max(0.05, 60.0 - (now - self._spent[0][0]) + 0.01))
            self.nap(nap)
            now = max(self._now(), now + nap)

        self._spent.append((now, weight))
        self._last = now

    def nap(self, seconds: float) -> None:
        """Sleep on the pacer's clock, counting it as throttled time."""
        self._sleep(seconds)
        self.waited_sec += seconds

    def observe(self, used_weight: Optional[int]) -> None:
        """React to IP-wide usage — back off when live traffic is near the cap."""
        if used_weight is None or used_weight < self.yield_above:
            return
        print(f"[pace] IP used-weight {used_weight}/{_FUTURES_WEIGHT_CAP} — "
              f"yielding {_YIELD_SLEEP_SEC:g}s to live traffic", file=sys.stderr)
        self._sleep(_YIELD_SLEEP_SEC)
        self.yielded_sec += _YIELD_SLEEP_SEC


def _as_int(v: Optional[str]) -> Optional[int]:
    try:
        return int(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def _get(url: str, timeout: float = 30.0) -> Tuple[Any, Optional[int]]:
    """GET returning (payload, IP-wide used weight from the response header)."""
    req = urllib.request.Request(url, headers={"User-Agent": "exit-backtest/1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
        used = _as_int(resp.headers.get("X-MBX-USED-WEIGHT-1M")
                       or resp.headers.get("X-MBX-USED-WEIGHT"))
        return payload, used


def _get_paced(url: str, pacer: WeightPacer, *, weight: int = _PAGE_WEIGHT) -> Any:
    """One paced, retrying request. Raises BinanceBanned on a ban (never retries it)."""
    delay = 1.0
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        pacer.spend(weight)
        try:
            payload, used = _get(url)
            pacer.observe(used)
            return payload
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")[:400]
            except Exception:  # noqa: BLE001 — diagnostics only
                pass
            if exc.code in _BAN_STATUSES:
                raise BinanceBanned(
                    f"HTTP {exc.code} from Binance — this IP is blocked/banned. "
                    f"Aborting so we do not deepen it. {body}") from exc
            if exc.code not in _RETRY_STATUSES or attempt == _MAX_ATTEMPTS:
                raise
            wait = _as_int(exc.headers.get("Retry-After")) if exc.headers else None
            nap = float(wait) if wait else delay
            print(f"[pace] HTTP {exc.code} — retry {attempt}/{_MAX_ATTEMPTS} "
                  f"in {nap:g}s", file=sys.stderr)
            pacer.nap(nap)
            delay = min(30.0, delay * 2)
        except urllib.error.URLError:
            if attempt == _MAX_ATTEMPTS:
                raise
            pacer.nap(delay)
            delay = min(30.0, delay * 2)
    raise RuntimeError("unreachable")


# --- On-disk kline cache ---------------------------------------------------- #
# Re-runs are the norm here: the whole point is sweeping exit methods and knobs
# over the SAME candles. Fetching 1.38M candles (~5,540 weight) again for every
# sweep is what turns a cheap question into a rate-limit incident, so closed
# candles are cached per (symbol, interval) and only the gap is fetched.
_CACHE_WARNED = False


def _cache_path(cache_dir: str, symbol: str, interval: str) -> str:
    return os.path.join(cache_dir, f"{symbol}_{interval}.csv.gz")


def _load_cache(path: str) -> List[Row]:
    try:
        with gzip.open(path, "rt", newline="") as fh:
            out: List[Row] = []
            for r in csv.reader(fh):
                try:
                    out.append((int(r[0]), float(r[1]), float(r[2]),
                                float(r[3]), float(r[4]), float(r[5])))
                except (IndexError, TypeError, ValueError):
                    continue
            return out
    except (OSError, EOFError, gzip.BadGzipFile):
        return []


def _save_cache(path: str, rows: Sequence[Row]) -> None:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = f"{path}.tmp"
        with gzip.open(tmp, "wt", newline="") as fh:
            csv.writer(fh).writerows(rows)
        os.replace(tmp, path)
    except OSError as exc:
        # Once, not once per symbol per timeframe — an unwritable cache dir is a
        # single fact, and repeating it 40x buries the run's real progress.
        global _CACHE_WARNED
        if not _CACHE_WARNED:
            _CACHE_WARNED = True
            print(f"[warn] kline cache disabled — cannot write {path} ({exc}). "
                  "The run continues but re-runs will refetch (and cost weight); "
                  "point --cache-dir at a writable path.", file=sys.stderr)


def _fetch_range(symbol: str, interval: str, start_ms: int, end_ms: int,
                 pacer: WeightPacer) -> List[Row]:
    """Paginated (open_ms, o, h, l, c, volume) for [start_ms, end_ms]. Ascending."""
    step_ms = _TF_MIN[interval] * _MINUTE_MS
    out: List[Row] = []
    cursor = start_ms
    # 6mo of 5m at 499/page is ~104 pages; cap generously but never unbounded.
    for _ in range(2000):
        if cursor > end_ms:
            break
        url = (f"{_FAPI}?symbol={symbol}&interval={interval}"
               f"&startTime={cursor}&endTime={end_ms}&limit={_PAGE_LIMIT}")
        rows = _get_paced(url, pacer)
        if not isinstance(rows, list) or not rows:
            break
        for row in rows:
            try:
                out.append((int(row[0]), float(row[1]), float(row[2]),
                            float(row[3]), float(row[4]), float(row[5])))
            except (IndexError, TypeError, ValueError):
                continue
        if len(rows) < _PAGE_LIMIT:
            break
        cursor = int(rows[-1][0]) + step_ms
    return out


def fetch_klines(
    symbol: str, interval: str, start_ms: int, end_ms: int, *,
    pacer: Optional[WeightPacer] = None, cache_dir: Optional[str] = None,
) -> List[Row]:
    """Closed candles for [start_ms, end_ms], served from cache where possible."""
    pacer = pacer or WeightPacer()
    step_ms = _TF_MIN[interval] * _MINUTE_MS
    # Never cache the still-forming bar — it would freeze a partial candle.
    closed_end = min(end_ms, int(time.time() * 1000) - step_ms)

    cached: List[Row] = _load_cache(_cache_path(cache_dir, symbol, interval)) \
        if cache_dir else []
    merged: Dict[int, Row] = {r[0]: r for r in cached}

    if cached:
        head, tail = cached[0][0], cached[-1][0]
        gaps = []
        if start_ms < head - step_ms:          # missing older history
            gaps.append((start_ms, head - step_ms))
        if closed_end > tail + step_ms:        # missing newer candles
            gaps.append((tail + step_ms, closed_end))
    else:
        gaps = [(start_ms, closed_end)] if closed_end > start_ms else []

    for g_start, g_end in gaps:
        for r in _fetch_range(symbol, interval, g_start, g_end, pacer):
            merged[r[0]] = r

    rows = [merged[k] for k in sorted(merged)]
    if cache_dir and gaps:
        _save_cache(_cache_path(cache_dir, symbol, interval),
                    [r for r in rows if r[0] <= closed_end])
    return [r for r in rows if start_ms <= r[0] <= end_ms]


# --------------------------------------------------------------------------- #
# Entry generation via the engine Backtester (lazy import — keeps the pure code
# above importable without numpy / the engine stack, for unit tests).
# --------------------------------------------------------------------------- #
def run_entries_for_symbol(
    symbol: str,
    entry_rows: List[Tuple[int, float, float, float, float, float]],
    *,
    lookahead: int,
    fee_pct: float,
) -> List[Dict[str, Any]]:
    """Run the Backtester over one symbol's entry-TF candles; return signal_details
    dicts augmented with the entry-candle open_time (candle_index -> open_ms)."""
    import numpy as np  # noqa: PLC0415 — lazy: VPS-only dep
    # Put the repo root (parent of scripts/) on the path from this file's
    # location, so the engine import works regardless of the caller's cwd (e.g.
    # `docker exec ... python /app/scripts/exit_method_backtest.py`).
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _root not in sys.path:
        sys.path.insert(0, _root)
    from src.backtester import Backtester  # noqa: PLC0415,E402

    open_ms = [r[0] for r in entry_rows]
    flat = {
        "open": np.asarray([r[1] for r in entry_rows], dtype=float),
        "high": np.asarray([r[2] for r in entry_rows], dtype=float),
        "low": np.asarray([r[3] for r in entry_rows], dtype=float),
        "close": np.asarray([r[4] for r in entry_rows], dtype=float),
        "volume": np.asarray([r[5] for r in entry_rows], dtype=float),
    }
    bt = Backtester(lookahead_candles=lookahead, fee_pct=fee_pct)
    results = bt.run(flat, symbol=symbol, tag_regimes=True)
    details: List[Dict[str, Any]] = []
    for res in results:
        for d in res.signal_details:
            ci = d.get("candle_index")
            if ci is None or ci < 0 or ci >= len(open_ms):
                continue
            d = dict(d)
            d["entry_ms"] = open_ms[ci]
            details.append(d)
    return details


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
@dataclass
class SimKnobs:
    entry_tf: str
    exit_tf: str
    period: int
    mult: float
    sar_step: float
    sar_max: float
    fee_pct: float
    funding_bps_per_8h: float
    lookahead: int
    max_forward_bars: int


def build_records_for_symbol(
    symbol: str,
    entry_rows: List[Tuple[int, float, float, float, float, float]],
    exit_rows: List[Tuple[int, float, float, float, float, float]],
    knobs: SimKnobs,
) -> List[SignalRecord]:
    """Generate entries for one symbol and replay every exit method on each."""
    exit_tf_min = _TF_MIN[knobs.exit_tf]
    bars = resample(exit_rows, exit_tf_min)
    if len(bars) < knobs.period + 2:
        return []

    details = run_entries_for_symbol(
        symbol, entry_rows, lookahead=knobs.lookahead, fee_pct=knobs.fee_pct,
    )

    records: List[SignalRecord] = []
    for d in details:
        setup = str(d.get("setup_class") or "").upper()
        if setup in ORDER_FLOW_SETUPS:
            continue  # klines can't reconstruct this trigger — exclude
        direction = str(d.get("direction") or "").upper()
        entry = float(d.get("entry") or 0.0)
        entry_ms = int(d["entry_ms"])
        if direction not in ("LONG", "SHORT") or entry <= 0:
            continue
        entry_idx = find_entry_idx(bars, entry_ms, exit_tf_min)
        if entry_idx is None:
            continue
        # Slice a per-signal window: warmup bars before entry so the indicator has
        # a value AT entry (a trail present from bar one), plus a bounded forward
        # window so a single trade can't "run to the end of the dataset" (mirrors
        # the ops tab's max-lookback bound).
        warm = min(entry_idx, max(knobs.period + 2, 60))
        fwd_end = (entry_idx + knobs.max_forward_bars + 1
                   if knobs.max_forward_bars > 0 else len(bars))
        sub = bars[entry_idx - warm: fwd_end]
        sub_entry_idx = warm

        rec = SignalRecord(
            symbol=symbol,
            entry_ms=entry_ms,
            direction=direction,
            setup_class=setup or "UNKNOWN",
            regime=str(d.get("regime") or "UNKNOWN"),
            entry=entry,
            pnl={},
        )
        # Engine baseline = backtester's own realised pnl.
        base = d.get("pnl_pct")
        rec.pnl["engine"] = float(base) if base is not None else None
        for m in TRAIL_METHODS:
            tr = simulate_trailing_exit(
                sub, sub_entry_idx, entry, direction, m,
                period=knobs.period, mult=knobs.mult,
                sar_step=knobs.sar_step, sar_max=knobs.sar_max,
                tf_min=exit_tf_min, fee_pct=knobs.fee_pct,
                funding_bps_per_8h=knobs.funding_bps_per_8h,
            )
            rec.pnl[m] = tr.result_pct if tr.reason != "no-data" else None
        records.append(rec)
    return records


def _fmt_pf(pf: float) -> str:
    return "inf" if pf == math.inf else f"{pf:.2f}"


def write_outputs(records: List[SignalRecord], knobs: SimKnobs, out_dir: str,
                  universe: Sequence[str], months: float) -> Tuple[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "signals.csv")
    md_path = os.path.join(out_dir, "summary.md")

    with open(csv_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["timestamp", "symbol", "direction", "setup_class", "regime", "entry"]
                   + [f"pnl_{m}" for m in ALL_METHODS])
        for r in sorted(records, key=lambda x: x.entry_ms):
            w.writerow([r.timestamp, r.symbol, r.direction, r.setup_class, r.regime,
                        f"{r.entry:.8g}"]
                       + [("" if r.pnl.get(m) is None else f"{r.pnl[m]:.4f}")
                          for m in ALL_METHODS])

    stats = {m: method_stats(records, m) for m in ALL_METHODS}
    lines: List[str] = []
    lines.append(f"# Exit-method bake-off — {len(records)} price-action entries")
    lines.append("")
    lines.append(f"- Window: ~{months:g} months, entry TF `{knobs.entry_tf}`, "
                 f"exit TF `{knobs.exit_tf}`")
    lines.append(f"- Universe ({len(universe)}): {', '.join(universe)}")
    lines.append(f"- SAR step/max: {knobs.sar_step}/{knobs.sar_max}; "
                 f"ATR/ST period {knobs.period}, mult {knobs.mult}")
    lines.append(f"- Fees {knobs.fee_pct}% round-trip, funding "
                 f"{knobs.funding_bps_per_8h}bps/8h; engine baseline lookahead "
                 f"{knobs.lookahead} bars")
    lines.append(f"- Excluded order-flow setups: {', '.join(sorted(ORDER_FLOW_SETUPS))}")
    lines.append("")
    lines.append("## Aggregate (net of fees + funding)")
    lines.append("")
    lines.append("| Method | N | Total % | Avg % | Median % | Win % | PF |")
    lines.append("|---|---|---|---|---|---|---|")
    for m in ALL_METHODS:
        s = stats[m]
        lines.append(f"| {METHOD_LABELS[m]} | {s.n} | {s.total:+.1f} | {s.avg:+.3f} "
                     f"| {s.median:+.3f} | {s.win_rate:.0f} | {_fmt_pf(s.pf)} |")
    lines.append("")
    lines.append("## Outlier robustness — drop the top N winners")
    lines.append("")
    lines.append("| Method | Full PF | Full total | Drop-1 PF / total | "
                 "Drop-2 PF / total | Drop-3 PF / total |")
    lines.append("|---|---|---|---|---|---|")
    for m in ALL_METHODS:
        s = stats[m]
        d1t, d1p = s.drop_top.get(1, (0.0, 0.0))
        d2t, d2p = s.drop_top.get(2, (0.0, 0.0))
        d3t, d3p = s.drop_top.get(3, (0.0, 0.0))
        lines.append(f"| {METHOD_LABELS[m]} | {_fmt_pf(s.pf)} | {s.total:+.1f} "
                     f"| {_fmt_pf(d1p)} / {d1t:+.1f} | {_fmt_pf(d2p)} / {d2t:+.1f} "
                     f"| {_fmt_pf(d3p)} / {d3t:+.1f} |")
    lines.append("")
    lines.append("## Per-regime profit factor")
    lines.append("")
    for m in ALL_METHODS:
        lines.append(f"### {METHOD_LABELS[m]}")
        lines.append("")
        lines.append("| Regime | N | Total % | PF |")
        lines.append("|---|---|---|---|")
        for reg, (n, tot, pf) in per_regime_pf(records, m).items():
            lines.append(f"| {reg} | {n} | {tot:+.1f} | {_fmt_pf(pf)} |")
        lines.append("")
    lines.append("## Read this honestly")
    lines.append("")
    lines.append("- Trust the **relative exit ranking + outlier robustness**, not "
                 "absolute PnL (klines-only entries, backtester ≠ live scanner).")
    lines.append("- SAR's edge is real only if it **survives drop-top-2** and its "
                 "**median is not negative**. If PF collapses toward ~1 once a "
                 "couple of winners are removed, it was luck — stop.")
    lines.append("- If it survives: promote to engine-side forward-shadow "
                 "measurement (dark-first + owner sign-off) before it touches a "
                 "live exit.")

    with open(md_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return csv_path, md_path


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--months", type=float, default=6.0, help="lookback window in months")
    p.add_argument("--pairs", type=str, default="",
                   help="comma-separated symbols (default: fixed liquid universe)")
    p.add_argument("--entry-tf", type=str, default="5m", choices=sorted(_TF_MIN),
                   help="timeframe the Backtester generates entries on")
    p.add_argument("--exit-tf", type=str, default="15m", choices=sorted(_TF_MIN),
                   help="timeframe the trailing-exit sim replays on")
    p.add_argument("--period", type=int, default=10, help="ATR/SuperTrend period")
    p.add_argument("--mult", type=float, default=3.0, help="ATR/SuperTrend multiplier")
    p.add_argument("--sar-step", type=float, default=0.02)
    p.add_argument("--sar-max", type=float, default=0.2)
    p.add_argument("--fee-pct", type=float, default=0.07, help="round-trip fee percent")
    p.add_argument("--funding-bps", type=float, default=1.0, help="funding bps / 8h")
    p.add_argument("--lookahead", type=int, default=20,
                   help="engine-baseline forward candles (Backtester lookahead)")
    p.add_argument("--max-forward-bars", type=int, default=192,
                   help="cap on exit-TF bars the trail may run (0 = unbounded)")
    p.add_argument("--out-dir", type=str, default="",
                   help="output dir (default scripts/out/exit_backtest_<ts>)")
    p.add_argument("--weight-per-min", type=int, default=_DEFAULT_WEIGHT_PER_MIN,
                   help="Binance request-weight/min this job may use. Default "
                        f"{_DEFAULT_WEIGHT_PER_MIN} = the headroom the engine's "
                        "limiter leaves free (it budgets 2,200 of 2,400). Raising "
                        "this eats into live trading's budget on the same IP.")
    p.add_argument("--cache-dir", type=str, default="",
                   help="on-disk kline cache; re-runs then cost ~0 weight. "
                        "Default: a 'kline_cache' dir beside --out-dir, which is "
                        "writable by construction (the run must write outputs "
                        "there anyway). An absolute path like /data is NOT a safe "
                        "default — that volume belongs to the ops container, and "
                        "this script runs inside the engine container.")
    p.add_argument("--no-cache", action="store_true",
                   help="ignore the kline cache and refetch everything")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    universe = tuple(s.strip().upper() for s in args.pairs.split(",") if s.strip()) \
        or DEFAULT_UNIVERSE
    knobs = SimKnobs(
        entry_tf=args.entry_tf, exit_tf=args.exit_tf, period=args.period,
        mult=args.mult, sar_step=args.sar_step, sar_max=args.sar_max,
        fee_pct=args.fee_pct, funding_bps_per_8h=args.funding_bps,
        lookahead=args.lookahead, max_forward_bars=args.max_forward_bars,
    )
    out_dir = args.out_dir or os.path.join(
        "scripts", "out", f"exit_backtest_{int(time.time())}")

    now_ms = int(time.time() * 1000)
    start_ms = now_ms - int(args.months * 30 * 24 * 3600 * 1000)

    pacer = WeightPacer(args.weight_per_min)
    # Sit the cache beside the outputs. ops invokes with
    # --out-dir /app/scripts/out/ops_<ts>, so this lands at
    # /app/scripts/out/kline_cache — stable across runs, and writable for the
    # same reason the outputs are.
    cache_dir = None if args.no_cache else (
        args.cache_dir or os.path.join(os.path.dirname(os.path.abspath(out_dir)),
                                       "kline_cache")
    )
    print(f"[pace] budget {pacer.per_min} weight/min "
          f"(IP cap {_FUTURES_WEIGHT_CAP}, engine reserves 2,200); "
          f"page limit {_PAGE_LIMIT} (weight {_PAGE_WEIGHT}); "
          f"cache {cache_dir or 'OFF'}", file=sys.stderr)

    all_records: List[SignalRecord] = []
    for sym in universe:
        try:
            entry_rows = fetch_klines(sym, args.entry_tf, start_ms, now_ms,
                                      pacer=pacer, cache_dir=cache_dir)
            if args.exit_tf == args.entry_tf:
                exit_rows = entry_rows
            else:
                exit_rows = fetch_klines(sym, args.exit_tf, start_ms, now_ms,
                                         pacer=pacer, cache_dir=cache_dir)
        except BinanceBanned as exc:
            # Every remaining symbol would hit the same wall; continuing is what
            # turns a rate-limit into a longer ban on the live trading IP.
            print(f"[error] {exc}", file=sys.stderr)
            print("[error] aborting run — retry once the ban window clears",
                  file=sys.stderr)
            return 2
        except Exception as exc:  # noqa: BLE001 — per-symbol degrade, keep going
            print(f"[warn] {sym}: fetch failed ({type(exc).__name__}: {exc}); skipping",
                  file=sys.stderr)
            continue
        if len(entry_rows) < 200 or len(exit_rows) < 60:
            print(f"[warn] {sym}: too few candles "
                  f"(entry={len(entry_rows)}, exit={len(exit_rows)}); skipping",
                  file=sys.stderr)
            continue
        recs = build_records_for_symbol(sym, entry_rows, exit_rows, knobs)
        # flush: this is the only progress a long run emits, and the ops runner
        # shows it live — buffering it defeats the purpose.
        print(f"[ok] {sym}: {len(recs)} price-action entries", file=sys.stderr,
              flush=True)
        all_records.extend(recs)

    print(f"[pace] done — {pacer.waited_sec:.0f}s throttled, "
          f"{pacer.yielded_sec:.0f}s yielded to live traffic", file=sys.stderr)

    if not all_records:
        print("[error] no entries generated — check universe / window / Binance "
              "reachability (this box may be geo-blocked; run on the VPS)",
              file=sys.stderr)
        return 1

    csv_path, md_path = write_outputs(all_records, knobs, out_dir, universe, args.months)
    print(f"\nWrote {len(all_records)} signals -> {csv_path}")
    print(f"Summary -> {md_path}\n")
    # Echo the aggregate to stdout for a quick read.
    for m in ALL_METHODS:
        s = method_stats(all_records, m)
        print(f"  {METHOD_LABELS[m]:26s} n={s.n:5d} total={s.total:+8.1f} "
              f"avg={s.avg:+.3f} median={s.median:+.3f} win={s.win_rate:4.0f}% "
              f"PF={_fmt_pf(s.pf)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
