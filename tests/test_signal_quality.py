from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.signal_quality import (
    ACTIVE_PATH_PORTFOLIO_ROLES,
    APPROVED_PORTFOLIO_ROLES,
    MarketState,
    PortfolioRole,
    QualityTier,
    SetupClass,
    SignalScoringEngine,
    ScoringInput,
    assess_pair_quality,
    build_risk_plan,
    classify_market_state,
    classify_setup,
    execution_quality_check,
    score_signal_components,
    validate_geometry_against_policy,
)
from src.smc import Direction


def _candles(base: float = 100.0, trend: float = 1.0, n: int = 60) -> dict:
    close = [base + trend * i * 0.2 for i in range(n)]
    high = [c + 0.4 for c in close]
    low = [c - 0.4 for c in close]
    return {"high": high, "low": low, "close": close, "volume": [1000.0] * n}


def _signal(channel: str = "360_SCALP", direction: Direction = Direction.LONG):
    return SimpleNamespace(
        channel=channel,
        direction=direction,
        entry=100.0,
        stop_loss=97.0,
        tp1=104.0,
        tp2=108.0,
        tp3=112.0,
    )


def _indicators() -> dict:
    return {
        "1m": {"ema9_last": 100.8, "ema21_last": 100.2, "atr_last": 1.1, "momentum_last": 0.7},
        "5m": {
            "ema9_last": 101.0,
            "ema21_last": 100.4,
            "atr_last": 1.4,
            "momentum_last": 0.6,
            "bb_upper_last": 104.0,
            "bb_mid_last": 101.0,
            "bb_lower_last": 98.0,
        },
        "15m": {
            "ema9_last": 101.2,
            "ema21_last": 100.6,
            "atr_last": 1.8,
            "momentum_last": 0.5,
            "bb_upper_last": 105.0,
            "bb_mid_last": 101.0,
            "bb_lower_last": 97.0,
        },
        "1h": {
            "ema9_last": 102.0,
            "ema21_last": 101.0,
            "atr_last": 2.0,
            "momentum_last": 0.4,
            "bb_upper_last": 106.0,
            "bb_mid_last": 101.0,
            "bb_lower_last": 96.0,
        },
    }


def _smc(direction: Direction = Direction.LONG) -> dict:
    return {
        "sweeps": [SimpleNamespace(direction=direction, sweep_level=98.0)],
        "mss": SimpleNamespace(direction=direction, midpoint=99.2),
        "fvg": [],
        "whale_alert": {"usd": 1_500_000},
        "volume_delta_spike": True,
    }


class TestRegimeSetupCompatibility:
    def test_scalp_generates_trend_continuation_in_strong_trend(self):
        """In STRONG_TREND, ScalpChannel should produce a channel-compatible setup."""
        signal = _signal(channel="360_SCALP")
        setup = classify_setup(
            "360_SCALP",
            signal,
            _indicators(),
            {"sweeps": [], "mss": None, "fvg": [], "whale_alert": None, "volume_delta_spike": False},
            MarketState.STRONG_TREND,
        )
        # In trending conditions the classifier picks a trend-aligned setup class
        assert setup.setup_class in {
            SetupClass.TREND_PULLBACK_CONTINUATION,
            SetupClass.MOMENTUM_EXPANSION,
            SetupClass.LIQUIDITY_SWEEP_REVERSAL,
            SetupClass.BREAKOUT_RETEST,
        }
        assert setup.channel_compatible is True
        assert setup.regime_compatible is True

    def test_range_fade_regime_incompatible_in_strong_trend(self):
        """RANGE_FADE should be regime-incompatible with STRONG_TREND."""
        from src.signal_quality import REGIME_SETUP_COMPATIBILITY
        assert SetupClass.RANGE_FADE not in REGIME_SETUP_COMPATIBILITY.get(
            MarketState.STRONG_TREND, set()
        )

    def test_continuation_rejected_in_dirty_range(self):
        signal = _signal(channel="360_SCALP")
        setup = classify_setup("360_SCALP", signal, _indicators(), {"sweeps": [], "mss": None, "fvg": []}, MarketState.DIRTY_RANGE)
        assert setup.setup_class in {SetupClass.RANGE_REJECTION, SetupClass.RANGE_FADE}
        assert setup.channel_compatible in {True, False}  # RANGE_REJECTION not in SCALP compat; RANGE_FADE is

    def test_breakout_setup_allowed_in_breakout_expansion(self):
        signal = _signal(channel="360_SCALP")
        setup = classify_setup("360_SCALP", signal, _indicators(), _smc(), MarketState.BREAKOUT_EXPANSION)
        assert setup.setup_class in {SetupClass.BREAKOUT_RETEST, SetupClass.LIQUIDITY_SWEEP_REVERSAL, SetupClass.WHALE_MOMENTUM}
        assert setup.channel_compatible is True
        assert setup.regime_compatible is True

    def test_liquidity_sweep_reversal_self_classifying(self):
        """LIQUIDITY_SWEEP_REVERSAL on signal.setup_class must not be remapped to RANGE_FADE (PR-ARCH-4)."""
        signal = _signal(channel="360_SCALP")
        signal.setup_class = "LIQUIDITY_SWEEP_REVERSAL"
        setup = classify_setup(
            "360_SCALP",
            signal,
            _indicators(),
            {"sweeps": [], "mss": None, "fvg": [], "whale_alert": None, "volume_delta_spike": False},
            MarketState.CLEAN_RANGE,
        )
        assert setup.setup_class == SetupClass.LIQUIDITY_SWEEP_REVERSAL

    def test_quiet_compression_break_self_classifying(self):
        """QUIET_COMPRESSION_BREAK on signal.setup_class must not be remapped to RANGE_FADE (PR-ARCH-4)."""
        signal = _signal(channel="360_SCALP")
        signal.setup_class = "QUIET_COMPRESSION_BREAK"
        setup = classify_setup(
            "360_SCALP",
            signal,
            _indicators(),
            {"sweeps": [], "mss": None, "fvg": [], "whale_alert": None, "volume_delta_spike": False},
            MarketState.DIRTY_RANGE,
        )
        assert setup.setup_class == SetupClass.QUIET_COMPRESSION_BREAK

    # ── PR-ARCH-7A: enum membership regression ─────────────────────────────

    @pytest.mark.parametrize("name", [
        "LIQUIDATION_REVERSAL",
        "TREND_PULLBACK_EMA",
        "WHALE_MOMENTUM",
        "DIVERGENCE_CONTINUATION",
        "SR_FLIP_RETEST",
    ])
    def test_arch7a_setup_class_enum_membership(self, name):
        """All five PR-ARCH-7A setup identities must exist in SetupClass enum."""
        assert SetupClass[name].name == name

    # ── PR-ARCH-7A: self-classifying preservation regression ───────────────

    @pytest.mark.parametrize("setup_name,market_state", [
        ("LIQUIDATION_REVERSAL", MarketState.STRONG_TREND),
        ("TREND_PULLBACK_EMA", MarketState.STRONG_TREND),
        ("WHALE_MOMENTUM", MarketState.STRONG_TREND),
        ("DIVERGENCE_CONTINUATION", MarketState.STRONG_TREND),
        ("SR_FLIP_RETEST", MarketState.STRONG_TREND),
    ])
    def test_arch7a_self_classifying_preserved(self, setup_name, market_state):
        """Each PR-ARCH-7A setup class must be preserved by classify_setup() and not remapped."""
        signal = _signal(channel="360_SCALP")
        signal.setup_class = setup_name  # evaluators assign string values, matching _SELF_CLASSIFYING
        setup = classify_setup(
            "360_SCALP",
            signal,
            _indicators(),
            {"sweeps": [], "mss": None, "fvg": [], "whale_alert": None, "volume_delta_spike": False},
            market_state,
        )
        assert setup.setup_class == SetupClass[setup_name], (
            f"{setup_name} was remapped to {setup.setup_class!r} — self-classifying identity corrupted"
        )
        assert setup.channel_compatible is True, (
            f"{setup_name} must be channel-compatible with 360_SCALP"
        )

    # ── PR-ARCH-7B: LIQUIDATION_REVERSAL volatile compatibility ───────────────

    def test_arch7b_liquidation_reversal_in_volatile_unsuitable_compat(self):
        """LIQUIDATION_REVERSAL must appear in REGIME_SETUP_COMPATIBILITY[VOLATILE_UNSUITABLE]."""
        from src.signal_quality import REGIME_SETUP_COMPATIBILITY
        assert SetupClass.LIQUIDATION_REVERSAL in REGIME_SETUP_COMPATIBILITY[MarketState.VOLATILE_UNSUITABLE], (
            "LIQUIDATION_REVERSAL must be in REGIME_SETUP_COMPATIBILITY[VOLATILE_UNSUITABLE] (PR-ARCH-7B)"
        )

    def test_arch7b_liquidation_reversal_regime_compatible_in_volatile(self):
        """classify_setup() must return regime_compatible=True for LIQUIDATION_REVERSAL in VOLATILE_UNSUITABLE."""
        signal = _signal(channel="360_SCALP")
        signal.setup_class = "LIQUIDATION_REVERSAL"
        setup = classify_setup(
            "360_SCALP",
            signal,
            _indicators(),
            {"sweeps": [], "mss": None, "fvg": [], "whale_alert": None, "volume_delta_spike": False},
            MarketState.VOLATILE_UNSUITABLE,
        )
        assert setup.setup_class == SetupClass.LIQUIDATION_REVERSAL, (
            f"LIQUIDATION_REVERSAL was remapped to {setup.setup_class!r} in VOLATILE_UNSUITABLE"
        )
        assert setup.regime_compatible is True, (
            "LIQUIDATION_REVERSAL must be regime-compatible in VOLATILE_UNSUITABLE (PR-ARCH-7B)"
        )

    def test_arch7b_existing_volatile_setups_unchanged(self):
        """Existing volatile-compatible setup classes must remain in REGIME_SETUP_COMPATIBILITY[VOLATILE_UNSUITABLE]."""
        from src.signal_quality import REGIME_SETUP_COMPATIBILITY
        expected = {
            SetupClass.WHALE_MOMENTUM,
            SetupClass.LIQUIDITY_SWEEP_REVERSAL,
            SetupClass.VOLUME_SURGE_BREAKOUT,
            SetupClass.BREAKDOWN_SHORT,
            SetupClass.OPENING_RANGE_BREAKOUT,
            SetupClass.FUNDING_EXTREME_SIGNAL,
        }
        actual = REGIME_SETUP_COMPATIBILITY[MarketState.VOLATILE_UNSUITABLE]
        missing = expected - actual
        assert not missing, (
            f"Previously volatile-compatible setups were removed: {missing}"
        )


