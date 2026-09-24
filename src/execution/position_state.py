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

import re
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from src import firestore_reads as _reads
from src.utils import get_logger

log = get_logger("execution.position_state")


class PositionState(str, Enum):
    """FSM states for a per-user-per-signal position.

    Inherits from ``str`` so Firestore stores the enum as its string
    value automatically (no custom serialiser needed).

    Allowed transitions are pinned in :mod:`src.execution.position_fsm`.
    """

    # Resting LIMIT entry order placed, waiting for fill.  Only used
    # when FSM_LIMIT_ENTRY_ENABLED=true.  Binance has a resting GTC
    # LIMIT on the book; the position has no size yet.  SL/TP are NOT
    # placed until the fill event arrives (PENDING_ENTRY → OPEN via
    # _apply_entry_fill which places SL first).
    PENDING_ENTRY = "PENDING_ENTRY"

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

    # Terminal state.  PENDING_ENTRY TTL elapsed: the reconciler
    # cancelled the resting LIMIT order before it filled.  Zero P&L —
    # never entered.  Mirrors the signal-book's EXPIRED_NO_FILL.
    CANCELLED_NO_FILL = "CANCELLED_NO_FILL"


# Terminal states — FSM rejects further transitions once here.
_TERMINAL_STATES = frozenset({PositionState.CLOSED, PositionState.CANCELLED_NO_FILL})

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

# Hard cap on the bounded closed-history read below.  A render bound, not a
# retention policy: the collection is never pruned, so without a ceiling a
# caller could ask for the whole history through a "limited" query.
_MAX_CLOSED_HISTORY: int = 100


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
    # Set True the moment the mark-price-triggered BE shift fires (pretp_dispatcher).
    # Prevents the dispatcher from re-cancelling an already-shifted SL on subsequent ticks.
    be_shift_fired: bool = False
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_event_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    closed_at: Optional[datetime] = None
    # PENDING_ENTRY only: when the resting LIMIT must be filled by.
    # None for MARKET-entry (PENDING) positions.
    entry_expires_at: Optional[datetime] = None
    close_reason: str = ""
    realized_pnl_total: float = 0.0
    # Protection responsibility for this position (manual trade builder,
    # 2026-07-18, docs/MANUAL_TRADE_BUILDER_DESIGN.md):
    #   * "managed"    — auto-dispatched from one of our signals. The engine
    #                    owns the exit: SL is compulsory, the naked-position
    #                    invariant + backstop + ops Tier-0 detector all apply.
    #   * "user_owned" — a user-directed manual take (signal or alert). SL is
    #                    OPTIONAL (owner decision 2026-07-18); the invariant,
    #                    the reconciler backstop, and the naked-position
    #                    detector EXEMPT it. The user owns the exit.
    # Default "managed" so any un-stamped / pre-upgrade row fails toward MORE
    # protection, never less.
    protection_mode: str = "managed"
    # --- live trail governor (2026-08-10) -------------------------------
    # Stamped at signal placement from the user's ``exit_mechanism`` setting
    # so the governor never re-reads SQLite per bar (the hot-loop rule), and
    # so a mid-flight settings change cannot re-govern a position that is
    # already running.  "" / "default" = the SL/TP FSM, unchanged.
    exit_mechanism: str = ""
    # False until the mechanism comes onside and takes the exit over.  Before
    # handover the evaluator's SL and TP1 are live and untouched; after it,
    # they are cancelled and ``trail_stop_order_id`` is the only stop.
    trail_governing: bool = False
    #: algoId of the currently parked trail stop (0 = none parked).
    trail_stop_order_id: int = 0
    #: Price of that parked stop.  Persisted because the ratchet is enforced
    #: against it after a restart — mechanism state is rebuilt by re-walking,
    #: but the stop we already told Binance about is a fact, not a derivation.
    trail_stop_price: float = 0.0
    #: Monotonic re-place counter.  Every amend mints a new clientAlgoId
    #: (Binance rejects a duplicate), so the sequence is part of the coid and
    #: the FSM parses it back out to recognise the fill.
    trail_stop_seq: int = 0
    #: ms timestamp of the newest closed bar the governor has consumed.  The
    #: governor acts once per bar; this is what makes it idempotent across
    #: sweeps and is the clock a staleness probe reads (#835).
    trail_last_bar_ms: float = 0.0
    # ---- Close that did not land (2026-09-24) ----------------------------
    #: Set when the engine decided to close this position and Binance did not
    #: take the market close.  The position stays NON-terminal with its stop
    #: still resting, so the reconciler — which only walks live positions —
    #: retries the close every cycle.  Until then a close failure cancelled the
    #: stop first and marked the doc CLOSED anyway, leaving a position open on
    #: Binance with no stop and nothing left that would ever look at it.
    pending_close_reason: str = ""
    pending_close_at: Optional[datetime] = None
    #: The entry order's outcome is unknown: the signing call timed out or was
    #: unreachable, so it may still have filled.  The doc is written BEFORE the
    #: entry goes out, so a late fill always finds it; this flag tells the fill
    #: handler (and the reconciler) that nobody is laying the stop for it.
    entry_ambiguous: bool = False


