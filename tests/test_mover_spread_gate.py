"""Regression guard for the mover spread-gate unit bug.

`ScanContext.spread_pct` is a PERCENT of mid (0.5 == 0.5%). The mover spread
gate once compared it against the literal ``0.005`` — i.e. 0.005% — which is
~100× too tight and silently skipped every promoted mover *before* evaluation,
the root cause of "movers never fire". These tests pin the threshold to a sane
percent-unit value so the off-by-100 can't creep back.
"""
from __future__ import annotations

import config


def test_mover_max_spread_is_percent_unit_and_sane():
    # Percent units: a realistic mover spread (~0.05–0.3%) must be admittable,
    # so the threshold has to be well above a fraction-style 0.005.
    assert config.MOVER_MAX_SPREAD_PCT >= 0.1, (
        "MOVER_MAX_SPREAD_PCT looks like a fraction (0.005==0.5%) — it must be a "
        "PERCENT (0.5==0.5%), or the gate rejects every mover before evaluation."
    )
    # …but not so loose it admits genuinely untradeable books.
    assert config.MOVER_MAX_SPREAD_PCT <= 2.0


def test_mover_gate_is_looser_than_a_hair_tight_fraction():
    # The exact bug value, asserted dead: 0.005 (0.005%) must NOT be the gate.
    assert config.MOVER_MAX_SPREAD_PCT != 0.005


def test_typical_liquid_mover_spread_passes_the_gate():
    # FET/PUNDIX/GWEI-class movers run ~0.02–0.08% on Binance futures; all must
    # clear the gate (these were the pairs flunking the buggy 0.005 gate live).
    for spread_pct in (0.02, 0.05, 0.08):
        assert spread_pct <= config.MOVER_MAX_SPREAD_PCT
