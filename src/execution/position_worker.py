"""Per-user execution worker — outer loop that ties listenKey + WS together.

One :class:`PositionWorker` instance per active user.  Its
:meth:`run` method:

1. Acquires a listenKey via :func:`listen_key.acquire`.
2. Connects to the User Data Stream and consumes events.
3. On any disconnect (WS closed, listenKey expired, handler crash):
   * Closes the listenKey handle.
   * Backs off (exponential) before re-acquiring.
4. Stops cleanly on :meth:`stop`.

The event handler is INJECTED at construction time so PR-6's FSM can
plug in without modifying this module.  PR-5 ships with a default
handler that just logs each event — once PR-6 lands, the FSM
constructor will pass its own handler.

This is the scaffold module: it owns lifecycle + reconnect, NOT the
business logic.  Pre-TP firing, SL placement, BE shifting, anomaly
tripwires — all live in PR-6+ on top of this scaffold.
"""

from __future__ import annotations

import asyncio
import re
import time
from typing import Callable, Optional

from src.security.signing_service import client as signing_client
from src.utils import get_logger

from . import events as _events
from . import listen_key as _listen_key
from . import user_data_stream

log = get_logger("execution.position_worker")


EventHandler = user_data_stream.EventHandler


# Reconnect backoff for *transient* failures (Binance briefly down, WS
# blip): exponential 1s → 60s.
_MIN_BACKOFF_S = 1.0
_MAX_BACKOFF_S = 60.0

# Auth-failure backoff (dead/invalid key — 401 / -2015). A 60s retry cadence
# on a permanently-invalid key is what earned a Binance -1003 IP ban of the
# whole box (2026-07-24): ~1 req/min of guaranteed failures accumulated until
# Binance banned the shared IP, which then blocked ALL market data and cycled
# the engine. Backing a dead key off to every 15 min makes that impossible
# (the rate is far too low to trip -1003) while still auto-recovering the
# moment the user fixes the key / IP-whitelist — no reconnect required.
_AUTH_FAIL_BACKOFF_S = 900.0
# After this many consecutive auth failures we escalate the log to ERROR so
# the monitoring agent pages "key needs reconnect" — but we keep retrying
# slowly rather than disabling, so a fixed key resumes on its own.
_AUTH_ALERT_THRESHOLD = 3

# IP-ban backoff (418 / -1003). Retrying *into* an active ban only extends it,
# so wait out the ban window — parsed from Binance's own "banned until <ms>"
# when present, else a 10-min floor, capped at 1h.
_BAN_BACKOFF_S = 600.0
_BAN_MAX_BACKOFF_S = 3600.0
_BAN_UNTIL_RE = re.compile(r"banned until (\d+)")


def _ban_backoff_seconds(exc: _listen_key.ListenKeyAcquireError) -> float:
    """Seconds to wait out an IP ban — Binance's ``banned until`` if given."""
    body = exc.error_message or str(exc)
    match = _BAN_UNTIL_RE.search(body or "")
    if match:
        try:
            remaining = int(match.group(1)) / 1000.0 - time.time()
            if remaining > 0:
                return max(_BAN_BACKOFF_S, min(_BAN_MAX_BACKOFF_S, remaining + 5.0))
        except ValueError:
            pass
    return _BAN_BACKOFF_S


async def _default_handler(event: _events.Event) -> None:
    """Stub handler — logs the event at info level.

    PR-6's FSM replaces this with a real handler that mutates
    position state, fires pre-TP partials, shifts SL to BE, etc.
    Until then, the worker still RUNS and proves end-to-end WS
    plumbing works — log lines become the operator-visible
    smoke test.
    """
    log.info(
        "position_worker.default_handler: received event type={}",
        type(event).__name__,
    )


