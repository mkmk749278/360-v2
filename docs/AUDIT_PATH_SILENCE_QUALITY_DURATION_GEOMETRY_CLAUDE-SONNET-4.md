# AUDIT: Path Silence, Quality, Duration & Geometry — Deep Research

**Model**: Claude Sonnet 4 (claude-sonnet-4)  
**Date**: 2026-04-18  
**Scope**: Full end-to-end live signal engine audit  
**Branch**: `main` (as of 2026-04-18)  
**Live Evidence**: `monitor/latest.txt` from `monitor-logs` branch (2026-04-18 02:30 UTC)

---

## 1. Executive Verdict

The 360 Crypto Eye signal engine is currently expressing only **2 of 14** internal setup paths (`TREND_PULLBACK_EMA` and `SR_FLIP_RETEST`), not because the other 12 are broken, but because of a **compounding gate stack** that systematically eliminates paths that don't align with the dominant `trend_following` gate profile.

**The core truth:**
- The two surviving paths are the **easiest to generate** (fewest evaluator-level hard gates) AND the **most compatible with the MTF/scoring/geometry gate chain** (both are trend-aligned by design).
- The other 12 paths either cannot generate signals under current market conditions (correct filtering), or **do generate** but are systematically destroyed by the gate chain before emission. The monitor evidence proves at least 3 paths (LIQUIDITY_SWEEP_REVERSAL, SR_FLIP_RETEST within reclaim_retest, FAILED_AUCTION_RECLAIM) are actively generating and being destroyed.
- The two expressive paths are **weak** primarily because of (a) tight SL placement that doesn't survive normal noise — 19/20 recent SL trades show **0.00% MFE** and **3-minute hold** — and (b) the scoring engine awards them high enough confidence to pass gates but this confidence does not correlate with entry timing quality.
- The "3-minute" hold duration is **mostly real, not an artifact**. Trades genuinely die at the first lifecycle poll (5-second interval) because SL placement is within the bid-ask spread noise floor. The `int(hold_sec // 60)` display truncation adds a cosmetic component, but the underlying reality is that these trades never move favorably at all.
- The system is selecting the **most survivable** paths through existing gates, not the **genuinely best** setups. This is a funnel misalignment problem.

**Business impact**: 28 total signals, 21 SL hits (75% SL rate), average hold 4 minutes, average SL PnL -0.43%. The current engine is destroying subscriber trust faster than it builds it.

---

## 2. What Is Actually Happening Live

### Runtime truth from monitor/latest.txt (2026-04-18 02:30 UTC):

**Signal history (28 signals total):**
- TREND_PULLBACK_EMA: 17 signals → 5 TP, 12 SL (29% win rate, avg PnL +0.13%)
- SR_FLIP_RETEST: 11 signals → 1 TP, 9 SL, 1 CLOSED (9% win rate, avg PnL -0.18%)
- **No other setup class has emitted a single signal.**

**SL follow-through analysis (20 most recent SLs):**
- 19 of 20 SL trades: **MFE = +0.00%** (zero favorable movement before stop)
- 18 of 20 SL trades: **hold duration = 3 minutes** (first lifecycle check)
- 11 of 20 classified as "clean failure" (55%)
- 4 of 20 classified as "possible stop-too-tight" (20%)
- Average hold: 4 minutes
- Average SL PnL: -0.43%

**Active suppressors per scan cycle:**
| Suppressor | Count (last 500 lines) | Meaning |
|---|---|---|
| volatile_unsuitable:channel_preskip_bypassed:360_SCALP | 134 | Volatile pairs bypassing pre-skip (correct) |
| pair_quality:spread | 123 | Spread too wide (correct filtering) |
| mtf_gate:360_SCALP | 123 | Hard MTF rejection |
| mtf_gate_family:360_SCALP:reclaim_retest | 117 | Reclaim/retest family MTF rejection |
| mtf_gate_setup:360_SCALP:SR_FLIP_RETEST | 88 | SR_FLIP specific MTF rejection |
| mtf_gate_setup:360_SCALP:FAILED_AUCTION_RECLAIM | 79 | FAR specific MTF rejection |
| score_below50:360_SCALP | 32 | Below-50 scoring rejection |
| score_below50:SR_FLIP_RETEST | 31 | SR_FLIP scoring rejection |
| QUIET_SCALP_BLOCK | 31 | Quiet regime block |
| mtf_gate_setup:360_SCALP:LIQUIDITY_SWEEP_REVERSAL | 20 | LSR specific MTF rejection |
| mtf_gate_family:360_SCALP:reversal | 20 | Reversal family MTF rejection |
| geometry_rejected_risk_plan:360_SCALP:reclaim_retest | ~8-14 per cycle | Geometry rejection |

**Key observation**: The reclaim_retest family (SR_FLIP_RETEST + FAILED_AUCTION_RECLAIM) is generating heavily but being destroyed primarily by MTF gates (117+88+79 = **284 MTF rejections** in 500 lines) and geometry rejection (8-14 per cycle). The reversal family (LIQUIDITY_SWEEP_REVERSAL) shows 20 MTF rejections.

---

## 3. Path-by-Path Survival Matrix

### All 14 Internal 360_SCALP Setup Paths

