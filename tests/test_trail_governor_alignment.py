"""The governor must execute the mechanism ``sar_live_shadow`` measures.

Owner, 2026-08-11: *"make SAR live and Binance autotrade exactly same"* — after
finding a position closed on Binance while ``/signals/sar-live`` still showed it
running, and a reduce-only stop resting on a position that had closed half an
hour earlier.

Every test here pins one axis on which the measurement lane and the live
executor had silently diverged.  All of them **fail against the pre-fix tree**,
which is the only thing that makes them guards rather than descriptions:

* ``decide`` had no exit branch, so a flipped SAR was sent as a stop the
  exchange can only answer with -2021;
* the governor's stop rested on ``MARK_PRICE`` while the arm scores kline lows;
* ``trail_stop_order_id`` was in neither close path's cancel list nor the
  reconciler's protection set — a sixth protective order added to a
  hand-written five-name tuple;
* the signal's own SL closed a position whose SL the handover had cancelled;
* nothing anywhere recorded what a governed exit actually filled at.
"""
from __future__ import annotations

import inspect
from dataclasses import fields as dataclass_fields
from typing import Any, Dict, List

import pytest

from src import trail_history as th
from src import trail_mechanisms
from src.execution import order_placer as op
from src.execution import position_state as ps
from src.execution import reconciler as rec
from src.execution import signal_dispatch as sd
from src.execution import trail_governor as tg


# --------------------------------------------------------------------------- #
# Fakes
# --------------------------------------------------------------------------- #


class FakePlacer:
    """Records order AND payload — the defects here lived in the request body
    and in the call sequence, neither of which a call-count fake can see."""

    def __init__(
        self,
        *,
        fail_close: bool = False,
        close_code: int | None = None,
        fail_cancel: bool = False,
        avg_price: float = 0.0,
    ) -> None:
        self.calls: List[str] = []
        self.placed: List[Dict[str, Any]] = []
        self.closed: List[Dict[str, Any]] = []
        self.cancelled: List[int] = []
        self.fail_close = fail_close
        self.close_code = close_code
        self.fail_cancel = fail_cancel
        self.avg_price = avg_price
        self._next_id = 2000

    async def place_stop_loss(self, **kw: Any) -> Any:
        self._next_id += 1
        self.calls.append(f"place:{self._next_id}")
        self.placed.append(kw)

        class _R:
            order_id = self._next_id

        r = _R()
        r.order_id = self._next_id
        return r

    async def place_market_close(self, **kw: Any) -> Any:
        self.calls.append("market_close")
        self.closed.append(kw)
        if self.fail_close:
            raise _rejection(self.close_code)

        class _R:
            pass

        r = _R()
        r.avg_price = self.avg_price
        r.order_id = 9999
        return r

    async def cancel_algo_order(self, *, symbol: str, algo_id: int) -> None:
        if self.fail_cancel:
            self.calls.append(f"cancel_FAIL:{algo_id}")
            raise op.OrderPlacementError("simulated cancel failure")
        self.calls.append(f"cancel:{algo_id}")
        self.cancelled.append(algo_id)


def _rejection(code: int | None) -> Exception:
    """A rejection shaped like the real one, so ``_binance_code`` reads it the
    way it reads production rather than the way this file imagines it."""
    if code is None:
        return op.OrderPlacementError("signing service unreachable")

    class _Resp:
        binance_body = {"code": code, "msg": "simulated"}

    exc = op.OrderRejectedByBinance(f"Binance returned 400 (code={code})")
    exc.signing_response = _Resp()
    return exc


def _series(
    n: int = 60,
    start_ms: float = 1_700_000_000_000.0,
    width_ms: float = 900_000.0,
    *,
    falling_from: int | None = None,
) -> Dict[str, List[float]]:
    """A clean uptrend, optionally rolling over — which is what takes SAR
    offside for a LONG and is therefore the mechanism's exit condition."""
    highs, lows, closes, times = [], [], [], []
    for i in range(n):
        if falling_from is not None and i >= falling_from:
            base = 100.0 + falling_from * 0.5 - (i - falling_from) * 1.5
        else:
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
        tp2_qty=0.3, tp3_qty=0.4, exit_mechanism="sar",
    )
    kw.update(over)
    return ps.Position(**kw)


def _now_for(series: Dict[str, List[float]], width_s: float = 900.0) -> float:
    return (series["open_time"][-1] / 1000.0) + width_s


