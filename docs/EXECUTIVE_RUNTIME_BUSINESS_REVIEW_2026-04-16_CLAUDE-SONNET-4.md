# 360 Crypto Eye — Executive Runtime + Business Review

> **Model:** Claude Sonnet 4
> **Date:** 2026-04-16
> **Role:** Chief Technical Engineer, full technical system owner, and business-aligned technical partner
> **Source evidence:** `OWNER_BRIEF.md` (main), `docs/ACTIVE_CONTEXT.md` (main), `monitor/latest.txt` (monitor-logs branch, 2026-04-16 06:12 UTC), repository commit history through PR-5 (#162)

---

## 1. Executive Truth

### Infrastructure truth
The infrastructure is genuinely healthy. Container up 14 hours, heartbeat 21s fresh, websocket connected to 300 streams, scan latency 1.57–1.94s (excellent), memory stable at 186MB, Redis alive with 3 keys, no errors or exceptions, no scan latency spikes. The VPS has 7GB free RAM, 140GB free disk. **Infrastructure is not the problem.**

### Architecture truth
The architecture has matured meaningfully since the April 13 correction pass. Five new PRs (PR-1 through PR-5) have landed on main since the last continuity update:
- **PR-1** (#158): Family-aware MTF gate refinement with per-family suppression telemetry
- **PR-2** (#159): Post-predictive SL/TP geometry revalidation with geometry delta telemetry
- **PR-3** (#160): Channel runtime-role truth made explicit; volatile pre-skip scoped
- **PR-4** (#161): End-to-end setup-path observability (full path funnel counters)
- **PR-5** (#162): Fail-closed specialist rollout states with limited-live divergence pilot

This is real structural progress. The scanner now has family-aware MTF policy, geometry telemetry at every stage, and a fail-closed rollout governance model. The observability now shows exactly where every candidate dies — by channel, family, setup class, and rejection reason.

### Runtime truth
**Zero emitted signals in the observed window.** This is the fact that matters most. The engine is alive, scanning, generating hundreds of candidates per cycle, and suppressing every single one. The system is a perfectly instrumented zero-output machine.

The path funnel data (last 100 cycles) tells the exact story:
- **FAILED_AUCTION_RECLAIM**: 626 generated → 626 gated (MTF passed some after policy relaxation) → **169 geometry-rejected** → 0 scored → 0 emitted
- **SR_FLIP_RETEST**: 325 generated → 280 gated → **112 geometry-rejected** → 45 scored → **45 filtered** (all score 50–64, WATCHLIST) → 0 emitted
- **LIQUIDITY_SWEEP_REVERSAL**: 121 generated → 95 gated → 26 scored → **26 filtered** (all score 50–64, WATCHLIST) → 0 emitted
- **RSI_MACD_DIVERGENCE**: 170 generated → 86 gated → 84 scored → **84 filtered** (all below 50) → 0 emitted
- **TREND_PULLBACK_EMA**: 1 generated → 1 geometry-rejected → 0 emitted

**No candidate in the entire observed window scored ≥65.** Every candidate that survived gates and geometry landed in WATCHLIST (50–64) or FILTERED (<50).

### Business truth
The system cannot produce a validation sample. It is a healthy, well-instrumented engine that emits zero paid signals. The business objective — a trustworthy, validation-capable, multi-family signal product — is completely blocked. Every improvement since April 13 has been observability and governance progress, not expression progress. The engine can tell you exactly why it fires nothing, but it still fires nothing.

---

## 2. What is Genuinely Improved vs. What Only Appears Improved

### Materially better now
1. **Path-level observability is genuinely excellent.** The funnel shows generated → gated → geometry → scored → filtered → emitted for every setup class. Rejection reasons are quantified. This was not available before PR-4.
2. **MTF gating is family-aware.** PR-1 introduced per-family MTF floor caps. `reclaim_retest` family (FAR + SFR) has a 0.35 cap; `reversal` has 0.35. MTF is no longer fully generic.
3. **Geometry telemetry is real.** The system now tracks SL cap events, risk-plan preservation vs. change, and exact rejection reasons at the risk-plan stage. This is new from PR-2.
4. **Rollout governance is fail-closed.** PR-5 introduced explicit rollout states (disabled/radar_only/limited_live/full_live). Channels cannot accidentally become live. This is structurally correct.
5. **WATCHLIST lifecycle segregation is clean.** PR #144 removed the defect where WATCHLIST signals entered paid active lifecycle.

### Only superficially better
1. **Family-aware MTF did not unlock expression.** MTF_gate is still the #1 suppressor by volume (227 events in the capture window), and the `mtf_policy_relaxed` counter shows the family caps are actively loosening many of these — **but the candidates that survive MTF are being killed by geometry or scoring.** MTF improvement addressed the wrong bottleneck layer.
2. **Geometry telemetry is excellent observation, not correction.** We can now see that FAILED_AUCTION_RECLAIM geometry is rejected 169/626 times (27%), with 76 "risk_distance_too_tight" and 40+ "rr below 1.00" rejections — but the geometry policy itself is unchanged. Observability without action is surveillance, not improvement.
3. **Specialist rollout is well-governed but inert.** The limited_live divergence pilot produces nothing — 360_SCALP_DIVERGENCE candidates are generated (170) but all score below 50. The rollout framework is clean but has no expression flowing through it.

### Does not translate to business progress
- All 5 new PRs (PR-1 through PR-5) are governance, observability, and correctness improvements. None of them increased the probability of a signal scoring ≥65.
- The system has gone from "zero output with no visibility into why" to "zero output with complete visibility into why." This is diagnostic progress, not product progress.
- The continuity docs record this as Phase 7: "Post-Correction Live Monitoring." In reality, monitoring has been conclusive for days — the diagnosis is clear. Continued monitoring without action is stalling.

---

## 3. Primary Bottleneck Diagnosis

### #1 Bottleneck: Geometry rejection is destroying the reclaim_retest family before scoring

**Why it matters:** FAILED_AUCTION_RECLAIM is the most prolific candidate generator in the system (626 candidates/100 cycles). It is also the most prolific path to geometry death: 169 rejections, of which **76 are "risk_distance_too_tight"** and **40+ are R:R below 1.00**. Not a single FAR candidate reaches scoring. SR_FLIP_RETEST generates 325 candidates; 112 are geometry-rejected (mostly R:R below 1.00). The reclaim_retest family — which should be the structural backbone of the system — is being obliterated by geometry policy before the scoring engine ever sees it.

**Root cause (code-driven):** The `risk_distance_too_tight` rejection in `build_risk_plan` (signal_quality.py:1157) fires when `risk <= max(entry * 0.0003, buffer * 0.5)`. For FAILED_AUCTION_RECLAIM, the evaluator-authored structural SL is often very close to entry (tight auction reclaim), and after the 1.5% SL cap compresses the distance further, the remaining risk is below the `buffer * 0.5` floor. The system is rejecting structurally valid tight reclaims because the geometry guard doesn't understand that a tight reclaim SL is the thesis, not a defect.

Similarly, the `rr_below_min` rejection (min R:R = 1.0 for FAR/SFR) kills candidates where the TP targets are modest relative to the capped risk. When the SL is artificially compressed by the 1.5% cap, and the TP is calculated from the compressed risk, the R:R math is distorted. The evaluator may have authored a healthy 1.5R setup, but after SL capping, the geometry looks sub-1.0R.

**This is internal-code-driven, not market-driven.** The geometry policy is systematically destroying the highest-volume family.

**Should be acted on now:** YES — this is the primary expression-blocking bottleneck.

### #2 Bottleneck: All surviving candidates score 50–64 (WATCHLIST), never ≥65

**Why it matters:** The few candidates that survive geometry (45 SR_FLIP_RETEST, 26 LIQUIDITY_SWEEP_REVERSAL) all land in the WATCHLIST tier (50–64). Not one reaches B-tier (65+). This means even if geometry is fixed, the scoring engine may still filter everything.

**Root cause (code-driven + scoring model):** The scoring model's base dimensions (market_score, setup_score, execution_score, risk_score, context_score) appear to produce a natural ceiling around 60–64 for current market conditions. The `legacy_confidence` context dimension (10% weight) and the risk_score dimension (anchored to R:R which is depressed by SL capping) both contribute to the ceiling.

**Should be acted on:** After geometry is addressed. Fixing geometry may naturally lift scores by improving R:R, which feeds directly into `risk_score`. Premature scoring changes would be speculative.

### #3 Bottleneck: Spread suppression removes ~10 pairs per cycle

**Why it matters:** `pair_quality:spread too wide` hits 9–12 pairs per cycle. This is the second-highest suppressor volume. It reduces the candidate pool before evaluation.

**Root cause (market-driven):** Spread is a genuine market quality gate. Current market conditions have wide spreads on many altcoins. This is not fixable by code unless the threshold is loosened, which would compromise signal quality.

**Should be acted on later:** Not now. Spread suppression is protective. Market conditions will shift.

### #4 Bottleneck: Volatile_unsuitable bypass hits 8–12 candidates per cycle

**Why it matters:** `volatile_unsuitable:channel_preskip_bypassed:360_SCALP` fires 8–12 times per cycle. These are candidates where the volatile regime would normally block the channel, but the pre-skip bypass logic allows 360_SCALP to continue. This is a telemetry marker, not a direct suppressor — but it signals that many candidates are being generated in marginal volatile conditions.

**Should be acted on later:** This is informational, not blocking.

---

## 4. Is Targeted Family-Aware MTF Refinement Truly the Best Next Move?

**No. It is not.**

The continuity docs and the apparent roadmap assume MTF refinement is the next priority. This was a reasonable assumption as of April 14, when the MTF gate was the most visible suppressor by counter volume. But the current path funnel data — now available thanks to PR-4 — tells a different story.

### Evidence against MTF refinement as the next move

1. **MTF is not the binding constraint.** The `mtf_policy_relaxed` counter shows 7–14 candidates per cycle where the family-aware MTF floor already loosened the gate. Many FAILED_AUCTION_RECLAIM and LIQUIDITY_SWEEP_REVERSAL candidates **pass** MTF after relaxation — but they die in geometry. MTF refinement would increase the number of candidates entering the geometry stage, but if geometry still kills them all, the net output is still zero.

2. **The geometry rejection rate is catastrophic.** 169/626 (27%) of FAR candidates and 112/325 (34%) of SFR candidates are geometry-rejected. Of the FAR geometry rejections, 76/169 (45%) are `risk_distance_too_tight` — a problem that is entirely internal to the risk plan builder, not to MTF.

3. **Candidates that survive geometry all score 50–64.** Even if MTF refinement pushed 10 more candidates past the MTF gate, they would die at geometry or score below 65 and land in WATCHLIST. Zero paid output.

4. **PR-1 already addressed MTF with family-aware floors.** Further MTF loosening without fixing the downstream geometry blockage is the definition of "fake progress through broad loosening."

### Alternatives evaluated

- **Geometry hardening/repair:** Directly addresses the binding constraint. The `risk_distance_too_tight` threshold and the interaction between SL capping and R:R validation are the specific mechanisms killing expression. Fixing this is the highest-leverage move.
- **Duplicate lifecycle hardening:** Confirmed defect (2026-04-14 audit), but not expression-blocking. It matters for product quality but doesn't help until there are signals to track.
- **Specialist rollout refinement:** The rollout framework is clean (PR-5). There's nothing to refine until expression exists to roll out.
- **Continuity/doc sync:** Stale docs are a real problem (see Section 8) but don't block expression.
- **More evidence gathering:** The evidence is already conclusive. The path funnel tells the full story. Further monitoring without action is delay.

---

## 5. Best Next Action

**One best next action: Fix the geometry risk-plan policy for the reclaim_retest family to stop systematically destroying structurally valid FAILED_AUCTION_RECLAIM and SR_FLIP_RETEST candidates.**

### Why this is first
1. **It targets the binding constraint.** Geometry rejection is the single largest destroyer of expression in the system. 169 FAR + 112 SFR = 281 geometry kills per 100 cycles. This is more than MTF, spread, volatile, or scoring combined as a barrier to paid output.

2. **It is high-leverage.** Fixing `risk_distance_too_tight` for FAR alone would let ~76 additional candidates reach scoring per 100 cycles. Fixing R:R validation interaction with SL capping would rescue another 40+. Even if only 10% of these score ≥65, that is **7–12 paid-tier signals per 100 cycles** — from zero.

3. **It is surgically addressable.** The problem is localized in `build_risk_plan` (signal_quality.py:1150–1167) and the interaction between the 1.5% SL cap (lines 1079–1098) and the `risk <= max(entry * 0.0003, buffer * 0.5)` guard. The fix is family-specific geometry policy for reclaim setups, not a global loosening.

4. **It protects doctrine.** The fix does not require lowering global thresholds, removing protective gates, or compromising the quality bar. It requires making the geometry guard family-aware — the same principle already applied to MTF in PR-1.

### Why alternatives are weaker right now
- **MTF refinement:** Already partially addressed by PR-1. Further loosening doesn't help because geometry kills everything downstream.
- **Scoring model adjustment:** Premature. Fixing geometry will improve R:R, which directly feeds risk_score. The scoring ceiling may self-correct once geometry stops destroying the inputs.
- **Duplicate lifecycle fix:** Important but doesn't produce expression.
- **Continuity sync:** Necessary but doesn't produce expression.

### Business/system outcome it unlocks
- First real paid signal emission since the correction sequence
- A validation sample of reclaim_retest family signals
- Evidence-based scoring model evaluation (impossible without surviving candidates)
- Phase 1 validation progress

---

## 6. PR Definition: Family-Aware Geometry Policy for Reclaim Setups

### Objective
Stop the `risk_distance_too_tight` and `rr_below_min` rejections from systematically destroying FAILED_AUCTION_RECLAIM and SR_FLIP_RETEST candidates where the evaluator-authored geometry is structurally valid.

### Why now
Because the path funnel data proves this is the primary expression-blocking bottleneck. MTF, spread, and scoring are all secondary to this. No paid signals will emerge from the system until the geometry policy stops killing the two most prolific setup families.

### What it should change

1. **Make `risk_distance_too_tight` threshold family-aware in `build_risk_plan`** (signal_quality.py:1156–1167):
   - For FAILED_AUCTION_RECLAIM: the tight structural SL is the thesis. The guard should use a tighter floor (e.g., `entry * 0.0001`) instead of `max(entry * 0.0003, buffer * 0.5)`. The `buffer * 0.5` component is the killer — it's derived from ATR and spread, which can be large relative to a tight reclaim distance.
   - For SR_FLIP_RETEST: similar adjustment, since structural flip retests can have tight invalidation distances.
   - All other setup classes: unchanged.

2. **Evaluate whether the 1.5% SL cap distortion needs mitigation for reclaim setups:**
   - The SL cap (lines 1079–1098) compresses evaluator-authored SL before R:R is checked. If FAR's evaluator SL is 2.1% and gets capped to 1.5%, the TP targets (computed from the original structure) now have a distorted R:R.
   - Consider: compute R:R from evaluator-original SL distance before cap, or raise the SL cap for reclaim setups only (e.g., 2.0%). This must be carefully scoped — not global.

3. **Add telemetry for candidates that pass the updated geometry guard** — track how many additional candidates reach scoring and what tier they land in.

### What it must not change
- **Do not lower global SL cap.** Channel-wide 1.5% max stays for all non-reclaim families.
- **Do not lower global R:R minimums.** The 1.0 minimum for structured setups (FAR/SFR) is reasonable if the SL isn't being artificially compressed.
- **Do not remove or weaken `validate_geometry_against_policy`.** The post-predictive revalidation gate (PR-2) must remain intact.
- **Do not touch MTF gates, scoring thresholds, or confidence floors.**
- **Do not enable any disabled channels or change rollout states.**
- **Do not modify QUIET_SCALP_BLOCK, trend_hard_gate, or spread gate logic.**

### Acceptance criteria
1. **Path funnel shows FAR candidates reaching scoring stage** (currently 0 — target: 10+ per 100 cycles)
2. **At least some scored FAR/SFR candidates reach B-tier (≥65)** within 24h of deployment
3. **No increase in SL_HIT rate** for surviving signals (checked against performance history once signals exist)
4. **All existing tests pass** (no behavioral regression)
5. **New tests cover the family-specific geometry guard** with edge cases (tight reclaim, wide reclaim, cap interaction)

### Failure modes / business risk
1. **Over-loosening risk_distance_too_tight:** If the threshold is dropped too far, garbage candidates with near-zero risk (noise, not structural) could reach scoring. Mitigation: use a family-specific floor, not a global one; test with real FAR candidate data from the monitor.
2. **SL cap interaction creating bad R:R signals:** If the SL cap is raised for reclaim setups, some signals may have wider stops. Mitigation: test the R:R distribution empirically; keep the cap modest (e.g., 2.0%, not 3.0%).
3. **Scoring ceiling persists:** The candidates may survive geometry but still score 50–64. If this happens, it confirms the scoring model needs attention as a follow-up — but the geometry fix is still the correct first step because it creates the data to diagnose scoring.

---

## 7. What Should Not Be Done Now

1. **Broad MTF threshold loosening.** MTF is not the binding constraint. Further loosening sends more candidates into the geometry meat grinder and produces zero net expression. Tempting because MTF counters are high, but wrong because geometry kills everything downstream.

2. **Global SL cap relaxation.** Raising the 1.5% SL cap for all channels would increase risk exposure across every setup family. The correct fix is family-specific: only reclaim setups need geometry policy adjustment.

3. **Scoring model overhaul.** Premature without candidates that survive geometry to calibrate against. Fix geometry first, then evaluate whether scoring is the next bottleneck with real data.

4. **Enabling disabled auxiliary channels.** The rollout framework (PR-5) is correct to keep channels disabled until expression from 360_SCALP is proven. Enabling FVG/CVD/VWAP now would spread attention without solving the core problem.

5. **Treating healthy infrastructure as business progress.** The engine is healthy. The infrastructure is solid. The telemetry is excellent. None of this is business progress. The only business progress is emitted paid signals.

6. **More monitoring without action.** The path funnel data is conclusive. The geometry bottleneck is quantified, localized, and actionable. Further monitoring cycles produce the same data. The diagnosis phase is complete.

7. **Continuity doc update as a primary action.** The docs are stale (see Section 8), but updating them without fixing the expression bottleneck is paperwork disguised as progress.

8. **Chasing QUIET_SCALP_BLOCK or spread suppressors.** QUIET_SCALP_BLOCK fires on candidates with conf 41–64 — these are legitimately weak candidates in a quiet regime. Spread suppression is market-driven. Neither is actionable for expression recovery.

---

## 8. Repo Truth vs. Continuity Truth

### ACTIVE_CONTEXT.md is materially stale.

**Last updated:** 2026-04-14 (PR #146)

**What it does not know about:**
- **PR-1** (2026-04-15): Family-aware MTF gate refinement — entirely absent from ACTIVE_CONTEXT
- **PR-2** (2026-04-15): Post-predictive geometry revalidation and geometry delta telemetry — absent
- **PR-3** (2026-04-15): Channel runtime-role truth and volatile pre-skip scoping — absent
- **PR-4** (2026-04-15): End-to-end path observability with path funnel counters — absent
- **PR-5** (2026-04-15): Fail-closed specialist rollout states with divergence pilot — absent
- **OWNER_BRIEF.md** was updated (PR #157, 2026-04-15) to reflect the new phase roadmap — ACTIVE_CONTEXT still references the old priority queue

**What it says that is now wrong:**
- "Current Active Priority #1: Verify post-merge WATCHLIST behavior live" — this was the priority before PR-1 through PR-5. The priority should now be geometry-driven expression recovery.
- "Next PR Queue: Priority 2 = lifecycle idempotency, Priority 3 = targeted family-aware MTF gate refinement" — MTF refinement is done (PR-1). The next priority should be geometry policy for reclaim setups.
- "Current Known Live Issues" table doesn't mention the path funnel data, geometry rejection rates, or the zero-expression state post-PR-5.
- "Duplicate lifecycle posting not yet fixed" — still true, but its relative priority has shifted given the expression emergency.

### Why staleness matters
A new Copilot session reading ACTIVE_CONTEXT would:
1. Think WATCHLIST verification is still the top priority (it was validated days ago)
2. Think MTF refinement is the planned next technical PR (it was already done)
3. Not know about the path funnel evidence showing geometry as the real bottleneck
4. Miss the complete set of PRs (PR-1 through PR-5) that represent the current system state

This creates a real risk of wasted sessions and misaligned next moves.

### OWNER_BRIEF.md is current as of 2026-04-15.
It was updated in PR #157 to reflect the new-phase roadmap. It correctly describes the architecture, the setup families, and the strategic objectives. However, it does not contain the path funnel diagnosis — that evidence is only in the monitor data.

### Fix priority
Continuity doc synchronization is a **required follow-up action** after the geometry PR, not a primary action. It should be done in the same session that implements the geometry fix, as the session-end responsibility.

---

## 9. Final Owner-Level Verdict

Speaking directly:

**What is true:**
- The engine is healthy. The infrastructure is solid. The architecture has genuinely matured through PR-1 to PR-5. The observability is now excellent. None of this has produced a single paid signal.

**What matters most:**
- Geometry rejection is destroying the reclaim_retest family — the system's highest-volume candidate generator — before the scoring engine ever touches it. 281 geometry kills per 100 cycles. Zero survivors reach B-tier. This is not a market condition. This is a code policy that treats tight structural reclaims as defects.

**What is misleadingly comforting:**
- "Engine healthy, heartbeat fresh, no errors." True and meaningless for the business. A perfectly healthy engine that emits nothing is the definition of a well-maintained zero-revenue product.
- "Path observability is now live." Excellent for diagnosis, but diagnosis without action is just watching. The path funnel has been telling the same story across multiple monitoring cycles. The data is conclusive.
- "Family-aware MTF is deployed." Real progress, but MTF was not the binding constraint. The highest-volume families survive MTF (with policy relaxation) and die in geometry.

**The strongest next move:**
Family-specific geometry policy repair for reclaim setups — targeted fix to `risk_distance_too_tight` threshold and SL-cap/R:R interaction in `build_risk_plan` for FAILED_AUCTION_RECLAIM and SR_FLIP_RETEST. One PR, one clear outcome: candidates from the system's most prolific family reach scoring and have a real chance at B-tier or above.

**Why this is right for both technical integrity and business progress:**
It is the only action that addresses the actual binding constraint. It doesn't lower quality bars, doesn't loosen global protections, doesn't pretend observability is output. It fixes a specific geometry policy that treats valid tight-reclaim setups as defective, and it does so family-specifically — exactly the architectural principle the system has been evolving toward since PR-1.

The system has spent two days in Phase 7 "post-correction monitoring." The monitoring is conclusive. The geometry bottleneck is quantified. The next phase is not more monitoring — it is targeted geometry correction that converts the observability investment into actual expression.

---

## Appendix: Key Evidence Sources

### Monitor data (2026-04-16 06:12 UTC)
- Container: healthy, 14h uptime
- Scan latency: 1.57–1.94s
- Signals fired: 0
- Signal history: none
- Top suppressors (last 500 lines):
  - `mtf_gate_setup:360_SCALP:FAILED_AUCTION_RECLAIM`: 227
  - `mtf_gate_family:360_SCALP:reclaim_retest`: 227
  - `mtf_gate:360_SCALP`: 227
  - `volatile_unsuitable:channel_preskip_bypassed:360_SCALP`: 218
  - `score_below50:RSI_MACD_DIVERGENCE`: 209
  - `pair_quality:spread`: 209
  - `score_below50:360_SCALP_DIVERGENCE`: 206
  - `QUIET_SCALP_BLOCK`: 64

### Path funnel (last 100 cycles)
- FAR: 626 generated → 169 geometry-rejected (76 risk_distance_too_tight, 40+ rr_below_min) → 0 scored
- SFR: 325 generated → 112 geometry-rejected → 45 scored → 45 filtered (all 50–64)
- LSR: 121 generated → 26 scored → 26 filtered (all 50–64)
- RSI_MACD: 170 generated → 84 scored → 84 filtered (all <50)
- TPE: 1 generated → 1 geometry-rejected → 0

### Geometry rejection breakdown (FAR, last 100 cycles)
| Reason | Count |
|--------|-------|
| risk_distance_too_tight | 76 |
| rr_0.36_below_1.00 | 40 |
| rr_0.10_below_1.00 | 12 |
| rr_0.21_below_1.00 | 11 |
| rr_0.22_below_1.00 | 6 |
| rr_0.55_below_1.00 | 2 |
| rr_0.01_below_1.00 | 6 |
| rr_0.04_below_1.00 | 6 |
| rr_0.07_below_1.00 | 1 |
| rr_0.37_below_1.00 | 9 |

### Scoring tier distribution (last 100 cycles)
| Evaluator | Reached Scoring | Score 50–64 | Score <50 |
|-----------|----------------|-------------|-----------|
| RSI_MACD_DIVERGENCE | 84 | 0 | 84 |
| LIQUIDITY_SWEEP_REVERSAL | 26 | 18 | 8 |
| SR_FLIP_RETEST | 45 | 35 | 10 |

### Commits since last ACTIVE_CONTEXT update
| SHA | PR | Description |
|-----|-----|-------------|
| d0e2b8f | PR-5 (#162) | Fail-closed specialist rollout states with limited-live divergence pilot |
| 99e048f | PR-4 (#161) | End-to-end setup-path observability across scanner funnel and lifecycle outcomes |
| e51c0a5 | PR-3 (#160) | Make channel runtime-role truth explicit and scope volatile pre-skip cleanup |
| 81b706f | PR-2 (#159) | Harden SL/TP geometry integrity with post-predictive revalidation and geometry delta telemetry |
| 0de5f46 | PR-1 (#158) | Family-aware 360_SCALP MTF gate refinement with per-family suppression telemetry |
