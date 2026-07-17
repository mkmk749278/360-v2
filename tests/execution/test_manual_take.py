"""Tests for the server-side manual take (owner-approved 2026-07-17).

What we pin:

* ``dispatch_signal_to_uid_manual`` dispatches to exactly the one uid and
  SKIPS the unattended-consent gates (mode, auto-pause, path/regime
  preferences) — the user's tap is the consent those gates encode.
* The tier gate applies at ``can_assist`` (assist tier may take; free may
  not) instead of ``can_auto``.
* The ``(uid, signal_id)`` dup guard: a non-terminal existing position
  refuses the take (no second MARKET entry, ever); a terminal one allows a
  re-take; a store error fails CLOSED.
* The result dict carries the terminal outcome (placed fields / reject
  fields) so the API can answer the user's request synchronously.
* dispatch_log records carry ``source="manual_take"``.
* ``CryptoSignalEngine.take_signal_for_user``: flag gate, unknown signal,
  terminal-status signal, and the happy-path handoff to dispatch.
* ``ManualTakeConsumer``: envelope processing, stale refusal, malformed
  drop, result write.
"""
from __future__ import annotations

import json
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution import position_state, signal_dispatch, symbol_filters


@pytest.fixture(autouse=True)
def _reset_cache(monkeypatch):
    signal_dispatch.reset_cache_for_test()
    symbol_filters._set_cache_for_test({
        "BTCUSDT": symbol_filters.SymbolFilters(
            symbol="BTCUSDT",
            step_size=0.001,
            tick_size=0.10,
            min_qty=0.001,
            min_notional=5.0,
        ),
    })
    # Default stubs mirror tests/execution/test_signal_dispatch.py: the
    # manual path must place even when these would block the auto path,
    # so the interesting tests override them to *blocking* values.
    from src.api import user_overrides as _uo
    monkeypatch.setattr(_uo, "resolve_user_mode_uid", lambda uid: "live")
    monkeypatch.setattr(signal_dispatch, "_resolve_user_tier", lambda uid: "auto")
    # No pre-existing position unless a test installs one.
    monkeypatch.setattr(
        position_state, "get_position",
        MagicMock(side_effect=position_state.PositionNotFoundError("none")),
    )
    yield
    signal_dispatch.reset_cache_for_test()
    symbol_filters.reset_for_test()


def _geometry(**overrides):
    base = dict(
        signal_id="sig-M1",
        symbol="BTCUSDT",
        direction="LONG",
        entry_price=29000.0,
        sl_price=28500.0,
        tp1_price=29500.0,
        tp2_price=30000.0,
        tp3_price=30500.0,
    )
    base.update(overrides)
    return base


async def _manual_take(uid="fb-M", **overrides):
    return await signal_dispatch.dispatch_signal_to_uid_manual(
        uid=uid, **_geometry(**overrides),
    )


# ---------------------------------------------------------------------------
# Gate semantics
# ---------------------------------------------------------------------------


async def test_manual_take_places_for_the_one_uid_only() -> None:
    """The roster is bypassed — exactly one uid, even when _active_uids
    would return others."""
    with patch.object(
        signal_dispatch, "_active_uids", return_value=["fb-A", "fb-B"]
    ) as mock_roster:
        from src.execution import position_fsm
        with patch.object(
            position_fsm, "place_signal", new_callable=AsyncMock
        ) as mock_place:
            result = await _manual_take(uid="fb-M")
    assert result["outcome"] == "placed"
    assert mock_place.await_count == 1
    assert mock_place.await_args.kwargs["firebase_uid"] == "fb-M"
    mock_roster.assert_not_called()


async def test_manual_take_skips_mode_gate(monkeypatch) -> None:
    """A user in mode='off' (assist users typically are) can still take —
    the tap IS the consent the mode gate encodes for unattended orders."""
    from src.api import user_overrides as _uo
    monkeypatch.setattr(_uo, "resolve_user_mode_uid", lambda uid: "off")
    from src.execution import position_fsm
    with patch.object(
        position_fsm, "place_signal", new_callable=AsyncMock
    ):
        result = await _manual_take()
    assert result["outcome"] == "placed"