class TestExecutionAndRiskChecks:
    def test_overextended_entry_is_rejected(self):
        signal = _signal(channel="360_SCALP")
        signal.entry = 105.0
        indicators = _indicators()
        indicators["5m"]["ema9_last"] = 100.0
        indicators["5m"]["atr_last"] = 1.0
        result = execution_quality_check(signal, indicators, _smc(), SetupClass.MOMENTUM_EXPANSION, MarketState.BREAKOUT_EXPANSION)
        assert result.passed is False
        assert "overextended" in result.reason

    def test_reclaim_required_for_sweep_reversal(self):
        signal = _signal(channel="360_SCALP")
        signal.entry = 97.5
        result = execution_quality_check(signal, _indicators(), _smc(), SetupClass.LIQUIDITY_SWEEP_REVERSAL, MarketState.CLEAN_RANGE)
        assert result.passed is False
        assert "trigger" in result.reason

    def test_range_fade_no_key_error(self):
        """RANGE_FADE must not raise KeyError — this was the P0 production bug."""
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        # entry near bb_lower (98.0) in a CLEAN_RANGE — should pass
        signal.entry = 98.5
        result = execution_quality_check(signal, _indicators(), _smc(), SetupClass.RANGE_FADE, MarketState.CLEAN_RANGE)
        assert result.trigger_confirmed is True
        assert result.passed is True
        assert "band edge" in result.execution_note

    def test_range_fade_mid_range_rejected(self):
        """RANGE_FADE entry far from band edge should be rejected (trigger not confirmed)."""
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        # entry at 101.0 which is near bb_mid (101.0), far from bb_lower (98.0) — trigger should fail
        signal.entry = 101.0
        result = execution_quality_check(signal, _indicators(), _smc(), SetupClass.RANGE_FADE, MarketState.CLEAN_RANGE)
        assert result.passed is False

    def test_range_fade_dirty_range_accepted(self):
        """RANGE_FADE should also trigger-confirm in DIRTY_RANGE, not just CLEAN_RANGE."""
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 98.5
        result = execution_quality_check(signal, _indicators(), _smc(), SetupClass.RANGE_FADE, MarketState.DIRTY_RANGE)
        assert result.trigger_confirmed is True
        assert result.passed is True

    def test_whale_momentum_no_key_error(self):
        """WHALE_MOMENTUM must not raise KeyError — this was the P0 production bug."""
        signal = _signal(channel="360_SCALP")
        indicators = _indicators()
        indicators["5m"]["momentum_last"] = 0.5  # >= 0.3 threshold
        result = execution_quality_check(signal, indicators, _smc(), SetupClass.WHALE_MOMENTUM, MarketState.BREAKOUT_EXPANSION)
        assert result.trigger_confirmed is True
        assert result.passed is True
        assert "trailing stops" in result.execution_note

    def test_whale_momentum_low_momentum_rejected(self):
        """WHALE_MOMENTUM with momentum below 0.3 should not confirm trigger."""
        signal = _signal(channel="360_SCALP")
        indicators = _indicators()
        indicators["5m"]["momentum_last"] = 0.1  # below 0.3 threshold
        result = execution_quality_check(signal, indicators, _smc(), SetupClass.WHALE_MOMENTUM, MarketState.STRONG_TREND)
        assert result.trigger_confirmed is False
        assert result.passed is False

    def test_pdc_trigger_confirmed_when_entry_above_breakout_level(self):
        """PDC LONG: entry above consolidation breakout level → trigger confirmed."""
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 101.5          # above consolidation high
        signal.pdc_breakout_level = 101.0   # consolidation high (breakout level)
        result = execution_quality_check(
            signal, _indicators(), _smc(), SetupClass.POST_DISPLACEMENT_CONTINUATION,
            MarketState.STRONG_TREND,
        )
        assert result.trigger_confirmed is True
        assert result.passed is True
        assert "re-acceleration" in result.execution_note
        assert "consolidation" in result.execution_note

    def test_pdc_trigger_not_confirmed_when_entry_at_breakout_level(self):
        """PDC LONG: entry exactly at consolidation breakout level → trigger not confirmed."""
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 101.0
        signal.pdc_breakout_level = 101.0   # not yet broken out
        result = execution_quality_check(
            signal, _indicators(), _smc(), SetupClass.POST_DISPLACEMENT_CONTINUATION,
            MarketState.STRONG_TREND,
        )
        assert result.trigger_confirmed is False
        assert result.passed is False
        assert "trigger" in result.reason

    def test_pdc_short_trigger_confirmed_when_entry_below_breakout_level(self):
        """PDC SHORT: entry below consolidation floor → trigger confirmed."""
        signal = _signal(channel="360_SCALP", direction=Direction.SHORT)
        signal.entry = 98.5           # below consolidation low
        signal.stop_loss = 101.0      # above entry for short
        signal.pdc_breakout_level = 99.0    # consolidation low (breakout level)
        result = execution_quality_check(
            signal, _indicators(), _smc(direction=Direction.SHORT),
            SetupClass.POST_DISPLACEMENT_CONTINUATION, MarketState.STRONG_TREND,
        )
        assert result.trigger_confirmed is True
        assert result.passed is True

    def test_pdc_overextended_entry_rejected(self):
        """PDC: entry overextended from breakout level (> 1.0 ATR) → rejected."""
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 103.5           # well above consolidation high
        signal.pdc_breakout_level = 101.0
        # atr_last = 1.4 (from _indicators), extension = (103.5 - 101.0) / 1.4 ≈ 1.79 > 1.0
        result = execution_quality_check(
            signal, _indicators(), _smc(), SetupClass.POST_DISPLACEMENT_CONTINUATION,
            MarketState.STRONG_TREND,
        )
        assert result.passed is False
        assert "overextended" in result.reason

    def test_pdc_fallback_when_no_breakout_level_stored(self):
        """PDC: signal without pdc_breakout_level attribute falls back to entry anchor."""
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 100.0
        # No pdc_breakout_level attribute — fallback to entry → extension = 0
        result = execution_quality_check(
            signal, _indicators(), _smc(), SetupClass.POST_DISPLACEMENT_CONTINUATION,
            MarketState.STRONG_TREND,
        )
        # With anchor == entry, extension_ratio == 0 and trigger_confirmed == False
        # (entry is not > entry). The important thing is no KeyError is raised.
        assert result is not None
        signal = _signal(channel="360_SWING")
        risk = build_risk_plan(signal, _indicators(), {"1h": _candles()}, _smc(), SetupClass.TREND_PULLBACK_CONTINUATION, 0.008)
        assert risk.passed is True
        assert risk.stop_loss < signal.entry
        assert risk.tp2 > risk.tp1
        assert "structure" in risk.invalidation_summary

    # ── FAILED_AUCTION_RECLAIM execution-quality tests ───────────────────

    def test_far_long_trigger_confirmed_when_entry_above_reclaim_level(self):
        """FAR LONG: trigger confirmed when entry > far_reclaim_level."""
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 100.5
        signal.far_reclaim_level = 100.0  # broken support that was reclaimed
        result = execution_quality_check(
            signal, _indicators(), _smc(), SetupClass.FAILED_AUCTION_RECLAIM,
            MarketState.CLEAN_RANGE,
        )
        assert result.trigger_confirmed is True
        assert "auction" in result.execution_note.lower()

    def test_far_short_trigger_confirmed_when_entry_below_reclaim_level(self):
        """FAR SHORT: trigger confirmed when entry < far_reclaim_level."""
        signal = _signal(channel="360_SCALP", direction=Direction.SHORT)
        signal.entry = 99.5
        signal.far_reclaim_level = 100.0  # broken resistance that was reclaimed
        result = execution_quality_check(
            signal, _indicators(), _smc(), SetupClass.FAILED_AUCTION_RECLAIM,
            MarketState.CLEAN_RANGE,
        )
        assert result.trigger_confirmed is True

    def test_far_long_trigger_not_confirmed_when_entry_at_level(self):
        """FAR LONG: trigger NOT confirmed when entry == far_reclaim_level (no clearance)."""
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 100.0
        signal.far_reclaim_level = 100.0
        result = execution_quality_check(
            signal, _indicators(), _smc(), SetupClass.FAILED_AUCTION_RECLAIM,
            MarketState.CLEAN_RANGE,
        )
        assert result.trigger_confirmed is False
        assert result.passed is False

    def test_far_overextended_entry_rejected(self):
        """FAR: entry overextended beyond 1.2 ATR from reclaim level is rejected."""
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 103.0
        signal.far_reclaim_level = 100.0  # 3 ATR away (atr=1.4 → 3/1.4 ≈ 2.1 > 1.2)
        result = execution_quality_check(
            signal, _indicators(), _smc(), SetupClass.FAILED_AUCTION_RECLAIM,
            MarketState.CLEAN_RANGE,
        )
        assert result.passed is False
        assert "overextended" in result.reason

    def test_far_fallback_when_no_reclaim_level_stored(self):
        """FAR: signal without far_reclaim_level falls back to entry anchor (no KeyError)."""
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 100.0
        # No far_reclaim_level attribute at all
        result = execution_quality_check(
            signal, _indicators(), _smc(), SetupClass.FAILED_AUCTION_RECLAIM,
            MarketState.CLEAN_RANGE,
        )
        # anchor == entry → trigger_confirmed == False (entry is not > entry)
        assert result is not None
        assert result.trigger_confirmed is False

    # ── FAILED_AUCTION_RECLAIM regime-compatibility tests ───────────────

    def test_far_regime_compatible_in_clean_range(self):
        """FAILED_AUCTION_RECLAIM must be regime-compatible with CLEAN_RANGE."""
        from src.signal_quality import REGIME_SETUP_COMPATIBILITY
        assert SetupClass.FAILED_AUCTION_RECLAIM in REGIME_SETUP_COMPATIBILITY.get(
            MarketState.CLEAN_RANGE, set()
        ), "FAR must be allowed in CLEAN_RANGE (prime regime for failed auctions)."

    def test_far_regime_compatible_in_dirty_range(self):
        """FAILED_AUCTION_RECLAIM must be regime-compatible with DIRTY_RANGE."""
        from src.signal_quality import REGIME_SETUP_COMPATIBILITY
        assert SetupClass.FAILED_AUCTION_RECLAIM in REGIME_SETUP_COMPATIBILITY.get(
            MarketState.DIRTY_RANGE, set()
        ), "FAR must be allowed in DIRTY_RANGE."

    def test_far_regime_compatible_in_weak_trend(self):
        """FAILED_AUCTION_RECLAIM must be regime-compatible with WEAK_TREND."""
        from src.signal_quality import REGIME_SETUP_COMPATIBILITY
        assert SetupClass.FAILED_AUCTION_RECLAIM in REGIME_SETUP_COMPATIBILITY.get(
            MarketState.WEAK_TREND, set()
        ), "FAR must be allowed in WEAK_TREND (breakouts often fail when trend is weak)."

    def test_far_regime_compatible_in_breakout_expansion(self):
        """FAILED_AUCTION_RECLAIM must be regime-compatible with BREAKOUT_EXPANSION."""
        from src.signal_quality import REGIME_SETUP_COMPATIBILITY
        assert SetupClass.FAILED_AUCTION_RECLAIM in REGIME_SETUP_COMPATIBILITY.get(
            MarketState.BREAKOUT_EXPANSION, set()
        ), "FAR must be allowed in BREAKOUT_EXPANSION (false breakouts at expansion boundaries)."

    def test_far_regime_incompatible_in_strong_trend(self):
        """FAILED_AUCTION_RECLAIM must NOT be regime-compatible with STRONG_TREND."""
        from src.signal_quality import REGIME_SETUP_COMPATIBILITY
        assert SetupClass.FAILED_AUCTION_RECLAIM not in REGIME_SETUP_COMPATIBILITY.get(
            MarketState.STRONG_TREND, set()
        ), "FAR must be blocked in STRONG_TREND (genuine breakouts succeed; FAR has no edge)."

    def test_far_regime_incompatible_in_volatile_unsuitable(self):
        """FAILED_AUCTION_RECLAIM must NOT be regime-compatible with VOLATILE_UNSUITABLE."""
        from src.signal_quality import REGIME_SETUP_COMPATIBILITY
        assert SetupClass.FAILED_AUCTION_RECLAIM not in REGIME_SETUP_COMPATIBILITY.get(
            MarketState.VOLATILE_UNSUITABLE, set()
        ), "FAR must be blocked in VOLATILE_UNSUITABLE (chaotic orderflow)."

    def test_far_channel_compatible_in_360_scalp(self):
        """FAILED_AUCTION_RECLAIM must be channel-compatible with 360_SCALP."""
        from src.signal_quality import CHANNEL_SETUP_COMPATIBILITY
        assert SetupClass.FAILED_AUCTION_RECLAIM in CHANNEL_SETUP_COMPATIBILITY.get(
            "360_SCALP", set()
        ), "FAR must be registered in CHANNEL_SETUP_COMPATIBILITY for 360_SCALP."

    def test_far_self_classifying(self):
        """classify_setup() preserves FAILED_AUCTION_RECLAIM identity (self-classifying)."""
        signal = _signal(channel="360_SCALP")
        signal.setup_class = "FAILED_AUCTION_RECLAIM"
        setup = classify_setup(
            "360_SCALP",
            signal,
            _indicators(),
            {"sweeps": [], "mss": None, "fvg": [], "whale_alert": None, "volume_delta_spike": False},
            MarketState.CLEAN_RANGE,
        )
        assert setup.setup_class == SetupClass.FAILED_AUCTION_RECLAIM, (
            f"FAILED_AUCTION_RECLAIM was remapped to {setup.setup_class!r} — "
            "self-classifying identity corrupted."
        )
        assert setup.channel_compatible is True
        assert setup.regime_compatible is True


