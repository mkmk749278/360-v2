"""Anomaly tripwires — the blast-radius caps per B18 + #431.

The operative defence layer if the engine VPS is rooted.  Each
tripwire raises a typed exception when violated; the FSM (PR-6/7)
calls these BEFORE placing any order so a malicious caller — or a
buggy code path — cannot push past the boundaries.

Tripwires (per OWNER_BRIEF B18 + the strengthened defaults in #431):

1. **Symbol allowlist** — only Lumin signal-channel symbols can be
   traded.  Order for any other symbol = breach signal, engages the
   global kill switch + Telegram alert.  Configurable via env so
   adding a new pair is a deploy, not a code change.

2. **Per-user rate limit** — 5 orders/min, 30 orders/hour.  Tighter
   than the original B18 spec (10/min, 50/hour) per the no-staged-
   beta compensating-controls decision in #431.

3. **Per-user position cap** — default $500, user-configurable up to
   $2000.  Caps the dollar damage from any single signal — even if
   the FSM places a wrong-direction order, max bleed per signal is
   the cap, not the engine's full sizing.

4. **Per-user circuit breaker** — auto-disable a user after 3
   Binance rejections in 5 minutes.  Catches: one user's API key
   permissions changed underneath us; key revoked; account
   suspended.  Bounded blast to one user.

5. **Global circuit breaker** — auto-disable engine-wide auto-trade
   after 10 Binance rejections cluster in 60s across all users.
   Catches: FSM bug firing wrong-permission orders for every user;
   KMS outage breaking signing globally; symbol-allowlist drift.
   Manual Telegram re-enable required.

State storage:

* Symbol allowlist: in-memory constant, env-overridable.
* Rate counters + rejection counters: in-memory sliding windows.
  Reset on engine restart — acceptable because (a) the windows are
  short (minutes) and (b) post-restart we expect lower order
  volume during reconnect.  Per-user disable that persists across
  restart is in :mod:`src.execution.kill_switch` (Firestore-backed).
* Global kill switch flag: Firestore (cross-process visibility —
  the Telegram bot may engage it from a separate process).

All counters are per-process.  In a multi-process engine deployment
(future hardening) these would need to be lifted to Redis.  For solo
+ single-VPS that's not required.
"""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque, Dict, Optional, Set

from src.utils import get_logger

log = get_logger("execution.tripwires")


# ---------------------------------------------------------------------------
# Defaults — per #431 strengthened blast-radius decision (no-staged-beta
# compensating controls)
# ---------------------------------------------------------------------------


# Defaults match B18 §3.9 strengthened-defaults table.  All env-overridable.
DEFAULT_RATE_LIMIT_PER_MIN = 5
DEFAULT_RATE_LIMIT_PER_HOUR = 30
DEFAULT_POSITION_CAP_USD = 500.0
DEFAULT_POSITION_CAP_MAX_USD = 2_000.0  # User can opt UP to this, not above.
DEFAULT_PER_USER_REJECTION_THRESHOLD = 3
DEFAULT_PER_USER_REJECTION_WINDOW_S = 5 * 60  # 5 minutes
DEFAULT_GLOBAL_REJECTION_THRESHOLD = 10
DEFAULT_GLOBAL_REJECTION_WINDOW_S = 60  # 1 minute


# ---------------------------------------------------------------------------
# Errors — typed so the FSM's catch chain stays small
# ---------------------------------------------------------------------------


class TripwireViolation(Exception):
    """Base.  Caller (the FSM / signal handler) treats as 'do not
    place this order; record an anomaly event; surface to operator'."""


class SymbolNotAllowed(TripwireViolation):
    """Order for a symbol not in the engine's signal-channel allowlist.

    This is the strongest breach signal in the tripwire taxonomy —
    nothing in normal operation should try to trade an out-of-list
    symbol.  Engaging the global kill switch on this trigger is the
    default response."""


class RateLimitExceeded(TripwireViolation):
    """User has fired too many orders in the per-min or per-hour window."""


class PositionCapExceeded(TripwireViolation):
    """Order notional exceeds the user's configured position cap."""


class UserAutoDisabled(TripwireViolation):
    """The per-user circuit breaker has tripped for this user.  Order
    refused until manual operator re-enable."""


class GlobalKillSwitchEngaged(TripwireViolation):
    """The global kill switch is engaged.  Order refused for ALL
    users until manual operator re-enable."""


class SymbolNotInUserPreference(TripwireViolation):
    """Symbol passes the engine-wide allowlist but the user has
    explicitly excluded it from their per-user symbol preference.

    Distinct from :class:`SymbolNotAllowed` — this is a USER decision,
    not an engine-wide blast-radius defence.  Lower-severity (operator
    doesn't need to act); the FSM just skips the order and logs.  No
    kill-switch engagement on this trip."""


