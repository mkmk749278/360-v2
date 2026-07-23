# LLM Signal Critic Bridge — Implementation Doc

**Status:** Design of record. Not yet implemented.
**Author:** CTE session, 2026-07-22.
**Companion:** `docs/AUTONOMOUS_SYSTEM_AUDIT_AND_REMEDIATION.md` (the net-edge programme this plugs into).

> **One line:** the engine generates a signal; an LLM critic reviews it *in shadow*,
> proposes adjusted geometry, and that proposal is **forward-measured net-of-cost
> against the engine's own geometry** — exactly like our shadow strategies and
> geometry A/B. The LLM never edits a live signal. Consistent, measured wins get
> promoted into **deterministic rules**. Opinion earns its place in the ledger, or
> it doesn't ship.

---

## 1. Why this shape (and not inline editing)

The owner's instinct — "the system generates signals, you review and fix the
geometry before it posts" — is correct that the deterministic evaluators miss
contextual judgment (a real HANAUSDT example: shorting into coil *support* instead
of into resistance; a squeeze-vulnerable stop; thin-book slippage the flat cost
model understates). But putting an LLM **inline in the dispatch path** is the wrong
mechanism, for four reasons that are structural, not fixable by prompt:

1. **Latency vs decay.** Signals are scalps (5–60 min, precise entry prices). An LLM
   round-trip (fetch data → reason → respond) is seconds to tens of seconds; the
   price moves while it thinks. Posting a reviewed entry *is* the `dispatch_staleness`
   leak we already measured at −0.63R. Inline review **manufactures** staleness.
2. **Non-determinism kills measurement.** We just spent the cost-model programme
   making every decision measurable. An LLM-edited geometry differs run-to-run and
   can't be cleanly forward-measured against a counterfactual. Inline opinion undoes
   the rigor.
3. **Symptoms, not root cause.** The gaps (entry-into-support, thin-book slippage,
   BE-bleed) are *systematic*. The production-grade fix is to fix the geometry/cost
   logic **once**, deterministically, so all 75 pairs benefit — not to hand-babysit
   each signal forever. Per-signal LLM edits are a scaffold, and scaffolds are banned.
4. **Trust + cost on the money path.** An LLM silently altering a live auto-trade
   signal (one hallucinated stop = real loss) is a safety surface; per-signal
   inference 24/7 is a recurring cost.

**Therefore:** the LLM is a **measured shadow-critic and hypothesis generator**, not
an inline editor. It proposes; the ledger judges; deterministic rules harvest the
wins. Its contributions are subject to the exact same net-of-cost forward
measurement as everything else in the autonomous stack.

---

## 2. Architecture

```
Scanner generates candidate ──► (unchanged) live gate chain / scoring / dispatch
        │
        │ stamp (O(1), hot-path-safe: id + geometry + context only)
        ▼
  llm_critic queue  ──(async, off the event loop, BATCHED)──►  Anthropic Batch API
        │                                                         (claude-opus-4-8)
        │  structured critique + adjusted geometry (JSON schema)
        ▼
  suppression_audit / geometry-style forward measurement
        │  net-of-cost R for BOTH arms: engine-geometry vs LLM-geometry
        ▼
  strategy_edge matrix  ──►  truth report: "LLM-geometry ΔR vs engine-geometry"
        │
        ▼  (only when a pattern wins consistently, net, past sample floor)
  promote to a DETERMINISTIC rule in the evaluator/geometry code (dark-first + sign-off)
```

**Placement in the module map** (all new, additive):

| Concern | File |
|---|---|
| Critic client + prompt + structured schema | `src/llm_signal_critic.py` (new) |
| Critique record store + forward measurement | reuse `src/suppression_audit.py` + `src/geometry_ab.py` patterns |
| Batch submit/collect loop | wired in `src/main.py` on the existing 5-min audit cadence |
| Config / flags | `config/__init__.py` |
| Liveness probe | `src/feature_liveness.py` (a critic-output-vs-signal-rate probe) |

