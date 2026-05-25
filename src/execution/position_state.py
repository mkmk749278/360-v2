"""Firestore-backed per-user-per-signal position state.

One document per open position at ``users/{firebase_uid}/positions/{signal_id}``.
Stored fields are the FSM's authoritative state: which orders are
open, which have filled, how much has been filled, what the next
expected transition is.

The Lumin app reads this collection (PR-3 security rules allow owner
read) to render the live-position view.  The engine writes via the
Firebase Admin SDK; Firestore Security Rules deny client write.

Document shape (Firestore ``users/{firebase_uid}/positions/{signal_id}``):

    {
      "signal_id": str,                 # matches the document id
      "firebase_uid": str,
      "symbol": str,                    # e.g. "BTCUSDT"
      "side": str,                      # "LONG" | "SHORT"
      "state": str,                     # FSM state — see PositionState enum
      "entry_price_target": float,      # what the signal said
      "entry_price_filled": float,      # average filled price (after entry)
      "sl_price": float,                # current SL price (moves on BE shift in PR-7)
      "tp1_price": float,
      "tp2_price": float,
      "tp3_price": float,
      "total_qty": float,               # entry size
      "tp1_qty": float,                 # how much closes on TP1
      "tp2_qty": float,
      "tp3_qty": float,
      "filled_qty": float,              # cumulative fill on the entry
      "closed_qty": float,              # cumulative close from TPs / SL / pre-TP partial
      "entry_order_id": int,            # Binance order id
      "sl_order_id": int,
      "tp1_order_id": int,
      "tp2_order_id": int,
      "tp3_order_id": int,
      "created_at": Timestamp,
      "last_event_at": Timestamp,
      "closed_at": Timestamp | None,
      "close_reason": str,              # "SL" | "TP1" | "TP2" | "TP3" | "MANUAL" | ""
      "realized_pnl_total": float,
    }

This module is **CRUD only** — the FSM transition logic lives in
:mod:`src.execution.position_fsm`.
"""

from __future__ import annotations

import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from src.utils import get_logger

log = get_logger("execution.position_state")


class PositionState(str, Enum):
    """FSM states for a per-user-per-signal position.

    Inherits from ``str`` so Firestore stores the enum as its string
    value automatically (no custom serialiser needed).

    Allowed transitions are pinned in :mod:`src.execution.position_fsm`.
    """

    # Entry order placed, no fills yet.  Brief — entry is MARKET so it
    # typically fills within 1 second of placement.
    PENDING = "PENDING"

    # Entry filled, SL + TPs active, no take-profits hit yet.  The
    # "long tail" of a position's lifetime — minutes to hours.
    OPEN = "OPEN"

    # Pre-TP partial close fired (per §3.2a doctrine).  The user has
    # banked profit on ``pretp_fraction`` of the position; SL has
    # moved to entry price (BE shift); residual rides toward TP1
    # OR closes flat at the BE-SL if reversed.  Most signals end
    # their lifecycle in this state followed by TP1_HIT or CLOSED
    # via BE-SL.  This is THE state the §3.2a doctrine optimises
    # for — banking + BE residual.
    PRE_TP_FIRED = "PRE_TP_FIRED"

    # TP1 filled (partial close).  Reached when TP1 fires WITHOUT
    # pre-TP having fired first (an unusually-fast favourable move).
    # On transition: SL moves to BE on this transition (PR-7).
    TP1_HIT = "TP1_HIT"

    # TP2 filled (further partial close).
    TP2_HIT = "TP2_HIT"

    # Terminal state.  Reached when SL fires, all TPs fill, or the
    # user manually closes from the Lumin app.
    CLOSED = "CLOSED"


# Terminal states — FSM rejects further transitions once here.
_TERMINAL_STATES = frozenset({PositionState.CLOSED})


def is_terminal(state: PositionState) -> bool:
    """True if the state cannot transition further.  FSM uses this to
    short-circuit incoming events for already-closed positions
    (Binance may send late events after a manual close)."""
    return state in _TERMINAL_STATES


# ---------------------------------------------------------------------------
# Dataclass projection — what the FSM operates on
# ---------------------------------------------------------------------------


