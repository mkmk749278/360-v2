"""No engine path may leave a live position without its stop (2026-09-24).

Two paths did, and neither had fired only because nobody trades live yet:

1. **An engine close that failed.**  ``close_fsm_positions_for_signal`` /
   ``close_single_fsm_position`` cancelled the whole bracket FIRST, then sent
   the MARKET close, then marked the doc CLOSED "regardless of whether the
   MARKET order succeeded", trusting that "the reconciler will catch any
   remaining Binance state drift".  The reconciler walks NON-terminal docs
   only, so it never looked.  A close refused by Binance (or lost to a
   signing timeout) left a real position with no stop and no manager.

2. **An entry whose outcome was unknown.**  The doc was written only AFTER the
   entry REST call returned.  A timeout after Binance had accepted the order,
   or a fill event that outran the REST response, produced a position the FSM
   logged as "unknown" and dropped — so nothing laid its stop.

Each test below was checked against the pre-fix tree.
"""
from __future__ import annotations

import ast
import asyncio
import inspect
import pathlib
import textwrap
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution import order_placer
from src.execution import position_fsm
from src.execution import position_state
from src.execution import reconciler as reconciler_mod
from src.execution import signal_dispatch
from src.security.signing_service import protocol as sig_protocol

from tests.execution.test_position_fsm import (
    _otu,
    _placer_with_mock_results,
    _stub_placer_factory,
)

REPO = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _store(monkeypatch):
    """Dict-backed position store, the suite's convention (see
    ``test_orphan_protective_orders``): an assertion about the PERSISTED doc
    means what it says."""
    position_state.reset_for_test()
    for k in list(signal_dispatch._CLOSE_COUNTS):
        signal_dispatch._CLOSE_COUNTS[k] = 0
    docs: dict = {}
    writes: list = []

    def _put(p):
        docs[(p.firebase_uid, p.signal_id)] = p
        writes.append((p.state, p.entry_order_id, p.entry_ambiguous))

    def _get(uid, sid):
        try:
            return docs[(uid, sid)]
        except KeyError:
            raise position_state.PositionNotFoundError(f"{uid}/{sid}")

    monkeypatch.setattr(position_state, "put_position", _put)
    monkeypatch.setattr(position_state, "get_position", _get)
    monkeypatch.setattr(position_state, "is_initialised", lambda: True)
    yield {"docs": docs, "writes": writes}
    position_state.reset_for_test()


