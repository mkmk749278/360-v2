"""The SAR shadow arm must replay the bar the trade actually started on.

Regression cover for the 2026-07-26 defect. ``fetch_ohlc_15m_since`` used to
locate the entry bar arithmetically — ``n_post = elapsed // bar_seconds``,
counted back from the end of the array — which assumes the candle array is
gap-free and its last bar is current. Neither holds on a feed that drops frames
or freezes, and the clamps (``min``/``max(0, …)``) hid the breakage instead of
surfacing it, so the walk replayed an unrelated bar and still returned a
verdict.

The owner's ops export is what these tests encode: exit price came out a pure
function of (symbol, side) — TRUMPUSDT signals stamped three hours apart all
"exited" at 1.598 — 41% of supposed one-bar moves exceeded 5%, and the arm read
−4.4R across 172 fabricated rows.

The contract now: find the bar by ``open_time``, or return None. A record that
cannot be honestly replayed produces no verdict.
"""
from __future__ import annotations

import time

import numpy as np
import pytest

from src.sar_exit_shadow import simulate_sar_exit

BAR_MS = 15 * 60 * 1000.0


def _series(n: int, *, last_open_ms: float, gap_at: int | None = None):
    """n contiguous 15m bars ending at ``last_open_ms`` (optionally with a gap)."""
    ot = np.array([last_open_ms - (n - 1 - i) * BAR_MS for i in range(n)], dtype=np.float64)
    if gap_at is not None:
        ot[gap_at:] += BAR_MS * 5  # five missing bars
    price = np.array([100.0 + i * 0.1 for i in range(n)], dtype=np.float64)
    return {
        "open": price.copy(),
        "high": price + 0.5,
        "low": price - 0.5,
        "close": price.copy(),
        "open_time": ot,
    }


# ``fetch_ohlc_15m_since`` is a closure inside the engine's audit loop and is
# not importable on its own, so these pin the invariants it must satisfy —
# every guard below maps one-to-one onto a return-None branch in that closure.


class TestEntryBarContract:
    def test_entry_index_points_at_the_bar_containing_the_stamp(self):
        now_ms = time.time() * 1000.0
        n = 100
        b = _series(n, last_open_ms=now_ms - BAR_MS)
        stamp_ms = float(b["open_time"][60]) + 1000.0  # 1s into bar 60
        idx = int(np.searchsorted(b["open_time"], stamp_ms, side="right")) - 1
        assert idx == 60
        # The stamp must fall inside that bar, not merely after it.
        assert 0.0 <= stamp_ms - float(b["open_time"][idx]) < BAR_MS

    def test_stale_feed_does_not_resolve_to_a_recent_bar(self):
        """The bug: a frozen feed made every record land on the same bar.

        With the array's last bar 6 hours old, a signal stamped *now* has no
        bar covering it — the honest answer is None, not the newest bar.
        """
        now_ms = time.time() * 1000.0
        b = _series(100, last_open_ms=now_ms - 6 * 3600 * 1000.0)
        stamp_ms = now_ms
        idx = int(np.searchsorted(b["open_time"], stamp_ms, side="right")) - 1
        assert idx == len(b["open_time"]) - 1
        # …but the stamp is NOT inside that bar, which is what the guard checks.
        assert not (0.0 <= stamp_ms - float(b["open_time"][idx]) < BAR_MS)

    def test_two_stamps_hours_apart_get_different_entry_bars(self):
        """TRUMPUSDT: 09:55 and 13:01 must not resolve to the same bar."""
        now_ms = time.time() * 1000.0
        b = _series(200, last_open_ms=now_ms)
        early = float(b["open_time"][100]) + 1.0
        late = early + 3 * 3600 * 1000.0
        i_early = int(np.searchsorted(b["open_time"], early, side="right")) - 1
        i_late = int(np.searchsorted(b["open_time"], late, side="right")) - 1
        assert i_early != i_late
        assert i_late - i_early == 12  # 3h of 15m bars

    def test_gap_in_the_window_is_detectable(self):
        b = _series(100, last_open_ms=time.time() * 1000.0, gap_at=70)
        ot = b["open_time"][50:100]
        assert not np.all(np.abs(np.diff(ot) - BAR_MS) < 1.0)

    def test_nan_timestamps_are_detectable(self):
        b = _series(100, last_open_ms=time.time() * 1000.0)
        b["open_time"][55] = np.nan
        assert not np.all(np.isfinite(b["open_time"][50:100]))


