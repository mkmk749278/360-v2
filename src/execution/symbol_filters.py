"""Per-symbol Binance filter cache — LOT_SIZE / PRICE_FILTER / MIN_NOTIONAL.

Server-side execution (B18) places orders directly with Binance Futures.
Binance enforces per-symbol filters on every order:

* **LOT_SIZE.stepSize** — quantity must be a multiple of stepSize.
  Examples: BTCUSDT stepSize=0.001, ETHUSDT 0.001, DOGEUSDT 1,
  CHZUSDT 1, PROMUSDT 1.  Violation → ``code=-1111 "Precision is
  over the maximum defined for this asset"``.
* **PRICE_FILTER.tickSize** — price must be a multiple of tickSize
  (per-symbol; high-cap pairs allow more decimals than low-cap).
  Violation → ``code=-4014 "Price not increased by tick size"``
  or similar.
* **MIN_NOTIONAL.notional** — qty * price must be ≥ minNotional.
  Default $5–$10 on Futures.  Violation → ``code=-4164 "Order's
  notional must be no smaller than 5"``.

Without per-symbol rounding the engine sends qty with 8 decimals
universally, which only works for symbols whose stepSize ≤ 0.00000001.
For everything else (most major USDT-M pairs) Binance rejects every
order with -1111.

Design
------

* Module-level singleton ``_FILTERS: Dict[symbol_upper, SymbolFilters]``.
* Populated on engine boot via :func:`refresh_filters` (async; calls
  Binance ``/fapi/v1/exchangeInfo``).  Bootstrap kicks off a periodic
  refresh task at ``_REFRESH_INTERVAL_S`` so a Binance listing /
  delisting flows in without an engine restart.
* Synchronous helpers ``round_qty`` / ``round_price`` / ``meets_min_notional``
  read the cache.  Defensive default behaviour on cache miss: return
  the input unchanged so the FSM's downstream Binance error is the
  fallback diagnostic.  We DON'T silently floor to 0 — that'd hide
  the cache-miss as a "skipped" order in the dispatch log instead of
  surfacing the missing-filter telemetry.

Doctrine (OWNER_BRIEF B18)
--------------------------

This module reads ``/fapi/v1/exchangeInfo`` — a PUBLIC unsigned
endpoint — so it does NOT touch the signing service / KMS / secrets
path.  Safe to live in ``src/execution/`` alongside the other
order-path helpers.
"""

from __future__ import annotations

import asyncio
import math
from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.utils import get_logger

log = get_logger("execution.symbol_filters")


# Refresh once every 6 hours.  Binance listings happen weekly-ish;
# stepSize changes on existing pairs are rare but happen.  6h is a
# defensive cadence well inside the listing-announcement-to-first-
# trade window (Binance typically gives ~24h notice).
_REFRESH_INTERVAL_S: int = 6 * 60 * 60


# Binance's contractType marker for tokenised-stock / TradFi
# perpetuals — equity, ETF and commodity perps (TSLA, AAPL, WDC =
# Western Digital, …) that share the USDT-M venue but carry
# traditional-market microstructure (RTH price discovery, "Off-Hours"
# gaps, weekend closes).  Binance's own enum spells it
# "TRADIFI_PERPETUAL" (sic — not a typo on our side).
#
# Two reasons they must never enter the scanning / dispatch universe:
#   1. Every chartist-eye component assumes 24/7 crypto microstructure
#      and systematically mis-scores them.
#   2. They require a SEPARATE Binance agreement; an order on one is
#      rejected with -4411 "sign TradFi-Perps agreement" for any
#      account that hasn't signed it — even accounts that trade crypto
#      futures fine.  (2026-07-18: WDCUSDT slipped past the static
#      name-blacklist in pair_manager, a signal fired on it, and a paid
#      user's auto-trade order was rejected with -4411.)
#
# Captured here because this module already owns the one authoritative
# exchangeInfo pull; ``pair_manager`` reads :func:`is_tradfi_perp` to
# structurally exclude the whole class — current and future listings —
# instead of chasing individual tickers by hand.
_TRADFI_CONTRACT_TYPE = "TRADIFI_PERPETUAL"


@dataclass(frozen=True)
class SymbolFilters:
    """Binance filter values needed for order construction.

    All values are absolute (not log-scale).  ``min_notional`` is in
    quote currency (USDT for USDT-M futures).
    """

    symbol: str
    step_size: float  # LOT_SIZE.stepSize — qty multiple
    tick_size: float  # PRICE_FILTER.tickSize — price multiple
    min_qty: float    # LOT_SIZE.minQty
    min_notional: float  # MIN_NOTIONAL.notional (or NOTIONAL.minNotional)