**Hot-path safety (Cost Discipline).** The scanner only does an **O(1) stamp** (append
signal id + geometry + context key to a bounded deque) — no network, no LLM call on
the scan loop. The LLM calls happen on the periodic audit thread, off the event loop,
in **batches**. This mirrors `suppression_audit`'s stamp/classify split exactly.

---

## 3. The critic contract

### Inputs (per stamped signal)
- Setup class, side, engine geometry (entry / SL / TP1 / TP2), confidence, market
  context key (session / phase / volatility / rotation), regime, `pair_cohort`
  (liquidity tier).
- Real structural data for the pair: recent OHLCV (multi-TF), order-flow summary
  (CVD/delta if available), funding, OI, nearest structure levels, 24h range, and
  **liquidity/volume** (so it can flag thin-book pairs like HANA).

### Output — **structured** (`output_config.format`, JSON schema, `strict`)
```json
{
  "verdict": "AGREE | ADJUST | VETO",
  "direction_agrees": true,
  "adjusted_entry": 0.0,
  "adjusted_sl": 0.0,
  "adjusted_tp1": 0.0,
  "adjusted_tp2": 0.0,
  "confidence": 0.0,
  "liquidity_flag": "OK | THIN | ILLIQUID",
  "rationale": "one paragraph, structural, no hedging"
}
```
Structured output guarantees a parseable proposal every time (no free-text parsing).
`VETO` is a *proposal to suppress*, measured like any other — never a live block.

### Model, thinking, cost controls
- **Model:** `claude-opus-4-8` (default; best structural judgment). **Owner cost
  lever:** `claude-haiku-4-5` ($1/$5 per 1M vs $5/$25) if per-signal cost needs
  cutting — decided by config, not code.
- **Adaptive thinking** (`thinking:{type:"adaptive"}`, `effort:"high"`) for the
  structure read.
- **Prompt caching** on the stable prefix — the doctrine/system prompt (how to read
  structure, the strategy catalog, the cost model, the output contract) is large and
  frozen, so it caches at ~0.1× read cost; only the per-signal candles/geometry vary
  after the cache breakpoint. This is the single biggest cost lever.
- **Batch API** (`client.messages.batches`) — the critic is **not latency-sensitive**
  (outcomes are forward-measured over a 60-min window regardless), so batching buys a
  flat **50% discount** and fits the periodic cadence. Real-time single calls are the
  fallback only if we ever want interactive critique.

**Cost envelope (estimate).** With the doctrine prefix cached and requests batched:
per-signal ≈ (small uncached candle/geometry input + ~500 output tokens). At current
emission volume (dozens/day) this is cents/day; even at 10× emission it stays well
under any hot-path concern. Recomputed precisely once the prefix token count is
known. Secret handling: `ANTHROPIC_API_KEY` injected via deploy secrets like
`OPENAI`/`NOWPAYMENTS` keys — **never logged, never in errors** (mirrors the Binance
secret hard-limit).

---

## 4. Measurement (the whole point)

For every critiqued signal we stamp a **counterfactual pair**, identical to the
stop-geometry A/B design (`geometry_ab.py`):