# ---------------------------------------------------------------------------
# Symbol allowlist
# ---------------------------------------------------------------------------


def _load_symbol_allowlist() -> Set[str]:
    """Resolve the engine-wide symbol allowlist.

    Sources, in priority order:

    1. ``TRIPWIRE_SYMBOL_ALLOWLIST`` env (comma-separated symbols) —
       operator hard-narrow.  When set, the value is the cap; even
       if the engine's pair universe contains more symbols, only the
       env list trades.  Doctrine-strict mode for paranoid deployments.
    2. The live ``PairManager`` singleton's ``futures_symbols`` — the
       engine's actual scan universe (top-75 USDT-M futures, evolves
       as Binance lists / delists / volume shifts).  When the env is
       unset, the allowlist auto-tracks the engine.  Maintains the
       "every paid signal is potentially executable" doctrine without
       requiring operator env edits each time the universe drifts.
    3. Empty set — safe default when neither is available (boot order,
       test harness).  Every order blocks until one of the above is
       wired.

    B18 doctrine change (2026-05-19, PR G owner-sign-off): the prior
    rule was env-only with empty = block-all.  That produced stale
    coverage gaps whenever PairManager promoted / demoted a pair
    without an operator env edit.  The new rule auto-tracks PairManager
    (whose pair-list updates flow through the same GitHub Actions
    deployment pipeline as the env, so the audit-trail surface is
    unchanged) while preserving the env override for operator
    hard-narrow.  Dollar blast-radius cap is unchanged
    (MAX_POSITION_USD × MAX_CONCURRENT × rate_limit ≈ $2500/user/min).
    """
    raw = os.environ.get("TRIPWIRE_SYMBOL_ALLOWLIST", "").strip()
    if raw:
        return {s.strip().upper() for s in raw.split(",") if s.strip()}
    # Env unset → fall back to the engine's live pair universe.
    try:
        from src import pair_manager as _pair_manager_module
        pm = _pair_manager_module.get_singleton()
        if pm is None:
            return set()
        # futures_symbols returns a list of Binance futures pair codes
        # (e.g. ["BTCUSDT", "ETHUSDT", ...]) currently in the engine's
        # scan universe.  PairManager refreshes this periodically via
        # ``refresh_top50_futures`` so newly-promoted pairs appear
        # without an engine restart.
        return {s.upper() for s in pm.futures_symbols}
    except Exception:
        # Defensive: PairManager not initialised, or read failed mid-
        # refresh.  Block-all rather than risk a false widen on
        # transient errors — the env override remains the explicit
        # path to a known-good list.
        log.exception("Failed to resolve PairManager allowlist fallback")
        return set()


def assert_symbol_allowed(
    symbol: str, *, allowlist: Optional[Set[str]] = None
) -> None:
    """Raise :class:`SymbolNotAllowed` if ``symbol`` isn't on the
    allowlist.

    ``allowlist`` is injectable for tests; production reads from env
    via :func:`_load_symbol_allowlist`.
    """
    if allowlist is None:
        allowlist = _load_symbol_allowlist()
    if symbol.upper() not in allowlist:
        raise SymbolNotAllowed(
            f"symbol {symbol!r} is not on the tripwire allowlist "
            f"(allowlist size: {len(allowlist)})"
        )


def assert_symbol_in_user_preference(
    symbol: str,
    firebase_uid: str,
) -> None:
    """Raise :class:`SymbolNotInUserPreference` if the user has set a
    symbol preference and this symbol is not in it.

    Per-user narrowing of the engine-wide allowlist (PR E 2026-05-19).
    Default behaviour: when the user has no preference set (NULL row,
    empty resolution), this is a no-op — order proceeds.  When the
    user has set an explicit list, ``symbol`` must appear in it.  The
    empty-list case ("user explicitly chose nothing") blocks every
    order — that's the doctrine-strict opt-out path.

    Soft-failure semantics: if the user-overrides store isn't wired
    (test harnesses, engine boot order), default to allowing through.
    The engine-wide ``assert_symbol_allowed`` is still the hard
    security floor — this gate only narrows.
    """
    try:
        from src.api import user_overrides as _uo
        from src.api import users as _users_module
    except Exception:
        return  # boot order — fall through, engine-wide cap still applies

    store = _uo.get_singleton()
    user_store = _users_module.get_singleton() if hasattr(
        _users_module, "get_singleton"
    ) else None
    if store is None or user_store is None:
        return

    try:
        user = user_store.get_by_firebase_uid(firebase_uid)
    except Exception:
        return
    if user is None or user.user_id is None:
        return

    try:
        overrides = store.get_auto_trade(user.user_id)
    except Exception:
        return

    pref = overrides.get("symbol_preference")
    # pref is None (NULL row / no preference) → default = all engine-allowed.
    # pref is a list (possibly empty) → must contain the symbol.
    if pref is None:
        return
    if not isinstance(pref, list):
        return  # defensive — corrupted row, fall through
    if symbol.upper() not in {s.upper() for s in pref}:
        raise SymbolNotInUserPreference(
            f"symbol {symbol!r} is not in user {firebase_uid!r}'s "
            f"symbol preference (pref size: {len(pref)})"
        )