async def test_auto_path_still_blocked_by_mode_gate(monkeypatch) -> None:
    """Regression pin: the same mode='off' user is still skipped by the
    unattended fan-out — the manual bypass must not leak into auto."""
    from src.api import user_overrides as _uo
    monkeypatch.setattr(_uo, "resolve_user_mode_uid", lambda uid: "off")
    with patch.object(
        signal_dispatch, "_active_uids", return_value=["fb-A"]
    ):
        from src.execution import position_fsm
        with patch.object(
            position_fsm, "place_signal", new_callable=AsyncMock
        ) as mock_place:
            placed = await signal_dispatch.dispatch_signal_to_active_users(
                **_geometry(),
            )
    assert placed == 0
    mock_place.assert_not_called()


async def test_manual_take_skips_auto_pause_gate(monkeypatch) -> None:
    from src.api import user_overrides as _uo
    monkeypatch.setattr(_uo, "is_user_auto_paused_uid", lambda uid: True)
    from src.execution import position_fsm
    with patch.object(
        position_fsm, "place_signal", new_callable=AsyncMock
    ):
        result = await _manual_take()
    assert result["outcome"] == "placed"


async def test_manual_take_skips_path_and_regime_preferences(monkeypatch) -> None:
    """Even a block-all (empty set) preference doesn't stop an explicit
    take — preferences filter *unattended* dispatch only."""
    from src.api import user_overrides as _uo
    monkeypatch.setattr(
        _uo, "resolve_auto_trade_preferences_uid",
        lambda uid: (frozenset(), frozenset()),
    )
    from src.execution import position_fsm
    with patch.object(
        position_fsm, "place_signal", new_callable=AsyncMock
    ):
        result = await _manual_take(setup_class="SR_FLIP_RETEST")
    assert result["outcome"] == "placed"


async def test_manual_take_tier_gate_allows_assist(monkeypatch) -> None:
    monkeypatch.setattr(signal_dispatch, "_resolve_user_tier", lambda uid: "assist")
    from src.execution import position_fsm
    with patch.object(
        position_fsm, "place_signal", new_callable=AsyncMock
    ):
        result = await _manual_take()
    assert result["outcome"] == "placed"


async def test_manual_take_tier_gate_rejects_free(monkeypatch) -> None:
    monkeypatch.setattr(signal_dispatch, "_resolve_user_tier", lambda uid: "free")
    from src.execution import position_fsm
    with patch.object(
        position_fsm, "place_signal", new_callable=AsyncMock
    ) as mock_place:
        result = await _manual_take()
    assert result["outcome"] == "rejected"
    assert result["reject_class"] == "TierNotEntitled"
    mock_place.assert_not_called()


# ---------------------------------------------------------------------------
# Dup guard
# ---------------------------------------------------------------------------


async def test_manual_take_refuses_when_position_already_active(monkeypatch) -> None:
    existing = SimpleNamespace(state=position_state.PositionState.OPEN)
    monkeypatch.setattr(
        position_state, "get_position", MagicMock(return_value=existing),
    )
    from src.execution import position_fsm
    with patch.object(
        position_fsm, "place_signal", new_callable=AsyncMock
    ) as mock_place:
        result = await _manual_take()
    assert result["outcome"] == "rejected"
    assert result["reject_class"] == "AlreadyActive"
    mock_place.assert_not_called()


async def test_manual_take_allows_retake_after_terminal_position(monkeypatch) -> None:
    terminal_state = next(
        s for s in position_state.PositionState if position_state.is_terminal(s)
    )
    existing = SimpleNamespace(state=terminal_state)
    monkeypatch.setattr(
        position_state, "get_position", MagicMock(return_value=existing),
    )
    from src.execution import position_fsm
    with patch.object(
        position_fsm, "place_signal", new_callable=AsyncMock
    ):
        result = await _manual_take()
    assert result["outcome"] == "placed"


async def test_manual_take_fails_closed_on_dup_guard_error(monkeypatch) -> None:
    """A store error must refuse the take (double real entry is the worse
    failure mode), not fall through to placement."""
    monkeypatch.setattr(
        position_state, "get_position",
        MagicMock(side_effect=RuntimeError("firestore down")),
    )
    from src.execution import position_fsm
    with patch.object(
        position_fsm, "place_signal", new_callable=AsyncMock
    ) as mock_place:
        result = await _manual_take()
    assert result["outcome"] == "rejected"
    assert result["reject_class"] == "DupGuardUnavailable"
    mock_place.assert_not_called()


