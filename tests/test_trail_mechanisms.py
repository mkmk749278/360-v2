"""The mechanism seam: two trailing exits, one arm engine, no second copy.

What these tests are actually protecting is not the chandelier arithmetic — it
is the property that adding a second mechanism did **not** add a second copy of
``sar_live_shadow``'s guards. So they check three things:

1. the chandelier's ATR is the engine's ATR, element for element, rather than a
   third definition wearing the same name;
2. the chandelier's level series is the one ops' exit bake-off has printed under
   the words "ATR-trail (Chandelier)" since long before this module — two arms
   named for the same mechanism measuring different mechanisms cost this repo a
   session on 2026-07-31;
3. the mechanism decides only the level and whether it may govern, and every
   refusal is a refusal rather than a clamp.
"""
from __future__ import annotations

import numpy as np
import pytest

from src import indicators, trail_mechanisms as tm

PERIOD, MULT = 22, 3.0


def _bars(n, start=100.0, drift=1.0, rng_pct=0.6):
    """(open, high, low, close) with a deterministic wobble, no randomness."""
    out = []
    for i in range(n):
        base = start + i * drift + (2.0 if i % 7 == 0 else 0.0)
        rng = base * rng_pct / 100.0
        out.append((base, base + rng, base - rng, base + rng * 0.25))
    return out


def _cols(bars):
    return (
        [b[1] for b in bars],
        [b[2] for b in bars],
        [b[3] for b in bars],
    )


# --------------------------------------------------------------------------- #
# ATR — one definition, not a third
# --------------------------------------------------------------------------- #


def test_wilder_atr_matches_the_engines_own_atr_element_for_element():
    """``indicators.atr`` is the engine's ATR. This must not be a second one.

    The list version exists because this walk consumes the plain lists the arm
    engine's ``_series`` hands out, and round-tripping them through numpy per
    bar on the monitor loop is cost for nothing. That is an implementation
    choice; it must never become a definition choice — and the only thing that
    can keep those apart is this assertion rather than the docstring saying so.
    """
    highs, lows, closes = _cols(_bars(120))
    mine = tm.wilder_atr(highs, lows, closes, PERIOD)
    theirs = indicators.atr(
        np.asarray(highs), np.asarray(lows), np.asarray(closes), PERIOD
    )
    assert len(mine) == len(theirs)
    for i, (a, b) in enumerate(zip(mine, theirs)):
        if a is None:
            assert np.isnan(b), f"bar {i}: we refuse, numpy produced {b}"
        else:
            assert b == pytest.approx(a, rel=1e-12), f"bar {i}"


def test_atr_refuses_below_its_seed_window_rather_than_seeding_short():
    highs, lows, closes = _cols(_bars(PERIOD))
    assert tm.wilder_atr(highs, lows, closes, PERIOD) == [None] * PERIOD


# --------------------------------------------------------------------------- #
# The chandelier's level — the cross-repo vector
# --------------------------------------------------------------------------- #

#: Byte-identical to ops' ``tests/test_atr_trail_contract.py``. Generated from
#: THIS function, so ops is asserted against the engine and never the reverse —
#: the same direction ``test_sar_chart_contract`` pins SAR in.
#:
#: A short period so the vector is readable; the mechanism is period-agnostic
#: and ``test_wilder_atr_matches...`` above covers the smoothing itself.
CONTRACT_PERIOD, CONTRACT_MULT = 5, 2.0
CONTRACT_HIGHS = [
    100.6, 101.6, 102.6, 103.6, 104.6, 105.6, 106.6, 107.6, 108.6, 109.6,
    108.6, 107.6, 106.6, 105.6, 104.6, 105.6, 106.6, 107.6, 108.6, 109.6,
]
CONTRACT_LOWS = [
    99.4, 100.4, 101.4, 102.4, 103.4, 104.4, 105.4, 106.4, 107.4, 108.4,
    107.4, 106.4, 105.4, 104.4, 103.4, 104.4, 105.4, 106.4, 107.4, 108.4,
]
CONTRACT_CLOSES = [
    100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0,
    108.0, 107.0, 106.0, 105.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0,
]


def _walk(highs, lows, closes, side, period, mult, start=0):
    """Every level the mechanism would have parked, bar by bar.

    Walks through the public entry point with the arm's own carried state,
    exactly as ``step_arm`` does — a test that reached into ``_chandelier_point``
    directly would be asserting the private helper rather than the seam the
    engine actually uses.
    """
    ctx = tm.prepare(tm.MECH_CHANDELIER, highs, lows, closes, {"period": period})
    state: dict = {}
    out = []
    for i in range(start, len(highs)):
        p = tm.point(
            tm.MECH_CHANDELIER, ctx, highs, lows, closes, i,
            side=side, state=state, params={"period": period, "mult": mult},
        )
        out.append(None if p is None else round(p.next_stop, 6))
    return out


