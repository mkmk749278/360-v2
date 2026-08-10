"""Live trail governor — the half that spends money.

Most of these are ordinary behaviour tests.  Four are guards against defect
shapes this repo has already paid for, and they are marked as such, because a
future reader deleting one should know what it was protecting:

* the **serializer round trip** (#842 — a field one writer sets and the
  serializer drops is invisible at both ends);
* the **dead-parameter** check (``build_channel_signal``'s ``candle_highs`` —
  a parameter no caller passes, under a docstring saying every caller does);
* the **never-naked ordering**, which is the whole safety argument of the
  module and is a property of the call *order*, not of the retry working;
* the **coid round trip**, since the trail id is the first non-deterministic
  one in the scheme and a mis-parse would silently orphan a real fill.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Any, Dict, List

import pytest

from src import trail_mechanisms
from src.execution import position_state as ps
from src.execution import trail_governor as tg


# --------------------------------------------------------------------------- #
# Fakes — driven from the real producers wherever a shape is being asserted
# --------------------------------------------------------------------------- #


class FakePlacer:
    """Records the ORDER of placements and cancels — that ordering is the
    safety property, so a fake that only counted calls would pass while the
    module went naked on every bar."""

    def __init__(self, fail_place: bool = False, fail_cancel: bool = False) -> None:
        self.calls: List[str] = []
        self.placed: List[Dict[str, Any]] = []
        self.cancelled: List[int] = []
        self.fail_place = fail_place
        self.fail_cancel = fail_cancel
        self._next_id = 1000

    async def place_stop_loss(self, **kw: Any) -> Any:
        if self.fail_place:
            from src.execution.order_placer import OrderPlacementError

            self.calls.append("place_FAIL")
            raise OrderPlacementError("simulated placement failure")
        self._next_id += 1
        self.calls.append(f"place:{self._next_id}")
        self.placed.append(kw)

        class _R:
            order_id = self._next_id

        r = _R()
        r.order_id = self._next_id
        return r

    async def cancel_algo_order(self, *, symbol: str, algo_id: int) -> None:
        if self.fail_cancel:
            from src.execution.order_placer import OrderPlacementError

            self.calls.append(f"cancel_FAIL:{algo_id}")
            raise OrderPlacementError("simulated cancel failure")
        self.calls.append(f"cancel:{algo_id}")
        self.cancelled.append(algo_id)


class FakeStore:
    def __init__(self, candles: Dict[str, Any]) -> None:
        self._c = candles

    def get_candles(self, symbol: str, timeframe: str) -> Any:
        return self._c


def _rising_series(n: int = 60, start_ms: float = 1_700_000_000_000.0,
                   width_ms: float = 900_000.0) -> Dict[str, List[float]]:
    """A clean uptrend — SAR comes onside for a LONG and ratchets up."""
    highs, lows, closes, times = [], [], [], []
    for i in range(n):
        base = 100.0 + i * 0.5
        highs.append(base + 0.4)
        lows.append(base - 0.4)
        closes.append(base)
        times.append(start_ms + i * width_ms)
    return {"high": highs, "low": lows, "open": list(closes),
            "close": closes, "open_time": times}


def _pos(**over: Any) -> ps.Position:
    kw: Dict[str, Any] = dict(
        signal_id="SIG1", firebase_uid="UID1", symbol="BTCUSDT", side="LONG",
        state=ps.PositionState.OPEN, entry_price_target=100.0,
        entry_price_filled=100.0, sl_price=97.0, tp1_price=103.0,
        tp2_price=106.0, tp3_price=110.0, total_qty=1.0, tp1_qty=0.3,
        tp2_qty=0.3, tp3_qty=0.4, sl_order_id=501, tp1_order_id=601,
        tp2_order_id=602, tp3_order_id=603, exit_mechanism="sar",
    )
    kw.update(over)
    return ps.Position(**kw)


def _now_for(series: Dict[str, List[float]], width_s: float = 900.0) -> float:
    """A clock one bar after the newest closed bar — i.e. genuinely current."""
    return (series["open_time"][-1] / 1000.0) + width_s


@pytest.fixture(autouse=True)
def _clean():
    tg.reset_health_for_test()
    tg.reset_state_for_test()
    yield
    tg.reset_health_for_test()
    tg.reset_state_for_test()


@pytest.fixture(autouse=True)
def _no_persist(monkeypatch):
    """The governor persists through put_position, which needs Firestore."""
    monkeypatch.setattr(ps, "put_position", lambda position: None)


# --------------------------------------------------------------------------- #
# The safety property: never naked
# --------------------------------------------------------------------------- #


async def test_handover_places_before_it_cancels_anything():
    """GUARD (the module's whole safety argument).

    BE-shift cancels then places and accepts a naked window once.  This
    governor re-parks every bar, so it must invert that ordering.  Asserted on
    the call SEQUENCE: a test counting calls would pass on the unsafe order.
    """
    series = _rising_series()
    pos = _pos()
    placer = FakePlacer()
    out = await tg.step_position(
        pos, FakeStore(series), timeframe="15m",
        placer_factory=lambda uid: placer, now_ts=_now_for(series),
    )
    assert out == "handover"
    assert placer.calls, "nothing happened at all"
    assert placer.calls[0].startswith("place:"), (
        f"first call must be the placement, got {placer.calls}"
    )
    # ...and the evaluator's whole ladder comes down after it, not before.
    assert set(placer.cancelled) == {501, 601, 602, 603}
    assert placer.calls.index("place:1001") < min(
        placer.calls.index(f"cancel:{i}") for i in (501, 601, 602, 603)
    )


async def test_placement_failure_leaves_the_old_protection_untouched():
    """A failed park must give nothing up — no cancel, no state change."""
    series = _rising_series()
    pos = _pos()
    placer = FakePlacer(fail_place=True)
    out = await tg.step_position(
        pos, FakeStore(series), timeframe="15m",
        placer_factory=lambda uid: placer, now_ts=_now_for(series),
    )
    assert out == "place_failed"
    assert placer.cancelled == [], "cancelled something after failing to place"
    assert pos.sl_order_id == 501, "original stop was dropped"
    assert pos.trail_governing is False
    assert pos.trail_stop_order_id == 0
    assert tg.health()["place_failed"] == 1


async def test_cancel_failure_leaves_two_stops_and_is_counted():
    """Over-protected is the safe direction, but it must not be silent."""
    series = _rising_series()
    pos = _pos()
    placer = FakePlacer(fail_cancel=True)
    out = await tg.step_position(
        pos, FakeStore(series), timeframe="15m",
        placer_factory=lambda uid: placer, now_ts=_now_for(series),
    )
    assert out == "handover"
    assert pos.trail_stop_order_id != 0, "new stop must still be live"
    assert tg.health()["orphan_cancel"] == 4
    # The superseded ids are NOT zeroed when their cancel failed — the next
    # sweep must still know they are out there.
    assert pos.sl_order_id == 501


# --------------------------------------------------------------------------- #
# When it must do nothing, and which nothing it is
# --------------------------------------------------------------------------- #


async def test_does_not_hand_over_while_the_mechanism_is_offside():
    """Before handover the evaluator's SL/TP govern, untouched."""
    series = _rising_series()
    # A LONG into a falling series: SAR sits above price, i.e. opposed.
    series["high"] = list(reversed(series["high"]))
    series["low"] = list(reversed(series["low"]))
    series["close"] = list(reversed(series["close"]))
    pos = _pos()
    placer = FakePlacer()
    out = await tg.step_position(
        pos, FakeStore(series), timeframe="15m",
        placer_factory=lambda uid: placer, now_ts=_now_for(series),
    )
    assert out == tg.REFUSE_NOT_ONSIDE
    assert placer.calls == []
    assert pos.sl_order_id == 501 and pos.trail_governing is False


async def test_refuses_a_stale_series_rather_than_parking_off_an_old_bar():
    """#836 with money behind it — a stop off an hours-old bar is a stop
    nobody computed for this market."""
    series = _rising_series()
    pos = _pos()
    placer = FakePlacer()
    stale_now = _now_for(series) + (900.0 * 20)  # 20 bars late
    out = await tg.step_position(
        pos, FakeStore(series), timeframe="15m",
        placer_factory=lambda uid: placer, now_ts=stale_now,
    )
    assert out == tg.REFUSE_STALE
    assert placer.calls == []
    assert tg.health()["refusals"][tg.REFUSE_STALE] == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("pretp_fired", True),
        ("be_shift_fired", True),
        ("closed_qty", 0.3),
        ("sl_be_order_id", 777),
        ("trail_order_id", 888),
    ],
)
async def test_declines_a_position_whose_ladder_was_already_touched(field, value):
    """The measured mechanism runs from entry.  Adopting a half-managed
    position measures neither it nor the FSM."""
    pos = _pos(**{field: value})
    placer = FakePlacer()
    out = await tg.step_position(
        pos, FakeStore(_rising_series()), timeframe="15m",
        placer_factory=lambda uid: placer, now_ts=_now_for(_rising_series()),
    )
    assert out == tg.REFUSE_LADDER
    assert placer.calls == []