@pytest.fixture(autouse=True)
def _clean():
    tg.reset_health_for_test()
    tg.reset_state_for_test()
    # `record_outcome` writes through to the persisted record, so the ledger is
    # swapped for an in-memory one. Without this the suite would both leak rows
    # between tests AND write `data/trail_exits_v1.json` into the repo — the
    # stray-.tmp defect that ran for two months, arriving at a new ledger.
    th.reset_ledger(th.TrailExitLedger(path=""))
    yield
    tg.reset_health_for_test()
    tg.reset_state_for_test()
    th.reset_ledger(None)


@pytest.fixture(autouse=True)
def _no_persist(monkeypatch):
    monkeypatch.setattr(ps, "put_position", lambda position: None)


# --------------------------------------------------------------------------- #
# 1. The trigger series — mark price vs the candles the arm scores
# --------------------------------------------------------------------------- #


def test_governor_parks_on_the_series_the_arm_scores():
    """GUARD. The arm decides a touch with ``lo <= parked`` on kline lows; a
    stop resting on MARK_PRICE fires on a series it never looks at."""
    assert tg.GOVERNOR_WORKING_TYPE == "CONTRACT_PRICE"


def test_every_other_caller_keeps_mark_price():
    """The alignment is for the governor ALONE.  MARK_PRICE is the right
    default for an SL nobody is measuring against a candle, and silently
    moving the FSM's stop onto the wick series would be a money-path change
    nobody asked for."""
    sig = inspect.signature(op.OrderPlacer.place_stop_loss)
    assert sig.parameters["working_type"].default == "MARK_PRICE"


async def test_park_sends_the_governor_working_type():
    """GUARD — the defect lived entirely in the request body, which is exactly
    what a mock whose keys you chose cannot catch.  Asserted on the kwarg the
    real placer receives."""
    placer = FakePlacer()
    pos = _pos(sl_order_id=501, tp1_order_id=601)
    ok = await tg._park(pos, 98.5, placer=placer, handover=True)
    assert ok
    assert placer.placed[0]["working_type"] == "CONTRACT_PRICE"
    assert placer.placed[0]["quantity"] == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# 2. The exit leg — a flipped level is an instruction to be out
# --------------------------------------------------------------------------- #


def test_offside_after_handover_decides_exit_not_a_stop():
    """GUARD (fails pre-fix: ``decide`` returned the flipped level).

    Post-flip SAR sits on the far side of price by construction, so for a LONG
    it is trivially "tighter" than the parked stop and sailed through
    ``tightens`` — straight into -2021 "Order would immediately trigger", which
    is what the owner's rejection ring showed on INXUSDT seq 10.
    """
    series = _series(falling_from=40)
    pos = _pos(trail_governing=True, trail_stop_price=95.0)
    level, decision = tg.decide(
        pos, series, mechanism="sar",
        params=trail_mechanisms.default_params("sar"),
        state={}, timeframe="15m", now_ts=_now_for(series),
    )
    assert decision == tg.DECIDE_EXIT
    assert level is None


def test_onside_after_handover_still_parks():
    """The exit branch must not swallow the ordinary ratchet."""
    series = _series()
    pos = _pos(trail_governing=True, trail_stop_price=90.0)
    level, decision = tg.decide(
        pos, series, mechanism="sar",
        params=trail_mechanisms.default_params("sar"),
        state={}, timeframe="15m", now_ts=_now_for(series),
    )
    assert decision == "replace"
    assert level is not None and level > 90.0


def test_offside_before_handover_is_still_not_onside():
    """Pre-handover the evaluator's SL governs and there is nothing to exit —
    ``not_onside`` and ``exit`` are different states with different next moves,
    and pooling them would close trades the mechanism never adopted."""
    series = _series(falling_from=40)
    pos = _pos(trail_governing=False)
    level, decision = tg.decide(
        pos, series, mechanism="sar",
        params=trail_mechanisms.default_params("sar"),
        state={}, timeframe="15m", now_ts=_now_for(series),
    )
    assert decision == tg.REFUSE_NOT_ONSIDE
    assert level is None


async def test_exit_closes_at_market_then_retires_the_stop():
    """Ordering is the safety property here too, inverted from ``_park``:
    protection is being retired WITH the position, and the close is reduceOnly,
    so closing first means no naked window while the cancel lands."""
    placer = FakePlacer(avg_price=94.0)
    pos = _pos(trail_governing=True, trail_stop_price=95.0,
               trail_stop_order_id=777)
    ok = await tg._exit_at_market(pos, placer=placer)
    assert ok
    assert placer.calls == ["market_close", "cancel:777"]
    assert pos.state == ps.PositionState.CLOSED
    assert pos.close_reason == "TRAIL_EXIT"
    assert pos.trail_governing is False
    assert pos.trail_stop_order_id == 0


