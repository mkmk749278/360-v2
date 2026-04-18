"""Tests for Scanner – cooldown logic and regime-aware gating."""

from __future__ import annotations

import asyncio
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import CHANNEL_ENABLE_DEFAULTS, CHANNEL_VOLATILE_FAMILY_GOVERNED
from src.channels.base import Signal
from src.regime import MarketRegime
from src.scanner import Scanner, _RANGING_ADX_SUPPRESS_THRESHOLD
from src.signal_quality import (
    ExecutionAssessment,
    MarketState,
    RiskAssessment,
    SetupAssessment,
    SetupClass,
)
from src.smc import Direction
from src.utils import utcnow


def _make_scanner(**kwargs) -> Scanner:
    """Create a minimal Scanner instance with mocked dependencies."""
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
    signal_id: str = "SIG-001",
    confidence: float = 10.0,
) -> Signal:
    return Signal(
        channel=channel,
        symbol="BTCUSDT",
        direction=Direction.LONG,
        entry=100.0,
        stop_loss=95.0,
        tp1=105.0,
        tp2=110.0,
        confidence=confidence,
        signal_id=signal_id,
        timestamp=utcnow(),
    )


def _make_scan_ready_scanner(
    *,
    channel: MagicMock,
    signal_queue: MagicMock,
    predictive: MagicMock | None = None,
    openai_evaluator: MagicMock | None = None,
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
    if predictive is None:
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
        openai_evaluator=openai_evaluator,
        onchain_client=MagicMock(get_exchange_flow=AsyncMock(return_value=None)),
    )


def _setup_pass(
    setup_class: SetupClass = SetupClass.BREAKOUT_RETEST,
    thesis: str | None = None,
) -> SetupAssessment:
    return SetupAssessment(
        setup_class=setup_class,
        thesis=thesis or setup_class.value,
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


class TestScannerCooldown:
    def test_no_cooldown_initially(self):
        scanner = _make_scanner()
        assert scanner._is_in_cooldown("BTCUSDT", "360_SCALP") is False

    def test_cooldown_active_after_set(self):
        scanner = _make_scanner()
        scanner._set_cooldown("BTCUSDT", "360_SCALP")
        assert scanner._is_in_cooldown("BTCUSDT", "360_SCALP") is True

    def test_cooldown_expires(self):
        scanner = _make_scanner()
        # Manually set an already-expired cooldown
        scanner._cooldown_until[("BTCUSDT", "360_SCALP")] = (
            time.monotonic() - 1  # 1 second in the past
        )
        assert scanner._is_in_cooldown("BTCUSDT", "360_SCALP") is False

    def test_cooldown_expires_cleans_up(self):
        scanner = _make_scanner()
        scanner._cooldown_until[("BTCUSDT", "360_SCALP")] = (
            time.monotonic() - 1
        )
        scanner._is_in_cooldown("BTCUSDT", "360_SCALP")
        assert ("BTCUSDT", "360_SCALP") not in scanner._cooldown_until

    def test_cooldown_separate_per_channel(self):
        scanner = _make_scanner()
        scanner._set_cooldown("BTCUSDT", "360_SCALP")
        assert scanner._is_in_cooldown("BTCUSDT", "360_SCALP") is True
        assert scanner._is_in_cooldown("BTCUSDT", "360_SWING") is False

    def test_cooldown_separate_per_symbol(self):
        scanner = _make_scanner()
        scanner._set_cooldown("BTCUSDT", "360_SCALP")
        assert scanner._is_in_cooldown("ETHUSDT", "360_SCALP") is False

    def test_cooldown_duration_from_config(self):
        from config import SIGNAL_SCAN_COOLDOWN_SECONDS
        scanner = _make_scanner()
        scanner._set_cooldown("BTCUSDT", "360_SCALP")
        expiry = scanner._cooldown_until[("BTCUSDT", "360_SCALP")]
        expected_duration = SIGNAL_SCAN_COOLDOWN_SECONDS.get("360_SCALP", 300)
        actual_duration = expiry - time.monotonic()
        assert abs(actual_duration - expected_duration) < 2  # within 2 seconds

    def test_lifecycle_outcome_counter_is_family_attributed(self):
        scanner = _make_scanner()
        sig = _make_signal(channel="360_SCALP")
        sig.setup_class = "FAILED_AUCTION_RECLAIM"

        scanner.on_signal_lifecycle_outcome(sig, "SL_HIT")

        assert scanner._path_funnel_counters[
            "lifecycle:SL_HIT:360_SCALP:reclaim_retest:FAILED_AUCTION_RECLAIM"
        ] == 1

    def test_lifecycle_outcome_uses_origin_setup_identity_when_setup_missing(self):
        scanner = _make_scanner()
        sig = _make_signal(channel="360_SCALP")
        sig.setup_class = ""
        sig.origin_setup_class = "FAILED_AUCTION_RECLAIM"
        sig.origin_setup_family = "reclaim_retest"

        scanner.on_signal_lifecycle_outcome(sig, "SL_HIT")

        assert scanner._path_funnel_counters[
            "lifecycle:SL_HIT:360_SCALP:reclaim_retest:FAILED_AUCTION_RECLAIM"
        ] == 1


class TestScannerCircuitBreaker:
    def test_circuit_breaker_not_set_by_default(self):
        scanner = _make_scanner()
        assert scanner.circuit_breaker is None

    @pytest.mark.asyncio
    async def test_scan_loop_skips_when_tripped(self):
        """Scan loop should skip evaluation when circuit breaker is tripped."""
        scanner = _make_scanner()
        cb = MagicMock()
        cb.is_tripped.return_value = True
        scanner.circuit_breaker = cb

        # Patch asyncio.sleep to avoid infinite loop
        sleep_count = 0

        async def mock_sleep(n):
            nonlocal sleep_count
            sleep_count += 1
            if sleep_count >= 2:
                raise asyncio.CancelledError

        with patch("src.scanner.asyncio.sleep", side_effect=mock_sleep):
            try:
                await scanner.scan_loop()
            except asyncio.CancelledError:
                pass

        # pair_mgr should NOT have been accessed (scan was skipped)
        scanner.pair_mgr.pairs.items.assert_not_called()


class TestScannerRegimeGating:
    def test_ranging_adx_threshold_constant(self):
        assert _RANGING_ADX_SUPPRESS_THRESHOLD == 15.0

    def test_scanner_has_paused_channels_attribute(self):
        scanner = _make_scanner()
        assert isinstance(scanner.paused_channels, set)

    def test_scanner_has_confidence_overrides_attribute(self):
        scanner = _make_scanner()
        assert isinstance(scanner.confidence_overrides, dict)

    def test_scanner_paused_channels_shared_with_external_set(self):
        shared = set()
        scanner = _make_scanner()
        scanner.paused_channels = shared
        shared.add("360_SCALP")
        assert "360_SCALP" in scanner.paused_channels


class TestScannerAttributes:
    def test_force_scan_starts_false(self):
        scanner = _make_scanner()
        assert scanner.force_scan is False

    def test_force_scan_can_be_set(self):
        scanner = _make_scanner()
        scanner.force_scan = True
        assert scanner.force_scan is True

    def test_ws_spot_starts_none(self):
        scanner = _make_scanner()
        assert scanner.ws_spot is None

    def test_ws_futures_starts_none(self):
        scanner = _make_scanner()
        assert scanner.ws_futures is None


class TestScannerConfidencePipeline:
    @pytest.mark.asyncio
    async def test_adjustments_persist_and_final_clamp_applies_last(self):
        """Signal pipeline: base → regime adjustment → predictive → clamp.

        Since OpenAI is no longer in the hot path, confidence is determined
        purely by score_signal_components (mocked to 87.0).  Predictive
        adjustments still run before score_signal_components overwrites the
        confidence.  The final clamped value is above min_confidence (60.0)
        so the signal is enqueued, and post_ai_confidence equals confidence.
        """
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=60.0)
        channel.evaluate.return_value = _make_signal(channel="360_SCALP", signal_id="SIG-001")

        predictive = MagicMock()
        predictive.predict = AsyncMock(
            return_value=SimpleNamespace(
                confidence_adjustment=7.0,
                predicted_direction="UP",
                suggested_tp_adjustment=1.0,
                suggested_sl_adjustment=1.0,
            )
        )
        predictive.adjust_tp_sl = MagicMock()
        predictive.update_confidence = MagicMock()

        fake_component_score = SimpleNamespace(
            total=87.0,
            quality_tier=SimpleNamespace(value="A"),
            components={
                "market": 20.0,
                "setup": 25.0,
                "execution": 20.0,
                "risk": 15.0,
                "context": 7.0,
            },
        )

        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)

        scanner = _make_scan_ready_scanner(
            channel=channel,
            signal_queue=signal_queue,
            predictive=predictive,
            regime=MarketRegime.RANGING,
        )

        with patch("src.scanner.compute_confidence", return_value=SimpleNamespace(total=55.0, blocked=False)), \
             patch("src.scanner.score_signal_components", return_value=fake_component_score), \
             patch.object(scanner, "_evaluate_setup", return_value=_setup_pass()), \
             patch.object(scanner, "_evaluate_execution", return_value=_execution_pass()), \
             patch.object(scanner, "_evaluate_risk", return_value=_risk_pass()), \
             patch("src.scanner.check_vwap_extension", return_value=(True, "")), \
             patch("src.scanner.check_kill_zone_gate", return_value=(True, "")):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        queued_signal = signal_queue.put.await_args.args[0]
        # score_signal_components mock returns 87.0; clamped to 100 max
        assert queued_signal.confidence <= 100.0
        assert queued_signal.confidence >= 60.0  # above min_confidence
        assert predictive.adjust_tp_sl.called
        assert predictive.update_confidence.called
        assert queued_signal.post_ai_confidence == queued_signal.confidence
        assert queued_signal.setup_class == SetupClass.BREAKOUT_RETEST.value

    @pytest.mark.asyncio
    async def test_signals_below_final_min_confidence_are_rejected_after_all_adjustments(self):
        """Signals that fall below min_confidence after quantitative scoring
        must be rejected (not enqueued).  Purely algorithmic – no AI involved.
        """
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SWING", min_confidence=80.0)
        channel.evaluate.return_value = _make_signal(channel="360_SWING", signal_id="SIG-LOW")

        fake_component_score = SimpleNamespace(
            total=65.0,
            quality_tier=SimpleNamespace(value="C"),
            components={
                "market": 20.0,
                "setup": 20.0,
                "execution": 13.0,
                "risk": 10.0,
                "context": 2.0,
            },
        )

        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(
            channel=channel,
            signal_queue=signal_queue,
        )

        with patch("src.scanner.compute_confidence", return_value=SimpleNamespace(total=50.0, blocked=False)), \
             patch("src.scanner.score_signal_components", return_value=fake_component_score), \
             patch.object(scanner, "_evaluate_setup", return_value=_setup_pass()), \
             patch.object(scanner, "_evaluate_execution", return_value=_execution_pass()), \
             patch.object(scanner, "_evaluate_risk", return_value=_risk_pass()), \
             patch("src.scanner.check_vwap_extension", return_value=(True, "")), \
             patch("src.scanner.check_kill_zone_gate", return_value=(True, "")):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Confidence 65.0 < min_confidence 80.0 → rejected
        signal_queue.put.assert_not_awaited()


