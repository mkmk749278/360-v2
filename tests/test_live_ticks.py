"""The live aggTrade feed, and the handover it must not perform on its own.

Phase 2a exists because the engine had a complete trade handler, a tick store,
a cap, five consumers and gate telemetry — and no subscription. So the store
served a seed-time REST snapshot and five call sites read it as live.

The trap on the way out is the mirror image: making the data fresh and letting
a money-path gate silently start reading it in the same deploy. These tests pin
that the feed and the handover are two separate things.
"""
from __future__ import annotations

import time

import pytest

from src.live_ticks import QUIET_AFTER_S, LiveTickStore, resolve_recent_ticks


def _msg(price=100.0, qty=2.0, maker=False, ts=None):
    """An ``@aggTrade`` payload in Binance's real field names.

    ``p``/``q``/``m``/``T`` — not a shape invented here. A fixture whose keys
    you chose asserts your assumption back at you and goes green over a reader
    that cannot parse the real thing, which is how a zone reader that guessed
    five key names stayed uncomputable for its whole life.
    """
    return {
        "e": "aggTrade", "s": "BTCUSDT",
        "p": str(price), "q": str(qty), "m": maker,
        "T": int((ts if ts is not None else time.time()) * 1000),
    }


class TestIngestion:
    def test_a_trade_is_stored_with_its_aggressor_side(self):
        """``m`` is 'buyer is the maker', so m=True means the AGGRESSOR sold.

        Stored as the aggressor rather than the raw flag: re-deriving it at
        each call site is how a sign convention gets inverted on half the book,
        which cost two entry features a schema version.
        """
        s = LiveTickStore()
        s.add("BTCUSDT", _msg(maker=False))
        s.add("BTCUSDT", _msg(maker=True))
        rows = s.recent("BTCUSDT")
        assert [r["aggressor"] for r in rows] == ["BUY", "SELL"]

    def test_quote_volume_is_computed_once_at_ingest(self):
        s = LiveTickStore()
        s.add("BTCUSDT", _msg(price=100.0, qty=3.0))
        assert s.recent("BTCUSDT")[0]["quote"] == pytest.approx(300.0)

    def test_a_malformed_payload_is_counted_not_raised(self):
        """Raising here would kill the read loop for every symbol on the
        connection. The failure is already visible as a rejection count, and a
        vendor shape change must not present as a quiet feed."""
        s = LiveTickStore()
        assert s.add("BTCUSDT", {"p": "not-a-number", "q": "1"}) is False
        assert s.add("BTCUSDT", {}) is False
        assert s.health()["total_rejected"] == 2
        assert s.recent("BTCUSDT") == []

    def test_the_ring_is_bounded_and_evicts_oldest_first(self):
        """A deque, not a re-sliced list: the legacy ``append_tick`` copies a
        1,000-element list on every message past the cap, which is free at its
        real call volume (zero) and O(n) per message at aggTrade volume."""
        s = LiveTickStore(maxlen=3)
        for i in range(5):
            s.add("BTCUSDT", _msg(price=float(i)))
        assert [r["price"] for r in s.recent("BTCUSDT")] == [2.0, 3.0, 4.0]

    def test_total_survives_ring_rotation(self):
        """A symbol whose ring has fully rotated still reports true throughput
        — a count bounded by the ring would understate a busy symbol exactly
        when it matters."""
        s = LiveTickStore(maxlen=2)
        for _ in range(10):
            s.add("BTCUSDT", _msg())
        h = s.health()
        assert h["rows"] == 2 and h["total_accepted"] == 10


class TestFeedHealth:
    def test_a_symbol_receiving_trades_is_fed(self):
        s = LiveTickStore()
        s.add("BTCUSDT", _msg())
        assert s.is_fed("BTCUSDT") is True

    def test_a_symbol_that_stopped_is_not_fed_even_with_a_full_ring(self):
        """The defect one store over, avoided: a stream that stopped an hour
        ago still has a full ring, and handing that back as live is exactly the
        stale-but-plausible failure this phase exists to end."""
        s = LiveTickStore()
        s.add("BTCUSDT", _msg())
        s._by_symbol["BTCUSDT"].last_msg_at = time.time() - (QUIET_AFTER_S + 60)
        assert s.is_fed("BTCUSDT") is False
        assert s.recent("BTCUSDT"), "the rows are still there — only 'fed' is false"

    def test_a_never_seen_symbol_is_not_fed(self):
        assert LiveTickStore().is_fed("NOPEUSDT") is False

    def test_subscribed_but_silent_is_its_own_count(self):
        """A subscription that did not take is invisible in any count keyed on
        arrival — it has no key at all. Named separately from 'quiet', which is
        a symbol we have heard from and stopped hearing from."""
        s = LiveTickStore()
        s.note_subscribed(["BTCUSDT", "ETHUSDT", "SOLUSDT"])
        s.add("BTCUSDT", _msg())
        h = s.health()
        assert h["subscribed"] == 3
        assert h["fed"] == 1
        assert h["subscribed_silent"] == 2
        assert set(h["subscribed_silent_sample"]) == {"ETHUSDT", "SOLUSDT"}

    def test_quiet_is_not_reported_as_a_failed_subscription(self):
        """An illiquid perp can genuinely go a minute without an aggressive
        trade. Calling that a fault reports one that is not happening."""
        s = LiveTickStore()
        s.note_subscribed(["BTCUSDT"])
        s.add("BTCUSDT", _msg())
        s._by_symbol["BTCUSDT"].last_msg_at = time.time() - (QUIET_AFTER_S + 1)
        h = s.health()
        assert h["quiet"] == 1 and h["subscribed_silent"] == 0


