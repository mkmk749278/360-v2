"""The SAR ledger must keep the candles it needs to resolve its own records.

Regression cover for the 2026-07-28 defect. The resolver reads only the warm
in-memory 15m store. A promoted mover has no WS subscription — the scanner's
``_refresh_stale_mover_candles`` is its only 15m writer, and that runs solely
for *actively scanned* movers. So when a mover rotates out, its 15m array stops
advancing: the walker sees a window that ends before the trade's exit, returns a
WINDOW verdict, ``classify_pending`` rightly refuses that as "ran out of
candles", and the record sits RUNNING for 48h before ageing into INSUFFICIENT.

What the owner saw on /signals/sar: four mover rows at RUNNING carrying live
marks of −6% to −10%, for trades that had already stopped out at their 3% SL
cap — COTIUSDT 15 minutes after entry, KAITOUSDT 120 minutes after. The page's
UNREAL % is a mark, not a result, so the arm's real loss (≈ −1R) was overstated
by 2–3× on the one screen an adoption decision reads.

Neither watchdog could see it. The miss was silent by construction (no counter,
no log), and ``candle_coverage`` walks ``pair_mgr.pairs`` — the current universe
— which by definition excludes the rotated-out symbols at risk.

The contract now: the resolver keeps its own data alive for symbols it still
owes a verdict on, counts every fetch it could not serve, and pages on the rate.
"""
from __future__ import annotations

import time

import numpy as np
import pytest

from src import sar_exit_shadow as sar
from src import suppression_audit as sa
from src.historical_data import HistoricalDataStore
from src.suppression_audit import SuppressedCandidateStore

BAR_MS = 15 * 60 * 1000.0


@pytest.fixture(autouse=True)
def _clear_pair_cooldown():
    """The stamp throttles are module-globals.

    Without this, the second test to stamp a given symbol is silently throttled
    and its ``stamp_sar_pair`` returns False — a green suite measuring nothing.
    Goes through the module's own hook rather than naming the maps: the
    same-move map added on 2026-07-28 leaks identically, and a hand-maintained
    list of globals to clear is exactly what drifts.
    """
    sar.reset_pair_throttles()
    yield
    sar.reset_pair_throttles()


# ---------------------------------------------------------------------------
# The regression: frozen candles must not resolve, refreshed ones must
# ---------------------------------------------------------------------------


def _opposed_long_path(warmup: int, post: int, *, sl_at: int):
    """A LONG taken into a downtrend (SAR opposed), stopped out at ``sl_at``.

    Mirrors COTIUSDT/KAITOUSDT: the indicator sits above price at entry, so the
    live SL — not the trail — governs, and price takes it out a few bars in.
    """
    opens, highs, lows, closes = [], [], [], []
    # Warmup: a clean downtrend into the entry, which is what leaves the SAR
    # bearish (above price) on the last bar closed at entry.
    for i in range(warmup):
        px = 130.0 - i * (30.0 / max(1, warmup))
        opens.append(px + 0.2)
        highs.append(px + 0.4)
        lows.append(px - 0.4)
        closes.append(px)
    # Post-entry: drifts down, then breaks the 97.0 stop on bar ``sl_at``.
    for i in range(post):
        px = 100.0 - i * 0.35
        low = px - 0.4
        if i >= sl_at:
            px, low = 94.0, 93.0
        opens.append(px + 0.2)
        highs.append(px + 0.4)
        lows.append(low)
        closes.append(px)
    return opens, highs, lows, closes


def _fetcher(opens, highs, lows, closes, entry_index, *, visible_bars=None):
    """A resolver fetcher over a fixed series, optionally truncated.

    ``visible_bars`` truncates the post-entry slice — the frozen-array case: the
    symbol rotated out, so the store still holds every bar up to the freeze and
    nothing after it.
    """
    end = len(closes) if visible_bars is None else entry_index + 1 + visible_bars

    def _fetch(symbol: str, since_ts: float):
        return {
            "open": list(opens[:end]),
            "high": list(highs[:end]),
            "low": list(lows[:end]),
            "close": list(closes[:end]),
            "entry_index": entry_index,
        }

    return _fetch


