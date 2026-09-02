"""Firestore-backed global kill switch + per-user auto-disable state.

Two flags persisted in Firestore so they survive engine restart AND
are visible across processes (the Telegram bot may flip them from a
separate process):

1. **Global kill switch** — ``kill_switch/global`` doc with a single
   ``engaged: bool`` field.  When True, ALL auto-trade halts within
   one cache TTL (default 5 seconds — well under the 5s SLA in B18).
2. **Per-user disabled** — ``users/{uid}/auto_trade_disabled``
   field on the user's root doc.  Set when the per-user circuit
   breaker (see :mod:`src.execution.tripwires`) trips.  Survives
   restart so a tripped user stays disabled until manual operator
   re-enable from the Telegram bot.

The order placement chain consults BOTH on every order.

**That paragraph used to end "total Firestore reads ~12k/day, well inside the
free tier."**  It was arithmetic about the ORDER path, and the order path was
never the cost: the readers that actually spent the quota are loops — the trade
monitor at 5s and the scanner every cycle — which the estimate did not model at
all.  Measured on 2026-09-02, this one document was costing ~34,000 reads a day
through two cache slots, and the project was refused at 53,000 against a 50,000
allowance.  Reads are now gated on an explicit invalidation signal
(:mod:`src.control_generation`) with the TTL demoted to a floor, and
:mod:`src.firestore_reads` counts them per call site so the next estimate in
this file can be checked instead of believed.
"""

from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Optional

from src import firestore_reads as _reads
from src.utils import get_logger

log = get_logger("execution.kill_switch")


_GLOBAL_KILL_DOC = ("kill_switch", "global")
_GLOBAL_KILL_FIELD = "engaged"
_USER_DISABLED_FIELD = "auto_trade_disabled"

# Global auto-trade enable flag (PR-14, per #431 no-staged-beta
# compensating controls).  Lives on the same kill_switch/global doc
# as the kill switch field for atomic visibility (one Firestore
# read covers BOTH flags).  Distinct field name + inverse default:
#   * ``engaged`` defaults False (kill switch OFF → trading allowed)
#   * ``auto_trade_globally_enabled`` defaults False
#       (auto-trade OFF until operator explicitly turns it ON)
# The combined gate the FSM checks before placing orders:
#   auto_trade_globally_enabled == True
#       AND engaged == False
#       AND user-not-disabled
# Default-OFF on the enable flag means a fresh deploy ships in a
# SAFE state — no user can auto-trade until the operator flips the
# Firestore doc.  This is the operative blast-radius cap per #431.
_GLOBAL_ENABLED_FIELD = "auto_trade_globally_enabled"

# Time-based signal-expiry backstop toggle, on the same doc so the ops
# control plane can flip it live (owner decision 2026-06-26). Absent field →
# fall back to the SIGNAL_EXPIRY_ENABLED env default. Independent cache slot
# (NOT folded into the kill-switch combined read) so the safety-critical
# engaged/enabled read path is untouched.
_SIGNAL_EXPIRY_FIELD = "signal_expiry_enabled"

# Google Play billing master switch, on the same doc so the ops control plane
# can turn the subscription paywall on/off live (owner request 2026-07-16).
# Absent field → fall back to the GOOGLE_PLAY_BILLING_ENABLED env default.
# Served by the SAME cached document read as the other three flags: this
# comment used to say it was read straight through "so write-through is
# immediately live", which was true and is now true more cheaply, because a
# write bumps the generation and every reader drops its cache on the next tick.
_BILLING_ENABLED_FIELD = "play_billing_enabled"