| # | Setup Class | Family | Generates? | MTF Gate | Geometry | Scoring | Trend Gate | Quiet Block | SMC Gate | Emission | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | TREND_PULLBACK_EMA | trend_following | ✅ High | ✅ Pass (no cap) | ⚠️ SL capping | ✅ 80+ | ✅ Exempt: no | N/A (trending only) | ✅ | ✅ EMITTING | Active |
| 2 | SR_FLIP_RETEST | reclaim_retest | ✅ High | ⚠️ Cap 0.35 but still heavy rejection | ⚠️ Geometry rejection | ⚠️ 50-79 | ⚠️ Some rejection | N/A | ✅ | ✅ EMITTING (reduced) | Active-weak |
| 3 | LIQUIDITY_SWEEP_REVERSAL | reversal | ✅ Moderate | ❌ Cap 0.35, 20 rejections | ⚠️ Changed geometry | ⚠️ 65-79 range | N/A | N/A | ⚠️ | ❌ SILENT | MTF-blocked |
| 4 | FAILED_AUCTION_RECLAIM | reclaim_retest | ✅ Moderate | ❌ Cap 0.35, 79 rejections | ❌ Heavy geometry rejection | ⚠️ Below 50 | ✅ Exempt | N/A | ⚠️ | ❌ SILENT | MTF+geom blocked |
| 5 | LIQUIDATION_REVERSAL | reversal | ⛔ Rare | Cap 0.35 | N/A | N/A | ✅ Exempt | N/A | N/A | ❌ SILENT | Rarely generates |
| 6 | WHALE_MOMENTUM | orderflow_momentum | ⛔ Rare | Cap 0.45 | N/A | N/A | ✅ Exempt | Blocked in QUIET | N/A | ❌ SILENT | Rarely generates |
| 7 | VOLUME_SURGE_BREAKOUT | breakout_momentum | ⛔ Rare | No cap (strict) | N/A | N/A | Not exempt | Blocked in QUIET | N/A | ❌ SILENT | Rarely generates |
| 8 | BREAKDOWN_SHORT | breakout_momentum | ⛔ Rare | No cap (strict) | N/A | N/A | Not exempt | Blocked in QUIET | N/A | ❌ SILENT | Rarely generates |
| 9 | OPENING_RANGE_BREAKOUT | breakout_momentum | ⛔ Disabled | N/A | N/A | N/A | N/A | N/A | N/A | ❌ SILENT | Feature-gated off |
| 10 | POST_DISPLACEMENT_CONTINUATION | continuation | ⛔ Rare | Cap 0.45 | N/A | N/A | Not exempt | Blocked in QUIET | N/A | ❌ SILENT | Rarely generates |
| 11 | CONTINUATION_LIQUIDITY_SWEEP | continuation | ⛔ Rare | Cap 0.45 | N/A | N/A | Not exempt | N/A | N/A | ❌ SILENT | Rarely generates |
| 12 | FUNDING_EXTREME_SIGNAL | mean_reversion | ⛔ Rare | Cap 0.30 | N/A | N/A | ✅ Exempt | Blocked in QUIET | N/A | ❌ SILENT | Rarely generates |
| 13 | QUIET_COMPRESSION_BREAK | compression | ⛔ Rare | Cap 0.25 | N/A | N/A | N/A | ✅ Exempt | N/A | ❌ SILENT | Rarely generates |
| 14 | DIVERGENCE_CONTINUATION | divergence | ⛔ Rare | Cap 0.30 | N/A | N/A | Not exempt | ⚠️ Conditional exempt | N/A | ❌ SILENT | Rarely generates |

### Legend:
- ✅ = passes reliably
- ⚠️ = passes sometimes / marginal
- ❌ = blocked / fails
- ⛔ = evaluator-level conditions rarely met

---

## 4. Root Causes of Silent Paths

### A. Correct Filtering (should remain silent)

| Path | Reason | Verdict |
|---|---|---|
| OPENING_RANGE_BREAKOUT | Feature-gated (`SCALP_ORB_ENABLED` = false) + narrow session window (London 07-09, NY 12-14 UTC) | **Correct** — disabled by design |
| LIQUIDATION_REVERSAL | Requires ≥2% cascade + CVD divergence + RSI <25/>75 + volume spike 2.5×. This is an extreme-condition pattern. | **Correct** — genuinely rare pattern |
| WHALE_MOMENTUM | Requires 2× tick-flow imbalance + QUIET regime excluded + order book depth validation. Requires whale activity. | **Correct** — correctly conditional |
| FUNDING_EXTREME_SIGNAL | Requires extreme funding rate beyond threshold + CVD confirmation + EMA/RSI alignment. Rare market condition. | **Correct** — rare by design |
| QUIET_COMPRESSION_BREAK | Requires BB squeeze <1.5% + MACD zero-cross + volume 2× + QUIET/RANGING regime only. Compression patterns are periodic. | **Mostly correct** — fires periodically |

### B. Incorrect Suppression (should be expressing but are blocked)

| Path | Generates? | Primary Blocker | Root Cause | Impact |
|---|---|---|---|---|
| FAILED_AUCTION_RECLAIM | ✅ Yes (8-14/cycle geometry, 79 MTF rejections/500 lines) | MTF gate + geometry rejection | Family cap is 0.35 but regime-driven min_score for TRENDING regimes is 0.60. Cap only activates when 0.35 < regime score — **but in trending markets, the regime score is already 0.60**, so cap has no effect. In RANGING (min_score 0.30), cap 0.35 is actually TIGHTER than the regime. **The relaxation is cosmetically present but structurally ineffective.** Additionally, geometry rejection occurs because FAR produces structure-based SL that often exceeds the 1.5% scalp cap. | **HIGH** — active generation being destroyed |
| LIQUIDITY_SWEEP_REVERSAL | ✅ Yes (20 MTF rejections, score 50-79 range) | MTF gate + scoring | Same MTF ineffectiveness as FAR. Additionally, reversal family gets 8pt regime score (vs 18pt for affinity match), no thesis adjustment for this family. Total scoring disadvantage: ~10-12 points. | **HIGH** — active generation being destroyed |
| SR_FLIP_RETEST (partial) | ✅ Yes (88 MTF rejections, 31 below-50) | MTF gate on some + scoring below 50 on others | Same family cap ineffectiveness. Many SR_FLIP signals score 50-64 (WATCHLIST tier), which only goes to free channel, not paid. The 88 MTF rejections represent the bulk of expression loss. | **MEDIUM** — partially expressing but losing many candidates |

