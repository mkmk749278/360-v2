"""The post-emission AI Trade Governor — arms, budgets, verdicts, apply.

Design of record: `docs/PLAN_AI_TRADE_GOVERNOR.md`. Read §2 before changing
anything here; it is the section that decides whether this is safe.

Two fan-outs, and only one of them is the LLM
---------------------------------------------
Owner, 2026-09-02: *"AI works per signals, FSM calls users."* An arm is keyed by
``signal_id``, never by position, so the model cost is **flat in members** —
~120 calls/day at one member and at a thousand. Order-book walls, CVD and BTC
are facts about the symbol; quantity and the B17 exit profile are the only
per-user facts and they are filters applied after the verdict.

The **apply** path is the one that scales, and it is the real risk.
``close_fsm_positions_for_signal`` loops over every active uid with a Firestore
read each, then cancels the bracket and market-closes per uid. One
``PANIC_CLOSE`` at 1,000 members is ~1,000 reads and ~5,000 signed Binance calls
in a burst, from an IP that has been rate-limited before — the 2026-09-01 shape
exactly, which took auto-trade down for every paid user for four hours. Hence:

* ``MAINTAIN`` costs **nothing** — no read, no call, no position walk.
* The apply path carries its **own** budget, separate from the model budget.
* Non-urgent verdicts are **paced** across users.
* ``PANIC_CLOSE`` cannot be paced (a queued emergency close is not one), so it
  is bounded by a hard position ceiling instead — and when that ceiling is
  **unset the arm refuses outright**. An owner-set blast-radius cap that
  defaults to "unlimited" is not a cap, and this is the one arm where the
  absence of a number must not read as permission.

The clock
---------
Verdicts are decided on **closed bars** of the signal's own trigger timeframe.
`trail_governor` established the property a placeable exit needs — a level
projected from closed bars, knowable before the bar trades. A wall-clock verdict
describes a state that has already moved and cannot be replayed against
anything, which is also why it could never be measured.

The async contract
------------------
**The LLM is never awaited inside the sweep.** ``MONITOR_POLL_INTERVAL`` is 5s
and that loop already carries the signal fan-out, four measurement lanes and the
trail governor; a 3–10s round trip inside it would stall the loop that owns the
FSM clock — and the instrument would be blind to its own stall, because an
instrument that travels on a starved channel cannot measure the starvation.
So: ``create_task``, a bounded queue, and the **next** tick applies after
re-validating every precondition against state read fresh in that tick. A
verdict older than one tick is refused and counted, never applied.

Which container
---------------
Engine. The governor needs the in-process position index and the candle store;
assembling this in the api container is the ``INDEX COLD`` defect.
"""
from __future__ import annotations

import asyncio
import json
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional, Tuple

from src import ai_governor_score as _score
from src import fail_open, llm_client
from src.ai_governor_ledger import get_ledger
from src.execution import ai_governor_menu as _menu
from src.execution import ai_governor_snapshot as _snap
from src.utils import get_logger

log = get_logger("ai_governor")

# ── The verdict vocabulary ──────────────────────────────────────────────────

MAINTAIN = "MAINTAIN"
ADJUST_TP = "ADJUST_TP"
ADJUST_SL = "ADJUST_SL"
PANIC_CLOSE = "PANIC_CLOSE"
ACTIONS = (MAINTAIN, ADJUST_TP, ADJUST_SL, PANIC_CLOSE)

#: Arms that may APPLY, as config tokens. Kept apart from ACTIONS because
#: MAINTAIN is not an arm anybody arms.
ARM_TP = "tp"
ARM_SL = "sl"
ARM_PANIC = "panic"
ARMS = (ARM_TP, ARM_SL, ARM_PANIC)
_ARM_OF = {ADJUST_TP: ARM_TP, ADJUST_SL: ARM_SL, PANIC_CLOSE: ARM_PANIC}

#: Closed vocabulary for `premise_broken`. The model may only name reasons we
#: have thought about; anything else is dropped and counted, so a page cannot
#: grow categories nobody defined.
PREMISE_REASONS = (
    "macro_regime_flip",
    "flow_opposed",
    "wall_ahead_of_tp",
    "structure_lost",
    "target_unreachable",
)

# ── Named refusals. Every one is a state a panel renders under its own name ──

REFUSE_DISABLED = "disabled"
REFUSE_NOT_CONFIGURED = "not_configured"
REFUSE_KILL_SWITCH = "kill_switch"
REFUSE_INDEX_COLD = "index_cold"
REFUSE_BUDGET_CALLS = "budget_exhausted_calls"
REFUSE_BUDGET_SPEND = "budget_exhausted_spend"
#: NOT a refusal. `cooldown` means the lane found an arm it was willing to
#: evaluate and deliberately did not, which is positive evidence it is
#: working. Bucketed with the refusals it reads as the governor being
#: blocked when it was us throttling — #816 arriving from the display side.
THROTTLE_COOLDOWN = "cooldown"
REFUSE_NO_BAR = "no_new_bar"
REFUSE_NO_TRIGGER = "no_trigger"
REFUSE_TF_UNKNOWN = "tf_unknown"
REFUSE_NO_SERIES = "no_series"
REFUSE_STALE_VERDICT = "stale_verdict"
REFUSE_UNKNOWN_CHOICE = "unknown_choice"
REFUSE_UNKNOWN_SIGNAL = "unknown_signal"
REFUSE_UNKNOWN_ACTION = "unknown_action"
REFUSE_NOT_MONOTONE = "not_monotone"
REFUSE_ARM_OFF = "arm_off"
REFUSE_APPLY_OFF = "apply_off"
REFUSE_PANIC_CEILING_UNSET = "panic_ceiling_unset"
REFUSE_PANIC_CEILING_HIT = "panic_ceiling_hit"
REFUSE_APPLY_PACED = "apply_paced"
REFUSE_TRAIL_GOVERNED = "trail_governed"
REFUSE_QUEUE_FULL = "verdict_queue_full"

#: Bounded verdict queue. Small on purpose: it holds at most one verdict per
#: open signal, and a backlog means the apply path is not keeping up — which is
#: a fault to surface, not a depth to absorb.
_QUEUE_MAX = 32


def _now() -> float:
    return time.time()


# ── Counters ────────────────────────────────────────────────────────────────

_health_lock = threading.RLock()


def _blank_health() -> Dict[str, Any]:
    return {
        "cycles": 0,
        "arms": 0,
        "triggers": 0,
        "calls": 0,
        "verdicts": 0,
        "applied": 0,
        "spend_usd": 0.0,
        "spend_unpriced_calls": 0,
        "by_action": {},
        "refusals": {},
        # Kept apart from `refusals` on purpose: a throttle is the lane
        # working, and pooling the two makes a healthy governor read as a
        # blocked one.
        "throttles": {},
        "provider_status": {},
        # The counts above say HOW MANY calls failed and cannot say what the
        # provider objected to. `bad_json` covers a truncated answer, a
        # schema-shaped answer with the wrong types, and an error envelope;
        # each has a different fix, and the vendor already told us which — in a
        # `detail` string that never left this process. This is
        # `trail_governor.place_failed` exactly: a counter is not a cause on a
        # path that talks to a vendor. Bounded ring, newest last, published
        # BESIDE the unbounded count so the newest few can never read as the
        # whole population.
        "provider_failures": [],
        "latency_ms_last": 0,
        "served_models": {},
    }


