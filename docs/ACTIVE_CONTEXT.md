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

1. **Diagnose zero live signal output** — monitor shows `Signals=0`, `ScanLat=~20s`, WS healthy, suppression summary present. Root cause not yet confirmed. Highest priority before any build work proceeds.
2. **Confirm evaluator family diversity** — need evidence that more than one or two evaluator families are producing candidates in live conditions.
3. **Heartbeat file missing** — needs investigation. May indicate healthcheck or I/O issue.

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
| 1 | Diagnosis session | Trace zero-output root cause via code + monitor evidence | Now — no build gate |
| 2 | PR-A1 | Path-level observability framework | After zero-output cause confirmed |
| 3 | PR-A2 | `/why SYMBOL` deep diagnostics | After PR-A1 |
| 4 | PR-A3 | VPS Monitor path health section | After PR-A2 |
| 5 | PR-B1 | Refine `VOLUME_SURGE_BREAKOUT` | After Stage A complete |
| 6 | PR-B2 | Refine `BREAKDOWN_SHORT` | After PR-B1 |
| 7 | PR-B3 | Refine `SR_FLIP_RETEST` | After PR-B2 |
| 8 | PR-B4 | `WHALE_MOMENTUM` role review | After PR-B3 |

Full detailed roadmap: `OWNER_BRIEF.md` Part VI.

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

2026-04-10 — Initial creation as part of operating-contract upgrade (PR: full technical ownership / operating-contract upgrade).
Next update: session end of the first diagnostic session on the zero-signal issue.
