# Plan — Fully Autonomous, Context-Adaptive Best-Signal Emission

*Author: CTE · Date: 2026-07-19 · Status: BUILT + LIVE (owner directive) — §7 decisions taken by CTE; controls in ops.*

> **Goal (owner, verbatim):** a fully autonomous best-signals emitting system that
> dynamically adjusts based on the Strategy Lab data.

> **Owner directive (2026-07-19), verbatim:** *"no darks make it live but give
> controls in ops."*  So this ships **applying, not dark**, with every knob exposed
> as a runtime tunable on the ops Control page.  CTE flag on the doctrine trade-off:
> this overrides the production dark-flag-first rule for a money-path (emission)
> change — real subscribers see the changed signal set immediately, without a shadow
> window first.  It is accepted because (a) the owner explicitly directed it, (b) it
> is an **emission** change only — no execution / sizing / blast-radius behaviour is
> touched, so no capital-safety limit is relaxed, and (c) the full safety envelope
> stays enforced in the math and is instantly reversible from ops (`context_emission_enabled`
> OFF → pre-policy behaviour, applied ≤5s, no redeploy).  The relax side is the only
> part that changes what paid users see; it is bounded by the quality anchor and a
> sample floor and starts conservative (anchor 60, STRONG→60 / POSITIVE→62).

This document is the engineering plan to get there. It is grounded in the
2026-07-19 Strategy Lab + Profit-tab read (see *Evidence* below) and the code as
it stands at `main` HEAD.

---

## 1. The one-sentence design

Turn the **single, context-blind confidence floor** that decides emission today
into a **per-`(strategy × context)` policy driven live by the Layer-C edge
matrix**, bounded by the Layer-E safety envelope, so every path emits its
**outcome-proven** best setups in the contexts where it wins and stays silent
where it loses — continuously, autonomously, with the owner arming the mechanism
once and the kill-switch/blast-caps bounding it forever after.

