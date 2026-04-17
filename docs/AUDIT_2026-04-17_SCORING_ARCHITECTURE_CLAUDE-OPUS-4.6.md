# Scoring Architecture Deep Audit — 2026-04-17

**Author:** Claude Opus 4.6 (system-owner audit mode)
**Scope:** Full scoring pipeline — from evaluator output to paid-tier dispatch
**Status:** PR-6 merged, runtime healthy, 250+ WATCHLIST/day, weak paid conversion

---

## 1. Executive Truth

**The scoring calculation is structurally miscalibrated.** The system is alive, operationally sound, and expressing heavily — but it is expressing into the wrong tier. The 250+ daily WATCHLIST alerts prove the engine is generating candidates; the near-zero paid-tier conversion proves the scoring architecture is systematically under-crediting valid setups.

The root cause is a **three-layer scoring compression problem**:

1. **The `score_signal_components()` setup bonus is path-biased.** Only three legacy setup classes (`TREND_PULLBACK_CONTINUATION`, `BREAKOUT_RETEST`, `LIQUIDITY_SWEEP_REVERSAL`) receive the +6 setup bonus. All seven core active paths — including `SR_FLIP_RETEST`, `TREND_PULLBACK_EMA`, `VOLUME_SURGE_BREAKOUT`, `CONTINUATION_LIQUIDITY_SWEEP`, and `POST_DISPLACEMENT_CONTINUATION` — are structurally capped at `setup_score = 19` while the three legacy paths can reach `25`. This is a **6-point systemic deficit** on every signal from the engine's most active paths.

2. **The `SignalScoringEngine` family thesis adjustment is too narrow.** Only three family groups receive thesis adjustments: reversal/liquidation (max +8), order-flow/divergence (max +8), and sweep-continuation (max +4). The remaining core paths — `SR_FLIP_RETEST`, `TREND_PULLBACK_EMA`, `VOLUME_SURGE_BREAKOUT`, `POST_DISPLACEMENT_CONTINUATION`, `FAILED_AUCTION_RECLAIM`, `BREAKDOWN_SHORT` — receive **zero thesis adjustment**. These paths account for >80% of live signal expression.

3. **Soft penalties are applied after composite scoring and stack without path awareness.** A signal scoring 68 from the composite engine loses 15+ points from VWAP + KZ + VOL_DIV soft penalties (all at base weight × regime multiplier) — pushing it to 53 (WATCHLIST) regardless of whether the path thesis is even sensitive to those gates.

**Net effect:** The system's most productive paths are scored 6–14 points below their thesis-correct value, pushing the vast majority into WATCHLIST (50–64) rather than B-tier (65–79) paid signals.

---

## 2. Current Scoring Architecture — What Actually Happens at Runtime

### The Scoring Authority Chain

A signal passes through **five sequential scoring layers** before tier classification:

#### Layer 1: Legacy Confidence (`compute_confidence()` in `confidence.py`)
- Sums 9 sub-scores: SMC (0–30), Trend (0–25), Liquidity (0–20), Spread (0–10), Data Sufficiency (0–10), Multi-Exchange (0–5), Onchain (0–10), Order Flow (0–20), Sentiment (0 for SCALP)
- Applies channel weight profiles (all 1.0 for SCALP = no weighting)
- Applies regime weight adjustments (×0.6–1.5 per dimension by regime)
- Applies session multiplier (0.9 Asian, 1.0 EU, 1.05 US)
- **Max theoretical: ~130 raw × 1.05 session = capped at 100**
- This score becomes `legacy_confidence` and is used only as a 10% context input to Layer 2

#### Layer 2: Component Scoring (`score_signal_components()` in `signal_quality.py`)
- Five dimensions summing to max 100:
  - **Market** (max 25): `pair_quality.score × 0.25`
  - **Setup** (max 25): base 11 + channel_compat (+4) + regime_compat (+4) + legacy_bonus (+6 for TPC/BR/LSR only)
  - **Execution** (max 20): 8 + trigger (6) + extension quality (0–6)
  - **Risk** (max 20): `8 + min(r_multiple, 2.5) × 4.8`
  - **Context** (max 10): `legacy_confidence × 0.1` + cross-verify adjustment
- Assigns `sig.confidence = setup_score.total`
- **This is immediately overwritten by Layer 3** — Layer 2 only writes to `sig.component_scores` (keys: market, execution, risk) which are checked as floor gates later

#### Layer 3: Composite Signal Scoring Engine (`SignalScoringEngine.score()` in `signal_quality.py`)
- **This is the true runtime scoring authority.** It overwrites `sig.confidence` and `sig.signal_tier`.
- Six dimensions + thesis adjustment:
  - **SMC** (max 25): sweeps (10) + recency (5) + MSS (8) + FVG (2)
  - **Regime** (max 20): affinity (18 aligned / 8 known-unaligned / 10 unknown)
  - **Volume** (max 15): last/avg ratio (3–15 by bucket)
  - **Indicators** (max 20): MACD (7) + RSI (7) + EMA alignment (6)
  - **Patterns** (max 10): neutral 5 + aligned pattern bonus
  - **MTF** (max 10): `mtf_score × 10`
  - **Thesis Adjustment** (−2 to +8): family-specific, only for 3 families
