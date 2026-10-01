"""CoinDCX position lifecycle: plan → enter → protect → close → record.

The one exit shape this venue uses is the engine's default exit profile —
**TP1 for the whole position against a fixed stop** — placed as CoinDCX's
position-level TP/SL, which closes the entire position whichever fires.  No
partial legs, no reduce-only orders (CoinDCX's order API has no such flag, so
a standalone take-profit could open a reverse position after the stop closed
the trade), no trailing.  A user's Binance-only opt-ins (pre-TP, trail
governor, TP ladder) therefore do not apply on CoinDCX, and the app says so.

Invariants this module enforces, each with the failure it prevents:

1. **Never naked.**  After the entry fills, the stop is placed; if it is
   refused twice, the position is exited at market.  If the exit itself fails
   the row stays ``OPEN`` with ``sl_resting = False`` and the reconciler
   retries both every cycle.
2. **Never merged.**  CoinDCX keeps one net position per pair; an entry is
   refused unless the user's pair is flat with no resting orders, so our
   position can never absorb (or be absorbed by) one the user holds.
3. **Never twice.**  The record for (uid, signal) is inserted before the order
   with ``INSERT OR IGNORE``; a second dispatch finds it and stops.
4. **Never liquidated before stopped.**  Isolated margin; leverage is lowered
   until liquidation sits at least ``COINDCX_LIQUIDATION_STOP_MULTIPLE`` stop
   distances away, and the liquidation price CoinDCX reports after the fill is
   checked against the stop — if the stop is not the nearer level, we exit.
5. **Record what happened.**  Every refusal is named (dispatch log + record),
   and a close carries the exchange's own exit price and fees.
"""

from __future__ import annotations

import asyncio
import math
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from src.utils import get_logger
from src.venues.coindcx import client as _client
from src.venues.coindcx import instruments as _inst
from src.venues.coindcx import positions as _pos

log = get_logger("venues.coindcx.execution")

VENUE = "coindcx"

# Close reasons (``CoinDCXPosition.close_reason``).
CLOSE_SL = "SL"
CLOSE_TP1 = "TP1"
CLOSE_LIQUIDATED = "LIQUIDATED"
CLOSE_EXIT = "EXIT"                  # a market exit we requested (reason in last_error)
CLOSE_EXTERNAL = "EXTERNAL"          # flattened by something other than our orders
CLOSE_PROTECTION_FAILED = "PROTECTION_FAILED"
CLOSE_LIQUIDATION_INSIDE_STOP = "LIQUIDATION_INSIDE_STOP"
CLOSE_AGE_CAP = "AGE_CAP"

_counters: Dict[str, int] = {}


def _count(key: str) -> None:
    _counters[key] = _counters.get(key, 0) + 1


def counters() -> Dict[str, int]:
    return dict(_counters)


# ---------------------------------------------------------------------------
# Planning — pure
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EntryPlan:
    pair: str
    symbol: str
    direction: str
    side: str            # "buy" | "sell"
    qty: float
    qty_str: str
    leverage: int
    sl: float
    sl_str: str
    tp: float
    tp_str: str
    live_price: float
    notional_usdt: float


@dataclass(frozen=True)
class Refusal:
    reason: str
    detail: str


