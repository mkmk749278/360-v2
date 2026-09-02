"""Cross-process invalidation for the control documents — the thing a TTL was
standing in for (2026-09-02).

Three Firestore documents cost the entire daily read allowance on the day
auto-trade went down, and none of them had changed in months:

===========================  ==========================  ================
Document / field             Reader                      Reads/day
===========================  ==========================  ================
``kill_switch/global``       order path, trail governor  ~17,280
``kill_switch/global``       ``trade_monitor``, 5s poll  ~17,280
  (a SECOND ``.get()`` on the same doc, its own cache slot)
``control/runtime_tunables`` scanner, every cycle        ~17,280 (5s TTL)
===========================  ==========================  ================

Just over 50,000 — the whole free-tier allowance — on data nobody was
editing.  The mechanism is not a slow cache, it is a cache that **can never
hit**: ``MONITOR_POLL_INTERVAL`` is 5.0s and the TTL was 5.0s, so every poll
arrived one tick after its own entry expired.  A TTL equal to the period of
the loop reading it is not a cache, it is a rename of the read.

``CLAUDE.md`` § Cost Discipline already named the end state: *"an explicit
invalidation signal (a Redis generation the ops write path bumps), which is
both cheaper and faster than any TTL."*  This module is that signal.

How it works
────────────
* Every writer of a control document calls :func:`bump` — one Redis ``INCR``
  on ``control:gen:<doc>``.  Writes are rare by construction (an owner flipping
  a switch), so this path is never hot.
* Every reader process runs :func:`poll` on a loop it already has.  That is one
  Redis ``MGET`` of a handful of tiny keys: free, local, sub-millisecond, and
  **not** a Firestore read.  When a generation has moved, the registered
  invalidator fires and the next Firestore read is taken.
* A writer inside the reader's own process ALSO invalidates locally and
  immediately, exactly as before — the generation covers only what happened in
  the *other* container.

**The TTL survives as a floor, not as the mechanism.**  Redis is optional in
this engine (``RedisClient`` falls back to in-memory), so a deployment with no
Redis must still converge.  It does, on the defensive TTL, which is why that
bound is now measured in minutes rather than seconds: it is what catches a
missed signal, not what carries every read.

Why this makes the kill switch FASTER, not slower
─────────────────────────────────────────────────
B18 requires a kill-switch flip to take effect in under five seconds.  Under
the old design that was met by *chance* — a reader happened to re-ask Firestore
every 5s.  Under this one it is met by *construction*: the flip bumps the
generation on the write, and the monitor's 5s poll sees it on the next tick and
re-reads immediately.  The worst case is unchanged; the common case is faster,
and the cost fell by roughly sixty-fold.

Failure direction
─────────────────
Redis being unreachable must never make a switch look un-thrown.  :func:`poll`
counts a failure and returns without invalidating, so readers fall back to the
defensive TTL — later, never wrong.  A generation that goes *backwards* (a
flushed Redis, a rebuilt container) is treated as a change, not as an error:
the cheap response to "I cannot tell" here is one extra Firestore read.
"""
from __future__ import annotations

import os
import threading
from typing import Any, Callable, Dict, List, Optional

from src.utils import get_logger

log = get_logger("control_generation")

#: Redis key prefix.  One tiny integer per control document.
KEY_PREFIX = "control:gen:"

#: The documents that carry a generation.  Named here rather than passed as
#: strings at every call site so :func:`poll` can read them in ONE round trip
#: and a typo cannot invent a key nothing bumps.
DOC_KILL_SWITCH = "kill_switch_global"
DOC_RUNTIME_TUNABLES = "runtime_tunables"
DOC_ACTIVE_UIDS = "active_uids"
DOC_DISABLED_UIDS = "disabled_uids"

_ALL_DOCS = (
    DOC_KILL_SWITCH,
    DOC_RUNTIME_TUNABLES,
    DOC_ACTIVE_UIDS,
    DOC_DISABLED_UIDS,
)

_lock = threading.RLock()
#: doc -> the generation value this process has already acted on.
_seen: Dict[str, int] = {}
#: doc -> callbacks to run when the generation moves.
_listeners: Dict[str, List[Callable[[], None]]] = {}
#: Observability: this is a safety path, so a silent failure is not acceptable.
_stats: Dict[str, int] = {
    "bumps": 0,
    "bump_failures": 0,
    "polls": 0,
    "poll_failures": 0,
    "invalidations": 0,
}

#: Lazily-created SYNCHRONOUS Redis client.
#:
#: Deliberately not the engine's async ``RedisClient``.  Every writer here is
#: synchronous (``engage_global``, ``set_values``) and may be called from a
#: worker thread with no event loop, so a fire-and-forget task would silently
#: drop the bump in exactly the deployment shape this module exists to repair —
#: the seam this repo keeps paying for.  A blocking ``INCR`` on a path that
#: runs when an owner flips a switch costs nothing worth measuring.
_client: Any = None
_client_tried = False


