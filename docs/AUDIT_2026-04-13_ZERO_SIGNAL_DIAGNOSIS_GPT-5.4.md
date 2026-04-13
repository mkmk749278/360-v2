# Zero-Signal Diagnosis Audit — 2026-04-13 — GPT-5.4

## Executive Summary

This audit was produced under the 360 Crypto Eye chief-engineer operating contract after reading:
- `OWNER_BRIEF.md` from `main` (821 lines; integrity confirmed)
- `docs/ACTIVE_CONTEXT.md` from `main`
- `monitor/latest.txt` from `monitor-logs` (generated 2026-04-13 06:49:44 UTC)

Primary conclusion: **the engine is alive, scanning, and generating some real candidates, but live output is being suppressed by a combination of genuine poor scalp market quality and an over-tight downstream governance funnel inside `360_SCALP`.** This is **not** a dead-infrastructure incident.

The zero-signal state is best explained as:
1. **Real market-quality suppression** on a large part of the pair universe (`spread too wide`, auxiliary channels marked `volatile_unsuitable`)
2. **Strong generic MTF rejection** on the main paid channel
3. **A confirmed policy/architecture mismatch** where `360_SCALP` B-tier scores (65–79) are classified as valid setup-quality signals but still fail the final `min_confidence=80` dispatch floor
4. **Recurring quiet-regime filtering** on surviving sub-65 scalp candidates
5. **Localized risk-geometry loss** in FVG setups, but this is a secondary, family-specific issue rather than the primary system-wide blocker

Protective mode is **not** itself blocking entries. It is a broadcaster/symptom layer reflecting the same spread/volatility reality already suppressing the funnel.

---

## 1. Executive diagnosis

- The engine is operational: container healthy, heartbeat fresh, websocket health OK, Redis connected, no runtime exceptions.
- The engine is **not silent because it is broken**; it is silent because candidates are being filtered out.
- Live evidence proves the scanner is producing real `360_SCALP` candidates that reach the scoring stage.
- The dominant hard suppressor in the live snapshot is **pair-quality spread rejection**, often affecting **32–60 pairs per cycle**.
- The next dominant suppressor on the main paid path is **generic scanner MTF gating**, peaking at **14 `mtf_gate:360_SCALP` suppressions per cycle**.
- The main path is also producing repeated **65–79 B-tier** `LIQUIDITY_SWEEP_REVERSAL` candidates, but `360_SCALP` still requires `min_confidence=80`, so those B-tier candidates cannot dispatch.
- Repeated `QUIET_SCALP_BLOCK` logs show surviving scalp candidates are still failing the quiet-regime floor of **65.0** after scoring/penalties.
- Auxiliary scalp families (`FVG`, `DIVERGENCE`, `ORDERBLOCK`) are frequently excluded earlier by `VOLATILE_UNSUITABLE` gating; this is reducing family diversity materially.
- FVG also has repeated evaluator-local **SL geometry discards**, but that is a secondary family-specific loss channel, not the main reason for zero total output.
- Net: **zero live signals is a mixed outcome** — partly correct caution in poor scalp conditions, partly over-suppression from current governance architecture.

---

## 2. Live operational evidence

### Confirmed facts from `monitor/latest.txt`

- Engine container is `Up ... (healthy)` and Redis is up.
- Heartbeat age is `0s`.
- Telemetry repeatedly shows `Signals=0`, `Pairs=75`, `WS=300(ok=True)`, `Redis=True`.
- Scan latency is mixed: healthy stretches around **4.0s–4.9s**, but spikes also occur at **14.3s**, **28.8s**, and **35.3s**.
- No signal history exists yet.
- No runtime errors/exceptions were found in the last 500 log lines.
- Repeated scanner summaries show:
  - `pair_quality:spread too wide`
  - `mtf_gate:360_SCALP`
  - `volatile_unsuitable:360_SCALP_FVG`
  - `volatile_unsuitable:360_SCALP_DIVERGENCE`
  - `volatile_unsuitable:360_SCALP_ORDERBLOCK`
  - `score_65to79:LIQUIDITY_SWEEP_REVERSAL`
  - `score_50to64:LIQUIDITY_SWEEP_REVERSAL`
  - `candidate_reached_scoring:SR_FLIP_RETEST`
  - `score_below50:SR_FLIP_RETEST`