# ---------------------------------------------------------------------------
# Result capture + dispatch_log source
# ---------------------------------------------------------------------------


async def test_manual_take_placed_result_carries_fill_fields() -> None:
    from src.execution import position_fsm
    with patch.object(
        position_fsm, "place_signal", new_callable=AsyncMock
    ):
        result = await _manual_take()
    assert result["outcome"] == "placed"
    assert result["symbol"] == "BTCUSDT"
    assert result["direction"] == "LONG"
    assert result["total_qty"] > 0
    assert result["signal_id"] == "sig-M1"


async def test_manual_take_rejection_result_carries_reject_fields() -> None:
    from src.execution import position_fsm

    class _FakeReject(Exception):
        pass

    with patch.object(
        position_fsm, "place_signal",
        new_callable=AsyncMock, side_effect=_FakeReject("kill switch engaged"),
    ):
        result = await _manual_take()
    assert result["outcome"] == "rejected"
    assert result["reject_class"] == "_FakeReject"
    assert "kill switch" in result["reject_detail"]


async def test_manual_take_records_dispatch_log_with_manual_source() -> None:
    from src.execution import dispatch_log, position_fsm
    with patch.object(
        position_fsm, "place_signal", new_callable=AsyncMock
    ):
        with patch.object(dispatch_log, "record_placed") as mock_record:
            result = await _manual_take()
    assert result["outcome"] == "placed"
    assert mock_record.call_args.kwargs["source"] == "manual_take"


async def test_auto_path_records_dispatch_log_with_auto_source() -> None:
    from src.execution import dispatch_log, position_fsm
    with patch.object(
        signal_dispatch, "_active_uids", return_value=["fb-A"]
    ):
        with patch.object(
            position_fsm, "place_signal", new_callable=AsyncMock
        ):
            with patch.object(dispatch_log, "record_placed") as mock_record:
                await signal_dispatch.dispatch_signal_to_active_users(
                    **_geometry(),
                )
    assert mock_record.call_args.kwargs["source"] == "auto"


# ---------------------------------------------------------------------------
# CryptoSignalEngine.take_signal_for_user (called unbound with a stub self —
# the method touches only self.router)
# ---------------------------------------------------------------------------


def _engine_stub(active_signals: dict):
    return SimpleNamespace(
        router=SimpleNamespace(active_signals=active_signals),
    )


def _live_signal(signal_id="sig-M1", status="ACTIVE"):
    return SimpleNamespace(
        signal_id=signal_id,
        symbol="BTCUSDT",
        direction=SimpleNamespace(value="LONG"),
        entry=29000.0,
        stop_loss=28500.0,
        tp1=29500.0,
        tp2=30000.0,
        tp3=30500.0,
        status=status,
        entry_regime="RANGING",
        entry_regime_15m="RANGING",
        atr_percentile_at_entry=50.0,
        atr_value_at_entry=100.0,
        setup_class="SR_FLIP_RETEST",
    )


async def _engine_take(engine_stub, uid="fb-M", signal_id="sig-M1"):
    from src.main import CryptoSignalEngine
    return await CryptoSignalEngine.take_signal_for_user(
        engine_stub, uid, signal_id,
    )


async def test_engine_take_rejects_when_flag_off(monkeypatch) -> None:
    import config as _config
    monkeypatch.setattr(_config, "AUTO_TRADE_MANUAL_TAKE_ENABLED", False)
    result = await _engine_take(_engine_stub({"sig-M1": _live_signal()}))
    assert result["outcome"] == "rejected"
    assert result["reject_class"] == "ManualTakeDisabled"


async def test_engine_take_rejects_unknown_signal(monkeypatch) -> None:
    import config as _config
    monkeypatch.setattr(_config, "AUTO_TRADE_MANUAL_TAKE_ENABLED", True)
    result = await _engine_take(_engine_stub({}))
    assert result["outcome"] == "rejected"
    assert result["reject_class"] == "SignalNotFound"


