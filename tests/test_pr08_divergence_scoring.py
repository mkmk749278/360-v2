"""PR-08: Divergence scoring refinement.

Verifies that DIVERGENCE_CONTINUATION scoring now reflects the evaluator's
actual CVD-divergence evidence faithfully and that unrelated paths are
unaffected.

Test surface:
1. Evaluator keeps shared smc_data cvd_divergence keys untouched.
2. Evaluator preserves local divergence evidence in signal analyst_reason.
3. Scorer gives DIVERGENCE_CONTINUATION a higher score when divergence
   evidence is present (vs None) — the +4-pt aligned bonus now fires.
4. Divergence strength raises thesis_adj above the base aligned bonus.
5. Unrelated paths (TREND_PULLBACK_CONTINUATION, BREAKOUT_RETEST) are
   unaffected by cvd_divergence_strength.
6. Contra-divergence still yields a negative thesis adjustment.
7. The thesis_adj cap for the order-flow family is respected (≤ 8 pts).
"""

from __future__ import annotations

import pytest

from src.channels.scalp import ScalpChannel
from src.signal_quality import ScoringInput, SignalScoringEngine


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_smc_data(fvg_present: bool = True, cvd: list | None = None) -> dict:
    """Build a minimal smc_data dict for the divergence-continuation evaluator."""
    # Simple FVG zone object substitute (the evaluator only checks truthiness)
    fvg_stub = [{"top": 105.0, "bottom": 100.0, "direction": "BULLISH"}] if fvg_present else []
    if cvd is None:
        cvd = [float(i) for i in range(20)]
    return {
        "fvg": fvg_stub,
        "orderblocks": [],
        "sweeps": [],
        "mss": None,
        "pair_profile": None,
        "regime_context": None,
        "cvd": cvd,
        "funding_rate": None,
    }


def _make_candles_long_divergence(close: float = 100.0) -> dict:
    """Return 5m candles that produce a bullish hidden CVD divergence.

    Price makes a lower low in the later window; CVD makes a higher low.
    """
    n = 25
    closes = [close] * n
    # Late window: lower-low price
    closes[-5] = close * 0.97   # dip below early lows
    highs = [c * 1.002 for c in closes]
    lows = [c * 0.998 for c in closes]
    return {
        "5m": {
            "close": closes,
            "high": highs,
            "low": lows,
            "volume": [1000.0] * n,
        },
    }


def _make_cvd_long_divergence(base: float = 50.0) -> list:
    """CVD that makes a higher low in the late window (absorption signal)."""
    cvd = [base] * 20
    # Early window: lower CVD
    for i in range(2, 7):
        cvd[i] = base - 20.0
    # Late window: CVD recovers (higher low)
    for i in range(12, 17):
        cvd[i] = base - 5.0
    return cvd


def _make_indicators_long(
    ema9: float = 101.5,
    ema21: float = 100.0,
    close: float = 100.0,
) -> dict:
    """Indicators suitable for a LONG DIVERGENCE_CONTINUATION signal."""
    return {
        "5m": {
            "ema9_last": ema9,
            "ema21_last": ema21,
            "rsi_last": 48.0,
            "macd_histogram_last": 0.1,
            "macd_histogram_prev": 0.05,
            "atr_last": close * 0.002,
            "adx_last": 28.0,
        }
    }


def _extract_strength(reason: str) -> float:
    """Extract divergence strength from analyst_reason text."""
    marker = " CVD divergence (strength="
    if marker not in reason or not reason.endswith(")"):
        raise AssertionError(f"Expected strength marker in analyst_reason, got {reason!r}")
    return float(reason.split(marker, 1)[1][:-1])


# ---------------------------------------------------------------------------
# Section 1: Evaluator evidence propagation
# ---------------------------------------------------------------------------

