"""Tests for src.execution.symbol_filters.

Pins:

* LOT_SIZE.stepSize floor for various Binance-realistic stepSizes
  (0.001 / 0.01 / 1 / 100 — covers BTCUSDT through DOGEUSDT through
  hypothetical micro-cap pairs).
* PRICE_FILTER.tickSize round (direction-aware).
* MIN_NOTIONAL guard.
* Cache miss fallback (return-unchanged + warning, don't return 0).
* Refresh parses real Binance exchangeInfo shape.
"""
from __future__ import annotations

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.execution import symbol_filters


@pytest.fixture(autouse=True)
def _reset_cache():
    symbol_filters.reset_for_test()
    yield
    symbol_filters.reset_for_test()


# ---------------------------------------------------------------------------
# round_qty
# ---------------------------------------------------------------------------


def test_round_qty_floors_to_step_size_001() -> None:
    """BTCUSDT-style: stepSize 0.001 → qty floored to 3 decimals."""
    symbol_filters._set_cache_for_test({
        "BTCUSDT": symbol_filters.SymbolFilters(
            symbol="BTCUSDT", step_size=0.001, tick_size=0.10,
            min_qty=0.001, min_notional=5.0,
        ),
    })
    assert symbol_filters.round_qty("BTCUSDT", 0.017241379) == pytest.approx(0.017)


def test_round_qty_floors_to_integer_step() -> None:
    """DOGEUSDT-style: stepSize 1 → qty floored to integer."""
    symbol_filters._set_cache_for_test({
        "DOGEUSDT": symbol_filters.SymbolFilters(
            symbol="DOGEUSDT", step_size=1.0, tick_size=0.00001,
            min_qty=1.0, min_notional=5.0,
        ),
    })
    assert symbol_filters.round_qty("DOGEUSDT", 1234.5678) == 1234.0
    assert symbol_filters.round_qty("DOGEUSDT", 0.999) == 0.0


def test_round_qty_floors_to_coarse_step() -> None:
    """Hypothetical micro-cap with stepSize 100: 1234 → 1200."""
    symbol_filters._set_cache_for_test({
        "FOOUSDT": symbol_filters.SymbolFilters(
            symbol="FOOUSDT", step_size=100.0, tick_size=0.0001,
            min_qty=100.0, min_notional=5.0,
        ),
    })
    assert symbol_filters.round_qty("FOOUSDT", 1234.5) == 1200.0
    assert symbol_filters.round_qty("FOOUSDT", 99.9) == 0.0


def test_round_qty_handles_float_drift_at_step_boundary() -> None:
    """The classic 0.1 + 0.2 != 0.3 case — stepSize=0.1, value=0.3
    must come back as 0.3 not 0.2.  Tests the integer-math path
    inside _round_down_to_step."""
    symbol_filters._set_cache_for_test({
        "XYZUSDT": symbol_filters.SymbolFilters(
            symbol="XYZUSDT", step_size=0.1, tick_size=0.01,
            min_qty=0.1, min_notional=5.0,
        ),
    })
    assert symbol_filters.round_qty("XYZUSDT", 0.30) == pytest.approx(0.30)
    assert symbol_filters.round_qty("XYZUSDT", 0.35) == pytest.approx(0.30)


def test_round_qty_cache_miss_returns_unchanged() -> None:
    """Cache miss surfaces a warning + lets the downstream Binance
    error be the fallback diagnostic.  Better than silently floor
    to 0 which would hide the missing-filter telemetry."""
    assert symbol_filters.round_qty("UNKNOWNUSDT", 0.123456) == 0.123456


def test_round_qty_is_case_insensitive() -> None:
    symbol_filters._set_cache_for_test({
        "BTCUSDT": symbol_filters.SymbolFilters(
            symbol="BTCUSDT", step_size=0.001, tick_size=0.10,
            min_qty=0.001, min_notional=5.0,
        ),
    })
    assert symbol_filters.round_qty("btcusdt", 0.017241) == pytest.approx(0.017)


