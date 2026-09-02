# The Post-Emission AI Trade Governor

**Status:** design of record. Written 2026-09-02, before any code. Nothing in this
document is implemented.
**Owner request:** *"build an asynchronous AI Trade Governor… the deterministic
system must execute the trade instantly to avoid slippage. The AI steps in
immediately after the trade is live… Maintain / Adjust TP / Adjust SL / Panic
Close… strictly formatted JSON that our FSM can instantly parse and execute."*
**Companions:** `docs/LLM_SIGNAL_CRITIC_BRIDGE.md` (the pre-dispatch sibling — §1
below), `docs/STATISTICAL_CHANGE_POLICY.md` (binds the rollout — §11),
`docs/PRICE_ACTION_PROGRAM.md` (owns the reality-feed inputs — §3).

Two standing rules from `CLAUDE.md` govern this document, and they are why it
exists before the code:

- **Re-check the claim before you test it.** Every fact below is labelled
  **[verified]** (read from this source tree or an official vendor page during the
  session that wrote this), **[documented]** (vendor documentation I could read but
  not exercise), or **[inferred]**. An unlabelled inference reads exactly like a
  measurement.
- **A finding and a fix are separate deliverables.** §1–§5 are findings about what
  this system can and cannot support. §6 onward is the build.

---

## 0. Executive summary

The brief is buildable and it is worth building. Three things in it, read
literally, would sink it, and all three are architectural rather than a matter of
prompt quality:

1. **"Spawn a task dedicated to that trade" is the wrong unit.** One *signal* fans
   out to N *positions*. At the owner's 1,000-member target that is the same
   question asked 1,000 times a tick. Governing the **signal** instead of the
   position is a ~200,000× reduction in calls on identical information (§2).
2. **A 15–30s wall-clock loop is the wrong clock.** The mechanism this repo already
   validated parks a level *knowable before the bar trades*; a timer-driven verdict
   describes a market state that is gone by the time it lands (§4).
3. **An LLM that emits prices is unbounded; an LLM that picks from a menu is
   bounded by the menu.** The engine computes and pre-validates candidate levels;
   the model returns a **choice key**, never a float (§5).

With those three corrections the whole thing costs **$0.68–$37/month** depending
on model tier (§9) — one to two Auto subscribers at ₹2,000/mo — and the cost question
stops being interesting. What remains interesting is whether it makes money, and
this repo's own history says the prior is **negative**: the real pre-TP +
invalidation exit machinery netted **−25.79%** across 494 live signals while a plain
TP1-full exit netted **−6.65%** on the same signals, a **+19.14%** gap
(`OWNER_BRIEF.md` §3.2) **[verified]**. *The exit logic, not the entries, was
giving back the edge.* An AI governor is a more sophisticated version of exactly
that. So the baseline it must beat is TP1-full net of fees, and the shadow window —
not the mechanism — is the deliverable.

Under `docs/STATISTICAL_CHANGE_POLICY.md` rule 1 that window is **months, not
weeks** (§11). Say so now, so nobody is surprised in November.

---

## 1. The sibling doc, and what changed

`docs/LLM_SIGNAL_CRITIC_BRIDGE.md` (2026-07-22, design of record, **never
implemented** — `src/llm_signal_critic.py` does not exist and no `LLM_CRITIC_*` key
appears in `config/` **[verified]**) covers the **pre-dispatch** critic: review the
geometry *before* the signal posts. Its §1 gives four structural reasons not to put
an LLM inline on the money path. This document is the **post-emission** counterpart,
so each of those four has to be answered rather than assumed away.

| Critic-bridge §1 objection | Does it apply post-entry? |
|---|---|
| **1. Latency vs decay.** An LLM round trip decays a precise scalp entry; inline review *manufactures* the `dispatch_staleness` leak measured at −0.63R. | **Partly, and differently.** There is no entry left to decay — the fill happened. What decays is the *exit level*, and the answer is the same one `trail_governor` already uses: decide on **closed bars**, park a level knowable before the next bar trades (§4). This is a real mitigation, not a dismissal. |
| **2. Non-determinism kills measurement.** | **Fully, unchanged.** This is the hardest constraint in the document and §10 is written around it. |
| **3. Symptoms, not root cause — per-signal LLM edits are a scaffold, and scaffolds are banned.** | **Fully.** Inherited verbatim: the governor is a **hypothesis generator**, and its wins are harvested into deterministic rules (§12 Phase 4). It is not a permanent oracle. |
| **4. Trust + cost on the money path.** | **Fully, and worse.** The critic proposed geometry on a signal not yet placed; this one can close a live position at market. §5 (menu, not prices), §7 (invariants in code) and §8 (budget) exist for this. |

Its §6 already anticipated this document: *"a bounded pre-dispatch VETO gate
(reject-only, never silently edit) … a veto is boundable and safe; an inline
geometry editor on scalps is not."* The governor is that idea moved past the fill,
where a veto is a **close** rather than a suppression.

**Reuse, not a second client.** The critic bridge specifies `ANTHROPIC_API_KEY`,
prompt caching on a frozen doctrine prefix, and the Batch API. Both lanes want the
same client, the same secret handling and the same rate table. `src/llm_client.py`
is therefore a shared module (§6) and the critic bridge, when it is built, consumes
it. Two vendor clients for two lanes is the drift this repo has paid for under
several names.

---

## 2. The unit of work is the SIGNAL, not the position

This is the single decision that determines whether the feature is affordable.

**[verified]** `config/__init__.py:2817` — `MAX_CONCURRENT_SIGNALS_PER_CHANNEL`
caps `360_SCALP` at **5**; `MAX_SAME_DIRECTION_GLOBAL` is **3**. The live book
carries a handful of distinct theses at any moment.

**[verified]** `src/execution/signal_dispatch.py:660` —
`dispatch_signal_to_active_users()` fans **one signal to every active uid**. At the
owner's stated target of 1,000 auto-trade members (`CLAUDE.md`, owner 2026-09-02)
that is ~5 concurrent theses expressed as ~5,000 concurrent positions.

Everything in the brief's Reality Feed — order-book imbalance, CVD, BTC context, the
wall in front of TP — is a fact about the **symbol**, not about the user. The only
per-user facts are quantity and which exit profile the user opted into (B17), and
those are deterministic filters applied *after* the verdict, never inputs to it.