def _redis() -> Any:
    """Return a sync Redis client, or ``None`` when Redis is not configured.

    Never raises: a control write must land in Firestore whatever Redis is
    doing, and the defensive TTL is what covers the missed signal.
    """
    global _client, _client_tried
    with _lock:
        if _client is not None or _client_tried:
            return _client
        _client_tried = True
        url = os.environ.get("REDIS_URL", "").strip()
        if not url:
            log.info(
                "control_generation: REDIS_URL not set — cross-process "
                "invalidation runs on the defensive TTL only"
            )
            return None
        try:
            import redis as _sync_redis  # sync client; redis>=5 ships both

            _client = _sync_redis.from_url(
                url,
                decode_responses=True,
                socket_timeout=1.0,
                socket_connect_timeout=1.0,
            )
        except Exception as exc:
            log.warning("control_generation: Redis client unavailable: {}", exc)
            _client = None
        return _client


def register(doc: str, invalidate: Callable[[], None]) -> None:
    """Run *invalidate* whenever *doc*'s generation moves in another process.

    Idempotent per callback identity is NOT assumed — a module registering
    twice would invalidate twice, which is harmless (an extra Firestore read)
    and cheaper than a registry that silently drops the second listener.
    """
    if doc not in _ALL_DOCS:
        raise ValueError(f"unknown control document: {doc!r}")
    with _lock:
        _listeners.setdefault(doc, []).append(invalidate)


def bump(doc: str) -> None:
    """Signal that *doc* has been written.  Called by every writer.

    Fails soft and COUNTED.  A dropped bump is not a correctness failure — the
    other container converges on its defensive TTL — but an unbounded number of
    dropped bumps means every reader is running on the slow path, which is
    precisely the state that must not be silent.
    """
    if doc not in _ALL_DOCS:
        raise ValueError(f"unknown control document: {doc!r}")
    client = _redis()
    if client is None:
        return
    try:
        client.incr(KEY_PREFIX + doc)
        with _lock:
            _stats["bumps"] += 1
    except Exception as exc:
        with _lock:
            _stats["bump_failures"] += 1
        log.warning("control_generation: bump({}) failed: {}", doc, exc)


def poll() -> List[str]:
    """Read every generation in ONE round trip; invalidate what moved.

    Returns the documents whose listeners were fired, so a caller can log a
    real event rather than a heartbeat.  Call this from a loop the process
    already runs — the monitor's 5s poll for the engine, the snapshot writer's
    cycle for the api container.  It is a Redis read, never a Firestore one.

    First observation of a generation is NOT an invalidation: at boot every
    cache is already cold, and firing here would spend a Firestore read per
    document on every restart for no information.
    """
    client = _redis()
    if client is None:
        return []
    keys = [KEY_PREFIX + d for d in _ALL_DOCS]
    try:
        values = client.mget(keys)
        with _lock:
            _stats["polls"] += 1
    except Exception as exc:
        with _lock:
            _stats["poll_failures"] += 1
        log.debug("control_generation: poll failed: {}", exc)
        return []

    moved: List[str] = []
    for doc, raw in zip(_ALL_DOCS, values or []):
        # An ABSENT key is generation zero, not "no information".  Skipping it
        # was a real defect the first test written for this found: on a fresh
        # Redis no key exists, so the first poll recorded nothing, the first
        # bump moved the key 0 -> 1, and the poll after it saw a FIRST sighting
        # and declined to invalidate.  The first kill-switch flip after a Redis
        # restart would have been swallowed — silently, because the defensive
        # TTL converges minutes later and nothing looks broken.
        try:
            remote = 0 if raw is None else int(raw)
        except (TypeError, ValueError):
            continue
        with _lock:
            previous = _seen.get(doc)
            _seen[doc] = remote
            first_sight = previous is None
            # A generation that went BACKWARDS (flushed Redis, rebuilt
            # container) is a change, not an error: "I cannot tell whether the
            # doc moved" is answered with one Firestore read, never with a
            # stale cache.
            changed = (not first_sight) and remote != previous
            callbacks = list(_listeners.get(doc, ())) if changed else []
            if changed:
                _stats["invalidations"] += 1
        if not callbacks:
            continue
        moved.append(doc)
        for cb in callbacks:
            try:
                cb()
            except Exception:
                log.exception("control_generation: invalidator for {} raised", doc)
    return moved


def stats() -> Dict[str, Any]:
    """Counters for the diag console.  A control plane whose invalidation
    channel is dead must be able to say so — bumps landing with no polls, or
    poll failures climbing, both mean every reader is on the TTL floor."""
    with _lock:
        return {
            "redis_configured": bool(os.environ.get("REDIS_URL", "").strip()),
            "documents": list(_ALL_DOCS),
            "seen": dict(_seen),
            **{k: int(v) for k, v in _stats.items()},
        }


def reset_for_test() -> None:
    global _client, _client_tried
    with _lock:
        _seen.clear()
        _listeners.clear()
        for k in _stats:
            _stats[k] = 0
        _client = None
        _client_tried = False


def set_client_for_test(client: Optional[Any]) -> None:
    """Inject a fake Redis so the bump/poll contract is testable without a
    server.  ``None`` pins the not-configured branch."""
    global _client, _client_tried
    with _lock:
        _client = client
        _client_tried = True
