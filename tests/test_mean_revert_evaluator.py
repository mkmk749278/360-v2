"""MEAN_REVERT — statistical mean-reversion, 18th evaluator (2026-07-15).

Graduated live from the SHADOW_MEAN_REVERT shadow unit (+0.67R / 59% win /
n=550 forward-measured).  These tests pin the graduation contract:

1. The evaluator fires with its own identity on a 2.5σ over-extension and its
   geometry is BYTE-IDENTICAL to ``shadow_strategies.evaluate_mean_revert``
   on the same arrays (shared detection — live and shadow can never drift).
2. Live by owner directive 2026-07-15 (tunable default ON); the
   ``mean_revert_live`` runtime tunable is the ops off-switch — OFF logs the
   would-fire and rejects ``shadow_mode`` while the detection counter still
   moves (liveness probe contract).
3. Numpy candle arrays (the production shape) never raise.
"""
from __future__ import annotations

import numpy as np
import pytest

from src.channels.scalp import ScalpChannel
from src.shadow_strategies import evaluate_mean_revert as shadow_mean_revert
from src.smc import Direction

_IND = {"15m": {"atr_last": 0.4}}
_SMC = {"pair_profile": None, "regime_context": None}


def _overextended_candles(direction: str = "SHORT"):
    """15m series: 40 bars of tight chop around 100, then a final spike far
    outside the 20-bar band (z >> 2.5) — SHORT fades the spike up, LONG the
    spike down."""
    n = 44
    rng = np.random.default_rng(7)
    close = 100.0 + rng.normal(0.0, 0.15, n)
    spike = 103.5 if direction == "SHORT" else 96.5
    close[-1] = spike
    high = close + 0.2
    low = close - 0.2
    high[-1] = spike + 0.3
    low[-1] = spike - 0.3
    vol = np.ones(n) * 1000.0
    return {"15m": {"open": close - 0.05, "high": high, "low": low,
                    "close": close, "volume": vol}}


def _force_live(monkeypatch, value: bool):
    monkeypatch.setattr(
        ScalpChannel, "_mover_path_live",
        staticmethod(lambda key, default: value),
    )


def test_fires_short_with_own_identity_and_shadow_parity(monkeypatch):
    _force_live(monkeypatch, True)
    ch = ScalpChannel()
    candles = _overextended_candles("SHORT")
    sig = ch._evaluate_mean_revert(
        "ABCUSDT", candles, _IND, _SMC, 0.001, 50_000_000, regime="RANGING",
    )
    assert sig is not None, f"expected a signal, got reject {ch._active_no_signal_reason!r}"
    assert sig.setup_class == "MEAN_REVERT"          # identity preserved
    assert sig.direction == Direction.SHORT
    assert sig.entry_trigger == "mean_revert_z"
    assert sig.valid_for_minutes == 180              # not the 15-min sentinel default

    # Shadow parity: entry/SL/TP1 equal the shadow unit's output verbatim.
    tf = candles["15m"]
    cand = shadow_mean_revert(tf["high"], tf["low"], tf["close"])
    assert cand is not None and cand.side == "SHORT"
    assert sig.entry == pytest.approx(cand.entry)
    assert sig.stop_loss == pytest.approx(round(cand.stop_loss, 8))
    assert sig.tp1 == pytest.approx(round(cand.tp1, 8))
    assert sig.original_sl_distance == pytest.approx(abs(cand.entry - cand.stop_loss))
    # TP ladder is monotonic on the profit side.
    assert sig.tp1 > sig.tp2 > sig.tp3
    assert ch._mean_revert_detections == 1


def test_fires_long_on_downside_extension(monkeypatch):
    _force_live(monkeypatch, True)
    ch = ScalpChannel()
    sig = ch._evaluate_mean_revert(
        "ABCUSDT", _overextended_candles("LONG"), _IND, _SMC, 0.001,
        50_000_000, regime="RANGING",
    )
    assert sig is not None
    assert sig.direction == Direction.LONG
    assert sig.tp1 < sig.tp2 < sig.tp3
    assert sig.stop_loss < sig.entry < sig.tp1


def test_no_fire_without_extension(monkeypatch):
    _force_live(monkeypatch, True)
    ch = ScalpChannel()
    n = 44
    close = 100.0 + np.random.default_rng(3).normal(0.0, 0.15, n)  # no spike
    candles = {"15m": {"open": close, "high": close + 0.2, "low": close - 0.2,
                       "close": close, "volume": np.ones(n) * 1000.0}}
    assert ch._evaluate_mean_revert("X", candles, _IND, _SMC, 0.001, 5e7) is None
    assert ch._active_no_signal_reason == "no_extension"
    assert ch._mean_revert_detections == 0


def test_insufficient_candles_rejects(monkeypatch):
    _force_live(monkeypatch, True)
    ch = ScalpChannel()
    short = {"15m": {k: np.ones(10) for k in ("open", "high", "low", "close", "volume")}}
    assert ch._evaluate_mean_revert("X", short, {}, {}, 0.001, 1e6) is None
    assert ch._active_no_signal_reason == "insufficient_candles"


def test_tunable_off_is_shadow_only_but_detection_still_counts(monkeypatch):
    _force_live(monkeypatch, False)
    ch = ScalpChannel()
    sig = ch._evaluate_mean_revert(
        "ABCUSDT", _overextended_candles("SHORT"), _IND, _SMC, 0.001,
        50_000_000, regime="RANGING",
    )
    assert sig is None
    assert ch._active_no_signal_reason == "shadow_mode"
    # The liveness counter moves even while shadowed — dead wiring is
    # distinguishable from an ops-disabled path.
    assert ch._mean_revert_detections == 1


def test_registry_default_is_live_per_owner_directive():
    """Owner directive 2026-07-15: 'no dark on 18th path, make it live'.
    The runtime tunable exists as the ops off-switch and defaults ON."""
    from src import runtime_tunables as rt

    t = rt.registry()["mean_revert_live"]
    assert t.default is True
    assert t.category == "Signal gating"


def test_evaluator_runs_in_dispatch_loop(monkeypatch):
    """The 18th row is actually wired into ScalpChannel.evaluate."""
    _force_live(monkeypatch, True)
    ch = ScalpChannel()
    ch.evaluate(
        "ABCUSDT", _overextended_candles("SHORT"), _IND, _SMC, 0.001,
        50_000_000,
    )
    telemetry = ch.consume_generation_telemetry()
    assert telemetry["attempts"]["MEAN_REVERT"] == 1
