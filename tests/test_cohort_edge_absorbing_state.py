"""The cohort-edge gate must be able to change its mind (2026-07-30).

Cohort-edge STEP 2 went ACTIVE on 2026-07-07 and the delivered feed fell from
~48/day to ~9/day the next day.  The gate suppresses on MEASURED expectancy,
and the only thing that feeds that measurement is a delivered signal resolving
(``trade_monitor`` → ``CohortEdgeStore.record``).  So a suppressed cohort
produces no new evidence about itself:

    suppressed → never emits → never resolves → never records →
    the count-bounded deque never rotates → the verdict is permanent

An absorbing state.  ``_window`` bounds the record COUNT and nothing bounded
their AGE, so cohorts locked on 2026-07-07 were still being judged on that
day's outcomes 23 days later with no path back.

Second defect, same gate: it was the only live gate that never called
``_stamp_suppressed``, so it is absent from the Suppression Quality Audit —
no WOULD_WIN%, no EV/suppression, no KEEP/TUNE/DROP.  It had been suppressing
unmeasured for 23 days.

Every test here fails against the pre-fix code.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.stat_filter import CohortEdgeStore, SignalOutcome


def _store(**kw) -> CohortEdgeStore:
    # persist_path="" disables disk I/O (documented test seam).
    kw.setdefault("persist_path", "")
    kw.setdefault("min_samples", 10)
    return CohortEdgeStore(**kw)


def _outcome(won: bool, pnl: float) -> SignalOutcome:
    return SignalOutcome(
        signal_id="s", channel="360_SCALP", pair="GUAUSDT", regime="RANGING",
        setup_class="MOVER_TREND_PULLBACK", won=won, pnl_pct=pnl,
        side="LONG", macro_dir="DECLINE",
    )


def _fill(store: CohortEdgeStore, n: int, won: bool = False, pnl: float = -1.5) -> None:
    for _ in range(n):
        store.record(_outcome(won, pnl))


def _age_all(store: CohortEdgeStore, days: float) -> None:
    """Push every stored record back in time — simulates a cohort that armed
    the gate and then, by construction, produced nothing further."""
    old = datetime.now(timezone.utc) - timedelta(days=days)
    with store._lock:
        for recs in store._records.values():
            for r in recs:
                object.__setattr__(r, "timestamp", old) if hasattr(r, "__dataclass_fields__") else None
                r.timestamp = old


KEY = ("MOVER_TREND_PULLBACK", "LONG", "RANGING", "DECLINE")


class TestEvidenceExpires:
    def test_a_locked_cohort_releases_once_its_evidence_ages_out(self):
        """The whole point: the gate must not hold a verdict forever."""
        s = _store(max_age_days=14)
        _fill(s, 12)                       # arms: n=12 >= 10, expectancy negative
        assert s.sample_count(*KEY) == 12
        assert s.expectancy(*KEY) is not None
        assert s.expectancy(*KEY) < 0

        _age_all(s, 20)                    # 20 days later, still nothing emitted

        assert s.sample_count(*KEY) == 0, "stale outcomes still counting as evidence"
        assert s.expectancy(*KEY) is None, (
            "cohort still carries a verdict built from evidence older than the "
            "expiry window — the gate can never release it"
        )

    def test_a_cohort_re_arms_on_fresh_losses(self):
        """Releasing is not forgiving — a genuinely losing cohort comes back."""
        s = _store(max_age_days=14)
        _fill(s, 12)
        _age_all(s, 20)
        assert s.expectancy(*KEY) is None
        _fill(s, 10)                       # ten fresh live fills, all losers
        assert s.sample_count(*KEY) == 10
        assert s.expectancy(*KEY) is not None and s.expectancy(*KEY) < 0

    def test_fresh_evidence_is_unaffected(self):
        s = _store(max_age_days=14)
        _fill(s, 12)
        _age_all(s, 3)
        assert s.sample_count(*KEY) == 12
        assert s.expectancy(*KEY) is not None

    def test_expiry_can_be_switched_off(self):
        """0 restores the pre-fix behaviour from the ops panel, no deploy."""
        s = _store(max_age_days=0)
        _fill(s, 12)
        _age_all(s, 400)
        assert s.sample_count(*KEY) == 12
        assert s.expectancy(*KEY) is not None

    def test_runtime_setter_changes_the_window(self):
        s = _store(max_age_days=0)
        _fill(s, 12)
        _age_all(s, 30)
        assert s.sample_count(*KEY) == 12
        s.set_max_age_days(14)
        assert s.sample_count(*KEY) == 0


class TestFreshnessIsReportable:
    def test_freshness_separates_fresh_from_total(self):
        s = _store(max_age_days=14)
        _fill(s, 12)
        _age_all(s, 30)
        _fill(s, 3)
        fresh, total = s.freshness(*KEY)
        assert (fresh, total) == (3, 15)

    def test_frozen_cohorts_names_what_stopped_being_measured(self):
        s = _store(max_age_days=14)
        _fill(s, 12)
        _age_all(s, 30)
        frozen = s.frozen_cohorts()
        assert "MOVER_TREND_PULLBACK/LONG/QUIET/DECLINE" in frozen
        assert frozen["MOVER_TREND_PULLBACK/LONG/QUIET/DECLINE"] == 12

    def test_a_live_cohort_is_not_reported_frozen(self):
        s = _store(max_age_days=14)
        _fill(s, 12)
        assert s.frozen_cohorts() == {}


class TestGateIsMeasurable:
    """The gate must stamp its counterfactual like every other live gate.

    Pinned as a source contract rather than by driving a full scan: the point
    is that the call exists at the suppression site, which is exactly what was
    missing for 23 days.
    """

    def test_cohort_edge_suppression_stamps_a_counterfactual(self):
        import inspect

        import src.scanner as scanner_mod

        src = inspect.getsource(scanner_mod)
        i = src.index("COHORT_EDGE suppressed")
        window = src[i:i + 1400]
        assert '_stamp_suppressed(sig, "cohort_edge")' in window, (
            "the cohort gate rejects without stamping — it cannot appear in "
            "the Suppression Quality Audit and cannot earn its place"
        )

    def test_pair_analysis_critical_stamps_a_counterfactual(self):
        import inspect

        import src.scanner as scanner_mod

        src = inspect.getsource(scanner_mod)
        i = src.index("pair_analysis suppressed")
        window = src[i:i + 1400]
        assert '_stamp_suppressed(sig, "pair_analysis_critical")' in window


class TestTunableIsWired:
    def test_max_age_is_an_ops_tunable(self):
        from src.runtime_tunables import registry

        assert "cohort_edge_max_age_days" in registry()

    def test_default_is_a_real_window_not_disabled(self):
        """A default of 0 would ship the absorbing state straight back."""
        from config import COHORT_EDGE_MAX_AGE_DAYS

        assert COHORT_EDGE_MAX_AGE_DAYS > 0