- Repeated info logs show `QUIET_SCALP_BLOCK` on main `360_SCALP` candidates with live confidence values such as **63.0**, **62.3**, **61.2**, **60.3**, **56.7**, **55.3**, **49.7**.
- Repeated warnings show FVG evaluator discards such as:
  - `FVG SL rejected ... > 2.00% max — signal discarded`
- Repeated warnings show risk-plan SL caps such as:
  - `SL capped for 360_SCALP ... > 1.50% max`
- Protective mode is repeatedly entered with trigger counts such as:
  - `(volatile=21, spread_wide=40)`
  - `(volatile=24, spread_wide=40)`
  - `(volatile=33, spread_wide=32)`
  - `(volatile=15, spread_wide=48)`
  - `(volatile=18, spread_wide=40)`
  - `(volatile=15, spread_wide=60)`

### Confirmed facts from monitor aggregation

- Only two internal `360_SCALP` setup classes are visibly reaching scoring in this snapshot:
  - `LIQUIDITY_SWEEP_REVERSAL`
  - `SR_FLIP_RETEST`
- Observed peak suppressor counts in the snapshot:
  - `pair_quality:spread too wide` → **60**
  - `mtf_gate:360_SCALP` → **14**
  - `volatile_unsuitable:360_SCALP_FVG` → **13**
  - `volatile_unsuitable:360_SCALP_DIVERGENCE` → **13**
  - `volatile_unsuitable:360_SCALP_ORDERBLOCK` → **13**
  - `trend_hard_gate:360_SCALP` → **2**

### Inferences supported by those facts

- The scanner loop is alive and repeatedly completing cycles; infrastructure is not the primary failure mode.
- Candidate generation exists, but diversity is narrow in current live conditions.
- The current market is hostile to scalp execution across much of the watched universe.
- The main output bottleneck is the **suppression funnel**, not dispatch failure.
- Scan latency is a secondary operational concern, not the main reason for zero output, because zero signals persists during low-latency windows too.

---

## 3. Code-path diagnosis

### Candidate flow traced in code

1. **Context build**
   - `_build_scan_context()` assembles candles, indicators, SMC state, spread, pair quality, market state, regime context, funding, and CVD.
2. **Channel pre-skip stage**
   - `_should_skip_channel()` can block a whole channel before evaluation for:
     - pair quality / spread
     - `VOLATILE_UNSUITABLE` on non-main scalp channels
     - cooldown / circuit breaker / existing active signal
3. **Evaluator generation**
   - `ScalpChannel.evaluate()` runs all 14 internal evaluators and returns a list of all non-`None` candidates.
4. **Per-candidate pipeline in `_prepare_signal()`**
   - setup compatibility
   - execution quality
   - generic scanner MTF gate
   - soft gates / penalties
   - risk-plan evaluation
   - scoring engine
   - post-score penalties
   - SMC hard gate
   - trend hard gate
   - quiet-regime block
   - watchlist/min-confidence/final component floors
5. **Arbitration / enqueue**
   - `_scan_symbol()` keeps the highest-confidence `360_SCALP` candidate per direction, then enqueues survivors.

### Where live candidates are being lost

#### Layer A — pre-evaluator / whole-channel suppression
- `pair_quality:spread too wide` is applied in `_should_skip_channel()` before signal evaluation.
- `volatile_unsuitable:*` suppresses `360_SCALP_FVG`, `360_SCALP_DIVERGENCE`, and `360_SCALP_ORDERBLOCK` before they can compete.
- This explains why auxiliary family diversity is low in live output.

#### Layer B — evaluator-local discards
- `ScalpFVGChannel` hard-discards setups when FVG stop geometry exceeds **2.00%** of entry.
- Those warnings in monitor map directly to evaluator-level rejection before scanner scoring.

#### Layer C — scanner generic MTF gate
- `_prepare_signal()` applies a generic `check_mtf_gate()` to every prepared candidate.
- This gate is recorded live as `mtf_gate:360_SCALP` and is one of the dominant suppressors.
- This happens even though some evaluators already contain their own thesis-aware MTF logic.

#### Layer D — scoring stage
- Live monitor proves some candidates reach scoring via `candidate_reached_scoring:*` counters.
- In this snapshot, the visible scoring survivors are mainly `LIQUIDITY_SWEEP_REVERSAL` and `SR_FLIP_RETEST`.

#### Layer E — post-score governance loss
- `classify_signal_tier()` defines:
  - `A+` = 80–100
  - `B` = 65–79
  - `WATCHLIST` = 50–64
