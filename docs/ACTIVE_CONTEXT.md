# 360 Crypto Eye — Active Context (Continuity Companion)

> **Purpose:** This file is read at every Copilot session start alongside `OWNER_BRIEF.md`.
> It records current phase, active priority, known live issues, the next PR queue, and open risks.
> It is updated at every session end. It complements the canonical brief — it does not replace it.
> Keep it compact. Every field must be accurate or marked unknown.

---

## Current Phase

**Phase:** 7 — Post-Correction Live Monitoring (active as of 2026-04-13)

The full correction sequence is complete. Two independent correction passes have been merged:
- **Pre-redeploy correction pass** (PR-01 through PR-09) — all merged 2026-04-11
- **Post-audit correction pass** (PR-10 through PR-18) — all merged 2026-04-12 to 2026-04-13

The engine is live on VPS. Current task is to observe live monitor output after PR-18 before deciding the next technical action. Do not claim successful live recovery until monitor evidence supports it.

### Completed Roadmap (all merged)

| PR | Description | Status | Merged |
|---|---|---|---|
| PR-01 | Preserve evaluator identity, penalties, path metadata | ✅ merged | 2026-04-11 |
| PR-02 | Preserve structural SL/TP intent for top-tier paths | ✅ merged | 2026-04-11 |
| PR-03 | Quality-ranked same-direction arbitration for `360_SCALP` | ✅ merged | 2026-04-11 |
| PR-04 | Disable auxiliary paid-channel paths by default | ✅ merged | 2026-04-11 |
| PR-05 | Fix gate-policy mismatches (TREND_PULLBACK, WHALE, FAR) | ✅ merged | 2026-04-11 |
| PR-06 | Disable OPENING_RANGE_BREAKOUT from trusted portfolio | ✅ merged | 2026-04-11 |
| PR-07 | Specialist-path quality tuning (FUNDING_EXTREME TP1, WHALE SL) | ✅ merged | 2026-04-11 |
| PR-08 | DIVERGENCE_CONTINUATION scoring alignment | ✅ merged | 2026-04-11 |
| PR-09 | Residual cleanup / final architecture polish | ✅ merged | 2026-04-11 |
| PR-10 | Per-setup-class scoring tier telemetry | ✅ merged | 2026-04-12 |
| PR-11 | LIQUIDATION_REVERSAL Fibonacci retrace TP + structural protection (B13) | ✅ merged | 2026-04-12 |
| PR-12 | WHALE_MOMENTUM evaluator-owned TP targets (B13) | ✅ merged | 2026-04-12 |
| PR-13 | DIVERGENCE_CONTINUATION swing-based TP + structural protection (B13) | ✅ merged | 2026-04-12 |
| — | Heartbeat path mismatch fix | ✅ merged | 2026-04-13 |
| PR-14 | Remove RANGE_FADE dead code + FUNDING_EXTREME_SIGNAL SL/TP protection | ✅ merged | 2026-04-13 |
| PR-15 | Fix evaluator soft-penalty not applied post-scoring; stale tier in floor gates | ✅ merged | 2026-04-13 |
| PR-16 | Hard-block WHALE_MOMENTUM in QUIET regime | ✅ merged | 2026-04-13 |
| PR-17 | Preserve evaluator-authored `valid_for_minutes` through scanner pipeline | ✅ merged | 2026-04-13 |
| PR-18 | Align `360_SCALP` tier semantics with actual dispatch (A+/B/WATCHLIST) | ✅ merged | 2026-04-13 |

---

## Current Active Priority

1. **Observe live monitor after PR-18** — check whether B-tier signals (65–79) are now dispatching and whether WATCHLIST handling is now preserved as intended downstream. Compare suppressor counts before and after.
2. **Identify dominant suppressor post-PR-18** — confirmed pre-PR-18 suppressors: spread-quality rejection (~32–60 pairs/cycle), MTF gating (~14/cycle), quiet-regime floor. Determine if the pattern changes.
3. **Evidence-gated next action** — if MTF gating remains the dominant paid-channel suppressor, prepare a targeted family-aware MTF gate refinement PR. Do not raise this until post-PR-18 evidence is reviewed.

---

## 2026-04-13 Zero-Signal Audit Summary

Two independent audit documents now exist in `docs/`:

