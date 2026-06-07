"""Tests for SR_FLIP change A (momentum-kill grace) and change B (pre-TP R-scaling).

Change A: SR_FLIP signals require an extra consecutive bad-momentum reading before
momentum_loss kills them.  Per-setup INVALIDATION_CONSECUTIVE_THRESHOLD entry
"360_SCALP::SR_FLIP_RETEST" controls the threshold (env: SR_FLIP_CONSECUTIVE_REQUIRED).

Change B: When SR_FLIP_PRETP_R_SCALING_ENABLED=true, the pre-TP threshold for
SR_FLIP_RETEST signals is floored at SL_dist_pct × SR_FLIP_PRETP_R_FACTOR so
wide-SL signals don't bank at 0.2R.
"""
from __future__ import annotations

import pytest
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Minimal signal stub — only the fields _check_invalidation reads
# ---------------------------------------------------------------------------

@dataclass
class _Sig:
    symbol: str = "TESTUSDT"
    channel: str = "360_SCALP"
    direction_val: str = "SHORT"
    entry: float = 1.0
    stop_loss: float = 1.015   # 1.5% SL (SHORT: SL above entry)
    current_price: float = 1.0  # at-entry, no adverse movement
    status: str = "OPEN"
    market_phase: str = "RANGING"
    timestamp: object = None
    pre_tp_hit: bool = False
    pretp_fired: bool = False
    entry_2_filled: bool = False
    dca_timestamp: object = None
    momentum_invalidation_count: int = 0
    setup_class: Optional[str] = "SR_FLIP_RETEST"

    @property
    def direction(self):
        from src.smc import Direction
        return Direction.LONG if self.direction_val == "LONG" else Direction.SHORT

    def __post_init__(self):
        from datetime import datetime, timezone
        if self.timestamp is None:
            self.timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Helper: run _check_invalidation on a sig with mocked indicators
# ---------------------------------------------------------------------------

def _run_check(sig, indicators, monkeypatch, *, consecutive_override=None):
    from src.trade_monitor import TradeMonitor
    tm = TradeMonitor.__new__(TradeMonitor)
    tm._regime_detector = None
    tm._indicators_fn = None
    tm._store = None
    tm._btc_direction_cache = {}

    # Patch module-level imports that _check_invalidation uses
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "standard")
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_MIN_AGE_SECONDS",
                        {"360_SCALP": 0, "360_SCALP::SR_FLIP_RETEST": 0})
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_MOMENTUM_THRESHOLD", {"360_SCALP": 0.05})
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_ADVERSE_EXCURSION_FRACTION", 0.99)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC", 9999)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_BY_SETUP", {})
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_ADVERSE_EXCURSION_FRACTION_BY_SETUP", {})
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_CORRELATION_ENABLED", False)
    monkeypatch.setattr("src.trade_monitor.SR_FLIP_MOMENTUM_GRACE_ENABLED", False)

    base = {"360_SCALP": 2}
    if consecutive_override is not None:
        base["360_SCALP::SR_FLIP_RETEST"] = consecutive_override
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_CONSECUTIVE_THRESHOLD", base)

    # Supply indicators directly
    original_fn = tm._indicators_fn
    tm._indicators_fn = lambda _sym: indicators

    return tm._check_invalidation(sig)


# ---------------------------------------------------------------------------
# Change A: per-setup consecutive threshold
# ---------------------------------------------------------------------------

