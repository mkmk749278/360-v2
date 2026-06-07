"""Tests for the R-scaled trailing-kill ARM threshold (session 22, ships dark).

When INVALIDATION_TRAILING_ARM_RSCALE_ENABLED=true, the trailing kill arms at
``MFE_R_DEFAULT + ARM_R_PER_SL_PCT × sl_dist_pct`` (capped at ARM_R_MAX) instead
of the flat 0.30R floor.  Wide-SL setups (SR_FLIP 1.6–2.5%) must therefore bank
a larger R-multiple before the trailing kill engages; tight-SL setups are barely
affected.  Audit (2026-06-07): trailing_invalidation was the dominant SR_FLIP
premature killer at 44% precisely because the flat arm engaged at trivial profit.

Drives the pure ``_check_trailing_invalidation`` method via a minimal stub so the
tests collect without a live GCP / Firestore environment.
"""
from __future__ import annotations

from dataclasses import dataclass
import pytest

from src.smc import Direction


@dataclass
class _Sig:
    direction: object
    entry: float
    stop_loss: float
    max_favorable_excursion_pct: float
    current_price: float
    entry_regime: str = ""
    symbol: str = "TESTUSDT"
    setup_class: str = "SR_FLIP_RETEST"


class _TM:
    def _check_trailing_invalidation(self, sig):
        from src.trade_monitor import TradeMonitor
        return TradeMonitor._check_trailing_invalidation(self, sig)


def _patch_common(monkeypatch, *, rscale_enabled):
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_RETRACE_REGIME_AWARE", False)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_RETRACE_PCT_DEFAULT", 0.50)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_RETRACE_PCT_TRENDING", 0.70)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_MFE_R_DEFAULT", 0.30)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_ARM_RSCALE_ENABLED", rscale_enabled)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_ARM_R_PER_SL_PCT", 0.15)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_TRAILING_ARM_R_MAX", 0.80)


@pytest.fixture
def _flag_off(monkeypatch):
    _patch_common(monkeypatch, rscale_enabled=False)


@pytest.fixture
def _flag_on(monkeypatch):
    _patch_common(monkeypatch, rscale_enabled=True)


def _short_sig(entry, sl, mfe_pct, current_price, **kw):
    return _Sig(
        direction=Direction.SHORT,
        entry=entry, stop_loss=sl,
        max_favorable_excursion_pct=mfe_pct,
        current_price=current_price, **kw,
    )


def _long_sig(entry, sl, mfe_pct, current_price, **kw):
    return _Sig(
        direction=Direction.LONG,
        entry=entry, stop_loss=sl,
        max_favorable_excursion_pct=mfe_pct,
        current_price=current_price, **kw,
    )


# ---------------------------------------------------------------------------
# Flag OFF — current behavior must be exactly preserved
# ---------------------------------------------------------------------------

class TestFlagOffPreservesBehavior:
    def test_low_mfe_r_still_arms_and_fires_when_off(self, _flag_off):
        # EDGEUSDT reproduction: entry 0.6472 SHORT, SL 0.65776 (1.63% SL),
        # MFE +0.56% → MFE_R≈0.34, retraced to +0.06% (89% retrace).
        sig = _short_sig(0.6472, 0.65776414, 0.56, 0.6468)
        result = _TM()._check_trailing_invalidation(sig)
        assert result is not None
        assert "trailing invalidation" in result

    def test_below_flat_arm_does_not_fire_when_off(self, _flag_off):
        # MFE_R = 0.20 < 0.30 flat arm → not armed regardless.
        sig = _short_sig(1.0, 1.05, 1.0, 0.999)  # SL 5%, MFE 1% → MFE_R 0.20
        assert _TM()._check_trailing_invalidation(sig) is None


# ---------------------------------------------------------------------------
# Flag ON — wide-SL signals no longer arm at trivial R
# ---------------------------------------------------------------------------

