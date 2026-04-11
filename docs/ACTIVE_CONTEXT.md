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
Steps 1–8 complete. Zero-signal diagnosis and fix PR is the pre-step-9 blocker.
Step 9 (path-by-path portfolio tuning) remains gated on live evidence.

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
| 8 | Formalize path portfolio roles | ✅ merged (PR #106) |
| Pre-9 | Diagnose and fix zero live signal | ✅ current PR |
| 9 | Path-by-path portfolio tuning | ⏳ next (needs live signal data) |

---

## Current Active Priority

1. **Confirm live signal output is restored** — zero-signal diagnosis PR fixes three confirmed code-level blockers (see below). Monitor output should show non-zero candidate/emit counts after merge.
2. **Gather live diagnostic evidence** — once signals are flowing, collect candidate rate, emit rate, and gate-block distribution for evidence-led step-9 tuning.
3. **Step 9: Path-by-path portfolio tuning** — next roadmap item. Requires live diagnostic evidence before any threshold adjustments.

---

## Zero-Signal Diagnosis — Confirmed Root Causes and Fixes

Diagnosed in the pre-step-9 PR. Three confirmed code-level blockers:

### Blocker 1 — Missing `_evaluate_range_fade` evaluator (Critical)
- **Evidence:** 10 pre-existing test failures referencing `ScalpChannel._evaluate_range_fade`. Method did not exist.
- **Impact:** RANGE_FADE setup class is in `CHANNEL_SETUP_COMPATIBILITY["360_SCALP"]` and in the regime-setup compatibility table for CLEAN_RANGE, DIRTY_RANGE, and QUIET. With no evaluator, zero RANGE_FADE candidates were ever generated for ranging/quiet markets — the most common live market state for crypto.
- **Fix:** Implemented `_evaluate_range_fade` in `ScalpChannel`. Fires on BB extreme touch + low ADX + RSI confirmation (LONG ≤ 55, SHORT ≥ 45). BB squeeze guard blocks expansion (breakout-not-range scenario). Added RANGE_FADE to `_SMC_GATE_EXEMPT_SETUPS` and `_TREND_GATE_EXEMPT_SETUPS` in scanner (sweep/EMA alignment are architecturally wrong gates for mean-reversion).

### Blocker 2 — `_select_indicator_weights` missing `"mean_reversion"` key (High)
- **Evidence:** 6 pre-existing test failures (`KeyError: 'mean_reversion'`) in `test_phase4_adaptive_logic.py`.
- **Impact:** Any code path using the weights dict for `"mean_reversion"` would raise a `KeyError`. With RANGE_FADE now added, the `"mean_reversion"` weight (1.2 for RANGING/QUIET) is needed to correctly weight range-fade candidates in the portfolio selector.
- **Fix:** Added `"mean_reversion"` key to all regime branches of `_select_indicator_weights`. Values: VOLATILE=0.8, RANGING/QUIET=1.2 (preferred), TRENDING=0.7, default=1.0.

### Blocker 3 — MTF hard gate not tracked in suppression_counters (High observability gap)
- **Evidence:** `_prepare_signal` line 2172 returned `None, None` silently with only a debug log. Suppression summary never showed MTF as a cause. Zero-signal scans could be entirely due to MTF blocking without any visible diagnostic.
- **Impact:** Operators cannot distinguish between "no candidates from evaluators" and "candidates blocked by MTF gate". This is the primary reason zero-output conditions are silent.
- **Fix:** Added `self._suppression_counters[f"mtf_gate:{chan_name}"] += 1` and `suppression_tracker.record()` before returning at the MTF gate. MTF rejections now appear in suppression summary.

### Additional — PR09 < 50 rejection now logged (Medium observability gap)
- **Evidence:** PR09 < 50 branch returned `None` without logging.
- **Fix:** Added `log.debug()` and `self._suppression_counters[f"pr09_below50:{chan_name}"] += 1` before return. Below-threshold rejections now appear in suppression summary.

---

## Current Known Live Issues

| Issue | Severity | Status |
|---|---|---|
| Zero live signal output — root causes diagnosed and fixed | Critical | Fixed in current PR — pending merge + live verification |
| `ScanLat=~20398ms` — elevated scan latency | High | Cause not confirmed — not a code defect in signal path |
| Heartbeat file missing after grace period | Medium | Needs trace — may be related to long scan latency |
| Evaluator family diversity — RANGE_FADE now generates candidates in RANGING/QUIET | High | Partially resolved by RANGE_FADE fix — live evidence needed |
| PR09 score < 50 rejections previously silent | Medium | Fixed — now logged and counted in suppression summary |

---

## Next PR Queue

| Priority | PR | Description | Gate |
|---|---|---|---|
| 1 | PR-9 | Path-by-path portfolio tuning (evidence-led, per `ACTIVE_PATH_PORTFOLIO_ROLES`) | Live signal data required first |

Full current roadmap: `OWNER_BRIEF.md` Part VI section 6.2.

---

## Portfolio Role State (step 8 output)

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
| Zero signal output cause may be multi-layer | High | Could be evaluator silence + gate rejection + suppression combined |
| Elevated scan latency root cause unknown | High | Could be I/O, pair volume, or data assembly cost |
| Session continuity gap | Medium | This file was created to address this — update it every session end |
| Step 9 tuning requires live data | Medium | No speculative adjustments without diagnostic evidence |

---

## Last Updated

2026-04-11 — Roadmap step 8 complete: `PortfolioRole` enum and `ACTIVE_PATH_PORTFOLIO_ROLES` mapping added to `src/signal_quality.py`. All 14 active evaluators assigned explicit portfolio roles. Focused tests added to `tests/test_signal_quality.py`. Next step is path-by-path portfolio tuning (step 9) using live diagnostic data.
