"""Statistical false-positive filter using rolling win-rate tracking.

Tracks per-(channel, pair, regime) rolling win rates and applies adaptive
confidence penalties or hard suppression when quality drops below thresholds.

Uses Wilson score lower bound for conservative threshold comparison —
requires statistical confidence before penalising.

Thresholds are configurable via environment variables:

  STAT_FILTER_WINDOW            Rolling window size (default: 30)
  STAT_FILTER_MIN_SAMPLES       Minimum outcomes before filtering (default: 15)
  STAT_FILTER_HARD_SUPPRESS_WR  Hard suppress threshold as % (default: 25)
  STAT_FILTER_SOFT_PENALTY_WR   Soft penalty threshold as % (default: 45)
  STAT_FILTER_SOFT_PENALTY_PTS  Confidence points deducted (default: 10.0)
"""
from __future__ import annotations

import os
import threading
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Deque, Dict, List, Optional, Tuple

from src.confidence_calibration import wilson_lower_bound


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


@dataclass
class SignalOutcome:
    """Record of a single resolved signal for win-rate tracking."""

    signal_id: str
    channel: str
    pair: str
    regime: str
    setup_class: str
    won: bool        # True if TP1 or higher was hit; False if SL hit or expired
    pnl_pct: float   # Actual PnL % achieved
    # Extended cohort fields — empty-string / NEUTRAL defaults maintain backward
    # compatibility with existing callers that pre-date the CohortEdgeStore.
    side: str = ""          # "LONG" or "SHORT"; empty = unknown (legacy callers)
    macro_dir: str = "NEUTRAL"  # BTC weekly macro regime at emit (BULL/RECOVERY/NEUTRAL/DECLINE)


@dataclass
class _OutcomeRecord:
    """Internal storage unit — won flag, PnL, and resolution timestamp."""

    won: bool
    pnl_pct: float
    timestamp: datetime


class RollingWinRateStore:
    """Thread-safe rolling win-rate store per (channel, pair, regime) key.

    Uses a fixed-size deque per key so memory is bounded regardless of
    how many signals are recorded.
    """

    def __init__(
        self,
        window: Optional[int] = None,
        min_samples: Optional[int] = None,
    ) -> None:
        self._window: int = window if window is not None else _env_int("STAT_FILTER_WINDOW", 30)
        self._min_samples: int = (
            min_samples if min_samples is not None else _env_int("STAT_FILTER_MIN_SAMPLES", 15)
        )
        self._lock = threading.Lock()
        # Key: (channel, pair, regime) → deque of _OutcomeRecord
        self._records: Dict[Tuple[str, str, str], Deque[_OutcomeRecord]] = defaultdict(
            lambda: deque(maxlen=self._window)
        )

    def record(self, outcome: SignalOutcome) -> None:
        """Record the outcome of a resolved signal."""
        key = (outcome.channel, outcome.pair, outcome.regime)
        rec = _OutcomeRecord(
            won=outcome.won,
            pnl_pct=outcome.pnl_pct,
            timestamp=datetime.now(timezone.utc),
        )
        with self._lock:
            self._records[key].append(rec)

    def win_rate(self, channel: str, pair: str, regime: str) -> Optional[float]:
        """Return rolling win rate (0.0–1.0) or None if below min_samples.

        Returns None when there is insufficient history to make a judgment
        (fail-open behaviour).
        """
        key = (channel, pair, regime)
        with self._lock:
            records = self._records.get(key)
            if records is None or len(records) < self._min_samples:
                return None
            return sum(1 for r in records if r.won) / len(records)

    def stats(self, channel: str, pair: str, regime: str) -> Dict:
        """Return statistics dict for a specific (channel, pair, regime) key.

        Returns
        -------
        dict with keys: win_rate (float), n (int), avg_pnl (float),
        last_updated (datetime).  win_rate is 0.0 when n == 0.
        """
        key = (channel, pair, regime)
        with self._lock:
            records = self._records.get(key)
            if not records:
                return {
                    "win_rate": 0.0,
                    "n": 0,
                    "avg_pnl": 0.0,
                    "last_updated": None,
                }
            n = len(records)
            wr = sum(1 for r in records if r.won) / n
            avg_pnl = sum(r.pnl_pct for r in records) / n
            last_updated = max(r.timestamp for r in records)
            return {
                "win_rate": wr,
                "n": n,
                "avg_pnl": avg_pnl,
                "last_updated": last_updated,
            }

    def all_stats(self) -> Dict[str, Dict]:
        """Return stats for all tracked keys that have at least one outcome."""
        out: Dict[str, Dict] = {}
        with self._lock:
            for (ch, pair, regime), records in self._records.items():
                if not records:
                    continue
                n = len(records)
                wr = sum(1 for r in records if r.won) / n
                avg_pnl = sum(r.pnl_pct for r in records) / n
                last_updated = max(r.timestamp for r in records)
                key = f"{ch}/{pair}/{regime}"
                out[key] = {
                    "channel": ch,
                    "pair": pair,
                    "regime": regime,
                    "win_rate": wr,
                    "n": n,
                    "avg_pnl": avg_pnl,
                    "last_updated": last_updated,
                }
        return out

    def wilson_lower(self, channel: str, pair: str, regime: str, z: float = 1.96) -> Optional[float]:
        """Return Wilson score lower bound (0.0-1.0) or None if below min_samples."""
        key = (channel, pair, regime)
        with self._lock:
            records = self._records.get(key)
            if records is None or len(records) < self._min_samples:
                return None
            wins = sum(1 for r in records if r.won)
            return wilson_lower_bound(wins, len(records), z)

    def all_keys(self) -> List[Tuple[str, str, str]]:
        """Return all (channel, pair, regime) keys that have recorded outcomes."""
        with self._lock:
            return list(self._records.keys())


