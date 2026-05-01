# ACTIVE CONTEXT
*Updated: 2026-05-02 — Regime classifier recalibration + component-score histogram (Tier-2 monitor)*

---

## Current Phase
**Phase 2 — Quality + Volume Tuning**
Post-audit instrumentation revealed the dominant signal-flow constraint is
NOT what every prior audit assumed.  The 14-path audit is closed; we now have
the data to make principled tuning decisions instead of grep-driven guesses.

### Latest live monitor truth (2026-04-30 12:54 UTC, 24h window)
- **Total log lines processed:** 23.2 M (vs 49 in the pre-PR-#262 run — log
  source fix worked as designed)
- **Regime distribution:** VOLATILE 83.9% / QUIET 16.1% / TRENDING 0.0%.
  The "99.7% QUIET" assumption that drove every prior audit was wrong.  Most
  paths block on VOLATILE (VSB/BDS/ORB/WHALE/FAR/PDC), and 5% Bollinger width
  is routine mid-cap activity, not exceptional volatility.  **This was the
  miscalibration, not the market.**
- **Funnel health:** evaluators generate plenty of candidates — FAR 387k,
  SR_FLIP 211k, QCB 90k, LSR 86k.  The bottleneck is the confidence gate.
- **QUIET_SCALP_BLOCK avg gap to threshold:** 14.83 pts (samples=19,085).
  Candidates are scoring ~45-50 vs threshold 60 — structurally far away,
  not "tunable away" by lowering threshold.  Lowering would flood paid
  channels with low-conviction garbage.

This session (2026-05-02 — Phase 2 kickoff):

- **🔴 Regime classifier recalibration — `_BB_WIDTH_VOLATILE_PCT` 5.0 → 8.0**
  (`src/regime.py:103`).  Live monitor showed 83.9% VOLATILE; cross-checked
  against typical crypto BB widths (mid-cap pairs sit at 4-7% during routine
  ranging/trending activity), confirmed 5% threshold was systematically
  mistagging normal action as VOLATILE.  Bumped default to 8.0 + made
  env-overridable as `BB_WIDTH_VOLATILE_PCT` per B8 (matching the
  `BB_WIDTH_QUIET_PCT` convention immediately below).  4 new tests in
  `tests/test_regime_context.py::TestBBWidthVolatileThresholdRecalibration`.
  **Expected impact:** unlocks regime-blocked paths (VSB / BDS / ORB / WHALE /
  FAR / PDC) on the bulk of pairs that were falsely VOLATILE.  Worst case:
  fewer signals shift the regime classifier from a hard-blocking VOLATILE to
  a path-decided RANGING/TRENDING — paths still have to clear their own
  evaluator gates.

- **🟢 Tier-2 monitor upgrade — confidence component-score histogram**
  (`src/runtime_truth_report.py::parse_confidence_gate_components_from_logs`).
  Extracts the full numeric breakdown already emitted by every
  `confidence_gate ...` log line: avg final / threshold / gap, raw +
  composite, total penalty, AND per-component averages
  (market / execution / risk / thesis_adj).  Renders as a markdown table
  in the truth report.  Once the next monitor run captures post-fix data,
  this section will tell us *where* the 14.83-pt gap is sourced from —
  whether to retune component weights, fix specific scorers, or accept that
  the threshold is right and signals are correctly being filtered.

### What's NOT in this work-stream (deliberate)

- No threshold lowering anywhere.  With a 14.83-pt confidence gap, dropping
  the floor to manufacture volume is revenue-destroying.  Component data first.
- No new evaluator paths.  Existing 14 generate 1.2M+ candidates per 24h;
  scoring is the binding constraint, not setup variety.
- No watchlist tier (50-64) → paid channel promotion.  B5 prohibits it.

### Open queue for next session

After the next monitor run (post-regime fix deploy):
1. Verify regime distribution shifts (target: VOLATILE ≤30%, RANGING/TRENDING
   pick up the slack).
2. Read the confidence component breakdown table and identify which
   component(s) are systematically underscored.
3. If VSB/BDS/ORB/WHALE start emitting candidates, watch their quality —
   they were silent for so long that any regression would show fast.

### 2026-05-04: Scalping doctrine clarified — soft penalty, not hard veto

Owner-promoted CTE thinking on 2026-05-04 corrected an over-engineered
direction in the Phase 2 entry-quality audit.  PRs #266 (SR_FLIP) and
#267 (QCB) shipped HARD HTF vetoes — directly blocking signals where
1H AND 4H both opposed direction.

Owner's reality check: this is a SCALPING business.  Top-75 USDT-M pairs
are highly correlated to BTC.  A hard HTF veto across all paths would
force directional bias — only LONGs in BTC uptrends, only SHORTs in
downtrends.  That's trend-following, not scalping.  Counter-trend scalps
(short at resistance during uptrend pullbacks, long at support during
downtrend bounces) are legitimate scalp products.

**Corrected doctrine:** HTF mismatch is a SOFT confidence penalty, not
a hard reject.  Signal still generates; scoring tier decides.

**OWNER_BRIEF.md §2.1a "Scalping Doctrine"** added — direction-agnostic,
fast in/out, soft penalties over hard blocks, per-path HTF policy table.
**CLAUDE.md** updated with system-owner-not-assistant framing.

### 2026-05-04: Phase 2 path audit #3 — FAILED_AUCTION_RECLAIM (entry quality, soft-penalty doctrine)

Third path. First path to follow the corrected scalping doctrine.

Shipped: `_FAR_HTF_MISMATCH_PENALTY` (default 6.0 confidence pts) attached
when 1H AND 4H BOTH oppose direction.  Env-overridable; set to 0 to disable.
Signal still generates; scoring tier decides whether it clears.

Known weakness deferred to focused follow-up: FAR's level detection uses
scalar `max(highs[-26:-7])` / `min(lows)` — a single wick can define the
"structural" level.  SR_FLIP's clustered+VP-anchored `_sr_detect_levels()`
is much more robust.  Porting FAR to the same is a larger change that
would significantly affect signal generation rate; needs proper before/after
testing and a focused PR.

**Follow-up shipped (PR #269):** SR_FLIP and QCB hard HTF vetoes
downgraded to the same soft-penalty pattern shipped here for FAR.  All
three structural-reversion paths now share a consistent doctrine via
the `_classify_htf_trend` helper.  Env vars renamed:
`SR_FLIP_HTF_VETO_ENABLED` → `SR_FLIP_HTF_MISMATCH_PENALTY` (default 6.0,
set 0 to disable) and `QCB_HTF_VETO_ENABLED` → `QCB_HTF_MISMATCH_PENALTY`
(same default).

6 new tests in `TestFailedAuctionReclaimPhase2EntryQuality` — all assert
signal STILL GENERATES on HTF mismatch (only the soft penalty attaches).

### 2026-05-04: Phase 2 path audit #2 — QUIET_COMPRESSION_BREAK (entry quality)

Second-most-emitting path (10-179 signals/window post-recalibration).
Audit found the same HTF-veto gap as SR_FLIP — no 1H/4H trend check
at the evaluator level.  Other checklist items mostly ✅ or 🟡 deferred.

Shipped:
- HTF direction veto via reused `_classify_htf_trend` helper.  Conservative
  semantic: block only when BOTH 1H AND 4H oppose signal direction.
- Env-overridable as `QCB_HTF_VETO_ENABLED` (B8).

Deferred (will revisit if data shows need):
- Breakout-candle body quality check (would need fixture redesign)
- Closed-candle volume confirmation (same)
- Soft RSI layering (current hard bounds 48-75 / 25-52 are reasonable)

6 new tests in `TestQuietCompressionBreakPhase2EntryQuality`:
veto fires LONG-into-bearish-HTF, mirror SHORT-into-bullish, mixed-HTF
doesn't fire, missing data degrades gracefully, aligned signal not vetoed,
env override toggles.

3397 pass / 0 fail (was 3391 = +6, zero regressions).

### 2026-05-04: Phase 2 path audit #1 — SR_FLIP_RETEST (entry quality)

Owner-driven per-path audit (mirrors the 14-path workflow from yesterday)
focused on entry-generation mechanics rather than scoring/SL geometry.
SR_FLIP_RETEST audited first because it's the highest-emit path (67-105
signals/window) and has the canonical XAG bad-entry case.

Checklist score: most areas ✅ (level detection sophisticated, EMA/RSI gates
layered, FVG/OB regime-aware) but **2 defects to fix**:

1. 🔴 No HTF direction check — XAG SHORT fired in clear 1H+4H uptrend
2. 🔴 `close <= 0` emits `breakout_not_found` (family bug from yesterday)

Shipped:
- HTF direction veto: block when 1H AND 4H BOTH oppose signal direction.
  Conservative — mixed HTF passes through, only unambiguous mismatches
  vetoed.  Env-overridable as `SR_FLIP_HTF_VETO_ENABLED` per B8.
- `invalid_price` token replaces `breakout_not_found` on 0-close.
- New helper `ScalpChannel._classify_htf_trend()` mirrors `src.mtf._classify_trend`
  contract for per-evaluator HTF checks (will be reused by the rest of the
  Phase 2 audit).

7 new tests in `TestSrFlipRetestPhase2EntryQuality`:
veto-fires for SHORT-into-1H+4H-BULLISH, mirror for LONG-into-bearish,
veto-doesn't-fire on mixed HTF, missing HTF data degrades gracefully,
aligned signal not vetoed, env-override toggles, invalid_price token.

3391 pass / 0 fail (was 3384 = +7, zero regressions).

Out of scope for this PR (deferred):
- Entry zone depth (XAG LONG case — "right direction, wrong timing")
- ADX/momentum at evaluator level (intentional for reclaim setup)
- Setup classification doc for invalidation tuning (Phase 3 work)

### 2026-05-04: Phase 3 — Invalidation Quality Audit (instrumentation only)

Owner observation crystallised the next priority: telegram dump showed every
signal dies at exactly T+10 min via `INVALIDATION_MIN_AGE_SECONDS=600` grace
expiring + momentum gate firing immediately.  My initial proposal was to
exempt structural setups from momentum invalidation — but charts showed
those kills were often *protective* (saving signals from going to SL on
wrong-direction entries).

The honest answer is we don't actually know what fraction of kills are
protective vs premature.  Without that, every threshold-tuning decision is
opinion-driven.

**Phase 3a — instrumentation shipped (this PR):**
- `src/invalidation_audit.py` — `record_invalidation()` / `classify_record()`
  pure-function classifier + `classify_pending_records()` periodic worker.
  Each kill is recorded with entry/SL/TP1; 30 min later, post-kill OHLC is
  examined and the kill is labelled PROTECTIVE / PREMATURE / NEUTRAL /
  INSUFFICIENT_DATA.
- Hooked into `trade_monitor.py` invalidation path with broad-exception
  guard (audit must never break a close).
- Periodic loop in `main.py::_invalidation_audit_loop` runs every 5 min,
  uses 1m candles from the live data store (assumption: each candle = 60s).
- Workflow extracts `data/invalidation_records.json` from the engine
  container; truth report renders a histogram per setup × kill_reason
  family.  When net PROTECTIVE > PREMATURE, surfaces "Net-helping";
  otherwise "Net-hurting".

**Phase 3b/3c — held until data lands:**
- Entry quality audit per evaluator (HTF direction filter on SR_FLIP / QCB)
- Invalidation tuning based on actual classified data (PnL-aware vs
  blanket exemption — to be decided by data, not opinion)

23 new tests across `test_invalidation_audit.py` (16) and
`test_runtime_truth_report.py` (5 audit-section tests + 2 misc).  3384 pass
/ 0 fail (was 3361 = +23 net).  Zero regressions.

### 2026-05-03 follow-up: risk-component recalibration shipped

