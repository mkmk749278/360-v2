# Layer G — Autonomous Emission Controller (closed-loop policy tuner)

_Owner-sign-off design. Status: **shadow-first**, apply gated OFF by default._
_Created 2026-07-20 (Session 72), owner ask: "we are making an autonomous system,
everything needs to adjust dynamically based on data — we can't look daily and adjust."_

---

## The gap this closes

Two loops already self-adapt on measured data:

- **Layer C→D (edge matrix → allocator):** every strategy×context cell is
  forward-measured; the allocator computes the routing answer.
- **PR 752 (context-emission policy):** the *per-cell* emission floor already
  adapts — a cell measured STRONG relaxes, a cell measured NEGATIVE suppresses,
  with no human. That inner loop works.

What is **still static / human-in-the-loop** — the gap:

1. **The gate KEEP/TUNE/DROP verdicts are advisory.** `suppression_audit`
   computes that `context_floor:MOVER_TREND_PULLBACK` is DROP at −0.38R (killing
   winners) and `context_floor:FAILED_AUCTION_RECLAIM` is KEEP at +0.12R — and
   then **nothing consumes those verdicts.** This is exactly where the edge
   matrix sat *before* 752: measured, correct, wired to nothing.
2. **The policy's own parameters are frozen config** — the `min_samples` relax
   floor (30), the anchor (60), `suppress_negative` (a single **global** bool).
   The thing that decides *how* the inner loop adapts cannot itself adapt. That
   is why the strongest cell in the whole matrix — `QUIET_COMPRESSION_BREAK @
   OVERLAP/QUIET/COMPRESSED` at **+2.21R** — sits at **n=29**, one sample under
   the n≥30 relax floor, and never emits.

Layer G is the outer loop that **consumes the gate verdicts + edge measurements
and moves the policy parameters itself**, per-strategy, inside a bounded envelope
— so the operator reviews the *envelope*, not the daily decisions.

---

## Principle: autonomy inside a bounded, owner-approved envelope

An unattended process mutating the **money path** (which signals emit) is a
different risk class than a one-time flip. Autonomy and the production
dark-flag-first doctrine reconcile **not** by removing guardrails but by making
the controller operate strictly inside an envelope the owner signs off on **once**:

- **Emission-only.** The controller can touch only the `context_emission_policy`
  parameters below. It can **never** touch scoring, evaluator geometry, the FSM,
  sizing, dispatch, paid-channel routing, blast-radius caps, the naked-position
  invariant, or any safety limit. Those remain exactly as enforced today.
- **Bounded action space** (hard-clamped in code, not just config).
- **Hysteresis, never reflexes** — acts only on verdicts stable across *K*
  cycles with sufficient sample. (Real evidence for why: in one 90-min span
  `min_confidence` EV swung +0.64R→+0.087R as counts grew. A reflex controller
  would chase that noise.)
- **Rate-limited + anti-oscillation** — at most one step per (strategy, param)
  per cycle; a reversal requires K fresh cycles of the opposite verdict.
- **Fully audited + one-flip kill** — every adjustment is stamped with the EV
  that justified it; `emission_controller_enabled=OFF` reverts to static policy
  instantly; a liveness probe pages if the controller flat-lines or pins a bound.