def _bracketed(**overrides) -> position_state.Position:
    kw = dict(
        signal_id="sig-1",
        firebase_uid="fb-x",
        symbol="BTCUSDT",
        side="LONG",
        state=position_state.PositionState.OPEN,
        entry_price_target=29000.0,
        entry_price_filled=29000.0,
        sl_price=28500.0,
        tp1_price=29500.0,
        tp2_price=30000.0,
        tp3_price=30500.0,
        total_qty=1.0,
        tp1_qty=0.3,
        tp2_qty=0.4,
        tp3_qty=0.3,
        entry_order_id=1000,
        sl_order_id=2000,
        tp1_order_id=3001,
        tp2_order_id=3002,
        tp3_order_id=3003,
        created_at=datetime.now(timezone.utc),
        last_event_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    kw.update(overrides)
    return position_state.Position(**kw)


def _rejected(code: int, status: int = 400) -> order_placer.OrderRejectedByBinance:
    resp = sig_protocol.SignResponse(
        id="rid", ok=False, binance_status=status,
        binance_body={"code": code, "msg": "x"},
        error_code=sig_protocol.ERR_BINANCE_HTTP_ERROR, error_message="x",
    )
    return order_placer.OrderRejectedByBinance("rejected", signing_response=resp)


def _order_of_calls(placer) -> list:
    """Method names in the order they were awaited."""
    return [c[0] for c in placer.mock_calls if c[0] in (
        "place_market_close", "cancel_algo_order",
    )]


# ---------------------------------------------------------------------------
# 1. The close helper
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_stop_comes_off_only_after_the_close_is_taken():
    _f, placer = _stub_placer_factory()
    pos = _bracketed()

    out = await signal_dispatch.close_position_keeping_stop(
        pos, placer, reason="invalidated", site="t",
    )

    assert out == signal_dispatch.CLOSE_CLOSED
    calls = _order_of_calls(placer)
    assert calls[0] == "place_market_close", calls
    assert set(calls[1:]) == {"cancel_algo_order"}
    assert pos.state is position_state.PositionState.CLOSED
    assert pos.close_reason == "invalidated"
    assert pos.sl_order_id == 0 and pos.tp1_order_id == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", [
    order_placer.OrderPlacementUnreachable("signing service down"),
    asyncio.TimeoutError(),
    "reject_-1003",
])
async def test_a_failed_close_keeps_the_stop_and_the_doc_live(failure, _store):
    """The defect itself: the stop must still be resting, the doc must still
    be live (so the reconciler — which walks live docs only — sees it), and
    the failure must be recorded as a pending close."""
    _f, placer = _stub_placer_factory()
    exc = _rejected(-1003, 429) if failure == "reject_-1003" else failure
    placer.place_market_close = AsyncMock(side_effect=exc)
    pos = _bracketed()

    out = await signal_dispatch.close_position_keeping_stop(
        pos, placer, reason="invalidated", site="t",
    )

    assert out == signal_dispatch.CLOSE_FAILED
    placer.cancel_algo_order.assert_not_called()
    assert pos.state is position_state.PositionState.OPEN
    assert not position_state.is_terminal(pos.state)
    assert pos.sl_order_id == 2000, "the stop must still be recorded as resting"
    assert pos.pending_close_reason == "invalidated"
    assert pos.pending_close_at is not None
    assert _store["docs"][("fb-x", "sig-1")] is pos
    assert signal_dispatch.close_counts()["failed"] == 1


@pytest.mark.asyncio
async def test_already_flat_is_a_close_and_retires_the_bracket():
    _f, placer = _stub_placer_factory()
    placer.place_market_close = AsyncMock(side_effect=_rejected(-2022))
    pos = _bracketed()

    out = await signal_dispatch.close_position_keeping_stop(
        pos, placer, reason="sl_hit", site="t",
    )

    assert out == signal_dispatch.CLOSE_ALREADY_FLAT
    assert pos.state is position_state.PositionState.CLOSED
    assert placer.cancel_algo_order.await_count == 4


@pytest.mark.asyncio
async def test_a_retry_keeps_the_first_failure_time():
    """The probe measures how long a position has been OWED a close."""
    _f, placer = _stub_placer_factory()
    placer.place_market_close = AsyncMock(
        side_effect=order_placer.OrderPlacementUnreachable("down")
    )
    first = datetime.now(timezone.utc) - timedelta(minutes=9)
    pos = _bracketed(pending_close_reason="expired", pending_close_at=first)

    await signal_dispatch.close_position_keeping_stop(
        pos, placer, reason="expired", site="t",
    )

    assert pos.pending_close_at == first


# ---------------------------------------------------------------------------
# 2. Both public close paths go through it
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_close_fsm_does_not_count_a_close_binance_refused(monkeypatch, _store):
    """The app's Close button renders this count.  "closed" over a position
    that is still open is the #988 class, inverted."""
    _f, placer = _stub_placer_factory()
    placer.place_market_close = AsyncMock(
        side_effect=order_placer.OrderPlacementUnreachable("down")
    )
    pos = _bracketed()
    position_state.put_position(pos)
    monkeypatch.setattr(order_placer, "OrderPlacer", lambda uid: placer)

    closed = await signal_dispatch.close_fsm_positions_for_signal(
        "sig-1", symbol="BTCUSDT", direction="LONG", reason="USER_CLOSE",
        only_uid="fb-x",
    )

    assert closed == 0
    assert pos.state is position_state.PositionState.OPEN
    placer.cancel_algo_order.assert_not_called()


