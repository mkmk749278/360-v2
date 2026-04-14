# Signal Path Expression Lifecycle Research Report

**Model/Agent Identifier:** `claude-sonnet-4` (GitHub Copilot Coding Agent, running Claude Sonnet 4 model)
**Identifier precision:** Best-available — the exact model version string exposed to the agent runtime is `claude-sonnet-4`.
**Date:** 2026-04-14
**Repository:** `mkmk749278/360-v2`

---

## Executive Summary

This report is a repo-wide investigation of the signal-path expression lifecycle in the 360-v2 trading signal engine. The core finding is that **the narrow persisted path diversity observed in live `signal_performance.json` is primarily structural, not accidental**:

1. **Only 1 of 8 channel evaluators is enabled by default** (`360_SCALP`). The other 7 (FVG, CVD, VWAP, Divergence, Supertrend, Ichimoku, Orderblock) default to `false`.
2. Within `360_SCALP`, 14 evaluator paths exist, but a **cascading chain of 42+ gates** compresses live expression to a narrow subset dominated by paths with the widest regime compatibility and fewest hard penalties.
3. **WATCHLIST signals (50-64 confidence) are intentionally non-persisted** — they route to free channel only, never enter `_active_signals`, never reach `TradeMonitor`, and never call `record_outcome()`.
4. **B-tier signals (65-79) are in a dead zone** — they pass the scanner's 65 min_confidence but fail the `classify_signal_tier` A+ threshold (≥80), resulting in fewer emission opportunities than the configuration suggests.
5. Paths that are CORE portfolio role, wide-regime compatible, and exempt from both SMC and trend hard gates have the highest expression probability. In practice, this favors: `SR_FLIP_RETEST`, `LIQUIDITY_SWEEP_REVERSAL`, `CONTINUATION_LIQUIDITY_SWEEP`, `TREND_PULLBACK_EMA`, and to a lesser extent `VOLUME_SURGE_BREAKOUT` and `BREAKDOWN_SHORT`.

The report separates **confirmed code facts** (marked ✅) from **realistic operational inferences** (marked 🔮).

---

## Table of Contents

