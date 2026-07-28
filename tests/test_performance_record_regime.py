"""Closed-signal records must carry the regime they were entered in.

The ops ``/performance`` page has read ``entry_regime`` off these records since
it was written (``app/routes/performance.py``: ``r.get("entry_regime") or
r.get("regime", "UNKNOWN")``), and the engine never wrote either field — so its
per-regime table silently bucketed **every** closed signal into UNKNOWN. Not a
crash, not an empty table: a full-looking table describing nothing, which is the
failure class this repo keeps paying for.

It also blocks the track-record work: a regime filter over closed signals needs
the regime on the record, and it is one of the few facts that genuinely cannot
be recovered later. The 5m/15m regime at entry exists only at entry. Records
already on disk keep reading UNKNOWN rather than being backfilled with a guess.

Both labels travel. ``entry_regime`` is the 5m read; ``entry_regime_15m`` is the
HTF label the exit-runner gate uses. A setup whose HTF context disagrees with
its LTF one is a different trade, and collapsing them to one label would make
that undetectable.
"""
from __future__ import annotations

from dataclasses import asdict, fields

from src.performance_tracker import PerformanceTracker, SignalRecord


def _tracker(tmp_path) -> PerformanceTracker:
    return PerformanceTracker(storage_path=str(tmp_path / "perf.json"))


def _record(tracker, **kw):
    base = dict(
        signal_id="sig-1", channel="360_SCALP", symbol="BTCUSDT",
        direction="LONG", entry=100.0, hit_tp=1, hit_sl=False, pnl_pct=1.5,
        stop_loss=99.0,
    )
    base.update(kw)
    tracker.record_outcome(**base)
    return tracker._records[-1]


class TestTheRecordCarriesRegime:
    def test_both_labels_are_stored(self, tmp_path):
        rec = _record(
            _tracker(tmp_path),
            entry_regime="TRENDING_UP", entry_regime_15m="RANGING",
        )
        assert rec.entry_regime == "TRENDING_UP"
        assert rec.entry_regime_15m == "RANGING"

    def test_they_survive_the_json_round_trip(self, tmp_path):
        """Ops reads the persisted file, not the live object — a field that
        exists in memory and vanishes on disk fixes nothing."""
        path = tmp_path / "perf.json"
        tracker = PerformanceTracker(storage_path=str(path))
        _record(tracker, entry_regime="VOLATILE", entry_regime_15m="TRENDING_DOWN")

        reloaded = PerformanceTracker(storage_path=str(path))
        assert len(reloaded._records) == 1
        assert reloaded._records[0].entry_regime == "VOLATILE"
        assert reloaded._records[0].entry_regime_15m == "TRENDING_DOWN"

    def test_the_key_ops_reads_is_present_in_the_payload(self, tmp_path):
        """The exact key name, pinned. ``entry_regime`` is a cross-repo contract
        with ``app/routes/performance.py``; renaming it here silently returns
        that page to bucketing everything as UNKNOWN."""
        rec = _record(_tracker(tmp_path), entry_regime="QUIET")
        assert asdict(rec)["entry_regime"] == "QUIET"

    def test_an_old_record_reloads_without_the_fields(self, tmp_path):
        """Every record written before this change lacks both keys. They must
        default rather than crash the load — the whole file is one JSON array,
        so one strict field would cost the entire history.

        (``confidence`` is present because it has no default and every record
        ever written carries it — the fixture mirrors a real legacy row, not a
        minimal one.)"""
        path = tmp_path / "perf.json"
        path.write_text(
            '[{"signal_id":"old","channel":"c","symbol":"BTCUSDT",'
            '"direction":"LONG","entry":1.0,"hit_tp":0,"hit_sl":true,'
            '"pnl_pct":-1.0,"confidence":70.0}]'
        )
        reloaded = PerformanceTracker(storage_path=str(path))
        assert len(reloaded._records) == 1
        assert reloaded._records[0].entry_regime == ""

    def test_omitting_them_is_empty_string_not_none(self, tmp_path):
        """``UNKNOWN`` is ops' display fallback; the record's own absent value
        is ``""``. Storing None would put a null in the JSON that every reader
        then has to special-case."""
        rec = _record(_tracker(tmp_path))
        assert rec.entry_regime == "" and rec.entry_regime_15m == ""

    def test_none_is_coerced_not_propagated(self, tmp_path):
        rec = _record(_tracker(tmp_path), entry_regime=None, entry_regime_15m=None)
        assert rec.entry_regime == "" and rec.entry_regime_15m == ""


class TestBothTerminalPathsStamp:
    """There are two ``record_outcome`` call sites — ``trade_monitor`` for the
    normal terminal transitions and ``main`` for expiry. A field stamped by only
    one of them produces a population skewed by *outcome type*, which is worse
    than no field at all: expired signals would all read UNKNOWN and quietly
    concentrate in one bucket."""

    def test_the_signal_dataclass_exposes_what_both_sites_read(self):
        from src.channels.base import Signal

        names = {f.name for f in fields(Signal)}
        assert {"entry_regime", "entry_regime_15m"} <= names, (
            "the call sites read these off Signal; if they are renamed there, "
            "both stamps silently become empty strings"
        )

    def test_the_record_accepts_what_the_signal_provides(self):
        record_names = {f.name for f in fields(SignalRecord)}
        assert {"entry_regime", "entry_regime_15m"} <= record_names