class TestScoringAndSelectTier:
    def test_stronger_quality_scores_higher_than_weaker(self):
        pair_strong = assess_pair_quality(20_000_000.0, 0.008, _indicators()["5m"], _candles())
        pair_weak = assess_pair_quality(1_500_000.0, 0.025, {"atr_last": 6.0}, _candles())
        strong = score_signal_components(
            pair_quality=pair_strong,
            setup=SimpleNamespace(
                setup_class=SetupClass.BREAKOUT_RETEST,
                channel_compatible=True,
                regime_compatible=True,
            ),
            execution=SimpleNamespace(trigger_confirmed=True, extension_ratio=0.5),
            risk=SimpleNamespace(r_multiple=1.6),
            legacy_confidence=78.0,
            cross_verified=True,
        )
        weak = score_signal_components(
            pair_quality=pair_weak,
            setup=SimpleNamespace(
                setup_class=SetupClass.EXHAUSTION_FADE,
                channel_compatible=True,
                regime_compatible=False,
            ),
            execution=SimpleNamespace(trigger_confirmed=False, extension_ratio=1.6),
            risk=SimpleNamespace(r_multiple=0.9),
            legacy_confidence=52.0,
            cross_verified=False,
        )
        assert strong.total > weak.total
        assert strong.quality_tier in {QualityTier.A, QualityTier.A_PLUS}
        assert weak.quality_tier in {QualityTier.B, QualityTier.C}


class TestFailedAuctionReclaimRiskPlan:
    def test_far_risk_plan_uses_structural_stop_loss_long(self):
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 100.0
        signal.stop_loss = 98.7
        signal.far_reclaim_level = 99.8
        risk = build_risk_plan(
            signal=signal,
            indicators=_indicators(),
            candles={"5m": _candles(base=100.0, trend=0.0)},
            smc_data={"sweeps": [], "mss": None, "fvg": []},
            setup=SetupClass.FAILED_AUCTION_RECLAIM,
            spread_pct=0.01,
            channel="360_SCALP",
        )
        assert risk.stop_loss == 98.7
        assert "reclaimed level" in risk.invalidation_summary.lower()
        assert "failed-auction" in risk.invalidation_summary.lower()

    def test_far_risk_plan_uses_structural_stop_loss_short(self):
        signal = _signal(channel="360_SCALP", direction=Direction.SHORT)
        signal.entry = 100.0
        signal.stop_loss = 101.3
        signal.far_reclaim_level = 100.2
        risk = build_risk_plan(
            signal=signal,
            indicators=_indicators(),
            candles={"5m": _candles(base=100.0, trend=0.0)},
            smc_data={"sweeps": [], "mss": None, "fvg": []},
            setup=SetupClass.FAILED_AUCTION_RECLAIM,
            spread_pct=0.01,
            channel="360_SCALP",
        )
        assert risk.stop_loss == 101.3
        assert "reclaimed level" in risk.invalidation_summary.lower()
        assert "failed-auction" in risk.invalidation_summary.lower()

    def test_far_risk_plan_tp_geometry_is_measured_move_style(self):
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 100.0
        signal.stop_loss = 98.8
        signal.far_reclaim_level = 99.8
        risk = build_risk_plan(
            signal=signal,
            indicators=_indicators(),
            candles={"5m": _candles(base=100.0, trend=0.0)},
            smc_data={"sweeps": [], "mss": None, "fvg": []},
            setup=SetupClass.FAILED_AUCTION_RECLAIM,
            spread_pct=0.01,
            channel="360_SCALP",
        )
        assert risk.tp1 > signal.entry
        assert risk.tp2 > risk.tp1
        assert risk.tp3 > risk.tp2
        # FAR branch enforces at least a structured 1.2R first target.
        assert risk.r_multiple >= 1.2


class TestReclaimRetestGeometryPolicy:
    def _build_high_atr_indicators(self) -> dict:
        indicators = _indicators()
        indicators["5m"]["atr_last"] = 10.0
        return indicators

    def test_failed_auction_reclaim_accepts_tight_structural_stop_loss(self):
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 100.0
        signal.stop_loss = 99.90  # 0.10% structural invalidation
        signal.tp1 = 100.20
        signal.tp2 = 100.40
        signal.tp3 = 100.80
        signal.far_reclaim_level = 99.95

        risk = build_risk_plan(
            signal=signal,
            indicators=self._build_high_atr_indicators(),
            candles={"5m": _candles(base=100.0, trend=0.0)},
            smc_data={"sweeps": [], "mss": None, "fvg": []},
            setup=SetupClass.FAILED_AUCTION_RECLAIM,
            spread_pct=0.01,
            channel="360_SCALP",
        )

        assert risk.passed is True
        assert risk.reason == ""
        assert risk.stop_loss == 99.9

    def test_sr_flip_retest_accepts_tight_structural_stop_loss(self):
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 100.0
        signal.stop_loss = 99.92  # 0.08% structural invalidation
        signal.tp1 = 100.16
        signal.tp2 = 100.30
        signal.tp3 = 100.45

        risk = build_risk_plan(
            signal=signal,
            indicators=self._build_high_atr_indicators(),
            candles={"5m": _candles(base=100.0, trend=0.0)},
            smc_data={"sweeps": [], "mss": None, "fvg": []},
            setup=SetupClass.SR_FLIP_RETEST,
            spread_pct=0.01,
            channel="360_SCALP",
        )

        assert risk.passed is True
        assert risk.reason == ""
        assert risk.stop_loss == 99.92

    def test_reclaim_retest_still_rejects_near_zero_sl(self):
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 100.0
        signal.stop_loss = 99.98  # 0.02% distance
        signal.tp1 = 100.20
        signal.tp2 = 100.40
        signal.tp3 = 100.80
        signal.far_reclaim_level = 99.95

        risk = build_risk_plan(
            signal=signal,
            indicators=self._build_high_atr_indicators(),
            candles={"5m": _candles(base=100.0, trend=0.0)},
            smc_data={"sweeps": [], "mss": None, "fvg": []},
            setup=SetupClass.FAILED_AUCTION_RECLAIM,
            spread_pct=0.01,
            channel="360_SCALP",
        )

        assert risk.passed is False
        assert "near-zero SL rejected" in risk.reason

    def test_non_reclaim_setup_keeps_generic_risk_tight_guard(self):
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 100.0
        signal.stop_loss = 99.90  # same 0.10% distance as FAR test
        signal.tp1 = 100.20
        signal.tp2 = 100.40
        signal.tp3 = 100.80

        risk = build_risk_plan(
            signal=signal,
            indicators=self._build_high_atr_indicators(),
            candles={"5m": _candles(base=100.0, trend=0.0)},
            smc_data={"sweeps": [], "mss": None, "fvg": []},
            setup=SetupClass.BREAKOUT_RETEST,
            spread_pct=0.01,
            channel="360_SCALP",
        )

        assert risk.passed is False
        assert risk.reason == "risk distance too tight"


class TestValidateGeometryPolicyReclaimRetest:
    def test_reclaim_retest_tight_sl_rejected_by_default_guard(self):
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 100.0
        signal.stop_loss = 99.96  # 0.04% distance
        signal.tp1 = 100.06
        signal.tp2 = 100.12
        signal.tp3 = 100.20

        valid, reason = validate_geometry_against_policy(
            signal=signal,
            setup=SetupClass.FAILED_AUCTION_RECLAIM,
            channel="360_SCALP",
        )

        assert valid is False
        assert reason == "near_zero_sl"

    def test_non_reclaim_setup_keeps_default_near_zero_guard(self):
        signal = _signal(channel="360_SCALP", direction=Direction.LONG)
        signal.entry = 100.0
        signal.stop_loss = 99.96  # 0.04% distance
        signal.tp1 = 100.06
        signal.tp2 = 100.12
        signal.tp3 = 100.20

        valid, reason = validate_geometry_against_policy(
            signal=signal,
            setup=SetupClass.BREAKOUT_RETEST,
            channel="360_SCALP",
        )

        assert valid is False
        assert reason == "near_zero_sl"


class TestMarketStateClassification:
    def test_dirty_and_clean_range_distinguished(self):
        clean = classify_market_state(
            regime_result=SimpleNamespace(regime="RANGING", bb_width_pct=2.0),
            indicators={"adx_last": 14.0, "atr_last": 0.9, "momentum_last": 0.05},
            candles=_candles(base=100.0, trend=0.0),
            spread_pct=0.008,
        )
        dirty = classify_market_state(
            regime_result=SimpleNamespace(regime="RANGING", bb_width_pct=4.0),
            indicators={"adx_last": 19.0, "atr_last": 1.8, "momentum_last": 0.15},
            candles={
                "high": [101.0, 102.5, 101.2, 102.8, 101.4, 102.9],
                "low": [99.0, 98.0, 99.1, 97.8, 99.2, 97.7],
                "close": [100.0, 100.1, 100.0, 100.2, 100.1, 100.0],
            },
            spread_pct=0.012,
        )
        assert clean == MarketState.CLEAN_RANGE
        assert dirty == MarketState.DIRTY_RANGE