def _stamp_pair(store):
    assert sar.stamp_sar_pair(
        symbol="COTIUSDT", channel="scalp", setup_class="MOVER_TREND_PULLBACK",
        side="LONG", entry=100.0, stop_loss=97.0, tp1=106.0, store=store,
    ) is True


def _trail_record(store):
    return {r["setup_class"]: r for r in store.records()}[
        "MOVER_TREND_PULLBACK@SAREXIT"
    ]


class TestFrozenCandlesLeaveTheRecordUnresolvable:
    """The bug, stated as a contract: a short window is not a verdict."""

    WARMUP = 40
    POST = 30
    SL_AT = 6

    def test_a_frozen_array_ending_before_the_exit_resolves_nothing(self, tmp_path):
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        _stamp_pair(store)
        opens, highs, lows, closes = _opposed_long_path(
            self.WARMUP, self.POST, sl_at=self.SL_AT
        )

        # The store froze two bars before the stop was taken out.
        counters = store.classify_pending(
            fetch_ohlc_since=_fetcher(
                opens, highs, lows, closes, self.WARMUP,
                visible_bars=self.SL_AT - 2,
            ),
            now_ts=time.time() + 600,   # mid-window: 10 min into a 48h window
            window_sec=48 * 3600.0,
            trail_classifier=sar.classify_sar_record,
        )

        assert _trail_record(store)["classification"] is None, (
            "a window that ends before the exit is the walker running out of "
            "candles, not the trade closing — it must not book a verdict"
        )
        assert sa.INSUFFICIENT not in counters, (
            "mid-window, missing candles are 'not yet', never 'we don't know'"
        )

    def test_refreshed_candles_covering_the_exit_resolve_it(self, tmp_path):
        """Same record, same series, same mid-window clock — the *only*
        difference is that the array now reaches past the stop, which is exactly
        what the resolver's own candle refresh restores for a rotated-out symbol.

        Note what this pair does and does not prove. Both tests inject the
        fetcher, so they pin the *mechanism* — short window ⇒ no verdict, full
        window ⇒ verdict — and would pass against the pre-fix code too. The
        tests that fail without the fix are the ones covering the new surface:
        ``TestRefreshTimeframe``, ``TestCandleFetchHealth``,
        ``TestUnresolvedSymbols``.
        """
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        _stamp_pair(store)
        opens, highs, lows, closes = _opposed_long_path(
            self.WARMUP, self.POST, sl_at=self.SL_AT
        )

        store.classify_pending(
            fetch_ohlc_since=_fetcher(opens, highs, lows, closes, self.WARMUP),
            now_ts=time.time() + 600,   # still mid-window — early resolution
            window_sec=48 * 3600.0,
            trail_classifier=sar.classify_sar_record,
        )

        rec = _trail_record(store)
        assert rec["classification"] == sa.WOULD_LOSE
        # Vocabulary comes from the ledger module, never re-typed here.
        assert rec["trail_exit_reason"] in sa._FINAL_REASONS, (
            "only a final exit may resolve early; a WINDOW verdict mid-window "
            "is the walker marking to the last bar it can see"
        )
        # The arm's loss is bounded by the geometry it ran on — the point the
        # ops page obscured by showing a −10% live mark instead.
        assert rec["trail_exit_price"] <= 100.0

    def test_the_hold_reflects_the_real_stop_not_the_freeze(self, tmp_path):
        """A resolved record must date the exit from the bar that caused it."""
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        _stamp_pair(store)
        opens, highs, lows, closes = _opposed_long_path(
            self.WARMUP, self.POST, sl_at=self.SL_AT
        )
        store.classify_pending(
            fetch_ohlc_since=_fetcher(opens, highs, lows, closes, self.WARMUP),
            now_ts=time.time() + 600,
            window_sec=48 * 3600.0,
            trail_classifier=sar.classify_sar_record,
        )
        hold = _trail_record(store)["trail_hold_min"]
        assert hold == pytest.approx(self.SL_AT * 15.0), (
            f"stop was taken out on post-entry bar {self.SL_AT}; hold must date "
            f"from that bar, got {hold} min"
        )


