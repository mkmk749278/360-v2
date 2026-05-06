"""Persistent multi-TF Support/Resistance Level Book.

This module gives every evaluator a shared "world model" of meaningful
price levels per pair — the chartist eye the engine has lacked.

What it does
------------
For each symbol we discover, score, and persist horizontal S/R levels
from multiple timeframes (1d / 4h / 1h):

* **Swing-pivot detection** via ``chart_patterns._find_swing_highs/lows``
  on each TF.
* **Touch counting** — how many times each candle high/low has tested the
  level within ±0.15%.  More touches = more meaningful.
* **Clustering** — levels within ±0.30% of each other on the same or
  different TFs are merged into a single zone, summing their touches.
* **Round-number injection** — psychological levels (0.001, 0.01, 0.1,
  1, 10, 100, 1000, 10000, 50000, 100000…) within ±20% of current price
  are added with a base score boost.
* **Scoring** — ``base + touches × 5 × tf_weight × age_decay``, where
  tf_weight is 2.0 / 1.5 / 1.0 for 1d / 4h / 1h, and age_decay is 1.0
  for tested in last 24h, 0.5 for 1–7d, 0.25 for >7d.

What other modules consume from this
------------------------------------
The ``LevelBook`` is wired in PR-6 (confluence scoring).  Today every
evaluator only sees its own one rolling swing-pivot window per TF; with
the LevelBook a candidate at price ``P`` can ask:

* ``book.nearest_level(symbol, P)`` — returns the closest scored level.
* ``book.confluence_count(symbol, P)`` — how many distinct levels live
  within ±0.3% of P (level + round number + multi-TF cluster all count).

PR-5 ships the infrastructure only.  No evaluator wiring; no scoring
side-effects; no Telegram changes.

Cost
----
Discovery is O(N × TFs) per refresh, where N = candles per TF (typically
500).  At 75 pairs × 3 TFs that's ~112 500 swing-pivot ops per refresh —
trivially cheap (< 100 ms total).  Refresh cadence is once an hour by
default; evaluator queries hit the in-memory cache.

Persistence (TODO PR-6)
-----------------------
Currently in-memory only.  The next iteration will write
``data/level_book.json`` periodically so the engine retains its level
view across restarts.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from src.chart_patterns import _find_swing_highs, _find_swing_lows
from src.utils import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Tunables — env-overridable per B8 in a future iteration
# ---------------------------------------------------------------------------

#: Tolerance for considering two levels the same zone (cluster) and for
#: counting a candle high/low as having tested a level.
LEVEL_CLUSTER_TOLERANCE_PCT: float = 0.30
LEVEL_TOUCH_TOLERANCE_PCT: float = 0.15

#: Confluence query tolerance — levels within this band of a price are
#: considered confluent.
CONFLUENCE_TOLERANCE_PCT: float = 0.30

#: Per-TF score weight.  Higher TF levels are more meaningful.
TF_WEIGHT: Dict[str, float] = {
    "1d": 2.0,
    "4h": 1.5,
    "1h": 1.0,
    "round": 1.5,  # round numbers anchor as a ~4h-strength level
}

#: Score decay by age since last test.  Stale levels matter less.
AGE_DECAY_BUCKETS: List[tuple] = [
    (24 * 3600, 1.0),       # tested in last 24h → full weight
    (7 * 24 * 3600, 0.5),   # 1–7 days
    (30 * 24 * 3600, 0.25), # 7–30 days
]
AGE_DECAY_FLOOR: float = 0.10  # > 30 days

#: Base score for any discovered swing pivot before touch / TF / age scaling.
BASE_SCORE: float = 10.0
TOUCH_SCORE_PER: float = 5.0
TOUCH_SCORE_CAP: int = 6  # diminishing returns beyond 6 touches

#: Round-number bonus added on top of the standard scoring.
ROUND_NUMBER_BONUS: float = 5.0

#: How far back from the current price to seed round-number levels.
ROUND_NUMBER_RANGE_PCT: float = 20.0

#: Swing-detection look-back window per TF (bars on each side of pivot).
SWING_ORDER_BY_TF: Dict[str, int] = {
    "1d": 3,
    "4h": 4,
    "1h": 5,
}

#: Maximum levels retained per symbol (top-N by score).  Keeps the book
#: bounded so confluence queries stay O(N) with N small.
MAX_LEVELS_PER_SYMBOL: int = 60


# ---------------------------------------------------------------------------
# Level dataclass
# ---------------------------------------------------------------------------


@dataclass
class Level:
    """A single S/R level with its provenance and score."""

    price: float
    type: str  # "support" or "resistance"
    source_tf: str  # "1d" | "4h" | "1h" | "round"
    touches: int = 1
    last_test_ts: Optional[float] = None
    score: float = 0.0
    is_round_number: bool = False
    # When clustered, source_tfs records all TFs that contributed.
    source_tfs: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.source_tfs:
            self.source_tfs = [self.source_tf]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _round_number_levels(price: float, range_pct: float = ROUND_NUMBER_RANGE_PCT) -> List[float]:
    """Generate psychological round-number levels around *price*.

    Strategy: pick the order-of-magnitude step appropriate to the price
    (e.g. step=10 for BTC at 78000, step=0.0001 for SHIBUSDT at 0.00002),
    then walk the band ±range_pct.
    """
    if price <= 0:
        return []
    # Choose step as 10^floor(log10(price) - 1).  At price=78000 → step=1000;
    # at price=2.5 → step=0.1; at price=0.0023 → step=0.0001.
    log_step = math.floor(math.log10(price) - 1)
    step = 10 ** log_step
    low = price * (1 - range_pct / 100.0)
    high = price * (1 + range_pct / 100.0)
    n_low = math.ceil(low / step)
    n_high = math.floor(high / step)
    levels: List[float] = []
    for n in range(int(n_low), int(n_high) + 1):
        v = round(n * step, 12)
        if v > 0:
            levels.append(v)
    return levels


def _count_touches(
    level_price: float,
    highs: np.ndarray,
    lows: np.ndarray,
    *,
    tolerance_pct: float = LEVEL_TOUCH_TOLERANCE_PCT,
) -> tuple:
    """Count candles whose wick touched the level within tolerance.

    Returns ``(touches, last_index)``.  ``last_index`` is the most recent
    bar index where a touch occurred, or ``None`` if no touch.
    """
    if level_price <= 0 or len(highs) == 0:
        return 0, None
    band = level_price * (tolerance_pct / 100.0)
    lo = level_price - band
    hi = level_price + band
    touches = 0
    last_idx: Optional[int] = None
    for i in range(len(highs)):
        if highs[i] >= lo and lows[i] <= hi:
            touches += 1
            last_idx = i
    return touches, last_idx


def _age_decay(last_test_ts: Optional[float], now_ts: Optional[float] = None) -> float:
    """Multiplicative decay based on age since the last touch."""
    if last_test_ts is None:
        return AGE_DECAY_FLOOR
    now_ts = now_ts if now_ts is not None else time.time()
    age = max(0.0, now_ts - last_test_ts)
    for cutoff, weight in AGE_DECAY_BUCKETS:
        if age <= cutoff:
            return weight
    return AGE_DECAY_FLOOR


def _score_level(level: Level, *, now_ts: Optional[float] = None) -> float:
    """Compute the level's score from touches, TF, age and round-number bonus."""
    touches_capped = min(level.touches, TOUCH_SCORE_CAP)
    tf_weight = TF_WEIGHT.get(level.source_tf, 1.0)
    age_w = _age_decay(level.last_test_ts, now_ts=now_ts)
    score = (BASE_SCORE + TOUCH_SCORE_PER * touches_capped) * tf_weight * age_w
    if level.is_round_number:
        score += ROUND_NUMBER_BONUS
    return round(score, 2)