@dataclass
class Position:
    """In-memory projection of the Firestore position document.

    Mutated by FSM transitions; persisted back via :func:`put_position`.
    Not frozen because the FSM updates fields in-place (filled_qty,
    state, closed_qty, etc.).
    """

    signal_id: str
    firebase_uid: str
    symbol: str
    side: str  # "LONG" | "SHORT"
    state: PositionState
    entry_price_target: float
    entry_price_filled: float
    sl_price: float
    tp1_price: float
    tp2_price: float
    tp3_price: float
    total_qty: float
    tp1_qty: float
    tp2_qty: float
    tp3_qty: float
    filled_qty: float = 0.0
    closed_qty: float = 0.0
    entry_order_id: int = 0
    sl_order_id: int = 0
    sl_be_order_id: int = 0  # Replacement SL after BE shift (post-pre-TP / post-TP1)
    pretp_order_id: int = 0  # Pre-TP partial-close order (when fired)
    tp1_order_id: int = 0
    tp2_order_id: int = 0
    tp3_order_id: int = 0
    # Per §3.2a doctrine.  Pre-TP threshold price + fraction are
    # captured at signal-placement time so the controller can fire
    # without re-reading user settings every tick.  pretp_fraction
    # honours the B17 30% floor / 100% ceiling enforced at the
    # signal-placement entry point.
    pretp_threshold_price: float = 0.0
    pretp_fraction: float = 0.5  # Engine default per B17 / §3.2a
    pretp_fired: bool = False
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_event_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    closed_at: Optional[datetime] = None
    close_reason: str = ""
    realized_pnl_total: float = 0.0


# ---------------------------------------------------------------------------
# Client-order-id convention — single source of truth
# ---------------------------------------------------------------------------


_COID_ENTRY_SUFFIX = "_entry"
_COID_SL_SUFFIX = "_sl"
# After pre-TP fires + SL moves to BE, the replacement SL gets a
# distinct suffix so the FSM can tell "original SL filled" from "BE
# SL filled" — different ``close_reason`` for accounting.
_COID_SL_BE_SUFFIX = "_sl_be"
_COID_PRETP_SUFFIX = "_pretp"
_COID_TP1_SUFFIX = "_tp1"
_COID_TP2_SUFFIX = "_tp2"
_COID_TP3_SUFFIX = "_tp3"
# Market close placed by the invalidation/expiry/cancellation path in
# signal_dispatch.close_fsm_positions_for_signal.  Distinct from
# _pretp so the FSM doesn't mis-classify invalidation closes as pre-TP
# fills when the ORDER_TRADE_UPDATE event arrives.
_COID_CLOSE_SUFFIX = "_close"


def coid(signal_id: str, phase: str) -> str:
    """Build the deterministic clientOrderId for a phase of one signal.

    Convention: ``lumin_<signal_id>_<phase>``.  Binance limits
    clientOrderId to 36 chars + restricted character set; signal_id is
    UUID-shape so we stay well under the limit.

    The FSM uses the clientOrderId on incoming ORDER_TRADE_UPDATE
    events to identify which order phase the event belongs to —
    Binance's ``order_id`` (numeric, server-assigned) doesn't carry
    that information.
    """
    return f"lumin_{signal_id}{phase}"


def coid_entry(signal_id: str) -> str:
    return coid(signal_id, _COID_ENTRY_SUFFIX)


def coid_sl(signal_id: str) -> str:
    return coid(signal_id, _COID_SL_SUFFIX)


def coid_sl_be(signal_id: str) -> str:
    """clientOrderId for the BE-shifted SL (post-pre-TP / post-TP1)."""
    return coid(signal_id, _COID_SL_BE_SUFFIX)


def coid_pretp(signal_id: str) -> str:
    """clientOrderId for the pre-TP partial-close order (REDUCE_ONLY
    MARKET fired when mark price crosses the pre-TP threshold)."""
    return coid(signal_id, _COID_PRETP_SUFFIX)


def coid_tp1(signal_id: str) -> str:
    return coid(signal_id, _COID_TP1_SUFFIX)


def coid_tp2(signal_id: str) -> str:
    return coid(signal_id, _COID_TP2_SUFFIX)


def coid_tp3(signal_id: str) -> str:
    return coid(signal_id, _COID_TP3_SUFFIX)


def coid_close(signal_id: str) -> str:
    """clientOrderId for a MARKET close placed on invalidation/expiry/
    cancellation by :func:`signal_dispatch.close_fsm_positions_for_signal`.

    Distinct from ``_pretp`` so the FSM can log these terminal closes
    without confusing them with pre-TP partial fills.
    """
    return coid(signal_id, _COID_CLOSE_SUFFIX)