| Design | Calls/day at 1,000 members | Note |
|---|---|---|
| Per-position, 15s (brief as written) | **28,800,000** | 5 × 1,000 × 4/min × 1,440 |
| Per-position, 30s | 14,400,000 | |
| **Per-signal**, 30s timer | **14,400** | identical information |
| **Per-signal, event-gated**, ≤8 calls/position | **~120** | §4 |
| + macro batching (all open signals in one call) | **~50–90** | |

**[inferred, from the caps above and ~16 delivered signals/day]** the gated figure
is ~120 calls/day. The first row and the fourth differ by a factor of ~240,000 on
the same information. Nothing else in this document matters as much.

**Corollary — the arm outlives the user.** A verdict is stamped once per signal and
applied to every eligible position. A user who joins mid-trade inherits the standing
verdict; a user whose position closes early drops out. The governor's lifetime is
the **signal's**, not any one position's — which is #835's lesson (*a measurement
that rides another subsystem's loop inherits that subsystem's lifetime*) applied
before it can be paid for again.

---

## 3. What the Reality Feed can actually see today — audit

The brief asks for four inputs. Three exist; their coverage is narrower than the
brief assumes, and a governor that treats a missing input as a neutral one is the
`zone_distance_atr` failure (a feature uncomputable from the day it shipped,
0 of 57 rows, two passing tests over a shape nothing produced).

| Brief input | What exists | Coverage / caveat |
|---|---|---|
| **Current price action** | `HistoricalDataStore` multi-TF candles; `mark_price_feed`; `_publish_pricing_freshness` already flags a `blind` signal **[verified]** | Good. Freshness is already published per open signal — the governor reads that, it does not re-derive it. |
| **Order-book imbalance** | `src/depth_book.py`, `@depth20@500ms` **[verified]** | `DEPTH_MAX_SYMBOLS = 40` **[verified]**, and `DEPTH_LIVE_FOR_CONSUMERS` defaults **false** **[verified]**. Much of the delivered book is promoted movers outside the core universe, so *a large share of governed signals will have no book at all.* |
| **CVD** | `src/live_ticks.py` (`@aggTrade`), `src/footprint.py`, and `entry_features.cvd_slope_aligned` **[verified]** | `AGGTRADE_MAX_SYMBOLS = 40` **[verified]**. Same coverage hole. **Use the `_aligned` form** — `cvd_slope_aligned` / `book_imbalance_aligned` are signed toward the trade (`src/entry_features.py:923,929` **[verified]**); the raw values score every SHORT backwards, which cost a session and never showed up as an empty column. |
| **Macro / BTC** | `src/market_context.py` — BTC-anchored session/phase/volatility/funding/rotation vector, published each 5-min cycle, pure and network-free **[verified]** | Available and free. Its `context_key` is the same key Layer C routes on, so a governor keyed on it is comparable with the edge matrix. |

**Three consequences for the design:**

1. **A missing input is `unknown`, never zero.** An em-dash is "we could not ask";
   `0.0` there is how a blank becomes a finding. Every field in the snapshot carries
   its own readability, per `CLAUDE.md`'s hard limit on rendering an unreadable
   money-path flag as a readable one.
2. **The governor must publish its own blindness rate.** A verdict issued with the
   book and CVD both absent is a verdict on price action and macro alone. That is a
   legitimate verdict; presenting it as a full-context one is not. `unknown_frac`
   is a column, and an *enforcing* governor blind on most of its population pages
   the watchdog — the same rule `entry_quality` carries.
3. **Depth and aggTrade coverage is the real Phase-0 dependency.** If the governor
   is to see walls on mover pairs, `DEPTH_MAX_SYMBOLS` has to cover the open book,
   not the top 40. That is a stream-budget question owned by
   `docs/PRICE_ACTION_PROGRAM.md` §4, and it is **out of scope here** — this
   document consumes what exists and names what it cannot see.

---

## 4. The clock — bar-aligned, plus a trigger ladder

**Not a timer.** `trail_governor`'s docstring states the property that makes a
mechanism placeable: `trail_mechanisms.point()` *"returns the level in force for the
bar now forming, projected from closed bars only — knowable before the bar trades,
which is precisely what a resting stop needs"* **[verified]**. A wall-clock verdict
has no such property: it describes a mid-bar state that has already moved by the
time the round trip lands, and it cannot be replayed, because there is no bar to
replay it against.

So the governor evaluates **on closed bars of the position's own trigger timeframe**
(`src/setup_timeframes.py` declares it per setup; a setup absent from the map is
refused as `tf_unknown` rather than defaulted **[verified]**), and *within* that,
only when a deterministic pre-filter says the state materially moved.

### The trigger ladder

Computed every monitor tick (`MONITOR_POLL_INTERVAL = 5.0` **[verified]**) from data
already in the process — zero marginal cost, no network, no Firestore:

| Trigger | Scope | Why |
|---|---|---|
| Position crossed an R-band (±0.5R, ±1.0R) | per signal | the state the brief's "deep profit" case names |
| Distance to TP1 fell inside the band where a wall could matter | per signal | the only window in which "front-run the resistance" is actionable |
| Notional resting ahead of TP1 exceeded a multiple of recent traded size | per signal | requires depth (§3) |
| `cvd_slope_aligned` flipped sign against the trade | per signal | requires aggTrade (§3) |
| BTC moved > k×ATR in N minutes | **global — one batched call covering every open signal** | the brief's headline case, and the reason `MAX_SAME_DIRECTION_GLOBAL` exists |
| `market_context.context_key` changed | **global — batched** | 5-min cycle, already published |

**Batch by default.** One request carrying an array of all open signals returns an
array of verdicts: ~5× fewer calls, one shared cacheable prefix, and it lets the
model see the correlation the correlation throttle exists to bound. Single-signal
calls only for signal-specific triggers.

### Three hard bounds, spent at the top

**This is the Session 137 lesson and it is not negotiable.** The orphan sweep's
budget was named for what it *does* (cancel) and only decremented on that branch;
production takes the other branch, so it spent nothing, ran unbounded, got the box
rate-limited off Binance and **took auto-trade down for every paid user for ~4
hours** **[verified — `CLAUDE.md`, incident 2026-09-01]**.

Therefore: **every bound is decremented per signal EXAMINED, before any work** —
before the pre-filter, before the snapshot build, before any call. A budget that
only decrements when an LLM call is actually issued is unbounded on the path
production takes.

1. `AI_GOV_MAX_CALLS_PER_SIGNAL` — lifetime, per signal
2. `AI_GOV_MAX_CALLS_PER_HOUR` — global rolling
3. `AI_GOV_MAX_USD_PER_DAY` — global, from the provider's returned `usage`, never estimated