- But final dispatch still rejects `360_SCALP` if `sig.confidence < min_conf`, and `360_SCALP` is configured with `min_confidence=80`.
- Therefore **B-tier `360_SCALP` candidates are structurally non-dispatchable** under current config.
- Live monitor repeatedly shows `score_65to79:LIQUIDITY_SWEEP_REVERSAL`, confirming this is not hypothetical.

#### Layer F — quiet-regime block
- In QUIET regime, `360_SCALP` candidates below **65.0** are blocked unless they are narrow named exemptions.
- The repeated `QUIET_SCALP_BLOCK ... conf=<65.0` logs map directly to this block.

#### Layer G — risk-plan / geometry friction
- `build_risk_plan()` caps main scalp SLs at **1.50%** and preserves some structural stops.
- SL caps are warnings, not automatic rejections.
- Risk-plan rejection is therefore present but **not evidenced as a dominant global suppressor** in the current monitor snapshot.
- FVG geometry rejection is real, but localized to that family.

### Important architectural finding: protective mode is not a suppressor

- Protective mode logic is a **broadcaster only**.
- It is triggered by high counts of `volatile_unsuitable:*` and `pair_quality:spread too wide`.
- It does **not** itself block signal creation or dispatch.
- Therefore it should be treated as **evidence of hostile market conditions**, not as the direct root cause of zero signals.

---

## 4. Ranked root causes

### Root cause 1 — Poor live scalp market quality across much of the universe
- **What it is:** Large portions of the 75-pair universe are failing spread suitability for scalp execution.
- **Evidence:** `pair_quality:spread too wide` repeatedly appears at **32–60 pairs per cycle**; protective mode spread triggers are repeatedly breached.
- **Type:** **Market reality** with correct safety enforcement.
- **Confidence:** **High**.
- **Business impact:** Correctly protects capital and honesty, but sustained zero output will hurt subscriber trust if the engine cannot still express quality on the tradable subset.

### Root cause 2 — Generic scanner MTF gate is heavily suppressing the main paid path
- **What it is:** A universal scanner-level MTF confluence gate is rejecting many `360_SCALP` candidates before scoring/dispatch.
- **Evidence:** `mtf_gate:360_SCALP` peaks at **14 per cycle** and is consistently present even when other suppressors fluctuate.
- **Type:** **Mixed** — some market reality, some probable policy/architecture mismatch.
- **Confidence:** **High** that it is dominant; **medium-high** that it is partially over-tight.
- **Business impact:** Strongly reduces main paid-channel expression and may disproportionately harm reversal/structure paths whose thesis is not generic trend alignment.

### Root cause 3 — Confirmed `360_SCALP` B-tier dead zone
- **What it is:** The system classifies 65–79 as valid B-tier signals, but `360_SCALP` still requires `min_confidence=80`, so B-tier main-channel signals cannot dispatch.
- **Evidence:**
  - `classify_signal_tier()` defines B = 65–79.
  - `CHANNEL_SCALP.min_confidence` is 80.
  - final floor check rejects anything below that min.
  - monitor repeatedly shows `score_65to79:LIQUIDITY_SWEEP_REVERSAL` with zero output.
- **Type:** **Policy mismatch / architecture mismatch**.
- **Confidence:** **High**.
- **Business impact:** This is a direct strategy-expression integrity issue. The engine is finding B-tier setups but structurally cannot express them on the paid main path.

### Root cause 4 — Quiet-regime scalp floor is blocking the remaining near-threshold main-channel candidates
- **What it is:** Surviving `360_SCALP` candidates in QUIET regime are failing the 65.0 floor.
- **Evidence:** repeated `QUIET_SCALP_BLOCK` logs with live confidence values below 65.
- **Type:** **Mixed** — partly correct caution, partly interacting with the B-tier mismatch and earlier MTF pressure.
- **Confidence:** **High**.
- **Business impact:** Correctly avoids weak quiet-market scalps, but in combination with the current funnel it contributes to total silence.

### Root cause 5 — Auxiliary families are largely excluded before meaningful competition
- **What it is:** `FVG`, `DIVERGENCE`, and `ORDERBLOCK` families are repeatedly suppressed by `VOLATILE_UNSUITABLE` before they can meaningfully contribute diversity.
- **Evidence:** repeated `volatile_unsuitable:*` counts around **5–13** per family per cycle.
- **Type:** **Mixed** — likely correct in current market, but strategically important because it leaves too much burden on the main `360_SCALP` path.
- **Confidence:** **High** on effect, **medium** on whether current policy is too tight.
- **Business impact:** Low diversity means the business experiences “engine alive but silent” even when some path families might otherwise express edge.

