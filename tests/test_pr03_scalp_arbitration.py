"""PR-03 tests: Quality-ranked arbitration for same-direction 360_SCALP candidates.

Validates the five required invariants from the PR-03 specification:

1. When two same-direction 360_SCALP candidates survive, the higher-quality
   candidate is kept even if it was evaluated later (method order does not win).
2. Method order no longer determines the surviving candidate (confirmed by
   testing both orderings: weak-first and strong-first).
3. Opposite-direction candidates are not incorrectly merged into the same
   arbitration bucket — LONG and SHORT winners both reach the signal queue.
4. Existing global cooldown behaviour is preserved — candidates that fall
   inside the directional cooldown window are not emitted regardless of quality.
5. Arbitration decisions are observable via debug log messages (suppression and
   replacement messages are emitted when a weaker candidate is discarded).
"""

from __future__ import annotations

import dataclasses
from types import SimpleNamespace
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.channels.base import Signal
from src.smc import Direction


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_raw_signal(
    *,
    direction: Direction = Direction.LONG,
    confidence: float = 70.0,
    setup_class: str = "SETUP_A",
    symbol: str = "BTCUSDT",
) -> Signal:
    """Minimal raw 360_SCALP candidate as returned by ScalpChannel.evaluate()."""
    return Signal(
        channel="360_SCALP",
        symbol=symbol,
        direction=direction,
        entry=100.0,
        stop_loss=95.0,
        tp1=105.0,
        tp2=110.0,
        confidence=confidence,
        signal_id=f"SIG-{setup_class}",
        setup_class=setup_class,
    )


def _prepared_from(raw: Signal) -> Signal:
    """Return a prepared copy of a raw signal (confidence & setup_class unchanged)."""
    return dataclasses.replace(raw)


def _make_scanner(raw_signals: list, *, signal_queue: Optional[MagicMock] = None):
    """Build a minimal Scanner whose 360_SCALP channel returns `raw_signals`.

    The ``_prepare_signal`` method is NOT mocked here — callers should patch it
    inside their test bodies when they need controlled confidence values.
    """
    from src.scanner import Scanner

    if signal_queue is None:
        signal_queue = MagicMock()
        signal_queue.put = AsyncMock(return_value=True)

    channel = MagicMock()
    channel.config = SimpleNamespace(name="360_SCALP", min_confidence=10.0)
    channel.evaluate.return_value = raw_signals

    candles_tf = {
        "high": [float(i + 1) for i in range(40)],
        "low": [float(i) for i in range(40)],
        "close": [float(i + 1) for i in range(40)],
        "volume": [100.0] * 40,
        "open": [float(i + 1) for i in range(40)],
    }
    candles_store = {tf: candles_tf for tf in ("5m", "15m", "1h", "4h")}

    smc_result = SimpleNamespace(
        sweeps=[SimpleNamespace(direction=Direction.LONG, sweep_level=95.0)],
        fvg=[],
        mss=SimpleNamespace(direction=Direction.LONG, midpoint=98.0),
        as_dict=lambda: {
            "sweeps": [],
            "fvg": [],
            "mss": None,
            "funding_rate": 0.0,
            "cvd": 0.0,
        },
    )

    scanner = Scanner(
        pair_mgr=MagicMock(
            has_enough_history=MagicMock(return_value=True),
            pairs={},
        ),
        data_store=MagicMock(
            get_candles=MagicMock(side_effect=lambda _sym, _tf: candles_store.get(_tf, candles_tf)),
            ticks={"BTCUSDT": []},
        ),
        channels=[channel],
        smc_detector=MagicMock(detect=MagicMock(return_value=smc_result)),
        regime_detector=MagicMock(
            classify=MagicMock(
                return_value=SimpleNamespace(
                    regime=SimpleNamespace(value="TRENDING_UP")
                )
            )
        ),
        predictive=MagicMock(
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
        ),
        exchange_mgr=MagicMock(
            verify_signal_cross_exchange=AsyncMock(return_value=True)
        ),
        spot_client=MagicMock(),
        signal_queue=signal_queue,
        router=MagicMock(
            active_signals={},
            cleanup_expired=MagicMock(return_value=0),
        ),
        telemetry=MagicMock(),
    )
    return scanner, signal_queue, channel


