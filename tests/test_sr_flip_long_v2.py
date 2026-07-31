"""SR_FLIP long V2 (S40, issue #674) — trap-discriminating evidence gates.

The long/short evaluator code is symmetric; the LONG side bled (19% win,
losing in every regime) because a break above resistance in leveraged crypto
is disproportionately a bull trap and V1 confirmed flips on pure price.  V2
requires what a trap can't fake before any LONG:

* volume-backed break  (breakout candle >= 1.5x prior-20 mean volume)
* acceptance hold      (>= 2 closed candles above the level since the break)
* whipsaw guard        (both-direction confirmation in one window = chop)

While SR_FLIP_LONG_ENABLED stays false, V2-passing candidates emit
"[SHADOW] SR_FLIP_LONG_V2_WOULD_FIRE" and are still rejected long_disabled —
merge is behavior-neutral; re-enable is an owner decision on the shadow data.
SR_FLIP_RETEST also joins the CT_LONG macro gate scope so re-enabled longs
inherit the weekly-BTC / coin-daily DOWN suppression.
"""
from __future__ import annotations

import numpy as np
import pytest

import src.channels.scalp as scalp_mod
from src.channels.scalp import ScalpChannel
from tests.test_channels import (
    _make_srflip_candles_long,
    _make_srflip_candles_short,
    _srflip_indicators_long,
    _srflip_indicators_short,
    _srflip_smc,
)


def _eval_long(candles, rsi_val: float = 55.0, regime: str = "TRENDING_UP"):
    ch = ScalpChannel()
    sig = ch._evaluate_sr_flip_retest(
        "BTCUSDT", {"5m": candles}, _srflip_indicators_long(rsi_val=rsi_val),
        _srflip_smc(direction="LONG"), 0.01, 10_000_000, regime=regime,
    )
    return ch, sig