def parse_coid(client_order_id: str) -> Optional[tuple[str, str]]:
    """Parse a clientOrderId back into ``(signal_id, phase)``.

    Returns ``None`` if the id doesn't match Lumin's convention —
    that's a foreign order (manual fill from another tool, or a
    signal placed before this PR landed).  Caller should LOG and
    SKIP for foreign orders rather than crash.

    ``phase`` is one of: "entry" | "sl" | "sl_be" | "pretp" |
    "close" | "tp1" | "tp2" | "tp3".
    """
    if not client_order_id.startswith("lumin_"):
        return None
    rest = client_order_id[len("lumin_"):]
    # Order matters: longer suffixes must be checked FIRST so
    # ``..._sl_be`` doesn't get classified as ``..._sl`` (and
    # ``..._pretp`` doesn't shadow a future ``..._tp`` suffix).
    for phase in ("sl_be", "pretp", "close", "entry", "sl", "tp1", "tp2", "tp3"):
        suffix = f"_{phase}"
        if rest.endswith(suffix):
            signal_id = rest[: -len(suffix)]
            if signal_id:
                return (signal_id, phase)
    return None


# ---------------------------------------------------------------------------
# Module singleton + init (mirrors firestore_keystore pattern)
# ---------------------------------------------------------------------------


class PositionStateError(Exception):
    """Base — caller maps to a sensible HTTP / log response."""


class PositionStateNotInitialisedError(PositionStateError):
    """Read/write attempted before :func:`init_position_state` succeeded."""


class PositionNotFoundError(PositionStateError):
    """The requested ``(uid, signal_id)`` has no position doc."""


_lock = threading.RLock()
_db: Any = None  # google.cloud.firestore.Client once initialised


def init_position_state(service_account_path: Optional[str] = None) -> None:
    """Initialise the Firestore Admin SDK client for the position
    state collection.

    Idempotent.  Shares the same service-account credential as
    :func:`src.security.firestore_keystore.init_keystore` (and may
    even share the underlying client in a future consolidation —
    both modules talk to the same Firestore project).
    """
    global _db
    with _lock:
        if _db is not None:
            log.info("position_state already initialised")
            return
        from google.cloud import firestore  # type: ignore[import-not-found]
        from google.oauth2 import service_account  # type: ignore[import-not-found]

        if service_account_path:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_path
            )
            _db = firestore.Client(credentials=credentials)
        else:
            _db = firestore.Client()
        log.info(
            "position_state initialised: service_account={}",
            service_account_path or "ADC",
        )


def is_initialised() -> bool:
    with _lock:
        return _db is not None


def _doc_ref(firebase_uid: str, signal_id: str) -> Any:
    """Resolve the position document reference.

    Path: ``users/{uid}/positions/{signal_id}``.  Matches the
    Firestore Security Rules in PR-3 — client-readable but
    engine-write-only.
    """
    with _lock:
        if _db is None:
            raise PositionStateNotInitialisedError(
                "position_state not initialised — call init_position_state at boot"
            )
        return (
            _db.collection("users")
            .document(firebase_uid)
            .collection("positions")
            .document(signal_id)
        )


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


def put_position(position: Position) -> None:
    """Insert or replace a position document.

    Idempotent — used for both first-time write (at signal placement)
    and FSM transitions (every state change rewrites the document).
    Firestore's ``set`` semantics handle both with one call.
    """
    _doc_ref(position.firebase_uid, position.signal_id).set(
        _to_firestore_dict(position)
    )


def get_position(firebase_uid: str, signal_id: str) -> Position:
    """Load a position document.  Raises :class:`PositionNotFoundError`
    when the doc doesn't exist.
    """
    snap = _doc_ref(firebase_uid, signal_id).get()
    if not snap.exists:
        raise PositionNotFoundError(
            f"no position for uid={firebase_uid} signal_id={signal_id}"
        )
    return _from_firestore_dict(snap.to_dict() or {})


def delete_position(firebase_uid: str, signal_id: str) -> None:
    """Remove a position document.  Idempotent — no error on missing doc.

    Currently unused (positions stay in Firestore for audit /
    historical-PnL view).  Provided for completeness + future
    retention-policy implementation.
    """
    _doc_ref(firebase_uid, signal_id).delete()


def list_positions_for_user(
    firebase_uid: str, *, include_closed: bool = False
) -> list[Position]:
    """Return every position document under ``users/{uid}/positions/``.

    Used by the Lumin app's Live-tab "your open positions" card
    (``GET /api/auto-trade/positions``).  ``include_closed=False``
    filters out terminal states so the dashboard doesn't show
    yesterday's closed trades — pair with the trade-records history
    view for the historical surface.

    Returns empty list when the collection doesn't exist yet (a fresh
    user who has never had a position).  Raises
    :class:`PositionStateNotInitialisedError` if the keystore wasn't
    initialised at boot.
    """
    with _lock:
        if _db is None:
            raise PositionStateNotInitialisedError(
                "position_state not initialised — call init_position_state at boot"
            )
        coll = (
            _db.collection("users")
            .document(firebase_uid)
            .collection("positions")
        )
    docs = coll.stream()
    out: list[Position] = []
    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue
        try:
            pos = _from_firestore_dict(data)
        except Exception:
            log.exception(
                "list_positions_for_user: skipping malformed doc uid={} doc_id={}",
                firebase_uid, doc.id,
            )
            continue
        if not include_closed and is_terminal(pos.state):
            continue
        out.append(pos)
    return out


