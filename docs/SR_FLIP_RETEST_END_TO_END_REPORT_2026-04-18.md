# SR_FLIP_RETEST End-to-End Technical Report (2026-04-18)

- Repository: `mkmk749278/360-v2`
- Scope: How `SR_FLIP_RETEST` is generated, qualified, risk-authored, transformed, and monitored end-to-end.
- Evidence standard:
  - **Confirmed** = directly verified in current code/tests/docs
  - **Inference** = reasoned from confirmed behavior

---

## 1) Where/how SR zones or flip levels are detected for `SR_FLIP_RETEST`

### Confirmed
- Primary logic is in `ScalpChannel._evaluate_sr_flip_retest` (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1813-2102`).
- Flip level is a **single prior extrema level**, not a multi-touch zone model:
  - `prior_swing_high = max(highs[-50:-9])`
  - `prior_swing_low = min(lows[-50:-9])`
  - LONG flip when `max(highs[-9:-1]) > prior_swing_high`
  - SHORT flip when `min(lows[-9:-1]) < prior_swing_low`
  (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1886-1903`).
- SMC data comes from `SMCDetector` (`/home/runner/work/360-v2/360-v2/src/detector.py:71-247`) and includes `sweeps`, `mss`, `fvg` (`/home/runner/work/360-v2/360-v2/src/detector.py:52-65`).
- `orderblocks` are read by evaluators (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1995`) but `SMCResult.as_dict()` does not provide `orderblocks` (`/home/runner/work/360-v2/360-v2/src/detector.py:52-65`).

### Inference
- `orderblocks` are likely empty in the default runtime SMC path unless injected elsewhere.

---

## 2) Conditions required for an `SR_FLIP_RETEST` signal to be emitted

## 2.1 Evaluator-local path conditions

### Confirmed
Inside `_evaluate_sr_flip_retest`:
- Hard block in `VOLATILE` regime (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1853-1855`).
- Candle sufficiency and basic spread/volume checks (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1857-1869`).
- Structural flip found from prior/recent windows (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1886-1903`).
- Retest proximity rule:
  - reject if `dist_from_level_pct > 0.006`
  - 0.3%-0.6% gets +3 soft penalty
  (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1905-1915`).
- Reclaim/hold entry-quality checks over current+previous candle (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1927-1942`).
- Rejection-wick gate:
  - `<20%` wick/body = hard reject
  - `20%-50%` = +4 penalty
  - doji passes
  (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1944-1959`).
- EMA alignment is mandatory:
  - LONG requires `ema9 > ema21`
  - SHORT requires `ema9 < ema21`
  (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1960-1969`).
- RSI hard/soft bands:
  - LONG: reject `>=80`, penalize `>=70`
  - SHORT: reject `<=20`, penalize `<=30`
  (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1971-1989`).
- FVG/OB context:
  - hard reject in calm regimes if absent
  - +8 soft penalty in fast structural regimes
  (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1991-2001`).

## 2.2 Scanner/funnel conditions after evaluator

### Confirmed
`_prepare_signal` applies additional gates after evaluator success:
- Setup classification + channel/regime compatibility (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:2861-2873`; `/home/runner/work/360-v2/360-v2/src/signal_quality.py:812-900`).
- Execution quality gate (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:2874-2877`; `/home/runner/work/360-v2/360-v2/src/signal_quality.py:905-1040`).
- MTF gate with family cap and semantic rescue (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:2908-2994`, `2213-2261`).
- VWAP/KZ/OI/spoof/volume-div/cluster soft penalties (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:3014-3231`).
- Risk-plan pass requirement and possible geometry rewrite (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:3232-3280`).
- Composite scoring, stat filter, pair-analysis, SMC/trend gates, confidence floors (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:3503-3879`).

### Confirmed family-specific points
- `SR_FLIP_RETEST` maps to family `reclaim_retest` (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:354-355`).
- `reclaim_retest` MTF min-score cap is `0.35` (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:369`).
- `SR_FLIP_RETEST` is SMC-hard-gate exempt (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:259-266`, `3731-3760`).
- `SR_FLIP_RETEST` is **not** trend-hard-gate exempt (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:288-301`, `3762-3789`).

---

## 3) Initial SL/TP authoring for `SR_FLIP_RETEST` and invalidation doctrine