_health: Dict[str, Any] = _blank_health()


def _count(bucket: str, n: int = 1) -> None:
    with _health_lock:
        _health[bucket] = int(_health.get(bucket, 0)) + n


def _count_in(bucket: str, key: str, n: int = 1) -> None:
    with _health_lock:
        sub = _health.setdefault(bucket, {})
        sub[key] = int(sub.get(key, 0)) + n


def _refuse(reason: str) -> None:
    _count_in("refusals", reason)


#: How many recent provider failures to keep. Small on purpose: this is a
#: diagnosis aid, not a ledger, and the ledger of verdicts is elsewhere.
_PROVIDER_FAILURE_RING = 20


def _record_provider_failure(result: Any, now: float, *, max_output_tokens: int) -> None:
    """Keep the provider's own words for the last few failures.

    Called for every non-OK result. `detail` is scrubbed of the API key at the
    point it is built (`llm_client._scrub`), so nothing here can leak a secret
    onto a panel — but the scrub is asserted in this module's tests too,
    because the guarantee matters at the surface that renders it, not only at
    the surface that writes it.
    """
    with _health_lock:
        ring = _health.setdefault("provider_failures", [])
        usage = dict(getattr(result, "usage", None) or {})
        ring.append({
            "at": round(float(now), 3),
            "status": str(getattr(result, "status", "") or ""),
            "detail": str(getattr(result, "detail", "") or "")[:400],
            # Empty means the provider did not say why it stopped — never that
            # it stopped cleanly. MAX_TOKENS here beside a `bad_json` above is
            # the whole diagnosis.
            "finish_reason": str(getattr(result, "finish_reason", "") or ""),
            "served_model": str(getattr(result, "served_model", "") or ""),
            "output_tokens": int(usage.get("output_tokens") or 0),
            "thinking_tokens": int(usage.get("thinking_tokens") or 0),
            # The ceiling we ASKED for, beside what was spent: `output_tokens`
            # at the ceiling is a truncation, and the two numbers are only a
            # diagnosis together.
            "max_output_tokens": int(max_output_tokens),
            "latency_ms": int(getattr(result, "latency_ms", 0) or 0),
        })
        if len(ring) > _PROVIDER_FAILURE_RING:
            del ring[:-_PROVIDER_FAILURE_RING]


def health() -> Dict[str, Any]:
    with _health_lock:
        return json.loads(json.dumps(_health))


def reset_health_for_test() -> None:
    global _health
    with _health_lock:
        _health = _blank_health()


# ── Flags ───────────────────────────────────────────────────────────────────

def _tunable(key: str, default: Any) -> Any:
    try:
        from src import runtime_tunables as _rt

        return _rt.get(key)
    except Exception as exc:  # noqa: BLE001 — a tunable read never blocks the lane
        fail_open.record(f"ai_governor.tunable.{key}", exc)
        return default


def measure_enabled() -> bool:
    """Stamping and calling. Default **ON**.

    A measurement shipped OFF produces an empty ops panel and a decision that
    keeps getting deferred — which is exactly what happened to the SAR exit arm,
    shipped off, with the owner having to enable it and then ask where to look.
    """
    from config import AI_GOV_MEASURE_ENABLED

    return bool(_tunable("ai_gov_measure_enabled", AI_GOV_MEASURE_ENABLED))


def apply_enabled() -> bool:
    """Whether a verdict may touch a real order. Default **OFF** — owner sign-off."""
    from config import AI_GOV_APPLY_ENABLED

    return bool(_tunable("ai_gov_apply_enabled", AI_GOV_APPLY_ENABLED))


def armed_arms() -> Tuple[str, ...]:
    from config import AI_GOV_ARMS_ENABLED

    raw = str(_tunable("ai_gov_arms_enabled", AI_GOV_ARMS_ENABLED) or "")
    return tuple(a for a in (p.strip().lower() for p in raw.split(",")) if a in ARMS)


# ── Arms — one per SIGNAL, never per position ───────────────────────────────

@dataclass
class Arm:
    signal_id: str
    symbol: str
    trigger_tf: str
    opened_at: float
    calls_made: int = 0
    last_call_at: float = 0.0
    last_bar_evaluated_ms: int = 0
    last_r: Optional[float] = None
    standing: Optional["Verdict"] = None
    refusals: Dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class Verdict:
    signal_id: str
    action: str
    choice: Optional[str]
    confidence: float
    rationale: str
    premise_broken: Tuple[str, ...]
    served_model: str
    requested_model: str
    prompt_schema: int
    snapshot_digest: str
    as_of_bar_ms: int
    issued_at: float
    latency_ms: int
    usage: Dict[str, int]
    cost_usd: Optional[float]
    price_at_verdict: Optional[float] = None

    def as_row(self) -> Dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "action": self.action,
            "choice": self.choice,
            "confidence": round(float(self.confidence), 4),
            "rationale": self.rationale,
            "premise_broken": list(self.premise_broken),
            # The SERVED version, not the alias we asked for. Gemini rotates
            # aliases; stamping the request would let a rotation redefine every
            # row with no diff in our repo.
            "served_model": self.served_model,
            "requested_model": self.requested_model,
            "prompt_schema": self.prompt_schema,
            "snapshot_digest": self.snapshot_digest,
            "as_of_bar_ms": self.as_of_bar_ms,
            "issued_at": self.issued_at,
            "latency_ms": self.latency_ms,
            "usage": dict(self.usage),
            "cost_usd": self.cost_usd,
            "rate_table_version": llm_client.RATE_TABLE_VERSION,
        }


_arms: Dict[str, Arm] = {}
_arms_lock = threading.RLock()
_queue: Deque[Tuple[Verdict, _snap.Snapshot, _menu.Menu]] = deque(maxlen=_QUEUE_MAX)
_queue_lock = threading.RLock()

#: Rolling window of call timestamps for the per-hour bound, and the day's
#: spend. Both are process-local by design: the governor runs in one container,
#: and a Firestore-backed counter on a per-bar path is the cost defect this
#: repo has paid for more than once.
_call_times: Deque[float] = deque(maxlen=4096)
_spend_day: str = ""
_spend_usd: float = 0.0
_apply_times: Deque[float] = deque(maxlen=8192)


def reset_state_for_test() -> None:
    global _spend_day, _spend_usd
    with _arms_lock:
        _arms.clear()
    with _queue_lock:
        _queue.clear()
    _call_times.clear()
    _apply_times.clear()
    _spend_day = ""
    _spend_usd = 0.0


def arms_snapshot() -> List[Dict[str, Any]]:
    with _arms_lock:
        return [
            {
                "signal_id": a.signal_id, "symbol": a.symbol,
                "trigger_tf": a.trigger_tf, "calls_made": a.calls_made,
                "last_bar_evaluated_ms": a.last_bar_evaluated_ms,
                "standing": a.standing.action if a.standing else None,
                "refusals": dict(a.refusals),
            }
            for a in _arms.values()
        ]


