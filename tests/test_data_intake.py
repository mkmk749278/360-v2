"""The data-intake X-ray must name what it cannot see.

Every finding this panel exists to surface is an *absence* or a *provenance*,
not a failure: a store fed by a seed-time snapshot, a detector with no writer, a
one-level book. None of them raise, so none of them can be tested by asserting
"no exception". These tests assert the panel **says so** — because a hollow
input behind a passing gate is indistinguishable from a working one, and the
whole point of the page is to make that difference visible.
"""
from __future__ import annotations

import time

import numpy as np
import pytest

from src.data_intake import SCHEMA, build_data_intake


class _Conn:
    """A WSConnection's shape, using the field names the real one carries."""

    def __init__(self, streams, *, degraded=False, connected_ts=None, silent=()):
        self.streams = list(streams)
        self.degraded = degraded
        self.reconnect_attempts = 0
        self.ping_latency_ms = 12.0
        self.last_reconnect_ms = 0.0
        self.connected_ts = (
            connected_ts if connected_ts is not None else time.monotonic()
        )
        self.health_msg_count = 100
        now = time.monotonic()
        self.stream_data_ts = {
            s: (0.0 if s in silent else now) for s in streams
        }


class _Mgr:
    """A WebSocketManager's shape: connections, a label, a staleness multiplier.

    The label is the manager's OWN — the page reads it rather than mapping
    attribute names, so a pool added tomorrow needs no list updated anywhere.
    """

    def __init__(self, conns, label="futures_klines", staleness_multiplier=None):
        self._connections = list(conns)
        self._label = label
        self._staleness_multiplier = staleness_multiplier


class _Store:
    def __init__(self, candles=None, ticks=None):
        self.candles = candles or {}
        self.ticks = ticks or {}


class _Flow:
    def __init__(self):
        self._running_cvd = {"BTCUSDT": 1.0}
        self._running_cvd_15m = {"BTCUSDT": 1.0}
        self._oi = {"BTCUSDT": []}
        self._funding_rates = {"BTCUSDT": 0.0001}
        self._liqs = {"BTCUSDT": []}


class _Book:
    def __init__(self):
        self._levels = {"BTCUSDT": [1, 2, 3]}
        self._refresh_ts = {"BTCUSDT": time.time() - 30}


class _Scanner:
    def __init__(self):
        self.level_book = _Book()
        self._order_book_snapshot_cache = {"BTCUSDT": ({}, 0.0)}
        self.volume_profile_store = type("VP", (), {"_cache": {"BTCUSDT": 1}})()
        self.volume_profile_store_macro = type("VP", (), {"_cache": {"BTCUSDT": 1}})()


def _candles(newest_age_s: float, bars: int = 500):
    """A candle bucket in the store's real shape — numpy arrays, `open_time`
    in **milliseconds**, which is what `historical_data` writes."""
    newest_ms = (time.time() - newest_age_s) * 1000.0
    return {
        "close": np.ones(bars),
        "open_time": np.array([newest_ms - i * 60_000 for i in range(bars)][::-1]),
    }


class _Engine:
    def __init__(self, **kw):
        self._ws_futures = kw.get("ws_futures")
        self._ws_futures_liq = kw.get("ws_liq")
        self._ws_futures_mover = kw.get("ws_mover")
        self._ws_futures_aggtrade = kw.get("ws_aggtrade")
        self._ws = None
        self.pair_mgr = kw.get("pair_mgr")
        self.data_store = kw.get("store", _Store())
        self._order_flow_store = kw.get("flow", _Flow())
        self.scanner = kw.get("scanner", _Scanner())


def _engine_with_current_streams():
    """The subscription set the engine actually starts today: klines,
    forceOrder and !ticker@arr — and deliberately no trade stream."""
    return _Engine(
        ws_futures=_Mgr([_Conn(["btcusdt@kline_1m", "btcusdt@kline_5m"])],
                        label="futures_klines"),
        ws_liq=_Mgr([_Conn(["btcusdt@forceOrder"])], label="futures_liq",
                    staleness_multiplier=100),
        ws_mover=_Mgr([_Conn(["!ticker@arr"])], label="futures_mover"),
    )


# ---------------------------------------------------------------------------
# The absence that started the program
# ---------------------------------------------------------------------------