### Confirmed
- Evaluator-authored SR geometry:
  - LONG SL: `level * (1 - 0.002)`
  - SHORT SL: `level * (1 + 0.002)`
  (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:2003-2008`).
- TP logic:
  - TP1: 20-candle swing extreme fallback
  - TP2: 4h structural target fallback
  - TP3: `3.5R`
  (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:2017-2047`).
- Evaluator doctrine comments explicitly state flipped-level structural invalidation (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:2003`).
- SR is in `STRUCTURAL_SLTP_PROTECTED_SETUPS`, so risk-plan should preserve evaluator structure (`/home/runner/work/360-v2/360-v2/src/signal_quality.py:118-126`).
- Regression tests assert SR TP preservation through risk plan (`/home/runner/work/360-v2/360-v2/tests/test_signal_quality.py:1247-1265`).

---

## 4) Downstream stages that can modify/cap/reject/replace/scale geometry

### Confirmed
1. **Signal construction helper baseline**  
   `build_channel_signal()` computes generic ratios, then SR evaluator overrides with structural SL/TP (`/home/runner/work/360-v2/360-v2/src/channels/base.py:449-470`; `/home/runner/work/360-v2/360-v2/src/channels/scalp.py:2072-2079`).

2. **Risk-plan normalization (`build_risk_plan`)**  
   - Preserves evaluator SL for protected setups including SR (`/home/runner/work/360-v2/360-v2/src/signal_quality.py:1102-1108`)
   - Preserves evaluator TP values when directionally valid (`/home/runner/work/360-v2/360-v2/src/signal_quality.py:1211-1231`)
   - Applies channel SL cap (`360_SCALP=1.5%`) (`/home/runner/work/360-v2/360-v2/src/signal_quality.py:343-354`, `1111-1128`)
   - Near-zero SL rejection (`/home/runner/work/360-v2/360-v2/src/signal_quality.py:405-408`, `1135-1158`)
   - Risk-distance-too-tight rejection (`/home/runner/work/360-v2/360-v2/src/signal_quality.py:1186-1197`)
   - Setup minimum RR check (`/home/runner/work/360-v2/360-v2/src/signal_quality.py:378-386`, `1345-1349`).

3. **Scanner applies risk plan**
   - Risk-plan rejection blocks candidate (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:3232-3249`)
   - Changed/capped geometry is tracked (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:3256-3274`)
   - Risk-plan geometry is written back to signal (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:3279`, `2109-2119`).

4. **Predictive AI stage**
   - Called in scanner (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:3320-3326`)
   - SR is in predictive TP/SL bypass set (`/home/runner/work/360-v2/360-v2/src/predictive_ai.py:44-56`, `164-172`)
   - Any predictive geometry change requires policy revalidation; otherwise reverted (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:2694-2746`).

5. **Router dispatch checks**
   - TP/SL side sanity and stale checks (`/home/runner/work/360-v2/360-v2/src/signal_router.py:545-571`, `573-627`)
   - Min-confidence and risk manager checks (`/home/runner/work/360-v2/360-v2/src/signal_router.py:632-656`)
   - Risk manager applies global RR floor 1.3 (`/home/runner/work/360-v2/360-v2/src/risk.py:35`, `119-123`).

6. **Trade monitor lifecycle mutations**
   - Min-lifespan before SL/TP checks (`/home/runner/work/360-v2/360-v2/config/__init__.py:1034-1043`; `/home/runner/work/360-v2/360-v2/src/trade_monitor.py:595-604`)
   - TP hits move SL to BE/buffer/TP1 lock (`/home/runner/work/360-v2/360-v2/src/trade_monitor.py:787-794`, `768-770`, `852-858`, `834`)
   - Trailing stop ratchets SL (`/home/runner/work/360-v2/360-v2/src/trade_monitor.py:866-967`)
   - Invalidation exits are capped against SL (never worse than SL) (`/home/runner/work/360-v2/360-v2/src/trade_monitor.py:715-724`)
   - DCA recalculates entry and TP1/2/3 (SL fixed) (`/home/runner/work/360-v2/360-v2/src/dca.py:121-124`, `167-183`; called at `/home/runner/work/360-v2/360-v2/src/trade_monitor.py:623-644`).

---

## 5) Can `SR_FLIP_RETEST` emit without a visually convincing flip zone?