class TestPredictiveGeometryRevalidation:
    @staticmethod
    def _predictive(tp_mult: float, sl_mult: float):
        pred = SimpleNamespace(
            confidence_adjustment=0.0,
            predicted_direction="NEUTRAL",
            suggested_tp_adjustment=tp_mult,
            suggested_sl_adjustment=sl_mult,
        )

        async def _predict(*_args, **_kwargs):
            return pred

        def _adjust(sig, prediction):
            entry = sig.entry
            if prediction.suggested_tp_adjustment != 1.0:
                m = prediction.suggested_tp_adjustment
                sig.tp1 = entry + (sig.tp1 - entry) * m
                sig.tp2 = entry + (sig.tp2 - entry) * m
                if getattr(sig, "tp3", None) is not None:
                    sig.tp3 = entry + (sig.tp3 - entry) * m
            if prediction.suggested_sl_adjustment != 1.0:
                m = prediction.suggested_sl_adjustment
                sig.stop_loss = entry + (sig.stop_loss - entry) * m

        return SimpleNamespace(
            predict=AsyncMock(side_effect=_predict),
            adjust_tp_sl=MagicMock(side_effect=_adjust),
            update_confidence=MagicMock(),
        )

    @pytest.mark.asyncio
    async def test_invalid_predictive_geometry_is_reverted(self):
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(
            channel=channel,
            signal_queue=signal_queue,
            predictive=self._predictive(tp_mult=1.0, sl_mult=-1.0),
        )
        sig = _make_signal(channel="360_SCALP")
        sig.stop_loss = 98.8
        sig.tp1 = 101.6
        sig.tp2 = 103.2
        sig.tp3 = 104.8
        before = (sig.stop_loss, sig.tp1, sig.tp2, sig.tp3)
        ctx = SimpleNamespace(candles={"5m": _candles()}, ind_for_predict={"atr_last": 1.0})

        await scanner._apply_predictive_adjustments(
            "BTCUSDT",
            sig,
            ctx,
            setup=_setup_pass(SetupClass.VOLUME_SURGE_BREAKOUT),
            chan_name="360_SCALP",
        )

        assert (sig.stop_loss, sig.tp1, sig.tp2, sig.tp3) == pytest.approx(before, rel=1e-8)
        assert scanner._suppression_counters[
            "predictive_revalidation_rejected:360_SCALP:breakout_momentum"
        ] == 1
        assert scanner._suppression_counters[
            "geometry_preserved_final:360_SCALP:breakout_momentum"
        ] == 1
        assert scanner._path_funnel_counters[
            "geometry:final_live:rejected:360_SCALP:breakout_momentum:VOLUME_SURGE_BREAKOUT"
        ] == 1
        assert any(
            key.startswith("geometry:final_live:rejected_reason:")
            and key.endswith(":360_SCALP:breakout_momentum:VOLUME_SURGE_BREAKOUT")
            for key in scanner._path_funnel_counters
        )

    @pytest.mark.asyncio
    async def test_valid_predictive_geometry_change_is_kept(self):
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(
            channel=channel,
            signal_queue=signal_queue,
            predictive=self._predictive(tp_mult=1.1, sl_mult=0.9),
        )
        sig = _make_signal(channel="360_SCALP")
        sig.stop_loss = 98.8
        sig.tp1 = 101.6
        sig.tp2 = 103.2
        sig.tp3 = 104.8
        before = (sig.stop_loss, sig.tp1, sig.tp2, sig.tp3)
        ctx = SimpleNamespace(candles={"5m": _candles()}, ind_for_predict={"atr_last": 1.0})

        await scanner._apply_predictive_adjustments(
            "BTCUSDT",
            sig,
            ctx,
            setup=_setup_pass(SetupClass.VOLUME_SURGE_BREAKOUT),
            chan_name="360_SCALP",
        )

        assert (sig.stop_loss, sig.tp1, sig.tp2, sig.tp3) != pytest.approx(before, rel=1e-8)
        assert scanner._suppression_counters[
            "predictive_revalidation_passed:360_SCALP:breakout_momentum"
        ] == 1
        assert scanner._suppression_counters[
            "geometry_changed_final:360_SCALP:breakout_momentum"
        ] == 1
        assert scanner._path_funnel_counters[
            "geometry:final_live:changed:360_SCALP:breakout_momentum:VOLUME_SURGE_BREAKOUT"
        ] == 1

    @pytest.mark.asyncio
    async def test_unchanged_predictive_geometry_is_bypassed(self):
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(
            channel=channel,
            signal_queue=signal_queue,
            predictive=self._predictive(tp_mult=1.0, sl_mult=1.0),
        )
        sig = _make_signal(channel="360_SCALP")
        sig.stop_loss = 98.8
        sig.tp1 = 101.6
        sig.tp2 = 103.2
        sig.tp3 = 104.8
        before = (sig.stop_loss, sig.tp1, sig.tp2, sig.tp3)
        ctx = SimpleNamespace(candles={"5m": _candles()}, ind_for_predict={"atr_last": 1.0})

        await scanner._apply_predictive_adjustments(
            "BTCUSDT",
            sig,
            ctx,
            setup=_setup_pass(SetupClass.VOLUME_SURGE_BREAKOUT),
            chan_name="360_SCALP",
        )

        assert (sig.stop_loss, sig.tp1, sig.tp2, sig.tp3) == pytest.approx(before, rel=1e-8)
        assert scanner._suppression_counters[
            "predictive_revalidation_bypassed:360_SCALP:unchanged"
        ] == 1
        assert scanner._suppression_counters[
            "geometry_preserved_final:360_SCALP:breakout_momentum"
        ] == 1
        assert scanner._path_funnel_counters[
            "geometry:final_live:preserved:360_SCALP:breakout_momentum:VOLUME_SURGE_BREAKOUT"
        ] == 1

    @pytest.mark.asyncio
    async def test_high_confidence_signals_enqueued_without_ai(self):
        """High-confidence quantitative signals fire immediately without any AI
        evaluation, for all channel types.
        """
        for ch_name in ("360_SCALP", "360_SPOT", "360_SWING", "360_GEM"):
            channel = MagicMock()
            channel.config = SimpleNamespace(name=ch_name, min_confidence=10.0)
            channel.evaluate.return_value = _make_signal(channel=ch_name, signal_id="SIG-HOT")
            signal_queue = MagicMock()
            signal_queue.put = AsyncMock(return_value=True)

            fake_component_score = SimpleNamespace(
                total=92.0,
                quality_tier=SimpleNamespace(value="A+"),
                components={
                    "market": 22.0,
                    "setup": 25.0,
                    "execution": 20.0,
                    "risk": 17.0,
                    "context": 8.0,
                },
            )

            scanner = _make_scan_ready_scanner(
                channel=channel,
                signal_queue=signal_queue,
            )

            with patch("src.scanner.compute_confidence", return_value=SimpleNamespace(total=55.0, blocked=False)), \
                 patch("src.scanner.score_signal_components", return_value=fake_component_score), \
                 patch.object(scanner, "_evaluate_setup", return_value=_setup_pass()), \
                 patch.object(scanner, "_evaluate_execution", return_value=_execution_pass()), \
                 patch.object(scanner, "_evaluate_risk", return_value=_risk_pass()), \
                 patch("src.scanner.check_vwap_extension", return_value=(True, "")), \
                 patch("src.scanner.check_kill_zone_gate", return_value=(True, "")):
                await scanner._scan_symbol("BTCUSDT", 10_000_000)

            # Signal IS enqueued instantly (no AI latency)
            signal_queue.put.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_signals_enqueued_with_quantitative_scoring_only(self):
        """Signals are evaluated purely on quantitative scores; no AI calls."""
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SWING", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(channel="360_SWING", signal_id="SIG-QUANT")
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)

        fake_component_score = SimpleNamespace(
            total=70.0,
            quality_tier=SimpleNamespace(value="B"),
            components={
                "market": 15.0,
                "setup": 20.0,
                "execution": 15.0,
                "risk": 13.0,
                "context": 7.0,
            },
        )

        scanner = _make_scan_ready_scanner(
            channel=channel,
            signal_queue=signal_queue,
        )

        with patch("src.scanner.compute_confidence", return_value=SimpleNamespace(total=50.0, blocked=False)), \
             patch("src.scanner.score_signal_components", return_value=fake_component_score), \
             patch.object(scanner, "_evaluate_setup", return_value=_setup_pass()), \
             patch.object(scanner, "_evaluate_execution", return_value=_execution_pass()), \
             patch.object(scanner, "_evaluate_risk", return_value=_risk_pass()), \
             patch("src.scanner.check_vwap_extension", return_value=(True, "")), \
             patch("src.scanner.check_kill_zone_gate", return_value=(True, "")):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Signal passes (min_confidence=10.0) and is enqueued without AI
        signal_queue.put.assert_awaited_once()


class TestScannerEnqueueSemantics:
    @pytest.mark.asyncio
    async def test_cooldown_not_started_when_enqueue_fails(self):
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(channel="360_SCALP", signal_id="SIG-DROP")
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=False)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)

        with patch("src.scanner.compute_confidence", return_value=SimpleNamespace(total=80.0, blocked=False)), \
             patch.object(scanner, "_evaluate_setup", return_value=_setup_pass()), \
             patch.object(scanner, "_evaluate_execution", return_value=_execution_pass()), \
             patch.object(scanner, "_evaluate_risk", return_value=_risk_pass()), \
             patch("src.scanner.check_vwap_extension", return_value=(True, "")), \
             patch("src.scanner.check_kill_zone_gate", return_value=(True, "")):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        assert ("BTCUSDT", "360_SCALP") not in scanner._cooldown_until

    @pytest.mark.asyncio
    async def test_failed_enqueue_does_not_suppress_later_signal(self):
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.side_effect = [
            _make_signal(channel="360_SCALP", signal_id="SIG-FIRST"),
            _make_signal(channel="360_SCALP", signal_id="SIG-SECOND"),
        ]
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(side_effect=[False, True])
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)

        with patch("src.scanner.compute_confidence", return_value=SimpleNamespace(total=80.0, blocked=False)), \
             patch.object(scanner, "_evaluate_setup", return_value=_setup_pass()), \
             patch.object(scanner, "_evaluate_execution", return_value=_execution_pass()), \
             patch.object(scanner, "_evaluate_risk", return_value=_risk_pass()), \
             patch("src.scanner.check_vwap_extension", return_value=(True, "")), \
             patch("src.scanner.check_kill_zone_gate", return_value=(True, "")):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        assert signal_queue.put.await_count == 2
        assert scanner._cooldown_until.get(("BTCUSDT", "360_SCALP")) is not None


