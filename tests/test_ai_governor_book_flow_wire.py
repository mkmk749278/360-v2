"""The governor's order-book and CVD context, wired end to end (2026-09-23).

`build_snapshot` accepted `book_getter` / `flow_getter` from the day the lane
shipped and no caller passed them, so every verdict (200 of 200 on the live
ledger) was recorded book- and flow-blind, labelled ``not_subscribed``, and
`ai_governor_blind` paged hourly. `macro` had the identical defect and was
repaired on 2026-09-10 with these two left behind. These tests pin each hop:
the scanner's one book accessor, the sweep's per-signal getters, the monitor
forwarding its sources, `main.py` setting them, and — derived rather than
listed — that the sweep passes EVERY parameter `build_snapshot` accepts.
"""
from __future__ import annotations

import ast
import inspect
import pathlib
import time

import pytest

from src.execution import ai_governor as gov
from src.execution import ai_governor_snapshot as snap
from src.execution import ai_governor_menu as menu

ROOT = pathlib.Path(__file__).resolve().parents[1]


class _Sig:
    signal_id = "s1"
    symbol = "BTCUSDT"
    entry = 100.0
    stop_loss = 98.0
    tp1 = 104.0
    setup_class = "MOVER_TREND_PULLBACK"
    entry_regime = "TRENDING_UP"
    original_sl_distance = 2.0

    def __init__(self, direction="LONG"):
        self.direction = direction


BOOK = {"bids": [[100.0, 30.0]], "asks": [[100.1, 10.0]]}  # imbalance +0.5
CVD = [float(i) for i in range(40)]  # rising: positive slope


# --- the derived guard ----------------------------------------------------------


def test_the_sweep_passes_every_parameter_build_snapshot_accepts():
    """A parameter one function reads and no caller writes is a dead wire.

    Derived from the signature, so tomorrow's parameter is covered without
    anyone editing this test. Reverting this PR's call-site lines fails it.
    """
    params = set(inspect.signature(snap.build_snapshot).parameters)
    tree = ast.parse(inspect.getsource(gov))
    calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == "build_snapshot"
    ]
    assert calls, "the sweep must build a snapshot"
    for call in calls:
        passed = {k.arg for k in call.keywords}
        assert not (params - passed), f"never passed: {sorted(params - passed)}"


def test_the_monitor_forwards_both_sources_into_the_sweep():
    from src import trade_monitor

    tree = ast.parse(inspect.getsource(trade_monitor))
    calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == "sweep"
        and getattr(n.func.value, "id", "") == "ai_governor"
    ]
    assert calls
    kws = {k.arg: ast.unparse(k.value) for k in calls[0].keywords}
    assert kws.get("book_source") == "self._book_getter"
    assert kws.get("cvd_source") == "self._cvd_getter"


def test_main_sets_both_sources_from_the_scan_paths_own_readers():
    tree = ast.parse((ROOT / "src" / "main.py").read_text())
    assigned = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Attribute) and t.attr in ("_book_getter", "_cvd_getter"):
                    assigned[t.attr] = ast.unparse(node.value)
    assert "current_order_book" in assigned.get("_book_getter", "")
    assert "_governor_cvd_series" in assigned.get("_cvd_getter", "")


# --- the per-signal getters -------------------------------------------------------


@pytest.mark.parametrize("direction,sign", [("LONG", 1), ("SHORT", -1)])
def test_getters_sign_toward_the_trade(direction, sign):
    book = gov._book_getter_for(_Sig(direction), lambda s: BOOK)
    flow = gov._flow_getter_for(_Sig(direction), lambda s: CVD)
    assert book() == pytest.approx(0.5 * sign)
    assert flow() * sign > 0


def test_unwired_and_empty_are_different_facts():
    # No source at all: the snapshot records not_wired.
    assert gov._book_getter_for(_Sig(), None) is None
    assert gov._flow_getter_for(_Sig(), None) is None
    # A source with nothing for the symbol: the getter answers None.
    assert gov._book_getter_for(_Sig(), lambda s: None)() is None
    assert gov._flow_getter_for(_Sig(), lambda s: None)() is None


def _build(book_getter, flow_getter):
    return snap.build_snapshot(
        signal=_Sig(), trigger_tf="15m", as_of_bar_ms=1, bars_since_entry=3,
        last_price=101.0, menu=menu.Menu(tp=(), sl=()),
        book_getter=book_getter, flow_getter=flow_getter,
    )


