"""Tests for the strategy portfolio registry (src/strategy_portfolio.py, Layer B)."""
from __future__ import annotations

import pytest

from src import market_context as mc_mod
from src import strategy_portfolio as sp
from src.market_context import build_market_context
from src.signal_quality import SetupClass

_VALID_PHASES = {
    mc_mod.PHASE_MARKUP,
    mc_mod.PHASE_MARKDOWN,
    mc_mod.PHASE_ACCUMULATION,
    mc_mod.PHASE_DISTRIBUTION,
    mc_mod.PHASE_RANGE,
    mc_mod.PHASE_VOLATILE,
    mc_mod.PHASE_QUIET,
    mc_mod.PHASE_UNKNOWN,
}
_VALID_SESSIONS = {
    mc_mod.SESSION_OVERLAP,
    mc_mod.SESSION_NY,
    mc_mod.SESSION_LONDON,
    mc_mod.SESSION_ASIA,
    mc_mod.SESSION_OFF,
}


@pytest.mark.parametrize("setup", [s.value for s in SetupClass])
def test_every_setup_class_has_affinity(setup: str) -> None:
    assert setup in sp.AFFINITY, f"{setup} missing from AFFINITY registry"


def test_shadow_units_registered() -> None:
    for name in sp.SHADOW_STRATEGY_NAMES:
        assert name in sp.AFFINITY


def test_affinity_tags_use_market_context_vocabulary() -> None:
    for name, aff in sp.AFFINITY.items():
        assert aff.phases <= _VALID_PHASES, f"{name} has unknown phase tags"
        assert aff.sessions <= _VALID_SESSIONS, f"{name} has unknown session tags"


def test_unknown_strategy_gets_any_any_default() -> None:
    aff = sp.affinity("NOT_A_REAL_SETUP")
    assert aff.phases == frozenset() and aff.sessions == frozenset()
    # any/any never misaligns
    assert sp.is_context_aligned("NOT_A_REAL_SETUP", "ASIA/QUIET/COMPRESSED/BTC_NEUTRAL") is True


def test_is_context_aligned_true_false_none() -> None:
    # Trend setup inside its design context.
    assert sp.is_context_aligned("BREAKOUT_RETEST", "OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL") is True
    # Trend setup in a quiet Asia range — the doctrine's canonical mismatch.
    assert sp.is_context_aligned("BREAKOUT_RETEST", "ASIA/RANGE/NORMAL/BTC_NEUTRAL") is False
    # Unparseable key → unknown, not misaligned.
    assert sp.is_context_aligned("BREAKOUT_RETEST", "garbage") is None
    assert sp.is_context_aligned("BREAKOUT_RETEST", "") is None


def test_range_family_aligned_where_trend_family_is_not() -> None:
    quiet_asia = "ASIA/RANGE/COMPRESSED/BTC_NEUTRAL"
    assert sp.is_context_aligned("RANGE_REJECTION", quiet_asia) is True
    assert sp.is_context_aligned(sp.SHADOW_RANGE_FADE, quiet_asia) is True
    assert sp.is_context_aligned("TREND_PULLBACK_CONTINUATION", quiet_asia) is False


def test_affinity_as_dict_is_json_shaped() -> None:
    d = sp.affinity_as_dict()
    assert set(d) == set(sp.AFFINITY)
    for tags in d.values():
        assert isinstance(tags["phases"], list)
        assert isinstance(tags["sessions"], list)


def test_build_context_payload_shape() -> None:
    mc = build_market_context(regime_label="TRENDING_UP", funding_rate=0.0002)
    payload = sp.build_context_payload(mc, now_ts=1_752_300_000.0)
    # Context fields + key + timestamps + the affinity registry.
    assert payload["context_key"] == mc.context_key()
    assert payload["mc_phase"] == mc.phase
    assert payload["generated_at"] == 1_752_300_000.0
    assert payload["generated_at_iso"].endswith("Z")
    affinity = payload["strategy_affinity"]
    for s in SetupClass:
        assert s.value in affinity
    for name in sp.SHADOW_STRATEGY_NAMES:
        assert name in affinity
