"""D1 — the engine's Slack packet poster. A SURFACE, never a link in the chain.

What this is, and what it is emphatically not
---------------------------------------------
The engine posts a short report into the owner's Slack channel: a delivered
signal when its governor arm opens, and a governor verdict that is not
``MAINTAIN``. He reads it on his phone, where he already is, and when he wants
a judgement pass he ``@Claude``s the thread himself.

**Nothing reads Slack back.** There is no return path, no verdict depends on a
post, and this whole module failing changes no exit, no order and no signal.
That standing is measured rather than chosen — `docs/PLAN_AI_TRADE_GOVERNOR_V2`
§6.2a. The Claude Slack app was posted to twice on 2026-09-04, once from the
connector and once from a plain incoming webhook, in a channel it belongs to
and where a message typed by the owner gets a reply in seconds. It did not
answer either time, and the mechanism is structural: it runs a session under
the connected account of the PERSON who mentioned it, and a webhook message has
no person behind it. The session-scoped inbound webhook answers 401, sealed to
a service the VPS cannot hold a credential for. **Both engine-to-analyst wake
routes are measured dead**, so the automatic analyst is the engine's own model
call and this is a report about it.

Written down because the next reader will otherwise re-run those tests, and
because a lane built on the assumption that Slack can wake something would be a
watchdog that fails silently — the one shape this repo refuses outright.

Default OFF
-----------
A new outbound loop on the trading box ships disarmed and is armed by the owner
after one watched cycle. On 2026-09-01 a default-ON sweep got this IP
rate-limited off Binance and took auto-trade down for every paid user for about
four hours; the default is that incident report.

The budget is spent at the TOP
------------------------------
Per the same incident: the cap decrements per packet EXAMINED, before the HTTP
call and before any per-packet work, so it bounds the branch that does nothing
as well as the branch that posts. A budget that only decrements on success is a
retry storm on the path production actually takes.

The secret
----------
The webhook URL is a write capability on the channel. It is never logged, never
rendered into an error, and never put in a diag payload — and because an
aiohttp exception string can carry the URL it was dialling, every recorded
detail goes through `_redact` rather than being trusted to be clean.
"""
from __future__ import annotations

import asyncio
import json
import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional

import aiohttp

from src import fail_open
from src.utils import get_logger

log = get_logger("slack_packet")

# Outcome vocabulary, mirroring `llm_client`'s so a reader moving between the
# two lanes does not have to learn a second set of words for the same states.
OK = "ok"
NOT_CONFIGURED = "not_configured"   # no webhook URL — the lane is off, not broken
DISABLED = "disabled"               # the switch is off, which is a decision
TIMEOUT = "timeout"
HTTP_ERROR = "http_error"           # Slack answered non-2xx
TRANSPORT_ERROR = "transport_error"  # never reached Slack
BUDGET_EXHAUSTED = "budget_exhausted"
QUEUE_FULL = "queue_full"

#: Packet kinds. Named apart because they answer different questions and a
#: reader filtering the channel wants one or the other.
KIND_SIGNAL = "signal"
KIND_VERDICT = "verdict"

#: Bounded outbound queue. Small on purpose: this is a report, and a backlog
#: older than a few minutes describes a market that has moved. Dropping the
#: OLDEST is deliberate — the newest packet is the one still worth reading.
_QUEUE_MAX = 64
_queue: Deque[Dict[str, Any]] = deque(maxlen=_QUEUE_MAX)
_queue_lock = threading.RLock()

#: Rolling window of send timestamps for the per-hour bound.
_send_times: Deque[float] = deque(maxlen=4096)

#: What Slack itself said, newest last. The unbounded counts sit beside it:
#: `place_failed` on the trail governor was an integer that could not say
#: whether the exchange objected to the level, the rounding or the key, and
#: those have three different fixes. A counter is not a cause on a path that
#: talks to a vendor.
_RESPONSE_RING = 20

_lock = threading.RLock()
_drain_running = False


def _blank_health() -> Dict[str, Any]:
    return {
        "queued": 0,
        "posted": 0,
        "dropped_queue_full": 0,
        "by_kind": {},
        "outcomes": {},
        "refusals": {},
        "responses": [],
        "last_post_at": 0.0,
    }


_health: Dict[str, Any] = _blank_health()


def reset_state_for_test() -> None:
    global _drain_running
    with _queue_lock:
        _queue.clear()
    with _lock:
        _send_times.clear()
        _health.clear()
        _health.update(_blank_health())
        _drain_running = False


def _count(bucket: str, n: int = 1) -> None:
    with _lock:
        _health[bucket] = int(_health.get(bucket, 0)) + n