First post-deploy monitor run (2026-04-30 13:40 UTC) gave us actionable component
data via PR #263's Tier-2 instrumentation.  Headline finding:

**Risk component averages 12.8-14.3 across every path** while Market averages
~21 and Execution ~19 (out of 20).  Risk was the structural deficit pulling
signals under the confidence threshold.

Root cause was a **scoring-model miscalibration**: the risk_score formula
(`8.0 + min(R, 2.5) * 4.8`) demanded 2.5R for full credit — swing-style targets.
360_SCALP's audit-shipped SL geometry was deliberately built to keep TP1 at
1.0-1.8R for tight risk control.  The scorer was penalising the geometry we
deliberately built.

Owner reality-check (2026-05-03): "think reality of crypto market, if it's
correct proceed and update Owner brief."  Validated:
- Industry-standard scalp signals: 1.5R typical, 2.0R strong, 2.5R+ exceptional
- 60-70% win rate at 1.2-1.8R = positive expectancy for paid signals
- 2.5R cap is swing-trading territory, not scalp

Recalibration: `8.0 + min(R, 2.0) * 6.0`, env-overridable as `RISK_SCORE_BASE`
/ `RISK_SCORE_R_CAP` / `RISK_SCORE_R_MULT` per B8.

Per-R impact (delta to score):
- 1.0R: 12.8 → 14.0 (+1.2)
- 1.5R: 15.2 → 17.0 (+1.8) ← typical signal
- 2.0R: 17.6 → 20.0 (+2.4, max credit)
- 2.5R: 20.0 → 20.0 (capped)

Aggregate effect: typical 5-10 pt boost across the funnel for signals
already passing structural gates.  Closes roughly half of the 14.83-pt
QUIET_SCALP_BLOCK gap without lowering any threshold.  6 new tests in
`TestRiskScoreRecalibration`.  3361 pass / 0 fail (was 3355 = +6 new tests,
zero regressions).

This was a B10 scoring-model change requiring owner sign-off — captured here
and in OWNER_BRIEF for audit trail.

---

## Prior session (2026-05-02 — path audit #14, FINAL of 14)

**🏁 The 14-evaluator deep audit is complete.**  All 14 paths reviewed end-to-end,
defects fixed, tests added, OWNER_BRIEF table populated.  Family-bug pattern
addressed across the entire scoring surface: telemetry-truth tokens
(`invalid_price`, `atr_invalid`, `feature_disabled`); SL geometry with
close-relative + 1×ATR floor; TP1 ATR-adaptive caps where structurally
appropriate; partial-candle volume gates removed; per-channel/per-setup
SL caps reconciled; QUIET-regime exempts (FUNDING) where confidence justifies.

- **FAILED_AUCTION_RECLAIM deep dive** (`_evaluate_failed_auction_reclaim`,
  `src/channels/scalp.py:4189-4480`).  Live monitor shows FAR firing in
  production: 4 dispatched signals on liquid pairs (ORDI SHORT, XLM/LINK/FIL
  LONG) with confidence 80.33-84.00 (A+ tier).  Unlike PDC/CLS (silent paths
  audited as preventive), FAR is an **active high-quality producer** — these
  fixes have direct production impact.
- **🟡 Bug A — wrong reject reason for `close <= 0`** (line 4258).
  Pre-fix emitted `breakout_not_found` for invalid candle data.  Same family
  as DIV_CONT/FUNDING/CLS/PDC audits.
  **Fix**: emit `invalid_price`.
- **🟡 Bug B — wrong reject reason for ATR invalid** (line 4254).
  Pre-fix emitted `adx_reject` for an `atr_val is None or atr_val <= 0`
  check.  Confirmed via grep that all three other usages of `adx_reject`
  in scalp.py guard genuine ADX gates (lines 778, 3632, 3945) — FAR's
  use was a copy-paste defect that conflated two telemetry classes.
  **Fix**: emit `atr_invalid` (new distinct token).
- **🔴 Bug C — tight SL geometry** (lines 4392-4406).
  Pre-fix: `sl = auction_wick_extreme ± 0.3×ATR` with min `0.5×ATR` floor.
  Tight failed-auction wicks (probe just below/above struct level by ~0.05% of
  price) yielded sl_dist of 0.5-0.6% — defeated by 0.80% universal floor at
  `_enqueue_signal`, structural anchor lost.
  **Fix**: applied close-relative + 1×ATR floor pattern (mirror of
  VSB/BDS/ORB/QCB/DIV_CONT/CLS/PDC).
- **TP cap explicitly NOT applied** for FAR: `tp1 = max(close + tail,
  close + sl_dist × 1.0)` where `tail = wick depth` is the failed-auction
  rejection magnitude (a Type-C measured-move, mirroring PDC's
  displacement-height target).  Capping by ATR percentile would defeat
  the projection thesis: the rejected-probe size IS the relevant move.
- **Tests added** (`tests/test_channels.py::TestFailedAuctionReclaimAuditFixes`):
  3 new — invalid_price reject reason, atr_invalid reject reason, SL
  respects close-relative floor.  Plus one precision-fix on
  `test_long_tp1_has_minimum_1r_floor` (added 1e-8 tolerance — wider SL
  causes tp1 to land exactly at the 1R floor, where `round(tp1, 8)`
  truncates a sub-rounding bit).  3331 broader tests pass (vs 3328
  post-PDC — net +3, zero regressions).
- **Data sufficiency check**: FAR needs 5m candles ≥ 20 (boot 500), ATR
  (always populated), RSI (soft gate, optional), FVG/orderblock soft-quality
  fallback (optional).  All trivially met after seed.  Path is firing in
  production — no data starvation observed.