# Cache lifetime for the ``kill_switch/global`` document.
#
# Was 5.0s, and that was the single most expensive constant in this project.
# ``MONITOR_POLL_INTERVAL`` is 5.0s and the trade monitor asks about the
# signal-expiry flag once per poll, so the entry expired exactly one tick
# before every read: a cache that could never hit, costing ~17,280 reads a day
# on one document — plus another ~17,280 because the expiry flag took its OWN
# ``.get()`` of the SAME doc through a separate cache slot.  Together with
# ``runtime_tunables`` that was the entire 50,000/day allowance, and on
# 2026-09-02 Firestore refused us: the keystore went blind, every signal fanned
# out to zero users, and ``POST /api/kill-switch`` 503'd — the emergency stop
# and the thing it stops failing together.
#
# **This is now a floor, not the mechanism.**  Cross-process visibility is a
# Redis generation the write path bumps (:mod:`src.control_generation`), which
# is both cheaper and faster than any TTL.  The TTL is what converges a
# deployment with no Redis, and what catches a dropped bump.
#
# B18's "a flip takes effect in under 5 seconds" is *better* met than before:
# it used to hold by luck, because a reader happened to re-ask Firestore every
# 5s.  It now holds by construction — the flip bumps the generation, the
# monitor's 5s poll sees it on the next tick, and the re-read is immediate.
def _global_ttl_from_env() -> float:
    """Defensive TTL in seconds.  Env-overridable, floored at 5s.

    Floored rather than clamped both ways because a longer value is only ever
    a cost/latency trade, while a sub-5s one would put a Firestore read back on
    the monitor's own period — the defect this constant records.
    """
    raw = os.environ.get("KILL_SWITCH_CACHE_TTL_SEC", "").strip()
    if not raw:
        return 300.0
    try:
        return max(float(raw), 5.0)
    except (TypeError, ValueError):
        log.warning(
            "KILL_SWITCH_CACHE_TTL_SEC={!r} is not a number — using 300s", raw
        )
        return 300.0


_CACHE_TTL_S = _global_ttl_from_env()

#: Per-user disable state is mirrored onto ONE document so the fan-out gate
#: costs one read instead of one per user.  See :meth:`is_user_disabled`.
_DISABLED_MIRROR_DOC = ("control", "disabled_uids")
_DISABLED_MIRROR_FIELD = "uids"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class KillSwitchError(Exception):
    """Base — caller decides retry / surface."""


class KillSwitchNotInitialisedError(KillSwitchError):
    """Read/write attempted before init."""


# ---------------------------------------------------------------------------
# Availability — three worlds, not two
# ---------------------------------------------------------------------------

#: The client is wired and the last read succeeded.
AVAIL_OK = "ok"
#: No Firestore client in this process — a deployment/credentials fact.  The
#: switch cannot be read OR thrown here and will not recover on its own.
AVAIL_NOT_CONFIGURED = "not_configured"
#: The client exists and Firestore refused or failed.  Transient in principle;
#: on 2026-09-02 it was the daily read quota, which resets at midnight Pacific.
AVAIL_READ_FAILED = "read_failed"


def _bump_global() -> None:
    """Tell every other process the flags document has changed.

    Separate from the write so a Redis failure can never roll back a Firestore
    write that already landed: the switch is thrown either way, and a dropped
    signal costs the other container one defensive TTL, not correctness.
    """
    try:
        from src import control_generation as _gen

        _gen.bump(_gen.DOC_KILL_SWITCH)
    except Exception:  # pragma: no cover - never break a control write
        log.exception("kill_switch: generation bump failed")


def _bump_disabled() -> None:
    """Same, for the per-user disable mirror."""
    try:
        from src import control_generation as _gen

        _gen.bump(_gen.DOC_DISABLED_UIDS)
    except Exception:  # pragma: no cover
        log.exception("kill_switch: disabled-mirror generation bump failed")


@dataclass
class _CachedFlag:
    """One cached boolean read plus when it was taken.

    Survives only for the per-user fallback in :meth:`is_user_disabled` — the
    path taken when the one-document mirror has never been written.  Every
    other flag now rides the shared ``_CachedDoc``.
    """

    value: bool
    read_at_monotonic: float