class CohortEdgeStore:
    """Rolling outcome store keyed by (setup_class, side, regime_family, macro_dir).

    regime_family: 'QUIET' when the local 5m regime is quiet/low-volatility,
                   'ACTIVE' otherwise.
    macro_dir:     BTC weekly macro regime at signal emit — one of BULL / RECOVERY /
                   NEUTRAL / DECLINE (from btc_state.macro_direction()).

    This is the STEP 1 (observe-only) data collection layer for the cohort-edge
    ranker described in docs/SCORING_AUDIT_2026_07_03.md.  No live decisions are
    made here yet — the store records outcomes so the shadow-logged verdicts can be
    validated against realised P&L before STEP 2 activation.

    Edge formula (Wilson-lower-bounded expectancy — small samples are penalised):
        expectancy = WLB(WR) × avg_win_pnl  +  (1 − WR) × avg_loss_pnl
    """

    # Local 5m regime labels that map to the 'QUIET' family.
    _QUIET_REGIMES: frozenset = frozenset({
        "QUIET", "CHOPPY", "LOW_VOL", "RANGING_LOW_ADX", "RANGING",
    })

    def __init__(
        self,
        window: Optional[int] = None,
        min_samples: Optional[int] = None,
    ) -> None:
        self._window: int = window if window is not None else _env_int("COHORT_EDGE_WINDOW", 30)
        self._min_samples: int = (
            min_samples if min_samples is not None else _env_int("COHORT_EDGE_MIN_SAMPLES", 10)
        )
        self._lock = threading.Lock()
        # Key: (setup_class, side, regime_family, macro_dir) → deque of _OutcomeRecord
        self._records: Dict[Tuple[str, str, str, str], Deque[_OutcomeRecord]] = defaultdict(
            lambda: deque(maxlen=self._window)
        )

    @classmethod
    def regime_family(cls, regime: str) -> str:
        """Collapse fine-grained regime labels to QUIET vs ACTIVE family."""
        return "QUIET" if regime.upper() in cls._QUIET_REGIMES else "ACTIVE"

    def cohort_key(
        self, setup_class: str, side: str, regime: str, macro_dir: str,
    ) -> Tuple[str, str, str, str]:
        return (
            (setup_class or "UNKNOWN").upper(),
            (side or "UNKNOWN").upper(),
            self.regime_family(regime),
            (macro_dir or "NEUTRAL").upper(),
        )

    def record(self, outcome: SignalOutcome) -> None:
        """Record the outcome of a resolved signal into the cohort store."""
        key = self.cohort_key(outcome.setup_class, outcome.side, outcome.regime, outcome.macro_dir)
        rec = _OutcomeRecord(
            won=outcome.won,
            pnl_pct=outcome.pnl_pct,
            timestamp=datetime.now(timezone.utc),
        )
        with self._lock:
            self._records[key].append(rec)

    def expectancy(
        self,
        setup_class: str,
        side: str,
        regime: str,
        macro_dir: str,
        z: float = 1.96,
    ) -> Optional[float]:
        """Return Wilson-lower-bounded expectancy (% per trade) or None if no history.

        Positive = edge on this cohort, negative = negative expectancy.
        None = insufficient samples (fail-open; caller should emit with no penalty).
        """
        key = self.cohort_key(setup_class, side, regime, macro_dir)
        with self._lock:
            records = self._records.get(key)
            if records is None or len(records) < self._min_samples:
                return None
            wins = [r for r in records if r.won]
            losses = [r for r in records if not r.won]
            n = len(records)
            wr = len(wins) / n
            wlb = wilson_lower_bound(len(wins), n, z)
            avg_win = sum(r.pnl_pct for r in wins) / len(wins) if wins else 0.0
            avg_loss = sum(r.pnl_pct for r in losses) / len(losses) if losses else 0.0
            # Wilson-lower-bound on WR (pessimistic WR for the win term),
            # but raw WR for the loss weight (if anything under-penalises losses).
            return wlb * avg_win + (1.0 - wr) * avg_loss

    def sample_count(self, setup_class: str, side: str, regime: str, macro_dir: str) -> int:
        """Return the number of outcomes recorded for this cohort."""
        key = self.cohort_key(setup_class, side, regime, macro_dir)
        with self._lock:
            records = self._records.get(key)
            return len(records) if records else 0

    def shadow_verdict(
        self,
        setup_class: str,
        side: str,
        regime: str,
        macro_dir: str,
    ) -> str:
        """Return a shadow verdict string for [SHADOW] COHORT_EDGE logging.

        would-emit:no_history  — insufficient samples, fail-open
        would-emit:edge=X%:n=N — positive measured expectancy
        would-suppress:edge=X%:n=N — negative measured expectancy (enough samples)
        """
        exp = self.expectancy(setup_class, side, regime, macro_dir)
        n = self.sample_count(setup_class, side, regime, macro_dir)
        if exp is None:
            return f"would-emit:no_history:n={n}"
        key_str = "/".join(self.cohort_key(setup_class, side, regime, macro_dir))
        if exp < 0:
            return f"would-suppress:edge={exp:.3f}%:n={n}:key={key_str}"
        return f"would-emit:edge={exp:.3f}%:n={n}:key={key_str}"

    def all_stats(self) -> Dict[str, Dict]:
        """Return stats for all tracked cohorts that have at least one outcome."""
        out: Dict[str, Dict] = {}
        with self._lock:
            for (setup, side, fam, macro), records in self._records.items():
                if not records:
                    continue
                n = len(records)
                wr = sum(1 for r in records if r.won) / n
                avg_pnl = sum(r.pnl_pct for r in records) / n
                key = f"{setup}/{side}/{fam}/{macro}"
                out[key] = {
                    "setup": setup,
                    "side": side,
                    "regime_family": fam,
                    "macro_dir": macro,
                    "win_rate": wr,
                    "n": n,
                    "avg_pnl": avg_pnl,
                    "last_updated": max(r.timestamp for r in records),
                }
        return out


