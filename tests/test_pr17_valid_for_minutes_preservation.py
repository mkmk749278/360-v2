"""Tests for PR-17: preserve evaluator-authored valid_for_minutes.

Covers:
1. Signal dataclass default is 0 (sentinel meaning "no evaluator value set").
2. build_channel_signal() preserves evaluator-authored valid_for_minutes
   from the signal_params table (e.g. WHALE_MOMENTUM VOLATILE → 3 min).
3. _populate_signal_context() applies the per-channel SIGNAL_VALID_FOR_MINUTES
   fallback only when valid_for_minutes is still 0 (no evaluator value).
4. _populate_signal_context() does NOT overwrite a value already set by the
   evaluator — this is the exact overwrite bug PR-17 fixes.
5. No regression: signals without an evaluator-authored value still receive the
   channel default (15 min for scalp channels).
"""
from __future__ import annotations

from types import SimpleNamespace

from config import CHANNEL_SCALP, SIGNAL_VALID_FOR_MINUTES
from src.channels.base import Direction, Signal, build_channel_signal
from src.scanner import Scanner


# ---------------------------------------------------------------------------
# Minimal ScanContext stand-in for _populate_signal_context tests
# ---------------------------------------------------------------------------

def _make_ctx(channel: str = "360_SCALP") -> SimpleNamespace:
    """Minimal mock of ScanContext sufficient for _populate_signal_context."""
    return SimpleNamespace(
        market_state=SimpleNamespace(value="TRENDING"),
        regime_context=None,
        smc_result=SimpleNamespace(sweeps=[], fvg=[]),
        spread_pct=0.05,
        pair_quality=SimpleNamespace(score=70.0, label="GOOD"),
    )


def _make_scanner_sig(channel: str = "360_SCALP", valid_for_minutes: int = 0) -> SimpleNamespace:
    """Minimal signal with a controllable valid_for_minutes value."""
    return SimpleNamespace(
        channel=channel,
        valid_for_minutes=valid_for_minutes,
        market_phase="",
        regime_context="",
        liquidity_info="",
        spread_pct=0.0,
        volume_24h_usd=0.0,
        pair_quality_score=0.0,
        pair_quality_label="",
    )


def _call_populate(sig: SimpleNamespace, channel: str = "360_SCALP") -> None:
    """Exercise Scanner._populate_signal_context() with a minimal mock."""
    ctx = _make_ctx(channel)
    Scanner._populate_signal_context(None, sig, volume_24h=1_000_000.0, ctx=ctx)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Helper for build_channel_signal-based signals (no scanner context)
# ---------------------------------------------------------------------------

def _build_scalp_signal(setup_class: str, regime: str) -> Signal | None:
    close = 100.0
    sl_dist = 0.5
    sl = close - sl_dist
    tp1 = close + sl_dist * CHANNEL_SCALP.tp_ratios[0]
    tp2 = close + sl_dist * CHANNEL_SCALP.tp_ratios[1]
    tp3 = close + sl_dist * CHANNEL_SCALP.tp_ratios[2]
    return build_channel_signal(
        config=CHANNEL_SCALP,
        symbol="BTCUSDT",
        direction=Direction.LONG,
        close=close,
        sl=sl,
        tp1=tp1,
        tp2=tp2,
        tp3=tp3,
        sl_dist=sl_dist,
        id_prefix="PR17",
        atr_val=0.5,
        setup_class=setup_class,
        regime=regime,
    )


# ---------------------------------------------------------------------------
# 1. Signal dataclass sentinel
# ---------------------------------------------------------------------------

class TestSignalDefaultSentinel:
    """Signal.valid_for_minutes default must be 0 (the 'not yet set' sentinel)."""

    def test_signal_default_valid_for_minutes_is_zero(self):
        """Signal() without explicit valid_for_minutes must default to 0.

        This is the sentinel value that tells _populate_signal_context() to
        apply the per-channel fallback.  Any non-zero value means an evaluator
        explicitly authored it and must not be overwritten.
        """
        sig = Signal(
            channel="360_SCALP",
            symbol="BTCUSDT",
            direction=Direction.LONG,
            entry=100.0,
            stop_loss=99.0,
            tp1=101.0,
            tp2=102.0,
            tp3=103.0,
            confidence=75.0,
        )
        assert sig.valid_for_minutes == 0, (
            "Signal.valid_for_minutes must default to 0 (PR-17 sentinel). "
            "A zero value signals to the scanner that no evaluator has set it yet."
        )


# ---------------------------------------------------------------------------
# 2. build_channel_signal preserves evaluator-authored value
# ---------------------------------------------------------------------------

