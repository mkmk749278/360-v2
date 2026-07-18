"""Manual trade builder — dispatch_manual_trade gates + placement wiring.

Unit-tests the server-side dispatch entry point in isolation: the dark flag,
input validation, the can_assist tier gate, the (uid, ref_id) dup-guard,
MIN_NOTIONAL rejection, and that the happy path calls place_signal with the
user_owned / entry_type / pre-TP-off geometry. place_signal + sizing + the
store are patched at the boundary so no Binance/Firestore is touched.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

import config as _config
from src.api import user_overrides
from src.execution import dispatch_log
from src.execution import position_fsm
from src.execution import position_state
from src.execution import signal_dispatch
from src.execution import symbol_filters


@pytest.fixture
def env(monkeypatch):
    """Enabled + entitled + no-existing-position happy environment.

    Returns the place_signal AsyncMock so tests can set its return state.
    """
    monkeypatch.setattr(_config, "MANUAL_TRADE_BUILDER_ENABLED", True)
    monkeypatch.setattr(_config, "AUTO_TRADE_TIER_GATE_ENABLED", True)
    monkeypatch.setattr(signal_dispatch, "_resolve_user_tier", lambda uid: "assist")

    def _no_existing(*a, **k):
        raise position_state.PositionNotFoundError("none")
    monkeypatch.setattr(position_state, "get_position", _no_existing)
    monkeypatch.setattr(user_overrides, "resolve_notional_usd", lambda uid, d: 500.0)
    monkeypatch.setattr(
        signal_dispatch, "_compute_qty_split",
        lambda symbol, price, notional_usd=None: (0.01, 0.003, 0.004, 0.003),
    )
    monkeypatch.setattr(dispatch_log, "record_placed", MagicMock())
    monkeypatch.setattr(dispatch_log, "record_rejected", MagicMock())
    # TP-leg split calls symbol_filters.round_qty directly — passthrough so
    # tests don't need loaded Binance exchangeInfo.
    monkeypatch.setattr(symbol_filters, "round_qty", lambda symbol, qty: qty)

    place = AsyncMock(return_value=SimpleNamespace(
        state=position_state.PositionState.OPEN))
    monkeypatch.setattr(position_fsm, "place_signal", place)
    return place


def _call(**over):
    kw = dict(
        uid="uid", ref_id="alert-1", symbol="BTCUSDT", direction="LONG",
        entry_type="market", entry_price=29000.0, sl_price=28500.0,
        tp_prices=[29500.0], valid_for_minutes=0,
    )
    kw.update(over)
    return signal_dispatch.dispatch_manual_trade(**kw)


@pytest.mark.asyncio
async def test_disabled_flag_rejects(monkeypatch):
    monkeypatch.setattr(_config, "MANUAL_TRADE_BUILDER_ENABLED", False)
    r = await _call()
    assert r["outcome"] == "rejected"
    assert r["reject_class"] == "ManualTradeBuilderDisabled"


@pytest.mark.asyncio
async def test_bad_direction_rejected(env):
    r = await _call(direction="UP")
    assert r["reject_class"] == "BadRequest"


@pytest.mark.asyncio
async def test_bad_entry_type_rejected(env):
    r = await _call(entry_type="stop")
    assert r["reject_class"] == "BadRequest"


@pytest.mark.asyncio
async def test_tier_gate_blocks_free(env, monkeypatch):
    monkeypatch.setattr(signal_dispatch, "_resolve_user_tier", lambda uid: "free")
    r = await _call()
    assert r["reject_class"] == "TierNotEntitled"


@pytest.mark.asyncio
async def test_dup_guard_already_active(env, monkeypatch):
    active = SimpleNamespace(state=position_state.PositionState.OPEN)
    monkeypatch.setattr(position_state, "get_position", lambda uid, sid: active)
    r = await _call()
    assert r["reject_class"] == "AlreadyActive"


@pytest.mark.asyncio
async def test_notional_too_small_rejected(env, monkeypatch):
    monkeypatch.setattr(
        signal_dispatch, "_compute_qty_split",
        lambda symbol, price, notional_usd=None: (0.0, 0.0, 0.0, 0.0),
    )
    r = await _call()
    assert r["reject_class"] == "NotionalTooSmall"


@pytest.mark.asyncio
async def test_market_happy_path(env):
    r = await _call(entry_type="market")
    assert r["outcome"] == "placed"
    assert r["resting"] is False
    kw = env.call_args.kwargs
    assert kw["entry_type"] == "market"
    assert kw["protection_mode"] == "user_owned"
    assert kw["pretp_fraction"] == 0.0
    assert kw["invalidation_mode"] == "loose"


@pytest.mark.asyncio
async def test_limit_happy_path(env):
    env.return_value = SimpleNamespace(
        state=position_state.PositionState.PENDING_ENTRY)
    r = await _call(entry_type="limit", entry_price=28900.0, valid_for_minutes=15)
    assert r["outcome"] == "placed"
    assert r["resting"] is True
    kw = env.call_args.kwargs
    assert kw["entry_type"] == "limit"
    assert kw["valid_for_minutes"] == 15
    assert kw["protection_mode"] == "user_owned"


@pytest.mark.asyncio
async def test_entry_only_no_tp_passes_zero_tp_qty(env):
    r = await _call(sl_price=0.0, tp_prices=[])
    assert r["outcome"] == "placed"
    kw = env.call_args.kwargs
    assert kw["sl_price"] == 0.0
    assert kw["tp1_qty"] == 0.0 and kw["tp2_qty"] == 0.0 and kw["tp3_qty"] == 0.0
