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

import pytest

from src.pair_manager import (
    _NON_CRYPTO_BLACKLIST,
    _PAIR_BLACKLIST,
    _STABLECOIN_BLACKLIST,
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