@dataclass
class _CachedDoc:
    """The whole ``kill_switch/global`` document plus when it was read.

    Caching the DOCUMENT rather than one field per slot is the repair for the
    defect above: ``engaged``, ``auto_trade_globally_enabled``,
    ``signal_expiry_enabled`` and ``play_billing_enabled`` all live here, and
    every one of them used to be able to spend its own read of the same doc.

    ``exists`` is carried apart from an empty ``data`` because a missing
    document and a document with no fields are the same dict and different
    facts — the first is a fresh project, the second is somebody having cleared
    a flag.
    """

    data: dict
    exists: bool
    read_at_monotonic: float


@dataclass
class _CachedDisabled:
    """The mirrored set of auto-disabled uids, and whether the mirror EXISTS.

    ``present`` False means the mirror document has never been written — which
    is not the same as "nobody is disabled" and must never be read as it.  The
    caller falls back to the per-user document in that case; absence of
    knowledge is not permission.
    """

    uids: frozenset
    present: bool
    read_at_monotonic: float


class KillSwitchClient:
    """Firestore-backed kill switch + per-user disable state.

    Constructed once per engine process.  All public methods are
    thread-safe (RLock).  Reads are cached until the generation moves or the
    defensive TTL lapses; writes are write-through (immediate, invalidate the
    local cache, bump the cross-process generation).

    The Firestore SDK is injected at construction time so tests can
    pass a mock without touching ``google.cloud.firestore``.
    """

    def __init__(self, firestore_client: Any) -> None:
        self._db = firestore_client
        self._lock = threading.RLock()
        self._doc_cache: Optional[_CachedDoc] = None
        self._disabled_cache: Optional[_CachedDisabled] = None
        self._user_cache: dict[str, _CachedFlag] = {}
        #: Why the last read failed, if it did.  Published so a surface can
        #: name what the engine said instead of inventing a cause — ops turned
        #: one boolean into a confident sentence about this deployment's
        #: credentials for the third time on 2026-09-02.
        self._last_error: Optional[str] = None
        # ``time.monotonic`` injectable for tests so cache-expiry
        # behaviour is testable without ``time.sleep``.
        self._clock = time.monotonic

    # ---- The one document read ----------------------------------------

    def _doc(self) -> _CachedDoc:
        """Return the cached ``kill_switch/global`` document, reading it at
        most once per generation change or defensive TTL.

        **One read serves every flag on the document.**  Four accessors used to
        be able to take four reads of the same doc within a second of each
        other.
        """
        with self._lock:
            cached = self._doc_cache
            now = self._clock()
            if (
                cached is not None
                and (now - cached.read_at_monotonic) < _CACHE_TTL_S
            ):
                return cached
        try:
            snap = (
                self._db.collection(_GLOBAL_KILL_DOC[0])
                .document(_GLOBAL_KILL_DOC[1])
                .get()
            )
        except Exception as exc:
            # Record WHAT Firestore said, then re-raise.  The order path must
            # still fail closed — refusing an order is the safe direction — but
            # a refusal whose cause lives only in a traceback is how ops ended
            # up inventing one.  ``availability()`` reads this.
            self._note_error(exc)
            raise
        _reads.record("kill_switch.global_doc", 1)
        fresh = _CachedDoc(
            data=(snap.to_dict() or {}) if snap.exists else {},
            exists=bool(snap.exists),
            read_at_monotonic=self._clock(),
        )
        with self._lock:
            self._doc_cache = fresh
            self._last_error = None
        return fresh

    def invalidate_global(self) -> None:
        """Drop the cached document — the generation listener's entry point."""
        with self._lock:
            self._doc_cache = None

    def invalidate_disabled(self) -> None:
        """Drop the cached disabled-uid mirror."""
        with self._lock:
            self._disabled_cache = None
            self._user_cache.clear()

    def last_error(self) -> Optional[str]:
        with self._lock:
            return self._last_error

    def _note_error(self, exc: BaseException) -> None:
        with self._lock:
            self._last_error = f"{type(exc).__name__}: {exc}"

    # ---- Global kill switch -------------------------------------------

    def is_global_engaged(self) -> bool:
        """True if engine-wide auto-trade is currently halted.

        Cheap by design — called on every order placement attempt across all
        users.  Serves from the cached document; a flip in another container
        arrives through the generation, not through an expiry.
        """
        return bool(self._doc().data.get(_GLOBAL_KILL_FIELD, False))

    def global_reason(self) -> Optional[str]:
        """The operator's stated reason for the current engage, if any."""
        value = self._doc().data.get("reason")
        return str(value) if value else None

    def engage_global(self, reason: str = "") -> None:
        """Flip the global kill switch ON.  Effective on the next reader tick
        in this process and in every other one (the generation is bumped as
        part of the write).  ``reason`` is recorded for operator visibility.

        Fires a Telegram alert on engage so the operator gets
        notified regardless of whether they initiated the engage
        (programmatic engagement from the global circuit breaker
        also routes through here)."""
        # Invalidate the cache BEFORE writing to Firestore so any
        # concurrent reader misses the stale cache and is forced to
        # re-read rather than seeing an old "not engaged" value after
        # the Firestore doc has already been updated.
        self.invalidate_global()
        self._write_global(engaged=True, reason=reason)
        _bump_global()
        log.warning("kill_switch: GLOBAL engaged reason={}", reason)
        _spawn_engage_alert(reason)

    def disengage_global(self) -> None:
        """Manual operator re-enable.  Flips OFF; resumes auto-trade
        for all non-disabled users."""
        self.invalidate_global()
        self._write_global(engaged=False, reason="")
        _bump_global()
        log.info("kill_switch: GLOBAL disengaged")

    def _write_global(self, *, engaged: bool, reason: str) -> None:
        from datetime import datetime, timezone

        # ``merge=True`` so we don't clobber ``auto_trade_globally_enabled``
        # which lives on the same doc.  The two flags are independent
        # surfaces: kill switch = emergency stop; enable flag = global
        # opt-in.  Both must be writable without disturbing the other.
        self._db.collection(_GLOBAL_KILL_DOC[0]).document(
            _GLOBAL_KILL_DOC[1]
        ).set(
            {
                _GLOBAL_KILL_FIELD: engaged,
                "reason": reason,
                "updated_at": datetime.now(timezone.utc),
            },
            merge=True,
        )

    # ---- Global auto-trade enable flag (PR-14) ------------------------

    def is_globally_enabled(self) -> bool:
        """True if engine-wide auto-trade is currently ENABLED.

        Default is ``False`` — fresh deploy ships with auto-trade
        OFF for every user until the operator explicitly flips this.
        This is the operative blast-radius cap per #431's no-staged-
        beta compensating controls.

        Served by the same cached document as :meth:`is_global_engaged`.
        """
        return bool(self._doc().data.get(_GLOBAL_ENABLED_FIELD, False))

    def enable_global_auto_trade(self) -> None:
        """Operator action — flip ``auto_trade_globally_enabled`` to
        True so auto-trade is allowed engine-wide (subject to per-user
        disable + kill switch checks).  Survives engine restart.
        """
        self._write_enabled(enabled=True)
        self.invalidate_global()
        _bump_global()
        log.info("kill_switch: GLOBAL auto-trade ENABLED")

    def disable_global_auto_trade(self) -> None:
        """Operator action — flip ``auto_trade_globally_enabled`` to
        False.  Halts new order placement for all users (orders
        already on Binance are not cancelled — use the kill switch
        for that scenario)."""
        self._write_enabled(enabled=False)
        self.invalidate_global()
        _bump_global()
        log.warning("kill_switch: GLOBAL auto-trade DISABLED")

    def _write_enabled(self, *, enabled: bool) -> None:
        from datetime import datetime, timezone

        # Same merge=True semantics as _write_global so we don't
        # clobber the engaged field when toggling enable.
        self._db.collection(_GLOBAL_KILL_DOC[0]).document(
            _GLOBAL_KILL_DOC[1]
        ).set(
            {
                _GLOBAL_ENABLED_FIELD: enabled,
                "auto_trade_globally_enabled_at": datetime.now(timezone.utc),
            },
            merge=True,
        )

    # ---- Signal-expiry backstop toggle (ops control, 2026-06-26) ------

    def is_signal_expiry_enabled(self, default: bool) -> bool:
        """True if the time-based max-hold signal-expiry backstop is ON.

        When the field is absent from the doc (ops never set it) returns
        ``default`` — the SIGNAL_EXPIRY_ENABLED env boot default.  Read on
        every monitor poll, and until 2026-09-02 that cost a Firestore read
        per poll through a cache slot of its own on a document the kill switch
        had already fetched.  It now shares the one cached read.
        """
        data = self._doc().data
        if _SIGNAL_EXPIRY_FIELD not in data:
            return default
        return bool(data.get(_SIGNAL_EXPIRY_FIELD, default))

    def set_signal_expiry_enabled(self, enabled: bool) -> None:
        """Operator action — flip the signal-expiry backstop. Write-through +
        cache invalidate so the next monitor poll sees it.  Survives engine
        restart."""
        from datetime import datetime, timezone

        self._db.collection(_GLOBAL_KILL_DOC[0]).document(
            _GLOBAL_KILL_DOC[1]
        ).set(
            {
                _SIGNAL_EXPIRY_FIELD: enabled,
                "signal_expiry_enabled_at": datetime.now(timezone.utc),
            },
            merge=True,
        )
        self.invalidate_global()
        _bump_global()
        log.info(
            "kill_switch: SIGNAL EXPIRY backstop {}",
            "ENABLED" if enabled else "DISABLED",
        )

    # ---- Google Play billing master switch (ops control, 2026-07-16) ---

    def is_billing_enabled(self, default: bool) -> bool:
        """True if the Google Play subscription paywall is ON engine-wide.

        Missing doc / missing field → ``default`` (the GOOGLE_PLAY_BILLING_
        ENABLED env boot value).  Used to be read straight through on the
        reasoning that verify / RTDN are low-frequency and a flip should be
        live immediately; both halves are now served better by the shared
        cached read, because a flip bumps the generation and is therefore live
        immediately WITHOUT a read per call."""
        data = self._doc().data
        if _BILLING_ENABLED_FIELD not in data:
            return default
        return bool(data.get(_BILLING_ENABLED_FIELD, default))

    def set_billing_enabled(self, enabled: bool) -> None:
        """Operator action — turn the Play billing paywall on/off engine-wide.
        Write-through (``merge=True`` so the kill-switch / auto-trade flags on
        the same doc are untouched). Survives engine restart."""
        from datetime import datetime, timezone

        self._db.collection(_GLOBAL_KILL_DOC[0]).document(
            _GLOBAL_KILL_DOC[1]
        ).set(
            {
                _BILLING_ENABLED_FIELD: enabled,
                "play_billing_enabled_at": datetime.now(timezone.utc),
            },
            merge=True,
        )
        self.invalidate_global()
        _bump_global()
        log.info(
            "kill_switch: PLAY BILLING {}",
            "ENABLED" if enabled else "DISABLED",
        )

    # ---- Per-user disable ---------------------------------------------
    #
    # This gate is consulted once per user per order attempt, so under the
    # original design its cost grew linearly with subscribers: one document
    # read per user per 5s cache window.  At the 1,000-member target that is
    # millions of reads a day for a field that is false for almost everybody
    # almost always — a breaker trip is rare by construction.
    #
    # So the SET of disabled uids is mirrored onto one document.  The per-user
    # field remains the durable, audited record (it carries the reason and the
    # timestamp, and it is what an operator reads on a user); the mirror is an
    # index over it, written by the same two methods and rebuilt from a query
    # at boot and on a slow timer.
    #
    # The failure direction is the important half: a mirror that has never
    # been written must NOT read as "nobody is disabled".  ``present`` says
    # whether the document exists at all, and when it does not this falls back
    # to the per-user read it replaced.

    def is_user_disabled(self, firebase_uid: str) -> bool:
        """True if this user is auto-trade-disabled (tripped circuit
        breaker, manual operator action, etc.).

        Answered from the one-document mirror.  Falls back to the per-user
        document — the pre-2026-09-02 path — when the mirror has never been
        written, because an absent index is not evidence of an empty one.
        """
        mirror = self._disabled_set()
        if mirror.present:
            return firebase_uid in mirror.uids
        with self._lock:
            cached = self._user_cache.get(firebase_uid)
            now = self._clock()
            if (
                cached is not None
                and (now - cached.read_at_monotonic) < _CACHE_TTL_S
            ):
                return cached.value
        value = self._read_user_disabled(firebase_uid)
        with self._lock:
            self._user_cache[firebase_uid] = _CachedFlag(
                value=value, read_at_monotonic=self._clock()
            )
        return value

    def _disabled_set(self) -> _CachedDisabled:
        """One read of ``control/disabled_uids``, cached like the flags doc."""
        with self._lock:
            cached = self._disabled_cache
            now = self._clock()
            if (
                cached is not None
                and (now - cached.read_at_monotonic) < _CACHE_TTL_S
            ):
                return cached
        snap = (
            self._db.collection(_DISABLED_MIRROR_DOC[0])
            .document(_DISABLED_MIRROR_DOC[1])
            .get()
        )
        _reads.record("kill_switch.disabled_mirror", 1)
        if snap.exists:
            data = snap.to_dict() or {}
            raw = data.get(_DISABLED_MIRROR_FIELD)
            # A document that exists with no list is a mirror somebody
            # truncated, not a mirror that says the set is empty.  Treat it as
            # absent so the per-user fallback covers it.
            if isinstance(raw, list):
                present = True
                uids = frozenset(str(u) for u in raw)
            else:
                present = False
                uids = frozenset()
        else:
            present = False
            uids = frozenset()
        fresh = _CachedDisabled(
            uids=uids, present=present, read_at_monotonic=self._clock()
        )
        with self._lock:
            self._disabled_cache = fresh
        return fresh

    def rebuild_disabled_mirror(self) -> int:
        """Rebuild ``control/disabled_uids`` from the per-user fields.

        Costs one query returning only the disabled users — a handful at any
        realistic scale, and zero on a healthy book (an empty query still
        bills one read).  Called at engine boot and on a slow timer so the
        mirror cannot drift from the durable field indefinitely: a write that
        bypassed :meth:`disable_user` would otherwise be invisible forever,
        and this gate is a safety gate.

        Returns the number of disabled users found.
        """
        query = self._db.collection("users").where(
            _USER_DISABLED_FIELD, "==", True
        )
        uids = []
        docs = 0
        for snap in query.stream():
            docs += 1
            uids.append(snap.id)
        _reads.record("kill_switch.disabled_rebuild", max(docs, 1))
        self._write_disabled_mirror(uids)
        return len(uids)

    def _write_disabled_mirror(self, uids) -> None:
        from datetime import datetime, timezone

        ordered = sorted({str(u) for u in uids})
        self._db.collection(_DISABLED_MIRROR_DOC[0]).document(
            _DISABLED_MIRROR_DOC[1]
        ).set(
            {
                _DISABLED_MIRROR_FIELD: ordered,
                "updated_at": datetime.now(timezone.utc),
            },
            merge=True,
        )
        with self._lock:
            self._disabled_cache = _CachedDisabled(
                uids=frozenset(ordered),
                present=True,
                read_at_monotonic=self._clock(),
            )
        _bump_disabled()

    def _mirror_apply(self, firebase_uid: str, *, disabled: bool) -> None:
        """Add/remove one uid from the mirror without a full rebuild.

        Reads the current set (one cached read) and writes the amended one, so
        a trip costs one read and one write rather than a scan.
        """
        current = set(self._disabled_set().uids)
        if disabled:
            current.add(firebase_uid)
        else:
            current.discard(firebase_uid)
        self._write_disabled_mirror(current)

    def disable_user(self, firebase_uid: str, reason: str = "") -> None:
        """Mark a user auto-trade-disabled.  Called by the per-user
        circuit breaker (PerUserCircuitBreaker) on trip, or by the
        operator.  Survives engine restart.

        Writes the durable per-user field FIRST — it is the record of
        record — then the mirror.  A crash between the two leaves a user
        disabled in the durable field and absent from the index; the slow
        rebuild repairs it, and until then the user is under-protected rather
        than the reverse, which is why the order is not the other way round for
        :meth:`enable_user`.
        """
        self._write_user_disabled(firebase_uid, disabled=True, reason=reason)
        with self._lock:
            self._user_cache.pop(firebase_uid, None)
        self._mirror_apply(firebase_uid, disabled=True)
        log.warning(
            "kill_switch: user disabled uid={} reason={}",
            firebase_uid, reason,
        )

    def enable_user(self, firebase_uid: str) -> None:
        """Manual operator action — re-enable a disabled user.

        Mirror first, then the durable field: a crash between them leaves the
        user still disabled in the record of record, which the next rebuild
        restores.  Both orderings fail toward the user being disabled.
        """
        self._mirror_apply(firebase_uid, disabled=False)
        self._write_user_disabled(firebase_uid, disabled=False, reason="")
        with self._lock:
            self._user_cache.pop(firebase_uid, None)
        log.info("kill_switch: user enabled uid={}", firebase_uid)

    def last_self_reenable_at(self, firebase_uid: str):
        """UTC datetime of the user's last self-service re-enable, or
        ``None``.  Backs the self-serve breaker-recovery cooldown
        (2026-07-18) — uncached: this is only read on the explicit
        re-enable tap, never on a hot path."""
        doc = (
            self._db.collection("users")
            .document(firebase_uid)
            .get()
        )
        _reads.record("kill_switch.self_reenable", 1)
        if not doc.exists:
            return None
        data = doc.to_dict() or {}
        return data.get("auto_trade_self_reenabled_at")

    def record_self_reenable(self, firebase_uid: str) -> None:
        """Stamp the self-service re-enable time (rate-limit anchor)."""
        from datetime import datetime, timezone

        (
            self._db.collection("users")
            .document(firebase_uid)
            .set(
                {"auto_trade_self_reenabled_at": datetime.now(timezone.utc)},
                merge=True,
            )
        )

    def _read_user_disabled(self, firebase_uid: str) -> bool:
        doc = (
            self._db.collection("users")
            .document(firebase_uid)
            .get()
        )
        _reads.record("kill_switch.user_disabled", 1)
        if not doc.exists:
            return False
        data = doc.to_dict() or {}
        return bool(data.get(_USER_DISABLED_FIELD, False))

    def _write_user_disabled(
        self, firebase_uid: str, *, disabled: bool, reason: str
    ) -> None:
        from datetime import datetime, timezone

        update = {
            _USER_DISABLED_FIELD: disabled,
            "auto_trade_disabled_reason": reason,
            "auto_trade_disabled_at": datetime.now(timezone.utc) if disabled else None,
        }
        # Use set with merge=True so we don't clobber other fields
        # on the user doc.
        (
            self._db.collection("users")
            .document(firebase_uid)
            .set(update, merge=True)
        )

    # ---- Test helpers -------------------------------------------------

    def invalidate_cache(self) -> None:
        """Drop ALL cached reads.  Used by tests + by the Telegram
        bot's debug ``/refresh_kill_switch`` command."""
        with self._lock:
            self._doc_cache = None
            self._disabled_cache = None
            self._user_cache.clear()


