"""Three MVRTP findings, made measurable — the clock, the mover's own timeframe,
and the stop that actually shipped.

Measured 2026-08-04 on the last 100 delivered signals (91 of them
``MOVER_TREND_PULLBACK``, so this path *is* the book) plus the same day's
dispatch log and the 15k-row edge matrix:

* **The clock.** Entries in Asia / off-hours / any weekend: 50 trades, 18.0%
  win, −59.14%. Weekday London/Overlap/NY: 41 trades, 48.8% win, +49.58%.
  Permutation p=0.0013, and it replicates on the edge matrix, where Asia and
  off-hours are the only negative sessions. The engine has scored this all
  along — ``classify_session`` returns a quality in [0,1] and stores it on every
  signal as ``mc_session_quality`` — and **no emission decision has ever read
  it**.
* **The mover's own timeframe.** The mover gate clears on
  ``max(15m MA7<->MA99, 1H EMA21/50 fan)``, so the 1H term can carry a candidate
  whose 15m stack is flat. Nothing recorded which term did the carrying.
* **The stop that shipped.** 46 of 46 dispatched MVRTP signals had a stop
  *tighter* than the geometry their TP ladder was built from — structural 4.13%
  median against 3.09% shipped, ratio 1.21–1.37 — because
  ``predictive_ai.adjust_tp_sl`` rescales the SL distance and the two mover
  paths are absent from ``_PREDICTIVE_SLTP_BYPASS_SETUPS``. It took a
  dispatch-log diff to notice, because the closed record kept only the
  structural figure, under a name that reads like the shipped one.

What is pinned here is the **separation**, not a verdict:

1. Both new rules ship SHADOW. Neither is a repair of a filter the engine
   already applies — the session rule is a discovery that would move roughly
   half the delivered book — so measurement runs and enforcement waits for a
   flip. A test guards the default, because it is the doctrine and not a
   preference.
2. Thresholds come from numbers that already exist (``classify_session``'s
   scale, ``MOVER_TP_MIN_STACK_SEP_PCT``), never from the window above.
3. The designed and shipped stops are two different measurements, published
   side by side, with "unknown" kept apart from "no override".
"""
from __future__ import annotations

import datetime as dt

from config import MOVER_TP_MIN_STACK_SEP_PCT
from src import entry_features as ef
from src import entry_quality as eq
from src.channels.base import Signal
from src.performance_tracker import (
    PerformanceTracker,
    SignalRecord,
    entry_sl_distance_pct,
    shipped_sl_distance_pct,
)
from src.runtime_truth_report import build_geometry_override
from src.smc import Direction


def _ts(iso: str) -> float:
    return dt.datetime.fromisoformat(iso).replace(tzinfo=dt.timezone.utc).timestamp()


def _tf(n: int = 30) -> dict:
    return {
        "close": [10.0] * n,
        "high": [10.2] * n,
        "low": [9.8] * n,
        "volume": [100.0] * n,
    }


def _capture(iso: str, **over) -> dict:
    kwargs = dict(
        symbol="BTWUSDT",
        direction_is_long=True,
        entry=10.0,
        sl_dist=0.3,
        tp1=10.3,
        trigger="fast_pullback",
        tf=_tf(),
        tf_name="15m",
        atr=0.1,
        smc_data={},
        now_ts=_ts(iso),
    )
    kwargs.update(over)
    return ef.capture(**kwargs)


# --------------------------------------------------------------------------- #
# The clock — stamped where it becomes true, on the same clock as `stamped_at`
# --------------------------------------------------------------------------- #


