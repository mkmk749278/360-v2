# 360 Crypto Eye — Signal Engine Pre-Redeploy Audit Report

**Date:** 2026-04-12
**Repository:** `mkmk749278/360-v2` / `main`
**Auditor:** Deep codebase analysis — all evaluator paths, scanner funnel, risk-plan, scoring engine, config, and owner brief reviewed

---

## 1. Executive Judgment

**Is the engine currently trustworthy enough for a fresh clean redeploy?**

**Verdict: Redeploy only after one more correction pass.**

The signal engine is architecturally serious and well above retail-grade. The multi-path evaluator portfolio, structural SL/TP protection system, family-aware scoring, and layered gate architecture are all business-grade foundations. However, several concrete issues would compromise signal quality if deployed as-is:

1. **Seven of eight specialist channels are disabled by default** — the live engine is effectively a single-channel system (360_SCALP only). This is acceptable for quality-over-quantity, but means the entire specialist layer (FVG, VWAP, Ichimoku, Supertrend, Orderblock, CVD, Divergence) is dead weight in production. Their code is maintained but untested in live conditions.

2. **Known soft-penalty preservation was fixed (PR-01)** but the fix depends on `getattr(sig, "soft_penalty_total", 0.0)` — if any evaluator path fails to set this attribute, the scanner-level penalty becomes the only penalty. This is a fragile accumulation pattern.

3. **RANGE_FADE is permanently removed from scalp.py** but dead-code references remain in scanner (lines 165-166, 1995-1998): a +5.0 confidence boost for RANGE_FADE in RANGING regime will never fire but pollutes the codebase.

4. **Three evaluator paths defer TP calculation entirely** (LIQUIDATION_REVERSAL, WHALE_MOMENTUM, and most specialist channels) — downstream build_risk_plan computes generic R-multiple TPs that may not match the evaluator thesis.

5. **Non-protected setups have their SL/TP overwritten twice** — once by build_risk_plan (recent-structure + ATR), again by predictive_ai (volatility scaling ±15%) — creating drift from evaluator intent.

6. **The PR09 scoring floor at 50** combined with post-scoring soft penalty deduction means a signal scoring 55 with 8 points of soft penalty fires at 47 and gets rejected — this creates a hidden interaction where soft penalties effectively raise the scoring floor above 50.

One correction pass addressing items 3-6 would make this engine deploy-trustworthy.

---

## 2. Full Active Path Inventory

### Live Active Paths (14 evaluators, all in 360_SCALP channel)

| # | Path Name | Setup Class | File Location | Portfolio Role | Default Status |
|---|-----------|------------|---------------|----------------|----------------|
| 1 | `_evaluate_standard` | LIQUIDITY_SWEEP_REVERSAL | `src/channels/scalp.py:360–602` | CORE | Active |
| 2 | `_evaluate_trend_pullback` | TREND_PULLBACK_EMA | `src/channels/scalp.py:609–764` | CORE | Active |
| 3 | `_evaluate_liquidation_reversal` | LIQUIDATION_REVERSAL | `src/channels/scalp.py:772–906` | SUPPORT | Active |
| 4 | `_evaluate_whale_momentum` | WHALE_MOMENTUM | `src/channels/scalp.py:913–1080` | SPECIALIST | Active |
| 5 | `_evaluate_volume_surge_breakout` | VOLUME_SURGE_BREAKOUT | `src/channels/scalp.py:1087–1296` | CORE | Active |
| 6 | `_evaluate_breakdown_short` | BREAKDOWN_SHORT | `src/channels/scalp.py:1303–1517` | CORE | Active |
| 7 | `_evaluate_opening_range_breakout` | OPENING_RANGE_BREAKOUT | `src/channels/scalp.py:1525–1669` | SUPPORT | **Disabled (flag)** |
| 8 | `_evaluate_sr_flip_retest` | SR_FLIP_RETEST | `src/channels/scalp.py:1676–1946` | CORE | Active |
| 9 | `_evaluate_funding_extreme` | FUNDING_EXTREME_SIGNAL | `src/channels/scalp.py:1953–2102` | SPECIALIST | Active |
| 10 | `_evaluate_quiet_compression_break` | QUIET_COMPRESSION_BREAK | `src/channels/scalp.py:2109–2254` | SPECIALIST | Active |
| 11 | `_evaluate_divergence_continuation` | DIVERGENCE_CONTINUATION | `src/channels/scalp.py:2261–2441` | SUPPORT | Active |
| 12 | `_evaluate_continuation_liquidity_sweep` | CONTINUATION_LIQUIDITY_SWEEP | `src/channels/scalp.py:2448–2698` | CORE | Active |
| 13 | `_evaluate_post_displacement_continuation` | POST_DISPLACEMENT_CONTINUATION | `src/channels/scalp.py:2705–3031` | CORE | Active |
| 14 | `_evaluate_failed_auction_reclaim` | FAILED_AUCTION_RECLAIM | `src/channels/scalp.py:3038–3331` | SUPPORT | Active |

### Disabled Specialist Channels (7 channels, all disabled by default)

| Channel | File | Setup Type | Default |
|---------|------|-----------|---------|
| 360_SCALP_FVG | `src/channels/scalp_fvg.py` | FVG_RETEST / FVG_RETEST_HTF_CONFLUENCE | Disabled |
| 360_SCALP_CVD | `src/channels/scalp_cvd.py` | CVD_DIVERGENCE | Disabled |
| 360_SCALP_DIVERGENCE | `src/channels/scalp_divergence.py` | RSI_MACD_DIVERGENCE | Disabled |
| 360_SCALP_VWAP | `src/channels/scalp_vwap.py` | VWAP_BOUNCE | Disabled |
| 360_SCALP_SUPERTREND | `src/channels/scalp_supertrend.py` | SUPERTREND_FLIP | Disabled |
| 360_SCALP_ICHIMOKU | `src/channels/scalp_ichimoku.py` | ICHIMOKU_TK_CROSS | Disabled |
| 360_SCALP_ORDERBLOCK | `src/channels/scalp_orderblock.py` | SMC_ORDERBLOCK | Disabled |

### Permanently Removed
- `_evaluate_range_fade` (RANGE_FADE) — BB mean reversion, no SMC basis, retail strategy

---

## 3. Path-by-Path Audit