def observe_signal(sig: Any, *, trigger_tf: str, now: Optional[float] = None) -> bool:
    """Open an arm for a signal, once. Returns True when a new arm was created.

    Keyed by ``signal_id``: a second call for the same signal — which happens on
    every monitor tick — refreshes nothing and costs nothing. The arm's lifetime
    is the SIGNAL's, so a user joining mid-trade inherits the standing verdict
    and a user whose position closes early simply drops out of the apply set.
    """
    signal_id = str(getattr(sig, "signal_id", "") or "")
    if not signal_id:
        return False
    with _arms_lock:
        if signal_id in _arms:
            return False
        _arms[signal_id] = Arm(
            signal_id=signal_id,
            symbol=str(getattr(sig, "symbol", "") or ""),
            trigger_tf=str(trigger_tf or ""),
            opened_at=float(now if now is not None else _now()),
        )
    return True


def retire(signal_id: str) -> None:
    """Drop an arm whose signal is no longer active."""
    with _arms_lock:
        _arms.pop(str(signal_id), None)


# ── Budgets — spent at the TOP, per signal EXAMINED ─────────────────────────

def _spend_call_budget(arm: Arm, now: float) -> Optional[str]:
    """Charge the model budget before any work. ``None`` means proceed.

    Session 137's lesson, and it is not negotiable: the orphan sweep's budget
    was named for what it *does* (cancel) and only decremented on that branch;
    production takes the other branch, so it spent nothing, ran unbounded, got
    the box rate-limited off Binance and took auto-trade down for four hours.
    A budget that only decrements when a call is actually issued is unbounded
    on the path production takes — which here is "nothing triggered".
    """
    from config import (
        AI_GOV_MAX_CALLS_PER_HOUR,
        AI_GOV_MAX_CALLS_PER_SIGNAL,
        AI_GOV_MAX_USD_PER_DAY,
        AI_GOV_MIN_SECONDS_BETWEEN,
    )

    if arm.calls_made >= int(AI_GOV_MAX_CALLS_PER_SIGNAL):
        return REFUSE_BUDGET_CALLS
    if now - arm.last_call_at < float(AI_GOV_MIN_SECONDS_BETWEEN):
        return THROTTLE_COOLDOWN

    cutoff = now - 3600.0
    while _call_times and _call_times[0] < cutoff:
        _call_times.popleft()
    if len(_call_times) >= int(AI_GOV_MAX_CALLS_PER_HOUR):
        return REFUSE_BUDGET_CALLS

    cap = float(AI_GOV_MAX_USD_PER_DAY)
    if cap > 0 and _spend_today(now) >= cap:
        return REFUSE_BUDGET_SPEND
    return None


def _spend_today(now: float) -> float:
    global _spend_day, _spend_usd
    day = time.strftime("%Y-%m-%d", time.gmtime(now))
    if day != _spend_day:
        _spend_day = day
        _spend_usd = 0.0
    return _spend_usd


def _record_spend(cost: Optional[float], now: float) -> None:
    global _spend_usd
    _spend_today(now)
    if cost is None:
        # An unpriced model is a table that needs updating, and it must not
        # read as free — a cost we cannot bound is counted under its own name
        # so a cap cannot be silently escaped by configuring a model nobody
        # priced.
        _count("spend_unpriced_calls")
        return
    _spend_usd += float(cost)
    with _health_lock:
        _health["spend_usd"] = round(_spend_usd, 6)


def _spend_apply_budget(now: float, *, count: int) -> bool:
    """Charge the EXCHANGE-call budget. Separate from the model budget on purpose.

    §2.2: the model bill is flat in members and the execution bill is linear and
    bursty. These are not the same bound and tuning them together is how one
    hides the other.
    """
    from config import AI_GOV_APPLY_MAX_POS_PER_MIN

    cap = int(AI_GOV_APPLY_MAX_POS_PER_MIN)
    if cap <= 0:
        return True
    cutoff = now - 60.0
    while _apply_times and _apply_times[0] < cutoff:
        _apply_times.popleft()
    if len(_apply_times) + count > cap:
        return False
    for _ in range(count):
        _apply_times.append(now)
    return True


# ── The trigger ladder ──────────────────────────────────────────────────────

def should_trigger(arm: Arm, snapshot: _snap.Snapshot, macro_moved: bool) -> Optional[str]:
    """Has the state materially moved? ``None`` means do not spend a call.

    Deterministic, in-process, no network — computed every tick from data the
    engine already holds, so the gate itself costs nothing at any member count.
    """
    from config import AI_GOV_TRIGGER_R_BAND, AI_GOV_TRIGGER_TP_PROXIMITY_PCT

    if macro_moved:
        return "macro"

    band = float(AI_GOV_TRIGGER_R_BAND)
    if band > 0 and snapshot.price.readable:
        r = snapshot.r_multiple_now
        prev = arm.last_r
        if prev is None or abs(r - prev) >= band:
            return "r_band"

    prox = float(AI_GOV_TRIGGER_TP_PROXIMITY_PCT)
    if prox > 0 and 0 < snapshot.dist_to_tp1_pct <= prox:
        return "near_tp"

    if snapshot.cvd_slope_aligned.readable and float(
        snapshot.cvd_slope_aligned.value or 0.0
    ) < 0:
        return "flow_opposed"

    return None


# ── The model contract ──────────────────────────────────────────────────────

PROMPT_SCHEMA = 1

_SYSTEM_PROMPT = """\
You are a risk critic for an already-open crypto futures scalp. The trade is
live; you cannot open, reverse, or size anything. You choose among four
outcomes and nothing else.

MAINTAIN     - reality still supports the original premise. Prefer this.
ADJUST_TP    - take profit sooner. Choose a tp_* key NEARER than tp_0.
ADJUST_SL    - reduce risk. Choose an sl_* key TIGHTER than sl_0.
PANIC_CLOSE  - the premise is broken and waiting for the stop is worse than
               paying the exit now. Reserve this for a genuine regime break.

Rules you must follow:
- Return ONLY a key that appears in this position's own candidate list.
- choice must be null for MAINTAIN and PANIC_CLOSE.
- Every distance is signed TOWARD the trade: positive is in its favour on both
  a LONG and a SHORT. Do not re-derive direction.
- A field marked readable:false means we could not observe it. It is not zero
  and not neutral - reason about the trade without it and say so if it matters.
- rationale is one sentence, under 140 characters, describing what changed.
- premise_broken names only reasons from the allowed list.

Closing a position costs a round-trip fee of roughly 0.7% of margin, charged
whether or not the exit was right. A MAINTAIN that turns out wrong costs the
stop, which was already sized for. Weigh accordingly.
"""