class TestSessionStamp:
    def test_session_quality_is_a_declared_core_feature(self):
        """Every entry happens at a time, so every path declares it.

        Declared rather than merely present: the missing-accounting and the ops
        now-vs-later split both read ``features_for``, and a value that is
        stamped but undeclared is exactly what let ``stack_sep_pct`` sit
        unwatchable on the one path that reads it.
        """
        assert "session_quality" in ef.CORE_FEATURES
        for path in ("MOVER_TREND_PULLBACK", "TREND_PULLBACK_EMA", "MOVER_AVWAP_SCALP"):
            assert "session_quality" in ef.features_for(path)

    def test_the_engines_own_scale_is_what_gets_stamped(self):
        """Not a re-derivation — ``classify_session``'s published numbers."""
        assert _capture("2026-08-04T13:00")["session_quality"] == 1.00   # OVERLAP
        assert _capture("2026-08-04T18:00")["session_quality"] == 0.85   # NY
        assert _capture("2026-08-04T09:00")["session_quality"] == 0.80   # LONDON
        assert _capture("2026-08-04T03:00")["session_quality"] == 0.45   # ASIA
        assert _capture("2026-08-04T23:00")["session_quality"] == 0.30   # OFF_HOURS

    def test_the_weekend_multiplier_reaches_the_stamp(self):
        """A Saturday NY entry is not an NY entry. 25 weekend trades ran
        −27.54% in the measured window, and the engine's own x0.6 already says
        so — this pins that the multiplier survives to the row."""
        weekday = _capture("2026-08-04T18:00")   # Tuesday
        weekend = _capture("2026-08-01T18:00")   # Saturday
        assert weekday["session"] == weekend["session"] == "NY"
        assert weekday["is_weekend"] is False and weekend["is_weekend"] is True
        assert weekend["session_quality"] < weekday["session_quality"]

    def test_session_and_is_weekend_are_metadata_not_measurements(self):
        """The measurement is the quality. The two names behind it must not
        land in ``missing`` on a healthy row — that is what ROW_METADATA_KEYS
        is for, and putting a non-feature in there marks every good row
        incomplete."""
        assert {"session", "is_weekend"} <= ef.ROW_METADATA_KEYS
        missing = _capture("2026-08-04T03:00")["missing"]
        assert "session" not in missing and "is_weekend" not in missing
        # ...and the quality itself is the feature, so it must be present on a
        # row where the order book and level book are absent — its input is a
        # clock, which is the one upstream that cannot go dark.
        assert "session_quality" not in missing

    def test_the_clock_is_injectable_so_the_suite_does_not_drift(self):
        """Without ``now_ts`` these assertions would pass or fail depending on
        the hour CI happened to run."""
        assert _capture("2026-08-04T03:00")["session"] == "ASIA"
        assert _capture("2026-08-04T13:00")["session"] == "OVERLAP"


class TestMoverFifteenMinuteTerm:
    def test_sep_15m_is_declared_by_the_mover_path_only(self):
        """``max(15m, 1H fan)`` is MVRTP's gate and nobody else's; the split
        that reads this column would mean nothing on a path without it."""
        assert "sep_15m_pct" in ef.features_for("MOVER_TREND_PULLBACK")
        assert "sep_15m_pct" not in ef.features_for("TREND_PULLBACK_EMA")
        assert "sep_15m_pct" not in ef.CORE_FEATURES

    def test_the_15m_term_travels_through_extras(self):
        row = _capture("2026-08-04T13:00", extras={"sep_15m_pct": 1.2})
        assert row["sep_15m_pct"] == 1.2

    def test_a_15m_term_that_stops_computing_is_reported_dark(self):
        """It shares the missing-accounting, so it cannot quietly vanish the
        way ``stack_sep_pct`` could before ROW_METADATA_KEYS decided."""
        row = _capture("2026-08-04T13:00", extras={"sep_15m_pct": None})
        assert "sep_15m_pct" in row["missing"]


# --------------------------------------------------------------------------- #
# Both rules ship shadow — the doctrine, guarded
# --------------------------------------------------------------------------- #


class TestRulesShipShadow:
    def test_the_two_new_rules_are_registered(self):
        assert {"session_quality", "mover_stack_15m"} <= set(eq.RULES_BY_KEY)

    def test_neither_new_rule_enforces_by_default(self):
        """The guard, and the reason this file exists.

        ``profile_reject`` enforces because applying the pair-tier thresholds
        ``_pass_basic_filters`` already computes invents no number. Neither of
        these does: the session rule is a discovery from one window (however
        well it replicates), and the mover rule would partly undo a deliberate
        widening. Measurement is ON from the moment they ship; enforcement is
        an owner flip on the ops panel, on a fresh window.
        """
        for key in ("session_quality", "mover_stack_15m"):
            assert eq.RULES_BY_KEY[key].live_default is False, (
                f"{key} must ship shadow — enforcing it changes what emits, "
                "which is dark-first + owner sign-off"
            )

    def test_the_mover_threshold_is_bound_to_the_paths_own_floor(self):
        """Not a second opinion about what a strong run is.

        The rule applies ``MOVER_TP_MIN_STACK_SEP_PCT`` to the 15m term alone —
        the term ``max(15m, 1H fan)`` can hide. If the floor moves, this moves
        with it; a hand-typed copy here would be the third spelling of one
        number.
        """
        from config import ENTRY_QUALITY_RULE_THRESHOLD

        assert ENTRY_QUALITY_RULE_THRESHOLD["mover_stack_15m"] == MOVER_TP_MIN_STACK_SEP_PCT

    def test_the_session_threshold_is_a_boundary_on_the_existing_scale(self):
        """0.8 is exactly 'weekday London / Overlap / NY' — a cut on
        ``classify_session``'s published numbers, not a fitted value."""
        from config import ENTRY_QUALITY_RULE_THRESHOLD

        thr = ENTRY_QUALITY_RULE_THRESHOLD["session_quality"]
        for good in ("2026-08-04T09:00", "2026-08-04T13:00", "2026-08-04T18:00"):
            assert _capture(good)["session_quality"] >= thr
        for bad in ("2026-08-04T03:00", "2026-08-04T23:00", "2026-08-01T18:00"):
            assert _capture(bad)["session_quality"] < thr


