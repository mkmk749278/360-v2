# 360 Crypto Eye — Active Context (Continuity Companion)

> **Purpose:** This file is read at every Copilot session start alongside `OWNER_BRIEF.md`.
> It records current phase, active priority, known live issues, the next PR queue, and open risks.
> It is updated at every session end. It complements the canonical brief — it does not replace it.
> Keep it compact. Every field must be accurate or marked unknown.

---

## Current Phase

**Phase:** 6.2 — Post-Audit Correction Pass (active)

Two independent signal engine audits were conducted on 2026-04-12 (Audit B: deep codebase analysis, 628 lines; Audit C: GPT-5, 396 lines). Both audits agree: **do not redeploy yet — one more correction pass required**.

The previous correction pass (PR-01 through PR-09) is **complete and merged**. The current roadmap addresses all remaining findings from both 2026-04-12 audits.

### Previous Roadmap (Complete)

| Step | Description | Status |
|---|---|---|
| 1 | Refine `VOLUME_SURGE_BREAKOUT` | ✅ merged |
| 2 | Refine `BREAKDOWN_SHORT` | ✅ merged |
| 3 | Refine `SR_FLIP_RETEST` | ✅ merged |
| 4 | Review `WHALE_MOMENTUM` role | ✅ merged |
| 5 | Add `CONTINUATION_LIQUIDITY_SWEEP` | ✅ merged |
| 6 | Add `POST_DISPLACEMENT_CONTINUATION` | ✅ merged |
| 7 | Add `FAILED_AUCTION_RECLAIM` | ✅ merged (PR #105) |
| 8 | Formalize path portfolio roles | ✅ merged (PR #106) |
| Pre-9 | Diagnose zero live signal — observability fix | ✅ merged |
| PR-01–09 | Pre-redeploy correction pass (identity, SL/TP, dedup, gates, ORB, cleanup) | ✅ all merged |

### Current Post-Audit Correction Roadmap

| PR | Phase | Title | Status | Gate |
|---|---|---|---|---|
| **PR-10** | A | Scoring Diagnostic Telemetry | 🔄 Agent running | None |
| **PR-11** | B | LIQUIDATION_REVERSAL Fibonacci Retrace TP (B13) | 🔄 Agent running | None |
| **PR-12** | B | WHALE_MOMENTUM Evaluator TP (B13) | 🔄 Agent running | None |
| **PR-13** | B | DIVERGENCE_CONTINUATION Evaluator TP (B13) | 🔄 Agent running | None |
| **PR-14** | C | RANGE_FADE Dead Code + FUNDING_EXTREME Protection | ⏳ Next | None |
| **PR-15** | C | Soft-Penalty-After-Scoring Interaction Fix | ⏳ Next | None |
| **PR-16** | C | WHALE_MOMENTUM QUIET Regime Block | ⏳ Next | PR-12 |
| **PR-17** | C | `valid_for_minutes` Preservation | ⏳ Next | None |
| **PR-18** | D | Regime-Affinity for Non-Sweep Paths | ⏳ Gated | PR-10 data |
| **PR-19** | D | B-Tier Dead Zone Resolution | ⏳ Gated | PR-10 data + discuss |
| **PR-20** | D | Family Thesis Adjustments for Non-Sweep | ⏳ Gated | PR-18 data |
| **PR-21** | E | Post-Correction Audit Report | ⏳ Final | All above |
| **PR-22** | E | OWNER_BRIEF + ACTIVE_CONTEXT Final Refresh | ⏳ Final | PR-21 |

---

## Current Active Priority

1. **Phase A+B: 4 parallel agents running** — PR-10 (telemetry), PR-11 (LIQUIDATION_REVERSAL TP), PR-12 (WHALE_MOMENTUM TP), PR-13 (DIVERGENCE_CONTINUATION TP). All independent, no dependencies.
2. **Review each PR against §1.7 checklist** as agents complete, then merge.
3. **Launch Phase C** (PR-14 through PR-17) immediately after Phase A+B merges.
4. **Phase D is gated** on PR-10 live diagnostic data — resolves the Audit B vs GPT-5 divergence on scoring funnel bias.

---

## 2026-04-12 Dual Audit Summary

### Consensus (both audits agree)
- Do not redeploy yet — one more correction pass
- Engine has strong evaluator designs — core architecture is sound
- 3 evaluators violate B13 (LIQUIDATION_REVERSAL, WHALE_MOMENTUM, DIVERGENCE_CONTINUATION lack evaluator TP)
- `CONTINUATION_LIQUIDITY_SWEEP`, `VOLUME_SURGE_BREAKOUT`, `BREAKDOWN_SHORT` are universally trusted
- `OPENING_RANGE_BREAKOUT` disabled correctly, needs rebuild
- RANGE_FADE dead code should be removed
- FUNDING_EXTREME_SIGNAL missing from protection sets

### Key divergence
- **Audit B** says 9 of 14 paths are deploy-ready; fix TPs and deploy
- **GPT-5** says only 3-4 paths are deploy-ready; scoring funnel structurally starves non-sweep paths
- **Resolution:** PR-10 diagnostic telemetry will provide live evidence (per-path scoring distributions) to determine which diagnosis is correct

### Unique findings per audit
- **Audit B only:** soft-penalty-after-scoring interaction bug, `valid_for_minutes` overwrite, FUNDING_EXTREME protection gap
- **GPT-5 only:** B-tier dead zone (65-79 signals go nowhere), regime-affinity gaps for non-sweep paths, MTF gate not thesis-aware

---

## Current Known Live Issues

| Issue | Severity | Status |
|---|---|---|
| Zero live signal output — root cause multi-layer | Critical | Observability improved; diagnostic telemetry (PR-10) in flight |
| 3 evaluators violate B13 (no evaluator TP) | High | PR-11, PR-12, PR-13 agents running |
| RANGE_FADE dead code in scanner | Low | PR-14 queued |
| FUNDING_EXTREME_SIGNAL not in protection sets | Medium | PR-14 queued |
| Soft-penalty applied after scoring floor check | Medium | PR-15 queued |
| `valid_for_minutes` overwritten by channel defaults | Medium | PR-17 queued |
| Scoring funnel may starve non-sweep paths | High | Unconfirmed — PR-10 data will resolve |
| B-tier dead zone (65-79 scores suppressed) | Medium | Unconfirmed — PR-19 architectural discussion needed |
| `ScanLat=~20398ms` — elevated scan latency | High | Root cause not confirmed |
| Heartbeat file missing after grace period | Medium | Needs trace — may be related to scan latency |

---

## Next PR Queue

| Priority | PR | Description | Gate |
|---|---|---|---|
| 1 | PR-10 | Scoring diagnostic telemetry | 🔄 In flight |
| 2 | PR-11 | LIQUIDATION_REVERSAL Fibonacci TP | 🔄 In flight |
| 3 | PR-12 | WHALE_MOMENTUM evaluator TP | 🔄 In flight |
| 4 | PR-13 | DIVERGENCE_CONTINUATION evaluator TP | 🔄 In flight |
| 5 | PR-14 | RANGE_FADE dead code + FUNDING_EXTREME protection | After Phase B |
| 6 | PR-15 | Soft-penalty-after-scoring fix | After Phase B |
| 7 | PR-16 | WHALE_MOMENTUM QUIET block | After PR-12 |
| 8 | PR-17 | `valid_for_minutes` preservation | After Phase B |
| 9 | PR-18–20 | Scoring corrections (gated on evidence) | PR-10 live data |
| 10 | PR-21–22 | Post-correction audit + doc refresh | After all above |

Full roadmap: `OWNER_BRIEF.md` Part VI section 6.2.

---

## Portfolio Role State (unchanged from step 8)

Introduced in `src/signal_quality.py`:
- `PortfolioRole` enum: `core`, `support`, `specialist`
- `ACTIVE_PATH_PORTFOLIO_ROLES` dict: explicit role for all 14 active evaluators
- `APPROVED_PORTFOLIO_ROLES` frozenset: taxonomy guard for future additions

Role assignments:
- **core (7):** `LIQUIDITY_SWEEP_REVERSAL`, `TREND_PULLBACK_EMA`, `VOLUME_SURGE_BREAKOUT`, `BREAKDOWN_SHORT`, `SR_FLIP_RETEST`, `CONTINUATION_LIQUIDITY_SWEEP`, `POST_DISPLACEMENT_CONTINUATION`
- **support (4):** `LIQUIDATION_REVERSAL`, `DIVERGENCE_CONTINUATION`, `OPENING_RANGE_BREAKOUT`, `FAILED_AUCTION_RECLAIM`
- **specialist (3):** `WHALE_MOMENTUM`, `FUNDING_EXTREME_SIGNAL`, `QUIET_COMPRESSION_BREAK`

---

## Open Risks

| Risk | Impact | Notes |
|---|---|---|
| Zero signal output root cause multi-layer | High | PR-10 telemetry will isolate which layer dominates |
| GPT-5 scoring funnel hypothesis unconfirmed | High | Phase D corrections gated on evidence — no speculative changes |
| B-tier dead zone may suppress 65-79 signals | Medium | Architectural decision needed (PR-19) — owner discussion required |
| Elevated scan latency root cause unknown | High | Could be I/O, pair volume, or data assembly cost |
| 4 agents running in parallel — merge conflicts possible | Medium | All touch different files/evaluators — conflicts unlikely but review carefully |

---

## Last Updated

2026-04-12 — Post-audit correction roadmap established. Two audits analyzed (Audit B + GPT-5). Unified 13-PR roadmap created (PR-10 through PR-22). Phase A+B (4 PRs) launched in parallel. OWNER_BRIEF.md Part II, VI, VII updated to reflect post-audit state.