_FILTERS: Dict[str, SymbolFilters] = {}
# Symbols whose contractType is TRADIFI_PERPETUAL — the tokenised-stock
# / TradFi-perp deny-set, rebuilt on every exchangeInfo refresh.
_TRADFI_PERPS: frozenset = frozenset()
_filters_lock = asyncio.Lock()


def _round_down_to_step(value: float, step: float) -> float:
    """Floor ``value`` to the nearest multiple of ``step``.

    Uses integer math after scaling to avoid the classic
    binary-float drift (e.g. ``0.3 / 0.1 == 2.9999...``).  Falls
    back to ``math.floor(value / step) * step`` when ``step`` isn't
    representable as a clean decimal.
    """
    if step <= 0:
        return value
    # Scale by the smallest power of 10 that makes ``step`` an
    # integer.  Caps at 10**12 so 1e-13 stepSizes (Binance has none
    # but defensively) don't blow up.
    scale = 1
    s = step
    for _ in range(12):
        if abs(s - round(s)) < 1e-12:
            break
        s *= 10
        scale *= 10
    step_int = round(step * scale)
    if step_int == 0:
        return math.floor(value / step) * step
    value_int = int(value * scale)
    return (value_int // step_int) * step_int / scale


def _round_to_step(value: float, step: float, *, round_up: bool) -> float:
    """Round ``value`` to the nearest multiple of ``step``.

    ``round_up=True`` ceils (for take-profit on shorts, stop-loss
    on shorts); ``round_up=False`` floors (the other direction).
    """
    floored = _round_down_to_step(value, step)
    if not round_up:
        return floored
    if abs(value - floored) < 1e-12:
        return floored
    return floored + step


def round_qty(symbol: str, qty: float) -> float:
    """Floor ``qty`` to the symbol's stepSize.

    Floor (not nearest) so the engine never sends an order whose
    notional exceeds the user's intent — Binance rejects with
    -2019 (insufficient margin) when over.

    On cache miss returns ``qty`` unchanged with a warning log.  The
    downstream Binance rejection (still -1111) then carries the
    diagnostic via the FSM rejection log.  Better than silently
    returning 0 which would hide the cache miss as a "skipped" order.
    """
    f = _FILTERS.get(symbol.upper())
    if f is None:
        log.warning(
            "symbol_filters: no cache entry for symbol={} — returning qty "
            "unchanged; order may be rejected with -1111", symbol,
        )
        return qty
    return _round_down_to_step(qty, f.step_size)


def round_price(symbol: str, price: float, *, round_up: bool = False) -> float:
    """Round ``price`` to the symbol's tickSize.

    ``round_up`` direction-aware: for a LONG signal, SL is below
    entry (floor towards safer) and TP is above (ceil towards safer);
    for SHORT, inverse.  Callers in ``order_placer`` pass the right
    direction based on which leg they're placing.
    """
    f = _FILTERS.get(symbol.upper())
    if f is None:
        log.warning(
            "symbol_filters: no cache entry for symbol={} — returning price "
            "unchanged", symbol,
        )
        return price
    return _round_to_step(price, f.tick_size, round_up=round_up)


def meets_min_notional(symbol: str, qty: float, price: float) -> bool:
    """True iff ``qty * price`` clears the symbol's MIN_NOTIONAL.

    On cache miss returns True (let Binance reject as the fallback
    diagnostic).  ``qty <= 0`` returns False — degenerate orders
    skipped upstream.
    """
    if qty <= 0 or price <= 0:
        return False
    f = _FILTERS.get(symbol.upper())
    if f is None:
        return True
    return (qty * price) >= f.min_notional


def get_filters(symbol: str) -> Optional[SymbolFilters]:
    """Read-only accessor for tests + diagnostics."""
    return _FILTERS.get(symbol.upper())


def all_cached_symbols() -> list[str]:
    """Return every symbol currently in the filter cache.  Used by
    diagnostics + the runtime-status endpoint to surface "engine
    knows N symbol filters" alongside the allowlist."""
    return sorted(_FILTERS.keys())


def is_tradfi_perp(symbol: str) -> bool:
    """True iff ``symbol`` is a Binance tokenised-stock / TradFi
    perpetual (contractType ``TRADIFI_PERPETUAL``).

    ``pair_manager`` calls this to keep the whole class out of the
    scanning / dispatch universe.  Returns ``False`` on an unpopulated
    cache — the caller's static ``_NON_CRYPTO_BLACKLIST`` remains the
    floor, so a boot-time race can never *admit* a known stock perp."""
    return symbol.upper() in _TRADFI_PERPS


def tradfi_perp_symbols() -> list[str]:
    """Sorted snapshot of the known TradFi-Perps deny-set (diagnostics
    + the runtime-status endpoint)."""
    return sorted(_TRADFI_PERPS)


# ---------------------------------------------------------------------------
# Refresh + bootstrap
# ---------------------------------------------------------------------------


def _parse_filters(symbol_entry: Dict[str, Any]) -> Optional[SymbolFilters]:
    """Convert one Binance exchangeInfo ``symbols[i]`` entry to a
    SymbolFilters.  Returns None when required filters are missing
    (handles Binance's occasional schema drift gracefully)."""
    symbol = symbol_entry.get("symbol", "").upper()
    if not symbol:
        return None
    step_size: Optional[float] = None
    tick_size: Optional[float] = None
    min_qty: float = 0.0
    min_notional: float = 0.0
    for f in symbol_entry.get("filters", []) or []:
        ft = f.get("filterType")
        if ft == "LOT_SIZE":
            try:
                step_size = float(f.get("stepSize", "0"))
                min_qty = float(f.get("minQty", "0"))
            except (TypeError, ValueError):
                pass
        elif ft == "PRICE_FILTER":
            try:
                tick_size = float(f.get("tickSize", "0"))
            except (TypeError, ValueError):
                pass
        elif ft in ("MIN_NOTIONAL", "NOTIONAL"):
            # Futures uses "MIN_NOTIONAL" historically, "NOTIONAL"
            # on some endpoints.  Pull whichever key carries the
            # value.  Some entries have ``notional`` (minimum) and
            # ``maxNotional`` (cap) — we only care about the min.
            try:
                min_notional = float(
                    f.get("notional")
                    or f.get("minNotional")
                    or "0"
                )
            except (TypeError, ValueError):
                pass
    if step_size is None or tick_size is None:
        return None
    return SymbolFilters(
        symbol=symbol,
        step_size=step_size,
        tick_size=tick_size,
        min_qty=min_qty,
        min_notional=min_notional,
    )


async def refresh_filters(
    binance_client: Any | None = None,
) -> int:
    """Fetch ``/fapi/v1/exchangeInfo`` from Binance and populate the
    cache.  Returns the number of symbols whose filters were parsed
    successfully.

    Calls Binance's PUBLIC unsigned endpoint — no signing service /
    KMS interaction.  Safe to call from any context.

    ``binance_client`` is injectable for tests; production uses a
    lazy-imported :class:`src.binance.BinanceClient` (futures market).
    """
    if binance_client is None:
        from src.binance import BinanceClient
        binance_client = BinanceClient("futures")

    try:
        info = await binance_client.fetch_exchange_info()
    except Exception:
        log.exception("symbol_filters: fetch_exchange_info failed")
        return 0
    if not info or not isinstance(info, dict):
        log.warning("symbol_filters: exchange_info returned empty/wrong shape")
        return 0

    new_cache: Dict[str, SymbolFilters] = {}
    tradfi: set[str] = set()
    for entry in info.get("symbols", []) or []:
        sym = (entry.get("symbol") or "").upper()
        # Classify TradFi-Perps independently of filter parsing — these
        # symbols DO carry valid LOT_SIZE/PRICE_FILTER (they're tradeable),
        # so they'd otherwise land in the filter cache and the universe.
        if sym and entry.get("contractType") == _TRADFI_CONTRACT_TYPE:
            tradfi.add(sym)
        parsed = _parse_filters(entry)
        if parsed is None:
            continue
        new_cache[parsed.symbol] = parsed

    async with _filters_lock:
        global _FILTERS, _TRADFI_PERPS
        _FILTERS = new_cache
        _TRADFI_PERPS = frozenset(tradfi)

    log.info(
        "symbol_filters: refreshed cache with {} symbols "
        "({} TradFi-Perps flagged for universe exclusion)",
        len(new_cache), len(tradfi),
    )
    return len(new_cache)


async def run_periodic_refresh() -> None:
    """Background task — refresh the filter cache every
    ``_REFRESH_INTERVAL_S`` seconds.  Bootstrap schedules this once
    at boot; cancelled at engine shutdown.

    Continues on individual refresh failures (network blips, Binance
    5xx) — never raises, never exits the loop.
    """
    while True:
        try:
            await refresh_filters()
        except Exception:
            log.exception("symbol_filters: periodic refresh raised")
        await asyncio.sleep(_REFRESH_INTERVAL_S)


def reset_for_test() -> None:
    """Test-only: drop the cache.  Used by per-test fixtures."""
    global _FILTERS, _TRADFI_PERPS
    _FILTERS = {}
    _TRADFI_PERPS = frozenset()


def _set_cache_for_test(filters: Dict[str, SymbolFilters]) -> None:
    """Test-only: pre-populate the cache without an HTTP call."""
    global _FILTERS
    _FILTERS = dict(filters)


def _set_tradfi_perps_for_test(symbols: set[str]) -> None:
    """Test-only: pre-populate the TradFi-Perps deny-set."""
    global _TRADFI_PERPS
    _TRADFI_PERPS = frozenset(s.upper() for s in symbols)