def test_the_chandelier_level_is_the_one_ops_bake_off_prints():
    """The cross-repo vector. Change this and ops' column changes meaning."""
    got = _walk(
        CONTRACT_HIGHS, CONTRACT_LOWS, CONTRACT_CLOSES,
        "LONG", CONTRACT_PERIOD, CONTRACT_MULT,
    )
    # Derived by hand rather than recorded from the code — a vector copied out
    # of its own output pins nothing. Every bar of this series prints
    # ``high - prev_close == 1.6``, which is its widest true range, so ATR is a
    # flat **1.6** from the seed onward and the level is simply
    # ``running_high - 2 x 1.6``. The extreme rises to 109.6 at bar 9 and the
    # series then falls back, so the ratchet holds 109.6 - 3.2 = 106.4 for the
    # rest of the window and never loosens.
    assert got == [
        None, None, None, None, None,
        102.4, 103.4, 104.4, 105.4, 106.4,
        106.4, 106.4, 106.4, 106.4, 106.4,
        106.4, 106.4, 106.4, 106.4, 106.4,
    ]
    # …and the second half is the ratchet, not a coincidence of flat data: the
    # highs genuinely fall to 104.6 at bar 14, which un-ratcheted would put the
    # level at 101.4.
    assert min(CONTRACT_HIGHS[10:15]) == 104.6


def test_the_trail_ratchets_toward_price_and_never_widens():
    """A trailing stop that can loosen hands back risk the trade was not sized
    for — the one behaviour SAR's two-bar clamp *does* have and this must not."""
    highs, lows, closes = _cols(_bars(80))
    levels = [x for x in _walk(highs, lows, closes, "LONG", PERIOD, MULT) if x is not None]
    assert levels, "the walk produced no level at all"
    assert all(b >= a for a, b in zip(levels, levels[1:])), levels[:12]


def test_a_short_trail_ratchets_downward():
    bars = _bars(80, start=200.0, drift=-1.0)
    highs, lows, closes = _cols(bars)
    levels = [x for x in _walk(highs, lows, closes, "SHORT", PERIOD, MULT) if x is not None]
    assert levels
    assert all(b <= a for a, b in zip(levels, levels[1:])), levels[:12]


def test_the_ratchet_is_anchored_to_THIS_arm_not_to_the_window():
    """Two arms opening on different bars of one series get different levels.

    This is the property that forces the chandelier's state onto the arm rather
    than into a per-(symbol, bar) cache. Sharing a cache entry would hand a new
    arm an older arm's running extreme — #846's frozen-then-refreshed defect
    arriving through a cache instead of through a store, and just as silent.
    """
    # A series that PEAKS in the middle. On a monotonic rise both arms would
    # converge on the same running high and the test would pass vacuously —
    # which is exactly what the first cut of it did.
    bars = _bars(50) + _bars(40, start=_bars(50)[-1][0], drift=-1.0)
    highs, lows, closes = _cols(bars)
    early = _walk(highs, lows, closes, "LONG", PERIOD, MULT, start=0)[-1]
    late = _walk(highs, lows, closes, "LONG", PERIOD, MULT, start=70)[-1]
    assert early is not None and late is not None
    # The early arm still carries the peak; the arm opened after it never saw
    # one, so its stop sits lower.
    assert early > late


def test_the_chandelier_refuses_before_its_atr_exists():
    highs, lows, closes = _cols(_bars(PERIOD))
    ctx = tm.prepare(tm.MECH_CHANDELIER, highs, lows, closes, {"period": PERIOD})
    got = tm.point(
        tm.MECH_CHANDELIER, ctx, highs, lows, closes, len(highs) - 1,
        side="LONG", state={}, params={"period": PERIOD, "mult": MULT},
    )
    assert got is None


def test_min_bars_is_larger_than_the_atr_seed_so_the_engine_refuses_first():
    assert tm.min_bars(tm.MECH_CHANDELIER, {"period": PERIOD}) > PERIOD
    assert tm.min_bars(tm.MECH_SAR, {}) == 3


# --------------------------------------------------------------------------- #
# onside — the question each mechanism answers its own way
# --------------------------------------------------------------------------- #


