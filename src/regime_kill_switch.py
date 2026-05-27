"""BTC Regime Kill Switch.

Detects when BTC is in a whipsaw regime and blocks new signal dispatch.

**The problem this solves:**
Top-75 USDT-M pairs are 0.85-0.95 correlated to BTC.  When BTC is
oscillating without net direction — rapid alternating impulses that cover
significant range but go nowhere — structural setup signals (SR_FLIP,
DIV_CONT, BREAKOUT, etc.) have ~50/50 directional probability regardless
of their score.  Dispatching 5 signals into a 4-hour BTC chop window
produces 3-4 simultaneous SL hits on the next BTC micro-impulse.

**Detection: direction efficiency**

Over a rolling window of BTC 15m candles:

    total_range  = sum of (high - low) per candle
    net_move     = |close[-1] - close[-lookback-1]|
    efficiency   = net_move / total_range  (0.0 → 1.0)

Interpretation:
  * Trending market: 0.60-0.90  (most range is directional progress)
  * Normal ranging:  0.30-0.60  (range is used, but direction is modest)
  * Whipsaw:         0.05-0.20  (range is almost entirely wasted)

Guard condition: `total_range / close[-1]` must be ≥ MIN_MOVES_PCT
(default 1.5%).  Below that, BTC is too quiet for the efficiency metric
to be meaningful — the gate does not fire on silence.

**Tape-driven setup exemptions:**
WHALE_MOMENTUM, FUNDING_EXTREME_SIGNAL, LIQUIDATION_REVERSAL are exempt
because their thesis IS to read the chaos.  Penalising them would suppress
the exact signals they exist to capture.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

from src.utils import get_logger

log = get_logger("regime_kill_switch")

# ---------------------------------------------------------------------------
# Tunables — all env-overridable per B8
# ---------------------------------------------------------------------------

# Master on/off switch.  Default enabled.
REGIME_KILL_ENABLED: bool = os.getenv("REGIME_KILL_ENABLED", "true").lower() != "false"

# Number of BTC 15m candles to examine (default 16 = 4 hours).
REGIME_KILL_LOOKBACK: int = int(os.getenv("REGIME_KILL_LOOKBACK", "16"))

# Direction efficiency below which BTC is classified as WHIPSAW.
# 0.20 = net move uses less than 20% of total candle range → whipsaw.
REGIME_KILL_EFFICIENCY_MIN: float = float(os.getenv("REGIME_KILL_EFFICIENCY_MIN", "0.20"))

# Minimum total candle range as % of BTC price for the gate to fire.
# Prevents the gate from triggering on flat/quiet days where efficiency
# is undefined rather than genuinely choppy.
REGIME_KILL_MIN_RANGE_PCT: float = float(os.getenv("REGIME_KILL_MIN_RANGE_PCT", "1.5"))

# Setup classes exempt from the kill switch (tape-driven paths whose
# thesis is to trade the chaos, not avoid it).
REGIME_KILL_EXEMPT_SETUPS: frozenset = frozenset(
    s.strip()
    for s in os.getenv(
        "REGIME_KILL_EXEMPT_SETUPS",
        "WHALE_MOMENTUM,FUNDING_EXTREME_SIGNAL,LIQUIDATION_REVERSAL",
    ).split(",")
    if s.strip()
)


# ---------------------------------------------------------------------------
# Core evaluator
# ---------------------------------------------------------------------------


def evaluate_btc_whipsaw(
    btc_candles_15m: Dict[str, Any],
    lookback: int = REGIME_KILL_LOOKBACK,
    efficiency_min: float = REGIME_KILL_EFFICIENCY_MIN,
    min_range_pct: float = REGIME_KILL_MIN_RANGE_PCT,
) -> Tuple[bool, str, float]:
    """Evaluate whether BTC 15m data indicates a whipsaw regime.

    Parameters
    ----------
    btc_candles_15m:
        Dict with keys ``"high"``, ``"low"``, ``"close"`` (lists/arrays).
    lookback:
        Number of candles to examine.
    efficiency_min:
        Direction efficiency threshold below which whipsaw is declared.
    min_range_pct:
        Minimum total range as % of price for the gate to be active.

    Returns
    -------
    (is_whipsaw, reason, efficiency)
        * ``is_whipsaw``: True when BTC is in whipsaw regime.
        * ``reason``: Human-readable explanation (empty when not whipsaw).
        * ``efficiency``: Computed efficiency value (0.0 on data error).
    """
    if not btc_candles_15m:
        return False, "", 0.0

    highs = btc_candles_15m.get("high", [])
    lows = btc_candles_15m.get("low", [])
    closes = btc_candles_15m.get("close", [])

    if len(highs) < lookback + 1 or len(lows) < lookback + 1 or len(closes) < lookback + 1:
        return False, "", 0.0

    try:
        h = [float(x) for x in highs[-lookback:]]
        lo = [float(x) for x in lows[-lookback:]]
        c = [float(x) for x in closes[-(lookback + 1):]]

        reference_price = c[-1]
        if reference_price <= 0:
            return False, "", 0.0

        total_range = sum(h[i] - lo[i] for i in range(lookback))
        net_move = abs(c[-1] - c[0])

        total_range_pct = total_range / reference_price * 100.0

        # Guard: if BTC barely moved, don't classify as whipsaw
        if total_range_pct < min_range_pct:
            return False, "", total_range / total_range if total_range > 0 else 0.0

        if total_range <= 0:
            return False, "", 0.0

        efficiency = net_move / total_range

        if efficiency < efficiency_min:
            reason = (
                f"BTC whipsaw: 15m direction_efficiency={efficiency:.2f} "
                f"(< {efficiency_min:.2f} threshold), "
                f"total_range={total_range_pct:.2f}% over {lookback} candles"
            )
            return True, reason, efficiency

        return False, "", efficiency

    except Exception as exc:
        log.debug("evaluate_btc_whipsaw error (fail-open): {}", exc)
        return False, "", 0.0


class BtcRegimeKillSwitch:
    """Stateless evaluator wrapping :func:`evaluate_btc_whipsaw`.

    Keeps a rolling log of the last kill reason for the ``/diag`` command.
    """

    def __init__(self) -> None:
        self._last_kill_reason: str = ""
        self._kill_count: int = 0

    def check(
        self,
        sig: Any,
        btc_candles_15m: Optional[Dict[str, Any]],
    ) -> Tuple[bool, str]:
        """Return ``(blocked, reason)``.

        ``blocked=True`` means the signal should be suppressed.
        Always fails open when REGIME_KILL_ENABLED is False or BTC data
        is unavailable.
        """
        if not REGIME_KILL_ENABLED:
            return False, ""

        setup_class = (getattr(sig, "setup_class", "") or "").upper()
        if setup_class in REGIME_KILL_EXEMPT_SETUPS:
            return False, ""

        if not btc_candles_15m:
            return False, ""

        is_whipsaw, reason, _eff = evaluate_btc_whipsaw(btc_candles_15m)
        if is_whipsaw:
            self._last_kill_reason = reason
            self._kill_count += 1
            return True, reason

        return False, ""

    @property
    def last_kill_reason(self) -> str:
        return self._last_kill_reason

    @property
    def kill_count(self) -> int:
        return self._kill_count
