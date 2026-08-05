"""Per-bar, per-price volume — magnitudes, bounds, and named incompleteness.

Phase 2b's job is to make a distribution exist so Phases 4-5 can pick a
threshold from it. So these tests are mostly about what the store REFUSES to
say: no verdicts, no silent caps, no partial bar rendered as a whole one.
"""
from __future__ import annotations

import pytest

from src.footprint import (
    BAR_MS,
    MAX_BINS_PER_BAR,
    FootprintStore,
    bar_open_ms,
)


def _row(price=100.0, quote=1_000.0, side="BUY", ts_s=1_000_000.0):
    """A normalised row as ``live_ticks.add`` returns it — the real producer's
    shape, not one invented here."""
    return {
        "price": price,
        "qty": quote / price,
        "quote": quote,
        "aggressor": side,
        "isBuyerMaker": side == "SELL",
        "time": ts_s * 1000.0,
    }


class TestBinning:
    def test_bins_are_relative_to_price_not_an_absolute_grid(self):
        """`find_round_numbers` steps by 0.01 below $1 — 1% at $1 and 20% at
        $0.05 — and is inert across a book of sub-dollar movers. An absolute
        footprint grid would have the same defect and be far less visible:
        every cheap symbol would collapse into one bin and read as perfectly
        balanced."""
        s = FootprintStore(bin_bps=10.0)
        # Two symbols four orders of magnitude apart, each moving 0.2%.
        for px in (50_000.0, 50_100.0):
            s.add_row("BTCUSDT", _row(price=px))
        for px in (0.0500, 0.0501):
            s.add_row("PEPEUSDT", _row(price=px))
        s.add_row("BTCUSDT", _row(ts_s=1_000_060.0))
        s.add_row("PEPEUSDT", _row(ts_s=1_000_060.0))
        btc = s.bars("BTCUSDT")[0]
        pepe = s.bars("PEPEUSDT")[0]
        # The same relative move resolves into the same number of bins.
        assert len(btc.bins) == len(pepe.bins) == 2

    def test_the_bin_width_is_stamped_on_every_bar(self):
        """A shape without its granularity is unreadable — the reader cannot
        tell a wall from a rounding artefact."""
        s = FootprintStore(bin_bps=7.5)
        s.add_row("BTCUSDT", _row())
        assert s.open_bar("BTCUSDT").bin_bps == 7.5
        assert s.open_bar("BTCUSDT").as_dict()["bin_bps"] == 7.5

    def test_a_bin_index_maps_back_to_a_price(self):
        """Stored so a reader never has to guess which price the grid was
        anchored to."""
        s = FootprintStore(bin_bps=10.0)
        s.add_row("BTCUSDT", _row(price=100.0))
        s.add_row("BTCUSDT", _row(price=100.1))
        bar = s.open_bar("BTCUSDT")
        idx, _ = bar.poc()
        assert bar.price_of_bin(idx) == pytest.approx(100.0, rel=1e-6)


class TestBoundsRefuseRatherThanTrim:
    def test_a_bar_past_the_bin_cap_keeps_exact_totals_and_says_so(self):
        """Refuse the claim, not the measurement. The bar's totals stay
        correct; only its per-price SHAPE stops, and it carries the fact.
        Silently widening or dropping trades would make a violent bar read as
        a narrow one with understated volume."""
        s = FootprintStore(bin_bps=1.0, max_bins=5)
        for i in range(40):
            s.add_row("BTCUSDT", _row(price=100.0 * (1 + i * 0.001), quote=10.0))
        bar = s.open_bar("BTCUSDT")
        assert bar.bins_capped is True
        assert len(bar.bins) == 5
        assert bar.trades == 40
        assert bar.total_quote == pytest.approx(400.0)   # totals exact
        assert s.health()["capped_bars_total"] == 1

    def test_the_ring_is_bounded_per_symbol(self):
        s = FootprintStore(bars=3)
        for i in range(6):
            s.add_row("BTCUSDT", _row(ts_s=1_000_000.0 + i * 60))
        # 5 sealed (the 6th is still open), capped at 3.
        assert len(s.bars("BTCUSDT")) == 3

    def test_the_default_bin_cap_is_a_real_bound(self):
        assert MAX_BINS_PER_BAR > 0