async def test_same_bar_is_idempotent():
    """The monitor loop runs many times per bar; the governor acts once."""
    series = _rising_series()
    pos = _pos()
    placer = FakePlacer()
    now = _now_for(series)
    first = await tg.step_position(
        pos, FakeStore(series), timeframe="15m",
        placer_factory=lambda uid: placer, now_ts=now)
    second = await tg.step_position(
        pos, FakeStore(series), timeframe="15m",
        placer_factory=lambda uid: placer, now_ts=now)
    assert first == "handover"
    assert second == "same_bar"
    assert len(placer.placed) == 1


async def test_a_position_with_no_mechanism_is_never_touched():
    pos = _pos(exit_mechanism="")
    placer = FakePlacer()
    out = await tg.step_position(
        pos, FakeStore(_rising_series()), timeframe="15m",
        placer_factory=lambda uid: placer, now_ts=_now_for(_rising_series()))
    assert out == "not_governed"
    assert placer.calls == []


# --------------------------------------------------------------------------- #
# The ratchet
# --------------------------------------------------------------------------- #


def test_tightens_never_allows_a_widening_or_an_equal_move():
    assert tg.tightens("LONG", 95.0, 96.0) is True
    assert tg.tightens("LONG", 95.0, 94.0) is False
    assert tg.tightens("LONG", 95.0, 95.0) is False, "equal must not spend an order"
    assert tg.tightens("SHORT", 105.0, 104.0) is True
    assert tg.tightens("SHORT", 105.0, 106.0) is False
    assert tg.tightens("SHORT", 105.0, 105.0) is False
    assert tg.tightens("LONG", 0.0, 94.0) is True, "first park has nothing to beat"