class TestEvaluatorPropagation:
    """The evaluator must preserve divergence details on the signal, not shared smc_data."""

    def _run_long(self, close: float = 100.0):
        """Run _evaluate_divergence_continuation for a LONG setup and return
        (signal, smc_data) so tests can inspect what the evaluator wrote."""
        channel = ScalpChannel()
        cvd = _make_cvd_long_divergence()
        smc = _make_smc_data(cvd=cvd)
        candles = _make_candles_long_divergence(close=close)
        ind = _make_indicators_long(close=close)
        sig = channel._evaluate_divergence_continuation(
            symbol="TESTUSDT",
            candles=candles,
            indicators=ind,
            smc_data=smc,
            spread_pct=0.001,
            volume_24h_usd=50_000_000,
            regime="TRENDING_UP",
        )
        return sig, smc

    def test_long_signal_fires(self):
        """Evaluator fires for a valid LONG divergence setup."""
        sig, _ = self._run_long()
        assert sig is not None, "Expected a signal for valid LONG divergence setup"

    def test_long_preserves_shared_smc_data_divergence_keys(self):
        """Evaluator must not mutate global smc_data divergence keys for LONG."""
        sig, smc = self._run_long()
        if sig is None:
            pytest.skip("Signal did not fire — cannot test propagation")
        assert "cvd_divergence" not in smc
        assert "cvd_divergence_strength" not in smc

    def test_long_sets_analyst_reason_with_label_and_strength(self):
        """Signal analyst_reason includes local divergence label and strength."""
        sig, _ = self._run_long()
        if sig is None:
            pytest.skip("Signal did not fire — cannot test propagation")
        assert sig.analyst_reason is not None
        assert "Hidden BULLISH CVD divergence" in sig.analyst_reason
        strength = _extract_strength(sig.analyst_reason)
        assert strength > 0.0, (
            "Divergence strength must be > 0 when evaluator detects a measurable price dip"
        )
        assert strength <= 1.0, (
            f"Divergence strength must be ≤ 1.0, got {strength}"
        )

    def test_strength_reflects_price_drop_magnitude(self):
        """A larger price drop produces a higher divergence strength."""
        # Close = 100; dip to ~97 → ~3% drop → strength ≈ 1.0
        sig_big, _ = self._run_long(close=100.0)
        if sig_big is None:
            pytest.skip("Big-dip signal did not fire — cannot test magnitude")
        assert sig_big.analyst_reason is not None
        # Smaller dip: build a candle set with only a 1.5% dip
        channel = ScalpChannel()
        close_small = 100.0
        n = 25
        closes_small = [close_small] * n
        closes_small[-5] = close_small * 0.985   # ~1.5% dip
        candles_small = {
            "5m": {
                "close": closes_small,
                "high": [c * 1.002 for c in closes_small],
                "low": [c * 0.998 for c in closes_small],
                "volume": [1000.0] * n,
            }
        }
        smc_small = _make_smc_data(cvd=_make_cvd_long_divergence())
        sig_s = channel._evaluate_divergence_continuation(
            symbol="TESTUSDT",
            candles=candles_small,
            indicators=_make_indicators_long(close=close_small),
            smc_data=smc_small,
            spread_pct=0.001,
            volume_24h_usd=50_000_000,
            regime="TRENDING_UP",
        )
        if sig_s is None:
            pytest.skip("Small-dip signal did not fire — skipping magnitude comparison")
        assert sig_s.analyst_reason is not None
        big_strength = _extract_strength(sig_big.analyst_reason)
        small_strength = _extract_strength(sig_s.analyst_reason)
        assert big_strength >= small_strength, (
            f"Larger price drop should produce >= strength: big={big_strength}, small={small_strength}"
        )

    def test_no_signal_leaves_cvd_divergence_unchanged(self):
        """When the evaluator returns None the smc_data cvd_divergence is not set."""
        channel = ScalpChannel()
        # Wrong regime → evaluator returns None immediately
        smc = _make_smc_data()
        sig = channel._evaluate_divergence_continuation(
            symbol="TESTUSDT",
            candles=_make_candles_long_divergence(),
            indicators=_make_indicators_long(),
            smc_data=smc,
            spread_pct=0.001,
            volume_24h_usd=50_000_000,
            regime="RANGING",          # not TRENDING_UP → early return
        )
        assert sig is None
        # cvd_divergence should not have been written
        assert "cvd_divergence" not in smc or smc.get("cvd_divergence") is None, (
            "smc_data['cvd_divergence'] must not be set when evaluator returns None early"
        )