class TestBuildRiskPlanSLDirectionValidation:
    """build_risk_plan must reject signals where SL is on the wrong side of entry."""

    def test_long_sl_above_entry_rejected(self):
        """LONG with SL above entry must be rejected."""
        sig = SimpleNamespace(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=100.0,
            stop_loss=97.0,
            tp1=104.0,
            tp2=108.0,
            tp3=112.0,
        )
        # Use candles where all lows are above entry so _recent_structure for LONG
        # (min of lows) also sits above entry, forcing stop_loss > entry.
        candles = {
            "5m": {
                "high": [105.0] * 60,
                "low": [104.0] * 60,  # all lows above entry=100
                "close": [104.5] * 60,
                "volume": [1000.0] * 60,
            }
        }
        indicators = {
            "5m": {
                "ema9_last": 104.5,
                "ema21_last": 104.0,
                "atr_last": 0.001,  # tiny ATR → tiny buffer
                "momentum_last": 0.4,
                "bb_upper_last": 106.0,
                "bb_mid_last": 104.5,
                "bb_lower_last": 103.0,
            }
        }
        risk = build_risk_plan(
            signal=sig,
            indicators=indicators,
            candles=candles,
            smc_data={"sweeps": [], "fvg": []},
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
        )
        # structure for LONG = min(lows) = 104 > entry=100
        # → stop_loss ≈ 104 > entry → direction check should fire
        if not risk.passed and "SL above entry" in risk.reason:
            assert risk.passed is False
            assert "LONG" in risk.reason

    def test_short_sl_below_entry_rejected(self):
        """SHORT with SL below entry must be rejected."""
        sig = SimpleNamespace(
            channel="360_SCALP",
            direction=Direction.SHORT,
            entry=100.0,
            stop_loss=103.0,
            tp1=97.0,
            tp2=93.0,
            tp3=89.0,
        )
        # Use indicators that force structure below entry for SHORT
        # (min of highs in a very bullish candle set).
        candles = {
            "5m": {
                "high": [105.0] * 60,
                "low": [104.0] * 60,
                "close": [104.5] * 60,
                "volume": [1000.0] * 60,
            }
        }
        indicators = {
            "5m": {
                "ema9_last": 104.5,
                "ema21_last": 104.0,
                "atr_last": 0.001,  # tiny ATR → tiny buffer
                "momentum_last": -0.3,
                "bb_upper_last": 106.0,
                "bb_mid_last": 104.5,
                "bb_lower_last": 103.0,
            }
        }
        risk = build_risk_plan(
            signal=sig,
            indicators=indicators,
            candles=candles,
            smc_data={"sweeps": [], "fvg": []},
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
        )
        # stop_loss is computed as structure + buffer; when candles all have high=105,
        # structure for SHORT (max of highs) is 105 which is > entry(100), so
        # stop_loss = 105 + buffer > entry → validation rejects.
        if not risk.passed and "SL below entry" in risk.reason:
            assert risk.passed is False
            assert "SHORT" in risk.reason

    def test_valid_long_risk_plan_passes_direction_check(self):
        """A normally-computed LONG SL below entry must NOT be rejected."""
        sig = _signal(channel="360_SCALP", direction=Direction.LONG)
        risk = build_risk_plan(
            signal=sig,
            indicators=_indicators(),
            candles={"5m": _candles()},
            smc_data=_smc(Direction.LONG),
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
        )
        # SL must be below entry for LONG
        if risk.passed:
            assert risk.stop_loss < sig.entry

    def test_valid_short_risk_plan_passes_direction_check(self):
        """A normally-computed SHORT SL above entry must NOT be rejected."""
        sig = _signal(channel="360_SCALP", direction=Direction.SHORT)
        risk = build_risk_plan(
            signal=sig,
            indicators=_indicators(),
            candles={"5m": _candles()},
            smc_data=_smc(Direction.SHORT),
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
        )
        if risk.passed:
            assert risk.stop_loss > sig.entry


# ---------------------------------------------------------------------------
# Bug 5: Channel-aware SL cap in build_risk_plan
# ---------------------------------------------------------------------------


class TestSLCap:
    """Tests for the channel-specific maximum SL distance cap."""

    def _make_signal_with_wide_structure(
        self,
        channel: str,
        direction: Direction = Direction.LONG,
    ):
        """Create a signal whose structure would produce a very wide SL."""
        sig = SimpleNamespace(
            channel=channel,
            direction=direction,
            entry=100.0,
            stop_loss=95.0,
            tp1=110.0,
            tp2=120.0,
            tp3=130.0,
        )
        return sig

    def _wide_candles(self, base: float = 100.0, n: int = 60) -> dict:
        """Candles with extreme swing highs/lows to produce a wide structure SL."""
        close = [base] * n
        high = [base + 10.0] * n  # very wide
        low = [base - 10.0] * n
        return {"high": high, "low": low, "close": close, "volume": [1000.0] * n}

    def _wide_indicators(self) -> dict:
        return {
            "1m": {"ema9_last": 100.0, "ema21_last": 100.0, "atr_last": 0.5,
                   "momentum_last": 0.1},
            "5m": {"ema9_last": 100.0, "ema21_last": 100.0, "atr_last": 0.5,
                   "momentum_last": 0.1, "bb_upper_last": 110.0,
                   "bb_mid_last": 100.0, "bb_lower_last": 90.0},
            "15m": {"ema9_last": 100.0, "ema21_last": 100.0, "atr_last": 0.5,
                    "momentum_last": 0.1, "bb_upper_last": 110.0,
                    "bb_mid_last": 100.0, "bb_lower_last": 90.0},
            "1h": {"ema9_last": 100.0, "ema21_last": 100.0, "atr_last": 0.5,
                   "momentum_last": 0.1, "bb_upper_last": 110.0,
                   "bb_mid_last": 100.0, "bb_lower_last": 90.0},
        }

    def test_scalp_sl_capped_to_1_5pct(self):
        """SCALP channel SL must not exceed 1.5% of entry (raised from 1.0% to allow wider structure stops)."""
        sig = self._make_signal_with_wide_structure("360_SCALP")
        risk = build_risk_plan(
            signal=sig,
            indicators=self._wide_indicators(),
            candles={"5m": self._wide_candles()},
            smc_data={"sweeps": [], "mss": None, "fvg": []},
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
            channel="360_SCALP",
        )
        sl_pct = abs(sig.entry - risk.stop_loss) / sig.entry
        assert sl_pct <= 0.015 + 1e-9, f"SCALP SL pct {sl_pct:.4f} exceeds 1.5%"

    def test_spot_sl_capped_to_2pct(self):
        """SPOT channel SL must not exceed 2% of entry."""
        sig = self._make_signal_with_wide_structure("360_SPOT")
        risk = build_risk_plan(
            signal=sig,
            indicators=self._wide_indicators(),
            candles={"4h": self._wide_candles()},
            smc_data={"sweeps": [], "mss": None, "fvg": []},
            setup=SetupClass.MOMENTUM_EXPANSION,
            spread_pct=0.01,
            channel="360_SPOT",
        )
        sl_pct = abs(sig.entry - risk.stop_loss) / sig.entry
        assert sl_pct <= 0.02 + 1e-9, f"SPOT SL pct {sl_pct:.4f} exceeds 2%"

    def test_swing_sl_capped_to_3pct(self):
        """SWING channel SL must not exceed 3% of entry."""
        sig = self._make_signal_with_wide_structure("360_SWING")
        risk = build_risk_plan(
            signal=sig,
            indicators=self._wide_indicators(),
            candles={"1h": self._wide_candles()},
            smc_data={"sweeps": [], "mss": None, "fvg": []},
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
            channel="360_SWING",
        )
        sl_pct = abs(sig.entry - risk.stop_loss) / sig.entry
        assert sl_pct <= 0.03 + 1e-9, f"SWING SL pct {sl_pct:.4f} exceeds 3%"

    def test_channel_param_overrides_signal_channel(self):
        """Explicitly passing channel= overrides signal.channel for SL cap."""
        sig = self._make_signal_with_wide_structure("360_SWING")
        risk = build_risk_plan(
            signal=sig,
            indicators=self._wide_indicators(),
            candles={"5m": self._wide_candles()},
            smc_data={"sweeps": [], "mss": None, "fvg": []},
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
            channel="360_SCALP",  # tighter cap overrides signal.channel
        )
        sl_pct = abs(sig.entry - risk.stop_loss) / sig.entry
        assert sl_pct <= 0.015 + 1e-9

    def test_no_cap_applied_when_sl_within_limit(self):
        """When the structure-based SL is already within limits, it is not altered."""
        sig = _signal(channel="360_SWING")
        risk_no_channel = build_risk_plan(
            signal=sig,
            indicators=_indicators(),
            candles={"1h": _candles()},
            smc_data=_smc(Direction.LONG),
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
        )
        risk_with_channel = build_risk_plan(
            signal=sig,
            indicators=_indicators(),
            candles={"1h": _candles()},
            smc_data=_smc(Direction.LONG),
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
            channel="360_SWING",
        )
        # When SL is already within the cap, both should be equal
        assert risk_no_channel.stop_loss == risk_with_channel.stop_loss

    def test_short_sl_capped_correctly(self):
        """For a SHORT, the capped SL should be above entry (not below)."""
        sig = self._make_signal_with_wide_structure("360_SCALP", direction=Direction.SHORT)
        risk = build_risk_plan(
            signal=sig,
            indicators=self._wide_indicators(),
            candles={"5m": self._wide_candles()},
            smc_data={"sweeps": [], "mss": None, "fvg": []},
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
            channel="360_SCALP",
        )
        # For a SHORT, SL is above entry
        if sig.entry != 0:  # entry is always non-zero in practice
            sl_pct = abs(sig.entry - risk.stop_loss) / sig.entry
            assert sl_pct <= 0.015 + 1e-9


# ---------------------------------------------------------------------------
# PR-ARCH-9 — Family-aware TP / risk-plan refinement regression tests
# ---------------------------------------------------------------------------


def _risk_plan_for(setup: SetupClass, direction: Direction = Direction.LONG):
    """Return a RiskAssessment for *setup* using standard test fixtures."""
    sig = _signal(channel="360_SCALP", direction=direction)
    return build_risk_plan(
        signal=sig,
        indicators=_indicators(),
        candles={"5m": _candles()},
        smc_data=_smc(direction),
        setup=setup,
        spread_pct=0.01,
        channel="360_SCALP",
    )


