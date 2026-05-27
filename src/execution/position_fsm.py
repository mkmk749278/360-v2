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

import asyncio
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
        # Pre-TP and SL-BE may trigger additional async order
        # placements (BE shift on pre-TP fill) so they're awaited.
        if phase == "entry":
            self._apply_entry_fill(position, event)
        elif phase == "pretp":
            await self._apply_pretp_fill(position, event)
        elif phase == "tp1":
            await self._apply_tp1_fill(position, event)
        elif phase == "tp2":
            self._apply_tp2_fill(position, event)
        elif phase == "tp3":
            self._apply_tp3_fill(position, event)
        elif phase == "sl":
            self._apply_sl_fill(position, event)
        elif phase == "sl_be":
            self._apply_sl_be_fill(position, event)
        else:
            # parse_coid only emits known phases, so unreachable
            # in practice.  Defensive log.
            log.warning(
                "position_fsm: unrecognised phase: {}", phase
            )
            return

        position.last_event_at = datetime.now(timezone.utc)
        try:
            _position_state.put_position(position)
        except Exception as exc:
            log.error(
                "position_fsm: put_position FAILED uid={} signal_id={} "
                "phase={} new_state={} exc={} — in-memory state advanced "
                "but Firestore not updated; reconciler will re-diverge",
                self.firebase_uid, signal_id, phase,
                position.state.value, exc,
            )
            return
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
            from src.execution import pretp_dispatcher as _pd
            _pd_inst = _pd.get_instance()
            if _pd_inst is not None:
                asyncio.create_task(
                    _pd_inst.track(position.symbol),
                    name=f"pd_track_{position.symbol}",
                )

    async def _apply_pretp_fill(
        self,
        position: _position_state.Position,
        event: _events.OrderTradeUpdate,
    ) -> None:
        """Pre-TP partial close filled (per §3.2a doctrine).

        State: OPEN → PRE_TP_FIRED.

        Side effects (the doctrine):
        1. Record closed qty + realized PnL from the partial.
        2. **Cancel the original SL** at the signal's SL price.
        3. **Place a new SL at the entry price** (BE shift) so the
           residual rides to TP1 with break-even downside protection.
        4. Cancel TP2 + TP3 — residual is small enough that a single
           TP at TP1 is sufficient; multi-TP orders for the residual
           would over-commit qty.  TP1 stays active (it still closes
           the residual profitably if hit).

        BE shift order placement is best-effort: if the new SL fails
        to place, the position is uncovered until manual operator
        intervention.  PR-8's tripwires will Telegram-alert on this.
        """
        position.closed_qty += event.last_filled_qty
        position.realized_pnl_total += event.realized_pnl
        position.state = _position_state.PositionState.PRE_TP_FIRED
        position.pretp_fired = True
        placer = self._order_placer_factory(self.firebase_uid)
        # Cancel original SL.  Tolerant of -2011 (order already gone)
        # so a race between SL hit + pre-TP fill doesn't crash here.
        if position.sl_order_id:
            try:
                await placer.cancel_order(
                    symbol=position.symbol,
                    order_id=position.sl_order_id,
                )
            except _order_placer.OrderPlacementError as exc:
                log.warning(
                    "_apply_pretp_fill: SL cancel failed uid={} signal_id={} "
                    "exc={}",
                    self.firebase_uid, position.signal_id, exc,
                )
        # Cancel TP2 + TP3 — residual is too small for multi-leg TP.
        for tp_order_id in (position.tp2_order_id, position.tp3_order_id):
            if tp_order_id:
                try:
                    await placer.cancel_order(
                        symbol=position.symbol,
                        order_id=tp_order_id,
                    )
                except _order_placer.OrderPlacementError as exc:
                    log.warning(
                        "_apply_pretp_fill: TP cancel failed uid={} "
                        "signal_id={} order_id={} exc={}",
                        self.firebase_uid, position.signal_id,
                        tp_order_id, exc,
                    )
        position.tp2_order_id = 0
        position.tp3_order_id = 0
        # Place the BE-shifted SL at the entry price.  Distinct
        # clientOrderId suffix so we can tell it apart from the
        # original on fill events.
        be_price = (
            position.entry_price_filled
            if position.entry_price_filled > 0
            else position.entry_price_target
        )
        try:
            sl_be = await placer.place_stop_loss(
                signal_id=position.signal_id,
                symbol=position.symbol,
                direction=position.side,
                stop_price=be_price,
                coid_override=_position_state.coid_sl_be(position.signal_id),
            )
            position.sl_be_order_id = sl_be.order_id
            position.sl_order_id = 0  # original is gone
            position.sl_price = be_price
        except _order_placer.OrderPlacementError as exc:
            log.error(
                "_apply_pretp_fill: BE-SL placement failed (residual "
                "uncovered) uid={} signal_id={} exc={}",
                self.firebase_uid, position.signal_id, exc,
            )

    async def _apply_tp1_fill(
        self,
        position: _position_state.Position,
        event: _events.OrderTradeUpdate,
    ) -> None:
        """TP1 fill — typically reaches OPEN → TP1_HIT directly when
        pre-TP didn't fire first (an unusually-fast favourable move),
        OR PRE_TP_FIRED → TP1_HIT when the residual rides to TP1.

        Side effects:
        * Record closed qty + realized PnL.
        * If pre-TP hasn't fired yet (raw OPEN → TP1_HIT path):
          cancel original SL + place BE-shifted SL.
        * If pre-TP already fired, the SL is ALREADY at BE — nothing
          to do, just transition state.
        """
        position.closed_qty += event.last_filled_qty
        position.realized_pnl_total += event.realized_pnl
        from_open = position.state == _position_state.PositionState.OPEN
        position.state = _position_state.PositionState.TP1_HIT
        if not from_open:
            return  # already PRE_TP_FIRED → TP1_HIT: SL already at BE
        # OPEN → TP1_HIT directly: do the BE shift now.
        placer = self._order_placer_factory(self.firebase_uid)
        if position.sl_order_id:
            try:
                await placer.cancel_order(
                    symbol=position.symbol,
                    order_id=position.sl_order_id,
                )
            except _order_placer.OrderPlacementError as exc:
                log.warning(
                    "_apply_tp1_fill: SL cancel failed uid={} signal_id={} "
                    "exc={}",
                    self.firebase_uid, position.signal_id, exc,
                )
        be_price = (
            position.entry_price_filled
            if position.entry_price_filled > 0
            else position.entry_price_target
        )
        try:
            sl_be = await placer.place_stop_loss(
                signal_id=position.signal_id,
                symbol=position.symbol,
                direction=position.side,
                stop_price=be_price,
                coid_override=_position_state.coid_sl_be(position.signal_id),
            )
            position.sl_be_order_id = sl_be.order_id
            position.sl_order_id = 0
            position.sl_price = be_price
        except _order_placer.OrderPlacementError as exc:
            log.error(
                "_apply_tp1_fill: BE-SL placement failed uid={} signal_id={} "
                "exc={}",
                self.firebase_uid, position.signal_id, exc,
            )

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
        self._untrack_symbol(position.symbol)

    def _apply_sl_fill(
        self,
        position: _position_state.Position,
        event: _events.OrderTradeUpdate,
    ) -> None:
        """Original SL fill — any state → CLOSED.  Terminal; stop hit
        at the signal's original SL price (i.e. pre-TP / TP1 hadn't
        fired yet).

        The SL order has ``closePosition=true`` so the cumulative
        fill on the SL order equals the remaining position size at
        the time of the SL firing.  Records realized_pnl + closes
        the position; further events on this signal_id are
        late-event-skipped by the terminal check.
        """
        position.closed_qty = position.total_qty  # SL is closePosition
        position.realized_pnl_total += event.realized_pnl
        position.state = _position_state.PositionState.CLOSED
        position.closed_at = datetime.now(timezone.utc)
        if position.close_reason == "":
            position.close_reason = "SL"
        self._untrack_symbol(position.symbol)

    def _apply_sl_be_fill(
        self,
        position: _position_state.Position,
        event: _events.OrderTradeUpdate,
    ) -> None:
        """BE-shifted SL fill — terminal, fees-only close.

        The BE-SL fires at the entry price after pre-TP (or TP1) has
        banked profit on a fraction of the position.  At this exit
        point the user has:

        * Banked: pretp_fraction × move_to_pretp_threshold profit.
        * Lost: ~0% on the residual (entry → entry = 0 raw, minus
          round-trip fees ≈ −0.7% on margin for the residual fraction
          at 10x).

        Net per §3.2a: the asymmetry is decisive — banked partial +
        BE on residual is the doctrine's "capital preservation"
        property in action.
        """
        position.closed_qty = position.total_qty
        position.realized_pnl_total += event.realized_pnl
        position.state = _position_state.PositionState.CLOSED
        position.closed_at = datetime.now(timezone.utc)
        # Distinct from "SL" close_reason so the truth report can
        # classify these correctly (BE-stop is doctrinally healthy;
        # raw SL is not).
        if position.close_reason == "":
            position.close_reason = "SL_BE"
        self._untrack_symbol(position.symbol)

    def _untrack_symbol(self, symbol: str) -> None:
        """Schedule an untrack task for ``symbol`` on the running loop.

        Called from sync close methods; safe because they're always
        invoked from the async ``handle_event`` coroutine.  No-op when
        the PretpDispatcher singleton isn't set.
        """
        from src.execution import pretp_dispatcher as _pd
        _pd_inst = _pd.get_instance()
        if _pd_inst is not None:
            asyncio.create_task(
                _pd_inst.untrack(symbol),
                name=f"pd_untrack_{symbol}",
            )


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
    pretp_threshold_pct: float = 0.32,  # §3.2a default — raw %
    pretp_fraction: float = 0.5,  # B17 engine default — must be in [0.3, 1.0]
    invalidation_mode: str = "standard",  # B17: "loose" / "standard" / "tight"
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
    # ---- Safety gates (PR-8 + PR-11 + PR-14 wiring follow-up) ----
    #
    # Combined check before any order is placed: the engine's auto-
    # trade must be globally ENABLED, the kill switch must NOT be
    # engaged, and the user must not be auto-disabled (per-user
    # circuit breaker tripped).  Plus the tripwires from PR-8 fire
    # here too — symbol allowlist + position cap.  Rate limit is
    # checked LAST so that a tripwire-rejection doesn't count toward
    # the user's order budget.
    #
    # Default state on fresh deploy: is_globally_enabled() == False,
    # so this branch raises ``NotGloballyEnabledError`` and no orders
    # land until the operator explicitly flips the Firestore flag.
    # This is the #431 no-staged-beta safety floor in action.
    _enforce_safety_gates(
        firebase_uid=firebase_uid,
        symbol=symbol,
        signal_id=signal_id,
    )

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
    # Local import to avoid circular dep (pretp_controller imports
    # this module via the FSM tests).
    from . import pretp_controller as _pretp

    # Clamp pretp_fraction to B17 [0.30, 1.0] floor/ceiling.
    # 0.0 (or negative) passes through unchanged — PR-F allowlist uses 0
    # to suppress pre-TP entirely; clamping 0→0.30 would defeat that.
    pretp_fraction_clamped = (
        0.0 if pretp_fraction <= 0 else max(0.30, min(1.0, pretp_fraction))
    )
    pretp_threshold_price = _pretp.compute_pretp_threshold_price(
        entry_price=entry_price,
        direction=direction,
        threshold_pct=pretp_threshold_pct,
    )
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
        pretp_threshold_price=pretp_threshold_price,
        pretp_fraction=pretp_fraction_clamped,
        invalidation_mode=invalidation_mode,
    )
    _position_state.put_position(position)

    # Steps 3-5: SL + 3x TP.  Best-effort — failures are logged and
    # surfaced in the user's Recent Activity (dispatch_log) so they
    # see "SL placement failed — position uncovered" in the app
    # rather than complete silence.
    from src.execution import dispatch_log as _dl

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
        # Surface the failure in Recent Activity so the user can act.
        b_code = None
        b_msg = None
        sig_resp = getattr(exc, "signing_response", None)
        if sig_resp is not None:
            body = getattr(sig_resp, "binance_body", None)
            if isinstance(body, dict):
                try:
                    b_code = int(body.get("code", 0)) or None
                except (TypeError, ValueError):
                    pass
                raw_msg = body.get("msg") or body.get("message")
                if isinstance(raw_msg, str):
                    b_msg = raw_msg
        _dl.record_rejected(
            firebase_uid=firebase_uid,
            signal_id=signal_id,
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            reject_class="SLPlacementFailed",
            reject_detail=(
                f"Entry filled but SL order failed for {symbol}: {exc}. "
                "Position is OPEN WITHOUT stop-loss protection — "
                "close manually on Binance."
            ),
            reject_binance_code=b_code,
            reject_binance_msg=b_msg,
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
            b_code = None
            b_msg = None
            sig_resp = getattr(exc, "signing_response", None)
            if sig_resp is not None:
                body = getattr(sig_resp, "binance_body", None)
                if isinstance(body, dict):
                    try:
                        b_code = int(body.get("code", 0)) or None
                    except (TypeError, ValueError):
                        pass
                    raw_msg = body.get("msg") or body.get("message")
                    if isinstance(raw_msg, str):
                        b_msg = raw_msg
            _dl.record_rejected(
                firebase_uid=firebase_uid,
                signal_id=signal_id,
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                reject_class="TPPlacementFailed",
                reject_detail=(
                    f"Entry filled but {tp_phase.upper()} order failed for "
                    f"{symbol}: {exc}."
                ),
                reject_binance_code=b_code,
                reject_binance_msg=b_msg,
            )

    # Step 6: native pre-TP LIMIT (PR-C).  Placed here at dispatch time
    # so it rests on Binance's book passively — no tick polling needed.
    # Best-effort: a failure leaves pretp_order_id=0, which lets the
    # tick-based MARKET fallback in pretp_controller run instead.
    if pretp_fraction_clamped > 0 and pretp_threshold_price > 0:
        from src.execution import symbol_filters as _sf
        pretp_qty = _sf.round_qty(
            symbol, total_qty * pretp_fraction_clamped
        )
        if pretp_qty > 0:
            try:
                pretp_lim_result = await placer.place_pretp_limit(
                    signal_id=signal_id,
                    symbol=symbol,
                    direction=direction,
                    limit_price=pretp_threshold_price,
                    quantity=pretp_qty,
                )
                position.pretp_order_id = pretp_lim_result.order_id
            except _order_placer.OrderPlacementError as exc:
                log.warning(
                    "place_signal: pre-TP LIMIT placement failed — "
                    "tick-based MARKET fallback will fire instead "
                    "uid={} signal_id={} exc={}",
                    firebase_uid, signal_id, exc,
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


# ---------------------------------------------------------------------------
# Safety-gate enforcement (PR-8 + PR-11 + PR-14 follow-up wiring)
# ---------------------------------------------------------------------------


class NotGloballyEnabledError(Exception):
    """Engine's global auto-trade enable flag is OFF.  Default state
    on fresh deploy.  Operator must flip ``auto_trade_globally_enabled``
    in Firestore (or via the future Telegram bot command) before any
    user can auto-trade."""


def _enforce_safety_gates(
    *, firebase_uid: str, symbol: str, signal_id: str
) -> None:
    """Run every blast-radius check before an order is placed.

    Raises a typed exception on the first failure — caller (typically
    the signal-handler orchestrator) catches + decides whether to
    surface to the user, alert the operator, or silently skip the
    signal for this user.

    Check order is intentional:
      1. Global enable flag — cheapest read (cached); rejects every
         user immediately when auto-trade is off engine-wide.
      2. Kill switch — same cached read; rejects when emergency
         halt is engaged.
      3. Per-user disable — cached read; rejects users tripped by
         the per-user circuit breaker.
      4. Symbol allowlist — pure-Python check; rejects out-of-list
         symbols (the breach-signal tripwire).
      5. Per-user circuit breaker — same; rejects users with too many
         recent rejections.
      6. Global circuit breaker — same; rejects when engine-wide
         rejection cluster has tripped.
      7. Rate limit — LAST so a tripwire-rejection above doesn't
         count against the user's order budget.

    The kill_switch + tripwires modules silently no-op when they're
    not initialised (e.g. dev path without GCP wired), so this gate
    chain doesn't crash in test / dev contexts that haven't booted
    the full server-side execution stack.
    """
    from . import kill_switch as _kill_switch
    from . import tripwires as _tripwires

    # 1 + 2 + 3 — Firestore-backed flags (cached 5s).
    if _kill_switch.is_initialised():
        ks = _kill_switch.get_client()
        if not ks.is_globally_enabled():
            raise NotGloballyEnabledError(
                "auto-trade is globally disabled — operator must flip "
                "auto_trade_globally_enabled = true in Firestore"
            )
        if ks.is_global_engaged():
            raise _tripwires.GlobalKillSwitchEngaged(
                "global kill switch engaged — orders refused for all users"
            )
        if ks.is_user_disabled(firebase_uid):
            raise _tripwires.UserAutoDisabled(
                f"user {firebase_uid} is auto-disabled"
            )

    # 4a — symbol allowlist (engine-wide).  Reads env at call-time
    # so a deploy that narrows the allowlist takes effect on the next
    # signal without an engine restart.
    _tripwires.assert_symbol_allowed(symbol)
    # 4b — per-user symbol preference (PR E 2026-05-19).  User can
    # narrow (never widen) the engine-wide list via the app's symbol
    # picker.  No preference set (NULL) → fall through.
    _tripwires.assert_symbol_in_user_preference(symbol, firebase_uid)

    # 5 + 6 — circuit breakers.  These also fire Telegram alerts on
    # first trip via PR-11's spawn pattern.
    _tripwires.per_user_breaker().check(firebase_uid)
    _tripwires.global_breaker().check()

    # 7 — rate limit last.  Records this order in the per-user
    # sliding window IFF every prior check passed.
    _tripwires.rate_limiter().check_and_record(firebase_uid)