RESPONSE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "signal_id": {"type": "string"},
                    "verdict": {"type": "string", "enum": list(ACTIONS)},
                    "choice": {"type": "string"},
                    "confidence": {"type": "number"},
                    "rationale": {"type": "string"},
                    "premise_broken": {
                        "type": "array",
                        "items": {"type": "string", "enum": list(PREMISE_REASONS)},
                    },
                },
                "required": ["signal_id", "verdict", "rationale"],
            },
        },
    },
    "required": ["verdicts"],
}


def _client() -> llm_client.LLMClient:
    from config import AI_GOV_MODEL, AI_GOV_PROVIDER, AI_GOV_REQUEST_TIMEOUT_SEC

    return llm_client.LLMClient(
        provider=str(_tunable("ai_gov_provider", AI_GOV_PROVIDER)),
        model=str(_tunable("ai_gov_model", AI_GOV_MODEL)),
        timeout_sec=float(AI_GOV_REQUEST_TIMEOUT_SEC),
    )


def parse_verdicts(
    data: Dict[str, Any],
    *,
    result: llm_client.LLMResult,
    batch: Dict[str, Tuple[_snap.Snapshot, _menu.Menu]],
    now: float,
) -> List[Tuple[Verdict, _snap.Snapshot, _menu.Menu]]:
    """Turn the model's reply into verdicts, refusing anything outside the menu.

    Structured output makes a malformed shape unlikely; it does not make it
    impossible, and the API's schema cannot know which keys belong to WHICH
    position. A key from another position's menu is a cross-wire and is refused
    here rather than resolved by luck.
    """
    out: List[Tuple[Verdict, _snap.Snapshot, _menu.Menu]] = []
    for item in data.get("verdicts") or []:
        if not isinstance(item, dict):
            continue
        signal_id = str(item.get("signal_id") or "")
        pair = batch.get(signal_id)
        if pair is None:
            # A verdict for a signal that was not in this batch. Named apart
            # from an unknown menu key: one is the model inventing a level, the
            # other is it answering about a position we did not ask about, and
            # the second is the more alarming of the two.
            _refuse(REFUSE_UNKNOWN_SIGNAL)
            continue
        snapshot, menu = pair

        action = str(item.get("verdict") or "").upper()
        if action not in ACTIONS:
            _refuse(REFUSE_UNKNOWN_ACTION)
            continue

        raw_choice = item.get("choice")
        choice = str(raw_choice) if raw_choice else None
        if action in (MAINTAIN, PANIC_CLOSE):
            choice = None
        elif choice is None or menu.lookup(choice) is None:
            # The named refusal that makes a hallucinated key harmless.
            _refuse(REFUSE_UNKNOWN_CHOICE)
            continue
        elif not _choice_is_monotone(action, choice, menu):
            _refuse(REFUSE_NOT_MONOTONE)
            continue

        premise = tuple(
            r for r in (item.get("premise_broken") or [])
            if isinstance(r, str) and r in PREMISE_REASONS
        )
        cost = llm_client.cost_usd(result.served_model or result.requested_model, result.usage)
        verdict = Verdict(
            signal_id=signal_id,
            action=action,
            choice=choice,
            confidence=_clamp01(item.get("confidence")),
            rationale=str(item.get("rationale") or "")[:140],
            premise_broken=premise,
            served_model=result.served_model,
            requested_model=result.requested_model,
            prompt_schema=PROMPT_SCHEMA,
            snapshot_digest=snapshot.digest(),
            as_of_bar_ms=snapshot.as_of_bar_ms,
            issued_at=now,
            latency_ms=result.latency_ms,
            usage=dict(result.usage),
            cost_usd=cost,
            price_at_verdict=snapshot.price.value,
        )
        out.append((verdict, snapshot, menu))
    return out


def _clamp01(value: Any) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def _choice_is_monotone(action: str, choice: str, menu: _menu.Menu) -> bool:
    """TP may move NEARER only; SL may move TIGHTER only.

    Enforced here **and** again on apply. The menu is already built to contain
    only monotone candidates, so this cannot normally fire — which is exactly
    why it is checked: an invariant that only holds because of how a collaborator
    happens to behave is one refactor away from not holding, and the model's
    output is untrusted regardless.
    """
    cand = menu.lookup(choice)
    if cand is None:
        return False
    if action == ADJUST_TP:
        current = menu.lookup(f"{_menu.TP_PREFIX}0")
        return current is not None and 0 < cand.dist_pct < current.dist_pct
    if action == ADJUST_SL:
        current = menu.lookup(f"{_menu.SL_PREFIX}0")
        return current is not None and cand.dist_pct > current.dist_pct
    return True


# ── The sweep ───────────────────────────────────────────────────────────────

async def sweep(
    signals: Any,
    store: Any,
    *,
    price_fn: Any,
    now_ts: Optional[float] = None,
    macro: Optional[Dict[str, Any]] = None,
    macro_moved: bool = False,
    task_factory: Any = None,
) -> Dict[str, Any]:
    """Advance every armed SIGNAL by at most one bar. Never blocks on the model.

    Returns the cycle's outcome mix so the caller can log it and the probe can
    read it. Every early return is a *named, counted* state — there is no
    silent path, and "nothing happened" is several different facts with
    different fixes.
    """
    now = _now() if now_ts is None else now_ts
    _count("cycles")

    # Applied FIRST, so a verdict lands on the tick after it arrives and is
    # re-validated against state read fresh in that same tick.
    drained = await drain_verdicts(now=now)

    if not measure_enabled():
        _refuse(REFUSE_DISABLED)
        return {"enabled": False, "drained": drained}

    try:
        from src.execution import kill_switch as _ks

        if _ks.is_initialised() and _ks.get_client().is_global_engaged():
            # The kill switch means "stop acting on this account", and asking a
            # model whether to act is the first half of acting. The existing
            # protection stays exactly where it is.
            _refuse(REFUSE_KILL_SWITCH)
            return {"enabled": True, "killed": True, "drained": drained}
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor.sweep:kill_switch", exc)

    active = _active_signals(signals)
    _retire_missing(set(active))

    batch: Dict[str, Tuple[_snap.Snapshot, _menu.Menu]] = {}
    outcomes: Dict[str, int] = {}

    for signal_id, sig in active.items():
        trigger_tf = _trigger_tf_for(sig)
        if not trigger_tf:
            _refuse(REFUSE_TF_UNKNOWN)
            outcomes[REFUSE_TF_UNKNOWN] = outcomes.get(REFUSE_TF_UNKNOWN, 0) + 1
            continue
        observe_signal(sig, trigger_tf=trigger_tf, now=now)
        with _arms_lock:
            arm = _arms.get(signal_id)
        if arm is None:
            continue

        # The budget guard runs BEFORE any per-signal work — menu building,
        # snapshot assembly, all of it. Session 137's rule is that the
        # do-nothing branch must be the cheap one; here that means an arm with
        # no calls left costs a dict lookup and nothing else. The budget is
        # charged on the call because the call is the only thing that spends a
        # remote resource, but the GUARD is what has to come first.
        denied = _spend_call_budget(arm, now)
        if denied:
            if denied == THROTTLE_COOLDOWN:
                # Counted under its own name, never as a refusal.
                _count_in("throttles", denied)
            else:
                _refuse(denied)
                arm.refusals[denied] = arm.refusals.get(denied, 0) + 1
            outcomes[denied] = outcomes.get(denied, 0) + 1
            continue

        series = _series_for(store, sig, trigger_tf)
        if series is None:
            _refuse(REFUSE_NO_SERIES)
            outcomes[REFUSE_NO_SERIES] = outcomes.get(REFUSE_NO_SERIES, 0) + 1
            continue
        bar_ms = int(series["open_time"][-1]) if len(series.get("open_time", [])) else 0
        if bar_ms and bar_ms == arm.last_bar_evaluated_ms:
            # Not a refusal. Between bar closes there is genuinely nothing new
            # to decide, and counting that as a failure is how a real one stops
            # standing out.
            outcomes[REFUSE_NO_BAR] = outcomes.get(REFUSE_NO_BAR, 0) + 1
            continue

        price = _safe_price(price_fn, sig)
        menu = _build_menu_for(sig, series, price)
        snapshot = _snap.build_snapshot(
            signal=sig,
            trigger_tf=trigger_tf,
            as_of_bar_ms=bar_ms,
            bars_since_entry=_bars_since_entry(arm, series, trigger_tf, now),
            last_price=price,
            menu=menu,
            macro=macro or {},
            now=now,
        )
        snapshot = _snap.with_menu(snapshot, menu)

        trigger = should_trigger(arm, snapshot, macro_moved)
        arm.last_r = snapshot.r_multiple_now
        if trigger is None:
            outcomes[REFUSE_NO_TRIGGER] = outcomes.get(REFUSE_NO_TRIGGER, 0) + 1
            continue

        arm.last_bar_evaluated_ms = bar_ms
        _count("triggers")
        _count_in("by_action", f"trigger:{trigger}")
        batch[signal_id] = (snapshot, menu)

    with _arms_lock:
        n_arms = len(_arms)
    with _health_lock:
        _health["arms"] = n_arms

    if batch:
        # Fire and forget. Never awaited here — a 3-10s round trip inside the
        # monitor loop would stall the loop that owns the FSM clock.
        spawn = task_factory or asyncio.create_task
        spawn(evaluate(batch, now=now))

    return {
        "enabled": True,
        "arms": len(active),
        "batched": len(batch),
        "drained": drained,
        "outcomes": outcomes,
    }


