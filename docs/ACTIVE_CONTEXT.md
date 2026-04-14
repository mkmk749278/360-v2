# 360 Crypto Eye — Active Context (Continuity Companion)

> **Purpose:** This file is read at every Copilot session start alongside `OWNER_BRIEF.md`.
> It records current phase, active priority, known live issues, the next PR queue, and open risks.
> It is updated at every session end. It complements the canonical brief — it does not replace it.
> Keep it compact. Every field must be accurate or marked unknown.

---

## Current Phase

**Phase:** 7 — Post-Correction Live Monitoring (active as of 2026-04-13; updated 2026-04-14)

The full correction sequence is complete. Two independent correction passes have been merged:
- **Pre-redeploy correction pass** (PR-01 through PR-09) — all merged 2026-04-11
- **Post-audit correction pass** (PR-10 through PR-18) — all merged 2026-04-12 to 2026-04-13
- **WATCHLIST lifecycle correction** (PR #144, PR #145) — merged 2026-04-14

The engine is live on VPS. The 2026-04-14 investigation confirmed and fixed the WATCHLIST lifecycle admission defect. Current task is to observe live Telegram/monitor output post-PR #144 before deciding the next technical action. Do not claim operational WATCHLIST confirmation until monitor evidence supports it.

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
| PR #144 | fix: segregate WATCHLIST 360_SCALP signals from paid active lifecycle | ✅ merged | 2026-04-14 |
| PR #145 | fix: defensive entry guard in `_format_watchlist_preview` for zero-price edge case | ✅ merged | 2026-04-14 |

---

## Current Active Priority

1. **Verify post-merge WATCHLIST behavior live** — confirm that WATCHLIST (`50–64`) signals no longer appear in paid lifecycle events (TP HIT, SL HIT, INVALIDATED, expiry posts) in Telegram or monitor output. PR #144 and PR #145 are merged on 2026-04-14; operational confirmation requires fresh live evidence.
2. **Identify duplicate lifecycle posting in live output** — the 2026-04-14 canonical audit (`docs/AUDIT_2026-04-14_REPORT_COMPARISON_AND_CANONICAL_VERDICT.md`) confirmed duplicate terminal lifecycle posting is real. It is the second confirmed defect, deferred until post-PR #144 live evidence is reviewed.
3. **Evidence-gated next PR** — raise lifecycle idempotency / duplicate-post hardening only after post-merge monitor evidence is reviewed. Do not raise speculatively.

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

## 2026-04-14 WATCHLIST Investigation Summary

Three independent audit reports were synthesised into a canonical verdict. Basis for current continuity state:

### `docs/AUDIT_2026-04-14_REPORT_COMPARISON_AND_CANONICAL_VERDICT.md` (canonical)
- **Primary confirmed defect:** WATCHLIST lifecycle admission — `WATCHLIST` (`50–64`) was documented as free-channel preview only, but runtime admitted it into the paid active lifecycle
- WATCHLIST signals were entering `_active_signals` and being managed by `TradeMonitor` as live tracked trades
- Duplicate lifecycle posting was confirmed real but classified as the second defect (not yet fixed)
- PR #144: segregates WATCHLIST from paid active lifecycle; WATCHLIST now routed to free-channel preview only; WATCHLIST not stored in `_active_signals`; scanner comment corrected; tests updated
- PR #145: defensive zero-price guard added to `_format_watchlist_preview()`

### Three source audit reports (all in `docs/`)
- `docs/AUDIT_2026-04-14_LIVE_SIGNAL_EXPRESSION_INVESTIGATION_GPT-5.4.md`
- `docs/AUDIT_2026-04-14_LIVE_SIGNAL_EXPRESSION_INVESTIGATION_GPT-5.3-CODEX.md`
- `docs/AUDIT_2026-04-14_LIVE_SIGNAL_EXPRESSION_INVESTIGATION_CLAUDE-OPUS-4.6.md`

---

## Current Known Live Issues

| Issue | Severity | Status |
|---|---|---|
| WATCHLIST signals entering paid active lifecycle | High | ✅ Fixed — PR #144 merged 2026-04-14; live verification pending |
| Duplicate lifecycle posting (SL/invalidation/expiry terminal events) | High | Confirmed real (2026-04-14 audit); fix deferred to next PR after live verification |
| Generic scanner MTF gate may be over-generic for some families | Medium | Confirmed likely; deferred behind lifecycle idempotency fix — reassess post-PR #144 monitor |
| Scan latency spikes (14.3s, 28.8s, 35.3s seen in 2026-04-13 monitor) | Medium | Root cause not confirmed; baseline 4–5s healthy |

---

## Next PR Queue

| Priority | PR | Description | Gate |
|---|---|---|---|
| 1 | — | Verify post-PR #144 live Telegram/monitor output | No gate — do this first |
| 2 | — (candidate) | Lifecycle idempotency / duplicate-post hardening | Evidence: post-PR #144 monitor confirms WATCHLIST clean; duplicate-post pattern still present |
| 3 | — (candidate) | Targeted family-aware MTF gate refinement | After lifecycle fix; evidence: MTF still dominant suppressor |

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
| WATCHLIST contamination of paid lifecycle not yet confirmed removed in live output | High | PR #144 merged; live Telegram/monitor evidence required to confirm clean |
| Duplicate terminal lifecycle posting not yet fixed | High | Confirmed real by 2026-04-14 audit; fix queued for next PR after live verification |
| MTF gate over-generic for non-trend thesis paths | Medium | Evidence-gated; reassess after lifecycle idempotency fix from post-PR #144 monitor |
| Scan latency spikes (not baseline 4-5s) | Medium | Root cause unknown; monitor to see if it stabilizes |
| Spread-quality suppression is market-condition-driven | Medium | Not directly fixable by code; may self-resolve as market conditions improve |

---

## Last Updated

2026-04-14 — ACTIVE_CONTEXT updated to reflect 2026-04-14 WATCHLIST investigation and merged PRs. PR #144 (WATCHLIST lifecycle segregation) and PR #145 (formatter defensive guard) merged. Canonical verdict: `docs/AUDIT_2026-04-14_REPORT_COMPARISON_AND_CANONICAL_VERDICT.md`. Next action: verify post-PR #144 live behavior; then lifecycle idempotency / duplicate-post hardening PR.