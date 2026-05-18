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
from typing import Awaitable, Callable, Optional

from src.security.signing_service import client as signing_client
from src.utils import get_logger

from . import events as _events
from . import listen_key as _listen_key
from . import user_data_stream

log = get_logger("execution.position_worker")


EventHandler = user_data_stream.EventHandler


# Reconnect backoff: cap at 60s.  A persistent failure (Binance down,
# user revoked the API key) is bounded but not silent — the next
# reconnect attempt fires every minute, giving operator alerts time
# to fire and Telegram to be checked.
_MIN_BACKOFF_S = 1.0
_MAX_BACKOFF_S = 60.0


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
            try:
                client = self._signing_client_factory()
                handle = await _listen_key.acquire(
                    self.firebase_uid, client=client
                )
                # Reset backoff on a successful acquire — long-lived
                # WS sessions shouldn't accumulate backoff across
                # accidental brief disconnects.
                backoff_s = _MIN_BACKOFF_S
                await user_data_stream.consume(
                    handle.listen_key,
                    self.handler,
                    ws_factory=self._ws_factory,
                )
            except _listen_key.ListenKeyAcquireError as exc:
                log.warning(
                    "position_worker: listenKey acquire failed uid={} exc={}",
                    self.firebase_uid,
                    exc,
                )
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
            # Exponential backoff before reconnect.  Cancellable via
            # the stop event so a stop request during sleep takes
            # effect within ``backoff_s`` rather than the full cycle.
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(), timeout=backoff_s
                )
                # If we get here, stop fired during sleep.
                break
            except asyncio.TimeoutError:
                pass  # backoff elapsed normally; retry
            backoff_s = min(backoff_s * 2.0, _MAX_BACKOFF_S)
        log.info(
            "position_worker: stopped uid={}", self.firebase_uid
        )
