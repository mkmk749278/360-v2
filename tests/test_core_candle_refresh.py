"""Tier-1 CORE pairs must recover from dead kline streams (2026-08-29).

Core pairs have a WS kline subscription, so their 1m age hovers near zero at
steady state.  When a stream dies silently nothing re-seeded a core pair —
the mover sweep covers only promoted pairs and `seed_all` runs only at boot —
which is how 18 Tier-1 pairs (including BTCUSDT) sat unusable on the live box
for days while the coverage probe named the fault every cycle.  The scanner
now runs a dead-stream recovery sweep: re-seed any Tier-1 futures pair whose
1m age exceeds ``CORE_CANDLE_REFRESH_SEC``, throttled per symbol and bounded
per cycle, with the shortfall counted (``core_reseed:deferred``) rather than
silently dropped.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import src.scanner as scanner_mod
from src.scanner import Scanner


def _info(vol=1e7, vola=20.0, market="futures"):
    return SimpleNamespace(volume_24h_usd=vol, volatility_24h=vola, market=market)


def _make_scanner(pairs, tier1=None):
    pair_mgr = MagicMock()
    pair_mgr.pairs = pairs
    pair_mgr.tier1_futures_symbols.return_value = (
        list(pairs) if tier1 is None else list(tier1)
    )
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


async def test_dead_stream_core_pair_is_reseeded():
    sc = _make_scanner({"BTCUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = 9999.0  # dead stream
    await sc._refresh_stale_core_candles()
    sc.data_store.seed_symbol.assert_awaited_once_with("BTCUSDT", "futures")


async def test_healthy_core_pair_is_left_alone():
    sc = _make_scanner({"BTCUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = 5.0  # WS is writing
    await sc._refresh_stale_core_candles()
    sc.data_store.seed_symbol.assert_not_awaited()


async def test_never_stamped_core_pair_is_reseeded():
    # age None on a core pair means the WS stream never wrote a single
    # frame — the worst case, not evidence of freshness.
    sc = _make_scanner({"BTCUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = None
    await sc._refresh_stale_core_candles()
    sc.data_store.seed_symbol.assert_awaited_once()


async def test_refresh_is_throttled_per_symbol():
    sc = _make_scanner({"BTCUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = 9999.0
    await sc._refresh_stale_core_candles()
    await sc._refresh_stale_core_candles()  # immediately again
    assert sc.data_store.seed_symbol.await_count == 1  # throttled


async def test_refresh_bounded_per_cycle_and_shortfall_counted():
    from config import CORE_CANDLE_REFRESH_MAX_PER_CYCLE
    n_extra = 5
    syms = [f"C{i}USDT" for i in range(CORE_CANDLE_REFRESH_MAX_PER_CYCLE + n_extra)]
    sc = _make_scanner({s: _info() for s in syms})
    sc.data_store.last_kline_age_seconds.return_value = 9999.0
    await sc._refresh_stale_core_candles()
    assert (
        sc.data_store.seed_symbol.await_count
        == CORE_CANDLE_REFRESH_MAX_PER_CYCLE
    )
    # The budget shortfall is counted, not silently dropped.
    assert sc._suppression_counters["core_reseed:deferred"] == n_extra
    assert sc._suppression_counters["core_reseed:wanted"] == len(syms)
    assert (
        sc._suppression_counters["core_reseed:refreshed"]
        == CORE_CANDLE_REFRESH_MAX_PER_CYCLE
    )


async def test_seed_failure_is_swallowed_and_throttled():
    sc = _make_scanner({"BTCUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = 9999.0
    sc.data_store.seed_symbol.side_effect = RuntimeError("rest down")
    await sc._refresh_stale_core_candles()  # must not raise
    await sc._refresh_stale_core_candles()
    assert sc.data_store.seed_symbol.await_count == 1  # attempt throttled too


async def test_refresh_disabled_by_zero_interval(monkeypatch):
    import config
    monkeypatch.setattr(config, "CORE_CANDLE_REFRESH_SEC", 0.0)
    sc = _make_scanner({"BTCUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = 9999.0
    await sc._refresh_stale_core_candles()
    sc.data_store.seed_symbol.assert_not_awaited()


async def test_only_tier1_futures_population_is_swept():
    # The sweep asks pair_mgr.tier1_futures_symbols() — Tier 2/3 discovery
    # pairs are REST-polled by design and must not consume the budget.
    sc = _make_scanner(
        {"BTCUSDT": _info(), "TINYUSDT": _info()}, tier1=["BTCUSDT"],
    )
    sc.data_store.last_kline_age_seconds.return_value = 9999.0
    await sc._refresh_stale_core_candles()
    sc.data_store.seed_symbol.assert_awaited_once_with("BTCUSDT", "futures")


async def test_stub_pair_manager_without_tier_helper_is_a_noop():
    # Minimal test/diagnostic pair managers predate tiers — fail soft.
    sc = _make_scanner({"BTCUSDT": _info()})
    del sc.pair_mgr.tier1_futures_symbols
    sc.pair_mgr.mock_add_spec([], spec_set=False)  # ensure attr truly absent
    sc.pair_mgr.tier1_futures_symbols = None
    sc.data_store.last_kline_age_seconds.return_value = 9999.0
    await sc._refresh_stale_core_candles()  # must not raise
    sc.data_store.seed_symbol.assert_not_awaited()


async def test_first_refresh_runs_on_a_freshly_booted_clock():
    """A low ``time.monotonic()`` must not throttle the FIRST-EVER refresh.

    ``time.monotonic()`` counts from BOOT on Linux, not from process start, so
    on a fresh machine it returns a small number — 120s here.  The throttle
    originally defaulted a missing entry to ``0.0``, which is a real value on
    that same scale, so ``now_mono - 0.0 < CORE_CANDLE_REFRESH_SEC`` was TRUE
    and the sweep skipped every symbol for the first 300s of process life.

    That is the worst window to be silent in: a just-restarted engine is
    exactly when a dead stream's backfill gap is widest, and it is the state
    autoheal leaves the container in.  It also made the suite host-dependent —
    green on a long-lived dev box, red on a fresh CI runner, which is how it
    reached a PR (2026-08-31).
    """
    sc = _make_scanner({"BTCUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = 9999.0
    with patch.object(scanner_mod.time, "monotonic", return_value=120.0):
        await sc._refresh_stale_core_candles()
    sc.data_store.seed_symbol.assert_awaited_once_with("BTCUSDT", "futures")


async def test_throttle_still_holds_on_a_freshly_booted_clock():
    # The converse of the above: fixing the sentinel must not disable the
    # throttle itself.  Two sweeps 1s apart on a low clock = still one attempt.
    sc = _make_scanner({"BTCUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = 9999.0
    with patch.object(scanner_mod.time, "monotonic", return_value=120.0):
        await sc._refresh_stale_core_candles()
    with patch.object(scanner_mod.time, "monotonic", return_value=121.0):
        await sc._refresh_stale_core_candles()
    assert sc.data_store.seed_symbol.await_count == 1


async def test_heartbeat_progress_is_touched_per_reseed():
    # REST-bound work before any symbol finishes scanning — the wedge
    # detector is owed a beat per completed unit (same contract as the
    # mover sweep).
    sc = _make_scanner({"BTCUSDT": _info()})
    sc.data_store.last_kline_age_seconds.return_value = 9999.0
    beats = []
    sc._touch_heartbeat_progress = lambda: beats.append(1)
    await sc._refresh_stale_core_candles()
    assert len(beats) == 1
