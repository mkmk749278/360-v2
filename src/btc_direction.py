"""BTC direction soft-penalty gate.

OWNER_BRIEF §2.1 doctrine: alts are heavily BTC-correlated.  When BTC is
in a defined 1H + 4H trend, alt signals moving counter-BTC tend to get
swept on the next BTC impulse.  Production data 2026-05-18 (last-100
window): LONG signals fired 27% full-SL hit rate vs SHORT at 7% — the
asymmetry mapped 1:1 onto a TRENDING_DOWN-skewed market regime.

This gate applies a soft penalty (not a hard block — per scalping
doctrine §5: ``soft penalties over hard blocks``) when:

* BTC 1H AND 4H are both BEARISH and the signal is LONG, OR
* BTC 1H AND 4H are both BULLISH and the signal is SHORT.

The both-TFs requirement matches the existing per-pair HTF mismatch
penalty pattern (``_SR_FLIP_HTF_MISMATCH_PENALTY`` and friends): the
1H-only signal is too noisy to act on, so we require 4H confirmation.

Exempt setups (tape-driven counter-tape paths) bypass the gate
entirely.  Their thesis is to fade BTC's macro move; penalising them
would suppress the exact signal they exist to capture.

Fail-open when BTC indicator or candle data is unavailable (warmup,
data drop) — soft-penalty doctrine never blocks on missing data.
"""
from __future__ import annotations

from typing import Optional, Tuple


# Setups exempt from the BTC direction penalty.  Tape-driven paths
# whose thesis is fading the macro tape — applying the penalty would
# suppress the exact signal they exist to capture.
_BTC_DIR_EXEMPT_SETUPS: frozenset[str] = frozenset({
    "WHALE_MOMENTUM",
    "FUNDING_EXTREME_SIGNAL",
    "LIQUIDATION_REVERSAL",
})


def _classify_btc_1h(btc_indicators_1h: Optional[dict]) -> Optional[str]:
    """Classify BTC 1H direction from EMA21 / EMA50 alignment + slope.

    Returns ``"BULLISH"`` / ``"BEARISH"`` / ``"NEUTRAL"`` / ``None``.
    ``None`` indicates insufficient data — callers should treat as
    fail-open (no penalty).
    """
    if not btc_indicators_1h:
        return None
    ema21 = btc_indicators_1h.get("ema21_last")
    ema50 = btc_indicators_1h.get("ema50_last")
    if ema21 is None or ema50 is None:
        return None
    try:
        ema21_f = float(ema21)
        ema50_f = float(ema50)
    except (TypeError, ValueError):
        return None
    ema21_prev = btc_indicators_1h.get("ema21_prev")
    # Slope: when ema21_prev unavailable (warmup), accept alignment-only.
    slope_pos = ema21_prev is None or float(ema21_prev) < ema21_f
    slope_neg = ema21_prev is None or float(ema21_prev) > ema21_f
    if ema21_f > ema50_f and slope_pos:
        return "BULLISH"
    if ema21_f < ema50_f and slope_neg:
        return "BEARISH"
    return "NEUTRAL"


def _classify_btc_4h(
    btc_indicators_4h: Optional[dict],
    btc_candles_4h: Optional[dict],
) -> Optional[str]:
    """Classify BTC 4H direction.  Same EMA21 vs EMA50 alignment as
    1H but adds a close-on-the-right-side-of-EMA-fast check (mirrors
    the contract used by ``src.mtf._classify_trend`` and
    ``ScalpChannel._classify_htf_trend``).

    Returns ``"BULLISH"`` / ``"BEARISH"`` / ``"NEUTRAL"`` / ``None``.
    """
    if not btc_indicators_4h:
        return None
    ema21 = btc_indicators_4h.get("ema21_last")
    ema50 = btc_indicators_4h.get("ema50_last")
    if ema21 is None or ema50 is None:
        return None
    try:
        ema21_f = float(ema21)
        ema50_f = float(ema50)
    except (TypeError, ValueError):
        return None
    cd = btc_candles_4h or {}
    closes = cd.get("close") or []
    if not closes:
        # Alignment-only fallback when candle data missing.
        if ema21_f > ema50_f:
            return "BULLISH"
        if ema21_f < ema50_f:
            return "BEARISH"
        return "NEUTRAL"
    try:
        close_f = float(closes[-1])
    except (TypeError, ValueError):
        return None
    if ema21_f > ema50_f and close_f > ema21_f:
        return "BULLISH"
    if ema21_f < ema50_f and close_f < ema21_f:
        return "BEARISH"
    return "NEUTRAL"


