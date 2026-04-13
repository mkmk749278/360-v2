"""PR-15: Soft-penalty-after-scoring interaction fix — focused regression tests.

Bug fixed: In _prepare_signal(), sig.soft_penalty_total stores both evaluator-authored
quality penalties (E) and scanner-gate penalties (S).  Before this fix, only S was
deducted from sig.confidence after the composite scoring engine ran; E was recorded
in soft_penalty_total but never applied.  Additionally, sig.signal_tier was set by
the scoring engine (pre-penalty) and never updated, so WATCHLIST/floor decisions were
evaluated on stale pre-penalty tier values.

Fix applied (src/scanner/__init__.py):
1. Deduct sig.soft_penalty_total (E+S) instead of soft_penalty (S only) after scoring.
2. Re-classify sig.signal_tier after full penalty so downstream gates use true tier.

Tests in this file prove:
- A signal that only passes the confidence floor before evaluator penalties are applied
  is correctly rejected after the fix.
- A signal whose evaluator-authored penalties reduce it below the WATCHLIST floor
  (confidence < 50) is handled correctly — not kept as WATCHLIST based on stale tier.
- A signal with no evaluator-authored penalties (only scanner-gate penalties) behaves
  identically to the pre-fix behaviour (unaffected case).
"""

from __future__ import annotations

import contextlib
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.channels.base import Signal
from src.regime import MarketRegime
from src.scanner import Scanner
from src.signal_quality import (
    ExecutionAssessment,
    RiskAssessment,
    SetupAssessment,
    SetupClass,
)
from src.smc import Direction
from src.utils import utcnow


# ---------------------------------------------------------------------------
# Shared helpers — intentionally minimal, mirroring test_regime_soft_penalty.py
# ---------------------------------------------------------------------------

def _candles(length: int = 40) -> dict:
    base = [float(i + 1) for i in range(length)]
    return {
        "high": base,
        "low": [max(v - 0.5, 0.1) for v in base],
        "close": base,
        "volume": [100.0 for _ in base],
    }


def _make_signal(
    *,
    channel: str = "360_SCALP",
    confidence: float = 10.0,
    soft_penalty_total: float = 0.0,
) -> Signal:
    sig = Signal(
        channel=channel,
        symbol="BTCUSDT",
        direction=Direction.LONG,
        entry=100.0,
        stop_loss=95.0,
        tp1=105.0,
        tp2=110.0,
        confidence=confidence,
        signal_id="SIG-PR15-001",
        timestamp=utcnow(),
    )
    sig.soft_penalty_total = soft_penalty_total
    return sig


def _make_scanner(**kwargs) -> Scanner:
    signal_queue = MagicMock()
    signal_queue.put = AsyncMock(return_value=True)
    router_mock = MagicMock(active_signals={})
    router_mock.cleanup_expired.return_value = 0
    defaults = dict(
        pair_mgr=MagicMock(),
        data_store=MagicMock(),
        channels=[],
        smc_detector=MagicMock(),
        regime_detector=MagicMock(),
        predictive=MagicMock(),
        exchange_mgr=MagicMock(),
        spot_client=None,
        telemetry=MagicMock(),
        signal_queue=signal_queue,
        router=router_mock,
    )
    defaults.update(kwargs)
    return Scanner(**defaults)


def _setup_pass() -> SetupAssessment:
    return SetupAssessment(
        setup_class=SetupClass.BREAKOUT_RETEST,
        thesis="Breakout Retest",
        channel_compatible=True,
        regime_compatible=True,
    )


def _execution_pass() -> ExecutionAssessment:
    return ExecutionAssessment(
        passed=True,
        trigger_confirmed=True,
        extension_ratio=0.6,
        anchor_price=99.0,
        entry_zone="99.0000 – 100.0000",
        execution_note="Retest hold confirmed.",
    )


