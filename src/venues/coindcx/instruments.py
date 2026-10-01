"""CoinDCX futures instruments, live prices and the INR conversion price.

Public, unsigned endpoints only — nothing here touches a key.

Three sources, each read at the cadence its fact changes:

* ``data/active_instruments`` — the list of live pairs, per margin currency.
  Refreshed every :data:`LIST_TTL_S`.
* ``data/instrument`` — one pair's filters (tick, step, min notional, max
  leverage, ``exit_only``).  Fetched when a pair is first needed and cached for
  :data:`DETAIL_TTL_S`; a pair nobody trades is never fetched.
* ``current_prices/futures/rt`` — every pair's last price, mark price and the
  **Binance symbol it tracks** (``mkt``).  That field is the symbol map: it is
  CoinDCX saying which contract theirs is, so we never derive the mapping from
  a string pattern where the feed can tell us.  Cached :data:`PRICE_TTL_S`.

**Refuse, never guess.**  A symbol with no ``mkt`` match, an instrument with a
contract value other than 1, a quanto or inverse contract, an inactive or
exit-only pair, or a fetch that failed all return ``None`` from the lookup and
the caller refuses the trade with a named reason.  A wrong mapping here is a
size error of the contract multiplier (10×–1000×) on a real account.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal
from typing import Any, Dict, Iterable, Optional

import aiohttp

from src.utils import get_logger

log = get_logger("venues.coindcx.instruments")

API_BASE = "https://api.coindcx.com"
PUBLIC_BASE = "https://public.coindcx.com"

ACTIVE_INSTRUMENTS_PATH = "/exchange/v1/derivatives/futures/data/active_instruments"
INSTRUMENT_PATH = "/exchange/v1/derivatives/futures/data/instrument"
PRICES_PATH = "/market_data/v3/current_prices/futures/rt"
CONVERSIONS_PATH = "/api/v1/derivatives/futures/data/conversions"

MARGIN_USDT = "USDT"
MARGIN_INR = "INR"
MARGIN_CURRENCIES = (MARGIN_USDT, MARGIN_INR)

LIST_TTL_S = 6 * 3600.0
DETAIL_TTL_S = 6 * 3600.0
PRICE_TTL_S = 3.0
#: The oldest snapshot an ORDER may be planned against.  A failed refresh
#: keeps the previous snapshot (right for the symbol map, which rarely
#: changes); it is wrong for a price, which during a CoinDCX outage could be
#: hours old and would then decide the gap and levels-crossed checks.
PRICE_MAX_AGE_FOR_ORDER_S = 15.0
CONVERSION_TTL_S = 60.0
_HTTP_TIMEOUT_S = 8.0


@dataclass(frozen=True)
class Instrument:
    """The filters an order on one CoinDCX pair must satisfy."""

    pair: str                      # "B-BTC_USDT"
    symbol: str                    # "BTCUSDT" — the Binance twin
    status: str
    price_increment: float
    quantity_increment: float
    min_quantity: float
    max_quantity: float
    max_market_order_quantity: float
    min_notional: float            # USDT
    max_leverage_long: float
    max_leverage_short: float
    exit_only: bool
    order_types: tuple
    unit_contract_value: float = 1.0
    is_inverse: bool = False
    is_quanto: bool = False
    maker_fee_pct: float = 0.0
    taker_fee_pct: float = 0.0

    @property
    def tradable(self) -> bool:
        """Every property our order shape depends on, checked in one place."""
        return (
            self.status == "active"
            and not self.exit_only
            and not self.is_inverse
            and not self.is_quanto
            and abs(self.unit_contract_value - 1.0) < 1e-12
            and self.quantity_increment > 0
            and self.price_increment > 0
            and "market_order" in self.order_types
            and "stop_market" in self.order_types
            and "take_profit_market" in self.order_types
        )

    def refusal(self) -> Optional[str]:
        """Why this instrument cannot carry our order shape, or ``None``."""
        if self.status != "active":
            return f"instrument_{self.status or 'inactive'}"
        if self.exit_only:
            return "instrument_exit_only"
        if self.is_inverse or self.is_quanto:
            return "instrument_not_linear"
        if abs(self.unit_contract_value - 1.0) >= 1e-12:
            return "contract_multiplier"
        for needed in ("market_order", "stop_market", "take_profit_market"):
            if needed not in self.order_types:
                return f"order_type_unsupported:{needed}"
        if self.quantity_increment <= 0 or self.price_increment <= 0:
            return "filters_missing"
        return None

    def max_leverage(self, direction: str) -> float:
        return self.max_leverage_long if direction == "LONG" else self.max_leverage_short


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_instrument(raw: Dict[str, Any], symbol: str) -> Optional[Instrument]:
    """Build an :class:`Instrument` from the ``instrument`` payload, or refuse."""
    if not isinstance(raw, dict) or not raw.get("pair"):
        return None
    types = raw.get("order_types") or []
    return Instrument(
        pair=str(raw["pair"]),
        symbol=symbol,
        status=str(raw.get("status") or ""),
        price_increment=_num(raw.get("price_increment")),
        quantity_increment=_num(raw.get("quantity_increment")),
        min_quantity=_num(raw.get("min_quantity")),
        max_quantity=_num(raw.get("max_quantity")),
        max_market_order_quantity=_num(raw.get("max_market_order_quantity")),
        min_notional=_num(raw.get("min_notional")),
        max_leverage_long=_num(raw.get("max_leverage_long"), 1.0) or 1.0,
        max_leverage_short=_num(raw.get("max_leverage_short"), 1.0) or 1.0,
        exit_only=bool(raw.get("exit_only")),
        order_types=tuple(str(t) for t in types if isinstance(t, str)),
        unit_contract_value=_num(raw.get("unit_contract_value"), 1.0),
        is_inverse=bool(raw.get("is_inverse")),
        is_quanto=bool(raw.get("is_quanto")),
        maker_fee_pct=_num(raw.get("maker_fee")),
        taker_fee_pct=_num(raw.get("taker_fee")),
    )


def _decimal(x: float) -> Decimal:
    return Decimal(repr(float(x)))


def round_qty_down(qty: float, step: float) -> float:
    """Floor ``qty`` to a multiple of ``step`` — never round a size UP."""
    if step <= 0 or qty <= 0:
        return 0.0
    q = (_decimal(qty) / _decimal(step)).to_integral_value(rounding=ROUND_DOWN)
    return float(q * _decimal(step))


def round_price(price: float, tick: float) -> float:
    """Nearest multiple of ``tick`` (the tick is far below any stop distance)."""
    if tick <= 0 or price <= 0:
        return 0.0
    q = (_decimal(price) / _decimal(tick)).to_integral_value(rounding=ROUND_HALF_UP)
    return float(q * _decimal(tick))


def format_number(value: float, step: float) -> str:
    """Render ``value`` with exactly the decimals ``step`` carries.

    CoinDCX checks divisibility on the value it parses; sending the float's
    repr (``0.30000000000000004``) is how a correctly rounded size is refused.
    """
    exp = _decimal(step).normalize().as_tuple().exponent
    places = -exp if isinstance(exp, int) and exp < 0 else 0
    return f"{value:.{places}f}"


@dataclass
class _PriceSnapshot:
    #: ``None`` = never fetched.  Not ``0.0``: ``time.monotonic()`` counts from
    #: boot, so on a host up for less than a TTL a zero reads as *fresh* and
    #: the first fetch never happens (found by the live check, 2026-09-27).
    fetched_at: Optional[float] = None
    by_symbol: Dict[str, dict] = field(default_factory=dict)  # BTCUSDT → row (+ "pair")


class InstrumentRegistry:
    """Process-wide cache of CoinDCX futures instruments and prices.

    ``session`` is injectable for tests; production creates one lazily.
    Every fetch failure leaves the previous cache in place and is counted in
    :attr:`stats`, so a CoinDCX outage degrades to refusals with a cause
    rather than to a registry that silently empties.
    """

    def __init__(self, *, session: Optional[aiohttp.ClientSession] = None) -> None:
        self._session = session
        self._own_session = session is None
        self._lock = asyncio.Lock()
        self._pairs: Dict[str, set] = {}
        self._pairs_at: Optional[float] = None
        self._details: Dict[str, tuple] = {}  # pair → (Instrument|None, fetched_at)
        self._prices = _PriceSnapshot()
        self._conversion: Optional[tuple] = None  # (price, fetched_at)
        self.stats: Dict[str, int] = {
            "list_fetches": 0, "list_failures": 0,
            "detail_fetches": 0, "detail_failures": 0,
            "price_fetches": 0, "price_failures": 0, "price_stale_refusals": 0,
            "conversion_fetches": 0, "conversion_failures": 0,
        }

    # -- HTTP -------------------------------------------------------------

    async def _get_json(self, url: str, params: Optional[dict] = None) -> Any:
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=_HTTP_TIMEOUT_S)
            )
        async with self._session.get(url, params=params) as resp:
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status} from {url}")
            return await resp.json(content_type=None)

    async def close(self) -> None:
        if self._own_session and self._session is not None:
            await self._session.close()
            self._session = None

    # -- Active list ------------------------------------------------------

    async def active_pairs(self, margin_currency: str = MARGIN_USDT) -> Optional[set]:
        """Live pair names for one margin currency; ``None`` if never loaded."""
        if self._pairs_at is None or (time.monotonic() - self._pairs_at) > LIST_TTL_S:
            await self._refresh_pairs()
        pairs = self._pairs.get(margin_currency)
        return set(pairs) if pairs is not None else None

    async def _refresh_pairs(self) -> None:
        fresh: Dict[str, set] = {}
        for ccy in MARGIN_CURRENCIES:
            self.stats["list_fetches"] += 1
            try:
                data = await self._get_json(
                    API_BASE + ACTIVE_INSTRUMENTS_PATH,
                    params={"margin_currency_short_name[]": ccy},
                )
            except Exception as exc:
                self.stats["list_failures"] += 1
                log.warning("coindcx: active_instruments({}) failed: {}", ccy, exc)
                continue
            if isinstance(data, list):
                fresh[ccy] = {str(p) for p in data if isinstance(p, str)}
        if fresh:
            self._pairs.update(fresh)
            self._pairs_at = time.monotonic()

    # -- Prices + symbol map ---------------------------------------------

    async def prices(self, *, max_age_s: float = PRICE_TTL_S) -> Dict[str, dict]:
        """``{BINANCE_SYMBOL: {"pair", "ls", "mp", "fr", ...}}`` — may be stale
        by up to ``max_age_s``; empty when never loaded."""
        if self._prices_stale(max_age_s):
            async with self._lock:
                if self._prices_stale(max_age_s):
                    await self._refresh_prices()
        return self._prices.by_symbol

    def _prices_stale(self, max_age_s: float) -> bool:
        at = self._prices.fetched_at
        return at is None or (time.monotonic() - at) > max_age_s

    async def _refresh_prices(self) -> None:
        self.stats["price_fetches"] += 1
        try:
            data = await self._get_json(PUBLIC_BASE + PRICES_PATH)
        except Exception as exc:
            self.stats["price_failures"] += 1
            log.warning("coindcx: price snapshot failed: {}", exc)
            return
        rows = (data or {}).get("prices") if isinstance(data, dict) else None
        if not isinstance(rows, dict):
            self.stats["price_failures"] += 1
            return
        self._prices = _PriceSnapshot(
            fetched_at=time.monotonic(),
            by_symbol=build_symbol_map(rows),
        )

    async def pair_for(self, symbol: str) -> Optional[str]:
        """The CoinDCX pair tracking Binance ``symbol``, or ``None``."""
        row = (await self.prices(max_age_s=LIST_TTL_S)).get(symbol.upper())
        return row.get("pair") if row else None

    async def last_price(self, symbol: str) -> Optional[float]:
        """Last price, or ``None`` when no snapshot younger than
        :data:`PRICE_MAX_AGE_FOR_ORDER_S` exists — the caller refuses with
        ``price_unavailable`` rather than trading on a stale number."""
        snapshot = await self.prices()
        if self._prices_stale(PRICE_MAX_AGE_FOR_ORDER_S):
            self.stats["price_stale_refusals"] += 1
            return None
        row = snapshot.get(symbol.upper())
        px = _num(row.get("ls")) if row else 0.0
        return px if px > 0 else None

    # -- Instrument detail ------------------------------------------------

    async def instrument(self, symbol: str) -> Optional[Instrument]:
        """The instrument for Binance ``symbol`` — ``None`` means refuse."""
        pair = await self.pair_for(symbol)
        if not pair:
            return None
        cached = self._details.get(pair)
        if cached is not None and (time.monotonic() - cached[1]) < DETAIL_TTL_S:
            return cached[0]
        self.stats["detail_fetches"] += 1
        try:
            data = await self._get_json(
                API_BASE + INSTRUMENT_PATH,
                params={"pair": pair, "margin_currency_short_name": MARGIN_USDT},
            )
        except Exception as exc:
            self.stats["detail_failures"] += 1
            log.warning("coindcx: instrument({}) failed: {}", pair, exc)
            # A stale entry is better than none for filters that rarely change.
            return cached[0] if cached is not None else None
        raw = (data or {}).get("instrument") if isinstance(data, dict) else None
        inst = parse_instrument(raw, symbol.upper()) if isinstance(raw, dict) else None
        self._details[pair] = (inst, time.monotonic())
        return inst

    # -- INR conversion ---------------------------------------------------

    async def inr_per_usdt(self) -> Optional[float]:
        """CoinDCX's USDT→INR conversion price for INR-margined futures."""
        now = time.monotonic()
        if self._conversion is not None and (now - self._conversion[1]) < CONVERSION_TTL_S:
            return self._conversion[0]
        self.stats["conversion_fetches"] += 1
        try:
            data = await self._get_json(API_BASE + CONVERSIONS_PATH)
        except Exception as exc:
            self.stats["conversion_failures"] += 1
            log.warning("coindcx: conversions failed: {}", exc)
            return self._conversion[0] if self._conversion else None
        price = parse_inr_conversion(data)
        if price is None:
            self.stats["conversion_failures"] += 1
            return self._conversion[0] if self._conversion else None
        self._conversion = (price, time.monotonic())
        return price

    def snapshot(self) -> dict:
        """Health view for ops — counts, never raw payloads."""
        return {
            "pairs": {k: len(v) for k, v in self._pairs.items()},
            "pairs_age_s": (
                round(time.monotonic() - self._pairs_at, 1)
                if self._pairs_at is not None else None
            ),
            "symbols_mapped": len(self._prices.by_symbol),
            "prices_age_s": (
                round(time.monotonic() - self._prices.fetched_at, 1)
                if self._prices.fetched_at is not None else None
            ),
            "details_cached": len(self._details),
            "inr_per_usdt": self._conversion[0] if self._conversion else None,
            "stats": dict(self.stats),
        }