1. [Path/Setup Inventory](#1-pathsetup-inventory)
2. [End-to-End Lifecycle Map](#2-end-to-end-lifecycle-map)
3. [Drop-off / Suppression Map](#3-drop-off--suppression-map)
4. [Realistic Operational Interpretation](#4-realistic-operational-interpretation)
5. [Why Persisted History Shows Only a Subset of Paths](#5-why-persisted-history-shows-only-a-subset-of-paths)
6. [Best Instrumentation Points for Path-Expression Monitor](#6-best-instrumentation-points-for-path-expression-monitor)
7. [Most Important Findings / Recommendations](#7-most-important-findings--recommendations)

---

## 1. Path/Setup Inventory

### 1.1 SetupClass Enum (25 members)
✅ **File:** `src/signal_quality.py:18-45`

| # | SetupClass | Portfolio Role | Category |
|---|-----------|---------------|----------|
| 1 | `TREND_PULLBACK_CONTINUATION` | — (legacy/non-active) | Trend |
| 2 | `TREND_PULLBACK_EMA` | CORE | Trend |
| 3 | `BREAKOUT_RETEST` | — (legacy/non-active) | Breakout |
| 4 | `LIQUIDITY_SWEEP_REVERSAL` | CORE | Reversal |
| 5 | `LIQUIDATION_REVERSAL` | SUPPORT | Reversal |
| 6 | `MOMENTUM_EXPANSION` | — (legacy/non-active) | Momentum |
| 7 | `VOLUME_SURGE_BREAKOUT` | CORE | Breakout |
| 8 | `BREAKDOWN_SHORT` | CORE | Short |
| 9 | `OPENING_RANGE_BREAKOUT` | SUPPORT | Breakout |
| 10 | `SR_FLIP_RETEST` | CORE | Structural |
| 11 | `FUNDING_EXTREME_SIGNAL` | SPECIALIST | Funding |
| 12 | `QUIET_COMPRESSION_BREAK` | SPECIALIST | Compression |
| 13 | `DIVERGENCE_CONTINUATION` | SUPPORT | Divergence |
| 14 | `CONTINUATION_LIQUIDITY_SWEEP` | CORE | Liquidity |
| 15 | `POST_DISPLACEMENT_CONTINUATION` | CORE | Displacement |
| 16 | `FAILED_AUCTION_RECLAIM` | SUPPORT | Auction |
| 17 | `RANGE_REJECTION` | — (auxiliary) | Range |
| 18 | `EXHAUSTION_FADE` | — (auxiliary) | Fade |
| 19 | `RANGE_FADE` | — (auxiliary) | Range |
| 20 | `WHALE_MOMENTUM` | SPECIALIST | Momentum |
| 21 | `MULTI_STRATEGY_CONFLUENCE` | — (auxiliary) | Confluence |
| 22 | `FVG_RETEST` | — (PR-01 auxiliary) | FVG |
| 23 | `FVG_RETEST_HTF_CONFLUENCE` | — (PR-01 auxiliary) | FVG |
| 24 | `RSI_MACD_DIVERGENCE` | — (PR-01 auxiliary) | Divergence |
| 25 | `SMC_ORDERBLOCK` | — (PR-01 auxiliary) | Orderblock |

### 1.2 Active Evaluator Paths (14 in scalp.py)
✅ **File:** `src/channels/scalp.py` — Each has a dedicated evaluator function:

| # | Evaluator Path | Line | Regime Blocks | Hard Boosts |
|---|---------------|------|---------------|-------------|
| 1 | `LIQUIDITY_SWEEP_REVERSAL` | 568 | None specific | — |
| 2 | `TREND_PULLBACK_EMA` | 744 | — | — |
| 3 | `LIQUIDATION_REVERSAL` | 895 | — | +10 boost |
| 4 | `WHALE_MOMENTUM` | 1097 | — | — |
| 5 | `VOLUME_SURGE_BREAKOUT` | 1316 | — | +8 boost |
| 6 | `BREAKDOWN_SHORT` | 1537 | — | +8 boost |
| 7 | `OPENING_RANGE_BREAKOUT` | 1709 | — | +5 boost |
| 8 | `SR_FLIP_RETEST` | 1968 | VOLATILE only | — |
| 9 | `FUNDING_EXTREME_SIGNAL` | 2142 | — | — |
| 10 | `QUIET_COMPRESSION_BREAK` | 2294 | — | — |
| 11 | `DIVERGENCE_CONTINUATION` | 2508 | — | — |
| 12 | `CONTINUATION_LIQUIDITY_SWEEP` | 2759 | — | — |
| 13 | `POST_DISPLACEMENT_CONTINUATION` | 3083 | — | — |
| 14 | `FAILED_AUCTION_RECLAIM` | 3387 | — | — |

### 1.3 Channel Families (8 channels, only 1 enabled by default)
✅ **File:** `config/__init__.py:569-730`

| Channel | Default Enabled | min_confidence | Evaluator File |
|---------|----------------|----------------|----------------|
| `360_SCALP` | **true** | 65 | `channels/scalp.py` |
| `360_SCALP_FVG` | false | 78 | `channels/scalp_fvg.py` |
| `360_SCALP_CVD` | false | 75 | `channels/scalp_cvd.py` |
| `360_SCALP_VWAP` | false | 75 | `channels/scalp_vwap.py` |
| `360_SCALP_DIVERGENCE` | false | 76 | `channels/scalp_divergence.py` |
| `360_SCALP_SUPERTREND` | false | 75 | `channels/scalp_supertrend.py` |
| `360_SCALP_ICHIMOKU` | false | 75 | `channels/scalp_ichimoku.py` |
| `360_SCALP_ORDERBLOCK` | false | 78 | `channels/scalp_orderblock.py` |

### 1.4 Portfolio Roles
✅ **File:** `src/signal_quality.py:75-106`

- **CORE** (7 paths): LIQUIDITY_SWEEP_REVERSAL, TREND_PULLBACK_EMA, VOLUME_SURGE_BREAKOUT, BREAKDOWN_SHORT, SR_FLIP_RETEST, CONTINUATION_LIQUIDITY_SWEEP, POST_DISPLACEMENT_CONTINUATION
- **SUPPORT** (4 paths): LIQUIDATION_REVERSAL, DIVERGENCE_CONTINUATION, OPENING_RANGE_BREAKOUT, FAILED_AUCTION_RECLAIM
- **SPECIALIST** (3 paths): WHALE_MOMENTUM, FUNDING_EXTREME_SIGNAL, QUIET_COMPRESSION_BREAK
- **Auxiliary** (4 paths, intentionally absent): FVG_RETEST, FVG_RETEST_HTF_CONFLUENCE, RSI_MACD_DIVERGENCE, SMC_ORDERBLOCK

### 1.5 Auxiliary Systems (Not Full Channels)

- **Radar**: Integrated in `main.py:403` (`_handle_radar_candidate()`), `formatter.py:169` (`format_radar_alert()`). Free-channel alert handler, not a separate evaluator. `RADAR_CHANNEL_ENABLED` defaults `true`. No `src/radar_channel.py` file exists. ✅
- **Free Watch Service**: `src/free_watch_service.py` — condensed free-channel picks. ✅
- **360_GEM**: Not a trading channel. Only referenced for historical data seeding timeframes (`GEM_SEED_DAILY_CANDLES`, `GEM_SEED_WEEKLY_CANDLES`). ✅

---

## 2. End-to-End Lifecycle Map

### Phase 1: Detection (Scanner)
✅ **File:** `src/scanner/__init__.py`

```
scan_loop() [842-900]
  ├─ for each symbol in pair universe:
  │   └─ _scan_symbol_bounded() → _scan_symbol() [2974-3246]
  │       ├─ _build_scan_context() — aggregates candles, indicators, SMC, regime
  │       ├─ for each channel in self.channels:
  │       │   ├─ check _CHANNEL_ENABLED_FLAGS → skip if disabled [2994]
  │       │   ├─ _should_skip_channel() — 10+ hard gates [1662-1790]
  │       │   └─ channel.evaluate() → List[Signal] [3045]
  │       ├─ Scalp arbitration: per-direction best-of-N [3064-3117]
  │       └─ Winners → _prepare_signal() [2072-2820]
  └─ cleanup_expired() per cycle
```

### Phase 2: Preparation & Gating (Scanner)
✅ **File:** `src/scanner/__init__.py:2072-2968`

```
_prepare_signal()
  ├─ Failed-detection cooldown check [2085-2094]
  ├─ Setup/regime compatibility validation [2120-2128]
  ├─ 8 sequential gate checks:
  │   ├─ MTF Confluence (hard gate) [2147-2196]
  │   ├─ VWAP Extension (soft penalty) [2197-2241]
  │   ├─ Kill Zone (soft penalty) [2246-2288]
  │   ├─ OI Filter (soft penalty) [2291-2298]
  │   ├─ Funding Rate (±boost/penalty) [2299-2313]
  │   ├─ Cross-Asset (hard gate) [2316-2351]
  │   ├─ Spoofing Detection (soft penalty) [2354-2371]
  │   └─ Volume Divergence (soft penalty) [2374-2397]
  ├─ Cluster Suppression (soft penalty) [2399-2412]
  ├─ Risk Assessment (hard gate) [2414-2417]
  ├─ Correlated Exposure Cap (hard gate) [2423-2435]
  ├─ Signal Quality Scoring [2625-2750]
  │   ├─ build_risk_plan() → SL/TP/sizing
  │   ├─ Apply soft_penalty_total → confidence deduction [2734-2742]
  │   └─ classify_signal_tier() [2745]
  ├─ SMC Hard Gate (smc_score < 12.0) [2825-2852]
  ├─ Trend Hard Gate (indicator_score < 10.0) [2854-2881]
  ├─ Stat Filter (rolling win-rate) [2747-2774]
  ├─ Pair Analysis Quality (CRITICAL/WEAK) [2776-2815]
  ├─ QUIET Regime Scalp Floor (conf < 65.0) [2906-2941]
  ├─ Component floors (market<12, execution<10, risk<10) [2955-2959]
  └─ Final min_confidence check [2955-2968]
      ├─ WATCHLIST (50-64): kept, routes to free only [2942-2954]
      ├─ FILTERED (<50): dropped [2968]
      └─ B+ (≥65): enqueued to signal_queue
```

### Phase 3: Routing (Signal Router)
✅ **File:** `src/signal_router.py:482-769`

```
_process(signal)
  ├─ WATCHLIST → _route_watchlist_to_free() → return [483-489]
  │   (no _active_signals, no lifecycle, no persistence)
  ├─ Position Lock check [491-499]
  ├─ Per-channel Cooldown [501-513]
  ├─ Per-channel Concurrent Cap [515-526]
  ├─ Correlation Limit [528-543]
  ├─ TP/SL Sanity [545-577]
  ├─ Stale Signal Detection (120s SCALP, 3600s others) [578-627]
  ├─ AI Enrichment (optional) [629-630]
  ├─ Min-Confidence Filter (per-channel) [632-642]
  ├─ Risk Assessment [644-656]
  └─ PASS → Emit:
      ├─ Format + publish to Telegram [670-730]
      ├─ Register in _active_signals [740-741]
      ├─ Lock position [742]
      ├─ Schedule Redis persist [743]
      ├─ Track for daily free pick [746]
      └─ _maybe_publish_free_signal() [751]
```

### Phase 4: Trade Monitoring
✅ **File:** `src/trade_monitor.py:351-897`

```
start() → polling loop
  ├─ for each signal in _active_signals:
  │   └─ _evaluate_signal(sig)
  │       ├─ MAX HOLD expiry → EXPIRED + record_outcome [554-560]
  │       ├─ Invalid SL → CANCELLED + _remove (NO record_outcome!) [594-611]
  │       ├─ SL hit → SL_HIT + record_outcome [634-651]
  │       ├─ Invalidation → INVALIDATED + record_outcome [657-673]
  │       ├─ TP1 hit → partial close + record_outcome [677-695]
  │       ├─ TP2 hit → partial close + record_outcome
  │       ├─ TP3 hit → full close + record_outcome [737-755]
  │       └─ Trailing stop update [51-100]
  └─ Pulse updates every ~30s [343-440]
```

### Phase 5: Persistence
✅ **File:** `src/performance_tracker.py:92-157`

```
record_outcome(signal_id, channel, symbol, direction, entry,
               hit_tp, hit_sl, pnl_pct, outcome_label, confidence,
               pre_ai_confidence, post_ai_confidence,
               setup_class, market_phase, quality_tier,
               spread_pct, volume_24h_usd, hold_duration_sec,
               max_favorable_excursion_pct, max_adverse_excursion_pct,
               signal_quality_pnl_pct, signal_quality_hit_tp, session_name)
  ├─ Creates SignalRecord (dataclass)
  ├─ Appends to self._records
  ├─ Calls self._save() → writes data/signal_performance.json
  └─ Log: "Recorded outcome for {}: pnl={:.2f}%% hit_sl={}" (DEBUG)
```

### Phase 6: Router State Persistence
✅ **File:** `src/signal_router.py:250-323`

- Active signals persisted to **Redis** (`signal_router:active_signals`), not disk
- Restored from Redis on restart via `restore()`
- If Redis unavailable, state is lost on restart

---

## 3. Drop-off / Suppression Map

### 3.1 Complete Gate Chain (42+ checkpoints)

| # | Stage | Gate | File:Line | Type | Likely Impact |
|---|-------|------|-----------|------|--------------|
| 1 | Pre-filter | Symbol blacklist | scanner:1351 | Hard | <1% |
| 2 | Pre-filter | Volume floor | scanner:1357 | Hard | 5-10% |
| 3 | Pre-filter | All channels active | scanner:1365 | Hard | 2-5% |
| 4 | Pre-filter | All channels cooldown | scanner:1371 | Hard | 1-3% |
| 5 | Channel-skip | Tier2 scalp exclusion | scanner:1666 | Hard | 2-5% |
| 6 | Channel-skip | Pair quality gate | scanner:1674 | Hard | 10-20% |
| 7 | Channel-skip | Volatile/unsuitable | scanner:1724 | Hard | 2-10% |
| 8 | Channel-skip | Paused channel | scanner:1738 | Hard | Admin-only |
| 9 | Channel-skip | Cooldown active | scanner:1741 | Hard | 5-15% |
| 10 | Channel-skip | Circuit breaker | scanner:1747 | Hard | 0-5% |
| 11 | Channel-skip | Active signal exists | scanner:1753 | Hard | 3-10% |
| 12 | Channel-skip | Ranging low ADX (<15) | scanner:1760 | Hard | 2-8% |
| 13 | Channel-skip | Regime incompatibility | scanner:1772 | Hard | <1% |
| 14 | Prepare | Failed-detection cooldown | scanner:2089 | Hard | 1-2% |
| 15 | Prepare | Setup incompatibility | scanner:2121 | Hard | 1-5% |
| 16 | Prepare | Execution quality fail | scanner:2125 | Hard | 2-5% |
| 17 | Prepare | MTF hard gate | scanner:2147 | Hard | 5-15% |
| 18 | Prepare | Cross-asset conflict | scanner:2333 | Hard | 1-5% |
| 19 | Prepare | Risk assessment | scanner:2414 | Hard | 1-3% |
| 20 | Prepare | Correlated exposure cap | scanner:2423 | Hard | 2-8% |
| 21 | Prepare | VWAP extension | scanner:2206 | Soft | -15 pts max |
| 22 | Prepare | Kill zone/session | scanner:2232 | Soft | -10 pts max |
| 23 | Prepare | OI + Funding rate | scanner:2247 | Soft | -15 pts max |
| 24 | Prepare | Spoofing/layering | scanner:2353 | Soft | -12 pts max |
| 25 | Prepare | Volume divergence | scanner:2373 | Soft | -12 pts max |
| 26 | Prepare | Cluster suppression | scanner:2399 | Soft | -10 pts max |
| 27 | Prepare | Funding rate penalty | scanner:2289 | Soft | ±5-8 pts |
| 28 | Scoring | SMC hard gate (<12.0) | scanner:2825 | Hard | 10-20% |
| 29 | Scoring | Trend hard gate (<10.0) | scanner:2854 | Hard | 5-15% |
| 30 | Scoring | Stat filter suppress | scanner:2756 | Hard | 2-8% |
| 31 | Scoring | Pair analysis CRITICAL | scanner:2786 | Hard | 1-5% |
| 32 | Scoring | Pair analysis WEAK | scanner:2802 | Soft | -8 pts |
| 33 | Scoring | QUIET regime floor (65.0) | scanner:2906 | Hard | 10-30% in QUIET |
| 34 | Scoring | Component floors | scanner:2957 | Hard | 5-10% |
| 35 | Scoring | min_confidence (65 for SCALP) | scanner:2956 | Hard | 5-15% |
| 36 | Router | WATCHLIST → free only | router:487 | Reroute | Non-persisted |
| 37 | Router | Position lock | router:491 | Hard | 3-10% |
| 38 | Router | Per-channel cooldown | router:501 | Hard | 1-5% |
| 39 | Router | Concurrent cap | router:515 | Hard | 5-15% |
| 40 | Router | Correlation limit | router:528 | Hard | 2-8% |
| 41 | Router | TP/SL sanity | router:545 | Hard | 0-1% |
| 42 | Router | Stale signal (120s) | router:578 | Hard | 5-20% |
| 43 | Router | Min-confidence (router) | router:632 | Hard | 2-5% |
| 44 | Router | Risk assessment | router:644 | Hard | 1-3% |

### 3.2 Trade Monitor Exit Paths

| Exit | Status | record_outcome? | Persistence Gap? |
|------|--------|-----------------|-----------------|
| MAX HOLD expiry | EXPIRED | ✅ Yes | No |
| SL hit (valid) | SL_HIT | ✅ Yes | No |
| Invalidation | INVALIDATED | ✅ Yes | No |
| TP1/TP2/TP3 hit | TPx_HIT | ✅ Yes | No |
| Invalid SL (LONG) | CANCELLED | ❌ **No** | **Yes — persistence blind spot** |
| Invalid SL (SHORT) | CANCELLED | ❌ **No** | **Yes — persistence blind spot** |

### 3.3 Non-Persisted Signal Paths

| Signal Category | What Happens | Persisted? |
|----------------|-------------|-----------|
| WATCHLIST (50-64) | Free channel preview only | ❌ Never |
| FILTERED (<50) | Dropped at scanner | ❌ Never |
| Router-rejected | Various hard gates | ❌ Never |
| CANCELLED (invalid SL) | Removed from monitor without outcome | ❌ **Bug/gap** |
| Router-expired (cleanup_expired) | Removed from _active_signals | ❌ **Gap** — router cleanup does NOT call record_outcome; only TradeMonitor expiry does |

---

## 4. Realistic Operational Interpretation

### 4.1 Which paths are likely expressing in practice?

🔮 **High expression probability (CORE, wide regime, gate-exempt):**
- **SR_FLIP_RETEST** — Widest regime compatibility (blocks only VOLATILE), CORE role, SMC-exempt, trend-exempt. However, has up to 20pts soft penalties that push many candidates into WATCHLIST zone.
- **LIQUIDITY_SWEEP_REVERSAL** — CORE, no regime restrictions, strong structural signal.
- **CONTINUATION_LIQUIDITY_SWEEP** — CORE, wide regime, structural.
- **TREND_PULLBACK_EMA** — CORE, SMC-exempt, structural SL/TP protected.

🔮 **Moderate expression probability:**
- **VOLUME_SURGE_BREAKOUT** — CORE, +8 boost, SMC-exempt. But requires genuine volume surge conditions.
- **BREAKDOWN_SHORT** — CORE, +8 boost, SMC-exempt. Requires clear short setup.
- **DIVERGENCE_CONTINUATION** — SUPPORT, structural SL/TP protected. Requires divergence conditions.

🔮 **Low expression probability (narrow context, specialist):**
- **OPENING_RANGE_BREAKOUT** — SUPPORT, only +5 boost, requires opening range session.
- **LIQUIDATION_REVERSAL** — SUPPORT, +10 boost, but requires liquidation cascade detection.
- **WHALE_MOMENTUM** — SPECIALIST, requires whale activity detection.
- **FUNDING_EXTREME_SIGNAL** — SPECIALIST, requires extreme funding rate conditions.
- **QUIET_COMPRESSION_BREAK** — SPECIALIST, requires QUIET regime + compression breakout.
- **FAILED_AUCTION_RECLAIM** — SUPPORT, requires auction failure conditions.
- **POST_DISPLACEMENT_CONTINUATION** — CORE role but requires displacement event.

### 4.2 Which suppressors likely dominate live behavior?

🔮 **Top-5 most impactful suppressors in practice:**

1. **Only 360_SCALP enabled** — This is the #1 filter. 7 of 8 channels are disabled by default. All signal diversity must come from the 14 evaluators within `scalp.py`. ✅ Confirmed by code.

2. **Soft penalty accumulation → WATCHLIST zone** — Soft penalties (VWAP: 15, kill zone: 10, OI: 8, volume div: 12, cluster: 10, spoof: 12) can easily deduct 20-40 points from an 85-point candidate, pushing it into the 50-64 WATCHLIST zone. WATCHLIST signals are not persisted. 🔮 Very likely the dominant live suppressor.

3. **SMC hard gate** (smc_score < 12.0) — Non-exempt paths must pass this. Only 12 of 14 paths are SMC-exempt. `LIQUIDITY_SWEEP_REVERSAL` and `CONTINUATION_LIQUIDITY_SWEEP` are the 2 non-exempt CORE paths; if their SMC scores are marginal, this gate kills them. ✅ Confirmed by code.

4. **QUIET regime floor** (65.0 for SCALP) + **SCALP QUIET penalty multiplier** (1.8x) — During quiet markets, soft penalties are nearly doubled. A 10-point base penalty becomes 18 points. This heavily suppresses signals during low-volatility periods. ✅ Confirmed by code.

5. **Concurrent cap + position lock + cooldown** — These create temporal bottlenecks. Only 5 concurrent SCALP signals allowed, with per-symbol position locks. After a signal fires, the symbol enters cooldown. During busy periods, this severely limits throughput. ✅ Confirmed by code.

### 4.3 The B-tier dead zone

✅ **Confirmed code fact:** `classify_signal_tier` returns:
- A+ (sniper): ≥80
- B (setup): 65-79
- WATCHLIST: 50-64
- FILTERED: <50

✅ **Confirmed code fact:** Scanner min_confidence for 360_SCALP is 65.

🔮 **Operational inference:** B-tier signals (65-79) pass the scanner but enter the router without the "A+" tier advantage. They still face the full router gate chain. The router's own min_confidence check is per-channel from `ALL_CHANNELS` config, so they may pass. But the overall confidence band 65-79 represents signals that survived gating but with accumulated penalties. These are the "marginal" signals — they fire and can persist, but they represent weaker setups that may have lower win rates.

### 4.4 The WATCHLIST routing paradox

✅ **Confirmed code fact:** WATCHLIST signals (50-64) in the scanner are kept and routed to the free channel.

✅ **Confirmed code fact:** In the signal router, WATCHLIST signals call `_route_watchlist_to_free()` and immediately return — no lifecycle tracking, no persistence.

🔮 **Operational inference:** This means a significant volume of candidates that pass most gates but accumulate moderate soft penalties are being generated, formatted, and posted to the free channel — but leave zero trace in `signal_performance.json`. The free channel may appear active while the paid channel / persisted history appears sparse. This is by design but creates a monitoring blind spot.

### 4.5 Paths that exist mostly on paper

🔮 **Likely paper-only paths:**
- **All 7 disabled channels** (FVG, CVD, VWAP, Divergence, Supertrend, Ichimoku, Orderblock) — Unless env vars override defaults, these never evaluate candidates.
- **RANGE_REJECTION, EXHAUSTION_FADE, RANGE_FADE, MULTI_STRATEGY_CONFLUENCE** — These are in CHANNEL_SETUP_COMPATIBILITY for non-SCALP channels but NOT in ACTIVE_PATH_PORTFOLIO_ROLES. They exist in the SetupClass enum but have no active evaluator in `scalp.py`.
- **FVG_RETEST, FVG_RETEST_HTF_CONFLUENCE, RSI_MACD_DIVERGENCE, SMC_ORDERBLOCK** — Auxiliary identities intentionally absent from ACTIVE_PATH_PORTFOLIO_ROLES. They are sub-evaluator signals within disabled channels.

### 4.6 Pipeline bottleneck analysis

🔮 **The pipeline narrows dramatically at three points:**

```
                                    ┌─ All 8 channels
                                    │  (25 SetupClass values)
                                    │  = theoretical maximum
                                    ▼
Channel enable flags ──────────────→  Only 360_SCALP active
                                    │  (14 evaluator paths)
                                    ▼
Soft penalty accumulation ─────────→  Many pushed to WATCHLIST
                                    │  (free-channel only, not persisted)
                                    ▼
SMC + Trend hard gates ────────────→  Some paths killed outright
                                    │
                                    ▼
Concurrent cap + cooldowns ────────→  Temporal throttling
                                    │  (max 5 concurrent SCALP)
                                    ▼
                                    ~3-7 paths regularly persisting
```

---

## 5. Why Persisted History Shows Only a Subset of Paths

### Root causes (ordered by impact):

| # | Cause | Type | Impact |
|---|-------|------|--------|
| 1 | **7 of 8 channels disabled by default** | ✅ Confirmed | Eliminates all non-SCALP path diversity |
| 2 | **WATCHLIST signals never persisted** | ✅ Confirmed | Soft-penalty victims leave no trace |
| 3 | **Soft penalty accumulation dominates** | 🔮 Inferred | 20-40pt deductions common, pushing B→WATCHLIST |
| 4 | **SPECIALIST paths fire rarely** | 🔮 Inferred | Require narrow market conditions |
| 5 | **Concurrent cap limits throughput** | ✅ Confirmed | Max 5 concurrent, with position locks |
| 6 | **CANCELLED signals not persisted** | ✅ Confirmed | Invalid-SL exits skip record_outcome() |
| 7 | **Router cleanup_expired skips persistence** | ✅ Confirmed | Router expiry ≠ TradeMonitor expiry path |
| 8 | **No naming mismatch** | ✅ Confirmed | setup_class stored as string matches SetupClass enum names |

### Is this genuine selectivity or a blind spot?

🔮 **Assessment: It's primarily genuine selectivity with minor blind spots.**

The narrow persisted diversity is mostly structural:
- Only one channel is active → 14 paths maximum
- Of those 14, ~7 are CORE, ~4 SUPPORT, ~3 SPECIALIST
- SPECIALIST paths require rare conditions → maybe 1-2 fire per day
- Soft penalties are aggressive → many candidates become WATCHLIST → not persisted
- This leaves ~5-8 paths that regularly survive the full pipeline

The **minor blind spots** are:
- CANCELLED signal non-persistence (trade_monitor.py:594-611)
- Router cleanup_expired non-persistence (signal_router.py:1168-1205)
- WATCHLIST volume invisible (no logging of how many WATCHLIST candidates are generated)

---

## 6. Best Instrumentation Points for Path-Expression Monitor

### 6.1 Recommended Monitor Hooks

| Hook | File:Component | Log/Persist | What It Proves | Reliability | Production vs Upstream |
|------|---------------|-------------|----------------|-------------|----------------------|
| **Candidate reached scoring** | scanner:2625 `classify_signal_tier()` | Log (DEBUG) | Path generated a candidate that survived all pre-scoring gates | High | Upstream (pre-emission) |
| **SOFT_PENALTY log** | scanner:2206+ | Log (INFO) | Which soft penalties are firing, regime multiplier, cumulative total | High | Upstream |
| **Scalp arbitration** | scanner:3094-3112 | Log (DEBUG) | Which candidates win/lose per-direction arbitration | High | Upstream |
| **WATCHLIST routed** | router:913 `"WATCHLIST preview → free channel"` | Log (INFO) | Path generated candidate but lost to soft penalties | High | Upstream (non-persisted) |
| **Signal posted** | router:718 `"Signal posted → {} \| {} {}"` | Log (INFO) | Signal actually emitted to paid channel | Very High | **Production expression** |
| **Recorded outcome** | perf_tracker:152 `"Recorded outcome for {}"` | Log (DEBUG) + JSON persist | Signal completed full lifecycle with terminal event | Very High | **Production persistence** |
| **Suppression telemetry** | suppression_telemetry.py | In-memory (4h rolling) | Aggregated suppression reasons/channels/symbols | Medium (volatile) | Upstream |
| **stat_filter suppressed** | scanner:2756 `"stat_filter suppressed"` | Log (INFO) | Rolling win-rate gate killed a path | High | Upstream |
| **pair_analysis suppressed** | scanner:2786 `"pair_analysis suppressed"` | Log (INFO) | Pair quality killed a path | High | Upstream |
| **SMC hard gate** | scanner:2825 `"SMC hard gate"` | Log (DEBUG) | SMC scoring insufficient | High | Upstream |
| **Trend hard gate** | scanner:2854 `"Trend hard gate"` | Log (DEBUG) | Trend scoring insufficient | High | Upstream |
| **Circuit breaker** | scanner:1747, circuit_breaker.py | Log (INFO) | Per-symbol or global circuit breaker tripped | High | System health |
| **QUIET scalp block** | scanner:2906 `"QUIET_SCALP_BLOCK"` | Log (INFO) | Quiet regime floor killed candidate | High | Upstream |
| **Router stale** | router:585 `"STALE signal"` | Log (INFO) | Latency caused signal to be discarded | High | System health |
| **CANCELLED (no record)** | trade_monitor:599,608 | Log (WARNING) | Invalid SL config caused persistence blind spot | High | **Persistence gap indicator** |

### 6.2 Proposed "Path Expression Audit" Section Structure

```
📊 PATH EXPRESSION AUDIT (last 24h)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Active channels: 360_SCALP (1/8 enabled)
Evaluator paths available: 14

UPSTREAM (candidates generated):
  SR_FLIP_RETEST:              47 candidates → 12 scored → 3 emitted
  LIQUIDITY_SWEEP_REVERSAL:    31 candidates → 8 scored → 2 emitted
  TREND_PULLBACK_EMA:          28 candidates → 9 scored → 2 emitted
  CONTINUATION_LIQUIDITY_SWEEP: 19 candidates → 5 scored → 1 emitted
  VOLUME_SURGE_BREAKOUT:       14 candidates → 3 scored → 1 emitted
  BREAKDOWN_SHORT:             11 candidates → 2 scored → 0 emitted
  [... remaining paths with 0 candidates ...]

DOWNSTREAM (persisted outcomes):
  SR_FLIP_RETEST:              2 (TP1: 1, SL: 1)
  LIQUIDITY_SWEEP_REVERSAL:    1 (TP2: 1)
  TREND_PULLBACK_EMA:          2 (TP1: 1, EXPIRED: 1)

SUPPRESSION BREAKDOWN:
  Soft penalty → WATCHLIST:    67 (42% of all candidates)
  SMC hard gate:               23 (15%)
  Stat filter:                  8 (5%)
  Pair analysis CRITICAL:       4 (3%)
  Concurrent cap:              11 (7%)
  Stale signal:                 6 (4%)

PERSISTENCE GAPS:
  CANCELLED (no record):        0
  Router cleanup (no record):   0
  WATCHLIST (free-only):       67
```

### 6.3 Implementation Priority

1. **Highest value:** Count candidates per setup_class at `classify_signal_tier()` (scanner:2625). This reveals upstream path activity before any suppression.
2. **Second highest:** Count WATCHLIST routes per setup_class at `_route_watchlist_to_free()` (router:896). This reveals the soft-penalty suppression volume.
3. **Third:** Parse `suppression_telemetry.summary()` for real-time gate-level breakdown.
4. **Fourth:** Count `"Signal posted"` logs per setup_class for actual production emission rate.
5. **Fifth:** Parse `signal_performance.json` for persisted outcome diversity.

---

## 7. Most Important Findings / Recommendations

### Finding 1: Single-Channel Bottleneck (✅ Confirmed)
Only `360_SCALP` is enabled by default. The other 7 channels have full evaluator implementations but are disabled via env flags defaulting to `"false"`. **This is the primary reason for narrow path diversity.**

**Recommendation:** If path diversity is desired, enable additional channels via env vars. Start with `CHANNEL_SCALP_FVG_ENABLED=true` and `CHANNEL_SCALP_DIVERGENCE_ENABLED=true` as these have the most distinct setup families.

### Finding 2: WATCHLIST Non-Persistence Creates Monitoring Blind Spot (✅ Confirmed)
WATCHLIST signals represent a potentially large volume of candidates that survive most gates but die to soft penalties. They are posted to the free channel but leave no trace in `signal_performance.json`.

**Recommendation:** Add a lightweight WATCHLIST outcome tracker — even if just a counter per setup_class per day — to measure the "soft penalty funnel." This would answer: "How many candidates are being generated but not expressed?"

### Finding 3: CANCELLED Signal Persistence Gap (✅ Confirmed)
`trade_monitor.py:594-611` removes CANCELLED signals (invalid SL) without calling `record_outcome()`. This is a minor persistence blind spot.

**Recommendation:** Add `self._record_outcome(sig, hit_tp=0, hit_sl=False)` before `self._remove()` in the CANCELLED code paths, with outcome_label `"CANCELLED"`.

### Finding 4: Router cleanup_expired vs TradeMonitor Expiry (✅ Confirmed)
`signal_router.py:cleanup_expired()` removes signals from `_active_signals` without calling `record_outcome()`. `trade_monitor.py` has its own MAX_HOLD expiry that DOES call `record_outcome()`. If a signal expires via router cleanup before the trade monitor catches it, the outcome is lost.

**Recommendation:** Verify that the TradeMonitor expiry always fires before the router cleanup for the same signal. If there's a race condition, add record_outcome to router cleanup as a fallback.

### Finding 5: SR_FLIP_RETEST Likely Over-Represents (🔮 Inferred)
SR_FLIP_RETEST has the widest regime compatibility (blocks only VOLATILE), is CORE portfolio role, and is SMC-gate-exempt. However, it has up to 20pts cumulative soft penalties (proximity+3, wick+4, RSI+5, SMC+8) per the scalp evaluator, meaning many of its candidates likely land in the WATCHLIST zone.

**Recommendation:** Monitor SR_FLIP_RETEST upstream candidate count vs emission count to quantify its conversion rate. If it generates 50 candidates but only 3 emit, the soft penalties may need recalibration.

### Finding 6: Soft Penalty Regime Multiplier is Very Aggressive in QUIET (🔮 Inferred)
The SCALP QUIET regime penalty multiplier is 1.8x (vs 0.6x for TRENDING). A 12pt VWAP penalty becomes 21.6pts in QUIET. Combined with other penalties, this can easily push a 90pt candidate below 65.

**Recommendation:** If the system operates frequently in QUIET regime (low-volatility crypto market conditions), this multiplier is likely the dominant live suppressor. Monitor regime distribution alongside signal expression to validate.

### Finding 7: Radar Channel is Partial/Unfinished (✅ Confirmed)
`_radar_scores` is populated in scanner but no runtime caller consumes `_get_scanner_context()`, and no `src/radar_channel.py` exists. Radar alerts use disabled-channel evaluations in a "radar pass" (scanner:3136-3196) for free-channel alerts only.

**Recommendation:** Radar data could serve as a rich path-expression data source if connected to monitoring — it represents what disabled channels *would* produce without actually emitting them.

### Finding 8: No Naming Mismatch Between Internal and Persisted Labels (✅ Confirmed)
`setup_class` is stored as a plain string in `SignalRecord` (performance_tracker.py:44). The value comes directly from the evaluator path name (e.g., `"SR_FLIP_RETEST"`). There is no label transformation or mapping between internal and persisted names.

**Recommendation:** No action needed. Path labels are consistent end-to-end.

---

## Appendix A: Key File Reference

| Component | File | Key Functions/Lines |
|-----------|------|-------------------|
| SetupClass enum | `src/signal_quality.py:18-45` | 25 members |
| Portfolio roles | `src/signal_quality.py:75-106` | ACTIVE_PATH_PORTFOLIO_ROLES |
| Channel config | `config/__init__.py:569-730` | ALL_CHANNELS, enable flags |
| Scanner main loop | `src/scanner/__init__.py:842-900` | scan_loop() |
| Symbol scanning | `src/scanner/__init__.py:2974-3246` | _scan_symbol() |
| Signal preparation | `src/scanner/__init__.py:2072-2968` | _prepare_signal() |
| Tier classification | `src/scanner/__init__.py:383-402` | classify_signal_tier() |
| Scalp arbitration | `src/scanner/__init__.py:3064-3117` | _scalp_dir_best |
| Signal routing | `src/signal_router.py:482-769` | _process() |
| WATCHLIST routing | `src/signal_router.py:893-917` | _route_watchlist_to_free() |
| Free daily pick | `src/signal_router.py:956-1030` | _maybe_publish_free_signal() |
| Trade monitoring | `src/trade_monitor.py:351-897` | _evaluate_signal() |
| Outcome recording | `src/trade_monitor.py:219-348` | _record_outcome() |
| Performance persistence | `src/performance_tracker.py:92-157` | record_outcome() |
| Suppression telemetry | `src/suppression_telemetry.py` | SuppressionTracker |
| Scalp evaluator | `src/channels/scalp.py:317-354` | evaluate() (14 paths) |
| Circuit breaker | `src/circuit_breaker.py` | is_symbol_tripped() |
| Stat filter | `src/stat_filter.py` | check() |
| Cluster suppression | `src/cluster_suppression.py` | cluster penalty |
| Confidence decay | `src/confidence_decay.py` | age-based decay |
| Regime detection | `src/regime.py:23-30` | MarketRegime enum |

## Appendix B: Suppression Telemetry Reason Keys

✅ **File:** `src/suppression_telemetry.py:38-49`

| Reason Key | Description |
|-----------|-------------|
| `REASON_QUIET_REGIME` | Quiet regime gate blocked |
| `REASON_SPREAD_GATE` | Spread too wide |
| `REASON_VOLUME_GATE` | Volume too low |
| `REASON_OI_INVALIDATION` | Open interest issue |
| `REASON_CLUSTER` | Cluster suppression |
| `REASON_STAT_FILTER` | Stat filter gate |
| `REASON_LIFESPAN` | Min lifespan not met |
| `REASON_CONFIDENCE` | Confidence too low (final) |
| `REASON_REGIME_PENALTY` | Regime penalty applied |
| `REASON_PAIR_QUALITY` | Pair quality gate |
| `REASON_RANGING_ADX` | Ranging regime with low ADX |
| `REASON_PAIR_ANALYSIS` | Pair analysis suppression |

## Appendix C: Outcome Labels (Persistence)

✅ **File:** `src/performance_metrics.py:22-43`

| Outcome Label | Condition |
|--------------|-----------|
| `FULL_TP_HIT` | All 3 TPs hit |
| `TP1_HIT` | TP1 reached |
| `TP2_HIT` | TP2 reached |
| `TP3_HIT` | TP3 reached |
| `SL_HIT` | Stop loss hit, negative PnL |
| `BREAKEVEN_EXIT` | SL hit, near-zero PnL (±2%) |
| `PROFIT_LOCKED` | SL hit, positive PnL |
| `CLOSED` | Manual close |
| `EXPIRED` | MAX HOLD exceeded |
| `INVALIDATED` | Regime flip / momentum loss |
| *(missing)* | `CANCELLED` — not persisted (bug) |
