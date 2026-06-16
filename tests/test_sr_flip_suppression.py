"""Tests for the SR_FLIP_RETEST setup-level kill switch (2026-06-16).

7-day ops-dashboard counterfactual (n=106): WITH SR_FLIP_RETEST the book is
+6.46% (avg +0.061/signal); WITHOUT it, +12.78% over 63 signals (avg +0.203 —
3.3x better/signal).  SR_FLIP is ~40% of signal volume and net-negative across
every slice — LONG (-0.16) ~= SHORT (-0.16), and confidence INVERTS (conf<70
~flat, conf>=75 worst at -0.46, 0/3 wins) — so no score threshold rescues it.
LIQUIDITY_SWEEP_REVERSAL is deliberately NOT suppressed (turned net-positive).

Pure predicate Scanner._should_suppress_sr_flip_retest drives the call-site
shadow-vs-block decision; gated by config.SR_FLIP_RETEST_SUPPRESS_ENABLED.
"""
from __future__ import annotations

import config
import src.scanner as scanner
from src.scanner import Scanner

P = Scanner._should_suppress_sr_flip_retest


class TestSrFlipSuppressionPredicate:
    def test_ships_dark(self):
        # Paid-channel routing change — must default OFF so merge-to-main is
        # behavior-neutral; activation is a one-line env flag on the VPS.
        assert config.SR_FLIP_RETEST_SUPPRESS_ENABLED is False

    def test_no_suppression_while_flag_off(self):
        # Default (dark): even SR_FLIP_RETEST passes — only [SHADOW] telemetry.
        assert P("SR_FLIP_RETEST") is False

    def test_suppresses_only_sr_flip_when_enabled(self, monkeypatch):
        monkeypatch.setattr(scanner, "SR_FLIP_RETEST_SUPPRESS_ENABLED", True)
        assert P("SR_FLIP_RETEST") is True
        # Surgical: the kill switch touches SR_FLIP_RETEST and nothing else.
        for other in (
            "LIQUIDITY_SWEEP_REVERSAL",   # turned net-positive — must keep firing
            "FAILED_AUCTION_RECLAIM",
            "DIVERGENCE_CONTINUATION",
            "VOLUME_SURGE_BREAKOUT",
        ):
            assert P(other) is False