def plan_entry(
    *,
    instrument: Optional[_inst.Instrument],
    symbol: str,
    direction: str,
    entry: float,
    sl: float,
    tp1: float,
    live_price: Optional[float],
    notional_usdt: float,
    requested_leverage: float,
    max_gap_pct: float,
    liquidation_stop_multiple: float,
) -> EntryPlan | Refusal:
    """Everything that decides whether and how big — no I/O."""
    if instrument is None:
        return Refusal("instrument_unavailable", f"{symbol} is not tradable on CoinDCX right now.")
    why = instrument.refusal()
    if why is not None:
        return Refusal(why, f"{instrument.pair} cannot take this order ({why}).")
    if direction not in ("LONG", "SHORT"):
        return Refusal("bad_direction", f"unknown direction {direction!r}")
    if not live_price or live_price <= 0:
        return Refusal("price_unavailable", "CoinDCX price is unavailable right now.")
    if entry <= 0 or sl <= 0 or tp1 <= 0:
        return Refusal("bad_levels", "The signal carries no usable entry, stop or target.")
    gap_pct = abs(live_price - entry) / entry * 100.0
    if gap_pct > max_gap_pct:
        return Refusal(
            "entry_gap",
            f"CoinDCX price {live_price:g} is {gap_pct:.2f}% from the signal entry "
            f"{entry:g} (limit {max_gap_pct:g}%).",
        )
    long = direction == "LONG"
    if long and not (sl < live_price < tp1):
        return Refusal("levels_crossed", "Price is already past the stop or the target.")
    if not long and not (tp1 < live_price < sl):
        return Refusal("levels_crossed", "Price is already past the stop or the target.")

    sl_r = _inst.round_price(sl, instrument.price_increment)
    tp_r = _inst.round_price(tp1, instrument.price_increment)
    if long and not (sl_r < live_price < tp_r):
        return Refusal("levels_crossed", "Stop or target collapses onto price at CoinDCX's tick.")
    if not long and not (tp_r < live_price < sl_r):
        return Refusal("levels_crossed", "Stop or target collapses onto price at CoinDCX's tick.")

    stop_frac = abs(live_price - sl_r) / live_price
    safe_lev = math.floor(1.0 / (liquidation_stop_multiple * stop_frac)) if stop_frac > 0 else 0
    leverage = int(min(
        math.floor(max(requested_leverage, 1.0)),
        math.floor(instrument.max_leverage(direction)),
        safe_lev,
    ))
    if leverage < 1:
        return Refusal(
            "stop_too_wide",
            f"The stop is {stop_frac * 100:.2f}% away — too wide for an isolated "
            f"position at any leverage.",
        )

    qty = _inst.round_qty_down(notional_usdt / live_price, instrument.quantity_increment)
    if qty <= 0 or qty < instrument.min_quantity or qty * live_price < instrument.min_notional:
        need = max(instrument.min_notional, instrument.min_quantity * live_price)
        return Refusal(
            "below_min_notional",
            f"Position size ${notional_usdt:.2f} is below CoinDCX's minimum for "
            f"{symbol} (about ${need:.2f}). Increase your position size in Settings.",
        )
    if instrument.max_market_order_quantity > 0 and qty > instrument.max_market_order_quantity:
        return Refusal(
            "above_max_market_qty",
            f"Size {qty:g} exceeds CoinDCX's maximum market order for {symbol}.",
        )
    return EntryPlan(
        pair=instrument.pair,
        symbol=symbol,
        direction=direction,
        side="buy" if long else "sell",
        qty=qty,
        qty_str=_inst.format_number(qty, instrument.quantity_increment),
        leverage=leverage,
        sl=sl_r,
        sl_str=_inst.format_number(sl_r, instrument.price_increment),
        tp=tp_r,
        tp_str=_inst.format_number(tp_r, instrument.price_increment),
        live_price=live_price,
        notional_usdt=qty * live_price,
    )


def _num(v: Any) -> float:
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def position_row(rows: list, pair: str, margin_currency: str) -> Optional[Dict[str, Any]]:
    for r in rows:
        if (
            r.get("pair") == pair
            and str(r.get("margin_currency_short_name") or "USDT").upper() == margin_currency
        ):
            return r
    return None


def row_is_flat(row: Optional[Dict[str, Any]]) -> bool:
    """No position and nothing resting — ``None`` (never traded) is flat."""
    if row is None:
        return True
    return (
        abs(_num(row.get("active_pos"))) == 0
        and _num(row.get("inactive_pos_buy")) == 0
        and _num(row.get("inactive_pos_sell")) == 0
    )


def duplicate_outcome(existing: "_pos.CoinDCXPosition") -> Dict[str, Any]:
    """Say what actually happened to this signal on CoinDCX, by state.

    One sentence ("already sent") used to cover five different worlds, two of
    which placed nothing at all.  The class stays ``AlreadyActive`` for a live
    record and ``AlreadyHandled`` for a finished one, so consumers keyed on
    those names are unchanged; only the sentence now tells the truth.
    """
    st = existing.state
    if st in (_pos.PENDING, _pos.ENTRY_UNCERTAIN):
        return _outcome(
            "rejected", "AlreadyActive",
            "Your earlier order for this signal is still being confirmed with "
            "CoinDCX. Check the Trade tab in a minute — do not place it again.",
        )
    if st in (_pos.OPEN, _pos.CLOSING):
        return _outcome(
            "rejected", "AlreadyActive",
            "This signal is already open on your CoinDCX account — see the "
            "Trade tab.",
        )
    if st == _pos.CLOSED:
        return _outcome(
            "rejected", "AlreadyHandled",
            "This signal already traded on your CoinDCX account and has closed.",
        )
    why = (existing.last_error or "").strip()
    return _outcome(
        "rejected", "AlreadyHandled",
        "CoinDCX refused this signal earlier, so nothing was placed"
        + (f" ({why[:160]})" if why else "")
        + ". Tap Take to try again.",
    )


def liquidation_inside_stop(direction: str, liquidation: float, sl: float) -> bool:
    """True when liquidation would be hit before the stop."""
    if liquidation <= 0:
        return False  # not reported (cross margin) — nothing to compare
    return liquidation >= sl if direction == "LONG" else liquidation <= sl


# ---------------------------------------------------------------------------
# Executor
# ---------------------------------------------------------------------------


ClientFactory = Callable[[str], _client.CoinDCXClient]


