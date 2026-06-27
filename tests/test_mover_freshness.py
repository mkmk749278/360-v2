"""Mover-freshness gate (VSB/BDS) — rejects stale or exhausted continuation
breakouts so the engine stops 'promoting after the move, then fighting the
exhaustion' (owner finding 2026-06-26).

The gate is a pure helper (no instance state), so we exercise it directly
across the band boundaries + the recency cap + the off-switch + fail-open.
"""
import pytest

import src.channels.scalp as scalp
from src.channels.scalp import ScalpChannel

_LB = scalp._MOVER_FRESHNESS_LOOKBACK


def _ch():
    # The helper reads no instance state — bypass __init__ to avoid config wiring.
    return ScalpChannel.__new__(ScalpChannel)


def _closes(past_close: float, n: int = 30):
    """Build a closes list whose value LOOKBACK candles back == past_close."""
    arr = [past_close] * n
    arr[-(_LB + 1)] = past_close
    return arr


def test_fresh_long_passes():
    ok, reason = _ch()._check_mover_freshness(
        closes=_closes(100.0), swing_level=104.0, breakout_idx=-2, is_long=True
    )
    assert ok and reason == ""


def test_fresh_short_passes():
    # SHORT impulse = (past_close - swing_low)/past_close = 4%
    ok, reason = _ch()._check_mover_freshness(
        closes=_closes(100.0), swing_level=96.0, breakout_idx=-2, is_long=False
    )
    assert ok and reason == ""


def test_stale_move_rejected():
    # 0.5% recent impulse < MIN (1.5%) → no live momentum, stale 24h mover.
    ok, reason = _ch()._check_mover_freshness(
        closes=_closes(100.0), swing_level=100.5, breakout_idx=-2, is_long=True
    )
    assert not ok and reason == "move_not_fresh"


def test_exhausted_move_rejected_long():
    # 15% recent impulse > MAX (10%) → blow-off; entering late.
    ok, reason = _ch()._check_mover_freshness(
        closes=_closes(100.0), swing_level=115.0, breakout_idx=-2, is_long=True
    )
    assert not ok and reason == "move_exhausted"


def test_exhausted_dump_rejected_short():
    # SHORT: 15% drop into the level > MAX → oversold-bounce trap.
    ok, reason = _ch()._check_mover_freshness(
        closes=_closes(100.0), swing_level=85.0, breakout_idx=-2, is_long=False
    )
    assert not ok and reason == "move_exhausted"


def test_stale_breakout_age_rejected():
    # Breakout candle older than MAX_BREAKOUT_AGE regardless of a healthy impulse.
    old = scalp._MOVER_FRESHNESS_MAX_BREAKOUT_AGE + 2
    ok, reason = _ch()._check_mover_freshness(
        closes=_closes(100.0), swing_level=104.0, breakout_idx=-old, is_long=True
    )
    assert not ok and reason == "breakout_stale"


def test_disabled_fails_open(monkeypatch):
    monkeypatch.setattr(scalp, "_MOVER_FRESHNESS_ENABLED", False)
    # Even a clearly-stale move passes when the gate is off.
    ok, reason = _ch()._check_mover_freshness(
        closes=_closes(100.0), swing_level=100.1, breakout_idx=-2, is_long=True
    )
    assert ok and reason == ""


def test_insufficient_history_fails_open():
    short = [100.0] * (_LB - 2)  # fewer than LOOKBACK+1 candles
    ok, reason = _ch()._check_mover_freshness(
        closes=short, swing_level=104.0, breakout_idx=-2, is_long=True
    )
    assert ok and reason == ""


def test_boundaries_inclusive():
    ch = _ch()
    # Exactly MIN → pass (>= boundary).
    ok_min, _ = ch._check_mover_freshness(
        closes=_closes(100.0),
        swing_level=100.0 + scalp._MOVER_FRESHNESS_MIN_PCT,
        breakout_idx=-2,
        is_long=True,
    )
    assert ok_min
    # Exactly MAX → pass (<= boundary).
    ok_max, _ = ch._check_mover_freshness(
        closes=_closes(100.0),
        swing_level=100.0 + scalp._MOVER_FRESHNESS_MAX_PCT,
        breakout_idx=-2,
        is_long=True,
    )
    assert ok_max