def test_a_chandelier_below_the_close_may_govern_a_long():
    highs, lows, closes = _cols(_bars(80))
    ctx = tm.prepare(tm.MECH_CHANDELIER, highs, lows, closes, {"period": PERIOD})
    p = tm.point(
        tm.MECH_CHANDELIER, ctx, highs, lows, closes, len(highs) - 1,
        side="LONG", state={}, params={"period": PERIOD, "mult": MULT},
    )
    assert p is not None and p.onside is True
    assert p.next_stop < closes[-1]


def test_a_chandelier_carries_no_direction_of_its_own():
    """``up`` is None, never False.

    "This mechanism does not answer that" and "this mechanism says down" are
    different facts, and a surface that pools them reports a direction nobody
    computed.
    """
    highs, lows, closes = _cols(_bars(80))
    ctx = tm.prepare(tm.MECH_CHANDELIER, highs, lows, closes, {"period": PERIOD})
    p = tm.point(
        tm.MECH_CHANDELIER, ctx, highs, lows, closes, len(highs) - 1,
        side="LONG", state={}, params={"period": PERIOD, "mult": MULT},
    )
    assert p is not None and p.up is None


def test_a_chandelier_already_past_the_close_may_not_govern():
    """A stop above a long's close is an instant exit, not a trailing stop.

    Handing governance to it would book a fill the mechanism never legitimately
    took, so the arm keeps its original geometry until the trail comes onside —
    the same handover SAR runs when its direction opposes the trade.
    """
    # A sharp reversal: the extreme is far above, so a *narrow* multiplier is
    # needed to put the level above the (collapsed) close.
    highs = [100.0 + i for i in range(30)] + [130.0, 100.0]
    lows = [99.0 + i for i in range(30)] + [99.0, 60.0]
    closes = [99.5 + i for i in range(30)] + [100.0, 61.0]
    ctx = tm.prepare(tm.MECH_CHANDELIER, highs, lows, closes, {"period": 5})
    state: dict = {}
    p = None
    for i in range(len(highs)):
        p = tm.point(
            tm.MECH_CHANDELIER, ctx, highs, lows, closes, i,
            side="LONG", state=state, params={"period": 5, "mult": 0.5},
        )
    assert p is not None
    assert p.next_stop > closes[-1]
    assert p.onside is False


def test_sar_still_answers_onside_from_its_own_direction():
    """The seam must not have changed SAR's answer.

    A rising series is bullish, so SAR may govern a LONG and may not govern a
    SHORT — read off the same ``parabolic_sar_live`` the replay arm, the
    reconciler and the Lumin chart study all use.
    """
    bars = _bars(60)
    highs, lows, closes = _cols(bars)
    kw = dict(state={}, params={"step": 0.02, "max_step": 0.2})
    long_p = tm.point(
        tm.MECH_SAR, None, highs, lows, closes, len(highs) - 1, side="LONG", **kw
    )
    short_p = tm.point(
        tm.MECH_SAR, None, highs, lows, closes, len(highs) - 1, side="SHORT", **kw
    )
    assert long_p is not None and short_p is not None
    assert long_p.up is True
    assert long_p.onside is True and short_p.onside is False
    assert long_p.next_stop == short_p.next_stop  # the level does not depend on side


def test_an_index_past_the_window_refuses_rather_than_clamping():
    highs, lows, closes = _cols(_bars(60))
    assert tm.point(
        tm.MECH_SAR, None, highs, lows, closes, len(highs), side="LONG",
        state={}, params={"step": 0.02, "max_step": 0.2},
    ) is None


# --------------------------------------------------------------------------- #
# The manifest — one writer
# --------------------------------------------------------------------------- #


def test_every_mechanism_has_a_manifest_entry():
    """Derived from ``MECHANISMS``, so a third mechanism fails here rather than
    rendering under its raw key on the one page that reads it."""
    for mech in tm.MECHANISMS:
        man = tm.manifest(mech, tm.default_params(mech))
        assert man["key"] == mech
        assert man["label"] and man["label"] != mech
        assert man["params"]
    assert tm.manifest(tm.MECH_SAR, {})["has_direction"] is True
    assert tm.manifest(tm.MECH_CHANDELIER, {})["has_direction"] is False


def test_default_params_come_from_config_not_from_a_literal_here():
    from config import ATR_TRAIL_MULT, ATR_TRAIL_PERIOD

    p = tm.default_params(tm.MECH_CHANDELIER)
    assert p["period"] == float(ATR_TRAIL_PERIOD)
    assert p["mult"] == float(ATR_TRAIL_MULT)
