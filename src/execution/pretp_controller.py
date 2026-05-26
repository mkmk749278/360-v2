"""Pre-TP partial-close controller — the §3.2a doctrine plug-in.

Per OWNER_BRIEF §3.2a + B17:

* Pre-TP is the **primary exit** for the doctrine.  Most signals
  partially close at the pre-TP threshold (banking real profit on
  ``pretp_fraction`` of the position at the user-configured value,
  minimum 30%).  The residual rides toward TP1 with SL ratcheted to
  break-even.
* Asymmetry: full SL hit = −7.9% on margin at 10×; banked partial +
  BE-stop on residual = ~−0.5% even if the residual flatlines.
* This is what turns the engine's cohort from net-negative-after-
  fees to net-positive.

This module's responsibilities:

1. :func:`compute_pretp_threshold_price` — given entry price +
   direction + pre-TP raw-percent threshold, return the price at
   which pre-TP should fire.
2. :func:`should_fire_pretp` — given a position's pre-TP threshold
   and the current mark price + direction, return True if pre-TP
   should fire NOW.  Pure, side-effect-free.
3. :func:`fire_pretp` — execute the pre-TP partial close: place the
   REDUCE_ONLY MARKET order, mark ``pretp_fired=True`` on the
   position, persist.  Idempotent — won't double-fire if called
   twice.

The companion logic in :mod:`src.execution.position_fsm` handles
what happens AFTER the pre-TP fills (the BE shift): cancel original
SL → place new SL at entry price.  That's tracked through the
ORDER_TRADE_UPDATE event for the pre-TP order; see
:meth:`PositionFSM._apply_pretp_fill`.

Mark-price subscription itself is out of scope for PR-7.  This
module exposes the threshold-detection logic as a pure function so
PR-8/9 can wire it to either (a) the engine's existing Binance WS
infrastructure (cheaper — one shared market-data stream for all
users) or (b) per-user ``@markPrice`` subscriptions.  Either way,
when the price-feed surface decides "this user's position needs to
check pre-TP," it calls :func:`maybe_fire_pretp` with the current
mark price and we do the rest.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional

from src.utils import get_logger

from . import order_placer as _order_placer
from . import position_state as _position_state

log = get_logger("execution.pretp_controller")


# Per §3.2a doctrine the pre-TP raw threshold is typically +0.32%
# of entry price.  Configurable per-signal but the engine ships a
# safe default.  Net @ 10x after fees lands at +2.5% on margin.
_DEFAULT_PRETP_THRESHOLD_PCT = 0.32  # percent of entry price


# ---------------------------------------------------------------------------
# Threshold math — pure
# ---------------------------------------------------------------------------


def compute_pretp_threshold_price(
    *,
    entry_price: float,
    direction: str,  # "LONG" | "SHORT"
    threshold_pct: float = _DEFAULT_PRETP_THRESHOLD_PCT,
) -> float:
    """Return the price at which pre-TP should fire.

    LONG: entry_price * (1 + threshold_pct/100)
    SHORT: entry_price * (1 - threshold_pct/100)

    ``threshold_pct`` is in raw percent (0.32 = 0.32%, not 32%).
    A 0 or negative threshold returns ``entry_price`` — defensive,
    so a misconfiguration doesn't fire pre-TP immediately.
    """
    if threshold_pct <= 0 or entry_price <= 0:
        return entry_price
    factor = 1.0 + threshold_pct / 100.0
    if direction == "LONG":
        return entry_price * factor
    if direction == "SHORT":
        return entry_price * (2.0 - factor)  # 1 - pct/100
    raise ValueError(f"unknown direction: {direction!r}")


def should_fire_pretp(
    *,
    position: _position_state.Position,
    mark_price: float,
) -> bool:
    """Decide if pre-TP should fire RIGHT NOW.

    Returns False (no-op) when any of:

    * pre-TP already fired (``position.pretp_fired``) — idempotency.
    * Position not in OPEN state (PENDING means entry hasn't filled
      yet; PRE_TP_FIRED / TP*_HIT / CLOSED means we've moved past).
    * pre-TP threshold price not set (zero — signal was placed with
      pre-TP disabled).
    * Mark price hasn't crossed the threshold yet.

    Returns True when:

    * Position OPEN + not yet fired + threshold set + mark price
      crossed (above for LONG, below for SHORT).
    """
    if position.pretp_fired:
        return False
    if position.state != _position_state.PositionState.OPEN:
        return False
    if position.pretp_threshold_price <= 0:
        return False
    if mark_price <= 0:
        return False
    if position.side == "LONG":
        return mark_price >= position.pretp_threshold_price
    if position.side == "SHORT":
        return mark_price <= position.pretp_threshold_price
    return False


# ---------------------------------------------------------------------------
# Pre-TP firing — places the partial-close order + persists the flag
# ---------------------------------------------------------------------------


class PretpAlreadyFiredError(Exception):
    """Caller asked to fire pre-TP but it's already fired.  Indicates
    a caller-side bug (the should_fire_pretp check should have caught
    this); surface loudly rather than silently double-firing."""


async def fire_pretp(
    position: _position_state.Position,
    *,
    placer: _order_placer.OrderPlacer,
    mark_price: float = 0.0,
) -> _order_placer.OrderPlacementResult:
    """Place the pre-TP partial close + mark the position as fired.

    Idempotency: raises :class:`PretpAlreadyFiredError` if the
    position is already pretp_fired.  Callers (typically
    :func:`maybe_fire_pretp`) check via :func:`should_fire_pretp`
    before calling, so this is a defensive check, not the primary
    flow.

    Order placement failure propagates — caller decides whether to
    retry on the next mark-price tick (transient) or surface to
    the user (key revoked, account suspended).  We do NOT mark
    pretp_fired=True until the order placement succeeds; a transient
    failure leaves the controller free to retry on the next tick.

    ``mark_price`` is forwarded to :func:`_compute_pretp_qty` for the
    MIN_NOTIONAL guard (see that function's docstring).
    """
    if position.pretp_fired:
        raise PretpAlreadyFiredError(
            f"pre-TP already fired for signal_id={position.signal_id}"
        )
    pretp_qty = _compute_pretp_qty(position, mark_price=mark_price)
    if pretp_qty <= 0:
        # Nothing to close — pretp_fraction is 0 or position has no
        # filled qty yet.  Mark as fired so we don't retry forever.
        log.info(
            "fire_pretp: skipped (zero qty) uid={} signal_id={}",
            position.firebase_uid,
            position.signal_id,
        )
        position.pretp_fired = True
        _position_state.put_position(position)
        return _order_placer.OrderPlacementResult(
            order_id=0,
            client_order_id="",
            status="SKIPPED",
            avg_price=0.0,
            binance_body={},
        )
    result = await placer.place_pretp_partial(
        signal_id=position.signal_id,
        symbol=position.symbol,
        direction=position.side,
        quantity=pretp_qty,
    )
    position.pretp_fired = True
    position.pretp_order_id = result.order_id
    position.last_event_at = datetime.now(timezone.utc)
    _position_state.put_position(position)
    log.info(
        "fire_pretp: order placed uid={} signal_id={} qty={} order_id={}",
        position.firebase_uid,
        position.signal_id,
        pretp_qty,
        result.order_id,
    )
    return result


async def maybe_fire_pretp(
    position: _position_state.Position,
    *,
    mark_price: float,
    placer: _order_placer.OrderPlacer,
) -> bool:
    """Composite of should + fire.  Returns True if pre-TP fired this
    call, False if the threshold check said no.

    This is the verb the mark-price feed (PR-8/9) calls on every
    tick for every open position.  Cheap when nothing to do: a
    handful of bool comparisons.  Expensive only when actually
    firing: one Binance order placement + one Firestore write.
    """
    if not should_fire_pretp(position=position, mark_price=mark_price):
        return False
    try:
        await fire_pretp(position, placer=placer, mark_price=mark_price)
        return True
    except _order_placer.OrderPlacementError as exc:
        log.warning(
            "maybe_fire_pretp: placement failed (will retry on next "
            "tick) uid={} signal_id={} exc={}",
            position.firebase_uid,
            position.signal_id,
            exc,
        )
        return False


# ---------------------------------------------------------------------------
# Quantity computation
# ---------------------------------------------------------------------------


def _compute_pretp_qty(
    position: _position_state.Position,
    mark_price: float = 0.0,
) -> float:
    """``pretp_fraction × filled_qty`` (or total_qty if entry fully filled),
    floored to the symbol's LOT_SIZE stepSize.

    B17 enforces the 30%-floor / 100%-ceiling at signal-placement time;
    this function just multiplies + rounds — no fraction validation.

    ``mark_price`` is used for the MIN_NOTIONAL check only.  When below
    Binance's per-symbol minimum (typically $5 USDT), the partial qty is
    bumped to the full remaining position so the pre-TP banking doesn't
    silently fail with -4164.  Callers that don't have mark_price handy
    can pass 0 to skip the MIN_NOTIONAL check (Binance will reject if
    needed; the signing-service error is then the diagnostic).
    """
    from src.execution import symbol_filters as _sf

    base_qty = position.filled_qty if position.filled_qty > 0 else position.total_qty
    remaining = position.total_qty - position.closed_qty
    if remaining <= 0:
        remaining = base_qty

    raw_qty = base_qty * position.pretp_fraction
    # Apply LOT_SIZE stepSize so Binance never returns -1111.
    qty = _sf.round_qty(position.symbol, raw_qty)
    if qty <= 0:
        return 0.0

    # MIN_NOTIONAL guard: for small positions the partial qty × price can
    # fall below the $5 Binance floor.  Fall back to full remaining qty
    # so the partial actually executes.
    if mark_price > 0 and not _sf.meets_min_notional(position.symbol, qty, mark_price):
        full_qty = _sf.round_qty(position.symbol, remaining)
        if full_qty > 0 and _sf.meets_min_notional(position.symbol, full_qty, mark_price):
            log.info(
                "_compute_pretp_qty: partial {:.8f} below MIN_NOTIONAL — "
                "using full qty {:.8f} for {}",
                qty, full_qty, position.symbol,
            )
            return full_qty
        # Both partial and full are below MIN_NOTIONAL (shouldn't happen
        # since the entry itself passed MIN_NOTIONAL, but be defensive).
        return 0.0

    return qty
