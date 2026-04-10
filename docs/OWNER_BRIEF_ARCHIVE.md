# OWNER_BRIEF Archive

> **This file preserves historical material from the OWNER_BRIEF.md that predates the 2026-04-10 canonical redesign.**
> The live operating manual is in `OWNER_BRIEF.md` at repo root.
> This archive exists for reference only — it does not define current operating state.

---

## Full PR History (PR1 through PR14)

### PR1 — Signal Quality Overhaul — MERGED (PR#44, 2026-04-06)
- SMC hard gate (smc_score >= 12), trend hard gate (trend_score >= 10)
- Per-channel confidence thresholds (SCALP=80, FVG=78, OB=78, DIV=76)
- ADX minimum raised, global 30-min cooldown, named signal headers
- 4 channels soft-disabled (CVD, VWAP, SUPERTREND, ICHIMOKU)
- Pairs expanded to 75

### PR2 — AI-Powered Engagement Layer — MERGED (PR#45, 2026-04-06)
- Scheduled content (morning brief, session opens, EOD wrap, weekly card)
- Radar alerts — soft-disabled channels at conf >= 65 post to free channel
- Trade closed posts — every TP and SL auto-posts
- Smart silence breaker — 3hr silence during trading hours triggers market watch post
- GPT-4o-mini analyst voice, rotating variants, template fallback

### PR2-bugfix — Fix scheduler routing + BTC price + digest misclassification — MERGED (PR#46, PR#47, 2026-04-06)
- Fixed /digest win/loss misclassification for INVALIDATED trades
- Fixed scheduler routing, BTC price, silence breaker, radar scores

### PR3 — Scan Latency Fix + 75-Pair Universe Unlock — MERGED (PR#48, 2026-04-07)
- Indicator result cache — eliminates ~90% of thread pool work per cycle
- SMC detection deduplicated — 4 detections to 2 per symbol
- Scan latency reduced from 33-40s to 8-12s
- WS_DEGRADED_MAX_PAIRS default raised 50 to 75

### PR4 — User Interaction Layer — MERGED (PR#49, 2026-04-07)
- Protective Mode Broadcaster — auto-posts when market volatile/unsuitable
- Commands revamped — /signals, /history, /market, /performance, /ask

### PR5 — Signal Safety — MERGED (PR#50, 2026-04-07)
- Near-zero SL rejection (< 0.05% from entry)
- Failed-detection cooldown (3 consecutive failures -> 60s suppression)
- Dynamic pair count in all subscriber-facing commands

### PR6 — Dead Channel Removal — MERGED (PR#51, 2026-04-07)
- Removed 360_SPOT, 360_GEM, 360_SWING, 360_SCALP_OBI from entire codebase
- Depth fetches and depth circuit breaker fully removed

### PR7 — Signal Architecture Overhaul — MERGED (PR#52, 2026-04-07)
- REMOVED _evaluate_range_fade (BB mean reversion — no SMC basis, retail strategy)
- FIXED Cross-asset gate — now direction-aware and graduated by correlation strength
- FIXED Regime ADX lag — EMA9 slope fast-path for TRENDING_DOWN detection
- FIXED HTF EMA rejection threshold 0.05% -> 0.15%
- FIXED EMA crossover invalidation age gate (>= 300s)
- FIXED Momentum threshold — ATR-adaptive per pair
- ADDED _evaluate_trend_pullback (TREND_PULLBACK_CONTINUATION)
- ADDED _evaluate_liquidation_reversal (LIQUIDATION_REVERSAL)
- ADDED detect_continuation_sweep() in smc.py
- ADDED Regime transition boost (RANGING->TRENDING_DOWN boosts SHORTs +6)
- ADDED Per-pair session multipliers in kill_zone.py
- Global symbol cooldown: 1800s -> 900s, made directional (symbol+direction keyed)

### PR7-bugfix — _regime_key NameError fix — MERGED (PR#53, 2026-04-08)
- Fixed _regime_key NameError in _compute_base_confidence

### PR8 — Volume Surge Signal Paths + Dynamic Discovery — MERGED (PR#54, 2026-04-08)
- ADDED _evaluate_volume_surge_breakout (VOLUME_SURGE_BREAKOUT) — breakout + retest entry
- ADDED _evaluate_breakdown_short (BREAKDOWN_SHORT) — mirror for shorts
- ADDED Dynamic pair promotion — 5x volume surge promotes pair for 3 scan cycles
- ADDED Signal expiry notifications via Telegram
- FIXED Structural SL/TP for _evaluate_standard and _evaluate_trend_pullback
- Blocked in VOLATILE_UNSUITABLE for QUIET only — fires in all other regimes

### PR9 — Method Expansion + Diagnostics — MERGED (PR#55, 2026-04-08)

