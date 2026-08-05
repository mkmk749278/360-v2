"""Declared Binance request weights — one table, one reader.

Every REST call this engine makes declares a weight, and
:mod:`src.rate_limiter` spends the per-minute budget against that declaration.
An **under-declared** weight is therefore not a cosmetic error: it makes the
limiter optimistic, so it keeps issuing requests believing it has budget it has
already spent, and the first symptom is a 429 or an IP ban rather than a warning.

That is not hypothetical. ``fetch_recent_trades`` declared ``weight=1`` for both
``/fapi/v1/trades`` (actual **5**) and ``/api/v3/trades`` (actual **25**) while
fetching ``limit=1000`` — a 5x and 25x under-declaration on the endpoint that
seeds the tick store, flagged as an open follow-up in ``ACTIVE_CONTEXT.md`` and
never acted on. This module exists so the next one fails CI instead.

Provenance is part of the data
------------------------------
Each entry records **where its number came from**, because "say which parts you
verified and which you inferred" applies to a constant as much as to a claim. An
entry marked ``VERIFIED`` was read from Binance's own endpoint documentation on
the stated date. An entry marked ``CARRIED`` was already in this codebase and is
preserved unchanged — it is not thereby confirmed, and it is the first thing to
re-check if the limiter starts disagreeing with the exchange.

The authority is still the exchange, not this file
--------------------------------------------------
``binance.py`` syncs the live counter from the ``x-mbx-used-weight-1m`` response
header on every call, so the *budget* is measured rather than assumed. This table
governs how much we believe a request will cost **before** we make it, which is
what the limiter needs in order to decide whether to make it at all. The two are
complementary: the header corrects us after the fact, this table stops us
overspending before it.

Vendor limits, for reference (documented 2026-08-05):

* ``REQUEST_WEIGHT`` — 2,400/min per IP for USDⓈ-M futures; 6,000/min for spot.
* WebSocket **market streams consume no REQUEST_WEIGHT** at any message rate.
  This is why the price-action program moves order flow and depth onto
  WebSocket rather than polling them — see ``docs/PRICE_ACTION_PROGRAM.md`` §4.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Union

# ---------------------------------------------------------------------------
# Provenance markers
# ---------------------------------------------------------------------------

#: Read from Binance's endpoint documentation on this date.
VERIFIED = "verified:2026-08-05"
#: Pre-existing value preserved from the call site it was moved out of. NOT
#: independently confirmed — re-check this first if the limiter drifts.
CARRIED = "carried"


class Weight:
    """A declared weight and where its number came from."""

    __slots__ = ("value", "source", "note")

    def __init__(self, value: int, source: str, note: str = "") -> None:
        self.value = value
        self.source = source
        self.note = note

    def __int__(self) -> int:
        return self.value

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"Weight({self.value}, {self.source!r})"


# ---------------------------------------------------------------------------
# Fixed-weight endpoints
# ---------------------------------------------------------------------------

FIXED: Dict[str, Weight] = {
    # --- the defect this module was written for -----------------------------
    # Declared 1, actual 5. Under-declared 5x on every symbol seed.
    "/fapi/v1/trades": Weight(5, VERIFIED, "Recent Trades List; limit max 1000"),
    # Declared 1, actual 25. Under-declared 25x.
    "/api/v3/trades": Weight(25, VERIFIED, "Recent Trades List; limit max 1000"),
    # --- order flow and depth, for the price-action program ------------------
    # Fixed regardless of limit. History is 24h only and any
    # startTime/endTime window must be under 1 hour — which is precisely why
    # this is a WebSocket subscription in the program and not a poller.
    "/fapi/v1/aggTrades": Weight(20, VERIFIED, "fixed; 24h history, <1h window"),
    # --- already correct at their call sites, centralised here ---------------
    "/api/v3/ping": Weight(1, CARRIED),
    "/fapi/v1/ticker/bookTicker": Weight(2, CARRIED, "no symbol param = all symbols"),
    "/api/v3/ticker/bookTicker": Weight(2, CARRIED, "no symbol param = all symbols"),
    "/fapi/v1/exchangeInfo": Weight(10, CARRIED),
    "/api/v3/exchangeInfo": Weight(10, CARRIED),
    # No symbol param = whole board.
    "/fapi/v1/ticker/24hr": Weight(40, CARRIED, "no symbol param = all symbols"),
    "/api/v3/ticker/24hr": Weight(40, CARRIED, "no symbol param = all symbols"),
}

#: Single-symbol variants of endpoints whose all-symbol form is far heavier.
#: Keyed the same way but selected explicitly by the caller, because the
#: difference between them is a factor of 40 and must never be implicit.
FIXED_SINGLE_SYMBOL: Dict[str, Weight] = {
    "/fapi/v1/ticker/24hr": Weight(1, CARRIED, "with symbol param"),
    "/api/v3/ticker/24hr": Weight(1, CARRIED, "with symbol param"),
}


# ---------------------------------------------------------------------------
# Weight-by-limit endpoints
# ---------------------------------------------------------------------------

def _klines_weight(limit: int) -> int:
    """Kline weight tiers.

    CARRIED from ``BinanceClient.fetch_klines``, whose docstring called these
    "Binance exact". I could not re-read the vendor table during the
    2026-08-05 audit — the doc page did not render the weight section and the
    live ``exchangeInfo`` endpoint returns HTTP 451 to our build sandbox — so
    this is preserved rather than confirmed, and it is marked as such instead
    of being presented as verified.
    """
    if limit < 100:
        return 1
    if limit < 500:
        return 2
    if limit <= 1000:
        return 5
    return 10


def _depth_weight(limit: int) -> int:
    """Order-book weight tiers. VERIFIED 2026-08-05.

    limit 5/10/20/50 -> 2 · 100 -> 5 · 500 -> 10 · 1000 -> 20.

    Kept even though the scan path deliberately uses ``bookTicker`` instead:
    the program's Phase 2c adds a real depth book over WebSocket, and any REST
    depth call that appears later must cost what it actually costs. Polling 75
    symbols at ``limit=20`` on the 15s scan cadence would be 600 weight/minute
    — a quarter of the futures budget — which is the arithmetic that sent depth
    to WebSocket in the first place.
    """
    if limit <= 50:
        return 2
    if limit <= 100:
        return 5
    if limit <= 500:
        return 10
    return 20


BY_LIMIT: Dict[str, Callable[[int], int]] = {
    "/fapi/v1/klines": _klines_weight,
    "/api/v3/klines": _klines_weight,
    "/fapi/v1/depth": _depth_weight,
    "/api/v3/depth": _depth_weight,
}

#: Provenance for the by-limit endpoints, so the audit test can report it.
BY_LIMIT_SOURCE: Dict[str, str] = {
    "/fapi/v1/klines": CARRIED,
    "/api/v3/klines": CARRIED,
    "/fapi/v1/depth": VERIFIED,
    "/api/v3/depth": VERIFIED,
}


def weight_for(
    path: str,
    *,
    limit: Optional[int] = None,
    single_symbol: bool = False,
) -> int:
    """The declared weight for *path*.

    Raises ``KeyError`` for an unknown endpoint rather than defaulting to 1.
    **Absence of knowledge is not permission**: a silent default of 1 on a new
    endpoint is exactly the under-declaration this module exists to prevent, and
    it would be invisible until the limiter had already overspent. A new
    endpoint must be declared here before it can be called.
    """
    if path in BY_LIMIT:
        if limit is None:
            raise ValueError(
                f"{path} is weight-by-limit; caller must pass limit="
            )
        return BY_LIMIT[path](int(limit))
    if single_symbol and path in FIXED_SINGLE_SYMBOL:
        return FIXED_SINGLE_SYMBOL[path].value
    try:
        return FIXED[path].value
    except KeyError:
        raise KeyError(
            f"No declared Binance weight for {path!r}. Add it to "
            f"src/binance_weights.py with its provenance before calling it — "
            f"an undeclared weight makes the rate limiter optimistic."
        ) from None


def known_paths() -> set[str]:
    """Every endpoint this table can price. Used by the audit test."""
    return set(FIXED) | set(BY_LIMIT)


def describe() -> Dict[str, Dict[str, Union[int, str]]]:
    """The table as data, for the ops data-intake surface.

    Rendered rather than mirrored: the ops page shows what we *believe* each
    call costs beside what the exchange's own header says we have spent, so a
    disagreement between the two is visible instead of being discovered as a
    ban.
    """
    out: Dict[str, Dict[str, Union[int, str]]] = {}
    for path, w in FIXED.items():
        out[path] = {"weight": w.value, "source": w.source, "note": w.note}
    for path in BY_LIMIT:
        out[path] = {
            "weight": -1,  # sentinel: depends on limit
            "source": BY_LIMIT_SOURCE.get(path, CARRIED),
            "note": "weight varies by limit",
        }
    return out