On exhaustion the verdict is `MAINTAIN` stamped `budget_exhausted` — a **named,
counted refusal** rendered as its own state. It must never pool with "the model said
maintain", or a spent budget reads as a quiet market.

---

## 5. The output contract — a menu, never a price

**The model selects; it does not compute.** This is a direct port of two properties
this repo already relies on:

- `trail_governor` *"computes nothing about SAR"* — the mechanism is deterministic
  and reconciled bit-exact against Binance's own candles over 5,400 bars, and the
  governor answers only *"given that level, what order should exist right now"*
  **[verified]**.
- `src/diag_catalog.py` accepts a **key** selected from a registry, never a command,
  with no shell and no argument interpolated into a command line **[verified]** —
  which is what made an ops-driven engine action admissible at all.

So the engine builds the candidate set, pre-validates every member, and the model
returns an index into it.

### Why this is not merely tidier

- A hallucinated float is unbounded. A hallucinated key is bounded by a menu we
  built, and an unrecognised key is a **counted refusal**, not a price.
- Every candidate is validated *before it is offered*: tick-rounded via
  `_sf.round_price`, monotone-safe, past `would_breach_min_distance`
  (`structural_snap.REFUSE_MIN_DISTANCE` **[verified]**), and non-naked.
- A menu makes the verdict **replayable**. The same snapshot and the same menu can
  be re-scored later; a free float cannot be reconstructed from anything.
- It bounds the prompt-injection surface to a choice among options we authored.

### Request (batched)

```json
{
  "schema": 1,
  "as_of_bar_ms": 1756800000000,
  "macro": {
    "context_key": "OVERLAP|TRENDING_UP|HIGH_VOL|BTC_LEADS",
    "btc_ret_1m": -0.0031, "btc_ret_5m": -0.0118, "btc_atr_mult": 2.4,
    "btc_readable": true
  },
  "positions": [
    {
      "signal_id": "sig_01J...",
      "symbol": "ARBUSDT", "side": "LONG", "setup_class": "MOVER_TREND_PULLBACK",
      "entry_regime": "TRENDING_UP", "trigger_tf": "15m",
      "bars_since_entry": 7,
      "dist_to_tp1_pct": 0.42, "dist_to_sl_pct": -1.81,
      "r_multiple_now": 0.31, "tp1_r_multiple": 0.79,
      "mfe_pct": 0.55, "mae_pct": -0.22,
      "book": { "readable": false, "reason": "not_subscribed" },
      "flow": { "readable": true, "cvd_slope_aligned": -0.41, "cvd_source": "15m" },
      "tp_candidates": [
        {"key": "tp_0", "kind": "current",     "dist_pct": 0.42},
        {"key": "tp_1", "kind": "swing",       "dist_pct": 0.28},
        {"key": "tp_2", "kind": "vp_poc",      "dist_pct": 0.19}
      ],
      "sl_candidates": [
        {"key": "sl_0", "kind": "current",     "dist_pct": -1.81},
        {"key": "sl_1", "kind": "breakeven",   "dist_pct": 0.00},
        {"key": "sl_2", "kind": "swing",       "dist_pct": -0.74}
      ]
    }
  ]
}
```

Every candidate carries `dist_pct` **signed toward the trade**, so "nearer" and
"tighter" mean the same thing on a LONG and a SHORT. `kind` names the generator, so
an all-`swing` column reads as the round-number grid being inert rather than as
round numbers being unhelpful — the `round_step_pct` lesson.

### Response (strict schema, one element per position)

```json
{
  "schema": 1,
  "verdicts": [
    {
      "signal_id": "sig_01J...",
      "verdict": "MAINTAIN | ADJUST_TP | ADJUST_SL | PANIC_CLOSE",
      "choice": "tp_2",
      "premise_broken": ["macro_regime_flip", "flow_opposed"],
      "confidence": 0.72,
      "rationale": "BTC down 1.2% in 5m with CVD turning against the long; taking the nearer VP target."
    }
  ]
}
```

Constraints, enforced by the API's structured-output mode **and** re-checked on
parse: `choice` is `null` for `MAINTAIN`/`PANIC_CLOSE` and otherwise **must** be a
key from that position's own menu; `rationale` ≤ 140 chars (it goes to Telegram
anyway); `premise_broken` is drawn from a closed vocabulary. No free text elsewhere,
no chain-of-thought in the response, `max_tokens` ~150 per position.

**Unknown fields do not fail the parse.** A provider that adds a key must not empty
the lane — the row is accepted, the extra key stamped, and the schema bump decided
deliberately (§10).

---

## 6. Architecture

```
signal delivered (router-confirmed)  ──►  FSM opens positions for N users
        │                                        (unchanged, deterministic, instant)
        │  arm opened ONCE PER SIGNAL
        ▼
  ai_governor.arm(signal)                        [engine container]
        │
        │  monitor loop, 5s tick, per closed bar of the signal's trigger TF
        ▼
  ai_governor.sweep(store)  ── budget spent at top, per signal examined
        │    │
        │    └─ trigger ladder (deterministic, in-process, no network)
        │           │  fires
        │           ▼
        │    asyncio.create_task(evaluate)   ── NEVER awaited in the sweep
        │           │
        │           ▼   src/llm_client.py  (shared with the critic bridge)
        │      provider ── strict JSON schema, temperature 0, pinned model version
        │           │
        │           ▼
        │    bounded verdict queue  (maxlen; oldest dropped and counted)
        │
        ▼  NEXT tick drains the queue
  apply(verdict)  ── re-validate EVERY precondition against state NOW
        │              stale (> 1 tick) → refused, counted, never applied
        ├─ ADJUST_TP   → cancel + re-place the reduce-only LIMIT (SL keeps resting)
        ├─ ADJUST_SL   → trail_governor._park(...)  place-then-cancel, reduceOnly
        └─ PANIC_CLOSE → signal_dispatch.close_fsm_positions_for_signal(...)
        │
        ▼
  ai_governor ledger  ──► ops /signals/ai-governor   ──► FCM / Telegram rationale
```

### Module map (all new and additive, except the two reused primitives)

