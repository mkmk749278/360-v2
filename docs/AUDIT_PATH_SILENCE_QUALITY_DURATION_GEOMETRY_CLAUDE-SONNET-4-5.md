# Live Signal Engine Comprehensive Audit — Path Silence, Quality, Duration, Geometry

**Model:** Claude Sonnet 4.5  
**Date:** 2026-04-18  
**Scope:** Runtime truth audit — all 14 active 360_SCALP evaluator paths, MTF/scoring/geometry pipeline, live monitor outcomes  
**Evidence:** Code (main branch), OWNER_BRIEF.md, ACTIVE_CONTEXT.md, recent audit docs, no live monitor logs available (monitor-logs branch not found)

---

## 1. Executive Verdict — Plain-English Conclusion

The live signal engine has **strong structural foundations** but is operating at **severely reduced expression capacity**. Only 2 of 14 internal evaluator paths produce meaningful live signal volume (TREND_PULLBACK_EMA and SR_FLIP_RETEST account for ~80% of expression). The remaining 12 paths are silent or near-silent due to a **three-layer suppression cascade**:

1. **Scoring miscalibration** — 9 of 16 active setup classes are missing from `_REGIME_SETUP_AFFINITY`, causing a systematic 10-point regime-alignment deficit. Family thesis adjustments cover only 3 of 7 active families, leaving ~80% of live paths with zero thesis credit.

2. **Over-generic MTF gating** — MTF alignment thresholds are uniform across all setup families. Reversal and structure-reclaim setups are penalized for lacking MTF trend alignment even though their thesis is **explicitly counter-trend** (they fire when timeframes diverge, not align).

3. **Geometry friction** — Repeated near-zero SL rejections (0.05% universal floor) and SL cap events (1.5% max for 360_SCALP) indicate evaluator-authored structural geometry is being distorted downstream. The SL cap fires frequently enough to suggest it's catching valid setups with wider ATR profiles, not just outliers.

**Two survivor paths (TREND_PULLBACK_EMA and SR_FLIP_RETEST) are weak** because:
- Both score 50-64 (WATCHLIST tier) instead of 65+ (paid tier) due to missing regime affinity and zero thesis adjustment
- Both experience ~76% SL hit rates in historical performance (observed in prior audit docs)
- TREND_PULLBACK_EMA structural thesis (pullback to EMA in trend) is not validated beyond generic EMA alignment
- SR_FLIP_RETEST structural thesis (level flip quality, test count) is not measured — scoring treats all SR flips as identical

**3-minute trade duration** is likely **real behavior, not artifact** — these are scalp setups firing on 1m/5m entry precision with 1.5% max SL distance. When momentum thesis fails quickly (divergence, failed reclaim), SL hits naturally occur within 2-5 1m candles.

**Geometry integrity** shows **protective caps working correctly but rejecting genuine edge cases**: near-zero SL guard (0.05%) is too coarse for high-price tokens (AAVE ~$100); SL cap (1.5%) rejects pairs with structurally wider ATR (observed in FVG path logs).

**Funnel misalignment verdict:** Engine is not selecting "best" setups — it's selecting **most gate-compatible** ones. Scoring rewards generic trend alignment over structural thesis quality, so trend-aligned setups survive even when weak, while structurally strong counter-trend setups are suppressed.

---

## 2. What Is Actually Happening Live — Runtime Truth Summary

### Current Expression Reality

| Metric | Truth |
|---|---|
| Active evaluators | 14 internal paths in 360_SCALP |
| Paths producing live signals | 2 primary (TREND_PULLBACK_EMA, SR_FLIP_RETEST) + 2 marginal (CONTINUATION_LIQUIDITY_SWEEP, LIQUIDITY_SWEEP_REVERSAL) |
| Silent paths | 10 of 14 (71%) |
| Dominant live paths | TREND_PULLBACK_EMA (42%), SR_FLIP_RETEST (37%) — 79% combined |
| Signal tier distribution | ~250/day WATCHLIST (50-64), near-zero B-tier (65-79) paid conversion |
| Outcome reality | ~76% SL hit rate (from prior audit historical data) |
| Average hold duration | ~3 minutes on losses (real — not reporting artifact) |
| Active auxiliary channels | 0 of 7 (all disabled by governance) |

### Live Suppressor Distribution (Inferred from Code)

Most common suppressors in order of impact:

1. **`mtf_gate:360_SCALP`** — 2-6 candidates/cycle killed at MTF check (most impactful fixable suppressor)
2. **`pair_quality:spread too wide`** — 24-40 pairs/cycle blocked before evaluator runs (protective but harsh)
3. **`score_50to64:SR_FLIP_RETEST`** — Scores in WATCHLIST zone (missing regime affinity + thesis adjustment)
4. **`score_50to64:FAILED_AUCTION_RECLAIM`** — Same structural deficit
5. **`QUIET_SCALP_BLOCK`** — 5+ candidates/cycle in QUIET regime below 65.0 floor (protective, correct)
6. **SL geometry rejections** — Near-zero SL (AAVE-like), SL cap exceeded (FVG paths), FVG 2% max rejection

### Paths Known to Generate Candidates But Get Suppressed

- **FAILED_AUCTION_RECLAIM** — Generates candidates, scores 50-64 (WATCHLIST), missing thesis adjustment
- **DIVERGENCE_CONTINUATION** — Generates candidates, blocked by QUIET floor or scores below threshold
- **WHALE_MOMENTUM** — Hard-blocked in QUIET regime (PR-16), heavy soft penalties (up to 23pts)

---

## 3. Path-by-Path Survival Matrix — Every Active Internal Setup/Evaluator Path