def build_symbol_map(rows: Dict[str, Any]) -> Dict[str, dict]:
    """``{pair: row}`` from the price feed → ``{binance_symbol: row+pair}``.

    Only rows that name their twin (``mkt``) are mapped, and only USDT-quoted
    ``B-`` pairs: a symbol two pairs both claim is dropped from the map rather
    than resolved by whichever came last.
    """
    out: Dict[str, dict] = {}
    claimed: Dict[str, int] = {}
    for pair, row in rows.items():
        if not isinstance(row, dict) or not isinstance(pair, str):
            continue
        if not (pair.startswith("B-") and pair.endswith("_USDT")):
            continue
        mkt = row.get("mkt")
        if not isinstance(mkt, str) or not mkt:
            continue
        sym = mkt.upper()
        claimed[sym] = claimed.get(sym, 0) + 1
        out[sym] = dict(row, pair=pair)
    for sym, n in claimed.items():
        if n > 1:
            out.pop(sym, None)
    return out


def parse_inr_conversion(data: Any) -> Optional[float]:
    """The USDT→INR price from the conversions payload, or ``None``."""
    if not isinstance(data, list):
        return None
    for row in data:
        if (
            isinstance(row, dict)
            and str(row.get("margin_currency_short_name") or "").upper() == MARGIN_INR
            and str(row.get("target_currency_short_name") or "").upper() == MARGIN_USDT
        ):
            px = _num(row.get("conversion_price"))
            if px > 0:
                return px
    return None


_REGISTRY: Optional[InstrumentRegistry] = None


def get_registry() -> InstrumentRegistry:
    """The process-wide registry (created on first use)."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = InstrumentRegistry()
    return _REGISTRY


def set_registry_for_test(registry: Optional[InstrumentRegistry]) -> None:
    global _REGISTRY
    _REGISTRY = registry


def symbols_covered(symbols: Iterable[str], mapped: Dict[str, dict]) -> Dict[str, Optional[str]]:
    """``{symbol: pair or None}`` — used by ops to show coverage of a scan set."""
    return {s: (mapped.get(s.upper()) or {}).get("pair") for s in symbols}