class TestAlignmentIsRecorded:
    """Counter-SAR entries must be identifiable, not silently pooled.

    The authoritative verdict moved to STAMP time on 2026-07-27 (it needs no
    future candle, and deferring it left 94% of the ledger unlabelled for up to
    48h). What the resolver returns is now ``sar_aligned_at_resolve`` — the
    cross-check, read at the last bar CLOSED at entry so it measures the same
    bar the scanner did. These cases still pin the direction convention: a
    bearish SAR sits above price, so it opposes a LONG and agrees with a SHORT.
    """

    @staticmethod
    def _downtrend(n=80):
        highs, lows, closes, opens = [], [], [], []
        p = 100.0
        for _ in range(n):
            opens.append(p)
            highs.append(p + 0.2)
            lows.append(p - 1.2)
            p -= 1.0
            closes.append(p)
        return highs, lows, closes, opens

    def test_long_into_a_bearish_sar_is_flagged_opposed(self):
        h, l, c, o = self._downtrend()
        entry = c[59]
        r = simulate_sar_exit(
            highs=h, lows=l, closes=c, opens=o, entry_idx=60, entry=entry,
            side="LONG", step=0.02, max_step=0.2, max_bars=192, bar_minutes=15.0,
            # Under conditional handover an opposed entry runs on its LIVE
            # geometry, so the replay needs that geometry to exist.
            stop_loss=entry * 0.98, tp1=entry * 1.02,
        )
        assert r is not None
        assert r["sar_aligned_at_resolve"] is False

    def test_opposed_entry_without_geometry_refuses_rather_than_guessing(self):
        """An opposed entry starts on its live SL/TP1. Without them there is no
        defined behaviour to replay, and a clamp is not a guard."""
        h, l, c, o = self._downtrend()
        assert simulate_sar_exit(
            highs=h, lows=l, closes=c, opens=o, entry_idx=60, entry=c[59],
            side="LONG", step=0.02, max_step=0.2, max_bars=192, bar_minutes=15.0,
        ) is None

    def test_short_with_a_bearish_sar_is_flagged_aligned(self):
        h, l, c, o = self._downtrend()
        r = simulate_sar_exit(
            highs=h, lows=l, closes=c, opens=o, entry_idx=60, entry=c[59],
            side="SHORT", step=0.02, max_step=0.2, max_bars=192, bar_minutes=15.0,
        )
        assert r is not None
        assert r["sar_aligned_at_resolve"] is True

    def test_opposed_entries_run_on_live_geometry_not_the_trail(self):
        """Premise replaced, 2026-07-27 (owner design).

        This case used to pin the opposite behaviour — an opposed entry stopped
        out on the first testable bar, because the trail was applied from bar
        zero even though its level sat on the wrong side of price. Measured on
        the real feed that made 84% of the opposed cohort a one-bar exit at the
        next bar's open: a ~7-minute drift measurement wearing an exit method's
        name. Under conditional handover the trade runs on the geometry it was
        given, so the trail must NOT be what closes it here.
        """
        h, l, c, o = self._downtrend()
        entry = c[59]
        r = simulate_sar_exit(
            highs=h, lows=l, closes=c, opens=o, entry_idx=60, entry=entry,
            side="LONG", step=0.02, max_step=0.2, max_bars=192, bar_minutes=15.0,
            # A stop wide enough to survive several bars of this -1%/bar
            # fixture: the point is that the trade is NOT closed on bar one.
            stop_loss=entry * 0.90, tp1=entry * 1.20,
        )
        assert r is not None
        assert r["exit_reason"] == "static_sl", "the live stop must own this exit"
        assert r["hold_min"] > 15.0, "no longer stopped on the first testable bar"
        assert r["handover_bars"] is None, "SAR never came onside in a downtrend"


class TestAlignmentRollup:
    def test_split_keeps_the_two_populations_apart(self):
        from src.sar_exit_shadow import SAREXIT_SUFFIX, summarize_sar_alignment

        recs = [
            {"setup_class": f"MTP{SAREXIT_SUFFIX}", "classification": "would_win",
             "sar_aligned_at_entry": True, "r_multiple": 1.5, "trail_hold_min": 120.0},
            {"setup_class": f"MTP{SAREXIT_SUFFIX}", "classification": "would_win",
             "sar_aligned_at_entry": True, "r_multiple": 0.5, "trail_hold_min": 90.0},
            {"setup_class": f"MTP{SAREXIT_SUFFIX}", "classification": "would_lose",
             "sar_aligned_at_entry": False, "r_multiple": -0.25, "trail_hold_min": 15.0},
        ]
        out = summarize_sar_alignment(recs)
        assert out["aligned"]["n"] == 2
        assert out["aligned"]["avg_r"] == pytest.approx(1.0)
        assert out["opposed"]["n"] == 1
        assert out["opposed"]["avg_r"] == pytest.approx(-0.25)
        assert out["opposed_share"] == pytest.approx(1 / 3)
        # The pooled number the panel used to show would have been +0.583 —
        # a blend that moves with the alignment mix, not with the exit.

    def test_pre_fix_rows_without_the_flag_are_excluded(self):
        from src.sar_exit_shadow import SAREXIT_SUFFIX, summarize_sar_alignment

        out = summarize_sar_alignment(
            [{"setup_class": f"MTP{SAREXIT_SUFFIX}", "classification": "would_win",
              "r_multiple": 9.0}]
        )
        assert out["total"] == 0

    def test_base_arm_rows_are_not_counted(self):
        from src.sar_exit_shadow import SARBASE_SUFFIX, summarize_sar_alignment

        out = summarize_sar_alignment(
            [{"setup_class": f"MTP{SARBASE_SUFFIX}", "classification": "would_win",
              "sar_aligned_at_entry": True, "r_multiple": 1.0}]
        )
        assert out["total"] == 0


class TestLedgerClear:
    def test_clear_empties_the_buffer_but_keeps_the_liveness_counter(self, tmp_path):
        from src.suppression_audit import SuppressedCandidateStore, stamp_candidate

        store = SuppressedCandidateStore(persist_path=str(tmp_path / "l.json"))
        for _ in range(3):
            stamp_candidate(
                gate_name="g", symbol="BTCUSDT", channel="scalp", setup_class="MTP",
                side="LONG", entry=100.0, stop_loss=99.0, tp1=102.0, store=store,
            )
        assert len(store.records()) == 3
        assert store.clear() == 3
        assert store.records() == []
        # Liveness probes read stamped_total for a monotonic heartbeat; resetting
        # it would page as a dead feature.
        assert store.stamped_total == 3
