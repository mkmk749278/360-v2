"""Tests for the honest multi-metric ``/stats`` formatter.

``performance_tracker_honest`` exists because the legacy win-rate
formula counted PROFIT_LOCKED (capital preserved) as a *loss* — a
subscriber-facing lie.  Until now the module was only ever mocked out in
``test_commands.py``, so the bucket attribution itself was untested.
Given the hard limit "never fabricate signal performance numbers", the
aggregation math gets pinned directly here:

* bucket attribution: TP outcomes → decisive wins, PROFIT_LOCKED /
  BREAKEVEN_EXIT → pre-TP grabs (NOT losses), SL_HIT → clean SL,
  everything else → other;
* capital_preserved_pct = 1 - clean_sl/total (the number the legacy
  formula understated);
* percentages / averages, zero-division safety on an empty tracker;
* the fallback classify() path for legacy rows whose ``outcome_label``
  pre-dates the field;
* channel + window filters stay consistent with the legacy formatter
  (both go through the same ``_filter``);
* the Telegram formatter renders every bucket and the empty-state line.

Uses a real ``PerformanceTracker`` against a tmp-path JSON file — no
mocks of the module under test.
"""

from __future__ import annotations

import time

from src.performance_tracker import PerformanceTracker, SignalRecord
from src.performance_tracker_honest import (
    format_honest_stats_message,
    get_honest_outcome_breakdown,
)


def _tracker(tmp_path) -> PerformanceTracker:
    return PerformanceTracker(storage_path=str(tmp_path / "perf.json"))


def _record(
    tracker: PerformanceTracker,
    outcome_label: str,
    *,
    pnl_pct: float = 1.0,
    hit_tp: int = 0,
    hit_sl: bool = False,
    channel: str = "scalp",
) -> None:
    tracker.record_outcome(
        signal_id=f"sig-{len(tracker._records)}",
        channel=channel,
        symbol="BTCUSDT",
        direction="LONG",
        entry=100.0,
        hit_tp=hit_tp,
        hit_sl=hit_sl,
        pnl_pct=pnl_pct,
        outcome_label=outcome_label,
    )


class TestBucketAttribution:
    def test_tp_outcomes_are_decisive_wins(self, tmp_path):
        tracker = _tracker(tmp_path)
        for label in ("TP1_HIT", "TP2_HIT", "TP3_HIT", "FULL_TP_HIT"):
            _record(tracker, label, hit_tp=1, pnl_pct=2.0)
        b = get_honest_outcome_breakdown(tracker)
        assert b["decisive_wins"] == 4
        assert b["pre_tp_grabs"] == 0
        assert b["clean_sl_hits"] == 0
        assert b["decisive_win_pct"] == 100.0

    def test_profit_locked_is_capital_preserved_not_a_loss(self, tmp_path):
        # THE motivating case: the legacy formula counted PROFIT_LOCKED as
        # a loss.  The honest breakdown must attribute it to the pre-TP
        # grab bucket and keep it out of clean_sl.
        tracker = _tracker(tmp_path)
        _record(tracker, "PROFIT_LOCKED", pnl_pct=0.3)
        _record(tracker, "BREAKEVEN_EXIT", pnl_pct=0.0)
        b = get_honest_outcome_breakdown(tracker)
        assert b["pre_tp_grabs"] == 2
        assert b["clean_sl_hits"] == 0
        assert b["capital_preserved_pct"] == 100.0

    def test_sl_hit_is_the_only_capital_loss_bucket(self, tmp_path):
        tracker = _tracker(tmp_path)
        _record(tracker, "SL_HIT", hit_sl=True, pnl_pct=-2.0)
        _record(tracker, "TP1_HIT", hit_tp=1, pnl_pct=2.0)
        _record(tracker, "PROFIT_LOCKED", pnl_pct=0.4)
        _record(tracker, "PROFIT_LOCKED", pnl_pct=0.2)
        b = get_honest_outcome_breakdown(tracker)
        assert b["total"] == 4
        assert b["clean_sl_hits"] == 1
        assert b["clean_sl_pct"] == 25.0
        # 1 - 1/4 → 75% of signals preserved capital.
        assert b["capital_preserved_pct"] == 75.0

    def test_closed_and_expired_fall_into_other(self, tmp_path):
        tracker = _tracker(tmp_path)
        _record(tracker, "CLOSED", pnl_pct=0.1)
        _record(tracker, "EXPIRED_NO_FILL", pnl_pct=0.0)
        b = get_honest_outcome_breakdown(tracker)
        assert b["other"] == 2
        assert b["decisive_wins"] == 0
        assert b["pre_tp_grabs"] == 0

    def test_avg_pnl_is_mean_over_all_records(self, tmp_path):
        tracker = _tracker(tmp_path)
        _record(tracker, "TP1_HIT", hit_tp=1, pnl_pct=3.0)
        _record(tracker, "SL_HIT", hit_sl=True, pnl_pct=-1.0)
        b = get_honest_outcome_breakdown(tracker)
        assert b["avg_pnl_pct"] == 1.0


