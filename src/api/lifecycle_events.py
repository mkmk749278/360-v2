"""User-lifecycle alerts — the four moments worth a phone buzz (2026-09-15).

Owner ask: *"Can we get Alerts to telegram on every new user joined?"*, scoped
by him to four moments — account created, onboarding completed, Binance key
connected, trial claimed or first payment.

Why this is a QUEUE and not a Telegram call
───────────────────────────────────────────
Every one of those moments happens in the **api** container, and
``src/api/main.py`` says in as many words that a live ``TelegramBot`` is *only*
available in the **engine** container — the api process falls back to
``LogOnlyOtpProvider`` for exactly this reason.  So a ``send_admin_alert()``
call at the insert site would be a silent no-op in production while passing
every test that patched the bot.  That is ``INDEX COLD`` and the promotion
census verbatim: *which process holds the state is not a deployment detail.*

So the api side only ever **records an event**; the engine, which owns the
bot, sends it (:mod:`src.execution.lifecycle_alert_bridge`).  Same shape as
``safety_switch_bridge`` and ``manual_take``.

Why emitting is a deque and not an await
────────────────────────────────────────
:meth:`UserStore.get_or_create_by_firebase_uid` is **synchronous and holds a
write lock**, and its async wrappers run it on a worker thread — so at the
call site there may be no running event loop, and anything that blocks is
blocking a signup.  :func:`emit` therefore appends to a bounded deque
(thread-safe, O(1), cannot raise) and a pump task owned by the api process
drains it to Redis.  A signup must never fail, or even slow down, because a
chat message could not be delivered.

Bounds, because an alert path is still a path
─────────────────────────────────────────────
The deque is capped and counts what it drops.  The *vendor* bound lives on the
engine side, where the Telegram call actually happens — a cap enforced only at
the producer is a cap that a second producer walks straight past.

PII
───
The alert carries a **masked** phone (``+91 •••••••23``) and the numeric user
id, never the full number.  The owner chose this: Telegram history is
long-lived, third-party, and not something we can redact later, and ops can
already resolve a user id to the real number behind the auth gate.
:func:`mask_phone` is the only formatter, so there is one place to audit.
"""
from __future__ import annotations

import time
from collections import deque
from typing import Any, Deque, Dict, Optional

import config
from src.utils import get_logger

log = get_logger("api.lifecycle_events")

#: The events this channel may carry. A literal set rather than a free string:
#: the engine formats whatever arrives, so an unknown name must be refused
#: there rather than rendered as a message nobody wrote.
EVENT_SIGNUP = "signup"
EVENT_ONBOARDED = "onboarded"
EVENT_KEY_CONNECTED = "key_connected"
EVENT_TRIAL_CLAIMED = "trial_claimed"
EVENT_PAID = "paid"

EVENTS = frozenset({
    EVENT_SIGNUP,
    EVENT_ONBOARDED,
    EVENT_KEY_CONNECTED,
    EVENT_TRIAL_CLAIMED,
    EVENT_PAID,
})

_queue: Deque[Dict[str, Any]] = deque(maxlen=int(config.LIFECYCLE_ALERT_QUEUE_MAX))
_dropped = 0
_emitted = 0


def mask_phone(phone_e164: Optional[str]) -> str:
    """``+919876543210`` → ``+91 •••••••10``.

    Keeps the country code (useful — it says which market an install came
    from) and the last two digits (enough to match against a support message),
    and discloses nothing else. Returns ``"unknown"`` rather than an empty
    string, because a blank in a message reads as a formatting bug.
    """
    if not phone_e164:
        return "unknown"
    digits = "".join(ch for ch in phone_e164 if ch.isdigit())
    if len(digits) < 4:
        # Too short to mask meaningfully — say so rather than print a stub
        # that looks like a real number.
        return "unknown"
    cc = digits[:2]
    tail = digits[-2:]
    hidden = "•" * max(3, len(digits) - 4)
    return f"+{cc} {hidden}{tail}"


def emit(
    event: str,
    *,
    user_id: Optional[int] = None,
    phone_e164: Optional[str] = None,
    detail: Optional[str] = None,
) -> None:
    """Record a lifecycle event for the engine to announce.

    Never raises and never blocks — callers are on a signup path, and some of
    them hold a SQLite write lock. An unknown event name is dropped here with
    a WARN rather than travelling to the engine to be refused there.
    """
    global _dropped, _emitted
    try:
        if not config.LIFECYCLE_ALERTS_ENABLED:
            return
        if event not in EVENTS:
            log.warning("lifecycle_events: unknown event {!r}, dropped", event)
            return
        if len(_queue) == _queue.maxlen:
            # deque drops the oldest silently; count it, or a flood reads as
            # a quiet day.
            _dropped += 1
        _queue.append({
            "event": event,
            "user_id": user_id,
            "phone_masked": mask_phone(phone_e164),
            "detail": detail,
            "ts": time.time(),
        })
        _emitted += 1
    except Exception:  # pragma: no cover — defensive; a chat message is never
        # worth failing a signup for, and this path has no safe re-raise.
        log.exception("lifecycle_events: emit failed for {!r}", event)


def drain(limit: int = 32) -> list:
    """Pop up to *limit* events, oldest first. Used by the api-side pump."""
    out = []
    while _queue and len(out) < limit:
        out.append(_queue.popleft())
    return out


def stats() -> Dict[str, int]:
    """Counters for ops — emitted, still queued, and dropped on overflow."""
    return {"emitted": _emitted, "queued": len(_queue), "dropped": _dropped}


def reset_for_tests() -> None:
    global _dropped, _emitted
    _queue.clear()
    _dropped = 0
    _emitted = 0


async def pump(redis_client: Any, interval: float = 1.0) -> None:
    """Drain the in-process queue into Redis for the engine to announce.

    Owned by whichever process serves HTTP: the api container in isolated
    mode, the engine itself in single-process mode. Runs forever; a Redis
    failure is counted and retried rather than raised, because the caller is
    a startup task and the alternative is a dead pump nobody notices.
    """
    import asyncio
    import json

    from src import fail_open
    from src.api import snapshot_store as _store

    log.info("lifecycle pump started — {} → {}", "queue", _store.KEY_CMD_LIFECYCLE)
    while True:
        try:
            batch = drain()
            for env in batch:
                await redis_client.client.lpush(
                    _store.KEY_CMD_LIFECYCLE, json.dumps(env),
                )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            # Re-queueing the batch would risk duplicating an alert on a
            # partial failure; an alert missed is better than an alert sent
            # twice, and the loss is counted rather than silent.
            fail_open.record("lifecycle_events.pump", exc)
        await asyncio.sleep(interval)