| Concern | File |
|---|---|
| Provider-neutral client, retries, usage accounting, secret handling | `src/llm_client.py` (new — **shared with `LLM_SIGNAL_CRITIC_BRIDGE`**) |
| Arm lifecycle, trigger ladder, sweep, budget, verdict queue | `src/execution/ai_governor.py` (new) |
| Candidate-menu construction + pre-validation | `src/execution/ai_governor_menu.py` (new; reads `level_book`, `volume_profile`, `structural_levels`) |
| Snapshot assembly (the Reality Feed, with per-field readability) | `src/execution/ai_governor_snapshot.py` (new) |
| Ledger + two-arm counterfactual | `src/ai_governor_ledger.py` (new; `ledger_schema.accepts` + `ADDITIVE_FROM_SCHEMAS`) |
| **SL placement** | **reuse `src/execution/trail_governor.py` `_park` — no second stop-mover** |
| **Panic close** | **reuse `src/execution/signal_dispatch.py` `close_fsm_positions_for_signal` [verified]** |
| Liveness probes | `src/feature_liveness.py` (`RateProbe` + `PredicateProbe` **[verified]**) |
| Ops read | `src/diag_catalog.py` entry (`read.ai_governor`) |
| Config | `config/__init__.py` |

### Why the SL arm reuses `trail_governor` rather than placing its own stop

`trail_governor` is not "the SAR module"; it is the **stop-placement engine**, and
six sessions bought its guards: the -4130 collision that made every handover
impossible for a month, the place-then-cancel ordering that never leaves a position
naked, `reduceOnly` with the position's own quantity, bar-keyed idempotence,
`REFUSE_NO_QUANTITY`, the explicit cancel-on-terminal sweep, and the vendor-rejection
ring **[verified from the module docstring and `_park`]**. A second module that moves
a resting stop would re-buy every one of those. The AI governor emits an **intent**;
`trail_governor` executes it.

**One extension is required and it is small:** `_park` is currently reached from
`step_position`, which computes its level from `trail_mechanisms`. It needs an entry
point that accepts a caller-supplied level with a caller-supplied provenance tag, so
the health counters can tell an AI-sourced park from a mechanism-sourced one. Those
two populations must never pool — a governor that degrades the trail lane's numbers
while looking healthy itself is the exact shape of `sar_live_shadow`'s health-lane
split.

### The async contract

**The LLM is never awaited inside the sweep.** `MONITOR_POLL_INTERVAL` is 5.0s and
that loop already carries `_process_signal` fan-out, four measurement lanes and the
trail governor **[verified, `src/trade_monitor.py:1130–1180`]**. A 3–10s round trip
inside it would stall the loop that owns the FSM clock — and the instrument would be
blind to its own stall, because *an instrument that travels on a starved channel
cannot measure the starvation* (2026-08-19).

So: `create_task`, a bounded queue, and the **next** tick applies. Concretely —

- The evaluation task holds no reference to a `Position`. It carries an immutable
  snapshot; positions mutate under it.
- Applying re-reads state from `position_state.index_open_positions()`
  **[verified — returns `Optional[list[Position]]`, `None` meaning "cannot answer",
  which is refused as `index_cold` rather than falling back to Firestore]**.
- A verdict older than one tick is **refused and counted**, never applied — the
  stale-envelope rule the diag channel already uses: the requester stopped waiting,
  and applying a minutes-old exit decision from a world that has moved on is worse
  than doing nothing.
- Task count is bounded by the open-signal cap, so there is no unbounded fan-out.

### Which container

**Engine.** The governor needs the in-process position index and the candle store;
assembling this in the api container is the `INDEX COLD` defect
(`/internal/diag/trail-governor` read cold in production while the governor worked
fine) **[verified]**. Ops reads through Redis, like the three sibling X-rays.

---

### The shapes

Dataclasses, frozen where they cross a task boundary — an evaluation task must not
be able to mutate what the sweep is holding.

```python
@dataclass(frozen=True)
class Candidate:
    key: str            # "tp_2" — what the model returns
    kind: str           # "current" | "swing" | "vp_poc" | "round" | "breakeven"
    price: float        # tick-rounded, pre-validated
    dist_pct: float     # SIGNED TOWARD THE TRADE

@dataclass(frozen=True)
class Readable:
    """A value and whether we could observe it. Never a bare float."""
    value: Optional[float]
    readable: bool
    reason: str = ""    # "not_subscribed" | "stale" | "ok"

@dataclass(frozen=True)
class Snapshot:
    """Immutable. Stored with the verdict, so a row can be re-scored."""
    signal_id: str; symbol: str; side: str; setup_class: str
    trigger_tf: str; as_of_bar_ms: int; taken_at: float
    price: Readable; dist_to_tp1_pct: float; dist_to_sl_pct: float
    r_multiple_now: float; tp1_r_multiple: float
    mfe_pct: float; mae_pct: float; bars_since_entry: int
    book_imbalance_aligned: Readable; cvd_slope_aligned: Readable
    macro: Mapping[str, Any]          # market_context vector + BTC returns
    tp_candidates: Tuple[Candidate, ...]
    sl_candidates: Tuple[Candidate, ...]

@dataclass(frozen=True)
class Verdict:
    signal_id: str
    action: str                 # MAINTAIN | ADJUST_TP | ADJUST_SL | PANIC_CLOSE
    choice: Optional[str]
    confidence: float
    rationale: str
    premise_broken: Tuple[str, ...]
    # provenance — every one of these is stamped, none is optional
    model: str                  # exact version string
    prompt_schema: int
    snapshot_digest: str
    as_of_bar_ms: int
    issued_at: float
    latency_ms: int
    usage: Mapping[str, int]    # provider's own counts, never estimated
    arm: str = "primary"        # "primary" | "shadow_model"

@dataclass
class Arm:
    """One per SIGNAL, not per position (§2). Lives as long as the signal."""
    signal_id: str; symbol: str; opened_at: float
    calls_made: int = 0
    last_call_at: float = 0.0
    last_bar_evaluated_ms: int = 0
    standing: Optional[Verdict] = None
    refusals: Dict[str, int] = field(default_factory=dict)
```

And the loop, in outline — note where the budget is spent and what is never awaited:

```python
async def sweep(store, *, now_ts=None) -> Dict[str, Any]:
    """Advance every armed SIGNAL by at most one bar. Never blocks."""
    if not measure_enabled():
        return _refuse_all("disabled")
    if _kill_switch_engaged():
        return _refuse_all("kill_switch")          # acting is what a kill switch stops

    _drain_verdicts(now_ts)                        # apply what arrived since last tick

    positions = position_state.index_open_positions()
    if positions is None:
        return _refuse_all("index_cold")           # cannot answer; not a Firestore fallback

    for arm in _arms_owed_a_decision(positions):
        if not _spend_budget(arm):                 # AT THE TOP, per signal EXAMINED
            _refuse(arm, "budget_exhausted")
            continue
        bar = _current_closed_bar(arm)
        if bar is None or bar == arm.last_bar_evaluated_ms:
            continue                               # not a refusal: nothing new closed
        trigger = _trigger_ladder(arm, bar)
        if trigger is None:
            continue
        arm.last_bar_evaluated_ms = bar
        _pending.append((arm, _build_snapshot(arm, bar), trigger))

    for batch in _batched(_pending):
        asyncio.create_task(_evaluate(batch))      # fire-and-forget; result lands on the queue
    return _health()
```