def effective_allowed_symbols_for_user(
    firebase_uid: str,
) -> list[str]:
    """Return the sorted intersection of the engine-wide allowlist and
    the user's symbol preference.

    Used by ``/api/auto-trade/runtime-status`` so the app's footnote
    accurately shows "what will actually trade for me" rather than
    just the engine cap.  Default = engine-wide list when the user has
    no preference set.

    Soft-failure semantics match ``assert_symbol_in_user_preference``
    — if the override store isn't wired, return the engine-wide list.
    """
    engine_allowlist = _load_symbol_allowlist()

    try:
        from src.api import user_overrides as _uo
        from src.api import users as _users_module
    except Exception:
        return sorted(engine_allowlist)

    store = _uo.get_singleton()
    user_store = _users_module.get_singleton() if hasattr(
        _users_module, "get_singleton"
    ) else None
    if store is None or user_store is None:
        return sorted(engine_allowlist)

    try:
        user = user_store.get_by_firebase_uid(firebase_uid)
    except Exception:
        return sorted(engine_allowlist)
    if user is None or user.user_id is None:
        return sorted(engine_allowlist)

    try:
        overrides = store.get_auto_trade(user.user_id)
    except Exception:
        return sorted(engine_allowlist)

    pref = overrides.get("symbol_preference")
    if pref is None or not isinstance(pref, list):
        return sorted(engine_allowlist)
    pref_set = {s.upper() for s in pref if isinstance(s, str)}
    return sorted(engine_allowlist & pref_set)


# ---------------------------------------------------------------------------
# Per-user rate limit — sliding window
# ---------------------------------------------------------------------------


class RateLimiter:
    """Per-user sliding-window rate limiter.

    Two windows enforced simultaneously: per-minute + per-hour.
    Storage: ``deque[float]`` of recent-order timestamps per user.
    Trimmed lazily on each check.

    Thread-safe via a single RLock — orders are placed from asyncio
    tasks (single thread) but tests may exercise multi-threaded
    scenarios so we lock defensively.
    """

    def __init__(
        self,
        *,
        per_min: int = DEFAULT_RATE_LIMIT_PER_MIN,
        per_hour: int = DEFAULT_RATE_LIMIT_PER_HOUR,
        clock: Optional[callable] = None,
    ) -> None:
        self._per_min = per_min
        self._per_hour = per_hour
        self._clock = clock or time.monotonic
        self._lock = threading.RLock()
        # Single deque per user holds all timestamps from the last
        # hour; per-minute is enforced by scanning the tail.
        self._by_user: Dict[str, Deque[float]] = defaultdict(deque)

    def check_and_record(self, firebase_uid: str) -> None:
        """Raise :class:`RateLimitExceeded` if firing now would
        violate per-min OR per-hour limits.  On success, record the
        order timestamp."""
        now = self._clock()
        with self._lock:
            ts = self._by_user[firebase_uid]
            # Trim everything older than 1 hour.
            hour_ago = now - 3600.0
            while ts and ts[0] < hour_ago:
                ts.popleft()
            # Per-hour check.
            if len(ts) >= self._per_hour:
                raise RateLimitExceeded(
                    f"user {firebase_uid} exceeded {self._per_hour} "
                    f"orders/hour limit"
                )
            # Per-minute check — count how many are within last 60s.
            min_ago = now - 60.0
            recent = sum(1 for t in ts if t >= min_ago)
            if recent >= self._per_min:
                raise RateLimitExceeded(
                    f"user {firebase_uid} exceeded {self._per_min} "
                    f"orders/minute limit"
                )
            ts.append(now)


# ---------------------------------------------------------------------------
# Position cap
# ---------------------------------------------------------------------------