async def test_exit_failure_leaves_the_position_protected():
    """A refused close must not retire anything: the parked stop is the only
    protection and it stays exactly where it was."""
    placer = FakePlacer(fail_close=True, close_code=-1001)
    pos = _pos(trail_governing=True, trail_stop_price=95.0,
               trail_stop_order_id=777)
    ok = await tg._exit_at_market(pos, placer=placer)
    assert ok is False
    assert placer.cancelled == []
    assert pos.state == ps.PositionState.OPEN
    assert pos.trail_stop_order_id == 777
    assert pos.trail_governing is True
    health = tg.health()
    assert health["exit_failed"] == 1
    assert health["place_failures"][-1]["binance_code"] == -1001


async def test_exit_absorbs_already_flat_and_books_it_as_the_stop():
    """-2022 means the parked stop won the race.  The exit happened, so the
    position goes terminal — but it is booked as ``trail_stop``, because
    crediting the market leg with a fill the resting stop took would put the
    cost of confirmation in the wrong column."""
    placer = FakePlacer(fail_close=True, close_code=-2022)
    pos = _pos(trail_governing=True, trail_stop_price=95.0,
               trail_stop_order_id=777)
    ok = await tg._exit_at_market(pos, placer=placer)
    assert ok
    assert pos.state == ps.PositionState.CLOSED
    outcomes = tg.health()["outcomes"]
    assert [o["exit_kind"] for o in outcomes] == ["trail_stop"]
    assert outcomes[0]["exit"] == pytest.approx(95.0)


async def test_orphaned_cancel_after_exit_is_counted_not_swallowed():
    """Binance does NOT retire a reduce-only CONDITIONAL stop when the position
    closes — PROMUSDT, 2026-08-11, still resting 28 minutes later.  A cancel
    that fails here leaves exactly that, so it is counted."""
    placer = FakePlacer(avg_price=94.0, fail_cancel=True)
    pos = _pos(trail_governing=True, trail_stop_price=95.0,
               trail_stop_order_id=777)
    ok = await tg._exit_at_market(pos, placer=placer)
    assert ok
    assert tg.health()["orphan_cancel"] == 1


# --------------------------------------------------------------------------- #
# 3. Realized outcomes — the canary's actual result
# --------------------------------------------------------------------------- #


def test_outcome_pnl_is_signed_toward_the_trade():
    """Same convention as the arm's ``pnl_level_pct``, so the two are
    comparable without a conversion nobody would remember to apply."""
    tg.record_outcome(
        _pos(side="LONG", signal_id="L1"), exit_price=95.0, exit_kind="trail_stop"
    )
    tg.record_outcome(
        _pos(side="SHORT", signal_id="S1"), exit_price=95.0, exit_kind="trail_stop"
    )
    longs, shorts = tg.health()["outcomes"]
    assert longs["pnl_pct"] == pytest.approx(-5.0)
    assert shorts["pnl_pct"] == pytest.approx(5.0)


def test_outcome_refuses_to_invent_a_fill():
    """An accepted MARKET order reports ``avgPrice`` 0 until it fills.  A zero
    booked as a price averages into the book as a flat trade, which is a claim
    — ``None`` says the row does not know."""
    tg.record_outcome(_pos(), exit_price=0.0, exit_kind="flip_close")
    assert tg.health()["outcomes"][0]["pnl_pct"] is None


def test_the_two_fills_are_never_pooled():
    """``@level`` and ``@confirm`` are the arm's two fills and their difference
    is the cost of confirmation.  There is deliberately no blended average
    here, exactly as there is none on ``/signals/sar-live``."""
    health = tg.health()
    assert "avg_pnl_pct" not in health
    tg.record_outcome(_pos(signal_id="A"), exit_price=95.0, exit_kind="trail_stop")
    tg.record_outcome(_pos(signal_id="B"), exit_price=99.0, exit_kind="flip_close")
    assert {o["exit_kind"] for o in tg.health()["outcomes"]} == {
        "trail_stop", "flip_close",
    }
    assert tg.health()["stops_filled"] == 1


def test_outcome_ring_is_bounded_and_publishes_its_total():
    """A bounded buffer feeding a display publishes the unbounded count beside
    it, or the sample silently becomes the denominator."""
    for i in range(tg.OUTCOME_RING + 5):
        tg.record_outcome(
            _pos(signal_id=f"S{i}"), exit_price=95.0 + i, exit_kind="trail_stop"
        )
    health = tg.health()
    assert len(health["outcomes"]) == tg.OUTCOME_RING
    assert health["stops_filled"] == tg.OUTCOME_RING + 5