# ---------------------------------------------------------------------------
# Section 2: Scorer sees the evidence and applies the thesis bonus
# ---------------------------------------------------------------------------

class TestScorerReceivesEvidence:
    """Score for DIVERGENCE_CONTINUATION with cvd_divergence='BULLISH' must
    exceed the score when cvd_divergence is None — the +4-pt bonus now fires."""

    @pytest.fixture
    def engine(self):
        return SignalScoringEngine()

    def _base_inp(self, **overrides):
        defaults = dict(
            setup_class="DIVERGENCE_CONTINUATION",
            direction="LONG",
            regime="TRENDING_UP",
            ema_fast=101.0,
            ema_slow=100.0,
            rsi_last=48.0,
            volume_last_usd=1_200_000,
            volume_avg_usd=1_000_000,
            mtf_score=0.5,
        )
        defaults.update(overrides)
        return ScoringInput(**defaults)

    def test_aligned_cvd_scores_higher_than_none(self, engine):
        """Score with cvd_divergence='BULLISH' (LONG) must exceed score with None."""
        r_with = engine.score(self._base_inp(cvd_divergence="BULLISH"))
        r_none = engine.score(self._base_inp(cvd_divergence=None))
        assert r_with["total"] > r_none["total"], (
            f"DIVERGENCE_CONTINUATION with confirmed CVD ({r_with['total']:.2f}) "
            f"should outscore no-evidence case ({r_none['total']:.2f})"
        )
        assert r_with["thesis_adj"] > 0.0, (
            "thesis_adj must be positive when cvd_divergence is aligned"
        )

    def test_thesis_adj_zero_when_cvd_none(self, engine):
        """When cvd_divergence is None, thesis_adj should be 0 (no OI either)."""
        r = engine.score(self._base_inp(cvd_divergence=None, oi_trend="NEUTRAL"))
        assert r["thesis_adj"] == 0.0, (
            "thesis_adj must be 0 for DIVERGENCE_CONTINUATION with no order-flow evidence"
        )

    def test_strength_raises_thesis_adj_above_base(self, engine):
        """Strong divergence (strength=1.0) must yield higher thesis_adj than
        weak divergence (strength=0.0) given the same aligned CVD label."""
        r_strong = engine.score(self._base_inp(
            cvd_divergence="BULLISH",
            cvd_divergence_strength=1.0,
        ))
        r_weak = engine.score(self._base_inp(
            cvd_divergence="BULLISH",
            cvd_divergence_strength=0.0,
        ))
        assert r_strong["thesis_adj"] > r_weak["thesis_adj"], (
            f"Strong divergence ({r_strong['thesis_adj']}) must beat weak "
            f"divergence ({r_weak['thesis_adj']}) in thesis_adj"
        )

    def test_strength_max_2pt_magnitude_bonus(self, engine):
        """The magnitude bonus must be at most 2 pts (strength=1.0 → +2)."""
        r_strong = engine.score(self._base_inp(
            cvd_divergence="BULLISH",
            cvd_divergence_strength=1.0,
        ))
        r_weak = engine.score(self._base_inp(
            cvd_divergence="BULLISH",
            cvd_divergence_strength=0.0,
        ))
        bonus_delta = r_strong["thesis_adj"] - r_weak["thesis_adj"]
        assert bonus_delta <= 2.0 + 1e-9, (
            f"Magnitude bonus must not exceed 2 pts; got delta = {bonus_delta:.2f}"
        )

    def test_thesis_adj_cap_8(self, engine):
        """thesis_adj for order-flow family must not exceed +8 even at max inputs."""
        r = engine.score(self._base_inp(
            cvd_divergence="BULLISH",
            cvd_divergence_strength=1.0,
            oi_trend="FALLING",
        ))
        assert r["thesis_adj"] <= 8.0, (
            f"thesis_adj cap is 8.0; got {r['thesis_adj']}"
        )

    def test_contra_cvd_still_penalised(self, engine):
        """Contra CVD (BEARISH for LONG) must still produce negative thesis_adj."""
        r = engine.score(self._base_inp(
            direction="LONG",
            cvd_divergence="BEARISH",    # contra
            cvd_divergence_strength=0.5,
        ))
        assert r["thesis_adj"] < 0.0, (
            "Contra CVD must still give a negative thesis adjustment"
        )