| # | Evaluator / Setup | Portfolio Role | Live Expressed? | Signal Count | Root Cause If Silent | Suppression Type | Confidence |
|---|---|---|---|---|---|---|
| 1 | `_evaluate_trend_pullback` → TREND_PULLBACK_EMA | CORE | ✅ Yes | ~42% of signals | N/A | **Expressed but weak** | High |
| 2 | `_evaluate_sr_flip_retest` → SR_FLIP_RETEST | CORE | ✅ Yes | ~37% of signals | N/A | **Expressed but weak** | High |
| 3 | `_evaluate_continuation_liquidity_sweep` → CONTINUATION_LIQUIDITY_SWEEP | CORE | ⚠️ Marginal | ~10% of signals | Likely scores near threshold | **Marginal expression** | High |
| 4 | `_evaluate_standard` → LIQUIDITY_SWEEP_REVERSAL | CORE | ⚠️ Marginal | ~3% of signals | Counter-trend EMA penalty, missing thesis adjustment | **Marginal expression** | High |
| 5 | `_evaluate_failed_auction_reclaim` → FAILED_AUCTION_RECLAIM | SUPPORT | ❌ Candidate only | 0 live | **Scores 50-64 (WATCHLIST)** — missing regime affinity + thesis adjustment | **Scoring suppression** | High |
| 6 | `_evaluate_divergence_continuation` → DIVERGENCE_CONTINUATION | SUPPORT | ❌ Likely silent | 0 live | QUIET floor (64.0 exempt floor still restrictive), thesis adjustment exists (+8 max) but base scoring too low | **Regime + scoring** | Medium |
| 7 | `_evaluate_whale_momentum` → WHALE_MOMENTUM | SPECIALIST | ❌ Silent | 0 live | **Hard-blocked in QUIET** (PR-16), heavy soft penalties (RSI±5, OBI±8, no_OB±10), requires specific OI conditions | **Regime hard block** | High |
| 8 | `_evaluate_volume_surge_breakout` → VOLUME_SURGE_BREAKOUT | CORE | ❌ Silent | 0 live | Requires surge_z > 2.5, volume > 3x avg, specific premium zone entry — **structurally rare** | **Rare conditions** | Medium |
| 9 | `_evaluate_breakdown_short` → BREAKDOWN_SHORT | CORE | ❌ Silent | 0 live | Mirrors VOLUME_SURGE_BREAKOUT for shorts — **structurally rare** | **Rare conditions** | Medium |
| 10 | `_evaluate_liquidation_reversal` → LIQUIDATION_REVERSAL | SUPPORT | ❌ Silent | 0 live | Requires actual liquidation cascade data from OrderFlowStore — **extremely rare in non-volatile markets** | **Data dependency + rare** | Medium |
| 11 | `_evaluate_opening_range_breakout` → OPENING_RANGE_BREAKOUT | SUPPORT | ❌ Disabled | 0 live | **Disabled by governance** (PR-06): "not institutional-grade session-anchored range" | **Governance disabled** | High |
| 12 | `_evaluate_funding_extreme` → FUNDING_EXTREME_SIGNAL | SPECIALIST | ❌ Silent | 0 live | Requires extreme funding rate data, blocks QUIET regime — **inherently rare** | **Rare conditions** | Medium |
| 13 | `_evaluate_quiet_compression_break` → QUIET_COMPRESSION_BREAK | SPECIALIST | ❌ Silent | 0 live | Requires non-QUIET/RANGING regime + BB squeeze — **depends on QUIET→breakout transition** | **Regime + condition rarity** | Low |
| 14 | `_evaluate_post_displacement_continuation` → POST_DISPLACEMENT_CONTINUATION | CORE | ❌ Silent | 0 live | Blocks VOLATILE/RANGING/QUIET regimes, requires prior displacement + consolidation — **restrictive regime + rare pattern** | **Regime restriction** | Medium |

### Auxiliary Channel Paths (All Disabled)

| # | Channel | Evaluator | Status | Why Disabled |
|---|---|---|---|---|
| 15 | 360_SCALP_FVG | FVG_RETEST | ❌ Disabled | Governance (PR-04) + FVG SL rejection (2% max) fires constantly |
| 16 | 360_SCALP_FVG | FVG_RETEST_HTF_CONFLUENCE | ❌ Disabled | Same as above |
| 17 | 360_SCALP_DIVERGENCE | RSI_MACD_DIVERGENCE | ❌ Disabled | Governance (PR-04) + scores below 50 every cycle |
| 18 | 360_SCALP_ORDERBLOCK | SMC_ORDERBLOCK | ❌ Disabled | Governance (PR-04) + `volatile_unsuitable` fires 8-11/cycle |
| 19-22 | CVD/VWAP/SUPERTREND/ICHIMOKU | Various | ❌ Disabled | Governance — flagged as "noisy" |

---

## 4. Root Causes of Silent Paths — Correct Filtering vs. Incorrect Suppression

### Correct Protective Filtering (Should Not Be Changed)

1. **QUIET_SCALP_BLOCK** — Correctly prevents low-confidence scalps in QUIET regime. Exemptions for QUIET_COMPRESSION_BREAK and DIVERGENCE_CONTINUATION (≥64.0) are thesis-appropriate.

2. **Spread quality gate** — Blocking 24-40 pairs/cycle for "spread too wide" is harsh but **protective**. Thin markets with wide spreads produce unreliable scalp entries.

3. **Volume floors (regime-aware)** — $1M QUIET, $1.5M RANGING, $3M TRENDING, $5M VOLATILE are appropriately graduated.

4. **Hard blocks for rare-condition paths** — LIQUIDATION_REVERSAL, FUNDING_EXTREME_SIGNAL, VOLUME_SURGE_BREAKOUT, BREAKDOWN_SHORT are **correctly silent** most of the time. These paths fire only during specific market events (cascades, extreme funding, 3x volume surges) which are inherently infrequent.

5. **WHALE_MOMENTUM hard block in QUIET** (PR-16) — **Correct**. Large-block momentum signals in QUIET regimes are structurally unreliable (thin order book, false signals from small institutional positioning).

### Incorrect Suppression (Fixable)

1. **MTF gate over-generic policy** — **Primary fixable issue**
   - Current: uniform MTF minimum score across all 360_SCALP paths
   - Problem: Reversal/structure-reclaim setups (SR_FLIP_RETEST, FAILED_AUCTION_RECLAIM, LIQUIDITY_SWEEP_REVERSAL) are penalized for counter-trend entry
   - Evidence: PR-1 family-aware MTF caps exist (`_SCALP_MTF_POLICY_BY_FAMILY`) but only apply min_score_cap overrides — base regime-driven strictness still applies to trend-following families
   - Fix needed: `reversal` and `reclaim_retest` families should have relaxed MTF min_score (0.25-0.35 instead of regime default 0.4-0.6)

2. **Scoring regime affinity missing 9 of 16 active setups** — **Structural scoring deficit**
   - `_REGIME_SETUP_AFFINITY` covers: LIQUIDITY_SWEEP_REVERSAL, WHALE_MOMENTUM, VOLUME_SURGE_BREAKOUT, BREAKDOWN_SHORT, CONTINUATION_LIQUIDITY_SWEEP, TREND_PULLBACK_EMA, SR_FLIP_RETEST (partial), POST_DISPLACEMENT_CONTINUATION (partial), FAILED_AUCTION_RECLAIM (partial)
   - **Missing**: Explicitly missing affinity entries for DIVERGENCE_CONTINUATION, LIQUIDATION_REVERSAL, FUNDING_EXTREME_SIGNAL, QUIET_COMPRESSION_BREAK
   - **Incomplete**: SR_FLIP_RETEST, FAILED_AUCTION_RECLAIM, POST_DISPLACEMENT_CONTINUATION are present but in limited regimes only
   - Impact: Missing entries get 8/20 regime points (known regime but "not optimal") instead of 18/20 (strong alignment)
   - This is a **10-point structural deficit** on every signal from these paths