`_drain_verdicts` runs **first**, so a verdict is applied on the tick after it
arrives against state read fresh in that same tick — and anything older than
`AI_GOV_VERDICT_MAX_AGE_SEC` is refused there rather than applied.

---

## 7. The invariants — in code, not in the prompt

The model's output is **untrusted**. Every one of these is asserted on the apply
path and each violation is a named, counted refusal:

| Invariant | Why |
|---|---|
| TP may move **nearer only** | the arm the record can actually decide (§8); moving a target further away is a new trade, not an adjustment |
| SL may move **tighter only** | widening a stop on a live position is unbounded loss and is what the naked-position invariant exists near |
| No verdict may leave a position without a stop | B18 / `CLAUDE.md` hard limit, no exceptions |
| `choice` must be a key from **that position's own menu** | a key from another position's menu is a parse-level cross-wire |
| The verdict's `as_of_bar_ms` must match the bar still current | prevents applying a verdict computed on a bar the market has left |
| Kill switch engaged → no action, existing protection untouched | re-parking is *acting*; withdrawing protection is the opposite of what a kill switch is for (`trail_governor.sweep` already reasons exactly this way **[verified]**) |
| Provider unreachable / malformed / timeout → `MAINTAIN` | fail-open in behaviour, **counted** via `fail_open.record` — never silent |
| An unavailable AI never changes an exit | the whole system's default is the deterministic FSM |

**Fail-open direction, argued rather than assumed.** `crypto_perp_admission` is
fail-**closed** because its input is the whole exchange; this governor is
fail-**open** because its input is a measurement lane and a fail-closed governor
would freeze exits the moment a provider had a bad minute. The cost of fail-open is
that an inert governor reads exactly like a working one — which is why
`unknown_frac` and the blindness rate are columns, and why total blindness pages the
watchdog in either mode.

**Prompt injection.** The snapshot is engine-computed numbers, and it stays that
way: **no news text, no social text, no user-supplied string enters this prompt.**
The MacroWatchdog already pulls news through `src/openai_evaluator.py`
**[verified]**; that lane must not be joined to this one. Free-form external text in
a prompt whose output can close a position is a money-path injection surface, and
the structural defence (menu keys, closed vocabularies, invariants in code) is what
holds if it is ever breached anyway.

---

## 8. The four actions — and which the record can decide

Owner decision, 2026-09-02: **all four arms ship dark together**, measured in one
window. That is workable, and it carries one caveat that must be on screen from day
one rather than discovered later: **three of the four are decidable from the closed-
signal record and one is not.**

| Action | Decidable? | How |
|---|---|---|
| `MAINTAIN` | **Yes** | the position's actual outcome *is* the answer |
| `ADJUST_TP` | **Yes, fully** | the snap moves TP **nearer only**, so a nearer target was reached iff `MFE ≥ its distance`; all excursion is recorded before the close, so there is no ordering ambiguity (`structural_snap` docstring **[verified]**) |
| `PANIC_CLOSE` | **Yes** | we know where the position actually closed and can walk what it did after the veto point |
| `ADJUST_SL` | **Partly, and the residue is direction-biased** | a *wider* stop on a loser asks whether price would have come back and the walk ended at the stop; a *tighter* stop on a winner asks whether MAE preceded TP1, and MFE/MAE carry no ordering between them **[verified — same docstring]** |

The undecidable SL cases are named separately (ops calls them
`undecidable_truncated` and `undecidable_ordering`) and **never pooled**, because
they remove **opposite ends** of the distribution: dropping them silently leaves a
loss-selected sample on one side and a win-selected one on the other, and a
loss-selected sample is worse than no sample because it looks like an answer.

**There is deliberately no single "did the governor help" number**, and a test will
assert the key does not exist. One figure over all four arms would move with the SL
arm's refusal rate rather than with the mechanism. Per-arm, with decidable fractions
beside every delta — the same call `/signals/structural-snap` and `/signals/sar-live`
already make.

**Two further biases, stated because they are not neutral:**

- **MFE/MAE are updated on mark-price ticks, not intrabar** **[verified]**. Every
  "the level was reached" verdict is therefore conservative: the lane can
  under-count rescues and can never invent one. That points *against* the governor,
  which is the safe direction for an adoption decision.
- **`PANIC_CLOSE` is structurally expensive.** B11: round-trip fees ≈ 0.7% of margin
  at 10×, and a panic close pays **taker** on the exit leg. A wrong veto costs the
  fee *and* the foregone target. Every panic-close row is scored **net of the
  round trip charged to both arms** — charging it to the governor and not to the
  baseline manufactures an edge out of the fee, and charging it to neither hides the
  cost that dominates this book.

**And one population the governor cannot help.** **[verified — `CLAUDE.md`,
2026-09-01]** 39 of 140 matched positions (28%) in the owner's 24 Aug – 1 Sep Binance
history closed at **120–121 minutes**, none by a TP or a stop: they hit
`RECONCILER_MAX_POSITION_AGE_SEC` (7200s **[verified]**). A governor reasoning over a
two-hour horizon is helping a smaller population than the trade count suggests, and
the ledger must split `STALE_EXPIRY` closes out rather than scoring them as the
governor's outcomes.

---

## 9. Provider and cost

### The subscriptions do not apply

**[documented]** A paid **Claude Pro** subscription does not include Claude API
usage; the subscription and the API/Console are separately billed products.
**[documented]** **Google AI Pro / Gemini Advanced** is a consumer chat subscription
(~100 Pro prompts/day in the app); Gemini API usage bills through Google Cloud
Billing, independently.

So neither existing subscription can serve the engine. This needs a new API account,
a new secret in the engine container, and a new billing line — and anything that
*did* work by driving a consumer subscription programmatically would carry no rate
SLA and no pinned model version, which for a measurement ledger is disqualifying
before the terms of service are even reached.

### Cost, at the design volume of §2

