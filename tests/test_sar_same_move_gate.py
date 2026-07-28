"""One move must not buy ten rows in the SAR ledger.

Regression cover for the 2026-07-28 defect. The stamp path's only throttle was a
cooldown keyed ``(symbol, setup, side, provenance)``. That bounds the stamp
*rate*; it cannot bound how many rows one move contributes, and on a mover setup
that persists for hours those are very different numbers.

From the owner's export (300 rows, 4.17h): 221 of 300 sat in a
``(symbol, side, setup)`` cluster with more than one stamp. SLXUSDT SHORT
MOVER_TREND_PULLBACK produced **10** rows in 2h10m across an entry spread of
0.37% — one setup, one move, one price — and supplied 36% of the whole resolved
population. Counted as written that population read 32% win / −0.364R; counted
one row per move it read 55% / +0.003R. **The sign of the arm's verdict was an
artifact of re-detection.**

Two things conspired. The cooldown period is short relative to how long these
setups live, and the key carries provenance — so a candidate oscillating across
a gate boundary holds two budgets and stamps twice as fast. All 21 sub-cooldown
repeats in the export were provenance flips; zero were genuine cooldown misses.

The contract now: a re-stamp on a move we already hold must carry new
information to earn a row, and the only new information available at the stamp
site is a provenance upgrade.
"""
from __future__ import annotations

import pytest

from src import sar_exit_shadow as sar
from src import suppression_audit as sa
from src.suppression_audit import SuppressedCandidateStore


@pytest.fixture(autouse=True)
def _clear_throttles():
    sar.reset_pair_throttles()
    yield
    sar.reset_pair_throttles()


@pytest.fixture()
def store(tmp_path):
    return SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=200)


def _stamp(store, *, entry, prov, mono, symbol="SLXUSDT"):
    """Drive the real stamp path — SHORT, mirroring the export's 83% SHORT mix."""
    return sar.stamp_sar_pair(
        symbol=symbol, channel="scalp", setup_class="MOVER_TREND_PULLBACK",
        side="SHORT", entry=entry, stop_loss=entry * 1.03, tp1=entry * 0.97,
        provenance=prov, now_mono=mono, store=store,
    )


def _pairs(store):
    """Stamped pairs, not records — each accepted stamp writes two arms."""
    return len(store.records()) // 2


class TestTheRealSLXSequence:
    """Replayed verbatim from the owner's 2026-07-28 export."""

    # (minutes from first stamp, provenance, entry) — the exact ten.
    SEQUENCE = [
        (0.00, sa.PROVENANCE_SUPPRESSED, 0.09118),
        (13.15, sa.PROVENANCE_SUPPRESSED, 0.09088),
        (15.17, sa.PROVENANCE_ENQUEUED, 0.09093),
        (45.33, sa.PROVENANCE_ENQUEUED, 0.09116),
        (59.48, sa.PROVENANCE_SUPPRESSED, 0.09101),
        (88.25, sa.PROVENANCE_SUPPRESSED, 0.09116),
        (91.35, sa.PROVENANCE_ENQUEUED, 0.09117),
        (107.77, sa.PROVENANCE_SUPPRESSED, 0.09115),
        (120.42, sa.PROVENANCE_SUPPRESSED, 0.09116),
        (130.47, sa.PROVENANCE_SUPPRESSED, 0.09084),
    ]

    def test_ten_re_detections_of_one_move_become_two_rows(self, store):
        accepted = [
            (mins, prov)
            for mins, prov, entry in self.SEQUENCE
            if _stamp(store, entry=entry, prov=prov, mono=mins * 60.0)
        ]
        assert _pairs(store) == 2, (
            f"one move, one price band, ten re-detections — got {_pairs(store)} "
            f"rows from {accepted}"
        )
        # The two that survive are the first sighting and the one upgrade.
        assert [p for _, p in accepted] == [
            sa.PROVENANCE_SUPPRESSED, sa.PROVENANCE_ENQUEUED,
        ]

    def test_the_whole_sequence_stays_inside_one_price_band(self):
        """Guards the fixture itself: if these entries ever stopped being one
        move, the test above would be asserting something else entirely."""
        entries = [e for _, _, e in self.SEQUENCE]
        spread = (max(entries) - min(entries)) / min(entries) * 100.0
        assert spread == pytest.approx(0.374, abs=0.01)

    def test_pre_fix_sampling_is_recoverable(self, store):
        """``SAR_EXIT_SHADOW_SAME_MOVE_PCT=0`` restores the old behaviour.

        Not decoration — it is how the change is rolled back on a live VPS
        without a deploy, and it pins that the cooldown (not the new gate) is
        what shapes the result when the gate is off.
        """
        import config
        original = config.SAR_EXIT_SHADOW_SAME_MOVE_PCT
        config.SAR_EXIT_SHADOW_SAME_MOVE_PCT = 0.0
        try:
            for mins, prov, entry in self.SEQUENCE:
                _stamp(store, entry=entry, prov=prov, mono=mins * 60.0)
        finally:
            config.SAR_EXIT_SHADOW_SAME_MOVE_PCT = original
        assert _pairs(store) > 2, "the gate must be switchable off"