@pytest.mark.asyncio
async def test_close_single_keeps_the_stop_on_failure(monkeypatch, _store):
    _f, placer = _stub_placer_factory()
    placer.place_market_close = AsyncMock(
        side_effect=order_placer.OrderPlacementUnreachable("down")
    )
    pos = _bracketed()
    position_state.put_position(pos)
    monkeypatch.setattr(order_placer, "OrderPlacer", lambda uid: placer)

    await signal_dispatch.close_single_fsm_position(
        "fb-x", "sig-1", symbol="BTCUSDT", direction="LONG", reason="inv_tight",
    )

    assert pos.state is position_state.PositionState.OPEN
    assert pos.sl_order_id == 2000
    placer.cancel_algo_order.assert_not_called()


def test_no_close_path_cancels_the_bracket_before_its_market_close():
    """Derived, so a close path added later is covered: in every function in
    ``src/`` that both cancels algo orders and sends a market close, no
    cancel may appear textually before the close.  A helper that does both in
    the right order (``close_position_keeping_stop``) is the only sanctioned
    shape; the FSM's post-fill sweep sends no close and is out of scope."""
    offenders = []
    for path in (REPO / "src").rglob("*.py"):
        tree = ast.parse(path.read_text())
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            first_cancel = first_close = None
            for node in ast.walk(fn):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    name = node.func.attr
                    line = node.lineno
                    if name in ("cancel_algo_order", "cancel_protective_orders"):
                        first_cancel = line if first_cancel is None else min(first_cancel, line)
                    if name in ("place_market_close", "place_funding_market_close"):
                        first_close = line if first_close is None else min(first_close, line)
            if first_cancel and first_close and first_cancel < first_close:
                offenders.append(f"{path.relative_to(REPO)}:{fn.name}")
    assert offenders == [], offenders


# ---------------------------------------------------------------------------
# 3. The reconciler retries, and re-protects a stop-less live position
# ---------------------------------------------------------------------------


def _reconciler(placer, positions=None) -> reconciler_mod.Reconciler:
    return reconciler_mod.Reconciler(
        signing_client_factory=lambda: MagicMock(),
        order_placer_factory=lambda uid: placer,
        positions_for_user=lambda uid: list(positions or []),
        max_position_age_sec=7200,
        stale_close_enabled=True,
    )


@pytest.mark.asyncio
async def test_a_pending_close_is_retried_and_keeps_the_engines_reason():
    _f, placer = _stub_placer_factory()
    pos = _bracketed(
        pending_close_reason="invalidated",
        pending_close_at=datetime.now(timezone.utc) - timedelta(minutes=2),
    )
    rec = _reconciler(placer, [pos])
    rec._fetch_binance_positions = AsyncMock(return_value={"BTCUSDT": 1.0})
    rec._fetch_open_algo_ids = AsyncMock(return_value={2000, 3001, 3002, 3003})

    await rec.reconcile_user("fb-x")

    placer.place_market_close.assert_awaited_once()
    assert pos.state is position_state.PositionState.CLOSED
    assert pos.close_reason == "invalidated"
    assert pos.pending_close_reason == ""


@pytest.mark.asyncio
async def test_a_pending_close_binance_already_flattened_keeps_the_reason():
    _f, placer = _stub_placer_factory()
    pos = _bracketed(pending_close_reason="expired")

    await _reconciler(placer)._diff_and_heal(pos, {"BTCUSDT": 0.0})

    assert pos.state is position_state.PositionState.CLOSED
    assert pos.close_reason == "expired"


@pytest.mark.asyncio
async def test_the_stale_close_keeps_the_stop_when_the_close_fails():
    _f, placer = _stub_placer_factory()
    placer.place_market_close = AsyncMock(
        side_effect=order_placer.OrderPlacementUnreachable("down")
    )
    pos = _bracketed(created_at=datetime.now(timezone.utc) - timedelta(hours=3))

    await _reconciler(placer)._maybe_force_close_stale(pos)

    placer.cancel_algo_order.assert_not_called()
    assert pos.state is position_state.PositionState.OPEN
    assert pos.pending_close_reason == "STALE_EXPIRY"


