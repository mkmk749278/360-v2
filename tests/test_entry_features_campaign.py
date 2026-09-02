"""The campaign stamp inside ``entry_features`` — and the accounting seam.

The one thing here that is not obvious: the campaign facts arrive from ``sig``,
which ``capture`` never sees, so they are merged in ``stamp`` *after*
``capture`` has already computed ``missing``. That is precisely the shape that
made ``stack_sep_pct`` a declared feature no probe could flag — a value's
classification depending on where its line sits in a function. These tests pin
the re-derivation instead of trusting the comment.
"""
from __future__ import annotations

import time
from types import SimpleNamespace

import pytest

from src import campaign_state as cs
from src import entry_features as ef


class _Dir:
    def __init__(self, value: str) -> None:
        self.value = value


def _sig(sid="SIG-1", symbol="BTCUSDT", setup="MOVER_TREND_PULLBACK", side="LONG"):
    return SimpleNamespace(
        signal_id=sid,
        symbol=symbol,
        setup_class=setup,
        direction=_Dir(side),
        confidence=71.0,
        entry_regime="",
    )


@pytest.fixture(autouse=True)
def _isolated():
    """A fresh registry AND a fresh ledger per test.

    `EntryFeatureLedger.add` dedupes on `signal_id` — a signal is stamped once
    at creation and a second stamp is a counted fault, not an overwrite. So a
    shared ledger makes the second test reusing an id fail for a reason that has
    nothing to do with what it asserts.
    """
    cs.reset_for_tests(path="")
    ef.reset_ledger(ef.EntryFeatureLedger(path=""))
    yield
    cs.reset_for_tests(path="")
    ef.reset_ledger(None)


def _row_for(sig, features=None, now=None):
    assert ef.stamp(sig, features=dict(features or {}), regime="RANGING", now_ts=now)
    return ef.get_ledger().row_for(str(sig.signal_id))


# --------------------------------------------------------------------------- #


def test_first_entry_stamps_a_known_zero_and_two_honest_blanks():
    row = _row_for(_sig())
    assert row["campaign_leg_index"] == 0.0, "always known — 0 is a value here"
    assert row["campaign_prev_won"] is None, "no previous leg is not a loss"
    assert row["campaign_prev_age_h"] is None
    assert row[ef.reason_key("campaign_prev_won")] == "first_leg"


def test_a_previous_winner_is_stamped_with_its_age():
    now = time.time()
    sig = _sig()
    cs.get_registry().record_outcome(
        cs.key_for(sig), "PROFIT_LOCKED", pnl_pct=2.1, closed_at=now - 5400
    )
    row = _row_for(_sig(sid="SIG-2"), now=now)
    assert row["campaign_prev_won"] == 1.0
    assert row["campaign_leg_index"] == 1.0
    assert row["campaign_prev_age_h"] == pytest.approx(1.5, abs=0.01)
    assert row["campaign_prev_outcome"] == "PROFIT_LOCKED"
    assert row["campaign_prev_pnl_pct"] == pytest.approx(2.1)
    assert row[ef.reason_key("campaign_prev_won")] is None


def test_missing_is_recomputed_over_the_merged_row():
    """The accounting must see keys added AFTER `capture` returned.

    Fails against a tree where `stamp` merges the campaign block without
    re-deriving `missing`: there, a first entry's absent `campaign_prev_won`
    never reaches the column that reports a dark feature.
    """
    row = _row_for(_sig())
    assert "campaign_prev_won" in row["missing"]
    assert "campaign_prev_age_h" in row["missing"]
    # ...and the always-present one never is.
    assert "campaign_leg_index" not in row["missing"]


def test_descriptive_campaign_keys_never_enter_missing():
    """`prev_outcome` and `prev_pnl_pct` describe the PREVIOUS trade.

    They are not measurements of this setup, so counting them would mark every
    first entry incomplete for a reason that is not a fault — the same rule
    that keeps `session` out of `missing` beside `session_quality`.
    """
    row = _row_for(_sig())
    assert row["campaign_prev_outcome"] == ""
    assert "campaign_prev_outcome" not in row["missing"]
    assert "campaign_prev_pnl_pct" not in row["missing"]
    assert ef.reason_key("campaign_prev_won") not in row["missing"]


def test_the_three_features_are_declared_on_every_path():
    """Core by the list's own definition — facts about the trade."""
    for setup in ("MOVER_TREND_PULLBACK", "TREND_PULLBACK_EMA", "MEAN_REVERT", ""):
        declared = ef.features_for(setup)
        for key in ("campaign_leg_index", "campaign_prev_won", "campaign_prev_age_h"):
            assert key in declared, f"{key} missing from {setup or 'core'}"


def test_split_directions_are_the_measured_ones():
    """Higher `prev_won` is better; FRESHER `prev_age_h` is better.

    `campaign_prev_age_h` must stay OUT of `keep_above` — the effect lives
    inside ~6 hours, so keeping the high half keeps the stale rows and would
    read as the effect not existing. `campaign_leg_index` is in neither because
    the measured relationship is not monotonic.
    """
    spec = ef.describe_features()
    keep_above = set(spec["keep_above"])
    assert "campaign_prev_won" in keep_above
    assert "campaign_prev_age_h" not in keep_above
    assert "campaign_leg_index" not in keep_above


def test_schema_bump_is_additive_and_still_reads_its_predecessor():
    """Schema 4 ADDS keys, so schema 3 rows must still load.

    A loader that drops them destroys the entire outcome-joined evidence base
    every other feature on the page is measured on — 371 SAR arms, 2026-08-09.
    """
    assert ef.SCHEMA == 4
    assert 3 in ef.ADDITIVE_FROM_SCHEMAS
    assert 2 in ef.ADDITIVE_FROM_SCHEMAS


def test_a_stamp_survives_a_broken_registry(monkeypatch):
    """A measurement must never kill a scan, and a dead registry is not a fault
    the evaluator should discover."""

    def _boom(*_a, **_kw):
        raise RuntimeError("registry down")

    monkeypatch.setattr(cs, "read_for", _boom)
    row = _row_for(_sig())
    assert row is not None
    assert "campaign_leg_index" not in row, "no invented value on a failed read"
