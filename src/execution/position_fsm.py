"""Position FSM — state transitions on Binance ORDER_TRADE_UPDATE events.

The FSM reacts to fill events and advances per-position state.  In
PR-6 it ships:

* Entry fill → ``PENDING`` → ``OPEN`` (records filled price + qty).
* TP1 fill → ``OPEN`` → ``TP1_HIT`` (updates closed_qty + realized_pnl).
* TP2 fill → ``TP1_HIT`` → ``TP2_HIT``.
* TP3 fill → ``TP2_HIT`` → ``CLOSED`` (terminal; all profit taken).
* SL fill → any state → ``CLOSED`` (terminal; stop hit).

What this PR does NOT do — deferred to **PR-7**:

* Pre-TP partial close (the doctrine-critical §3.2a banking).
* BE shift: on TP1 fill, cancel old SL + place new SL at entry.
* SL ratcheting on TP2 fill (further tightening).

PR-6 ships the FSM SCAFFOLD with all transitions wired but the BE
shift logic stubbed.  PR-7 plugs the §3.2a doctrine in by replacing
the stub.

Concurrency: each position's events are processed in series (the WS
consumer dispatches one event at a time per user).  No locking
required at this layer — Firestore writes are atomic per document
and we're the only writer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Optional

from src.execution import events as _events
from src.execution import order_placer as _order_placer
from src.execution import position_state as _position_state
from src.utils import get_logger

log = get_logger("execution.position_fsm")


# ---------------------------------------------------------------------------
# Public API — what the worker (PR-5) wires as the event handler
# ---------------------------------------------------------------------------


class PositionFSM:
    """Per-user FSM that handles ORDER_TRADE_UPDATE events.

    Constructed once per user (per :class:`src.execution.position_worker.PositionWorker`).
    Routes incoming events to the right per-signal position state +
    advances the state machine.

    ``order_placer_factory`` is injected so PR-7 (which extends the
    FSM to do BE shifts) and tests can swap in different placers.
    """

    def __init__(
        self,
        firebase_uid: str,
        *,
        order_placer_factory: Optional[
            Callable[[str], _order_placer.OrderPlacer]
        ] = None,
    ) -> None:
        self.firebase_uid = firebase_uid
        self._order_placer_factory = (
            order_placer_factory or _default_order_placer_factory
        )

    async def handle_event(self, event: _events.Event) -> None:
        """Top-level dispatch.  ORDER_TRADE_UPDATE → state transition;
        other event types are no-ops in this FSM (ACCOUNT_UPDATE is
        consumed by PR-9 reconciler; MARGIN_CALL by PR-8 tripwires;
        listenKeyExpired by the worker's outer reconnect loop).

        Any exception is logged but does NOT propagate — the WS
        consumer's design (PR-5) absorbs handler failures so one
        broken event doesn't tear down the stream.  Re-raising here
        would only mean the user's WS gets restarted, which doesn't
        help unless the FSM bug is somehow self-healing.
        """
        if isinstance(event, _events.OrderTradeUpdate):
            try:
                await self._handle_order_trade_update(event)
            except Exception:
                log.exception(
                    "position_fsm: handler raised on ORDER_TRADE_UPDATE "
                    "uid={} client_order_id={}",
                    self.firebase_uid,
                    event.client_order_id,
                )

    async def _handle_order_trade_update(
        self, event: _events.OrderTradeUpdate
    ) -> None:
        """The FSM's core.  Decode the clientOrderId to find which
        signal + phase this event belongs to, load the position state,
        apply the transition, persist.
        """
        parsed = _position_state.parse_coid(event.client_order_id)
        if parsed is None:
            # Foreign order — placed via Binance UI / another tool,
            # not via Lumin.  Log + skip.  This is expected behaviour
            # if the user trades manually alongside Lumin.
            log.debug(
                "position_fsm: foreign order (uid={} coid={})",
                self.firebase_uid,
                event.client_order_id,
            )
            return
        signal_id, phase = parsed
        try:
            position = _position_state.get_position(
                self.firebase_uid, signal_id
            )
        except _position_state.PositionNotFoundError:
            log.warning(
                "position_fsm: event for unknown position uid={} signal_id={} "
                "phase={} (was the position deleted?)",
                self.firebase_uid,
                signal_id,
                phase,
            )
            return

        if _position_state.is_terminal(position.state):
            # Late event for an already-closed position (Binance can
            # send out-of-order events when the WS reconnects after a
            # brief gap).  Log + skip — re-applying transitions on a
            # terminal position would corrupt the audit trail.
            log.debug(
                "position_fsm: late event for terminal position "
                "uid={} signal_id={} phase={} state={}",
                self.firebase_uid,
                signal_id,
                phase,
                position.state.value,
            )
            return

        if event.execution_type != "TRADE":
            # NEW / CANCELED / EXPIRED / TRAILING_STOP_UPDATE — not a
            # fill.  We only care about fills.
            return

        # Dispatch to the per-phase transition.  Each updates the
        # position dataclass in place; we persist once at the end.
        if phase == "entry":
            self._apply_entry_fill(position, event)
        elif phase == "tp1":
            self._apply_tp1_fill(position, event)
        elif phase == "tp2":
            self._apply_tp2_fill(position, event)
        elif phase == "tp3":
            self._apply_tp3_fill(position, event)
        elif phase == "sl":
            self._apply_sl_fill(position, event)
        else:
            # parse_coid only emits these five phases, so unreachable
            # in practice.  Defensive log.
            log.warning(
                "position_fsm: unrecognised phase: {}", phase
            )
            return

        position.last_event_at = datetime.now(timezone.utc)
        _position_state.put_position(position)
        log.info(
            "position_fsm: transition uid={} signal_id={} phase={} → state={}",
            self.firebase_uid,
            signal_id,
            phase,
            position.state.value,
        )

    # ------------------------------------------------------------------
    # Per-phase transition logic — pure mutation of the Position dataclass
    # ------------------------------------------------------------------

    def _apply_entry_fill(
        self,
        position: _position_state.Position,
        event: _events.OrderTradeUpdate,
    ) -> None:
        """Entry fill — PENDING → OPEN (or stays PENDING if partial).

        Records the cumulative filled qty + the average filled price.
        Once cumulative_filled_qty equals (or exceeds, defensively)
        the position's total_qty, transition to OPEN.
        """
        position.filled_qty = event.cumulative_filled_qty
        if event.average_price > 0:
            position.entry_price_filled = event.average_price
        if event.order_status == "FILLED" or position.filled_qty >= position.total_qty:
            position.state = _position_state.PositionState.OPEN

    def _apply_tp1_fill(
        self,
        position: _position_state.Position,
        event: _events.OrderTradeUpdate,
    ) -> None:
        """TP1 fill — OPEN → TP1_HIT.

        Records the closed quantity.  PR-7 will additionally:

            (a) cancel position.sl_order_id (the original SL at the
                signal's SL price);
            (b) place a new SL at position.entry_price_filled
                (the BE shift).

        For PR-6 we just transition state and update accounting.  The
        BE shift is stubbed in :meth:`_post_tp1_fill_hook` so PR-7's
        diff is small and the FSM tests for PR-6 can pin the
        accounting transitions in isolation.
        """
        position.closed_qty += event.last_filled_qty
        position.realized_pnl_total += event.realized_pnl
        position.state = _position_state.PositionState.TP1_HIT
        # PR-7 plug-in point.  Default is no-op so PR-6 is self-
        # contained.
        # await self._post_tp1_fill_hook(position)

    def _apply_tp2_fill(
        self,
        position: _position_state.Position,
        event: _events.OrderTradeUpdate,
    ) -> None:
        """TP2 fill — TP1_HIT → TP2_HIT."""
        position.closed_qty += event.last_filled_qty
        position.realized_pnl_total += event.realized_pnl
        position.state = _position_state.PositionState.TP2_HIT

    def _apply_tp3_fill(
        self,
        position: _position_state.Position,
        event: _events.OrderTradeUpdate,
    ) -> None:
        """TP3 fill — TP2_HIT → CLOSED.  All profit booked."""
        position.closed_qty += event.last_filled_qty
        position.realized_pnl_total += event.realized_pnl
        position.state = _position_state.PositionState.CLOSED
        position.closed_at = datetime.now(timezone.utc)
        position.close_reason = "TP3"

    def _apply_sl_fill(
        self,
        position: _position_state.Position,
        event: _events.OrderTradeUpdate,
    ) -> None:
        """SL fill — any state → CLOSED.  Terminal; stop hit.

        The SL order has ``closePosition=true`` so the cumulative
        fill on the SL order equals the remaining position size at
        the time of the SL firing.  We record realized_pnl + close
        the position; further events on this signal_id are
        late-event-skipped by the terminal check.
        """
        position.closed_qty = position.total_qty  # SL is closePosition
        position.realized_pnl_total += event.realized_pnl
        position.state = _position_state.PositionState.CLOSED
        position.closed_at = datetime.now(timezone.utc)
        # Record which TP phase was last reached so the close_reason
        # is informative ("SL after TP1 hit" vs "raw SL hit").
        if position.close_reason == "":
            position.close_reason = "SL"


# ---------------------------------------------------------------------------
# Signal placement — called externally when a signal arrives
# ---------------------------------------------------------------------------


async def place_signal(
    firebase_uid: str,
    *,
    signal_id: str,
    symbol: str,
    direction: str,  # "LONG" | "SHORT"
    entry_price: float,
    sl_price: float,
    tp1_price: float,
    tp2_price: float,
    tp3_price: float,
    total_qty: float,
    tp1_qty: float,
    tp2_qty: float,
    tp3_qty: float,
    order_placer_factory: Optional[
        Callable[[str], _order_placer.OrderPlacer]
    ] = None,
) -> _position_state.Position:
    """Place all orders for one new signal + persist the position state.

    Steps (in strict order so a failure mid-way leaves a recoverable
    state in Firestore):

    1. Place the MARKET entry order.  This is the only order that
       moves money; if it fails, the position never opens and we
       don't have to clean up dangling SL/TP orders.
    2. Persist the position to Firestore in ``PENDING`` state with
       the entry order id captured.  At this point the FSM can
       receive ORDER_TRADE_UPDATE events and advance state.
    3. Place the native SL.
    4. Place the three TPs.
    5. Re-persist with all order ids captured.

    Steps 3-5 are best-effort — if Binance rejects a TP (e.g. price
    too far from market), we log and continue; the position is OPEN
    with whatever subset of SL/TP orders landed.  A future hardening
    would attempt to cancel the entry on critical-SL failure, but
    for PR-6 the simpler "all-or-some" semantics is the floor.

    Raises :class:`order_placer.OrderPlacementError` only if the
    ENTRY fails.  All other failures are logged + tolerated.
    """
    factory = order_placer_factory or _default_order_placer_factory
    placer = factory(firebase_uid)

    # Step 1: entry — the only must-succeed step.
    entry_result = await placer.place_market_entry(
        signal_id=signal_id,
        symbol=symbol,
        direction=direction,
        quantity=total_qty,
    )

    # Step 2: persist immediately with entry_order_id captured so the
    # FSM can handle the entry-fill event even if subsequent SL/TP
    # placements crash this coroutine.
    position = _position_state.Position(
        signal_id=signal_id,
        firebase_uid=firebase_uid,
        symbol=symbol,
        side=direction,
        state=_position_state.PositionState.PENDING,
        entry_price_target=entry_price,
        entry_price_filled=0.0,
        sl_price=sl_price,
        tp1_price=tp1_price,
        tp2_price=tp2_price,
        tp3_price=tp3_price,
        total_qty=total_qty,
        tp1_qty=tp1_qty,
        tp2_qty=tp2_qty,
        tp3_qty=tp3_qty,
        entry_order_id=entry_result.order_id,
    )
    _position_state.put_position(position)

    # Steps 3-5: SL + 3x TP.  Best-effort.
    try:
        sl_result = await placer.place_stop_loss(
            signal_id=signal_id,
            symbol=symbol,
            direction=direction,
            stop_price=sl_price,
        )
        position.sl_order_id = sl_result.order_id
    except _order_placer.OrderPlacementError as exc:
        log.warning(
            "place_signal: SL placement failed (position remains "
            "uncovered until manual intervention) uid={} signal_id={} "
            "exc={}",
            firebase_uid, signal_id, exc,
        )

    for tp_phase, tp_price, tp_qty_value in (
        ("tp1", tp1_price, tp1_qty),
        ("tp2", tp2_price, tp2_qty),
        ("tp3", tp3_price, tp3_qty),
    ):
        if tp_qty_value <= 0:
            continue  # signal didn't specify this TP leg
        try:
            tp_result = await placer.place_take_profit(
                signal_id=signal_id,
                symbol=symbol,
                direction=direction,
                stop_price=tp_price,
                quantity=tp_qty_value,
                tp_phase=tp_phase,
            )
            if tp_phase == "tp1":
                position.tp1_order_id = tp_result.order_id
            elif tp_phase == "tp2":
                position.tp2_order_id = tp_result.order_id
            elif tp_phase == "tp3":
                position.tp3_order_id = tp_result.order_id
        except _order_placer.OrderPlacementError as exc:
            log.warning(
                "place_signal: {} placement failed (position keeps "
                "remaining TPs) uid={} signal_id={} exc={}",
                tp_phase, firebase_uid, signal_id, exc,
            )

    # Re-persist with all order ids captured.
    _position_state.put_position(position)
    log.info(
        "place_signal: position OPEN-bound uid={} signal_id={} symbol={} "
        "entry_order_id={}",
        firebase_uid, signal_id, symbol, entry_result.order_id,
    )
    return position


def _default_order_placer_factory(firebase_uid: str) -> _order_placer.OrderPlacer:
    return _order_placer.OrderPlacer(firebase_uid)
