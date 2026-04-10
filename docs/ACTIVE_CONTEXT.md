# 360 Crypto Eye — Active Context (Continuity Companion)

> **Purpose:** This file is read at every Copilot session start alongside `OWNER_BRIEF.md`.
> It records current phase, active priority, known live issues, the next PR queue, and open risks.
> It is updated at every session end. It complements the canonical brief — it does not replace it.
> Keep it compact. Every field must be accurate or marked unknown.

---

## Current Phase

**Phase:** 6.1 — Live Architecture Validation (active)

Architecture correction sequence (ARCH-2 through ARCH-10) is complete.
Current work is confirming live signal output quality and evaluator family diversity before
beginning any Stage A build work (observability framework, `/why` deep diagnostics, monitor path health).

---

## Current Active Priority

1. **Diagnose zero live signal output** — monitor shows `Signals=0`, `ScanLat=~20s`, WS healthy, suppression summary present. Root cause not yet confirmed. Resolve before path refinement work begins.
2. **Confirm evaluator family diversity** — need evidence that more than one or two evaluator families are producing candidates in live conditions.
3. **Heartbeat file missing** — needs investigation. May indicate healthcheck or I/O issue.
4. **Signal-engine path quality** — once live output is confirmed, immediately begin path refinement sequence: `VOLUME_SURGE_BREAKOUT` → `BREAKDOWN_SHORT` → `SR_FLIP_RETEST` → `WHALE_MOMENTUM` role review. This is the current business-first strategic direction.

---

## Current Known Live Issues

| Issue | Severity | Status |
|---|---|---|
| `Signals=0` in live monitor output | Critical | Under investigation |
| `ScanLat=~20398ms` — elevated scan latency | High | Cause not confirmed |
| Heartbeat file missing after grace period | Medium | Needs trace |
| Evaluator family diversity unconfirmed | High | No live emit data yet |
| Same-symbol same-direction scalp dedup may discard better candidates early | Medium | Identified in code, not root-cause confirmed |

---

## Next PR Queue

| Priority | PR | Description | Gate |
|---|---|---|---|
| 1 | Diagnosis | Trace zero-output root cause via code + monitor evidence | Now — no build gate |
| 2 | PR-1 | Refine `VOLUME_SURGE_BREAKOUT` | After zero-output diagnosis |
| 3 | PR-2 | Refine `BREAKDOWN_SHORT` | After PR-1 |
| 4 | PR-3 | Refine `SR_FLIP_RETEST` | After PR-2 |
| 5 | PR-4 | `WHALE_MOMENTUM` role review and reclassification | After PR-3 |
| 6 | PR-5 | Add `CONTINUATION_LIQUIDITY_SWEEP` | After PR-1 through PR-3 stable |
| 7 | PR-6 | Add `POST_DISPLACEMENT_CONTINUATION` | After PR-5 |
| 8 | PR-7 | Add `FAILED_AUCTION_RECLAIM` | After PR-6 |
| 9 | PR-8 | Formalize path portfolio roles (core / support / specialist) | After new paths are live |

Full current roadmap: `OWNER_BRIEF.md` Part VI section 6.2.

---

## Open Risks

| Risk | Impact | Notes |
|---|---|---|
| Zero signal output cause may be multi-layer | High | Could be evaluator silence + gate rejection + suppression combined |
| Elevated scan latency root cause unknown | High | Could be I/O, pair volume, or data assembly cost |
| Session continuity gap | Medium | This file was created to address this — update it every session end |
| Stage A build not started | Medium | Must not start Stage B/C/D until Stage A complete |

---

## Last Updated

2026-04-10 — Roadmap refresh: replaced Stage A–E observability-gated expansion sequence with business-first signal-engine path roadmap. Next PR queue updated to reflect new sequence (path refinements → new path additions → portfolio formalization). Prior operating-contract upgrade (PR #97) is still the base brief version.