async def test_engine_take_rejects_terminal_signal(monkeypatch) -> None:
    import config as _config
    monkeypatch.setattr(_config, "AUTO_TRADE_MANUAL_TAKE_ENABLED", True)
    result = await _engine_take(
        _engine_stub({"sig-M1": _live_signal(status="SL_HIT")}),
    )
    assert result["outcome"] == "rejected"
    assert result["reject_class"] == "SignalClosed"


async def test_engine_take_hands_geometry_to_manual_dispatch(monkeypatch) -> None:
    import config as _config
    monkeypatch.setattr(_config, "AUTO_TRADE_MANUAL_TAKE_ENABLED", True)
    captured = {}

    async def _fake_manual(**kwargs):
        captured.update(kwargs)
        return {"outcome": "placed", "signal_id": kwargs["signal_id"]}

    monkeypatch.setattr(
        signal_dispatch, "dispatch_signal_to_uid_manual", _fake_manual,
    )
    result = await _engine_take(_engine_stub({"sig-M1": _live_signal()}))
    assert result["outcome"] == "placed"
    assert captured["uid"] == "fb-M"
    assert captured["symbol"] == "BTCUSDT"
    assert captured["direction"] == "LONG"
    assert captured["entry_price"] == 29000.0
    assert captured["sl_price"] == 28500.0


# ---------------------------------------------------------------------------
# ManualTakeConsumer
# ---------------------------------------------------------------------------


class _FakeRedisForConsumer:
    def __init__(self) -> None:
        self.available = True
        self.client = self
        self.written: dict = {}

    async def set(self, key, value, ex=None):
        self.written[key] = value


def _envelope(request_id="req-1", uid="fb-M", signal_id="sig-M1", ts=None):
    return json.dumps({
        "request_id": request_id,
        "uid": uid,
        "signal_id": signal_id,
        "ts": time.time() if ts is None else ts,
    })


async def test_consumer_processes_envelope_and_writes_result() -> None:
    from src.api import snapshot_store as _store
    from src.execution.manual_take import ManualTakeConsumer

    engine = SimpleNamespace(
        take_signal_for_user=AsyncMock(
            return_value={"outcome": "placed", "signal_id": "sig-M1"},
        ),
    )
    redis = _FakeRedisForConsumer()
    consumer = ManualTakeConsumer(engine, redis)
    await consumer._process(_envelope())
    engine.take_signal_for_user.assert_awaited_once_with("fb-M", "sig-M1")
    written = json.loads(redis.written[_store.KEY_TAKE_RESULT_PREFIX + "req-1"])
    assert written["outcome"] == "placed"


async def test_consumer_rejects_stale_envelope_without_placing() -> None:
    from src.api import snapshot_store as _store
    from src.execution.manual_take import ManualTakeConsumer

    engine = SimpleNamespace(take_signal_for_user=AsyncMock())
    redis = _FakeRedisForConsumer()
    consumer = ManualTakeConsumer(engine, redis)
    await consumer._process(
        _envelope(ts=time.time() - _store.TAKE_CMD_STALE_S - 5),
    )
    engine.take_signal_for_user.assert_not_awaited()
    written = json.loads(redis.written[_store.KEY_TAKE_RESULT_PREFIX + "req-1"])
    assert written["reject_class"] == "TakeRequestStale"


async def test_consumer_drops_malformed_envelope_silently() -> None:
    from src.execution.manual_take import ManualTakeConsumer

    engine = SimpleNamespace(take_signal_for_user=AsyncMock())
    redis = _FakeRedisForConsumer()
    consumer = ManualTakeConsumer(engine, redis)
    await consumer._process("{not json")
    await consumer._process(json.dumps({"request_id": "x"}))  # incomplete
    engine.take_signal_for_user.assert_not_awaited()
    assert redis.written == {}


async def test_consumer_answers_even_when_take_crashes() -> None:
    from src.api import snapshot_store as _store
    from src.execution.manual_take import ManualTakeConsumer

    engine = SimpleNamespace(
        take_signal_for_user=AsyncMock(side_effect=RuntimeError("boom")),
    )
    redis = _FakeRedisForConsumer()
    consumer = ManualTakeConsumer(engine, redis)
    await consumer._process(_envelope())
    written = json.loads(redis.written[_store.KEY_TAKE_RESULT_PREFIX + "req-1"])
    assert written["outcome"] == "rejected"
    assert written["reject_class"] == "RuntimeError"