@pytest.mark.asyncio
async def test_a_live_position_with_no_stop_at_all_is_reprotected():
    """_heal_external_order_cancels only re-protects when a RECORDED stop
    vanishes; a position that never had one was never re-protected."""
    _f, placer = _stub_placer_factory()
    pos = _bracketed(sl_order_id=0, tp1_order_id=0, tp2_order_id=0, tp3_order_id=0)
    rec = _reconciler(placer)

    await rec._ensure_protected(pos, set())

    placer.place_stop_loss.assert_awaited_once()
    assert pos.sl_be_order_id == 4001
    assert rec.protection_counts["stopless_reprotected"] == 1


@pytest.mark.asyncio
async def test_an_unrecorded_resting_order_blocks_a_blind_second_stop():
    """An unrecorded closePosition stop would make a second one fail (-4130)
    and page a naked position that is not naked."""
    _f, placer = _stub_placer_factory()
    pos = _bracketed(sl_order_id=0, tp1_order_id=0, tp2_order_id=0, tp3_order_id=0)
    rec = _reconciler(placer)

    await rec._ensure_protected(pos, {777})

    placer.place_stop_loss.assert_not_called()
    assert rec.protection_counts["stopless_unrecorded_orders"] == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("override", [
    {"protection_mode": "user_owned"},
    {"last_event_at": datetime.now(timezone.utc)},
])
async def test_reprotection_respects_user_owned_and_in_flight(override):
    _f, placer = _stub_placer_factory()
    pos = _bracketed(sl_order_id=0, **override)
    await _reconciler(placer)._ensure_protected(pos, set())
    placer.place_stop_loss.assert_not_called()


@pytest.mark.asyncio
async def test_a_young_pending_doc_is_left_alone():
    """The doc is now written BEFORE the entry: a young PENDING row can be a
    placement still talking to Binance — flat because it has not filled yet.
    Healing it as a manual close would race the placement."""
    _f, placer = _stub_placer_factory()
    pos = _bracketed(
        state=position_state.PositionState.PENDING,
        sl_order_id=0, entry_order_id=0, filled_qty=0.0,
        last_event_at=datetime.now(timezone.utc),
    )
    rec = _reconciler(placer, [pos])
    rec._fetch_binance_positions = AsyncMock(return_value={"BTCUSDT": 0.0})
    rec._fetch_open_algo_ids = AsyncMock(return_value=set())

    await rec.reconcile_user("fb-x")

    assert pos.state is position_state.PositionState.PENDING
    placer.place_stop_loss.assert_not_called()


@pytest.mark.asyncio
async def test_a_quiet_pending_doc_live_on_binance_is_opened_and_protected():
    _f, placer = _stub_placer_factory()
    pos = _bracketed(
        state=position_state.PositionState.PENDING,
        sl_order_id=0, tp1_order_id=0, tp2_order_id=0, tp3_order_id=0,
        filled_qty=0.0, entry_price_filled=0.0, entry_ambiguous=True,
    )
    rec = _reconciler(placer, [pos])
    rec._fetch_binance_positions = AsyncMock(return_value={"BTCUSDT": 1.0})
    rec._fetch_open_algo_ids = AsyncMock(return_value=set())

    await rec.reconcile_user("fb-x")

    assert pos.state is position_state.PositionState.OPEN
    assert pos.filled_qty == 1.0
    placer.place_stop_loss.assert_awaited_once()


@pytest.mark.asyncio
async def test_an_ambiguous_entry_that_never_filled_retires_as_no_fill():
    _f, placer = _stub_placer_factory()
    pos = _bracketed(
        state=position_state.PositionState.PENDING,
        sl_order_id=0, tp1_order_id=0, tp2_order_id=0, tp3_order_id=0,
        filled_qty=0.0, entry_ambiguous=True,
    )

    await _reconciler(placer)._diff_and_heal(pos, {"BTCUSDT": 0.0})

    assert pos.state is position_state.PositionState.CANCELLED_NO_FILL
    assert pos.close_reason == "EXPIRED_NO_FILL"


# ---------------------------------------------------------------------------
# 4. Entry: doc first, and an unknown outcome is not a refusal
# ---------------------------------------------------------------------------