### PATH 1: LIQUIDITY_SWEEP_REVERSAL (`_evaluate_standard`)

**Implementation:** `src/channels/scalp.py:360–602`

**Thesis:** M5 liquidity sweep — price sweeps recent highs/lows with momentum confirmation, then reverses. This is the foundational SMC scalp thesis.

**Regime fit:** Fires in all regimes. VOLATILE gets soft penalty. This is correct — sweeps happen in all conditions, but volatile sweeps are less reliable.

**SL review:** Swept level ± 0.1% buffer, minimum ATR × 0.5. **Strong** — SL is anchored to the exact structural level that was swept. This is thesis-aligned: if price revisits the swept level and holds, the sweep thesis is intact; if it breaks, the thesis is dead.

**TP review:** Nearest FVG midpoint / 20-candle swing / ATR ratios (1.5R, 2.5R, 4.0R). **Good** — structural targets (FVG, swing) take priority; ATR ratios are conservative fallback.

**Scanner/funnel review:** Subject to all gates (MTF, SMC, trend, cross-asset). Not exempted from any gate. This is correct — the standard path should pass all standard gates.

**Business-quality judgment:** **Strong.** This is the canonical institutional scalp thesis — sweep, confirm, reverse. Multi-layer confirmation (sweep + momentum + EMA + MACD + MTF + HTF EMA200 rejection). The gate chain is thorough without being excessive.

**Deploy verdict:** ✅ **Strong / trust for redeploy**

**Recommended action:** None required.

---

### PATH 2: TREND_PULLBACK_EMA (`_evaluate_trend_pullback`)

**Implementation:** `src/channels/scalp.py:609–764`

**Thesis:** EMA pullback in established trend — price pulls back to EMA9/EMA21 zone in TRENDING regime, bounces in trend direction. Classic institutional trend continuation.

**Regime fit:** TRENDING_UP (LONG) / TRENDING_DOWN (SHORT) only. **Correct** — pullback thesis requires established trend. Regime-locked by design.

**SL review:** Beyond EMA21, minimum ATR × 0.5. **Strong** — thesis-aligned: if price closes beyond EMA21, the pullback thesis is dead because the trend structure (EMA stacking) has broken. Structurally protected (PR-02).

**TP review:** 20-candle swing / 4h swing / ATR ratios (1.5R, 2.0R, 4.0R). Evaluator TPs structurally protected. **Good** — swing targets are appropriate for trend continuation.

**Scanner/funnel review:** Exempt from SMC hard gate (PR-05) and trend gate. **Correct** — pullback entries inherently have low sweep scores (no sweep event) and EMA alignment is the thesis itself, not an independent gate.

**Business-quality judgment:** **Strong.** Clean thesis, tight regime lock, structural SL, protected TPs. The RSI 40-60 pullback zone is a well-known institutional re-entry zone. +8 confidence boost is appropriate.

**Deploy verdict:** ✅ **Strong / trust for redeploy**

**Recommended action:** None required.

---

### PATH 3: LIQUIDATION_REVERSAL (`_evaluate_liquidation_reversal`)

**Implementation:** `src/channels/scalp.py:772–906`

**Thesis:** Cascade exhaustion (3-candle ≥2% move) + CVD divergence → reversal entry after panic selling/buying is exhausted.

**Regime fit:** No hard regime block. CVD divergence is the primary gate. **Acceptable** — cascades can happen in any regime, but the path is designed for VOLATILE conditions where it thrives.

**SL review:** Cascade extremum ± 0.3% buffer. **Good** — thesis-aligned: the cascade extreme is the exact invalidation point. If price makes a new extreme beyond the cascade, the exhaustion thesis is dead.

**TP review:** **Weak.** No evaluator-authored TP calculation — defaults to downstream build_risk_plan generic R-multiples (1.0R, 1.8R, 2.5R). The OWNER_BRIEF specifies Fibonacci retrace targets (38.2%, 61.8%, 100%) as the correct TP Type D for this path. **The evaluator does not implement this.** Downstream generic TPs do not match the thesis — a cascade reversal should target specific retrace levels of the cascade range, not arbitrary R-multiples.

**Scanner/funnel review:** Exempt from SMC hard gate, trend gate. **Correct** — cascade reversals are inherently counter-trend and occur without sweep structures.