class TestShadowRuleBehaviour:
    """Driven through the real registry rules, not a fixture — the point is
    what *these* rules do."""

    def _params(self, live_master: bool = True):
        return eq.EntryQualityParams(
            enabled=True,
            live=live_master,
            max_reject_frac=1.0,
            budget_window=200,
            rules=tuple(
                eq.RuleParams(
                    rule=r,
                    live=r.live_default,
                    threshold=(
                        0.8 if r.key == "session_quality"
                        else MOVER_TP_MIN_STACK_SEP_PCT if r.key == "mover_stack_15m"
                        else r.threshold_default
                    ),
                )
                for r in eq.RULES
            ),
        )

    def test_an_asia_entry_would_reject_but_does_not_suppress(self):
        """The separation the whole shadow half rests on: the rule fires, is
        recorded, and costs the candidate nothing."""
        row = _capture("2026-08-04T03:00", extras={"sep_15m_pct": 9.0})
        out = eq.evaluate(row, "MOVER_TREND_PULLBACK", self._params())
        assert "session_quality" in out.would_reject_by
        assert out.enforced_by is None
        assert out.suppressed is False
        assert out.reason == "shadow"

    def test_a_prime_window_entry_does_not_fire_the_session_rule(self):
        row = _capture("2026-08-04T13:00", extras={"sep_15m_pct": 9.0})
        out = eq.evaluate(row, "MOVER_TREND_PULLBACK", self._params())
        assert "session_quality" not in out.would_reject_by

    def test_a_flat_15m_stack_would_reject_on_the_mover_path(self):
        """The 1H fan carried this candidate; the traded timeframe is flat."""
        row = _capture("2026-08-04T13:00", extras={"sep_15m_pct": 0.4})
        out = eq.evaluate(row, "MOVER_TREND_PULLBACK", self._params())
        assert "mover_stack_15m" in out.would_reject_by
        assert out.enforced_by is None

    def test_the_mover_rule_does_not_speak_to_other_paths(self):
        row = _capture("2026-08-04T13:00")
        out = eq.evaluate(row, "TREND_PULLBACK_EMA", self._params())
        assert "mover_stack_15m" not in tuple(o.key for o in out.outcomes)

    def test_an_unstamped_15m_term_abstains_rather_than_suppressing(self):
        """Fail-open, deliberately: the input is a measurement lane, and a
        fail-closed rule here kills the feed the moment a stamp goes missing."""
        row = _capture("2026-08-04T13:00")   # no sep_15m_pct
        out = eq.evaluate(row, "MOVER_TREND_PULLBACK", self._params())
        mover = next(o for o in out.outcomes if o.key == "mover_stack_15m")
        assert mover.verdict == eq.VERDICT_UNKNOWN
        assert "mover_stack_15m" not in out.would_reject_by


# --------------------------------------------------------------------------- #
# Designed vs shipped — two measurements, never one
# --------------------------------------------------------------------------- #


def _signal(entry: float = 100.0, structural: float = 4.13, shipped_pct: float = 3.09) -> Signal:
    """A real ``Signal``. The defect lives in the gap between two of its fields,
    so a stub with keys of our choosing would assert our assumption back."""
    sig = Signal(
        channel="360_SCALP",
        symbol="BTWUSDT",
        direction=Direction.LONG,
        entry=entry,
        stop_loss=entry - entry * shipped_pct / 100.0,
        tp1=entry + structural,
        tp2=entry + structural * 2,
    )
    sig.original_sl_distance = entry * structural / 100.0
    sig.sl_distance_pct_at_entry = shipped_pct
    return sig