- **Max theoretical: 25+20+15+20+10+10+8 = 108, capped at 100**

#### Layer 4: Soft Penalty Deduction (scanner `_prepare_signal()`)
- Applied **after** Layer 3 scoring
- Accumulated from up to 6 gates: VWAP (15), KZ (10), OI (8), VOL_DIV (12), CLUSTER (10), SPOOF (12)
- Each base weight × regime multiplier (0.6 trending, 1.0 ranging, 1.5 volatile, 1.8 quiet-scalp)
- **Evaluator-authored penalties** also stacked here via `sig.soft_penalty_total`
- `sig.confidence -= total_soft_penalty` then re-classify tier

#### Layer 5: Post-Scoring Gates and Floor Checks
- SMC hard gate (min SMC score unless exempt)
- Trend hard gate (min indicator score unless exempt)
- QUIET scalp block (min confidence in quiet regime)
- Pair analysis penalty (−8 for WEAK pairs)
- Statistical false-positive filter
- Final floor: `min_conf` (65 for 360_SCALP) + component score floors (market ≥12, execution ≥10, risk ≥10)

#### Tier Classification
```
A+  : confidence ≥ 80  → paid channel + lifecycle
B   : confidence ≥ 65  → paid channel + lifecycle
WATCHLIST: confidence ≥ 50  → free channel only, no lifecycle
FILTERED : confidence < 50  → discarded
```

### Key Observation
**Layers 2 and 3 both write to `sig.confidence` but Layer 3 overwrites Layer 2.** Layer 2's total is discarded; only its component_scores (market, execution, risk) survive as downstream floor gates. The real confidence authority is Layer 3 (SignalScoringEngine) minus Layer 4 (soft penalties).

---

## 3. Is the Scoring Calculation Good or Not?

**No. The scoring calculation is not good for the live system.**

It is mathematically coherent — every function computes what it claims to compute. But it is **strategically wrong** in three specific ways:

### 3A. The setup bonus in `score_signal_components()` is vestigial and biased

```python
# signal_quality.py:1394-1399
if setup.setup_class in (
    SetupClass.TREND_PULLBACK_CONTINUATION,
    SetupClass.BREAKOUT_RETEST,
    SetupClass.LIQUIDITY_SWEEP_REVERSAL,
):
    setup_score += 6.0
```

**Only three setup classes get the +6 bonus.** These are the original legacy evaluators. None of the seven core active paths (`SR_FLIP_RETEST`, `TREND_PULLBACK_EMA`, `VOLUME_SURGE_BREAKOUT`, `CONTINUATION_LIQUIDITY_SWEEP`, `POST_DISPLACEMENT_CONTINUATION`, `FAILED_AUCTION_RECLAIM`, `BREAKDOWN_SHORT`) receive this bonus.

**Impact on live system:** This doesn't directly cause WATCHLIST accumulation because Layer 3 overwrites Layer 2's total. But it **does** affect the `setup` component floor gate and creates a latent misalignment where component_scores don't reflect actual signal quality.

### 3B. The SignalScoringEngine thesis adjustment covers only 3 of 7+ active families

The `_apply_family_thesis_adjustment()` method provides adjustments for:
- **Reversal/Liquidation family** (`LIQUIDATION_REVERSAL`, `LIQUIDITY_SWEEP_REVERSAL`, `FUNDING_EXTREME_SIGNAL`, `EXHAUSTION_FADE`): up to +8 pts
- **Order-Flow/Divergence family** (`DIVERGENCE_CONTINUATION`): up to +8 pts
- **Sweep-Continuation family** (`CONTINUATION_LIQUIDITY_SWEEP`): up to +4 pts

The following active paths receive **zero thesis adjustment**:
- `SR_FLIP_RETEST` — 37% of live signals
- `TREND_PULLBACK_EMA` — 42% of live signals
- `VOLUME_SURGE_BREAKOUT` — core path
- `POST_DISPLACEMENT_CONTINUATION` — core path
- `FAILED_AUCTION_RECLAIM` — support path
- `BREAKDOWN_SHORT` — core path
- `QUIET_COMPRESSION_BREAK` — specialist path

**These zero-adjustment paths account for ~80%+ of live signal expression.** They are scored purely on the shared base model, which systematically under-credits their path-specific strengths.

### 3C. The indicator dimension structurally penalises non-trend-following paths

The `_score_indicators()` method in `SignalScoringEngine` awards up to 20 points across:
- MACD histogram alignment (max 7)
- RSI position (max 7)
- EMA alignment (max 6)

For **reversal paths** (`SR_FLIP_RETEST`, `FAILED_AUCTION_RECLAIM`, `LIQUIDITY_SWEEP_REVERSAL`), EMA is frequently counter-trend at entry because the thesis is a **structural level reclaim**, not a trend continuation. This means:
- EMA alignment: 1/6 instead of 6/6 (−5 pts)
- MACD may be counter-signal: 0–4/7 instead of 7/7 (−3 pts potential)
- RSI may be mid-range: 4/7 instead of 7/7

