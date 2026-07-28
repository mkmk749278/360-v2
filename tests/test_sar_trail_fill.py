"""The trail fill must be the stop price breached, not the reversal bar's open.

Owner-caught by asking whether the dark-signals replay was measuring accurately
(2026-07-28). It was not, and neither was this arm.

``parabolic_sar`` overwrites its output on a reversal bar with the *post-flip*
level — the prior trend's extreme point, which sits on the far side of price.
``simulate_sar_exit`` read that value as "the stop in force during bar i", so on
a flip bar ``lows[i] <= stop_level`` was trivially true and the gap-through
branch filled at the **bar's open** instead of at the level price actually
breached. Right bar, wrong price.

The error was one-directional. A flip bar normally opens on the profitable side
of the stop and wicks through it, so filling at the open is *better* than the
stop — measured across 820 real 15m flip events on 10 symbols: mean **+0.222%**
per trail exit, flattering the trade in **95%** of cases, with only 1% genuine
gap-throughs where filling at the open is correct. Session 88 reported +0.197%
net/trade for this arm; corrected, that is roughly +0.02%. **The measured edge
was smaller than the measurement error.**

These tests are written to fail against the pre-fix code: revert
``simulate_sar_exit`` to ``stop_level = series[i]`` and
``test_long_trail_fills_at_the_breached_stop`` fails with the fill at the bar's
open. A test that does not fail against the old code is not testing the fix.
"""
from __future__ import annotations

import pytest

from src.sar_exit_shadow import (
    parabolic_sar,
    parabolic_sar_levels,
    simulate_sar_exit,
)

_STEP, _MAX = 0.02, 0.2


def _rising_then_stopped() -> tuple[list[float], list[float], list[float], list[float]]:
    """A clean uptrend, then one bar that opens ABOVE the trailing stop and
    wicks down through it — the ordinary intrabar stop-out, not a gap.

    Built in two passes because the stop-out bar's low has to be placed relative
    to a SAR level that only exists once the preceding bars are fixed.
    """
    highs = [100.0 + i * 0.4 for i in range(24)]
    lows = [h - 0.5 for h in highs]
    opens = [(h + low) / 2 for h, low in zip(highs, lows)]
    closes = list(opens)

    _, stops = parabolic_sar_levels(highs, lows, _STEP, _MAX)
    # The level that will be in force on the bar we are about to append.
    trailing = stops[23]
    assert trailing is not None

    highs.append(highs[23])
    lows.append(trailing - 0.30)          # wicks through the stop
    opens.append(highs[23] - 0.10)        # ...but opens well above it
    closes.append(trailing - 0.20)
    return highs, lows, closes, opens


class TestTrailFillPrice:
    def test_published_and_in_force_differ_only_on_reversal_bars(self):
        highs, lows, _, _ = _rising_then_stopped()
        published, in_force = parabolic_sar_levels(highs, lows, _STEP, _MAX)
        # The published series is the indicator and must be untouched by the fix
        # — it is pinned across three repos by test_sar_chart_contract.py.
        assert published == parabolic_sar(highs, lows, _STEP, _MAX)

        differing = [
            i for i in range(2, len(highs))
            if in_force[i] is not None and published[i] != in_force[i]
        ]
        assert differing == [len(highs) - 1], (
            "the two series may differ on reversal bars and nowhere else"
        )

    def test_long_trail_fills_at_the_breached_stop(self):
        """The regression. Pre-fix this filled at the bar's open."""
        highs, lows, closes, opens = _rising_then_stopped()
        _, in_force = parabolic_sar_levels(highs, lows, _STEP, _MAX)
        flip = len(highs) - 1
        stop = in_force[flip]
        bar_open = opens[flip]
        # The setup is only meaningful if the bar opened above the stop.
        assert bar_open > stop

        res = simulate_sar_exit(
            highs=highs, lows=lows, closes=closes, opens=opens,
            entry_idx=4, entry=opens[4], side="LONG",
            step=_STEP, max_step=_MAX, max_bars=0, bar_minutes=15.0,
            stop_loss=opens[4] * 0.95, tp1=opens[4] * 1.20,
        )
        assert res is not None
        assert res["exit_idx"] == flip
        assert res["exit_price"] == pytest.approx(stop, abs=1e-9), (
            "filled at the reversal bar's open instead of the stop it breached"
        )
        assert res["exit_price"] < bar_open, (
            "the corrected fill must be worse than the bar open, not better"
        )

    def test_short_trail_fills_at_the_breached_stop(self):
        highs, lows, closes, opens = _rising_then_stopped()
        # Mirror the series about a price level to make the same shape a short.
        pivot = 200.0
        s_highs = [pivot - low for low in lows]
        s_lows = [pivot - h for h in highs]
        s_opens = [pivot - o for o in opens]
        s_closes = [pivot - c for c in closes]

        _, in_force = parabolic_sar_levels(s_highs, s_lows, _STEP, _MAX)
        flip = len(s_highs) - 1
        stop = in_force[flip]
        assert s_opens[flip] < stop

        res = simulate_sar_exit(
            highs=s_highs, lows=s_lows, closes=s_closes, opens=s_opens,
            entry_idx=4, entry=s_opens[4], side="SHORT",
            step=_STEP, max_step=_MAX, max_bars=0, bar_minutes=15.0,
            stop_loss=s_opens[4] * 1.05, tp1=s_opens[4] * 0.80,
        )
        assert res is not None
        assert res["exit_idx"] == flip
        assert res["exit_price"] == pytest.approx(stop, abs=1e-9)
        assert res["exit_price"] > s_opens[flip], (
            "a short's corrected fill must be worse (higher) than the bar open"
        )

    def test_a_genuine_gap_through_still_fills_at_the_open(self):
        """The pessimistic rule survives: a bar that gaps past the stop fills
        at the open, which is worse. Only the non-gap case changes."""
        highs, lows, closes, opens = _rising_then_stopped()
        _, in_force = parabolic_sar_levels(highs, lows, _STEP, _MAX)
        flip = len(highs) - 1
        stop = in_force[flip]
        opens[flip] = stop - 0.20          # gaps below the stop
        highs[flip] = stop - 0.05

        res = simulate_sar_exit(
            highs=highs, lows=lows, closes=closes, opens=opens,
            entry_idx=4, entry=opens[4], side="LONG",
            step=_STEP, max_step=_MAX, max_bars=0, bar_minutes=15.0,
            stop_loss=opens[4] * 0.95, tp1=opens[4] * 1.20,
        )
        assert res is not None
        assert res["exit_price"] == pytest.approx(opens[flip], abs=1e-9)
        assert res["exit_price"] < stop

    def test_the_fix_never_flatters_a_trade(self):
        """Direction check: the corrected fill is never better than the old one.

        Whatever else changes, a fill correction that could improve a result
        would be a fourth way to flatter a counterfactual.
        """
        highs, lows, closes, opens = _rising_then_stopped()
        published, in_force = parabolic_sar_levels(highs, lows, _STEP, _MAX)
        flip = len(highs) - 1
        old_fill = min(opens[flip], published[flip])   # what the old code did
        new_fill = min(opens[flip], in_force[flip])    # what it does now
        assert new_fill <= old_fill
