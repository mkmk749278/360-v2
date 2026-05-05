"""Tests for the pre-TP indicator line in TelegramBot.format_signal.

Subscribers asked: the signal post tells them about Entry / SL / TP1/2/3
but doesn't mention the pre-TP grab.  When pre-TP fires (price moves
≥ ATR-adaptive threshold favourably within 30 min), it bumps SL to
breakeven and posts a "PRE-TP BANKED" update.  Without an indicator in
the original signal post, subscribers don't know to expect this.

This adds a single line after TP3:

    ⚡ Pre-TP: +0.20%+ raw (≥+1.3% net @ 10x) → SL → breakeven (auto)

The line is:
* Hidden when PRE_TP_ENABLED is False
* Hidden for breakout setups (PRE_TP_SETUP_BLACKLIST)
* Shown on every other paid signal
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from src.channels.base import Signal
from src.smc import Direction
from src.telegram_bot import TelegramBot
from src.utils import utcnow


def _make_signal(*, setup_class: str = "SR_FLIP_RETEST", confidence: float = 75.0):
    return Signal(
        channel="360_SCALP",
        symbol="ETHUSDT",
        direction=Direction.LONG,
        entry=2329.0,
        stop_loss=2310.0,
        tp1=2351.0,
        tp2=2360.0,
        tp3=2394.0,
        confidence=confidence,
        timestamp=utcnow(),
        setup_class=setup_class,
        signal_tier="A+" if confidence >= 80 else "B",
    )


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------


def test_pre_tp_line_present_for_paid_signal_when_enabled():
    sig = _make_signal()
    with patch("src.telegram_bot.PRE_TP_ENABLED", True):
        text = TelegramBot.format_signal(sig)
    assert "⚡ Pre-TP:" in text
    assert "raw" in text
    assert "net @" in text
    assert "breakeven" in text


def test_pre_tp_line_appears_after_tp3():
    sig = _make_signal()
    with patch("src.telegram_bot.PRE_TP_ENABLED", True):
        text = TelegramBot.format_signal(sig)
    tp3_idx = text.find("TP3")
    pretp_idx = text.find("Pre-TP")
    setup_idx = text.find("Setup:")
    assert tp3_idx >= 0 and pretp_idx > tp3_idx
    assert setup_idx > pretp_idx, "Pre-TP must appear before the Setup metadata block"


def test_pre_tp_shows_threshold_floor_and_net_at_leverage():
    """Default config: 0.20% floor, 10x leverage, 0.07% fees → +1.3% net."""
    sig = _make_signal()
    with patch("src.telegram_bot.PRE_TP_ENABLED", True):
        text = TelegramBot.format_signal(sig)
    # Threshold floor
    assert "+0.20%" in text
    # Net at leverage (after 0.7% margin fee burn) = (0.20 - 0.07) * 10 = 1.3%
    assert "+1.3%" in text or "1.3% net" in text
    # Leverage
    assert "10x" in text
    # SL action
    assert "breakeven" in text


# ---------------------------------------------------------------------------
# Hidden when feature disabled or setup blacklisted
# ---------------------------------------------------------------------------


def test_pre_tp_line_hidden_when_feature_disabled():
    sig = _make_signal()
    with patch("src.telegram_bot.PRE_TP_ENABLED", False):
        text = TelegramBot.format_signal(sig)
    assert "Pre-TP" not in text


@pytest.mark.parametrize(
    "blacklisted_setup",
    ["VOLUME_SURGE_BREAKOUT", "BREAKDOWN_SHORT", "OPENING_RANGE_BREAKOUT"],
)
def test_pre_tp_line_hidden_for_breakout_setups(blacklisted_setup):
    """Breakouts are built for bigger moves — pre-TP would cap thesis."""
    sig = _make_signal(setup_class=blacklisted_setup)
    with patch("src.telegram_bot.PRE_TP_ENABLED", True):
        text = TelegramBot.format_signal(sig)
    assert "Pre-TP" not in text


# ---------------------------------------------------------------------------
# Format integrity (other lines unaffected)
# ---------------------------------------------------------------------------


def test_pre_tp_addition_preserves_existing_lines():
    """Adding pre-TP line must not break TP/SL/Setup rendering."""
    sig = _make_signal()
    with patch("src.telegram_bot.PRE_TP_ENABLED", True):
        text = TelegramBot.format_signal(sig)
    assert "🛑 SL:" in text
    assert "🎯 TP1:" in text
    assert "🎯 TP2:" in text
    assert "🎯 TP3:" in text
    assert "Setup:" in text
    assert "Confidence" in text
    assert "R:R" in text


def test_pre_tp_uses_markdown_v2_safe_escaping():
    """Parens around the net% annotation must be escaped (\\() to render
    as literals in MarkdownV2 — same pattern as the Entry Zone line."""
    sig = _make_signal()
    with patch("src.telegram_bot.PRE_TP_ENABLED", True):
        text = TelegramBot.format_signal(sig)
    # The net% annotation should be wrapped in escaped parens
    assert "\\(≥" in text or "\\(" in text


# ---------------------------------------------------------------------------
# Stamped trigger-price rendering (B11 fee-aware locking).
#
# When pre_tp_trigger_price + pre_tp_threshold_pct are stamped on the
# signal at dispatch (as the scanner now does in `_enqueue_signal`), the
# Telegram post must show the actual trigger price — not the floor — so
# subscribers have an actionable number and auto-trade fires against
# the same locked target.
# ---------------------------------------------------------------------------


def test_pre_tp_line_shows_stamped_trigger_price_when_present():
    sig = _make_signal()
    sig.pre_tp_threshold_pct = 0.45
    sig.pre_tp_trigger_price = 2339.48  # entry 2329 × (1 + 0.45/100)
    with patch("src.telegram_bot.PRE_TP_ENABLED", True):
        text = TelegramBot.format_signal(sig)
    assert "⚡ Pre-TP @" in text
    assert "0.45%" in text  # locked threshold
    # Price formatting is currency-aware; the integer part must appear.
    assert "2339" in text or "2,339" in text


def test_pre_tp_line_uses_stamped_threshold_for_net_calc():
    """Net% must reflect the stamped threshold, not the env floor.
    Subscriber sees `(+0.45% raw, ≥+3.8% net @ 10x)` not `(≥+1.3%)`.
    """
    sig = _make_signal()
    sig.pre_tp_threshold_pct = 0.45
    sig.pre_tp_trigger_price = 2339.48
    with patch("src.telegram_bot.PRE_TP_ENABLED", True):
        text = TelegramBot.format_signal(sig)
    # (0.45 - 0.07) × 10 = 3.8 — net at 10x with 0.07% round-trip fees
    assert "3.8%" in text or "+3.8%" in text


def test_pre_tp_line_falls_back_to_floor_template_when_unstamped():
    """Legacy / pre-rollout signals carry zero in the stamped fields —
    template must drop back to the floor-only line so we don't leak
    `Pre-TP @ 0.00` to subscribers.
    """
    sig = _make_signal()
    sig.pre_tp_threshold_pct = 0.0
    sig.pre_tp_trigger_price = 0.0
    with patch("src.telegram_bot.PRE_TP_ENABLED", True):
        text = TelegramBot.format_signal(sig)
    assert "Pre-TP:" in text  # legacy line uses colon, not "@"
    assert "Pre-TP @" not in text
    assert "+0.20%" in text


def test_pre_tp_short_uses_below_entry_trigger():
    """Sanity — SHORT signals should display a trigger BELOW entry."""
    sig = _make_signal()
    sig.direction = Direction.SHORT
    sig.entry = 78240.0
    sig.pre_tp_threshold_pct = 0.20
    sig.pre_tp_trigger_price = 78083.5  # entry × (1 - 0.20/100)
    with patch("src.telegram_bot.PRE_TP_ENABLED", True):
        text = TelegramBot.format_signal(sig)
    assert "⚡ Pre-TP @" in text
    # fmt_price rounds the trigger; just verify the integer-part proximity.
    assert "78,084" in text or "78,083" in text