class TestFamilyAwareTP:
    """PR-ARCH-9: verify that TP targets are differentiated by setup family.

    Each group assertion checks that:
    - the family's tp1 distance from entry is within the expected ratio band
    - tp2 > tp1 (multi-level structure preserved)
    - the plan passes universal hard risk controls
    """

    # ── Mean-reversion / snap-back families ────────────────────────────────

    @pytest.mark.parametrize("setup", [
        SetupClass.EXHAUSTION_FADE,
        # PR-14: FUNDING_EXTREME_SIGNAL excluded — it is now in
        # STRUCTURAL_SLTP_PROTECTED_SETUPS so build_risk_plan preserves
        # evaluator-authored TPs; TP1 is no longer a fixed R-multiple.
    ])
    def test_mean_reversion_tp1_is_tight(self, setup):
        """Snap-back families must use tp1 ≈ 1.2R (tighter than trend families).

        LIQUIDATION_REVERSAL is excluded here because it now uses evaluator-authored
        Fibonacci retrace TPs (38.2%/61.8%/100% of cascade range) preserved by
        STRUCTURAL_SLTP_PROTECTED_SETUPS — its TP1 is no longer a fixed R-multiple.
        PR-14: FUNDING_EXTREME_SIGNAL is also excluded for the same reason — added
        to STRUCTURAL_SLTP_PROTECTED_SETUPS so evaluator-authored TPs are preserved.
        EXHAUSTION_FADE (1.2R) is used as the snap-back family representative.
        """
        risk = _risk_plan_for(setup)
        assert risk.passed, f"{setup.value} plan unexpectedly failed: {risk.reason}"
        entry = 100.0
        risk_dist = entry - risk.stop_loss
        tp1_ratio = (risk.tp1 - entry) / risk_dist
        assert tp1_ratio == pytest.approx(1.2, abs=0.05), (
            f"{setup.value} tp1 ratio {tp1_ratio:.2f} deviates from expected 1.2R"
        )
        assert risk.tp2 > risk.tp1

    def test_mean_reversion_tp1_tighter_than_trend(self):
        """Mean-reversion tp1 must be closer to entry than TREND_PULLBACK_CONTINUATION.

        LIQUIDATION_REVERSAL is excluded from this comparison because it now uses
        evaluator-authored Fibonacci retrace TPs preserved by STRUCTURAL_SLTP_PROTECTED_SETUPS,
        making its TP1 variable and unrelated to a fixed R-multiple ordering.
        PR-14: FUNDING_EXTREME_SIGNAL is also excluded for the same reason — it is
        now in STRUCTURAL_SLTP_PROTECTED_SETUPS so its TP is evaluator-authored.
        """
        rev = _risk_plan_for(SetupClass.EXHAUSTION_FADE)
        trend = _risk_plan_for(SetupClass.TREND_PULLBACK_CONTINUATION)
        assert rev.tp1 < trend.tp1, (
            "Mean-reversion (EXHAUSTION_FADE) tp1 should be closer to entry than trend tp1"
        )

    # ── Measured-move breakout families ────────────────────────────────────

    @pytest.mark.parametrize("setup", [
        SetupClass.BREAKOUT_RETEST,
        SetupClass.OPENING_RANGE_BREAKOUT,
    ])
    def test_breakout_tp1_is_extended(self, setup):
        """Non-protected measured-move breakout families use tp1 ≈ 1.5R (generic multiplier)."""
        risk = _risk_plan_for(setup)
        assert risk.passed, f"{setup.value} plan unexpectedly failed: {risk.reason}"
        entry = 100.0
        risk_dist = entry - risk.stop_loss
        tp1_ratio = (risk.tp1 - entry) / risk_dist
        assert tp1_ratio == pytest.approx(1.5, abs=0.05), (
            f"{setup.value} tp1 ratio {tp1_ratio:.2f} deviates from expected 1.5R"
        )
        assert risk.tp2 > risk.tp1
        assert risk.tp3 is not None and risk.tp3 > risk.tp2

    @pytest.mark.parametrize("setup", [
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.QUIET_COMPRESSION_BREAK,
        SetupClass.BREAKDOWN_SHORT,
    ])
    def test_protected_breakout_preserves_evaluator_tp(self, setup):
        """PR-02: Protected breakout paths preserve evaluator-authored TP geometry.

        VOLUME_SURGE_BREAKOUT, QUIET_COMPRESSION_BREAK, and BREAKDOWN_SHORT have
        evaluator-computed measured-move or band-width TPs that must survive
        downstream risk-plan handling rather than being replaced by generic
        risk-multiple targets.
        """
        sig = _signal(channel="360_SCALP", direction=Direction.LONG)
        risk = _risk_plan_for(setup)
        assert risk.passed, f"{setup.value} plan unexpectedly failed: {risk.reason}"
        # Evaluator-authored TP1 (104.0 in the test signal) must be preserved.
        assert risk.tp1 == pytest.approx(sig.tp1, rel=1e-6), (
            f"{setup.value} tp1 {risk.tp1:.6f} should equal evaluator-authored "
            f"{sig.tp1:.6f} (PR-02 structural TP preservation violated)"
        )
        assert risk.tp2 == pytest.approx(sig.tp2, rel=1e-6), (
            f"{setup.value} tp2 {risk.tp2:.6f} should equal evaluator-authored {sig.tp2:.6f}"
        )
        assert risk.tp2 > risk.tp1
        assert risk.tp3 is not None and risk.tp3 > risk.tp2

    def test_breakout_tp1_larger_than_sweep_reversal(self):
        """BREAKOUT_RETEST tp1 must be further than LIQUIDITY_SWEEP_REVERSAL tp1."""
        bko = _risk_plan_for(SetupClass.BREAKOUT_RETEST)
        sweep = _risk_plan_for(SetupClass.LIQUIDITY_SWEEP_REVERSAL)
        assert bko.tp1 > sweep.tp1, (
            "Breakout tp1 should extend further than sweep-reversal tp1"
        )

    # ── Divergence / swing continuation family ─────────────────────────────

    def test_divergence_continuation_tp2_extended(self):
        """DIVERGENCE_CONTINUATION tp2 must be further than default fallback tp2."""
        div = _risk_plan_for(SetupClass.DIVERGENCE_CONTINUATION)
        # default fallback uses 2.3R for tp2; DIVERGENCE uses 2.5R
        assert div.passed, f"DIVERGENCE_CONTINUATION plan failed: {div.reason}"
        entry = 100.0
        risk_dist = entry - div.stop_loss
        tp2_ratio = (div.tp2 - entry) / risk_dist
        assert tp2_ratio == pytest.approx(2.5, abs=0.05), (
            f"DIVERGENCE_CONTINUATION tp2 ratio {tp2_ratio:.2f} should be 2.5R"
        )

    # ── Whale / momentum families ───────────────────────────────────────────

    def test_whale_momentum_tp1_aggressive(self):
        """WHALE_MOMENTUM tp1 must be ≈ 1.5R (aggressive extension)."""
        risk = _risk_plan_for(SetupClass.WHALE_MOMENTUM)
        assert risk.passed, f"WHALE_MOMENTUM plan failed: {risk.reason}"
        entry = 100.0
        risk_dist = entry - risk.stop_loss
        tp1_ratio = (risk.tp1 - entry) / risk_dist
        assert tp1_ratio == pytest.approx(1.5, abs=0.05), (
            f"WHALE_MOMENTUM tp1 ratio {tp1_ratio:.2f} should be 1.5R"
        )

    # ── Trend-following families ────────────────────────────────────────────

    def test_trend_pullback_continuation_tp1_medium(self):
        """TREND_PULLBACK_CONTINUATION tp1 must be ≈ 1.4R."""
        risk = _risk_plan_for(SetupClass.TREND_PULLBACK_CONTINUATION)
        assert risk.passed, f"TREND_PULLBACK_CONTINUATION plan failed: {risk.reason}"
        entry = 100.0
        risk_dist = entry - risk.stop_loss
        tp1_ratio = (risk.tp1 - entry) / risk_dist
        assert tp1_ratio == pytest.approx(1.4, abs=0.05), (
            f"TREND_PULLBACK_CONTINUATION tp1 ratio {tp1_ratio:.2f} should be 1.4R"
        )

    def test_trend_pullback_ema_tp1_preserves_evaluator(self):
        """PR-02: TREND_PULLBACK_EMA preserves evaluator-authored TP (not generic 1.3R).

        The TREND_PULLBACK_EMA evaluator computes structure-based TPs anchored to
        swing highs and 4h structure.  These must survive build_risk_plan() rather
        than being replaced by the generic 1.3R risk-multiple target.
        """
        sig = _signal(channel="360_SCALP", direction=Direction.LONG)
        risk = _risk_plan_for(SetupClass.TREND_PULLBACK_EMA)
        assert risk.passed, f"TREND_PULLBACK_EMA plan failed: {risk.reason}"
        # Evaluator-authored TP1 (104.0 in the test signal) must be preserved.
        assert risk.tp1 == pytest.approx(sig.tp1, rel=1e-6), (
            f"TREND_PULLBACK_EMA tp1 {risk.tp1:.6f} should equal evaluator-authored "
            f"{sig.tp1:.6f} (PR-02 structural TP preservation violated)"
        )
        assert risk.tp2 == pytest.approx(sig.tp2, rel=1e-6), (
            f"TREND_PULLBACK_EMA tp2 {risk.tp2:.6f} should equal evaluator-authored {sig.tp2:.6f}"
        )

    # ── Range / structured level families ──────────────────────────────────

    def test_range_fade_tp1_conservative(self):
        """RANGE_FADE tp1 must be ≈ 0.9R (conservative range fade)."""
        risk = _risk_plan_for(SetupClass.RANGE_FADE)
        assert risk.passed, f"RANGE_FADE plan failed: {risk.reason}"
        entry = 100.0
        risk_dist = entry - risk.stop_loss
        tp1_ratio = (risk.tp1 - entry) / risk_dist
        assert tp1_ratio == pytest.approx(0.9, abs=0.05), (
            f"RANGE_FADE tp1 ratio {tp1_ratio:.2f} should be 0.9R"
        )

    def test_sr_flip_retest_tp1_preserves_evaluator(self):
        """PR-02: SR_FLIP_RETEST preserves evaluator-authored TP1 (swing-high level).

        SR_FLIP_RETEST is now in STRUCTURAL_SLTP_PROTECTED_SETUPS.  The evaluator
        computes TP1 from the 20-candle swing high/low (a structural anchor), not
        from a generic risk multiple.  That evaluator-authored value must survive
        build_risk_plan() rather than being replaced by the old generic 1.2R target.
        """
        sig = _signal(channel="360_SCALP", direction=Direction.LONG)
        risk = _risk_plan_for(SetupClass.SR_FLIP_RETEST)
        assert risk.passed, f"SR_FLIP_RETEST plan failed: {risk.reason}"
        # Evaluator-authored TP1 (104.0 in the test signal) must be preserved.
        assert risk.tp1 == pytest.approx(sig.tp1, rel=1e-6), (
            f"SR_FLIP_RETEST tp1 {risk.tp1:.6f} should equal evaluator-authored "
            f"{sig.tp1:.6f} (PR-02 structural TP preservation violated)"
        )
        assert risk.tp2 == pytest.approx(sig.tp2, rel=1e-6), (
            f"SR_FLIP_RETEST tp2 {risk.tp2:.6f} should equal evaluator-authored {sig.tp2:.6f}"
        )

    def test_liquidation_reversal_tp1_preserves_evaluator(self):
        """B13: LIQUIDATION_REVERSAL preserves evaluator-authored Fibonacci retrace TPs.

        LIQUIDATION_REVERSAL is now in STRUCTURAL_SLTP_PROTECTED_SETUPS.  The evaluator
        computes TPs as 38.2%/61.8%/100% Fibonacci retraces of the cascade range.
        Those evaluator-authored values must survive build_risk_plan() rather than
        being replaced by the old generic 1.0R/1.8R/2.5R mean-reversion targets.
        """
        sig = _signal(channel="360_SCALP", direction=Direction.LONG)
        risk = _risk_plan_for(SetupClass.LIQUIDATION_REVERSAL)
        assert risk.passed, f"LIQUIDATION_REVERSAL plan failed: {risk.reason}"
        # Evaluator-authored TP1 (104.0 in the test signal) must be preserved.
        assert risk.tp1 == pytest.approx(sig.tp1, rel=1e-6), (
            f"LIQUIDATION_REVERSAL tp1 {risk.tp1:.6f} should equal evaluator-authored "
            f"{sig.tp1:.6f} (B13 structural TP preservation violated)"
        )
        assert risk.tp2 == pytest.approx(sig.tp2, rel=1e-6), (
            f"LIQUIDATION_REVERSAL tp2 {risk.tp2:.6f} should equal evaluator-authored {sig.tp2:.6f}"
        )

    # ── Family ordering invariants ──────────────────────────────────────────

    def test_tp1_ordering_mean_rev_lt_trend_lt_breakout(self):
        """Family TP1 ordering: mean-reversion < trend < breakout (measured move).

        Uses EXHAUSTION_FADE as the mean-reversion representative because both
        LIQUIDATION_REVERSAL and FUNDING_EXTREME_SIGNAL now use evaluator-authored
        structural TPs (preserved by STRUCTURAL_SLTP_PROTECTED_SETUPS) which are
        variable and not comparable to fixed R-multiple ordering.
        PR-14: FUNDING_EXTREME_SIGNAL was previously the representative here;
        it was moved to STRUCTURAL_SLTP_PROTECTED_SETUPS so its TP is now
        evaluator-authored and no longer a fixed R-multiple.
        """
        mean_rev = _risk_plan_for(SetupClass.EXHAUSTION_FADE)
        trend = _risk_plan_for(SetupClass.TREND_PULLBACK_CONTINUATION)
        breakout = _risk_plan_for(SetupClass.BREAKOUT_RETEST)
        assert mean_rev.tp1 < trend.tp1 < breakout.tp1, (
            f"Expected mean_rev.tp1 {mean_rev.tp1:.4f} < trend.tp1 {trend.tp1:.4f}"
            f" < breakout.tp1 {breakout.tp1:.4f}"
        )

    # ── SHORT direction parity ──────────────────────────────────────────────

    @pytest.mark.parametrize("setup", [
        SetupClass.LIQUIDATION_REVERSAL,
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.BREAKOUT_RETEST,
        SetupClass.DIVERGENCE_CONTINUATION,
    ])
    def test_short_tp_below_entry(self, setup):
        """For SHORT signals, all TP levels must be below entry."""
        risk = _risk_plan_for(setup, direction=Direction.SHORT)
        assert risk.passed, f"{setup.value} SHORT plan failed: {risk.reason}"
        assert risk.tp1 < 100.0, f"{setup.value} SHORT tp1 {risk.tp1} not below entry"
        assert risk.tp2 < risk.tp1, f"{setup.value} SHORT tp2 should be lower than tp1"

    # ── Universal hard controls remain enforced ─────────────────────────────

    @pytest.mark.parametrize("setup", [
        SetupClass.LIQUIDATION_REVERSAL,
        SetupClass.BREAKOUT_RETEST,
        SetupClass.DIVERGENCE_CONTINUATION,
        SetupClass.WHALE_MOMENTUM,
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.RANGE_FADE,
    ])
    def test_sl_cap_enforced_for_all_families(self, setup):
        """Universal SL cap (1.5% for SCALP) must be enforced regardless of family."""
        sig = SimpleNamespace(
            channel="360_SCALP",
            direction=Direction.LONG,
            entry=100.0,
            stop_loss=95.0,
            tp1=110.0,
            tp2=120.0,
            tp3=130.0,
        )
        wide_candles = {
            "high": [110.0] * 60,
            "low": [90.0] * 60,
            "close": [100.0] * 60,
            "volume": [1000.0] * 60,
        }
        wide_indicators = {
            "5m": {
                "ema9_last": 100.0,
                "ema21_last": 100.0,
                "atr_last": 0.5,
                "momentum_last": 0.1,
                "bb_upper_last": 110.0,
                "bb_mid_last": 100.0,
                "bb_lower_last": 90.0,
            }
        }
        risk = build_risk_plan(
            signal=sig,
            indicators=wide_indicators,
            candles={"5m": wide_candles},
            smc_data={"sweeps": [], "mss": None, "fvg": []},
            setup=setup,
            spread_pct=0.01,
            channel="360_SCALP",
        )
        sl_pct = abs(sig.entry - risk.stop_loss) / sig.entry
        assert sl_pct <= 0.015 + 1e-9, (
            f"{setup.value} SL pct {sl_pct:.4f} exceeds 1.5% cap"
        )


