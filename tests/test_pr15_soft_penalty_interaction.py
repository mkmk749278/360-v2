"""PR-15: Soft-penalty-after-scoring interaction — focused regression tests.

Four tests proving the exact fix:
1. Evaluator-authored penalty is actually deducted from confidence after scoring.
2. Total penalty (evaluator + scanner) is used, not scanner-local only.
3. sig.signal_tier is re-classified after final penalty.
4. Stale WATCHLIST acceptance does not survive when evaluator penalty drops
   confidence below the WATCHLIST floor.
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
# Helpers
# ---------------------------------------------------------------------------

def _candles(length: int = 40) -> dict:
    base = [float(i + 1) for i in range(length)]
    return {
        "high": base,
        "low": [max(v - 0.5, 0.1) for v in base],
        "close": base,
        "volume": [100.0 for _ in base],
    }


def _make_signal(*, soft_penalty_total: float = 0.0) -> Signal:
    sig = Signal(
        channel="360_SCALP",
        symbol="BTCUSDT",
        direction=Direction.LONG,
        entry=100.0,
        stop_loss=95.0,
        tp1=105.0,
        tp2=110.0,
        confidence=10.0,
        signal_id="SIG-PR15",
        timestamp=utcnow(),
    )
    sig.soft_penalty_total = soft_penalty_total
    return sig


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
    signal_queue_default = MagicMock()
    signal_queue_default.put = AsyncMock(return_value=True)
    return Scanner(
        pair_mgr=MagicMock(has_enough_history=MagicMock(return_value=True)),
        data_store=MagicMock(
            get_candles=MagicMock(side_effect=lambda _s, _i: _candles()),
            ticks={"BTCUSDT": []},
        ),
        channels=[channel],
        smc_detector=MagicMock(detect=MagicMock(return_value=smc_result)),
        regime_detector=MagicMock(
            classify=MagicMock(return_value=SimpleNamespace(regime=regime))
        ),
        predictive=predictive,
        exchange_mgr=MagicMock(verify_signal_cross_exchange=AsyncMock(return_value=True)),
        spot_client=MagicMock(),
        telemetry=MagicMock(),
        signal_queue=signal_queue,
        router=MagicMock(active_signals={}, cleanup_expired=MagicMock(return_value=0)),
        onchain_client=MagicMock(get_exchange_flow=AsyncMock(return_value=None)),
    )


def _base_patches(scanner, extra=None):
    """Standard pipeline patches — no gates fire by default."""
    stack = contextlib.ExitStack()
    stack.enter_context(
        patch("src.scanner.compute_confidence",
              return_value=SimpleNamespace(total=70.0, blocked=False))
    )
    stack.enter_context(patch("src.scanner.check_vwap_extension", return_value=(True, "")))
    stack.enter_context(patch("src.scanner.check_kill_zone_gate", return_value=(True, "")))
    stack.enter_context(patch.object(scanner, "_evaluate_setup", return_value=SetupAssessment(
        setup_class=SetupClass.BREAKOUT_RETEST, thesis="Breakout",
        channel_compatible=True, regime_compatible=True,
    )))
    stack.enter_context(patch.object(scanner, "_evaluate_execution", return_value=ExecutionAssessment(
        passed=True, trigger_confirmed=True, extension_ratio=0.6,
        anchor_price=99.0, entry_zone="99–100", execution_note="ok",
    )))
    stack.enter_context(patch.object(scanner, "_evaluate_risk", return_value=RiskAssessment(
        passed=True, stop_loss=95.0, tp1=106.5, tp2=111.5, tp3=117.0,
        r_multiple=1.3, invalidation_summary="below 96",
    )))
    for p in (extra or []):
        stack.enter_context(p)
    return stack


# ---------------------------------------------------------------------------
# PR-15 regression tests
# ---------------------------------------------------------------------------

class TestPR15SoftPenaltyInteraction:

    @pytest.mark.asyncio
    async def test_evaluator_penalty_is_deducted_from_confidence(self):
        """Evaluator-authored soft_penalty_total must reduce confidence after scoring.

        E=10, S=0.  Composite score=80.  Expected final confidence = 80 − 10 = 70.
        Before the fix, E was recorded but never subtracted, so confidence stayed at 80.
        """
        import src.scanner as scanner_mod

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(soft_penalty_total=10.0)
        sq = MagicMock()
        captured: dict = {}

        async def _cap(sig):
            captured["sig"] = sig

        sq.put = AsyncMock(side_effect=_cap)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=sq)

        score = {"smc": 20.0, "regime": 18.0, "volume": 14.0,
                 "indicators": 14.0, "patterns": 7.0, "mtf": 7.0, "total": 80.0}
        with _base_patches(scanner, extra=[
            patch.object(scanner_mod._scoring_engine, "score", return_value=score),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        sig = captured.get("sig")
        assert sig is not None
        assert sig.confidence == pytest.approx(70.0, abs=0.2), (
            f"Expected 80 - 10 = 70, got {sig.confidence}. "
            "Evaluator penalty was not deducted."
        )

    @pytest.mark.asyncio
    async def test_total_penalty_used_not_scanner_local_only(self):
        """sig.soft_penalty_total (E+S) must be deducted, not just the scanner portion.

        E=10 (evaluator), S=15 (VWAP gate, RANGING regime × 1.0).
        Score=82.  Expected final = 82 − 25 = 57.
        Before the fix, only S=15 was deducted, giving 82 − 15 = 67.
        """
        import src.scanner as scanner_mod

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(soft_penalty_total=10.0)
        sq = MagicMock()
        captured: dict = {}

        async def _cap(sig):
            captured["sig"] = sig

        sq.put = AsyncMock(side_effect=_cap)
        scanner = _make_scan_ready_scanner(
            channel=channel, signal_queue=sq, regime=MarketRegime.RANGING
        )

        score = {"smc": 22.0, "regime": 18.0, "volume": 14.0,
                 "indicators": 14.0, "patterns": 7.0, "mtf": 7.0, "total": 82.0}
        with _base_patches(scanner, extra=[
            patch("src.scanner.check_vwap_extension", return_value=(False, "VWAP: overextended")),
            patch.object(scanner_mod._scoring_engine, "score", return_value=score),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        sig = captured.get("sig")
        assert sig is not None
        # Consistency: final confidence must equal score − total penalty (E+S)
        assert sig.confidence == pytest.approx(82.0 - sig.soft_penalty_total, abs=0.5), (
            "Final confidence must equal composite_score − soft_penalty_total (E+S combined)."
        )
        # Numeric check: E=10, S=15, total=25, score=82 → 57
        assert sig.confidence == pytest.approx(57.0, abs=1.0), (
            f"Expected 82 - (10+15) = 57, got {sig.confidence}. "
            "Only scanner portion may have been deducted."
        )

    @pytest.mark.asyncio
    async def test_signal_tier_reclassified_after_full_penalty(self):
        """sig.signal_tier must reflect post-penalty confidence, not the scoring-engine tier.

        Scoring engine: score=82 → A+.
        E=10 → post-penalty confidence=72 → should be reclassified to "B".
        Before the fix, tier remained "A+" even though confidence had dropped to 72.
        """
        import src.scanner as scanner_mod

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(soft_penalty_total=10.0)
        sq = MagicMock()
        captured: dict = {}

        async def _cap(sig):
            captured["sig"] = sig

        sq.put = AsyncMock(side_effect=_cap)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=sq)

        score = {"smc": 22.0, "regime": 18.0, "volume": 14.0,
                 "indicators": 14.0, "patterns": 7.0, "mtf": 7.0, "total": 82.0}
        with _base_patches(scanner, extra=[
            patch.object(scanner_mod._scoring_engine, "score", return_value=score),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        sig = captured.get("sig")
        assert sig is not None
        assert sig.confidence == pytest.approx(72.0, abs=0.2)
        assert sig.signal_tier == "B", (
            f"Expected tier 'B' for post-penalty confidence 72, got '{sig.signal_tier}'. "
            "Tier was not re-classified after penalty."
        )

    @pytest.mark.asyncio
    async def test_stale_watchlist_acceptance_rejected_after_evaluator_penalty(self):
        """A WATCHLIST-tier signal must not be accepted when evaluator penalty drops it below 50.

        Scoring engine: score=55 → WATCHLIST.  E=8 → post-penalty confidence=47.
        Before the fix, sig.signal_tier stayed "WATCHLIST" and the WATCHLIST branch
        kept the signal even though its true confidence was below the 50 floor.
        After the fix, the stale tier is updated to "FILTERED" and the signal is rejected.
        """
        import src.scanner as scanner_mod

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=50.0)
        channel.evaluate.return_value = _make_signal(soft_penalty_total=8.0)
        sq = MagicMock()
        sq.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=sq)

        score = {"smc": 12.0, "regime": 10.0, "volume": 8.0,
                 "indicators": 10.0, "patterns": 8.0, "mtf": 7.0, "total": 55.0}
        with _base_patches(scanner, extra=[
            patch.object(scanner_mod._scoring_engine, "score", return_value=score),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Post-penalty = 55 − 8 = 47 < 50 → must not be accepted as WATCHLIST.
        sq.put.assert_not_awaited()
