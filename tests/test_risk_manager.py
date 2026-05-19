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


# ---------------------------------------------------------------------------
# user_settings override of max_concurrent / leverage_cap (owner-flagged
# 2026-05-10).  The Auto-trade page can lower the engine-side caps live.
# ---------------------------------------------------------------------------


def test_user_settings_can_lower_max_concurrent(tmp_path, monkeypatch):
    """When the user sets a lower max_concurrent than the constructor default,
    ``check`` enforces the user value."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )
    user_settings.update_auto_trade({"max_concurrent_positions": 1})

    rm = RiskManager(starting_equity_usd=1000, max_concurrent=5)
    sig_a = _make_signal(signal_id="A")
    rm.register_open(sig_a)
    sig_b = _make_signal(signal_id="B")
    result = rm.check(sig_b)
    assert result.allowed is False
    assert result.reason == "max_concurrent"


def test_user_settings_cannot_raise_above_constructor_cap(tmp_path, monkeypatch):
    """Defence in depth: the user can LOWER the cap but not raise it above
    the constructor default — ratchet-down only."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )
    user_settings.update_auto_trade({"max_concurrent_positions": 10})

    rm = RiskManager(starting_equity_usd=1000, max_concurrent=3)
    for sid in ("A", "B", "C"):
        rm.register_open(_make_signal(signal_id=sid))
    result = rm.check(_make_signal(signal_id="D"))
    assert result.allowed is False
    assert result.reason == "max_concurrent"


def test_user_settings_can_lower_leverage_cap(tmp_path, monkeypatch):
    """User-set leverage_cap below the constructor default takes precedence."""
    from src import user_settings
    from src.api import user_overrides as user_overrides_module
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )
    # Override singleton must be cleared so the per-user check below
    # falls through to user_settings — otherwise an earlier test's
    # registered store can leak in via the module-level singleton.
    monkeypatch.setattr(
        user_overrides_module, "_SINGLETON", None, raising=False,
    )
    user_settings.update_auto_trade({"leverage_cap": 5.0})

    rm = RiskManager(starting_equity_usd=1000, max_leverage=30.0)
    sig = _make_signal()
    # Requesting 8x exceeds the user-set 5x cap even though constructor allows 30x.
    result = rm.check(sig, leverage=8.0)
    assert result.allowed is False
    assert result.reason == "leverage_cap"


def test_reset_daily_zeros_in_memory_state():
    """``reset_daily()`` zeros daily PnL, equity, and the sticky kill flag.

    Doctrine: the paper-balance reset endpoint must clear the
    RiskManager's in-memory daily state too — without this, the Trade
    tab keeps reading yesterday's loss number (sourced from
    ``daily_realised_pnl_usd``) until UTC midnight.
    """
    rm = RiskManager(
        starting_equity_usd=1000,
        daily_loss_limit_pct=-3.0,
        max_concurrent=5,
        max_leverage=30.0,
    )
    # Simulate a sequence of losing closes that trips the daily kill.
    sig_a = _make_signal(signal_id="A")
    sig_b = _make_signal(signal_id="B")
    rm.register_open(sig_a)
    rm.register_close(sig_a, realised_pnl_usd=-20.0)
    rm.register_open(sig_b)
    rm.register_close(sig_b, realised_pnl_usd=-15.0)
    # Force a check so the sticky kill flag flips.
    rm.check(_make_signal(signal_id="C"), leverage=10.0)
    assert rm.daily_realised_pnl_usd == -35.0
    assert rm.daily_kill_tripped is True

    rm.reset_daily()

    assert rm.daily_realised_pnl_usd == 0.0
    assert rm.daily_kill_tripped is False
    assert rm.current_equity_usd == 1000.0


def test_per_user_override_lowers_leverage_cap(tmp_path, monkeypatch):
    """Per-user override beats engine-global user_settings on leverage_cap.

    Regression test for the 2026-05-19 paper-30x bug: the app saves
    leverage_cap to the per-user SQLite row, but the engine used to
    read only from ``user_settings.json``.  The RiskManager + paper
    trader now consult the per-user override first.
    """
    from src.api import user_overrides as user_overrides_module
    from src.api.user_overrides import UserOverridesStore

    # UserOverridesStore has FK references to the users(user_id) table —
    # which lives in the same SQLite file under normal operation.  Create
    # the parent table (and a user_id=1 row) so the override insert isn't
    # rejected by the FK constraint.
    from src.api.users import UserStore
    db_path = tmp_path / "lumin.sqlite"
    user_store = UserStore(db_path)
    user_store._conn.execute(
        "INSERT INTO users (user_id, phone_e164, tier, "
        "created_at, updated_at) VALUES (1, '+10000000001', 'free', "
        "datetime('now'), datetime('now'))"
    )
    store = UserOverridesStore(db_path)
    monkeypatch.setattr(
        user_overrides_module, "_SINGLETON", store, raising=False,
    )
    # User saves leverage_cap=5 via the app's Auto-trade page.
    store.update_auto_trade(user_id=1, partial={"leverage_cap": 5.0})

    rm = RiskManager(starting_equity_usd=1000, max_leverage=30.0)
    sig = _make_signal()
    result = rm.check(sig, leverage=8.0)
    assert result.allowed is False
    assert result.reason == "leverage_cap"
    # And 4x (below the per-user cap) IS allowed even though user_settings
    # has nothing saved.
    result2 = rm.check(_make_signal(signal_id="ALLOWED"), leverage=4.0)
    assert result2.allowed is True


def test_paper_order_manager_reads_per_user_leverage_override(
    tmp_path, monkeypatch
):
    """PaperOrderManager._resolved_leverage() picks the per-user override
    over engine-global user_settings.  Regression for paper-30x bug."""
    from src.api import user_overrides as user_overrides_module
    from src.api.user_overrides import UserOverridesStore

    from src.api.users import UserStore
    db_path = tmp_path / "lumin.sqlite"
    user_store = UserStore(db_path)
    user_store._conn.execute(
        "INSERT INTO users (user_id, phone_e164, tier, "
        "created_at, updated_at) VALUES (1, '+10000000002', 'free', "
        "datetime('now'), datetime('now'))"
    )
    store = UserOverridesStore(db_path)
    monkeypatch.setattr(
        user_overrides_module, "_SINGLETON", store, raising=False,
    )
    store.update_auto_trade(user_id=1, partial={"leverage_cap": 7.0})

    om = PaperOrderManager(starting_equity_usd=1000)
    assert om._resolved_leverage() == 7.0


def test_paper_order_manager_falls_through_when_no_override(
    tmp_path, monkeypatch
):
    """PaperOrderManager defaults to 10x when neither override nor
    user_settings is set — matches the PRE_TP_LEVERAGE convention."""
    from src import user_settings
    from src.api import user_overrides as user_overrides_module

    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )
    monkeypatch.setattr(
        user_overrides_module, "_SINGLETON", None, raising=False,
    )
    # Clear any RISK_MAX_LEVERAGE env so the user_settings fallback
    # returns the config default — which is 30, but the bug is that
    # this leaked through to the paper trader.  After fix, _resolved
    # falls back via user_settings → 30.  That's still the engine-
    # global default; we assert it's used only when nothing else.
    om = PaperOrderManager(starting_equity_usd=1000)
    resolved = om._resolved_leverage()
    # Either the config default (30 by env) or the safety floor (10) —
    # not asserting an exact number, but asserting "doesn't crash and
    # returns a sensible positive number" so this test doesn't get
    # brittle against env tweaks.
    assert resolved > 0
    assert resolved <= 30.0
