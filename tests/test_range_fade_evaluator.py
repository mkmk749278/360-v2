"""RANGE_FADE — range-edge fade to mid, 19th evaluator (2026-07-18).

Graduated from the SHADOW_RANGE_FADE shadow unit — the Strategy Lab
allocator's top recommendation in range/quiet contexts (+0.841R n=24
ASIA/QUIET/NORMAL; +0.885R n=15 OVERLAP/RANGE/NORMAL) — shipped DARK
(``RANGE_FADE_LIVE`` default false) and CONTEXT-GATED (blanket activation is
measured net-negative: gate audit +0.20R saved/suppression over n=223).

These tests pin the graduation contract:

1. The evaluator fires with its own identity at a tested range edge and its
   geometry is BYTE-IDENTICAL to ``shadow_strategies.evaluate_range_fade``
   on the same arrays (shared detection — live and shadow can never drift).
2. DARK by default: ``RANGE_FADE_LIVE`` ships false; the ``range_fade_live``
   runtime tunable is the ops activation switch — OFF logs the would-fire and
   rejects ``shadow_mode`` while the detection counter still moves (liveness
   probe contract).
3. The context-edge gate's pure eligibility rule mirrors the allocator:
   STRONG always emits, POSITIVE only when the operator relaxes the config,
   everything else (FLAT / NEGATIVE / INSUFFICIENT_DATA / unknown) blocks.
4. Numpy candle arrays (the production shape) never raise.
"""
from __future__ import annotations

import numpy as np
import pytest

import src.scanner as scanner_mod
from src.channels.scalp import ScalpChannel
from src.scanner import _range_fade_context_allowed
from src.shadow_strategies import evaluate_range_fade as shadow_range_fade
from src.smc import Direction
from src.strategy_edge import (
    VERDICT_FLAT,
    VERDICT_INSUFFICIENT,
    VERDICT_NEGATIVE,
    VERDICT_POSITIVE,
    VERDICT_STRONG,
)

_IND = {"15m": {"atr_last": 0.4}}
_SMC = {"pair_profile": None, "regime_context": None}


