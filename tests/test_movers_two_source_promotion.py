"""Mover promotion has two complementary sources: real-time ignition AND top
24h movers. Both must land in the scan universe so VSB/BDS/MOVER_TREND_PULLBACK
can scalp sudden bursts *and* sustained trends (e.g. a pair −40% on the day).
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from src.scanner import Scanner


# The mover-admission funnel is now fail-CLOSED on exchangeInfo metadata
# (2026-07-30): "we do not know what this instrument is" rejects.  Seed the
# REAL symbol_filters cache through its own test seams so these tests exercise
# the production collaborator rather than a shape we invented.
import pytest as _pytest  # noqa: E402

from src.execution import symbol_filters as _sf  # noqa: E402


@_pytest.fixture(autouse=True)
def _seed_exchange_metadata():
    _sf.reset_for_test()
    _known = (
        "BTCUSDT", "ETHUSDT", "GUAUSDT", "SKYAIUSDT", "AAAUSDT", "BBBUSDT",
        "CCCUSDT", "DDDUSDT", "EEEUSDT", "FFFUSDT", "PEPEUSDT", "WIFUSDT",
        "SAMSUNGUSDT", "HOODUSDT", "COINUSDT", "QCOMUSDT", "PLTRUSDT",
        "NEWUSDT",
    )
    _sf._set_cache_for_test({
        s: _sf.SymbolFilters(symbol=s, step_size=0.001, tick_size=0.01,
                             min_qty=0.001, min_notional=5.0)
        for s in _known
    })
    _sf._set_tradfi_perps_for_test(
        {"SAMSUNGUSDT", "HOODUSDT", "COINUSDT", "QCOMUSDT", "PLTRUSDT"}
    )
    yield
    _sf.reset_for_test()


def _info(vol, vola):
    return SimpleNamespace(volume_24h_usd=vol, volatility_24h=vola)


def _make_scanner(pairs):
    pair_mgr = MagicMock()
    pair_mgr.pairs = pairs
    router = MagicMock(active_signals={})
    router.cleanup_expired.return_value = 0
    sq = MagicMock()
    sq.put = AsyncMock(return_value=True)
    sc = Scanner(
        pair_mgr=pair_mgr, data_store=MagicMock(), channels=[],
        smc_detector=MagicMock(), regime_detector=MagicMock(), predictive=MagicMock(),
        exchange_mgr=MagicMock(), spot_client=None, telemetry=MagicMock(),
        signal_queue=sq, router=router,
    )
    # Skip the REST seed — pretend every candidate seeds successfully.
    sc._seed_mover_pair = AsyncMock(return_value=True)
    return sc


class _FakeDetector:
    """Stand-in for MoverIgnitionDetector's universe view."""

    def __init__(self, movers, meta):
        self._movers = movers   # list[(symbol, change_pct, quote_vol)]
        self._meta = meta       # {symbol: (change_pct, quote_vol)}

    def universe_movers(self, min_pct, min_vol):
        return [m for m in self._movers if abs(m[1]) >= min_pct and m[2] >= min_vol]

    def meta(self, sym):
        return self._meta.get(sym.upper())


async def test_outside_universe_mover_is_admitted_and_promoted():
    # pair_mgr only tracks BTC (the top-75 world). The real mover (GUAUSDT −40%)
    # is NOT in pair_mgr — it exists only in the detector's full-universe feed.
    sc = _make_scanner({"BTCUSDT": _info(5e9, 1.0)})
    sc.mover_ignition_pending = {}
    sc.mover_ignition_detector = _FakeDetector(
        movers=[("GUAUSDT", -40.0, 18_000_000.0)],
        meta={"GUAUSDT": (-40.0, 18_000_000.0)},
    )
    await sc._update_movers_promotion(set())
    assert "GUAUSDT" in sc.pair_mgr.pairs                  # admitted so it can be scanned
    assert sc.pair_mgr.pairs["GUAUSDT"].tier.value == "TIER3"
    assert "GUAUSDT" in sc._mover_promoted_pairs           # and promoted
    assert "GUAUSDT" in sc._synthetic_mover_pairs


async def test_ignition_admits_outside_pair_via_detector_meta():
    sc = _make_scanner({})
    sc.mover_ignition_pending = {"NEWUSDT": "short"}
    sc.mover_ignition_detector = _FakeDetector(
        movers=[], meta={"NEWUSDT": (-12.0, 9_000_000.0)})
    await sc._update_movers_promotion(set())
    assert "NEWUSDT" in sc.pair_mgr.pairs                  # admitted from ignition meta
    assert "NEWUSDT" in sc._mover_promoted_pairs


async def test_synthetic_mover_removed_from_pair_mgr_on_expiry():
    sc = _make_scanner({})
    sc.mover_ignition_pending = {}
    sc.mover_ignition_detector = _FakeDetector(
        movers=[("GUAUSDT", -40.0, 18_000_000.0)], meta={"GUAUSDT": (-40.0, 18e6)})
    await sc._update_movers_promotion(set())
    assert "GUAUSDT" in sc.pair_mgr.pairs
    # Force its promotion to have already expired; a quiet detector won't re-add it.
    sc._mover_promoted_pairs["GUAUSDT"] = 0.0
    sc.mover_ignition_detector = _FakeDetector(movers=[], meta={})
    await sc._update_movers_promotion(set())
    assert "GUAUSDT" not in sc.pair_mgr.pairs              # synthetic entry cleaned up
    assert "GUAUSDT" not in sc._mover_promoted_pairs


async def test_both_ignition_and_top_24h_movers_are_promoted():
    pairs = {
        "IGNUSDT": _info(10_000_000, 2.0),    # low 24h move, but igniting now
        "TRENDUSDT": _info(80_000_000, 40.0),  # sustained top mover (−/+40%)
        "SCANNED": _info(90_000_000, 50.0),    # already in main scan
        "THINUSDT": _info(1_000_000, 60.0),    # huge move but too illiquid
    }
    sc = _make_scanner(pairs)
    sc.mover_ignition_pending = {"IGNUSDT": "long"}

    active = await sc._update_movers_promotion({"SCANNED"})

    promoted = set(sc._mover_promoted_pairs)
    assert "IGNUSDT" in promoted        # source 1: ignition
    assert "TRENDUSDT" in promoted      # source 2: top 24h mover
    assert "SCANNED" not in promoted    # already scanned
    assert "THINUSDT" not in promoted   # below liquidity floor
    assert set(active) >= {"IGNUSDT", "TRENDUSDT"}


async def test_top_movers_promoted_even_with_ignition_unwired():
    # ignition off (pending is None) → the 24h-mover source still promotes.
    pairs = {"TRENDUSDT": _info(80_000_000, 40.0)}
    sc = _make_scanner(pairs)
    sc.mover_ignition_pending = None

    await sc._update_movers_promotion(set())
    assert "TRENDUSDT" in sc._mover_promoted_pairs


async def test_promotion_stores_future_expiry_for_six_hour_hold():
    import time

    pairs = {"TRENDUSDT": _info(80_000_000, 40.0)}
    sc = _make_scanner(pairs)
    sc.mover_ignition_pending = None
    await sc._update_movers_promotion(set())
    # Value is a monotonic expiry well in the future (≈ 6h default TTL).
    assert sc._mover_promoted_pairs["TRENDUSDT"] > time.monotonic() + 3600