_ENTRY_KW = dict(
    firebase_uid="fb-x", signal_id="sig-1", symbol="BTCUSDT", direction="LONG",
    entry_price=29000.0, sl_price=28500.0, tp1_price=29500.0,
    tp2_price=30000.0, tp3_price=30500.0, total_qty=1.0, tp1_qty=0.3,
    tp2_qty=0.4, tp3_qty=0.3,
)


@pytest.mark.asyncio
async def test_the_doc_exists_before_the_entry_goes_out(_store):
    placer = _placer_with_mock_results()
    seen_at_entry: list = []

    async def _entry(**kw):
        seen_at_entry.append(("fb-x", "sig-1") in _store["docs"])
        return order_placer.OrderPlacementResult(
            order_id=1001, client_order_id="c", status="FILLED",
            avg_price=29010.0, binance_body={},
        )

    placer.place_market_entry = AsyncMock(side_effect=_entry)
    with patch.object(position_fsm, "_enforce_safety_gates"):
        pos = await position_fsm.place_signal(
            **_ENTRY_KW, order_placer_factory=lambda uid: placer,
        )
    assert seen_at_entry == [True]
    assert pos.entry_order_id == 1001


@pytest.mark.asyncio
@pytest.mark.parametrize("exc", [
    order_placer.OrderPlacementUnreachable("timeout"),
    asyncio.TimeoutError(),
    "reject_-1007",
    "reject_503",
])
async def test_an_entry_with_unknown_outcome_stays_live_and_flagged(exc, _store):
    placer = _placer_with_mock_results()
    err = {
        "reject_-1007": _rejected(-1007, 400),
        "reject_503": _rejected(-1000, 503),
    }.get(exc, exc) if isinstance(exc, str) else exc
    placer.place_market_entry = AsyncMock(side_effect=err)
    with patch.object(position_fsm, "_enforce_safety_gates"):
        with pytest.raises(BaseException):
            await position_fsm.place_signal(
                **_ENTRY_KW, order_placer_factory=lambda uid: placer,
            )
    doc = _store["docs"][("fb-x", "sig-1")]
    assert doc.state is position_state.PositionState.PENDING
    assert doc.entry_ambiguous is True
    placer.place_stop_loss.assert_not_called()


@pytest.mark.asyncio
async def test_an_entry_binance_refused_is_retired_not_left_live(_store):
    placer = _placer_with_mock_results()
    placer.place_market_entry = AsyncMock(side_effect=_rejected(-2019, 400))
    with patch.object(position_fsm, "_enforce_safety_gates"):
        with pytest.raises(order_placer.OrderRejectedByBinance):
            await position_fsm.place_signal(
                **_ENTRY_KW, order_placer_factory=lambda uid: placer,
            )
    doc = _store["docs"][("fb-x", "sig-1")]
    assert doc.state is position_state.PositionState.CANCELLED_NO_FILL
    assert doc.close_reason == "ENTRY_REJECTED"


@pytest.mark.asyncio
async def test_a_fill_on_an_ambiguous_entry_lays_the_stop():
    factory, placer = _stub_placer_factory()
    pos = _bracketed(
        state=position_state.PositionState.PENDING,
        sl_order_id=0, tp1_order_id=0, tp2_order_id=0, tp3_order_id=0,
        filled_qty=0.0, entry_price_filled=0.0, entry_ambiguous=True,
    )
    position_state.put_position(pos)
    fsm = position_fsm.PositionFSM("fb-x", order_placer_factory=factory)

    await fsm.handle_event(_otu(
        client_order_id=position_state.coid_entry("sig-1"),
        order_status="FILLED", last_filled_qty=1.0, cumulative_filled_qty=1.0,
        average_price=29000.0,
    ))

    assert pos.state is position_state.PositionState.OPEN
    placer.place_stop_loss.assert_awaited_once()