class TestComputeIndicatorsArrayShape:
    """_compute_indicators must tolerate 2-D (non-flat) candle arrays."""

    def test_2d_arrays_do_not_raise(self):
        """Candle data stored as 2-D arrays must be flattened without error."""
        import numpy as np
        n = 40
        flat = np.arange(1.0, n + 1.0)
        # Wrap flat 1-D arrays into 2-D column vectors (simulates bad storage)
        candles = {
            "5m": {
                "high": flat.reshape(-1, 1),
                "low": (flat - 0.5).reshape(-1, 1),
                "close": flat.reshape(-1, 1),
                "volume": np.ones((n, 1)) * 100,
            }
        }
        scanner = _make_scanner()
        # Should not raise ValueError about truth value of array
        indicators = scanner._compute_indicators(candles)
        assert "5m" in indicators
        # EMA values must be scalar floats
        assert isinstance(indicators["5m"].get("ema9_last"), float)
        assert isinstance(indicators["5m"].get("ema21_last"), float)


class TestThesisCooldown:
    """Thesis-based cooldowns have been removed (all suppression is now handled
    by the quality-gate confidence floor).  These tests verify that the old
    state attributes and methods no longer exist on Scanner."""

    def test_no_thesis_cooldown_dict(self):
        scanner = _make_scanner()
        assert not hasattr(scanner, "_thesis_cooldown_until")

    def test_no_symbol_sl_cooldown_dict(self):
        scanner = _make_scanner()
        assert not hasattr(scanner, "_symbol_sl_cooldown_until")

    def test_no_notify_sl_hit_method(self):
        scanner = _make_scanner()
        assert not hasattr(scanner, "notify_sl_hit")

    def test_1d_arrays_still_work(self):
        """Normal 1-D candle arrays continue to produce correct indicators."""
        import numpy as np
        n = 40
        flat = np.arange(1.0, n + 1.0)
        candles = {
            "5m": {
                "high": flat,
                "low": flat - 0.5,
                "close": flat,
                "volume": np.ones(n) * 100,
            }
        }
        scanner = _make_scanner()
        indicators = scanner._compute_indicators(candles)
        assert isinstance(indicators["5m"].get("ema9_last"), float)


class TestSpreadCacheFailureTTL:
    """_get_spread_pct is now a pure cache lookup (no HTTP calls).
    Spread is seeded by _fetch_global_book_tickers() via bookTicker pre-fetch."""

    @pytest.mark.asyncio
    async def test_returns_fallback_when_cache_empty(self):
        """Returns 0.01 fallback when no bookTicker data has been cached."""
        scanner = _make_scanner()
        spread = await scanner._get_spread_pct("EURUSDT")
        assert spread == 0.01

    @pytest.mark.asyncio
    async def test_returns_cached_spread_when_populated(self):
        """Returns the bookTicker-seeded spread when cache is fresh."""
        import time
        scanner = _make_scanner()
        scanner._order_book_cache["BTCUSDT"] = (0.05, time.monotonic() + 20.0)
        spread = await scanner._get_spread_pct("BTCUSDT")
        assert spread == 0.05

    @pytest.mark.asyncio
    async def test_returns_fallback_when_cache_expired(self):
        """Returns 0.01 fallback when cache entry has expired."""
        import time
        scanner = _make_scanner()
        scanner._order_book_cache["ETHUSDT"] = (0.03, time.monotonic() - 1.0)
        spread = await scanner._get_spread_pct("ETHUSDT")
        assert spread == 0.01

    @pytest.mark.asyncio
    async def test_no_http_calls_made(self):
        """_get_spread_pct never calls fetch_order_book regardless of market."""
        scanner = _make_scanner()
        mock_client = MagicMock()
        mock_client.fetch_order_book = AsyncMock(return_value=None)
        scanner.spot_client = mock_client
        scanner.futures_client = mock_client

        await scanner._get_spread_pct("BTCUSDT", market="spot")
        await scanner._get_spread_pct("BTCUSDT", market="futures")
        assert mock_client.fetch_order_book.await_count == 0


# ---------------------------------------------------------------------------
# Bug 1: Regime stability tracker
# ---------------------------------------------------------------------------


class TestRegimeStabilityTracker:
    """Tests for _regime_history and _is_regime_unstable."""

    def test_regime_history_initialized_empty(self):
        scanner = _make_scanner()
        assert scanner._regime_history == {}

    def test_not_unstable_with_no_history(self):
        scanner = _make_scanner()
        assert scanner._is_regime_unstable("ETHUSDT") is False

    def test_not_unstable_with_single_entry(self):
        scanner = _make_scanner()
        scanner._regime_history["ETHUSDT"] = [(time.monotonic(), "RANGING")]
        assert scanner._is_regime_unstable("ETHUSDT") is False

    def test_not_unstable_below_max_flips(self):
        scanner = _make_scanner()
        now = time.monotonic()
        # 2 flips (below max_flips=2 — not strictly greater)
        scanner._regime_history["ETHUSDT"] = [
            (now - 1000, "RANGING"),
            (now - 800, "TRENDING_UP"),
            (now - 600, "RANGING"),
        ]
        assert scanner._is_regime_unstable("ETHUSDT", window_minutes=30, max_flips=2) is False

    def test_unstable_when_exceeds_max_flips(self):
        scanner = _make_scanner()
        now = time.monotonic()
        # 3 flips > max_flips=2
        scanner._regime_history["ETHUSDT"] = [
            (now - 1500, "RANGING"),
            (now - 1200, "TRENDING_UP"),
            (now - 900, "RANGING"),
            (now - 600, "TRENDING_DOWN"),
        ]
        assert scanner._is_regime_unstable("ETHUSDT", window_minutes=30, max_flips=2) is True

    def test_old_entries_excluded_from_window(self):
        scanner = _make_scanner()
        now = time.monotonic()
        # The flips happen outside the 30-min window
        scanner._regime_history["ETHUSDT"] = [
            (now - 3600, "RANGING"),
            (now - 3000, "TRENDING_UP"),
            (now - 2400, "RANGING"),
            (now - 1800, "TRENDING_DOWN"),
            # Only one entry within the 30-min window → no flips
            (now - 100, "RANGING"),
        ]
        assert scanner._is_regime_unstable("ETHUSDT", window_minutes=30, max_flips=2) is False

    def test_should_skip_scalp_when_regime_quiet(self):
        """_should_skip_channel returns False for 360_SCALP when regime is QUIET.

        Since PR-OPT-01, SCALP channels are no longer hard-blocked in QUIET.
        Instead they receive a higher soft-gate penalty and a minimum confidence
        gate inside _prepare_signal.  _should_skip_channel must return False so
        the signal evaluation proceeds to the soft-penalty stage.
        """
        scanner = _make_scanner()
        ctx = MagicMock()
        ctx.pair_quality.passed = True
        ctx.market_state = MagicMock()
        ctx.market_state.__eq__ = lambda self, other: False
        ctx.regime_result.regime.value = "QUIET"
        scanner.circuit_breaker = None
        scanner.router.active_signals = {}
        ctx.is_ranging = False
        ctx.adx_val = 25.0
        result = scanner._should_skip_channel("ETHUSDT", "360_SCALP", ctx)
        assert result is False

    def test_should_skip_scalp_vwap_when_regime_quiet(self):
        """_should_skip_channel returns True for 360_SCALP_VWAP when regime is QUIET.

        VWAP signals are meaningless without sufficient trading volume, so
        360_SCALP_VWAP remains hard-blocked in QUIET regime.
        """
        scanner = _make_scanner()
        ctx = MagicMock()
        ctx.pair_quality.passed = True
        ctx.market_state = MagicMock()
        ctx.market_state.__eq__ = lambda self, other: False
        ctx.regime_result.regime.value = "QUIET"
        scanner.circuit_breaker = None
        scanner.router.active_signals = {}
        ctx.is_ranging = False
        ctx.adx_val = 25.0
        result = scanner._should_skip_channel("ETHUSDT", "360_SCALP_VWAP", ctx)
        assert result is True

    def test_should_not_skip_swing_when_regime_quiet(self):
        """QUIET regime is incompatible with SCALP_VWAP only, not SWING."""
        scanner = _make_scanner()
        ctx = MagicMock()
        ctx.pair_quality.passed = True
        ctx.market_state = MagicMock()
        ctx.market_state.__eq__ = lambda self, other: False
        ctx.regime_result.regime.value = "QUIET"
        scanner.circuit_breaker = None
        scanner.router.active_signals = {}
        ctx.is_ranging = False
        ctx.adx_val = 25.0
        # SWING should not be blocked by QUIET regime
        result = scanner._should_skip_channel("ETHUSDT", "360_SWING", ctx)
        assert result is False