### Confirmed permissive criteria
- Single breakout event in recent window is sufficient; no explicit breakout-close acceptance gate (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1894-1901`).
- Flip level is a single prior extrema, not a zone-quality model (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1891-1893`).
- Retest allows up to 0.6% distance (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1911-1913`).
- Doji rejection-candle pass is unconditional in wick gate logic (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1946-1959`).
- Missing FVG/OB can still pass in fast regimes via soft penalty (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1998-2001`; tests at `/home/runner/work/360-v2/360-v2/tests/test_channels.py:1422-1468`).
- SR is SMC-hard-gate exempt in scanner (`/home/runner/work/360-v2/360-v2/src/scanner/__init__.py:259-266`, `3731-3760`).

### Inference
- On noisy alt pairs (e.g., PENGU-like behavior), these criteria can pass setups that are structurally arguable in code but weak visually.

---

## 6) Doctrine vs implementation mismatches

### Confirmed
1. Doctrine language is “confirmed S/R role-change retest,” but implementation uses one-break extrema heuristic (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1823`, `1894-1901`).
2. No SR-specific execution-quality branch exists; SR falls through generic branch in `execution_quality_check` (`/home/runner/work/360-v2/360-v2/src/signal_quality.py:924-997`).
3. Regime taxonomy mismatch:
   - evaluator fast-structural set includes values like `STRONG_TREND`/`BREAKOUT_EXPANSION` (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:88-90`)
   - runtime `MarketRegime` labels are `TRENDING_*`, `RANGING`, `VOLATILE`, `QUIET` (`/home/runner/work/360-v2/360-v2/src/regime.py:23-30`).
4. Risk-plan invalidation summary is generic “structure + buffer,” even when SR-specific evaluator SL is preserved (`/home/runner/work/360-v2/360-v2/src/signal_quality.py:1057`, `1102-1108`, `1360-1386`).

---

## 7) Likely root-cause buckets

## 7.1 Thesis-right but stop-too-tight (ZEC-like)

### Confirmed
- SR stop is fixed to flip level ±0.2% (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:2003-2008`).
- Risk-plan applies global channel cap/floor/rejection machinery (`/home/runner/work/360-v2/360-v2/src/signal_quality.py:1111-1197`).
- Router risk manager enforces global RR floor 1.3 (`/home/runner/work/360-v2/360-v2/src/risk.py:35`, `119-123`).
- Runtime monitor can end trades early due to lifecycle SL/invalidation mechanics after minimum lifespan (`/home/runner/work/360-v2/360-v2/src/trade_monitor.py:595-604`, `686-731`).

## 7.2 Flip-may-not-exist (PENGU-like)

### Confirmed
- Single-break flip logic + no breakout-close acceptance (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1894-1901`).
- Loose retest and permissive rejection patterns (including doji) (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1911-1915`, `1946-1959`).
- Optional SMC context in fast regimes (`/home/runner/work/360-v2/360-v2/src/channels/scalp.py:1998-2001`).

---

## 8) Recommended next engineering actions

## 8.1 Observability-only
- Emit SR diagnostics: breakout candle index, breakout close-vs-level delta, retest depth, wick/body ratio, premium vs extended zone flag.
- Persist geometry lineage: evaluator SL/TP -> risk-plan SL/TP -> predictive delta -> router acceptance -> monitor SL mutations.
- Add counters for `orderblocks_present` and `single-break-only` SR emissions.

## 8.2 Doctrine/logic fixes
- Require breakout **close acceptance** for flip confirmation (not only wick/high-low breach).
- Add SR-specific `execution_quality_check` branch with explicit structural anchor.
- Reconcile regime labels between evaluator soft-logic and runtime regime enum.
- Reassess SR exemption from scanner SMC hard gate if structural quality remains too permissive.

## 8.3 Geometry fixes
- Replace fixed ±0.2% SL offset with adaptive structure-aware buffer (ATR + wick-depth + level quality).
- Move from universal channel SL cap to setup-family-aware geometry constraints.
- Harmonize RR doctrine between `build_risk_plan` and router `RiskManager` floors for reclaim/retest families.
- Make DCA policy setup-aware for SR (or preserve SR structural TP doctrine through DCA transforms).

---

## Appendix: Relevant tests/docs that currently codify SR behavior

- SR evaluator behavior/regressions: `/home/runner/work/360-v2/360-v2/tests/test_channels.py:1212-1495`
- SR risk-plan TP preservation: `/home/runner/work/360-v2/360-v2/tests/test_signal_quality.py:1247-1265`
- Reclaim/retest geometry floor tests: `/home/runner/work/360-v2/360-v2/tests/test_signal_quality.py:600-751`
- Path/gating doctrine references: `/home/runner/work/360-v2/360-v2/OWNER_BRIEF.md:398-434`