class TestFlagOnScalesArm:
    def test_edge_case_no_longer_arms_when_on(self, _flag_on):
        # Same EDGE signal: sl_dist 1.63% → scaled_arm = 0.30 + 0.15×1.63 ≈ 0.545.
        # MFE_R 0.34 < 0.545 → does NOT arm → no premature kill.
        sig = _short_sig(0.6472, 0.65776414, 0.56, 0.6468)
        assert _TM()._check_trailing_invalidation(sig) is None

    def test_wide_sl_high_mfe_still_fires_when_on(self, _flag_on):
        # SL 1.63%, MFE +1.5% → MFE_R≈0.92 > scaled_arm 0.545 → armed.
        # Retrace to +0.5% = (1.5-0.5)/1.5 = 67% > 0.50 → fires.
        sig = _short_sig(0.6472, 0.65776414, 1.5, 0.6472 * (1 - 0.5 / 100))
        result = _TM()._check_trailing_invalidation(sig)
        assert result is not None
        assert "trailing invalidation" in result

    def test_tight_sl_barely_affected(self, _flag_on):
        # SL 0.8% → scaled_arm = 0.30 + 0.15×0.8 = 0.42 (close to flat 0.30).
        # MFE +0.5% → MFE_R = 0.625 > 0.42 → armed. Retrace 60% > 0.50 → fires.
        entry = 1.0
        sl = 1.008  # 0.8% SL, SHORT
        mfe = 0.5
        current = entry * (1 - 0.2 / 100)  # +0.2% excursion → retrace (0.5-0.2)/0.5=60%
        sig = _short_sig(entry, sl, mfe, current)
        result = _TM()._check_trailing_invalidation(sig)
        assert result is not None

    def test_arm_capped_at_max(self, _flag_on):
        # Very wide SL 10% → uncapped arm = 0.30+0.15×10 = 1.80, capped to 0.80.
        # MFE_R = 0.90 (> 0.80 cap) → armed; retrace 70% > 0.50 → fires.
        entry = 1.0
        sl = 1.10  # 10% SL SHORT
        mfe = 9.0  # MFE_R = 9.0/10 = 0.90
        current = entry * (1 - 2.7 / 100)  # excursion +2.7% → retrace (9-2.7)/9=70%
        sig = _short_sig(entry, sl, mfe, current)
        result = _TM()._check_trailing_invalidation(sig)
        assert result is not None

    def test_just_below_capped_arm_does_not_fire(self, _flag_on):
        # Wide SL 10%, MFE_R = 0.70 < 0.80 cap → not armed even with deep retrace.
        entry = 1.0
        sl = 1.10
        mfe = 7.0  # MFE_R = 0.70
        current = entry * (1 - 0.5 / 100)
        sig = _short_sig(entry, sl, mfe, current)
        assert _TM()._check_trailing_invalidation(sig) is None


# ---------------------------------------------------------------------------
# Shadow telemetry — fires only when flag off + kill confirmed below scaled arm
# ---------------------------------------------------------------------------

def _capture_logs():
    """Attach a loguru sink that collects INFO+ messages into a list."""
    from src.utils import get_logger  # noqa: F401  (ensures loguru configured)
    from loguru import logger
    captured: list[str] = []
    sink_id = logger.add(lambda m: captured.append(m.record["message"]), level="INFO")
    return captured, sink_id


class TestShadowTelemetry:
    def test_shadow_logs_when_off_and_would_suppress(self, _flag_off, monkeypatch):
        from loguru import logger
        monkeypatch.setattr("config.DARK_FLAG_SHADOW_TELEMETRY", True)
        captured, sink_id = _capture_logs()
        try:
            # EDGE: fires now (flag off), but MFE_R 0.34 < scaled_arm 0.545 → shadow.
            sig = _short_sig(0.6472, 0.65776414, 0.56, 0.6468)
            result = _TM()._check_trailing_invalidation(sig)
        finally:
            logger.remove(sink_id)
        assert result is not None  # still kills (flag off)
        assert any("TRAILING_RSCALE_WOULD_SUPPRESS" in m for m in captured)

    def test_no_shadow_when_kill_above_scaled_arm(self, _flag_off, monkeypatch):
        from loguru import logger
        monkeypatch.setattr("config.DARK_FLAG_SHADOW_TELEMETRY", True)
        captured, sink_id = _capture_logs()
        try:
            # High MFE_R kill (0.92 > scaled_arm 0.545) → not in suppression set.
            sig = _short_sig(0.6472, 0.65776414, 1.5, 0.6472 * (1 - 0.5 / 100))
            result = _TM()._check_trailing_invalidation(sig)
        finally:
            logger.remove(sink_id)
        assert result is not None
        assert not any("TRAILING_RSCALE_WOULD_SUPPRESS" in m for m in captured)

    def test_no_shadow_when_flag_on(self, _flag_on, monkeypatch):
        from loguru import logger
        monkeypatch.setattr("config.DARK_FLAG_SHADOW_TELEMETRY", True)
        captured, sink_id = _capture_logs()
        try:
            # Flag on → EDGE doesn't arm → no kill, no shadow (shadow is off-path only).
            sig = _short_sig(0.6472, 0.65776414, 0.56, 0.6468)
            _TM()._check_trailing_invalidation(sig)
        finally:
            logger.remove(sink_id)
        assert not any("TRAILING_RSCALE_WOULD_SUPPRESS" in m for m in captured)

    def test_no_shadow_when_telemetry_master_off(self, _flag_off, monkeypatch):
        from loguru import logger
        monkeypatch.setattr("config.DARK_FLAG_SHADOW_TELEMETRY", False)
        captured, sink_id = _capture_logs()
        try:
            sig = _short_sig(0.6472, 0.65776414, 0.56, 0.6468)
            result = _TM()._check_trailing_invalidation(sig)
        finally:
            logger.remove(sink_id)
        assert result is not None  # kill still fires
        assert not any("TRAILING_RSCALE_WOULD_SUPPRESS" in m for m in captured)