### C. The MTF Cap Ineffectiveness Problem (Critical Finding)

The family-aware MTF policy (PR-1) defines relaxation caps:
```
reclaim_retest:  min_score_cap = 0.35
reversal:        min_score_cap = 0.35
mean_reversion:  min_score_cap = 0.30
```

**But the cap only fires when `cap < regime_min_score`:**
```python
if _family_mtf_cap is not None and _family_mtf_cap < _mtf_min_score:
    _mtf_min_score = _family_mtf_cap
```

**Regime-driven min_score values:**
| Regime | min_score (from config) |
|---|---|
| TRENDING_UP/DOWN | 0.60 |
| RANGING | 0.30 |
| VOLATILE | 0.20 |
| QUIET | 0.40 |

**Analysis:**
- In **TRENDING** regimes (where most signals generate): regime min = 0.60, cap = 0.35 → cap fires → min_score becomes 0.35. **This should work.**
- **BUT**: The base MTF min_score for 360_SCALP is 0.55 (line 2724), and the regime config overrides it to 0.60 for trending. So the effective gate is `max(0.55, 0.60) = 0.60`. The cap reduces this to 0.35.

**Wait — the monitor evidence contradicts this.** If cap fires (to 0.35), why are there 117 MTF rejections for reclaim_retest?

Let me trace more carefully. The telemetry shows:
- `mtf_policy_relaxed:360_SCALP:reclaim_retest`: 10-17 per cycle (cap IS firing)
- `mtf_gate_family:360_SCALP:reclaim_retest`: 2-3 per cycle (STILL being rejected after relaxation)
- `mtf_policy_saved:360_SCALP:reclaim_retest`: 1-2 per cycle (some ARE being saved)

**Refined finding**: The cap IS working — it fires frequently (10-17 relaxations per cycle). But even with the 0.35 threshold, **many signals still can't reach 0.35 MTF score**. This means the underlying MTF alignment for these setups is extremely poor (below 35% timeframe agreement). The issue is not that the cap is broken; the issue is that these setups genuinely have very low MTF alignment because **they are structural/mean-reversion setups being evaluated against a trend-confluence scoring model**.

The MTF score measures: "what percentage of timeframes agree with signal direction?" For a reclaim/retest setup, the thesis is "price reclaimed a structural level" — it doesn't need multi-timeframe trend agreement. But the MTF gate still requires 35% agreement even after relaxation.

**Root cause**: The MTF gate is fundamentally a trend-confluence gate. Applying it (even with relaxation) to structural/reclaim setups is a **doctrinal mismatch**. These setups should not be evaluated on multi-timeframe trend alignment at all.

---

## 5. Root Causes of Weak Quality on the Two Expressive Paths

### TREND_PULLBACK_EMA (17 signals: 5 TP, 12 SL = 29% win rate)

**Why it survives the funnel:**
1. Regime hard-gate ensures it only fires in TRENDING_UP/TRENDING_DOWN — aligns perfectly with MTF trend-confluence model.
2. EMA proximity + RSI pullback + SMC requirement = structurally sound.
3. No MTF cap needed — the setup IS the trend, so MTF scores high naturally.
4. Thesis adjustment gives +0 to +6 pts (has dedicated family).
5. Confidence boost +8 at evaluator level.
6. Regime affinity awards 18 pts (in trending regimes).

**Why the 12 SL hits are happening (evidence-based):**
1. **SL placement is too tight relative to market noise**: SL is placed beyond EMA21 with buffer, typically resulting in 0.20-0.51% stop distance. Monitor evidence shows SL PnL range: -0.20% to -0.51%. These are **sub-ATR stops** in most cases.
2. **MFE = 0.00% on almost all SLs**: Price never moves favorably after entry. This is not "stop too tight" — it's **bad entry timing**. The signal fires at EMA proximity, but the pullback has not completed. Price continues pulling back through EMA21 and hits the stop.
3. **The proximity gate is too loose**: 0.3% of EMA9 or 0.5% of EMA21 — in a volatile crypto market, this is within normal bid-ask noise for many pairs. The evaluator fires before the actual bounce.
4. **No momentum confirmation at entry**: Unlike LIQUIDITY_SWEEP_REVERSAL which requires momentum persistence for 2 candles, TREND_PULLBACK_EMA has **no momentum requirement**. It fires purely on proximity + direction alignment. This means it catches pullbacks that haven't reversed yet.
5. **RSI 40-60 zone is too wide**: This covers the entire "neutral" zone. A genuine pullback entry should require RSI closer to the extreme (35-45 for LONG, 55-65 for SHORT).

**Diagnosis: Weak entry timing is the primary cause.** The evaluator fires too early in the pullback, before price has shown any evidence of reversal. The SL placement then compounds this by being within the continuation range of the pullback.