### Root cause 6 — FVG risk geometry is causing family-specific early discards
- **What it is:** FVG evaluator rejects setups whose structural stop is too wide for scalp use.
- **Evidence:** repeated `FVG SL rejected ... signal discarded` warnings, sometimes with extremely wide distances.
- **Type:** Mostly **market reality** with possible evaluator/path-fit limitations.
- **Confidence:** **High** that it is real, **low** that it is primary.
- **Business impact:** Secondary; it hurts one auxiliary family, not the whole engine.

### Root cause 7 — Scan latency remains an operational drag but not the main zero-signal cause
- **What it is:** Some scan cycles still spike to 14–35 seconds.
- **Evidence:** live telemetry in monitor snapshot.
- **Type:** **Operational issue**, not primary zero-signal root cause.
- **Confidence:** **High** that it exists, **high** that it is secondary here.
- **Business impact:** Delayed recognition and weaker freshness, but not sufficient to explain zero output because silence persists during fast cycles too.

---

## 5. Reality-vs-doctrine analysis

### Strategy-expression integrity doctrine
- **Aligned:** The system is honestly refusing many low-quality conditions rather than fabricating activity.
- **Misaligned:** The `360_SCALP` B-tier dead zone is a direct expression-integrity conflict. Valid B-tier candidates are identified but structurally blocked from live expression.

### Family-aware gating doctrine
- **Aligned:** Named exemption sets exist for SMC and trend gates; the architecture is trying to be family-aware.
- **Misaligned:** The scanner still applies a generic MTF gate broadly, and live evidence shows that gate is a major suppressor. This supports the existing concern that MTF gating is not yet thesis-aware enough.

### Signal quality over signal count
- **Aligned:** Spread gating, FVG over-wide SL discards, and quiet-regime caution are quality-protective and commercially honest.
- **Misaligned:** The current funnel appears to overshoot from “quality first” into “quality expressed too rarely,” especially when B-tier main-channel signals are structurally non-dispatchable.

### Observability-first duty
- **Aligned:** The monitor now provides enough evidence to prove the engine is alive and to localize suppression layers.
- **Still incomplete:** We still do not have full per-internal-evaluator funnel telemetry across all 14 `360_SCALP` paths. Only some setup classes are visible in the current snapshot.

### Best-system-first standard
- **Aligned:** Current safety protections are generally protecting business trust from weak scalp entries in poor market quality.
- **Misaligned:** The roadmap still places meaningful weight on evaluator TP polish while the live business problem is “scanner alive, zero paid output.” That priority balance now needs adjustment.

### Business rules B1–B14
- **B5 / SMC basis:** Mostly aligned; structural quality enforcement remains strong.
- **B13 / method-specific SL/TP:** Mostly aligned in architecture; some downstream risk friction remains, but this snapshot does not prove B13 is the primary zero-output blocker.
- **B12 / system-and-data focus first:** Strongly aligned with the correct next move: stay focused on live-output truth and suppression architecture before broader feature work.

### Bottom line on doctrine alignment

The system is **partly behaving correctly**:
- It is truthfully cautious in poor scalp conditions.
- It is not hiding infrastructure failures.
- It is not posting low-grade noise just to create activity.

The system is also **partly misaligned**:
- It is over-suppressing strategy expression on the main path.
- It is carrying a confirmed B-tier governance contradiction.
- It likely remains too generic in scanner-level MTF gating for some path families.

---

## 6. Recommended action plan

### Immediate next action
**Land and deploy the strongest possible scoring/funnel telemetry (PR-10 scope or equivalent) with explicit per-setup, per-stage loss accounting for the internal `360_SCALP` evaluators.**

Reason: the live snapshot already proves the broad diagnosis, but the next engineering move should isolate exactly which of the 14 internal paths are dying at:
- channel pre-skip
- generic MTF gate
- risk stage
- post-score floor
- quiet block
- final dispatch floor

### Next 3 actions after that
1. **Elevate the `360_SCALP` B-tier dead-zone decision from “later gated idea” to active architecture review.**
   - This is no longer hypothetical; code and live evidence already prove the mismatch.
2. **Run a targeted MTF gate review on main `360_SCALP` families, especially reversal/structure paths.**
   - Focus on whether the universal scanner MTF gate is incorrectly overriding family thesis.