def _make_prepare_side_effect(mapping: dict):
    """Return an AsyncMock side_effect that maps raw signal id → (prepared_sig, None).

    ``mapping`` must be ``{id(raw_signal): prepared_signal, ...}``.
    Unknown raw signals return ``(None, None)``.
    """
    async def _side_effect(symbol, volume_24h, chan, ctx, _preseed_signal=None):
        if _preseed_signal is None:
            return None, None
        return mapping.get(id(_preseed_signal), (None, None))

    return _side_effect


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestScalpArbitrationQualityRanked:
    """Test 1 & 2 — quality wins regardless of evaluation order."""

    @pytest.mark.asyncio
    async def test_weaker_first_stronger_second_keeps_stronger(self):
        """When weak candidate is first and strong is second, strong wins."""
        weak_raw = _make_raw_signal(confidence=60.0, setup_class="WEAK_SETUP")
        strong_raw = _make_raw_signal(confidence=80.0, setup_class="STRONG_SETUP")

        weak_prep = _prepared_from(weak_raw)
        strong_prep = _prepared_from(strong_raw)

        scanner, signal_queue, _ = _make_scanner([weak_raw, strong_raw])

        mapping = {
            id(weak_raw): (weak_prep, None),
            id(strong_raw): (strong_prep, None),
        }
        with patch.object(scanner, "_prepare_signal", side_effect=_make_prepare_side_effect(mapping)):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        assert signal_queue.put.await_count == 1
        emitted = signal_queue.put.call_args[0][0]
        assert emitted.setup_class == "STRONG_SETUP"
        assert emitted.confidence == 80.0

    @pytest.mark.asyncio
    async def test_stronger_first_weaker_second_keeps_stronger(self):
        """When strong candidate is first and weak is second, strong still wins."""
        strong_raw = _make_raw_signal(confidence=80.0, setup_class="STRONG_SETUP")
        weak_raw = _make_raw_signal(confidence=60.0, setup_class="WEAK_SETUP")

        strong_prep = _prepared_from(strong_raw)
        weak_prep = _prepared_from(weak_raw)

        scanner, signal_queue, _ = _make_scanner([strong_raw, weak_raw])

        mapping = {
            id(strong_raw): (strong_prep, None),
            id(weak_raw): (weak_prep, None),
        }
        with patch.object(scanner, "_prepare_signal", side_effect=_make_prepare_side_effect(mapping)):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        assert signal_queue.put.await_count == 1
        emitted = signal_queue.put.call_args[0][0]
        assert emitted.setup_class == "STRONG_SETUP"
        assert emitted.confidence == 80.0

    @pytest.mark.asyncio
    async def test_equal_confidence_keeps_first(self):
        """When candidates have equal confidence, the first-evaluated one is retained
        (deterministic tie-breaker — Python dict insertion order is stable)."""
        first_raw = _make_raw_signal(confidence=75.0, setup_class="FIRST_SETUP")
        second_raw = _make_raw_signal(confidence=75.0, setup_class="SECOND_SETUP")

        first_prep = _prepared_from(first_raw)
        second_prep = _prepared_from(second_raw)

        scanner, signal_queue, _ = _make_scanner([first_raw, second_raw])

        mapping = {
            id(first_raw): (first_prep, None),
            id(second_raw): (second_prep, None),
        }
        with patch.object(scanner, "_prepare_signal", side_effect=_make_prepare_side_effect(mapping)):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        assert signal_queue.put.await_count == 1
        emitted = signal_queue.put.call_args[0][0]
        assert emitted.setup_class == "FIRST_SETUP"

    @pytest.mark.asyncio
    async def test_all_candidates_prepared_before_arbitration(self):
        """All candidates are prepared/scored (not just the first) so the best can win."""
        weak_raw = _make_raw_signal(confidence=60.0, setup_class="WEAK_SETUP")
        strong_raw = _make_raw_signal(confidence=80.0, setup_class="STRONG_SETUP")

        weak_prep = _prepared_from(weak_raw)
        strong_prep = _prepared_from(strong_raw)

        scanner, signal_queue, _ = _make_scanner([weak_raw, strong_raw])

        call_order = []

        async def _tracking_prepare(symbol, volume_24h, chan, ctx, _preseed_signal=None):
            mapping = {
                id(weak_raw): (weak_prep, None),
                id(strong_raw): (strong_prep, None),
            }
            result = mapping.get(id(_preseed_signal), (None, None))
            call_order.append(getattr(_preseed_signal, "setup_class", "?"))
            return result

        with patch.object(scanner, "_prepare_signal", side_effect=_tracking_prepare):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Both candidates must have been prepared (not short-circuited after first)
        assert "WEAK_SETUP" in call_order
        assert "STRONG_SETUP" in call_order


