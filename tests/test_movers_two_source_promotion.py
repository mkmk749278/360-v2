"""Mover promotion has two complementary sources: real-time ignition AND top
24h movers. Both must land in the scan universe so VSB/BDS/MOVER_TREND_PULLBACK
can scalp sudden bursts *and* sustained trends (e.g. a pair −40% on the day).
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from src.scanner import Scanner


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
