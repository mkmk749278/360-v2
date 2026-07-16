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

The order placement chain consults BOTH on every order.  The cached
read (5s TTL) means we only hit Firestore once per ~5s per check,
which at 50 users × 7 orders/day each is trivial — total Firestore
reads ~12k/day, well inside the free tier.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any, Optional

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
# Absent field → fall back to the GOOGLE_PLAY_BILLING_ENABLED env default. Read
# only on the low-frequency verify / RTDN paths (never a hot loop), so it is
# read straight through with no cache slot — write-through is immediately live.
_BILLING_ENABLED_FIELD = "play_billing_enabled"

# Cache TTL for reads.  5s gives us the B18 "<5s SLA on kill switch
# flip taking effect" property while keeping Firestore reads minimal.
_CACHE_TTL_S = 5.0


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class KillSwitchError(Exception):
    """Base — caller decides retry / surface."""


class KillSwitchNotInitialisedError(KillSwitchError):
    """Read/write attempted before init."""


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


@dataclass
class _CachedFlag:
    """One cached read from Firestore + when it was read.

    Carries BOTH flags from the ``kill_switch/global`` doc so a
    single read covers both ``is_global_engaged`` and
    ``is_globally_enabled`` lookups without doubling the Firestore
    quota.  ``enabled_value`` is Optional for backward-compat with
    cache entries written before PR-14 (treated as cache-miss on
    subsequent enable-flag reads → triggers a re-fetch)."""

    value: bool
    read_at_monotonic: float
    enabled_value: Optional[bool] = None