We are not building a new measurement system. **The measurement system already
exists and is running** (Layers A–E, Session 53, PR #720). We are wiring its
output into the emission decision — the step deliberately deferred as "Phase 4
master-arm."

---

## 2. Why this is the right design (the evidence)

### 2.1 The bottleneck is one global gate, not the market

7-day / edge-matrix window, per-strategy rollup (Strategy Lab p97–99):

| Strategy | candidates | **emitted** | emit % | best measured cell |
|---|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | 6,698 | 17 | 0.25% | NY/MARKDOWN/EXPANDED **+1.24R** |
| SR_FLIP_RETEST | 4,790 | 1 | 0.02% | LONDON/VOL_EXP/CASCADE **+1.29R** |
| FAILED_AUCTION_RECLAIM | 3,893 | 9 | 0.23% | LONDON/MARKDOWN/EXPANDED **+1.70R** |
| DIVERGENCE_CONTINUATION | 2,540 | 4 | 0.16% | NY/ACCUM/NORMAL **+1.22R** |
| QUIET_COMPRESSION_BREAK | 1,055 | **0** | 0% | OVERLAP/QUIET/COMPRESSED **+2.21R** |
| LIQUIDITY_SWEEP_REVERSAL | 1,035 | 1 | 0.10% | ASIA/ACCUM/NORMAL **+1.53R** |
| FUNDING_EXTREME_SIGNAL | 106 | **0** | 0% | ASIA/ACCUM/NORMAL **+1.24R** |
| MEAN_REVERT (18th) | 172 | **0** | 0% | ASIA/RANGE/NORMAL +0.15R |

≈42 signals emitted across **all** paths; MTP+FAR = 62% of them. Every path is
detecting hundreds–thousands of setups; **≈99.8% die at the gate chain.** The
survivors are dominated by the two paths whose setups the confidence model scores
highest — MTP and FAR — because emission is decided by `sig.confidence < min_conf`
(≈65 + component floors) at `scanner/__init__.py:7604`, and that floor is
**context-blind**. It does not know that a 62-confidence QCB in
OVERLAP/QUIET/COMPRESSED has a measured **+2.21R** edge (the strongest cell in the
matrix) while an 80-confidence MTP in VOLATILE loses money.

**The edge lives in `(session × regime × path)` cells. The emission decision only
reads a global score. That is the whole problem.**

### 2.2 The gate audit prices the leak (Strategy Lab p99)

| Gate | suppressed | would-win % | saved R | missed R | EV/supp | verdict |
|---|---:|---:|---:|---:|---:|---|
| **dispatch_cooldown** | 312 | **100%** | 0 | **235.1** | −0.75 | **DROP** |
| min_confidence | 1,733 | 34.4% | 598 | **797.0** | −0.11 | TUNE |
| level_still_in_play | 1,832 | 16.3% | 187 | 171.9 | +0.01 | TUNE |
| dispatch_staleness | 526 | 20.9% | 355 | 99 | +0.49 | **KEEP** |
| quiet_scalp_block | 266 | 7.1% | 34 | 25 | +0.03 | TUNE |

`dispatch_staleness` earns its keep. `dispatch_cooldown` is a **pure loss** — every
blocked candidate would have won, 235R gone. `min_confidence` is **net-negative** —
blocks 797R of winners to save 598R. These are the levers the context policy pulls.

### 2.3 The machinery to fix it is built and idle

- **Layer C** (`strategy_edge.py`) measures every strategy per context, Wilson-bounded,
  `emitted/suppressed/shadow` split — **in-memory, refreshed on the 5-min loop.**
- **Layer D** (`strategy_allocator.py`) already computes, per context, the
  activate-list (top-N by edge, weight-capped) and demote-list (NEGATIVE cells).
  Mode `RECOMMENDATION_ONLY` — **"consumed by nothing."**
- **Layer E** — caps baked into the recommendation math (`ALLOCATOR_MAX_CONCURRENT_STRATEGIES=6`,
  `ALLOCATOR_MAX_STRATEGY_WEIGHT=0.35`).
- **One consumer exists**: the RANGE_FADE context gate (S67) — but it is a *one-sided
  filter* (fail-closed; makes a path emit **less**). It is the proof-of-concept for
  reading Layer C live; this plan **generalises and inverts** it into a two-sided policy.

---

## 3. The mechanism: `context_emission_policy`

A new **pure function** — no I/O, O(1) dict lookup against the already-warm edge
store, following the RANGE_FADE cost pattern exactly:

```
effective_floor(strategy, context_key, base_floor, limits) -> (float, reason)

  cell = edge_store.cell(strategy, context_key)          # in-memory
  if cell is None or cell.n < EDGE_SAMPLE_FLOOR:          # cold / thin
      return base_floor, "cold_cell"                     # today's behaviour, unchanged
  match cell.verdict:
      STRONG    -> base_floor - relax(cell.edge_r), "strong:{edge_r}"
      POSITIVE  -> base_floor - relax(cell.edge_r)*0.5,  "positive:{edge_r}"
      NEGATIVE  -> HARD_SUPPRESS, "negative:{edge_r}"     # RANGE_FADE model, proven
      _         -> base_floor, "neutral"
  # relaxation is CLAMPED so effective_floor never drops below QUALITY_ANCHOR
```

At the emission gate, the candidate emits iff `confidence >= effective_floor` (and
contextualised component floors). The floor per path per context is therefore a
**live function of the Strategy Lab data** — exactly "dynamically adjust based on
strategy lab data."

**Two-sided, and that is the point.** RANGE_FADE today only *tightens*. This policy
*relaxes* STRONG cells (so QCB fires its +2.21R cell, SR_FLIP its +1.29R cell) **and**
*suppresses* NEGATIVE cells. Breadth and quality rise together: every additional
signal it lets through is one the matrix has **measured winning in that context.**

### 3.1 The quality-anchor question (owner decision, §7)

`min_confidence = 65` is a **business rule** — the paid B-tier minimum
(`OWNER_BRIEF §2.1a`; sub-65 = "scrap"). We do **not** lower the headline 65 blindly.
Phase 1's shadow must first **attribute the 797R of missed winners** to their real
sub-reason:

- missed because `confidence < 65` (headline) → lowering needs an explicit business
  decision on a **context-proven** minimum (e.g. "≥60 allowed only in a STRONG cell
  with n≥30"), never a blanket drop;
- missed because a **component floor** (`market≥12, execution≥10, risk≥10`) — these
  are structurally biased against non-mover setups and are the safer first lever;
- missed because a **secondary gate** (`dispatch_cooldown`, `quiet_scalp_block`,
  `level_still_in_play`) — tune the gate, not the floor.

The shadow tells us which lever carries the R. We pull the safe ones first.

---

## 4. Guardrails (non-negotiable — from doctrine)

- **Dark-first.** Master flag `CONTEXT_EMISSION_POLICY_ENABLED` default **OFF**. The
  would-be effective floor is **stamped on every candidate** and shadow-measured on a
  real window before it ever changes live output. Activation is an ops tunable +
  owner sign-off (new evaluator/scoring path = owner-sign-off item).
- **Fail-safe direction is asymmetric.** Edge-store error / cold cell → fall back to
  **today's global floor** (never fail toward *more* emission). NEGATIVE-side
  suppression fails **closed** (RANGE_FADE model). Every fail-open path calls
  `fail_open.record(...)` and pages.
- **Quality anchor.** Relaxation is clamped; the effective floor never drops below
  `CONTEXT_EMISSION_QUALITY_ANCHOR`. Sub-anchor never reaches paid users. Paid-tier
  integrity is preserved by construction.
- **Sample floor.** Relaxation only on cells with `n ≥ EDGE_SAMPLE_FLOOR` (15,
  mirrors `STRATEGY_EDGE_*`); STRONG-band relaxation gated higher (owner-tunable).
- **Cost.** In-memory only. Zero new Firestore/network reads on scanner, tick, order,
  or dispatch hot paths (Cost Discipline hard limit). The edge store is already in RAM.
- **Blast radius untouched.** This is **emission** (which signals fire), not execution.
  Sizing caps, naked-position invariant, tripwires, kill-switch, per-user gates all sit
  downstream and are unchanged.
- **Liveness.** New probe: the policy must not silently flat-line. Page if the edge
  store goes stale or the policy stops adjusting (a frozen policy = an unfinished feature).

---

## 5. Phasing (each phase = one PR; dark-first throughout)

**Phase 0 — De-risk + instrument (OFF money path, ships normally, auto-merge-eligible)**
- Make `dispatch_cooldown` and `min_confidence` **live tunables**; fix the
  `dispatch_cooldown` DROP leak (235R, 100% would-win) behind its tunable. Immediate,
  safe emission lift; the deferred S53 follow-up.
- Split `min_confidence` missed-R telemetry by sub-reason (headline vs component vs
  secondary gate) so Phase 1 knows which lever holds the R.
- Fix MEAN_REVERT `REGIME_SETUP_COMPATIBILITY` (#739 / audit F1) so the 18th path can
  enter measurement at all. *(Money-path compat change → dark-first + owner sign-off.)*

**Phase 1 — Shadow the context policy (money-path but DARK, zero live change)**
- New `src/context_emission_policy.py` (pure). Stamp `would_be_effective_floor` +
  `would_emit` on every candidate at the emission gate; shadow-log; new edge-matrix
  stamp `context_floor:<strategy>` so the **gate audit prices this policy's own
  save/miss balance** on real data. Liveness probe. Full test suite. Flag default OFF.

**Phase 2 — Read the window + owner sign-off**
- After a real forward window, read the `context_floor:*` gate-audit rows: does the
  policy lift STRONG cells (missed→would-emit winners) **without** opening NEGATIVE
  cells? Owner signs off (globally, or per verdict-band).

**Phase 3 — Activate the two-sided floor (money-path, owner-signed, tunable)**
- Flip the tunable. Relax STRONG, suppress NEGATIVE, global floor on cold. Instant
  off-switch. **Retire the bespoke RANGE_FADE gate into this unified policy** —
  RANGE_FADE becomes just another matrix-driven strategy; removes the special-case.

**Phase 4 — Allocator drives the portfolio (the master-arm)**
- Layer D goes from `RECOMMENDATION_ONLY` to a live input: the current-context
  activate-list caps the concurrently-promoted strategy set (Layer E), the demote-list
  hard-suppresses, and candidate **priority ranking** (blended confidence × measured
  edge_r) resolves rate-limit / per-scan competition so the **best** signal wins the slot.

**Phase 5 — Pair-cohort dimension (honest "which pairs")**
- Per-symbol cells are far too sparse to ever pass n≥15. Add a **liquidity-tier /
  mover-vs-established cohort** axis to the context key, re-measure, extend the policy.
  This is the tractable form of "which pairs."

**Phase 6 — Steady-state autonomy**
- Cells self-unlock (turn STRONG → more emission) and self-suppress (decay to
  NEGATIVE → less) on each fresh verdict, no human in the loop. Watchdog + kill-switch
  + blast caps bound it. Weekly owner review of allocator decisions vs realised outcomes.

---

## 6. Success metrics (measured, not asserted)

- **Breadth:** distinct paths emitting / week ↑ (from ~9 toward all viable paths).
- **Placement:** emission rate in STRONG cells ↑; in NEGATIVE cells → 0.
- **Quality:** realised avg R per emitted signal held or ↑; gate-audit **missed-R ↓**.
- **Integrity:** sub-anchor emissions to paid tier = **0** (hard invariant).
- **Autonomy:** cells transition STRONG↔NEGATIVE and emission follows within one
  measurement window with no code change.

Out of scope (separate leak, noted): exit give-back (+1.78% engine vs TP1-full sim;
Profit tab). This plan is emission quality, not exit machinery.

---

## 7. Decisions — taken by CTE (owner delegated 2026-07-19)

1. **Quality anchor = 60** (`CONTEXT_EMISSION_QUALITY_ANCHOR`, ops-tunable 50–75).
   A STRONG cell may emit down to ~60 off the 65 base (STRONG relax 5pts), POSITIVE
   to ~62 (3pts) — a context-*proven* minimum, gated on n≥30 real outcomes, never a
   blanket drop. Owner raises the anchor toward 65 in ops to shrink/kill the relax
   side; 65 = suppress-only. Sub-anchor never reaches paid users (hard clamp).
2. **Provenance weighting = emitted fully trusted, counterfactual-only haircut ×0.85**
   (`_PROV_*` in the allocator). Held-to-stop counterfactual MFE overstates a live
   exit, so equal measured edge is not equal confidence — a cell proven only on
   suppressed/shadow outcomes ranks below an emitted-confirmed one.
3. **Emission concurrency = 10** (`ALLOCATOR_EMISSION_MAX_CONCURRENT`), separate from
   and ≥ the capital cap of 6. Emitting a signal is not allocating capital; a signals
   business wants breadth. Ops-tunable.
4. **Pair-cohort taxonomy = deferred to Phase 5** — liquidity-tier + mover-vs-established
   cohort added to the context key (per-symbol is too sparse for n≥15). Not in this build.

---

## 8. What shipped (this PR) vs what's next

**Shipped LIVE (this PR), per owner directive:**
- `src/context_emission_policy.py` — the two-sided per-(strategy×context) floor.
- Scanner emission-gate wiring: relax STRONG/POSITIVE, suppress NEGATIVE, apply live
  (with `[CONTEXT_FLOOR_SHADOW]` divergence logging + monotonic counters either way).
- Allocator upgrade: provenance weighting + emission-concurrency envelope + emission
  view in the ops payload.
- **Full ops control** (Control → Signal gating): `context_emission_enabled` (kill),
  `context_emission_live` (apply vs measure-only), quality anchor, STRONG/POSITIVE
  relax points, min samples, suppress-NEGATIVE — all applied ≤5s, no redeploy.
- Liveness probe `context_emission_policy`; config env defaults; tests.

**Watch after deploy:** Strategy Lab — new `context_floor:*` gate-audit rows + the
per-path emission counts climbing (QCB / SR_FLIP / LIQ_SWEEP / DIV_CONT in their STRONG
cells). If the relax side misbehaves, raise the anchor toward 65 (or flip
`context_emission_live` OFF) in ops.

**Shipped (follow-up PR, 2026-07-19 — all three, LIVE + ops-controlled):**
- **`dispatch_cooldown` DROP leak** (235R, 100% would-win): default lowered 1800→900s
  and made two live ops tunables (`dispatch_cooldown_enabled`, `dispatch_cooldown_sec`,
  0–7200s). An explicit ops override wins; otherwise the module global (monkeypatch-safe).
- **MEAN_REVERT compat-map (#739 / F1):** the 18th path was compat-listed under
  CLEAN/DIRTY_RANGE only, but its ≥2.5σ trigger flips the classifier INTO
  VOLATILE_UNSUITABLE / BREAKOUT_EXPANSION — so it was gated pre-scoring by its own
  trigger (0 emissions). Added to both those states (additive; range homes intact). The
  context-emission policy auto-suppresses any cell where its edge turns NEGATIVE.
- **Phase 5 pair-cohort dimension:** `src/pair_cohort.py` (MAJOR/MIDCAP/ALTCOIN by
  liquidity). Every candidate stamps `mc_pair_cohort`; the edge-store feeders **dual-write**
  a cohort-refined cell (`context_key/COHORT`) **alongside** the base cell — additive, never
  fragments the live matrix. `context_emission_cohort_aware` (default OFF) makes the policy
  read the cohort cell first, base fallback when thin — the owner flips it ON in ops once
  cohort cells populate.

**Still open:** retire the bespoke RANGE_FADE gate into `context_emission_policy` (behaviour-equivalent cleanup).
