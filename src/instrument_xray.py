"""What KIND of instrument is this — read from data the engine already has.

`docs/PLAN_AI_TRADE_GOVERNOR_V2.md` §8. Two days of manual analysis over nine
open signals produced exactly **one** actionable finding, and it came from three
numbers rather than from any model: BULLAUSDT was a $29M-market-cap meme token
up **+48.6% on the day** on **$2.8M** of spot volume. The governor sees
R-multiple and distance-to-TP1 and cannot tell that instrument from an $8.4B
LINK — it treats them identically.

Why this does NOT call a market-data vendor
-------------------------------------------
Market cap is the one figure of the three that no engine surface carries, and
fetching it means mapping a Binance symbol onto a vendor's coin id. That mapping
is *silently* wrong rather than loudly wrong — several listed tokens share the
ticker ``BULLA``, and picking the wrong one yields a confident market cap for a
different asset. This repo's whole record is that a confidently wrong number
outlives a missing one, so market cap is **named as absent** here rather than
guessed at, and the two numbers that actually did the work are read from
`pair_manager`, which already receives both from Binance's own 24h ticker.

So: no new vendor, no network call, no symbol mapping that can describe the
wrong coin, and no cost on any loop.

A feature, never a policy
-------------------------
The classification below is stamped and **consumed by nothing**. That is not
timidity, it is the finding: every fact in the manual BULLA thesis was true —
micro-cap, parabolic, thin — and the conclusion drawn from them ("harvest
early") was **wrong by 2.3 percentage points** against simply holding, on the
single best trade of that day. Identifying the instrument is a measurement;
what to do about it is a question a scored window answers, not this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

#: Liquidity bands, in 24h quote volume. Deliberately the SAME thresholds
#: `pair_manager.classify_pair_tier` already uses — a second opinion about a
#: question the engine has already answered is a mirror, and mirrors drift.
MAJOR_VOLUME_USD = 500_000_000.0
MIDCAP_VOLUME_USD = 50_000_000.0

#: A day's move at or beyond this is "parabolic" for the purposes of the label.
#: Chosen from the case that prompted the module (BULLA at +48.6%) and from the
#: delivered book's ordinary range, and deliberately generous: this flag exists
#: to make an unusual instrument *visible*, not to gate anything, so a false
#: positive costs a column and a false negative costs the finding.
PARABOLIC_MOVE_PCT = 25.0

#: Below this, a day's move of that size is happening on very little money.
THIN_VOLUME_USD = 10_000_000.0

WHY_OK = "ok"
WHY_NO_PAIR = "pair_not_in_universe"
WHY_NO_VENDOR = "no_vendor_wired"
WHY_NOT_REPORTED = "not_reported_by_source"


@dataclass(frozen=True)
class InstrumentXray:
    """One instrument's character, and what we could not observe about it."""

    symbol: str
    volume_24h_usd: Optional[float]
    change_24h_pct: Optional[float]
    liquidity: str                      # major | midcap | altcoin | unknown
    parabolic: Optional[bool]
    thin: Optional[bool]
    is_new: Optional[bool]
    readable: bool
    reason: str = WHY_OK
    #: Named, not omitted. An absent row would read as an ordinary instrument;
    #: this says we cannot see the figure that most separates a micro-cap meme
    #: from a major, and why.
    market_cap_usd: Optional[float] = None
    market_cap_reason: str = WHY_NO_VENDOR

    def as_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "readable": self.readable,
            "reason": self.reason,
            "volume_24h_usd": self.volume_24h_usd,
            "change_24h_pct": self.change_24h_pct,
            "liquidity": self.liquidity,
            "parabolic": self.parabolic,
            "thin": self.thin,
            "is_new": self.is_new,
            "market_cap_usd": self.market_cap_usd,
            "market_cap_reason": self.market_cap_reason,
        }

    @classmethod
    def unknown(cls, symbol: str, reason: str) -> "InstrumentXray":
        """We could not observe this instrument at all.

        Every field is None rather than zero: a pair missing from the universe
        is not a pair with no volume, and rendering the second for the first is
        how a blank becomes a finding.
        """
        return cls(
            symbol=symbol, volume_24h_usd=None, change_24h_pct=None,
            liquidity="unknown", parabolic=None, thin=None, is_new=None,
            readable=False, reason=reason,
        )


def _liquidity_band(volume: Optional[float]) -> str:
    if volume is None:
        return "unknown"
    if volume >= MAJOR_VOLUME_USD:
        return "major"
    if volume >= MIDCAP_VOLUME_USD:
        return "midcap"
    return "altcoin"


def classify(symbol: str, pair: Any) -> InstrumentXray:
    """Describe one instrument from its `pair_manager.PairInfo`.

    ``pair`` is the real `PairInfo`, read by name — ``volume_24h_usd``,
    ``change_24h_signed_pct``, ``is_new``. The **signed** change is the one
    read on purpose: `volatility_24h` is deliberately absolute, and a reader
    taking that would render a token down 30% identically to one up 30%, which
    is a defect `pair_manager`'s own comment records having already shipped
    once.
    """
    if pair is None:
        return InstrumentXray.unknown(symbol, WHY_NO_PAIR)

    volume = _opt_float(getattr(pair, "volume_24h_usd", None))
    change = _opt_float(getattr(pair, "change_24h_signed_pct", None))
    is_new = getattr(pair, "is_new", None)

    return InstrumentXray(
        symbol=symbol,
        volume_24h_usd=volume,
        change_24h_pct=change,
        liquidity=_liquidity_band(volume),
        # None, never False, when the source did not report a move: "we could
        # not ask" and "it did not move" are different facts.
        parabolic=None if change is None else abs(change) >= PARABOLIC_MOVE_PCT,
        thin=None if volume is None else volume < THIN_VOLUME_USD,
        is_new=None if is_new is None else bool(is_new),
        readable=True,
        reason=WHY_OK if change is not None else WHY_NOT_REPORTED,
    )


def _opt_float(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if out == out else None


def from_getter(symbol: str, pair_getter: Any) -> InstrumentXray:
    """`classify` with the pair looked up, or a named unknown. Never raises."""
    if pair_getter is None:
        return InstrumentXray.unknown(symbol, WHY_NO_PAIR)
    try:
        pair = pair_getter(symbol)
    except Exception as exc:  # noqa: BLE001 — an X-ray is never worth a raise
        from src import fail_open

        # The real exception, not None: this counter exists so a genuine
        # failure stands out, and filling it with a placeholder is how it
        # stops doing that.
        fail_open.record("instrument_xray.pair_getter", exc)
        return InstrumentXray.unknown(symbol, WHY_NO_PAIR)
    return classify(symbol, pair)