async def evaluate(
    batch: Dict[str, Tuple[_snap.Snapshot, _menu.Menu]],
    *,
    now: Optional[float] = None,
    client: Optional[llm_client.LLMClient] = None,
) -> int:
    """Ask the model about a batch and queue the verdicts. Never raises.

    Batched by design: one request carrying every open signal shares one
    cacheable prefix, costs ~5x fewer calls, and lets the model see the
    correlation that ``MAX_SAME_DIRECTION_GLOBAL`` exists to bound.
    """
    from config import AI_GOV_OUTPUT_TOKEN_FLOOR

    now = _now() if now is None else now
    cli = client or _client()
    try:
        if not llm_client.configured(cli.provider):
            # A named state, not a silence: an unconfigured lane is a decision
            # nobody has taken yet, and it must not render as a failure.
            _refuse(REFUSE_NOT_CONFIGURED)
            _count_in("provider_status", llm_client.NOT_CONFIGURED)
            return 0

        payload = {
            "schema": PROMPT_SCHEMA,
            "positions": [snap.as_dict() for snap, _m in batch.values()],
        }
        for _sid in batch:
            with _arms_lock:
                arm = _arms.get(_sid)
            if arm is not None:
                arm.calls_made += 1
                arm.last_call_at = now
        _call_times.append(now)
        _count("calls")

        # A FLOOR plus a per-signal allowance, not a per-signal allowance
        # alone. The verdicts themselves are tiny (~50 tokens each), so 150 per
        # signal was ample for the ANSWER — and on a thinking-class model the
        # reasoning is drawn from this same budget before the answer is
        # written, so the whole allowance can be spent producing nothing. The
        # ceiling is not a reservation: unused tokens are not billed, and the
        # per-hour call bound is what actually caps the spend.
        budget = AI_GOV_OUTPUT_TOKEN_FLOOR + 150 * max(1, len(batch))
        result = await cli.complete_json(
            system=_SYSTEM_PROMPT,
            user=json.dumps(payload, separators=(",", ":")),
            schema=RESPONSE_SCHEMA,
            max_output_tokens=budget,
        )
        _count_in("provider_status", result.status)
        if result.status != llm_client.OK:
            _record_provider_failure(result, now, max_output_tokens=budget)
        with _health_lock:
            _health["latency_ms_last"] = int(result.latency_ms)
        _record_spend(
            llm_client.cost_usd(result.served_model or result.requested_model, result.usage),
            now,
        )
        if result.served_model:
            _count_in("served_models", result.served_model)
        if not result.ok:
            # Fail-open in behaviour, counted in telemetry. An unavailable
            # model never changes an exit; the default is the deterministic FSM.
            return 0

        verdicts = parse_verdicts(result.data or {}, result=result, batch=batch, now=now)
        ledger = get_ledger()
        for verdict, snapshot, menu in verdicts:
            # MAINTAIN rows are recorded too. A lane that logs only its
            # interventions cannot compute a baseline and will look brilliant.
            row = verdict.as_row()
            row["snapshot"] = snapshot.as_dict()
            row["unknown_frac"] = round(snapshot.blind_fraction(), 4)
            # Beside the pooled fraction, never instead of it. Book-blind and
            # flow-blind have different causes and different fixes, and the
            # pooled number cannot say which — see `Snapshot.readability`.
            row.update(snapshot.readability())
            ledger.add(row)
            _count("verdicts")
            _count_in("by_action", verdict.action)
            with _arms_lock:
                arm = _arms.get(verdict.signal_id)
                if arm is not None:
                    arm.standing = verdict
            with _queue_lock:
                if len(_queue) >= _QUEUE_MAX:
                    _refuse(REFUSE_QUEUE_FULL)
                _queue.append((verdict, snapshot, menu))
        return len(verdicts)
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor.evaluate", exc)
        return 0
    finally:
        if client is None:
            await cli.close()


# ── Apply — the path that scales with members ───────────────────────────────

async def drain_verdicts(*, now: Optional[float] = None, placer_factory: Any = None) -> int:
    """Apply what was queued BEFORE this tick began. Returns verdicts handled.

    Bounded by the depth at entry, and that bound is load-bearing rather than
    tidy. `_requeue` puts a paced verdict back on the same queue, so an
    unbounded ``while _queue`` would pop it, find the pacing budget unchanged
    within this same instant, requeue it, and pop it again — a live-lock inside
    the monitor tick, on the loop that owns SL/TP monitoring for every open
    position. Taking the depth once means a requeued verdict waits for the next
    tick, which is exactly what pacing means.

    The other half of the same reasoning: a verdict arriving from an evaluation
    task *while* this drain runs is also next tick's work. Applying it here
    would mean acting on a verdict younger than the state re-read at the top of
    the tick.
    """
    now = _now() if now is None else now
    with _queue_lock:
        pending = len(_queue)
    handled = 0
    for _ in range(pending):
        with _queue_lock:
            if not _queue:
                break
            verdict, snapshot, menu = _queue.popleft()
        try:
            await apply_verdict(
                verdict, snapshot, menu, now=now, placer_factory=placer_factory
            )
        except Exception as exc:  # noqa: BLE001
            fail_open.record("ai_governor.apply_verdict", exc)
        handled += 1
    return handled


