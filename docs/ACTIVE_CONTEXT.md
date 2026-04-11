# 360 Crypto Eye — Active Context (Continuity Companion)

> **Purpose:** This file is read at every Copilot session start alongside `OWNER_BRIEF.md`.
> It records current phase, active priority, known live issues, the next PR queue, and open risks.
> It is updated at every session end. It complements the canonical brief — it does not replace it.
> Keep it compact. Every field must be accurate or marked unknown.

---

## Current Phase

**Phase:** 6.1 — Live Architecture Validation (active)

Architecture correction sequence (ARCH-2 through ARCH-10) is complete.
Active roadmap is the business-first signal-engine path sequence (OWNER_BRIEF.md Part VI §6.2).
Steps 1–8 complete. Next step is step 9 (path-by-path portfolio tuning).

### Roadmap completion state

| Step | Description | Status |
|---|---|---|
| 1 | Refine `VOLUME_SURGE_BREAKOUT` | ✅ merged |
| 2 | Refine `BREAKDOWN_SHORT` | ✅ merged |
| 3 | Refine `SR_FLIP_RETEST` | ✅ merged |
| 4 | Review `WHALE_MOMENTUM` role | ✅ merged |
| 5 | Add `CONTINUATION_LIQUIDITY_SWEEP` | ✅ merged |
| 6 | Add `POST_DISPLACEMENT_CONTINUATION` | ✅ merged |
| 7 | Add `FAILED_AUCTION_RECLAIM` | ✅ merged (PR #105) |
| 8 | Formalize path portfolio roles | ✅ merged (current PR) |
| 9 | Path-by-path portfolio tuning | ⏳ next |

---

## Current Active Priority

1. **Diagnose zero live signal output** — monitor shows `Signals=0`, `ScanLat=~20s`, WS healthy, suppression summary present. Root cause not yet confirmed.
2. **Confirm evaluator family diversity** — need evidence that more than one or two evaluator families are producing candidates in live conditions.
3. **Heartbeat file missing** — needs investigation. May indicate healthcheck or I/O issue.
4. **Step 9: Path-by-path portfolio tuning** — next roadmap item. Requires live diagnostic evidence (candidate rate, emit rate, gate-block rate, outcome distribution) before any threshold adjustments.

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
| 1 | PR-9 | Path-by-path portfolio tuning (evidence-led, per `ACTIVE_PATH_PORTFOLIO_ROLES`) | Live data required first |

Full current roadmap: `OWNER_BRIEF.md` Part VI section 6.2.

---

## Portfolio Role State (step 8 output)

Introduced in `src/signal_quality.py`:
- `PortfolioRole` enum: `core`, `support`, `specialist`
- `ACTIVE_PATH_PORTFOLIO_ROLES` dict: explicit role for all 14 active evaluators
- `APPROVED_PORTFOLIO_ROLES` frozenset: taxonomy guard for future additions

Role assignments:
- **core (6):** `LIQUIDITY_SWEEP_REVERSAL`, `TREND_PULLBACK_EMA`, `VOLUME_SURGE_BREAKOUT`, `BREAKDOWN_SHORT`, `CONTINUATION_LIQUIDITY_SWEEP`, `POST_DISPLACEMENT_CONTINUATION`
- **support (5):** `LIQUIDATION_REVERSAL`, `SR_FLIP_RETEST`, `DIVERGENCE_CONTINUATION`, `OPENING_RANGE_BREAKOUT`, `FAILED_AUCTION_RECLAIM`
- **specialist (3):** `WHALE_MOMENTUM`, `FUNDING_EXTREME_SIGNAL`, `QUIET_COMPRESSION_BREAK`

---

## Open Risks

| Risk | Impact | Notes |
|---|---|---|
| Zero signal output cause may be multi-layer | High | Could be evaluator silence + gate rejection + suppression combined |
| Elevated scan latency root cause unknown | High | Could be I/O, pair volume, or data assembly cost |
| Session continuity gap | Medium | This file was created to address this — update it every session end |
| Step 9 tuning requires live data | Medium | No speculative adjustments without diagnostic evidence |

---

## Last Updated

2026-04-11 — Roadmap step 8 complete: `PortfolioRole` enum and `ACTIVE_PATH_PORTFOLIO_ROLES` mapping added to `src/signal_quality.py`. All 14 active evaluators assigned explicit portfolio roles. Focused tests added to `tests/test_signal_quality.py`. Next step is path-by-path portfolio tuning (step 9) using live diagnostic data.