class TestIncompleteIsAStateNotASmallNumber:
    def test_a_feed_gap_marks_the_open_bar_with_its_cause(self):
        """A bar that lost half its trades holds a fraction of the truth while
        looking exactly like a quiet bar."""
        s = FootprintStore()
        s.add_row("BTCUSDT", _row())
        s.mark_gap("BTCUSDT", "ws_reconnect")
        bar = s.open_bar("BTCUSDT")
        assert bar.incomplete is True
        assert bar.incomplete_reason == "ws_reconnect"
        assert s.health()["incomplete_bars_total"] == 1

    def test_a_gap_on_a_symbol_with_no_open_bar_is_not_invented(self):
        """Nothing was open, so nothing was spoiled. Marking anyway would
        report a fault that is not happening."""
        s = FootprintStore()
        s.mark_gap("NOTHINGUSDT")
        assert s.health()["incomplete_bars_total"] == 0

    def test_cvd_excludes_incomplete_bars_rather_than_summing_them(self):
        """A cumulative sum is exactly where a partial bar's error stops being
        visible."""
        s = FootprintStore()
        s.add_row("BTCUSDT", _row(side="BUY", quote=1_000.0, ts_s=1_000_000.0))
        s.mark_gap("BTCUSDT")
        s.add_row("BTCUSDT", _row(side="BUY", quote=500.0, ts_s=1_000_060.0))
        s.add_row("BTCUSDT", _row(ts_s=1_000_120.0))       # seals bar 2
        assert s.cvd_quote("BTCUSDT") == pytest.approx(500.0)

    def test_an_out_of_order_trade_is_dropped_and_the_bar_marked(self):
        """Across a reconnect a stale message can arrive for a bar already
        sealed. Folding it into the current bar would put volume at the wrong
        minute; dropping it silently would hide that the bar is short."""
        s = FootprintStore()
        s.add_row("BTCUSDT", _row(ts_s=1_000_060.0))
        assert s.add_row("BTCUSDT", _row(ts_s=1_000_000.0)) is False
        assert s.open_bar("BTCUSDT").incomplete_reason == "out_of_order_trade"


class TestMagnitudesNotVerdicts:
    def test_imbalance_is_a_ratio_with_its_side_never_a_boolean(self):
        """A boolean bakes in a threshold, and a threshold chosen now would be
        chosen from no data at all."""
        s = FootprintStore(bin_bps=10.0)
        s.add_row("BTCUSDT", _row(price=100.0, quote=3_000.0, side="BUY"))
        s.add_row("BTCUSDT", _row(price=100.0, quote=1_000.0, side="SELL"))
        imb = s.open_bar("BTCUSDT").max_imbalance()
        assert imb["ratio"] == pytest.approx(3.0)
        assert imb["side"] == "BUY"
        assert imb["one_sided"] is False
        assert "imbalanced" not in imb

    def test_a_level_with_no_opposing_volume_is_infinite_not_a_big_number(self):
        """Dividing by an epsilon would manufacture a finite ratio out of an
        absent one — 'nobody sold here at all' is a different observation from
        'a big ratio'."""
        s = FootprintStore(bin_bps=10.0)
        s.add_row("BTCUSDT", _row(price=100.0, quote=1_000.0, side="BUY"))
        imb = s.open_bar("BTCUSDT").max_imbalance()
        assert imb["ratio"] == float("inf")
        assert imb["one_sided"] is True

    def test_a_tiny_level_can_be_excluded_and_the_floor_is_reported(self):
        """$12 of one-sided volume has a spectacular ratio and means nothing.
        The floor is the caller's, and it rides back so a reader knows what was
        excluded rather than wondering why a level is missing."""
        s = FootprintStore(bin_bps=10.0)
        s.add_row("BTCUSDT", _row(price=100.0, quote=12.0, side="BUY"))
        s.add_row("BTCUSDT", _row(price=101.0, quote=5_000.0, side="BUY"))
        s.add_row("BTCUSDT", _row(price=101.0, quote=4_000.0, side="SELL"))
        imb = s.open_bar("BTCUSDT").max_imbalance(min_quote=1_000.0)
        assert imb["quote"] == pytest.approx(9_000.0)
        assert imb["min_quote_floor"] == 1_000.0

    def test_range_is_published_beside_volume_never_folded_into_a_score(self):
        """Volume that moved price a long way and volume that moved it nowhere
        are different events with the same total — which is the whole of what
        'absorption' means. Both components, no score."""
        s = FootprintStore()
        s.add_row("BTCUSDT", _row(price=100.0))
        s.add_row("BTCUSDT", _row(price=101.0))
        bar = s.open_bar("BTCUSDT")
        assert bar.range_pct == pytest.approx(1.0, rel=1e-3)
        assert "absorption" not in bar.as_dict()

    def test_the_point_of_control_is_the_most_traded_price(self):
        s = FootprintStore(bin_bps=10.0)
        s.add_row("BTCUSDT", _row(price=100.0, quote=100.0))
        s.add_row("BTCUSDT", _row(price=100.5, quote=9_000.0))
        idx, vol = s.open_bar("BTCUSDT").poc()
        assert vol == pytest.approx(9_000.0)
        assert s.open_bar("BTCUSDT").price_of_bin(idx) == pytest.approx(100.5, rel=1e-3)

    def test_size_buckets_have_fixed_edges(self):
        """A percentile basis would move under its own data and make two days
        incomparable."""
        s = FootprintStore()
        for q in (50.0, 500.0, 5_000.0, 50_000.0, 500_000.0):
            s.add_row("BTCUSDT", _row(quote=q))
        buckets = s.open_bar("BTCUSDT").as_dict()["size_buckets"]
        assert list(buckets.values()) == [1, 1, 1, 1, 1]