async def apply_verdict(
    verdict: Verdict,
    snapshot: _snap.Snapshot,
    menu: _menu.Menu,
    *,
    now: Optional[float] = None,
    placer_factory: Any = None,
) -> str:
    """Act on one verdict, re-validating every precondition against state NOW.

    Returns the outcome name. Every refusal is counted; there is no path that
    both declines to act and says nothing.
    """
    from config import AI_GOV_VERDICT_MAX_AGE_SEC

    now = _now() if now is None else now

    # MAINTAIN costs NOTHING. Not a Firestore read, not a position walk, not an
    # exchange call. It is most of every window, and any per-user work here is
    # pure waste multiplied by the member count (§2.2).
    if verdict.action == MAINTAIN:
        _count_in("by_action", "applied:maintain")
        return MAINTAIN

    if now - verdict.issued_at > float(AI_GOV_VERDICT_MAX_AGE_SEC):
        # The stale-envelope rule the diag channel already uses: the world has
        # moved on, and applying a minutes-old exit decision from it is worse
        # than doing nothing.
        _refuse(REFUSE_STALE_VERDICT)
        return REFUSE_STALE_VERDICT

    if not apply_enabled():
        _refuse(REFUSE_APPLY_OFF)
        return REFUSE_APPLY_OFF

    arm = _ARM_OF.get(verdict.action)
    if arm is None or arm not in armed_arms():
        _refuse(REFUSE_ARM_OFF)
        return REFUSE_ARM_OFF

    positions = _open_positions_for(verdict.signal_id)
    if positions is None:
        # Cannot answer. Deliberately NOT a Firestore fallback: a per-user
        # collection scan here is the read that scales with the subscriber
        # count, and the whole point of the in-process index is to not take it.
        _refuse(REFUSE_INDEX_COLD)
        return REFUSE_INDEX_COLD
    if not positions:
        return "no_positions"

    if verdict.action == PANIC_CLOSE:
        return await _apply_panic(verdict, positions, now)
    return await _apply_level(
        verdict, snapshot, menu, positions, now, placer_factory
    )


async def _apply_panic(verdict: Verdict, positions: List[Any], now: float) -> str:
    """Close every position on this signal, bounded by an owner-set ceiling.

    A queued emergency close is not an emergency close, so this arm cannot be
    paced. It is bounded the other way instead — and when the ceiling is UNSET
    the arm refuses outright rather than running unbounded. An owner-set
    blast-radius cap that defaults to "unlimited" is not a cap, and this is the
    one arm where the absence of a number must not read as permission.
    """
    from config import AI_GOV_PANIC_MAX_POSITIONS

    ceiling = int(AI_GOV_PANIC_MAX_POSITIONS)
    if ceiling <= 0:
        _refuse(REFUSE_PANIC_CEILING_UNSET)
        return REFUSE_PANIC_CEILING_UNSET
    if len(positions) > ceiling:
        # Refused and NAMED, never silently truncated to the first N: closing
        # an arbitrary subset of a correlated book is a different action from
        # the one the model asked for, and picking the subset by iteration
        # order is order-dependent by construction.
        _refuse(REFUSE_PANIC_CEILING_HIT)
        _count_in("by_action", f"panic_refused:{len(positions)}>{ceiling}")
        return REFUSE_PANIC_CEILING_HIT

    from src.execution import signal_dispatch as _dispatch

    closed = await _dispatch.close_fsm_positions_for_signal(
        verdict.signal_id,
        symbol=verdict_symbol(verdict, positions),
        direction=verdict_direction(positions),
        reason="ai_governor_panic",
    )
    _count("applied", int(closed or 0))
    _count_in("by_action", "applied:panic")
    log.warning(
        "ai_governor: PANIC_CLOSE signal_id={} closed={} rationale={!r}",
        verdict.signal_id, closed, verdict.rationale,
    )
    return PANIC_CLOSE


async def _apply_level(
    verdict: Verdict,
    snapshot: _snap.Snapshot,
    menu: _menu.Menu,
    positions: List[Any],
    now: float,
    placer_factory: Any,
) -> str:
    """Move a TP or an SL across every position on this signal, paced."""
    cand = menu.lookup(verdict.choice or "")
    if cand is None:
        _refuse(REFUSE_UNKNOWN_CHOICE)
        return REFUSE_UNKNOWN_CHOICE

    if verdict.action == ADJUST_SL:
        # Two modules must never move one stop. `trail_governor` owns the stop
        # of any position carrying an exit mechanism, and a second mover would
        # re-buy every guard six sessions paid for — the -4130 collision, the
        # place-then-cancel ordering, the bar-keyed idempotence.
        governed = [p for p in positions if str(getattr(p, "exit_mechanism", "") or "")]
        if governed:
            _refuse(REFUSE_TRAIL_GOVERNED)
            _count_in("by_action", f"sl_skipped_governed:{len(governed)}")
            positions = [p for p in positions if p not in governed]
            if not positions:
                return REFUSE_TRAIL_GOVERNED

    if not _spend_apply_budget(now, count=len(positions)):
        # Deferred, not dropped: the existing protection stays exactly where it
        # is, and the next tick retries. A TP or SL adjustment is not urgent to
        # the second — it is a resting order — so pacing costs nothing but a
        # tick and protects the one IP the engine is whitelisted to.
        _refuse(REFUSE_APPLY_PACED)
        _requeue(verdict, snapshot, menu)
        return REFUSE_APPLY_PACED

    factory = placer_factory or _default_placer_factory
    applied = 0
    for position in positions:
        try:
            placer = factory(position.firebase_uid)
            if verdict.action == ADJUST_TP:
                ok = await _move_tp(position, cand.price, placer)
            else:
                ok = await _move_sl(position, cand.price, placer)
            if ok:
                applied += 1
        except Exception as exc:  # noqa: BLE001
            fail_open.record("ai_governor.apply_level", exc)
    _count("applied", applied)
    _count_in("by_action", f"applied:{verdict.action.lower()}")
    log.info(
        "ai_governor: {} signal_id={} choice={} price={} positions={} applied={}",
        verdict.action, verdict.signal_id, verdict.choice, cand.price,
        len(positions), applied,
    )
    return verdict.action


def _requeue(verdict: Verdict, snapshot: _snap.Snapshot, menu: _menu.Menu) -> None:
    """Put a paced verdict back for the next tick.

    Deferring is safe for a level move and only for a level move: the existing
    protection stays exactly where it is while it waits, so the cost is a tick.
    The staleness check at the top of `apply_verdict` still applies on the way
    back in, so a verdict that ages out while pacing is dropped and counted
    rather than applied late.
    """
    with _queue_lock:
        if len(_queue) >= _QUEUE_MAX:
            # A full queue while pacing means the apply path is not keeping up.
            # That is a fault to surface, not a depth to absorb.
            _refuse(REFUSE_QUEUE_FULL)
            return
        _queue.append((verdict, snapshot, menu))


