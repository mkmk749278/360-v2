"""1d / 1w buckets must advance while the engine runs (2026-11-19).

Neither timeframe has a WS kline subscription, and boot gap-fill measured the
gap from the snapshot's save time (which advances every save) rather than from
the bucket — so after a restart nothing ever wrote them again. BTCUSDT 1d was
found 16 bars behind while 1h/4h were current. The scanner now replaces a
1d/1w bucket once its forming bar has closed, budgeted and throttled.
"""
from __future__ import annotations

import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from src.scanner import Scanner

DAY = 86_400_000
WEEK = 7 * DAY


def _make(pairs, last_open):
    pair_mgr = MagicMock()
    pair_mgr.pairs = {s: SimpleNamespace(market="futures") for s in pairs}
    router = MagicMock(active_signals={})
    data_store = MagicMock()
    data_store.last_bar_open_ms.side_effect = lambda s, tf: last_open(s, tf)
    data_store.refresh_timeframe = AsyncMock(return_value=True)
    return Scanner(
        pair_mgr=pair_mgr, data_store=data_store, channels=[],
        smc_detector=MagicMock(), regime_detector=MagicMock(), predictive=MagicMock(),
        exchange_mgr=MagicMock(), spot_client=None, telemetry=MagicMock(),
        signal_queue=MagicMock(), router=router,
    )


def _now_ms():
    return time.time() * 1000.0


async def test_frozen_daily_bucket_is_replaced_at_seed_depth():
    frozen = _now_ms() - 17 * DAY
    sc = _make(["BTCUSDT"], lambda s, tf: frozen if tf == "1d" else _now_ms() - 1000)
    await sc._refresh_stale_htf_candles()
    sc.data_store.refresh_timeframe.assert_awaited_once_with("BTCUSDT", "1d", 500, "futures")
    assert sc._suppression_counters["htf_refresh:refreshed"] == 1


async def test_forming_bar_still_open_costs_no_call():
    # The not-due path is the common one; it must make no exchange call.
    sc = _make(["BTCUSDT"], lambda s, tf: _now_ms() - 1000)
    await sc._refresh_stale_htf_candles()
    sc.data_store.refresh_timeframe.assert_not_awaited()
    assert sc._suppression_counters["htf_refresh:wanted"] == 0


async def test_weekly_bucket_is_refreshed_once_its_week_closed():
    sc = _make(["BTCUSDT"], lambda s, tf: _now_ms() - WEEK - 1000 if tf == "1w"
               else _now_ms() - 1000)
    await sc._refresh_stale_htf_candles()
    sc.data_store.refresh_timeframe.assert_awaited_once_with("BTCUSDT", "1w", 200, "futures")


async def test_undated_bucket_is_due_not_current():
    sc = _make(["BTCUSDT"], lambda s, tf: None if tf == "1d" else _now_ms())
    await sc._refresh_stale_htf_candles()
    assert sc._suppression_counters["htf_refresh:undated"] == 1
    sc.data_store.refresh_timeframe.assert_awaited_once()


async def test_budget_serves_oldest_first_and_counts_the_shortfall():
    from config import HTF_CANDLE_REFRESH_MAX_PER_CYCLE as cap
    syms = [f"S{i}USDT" for i in range(cap + 3)]
    ages = {s: (i + 2) * DAY for i, s in enumerate(syms)}
    sc = _make(syms, lambda s, tf: _now_ms() - ages[s] if tf == "1d" else _now_ms())
    await sc._refresh_stale_htf_candles()
    served = [c.args[0] for c in sc.data_store.refresh_timeframe.await_args_list]
    assert len(served) == cap
    assert set(served) == set(sorted(syms, key=lambda s: -ages[s])[:cap])
    assert sc._suppression_counters["htf_refresh:deferred"] == 3


async def test_a_failing_symbol_is_throttled_not_retried_every_cycle():
    sc = _make(["BTCUSDT"], lambda s, tf: _now_ms() - 3 * DAY if tf == "1d" else _now_ms())
    sc.data_store.refresh_timeframe.return_value = False
    await sc._refresh_stale_htf_candles()
    await sc._refresh_stale_htf_candles()
    assert sc.data_store.refresh_timeframe.await_count == 1
    assert sc._suppression_counters["htf_refresh:failed"] == 1


async def test_refresher_is_wired_into_the_scan_cycle():
    import ast
    import inspect

    import src.scanner as mod
    tree = ast.parse(inspect.getsource(mod.Scanner.scan_loop).lstrip())
    called = {n.func.attr for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert "_refresh_stale_htf_candles" in called