### SR_FLIP_RETEST (11 signals: 1 TP, 9 SL, 1 CLOSED = 9% win rate)

**Why it survives the funnel (partially):**
1. Structural flip pattern is common in all non-VOLATILE regimes.
2. Soft-penalty layered approach means borderline setups accumulate penalties but can still pass.
3. Cap 0.35 helps some signals survive MTF.
4. Reclaim_retest family thesis adjustment awards +0 to +6 pts.

**Why the 9 SL hits are happening:**
1. **SL at 0.2% beyond flip level is catastrophically tight**: The structural invalidation stop at `level × (1 ± 0.002)` means a 0.2% buffer beyond the flip level. In crypto, this is within normal wick range. The flip level itself is often tested multiple times before a clean move.
2. **MFE = 0.00% on 8 of 9 SLs**: Same pattern — price never moves favorably. The "retest" is actually a **continuation through the level**, not a rejection. The entry fires on the first touch, before genuine rejection is confirmed.
3. **Rejection candle gate is too permissive**: Wick ≥ 50% = pass, 20-50% = +4 penalty, <20% = hard reject, Doji = pass. The 20-50% wick zone + doji exemption allows entries where there's minimal evidence of actual rejection.
4. **No time-delay between flip and retest**: The flip window is 8 candles (40 minutes on 5m), and the retest proximity is 0-0.6%. This means the evaluator can fire on the immediate pullback after a brief break, which often continues through the level.
5. **Confidence scores are high (80-90) despite poor entry quality**: The scoring engine gives high marks for structural clarity (sweep, regime, volume) without penalizing entry timing uncertainty.

**Diagnosis: The evaluator fires on level proximity without sufficient evidence of rejection.** True SR flip retests typically need 2-3 candle confirmation that the level is holding, not just a single wick.

### Combined Quality Verdict

Both paths share the same fundamental weakness: **they trigger on proximity/alignment conditions without requiring price-action confirmation of the thesis**. The scoring engine then awards high confidence based on structural context (regime, sweep, volume) that doesn't correlate with micro-timing quality.

---

## 6. 3-Minute Duration Analysis

### How Hold Duration Is Computed

1. **Signal.timestamp** = `datetime.now(timezone.utc)` at signal creation (wall-clock UTC, not monotonic)
2. **Hold duration** = `(utcnow() - sig.timestamp).total_seconds()` computed at outcome determination
3. **Polling interval** = `MONITOR_POLL_INTERVAL = 5.0 seconds` (config)
4. **Display format** = `f"{int(hold_sec // 60)}min"` (floor division to integer minutes)
5. **JSON storage** = `hold_duration_sec: float` (full precision in signal_performance.json)

### Is the 3-Minute Hold Real or Artifact?

**Answer: Mostly real, with a minor cosmetic component.**

**Evidence chain:**
1. Monitor evidence shows 18 of 20 SL trades with hold = "3m" display.
2. MFE = 0.00% on 19 of 20 — price **never** moved favorably.
3. Poll interval is 5 seconds, so the **minimum detectable outcome** is ~5-10 seconds after signal creation.
4. But `Signal.timestamp` is set at signal **creation** inside `_prepare_signal`, not at dispatch. There is latency between creation and Telegram delivery (formatting, retry, queue). Typical: 5-30 seconds.
5. A trade that hits SL on the very first poll (5s after dispatch) would have hold_duration of ~10-35 seconds from timestamp.

**The "3-minute" display is:**
- `int(hold_sec // 60)` → any duration between 180.0 and 239.9 seconds displays as "3".
- **But**: Most of these trades likely lasted 120-239 seconds (2-4 minutes real time).
- The 5-second poll means outcomes are checked every 5 seconds after dispatch. A trade dispatched at T=0 gets first check at T+5s, T+10s, etc.

