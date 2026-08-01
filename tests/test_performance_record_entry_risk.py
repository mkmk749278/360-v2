"""Closed-signal records must carry the risk the trade was actually sized for.

``SignalRecord.stop_loss`` is not that number, and had been standing in for it.
``TradeMonitor`` mutates ``sig.stop_loss`` **in place** as a trade progresses —
break-even shift, TP1 park, trail — so the value reaching the record is the stop
as of the *exit*. Ops divides by it (``R = pnl_pct / sl_distance_pct``, see
``app/routes/track_record.py``), which means a trade that was BE-shifted and then
stopped out for −0.1% scored exactly **−1.00R**: identical to a trade that gave
back its full designed risk.

Measured on the 2026-07-29→08-01 window: 9 of 28 SL_HITs were that row, and the
closed book read −0.088R where the designed denominator gives +0.160R. A sign
flip on the headline number of the page whose own docstring calls it "the number
a subscription decision would rest on".

The engine already knew the right denominator in two places —
``snapshot._original_stop_loss`` reconstructs it, and the Layer-C writer in
``trade_monitor`` divides by it — it simply never travelled onto the artifact the
owner reads. Same failure class as ``entry_regime`` (#817): a field one repo
reads and no repo writes fails silently and looks full.

``sl_distance_pct_at_entry`` is a cross-repo contract with ops. It is pinned here,
on the producing side, so renaming it fails loudly instead of quietly returning
``/track-record`` to the mutated denominator.
"""
from __future__ import annotations

from dataclasses import asdict, fields

from src.channels.base import Signal
from src.performance_tracker import (
    PerformanceTracker,
    SignalRecord,
    entry_sl_distance_pct,
)
from src.smc import Direction


def _signal(entry: float = 100.0, sl_dist: float = 3.0) -> Signal:
    """A real ``Signal``, not a stand-in.

    The whole defect lives in the difference between two fields on this
    dataclass, so a hand-written stub with keys of our choosing would assert our
    assumption back at us.
    """
    sig = Signal(
        channel="360_SCALP",
        symbol="BTCUSDT",
        direction=Direction.LONG,
        entry=entry,
        stop_loss=entry - sl_dist,
        tp1=entry + sl_dist,
        tp2=entry + sl_dist * 2,
    )
    sig.original_sl_distance = sl_dist
    return sig


def _tracker(tmp_path) -> PerformanceTracker:
    return PerformanceTracker(storage_path=str(tmp_path / "perf.json"))


def _record(tracker, **kw):
    base = dict(
        signal_id="sig-1", channel="360_SCALP", symbol="BTCUSDT",
        direction="LONG", entry=100.0, hit_tp=0, hit_sl=True, pnl_pct=-3.0,
        stop_loss=97.0,
    )
    base.update(kw)
    tracker.record_outcome(**base)
    return tracker._records[-1]