- **Arm A — engine geometry** (entry/SL/TP as the engine posted).
- **Arm B — LLM-adjusted geometry** (the critic's proposal).

Both arms are forward-measured on the same real candles, **net of costs** (the W1
cost model — per-liquidity-tier slippage matters most here, since the critic's edge
is largely on thin pairs). Results land in the `strategy_edge` matrix as
`X@ENGINE` / `X@LLM` shadow rows and surface in the truth report:

> **per strategy × context: LLM-geometry net-R − engine-geometry net-R (ΔR), with n.**

Plus a **VETO scorecard**: of the signals the critic wanted to suppress, what did
they actually do net (WOULD_WIN / WOULD_LOSE)? — the same suppression-audit verdict
math, answering "is the critic's judgment net-positive or is it just opinion?"

A `feature_liveness` probe pages if the critic silently stops producing (output rate
vs signal rate), per the no-silent-flatline convention.

---

## 5. The promotion loop (opinion → deterministic rule)

The critic is a **hypothesis generator**, not a permanent oracle. When the ledger
shows the critic *consistently* wins on a specific, describable pattern (past the
sample floor, net-of-cost, across a real window), we:

1. **Extract the rule** the critic is effectively applying (e.g. "don't short into a
   volume-profile support node," "widen the stop beyond the liquidity pool on
   CASCADE," "suppress signals on pairs below $X/24h liquidity").
2. **Encode it deterministically** in the evaluator/geometry/cost code — fast, free,
   reproducible, measurable.
3. **Ship that rule dark-first + owner sign-off** (it's a money-path scoring change).

The LLM's job is to *find* the systematic fixes faster than we'd find them by hand;
the engine's job is to *apply* them deterministically. Over time the critic's unique
contribution shrinks as its wins become rules — which is success, not obsolescence.

---

## 6. Where inline review *could* legitimately live (later, narrow)

Not on fast scalps. Two bounded exceptions worth revisiting only after the shadow
critic proves edge:
- **Slower-timeframe setups** where a 10–30s review doesn't decay the entry.
- **A bounded pre-dispatch VETO gate** (reject-only, never silently edit), for sanity
  checks the rules missed (e.g. "book too thin for this size"). A veto is boundable
  and safe; an inline geometry *editor* on scalps is not.

Both remain out of scope for the initial build.

---

## 7. Rollout (dark-first, measurement-first)

| Phase | Ships | Gate |
|---|---|---|
| P1 | Stamp + batch critic + structured output + **shadow measurement** (no live effect) | `LLM_CRITIC_ENABLED` default OFF; observe-only |
| P2 | Truth-report ΔR + VETO scorecard + liveness probe | telemetry, ships normally |
| P3 | Promote the *first* consistently-winning pattern to a deterministic rule | dark-first + owner sign-off |
| P4 (optional) | Bounded pre-dispatch VETO gate for slow-TF signals | dark-first + owner sign-off |

The critic **never** touches a live signal in P1–P2. It changes live behaviour only
in P3, and only as a *deterministic rule distilled from measured wins* — not as live
LLM inference.

---

## 8. Config (new)

```
LLM_CRITIC_ENABLED            (bool, default false)   # master; OFF = no calls, no stamps consumed
LLM_CRITIC_MODEL              (str,  default "claude-opus-4-8")   # owner cost lever → "claude-haiku-4-5"
LLM_CRITIC_USE_BATCH          (bool, default true)    # 50% cost; single-call fallback if false
LLM_CRITIC_MAX_PER_CYCLE      (int,  default 50)       # blast radius on spend per audit cycle
LLM_CRITIC_EFFORT             (str,  default "high")
ANTHROPIC_API_KEY             (secret, deploy-injected; never logged)
```

## 9. Testing

- **Pure critique parser / schema round-trip** — structured output → typed record,
  fail-open on malformed (never breaks the audit loop).
- **Stamp is O(1) / no I/O** (mirrors `test` for suppression stamp).
- **Forward-measurement pairing** — engine-arm vs LLM-arm net-R, geometry-A/B-style
  tests with the `numpy_seeded_store` fixture.
- **VETO scorecard math** — reuse suppression-audit verdict tests.
- **Cost-model integration** — LLM-arm R is netted per liquidity tier (the thin-pair
  case is the point).
- **API client is mocked** in tests (no live Anthropic calls in CI); a single
  contract test asserts the request shape (cache breakpoint on the doctrine prefix,
  structured-output format present, batch envelope).

## 10. Doctrine compliance

- **No inline money-path LLM edits.** The critic is shadow-only through P2; P3 ships
  deterministic rules, dark-first + sign-off.
- **Cost Discipline.** Hot path does an O(1) stamp only; all inference is off-loop,
  batched, prefix-cached, and blast-radius-capped per cycle.
- **Secret handling.** `ANTHROPIC_API_KEY` treated like the Binance secret — never
  logged, written, or surfaced in errors.
- **No scaffolds.** The bridge ships wired end-to-end (stamp → critique → measure →
  surface); it is not "store a critique and use it later." Its *output is measurement*
  from day one.
- **Measured, not assumed.** Even the CTE's own structural reads must earn their place
  in the ledger — same bar the cost-model programme just imposed on the engine.
