"""Tests for the Market-Context Engine (src/market_context.py, Layer A).

Pure-function tests — no network, no fixtures beyond a frozen clock.  Verifies each
classifier's cut points, the composite assembler, fail-toward-neutral behaviour, and
the signal-stamp / edge-matrix-key contracts.
"""
from __future__ import annotations

from datetime import datetime, timezone

from src.market_context import (
    FUNDING_CROWDED_LONG,
    FUNDING_CROWDED_SHORT,
    FUNDING_EXTREME_LONG,
    FUNDING_EXTREME_SHORT,
    FUNDING_NEUTRAL,
    FUNDING_UNKNOWN,
    PHASE_ACCUMULATION,
    PHASE_DISTRIBUTION,
    PHASE_MARKDOWN,
    PHASE_MARKUP,
    PHASE_QUIET,
    PHASE_RANGE,
    PHASE_UNKNOWN,
    PHASE_VOLATILE,
    ROTATION_BTC_FALLING,
    ROTATION_BTC_RISING,
    ROTATION_NEUTRAL,
    SESSION_ASIA,
    SESSION_LONDON,
    SESSION_NY,
    SESSION_OFF,
    SESSION_OVERLAP,
    VOL_CASCADE,
    VOL_COMPRESSED,
    VOL_EXPANDED,
    VOL_NORMAL,
    MarketContext,
    build_market_context,
    classify_funding,
    classify_phase,
    classify_rotation,
    classify_session,
    classify_volatility,
)


def _utc(y, mo, d, h, mi=0):
    return datetime(y, mo, d, h, mi, tzinfo=timezone.utc)


# --------------------------------------------------------------------------- session
def test_session_windows_weekday():
    # A Wednesday (2026-07-08).
    assert classify_session(_utc(2026, 7, 8, 3))[0] == SESSION_ASIA
    assert classify_session(_utc(2026, 7, 8, 9))[0] == SESSION_LONDON
    assert classify_session(_utc(2026, 7, 8, 14))[0] == SESSION_OVERLAP
    assert classify_session(_utc(2026, 7, 8, 18))[0] == SESSION_NY
    assert classify_session(_utc(2026, 7, 8, 23))[0] == SESSION_OFF


def test_session_overlap_is_highest_quality():
    _, _, q_overlap = classify_session(_utc(2026, 7, 8, 14))
    _, _, q_asia = classify_session(_utc(2026, 7, 8, 3))
    assert q_overlap == 1.0
    assert q_asia < q_overlap


def test_weekend_flag_and_quality_haircut():
    # 2026-07-11 is a Saturday.
    session, is_weekend, q_wknd = classify_session(_utc(2026, 7, 11, 14))
    _, weekday_flag, q_week = classify_session(_utc(2026, 7, 8, 14))
    assert session == SESSION_OVERLAP  # same clock window
    assert is_weekend is True and weekday_flag is False
    assert q_wknd < q_week  # weekend is thinner


def test_session_naive_datetime_treated_as_utc():
    naive = datetime(2026, 7, 8, 14, 0)  # no tzinfo
    assert classify_session(naive)[0] == SESSION_OVERLAP


# ------------------------------------------------------------------------ volatility
def test_volatility_bands():
    assert classify_volatility(5) == VOL_COMPRESSED
    assert classify_volatility(50) == VOL_NORMAL
    assert classify_volatility(80) == VOL_EXPANDED
    assert classify_volatility(95) == VOL_CASCADE


def test_volatility_cascade_flag_overrides():
    assert classify_volatility(5, cascade_active=True) == VOL_CASCADE


def test_volatility_missing_is_normal():
    assert classify_volatility(None) == VOL_NORMAL
    assert classify_volatility("nonsense") == VOL_NORMAL


# --------------------------------------------------------------------------- funding
def test_funding_bands_both_sides():
    assert classify_funding(0.0) == FUNDING_NEUTRAL
    assert classify_funding(0.0006) == FUNDING_CROWDED_LONG
    assert classify_funding(-0.0006) == FUNDING_CROWDED_SHORT
    assert classify_funding(0.002) == FUNDING_EXTREME_LONG
    assert classify_funding(-0.002) == FUNDING_EXTREME_SHORT