def check_symbol_direction_gate(
    signal_direction: str,
    sym_indicators_1h: Optional[dict],
    sym_indicators_4h: Optional[dict] = None,
    sym_candles_4h: Optional[dict] = None,
    *,
    setup_class: Optional[str] = None,
) -> Tuple[bool, str]:
    """Per-symbol direction soft-penalty gate.

    Mirrors ``check_btc_direction_gate`` but uses the signal's own symbol's
    1H / 4H EMA trend instead of BTC's macro trend.  Catches opposite-direction
    signals on pairs that are in a clear local downtrend or uptrend even when
    BTC itself is range-bound (QUIET regime).

    Exempt setups — counter-trend by design, should not be penalised for
    trading against the pair's own recent structure:
      * LIQUIDITY_SWEEP_REVERSAL — entry IS the sweep reversal against recent structure
      * FAILED_AUCTION_RECLAIM   — entry IS counter to the failed breakout direction
      * WHALE_MOMENTUM, FUNDING_EXTREME_SIGNAL, LIQUIDATION_REVERSAL — tape-driven

    Returns ``(False, reason)`` when the pair's 1H AND 4H both oppose the
    signal direction.  ``(True, "")`` on fail-open (missing data, NEUTRAL, exempt).
    """
    _SYM_DIR_EXEMPT: frozenset = frozenset({
        "LIQUIDITY_SWEEP_REVERSAL",
        "FAILED_AUCTION_RECLAIM",
        "WHALE_MOMENTUM",
        "FUNDING_EXTREME_SIGNAL",
        "LIQUIDATION_REVERSAL",
    })
    if setup_class and setup_class.upper() in _SYM_DIR_EXEMPT:
        return True, ""
    trend_1h = _classify_btc_1h(sym_indicators_1h)
    trend_4h = _classify_btc_4h(sym_indicators_4h, sym_candles_4h)
    if trend_1h is None or trend_4h is None:
        return True, ""  # fail-open on missing data
    direction = signal_direction.upper() if signal_direction else ""
    if direction == "LONG" and trend_1h == "BEARISH" and trend_4h == "BEARISH":
        return False, "sym_1h_4h_both_bearish_long"
    if direction == "SHORT" and trend_1h == "BULLISH" and trend_4h == "BULLISH":
        return False, "sym_1h_4h_both_bullish_short"
    return True, ""


def check_btc_direction_gate(
    signal_direction: str,
    btc_indicators_1h: Optional[dict],
    btc_indicators_4h: Optional[dict] = None,
    btc_candles_4h: Optional[dict] = None,
    *,
    setup_class: Optional[str] = None,
) -> Tuple[bool, str]:
    """Pipeline gate: soft penalty for counter-BTC-trend signals.

    Returns ``(False, reason)`` when BTC 1H AND 4H both oppose the
    signal's direction (and the setup is not exempt).  Otherwise
    returns ``(True, "")`` — including all fail-open cases (missing
    data, NEUTRAL BTC, exempt setup).

    Parameters
    ----------
    signal_direction:
        ``"LONG"`` or ``"SHORT"`` (case-insensitive).
    btc_indicators_1h:
        BTC 1H indicator dict (``ema21_last``, ``ema50_last``,
        ``ema21_prev``).  ``None`` → fail-open.
    btc_indicators_4h:
        BTC 4H indicator dict (same shape).  ``None`` → fail-open.
    btc_candles_4h:
        BTC 4H candle dict (``close`` series for the close-vs-EMA
        confirmation).  Optional; alignment-only used when absent.
    setup_class:
        Setup-class name (uppercase) used to check the exempt set.

    Returns
    -------
    ``(allowed, reason)``
        ``False`` + diagnostic reason when the gate triggers,
        ``True`` + empty string otherwise.
    """
    if setup_class and setup_class.upper() in _BTC_DIR_EXEMPT_SETUPS:
        return True, ""
    trend_1h = _classify_btc_1h(btc_indicators_1h)
    trend_4h = _classify_btc_4h(btc_indicators_4h, btc_candles_4h)
    if trend_1h is None or trend_4h is None:
        return True, ""  # fail-open on missing data
    direction = signal_direction.upper() if signal_direction else ""
    if direction == "LONG" and trend_1h == "BEARISH" and trend_4h == "BEARISH":
        return False, "btc_1h_4h_both_bearish_long"
    if direction == "SHORT" and trend_1h == "BULLISH" and trend_4h == "BULLISH":
        return False, "btc_1h_4h_both_bullish_short"
    return True, ""