- **Dark-first, autonomous promotion** (owner directive, S72: _"I don't confirm
  anything — everything is autonomous, but dark-first, then make it live
  autonomously"_): there is **no human confirmation step.** The **data** promotes
  each change, not the owner. Every candidate adjustment starts **dark** — stamped
  to the ledger, applied to nothing — and is promoted to live **by itself** only
  once its own evidence clears the bar (verdict stable K cycles + EV magnitude +
  sample floor), after a global boot-grace of pure observation. The dark period is
  real but **self-administered per adjustment**, not gated on a person. The owner
  is in the loop for the **envelope and the kill switch**, never for a decision.
  This keeps "dark-first" (nothing applies on first sight, ever) while removing the
  human as the promotion latency — which is the whole point of an autonomous system.

---

## Action space (the only things Layer G may change)

Per **strategy** (e.g. `MOVER_TREND_PULLBACK`), an override on top of the global
`PolicyParams`:

| Param | Meaning | Bounds | Trigger to loosen | Trigger to tighten |
|---|---|---|---|---|
| `suppress_negative` | hard-suppress this strategy's NEGATIVE cells | {on, off} | `context_floor:S` = **DROP** stable K cycles (suppress is killing winners) → **off** | `context_floor:S` = **KEEP** stable K cycles → **on** (back to protective default) |
| `min_samples` | relax sample floor for this strategy's STRONG/POSITIVE cells | `[15, 30]`, step 5 | a STRONG cell exists with edge ≥ strong_r and `15 ≤ n < min_samples` stable K cycles → step **down** (unlock thin-but-strong, e.g. the n=29 QCB cell) | emissions unlocked by a prior step-down measure NEGATIVE → step **up** |

Both default to the global value; the controller only ever moves them **within the
bounds above**, one step per cycle, and both directions are data-triggered so it
self-corrects if a loosening turns out wrong. Nothing else is controllable.

Deliberately **out of scope** for v1 (candidates for a later envelope expansion,
each its own owner sign-off): per-cell relax magnitude, the anchor, cross-strategy
capital reallocation, and anything touching the suppress **threshold** edge value
(we toggle on/off, we don't move the NEGATIVE cutoff — smaller blast radius).

---

## Control signals (inputs, all already measured)

- **Per-gate EV** from `suppression_audit.compute_gate_suppression_metrics` →
  `by_gate["context_floor:<STRATEGY>"] = {n, ev_per_suppression_r, verdict}`.
  Verdict thresholds are the existing `SUPPRESSION_AUDIT_KEEP_EV_R` (+0.10) /
  `DROP_EV_R` (−0.20).
- **Per-strategy edge** from `strategy_edge` matrix: the largest-n cell above the
  STRONG edge that is currently below `min_samples` (the unlock candidate).
- **Controller state/history** (persisted): per-strategy current overrides + a
  deque of the last K verdicts per (strategy, param) + last-change cycle index.

---

## Cadence, hysteresis, guardrails (proposed envelope — owner tunable)

- **Cycle cadence:** every **30 min** in-process (piggybacks the existing
  measurement cadence; O(1) over the in-memory audit + edge stores, no hot-path
  I/O, one Firestore write only when an override actually changes → Cost
  Discipline safe).
- **Stability window K = 3** consecutive cycles of a consistent verdict before
  any change (~1.5 h of agreement). Tunable `emission_controller_stability_cycles`.
- **Sample floor per cycle:** a gate verdict counts toward stability only when its
  `n ≥ emission_controller_min_gate_n` (default 40).
- **Rate limit:** ≤ 1 change per (strategy, param) per cycle; a reversal needs K
  fresh opposite cycles (kills oscillation).
- **Blast-radius:** at most `emission_controller_max_changes_per_cycle` (default 2)
  distinct overrides changed in a single cycle across all strategies.
- **Kill / revert:** `emission_controller_enabled=OFF` → controller stops and the
  policy reads global params only (all overrides ignored). Instant, reversible.
- **Liveness:** probe `emission_controller` pages if the loop stops stamping, or if
  any param pins a bound for > N cycles (a pinned bound means the envelope is too
  tight and needs owner review — surfaced, never silently swallowed).

---

## Rollout — autonomous, no human confirmation

1. **Ship (this PR):** controller + store + per-strategy policy override read +
   loop + liveness + tunables + ledger surfaced in the truth report and the analysis
   bundle. `emission_controller_enabled=ON`.
2. **Boot-grace (automatic):** for the first `emission_controller_boot_grace_cycles`
   after any start/restart the controller **observes only** — it stamps candidate
   adjustments but promotes nothing. This is the system-level dark period; it needs
   no human. (Expected first candidates on today's data:
   `context_floor:MOVER_TREND_PULLBACK`→suppress off (measured −0.38R),
   `context_floor:SR_FLIP_RETEST`→suppress off (−0.37R),
   `min_samples[QUIET_COMPRESSION_BREAK]` 30→25 to unlock the +2.21R n=29 cell.)
3. **Autonomous promotion (automatic):** after boot-grace, each candidate is
   promoted to live **by the controller itself** the moment its own evidence clears
   the bar — verdict stable over K cycles, `|EV| ≥ promote_ev_r`, gate `n ≥ min_gate_n`.
   No owner action. A promotion that later sours is auto-reverted by the opposite
   verdict (the loop is symmetric).
4. **Owner's role:** the **envelope** (bounds/tunables) and the **kill**
   (`emission_controller_enabled=OFF` → static policy, instant). Never a per-change
   or go-live confirmation.

---

## Tunables (registry keys)

| Key | Default | Meaning |
|---|---|---|
| `emission_controller_enabled` | ON | master switch / kill; OFF → static policy, all overrides ignored |
| `emission_controller_boot_grace_cycles` | 3 | pure-observation cycles after start before anything can be promoted |
| `emission_controller_stability_cycles` | 3 | K — cycles of consistent verdict before a promotion |
| `emission_controller_promote_ev_r` | 0.25 | min \|EV/suppression\| magnitude to promote a suppress toggle |
| `emission_controller_min_gate_n` | 40 | min gate sample for a verdict to count toward stability |
| `emission_controller_max_changes_per_cycle` | 2 | blast-radius per cycle |
| `emission_controller_min_samples_floor` | 15 | lower bound for the per-strategy relax floor |

There is deliberately **no** `emission_controller_live` confirm-flag: promotion is
autonomous and data-gated (per owner directive). The only human switches are the
master kill and the envelope bounds above.

All owner-tunable at runtime (Control → Signal gating), ≤5s, no redeploy — same as
the PR 752 knobs.
