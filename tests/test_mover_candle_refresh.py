"""Promoted movers must keep LIVE candles for their whole scan hold (2026-07-10).

Promoted pairs have no WS kline subscription — the one-time promotion seed was
their only candle write.  Minutes into the 6 h TTL every evaluator read frozen
data, and with REST seeds now stamping freshness (test_seed_freshness_stamp)
the dispatch staleness gate would rightly block them.  The scanner re-seeds
any actively-scanned mover whose 1m age exceeds ``MOVER_CANDLE_REFRESH_SEC``,
throttled per symbol and bounded per cycle.
"""
from __future__ import annotations

import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from src.scanner import Scanner


def _info(vol=1e7, vola=20.0, market="futures"):
    return SimpleNamespace(volume_24h_usd=vol, volatility_24h=vola, market=market)


def _make_scanner(pairs):
    pair_mgr = MagicMock()
    pair_mgr.pairs = pairs
    router = MagicMock(active_signals={})
    router.cleanup_expired.return_value = 0
    sq = MagicMock()
    sq.put = AsyncMock(return_value=True)
    data_store = MagicMock()
    data_store.seed_symbol = AsyncMock()
    return Scanner(
        pair_mgr=pair_mgr, data_store=data_store, channels=[],
        smc_detector=MagicMock(), regime_detector=MagicMock(), predictive=MagicMock(),
        exchange_mgr=MagicMock(), spot_client=None, telemetry=MagicMock(),
        signal_queue=sq, router=router,
    )


async def test_stale_mover_is_reseeded():
    sc = _make_scanner({"GUAUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = 999.0  # stale
    await sc._refresh_stale_mover_candles(["GUAUSDT"])
    sc.data_store.seed_symbol.assert_awaited_once_with("GUAUSDT", "futures")


async def test_fresh_mover_is_not_reseeded():
    sc = _make_scanner({"GUAUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = 10.0  # fresh
    await sc._refresh_stale_mover_candles(["GUAUSDT"])
    sc.data_store.seed_symbol.assert_not_awaited()


async def test_unstamped_mover_is_reseeded():
    # age None = pre-stamp data (restored snapshot / legacy seed) — refresh so
    # the pair carries a real freshness stamp from here on.
    sc = _make_scanner({"GUAUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = None
    await sc._refresh_stale_mover_candles(["GUAUSDT"])
    sc.data_store.seed_symbol.assert_awaited_once()


async def test_refresh_is_throttled_per_symbol():
    sc = _make_scanner({"GUAUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = 999.0
    await sc._refresh_stale_mover_candles(["GUAUSDT"])
    await sc._refresh_stale_mover_candles(["GUAUSDT"])  # immediately again
    assert sc.data_store.seed_symbol.await_count == 1  # throttled


async def test_refresh_bounded_per_cycle():
    from config import MOVER_CANDLE_REFRESH_MAX_PER_CYCLE
    syms = [f"M{i}USDT" for i in range(MOVER_CANDLE_REFRESH_MAX_PER_CYCLE + 5)]
    sc = _make_scanner({s: _info() for s in syms})
    sc.data_store.last_kline_age_seconds.return_value = 999.0
    await sc._refresh_stale_mover_candles(syms)
    assert (
        sc.data_store.seed_symbol.await_count
        == MOVER_CANDLE_REFRESH_MAX_PER_CYCLE
    )


async def test_seed_failure_is_swallowed_and_throttled():
    sc = _make_scanner({"GUAUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = 999.0
    sc.data_store.seed_symbol.side_effect = RuntimeError("rest down")
    await sc._refresh_stale_mover_candles(["GUAUSDT"])  # must not raise
    await sc._refresh_stale_mover_candles(["GUAUSDT"])
    assert sc.data_store.seed_symbol.await_count == 1  # attempt throttled too


async def test_refresh_disabled_by_zero_interval(monkeypatch):
    import config
    monkeypatch.setattr(config, "MOVER_CANDLE_REFRESH_SEC", 0.0)
    sc = _make_scanner({"GUAUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = 999.0
    await sc._refresh_stale_mover_candles(["GUAUSDT"])
    sc.data_store.seed_symbol.assert_not_awaited()