5 new signal paths (each with own SL/TP from day one — B13):

**1. _evaluate_opening_range_breakout — OPENING_RANGE_BREAKOUT**
- Fires at London open (07:00-09:00 UTC) or NY open (12:00-14:00 UTC)
- Opening range = high/low of first 4 x 5m candles of the session
- Entry: confirmed close above range_high (LONG) or below range_low (SHORT)
- Conditions: volume >= 1.5x avg, EMA9 aligned, SMC basis required (B5)
- SL: range_low - 0.1% (LONG) / range_high + 0.1% (SHORT) — Type 1 structure
- TP: range_height x 1.0 / 1.5 / 2.0 projected from close — Type C measured move
- Regime: TRENDING, VOLATILE only — blocked in QUIET, RANGING

**2. _evaluate_sr_flip_retest — SR_FLIP_RETEST**
- Broken S/R level retested from the other side (resistance to support or vice versa)
- Break must be within last 5 candles; retest within 0.3% of level
- Rejection candle required: wick >= 0.5x body in reversal direction
- SL: level - 0.2% (LONG) / level + 0.2% (SHORT) — Type 1 structure
- TP1: 20-candle 5m swing high/low | TP2: 4h target or sl_dist x 1.5 | TP3: sl_dist x 3.5 — Type B structural
- Regime: RANGING, TRENDING — blocked in VOLATILE

**3. _evaluate_funding_extreme — FUNDING_EXTREME_SIGNAL**
- Funding rate > +0.1% (longs overcrowded, dump) or < -0.1% (shorts overcrowded, squeeze)
- LONG: funding < -0.001, close > EMA9, RSI rising from below 45, CVD agrees
- SHORT: funding > +0.001, close < EMA9, RSI falling from above 55, CVD agrees
- SL: entry +/- liquidation_cluster_distance x 1.1 — Type 5 liquidation distance
- TP1: funding normalization proxy | TP2: sl_dist x 2.0 | TP3: sl_dist x 3.5 — Type E normalization
- Regime: all except QUIET

**4. _evaluate_quiet_compression_break — QUIET_COMPRESSION_BREAK**
- ONLY fires in QUIET or RANGING regime — specifically for compression release
- BB width contracting 3 successive candles: bb_width[-5] > bb_width[-3] > bb_width[-1]
- Confirmed close outside BB band + MACD histogram crosses zero + volume >= 2.0x avg
- SL: bb_lower - 0.1% (LONG) / bb_upper + 0.1% (SHORT) — Type 1 structure
- TP: band_width x 0.5 / 1.0 / 1.5 — Type C measured move

**5. _evaluate_divergence_continuation — DIVERGENCE_CONTINUATION**
- CVD + RSI hidden divergence in trend direction (both must agree)
- LONG: price lower lows + CVD higher lows | SHORT: price higher highs + CVD lower highs
- SL: ema21 - 0.5% (LONG) / ema21 + 0.5% (SHORT) — Type 2 EMA
- TP1: 20-candle 5m swing high/low | TP2: 4h target or sl_dist x 2.5 | TP3: sl_dist x 4.0 — Type B structural

2 diagnostic features added in PR9:
- /why SYMBOL command — gate-by-gate breakdown in dry-run mode
- Live signal pulse — every 30 min for active entry-reached signals

### PR10 — VPS Monitor Workflow — MERGED (PR#56-#63, 2026-04-08)
- Manual GitHub Actions workflow to SSH into VPS and collect live system state
- Writes output to monitor-logs branch (monitor/latest.txt) for autonomous Copilot access
- Health gate: job goes RED if engine not running or unhealthy

### PR10-hotfix — Circuit breaker grace + volatile bypass — MERGED (PR#58, 2026-04-08)
- Private repo auth fix for VPS deploy
- Circuit breaker grace period on startup (178s)
- Volatile_unsuitable bypass for surge/breakdown paths

### PR11 — Heartbeat Path Fix — MERGED (PR#64, 2026-04-08)
- Fixed heartbeat monitoring permanently blind due to named volume path mismatch
- Container was showing UNHEALTHY despite engine running fine

### PR12 — Snapshot I/O Async Fix — MERGED (PR#65, 2026-04-09)
- Fixed save_snapshot() blocking I/O — 30-55s ScanLat spikes every 5 min
- Wrapped np.savez_compressed() in loop.run_in_executor(None, self._save_snapshot_sync)
- ScanLat confirmed stable at 3,400-4,000ms post-merge

### PR13 — Heartbeat YAML Fix — MERGED (PR#66, 2026-04-09)
- Base64-encoded heartbeat Python block to resolve YAML syntax error in vps-monitor.yml

