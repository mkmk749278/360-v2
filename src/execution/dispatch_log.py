"""Per-user dispatch event log — Firestore-backed history of every
order-placement attempt (success or rejection).

Why this exists
---------------

Server-side execution dispatches signals to each user's FSM via
:mod:`signal_dispatch`.  Pre-PR-this, rejections only surfaced in
engine logs — the user had zero in-app visibility into why their
account wasn't trading.  Examples seen in production:

* ``code=-2019 'Margin is insufficient.'`` — empty Futures wallet
* ``code=-1111 'Precision is over the maximum defined.'`` — engine
  bug (fixed in PR-prior)
* ``code=-2014 'Invalid API-key, IP, or permissions.'`` — VPS IP
  changed since connect; key needs re-whitelist
* ``code=-4131 'PERCENT_PRICE filter limit.'`` — SL/TP too far
  from mark
* ``SymbolNotInUserPreference`` — user's picker excluded the pair
* ``NotGloballyEnabledError`` — operator hasn't flipped the global
  enable flag

This module persists one document per dispatch attempt under
``users/{firebase_uid}/dispatch_events/{event_id}``.  The Lumin
app's Trade tab reads the latest N events via
``GET /api/auto-trade/recent-events`` and renders each with a
status chip + plain-English translation of the rejection reason.

Doctrine (OWNER_BRIEF B18)
--------------------------

* Persisted fields contain Binance error codes + msgs from the
  response body, plus our typed exception classes — NEVER any
  plaintext API secret material.  Binance's response body is
  server→client only and never echoes the secret; the typed
  exceptions carry only our diagnostic strings.  Safe under the
  "never log a Binance API secret" hard limit.
* Soft-fail on Firestore errors — a failed write must NEVER block
  the signal_dispatch path (worst case we lose visibility for one
  event; we don't lose the order placement).
* Retention is TBD (PR follow-up).  For v1 the subcollection
  grows monotonically; a periodic prune can land later if scale
  becomes a concern (~5 KB/event × 100 events/user/day ≈ 500 KB
  per user per day, well within Firestore free tier).
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from src.utils import get_logger

log = get_logger("execution.dispatch_log")


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DispatchEvent:
    """In-memory projection of one dispatch-attempt document.

    Mirrors the Firestore doc shape 1:1; serialised via
    :func:`_to_firestore_dict` on write, :func:`_from_firestore_dict`
    on read.
    """

    event_id: str
    firebase_uid: str
    signal_id: str
    symbol: str
    direction: str  # "LONG" | "SHORT"
    outcome: str  # "placed" | "rejected"
    timestamp: datetime
    entry_price: float = 0.0
    total_qty: float = 0.0
    # Rejection-only fields (None on placed events):
    reject_class: Optional[str] = None  # type(exc).__name__
    reject_detail: Optional[str] = None  # str(exc) — full diagnostic
    reject_binance_code: Optional[int] = None  # extracted from binance_body
    reject_binance_msg: Optional[str] = None  # extracted from binance_body


# ---------------------------------------------------------------------------
# Module-level singleton + init (mirrors firestore_keystore / position_state)
# ---------------------------------------------------------------------------


_lock = threading.RLock()
_db: Any = None  # google.cloud.firestore.Client once initialised


def init_dispatch_log(firestore_client: Any) -> None:
    """Initialise the singleton.  Called once at engine boot, sharing
    the Firestore Admin SDK client with firestore_keystore +
    position_state to save quota + connection overhead."""
    global _db
    with _lock:
        if _db is None:
            _db = firestore_client


def is_initialised() -> bool:
    with _lock:
        return _db is not None


def reset_for_test() -> None:
    global _db
    with _lock:
        _db = None


# ---------------------------------------------------------------------------
# Write path — called from signal_dispatch
# ---------------------------------------------------------------------------


def _events_collection(firebase_uid: str) -> Any:
    """Return the subcollection ref for a user's dispatch events.

    Raises if not initialised — caller is expected to gate via
    :func:`is_initialised` first to keep write paths from breaking
    in dev / test contexts without the GCP env wired.
    """
    if _db is None:
        raise RuntimeError(
            "dispatch_log not initialised — call init_dispatch_log first"
        )
    return (
        _db.collection("users")
        .document(firebase_uid)
        .collection("dispatch_events")
    )


def record_placed(
    *,
    firebase_uid: str,
    signal_id: str,
    symbol: str,
    direction: str,
    entry_price: float,
    total_qty: float,
) -> None:
    """Record a successful dispatch attempt.

    Soft-fail: any exception is caught + logged but never raised
    (the calling FSM path's success is the contract; visibility is
    best-effort).
    """
    if not is_initialised():
        return
    try:
        event_id = f"{int(datetime.now(timezone.utc).timestamp() * 1000)}-{uuid.uuid4().hex[:8]}"
        doc = {
            "event_id": event_id,
            "firebase_uid": firebase_uid,
            "signal_id": signal_id,
            "symbol": symbol,
            "direction": direction,
            "outcome": "placed",
            "timestamp": datetime.now(timezone.utc),
            "entry_price": float(entry_price),
            "total_qty": float(total_qty),
        }
        _events_collection(firebase_uid).document(event_id).set(doc)
    except Exception:
        log.exception(
            "dispatch_log.record_placed failed: uid=%s signal_id=%s",
            firebase_uid, signal_id,
        )


def record_rejected(
    *,
    firebase_uid: str,
    signal_id: str,
    symbol: str,
    direction: str,
    entry_price: float,
    reject_class: str,
    reject_detail: str,
    reject_binance_code: Optional[int] = None,
    reject_binance_msg: Optional[str] = None,
) -> None:
    """Record a rejected dispatch attempt.

    ``reject_class`` is the exception class name (e.g.
    ``OrderRejectedByBinance``); ``reject_detail`` is the full
    ``str(exc)`` carrying the Binance code + msg.  When the
    underlying error was a Binance HTTP rejection,
    ``reject_binance_code`` + ``reject_binance_msg`` are extracted
    from the SignResponse.binance_body so the app can switch on the
    typed Binance code without re-parsing the detail string.

    Soft-fail same as :func:`record_placed`.
    """
    if not is_initialised():
        return
    try:
        event_id = f"{int(datetime.now(timezone.utc).timestamp() * 1000)}-{uuid.uuid4().hex[:8]}"
        doc = {
            "event_id": event_id,
            "firebase_uid": firebase_uid,
            "signal_id": signal_id,
            "symbol": symbol,
            "direction": direction,
            "outcome": "rejected",
            "timestamp": datetime.now(timezone.utc),
            "entry_price": float(entry_price),
            "total_qty": 0.0,
            "reject_class": reject_class,
            "reject_detail": reject_detail,
            "reject_binance_code": (
                int(reject_binance_code)
                if reject_binance_code is not None
                else None
            ),
            "reject_binance_msg": reject_binance_msg,
        }
        _events_collection(firebase_uid).document(event_id).set(doc)
    except Exception:
        log.exception(
            "dispatch_log.record_rejected failed: uid=%s signal_id=%s",
            firebase_uid, signal_id,
        )


# ---------------------------------------------------------------------------
# Read path — called by the API endpoint
# ---------------------------------------------------------------------------


_MAX_LIMIT: int = 100


def list_recent_events(
    firebase_uid: str,
    *,
    limit: int = 20,
) -> list[DispatchEvent]:
    """Return the user's most recent dispatch events, newest first.

    ``limit`` capped at ``_MAX_LIMIT`` to bound query cost.  Returns
    empty list if the keystore isn't initialised so the API endpoint
    no-ops cleanly in dev contexts that haven't booted the full
    server-side execution stack.
    """
    if not is_initialised():
        return []
    limit = max(1, min(int(limit), _MAX_LIMIT))
    try:
        from google.cloud.firestore_v1 import Query  # type: ignore[import-not-found]
    except Exception:
        Query = None  # type: ignore[assignment]
    try:
        coll = _events_collection(firebase_uid)
        if Query is not None:
            query = coll.order_by(
                "timestamp", direction=Query.DESCENDING,
            ).limit(limit)
        else:
            # Fallback if the firestore SDK shape changes — read
            # without explicit ordering, sort client-side.
            query = coll.limit(limit)
        snaps = list(query.stream())
    except Exception:
        log.exception(
            "dispatch_log.list_recent_events read failed: uid=%s",
            firebase_uid,
        )
        return []

    out: list[DispatchEvent] = []
    for snap in snaps:
        data = snap.to_dict()
        if not data:
            continue
        try:
            out.append(_from_firestore_dict(data))
        except Exception:
            log.exception(
                "dispatch_log.list_recent_events: skipping malformed doc "
                "uid=%s doc_id=%s",
                firebase_uid, snap.id,
            )
            continue
    # Defensive sort newest-first in case the Query ordering path
    # didn't apply (or the fallback path is in use).
    out.sort(key=lambda e: e.timestamp, reverse=True)
    return out[:limit]


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------


def _from_firestore_dict(data: dict) -> DispatchEvent:
    """Tolerant deserialisation — missing fields default to typed
    zeros so a partially-written doc still surfaces as a row in the
    app's Recent Activity card rather than 500-ing the whole list."""
    ts = data.get("timestamp") or datetime.now(timezone.utc)
    return DispatchEvent(
        event_id=str(data.get("event_id", "")),
        firebase_uid=str(data.get("firebase_uid", "")),
        signal_id=str(data.get("signal_id", "")),
        symbol=str(data.get("symbol", "")),
        direction=str(data.get("direction", "")),
        outcome=str(data.get("outcome", "")),
        timestamp=ts if isinstance(ts, datetime) else datetime.now(timezone.utc),
        entry_price=float(data.get("entry_price", 0.0)),
        total_qty=float(data.get("total_qty", 0.0)),
        reject_class=data.get("reject_class"),
        reject_detail=data.get("reject_detail"),
        reject_binance_code=(
            int(data["reject_binance_code"])
            if data.get("reject_binance_code") is not None
            else None
        ),
        reject_binance_msg=data.get("reject_binance_msg"),
    )
