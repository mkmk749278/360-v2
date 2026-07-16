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


def test_pair_profile_reaches_basic_filters(monkeypatch):
    """2026-07-16 audit F6: MEAN_REVERT was the only evaluator of 18 that
    called _pass_basic_filters without profile= — ignoring the pair's
    spread/volume multipliers.  Pin the pass-through."""
    _force_live(monkeypatch, True)
    ch = ScalpChannel()
    seen = {}
    real = ch._pass_basic_filters

    def _spy(spread_pct, volume_24h_usd, regime="", profile=None):
        seen["profile"] = profile
        return real(spread_pct, volume_24h_usd, regime=regime, profile=profile)

    monkeypatch.setattr(ch, "_pass_basic_filters", _spy)
    from types import SimpleNamespace
    sentinel = SimpleNamespace(
        spread_max_mult=1.0, volume_min_mult=1.0, adx_min_mult=1.0,
        rsi_ob_level=70.0, rsi_os_level=30.0, bb_touch_pct=0.0, tier="MIDCAP",
    )
    smc = dict(_SMC)
    smc["pair_profile"] = sentinel
    ch._evaluate_mean_revert(
        "ABCUSDT", _overextended_candles("SHORT"), _IND, smc,
        0.001, 50_000_000, regime="RANGING",
    )
    assert seen["profile"] is sentinel


# ---------------------------------------------------------------------------
# 2026-07-16 incident: 300 generated / 300 gated / 0 emitted.
# execution_quality_check had no MEAN_REVERT branch, so the fade fell into
# the generic trend-continuation else (EMA9 aligned WITH the trade — always
# false for a counter-trend fade) AND the 1.5-ATR default max_extension
# (always exceeded by a 2.5σ entry).  These tests pin the fade branch.
# ---------------------------------------------------------------------------

from types import SimpleNamespace

from src.signal_quality import MarketState, SetupClass, execution_quality_check


def _gate_indicators(ema9: float, ema21: float, atr: float = 0.4) -> dict:
    return {
        "5m": {
            "ema9_last": ema9,
            "ema21_last": ema21,
            "atr_last": atr,
            "momentum_last": 0.1,
            "bb_upper_last": 103.0,
            "bb_mid_last": 100.5,
            "bb_lower_last": 98.0,
        },
    }


def _gate_signal(direction: Direction, entry: float, mean: float):
    if direction == Direction.LONG:
        sl, tp1 = entry - 1.0, mean
    else:
        sl, tp1 = entry + 1.0, mean
    return SimpleNamespace(
        channel="360_SCALP", direction=direction, entry=entry,
        stop_loss=sl, tp1=tp1, tp2=tp1, tp3=tp1,
        mean_revert_mean=mean,
    )


class TestExecutionGateFadeBranch:
    def test_long_fade_below_mean_passes(self):
        """LONG at −2.5σ: EMA9 < EMA21 (downswing) — the generic else rejected
        this 100% of the time pre-fix; the fade branch must pass it."""
        sig = _gate_signal(Direction.LONG, entry=100.0, mean=101.5)
        result = execution_quality_check(
            sig, _gate_indicators(ema9=99.6, ema21=100.4), {"sweeps": [], "mss": None},
            SetupClass.MEAN_REVERT, MarketState.CLEAN_RANGE,
        )
        assert result.trigger_confirmed is True
        assert result.passed is True, result.reason
        assert result.anchor_price == pytest.approx(101.5)
        assert "rolling mean" in result.execution_note

    def test_short_fade_above_mean_passes(self):
        sig = _gate_signal(Direction.SHORT, entry=103.5, mean=102.0)
        result = execution_quality_check(
            sig, _gate_indicators(ema9=103.2, ema21=102.1), {"sweeps": [], "mss": None},
            SetupClass.MEAN_REVERT, MarketState.CLEAN_RANGE,
        )
        assert result.trigger_confirmed is True
        assert result.passed is True, result.reason

    def test_entry_on_wrong_side_of_mean_rejected(self):
        """LONG entry already ABOVE the mean = the reversion has happened —
        no stretched edge left to fade."""
        sig = _gate_signal(Direction.LONG, entry=102.0, mean=101.5)
        result = execution_quality_check(
            sig, _gate_indicators(ema9=101.0, ema21=101.2), {"sweeps": [], "mss": None},
            SetupClass.MEAN_REVERT, MarketState.CLEAN_RANGE,
        )
        assert result.trigger_confirmed is False
        assert result.passed is False
        assert "trigger" in result.reason

    def test_catastrophic_dislocation_rejected_by_extension_cap(self):
        """> 5 ATR from the mean is a news candle, not a fade."""
        sig = _gate_signal(Direction.LONG, entry=100.0, mean=112.0)
        result = execution_quality_check(
            sig, _gate_indicators(ema9=99.0, ema21=101.0, atr=2.0),
            {"sweeps": [], "mss": None},
            SetupClass.MEAN_REVERT, MarketState.CLEAN_RANGE,
        )
        assert result.passed is False
        assert "overextended" in result.reason

    def test_missing_anchor_falls_back_without_raising(self):
        """A signal that somehow lost its stamp must not crash the gate."""
        sig = _gate_signal(Direction.LONG, entry=100.0, mean=101.5)
        sig.mean_revert_mean = None
        result = execution_quality_check(
            sig, _gate_indicators(ema9=99.6, ema21=100.4), {"sweeps": [], "mss": None},
            SetupClass.MEAN_REVERT, MarketState.CLEAN_RANGE,
        )
        # Falls back to bb_mid (100.5): entry 100.0 < 100.5 → still a fade.
        assert result.anchor_price == pytest.approx(100.5)
        assert result.trigger_confirmed is True

    def test_generic_else_branch_unchanged_for_other_setups(self):
        """The trend-continuation else must keep its semantics for setups
        without a dedicated branch (pin against accidental drift)."""
        sig = _gate_signal(Direction.LONG, entry=100.0, mean=101.5)
        result = execution_quality_check(
            sig, _gate_indicators(ema9=99.6, ema21=100.4), {"sweeps": [], "mss": None},
            SetupClass.TREND_PULLBACK_CONTINUATION, MarketState.STRONG_TREND,
        )
        assert result.trigger_confirmed is False  # EMA9 < EMA21 for a LONG

    def test_evaluator_stamps_mean_anchor(self, monkeypatch):
        _force_live(monkeypatch, True)
        ch = ScalpChannel()
        sig = ch._evaluate_mean_revert(
            "ABCUSDT", _overextended_candles("SHORT"), _IND, _SMC,
            0.001, 50_000_000, regime="RANGING",
        )
        assert sig is not None
        assert sig.mean_revert_mean == pytest.approx(sig.tp1)