### PR14-hotfix — trade_monitor TypeError on signal close — MERGED (PR#70, 2026-04-09)
- TypeError in `_post_signal_closed`: `float - datetime` at line 978
- Fix: `(utcnow() - sig.timestamp).total_seconds()` — one line, single file
- Telegram signal-closed posts were silently failing on every TP/SL hit

---

## Architecture Correction Sequence Detail (ARCH-1 through ARCH-10)

### PR-ARCH-1 — CANCELLED
- Originally planned: SMC/trend gate exemptions, QUIET_SCALP_BLOCK exemptions
- Cancelled mid-sequence due to agent task confusion
- Fixes were absorbed into subsequent PRs (ARCH-5, ARCH-6)

### PR-ARCH-2 — Winner-Takes-All Removal — MERGED
- ScalpChannel.evaluate() returns List[Signal] instead of Optional[Signal]
- Scanner processes each candidate independently through gate chain
- Same-symbol same-direction dedup enforced
- MAX_CORRELATED_SCALP_SIGNALS=4 cap applied across list

### PR-ARCH-3 — Data Pipeline Wiring — MERGED
- Wire funding_rate (from order_flow_store) into smc_data before channel.evaluate()
- Wire cvd data into smc_data
- Unlocks: _evaluate_funding_extreme, _evaluate_divergence_continuation, _evaluate_liquidation_reversal

### PR-ARCH-4 — Setup Classification Bug Fix — MERGED
- Add LIQUIDITY_SWEEP_REVERSAL and QUIET_COMPRESSION_BREAK to _SELF_CLASSIFYING frozenset
- Correct setup class attribution in all signal output

### PR-ARCH-5 — DIVERGENCE_CONTINUATION QUIET Floor — MERGED (PR#81)
- Added `_QUIET_DIVERGENCE_MIN_CONFIDENCE = 64.0`
- DIVERGENCE_CONTINUATION in QUIET regime exempt from global QUIET_SCALP_MIN_CONFIDENCE=65.0 when confidence >= 64.0
- Backed by live evidence: divergence candidates at 64.3 in logs

### PR-ARCH-6 — SMC Gate Exemption Corrections — MERGED (PR#83)
- Added LIQUIDATION_REVERSAL, FUNDING_EXTREME_SIGNAL, and DIVERGENCE_CONTINUATION to `_SMC_GATE_EXEMPT_SETUPS`

### PR-ARCH-7A — Setup Identity / Classification Repair — MERGED
- Added missing setup classes to SetupClass enum and _SELF_CLASSIFYING frozenset
- Setups added: LIQUIDATION_REVERSAL, TREND_PULLBACK_EMA, WHALE_MOMENTUM, DIVERGENCE_CONTINUATION, SR_FLIP_RETEST

### PR-ARCH-7B — Volatile Compatibility Fix — MERGED
- Added LIQUIDATION_REVERSAL to the volatile-compatible setup mapping
- Resolved structural suppression in VOLATILE_UNSUITABLE market state

### PR-ARCH-7C — _SCALP_CHANNELS Cleanup — MERGED
- Expanded _SCALP_CHANNELS to include all scalp channels
- Resolved inconsistent gate behaviour caused by 4 of 8 scalp channels being excluded

### PR-ARCH-8 — Scoring Integrity Fix — MERGED
- Moved soft-penalty subtraction to after PR09 final score assignment
- Restored VWAP, kill zone, OI, spoof, volume divergence, and cluster penalties to actual effect on final confidence

### PR-ARCH-9 — Family-Aware TP / Risk-Plan Refinement — MERGED
- Replaced uniform build_risk_plan() overwrite with family-aware TP/SL logic
- Preserved universal hard risk controls (max SL %, min R:R)

### PR-ARCH-10 — Family-Based Confidence Scoring in PR09 — MERGED
- Added order-flow thesis dimension to PR09 for reversal / positioning / divergence families
- Full family-based scoring model complete

---

## Root-Cause Diary (2026-04-09)

### Why 10 of 11 Signal Paths Were Silent — Full Root Cause (Confirmed 2026-04-09)

| Evaluator | Confirmed Blocker |
|---|---|
| _evaluate_standard | None — dominated scored[] (winner-takes-all) |
| _evaluate_trend_pullback | Regime was QUIET not TRENDING |
| _evaluate_liquidation_reversal | cvd never populated in smc_data |
| _evaluate_whale_momentum | whale_alert / volume_delta_spike never in smc_data |
| _evaluate_volume_surge_breakout | Loses winner-takes-all to _evaluate_standard |
| _evaluate_breakdown_short | Loses winner-takes-all to _evaluate_standard |
| _evaluate_opening_range_breakout | SMC hard gate blocks it + wrong session hours |
| _evaluate_sr_flip_retest | SMC hard gate blocks it + winner-takes-all |
| _evaluate_funding_extreme | funding_rate never written into smc_data |
| _evaluate_quiet_compression_break | QUIET_SCALP_BLOCK self-defeating loop |
| _evaluate_divergence_continuation | cvd never in smc_data + regime QUIET |