# ---------------------------------------------------------------------------
# Module-level singleton + init
# ---------------------------------------------------------------------------


_lock = threading.RLock()
_client: Optional[KillSwitchClient] = None


def init_kill_switch(firestore_client: Any) -> None:
    """Initialise the singleton.  Called once at engine boot.

    Idempotent — a second call is a no-op.  ``firestore_client`` is
    the same Firebase Admin SDK Firestore client used by
    :mod:`src.security.firestore_keystore` (sharing one client
    saves Firestore quota + connection overhead).
    """
    global _client
    with _lock:
        if _client is not None:
            return
        _client = KillSwitchClient(firestore_client)
        client = _client
    # Cross-process invalidation.  Registered here rather than in the class so
    # a test constructing a bare ``KillSwitchClient`` does not acquire a
    # process-global listener, and so the wiring is visible at the one place
    # that decides this process reads the switch at all.
    try:
        from src import control_generation as _gen

        _gen.register(_gen.DOC_KILL_SWITCH, client.invalidate_global)
        _gen.register(_gen.DOC_DISABLED_UIDS, client.invalidate_disabled)
    except Exception:  # pragma: no cover - defensive
        log.exception(
            "kill_switch: could not register generation listeners — "
            "cross-process flips will converge on the defensive TTL only"
        )