def test_a_wired_source_makes_the_snapshot_readable():
    built = _build(gov._book_getter_for(_Sig(), lambda s: BOOK),
                   gov._flow_getter_for(_Sig(), lambda s: CVD))
    assert built.blind_fraction() == 0.0
    read = built.readability()
    assert read["book_readable"] and read["flow_readable"]


def test_reasons_name_the_world():
    unwired = _build(None, None).readability()
    assert unwired["book_reason"] == snap.WHY_NOT_WIRED
    empty = _build(gov._book_getter_for(_Sig(), lambda s: None),
                   gov._flow_getter_for(_Sig(), lambda s: None)).readability()
    assert empty["book_reason"] == snap.WHY_NOT_SUBSCRIBED
    assert empty["flow_reason"] == snap.WHY_NOT_SUBSCRIBED


# --- the scanner's one book accessor ---------------------------------------------


def _scanner_stub():
    from src.scanner import Scanner

    s = Scanner.__new__(Scanner)
    s._order_book_snapshot_cache = {}
    return s


def test_current_order_book_serves_only_an_unexpired_snapshot(monkeypatch):
    from src import scanner as scan_mod

    monkeypatch.setattr(scan_mod, "DEPTH_LIVE_FOR_CONSUMERS", False)
    s = _scanner_stub()
    s._order_book_snapshot_cache["BTCUSDT"] = (BOOK, time.monotonic() + 30)
    s._order_book_snapshot_cache["ETHUSDT"] = (BOOK, time.monotonic() - 1)
    assert s.current_order_book("BTCUSDT") is BOOK
    assert s.current_order_book("ETHUSDT") is None
    assert s.current_order_book("XRPUSDT") is None


def test_grace_lets_the_governor_read_a_just_expired_snapshot(monkeypatch):
    """The snapshot refreshes only at a scan cycle's start, so a read landing
    between its expiry and the next refresh saw nothing (4 of 12 post-boot
    verdicts).  The governor's grace covers that gap; beyond it, still None."""
    from src import scanner as scan_mod

    monkeypatch.setattr(scan_mod, "DEPTH_LIVE_FOR_CONSUMERS", False)
    s = _scanner_stub()
    s._order_book_snapshot_cache["ETHUSDT"] = (BOOK, time.monotonic() - 5)
    s._order_book_snapshot_cache["XRPUSDT"] = (BOOK, time.monotonic() - 100)
    assert s.current_order_book("ETHUSDT") is None
    assert s.current_order_book("ETHUSDT", grace_sec=40) is BOOK
    assert s.current_order_book("XRPUSDT", grace_sec=40) is None


def test_the_scan_path_reads_the_book_without_grace():
    """Widening what a live gate reads is an owner decision.  The scan path's
    call must never pass ``grace_sec``; only the governor's getter may."""
    tree = ast.parse((ROOT / "src" / "scanner" / "__init__.py").read_text())
    calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == "current_order_book"
    ]
    assert calls, "the scan path no longer calls current_order_book"
    for call in calls:
        assert not any(k.arg == "grace_sec" for k in call.keywords)

    main_src = (ROOT / "src" / "main.py").read_text()
    assert "grace_sec=GOVERNOR_BOOK_GRACE_SEC" in main_src


def test_current_order_book_prefers_depth_only_when_handed_over(monkeypatch):
    from src import scanner as scan_mod

    depth_book = {"bids": [[1, 1]] * 20, "asks": [[1, 1]] * 20}

    class _Depth:
        def order_book(self, symbol):
            return depth_book

    monkeypatch.setattr(scan_mod, "get_depth_store", lambda: _Depth())
    s = _scanner_stub()
    s._order_book_snapshot_cache["BTCUSDT"] = (BOOK, time.monotonic() + 30)
    monkeypatch.setattr(scan_mod, "DEPTH_LIVE_FOR_CONSUMERS", True)
    assert s.current_order_book("BTCUSDT") is depth_book
    monkeypatch.setattr(scan_mod, "DEPTH_LIVE_FOR_CONSUMERS", False)
    assert s.current_order_book("BTCUSDT") is BOOK