class TestLongV2EvidenceGates:
    @pytest.fixture(autouse=True)
    def _enable_long(self, monkeypatch):
        monkeypatch.setattr(scalp_mod, "SR_FLIP_LONG_ENABLED", True)

    def test_volume_backed_break_passes(self):
        # Fixture ships a 2x volume spike on the breakout candle → emits.
        ch, sig = _eval_long(_make_srflip_candles_long(n=60, flip_offset=3))
        assert sig is not None

    def test_thin_volume_break_rejected(self):
        # Flatten the breakout candle's volume to the baseline → bull-trap
        # signature → long_break_volume_thin.
        candles = _make_srflip_candles_long(n=60, flip_offset=3)
        candles["volume"] = np.ones(60) * 1000.0
        ch, sig = _eval_long(candles)
        assert sig is None
        assert ch._active_no_signal_reason == "long_break_volume_thin"

    def test_single_poke_above_level_rejected(self):
        # Break candle closes above, but every later closed candle closes
        # back below the level — no acceptance, only a poke.
        candles = _make_srflip_candles_long(n=60, flip_offset=3)
        candles["close"][-2] = 99.95  # below level=100 → only the break close is above
        ch, sig = _eval_long(candles)
        assert sig is None
        # The reclaim/acceptance failure is caught either by the V2 hold gate
        # or the pre-existing reclaim gate — both are acceptance semantics.
        assert ch._active_no_signal_reason in (
            "long_acceptance_not_held", "reclaim_hold_failed",
        )

    def test_whipsaw_both_directions_rejected(self):
        # Construct a window where price broke above the resistance AND below
        # the support: V1 silently resolved this LONG; V2 calls it chop.
        # Uses the LevelBook (production) path with fake clustered levels so
        # both structural sides exist to whipsaw through.
        class _FakeLevel:
            def __init__(self, price, type_, tfs):
                self.price = price
                self.type = type_
                self.source_tfs = tfs
                self.source_tf = tfs[0]

        candles = _make_srflip_candles_long(n=60, flip_offset=3)
        # Break BELOW the support with a closed candle inside the same
        # 8-candle window that already contains the long break above 100.
        support = 99.2
        candles["low"][-6] = support * 0.99
        candles["close"][-6] = support * 0.995
        candles["open"][-6] = support * 1.001
        smc = _srflip_smc(direction="LONG")
        smc["level_book_levels"] = [
            _FakeLevel(100.0, "resistance", ["1h", "4h"]),
            _FakeLevel(support, "support", ["1h", "4h"]),
        ]
        ch = ScalpChannel()
        sig = ch._evaluate_sr_flip_retest(
            "BTCUSDT", {"5m": candles}, _srflip_indicators_long(rsi_val=55.0),
            smc, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None
        assert ch._active_no_signal_reason == "whipsaw_flip"


class TestLongStillDarkByDefault:
    """The long side is off (−21.8%, 19% win). Owner 2026-07-31 routed the
    V2-passing candidates into the dark lane so the re-enable decision rests on
    forward-resolved outcomes instead of a candidate count in a log line.

    The safety contract has two halves and both are pinned here: without the
    lane the candidate is rejected outright, and with it the candidate is
    carried but **marked dark**, which is what keeps it out of `signal_queue`.
    A carried-but-unmarked long would reach paid subscribers.
    """

    def _no_dark_lane(self, monkeypatch):
        """Turn off only the dark lane, delegating every other tunable to the
        real one — a blanket `lambda: False` would silently switch off whatever
        else this evaluator happens to read."""
        from src import runtime_tunables as rt

        _real = rt.get
        monkeypatch.setattr(
            rt, "get",
            lambda key, *a, **k: (
                False if key == "dark_emission_enabled" else _real(key, *a, **k)
            ),
        )

    def test_with_the_lane_off_the_long_is_rejected_and_shadow_logged(self, monkeypatch):
        """The tourniquet does not depend on the measurement being switched on."""
        monkeypatch.setattr(scalp_mod, "SR_FLIP_LONG_ENABLED", False)
        self._no_dark_lane(monkeypatch)
        from loguru import logger

        shadow_lines: list = []
        sink_id = logger.add(
            lambda m: shadow_lines.append(str(m)), level="INFO",
        )
        try:
            ch, sig = _eval_long(_make_srflip_candles_long(n=60, flip_offset=3))
        finally:
            logger.remove(sink_id)
        assert sig is None
        assert ch._active_no_signal_reason == "long_disabled"
        assert any("SR_FLIP_LONG_V2_WOULD_FIRE" in line for line in shadow_lines)
        assert any("rejected" in line for line in shadow_lines)

    def test_with_the_lane_on_the_long_is_carried_but_marked_dark(self, monkeypatch):
        """Carried, so it runs the rest of the evaluator and the whole gate
        chain — and dark, so the enqueue site diverts it. `is_dark` is the only
        thing standing between this candidate and a real order."""
        monkeypatch.setattr(scalp_mod, "SR_FLIP_LONG_ENABLED", False)
        from src import dark_emission

        ch, sig = _eval_long(_make_srflip_candles_long(n=60, flip_offset=3))
        assert sig is not None, "the candidate should now be carried, not rejected"
        assert dark_emission.is_dark(sig) is True, (
            "an unmarked carry reaches signal_queue.put and puts a path measured "
            "at -21.8% in front of paid subscribers"
        )
        assert getattr(sig, dark_emission.DARK_ATTR) == dark_emission.GATE_SR_FLIP_LONG

    def test_the_carried_long_is_a_long(self, monkeypatch):
        """Guards against the carry silently attaching to the short side, which
        emits live and must never be diverted."""
        monkeypatch.setattr(scalp_mod, "SR_FLIP_LONG_ENABLED", False)
        _, sig = _eval_long(_make_srflip_candles_long(n=60, flip_offset=3))
        assert sig.direction.value == "LONG"

    def test_config_default_still_disabled(self):
        from config import SR_FLIP_LONG_ENABLED

        assert SR_FLIP_LONG_ENABLED is False

    def test_srflip_in_ct_long_macro_gate_scope(self):
        # Re-enabled longs must inherit the macro DOWN suppression.
        from config import CT_LONG_MACRO_GATE_SETUPS

        assert "SR_FLIP_RETEST" in CT_LONG_MACRO_GATE_SETUPS


class TestShortSideUntouched:
    def test_short_flip_still_emits(self):
        ch = ScalpChannel()
        sig = ch._evaluate_sr_flip_retest(
            "BTCUSDT", {"5m": _make_srflip_candles_short(n=60, flip_offset=3)},
            _srflip_indicators_short(rsi_val=45.0), _srflip_smc(direction="SHORT"),
            0.01, 10_000_000, regime="TRENDING_DOWN",
        )
        assert sig is not None

    def test_short_needs_no_volume_evidence(self):
        # V2 evidence gates are LONG-only by design: the short side is the
        # profitable one (+5.1% / 52% win) and downside breaks are cascade-
        # driven, not trap-driven — flat volume must not block shorts.
        candles = _make_srflip_candles_short(n=60, flip_offset=3)
        candles["volume"] = np.ones(60) * 1000.0
        ch = ScalpChannel()
        sig = ch._evaluate_sr_flip_retest(
            "BTCUSDT", {"5m": candles},
            _srflip_indicators_short(rsi_val=45.0), _srflip_smc(direction="SHORT"),
            0.01, 10_000_000, regime="TRENDING_DOWN",
        )
        assert sig is not None
