"""One signal, one exchange: the venue split between the two fan-outs.

* the Binance fan-out never places for a user who chose CoinDCX;
* the CoinDCX fan-out does nothing while its switch is off, honours the
  owner-only allow-list, and applies the same account gates as Binance;
* a manual take by a CoinDCX user is routed to CoinDCX, not Binance.
"""
from __future__ import annotations

from tests.venues.conftest import DCX

from unittest.mock import AsyncMock, patch

import pytest

from src.execution import signal_dispatch, symbol_filters
from src.venues.coindcx import dispatch as dcx
from src.venues.coindcx import execution as E


@pytest.fixture(autouse=True)
def _gates(monkeypatch):
    symbol_filters._set_cache_for_test({
        "BTCUSDT": symbol_filters.SymbolFilters(
            symbol="BTCUSDT", step_size=0.001, tick_size=0.1, min_qty=0.001, min_notional=5.0,
        ),
    })
    from src.api import user_overrides as _uo

    monkeypatch.setattr(_uo, "resolve_user_mode_uid_detailed", lambda uid: ("live", _uo.MODE_REASON_OK))
    monkeypatch.setattr(signal_dispatch, "_resolve_user_tier", lambda uid: "auto")
    monkeypatch.setattr(_uo, "is_user_auto_paused_uid", lambda uid: False)
    monkeypatch.setattr(_uo, "resolve_auto_trade_preferences_uid", lambda uid: (None, None))
    monkeypatch.setattr(_uo, "resolve_notional_usd", lambda uid, d: 100.0)
    venues = {"u_dcx": "coindcx", "u_bn": "binance"}
    monkeypatch.setattr(_uo, "resolve_venue_uid", lambda uid: venues.get(uid, "binance"))
    monkeypatch.setattr(_uo, "resolve_venue_settings_uid", lambda uid: {
        "venue": venues.get(uid, "binance"), "margin_currency": "INR", "leverage": 5.0,
        "reason": "ok"})
    from src.execution import position_fsm
    monkeypatch.setattr(position_fsm, "_enforce_safety_gates", lambda **kw: None)
    DCX["coindcx_execution_enabled"] = True
    DCX["coindcx_open_to_all"] = True  # the fan-out tests mean "every connected user"
    yield
    signal_dispatch.reset_cache_for_test()
    symbol_filters.reset_for_test()


_SIG = dict(signal_id="S", symbol="BTCUSDT", direction="LONG", entry_price=100.0,
            sl_price=98.0, tp1_price=103.0)


async def test_binance_fanout_skips_a_user_who_chose_coindcx() -> None:
    from src.execution import position_fsm

    with patch.object(signal_dispatch, "_active_uids", return_value=["u_dcx", "u_bn"]), \
         patch.object(position_fsm, "place_signal", new_callable=AsyncMock) as place:
        placed = await signal_dispatch.dispatch_signal_to_active_users(
            **_SIG, tp2_price=104.0, tp3_price=105.0,
        )
    assert placed == 1
    assert {c.kwargs["firebase_uid"] for c in place.await_args_list} == {"u_bn"}


async def test_coindcx_fanout_off_by_default_does_nothing(monkeypatch) -> None:
    DCX["coindcx_execution_enabled"] = False
    opened = AsyncMock()
    monkeypatch.setattr(E.get_executor(), "open_position", opened)
    out = await dcx.dispatch_signal(**_SIG)
    assert out["placed"] == 0 and opened.await_count == 0


async def test_coindcx_fanout_only_opens_for_coindcx_users(monkeypatch) -> None:
    from src.venues.coindcx import keystore
    monkeypatch.setattr(keystore, "list_active_uids", lambda: ["u_dcx", "u_bn"])
    opened = AsyncMock(return_value={"outcome": "placed", "qty": 1.0})
    monkeypatch.setattr(E.get_executor(), "open_position", opened)
    out = await dcx.dispatch_signal(**_SIG)
    assert out["placed"] == 1
    assert [c.kwargs["uid"] for c in opened.await_args_list] == ["u_dcx"]
    kw = opened.await_args_list[0].kwargs
    assert kw["margin_currency"] == "INR" and kw["notional_usdt"] == 100.0


async def test_allow_list_restricts_to_owner(monkeypatch) -> None:
    from src.venues.coindcx import keystore
    DCX["coindcx_open_to_all"] = False
    DCX["coindcx_execution_allowed_uids"] = "owner"
    monkeypatch.setattr(keystore, "list_active_uids", lambda: ["u_dcx"])
    opened = AsyncMock()
    monkeypatch.setattr(E.get_executor(), "open_position", opened)
    await dcx.dispatch_signal(**_SIG)
    assert opened.await_count == 0


async def test_an_empty_allow_list_means_nobody_not_everybody(monkeypatch) -> None:
    """Clearing the list must never open the venue: that is its own switch."""
    from src.venues.coindcx import keystore
    DCX["coindcx_open_to_all"] = False
    DCX["coindcx_execution_allowed_uids"] = ""
    monkeypatch.setattr(keystore, "list_active_uids", lambda: ["u_dcx"])
    opened = AsyncMock()
    monkeypatch.setattr(E.get_executor(), "open_position", opened)
    await dcx.dispatch_signal(**_SIG)
    assert opened.await_count == 0
    assert dcx._allowed_uids() == set()


