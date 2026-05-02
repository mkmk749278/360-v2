"""Tests for ``src.auto_trade.risk_manager`` — Phase A2 risk gates.

Covers every gate plus integration with PaperOrderManager.

Gates verified:
* daily_loss_kill — triggers at threshold, sticky for the rest of UTC day
* min_equity_floor
* max_concurrent
* per_symbol_cap
* leverage_cap
* setup_blacklisted
* manual_pause (overrides everything)
* All-pass case (returns allowed=True)

Integration:
* PaperOrderManager + RiskManager rejects opens when gate trips
* Successful open registers position in RiskManager
* Full close releases position + applies PnL to daily total
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.auto_trade.risk_manager import RiskGateResult, RiskManager
from src.paper_order_manager import PaperOrderManager
from src.smc import Direction


def _make_signal(
    *,
    signal_id: str = "GATE-001",
    symbol: str = "BTCUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 30000.0,
    setup_class: str = "SR_FLIP_RETEST",
    leverage: float = 10.0,
):
    sig = MagicMock()
    sig.signal_id = signal_id
    sig.symbol = symbol
    sig.direction = direction
    sig.entry = entry
    sig.current_price = entry
    sig.setup_class = setup_class
    sig.leverage = leverage
    return sig


# ---------------------------------------------------------------------------
# Constructor validation
# ---------------------------------------------------------------------------


def test_rejects_zero_starting_equity():
    with pytest.raises(ValueError):
        RiskManager(starting_equity_usd=0)


def test_rejects_positive_loss_limit():
    """daily_loss_limit_pct must be negative (a loss)."""
    with pytest.raises(ValueError):
        RiskManager(starting_equity_usd=1000, daily_loss_limit_pct=3.0)


def test_rejects_zero_max_concurrent():
    with pytest.raises(ValueError):
        RiskManager(starting_equity_usd=1000, max_concurrent=0)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_check_allows_when_all_gates_pass():
    rm = RiskManager(starting_equity_usd=1000)
    sig = _make_signal(leverage=10.0)
    result = rm.check(sig)
    assert result.allowed is True
    assert result.reason == ""


# ---------------------------------------------------------------------------
# Daily loss kill
# ---------------------------------------------------------------------------


def test_daily_loss_kill_trips_at_threshold():
    rm = RiskManager(starting_equity_usd=1000, daily_loss_limit_pct=-3.0)
    sig = _make_signal()
    # Apply -3% loss directly via register_close
    rm._apply_realised_pnl(-30.0)  # exactly -3%
    result = rm.check(sig)
    assert result.allowed is False
    assert result.reason == "daily_loss_kill"


def test_daily_loss_kill_is_sticky_within_day():
    """Once tripped, recovery during the same UTC day still blocks."""
    rm = RiskManager(starting_equity_usd=1000, daily_loss_limit_pct=-3.0)
    sig = _make_signal()
    rm._apply_realised_pnl(-50.0)  # -5% — over threshold
    assert rm.check(sig).reason == "daily_loss_kill"
    # Recover back into profit — kill stays sticky
    rm._apply_realised_pnl(+100.0)  # +5% net for the day
    assert rm.daily_loss_pct == 5.0
    assert rm.check(sig).reason == "daily_loss_kill"
    assert rm.daily_kill_tripped is True


def test_daily_loss_kill_does_not_trip_below_threshold():
    rm = RiskManager(starting_equity_usd=1000, daily_loss_limit_pct=-3.0)
    sig = _make_signal()
    rm._apply_realised_pnl(-20.0)  # -2%, under threshold
    assert rm.check(sig).allowed is True
    assert rm.daily_kill_tripped is False


# ---------------------------------------------------------------------------
# Min equity floor
# ---------------------------------------------------------------------------


def test_min_equity_floor_blocks_below_floor():
    rm = RiskManager(starting_equity_usd=1000, min_equity_usd=500)
    rm._apply_realised_pnl(-600.0)  # equity now $400
    sig = _make_signal()
    # Daily loss kill would also trip — temporarily clear it to isolate
    rm._daily_kill_tripped = False
    rm._daily.realised_pnl_usd = 0.0  # zero out so daily kill doesn't fire
    rm._current_equity = 400.0
    assert rm.check(sig).reason == "min_equity_floor"


def test_min_equity_floor_disabled_by_default():
    rm = RiskManager(starting_equity_usd=1000)  # min_equity_usd defaults to 0
    sig = _make_signal()
    assert rm.check(sig).allowed is True


# ---------------------------------------------------------------------------
# Concurrent / per-symbol caps
# ---------------------------------------------------------------------------


def test_max_concurrent_blocks_new_open():
    rm = RiskManager(starting_equity_usd=10000, max_concurrent=2)
    rm.register_open(_make_signal(signal_id="A", symbol="BTCUSDT"))
    rm.register_open(_make_signal(signal_id="B", symbol="ETHUSDT"))
    new_sig = _make_signal(signal_id="C", symbol="SOLUSDT")
    assert rm.check(new_sig).reason == "max_concurrent"


def test_per_symbol_cap_blocks_doubling_up():
    rm = RiskManager(starting_equity_usd=10000)
    rm.register_open(_make_signal(signal_id="A", symbol="BTCUSDT"))
    second_btc = _make_signal(signal_id="B", symbol="BTCUSDT")
    assert rm.check(second_btc).reason == "per_symbol_cap"


def test_register_close_releases_capacity():
    rm = RiskManager(starting_equity_usd=10000, max_concurrent=1)
    sig = _make_signal(signal_id="A", symbol="BTCUSDT")
    rm.register_open(sig)
    assert rm.check(_make_signal(signal_id="B", symbol="ETHUSDT")).reason == "max_concurrent"
    rm.register_close(sig, realised_pnl_usd=10.0)
    assert rm.check(_make_signal(signal_id="B", symbol="ETHUSDT")).allowed is True


# ---------------------------------------------------------------------------
# Leverage cap
# ---------------------------------------------------------------------------


def test_leverage_cap_blocks_above_max():
    rm = RiskManager(starting_equity_usd=1000, max_leverage=30.0)
    sig = _make_signal()
    result = rm.check(sig, leverage=50.0)
    assert result.reason == "leverage_cap"


def test_leverage_at_cap_is_allowed():
    rm = RiskManager(starting_equity_usd=1000, max_leverage=30.0)
    sig = _make_signal()
    assert rm.check(sig, leverage=30.0).allowed is True


def test_leverage_falls_back_to_signal_attr():
    rm = RiskManager(starting_equity_usd=1000, max_leverage=10.0)
    sig = _make_signal(leverage=20.0)
    # No explicit leverage arg → reads from signal
    assert rm.check(sig).reason == "leverage_cap"


# ---------------------------------------------------------------------------
# Setup blacklist
# ---------------------------------------------------------------------------


def test_setup_blacklist_blocks_named_setup():
    rm = RiskManager(
        starting_equity_usd=1000,
        setup_blacklist={"OPENING_RANGE_BREAKOUT"},
    )
    sig = _make_signal(setup_class="OPENING_RANGE_BREAKOUT")
    assert rm.check(sig).reason == "setup_blacklisted"


def test_setup_blacklist_does_not_affect_other_setups():
    rm = RiskManager(
        starting_equity_usd=1000,
        setup_blacklist={"OPENING_RANGE_BREAKOUT"},
    )
    sig = _make_signal(setup_class="SR_FLIP_RETEST")
    assert rm.check(sig).allowed is True


# ---------------------------------------------------------------------------
# Manual pause
# ---------------------------------------------------------------------------


def test_manual_pause_blocks_everything():
    rm = RiskManager(starting_equity_usd=1000)
    rm.set_manual_pause(True)
    sig = _make_signal()
    result = rm.check(sig)
    assert result.allowed is False
    assert result.reason == "manual_pause"


def test_manual_pause_can_be_unpaused():
    rm = RiskManager(starting_equity_usd=1000)
    rm.set_manual_pause(True)
    rm.set_manual_pause(False)
    assert rm.check(_make_signal()).allowed is True


# ---------------------------------------------------------------------------
# Read-only state
# ---------------------------------------------------------------------------


def test_state_properties_reflect_activity():
    rm = RiskManager(starting_equity_usd=1000)
    rm.register_open(_make_signal(signal_id="A", symbol="BTCUSDT"))
    rm.register_open(_make_signal(signal_id="B", symbol="ETHUSDT"))
    assert rm.open_position_count == 2
    rm.register_close(
        _make_signal(signal_id="A", symbol="BTCUSDT"), realised_pnl_usd=15.0
    )
    assert rm.open_position_count == 1
    assert rm.daily_realised_pnl_usd == 15.0
    assert rm.daily_loss_pct == 1.5  # +15 on $1000 = +1.5%
    assert rm.current_equity_usd == 1015.0


# ---------------------------------------------------------------------------
# Integration with PaperOrderManager
# ---------------------------------------------------------------------------


async def test_paper_order_manager_respects_risk_gates():
    rm = RiskManager(starting_equity_usd=1000, max_concurrent=1)
    pm = PaperOrderManager(starting_equity_usd=1000, risk_manager=rm)

    first = _make_signal(signal_id="FIRST", symbol="BTCUSDT")
    second = _make_signal(signal_id="SECOND", symbol="ETHUSDT")

    # First open succeeds and registers.
    order_id = await pm.place_market_order(first)
    assert order_id is not None
    assert rm.open_position_count == 1

    # Second open is blocked by max_concurrent=1.
    blocked = await pm.place_market_order(second)
    assert blocked is None
    assert pm.open_position_count == 1  # still just the first


async def test_paper_close_releases_position_in_risk_manager():
    rm = RiskManager(starting_equity_usd=1000)
    pm = PaperOrderManager(starting_equity_usd=1000, risk_manager=rm)

    sig = _make_signal()
    await pm.place_market_order(sig)
    assert rm.open_position_count == 1

    # Full close (33+33+34%)
    await pm.close_partial(sig, fraction=0.33, tp_level=1, current_price=30100.0)
    await pm.close_partial(sig, fraction=0.33, tp_level=2, current_price=30200.0)
    await pm.close_partial(sig, fraction=0.34, tp_level=3, current_price=30300.0)
    assert rm.open_position_count == 0
    assert rm.daily_realised_pnl_usd > 0  # all three TPs were profitable


async def test_paper_blocked_by_daily_loss_kill():
    """Force a daily loss kill, then verify subsequent opens are blocked."""
    rm = RiskManager(starting_equity_usd=1000, daily_loss_limit_pct=-3.0)
    pm = PaperOrderManager(starting_equity_usd=1000, risk_manager=rm)
    # Trip the kill directly.
    rm._apply_realised_pnl(-50.0)  # -5%
    sig = _make_signal()
    blocked = await pm.place_market_order(sig)
    assert blocked is None
    assert pm.open_position_count == 0