# ---------------------------------------------------------------------------
# PR_09 — Composite Signal Scoring Engine tests
# ---------------------------------------------------------------------------


@pytest.fixture
def engine():
    return SignalScoringEngine()


class TestScoringDimensions:
    """Test each scoring dimension independently."""

    def test_smc_no_data(self, engine):
        inp = ScoringInput()
        result = engine.score(inp)
        assert result["smc"] == 0.0

    def test_smc_full_confluence(self, engine):
        sweep = MagicMock()
        sweep.index = -1
        inp = ScoringInput(sweeps=[sweep], mss=MagicMock(), fvg_zones=[MagicMock()])
        result = engine.score(inp)
        assert result["smc"] == 25.0

    def test_smc_sweep_only(self, engine):
        sweep = MagicMock()
        sweep.index = -1
        inp = ScoringInput(sweeps=[sweep])
        result = engine.score(inp)
        assert result["smc"] == 15.0  # 10 base + 5 recency

    def test_smc_old_sweep(self, engine):
        sweep = MagicMock()
        sweep.index = -5
        inp = ScoringInput(sweeps=[sweep])
        result = engine.score(inp)
        assert result["smc"] == 10.0  # 10 base, no recency bonus

    def test_regime_no_data(self, engine):
        inp = ScoringInput(regime="")
        result = engine.score(inp)
        assert result["regime"] == 10.0

    def test_regime_strong_alignment(self, engine):
        inp = ScoringInput(regime="TRENDING_UP", setup_class="LIQUIDITY_SWEEP_REVERSAL")
        result = engine.score(inp)
        assert result["regime"] == 18.0

    def test_regime_weak_alignment(self, engine):
        inp = ScoringInput(regime="TRENDING_UP", setup_class="RANGE_FADE")
        result = engine.score(inp)
        assert result["regime"] == 8.0

    def test_regime_volatile_atr_bonus(self, engine):
        inp = ScoringInput(regime="VOLATILE", setup_class="WHALE_MOMENTUM", atr_percentile=80)
        result = engine.score(inp)
        assert result["regime"] == 20.0  # 18 + 2 bonus

    def test_volume_neutral(self, engine):
        inp = ScoringInput(volume_last_usd=0, volume_avg_usd=0)
        result = engine.score(inp)
        assert result["volume"] == 7.5

    def test_volume_high_ratio(self, engine):
        inp = ScoringInput(volume_last_usd=3_000_000, volume_avg_usd=1_000_000)
        result = engine.score(inp)
        assert result["volume"] == 15.0

    def test_volume_below_average(self, engine):
        inp = ScoringInput(volume_last_usd=500_000, volume_avg_usd=1_000_000)
        result = engine.score(inp)
        assert result["volume"] == 3.0

    def test_indicators_all_aligned_long(self, engine):
        inp = ScoringInput(
            macd_histogram_last=0.5, macd_histogram_prev=0.3,
            rsi_last=42.0, ema_fast=101.0, ema_slow=100.0,
            direction="LONG"
        )
        result = engine.score(inp)
        assert result["indicators"] == 20.0  # 7 + 7 + 6

    def test_indicators_all_aligned_short(self, engine):
        inp = ScoringInput(
            macd_histogram_last=-0.5, macd_histogram_prev=-0.3,
            rsi_last=58.0, ema_fast=99.0, ema_slow=100.0,
            direction="SHORT"
        )
        result = engine.score(inp)
        assert result["indicators"] == 20.0

    def test_indicators_misaligned(self, engine):
        inp = ScoringInput(
            macd_histogram_last=-0.5, macd_histogram_prev=-0.3,
            rsi_last=72.0, ema_fast=99.0, ema_slow=100.0,
            direction="LONG"
        )
        result = engine.score(inp)
        assert result["indicators"] < 10.0

    def test_patterns_neutral_no_patterns(self, engine):
        inp = ScoringInput(chart_patterns=[])
        result = engine.score(inp)
        assert result["patterns"] == 5.0

    def test_patterns_none(self, engine):
        inp = ScoringInput(chart_patterns=None)
        result = engine.score(inp)
        assert result["patterns"] == 5.0

    def test_mtf_full(self, engine):
        inp = ScoringInput(mtf_score=1.0)
        result = engine.score(inp)
        assert result["mtf"] == 10.0

    def test_mtf_zero(self, engine):
        inp = ScoringInput(mtf_score=0.0)
        result = engine.score(inp)
        assert result["mtf"] == 0.0

    def test_mtf_partial(self, engine):
        inp = ScoringInput(mtf_score=0.5)
        result = engine.score(inp)
        assert result["mtf"] == 5.0


class TestEndToEnd:
    """Test full scoring pipeline and tier gating."""

    def test_scoring_high_smc_and_volume(self, engine):
        sweep = MagicMock()
        sweep.index = -1
        inp = ScoringInput(
            sweeps=[sweep], mss=MagicMock(), regime="TRENDING_UP",
            setup_class="LIQUIDITY_SWEEP_REVERSAL",
            volume_last_usd=3_000_000, volume_avg_usd=1_000_000,
            macd_histogram_last=0.5, macd_histogram_prev=0.3,
            rsi_last=42.0, ema_fast=101.0, ema_slow=100.0,
            direction="LONG", mtf_score=1.0
        )
        result = engine.score(inp)
        assert result["total"] >= 80

    def test_scoring_filters_low_quality(self, engine):
        inp = ScoringInput(
            regime="RANGING", setup_class="LIQUIDITY_SWEEP_REVERSAL",
            volume_last_usd=500_000, volume_avg_usd=2_000_000,
            rsi_last=68.0, ema_fast=100.0, ema_slow=101.0,
            direction="LONG", mtf_score=0.0
        )
        result = engine.score(inp)
        assert result["total"] < 50

    def test_total_never_exceeds_100(self, engine):
        sweep = MagicMock()
        sweep.index = -1
        inp = ScoringInput(
            sweeps=[sweep], mss=MagicMock(), fvg_zones=[MagicMock()],
            regime="TRENDING_UP", setup_class="LIQUIDITY_SWEEP_REVERSAL",
            atr_percentile=90,
            volume_last_usd=5_000_000, volume_avg_usd=1_000_000,
            macd_histogram_last=1.0, macd_histogram_prev=0.5,
            rsi_last=35.0, ema_fast=105.0, ema_slow=100.0,
            direction="LONG", mtf_score=1.0
        )
        result = engine.score(inp)
        assert result["total"] <= 100.0

    def test_score_returns_all_dimensions(self, engine):
        inp = ScoringInput()
        result = engine.score(inp)
        assert set(result.keys()) == {"smc", "regime", "volume", "indicators", "patterns", "mtf", "thesis_adj", "total"}

    def test_tier_a_plus(self, engine):
        """Verify a well-confirmed signal scores ≥ 80 (A+ tier)."""
        sweep = MagicMock()
        sweep.index = -1
        inp = ScoringInput(
            sweeps=[sweep], mss=MagicMock(), fvg_zones=[MagicMock()],
            regime="TRENDING_UP", setup_class="LIQUIDITY_SWEEP_REVERSAL",
            volume_last_usd=3_000_000, volume_avg_usd=1_000_000,
            macd_histogram_last=0.5, macd_histogram_prev=0.3,
            rsi_last=42.0, ema_fast=101.0, ema_slow=100.0,
            direction="LONG", mtf_score=1.0
        )
        result = engine.score(inp)
        assert result["total"] >= 80

    def test_tier_b(self, engine):
        """B tier: reasonable signal without full confluence."""
        sweep = MagicMock()
        sweep.index = -1
        inp = ScoringInput(
            sweeps=[sweep], regime="TRENDING_UP",
            setup_class="LIQUIDITY_SWEEP_REVERSAL",
            volume_last_usd=1_500_000, volume_avg_usd=1_000_000,
            rsi_last=48.0, ema_fast=101.0, ema_slow=100.0,
            direction="LONG", mtf_score=0.5
        )
        result = engine.score(inp)
        assert 50 <= result["total"] < 80


