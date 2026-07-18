"""Manual-take command consumer — engine side of ``POST /api/auto-trade/take``.

Owner-approved 2026-07-17.  In isolated mode (``API_PROCESS_ISOLATED=true``)
the api container cannot touch the live signal book or the FSM, so a user's
"Take trade" tap flows through Redis:

    api container                       engine container (this module)
    ─────────────                       ──────────────────────────────
    LPUSH snapshot:cmd:take             BRPOP snapshot:cmd:take (FIFO)
      {request_id, uid,                   → engine.take_signal_for_user()
       signal_id, ts}                     → SET snapshot:take_result:<id>
    poll take_result:<id> ≤ ~8s  ◄──────────  (TTL 120s)

Why a LIST + BRPOP instead of the single-value command keys the mode/reset
commands use: a take carries a per-user payload and multiple users can take
concurrently — overwrite-in-place would drop requests.  BRPOP also gives
sub-second consume latency (the SnapshotWriter's 15 s poll cycle would feel
broken for a button tap) without adding any polling reads (the block happens
server-side in Redis; zero cost while idle — Cost Discipline clean).

The consumer is deliberately defensive: every envelope is processed inside
its own try/except, malformed JSON is dropped with a log line, stale
envelopes (engine was down while the user tapped) are answered with a
rejection rather than firing a minutes-late market order, and a result is
written for every consumed envelope so the api's poll never hangs on a
consumed-but-unanswered request.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict

from src.api import snapshot_store as _store
from src.utils import get_logger

log = get_logger("execution.manual_take")

# Small pause after an unexpected error so a persistent Redis failure
# can't spin this loop hot.
_ERROR_BACKOFF_S = 3.0
# BRPOP block window — short enough that cancellation at shutdown is
# prompt, long enough that idle cost is one blocked command per window.
_BRPOP_TIMEOUT_S = 5


class ManualTakeConsumer:
    """Drains ``snapshot:cmd:take`` and answers each request.

    Started by bootstrap alongside the SnapshotWriter (isolated mode
    only — single-process mode calls ``engine.take_signal_for_user``
    directly from the route handler, no Redis hop).
    """

    def __init__(self, engine: Any, redis_client: Any) -> None:
        self._engine = engine
        self._redis = redis_client

    async def start(self) -> None:
        log.info(
            "ManualTakeConsumer started — draining {} (brpop {}s)",
            _store.KEY_CMD_TAKE, _BRPOP_TIMEOUT_S,
        )
        while True:
            try:
                if not self._redis.available:
                    await asyncio.sleep(_ERROR_BACKOFF_S)
                    continue
                item = await self._redis.client.brpop(
                    _store.KEY_CMD_TAKE, timeout=_BRPOP_TIMEOUT_S,
                )
                if item is None:
                    continue  # timed out — loop again
                _key, raw = item
                await self._process(raw)
            except asyncio.CancelledError:
                log.info("ManualTakeConsumer stopped")
                raise
            except Exception:
                log.exception("ManualTakeConsumer: cycle failed")
                await asyncio.sleep(_ERROR_BACKOFF_S)

    async def _process(self, raw: str) -> None:
        """Handle one envelope; always writes a result for a parseable
        request_id so the api's poll resolves."""
        try:
            envelope = json.loads(raw)
        except (TypeError, ValueError):
            log.warning(
                "ManualTakeConsumer: dropping malformed envelope {!r}", raw,
            )
            return
        # Envelope kind routes the command. "take" (default, back-compat) is
        # the signal take; "manual_trade" is the manual trade builder. Both
        # share this queue + the take_result key so one consumer + one bridge
        # serve both.
        if str(envelope.get("kind") or "take") == "manual_trade":
            await self._process_manual_trade(envelope, raw)
            return
        request_id = str(envelope.get("request_id") or "")
        uid = str(envelope.get("uid") or "")
        signal_id = str(envelope.get("signal_id") or "")
        ts = envelope.get("ts")
        if not (request_id and uid and signal_id):
            log.warning(
                "ManualTakeConsumer: dropping incomplete envelope {!r}", raw,
            )
            return
        try:
            age_s = time.time() - float(ts)
        except (TypeError, ValueError):
            age_s = 0.0
        if age_s > _store.TAKE_CMD_STALE_S:
            # The engine was down (or wedged) when the user tapped —
            # refusing beats firing a market order minutes after the
            # user's intent, at a price they never saw.
            result: Dict[str, Any] = {
                "outcome": "rejected",
                "reject_class": "TakeRequestStale",
                "reject_detail": (
                    f"Take request was {age_s:.0f}s old when the engine "
                    f"picked it up — refused for your safety. Try again."
                ),
                "signal_id": signal_id,
            }
            log.warning(
                "ManualTakeConsumer: stale envelope uid={} signal_id={} "
                "age={:.0f}s — rejected",
                uid, signal_id, age_s,
            )
        else:
            log.info(
                "ManualTakeConsumer: take uid={} signal_id={} (age={:.1f}s)",
                uid, signal_id, age_s,
            )
            try:
                result = await self._engine.take_signal_for_user(uid, signal_id)
            except Exception as exc:
                log.exception(
                    "ManualTakeConsumer: take crashed uid={} signal_id={}",
                    uid, signal_id,
                )
                result = {
                    "outcome": "rejected",
                    "reject_class": type(exc).__name__,
                    "reject_detail": str(exc),
                    "signal_id": signal_id,
                }
        try:
            await self._redis.client.set(
                _store.KEY_TAKE_RESULT_PREFIX + request_id,
                json.dumps(result, default=str),
                ex=_store.TTL_TAKE_RESULT,
            )
        except Exception:
            # The order outcome is already durable in dispatch_log /
            # position_state — losing the ephemeral result key only
            # degrades the app's synchronous answer to "check Recent
            # Activity".  Never let it look like the take failed.
            log.exception(
                "ManualTakeConsumer: result write failed request_id={} "
                "(order outcome itself is recorded in dispatch_log)",
                request_id,
            )

    async def _process_manual_trade(
        self, envelope: Dict[str, Any], raw: str
    ) -> None:
        """Handle a manual trade builder envelope (kind="manual_trade").

        Same staleness + always-write-a-result contract as the take path, but
        the payload is the user's chart geometry and the engine call is
        ``build_manual_trade_for_user``.
        """
        request_id = str(envelope.get("request_id") or "")
        uid = str(envelope.get("uid") or "")
        payload = envelope.get("payload")
        ts = envelope.get("ts")
        if not (request_id and uid and isinstance(payload, dict)):
            log.warning(
                "ManualTakeConsumer: dropping incomplete manual_trade "
                "envelope {!r}", raw,
            )
            return
        ref_id = str(payload.get("ref_id") or "")
        try:
            age_s = time.time() - float(ts)
        except (TypeError, ValueError):
            age_s = 0.0
        if age_s > _store.TAKE_CMD_STALE_S:
            # Engine was down/wedged when the user hit Confirm — refusing beats
            # firing a market/limit order minutes after their intent.
            result: Dict[str, Any] = {
                "outcome": "rejected",
                "reject_class": "TradeRequestStale",
                "reject_detail": (
                    f"Trade request was {age_s:.0f}s old when the engine "
                    "picked it up — refused for your safety. Try again."
                ),
                "ref_id": ref_id,
            }
            log.warning(
                "ManualTakeConsumer: stale manual_trade envelope uid={} "
                "ref_id={} age={:.0f}s — rejected", uid, ref_id, age_s,
            )
        else:
            log.info(
                "ManualTakeConsumer: manual_trade uid={} ref_id={} "
                "(age={:.1f}s)", uid, ref_id, age_s,
            )
            try:
                result = await self._engine.build_manual_trade_for_user(
                    uid, payload
                )
            except Exception as exc:
                log.exception(
                    "ManualTakeConsumer: manual_trade crashed uid={} "
                    "ref_id={}", uid, ref_id,
                )
                result = {
                    "outcome": "rejected",
                    "reject_class": type(exc).__name__,
                    "reject_detail": str(exc),
                    "ref_id": ref_id,
                }
        try:
            await self._redis.client.set(
                _store.KEY_TAKE_RESULT_PREFIX + request_id,
                json.dumps(result, default=str),
                ex=_store.TTL_TAKE_RESULT,
            )
        except Exception:
            log.exception(
                "ManualTakeConsumer: manual_trade result write failed "
                "request_id={} (outcome recorded in dispatch_log)", request_id,
            )