def _ema_fan_pct(indicators: Optional[dict]) -> Optional[float]:
    """EMA21/50 fan width as a percent of EMA50 — a trend-strength proxy.

    A strong/parabolic mover fans the EMAs wide apart (SYNUSDT-class: >5%); a
    gently-trending pair keeps them within ~1-2%.  Returns ``None`` on missing or
    invalid data so callers fail-open.
    """
    if not indicators:
        return None
    ema21 = indicators.get("ema21_last")
    ema50 = indicators.get("ema50_last")
    if ema21 is None or ema50 is None:
        return None
    try:
        e21 = float(ema21)
        e50 = float(ema50)
    except (TypeError, ValueError):
        return None
    if e50 <= 0:
        return None
    return abs(e21 - e50) / e50 * 100.0


def check_countertrend_mover_block(
    signal_direction: str,
    sym_indicators_1h: Optional[dict],
    sym_indicators_4h: Optional[dict],
    sym_candles_4h: Optional[dict],
    *,
    setup_class: Optional[str],
    blocked_setups: frozenset,
    min_fan_pct: float,
) -> Tuple[bool, str]:
    """HARD-block a counter-trend reversal that fades a CONFIRMED STRONG mover.

    The per-symbol direction gate (``check_symbol_direction_gate``) is a SOFT
    penalty AND exempts LSR/FAR by design — so a reversal fading a parabolic
    mover receives no penalty at all (SYNUSDT: +300%/7d, 4h+1h both stacked up,
    repeatedly SHORTED by LIQUIDITY_SWEEP_REVERSAL → full SL).  Fading a confirmed
    strong mover is structural impossibility, the one case §3.2 #5 reserves a hard
    block for.

    Returns ``(False, reason)`` — block — only when ALL hold:
      * ``setup_class`` is in ``blocked_setups`` (the counter-trend reversal/
        structure paths that fade trend), AND
      * the signal direction opposes BOTH the pair's 1H and 4H EMA trend, AND
      * the move is mover-grade — the wider of the 1H / 4H EMA21/50 fan
        ``>= min_fan_pct``.

    Otherwise ``(True, "")`` — fail-open on missing data, not-in-set, NEUTRAL/
    aligned trend, or a narrow fan (gently-trending pair → keep the soft penalty).
    """
    if not setup_class or setup_class.upper() not in blocked_setups:
        return True, ""
    direction = (signal_direction or "").upper()
    if direction not in ("LONG", "SHORT"):
        return True, ""
    trend_1h = _classify_btc_1h(sym_indicators_1h)
    trend_4h = _classify_btc_4h(sym_indicators_4h, sym_candles_4h)
    if trend_1h is None or trend_4h is None:
        return True, ""  # fail-open on missing data
    # The entry must oppose BOTH higher timeframes.
    if direction == "SHORT" and not (trend_1h == "BULLISH" and trend_4h == "BULLISH"):
        return True, ""
    if direction == "LONG" and not (trend_1h == "BEARISH" and trend_4h == "BEARISH"):
        return True, ""
    # Mover-grade strength: a wide EMA fan on either higher timeframe.  Narrow
    # fan = ordinary trend → leave it to the soft penalty, don't hard-block.
    fans = [f for f in (_ema_fan_pct(sym_indicators_1h), _ema_fan_pct(sym_indicators_4h)) if f is not None]
    if not fans:
        return True, ""
    strongest = max(fans)
    if strongest < min_fan_pct:
        return True, ""
    side = "bullish" if direction == "SHORT" else "bearish"
    return False, f"countertrend_mover_block_{side}_fan{strongest:.1f}pct"

