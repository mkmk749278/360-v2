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
from dataclasses import dataclass, field
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

    # Pre-TP fired and regime check routed to the ATR trail path.
    # TP2 remains live; original SL is replaced by a Binance
    # TRAILING_STOP_MARKET at trail_order_id.  Transitions to
    # TP1_HIT, TP2_HIT, or CLOSED (via SL_BE fill).
    TRAILING = "TRAILING"

    # Terminal state.  Reached when SL fires, all TPs fill, or the
    # user manually closes from the Lumin app.
    CLOSED = "CLOSED"


# Terminal states — FSM rejects further transitions once here.
_TERMINAL_STATES = frozenset({PositionState.CLOSED})

# Non-terminal state string values, in enum order.  Used as a server-side
# Firestore ``state in (...)`` filter so live-position listings read ONLY
# the handful of active positions — never the unbounded CLOSED history.
# The positions collection is never pruned (``delete_position`` is unused;
# closed docs are retained for the historical-PnL view), so an unfiltered
# collection stream bills one Firestore read per closed position on EVERY
# reconciler / funding-watcher / app-poll cycle.  Keeping this filter
# server-side is the cost-discipline invariant for this collection.
_NON_TERMINAL_STATE_VALUES = tuple(
    s.value for s in PositionState if s not in _TERMINAL_STATES
)


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
    # Per-user soft-invalidation aggressiveness (B17): "loose" / "standard" /
    # "tight".  Captured at signal-placement time from user_invalidation_settings
    # so enforcement doesn't need to re-query SQLite on every FSM tick.
    invalidation_mode: str = "standard"
    # Regime-per-exit context stamped at signal-placement time (Fix A+B).
    # Used by _apply_pretp_fill to choose between TRAIL / VOLATILE / CANCEL.
    entry_regime: str = ""          # 5m Hurst-gated regime at entry
    entry_regime_15m: str = ""      # 15m stateless regime at entry
    atr_percentile_at_entry: float = 50.0  # 0-100; drives trail_atr_multiplier
    atr_value_at_entry: float = 0.0        # Absolute ATR(14) used to compute callbackRate
    trail_order_id: int = 0                # Binance algoId of the TRAILING_STOP_MARKET order
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
# Market close placed by the funding-exit watcher for TRENDING_UP LONG
# positions within the pre-funding window.  Separate suffix so the FSM
# logs FUNDING_EXIT rather than REGIME_EXIT as the close_reason.
_COID_FUNDING_CLOSE_SUFFIX = "_funding_close"


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


def coid_funding_close(signal_id: str) -> str:
    """clientOrderId for a MARKET close placed by the funding-exit watcher.

    Distinct suffix so the FSM records close_reason="FUNDING_EXIT" rather
    than "REGIME_EXIT", keeping telemetry clean for the two exit sources.
    """
    return coid(signal_id, _COID_FUNDING_CLOSE_SUFFIX)


def parse_coid(client_order_id: str) -> Optional[tuple[str, str]]:
    """Parse a clientOrderId back into ``(signal_id, phase)``.

    Returns ``None`` if the id doesn't match Lumin's convention —
    that's a foreign order (manual fill from another tool, or a
    signal placed before this PR landed).  Caller should LOG and
    SKIP for foreign orders rather than crash.

    ``phase`` is one of: "entry" | "sl" | "sl_be" | "pretp" |
    "close" | "funding_close" | "tp1" | "tp2" | "tp3".
    """
    if not client_order_id.startswith("lumin_"):
        return None
    rest = client_order_id[len("lumin_"):]
    # Order matters: longer suffixes must be checked FIRST so
    # ``..._sl_be`` doesn't get classified as ``..._sl`` (and
    # ``..._funding_close`` doesn't get classified as ``..._close``).
    for phase in ("sl_be", "funding_close", "pretp", "close", "entry", "sl", "tp1", "tp2", "tp3"):
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

# Monotonic counter bumped on every position-document write
# (``put_position`` / ``delete_position``).  Read-side caches that want
# to avoid re-querying Firestore on a hot loop (e.g. the per-tick pre-TP
# dispatcher) can compare this generation: while it is unchanged, the set
# of stored positions — and every field on them — is byte-for-byte
# unchanged, because every mutation funnels through one of those two
# writers.  This is the freshness guarantee that makes caching the
# OPEN-positions query safe in a real-money path.
_write_generation: int = 0


def get_write_generation() -> int:
    """Return the current position-write generation (see
    :data:`_write_generation`).  Increments on every ``put_position`` /
    ``delete_position``; never decreases for the life of the process."""
    with _lock:
        return _write_generation


def _bump_write_generation() -> None:
    global _write_generation
    with _lock:
        _write_generation += 1