class TestBarLifecycle:
    def test_bars_seal_on_the_minute_boundary(self):
        s = FootprintStore()
        s.add_row("BTCUSDT", _row(ts_s=1_000_000.0))
        assert s.bars("BTCUSDT") == []
        s.add_row("BTCUSDT", _row(ts_s=1_000_060.0))
        assert len(s.bars("BTCUSDT")) == 1

    def test_the_open_bar_is_excluded_from_reads(self):
        """A bar still being filled is not comparable with a finished one, and
        including it makes every 'latest bar' read low."""
        s = FootprintStore()
        s.add_row("BTCUSDT", _row(quote=1_000.0, ts_s=1_000_000.0))
        s.add_row("BTCUSDT", _row(quote=5.0, ts_s=1_000_060.0))
        assert [b.total_quote for b in s.bars("BTCUSDT")] == [1_000.0]

    def test_bar_open_ms_floors_to_the_minute(self):
        assert bar_open_ms(1_000_059_999) % BAR_MS == 0

    def test_the_baseline_is_a_median_not_a_mean(self):
        """One liquidation cascade sets a mean nothing else can approach."""
        s = FootprintStore()
        for i, q in enumerate([100.0, 100.0, 100.0, 1_000_000.0]):
            s.add_row("BTCUSDT", _row(quote=q, ts_s=1_000_000.0 + i * 60))
        s.add_row("BTCUSDT", _row(ts_s=1_000_300.0))
        assert s.volume_baseline("BTCUSDT") == pytest.approx(100.0)


class TestDetectorNotDuplicate:
    def test_tick_cvd_lives_under_its_own_key(self):
        """OrderFlowStore already computes CVD from kline taker fields. A
        second computation of the same quantity is a detector, not a
        duplicate — provided it never overwrites the first. It does not: this
        one is only reachable through the footprint store."""
        from src.order_flow import OrderFlowStore

        assert not hasattr(OrderFlowStore, "cvd_quote")
        assert hasattr(FootprintStore, "cvd_quote")


class TestWiring:
    def test_one_parse_feeds_both_stores(self):
        """The read loop handles thousands of messages a second; parsing each
        twice to fill two stores is waste that grows with the universe."""
        import inspect

        from src import main
        src = inspect.getsource(main)
        assert "_row = get_live_tick_store().add(symbol, data)" in src
        assert "get_footprint_store().add_row(symbol, _row)" in src

    def test_live_ticks_add_returns_the_row_for_reuse(self):
        from src.live_ticks import LiveTickStore

        st = LiveTickStore()
        row = st.add("BTCUSDT", {"p": "100", "q": "2", "m": False, "T": 1})
        assert isinstance(row, dict) and row["quote"] == pytest.approx(200.0)
        assert st.add("BTCUSDT", {"p": "nope"}) is None

    def test_a_reconnect_marks_the_footprint(self):
        """A bar open across a feed gap must carry its cause. Marked on the
        reconnect itself, not inferred from silence — an illiquid symbol is
        legitimately quiet and inferring a gap from that reports one that never
        happened."""
        import inspect

        from src import websocket_manager
        src = inspect.getsource(websocket_manager)
        assert "_mark_footprint_gap" in src
        assert "@aggTrade" in src

    def test_the_gap_marker_ignores_connections_without_aggtrade(self):
        """Marking a kline-only connection would flag bars that were never at
        risk."""
        from src.footprint import get_store, reset_store
        from src.websocket_manager import WebSocketManager

        reset_store(FootprintStore())
        store = get_store()
        store.add_row("BTCUSDT", _row())

        class _Conn:
            streams = ["btcusdt@kline_1m"]

        mgr = WebSocketManager.__new__(WebSocketManager)
        mgr._mark_footprint_gap(_Conn())
        assert store.open_bar("BTCUSDT").incomplete is False

        class _AggConn:
            streams = ["btcusdt@aggTrade"]

        mgr._mark_footprint_gap(_AggConn())
        assert store.open_bar("BTCUSDT").incomplete is True
        reset_store(None)