class TestStreamKinds:
    def test_the_missing_trade_stream_is_reported_by_name(self):
        """An absence cannot be seen in a list of what IS subscribed.

        `@aggTrade` and `@trade` appear in no `.start()` call while a complete
        trade handler waits in `main.py`. The expected kinds are enumerated so
        each is present or absent by name rather than simply not listed.
        """
        rep = build_data_intake(_engine_with_current_streams())
        kinds = rep["stream_kinds"]["kinds"]
        assert kinds["klines"] is True
        assert kinds["liquidations"] is True
        assert kinds["all_market_ticker"] is True
        # The finding.
        assert kinds["aggregate_trades"] is False
        assert kinds["raw_trades"] is False
        assert kinds["depth"] is False

    def test_an_added_aggtrade_subscription_is_detected(self):
        """Phase 2a flips this. Pinned so the panel is proven to be reading the
        subscription rather than hardcoding the answer."""
        eng = _Engine(ws_futures=_Mgr([_Conn(["btcusdt@aggTrade"])]))
        assert build_data_intake(eng)["stream_kinds"]["kinds"]["aggregate_trades"] is True

    def test_a_pool_on_a_new_attribute_is_seen_without_updating_a_list(self):
        """THE regression this page shipped with.

        The first cut hard-coded four pool attribute names, and Phase 2a added
        `_ws_futures_aggtrade` the very next change. The live page then read
        "Aggregate trades: NOT SUBSCRIBED" on a feed nobody could confirm either
        way, because the reporter could not see the pool at all — a hand-written
        list excluding exactly the thing somebody already typed, committed by
        the surface built to catch that class of defect.

        Pools are now discovered by shape. This fails against the old tree.
        """
        eng = _Engine(ws_aggtrade=_Mgr([_Conn(["btcusdt@aggTrade"])],
                                       label="futures_aggtrade"))
        rep = build_data_intake(eng)
        assert rep["stream_kinds"]["kinds"]["aggregate_trades"] is True
        assert "futures_aggtrade" in {p["label"] for p in rep["pools"]}


# ---------------------------------------------------------------------------
# Provenance before freshness
# ---------------------------------------------------------------------------

class TestDerivedProvenance:
    def test_cvd_names_its_source_rather_than_implying_tick_data(self):
        rep = build_data_intake(_engine_with_current_streams())
        assert rep["derived"]["cvd"]["source"] == "kline_taker_buy"
        assert "not tick data" in rep["derived"]["cvd"]["detail"]

    def test_the_tick_store_is_labelled_a_seed_snapshot(self):
        """Five call sites read this store as live. It is whatever
        /fapi/v1/trades returned when the symbol was seeded."""
        rep = build_data_intake(_engine_with_current_streams())
        ticks = rep["derived"]["ticks"]
        assert ticks["source"] == "rest_seed_snapshot"
        assert "@trade" in ticks["detail"]
        assert ticks["consumers"], "consumers must be named — the risk is theirs"

    def test_a_stale_tick_store_shows_its_age(self):
        """The store looks populated whatever its age; only the timestamp of
        the newest trade distinguishes 'live' from 'seeded four hours ago'."""
        old_ms = (time.time() - 4 * 3600) * 1000.0
        store = _Store(ticks={"BTCUSDT": [{"time": old_ms, "price": 1.0}]})
        rep = build_data_intake(_Engine(store=store))
        age = rep["derived"]["ticks"]["newest_trade_age_s"]
        assert age is not None and age > 3_000

    def test_the_order_book_quality_is_badged_not_counted(self):
        """A depth count of 1 invites the reader to assume a thin book. The
        badge says it is one level by construction."""
        rep = build_data_intake(_engine_with_current_streams())
        assert rep["derived"]["order_book"]["quality"] == "top_of_book_only"


# ---------------------------------------------------------------------------
# The hollow-detector panel
# ---------------------------------------------------------------------------