**Business-quality judgment:** **Good but incomplete.** The entry logic (cascade + CVD + volume + RSI extreme) is strong. The SL is thesis-aligned. But the TP gap is a real business issue — generic R-multiples will either overshoot (cascade didn't retrace enough) or undershoot (missed the full retrace). The +10 confidence boost is the highest of any path, reflecting conviction in the thesis.

**Deploy verdict:** ⚠️ **Good but needs refinement**

**Recommended action:** Implement Fibonacci-retrace TP targets (38.2%, 61.8%, 100% of cascade range) as specified in OWNER_BRIEF. Add to STRUCTURAL_SLTP_PROTECTED_SETUPS after TP is implemented.

---

### PATH 4: WHALE_MOMENTUM (`_evaluate_whale_momentum`)

**Implementation:** `src/channels/scalp.py:913–1080`

**Thesis:** Large volume spike (whale alert or delta spike) + dominant tick flow + OBI confirmation → momentum entry in flow direction.

**Regime fit:** Fires in all regimes. OBI soft/hard gates adapt: fast regimes (VOLATILE, BREAKOUT_EXPANSION) accept marginal OBI (1.2×) with penalty; calm regimes require full 1.5× OBI. **Well-designed** — whale activity occurs anywhere but needs higher confirmation in calm conditions.

**SL review:** Recent swing low/high (5-bar lookback) ± 0.1% buffer, or ATR minimum. **Acceptable** — swing-based SL is reasonable but not strongly thesis-aligned. The OWNER_BRIEF specifies ATR-based SL (Type 4: entry ±1.0×ATR). The evaluator uses swing + ATR fallback, which is close but not identical. Not structurally protected.

**TP review:** **Weak.** TP1/TP2/TP3 all set to 0.0 (trailing-only setup). Downstream build_risk_plan assigns generic multiples (1.5R, 2.5R, 3.8R). **The evaluator deliberately defers TP** — this is a momentum-following path that relies on trailing stops. However, zero TP forces downstream to generate arbitrary targets that have no thesis basis.

**Scanner/funnel review:** Exempt from SMC hard gate and trend gate (PR-05). **Correct** — whale flows are order-flow events, not sweep structures or trend alignment signals.

**Business-quality judgment:** **Usable but questionable.** The entry logic is strong (tick flow dominance + OBI + RSI layered gates). The adaptive OBI regime handling is sophisticated. However: (1) zero-TP design creates downstream thesis drift; (2) OBI dependency on order book data creates fail-closed risk when book is unavailable (mitigated by +10 penalty); (3) the path fires in ANY regime, including QUIET where whale activity is rare and more likely to be noise.

**Deploy verdict:** ⚠️ **Usable but questionable**

**Recommended action:** Implement momentum-based TP targets (ATR multiples as specified in OWNER_BRIEF Type A: 1.5R, 2.5R, 4.0R) at the evaluator level instead of deferring. Consider adding QUIET regime block.

---

### PATH 5: VOLUME_SURGE_BREAKOUT (`_evaluate_volume_surge_breakout`)

**Implementation:** `src/channels/scalp.py:1087–1296`

**Thesis:** Price breaks swing high on surge volume, pulls back into premium zone (0.3–0.6%), re-enters. Classic breakout-pullback re-entry.

**Regime fit:** All except QUIET. **Correct** — breakouts require momentum that QUIET regimes lack.

**SL review:** 0.8% below swing high. **Acceptable** — percentage-based SL is simple but not deeply structural. The swept swing high would be a stronger anchor. However, the 0.8% provides consistent risk sizing. Structurally protected (PR-02).

**TP review:** Measured move from base of range (1×, 1.5×, 2.0×). **Strong** — measured-move TP is the correct methodology for breakout setups. Base-of-range calculation gives targets directly tied to the price structure. Protected (PR-02).

**Scanner/funnel review:** Exempt from SMC hard gate. FVG/OB soft gate in fast regimes (+8 penalty). **Correct** — volume surge breakouts are volume events, not sweep events; FVG/OB may lag in fast moves.

**Business-quality judgment:** **Strong.** Multi-confluence entry (volume surge + swing break + pullback zone + EMA + RSI). Measured-move TPs are the gold standard for breakout entries. Pullback zone grading (premium/extended) with soft penalties is sophisticated.

**Deploy verdict:** ✅ **Strong / trust for redeploy**

**Recommended action:** None required. Minor: could tighten the 0.75% max pullback zone for highly volatile pairs.

---

### PATH 6: BREAKDOWN_SHORT (`_evaluate_breakdown_short`)

**Implementation:** `src/channels/scalp.py:1303–1517`

**Thesis:** Mirror of VOLUME_SURGE_BREAKOUT for shorts — price breaks swing low on volume, dead-cat bounces into zone, re-enters short.

**Regime fit:** All except QUIET. Extended fast-bearish regimes include TRENDING_DOWN. **Correct** — symmetric to long-side breakout, with appropriate bearish regime additions.

**SL review:** 0.8% above swing low. Structurally protected. **Acceptable** — same assessment as VOLUME_SURGE_BREAKOUT.

**TP review:** Measured move downward (1×, 1.5×, 2.0×). Protected. **Strong** — identical measured-move methodology as the long counterpart.

**Scanner/funnel review:** Exempt from SMC hard gate. FVG/OB soft in VOLATILE/TRENDING_DOWN/BREAKOUT_EXPANSION/STRONG_TREND. **Correct.**

**Business-quality judgment:** **Strong.** Symmetric design to long-side breakout, which is architecturally clean. RSI range 20–68 is wider than the long side (40–82), which is appropriate for shorts (shorts trigger at lower RSI readings).

**Deploy verdict:** ✅ **Strong / trust for redeploy**

**Recommended action:** None required.

---

### PATH 7: OPENING_RANGE_BREAKOUT (`_evaluate_opening_range_breakout`)

**Implementation:** `src/channels/scalp.py:1525–1669`

**Thesis:** Session opening range breakout during London (07–08 UTC) or NY (12–13 UTC) session on volume + EMA alignment.

**Regime fit:** All except QUIET/RANGING. **Correct** — breakouts need directional momentum.

**SL review:** Range boundary ± 0.1%. **Acceptable** — range-anchored SL is thesis-aligned.

**TP review:** Range height multiples (1.0×, 1.5×, 2.0×). **Acceptable** — measured-move from range.

**Scanner/funnel review:** Exempt from SMC hard gate. **Correct.**

**Business-quality judgment:** **Effectively inactive — disabled by default.** The evaluator uses a proxy opening range (candles [-8:-4]) instead of true session-opening-range logic. The OWNER_BRIEF explicitly flags this for rebuild: "awaiting rebuild with true session-opening-range logic." The hour-based windows (07-08, 12-13) miss Asia session entirely. The proxy range is not the real opening range.

**Deploy verdict:** 🔴 **Effectively inactive / blocked / not contributing**

**Recommended action:** Leave disabled until rebuilt with proper session-opening-range detection. Low priority — other paths cover breakout thesis better.

---

### PATH 8: SR_FLIP_RETEST (`_evaluate_sr_flip_retest`)

**Implementation:** `src/channels/scalp.py:1676–1946`

**Thesis:** Prior support becomes resistance (or vice versa) — price flips a structural level and retests with rejection wick confirmation.

**Regime fit:** All except VOLATILE. **Correct** — SR flips need orderly price action to form and retest; volatile conditions invalidate the structure.

**SL review:** Flipped level ± 0.2%. Structurally protected. **Strong** — the flipped level is the exact thesis anchor. If price passes back through the level, the flip thesis is dead. 0.2% buffer is tight enough to capture the invalidation without being noise-triggered.

**TP review:** 20-candle swing / 4h target / ATR ratios (1.5R, 1.5R→SL buffer, 3.5R). Protected. **Strong** — structural targets (swing, 4h) are appropriate for S/R-based entries.

**Scanner/funnel review:** Exempt from SMC hard gate. FVG/OB soft in trending/expansion regimes. Layered soft penalties for proximity zone (+3), wick quality (+4), RSI (+5), missing FVG/OB (+8). **Well-designed** — the graduated penalty system (proximity zone grading, wick quality assessment) is sophisticated.

**Business-quality judgment:** **Strong.** SR flip is one of the most reliable institutional patterns. The evaluator's implementation is thorough: 50-candle history for structure, 8-candle flip window, graduated retest proximity, wick quality assessment (body ratio < 20% hard reject, 20-50% soft, ≥50% pass). The wick quality gate alone elevates this above retail-grade.

**Deploy verdict:** ✅ **Strong / trust for redeploy**

**Recommended action:** None required.

---

### PATH 9: FUNDING_EXTREME_SIGNAL (`_evaluate_funding_extreme`)

**Implementation:** `src/channels/scalp.py:1953–2102`

**Thesis:** Contrarian entry when funding rate hits extreme + price/RSI/CVD alignment. Funding extremes indicate crowded positioning, creating mean-reversion opportunity.

**Regime fit:** All except QUIET. **Correct** — funding extremes in quiet markets are usually noise (thin volume inflates rates).

**SL review:** Nearest liquidation cluster × 1.1 multiplier, or ATR × 1.5 fallback. **Strong** — liquidation cluster is the ideal SL for a funding-driven contrarian play. If price moves to the cluster, cascading liquidations will destroy the thesis. The 1.1× multiplier provides buffer against wick noise.

**TP review:** Nearest FVG/OB structure (1.0R min, fallback 1.5R) / ATR ratios (2.0R, 3.5R). **Acceptable** — structural TP1 is good, but downstream build_risk_plan overwrites with generic 1.0R/1.8R/2.5R. The evaluator sets initial TP but it's not structurally protected (not in STRUCTURAL_SLTP_PROTECTED_SETUPS).

**Scanner/funnel review:** Exempt from SMC hard gate and trend gate. **Correct** — funding extremes are order-flow events independent of sweep structures and trend alignment.

**Business-quality judgment:** **Good.** The thesis is sound — extreme funding rates historically precede mean-reversion. Multi-confluence entry (funding + RSI + CVD + EMA + FVG/OB) prevents false signals. Liquidation-cluster SL is the correct institutional approach. However, the path depends on funding rate data availability, and the extreme threshold (0.001 = 0.1%) may be too sensitive for some market conditions.

**Deploy verdict:** ✅ **Good but needs refinement**

**Recommended action:** Add to STRUCTURAL_SLTP_PROTECTED_SETUPS or _PREDICTIVE_SLTP_BYPASS_SETUPS to prevent downstream TP overwriting. Verify funding rate extreme threshold is appropriate for current market.

---

### PATH 10: QUIET_COMPRESSION_BREAK (`_evaluate_quiet_compression_break`)

**Implementation:** `src/channels/scalp.py:2109–2254`

**Thesis:** Bollinger Band squeeze breakout — price breaks out of tight bands after compression, with MACD zero-cross and volume confirmation.

**Regime fit:** QUIET and RANGING only. **Correct** — this path is specifically designed for low-volatility environments where compression precedes expansion. Regime-locked.

**SL review:** BB boundary ± 0.1%. **Strong** — BB lower/upper as SL anchor is thesis-aligned: if price returns inside the bands after breakout, the compression-break thesis has failed. Structurally protected.

**TP review:** Band-width multiples (0.5×, 1.0×, 1.5×) or ATR fallback. Protected. **Good** — band-width projection is the correct measured-move methodology for BB squeeze breakouts. Conservative (0.5× for TP1) — appropriate for quiet-regime scalps.

**Scanner/funnel review:** Exempt from quiet-regime confidence floor. Exempt from SMC hard gate. **Correct** — this is the path designed for quiet conditions; blocking it on quiet-regime gates would be architecturally contradictory.

**Business-quality judgment:** **Strong for its niche.** Narrow but precise — MACD zero-cross is a strong entry trigger for compression breakouts. Volume confirmation (2.0× average) filters false breakouts. Band compression threshold (1.5%) is tight enough to catch genuine squeezes. This is a specialist path that will fire rarely but with high conviction when it does.

**Deploy verdict:** ✅ **Strong / trust for redeploy**

**Recommended action:** None required.

---

### PATH 11: DIVERGENCE_CONTINUATION (`_evaluate_divergence_continuation`)

**Implementation:** `src/channels/scalp.py:2261–2441`

**Thesis:** Hidden CVD divergence in trending regime — price makes lower low but CVD makes higher low (LONG), indicating absorption/accumulation. Continuation entry in trend direction.

**Regime fit:** TRENDING_UP / TRENDING_DOWN only. **Correct** — hidden divergence is a continuation signal that requires established trend context.

**SL review:** EMA21 ± 0.5%. **Acceptable** — EMA-based SL is appropriate for trend continuation but the 0.5% buffer is wider than TREND_PULLBACK_EMA's EMA21 anchor. This is reasonable given the divergence thesis allows for deeper pullbacks.

**TP review:** **Weak.** No evaluator-authored TP calculation — defaults to downstream generic multiples (1.3R, 2.5R, 3.8R). The path stores divergence strength (0-1.0) in smc_data for downstream scoring but does not use it for TP calibration. **A divergence-based path should target the previous swing high/low that formed the divergence pattern.**

**Scanner/funnel review:** Exempt from quiet-regime block if confidence ≥ 64.0. Subject to standard gates. CVD divergence strength feeds into PR09 family thesis adjustment (+4 for aligned divergence, up to +2 magnitude bonus). **Good scoring integration.**

**Business-quality judgment:** **Good but incomplete.** The entry logic (hidden divergence + trend + EMA proximity + FVG/OB) is sound. CVD divergence strength propagation to scorer is sophisticated. But the TP gap means downstream generic targets may not capture the divergence pattern's natural resolution point. Not structurally protected.

**Deploy verdict:** ⚠️ **Good but needs refinement**

**Recommended action:** Implement divergence-pattern-based TP targets (swing high/low from the divergence window). Add to STRUCTURAL_SLTP_PROTECTED_SETUPS.

---

### PATH 12: CONTINUATION_LIQUIDITY_SWEEP (`_evaluate_continuation_liquidity_sweep`)

**Implementation:** `src/channels/scalp.py:2448–2698`

**Thesis:** Sweep of local liquidity in trend direction → price reclaims swept level → continuation entry. Combines sweep mechanics with trend context.

**Regime fit:** TRENDING_UP, TRENDING_DOWN, STRONG_TREND, WEAK_TREND, BREAKOUT_EXPANSION. **Correct** — continuation thesis requires directional context. VOLATILE/RANGING/QUIET correctly blocked.

**SL review:** Swept level − ATR buffer (LONG) or + ATR buffer (SHORT). Structurally protected. **Strong** — swept level is the exact thesis anchor. If price returns below the swept level, the sweep-reclaim-continuation thesis is dead. ATR buffer accounts for re-test noise.

**TP review:** Nearest FVG midpoint / 20-candle swing / ATR ratios (1.5R, 2.5R, 4.0R). Protected. **Strong** — structural targets (FVG, swing) are appropriate for continuation entries. The graduated target approach (FVG first, swing second, ATR third) reflects decreasing structural conviction.

**Scanner/funnel review:** Subject to standard gates. Soft penalties for RSI (+6), missing FVG/OB (+8), older sweep age (+5). **Well-designed** — sweep recency penalty (≥6 candles +5) correctly penalizes stale setups without hard-blocking them.

**Business-quality judgment:** **Strong.** This path combines two of the engine's strongest concepts (liquidity sweep + trend continuation). The reclaim confirmation gate (price must already be beyond swept level) is the key differentiator — it prevents entering during the sweep itself, waiting for reclaim confirmation. This is an institutional-grade entry technique.

**Deploy verdict:** ✅ **Strong / trust for redeploy**

**Recommended action:** None required.

---

### PATH 13: POST_DISPLACEMENT_CONTINUATION (`_evaluate_post_displacement_continuation`)

**Implementation:** `src/channels/scalp.py:2705–3031`

**Thesis:** Institutional displacement (high-volume strong-body candle) → tight consolidation (2-5 candles within displacement territory) → breakout of consolidation in displacement direction. Captures institutional re-accumulation pattern.

**Regime fit:** TRENDING_UP, TRENDING_DOWN, STRONG_TREND, WEAK_TREND, BREAKOUT_EXPANSION. **Correct** — displacement requires directional context.

**SL review:** Consolidation range boundary − ATR buffer. Structurally protected. **Strong** — if price breaks back through the consolidation range, the re-accumulation thesis is dead. This is the optimal invalidation point for this pattern.

**TP review:** Displacement height multiples (1.0×, 1.5×, 2.5×). Protected. **Strong** — displacement-height-based measured move is the textbook TP methodology for this pattern. The targets are calibrated to the specific displacement that triggered the setup, not generic R-multiples.

**Scanner/funnel review:** Subject to standard gates. Soft penalties for RSI (+6), missing FVG/OB (+7), noisy consolidation volume (+5). **Well-designed** — consolidation volume quality check (avg ≥1.5× displacement vol → penalty) correctly identifies distribution disguised as consolidation.

**Business-quality judgment:** **Strong.** This is one of the engine's best-designed paths. The three-phase detection (displacement → consolidation → breakout) with specific criteria for each phase (60% body ratio, 2.5× volume for displacement; 50% range limit, territory containment for consolidation) is genuinely institutional-grade. The consolidation territory check (price must stay within displacement territory) is the key quality gate.

**Deploy verdict:** ✅ **Strong / trust for redeploy**

**Recommended action:** None required.

---

### PATH 14: FAILED_AUCTION_RECLAIM (`_evaluate_failed_auction_reclaim`)

**Implementation:** `src/channels/scalp.py:3038–3331`

**Thesis:** Failed breakout/breakdown — price breaks structural level, fails to hold (acceptance fails), reclaims the level. Entry on the reclaim. Captures trapped traders on the wrong side of a failed break.

**Regime fit:** All except VOLATILE, VOLATILE_UNSUITABLE, STRONG_TREND. **Correct** — failed auctions occur in orderly conditions (RANGING, WEAK_TREND) where false breakouts are common. VOLATILE/STRONG_TREND would make the "failure" more likely a real move.

**SL review:** Auction wick extreme − ATR buffer. **Strong** — the auction wick extreme is the exact point where the failed breakout reached. If price exceeds this, the breakout wasn't actually failed. Dual-protected (special block in build_risk_plan + _PREDICTIVE_SLTP_BYPASS_SETUPS).

**TP review:** Auction tail multiples (1.0×, 1.5×, 2.5×) or reclaim-span measured move fallback. Dual-protected. **Strong** — tail-based TP is calibrated to the rejection strength. Larger tail = stronger rejection = larger target. The reclaim-span fallback preserves target coherence when evaluator TPs are invalid.

**Scanner/funnel review:** Subject to standard gates. Soft penalties for RSI (+6), missing FVG/OB (+5). Conservative RSI thresholds (65/35 soft, 75/25 hard). **Correct** — tighter RSI gates for a reclaim path make sense because extreme RSI readings suggest momentum, not failed auction.

**Business-quality judgment:** **Strong.** This is the engine's most carefully protected path (dual SL/TP protection, special build_risk_plan block, predictive AI bypass). The auction detection logic (structural level + break + close back within level - 0.2% acceptance threshold) is precise. The reclaim confirmation (≥ ATR × 0.1 from level) prevents premature entries. The auction window (1-7 bars) is appropriately narrow for scalp timeframes.

**Deploy verdict:** ✅ **Strong / trust for redeploy**

**Recommended action:** None required.

---

### DISABLED SPECIALIST CHANNELS (Brief Assessment)

**FVG_RETEST (scalp_fvg.py):** Age decay + fill decay SL scaling is sophisticated. However, 50% zone-width proximity threshold is too wide (includes non-retests). No regime gate. SL decay can create sub-0.5% stops. **Verdict: Not ready. Needs regime gating and proximity tightening.**

**CVD_DIVERGENCE (scalp_cvd.py):** Hard-gate-only architecture (no soft penalties) is rigid. CVD metadata dependency creates fail-closed risk. No regime gate. **Verdict: Not ready. Needs soft penalty layer and regime awareness.**

**RSI_MACD_DIVERGENCE (scalp_divergence.py):** Distinguishes regular vs hidden divergence. ADX ≤40 gate is appropriate. Local extrema window (3-candle) may miss broader swings. No TP structure. **Verdict: Acceptable but weak TP. Needs TP implementation.**

**VWAP_BOUNCE (scalp_vwap.py):** VWAP TP1 (institutional mean-reversion target) is strong. 2SD SL is clear. But relies on ADX proxy for regime detection (not true regime). ±2SD SL may be too wide for tight R:R. **Verdict: Closest to ready among disabled channels.**

**SUPERTREND_FLIP (scalp_supertrend.py):** MTF confirmation (2 timeframes required) is strict but good. Supertrend line as SL is clean. However, Supertrend is a lagging indicator on fast moves. **Verdict: Acceptable as support, not standalone.**

**ICHIMOKU_TK_CROSS (scalp_ichimoku.py):** Kijun-sen SL is Ichimoku-standard. Cloud filter ensures direction. But 80-candle minimum excludes many opportunities, and the ATR-multiple TPs don't leverage Ichimoku targets (Kumo, Chikou). **Verdict: Incomplete — should use native Ichimoku targets.**

**SMC_ORDERBLOCK (scalp_orderblock.py):** Freshness gate (stale OBs rejected) is good. Impulse detection is strong. But 50-candle fixed lookback and no regime gate limit quality. **Verdict: Needs regime gate and dynamic lookback.**

---

## 4. Cross-Path Findings

### Strongest Paths (Business-Grade, Trust Immediately)
1. **POST_DISPLACEMENT_CONTINUATION** — best-designed three-phase detection; institutional re-accumulation pattern
2. **FAILED_AUCTION_RECLAIM** — most carefully protected; dual SL/TP preservation; precise auction detection
3. **CONTINUATION_LIQUIDITY_SWEEP** — combines sweep + trend; reclaim confirmation gate is excellent
4. **SR_FLIP_RETEST** — graduated wick quality assessment; tight structural SL; institutional pattern
5. **TREND_PULLBACK_EMA** — clean regime-lock; EMA-stacking + RSI pullback zone; low-noise design
6. **VOLUME_SURGE_BREAKOUT / BREAKDOWN_SHORT** — measured-move TPs; pullback zone grading; symmetric design

### Weakest Paths (Need Attention)
1. **OPENING_RANGE_BREAKOUT** — disabled, proxy range, needs full rebuild
2. **WHALE_MOMENTUM** — zero TP at evaluator level; fires in all regimes including QUIET; OBI dependency
3. **LIQUIDATION_REVERSAL** — no evaluator TP; OWNER_BRIEF specifies Fibonacci retrace but evaluator doesn't implement

### Best SL Design
1. **FAILED_AUCTION_RECLAIM** — auction wick extreme (exact rejection point) + dual protection
2. **SR_FLIP_RETEST** — flipped structural level (exact thesis anchor)
3. **POST_DISPLACEMENT_CONTINUATION** — consolidation boundary (exact pattern invalidation)
4. **CONTINUATION_LIQUIDITY_SWEEP** — swept level (exact structural anchor)
5. **FUNDING_EXTREME_SIGNAL** — liquidation cluster (institutional invalidation point)

### Weakest SL Design
1. **WHALE_MOMENTUM** — swing-based SL is generic; not thesis-anchored to the whale flow event
2. **VOLUME_SURGE_BREAKOUT / BREAKDOWN_SHORT** — 0.8% percentage SL is simple but not structural (should be swing-anchored)

### Best TP Design
1. **POST_DISPLACEMENT_CONTINUATION** — displacement-height measured move (calibrated to pattern)
2. **FAILED_AUCTION_RECLAIM** — auction-tail measured move (calibrated to rejection strength)
3. **VOLUME_SURGE_BREAKOUT / BREAKDOWN_SHORT** — range-based measured move
4. **QUIET_COMPRESSION_BREAK** — band-width projection

### Weakest TP Design
1. **WHALE_MOMENTUM** — zero evaluator TP; relies entirely on downstream generic R-multiples
2. **LIQUIDATION_REVERSAL** — no evaluator TP; OWNER_BRIEF specifies Fibonacci retrace, not implemented
3. **DIVERGENCE_CONTINUATION** — no evaluator TP; divergence pattern should have pattern-based targets
4. **All disabled specialist channels** — ATR-multiple fallback TPs are generic, not thesis-calibrated

### Paths Likely Overblocked
- None identified. Gate exemptions are appropriately applied. The engine errs slightly toward over-filtering (13-layer gate chain) but this is aligned with the quality-over-quantity philosophy.

### Paths Likely Too Noisy
- **WHALE_MOMENTUM** in QUIET regime — whale flows in quiet conditions are rare and more likely to be noise than real institutional activity
- **LIQUIDITY_SWEEP_REVERSAL** in all regimes — no regime restriction means it fires everywhere, including conditions where sweeps are noise (though the multi-layer confirmation mitigates this)

### Duplicated / Overlapping Paths
- **VOLUME_SURGE_BREAKOUT + BREAKDOWN_SHORT** are symmetric designs (long/short). This is intentional and correct — they don't compete because they fire in opposite directions.
- **CONTINUATION_LIQUIDITY_SWEEP overlaps with LIQUIDITY_SWEEP_REVERSAL** in trending regimes. CLS is continuation (same direction as sweep), standard is reversal (opposite direction). Correctly differentiated by thesis.
- **DIVERGENCE_CONTINUATION partially overlaps with scalp_divergence.py (RSI_MACD_DIVERGENCE)** — both detect divergence but on different indicators (CVD vs RSI/MACD) and in different channels. The specialist channel is disabled, so no live overlap.

### Scoring Inconsistencies
1. **PR09 scoring floor (50) + post-scoring soft penalty deduction** creates hidden interaction: signals scoring 55 with >5 points of soft penalty get rejected after penalty application, but the 50-floor check happened before penalty. The penalty deduction at line 2716-2722 happens AFTER the 50-floor gate at line 2694-2703. **This means soft penalties can push signals below the tier threshold without triggering rejection.** A signal at 52 with 8 points penalty becomes 44 — it passed the floor but fires at WATCHLIST-minus quality.
2. **RANGE_FADE confidence boost** (+5.0 for RANGING regime) is dead code — evaluator removed, boost unreachable. Harmless but cluttering.

### Portfolio-Role Inconsistencies
- **FUNDING_EXTREME_SIGNAL** is classified as SPECIALIST but its TP is not protected (not in STRUCTURAL_SLTP_PROTECTED_SETUPS or _PREDICTIVE_SLTP_BYPASS_SETUPS for TP). Its liquidation-cluster SL is strong but downstream TP scaling can distort the thesis.
- **DIVERGENCE_CONTINUATION** is classified as SUPPORT but has no evaluator TP — it should either implement TP or be downgraded to SPECIALIST pending completion.

### Architecturally Unfinished
1. **Three evaluator paths lack thesis-specific TP** (LIQUIDATION_REVERSAL, WHALE_MOMENTUM, DIVERGENCE_CONTINUATION) — violates B13 ("Every signal method has its own SL/TP calculation")
2. **All seven specialist channels disabled** — the portfolio is effectively single-channel; diversity exists in code but not in production
3. **RANGE_FADE dead code** in scanner (boost logic for removed evaluator)
4. **`valid_for_minutes` overwrite** — scanner `_populate_signal_context()` overwrites evaluator-set valid_for_minutes with per-channel defaults, removing any path-specific validity windows

---

## 5. Pre-Redeploy Action List

### 🔴 Must Be Corrected Before Fresh VPS Reinstall/Deploy

1. **Implement LIQUIDATION_REVERSAL evaluator TP** — Add Fibonacci retrace targets (38.2%, 61.8%, 100% of cascade range) as specified in OWNER_BRIEF Type D. Add to STRUCTURAL_SLTP_PROTECTED_SETUPS. This path is SUPPORT role and fires actively; generic TPs violate B13.

2. **Implement WHALE_MOMENTUM evaluator TP** — Add ATR-based targets (1.5R, 2.5R, 4.0R) at evaluator level as specified in OWNER_BRIEF Type A, instead of deferring to downstream. Currently zero-TP forces entirely generic downstream targets.

3. **Remove RANGE_FADE dead code** — Delete scanner lines 165-166 (confidence boost constant) and 1995-1998 (boost application). This is dead code for a permanently removed evaluator. Trivial cleanup but prevents confusion.

### 🟡 Should Ideally Be Refined Before Redeploy

4. **Implement DIVERGENCE_CONTINUATION evaluator TP** — Add divergence-pattern-based targets (previous swing that formed the divergence). Add to STRUCTURAL_SLTP_PROTECTED_SETUPS. Currently uses generic downstream R-multiples.

5. **Add FUNDING_EXTREME_SIGNAL to _PREDICTIVE_SLTP_BYPASS_SETUPS** — Its liquidation-cluster SL and structural TP1 should be protected from predictive AI scaling. Currently unprotected.

6. **Fix soft-penalty-after-scoring interaction** — The soft penalty deduction happens after the PR09 50-floor gate, meaning signals can pass the floor but fire at sub-50 quality. Either: (a) re-check floor after penalty, or (b) apply penalty before scoring, or (c) integrate penalty into scoring engine directly.

7. **Add QUIET regime block to WHALE_MOMENTUM** — Whale flows in quiet markets are rare and unreliable. The path should block or penalize QUIET regime more aggressively.

### 🟢 Can Wait Until After Fresh Deployment

8. **Implement VWAP_BOUNCE channel regime gate** — Replace ADX proxy with true regime input from scanner. Lowest-friction specialist channel to enable post-deploy.

9. **Implement Ichimoku native TP targets** — Replace ATR-multiple TPs with Kumo/Chikou targets. Required before enabling channel.

10. **Fix `valid_for_minutes` overwrite** — Evaluator-set validity windows should be preserved through scanner like soft_penalty_total is (PR-01 pattern).

11. **Review specialist channel readiness** — FVG, Orderblock, Supertrend, CVD, Divergence channels all need regime gates, soft penalty layers, and TP improvements before production enablement.

### ✅ Paths Safe to Trust Immediately After Clean Deploy

| Path | Confidence |
|------|------------|
| POST_DISPLACEMENT_CONTINUATION | ✅ Full trust |
| FAILED_AUCTION_RECLAIM | ✅ Full trust |
| CONTINUATION_LIQUIDITY_SWEEP | ✅ Full trust |
| SR_FLIP_RETEST | ✅ Full trust |
| TREND_PULLBACK_EMA | ✅ Full trust |
| VOLUME_SURGE_BREAKOUT | ✅ Full trust |
| BREAKDOWN_SHORT | ✅ Full trust |
| LIQUIDITY_SWEEP_REVERSAL (standard) | ✅ Full trust |
| QUIET_COMPRESSION_BREAK | ✅ Full trust |
| FUNDING_EXTREME_SIGNAL | ✅ Trust (minor TP protection gap) |
| DIVERGENCE_CONTINUATION | ⚠️ Trust with awareness (generic TP) |
| LIQUIDATION_REVERSAL | ⚠️ Trust with awareness (generic TP) |
| WHALE_MOMENTUM | ⚠️ Conditional trust (zero evaluator TP, no QUIET block) |
| OPENING_RANGE_BREAKOUT | 🔴 Disabled — leave disabled |

---

## 6. Final Deploy Recommendation

### **Redeploy only after one more correction pass**

**Justification:**

The engine is architecturally strong. The 14-path evaluator portfolio, structural SL/TP protection system (PR-02), self-classifying identity preservation (PR-01), family-aware thesis scoring (PR-09), quality-ranked arbitration (PR-03), and 13-layer gate chain are all business-grade foundations built to institutional standards.

**9 of 14 active paths are deploy-ready now.** The core portfolio (LIQUIDITY_SWEEP_REVERSAL, TREND_PULLBACK_EMA, VOLUME_SURGE_BREAKOUT, BREAKDOWN_SHORT, SR_FLIP_RETEST, CONTINUATION_LIQUIDITY_SWEEP, POST_DISPLACEMENT_CONTINUATION) plus QUIET_COMPRESSION_BREAK and FAILED_AUCTION_RECLAIM are genuinely strong and trustworthy.

**However, 3 active paths violate Business Rule B13** ("Every signal method has its own SL/TP calculation") — LIQUIDATION_REVERSAL, WHALE_MOMENTUM, and DIVERGENCE_CONTINUATION all defer TP to downstream generic logic. The OWNER_BRIEF itself specifies the correct TP methodology for each (Fibonacci retrace, ATR-fixed, swing-pattern-based) but these are not implemented in the evaluators.

**The correction pass is bounded and small:**
- 3 evaluator TP implementations (items 1-2, 4)
- 1 dead-code cleanup (item 3)
- 2 protection-set additions (items 5, 7)
- 1 scoring interaction fix (item 6)

This is approximately 1-2 focused PR passes. After these corrections, the engine would be fully B13-compliant with all active paths having thesis-specific SL and TP at the evaluator level, and the scoring interaction would be clean.

**The alternative — deploying now and fixing later — is not recommended** because generic TPs on 3 active paths will produce signals where the TP targets have no relationship to the entry thesis. This directly undermines subscriber trust (B8: SL hits posted honestly) because TP exits that don't match the setup pattern look arbitrary to informed subscribers.

**Bottom line:** The architecture is sound. The strongest paths are genuinely institutional-grade. One focused correction pass (3-5 days of engineering work) transforms this from "strong with known gaps" to "fully ready for production trust."

---

## Appendix A: Key Configuration Thresholds (as-deployed)

| Parameter | Value | Notes |
|-----------|-------|-------|
| SMC_HARD_GATE_MIN | 12.0 | Minimum structural basis |
| TREND_HARD_GATE_MIN | 10.0 | Minimum indicator sub-score for scalp |
| MTF_HARD_BLOCK | false | Soft -5.0 penalty instead |
| QUIET_SCALP_MIN_CONFIDENCE | 65.0 | Hard floor in QUIET regime |
| MIN_CONFIDENCE_SCALP | 80 | Main scalp channel minimum |
| MAX_CORRELATED_SCALP_SIGNALS | 4 | Same-direction exposure cap |
| GLOBAL_SYMBOL_COOLDOWN_SECONDS | 900 | 15 min per-symbol lockout |
| SIGNAL_SCAN_COOLDOWN (360_SCALP) | 600 | 10 min per-(symbol, channel) |
| SURGE_VOLUME_MULTIPLIER | 3.0 | Volume vs 7-candle average |
| FUNDING_RATE_EXTREME_THRESHOLD | 0.001 | Absolute funding rate for extreme signal |
| FUNDING_RATE_BOOST | +5.0 | Confidence boost for extreme opposite |
| FUNDING_RATE_PENALTY | -8.0 | Confidence penalty for crowded direction |
| CIRCUIT_BREAKER_MAX_CONSECUTIVE_SL | 3 | Consecutive SL before trip |
| CIRCUIT_BREAKER_COOLDOWN_SECONDS | 1800 | 30 min cooldown after trip |

## Appendix B: Structural Protection Sets

### STRUCTURAL_SLTP_PROTECTED_SETUPS (build_risk_plan)
- POST_DISPLACEMENT_CONTINUATION
- VOLUME_SURGE_BREAKOUT
- BREAKDOWN_SHORT
- QUIET_COMPRESSION_BREAK
- TREND_PULLBACK_EMA
- CONTINUATION_LIQUIDITY_SWEEP
- SR_FLIP_RETEST

### _PREDICTIVE_SLTP_BYPASS_SETUPS (predictive_ai)
- POST_DISPLACEMENT_CONTINUATION
- VOLUME_SURGE_BREAKOUT
- BREAKDOWN_SHORT
- QUIET_COMPRESSION_BREAK
- TREND_PULLBACK_EMA
- CONTINUATION_LIQUIDITY_SWEEP
- SR_FLIP_RETEST
- FAILED_AUCTION_RECLAIM

### _SMC_GATE_EXEMPT_SETUPS
- OPENING_RANGE_BREAKOUT
- QUIET_COMPRESSION_BREAK
- VOLUME_SURGE_BREAKOUT
- BREAKDOWN_SHORT
- SR_FLIP_RETEST
- LIQUIDATION_REVERSAL
- FUNDING_EXTREME_SIGNAL
- DIVERGENCE_CONTINUATION
- POST_DISPLACEMENT_CONTINUATION
- FAILED_AUCTION_RECLAIM
- TREND_PULLBACK_EMA
- WHALE_MOMENTUM

### _TREND_GATE_EXEMPT_SETUPS
- LIQUIDATION_REVERSAL
- FUNDING_EXTREME_SIGNAL
- WHALE_MOMENTUM
- FAILED_AUCTION_RECLAIM

## Appendix C: Portfolio Role Mapping

| Role | Paths | Count |
|------|-------|-------|
| CORE | LIQUIDITY_SWEEP_REVERSAL, TREND_PULLBACK_EMA, VOLUME_SURGE_BREAKOUT, BREAKDOWN_SHORT, SR_FLIP_RETEST, CONTINUATION_LIQUIDITY_SWEEP, POST_DISPLACEMENT_CONTINUATION | 7 |
| SUPPORT | LIQUIDATION_REVERSAL, DIVERGENCE_CONTINUATION, OPENING_RANGE_BREAKOUT, FAILED_AUCTION_RECLAIM | 4 |
| SPECIALIST | WHALE_MOMENTUM, FUNDING_EXTREME_SIGNAL, QUIET_COMPRESSION_BREAK | 3 |

## Appendix D: SL/TP Type Classification (per OWNER_BRIEF)

### SL Types
| Type | Evaluators | Logic |
|------|-----------|-------|
| Type 1 — Structure | SWEEP_REVERSAL, SURGE, BREAKDOWN, ORB, SR_FLIP, QUIET_BREAK | SL just beyond structural level |
| Type 2 — EMA | TREND_PULLBACK, DIVERGENCE_CONTINUATION | SL beyond EMA21 × 1.1 |
| Type 3 — Cascade Extreme | LIQUIDATION_REVERSAL | SL beyond cascade extreme + 0.3% |
| Type 4 — ATR | WHALE_MOMENTUM | SL = entry ± 1.0 × ATR |
| Type 5 — Liquidation Distance | FUNDING_EXTREME_SIGNAL | SL beyond nearest liquidation cluster × 1.1 |

### TP Types
| Type | Evaluators | Logic |
|------|-----------|-------|
| Type A — Fixed Ratio | WHALE_MOMENTUM | 1.5R, 2.5R, 4.0R |
| Type B — Structural | SWEEP_REVERSAL, TREND_PULLBACK, SR_FLIP, DIVERGENCE_CONTINUATION | FVG → swing → HTF |
| Type C — Measured Move | SURGE, BREAKDOWN, ORB, QUIET_BREAK | Range/band height projection |
| Type D — Reversion | LIQUIDATION_REVERSAL | 38.2%, 61.8%, 100% Fibonacci retrace |
| Type E — Normalization | FUNDING_EXTREME_SIGNAL | Funding normalization proxy → ratio fallback |
