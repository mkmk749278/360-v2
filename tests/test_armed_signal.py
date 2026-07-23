"""Unit tests for the precise-entry arming resolver (pure, no I/O).

Candles are (open, high, low, close, volume).  These mirror the validated
no-look-ahead replay logic: a turn triggers only on a momentum hook + volume
confirm whose *structural* stop is tighter than max_sl_pct; otherwise it keeps
watching and eventually expires (no trade).
"""
from __future__ import annotations

from src.armed_signal import ArmConfig, ArmStatus, resolve_arm


def test_long_turn_triggers_with_tight_structural_stop():
    candles = [
        (100.0, 100.2, 99.8, 100.0, 10.0),
        (100.0, 100.1, 99.5, 99.6, 10.0),   # shallow pullback, swing low 99.5
        (99.6, 100.6, 99.5, 100.5, 30.0),   # turn: reclaims prior high, green, vol burst
    ]
    out = resolve_arm("LONG", candles)
    assert out.status is ArmStatus.TRIGGERED
    assert out.trigger_index == 2
    assert out.entry == 100.5
    # stop anchored just below the 99.5 swing low; well inside the 3% cap
    assert 99.0 < out.stop < 99.5
    assert out.sl_pct is not None and out.sl_pct < 3.0


def test_short_turn_triggers_mirror():
    candles = [
        (100.0, 100.2, 99.8, 100.0, 10.0),
        (100.0, 100.6, 99.9, 100.4, 10.0),   # small bounce, swing high 100.6
        (100.4, 100.5, 99.3, 99.4, 30.0),    # turn down: takes prior low, red, vol burst
    ]
    out = resolve_arm("SHORT", candles)
    assert out.status is ArmStatus.TRIGGERED
    assert out.entry == 99.4
    assert out.stop > 100.4          # stop above the bounce high
    assert out.sl_pct is not None and out.sl_pct < 3.0


def test_wide_stop_turn_is_rejected_then_expires():
    # A genuine momentum hook, but the pullback was so deep the only structural
    # stop is 5%+ wide — not a precise entry.  With a short window it expires.
    candles = [
        (100.0, 100.2, 99.8, 100.0, 10.0),
        (100.0, 100.1, 95.0, 96.0, 10.0),    # deep pullback, swing low 95
        (96.0, 100.6, 95.0, 100.5, 30.0),    # hook, but stop ~5.6% wide -> reject
    ]
    out = resolve_arm("LONG", candles, ArmConfig(expire_bars=3))
    assert out.status is ArmStatus.EXPIRED


def test_low_volume_turn_does_not_trigger():
    candles = [
        (100.0, 100.2, 99.8, 100.0, 10.0),
        (100.0, 100.1, 99.5, 99.6, 10.0),
        (99.6, 100.6, 99.5, 100.5, 5.0),     # same hook, but volume below baseline
    ]
    out = resolve_arm("LONG", candles)   # long default window -> still watching
    assert out.status is ArmStatus.PENDING


def test_insufficient_candles_is_pending():
    out = resolve_arm("LONG", [(100.0, 100.2, 99.8, 100.0, 10.0)])
    assert out.status is ArmStatus.PENDING
    assert out.reason == "insufficient_candles"


def test_no_turn_expires_no_trade():
    # Monotonic drift with no reclaim of a prior high -> never triggers.
    candles = [(100.0 - i, 100.3 - i, 99.5 - i, 99.8 - i, 10.0) for i in range(5)]
    out = resolve_arm("LONG", candles, ArmConfig(expire_bars=5))
    assert out.status is ArmStatus.EXPIRED
    assert out.reason == "no_turn_in_window"


def test_malformed_candle_fails_toward_expired():
    # A resolver bug/bad data must never break the money path: fail toward
    # EXPIRED (no trade), the safe direction.
    out = resolve_arm("LONG", [(1.0, 1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0)])
    assert out.status is ArmStatus.EXPIRED
    assert out.reason == "resolver_error"