def _count_in(bucket: str, key: str, n: int = 1) -> None:
    with _lock:
        sub = _health.setdefault(bucket, {})
        sub[key] = int(sub.get(key, 0)) + n


def _now() -> float:
    return time.time()


def _webhook_url() -> str:
    from config import SLACK_PACKET_WEBHOOK_URL

    return str(SLACK_PACKET_WEBHOOK_URL or "").strip()


def _redact(text: Any) -> str:
    """Strip the webhook URL from anything about to be recorded.

    Not decoration. `aiohttp` puts the URL it was dialling into the string form
    of a connection error, so an unredacted `str(exc)` in the response ring
    publishes a write capability on the channel to every reader of the ops page
    — including a read-only guest, who is exactly the tier that must not get
    one. Also strips the trailing path segment on its own, because Slack's
    token lives there and a partial URL is still a partial secret.
    """
    out = str(text)
    url = _webhook_url()
    if url:
        out = out.replace(url, "<webhook redacted>")
        tail = url.rstrip("/").rsplit("/", 1)[-1]
        # A short tail is not a token and blanket-replacing it would corrupt
        # ordinary words; only redact something long enough to be one.
        if len(tail) >= 8:
            out = out.replace(tail, "<redacted>")
    return out[:300]


def _record_response(status: str, http_status: Optional[int], detail: Any) -> None:
    with _lock:
        ring: List[Dict[str, Any]] = _health.setdefault("responses", [])
        ring.append(
            {
                "status": status,
                # None means Slack never answered, which is a different fault
                # from Slack answering with a code. Never rendered as 0.
                "http_status": http_status,
                "detail": _redact(detail),
                "at": round(_now(), 3),
            }
        )
        if len(ring) > _RESPONSE_RING:
            del ring[:-_RESPONSE_RING]


def enabled() -> bool:
    """The switch, ops-overridable, defaulting to the config value."""
    from config import SLACK_PACKET_ENABLED

    try:
        from src import runtime_tunables as _rt

        # One argument. `runtime_tunables.get` takes no default and RAISES on
        # an unregistered key, so passing one would be a TypeError swallowed by
        # the except below — an ops switch that silently served the boot value
        # forever while reading ON. That is `trail_governor_timeframe`
        # exactly, and the registry entry beside this is what makes the key
        # real rather than decorative.
        return bool(_rt.get("slack_packet_enabled"))
    except Exception as exc:  # noqa: BLE001 - a tunable read never gates a report
        fail_open.record("slack_packet.tunable", exc)
        return bool(SLACK_PACKET_ENABLED)


def configured() -> bool:
    return bool(_webhook_url())


def lane_state() -> str:
    """Four states, not two.

    ``off`` / ``not_configured`` / ``ready``. "Armed but no webhook URL set" is
    neither working nor broken, and collapsing it into either sends the owner to
    fix the wrong thing — the AI-governor page's own rule, one lane over.
    """
    if not enabled():
        return DISABLED
    if not configured():
        return NOT_CONFIGURED
    return "ready"


def _budget_ok(now: float) -> bool:
    """Spent per packet EXAMINED, at the top, before any work."""
    from config import SLACK_PACKET_MAX_PER_HOUR

    cap = int(SLACK_PACKET_MAX_PER_HOUR)
    cutoff = now - 3600.0
    with _lock:
        while _send_times and _send_times[0] < cutoff:
            _send_times.popleft()
        if len(_send_times) >= cap:
            return False
        _send_times.append(now)
    return True


# ── Packet building ─────────────────────────────────────────────────────────


def build_signal_packet(sig: Any, *, trigger_tf: str = "") -> Dict[str, Any]:
    """The report for a newly delivered signal.

    Geometry only, and no per-user anything: quantity, uid and the B17 exit
    profile are facts about a subscriber and have no business in a third-party
    workspace. §6.4 records putting signal geometry there as a deliberate
    decision rather than a default.
    """
    return {
        "kind": KIND_SIGNAL,
        "signal_id": str(getattr(sig, "signal_id", "") or ""),
        "symbol": str(getattr(sig, "symbol", "") or ""),
        "side": str(getattr(sig, "side", "") or ""),
        "setup_class": str(getattr(sig, "setup_class", "") or ""),
        "entry": getattr(sig, "entry", None),
        "stop_loss": getattr(sig, "stop_loss", None),
        "tp1": getattr(sig, "tp1", None),
        "confidence": getattr(sig, "confidence", None),
        "trigger_tf": str(trigger_tf or ""),
        "at": round(_now(), 3),
    }


