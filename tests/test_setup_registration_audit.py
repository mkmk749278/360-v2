"""S41 wiring audit — setup-registration invariants.

The #634 bug class: a setup exists in the SetupClass enum and its evaluator
emits, but it is missing from CHANNEL_SETUP_COMPATIBILITY and/or
REGIME_SETUP_COMPATIBILITY, so `_prepare_signal` hard-rejects it before
scoring in EVERY regime — a silently dead path burning scan budget.
MOVER_TREND_PULLBACK died this way for weeks (#627→#634);
MA_CROSS_TREND_SHIFT was found the same way in the S41 audit.

These tests lock the fix and make the whole class impossible to reintroduce:
every setup an evaluator can emit must be registered in at least one channel
set and at least one regime set (unless it is deliberately disabled).
"""
from __future__ import annotations

import re
from pathlib import Path

from src.signal_quality import (
    CHANNEL_SETUP_COMPATIBILITY,
    REGIME_SETUP_COMPATIBILITY,
    SetupClass,
)

# Setups that are deliberately non-emitting: feature-disabled or merged away.
# A setup belongs here ONLY with a reason string.
_DELIBERATELY_DEAD = {
    "CONTINUATION_LIQUIDITY_SWEEP": "merged into LSR (cls_disabled_merged_into_lsr)",
}


def _emitted_setup_names() -> set[str]:
    scalp_src = Path("src/channels/scalp.py").read_text()
    return set(re.findall(r'setup_class\s*=\s*"([A-Z0-9_]+)"', scalp_src))


def _registered_anywhere(name: str, mapping) -> bool:
    return any(
        any(s.name == name for s in setups) for setups in mapping.values()
    )


class TestMaCrossRegistration:
    def test_in_scalp_channel_set(self):
        assert SetupClass.MA_CROSS_TREND_SHIFT in CHANNEL_SETUP_COMPATIBILITY["360_SCALP"]

    def test_in_trending_regime_sets_only(self):
        from src.signal_quality import MarketState

        member_states = {
            st.name
            for st, setups in REGIME_SETUP_COMPATIBILITY.items()
            if SetupClass.MA_CROSS_TREND_SHIFT in setups
        }
        assert member_states == {"STRONG_TREND", "WEAK_TREND", "BREAKOUT_EXPANSION"}, (
            "MA cross is a trend-shift entry: trending + expansion states only; "
            "ranges whipsaw MA crosses"
        )

    def test_self_classifying(self):
        scalp_quality_src = Path("src/signal_quality.py").read_text()
        m = re.search(r"_SELF_CLASSIFYING = frozenset\(\{(.*?)\}\)", scalp_quality_src, re.S)
        assert m is not None
        assert '"MA_CROSS_TREND_SHIFT"' in m.group(1), (
            "without self-classification, classify_setup re-labels MA-cross "
            "signals by heuristic — wrong SL caps / telemetry / exits"
        )


class TestNoSetupIsSilentlyDead:
    def test_every_emitted_setup_registered_in_a_channel_set(self):
        missing = [
            n
            for n in sorted(_emitted_setup_names())
            if n not in _DELIBERATELY_DEAD
            and hasattr(SetupClass, n)
            and not _registered_anywhere(n, CHANNEL_SETUP_COMPATIBILITY)
        ]
        assert not missing, (
            f"Setups emitted by evaluators but in NO channel set (they will be "
            f"hard-rejected before scoring): {missing}"
        )

    def test_every_emitted_setup_registered_in_a_regime_set(self):
        missing = [
            n
            for n in sorted(_emitted_setup_names())
            if n not in _DELIBERATELY_DEAD
            and hasattr(SetupClass, n)
            and not _registered_anywhere(n, REGIME_SETUP_COMPATIBILITY)
        ]
        assert not missing, (
            f"Setups emitted by evaluators but in NO regime set (they will be "
            f"hard-rejected before scoring): {missing}"
        )

    def test_every_emitted_setup_has_a_display_label(self):
        from config import SIGNAL_TYPE_LABELS

        missing = [
            n
            for n in sorted(_emitted_setup_names())
            if n not in _DELIBERATELY_DEAD and n not in SIGNAL_TYPE_LABELS
        ]
        assert not missing, (
            f"Setups emitted without a subscriber-facing display label: {missing}"
        )