class KillSwitchClient:
    """Firestore-backed kill switch + per-user disable state.

    Constructed once per engine process.  All public methods are
    thread-safe (RLock).  Reads are cached for 5s; writes are
    write-through (immediate + invalidate the cache).

    The Firestore SDK is injected at construction time so tests can
    pass a mock without touching ``google.cloud.firestore``.
    """

    def __init__(self, firestore_client: Any) -> None:
        self._db = firestore_client
        self._lock = threading.RLock()
        self._global_cache: Optional[_CachedFlag] = None
        self._user_cache: dict[str, _CachedFlag] = {}
        self._expiry_cache: Optional[_CachedFlag] = None
        # ``time.monotonic`` injectable for tests so cache-expiry
        # behaviour is testable without ``time.sleep``.
        self._clock = time.monotonic

    # ---- Global kill switch -------------------------------------------

    def is_global_engaged(self) -> bool:
        """True if engine-wide auto-trade is currently halted.

        Cached for 5s.  Cheap by design — called on every order
        placement attempt across all users.  After PR-14 this also
        populates the cached ``enabled_value`` so a subsequent
        ``is_globally_enabled`` call hits cache without a second
        Firestore read.
        """
        with self._lock:
            cached = self._global_cache
            now = self._clock()
            if (
                cached is not None
                and (now - cached.read_at_monotonic) < _CACHE_TTL_S
            ):
                return cached.value
            engaged, enabled = self._read_global_both()
            self._global_cache = _CachedFlag(
                value=engaged,
                read_at_monotonic=now,
                enabled_value=enabled,
            )
            return engaged

    def engage_global(self, reason: str = "") -> None:
        """Flip the global kill switch ON.  Effective within
        ``_CACHE_TTL_S`` for every reader.  ``reason`` is recorded
        for operator visibility (Telegram bot displays this when
        showing kill-switch status).

        Fires a Telegram alert on engage so the operator gets
        notified regardless of whether they initiated the engage
        (programmatic engagement from the global circuit breaker
        also routes through here)."""
        # Invalidate the cache BEFORE writing to Firestore so any
        # concurrent reader misses the stale cache and is forced to
        # re-read rather than seeing an old "not engaged" value after
        # the Firestore doc has already been updated.
        with self._lock:
            self._global_cache = None
        self._write_global(engaged=True, reason=reason)
        log.warning("kill_switch: GLOBAL engaged reason={}", reason)
        _spawn_engage_alert(reason)

    def disengage_global(self) -> None:
        """Manual operator re-enable.  Flips OFF; resumes auto-trade
        for all non-disabled users."""
        with self._lock:
            self._global_cache = None
        self._write_global(engaged=False, reason="")
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

        Cached for 5s via the same cache as :meth:`is_global_engaged`
        — both fields live on the same doc, so the cached read covers
        both flags.
        """
        with self._lock:
            cached = self._global_cache
            now = self._clock()
            if (
                cached is not None
                and (now - cached.read_at_monotonic) < _CACHE_TTL_S
                and cached.enabled_value is not None
            ):
                return cached.enabled_value
            engaged, enabled = self._read_global_both()
            self._global_cache = _CachedFlag(
                value=engaged,
                read_at_monotonic=now,
                enabled_value=enabled,
            )
            return enabled

    def enable_global_auto_trade(self) -> None:
        """Operator action — flip ``auto_trade_globally_enabled`` to
        True so auto-trade is allowed engine-wide (subject to per-user
        disable + kill switch checks).  Survives engine restart.
        """
        self._write_enabled(enabled=True)
        with self._lock:
            self._global_cache = None
        log.info("kill_switch: GLOBAL auto-trade ENABLED")

    def disable_global_auto_trade(self) -> None:
        """Operator action — flip ``auto_trade_globally_enabled`` to
        False.  Halts new order placement for all users (orders
        already on Binance are not cancelled — use the kill switch
        for that scenario)."""
        self._write_enabled(enabled=False)
        with self._lock:
            self._global_cache = None
        log.warning("kill_switch: GLOBAL auto-trade DISABLED")

    def _read_global_both(self) -> tuple[bool, bool]:
        """One Firestore read returning ``(engaged, enabled)``.  Both
        flags default False when the doc is missing — kill switch
        OFF, enable flag OFF.  Fresh-deploy state is safe-by-default
        (no trading until operator enables)."""
        doc = (
            self._db.collection(_GLOBAL_KILL_DOC[0])
            .document(_GLOBAL_KILL_DOC[1])
            .get()
        )
        if not doc.exists:
            return (False, False)
        data = doc.to_dict() or {}
        return (
            bool(data.get(_GLOBAL_KILL_FIELD, False)),
            bool(data.get(_GLOBAL_ENABLED_FIELD, False)),
        )

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
        ``default`` — the SIGNAL_EXPIRY_ENABLED env boot default. Cached 5s:
        this is read on every monitor poll, so it must never hit Firestore
        per-signal (Cost Discipline). Its own cache slot keeps the
        safety-critical kill-switch combined read untouched."""
        with self._lock:
            cached = self._expiry_cache
            now = self._clock()
            if (
                cached is not None
                and (now - cached.read_at_monotonic) < _CACHE_TTL_S
                and cached.enabled_value is not None
            ):
                return cached.enabled_value
            value = self._read_signal_expiry(default)
            self._expiry_cache = _CachedFlag(
                value=value, read_at_monotonic=now, enabled_value=value
            )
            return value

    def set_signal_expiry_enabled(self, enabled: bool) -> None:
        """Operator action — flip the signal-expiry backstop. Write-through +
        cache invalidate so the next monitor poll sees it within one TTL.
        Survives engine restart."""
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
        with self._lock:
            self._expiry_cache = None
        log.info(
            "kill_switch: SIGNAL EXPIRY backstop {}",
            "ENABLED" if enabled else "DISABLED",
        )

    def _read_signal_expiry(self, default: bool) -> bool:
        """One Firestore read for the expiry field. Missing doc / missing
        field → ``default`` (env boot value)."""
        doc = (
            self._db.collection(_GLOBAL_KILL_DOC[0])
            .document(_GLOBAL_KILL_DOC[1])
            .get()
        )
        if not doc.exists:
            return default
        data = doc.to_dict() or {}
        if _SIGNAL_EXPIRY_FIELD not in data:
            return default
        return bool(data.get(_SIGNAL_EXPIRY_FIELD, default))

    # ---- Google Play billing master switch (ops control, 2026-07-16) ---

    def is_billing_enabled(self, default: bool) -> bool:
        """True if the Google Play subscription paywall is ON engine-wide.

        Missing doc / missing field → ``default`` (the GOOGLE_PLAY_BILLING_
        ENABLED env boot value). Read straight through (verify / RTDN are
        low-frequency, never a hot loop) so a flip is live immediately."""
        doc = (
            self._db.collection(_GLOBAL_KILL_DOC[0])
            .document(_GLOBAL_KILL_DOC[1])
            .get()
        )
        if not doc.exists:
            return default
        data = doc.to_dict() or {}
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
        log.info(
            "kill_switch: PLAY BILLING {}",
            "ENABLED" if enabled else "DISABLED",
        )

    # ---- Per-user disable ---------------------------------------------

    def is_user_disabled(self, firebase_uid: str) -> bool:
        """True if this user is auto-trade-disabled (tripped circuit
        breaker, manual operator action, etc.).  Cached for 5s per
        user."""
        with self._lock:
            cached = self._user_cache.get(firebase_uid)
            now = self._clock()
            if (
                cached is not None
                and (now - cached.read_at_monotonic) < _CACHE_TTL_S
            ):
                return cached.value
            value = self._read_user_disabled(firebase_uid)
            self._user_cache[firebase_uid] = _CachedFlag(
                value=value, read_at_monotonic=now
            )
            return value

    def disable_user(self, firebase_uid: str, reason: str = "") -> None:
        """Mark a user auto-trade-disabled.  Called by the per-user
        circuit breaker (PerUserCircuitBreaker) on trip, or by the
        operator via the Telegram bot.  Survives engine restart."""
        self._write_user_disabled(firebase_uid, disabled=True, reason=reason)
        with self._lock:
            self._user_cache.pop(firebase_uid, None)
        log.warning(
            "kill_switch: user disabled uid={} reason={}",
            firebase_uid, reason,
        )

    def enable_user(self, firebase_uid: str) -> None:
        """Manual operator action — re-enable a disabled user."""
        self._write_user_disabled(firebase_uid, disabled=False, reason="")
        with self._lock:
            self._user_cache.pop(firebase_uid, None)
        log.info("kill_switch: user enabled uid={}", firebase_uid)

    def _read_user_disabled(self, firebase_uid: str) -> bool:
        doc = (
            self._db.collection("users")
            .document(firebase_uid)
            .get()
        )
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
            self._global_cache = None
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


def is_initialised() -> bool:
    with _lock:
        return _client is not None


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