class TestEmptyAndFallback:
    def test_empty_tracker_is_all_zeros_no_division_error(self, tmp_path):
        b = get_honest_outcome_breakdown(_tracker(tmp_path))
        assert b["total"] == 0
        assert b["decisive_win_pct"] == 0.0
        assert b["capital_preserved_pct"] == 0.0
        assert b["avg_pnl_pct"] == 0.0

    def test_legacy_row_without_outcome_label_is_classified_fresh(
        self, tmp_path
    ):
        # Rows persisted before the outcome_label field shipped have "" —
        # the breakdown must re-classify from the mechanical flags instead
        # of dumping them all into "other".
        tracker = _tracker(tmp_path)
        tracker._records.append(
            SignalRecord(
                signal_id="legacy",
                channel="scalp",
                symbol="ETHUSDT",
                direction="SHORT",
                entry=2000.0,
                hit_tp=0,
                hit_sl=True,
                pnl_pct=-1.5,
                confidence=70.0,
                outcome_label="",
            )
        )
        b = get_honest_outcome_breakdown(tracker)
        assert b["clean_sl_hits"] == 1
        assert b["other"] == 0


class TestFilters:
    def test_channel_filter(self, tmp_path):
        tracker = _tracker(tmp_path)
        _record(tracker, "TP1_HIT", hit_tp=1, channel="scalp")
        _record(tracker, "SL_HIT", hit_sl=True, pnl_pct=-1.0, channel="swing")
        b = get_honest_outcome_breakdown(tracker, channel="scalp")
        assert b["total"] == 1
        assert b["decisive_wins"] == 1

    def test_window_filter_drops_old_records(self, tmp_path):
        tracker = _tracker(tmp_path)
        _record(tracker, "TP1_HIT", hit_tp=1)
        _record(tracker, "SL_HIT", hit_sl=True, pnl_pct=-1.0)
        # Age the SL record out of a 7-day window.
        tracker._records[-1].timestamp = time.time() - 8 * 86_400.0
        b = get_honest_outcome_breakdown(tracker, window_days=7)
        assert b["total"] == 1
        assert b["clean_sl_hits"] == 0


class TestFormatter:
    def test_empty_state_message(self, tmp_path):
        msg = format_honest_stats_message(_tracker(tmp_path))
        assert "No completed signals yet." in msg
        assert "All Channels" in msg
        assert "(all time)" in msg

    def test_renders_every_bucket_and_signed_avg(self, tmp_path):
        tracker = _tracker(tmp_path)
        _record(tracker, "TP1_HIT", hit_tp=1, pnl_pct=2.0)
        _record(tracker, "PROFIT_LOCKED", pnl_pct=0.5)
        _record(tracker, "SL_HIT", hit_sl=True, pnl_pct=-2.0)
        msg = format_honest_stats_message(tracker)
        assert "Total signals: 3" in msg
        assert "Decisive wins (TP): 1" in msg
        assert "Pre-TP grabs (BE):  1" in msg
        assert "Clean SL hits:      1" in msg
        assert "Capital preserved:" in msg
        # Signed average: +0.17% for (2.0 + 0.5 - 2.0) / 3.
        assert "Avg PnL: +0.17%" in msg

    def test_channel_and_window_labels(self, tmp_path):
        tracker = _tracker(tmp_path)
        _record(tracker, "TP1_HIT", hit_tp=1, channel="scalp")
        msg = format_honest_stats_message(tracker, channel="scalp", window_days=7)
        assert "scalp" in msg
        assert "(last 7d)" in msg