async def _move_tp(position: Any, price: float, placer: Any) -> bool:
    """Place the new TP, then retire the one it replaces.

    Place-then-cancel, the same ordering `trail_governor` uses and for the same
    reason: a failed place leaves the position with its ORIGINAL take-profit
    resting, so nothing is given up. Cancel-then-place would leave a position
    running to its stop or to the 2h reconciler if the second half failed.
    """
    from src.execution import order_placer as _op
    from src.execution import position_state as _ps

    qty = float(getattr(position, "filled_qty", 0.0) or 0.0) - float(
        getattr(position, "closed_qty", 0.0) or 0.0
    )
    if qty <= 0:
        return False
    old_id = int(getattr(position, "tp1_order_id", 0) or 0)
    try:
        result = await placer.place_take_profit(
            signal_id=position.signal_id,
            symbol=position.symbol,
            direction=position.side,
            stop_price=float(price),
            quantity=qty,
            tp_phase="tp1",
        )
    except _op.OrderPlacementError as exc:
        _count_in("refusals", f"tp_place_failed:{type(exc).__name__}")
        return False
    new_id = int(getattr(result, "order_id", 0) or 0)
    position.tp1_order_id = new_id
    try:
        _ps.put_position(position)
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor.put_position", exc)
    if old_id and old_id != new_id:
        try:
            await placer.cancel_algo_order(symbol=position.symbol, algo_id=old_id)
        except _op.OrderPlacementError as exc:
            # The new TP is live and the old one is an orphan the FSM's
            # terminal-close sweep already retires. Counted, not fatal.
            _count_in("refusals", f"tp_cancel_failed:{type(exc).__name__}")
    return True


async def _move_sl(position: Any, price: float, placer: Any) -> bool:
    """Move the stop through `trail_governor`, never around it.

    That module is not "the SAR module" — it is the stop-placement engine, and
    six sessions bought its guards: the -4130 collision that made every
    handover impossible for a month, the place-then-cancel ordering that never
    leaves a position naked, `reduceOnly` with the position's own quantity, the
    zero-quantity refusal, and the explicit cancel-on-terminal sweep. A second
    module that moves a resting stop would re-buy every one of them.
    """
    from src.execution import trail_governor as _tg

    if not _tg.tightens(position.side, float(position.sl_price or 0.0), float(price)):
        _refuse(REFUSE_NOT_MONOTONE)
        return False
    return await _tg.park_external_level(
        position, float(price), placer=placer, source="ai_governor"
    )


def verdict_symbol(verdict: Verdict, positions: List[Any]) -> str:
    for p in positions:
        sym = str(getattr(p, "symbol", "") or "")
        if sym:
            return sym
    return ""


def verdict_direction(positions: List[Any]) -> str:
    for p in positions:
        side = str(getattr(p, "side", "") or "")
        if side:
            return side
    return ""


def _default_placer_factory(firebase_uid: str) -> Any:
    from src.execution import trail_governor as _tg

    return _tg._default_placer_factory(firebase_uid)


# ── Helpers — every one of them fail-soft and counted ───────────────────────

def _active_signals(signals: Any) -> Dict[str, Any]:
    """Normalise whatever the monitor hands us into {signal_id: signal}."""
    out: Dict[str, Any] = {}
    try:
        items = signals.values() if isinstance(signals, dict) else (signals or [])
        for sig in items:
            if str(getattr(sig, "status", "") or "").upper() != "ACTIVE":
                continue
            signal_id = str(getattr(sig, "signal_id", "") or "")
            if signal_id:
                out[signal_id] = sig
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor.active_signals", exc)
    return out


def _retire_missing(active_ids: set) -> None:
    """Drop arms whose signal is gone.

    Keyed on the population owed a decision, not on whatever list is
    convenient (#815). An arm that outlives its signal is the KORUUSDT shape:
    RUNNING forever, frozen, and reading as healthy on every panel.
    """
    with _arms_lock:
        for signal_id in [k for k in _arms if k not in active_ids]:
            _arms.pop(signal_id, None)


def _trigger_tf_for(sig: Any) -> str:
    """The setup's declared trigger timeframe.

    A setup absent from the map is REFUSED as `tf_unknown`, never defaulted to
    5m. `Scanner._get_primary_timeframe` returned the literal "5m" for every
    channel under a docstring claiming it was a lookup, and six money-path
    consumers read it — including two mover paths that trade 15m and are most
    of the book. A hand-maintained map is a floor; the miss has to be a counted
    refusal or it becomes that defect again.
    """
    try:
        from src import setup_timeframes as _stf

        declared = _stf.declared_for(str(getattr(sig, "setup_class", "") or ""))
        return str(declared or "")
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor.trigger_tf", exc)
        return ""


def _series_for(store: Any, sig: Any, timeframe: str) -> Optional[Dict[str, Any]]:
    try:
        from src import sar_live_shadow as _sar

        series, _reason = _sar._series_with_reason(
            store, str(getattr(sig, "symbol", "") or ""), timeframe, _menu.MIN_BARS
        )
        return series
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor.series", exc)
        return None


def _safe_price(price_fn: Any, sig: Any) -> Optional[float]:
    if price_fn is None:
        return None
    try:
        value = price_fn(str(getattr(sig, "symbol", "") or ""))
        return float(value) if value else None
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor.price", exc)
        return None


def _build_menu_for(sig: Any, series: Dict[str, Any], price: Optional[float]) -> _menu.Menu:
    rounder = None
    try:
        from src.execution import symbol_filters as _sf

        rounder = lambda px: _sf.round_price(sig.symbol, px)  # noqa: E731
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor.rounder", exc)

    return _menu.build_menu(
        side="LONG" if str(getattr(sig, "direction", "")).upper().endswith("LONG") else "SHORT",
        entry=float(getattr(sig, "entry", 0.0) or 0.0),
        current_sl=float(getattr(sig, "stop_loss", 0.0) or 0.0),
        current_tp1=float(getattr(sig, "tp1", 0.0) or 0.0),
        highs=series.get("high"),
        lows=series.get("low"),
        closes=series.get("close"),
        last_price=float(price or 0.0),
        round_price=rounder,
    )


def _bars_since_entry(arm: Arm, series: Dict[str, Any], timeframe: str, now: float) -> int:
    """Bars elapsed, from the arm's own clock rather than from array length.

    Deriving an index from wall-clock arithmetic assumes gap-free, current data
    and fails silently when that breaks — which is how a replay landed on an
    unrelated bar and published 172 confident rows describing nothing. This is
    a *reported* figure, never an index into anything, so an imprecise answer
    costs a slightly wrong column and cannot move a level.
    """
    try:
        from src import sar_live_shadow as _sar

        seconds = _sar.timeframe_seconds(timeframe)
        if not seconds:
            return 0
        return max(0, int((now - arm.opened_at) / float(seconds)))
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor.bars_since_entry", exc)
        return 0