**Root Cause 1 — QUIET_SCALP_BLOCK self-defeating loop**
QUIET_COMPRESSION_BREAK is the ONLY evaluator built for QUIET markets. It generates a signal. That signal then hits QUIET_SCALP_BLOCK and is rejected. The gate blocked the one method designed for the condition it was protecting. Fixed by exempting QUIET_COMPRESSION_BREAK from QUIET_SCALP_BLOCK.

**Root Cause 2 — SMC Hard Gate applied uniformly to all 11 paths**
SMC_HARD_GATE_MIN = 12.0 is correct for sweep-based paths. OPENING_RANGE_BREAKOUT, QUIET_COMPRESSION_BREAK, VOLUME_SURGE_BREAKOUT, BREAKDOWN_SHORT, SR_FLIP_RETEST are all structurally valid without a sweep score >= 12. Fixed by family-aware gate exemptions.

**Root Cause 3 — Data dependencies never populated in smc_data**
funding_rate and cvd both existed in order_flow_store but were never written into smc_data before ScalpChannel.evaluate() was called. Three evaluators permanently blocked. Fixed by ARCH-3 data pipeline wiring.

**Root Cause 4 — Winner-takes-all scored[] architecture**
ScalpChannel.evaluate() returned only ONE signal — the highest regime-adjusted R-multiple. _evaluate_standard produced a candidate every cycle. All other valid evaluators were silently discarded. Fixed by ARCH-2 List[Signal] return.

**Root Cause 5 — Trend hard gate applied uniformly**
TREND_HARD_GATE_MIN = 10.0 applied to LIQUIDATION_REVERSAL, FUNDING_EXTREME, WHALE_MOMENTUM — all of which do not use EMA alignment as their thesis. Fixed by trend gate exemptions.

**Root Cause 6 — Spread blocking (correct protective behaviour)**
40-44 of 75 pairs spread-blocked every cycle in Extreme Fear market. This is correct. Self-resolves when market conditions normalise.

**Root Cause 7 — Setup Classification Bug**
classify_setup() misclassified LIQUIDITY_SWEEP_REVERSAL and QUIET_COMPRESSION_BREAK signals as RANGE_FADE. Fixed by adding both to _SELF_CLASSIFYING frozenset (ARCH-4).

### Confidence Architecture Audit (2026-04-09)

Critical confirmed mismatches before ARCH-8/10:
- Soft-gate penalties overwritten — VWAP, kill zone, OI, spoof, volume divergence, cluster penalties all accumulated then discarded at PR09 final score
- LIQUIDATION_REVERSAL missing from _SMC_GATE_EXEMPT_SETUPS — hard-blocked despite passing its evaluator
- FUNDING_EXTREME_SIGNAL same problem
- EMA scoring penalizing reversal paths — reversal signals structurally penalised by EMA alignment scoring
- Order-flow thesis absent from final score — CVD, OI, liquidation flow, funding rate all excluded from 6-dimension scoring despite being the primary thesis for reversal/positioning families

All corrected by ARCH-8 (scoring integrity) and ARCH-10 (family-based scoring).

---

## Prior Session History (Summary)

**Sessions 1–6 (2026-04-06 to 2026-04-08):**
Built core system: signal quality overhaul, engagement layer, scan latency fix, user interaction layer, signal safety, dead channel removal, signal architecture overhaul (range_fade removal, trend pullback added, liquidation reversal added), volume surge breakout, breakdown short, dynamic pair discovery.

**Session 7 (2026-04-09):**
Full 11-evaluator pipeline audit. Identified all 6 root causes for silent paths. Launched architecture fix sequence (ARCH-1 through ARCH-10 plan). Completed ARCH-5 (divergence quiet floor), ARCH-6 (SMC exemptions). Completed confidence architecture audit. Fixed PR12 snapshot blocking I/O. Fixed PR13 heartbeat YAML. Fixed PR14 TypeError in signal close.

**Session 8 (2026-04-09, continued):**
Completed repository-wide architecture audit covering all four subsystems: signal paths, confidence scoring, gates, SL/TP design. Confirmed hybrid model as the correct target architecture. Defined full ARCH-7A through ARCH-10 implementation sequence.

**Post-session (2026-04-10):**
ARCH-7A through ARCH-10 all merged. Architecture correction sequence complete. All 11 evaluators architecturally unblocked. Fresh canonical brief created to replace rolling diary format.