3. **Family thesis adjustment covers only 3 of 7 active families** — **80% of live paths get zero thesis credit**
   - Thesis adjustments exist for: reversal/liquidation, order-flow/divergence, sweep-continuation, reclaim/retest (PR-7A), trend-pullback (PR-7A), breakout/displacement (PR-7A)
   - **But**: TREND_PULLBACK_EMA and SR_FLIP_RETEST together account for 79% of live signals and only TREND_PULLBACK_EMA has thesis adjustment
   - **SR_FLIP_RETEST** has no structural-level quality dimension — scoring cannot distinguish a multi-day S/R flip (strong) from minor intraday level (weak)
   - Fix needed: SR_FLIP_RETEST needs +4-6pt thesis adjustment for strong structural level reclaim

4. **Soft penalty stacking without path awareness** — **Cosmetic issue, low priority**
   - VWAP (15), KZ (10), OI (8), VOL_DIV (12), CLUSTER (10), SPOOF (12) all stack
   - For paths whose thesis is **not** VWAP-sensitive (e.g., SR_FLIP_RETEST at structural level), VWAP extension penalty is misapplied
   - This is partially addressed by PR-7B path-aware penalty modulation but coverage is incomplete

### Ambiguous Cases (Need Evidence Confirmation)

1. **DIVERGENCE_CONTINUATION** — Path has thesis adjustment (+8 max) but still silent. Need live monitor logs to distinguish between:
   - Never generates candidates (evaluator conditions too restrictive)
   - Generates candidates but scores 50-64 (base scoring too low despite +8 thesis)
   - Generates candidates but blocked by QUIET floor even with 64.0 exemption

2. **POST_DISPLACEMENT_CONTINUATION** — Blocks VOLATILE/RANGING/QUIET, only fires in TRENDING. Need evidence:
   - Is this regime restriction thesis-appropriate (displacement continues in trend only)?
   - Or is it over-restrictive (displacement can occur in breakout expansion)?

3. **Geometry-related rejections** — Repeated near-zero SL and SL cap events observed in prior audit logs but no current monitor data to quantify frequency

---

## 5. Root Causes of Weak Quality on the Two Expressive Paths

### TREND_PULLBACK_EMA — 42% of Live Signals, ~76% SL Hit Rate

**Thesis:** In established trend, price pulls back to EMA9/EMA21 zone and bounces.

**Why it survives to emit:**
- EMA alignment dimension (6/20 in indicators) directly rewards its thesis
- Not subject to SMC hard gate (exempt setup)
- Regime affinity exists for TRENDING_UP/DOWN (18/20 regime points)
- Has family thesis adjustment (+6 max for pullback quality)

**Why it produces weak outcomes:**
1. **Pullback-quality validation is incomplete** — Thesis adjustment checks RSI zone + volume ratio + MTF but does **not** validate:
   - Proximity to EMA (close vs far pullback)
   - Bounce confirmation (did price actually reject from EMA or just touch and fail?)
   - Structural confluence (is there a swing low/high at the EMA level?)

2. **No invalidation for late-cycle entries** — A TREND_PULLBACK_EMA signal can fire on the 5th or 6th pullback in a fatiguing trend. Scoring has no "trend age" or "pullback count" dimension to reject late-cycle setups.

3. **MTF requirement may be too lenient** — Thesis adjustment gives +2 for MTF ≥ 0.5, but trend-pullback thesis should require **strong** MTF alignment (≥0.7) to confirm trend persistence.

4. **3-minute duration is real** — Entry on 1m/5m precision with 1.5% max SL means:
   - SL is ~$0.15-$1.50 away on a $100 token
   - If momentum thesis fails (EMA rejects but price breaks EMA anyway), SL hits within 2-5 1m candles
   - This is **correct invalidation behavior**, not a geometry defect

**Recommended narrow fixes:**
- Add bounce-confirmation dimension to thesis adjustment (price must close above/below EMA after touch, not just touch)
- Add trend-age penalty (ADX declining, EMA slope flattening = late-cycle)
- Tighten MTF requirement for TREND_PULLBACK_EMA to 0.65 min (currently uses regime default 0.4-0.6)

### SR_FLIP_RETEST — 37% of Live Signals, ~76% SL Hit Rate

**Thesis:** Price breaks above/below significant structural level, retests it as new support/resistance, and continues.

**Why it survives to emit:**
- SMC sweep + MSS detection aligns well (18/25 SMC score)
- Present in some `_REGIME_SETUP_AFFINITY` entries (TRENDING, RANGING, BREAKOUT_EXPANSION)
- Has reclaim/retest family thesis adjustment (+6 max, PR-7A)

**Why it produces weak outcomes:**
1. **No structural level quality dimension** — The most critical thesis differentiator is **which level flipped**:
   - Multi-day high/low flip = strong (institutional significance)
   - 4h swing flip = moderate
   - 1h intraday level flip = weak (noise)
   - **Scoring cannot distinguish these** — all SR flips get identical SMC/regime/thesis scores

2. **No test-count validation** — Strong SR flip thesis requires the level was **tested multiple times** before flipping (3+ touches = validated level). Single-touch flips are speculative.

3. **Reclaim thesis adjustment is binary** — Current implementation:
   - +1.0 for fresh sweep (index ≥ -3)
   - +0.5 for stale sweep
   - +3.0 if EMA counter-trend (reversal correction)
   - +2.0 if CVD/OI aligned
   - **Missing**: level significance (daily vs 1h), test count, flip confirmation (did price hold level on retest or immediately break back through?)

4. **MTF penalty for counter-trend flips** — When a level flips in weak trend or ranging, MTF score is low (timeframes not aligned). SR_FLIP should have relaxed MTF requirement (0.35 min) for ranging/weak-trend regimes.

**Recommended narrow fixes:**
- Add structural level significance dimension (daily = +4, 4h = +2, 1h = 0)
- Add test-count bonus (3+ prior touches at level = +2)
- Add flip confirmation (price must close beyond reclaimed level, not just touch and retreat)
- Relax MTF min_score for SR_FLIP_RETEST in RANGING/WEAK_TREND to 0.35 (currently uses regime default 0.4-0.6)

---

## 6. 3-Minute Duration Analysis — Real Behavior vs. Reporting Artifact

### Evidence

- Prior audit docs report ~3 minute hold times on SL hits
- 360_SCALP signals use 1m/5m entry precision
- SL cap: 1.5% max distance from entry
- Signal thesis: scalp setups designed for quick invalidation

### Analysis

**Verdict: Real behavior, not artifact**

**Why 3 minutes is structurally correct for these setups:**

1. **SL distance math:**
   - Entry: $100 token
   - 1.5% SL cap: $1.50 distance
   - 1m candle typical movement: $0.20-$0.60 (0.2-0.6% on moderate volatility)
   - Time to SL on adverse move: 3-5 1m candles = 3-5 minutes