class StatisticalFilter:
    """Applies adaptive confidence gates based on rolling win-rate statistics.

    Gate logic (thresholds configurable via env vars; WR = win rate):
    ────────────────────────────────────────────────────────────
    WR >= SOFT_PENALTY_WR          → pass (no penalty)
    HARD_SUPPRESS_WR <= WR < SOFT_PENALTY_WR → soft penalty (-PENALTY_PTS confidence)
    WR < HARD_SUPPRESS_WR          → HARD SUPPRESS (signal dropped)
    None (no history)              → pass (fail-open)
    ────────────────────────────────────────────────────────────

    Default thresholds (overridable via env vars):
      Hard suppress: WR < 25%  (STAT_FILTER_HARD_SUPPRESS_WR)
      Soft penalty:  WR < 45%  (STAT_FILTER_SOFT_PENALTY_WR)
      Penalty pts:   -10.0     (STAT_FILTER_SOFT_PENALTY_PTS)
    """

    def __init__(self, store: Optional[RollingWinRateStore] = None) -> None:
        self._store = store or RollingWinRateStore()
        self._hard_suppress_wr: float = _env_float("STAT_FILTER_HARD_SUPPRESS_WR", 25.0) / 100.0
        self._soft_penalty_wr: float = _env_float("STAT_FILTER_SOFT_PENALTY_WR", 45.0) / 100.0
        self._soft_penalty_pts: float = _env_float("STAT_FILTER_SOFT_PENALTY_PTS", 10.0)

    @property
    def store(self) -> RollingWinRateStore:
        return self._store

    def check(
        self,
        channel: str,
        pair: str,
        regime: str,
        current_confidence: float,
    ) -> Tuple[bool, float, str]:
        """Check whether the signal should be emitted based on rolling win rate.

        Parameters
        ----------
        channel, pair, regime:
            Signal identifiers for win-rate lookup.
        current_confidence:
            Signal confidence score (0–100).

        Returns
        -------
        (allow: bool, adjusted_confidence: float, reason: str)
            allow: False means the signal should be suppressed.
            adjusted_confidence: confidence after penalty (may be unchanged).
            reason: human-readable explanation for logs.
        """
        win_rate = self._store.wilson_lower(channel, pair, regime)

        if win_rate is None:
            return True, current_confidence, "no_history"

        wr_pct = f"{win_rate:.1%}"

        if win_rate < self._hard_suppress_wr:
            return False, 0.0, f"hard_suppress:wilson={wr_pct}"

        if win_rate < self._soft_penalty_wr:
            adj = max(0.0, current_confidence - self._soft_penalty_pts)
            return True, adj, f"soft_penalty:wilson={wr_pct}"

        return True, current_confidence, f"ok:wilson={wr_pct}"

    def record(self, outcome: SignalOutcome) -> None:
        """Forward a resolved signal outcome to the underlying win-rate store."""
        self._store.record(outcome)

    def format_statstats(self) -> str:
        """Format win-rate stats as a Telegram-friendly table for /statstats.

        Returns a string with a table showing Channel | Pair | Regime | WR% | N | Avg PnL.
        """
        all_stats = self._store.all_stats()
        if not all_stats:
            return "📊 *Statistical Filter Stats*\n\nNo outcomes recorded yet."

        # Column widths must match the header format string below.
        _COL_SEP_LEN: int = 61  # 14+1+10+1+14+1+6+1+4+1+8

        lines = ["📊 *Statistical Filter Stats*\n"]
        lines.append("```")
        lines.append(f"{'Channel':<14} {'Pair':<10} {'Regime':<14} {'WR%':>6} {'N':>4} {'AvgPnL%':>8}")
        lines.append("-" * _COL_SEP_LEN)
        for _key, s in sorted(all_stats.items()):
            wr_pct = f"{s['win_rate'] * 100:.1f}%"
            avg_pnl = f"{s['avg_pnl']:+.2f}%"
            lines.append(
                f"{s['channel']:<14} {s['pair']:<10} {s['regime']:<14} "
                f"{wr_pct:>6} {s['n']:>4} {avg_pnl:>8}"
            )
        lines.append("```")
        return "\n".join(lines)