class TestEmissionLivenessProbe:
    """The mean_revert_path probe (detections vs shadow stamps) stayed green
    through the 100%-gated incident.  The new mean_revert_emission probe
    pages when ≥60 detections accrue with zero emissions."""

    def _build(self, tmp_path, monkeypatch, scanner):
        import time as _time

        from src import feature_liveness as fl_mod
        from src import runtime_tunables
        from src.main import CryptoSignalEngine

        monkeypatch.setattr(runtime_tunables, "get", lambda key: True)
        monkeypatch.setattr(
            fl_mod, "_DEFAULT_PATH", str(tmp_path / "feature_liveness.json")
        )
        stub = SimpleNamespace(
            _scanner=scanner,
            pair_mgr=SimpleNamespace(pairs={}),
            data_store=SimpleNamespace(get_candles=lambda *a, **k: None),
            _last_market_context_publish_ts=_time.time(),
            _last_atr_percentile=55.0,
        )
        fl = CryptoSignalEngine._build_feature_liveness(stub)
        fl._boot_grace = 0.0  # tests exercise steady-state, not warmup
        return fl

    def test_backlog_with_zero_emissions_violates(self, tmp_path, monkeypatch):
        chan = SimpleNamespace(_mean_revert_detections=0)
        scanner = SimpleNamespace(
            _scan_cycle_count=10, _shadow_last_stamp={}, channels=[chan],
            _mean_revert_emitted_total=0,
        )
        fl = self._build(tmp_path, monkeypatch, scanner)
        fl.run_cycle()                       # baseline
        chan._mean_revert_detections = 80    # detections flow, emissions flat
        statuses = []
        for _ in range(7):
            payload = fl.run_cycle()
            statuses.append(payload["features"]["mean_revert_emission"]["status"])
        assert statuses[-1] == "violating"
        assert payload["features"]["mean_revert_emission"]["streak"] >= 6

    def test_emission_resets_backlog(self, tmp_path, monkeypatch):
        chan = SimpleNamespace(_mean_revert_detections=0)
        scanner = SimpleNamespace(
            _scan_cycle_count=10, _shadow_last_stamp={}, channels=[chan],
            _mean_revert_emitted_total=0,
        )
        fl = self._build(tmp_path, monkeypatch, scanner)
        fl.run_cycle()
        chan._mean_revert_detections = 80
        fl.run_cycle()                                # violating
        scanner._mean_revert_emitted_total = 1        # an emission lands
        payload = fl.run_cycle()
        assert payload["features"]["mean_revert_emission"]["status"] == "ok"
        assert payload["features"]["mean_revert_emission"]["streak"] == 0


def test_scanner_monotonic_emitted_counter():
    """_increment_path_funnel('emitted', …, MEAN_REVERT) feeds the probe's
    monotonic counter; other setups and stages must not."""
    from src.scanner import Scanner

    sc = Scanner.__new__(Scanner)
    from collections import defaultdict
    sc._path_funnel_counters = defaultdict(int)
    sc._mean_revert_emitted_total = 0
    sc._increment_path_funnel("emitted", "360_SCALP", "MEAN_REVERT")
    sc._increment_path_funnel("emitted", "360_SCALP", "SR_FLIP_RETEST")
    sc._increment_path_funnel("gated", "360_SCALP", "MEAN_REVERT")
    assert sc._mean_revert_emitted_total == 1