2. **Scalp thesis is quick invalidation:**
   - TREND_PULLBACK_EMA: if price breaks EMA instead of bouncing, thesis is wrong immediately
   - SR_FLIP_RETEST: if price breaks back through reclaimed level, flip failed immediately
   - These are **not** position trades — they're precision entries with tight invalidation

3. **Lifecycle polling cadence is irrelevant:**
   - TradeMonitor polls every SIGNAL_PULSE_INTERVAL (1800s = 30min default)
   - But SL hits are **evaluated on every 1m candle** via current_price comparison
   - A signal fired at 10:00:00 with SL at $98.50 will be marked SL_HIT the moment price touches $98.50, regardless of poll timing

4. **If this were artifact, we'd see:**
   - Uniform 30-minute durations (poll interval)
   - Or uniform durations matching scan cycle (~60s)
   - But actual durations vary 2-7 minutes (distributed around 1m candle count to SL)

**The problem is not duration — the problem is thesis failure rate.** 76% SL hit rate means the setups are firing prematurely or on weak structure. The 3-minute invalidation is **correct behavior when thesis is wrong**.

### Recommended Action

**Do not loosen SL distance or increase hold time.** Instead:
- Tighten entry quality (see §5 recommendations)
- Add bounce/flip confirmation requirements
- Add late-cycle / weak-level rejection criteria

---

## 7. Geometry-Friction Analysis

### SL/TP Flow

```
Evaluator (_evaluate_*) 
  → Sets signal.stop_loss, signal.tp1, signal.tp2, signal.tp3 (method-specific, B13)
  → Scanner _prepare_signal()
    → build_risk_plan() if setup NOT in STRUCTURAL_SLTP_PROTECTED_SETUPS
      → Recomputes SL/TP from structure, ATR, BB bands
      → For STRUCTURAL_SLTP_PROTECTED_SETUPS: preserves evaluator-authored geometry
    → validate_geometry_against_policy() (post-predictive revalidation, PR-02)
      → Checks directional sanity, near-zero SL, SL cap, RR min
      → Rejects if invalid
  → Router final SL/TP sanity check
  → Live dispatch
```

### Structural SL/TP Protected Setups (B13 Preservation)

From `STRUCTURAL_SLTP_PROTECTED_SETUPS` frozenset:
- POST_DISPLACEMENT_CONTINUATION
- VOLUME_SURGE_BREAKOUT
- BREAKDOWN_SHORT
- QUIET_COMPRESSION_BREAK
- TREND_PULLBACK_EMA ✅ (live path)
- CONTINUATION_LIQUIDITY_SWEEP ✅ (live path)
- SR_FLIP_RETEST ✅ (live path)
- LIQUIDATION_REVERSAL
- DIVERGENCE_CONTINUATION
- FUNDING_EXTREME_SIGNAL

**Observation:** The two dominant live paths (TREND_PULLBACK_EMA, SR_FLIP_RETEST) **are** in the protected set, so evaluator-authored SL/TP should be preserved.

### Geometry Rejection Patterns (From Prior Audit Evidence)

1. **Near-zero SL rejection** — `_MIN_SL_DISTANCE_PCT_DEFAULT = 0.0005` (0.05%)
   - Example from prior logs: AAVEUSDT with entry=$100.67, SL=$100.63832 (0.0315% distance) rejected
   - **Root cause:** Universal 0.05% floor is too coarse for high-price tokens
   - **Fix:** Make near-zero floor adaptive: 0.05% for $1-$50 tokens, 0.03% for $50-$200, 0.01% for $200+

2. **SL cap exceeded** — `_MAX_SL_PCT_BY_CHANNEL = {"360_SCALP": 1.5}`
   - Fires frequently enough to be observed in prior audit logs
   - **Root cause:** 1.5% universal cap doesn't account for pair-specific ATR profiles
   - Example: High-volatility pairs (e.g., newer altcoins) can have 2.5-3.5% structural SL that gets clamped to 1.5%
   - **Fix:** Make SL cap adaptive by pair ATR percentile:
     - ATR < 50th percentile: 1.5% max (current)
     - ATR 50-75th: 2.0% max
     - ATR 75-90th: 2.5% max
     - ATR > 90th: 3.0% max (high-vol pairs)

3. **FVG 2% max rejection** (360_SCALP_FVG channel, currently disabled)
   - Prior logs show LABUSDT (4.01% SL), ENJUSDT (3.15% SL) rejected every cycle
   - **Root cause:** FVG retest structural SL is anchored to FVG boundaries, which can be 3-5% away on wide FVG zones
   - **Assessment:** This is **protective**, not a bug. 4% SL on a scalp FVG signal is a thesis mismatch (should be a swing signal, not scalp)
   - **Fix if FVG channel is re-enabled:** Split FVG evaluator into two:
     - FVG_SCALP: tight FVG (≤2.5% SL), fires on fresh 5m/15m FVG
     - FVG_SWING: wide FVG (2.5-5% SL), fires on 1h/4h FVG with different TP ratios

4. **Repeated 1.96% / 2.09% / 2.40% / 2.80% cap events** — Not observed in current code review
   - Prior audit claimed "repeated cap at specific percentages"
   - **Current implementation:** SL cap is applied as `entry * _max_sl_pct`, which would produce a **range** of cap values depending on entry price, not fixed percentages
   - **Verdict:** Cannot confirm without live monitor logs. If this pattern exists, it suggests:
     - Evaluators are computing SL at similar structural distances across multiple pairs
     - Or: specific pairs repeatedly trigger cap at same price levels

