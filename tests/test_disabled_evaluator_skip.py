"""Feature-flag-disabled evaluators are skipped, not invoked (2026-08-29).

ORB (``SCALP_ORB_ENABLED=false``) and CLS (``CLS_DISABLED_2026_05_17=true``)
are dormant by doctrine, but their evaluators were still CALLED for every
pair on every scan cycle just to return a flag-check rejection — ~59k no-op
calls each per truth-report window on the live box.  ``evaluate()`` now
consults ``_disabled_evaluator_rejects()`` and records the rejection without
the call.

The telemetry contract is the load-bearing part: the truth report must keep
showing non-zero suppression for disabled paths with the SAME tokens
(``feature_disabled`` / ``cls_disabled_merged_into_lsr``) so "disabled by
doctrine" stays distinguishable from "no candidates" (OWNER_BRIEF §3.4a).
"""
from __future__ import annotations

from unittest.mock import patch

from src.channels.scalp import ScalpChannel


def _minimal_candles(n=60):
    return {
        "5m": {
            "close": [100.0] * n, "open": [100.0] * n,
            "high": [100.5] * n, "low": [99.5] * n,
            "volume": [1000.0] * n,
        },
    }


def _run_evaluate(ch):
    ch.evaluate(
        "BTCUSDT", _minimal_candles(), {}, {}, 0.001, 10_000_000,
        regime="TRENDING_UP",
    )
    return ch.consume_generation_telemetry()


def test_disabled_orb_records_same_telemetry_without_a_call():
    ch = ScalpChannel()
    calls = []
    with patch("src.channels.scalp.SCALP_ORB_ENABLED", False), \
         patch.object(
             ch, "_evaluate_opening_range_breakout",
             side_effect=lambda *a, **k: calls.append(1) or None,
         ):
        telem = _run_evaluate(ch)
    assert not calls, "disabled ORB evaluator must not be invoked"
    # Exact same counters and tokens the in-evaluator flag check produced.
    assert telem["attempts"]["OPENING_RANGE_BREAKOUT"] == 1
    assert telem["no_signal"]["OPENING_RANGE_BREAKOUT"] == 1
    assert telem["no_signal_reason"][
        "OPENING_RANGE_BREAKOUT:feature_disabled"
    ] == 1


def test_disabled_cls_records_doctrine_token_without_a_call():
    ch = ScalpChannel()
    calls = []
    with patch("src.channels.scalp._CLS_DISABLED_2026_05_17", True), \
         patch.object(
             ch, "_evaluate_continuation_liquidity_sweep",
             side_effect=lambda *a, **k: calls.append(1) or None,
         ):
        telem = _run_evaluate(ch)
    assert not calls, "disabled CLS evaluator must not be invoked"
    assert telem["attempts"]["CONTINUATION_LIQUIDITY_SWEEP"] == 1
    assert telem["no_signal_reason"][
        "CONTINUATION_LIQUIDITY_SWEEP:cls_disabled_merged_into_lsr"
    ] == 1


def test_reenabled_orb_is_invoked_again():
    # The skip map is computed at call time from the module globals, so an
    # env re-enable (or a test patch) restores the call without a restart.
    ch = ScalpChannel()
    calls = []
    with patch("src.channels.scalp.SCALP_ORB_ENABLED", True), \
         patch.object(
             ch, "_evaluate_opening_range_breakout",
             side_effect=lambda *a, **k: calls.append(1) or None,
         ):
        _run_evaluate(ch)
    assert len(calls) == 1, "re-enabled ORB evaluator must be invoked"


def test_allowed_evaluators_restriction_still_wins():
    # A restricted scan context (mover allowlist) that excludes a disabled
    # path must record NOTHING for it — the allowlist check comes first,
    # same as before the skip.
    ch = ScalpChannel()
    with patch("src.channels.scalp.SCALP_ORB_ENABLED", False):
        ch.evaluate(
            "GUAUSDT", _minimal_candles(), {}, {}, 0.001, 10_000_000,
            regime="TRENDING_UP",
            allowed_evaluators=frozenset({"_evaluate_volume_surge_breakout"}),
        )
        telem = ch.consume_generation_telemetry()
    assert "OPENING_RANGE_BREAKOUT" not in telem["attempts"]


def test_in_evaluator_flag_check_remains_as_safety_net():
    # Direct calls (tests, diagnostics) still hit the in-evaluator check.
    ch = ScalpChannel()
    with patch("src.channels.scalp.SCALP_ORB_ENABLED", False):
        sig = ch._evaluate_opening_range_breakout(
            "BTCUSDT", _minimal_candles(), {}, {}, 0.001, 10_000_000,
            regime="TRENDING_UP",
        )
    assert sig is None
    assert ch._active_no_signal_reason == "feature_disabled"