def is_initialised() -> bool:
    with _lock:
        return _client is not None


def availability() -> tuple[str, Optional[str]]:
    """``(state, detail)`` — WHY the switch is or is not readable right now.

    ``initialised: false`` used to carry three different worlds at once: this
    process never wired Firestore, the read raised, or the flag is honestly
    off.  Ops turned that one boolean into the confident sentence *"no
    Firestore / GCP creds in this deployment"* — a cause the page cannot
    observe, printed in the typeface it uses for footnotes, over a control the
    owner could not operate.

    Two of those three worlds never recover on their own and neither is a
    safety pause, so they are named apart:

    * :data:`AVAIL_NOT_CONFIGURED` — no client here.  A deployment fact.
    * :data:`AVAIL_READ_FAILED` — the client exists and Firestore refused.
      On 2026-09-02 that was the daily read quota, which resets at midnight
      Pacific; ``detail`` carries what the SDK actually said.
    * :data:`AVAIL_OK` — the value on screen is a value.

    Taking the reading costs nothing: it reports the last read's outcome
    rather than provoking a new one.
    """
    with _lock:
        client = _client
    if client is None:
        return (AVAIL_NOT_CONFIGURED, None)
    err = client.last_error()
    if err:
        return (AVAIL_READ_FAILED, err)
    return (AVAIL_OK, None)


