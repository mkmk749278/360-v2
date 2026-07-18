"""Tests for the commodity / non-crypto pair blacklist (2026-05-07).

Owner reported XAU/XAG signals firing on Telegram.  These tokenised
metals run on traditional-market dynamics (24/5, London/NY session
liquidity) but the engine assumes 24/7 crypto microstructure — every
chartist-eye component (LevelBook, VolumeProfile, StructureTracker,
regime classifier) systematically mis-scores them.

Filter applied at every ``PairManager.fetch_*`` call so non-crypto
pairs never enter the scanning universe regardless of volume rank.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.execution import symbol_filters
from src.pair_manager import (
    _NON_CRYPTO_BLACKLIST,
    _PAIR_BLACKLIST,
    _STABLECOIN_BLACKLIST,
    PairManager,
)


class TestNonCryptoBlacklist:
    def test_xau_xag_excluded(self):
        """The pairs the owner specifically flagged."""
        assert "XAUUSDT" in _NON_CRYPTO_BLACKLIST
        assert "XAGUSDT" in _NON_CRYPTO_BLACKLIST

    def test_paxg_excluded(self):
        """Tokenised gold (PAXGUSDT) — same characteristics as XAUUSDT."""
        assert "PAXGUSDT" in _NON_CRYPTO_BLACKLIST

    def test_oil_pairs_excluded(self):
        for sym in ("WTIUSDT", "BRENTUSDT", "USOILUSDT"):
            assert sym in _NON_CRYPTO_BLACKLIST

    def test_fx_pairs_excluded(self):
        """EUR/GBP/JPY — traditional-market dynamics, macro-driven."""
        for sym in ("EURUSDT", "GBPUSDT", "JPYUSDT"):
            assert sym in _NON_CRYPTO_BLACKLIST

    def test_equity_index_pairs_excluded(self):
        for sym in ("SPXUSDT", "NDXUSDT", "TSLAUSDT", "AAPLUSDT"):
            assert sym in _NON_CRYPTO_BLACKLIST

    def test_wdc_western_digital_excluded(self):
        """2026-07-18: Western Digital stock perp reached a paid user's
        auto-trade (Binance -4411).  Static floor must catch it even
        before the structural filter's first exchangeInfo refresh."""
        assert "WDCUSDT" in _NON_CRYPTO_BLACKLIST

    def test_btc_eth_not_blacklisted(self):
        """Sanity: real crypto top pairs must NOT be in the blacklist."""
        for sym in ("BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"):
            assert sym not in _NON_CRYPTO_BLACKLIST
            assert sym not in _PAIR_BLACKLIST


class TestCombinedBlacklist:
    def test_combines_both_categories(self):
        """``_PAIR_BLACKLIST`` is the union of stablecoin + non-crypto sets."""
        assert _PAIR_BLACKLIST == _STABLECOIN_BLACKLIST | _NON_CRYPTO_BLACKLIST

    def test_stablecoins_still_excluded(self):
        """No regression: stablecoin filter still active."""
        assert "USDCUSDT" in _PAIR_BLACKLIST
        assert "FDUSDUSDT" in _PAIR_BLACKLIST

    def test_xau_in_combined(self):
        assert "XAUUSDT" in _PAIR_BLACKLIST


class TestFilterAppliedAtFetchSites:
    """Verify ``fetch_*`` paths actually use the combined blacklist."""

    def test_pair_manager_module_uses_pair_blacklist(self):
        import src.pair_manager as _pm
        source = open(_pm.__file__).read()
        # 4 fetch paths × 1 reference each = 4 occurrences of _PAIR_BLACKLIST
        # used as the filter keyword.  Should be ≥4 to cover spot+futures
        # × top+all variants.
        assert source.count("not in _PAIR_BLACKLIST") >= 4

    def test_pair_manager_module_uses_tradfi_filter(self):
        """The structural TradFi-Perps filter must be wired into every
        fetch path, not just one — a fetch site missing it re-opens the
        leak that let WDCUSDT through."""
        import src.pair_manager as _pm
        source = open(_pm.__file__).read()
        assert source.count("not is_tradfi_perp(") >= 4


class TestTradFiPerpStructuralFilter:
    """The durable filter: any TRADIFI_PERPETUAL symbol is dropped at
    fetch time regardless of whether its name is in the static list."""

    @pytest.fixture(autouse=True)
    def _reset_symbol_filters(self):
        symbol_filters.reset_for_test()
        yield
        symbol_filters.reset_for_test()

    def _make_pm(self):
        pm = PairManager.__new__(PairManager)
        pm.pairs = {}
        pm._prev_volumes = {}
        pm._spot_client = MagicMock()
        pm._futures_client = MagicMock()
        return pm

    @pytest.mark.asyncio
    async def test_unlisted_stock_perp_filtered_by_contract_type(self):
        """A stock perp NOT in the static blacklist is still excluded
        when the deny-set (from exchangeInfo) knows it.  This is the
        case the static list can't cover: a brand-new listing."""
        # NEWSTOCKUSDT is deliberately NOT in _NON_CRYPTO_BLACKLIST.
        symbol_filters._set_tradfi_perps_for_test({"NEWSTOCKUSDT"})
        # Non-empty filter cache so _ensure_symbol_metadata skips refresh.
        symbol_filters._set_cache_for_test({
            "BTCUSDT": symbol_filters.SymbolFilters(
                symbol="BTCUSDT", step_size=0.001, tick_size=0.1,
                min_qty=0.001, min_notional=5.0,
            ),
        })
        assert "NEWSTOCKUSDT" not in _NON_CRYPTO_BLACKLIST  # premise

        pm = self._make_pm()
        pm._futures_client._get = AsyncMock(return_value=[
            {"symbol": "BTCUSDT", "quoteVolume": "1000000", "priceChangePercent": "1"},
            {"symbol": "NEWSTOCKUSDT", "quoteVolume": "9999999", "priceChangePercent": "8"},
        ])
        pairs = await pm.fetch_top_futures_pairs(limit=10)
        syms = {p.symbol for p in pairs}
        assert "BTCUSDT" in syms
        assert "NEWSTOCKUSDT" not in syms  # excluded despite top volume

    @pytest.mark.asyncio
    async def test_crypto_perp_not_filtered(self):
        """Sanity: a normal crypto perp with an empty deny-set passes."""
        symbol_filters._set_cache_for_test({
            "BTCUSDT": symbol_filters.SymbolFilters(
                symbol="BTCUSDT", step_size=0.001, tick_size=0.1,
                min_qty=0.001, min_notional=5.0,
            ),
        })
        pm = self._make_pm()
        pm._futures_client._get = AsyncMock(return_value=[
            {"symbol": "BTCUSDT", "quoteVolume": "1000000", "priceChangePercent": "1"},
            {"symbol": "ETHUSDT", "quoteVolume": "900000", "priceChangePercent": "1"},
        ])
        pairs = await pm.fetch_top_futures_pairs(limit=10)
        assert {p.symbol for p in pairs} == {"BTCUSDT", "ETHUSDT"}