async def test_after_handover_the_stop_only_ever_tightens():
    """Risk after handover is monotonically non-increasing, whatever the
    mechanism does.  The handover itself may widen — that is the uncapped
    decision — but nothing after it."""
    series = _rising_series()
    pos = _pos()
    placer = FakePlacer()
    await tg.step_position(pos, FakeStore(series), timeframe="15m",
                           placer_factory=lambda uid: placer,
                           now_ts=_now_for(series))
    parked = pos.trail_stop_price
    assert pos.trail_governing is True

    # Feed a bar that would pull the level DOWN for a long: refuse to move.
    pos.trail_stop_price = parked + 5.0   # pretend we are already tighter
    series2 = _rising_series(n=61)
    out = await tg.step_position(pos, FakeStore(series2), timeframe="15m",
                                 placer_factory=lambda uid: placer,
                                 now_ts=_now_for(series2))
    assert out == "unchanged"
    assert len(placer.placed) == 1, "spent an order to widen the stop"
    assert tg.health()["unchanged"] == 1


# --------------------------------------------------------------------------- #
# Seam guards
# --------------------------------------------------------------------------- #


def test_position_trail_fields_survive_the_real_serializer():
    """GUARD #842 — ``open_time`` was added to the candle store and dropped by
    ``_save_snapshot_sync``, and nothing was missing while the process lived.
    Drives the real serializer both ways rather than asserting a dict shape."""
    pos = _pos(
        exit_mechanism="chandelier", trail_governing=True,
        trail_stop_order_id=4242, trail_stop_price=98.7654,
        trail_stop_seq=17, trail_last_bar_ms=1_700_000_900_000.0,
    )
    back = ps._from_firestore_dict(ps._to_firestore_dict(pos))
    for field in (
        "exit_mechanism", "trail_governing", "trail_stop_order_id",
        "trail_stop_price", "trail_stop_seq", "trail_last_bar_ms",
    ):
        assert getattr(back, field) == getattr(pos, field), (
            f"{field} did not survive the Firestore round trip"
        )