@pytest.mark.asyncio
async def test_a_fill_on_a_normal_entry_does_not_double_place_the_stop():
    """place_signal lays the stop for an entry it is still watching; the fill
    handler laying one too would be a duplicate closePosition (-4130)."""
    factory, placer = _stub_placer_factory()
    pos = _bracketed(
        state=position_state.PositionState.PENDING, sl_order_id=0,
        filled_qty=0.0, entry_ambiguous=False,
    )
    position_state.put_position(pos)
    fsm = position_fsm.PositionFSM("fb-x", order_placer_factory=factory)

    await fsm.handle_event(_otu(
        client_order_id=position_state.coid_entry("sig-1"),
        order_status="FILLED", last_filled_qty=1.0, cumulative_filled_qty=1.0,
        average_price=29000.0,
    ))

    placer.place_stop_loss.assert_not_called()


@pytest.mark.parametrize("exc,expected", [
    ("reject_-2019_400", True),
    ("reject_-1007_400", False),
    ("reject_-1000_503", False),
    ("unreachable", False),
    ("timeout", False),
    ("key_missing", True),
    ("internal", False),
])
def test_definitely_not_placed_is_only_true_on_proof(exc, expected):
    def _key(code):
        resp = sig_protocol.SignResponse.error_reply("r", code=code, message="x")
        return order_placer.OrderPlacementKeyError("k", signing_response=resp)

    e = {
        "reject_-2019_400": _rejected(-2019, 400),
        "reject_-1007_400": _rejected(-1007, 400),
        "reject_-1000_503": _rejected(-1000, 503),
        "unreachable": order_placer.OrderPlacementUnreachable("x"),
        "timeout": asyncio.TimeoutError(),
        "key_missing": _key(sig_protocol.ERR_KEY_BLOB_NOT_FOUND),
        "internal": _key(sig_protocol.ERR_INTERNAL_ERROR),
    }[exc]
    assert order_placer.definitely_not_placed(e) is expected


@pytest.mark.asyncio
async def test_a_signing_timeout_is_a_typed_placement_error():
    """A raw asyncio.TimeoutError escaped every ``except OrderPlacementError``,
    including the SL retry loop — a timed-out stop skipped the force-close."""
    client = MagicMock()
    client.binance_signed_post = AsyncMock(side_effect=asyncio.TimeoutError())
    placer = order_placer.OrderPlacer("fb-x", client=client)
    with pytest.raises(order_placer.OrderPlacementUnreachable):
        await placer.place_stop_loss(
            signal_id="sig-1", symbol="BTCUSDT", direction="LONG",
            stop_price=28500.0,
        )


# ---------------------------------------------------------------------------
# 5. Liveness probe, fan-out bound, signing-loop offload
# ---------------------------------------------------------------------------


def test_the_probe_pages_on_a_close_owed_too_long():
    old = _bracketed(
        pending_close_reason="expired",
        pending_close_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )
    ok, detail = signal_dispatch.pending_close_health([old])
    assert ok is False and "could not close" in detail
    young = _bracketed(
        pending_close_reason="expired",
        pending_close_at=datetime.now(timezone.utc),
    )
    assert signal_dispatch.pending_close_health([young])[0] is True
    assert signal_dispatch.pending_close_health([_bracketed()])[0] is True


def test_the_probe_is_registered():
    src = (REPO / "src" / "main.py").read_text()
    assert 'name="pending_close"' in src


def test_the_fanout_is_bounded():
    src = inspect.getsource(signal_dispatch.dispatch_signal_to_active_users)
    tree = ast.parse(textwrap.dedent(src))
    gathers = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "gather"
    ]
    assert gathers, "fan-out gather not found"
    text = ast.unparse(gathers[0])
    assert "_bounded(" in text and "_one_user(" not in text, text


def test_the_signing_handler_does_not_block_its_loop():
    """get_key_blob and kms.decrypt are blocking; called directly inside the
    async handler they serialised every concurrent signed call."""
    path = REPO / "src" / "security" / "signing_service" / "handler.py"
    tree = ast.parse(path.read_text())
    fn = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.AsyncFunctionDef) and n.name == "handle_request"
    )
    direct = []
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in ("get_key_blob", "decrypt"):
                direct.append(node.func.attr)
    assert direct == [], f"blocking call on the loop: {direct}"