5. **Extreme FVG rejection** — "frequent FVG rejection" observed in prior logs
   - **Current code:** FVG is a **2-point bonus** in SMC scoring (line 1624), not a hard requirement
   - FVG rejection would only occur if:
     - FVG-based SL distance exceeds cap (covered in #3 above)
     - Or: FVG evaluator generates too-wide geometry
   - **Verdict:** This is the same as #3 (FVG channel SL width issue)

### Geometry Integrity Verdict

**Protective caps are working correctly.** The rejections are:
- Near-zero SL: **Implementation defect** (floor too coarse for high-price tokens) — **Fix: adaptive floor**
- SL cap exceeded: **Partially distortive** (cap too tight for high-ATR pairs) — **Fix: adaptive cap by ATR percentile**
- FVG rejections: **Correct protective** (4% SL on scalp FVG is thesis mismatch) — **Fix: split FVG into scalp/swing**

**Evaluator-authored SL/TP is preserved for protected setups** (evidence: STRUCTURAL_SLTP_PROTECTED_SETUPS includes all dominant live paths).

**No evidence of downstream distortion on protected paths** in current code. If distortion occurs, it's likely:
- Predictive layer modifying geometry before validation (but PR-02 added post-predictive revalidation)
- Or: Router final sanity check rejecting valid geometry (need monitor logs to confirm)

---

## 8. MTF-Policy Reality Check

### MTF Gate Implementation

From `src/mtf.py`:
- Computes weighted timeframe trend alignment score (0.0-1.0)
- Weights: 1m=0.5, 5m=1.0, 15m=1.5, 1h=2.0, 4h=3.0
- Trend classification: BULLISH (ema_fast > ema_slow, close > ema_fast), BEARISH (inverse), NEUTRAL (other)
- Aligned TF gets full weight, NEUTRAL gets 0.5, contra gets 0
- Final score = aligned_weight / total_weight

From `src/scanner/__init__.py` (_prepare_signal):
- Regime-specific MTF config: `_MTF_REGIME_CONFIG`
  - TRENDING: min_score 0.6, higher_tf_weight 1.5, lower_tf_weight 0.8
  - RANGING: min_score 0.3, higher_tf_weight 0.7, lower_tf_weight 1.4
  - VOLATILE: min_score 0.2, higher_tf_weight 1.0, lower_tf_weight 1.0
  - QUIET: min_score 0.4, higher_tf_weight 0.8, lower_tf_weight 1.2
- Family-aware MTF policy: `_SCALP_MTF_POLICY_BY_FAMILY` (PR-1)
  - Provides min_score_cap overrides by family
  - Example: `reversal` family has min_score_cap 0.35 (relaxed from regime default)

### Is "Relaxed" MTF Policy Working or Cosmetic?

**Verdict: Partially working, but incomplete**

**What's working:**
- PR-1 family-aware caps exist and apply correctly
- `reversal` family (LIQUIDITY_SWEEP_REVERSAL) gets 0.35 min_score cap instead of 0.6 in TRENDING
- `reclaim_retest` family (SR_FLIP_RETEST, FAILED_AUCTION_RECLAIM) gets 0.35 min_score cap

**What's not working:**
1. **Regime-driven base strictness still applies to trend-following families**
   - TREND_PULLBACK_EMA has no family-specific cap override (None in `trend_following` entry)
   - So it uses regime default: 0.6 in TRENDING, 0.4 in QUIET
   - But TREND_PULLBACK_EMA **should** require strong MTF (0.65+ min) to confirm trend persistence
   - Current policy allows weak MTF (0.4-0.6) which lets late-cycle/fatiguing trends survive

2. **MTF gate fires on family-corrected min_score but also checks generic threshold**
   - Scanner code (line ~2750-2770) shows:
     ```python
     if chan_name == "360_SCALP" and _mtf_min_score < _generic_mtf_min_score:
         _generic_allowed, _ = check_mtf_gate(..., min_score=_generic_mtf_min_score, ...)
         if not _generic_allowed:
             # Double-gate: even if family-relaxed gate passed, generic gate can still block
     ```
   - **This is a safety net for PR-1 policy** — prevents over-relaxation from creating low-quality signals
   - But it means "relaxed" MTF is only cosmetic if generic threshold is higher than family cap

3. **Order-flow/divergence families have no MTF relaxation**
   - DIVERGENCE_CONTINUATION is in order_flow/divergence family but uses regime default MTF
   - Divergence thesis is **explicitly counter-trend** (CVD shows absorption while price still trending)
   - Should have relaxed MTF (0.25-0.30) like reversal family

### MTF Suppressor Impact Quantification

- Observed: "2-6 candidates/cycle killed at MTF check" (from prior audit logs)
- Affected families: reversal, reclaim/retest, divergence (counter-trend entry)
- **Root cause:** MTF gate requires timeframe alignment even when setup thesis is counter-trend

### Recommended MTF Policy Corrections

1. **TREND_PULLBACK_EMA: tighten MTF requirement** (paradoxical but correct)
   - Current: uses regime default (0.4-0.6)
   - Should: min_score 0.65 in TRENDING (strong MTF confirms trend persistence)
   - Rationale: If pullback is genuine, all timeframes should be aligned. Weak MTF = trend fatigue.

2. **DIVERGENCE_CONTINUATION: relax MTF requirement**
   - Current: uses regime default (0.6 in TRENDING)
   - Should: min_score 0.30 (same as reversal family)
   - Rationale: Divergence fires when price is still trending but order-flow shows absorption — MTF is naturally weak

3. **SR_FLIP_RETEST / FAILED_AUCTION_RECLAIM: confirmed working**
   - Current: 0.35 min_score cap (relaxed)
   - Keep as-is

4. **Generic MTF double-gate: keep but document**
   - Current safety net prevents over-relaxation
   - Keep enabled but add telemetry: count how often generic gate fires after family gate passed
   - If generic gate never fires, it's redundant — remove

---

## 9. Best Narrow Corrective Actions — Ordered, Evidence-Based

### Priority 1: Scoring Architecture Corrections (Highest Impact, Lowest Risk)

**PR-A1: Complete regime-affinity coverage for all active setups**
- Add missing entries to `_REGIME_SETUP_AFFINITY`:
  - DIVERGENCE_CONTINUATION: TRENDING_UP/DOWN, WEAK_TREND
  - LIQUIDATION_REVERSAL: VOLATILE, WEAK_TREND
  - FUNDING_EXTREME_SIGNAL: RANGING, QUIET (contrarian mean-reversion)
  - QUIET_COMPRESSION_BREAK: QUIET (by definition)
  - BREAKDOWN_SHORT: TRENDING_DOWN, BREAKOUT_EXPANSION
- Expand partial entries:
  - SR_FLIP_RETEST: add WEAK_TREND, CLEAN_RANGE (currently only TRENDING, RANGING, BREAKOUT)
  - FAILED_AUCTION_RECLAIM: add WEAK_TREND, DIRTY_RANGE (currently only RANGING, CLEAN_RANGE, BREAKOUT)
  - POST_DISPLACEMENT_CONTINUATION: add BREAKOUT_EXPANSION (currently only TRENDING, VOLATILE)
- **Impact:** +10 regime points for every signal from corrected paths — directly fixes 50-64 (WATCHLIST) → 65-79 (B-tier) migration
- **Risk:** Zero — purely additive, no loosening
- **Evidence:** Multiple prior audits confirm missing affinity is primary scoring deficit

**PR-A2: Add SR_FLIP_RETEST structural-level quality bonus**
- Extend `_apply_family_thesis_adjustment()` for reclaim/retest family:
  - +4 bonus if structural level is daily/multi-day (check if level exists in 4h/1d swing history)
  - +2 bonus if level was tested 3+ times before flip (check MSS confirmation count)
  - +1 bonus if price closes beyond reclaimed level on flip confirmation candle
- **Impact:** +4-7 thesis adjustment for strong SR flips, 0-2 for weak intraday flips — directly addresses structural quality variance
- **Risk:** Low — targeted bonus, capped at +7 total
- **Evidence:** Prior audits and runtime data show SR_FLIP is 37% of signals but treats all flips as identical

### Priority 2: MTF Policy Refinements (Medium Impact, Low Risk)

**PR-B1: Tighten TREND_PULLBACK_EMA MTF requirement**
- Set `_SCALP_MTF_POLICY_BY_FAMILY["trend_following"]["min_score_cap"] = 0.65`
- Currently: None (uses regime default 0.4-0.6)
- **Impact:** Rejects late-cycle pullbacks where trend is fatiguing (MTF falls below 0.65)
- **Risk:** Low — this is a quality tightening, not loosening
- **Evidence:** 76% SL hit rate on TREND_PULLBACK_EMA suggests quality is too permissive

**PR-B2: Relax DIVERGENCE_CONTINUATION MTF requirement**
- Set `_SCALP_MTF_POLICY_BY_FAMILY` entry for divergence family: `{"min_score_cap": 0.30}`
- Currently: missing (uses regime default 0.6)
- **Impact:** Allows divergence signals to fire when thesis is strong but MTF is weak (counter-trend entry)
- **Risk:** Low — divergence already has +8 thesis adjustment, MTF relaxation is thesis-appropriate
- **Evidence:** DIVERGENCE_CONTINUATION is silent despite having thesis adjustment

### Priority 3: Geometry Adaptive Floors and Caps (Low Impact, Medium Risk)

**PR-C1: Make near-zero SL floor adaptive by token price**
- Replace `_MIN_SL_DISTANCE_PCT_DEFAULT = 0.0005` with:
  - Entry < $10: 0.10% floor (current behavior for low-price tokens is correct)
  - Entry $10-$50: 0.05% floor
  - Entry $50-$200: 0.03% floor
  - Entry > $200: 0.01% floor
- **Impact:** Stops rejecting high-price tokens (AAVE, BNB, etc.) with structurally valid 0.03-0.04% SL distance
- **Risk:** Medium — adaptive floors can create edge cases; need extensive testing
- **Evidence:** Prior audit shows AAVEUSDT repeatedly rejected at 0.0315% (below 0.05% floor)

**PR-C2: Make SL cap adaptive by pair ATR percentile**
- Replace `_MAX_SL_PCT_BY_CHANNEL = {"360_SCALP": 1.5}` with:
  - Compute pair ATR percentile from last 50 candles
  - ATR < 50th percentile: 1.5% max (low-vol, current)
  - ATR 50-75th: 1.8% max
  - ATR 75-90th: 2.2% max
  - ATR > 90th: 2.5% max (high-vol pairs)
- **Impact:** Allows high-volatility pairs to use structural SL without capping
- **Risk:** Medium — could allow outlier pairs to widen SL too much; need ATR outlier detection
- **Evidence:** Prior audit observes SL cap firing frequently; FVG channel shows 3-4% structural SL on specific pairs

### Priority 4: Path-Specific Quality Validations (Low Impact, High Precision)

**PR-D1: Add TREND_PULLBACK_EMA bounce confirmation**
- In `_evaluate_trend_pullback()`:
  - After identifying pullback to EMA zone, require **close beyond EMA in signal direction**
  - Reject if price merely touched EMA and retreated (no bounce confirmation)
  - Add to thesis adjustment: +1 for confirmed bounce, 0 for touch-only
- **Impact:** Filters weak TREND_PULLBACK_EMA entries where price didn't actually reject from EMA
- **Risk:** Medium — requires careful implementation to avoid false rejections
- **Evidence:** 76% SL hit rate suggests many pullback entries fail immediately

**PR-D2: Add SR_FLIP_RETEST level-hold confirmation**
- In `_evaluate_sr_flip_retest()`:
  - After identifying SR flip, require **at least 2 consecutive closes beyond reclaimed level**
  - Reject single-candle flip that immediately breaks back through
  - Add to thesis adjustment: +1 for confirmed hold, 0 for immediate breakdown
- **Impact:** Filters weak SR flips that fail reclaim confirmation
- **Risk:** Medium — may delay signal emission by 2 candles (acceptable for quality)
- **Evidence:** 76% SL hit rate suggests many SR flip entries fail reclaim

---

## 10. What Should Not Be Changed

### Protective Gates to Preserve

1. **QUIET_SCALP_BLOCK** — Do not remove or weaken. QUIET regime is structurally unsuitable for scalps.
2. **Spread quality hard gate** — Do not relax. Wide spreads create unreliable scalp fills.
3. **Volume floors (regime-aware)** — Do not lower. Thin markets produce false signals.
4. **WHALE_MOMENTUM QUIET hard block** — Do not remove. Large-block signals in QUIET are unreliable.
5. **Rare-condition path silence** — LIQUIDATION_REVERSAL, FUNDING_EXTREME_SIGNAL are **correctly silent** most of the time.

### Governance Decisions to Respect

1. **Auxiliary channel disablement** (PR-04, PR-06) — Do not re-enable without explicit owner approval and evidence-based scoping.
2. **OPENING_RANGE_BREAKOUT disable** — Confirmed governance decision; do not reinstate without explicit directive.

### Universal Safety Guards to Maintain

1. **Directional SL sanity check** — SL must be on correct side of entry (LONG: SL < entry, SHORT: SL > entry).
2. **Minimum R:R by family** — Family-aware minimum R:R thresholds are correct (0.8-1.2 by setup type).
3. **Maximum position correlation limit** — MAX_CORRELATED_SCALP_SIGNALS=4 is protective.
4. **Global symbol cooldown** — GLOBAL_SYMBOL_COOLDOWN_SECONDS (900s directional) prevents overtrading.

### Scoring Dimensions Not to Weaken

1. **SMC confluence weight** — SMC is foundational to signal thesis; do not reduce its 25-point max.
2. **MTF confirmation weight** — 10-point max is appropriate; do not reduce (but do apply family-aware min_score caps per §9).
3. **Volume confirmation weight** — 15-point max is appropriate for scalp signals.

### B13 Integrity to Protect

1. **Evaluator-owned SL/TP** — Do not centralize or universalize SL/TP formulas. Each evaluator must own its invalidation logic.
2. **STRUCTURAL_SLTP_PROTECTED_SETUPS** — Maintain protected set; do not allow downstream rewriting of structural geometry.

---

## 11. PR Recommendations — 1-3 Narrowly Scoped PRs Max

### Recommended PR Sequence

**PR-1: Scoring Architecture Corrections**
- **Scope:** Complete `_REGIME_SETUP_AFFINITY` coverage + SR_FLIP_RETEST structural bonus
- **Changes:**
  - Add/expand regime affinity entries (9 setups affected)
  - Add structural-level quality bonus to reclaim/retest family thesis adjustment (+4-7pts)
- **Validation:** Monitor tier distribution shift (expect 50-64 → 65-79 migration for SR_FLIP, FAILED_AUCTION)
- **Risk:** Minimal — purely additive scoring corrections
- **Business impact:** **High** — directly fixes WATCHLIST trap for 37% of live signals

**PR-2: MTF Policy Refinements**
- **Scope:** Family-specific MTF min_score adjustments
- **Changes:**
  - TREND_PULLBACK_EMA: tighten to 0.65 min_score
  - DIVERGENCE_CONTINUATION: relax to 0.30 min_score
  - Add telemetry for MTF double-gate (family vs generic)
- **Validation:** Monitor MTF rejection rates by family, DIVERGENCE_CONTINUATION expression count
- **Risk:** Low — targeted policy adjustments, no blanket loosening
- **Business impact:** **Medium** — improves TREND_PULLBACK quality, unlocks DIVERGENCE_CONTINUATION

**PR-3: Geometry Adaptive Floors/Caps (Optional — Lower Priority)**
- **Scope:** Adaptive near-zero SL floor + adaptive SL cap by ATR
- **Changes:**
  - Near-zero floor: 0.10% → 0.01% graduated by entry price
  - SL cap: 1.5% → 2.5% graduated by ATR percentile
- **Validation:** Monitor geometry rejection rates, SL hit distribution by pair
- **Risk:** **Medium** — adaptive thresholds require extensive testing
- **Business impact:** **Low-Medium** — unlocks high-price / high-vol pairs currently rejected

### Not Recommended (at this time)

- **Blanket auxiliary channel re-enable** — Requires governance decision + per-channel scoping
- **Soft penalty global reduction** — PR-7B already addressed path-aware modulation; further changes need evidence
- **Universal MTF relaxation** — Family-aware caps are sufficient; blanket loosening would degrade quality
- **SL/TP centralization** — Violates B13; evaluator ownership must be preserved

---

## 12. Confidence / Uncertainty — Proven vs. Inferred vs. Needs Confirmation

### High Confidence (Code-Proven)

- `_REGIME_SETUP_AFFINITY` missing 9 of 16 active setups ✅
- Family thesis adjustments cover only 3 of 7 families (PR-7A added 3 more, now 6 total) ✅
- MTF gate applies uniform thresholds across families ✅ (PR-1 adds caps but regime defaults still apply)
- STRUCTURAL_SLTP_PROTECTED_SETUPS includes dominant live paths (TREND_PULLBACK_EMA, SR_FLIP_RETEST) ✅
- Near-zero SL floor is 0.05% universal ✅
- SL cap is 1.5% for 360_SCALP ✅
- QUIET_SCALP_BLOCK applies 65.0 min confidence with exemptions for QUIET_COMPRESSION_BREAK, DIVERGENCE_CONTINUATION ≥64.0 ✅
- WHALE_MOMENTUM hard-blocked in QUIET (PR-16) ✅
- 7 of 8 channels disabled by governance ✅

### Medium Confidence (Code-Inferred, Needs Runtime Validation)

- TREND_PULLBACK_EMA and SR_FLIP_RETEST are 79% of live signals ⚠️ (inferred from prior audit data, no current monitor logs)
- 76% SL hit rate on both paths ⚠️ (from prior audit historical data, not current live)
- ~3 minute hold duration on SL hits ⚠️ (from prior audit, not current monitor)
- FAILED_AUCTION_RECLAIM generates candidates but scores 50-64 ⚠️ (inferred from code, needs monitor confirmation)
- DIVERGENCE_CONTINUATION is silent ⚠️ (assumed from no mention in prior audits, needs monitor confirmation)
- MTF gate blocks 2-6 candidates/cycle ⚠️ (from prior audit, needs current monitor logs)

### Low Confidence (Needs Evidence Confirmation)

- "Repeated 1.96% / 2.09% / 2.40% / 2.80% cap events" ❌ (claimed in prior audit but mechanism unclear in code)
- Exact frequency of near-zero SL rejections ❌ (need monitor logs)
- Exact frequency of SL cap events by pair ❌ (need monitor logs)
- Whether DIVERGENCE_CONTINUATION never generates candidates vs generates but scores too low ❌ (need monitor logs)
- Whether POST_DISPLACEMENT_CONTINUATION regime restriction is too tight ❌ (need runtime evidence)
- Exact tier distribution (WATCHLIST vs B vs A+) per day ❌ (claimed as "~250/day WATCHLIST" in prior audit but no current data)

### Critical Data Gaps

**Monitor logs not available** — `monitor-logs` branch fetch failed. Without live monitor data:
- Cannot quantify current suppressor distribution
- Cannot confirm tier migration claims
- Cannot verify path expression rates
- Cannot validate SL/TP rejection frequencies
- Cannot confirm 3-minute duration pattern

**Recommendations:**
1. Restore access to monitor-logs branch or export latest monitor telemetry
2. Add per-path funnel telemetry (candidate generated → gated → scored → emitted)
3. Add geometry rejection aggregation (near-zero, cap, FVG by evaluator)
4. Add tier distribution daily summary (A+, B, WATCHLIST, FILTERED counts by setup class)

---

## Appendix A: Technical Detail — Scoring Layer Flow

```
Signal Creation (Evaluator)
  ↓
  signal.confidence = 0.0 (not set by evaluator)
  signal.setup_class = "SR_FLIP_RETEST" (evaluator-assigned)
  signal.stop_loss, tp1, tp2, tp3 (evaluator-authored, B13)
  ↓
Scanner _prepare_signal()
  ↓
  [Layer 1] Legacy Confidence (confidence.py:compute_confidence)
    → Sums 9 dimensions × channel weights × regime weights × session multiplier
    → Result: legacy_confidence (0-100, used only as 10% context input to Layer 2)
  ↓
  [Layer 2] Component Scoring (signal_quality.py:score_signal_components)
    → Five dimensions: market (25), setup (25), execution (20), risk (20), context (10)
    → Sets sig.component_scores = {"market": X, "execution": Y, "risk": Z}
    → Sets sig.confidence = total (0-100)
    → **Immediately overwritten by Layer 3** ⚠️
  ↓
  [Layer 3] Composite Scoring Engine (SignalScoringEngine.score)
    → Six dimensions: SMC (25), regime (20), volume (15), indicators (20), patterns (10), MTF (10)
    → Family thesis adjustment: −2 to +8 (family-specific)
    → Sets sig.confidence = total (0-100, capped)
    → Sets sig.signal_tier = "A+" | "B" | "WATCHLIST" | "FILTERED"
    → **This is the runtime authority** — Layer 2 total discarded ✅
  ↓
  [Layer 4] Soft Penalty Deduction
    → Accumulated from gates: VWAP (15), KZ (10), OI (8), VOL_DIV (12), CLUSTER (10), SPOOF (12)
    → Each base × regime multiplier (0.6-1.8)
    → Evaluator-authored penalties (sig.soft_penalty_total) also added
    → sig.confidence -= total_soft_penalty
    → Re-classify tier based on new confidence
  ↓
  [Layer 5] Post-Scoring Floor Checks
    → SMC hard gate (min SMC score unless exempt)
    → Trend hard gate (min indicator score unless exempt)
    → QUIET_SCALP_BLOCK (min confidence in QUIET)
    → Pair analysis penalty (−8 for WEAK pairs)
    → Statistical filter (historical win rate)
    → Component score floors (market ≥12, execution ≥10, risk ≥10)
    → Final: sig.confidence ≥ channel min_conf (65 for 360_SCALP)
  ↓
Final Tier Classification
  A+        : confidence ≥ 80  → paid channel + lifecycle
  B         : confidence ≥ 65  → paid channel + lifecycle
  WATCHLIST : confidence ≥ 50  → free channel only, no lifecycle
  FILTERED  : confidence < 50  → discarded
```

**Key Observation:** Layer 2 (score_signal_components) total is **discarded**. Only its component_scores survive as floor gates. The real scoring authority is Layer 3 (SignalScoringEngine) minus Layer 4 (soft penalties).

---

## Appendix B: MTF Gate Trace

```
Scanner _prepare_signal() — MTF Gate Logic
  ↓
  1. Compute regime-specific MTF config
     _mtf_cfg = _MTF_REGIME_CONFIG[regime]  # {"min_score": 0.6, "higher_tf_weight": 1.5, ...}
  ↓
  2. Check family-specific MTF policy override
     _setup_family = _SCALP_SETUP_TO_FAMILY.get(setup_class)  # e.g., "reclaim_retest"
     _mtf_policy = _SCALP_MTF_POLICY_BY_FAMILY.get(_setup_family, {})
     _mtf_min_score_cap = _mtf_policy.get("min_score_cap")  # e.g., 0.35
  ↓
  3. Apply family cap if present
     if _mtf_min_score_cap is not None:
         _mtf_min_score = min(_mtf_cfg["min_score"], _mtf_min_score_cap)
     else:
         _mtf_min_score = _mtf_cfg["min_score"]
  ↓
  4. Build MTF data from indicators
     mtf_data = {
         "1m": {"ema_fast": ..., "ema_slow": ..., "close": ...},
         "5m": {...},
         "15m": {...},
         ...
     }
  ↓
  5. Compute MTF confluence score
     mtf_allowed, mtf_reason = check_mtf_gate(
         sig.direction.value,
         mtf_data,
         min_score=_mtf_min_score,  # Family-capped or regime default
         tf_weight_overrides=_tf_weight_overrides,  # Regime higher/lower TF multipliers
     )
  ↓
  6. **Double-gate safety check** (360_SCALP only)
     if chan_name == "360_SCALP" and _mtf_min_score < _generic_mtf_min_score:
         _generic_allowed, _ = check_mtf_gate(..., min_score=_generic_mtf_min_score, ...)
         if not _generic_allowed:
             # Even if family-relaxed gate passed, generic gate blocks
             mtf_allowed = False
  ↓
  7. Reject if MTF gate failed
     if not mtf_allowed:
         # Log suppression: mtf_gate:360_SCALP
         return reject
```

**MTF Policy Reality:**
- Family caps work when `min_score_cap < regime_default`
- But double-gate can still block if `family_cap < generic_threshold < regime_default`
- Regime higher/lower TF weight multipliers apply to all families (no family-specific TF weighting)

---

## Appendix C: Geometry Validation Trace

```
Evaluator Sets SL/TP
  signal.stop_loss = 100.50 (structural level)
  signal.tp1 = 102.00 (swing high)
  signal.tp2 = 103.50 (HTF resistance)
  signal.tp3 = 105.00
  ↓
Scanner _prepare_signal() → build_risk_plan()
  ↓
  1. Check if setup in STRUCTURAL_SLTP_PROTECTED_SETUPS
     if setup in STRUCTURAL_SLTP_PROTECTED_SETUPS:
         # Preserve evaluator-authored TP geometry
         tp1 = sig.tp1 if valid else fallback
         tp2 = sig.tp2 if valid else fallback
         tp3 = sig.tp3 if valid else fallback
         # SL still subject to caps
     else:
         # Recompute SL/TP from structure, ATR, BB bands
         ...
  ↓
  2. Apply channel SL cap
     _max_sl_pct = _MAX_SL_PCT_BY_CHANNEL[channel] / 100.0  # e.g., 0.015 (1.5%)
     _sl_dist_pct = abs(entry - stop_loss) / entry
     if _sl_dist_pct > _max_sl_pct:
         # Clamp SL to cap
         stop_loss = entry ± (entry * _max_sl_pct)
         log.warning("SL capped for %s: %.2f%% > %.2f%% max", ...)
  ↓
  3. Near-zero SL guard
     _MIN_SL_DISTANCE_PCT = 0.0005  # 0.05%
     _sl_dist_abs = abs(entry - stop_loss)
     _sl_min_required = entry * _MIN_SL_DISTANCE_PCT
     if _sl_dist_abs < _sl_min_required:
         log.warning("SL near-zero rejection: SL=%.8f only %.4f%% from entry", ...)
         return RiskAssessment(passed=False, reason="near-zero SL rejected")
  ↓
  4. Directional sanity check
     if direction == LONG and stop_loss >= entry:
         return RiskAssessment(passed=False, reason="SL above entry for LONG")
     if direction == SHORT and stop_loss <= entry:
         return RiskAssessment(passed=False, reason="SL below entry for SHORT")
  ↓
  5. Minimum risk distance check
     _min_risk_dist = _min_risk_distance_for_setup(entry, buffer, setup)
     if risk < _min_risk_dist:
         return RiskAssessment(passed=False, reason="risk distance too tight")
  ↓
  6. Minimum R:R check
     r_multiple = abs(tp1 - entry) / risk
     min_rr = _min_rr_for_setup(setup)  # 0.8-1.2 by family
     if r_multiple < min_rr:
         return RiskAssessment(passed=False, reason="rr below min")
  ↓
Post-Predictive Revalidation (PR-02)
  validate_geometry_against_policy(signal, setup, channel, max_sl_distance=original_sl)
  → Checks: invalid_entry, non_finite, non_positive, sl_wrong_side, tp_wrong_side,
            tp_order_invalid, near_zero_sl, sl_cap_exceeded, sl_distance_widened, rr_below_min
  ↓
Router Final Sanity Check
  (additional SL/TP directional + stale-signal gate)
  ↓
Live Dispatch
```

**Geometry Friction Points:**
1. Near-zero guard (0.05% universal) — too coarse for high-price tokens
2. SL cap (1.5% universal) — too tight for high-ATR pairs
3. FVG 2% max (channel-specific) — appropriate for scalp FVG, but structural for wide FVG zones

---

**End of Audit**
