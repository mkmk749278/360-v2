"""Tests for ``src.pre_tp_stamping``.

The stamping module locks the pre-TP threshold + trigger price at
dispatch time (B11 fee-aware doctrine).  These tests cover:

  - ATR resolution paths (atr / atr_floored / static fallback)
  - Eligibility gates (PRE_TP_ENABLED, setup blacklist)
  - Long vs short trigger-price arithmetic
  - Idempotency of ``stamp_pre_tp``
  - ``is_stamped`` detection
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

import config
from src.channels.base import Signal
from src.pre_tp_stamping import (
    is_eligible,
    is_stamped,
    resolve_pre_tp_threshold,
    stamp_pre_tp,
)
from src.smc import Direction


# Auto-enable pre-TP for the tests in this module.  The default in production
# is `PRE_TP_ENABLED=False` (override in docker-compose flips it on); tests
# need it on to exercise the eligibility / stamping path.  Module-scoped via
# autouse so each test sees a consistent runtime config.
@pytest.fixture(autouse=True)
def _enable_pre_tp(monkeypatch):
    monkeypatch.setattr(config, "PRE_TP_ENABLED", True, raising=False)


# Bind the constants now (after autouse fixture won't run for module-level
# imports anyway) — tests reference them directly.
PRE_TP_ATR_MULTIPLIER = config.PRE_TP_ATR_MULTIPLIER
PRE_TP_FEE_FLOOR_PCT = config.PRE_TP_FEE_FLOOR_PCT
PRE_TP_THRESHOLD_PCT = config.PRE_TP_THRESHOLD_PCT


def _signal(
    *,
    direction: Direction = Direction.LONG,
    entry: float = 2370.0,
    atr_val: float = 0.0,
    setup_class: str = "SR_FLIP_RETEST",
) -> Signal:
    return Signal(
        channel="360_SCALP",
        symbol="ETHUSDT",
        direction=direction,
        entry=entry,
        stop_loss=entry * 0.99 if direction == Direction.LONG else entry * 1.01,
        tp1=entry * 1.01 if direction == Direction.LONG else entry * 0.99,
        tp2=entry * 1.02 if direction == Direction.LONG else entry * 0.98,
        tp3=entry * 1.03 if direction == Direction.LONG else entry * 0.97,
        signal_id="sig-001",
        setup_class=setup_class,
        atr_val=atr_val,
        timestamp=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# resolve_pre_tp_threshold
# ---------------------------------------------------------------------------


def test_resolve_returns_static_when_atr_missing() -> None:
    pct, src = resolve_pre_tp_threshold(entry=2370.0, atr_val=None)
    assert src == "static"
    assert pct == PRE_TP_THRESHOLD_PCT


def test_resolve_returns_static_when_atr_zero() -> None:
    pct, src = resolve_pre_tp_threshold(entry=2370.0, atr_val=0.0)
    assert src == "static"
    assert pct == PRE_TP_THRESHOLD_PCT


def test_resolve_returns_static_when_entry_zero() -> None:
    """Defensive — pathological entry should not divide by zero."""
    pct, src = resolve_pre_tp_threshold(entry=0.0, atr_val=10.0)
    assert src == "static"
    assert pct == PRE_TP_THRESHOLD_PCT


def test_resolve_atr_floored_when_atr_term_below_floor() -> None:
    """Low-vol pair: ATR×mult is below the fee floor → floor wins."""
    # entry=10000, atr=1.0 → atr_pct=0.01, atr*mult well below floor
    pct, src = resolve_pre_tp_threshold(entry=10000.0, atr_val=1.0)
    assert src == "atr_floored"
    assert pct == PRE_TP_FEE_FLOOR_PCT


def test_resolve_atr_wins_when_above_floor() -> None:
    """High-vol alt: ATR×mult exceeds the fee floor → ATR wins."""
    # entry=100, atr=2.0 → atr_pct=2.0, atr*mult >> floor
    pct, src = resolve_pre_tp_threshold(entry=100.0, atr_val=2.0)
    assert src == "atr"
    assert pct > PRE_TP_FEE_FLOOR_PCT
    expected = (2.0 / 100.0) * 100.0 * PRE_TP_ATR_MULTIPLIER
    assert pct == pytest.approx(expected)


# ---------------------------------------------------------------------------
# is_eligible
# ---------------------------------------------------------------------------


def test_eligible_for_eligible_setup() -> None:
    assert is_eligible(_signal(setup_class="SR_FLIP_RETEST"))


def test_not_eligible_for_blacklisted_setup() -> None:
    """Breakouts (VSB / BDS / ORB) are blacklisted by doctrine."""
    assert not is_eligible(_signal(setup_class="VOLUME_SURGE_BREAKOUT"))


def test_not_eligible_when_setup_class_empty() -> None:
    """Defensive — empty setup_class falls back to eligible (per existing
    template logic in telegram_bot.py)."""
    sig = _signal(setup_class="")
    # is_eligible: empty string is_in PRE_TP_SETUP_BLACKLIST is False, so eligible
    assert is_eligible(sig)


# ---------------------------------------------------------------------------
# stamp_pre_tp
# ---------------------------------------------------------------------------


def test_stamp_long_writes_threshold_and_trigger() -> None:
    sig = _signal(direction=Direction.LONG, entry=2370.0, atr_val=4.74)
    stamp_pre_tp(sig)
    assert sig.pre_tp_threshold_pct > 0
    assert sig.pre_tp_trigger_price > sig.entry  # LONG → trigger above entry


def test_stamp_short_writes_threshold_and_trigger() -> None:
    sig = _signal(direction=Direction.SHORT, entry=78240.0, atr_val=156.0)
    stamp_pre_tp(sig)
    assert sig.pre_tp_threshold_pct > 0
    assert sig.pre_tp_trigger_price < sig.entry  # SHORT → trigger below entry


def test_stamp_trigger_price_matches_threshold_arithmetic() -> None:
    """Trigger should equal entry × (1 ± threshold/100) — locked promise."""
    sig = _signal(direction=Direction.LONG, entry=1000.0, atr_val=5.0)
    stamp_pre_tp(sig)
    expected_trigger = 1000.0 * (1.0 + sig.pre_tp_threshold_pct / 100.0)
    assert sig.pre_tp_trigger_price == pytest.approx(expected_trigger, rel=1e-6)


def test_stamp_noop_for_blacklisted_setup() -> None:
    sig = _signal(setup_class="VOLUME_SURGE_BREAKOUT", atr_val=4.0)
    stamp_pre_tp(sig)
    assert sig.pre_tp_threshold_pct == 0.0
    assert sig.pre_tp_trigger_price == 0.0


def test_stamp_noop_when_entry_invalid() -> None:
    sig = _signal(entry=0.0, atr_val=4.0)
    stamp_pre_tp(sig)
    assert sig.pre_tp_threshold_pct == 0.0
    assert sig.pre_tp_trigger_price == 0.0


def test_stamp_falls_back_to_static_when_no_atr() -> None:
    """Without ATR the static fallback still produces a usable stamp.
    This is the doctrinal soft-fallback so subscribers always see *some*
    trigger price even when the indicator pipeline is starved."""
    sig = _signal(atr_val=0.0)
    stamp_pre_tp(sig)
    assert sig.pre_tp_threshold_pct == pytest.approx(PRE_TP_THRESHOLD_PCT)
    expected_trigger = sig.entry * (1.0 + PRE_TP_THRESHOLD_PCT / 100.0)
    assert sig.pre_tp_trigger_price == pytest.approx(expected_trigger, rel=1e-6)


def test_stamp_is_idempotent() -> None:
    """Re-stamping the same signal produces the same values — important
    because backfill in the trade-monitor stamps too, and any future
    code path could re-call without harm."""
    sig = _signal(entry=2370.0, atr_val=4.74)
    stamp_pre_tp(sig)
    first_threshold = sig.pre_tp_threshold_pct
    first_trigger = sig.pre_tp_trigger_price
    stamp_pre_tp(sig)
    assert sig.pre_tp_threshold_pct == first_threshold
    assert sig.pre_tp_trigger_price == first_trigger


# ---------------------------------------------------------------------------
# is_stamped
# ---------------------------------------------------------------------------


def test_is_stamped_false_on_fresh_signal() -> None:
    assert not is_stamped(_signal())


def test_is_stamped_true_after_stamp() -> None:
    sig = _signal(atr_val=4.74)
    stamp_pre_tp(sig)
    assert is_stamped(sig)


def test_is_stamped_false_when_blacklisted() -> None:
    """Stamp is a no-op for blacklisted setups — `is_stamped` must
    correctly report unstamped to keep the trade-monitor on the
    backfill path (or the safe-skip path, depending on PRE_TP_ENABLED)."""
    sig = _signal(setup_class="VOLUME_SURGE_BREAKOUT", atr_val=4.0)
    stamp_pre_tp(sig)
    assert not is_stamped(sig)


def test_eligible_false_when_globally_disabled(monkeypatch) -> None:
    """Master switch — owner can disable pre-TP without redeploying."""
    monkeypatch.setattr(config, "PRE_TP_ENABLED", False, raising=False)
    assert not is_eligible(_signal())


def test_stamp_noop_when_globally_disabled(monkeypatch) -> None:
    monkeypatch.setattr(config, "PRE_TP_ENABLED", False, raising=False)
    sig = _signal(atr_val=4.74)
    stamp_pre_tp(sig)
    assert sig.pre_tp_threshold_pct == 0.0
    assert sig.pre_tp_trigger_price == 0.0


def test_is_stamped_robust_to_partial_stamp() -> None:
    """If only one of the two fields is populated (shouldn't happen but
    defensive), is_stamped returns False so the monitor doesn't fire on
    incomplete data."""
    sig = _signal()
    sig.pre_tp_threshold_pct = 0.20
    # pre_tp_trigger_price still 0.0
    assert not is_stamped(sig)
    sig.pre_tp_threshold_pct = 0.0
    sig.pre_tp_trigger_price = 100.0
    assert not is_stamped(sig)