def _risk_pass() -> RiskAssessment:
    return RiskAssessment(
        passed=True,
        stop_loss=95.0,
        tp1=106.5,
        tp2=111.5,
        tp3=117.0,
        r_multiple=1.3,
        invalidation_summary="Below 96.0000 structure + volatility buffer",
    )


def _make_scan_ready_scanner(
    *,
    channel: MagicMock,
    signal_queue: MagicMock,
    regime: MarketRegime = MarketRegime.TRENDING_UP,
) -> Scanner:
    smc_result = SimpleNamespace(
        sweeps=[SimpleNamespace(direction=Direction.LONG, sweep_level=95.0)],
        fvg=[],
        mss=SimpleNamespace(direction=Direction.LONG, midpoint=98.0),
        as_dict=lambda: {
            "sweeps": [SimpleNamespace(direction=Direction.LONG, sweep_level=95.0)],
            "fvg": [],
            "mss": SimpleNamespace(direction=Direction.LONG, midpoint=98.0),
        },
    )
    predictive = MagicMock(
        predict=AsyncMock(
            return_value=SimpleNamespace(
                confidence_adjustment=0.0,
                predicted_direction="NEUTRAL",
                suggested_tp_adjustment=1.0,
                suggested_sl_adjustment=1.0,
            )
        ),
        adjust_tp_sl=MagicMock(),
        update_confidence=MagicMock(),
    )
    return _make_scanner(
        pair_mgr=MagicMock(has_enough_history=MagicMock(return_value=True)),
        data_store=MagicMock(
            get_candles=MagicMock(side_effect=lambda _symbol, _interval: _candles()),
            ticks={"BTCUSDT": []},
        ),
        channels=[channel],
        smc_detector=MagicMock(detect=MagicMock(return_value=smc_result)),
        regime_detector=MagicMock(
            classify=MagicMock(return_value=SimpleNamespace(regime=regime))
        ),
        predictive=predictive,
        exchange_mgr=MagicMock(
            verify_signal_cross_exchange=AsyncMock(return_value=True)
        ),
        spot_client=MagicMock(),
        signal_queue=signal_queue,
        router=MagicMock(active_signals={}, cleanup_expired=MagicMock(return_value=0)),
        onchain_client=MagicMock(get_exchange_flow=AsyncMock(return_value=None)),
    )


def _common_patches(scanner, extra=None):
    """Return ExitStack with standard pipeline patches (no gate fires by default)."""
    stack = contextlib.ExitStack()
    stack.enter_context(
        patch("src.scanner.compute_confidence", return_value=SimpleNamespace(total=70.0, blocked=False))
    )
    stack.enter_context(patch("src.scanner.check_vwap_extension", return_value=(True, "")))
    stack.enter_context(patch("src.scanner.check_kill_zone_gate", return_value=(True, "")))
    stack.enter_context(patch.object(scanner, "_evaluate_setup", return_value=_setup_pass()))
    stack.enter_context(patch.object(scanner, "_evaluate_execution", return_value=_execution_pass()))
    stack.enter_context(patch.object(scanner, "_evaluate_risk", return_value=_risk_pass()))
    for p in (extra or []):
        stack.enter_context(p)
    return stack


# ---------------------------------------------------------------------------
# PR-15 tests
# ---------------------------------------------------------------------------