def _open_positions_for(signal_id: str) -> Optional[List[Any]]:
    """Non-terminal positions on this signal, from the IN-PROCESS index.

    ``None`` means the index is cold — we could not ask — and is kept strictly
    apart from an empty list, which means nobody is in this trade. Conflating
    them would let a cold index read as "nothing to do" on a panic close.
    """
    try:
        from src.execution import position_state as _ps

        positions = _ps.index_open_positions()
        if positions is None:
            return None
        return [
            p for p in positions
            if str(getattr(p, "signal_id", "")) == str(signal_id)
            and not _ps.is_terminal(p.state)
        ]
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor.open_positions", exc)
        return None


# ── Ops surface ─────────────────────────────────────────────────────────────

def blindness(sample: int = 200) -> Dict[str, Any]:
    """How much context the recent verdicts actually had.

    `docs/PLAN_AI_TRADE_GOVERNOR.md` §3 specified this and nothing published it,
    so the ledger carried the per-row stamp while every surface was silent on
    it. A fail-open governor is *designed* to answer without book or flow — the
    cost of that choice is that an inert lane reads exactly like a working one
    on every count except this one, which is why it is a first-class block
    rather than a footnote.

    Reasons are counted separately from the totals because they have different
    next moves: ``not_subscribed`` is a stream-budget decision, ``stale`` is an
    incident, ``disabled`` is a switch nobody threw, and ``error`` is ours.
    """
    rows = get_ledger().rows()[-int(max(1, sample)):]
    if not rows:
        # Not a fault, and not zero blindness either: nothing has been asked
        # yet. A caller that renders 0% here would report a healthy lane on an
        # empty one.
        return {"rows": 0, "measured": False}

    def _count_reason(flag: str, reason: str) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for row in rows:
            if row.get(flag) is False:
                key = str(row.get(reason) or "unknown")
                out[key] = out.get(key, 0) + 1
        return out

    stamped = [r for r in rows if "book_readable" in r]
    fracs = [float(r.get("unknown_frac") or 0.0) for r in rows if r.get("unknown_frac") is not None]
    return {
        "rows": len(rows),
        "measured": True,
        # Rows written before the split shipped carry the pooled fraction only.
        # Counted apart rather than folded in: a missing stamp is not a pass.
        "rows_with_split": len(stamped),
        "avg_unknown_frac": round(sum(fracs) / len(fracs), 4) if fracs else None,
        "fully_blind": sum(1 for f in fracs if f >= 1.0),
        "book_blind": sum(1 for r in stamped if r.get("book_readable") is False),
        "flow_blind": sum(1 for r in stamped if r.get("flow_readable") is False),
        "book_reasons": _count_reason("book_readable", "book_reason"),
        "flow_reasons": _count_reason("flow_readable", "flow_reason"),
    }


def build_scorecard() -> Dict[str, Any]:
    """The scorecard, as its OWN diagnostic read — never folded into `build_diag`.

    It was folded in on the first cut and the production deploy said no: with
    every other catalog entry answering in 0.0s, `read.ai_governor` blew its 25s
    budget, because this is the only part of that payload that parses the
    closed-signal record off disk. A heavy read and a light one are different
    questions and belong in different entries — the arms, bounds and refusals
    must stay readable when the record is large, slow, or absent.

    It is also why `build_diag` no longer calls this at all: its one production
    caller is `main.py`'s maintenance loop, which builds that payload as the
    `extra` of `flush(force=True)`, so anything slow or raising there is charged
    to the ledger's HEARTBEAT. A missing panel is a missing panel; a stalled
    flush is a lost window.

    Returns a block the page can render either way — "the scorecard failed" and
    "the scorecard is empty" send a reader to different places.
    """
    try:
        return _score.build(get_ledger().rows())
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor.build_scorecard", exc)
        return {"error": f"{type(exc).__name__}: {exc}".strip() or type(exc).__name__}


def build_diag() -> Dict[str, Any]:
    """Everything the ops page needs, assembled in the ENGINE process.

    Published through Redis like the sibling X-rays: in isolated mode the api
    container cannot see the arms or the position index, and a diagnostic
    assembled there describes the wrong process (`INDEX COLD`).
    """
    from config import (
        AI_GOV_MAX_CALLS_PER_HOUR,
        AI_GOV_MAX_CALLS_PER_SIGNAL,
        AI_GOV_MAX_USD_PER_DAY,
        AI_GOV_PANIC_MAX_POSITIONS,
    )

    ledger = get_ledger()
    provider = str(_tunable("ai_gov_provider", ""))
    return {
        "measure_enabled": measure_enabled(),
        "apply_enabled": apply_enabled(),
        "armed_arms": list(armed_arms()),
        "provider": provider,
        "provider_configured": llm_client.configured(provider),
        "model_requested": str(_tunable("ai_gov_model", "")),
        "prompt_schema": PROMPT_SCHEMA,
        "rate_table_version": llm_client.RATE_TABLE_VERSION,
        "rate_table_read_on": llm_client.RATE_TABLE_READ_ON,
        "bounds": {
            "calls_per_signal": int(AI_GOV_MAX_CALLS_PER_SIGNAL),
            "calls_per_hour": int(AI_GOV_MAX_CALLS_PER_HOUR),
            "usd_per_day": float(AI_GOV_MAX_USD_PER_DAY),
            # Rendered even when unset, because unset is a STATE here: the
            # panic arm refuses while it is zero, and a missing row would read
            # as an arm that is simply quiet.
            "panic_max_positions": int(AI_GOV_PANIC_MAX_POSITIONS),
            "panic_armed": int(AI_GOV_PANIC_MAX_POSITIONS) > 0,
        },
        "health": health(),
        "arms": arms_snapshot(),
        "ledger_rows": ledger.count(),
        "ledger_evicted": ledger.evicted,
        "queue_depth": len(_queue),
        # The per-row stamp has always existed and nothing aggregated it, so no
        # surface could say whether a verdict was informed or blind — which
        # makes every verdict on the page uninterpretable in either direction.
        "blindness": blindness(),
    }


def probe_blindness() -> Tuple[bool, str]:
    """Fails when the lane is issuing verdicts on essentially no context.

    Fail-open is deliberate — the input is a measurement lane, and a
    fail-closed governor would freeze exits the moment a feed hiccupped. The
    cost of fail-open is that an inert lane reads exactly like a working one on
    every count except this, which is why total blindness is a fault in either
    mode. Returns ``True`` (not a raise) when idle: signalling a non-event by
    raising fills `fail_open` with things that are not failures, and that is how
    a real one stops standing out.
    """
    rows = get_ledger().rows()[-50:]
    if not rows:
        return True, "no verdicts yet"
    blind = [r for r in rows if float(r.get("unknown_frac") or 0.0) >= 1.0]
    frac = len(blind) / float(len(rows))
    if frac >= 0.95:
        return False, f"{len(blind)}/{len(rows)} verdicts had no readable context"
    return True, f"blind {frac:.0%} of last {len(rows)}"