def test_a_pre_upgrade_document_reads_back_as_ungoverned():
    """A doc written before this shipped must keep the exit it was placed
    with — every default fails toward the unchanged FSM exit."""
    old = ps._to_firestore_dict(_pos())
    for k in list(old):
        if k.startswith("trail_") or k == "exit_mechanism":
            del old[k]
    back = ps._from_firestore_dict(old)
    assert back.exit_mechanism == ""
    assert back.trail_governing is False
    assert back.trail_stop_order_id == 0
    assert tg.ladder_untouched(back) is True


def test_trail_coid_round_trips_and_no_existing_phase_regresses():
    """GUARD — the trail id is the first non-deterministic coid in the scheme.
    A mis-parse would leave a real fill unrecognised by the FSM."""
    for seq in (0, 1, 9, 42, 9999):
        c = ps.coid_trail("SIG-ABC123", seq)
        assert len(c) <= 36, f"{c} exceeds Binance's clientOrderId limit"
        assert ps.parse_coid(c) == ("SIG-ABC123", "trail")
    # The pre-existing phases must be untouched by the new branch.
    for builder, phase in (
        (ps.coid_sl, "sl"), (ps.coid_sl_be, "sl_be"), (ps.coid_entry, "entry"),
        (ps.coid_close, "close"), (ps.coid_funding_close, "funding_close"),
        (ps.coid_tp1, "tp1"), (ps.coid_tp2, "tp2"), (ps.coid_tp3, "tp3"),
        (ps.coid_pretp, "pretp"),
    ):
        assert ps.parse_coid(builder("SIG-ABC123")) == ("SIG-ABC123", phase)
    assert ps.parse_coid("someone-elses-order") is None


def test_the_fsm_dispatches_the_trail_phase():
    """GUARD — ``parse_coid`` emitting a phase the FSM does not handle would
    fall through to the 'unrecognised phase' warning and the fill would be
    dropped on the floor."""
    from src.execution import position_fsm

    src = Path(inspect.getfile(position_fsm)).read_text()
    assert 'phase == "trail"' in src, "FSM does not dispatch the trail phase"
    assert "_apply_trail_fill" in src
    # ...and it must not be booked as an ordinary stop-out.
    assert '"TRAIL_STOP"' in src


def test_exit_mechanism_is_actually_passed_by_the_dispatcher():
    """GUARD (the ``candle_highs`` defect) — a parameter one function reads and
    no caller writes is dead code under a docstring claiming otherwise.  Parses
    the real call site rather than grepping the import."""
    from src.execution import signal_dispatch

    tree = ast.parse(Path(inspect.getfile(signal_dispatch)).read_text())
    passed = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = getattr(func, "attr", getattr(func, "id", ""))
        if name != "place_signal":
            continue
        if any(kw.arg == "exit_mechanism" for kw in node.keywords):
            passed = True
    assert passed, (
        "signal_dispatch never passes exit_mechanism to place_signal — the "
        "per-user column would be stored and never consumed (a scaffold)"
    )


def test_governable_mirrors_the_mechanism_registry():
    """The fix for a drifting mirror is not a second mirror."""
    assert tg.GOVERNABLE == frozenset(trail_mechanisms.MECHANISMS)