def _cluster_levels(levels: List[Level], tolerance_pct: float = LEVEL_CLUSTER_TOLERANCE_PCT) -> List[Level]:
    """Merge levels within tolerance into single-zone aggregates.

    Merge rule:
    * Cluster price = touch-weighted mean
    * Touches summed
    * source_tfs set unioned
    * is_round_number = True if any contributor is a round number
    * last_test_ts = max across cluster
    """
    if not levels:
        return []
    # Sort by price so clustering is a single pass.
    sorted_levels = sorted(levels, key=lambda lv: lv.price)
    out: List[Level] = []
    current = [sorted_levels[0]]

    def _flush(group: List[Level]) -> Level:
        total_touches = sum(g.touches for g in group)
        if total_touches > 0:
            price = sum(g.price * g.touches for g in group) / total_touches
        else:
            price = sum(g.price for g in group) / len(group)
        last_ts_vals = [g.last_test_ts for g in group if g.last_test_ts is not None]
        last_ts = max(last_ts_vals) if last_ts_vals else None
        is_round = any(g.is_round_number for g in group)
        # Pick a representative type — majority across the cluster.
        n_support = sum(1 for g in group if g.type == "support")
        n_resistance = len(group) - n_support
        rep_type = "support" if n_support >= n_resistance else "resistance"
        # source_tf = highest-weight TF in cluster
        rep_tf = max(group, key=lambda g: TF_WEIGHT.get(g.source_tf, 0.0)).source_tf
        all_tfs = sorted({tf for g in group for tf in g.source_tfs})
        return Level(
            price=price,
            type=rep_type,
            source_tf=rep_tf,
            touches=total_touches,
            last_test_ts=last_ts,
            is_round_number=is_round,
            source_tfs=all_tfs,
        )

    for lv in sorted_levels[1:]:
        ref = current[-1]
        band = ref.price * (tolerance_pct / 100.0)
        if abs(lv.price - ref.price) <= band:
            current.append(lv)
        else:
            out.append(_flush(current))
            current = [lv]
    out.append(_flush(current))
    return out