class CoinDCXExecutor:
    """Opens, protects, closes and records CoinDCX positions."""

    def __init__(
        self,
        *,
        store: Optional[_pos.CoinDCXPositionStore] = None,
        registry: Optional[_inst.InstrumentRegistry] = None,
        client_factory: Optional[ClientFactory] = None,
        sleep: Callable[[float], Any] = asyncio.sleep,
        fill_wait_s: Optional[float] = None,
    ) -> None:
        from config import COINDCX_FILL_WAIT_SEC

        self._store = store
        self._registry = registry
        self._client_factory = client_factory or (lambda uid: _client.CoinDCXClient(uid))
        self._sleep = sleep
        self._fill_wait_s = COINDCX_FILL_WAIT_SEC if fill_wait_s is None else fill_wait_s
        self._uid_locks: Dict[str, asyncio.Lock] = {}
        # (uid, signal_id) asked to close while the entry was still being
        # confirmed.  Honoured the moment the position is known to exist —
        # after the fill here, or when the reconciler adopts it.  In memory:
        # a restart loses it and the age cap is then the backstop.
        self._close_requested: Dict[tuple, str] = {}
        # signal_id → close reason, for signals the engine has closed.  The
        # router fans CoinDCX out in the background, so a signal can close
        # before a user's record exists; the entry is then refused, or exited
        # if it filled first.  Bounded; a restart forgets it (age cap backstop).
        self._closed_signals: "OrderedDict[str, str]" = OrderedDict()

    @property
    def store(self) -> _pos.CoinDCXPositionStore:
        return self._store or _pos.get_store()

    @property
    def registry(self) -> _inst.InstrumentRegistry:
        return self._registry or _inst.get_registry()

    def _lock(self, uid: str) -> asyncio.Lock:
        lock = self._uid_locks.get(uid)
        if lock is None:
            lock = self._uid_locks[uid] = asyncio.Lock()
        return lock

    async def _put(self, pos: _pos.CoinDCXPosition) -> None:
        await asyncio.to_thread(self.store.put, pos)

    # -- Open -------------------------------------------------------------

    async def open_position(
        self,
        *,
        uid: str,
        signal_id: str,
        symbol: str,
        direction: str,
        entry: float,
        sl: float,
        tp1: float,
        notional_usdt: float,
        margin_currency: str,
        leverage: float,
        source: str = "auto",
    ) -> Dict[str, Any]:
        """Open one user's position.  Returns an outcome dict, never raises."""
        async with self._lock(uid):
            try:
                return await self._open_locked(
                    uid=uid, signal_id=signal_id, symbol=symbol, direction=direction,
                    entry=entry, sl=sl, tp1=tp1, notional_usdt=notional_usdt,
                    margin_currency=margin_currency, leverage=leverage, source=source,
                )
            except Exception as exc:  # the fan-out must never see a raise
                _count("open_crashed")
                log.exception("coindcx open crashed uid={} signal={}", uid, signal_id)
                _fail_open("coindcx.execution.open", exc)
                return _outcome("rejected", "InternalError", f"{type(exc).__name__}")

    async def _open_locked(self, **kw: Any) -> Dict[str, Any]:
        from config import COINDCX_LIQUIDATION_STOP_MULTIPLE, COINDCX_MAX_ENTRY_GAP_PCT

        uid, signal_id, symbol = kw["uid"], kw["signal_id"], kw["symbol"]
        direction, margin = kw["direction"], kw["margin_currency"]

        if self.close_reason_for(uid, signal_id) is not None:
            _count("refused:signal_closed")
            return _outcome("rejected", "SignalClosed",
                            "This signal has already closed, so nothing was placed.")

        existing = await asyncio.to_thread(self.store.get, uid, signal_id)
        # A manual Take after a refusal is a fresh attempt: REJECTED means
        # CoinDCX placed nothing, so answering "already sent" would be false
        # and would block the signal for this user forever (owner, 2026-09-28:
        # PENGUUSDT "already sent" with nothing on the account).  The auto
        # fan-out never retries — a refusal there stays a refusal.
        retry = (
            existing is not None
            and existing.state == _pos.REJECTED
            and kw.get("source") == "manual_take"
        )
        if existing is not None and not retry:
            _count("skip_duplicate")
            return duplicate_outcome(existing)

        instrument = await self.registry.instrument(symbol, margin)
        live = await self.registry.last_price(symbol)
        plan = plan_entry(
            instrument=instrument, symbol=symbol, direction=direction,
            entry=kw["entry"], sl=kw["sl"], tp1=kw["tp1"], live_price=live,
            notional_usdt=kw["notional_usdt"], requested_leverage=kw["leverage"],
            max_gap_pct=COINDCX_MAX_ENTRY_GAP_PCT,
            liquidation_stop_multiple=COINDCX_LIQUIDATION_STOP_MULTIPLE,
        )
        if isinstance(plan, Refusal):
            _count(f"refused:{plan.reason}")
            return _outcome("rejected", _refusal_class(plan.reason), plan.detail, reason=plan.reason)

        client = self._client_factory(uid)

        # Invariant 2 — the pair must be flat on this margin currency.
        try:
            rows = await client.positions(pairs=[plan.pair], margin_currencies=(margin,))
        except _client.CoinDCXKeyError as exc:
            return self._key_refusal(exc)
        except (_client.CoinDCXRejected, _client.CoinDCXUnreachable) as exc:
            _count("refused:precheck_failed")
            return _outcome(
                "rejected", "PrecheckFailed",
                f"Could not confirm your CoinDCX {plan.pair} position is flat: {exc}",
            )
        if not row_is_flat(position_row(rows, plan.pair, margin)):
            _count("refused:pair_not_flat")
            return _outcome(
                "rejected", "PairNotFlat",
                f"You already hold a position or open order on {plan.pair} "
                f"({margin} margin). CoinDCX keeps one position per pair, so this "
                f"signal was not placed.",
            )

        # Invariant 3 — the record exists before the order does.
        rate = await self.registry.inr_per_usdt() if margin == "INR" else None
        pos = _pos.CoinDCXPosition(
            uid=uid, signal_id=signal_id, symbol=symbol, pair=plan.pair,
            side=direction, state=_pos.PENDING, margin_currency=margin,
            leverage=float(plan.leverage), qty=plan.qty, entry_target=kw["entry"],
            sl_price=plan.sl, tp_price=plan.tp, notional_usdt=plan.notional_usdt,
            conversion_price=float(rate or 0.0), source=kw.get("source", "auto"),
        )
        claim = self.store.reclaim_rejected if retry else self.store.insert_new
        if not await asyncio.to_thread(claim, pos):
            _count("skip_duplicate")
            again = await asyncio.to_thread(self.store.get, uid, signal_id)
            if again is not None:
                return duplicate_outcome(again)
            return _outcome("rejected", "AlreadyActive",
                            "This signal is already being placed on your CoinDCX account.")
        if retry:
            _count("manual_retry_after_reject")

        # Leverage first: CoinDCX refuses an order whose leverage differs from
        # the position's.  A refusal here means nothing was opened.
        try:
            await client.update_leverage(
                pair=plan.pair, leverage=plan.leverage, margin_currency=margin,
            )
        except Exception as exc:  # noqa: BLE001 — classified below
            return await self._entry_refused(pos, exc, stage="leverage")

        try:
            order = await client.market_order(
                pair=plan.pair, side=plan.side, quantity=plan.qty_str,
                leverage=plan.leverage, margin_currency=margin,
            )
            pos.entry_order_id = str(order.get("id") or "")
        except Exception as exc:  # noqa: BLE001
            if _client.definitely_not_executed(exc):
                return await self._entry_refused(pos, exc, stage="entry")
            # Unknown outcome: the order may exist.  The reconciler resolves
            # it from the exchange; nothing here may assume either way.
            pos.state = _pos.ENTRY_UNCERTAIN
            pos.last_error = f"entry outcome unknown: {exc}"[:500]
            await self._put(pos)
            _count("entry_uncertain")
            _record_breaker(uid, exc)
            return _outcome(
                "rejected", "EntryUncertain",
                "CoinDCX did not confirm the entry. We are checking your account "
                "and will protect the position if it opened.",
            )

        filled = await self._await_fill(client, pos)
        if filled is None:
            # Nothing appeared in time: cancel what may still rest, then look
            # once more — a late fill is adopted, never abandoned.
            if pos.entry_order_id:
                try:
                    await client.cancel_order(order_id=pos.entry_order_id)
                except Exception as exc:  # noqa: BLE001
                    log.info("coindcx cancel after no-fill: {}", exc)
            filled = await self._await_fill(client, pos, attempts=2)
        if filled is None:
            pos.state = _pos.ENTRY_UNCERTAIN
            pos.last_error = "entry fill not visible after wait"
            await self._put(pos)
            _count("entry_no_fill")
            return _outcome(
                "rejected", "EntryNotFilled",
                "CoinDCX did not fill the entry in time. Nothing is held; the "
                "reconciler will confirm.",
            )

        self._apply_fill(pos, filled)
        await self._put(pos)
        _count("entry_filled")
        await self.protect(pos, client=client)
        if pos.state == _pos.OPEN:
            await self.honour_close_request(pos, client)
            if pos.state != _pos.OPEN:
                return _outcome(
                    "rejected", "ClosedOnRequest",
                    "The signal closed while your entry was being placed, so the "
                    "position was closed straight away.",
                )
        if pos.state != _pos.OPEN:
            return _outcome(
                "rejected", pos.close_reason or "ProtectionFailed",
                "The entry filled but the stop could not be placed, so the "
                "position was closed immediately.",
            )
        _count("placed")
        return _outcome("placed", None, None, qty=pos.qty, pair=pos.pair,
                        leverage=pos.leverage, entry_filled=pos.entry_filled)

    async def _await_fill(
        self, client: _client.CoinDCXClient, pos: _pos.CoinDCXPosition, *,
        attempts: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        n = attempts if attempts is not None else max(1, int(self._fill_wait_s / 0.5))
        for _ in range(n):
            try:
                rows = await client.positions(
                    pairs=[pos.pair], margin_currencies=(pos.margin_currency,),
                )
            except Exception as exc:  # noqa: BLE001 — keep waiting
                log.debug("coindcx fill poll failed: {}", exc)
                rows = []
            row = position_row(rows, pos.pair, pos.margin_currency)
            active = _num((row or {}).get("active_pos"))
            if active != 0 and (active > 0) == (pos.side == "LONG"):
                return row
            await self._sleep(0.5)
        return None

    @staticmethod
    def _apply_fill(pos: _pos.CoinDCXPosition, row: Dict[str, Any]) -> None:
        pos.position_id = str(row.get("id") or "")
        pos.entry_filled = _num(row.get("avg_price")) or pos.entry_target
        pos.qty = abs(_num(row.get("active_pos"))) or pos.qty
        pos.liquidation_price = _num(row.get("liquidation_price"))
        pos.opened_at = time.time()
        conv = _num(row.get("settlement_currency_avg_price"))
        if conv > 0:
            pos.conversion_price = conv
        pos.state = _pos.OPEN

    async def _entry_refused(
        self, pos: _pos.CoinDCXPosition, exc: BaseException, *, stage: str,
    ) -> Dict[str, Any]:
        pos.state = _pos.REJECTED
        pos.last_error = f"{stage}: {exc}"[:500]
        pos.closed_at = time.time()
        await self._put(pos)
        _count(f"rejected:{stage}")
        if isinstance(exc, _client.CoinDCXKeyError):
            return self._key_refusal(exc)
        _record_breaker(pos.uid, exc)
        if isinstance(exc, _client.CoinDCXRejected):
            msg = exc.exchange_message or str(exc)
            cls = "InsufficientMargin" if "insufficient" in msg.lower() else "OrderRejectedByCoinDCX"
            return _outcome("rejected", cls, f"CoinDCX refused the {stage}: {msg}")
        return _outcome("rejected", type(exc).__name__, f"CoinDCX {stage} failed: {exc}")

    @staticmethod
    def _key_refusal(exc: _client.CoinDCXKeyError) -> Dict[str, Any]:
        _count(f"refused:key:{exc.code}")
        detail = {
            "KEY_NOT_ATTESTED": "Reconnect your CoinDCX key and confirm the safety checklist.",
            "KEY_BLOB_NOT_FOUND": "Connect your CoinDCX API key in Settings.",
        }.get(exc.code, "Your CoinDCX key could not be used — reconnect it in Settings.")
        return _outcome("rejected", "CoinDCXKeyProblem", detail)

    # -- Protect ----------------------------------------------------------

    async def protect(
        self, pos: _pos.CoinDCXPosition, *, client: Optional[_client.CoinDCXClient] = None,
    ) -> None:
        """Place the position-level stop (and TP1).  Invariant 1 lives here.

        Called after a fill and by the reconciler whenever a live position is
        found without a resting stop.  Ends in exactly one of: stop resting
        (``OPEN``), exited (``CLOSED``), or exit also failed (``OPEN`` with
        ``sl_resting = False`` — retried next cycle, loudly).
        """
        client = client or self._client_factory(pos.uid)

        # Invariant 4 — liquidation must not come before the stop.
        if liquidation_inside_stop(pos.side, pos.liquidation_price, pos.sl_price):
            _count("liquidation_inside_stop")
            await self._exit(pos, client, CLOSE_LIQUIDATION_INSIDE_STOP,
                             note=f"liquidation {pos.liquidation_price:g} inside stop {pos.sl_price:g}")
            return

        inst = await self.registry.instrument(pos.symbol, pos.margin_currency)
        tick = inst.price_increment if inst else 0.0
        sl_str = _inst.format_number(pos.sl_price, tick) if tick else repr(pos.sl_price)
        tp_str = _inst.format_number(pos.tp_price, tick) if tick else repr(pos.tp_price)

        # The reconciler sets ``sl_resting`` from the exchange's own trigger.
        # When the stop already rests, this call is a target repair, and a
        # failure must leave a protected position alone — exiting it would
        # turn a missing take-profit into a forced close.
        stop_already_resting = pos.sl_resting

        last_err = ""
        for attempt in range(2):
            try:
                result = await client.create_tpsl(
                    position_id=pos.position_id, stop_price=sl_str,
                    take_profit_price=None if pos.tp_resting else tp_str,
                )
            except Exception as exc:  # noqa: BLE001
                last_err = str(exc)
                await self._sleep(0.5)
                continue
            sl_ok, sl_id, sl_err = _client.tpsl_leg(result, "stop_loss")
            tp_ok, tp_id, tp_err = _client.tpsl_leg(result, "take_profit")
            if tp_ok:
                pos.tp_resting, pos.tp_order_id = True, tp_id
            if sl_ok or "already exists" in sl_err.lower():
                pos.sl_resting = True
                if sl_id:
                    pos.sl_order_id = sl_id
                if not pos.tp_resting and "already exists" in tp_err.lower():
                    pos.tp_resting = True
                pos.last_error = "" if pos.tp_resting else f"take profit not placed: {tp_err}"
                pos.state = _pos.OPEN
                await self._put(pos)
                _count("protected" if pos.tp_resting else "protected_sl_only")
                return
            last_err = sl_err
            await self._sleep(0.5)

        if stop_already_resting:
            _count("tp_repair_failed")
            pos.last_error = f"take profit not placed: {last_err}"[:500]
            pos.state = _pos.OPEN
            await self._put(pos)
            return
        _count("stop_refused")
        await self._exit(pos, client, CLOSE_PROTECTION_FAILED, note=f"stop refused: {last_err}")

    # -- Close ------------------------------------------------------------

    async def honour_close_request(
        self, pos: _pos.CoinDCXPosition, client: _client.CoinDCXClient,
    ) -> None:
        """Exit ``pos`` if a close was asked for while its entry was unresolved."""
        reason = self._close_requested.pop((pos.uid, pos.signal_id), None)
        if reason is None:
            reason = self.close_reason_for(pos.uid, pos.signal_id)
        if reason is None or pos.state != _pos.OPEN:
            return
        _count("close_request_honoured")
        await self._exit(pos, client, CLOSE_EXIT, note=f"{reason} (requested during entry)")

    _CLOSED_SIGNALS_MAX = 5000

    def mark_signal_closed(self, signal_id: str, reason: str) -> None:
        self._closed_signals[signal_id] = reason
        self._closed_signals.move_to_end(signal_id)
        while len(self._closed_signals) > self._CLOSED_SIGNALS_MAX:
            self._closed_signals.popitem(last=False)

    def close_reason_for(self, uid: str, signal_id: str) -> Optional[str]:
        """Why this user's position on ``signal_id`` must close, or ``None``.

        ``invalidated`` spares users on the loose invalidation mode, exactly
        as :func:`dispatch.close_positions_for_signal` does.
        """
        reason = self._closed_signals.get(signal_id)
        if reason == "invalidated":
            try:
                from src.api import user_overrides as _uo

                if _uo.resolve_invalidation_mode_uid(uid, "standard") == "loose":
                    return None
            except Exception as exc:  # noqa: BLE001 — unknown mode: close
                _fail_open("coindcx.execution.invalidation_mode", exc)
        return reason

    def forget_close_request(self, uid: str, signal_id: str) -> None:
        self._close_requested.pop((uid, signal_id), None)

    async def close_position(
        self, uid: str, signal_id: str, *, reason: str,
    ) -> Dict[str, Any]:
        """Exit one user's position at market (signal closed, user tapped
        Close, age cap).  Idempotent: a closed or missing record is a no-op."""
        async with self._lock(uid):
            pos = await asyncio.to_thread(self.store.get, uid, signal_id)
            if pos is None:
                return _outcome("rejected", "PositionNotFound",
                                "No CoinDCX position of yours is open on this signal.")
            if not pos.live:
                return _outcome("closed", None, None, already=True)
            if pos.state in (_pos.PENDING, _pos.ENTRY_UNCERTAIN) or not pos.position_id:
                # Recorded, not dropped: the moment the entry is confirmed
                # (fill seen here, or adopted by the reconciler) it is exited.
                # This sentence used to promise that and nothing did it.
                self._close_requested[(uid, signal_id)] = reason
                _count("close_requested_during_entry")
                return _outcome(
                    "rejected", "EntryUnresolved",
                    "The entry is still being confirmed; it will be closed as "
                    "soon as CoinDCX confirms it.",
                )
            client = self._client_factory(uid)
            await self._exit(pos, client, CLOSE_EXIT, note=reason)
            if pos.state == _pos.CLOSED:
                return _outcome("closed", None, None, exit_price=pos.exit_price)
            return _outcome(
                "rejected", "ExitPending",
                "CoinDCX did not confirm the exit yet. Your stop is still in "
                "place and we will retry.",
            )

    async def _exit(
        self, pos: _pos.CoinDCXPosition, client: _client.CoinDCXClient, reason: str,
        *, note: str = "",
    ) -> None:
        pos.state = _pos.CLOSING
        pos.close_reason = reason
        pos.last_error = note[:500]
        await self._put(pos)
        try:
            await client.exit_position(position_id=pos.position_id)
        except Exception as exc:  # noqa: BLE001
            # The engine's backstop close and CoinDCX's own TP/SL often land
            # together: an exit refused because the pair is already flat is a
            # close that already happened, not a failure.
            try:
                rows = await client.positions(
                    pairs=[pos.pair], margin_currencies=(pos.margin_currency,),
                )
                flat_row = position_row(rows, pos.pair, pos.margin_currency)
            except Exception:  # noqa: BLE001
                flat_row = None
            if flat_row is not None and _num(flat_row.get("active_pos")) == 0:
                await self.finalize_closed(pos, client, forced_reason=reason)
                return
            _count("exit_failed")
            pos.last_error = f"{note} | exit failed: {exc}"[:500]
            # Back to OPEN so the reconciler re-examines it every cycle.
            pos.state = _pos.OPEN
            await self._put(pos)
            _fail_open("coindcx.execution.exit", exc)
            return
        for _ in range(max(1, int(self._fill_wait_s / 0.5))):
            try:
                rows = await client.positions(
                    pairs=[pos.pair], margin_currencies=(pos.margin_currency,),
                )
            except Exception:  # noqa: BLE001
                rows = []
            row = position_row(rows, pos.pair, pos.margin_currency)
            if row is not None and _num(row.get("active_pos")) == 0:
                await self.finalize_closed(pos, client, forced_reason=reason)
                return
            await self._sleep(0.5)
        # Exit sent but not yet visible — CLOSING stays; reconciler finishes it.

    async def finalize_closed(
        self, pos: _pos.CoinDCXPosition, client: _client.CoinDCXClient,
        *, forced_reason: Optional[str] = None,
    ) -> None:
        """The exchange shows the pair flat — record why, at what price, and
        clear anything still resting against the position."""
        exit_side = "sell" if pos.side == "LONG" else "buy"
        entry_side = "buy" if pos.side == "LONG" else "sell"
        since_ms = (pos.opened_at or pos.created_at) * 1000.0 - 1000.0

        # Price and fees come from the pair's own fills — a pair-scoped query.
        # The order list (needed only for the stage: stop, target or
        # liquidation) is account-wide with no pair filter, so it is paged;
        # reading page 1 alone missed the exit on any busy account and
        # recorded the close as EXTERNAL with no price, PnL or fees.
        fills: list = []
        try:
            fills = await client.trades(
                pair=pos.pair, from_date=_utc_date(since_ms / 1000.0),
                to_date=_utc_date(time.time()), margin_currencies=(pos.margin_currency,),
            )
        except Exception as exc:  # noqa: BLE001 — fall back to the orders
            _count("close_trades_lookup_failed")
            log.info("coindcx close trades lookup failed uid={} {}", pos.uid, exc)
        mine = [
            f for f in fills
            if f.get("pair") == pos.pair and _num(f.get("timestamp")) >= since_ms
        ]
        exit_fills = [f for f in mine if f.get("side") == exit_side]
        entry_fills = [
            f for f in mine if f.get("side") == entry_side
            and (not pos.entry_order_id or str(f.get("order_id")) == pos.entry_order_id)
        ]
        exit_ids = {str(f.get("order_id")) for f in exit_fills if f.get("order_id")}

        exit_order = entry_order = None
        try:
            exit_order = await _find_order(client, exit_side, pos, since_ms, exit_ids)
            if pos.entry_order_id and not entry_fills:
                entry_order = await _find_order(
                    client, entry_side, pos, since_ms, {pos.entry_order_id},
                )
        except Exception as exc:  # noqa: BLE001 — record what we know
            log.info("coindcx close lookup failed uid={} {}", pos.uid, exc)

        classified = _classify_exit(exit_order, pos)
        # The exchange's own stop, target or liquidation is the truth about
        # why the position is flat, even when we had also asked to exit.
        if classified in (CLOSE_SL, CLOSE_TP1, CLOSE_LIQUIDATED):
            reason = classified
        else:
            reason = forced_reason or classified
        exit_px = _vwap(exit_fills) or _num((exit_order or {}).get("avg_price"))
        pos.exit_price = exit_px
        if exit_px > 0 and pos.entry_filled > 0:
            pos.realized_pnl_usdt = round(
                (exit_px - pos.entry_filled) * pos.qty * pos.direction_sign, 8,
            )
        exit_fee = (
            sum(_num(f.get("fee_amount")) for f in exit_fills) if exit_fills
            else _num((exit_order or {}).get("fee_amount"))
        )
        entry_fee = (
            sum(_num(f.get("fee_amount")) for f in entry_fills) if entry_fills
            else _num((entry_order or {}).get("fee_amount"))
        )
        known = exit_fills or entry_fills or exit_order or entry_order
        pos.fees_usdt = round(exit_fee + entry_fee, 8) if known else None
        if exit_px <= 0:
            _count("close_exit_price_unknown")
        pos.close_reason = reason
        pos.state = _pos.CLOSED
        pos.closed_at = time.time()
        pos.sl_resting = pos.tp_resting = False
        await self._put(pos)
        _count(f"closed:{reason}")
        if pos.position_id:
            try:
                await client.cancel_all_for_position(position_id=pos.position_id)
            except Exception as exc:  # noqa: BLE001 — nothing may be resting
                log.debug("coindcx cancel_all after close: {}", exc)


#: Pages of the account-wide order list read to find one order (50 per page).
_ORDER_PAGES = 4


async def _find_order(
    client: _client.CoinDCXClient, side: str, pos: _pos.CoinDCXPosition,
    since_ms: float, ids: set,
) -> Optional[Dict[str, Any]]:
    """The order with an id in ``ids`` — or, with no ids, the newest one on
    this pair since ``since_ms`` — paging the newest-first list.  Stops at
    the first page that is short or reaches back before ``since_ms``."""
    seen: list = []
    size = 50
    for page in range(1, _ORDER_PAGES + 1):
        rows = await client.orders(statuses="filled", side=side, size=size, page=page)
        if ids:
            hit = next((o for o in rows if str(o.get("id")) in ids), None)
            if hit is not None:
                return hit
        seen.extend(rows)
        stamps = [_num(o.get("updated_at")) for o in rows]
        if len(rows) < size or (stamps and min(stamps) < since_ms):
            break
    else:
        _count("close_order_lookup_page_cap")
    if ids:
        _count("close_order_id_not_found")
    return _latest_exit_order(seen, pos)


def _vwap(fills: list) -> float:
    qty = sum(abs(_num(f.get("quantity"))) for f in fills)
    if qty <= 0:
        return 0.0
    return sum(_num(f.get("price")) * abs(_num(f.get("quantity"))) for f in fills) / qty


def _utc_date(ts: float) -> str:
    return time.strftime("%Y-%m-%d", time.gmtime(ts))


def _latest_exit_order(orders: list, pos: _pos.CoinDCXPosition) -> Optional[Dict[str, Any]]:
    since_ms = (pos.opened_at or pos.created_at) * 1000.0 - 1000.0
    mine = [
        o for o in orders
        if o.get("pair") == pos.pair
        and str(o.get("margin_currency_short_name") or "USDT").upper() == pos.margin_currency
        and _num(o.get("updated_at")) >= since_ms
    ]
    mine.sort(key=lambda o: _num(o.get("updated_at")), reverse=True)
    return mine[0] if mine else None


def _classify_exit(order: Optional[Dict[str, Any]], pos: _pos.CoinDCXPosition) -> str:
    if order is None:
        return CLOSE_EXTERNAL
    stage = str(order.get("stage") or "")
    if stage == "liquidate":
        return CLOSE_LIQUIDATED
    if stage == "tpsl_exit":
        trigger = _num(order.get("stop_price"))
        if trigger > 0:
            d_sl = abs(trigger - pos.sl_price)
            d_tp = abs(trigger - pos.tp_price)
            return CLOSE_SL if d_sl <= d_tp else CLOSE_TP1
        return CLOSE_EXTERNAL
    if stage == "exit":
        return CLOSE_EXIT
    return CLOSE_EXTERNAL


def _refusal_class(reason: str) -> str:
    return {
        "below_min_notional": "NotionalTooSmall",
        "instrument_unavailable": "SymbolNotOnCoinDCX",
        "entry_gap": "PriceGapTooLarge",
        "levels_crossed": "PriceMovedPastLevel",
        "stop_too_wide": "StopTooWide",
        "price_unavailable": "PriceUnavailable",
    }.get(reason, "InstrumentUnavailable")


def _outcome(outcome: str, reject_class: Optional[str], detail: Optional[str], **extra: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {"outcome": outcome, "venue": VENUE}
    if reject_class:
        out["reject_class"] = reject_class
    if detail:
        out["reject_detail"] = detail
    out.update(extra)
    return out


def _record_breaker(uid: str, exc: BaseException) -> None:
    """Feed a failure to the per-user breaker and the CoinDCX venue breaker.

    Never to the shared global breaker: its trip engages the global kill
    switch, so a CoinDCX outage used to halt every Binance user too.
    User-setup refusals (funds, size) count nowhere.
    """
    if isinstance(exc, _client.CoinDCXRejected) and exc.user_setup:
        return
    try:
        from src.execution import order_placer as _op
        from src.execution import tripwires as _tw

        _tw.record_order_placement_failure(
            firebase_uid=uid, exc=exc, count_global=False,  # type: ignore[arg-type]
        )
        if isinstance(exc, _op.OrderPlacementError):
            from src.venues.coindcx import breaker as _br

            _br.get_breaker().record_failure(exc)
    except Exception:  # pragma: no cover
        log.exception("coindcx: breaker record failed")


def _fail_open(site: str, exc: BaseException) -> None:
    try:
        from src import fail_open as _fo

        _fo.record(site, exc)
    except Exception:  # pragma: no cover
        pass


_EXECUTOR: Optional[CoinDCXExecutor] = None


def get_executor() -> CoinDCXExecutor:
    global _EXECUTOR
    if _EXECUTOR is None:
        _EXECUTOR = CoinDCXExecutor()
    return _EXECUTOR


def set_executor_for_test(ex: Optional[CoinDCXExecutor]) -> None:
    global _EXECUTOR
    _EXECUTOR = ex