# ---------------------------------------------------------------------------
# Protective orders — what has to be swept when a position goes terminal
# ---------------------------------------------------------------------------

#: Order-id fields naming an order that RESTS on Binance protecting an open
#: position: the stop in each of its forms, and every take-profit leg.
#:
#: DERIVED from the dataclass, not typed out again.  Two hand-kept copies of
#: this list already existed (``signal_dispatch._PROTECTIVE_ORDER_ATTRS`` and
#: the per-site ``if position.tpN_order_id`` chains in ``position_fsm``), and
#: they disagreed — which is exactly how the TP ladder came to be left resting
#: after a close.  A field added to :class:`Position` is covered here the day
#: it is added; a NON-protective order id has to be named in the exclusion set
#: below, which is a deliberate act somebody has to justify in a diff.
_NON_PROTECTIVE_ORDER_ATTRS: frozenset = frozenset(
    {
        # The entry itself.  Filled or cancelled long before terminal; it
        # protects nothing.
        "entry_order_id",
        # The pre-TP partial close is a REGULAR reduce-only LIMIT on the book
        # (``/fapi/v1/order``), not an algo order — Binance really does sweep
        # those when the position flattens, and it would need ``cancel_order``
        # rather than ``cancel_algo_order`` anyway.  Named here so its absence
        # reads as a decision rather than an oversight.
        "pretp_order_id",
    }
)


def _derive_protective_order_attrs() -> tuple:
    """Every ``*_order_id`` field on :class:`Position` bar the excluded ones."""
    from dataclasses import fields as _dc_fields

    return tuple(
        f.name
        for f in _dc_fields(Position)
        if f.name.endswith("_order_id")
        and f.name not in _NON_PROTECTIVE_ORDER_ATTRS
    )


#: The sweep set, resolved once at import.  ``position_fsm`` and
#: ``signal_dispatch`` both read THIS — neither keeps its own copy.
PROTECTIVE_ORDER_ATTRS: tuple = _derive_protective_order_attrs()


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
# The live trail governor re-parks its stop on every closed bar, and Binance
# rejects a duplicate clientAlgoId — so unlike every suffix above, this one is
# NOT deterministic per signal: it carries a monotonic sequence
# (``_trail3``).  ``parse_coid`` therefore matches it by pattern rather than
# by equality, and the sequence is discarded once parsed: the FSM only needs
# to know a trail stop filled, and *which* re-place it was is the governor's
# bookkeeping, already on the position.
_COID_TRAIL_PREFIX = "_trail"
_COID_TRAIL_RE = re.compile(r"^(?P<signal_id>.+)_trail(?P<seq>\d+)$")


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