class TestScalpArbitrationOppositeDirections:
    """Test 3 — opposite-direction candidates are kept in separate arbitration buckets."""

    @pytest.mark.asyncio
    async def test_long_and_short_both_emitted(self):
        """A LONG winner and a SHORT winner are both emitted as separate signals."""
        long_raw = _make_raw_signal(direction=Direction.LONG, confidence=70.0, setup_class="LONG_SETUP")
        short_raw = _make_raw_signal(direction=Direction.SHORT, confidence=75.0, setup_class="SHORT_SETUP")

        long_prep = _prepared_from(long_raw)
        short_prep = _prepared_from(short_raw)

        scanner, signal_queue, _ = _make_scanner([long_raw, short_raw])

        mapping = {
            id(long_raw): (long_prep, None),
            id(short_raw): (short_prep, None),
        }
        with patch.object(scanner, "_prepare_signal", side_effect=_make_prepare_side_effect(mapping)):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Both directions should be enqueued
        assert signal_queue.put.await_count == 2
        emitted_classes = {
            c[0][0].setup_class for c in signal_queue.put.call_args_list
        }
        assert "LONG_SETUP" in emitted_classes
        assert "SHORT_SETUP" in emitted_classes

    @pytest.mark.asyncio
    async def test_same_direction_not_cross_contaminated_by_opposite(self):
        """Arbitration for LONG does not affect the SHORT winner and vice versa."""
        strong_long = _make_raw_signal(direction=Direction.LONG, confidence=80.0, setup_class="STRONG_LONG")
        weak_long = _make_raw_signal(direction=Direction.LONG, confidence=60.0, setup_class="WEAK_LONG")
        short_raw = _make_raw_signal(direction=Direction.SHORT, confidence=70.0, setup_class="SHORT_SETUP")

        scanner, signal_queue, _ = _make_scanner([weak_long, strong_long, short_raw])

        mapping = {
            id(weak_long): (_prepared_from(weak_long), None),
            id(strong_long): (_prepared_from(strong_long), None),
            id(short_raw): (_prepared_from(short_raw), None),
        }
        with patch.object(scanner, "_prepare_signal", side_effect=_make_prepare_side_effect(mapping)):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        assert signal_queue.put.await_count == 2
        emitted_classes = {
            c[0][0].setup_class for c in signal_queue.put.call_args_list
        }
        assert "STRONG_LONG" in emitted_classes
        assert "SHORT_SETUP" in emitted_classes
        assert "WEAK_LONG" not in emitted_classes


class TestScalpArbitrationCooldownPreserved:
    """Test 4 — existing global cooldown behaviour is preserved."""

    @pytest.mark.asyncio
    async def test_cooldown_blocks_all_same_direction_candidates(self):
        """When a direction is in global cooldown, no candidate for that direction passes."""
        import time
        weak_raw = _make_raw_signal(confidence=60.0, setup_class="WEAK_SETUP")
        strong_raw = _make_raw_signal(confidence=90.0, setup_class="STRONG_SETUP")

        weak_prep = _prepared_from(weak_raw)
        strong_prep = _prepared_from(strong_raw)

        scanner, signal_queue, _ = _make_scanner([weak_raw, strong_raw])
        # Put LONG direction in global cooldown
        from src.scanner import GLOBAL_SYMBOL_COOLDOWN_SECONDS
        scanner._global_symbol_cooldown[("BTCUSDT", "LONG")] = (
            time.monotonic() + GLOBAL_SYMBOL_COOLDOWN_SECONDS
        )

        mapping = {
            id(weak_raw): (weak_prep, None),
            id(strong_raw): (strong_prep, None),
        }
        with patch.object(scanner, "_prepare_signal", side_effect=_make_prepare_side_effect(mapping)):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # No signals should be emitted — cooldown blocks both
        assert signal_queue.put.await_count == 0

    @pytest.mark.asyncio
    async def test_cooldown_on_one_direction_does_not_block_opposite(self):
        """Cooldown on LONG does not prevent the SHORT candidate from being emitted."""
        import time
        long_raw = _make_raw_signal(direction=Direction.LONG, confidence=80.0, setup_class="LONG_SETUP")
        short_raw = _make_raw_signal(direction=Direction.SHORT, confidence=75.0, setup_class="SHORT_SETUP")

        scanner, signal_queue, _ = _make_scanner([long_raw, short_raw])
        from src.scanner import GLOBAL_SYMBOL_COOLDOWN_SECONDS
        scanner._global_symbol_cooldown[("BTCUSDT", "LONG")] = (
            time.monotonic() + GLOBAL_SYMBOL_COOLDOWN_SECONDS
        )

        mapping = {
            id(long_raw): (_prepared_from(long_raw), None),
            id(short_raw): (_prepared_from(short_raw), None),
        }
        with patch.object(scanner, "_prepare_signal", side_effect=_make_prepare_side_effect(mapping)):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Only SHORT should be emitted
        assert signal_queue.put.await_count == 1
        emitted = signal_queue.put.call_args[0][0]
        assert emitted.setup_class == "SHORT_SETUP"