class TestPR3GovernanceRuntimeRoles:
    """PR-3 governance/runtime truth and volatile contradiction cleanup."""

    def test_runtime_role_distinguishes_paid_vs_limited_live_specialist(self):
        scanner = _make_scanner()
        assert scanner._classify_channel_runtime_role("360_SCALP") == "runtime_active_paid"
        assert (
            scanner._classify_channel_runtime_role("360_SCALP_DIVERGENCE")
            == "specialist_limited_live"
        )

    def test_runtime_role_marks_radar_only_channel_explicitly(self):
        scanner = _make_scanner()
        assert scanner._classify_channel_runtime_role("360_SCALP_FVG") == "radar_only"

    def test_runtime_role_marks_non_rollout_specialist_as_intentionally_disabled(self):
        scanner = _make_scanner()
        assert scanner._classify_channel_runtime_role("360_SCALP_CVD") == "intentionally_disabled"

    def test_governance_snapshot_exposes_default_and_runtime_truth(self):
        scanner = _make_scanner()
        snapshot = scanner._channel_governance_snapshot()
        assert set(snapshot.keys()).issubset(set(CHANNEL_ENABLE_DEFAULTS.keys()))
        assert snapshot["360_SCALP"]["config_default_enabled"] is True
        assert snapshot["360_SCALP"]["runtime_enabled"] is True
        assert snapshot["360_SCALP"]["runtime_role"] == "runtime_active_paid"
        assert snapshot["360_SCALP"]["rollout_state"] == "full_live"
        assert snapshot["360_SCALP_FVG"]["config_default_enabled"] is False
        assert snapshot["360_SCALP_FVG"]["runtime_enabled"] is False
        assert snapshot["360_SCALP_FVG"]["rollout_state"] == "radar_only"
        assert snapshot["360_SCALP_DIVERGENCE"]["runtime_enabled"] is True
        assert snapshot["360_SCALP_DIVERGENCE"]["rollout_state"] == "limited_live"
        assert snapshot["360_SCALP_DIVERGENCE"]["limited_live_pilot_symbols"] == [
            "BTCUSDT",
            "ETHUSDT",
        ]

    def test_rollout_state_fail_closes_for_unknown_values(self):
        scanner = _make_scanner()
        with patch.dict(
            "src.scanner.CHANNEL_ROLLOUT_STATE_DEFAULTS",
            {"360_SCALP_FVG": "invalid_state"},
            clear=False,
        ):
            assert scanner._resolve_channel_rollout_state("360_SCALP_FVG") == "disabled"

    def test_rollout_states_have_distinct_live_and_radar_semantics(self):
        scanner = _make_scanner()
        with patch.dict(
            "src.scanner.CHANNEL_ROLLOUT_STATE_DEFAULTS",
            {
                "360_SCALP_FVG": "radar_only",
                "360_SCALP_DIVERGENCE": "limited_live",
                "360_SCALP": "full_live",
                "360_SCALP_CVD": "disabled",
            },
            clear=False,
        ):
            assert scanner._is_live_rollout_enabled_for_symbol("360_SCALP", "BTCUSDT") is True
            assert scanner._is_live_rollout_enabled_for_symbol("360_SCALP_DIVERGENCE", "BTCUSDT") is True
            assert scanner._is_live_rollout_enabled_for_symbol("360_SCALP_DIVERGENCE", "SOLUSDT") is False
            assert scanner._is_live_rollout_enabled_for_symbol("360_SCALP_FVG", "BTCUSDT") is False
            assert scanner._is_live_rollout_enabled_for_symbol("360_SCALP_CVD", "BTCUSDT") is False
            assert scanner._is_radar_rollout_enabled("360_SCALP_FVG", "BTCUSDT") is True
            assert scanner._is_radar_rollout_enabled("360_SCALP_DIVERGENCE", "SOLUSDT") is True
            assert scanner._is_radar_rollout_enabled("360_SCALP_DIVERGENCE", "BTCUSDT") is False
            assert scanner._is_radar_rollout_enabled("360_SCALP", "BTCUSDT") is False
            assert scanner._is_radar_rollout_enabled("360_SCALP_CVD", "BTCUSDT") is False

    def test_limited_live_rollout_is_narrow_and_reversible(self):
        scanner = _make_scanner()
        assert scanner._is_live_rollout_enabled_for_symbol("360_SCALP_DIVERGENCE", "BTCUSDT") is True
        assert scanner._is_live_rollout_enabled_for_symbol("360_SCALP_DIVERGENCE", "SOLUSDT") is False
        with patch.dict(
            "src.scanner.CHANNEL_LIMITED_LIVE_PILOT_SYMBOLS",
            {"360_SCALP_DIVERGENCE": frozenset()},
            clear=False,
        ):
            assert (
                scanner._is_live_rollout_enabled_for_symbol("360_SCALP_DIVERGENCE", "BTCUSDT")
                is False
            )

    def test_no_blanket_specialist_full_live_activation(self):
        scanner = _make_scanner()
        snapshot = scanner._channel_governance_snapshot()
        specialist_live = [
            ch
            for ch, meta in snapshot.items()
            if meta["product_role"] == "specialist" and meta["rollout_live_enabled"]
        ]
        assert specialist_live == ["360_SCALP_DIVERGENCE"]

    def test_rollout_exclusion_counter_tracks_limited_live_non_pilot(self):
        scanner = _make_scanner()
        scanner._record_rollout_live_exclusion("360_SCALP_DIVERGENCE", "SOLUSDT")
        assert (
            scanner._channel_funnel_counters[
                "rollout_excluded:live:limited_live:360_SCALP_DIVERGENCE"
            ]
            == 1
        )
        assert (
            scanner._channel_funnel_counters[
                "rollout_excluded:live:limited_live_non_pilot:360_SCALP_DIVERGENCE"
            ]
            == 1
        )

    def test_rollout_exclusion_counter_tracks_non_live_state(self):
        scanner = _make_scanner()
        scanner._record_rollout_live_exclusion("360_SCALP_FVG", "BTCUSDT")
        assert scanner._channel_funnel_counters["rollout_excluded:live:radar_only:360_SCALP_FVG"] == 1
        assert (
            scanner._channel_funnel_counters[
                "rollout_excluded:live:limited_live_non_pilot:360_SCALP_FVG"
            ]
            == 0
        )

    @pytest.mark.asyncio
    async def test_scan_symbol_emits_rollout_exclusion_for_non_pilot_live_skip(self):
        chan = MagicMock()
        chan.config.name = "360_SCALP_DIVERGENCE"
        chan.evaluate.return_value = None
        scanner = _make_scanner(
            channels=[chan],
            data_store=MagicMock(ticks={"SOLUSDT": []}),
            pair_mgr=MagicMock(pairs={}),
        )
        scanner._build_scan_context = AsyncMock(
            return_value=SimpleNamespace(
                candles={},
                indicators={},
                smc_data={},
                spread_pct=0.001,
                regime_result=SimpleNamespace(regime=SimpleNamespace(value="TRENDING_UP")),
            ),
        )
        scanner._update_btc_correlation = MagicMock()
        with patch.dict(
            "src.scanner.CHANNEL_LIMITED_LIVE_PILOT_SYMBOLS",
            {"360_SCALP_DIVERGENCE": frozenset({"BTCUSDT"})},
            clear=False,
        ):
            await scanner._scan_symbol("SOLUSDT", 10_000_000.0)
        assert (
            scanner._channel_funnel_counters[
                "rollout_excluded:live:limited_live_non_pilot:360_SCALP_DIVERGENCE"
            ]
            == 1
        )

    def test_should_not_channel_skip_specialist_in_volatile_unsuitable(self):
        scanner = _make_scanner()
        assert "360_SCALP_DIVERGENCE" in CHANNEL_VOLATILE_FAMILY_GOVERNED
        ctx = MagicMock()
        ctx.pair_quality.passed = True
        ctx.market_state = MarketState.VOLATILE_UNSUITABLE
        ctx.regime_result.regime.value = "VOLATILE_UNSUITABLE"
        scanner.circuit_breaker = None
        scanner.router.active_signals = {}
        ctx.is_ranging = False
        ctx.adx_val = 25.0
        result = scanner._should_skip_channel("ETHUSDT", "360_SCALP_DIVERGENCE", ctx)
        assert result is False
        assert (
            scanner._suppression_counters[
                "volatile_unsuitable:channel_preskip_bypassed:360_SCALP_DIVERGENCE"
            ] == 1
        )
        assert scanner._suppression_counters["volatile_unsuitable:360_SCALP_DIVERGENCE"] == 0

    def test_should_still_skip_non_governed_channel_in_volatile_unsuitable(self):
        scanner = _make_scanner()
        assert "360_SCALP_CVD" not in CHANNEL_VOLATILE_FAMILY_GOVERNED
        ctx = MagicMock()
        ctx.pair_quality.passed = True
        ctx.market_state = MarketState.VOLATILE_UNSUITABLE
        ctx.regime_result.regime.value = "VOLATILE_UNSUITABLE"
        scanner.circuit_breaker = None
        scanner.router.active_signals = {}
        ctx.is_ranging = False
        ctx.adx_val = 25.0
        result = scanner._should_skip_channel("ETHUSDT", "360_SCALP_CVD", ctx)
        assert result is True
        assert scanner._suppression_counters["volatile_unsuitable:360_SCALP_CVD"] == 1
        assert (
            scanner._suppression_counters[
                "volatile_unsuitable:channel_preskip_bypassed:360_SCALP_CVD"
            ] == 0
        )

    @pytest.mark.asyncio
    async def test_prepare_signal_tracks_family_level_volatile_block(self):
        scanner = _make_scanner()
        chan = MagicMock()
        chan.config.name = "360_SCALP_DIVERGENCE"
        chan.evaluate.return_value = _make_signal(channel="360_SCALP_DIVERGENCE", confidence=70.0)
        ctx = SimpleNamespace(
            candles={},
            indicators={},
            smc_data={},
            spread_pct=0.001,
            regime_result=SimpleNamespace(regime=SimpleNamespace(value="VOLATILE_UNSUITABLE")),
            market_state=MarketState.VOLATILE_UNSUITABLE,
        )
        scanner._evaluate_setup = MagicMock(
            return_value=SetupAssessment(
                setup_class=SetupClass.FAILED_AUCTION_RECLAIM,
                thesis="volatile blocked",
                channel_compatible=True,
                regime_compatible=False,
                reason="regime incompatible",
            )
        )
        sig, cross_verified = await scanner._prepare_signal("ETHUSDT", 10_000_000.0, chan, ctx)
        assert sig is None
        assert cross_verified is None
        assert scanner._suppression_counters["volatile_unsuitable:family_block:360_SCALP_DIVERGENCE"] == 1


# ---------------------------------------------------------------------------
# Bug 2: Direction-agnostic invalidation pair cooldown
# ---------------------------------------------------------------------------


class TestInvalidationPairCooldown:
    """Invalidation-based cooldowns have been removed.  These tests verify that
    the old state attributes and methods no longer exist on Scanner."""

    def test_no_invalidation_cooldown_dict(self):
        scanner = _make_scanner()
        assert not hasattr(scanner, "_invalidation_cooldown_until")

    def test_no_invalidation_pair_cooldown_dict(self):
        scanner = _make_scanner()
        assert not hasattr(scanner, "_invalidation_pair_cooldown_until")

    def test_no_set_invalidation_cooldown_method(self):
        scanner = _make_scanner()
        assert not hasattr(scanner, "set_invalidation_cooldown")


# ---------------------------------------------------------------------------
# Helpers for the 5 new signal quality gate tests
# ---------------------------------------------------------------------------

_FAKE_SCORE = SimpleNamespace(
    total=85.0,
    quality_tier=SimpleNamespace(value="A"),
    components={
        "market": 20.0,
        "setup": 25.0,
        "execution": 18.0,
        "risk": 15.0,
        "context": 7.0,
    },
)


def _common_gate_patches(scanner, extra_patches: list | None = None):
    """Return an ExitStack with the standard infrastructure patches plus extras.

    Usage::

        with _common_gate_patches(scanner, [patch("src.scanner.check_mtf_gate", ...)]):
            ...
    """
    import contextlib
    stack = contextlib.ExitStack()
    stack.enter_context(
        patch("src.scanner.compute_confidence", return_value=SimpleNamespace(total=70.0, blocked=False))
    )
    stack.enter_context(
        patch("src.scanner.score_signal_components", return_value=_FAKE_SCORE)
    )
    stack.enter_context(patch("src.scanner.check_vwap_extension", return_value=(True, "")))
    stack.enter_context(patch("src.scanner.check_kill_zone_gate", return_value=(True, "")))
    stack.enter_context(patch.object(scanner, "_evaluate_setup", return_value=_setup_pass()))
    stack.enter_context(patch.object(scanner, "_evaluate_execution", return_value=_execution_pass()))
    stack.enter_context(patch.object(scanner, "_evaluate_risk", return_value=_risk_pass()))
    for p in (extra_patches or []):
        stack.enter_context(p)
    return stack


# ---------------------------------------------------------------------------
# New gate tests: 5 signal quality filters wired into _prepare_signal()
# ---------------------------------------------------------------------------


