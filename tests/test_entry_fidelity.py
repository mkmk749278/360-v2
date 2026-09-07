"""Entry fidelity: the stamped entry against the price that actually existed.

``Signal.entry`` is the close of the candle the evaluator triggered on, and
every number this engine publishes about a trade divides by it. The order goes
out seconds later. Measured against Binance's own 1m tape (2026-09-07, 605 of
the 652 rows closed in the 30 days to 09-06), the market had already moved WITH
the trade by dispatch on 67% of rows, mean +0.226% — and the book's
+0.342%/trade is +0.118% when the same exits are priced from the tape. The gap
closes to two thousandths of a percent, so the drift IS the gap.

These pin the two additive halves that ship for it:

* the first-observation stamp, write-once, carrying the feed that answered and
  whether it may be frozen;
* ``peak_pnl_pct`` / ``trough_pnl_pct``, the excursions without the zero floor
  that makes MFE 0.00 mean three different things.

Nothing here is a gate and nothing changes ``entry`` or ``pnl_pct``.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src import entry_fidelity
from src.channels.base import Signal
from src.execution import mark_price_feed as _mpf
from src.smc import Direction
from src.trade_monitor import TradeMonitor

_SYMBOL = "CAPUSDT"


# ---------------------------------------------------------------------------
# Sign convention — fixed once, because a signed feature split the wrong way
# scores every SHORT backwards and reads exactly like noise.
# ---------------------------------------------------------------------------


class TestSignConvention:
    def test_long_market_above_entry_is_positive_drift(self):
        # We said "buy at 100", the tape was 101: the move we booked but never had.
        assert entry_fidelity.signed_drift_pct(100.0, 101.0, "LONG") == pytest.approx(1.0)

    def test_short_market_below_entry_is_positive_drift(self):
        # Mirror image: for a SHORT, price already lower is already in our favour.
        assert entry_fidelity.signed_drift_pct(100.0, 99.0, "SHORT") == pytest.approx(1.0)

    def test_long_market_below_entry_is_negative_drift(self):
        assert entry_fidelity.signed_drift_pct(100.0, 99.0, "LONG") == pytest.approx(-1.0)

    def test_accepts_the_direction_enum_not_only_the_string(self):
        assert entry_fidelity.signed_drift_pct(
            100.0, 101.0, Direction.LONG
        ) == pytest.approx(1.0)

    def test_unusable_price_is_none_never_zero(self):
        # Zero is a reading. This is the absence of one.
        assert entry_fidelity.signed_drift_pct(0.0, 101.0, "LONG") is None
        assert entry_fidelity.signed_drift_pct(100.0, 0.0, "LONG") is None


# ---------------------------------------------------------------------------
# Rebasing one row
# ---------------------------------------------------------------------------


class TestRebase:
    def test_exit_level_survives_rebasing_and_only_the_entry_moves(self):
        # LONG booked at 100 → −3.00%, so the exit LEVEL is 97. On the tape we
        # started at 99, so the same exit is worth −2.02%, not −3.00%.
        out = entry_fidelity.rebase(
            entry=100.0, pnl_pct=-3.0, direction="LONG", observed_entry=99.0
        )
        assert out.ok
        assert out.exit_price == pytest.approx(97.0)
        assert out.rebased_pnl_pct == pytest.approx(-2.0202, abs=1e-4)
        assert out.drift_pct == pytest.approx(-1.0)

    def test_short_rebases_the_other_way(self):
        out = entry_fidelity.rebase(
            entry=100.0, pnl_pct=-3.0, direction="SHORT", observed_entry=101.0
        )
        assert out.ok
        assert out.exit_price == pytest.approx(103.0)
        assert out.rebased_pnl_pct == pytest.approx(-1.9802, abs=1e-4)

    def test_a_favourable_drift_is_the_profit_the_book_gained_for_free(self):
        # Booked +1.00% from 100; the tape had already reached 100.5 when we
        # could act, so the real result is about half of it.
        out = entry_fidelity.rebase(
            entry=100.0, pnl_pct=1.0, direction="LONG", observed_entry=100.5
        )
        assert out.drift_pct == pytest.approx(0.5)
        assert out.rebased_pnl_pct == pytest.approx(0.4975, abs=1e-4)
        assert out.rebased_pnl_pct < out.book_pnl_pct

    @pytest.mark.parametrize(
        "kwargs,reason",
        [
            (dict(entry=0.0, observed_entry=99.0), entry_fidelity.REFUSAL_NO_ENTRY),
            (
                dict(entry=100.0, observed_entry=None),
                entry_fidelity.REFUSAL_NO_OBSERVATION,
            ),
            (
                dict(entry=100.0, observed_entry=0.0),
                entry_fidelity.REFUSAL_NO_OBSERVATION,
            ),
        ],
    )
    def test_refusals_are_named_never_pooled_into_no_data(self, kwargs, reason):
        out = entry_fidelity.rebase(pnl_pct=-3.0, direction="LONG", **kwargs)
        assert not out.ok
        assert out.refusal == reason
        # ...and a refused row hands back no numbers at all, so a caller that
        # skips the check cannot read a plausible zero.
        assert out.drift_pct is None and out.rebased_pnl_pct is None

    def test_a_frozen_mover_close_is_refused_by_default(self):
        # Rebasing onto a stale candle manufactures a drift that is a fact
        # about our feed rather than about the market.
        out = entry_fidelity.rebase(
            entry=100.0,
            pnl_pct=-3.0,
            direction="LONG",
            observed_entry=99.0,
            observation_stale=True,
        )
        assert out.refusal == entry_fidelity.REFUSAL_STALE_OBSERVATION

    def test_allow_stale_exists_to_COUNT_them_not_to_hide_them(self):
        out = entry_fidelity.rebase(
            entry=100.0,
            pnl_pct=-3.0,
            direction="LONG",
            observed_entry=99.0,
            observation_stale=True,
            allow_stale=True,
        )
        assert out.ok


# ---------------------------------------------------------------------------
# The census
# ---------------------------------------------------------------------------


class TestSummarise:
    def _row(self, **kw):
        row = dict(entry=100.0, pnl_pct=-3.0, direction="LONG", first_observed_price=99.0)
        row.update(kw)
        return row

    def test_unstamped_rows_are_refused_not_averaged_in_as_zero_drift(self):
        out = entry_fidelity.summarise(
            [self._row(), self._row(first_observed_price=0.0)]
        )
        assert out["rows"] == 2
        assert out["priced"] == 1
        assert out["coverage_pct"] == 50.0
        assert out["refusals"] == {entry_fidelity.REFUSAL_NO_OBSERVATION: 1}
        # The one priced row's drift, not an average diluted by a zero.
        assert out["drift_mean_pct"] == pytest.approx(-1.0)

    def test_an_all_unstamped_book_says_so_instead_of_reporting_zeros(self):
        out = entry_fidelity.summarise([self._row(first_observed_price=0.0)])
        assert out["priced"] == 0
        assert "note" in out
        assert "drift_mean_pct" not in out

    def test_positive_share_answers_bias_versus_noise(self):
        rows = [
            self._row(first_observed_price=101.0),
            self._row(first_observed_price=100.5),
            self._row(first_observed_price=99.0),
        ]
        out = entry_fidelity.summarise(rows)
        assert out["drift_positive_share_pct"] == pytest.approx(66.7, abs=0.1)

    def test_the_two_books_are_reported_side_by_side_never_merged(self):
        out = entry_fidelity.summarise([self._row(), self._row()])
        assert out["book_avg_pct"] == pytest.approx(-3.0)
        assert out["rebased_avg_pct"] == pytest.approx(-2.0202, abs=1e-4)
        assert "avg_pct" not in out  # no blended third number


# ---------------------------------------------------------------------------
# record_fields — driven from a real Signal, never a hand-written dict
# ---------------------------------------------------------------------------


def _signal(**kw) -> Signal:
    sig = Signal(
        channel="TEST_CHANNEL",
        symbol=_SYMBOL,
        direction=kw.pop("direction", Direction.LONG),
        entry=kw.pop("entry", 100.0),
        stop_loss=kw.pop("stop_loss", 98.0),
        tp1=102.0,
        tp2=104.0,
        confidence=75.0,
        signal_id="EF-1",
    )
    sig.status = "ACTIVE"
    for key, value in kw.items():
        setattr(sig, key, value)
    return sig


class TestRecordFields:
    def test_a_fresh_signal_reports_absence_rather_than_zero(self):
        out = entry_fidelity.record_fields(_signal())
        assert out["first_observed_price"] == 0.0
        assert out["first_observed_at"] is None
        assert out["peak_pnl_pct"] is None and out["trough_pnl_pct"] is None

    def test_it_reads_a_stamped_signal_off_the_real_dataclass(self):
        when = datetime(2026, 9, 7, 2, 26, 22, tzinfo=timezone.utc)
        sig = _signal()
        sig.first_observed_price = 99.5
        sig.first_observed_at = when
        sig.first_observed_source = "mark"
        sig.first_observed_stale = False
        sig.peak_pnl_pct = -0.4
        sig.trough_pnl_pct = -3.2
        out = entry_fidelity.record_fields(sig)
        assert out["first_observed_price"] == pytest.approx(99.5)
        assert out["first_observed_at"] == pytest.approx(when.timestamp())
        assert out["first_observed_source"] == "mark"
        assert out["peak_pnl_pct"] == pytest.approx(-0.4)

    def test_every_key_is_one_the_record_actually_accepts(self):
        # A producer whose keys the consumer does not have is #817 with the
        # arrow reversed, so the contract is checked against the real record.
        from src.performance_tracker import SignalRecord

        assert set(entry_fidelity.record_fields(_signal())) <= set(
            SignalRecord.__dataclass_fields__
        )


# ---------------------------------------------------------------------------
# Both terminal writers, pinned on the AST — a field carried by one and not the
# other is populated on some rows and absent on others, which reads as missing
# data rather than as a missing writer.
# ---------------------------------------------------------------------------


def _perf_record_calls(path: Path) -> list:
    """Every ``_performance_tracker.record_outcome(...)`` call, and whether it
    splats ``record_fields``.

    Qualified on the receiver on purpose: ``_circuit_breaker.record_outcome``
    is a different object with the same method name, and a pin that matched on
    the method alone would go green on the wrong call. (The first cut of this
    pin matched the wrong name entirely and failed — which is what a pin is
    for; verify it by reverting it.)
    """
    tree = ast.parse(path.read_text())
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if getattr(func, "attr", None) != "record_outcome":
            continue
        receiver = getattr(func, "value", None)
        if getattr(receiver, "attr", None) != "_performance_tracker":
            continue
        found.append(
            any(
                kw.arg is None
                and isinstance(kw.value, ast.Call)
                and getattr(kw.value.func, "attr", None) == "record_fields"
                for kw in node.keywords
            )
        )
    return found


@pytest.mark.parametrize("module", ["src/trade_monitor.py", "src/main.py"])
def test_both_terminal_writers_splat_record_fields(module):
    calls = _perf_record_calls(Path(module))
    assert calls, f"{module} no longer writes the closed-signal record at all"
    assert all(calls), (
        f"{module} writes the closed-signal record without "
        "entry_fidelity.record_fields — the stamp would be present on rows "
        "closed by one path and silently absent on the other."
    )


# ---------------------------------------------------------------------------
# The stamp itself, driven through the real monitor
# ---------------------------------------------------------------------------


@pytest.fixture
def mark_feed():
    prev = _mpf.get_instance()
    feed = MagicMock()
    feed.get_price.side_effect = lambda s: 99.0 if s == _SYMBOL else None
    _mpf.set_instance(feed)
    try:
        yield feed
    finally:
        _mpf.set_instance(prev)  # type: ignore[arg-type]


def _monitor(age_seconds, close=100.0, signals=None):
    data_store = MagicMock()
    data_store.get_candles.return_value = {
        "high": [close], "low": [close], "close": [close],
        "open": [close], "volume": [1000.0],
    }
    data_store.last_kline_age_seconds.return_value = age_seconds
    data_store.ticks = {}
    return TradeMonitor(
        data_store=data_store,
        send_telegram=MagicMock(),
        get_active_signals=lambda: (signals or {}),
        remove_signal=MagicMock(),
        update_signal=MagicMock(),
    )


class TestPriceSource:
    def test_the_price_only_view_is_unchanged_by_the_split(self, mark_feed):
        # The refactor must not move a number: a fresh candle still answers.
        monitor = _monitor(age_seconds=5.0)
        assert monitor._latest_price(_SYMBOL) == pytest.approx(100.0)
        price, source, stale = monitor._latest_price_with_source(_SYMBOL)
        assert (price, source, stale) == (pytest.approx(100.0), "candle", False)

    def test_the_divert_reports_the_mark_and_calls_it_FRESH(self, mark_feed):
        # The flag describes the PRICE, not the store. Calling a diverted mark
        # stale would refuse exactly the rows the divert exists to rescue.
        monitor = _monitor(age_seconds=10800.0)
        price, source, stale = monitor._latest_price_with_source(_SYMBOL)
        assert (price, source, stale) == (pytest.approx(99.0), "mark", False)

    def test_a_stale_candle_with_no_mark_is_served_but_MARKED(self):
        prev = _mpf.get_instance()
        feed = MagicMock()
        feed.get_price.return_value = None
        _mpf.set_instance(feed)
        try:
            monitor = _monitor(age_seconds=10800.0)
            price, source, stale = monitor._latest_price_with_source(_SYMBOL)
            assert (price, source, stale) == (pytest.approx(100.0), "candle", True)
        finally:
            _mpf.set_instance(prev)  # type: ignore[arg-type]


class TestFirstObservationStamp:
    def test_it_is_write_once_because_it_is_knowable_once(self, mark_feed):
        monitor = _monitor(age_seconds=5.0)
        sig = _signal()
        monitor._stamp_first_observation(sig, 99.5, "candle", False)
        monitor._stamp_first_observation(sig, 42.0, "mark", True)
        assert sig.first_observed_price == pytest.approx(99.5)
        assert sig.first_observed_source == "candle"
        assert sig.first_observed_stale is False

    def test_an_unusable_price_leaves_the_row_unstamped(self, mark_feed):
        monitor = _monitor(age_seconds=5.0)
        sig = _signal()
        monitor._stamp_first_observation(sig, 0.0, "none", False)
        assert sig.first_observed_price == 0.0
        assert sig.first_observed_at is None

    async def test_the_monitor_stamps_the_tape_price_not_the_evaluator_entry(
        self, mark_feed
    ):
        # The signal says "buy at 100". The store's candle says 101.5 — price
        # has already run 1.5% before we could act, and THAT is what the trade
        # started from. This is the whole defect, in one assertion.
        sig = _signal()
        sig.timestamp = datetime.now(timezone.utc) - timedelta(seconds=1)
        monitor = _monitor(age_seconds=5.0, close=101.5, signals={"EF-1": sig})
        await monitor._check_all()
        assert sig.first_observed_price == pytest.approx(101.5)
        assert sig.first_observed_source == "candle"
        assert entry_fidelity.signed_drift_pct(
            sig.entry, sig.first_observed_price, sig.direction
        ) == pytest.approx(1.5)
        # ...and `entry` is untouched: nothing downstream is re-based by this.
        assert sig.entry == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# The zero floor. This is the assertion that fails against the pre-fix tree.
# ---------------------------------------------------------------------------


class TestUnclampedExcursions:
    async def _run(self, price):
        sig = _signal()
        sig.timestamp = datetime.now(timezone.utc) - timedelta(seconds=600)
        sig.current_price = price
        monitor = _monitor(age_seconds=5.0, close=price, signals={"EF-1": sig})
        await monitor._evaluate_signal(sig)
        return sig

    async def test_a_trade_that_never_went_positive_records_a_NEGATIVE_peak(self):
        # −0.5% and never better. MFE says +0.00% — the floor — while the
        # unclamped peak says what actually happened.
        sig = await self._run(99.5)
        assert sig.max_favorable_excursion_pct == 0.0      # unchanged, by design
        assert sig.peak_pnl_pct == pytest.approx(-0.5)     # the fix
        assert sig.trough_pnl_pct == pytest.approx(-0.5)

    async def test_the_clamped_pair_keeps_its_exact_meaning(self):
        # Additive: a trade that DID run favourably reads the same in both.
        sig = await self._run(100.8)
        assert sig.max_favorable_excursion_pct == pytest.approx(0.8)
        assert sig.peak_pnl_pct == pytest.approx(0.8)
        # ...and MAE is still floored at zero while the trough is not.
        assert sig.max_adverse_excursion_pct == 0.0
        assert sig.trough_pnl_pct == pytest.approx(0.8)

    async def test_never_evaluated_is_a_third_state_the_clamped_pair_cannot_show(self):
        sig = _signal()
        assert sig.max_favorable_excursion_pct == 0.0
        assert sig.peak_pnl_pct is None