def _candle_ts(candles: dict, idx: int) -> Optional[float]:
    """Best-effort extraction of a unix timestamp for candle *idx*."""
    # `or` chain on numpy arrays raises on truthiness — use explicit lookups.
    ts_arr = candles.get("timestamp")
    if ts_arr is None:
        ts_arr = candles.get("time")
    if ts_arr is None:
        ts_arr = candles.get("open_time")
    if ts_arr is None:
        return None
    try:
        v = float(ts_arr[idx])
    except (TypeError, ValueError, IndexError):
        return None
    # Heuristic: ms epoch if > 1e12 (year ≈2001+).
    if v > 1e12:
        v /= 1000.0
    return v


# ---------------------------------------------------------------------------
# LevelBook
# ---------------------------------------------------------------------------


class LevelBook:
    """In-memory store of multi-TF S/R levels per symbol."""

    def __init__(self) -> None:
        self._levels: Dict[str, List[Level]] = {}
        self._refresh_ts: Dict[str, float] = {}

    def refresh(self, symbol: str, candles_by_tf: Dict[str, dict]) -> List[Level]:
        """Rebuild the level book for *symbol* from multi-TF candles.

        Expected ``candles_by_tf``:
          {"1d": {"high":..., "low":..., "timestamp":...},
           "4h": {...},
           "1h": {...}}

        Missing TFs are skipped.  Returns the resulting clustered+scored
        level list (also stored on self).
        """
        raw: List[Level] = []
        now_ts = time.time()

        # 1. Seed swing pivots from each TF.
        for tf, candles in candles_by_tf.items():
            if tf not in TF_WEIGHT:
                continue
            highs_arr = candles.get("high")
            lows_arr = candles.get("low")
            if highs_arr is None or lows_arr is None:
                continue
            highs = np.asarray(highs_arr, dtype=np.float64).ravel()
            lows = np.asarray(lows_arr, dtype=np.float64).ravel()
            if len(highs) < 20 or len(lows) < 20:
                continue
            order = SWING_ORDER_BY_TF.get(tf, 5)

            for i in _find_swing_highs(highs, order):
                price = float(highs[i])
                touches, last_idx = _count_touches(price, highs, lows)
                last_ts = _candle_ts(candles, last_idx) if last_idx is not None else _candle_ts(candles, i)
                raw.append(Level(
                    price=price,
                    type="resistance",
                    source_tf=tf,
                    touches=max(1, touches),
                    last_test_ts=last_ts,
                ))

            for i in _find_swing_lows(lows, order):
                price = float(lows[i])
                touches, last_idx = _count_touches(price, highs, lows)
                last_ts = _candle_ts(candles, last_idx) if last_idx is not None else _candle_ts(candles, i)
                raw.append(Level(
                    price=price,
                    type="support",
                    source_tf=tf,
                    touches=max(1, touches),
                    last_test_ts=last_ts,
                ))

        # 2. Round-number levels around current price (use last close from
        #    highest available TF).
        ref_close: Optional[float] = None
        for tf in ("1h", "4h", "1d"):
            cd = candles_by_tf.get(tf, {})
            closes = cd.get("close")
            if closes is not None and len(closes) > 0:
                try:
                    ref_close = float(np.asarray(closes).ravel()[-1])
                    break
                except (TypeError, ValueError):
                    continue
        if ref_close is not None:
            primary_cd = candles_by_tf.get("1h") or candles_by_tf.get("4h") or {}
            highs_arr = primary_cd.get("high")
            lows_arr = primary_cd.get("low")
            if highs_arr is not None and lows_arr is not None:
                highs = np.asarray(highs_arr, dtype=np.float64).ravel()
                lows = np.asarray(lows_arr, dtype=np.float64).ravel()
                for rn_price in _round_number_levels(ref_close):
                    touches, last_idx = _count_touches(rn_price, highs, lows)
                    last_ts = _candle_ts(primary_cd, last_idx) if last_idx is not None else None
                    rn_type = "support" if rn_price <= ref_close else "resistance"
                    raw.append(Level(
                        price=rn_price,
                        type=rn_type,
                        source_tf="round",
                        touches=max(1, touches),
                        last_test_ts=last_ts,
                        is_round_number=True,
                    ))

        # 3. Cluster nearby levels into zones.
        clustered = _cluster_levels(raw)

        # 4. Score each clustered level.
        for lv in clustered:
            lv.score = _score_level(lv, now_ts=now_ts)

        # 5. Cap to top-N by score.
        clustered.sort(key=lambda lv: lv.score, reverse=True)
        final = clustered[:MAX_LEVELS_PER_SYMBOL]

        self._levels[symbol] = final
        self._refresh_ts[symbol] = now_ts
        log.debug(
            "LevelBook.refresh symbol={} raw={} clustered={} kept={}",
            symbol, len(raw), len(clustered), len(final),
        )
        return final

    def get_levels(self, symbol: str) -> List[Level]:
        """Return the current level list for *symbol* (empty if never refreshed)."""
        return list(self._levels.get(symbol, []))

    def last_refresh_ts(self, symbol: str) -> Optional[float]:
        return self._refresh_ts.get(symbol)

    def nearest_level(
        self,
        symbol: str,
        price: float,
        *,
        max_distance_pct: float = 0.5,
        type_filter: Optional[str] = None,
    ) -> Optional[Level]:
        """Return the highest-scoring level within ``max_distance_pct`` of *price*.

        ``type_filter`` may be ``"support"`` or ``"resistance"`` to restrict.
        """
        if price <= 0:
            return None
        band = price * (max_distance_pct / 100.0)
        candidates = []
        for lv in self._levels.get(symbol, []):
            if abs(lv.price - price) > band:
                continue
            if type_filter is not None and lv.type != type_filter:
                continue
            candidates.append(lv)
        if not candidates:
            return None
        candidates.sort(key=lambda lv: lv.score, reverse=True)
        return candidates[0]

    def confluence_count(
        self,
        symbol: str,
        price: float,
        *,
        tolerance_pct: float = CONFLUENCE_TOLERANCE_PCT,
    ) -> int:
        """How many distinct levels (post-cluster) sit within tolerance of *price*."""
        if price <= 0:
            return 0
        band = price * (tolerance_pct / 100.0)
        return sum(
            1 for lv in self._levels.get(symbol, [])
            if abs(lv.price - price) <= band
        )

    def stats(self, symbol: str) -> Dict[str, int]:
        """Telemetry helper — counts by type / TF / round-number."""
        levels = self._levels.get(symbol, [])
        return {
            "total": len(levels),
            "support": sum(1 for lv in levels if lv.type == "support"),
            "resistance": sum(1 for lv in levels if lv.type == "resistance"),
            "round_numbers": sum(1 for lv in levels if lv.is_round_number),
            "from_1d": sum(1 for lv in levels if "1d" in lv.source_tfs),
            "from_4h": sum(1 for lv in levels if "4h" in lv.source_tfs),
            "from_1h": sum(1 for lv in levels if "1h" in lv.source_tfs),
        }


__all__ = [
    "Level",
    "LevelBook",
    "LEVEL_CLUSTER_TOLERANCE_PCT",
    "LEVEL_TOUCH_TOLERANCE_PCT",
    "CONFLUENCE_TOLERANCE_PCT",
    "MAX_LEVELS_PER_SYMBOL",
]