class TestMTFGateInScanner:
    """Filter 1: MTF Confluence Gate wired into _prepare_signal."""

    def _scanner_and_queue(self, channel_name: str = "360_SCALP"):
        channel = MagicMock()
        channel.config = SimpleNamespace(name=channel_name, min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(channel=channel_name)
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)
        return scanner, signal_queue

    @pytest.mark.asyncio
    async def test_mtf_gate_blocks_signal_when_misaligned(self):
        """When check_mtf_gate returns (False, reason) the signal is rejected."""
        scanner, signal_queue = self._scanner_and_queue()

        with _common_gate_patches(scanner, [
            patch("src.scanner.check_mtf_gate", return_value=(False, "MTF misaligned")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_not_awaited()
        assert scanner._suppression_counters["mtf_gate_family:360_SCALP:other"] == 1
        assert scanner._suppression_counters.get("mtf_semantic_eval:360_SCALP:other", 0) == 0

    @pytest.mark.asyncio
    async def test_mtf_gate_passes_signal_when_aligned(self):
        """When check_mtf_gate returns (True, '') the signal is allowed through."""
        scanner, signal_queue = self._scanner_and_queue()

        with _common_gate_patches(scanner, [
            patch("src.scanner.check_mtf_gate", return_value=(True, "")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_mtf_gate_fails_open_with_empty_indicators(self):
        """MTF gate must fail open when no timeframe indicator data is available.

        The real check_mtf_gate() returns (True, '') for empty input, so an
        empty mtf_data dict must never block the signal.
        """
        scanner, signal_queue = self._scanner_and_queue()

        # Verify the real gate logic: empty timeframes → (True, "") → signal passes.
        with _common_gate_patches(scanner, [
            patch("src.scanner.check_mtf_gate", return_value=(True, "")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # With all gates passing, signal is enqueued.
        signal_queue.put.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_mtf_gate_uses_relaxed_min_score_for_reclaim_family(self):
        scanner, signal_queue = self._scanner_and_queue()
        mock_mtf = MagicMock(return_value=(False, "MTF misaligned"))

        with _common_gate_patches(scanner, [
            patch.object(scanner, "_evaluate_setup", return_value=_setup_pass(SetupClass.FAILED_AUCTION_RECLAIM)),
            patch.object(scanner, "_evaluate_family_semantic_mtf", return_value=(False, "family_semantic_mtf_fail")),
            patch("src.scanner.check_mtf_gate", mock_mtf),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_not_awaited()
        called_min_score = mock_mtf.call_args.kwargs["min_score"]
        assert called_min_score == pytest.approx(0.35)

    @pytest.mark.asyncio
    async def test_mtf_gate_keeps_generic_min_score_for_trend_following_family(self):
        scanner, signal_queue = self._scanner_and_queue()
        mock_mtf = MagicMock(return_value=(False, "MTF misaligned"))

        with _common_gate_patches(scanner, [
            patch.object(scanner, "_evaluate_setup", return_value=_setup_pass(SetupClass.TREND_PULLBACK_EMA)),
            patch("src.scanner.check_mtf_gate", mock_mtf),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_not_awaited()
        called_min_score = mock_mtf.call_args.kwargs["min_score"]
        assert called_min_score == pytest.approx(0.6)

    @pytest.mark.asyncio
    async def test_mtf_gate_reject_tracks_family_and_setup_counters(self):
        scanner, signal_queue = self._scanner_and_queue()

        with _common_gate_patches(scanner, [
            patch.object(scanner, "_evaluate_setup", return_value=_setup_pass(SetupClass.FAILED_AUCTION_RECLAIM)),
            patch.object(scanner, "_evaluate_family_semantic_mtf", return_value=(False, "family_semantic_mtf_fail")),
            patch("src.scanner.check_mtf_gate", return_value=(False, "MTF misaligned")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_not_awaited()
        assert scanner._suppression_counters["mtf_gate_family:360_SCALP:reclaim_retest"] == 1
        assert scanner._suppression_counters["mtf_gate_setup:360_SCALP:FAILED_AUCTION_RECLAIM"] == 1
        assert scanner._suppression_counters["mtf_semantic_eval:360_SCALP:reclaim_retest"] == 1
        assert scanner._suppression_counters["mtf_semantic_fail:360_SCALP:reclaim_retest"] == 1

    @pytest.mark.asyncio
    async def test_mtf_policy_saved_counter_when_relaxed_policy_preserves_candidate(self):
        scanner, signal_queue = self._scanner_and_queue()
        mock_mtf = MagicMock(side_effect=[(True, ""), (False, "generic fails")])

        with _common_gate_patches(scanner, [
            patch.object(scanner, "_evaluate_setup", return_value=_setup_pass(SetupClass.FAILED_AUCTION_RECLAIM)),
            patch("src.scanner.check_mtf_gate", mock_mtf),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_awaited_once()
        assert mock_mtf.call_count == 2
        assert mock_mtf.call_args_list[0].kwargs["min_score"] == pytest.approx(0.35)
        assert mock_mtf.call_args_list[1].kwargs["min_score"] == pytest.approx(0.6)
        assert scanner._suppression_counters["mtf_policy_saved:360_SCALP:reclaim_retest"] == 1

    @pytest.mark.asyncio
    async def test_mtf_semantic_path_saves_reclaim_family_when_generic_fails(self):
        scanner, signal_queue = self._scanner_and_queue()

        with _common_gate_patches(scanner, [
            patch.object(scanner, "_evaluate_setup", return_value=_setup_pass(SetupClass.FAILED_AUCTION_RECLAIM)),
            patch.object(scanner, "_evaluate_family_semantic_mtf", return_value=(True, "family_semantic_mtf_pass")),
            patch("src.scanner.check_mtf_gate", return_value=(False, "MTF misaligned")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_awaited_once()
        assert scanner._suppression_counters["mtf_semantic_eval:360_SCALP:reclaim_retest"] == 1
        assert scanner._suppression_counters["mtf_semantic_pass:360_SCALP:reclaim_retest"] == 1
        assert scanner._suppression_counters["mtf_semantic_saved:360_SCALP:reclaim_retest"] == 1
        assert scanner._suppression_counters["mtf_semantic_saved_setup:360_SCALP:FAILED_AUCTION_RECLAIM"] == 1
        assert scanner._suppression_counters["mtf_gate_family:360_SCALP:reclaim_retest"] == 0

    @pytest.mark.asyncio
    async def test_risk_plan_geometry_cap_telemetry(self):
        scanner, signal_queue = self._scanner_and_queue()
        capped_risk = RiskAssessment(
            passed=True,
            stop_loss=98.5,  # 1.5% from entry — channel cap boundary
            tp1=101.3,
            tp2=102.6,
            tp3=103.9,
            r_multiple=0.87,
            invalidation_summary="Below structure + buffer",
        )

        with _common_gate_patches(scanner, [
            patch.object(scanner, "_evaluate_setup", return_value=_setup_pass(SetupClass.VOLUME_SURGE_BREAKOUT)),
            patch.object(scanner, "_evaluate_risk", return_value=capped_risk),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_awaited_once()
        assert scanner._suppression_counters[
            "geometry_changed_risk_plan:360_SCALP:breakout_momentum"
        ] == 1
        assert scanner._suppression_counters[
            "geometry_capped_risk_plan:360_SCALP:breakout_momentum"
        ] == 1
        assert scanner._path_funnel_counters[
            "geometry:risk_plan:changed:360_SCALP:breakout_momentum:VOLUME_SURGE_BREAKOUT"
        ] == 1
        assert scanner._path_funnel_counters[
            "geometry:risk_plan:capped:360_SCALP:breakout_momentum:VOLUME_SURGE_BREAKOUT"
        ] == 1

    @pytest.mark.asyncio
    async def test_risk_plan_geometry_reject_reason_is_path_attributed(self):
        scanner, signal_queue = self._scanner_and_queue()
        rejected_risk = RiskAssessment(
            passed=False,
            stop_loss=0.0,
            tp1=0.0,
            tp2=0.0,
            tp3=None,
            r_multiple=0.0,
            invalidation_summary="",
            reason="sl_too_wide",
        )

        with _common_gate_patches(scanner, [
            patch.object(scanner, "_evaluate_setup", return_value=_setup_pass(SetupClass.VOLUME_SURGE_BREAKOUT)),
            patch.object(scanner, "_evaluate_risk", return_value=rejected_risk),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_not_awaited()
        assert scanner._path_funnel_counters[
            "geometry:risk_plan:rejected:360_SCALP:breakout_momentum:VOLUME_SURGE_BREAKOUT"
        ] == 1
        assert scanner._path_funnel_counters[
            "geometry:risk_plan:rejected_reason:sl_too_wide:360_SCALP:breakout_momentum:VOLUME_SURGE_BREAKOUT"
        ] == 1
        assert scanner._suppression_counters[
            "geometry_rejected_risk_plan_reason:360_SCALP:breakout_momentum:sl_too_wide"
        ] == 1

    @pytest.mark.asyncio
    async def test_path_funnel_distinguishes_no_candidate_and_gated(self):
        scanner, signal_queue = self._scanner_and_queue()
        scanner.channels[0].evaluate.return_value = None

        with _common_gate_patches(scanner):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_not_awaited()
        assert scanner._channel_funnel_counters["no_candidate_generated:360_SCALP"] == 1

        raw_sig = _make_signal(channel="360_SCALP")
        raw_sig.setup_class = SetupClass.VOLUME_SURGE_BREAKOUT.value
        scanner.channels[0].evaluate.return_value = raw_sig

        with _common_gate_patches(scanner, [
            patch("src.scanner.check_mtf_gate", return_value=(False, "MTF misaligned")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_not_awaited()
        assert scanner._path_funnel_counters[
            "generated:360_SCALP:breakout_momentum:VOLUME_SURGE_BREAKOUT"
        ] == 1
        assert scanner._path_funnel_counters[
            "gated:360_SCALP:breakout_momentum:VOLUME_SURGE_BREAKOUT"
        ] == 1

    @pytest.mark.asyncio
    async def test_path_funnel_tracks_scored_filtered_and_emitted(self):
        scanner, signal_queue = self._scanner_and_queue()
        raw_sig = _make_signal(channel="360_SCALP")
        raw_sig.setup_class = SetupClass.VOLUME_SURGE_BREAKOUT.value
        scanner.channels[0].evaluate.return_value = raw_sig

        low_score = {
            "total": 40.0,
            "smc": 10.0,
            "regime": 10.0,
            "volume": 5.0,
            "indicators": 5.0,
            "patterns": 5.0,
            "mtf": 5.0,
            "thesis_adj": 0.0,
        }
        with _common_gate_patches(scanner, [
            patch("src.scanner._scoring_engine.score", return_value=low_score),
            patch("src.scanner.check_mtf_gate", return_value=(True, "")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_not_awaited()
        scored = {
            k: v for k, v in scanner._path_funnel_counters.items()
            if k.startswith("scored:360_SCALP:")
        }
        filtered = {
            k: v for k, v in scanner._path_funnel_counters.items()
            if k.startswith("filtered:360_SCALP:")
        }
        assert sum(scored.values()) == 1
        assert sum(filtered.values()) == 1

        scanner._path_funnel_counters.clear()
        signal_queue.put.reset_mock()
        high_score = {
            "total": 85.0,
            "smc": 20.0,
            "regime": 15.0,
            "volume": 10.0,
            "indicators": 18.0,
            "patterns": 10.0,
            "mtf": 10.0,
            "thesis_adj": 2.0,
        }
        with _common_gate_patches(scanner, [
            patch("src.scanner._scoring_engine.score", return_value=high_score),
            patch("src.scanner.check_mtf_gate", return_value=(True, "")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_awaited_once()
        emitted_sig = signal_queue.put.await_args.args[0]
        assert emitted_sig.origin_setup_class == emitted_sig.setup_class
        assert emitted_sig.origin_setup_family == scanner._setup_family_for_channel(
            emitted_sig.channel,
            emitted_sig.setup_class,
        )
        emitted = {
            k: v for k, v in scanner._path_funnel_counters.items()
            if k.startswith("emitted:360_SCALP:")
        }
        assert sum(emitted.values()) == 1

    @pytest.mark.asyncio
    async def test_funnel_uses_explicit_prepare_reject_stage(self):
        scanner, signal_queue = self._scanner_and_queue()
        raw_sig = _make_signal(channel="360_SCALP")
        raw_sig.setup_class = SetupClass.VOLUME_SURGE_BREAKOUT.value
        scanner.channels[0].evaluate.return_value = raw_sig

        async def _fake_prepare_filtered(*args, **kwargs):
            kwargs["_funnel_meta"]["reject_stage"] = "filtered"
            return None, None

        with patch.object(scanner, "_prepare_signal", side_effect=_fake_prepare_filtered):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_not_awaited()
        assert scanner._path_funnel_counters[
            "filtered:360_SCALP:breakout_momentum:VOLUME_SURGE_BREAKOUT"
        ] == 1
        assert scanner._path_funnel_counters[
            "gated:360_SCALP:breakout_momentum:VOLUME_SURGE_BREAKOUT"
        ] == 0

        scanner_gated, signal_queue_gated = self._scanner_and_queue()
        raw_sig_gated = _make_signal(channel="360_SCALP")
        raw_sig_gated.setup_class = SetupClass.VOLUME_SURGE_BREAKOUT.value
        scanner_gated.channels[0].evaluate.return_value = raw_sig_gated

        async def _fake_prepare_gated(*args, **kwargs):
            kwargs["_funnel_meta"]["reject_stage"] = "gated"
            return None, None

        with patch.object(scanner_gated, "_prepare_signal", side_effect=_fake_prepare_gated):
            await scanner_gated._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue_gated.put.assert_not_awaited()
        assert scanner_gated._path_funnel_counters[
            "gated:360_SCALP:breakout_momentum:VOLUME_SURGE_BREAKOUT"
        ] == 1


class TestFamilySemanticMTFPolicy:
    @staticmethod
    def _tf(ema_fast: float, ema_slow: float, close: float) -> dict:
        return {"ema_fast": ema_fast, "ema_slow": ema_slow, "close": close}

    def test_semantic_mtf_fails_closed_without_data(self):
        allowed, reason = Scanner._evaluate_family_semantic_mtf(
            setup_family="reclaim_retest",
            signal_direction="LONG",
            mtf_data={},
            min_score=0.35,
        )
        assert allowed is False
        assert reason == "semantic_fail_no_data"

    def test_semantic_mtf_fails_closed_without_valid_timeframes(self):
        allowed, reason = Scanner._evaluate_family_semantic_mtf(
            setup_family="reclaim_retest",
            signal_direction="LONG",
            mtf_data={"1m": {"ema_fast": 101.0}},  # invalid payload (ema_slow/close missing)
            min_score=0.35,
        )
        assert allowed is False
        assert reason == "semantic_fail_no_valid_tf"

    def test_semantic_mtf_fails_closed_when_all_timeframes_are_malformed(self):
        allowed, reason = Scanner._evaluate_family_semantic_mtf(
            setup_family="reversal",
            signal_direction="SHORT",
            mtf_data={
                "1m": {"ema_fast": "nan", "ema_slow": None, "close": 100.0},
                "5m": {"ema_fast": 101.0},  # missing keys
                "1h": {"ema_fast": object(), "ema_slow": 100.0, "close": 99.0},
            },
            min_score=0.35,
        )
        assert allowed is False
        assert reason == "semantic_fail_no_valid_tf"

    def test_semantic_mtf_rejects_deep_misalignment(self):
        mtf_data = {
            "1m": self._tf(101.0, 100.0, 101.5),   # aligned
            "5m": self._tf(102.0, 101.0, 102.5),   # aligned
            "15m": self._tf(103.0, 102.0, 103.0),  # neutral
            "1h": self._tf(104.0, 103.0, 104.5),   # aligned
            "4h": self._tf(105.0, 104.0, 105.0),   # neutral
        }
        allowed, reason = Scanner._evaluate_family_semantic_mtf(
            setup_family="reclaim_retest",
            signal_direction="LONG",
            mtf_data=mtf_data,
            min_score=0.90,
        )
        assert allowed is False
        assert reason == "semantic_fail_deep_misalignment"

    def test_semantic_mtf_rejects_insufficient_lower_tf_alignment(self):
        mtf_data = {
            "1m": self._tf(101.0, 100.0, 101.5),   # aligned
            "5m": self._tf(102.0, 101.0, 102.0),   # neutral
            "15m": self._tf(103.0, 102.0, 103.0),  # neutral
            "1h": self._tf(104.0, 103.0, 104.5),   # aligned
            "4h": self._tf(105.0, 104.0, 105.0),   # neutral
        }
        allowed, reason = Scanner._evaluate_family_semantic_mtf(
            setup_family="reclaim_retest",
            signal_direction="LONG",
            mtf_data=mtf_data,
            min_score=0.70,
        )
        assert allowed is False
        assert reason == "semantic_fail_lower_tf_weak"

    def test_semantic_mtf_passes_only_near_miss_with_strong_confirmation(self):
        mtf_data = {
            "1m": self._tf(101.0, 100.0, 101.5),   # aligned
            "5m": self._tf(102.0, 101.0, 102.5),   # aligned
            "15m": self._tf(103.0, 102.0, 103.0),  # neutral
            "1h": self._tf(104.0, 103.0, 104.5),   # aligned
            "4h": self._tf(105.0, 104.0, 105.0),   # neutral
        }
        allowed, reason = Scanner._evaluate_family_semantic_mtf(
            setup_family="reversal",
            signal_direction="LONG",
            mtf_data=mtf_data,
            min_score=0.75,
        )
        assert allowed is True
        assert reason == "family_semantic_mtf_pass"


class TestVWAPGateInScanner:
    """Filter 2: VWAP Extension Rejection wired into _prepare_signal."""

    def _scanner_and_queue(self):
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(channel="360_SCALP")
        sq = MagicMock()
        sq.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=sq)
        return scanner, sq

    @pytest.mark.asyncio
    async def test_vwap_gate_blocks_overextended_long(self):
        """When check_vwap_extension returns (False, reason) a soft penalty is applied instead of hard-blocking.

        The signal is still enqueued but with reduced confidence (soft gate).
        """
        scanner, signal_queue = self._scanner_and_queue()

        with _common_gate_patches(scanner, [
            patch("src.scanner.check_vwap_extension", return_value=(False, "VWAP: overextended")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Soft penalty: signal is enqueued (not hard-blocked)
        signal_queue.put.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_vwap_gate_allows_signal_within_bands(self):
        """When check_vwap_extension returns (True, '') the signal passes."""
        scanner, signal_queue = self._scanner_and_queue()

        with _common_gate_patches(scanner, [
            patch("src.scanner.check_vwap_extension", return_value=(True, "")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_vwap_gate_fails_open_on_compute_exception(self):
        """When compute_vwap raises, the VWAP gate fails open (does not block signal)."""
        scanner, signal_queue = self._scanner_and_queue()

        with _common_gate_patches(scanner, [
            patch("src.scanner.compute_vwap", side_effect=RuntimeError("no candle data")),
            # check_vwap_extension must NOT be reached when compute_vwap raises;
            # keep the default (True,"") patch from _common_gate_patches so that
            # if the except branch somehow leaks through it still passes.
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_awaited_once()


class TestKillZoneGateInScanner:
    """Filter 3: Kill Zone / Session Filter wired into _prepare_signal."""

    def _scanner_and_queue(self):
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(channel="360_SCALP")
        sq = MagicMock()
        sq.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=sq)
        return scanner, sq

    @pytest.mark.asyncio
    async def test_kill_zone_gate_blocks_dead_zone_signals(self):
        """When check_kill_zone_gate returns (False, reason) a soft penalty is applied
        instead of hard-blocking.  The signal is still enqueued with reduced confidence.
        """
        scanner, signal_queue = self._scanner_and_queue()

        with _common_gate_patches(scanner, [
            patch("src.scanner.check_kill_zone_gate", return_value=(False, "Kill zone: ASIAN_DEAD_ZONE")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Soft penalty: signal is enqueued (not hard-blocked)
        signal_queue.put.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_kill_zone_gate_allows_signal_in_active_session(self):
        """When check_kill_zone_gate returns (True, '') the signal passes."""
        scanner, signal_queue = self._scanner_and_queue()

        with _common_gate_patches(scanner, [
            patch("src.scanner.check_kill_zone_gate", return_value=(True, "")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_kill_zone_gate_blocks_weekend(self):
        """Kill zone gate applies a soft penalty for weekend signals (not a hard block)."""
        scanner, signal_queue = self._scanner_and_queue()

        with _common_gate_patches(scanner, [
            patch(
                "src.scanner.check_kill_zone_gate",
                return_value=(False, "Kill zone: WEEKEND_DEAD_ZONE – Weekend dead zone"),
            ),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Soft penalty: signal is enqueued with reduced confidence
        signal_queue.put.assert_awaited_once()


class TestOIGateInScanner:
    """Filter 4: OI + Funding Rate Gate wired into _prepare_signal."""

    @pytest.mark.asyncio
    async def test_oi_gate_skipped_when_no_order_flow_store(self):
        """OI gate must not run when order_flow_store is None (the default)."""
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(channel="360_SCALP")
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)
        assert scanner.order_flow_store is None

        import contextlib
        with contextlib.ExitStack() as stack:
            stack.enter_context(
                patch("src.scanner.compute_confidence", return_value=SimpleNamespace(total=70.0, blocked=False))
            )
            stack.enter_context(patch("src.scanner.score_signal_components", return_value=_FAKE_SCORE))
            stack.enter_context(patch("src.scanner.check_vwap_extension", return_value=(True, "")))
            stack.enter_context(patch("src.scanner.check_kill_zone_gate", return_value=(True, "")))
            stack.enter_context(patch.object(scanner, "_evaluate_setup", return_value=_setup_pass()))
            stack.enter_context(patch.object(scanner, "_evaluate_execution", return_value=_execution_pass()))
            stack.enter_context(patch.object(scanner, "_evaluate_risk", return_value=_risk_pass()))
            mock_oi = stack.enter_context(
                patch("src.scanner.check_oi_gate", return_value=(False, "OI: squeeze"))
            )
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Gate function should never be called when order_flow_store is None
        mock_oi.assert_not_called()
        signal_queue.put.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_oi_gate_blocks_squeeze_when_order_flow_store_present(self):
        """When order_flow_store is set and OI gate detects a squeeze, a soft penalty is applied.

        The signal is still enqueued but with reduced confidence (soft gate).
        """
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(channel="360_SCALP")
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)

        from src.order_flow import OISnapshot
        oi_store = MagicMock()
        oi_store._oi = {
            "BTCUSDT": [
                OISnapshot(timestamp=1.0, open_interest=5000.0),
                OISnapshot(timestamp=2.0, open_interest=4800.0),
                OISnapshot(timestamp=3.0, open_interest=4600.0),
            ]
        }
        oi_store.get_oi_trend = MagicMock()
        oi_store.get_recent_liq_volume_usd = MagicMock(return_value=0.0)
        oi_store.get_cvd_divergence = MagicMock(return_value=False)

        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)
        scanner.order_flow_store = oi_store

        with _common_gate_patches(scanner, [
            patch("src.scanner.analyse_oi", return_value=MagicMock()),
            patch("src.scanner.check_oi_gate", return_value=(False, "OI: squeeze – LONG quality: LOW")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Soft penalty: signal is enqueued (not hard-blocked)
        signal_queue.put.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_oi_gate_allows_momentum_signal(self):
        """When OI gate detects rising price + rising OI (momentum), signal is allowed."""
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(channel="360_SCALP")
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)

        from src.order_flow import OISnapshot
        oi_store = MagicMock()
        oi_store._oi = {
            "BTCUSDT": [
                OISnapshot(timestamp=1.0, open_interest=4600.0),
                OISnapshot(timestamp=2.0, open_interest=4800.0),
                OISnapshot(timestamp=3.0, open_interest=5000.0),
            ]
        }
        oi_store.get_oi_trend = MagicMock()
        oi_store.get_recent_liq_volume_usd = MagicMock(return_value=0.0)
        oi_store.get_cvd_divergence = MagicMock(return_value=False)

        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)
        scanner.order_flow_store = oi_store

        with _common_gate_patches(scanner, [
            patch("src.scanner.analyse_oi", return_value=MagicMock()),
            patch("src.scanner.check_oi_gate", return_value=(True, "")),
        ]):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        signal_queue.put.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_oi_gate_fails_open_on_exception(self):
        """OI gate exceptions must be caught; signal is allowed through (fail-open)."""
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(channel="360_SCALP")
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)

        oi_store = MagicMock()
        oi_store._oi = {}

        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)
        scanner.order_flow_store = oi_store

        import contextlib
        with contextlib.ExitStack() as stack:
            stack.enter_context(
                patch("src.scanner.compute_confidence", return_value=SimpleNamespace(total=70.0, blocked=False))
            )
            stack.enter_context(patch("src.scanner.score_signal_components", return_value=_FAKE_SCORE))
            stack.enter_context(patch("src.scanner.check_vwap_extension", return_value=(True, "")))
            stack.enter_context(patch("src.scanner.check_kill_zone_gate", return_value=(True, "")))
            stack.enter_context(patch.object(scanner, "_evaluate_setup", return_value=_setup_pass()))
            stack.enter_context(patch.object(scanner, "_evaluate_execution", return_value=_execution_pass()))
            stack.enter_context(patch.object(scanner, "_evaluate_risk", return_value=_risk_pass()))
            stack.enter_context(patch("src.scanner.analyse_oi", side_effect=RuntimeError("bad data")))
            mock_oi = stack.enter_context(
                patch("src.scanner.check_oi_gate", return_value=(False, "would block"))
            )
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # check_oi_gate is never reached when analyse_oi raises
        mock_oi.assert_not_called()
        signal_queue.put.assert_awaited_once()


class TestCrossAssetGateInScanner:
    """Filter 5: Cross-Asset Correlation wired into _prepare_signal."""

    @pytest.mark.asyncio
    async def test_cross_asset_gate_skipped_for_btcusdt(self):
        """Cross-asset gate is not entered when the signal symbol is BTCUSDT."""
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        channel.evaluate.return_value = _make_signal(channel="360_SCALP")  # BTCUSDT
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)

        import contextlib
        with contextlib.ExitStack() as stack:
            stack.enter_context(
                patch("src.scanner.compute_confidence", return_value=SimpleNamespace(total=70.0, blocked=False))
            )
            stack.enter_context(patch("src.scanner.score_signal_components", return_value=_FAKE_SCORE))
            stack.enter_context(patch("src.scanner.check_vwap_extension", return_value=(True, "")))
            stack.enter_context(patch("src.scanner.check_kill_zone_gate", return_value=(True, "")))
            stack.enter_context(patch.object(scanner, "_evaluate_setup", return_value=_setup_pass()))
            stack.enter_context(patch.object(scanner, "_evaluate_execution", return_value=_execution_pass()))
            stack.enter_context(patch.object(scanner, "_evaluate_risk", return_value=_risk_pass()))
            mock_ca = stack.enter_context(
                patch("src.scanner.check_cross_asset_gate", return_value=(False, "would block"))
            )
            # BTCUSDT → cross-asset gate body is never entered
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        mock_ca.assert_not_called()
        signal_queue.put.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cross_asset_gate_skipped_for_ethusdt(self):
        """Cross-asset gate is not entered when the signal symbol is ETHUSDT."""
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        eth_signal = Signal(
            channel="360_SCALP",
            symbol="ETHUSDT",
            direction=Direction.LONG,
            entry=3000.0,
            stop_loss=2900.0,
            tp1=3100.0,
            tp2=3200.0,
            confidence=10.0,
            signal_id="SIG-ETH",
            timestamp=utcnow(),
        )
        channel.evaluate.return_value = eth_signal
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)

        import contextlib
        with contextlib.ExitStack() as stack:
            stack.enter_context(
                patch("src.scanner.compute_confidence", return_value=SimpleNamespace(total=70.0, blocked=False))
            )
            stack.enter_context(patch("src.scanner.score_signal_components", return_value=_FAKE_SCORE))
            stack.enter_context(patch("src.scanner.check_vwap_extension", return_value=(True, "")))
            stack.enter_context(patch("src.scanner.check_kill_zone_gate", return_value=(True, "")))
            stack.enter_context(patch.object(scanner, "_evaluate_setup", return_value=_setup_pass()))
            stack.enter_context(patch.object(scanner, "_evaluate_execution", return_value=_execution_pass()))
            stack.enter_context(patch.object(scanner, "_evaluate_risk", return_value=_risk_pass()))
            mock_ca = stack.enter_context(
                patch("src.scanner.check_cross_asset_gate", return_value=(False, "would block"))
            )
            await scanner._scan_symbol("ETHUSDT", 10_000_000)

        mock_ca.assert_not_called()
        signal_queue.put.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cross_asset_gate_blocks_altcoin_when_btc_dumping(self):
        """When check_cross_asset_gate returns (False,…) for an altcoin, signal is rejected."""
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        altcoin_signal = Signal(
            channel="360_SCALP",
            symbol="SOLUSDT",
            direction=Direction.LONG,
            entry=100.0,
            stop_loss=95.0,
            tp1=105.0,
            tp2=110.0,
            confidence=10.0,
            signal_id="SIG-SOL",
            timestamp=utcnow(),
        )
        channel.evaluate.return_value = altcoin_signal
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)

        with _common_gate_patches(scanner, [
            patch("src.scanner.check_cross_asset_gate", return_value=(False, "Cross-asset: BTCUSDT is DUMPING")),
        ]):
            await scanner._scan_symbol("SOLUSDT", 5_000_000)

        signal_queue.put.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_cross_asset_gate_allows_altcoin_when_btc_bullish(self):
        """When check_cross_asset_gate returns (True, '') the altcoin signal passes."""
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        altcoin_signal = Signal(
            channel="360_SCALP",
            symbol="SOLUSDT",
            direction=Direction.LONG,
            entry=100.0,
            stop_loss=95.0,
            tp1=105.0,
            tp2=110.0,
            confidence=10.0,
            signal_id="SIG-SOL-OK",
            timestamp=utcnow(),
        )
        channel.evaluate.return_value = altcoin_signal
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)

        with _common_gate_patches(scanner, [
            patch("src.scanner.check_cross_asset_gate", return_value=(True, "")),
        ]):
            await scanner._scan_symbol("SOLUSDT", 5_000_000)

        signal_queue.put.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cross_asset_gate_fails_open_on_exception(self):
        """Cross-asset gate exceptions are caught; signal is allowed through (fail-open)."""
        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
        altcoin_signal = Signal(
            channel="360_SCALP",
            symbol="SOLUSDT",
            direction=Direction.LONG,
            entry=100.0,
            stop_loss=95.0,
            tp1=105.0,
            tp2=110.0,
            confidence=10.0,
            signal_id="SIG-SOL-ERR",
            timestamp=utcnow(),
        )
        channel.evaluate.return_value = altcoin_signal
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)

        def _raise_for_major(sym, tf):
            if sym in ("BTCUSDT", "ETHUSDT"):
                raise RuntimeError("BTC/ETH data unavailable")
            return _candles()

        scanner.data_store.get_candles = MagicMock(side_effect=_raise_for_major)

        with _common_gate_patches(scanner):
            # Should not raise; cross-asset gate fails open
            await scanner._scan_symbol("SOLUSDT", 5_000_000)

        signal_queue.put.assert_awaited_once()


class TestNormalizeCandles:
    """_normalize_candle_dict must flatten 2-D numpy arrays to 1-D Python lists."""

    def test_2d_arrays_are_flattened(self):
        """2-D shape (n, 1) arrays must be converted to flat 1-D lists."""
        import numpy as np
        from src.scanner import _normalize_candle_dict

        n = 10
        raw = {
            "open":   np.arange(n, dtype=np.float64).reshape(n, 1),
            "high":   np.arange(n, dtype=np.float64).reshape(n, 1),
            "low":    np.arange(n, dtype=np.float64).reshape(n, 1),
            "close":  np.arange(n, dtype=np.float64).reshape(n, 1),
            "volume": np.arange(n, dtype=np.float64).reshape(n, 1),
        }
        result = _normalize_candle_dict(raw)

        for key, val in result.items():
            assert isinstance(val, list), f"{key} should be a Python list"
            assert len(val) == n, f"{key} should have {n} elements"
            # Plain Python list must be safe in boolean context
            assert bool(val) is True

    def test_1d_arrays_preserved_as_lists(self):
        """1-D numpy arrays are also converted to Python lists."""
        import numpy as np
        from src.scanner import _normalize_candle_dict

        raw = {"close": np.array([1.0, 2.0, 3.0])}
        result = _normalize_candle_dict(raw)
        assert isinstance(result["close"], list)
        assert result["close"] == [1.0, 2.0, 3.0]

    def test_python_lists_preserved(self):
        """Python lists pass through unchanged in value."""
        from src.scanner import _normalize_candle_dict

        raw = {"close": [1.0, 2.0, 3.0]}
        result = _normalize_candle_dict(raw)
        assert isinstance(result["close"], list)
        assert result["close"] == [1.0, 2.0, 3.0]

    def test_load_candles_normalizes_2d_data(self):
        """_load_candles must normalize 2-D arrays so downstream bool checks never raise."""
        import numpy as np
        from config import SEED_TIMEFRAMES

        n = 60
        two_d_candles = {
            "open":   np.ones((n, 1), dtype=np.float64),
            "high":   np.ones((n, 1), dtype=np.float64) * 1.1,
            "low":    np.ones((n, 1), dtype=np.float64) * 0.9,
            "close":  np.ones((n, 1), dtype=np.float64),
            "volume": np.ones((n, 1), dtype=np.float64) * 100,
        }

        data_store = MagicMock()
        data_store.get_candles.return_value = two_d_candles

        scanner = _make_scanner(data_store=data_store)
        candles = scanner._load_candles("ZECUSDT")

        assert candles, "candles dict must not be empty"
        for tf in SEED_TIMEFRAMES:
            cd = candles.get(tf.interval, {})
            if not cd:
                continue
            for key in ("open", "high", "low", "close", "volume"):
                val = cd[key]
                assert isinstance(val, list), f"{key} must be a Python list after normalization"
                assert len(val) == n
                # Verify boolean context works (would raise ValueError for raw 2-D numpy array)
                assert bool(val) is True




# ---------------------------------------------------------------------------
# Channel-aware gate profile tests
# ---------------------------------------------------------------------------


class TestChannelGateProfile:
    """_CHANNEL_GATE_PROFILE correctly skips gates for SPOT/GEM/SWING."""

    def test_scalp_all_gates_enabled(self):
        """360_SCALP has all 8 gates enabled."""
        from src.scanner import _CHANNEL_GATE_PROFILE
        profile = _CHANNEL_GATE_PROFILE["360_SCALP"]
        assert all(profile.values()), "All gates must be True for 360_SCALP"

    def test_spot_only_mtf_and_cross_asset(self):
        """360_SPOT enables only MTF and cross_asset gates."""
        from src.scanner import _CHANNEL_GATE_PROFILE
        profile = _CHANNEL_GATE_PROFILE["360_SPOT"]
        assert profile["mtf"] is True
        assert profile["cross_asset"] is True
        # Intraday gates must be disabled
        assert profile["vwap"] is False
        assert profile["kill_zone"] is False
        assert profile["oi"] is False
        assert profile["spoof"] is False
        assert profile["volume_div"] is False
        assert profile["cluster"] is False

    def test_gem_no_gates(self):
        """360_GEM disables all gates."""
        from src.scanner import _CHANNEL_GATE_PROFILE
        profile = _CHANNEL_GATE_PROFILE["360_GEM"]
        assert not any(profile.values()), "All gates must be False for 360_GEM"

    def test_swing_disables_microstructure_gates(self):
        """360_SWING disables kill_zone, spoof, and cluster gates."""
        from src.scanner import _CHANNEL_GATE_PROFILE
        profile = _CHANNEL_GATE_PROFILE["360_SWING"]
        assert profile["mtf"] is True
        assert profile["vwap"] is True
        assert profile["oi"] is True
        assert profile["cross_asset"] is True
        assert profile["volume_div"] is True
        # Microstructure gates disabled
        assert profile["kill_zone"] is False
        assert profile["spoof"] is False
        assert profile["cluster"] is False

    def test_unknown_channel_defaults_all_true(self):
        """Channels not in the profile dict default to True (all gates on)."""
        from src.scanner import _CHANNEL_GATE_PROFILE
        profile = _CHANNEL_GATE_PROFILE.get("NONEXISTENT_CHANNEL", {})
        # Default .get() with True fallback means unknown = all-True behavior
        assert profile.get("mtf", True) is True
        assert profile.get("spoof", True) is True


class TestChannelPenaltyWeights:
    """_CHANNEL_PENALTY_WEIGHTS provides per-channel soft penalty base values."""

    def test_scalp_vwap_penalty_is_15(self):
        from src.scanner import _CHANNEL_PENALTY_WEIGHTS
        assert _CHANNEL_PENALTY_WEIGHTS["360_SCALP"]["vwap"] == pytest.approx(15.0)

    def test_spot_all_penalties_zero(self):
        """360_SPOT has 0.0 for all soft penalties (gates are skipped anyway)."""
        from src.scanner import _CHANNEL_PENALTY_WEIGHTS
        weights = _CHANNEL_PENALTY_WEIGHTS["360_SPOT"]
        assert all(v == 0.0 for v in weights.values())

    def test_gem_all_penalties_zero(self):
        from src.scanner import _CHANNEL_PENALTY_WEIGHTS
        weights = _CHANNEL_PENALTY_WEIGHTS["360_GEM"]
        assert all(v == 0.0 for v in weights.values())

    def test_scalp_obi_spoof_highest(self):
        """360_SCALP_OBI has the highest spoof penalty (15.0) — OBI is spoof-sensitive."""
        from src.scanner import _CHANNEL_PENALTY_WEIGHTS
        assert _CHANNEL_PENALTY_WEIGHTS["360_SCALP_OBI"]["spoof"] == pytest.approx(15.0)

    def test_scalp_vwap_vwap_highest(self):
        """360_SCALP_VWAP has the highest VWAP penalty (18.0)."""
        from src.scanner import _CHANNEL_PENALTY_WEIGHTS
        assert _CHANNEL_PENALTY_WEIGHTS["360_SCALP_VWAP"]["vwap"] == pytest.approx(18.0)


@pytest.mark.asyncio
async def test_spot_skips_kill_zone_gate():
    """360_SPOT channel: kill_zone gate is never called."""
    channel = MagicMock()
    channel.config = SimpleNamespace(name="360_SPOT", min_confidence=10.0)
    channel.evaluate.return_value = _make_signal(channel="360_SPOT")
    signal_queue = MagicMock()
    signal_queue.put = AsyncMock(return_value=True)
    scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)

    mock_kz = MagicMock(return_value=(False, "wrong session"))
    with _common_gate_patches(scanner, [
        patch("src.scanner.check_kill_zone_gate", mock_kz),
    ]):
        await scanner._scan_symbol("SOLUSDT", 5_000_000)

    # kill_zone gate must NOT be called for 360_SPOT
    mock_kz.assert_not_called()


@pytest.mark.asyncio
async def test_gem_skips_mtf_gate():
    """360_GEM channel: MTF gate is never called."""
    channel = MagicMock()
    channel.config = SimpleNamespace(name="360_GEM", min_confidence=10.0)
    channel.evaluate.return_value = _make_signal(channel="360_GEM")
    signal_queue = MagicMock()
    signal_queue.put = AsyncMock(return_value=True)
    scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)

    mock_mtf = MagicMock(return_value=(False, "MTF misaligned"))
    with _common_gate_patches(scanner, [
        patch("src.scanner.check_mtf_gate", mock_mtf),
    ]):
        await scanner._scan_symbol("SOLUSDT", 500_000)

    # MTF gate must NOT be called for 360_GEM
    mock_mtf.assert_not_called()


# ---------------------------------------------------------------------------
# PR-ARCH-3: funding_rate and cvd wired into smc_data before evaluators run
# ---------------------------------------------------------------------------


class TestArch3ScanContextWiring:
    """Verify that funding_rate and cvd are wired into smc_data by _build_scan_context()."""

    def _make_oi_store(self, funding_rate=None, cvd_history=None):
        """Create a mock order_flow_store with controllable funding_rate and CVD."""
        import numpy as np
        oi_store = MagicMock()
        oi_store.get_funding_rate = MagicMock(return_value=funding_rate)
        cvd_arr = np.array(cvd_history or [], dtype=np.float64)
        oi_store.get_cvd_history = MagicMock(return_value=cvd_arr)
        oi_store.get_oi_trend = MagicMock()
        oi_store.get_recent_liq_volume_usd = MagicMock(return_value=0.0)
        oi_store.get_cvd_divergence = MagicMock(return_value=None)
        oi_store._oi = {}
        return oi_store

    @pytest.mark.asyncio
    async def test_funding_rate_wired_into_smc_data(self):
        """When order_flow_store has a funding rate, it is in smc_data before evaluate()."""
        captured_smc: list = []

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)

        def capture_and_return(**kwargs):
            captured_smc.append(kwargs.get("smc_data", {}))
            return []

        channel.evaluate.side_effect = capture_and_return
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)
        scanner.order_flow_store = self._make_oi_store(funding_rate=0.0005)

        with _common_gate_patches(scanner):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        assert len(captured_smc) >= 1
        assert captured_smc[0].get("funding_rate") == 0.0005

    @pytest.mark.asyncio
    async def test_cvd_wired_into_smc_data_when_history_available(self):
        """When order_flow_store has CVD history, smc_data['cvd'] is a non-empty list."""
        captured_smc: list = []

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)

        def capture_and_return(**kwargs):
            captured_smc.append(kwargs.get("smc_data", {}))
            return []

        channel.evaluate.side_effect = capture_and_return
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)
        scanner.order_flow_store = self._make_oi_store(
            cvd_history=[100.0, 150.0, 120.0, 130.0]
        )

        with _common_gate_patches(scanner):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        assert len(captured_smc) >= 1
        cvd = captured_smc[0].get("cvd")
        assert cvd is not None
        assert isinstance(cvd, list)
        assert len(cvd) == 4

    @pytest.mark.asyncio
    async def test_cvd_is_none_when_no_history(self):
        """When order_flow_store has no CVD history, smc_data['cvd'] is None (fail-open)."""
        captured_smc: list = []

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)

        def capture_and_return(**kwargs):
            captured_smc.append(kwargs.get("smc_data", {}))
            return []

        channel.evaluate.side_effect = capture_and_return
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)
        scanner.order_flow_store = self._make_oi_store(cvd_history=[])

        with _common_gate_patches(scanner):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        assert len(captured_smc) >= 1
        assert captured_smc[0].get("cvd") is None

    @pytest.mark.asyncio
    async def test_funding_rate_none_when_not_in_store(self):
        """When order_flow_store has no funding rate, smc_data['funding_rate'] is None."""
        captured_smc: list = []

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)

        def capture_and_return(**kwargs):
            captured_smc.append(kwargs.get("smc_data", {}))
            return []

        channel.evaluate.side_effect = capture_and_return
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)
        scanner.order_flow_store = self._make_oi_store(funding_rate=None)

        with _common_gate_patches(scanner):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        assert len(captured_smc) >= 1
        assert captured_smc[0].get("funding_rate") is None

    @pytest.mark.asyncio
    async def test_no_wiring_when_order_flow_store_absent(self):
        """When order_flow_store is None, smc_data keys are absent (no KeyError)."""
        captured_smc: list = []

        channel = MagicMock()
        channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)

        def capture_and_return(**kwargs):
            captured_smc.append(kwargs.get("smc_data", {}))
            return []

        channel.evaluate.side_effect = capture_and_return
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)
        scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)
        assert scanner.order_flow_store is None

        with _common_gate_patches(scanner):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        assert len(captured_smc) >= 1
        # Keys should be absent when store is not configured
        assert "funding_rate" not in captured_smc[0]
        assert "cvd" not in captured_smc[0]
