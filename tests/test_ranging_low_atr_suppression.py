"""Tests for the RANGING low-ATR loser-setup suppression gate (2026-06-15).

Live last-100 audit: in RANGING + low-ATR chop, SR_FLIP_RETEST (-4.36%) and
LIQUIDITY_SWEEP_REVERSAL (-3.77%) bleed at ~1:2 win:loss, while FAR (+0.71)
and DIVCON (+0.42) stay positive.  This gate suppresses only the two losers,
and only when the range is also low-ATR.  Pure predicate
Scanner._should_block_ranging_low_atr_loser drives the call-site decision.
"""
from __future__ import annotations

import importlib

import config
from src.scanner import Scanner

P = Scanner._should_block_ranging_low_atr_loser


class TestRangingLowAtrPredicate:
    def test_loser_in_low_atr_ranging_blocks(self):
        assert P("SR_FLIP_RETEST", True, 10.0) is True
        assert P("LIQUIDITY_SWEEP_REVERSAL", True, 0.0) is True

    def test_boundary_inclusive(self):
        # Default percentile threshold is 25 — boundary is suppressed (<=).
        assert config.RANGING_LOW_ATR_SUPPRESS_PCTILE == 25.0
        assert P("SR_FLIP_RETEST", True, 25.0) is True
        assert P("SR_FLIP_RETEST", True, 25.01) is False

    def test_high_atr_range_allowed(self):
        # A volatile/expanding range still offers reversal edge — not suppressed.
        assert P("SR_FLIP_RETEST", True, 60.0) is False

    def test_winner_setups_never_suppressed(self):
        # FAR and DIVCON are profitable — must pass even in dead chop.
        assert P("FAILED_AUCTION_RECLAIM", True, 1.0) is False
        assert P("DIVERGENCE_CONTINUATION", True, 1.0) is False

    def test_not_ranging_allowed(self):
        # Trending markets are the runner regime — gate must not fire there.
        assert P("SR_FLIP_RETEST", False, 1.0) is False

    def test_missing_atr_fails_open(self):
        # No ATR percentile available → do not suppress (fail open).
        assert P("SR_FLIP_RETEST", True, None) is False

    def test_default_setup_set_targets_the_two_losers(self):
        assert config.RANGING_LOW_ATR_SUPPRESS_SETUPS == frozenset(
            {"SR_FLIP_RETEST", "LIQUIDITY_SWEEP_REVERSAL"}
        )

    def test_ships_dark(self):
        # Routing change — must default OFF so merge-to-main is behavior-neutral.
        assert config.RANGING_LOW_ATR_LOSER_SUPPRESS_ENABLED is False
