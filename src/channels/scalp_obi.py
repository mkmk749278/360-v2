# 360_SCALP_OBI is disabled: order book depth fetches removed. Channel returns None.
"""360_SCALP_OBI – OBI Absorption Scalp ⚡

Trigger : Strong Order Book Imbalance (OBI) absorption pattern.
Logic   : OBI > 0.65 (strong bid absorption) + price near support → LONG
          OBI < -0.65 (strong ask absorption) + price near resistance → SHORT
          "At support/resistance" = within 0.5% of recent 20-bar low/high
Filters : Minimum volume threshold, spread gate
Risk    : Tight SL 0.1-0.2%, TP1 1R, TP2 1.5R
Signal ID prefix: "SOBI-"
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from config import CHANNEL_SCALP_OBI
from src.channels.base import BaseChannel, Signal, build_channel_signal
from src.filters import check_rsi
from src.smc import Direction
from src.spoof_detect import check_spoof_gate
from src.utils import get_logger

log = get_logger("scalp_obi")

# OBI thresholds for signal generation
_OBI_LONG_THRESHOLD: float = 0.65   # Strong bid absorption
_OBI_SHORT_THRESHOLD: float = -0.65  # Strong ask absorption

# Maximum distance from recent high/low to be considered at S/R.
# Used as fallback when ATR is not available.
_SR_PROXIMITY_PCT: float = 0.5  # 0.5%

# Order book data older than this threshold (seconds) is considered stale
# and will cause the OBI signal to be skipped.
_OBI_MAX_STALENESS_SEC: float = 2.0

# Flag to emit a one-time warning when the order book lacks a timestamp.
# Using a list so it can be mutated from within functions without `global`.
_obi_ts_warning_state: list = [False]  # [warned]

# When True, signals are rejected (fail-closed) when the order book lacks a
# timestamp.  Set to False only for backward-compatibility testing.
_OBI_REQUIRE_TIMESTAMP: bool = True

# Minimum total USD depth across top-10 bid+ask levels.
# Books thinner than this threshold produce unreliable OBI readings.
_MIN_OB_DEPTH_USD: float = 100_000.0


def _compute_obi(bids: List, asks: List) -> Optional[float]:
    """Compute depth-weighted Order Book Imbalance.

    Uses exponential depth weighting: level 1 = weight 1.0, deeper levels
    decay toward 0.  This reflects the reality that near-touch imbalance
    is far more predictive than deep-book imbalance.

    Returns OBI float in range [-1, 1], or None when data is insufficient.
    """
    try:
        weights = [1.0 / (1.0 + 0.25 * i) for i in range(10)]
        bid_qty = sum(float(b[1]) * w for b, w in zip(bids[:10], weights))
        ask_qty = sum(float(a[1]) * w for a, w in zip(asks[:10], weights))
        total = bid_qty + ask_qty
        if total <= 0:
            return None
        return (bid_qty - ask_qty) / total
    except (IndexError, TypeError, ValueError):
        return None


class ScalpOBIChannel(BaseChannel):
    """OBI Absorption scalp trigger."""

    def __init__(self) -> None:
        super().__init__(CHANNEL_SCALP_OBI)

    def evaluate(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        return None