**Net structural deficit for reversal/reclaim paths: 5–8 points on indicators alone.**

The reversal/liquidation family gets a +3 EMA counter-trend correction via thesis adjustment, but `SR_FLIP_RETEST` and `FAILED_AUCTION_RECLAIM` — which have the same structural entry pattern — receive **zero correction** because they are not in `_FAMILY_REVERSAL_LIQUIDATION`.

---

## 4. Are All Paths Scored Too Uniformly?

**Yes.** The system applies a single shared scoring model to paths with fundamentally different theses, then provides thesis corrections for only 3 of 7+ active families.

### What the shared model scores well
- **MACD/RSI/EMA trend alignment:** Correctly rewards paths whose thesis is "enter in the direction of established trend" — i.e., `TREND_PULLBACK_EMA`, `TREND_PULLBACK_CONTINUATION`
- **Volume confirmation:** Universal and correctly weighted
- **SMC confluence:** Universal and correctly weighted
- **MTF confirmation:** Universal and correctly weighted

### What the shared model scores poorly
- **Structural level interactions:** `SR_FLIP_RETEST` and `FAILED_AUCTION_RECLAIM` enter at structural levels where the thesis is "level holds as new support/resistance." The scoring model has no dimension for structural level quality, proximity, or test count.
- **Displacement momentum:** `POST_DISPLACEMENT_CONTINUATION` and `VOLUME_SURGE_BREAKOUT` thesis is "explosive price displacement creates a continuation opportunity." The scoring model counts volume as a generic 15-pt dimension but doesn't reward the displacement-specific thesis (ATR expansion, consolidation compression, breakout velocity).
- **Counter-trend reversal quality:** `LIQUIDITY_SWEEP_REVERSAL` at structural levels scores poorly on EMA/MACD/RSI because the reversal hasn't yet completed when the signal fires. The thesis adjustment partially compensates but only +3 for EMA correction.

### Quantified uniformity impact

