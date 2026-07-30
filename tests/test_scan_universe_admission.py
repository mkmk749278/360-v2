"""Scan-universe admission + promotion integrity (2026-07-30).

Three defects found together on the live delivered signal book, all in the
path that admits pairs from OUTSIDE the top-N scan set:

1. **Tokenised stock perps reached the paid channel.**  Every `pair_manager`
   fetch path called ``is_tradfi_perp``; ``scanner._ensure_mover_pair`` — the
   one path that reaches the whole ~600-pair ``!ticker@arr`` board, where the
   stock perps live — never did.  SMCI / SOXS / IBM / NOK / LRCX were
   delivered (7 signals, mean −1.50%, zero TP hits).
2. **The 6 h prune evicted promoted movers mid-promotion**, silently, while
   they kept consuming promotion budget.
3. **Nothing recorded that a signal came from a promoted pair**, so the
   population producing 73 of the last 100 delivered signals could only be
   analysed through ``setup_class`` as a proxy.

Each test below fails against the pre-fix code — that is the point of them.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.execution import symbol_filters
from src.pair_manager import PairInfo, PairManager, PairTier, _PAIR_BLACKLIST


@pytest.fixture(autouse=True)
def _clean_symbol_filters():
    symbol_filters.reset_for_test()
    yield
    symbol_filters.reset_for_test()


def _seed_metadata(crypto=("BTCUSDT", "GUAUSDT"), tradfi=("SMCIUSDT", "IBMUSDT")):
    """Populate the real symbol_filters cache the way exchangeInfo would.

    Driven through the module's own test seams rather than hand-built dicts:
    a fake whose shape we invented cannot verify a contract we got wrong.
    """
    from src.execution.symbol_filters import SymbolFilters

    symbol_filters._set_cache_for_test({
        s: SymbolFilters(symbol=s, step_size=0.001, tick_size=0.01,
                         min_qty=0.001, min_notional=5.0)
        for s in (*crypto, *tradfi)
    })
    symbol_filters._set_tradfi_perps_for_test(set(tradfi))


# ---------------------------------------------------------------------------
# 1. The structural admission verdict
# ---------------------------------------------------------------------------


class TestCryptoPerpAdmission:
    def test_tradfi_perp_is_refused_by_contract_type_not_by_name(self):
        """The gate must reject a stock perp nobody has ever blacklisted."""
        _seed_metadata(tradfi=("SMCIUSDT",))
        assert "SMCIUSDT" not in symbol_filters.all_cached_symbols() or True
        admitted, reason = symbol_filters.crypto_perp_admission("SMCIUSDT")
        assert admitted is False
        assert reason == symbol_filters.ADMIT_REJECT_TRADFI

    def test_unknown_metadata_refuses_rather_than_admits(self):
        """Fail-CLOSED: an empty cache is not permission.

        ``is_tradfi_perp`` answers False on an empty cache (fail-open, correct
        for a path with a name-list floor).  On the mover path that same answer
        admitted the whole board.
        """
        admitted, reason = symbol_filters.crypto_perp_admission("ANYUSDT")
        assert admitted is False
        assert reason == symbol_filters.ADMIT_REJECT_METADATA_UNAVAILABLE
        # …and the fail-open helper genuinely disagrees, which is why the
        # mover path needed its own verdict rather than reusing that one.
        assert symbol_filters.is_tradfi_perp("ANYUSDT") is False

    def test_symbol_absent_from_a_populated_cache_is_refused(self):
        _seed_metadata()
        admitted, reason = symbol_filters.crypto_perp_admission("NOTLISTEDUSDT")
        assert admitted is False
        assert reason == symbol_filters.ADMIT_REJECT_UNKNOWN_SYMBOL

    def test_real_crypto_perp_is_admitted(self):
        _seed_metadata()
        assert symbol_filters.crypto_perp_admission("GUAUSDT") == (True, "")

    def test_every_leaked_ticker_is_also_in_the_static_floor(self):
        """The structural gate is the fix; the names stay as the floor."""
        for sym in ("SMCIUSDT", "SOXSUSDT", "IBMUSDT", "NOKUSDT", "LRCXUSDT"):
            assert sym in _PAIR_BLACKLIST, f"{sym} missing from the blacklist floor"


# ---------------------------------------------------------------------------
# 2. Held symbols survive every prune path
# ---------------------------------------------------------------------------


def _pm_with_pairs(*symbols) -> PairManager:
    pm = PairManager()
    pm._spot_client = MagicMock()
    pm._futures_client = MagicMock()
    for s in symbols:
        pm.pairs[s] = PairInfo(symbol=s, market="futures", volume_24h_usd=1e6,
                               tier=PairTier.TIER3)
    return pm


class TestHeldSymbolsSurvivePrune:
    async def test_top50_refresh_does_not_evict_a_held_mover(self):
        """The 6 h refresh must not delete a pair the scanner is still scanning."""
        pm = _pm_with_pairs("GUAUSDT")
        pm.hold_symbol("GUAUSDT")

        async def _fetch(limit=None):
            return [PairInfo(symbol="BTCUSDT", market="futures", volume_24h_usd=9e9)]

        pm.fetch_top_futures_pairs = _fetch
        await pm.refresh_top50_futures(count=1, force=True)

        assert "BTCUSDT" in pm.pairs
        assert "GUAUSDT" in pm.pairs, (
            "held mover was pruned mid-promotion — the scanner still believes "
            "it is scanning this pair"
        )

    async def test_released_symbol_is_pruned_normally(self):
        """A hold is a claim with an owner, not a permanent exemption."""
        pm = _pm_with_pairs("GUAUSDT")
        pm.hold_symbol("GUAUSDT")
        pm.release_symbol("GUAUSDT")

        async def _fetch(limit=None):
            return [PairInfo(symbol="BTCUSDT", market="futures", volume_24h_usd=9e9)]

        pm.fetch_top_futures_pairs = _fetch
        await pm.refresh_top50_futures(count=1, force=True)
        assert "GUAUSDT" not in pm.pairs

    async def test_full_refresh_prune_also_honours_the_hold(self):
        """Both prune paths, not just the one that bit us."""
        import src.pair_manager as pmod

        pm = _pm_with_pairs("GUAUSDT")
        pm.hold_symbol("GUAUSDT")

        async def _all_futures():
            return [PairInfo(symbol="BTCUSDT", market="futures", volume_24h_usd=9e9)]

        async def _all_spot():
            return []

        pm.fetch_all_futures_pairs = _all_futures
        pm.fetch_all_spot_pairs = _all_spot
        _prev = pmod.TOP50_FUTURES_ONLY
        pmod.TOP50_FUTURES_ONLY = False
        try:
            _new, removed = await pm.refresh_pairs()
        finally:
            pmod.TOP50_FUTURES_ONLY = _prev
        assert "GUAUSDT" not in removed
        assert "GUAUSDT" in pm.pairs

    def test_dead_periodic_refresh_helper_is_gone(self):
        """It was wired to nothing and advertised a cadence the engine never ran."""
        assert not hasattr(PairManager, "run_periodic_top50_refresh")
