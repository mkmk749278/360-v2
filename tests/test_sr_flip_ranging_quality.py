"""Behavioral tests for the RANGING SR_FLIP quality re-tighten (2026-06-16).

SR_FLIP_RETEST bleeds specifically in RANGING (live: -3.97 over 32 signals,
all ATR buckets) while it is flat-to-positive in trends (+0.21 TRENDING_DOWN).
The fix GENERATES only the cleanest retests in range rather than disabling the
setup: when SR_FLIP_RANGING_STRICT_ENABLED, two loosened gates revert to hard
*only in RANGING* — the extended retest zone and the 70-79 / 21-30 RSI soft
band. Trending and clean (premium-zone, mid-RSI) signals are untouched.

Ships dark; these tests prove (a) default is behavior-neutral, (b) when enabled
it rejects only the marginal RANGING case, and (c) it stays surgical.

Reuses the SR_FLIP harness from test_channels.
"""
from __future__ import annotations

import pytest

import src.channels.scalp as scalp_mod
from src.channels.scalp import ScalpChannel
from tests.test_channels import (
    _make_srflip_candles_long,
    _srflip_indicators_long,
    _srflip_smc,
)


@pytest.fixture(autouse=True)
def _enable_srflip_long(monkeypatch):
    # SR_FLIP longs are disabled by default (owner stopgap 2026-06-29). These
    # cases verify the long-side mechanics, which remain valid as an opt-in —
    # enable the long side so they exercise the generation path.
    monkeypatch.setattr(scalp_mod, "SR_FLIP_LONG_ENABLED", True)


def test_srflip_long_disabled_by_default(monkeypatch):
    """Engine default: a valid SR_FLIP LONG retest is gated off (long_disabled)."""
    monkeypatch.setattr(scalp_mod, "SR_FLIP_LONG_ENABLED", False)
    ch = ScalpChannel()
    candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
    indicators = _srflip_indicators_long(rsi_val=55.0)
    sig = ch._evaluate_sr_flip_retest(
        "BTCUSDT", candles, indicators, _srflip_smc(direction="LONG"),
        0.01, 10_000_000, regime="RANGING",
    )
    assert sig is None
    assert ch._active_no_signal_reason == "long_disabled"


def _eval(rsi_val: float, regime: str = "RANGING"):
    ch = ScalpChannel()
    candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
    indicators = _srflip_indicators_long(rsi_val=rsi_val)
    sig = ch._evaluate_sr_flip_retest(
        "BTCUSDT", candles, indicators, _srflip_smc(direction="LONG"),
        0.01, 10_000_000, regime=regime,
    )
    return ch, sig


class TestSrFlipRangingQuality:
    def test_ships_dark(self):
        # Evaluator-path / paid-channel routing change — must default OFF so
        # merge-to-main is behavior-neutral; activation is a one-line env flag.
        assert scalp_mod._SR_FLIP_RANGING_STRICT_ENABLED is False

    def test_dark_mode_still_emits_overbought_ranging_retest(self):
        # Default (dark): an RSI-72 (soft-band) retest in RANGING still emits,
        # carrying only the existing +5 soft penalty — no behavior change.
        ch, sig = _eval(rsi_val=72.0)
        assert sig is not None, "dark mode must not change generation"

    def test_strict_rejects_softband_rsi_in_ranging(self, monkeypatch):
        monkeypatch.setattr(scalp_mod, "_SR_FLIP_RANGING_STRICT_ENABLED", True)
        ch, sig = _eval(rsi_val=72.0)
        assert sig is None
        assert ch._active_no_signal_reason == "ranging_strict_rsi"

    def test_strict_keeps_clean_rsi_in_ranging(self, monkeypatch):
        # Surgical: a clean mid-RSI retest in RANGING still emits even when
        # strict is on — only the overbought/oversold band is cut.
        monkeypatch.setattr(scalp_mod, "_SR_FLIP_RANGING_STRICT_ENABLED", True)
        ch, sig = _eval(rsi_val=55.0)
        assert sig is not None, "strict mode must keep clean-RSI RANGING retests"