# ---------------------------------------------------------------------------
# refresh_timeframe — replace, never merge
# ---------------------------------------------------------------------------


def _block(n: int, *, last_open_ms: float, base: float):
    ot = np.array(
        [last_open_ms - (n - 1 - i) * BAR_MS for i in range(n)], dtype=np.float64
    )
    px = np.array([base + i * 0.1 for i in range(n)], dtype=np.float64)
    return {
        "open": px.copy(), "high": px + 0.5, "low": px - 0.5,
        "close": px.copy(), "volume": np.ones(n), "open_time": ot,
    }


class TestRefreshTimeframe:
    @pytest.fixture()
    def store(self):
        return HistoricalDataStore()

    async def test_it_replaces_rather_than_merges(self, store, monkeypatch):
        """Merging is not a milder version of this — it is the bug again.

        ``_merge_candles`` concatenates with no dedupe on ``open_time``, so an
        overlapping REST pull duplicates bars. A duplicate reads as a zero-width
        gap to the resolver's contiguity guard, which then refuses the whole
        window — a refresh written to make a record resolvable would have made
        it permanently unresolvable.
        """
        now_ms = time.time() * 1000.0
        frozen = _block(60, last_open_ms=now_ms - 20 * BAR_MS, base=100.0)
        store.candles["COTIUSDT"] = {"15m": frozen}
        fresh = _block(200, last_open_ms=now_ms - BAR_MS, base=90.0)

        async def _fake_fetch(symbol, interval, limit, market="spot"):
            return fresh

        monkeypatch.setattr(store, "fetch_candles", _fake_fetch)
        assert await store.refresh_timeframe("COTIUSDT", "15m", 200, "futures") is True

        got = store.candles["COTIUSDT"]["15m"]
        assert len(got["close"]) == 200, "the bucket was merged, not replaced"
        diffs = np.diff(got["open_time"])
        assert np.all(np.abs(diffs - BAR_MS) < 1.0), (
            "the refreshed window must be strictly contiguous — a duplicated or "
            "missing bar is what the resolver's guard rejects"
        )

    async def test_it_stamps_freshness(self, store, monkeypatch):
        """A REST write is fresh data; ``fetch_and_store_fallback`` not stamping
        is why this needed its own method rather than reuse."""
        now_ms = time.time() * 1000.0

        async def _fake_fetch(symbol, interval, limit, market="spot"):
            return _block(100, last_open_ms=now_ms - BAR_MS, base=100.0)

        monkeypatch.setattr(store, "fetch_candles", _fake_fetch)
        assert store.last_kline_age_seconds("COTIUSDT", "15m") is None
        await store.refresh_timeframe("COTIUSDT", "15m", 100, "futures")
        age = store.last_kline_age_seconds("COTIUSDT", "15m")
        assert age is not None and age < 5.0

    async def test_a_failed_fetch_leaves_existing_data_untouched(self, store, monkeypatch):
        now_ms = time.time() * 1000.0
        frozen = _block(60, last_open_ms=now_ms - 20 * BAR_MS, base=100.0)
        store.candles["COTIUSDT"] = {"15m": frozen}

        async def _empty(symbol, interval, limit, market="spot"):
            return {}

        monkeypatch.setattr(store, "fetch_candles", _empty)
        assert await store.refresh_timeframe("COTIUSDT", "15m", 200, "futures") is False
        assert len(store.candles["COTIUSDT"]["15m"]["close"]) == 60

    async def test_a_raising_fetch_is_recorded_not_propagated(self, store, monkeypatch):
        """Fail-open, but counted — a refresh error must not kill the batch."""
        from src import fail_open

        async def _boom(symbol, interval, limit, market="spot"):
            raise RuntimeError("binance said no")

        monkeypatch.setattr(store, "fetch_candles", _boom)
        site = "historical_data.refresh_timeframe"
        before = (fail_open.snapshot().get(site) or {}).get("count", 0)
        assert await store.refresh_timeframe("COTIUSDT", "15m", 200, "futures") is False
        after = fail_open.snapshot().get(site) or {}
        assert after.get("count", 0) == before + 1
        assert "binance said no" in after.get("last_error", "")