### `docs/AUDIT_2026-04-13_ZERO_SIGNAL_DIAGNOSIS_GPT-5.4.md`
- Engine is alive, scanning, generating real candidates; zero output is suppression-driven, not infrastructure failure
- Dominant suppressors (confirmed from live monitor 2026-04-13 06:49 UTC):
  - `pair_quality:spread too wide` — 60 pairs/cycle peak
  - `mtf_gate:360_SCALP` — 14/cycle peak
  - `volatile_unsuitable:360_SCALP_FVG` / `_DIVERGENCE` / `_ORDERBLOCK` — 13/cycle peak each
  - `QUIET_SCALP_BLOCK` — repeated at 63.0, 62.3, 61.2, 60.3, 56.7, 55.3, 49.7 confidence
  - `score_65to79:LIQUIDITY_SWEEP_REVERSAL` — repeated (B-tier dead zone, now fixed by PR-18)

### `docs/AUDIT_2026-04-13_ZERO_SIGNAL_EXECUTION_PLAN_GPT-5.3-Codex.md`
- Confirmed all GPT-5.4 diagnoses via independent code verification
- Identified second contradiction: WATCHLIST semantics preserved in scanner but destroyed by router (now fixed by PR-18)
- Recommended PR-18 as the single best immediate next move (implemented and merged)
- Classified spread loosening, quiet-floor loosening, volatile-gate removal as "still too speculative" — do not pursue without evidence

---

## Current Known Live Issues

| Issue | Severity | Status |
|---|---|---|
| Zero live signal output — suppression-driven, not infrastructure failure | High | Monitoring post-PR-18; B-tier/WATCHLIST fix in place |
| Generic scanner MTF gate may be over-generic for some families | Medium | Confirmed strongly likely; evidence-gated — check post-PR-18 monitor |
| `score_65to79` signals now dispatching? | Medium | Unknown — observe after PR-18 deploys |
| Scan latency spikes (14.3s, 28.8s, 35.3s seen in 2026-04-13 monitor) | Medium | Root cause not confirmed; baseline 4–5s healthy |

---

## Next PR Queue

| Priority | PR | Description | Gate |
|---|---|---|---|
| 1 | — | Review post-PR-18 live monitor output | No gate — do this first |
| 2 | PR-19 (candidate) | Targeted family-aware MTF gate refinement | Evidence: MTF still dominant after PR-18 |
| 3 | — | Re-assess remaining suppressors from post-PR-19 monitor | After PR-19 if raised |

**What stays deferred (no evidence gate yet):**
- broad spread threshold loosening
- broad quiet-floor loosening
- global volatile-gate removal for auxiliary channels
- major evaluator redesigns

---

## Portfolio Role State (unchanged from step 8)

Introduced in `src/signal_quality.py`:
- `PortfolioRole` enum: `core`, `support`, `specialist`
- `ACTIVE_PATH_PORTFOLIO_ROLES` dict: explicit role for all 14 active evaluators
- `APPROVED_PORTFOLIO_ROLES` frozenset: taxonomy guard for future additions

Role assignments:
- **core (7):** `LIQUIDITY_SWEEP_REVERSAL`, `TREND_PULLBACK_EMA`, `VOLUME_SURGE_BREAKOUT`, `BREAKDOWN_SHORT`, `SR_FLIP_RETEST`, `CONTINUATION_LIQUIDITY_SWEEP`, `POST_DISPLACEMENT_CONTINUATION`
- **support (4):** `LIQUIDATION_REVERSAL`, `DIVERGENCE_CONTINUATION`, `OPENING_RANGE_BREAKOUT` (disabled from trusted portfolio), `FAILED_AUCTION_RECLAIM`
- **specialist (3):** `WHALE_MOMENTUM`, `FUNDING_EXTREME_SIGNAL`, `QUIET_COMPRESSION_BREAK`

---

## Open Risks

| Risk | Impact | Notes |
|---|---|---|
| Zero signal output not yet confirmed resolved | High | PR-18 corrected dispatch; live evidence required post-deploy |
| MTF gate over-generic for non-trend thesis paths | Medium | Evidence-gated; do not change without post-PR-18 confirmation |
| Scan latency spikes (not baseline 4-5s) | Medium | Root cause unknown; monitor to see if it stabilizes |
| Spread-quality suppression is market-condition-driven | Medium | Not directly fixable by code; may self-resolve as market conditions improve |

---

## Last Updated

2026-04-13 — Full ACTIVE_CONTEXT refresh. Correction pass (PR-01 through PR-18) confirmed complete. Phase changed to post-correction live monitoring. Next action: review post-PR-18 monitor output. Zero-signal diagnosis audit documents summarized.