def test_funding_missing_is_unknown():
    assert classify_funding(None) == FUNDING_UNKNOWN


# -------------------------------------------------------------------------- rotation
def test_rotation_btc_led_both_directions():
    tok, led = classify_rotation(0.8)
    assert tok == ROTATION_BTC_RISING and led is True
    tok, led = classify_rotation(-0.8)
    assert tok == ROTATION_BTC_FALLING and led is True


def test_rotation_weak_btc_is_neutral():
    tok, led = classify_rotation(0.1)
    assert tok == ROTATION_NEUTRAL and led is False
    tok, led = classify_rotation(None)
    assert tok == ROTATION_NEUTRAL and led is False


# ----------------------------------------------------------------------------- phase
def test_phase_trends():
    assert classify_phase("TRENDING_UP") == PHASE_MARKUP
    assert classify_phase("TRENDING_DOWN") == PHASE_MARKDOWN


def test_phase_range_resolves_by_prior_htf_trend():
    # Range after an uptrend = distribution; after a downtrend = accumulation.
    assert classify_phase("RANGING", htf_trend_prior="TRENDING_UP") == PHASE_DISTRIBUTION
    assert classify_phase("RANGING", htf_trend_prior="TRENDING_DOWN") == PHASE_ACCUMULATION
    assert classify_phase("RANGING") == PHASE_RANGE  # no prior → unresolved range


def test_phase_quiet_and_volatile():
    assert classify_phase("QUIET") == PHASE_QUIET
    assert classify_phase("RANGING", volatility=VOL_COMPRESSED) == PHASE_QUIET
    assert classify_phase("VOLATILE") == PHASE_VOLATILE
    assert classify_phase("RANGING", volatility=VOL_CASCADE) == PHASE_VOLATILE


def test_phase_unknown_on_empty():
    assert classify_phase("") == PHASE_UNKNOWN
    assert classify_phase(None) == PHASE_UNKNOWN


# ------------------------------------------------------------------ composite / build
def test_build_full_context():
    mc = build_market_context(
        ts=_utc(2026, 7, 8, 14),
        regime_label="TRENDING_UP",
        atr_percentile=80,
        funding_rate=0.0006,
        btc_state=0.7,
    )
    assert mc.session == SESSION_OVERLAP
    assert mc.phase == PHASE_MARKUP
    assert mc.volatility == VOL_EXPANDED
    assert mc.funding == FUNDING_CROWDED_LONG
    assert mc.rotation == ROTATION_BTC_RISING and mc.btc_led is True
    assert mc.context_key() == "OVERLAP/MARKUP/EXPANDED/BTC_RISING"


def test_build_degrades_to_neutral_on_empty_inputs():
    mc = build_market_context(ts=_utc(2026, 7, 8, 3))
    assert isinstance(mc, MarketContext)
    assert mc.phase == PHASE_UNKNOWN
    assert mc.volatility == VOL_NORMAL
    assert mc.funding == FUNDING_UNKNOWN
    assert mc.rotation == ROTATION_NEUTRAL
    # Still produces a valid, serialisable key.
    assert mc.context_key().count("/") == 3


def test_cascade_active_propagates_to_context_field():
    mc = build_market_context(ts=_utc(2026, 7, 8, 14), atr_percentile=95)
    assert mc.volatility == VOL_CASCADE
    assert mc.cascade_active is True


def test_as_signal_fields_contract():
    mc = build_market_context(
        ts=_utc(2026, 7, 8, 14), regime_label="TRENDING_DOWN", atr_percentile=50
    )
    fields = mc.as_signal_fields()
    # Every stamped field the Signal dataclass declares must be present.
    for key in (
        "mc_session", "mc_is_weekend", "mc_session_quality", "mc_phase",
        "mc_volatility", "mc_funding", "mc_rotation", "mc_btc_led",
        "mc_cascade_active", "mc_context_key",
    ):
        assert key in fields
    assert fields["mc_phase"] == PHASE_MARKDOWN
    assert fields["mc_context_key"] == mc.context_key()
