"""Strategy × Context edge matrix (Layer C backbone).

The autonomous allocator (Layer D) chooses which strategies to run *in the current
market context* by reading their **measured edge in that context** — not by opinion.
This module is the rolling, persisted store that answers, on real data:

    "For strategy S, when the market context was K, what was the edge?"

It mirrors ``CohortEdgeStore`` (``src/stat_filter.py``) exactly in persistence and
Wilson-bounded expectancy discipline — the same proven pattern — but is keyed by
``(strategy, context_key)`` where ``context_key`` comes from
``MarketContext.context_key()`` (session / phase / volatility / rotation).

Cost Discipline: ``record()`` is called on **outcome resolution** (dozens/day, off the
scan hot path), and only then is the JSON persisted — never on the per-scan loop.  The
in-memory read (``edge_r`` / ``matrix``) the allocator uses is O(1) dict + small deque.

Everything fails toward "insufficient data" (``None`` edge), so a cold or thin cell
never fabricates an edge — the allocator treats unknown cells as un-promotable.
"""
from __future__ import annotations

import json
import os
import threading
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Deque, Dict, Optional, Tuple

from src.stat_filter import wilson_lower_bound
from src.utils import get_logger

log = get_logger("strategy_edge")


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        return default


# Verdict bands on Wilson-bounded expectancy in R-units per trade.
_EDGE_STRONG_R: float = float(os.getenv("STRATEGY_EDGE_STRONG_R", "0.25"))
_EDGE_POSITIVE_R: float = float(os.getenv("STRATEGY_EDGE_POSITIVE_R", "0.05"))
_EDGE_NEGATIVE_R: float = float(os.getenv("STRATEGY_EDGE_NEGATIVE_R", "-0.05"))

VERDICT_STRONG = "STRONG"
VERDICT_POSITIVE = "POSITIVE"
VERDICT_FLAT = "FLAT"
VERDICT_NEGATIVE = "NEGATIVE"
VERDICT_INSUFFICIENT = "INSUFFICIENT_DATA"

# Outcome provenance — a matrix cell must be honest about how much of its edge is
# realised (emitted trades) vs counterfactual (gate-suppressed candidates) vs
# hypothetical (shadow-only strategy units that can never emit).
SOURCE_EMITTED = "emitted"
SOURCE_SUPPRESSED = "suppressed"
SOURCE_SHADOW = "shadow"


@dataclass
class StrategyOutcome:
    """A single resolved shadow/live trade attributed to a strategy × context cell."""

    strategy: str
    context_key: str
    side: str                 # LONG | SHORT
    won: bool                 # net-of-fees win
    pnl_pct: float            # realised PnL %, net of fees
    r_multiple: float         # realised PnL ÷ initial risk (R)
    mfe_pct: float = 0.0      # max favourable excursion %, for capture analysis
    source: str = SOURCE_EMITTED  # emitted | suppressed | shadow


@dataclass
class _Record:
    won: bool
    pnl_pct: float
    r_multiple: float
    mfe_pct: float
    timestamp: datetime
    source: str = SOURCE_EMITTED