class TestTheDenominatorIsTheRiskTaken:
    def test_it_reads_the_distance_the_evaluator_stamped(self):
        assert entry_sl_distance_pct(_signal(entry=100.0, sl_dist=3.0)) == 3.0

    def test_a_moved_stop_does_not_change_it(self):
        """The regression, driven through the real mutation.

        ``trade_monitor`` shifts the stop to entry on break-even. Nothing about
        that changes what the trade was sized for, and the whole point of this
        field is that it survives the shift.
        """
        sig = _signal(entry=100.0, sl_dist=3.0)
        sig.stop_loss = sig.entry          # the BE shift, as trade_monitor does it
        assert entry_sl_distance_pct(sig) == 3.0

    def test_a_trailed_stop_does_not_change_it(self):
        sig = _signal(entry=100.0, sl_dist=3.0)
        sig.stop_loss = 101.5              # trailed into profit
        assert entry_sl_distance_pct(sig) == 3.0

    def test_an_unstamped_signal_refuses_rather_than_guessing(self):
        """0.0 means "not knowable", and readers must refuse an R.

        The tempting fallback — ``abs(entry - sig.stop_loss)`` — returns exactly
        the wrong number here, because by the time a terminal transition asks,
        the stop has already moved. Refusing is the only honest answer for a
        signal that was in flight across the deploy.
        """
        sig = _signal()
        sig.original_sl_distance = 0.0
        sig.stop_loss = sig.entry
        assert entry_sl_distance_pct(sig) == 0.0

    def test_the_break_even_stop_out_no_longer_reads_minus_one_r(self):
        """The nine rows that wrote this test.

        A BE-shifted trade stopped out for −0.1% against a designed 3% risk is a
        −0.03R scratch, not a full loss. Under the old denominator the two were
        indistinguishable, and the difference decided the sign of the book.
        """
        sig = _signal(entry=100.0, sl_dist=3.0)
        sig.stop_loss = sig.entry
        designed = entry_sl_distance_pct(sig)
        mutated = abs(sig.entry - sig.stop_loss) / sig.entry * 100.0

        pnl = -0.1
        assert pnl / designed == -0.1 / 3.0
        assert mutated == 0.0, "the mutated stop cannot even produce an R here"


class TestTheRecordCarriesIt:
    def test_it_is_stored(self, tmp_path):
        rec = _record(_tracker(tmp_path), sl_distance_pct_at_entry=3.0)
        assert rec.sl_distance_pct_at_entry == 3.0

    def test_it_survives_the_json_round_trip(self, tmp_path):
        """Ops reads the persisted file, not the live object."""
        path = tmp_path / "perf.json"
        _record(PerformanceTracker(storage_path=str(path)), sl_distance_pct_at_entry=2.5)

        reloaded = PerformanceTracker(storage_path=str(path))
        assert reloaded._records[0].sl_distance_pct_at_entry == 2.5

    def test_the_exact_key_ops_reads_is_in_the_payload(self, tmp_path):
        """Pinned name. ``app/routes/track_record.py`` keys off this string;
        renaming it here silently returns that page to the mutated stop."""
        rec = _record(_tracker(tmp_path), sl_distance_pct_at_entry=1.25)
        assert asdict(rec)["sl_distance_pct_at_entry"] == 1.25

    def test_an_old_record_reloads_as_zero_not_a_crash(self, tmp_path):
        """Every record written before this change lacks the key, and the file
        is one JSON array — a strict field would cost the entire history.

        These rows are not backfilled. The stop they carry has already been
        moved, so there is no honest reconstruction; 0.0 tells the reader to
        refuse them an R."""
        path = tmp_path / "perf.json"
        path.write_text(
            '[{"signal_id":"old","channel":"c","symbol":"BTCUSDT",'
            '"direction":"LONG","entry":1.0,"hit_tp":0,"hit_sl":true,'
            '"pnl_pct":-1.0,"confidence":70.0}]'
        )
        reloaded = PerformanceTracker(storage_path=str(path))
        assert len(reloaded._records) == 1
        assert reloaded._records[0].sl_distance_pct_at_entry == 0.0

    def test_omitting_it_is_zero(self, tmp_path):
        assert _record(_tracker(tmp_path)).sl_distance_pct_at_entry == 0.0


class TestBothTerminalPathsCanStamp:
    """Two ``record_outcome`` call sites — ``trade_monitor`` for normal terminal
    transitions, ``main`` for expiry. A field stamped by only one produces a
    population skewed by *outcome type*, which is worse than no field: every
    expired signal would be refused an R and quietly leave the book."""

    def test_the_signal_exposes_what_both_sites_read(self):
        assert "original_sl_distance" in {f.name for f in fields(Signal)}, (
            "both call sites read this off Signal via entry_sl_distance_pct; "
            "renaming it there silently zeroes every stamp"
        )

    def test_the_record_accepts_what_the_signal_provides(self):
        assert "sl_distance_pct_at_entry" in {f.name for f in fields(SignalRecord)}