~120 calls/day × ~1,300 input / ~150 output tokens = ~4.68M input / 0.54M output per
month **[inferred from §2 and the prompt shape in §5]**. At published list rates
**[documented, read 2026-09-02]**:

| Model | In / Out per MTok | Est. $/month |
|---|---|---|
| Gemini 2.5 Flash-Lite | $0.10 / $0.40 | **$0.68** |
| Gemini 2.5 Flash | $0.30 / $2.50 | **$2.75** |
| Gemini 3.7 Flash | $0.75 / $3.75 *(promo to 31 Dec 2026, then $1.50/$7.50)* | **$5.54** → $11.07 |
| Claude Haiku 4.5 | $1 / $5 | **$7.38** |
| Gemini 2.5 Pro | $1.25 / $10 | **$11.25** |
| Claude Sonnet 5 | $2 / $10 | **$14.76** |
| Gemini 3.1 Pro Preview | $2 / $12 | **$15.84** |
| Claude Opus 5 | $5 / $25 | **$36.90** |

The whole spread is **$0.68 to $37/month**. At ₹2,000/mo (~$23) that is **one Auto
subscriber at every tier except Opus 5, which needs two** — and at the 1,000-member
target the most expensive row on that table is under 0.2% of revenue.
For contrast, the per-position design of §2 at 1,000 members is **~$82,000/month on
the cheapest model on that table**.

**So price does not decide this.** Gate correctly and buy the better model; the
expensive mistake is a wrong `PANIC_CLOSE`, not a token rate.

Prompt caching is worth wiring and not worth optimising: at ~5 calls/hour a 5-minute
cache mostly misses and a 1-hour cache saves roughly half the static prefix
**[inferred from the published cache multipliers and the call rate]**.

### The decision, and how it gets revisited

Three things actually differ for this use case:

1. **Model-version stability — decisive.** This lane is a ledger an adoption
   decision reads over months. A silent model change redefines every row and arrives
   with no diff in our repo: the additive-vs-redefining schema problem with the
   redefinition coming from the vendor. Anthropic publishes dated snapshots and a
   formal deprecation page **[documented]**.
2. **Data terms.** Gemini's free tier states content is used to improve Google's
   products; the paid tier opts out **[documented]**. The prompt carries
   `setup_class`, entry geometry and gate provenance — the proprietary part of the
   engine — so **the free tier is disqualified for the real prompt**, which removes
   Gemini's most attractive property (a zero-cost shadow window).
3. **Latency and region.** Near-irrelevant here: the loop is fire-and-forget on a
   bar clock (§6) and a 2–5s round trip is absorbed by queue-and-apply-next-tick.
   Do not let it decide anything.

**Ship one provider**, behind `src/llm_client.py`, with the exact model string
stamped in every ledger row. Two vendors on day one is two secrets, two rate-limit
behaviours, two deprecation calendars and two failure modes in the lane whose entire
job is to be trustworthy.

**Start on Claude Sonnet 5** ($14.76/mo at design volume) — version stability, no
free-tier data ambiguity, and it is the tier where being wrong costs a market-order
round trip. This also matches `LLM_SIGNAL_CRITIC_BRIDGE`'s existing choice
(`ANTHROPIC_API_KEY`, `claude-opus-4-8` **[verified]**), so one secret and one client
serve both lanes.

**Then settle it with data.** Because the lane is dark and the volume is tiny, run a
**dual-model arm** on a sampled subset: stamp a second model's verdict against the
*same* snapshot, in its own column, **never blended** — the two-arms pattern
`sar_live_shadow` and `structural_snap` already use. Total ≈ $18/month, and the
window ends with a measured verdict-agreement rate instead of an argument. If the
cheap model agrees on routine triage, downgrade tier 1 and keep the strong model for
`PANIC_CLOSE` escalation only. **That is a measurable decision, so it is made from
the ledger, not from this document.**

### Secret handling

`ANTHROPIC_API_KEY` is treated exactly as the Binance secret is: deploy-injected,
**never logged at any level, never written to disk, never surfaced in an error or a
traceback** (`OWNER_BRIEF` §1.4). The client scrubs it from every exception path, and
a test asserts the key never appears in a rendered error.

---

## 10. Measurement — the ledger and the ops surface

### Determinism, and what to do about not having it

`temperature = 0` does not make an LLM deterministic. So:

- **Every row stamps the exact model version string, the prompt hash, and
  `PROMPT_SCHEMA`.** A model change is then visible as a population split rather
  than as a drift nobody can see.
- **The snapshot is stored with the verdict.** A row that cannot be re-scored from
  its own contents is not evidence.
- **`ADDITIVE_FROM_SCHEMAS` is a required argument** to the loader
  (`src/ledger_schema.py:61` **[verified]**), so this ledger cannot inherit the bare
  `!=` loader that overwrote 371 SAR rows on a deploy. A schema bump must state
  which older schemas it reads; `frozenset()` is a valid answer somebody chose.
- **`load()` exists and `get_ledger()` calls it**, and `flush(force=True)` has a
  caller in `main.py`. Flush without load is worse than neither: it *deletes* the
  window on every deploy while the page reports a healthy ledger. Both are pinned by
  the derived guards this repo already runs.

### Two arms, never blended

Every row records the actual outcome **and** the counterfactual the position would
have produced untouched. `MAINTAIN` rows are recorded too — a lane that logs only
interventions cannot compute a baseline and will look brilliant.

The join is to `signal_performance.json`, which `trade_monitor` already writes
correctly at the terminal transition **[verified]** — including #848's
`original_sl_distance` denominator. **Do not build a resolver.** Every forward-
measurement arm in this repo that grew its own cost a session to
`INSUFFICIENT` rows, stalled arms, stale anchors, over-walked series and undatable
windows; `entry_features` is the pattern that avoided all of it by joining outcomes
somebody else owns.

### Ops — `/signals/ai-governor` (360ce-ops, same PR)

Dark work must be observable, and *"a panel that renders perfectly on a page nobody
can reach is exactly as useful as no panel"* — so the page ships **in the nav**, with
its own `active` key, in the same change. Contents:

- **Lane state first**, graded on the **engine's** stamps, never on ops' clock:
  `not_reported` / `unreachable` / `empty` / `measuring` / `enforcing`.
- **Verdict mix** — including `MAINTAIN` and every refusal by name
  (`budget_exhausted`, `stale_verdict`, `unknown_choice`, `index_cold`,
  `provider_error`, `kill_switch`). A silence is never a state.
