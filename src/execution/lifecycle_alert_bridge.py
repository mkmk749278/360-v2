"""Engine-side consumer for user-lifecycle alerts (2026-09-15).

The four moments the owner asked to be told about — account created,
onboarding completed, Binance key connected, trial claimed or first payment —
all happen in the **api** container. The live ``TelegramBot`` exists only in
the **engine** container (``src/api/main.py`` says so at the OTP fallback).
So the api records and this consumes, exactly as ``safety_switch_bridge`` and
``manual_take`` already do.

Three deliberate differences from the safety-switch bridge, because the two
channels answer different questions:

* **No result key.** Nobody is waiting on a chat message. The switch bridge
  guarantees every envelope gets a result because *"a flip whose outcome
  nobody confirmed is not a flip"*; a signup alert has no such caller.
* **Stale is late, not wrong.** The switch bridge refuses an envelope older
  than 30s — an operator who gave up has taken another action by now.
  A signup that happened while the engine was restarting is still worth
  knowing about, so an old event is **sent with its age stamped** rather than
  dropped. Silence about a real signup is the worse failure here.
* **A vendor cap, enforced at the top of the loop.** 2026-09-01 cost every
  paid user ~4h of auto-trade because a budget was spent only on the branch
  that did work. Here the cap is decremented per *event examined*, before any
  Bot API call, so a burst cannot become an unbounded run of vendor calls —
  and the overflow is coalesced into one line rather than dropped, because a
  flood must read as a flood and not as a quiet day.

Like the switch bridge, the event **name** is a key into a literal table a
reviewer can read. This channel formats messages and can do nothing else: it
cannot place an order, read a secret, or reach the money path.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, List, Optional

import config
from src.api import snapshot_store as _store
from src import fail_open
from src.utils import get_logger

log = get_logger("execution.lifecycle_alert_bridge")

_ERROR_BACKOFF_S = 3.0
_BRPOP_TIMEOUT_S = 5
#: Bounded drain per wake, so a backlog cannot starve the loop it shares.
_MAX_PER_CYCLE = 20
#: Past this, an event is described as late rather than presented as news.
_LATE_AFTER_S = 300.0

#: event name → (emoji, headline). A literal table rather than a format
#: string built from the payload: an unknown name renders under its own raw
#: name badged, never as a sentence nobody wrote.
_HEADLINE: Dict[str, str] = {
    "signup": "🎉 New user joined",
    "onboarded": "✅ Onboarding completed",
    "key_connected": "🔐 Binance key connected",
    "trial_claimed": "🎁 Free trial claimed",
    "paid": "💳 Subscription paid",
}


def format_event(env: Dict[str, Any], *, now: Optional[float] = None) -> str:
    """One alert line. Pure, so a test can pin the wording."""
    now = time.time() if now is None else now
    name = str(env.get("event") or "")
    head = _HEADLINE.get(name) or f"• {name or 'unknown'} (unclassified)"
    bits: List[str] = [head]
    uid = env.get("user_id")
    if uid is not None:
        bits.append(f"user #{uid}")
    phone = env.get("phone_masked")
    if phone:
        bits.append(str(phone))
    detail = env.get("detail")
    if detail:
        bits.append(str(detail))
    line = " · ".join(bits)
    try:
        age = now - float(env.get("ts") or now)
    except (TypeError, ValueError):
        age = 0.0
    if age > _LATE_AFTER_S:
        # Say it is late rather than let a restart backlog read as a burst of
        # signups that just happened.
        line += f"  _(delivered {int(age // 60)}m late)_"
    return line


class LifecycleAlertConsumer:
    """Drain the lifecycle queue and announce to the admin chat."""

    def __init__(self, redis_client: Any, telegram_bot: Any) -> None:
        self._redis = redis_client
        self._bot = telegram_bot
        self._window_start = 0.0
        self._sent_in_window = 0
        self._suppressed = 0
        self.sent = 0
        self.refused = 0

    # -- rate cap ---------------------------------------------------------
    def _allow(self, now: float) -> bool:
        """True when a Bot API call is still inside this minute's budget.

        Spent per event EXAMINED, at the top of the loop, so the do-nothing
        branch is bounded too — the 2026-09-01 lesson, in the one place here
        that talks to a vendor.
        """
        if now - self._window_start >= 60.0:
            if self._suppressed:
                # The window closed with events we never sent. Say so once.
                asyncio.ensure_future(self._flush_suppressed())
            self._window_start = now
            self._sent_in_window = 0
        cap = int(config.LIFECYCLE_ALERT_MAX_PER_MIN)
        if cap > 0 and self._sent_in_window >= cap:
            self._suppressed += 1
            return False
        self._sent_in_window += 1
        return True

    async def _flush_suppressed(self) -> None:
        n, self._suppressed = self._suppressed, 0
        if n <= 0:
            return
        try:
            await self._bot.send_admin_alert(
                f"… and {n} more lifecycle event(s) in the last minute "
                f"(rate cap {config.LIFECYCLE_ALERT_MAX_PER_MIN}/min)"
            )
        except Exception as exc:  # pragma: no cover
            fail_open.record("lifecycle_alert_bridge.flush_suppressed", exc)

    # -- loop -------------------------------------------------------------
    async def _send(self, env: Dict[str, Any]) -> None:
        now = time.time()
        if not self._allow(now):
            return
        try:
            ok = await self._bot.send_admin_alert(format_event(env, now=now))
            if ok:
                self.sent += 1
            else:
                # A bot with no admin chat configured returns False. That is
                # a configuration fact, not an exception — count it so the
                # difference between "off" and "broken" stays visible.
                self.refused += 1
        except Exception as exc:
            fail_open.record("lifecycle_alert_bridge.send", exc)

    async def _cycle(self) -> None:
        item = await self._redis.client.brpop(
            _store.KEY_CMD_LIFECYCLE, timeout=_BRPOP_TIMEOUT_S,
        )
        drained = 0
        while item is not None and drained < _MAX_PER_CYCLE:
            raw = item[1] if isinstance(item, (tuple, list)) else item
            drained += 1
            try:
                env = json.loads(raw)
            except (TypeError, ValueError):
                log.warning("lifecycle: dropping malformed envelope {!r}", raw)
                env = None
            if isinstance(env, dict):
                await self._send(env)
            if drained >= _MAX_PER_CYCLE:
                break
            item = await self._redis.client.rpop(_store.KEY_CMD_LIFECYCLE)

    async def start(self) -> None:
        """Run the drain loop. Async and long-lived, matching
        ``SafetySwitchConsumer.start`` so bootstrap wires both the same way."""
        log.info(
            "LifecycleAlertConsumer started — draining {} (brpop {}s, cap {}/min)",
            _store.KEY_CMD_LIFECYCLE, _BRPOP_TIMEOUT_S,
            config.LIFECYCLE_ALERT_MAX_PER_MIN,
        )
        while True:
            try:
                await self._cycle()
            except asyncio.CancelledError:
                log.info("LifecycleAlertConsumer stopped")
                raise
            except Exception as exc:
                fail_open.record("lifecycle_alert_bridge.cycle", exc)
                log.exception("LifecycleAlertConsumer: cycle failed")
                await asyncio.sleep(_ERROR_BACKOFF_S)

    def health(self) -> Dict[str, int]:
        return {
            "sent": self.sent,
            "refused": self.refused,
            "suppressed_pending": self._suppressed,
            "sent_this_window": self._sent_in_window,
        }
