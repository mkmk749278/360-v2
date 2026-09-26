"""The order-path safety chain, driven through ``place_signal``.

``_enforce_safety_gates`` is the single function standing between a
dispatched signal and a real Binance order. Every gate in it had unit tests
of its own — the kill-switch client reads ``engaged``, the breakers trip at
their thresholds, the rate limiter counts — and only two of the seven were
ever driven through the function that actually places orders (the symbol
allowlist and "globally disabled"). A gate that is correct in isolation and
not wired into the chain, or wired AFTER the entry order, passes every one
of those unit tests. This file is the seam test (2026-09-26 audit).

Every case asserts two things, and the second is the one that matters:

* the refusal is the TYPED exception for that gate — so a case cannot pass
  because some other gate happened to fire first;
* nothing reached the exchange: the order-placer factory was never called,
  and no position document was written.

``test_every_gate_open_places_the_order`` is the control. Without it, a
harness that refused everything (a mis-set allowlist, a stale singleton)
would make every refusal case pass while proving nothing.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Callable, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src import fail_open
from src.execution import kill_switch
from src.execution import order_placer
from src.execution import position_fsm
from src.execution import position_state
from src.execution import tripwires

UID = "fb-chain"
SYMBOL = "BTCUSDT"


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------


class _FakeKillSwitch:
    """Duck-types the three reads ``_enforce_safety_gates`` makes."""

    def __init__(
        self,
        *,
        enabled: bool = True,
        engaged: bool = False,
        disabled_uids: frozenset = frozenset(),
    ) -> None:
        self.enabled = enabled
        self.engaged = engaged
        self.disabled_uids = disabled_uids

    def is_globally_enabled(self) -> bool:
        return self.enabled

    def is_global_engaged(self) -> bool:
        return self.engaged

    def is_user_disabled(self, firebase_uid: str) -> bool:
        return firebase_uid in self.disabled_uids


def _result(order_id: int, suffix: str) -> order_placer.OrderPlacementResult:
    return order_placer.OrderPlacementResult(
        order_id=order_id, client_order_id=f"lumin_sig-chain_{suffix}",
        status="NEW", avg_price=0.0, binance_body={},
    )


def _placer() -> MagicMock:
    placer = MagicMock()
    placer.ensure_cross_margin = AsyncMock(return_value=True)
    placer.place_market_entry = AsyncMock(return_value=_result(1001, "entry"))
    placer.place_stop_loss = AsyncMock(return_value=_result(2001, "sl"))
    placer.place_take_profit = AsyncMock(
        side_effect=[_result(3001, "tp1"), _result(3002, "tp2"), _result(3003, "tp3")]
    )
    placer.place_pretp_limit = AsyncMock(return_value=_result(4001, "pretp"))
    placer.place_market_close = AsyncMock(return_value=_result(9001, "close"))
    return placer


class _Recorder:
    """Order-placer factory that records whether it was ever asked."""

    def __init__(self) -> None:
        self.calls: list[str] = []
        self.placer = _placer()

    def __call__(self, uid: str) -> MagicMock:
        self.calls.append(uid)
        return self.placer


def _kwargs(factory: _Recorder, signal_id: str = "sig-chain") -> dict:
    return dict(
        signal_id=signal_id,
        symbol=SYMBOL,
        direction="LONG",
        entry_price=29000.0,
        sl_price=28500.0,
        tp1_price=29500.0,
        tp2_price=30000.0,
        tp3_price=30500.0,
        total_qty=1.0,
        tp1_qty=0.3,
        tp2_qty=0.4,
        tp3_qty=0.3,
        order_placer_factory=factory,
    )


def _install_pref(symbol_preference: Optional[list], *, raises: Optional[Exception] = None):
    from src.api import user_overrides as _uo
    from src.api import users as _users

    user_store = MagicMock()
    user_store.get_by_firebase_uid = MagicMock(return_value=SimpleNamespace(user_id=7))
    _users.set_singleton(user_store)
    overrides = MagicMock()
    if raises is not None:
        overrides.get_auto_trade = MagicMock(side_effect=raises)
    else:
        row = {} if symbol_preference is None else {"symbol_preference": symbol_preference}
        overrides.get_auto_trade = MagicMock(return_value=row)
    _uo.set_singleton(overrides)


def _clear_pref() -> None:
    from src.api import user_overrides as _uo
    from src.api import users as _users

    _uo.clear_singleton()
    _users.set_singleton(None)  # type: ignore[arg-type]


@pytest.fixture(autouse=True)
def _chain_state(monkeypatch: pytest.MonkeyPatch):
    """Every gate OPEN by default; each test arms exactly one."""
    monkeypatch.setenv("TRIPWIRE_SYMBOL_ALLOWLIST", "BTCUSDT,ETHUSDT")
    monkeypatch.delenv("TRIPWIRE_USER_PREF_FAIL_CLOSED", raising=False)
    monkeypatch.delenv("FIREBASE_PROJECT_ID", raising=False)
    position_state.reset_for_test()
    tripwires.reset_singletons_for_test()
    kill_switch.reset_for_test()
    fail_open.reset()
    _clear_pref()
    kill_switch._client = _FakeKillSwitch()
    yield
    kill_switch.reset_for_test()
    tripwires.reset_singletons_for_test()
    position_state.reset_for_test()
    fail_open.reset()
    _clear_pref()


async def _place(factory: _Recorder, signal_id: str = "sig-chain"):
    return await position_fsm.place_signal(UID, **_kwargs(factory, signal_id))


def _assert_nothing_reached_the_exchange(factory: _Recorder, put: MagicMock) -> None:
    assert factory.calls == [], "the order placer was built for a refused order"
    factory.placer.place_market_entry.assert_not_called()
    factory.placer.place_stop_loss.assert_not_called()
    factory.placer.place_take_profit.assert_not_called()
    factory.placer.place_pretp_limit.assert_not_called()
    put.assert_not_called()


# ---------------------------------------------------------------------------
# The control
# ---------------------------------------------------------------------------


async def test_every_gate_open_places_the_order() -> None:
    factory = _Recorder()
    with patch.object(position_state, "put_position") as put:
        result = await _place(factory)
    assert result.entry_order_id == 1001
    assert factory.calls == [UID]
    factory.placer.place_market_entry.assert_awaited_once()
    assert put.called


# ---------------------------------------------------------------------------
# One gate at a time
# ---------------------------------------------------------------------------


def _arm_kill_switch_engaged(mp: pytest.MonkeyPatch) -> None:
    kill_switch._client = _FakeKillSwitch(engaged=True)


def _arm_globally_disabled(mp: pytest.MonkeyPatch) -> None:
    kill_switch._client = _FakeKillSwitch(enabled=False)


def _arm_user_disabled(mp: pytest.MonkeyPatch) -> None:
    kill_switch._client = _FakeKillSwitch(disabled_uids=frozenset({UID}))


def _arm_symbol_off_allowlist(mp: pytest.MonkeyPatch) -> None:
    mp.setenv("TRIPWIRE_SYMBOL_ALLOWLIST", "ETHUSDT")


def _arm_user_symbol_preference(mp: pytest.MonkeyPatch) -> None:
    _install_pref(["ETHUSDT"])


def _arm_per_user_breaker(mp: pytest.MonkeyPatch) -> None:
    tripwires._per_user_breaker = tripwires.PerUserCircuitBreaker(threshold=1)
    with patch.object(tripwires, "_spawn_alert"):
        assert tripwires._per_user_breaker.record_rejection(UID) is True


def _arm_global_breaker(mp: pytest.MonkeyPatch) -> None:
    tripwires._global_breaker = tripwires.GlobalCircuitBreaker(threshold=1)
    with patch.object(tripwires, "_spawn_alert"):
        assert tripwires._global_breaker.record_rejection() is True


def _arm_rate_limit(mp: pytest.MonkeyPatch) -> None:
    tripwires._rate_limiter = tripwires.RateLimiter(per_min=1, per_hour=10)
    tripwires._rate_limiter.check_and_record(UID)  # budget spent


GATES: list[tuple[str, Callable[[pytest.MonkeyPatch], None], type]] = [
    ("kill_switch_engaged", _arm_kill_switch_engaged, tripwires.GlobalKillSwitchEngaged),
    ("globally_disabled", _arm_globally_disabled, position_fsm.NotGloballyEnabledError),
    ("user_auto_disabled", _arm_user_disabled, tripwires.UserAutoDisabled),
    ("symbol_off_allowlist", _arm_symbol_off_allowlist, tripwires.SymbolNotAllowed),
    ("user_symbol_preference", _arm_user_symbol_preference, tripwires.SymbolNotInUserPreference),
    ("per_user_breaker", _arm_per_user_breaker, tripwires.UserAutoDisabled),
    ("global_breaker", _arm_global_breaker, tripwires.GlobalKillSwitchEngaged),
    ("rate_limit", _arm_rate_limit, tripwires.RateLimitExceeded),
]


@pytest.mark.parametrize(
    "name,arm,expected", GATES, ids=[g[0] for g in GATES],
)
async def test_each_gate_refuses_before_any_order_is_placed(
    name, arm, expected, monkeypatch,
) -> None:
    arm(monkeypatch)
    factory = _Recorder()
    with patch.object(position_state, "put_position") as put:
        with pytest.raises(expected):
            await _place(factory)
    _assert_nothing_reached_the_exchange(factory, put)


async def test_gate_list_covers_every_check_the_chain_makes() -> None:
    """If a gate is added to ``_enforce_safety_gates`` this file must learn it.

    Counted on the function's own calls, not on a comment: every tripwire
    helper it invokes, plus the three kill-switch reads, must have a case.
    """
    import ast
    import inspect

    src = inspect.getsource(position_fsm._enforce_safety_gates)
    called = {
        node.func.attr
        for node in ast.walk(ast.parse(src.lstrip()))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    known = {
        "is_initialised",  # the production fail-closed branch, tested below
        "is_globally_enabled", "is_global_engaged", "is_user_disabled",
        "assert_symbol_allowed", "assert_symbol_in_user_preference",
        "check", "check_and_record",
    }
    gate_calls = {c for c in called if c.startswith(("is_", "assert_", "check"))}
    assert gate_calls <= known, (
        f"_enforce_safety_gates gained {sorted(gate_calls - known)} — add a case to GATES"
    )


# ---------------------------------------------------------------------------
# Production fail-closed branch
# ---------------------------------------------------------------------------


async def test_firebase_configured_but_kill_switch_missing_refuses(monkeypatch) -> None:
    """A bootstrap partial failure must not let orders through with no
    global oversight. Only the dev/test path (no FIREBASE_PROJECT_ID) may
    skip the Firestore-backed gates."""
    kill_switch.reset_for_test()
    monkeypatch.setenv("FIREBASE_PROJECT_ID", "lumin-app")
    factory = _Recorder()
    with patch.object(position_state, "put_position") as put:
        with pytest.raises(position_fsm.NotGloballyEnabledError, match="not initialised"):
            await _place(factory)
    _assert_nothing_reached_the_exchange(factory, put)


# ---------------------------------------------------------------------------
# Ordering: the rate limit is charged only after every other gate passed
# ---------------------------------------------------------------------------


async def test_a_refused_order_does_not_spend_the_rate_limit() -> None:
    tripwires._rate_limiter = tripwires.RateLimiter(per_min=1, per_hour=10)

    kill_switch._client = _FakeKillSwitch(engaged=True)
    with patch.object(position_state, "put_position"):
        with pytest.raises(tripwires.GlobalKillSwitchEngaged):
            await _place(_Recorder(), "sig-a")

    # Disengaged: the one-per-minute budget must still be whole.
    kill_switch._client = _FakeKillSwitch()
    factory = _Recorder()
    with patch.object(position_state, "put_position"):
        result = await _place(factory, "sig-b")
    assert result.entry_order_id == 1001

    # …and now it is spent.
    with patch.object(position_state, "put_position"):
        with pytest.raises(tripwires.RateLimitExceeded):
            await _place(_Recorder(), "sig-c")


# ---------------------------------------------------------------------------
# An unreadable preference is counted, and refused only when switched on
# ---------------------------------------------------------------------------


def _unreadable_count() -> int:
    return int(fail_open.snapshot().get(
        tripwires.USER_PREF_UNREADABLE_SITE, {},
    ).get("count", 0))


async def test_an_unreadable_preference_is_counted_and_allowed_by_default() -> None:
    import sqlite3

    _install_pref(None, raises=sqlite3.OperationalError("database is locked"))
    factory = _Recorder()
    with patch.object(position_state, "put_position"):
        result = await _place(factory)
    assert result.entry_order_id == 1001
    assert _unreadable_count() == 1


async def test_an_unreadable_preference_refuses_when_fail_closed(monkeypatch) -> None:
    import sqlite3

    monkeypatch.setenv("TRIPWIRE_USER_PREF_FAIL_CLOSED", "true")
    _install_pref(None, raises=sqlite3.OperationalError("database is locked"))
    factory = _Recorder()
    with patch.object(position_state, "put_position") as put:
        with pytest.raises(tripwires.SymbolNotInUserPreference, match="could not be read"):
            await _place(factory)
    _assert_nothing_reached_the_exchange(factory, put)
    assert _unreadable_count() == 1


async def test_no_preference_is_not_a_failure() -> None:
    """A NULL row is the default "all symbols" case, not a read failure."""
    _install_pref(None)
    with patch.object(position_state, "put_position"):
        await _place(_Recorder())
    assert _unreadable_count() == 0