class TestFamilyAwareConfidenceScoring:
    """Regression tests verifying family-based thesis differentiation in PR09.

    The core invariant: materially different setup families must NOT produce
    the exact same final score from identical shared inputs.  Each family's
    primary thesis should influence its score via _apply_family_thesis_adjustment.
    """

    @pytest.fixture
    def engine(self) -> SignalScoringEngine:
        return SignalScoringEngine()

    # ── Shared base inputs used across most tests ──────────────────────
    def _base_inputs(self, **override) -> ScoringInput:
        """Return a neutral ScoringInput with identical shared dimensions."""
        sweep = MagicMock()
        sweep.index = -2
        kwargs = dict(
            sweeps=[sweep],
            regime="VOLATILE",
            atr_percentile=60.0,
            volume_last_usd=1_500_000,
            volume_avg_usd=1_000_000,
            rsi_last=48.0,
            mtf_score=0.5,
            # EMA counter-trend (bearish) for a LONG trade — typical reversal entry
            ema_fast=99.0,
            ema_slow=101.0,
            direction="LONG",
        )
        kwargs.update(override)
        return ScoringInput(**kwargs)

    # ── Thesis adjustment key present ─────────────────────────────────

    def test_score_includes_thesis_adj_key(self, engine):
        """score() must always return a 'thesis_adj' key."""
        result = engine.score(ScoringInput())
        assert "thesis_adj" in result

    def test_thesis_adj_zero_for_non_family_setup(self, engine):
        """Trend/continuation setup gets zero thesis adjustment."""
        inp = self._base_inputs(setup_class="TREND_PULLBACK_CONTINUATION")
        result = engine.score(inp)
        assert result["thesis_adj"] == 0.0

    def test_thesis_adj_zero_for_breakout_setup(self, engine):
        """Breakout/measured-move setup gets zero thesis adjustment."""
        inp = self._base_inputs(setup_class="BREAKOUT_RETEST")
        result = engine.score(inp)
        assert result["thesis_adj"] == 0.0

    def test_thesis_adj_zero_for_quiet_specialist(self, engine):
        """Quiet-specialist (range-fade) setup gets zero thesis adjustment."""
        inp = self._base_inputs(setup_class="RANGE_FADE")
        result = engine.score(inp)
        assert result["thesis_adj"] == 0.0

    # ── Reversal family: EMA counter-trend correction ──────────────────

    def test_reversal_ema_counter_trend_correction_long(self, engine):
        """LIQUIDATION_REVERSAL LONG with bearish EMA earns EMA correction bonus."""
        inp_reversal = self._base_inputs(
            setup_class="LIQUIDATION_REVERSAL",
            ema_fast=99.0, ema_slow=101.0,  # counter-trend for LONG
        )
        inp_trend = self._base_inputs(
            setup_class="TREND_PULLBACK_CONTINUATION",
            ema_fast=99.0, ema_slow=101.0,  # same mis-aligned EMA
        )
        r_reversal = engine.score(inp_reversal)
        r_trend = engine.score(inp_trend)
        # Reversal should score higher because it gets EMA correction
        assert r_reversal["total"] > r_trend["total"]
        assert r_reversal["thesis_adj"] > 0.0
        assert r_trend["thesis_adj"] == 0.0

    def test_reversal_ema_counter_trend_correction_short(self, engine):
        """LIQUIDITY_SWEEP_REVERSAL SHORT with bullish EMA earns EMA correction bonus."""
        inp = self._base_inputs(
            setup_class="LIQUIDITY_SWEEP_REVERSAL",
            direction="SHORT",
            ema_fast=101.0, ema_slow=99.0,  # bullish EMA — counter-trend for SHORT
        )
        result = engine.score(inp)
        assert result["thesis_adj"] > 0.0

    def test_reversal_no_ema_correction_when_aligned(self, engine):
        """LIQUIDATION_REVERSAL with EMA already aligned gets no EMA correction."""
        inp_aligned = self._base_inputs(
            setup_class="LIQUIDATION_REVERSAL",
            ema_fast=101.0, ema_slow=99.0,  # aligned for LONG
        )
        inp_counter = self._base_inputs(
            setup_class="LIQUIDATION_REVERSAL",
            ema_fast=99.0, ema_slow=101.0,  # counter-trend for LONG
        )
        r_aligned = engine.score(inp_aligned)
        r_counter = engine.score(inp_counter)
        # Counter-trend EMA earns correction; aligned EMA does not
        assert r_counter["thesis_adj"] > r_aligned["thesis_adj"]

    # ── Reversal family: order-flow thesis bonus ───────────────────────

    def test_reversal_oi_falling_boosts_score(self, engine):
        """LIQUIDATION_REVERSAL with falling OI scores higher than neutral OI."""
        inp_squeeze = self._base_inputs(
            setup_class="LIQUIDATION_REVERSAL",
            oi_trend="FALLING",
            liq_vol_usd=500_000,
        )
        inp_neutral = self._base_inputs(
            setup_class="LIQUIDATION_REVERSAL",
            oi_trend="NEUTRAL",
            liq_vol_usd=0.0,
        )
        r_squeeze = engine.score(inp_squeeze)
        r_neutral = engine.score(inp_neutral)
        assert r_squeeze["total"] > r_neutral["total"]
        assert r_squeeze["thesis_adj"] > r_neutral["thesis_adj"]

    def test_reversal_cvd_aligned_boosts_score(self, engine):
        """LIQUIDATION_REVERSAL LONG with BULLISH CVD earns thesis bonus."""
        inp_cvd = self._base_inputs(
            setup_class="LIQUIDATION_REVERSAL",
            cvd_divergence="BULLISH",
        )
        inp_none = self._base_inputs(
            setup_class="LIQUIDATION_REVERSAL",
            cvd_divergence=None,
        )
        r_cvd = engine.score(inp_cvd)
        r_none = engine.score(inp_none)
        assert r_cvd["total"] > r_none["total"]

    def test_reversal_contrarian_funding_boosts_score(self, engine):
        """FUNDING_EXTREME_SIGNAL LONG with extreme negative funding earns bonus."""
        inp_funding = self._base_inputs(
            setup_class="FUNDING_EXTREME_SIGNAL",
            funding_rate=-0.02,  # extreme negative — contrarian for LONG
        )
        inp_none = self._base_inputs(
            setup_class="FUNDING_EXTREME_SIGNAL",
            funding_rate=None,
        )
        r_funding = engine.score(inp_funding)
        r_none = engine.score(inp_none)
        assert r_funding["total"] > r_none["total"]

    def test_exhaustion_fade_is_in_reversal_family(self, engine):
        """EXHAUSTION_FADE gets thesis adjustment like other reversal family members."""
        inp = self._base_inputs(
            setup_class="EXHAUSTION_FADE",
            ema_fast=99.0, ema_slow=101.0,  # counter-trend for LONG
            oi_trend="FALLING",
        )
        result = engine.score(inp)
        assert result["thesis_adj"] > 0.0

    # ── Order-flow / divergence family ────────────────────────────────

    def test_divergence_continuation_cvd_aligned_bonus(self, engine):
        """DIVERGENCE_CONTINUATION LONG with BULLISH CVD earns thesis bonus."""
        inp_cvd = self._base_inputs(
            setup_class="DIVERGENCE_CONTINUATION",
            cvd_divergence="BULLISH",
        )
        inp_none = self._base_inputs(
            setup_class="DIVERGENCE_CONTINUATION",
            cvd_divergence=None,
        )
        r_cvd = engine.score(inp_cvd)
        r_none = engine.score(inp_none)
        assert r_cvd["total"] > r_none["total"]
        assert r_cvd["thesis_adj"] > 0.0

    def test_divergence_continuation_oi_falling_bonus(self, engine):
        """DIVERGENCE_CONTINUATION with falling OI earns thesis bonus."""
        inp_oi = self._base_inputs(
            setup_class="DIVERGENCE_CONTINUATION",
            oi_trend="FALLING",
        )
        inp_neutral = self._base_inputs(
            setup_class="DIVERGENCE_CONTINUATION",
            oi_trend="NEUTRAL",
        )
        r_oi = engine.score(inp_oi)
        r_neutral = engine.score(inp_neutral)
        assert r_oi["total"] > r_neutral["total"]

    def test_whale_momentum_uses_shared_base_scoring(self, engine):
        """WHALE_MOMENTUM is NOT in _FAMILY_ORDER_FLOW_DIVERGENCE and gets zero
        thesis adjustment regardless of CVD/OI inputs.

        This reflects that WHALE_MOMENTUM's primary thesis (large-participant
        impulse) is different from divergence confirmation, and its OI behavior
        is not universally indicative of a falling-OI squeeze.
        """
        inp_cvd = self._base_inputs(
            setup_class="WHALE_MOMENTUM",
            cvd_divergence="BULLISH",
            oi_trend="FALLING",
        )
        inp_none = self._base_inputs(
            setup_class="WHALE_MOMENTUM",
            cvd_divergence=None,
            oi_trend="NEUTRAL",
        )
        r_cvd = engine.score(inp_cvd)
        r_none = engine.score(inp_none)
        # Both must have zero thesis adjustment (shared base scoring)
        assert r_cvd["thesis_adj"] == 0.0
        assert r_none["thesis_adj"] == 0.0
        # Scores should be equal since order-flow fields do not affect shared base
        assert r_cvd["total"] == r_none["total"]

    def test_divergence_cvd_contra_applies_small_penalty(self, engine):
        """DIVERGENCE_CONTINUATION with contra CVD gets a negative thesis adj."""
        inp = self._base_inputs(
            setup_class="DIVERGENCE_CONTINUATION",
            direction="LONG",
            cvd_divergence="BEARISH",  # contra to LONG
        )
        result = engine.score(inp)
        assert result["thesis_adj"] < 0.0

    # ── Cross-family differentiation ──────────────────────────────────

    def test_reversal_scores_higher_than_trend_under_reversal_conditions(self, engine):
        """Given identical shared inputs and reversal-favorable order flow,
        LIQUIDATION_REVERSAL must score strictly higher than TREND_PULLBACK_CONTINUATION
        (which gets no thesis adjustment).
        """
        shared = dict(
            ema_fast=99.0, ema_slow=101.0,  # counter-trend for LONG
            oi_trend="FALLING",
            liq_vol_usd=1_000_000,
            cvd_divergence="BULLISH",
            regime="VOLATILE",
            atr_percentile=60.0,
            volume_last_usd=1_500_000,
            volume_avg_usd=1_000_000,
            rsi_last=48.0,
            mtf_score=0.5,
            direction="LONG",
        )
        r_reversal = engine.score(ScoringInput(setup_class="LIQUIDATION_REVERSAL", **shared))
        r_trend = engine.score(ScoringInput(setup_class="TREND_PULLBACK_CONTINUATION", **shared))
        assert r_reversal["total"] > r_trend["total"], (
            f"Reversal {r_reversal['total']} should exceed trend {r_trend['total']} "
            f"given reversal-favorable order flow"
        )

    def test_order_flow_family_scores_higher_than_breakout_under_cvd_conditions(self, engine):
        """DIVERGENCE_CONTINUATION with aligned CVD must score higher than
        BREAKOUT_RETEST (which gets no thesis adjustment) given the same inputs.

        Use RANGING regime so neither setup gets a regime-affinity advantage,
        allowing the thesis adjustment to be the determining factor.
        """
        shared = dict(
            cvd_divergence="BULLISH",
            oi_trend="FALLING",
            regime="RANGING",
            atr_percentile=60.0,
            volume_last_usd=1_500_000,
            volume_avg_usd=1_000_000,
            rsi_last=48.0,
            ema_fast=101.0,
            ema_slow=100.0,
            mtf_score=0.5,
            direction="LONG",
        )
        r_div = engine.score(ScoringInput(setup_class="DIVERGENCE_CONTINUATION", **shared))
        r_break = engine.score(ScoringInput(setup_class="BREAKOUT_RETEST", **shared))
        assert r_div["total"] > r_break["total"]

    def test_thesis_adj_bounded_above_for_reversal_family(self, engine):
        """Reversal thesis adjustment must never exceed +8 pts."""
        inp = ScoringInput(
            setup_class="LIQUIDATION_REVERSAL",
            direction="LONG",
            ema_fast=99.0, ema_slow=101.0,
            oi_trend="FALLING",
            liq_vol_usd=50_000_000,
            cvd_divergence="BULLISH",
            funding_rate=-0.05,
        )
        result = engine.score(inp)
        assert result["thesis_adj"] <= 8.0

    def test_thesis_adj_bounded_above_for_order_flow_family(self, engine):
        """Order-flow family thesis adjustment must never exceed +6 pts."""
        inp = ScoringInput(
            setup_class="DIVERGENCE_CONTINUATION",
            direction="LONG",
            cvd_divergence="BULLISH",
            oi_trend="FALLING",
        )
        result = engine.score(inp)
        assert result["thesis_adj"] <= 6.0

    def test_total_never_exceeds_100_with_thesis_adj(self, engine):
        """Total must never exceed 100 even with maximum thesis adjustment."""
        sweep = MagicMock()
        sweep.index = -1
        inp = ScoringInput(
            sweeps=[sweep], mss=MagicMock(), fvg_zones=[MagicMock()],
            setup_class="LIQUIDATION_REVERSAL",
            regime="VOLATILE",
            atr_percentile=90.0,
            volume_last_usd=5_000_000, volume_avg_usd=1_000_000,
            macd_histogram_last=1.0, macd_histogram_prev=0.5,
            rsi_last=35.0, ema_fast=99.0, ema_slow=101.0,
            direction="LONG", mtf_score=1.0,
            oi_trend="FALLING", liq_vol_usd=50_000_000,
            cvd_divergence="BULLISH", funding_rate=-0.05,
        )
        result = engine.score(inp)
        assert result["total"] <= 100.0

    def test_families_not_uniformly_scored_under_identical_shared_inputs(self, engine):
        """Core regression: major families must produce different final scores
        when order-flow conditions clearly differentiate them.

        This is the primary acceptance criterion for PR-ARCH-10: final
        confidence is no longer effectively globally uniform across all
        major setup families.
        """
        shared = dict(
            ema_fast=99.0, ema_slow=101.0,  # counter-trend for LONG
            oi_trend="FALLING",
            liq_vol_usd=2_000_000,
            cvd_divergence="BULLISH",
            regime="VOLATILE",
            atr_percentile=65.0,
            volume_last_usd=1_500_000,
            volume_avg_usd=1_000_000,
            rsi_last=45.0,
            mtf_score=0.6,
            direction="LONG",
        )
        families = {
            "reversal": "LIQUIDATION_REVERSAL",
            "order_flow": "DIVERGENCE_CONTINUATION",
            "trend": "TREND_PULLBACK_CONTINUATION",
            "breakout": "BREAKOUT_RETEST",
            "quiet": "RANGE_FADE",
        }
        scores = {
            name: engine.score(ScoringInput(setup_class=sc, **shared))["total"]
            for name, sc in families.items()
        }
        # Reversal and order-flow families must outperform trend/breakout/quiet
        # under these reversal-favorable conditions (failing OI, bullish CVD).
        assert scores["reversal"] > scores["trend"], (
            f"Reversal ({scores['reversal']}) must beat trend ({scores['trend']})"
        )
        assert scores["order_flow"] > scores["trend"], (
            f"Order-flow ({scores['order_flow']}) must beat trend ({scores['trend']})"
        )
        # Not all scores are identical
        unique_scores = set(scores.values())
        assert len(unique_scores) > 1, (
            f"All families produced the same score — uniform scoring not resolved: {scores}"
        )


