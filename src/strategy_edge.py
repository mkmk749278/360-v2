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

#: Reserved top-level key in the persisted store holding per-cell eviction
#: counts.  Cell keys are ``"STRATEGY|context_key"`` and ``_key`` upper-cases
#: the strategy, so a key containing no ``"|"`` can never collide with one.
_EVICTED_KEY = "__evicted__"


@dataclass
class StrategyOutcome:
    """A single resolved shadow/live trade attributed to a strategy × context cell."""

    strategy: str
    context_key: str
    side: str                 # LONG | SHORT
    won: bool                 # reached TP1 before SL (outcome, not profitability)
    pnl_pct: float            # realised PnL %, net of costs when the cost model is on
    r_multiple: float         # realised PnL ÷ initial risk (R), net of costs when on
    mfe_pct: float = 0.0      # max favourable excursion %, for capture analysis
    source: str = SOURCE_EMITTED  # emitted | suppressed | shadow
    # Pre-cost R carried alongside the (possibly netted) r_multiple so the W2
    # reconciliation can show the optimism tax.  None → gross == r_multiple.
    gross_r_multiple: Optional[float] = None
    # Always-netted R (flag-independent) — lets the reconciliation show net edge
    # while the live path (r_multiple) stays gross until sign-off.  None → == r_multiple.
    net_r_multiple: Optional[float] = None