class TestShippedStopDistance:
    def test_designed_and_shipped_are_different_numbers(self):
        """The whole finding in one assertion. Before this shipped, only the
        first travelled onto the record — and every R on every ops surface
        divides by it."""
        sig = _signal()
        assert entry_sl_distance_pct(sig) == 4.13
        assert shipped_sl_distance_pct(sig) == 3.09

    def test_a_missing_shipped_stamp_refuses_rather_than_guessing(self):
        """``abs(entry - stop_loss)`` is the tempting fallback and it is the
        bug: by the terminal transition the stop has been moved. 0.0 means
        'not knowable', and readers refuse it."""
        sig = _signal()
        del sig.sl_distance_pct_at_entry
        assert shipped_sl_distance_pct(sig) == 0.0

    def test_the_record_carries_both(self, tmp_path):
        """Driven through the real tracker and the real helpers, so the test
        cannot go green on a shape nobody produces."""
        tracker = PerformanceTracker(storage_path=str(tmp_path / "perf.json"))
        sig = _signal()
        tracker.record_outcome(
            signal_id="sig-1",
            channel="360_SCALP",
            symbol="BTWUSDT",
            direction="LONG",
            entry=100.0,
            hit_tp=0,
            hit_sl=True,
            pnl_pct=-3.09,
            outcome_label="SL_HIT",
            stop_loss=float(sig.stop_loss),
            sl_distance_pct_at_entry=entry_sl_distance_pct(sig),
            shipped_sl_distance_pct=shipped_sl_distance_pct(sig),
        )
        rec = tracker._records[-1]
        assert rec.sl_distance_pct_at_entry == 4.13
        assert rec.shipped_sl_distance_pct == 3.09
        # The point of the pair: they disagree, and the record now says so.
        assert rec.sl_distance_pct_at_entry > rec.shipped_sl_distance_pct

    def test_the_field_name_is_a_cross_repo_contract(self):
        """Pinned on the producing side so a rename fails loudly here rather
        than quietly emptying an ops column (#817's lesson)."""
        from dataclasses import fields

        assert "shipped_sl_distance_pct" in {f.name for f in fields(SignalRecord)}

    def test_old_rows_default_to_unknown_not_to_no_override(self):
        assert SignalRecord(
            signal_id="x", channel="c", symbol="s", direction="LONG",
            entry=1.0, hit_tp=0, hit_sl=False, pnl_pct=0.0, confidence=70.0,
        ).shipped_sl_distance_pct == 0.0


class TestGeometryOverrideSection:
    def test_unstamped_rows_are_excluded_and_counted_apart(self):
        """0.0 means unknown. Averaging it in reports 'no divergence' for a
        fault that is happening — the blank-needs-a-cause rule, applied to a
        migration."""
        out = build_geometry_override([
            {"setup_class": "MVRTP", "sl_distance_pct_at_entry": 4.13, "shipped_sl_distance_pct": 3.09},
            {"setup_class": "MVRTP", "sl_distance_pct_at_entry": 4.00, "shipped_sl_distance_pct": 0.0},
        ])["MVRTP"]
        assert out["rows"] == 2
        assert out["stamped"] == 1
        assert out["unstamped"] == 1
        assert out["median_designed_pct"] == 4.13

    def test_a_tightened_stop_reads_as_a_ratio_above_one(self):
        out = build_geometry_override([
            {"setup_class": "MVRTP", "sl_distance_pct_at_entry": 4.13, "shipped_sl_distance_pct": 3.09},
        ])["MVRTP"]
        assert out["tightened"] == 1
        assert out["widened"] == 0
        assert out["median_ratio"] > 1.0

    def test_an_untouched_geometry_reads_as_neither(self):
        """A bypassed path (SR_FLIP_RETEST is in the predictive bypass list)
        should show ratio 1.0 — which is what makes the mover rows legible."""
        out = build_geometry_override([
            {"setup_class": "SR_FLIP_RETEST", "sl_distance_pct_at_entry": 2.5, "shipped_sl_distance_pct": 2.5},
        ])["SR_FLIP_RETEST"]
        assert out["tightened"] == 0 and out["widened"] == 0
        assert out["median_ratio"] == 1.0