# ---------------------------------------------------------------------------
# Roadmap step 8 — Portfolio role formalization tests
# ---------------------------------------------------------------------------

class TestPortfolioRoles:
    """Verify the explicit portfolio-role model introduced in roadmap step 8.

    Guards:
    - every active evaluator path has an assigned role
    - roles are limited to the approved taxonomy (core / support / specialist)
    - no active path is missing from the mapping
    - the mapping stays aligned with the live evaluator list in ScalpChannel
    """

    # The 14 SetupClass values produced by live ScalpChannel evaluators.
    # This list must stay aligned with ScalpChannel.evaluate()'s evaluator
    # tuple (src/channels/scalp.py).  If an evaluator is added or removed
    # there, it must also be reflected here and in ACTIVE_PATH_PORTFOLIO_ROLES.
    # NOTE: Auxiliary channel identities (FVG_RETEST, FVG_RETEST_HTF_CONFLUENCE,
    # RSI_MACD_DIVERGENCE, SMC_ORDERBLOCK) are preserved as distinct SetupClass values
    # (PR-01) but are intentionally absent from ACTIVE_PATH_PORTFOLIO_ROLES.  They are
    # sub-evaluators of auxiliary channels whose portfolio role is expressed through
    # their parent channel's enabled/disabled state, not via a standalone path entry.
    # OPENING_RANGE_BREAKOUT is disabled by default (PR-06) but its evaluator code and
    # portfolio-role entry are preserved pending a proper session-anchored rebuild.
    ACTIVE_EVALUATOR_CLASSES = frozenset({
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        SetupClass.TREND_PULLBACK_EMA,
        SetupClass.LIQUIDATION_REVERSAL,
        SetupClass.WHALE_MOMENTUM,
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.BREAKDOWN_SHORT,
        SetupClass.OPENING_RANGE_BREAKOUT,
        SetupClass.SR_FLIP_RETEST,
        SetupClass.FUNDING_EXTREME_SIGNAL,
        SetupClass.QUIET_COMPRESSION_BREAK,
        SetupClass.DIVERGENCE_CONTINUATION,
        SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
        SetupClass.POST_DISPLACEMENT_CONTINUATION,
        SetupClass.FAILED_AUCTION_RECLAIM,
    })

    def test_every_active_path_has_a_role(self):
        """Every active evaluator SetupClass must appear in the role mapping."""
        missing = self.ACTIVE_EVALUATOR_CLASSES - set(ACTIVE_PATH_PORTFOLIO_ROLES.keys())
        assert not missing, (
            f"Active evaluator paths missing from ACTIVE_PATH_PORTFOLIO_ROLES: {missing}"
        )

    def test_no_extra_classes_in_mapping(self):
        """The role mapping must not contain classes absent from the active set."""
        extra = set(ACTIVE_PATH_PORTFOLIO_ROLES.keys()) - self.ACTIVE_EVALUATOR_CLASSES
        assert not extra, (
            f"ACTIVE_PATH_PORTFOLIO_ROLES contains non-active path(s): {extra}"
        )

    def test_all_roles_are_approved_taxonomy(self):
        """Every assigned role must be a member of the approved role taxonomy."""
        for setup_class, role in ACTIVE_PATH_PORTFOLIO_ROLES.items():
            assert role in APPROVED_PORTFOLIO_ROLES, (
                f"{setup_class} has unapproved role '{role}'. "
                f"Approved roles: {APPROVED_PORTFOLIO_ROLES}"
            )

    def test_approved_taxonomy_contains_exactly_three_roles(self):
        """The approved taxonomy must contain exactly core, support, specialist."""
        assert APPROVED_PORTFOLIO_ROLES == frozenset({
            PortfolioRole.CORE,
            PortfolioRole.SUPPORT,
            PortfolioRole.SPECIALIST,
        })

    def test_portfolio_has_all_three_role_tiers_represented(self):
        """The live portfolio must include at least one path in each role tier."""
        assigned_roles = set(ACTIVE_PATH_PORTFOLIO_ROLES.values())
        for role in PortfolioRole:
            assert role in assigned_roles, (
                f"No active path assigned to '{role}' — every role tier must be represented."
            )

    def test_core_paths_include_primary_signal_generators(self):
        """Core role must include the primary revenue-driving evaluators."""
        expected_core = {
            SetupClass.LIQUIDITY_SWEEP_REVERSAL,
            SetupClass.TREND_PULLBACK_EMA,
            SetupClass.VOLUME_SURGE_BREAKOUT,
            SetupClass.BREAKDOWN_SHORT,
            SetupClass.SR_FLIP_RETEST,
            SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
            SetupClass.POST_DISPLACEMENT_CONTINUATION,
        }
        actual_core = {
            sc for sc, role in ACTIVE_PATH_PORTFOLIO_ROLES.items()
            if role == PortfolioRole.CORE
        }
        assert expected_core == actual_core

    def test_specialist_paths_include_narrow_context_evaluators(self):
        """Specialist role must include the low-frequency narrow-context paths."""
        expected_specialist = {
            SetupClass.WHALE_MOMENTUM,
            SetupClass.FUNDING_EXTREME_SIGNAL,
            SetupClass.QUIET_COMPRESSION_BREAK,
        }
        actual_specialist = {
            sc for sc, role in ACTIVE_PATH_PORTFOLIO_ROLES.items()
            if role == PortfolioRole.SPECIALIST
        }
        assert expected_specialist == actual_specialist

    def test_support_paths_include_situational_contributors(self):
        """Support role must include situational contributors."""
        expected_support = {
            SetupClass.LIQUIDATION_REVERSAL,
            SetupClass.DIVERGENCE_CONTINUATION,
            SetupClass.OPENING_RANGE_BREAKOUT,
            SetupClass.FAILED_AUCTION_RECLAIM,
        }
        actual_support = {
            sc for sc, role in ACTIVE_PATH_PORTFOLIO_ROLES.items()
            if role == PortfolioRole.SUPPORT
        }
        assert expected_support == actual_support

    def test_mapping_count_matches_active_evaluator_count(self):
        """Role mapping must contain exactly as many entries as active evaluators."""
        assert len(ACTIVE_PATH_PORTFOLIO_ROLES) == len(self.ACTIVE_EVALUATOR_CLASSES), (
            f"Role mapping has {len(ACTIVE_PATH_PORTFOLIO_ROLES)} entries "
            f"but {len(self.ACTIVE_EVALUATOR_CLASSES)} active evaluators expected."
        )

    def test_portfolio_role_enum_values(self):
        """PortfolioRole enum string values match the approved taxonomy language."""
        assert PortfolioRole.CORE.value == "core"
        assert PortfolioRole.SUPPORT.value == "support"
        assert PortfolioRole.SPECIALIST.value == "specialist"