# ---------------------------------------------------------------------------
# Telemetry — the silence is what let this live
# ---------------------------------------------------------------------------


class TestCandleFetchHealth:
    def setup_method(self):
        sar.reset_candle_fetch_health()

    def teardown_method(self):
        sar.reset_candle_fetch_health()

    def test_counters_are_published_per_cycle_not_cumulatively(self):
        """A cumulative miss count never recovers, so it would page forever
        over a fault that healed."""
        sar.record_candle_fetch("COTIUSDT", False, "no 15m array")
        sar.roll_candle_fetch_cycle()
        assert sar.candle_fetch_health()["miss"] == 1

        sar.record_candle_fetch("COTIUSDT", True)
        sar.roll_candle_fetch_cycle()
        health = sar.candle_fetch_health()
        assert health["miss"] == 0 and health["ok"] == 1, (
            "last cycle was clean; the probe must see a clean cycle"
        )

    def test_a_miss_carries_its_cause(self):
        """'Blank' needs a cause before it gets a caption — the whole reason a
        bare None was not enough."""
        sar.record_candle_fetch("TAGUSDT", False, "no 15m array (rotated out?)")
        sar.roll_candle_fetch_cycle()
        health = sar.candle_fetch_health()
        assert health["reasons"] == {"no 15m array (rotated out?)": 1}
        assert health["symbols"]["TAGUSDT"].startswith("no 15m array")

    def test_a_symbol_that_recovers_leaves_the_failing_set(self):
        sar.record_candle_fetch("TAGUSDT", False, "no 15m array")
        sar.record_candle_fetch("TAGUSDT", True)
        sar.roll_candle_fetch_cycle()
        assert sar.candle_fetch_health()["symbols"] == {}

    def test_the_failing_symbol_map_is_bounded(self):
        for i in range(sar._CANDLE_SYMBOL_CAP + 50):
            sar.record_candle_fetch(f"SYM{i}USDT", False, "no 15m array")
        sar.roll_candle_fetch_cycle()
        health = sar.candle_fetch_health()
        assert len(health["symbols"]) == sar._CANDLE_SYMBOL_CAP
        # The count is never capped — only the per-symbol detail is.
        assert health["miss"] == sar._CANDLE_SYMBOL_CAP + 50


# ---------------------------------------------------------------------------
# unresolved_symbols — who the refresh budget is spent on
# ---------------------------------------------------------------------------


