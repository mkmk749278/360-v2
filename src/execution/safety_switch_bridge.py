"""Engine-side consumer for the safety switches — so the stop can always be
thrown (2026-09-02).

``POST /api/kill-switch`` raised **503** whenever the process serving it had no
Firestore client:

    raise HTTPException(503, "kill switch not initialised (no Firestore/GCP creds)")

In isolated mode that process is the ``api`` container, which initialises the
keystore and the kill switch under a *stricter* precondition than the engine's
own boot path — both ``FIREBASE_PROJECT_ID`` **and**
``FIREBASE_SERVICE_ACCOUNT_PATH``, where ``bootstrap.py`` needs only the
project and falls back to ADC.  So the api container can be blind to Firestore
while the engine trades perfectly, and every control surface the owner reads is
served by the blind one.

That made B18's *"a kill-switch flip takes effect in under five seconds"*
**unmeetable from the control plane**, with nothing red anywhere to say so —
ops rendered it in the grey it uses for footnotes.  A safety control that
cannot be operated is a Tier-0 fault, and this one failed silently.

The precondition is fixed too (``src/api/main.py`` now mirrors the engine's).
This module is the belt: a credentials, container, or deployment-mode change
can break the api container's client again, and when it does the emergency
stop must still work.  **The engine container is the one that certainly has a
Firestore client** — it is the process placing the orders — so the flip is
routed to it.

Design notes
────────────
* **BRPOP, not the SnapshotWriter's cycle.**  That loop runs every ~15 s, and
  an emergency stop must not wait on a telemetry cycle.  Blocking server-side
  costs nothing while idle (the same reasoning ``manual_take`` records for a
  button tap, with more at stake).
* **A switch NAME, never a command.**  The envelope carries one of four names
  from :data:`_SWITCHES` and a boolean; anything else is refused here.  This
  channel can reach the four safety flags and nothing else — it cannot place
  an order, read a secret, or run code.
* **A stale envelope is refused, and the window is short.**  An operator who
  gave up waiting on an emergency stop has taken another action by now;
  applying their flip minutes later, from an engine that has just come back, is
  worse than refusing it.  30 s, against the diag channel's 60.
* **Every consumed envelope gets a result.**  A flip whose outcome nobody
  confirmed is not a flip — the api's poll must never hang, and "the engine did
  not answer" must be sayable.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Callable, Dict

from src.api import snapshot_store as _store
from src.utils import get_logger

log = get_logger("execution.safety_switch_bridge")

_ERROR_BACKOFF_S = 3.0
#: Short enough that shutdown cancellation is prompt, long enough that idle
#: costs one blocked command per window.
_BRPOP_TIMEOUT_S = 5


def _apply(client: Any, switch: str, value: bool, reason: str) -> None:
    """Map a switch NAME onto the client method that owns it.

    Written as a dispatch table rather than ``getattr`` so the set of things
    this channel can do is a literal a reviewer can read, and so a future
    method on ``KillSwitchClient`` is not reachable from Redis by accident.
    """
    if switch == "kill_switch":
        if value:
            client.engage_global(reason=reason or "ops control plane")
        else:
            client.disengage_global()
    elif switch == "auto_trade_global":
        if value:
            client.enable_global_auto_trade()
        else:
            client.disable_global_auto_trade()
    elif switch == "signal_expiry":
        client.set_signal_expiry_enabled(value)
    elif switch == "play_billing":
        client.set_billing_enabled(value)
    else:  # pragma: no cover - guarded by _SWITCHES before we get here
        raise ValueError(f"unknown switch: {switch!r}")


#: The complete set of names this channel accepts.  Keep it and :func:`_apply`
#: in step — ``tests/test_safety_switch_bridge.py`` asserts they agree, because
#: a name accepted here and unhandled there would be a silent no-op on a
#: safety control, which is the exact failure mode this module exists to end.
_SWITCHES = ("kill_switch", "auto_trade_global", "signal_expiry", "play_billing")


class SafetySwitchConsumer:
    """Drains ``snapshot:cmd:switch`` and answers each request.

    Started by bootstrap alongside the SnapshotWriter in isolated mode only —
    in single-process mode the route handler holds the client itself and there
    is no hop.
    """

    def __init__(
        self,
        redis_client: Any,
        get_client: Callable[[], Any] | None = None,
    ) -> None:
        self._redis = redis_client
        self._get_client = get_client or self._default_get_client

    @staticmethod
    def _default_get_client() -> Any:
        from src.execution import kill_switch as _ks

        return _ks.get_client()

    async def start(self) -> None:
        log.info(
            "SafetySwitchConsumer started — draining {} (brpop {}s)",
            _store.KEY_CMD_SWITCH, _BRPOP_TIMEOUT_S,
        )
        while True:
            try:
                if not self._redis.available:
                    await asyncio.sleep(_ERROR_BACKOFF_S)
                    continue
                item = await self._redis.client.brpop(
                    _store.KEY_CMD_SWITCH, timeout=_BRPOP_TIMEOUT_S,
                )
                if item is None:
                    continue
                _key, raw = item
                await self._process(raw)
            except asyncio.CancelledError:
                log.info("SafetySwitchConsumer stopped")
                raise
            except Exception:
                log.exception("SafetySwitchConsumer: cycle failed")
                await asyncio.sleep(_ERROR_BACKOFF_S)

    async def _process(self, raw: str) -> None:
        try:
            env = json.loads(raw)
        except (TypeError, ValueError):
            log.warning("SafetySwitchConsumer: dropping malformed envelope {!r}", raw)
            return
        request_id = str(env.get("request_id") or "")
        switch = str(env.get("switch") or "")
        reason = str(env.get("reason") or "")
        ts = env.get("ts")
        if not request_id:
            log.warning("SafetySwitchConsumer: envelope with no request_id, dropped")
            return
        value = env.get("value")
        if not isinstance(value, bool):
            result = _fail(switch, "value must be a boolean")
        elif switch not in _SWITCHES:
            result = _fail(switch, f"unknown switch {switch!r}")
        else:
            try:
                age_s = time.time() - float(ts)
            except (TypeError, ValueError):
                age_s = 0.0
            if age_s > _store.SWITCH_CMD_STALE_S:
                result = _fail(
                    switch,
                    f"request was {age_s:.0f}s old when the engine picked it "
                    f"up — refused rather than applied late. Try again.",
                )
                log.warning(
                    "SafetySwitchConsumer: STALE {} value={} age={:.0f}s — refused",
                    switch, value, age_s,
                )
            else:
                result = await asyncio.to_thread(
                    self._apply_blocking, switch, value, reason
                )
        try:
            await self._redis.client.set(
                _store.KEY_SWITCH_RESULT_PREFIX + request_id,
                json.dumps(result, default=str),
                ex=_store.TTL_SWITCH_RESULT,
            )
        except Exception:
            # Unlike a take, the outcome here is NOT recorded anywhere else the
            # operator can see quickly, so losing the result key means they are
            # told nothing about an emergency stop they just tried to throw.
            # Log it loudly; the api's poll will time out and say so.
            log.exception(
                "SafetySwitchConsumer: result write failed request_id={} "
                "switch={} — the flip itself may well have landed",
                request_id, switch,
            )

    def _apply_blocking(self, switch: str, value: bool, reason: str) -> Dict[str, Any]:
        """Run the Firestore write on a thread; report what happened."""
        try:
            client = self._get_client()
        except Exception as exc:
            log.exception("SafetySwitchConsumer: no kill-switch client in the engine")
            return _fail(switch, f"engine has no kill-switch client: {exc}")
        try:
            _apply(client, switch, value, reason)
        except Exception as exc:
            log.exception(
                "SafetySwitchConsumer: {} := {} failed", switch, value
            )
            return _fail(switch, f"{type(exc).__name__}: {exc}")
        log.warning(
            "SafetySwitchConsumer: {} := {} applied via the control plane "
            "(reason={!r})", switch, value, reason,
        )
        return {"ok": True, "switch": switch, "value": value, "applied_by": "engine"}


def _fail(switch: str, error: str) -> Dict[str, Any]:
    return {"ok": False, "switch": switch, "error": error, "applied_by": "engine"}