# ---------------------------------------------------------------------------
# round_price
# ---------------------------------------------------------------------------


def test_round_price_floors_by_default() -> None:
    symbol_filters._set_cache_for_test({
        "BTCUSDT": symbol_filters.SymbolFilters(
            symbol="BTCUSDT", step_size=0.001, tick_size=0.10,
            min_qty=0.001, min_notional=5.0,
        ),
    })
    assert symbol_filters.round_price("BTCUSDT", 29000.17) == pytest.approx(29000.10)


def test_round_price_ceils_when_round_up() -> None:
    symbol_filters._set_cache_for_test({
        "BTCUSDT": symbol_filters.SymbolFilters(
            symbol="BTCUSDT", step_size=0.001, tick_size=0.10,
            min_qty=0.001, min_notional=5.0,
        ),
    })
    assert symbol_filters.round_price(
        "BTCUSDT", 29000.17, round_up=True,
    ) == pytest.approx(29000.20)


def test_round_price_no_change_when_already_on_tick() -> None:
    symbol_filters._set_cache_for_test({
        "BTCUSDT": symbol_filters.SymbolFilters(
            symbol="BTCUSDT", step_size=0.001, tick_size=0.10,
            min_qty=0.001, min_notional=5.0,
        ),
    })
    # Already on tick — both directions return the same.
    assert symbol_filters.round_price("BTCUSDT", 29000.10) == pytest.approx(29000.10)
    assert symbol_filters.round_price(
        "BTCUSDT", 29000.10, round_up=True,
    ) == pytest.approx(29000.10)


# ---------------------------------------------------------------------------
# meets_min_notional
# ---------------------------------------------------------------------------


def test_meets_min_notional_passes_above_threshold() -> None:
    symbol_filters._set_cache_for_test({
        "BTCUSDT": symbol_filters.SymbolFilters(
            symbol="BTCUSDT", step_size=0.001, tick_size=0.10,
            min_qty=0.001, min_notional=5.0,
        ),
    })
    # 0.001 BTC × $29000 = $29 ≥ $5 minimum.
    assert symbol_filters.meets_min_notional("BTCUSDT", 0.001, 29000.0) is True


def test_meets_min_notional_blocks_below_threshold() -> None:
    symbol_filters._set_cache_for_test({
        "FOOUSDT": symbol_filters.SymbolFilters(
            symbol="FOOUSDT", step_size=1.0, tick_size=0.01,
            min_qty=1.0, min_notional=10.0,
        ),
    })
    # 1 unit × $5 = $5 < $10 → blocked.
    assert symbol_filters.meets_min_notional("FOOUSDT", 1.0, 5.0) is False


def test_meets_min_notional_blocks_zero_qty() -> None:
    """qty<=0 always returns False — degenerate order; callers skip."""
    symbol_filters._set_cache_for_test({
        "BTCUSDT": symbol_filters.SymbolFilters(
            symbol="BTCUSDT", step_size=0.001, tick_size=0.10,
            min_qty=0.001, min_notional=5.0,
        ),
    })
    assert symbol_filters.meets_min_notional("BTCUSDT", 0.0, 29000.0) is False
    assert symbol_filters.meets_min_notional("BTCUSDT", -0.001, 29000.0) is False


def test_meets_min_notional_cache_miss_returns_true() -> None:
    """Defensive: cache miss → let Binance reject as the fallback
    diagnostic, don't pre-emptively block on missing filter data."""
    assert symbol_filters.meets_min_notional("UNKNOWNUSDT", 1.0, 5.0) is True


# ---------------------------------------------------------------------------
# refresh_filters — parses Binance exchangeInfo shape
# ---------------------------------------------------------------------------