# ---------------------------------------------------------------------------
# In-memory live-position index (engine process only)
# ---------------------------------------------------------------------------
#
# The engine is the SOLE writer of position state — every mutation funnels
# through ``put_position`` / ``delete_position`` (the same invariant that
# makes the write-generation counter valid).  This index mirrors the set of
# LIVE (non-terminal) positions in process memory, maintained write-through
# by those two writers.  Once active, engine-side readers (pre-TP dispatcher,
# reconciler, funding-exit watcher, the app-positions endpoint in
# single-process mode) are served from memory instead of re-reading the
# engine's own state from a per-read-billed remote DB on 24/7 hot loops.
#
# This is the architecturally-correct end state of the cost work: #609 cached
# the per-tick path and #623 filtered the per-60s path, but both still hit
# Firestore on cache-miss / generation-bump.  With the index active those
# reads are served from memory; Firestore is touched only for the durable
# write-through, a one-time boot hydration, and a low-frequency defensive
# resync.
#
# Process scope: ONLY the engine calls :func:`enable_position_index`.  A
# read-only process (the isolated ``api`` container) never enables it, so
# ``_index_active`` stays False there and every reader falls back to the
# Firestore path — which in that container is itself guarded off (it never
# initialises ``position_state``).  Only LIVE positions are held; a position
# is evicted the moment it is written in a terminal state, bounding memory
# and matching exactly what every live-position reader wants.
_index: dict[str, dict[str, "Position"]] = {}  # uid -> signal_id -> Position
_index_active: bool = False


def _index_put_locked(position: "Position") -> None:
    """Insert / update / evict one position in the live index.  Caller MUST
    hold :data:`_lock`.  A terminal-state write evicts the entry (the index
    tracks live positions only)."""
    uid = position.firebase_uid
    sid = position.signal_id
    if is_terminal(position.state):
        bucket = _index.get(uid)
        if bucket is not None:
            bucket.pop(sid, None)
            if not bucket:
                _index.pop(uid, None)
    else:
        _index.setdefault(uid, {})[sid] = position


def _index_delete_locked(firebase_uid: str, signal_id: str) -> None:
    """Drop one position from the live index.  Caller MUST hold :data:`_lock`."""
    bucket = _index.get(firebase_uid)
    if bucket is not None:
        bucket.pop(signal_id, None)
        if not bucket:
            _index.pop(firebase_uid, None)


def index_active() -> bool:
    """True if the in-memory live-position index is hydrated and serving."""
    with _lock:
        return _index_active


def enable_position_index() -> None:
    """Engine-only: hydrate the live-position index from Firestore (ONE
    collection-group read of all non-terminal positions) and serve every
    subsequent live-position read from memory.

    Idempotent.  No-op if ``position_state`` isn't initialised.  On hydration
    failure the index is left INACTIVE so readers keep using the safe
    Firestore path — we never activate a half-built index in a real-money
    path.  Must be called by the engine bootstrap AFTER
    :func:`init_position_state`; the isolated API process must NOT call it.
    """
    global _index_active
    with _lock:
        if _db is None:
            log.warning(
                "enable_position_index: position_state not initialised — "
                "index stays OFF (readers use Firestore)"
            )
            return
        if _index_active:
            return
        db = _db
    try:
        query = db.collection_group("positions").where(
            "state", "in", list(_NON_TERMINAL_STATE_VALUES)
        )
        fresh: dict[str, dict[str, "Position"]] = {}
        hydrated = 0
        for snap in query.stream():
            data = snap.to_dict() or {}
            try:
                pos = _from_firestore_dict(data)
            except Exception:
                log.exception(
                    "enable_position_index: skipping malformed position doc"
                )
                continue
            if is_terminal(pos.state):
                continue
            fresh.setdefault(pos.firebase_uid, {})[pos.signal_id] = pos
            hydrated += 1
    except Exception:
        log.exception(
            "enable_position_index: hydration query failed — index NOT "
            "activated; readers continue on the Firestore path"
        )
        return
    with _lock:
        # Merge any writes that landed during the (lock-free) hydration scan
        # on top of the freshly-read set, then activate.  Live writes win.
        for uid, bucket in _index.items():
            fresh.setdefault(uid, {}).update(bucket)
        _index.clear()
        _index.update(fresh)
        _index_active = True
    log.info(
        "position index ACTIVE: hydrated {} live positions across {} users",
        hydrated, len(_index),
    )


def resync_index() -> None:
    """Defensive re-hydration: rebuild the live index from Firestore in case
    a write ever bypassed ``put_position`` / ``delete_position`` (out-of-band
    tooling, future code path).  ONE collection-group read; safe to call on a
    low-frequency timer.  No-op while the index is inactive.

    Mirrors the defensive TTL the #609 generation cache carries — generation
    write-through is the primary mechanism; this bounds drift from anything
    that escapes it.
    """
    with _lock:
        if not _index_active or _db is None:
            return
        db = _db
    try:
        query = db.collection_group("positions").where(
            "state", "in", list(_NON_TERMINAL_STATE_VALUES)
        )
        fresh: dict[str, dict[str, "Position"]] = {}
        for snap in query.stream():
            data = snap.to_dict() or {}
            try:
                pos = _from_firestore_dict(data)
            except Exception:
                continue
            if is_terminal(pos.state):
                continue
            fresh.setdefault(pos.firebase_uid, {})[pos.signal_id] = pos
    except Exception:
        log.exception("resync_index: rebuild query failed — keeping current index")
        return
    with _lock:
        _index.clear()
        _index.update(fresh)