class TestUnresolvedSymbols:
    @pytest.fixture()
    def store(self, tmp_path, monkeypatch):
        s = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        monkeypatch.setattr(sar, "get_sar_store", lambda: s)
        return s

    def _stamp(self, store, symbol):
        assert sar.stamp_sar_pair(
            symbol=symbol, channel="scalp", setup_class="MOVER_TREND_PULLBACK",
            side="LONG", entry=100.0, stop_loss=97.0, tp1=106.0, store=store,
        ) is True

    def test_oldest_stamp_first(self, store):
        """A bounded budget must be spent on the records closest to ageing out,
        not on whichever symbol happens to sort first."""
        self._stamp(store, "AAAUSDT")
        for rec in store.records():
            rec["suppress_timestamp"] = time.time() - 3600
        # Cooldown is per (symbol, setup, side), so a second symbol is free.
        self._stamp(store, "ZZZUSDT")

        assert sar.unresolved_symbols(window_sec=48 * 3600.0) == [
            "AAAUSDT", "ZZZUSDT",
        ]

    def test_resolved_records_are_excluded(self, store):
        self._stamp(store, "AAAUSDT")
        for rec in store.records():
            rec["classification"] = sa.WOULD_LOSE
        assert sar.unresolved_symbols(window_sec=48 * 3600.0) == []

    def test_records_past_their_window_are_excluded(self, store):
        """Their verdict is already decided — refreshing buys nothing and burns
        REST weight."""
        self._stamp(store, "AAAUSDT")
        for rec in store.records():
            rec["suppress_timestamp"] = time.time() - 72 * 3600
        assert sar.unresolved_symbols(window_sec=48 * 3600.0) == []

    def test_the_budget_is_respected(self, store):
        self._stamp(store, "AAAUSDT")
        self._stamp(store, "BBBUSDT")
        assert len(sar.unresolved_symbols(window_sec=48 * 3600.0, limit=1)) == 1


# ---------------------------------------------------------------------------
# The 2026-07-29 defect: a budget smaller than the ledger starves it silently
# ---------------------------------------------------------------------------
# The refresh loop took the first ``MAX_PER_CYCLE`` due symbols off an
# oldest-first list and ``break``ed. With a per-symbol throttle of 900s on a
# 300s loop, a cycle cap of N sustains only 3N distinct symbols — at the old
# default of 8 that was 24, while the ledger carried 85. The 61 starved symbols
# were never fetched, so they never counted as a fetch *miss* either: the
# candle-health probe read a clean 100% while most of the ledger got no candles.
#
# What the owner saw on the 2026-07-29 export: 63 of 85 symbols resolved 0% of
# their rows and 15 resolved 100% (resolution is a per-symbol property, not a
# per-trade one — the signature of a data fault, not of market behaviour);
# resolution decayed 25 → 20 → 3 → 1 per hour as the ledger grew; and 395 of 401
# RUNNING rows described trades that had already closed. DEXEUSDT sat RUNNING
# for 19.2h having hit its stop 1 minute after entry; EULUSDT for 12.2h, 4
# minutes after entry.
#
# The contract now: the cap still bounds the work, but what it turns away is
# counted and published, so a budget too small can no longer look like one that
# fits.