def assert_position_cap(
    *,
    notional_usd: float,
    cap_usd: float,
    max_cap_usd: float = DEFAULT_POSITION_CAP_MAX_USD,
) -> None:
    """Raise :class:`PositionCapExceeded` when an order's notional
    is above the user's configured cap OR above the system-wide
    maximum (so a user can't set themselves a cap above the policy
    floor).
    """
    effective = min(cap_usd, max_cap_usd)
    if notional_usd > effective:
        raise PositionCapExceeded(
            f"notional ${notional_usd:.2f} exceeds cap "
            f"${effective:.2f} (user-configured ${cap_usd:.2f}, "
            f"max ${max_cap_usd:.2f})"
        )


# ---------------------------------------------------------------------------
# Per-user circuit breaker
# ---------------------------------------------------------------------------


class PerUserCircuitBreaker:
    """Sliding-window rejection counter per user.

    Tracks Binance rejections — the FSM calls ``record_rejection`` on
    every order placement failure.  When a user accumulates >N
    rejections in W seconds, the breaker trips: subsequent
    ``check`` calls raise until the breaker is manually reset.

    Trip side-effect: writes ``users/{uid}/auto_trade_disabled = true``
    to Firestore via the injected :class:`KillSwitchClient` so the
    disable survives engine restart.  This module just tracks counts +
    decides when to trip; persistence is the kill_switch module.
    """

    def __init__(
        self,
        *,
        threshold: int = DEFAULT_PER_USER_REJECTION_THRESHOLD,
        window_s: float = DEFAULT_PER_USER_REJECTION_WINDOW_S,
        clock: Optional[callable] = None,
    ) -> None:
        self._threshold = threshold
        self._window_s = window_s
        self._clock = clock or time.monotonic
        self._lock = threading.RLock()
        self._by_user: Dict[str, Deque[float]] = defaultdict(deque)
        self._tripped: Set[str] = set()

    def check(self, firebase_uid: str) -> None:
        """Raise :class:`UserAutoDisabled` if the user's breaker has
        tripped.  Called BEFORE placing orders for that user."""
        with self._lock:
            if firebase_uid in self._tripped:
                raise UserAutoDisabled(
                    f"user {firebase_uid} auto-disabled by circuit breaker "
                    f"(>{self._threshold} rejections in "
                    f"{self._window_s:.0f}s window)"
                )

    def record_rejection(self, firebase_uid: str) -> bool:
        """Record one Binance rejection for the user.  Returns True
        if THIS rejection tripped the breaker (the caller persists
        the disable + Telegram-alerts on the first trip).

        Fires a Telegram alert via :mod:`src.execution.telegram_alerts`
        on the first trip — only on the first, so the operator gets
        ONE notification per trip event rather than one per
        rejection."""
        now = self._clock()
        with self._lock:
            ts = self._by_user[firebase_uid]
            cutoff = now - self._window_s
            while ts and ts[0] < cutoff:
                ts.popleft()
            ts.append(now)
            if firebase_uid in self._tripped:
                return False  # already tripped — not a fresh trip
            if len(ts) >= self._threshold:
                self._tripped.add(firebase_uid)
                log.warning(
                    "PerUserCircuitBreaker tripped: uid={} rejections={}",
                    firebase_uid, len(ts),
                )
                # Telegram alert — fire-and-forget so the caller's
                # async context doesn't have to handle it.  Lazy
                # import to avoid circular dep at module load.
                _spawn_alert(
                    _alert_user_disabled,
                    firebase_uid=firebase_uid,
                    rejection_count=len(ts),
                    window_s=self._window_s,
                )
                return True
            return False

    def reset(self, firebase_uid: str) -> None:
        """Manual operator action — re-enable a disabled user.  Clears
        the rejection counter so the next order doesn't immediately
        re-trip on a single new rejection."""
        with self._lock:
            self._tripped.discard(firebase_uid)
            self._by_user.pop(firebase_uid, None)


# ---------------------------------------------------------------------------
# Global circuit breaker — engine-wide
# ---------------------------------------------------------------------------