def build_verdict_packet(verdict: Any, *, unknown_frac: Optional[float] = None) -> Dict[str, Any]:
    """The report for a governor verdict that is not MAINTAIN.

    Carries ``unknown_frac`` because a verdict issued with no order book and no
    CVD is legitimate — the governor is fail-open by design — and presenting it
    as a fully-informed one is not. Measured 2026-09-06: 200 of 200 rows fully
    blind. A packet that hid that would read as a confident call.
    """
    return {
        "kind": KIND_VERDICT,
        "signal_id": str(getattr(verdict, "signal_id", "") or ""),
        "action": str(getattr(verdict, "action", "") or ""),
        "choice": getattr(verdict, "choice", None),
        "confidence": getattr(verdict, "confidence", None),
        "rationale": str(getattr(verdict, "rationale", "") or "")[:140],
        "served_model": str(getattr(verdict, "served_model", "") or ""),
        "unknown_frac": unknown_frac,
        "at": round(_now(), 3),
    }


def render(packet: Dict[str, Any]) -> str:
    """One line a phone can read, with the caveats that change its meaning."""
    kind = packet.get("kind")
    if kind == KIND_SIGNAL:
        return (
            f"*{packet.get('symbol')}* {packet.get('side')} · "
            f"{packet.get('setup_class')}\n"
            f"entry `{packet.get('entry')}` · SL `{packet.get('stop_loss')}` · "
            f"TP1 `{packet.get('tp1')}` · conf `{packet.get('confidence')}` · "
            f"tf `{packet.get('trigger_tf')}`"
        )
    if kind == KIND_TEST:
        note = packet.get("note")
        return (
            ":test_tube: *Lumin Engine — connection test*\n"
            "This is NOT a signal and nothing was traded. It confirms the engine "
            "can reach this channel."
            + (f"\n_{note}_" if note else "")
        )
    if kind == KIND_VERDICT:
        blind = packet.get("unknown_frac")
        # An unmeasured blindness is not a measured zero, so it renders as a
        # dash rather than as a fully-informed verdict.
        blind_txt = "—" if blind is None else f"{float(blind):.2f}"
        return (
            f"*governor · {packet.get('action')}* on `{packet.get('signal_id')}`\n"
            f"choice `{packet.get('choice')}` · conf `{packet.get('confidence')}` · "
            f"unknown_frac `{blind_txt}` · model `{packet.get('served_model')}`\n"
            f"_{packet.get('rationale')}_\n"
            f"Recorded and applied to nothing — this lane is measurement only."
        )
    return json.dumps(packet, separators=(",", ":"))[:500]


# ── Queue and drain ─────────────────────────────────────────────────────────


def enqueue(packet: Dict[str, Any]) -> str:
    """Accept a packet for later posting. Never blocks, never raises.

    Called from the monitor loop, so it does exactly one thing: append under a
    lock. Every network cost is on the drain.
    """
    state = lane_state()
    if state != "ready":
        _count_in("refusals", state)
        return state
    with _queue_lock:
        if len(_queue) >= _QUEUE_MAX:
            # `deque(maxlen=)` would drop silently; counted instead, because a
            # report lane that quietly loses its backlog looks identical to a
            # quiet market.
            _count("dropped_queue_full")
            _count_in("refusals", QUEUE_FULL)
        _queue.append(packet)
    _count("queued")
    _count_in("by_kind", str(packet.get("kind") or "unknown"))
    return "queued"


async def _post_one(session: aiohttp.ClientSession, packet: Dict[str, Any]) -> str:
    from config import SLACK_PACKET_TIMEOUT_SEC

    url = _webhook_url()
    body = {"text": render(packet)}
    try:
        async with session.post(
            url,
            json=body,
            timeout=aiohttp.ClientTimeout(total=float(SLACK_PACKET_TIMEOUT_SEC)),
        ) as resp:
            text = await resp.text()
            if resp.status // 100 == 2:
                _count("posted")
                _count_in("outcomes", OK)
                with _lock:
                    _health["last_post_at"] = round(_now(), 3)
                return OK
            # Slack's own words. It answers a bad payload with a plain-text
            # reason ("invalid_payload", "channel_not_found") and those have
            # different fixes; the status code alone cannot say which.
            _count_in("outcomes", HTTP_ERROR)
            _record_response(HTTP_ERROR, resp.status, text)
            return HTTP_ERROR
    except asyncio.TimeoutError as exc:
        _count_in("outcomes", TIMEOUT)
        _record_response(TIMEOUT, None, exc)
        return TIMEOUT
    except Exception as exc:  # noqa: BLE001
        # Fail-open in behaviour, counted in telemetry. A report that cannot be
        # delivered must never reach the money path, and it never does: nothing
        # awaits this result.
        _count_in("outcomes", TRANSPORT_ERROR)
        _record_response(TRANSPORT_ERROR, None, exc)
        # Redacted before it reaches `fail_open`, which WARNs the exception
        # into the container log. aiohttp puts the dialled URL into the string
        # form of a connection error, so handing the raw exception over writes
        # the webhook token to disk — the ops payload was only one of two
        # surfaces, and this is the one a test asserting on `build_diag` cannot
        # see. Found by reading the captured stderr of the test that pins the
        # other half.
        fail_open.record(
            "slack_packet.post", RuntimeError(f"{type(exc).__name__}: {_redact(exc)}")
        )
        return TRANSPORT_ERROR