- **Per-arm deltas with decidable fractions beside them**, and no combined figure.
- **Blindness** — `unknown_frac` for book and flow, per §3.
- **Cost** — `spend_today_usd`, calls/day, tokens, and the version-stamped rate table
  the money was computed with, so a provider price change cannot rewrite history.
- **Latency** — p50/p95 round trip, and the count of verdicts that arrived too late
  to apply. That number is the honest measure of whether the clock in §4 is right.
- **Rationales**, labelled as *the model's stated reason*, never as the cause.

### Liveness

A `RateProbe` (verdicts vs triggers fired) and a `PredicateProbe` (the lane is
blind on essentially its whole population). **A non-failure must never reach
`fail_open`** — a probe signalling "idle" or "disabled" returns `True, "…"` rather
than raising, or it fills the counter whose whole purpose is making a real failure
stand out.

### Telemetry to the owner

The one-sentence rationale goes out on **FCM push and/or the Telegram mirror** —
alerting is read-only, so both are acceptable paths; **control stays ops-only** for
the audit trail (`CLAUDE.md § Delivery surfaces` **[verified]**).

**It does not go to subscribers.** A model-authored explanation of why a user's
position was closed is (a) not evidence, and (b) squarely into the B16 framing
problem — the paid feature is *automation software functionality*, not advice, and
that framing is load-bearing for Play policy and Indian regulatory exposure. Owner
call if it ever changes; the default is no.

---

## 11. Rollout — and the window this actually needs

Money-path, so dark-flag-first with **two** flags, per `CLAUDE.md § Project Phase`:
the **measurement** ships **ON** and visible in ops from day one; the
**user-visible effect** ships **OFF** and is activated only after owner sign-off on
the measured result. A measurement shipped default-OFF produces an empty panel and a
decision that keeps getting deferred — that is what happened to the SAR exit arm on
2026-07-25 and it is not repeated here.

| Phase | Ships | Gate |
|---|---|---|
| **P0** | `llm_client` + snapshot + menu builder + ledger + ops page + probes. **No calls.** Menus are built and stamped so we can see what the model *would* have been offered. | ships normally (off money path) |
| **P1** | Calls live, verdicts recorded, **nothing applied**. Both flags: `AI_GOV_MEASURE_ENABLED=true`, `AI_GOV_APPLY_ENABLED=false`. Dual-model arm sampled (§9). | armed by the owner after one watched cycle |
| **P2** | Ops verdict surface complete: per-arm deltas, decidable fractions, cost, latency, blindness. | telemetry, ships normally |
| **P3** | **Activate one arm** — `ADJUST_TP` first, being the only fully decidable one — for the owner's account only, then subscribers. | **owner sign-off**, against §11.1 |
| **P4** | Harvest: distil a consistently-winning pattern into a **deterministic rule** in the evaluator/geometry code. | dark-first + owner sign-off |

**P4 is the point, not an afterthought.** Inherited verbatim from
`LLM_SIGNAL_CRITIC_BRIDGE` §5: the governor is a hypothesis generator, and the
engine's job is to apply what it finds *deterministically* — fast, free,
reproducible, measurable. Its unique contribution shrinking over time is success,
not obsolescence. A permanent per-signal LLM oracle on the money path is the
scaffold this repo bans.

### 11.1 How long P1 actually takes — say it now

`docs/STATISTICAL_CHANGE_POLICY.md` rule 1 **[verified]**: no exit change goes live
unless the supporting window has **≥ 200 closed signals in the affected cohort AND
spans ≥ 21 days**, whichever is later. Wilson bounds do not exempt a decision.

The affected cohort here is **rows the governor acted on**, not all delivered
signals — a `MAINTAIN` row tests nothing about intervention.

**[inferred]** at ~16 delivered signals/day and an intervention rate of *r*:

| Intervention rate | Acted-on rows/day | Days to 200 |
|---|---|---|
| 40% | ~6.4 | **~31 days** |
| 20% | ~3.2 | **~63 days** |
| 10% | ~1.6 | **~125 days** |

So P1 is a **one-to-four-month** window, and it is longer still per arm, because 200
rows of `ADJUST_TP` and 200 of `PANIC_CLOSE` accumulate independently.

**And `PANIC_CLOSE` may never reach the bar.** A macro veto is rare by construction;
at any plausible rate, 200 panic-close rows is a year. That forces an explicit
choice and it is the owner's, not mine:

- **(a)** never activate that arm — keep it permanently shadow, as a page the owner
  reads and acts on manually; or
- **(b)** activate it on a smaller window under the policy's own override clause,
  with the override and its rationale recorded in `ACTIVE_CONTEXT.md`.

There is no third option that respects the policy. Recording this now is cheaper
than discovering it in month three.

**Rule 3 also binds:** one change-set per window. A governor P1 window running
concurrently with another exit change destroys attribution for both. Queue them.

---

## 12. Config (all new)

```
AI_GOV_MEASURE_ENABLED        bool   default TRUE   # measurement flag — ON when it ships
AI_GOV_APPLY_ENABLED          bool   default FALSE  # user-visible effect — owner sign-off to arm
AI_GOV_ARMS_ENABLED           str    default "tp"   # comma set of arms allowed to APPLY: tp,sl,panic
AI_GOV_PROVIDER               str    default "anthropic"
AI_GOV_MODEL                  str    default "claude-sonnet-5"   # exact version, stamped per row
AI_GOV_MODEL_SHADOW           str    default ""     # dual-model arm; "" = off
AI_GOV_SHADOW_SAMPLE_PCT      int    default 25
AI_GOV_MAX_CALLS_PER_SIGNAL   int    default 8      # lifetime, per signal
AI_GOV_MAX_CALLS_PER_HOUR     int    default 30     # global rolling
AI_GOV_MAX_USD_PER_DAY        float  default 0      # 0 = unset; see below
AI_GOV_VERDICT_MAX_AGE_SEC    float  default 10.0   # older than one tick → refused
AI_GOV_REQUEST_TIMEOUT_SEC    float  default 20.0
AI_GOV_MIN_SECONDS_BETWEEN    float  default 300.0  # per-signal cooldown floor
ANTHROPIC_API_KEY             secret deploy-injected; never logged (OWNER_BRIEF §1.4)
```

**`AI_GOV_MAX_USD_PER_DAY` is deliberately unset at ship**, and P0/P1 run on the
call-count bounds alone. The number comes from the **first week of the ledger** —
measured calls/day × measured $/call × 3 headroom — not from this document.
Inventing it now is the `_HEARTBEAT_MAX_AGE_SECONDS` mistake: a constant asserting a
property nobody measured, checkable in one command, which cost a day of restarts.