_FAKE_EXCHANGE_INFO: Dict[str, Any] = {
    "timezone": "UTC",
    "serverTime": 1700000000000,
    "symbols": [
        {
            "symbol": "BTCUSDT",
            "filters": [
                {
                    "filterType": "PRICE_FILTER",
                    "tickSize": "0.10",
                },
                {
                    "filterType": "LOT_SIZE",
                    "stepSize": "0.001",
                    "minQty": "0.001",
                },
                {
                    "filterType": "MIN_NOTIONAL",
                    "notional": "5",
                },
            ],
        },
        {
            "symbol": "DOGEUSDT",
            "filters": [
                {
                    "filterType": "PRICE_FILTER",
                    "tickSize": "0.00001",
                },
                {
                    "filterType": "LOT_SIZE",
                    "stepSize": "1",
                    "minQty": "1",
                },
                {
                    "filterType": "MIN_NOTIONAL",
                    "notional": "5",
                },
            ],
        },
        {
            # Defensive — missing LOT_SIZE → entry skipped, no crash.
            "symbol": "BROKENUSDT",
            "filters": [
                {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
            ],
        },
    ],
}


async def test_refresh_filters_parses_binance_shape() -> None:
    fake_client = MagicMock()
    fake_client.fetch_exchange_info = AsyncMock(
        return_value=_FAKE_EXCHANGE_INFO,
    )
    count = await symbol_filters.refresh_filters(binance_client=fake_client)
    # BTCUSDT + DOGEUSDT parsed; BROKENUSDT skipped (no LOT_SIZE).
    assert count == 2
    btc = symbol_filters.get_filters("BTCUSDT")
    assert btc is not None
    assert btc.step_size == 0.001
    assert btc.tick_size == 0.10
    assert btc.min_notional == 5.0
    doge = symbol_filters.get_filters("DOGEUSDT")
    assert doge is not None
    assert doge.step_size == 1.0
    assert symbol_filters.get_filters("BROKENUSDT") is None


async def test_refresh_filters_accepts_notional_filter_variant() -> None:
    """Binance docs note both ``MIN_NOTIONAL`` and ``NOTIONAL``
    filter types in different endpoint versions.  Both must parse."""
    fake_client = MagicMock()
    fake_client.fetch_exchange_info = AsyncMock(return_value={
        "symbols": [{
            "symbol": "FOOUSDT",
            "filters": [
                {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
                {"filterType": "LOT_SIZE", "stepSize": "1", "minQty": "1"},
                {"filterType": "NOTIONAL", "minNotional": "10"},
            ],
        }],
    })
    await symbol_filters.refresh_filters(binance_client=fake_client)
    foo = symbol_filters.get_filters("FOOUSDT")
    assert foo is not None
    assert foo.min_notional == 10.0


async def test_refresh_filters_handles_empty_response() -> None:
    """Binance 5xx or empty body → refresh returns 0 without
    raising; cache is wiped (refresh atomically replaces the cache,
    so an empty response means "no symbols known")."""
    fake_client = MagicMock()
    fake_client.fetch_exchange_info = AsyncMock(return_value=None)
    count = await symbol_filters.refresh_filters(binance_client=fake_client)
    assert count == 0


async def test_refresh_filters_atomic_swap_no_partial_cache() -> None:
    """A successful refresh should atomically replace the cache —
    never leave a half-built dict visible.  The lock guards this."""
    # Seed cache to a known state.
    symbol_filters._set_cache_for_test({
        "OLDUSDT": symbol_filters.SymbolFilters(
            symbol="OLDUSDT", step_size=1.0, tick_size=0.01,
            min_qty=1.0, min_notional=5.0,
        ),
    })
    fake_client = MagicMock()
    fake_client.fetch_exchange_info = AsyncMock(return_value=_FAKE_EXCHANGE_INFO)
    await symbol_filters.refresh_filters(binance_client=fake_client)
    # OLDUSDT no longer in cache; the new dict replaced the old.
    assert symbol_filters.get_filters("OLDUSDT") is None
    assert symbol_filters.get_filters("BTCUSDT") is not None


# ---------------------------------------------------------------------------
# TradFi-Perps classification (2026-07-18)
#
# Binance tokenised-stock / equity perps carry contractType
# "TRADIFI_PERPETUAL" (Binance's spelling).  They must be flagged for
# universe exclusion — an order on one is rejected with -4411 "sign
# TradFi-Perps agreement" for any account that hasn't signed the
# separate agreement, and the crypto scalp stack mis-scores them.
# ---------------------------------------------------------------------------


# WDCUSDT (Western Digital stock perp) carries valid filters — it is a
# fully tradeable contract, which is exactly why the *filter cache*
# alone can't exclude it; only contractType distinguishes it.
_FAKE_EXCHANGE_INFO_WITH_TRADFI: Dict[str, Any] = {
    "symbols": [
        {
            "symbol": "BTCUSDT",
            "contractType": "PERPETUAL",
            "filters": [
                {"filterType": "PRICE_FILTER", "tickSize": "0.10"},
                {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.001"},
                {"filterType": "MIN_NOTIONAL", "notional": "5"},
            ],
        },
        {
            "symbol": "WDCUSDT",
            "contractType": "TRADIFI_PERPETUAL",  # Western Digital stock perp
            "filters": [
                {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
                {"filterType": "LOT_SIZE", "stepSize": "0.1", "minQty": "0.1"},
                {"filterType": "MIN_NOTIONAL", "notional": "5"},
            ],
        },
    ],
}


async def test_refresh_flags_tradfi_perps() -> None:
    """A TRADIFI_PERPETUAL contract is added to the deny-set while a
    normal PERPETUAL is not."""
    fake_client = MagicMock()
    fake_client.fetch_exchange_info = AsyncMock(
        return_value=_FAKE_EXCHANGE_INFO_WITH_TRADFI,
    )
    await symbol_filters.refresh_filters(binance_client=fake_client)

    assert symbol_filters.is_tradfi_perp("WDCUSDT") is True
    assert symbol_filters.is_tradfi_perp("BTCUSDT") is False
    assert symbol_filters.tradfi_perp_symbols() == ["WDCUSDT"]


async def test_tradfi_perp_stays_tradeable_in_filter_cache() -> None:
    """The stock perp still parses into the filter cache (it has valid
    LOT_SIZE/PRICE_FILTER) — proving contractType, not filter absence,
    is what excludes it.  A filter-cache-only exclusion would miss it."""
    fake_client = MagicMock()
    fake_client.fetch_exchange_info = AsyncMock(
        return_value=_FAKE_EXCHANGE_INFO_WITH_TRADFI,
    )
    await symbol_filters.refresh_filters(binance_client=fake_client)
    assert symbol_filters.get_filters("WDCUSDT") is not None


def test_is_tradfi_perp_case_insensitive_and_fail_open() -> None:
    """Lookup is case-insensitive; an unpopulated cache returns False
    (fail-open to pair_manager's static blacklist floor)."""
    symbol_filters.reset_for_test()
    assert symbol_filters.is_tradfi_perp("WDCUSDT") is False  # empty cache
    symbol_filters._set_tradfi_perps_for_test({"WDCUSDT"})
    assert symbol_filters.is_tradfi_perp("wdcusdt") is True


async def test_refresh_replaces_tradfi_set_atomically() -> None:
    """A later refresh whose payload has no TradFi perps clears the
    deny-set — a delisted stock perp drops out without a restart."""
    symbol_filters._set_tradfi_perps_for_test({"STALEUSDT"})
    fake_client = MagicMock()
    fake_client.fetch_exchange_info = AsyncMock(return_value=_FAKE_EXCHANGE_INFO)
    await symbol_filters.refresh_filters(binance_client=fake_client)
    assert symbol_filters.tradfi_perp_symbols() == []
    assert symbol_filters.is_tradfi_perp("STALEUSDT") is False