For a **typical SR_FLIP_RETEST signal** in WEAK_TREND regime:
- SMC: 10 (sweep at level) + 8 (MSS) = 18/25
- Regime: 18/20 (affinity match — SR_FLIP_RETEST is in WEAK_TREND affinity? **No — it's not in `_REGIME_SETUP_AFFINITY`**) → actually 8/20
- Volume: 9/15 (1.5x avg typical)
- Indicators: 6 (EMA aligned) + 4 (RSI mid) + 4 (MACD partial) = 14/20
- Patterns: 5/10 (neutral)
- MTF: 6/10 (typical 0.6 score)
- Thesis: **0** (not in any family group)
- **Total: 60/100 → WATCHLIST**

The same signal with a +5 structural-level thesis adjustment and regime affinity correction would score **73 → B-tier paid**.

---

## 5. Which Paths Are Under-Credited and Why

### SR_FLIP_RETEST (37% of live signals — most under-credited)

**Real thesis:** Price breaks above/below a significant structural level, retests it as new support/resistance, and continues. The structural level (old resistance → new support, or vice versa) is the primary edge. The reclaim of the level is the trigger.

**What the scoring model rewards:**
- SMC confluence: ✅ Sweep + MSS detection aligns well
- Volume: ✅ Standard confirmation
- MTF: ✅ Standard confirmation

**What the scoring model misses/flattens:**
- **No structural level quality dimension.** The model cannot distinguish between a flip of a multi-day high/low (strong) vs a minor intraday level (weak). This is the primary thesis differentiator.
- **Regime affinity is absent.** `SR_FLIP_RETEST` is not listed in any `_REGIME_SETUP_AFFINITY` entry, so it always gets 8/20 regime points (known regime but "not optimal"). This is **factually wrong** — SR flips are valid in TRENDING, WEAK_TREND, CLEAN_RANGE, and BREAKOUT_EXPANSION.
- **No thesis adjustment.** Zero family-specific correction. The path receives no credit for its structural thesis over generic trend-following.
- **Setup bonus absent.** Not in the +6 bonus list in `score_signal_components()`.

**Under-credit magnitude: 10–14 points (6 regime + 0–5 thesis + 0–3 structural)**
**Verdict: SEVERELY under-credited**

### TREND_PULLBACK_EMA (42% of live signals)

**Real thesis:** In an established trend, price pulls back to the EMA zone (EMA9/EMA21 area) and bounces. The trend alignment + EMA proximity is the primary edge.

**What the scoring model rewards:**
- Indicators: ✅ EMA alignment is the core thesis — this path gets the full 6/6 EMA, and MACD/RSI should also be aligned in a trend
- SMC: ✅ Sweep/MSS during pullback
- Regime: Partially. "TREND_PULLBACK_EMA" is not in `_REGIME_SETUP_AFFINITY` lists — only `TREND_PULLBACK_CONTINUATION` is listed implicitly via "BREAKOUT_RETEST" etc.

**What the scoring model misses/flattens:**
- **No pullback depth/quality dimension.** A pullback exactly to EMA21 (ideal) scores the same as a pullback that barely dipped (weak). The depth and precision of the pullback to the EMA zone is the core thesis signal.
- **Regime affinity gap.** `TREND_PULLBACK_EMA` is not explicitly listed in TRENDING_UP or TRENDING_DOWN affinity — these lists include `BREAKOUT_RETEST` and `WHALE_MOMENTUM` but not the most common trend-following path.
- **No thesis adjustment.** The comment in the code explicitly states "Trend / continuation ... shared base scoring is appropriate" — but the regime affinity gap means it's actually under-scored.

**Under-credit magnitude: 4–10 points (regime affinity 10 + possibly thesis 0)**
**Verdict: MODERATELY under-credited, primarily through regime affinity omission**

### FAILED_AUCTION_RECLAIM (support path)

**Real thesis:** Price auctions beyond a structural level (failed breakout), then reclaims back through that level. The reclaim direction is the trade direction. The auction failure is the structural evidence of directional commitment.

**What the scoring model rewards:**
- SMC: Partially — sweep detection may fire, but the path's trigger is auction failure, not a traditional liquidity sweep
- Execution: ✅ Custom execution quality check with correct anchor

**What the scoring model misses/flattens:**
- **EMA is frequently counter-trend.** The failed auction creates a reversal entry where EMA hasn't caught up → indicator score deficit of 5+ pts
- **No thesis adjustment.** Not in any family group. The +3 EMA counter-trend correction that reversal/liquidation family gets is not applied to FAR.
- **Regime affinity absent.** Not in any `_REGIME_SETUP_AFFINITY` list despite being valid in WEAK_TREND, CLEAN_RANGE, DIRTY_RANGE, and BREAKOUT_EXPANSION.
- **SMC gate exempt but not thesis-compensated.** The code correctly exempts FAR from the SMC hard gate and trend hard gate, but doesn't add positive thesis credit for the structural edge it brings.

**Under-credit magnitude: 8–13 points (EMA correction 3–5 + regime 10 + thesis 0–5)**
**Verdict: SIGNIFICANTLY under-credited**

### CONTINUATION_LIQUIDITY_SWEEP (10.5% of live signals)

**Real thesis:** In a trend, a local pullback sweeps short-term liquidity (stop hunt) and price re-accelerates in the trend direction.

**What the scoring model rewards:**
- Thesis adjustment: ✅ Up to +4 pts (CVD aligned +2, OI rising +2). This is the only moderately well-treated continuation path.
- SMC: ✅ Sweep detection directly aligns with the path trigger

**What the scoring model misses:**
- **Regime affinity partially present.** Listed in TRENDING_UP and TRENDING_DOWN affinity lists → gets 18/20 when regime matches. However, it's absent from RANGING and VOLATILE lists where it can also fire.
- **Thesis cap too low.** Max +4 vs max +8 for reversal paths. The sweep-continuation thesis is strong enough to warrant +6.

**Under-credit magnitude: 2–4 points**
**Verdict: SLIGHTLY under-credited — best-treated among active paths**

### LIQUIDITY_SWEEP_REVERSAL (2.6% of live signals)

**Real thesis:** Price sweeps a structural liquidity pool and reverses. The sweep + structural level + MSS creates the reversal edge.

**What the scoring model rewards:**
- Thesis adjustment: ✅ Up to +8 pts (EMA correction +3, OI/liq/CVD/funding +5)
- SMC: ✅ Sweep detection is the core trigger
- Setup bonus: ✅ Gets +6 in `score_signal_components()`

**What the scoring model misses:**
- **Regime affinity well-handled.** Listed in TRENDING_UP, TRENDING_DOWN, VOLATILE affinity lists.
- Minor: sweep depth quality not granularly scored in the composite engine

**Under-credit magnitude: 0–2 points**
**Verdict: FAIRLY scored — best-treated path in the system**

### VOLUME_SURGE_BREAKOUT (core path)

**Real thesis:** Explosive volume surge with price breakout beyond recent structure. The volume explosion is the primary thesis evidence.

**What the scoring model rewards:**
- Volume: ✅ Volume ratio scoring directly aligns
- Listed in TRENDING_UP, TRENDING_DOWN, VOLATILE affinity lists → good regime credit

**What the scoring model misses:**
- **No thesis adjustment.** Not in any family group. The volume surge is the path's primary thesis but it only gets the standard 15-pt volume dimension, not a thesis bonus for surge magnitude.
- **No displacement quality dimension.** A 3x volume surge breakout scores 15/15 volume, same as a 10x surge. The magnitude beyond 3x has no scoring impact.

**Under-credit magnitude: 3–5 points**
**Verdict: MODERATELY under-credited**

### POST_DISPLACEMENT_CONTINUATION (core path)

**Real thesis:** After a large displacement candle, price consolidates tightly, then re-accelerates in the displacement direction. The consolidation tightness + breakout is the thesis.

**What the scoring model rewards:**
- Indicators: Partially — EMA should be aligned after displacement
- Execution: ✅ Custom check with consolidation breakout anchor

**What the scoring model misses:**
- **No consolidation quality dimension.** Tightness, duration, and breakout velocity of the consolidation are the primary thesis signals — none are scored.
- **No thesis adjustment.** Not in any family group.
- **Regime affinity partially present.** Not explicitly listed in TRENDING_UP/TRENDING_DOWN affinity, but it's a trend continuation play.

**Under-credit magnitude: 3–6 points**
**Verdict: MODERATELY under-credited**

---

## 6. Soft-Penalty / Threshold Interaction Analysis

### Penalty Stacking Audit

For the 360_SCALP channel, soft penalty base weights are:

| Gate | Base Weight | TRENDING (×0.6) | RANGING (×1.0) | VOLATILE (×1.5) | QUIET (×1.8) |
|------|------------|-----------------|----------------|-----------------|--------------|
| VWAP | 15 | 9.0 | 15.0 | 22.5 | 27.0 |
| Kill Zone | 10 | 6.0 | 10.0 | 15.0 | 18.0 |
| OI | 8 | 4.8 | 8.0 | 12.0 | 14.4 |
| Volume Div | 12 | 7.2 | 12.0 | 18.0 | 21.6 |
| Cluster | 10 | 6.0 | 10.0 | 15.0 | 18.0 |
| Spoof | 12 | 7.2 | 12.0 | 18.0 | 21.6 |
| **Max total** | **67** | **40.2** | **67.0** | **100.5** | **120.6** |

### Key Finding: Typical 2-gate penalty in RANGING regime is 22–27 points

In a ranging market (the most common regime), if VWAP extension fires + Volume Divergence fires:
- `15 + 12 = 27 points deducted`

A signal that scored 72 from the composite engine (solid B-tier) drops to **45 → FILTERED**.
A signal that scored 78 drops to **51 → WATCHLIST**.

In QUIET regime with 1.8× multiplier:
- Same two gates: `27 + 21.6 = 48.6 points deducted`
- **Any signal below 99 from composite scoring would be filtered.**

### Most Damaging Penalties

1. **VWAP (15 base):** Fires frequently because many valid pullback entries are naturally extended from session VWAP. VWAP extension is a reasonable concern for mean-reversion plays but is **irrelevant to trend-following and breakout paths**. A `TREND_PULLBACK_EMA` signal entering at a pullback to EMA21 may be 1+ ATR from VWAP — this is the correct entry, not an overextension.

2. **Volume Divergence (12 base):** Fires when higher TF volume contradicts lower TF spike. This is valid for detecting false breakouts but **penalises VOLUME_SURGE_BREAKOUT** which is specifically designed to trade volume spikes.

3. **Kill Zone (10 base):** Session-time penalty fires outside the defined kill zone windows. Valid for execution quality but applied uniformly regardless of whether the path thesis is time-dependent.

### Which Families Are Most Disproportionately Affected?

**Reclaim/retest family** (`SR_FLIP_RETEST`, `FAILED_AUCTION_RECLAIM`): These paths enter at structural levels that may be extended from VWAP. VWAP penalty is architecturally inappropriate for structural-level entries.

**Breakout/momentum family** (`VOLUME_SURGE_BREAKOUT`, `POST_DISPLACEMENT_CONTINUATION`): Volume divergence penalty directly contradicts the path thesis. The path fires *because* of a volume surge; penalising volume divergence is penalising the thesis confirmation.

**Trend-following family** (`TREND_PULLBACK_EMA`): VWAP penalty fires on pullbacks that are naturally VWAP-extended in a trending market. The trending regime multiplier (0.6×) helps but doesn't eliminate the problem.

### Penalties Are Not Path-Aware

**Critical finding:** Soft penalties are applied uniformly to all paths. There is no mechanism to suppress or reduce a penalty when it contradicts the path thesis. This is the second major structural problem:

- `VOLUME_SURGE_BREAKOUT` should not receive full volume_divergence penalty (its thesis *is* volume divergence from the higher TF)
- `SR_FLIP_RETEST` should not receive full VWAP penalty (structural entries are not VWAP-dependent)
- `FAILED_AUCTION_RECLAIM` should not receive full indicator penalty (its thesis is structural, not trend-aligned)

---

## 7. Whether Per-Path or Per-Family Scoring Is Required

### Architecture Tiers

The correct architecture has **four tiers of scoring treatment**:

#### Tier 1: Universal Safety Standards (keep as-is)
These must remain globally uniform and path-agnostic:
- Near-zero SL guard
- Directional sanity checks
- Max SL % cap per channel
- Minimum R:R per family (already family-aware — good)
- SMC hard gate for sweep-dependent paths
- Trend hard gate for trend-dependent paths
- Correlation exposure limits
- Pair quality floor

**Status: Correctly implemented.**

#### Tier 2: Shared Base Scoring (keep, fix regime affinity)
The six dimensions of `SignalScoringEngine` are appropriate as a shared base:
- SMC confluence
- Regime alignment
- Volume confirmation
- Indicator confluence
- Candlestick patterns
- MTF confirmation

**Required fix:** The `_REGIME_SETUP_AFFINITY` dict is incomplete. Many active paths are missing from regime lists where they are valid, causing a systematic 10-point regime penalty (18 → 8) on valid signals.

#### Tier 3: Family Thesis Adjustment (expand significantly)
The existing thesis adjustment layer in `_apply_family_thesis_adjustment()` is the correct architectural mechanism. It needs expansion to cover all active families:

- **Reclaim/Retest family** (`SR_FLIP_RETEST`, `FAILED_AUCTION_RECLAIM`): Needs +3 EMA counter-trend correction + structural level quality bonus (max +5 total)
- **Trend-Following family** (`TREND_PULLBACK_EMA`): Needs pullback depth quality bonus when entry is near EMA zone (max +3)
- **Breakout/Displacement family** (`VOLUME_SURGE_BREAKOUT`, `POST_DISPLACEMENT_CONTINUATION`, `BREAKDOWN_SHORT`): Needs displacement magnitude bonus for volume/ATR expansion (max +4)
- **Quiet/Specialist family** (`QUIET_COMPRESSION_BREAK`): Current scoring may be adequate but should be explicitly confirmed with `return 0.0` family treatment

#### Tier 4: Path-Aware Penalty Modulation (new — required)
Soft penalties must become path-aware. This is not "per-path scoring" — it is "per-path penalty relevance filtering":

- When `VOLUME_SURGE_BREAKOUT` fires, reduce `volume_div` penalty weight to 0.3× (the volume divergence is the thesis, not a flaw)
- When `SR_FLIP_RETEST` or `FAILED_AUCTION_RECLAIM` fires, reduce `vwap` penalty weight to 0.5× (structural entries are not VWAP-dependent)
- When `TREND_PULLBACK_EMA` fires in TRENDING regime, reduce `kill_zone` penalty weight to 0.5× (trends trade outside kill zones)

**The correct answer is: family-aware scoring correction + path-aware penalty modulation.** Full per-path scoring is not required — the shared base + family thesis + penalty modulation architecture covers the gap.

---

## 8. Best Next Action

The current scoring is not good. The next correct move is a **combined correction**:

1. **Family-aware scoring correction** (SignalScoringEngine thesis adjustments)
   - Add thesis adjustments for reclaim/retest, trend-following, and breakout/displacement families
   - Fix `_REGIME_SETUP_AFFINITY` to include all active paths in their valid regimes

2. **Path-aware penalty modulation** (scanner soft penalties)
   - Introduce a path→penalty weight modifier dict that reduces irrelevant penalties per path
   - Does not remove any penalty entirely — only scales down penalties that contradict path thesis

3. **Setup bonus modernisation** (score_signal_components)
   - Either extend the +6 bonus to all core active paths, or remove it (since Layer 2 total is overwritten by Layer 3). The component floor gates still use Layer 2 scores, so this affects which signals pass the `setup ≥ 12` implicit requirement.

**What NOT to do:**
- Do not lower the 65 B-tier threshold
- Do not reduce penalty base weights globally
- Do not inflate the composite scoring engine maximums
- Do not add artificial "boost" points outside of family thesis logic

---

## 9. Concrete Recommendation for the Next PR

### PR Title: "Family-Aware Scoring & Path-Aware Penalty Modulation"

### Change 1: Expand `_REGIME_SETUP_AFFINITY` in `SignalScoringEngine`

```python
_REGIME_SETUP_AFFINITY = {
    "TRENDING_UP": [
        "LIQUIDITY_SWEEP_REVERSAL", "BREAKOUT_RETEST", "WHALE_MOMENTUM",
        "VOLUME_SURGE_BREAKOUT", "CONTINUATION_LIQUIDITY_SWEEP",
        # ADD:
        "TREND_PULLBACK_EMA", "SR_FLIP_RETEST",
        "POST_DISPLACEMENT_CONTINUATION", "BREAKDOWN_SHORT",
    ],
    "TRENDING_DOWN": [
        "LIQUIDITY_SWEEP_REVERSAL", "BREAKOUT_RETEST", "WHALE_MOMENTUM",
        "BREAKDOWN_SHORT", "CONTINUATION_LIQUIDITY_SWEEP",
        # ADD:
        "TREND_PULLBACK_EMA", "SR_FLIP_RETEST",
        "POST_DISPLACEMENT_CONTINUATION", "VOLUME_SURGE_BREAKOUT",
    ],
    "RANGING": [
        "RANGE_FADE",
        # ADD:
        "SR_FLIP_RETEST", "FAILED_AUCTION_RECLAIM",
    ],
    "QUIET": [
        "RANGE_FADE",
        # ADD:
        "QUIET_COMPRESSION_BREAK", "DIVERGENCE_CONTINUATION",
    ],
    "VOLATILE": [
        "WHALE_MOMENTUM", "LIQUIDITY_SWEEP_REVERSAL",
        "VOLUME_SURGE_BREAKOUT", "BREAKDOWN_SHORT",
        # ADD:
        "LIQUIDATION_REVERSAL", "FUNDING_EXTREME_SIGNAL",
    ],
}
```

**Expected impact:** +10 points for regime-aligned signals currently receiving the non-affinity penalty (18 → 8 becomes 18 → 18). This alone converts many WATCHLIST signals to B-tier.

### Change 2: Add Family Thesis Adjustments

In `_apply_family_thesis_adjustment()`:

```python
# NEW: Reclaim/Retest family
_FAMILY_RECLAIM_RETEST = frozenset({
    "SR_FLIP_RETEST",
    "FAILED_AUCTION_RECLAIM",
})

# NEW: Breakout/Displacement family
_FAMILY_BREAKOUT_DISPLACEMENT = frozenset({
    "VOLUME_SURGE_BREAKOUT",
    "POST_DISPLACEMENT_CONTINUATION",
    "BREAKDOWN_SHORT",
})
```

For reclaim/retest family:
- EMA counter-trend correction: +3 when EMA is naturally misaligned (same logic as reversal family)
- Max adjustment: +5 (capped conservatively below the +8 reversal family cap)

For breakout/displacement family:
- Volume surge bonus: +2 when volume_last/volume_avg ≥ 2.0
- ATR expansion bonus: +2 when atr_percentile ≥ 75
- Max adjustment: +4

### Change 3: Path-Aware Penalty Modulation

Add a penalty modulation dict in scanner:

```python
_PATH_PENALTY_MODULATION: Dict[str, Dict[str, float]] = {
    "VOLUME_SURGE_BREAKOUT": {"volume_div": 0.3},
    "BREAKDOWN_SHORT": {"volume_div": 0.3},
    "SR_FLIP_RETEST": {"vwap": 0.5},
    "FAILED_AUCTION_RECLAIM": {"vwap": 0.5},
    "TREND_PULLBACK_EMA": {"kill_zone": 0.5},
    "POST_DISPLACEMENT_CONTINUATION": {"volume_div": 0.5, "vwap": 0.5},
}
```

In each soft penalty block, multiply the base weight by the path modulation factor:
```python
_base = _penalty_weights.get("vwap", 12.0)
_path_mod = _PATH_PENALTY_MODULATION.get(_setup_class_name, {}).get("vwap", 1.0)
_scaled = round(_base * regime_mult * _path_mod, 1)
```

**Expected impact:** 5–15 points recovered per signal on affected paths.

### Change 4: Modernise setup bonus in `score_signal_components()`

Extend the +6 setup bonus to all core and support paths:

```python
if setup.setup_class in (
    SetupClass.TREND_PULLBACK_CONTINUATION,
    SetupClass.BREAKOUT_RETEST,
    SetupClass.LIQUIDITY_SWEEP_REVERSAL,
    # ADD all core paths:
    SetupClass.SR_FLIP_RETEST,
    SetupClass.TREND_PULLBACK_EMA,
    SetupClass.VOLUME_SURGE_BREAKOUT,
    SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
    SetupClass.POST_DISPLACEMENT_CONTINUATION,
    SetupClass.BREAKDOWN_SHORT,
    # Support paths:
    SetupClass.FAILED_AUCTION_RECLAIM,
    SetupClass.LIQUIDATION_REVERSAL,
    SetupClass.DIVERGENCE_CONTINUATION,
):
    setup_score += 6.0
```

This change primarily affects the component_scores floor gates (market ≥ 12, execution ≥ 10, risk ≥ 10) since Layer 3 overwrites the total.

### Combined Expected Impact

For a typical `SR_FLIP_RETEST` in WEAK_TREND regime:

| Dimension | Current | After Fix |
|-----------|---------|-----------|
| SMC | 18 | 18 |
| Regime | 8 (no affinity) | 18 (affinity) |
| Volume | 9 | 9 |
| Indicators | 14 | 14 |
| Patterns | 5 | 5 |
| MTF | 6 | 6 |
| Thesis adj | 0 | +3 (EMA correction) |
| **Subtotal** | **60** | **73** |
| Soft penalty (VWAP+KZ) | −25 | −17.5 (VWAP modulated) |
| **Final** | **35 → FILTERED** | **55.5 → WATCHLIST** |

Better, but still WATCHLIST. The fix moves the boundary:
- Current: Most signals FILTERED or low WATCHLIST
- After fix: Most signals mid-to-high WATCHLIST or low B-tier

For signals with only one soft penalty (single gate fire):
- Current: 60 − 15 = 45 → FILTERED
- After fix: 73 − 7.5 = 65.5 → **B-tier** ✅

The combined corrections convert the engine from "almost everything is WATCHLIST/FILTERED" to "clean signals with ≤1 soft penalty reach B-tier" — which is the correct quality boundary.

### Constraints Preserved
- ✅ No blanket threshold lowering (65 B-tier stays)
- ✅ No broad loosening (all penalties remain, just path-modulated)
- ✅ No fake score inflation (thesis adjustments are evidence-based)
- ✅ No quantity-first behavior (signals must still pass all hard gates, floor checks, and composite scoring)
- ✅ Quality discipline preserved (the 50-floor WATCHLIST, 65-floor B-tier, and 80-floor A+ tier are unchanged)

---

## Appendix A: Scoring Layer Summary

```
Evaluator → Signal (entry, SL, TP, direction, setup_class)
    ↓
Scanner._prepare_signal()
    ├── Setup classification + regime/channel compatibility gates (HARD)
    ├── Execution quality check (HARD)
    ├── MTF confluence gate (HARD)
    ├── Soft penalty accumulation (VWAP, KZ, OI, VOL_DIV, CLUSTER, SPOOF)
    ├── Risk plan generation (HARD)
    ├── Correlated exposure cap (HARD)
    ├── Legacy confidence computation (input to Layer 2 context score)
    ├── score_signal_components() → Layer 2 (overwrites confidence, but then...)
    ├── SignalScoringEngine.score() → Layer 3 (OVERWRITES confidence again — TRUE AUTHORITY)
    ├── Soft penalty subtraction from Layer 3 score → Layer 4
    ├── Tier re-classification after penalty
    ├── Statistical false-positive filter
    ├── Pair analysis penalty
    ├── SMC hard gate (post-scoring)
    ├── Trend hard gate (post-scoring)
    ├── QUIET scalp block
    ├── WATCHLIST routing (50–64 → free channel only)
    └── Final floor checks (min_conf + component floors)
        ↓
Signal Router._process()
    ├── WATCHLIST → free channel (no lifecycle)
    ├── B-tier/A+ → paid channel + lifecycle management
    └── Channel min-confidence filter (65 for 360_SCALP)
```

## Appendix B: `_REGIME_SETUP_AFFINITY` Coverage Audit

| Setup Class | TRENDING_UP | TRENDING_DOWN | RANGING | QUIET | VOLATILE | Listed? |
|------------|:-----------:|:-------------:|:-------:|:-----:|:--------:|---------|
| LIQUIDITY_SWEEP_REVERSAL | ✅ | ✅ | ❌ | ❌ | ✅ | Yes |
| BREAKOUT_RETEST | ✅ | ✅ | ❌ | ❌ | ❌ | Yes |
| WHALE_MOMENTUM | ✅ | ✅ | ❌ | ❌ | ✅ | Yes |
| VOLUME_SURGE_BREAKOUT | ✅ | ❌ | ❌ | ❌ | ✅ | Partial |
| BREAKDOWN_SHORT | ❌ | ✅ | ❌ | ❌ | ✅ | Partial |
| CONTINUATION_LIQUIDITY_SWEEP | ✅ | ✅ | ❌ | ❌ | ❌ | Partial |
| RANGE_FADE | ❌ | ❌ | ✅ | ✅ | ❌ | Yes |
| **SR_FLIP_RETEST** | ❌ | ❌ | ❌ | ❌ | ❌ | **MISSING** |
| **TREND_PULLBACK_EMA** | ❌ | ❌ | ❌ | ❌ | ❌ | **MISSING** |
| **POST_DISPLACEMENT_CONTINUATION** | ❌ | ❌ | ❌ | ❌ | ❌ | **MISSING** |
| **FAILED_AUCTION_RECLAIM** | ❌ | ❌ | ❌ | ❌ | ❌ | **MISSING** |
| **LIQUIDATION_REVERSAL** | ❌ | ❌ | ❌ | ❌ | ❌ | **MISSING** |
| **FUNDING_EXTREME_SIGNAL** | ❌ | ❌ | ❌ | ❌ | ❌ | **MISSING** |
| **DIVERGENCE_CONTINUATION** | ❌ | ❌ | ❌ | ❌ | ❌ | **MISSING** |
| **QUIET_COMPRESSION_BREAK** | ❌ | ❌ | ❌ | ❌ | ❌ | **MISSING** |
| **OPENING_RANGE_BREAKOUT** | ❌ | ❌ | ❌ | ❌ | ❌ | **MISSING** |

**9 of 16 active setup classes are completely absent from regime affinity lists.** These paths always receive 8/20 regime points instead of the 18/20 they would get if correctly listed. This is a **10-point systematic deficit** on every signal from these paths when the regime is known.

## Appendix C: Evidence Index

| Finding | File | Line(s) | Mechanism |
|---------|------|---------|-----------|
| Setup bonus limited to 3 classes | `src/signal_quality.py` | 1394–1399 | `score_signal_components()` |
| Family thesis adj covers 3 families | `src/signal_quality.py` | 1509–1537 | `_FAMILY_*` frozensets |
| Regime affinity missing 9 paths | `src/signal_quality.py` | 1492–1503 | `_REGIME_SETUP_AFFINITY` |
| Soft penalties applied post-scoring | `src/scanner/__init__.py` | 3147–3164 | Penalty deduction block |
| Penalty weights per channel | `src/scanner/__init__.py` | 407–416 | `_CHANNEL_PENALTY_WEIGHTS` |
| Regime penalty multiplier | `src/scanner/__init__.py` | 318–324 | `_REGIME_PENALTY_MULTIPLIER` |
| QUIET scalp penalty 1.8× | `src/scanner/__init__.py` | 306 | `_SCALP_QUIET_REGIME_PENALTY` |
| Tier classification thresholds | `src/scanner/__init__.py` | 444–463 | `classify_signal_tier()` |
| Layer 3 overwrites Layer 2 | `src/scanner/__init__.py` | 3109–3112 | `sig.confidence = _score_result["total"]` |
| WATCHLIST → free only | `src/signal_router.py` | 482–489 | `_process()` |
| Floor gates from Layer 2 components | `src/scanner/__init__.py` | 3374–3387 | `min_conf + component floors` |
| Channel min_confidence = 65 | `config/__init__.py` | 601 | `MIN_CONFIDENCE_SCALP` |