class TestEvaluatorPenaltiesAppliedPostScoring:
    """Evaluator-authored soft_penalty_total must be deducted after the composite
    scoring engine assigns its score — not silently recorded and ignored."""

    @pytest.mark.asyncio
    async def test_signal_only_passes_before_evaluator_penalty_is_rejected(self):
        """A signal whose composite score clears the min_confidence floor but whose
        evaluator-authored penalty would push it below the floor must be rejected.

        Without the PR-15 fix:
        - scoring engine assigns confidence = 82 → A+ tier, passes min_conf = 80
        - evaluator soft_penalty_total = 15 is recorded but NOT deducted
        - signal is accepted with inflated confidence 82

        After the PR-15 fix:
        - evaluator soft_penalty_total = 15 is deducted from 82 → 67
        - 67 < min_conf (80) → signal is rejected
        """
        import src.scanner as scanner_mod

        eval_soft_penalty = 15.0  # set by the evaluator on the signal
        pr09_score = {
            "smc": 22.0, "regime": 18.0, "volume": 14.0,
            "indicators": 14.0, "patterns": 7.0, "mtf": 7.0,
            "total": 82.0,  # A+ tier, clears 80 floor before penalty
        }

        channel = MagicMock()
        # min_confidence=80 mirrors the real 360_SCALP config — A+ bar.
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=80.0)
        # Evaluator-authored signal carries evaluator-level quality penalty.
        channel.evaluate.return_value = _make_signal(soft_penalty_total=eval_soft_penalty)
        sq = MagicMock()
        sq.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(
            channel=channel, signal_queue=sq, regime=MarketRegime.TRENDING_UP
        )

        with _common_patches(scanner, extra=[
            patch.object(scanner_mod._scoring_engine, "score", return_value=pr09_score),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Signal must be rejected — post-penalty confidence (82 - 15 = 67) < min_conf (80).
        sq.put.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_evaluator_penalty_reduces_confidence_to_correct_value(self):
        """When an evaluator-authored penalty exists and the signal survives all gates,
        the final confidence must equal composite_score − soft_penalty_total (E+S).

        Setup: evaluator penalty E=10, no scanner gate fires (S=0).
        Composite score = 80.  Expected final confidence = 80 − 10 = 70.
        Channel min_confidence=10 so the signal survives all downstream gates.
        """
        import src.scanner as scanner_mod

        eval_soft_penalty = 10.0
        pr09_score = {
            "smc": 22.0, "regime": 18.0, "volume": 12.0,
            "indicators": 18.0, "patterns": 5.0, "mtf": 5.0,
            "total": 80.0,
        }

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(soft_penalty_total=eval_soft_penalty)
        sq = MagicMock()
        captured: dict = {}

        async def _capture(sig):
            captured["sig"] = sig
            return True

        sq.put = AsyncMock(side_effect=_capture)
        scanner = _make_scan_ready_scanner(
            channel=channel, signal_queue=sq, regime=MarketRegime.TRENDING_UP
        )

        with _common_patches(scanner, extra=[
            patch.object(scanner_mod._scoring_engine, "score", return_value=pr09_score),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        sig = captured.get("sig")
        assert sig is not None, "Signal should survive with min_confidence=10"
        # PR-15: both E and S must be reflected in confidence reduction.
        assert sig.confidence == pytest.approx(80.0 - eval_soft_penalty, abs=0.2), (
            f"Expected confidence 80 - {eval_soft_penalty} = {80 - eval_soft_penalty}, "
            f"got {sig.confidence}"
        )
        assert sig.soft_penalty_total == pytest.approx(eval_soft_penalty, abs=0.2)

    @pytest.mark.asyncio
    async def test_evaluator_and_scanner_penalties_both_deducted(self):
        """When both evaluator (E) and scanner-gate (S) penalties are present,
        the final confidence deduction must equal E + S.

        E=10 (evaluator quality), S=15 (VWAP scanner gate), total=25.
        Composite score = 82.  Expected final confidence = 82 − 25 = 57.
        """
        import src.scanner as scanner_mod

        eval_soft_penalty = 10.0  # E: evaluator-authored
        # S: VWAP fires for 360_SCALP in RANGING regime → 15 × 1.0 = 15
        pr09_score = {
            "smc": 22.0, "regime": 18.0, "volume": 14.0,
            "indicators": 14.0, "patterns": 7.0, "mtf": 7.0,
            "total": 82.0,
        }

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(soft_penalty_total=eval_soft_penalty)
        sq = MagicMock()
        captured: dict = {}

        async def _capture(sig):
            captured["sig"] = sig
            return True

        sq.put = AsyncMock(side_effect=_capture)
        scanner = _make_scan_ready_scanner(
            channel=channel, signal_queue=sq, regime=MarketRegime.RANGING
        )

        with _common_patches(scanner, extra=[
            patch("src.scanner.check_vwap_extension", return_value=(False, "VWAP: overextended")),
            patch.object(scanner_mod._scoring_engine, "score", return_value=pr09_score),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        sig = captured.get("sig")
        assert sig is not None, "Signal should survive with min_confidence=10"
        # Total deduction = E + S = 10 + 15 = 25
        expected_confidence = 82.0 - 25.0
        assert sig.confidence == pytest.approx(expected_confidence, abs=0.5), (
            f"Expected 82 - (10+15) = {expected_confidence}, got {sig.confidence}"
        )
        # Consistency check: final ≈ score − soft_penalty_total
        assert sig.confidence == pytest.approx(82.0 - sig.soft_penalty_total, abs=0.5)


class TestEvaluatorPenaltyFloorHandling:
    """Evaluator-authored penalties that push confidence below the WATCHLIST floor
    must cause rejection, not incorrect WATCHLIST acceptance on a stale tier."""

    @pytest.mark.asyncio
    async def test_evaluator_penalty_below_watchlist_floor_rejects_signal(self):
        """A signal scoring in WATCHLIST range (50-64) whose evaluator-authored penalty
        pushes it below 50 must be rejected — it must not survive as WATCHLIST based
        on the stale pre-penalty tier from the scoring engine.

        Without the PR-15 fix:
        - scoring engine: score=55 → tier="WATCHLIST"
        - evaluator soft_penalty_total=8 is NOT deducted
        - sig.confidence stays 55, sig.signal_tier stays "WATCHLIST"
        - WATCHLIST branch fires → signal accepted (BUG)

        After the PR-15 fix:
        - 8 pts deducted → confidence = 47
        - tier re-classified: classify_signal_tier(47) = "FILTERED"
        - WATCHLIST branch: "FILTERED" ≠ "WATCHLIST" → skipped
        - final confidence < min_conf → rejected (CORRECT)
        """
        import src.scanner as scanner_mod

        eval_soft_penalty = 8.0
        # Score places the signal in WATCHLIST range before penalty.
        pr09_score = {
            "smc": 12.0, "regime": 10.0, "volume": 8.0,
            "indicators": 10.0, "patterns": 8.0, "mtf": 7.0,
            "total": 55.0,  # WATCHLIST tier (50-64) from scoring engine
        }

        channel = MagicMock()
        # min_confidence=50 is the WATCHLIST floor; post-penalty confidence (47) must
        # fall below it.  Without the PR-15 fix the signal was kept as WATCHLIST (stale
        # tier) even though its true confidence is below 50.
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=50.0)
        channel.evaluate.return_value = _make_signal(soft_penalty_total=eval_soft_penalty)
        sq = MagicMock()
        sq.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(
            channel=channel, signal_queue=sq, regime=MarketRegime.TRENDING_UP
        )

        with _common_patches(scanner, extra=[
            patch.object(scanner_mod._scoring_engine, "score", return_value=pr09_score),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Post-penalty confidence = 55 - 8 = 47 < 50 → must not be kept as WATCHLIST.
        sq.put.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_tier_reclassified_after_penalty(self):
        """After evaluator + scanner penalties are applied, sig.signal_tier must reflect
        the post-penalty confidence, not the pre-penalty scoring-engine tier.

        Setup:
        - scoring engine: score=82 → tier="A+"
        - evaluator penalty E=10, no scanner penalty S=0 → total=10
        - Post-penalty confidence = 72 → classify_signal_tier(72) = "B"
        - Channel min_confidence=10 so the signal survives all gates.
        """
        import src.scanner as scanner_mod

        eval_soft_penalty = 10.0
        pr09_score = {
            "smc": 22.0, "regime": 18.0, "volume": 14.0,
            "indicators": 14.0, "patterns": 7.0, "mtf": 7.0,
            "total": 82.0,
        }

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(soft_penalty_total=eval_soft_penalty)
        sq = MagicMock()
        captured: dict = {}

        async def _capture(sig):
            captured["sig"] = sig
            return True

        sq.put = AsyncMock(side_effect=_capture)
        scanner = _make_scan_ready_scanner(
            channel=channel, signal_queue=sq, regime=MarketRegime.TRENDING_UP
        )

        with _common_patches(scanner, extra=[
            patch.object(scanner_mod._scoring_engine, "score", return_value=pr09_score),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        sig = captured.get("sig")
        assert sig is not None
        # Confidence = 82 - 10 = 72 → tier must be re-classified to "B".
        assert sig.confidence == pytest.approx(72.0, abs=0.2)
        assert sig.signal_tier == "B", (
            f"Expected tier 'B' for post-penalty confidence 72, got '{sig.signal_tier}'"
        )


class TestUnaffectedCases:
    """Cases where no evaluator-authored penalties exist must behave identically
    to the pre-fix behaviour (scanner-gate-only penalty path is unchanged)."""

    @pytest.mark.asyncio
    async def test_no_penalty_signal_passes_unchanged(self):
        """A signal with zero evaluator and zero scanner penalties keeps the exact
        composite score as its final confidence."""
        import src.scanner as scanner_mod

        pr09_score = {
            "smc": 22.0, "regime": 18.0, "volume": 14.0,
            "indicators": 14.0, "patterns": 7.0, "mtf": 7.0,
            "total": 82.0,
        }

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        # No evaluator penalty set (default soft_penalty_total=0).
        channel.evaluate.return_value = _make_signal()
        sq = MagicMock()
        captured: dict = {}

        async def _capture(sig):
            captured["sig"] = sig
            return True

        sq.put = AsyncMock(side_effect=_capture)
        scanner = _make_scan_ready_scanner(
            channel=channel, signal_queue=sq, regime=MarketRegime.TRENDING_UP
        )

        with _common_patches(scanner, extra=[
            patch.object(scanner_mod._scoring_engine, "score", return_value=pr09_score),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        sig = captured.get("sig")
        assert sig is not None
        assert sig.confidence == pytest.approx(82.0, abs=0.2), (
            "Zero-penalty signal must retain the composite score as final confidence"
        )
        assert sig.soft_penalty_total == pytest.approx(0.0, abs=0.01)

    @pytest.mark.asyncio
    async def test_scanner_only_penalty_still_applied_correctly(self):
        """When only scanner-gate penalties (S) are present and E=0, the final
        confidence must equal composite_score − S, unchanged from pre-fix behaviour.

        VWAP fires in RANGING regime: 360_SCALP weight 15 × mult 1.0 = 15.
        Score=75 → expected confidence = 75 − 15 = 60.
        """
        import src.scanner as scanner_mod

        pr09_score = {
            "smc": 20.0, "regime": 15.0, "volume": 10.0,
            "indicators": 15.0, "patterns": 8.0, "mtf": 7.0,
            "total": 75.0,
        }

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        # No evaluator penalty (E=0).
        channel.evaluate.return_value = _make_signal()
        sq = MagicMock()
        captured: dict = {}

        async def _capture(sig):
            captured["sig"] = sig
            return True

        sq.put = AsyncMock(side_effect=_capture)
        scanner = _make_scan_ready_scanner(
            channel=channel, signal_queue=sq, regime=MarketRegime.RANGING
        )

        with _common_patches(scanner, extra=[
            patch("src.scanner.check_vwap_extension", return_value=(False, "VWAP: overextended")),
            patch.object(scanner_mod._scoring_engine, "score", return_value=pr09_score),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        sig = captured.get("sig")
        assert sig is not None, "Signal must be enqueued (penalty reduces but does not kill it)"
        assert sig.confidence == pytest.approx(60.0, abs=0.2), (
            "Scanner-only penalty must still reduce confidence by the gate amount"
        )
        assert sig.soft_penalty_total == pytest.approx(15.0, abs=0.2)
        assert "VWAP" in sig.soft_gate_flags