class TestRefreshBatchPlanning:
    """``plan_refresh_batch`` — the selection the loop used to inline."""

    def _ages(self, stale=()):
        """Age lookup: listed symbols are stale (due), the rest are fresh."""
        return lambda s: (None if s in stale else 0.0)

    def test_the_cap_still_bounds_the_work(self):
        syms = [f"S{i}USDT" for i in range(10)]
        due, starved = sar.plan_refresh_batch(
            syms, last_refresh_at={}, age_seconds=self._ages(set(syms)),
            now_mono=10_000.0, refresh_sec=900.0, max_per_cycle=4,
        )
        assert len(due) == 4

    def test_symbols_turned_away_by_the_cap_are_counted_not_dropped(self):
        """The regression. The old loop ``break``ed here and reported nothing,
        so a starved ledger and a healthy one produced identical telemetry."""
        syms = [f"S{i}USDT" for i in range(10)]
        due, starved = sar.plan_refresh_batch(
            syms, last_refresh_at={}, age_seconds=self._ages(set(syms)),
            now_mono=10_000.0, refresh_sec=900.0, max_per_cycle=4,
        )
        assert starved == 6
        assert len(due) + starved == 10

    def test_oldest_first_order_is_preserved_under_the_cap(self):
        """A bounded budget must go to the records closest to ageing out."""
        syms = ["OLDESTUSDT", "MIDUSDT", "NEWESTUSDT"]
        due, _ = sar.plan_refresh_batch(
            syms, last_refresh_at={}, age_seconds=self._ages(set(syms)),
            now_mono=10_000.0, refresh_sec=900.0, max_per_cycle=2,
        )
        assert due == ["OLDESTUSDT", "MIDUSDT"]

    def test_a_throttled_symbol_is_neither_served_nor_starved(self):
        """It is not waiting on budget — it was served recently. Counting it as
        starvation would page over a healthy ledger."""
        due, starved = sar.plan_refresh_batch(
            ["AAAUSDT"], last_refresh_at={"AAAUSDT": 9_900.0},
            age_seconds=self._ages({"AAAUSDT"}),
            now_mono=10_000.0, refresh_sec=900.0, max_per_cycle=1,
        )
        assert due == [] and starved == 0

    def test_a_symbol_with_fresh_candles_is_not_due(self):
        due, starved = sar.plan_refresh_batch(
            ["AAAUSDT"], last_refresh_at={}, age_seconds=lambda s: 60.0,
            now_mono=10_000.0, refresh_sec=900.0, max_per_cycle=1,
        )
        assert due == [] and starved == 0

    def test_never_stamped_is_not_evidence_of_freshness(self):
        """``age is None`` means we have never written a bar for this symbol —
        exactly the rotated-out mover the refresh exists for."""
        due, _ = sar.plan_refresh_batch(
            ["AAAUSDT"], last_refresh_at={}, age_seconds=lambda s: None,
            now_mono=10_000.0, refresh_sec=900.0, max_per_cycle=1,
        )
        assert due == ["AAAUSDT"]

    def test_the_shipped_default_covers_the_observed_ledger(self):
        """85 symbols were in the 2026-07-29 export. With a 900s throttle on a
        300s loop a cap of N sustains 3N symbols, so the default must clear 85
        with headroom or the same starvation returns."""
        from config import (
            SAR_EXIT_SHADOW_CANDLE_REFRESH_MAX_PER_CYCLE as cap,
            SAR_EXIT_SHADOW_CANDLE_REFRESH_SEC as refresh_sec,
        )
        sustained = int(cap) * (float(refresh_sec) / 300.0)
        assert sustained >= 85, (
            f"cap {cap} sustains only {sustained:.0f} symbols; the ledger "
            f"carried 85 on 2026-07-29"
        )


class TestRefreshBudgetHealth:
    @pytest.fixture(autouse=True)
    def _clean(self):
        sar.reset_refresh_budget_health()
        yield
        sar.reset_refresh_budget_health()

    def test_counters_are_published_per_cycle_not_cumulatively(self):
        """A cumulative starvation count never recovers once the ledger drains,
        so it would page forever over a fault that healed."""
        sar.record_refresh_budget(due=10, served=4, starved=6, pending=20)
        sar.roll_refresh_budget_cycle()
        assert sar.refresh_budget_health()["starved"] == 6

        sar.record_refresh_budget(due=4, served=4, starved=0, pending=4)
        sar.roll_refresh_budget_cycle()
        assert sar.refresh_budget_health()["starved"] == 0

    def test_health_reads_the_last_completed_cycle_never_one_still_filling(self):
        sar.record_refresh_budget(due=9, served=9, starved=0, pending=9)
        sar.roll_refresh_budget_cycle()
        sar.record_refresh_budget(due=3, served=1, starved=2, pending=7)
        assert sar.refresh_budget_health()["served"] == 9

    def test_pending_counts_every_symbol_owed_a_verdict(self):
        """Not just this cycle's due list — the population at risk is what a
        probe has to reason about."""
        sar.record_refresh_budget(due=4, served=4, starved=0, pending=85)
        sar.roll_refresh_budget_cycle()
        assert sar.refresh_budget_health()["pending"] == 85