class TestBuildChannelSignalPreservesEvaluatorValue:
    """build_channel_signal must honour validity_minutes from signal_params table."""

    def test_whale_momentum_volatile_sets_3_minutes(self):
        """WHALE_MOMENTUM + VOLATILE → validity_minutes=3 from params table."""
        sig = _build_scalp_signal("WHALE_MOMENTUM", "VOLATILE")
        assert sig is not None
        assert sig.valid_for_minutes == 3, (
            "build_channel_signal must set valid_for_minutes=3 for "
            "WHALE_MOMENTUM + VOLATILE as specified in the signal_params table."
        )

    def test_no_params_entry_leaves_sentinel(self):
        """When no params entry specifies validity_minutes, signal stays at sentinel 0.

        Downstream code (_populate_signal_context) will then apply the channel
        default — this is the intended fallback path.
        """
        sig = _build_scalp_signal("UNKNOWN_SETUP", "TRENDING")
        assert sig is not None
        assert sig.valid_for_minutes == 0, (
            "build_channel_signal must leave valid_for_minutes=0 when the "
            "signal_params table does not specify validity_minutes, so that "
            "_populate_signal_context() can apply the correct channel default."
        )


# ---------------------------------------------------------------------------
# 3. _populate_signal_context applies channel default when sentinel is 0
# ---------------------------------------------------------------------------

class TestPopulateSignalContextDefaultFallback:
    """_populate_signal_context must apply the channel default when no evaluator value."""

    def test_sentinel_zero_receives_channel_default(self):
        """Signal with valid_for_minutes=0 must receive the 360_SCALP channel default."""
        sig = _make_scanner_sig(channel="360_SCALP", valid_for_minutes=0)
        _call_populate(sig)
        expected = SIGNAL_VALID_FOR_MINUTES.get("360_SCALP", 15)
        assert sig.valid_for_minutes == expected, (
            f"_populate_signal_context must apply SIGNAL_VALID_FOR_MINUTES[360_SCALP]="
            f"{expected} when signal carries the sentinel value 0."
        )

    def test_unknown_channel_gets_hardcoded_fallback(self):
        """An unknown channel must receive the hardcoded fallback of 15."""
        sig = _make_scanner_sig(channel="UNKNOWN_CHANNEL", valid_for_minutes=0)
        _call_populate(sig)
        assert sig.valid_for_minutes == 15, (
            "_populate_signal_context must fall back to 15 minutes for channels "
            "not present in SIGNAL_VALID_FOR_MINUTES."
        )


# ---------------------------------------------------------------------------
# 4. _populate_signal_context must NOT overwrite evaluator-authored value
# ---------------------------------------------------------------------------

class TestPopulateSignalContextPreservesEvaluatorValue:
    """This is the core PR-17 fix: evaluator-authored values must survive."""

    def test_evaluator_value_3_not_overwritten(self):
        """An evaluator-authored valid_for_minutes=3 must not be overwritten to 15."""
        sig = _make_scanner_sig(channel="360_SCALP", valid_for_minutes=3)
        _call_populate(sig)
        assert sig.valid_for_minutes == 3, (
            "_populate_signal_context must NOT overwrite an evaluator-authored "
            "valid_for_minutes=3 with the channel default. "
            "This is the exact bug PR-17 fixes."
        )

    def test_evaluator_value_60_not_overwritten(self):
        """An evaluator-authored valid_for_minutes=60 must not be overwritten."""
        sig = _make_scanner_sig(channel="360_SCALP", valid_for_minutes=60)
        _call_populate(sig)
        assert sig.valid_for_minutes == 60, (
            "_populate_signal_context must not overwrite valid_for_minutes=60 "
            "that was set by the evaluator."
        )

    def test_whale_momentum_value_survives_full_pipeline(self):
        """WHALE_MOMENTUM value=3 from build_channel_signal must survive _populate_signal_context.

        This is the end-to-end regression test for PR-17.  Previously,
        _populate_signal_context() would unconditionally overwrite 3 → 15.
        """
        sig = _build_scalp_signal("WHALE_MOMENTUM", "VOLATILE")
        assert sig is not None
        assert sig.valid_for_minutes == 3, (
            "After build_channel_signal, valid_for_minutes must already be 3."
        )

        # Simulate what the scanner does next:
        ctx = _make_ctx()
        Scanner._populate_signal_context(  # type: ignore[arg-type]
            None, sig, volume_24h=1_000_000.0, ctx=ctx
        )

        assert sig.valid_for_minutes == 3, (
            "WHALE_MOMENTUM evaluator set valid_for_minutes=3 via signal_params. "
            "_populate_signal_context must not overwrite it with the channel "
            "default of 15. This is the PR-17 fix."
        )


# ---------------------------------------------------------------------------
# 5. Regression: non-evaluator signals still get channel default
# ---------------------------------------------------------------------------

class TestNoRegressionDefaultFallback:
    """Signals without an evaluator-authored value must still receive channel default."""

    def test_plain_scalp_signal_gets_15(self):
        """A plain SCALP signal (no params entry) must get valid_for_minutes=15."""
        sig = _build_scalp_signal("UNKNOWN_SETUP", "TRENDING")
        assert sig is not None
        assert sig.valid_for_minutes == 0  # sentinel before context population

        ctx = _make_ctx()
        Scanner._populate_signal_context(  # type: ignore[arg-type]
            None, sig, volume_24h=1_000_000.0, ctx=ctx
        )

        assert sig.valid_for_minutes == SIGNAL_VALID_FOR_MINUTES.get("360_SCALP", 15), (
            "Signals without an evaluator-authored valid_for_minutes must still "
            "receive the channel default after _populate_signal_context()."
        )