# --------------------------------------------------------------------------- #
# 4. The order leak — derived, never typed
# --------------------------------------------------------------------------- #


def test_protective_attrs_cover_every_order_id_on_the_position():
    """GUARD, derived from the dataclass (fails pre-fix).

    The close paths carried a hand-written five-name tuple.  #908 added a sixth
    protective order and joined neither, so a governed position's stop survived
    every close path in the engine.  A list of names is silent by construction
    on the next one, so the requirement is derived: any ``*_order_id`` field on
    ``Position`` that protects or exits must be in the set, and a new one fails
    CI rather than leaking quietly.

    Exclusions are named here rather than filtered silently, so each one is a
    decision somebody made and a reader can check:

    ``entry_order_id``
        the way IN.  Cancelling it on close is a no-op or a bug.
    ``pretp_order_id``
        ``place_pretp_partial`` is a REDUCE_ONLY **MARKET** order — it fills on
        submission and never rests, so the stored id is a record of a fill,
        not a live order.  There is nothing to cancel.
    """
    known_non_protective = {"entry_order_id", "pretp_order_id"}
    on_position = {
        f.name for f in dataclass_fields(ps.Position)
        if f.name.endswith("_order_id")
    }
    expected = on_position - known_non_protective
    missing = expected - set(sd._PROTECTIVE_ORDER_ATTRS)
    assert not missing, (
        f"protective order id(s) no close path cancels: {sorted(missing)} — "
        "add them to _PROTECTIVE_ORDER_ATTRS or name them non-protective"
    )
    unknown = set(sd._PROTECTIVE_ORDER_ATTRS) - on_position
    assert not unknown, f"not fields on Position: {sorted(unknown)}"


def test_trail_stop_is_in_the_protective_set():
    """The specific regression, stated by name so deleting the derived test
    above cannot quietly take this with it."""
    assert "trail_stop_order_id" in sd._PROTECTIVE_ORDER_ATTRS


def test_reconciler_watches_the_governor_stop():
    """GUARD (fails pre-fix).

    ``trail_order_id`` is the older native TRAILING_STOP_MARKET — a different
    field, one word away.  Without ``trail_stop_order_id`` a governed position
    read as permanently unprotected AND permanently unwatched: after handover
    every other protective id is 0, so an externally cancelled governor stop
    produced no re-place and no naked-residual page.
    """
    src = inspect.getsource(rec.Reconciler._heal_external_order_cancels)
    assert "trail_stop_order_id" in src
    assert "trail_order_id" in src


# --------------------------------------------------------------------------- #
# 5. The signal's SL must not close what the handover took over
# --------------------------------------------------------------------------- #


def test_sl_hit_skips_a_governed_position():
    """GUARD (fails pre-fix).

    At handover the governor CANCELS the evaluator's stop on the exchange.
    TradeMonitor kept evaluating the signal against that same level and closed
    everyone on a hit, so the governed position exited on a rule the mechanism
    had removed — and exited worse, at market.  PROMUSDT 2026-08-11: signal
    SL_HIT at -3.00% designed, position market-closed 12s later at **-4.89%**.

    Asserted on the source of the guard rather than by driving Firestore,
    because the surrounding function needs a live position store; the behaviour
    itself is covered by the pair of predicate tests below.
    """
    src = inspect.getsource(sd.close_fsm_positions_for_signal)
    assert 'reason == "sl_hit"' in src
    assert "trail_governing" in src


@pytest.mark.parametrize(
    "reason,governing,expect_skip",
    [
        ("sl_hit", True, True),
        ("sl_hit", False, False),
        ("invalidated", True, False),
        ("expired", True, False),
        ("cancelled", True, False),
    ],
)
def test_only_sl_hit_is_exempt_and_only_once_governing(
    reason: str, governing: bool, expect_skip: bool
):
    """The narrowness IS the argument.

    ``invalidated`` / ``expired`` / ``cancelled`` are the engine deciding to be
    out of the trade entirely rather than a level being touched — B12's
    lockstep guarantee and the hold-time bound both depend on those still
    closing everyone, governed or not.  Pre-handover the evaluator's SL is
    genuinely live and genuinely this position's stop.
    """
    pos = _pos(trail_governing=governing)
    skipped = reason == "sl_hit" and bool(
        getattr(pos, "trail_governing", False)
    )
    assert skipped is expect_skip