class TestPrimitiveCensus:
    def test_the_orderblock_detector_is_reported_as_having_no_writer(self):
        """Read from `SMCResult` itself, not mirrored — the fix for a drifting
        mirror is one writer and one reader."""
        rep = build_data_intake(_engine_with_current_streams())
        rows = {r["primitive"]: r for r in rep["primitives"]["rows"]}
        assert rows["orderblocks"]["status"] == "not_implemented"
        assert rows["orderblocks"]["healthy"] is False
        assert "bool(fvgs)" in rows["orderblocks"]["detail"]

    def test_the_fvg_lookback_is_on_screen(self):
        """Not a fault — a design choice that makes a loose gate behave like a
        strict one, which is invisible from the gate's own code."""
        rep = build_data_intake(_engine_with_current_streams())
        rows = {r["primitive"]: r for r in rep["primitives"]["rows"]}
        assert rows["fvg"]["status"].startswith("lookback=")

    def test_the_census_renders_when_nothing_is_wrong(self):
        """A check that appears only when it trips teaches the reader that its
        absence means 'fine' when it equally means the check stopped running."""
        rep = build_data_intake(_Engine())
        assert rep["primitives"]["rows"], "census must render unconditionally"


# ---------------------------------------------------------------------------
# Series ageing — undated is not stale
# ---------------------------------------------------------------------------

class TestSeries:
    def test_a_fresh_series_is_not_flagged(self):
        store = _Store(candles={"BTCUSDT": {"1m": _candles(30)}})
        tf = build_data_intake(_Engine(store=store))["series"]["by_timeframe"]["1m"]
        assert tf["series"] == 1 and tf["stale"] == 0 and tf["undated"] == 0

    def test_a_stale_series_is_flagged_and_named(self):
        store = _Store(candles={"BTCUSDT": {"1m": _candles(3600)}})
        tf = build_data_intake(_Engine(store=store))["series"]["by_timeframe"]["1m"]
        assert tf["stale"] == 1
        assert tf["stalest_symbols"][0]["symbol"] == "BTCUSDT"

    def test_a_higher_timeframe_is_aged_against_its_own_budget(self):
        """A 4h bar an hour old is healthy; the same age on 1m is not. One
        global threshold would report a fault that is not happening."""
        store = _Store(candles={"BTCUSDT": {"4h": _candles(3600)}})
        tf = build_data_intake(_Engine(store=store))["series"]["by_timeframe"]["4h"]
        assert tf["stale"] == 0

    def test_undated_bars_are_their_own_bucket_not_stale(self):
        """A series whose bars carry no timestamps cannot be aged at all.
        Calling that 'fresh' is how a restart-dropped `open_time` stayed
        invisible (#842); calling it 'stale' reports the wrong fault."""
        store = _Store(candles={"BTCUSDT": {"1m": {"close": np.ones(10)}}})
        tf = build_data_intake(_Engine(store=store))["series"]["by_timeframe"]["1m"]
        assert tf["undated"] == 1 and tf["stale"] == 0


# ---------------------------------------------------------------------------
# Pools
# ---------------------------------------------------------------------------

class TestPools:
    def test_a_declared_but_unstarted_pool_is_named_not_omitted(self):
        """'Never started' and 'all connections died' both show zero streams,
        and a pool that is simply absent from the page is a third silence."""
        pools = build_data_intake(_Engine())["pools"]
        assert pools, "declared-but-None pools must still be reported"
        assert all(p["state"] == "not_started" for p in pools)
        assert all(p["present"] is False for p in pools)

    def test_a_partially_degraded_pool_is_not_reported_as_healthy(self):
        """Binance drops subsets of subscriptions silently — one degraded
        connection inside a healthy pool is exactly what an aggregate hides."""
        eng = _Engine(ws_futures=_Mgr([
            _Conn(["a@kline_1m"]), _Conn(["b@kline_1m"], degraded=True),
        ], label="futures_klines"))
        pools = {p["label"]: p for p in build_data_intake(eng)["pools"]}
        assert pools["futures_klines"]["state"] == "partially_degraded"
        assert pools["futures_klines"]["degraded_count"] == 1

    def test_silent_streams_are_counted_and_sampled(self):
        eng = _Engine(ws_futures=_Mgr([
            _Conn(["a@kline_1m", "b@kline_1m"], silent={"b@kline_1m"}),
        ], label="futures_klines"))
        pools = {p["label"]: p for p in build_data_intake(eng)["pools"]}
        conn = pools["futures_klines"]["connections"][0]
        assert conn["silent_streams"] == 1
        assert conn["silent_sample"] == ["b@kline_1m"]

    def test_a_pool_whose_silence_is_expected_is_not_flagged(self):
        """@forceOrder fires only during liquidations and is legitimately
        silent for hours — the engine sets staleness_multiplier=100 on that
        pool for exactly that reason. A flat budget flagged 64 of 75 of them
        on the first live read: this page reporting a fault that is not
        happening, against its own rule. The engine's own number is reused
        rather than a second threshold invented here."""
        eng = _Engine(ws_liq=_Mgr(
            [_Conn(["a@forceOrder"], silent={"a@forceOrder"})],
            label="futures_liq", staleness_multiplier=100,
        ))
        pools = {p["label"]: p for p in build_data_intake(eng)["pools"]}
        liq = pools["futures_liq"]
        assert liq["silence_is_expected"] is True
        assert liq["silence_budget_s"] == 12_000.0
        assert liq["connections"][0]["silent_streams"] == 0

    def test_the_24h_forced_cycle_is_reported_as_time_remaining(self):
        """Binance force-closes every connection at 24h. Showing the countdown
        turns a scheduled event into an expected one."""
        eng = _Engine(ws_futures=_Mgr([_Conn(["a@kline_1m"])],
                                      label="futures_klines"))
        pools = {p["label"]: p for p in build_data_intake(eng)["pools"]}
        conn = pools["futures_klines"]["connections"][0]
        assert conn["seconds_to_forced_cycle"] is not None
        assert 86_000 < conn["seconds_to_forced_cycle"] <= 86_400