class TestScalpArbitrationObservability:
    """Test 5 — arbitration decisions are observable via log messages."""

    @pytest.mark.asyncio
    async def test_suppression_logged_when_weaker_candidate_discarded(self):
        """A debug log is emitted when a lower-confidence candidate is suppressed."""
        from loguru import logger as _loguru_logger

        weak_raw = _make_raw_signal(confidence=60.0, setup_class="WEAK_SETUP")
        strong_raw = _make_raw_signal(confidence=80.0, setup_class="STRONG_SETUP")

        weak_prep = _prepared_from(weak_raw)
        strong_prep = _prepared_from(strong_raw)

        scanner, signal_queue, _ = _make_scanner([weak_raw, strong_raw])

        mapping = {
            id(weak_raw): (weak_prep, None),
            id(strong_raw): (strong_prep, None),
        }

        debug_messages: list = []
        handler_id = _loguru_logger.add(
            lambda record: debug_messages.append(record),
            level="DEBUG",
            format="{message}",
        )
        try:
            with patch.object(scanner, "_prepare_signal", side_effect=_make_prepare_side_effect(mapping)):
                await scanner._scan_symbol("BTCUSDT", 10_000_000)
        finally:
            _loguru_logger.remove(handler_id)

        arbitration_msgs = [
            str(m) for m in debug_messages
            if "arbitration" in str(m).lower() or "suppressed" in str(m).lower()
        ]
        assert len(arbitration_msgs) >= 1, (
            "Expected at least one arbitration/suppression log; got:\n"
            + "\n".join(str(m) for m in debug_messages[-20:])
        )

    @pytest.mark.asyncio
    async def test_replacement_logged_when_better_candidate_found(self):
        """A debug log is emitted when a higher-confidence candidate replaces an earlier one."""
        from loguru import logger as _loguru_logger

        first_raw = _make_raw_signal(confidence=60.0, setup_class="FIRST_SETUP")
        better_raw = _make_raw_signal(confidence=80.0, setup_class="BETTER_SETUP")

        scanner, signal_queue, _ = _make_scanner([first_raw, better_raw])

        mapping = {
            id(first_raw): (_prepared_from(first_raw), None),
            id(better_raw): (_prepared_from(better_raw), None),
        }

        debug_messages: list = []
        handler_id = _loguru_logger.add(
            lambda record: debug_messages.append(record),
            level="DEBUG",
            format="{message}",
        )
        try:
            with patch.object(scanner, "_prepare_signal", side_effect=_make_prepare_side_effect(mapping)):
                await scanner._scan_symbol("BTCUSDT", 10_000_000)
        finally:
            _loguru_logger.remove(handler_id)

        replace_msgs = [
            str(m) for m in debug_messages
            if "replaces" in str(m).lower()
        ]
        assert len(replace_msgs) >= 1, (
            "Expected at least one 'replaces' arbitration log; got:\n"
            + "\n".join(str(m) for m in debug_messages[-20:])
        )

    @pytest.mark.asyncio
    async def test_setup_eval_counts_tracks_only_winner(self):
        """_setup_eval_counts is incremented only for the arbitration winner, not the loser."""
        weak_raw = _make_raw_signal(confidence=60.0, setup_class="WEAK_SETUP")
        strong_raw = _make_raw_signal(confidence=80.0, setup_class="STRONG_SETUP")

        scanner, signal_queue, _ = _make_scanner([weak_raw, strong_raw])

        mapping = {
            id(weak_raw): (_prepared_from(weak_raw), None),
            id(strong_raw): (_prepared_from(strong_raw), None),
        }
        with patch.object(scanner, "_prepare_signal", side_effect=_make_prepare_side_effect(mapping)):
            await scanner._scan_symbol("BTCUSDT", 10_000_000)

        # Only the winner's setup class should appear in eval counts
        assert scanner._setup_eval_counts.get("STRONG_SETUP", 0) == 1
        assert scanner._setup_eval_counts.get("WEAK_SETUP", 0) == 0