class GlobalCircuitBreaker:
    """Engine-wide rejection counter.

    Different from :class:`PerUserCircuitBreaker`: this counts
    rejections across ALL users.  When the count crosses the
    threshold in the window, the breaker trips and the global kill
    switch is engaged — refusing orders for every user until manual
    operator re-enable.

    Catches blast scenarios:
    * KMS IAM outage breaking signing for every user simultaneously.
    * FSM bug firing wrong-permission orders.
    * Symbol-allowlist drift (engine + allowlist out of sync after
      a deploy).

    The Telegram-bot operator command ``/reset_global_breaker`` (PR-11
    or a follow-up) re-enables.  Until then, ``check`` raises on
    every order attempt.
    """

    def __init__(
        self,
        *,
        threshold: int = DEFAULT_GLOBAL_REJECTION_THRESHOLD,
        window_s: float = DEFAULT_GLOBAL_REJECTION_WINDOW_S,
        clock: Optional[callable] = None,
    ) -> None:
        self._threshold = threshold
        self._window_s = window_s
        self._clock = clock or time.monotonic
        self._lock = threading.RLock()
        self._timestamps: Deque[float] = deque()
        self._tripped: bool = False

    def check(self) -> None:
        with self._lock:
            if self._tripped:
                raise GlobalKillSwitchEngaged(
                    "global circuit breaker tripped — "
                    "manual Telegram reset required"
                )

    def record_rejection(self) -> bool:
        """Returns True if THIS rejection tripped the breaker.

        Fires a Telegram alert on the first trip — only on the first
        so the operator gets ONE notification per trip event, not one
        per rejection burst.  Subsequent rejections after the breaker
        is tripped return False (the engine already knows; no need
        to alert again)."""
        now = self._clock()
        with self._lock:
            cutoff = now - self._window_s
            while self._timestamps and self._timestamps[0] < cutoff:
                self._timestamps.popleft()
            self._timestamps.append(now)
            if self._tripped:
                return False
            if len(self._timestamps) >= self._threshold:
                self._tripped = True
                log.error(
                    "GlobalCircuitBreaker tripped: rejections in last "
                    "{:.0f}s = {}",
                    self._window_s, len(self._timestamps),
                )
                _spawn_alert(
                    _alert_global_breaker_tripped,
                    rejection_count=len(self._timestamps),
                    window_s=self._window_s,
                )
                return True
            return False

    def reset(self) -> None:
        """Manual operator action — re-enable engine-wide auto-trade."""
        with self._lock:
            self._tripped = False
            self._timestamps.clear()

    @property
    def is_tripped(self) -> bool:
        with self._lock:
            return self._tripped


# ---------------------------------------------------------------------------
# Module-level singletons (production wiring)
# ---------------------------------------------------------------------------


_rate_limiter: Optional[RateLimiter] = None
_per_user_breaker: Optional[PerUserCircuitBreaker] = None
_global_breaker: Optional[GlobalCircuitBreaker] = None


def rate_limiter() -> RateLimiter:
    """Lazily-constructed singleton.  Per-process state."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def per_user_breaker() -> PerUserCircuitBreaker:
    global _per_user_breaker
    if _per_user_breaker is None:
        _per_user_breaker = PerUserCircuitBreaker()
    return _per_user_breaker


def global_breaker() -> GlobalCircuitBreaker:
    global _global_breaker
    if _global_breaker is None:
        _global_breaker = GlobalCircuitBreaker()
    return _global_breaker


def reset_singletons_for_test() -> None:
    """Drop the singletons.  Tests that exercise tripwire behaviour
    should call this in their setup / teardown so per-test state
    doesn't bleed across tests."""
    global _rate_limiter, _per_user_breaker, _global_breaker
    _rate_limiter = None
    _per_user_breaker = None
    _global_breaker = None


# ---------------------------------------------------------------------------
# Telegram alert dispatch helpers
# ---------------------------------------------------------------------------


# Lazy-imported alert functions.  Imported on first use so that
# ``src.execution.tripwires`` doesn't pull ``telegram_alerts`` at
# module-load time (which would create a circular dep through the
# bot bootstrap path).
def _alert_user_disabled(**kwargs: Any) -> Any:
    from . import telegram_alerts
    return telegram_alerts.alert_user_disabled(
        firebase_uid=kwargs["firebase_uid"],
        reason=(
            f"per-user circuit breaker tripped ("
            f"{kwargs['rejection_count']} rejections in "
            f"{kwargs['window_s']:.0f}s)"
        ),
        rejection_count=kwargs["rejection_count"],
    )


def _alert_global_breaker_tripped(**kwargs: Any) -> Any:
    from . import telegram_alerts
    return telegram_alerts.alert_global_breaker_tripped(
        rejection_count=kwargs["rejection_count"],
        window_s=kwargs["window_s"],
    )


def _spawn_alert(coro_factory: Any, **kwargs: Any) -> None:
    """Fire-and-forget the alert coroutine without blocking the
    caller (which is typically inside a synchronous ``record_*``
    call).  Schedules on the running asyncio loop; if there's no
    loop (e.g. running from a sync test) the alert is silently
    dropped — the log line in the calling tripwire is the
    fallback record.
    """
    import asyncio

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return  # no loop — fallback to log-only path
    try:
        loop.create_task(coro_factory(**kwargs))
    except Exception:
        log.exception("tripwires: failed to schedule alert")