def index_open_positions_for_symbol(symbol: str) -> Optional[list["Position"]]:
    """Return OPEN positions on ``symbol`` across all users from the live
    index, or ``None`` when the index is inactive (caller should fall back to
    the Firestore query).  An empty list means "active, none open on this
    symbol" — distinct from ``None``.

    Matches the pre-TP dispatcher's query: state == OPEN only (PRE_TP_FIRED
    and later states don't consume mark-price ticks)."""
    with _lock:
        if not _index_active:
            return None
        out: list["Position"] = []
        for bucket in _index.values():
            for pos in bucket.values():
                if pos.state == PositionState.OPEN and pos.symbol == symbol:
                    out.append(pos)
        return out


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
    with _lock:
        # Write-through to the in-memory live index (terminal writes evict).
        # Maintained unconditionally — cheap, and ensures no write is missed
        # between boot hydration and activation; serving is gated separately
        # on _index_active.
        _index_put_locked(position)
        _bump_write_generation()


def get_position(firebase_uid: str, signal_id: str) -> Position:
    """Load a position document.  Raises :class:`PositionNotFoundError`
    when the doc doesn't exist.

    Served from the in-memory live index when active and the position is
    non-terminal (returning the same object the FSM mutates in place — the
    engine is single-event-loop, so there is no mid-mutation read race).
    Terminal / never-seen positions fall through to a Firestore read.
    """
    with _lock:
        if _index_active:
            bucket = _index.get(firebase_uid)
            if bucket is not None and signal_id in bucket:
                return bucket[signal_id]
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
    with _lock:
        _index_delete_locked(firebase_uid, signal_id)
        _bump_write_generation()


def list_positions_for_user(
    firebase_uid: str, *, include_closed: bool = False
) -> list[Position]:
    """Return every position document under ``users/{uid}/positions/``.

    Used by the Lumin app's Live-tab "your open positions" card
    (``GET /api/auto-trade/positions``), the reconciler, and the
    funding-exit watcher.  ``include_closed=False`` filters out terminal
    states so the dashboard doesn't show yesterday's closed trades —
    pair with the trade-records history view for the historical surface.

    Cost discipline: when ``include_closed`` is False the state filter is
    pushed into Firestore (``state in <non-terminal>``) so we read only
    live positions, NOT every CLOSED doc in the user's history.  This
    collection is never pruned, so an unfiltered stream on the per-60s
    reconciler / funding-watcher loops billed one read per historical
    position every cycle — the dominant Firestore cost after #609 fixed
    the per-tick pre-TP path.  The Python-side ``is_terminal`` guard
    below is kept as defence-in-depth (a CLOSED doc can never slip
    through both layers).

    When the in-memory live index is active and ``include_closed`` is False,
    this is served entirely from memory (zero Firestore reads) — the index
    holds exactly the user's live positions.  ``include_closed=True`` (the
    rare historical view) always streams Firestore since the index never
    holds terminal docs.

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
        if _index_active and not include_closed:
            bucket = _index.get(firebase_uid)
            return list(bucket.values()) if bucket else []
        coll = (
            _db.collection("users")
            .document(firebase_uid)
            .collection("positions")
        )
    if include_closed:
        docs = coll.stream()
    else:
        docs = coll.where(
            "state", "in", list(_NON_TERMINAL_STATE_VALUES)
        ).stream()
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
    """Test-only: drop the singleton + live index."""
    global _db, _write_generation, _index_active
    with _lock:
        _db = None
        _write_generation = 0
        _index.clear()
        _index_active = False


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
        "invalidation_mode": position.invalidation_mode,
        "entry_regime": position.entry_regime,
        "entry_regime_15m": position.entry_regime_15m,
        "atr_percentile_at_entry": position.atr_percentile_at_entry,
        "atr_value_at_entry": position.atr_value_at_entry,
        "trail_order_id": position.trail_order_id,
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
        invalidation_mode=str(data.get("invalidation_mode", "standard")),
        entry_regime=str(data.get("entry_regime", "")),
        entry_regime_15m=str(data.get("entry_regime_15m", "")),
        atr_percentile_at_entry=float(data.get("atr_percentile_at_entry", 50.0)),
        atr_value_at_entry=float(data.get("atr_value_at_entry", 0.0)),
        trail_order_id=int(data.get("trail_order_id", 0)),
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