Shape the cap like the Firestore allowance the owner just chose: **it converts a
bill into a degradation, not a charge.** Past the cap the governor returns
`MAINTAIN`, counted and named on the panel.

`AI_GOV_ARMS_ENABLED` is a **choices-validated** tunable
(`runtime_tunables.Tunable.choices`, which renders a `<select>` in ops), and the
sweep refuses and counts an unrecognised value rather than going silently inert.
That is the exact defect `TRAIL_GOVERNOR_TIMEFRAME` shipped with — free text, owner
typed `5` instead of `5m`, governor permanently inert with the switch reading ON —
and the write path refusing while the read path kept serving a bad stored value.

---

## 13. Testing

Beyond the ordinary unit coverage, these are the tests that would have caught this
repo's actual defects, so they are not optional:

- **Budget bounds the do-nothing path.** A test drives a sweep where the pre-filter
  fires on nothing and asserts the per-signal budget still decremented. Session
  137's bound passed its own test because that test only exercised the branch that
  did work.
- **Verdict schema round-trip against the REAL client.** Never hand-write the
  provider's response shape in a fixture — a mock whose keys you chose asserts your
  assumption back at you and goes green over dead code (`classify_pending` /
  `zone_distance_atr`, twice). Record one real response and replay it; no live calls
  in CI.
- **The menu is closed.** A verdict naming a key not in that position's menu is
  refused and counted; a verdict naming *another* position's key is refused.
- **Monotonicity.** Property tests over both sides: a TP that moves further, or an SL
  that widens, is always refused.
- **Naked-position invariant.** No apply path can leave a position without a resting
  stop, asserted for every arm.
- **Staleness.** A verdict older than `AI_GOV_VERDICT_MAX_AGE_SEC` is refused, and
  the refusal is counted rather than logged.
- **No combined figure.** Assert the ledger and the ops reducer expose **no** blended
  across-arm metric — the key must not exist.
- **Ledger round trip through the real serializer**, including `load()` after
  `flush()`, with a schema-2 file read by a schema-1-additive loader. `open_time` not
  surviving `_save_snapshot_sync` is why this is a named test and not a assumption.
- **The flush caller exists.** Derived guard: a module with `get_ledger()` and
  `flush()` must have a caller in `main.py`, must define `load()`, and `get_ledger()`
  must **call** it. *Defining a method is not calling it.*
- **The secret never renders.** Force every error path and assert the key does not
  appear in the message, the traceback, or the ops payload.
- **`ruff` before believing a green suite.** A missing import inside a route body the
  suite never enters is `F821` and invisible to 8,900 passing tests.

---

## 14. What this program will not claim

- **It will not claim the governor works because the model's rationales read well.**
  A rationale is prose the model produced, not evidence about the market.
- **It will not present a counterfactual R as an expected live result.** Measured at
  ~0.38R optimism on MOVER_TREND_PULLBACK **[verified]**.
- **It will not quote a verdict on a window shorter than §11.1**, nor declare the
  loop healthy from a window shorter than the period of the thing being judged —
  two "it is fixed" claims died within hours on 2026-08-19 for exactly that.
- **It will not blend the arms, the fills, or the two models.**
- **It will not fill the unarmed population with a guess.** A signal the governor
  could not evaluate (no book, no flow, provider down) is a fact about
  **deployability**, not a gap to impute — and imputing it would flatter the
  mechanism, because the blind population is the one where the mechanism could not
  have run live either.
- **It will not read the LLM's confidence as a probability.** It is a number the
  model emitted; if it turns out to correlate with outcomes, that is a finding the
  ledger produces, not an assumption the design makes.

---

## 15. Open questions for the owner

These are decisions, not unknowns — each needs an answer before the phase it gates:

1. **§11.1(a) or (b) for `PANIC_CLOSE`** — permanently shadow, or activated on a
   short window under a recorded policy override? *Gates P3.*
2. **Does the depth/aggTrade universe get widened** to cover the mover book
   (`docs/PRICE_ACTION_PROGRAM.md` §4 stream budget)? Without it, a large share of
   governed signals are book-blind and flow-blind. *Gates how much §3's blindness
   rate matters.* Out of scope for this document either way.
3. **Is there an appetite for the deterministic P4 harvest**, or is a standing LLM
   in the loop the intended end state? The doctrine says the former; the brief reads
   like the latter. *Gates whether P4 is the goal or a nice-to-have.*
4. **`AI_GOV_MAX_USD_PER_DAY`** — set from the first week's ledger (§12), confirmed
   by the owner then.

---

## 16. Sources

**In-repo [verified]:** `config/__init__.py` (concurrency caps, poll interval,
depth/aggTrade caps, reconciler age); `src/execution/trail_governor.py` (`decide`,
`_park`, `sweep`, refusal vocabulary); `src/execution/signal_dispatch.py`
(`dispatch_signal_to_active_users`, `close_fsm_positions_for_signal`);
`src/execution/position_state.py` (`index_open_positions`); `src/trade_monitor.py`
(monitor loop, lane sweeps, pricing freshness); `src/structural_snap.py`
(decidability of the two arms, refusal names); `src/entry_features.py`
(`cvd_slope_aligned`, `book_imbalance_aligned`); `src/market_context.py`;
`src/depth_book.py`; `src/ledger_schema.py`; `src/feature_liveness.py`;
`src/diag_catalog.py`; `src/openai_evaluator.py`; `OWNER_BRIEF.md`;
`CLAUDE.md`; `docs/LLM_SIGNAL_CRITIC_BRIDGE.md`;
`docs/STATISTICAL_CHANGE_POLICY.md`.

**Vendor [documented], read 2026-09-02:**
- Anthropic — subscription vs API billing: https://support.claude.com/en/articles/9876003-i-have-a-paid-claude-subscription-pro-max-team-or-enterprise-plans-why-do-i-have-to-pay-separately-to-use-the-claude-api-and-console
- Claude API pricing: https://platform.claude.com/docs/en/about-claude/pricing
- Gemini API pricing: https://ai.google.dev/gemini-api/docs/pricing
- Google AI plans: https://ai.google.dev/gemini-api/docs/google-ai-plans
- Gemini API billing: https://ai.google.dev/gemini-api/docs/billing

Prices and free-tier terms change. Re-read both pricing pages before quoting a
figure, and treat §9's table as of its date rather than as a constant.
