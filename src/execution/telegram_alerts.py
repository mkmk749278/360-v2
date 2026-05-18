"""Typed Telegram alert dispatcher for tripwire fires + circuit-breaker trips.

Wraps the engine's ``TelegramBot.send_admin_alert`` in a small typed
verb surface so the tripwires module + KillSwitchClient + reconciler
can fire alerts without each importing the Telegram bot directly
(which would create a circular import with bootstrap.py).

Verbs (one per actionable operator event):

* :func:`alert_user_disabled` — per-user circuit breaker tripped.
* :func:`alert_global_breaker_tripped` — engine-wide circuit breaker
  tripped; auto-trade halted for ALL users until manual reset.
* :func:`alert_kill_switch_engaged` — global kill switch flipped on
  (operator action or programmatic engage).
* :func:`alert_symbol_not_allowed` — order placement attempted for a
  symbol not on the allowlist.  Highest-severity tripwire event —
  this is the breach signal.
* :func:`alert_binance_rejection` — single Binance order rejection
  worth surfacing (rare; most go to logs).

Lifecycle: :func:`init_telegram_alerts` is called once at boot from
:mod:`src.bootstrap` after the TelegramBot is constructed.  The
dispatcher silently no-ops (logs at debug) if not initialised —
production behaviour is "log via loguru only" if Telegram fails to
boot, NOT crash.  This keeps tripwire firing decoupled from the
alert plumbing's availability.

Spec contract: each ``alert_*`` returns immediately on no-op /
no-Telegram-configured paths.  They never raise — a failed alert
must not propagate up into the FSM / tripwire code path.  Worst
case: the operator misses one alert; they still see the engine log
record via journalctl / Telegram-deliverable log file.
"""

from __future__ import annotations

import threading
from typing import Any, Optional

from src.utils import get_logger

log = get_logger("execution.telegram_alerts")


# ---------------------------------------------------------------------------
# Module-level singleton — set once at boot, read on every alert.
# ---------------------------------------------------------------------------


_lock = threading.RLock()
_bot: Any = None  # TelegramBot once initialised


def init_telegram_alerts(telegram_bot: Any) -> None:
    """Register the TelegramBot instance for alert dispatch.

    Idempotent — a second call is a no-op.  ``telegram_bot`` is the
    same instance the rest of the engine uses for signal dispatch;
    we share one bot to keep the rate-limit budget unified.
    """
    global _bot
    with _lock:
        if _bot is not None:
            return
        _bot = telegram_bot
        log.info("telegram_alerts: dispatcher initialised")


def is_initialised() -> bool:
    with _lock:
        return _bot is not None


def reset_for_test() -> None:
    """Test-only: drop the singleton so tests don't bleed across."""
    global _bot
    with _lock:
        _bot = None


async def _send(text: str) -> None:
    """Internal sender.  Catches every exception so the caller never
    has to deal with Telegram availability.  Logs the alert at warn
    level even when Telegram is offline so the operator can recover
    it from the engine's log file."""
    log.warning("telegram_alerts: {}", text.replace("\n", " | "))
    with _lock:
        bot = _bot
    if bot is None:
        return
    try:
        await bot.send_admin_alert(text)
    except Exception:
        log.exception("telegram_alerts: send failed (alert lost)")


# ---------------------------------------------------------------------------
# Public alert verbs
# ---------------------------------------------------------------------------


async def alert_user_disabled(
    *, firebase_uid: str, reason: str, rejection_count: int
) -> None:
    """Per-user circuit breaker tripped (PR-8 + #431).  The user has
    been auto-disabled and persisted to Firestore — next order
    placement for them refuses.  Operator action: investigate via
    the per-user audit log, then ``/enable_user <uid>`` once the
    underlying cause is resolved (e.g. user re-issues their Binance
    key after the previous one was revoked)."""
    text = (
        "🛑 *Per-user circuit breaker tripped*\n"
        f"uid: `{firebase_uid}`\n"
        f"rejection_count: {rejection_count}\n"
        f"reason: {reason or '(not provided)'}\n"
        f"user has been auto-disabled and persisted to Firestore"
    )
    await _send(text)


async def alert_global_breaker_tripped(
    *, rejection_count: int, window_s: float
) -> None:
    """Engine-wide circuit breaker tripped (PR-8 + #431).  ALL auto-
    trade halted until manual reset.  Operator action: investigate
    the cluster of Binance rejections (likely a KMS outage, allowlist
    drift, or FSM bug); fix root cause; then ``/global_breaker_reset``
    to re-enable engine-wide.  Do NOT reset until root cause is
    understood — re-enabling into a still-broken state would
    re-trip immediately + signal subscribers that auto-trade is
    flaky."""
    text = (
        "🚨 *GLOBAL circuit breaker tripped*\n"
        f"{rejection_count} Binance rejections in last {window_s:.0f}s\n"
        f"engine-wide auto-trade HALTED until manual reset\n"
        f"investigate root cause before re-enabling"
    )
    await _send(text)


async def alert_kill_switch_engaged(*, reason: str) -> None:
    """Global kill switch flipped ON.  Could be operator action via
    Telegram bot, programmatic engage from the global circuit breaker,
    or an explicit panic call from somewhere in the engine.  All
    auto-trade halted within 5s."""
    text = (
        "🚨 *Kill switch ENGAGED*\n"
        f"reason: {reason or '(none provided)'}\n"
        f"engine-wide auto-trade halted within 5s SLA"
    )
    await _send(text)


async def alert_symbol_not_allowed(
    *, firebase_uid: str, symbol: str
) -> None:
    """Order placement attempted for a symbol NOT on the tripwire
    allowlist.  This is the strongest breach signal in the tripwire
    taxonomy — nothing in normal operation should try to trade an
    out-of-list symbol.  Engaging the global kill switch on this
    trigger is the default response (caller does the engage; this
    alert is informational on top)."""
    text = (
        "🛑 *SYMBOL ALLOWLIST VIOLATION* — possible breach signal\n"
        f"uid: `{firebase_uid}`\n"
        f"attempted symbol: `{symbol}`\n"
        f"order REJECTED — caller should engage global kill switch"
    )
    await _send(text)


async def alert_binance_rejection(
    *, firebase_uid: str, signal_id: str, code: str, message: str
) -> None:
    """A single Binance rejection worth surfacing.  Most rejections
    only hit loguru — this verb is for the cases where the operator
    wants Telegram-visible escalation (e.g. -2010 insufficient margin
    on the first signal after the user's wallet drained).

    Use sparingly: rate-limited rejections aren't worth alerting on
    (the per-user breaker handles those); BAN-level rejections are."""
    text = (
        "⚠️  *Binance rejection*\n"
        f"uid: `{firebase_uid}` signal_id: `{signal_id}`\n"
        f"code: `{code}`\n"
        f"message: {message}"
    )
    await _send(text)