async def drain(*, now: Optional[float] = None, session: Any = None) -> int:
    """Post at most ``SLACK_PACKET_MAX_PER_DRAIN`` packets. Never raises.

    Depth is taken ONCE, like `ai_governor.drain_verdicts`: an unbounded
    ``while _queue`` would let a packet requeued by a budget refusal be popped
    again within the same instant, which is a live-lock inside a loop that owns
    the FSM clock.
    """
    from config import SLACK_PACKET_MAX_PER_DRAIN

    now = _now() if now is None else now
    if lane_state() != "ready":
        return 0

    with _queue_lock:
        pending = min(len(_queue), int(SLACK_PACKET_MAX_PER_DRAIN))
    if pending <= 0:
        return 0

    sent = 0
    owns_session = session is None
    sess = session or aiohttp.ClientSession()
    try:
        for _ in range(pending):
            # The budget is spent HERE — before the pop, before the render,
            # before the HTTP call. It therefore bounds every path below it,
            # including ones added later.
            if not _budget_ok(now):
                _count_in("refusals", BUDGET_EXHAUSTED)
                break
            with _queue_lock:
                if not _queue:
                    break
                packet = _queue.popleft()
            await _post_one(sess, packet)
            sent += 1
    finally:
        if owns_session:
            try:
                await sess.close()
            except Exception as exc:  # noqa: BLE001
                fail_open.record("slack_packet.session_close", exc)
    return sent


def spawn_drain(*, task_factory: Any = None) -> bool:
    """Kick a drain off the monitor loop. Returns True when one was started.

    Never awaited by the caller — a slow report must not become a slow monitor
    loop — and never more than one at a time, because two concurrent drains
    would each take their own depth and race the per-hour budget.
    """
    global _drain_running
    if lane_state() != "ready":
        return False
    with _queue_lock:
        if not _queue:
            return False
    with _lock:
        if _drain_running:
            return False
        _drain_running = True

    async def _run() -> None:
        global _drain_running
        try:
            await drain()
        except Exception as exc:  # noqa: BLE001
            fail_open.record("slack_packet.drain", exc)
        finally:
            with _lock:
                _drain_running = False

    spawn = task_factory or asyncio.create_task
    try:
        spawn(_run())
    except Exception as exc:  # noqa: BLE001
        # The latch must be released on the path where the task was never
        # created — `asyncio.create_task` raises without a running loop, and
        # leaving `_drain_running` True there would silently disable the lane
        # for the life of the process while every counter still read healthy.
        # A guard whose failure path forgets to undo its own flag is the
        # idempotence-key defect: what advances the clock, and does a failure
        # advance it?
        with _lock:
            _drain_running = False
        fail_open.record("slack_packet.spawn", exc)
        return False
    return True


# ── The pre-arm test post ───────────────────────────────────────────────────


#: A packet that is unmistakably not a signal. It shares the outbound path,
#: the budget and the counters with the real lane, and shares NOTHING with the
#: signal format: a test message that reads like a tradeable signal, in the
#: channel signals arrive on, is a message somebody can act on.
KIND_TEST = "test"


def build_test_packet(note: str = "") -> Dict[str, Any]:
    return {
        "kind": KIND_TEST,
        "note": str(note or "")[:140],
        "at": round(_now(), 3),
    }


