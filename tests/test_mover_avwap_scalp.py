"""MOVER_AVWAP_SCALP — anchored-VWAP continuation scalp for movers.

Drives the evaluator end-to-end (real ScalpChannel + builder) to prove it
fires with its own identity on a confirmed mover pullback-to-AVWAP, and that
the slope/leg/shadow gates reject correctly.
"""
from __future__ import annotations

import numpy as np

from src.channels.scalp import ScalpChannel
from src.smc import Direction


def _short_mover_candles():
    """15m series: swing high early → ~8% down-leg → pullback that tags the
    anchored VWAP → final bar rejects back below it on a volume spike."""
    n = 60
    close = np.zeros(n)
    for i in range(n):
        if i < 13:
            close[i] = 110 - i * 0.2          # swing-high region (leg origin)
        elif i < 53:
            close[i] = 107.4 - (i - 13) * 0.28  # the down-leg
        elif i < 59:
            close[i] = 96.2 + (i - 53) * 1.05   # pullback up toward AVWAP
        else:
            close[i] = 101.0                    # reject bar: below AVWAP + prev
    close[58] = 102.2                            # prev bar tags AVWAP from below
    high = close + 0.5
    low = close - 0.5
    vol = np.ones(n) * 1000.0
    vol[-1] = 3000.0                             # reclaim-bar volume spike
    return {"15m": {"open": close - 0.1, "high": high, "low": low,
                    "close": close, "volume": vol}}


_IND = {"15m": {"atr_last": 0.5}}
_SMC = {"pair_profile": None, "regime_context": None}


def test_fires_short_with_own_identity_and_tradeable_sl():
    ch = ScalpChannel()
    sig = ch._evaluate_mover_avwap_scalp(
        "ABCUSDT", _short_mover_candles(), _IND, _SMC, 0.001, 50_000_000,
        regime="TRENDING_DOWN",
    )
    assert sig is not None, f"expected a signal, got reject {ch._active_no_signal_reason!r}"
    assert sig.setup_class == "MOVER_AVWAP_SCALP"   # identity preserved
    assert sig.direction == Direction.SHORT
    assert sig.entry_trigger == "avwap_reclaim"
    sl_dist_pct = abs(sig.stop_loss - sig.entry) / sig.entry * 100.0
    assert sl_dist_pct < 3.0                        # under the path's max SL


def test_insufficient_candles_rejects():
    ch = ScalpChannel()
    short = {"15m": {k: np.ones(10) for k in ("open", "high", "low", "close", "volume")}}
    assert ch._evaluate_mover_avwap_scalp("X", short, {}, {}, 0.001, 1e6) is None
    assert ch._active_no_signal_reason == "insufficient_candles"


def test_flat_market_rejects_no_mover_leg():
    ch = ScalpChannel()
    n = 60
    close = np.full(n, 100.0) + np.random.default_rng(0).normal(0, 0.05, n)
    flat = {"15m": {"open": close, "high": close + 0.3, "low": close - 0.3,
                    "close": close, "volume": np.ones(n) * 1000.0}}
    sig = ch._evaluate_mover_avwap_scalp("X", flat, _IND, _SMC, 0.001, 50_000_000,
                                         regime="TRENDING_DOWN")
    assert sig is None
    assert ch._active_no_signal_reason == "no_mover_leg"


def test_shadow_mode_suppresses_when_disabled():
    """Shadowed via the ops runtime tunable (2026-07-09 — the live/shadow
    switch is ops-controlled; the env flag is only the boot default)."""
    from src import runtime_tunables as rt
    from tests.test_mover_runner_exit import _FakeFirestore

    rt.reset_for_test()
    try:
        rt.init_runtime_tunables(_FakeFirestore())
        rt.set_values({"mover_avwap_scalp_live": False})
        ch = ScalpChannel()
        sig = ch._evaluate_mover_avwap_scalp(
            "ABCUSDT", _short_mover_candles(), _IND, _SMC, 0.001, 50_000_000,
            regime="TRENDING_DOWN",
        )
        assert sig is None
        assert ch._active_no_signal_reason == "shadow_mode"
    finally:
        rt.reset_for_test()


def test_evaluator_method_exists():
    ch = ScalpChannel()
    assert callable(getattr(ch, "_evaluate_mover_avwap_scalp", None))