async def test_open_to_all_ignores_the_allow_list(monkeypatch) -> None:
    DCX["coindcx_open_to_all"] = True
    DCX["coindcx_execution_allowed_uids"] = "owner"
    assert dcx._allowed_uids() is None


def test_the_gate_reads_the_live_tunables_not_config(monkeypatch) -> None:
    """A config patch must not move the gate — the live value is the tunable."""
    import config
    monkeypatch.setattr(config, "COINDCX_EXECUTION_ENABLED", True)
    DCX["coindcx_execution_enabled"] = False
    assert dcx.execution_enabled() is False
    DCX["coindcx_execution_enabled"] = True
    assert dcx.execution_enabled() is True


def test_the_three_switches_are_registered_tunables() -> None:
    from src import runtime_tunables as _rt
    reg = _rt.registry()
    assert reg["coindcx_execution_enabled"].type == "bool"
    assert reg["coindcx_execution_enabled"].default is False
    assert reg["coindcx_open_to_all"].type == "bool"
    assert reg["coindcx_open_to_all"].default is False
    assert reg["coindcx_execution_allowed_uids"].type == "str"
    assert {reg[k].category for k in ("coindcx_execution_enabled", "coindcx_open_to_all",
                                      "coindcx_execution_allowed_uids")} == {"CoinDCX"}


async def test_unreadable_roster_dispatches_to_nobody(monkeypatch) -> None:
    from src.venues.coindcx import keystore
    monkeypatch.setattr(keystore, "list_active_uids", lambda: None)
    opened = AsyncMock()
    monkeypatch.setattr(E.get_executor(), "open_position", opened)
    out = await dcx.dispatch_signal(**_SIG)
    assert out["placed"] == 0 and opened.await_count == 0


async def test_same_account_gates_as_binance(monkeypatch) -> None:
    from src.api import user_overrides as _uo
    from src.venues.coindcx import keystore
    monkeypatch.setattr(keystore, "list_active_uids", lambda: ["u_dcx"])
    opened = AsyncMock(return_value={"outcome": "placed"})
    monkeypatch.setattr(E.get_executor(), "open_position", opened)

    monkeypatch.setattr(_uo, "resolve_user_mode_uid_detailed", lambda uid: ("paper", _uo.MODE_REASON_OK))
    await dcx.dispatch_signal(**_SIG)
    monkeypatch.setattr(_uo, "resolve_user_mode_uid_detailed", lambda uid: ("live", _uo.MODE_REASON_OK))
    monkeypatch.setattr(signal_dispatch, "_resolve_user_tier", lambda uid: "assist")
    await dcx.dispatch_signal(**_SIG)
    monkeypatch.setattr(signal_dispatch, "_resolve_user_tier", lambda uid: "auto")
    monkeypatch.setattr(_uo, "is_user_auto_paused_uid", lambda uid: True)
    await dcx.dispatch_signal(**_SIG)
    monkeypatch.setattr(_uo, "is_user_auto_paused_uid", lambda uid: False)
    monkeypatch.setattr(_uo, "resolve_auto_trade_preferences_uid", lambda uid: (frozenset({"OTHER"}), None))
    await dcx.dispatch_signal(**_SIG, setup_class="MOVER_TREND_PULLBACK")
    assert opened.await_count == 0

    from src.execution import position_fsm

    def _kill(**kw):
        raise RuntimeError("global kill switch engaged")
    monkeypatch.setattr(_uo, "resolve_auto_trade_preferences_uid", lambda uid: (None, None))
    monkeypatch.setattr(position_fsm, "_enforce_safety_gates", _kill)
    out = await dcx.dispatch_signal(**_SIG)
    assert opened.await_count == 0
    assert out["outcomes"]["u_dcx"]["reject_class"] == "RuntimeError"


async def test_manual_take_by_coindcx_user_routes_to_coindcx(monkeypatch) -> None:
    from src.execution import position_fsm
    opened = AsyncMock(return_value={"outcome": "placed", "qty": 0.5})
    monkeypatch.setattr(E.get_executor(), "open_position", opened)
    with patch.object(position_fsm, "place_signal", new_callable=AsyncMock) as place:
        result = await signal_dispatch.dispatch_signal_to_uid_manual(
            uid="u_dcx", **_SIG, tp2_price=104.0, tp3_price=105.0,
        )
    assert place.await_count == 0 and opened.await_count == 1
    assert result["outcome"] == "placed" and result["venue"] == "coindcx"


def test_gate_list_is_documented_in_the_order_it_runs() -> None:
    """The module docstring is the contract the owner reads; keep it true."""
    import inspect
    src = inspect.getsource(dcx._one_user)
    order = [src.index(t) for t in (
        "resolve_venue_settings_uid", "resolve_user_mode_uid_detailed", "_resolve_user_tier",
        "is_user_auto_paused_uid", "resolve_auto_trade_preferences_uid",
        "resolve_notional_usd", "_enforce_safety_gates", "open_position",
    )]
    assert order == sorted(order)