@dataclass
class _Record:
    won: bool
    pnl_pct: float
    r_multiple: float
    mfe_pct: float
    timestamp: datetime
    source: str = SOURCE_EMITTED
    gross_r_multiple: float = 0.0  # pre-cost R (== r_multiple when cost model off)
    net_r_multiple: float = 0.0    # always-netted R (flag-independent)


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
        #: Per-cell count of outcomes pushed out of the ring by ``maxlen``.
        #:
        #: Every cell here is a ``deque(maxlen=50)``, so ``len(records)`` is
        #: ``min(actual, 50)`` and a cell reading ``n=50`` may stand for fifty
        #: outcomes or five thousand.  Until 2026-08-04 nothing counted the
        #: difference and nothing published it, so every verdict on this matrix
        #: was a sample of unknown size presented as a population — including
        #: the ones Layer C's emission floor and Layer G's promotions route on.
        #:
        #: This is the Suppression Quality Audit's ring problem one subsystem
        #: over: that store already computes eviction counts and renders them
        #: beside its verdicts (``CLAUDE.md``: *"when a bounded buffer feeds a
        #: statistic, persist the eviction count with the data and put the
        #: denominator beside the verdict"*).  The edge matrix has the same
        #: shape at an eighth of the window and never got the same treatment.
        #:
        #: Counted here rather than derived, because it cannot be derived: once
        #: a record is evicted nothing downstream can tell it ever existed.
        self._evicted: Dict[Tuple[str, str], int] = defaultdict(int)
        self.recorded_total: int = 0
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

    def record(self, outcome: StrategyOutcome, persist: bool = True) -> None:
        """Append one outcome.  ``persist=False`` defers the disk write —
        batch feeders (the 5-min classify cycle can resolve hundreds of
        records at once) MUST use it and call :meth:`save` once at the end,
        or every record costs a full-store JSON dump on the caller's thread
        (2026-07-13 event-loop wedge contributor)."""
        key = self._key(outcome.strategy, outcome.context_key)
        rec = _Record(
            won=bool(outcome.won),
            pnl_pct=float(outcome.pnl_pct),
            r_multiple=float(outcome.r_multiple),
            mfe_pct=float(outcome.mfe_pct),
            timestamp=datetime.now(timezone.utc),
            source=(outcome.source or SOURCE_EMITTED).lower(),
            gross_r_multiple=(
                float(outcome.gross_r_multiple)
                if outcome.gross_r_multiple is not None
                else float(outcome.r_multiple)
            ),
            net_r_multiple=(
                float(outcome.net_r_multiple)
                if outcome.net_r_multiple is not None
                else float(outcome.r_multiple)
            ),
        )
        with self._lock:
            dq = self._records[key]
            # Count the eviction BEFORE it happens — a full ring drops its
            # oldest record on the next append and there is no observing it
            # afterwards.
            if dq.maxlen is not None and dq.maxlen > 0 and len(dq) >= dq.maxlen:
                self._evicted[key] += 1
            dq.append(rec)
            # Monotonic since-boot counter for the feature-liveness probes
            # (per-cell deques evict, so a raw record count can go backwards).
            self.recorded_total += 1
        if persist:
            self._save()

    def save(self) -> None:
        """Persist the store once — the batch counterpart of ``record(...,
        persist=False)``."""
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

    def sampling(self, strategy: str, context_key: str) -> Dict[str, int]:
        """``{held, evicted, seen, sampled}`` for one cell — the denominator.

        ``held`` is what every other statistic on this cell is computed from;
        ``seen`` is how many outcomes the cell has actually observed.  They are
        equal until the ring fills, and after that ``held`` is a **rolling
        most-recent-N window** while a sparse cell beside it is still all-time.
        Pooling the two without saying so averages different time windows,
        which is why this is published rather than kept internal.

        Mirrors ``suppression_audit``'s accessor of the same name, deliberately
        — a reader moving between the two surfaces should not have to learn two
        vocabularies for one idea.
        """
        key = self._key(strategy, context_key)
        with self._lock:
            records = self._records.get(key)
            held = len(records) if records else 0
            evicted = int(self._evicted.get(key, 0))
        return {
            "held": held,
            "evicted": evicted,
            "seen": held + evicted,
            "sampled": 1 if evicted else 0,
        }

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
            evicted_snapshot = dict(self._evicted)
        for (strategy, ctx), records in snapshot.items():
            n = len(records)
            wins = sum(1 for r in records if r.won)
            avg_pnl = sum(r.pnl_pct for r in records) / n
            avg_r = sum(r.r_multiple for r in records) / n
            avg_gross_r = sum(r.gross_r_multiple for r in records) / n
            avg_net_r = sum(r.net_r_multiple for r in records) / n
            # Per-source always-net R — the W2 realized-vs-counterfactual split.
            _by_src: Dict[str, list] = defaultdict(list)
            for _r in records:
                _by_src[_r.source].append(_r.net_r_multiple)
            net_r_by_source = {
                src: (sum(vals) / len(vals)) for src, vals in _by_src.items() if vals
            }
            mfe_records = [r for r in records if r.mfe_pct > 0]
            capture = (
                sum(r.pnl_pct for r in mfe_records) / sum(r.mfe_pct for r in mfe_records)
                if mfe_records and sum(r.mfe_pct for r in mfe_records) > 0
                else 0.0
            )
            _evicted = int(evicted_snapshot.get((strategy, ctx), 0))
            out[f"{strategy}|{ctx}"] = {
                "strategy": strategy,
                "context_key": ctx,
                "n": n,
                # The denominator, beside the verdict rather than behind it.
                # `n` is what the stats were computed from; `n_seen` is what
                # the cell actually observed. A reader who cannot tell a
                # 50-of-50 cell from a 50-of-5000 one is reading a sample as a
                # population — see `_evicted`'s note in __init__.
                "n_evicted": _evicted,
                "n_seen": n + _evicted,
                "sampled": bool(_evicted),
                "n_emitted": sum(1 for r in records if r.source == SOURCE_EMITTED),
                "n_suppressed": sum(1 for r in records if r.source == SOURCE_SUPPRESSED),
                "n_shadow": sum(1 for r in records if r.source == SOURCE_SHADOW),
                "win_rate": wins / n,
                "avg_pnl_pct": avg_pnl,
                "avg_r": avg_r,
                "avg_gross_r": avg_gross_r,
                "avg_net_r": avg_net_r,
                "net_r_by_source": net_r_by_source,
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
            # Eviction counts ride in a reserved key rather than an envelope,
            # so the file stays loadable by the previous build: a rollback
            # skips this entry (no "|" → not a cell key) and loses the counts
            # rather than losing the store. An envelope would have made every
            # cell unreadable to older code — a serializer whose blast radius
            # is every consumer (CLAUDE.md, #842).
            evicted_raw = raw.get(_EVICTED_KEY) if isinstance(raw, dict) else None
            with self._lock:
                if isinstance(evicted_raw, dict):
                    for key_str, count in evicted_raw.items():
                        parts = key_str.split("|", 1)
                        if len(parts) != 2:
                            continue
                        try:
                            self._evicted[(parts[0], parts[1])] = int(count)
                        except (TypeError, ValueError):
                            continue
                for key_str, recs in raw.items():
                    if key_str == _EVICTED_KEY:
                        continue
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
                                # Pre-cost store files: gross == the stored R.
                                gross_r_multiple=float(
                                    r.get("gr", r.get("r", 0.0))
                                ),
                                net_r_multiple=float(
                                    r.get("nr", r.get("r", 0.0))
                                ),
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
                            "gr": r.gross_r_multiple,
                            "nr": r.net_r_multiple,
                            "mfe": r.mfe_pct,
                            "ts": r.timestamp.isoformat(),
                            "src": r.source,
                        }
                        for r in records
                    ]
                    for (strategy, ctx), records in self._records.items()
                    if records
                }
                # A count that resets on restart would report every cell as
                # unsampled after each deploy — i.e. exactly the reassuring
                # answer, on the schedule that makes it hardest to notice.
                _ev = {
                    f"{strategy}|{ctx}": count
                    for (strategy, ctx), count in self._evicted.items()
                    if count
                }
            if _ev:
                payload[_EVICTED_KEY] = _ev
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