def dispatch_test_post(*, note: str = "", task_factory: Any = None) -> Dict[str, Any]:
    """Post ONE test message now, on the owner's explicit action.

    **This is the one path that does not require the lane switch, and that is a
    decision rather than an oversight.** The arming rule for a new outbound loop
    is *"armed by the owner after one watched cycle"* — and a cycle you cannot
    trigger is a cycle you cannot watch. Waiting for a real delivered signal to
    find out whether the webhook works means discovering a bad URL at the moment
    the lane is supposed to start being useful.

    What the switch still governs is untouched, and that is the property that
    matters: `enqueue` refuses while disabled, `drain` refuses while disabled,
    and `spawn_drain` refuses while disabled — so the ENGINE still posts nothing
    on its own. This is a single message, per invocation, through an audited ops
    action, and it spends the same hourly budget so it cannot be hammered.

    It does require a webhook URL. "No URL" is a named refusal rather than a
    silent no-op, because the two have different fixes and the whole point of
    this entry is to tell them apart.

    ``note`` is accepted for an API caller and is deliberately NOT declared in
    the catalog entry's ``needs``: the ops console renders a text input for
    ``symbol`` and for nothing else, on purpose, and a declared need no surface
    can satisfy is the same "declared and unread" shape this repo keeps paying
    for. Empty is the ordinary case.

    Returns what it DID, not what happened — the post is dispatched onto the
    loop and its outcome lands in the same `outcomes` / `responses` counters the
    real lane writes, so reading `read.slack_packet` afterwards exercises the
    instrument as well as the transport.
    """
    if not configured():
        _count_in("refusals", NOT_CONFIGURED)
        return {
            "dispatched": False,
            "reason": NOT_CONFIGURED,
            "detail": "no SLACK_PACKET_WEBHOOK_URL on this container",
        }

    now = _now()
    if not _budget_ok(now):
        _count_in("refusals", BUDGET_EXHAUSTED)
        return {"dispatched": False, "reason": BUDGET_EXHAUSTED}

    packet = build_test_packet(note)

    async def _run() -> None:
        session = aiohttp.ClientSession()
        try:
            await _post_one(session, packet)
        except Exception as exc:  # noqa: BLE001
            fail_open.record("slack_packet.test_post", exc)
        finally:
            try:
                await session.close()
            except Exception as exc:  # noqa: BLE001
                fail_open.record("slack_packet.test_session_close", exc)

    spawn = task_factory or asyncio.create_task
    try:
        spawn(_run())
    except Exception as exc:  # noqa: BLE001
        # No running loop. Named rather than raised, and the budget is already
        # spent — which is the conservative direction for a bypass path.
        fail_open.record("slack_packet.test_dispatch", exc)
        return {"dispatched": False, "reason": "no_event_loop", "detail": _redact(exc)}

    _count_in("by_kind", KIND_TEST)
    return {
        "dispatched": True,
        "lane_at_dispatch": lane_state(),
        "rendered": render(packet),
        "note": (
            "One test message was sent. Read `read.slack_packet` again for the "
            "outcome — it lands in `outcomes` and `responses` beside the real "
            "lane's, so a failure names what Slack said."
        ),
    }


def health() -> Dict[str, Any]:
    with _lock:
        return json.loads(json.dumps(_health))


def build_diag() -> Dict[str, Any]:
    """What the ops page reads. Carries no secret — see `_redact`.

    The channel id is display only: a webhook posts where it was created and
    nothing here can redirect it. It is published so the page can say WHERE the
    packets went rather than only that they went.
    """
    from config import (
        SLACK_PACKET_CHANNEL_ID,
        SLACK_PACKET_MAX_PER_DRAIN,
        SLACK_PACKET_MAX_PER_HOUR,
    )

    with _queue_lock:
        depth = len(_queue)
    # Both switches, because the lane is inert if EITHER is off and for
    # different reasons — a page showing one cannot say which half is missing.
    # Packets are enqueued from the governor's own sweep, so turning
    # `ai_gov_measure_enabled` off stops the reports while this lane still
    # reads "ready": armed, configured, and fed by nothing. That is the
    # promotions page's `lane_off` state arriving one repo earlier.
    try:
        from src.execution import ai_governor as _aig

        upstream = bool(_aig.measure_enabled())
    except Exception as exc:  # noqa: BLE001
        fail_open.record("slack_packet.upstream", exc)
        upstream = None

    return {
        "lane": lane_state(),
        "enabled": enabled(),
        # None is "we could not ask", never "the governor is off" — an
        # unreadable switch and a switch reading no are different facts.
        "source_lane_enabled": upstream,
        "source": "ai_governor.sweep",
        # Whether a URL EXISTS, never the URL. The one question the page needs
        # and the one answer that is safe to give it.
        "webhook_configured": configured(),
        "channel_id": str(SLACK_PACKET_CHANNEL_ID or ""),
        "bounds": {
            "max_per_hour": int(SLACK_PACKET_MAX_PER_HOUR),
            "max_per_drain": int(SLACK_PACKET_MAX_PER_DRAIN),
        },
        "queue_depth": depth,
        "health": health(),
    }