def coid_trail(signal_id: str, seq: int) -> str:
    """clientAlgoId for the ``seq``-th trail stop parked on this signal.

    Sequenced because the governor re-parks every bar and Binance rejects a
    duplicate id.  Kept well inside the 36-char limit: ``lumin_`` (6) +
    signal_id + ``_trail`` (6) + the sequence.
    """
    return coid(signal_id, f"{_COID_TRAIL_PREFIX}{int(seq)}")


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
    "close" | "funding_close" | "tp1" | "tp2" | "tp3" | "trail".
    """
    if not client_order_id.startswith("lumin_"):
        return None
    rest = client_order_id[len("lumin_"):]
    # Checked before the suffix loop: a trail coid ends in a digit, so it can
    # never collide with a fixed suffix, but matching it first keeps the two
    # schemes from having to reason about each other.  The sequence is parsed
    # and dropped — see ``_COID_TRAIL_PREFIX``.
    trail = _COID_TRAIL_RE.match(rest)
    if trail is not None:
        return (trail.group("signal_id"), "trail")
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
    _dirty_uids.add(uid)
    if _resync_touched is not None:
        _resync_touched.add((uid, sid))
    if is_terminal(position.state):
        bucket = _index.get(uid)
        if bucket is not None:
            bucket.pop(sid, None)
            if not bucket:
                _index.pop(uid, None)
        # Display-only.  This runs inside the FSM's write path, after the
        # Firestore write succeeded, so it must never raise into it.
        try:
            _closed_ring_push_locked(position)
        except Exception as exc:  # noqa: BLE001
            from src import fail_open as _fail_open

            _fail_open.record("position_state.closed_ring", exc)
    else:
        _index.setdefault(uid, {})[sid] = position


def _index_delete_locked(firebase_uid: str, signal_id: str) -> None:
    """Drop one position from the live index.  Caller MUST hold :data:`_lock`."""
    bucket = _index.get(firebase_uid)
    if bucket is not None:
        bucket.pop(signal_id, None)
        if not bucket:
            _index.pop(firebase_uid, None)
    _dirty_uids.add(firebase_uid)
    if _resync_touched is not None:
        _resync_touched.add((firebase_uid, signal_id))


def index_active() -> bool:
    """True if the in-memory live-position index is hydrated and serving."""
    with _lock:
        return _index_active


# ---------------------------------------------------------------------------
# Per-user book, published for the isolated api container (2026-09-23)
# ---------------------------------------------------------------------------
#
# Why this exists.  In isolated mode the api container never initialises this
# module (see "Process scope" above), so ``GET /api/auto-trade/positions`` hit
# ``if not _ps._db: return {"positions": []}`` on every request, and the
# position half of ``/api/auto-trade/signal-outcomes`` was skipped entirely.
# The Trade tab's "YOUR OPEN POSITIONS" card and every signal card's own
# outcome chip therefore read empty in production from the day each shipped,
# while the engine held the answer in memory.  Same seam as the trail
# governor's ``INDEX COLD``: in-process state read from the other process.
#
# The engine now publishes each user's book to Redis (``snapshot_writer``),
# and the api reads that.  The OPEN half is the live index (zero reads).  The
# CLOSED half is a bounded ring per user, fed by every terminal write, so it
# costs nothing going forward; history older than this process is seeded at
# most once per user, on demand, by one bounded query, and survives engine
# restarts because the published hash is restored at boot.

#: Closed positions kept per user.  Matches the app's own window.
CLOSED_RING: int = 25

_closed_recent: dict[str, list["Position"]] = {}   # uid -> newest first
_closed_seeded: set[str] = set()
_dirty_uids: set[str] = set()


def _closed_ring_push_locked(position: "Position") -> None:
    """Record a terminal write in the user's ring.  Caller holds :data:`_lock`.

    A copy, because the FSM mutates the object it passed in, and a ring that
    shares it would describe the position's next write rather than this one.
    """
    import dataclasses as _dc

    uid = position.firebase_uid
    ring = [p for p in _closed_recent.get(uid, []) if p.signal_id != position.signal_id]
    ring.insert(0, _dc.replace(position))
    ring.sort(key=_closed_sort_key, reverse=True)
    _closed_recent[uid] = ring[:CLOSED_RING]


def _closed_sort_key(position: "Position") -> float:
    ts = position.closed_at or position.last_event_at
    try:
        return float(ts.timestamp())
    except Exception:  # noqa: BLE001 — a malformed stamp sorts last, not raises
        return 0.0


#: The fields the api's readers use (``/api/auto-trade/positions`` and
#: ``/signal-outcomes``).  The book is published into a Redis capped at 128 MB
#: under ``allkeys-lru``: the full document is ~60 fields, and at 1,000 members
#: x (open + CLOSED_RING) rows that is tens of MB of cache able to push the
#: feed keys out.  Everything absent here defaults in ``_from_firestore_dict``.
BOOK_FIELDS: tuple = (
    "signal_id", "firebase_uid", "symbol", "side", "state",
    "entry_price_target", "entry_price_filled", "sl_price", "tp1_price",
    "total_qty", "filled_qty", "closed_qty", "realized_pnl_total",
    "pretp_fired", "close_reason", "created_at", "last_event_at", "closed_at",
)


#: Datetime fields a wire dict carries as ISO strings.  One list for both
#: directions, so a field added to one cannot be forgotten by the other.
_WIRE_DATETIME_FIELDS: tuple = (
    "created_at", "last_event_at", "closed_at", "entry_expires_at",
    "pending_close_at",
)


def to_wire(position: "Position", *, fields: Optional[tuple] = None) -> dict:
    """JSON-safe form of a position: the Firestore dict with ISO datetimes,
    optionally projected to *fields*."""
    out = _to_firestore_dict(position)
    if fields is not None:
        out = {k: out[k] for k in fields if k in out}
    for key in _WIRE_DATETIME_FIELDS:
        if key not in out:
            continue
        value = out.get(key)
        out[key] = value.isoformat() if isinstance(value, datetime) else None
    return out


def from_wire(data: dict) -> "Position":
    """Inverse of :func:`to_wire`."""
    parsed = dict(data)
    for key in _WIRE_DATETIME_FIELDS:
        value = parsed.get(key)
        if isinstance(value, str) and value:
            try:
                parsed[key] = datetime.fromisoformat(value)
            except ValueError:
                parsed[key] = None
        elif not isinstance(value, datetime):
            parsed[key] = None
    if parsed.get("created_at") is None:
        parsed.pop("created_at", None)
    if parsed.get("last_event_at") is None:
        parsed.pop("last_event_at", None)
    return _from_firestore_dict(parsed)


def take_dirty_uids() -> set[str]:
    """Users whose book changed since the last call; clears the set."""
    with _lock:
        out = set(_dirty_uids)
        _dirty_uids.clear()
        return out


def mark_all_dirty() -> None:
    """Every user this process knows about is republished on the next pass."""
    with _lock:
        _dirty_uids.update(_index.keys())
        _dirty_uids.update(_closed_recent.keys())


def user_book(firebase_uid: str) -> Optional[dict]:
    """``{"open": [...], "closed": [...], "closed_seeded": bool}`` or None.

    None while the live index is not serving: an engine that has not
    hydrated cannot say what is open, and publishing an empty book then would
    render a cold engine as a flat account.
    """
    with _lock:
        if not _index_active:
            return None
        open_rows = [
            to_wire(p, fields=BOOK_FIELDS)
            for p in (_index.get(firebase_uid) or {}).values()
        ]
        closed_rows = [
            to_wire(p, fields=BOOK_FIELDS)
            for p in _closed_recent.get(firebase_uid, [])
        ]
        return {
            "open": open_rows,
            "closed": closed_rows,
            "closed_seeded": firebase_uid in _closed_seeded,
        }


def is_closed_seeded(firebase_uid: str) -> bool:
    with _lock:
        return firebase_uid in _closed_seeded


def seed_closed(firebase_uid: str, positions: list["Position"]) -> None:
    """Merge a bounded history read into the ring and mark the user seeded.

    Merge, never replace: a terminal write that landed while the query was in
    flight is newer than anything the query returned.
    """
    with _lock:
        for position in positions:
            if position.firebase_uid == firebase_uid and is_terminal(position.state):
                _closed_ring_push_locked(position)
        _closed_seeded.add(firebase_uid)
        _dirty_uids.add(firebase_uid)


def restore_closed(firebase_uid: str, rows: list, seeded: bool) -> int:
    """Restore a user's ring from the book the previous process published.

    Returns how many rows were restored.  A malformed row is skipped rather
    than failing the user, and a user already written to by this process keeps
    those rows (they are newer).
    """
    restored: list[Position] = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        try:
            restored.append(from_wire(row))
        except Exception:  # noqa: BLE001
            log.warning("restore_closed: skipping malformed row uid={}", firebase_uid)
    with _lock:
        for position in restored:
            if is_terminal(position.state):
                _closed_ring_push_locked(position)
        if seeded:
            _closed_seeded.add(firebase_uid)
        _dirty_uids.add(firebase_uid)
    return len(restored)



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
        _docs = 0
        for snap in query.stream():
            _docs += 1
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
    finally:
        # Counted whether or not the hydration succeeded: a query that raised
        # part-way still billed for every document it had already returned,
        # and a census that only counts successes under-reports exactly the
        # failing loop somebody is hunting.
        _reads.record("position_state.index_hydrate", max(_docs, 1))
    with _lock:
        # Merge any writes that landed during the (lock-free) hydration scan
        # on top of the freshly-read set, then activate.  Live writes win.
        for uid, bucket in _index.items():
            fresh.setdefault(uid, {}).update(bucket)
        _index.clear()
        _index.update(fresh)
        _index_active = True
        # Every hydrated user is owed a published book.
        _dirty_uids.update(_index.keys())
    log.info(
        "position index ACTIVE: hydrated {} live positions across {} users",
        hydrated, len(_index),
    )


#: A full resync is forced at least this often even when the count agrees.
_INDEX_FULL_RESYNC_SEC: float = 3600.0
_last_full_resync_monotonic: Optional[float] = None
#: ``(uid, signal_id)`` written through ``put``/``delete`` while a resync scan
#: is in flight, or ``None`` when no resync is running.
_resync_touched: Optional[set] = None
_resync_stats: dict = {"count_checks": 0, "count_agreed": 0, "full_scans": 0}


def resync_stats() -> dict:
    with _lock:
        return dict(_resync_stats)


_reads.register_gate("position_index_resync", resync_stats)


def _count_live_positions(db: Any) -> Optional[int]:
    """Aggregation count of non-terminal position docs, or ``None``."""
    try:
        query = db.collection_group("positions").where(
            "state", "in", list(_NON_TERMINAL_STATE_VALUES)
        )
        result = query.count().get()
        value = int(result[0][0].value)
    except Exception as exc:  # noqa: BLE001 — unknown → do the full scan
        log.warning("resync_index: count failed ({}) — full scan instead", exc)
        return None
    _reads.record("position_state.index_resync_count", max(1, -(-value // 1000)))
    return value


def resync_index(*, force: bool = False) -> None:
    """Defensive re-hydration: rebuild the live index from Firestore in case
    a write ever bypassed ``put_position`` / ``delete_position`` (out-of-band
    tooling, future code path).  No-op while the index is inactive.

    Mirrors the defensive TTL the #609 generation cache carries — generation
    write-through is the primary mechanism; this bounds drift from anything
    that escapes it.

    Count-gated (2026-09-24).  The full scan bills one read per LIVE position
    every 5 minutes: ~860k reads a day at 1,000 members holding three each, to
    re-confirm an index its only writer keeps exact.  An aggregation
    ``count()`` (one read per 1,000 index entries) is compared with the
    index's own size, and the full scan runs only when they disagree or the
    last one is older than ``_INDEX_FULL_RESYNC_SEC``.

    Race-safe (2026-09-24).  The scan runs lock-free in a worker thread while
    the event loop keeps writing, and the old code then REPLACED the index with
    the scan's result — so a position opened during the scan vanished from the
    index for up to one period (invisible to the pre-TP dispatcher, the trail
    governor and tight invalidation) and one closed during it came back as
    live.  Every key written during the scan now keeps its live value.
    """
    global _resync_touched, _last_full_resync_monotonic
    now = time.monotonic()
    with _lock:
        if not _index_active or _db is None:
            return
        db = _db
        live_n = sum(
            1 for bucket in _index.values() for p in bucket.values()
            if not is_terminal(p.state)
        )
        due = (
            _last_full_resync_monotonic is None
            or (now - _last_full_resync_monotonic) >= _INDEX_FULL_RESYNC_SEC
        )
    if not force and not due:
        with _lock:
            _resync_stats["count_checks"] += 1
        n = _count_live_positions(db)
        if n is not None and n == live_n:
            with _lock:
                _resync_stats["count_agreed"] += 1
            return
    with _lock:
        _resync_touched = set()
    try:
        query = db.collection_group("positions").where(
            "state", "in", list(_NON_TERMINAL_STATE_VALUES)
        )
        fresh: dict[str, dict[str, "Position"]] = {}
        _docs = 0
        for snap in query.stream():
            _docs += 1
            data = snap.to_dict() or {}
            try:
                pos = _from_firestore_dict(data)
            except Exception:
                continue
            if is_terminal(pos.state):
                continue
            fresh.setdefault(pos.firebase_uid, {})[pos.signal_id] = pos
        _reads.record("position_state.index_resync", max(_docs, 1))
    except Exception:
        log.exception("resync_index: rebuild query failed — keeping current index")
        with _lock:
            _resync_touched = None
        return
    with _lock:
        touched = _resync_touched or set()
        _resync_touched = None
        # Writes that landed during the scan are newer than anything it read.
        for uid, sid in touched:
            live = (_index.get(uid) or {}).get(sid)
            if live is not None and not is_terminal(live.state):
                fresh.setdefault(uid, {})[sid] = live
            else:
                bucket = fresh.get(uid)
                if bucket is not None:
                    bucket.pop(sid, None)
                    if not bucket:
                        fresh.pop(uid, None)
        # Both sides: a user who dropped out of the index is owed a book with
        # nothing open in it, not a stale one.
        _dirty_uids.update(_index.keys())
        _dirty_uids.update(fresh.keys())
        _index.clear()
        _index.update(fresh)
        _resync_stats["full_scans"] += 1
        _last_full_resync_monotonic = now


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


def index_live_positions_for_signal(signal_id: str) -> Optional[dict[str, "Position"]]:
    """Every LIVE (non-terminal) position on ``signal_id``, keyed by uid, from
    the live index.  ``None`` when the index is inactive — "cannot answer",
    never "none live"; the caller falls back to its Firestore path.

    Exists because :func:`get_position` can only serve a HIT from memory: a
    uid with no live position on the signal falls through to a billed
    Firestore read.  On a per-tick sweep that miss is the common case (every
    paper user, every user the signal never placed for), and it measured
    102,882 reads/day at one member on 2026-09-23 — twice the 50,000/day
    ceiling behind the 2 Sep outage.  The index holds every live position
    write-through, so an absent uid here is an authoritative "no live
    position", which is the only question those sweeps ask.
    """
    with _lock:
        if not _index_active:
            return None
        out: dict[str, "Position"] = {}
        for uid, bucket in _index.items():
            pos = bucket.get(signal_id)
            if pos is not None and not is_terminal(pos.state):
                out[uid] = pos
        return out


def index_open_positions() -> Optional[list["Position"]]:
    """Every OPEN position across all users, from the live index.

    ``None`` when the index is inactive — and callers must treat that as
    "cannot answer", never as "none open".  There is deliberately no
    Firestore fallback: this is swept once per monitor cycle, and a
    collection-group query on that clock is the exact shape that cost
    ₹4,552/month in Session 24.  The governor counts the refusal and pages
    instead, because a sweep that silently sees nothing is indistinguishable
    from a book with nothing in it.
    """
    with _lock:
        if not _index_active:
            return None
        return [
            pos
            for bucket in _index.values()
            for pos in bucket.values()
            if pos.state == PositionState.OPEN
        ]


def index_live_positions() -> Optional[list["Position"]]:
    """Every LIVE (non-terminal) position across all users, from the index.

    Unlike :func:`index_open_positions` this includes PENDING, PRE_TP_FIRED,
    TP1_HIT and the rest — a close can be owed on any of them.  ``None`` when
    the index is inactive: "cannot answer", never "none live".
    """
    with _lock:
        if not _index_active:
            return None
        return [
            pos
            for bucket in _index.values()
            for pos in bucket.values()
            if not is_terminal(pos.state)
        ]


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
    _reads.record("position_state.get_position", 1)
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
    _docs = 0
    for doc in docs:
        _docs += 1
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
    _reads.record("position_state.list_for_user", max(_docs, 1))
    return out


def list_recent_closed_positions_for_user(
    firebase_uid: str, *, limit: int = 25
) -> list[Position]:
    """Return the user's most recently CLOSED positions, newest first.

    Why this exists (2026-08-31, owner: *"why don't we show ... its
    outcome, actually what traded in binance, so the user can understand
    what the engine produced and what's traded in binance"*).

    Everything that question needs — ``entry_price_filled``,
    ``filled_qty``, ``realized_pnl_total``, ``close_reason``,
    ``closed_at`` — has been written into the position document since the
    FSM shipped, and was readable through no endpoint.
    ``GET /api/auto-trade/positions`` excludes terminal states
    deliberately (it answers "what is open right now") and its docstring
    pointed at a trade-records endpoint that is still ``TBD``.  So the
    app's only record of a placed order was the dispatch *event*, which
    is a record of an ATTEMPT and carries no outcome at all — which is
    why the Trade tab renders "YOUR OPEN POSITIONS 0" directly above
    rows asserting "Position is open".

    Cost discipline.  ``list_positions_for_user(include_closed=True)``
    streams the whole never-pruned collection, and that unfiltered stream
    is exactly the read this module's own comment calls the dominant
    Firestore cost for this collection — it must never be put on an
    app-poll path.  This query is bounded two ways instead: ``order_by``
    ``closed_at`` DESC with a ``limit``.  It needs no composite index (a
    single field), and open positions carry ``closed_at = None``, which
    Firestore sorts last under DESC, so they fall outside the window
    rather than having to be filtered out with a second clause.

    The Python-side ``is_terminal`` guard is defence-in-depth: on a
    collection whose closed docs outnumber the open ones by orders of
    magnitude the ordering alone is enough, but a fresh account with two
    open positions and no closed ones would otherwise return them.
    """
    limit = max(1, min(int(limit), _MAX_CLOSED_HISTORY))
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
    try:
        from google.cloud.firestore_v1 import Query  # type: ignore[import-not-found]
    except Exception:
        Query = None  # type: ignore[assignment]
    try:
        if Query is not None:
            docs = coll.order_by(
                "closed_at", direction=Query.DESCENDING,
            ).limit(limit).stream()
        else:
            # SDK shape drift — refuse rather than fall back to an
            # unbounded stream.  An empty list here reads as "no closed
            # trades", which is wrong; a raise reaches the endpoint's
            # handler, which says the store could not be read.
            raise RuntimeError(
                "google.cloud.firestore_v1.Query unavailable — refusing an "
                "unbounded closed-position scan"
            )
    except Exception:
        log.exception(
            "list_recent_closed_positions_for_user: query failed uid={}",
            firebase_uid,
        )
        raise

    out: list[Position] = []
    _docs = 0
    for doc in docs:
        _docs += 1
        data = doc.to_dict()
        if not data:
            continue
        try:
            pos = _from_firestore_dict(data)
        except Exception:
            log.exception(
                "list_recent_closed_positions_for_user: skipping malformed "
                "doc uid={} doc_id={}",
                firebase_uid, doc.id,
            )
            continue
        if not is_terminal(pos.state):
            continue
        out.append(pos)
    _reads.record("position_state.list_recent_closed", max(_docs, 1))
    return out


def reset_for_test() -> None:
    """Test-only: drop the singleton + live index."""
    global _db, _write_generation, _index_active
    global _resync_touched, _last_full_resync_monotonic
    with _lock:
        _db = None
        _write_generation = 0
        _index.clear()
        _index_active = False
        _closed_recent.clear()
        _closed_seeded.clear()
        _dirty_uids.clear()
        _resync_touched = None
        _last_full_resync_monotonic = None
        for k in _resync_stats:
            _resync_stats[k] = 0


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
        "be_shift_fired": position.be_shift_fired,
        "created_at": position.created_at,
        "last_event_at": position.last_event_at,
        "closed_at": position.closed_at,
        "entry_expires_at": position.entry_expires_at,
        "close_reason": position.close_reason,
        "realized_pnl_total": position.realized_pnl_total,
        "protection_mode": position.protection_mode,
        "exit_mechanism": position.exit_mechanism,
        "trail_governing": position.trail_governing,
        "trail_stop_order_id": position.trail_stop_order_id,
        "trail_stop_price": position.trail_stop_price,
        "trail_stop_seq": position.trail_stop_seq,
        "trail_last_bar_ms": position.trail_last_bar_ms,
        "pending_close_reason": position.pending_close_reason,
        "pending_close_at": position.pending_close_at,
        "entry_ambiguous": position.entry_ambiguous,
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
        be_shift_fired=bool(data.get("be_shift_fired", False)),
        created_at=data.get(
            "created_at", datetime.now(timezone.utc)
        ),
        last_event_at=data.get(
            "last_event_at", datetime.now(timezone.utc)
        ),
        closed_at=data.get("closed_at"),
        entry_expires_at=data.get("entry_expires_at"),
        close_reason=str(data.get("close_reason", "")),
        realized_pnl_total=float(data.get("realized_pnl_total", 0.0)),
        # Default "managed": an un-stamped / pre-manual-builder row is an auto
        # position and must keep full protection (fail toward MORE safety).
        protection_mode=str(data.get("protection_mode", "managed")),
        # A doc written before the governor shipped carries none of these.
        # Every default is the un-governed state, so a pre-upgrade position
        # keeps the exit it was placed with rather than being adopted by a
        # mechanism mid-flight.
        exit_mechanism=str(data.get("exit_mechanism", "")),
        trail_governing=bool(data.get("trail_governing", False)),
        trail_stop_order_id=int(data.get("trail_stop_order_id", 0)),
        trail_stop_price=float(data.get("trail_stop_price", 0.0)),
        trail_stop_seq=int(data.get("trail_stop_seq", 0)),
        trail_last_bar_ms=float(data.get("trail_last_bar_ms", 0.0)),
        # Written before 2026-09-24 → no close pending, entry unambiguous: the
        # old code path either placed the stop itself or recorded why not.
        pending_close_reason=str(data.get("pending_close_reason", "") or ""),
        pending_close_at=data.get("pending_close_at"),
        entry_ambiguous=bool(data.get("entry_ambiguous", False)),
    )