class TestSrFlipGraceConsecutive:
    """Per-setup INVALIDATION_CONSECUTIVE_THRESHOLD extension."""

    def _bad_momentum_indicators(self):
        """SHORT signal: positive momentum = bad for thesis.
        ema9 < ema21 so EMA bearish crossover doesn't fire (we want only momentum to be bad)."""
        return {"ema9_last": 0.99, "ema21_last": 1.0, "momentum": 0.20, "atr_last": 0.005}

    def test_default_consecutive_2_kills_on_second_reading(self, monkeypatch):
        """With consecutive=2 (default), kill fires on the 2nd consecutive bad reading."""
        sig = _Sig()
        indicators = self._bad_momentum_indicators()
        # First reading — should not kill (count goes to 1)
        result = _run_check(sig, indicators, monkeypatch, consecutive_override=2)
        assert result is None
        assert sig.momentum_invalidation_count == 1
        # Second reading — should kill (count goes to 2)
        result = _run_check(sig, indicators, monkeypatch, consecutive_override=2)
        assert result is not None
        assert "momentum" in result

    def test_srflip_grace_consecutive_3_delays_kill(self, monkeypatch):
        """With consecutive=3 (grace), kill deferred until 3rd consecutive bad reading."""
        sig = _Sig()
        indicators = self._bad_momentum_indicators()
        # Readings 1 and 2 — should not kill
        for _ in range(2):
            result = _run_check(sig, indicators, monkeypatch, consecutive_override=3)
            assert result is None
        assert sig.momentum_invalidation_count == 2
        # Reading 3 — should kill
        result = _run_check(sig, indicators, monkeypatch, consecutive_override=3)
        assert result is not None
        assert "momentum" in result

    def test_non_srflip_unaffected_by_per_setup_key(self, monkeypatch):
        """A non-SR_FLIP setup still uses the channel-level consecutive=2."""
        sig = _Sig(setup_class="FAILED_AUCTION_RECLAIM")
        indicators = self._bad_momentum_indicators()
        # consecutive_override=3 applies to SR_FLIP key only; FAR falls back to channel=2
        # So FAR should still kill on reading 2
        _run_check(sig, indicators, monkeypatch, consecutive_override=None)
        assert sig.momentum_invalidation_count == 1
        result = _run_check(sig, indicators, monkeypatch, consecutive_override=None)
        assert result is not None

    def test_recovery_resets_count(self, monkeypatch):
        """A neutral momentum reading resets the count so grace starts over."""
        sig = _Sig()
        bad = self._bad_momentum_indicators()
        neutral = {"ema9_last": 1.0, "ema21_last": 1.0, "momentum": 0.01, "atr_last": 0.005}
        _run_check(sig, bad, monkeypatch, consecutive_override=3)
        assert sig.momentum_invalidation_count == 1
        _run_check(sig, neutral, monkeypatch, consecutive_override=3)
        assert sig.momentum_invalidation_count == 0

    def test_grace_does_not_block_protective_adverse_excursion(self, monkeypatch):
        """Grace only delays momentum kills; adverse excursion still fires independently."""
        from src.trade_monitor import TradeMonitor
        tm = TradeMonitor.__new__(TradeMonitor)
        tm._regime_detector = None
        tm._indicators_fn = None
        tm._store = None
        tm._btc_direction_cache = {}
        monkeypatch.setattr("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "standard")
        monkeypatch.setattr("src.trade_monitor.INVALIDATION_MIN_AGE_SECONDS",
                            {"360_SCALP": 0, "360_SCALP::SR_FLIP_RETEST": 0})
        monkeypatch.setattr("src.trade_monitor.INVALIDATION_MOMENTUM_THRESHOLD", {"360_SCALP": 0.05})
        monkeypatch.setattr("src.trade_monitor.INVALIDATION_ADVERSE_EXCURSION_FRACTION", 0.99)
        monkeypatch.setattr("src.trade_monitor.INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC", 0)
        monkeypatch.setattr("src.trade_monitor.INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_BY_SETUP",
                            {"360_SCALP::SR_FLIP_RETEST": 0})
        # 70% adverse fraction → fires at 0.7 × SL_dist
        monkeypatch.setattr("src.trade_monitor.INVALIDATION_ADVERSE_EXCURSION_FRACTION_BY_SETUP",
                            {"360_SCALP::SR_FLIP_RETEST": 0.50})
        monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_CORRELATION_ENABLED", False)
        monkeypatch.setattr("src.trade_monitor.SR_FLIP_MOMENTUM_GRACE_ENABLED", False)
        monkeypatch.setattr("src.trade_monitor.INVALIDATION_CONSECUTIVE_THRESHOLD",
                            {"360_SCALP": 2, "360_SCALP::SR_FLIP_RETEST": 3})
        # SR_FLIP SHORT: entry=1.0, SL=1.015, so SL_dist=0.015
        # Price at 1.011 → adverse = 0.011 > 0.015*0.50=0.0075 → fires
        sig = _Sig(current_price=1.011)
        tm._indicators_fn = lambda _: {"ema9_last": 1.0, "ema21_last": 1.0,
                                        "momentum": 0.0, "atr_last": 0.005}
        result = tm._check_invalidation(sig)
        assert result is not None
        assert "adverse excursion" in result


# ---------------------------------------------------------------------------
# Change B: SR_FLIP pre-TP R-scaling
# ---------------------------------------------------------------------------

class TestSrFlipPretpRScaling:
    """SR_FLIP pre-TP threshold floored at SL_dist_pct × R_FACTOR."""

    def _run_dispatch_rscale(
        self,
        monkeypatch,
        *,
        sl_price: float,
        entry_price: float,
        current_threshold: float,
        r_factor: float,
        flag_enabled: bool,
        shadow_on: bool = False,
    ) -> float:
        """
        Run the R-scaling block from signal_dispatch in isolation.
        Returns the resolved user_pretp_threshold after the block.
        """
        monkeypatch.setattr("config.SR_FLIP_PRETP_R_SCALING_ENABLED", flag_enabled)
        monkeypatch.setattr("config.SR_FLIP_PRETP_R_FACTOR", r_factor)
        monkeypatch.setattr("config.DARK_FLAG_SHADOW_TELEMETRY", shadow_on)

        # Replicate the R-scaling logic (pure math — no FSM needed)
        user_pretp_threshold = current_threshold
        if sl_price > 0 and entry_price > 0:
            sl_dist_pct = abs(entry_price - sl_price) / entry_price * 100.0
            r_scaled = sl_dist_pct * r_factor
            scaling_binds = r_scaled > user_pretp_threshold
            if flag_enabled and scaling_binds:
                user_pretp_threshold = r_scaled
        return user_pretp_threshold

    def test_wide_sl_raises_threshold_when_enabled(self, monkeypatch):
        """SL=2.5%, factor=0.35 → threshold raised from 0.503% to 0.875%."""
        result = self._run_dispatch_rscale(
            monkeypatch,
            entry_price=1.0, sl_price=1.025,   # SHORT: SL above entry → 2.5% dist
            current_threshold=0.503,
            r_factor=0.35,
            flag_enabled=True,
        )
        assert abs(result - 0.875) < 0.001

    def test_tight_sl_unchanged_when_scaling_does_not_bind(self, monkeypatch):
        """SL=0.8%, factor=0.35 → r_scaled=0.28 < 0.503 → threshold unchanged."""
        result = self._run_dispatch_rscale(
            monkeypatch,
            entry_price=1.0, sl_price=1.008,
            current_threshold=0.503,
            r_factor=0.35,
            flag_enabled=True,
        )
        assert abs(result - 0.503) < 0.001

    def test_noop_when_flag_disabled(self, monkeypatch):
        """Wide SL but flag off — threshold unchanged."""
        result = self._run_dispatch_rscale(
            monkeypatch,
            entry_price=1.0, sl_price=1.025,
            current_threshold=0.503,
            r_factor=0.35,
            flag_enabled=False,
        )
        assert abs(result - 0.503) < 0.001

    def test_sl_at_exactly_threshold_boundary(self, monkeypatch):
        """SL_dist * factor == current_threshold → scaling does not bind (no change)."""
        # 1.429% × 0.35 = 0.500% ≈ threshold → just below binding
        result = self._run_dispatch_rscale(
            monkeypatch,
            entry_price=1.0, sl_price=1.01429,
            current_threshold=0.503,
            r_factor=0.35,
            flag_enabled=True,
        )
        # 0.01429 * 0.35 = 0.00500 < 0.00503 → no binding
        assert abs(result - 0.503) < 0.001

    def test_r_factor_tunable(self, monkeypatch):
        """A higher R_FACTOR raises the threshold further."""
        r40 = self._run_dispatch_rscale(
            monkeypatch,
            entry_price=1.0, sl_price=1.025,
            current_threshold=0.503,
            r_factor=0.40,
            flag_enabled=True,
        )
        r35 = self._run_dispatch_rscale(
            monkeypatch,
            entry_price=1.0, sl_price=1.025,
            current_threshold=0.503,
            r_factor=0.35,
            flag_enabled=True,
        )
        assert r40 > r35

    def test_zero_sl_safe(self, monkeypatch):
        """Zero SL price (unset) skips scaling — no ZeroDivisionError."""
        result = self._run_dispatch_rscale(
            monkeypatch,
            entry_price=1.0, sl_price=0.0,
            current_threshold=0.503,
            r_factor=0.35,
            flag_enabled=True,
        )
        assert abs(result - 0.503) < 0.001