def test_governor_defaults_are_off():
    """Both switches must default to the unchanged exit."""
    from config import TRAIL_GOVERNOR_ENABLED

    assert TRAIL_GOVERNOR_ENABLED is False
    from src import runtime_tunables as rt

    assert rt.registry()["trail_governor_enabled"].default is False


async def test_sweep_is_inert_while_disabled(monkeypatch):
    monkeypatch.setattr(
        "src.runtime_tunables.get",
        lambda key: False if key == "trail_governor_enabled" else "15m",
    )
    out = await tg.sweep(FakeStore(_rising_series()))
    assert out["enabled"] is False
    assert tg.health()["refusals"][tg.REFUSE_DISABLED] == 1


async def test_sweep_refuses_a_cold_index_rather_than_reading_it_as_empty(monkeypatch):
    """A cold index means 'cannot answer'.  Reading it as 'no open positions'
    is how a governor silently stops governing and looks healthy."""
    monkeypatch.setattr(
        "src.runtime_tunables.get",
        lambda key: True if key == "trail_governor_enabled" else "15m",
    )
    monkeypatch.setattr(ps, "index_open_positions", lambda: None)
    out = await tg.sweep(FakeStore(_rising_series()))
    assert out.get("index_cold") is True
    assert tg.health()["refusals"][tg.REFUSE_INDEX_COLD] == 1


# --------------------------------------------------------------------------- #
# The process seam — caught on the deploy that shipped it
# --------------------------------------------------------------------------- #


def test_build_diag_reports_a_cold_index_rather_than_an_empty_book(monkeypatch):
    """`index_cold` and "nothing governed" must stay distinguishable."""
    monkeypatch.setattr(ps, "index_open_positions", lambda: None)
    out = tg.build_diag()
    assert out["index_cold"] is True
    assert out["open_total"] is None
    assert out["rows"] == []


def test_build_diag_carries_its_cause_on_failure(monkeypatch):
    def _boom():
        raise RuntimeError("index exploded")

    monkeypatch.setattr(ps, "index_open_positions", _boom)
    out = tg.build_diag()
    assert "index exploded" in out["error"]


def test_the_diag_is_published_from_the_engine_container():
    """GUARD — the defect this test exists for shipped to production.

    The governor's counters and the open-position index are in-process state
    of the ENGINE container. The first cut of `/internal/diag/trail-governor`
    built the payload locally, so in isolated mode (live on the VPS) it
    reported `index_cold` forever while the governor ran perfectly in the
    other container: the panel described the API process.

    Both sibling diags already carried the publish-then-read pattern. This
    derives the requirement from the tree rather than restating it:
    the writer must publish it, the facade must expose it, and the handler
    must consult the facade before building anything locally.
    """
    from src.api import redis_engine, server, snapshot_store, snapshot_writer

    writer_src = Path(inspect.getfile(snapshot_writer)).read_text()
    assert "_write_trail_governor" in writer_src
    # Defining a method is not calling it — pin the call site.
    assert "await self._write_trail_governor()" in writer_src, (
        "the writer defines the publisher but the cycle never calls it"
    )

    assert hasattr(snapshot_store, "KEY_TRAIL_GOVERNOR")
    assert hasattr(redis_engine.RedisEngineFacade, "published_trail_governor")

    facade_src = Path(inspect.getfile(redis_engine)).read_text()
    assert "KEY_TRAIL_GOVERNOR" in facade_src, (
        "the facade exposes the accessor but never refreshes it from Redis"
    )

    server_src = Path(inspect.getfile(server)).read_text()
    handler = server_src[server_src.index("async def trail_governor_diag"):]
    handler = handler[: handler.index("@app.get")]
    assert "published_trail_governor" in handler, (
        "the handler builds the payload locally without consulting the "
        "published snapshot — it will report index_cold in isolated mode"
    )
    assert handler.index("published_trail_governor") < handler.index(
        "build_diag"
    ), "the local build must be the FALLBACK, not the first choice"