# ---------------------------------------------------------------------------
# Section 3: Unrelated paths are unaffected
# ---------------------------------------------------------------------------

class TestUnrelatedPathsUnaffected:
    """cvd_divergence_strength must not accidentally change scores for paths
    outside _FAMILY_ORDER_FLOW_DIVERGENCE."""

    @pytest.fixture
    def engine(self):
        return SignalScoringEngine()

    @pytest.mark.parametrize("setup", [
        "TREND_PULLBACK_CONTINUATION",
        "BREAKOUT_RETEST",
        "SR_FLIP_RETEST",
        "CONTINUATION_LIQUIDITY_SWEEP",
    ])
    def test_unrelated_paths_ignore_strength(self, engine, setup):
        """Score for a non-divergence-family path must be identical regardless
        of cvd_divergence_strength — the field only matters for the
        DIVERGENCE_CONTINUATION family."""
        shared = dict(
            setup_class=setup,
            direction="LONG",
            regime="TRENDING_UP",
            ema_fast=101.0,
            ema_slow=100.0,
            volume_last_usd=1_200_000,
            volume_avg_usd=1_000_000,
            mtf_score=0.5,
            cvd_divergence="BULLISH",   # field present but should not trigger extra bonus
        )
        r_with_strength = engine.score(ScoringInput(cvd_divergence_strength=1.0, **shared))
        r_no_strength = engine.score(ScoringInput(cvd_divergence_strength=0.0, **shared))
        assert r_with_strength["total"] == r_no_strength["total"], (
            f"{setup}: score must not change with cvd_divergence_strength; "
            f"got {r_with_strength['total']} vs {r_no_strength['total']}"
        )

    def test_whale_momentum_unchanged(self, engine):
        """WHALE_MOMENTUM is explicitly excluded from the order-flow family and
        must receive zero thesis_adj regardless of cvd or strength."""
        r = engine.score(ScoringInput(
            setup_class="WHALE_MOMENTUM",
            direction="LONG",
            cvd_divergence="BULLISH",
            cvd_divergence_strength=1.0,
            oi_trend="FALLING",
        ))
        assert r["thesis_adj"] == 0.0, (
            "WHALE_MOMENTUM must have zero thesis_adj (uses shared base scoring)"
        )


# ---------------------------------------------------------------------------
# Section 4: Doctrine alignment — divergence beats generic at equal inputs
# ---------------------------------------------------------------------------

class TestDoctrineAlignment:
    """DIVERGENCE_CONTINUATION with confirmed evidence must outscore an
    evidence-free path when order-flow conditions are set (the whole point of
    path-specific evidence-aligned scoring)."""

    @pytest.fixture
    def engine(self):
        return SignalScoringEngine()

    def test_divergence_with_evidence_beats_generic(self, engine):
        """With aligned CVD and strength, DIVERGENCE_CONTINUATION must outscore
        TREND_PULLBACK_CONTINUATION (which gets zero thesis adjustment)."""
        shared = dict(
            direction="LONG",
            regime="RANGING",            # neutral regime so regime score is equal
            ema_fast=101.0,
            ema_slow=100.0,
            volume_last_usd=1_200_000,
            volume_avg_usd=1_000_000,
            mtf_score=0.5,
            cvd_divergence="BULLISH",
            cvd_divergence_strength=0.5,
        )
        r_div = engine.score(ScoringInput(setup_class="DIVERGENCE_CONTINUATION", **shared))
        r_gen = engine.score(ScoringInput(setup_class="TREND_PULLBACK_CONTINUATION", **shared))
        assert r_div["total"] > r_gen["total"], (
            f"DIVERGENCE_CONTINUATION with evidence ({r_div['total']:.2f}) must outscore "
            f"TREND_PULLBACK_CONTINUATION ({r_gen['total']:.2f}) in identical conditions"
        )