class PositionWorker:
    """Per-user worker with start / stop semantics.

    Usage from PR-9's worker manager (or smoke-test from a CLI):

        worker = PositionWorker(firebase_uid="...")
        task = asyncio.create_task(worker.run())
        # ... later ...
        await worker.stop()
        await task
    """

    def __init__(
        self,
        firebase_uid: str,
        *,
        handler: Optional[EventHandler] = None,
        signing_client_factory: Optional[
            Callable[[], signing_client.SigningClient]
        ] = None,
        ws_factory: Optional[Callable[[str], object]] = None,
    ) -> None:
        self.firebase_uid = firebase_uid
        self.handler: EventHandler = handler or _default_handler
        self._signing_client_factory = (
            signing_client_factory or signing_client.SigningClient
        )
        self._ws_factory = ws_factory
        self._stop_event = asyncio.Event()
        # Consecutive listenKey auth failures (401 / -2015). Reset on any
        # successful acquire; escalates the log to a pageable ERROR past the
        # alert threshold so a dead key can't fail silently.
        self._consecutive_auth_failures = 0

    def _backoff_for_error(
        self, exc: _listen_key.ListenKeyAcquireError
    ) -> Optional[float]:
        """Classify an acquire failure and return an override backoff.

        Returns the seconds to wait before the next attempt for an *auth
        failure* (dead key) or *IP ban*, or ``None`` for a transient error
        (caller uses its normal exponential ladder). Also owns the escalation
        logging so a dead key becomes operator-visible instead of a silent
        60s retry storm.
        """
        if exc.is_ip_ban:
            secs = _ban_backoff_seconds(exc)
            log.error(
                "position_worker: Binance IP-BAN on listenKey uid={} — backing "
                "off {:.0f}s to avoid extending the ban (retrying into an active "
                "ban only prolongs it): {}",
                self.firebase_uid, secs, exc,
            )
            return secs
        if exc.is_auth_failure:
            self._consecutive_auth_failures += 1
            if self._consecutive_auth_failures >= _AUTH_ALERT_THRESHOLD:
                log.error(
                    "position_worker: user Binance key INVALID (needs reconnect) "
                    "uid={} consecutive={} — retrying slowly (every {:.0f}s) so a "
                    "dead key can't IP-ban the box; fix the key/IP-whitelist or "
                    "disconnect it: {}",
                    self.firebase_uid, self._consecutive_auth_failures,
                    _AUTH_FAIL_BACKOFF_S, exc,
                )
            else:
                log.warning(
                    "position_worker: listenKey auth failure uid={} ({}/{}): {}",
                    self.firebase_uid, self._consecutive_auth_failures,
                    _AUTH_ALERT_THRESHOLD, exc,
                )
            return _AUTH_FAIL_BACKOFF_S
        log.warning(
            "position_worker: listenKey acquire failed uid={} exc={}",
            self.firebase_uid, exc,
        )
        return None

    async def stop(self) -> None:
        """Request shutdown.  Safe to call concurrently with :meth:`run`.

        The next reconnect-loop iteration sees the flag and exits;
        the active WS connection is closed in the consumer's finally
        block when the iterator stops.
        """
        self._stop_event.set()

    async def run(self) -> None:
        """Main loop.  Returns when :meth:`stop` is called.

        Exception policy: every iteration is wrapped — listenKey
        acquire errors, WS connect errors, handler raises (handler
        errors are logged inside ``consume``, not surfaced) all keep
        the loop running with exponential backoff.  The only way to
        exit the loop is :meth:`stop`.
        """
        backoff_s = _MIN_BACKOFF_S
        while not self._stop_event.is_set():
            handle: Optional[_listen_key.ListenKeyHandle] = None
            # Per-iteration override backoff for a classified auth failure /
            # IP ban; None means "use the transient exponential ladder".
            override_backoff: Optional[float] = None
            try:
                client = self._signing_client_factory()
                handle = await _listen_key.acquire(
                    self.firebase_uid, client=client
                )
                # Reset backoff + auth-failure streak on a successful acquire —
                # long-lived WS sessions shouldn't accumulate backoff across
                # accidental brief disconnects, and a key that just worked is
                # no longer "dead".
                backoff_s = _MIN_BACKOFF_S
                if self._consecutive_auth_failures:
                    log.info(
                        "position_worker: listenKey recovered uid={} after {} "
                        "auth failure(s)",
                        self.firebase_uid, self._consecutive_auth_failures,
                    )
                    self._consecutive_auth_failures = 0
                await user_data_stream.consume(
                    handle.listen_key,
                    self.handler,
                    ws_factory=self._ws_factory,
                )
            except _listen_key.ListenKeyAcquireError as exc:
                # Classify: a dead key (401/-2015) or an IP ban (418/-1003)
                # gets a long override backoff so it can neither hammer nor
                # extend a ban; a transient error falls through to exponential.
                override_backoff = self._backoff_for_error(exc)
            except asyncio.CancelledError:
                # Bubble up — the task is being torn down by the caller.
                if handle is not None:
                    await handle.close()
                raise
            except Exception:
                log.exception(
                    "position_worker: unexpected error in main loop uid={}",
                    self.firebase_uid,
                )
            finally:
                if handle is not None:
                    await handle.close()
            if self._stop_event.is_set():
                break
            # Backoff before reconnect. Cancellable via the stop event so a
            # stop request during sleep takes effect within the sleep window
            # rather than the full cycle.
            sleep_s = override_backoff if override_backoff is not None else backoff_s
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(), timeout=sleep_s
                )
                # If we get here, stop fired during sleep.
                break
            except asyncio.TimeoutError:
                pass  # backoff elapsed normally; retry
            if override_backoff is not None:
                # A classified long backoff already ran — reset the transient
                # ladder so a later blip starts from the bottom again.
                backoff_s = _MIN_BACKOFF_S
            else:
                backoff_s = min(backoff_s * 2.0, _MAX_BACKOFF_S)
        log.info(
            "position_worker: stopped uid={}", self.firebase_uid
        )