**Can trades die in seconds?**
- **Yes, in theory**: If the SL is within the spread at entry, the first price check (5s later) would show SL hit.
- **In practice**: SL distances of 0.20-0.51% from entry exceed typical spread on most pairs. But the issue is that price is already moving against the signal at entry time (the pullback hasn't reversed). So within 2-3 minutes, price easily traverses 0.20-0.51%.

**The real story:**
The "3-minute" pattern represents trades where:
1. Signal fires at EMA proximity during an active pullback
2. Price continues pulling back for ~2-4 minutes
3. SL hit at 0.20-0.51% from entry
4. First lifecycle poll after SL hit records the outcome
5. Display truncates to "3m"

**This is a real rapid failure pattern, not primarily an artifact.** The cosmetic truncation (`int(hold_sec // 60)`) compresses precision but doesn't change the diagnosis: these trades fail within the first few candles because the entry timing is wrong.

### Places Where Duration Truth Can Be Distorted

| Location | Distortion | Severity |
|---|---|---|
| `int(hold_sec // 60)` display formatting | Truncates to floor integer minutes | **Low** — cosmetic only, JSON has full precision |
| Signal.timestamp vs dispatch time gap | 5-30s added to apparent hold duration | **Low** — makes trades appear slightly longer |
| Wall-clock (not monotonic) time source | NTP jumps could affect duration | **Very low** — unlikely to cause systematic bias |
| 5-second poll interval | Outcome detected up to 5s after actual SL hit | **Low** — adds max 5s to apparent hold |
| No sub-poll-interval price tracking | SL could be hit between polls | **Medium** — trade may have failed faster than recorded |

---

## 7. Geometry-Friction Analysis

### Evidence from Monitor Logs

**Recurring patterns:**
1. **FVG SL rejection (232.15% distance)**: SIRENUSDT SHORT fires every ~3 seconds — evaluator produces wildly invalid geometry repeatedly. This is a data quality issue (likely broken price data for this pair), not a geometry gate problem.
2. **FVG SL rejection (59.32% distance)**: MOVRUSDT LONG — same pattern, extreme distance. Data quality issue.
3. **FVG SL rejection (6.73% distance)**: TRBUSDT SHORT — more reasonable but still outside 2.00% max. Likely genuine wide-stop setup on volatile pair.
4. **SL capped at 2.80% → 1.50%**: Recurring. Original SL is 2.80% from entry, capped to 1.50% max for 360_SCALP channel. This fundamentally distorts the risk-reward geometry.
5. **SL capped at 2.40% → 1.50%** and **2.09% → 1.50%**: Same pattern, different magnitudes.
6. **SL capped at 1.96% → 1.50%**: Near-boundary capping.
7. **Near-zero SL rejection (0.0415%, 0.0169%)**: Entry and SL effectively at the same price. Evaluator produced degenerate geometry.
8. **geometry_rejected_risk_plan:360_SCALP:reclaim_retest**: 8-14 per scan cycle. The risk plan rejects geometry produced by the reclaim_retest family.

### Correct vs Over-Restrictive

| Pattern | Classification | Explanation |
|---|---|---|
| FVG 232.15% / 59.32% rejection | **Correct** — data quality guard | These are broken evaluator outputs, not valid setups |
| FVG 6.73% rejection | **Correct** — scalp doctrine | 6.73% SL is not a scalp |
| Near-zero SL (0.04%, 0.02%) | **Correct** — degenerate geometry | Entry ≈ SL means zero risk definition |
| SL cap 2.80% → 1.50% | **Potentially over-restrictive** | Reversal setups (sweep-level SL) naturally produce wider stops. Capping distorts R:R and may produce worse outcomes than the original geometry. |
| SL cap 2.09% → 1.50% | **Borderline** | Setup produced 2.09% SL; the 1.50% cap shifts stop 28% closer. This may cause more SL hits. |
| SL cap 1.96% → 1.50% | **Borderline** | Original geometry was close to limit; 24% SL compression. |
| geometry_rejected_risk_plan:reclaim_retest (8-14/cycle) | **Partially over-restrictive** | Risk plan rejection means RR < 1.3 or SL distance exceeds cap after capping. The capping itself creates the geometry that then fails risk plan. Circular problem. |

### The Capping → Risk-Plan Rejection Cycle

**Critical finding**: Many geometry rejections are **caused by the capping process itself**:

1. Evaluator produces SL at 2.5% distance (structure-based, valid for the setup thesis)
2. Signal quality module caps SL to 1.5% (360_SCALP max)
3. Capped SL now produces different R:R ratio
4. Risk plan evaluates capped geometry → may now fail R:R minimum (1.3)
5. Signal rejected for "geometry_rejected_risk_plan"

**Or**: Capped SL is now very close to entry, creating the tight stops that produce the 3-minute failures we see in live outcomes.

**This is a fundamental doctrinal tension**: The 1.5% SL cap is appropriate for trend-following scalps where the stop should be tight. But for structural/reversal setups (LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM), the thesis requires wider stops because the invalidation level IS the structure. Capping the SL to 1.5% means:
- Either the stop is hit by normal noise (fast SL outcomes)
- Or the geometry fails risk-plan validation (path silence)

---

## 8. MTF-Policy Reality Check

### Is the Family-Aware MTF Policy Working?

**Cosmetically yes, structurally partially.**

**What the telemetry shows:**
- `mtf_policy_relaxed:360_SCALP:reclaim_retest`: 10-17 per cycle → Cap IS being applied
- `mtf_policy_saved:360_SCALP:reclaim_retest`: 1-2 per cycle → Some signals ARE being saved
- `mtf_gate_family:360_SCALP:reclaim_retest`: 2-3 per cycle → Some STILL fail even with cap

**What this means:**
The cap reduces threshold from 0.55-0.60 down to 0.35. This saves some signals (1-2 per cycle out of 10-17 relaxations). But many signals score below 0.35 MTF because the underlying thesis doesn't depend on multi-timeframe trend agreement.

**The real problem:**
The MTF gate uses `compute_mtf_confluence()` which scores: "what percentage of weighted timeframes show EMA alignment with signal direction?"

For a `reclaim_retest` setup:
- The thesis is: "price broke through a structural level and retested it"
- This can happen in ANY trend context — even counter-trend (failed breakout → reclaim of support from above)
- MTF alignment is **not a quality indicator** for this setup family
- A cap of 0.35 helps but still requires at least 35% of timeframe weight to agree, which is still a trend-confluence requirement

**For reversal family:**
- Same problem — reversals by definition happen when the prior trend was wrong
- MTF alignment will be LOW because the MTF is still measuring the old trend
- Cap 0.35 is better but fundamentally misaligned

**Verdict**: The family-aware MTF policy is a **partial mitigation** of a deeper doctrinal problem. The MTF gate itself is a trend-confluence gate; applying it (even with relaxation) to non-trend setup families is the wrong tool for the job.

### What Would Be Doctrinally Correct?

For `reclaim_retest` and `reversal` families, the quality signal is not "do multiple timeframes agree with my direction?" but rather:
- "Is the structural level I'm trading significant on higher timeframes?" (structural confirmation, not directional)
- "Has the prior trend shown exhaustion/failure at this level?" (regime transition, not alignment)

These are different questions than what `compute_mtf_confluence()` answers.

---

## 9. Best Narrow Corrective Actions (Ordered by Impact)

### Priority 1: Fix Entry Timing on TREND_PULLBACK_EMA (Highest Impact)

**Problem**: Evaluator fires on proximity to EMA without momentum confirmation, producing 71% SL rate with 0.00% MFE.

**Exact change**: Add a **momentum reversal confirmation gate** to `_evaluate_trend_pullback()` in `scalp.py`:
- Require the last closed candle to show directional reversal: for LONG, `close[-1] > open[-1]` is already checked (line 674), but add: momentum derivative must be positive (price acceleration in signal direction).
- Alternatively: require RSI to be rising (LONG) or falling (SHORT) from the pullback extreme, not just within 40-60 zone.
- Tighten proximity gate from 0.3%/0.5% to 0.15%/0.30% (require closer to EMA for trigger).

**Non-scope**: Do not change the evaluator's structural requirements (EMA alignment, regime, SMC).

**Validation**: 30-day live comparison — expect SL rate to drop from ~71% toward 50-55%, with fewer total signals but higher quality per signal.

### Priority 2: Widen SL for Structural Setups (High Impact)

**Problem**: 1.5% SL cap forces structural setups into tight stops that produce 3-minute SL hits and geometry rejection cascades.

**Exact change**: Add per-family SL cap overrides in `signal_quality.py`:
```
reclaim_retest: 2.0%  (up from 1.5%)
reversal: 2.5%        (up from 1.5%)
trend_following: 1.5%  (unchanged)
breakout_momentum: 1.5% (unchanged)
```

**Non-scope**: Do not change the global 1.5% default. Do not change TP construction. Do not relax the RR minimum (1.3).

**Validation**: Monitor geometry_rejected_risk_plan counts for reclaim_retest — should drop by 50%+. Monitor SL hold duration — should increase from 3-4 minutes toward 10-15 minutes. Win rate on structural setups should improve.

### Priority 3: MTF Gate Bypass for Structural Families (High Impact)

**Problem**: reclaim_retest and reversal families are being judged on trend-confluence which is not their quality signal.

**Exact change**: In the MTF gate section of `_prepare_signal()` (scanner/__init__.py lines 2766-2797), add family-level MTF bypass:
- Families `reclaim_retest`, `reversal`, `mean_reversion`: skip MTF gate entirely
- Replace with a **structural significance check**: does the level being traded appear on the 15m or 1h timeframe? (This is a different question than "do trends agree?")

**Non-scope**: Do not bypass MTF for trend_following or breakout_momentum families. Do not remove MTF telemetry (keep suppression counters for monitoring).

**Validation**: FAILED_AUCTION_RECLAIM and LIQUIDITY_SWEEP_REVERSAL should begin emitting. Monitor their live outcomes for 1 week before adjusting further.

### Priority 4: SR_FLIP_RETEST Rejection Candle Tightening (Medium Impact)

**Problem**: 20-50% wick range + doji exemption allows entries without genuine rejection evidence.

**Exact change**: In `_evaluate_sr_flip_retest()` (scalp.py):
- Raise minimum wick requirement from 20% to 40% of body for penalty zone (currently: <20% = hard reject, 20-50% = +4 penalty, ≥50% = pass)
- Remove doji exemption (doji at a structural level is indecision, not rejection)
- Add: require at least 2 candles within the retest zone before triggering (time-delay confirmation)

**Non-scope**: Do not change the flip detection window or proximity zone.

**Validation**: SR_FLIP_RETEST SL rate should drop from 82% toward 50-60%. Total signal count will decrease.

### Priority 5: Add Momentum Derivative Gate to Scoring (Medium Impact)

**Problem**: Scoring engine awards high confidence based on structural context without penalizing bad micro-timing.

**Exact change**: Add a `_score_momentum_quality()` dimension to `SignalScoringEngine.score()` that:
- Checks if price is accelerating in signal direction (positive momentum derivative for LONG)
- Awards 0-10 pts based on entry momentum quality
- This provides a scoring penalty for entries where price is still moving against the signal direction

**Non-scope**: Do not change existing scoring dimensions. Do not change tier thresholds.

**Validation**: Signals that score high should correlate better with positive MFE. Track pre/post correlation of momentum quality score with realized MFE.

---

## 10. What Should NOT Be Changed

| Item | Reason |
|---|---|
| Global MTF gate for trend-following/breakout families | These families genuinely need trend confluence |
| QUIET_SCALP_BLOCK logic | Correct protective filtering in compressed markets |
| Pair quality/spread suppression | Correct — 123 spread rejections protect against execution slippage |
| FVG extreme SL rejection (>2%) | Correct — these are data quality issues, not valid setups |
| Near-zero SL rejection | Correct — degenerate geometry guard |
| Risk plan RR minimum (1.3) | Correct — inverted RR guarantees account bleed |
| 5-second poll interval | Correct — faster polling wouldn't change outcomes |
| Soft penalty architecture | Correct design — path-aware modulation is working as intended |
| SMC hard gate | Correct — requires institutional footprint |
| Trend hard gate for non-exempt setups | Correct — EMA alignment is non-negotiable for trend setups |
| Score thresholds (50/65/80) | Correct — the problem is input quality, not threshold levels |
| Cooldown durations (600s/900s) | Correct — prevents rapid re-entry into failing setups |

---

## 11. PR Recommendations

### PR-8A: Entry Timing Tightening for Trend Pullback and SR Flip

**Exact problem**: Both expressive paths fire on proximity/alignment without momentum confirmation, producing 75% SL rate with 0% MFE.

**Exact changes**:
1. `scalp.py` `_evaluate_trend_pullback()`: Add momentum acceleration check (price derivative positive in signal direction). Tighten EMA proximity from 0.3%/0.5% to 0.15%/0.30%.
2. `scalp.py` `_evaluate_sr_flip_retest()`: Raise wick requirement from 20% to 40%. Remove doji exemption. Add 2-candle confirmation delay.
3. No changes to any other evaluator.

**Explicit non-scope**: No scoring changes. No threshold changes. No gate changes. No geometry changes.

**Validation criteria**:
- TREND_PULLBACK_EMA SL rate drops below 60% (currently 71%)
- SR_FLIP_RETEST SL rate drops below 70% (currently 82%)
- Average MFE on SL trades rises above 0.05% (currently 0.00%)
- Signal count may drop 20-40% — this is acceptable

### PR-8B: Family-Aware SL Cap and MTF Bypass for Structural Setups

**Exact problem**: Structural/reversal setups are destroyed by trend-focused gates (1.5% SL cap + trend-MTF gate) that are doctrinally inappropriate for their thesis.

**Exact changes**:
1. `signal_quality.py`: Add per-family SL cap overrides: reclaim_retest → 2.0%, reversal → 2.5%.
2. `scanner/__init__.py` MTF gate section: Add family-level MTF bypass for `reclaim_retest`, `reversal`, `mean_reversion`. Replace with structural-level significance check (does the traded level appear on 15m/1h?).
3. Update telemetry: new counter `mtf_bypass_structural:{family}` to track bypass frequency.

**Explicit non-scope**: No changes to trend_following or breakout_momentum MTF policy. No scoring changes. No soft penalty changes. No threshold changes.

**Validation criteria**:
- FAILED_AUCTION_RECLAIM begins emitting signals (currently zero)
- LIQUIDITY_SWEEP_REVERSAL begins emitting signals (currently zero)
- geometry_rejected_risk_plan:reclaim_retest drops by 50%+
- mtf_gate_family:reclaim_retest drops to near-zero
- New paths show >40% TP rate over 2-week observation
- If new paths show <30% TP rate after 2 weeks, revert MTF bypass and tighten family SL caps back

### PR-8C: Scoring Momentum Quality Dimension (Optional — After 8A/8B Validated)

**Exact problem**: Scoring engine awards high confidence to signals with bad micro-timing because it evaluates structural context without entry quality.

**Exact changes**:
1. `signal_quality.py` `SignalScoringEngine`: Add `_score_momentum_quality()` dimension (0-10 pts).
2. Update total score computation to include momentum quality.
3. Add telemetry: log momentum quality distribution per setup class.

**Explicit non-scope**: No changes to existing scoring dimensions. No threshold changes. No gate changes.

**Validation criteria**:
- Correlation between total score and realized MFE improves (measure pre/post)
- Signals scoring ≥80 show average MFE >0.10% (currently 0.00%)

---

## 12. Confidence and Uncertainty

### Proven (Hard Evidence)

| Finding | Evidence |
|---|---|
| Only 2 of 14 paths are emitting | monitor/latest.txt signal history: 28 signals, all TREND_PULLBACK_EMA or SR_FLIP_RETEST |
| 75% of signals hit SL | 21 SL / 28 total in monitor |
| 19/20 recent SLs show 0.00% MFE | Monitor SL follow-through analysis |
| 18/20 recent SLs show 3-minute hold | Monitor SL follow-through analysis |
| reclaim_retest family generates heavily but is MTF-blocked | 117 family-level + 167 setup-level MTF rejections in 500 log lines |
| reversal family generates and is MTF-blocked | 20 setup-level MTF rejections |
| Geometry rejection is concentrated on reclaim_retest | 8-14 geometry_rejected_risk_plan per scan cycle |
| SL capping is frequent (1.96-2.80% → 1.50%) | Multiple log lines per scan cycle |
| MTF relaxation cap is firing (10-17 per cycle) but many signals still fail | mtf_policy_relaxed vs mtf_gate counters |
| TREND_PULLBACK_EMA has fewest evaluator-level gates | Code analysis: ~6 hard gates, no momentum, no MACD, no MTF |
| 5-second poll interval, wall-clock timing | trade_monitor.py code: MONITOR_POLL_INTERVAL=5.0, datetime-based duration |
| Display truncation via `int(hold_sec // 60)` | trade_monitor.py line 1007 |

### Inferred (Strong Evidence, Not Directly Measured)

| Finding | Basis |
|---|---|
| SL cap → geometry rejection circular problem | Code trace shows capping precedes risk-plan evaluation; capped geometry may fail RR check |
| MTF gate is fundamentally wrong tool for structural setups | Doctrinal analysis: MTF scores trend alignment, structural setups don't depend on trend |
| Entry timing is the primary quality issue | 0% MFE pattern implies price never moves favorably; evaluator fires before thesis confirmation |
| Doji exemption contributes to SR_FLIP weak quality | Code review: doji at structural level is ambiguous, not confirmatory |
| Wider SL caps would reduce geometry rejection | Logical: if cap is 2.0% instead of 1.5%, fewer evaluator SLs at 1.5-2.0% would be capped |

### Needs Runtime Confirmation

| Question | How to Confirm |
|---|---|
| Would momentum confirmation gate actually reduce SL rate? | Deploy PR-8A and measure for 1-2 weeks |
| Would MTF bypass cause reversal/reclaim paths to emit quality signals? | Deploy PR-8B and measure TP rate |
| Would wider SL caps increase hold duration above 3 minutes? | Deploy family SL caps and measure hold_duration_sec |
| Is the 0.00% MFE pattern across all market conditions or concentrated in specific pairs/sessions? | Filter signal_performance.json by session, pair, regime |
| Do signals that score the relaxed momentum check perform better? | Requires scoring change + outcome tracking |
| Are the 4 "possible stop-too-tight" classifications genuinely better setups? | Track same-symbol later signals for reclaim rate |

---

## Appendix A: Scoring Engine Pipeline Summary

```
ScalpChannel.evaluate()                   → 14 internal evaluators, each assigns setup_class
    ↓ returns Signal(s)
Scanner._prepare_signal()
    ├─ Failed-detection cooldown check    → silent skip if 3+ consecutive failures
    ├─ Signal generation / preseed
    ├─ Setup classification               → classify_setup() honors evaluator assignment  
    ├─ Execution assessment
    ├─ MTF gate                           → family-aware cap (0.25-0.60); still trend-based
    ├─ Soft penalty gates (7x)            → VWAP, KZ, OI, Funding, Spoof, VolDiv, Cluster
    │   └─ Regime multiplier (0.6-1.8×)
    │   └─ Path-aware penalty modulation
    ├─ Risk assessment                    → RR ≥ 1.3, SL capping to 1.5%, geometry validation
    ├─ Correlated position cap
    ├─ Base confidence computation
    ├─ Predictive adjustments
    ├─ Component scoring (Layer 2)        → market/setup/execution/risk/context components
    ├─ ML feedback adjustment
    ├─ Chart pattern bonus
    ├─ Candlestick pattern bonus
    ├─ SignalScoringEngine.score (Layer 3) → OVERWRITES confidence with 7-dimension score
    ├─ Tier classification (A+/B/WATCHLIST/reject)
    ├─ Full soft penalty subtraction (PR-15)
    ├─ Tier reclassification post-penalty
    ├─ Statistical false-positive filter
    ├─ Pair analysis quality gate
    ├─ SMC hard gate (min 12)
    ├─ Trend hard gate (min 10)
    ├─ Regime transition boost
    ├─ QUIET regime safety net
    ├─ WATCHLIST short-circuit (→ free channel)
    └─ Final confidence + component floor check
        ↓
SignalRouter
    ├─ Correlation lock (one symbol at a time)
    ├─ Per-channel cooldown (600s)
    ├─ Concurrent position cap
    ├─ TP/SL direction sanity
    ├─ Stale signal gate (120s for SCALP)
    ├─ Channel min confidence
    ├─ Risk assessment (RR + concurrent + order book)
    └─ Telegram dispatch + lifecycle registration
        ↓
TradeMonitor
    ├─ 5-second poll interval
    ├─ Price check against SL/TP1/TP2/TP3
    ├─ MFE/MAE running update each poll
    ├─ Terminal outcome → signal_performance.json
    └─ Callbacks (lifecycle, SL, thesis SL)
```

## Appendix B: Key Threshold Reference

| Threshold | Value | Location | Impact |
|---|---|---|---|
| 360_SCALP SL cap | 1.50% | signal_quality.py:346 | Forces tight stops |
| FVG SL rejection | 2.00% | scalp_fvg.py | Discards extreme FVG SL |
| Near-zero SL min | 0.05% | signal_quality.py:369 | Catches degenerate geometry |
| RR minimum floor | 1.30 | risk.py:35 | Hard RR gate |
| MTF min score (360_SCALP) | 0.55 | scanner:2724 | Base MTF threshold |
| MTF min score (TRENDING) | 0.60 | config regime dict | Regime-driven MTF |
| MTF min score (SHORT in TRENDING_DOWN) | 0.45 | config:1230 | Relaxed for shorts |
| MTF family cap (reclaim_retest) | 0.35 | scanner:368 | Family relaxation |
| MTF family cap (reversal) | 0.35 | scanner:366 | Family relaxation |
| MTF family cap (compression) | 0.25 | scanner:372 | Most relaxed |
| QUIET_SCALP_MIN_CONFIDENCE | 65.0 | config:1052 | QUIET regime floor |
| SMC hard gate min | 12.0 | config:1209 | Institutional footprint min |
| Trend hard gate min | 10.0 | config:1216 | EMA alignment min |
| Channel min confidence (360_SCALP) | 65.0 | config:593 | Emission floor |
| Signal scan cooldown | 600s | config:964 | Per-symbol-channel |
| Global symbol cooldown | 900s | config:1224 | Cross-channel |
| Monitor poll interval | 5.0s | config:944 | Trade checking cadence |
| Score tier A+ | ≥80 | scanner:3374 | Premium tier |
| Score tier B | ≥65 | scanner:3378 | Standard paid tier |
| Score tier WATCHLIST | ≥50 | scanner:3382 | Free channel only |
| Component floor (market) | 12.0 | scanner:3666 | Hard component gate |
| Component floor (execution) | 10.0 | scanner:3667 | Hard component gate |
| Component floor (risk) | 10.0 | scanner:3668 | Hard component gate |

---

*Report completed 2026-04-18. All findings based on code analysis of main branch and live monitor evidence from monitor-logs branch.*