class TestDriftMeasurement:
    def test_the_gap_against_the_seeded_store_is_reported(self):
        """This is the measurement the handover flag is waiting on: the seeded
        store's age against the live one's is exactly the error every current
        consumer carries."""
        s = LiveTickStore()
        now = time.time()
        s.add("BTCUSDT", _msg(ts=now))
        seeded = {"BTCUSDT": [{"time": (now - 4 * 3600) * 1000, "price": 1.0}]}
        d = s.compare_with_seeded(seeded)
        assert d["compared"] == 1
        assert d["worst"][0]["gap_s"] == pytest.approx(4 * 3600, abs=5)
        assert d["worst"][0]["seeded_age_s"] > 14_000

    def test_a_symbol_missing_from_either_side_is_skipped_not_zeroed(self):
        """A missing counterpart is not a zero gap — scoring it as agreement
        would flatter the seeded store precisely where it has no data."""
        s = LiveTickStore()
        s.add("BTCUSDT", _msg())
        assert s.compare_with_seeded({})["compared"] == 0
        assert s.compare_with_seeded({"ETHUSDT": [{"time": 1}]})["compared"] == 0


class TestTheHandoverIsAFlagNotAConsequence:
    """The whole point of Phase 2a shipping dark.

    Five live consumers — including a `$500k cumulative tick volume` gate —
    read the seeded store. A gate that has been reading seed-time trades for
    months must not silently start reading current ones in the deploy that
    makes them current.
    """

    def _store(self, monkeypatch, *, live_on: bool, fed: bool):
        import config
        from src import live_ticks

        st = LiveTickStore()
        if fed:
            st.add("BTCUSDT", _msg(price=999.0))
        live_ticks.reset_store(st)
        monkeypatch.setattr(config, "TICKS_LIVE_FOR_CONSUMERS", live_on)

        class _Seeded:
            ticks = {"BTCUSDT": [{"price": 1.0, "qty": 1.0, "time": 1}]}

        return _Seeded()

    def test_with_the_flag_off_consumers_still_get_the_seeded_snapshot(
        self, monkeypatch,
    ):
        store = self._store(monkeypatch, live_on=False, fed=True)
        rows, source = resolve_recent_ticks(store, "BTCUSDT")
        assert source == "seed_snapshot"
        assert rows[0]["price"] == 1.0

    def test_with_the_flag_on_consumers_get_the_live_series(self, monkeypatch):
        store = self._store(monkeypatch, live_on=True, fed=True)
        rows, source = resolve_recent_ticks(store, "BTCUSDT")
        assert source == "live"
        assert rows[0]["price"] == 999.0

    def test_the_flag_on_but_the_feed_stopped_falls_back_and_says_so(
        self, monkeypatch,
    ):
        """Falling back is right; falling back *silently* is the bug. The
        source is returned so the caller records which series answered."""
        store = self._store(monkeypatch, live_on=True, fed=False)
        rows, source = resolve_recent_ticks(store, "BTCUSDT")
        assert source == "seed_snapshot" and rows[0]["price"] == 1.0

    def test_neither_series_is_named_none_not_returned_as_empty(
        self, monkeypatch,
    ):
        store = self._store(monkeypatch, live_on=True, fed=False)
        rows, source = resolve_recent_ticks(store, "NOTHINGUSDT")
        assert rows == [] and source == "none"

    def test_the_seam_returns_the_source_not_just_the_rows(self, monkeypatch):
        """Returning rows alone would rebuild the exact ambiguity this method
        exists to remove — five call sites read a stale store as live for
        months because nothing recorded which one they got."""
        store = self._store(monkeypatch, live_on=False, fed=True)
        result = resolve_recent_ticks(store, "BTCUSDT")
        assert isinstance(result, tuple) and len(result) == 2


class TestWiring:
    def test_the_aggtrade_event_is_handled(self):
        import inspect

        from src import main
        src = inspect.getsource(main)
        assert 'elif event == "aggTrade":' in src
        assert "get_live_tick_store().add(symbol, data)" in src

    def test_bootstrap_subscribes_the_stream_and_records_the_subscription(self):
        """`note_subscribed` is what makes a subscription that never delivers
        visible — without it a dead subscription has no key anywhere."""
        import inspect

        from src import bootstrap
        src = inspect.getsource(bootstrap)
        assert "@aggTrade" in src
        assert "note_subscribed" in src
        assert "_ws_futures_aggtrade.start(futures_aggtrade_streams)" in src

    def test_the_measurement_flag_defaults_on_and_the_effect_flag_off(self):
        """Shipping a measurement default-OFF produces an empty panel and a
        decision that keeps getting deferred; shipping the effect default-ON
        changes a live gate with no evidence. They are not the same flag."""
        from config import AGGTRADE_STREAM_ENABLED, TICKS_LIVE_FOR_CONSUMERS

        assert AGGTRADE_STREAM_ENABLED is True
        assert TICKS_LIVE_FOR_CONSUMERS is False

    def test_every_consumer_reads_through_the_seam(self):
        """Pins the migration. A call site left on `data_store.ticks.get` would
        keep silently reading the snapshot after the handover flag is flipped —
        the same defect, surviving its own fix."""
        import pathlib

        root = pathlib.Path(__file__).resolve().parents[1] / "src"
        for rel in ("scanner/__init__.py", "trade_monitor.py"):
            src = (root / rel).read_text(encoding="utf-8")
            assert ".ticks.get(" not in src, (
                f"{rel} still reads the seeded tick store directly"
            )