# ---------------------------------------------------------------------------
# Weight
# ---------------------------------------------------------------------------

class TestWeight:
    def test_the_live_gauge_and_the_declared_table_are_both_present(self):
        """The header value has been synced into the limiter all along and
        nothing rendered it. The declared table sits beside it because a
        disagreement between the two is the early symptom of an
        under-declaration."""
        w = build_data_intake(_Engine())["weight"]
        assert "futures" in w and "budget" in w["futures"]
        assert "/fapi/v1/trades" in w["declared"]
        assert w["declared"]["/fapi/v1/trades"]["weight"] == 5

    def test_every_declared_entry_carries_its_provenance(self):
        w = build_data_intake(_Engine())["weight"]
        for path, row in w["declared"].items():
            assert row["source"], f"{path} has no provenance on the panel"


# ---------------------------------------------------------------------------
# Fail-soft
# ---------------------------------------------------------------------------

class TestFailSoft:
    def test_a_broken_section_reports_its_cause_and_does_not_empty_the_page(self):
        """'The WS pool is down' and 'the WS section raised' are different
        states; pooling them reports a fault that is not happening."""
        class _ExplodingVars:
            """Pool discovery itself raises. Distinct from "no pools": one is a
            quiet engine, the other is a broken reporter, and rendering them
            alike is the failure this page exists to prevent."""

            def __init__(self):
                self.data_store = _Store()

            @property
            def __dict__(self):
                raise RuntimeError("boom")

        rep = build_data_intake(_ExplodingVars())
        assert rep["schema"] == SCHEMA
        assert isinstance(rep["pools"], dict) and "error" in rep["pools"]
        # Other sections still rendered.
        assert "primitives" in rep and rep["primitives"]["rows"]

    def test_the_report_carries_a_schema_and_a_timestamp(self):
        rep = build_data_intake(_Engine())
        assert rep["schema"] == SCHEMA
        assert rep["generated_at"] > 0


class TestWiring:
    def test_the_snapshot_writer_publishes_it(self):
        """In isolated mode the API container's facade cannot see WS state,
        the candle store or the limiter. If the writer stops publishing, the
        page silently falls back to a facade that reports nothing subscribed —
        which looks exactly like an engine with no streams."""
        import inspect

        from src.api import snapshot_writer
        src = inspect.getsource(snapshot_writer)
        assert "_write_data_intake" in src
        assert "KEY_DATA_INTAKE" in src
        assert "await self._write_data_intake()" in src, (
            "the writer defines the method but never calls it in the cycle"
        )

    def test_the_endpoint_prefers_the_published_snapshot(self):
        import inspect

        from src.api import server
        src = inspect.getsource(server)
        assert '"/internal/diag/data-intake"' in src
        assert "published_data_intake" in src
