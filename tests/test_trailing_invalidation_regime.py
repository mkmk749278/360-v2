"""Tests for regime-aware trailing-kill retrace threshold (session 20).

When INVALIDATION_TRAILING_RETRACE_REGIME_AWARE=true, signals entered in
TRENDING_UP/TRENDING_DOWN regimes use INVALIDATION_TRAILING_RETRACE_PCT_TRENDING
(default 0.70) instead of the baseline 0.50.  Normal trend pullbacks retrace
50-65% of a leg without reversing — the wider threshold prevents runner kills.

Tests drive the pure ``_check_trailing_invalidation`` method via a minimal
TradeMonitor stub so they collect without a live GCP / Firestore environment.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import pytest

from src.smc import Direction


# ---------------------------------------------------------------------------
# Minimal Signal stub — only the fields _check_trailing_invalidation reads.
# ---------------------------------------------------------------------------
@dataclass
class _Sig:
    direction: object
    entry: float
    stop_loss: float
    max_favorable_excursion_pct: float
    current_price: float
    entry_regime: str = ""


# ---------------------------------------------------------------------------
# Minimal TradeMonitor stub that exposes only the method under test.
# ---------------------------------------------------------------------------
class _TM:
    def _check_trailing_invalidation(self, sig):
        from src.trade_monitor import TradeMonitor
        return TradeMonitor._check_trailing_invalidation(self, sig)


@pytest.fixture
def _flag_off(monkeypatch):
    # Patch the module-level names in trade_monitor (bound at import via
    # ``from config import ...``); patching config.* would not affect the
    # already-bound names — same pattern as test_invalidation_btc_correlation.
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_RETRACE_REGIME_AWARE", False)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_RETRACE_PCT_DEFAULT", 0.50)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_RETRACE_PCT_TRENDING", 0.70)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_MFE_R_DEFAULT", 0.30)


@pytest.fixture
def _flag_on(monkeypatch):
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_RETRACE_REGIME_AWARE", True)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_RETRACE_PCT_DEFAULT", 0.50)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_RETRACE_PCT_TRENDING", 0.70)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_MFE_R_DEFAULT", 0.30)


def _long_sig(entry, sl, mfe_pct, current_price, regime=""):
    """Helper: a LONG signal with given parameters."""
    return _Sig(
        direction=Direction.LONG,
        entry=entry,
        stop_loss=sl,
        max_favorable_excursion_pct=mfe_pct,
        current_price=current_price,
        entry_regime=regime,
    )


def test_default_threshold_fires_at_50pct_retrace(_flag_off):
    # RANGING regime + flag OFF → uses 0.50 threshold.
    # MFE peak +2.0%, now at +0.8% → retrace = (2.0-0.8)/2.0 = 0.60 ≥ 0.50 → fires.
    sig = _long_sig(entry=100.0, sl=99.0, mfe_pct=2.0, current_price=100.8, regime="RANGING")
    result = _TM()._check_trailing_invalidation(sig)
    assert result is not None
    assert "trailing invalidation" in result


def test_default_threshold_not_armed_below_mfe_r(_flag_off):
    # MFE is only 0.1R (0.10 × SL_dist=1%) — not armed yet.
    sig = _long_sig(entry=100.0, sl=99.0, mfe_pct=0.1, current_price=100.05, regime="RANGING")
    assert _TM()._check_trailing_invalidation(sig) is None


def test_trending_still_uses_default_when_flag_off(_flag_off):
    # Flag off → TRENDING uses the same 0.50 threshold.
    # MFE +2.0%, now +0.8% → retrace 60% ≥ 50% → should still fire.
    sig = _long_sig(entry=100.0, sl=99.0, mfe_pct=2.0, current_price=100.8, regime="TRENDING_UP")
    result = _TM()._check_trailing_invalidation(sig)
    assert result is not None


def test_trending_wider_threshold_survives_60pct_retrace(_flag_on):
    # Flag ON + TRENDING_UP → threshold 0.70.
    # MFE +2.0%, now +0.8% → retrace 60% < 70% → should NOT fire.
    sig = _long_sig(entry=100.0, sl=99.0, mfe_pct=2.0, current_price=100.8, regime="TRENDING_UP")
    assert _TM()._check_trailing_invalidation(sig) is None


def test_trending_wider_threshold_fires_at_75pct_retrace(_flag_on):
    # Flag ON + TRENDING_DOWN → threshold 0.70.
    # Short: MFE +2.0%, now +0.4% → retrace = (2.0-0.4)/2.0 = 0.80 ≥ 0.70 → fires.
    sig = _Sig(
        direction=Direction.SHORT,
        entry=100.0,
        stop_loss=101.0,
        max_favorable_excursion_pct=2.0,
        current_price=99.6,  # 0.4% below entry (only 0.4% remaining of 2.0% MFE)
        entry_regime="TRENDING_DOWN",
    )
    result = _TM()._check_trailing_invalidation(sig)
    assert result is not None
    assert "TRENDING-wide threshold" in result


def test_non_trending_regime_uses_default_even_when_flag_on(_flag_on):
    # Flag ON but RANGING → still uses 0.50.
    # MFE +2.0%, now +0.8% → retrace 60% ≥ 50% → fires.
    sig = _long_sig(entry=100.0, sl=99.0, mfe_pct=2.0, current_price=100.8, regime="RANGING")
    result = _TM()._check_trailing_invalidation(sig)
    assert result is not None
    assert "TRENDING-wide threshold" not in (result or "")


def test_empty_regime_uses_default(_flag_on):
    # No regime stamped → falls back to default 0.50.
    sig = _long_sig(entry=100.0, sl=99.0, mfe_pct=2.0, current_price=100.8, regime="")
    result = _TM()._check_trailing_invalidation(sig)
    assert result is not None  # 60% retrace ≥ 50% default → fires