3. **Add a live tradable-universe view for spread-qualified pairs.**
   - Do not loosen spread standards first; measure how many pairs are genuinely tradable per cycle and whether pair selection itself should adapt.

### What should become PRs
- Telemetry/funnel visibility PR if current PR-10 does not already expose stage-loss data deeply enough.
- A narrow architecture PR for the B-tier dead-zone resolution, after owner decision on desired behavior.
- A narrow family-aware MTF-gate refinement PR, but only after telemetry confirms which families are being over-blocked.

### What should remain research only for now
- Broad loosening of spread limits
- Broad loosening of quiet-regime floors
- Broad removal of volatility gating on auxiliary channels

### What should wait for more evidence
- Any major evaluator redesign
- Any large portfolio reshuffle across all auxiliary families
- Any conclusion that the main issue is “just bad market conditions” without first resolving the confirmed downstream contradiction

---

## 7. PR recommendations

### PR-A — `PR-10+ Zero-Signal Funnel Telemetry Completion`
- **Purpose:** expose stage-by-stage losses for every internal `360_SCALP` evaluator and every active auxiliary channel.
- **Why now:** it is the fastest path from high-confidence diagnosis to surgical correction.
- **What it must not touch:** scoring formulas, thresholds, evaluator entry logic.
- **Expected impact:** converts current diagnosis from strong-but-partial into exact per-path truth.
- **Conflict risk:** low to medium, depending on overlap with current telemetry work.

### PR-B — `Resolve 360_SCALP B-Tier Dispatch Contradiction`
- **Purpose:** align paid-path dispatch policy with the declared tier model, or explicitly redefine the tier model if the owner wants only A+ on paid main.
- **Why now:** the contradiction is already confirmed by code and live monitor evidence.
- **What it must not touch:** spread gates, risk geometry, evaluator logic.
- **Expected impact:** removes a proven downstream expression defect.
- **Conflict risk:** medium, because this is governance-sensitive and may overlap with ongoing scoring discussion.

### PR-C — `Make Scanner MTF Gate Family-Aware for Main Scalp Paths`
- **Purpose:** stop a generic confluence gate from structurally over-blocking reversal/structure families that already have thesis-specific confirmation.
- **Why now:** live monitor shows MTF is one of the largest suppressors on the main paid path.
- **What it must not touch:** spread thresholds or quiet-floor policy.
- **Expected impact:** restores valid strategy expression without globally loosening quality standards.
- **Conflict risk:** medium to high, because MTF changes can create unintended signal inflation if not tightly scoped.

### PR-D — `Tradable Universe Observability for Live Spreads`
- **Purpose:** expose how many pairs are actually spread-qualified for scalp execution per cycle and by regime.
- **Why now:** spread rejection is the single biggest live suppressor and needs operational visibility.
- **What it must not touch:** execution thresholds themselves in the first PR.
- **Expected impact:** separates “bad market” from “bad universe selection.”
- **Conflict risk:** low.

---

## 8. Open risks and unknowns

- We do **not** yet have complete live per-path telemetry for all 14 internal `360_SCALP` evaluators in this single snapshot.
- The snapshot proves `LIQUIDITY_SWEEP_REVERSAL` and `SR_FLIP_RETEST` are reaching scoring, but it does not prove that every other internal path is inactive due to defect rather than market absence.
- The generic MTF gate is very likely over-tight for some families, but the exact best exemption/refinement set still needs telemetry-backed isolation.
- Scan latency is still elevated intermittently; it is secondary here, but it remains a live operational risk.
- An open PR already exists for the soft-penalty interaction fix. That fix is important, but it is **not** the strongest explanation for current zero output; if anything, the current live branch is already too silent even before fully applying evaluator-authored penalties.
- Existing repo lint/test baseline is dirty in this working tree context; this audit did not attempt unrelated repo-wide remediation.

---

## Final chief-engineer judgment

**Why no signals?**

Because the live engine is currently passing through a hostile scalp market with widespread spread disqualification, while the remaining viable `360_SCALP` candidates are then being thinned by a strong generic MTF gate, quiet-regime filtering, and a confirmed B-tier dispatch contradiction that prevents 65–79 main-path signals from expressing.

So the truthful answer is:

**Not dead infrastructure. Not one bug. Not “just bad market.”**

It is a **mixed suppression state**:
- **partly correct market caution**
- **partly over-tight downstream governance**
- **partly unresolved strategy-expression architecture mismatch**

That is the reality-first diagnosis.