class TestWhatStillEarnsARow:
    def test_a_move_that_leaves_the_band_stamps_again(self, store):
        assert _stamp(store, entry=100.0, prov=sa.PROVENANCE_SUPPRESSED, mono=0.0)
        # 0.4% away, inside the 0.5% band → same move.
        assert not _stamp(store, entry=100.4, prov=sa.PROVENANCE_SUPPRESSED, mono=3600.0)
        # 0.6% away → a different move.
        assert _stamp(store, entry=100.6, prov=sa.PROVENANCE_SUPPRESSED, mono=7200.0)
        assert _pairs(store) == 2

    def test_the_same_level_hours_later_is_a_different_move(self, store):
        """Price can return to a level by a different path. After
        ``SAME_MOVE_MAX_SEC`` that genuinely is new evidence."""
        assert _stamp(store, entry=100.0, prov=sa.PROVENANCE_SUPPRESSED, mono=0.0)
        from config import SAR_EXIT_SHADOW_SAME_MOVE_MAX_SEC as _max

        assert not _stamp(
            store, entry=100.0, prov=sa.PROVENANCE_SUPPRESSED, mono=float(_max) - 1.0
        )
        assert _stamp(
            store, entry=100.0, prov=sa.PROVENANCE_SUPPRESSED, mono=float(_max) + 1.0
        )

    def test_a_different_symbol_is_never_the_same_move(self, store):
        assert _stamp(store, entry=100.0, prov=sa.PROVENANCE_SUPPRESSED, mono=0.0)
        assert _stamp(
            store, entry=100.0, prov=sa.PROVENANCE_SUPPRESSED, mono=1.0,
            symbol="INJUSDT",
        )
        assert _pairs(store) == 2


class TestTheUpgradeIsSpentOnce:
    """The 2026-07-25 property survives, but it cannot become a new ratchet."""

    def test_suppressed_then_enqueued_is_allowed(self, store):
        assert _stamp(store, entry=100.0, prov=sa.PROVENANCE_SUPPRESSED, mono=0.0)
        assert _stamp(store, entry=100.0, prov=sa.PROVENANCE_ENQUEUED, mono=120.0), (
            "a suppressed stamp must never swallow a real signal's stamp — the "
            "reason the cooldown key carries provenance at all (2026-07-25)"
        )

    def test_but_only_once_per_move(self, store):
        _stamp(store, entry=100.0, prov=sa.PROVENANCE_SUPPRESSED, mono=0.0)
        _stamp(store, entry=100.0, prov=sa.PROVENANCE_ENQUEUED, mono=120.0)
        # Oscillating back and forth must not keep buying rows.
        for i, prov in enumerate(
            [sa.PROVENANCE_SUPPRESSED, sa.PROVENANCE_ENQUEUED] * 4
        ):
            assert not _stamp(
                store, entry=100.0, prov=prov, mono=1000.0 + i * 700.0
            ), f"re-stamp {i} on an already-upgraded move"
        assert _pairs(store) == 2

    def test_an_upgrade_still_waits_out_its_own_cooldown(self, store):
        """The same-move gate is additive. It never *loosens* the cooldown."""
        assert _stamp(store, entry=100.0, prov=sa.PROVENANCE_ENQUEUED, mono=0.0)
        assert not _stamp(store, entry=100.0, prov=sa.PROVENANCE_ENQUEUED, mono=60.0)


class TestSchemaStamp:
    """Rows either side of the change are sampled differently and must be
    distinguishable — the ``prov_schema`` precedent, for the same reason."""

    def test_rows_carry_the_stamp_rule_generation(self, store):
        assert _stamp(store, entry=100.0, prov=sa.PROVENANCE_ENQUEUED, mono=0.0)
        assert all(r["stamp_schema"] == sar.STAMP_SCHEMA for r in store.records())
        assert sar.STAMP_SCHEMA > 0

    def test_other_stampers_are_untouched(self, store):
        """A shared record field must not silently re-label another module's
        rows: everyone who has no dedup rule of their own stays at 0."""
        rec = sa.stamp_candidate(
            gate_name="some_gate", symbol="BTCUSDT", channel="scalp",
            setup_class="SR_FLIP_RETEST", side="LONG",
            entry=100.0, stop_loss=99.0, tp1=102.0, store=store,
        )
        assert rec is not None
        assert store.records()[-1]["stamp_schema"] == 0
