"""What Binance says the account actually holds, per user.

Owner, 2026-09-01, holding the Binance app beside the Trade tab: *"there we
have to show exactly how live open traded position shows in binance"*.

**Everything this module needs was already arriving and being thrown away.**
``events.parse_event`` has decoded ``ACCOUNT_UPDATE`` into a typed
:class:`~src.execution.events.AccountUpdatePosition` — signed size, entry
price, unrealized PnL, margin type, isolated wallet — since the user-data
stream shipped, and ``grep`` for a consumer returned nothing: ``PositionFSM``
no-ops every event that is not an ``ORDER_TRADE_UPDATE``, and its docstring
says so.  Separately, ``reconciler._fetch_binance_positions`` calls
``/fapi/v2/positionRisk`` on every cycle and keeps ``positionAmt``, discarding
``liquidationPrice``, ``leverage``, ``markPrice``, ``unRealizedProfit`` and the
rest of the row.  A field one side writes and no side reads, twice over —
which is why the first cut of the position card had to infer a position the
exchange was describing for free.

So this is not a new data source.  It is the reader for two that already
exist, and it adds no subscription, no poll and no vendor round trip.

Two writers, deliberately kept apart because they are on different clocks and
have different authority:

* :func:`apply_account_update` — the exchange PUSHING, sub-second, on every
  change.  Authoritative for size, entry, realized and unrealized PnL, margin
  type.  This is what makes the card live.
* :func:`apply_position_risk` — the reconciler's existing REST row, ~1/cycle.
  It is the ONLY source of ``liquidation_price`` and ``leverage`` (they are
  not in the push), and it re-confirms the rest.

Each field therefore carries the age of the source that set it, because a
single "as of" over two clocks is the defect this repo has paid for on
`/signals/sar-live` and `/truth`: a page cannot grade freshness it did not
measure.  :meth:`ExchangePosition.age_sec` answers per source.

**A flat position is a fact, not an absence.**  Binance pushes
``position_amount == 0`` when a position closes, and that is the single most
useful frame this module receives: it is the exchange saying "you are out",
which is exactly the state the app's Trade tab could not distinguish from
"the engine has not told us anything yet".  A zero is therefore RECORDED with
its timestamp and kept briefly, not dropped — see :data:`_FLAT_RETAIN_SEC`.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.utils import get_logger

log = get_logger("execution.exchange_positions")

#: How long a position the exchange has reported FLAT is retained.
#:
#: Not zero, and the reason is the owner's actual complaint.  The engine
#: force-closes a position at two hours while its signal runs on, so the app
#: showed an ACTIVE signal over an empty Trade tab with nothing anywhere
#: joining the two.  Keeping the flat frame briefly lets the card say "Binance
#: closed this at 14:32" instead of rendering the same blank it renders when
#: nothing was ever placed.  Bounded because this is memory, not a ledger --
#: the durable record of a close is the position document.
_FLAT_RETAIN_SEC: float = 900.0

#: A per-source reading older than this is reported as stale rather than
#: served as current.  Generous against the reconciler's cycle, because the
#: REST half legitimately updates slowly; the PUSH half updates on change and
#: may correctly be old on a quiet position, which is why staleness is
#: reported per source and never collapsed into one verdict.
_STALE_AFTER_SEC: float = 600.0


@dataclass
class ExchangePosition:
    """One symbol, as the exchange describes it.

    Field provenance is not cosmetic here — ``liquidation_price`` can only
    come from REST and ``unrealized_pnl`` only usefully from the push, so a
    reader that treats them as equally fresh will eventually quote a
    liquidation price from before the position was resized.
    """

    symbol: str
    #: Signed: positive LONG, negative SHORT, 0.0 flat.
    position_amount: float = 0.0
    entry_price: float = 0.0
    #: Binance's OWN unrealized PnL, as of the last push. Between pushes the
    #: mark moves and this does not, which is why the app recomputes from a
    #: live mark against this entry and size rather than rendering this
    #: directly -- see the endpoint. Kept because a divergence between the
    #: two is the signal that our mark or our arithmetic is wrong.
    unrealized_pnl: float = 0.0
    accumulated_realized_pnl: float = 0.0
    margin_type: str = ""
    isolated_wallet: float = 0.0

    #: REST-only, from positionRisk. 0.0 means "not reported yet", which is a
    #: different fact from "no liquidation risk" and is rendered as such.
    liquidation_price: float = 0.0
    leverage: float = 0.0
    mark_price_rest: float = 0.0
    notional_rest: float = 0.0

    #: Monotonic stamps, per source. Never one shared "updated_at".
    pushed_at: Optional[float] = None
    rest_at: Optional[float] = None
    #: Wall-clock of the transition to flat, for the app's "closed at" copy.
    flat_since: Optional[float] = None

    def is_open(self) -> bool:
        return abs(self.position_amount) > 1e-12

    def side(self) -> str:
        if self.position_amount > 1e-12:
            return "LONG"
        if self.position_amount < -1e-12:
            return "SHORT"
        return "FLAT"

    def age_sec(self) -> Dict[str, Optional[float]]:
        """``{"push": s|None, "rest": s|None}`` — per source, never pooled."""
        now = time.monotonic()
        return {
            "push": None if self.pushed_at is None else now - self.pushed_at,
            "rest": None if self.rest_at is None else now - self.rest_at,
        }

    def to_row(self) -> Dict[str, Any]:
        """The wire shape. Absent readings are ``None``, never ``0.0``.

        A liquidation price of zero renders as "you cannot be liquidated",
        which is a claim nobody made; the exchange simply has not told us yet
        (Binance sends "0" for a cross position with no liquidation in range,
        and sends nothing at all before the first REST cycle -- two states
        that must not become one).
        """
        ages = self.age_sec()
        return {
            "symbol": self.symbol,
            "side": self.side(),
            "position_amount": self.position_amount,
            "entry_price": self.entry_price or None,
            "exchange_unrealized_pnl": (
                self.unrealized_pnl if self.pushed_at is not None else None
            ),
            "accumulated_realized_pnl": self.accumulated_realized_pnl,
            "margin_type": self.margin_type or None,
            "isolated_wallet": self.isolated_wallet or None,
            "liquidation_price": self.liquidation_price or None,
            "leverage": self.leverage or None,
            "mark_price_rest": self.mark_price_rest or None,
            "notional_rest": self.notional_rest or None,
            "push_age_sec": (
                None if ages["push"] is None else round(ages["push"], 1)
            ),
            "rest_age_sec": (
                None if ages["rest"] is None else round(ages["rest"], 1)
            ),
            "push_stale": (
                None if ages["push"] is None
                else ages["push"] > _STALE_AFTER_SEC
            ),
            "is_open": self.is_open(),
            "flat_since_epoch": self.flat_since,
        }


# uid -> symbol -> ExchangePosition. Guarded by a plain lock: writes arrive on
# the per-user worker task and reads on the snapshot writer's, so this is
# genuinely concurrent, and the map is small enough that a lock costs nothing.
_positions: Dict[str, Dict[str, ExchangePosition]] = {}
_lock = threading.RLock()

#: Bumped on every mutation. A reader that has seen this generation knows
#: nothing has changed -- the same invalidation-gated pattern
#: ``position_state.get_write_generation`` uses, so the snapshot writer can
#: skip republishing an unchanged book instead of writing on a timer.
_generation: int = 0

_counts: Dict[str, int] = {
    "account_updates": 0,
    "position_frames": 0,
    "rest_rows": 0,
    "opened": 0,
    "went_flat": 0,
    "evicted_flat": 0,
}


def get_generation() -> int:
    with _lock:
        return _generation


def counters() -> Dict[str, int]:
    with _lock:
        return dict(_counts)


def _bump() -> None:
    global _generation
    _generation += 1


def apply_account_update(firebase_uid: str, event: Any) -> None:
    """Absorb one ``ACCOUNT_UPDATE`` frame — the exchange's own push.

    Called from the per-user position worker.  Never raises: this is a
    measurement path riding the same socket that drives the FSM, and a bad
    frame must not cost a fill event.
    """
    try:
        _apply_account_update_inner(firebase_uid, event)
    except Exception:
        log.exception(
            "exchange_positions: ACCOUNT_UPDATE apply failed uid={}",
            firebase_uid,
        )


def _apply_account_update_inner(firebase_uid: str, event: Any) -> None:
    frames = list(getattr(event, "positions", ()) or ())
    now = time.monotonic()
    with _lock:
        _counts["account_updates"] += 1
        if not frames:
            # A balance-only update (funding, deposit). Nothing to record; NOT
            # an assertion that the account is flat.
            return
        book = _positions.setdefault(firebase_uid, {})
        for frame in frames:
            symbol = str(getattr(frame, "symbol", "") or "").upper()
            if not symbol:
                continue
            # Binance sends a row per position SIDE. In one-way mode that is
            # "BOTH"; in hedge mode "LONG"/"SHORT" arrive separately and would
            # overwrite each other under one symbol key. This engine trades
            # one-way only (place_signal never sends positionSide), so a
            # non-BOTH frame is not ours to interpret -- skipped and counted
            # rather than merged into a number that would be wrong.
            pos_side = str(getattr(frame, "position_side", "BOTH") or "BOTH")
            if pos_side.upper() not in ("BOTH", ""):
                continue
            _counts["position_frames"] += 1
            amount = float(getattr(frame, "position_amount", 0.0) or 0.0)
            row = book.get(symbol)
            if row is None:
                row = ExchangePosition(symbol=symbol)
                book[symbol] = row
            was_open = row.is_open()
            row.position_amount = amount
            row.entry_price = float(getattr(frame, "entry_price", 0.0) or 0.0)
            row.unrealized_pnl = float(
                getattr(frame, "unrealized_pnl", 0.0) or 0.0
            )
            row.accumulated_realized_pnl = float(
                getattr(frame, "accumulated_realized_pnl", 0.0) or 0.0
            )
            row.margin_type = str(getattr(frame, "margin_type", "") or "")
            row.isolated_wallet = float(
                getattr(frame, "isolated_wallet", 0.0) or 0.0
            )
            row.pushed_at = now
            now_open = row.is_open()
            if now_open:
                row.flat_since = None
                if not was_open:
                    _counts["opened"] += 1
            else:
                # The exchange saying "you are out". The most useful frame
                # this module gets -- see the module docstring.
                #
                # `flat_since` is stamped whenever the row is flat and does
                # not already carry one, NOT only on the open->flat
                # transition. A row whose FIRST frame is flat is the ordinary
                # case after an engine restart (the position closed while we
                # were down), and stamping only on the transition left it with
                # `flat_since = None` -- which the evictor reads as "not yet
                # flat" and keeps forever. A retain window that a whole class
                # of rows never enters is not a bound.
                if row.flat_since is None:
                    row.flat_since = time.time()
                if was_open:
                    _counts["went_flat"] += 1
                    log.info(
                        "exchange_positions: {} went FLAT on Binance uid={} "
                        "(realized total {:.4f})",
                        symbol, firebase_uid, row.accumulated_realized_pnl,
                    )
        _bump()
        _evict_stale_flats_locked(book)


def apply_position_risk(firebase_uid: str, rows: List[Dict[str, Any]]) -> None:
    """Absorb the reconciler's ``positionRisk`` response.

    The REST row is the only place ``liquidationPrice`` and ``leverage``
    exist, and it also re-confirms size and entry -- so it is applied to those
    too, but ONLY when no push has landed since, because the push is fresher
    by construction and overwriting it with a REST snapshot would walk a live
    number backwards.
    """
    try:
        _apply_position_risk_inner(firebase_uid, rows)
    except Exception:
        log.exception(
            "exchange_positions: positionRisk apply failed uid={}",
            firebase_uid,
        )


def _num(d: Dict[str, Any], key: str) -> float:
    raw = d.get(key)
    if raw is None or raw == "":
        return 0.0
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def _apply_position_risk_inner(
    firebase_uid: str, rows: List[Dict[str, Any]]
) -> None:
    now = time.monotonic()
    with _lock:
        book = _positions.setdefault(firebase_uid, {})
        for entry in rows:
            if not isinstance(entry, dict):
                continue
            symbol = str(entry.get("symbol", "") or "").upper()
            if not symbol:
                continue
            amount = _num(entry, "positionAmt")
            row = book.get(symbol)
            if row is None:
                if abs(amount) <= 1e-12:
                    # Binance returns a row for every symbol on the account,
                    # nearly all flat. Recording those would grow this map to
                    # the size of the exchange for no reader.
                    continue
                row = ExchangePosition(symbol=symbol)
                book[symbol] = row
            _counts["rest_rows"] += 1
            # REST-only fields, always applied.
            row.liquidation_price = _num(entry, "liquidationPrice")
            row.leverage = _num(entry, "leverage")
            row.mark_price_rest = _num(entry, "markPrice")
            row.notional_rest = abs(_num(entry, "notional"))
            row.rest_at = now
            # Shared fields: only when REST is the fresher of the two.
            if row.pushed_at is None or row.pushed_at <= now - 1.0:
                was_open = row.is_open()
                row.position_amount = amount
                entry_px = _num(entry, "entryPrice")
                if entry_px:
                    row.entry_price = entry_px
                if not row.margin_type:
                    row.margin_type = str(entry.get("marginType", "") or "")
                if not row.is_open() and row.flat_since is None:
                    row.flat_since = time.time()
                    if was_open:
                        _counts["went_flat"] += 1
        _bump()
        _evict_stale_flats_locked(book)


def _evict_stale_flats_locked(book: Dict[str, ExchangePosition]) -> None:
    """Drop flat rows past :data:`_FLAT_RETAIN_SEC`. Caller holds the lock."""
    if not book:
        return
    now = time.time()
    doomed = [
        sym for sym, row in book.items()
        if not row.is_open()
        and row.flat_since is not None
        and now - row.flat_since > _FLAT_RETAIN_SEC
    ]
    for sym in doomed:
        book.pop(sym, None)
        _counts["evicted_flat"] += 1


def for_user(firebase_uid: str) -> Dict[str, Dict[str, Any]]:
    """``{symbol: row}`` for one user. Empty when we are tracking nothing.

    Note what an empty answer does NOT mean: it is not "the account is flat".
    It is "this process has received nothing about this user" — before the
    first frame, after a restart, or for a user whose worker is not running.
    The endpoint says which, because a reader who cannot tell those apart will
    read a cold engine as a closed position.
    """
    with _lock:
        book = _positions.get(firebase_uid) or {}
        return {sym: row.to_row() for sym, row in book.items()}


def snapshot_all() -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Every tracked user, for the snapshot writer."""
    with _lock:
        return {
            uid: {sym: row.to_row() for sym, row in book.items()}
            for uid, book in _positions.items()
            if book
        }


def tracked_users() -> int:
    with _lock:
        return sum(1 for book in _positions.values() if book)


def forget_user(firebase_uid: str) -> None:
    """Drop a user's book — called when their worker stops, so a disconnected
    account stops being described as though we were still watching it."""
    with _lock:
        if _positions.pop(firebase_uid, None) is not None:
            _bump()


def reset_for_test() -> None:
    global _generation
    with _lock:
        _positions.clear()
        _generation = 0
        for k in _counts:
            _counts[k] = 0