class StrategyEdgeStore:
    """Rolling per-(strategy, context_key) outcome store with Wilson-bounded edge."""

    def __init__(
        self,
        window: Optional[int] = None,
        min_samples: Optional[int] = None,
        persist_path: Optional[str] = None,
    ) -> None:
        self._window: int = window if window is not None else _env_int("STRATEGY_EDGE_WINDOW", 50)
        self._min_samples: int = (
            min_samples if min_samples is not None else _env_int("STRATEGY_EDGE_MIN_SAMPLES", 15)
        )
        self._lock = threading.Lock()
        self._records: Dict[Tuple[str, str], Deque[_Record]] = defaultdict(
            lambda: deque(maxlen=self._window)
        )
        # Empty persist_path disables disk I/O entirely (tests).
        self._persist_path: str = (
            persist_path
            if persist_path is not None
            else os.environ.get("STRATEGY_EDGE_PERSIST_PATH", "data/strategy_edge_store.json")
        )
        if self._persist_path:
            self._load()

    @staticmethod
    def _key(strategy: str, context_key: str) -> Tuple[str, str]:
        return ((strategy or "UNKNOWN").upper(), context_key or "UNKNOWN")

    # ---- write (off the hot path — outcome resolution only) ----------------

    def record(self, outcome: StrategyOutcome) -> None:
        key = self._key(outcome.strategy, outcome.context_key)
        rec = _Record(
            won=bool(outcome.won),
            pnl_pct=float(outcome.pnl_pct),
            r_multiple=float(outcome.r_multiple),
            mfe_pct=float(outcome.mfe_pct),
            timestamp=datetime.now(timezone.utc),
            source=(outcome.source or SOURCE_EMITTED).lower(),
        )
        with self._lock:
            self._records[key].append(rec)
        self._save()

    # ---- read (O(1), what the allocator uses) ------------------------------

    def edge_r(self, strategy: str, context_key: str, z: float = 1.96) -> Optional[float]:
        """Wilson-lower-bounded expectancy in R per trade, or ``None`` if too few samples.

        Pessimistic on the win term (Wilson-LB win rate), honest on the loss term — so a
        thin cell can't fake a positive edge and get auto-promoted.
        """
        key = self._key(strategy, context_key)
        with self._lock:
            records = self._records.get(key)
            if records is None or len(records) < self._min_samples:
                return None
            n = len(records)
            wins = [r for r in records if r.won]
            losses = [r for r in records if not r.won]
            wr = len(wins) / n
            wlb = wilson_lower_bound(len(wins), n, z)
            avg_win_r = sum(r.r_multiple for r in wins) / len(wins) if wins else 0.0
            avg_loss_r = sum(r.r_multiple for r in losses) / len(losses) if losses else 0.0
            return wlb * avg_win_r + (1.0 - wr) * avg_loss_r

    def sample_count(self, strategy: str, context_key: str) -> int:
        key = self._key(strategy, context_key)
        with self._lock:
            records = self._records.get(key)
            return len(records) if records else 0

    def verdict(self, strategy: str, context_key: str) -> str:
        edge = self.edge_r(strategy, context_key)
        if edge is None:
            return VERDICT_INSUFFICIENT
        if edge >= _EDGE_STRONG_R:
            return VERDICT_STRONG
        if edge >= _EDGE_POSITIVE_R:
            return VERDICT_POSITIVE
        if edge <= _EDGE_NEGATIVE_R:
            return VERDICT_NEGATIVE
        return VERDICT_FLAT

    def matrix(self) -> Dict[str, Dict]:
        """Full Strategy×Context matrix for the ops dashboard (Layer F).

        Keyed ``"STRATEGY|context_key"`` → per-cell stats.  Cells with no outcomes are
        omitted.  Edge/verdict are ``None``/INSUFFICIENT until the sample floor is met.
        """
        out: Dict[str, Dict] = {}
        with self._lock:
            snapshot = {k: list(v) for k, v in self._records.items() if v}
        for (strategy, ctx), records in snapshot.items():
            n = len(records)
            wins = sum(1 for r in records if r.won)
            avg_pnl = sum(r.pnl_pct for r in records) / n
            avg_r = sum(r.r_multiple for r in records) / n
            mfe_records = [r for r in records if r.mfe_pct > 0]
            capture = (
                sum(r.pnl_pct for r in mfe_records) / sum(r.mfe_pct for r in mfe_records)
                if mfe_records and sum(r.mfe_pct for r in mfe_records) > 0
                else 0.0
            )
            out[f"{strategy}|{ctx}"] = {
                "strategy": strategy,
                "context_key": ctx,
                "n": n,
                "n_emitted": sum(1 for r in records if r.source == SOURCE_EMITTED),
                "n_suppressed": sum(1 for r in records if r.source == SOURCE_SUPPRESSED),
                "n_shadow": sum(1 for r in records if r.source == SOURCE_SHADOW),
                "win_rate": wins / n,
                "avg_pnl_pct": avg_pnl,
                "avg_r": avg_r,
                "mfe_capture": capture,
                "edge_r": self.edge_r(strategy, ctx),
                "verdict": self.verdict(strategy, ctx),
                "last_updated": max(r.timestamp for r in records).isoformat(),
            }
        return out

    # ---- persistence (mirrors CohortEdgeStore) -----------------------------

    def _load(self) -> None:
        try:
            if not os.path.exists(self._persist_path):
                return
            with open(self._persist_path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            with self._lock:
                for key_str, recs in raw.items():
                    parts = key_str.split("|", 1)
                    if len(parts) != 2:
                        continue
                    dq = self._records[(parts[0], parts[1])]
                    for r in recs[-self._window:]:
                        dq.append(
                            _Record(
                                won=bool(r.get("won")),
                                pnl_pct=float(r.get("pnl_pct", 0.0)),
                                r_multiple=float(r.get("r", 0.0)),
                                mfe_pct=float(r.get("mfe", 0.0)),
                                timestamp=datetime.fromisoformat(r["ts"])
                                if r.get("ts")
                                else datetime.now(timezone.utc),
                                # Pre-provenance store files load as emitted.
                                source=str(r.get("src", SOURCE_EMITTED)),
                            )
                        )
        except Exception:
            # Never block boot on a bad store file (fail-open).
            pass

    def _save(self) -> None:
        if not self._persist_path:
            return
        try:
            with self._lock:
                payload = {
                    f"{strategy}|{ctx}": [
                        {
                            "won": r.won,
                            "pnl_pct": r.pnl_pct,
                            "r": r.r_multiple,
                            "mfe": r.mfe_pct,
                            "ts": r.timestamp.isoformat(),
                            "src": r.source,
                        }
                        for r in records
                    ]
                    for (strategy, ctx), records in self._records.items()
                    if records
                }
            dirname = os.path.dirname(self._persist_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            tmp = self._persist_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, self._persist_path)
        except Exception:
            # Persistence is best-effort; the in-memory store stays correct.
            pass


# Module-global singleton, mirroring _cohort_edge_store in the scanner.
_strategy_edge_store: Optional[StrategyEdgeStore] = None


def get_strategy_edge_store() -> StrategyEdgeStore:
    global _strategy_edge_store
    if _strategy_edge_store is None:
        _strategy_edge_store = StrategyEdgeStore()
    return _strategy_edge_store