def pooled_suppressed_edge(
    matrix: Dict[str, Dict], strategy: str
) -> Optional[Dict[str, float]]:
    """Pooled counterfactual edge for one strategy's **suppressed** candidates.

    Answers "if we had emitted the candidates the gates killed, what would they
    have paid?" — sample-weighted across contexts, always-net R.

    This exists for the emission liveness probes.  A path that generates
    candidates and emits none is only a *fault* if those candidates were worth
    emitting; when the counterfactual says they lose money, full gating is the
    gates working, not a dead path.  Without this number the probe cannot tell
    those two apart and pages identically for both — which is how ``#781`` sat
    alerting for days with two of its three alerts being correct behaviour.

    Returns ``None`` when the strategy has no suppressed sample at all (nothing
    measured yet — a different state from "measured and negative", and one that
    must never be read as evidence either way).
    """
    total_n = 0
    weighted = 0.0
    for cell in (matrix or {}).values():
        if not isinstance(cell, dict):
            continue
        if str(cell.get("strategy") or "") != str(strategy or ""):
            continue
        ns = int(cell.get("n_suppressed", 0) or 0)
        if ns <= 0:
            continue
        by_src = cell.get("net_r_by_source") or {}
        if SOURCE_SUPPRESSED not in by_src:
            continue
        weighted += float(by_src[SOURCE_SUPPRESSED]) * ns
        total_n += ns
    if total_n <= 0:
        return None
    return {"n": total_n, "avg_r": weighted / total_n}


def reconcile_matrix(matrix: Dict[str, Dict]) -> Dict[str, Dict]:
    """Per-strategy **realized** (emitted) vs **counterfactual** (suppressed) net-R.

    The W2 answer to 'does our idealised counterfactual overstate what actually
    happens?'  For each strategy it pools the always-net R across cells, split by
    source, so ``delta_r = realized − counterfactual`` is the optimism tax on real
    emitted trades.  Mean-based and weighted by each source's n, so the cohort
    dual-write (which scales n but not the mean) does not distort it.  Geometry A/B
    arms (``X@FIXED`` / ``X@ATR``) are excluded — they are their own rollup.
    """
    acc: Dict[str, Dict[str, float]] = {}
    for cell in (matrix or {}).values():
        if not isinstance(cell, dict):
            continue
        strat = str(cell.get("strategy") or "")
        if not strat or "@" in strat:
            continue
        by_src = cell.get("net_r_by_source") or {}
        ne = int(cell.get("n_emitted", 0) or 0)
        ns = int(cell.get("n_suppressed", 0) or 0)
        a = acc.setdefault(strat, {"es": 0.0, "en": 0, "ss": 0.0, "sn": 0})
        if SOURCE_EMITTED in by_src and ne > 0:
            a["es"] += float(by_src[SOURCE_EMITTED]) * ne
            a["en"] += ne
        if SOURCE_SUPPRESSED in by_src and ns > 0:
            a["ss"] += float(by_src[SOURCE_SUPPRESSED]) * ns
            a["sn"] += ns
    out: Dict[str, Dict] = {}
    for strat, a in acc.items():
        rnet = (a["es"] / a["en"]) if a["en"] else None
        cnet = (a["ss"] / a["sn"]) if a["sn"] else None
        out[strat] = {
            "realized_net_r": rnet,
            "realized_n": int(a["en"]),
            "counterfactual_net_r": cnet,
            "counterfactual_n": int(a["sn"]),
            "delta_r": (rnet - cnet) if (rnet is not None and cnet is not None) else None,
        }
    return out


# Module-global singleton, mirroring _cohort_edge_store in the scanner.
_strategy_edge_store: Optional[StrategyEdgeStore] = None


def get_strategy_edge_store() -> StrategyEdgeStore:
    global _strategy_edge_store
    if _strategy_edge_store is None:
        _strategy_edge_store = StrategyEdgeStore()
    return _strategy_edge_store