def get_client() -> KillSwitchClient:
    """Return the singleton or raise.  FSM / signal-handler call this
    on every order; the typed exception keeps misconfigured-boot
    failures obvious in tracebacks."""
    with _lock:
        if _client is None:
            raise KillSwitchNotInitialisedError(
                "kill switch not initialised — call init_kill_switch at boot"
            )
        return _client


def signal_expiry_enabled(default: bool) -> bool:
    """Safe accessor for the trade-monitor hot path. Returns ``default``
    when the kill switch isn't initialised (single-process mode / tests /
    no GCP creds), else the cached doc value. Never raises — the monitor
    must not crash on a missing Firestore client."""
    with _lock:
        client = _client
    if client is None:
        return default
    try:
        return client.is_signal_expiry_enabled(default)
    except Exception:  # pragma: no cover — defensive: never break the monitor
        log.exception("signal_expiry_enabled read failed — using default")
        return default


def reset_for_test() -> None:
    global _client
    with _lock:
        _client = None


# ---------------------------------------------------------------------------
# Telegram alert dispatch helper — fire-and-forget on engage
# ---------------------------------------------------------------------------


def _spawn_engage_alert(reason: str) -> None:
    """Fire-and-forget the engage alert.  Mirrors the spawn pattern
    in tripwires.py — caller is synchronous (the engage call), we
    schedule the async alert on the running loop without blocking.
    Silently drops if there's no running loop (sync test path)."""
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    try:
        # Lazy import to avoid circular dep at module load.
        from . import telegram_alerts

        loop.create_task(telegram_alerts.alert_kill_switch_engaged(reason=reason))
    except Exception:
        log.exception("kill_switch: failed to schedule engage alert")