def _range_candles(direction: str = "SHORT"):
    """15m series: 64 bars oscillating in 8-bar blocks between ~100 and ~110 —
    a wide (≫4·ATR), repeatedly-tested two-sided range.  Ending in a high
    block puts the last close at the top edge (SHORT fade); a low block ends
    at the bottom edge (LONG fade)."""
    n = 64
    rng = np.random.default_rng(11)
    close = np.empty(n)
    for i in range(n):
        # Odd blocks high so the final block (i=56..63, block 7) is HIGH —
        # the last close sits at the top edge and the SHORT fade triggers.
        base = 110.0 if (i // 8) % 2 == 1 else 100.0
        close[i] = base + rng.normal(0.0, 0.05)
    if direction == "LONG":
        close = 210.0 - close                     # mirror: ends in a low block
    high = close + 0.2
    low = close - 0.2
    vol = np.ones(n) * 1000.0
    return {"15m": {"open": close - 0.05, "high": high, "low": low,
                    "close": close, "volume": vol}}


def _force_live(monkeypatch, value: bool):
    monkeypatch.setattr(
        ScalpChannel, "_mover_path_live",
        staticmethod(lambda key, default: value),
    )


class TestEvaluator:
    def test_fires_short_with_own_identity_and_shadow_parity(self, monkeypatch):
        _force_live(monkeypatch, True)
        ch = ScalpChannel()
        candles = _range_candles("SHORT")
        sig = ch._evaluate_range_fade(
            "ABCUSDT", candles, _IND, _SMC, 0.001, 50_000_000, regime="RANGING",
        )
        assert sig is not None, (
            f"expected a signal, got reject {ch._active_no_signal_reason!r}"
        )
        assert sig.setup_class == "RANGE_FADE"       # identity preserved
        assert sig.direction == Direction.SHORT
        assert sig.entry_trigger == "range_fade_edge"
        assert sig.valid_for_minutes == 240          # not the 15-min sentinel default
        assert sig.range_fade_mid == sig.tp1         # execution-gate anchor stamped

        # Shadow parity: entry/SL/TP1 equal the shadow unit's output verbatim.
        tf = candles["15m"]
        cand = shadow_range_fade(tf["high"], tf["low"], tf["close"])
        assert cand is not None and cand.side == "SHORT"
        assert sig.entry == pytest.approx(cand.entry)
        assert sig.stop_loss == pytest.approx(round(cand.stop_loss, 8))
        assert sig.tp1 == pytest.approx(round(cand.tp1, 8))
        assert sig.original_sl_distance == pytest.approx(
            abs(cand.entry - cand.stop_loss)
        )
        # TP ladder is monotonic on the profit side (SHORT: descending).
        assert sig.tp1 > sig.tp2 > sig.tp3
        assert ch._range_fade_detections == 1

    def test_fires_long_at_bottom_edge(self, monkeypatch):
        _force_live(monkeypatch, True)
        ch = ScalpChannel()
        sig = ch._evaluate_range_fade(
            "ABCUSDT", _range_candles("LONG"), _IND, _SMC, 0.001,
            50_000_000, regime="RANGING",
        )
        assert sig is not None
        assert sig.direction == Direction.LONG
        assert sig.tp1 < sig.tp2 < sig.tp3
        assert sig.stop_loss < sig.entry < sig.tp1

    def test_no_fire_without_a_tested_range(self, monkeypatch):
        _force_live(monkeypatch, True)
        ch = ScalpChannel()
        n = 64
        # Tight chop — width ≪ 4·ATR relative structure, no tradeable range.
        close = 100.0 + np.random.default_rng(3).normal(0.0, 0.05, n)
        candles = {"15m": {"open": close, "high": close + 0.2,
                           "low": close - 0.2, "close": close,
                           "volume": np.ones(n) * 1000.0}}
        assert ch._evaluate_range_fade("X", candles, _IND, _SMC, 0.001, 5e7) is None
        assert ch._active_no_signal_reason == "no_range_edge"
        assert ch._range_fade_detections == 0

    def test_insufficient_candles_rejects(self, monkeypatch):
        _force_live(monkeypatch, True)
        ch = ScalpChannel()
        short = {"15m": {k: np.ones(10) for k in
                         ("open", "high", "low", "close", "volume")}}
        assert ch._evaluate_range_fade("X", short, {}, {}, 0.001, 1e6) is None
        assert ch._active_no_signal_reason == "insufficient_candles"

    def test_tunable_off_is_shadow_only_but_detection_still_counts(self, monkeypatch):
        _force_live(monkeypatch, False)
        ch = ScalpChannel()
        sig = ch._evaluate_range_fade(
            "ABCUSDT", _range_candles("SHORT"), _IND, _SMC, 0.001,
            50_000_000, regime="RANGING",
        )
        assert sig is None
        assert ch._active_no_signal_reason == "shadow_mode"
        assert ch._range_fade_detections == 1        # liveness contract

    def test_registered_in_evaluate_dispatch_list(self):
        ch = ScalpChannel()
        assert hasattr(ch, "_evaluate_range_fade")
        import inspect
        src = inspect.getsource(ScalpChannel.evaluate)
        assert '"_evaluate_range_fade"' in src


class TestDarkDefault:
    def test_boot_flag_ships_false(self):
        from config import RANGE_FADE_LIVE
        assert RANGE_FADE_LIVE is False, (
            "RANGE_FADE ships DARK (production dark-first doctrine) — the "
            "owner activates via the range_fade_live tunable from ops"
        )

    def test_runtime_tunable_registered_dark(self):
        from src.runtime_tunables import registry
        reg = registry()
        assert "range_fade_live" in reg
        t = reg["range_fade_live"]
        assert t.type == "bool"
        assert t.default is False
        assert t.category == "Signal gating"

    def test_context_gate_enabled_by_default(self):
        from config import (
            RANGE_FADE_CONTEXT_GATE_ENABLED,
            RANGE_FADE_CONTEXT_MIN_VERDICT,
        )
        assert RANGE_FADE_CONTEXT_GATE_ENABLED is True
        assert RANGE_FADE_CONTEXT_MIN_VERDICT == "strong"


class TestContextGateRule:
    def test_strong_always_allowed(self):
        assert _range_fade_context_allowed(VERDICT_STRONG) is True

    def test_positive_blocked_at_default_strictness(self):
        assert _range_fade_context_allowed(VERDICT_POSITIVE) is False

    def test_positive_allowed_when_relaxed(self, monkeypatch):
        monkeypatch.setattr(
            scanner_mod, "RANGE_FADE_CONTEXT_MIN_VERDICT", "positive"
        )
        assert _range_fade_context_allowed(VERDICT_POSITIVE) is True
        assert _range_fade_context_allowed(VERDICT_STRONG) is True

    @pytest.mark.parametrize("verdict", [
        VERDICT_FLAT, VERDICT_NEGATIVE, VERDICT_INSUFFICIENT, "UNKNOWN", "",
    ])
    def test_everything_else_blocked_even_relaxed(self, monkeypatch, verdict):
        assert _range_fade_context_allowed(verdict) is False
        monkeypatch.setattr(
            scanner_mod, "RANGE_FADE_CONTEXT_MIN_VERDICT", "positive"
        )
        assert _range_fade_context_allowed(verdict) is False


class TestScannerCounters:
    def test_emitted_stage_feeds_range_fade_total(self):
        from collections import defaultdict
        from src.scanner import Scanner

        sc = Scanner.__new__(Scanner)
        sc._path_funnel_counters = defaultdict(int)
        sc._mean_revert_emitted_total = 0
        sc._range_fade_emitted_total = 0
        sc._increment_path_funnel("emitted", "360_SCALP", "RANGE_FADE")
        assert sc._range_fade_emitted_total == 1
        assert sc._mean_revert_emitted_total == 0
        sc._increment_path_funnel("gate_reject:context_edge", "360_SCALP", "RANGE_FADE")
        assert sc._range_fade_emitted_total == 1    # gate rejects never count


class TestWiringPins:
    """RANGE_FADE must be wired at every stringly-coupled site — a miss at any
    one of these is the silent-death class (#739) this repo has already paid
    for."""

    def test_setup_class_enum(self):
        from src.signal_quality import SetupClass
        assert SetupClass.RANGE_FADE.value == "RANGE_FADE"

    def test_portfolio_role(self):
        from src.signal_quality import (
            ACTIVE_PATH_PORTFOLIO_ROLES,
            PortfolioRole,
            SetupClass,
        )
        assert ACTIVE_PATH_PORTFOLIO_ROLES[SetupClass.RANGE_FADE] is PortfolioRole.SUPPORT

    def test_structural_sltp_protected(self):
        from src.signal_quality import (
            STRUCTURAL_SLTP_PROTECTED_SETUPS,
            SetupClass,
        )
        assert SetupClass.RANGE_FADE in STRUCTURAL_SLTP_PROTECTED_SETUPS

    def test_channel_and_regime_compat(self):
        from src.signal_quality import (
            CHANNEL_SETUP_COMPATIBILITY,
            REGIME_SETUP_COMPATIBILITY,
            MarketState,
            SetupClass,
        )
        assert SetupClass.RANGE_FADE in CHANNEL_SETUP_COMPATIBILITY["360_SCALP"]
        assert SetupClass.RANGE_FADE in REGIME_SETUP_COMPATIBILITY[MarketState.CLEAN_RANGE]
        assert SetupClass.RANGE_FADE in REGIME_SETUP_COMPATIBILITY[MarketState.DIRTY_RANGE]

    def test_sl_cap_and_min_rr(self):
        from src.signal_quality import (
            _MAX_SL_PCT_BY_SETUP,
            _MIN_RR_RANGE,
            SetupClass,
            _min_rr_for_setup,
        )
        assert _MAX_SL_PCT_BY_SETUP["RANGE_FADE"] == 3.0
        assert _min_rr_for_setup(SetupClass.RANGE_FADE) == _MIN_RR_RANGE

    def test_scanner_family_is_mean_reversion(self):
        from src.scanner import _SCALP_SETUP_TO_FAMILY
        assert _SCALP_SETUP_TO_FAMILY["RANGE_FADE"] == "mean_reversion"

    def test_strategy_portfolio_affinity(self):
        from src.strategy_portfolio import AFFINITY
        assert "RANGE_FADE" in AFFINITY

    def test_display_label_and_agent_name(self):
        from config import SIGNAL_TYPE_LABELS
        from src.api.snapshot import _AGENT_DISPLAY_NAMES, _PATH_TO_SETUP
        assert "RANGE_FADE" in SIGNAL_TYPE_LABELS
        assert _AGENT_DISPLAY_NAMES["RANGE_FADE"] == "The Range Keeper"
        assert _PATH_TO_SETUP["RANGE_FADE"] == "RANGE_FADE"

    def test_excluded_from_young_pair_and_mover_sets(self):
        import inspect
        from src.scanner import _YOUNG_PAIR_EVALUATORS
        assert "_evaluate_range_fade" not in _YOUNG_PAIR_EVALUATORS
        import src.scanner as sc
        src_txt = inspect.getsource(sc)
        # The mover allowlist is built inline; pin its deliberate absence.
        assert "_evaluate_range_fade is DELIBERATELY absent" in src_txt

    def test_execution_quality_anchor_field_exists(self):
        import dataclasses
        from src.channels.base import Signal
        names = (
            {f.name for f in dataclasses.fields(Signal)}
            if dataclasses.is_dataclass(Signal)
            else set(dir(Signal))
        )
        assert "range_fade_mid" in names