def reset_for_test() -> None:
    """Test-only: drop the singleton."""
    global _db
    with _lock:
        _db = None


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------


def _to_firestore_dict(position: Position) -> dict:
    """Convert Position to a dict suitable for Firestore ``set``.

    PositionState (an Enum) is encoded as its string value so
    Firestore can store + index it.  ``datetime``s pass through
    directly — Firestore's Python SDK accepts UTC-aware datetimes
    natively.
    """
    return {
        "signal_id": position.signal_id,
        "firebase_uid": position.firebase_uid,
        "symbol": position.symbol,
        "side": position.side,
        "state": position.state.value,
        "entry_price_target": position.entry_price_target,
        "entry_price_filled": position.entry_price_filled,
        "sl_price": position.sl_price,
        "tp1_price": position.tp1_price,
        "tp2_price": position.tp2_price,
        "tp3_price": position.tp3_price,
        "total_qty": position.total_qty,
        "tp1_qty": position.tp1_qty,
        "tp2_qty": position.tp2_qty,
        "tp3_qty": position.tp3_qty,
        "filled_qty": position.filled_qty,
        "closed_qty": position.closed_qty,
        "entry_order_id": position.entry_order_id,
        "sl_order_id": position.sl_order_id,
        "sl_be_order_id": position.sl_be_order_id,
        "pretp_order_id": position.pretp_order_id,
        "tp1_order_id": position.tp1_order_id,
        "tp2_order_id": position.tp2_order_id,
        "tp3_order_id": position.tp3_order_id,
        "pretp_threshold_price": position.pretp_threshold_price,
        "pretp_fraction": position.pretp_fraction,
        "pretp_fired": position.pretp_fired,
        "created_at": position.created_at,
        "last_event_at": position.last_event_at,
        "closed_at": position.closed_at,
        "close_reason": position.close_reason,
        "realized_pnl_total": position.realized_pnl_total,
    }


def _from_firestore_dict(data: dict) -> Position:
    """Convert a Firestore doc dict back to a Position dataclass.

    Defaults are aggressive (missing fields → 0 / empty string)
    because we want a partial document to still be readable for
    diagnostics — if the FSM crashed mid-write, the partial doc
    should not block the position from being listed in the app's
    debug view.
    """
    return Position(
        signal_id=str(data.get("signal_id", "")),
        firebase_uid=str(data.get("firebase_uid", "")),
        symbol=str(data.get("symbol", "")),
        side=str(data.get("side", "")),
        state=PositionState(data.get("state", "PENDING")),
        entry_price_target=float(data.get("entry_price_target", 0.0)),
        entry_price_filled=float(data.get("entry_price_filled", 0.0)),
        sl_price=float(data.get("sl_price", 0.0)),
        tp1_price=float(data.get("tp1_price", 0.0)),
        tp2_price=float(data.get("tp2_price", 0.0)),
        tp3_price=float(data.get("tp3_price", 0.0)),
        total_qty=float(data.get("total_qty", 0.0)),
        tp1_qty=float(data.get("tp1_qty", 0.0)),
        tp2_qty=float(data.get("tp2_qty", 0.0)),
        tp3_qty=float(data.get("tp3_qty", 0.0)),
        filled_qty=float(data.get("filled_qty", 0.0)),
        closed_qty=float(data.get("closed_qty", 0.0)),
        entry_order_id=int(data.get("entry_order_id", 0)),
        sl_order_id=int(data.get("sl_order_id", 0)),
        sl_be_order_id=int(data.get("sl_be_order_id", 0)),
        pretp_order_id=int(data.get("pretp_order_id", 0)),
        tp1_order_id=int(data.get("tp1_order_id", 0)),
        tp2_order_id=int(data.get("tp2_order_id", 0)),
        tp3_order_id=int(data.get("tp3_order_id", 0)),
        pretp_threshold_price=float(data.get("pretp_threshold_price", 0.0)),
        pretp_fraction=float(data.get("pretp_fraction", 0.5)),
        pretp_fired=bool(data.get("pretp_fired", False)),
        created_at=data.get(
            "created_at", datetime.now(timezone.utc)
        ),
        last_event_at=data.get(
            "last_event_at", datetime.now(timezone.utc)
        ),
        closed_at=data.get("closed_at"),
        close_reason=str(data.get("close_reason", "")),
        realized_pnl_total=float(data.get("realized_pnl_total", 0.0)),
    )