Prior session (2026-05-02 — path audit #13):
- **POST_DISPLACEMENT_CONTINUATION deep dive** (`_evaluate_post_displacement_continuation`,
  `src/channels/scalp.py:3847-4170`).  Path was previously listed as
  "Effectively silent — never produced a signal" in OWNER_BRIEF §4.3.
  Diagnosis: PDC requires TRENDING/STRONG_TREND/WEAK_TREND/BREAKOUT_EXPANSION
  regimes (`_PDC_VALID_REGIMES`); market is 99.7% QUIET so the path is
  regime-blocked virtually 100% of the time.  Two structural defects
  found, both family bugs already fixed in other paths.
- **🟡 Bug A — wrong reject reason for `close <= 0`** (was line 3933).
  Pre-fix emitted `auction_not_detected` for invalid candle data.
  Same family as DIV_CONT/FUNDING/CLS audits.
  **Fix**: emit `invalid_price`.
- **🔴 Bug B — tight SL geometry** (was line 4079).
  Pre-fix: `sl = consol_low ± 0.3×ATR` with min `0.5×ATR` floor.
  PDC's design intent IS narrow consolidation (strong absorption), so
  consol_range is structurally tight by definition.  Combined with the
  0.3×ATR buffer this produced sl_dist as low as 0.2-0.4% in
  low-ATR/tight-consolidation cases — defeated by the 0.80% universal
  floor at `_enqueue_signal`, structural anchor lost.
  **Fix**: applied close-relative + 1×ATR floor pattern (mirror of
  VSB/BDS/ORB/QCB/DIV_CONT/CLS).
- **TP cap explicitly NOT applied** for PDC: TP1 = displacement_height
  × 1.0 (Type C measured-move).  This is structurally tied to the
  institutional move magnitude — capping by ATR percentile would
  defeat the projection thesis (different from FVG/swing-anchored TPs
  in other paths).  Min R:R floor (1.5R) preserved.
- **Tests added** (`tests/test_channels.py::TestPostDisplacementContinuationAuditFixes`):
  2 new — invalid_price reject reason, SL respects close-relative floor.
  All 45 PDC tests pass (43 existing + 2 new).  3328 broader tests
  pass (vs 3326 post-CLS baseline — net +2, zero regressions).
- **Data sufficiency check**: PDC needs 5m candles ≥ 20 (boot 500),
  EMA9/EMA21/RSI/ADX (always populated), volume background (uses 15
  candles excluded from displacement+consolidation window — fine).
  FVG/orderblock soft-penalty fallback.  ATR for new SL geometry.
  All trivially met after seed.  Path's silence is regime-driven
  (PDC valid only in trending regimes which are rare in current
  QUIET market).

Prior session (2026-05-02 — path audit #12):
- **CONTINUATION_LIQUIDITY_SWEEP deep dive** (`_evaluate_continuation_liquidity_sweep`,
  `src/channels/scalp.py:3554-3810`).  Path was previously listed as
  "Effectively silent — never produced a signal" in OWNER_BRIEF §4.3.
  Live monitor (prior 28h zip) showed 99.98% regime_blocked — correct
  doctrine since CLS requires TRENDING_UP/DOWN/STRONG_TREND/WEAK_TREND/
  BREAKOUT_EXPANSION (excludes QUIET/RANGING/VOLATILE), and market is
  99.7% QUIET.  Latest zip (smaller window) had no funnel data.
  Three structural defects found, all family bugs already fixed in
  other paths.
- **🟡 Bug A — wrong reject reason for `close <= 0`** (was line 3621).
  Same family as DIV_CONT/FUNDING audits.  Pre-fix emitted
  `momentum_reject` for invalid candle data.
  **Fix**: emit `invalid_price`.
- **🔴 Bug B — tight SL geometry** (was line 3708).
  Pre-fix: `sl = sweep_level ± 0.3×ATR` with min `0.5×ATR` floor.
  When sweep_level was very close to close (e.g., 5bp gap), structural
  sl_dist could be 0.15% — defeated by the 0.80% universal floor at
  `_enqueue_signal`, structural anchor lost.
  **Fix**: applied close-relative + 1×ATR floor pattern (mirror of
  VSB/BDS/ORB/QCB/DIV_CONT).
    `sl = min(sweep_level − 0.3×ATR, close − max(0.8% × close, 1×ATR))`
- **🟡 Bug C — missing TP1 ATR-adaptive cap**.
  TP1 = nearest FVG midpoint in direction.  In strong trends (CLS by
  definition is a continuation setup → trends), the FVG can sit
  several R from close.
  **Fix**: applied 1.8R / 2.5R / uncapped by ATR percentile (consistent
  with SR_FLIP / TPE / FUNDING / DIV_CONT).
- **Tests added** (`tests/test_channels.py::TestContinuationLiquiditySweepAuditFixes`):
  2 new — invalid_price reject reason, SL respects close-relative
  floor.  All 49 CLS tests pass (47 existing + 2 new).  3326 broader
  tests pass (vs 3324 post-DIV_CONT baseline — net +2, zero
  regressions).
- **Data sufficiency check**: CLS needs 5m candles ≥ 20 (boot 500),
  EMA9/EMA21/RSI/ADX (always populated), sweeps in `smc_data` (from
  detector — depends on actual sweep events occurring), FVG/orderblock
  (FVG always present, orderblocks not_implemented).  ATR for new SL
  geometry.  All trivially met after seed.  Path's silence is
  regime-driven (CLS valid only in trending regimes which are
  rare in current QUIET market).

Prior session (2026-05-02 — path audit #11):
- **DIVERGENCE_CONTINUATION deep dive** (`_evaluate_divergence_continuation`,
  `src/channels/scalp.py:3263-3530`).  Latest monitor zip:
  `EVAL::DIVERGENCE_CONTINUATION: regime_blocked=18,420 (99.98%),
  basic_filters_failed=1, cvd_divergence_failed=1` — 0 generated.  Path
  is exempted from QUIET_SCALP_BLOCK at conf ≥ 64 (`_QUIET_DIVERGENCE_MIN_CONFIDENCE`)
  but the evaluator-level regime gate restricts to TRENDING_UP/DOWN/WEAK_TREND;
  market is 99.7% QUIET so 99.98% blocked is correct doctrine.  Audit-3
  added dual 10+20 candle CVD window which is working.  Three structural
  defects found.
- **🟡 Bug A — wrong reject reason for `close <= 0`** (was line 3327).
  Pre-fix emitted `momentum_reject` for invalid candle data, conflating
  bad-data telemetry with the actual momentum gate count.  Same family
  as FUNDING audit #9.
  **Fix**: now emits `invalid_price`.
- **🔴 Bug B — tight SL geometry** (was line 3406).
  Pre-fix: `LONG: sl = ema21 × (1 − 0.005)`.
  When close sits very near EMA21 (e.g., 0.1% away — well within the
  1.5% retest_proximity gate), pre-fix sl_dist could be 0.6% — under
  the 0.80% universal floor at `_enqueue_signal`, defeating the
  structural anchor when clamped.
  **Fix**: applied close-relative + 1×ATR floor pattern (mirror of
  VSB/BDS/ORB/QCB).  `sl = min(ema21 × 0.995, close − max(0.8% × close,
  1×ATR))` for LONG.
- **🟡 Bug C — missing TP1 ATR-adaptive cap**.  TP1 = 10-candle swing
  high (LONG).  In strong-trend regimes the swing high can sit several R
  from close (DIV_CONT is a continuation setup → trending by definition).
  10-candle window naturally more contained than SR_FLIP's 20-candle,
  but the cap still matters on strong-trend pairs where 50min of
  one-direction price action can produce 4-5R extrema.
  **Fix**: applied 1.8R / 2.5R / uncapped by ATR percentile (consistent
  with SR_FLIP / TPE / FUNDING).  Structure-level wins when within cap.
- **Tests added** (`tests/test_divergence_continuation_tp.py::TestDivergenceContinuationAuditFixes`):
  2 new — invalid_price reject reason, SL respects close-relative floor.
  Plus updated `test_tp2_at_least_structural_swing_high_or_monotonicity_floor`
  (was `test_tp2_equals_20candle_swing_high_or_fallback`) — pre-audit-#11
  the test asserted strict equality with the swing high which only held
  because the old tight SL geometry produced small sl_dist values such
  that `tp1 + sl_dist*1.0` never exceeded the structural target.  Wider
  SL (correctly) propagates a larger sl_dist into the monotonicity check
  → tp2 forced above swing_high; updated to assert the looser invariant
  "tp2 ≥ structural target AND ≥ tp1 + 1R".
  All 15 DIV_CONT tests pass (12 existing + 2 new + 1 retitled).  3324
  broader tests pass (vs 3322 post-QCB baseline — net +2, zero
  regressions).
- **Data sufficiency check**: DIV_CONT needs 5m candles ≥ 20 (boot seed
  500), CVD ≥ 10 values (after CVD-fix boot seed), ema9/ema21
  (always populated), FVG/orderblock (FVG always present).  ATR for
  new SL geometry.  4h candles for TP3 (boot seed = 500, graceful 4R
  fallback).  All trivially met; path's silence is regime-driven.

Prior session (2026-05-02 — path audit #10):
- **QUIET_COMPRESSION_BREAK deep dive** (`_evaluate_quiet_compression_break`,
  `src/channels/scalp.py:3075-3239`).  Latest monitor zip:
  `EVAL::QUIET_COMPRESSION_BREAK: regime_blocked=15,126 (82.1%),
  breakout_not_detected=2,162 (11.7%), basic_filters_failed=539 (2.9%)` —
  0 generated in latest 18,423-cycle window.  Quality-by-path window
  shows 3 prior closes all at -0.046% PnL (SL hits at flat — minimal
  loss but no winners).  Two structural defects found, both mirror
  VSB/BDS/ORB family bugs.
- **🔴 Bug A — current-candle volume gate** (was line 3142).  Same
  `volumes[-1] >= 2.0 × avg_vol` partial-vs-complete-candle unit
  mismatch removed from VSB/BDS/ORB.  Especially backward for QCB:
  the path requires QUIET regime (low absolute volume by definition);
  the squeeze-release thesis tracks the BREAKOUT candle's volume,
  not a still-forming partial candle's running total.
  **Fix**: removed the partial-candle volume gate; the rolling-average
  non-degenerate check remains (`avg_vol > 0`).
- **🔴 Bug B — tight SL geometry** (was line 3162).  Pre-fix:
    LONG: `sl = min(bb_lower − 0.5×ATR, close × (1 − 0.003))`
  The 0.3% close-relative floor was sub-spread on most pairs and
  ignored ATR; the bb-anchored stop was tight in compressed-band
  conditions (QCB by definition fires when bb width <2.5%).  Result:
  the 0.80% universal floor at `_enqueue_signal` clamped most stops,
  defeating the structural anchor.  Path's 3 prior closes all
  hovered around break-even SL hits — consistent with the tight-stop
  thesis.
  **Fix**: applied close-relative + ATR floor pattern.
    `sl = min(bb_lower − 0.5×ATR, close − max(0.8% × close, 1×ATR))`
  Take the further-from-close so the stop respects both band geometry
  AND minimum room.
- **Tests added** (`tests/test_channels.py::TestQuietCompressionBreakAuditFixes`):
  3 new — accepts low/zero current-candle volume, SL respects
  close-relative floor on tight bands.  All 8 QCB tests pass (5
  existing + 3 new).  3322 broader tests pass (vs 3319 post-FUNDING
  baseline — net +3, zero regressions).
- **Data sufficiency check**: QCB needs 5m candles ≥ 25 (boot seed
  500), Bollinger Bands (`bb_upper_last`, `bb_lower_last`) — always
  populated by indicator pass, MACD histogram (last/prev) — present
  for trending checks, FVG/orderblock — always check FVG (orderblocks
  not_implemented).  ATR for SL geometry.  All trivially met after
  boot seed.  Path's silence in current zip is regime-driven (the
  82% regime_blocked = QUIET market actually doesn't trigger
  compression+breakout very often, which is correct doctrine).

Prior session (2026-05-02 — path audit #9):
- **FUNDING_EXTREME_SIGNAL deep dive** (`_evaluate_funding_extreme`,
  `src/channels/scalp.py:2878-3041`).  Latest monitor zip:
  `EVAL::FUNDING_EXTREME: funding_not_extreme=11,763 (63.8%),
  basic_filters_failed=3,879 (21%), missing_funding_rate=1,825 (9.9%)` —
  **95 candidates generated, ALL 95 killed downstream**.  Truth report
  explicitly calls FUNDING the *"most likely bottleneck"*.
- **🔴 QUIET_SCALP_BLOCK bottleneck — FUNDING exempt SHIPPED**
  (`src/scanner/__init__.py:_QUIET_FUNDING_MIN_CONFIDENCE = 60.0`).
  All 95 evaluator-passing candidates were dying at the scanner-level
  QUIET_SCALP_BLOCK gate (FUNDING wasn't QCB-exempt or DIV_CONT≥64-
  exempt).  Audit-3 already removed the evaluator-level QUIET block;
  this scanner-level exempt completes that doctrine.  Lower bar (60)
  than DIV_CONT (64) because extreme funding is itself the quality
  evidence — the trigger gate already filtered for the structural
  thesis.  Owner authorized the CTE recommendation in this session.
  6 new dedicated tests in
  `tests/test_audit_findings.py::TestQuietGateDivergenceContinuation`
  including a leak-test that verifies the 60-floor is FUNDING-only.
- **🟡 Bug A — wrong reject reason for `close <= 0`** (was line 2910).
  Pre-fix emitted `funding_not_extreme` for invalid-price rows,
  conflating bad-data telemetry with the actual trigger gate count.
  Fix: now emits `invalid_price` (truthful telemetry).
- **🟡 Bug B — missing TP1 ATR-adaptive cap**.  Same family as SR_FLIP
  audit #8 — FUNDING's TP1 comes from `_funding_extreme_structure_tp1`
  (nearest qualifying FVG/OB).  In trending markets the nearest FVG/OB
  can sit 5-10R from close, which is unreachable for a contrarian
  mean-reversion setup before SL fires.  Mean-reversion family has
  `min_rr=0.9` so capping more aggressively is structurally appropriate.
  Fix: applied 1.8R / 2.5R / uncapped by ATR percentile (mirror of
  SR_FLIP / TPE).  Structure-level wins when within cap.
- **Tests added** (`tests/test_pr07_specialist_path_quality.py::TestFundingExtremeAuditFixes`):
  4 new — invalid_price reject reason, TP1 capped at 2.5R median,
  capped at 1.8R low, uncapped high.  All 30 pr07 tests pass (26
  existing + 4 new).  3313 broader tests pass (vs 3309 post-SR_FLIP
  baseline — net +4, zero regressions).
- **Data sufficiency check**: FUNDING needs:
  - `funding_rate` from order_flow_store: ✅ present in 90% of cycles
    (10% absent on low-vol pairs — known issue, graceful reject)
  - 5m candles ≥ 5: ✅ trivial
  - CVD ≥ 4 values: ✅ for most pairs after CVD-fix boot seed
  - liquidation_clusters: ⚠️ ABSENT in 100% of cycles in latest zip
    (no cascades in QUIET regime).  FUNDING uses ATR×1.5 fallback with
    `_sl_degraded` flag and 5-pt soft penalty — this is GOOD graceful
    degradation, not a bug.  But contributes to lower confidence
    scores → exacerbates QUIET_SCALP_BLOCK kill.
  - FVG/OB: ✅ FVG always present (orderblocks not_implemented)
  - regime_context.atr_percentile (used by new TP1 cap): ✅ falls back

Prior session (2026-05-02 — path audit #8):
- **SR_FLIP_RETEST deep dive** (`_evaluate_sr_flip_retest`,
  `src/channels/scalp.py:2437-2810`).  Latest monitor zip showed
  `EVAL::SR_FLIP_RETEST: regime_blocked=15,123 (82.1%),
  flip_close_not_confirmed=1,562 (8.5%), wick_quality_failed=600 (3.3%)` of
  18,423 cycles — 1 generated, 0 emitted (filtered downstream by
  QUIET_SCALP_BLOCK).  Path is well-engineered with layered soft/hard
  gates and structural-level detection — but two real defects found.
- **🔴 Bug A — missing TP1 ATR-adaptive cap**.  OWNER_BRIEF Audit-3
  table claimed *"SR_FLIP + TPE TP1 ATR-adaptive cap (1.8–2.5× SL)"*
  was deployed, but only TPE (line ~1264) actually had the cap.  SR_FLIP's
  TP1 was the 20-candle swing high with only a 1.2R FLOOR — no upper cap.
  In trending markets the swing high can sit 5-10R from close, producing
  TP1 targets that rarely get hit before the structural SL fires — a
  documented contributor to the historical 100% SL rate
  (OWNER_BRIEF Part IV §4.3).
  **Fix**: applied the same ATR-adaptive cap pattern as TPE.
    atr_percentile <40  → cap TP1 at 1.8R   (accumulation/low-ATR)
    atr_percentile 40-65 → cap TP1 at 2.5R   (median ATR)
    atr_percentile ≥65   → no cap            (room to run in high vol)
- **🟡 Bug B — VOLATILE_UNSUITABLE block missing at evaluator**
  (was line 2480).  Evaluator-level regime block only checked
  `regime_upper == "VOLATILE"`; `VOLATILE_UNSUITABLE` slipped through.
  The scanner's REGIME_SETUP_COMPATIBILITY excludes SR_FLIP from
  VOLATILE_UNSUITABLE so this was caught downstream — but defence-in-
  depth fix mirrors the doctrine at the evaluator.
- **Tests added** (`tests/test_channels.py::TestSrFlipRetestRefinements`):
  4 new cases — VOLATILE_UNSUITABLE blocked, TP1 capped at 2.5R in
  median-ATR, capped at 1.8R in low-ATR, uncapped in high-ATR.
  All 39 SR_FLIP tests pass (35 existing + 4 new).  3309 broader tests
  pass (vs 3305 post-ORB-merge baseline — net +4, zero regressions).
- **Data sufficiency check**: SR_FLIP needs ≥55 5m candles (boot seed
  500), 4h candles for TP2 (500 from boot), structural-level detection
  uses 41 prior + 8 closed flip-search + 1 current.  All requirements
  trivially met after seed.  Path silence is purely regime-driven
  (QUIET_SCALP_BLOCK at scanner) since SR_FLIP isn't QCB or DIV_CONT≥64
  exempt.

Prior session (2026-05-02 — path audit #7):
- **OPENING_RANGE_BREAKOUT deep dive** (`_evaluate_opening_range_breakout`,
  `src/channels/scalp.py:2257`).  Latest monitor zip showed
  `EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=18,423` — 100% of cycles.
  Investigation answer: ORB is **feature-flag-disabled**
  (`SCALP_ORB_ENABLED=false` in `config/__init__.py:848`).  The path's
  rejection token was conflated with real regime blocks, making telemetry
  ambiguous.  ACTIVE_CONTEXT had ORB listed as "never produced a signal"
  needing root-cause investigation — the answer is "feature flag, by
  design, pending session-range rebuild."
- **Why ORB is disabled** (per `config/__init__.py:844-847` comment):
  current implementation uses `highs[-8:-4]` and `lows[-8:-4]` as a proxy
  for the session opening range — **not** institutional-grade
  session-anchored logic.  Code preserved for future controlled rebuild.
- **🟡 Telemetry fix — `feature_disabled` not `regime_blocked`**
  (`src/channels/scalp.py:2271`).  Disabled-flag rejection now reports
  `feature_disabled` so live monitor data clearly separates the dormant
  flag from real regime blocks.  Pre-fix was misleading — both causes
  shared the same token.
- **🔴 Bug A (preserved-fix) — current-candle volume gate**
  (was line 2322).  Same `volumes[-1] < 1.5 × avg_vol` partial-vs-complete
  candle unit-mismatch bug as VSB / BDS.  Removed for consistency so when
  ORB is re-enabled it doesn't ship the same family of defects.
- **🔴 Bug B (preserved-fix) — catastrophic SL placement**
  (was line 2348).  `sl = range_low × 0.999` for LONG produced sub-spread
  stops on tight ranges.  Same close-relative + ATR floor pattern as
  VSB / BDS now applied: `sl = min(range_low × 0.999, close − max(0.8% ×
  close, 1×ATR))` for LONG (mirror for SHORT).
- **Tests added** (`tests/test_pr06_orb_disable.py::TestORBAuditFixes`):
  3 new cases — disabled-path emits `feature_disabled`, active path
  accepts low partial-candle volume, active path SL respects close-
  relative floor on tight ranges.  All 13 ORB tests pass (10 existing
  + 3 new).  3305 broader tests pass (vs 3302 post-cleanup baseline —
  net +3, zero regressions).
- **Open question for owner** — ORB is currently disabled because the
  session-range proxy isn't institutional-grade.  Two paths forward:
    (a) leave disabled, build true session-anchored opening-range logic
        as a future evaluator rebuild (B10 territory — needs sign-off)
    (b) re-enable as-is now that the VSB-family bugs are fixed; the
        proxy is "good enough" for a MIDCAP scalp window even if not
        SMC-doctrinal.  Lower bar, more emissions, less institutional
        accuracy.
  CTE recommendation: (a) — the current proxy fires on a 20-minute
  window from "now", which has nothing to do with session-open
  liquidity dynamics.  Re-enabling would generate signals but not
  truthfully ORB-themed ones.  Better to either rebuild or keep
  disabled and surface the slot in an active path.

Prior session (2026-05-02 — path audit #6):
- **BREAKDOWN_SHORT deep dive** (`_evaluate_breakdown_short`,
  `src/channels/scalp.py:2006–2220`). The SHORT mirror of VSB.  Latest
  monitor zip showed identical numbers to VSB:
  `EVAL::BREAKDOWN_SHORT: volume_spike_missing=11,557 (62.7%)`,
  `basic_filters_failed=3,558 (19.3%)`, `regime_blocked=3,297 (17.9%)` of
  18,423 cycles — **0 generated**.  As predicted in the VSB PR, all 4
  structural bugs from VSB had exact mirrors in BDS.
- **🔴 Bug A — current-candle volume gate** (was line 2068).
  Same `volumes[-1] < SURGE_VOLUME_MULTIPLIER × rolling_avg` partial-vs-
  complete-candle unit mismatch.  Worse for BDS than VSB: BDS's thesis is
  "breakdown + DEAD-CAT BOUNCE" — the bounce phase has even more
  pronounced volume reduction than VSB's pullback.  Fix: removed.
- **🔴 Bug B — breakdown qualifier ignored close** (was line 2087).
  Same wick-only check as VSB.  A wick that pierces swing_low and CLOSES
  back above is a BULLISH SWEEP (LSR LONG bait), not a breakdown.  BDS
  was accepting bullish sweeps as "breakdowns" and treating the
  rejection upward as a "dead-cat bounce" — feeding false SHORT signals.
  Fix: gate now requires `lows[i] < swing_low AND closes[i] < swing_low`.
  Test fixture had the same papering-over pattern as VSB
  (`lows[idx]=97, closes[idx]=100.4` — wick pierces, close stays above —
  classic bullish sweep).  Updated to true breakdown geometry
  (close=98 below swing_low=100).
- **🔴 Bug C — catastrophic SL placement** (was line 2150).
  Same as VSB but mirrored to swing_low side.  `sl = swing_low * 1.008`
  produced sl_dist as low as 0.05% in extended bounce zones (close near
  the 0.75% upper bound of the bounce window).  In premium zone
  (0.3-0.6%) sl_dist was 0.20-0.50% — well below the 0.80% universal
  floor at `_enqueue_signal`.
  Fix: SL takes the HIGHER (further-from-close, since SHORT) of:
    1. structural ceiling: 0.8% above swing_low (anti-bear-trap)
    2. close-relative ceiling: max(0.8% of close, 1.0×ATR) above close
- **🟡 Bug D — hardcoded breakdown-vol multiplier 2.0** (was line 2146).
  B8 violation.  Fix: now uses the `_VSB_BREAKOUT_VOL_MULT` constant
  (env-overridable via `VSB_BREAKOUT_VOL_MULT`) introduced for VSB in
  PR #250 — shared because both paths are surge-confirmation gates of
  the same shape.
- **Tests added** (`tests/test_channels.py::TestBreakdownShortRefinements`):
  6 new cases mirroring the VSB family — current-candle vol low/zero
  (Bug A); wick-only rejected as bullish sweep (Bug B); close marginally
  below swing_low accepted (Bug B mirror); SL distance ≥ 0.8% in premium
  bounce zone (Bug C); env override on breakdown vol mult (Bug D).
  All 31 BDS tests pass (25 original + 6 new).  552 broader tests pass
  (vs 546 post-VSB-merge baseline — net +6, zero regressions).
- **Data sufficiency check (per owner request)**: identical to VSB —
  5m candles ≥ 28 trivially after boot seed; EMA9/EMA21/RSI always
  populated; FVG solid in practice; orderblocks not_implemented but
  soft-penalty fallback in fast-bearish regimes.  Path's silence was
  driven entirely by the same 4 structural gate bugs as VSB, not data.

Prior session (2026-05-01, very late — path audit #5, multi-fix):
- **VOLUME_SURGE_BREAKOUT deep dive** (`_evaluate_volume_surge_breakout`,
  `src/channels/scalp.py:1751–1960`). Latest monitor zip showed
  `EVAL::VOLUME_SURGE_BREAKOUT: volume_spike_missing=11,557 (62.7%)`,
  `basic_filters_failed=3,558 (19.3%)`, `regime_blocked=3,297 (17.9%)` of
  18,423 cycles — **0 generated**.  Owner pushed back ("we are not yet
  completed with VSB") after the first commit which only addressed the
  current-candle volume gate.  Re-audit found three more structural
  defects beyond the original gate.
- **🔴 Bug FIXED — current-candle volume gate** (was line 1808).
  The pre-fix gate compared `volumes[-1]` (the still-forming current 5m
  candle) to `SURGE_VOLUME_MULTIPLIER × rolling_avg` (3× the average of
  complete prior candles).  This was structurally wrong on two axes:
    1. **Unit mismatch**: a partial candle 1 minute into a 5m bar has
       roughly 1/5 of a complete candle's eventual volume — demanding
       it exceed 3× the complete-candle average is a unit mismatch.
    2. **Thesis contradiction**: VSB's pattern is "surge breakout +
       PULLBACK" — pullbacks have REDUCED volume by definition.
       Demanding the pullback candle still show 3× surge volume
       contradicts the very pattern.
  The breakout-candle volume check (≥ 2× rolling_avg on the actual closed
  breakout candle, line 1885 / now 1879) properly validates the surge.
  The current_vol gate was redundant and broken.
  Strong tell: existing test fixtures explicitly set `vols[-1] = 4500.0`
  with the comment "surge volume must exceed 3× rolling average" — a
  deliberate workaround that admits the gate was already known broken
  inside the test infrastructure.
  **Fix**: removed the gate.  Replaced with a multi-line explanatory NOTE
  comment for future readers.
- **🔴 Bug B (re-audit) — breakout qualifier ignored close** (was line 1825).
  Pre-fix the breakout-candle search only checked `highs[i] > swing_high`
  (a wick that pierces the level).  But a wick that pierces and CLOSES
  back below is a **sweep**, not a breakout — that's exactly what LSR
  is designed to fade.  VSB was accepting sweeps as breakouts and
  treating the subsequent reversal as a "pullback retest" — feeding
  false positives directly into the path's thesis.
  **Fix**: gate now requires `highs[i] > swing_high AND closes[i] >
  swing_high` — true close-above breakout.  Strong tell: the existing
  `_make_surge_candles` fixture set `highs[idx]=103, closes[idx]=98.5`
  (wick pierces, close stays below — classic sweep geometry) and was
  built to pass the wick-only check.  Fixture updated to true breakout
  geometry (close=102 above swing_high=99); also added a new test
  asserting wick-only setups are now correctly rejected.
- **🔴 Bug C (re-audit) — catastrophic SL placement** (was line 1889).
  Pre-fix: `sl = swing_high * (1 - 0.008)`.  Anchored to swing_high
  regardless of where close sat in the pullback zone.  Result:
    - close at 0.30% below swing_high → sl_dist = 0.50% (tight)
    - close at 0.50% below swing_high → sl_dist = 0.30% (very tight)
    - close at 0.60% below swing_high → sl_dist = 0.20% (dangerous)
    - close at 0.75% below swing_high → sl_dist = **0.05%** (< spread!)
  In the canonical "premium pullback zone" (0.3–0.6% below swing) the
  stop was 0.20–0.50% — well below the 0.80% universal floor enforced
  downstream at `_enqueue_signal`.  Stops getting clamped means the
  structural anchor is lost AND the actual stop is somewhere arbitrary.
  **Fix**: SL now takes the LOWER (further-from-close) of two anchors:
    1. structural floor: 0.8% below swing_high (anti-bull-trap intent)
    2. close-relative floor: max(0.8% of close, 1.0×ATR)
  Ensures SL respects both pair volatility AND the structural level
  while never producing absurdly-tight stops.
- **🟡 Bug D (re-audit) — hardcoded breakout-vol multiplier** (was 2.0
  at line 1885).  B8 violation.
  **Fix**: extracted to `_VSB_BREAKOUT_VOL_MULT` (default 2.0,
  env-overridable via `VSB_BREAKOUT_VOL_MULT`) at the module-level
  constants block alongside the WHALE thresholds.
- **Tests added** (`tests/test_channels.py::TestVolumeSurgeBreakoutRefinements`):
  6 new cases total — current-candle vol low/zero (Bug A); wick-only
  rejected as sweep (Bug B); close marginally above swing_high accepted
  (Bug B mirror); SL distance ≥ 0.8% in premium pullback zone (Bug C);
  env override on breakout vol mult (Bug D).  All 28 VSB tests pass
  (22 original + 6 new + 2 from initial #250 commit which were already
  in branch).  546 broader tests pass (vs 540 main baseline — net +6,
  zero regressions).  14 pre-existing failures remain (queue #13).
- **Data sufficiency check (per owner request)**:
  - 5m candles ≥ 28 (closes/highs ≥ 28, volumes ≥ 10): ✅ boot seed = 500
  - swing_high computation (`highs[-26:-6]`): ✅
  - breakout-candle search (`highs[-2:-7]`): ✅
  - base_of_range (`lows[-26:-6]`): ✅
  - EMA9, EMA21, RSI: ✅ always populated
  - FVG/orderblock: ⚠️ orderblocks not_implemented; FVG solid in practice;
    soft-penalty fallback in fast-momentum regimes (VOLATILE,
    BREAKOUT_EXPANSION, STRONG_TREND)
  - **Verdict**: data sufficiency is fine; the path's silence was driven
    by a broken gate, not a data gap.  Removing the gate unlocks the
    62.7% of cycles that were previously rejected on partial-candle
    volume.  Most of those will still fail other gates (breakout_not_found,
    retest_proximity, etc.) — but the structurally-valid setups will
    now actually emit.

Prior session (2026-05-01, very late — path audit #4):
- **LIQUIDATION_REVERSAL deep dive** (`_evaluate_liquidation_reversal`,
  `src/channels/scalp.py:1317–1495`). Latest monitor zip showed
  `EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=14,151 (76.8%)`,
  `basic_filters_failed=4,097 (22.2%)`, `cvd_divergence_failed=175 (0.95%)`
  of 18,423 cycles — 0 generated.  Cascade threshold catches everything in
  the current QUIET market by design (cascade by definition needs ≥1.5%
  move), but the audit found two structural gates downstream that would
  block valid setups when the regime returns.
- **🟡 Bug A — RSI extreme thresholds 25/75 too strict** (was line 1383).
  A 5m cascade reversal needs OVERSOLD context with reversal under way,
  not "RSI must be exhausted."  5m RSI rarely hits <25 / >75 during a
  normal 1.5–3% cascade — the gate killed valid reversal setups at the
  structural moment they form (RSI 28–35 with rising RSI is the canonical
  bullish-reversal context; demanding <25 means waiting until the cascade
  has already exhausted itself and the bounce is half over).
  **Fix**: thresholds 35/65 (was 25/75) AND require RSI direction confirms
  reversal under way (`rsi_val > rsi_prev` for LONG, `<` for SHORT) when
  rsi_prev is available. Same defence-in-depth pattern: standard oversold
  zone + reversal-direction confirmation rather than a single extreme cutoff.
  The existing test fixtures bypass the RSI gate by setting `rsi_last` to
  None — strong tell that the gate was known to be too restrictive even
  inside the test infrastructure.
- **🟡 Bug B — Zone proximity only checked close_now** (was line 1400).
  A cascade by definition OVERSHOOTS supply/demand zones, then bounces.
  By the time the evaluator runs, close_now is past the zone in recovery —
  the cascade extremum (low for LONG, high for SHORT) is what actually
  tested the zone.
  **Fix**: zone gate now passes if EITHER close_now or the cascade
  extremum is within 0.5% of an FVG/orderblock.  Strictly more permissive,
  preserves existing-test passes.  Also moved `cascade_low/high`
  computation up so the gate can reference them.
- **Tests added** (`tests/test_liquidation_reversal_tp.py`): 6 new cases
  covering RSI 30+rising → accept, RSI 36 → reject, RSI 30+falling → reject
  (cascade still bleeding), short 70+falling → accept, short 64 → reject,
  zone gate via cascade-extremum when close_now is past the zone.  All
  pass; 540 broader tests pass (vs 534 main baseline — net +6 from the new
  tests, zero regressions). 14 pre-existing failures remain (queue #13).
- **Data sufficiency check (per owner request)**:
  - 5m candles ≥ 20 (closes ≥ 4, volumes ≥ 21): ✅ boot seed = 500
  - CVD with ≥ 4 values: ✅ for most pairs after CVD-fix boot seed; 10.1%
    of cycles have CVD absent (low-vol pairs) — graceful reject as
    `cvd_insufficient`
  - 5m RSI / rsi_prev: ✅ always populated by indicator pass (rsi_prev at
    `src/scanner/indicator_compute.py:273`)
  - 5m volumes: ✅ always populated
  - `smc_data["fvg"]` OR `["orderblocks"]`: ⚠️ orderblocks not_implemented;
    LIQ_REV relies entirely on FVG availability — solid in practice
  - `liquidation_clusters: presence[absent=18423]` in latest zip: 100%
    absent — but LIQ_REV evaluator does NOT consume liquidation_clusters
    directly (only FUNDING_EXTREME does, with graceful fallback).  No
    impact on LIQ_REV.
  - **Verdict**: data sufficiency for LIQ_REV is fine; path silence is
    100% regime-driven (cascade doesn't trigger in QUIET).

Prior session 2026-04-30 (late evening — path audit #3):
- **TREND_PULLBACK_EMA deep dive** (`_evaluate_trend_pullback`,
  `src/channels/scalp.py:1036–1296`). Latest monitor zip showed
  `EVAL::TREND_PULLBACK: regime_blocked=18,420 (99.98%)` of 18,423 cycles —
  current QUIET market regime-blocks the path by design. Of the 3 cycles
  that escaped the regime gate, `body_conviction_fail` killed one. Tiny live
  sample, but the same gate kills the 3 currently-failing TPE entry-quality
  tests in `tests/test_channels.py::TestTrendPullbackEntryQuality`.
- **🔴 BUG FIXED — `body_conviction_fail` is structurally backward**
  (`src/channels/scalp.py:1127`). Old check:
    `body_size / candle_range >= 0.50` — punishes the canonical hammer/
    shooting-star reclaim (large lower wick on LONG, large upper wick on
    SHORT, small body, close near high/low) that *defines* a valid TPE
    entry. The 0.50 ratio threshold mistakes hammers for dojis.
  Fix: replaced with **close-position-in-range** check.
    LONG: `(close - low) / range >= 0.50` (close in upper half — large
    lower wick is FINE, that's the EMA-test wick).
    SHORT: `(high - close) / range >= 0.50` (close in lower half).
  Body-direction-must-match check (close vs open) retained — catches
  opposite-color candles, which the new metric alone wouldn't.
  This is the same architectural mistake family as the LSR mom-sign check
  from path audit #1: a metric that punishes the *identifying feature* of
  the setup.
- **Fix net result**: all 6 `TestTrendPullbackEntryQuality` tests pass
  (3 were failing on main before this fix). 416 broader tests pass; only 3
  pre-existing failures remain (down from 6 before — TPE was responsible
  for 3 of those 6). 0 regressions introduced.
- **Data sufficiency check (per owner request)**: TPE data needs are met.
  5m=500 candles boot seed (gate needs ≥50). 4h=500 candles for TP2 with
  graceful 2.0R fallback. Orderblocks `not_implemented` per dependency
  report — TPE relies on FVG availability for SMC support gate, which is
  solid in practice. Path's silence is regime-driven (99.98% QUIET),
  not data-driven.

Prior session 2026-04-30 (late evening — path audit #2):
- **WHALE_MOMENTUM deep dive** (`_evaluate_whale_momentum`,
  `src/channels/scalp.py:1488–1701`). Latest monitor zip showed
  `EVAL::WHALE_MOMENTUM: momentum_reject=15,126 (82%)` and
  `regime_blocked=3,297 (18%)` of 18,423 cycles — 100% silent.
  Root cause was upstream of the evaluator, in the trigger producer.
- **🔴 BUG FIXED — whale-alert single-tick detection** (`src/detector.py:228`).
  The producer was reading `latest = ticks[-1]; result.whale_alert =
  detect_whale_trade(latest...)`. A $1M whale at `tick[-50]` was overwritten
  by every subsequent small tick, leaving the alert detectable for ~50–100ms
  on any active pair. With WS streaming hundreds of ticks/sec on BTC and a
  15s scan cycle, the chance of `latest` being a qualifying whale was
  effectively zero. Institutional impact lasts minutes; the detection
  window must too.
  **Fix**: scan the recent_ticks window newest-first and surface the first
  qualifying whale found. The 100-tick window was already being captured —
  we were just sampling its end.
- **B8 compliance — three thresholds now env-overridable**:
  `WHALE_TRADE_USD_THRESHOLD` (1M default, in `src/detector.py`),
  `WHALE_DELTA_MIN_RATIO` (2.0), `WHALE_MIN_TICK_VOLUME_USD` (500k),
  `WHALE_OBI_MIN` (1.5) (all in `src/channels/scalp.py:42–44`). All were
  hardcoded; B8 says everything must be env-tunable.
- **Tests added** (`tests/test_new_modules.py::TestSMCDetector`): four new
  cases — whale buried in middle of window must still be detected, no whale
  when no tick exceeds threshold, env override lowers threshold, plus the
  pre-existing latest-tick-is-whale case still passes. All pass; same 6
  pre-existing failures elsewhere (queue #13).
- **Data sufficiency check (per owner request)**: 100-tick recent window is
  count-based not time-based — on a $0.50 alt with ~5 trades/min that's
  20 minutes of stale data; on BTC ~5 seconds. `SEED_TICK_LIMIT=1000`
  storage is fine. 1m candle minimum 10 trivial. Time-windowed ticks
  would be cleaner but requires data-store contract change — deferred.
- Tier-aware whale threshold (TOP=$1M, MIDCAP=$250k, etc.) noted as a
  future improvement — needs `pair_profile` plumbed into `SMCDetector.detect()`
  signature, which is a wider architectural change. Not blocking.

Prior session 2026-04-30 (evening — path audit #1):
- **Path audit #1 — LIQUIDITY_SWEEP_REVERSAL deep dive.** Owner authorized
  fixing the path before moving on; rule-override permitted where structurally
  justified. Audit identified two real defects in `_evaluate_standard`
  (`src/channels/scalp.py:747`):
  1. **Broken 5m-momentum-direction-sign check** (was lines 824–828).
     The 3-candle `momentum` indicator is a close-to-close % change measured
     across 3 bars — for a fresh sweep candle, 2 of those 3 bars are
     *pre-sweep drift* which by definition moves opposite to the post-sweep
     reversal. The sign check therefore rejected the very setups LSR is
     designed to fire on. Latest monitor zip showed `momentum_reject=7,330`
     (~40% of all `EVAL::STANDARD` cycles); this gate was a major contributor.
     **Fix**: deleted the sign check entirely. Magnitude (`|mom| ≥ threshold`)
     and persistence checks remain — both sign-agnostic. The MSS gate below
     is the structurally truthful direction confirmation.
  2. **Missing MSS confirmation** despite the helper existing. `detect_mss()`
     in `src/smc.py:184` is computed by `SMCDetector` and reaches the
     evaluator via `smc_data["mss"]`, but `_evaluate_standard` never read
     it — half the SMC pattern was unused.
     **Fix**: wired three-state MSS check after sweep direction is set —
     match → no penalty (canonical pattern complete), mismatch → hard reject
     (`mss_direction_mismatch`, LTF moved against the sweep), missing →
     soft penalty `MSS_MISSING:-8` applied alongside MTF/MACD penalties.
     Soft (not hard) when missing because 1m may not have updated past the
     sweep candle's body yet on a freshly-detected sweep.
- **Tests added** (`tests/test_channels.py::TestScalpChannel`): four new cases
  covering MSS missing/match/mismatch and a regression guard against the
  deleted sign check. All pass; no regressions introduced (the 6 failures in
  the broader test run are pre-existing per queue item #13, confirmed by
  `git stash` baseline).
- **Reviewed monitor zip 2026-04-30 04:08 UTC** — flagged stale (last performance
  record 3.4h old). Window-over-window deltas all zero vs prior window — same
  QUIET regime, same path silence. Only 3 QCB closes in window, all flat
  (~ -0.046% PnL each). No new bug surface or anomaly to act on.
- **Diagnosed HYPEUSDT QCB 89.2 → 67.6 gate penalty** (Priority 3 / queue #7).
  In `360_SCALP` channel, only two soft-gate bases (`volume_div=12.0` and
  `spoof=12.0`) yield exactly `12.0 × 1.8 (QUIET regime mult) = 21.6`. Of the
  two, **`volume_div` has a structural mismatch with QCB's thesis**: QCB by
  design fires on a primary-TF compression breakout volume spike during a
  QUIET window where higher-TF (15m) volume is declining — that pattern is
  exactly what `check_volume_divergence_gate` flags as manipulation
  (`_REGIME_SPIKE_THRESHOLD["QUIET"]=1.5`, `_REGIME_DECLINE_THRESHOLD["QUIET"]=0.8`).
  Spoof, by contrast, is an orderbook-anomaly signal that's informative
  regardless of setup type — leave it alone.
- **Shipped: PR-7B path-aware modulation entry for QCB on volume_div** at scale 0.60
  (matches existing VSB/FAR/SR_FLIP precedents). Effect: pre-fix
  `12.0 × 1.8 = 21.6` → post-fix `12.0 × 0.60 × 1.8 = 12.96`. Penalty preserved
  (volume_div divergence still meaningfully reflected) but no longer
  single-handedly drops an A+ tier signal to FILTERED. Edit at
  `src/scanner/__init__.py:449` plus mirroring assertion in
  `tests/test_regime_soft_penalty.py::TestPathAwarePenaltyModulation`.
  TestPathAwarePenaltyModulation passes; no new test failures introduced.
  Two pre-existing failures (`TestHardGatesStillBlock::test_cross_asset_gate_still_hard_blocks`,
  `TestRegimeMultiplierStoredOnSignal::test_regime_multiplier_stored_quiet`)
  exist on main and are unaffected — covered by tech-debt queue #13.

Prior session 2026-04-29:
- **Reviewed monitor zip 2026-04-29 08:49 UTC** — see "Monitor Zip Findings" below
- **Confirmed PR #236 fixes are live and working** (QCB went 0 → 12 emissions)
- **Verified all Audit-3 fixes are deployed** in `src/channels/scalp.py`
  (TPE/DIV_CONT WEAK_TREND at lines 1027/3044, FUNDING QUIET removed at 2692,
  LIQ_REV ATR-relative cascade at 1305)
- **Shipped: 360_SCALP channel cap raise 2.5% → 3.0%** in `signal_quality.py:347`.
  Unlocks per-setup 3.0% caps for FAR/QCB/TPE/FUNDING which were silently
  capped at 2.5% by the tighter-wins channel logic. Setups with <3.0% per-setup
  caps (SR_FLIP=2.5, RANGE_REJECTION=1.5, etc.) are unaffected — math verified
  in `_max_sl_pct_for_policy()`.
- **Shipped: mover promotion data-plumbing fix** (`src/scanner/__init__.py:1090`).
  Owner flagged that mover-promoted pairs (PR #233) weren't producing signals.
  Root cause: PR #233 wired the *promotion list* but skipped REST candle
  seeding and CVD seeding — promoted symbols had 0 candles, failing
  `insufficient_candles` on every cycle for the entire 5-cycle TTL.
  Fix: new `_seed_mover_pair()` method awaits `data_store.seed_symbol()`
  (mirrors `main.py:708` new-pair pattern) + `seed_cvd_from_klines()`
  (mirrors `bootstrap.py:177` boot pattern) before adding the pair to
  `_mover_promoted_pairs`. Pairs with <28 5m candles after seed are skipped
  to avoid burning telemetry on a dead pair. WS subscription deliberately
  skipped — `update_streams_for_top50()` does a full stop→start which is too
  disruptive for a 75-second promotion window; REST-seeded data is sufficient
  for VSB+BREAKDOWN evaluation in that span.

Prior session (2026-04-28): PR #236 — per-setup SL caps, EXHAUSTION_FADE 0.9 R:R,
`/dashboard` mover counter, interim 1.5% → 2.5% bump (now superseded).

---

## Monitor Zip Findings (2026-04-29 08:49 UTC, 28h window, 409,322 cycles)

### Engine Health: ✅
- Heartbeat 3s, status running, healthy.
- WS streams active, OI populated 99.97%, CVD populated 15.8% (low-vol pairs
  starved — known issue).

### Path Funnel Truth
| Path | Generated | Gated | Scored | Emitted | Notes |
|---|---:|---:|---:|---:|---|
| QUIET_COMPRESSION_BREAK | 12,374 | 36 | n/a | **12** | ✅ Loop broken (was 0 pre-fix) |
| FAILED_AUCTION_RECLAIM | 43,033 | 40,845 | n/a | **2** | Heavy gate filter — needs non-QUIET regime |
| SR_FLIP_RETEST | 27,133 | 22,539 | 4,594 | **0** | All 4,594 scored signals **FILTERED at QUIET_SCALP_BLOCK** |
| LIQUIDITY_SWEEP_REVERSAL | 7,431 | 7,269 | n/a | **0** | Same QUIET_SCALP_BLOCK structural protection |
| 9 other paths | 0 | — | — | — | `regime_blocked` (correct in QUIET) |

**Root cause of "0 SR_FLIP emissions"**: `scanner/__init__.py:4336` — the
`QUIET_SCALP_BLOCK` gate filters all 360_SCALP setups EXCEPT QCB (always exempt)
and DIV_CONT (when conf ≥ 64) when regime is QUIET. SR_FLIP, FAR, LSR all
correctly fall through this gate in QUIET. **This is structural protection,
not a bug.** Threshold `QUIET_SCALP_MIN_CONFIDENCE = 65.0` (config/__init__.py:1058).

### Liquidation Clusters Absent (409,322/409,322)
**Not a bug.** Per `bootstrap.py:385` the `@forceOrder` subscription is wired,
events flow through `main.py:542` → `_pending_liquidations` → `OrderFlowStore.add_liquidation()`.
QUIET markets simply produce no liquidation cascades. Only consumer is
FUNDING_EXTREME (`scalp.py:2760`) which has graceful ATR×1.5 fallback.

### Win-rate Validation: Still Blocked
Only **1** signal closed in window (QCB at -0.086% PnL — essentially flat exit,
not a real SL or TP). Need non-QUIET regime to generate enough signals for
statistical confidence.

---

## Current Priority (Do This First)

1. **Wait for non-QUIET regime data** — 9/14 paths and the QUIET_SCALP_BLOCK
   gate cannot be evaluated until market shifts to TRENDING / RANGING / WEAK_TREND.
   Until then, QCB and DIV_CONT are the only paths that can fire.
2. **Validate channel cap raise effect on next zip** — check FAR/QCB SL distance
   distribution; some signals should now use 2.5–3.0% range that were previously
   compressed/rejected at 2.5%.
3. **HYPEUSDT QCB 89.2 → 67.6 via -21.6 gate penalty** — open mystery from
   prior session. Source unknown.

---

## All Confirmed Bug Fixes (Deployed or in open PR)

| Fix | File | Session |
|---|---|---|
| MIN_LIFESPAN 180s → 30s | `config/__init__.py` | prior |
| WS fallback limit=2, raw[0] | `src/websocket_manager.py` | prior |
| EXPIRED outcome label | `src/performance_metrics.py` | prior |
| OI readiness present=count>0 | `src/scanner/__init__.py` | prior |
| Indicator cache includes candle count | `src/scanner/__init__.py` | prior |
| OI backfill at boot (30 snapshots) | `src/order_flow.py` | prior |
| TREND_PULLBACK_EMA confirmation entry | `src/channels/scalp.py` | prior |
| Universal SL minimum 0.80% | `src/scanner/__init__.py` (_enqueue_signal) | prior |
| SL minimum (0.50, 0.80) all channels | `config/__init__.py` | prior |
| TP confirmation buffer 0.05% | `src/trade_monitor.py` | prior |
| WATCHLIST spam disabled | `src/signal_router.py` | prior |
| SL/TP uses 1m candle HIGH/LOW | `src/trade_monitor.py` | prior |
| ATR minimum SL in evaluators | `src/channels/scalp.py` | prior |
| stop_loss field on SignalRecord | `src/performance_tracker.py` + `src/trade_monitor.py` | prior |
| LSR `build_signal_failed` telemetry | `src/channels/scalp.py:913` | Audit-2 |
| WHALE `build_signal_failed` telemetry | `src/channels/scalp.py:~1531` | Audit-2 |
| SR_FLIP TP1==TP2 collapse in 4h-data branch | `src/channels/scalp.py:~2475` | Audit-2 |
| TPE/DIV_CONT accept WEAK_TREND | `src/channels/scalp.py:~961/2920` | Audit-2 |
| TP-ladder monotonicity helper (5 sites) | `src/channels/scalp.py:259` | Audit-2 |
| deploy.yml: skip VPS deploy on doc-only commits | `.github/workflows/deploy.yml` | Audit-2 |
| `_check_invalidation` regime-flip & EMA-crossover creation-relative | `src/trade_monitor.py:555–615` | INV-1 |
| MOM-PROT: momentum invalidation profit-protection gate | `src/trade_monitor.py:617` | MOM-PROT |
| SR_FLIP + TPE TP1 ATR-adaptive cap (1.8–2.5× SL) | `src/channels/scalp.py` | Audit-3 |
| FUNDING_EXTREME remove QUIET regime block | `src/channels/scalp.py:2679` | Audit-3 |
| SL cap raised 0.80% → 1.20% across all 8 channel configs | `config/__init__.py` | Audit-3 |
| LIQ_REV ATR-relative cascade threshold (floor 1.5%, cap 3.5%) | `src/channels/scalp.py:~1294` | Audit-3 |
| DIV_CONT dual 10+20 candle CVD window | `src/channels/scalp.py:~3062` | Audit-3 |
| LSR momentum persistence 1-candle in QUIET/RANGING | `src/channels/scalp.py:~795` | Audit-3 |
| DISTRIBUTION soft gate −15pts on LONG signals | `src/scanner/__init__.py:~4105` | Audit-3 |
| Meme coin low-volume penalty 0.85× (<$150M 24h) | `src/scanner/__init__.py:~4124` | Audit-3 |
| CVD 24h starvation: boot seed from historical 1m candles | `src/historical_data.py` + `src/order_flow.py` | CVD-fix |
| Mover pairs dashboard: `set_mover_pairs()` + `/dashboard` counter | `src/telemetry.py` + `src/scanner/__init__.py` | PR #236 |
| 360_SCALP channel SL cap raised 1.5% → 2.5% (interim) | `src/signal_quality.py` | PR #236 |
| Per-setup SL caps: 17 values in `_MAX_SL_PCT_BY_SETUP` | `src/signal_quality.py` | PR #236 |
| EXHAUSTION_FADE moved to 0.9 R:R mean-reversion tier | `src/signal_quality.py` | PR #236 |
| **360_SCALP channel SL cap raised 2.5% → 3.0% — unlocks per-setup 3.0% caps for FAR/QCB/TPE/FUNDING** | `src/signal_quality.py:347` | **This session (2026-04-29)** |
| **Mover-promotion REST seed + CVD seed on promotion (PR #233 follow-up)** | `src/scanner/__init__.py:1090` (`_seed_mover_pair`) | **This session (2026-04-29)** |
| **REST-fallback admin-alert grace period (60s) — transient drops stay silent; only sustained outages alert. Cooldown layered on top for prolonged outages.** | `src/websocket_manager.py:303` (`_start_rest_fallback` + `_maybe_alert_after_grace`) | Prior 2026-04-29 |
| **PR-7B path-aware modulation: QCB volume_div = 0.60 — closes structural mismatch where QUIET volume_div thresholds flag QCB's own breakout pattern as manipulation; -21.6 → -13.0** | `src/scanner/__init__.py:449` (`_PENALTY_MODULATION_BY_SETUP`) + test mirror in `tests/test_regime_soft_penalty.py` | **This session (2026-04-30)** |
| **LSR path audit fix: removed broken 5m-mom-direction-sign check (was rejecting valid sweeps because pre-sweep drift contaminates 3-candle momentum); wired MSS confirmation as soft penalty (missing = -8, mismatch = hard reject)** | `src/channels/scalp.py:_evaluate_standard` + 4 new tests in `tests/test_channels.py::TestScalpChannel` | **2026-04-30 evening (path audit #1)** |
| **WHALE_MOMENTUM path audit fix: scan recent_ticks window for whale (was only checking latest tick — alert visible ~50–100ms on active pairs vs. 15s scan cycle); thresholds now env-overridable per B8** | `src/detector.py:228` (whale scan) + `src/channels/scalp.py:42` (env-overridable thresholds) + 4 new tests in `tests/test_new_modules.py::TestSMCDetector` | **2026-04-30 late eve (path audit #2)** |
| **TPE path audit fix: body-conviction gate replaced with close-position-in-range — old `body/range ≥ 0.50` punished the canonical hammer/shooting-star reclaim that defines a valid pullback entry; new gate accepts strong directional close while allowing the EMA-test wick** | `src/channels/scalp.py:1127` | **2026-04-30 late eve (path audit #3)** |
| **LIQ_REV path audit fix: RSI thresholds relaxed 25/75 → 35/65 (with RSI direction-of-travel check via rsi_prev) — pre-fix demanded RSI extreme exhaustion that 5m RSI rarely reaches during normal cascades; zone-proximity gate now also accepts cascade extremum (low/high) within 0.5% of zone, not just close_now — cascades overshoot zones by definition** | `src/channels/scalp.py:1382` (RSI gate) + `:1405` (zone gate) + 6 new tests in `tests/test_liquidation_reversal_tp.py` | **2026-05-01 very late (path audit #4)** |
| **VSB path audit (multi-fix): (A) removed broken current-candle volume gate (62.7% of rejections — was rejecting partial-candle volumes vs complete-candle thresholds, contradicting "surge + pullback" thesis); (B) breakout qualifier now requires close above swing_high — wick-only piercing was being accepted as breakout (was a sweep, not a breakout); (C) SL anchored to LOWER of `swing_high × 0.992` and `close − max(0.8%×close, 1×ATR)` — pre-fix produced 0.05% stops in extended pullback zones; (D) breakout vol multiplier now env-overridable via VSB_BREAKOUT_VOL_MULT (B8)** | `src/channels/scalp.py:1799` + `:1825` (close gate) + `:1907` (SL geometry) + `:46` (env constant) + 6 new tests in `tests/test_channels.py::TestVolumeSurgeBreakoutRefinements` | **2026-05-01 very late (path audit #5, re-audit)** |
| **BDS path audit (multi-fix mirror of #5): (A) removed broken current-candle volume gate (same 62.7% pattern — dead-cat bounces have reduced volume by definition); (B) breakdown qualifier now requires close BELOW swing_low — wick-only piercing was being accepted but is a bullish sweep, not a breakdown; (C) SL anchored to HIGHER of `swing_low × 1.008` and `close + max(0.8%×close, 1×ATR)` — pre-fix produced 0.05% stops in extended bounce zones; (D) shares VSB_BREAKOUT_VOL_MULT env constant for breakdown-candle vol gate** | `src/channels/scalp.py:2059` + `:2086` (close gate) + `:2153` (SL geometry) + 6 new tests in `tests/test_channels.py::TestBreakdownShortRefinements` | **2026-05-02 (path audit #6)** |
| **ORB path audit (dormant-path triage): path is feature-flag-disabled (`SCALP_ORB_ENABLED=false`); audit clarified the live monitor `regime_blocked=100%` was the disable token, NOT a regime gate.  Telemetry fix: dormant-flag check now reports `feature_disabled` (truthful).  Preserved-code fixes for re-enable readiness: removed broken current-candle volume gate (VSB/BDS-family bug); SL geometry now respects close-relative + 1×ATR floor (was 0.1% structural buffer producing sub-spread stops on tight ranges).  Open question on whether to rebuild session-range proxy or re-enable as-is — owner decision.** | `src/channels/scalp.py:2271` (telemetry) + `:2322` (vol gate) + `:2348` (SL geometry) + 3 new tests in `tests/test_pr06_orb_disable.py::TestORBAuditFixes` | **2026-05-02 (path audit #7)** |
| **SR_FLIP path audit: (A) TP1 ATR-adaptive cap was claimed deployed in OWNER_BRIEF Audit-3 but actually missing from the SR_FLIP code (only TPE had it) — added 1.8R/2.5R/uncapped-by-atr-percentile cap, addressing the documented historical 100% SL rate; (B) evaluator-level VOLATILE_UNSUITABLE regime block added (was VOLATILE-only — defence-in-depth)** | `src/channels/scalp.py:2479` (regime) + `:2738` (TP1 cap) + 4 new tests in `tests/test_channels.py::TestSrFlipRetestRefinements` | **2026-05-02 (path audit #8)** |
| **FUNDING path audit (3-fix shipped after CTE recommendation accepted): (A) `close <= 0` now emits `invalid_price` instead of conflating with `funding_not_extreme` telemetry; (B) TP1 ATR-adaptive cap (1.8R/2.5R/uncapped) — structure-anchored TP1 could sit 5-10R from close in trending markets, unreachable for mean-reversion contrarian setup before SL; (C) FUNDING_EXTREME_SIGNAL added to QUIET_SCALP_BLOCK exempt list at confidence ≥ 60 — was the truth report's "most likely bottleneck" with 95 candidates/28h all dying at scanner; lower bar than DIV_CONT's 64 because extreme funding is itself the quality evidence** | `src/channels/scalp.py:2910` (reject reason) + `:2989` (TP1 cap) + `src/scanner/__init__.py:318` (`_QUIET_FUNDING_MIN_CONFIDENCE`) + `:4421` (exempt branch) + 10 new tests across `tests/test_pr07_specialist_path_quality.py` and `tests/test_audit_findings.py` | **2026-05-02 (path audit #9)** |
| **QCB path audit: (A) removed partial-candle volume gate (`volumes[-1] >= 2.0 × avg_vol`) — same VSB/BDS/ORB family bug; especially backward for QCB which requires QUIET regime; (B) SL geometry now respects close-relative + 1×ATR floor (max(0.8% × close, 1×ATR)) — pre-fix flat 0.3% close-floor was sub-spread on most pairs, defeated by universal 0.80% floor downstream** | `src/channels/scalp.py:3142` (vol gate) + `:3163` (SL geometry) + 3 new tests in `tests/test_channels.py::TestQuietCompressionBreakAuditFixes` | **2026-05-02 (path audit #10)** |
| **DIV_CONT path audit: (A) `close <= 0` now emits `invalid_price` instead of conflating with `momentum_reject` telemetry; (B) SL geometry now respects close-relative + 1×ATR floor — pre-fix `ema21 × 0.995` could produce 0.6% sl_dist when close was very near EMA21, defeating universal 0.80% floor; (C) TP1 ATR-adaptive cap (1.8R/2.5R/uncapped) consistent with SR_FLIP / TPE / FUNDING — 10-candle swing extremum can sit 4-5R from close in strong trends.  Plus updated 1 stale test (test_tp2_*) — strict-equality assertion held only because old tight SL kept sl_dist small; refactored to assert structural invariant** | `src/channels/scalp.py:3327` (reject) + `:3406` (SL) + `:3454` (TP1 cap) + 2 new tests + 1 updated test in `tests/test_divergence_continuation_tp.py` | **2026-05-02 (path audit #11)** |
| **CLS path audit: (A) `close <= 0` now emits `invalid_price` instead of conflating with `momentum_reject` telemetry; (B) SL geometry now respects close-relative + 1×ATR floor — pre-fix `sweep_level ± 0.3×ATR` with `0.5×ATR` minimum could produce 0.15% sl_dist when sweep_level was very near close, defeating universal 0.80% floor; (C) TP1 ATR-adaptive cap (1.8R/2.5R/uncapped) consistent with SR_FLIP / TPE / FUNDING / DIV_CONT — FVG-anchored TP1 can sit several R from close in strong trends** | `src/channels/scalp.py:3621` (reject) + `:3708` (SL) + `:3768` (TP1 cap) + 2 new tests in `tests/test_channels.py::TestContinuationLiquiditySweepAuditFixes` | **2026-05-02 (path audit #12)** |
| **PDC path audit: (A) `close <= 0` now emits `invalid_price` instead of conflating with `auction_not_detected` telemetry; (B) SL geometry now respects close-relative + 1×ATR floor — pre-fix `consol_low ± 0.3×ATR` with `0.5×ATR` min could produce 0.2-0.4% sl_dist (PDC's design IS narrow consolidation), defeating universal 0.80% floor.  TP cap explicitly NOT applied — PDC's TP1 = displacement_height × 1.0 is a structural Type-C measured-move target, capping by ATR would defeat the projection thesis** | `src/channels/scalp.py:3933` (reject) + `:4079` (SL) + 2 new tests in `tests/test_channels.py::TestPostDisplacementContinuationAuditFixes` | **2026-05-02 (path audit #13)** |

---

## Per-Setup SL Cap Table (live as of 2026-04-29 channel cap raise)

**Channel cap (`_MAX_SL_PCT_BY_CHANNEL["360_SCALP"]`) is now 3.0%.**
Before today's change, this acted as a tighter-wins cap that silently capped
FAR/QCB/TPE/FUNDING at 2.5% even though their per-setup caps are 3.0%.

| Setup | Cap | Policy |
|---|---|---|
| RANGE_REJECTION | 1.5% | compress |
| RANGE_FADE | 1.5% | compress |
| DIVERGENCE_CONTINUATION | 1.5% | reject |
| EXHAUSTION_FADE | 2.0% | compress |
| WHALE_MOMENTUM | 2.0% | compress |
| OPENING_RANGE_BREAKOUT | 2.0% | compress |
| LIQUIDITY_SWEEP_REVERSAL | 2.0% | compress |
| LIQUIDATION_REVERSAL | 2.0% | reject |
| VOLUME_SURGE_BREAKOUT | 2.0% | reject |
| BREAKDOWN_SHORT | 2.0% | reject |
| CONTINUATION_LIQUIDITY_SWEEP | 2.0% | reject |
| SR_FLIP_RETEST | 2.5% | reject |
| POST_DISPLACEMENT_CONTINUATION | 2.5% | reject |
| FAILED_AUCTION_RECLAIM | 3.0% | reject |
| QUIET_COMPRESSION_BREAK | 3.0% | reject |
| TREND_PULLBACK_EMA | 3.0% | reject |
| FUNDING_EXTREME_SIGNAL | 3.0% | reject |

Tighter of per-setup cap vs channel cap always wins (`_max_sl_pct_for_policy()`).

---

## Known Live Issues

1. **Win-rate still unvalidated** — only 1 closed signal in latest 28h zip
   (QCB at -0.086% PnL). Need non-QUIET regime for meaningful sample.
2. ~~HYPEUSDT QCB gate penalty — 89.2 → 67.6 due to single -21.6 soft-gate penalty.~~
   **RESOLVED 2026-04-30**: source was `volume_div` (12.0 × 1.8 QUIET mult = 21.6).
   Structural mismatch with QCB thesis. Modulation entry shipped; penalty now ~13.0.
   Spoof gate (also 12.0 × 1.8) intentionally left unmodulated — orderbook
   anomalies are informative regardless of setup type.
3. **`cvd_candles=0` on some pairs** — ZBTUSDT, BSBUSDT, SWARMSUSDT. Low-volume pairs
   not covered by boot seed. CVD-gated evaluators silent on these until ~100 live 1m candles
   accumulate (~100 min post-start).
4. **`币安人生USDT` in scan universe** — Chinese-character symbol, likely a promo/test ticker.
   Burns a scan slot. Will fall out on next volume-sort cycle. No action needed.
5. **Market QUIET ~99.7% of latest 28h window** — 9/14 paths regime-blocked
   (correct behavior); QUIET_SCALP_BLOCK gate filters all 360_SCALP setups
   except QCB (always exempt) and DIV_CONT (conf ≥ 64). Signal throughput
   capped until regime shifts.
6. **DISTRIBUTION gate untested** — penalty fires but calibration unknown. Watch LONG
   suppression rate in next zip; reduce to 10pts if > 30% of LONGs suppressed.
7. **liquidation_clusters absent in 100% of cycles** — Expected in QUIET (no
   liquidation cascades occurring). Wiring is intact (`bootstrap.py:385`).
   Only consumer is FUNDING_EXTREME with graceful ATR fallback. Not a bug.
8. **Futures WS connection drops every ~15 min (alert spam now silenced).**
   Owner reported repeating `⚠️ REST fallback activated for futures critical pairs.`
   alerts every ~15 min for 3 days. Root cause: staleness watchdog at
   `src/websocket_manager.py:484` force-closes the futures WS when `last_pong`
   isn't updated for `WS_HEARTBEAT_INTERVAL_FUTURES (60) × WS_STALENESS_MULTIPLIER_FUTURES (15) = 900s`.
   Reconnect succeeds on first attempt (under 2s); the per-drop "WebSocket
   connection lost" alert is gated by `reconnect_attempts ≥ 2` so it stays
   silent — but the REST-fallback alert had no cooldown, firing every time.
   Most likely underlying cause: aiohttp consumes Binance's server-side PING
   frames internally with `heartbeat=60` set, and the kline TEXT stream
   silently stops every ~15 min on Binance's combined `/ws/<s1>/<s2>/...`
   endpoint without a TCP RST. Watchdog correctly catches it.
   **System impact: zero** — engine healthy, signals flowing, reconnect
   clean. **Two-stage fix this session**: PR #242 added a 600s cooldown,
   but with drops every 900s the alert still fired every cycle (cooldown
   < drop interval). Superseded by a **60s grace period**: the alert is
   delayed by 60s and only fires if REST fallback is still active when
   the timer expires. Transient drops (reconnect under 2s) stay silent;
   sustained outages still surface, with a cooldown still layered on top
   to coalesce repeat alerts during prolonged degradation.

---

## Phase 1 Scorecard (last known)

| Metric | Required | Status |
|---|---|---|
| Win rate (TP1 or better) | ≥ 40% | ~9% pre-Audit-3 — unvalidated post-fix |
| SL hit rate | ≤ 60% | **11.1%** ✅ |
| Signals per day | ≥ 5 | **~13.6/day** ✅ |
| Active paths | ≥ 6 | **6 of 14** ✅ |
| Fast failures | 0 | **0%** ✅ |
| Max consecutive SL losses | ≤ 5 | Non-consecutive ✅ |

Blocker: win rate. Per-setup SL caps + TP1 ATR-adaptive caps address structural causes.

---

## Next PR Queue

| Priority | Task | Status |
|---|---|---|
| 1 | QCB/FAR cap fix VALIDATED (12 + 2 emissions in latest zip) | ✅ Done |
| 2 | Audit-3 fixes verified deployed in code (TPE/DIV_CONT/FUNDING/LIQ_REV) | ✅ Done |
| 3 | 360_SCALP channel cap 2.5% → 3.0% — unlocks per-setup 3.0% caps | ✅ This session |
| 4 | Mover promotion REST+CVD seed on promotion (PR #233 follow-up) | ✅ This session |
| 5 | REST-fallback admin-alert cooldown (PR #242) — *insufficient: 600s cooldown < 900s drop interval, alerts still fired every cycle* | ⚠️ Superseded |
| 5b | REST-fallback admin-alert 60s grace period (this session) — transient drops stay silent | ✅ This session |
| 6 | Validate mover signals firing on next zip — search for VSB/BREAKDOWN_SHORT emissions on non-top-75 symbols | Observation |
| 7 | HYPEUSDT QCB -21.6 gate penalty source — diagnosed (volume_div) + modulation shipped | ✅ This session |
| 8 | Validate channel cap raise on next monitor zip | Observation |
| 9 | Monitor zip — validate Audit-3 path activation under non-QUIET regime | Observation (regime-gated) |
| 10 | Win-rate check — needs ≥20 closed signals in non-QUIET regime | Data validation |
| 11 | Investigate ORB / CLS / PDC silence under non-QUIET regime | Code investigation |
| 12 | DISTRIBUTION gate calibration (conditional on next zip) | Conditional |
| 13 | **Pre-existing test breakage cleanup** — was 136 failures on main (mostly stale assertions from refactors: SL cap raises, removed `_evaluate_range_fade`, dead channels SWING/SPOT/GEM/OBI, outcome-string refactor, mock kwarg additions, hold-time formatter changes).  Cleanup PR #N takes the suite from 136 failed → 0 failed (3302 passed, 13 skipped for removed features, 52 xfailed with structured rationale, 12 xpassed — markers to revisit).  Two follow-ups remain: (a) the 12 `xpassed` markers should be re-evaluated and removed if their root cause is gone; (b) `importlib.reload(config)` calls in test_pr04/test_pr06/test_channel_merge cause cross-test contamination of `from config import …` references — proper fix is to switch those tests to `monkeypatch.setattr` instead. | ✅ Fixed (cleanup PR) |
| 14 | Diagnose underlying 15-min futures WS drop (needs VPS-side `_health_watchdog` "stale WS connection" log) | Investigation |
| 15 | **Path audit #1: LSR (`_evaluate_standard`) — broken mom-sign removed, MSS gate wired** | ✅ Merged |
| 16 | **Path audit #2: WHALE_MOMENTUM — whale-alert single-tick bug fixed, thresholds env-overridable** | ✅ Merged (#246) |
| 17 | **Path audit #3: TREND_PULLBACK_EMA — body-conviction gate replaced with close-position-in-range** | ✅ Merged (#248) |
| 18 | **Path audit #4: LIQUIDATION_REVERSAL — RSI thresholds 25/75→35/65 + cascade-extremum zone proximity** | ✅ Merged (#249) |
| 18b | **Path audit #5: VOLUME_SURGE_BREAKOUT — removed broken current-candle volume gate** | ✅ This session — fresh PR pending |
| 18c | Path audit #6 — next path (BREAKDOWN_SHORT per OWNER_BRIEF order — likely has the same `current_vol` bug as VSB at `src/channels/scalp.py:2029`) | Pending owner go-ahead |
| 19 | LSR follow-up: validate momentum_reject rate drops on next monitor zip; check MSS_MISSING flag prevalence in emitted LSRs | Observation |
| 20 | WHALE_MOMENTUM follow-up: validate whale_alert detection rate jumps in next zip; check that `momentum_reject` count drops substantially on `EVAL::WHALE_MOMENTUM` | Observation |
| 21 | TPE follow-up: validate body_conviction_fail count drops on `EVAL::TREND_PULLBACK` once a non-QUIET regime returns; check whether TPE starts producing emissions when the regime gate finally permits | Observation |
| 22 | LSR open question: should LSR be added to `STRUCTURAL_SLTP_PROTECTED_SETUPS` so the FVG-anchored TP1 + 20-candle swing TP2 the evaluator computes survive `_assign_tps`? Currently they're discarded in favour of fixed 1.2/2.1/3.0R cadence. Adding it would also flip the SL cap from compress to reject — owner decision required | Pending owner decision |
| 23 | WHALE_MOMENTUM open question: tier-aware whale threshold (TOP=$1M, MIDCAP=$250k, SMALLCAP=$100k) — needs `pair_profile` plumbed into `SMCDetector.detect()`. Currently global threshold can be tuned via `WHALE_TRADE_USD_THRESHOLD` env. Tier-aware is cleaner but architecturally invasive | Pending data evidence |
| 24 | TPE open question: evaluator-level hard-block for STRONG_TREND and BREAKOUT_EXPANSION even though `signal_quality.py` allows them — documented as "revisit" but unresolved. Restoring those regimes may unlock more TPE emissions in mature trends | Pending data evidence |
| 25 | **Branch strategy decision needed**: standing instruction says develop on `claude/session-setup-JnbBe`. Owner asked for "PR every time" — current approach: rebase the branch onto main after each merge so each per-path PR is single-scope. Working pattern this session. | Resolved (rebase-after-merge) |

---

## Open Risks

- **New path signals untested** — LIQ_REV, DIV_CONT, FUNDING_EXT have never fired live
  (only QCB and FAR emitted in latest zip; rest were regime-blocked).
  First signals from these paths must be manually reviewed when regime allows.
- **DISTRIBUTION gate false positive** — ranging market may misclassify as DISTRIBUTION.
- **MOM-PROT SL exposure** — watch total SL rate.
- **CVD 10-candle divergence quality** — monitor DIV_CONT SL rate; revert if > 50%.
- **Channel cap raise side effect (this session)** — FAR/QCB/TPE/FUNDING signals
  may now use 2.5–3.0% SL geometry that was previously rejected. Watch SL hit
  rate on these 4 paths in the next zip; if > 60%, the per-setup 3.0% cap may
  be too loose for live conditions.
- **Mover promotion seed cost** — each newly-promoted mover incurs ~6 REST kline
  fetches (1m/5m/15m/1h/4h/1d × 500 candles) in parallel within the scan
  cycle. With `MOVER_PROMOTION_MIN_PCT=15.0` and a typical market this is
  1–3 movers per cycle = 6–18 weight-1 calls, well within Binance's 1200/min
  futures budget. Watch scan latency telemetry — if it spikes during high-
  volatility regimes (many movers qualifying simultaneously), consider
  staggering seeds across cycles.
- **Mover WS lag** — promoted pairs do NOT get WS subscriptions (deliberate;
  `update_streams_for_top50` does a stop→start). For the 75-second TTL, scan
  works off the REST seed snapshot; 1m candles don't update live. Adequate
  for VSB/BREAKDOWN setup detection (which look at closed 5m/1h structure)
  but not suitable if we ever extend the mover allowlist to setups that need
  live tick data.

---

## Deferred (Not In Phase 1 Budget)

- T4.1 Daily BTC bias filter — cross-instrument dependency, Phase 2
- T4.2 Regime-adaptive TP1 multipliers — needs per-regime hit rate data first
- Pair universe expansion — validate current 75 first
- Orderblock detection (Q2) — Phase 2 spec

---

*Read alongside `OWNER_BRIEF.md` at every session start.*
*Update this file at every session end.*
