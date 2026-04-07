"""Cross-Asset Correlation – BTC/ETH "Sneeze" Filter.

If a major asset (BTC or ETH) is in a high-volatility or dumping regime,
altcoin LONG signals are paused or rejected to prevent getting caught in
a market-wide flush.  When BTC is dumping, SHORT signals get a confidence
boost because the macro tailwind confirms the bearish setup.

Design notes
------------
* ``AssetState`` is a lightweight dataclass that accepts data from any source
  (live regime detector, backtesting, mock data).
* The ``trend`` field maps naturally to the output of :mod:`src.regime` or
  any external macro classifier.
* Fails open when no asset states are provided.
* Returns ``(allowed, reason, confidence_adj)`` where ``confidence_adj`` is a
  signed float to add to the signal's confidence score (+5 = boost, -10 = penalty).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

from src.utils import get_logger

log = get_logger("cross_asset")

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

#: Trend labels that trigger the altcoin long pause.
BEARISH_TREND_LABELS: frozenset[str] = frozenset({
    "DUMPING",
    "HIGH_VOLATILITY_DOWN",
    "DOWNTREND",
    "BEAR",
    "BEARISH",
    "CRASH",
})

#: Trend labels that indicate a strong bullish move — trigger altcoin short pause.
BULLISH_TREND_LABELS: frozenset[str] = frozenset({
    "PUMPING",
    "HIGH_VOLATILITY_UP",
    "UPTREND",
    "BULL",
    "BULLISH",
})

#: Volatility labels that trigger a downgrade of altcoin long confidence.
HIGH_VOLATILITY_LABELS: frozenset[str] = frozenset({
    "HIGH",
    "EXTREME",
    "HIGH_VOLATILITY",
    "HIGH_VOLATILITY_DOWN",
    "HIGH_VOLATILITY_UP",
    "VOLATILE",
})

# ---------------------------------------------------------------------------
# Graduated correlation thresholds for cross-asset gating
# ---------------------------------------------------------------------------
_CORR_VERY_LOW: float = 0.2   # Below this: pair is independent, no penalty
_CORR_LOW: float = 0.5        # Below this: minor penalty suggested
_CORR_HIGH: float = 0.8       # At or above this: hard block (for LONGs)

#: BTC % change threshold below which BTC is considered "dumping" for gate logic.
#: Expressed as a fraction (−0.015 = −1.5%).
_BTC_DUMP_THRESHOLD: float = -0.015

#: Default correlation used when none is available (conservative assumption).
_DEFAULT_BTC_CORRELATION: float = 0.7

#: Symbols treated as "major" assets that can affect altcoins.
#: Extend this set as needed (e.g. add "BNBUSDT" for BNB-chain tokens).
DEFAULT_MAJOR_SYMBOLS: frozenset[str] = frozenset({"BTCUSDT", "ETHUSDT"})


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class AssetState:
    """Current market state of a single asset.

    Attributes
    ----------
    symbol:
        Trading pair symbol (e.g. ``"BTCUSDT"``).
    trend:
        Trend label string.  Expected values include: ``"BULLISH"``,
        ``"BEARISH"``, ``"DUMPING"``, ``"NEUTRAL"``, ``"RANGING"``,
        ``"HIGH_VOLATILITY_DOWN"``, ``"HIGH_VOLATILITY_UP"``, etc.
        Case-insensitive comparison is used internally.
    volatility:
        Volatility label string.  Expected values: ``"NORMAL"``, ``"HIGH"``,
        ``"EXTREME"``.  ``None`` means unknown.
    price_change_pct:
        Optional recent percentage price change expressed as a fraction
        (e.g. ``-0.015`` for −1.5 %).
    """

    symbol: str
    trend: str = "NEUTRAL"
    volatility: Optional[str] = None
    price_change_pct: Optional[float] = None
    extra: dict = field(default_factory=dict)

    def is_bearish(self) -> bool:
        """Return True when the trend is classified as bearish/dumping."""
        return self.trend.upper() in BEARISH_TREND_LABELS

    def is_high_volatility(self) -> bool:
        """Return True when volatility is high or extreme."""
        if self.volatility is None:
            return False
        return self.volatility.upper() in HIGH_VOLATILITY_LABELS

    def is_dumping(self) -> bool:
        """Return True when recent price change is below the dump threshold."""
        if self.price_change_pct is not None:
            return self.price_change_pct < _BTC_DUMP_THRESHOLD
        return self.is_bearish()


# ---------------------------------------------------------------------------
# Core public API
# ---------------------------------------------------------------------------


def check_cross_asset_gate(
    signal_direction: str,
    signal_symbol: str,
    asset_states: Sequence[AssetState],
    major_symbols: Optional[frozenset[str]] = None,
    btc_correlation: Optional[float] = None,
) -> tuple[bool, str, float]:
    """Direction-aware, graduated cross-asset gate.

    Returns ``(allowed, reason, confidence_adj)`` where:
    - ``allowed`` is ``False`` only for hard blocks.
    - ``confidence_adj`` is a float to add to confidence (+ve = boost, -ve = penalty).

    Graduated by correlation strength:
    - corr ≥ 0.8:  LONG hard-blocked when BTC dumps; SHORT boosted +5.
    - 0.5 ≤ corr < 0.8: LONG soft -10; SHORT soft +3.
    - 0.2 ≤ corr < 0.5: LONG soft -3; SHORT soft +1.
    - corr < 0.2: no impact (meme coins / near-zero correlation).

    SHORTs are still blocked when BTC is strongly pumping (same as before).

    Parameters
    ----------
    signal_direction:
        ``"LONG"`` or ``"SHORT"``.
    signal_symbol:
        Symbol generating the signal.  Skipped for major assets themselves.
    asset_states:
        List of :class:`AssetState` objects for the major reference assets.
    major_symbols:
        Set of symbols considered "major".  Defaults to BTC + ETH.
    btc_correlation:
        Optional rolling Pearson correlation vs BTC.  Defaults to 0.7
        (conservative assumption) when ``None``.

    Returns
    -------
    ``(allowed, reason, confidence_adj)``
    """
    if not asset_states:
        return True, "", 0.0

    direction = signal_direction.upper()
    _major = major_symbols if major_symbols is not None else DEFAULT_MAJOR_SYMBOLS

    # If the signal itself is a major asset, skip the correlation filter
    if signal_symbol.upper() in _major:
        return True, "", 0.0

    # Use default correlation when none provided
    corr = btc_correlation if btc_correlation is not None else _DEFAULT_BTC_CORRELATION
    abs_corr = abs(corr)

    for state in asset_states:
        if state.symbol.upper() not in _major:
            continue

        btc_dumping = state.is_dumping()
        btc_pumping = state.trend.upper() in BULLISH_TREND_LABELS

        if direction == "LONG" and btc_dumping:
            if abs_corr < _CORR_VERY_LOW:
                # Near-zero correlation: no impact
                continue
            elif abs_corr < _CORR_LOW:
                return (
                    True,
                    f"Cross-asset: {state.symbol} dumping (corr={corr:.2f}) — minor LONG penalty",
                    -3.0,
                )
            elif abs_corr < _CORR_HIGH:
                return (
                    True,
                    f"Cross-asset: {state.symbol} dumping (corr={corr:.2f}) — LONG soft penalty",
                    -10.0,
                )
            else:
                # High correlation + BTC dumping → hard block LONG
                return (
                    False,
                    f"Cross-asset: {state.symbol} dumping (corr={corr:.2f}) — LONG hard-blocked",
                    0.0,
                )

        elif direction == "SHORT" and btc_dumping:
            # BTC dumping confirms SHORT thesis
            if abs_corr < _CORR_VERY_LOW:
                continue
            elif abs_corr < _CORR_LOW:
                return True, f"Cross-asset: BTC dump confirms SHORT (corr={corr:.2f})", 1.0
            elif abs_corr < _CORR_HIGH:
                return True, f"Cross-asset: BTC dump confirms SHORT (corr={corr:.2f})", 3.0
            else:
                return True, f"Cross-asset: BTC dump strongly confirms SHORT (corr={corr:.2f})", 5.0

        elif direction == "SHORT" and btc_pumping:
            # BTC strongly pumping → short is counter-trend, block when correlated
            if abs_corr < _CORR_LOW:
                continue
            return (
                False,
                f"Cross-asset: {state.symbol} is {state.trend.upper()} — altcoin SHORT paused",
                0.0,
            )

        elif direction == "LONG" and (state.is_high_volatility() and not btc_pumping and not btc_dumping):
            # High volatility in non-directional state — soft penalty for LONGs
            if abs_corr >= _CORR_HIGH:
                return (
                    False,
                    f"Cross-asset: {state.symbol} high volatility ({state.volatility}) — LONG paused",
                    0.0,
                )

    return True, "", 0.0


def get_dominant_market_state(
    asset_states: Sequence[AssetState],
    major_symbols: Optional[frozenset[str]] = None,
) -> str:
    """Summarise the overall market tone from major asset states.

    Returns one of: ``"RISK_ON"``, ``"RISK_OFF"``, ``"VOLATILE"``, or
    ``"NEUTRAL"``.

    Parameters
    ----------
    asset_states:
        States for the reference assets.
    major_symbols:
        Set of symbols to consider.  Defaults to BTC + ETH.

    Returns
    -------
    Market tone label string.
    """
    _major = major_symbols if major_symbols is not None else DEFAULT_MAJOR_SYMBOLS

    relevant = [s for s in asset_states if s.symbol.upper() in _major]
    if not relevant:
        return "NEUTRAL"

    bearish_count = sum(1 for s in relevant if s.is_bearish())
    volatile_count = sum(1 for s in relevant if s.is_high_volatility())
    bullish_count = sum(
        1 for s in relevant
        if s.trend.upper() in {"BULLISH", "UPTREND", "BULL", "PUMPING", "HIGH_VOLATILITY_UP"}
    )

    total = len(relevant)

    if bearish_count >= total // 2 + 1:
        return "RISK_OFF"
    if volatile_count >= total // 2 + 1:
        return "VOLATILE"
    if bullish_count >= total // 2 + 1:
        return "RISK_ON"
    return "NEUTRAL"
