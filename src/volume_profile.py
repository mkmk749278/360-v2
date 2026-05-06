"""Volume-Profile lite — Point of Control + Value Area High/Low per symbol.

Phase 4 of the chartist-eye world model.  Closes another gap a chart
reader picks up at a glance: *where the volume actually lives*.

What this is
------------
Given a candle history, build a price-binned histogram of volume —
each candle's volume is distributed uniformly across the bins its
[low, high] range overlaps.  From the histogram derive:

* **POC** (Point of Control)  — the single bin with the most volume.
  This is a "magnet" price: trades cluster here.  Entries far from
  POC are more likely to revert *toward* it.
* **Value Area** — the contiguous price band centred on the POC that
  contains 70% of total volume.  Endpoints are **VAH** (Value Area
  High) and **VAL** (Value Area Low).
* **Total volume**, raw bin volumes, bin midpoints — for telemetry
  and downstream wiring.

Why "lite"
----------
A real VPVR (Volume Profile Visible Range) uses tick-level
trade-by-price data.  We work from candles, so we approximate by
distributing each candle's bar volume linearly across its [low,high]
range.  The approximation is good enough to:

  - Identify POC zones (the dominant bin shows up regardless of
    distribution method)
  - Bound value areas correctly
  - Inform "is the entry in the high-volume node or at the edge"
    for confluence scoring

It is NOT precise enough for buy-vs-sell delta analysis, footprint
charts, or single-print imbalances.  Those need tick data which we
already store separately for the WHALE_MOMENTUM / FUNDING paths.

Wiring (deferred)
-----------------
Like PR-5 (LevelBook) and PR-7 (StructureTracker), this PR ships
infrastructure only.  No scanner changes, no scoring side-effects.

Planned follow-up integration:

  1. POC / VAH / VAL as auto-injected "structural" levels in the
     LevelBook so confluence scoring picks them up automatically.
  2. Direct entry-zone warnings: when entry sits **at the POC**, that
     is a known magnet for retracement → small soft penalty.  When
     entry sits at **VAH/VAL edge**, that's a textbook bounce zone →
     small bonus.
  3. Value-area-context emoji / annotation in the Telegram signal
     post (future Lumin v0.0.10+).

Cost
----
One refresh = O(candles × bins).  At 200 candles × 50 bins per pair
= 10 000 ops; 75 pairs → ~750 000 per refresh cycle.  Cached with
30-min TTL → ~25 000 ops/sec amortised, dwarfed by the indicator
pipeline already running.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from src.utils import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------

#: Number of price bins per profile.  50 is a reasonable balance — too few
#: collapses POC detection; too many spreads volume too thin to find a clear
#: peak.  Equity / futures industry standard is 24-72 for VPVR.
DEFAULT_BINS: int = 50

#: How many candles back to include.  200 candles on 5m = ~17h, on 1h = 8d.
#: The window is the "visible range" — what's structurally relevant for
#: scalping.
DEFAULT_LOOKBACK: int = 200

#: Fraction of total volume that defines the value area.  70% is the CME /
#: industry standard.
VALUE_AREA_FRACTION: float = 0.70

#: Per-symbol refresh TTL.  Volume distribution shifts slowly; 30 min plenty.
PROFILE_REFRESH_SEC: float = 1800.0

#: Minimum candle count before we'll attempt a profile.
MIN_CANDLES: int = 30


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class VolumeProfileResult:
    """Volume-profile snapshot for a symbol at the time of refresh."""

    symbol: str
    bins: int
    lookback: int
    poc: float
    vah: float
    val: float
    total_volume: float
    bin_edges: List[float]    # length bins+1
    bin_volumes: List[float]  # length bins
    last_update_ts: float = field(default_factory=time.time)

    def is_in_value_area(self, price: float) -> bool:
        """True if *price* sits inside [VAL, VAH]."""
        return self.val <= price <= self.vah

    def distance_to_poc_pct(self, price: float) -> float:
        """Signed % distance from POC — positive when price is above POC."""
        if self.poc <= 0:
            return 0.0
        return (price - self.poc) / self.poc * 100.0

    def is_near_poc(self, price: float, *, tolerance_pct: float = 0.30) -> bool:
        """True when *price* sits within tolerance of POC (a magnet)."""
        if self.poc <= 0:
            return False
        return abs(price - self.poc) <= self.poc * (tolerance_pct / 100.0)

    def is_at_value_edge(self, price: float, *, tolerance_pct: float = 0.30) -> bool:
        """True when *price* sits at VAH or VAL edge (bounce candidate)."""
        if self.vah <= 0 or self.val <= 0:
            return False
        edge_band_h = self.vah * (tolerance_pct / 100.0)
        edge_band_l = self.val * (tolerance_pct / 100.0)
        near_vah = abs(price - self.vah) <= edge_band_h
        near_val = abs(price - self.val) <= edge_band_l
        return near_vah or near_val


# ---------------------------------------------------------------------------
# Histogram construction
# ---------------------------------------------------------------------------


def _build_histogram(
    highs: np.ndarray,
    lows: np.ndarray,
    volumes: np.ndarray,
    bins: int,
) -> tuple:
    """Return ``(bin_edges, bin_volumes)`` for the candle range.

    Volume distribution rule:
      Each candle's bar volume is distributed *uniformly* across the bins
      its [low, high] range overlaps.  A candle whose range spans 5 bins
      contributes 1/5 of its volume to each.
    """
    price_min = float(np.min(lows))
    price_max = float(np.max(highs))
    if price_max <= price_min:
        # Degenerate range — single price, no histogram.
        edges = np.linspace(price_min - 1e-6, price_min + 1e-6, bins + 1).tolist()
        return edges, [0.0] * bins

    edges = np.linspace(price_min, price_max, bins + 1)
    bin_width = (price_max - price_min) / bins
    bin_volumes = np.zeros(bins, dtype=np.float64)

    for i in range(len(highs)):
        lo = float(lows[i])
        hi = float(highs[i])
        v = float(volumes[i])
        if v <= 0 or hi <= lo:
            continue
        # Find bin range overlapping [lo, hi].
        i_lo = max(0, min(bins - 1, int((lo - price_min) / bin_width)))
        i_hi = max(0, min(bins - 1, int((hi - price_min) / bin_width)))
        if i_hi < i_lo:
            i_lo, i_hi = i_hi, i_lo
        n_bins_touched = i_hi - i_lo + 1
        share = v / n_bins_touched
        for j in range(i_lo, i_hi + 1):
            bin_volumes[j] += share

    return edges.tolist(), bin_volumes.tolist()


def _find_poc(bin_edges: List[float], bin_volumes: List[float]) -> float:
    """Return the price midpoint of the highest-volume bin."""
    if not bin_volumes or all(v == 0 for v in bin_volumes):
        # No volume anywhere — return midpoint of overall range.
        return (bin_edges[0] + bin_edges[-1]) / 2.0
    poc_idx = max(range(len(bin_volumes)), key=lambda i: bin_volumes[i])
    return (bin_edges[poc_idx] + bin_edges[poc_idx + 1]) / 2.0


def _find_value_area(
    bin_edges: List[float],
    bin_volumes: List[float],
    *,
    fraction: float = VALUE_AREA_FRACTION,
) -> tuple:
    """Compute (VAH, VAL) by expanding outward from POC.

    Algorithm (mirrors CME's: alternate up vs. down, picking the side with
    the higher 2-bin sum, summing into the value area until ≥ fraction of
    total volume is covered).
    """
    n = len(bin_volumes)
    if n == 0:
        return bin_edges[0] if bin_edges else 0.0, bin_edges[-1] if bin_edges else 0.0

    total = sum(bin_volumes)
    if total <= 0:
        return bin_edges[-1], bin_edges[0]

    poc_idx = max(range(n), key=lambda i: bin_volumes[i])
    target = total * fraction

    accumulated = bin_volumes[poc_idx]
    lo_idx = poc_idx
    hi_idx = poc_idx

    while accumulated < target and (lo_idx > 0 or hi_idx < n - 1):
        # Sum next 2 bins on each side (or whatever's available).
        up_sum = 0.0
        if hi_idx < n - 1:
            up_sum += bin_volumes[hi_idx + 1]
            if hi_idx + 2 < n:
                up_sum += bin_volumes[hi_idx + 2]
        down_sum = 0.0
        if lo_idx > 0:
            down_sum += bin_volumes[lo_idx - 1]
            if lo_idx - 2 >= 0:
                down_sum += bin_volumes[lo_idx - 2]

        if up_sum > down_sum and hi_idx < n - 1:
            hi_idx = min(hi_idx + 2, n - 1)
            accumulated += up_sum
        elif down_sum > 0 and lo_idx > 0:
            lo_idx = max(lo_idx - 2, 0)
            accumulated += down_sum
        elif hi_idx < n - 1:
            hi_idx = min(hi_idx + 2, n - 1)
            accumulated += up_sum
        else:
            break

    val = bin_edges[lo_idx]
    vah = bin_edges[hi_idx + 1]
    return vah, val


# ---------------------------------------------------------------------------
# Public computation
# ---------------------------------------------------------------------------


def compute_volume_profile(
    symbol: str,
    candles: dict,
    *,
    bins: int = DEFAULT_BINS,
    lookback: int = DEFAULT_LOOKBACK,
) -> Optional[VolumeProfileResult]:
    """Compute a one-shot volume profile for *symbol* from *candles*.

    Returns ``None`` when the input is too small or malformed.
    """
    if not isinstance(candles, dict):
        return None
    highs_arr = candles.get("high")
    lows_arr = candles.get("low")
    vols_arr = candles.get("volume")
    if highs_arr is None or lows_arr is None or vols_arr is None:
        return None
    try:
        highs = np.asarray(highs_arr, dtype=np.float64).ravel()
        lows = np.asarray(lows_arr, dtype=np.float64).ravel()
        volumes = np.asarray(vols_arr, dtype=np.float64).ravel()
    except (TypeError, ValueError):
        return None

    n = min(len(highs), len(lows), len(volumes))
    if n < MIN_CANDLES:
        return None
    if n > lookback:
        highs = highs[-lookback:]
        lows = lows[-lookback:]
        volumes = volumes[-lookback:]

    bin_edges, bin_volumes = _build_histogram(highs, lows, volumes, bins)
    poc = _find_poc(bin_edges, bin_volumes)
    vah, val = _find_value_area(bin_edges, bin_volumes)

    # Defensive: VAL must be ≤ VAH.
    if val > vah:
        val, vah = vah, val

    return VolumeProfileResult(
        symbol=symbol,
        bins=bins,
        lookback=lookback,
        poc=poc,
        vah=vah,
        val=val,
        total_volume=float(sum(bin_volumes)),
        bin_edges=bin_edges,
        bin_volumes=bin_volumes,
    )


# ---------------------------------------------------------------------------
# Cached store with TTL
# ---------------------------------------------------------------------------


class VolumeProfileStore:
    """Per-symbol cache with refresh TTL — same pattern as LevelBook /
    StructureTracker so the scanner has a uniform integration shape."""

    def __init__(self) -> None:
        self._results: Dict[str, VolumeProfileResult] = {}
        self._refresh_ts: Dict[str, float] = {}

    def refresh(
        self, symbol: str, candles: dict,
        *, bins: int = DEFAULT_BINS, lookback: int = DEFAULT_LOOKBACK,
    ) -> Optional[VolumeProfileResult]:
        result = compute_volume_profile(
            symbol, candles, bins=bins, lookback=lookback,
        )
        if result is not None:
            self._results[symbol] = result
            self._refresh_ts[symbol] = time.time()
        return result

    def refresh_if_stale(
        self, symbol: str, candles: dict,
        *, ttl_sec: float = PROFILE_REFRESH_SEC,
        bins: int = DEFAULT_BINS, lookback: int = DEFAULT_LOOKBACK,
    ) -> Optional[VolumeProfileResult]:
        last = self._refresh_ts.get(symbol)
        if last is not None and (time.time() - last) < ttl_sec:
            return self._results.get(symbol)
        return self.refresh(symbol, candles, bins=bins, lookback=lookback)

    def get(self, symbol: str) -> Optional[VolumeProfileResult]:
        return self._results.get(symbol)

    def stats(self, symbol: str) -> Dict[str, float]:
        r = self._results.get(symbol)
        if r is None:
            return {}
        return {
            "poc": r.poc,
            "vah": r.vah,
            "val": r.val,
            "total_volume": r.total_volume,
            "value_area_width_pct": (
                (r.vah - r.val) / r.poc * 100.0 if r.poc > 0 else 0.0
            ),
        }


__all__ = [
    "DEFAULT_BINS",
    "DEFAULT_LOOKBACK",
    "VALUE_AREA_FRACTION",
    "PROFILE_REFRESH_SEC",
    "MIN_CANDLES",
    "VolumeProfileResult",
    "VolumeProfileStore",
    "compute_volume_profile",
]