def test_cvd_series_prefers_15m_then_5m_then_none():
    import numpy as np

    from src.main import CryptoSignalEngine as _E  # noqa: F401  (import check)

    class _Store:
        def __init__(self, m15, m5):
            self.m15, self.m5 = m15, m5

        def get_cvd_15m_history(self, symbol):
            return self.m15

        def get_cvd_history(self, symbol):
            return self.m5

    fn = _E._governor_cvd_series
    holder = type("H", (), {})()
    holder._order_flow_store = _Store(np.array([1.0, 2.0]), np.array([9.0]))
    assert list(fn(holder, "X")) == [1.0, 2.0]
    holder._order_flow_store = _Store(np.array([]), np.array([9.0]))
    assert list(fn(holder, "X")) == [9.0]
    holder._order_flow_store = _Store(np.array([]), np.array([]))
    assert fn(holder, "X") is None
    holder._order_flow_store = None
    assert fn(holder, "X") is None


# --- the bookTicker caches count their misses --------------------------------------


def test_book_reads_are_counted_per_lane(monkeypatch):
    """A miss reads as None to every caller, so without a count "the scan saw a
    book" was an assumption. The governor's grace reads are kept apart from the
    live scan's, because only the scan's feed a live gate."""
    from src import scanner as scan_mod

    monkeypatch.setattr(scan_mod, "DEPTH_LIVE_FOR_CONSUMERS", False)
    s = _scanner_stub()
    s._order_book_snapshot_cache["BTCUSDT"] = (BOOK, time.monotonic() + 30)
    s._order_book_snapshot_cache["ETHUSDT"] = (BOOK, time.monotonic() - 5)
    s.current_order_book("BTCUSDT")
    s.current_order_book("ETHUSDT")
    s.current_order_book("ETHUSDT", grace_sec=40)
    s.current_order_book("XRPUSDT", grace_sec=40)
    stats = s._book_stats()
    assert (stats["book_hit_scan"], stats["book_miss_scan"]) == (1, 1)
    assert (stats["book_hit_grace"], stats["book_miss_grace"]) == (1, 1)


async def test_the_invented_spread_is_counted_apart_from_a_real_one():
    from src.scanner import Scanner

    s = Scanner.__new__(Scanner)
    s._order_book_cache = {"BTCUSDT": (0.05, time.monotonic() + 20)}
    assert await s._get_spread_pct("BTCUSDT") == 0.05
    assert await s._get_spread_pct("ETHUSDT") == 0.01
    stats = s._book_stats()
    assert (stats["spread_hit"], stats["spread_fallback"]) == (1, 1)


async def test_the_prefetch_counts_the_entries_its_fresh_skip_left_alone():
    """The pre-fetch skips a symbol whose spread entry is still fresh, and that
    skip also suppresses the book-snapshot write beside it. The only writer of
    that cache is this loop, so the skip hits its own entries — counted, so the
    rewrite cadence is a measurement rather than a reading of the code."""
    from src.scanner import Scanner

    class _Client:
        async def fetch_all_book_tickers(self):
            row = {"bidPrice": "10", "askPrice": "10.01", "bidQty": "5", "askQty": "4"}
            return {"BTCUSDT": dict(row), "ETHUSDT": dict(row)}

    s = Scanner.__new__(Scanner)
    s._order_book_cache = {"BTCUSDT": (0.02, time.monotonic() + 15)}
    s._order_book_snapshot_cache = {}
    s._last_book_ticker_fetch_at = 0.0
    s.futures_client = _Client()
    await s._fetch_global_book_tickers("futures")
    stats = s._book_stats()
    assert stats["fetches"] == 1
    assert stats["last_populated"] == 1
    assert stats["last_skipped_fresh"] == 1
    assert "BTCUSDT" not in s._order_book_snapshot_cache


def test_cycle_health_publishes_the_book_counters_from_a_real_scanner():
    """`read.loop` carries `cycle_health`; a counter that is bumped and never
    published is the seam this repo keeps paying for."""
    from unittest.mock import AsyncMock, MagicMock

    from src.scanner import Scanner

    queue = MagicMock()
    queue.put = AsyncMock(return_value=True)
    router = MagicMock(active_signals={})
    s = Scanner(
        pair_mgr=MagicMock(), data_store=MagicMock(), channels=[],
        smc_detector=MagicMock(), regime_detector=MagicMock(),
        predictive=MagicMock(), exchange_mgr=MagicMock(), spot_client=None,
        telemetry=MagicMock(), signal_queue=queue, router=router,
    )
    s.current_order_book("BTCUSDT")
    health = s.cycle_health()
    assert health["book_ticker"]["book_miss_scan"] == 1
    assert health["book_ticker_ttl_sec"] > 0
