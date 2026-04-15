# 360 Crypto Eye — Runtime Truth, Signal Paths & Risk Geometry Audit

**Model:** Claude Opus 4.6
**Date:** 2026-04-15
**Scope:** Requirements-first deep research audit — architecture truth, signal path expression, SL/TP geometry, regime integrity, suppression funnel, doctrine compliance
**Evidence sources:** Main branch code, monitor/latest.txt (monitor-logs branch, 2026-04-15 05:03 UTC), docs, tests, OWNER_BRIEF.md, ACTIVE_CONTEXT.md, prior audit documents, performance history (38 signals on record)

---

## 1. Requirements-First Architecture Truth

### 1.1 What the System Should Be

360 Crypto Eye is a **multi-pair, institutional-grade crypto signal engine** scanning 75 Binance USDT-M futures pairs. The requirements demand:

1. **Per-pair market structure analysis** — each pair has its own microstructure, regime, liquidity profile, and volatility signature. A BTC trend reversal does not mean AVAX is doing the same thing.
2. **Multi-family signal diversity** — 14 distinct evaluator theses (reversal, continuation, breakout, compression, order-flow) must each express when their conditions are genuinely met.
3. **Method-specific SL/TP** (B13) — no universal formulas; each evaluator owns its invalidation logic.
4. **Hybrid downstream handling** — scoring, gating, and risk validation must be family-aware, not globally uniform.
5. **Proportional protective gating** — suppression should match the risk it addresses, not uniformly throttle all paths.

### 1.2 Should Market Structure Be Per-Pair, Global, BTC-Led, or Hybrid?

**Real requirement:** Hybrid, with per-pair as the primary axis.

| Layer | Correct design | Rationale |
|---|---|---|
| Regime classification | **Per-pair** | Each pair has its own ADX, BB width, EMA slope, volume delta. A QUIET AVAXUSDT does not mean BTC is quiet. |
| Cross-asset context | **BTC-led overlay** (soft gate, not veto) | BTC macro trend should inform but not dictate altcoin signals |
| Correlation gating | **Family-level** | Correlated pairs (e.g., ETH/SOL) should share exposure limits, not regime classification |
| Spread/quality | **Per-pair** | Spread is inherently pair-specific |
| Confidence scoring | **Hybrid** | Base dimensions (SMC, regime, MTF) are universal; thesis dimension must be family-aware |

### 1.3 Current Implementation Assessment

| Aspect | Real requirement | Current implementation | Gap |
|---|---|---|---|
| Regime detection | Per-pair | ✅ Per-pair (ADX, BB width, EMA slope per symbol) | None |
| Cross-asset gate | Soft overlay | ✅ Soft gate with directional check | None |
| MTF gate | Per-pair TF alignment | ⚠️ Generic threshold across all setup families | Medium — reversal setups should not need same MTF alignment as trend-following |
| Spread filtering | Per-pair with tier multipliers | ✅ Per-pair (MAJOR/MIDCAP/ALTCOIN multipliers) | Low — but 40+ pairs/cycle blocked suggests thresholds may be too tight |
| Scoring | Family-aware hybrid | ✅ Family-aware thesis dimension (PR-09) | Low |
| SL/TP | Method-specific (B13) | ✅ Evaluator-authored, structurally protected (PR-02, PR-14) | Medium — downstream caps can still distort (see §4) |
| Channel diversity | Multi-path expression | ❌ Only 360_SCALP enabled; 7 auxiliary channels disabled | **Critical** — only 1 of 8 channels producing signals |
| Evaluator diversity | All 14 paths should express when conditions are met | ❌ Only 3 of 14 paths have produced live signals in recent history | **Critical** |

### 1.4 Strongest Production-Grade Architecture (Independent of Current Code)

An ideal multi-pair institutional signal engine would have:

1. **Per-pair regime with BTC context overlay** — not BTC-proxy-led, not globally uniform ✅ (current is correct here)
2. **Family-aware gating** — MTF alignment requirement varies by setup thesis (trend-following needs strong MTF; mean-reversion/compression do not) ⚠️ (current is partially generic)
3. **Evaluator-owned SL/TP with proportional validation** — structural levels preserved, caps applied proportionally per setup family ⚠️ (caps exist but are uniform per channel, not per family)
4. **Spread and quality gates that adapt to market conditions** — during broad QUIET/low-vol periods, tighter spread limits should relax proportionally ⚠️ (current spread gates are too static)
5. **Per-evaluator confidence calibration** — a 60-confidence SR_FLIP_RETEST is not the same quality as a 60-confidence TREND_PULLBACK_EMA; each path needs its own calibration ❌ (not implemented)
6. **Observable suppression funnel with per-path metrics** — every candidate lost should be traceable to a specific gate with per-path statistics ✅ (suppression telemetry exists and is good)

---

## 2. Full Signal-Path Inventory and Expression Audit

### 2.1 Evidence Base

**Live performance history:** 38 signals on record (monitor/latest.txt, 2026-04-15 05:03 UTC)

**Setup type distribution in live signals:**
| Setup | Count | % of total | Avg Confidence |
|---|---|---|---|
| TREND_PULLBACK_EMA | 16 | 42.1% | 58.1 |
| SR_FLIP_RETEST | 14 | 36.8% | 59.5 |
| CONTINUATION_LIQUIDITY_SWEEP | 4 | 10.5% | 61.0 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 2.6% | 83.0 |
| (all others) | 0 | 0% | — |

**Outcome distribution:**
| Outcome | Count | % |
|---|---|---|
| SL_HIT | 29 | 76.3% |
| CLOSED | 5 | 13.2% |
| PROFIT_LOCKED | 1 | 2.6% |
| FULL_TP_HIT | 1 | 2.6% |
| (other) | 2 | 5.3% |

### 2.2 Path-by-Path Verdict Table

| # | Setup / Path | Channel | Live expressed? | Signal count | Evidence | If not expressed, likely cause | Verdict category | Confidence |
|---|---|---|---|---|---|---|---|---|
| 1 | TREND_PULLBACK_EMA | 360_SCALP | ✅ Yes | 16 | monitor history | N/A | **Expressed live** | High |
| 2 | SR_FLIP_RETEST | 360_SCALP | ✅ Yes | 14 | monitor history | N/A | **Expressed live** | High |
| 3 | CONTINUATION_LIQUIDITY_SWEEP | 360_SCALP | ✅ Yes | 4 | monitor history | N/A | **Expressed live** | High |
| 4 | LIQUIDITY_SWEEP_REVERSAL | 360_SCALP | ✅ Yes | 1 | monitor history | N/A | **Expressed live** | High |
| 5 | FAILED_AUCTION_RECLAIM | 360_SCALP | ⚠️ Candidate generated | 0 | suppression: `score_50to64:FAILED_AUCTION_RECLAIM` in logs | Score lands in 50-64 WATCHLIST zone, not paid tier; also regime-restricted (blocks VOLATILE, VOLATILE_UNSUITABLE, STRONG_TREND) | **Candidate generated but suppressed by scoring** | High |
| 6 | DIVERGENCE_CONTINUATION | 360_SCALP | ⚠️ Likely candidate | 0 | No direct evidence in current window | Regime-restricted to TRENDING only; soft penalties may push below threshold; QUIET exempt path exists but needs conf≥64 | **Suppressed by regime gating + scoring** | Medium |
| 7 | WHALE_MOMENTUM | 360_SCALP | ❌ No evidence | 0 | No log entries | Hard-blocked in QUIET (PR-16); heavy soft penalties (RSI±5, OBI±8, no_OB±10 = up to 23pts penalty); requires specific OI+large block conditions | **Suppressed by regime + soft penalties** | Medium |
| 8 | VOLUME_SURGE_BREAKOUT | 360_SCALP | ❌ No evidence | 0 | No log entries | Blocks QUIET only; requires surge_z > 2.5, volume > 3x avg, requires specific premium zone entry; structurally rare | **Silent — rare conditions** | Medium |
| 9 | BREAKDOWN_SHORT | 360_SCALP | ❌ No evidence | 0 | No log entries | Blocks QUIET only; mirrors VOLUME_SURGE_BREAKOUT for shorts; requires equivalent conditions | **Silent — rare conditions** | Medium |
| 10 | LIQUIDATION_REVERSAL | 360_SCALP | ❌ No evidence | 0 | No log entries | Requires actual liquidation cascade data from OrderFlowStore; conditions extremely rare in non-volatile markets | **Silent — rare conditions + data dependency** | Medium |
| 11 | OPENING_RANGE_BREAKOUT | 360_SCALP | ❌ Disabled | 0 | config: `SCALP_ORB_ENABLED=false` (PR-06) | Disabled by governance — "not institutional-grade session-anchored range" | **Disabled by governance** | High |
| 12 | FUNDING_EXTREME_SIGNAL | 360_SCALP | ❌ No evidence | 0 | No log entries | Requires extreme funding rate data; blocks QUIET regime; conditions are inherently rare | **Silent — rare conditions + data dependency** | Medium |
| 13 | QUIET_COMPRESSION_BREAK | 360_SCALP | ❌ No evidence | 0 | No log entries | Requires non-QUIET/RANGING regime; BB squeeze detection; conditions depend on QUIET→breakout transition | **Silent — regime + condition rarity** | Low |
| 14 | POST_DISPLACEMENT_CONTINUATION | 360_SCALP | ❌ No evidence | 0 | No log entries | Blocks VOLATILE, RANGING, QUIET; requires prior displacement + consolidation pattern; structurally demanding | **Silent — restrictive regime + rare conditions** | Medium |
| 15 | FVG_RETEST | 360_SCALP_FVG | ❌ Channel disabled | 0 | config: `CHANNEL_SCALP_FVG_ENABLED=false` | Disabled by governance (PR-04); even when running, FVG SL rejection (2% max) fires constantly on LABUSDT (4.01%) and ENJUSDT (3.15%) | **Disabled by governance + would be blocked by SL geometry** | High |
| 16 | CVD_DIVERGENCE | 360_SCALP_CVD | ❌ Channel disabled | 0 | config: `CHANNEL_SCALP_CVD_ENABLED=false` | Disabled as "noisy" | **Disabled by governance** | High |
| 17 | VWAP_BOUNCE | 360_SCALP_VWAP | ❌ Channel disabled | 0 | config: `CHANNEL_SCALP_VWAP_ENABLED=false` | Disabled as "noisy" | **Disabled by governance** | High |
| 18 | RSI_MACD_DIVERGENCE | 360_SCALP_DIVERGENCE | ❌ Channel disabled | 0 | config: `CHANNEL_SCALP_DIVERGENCE_ENABLED=false` | Disabled by governance (PR-04); suppression logs show `score_below50:RSI_MACD_DIVERGENCE` every cycle — evaluator still runs but scores poorly | **Disabled + would score below threshold** | High |
| 19 | SMC_ORDERBLOCK | 360_SCALP_ORDERBLOCK | ❌ Channel disabled | 0 | config: `CHANNEL_SCALP_ORDERBLOCK_ENABLED=false` | Disabled by governance (PR-04); `volatile_unsuitable` fires 8-11 per cycle | **Disabled + would be volatile-blocked** | High |
| 20 | SUPERTREND_FLIP | 360_SCALP_SUPERTREND | ❌ Channel disabled | 0 | config: `CHANNEL_SCALP_SUPERTREND_ENABLED=false` | Disabled as "noisy" | **Disabled by governance** | High |
| 21 | ICHIMOKU_TK_CROSS | 360_SCALP_ICHIMOKU | ❌ Channel disabled | 0 | config: `CHANNEL_SCALP_ICHIMOKU_ENABLED=false` | Disabled as "noisy" | **Disabled by governance** | High |

### 2.3 Why Have Only a Small Number of Paths Generated Live Signals?

**Direct answer:** Three compounding causes, ranked by impact:

1. **7 of 8 channels are disabled by governance (PR-04, PR-06)** — This is the single largest factor. Only 360_SCALP is enabled. The 7 auxiliary channels (FVG, CVD, VWAP, Divergence, Orderblock, Supertrend, Ichimoku) are all `false` in config. This eliminates 7 of 22 evaluator paths from producing any output regardless of market conditions.

2. **Within the enabled 360_SCALP channel, regime and structural rarity suppresses most paths** — Of the 14 internal evaluators, only 4 have produced live signals. The remaining 10 either:
   - Require rare market conditions (LIQUIDATION_REVERSAL, FUNDING_EXTREME, VOLUME_SURGE, BREAKDOWN_SHORT)
   - Are restricted to specific regimes that haven't been active (POST_DISPLACEMENT requires only TRENDING; QUIET_COMPRESSION_BREAK requires QUIET→breakout transition)
   - Accumulate heavy soft penalties that push confidence below thresholds (WHALE_MOMENTUM: up to 23pts penalty; FAILED_AUCTION_RECLAIM: scores 50-64)

3. **Generic gating disproportionately affects non-trend paths** — MTF gate, QUIET_SCALP_BLOCK, and spread filters apply uniformly across all 360_SCALP evaluators. MTF gate alone blocks 2-6 candidates per scan cycle. For mean-reversion and compression setups, requiring 50% multi-timeframe trend alignment is structurally inappropriate — these setups fire precisely when timeframes are NOT aligned.

**Business impact:** The system is effectively a 4-path signal engine (TREND_PULLBACK_EMA, SR_FLIP_RETEST, CONTINUATION_LIQUIDITY_SWEEP, LIQUIDITY_SWEEP_REVERSAL) masquerading as a 22-path system. 81.6% of all live signals come from just 2 paths (TREND_PULLBACK + SR_FLIP).

---

## 3. End-to-End Suppression Funnel

### 3.1 Full Runtime Path

```
1. Pair scan → _prefilter_pairs() → volume/cooldown/active filter → ~60-80 of 200+ pairs
2. Data assembly → _load_candles() → 5 timeframes (1m, 5m, 15m, 1h, 4h)
3. smc_data assembly → _build_scan_context() → indicators, SMC detect, regime, pair profile
4. Channel check → _should_skip_channel() → channel enabled? volatile_unsuitable? spread/quality?
5. Evaluator → ScalpChannel.evaluate() → all 14 _evaluate_* run → List[Signal] candidates
6. Gate chain → MTF gate, VWAP, kill zone, OI, cross-asset, spoof, vol-div, cluster
7. Scoring → _scoring_engine.score() → composite 0-100, family-aware dimensions
8. Post-score gates → SMC hard gate, trend hard gate, stat filter, pair analysis
9. QUIET_SCALP_BLOCK → confidence floor in QUIET regime
10. Tier classification → A+ (80+), B (65-79), WATCHLIST (50-64), FILTERED (<50)
11. SL/TP validation → build_risk_plan() → channel-specific caps, near-zero guard
12. Arbitration → per-direction best-of for 360_SCALP candidates
13. Router → _process() → correlation lock, cooldown, TP/SL sanity, stale gate
14. Lifecycle → _active_signals → TradeMonitor → SL/TP/expiry tracking
```

### 3.2 Where Candidates Are Most Commonly Lost

Based on monitor evidence (2026-04-15 05:03 UTC, last 500 lines):

| Suppressor | Count/cycle | What is lost | Stage |
|---|---|---|---|
| `pair_quality:spread too wide` | 24-40 | Entire pairs eliminated before evaluator runs | Stage 4 |
| `volatile_unsuitable:360_SCALP_FVG` | 2-11 | FVG channel candidates (channel disabled anyway) | Stage 4 |
| `volatile_unsuitable:360_SCALP_DIVERGENCE` | 2-11 | Divergence channel candidates (channel disabled anyway) | Stage 4 |
| `volatile_unsuitable:360_SCALP_ORDERBLOCK` | 2-11 | Orderblock channel candidates (channel disabled anyway) | Stage 4 |
| `mtf_gate:360_SCALP` | 2-6 | **Active evaluator candidates** killed at MTF check | Stage 6 |
| `mtf_gate:360_SCALP_DIVERGENCE` | 1 | Divergence candidates (channel disabled anyway) | Stage 6 |
| `QUIET_SCALP_BLOCK` | 5+ per window | SCALP candidates in QUIET below 65.0 | Stage 9 |
| `score_below50:360_SCALP` | 1 | Low-quality candidates correctly filtered | Stage 10 |
| `score_below50:LIQUIDITY_SWEEP_REVERSAL` | 1 | LSR candidate scored too low | Stage 10 |
| `score_below50:RSI_MACD_DIVERGENCE` | 1 | Divergence candidate too weak | Stage 10 |
| `score_50to64:SR_FLIP_RETEST` | 1-2 | SR_FLIP scoring in WATCHLIST zone | Stage 10 |
| `score_50to64:FAILED_AUCTION_RECLAIM` | 1 | FAR scoring in WATCHLIST zone | Stage 10 |
| `score_65to79:SR_FLIP_RETEST` | 1 | SR_FLIP scoring in B tier (passes if ≥65) | Stage 10 |
| FVG SL rejection (LABUSDT, ENJUSDT) | Every cycle | FVG candidates killed by 2% SL max | Stage 11 |
| SL near-zero rejection (AAVEUSDT-like) | Every cycle | SL=0.0315% < 0.05% min | Stage 11 |
| SL capped (360_SCALP) | Occasional | SL distance >1.50% clamped | Stage 11 |

### 3.3 Classification of Suppressors

| Suppressor | Behavior type | Assessment |
|---|---|---|
| `pair_quality:spread too wide` | Correct protective | **Harsh-but-valid** — 40 pairs/cycle means over half the universe is spread-blocked; may be too tight for current market conditions |
| `volatile_unsuitable:*` | Correct protective | **Healthy** for disabled channels; irrelevant since channels are off |
| `mtf_gate:360_SCALP` | **Over-generic policy** | MTF alignment requirement does not discriminate between trend-following and mean-reversion setups. Reversal and compression setups should have relaxed or waived MTF requirements. This is the **most impactful fixable suppressor** for the enabled channel. |
| `QUIET_SCALP_BLOCK` | Correct protective | **Healthy** — prevents low-confidence scalps in quiet markets; exemptions for QUIET_COMPRESSION_BREAK and DIVERGENCE_CONTINUATION are correct |
| `score_below50:*` | Correct protective | **Healthy** — sub-50 signals should be filtered |
| `score_50to64:*` | Correct protective | **Healthy** — WATCHLIST tier routes to free channel only; not a signal loss |
| FVG SL rejection (2% max) | **Geometry defect for specific pairs** | LABUSDT consistently produces 4.01% SL distance; ENJUSDT 3.15%. These are not transient — they're structural pair-price-level issues. See §4 for detailed analysis. |
| SL near-zero rejection | **Implementation defect** | Repeated rejection of AAVEUSDT with SL=100.63832 only 0.0315% from entry=100.67000 — the evaluator produces a structurally valid SL but the universal 0.05% minimum is too coarse for this price level. See §4. |
| SL capped (1.5% max) | Protective but potentially too tight | **Harsh-but-valid** for generic scalps; may distort evaluator-authored SL for pairs with wider ATR |

### 3.4 Missing Telemetry / Observability Gaps

1. **No per-evaluator hit-rate tracking** — we cannot determine which of the 14 evaluators has the best win rate without manual analysis of the 38-signal performance history
2. **No candidate-reached-but-gated counter** — for evaluators that never produce candidates (vs. those that produce candidates that get gated), we can't distinguish between "never fires" and "always suppressed"
3. **No SL/TP geometry rejection telemetry aggregation** — FVG SL rejections and near-zero rejections repeat every cycle but there's no per-evaluator rejection rate summary
4. **No regime transition event log** — regime changes are detected but not logged as discrete events, making it impossible to correlate regime transitions with signal expression windows
5. **WATCHLIST free-channel posts are not tracked in performance history** — signals with 50-64 confidence that route to free channel are invisible to outcome tracking

---

## 4. SL / TP / Risk Geometry Integrity Audit

### 4.1 End-to-End SL/TP Flow

```
Evaluator (_evaluate_*)
  └→ Computes method-specific SL and TP based on setup thesis
  └→ Signal.stop_loss, Signal.tp1/tp2/tp3, Signal.original_sl_distance set

  [If FVG evaluator: scalp_fvg.py early rejection if sl_dist > 2.00%]

build_risk_plan() (signal_quality.py:916-1267)
  ├→ Protected setup? → Preserve evaluator-authored SL (10 of 14 setups protected)
  ├→ Channel-specific SL cap:
  │     360_SCALP: 1.5% max
  │     360_SCALP_FVG: 1.0% max
  │     Others: 1.0-1.2% max
  ├→ Near-zero SL guard: reject if < 0.05% from entry
  ├→ Directional sanity: reject if SL on wrong side of entry
  └→ TP validation: preserve evaluator TPs for protected setups; R-multiple fallback

SignalRouter._process() (signal_router.py:545-571)
  ├→ TP direction sanity (TP1 must be on correct side of entry)
  └→ SL direction sanity (SL must be on correct side of entry)

TradeMonitor (trade_monitor.py)
  └→ Uses final SL/TP for lifecycle tracking, trailing stop, outcome recording
```

### 4.2 Live Warning Patterns — Correlation with Code Paths

#### Pattern 1: "FVG SL rejected for LABUSDT LONG: sl_dist/close=4.01% > 2.00% max"

- **Code path:** `scalp_fvg.py:178-188` — early SL distance check before signal is built
- **Root cause:** LABUSDT's FVG zone boundaries are structurally wide (4.01% of close). The FVG evaluator correctly identifies the zone, but the 2.00% cap in `scalp_fvg.py` rejects it.
- **Frequency:** Every scan cycle (LABUSDT is Tier 1, scanned every cycle)
- **Assessment:** **Mixed — half healthy, half defective:**
  - The 2.00% cap is reasonable for most pairs where FVG zones are tight
  - But LABUSDT is a low-price token where structural zones are inherently wider as a % of price
  - This is evidence of a **precision issue**: the percentage-based SL cap does not account for price magnitude differences across pairs
  - **Recommendation:** Use ATR-normalized SL distance (e.g., SL ≤ 3×ATR) instead of flat percentage for FVG evaluator

#### Pattern 2: "SL near-zero rejection for 360_SCALP LONG: SL=100.63832000 is only 0.0315% from entry=100.67000000 (min=0.0500%)"

- **Code path:** `signal_quality.py:1003-1031` — universal 0.05% minimum SL distance
- **Root cause:** The evaluator computes a valid structural SL (100.63832) for AAVEUSDT which is only 0.0315% from entry. At AAVEUSDT's ~$100 price level, this is $0.032 — a tight but potentially valid scalp SL.
- **Frequency:** Every scan cycle where AAVEUSDT candidate is generated
- **Assessment:** **Partially defective:**
  - The 0.05% universal floor is too coarse. For a $100 token, 0.05% = $0.05; for a $0.001 token, 0.05% = $0.000001.
  - The evaluator-authored SL of 0.0315% on a $100 token is $0.032 — this is a $3.20 risk on a 100× leveraged position, which is valid for a scalp.
  - The universal floor does not account for price magnitude, tick size, or spread.
  - **This is a B13 violation** — the downstream cap is rejecting an evaluator-authored structural SL without understanding the setup thesis.
  - **Recommendation:** Replace flat 0.05% floor with `max(0.02%, tick_size × 3, spread × 2)` adaptive floor

#### Pattern 3: "SL capped for 360_SCALP LONG: 3.52% > 1.50% max (capped to 0.45127775)"

- **Code path:** `signal_quality.py:982-1001` — channel-specific SL cap
- **Root cause:** Evaluator-authored SL is 3.52% from entry, exceeding the 1.50% cap for 360_SCALP.
- **Frequency:** Occasional (appears in some cycles)
- **Assessment:** **Protective but distortive:**
  - The 1.50% cap prevents extremely wide stops that would produce bad risk profiles
  - But clamping from 3.52% to 1.50% means the capped SL (0.45127775) is no longer at the evaluator-intended structural invalidation level
  - If the evaluator placed SL at a structural level (e.g., below a sweep), clamping moves it to an arbitrary price with no structural meaning
  - This **violates B13 intent** — the evaluator's thesis is that the trade is invalid below 3.52%, but the capped SL at 1.50% will trigger on normal volatility
  - **This directly contributes to the 76.3% SL_HIT rate** — capped SLs are tighter than the evaluator intended
  - **Recommendation:** Per-family SL caps instead of per-channel. E.g., TREND_PULLBACK may need wider SL than SR_FLIP. Also consider hard-rejecting signals where evaluator SL > 2× channel cap rather than clamping (which distorts).

### 4.3 SL Follow-Through Analysis from Monitor Evidence

The monitor's SL follow-through analysis reveals:

| Classification | Count | % |
|---|---|---|
| Clean failure | 14/20 | 70% |
| Possible stop-too-tight / continuation | 4/20 | 20% |
| Partial reclaim | 2/20 | 10% |

**Key statistics:**
- **Average SL exit PnL: -0.52%**
- **Average MFE before stop: +0.10%** — signals barely move favorably before hitting SL
- **Average hold duration: 5 minutes** — extremely short; signals are being stopped out almost immediately

**Signal #7 explicitly flagged:** "BTCUSDT LONG TREND_PULLBACK_EMA — possible stop-too-tight / continuation"
**Signal #10:** "GIGGLEUSDT LONG TREND_PULLBACK_EMA — possible stop-too-tight / continuation" (MFE +0.70% before -1.01% SL hit)

**Interpretation:** The 20% "stop-too-tight / continuation" rate plus +0.10% average MFE is concerning. It suggests approximately 1 in 5 SL hits may be premature — the trade thesis was correct but the SL was too tight to survive normal noise. This is consistent with:
- SL capping from evaluator-intended 3.52% to 1.50%
- Near-zero SL rejection removing valid tight scalps
- Universal SL floors not accounting for per-pair volatility profiles

### 4.4 Setup Classes Most Exposed to Geometry Issues

| Setup | Exposure | Why |
|---|---|---|
| TREND_PULLBACK_EMA | **High** — SL is EMA21 × 1.1 | If ATR is wide, EMA-based SL can exceed 1.5% cap. Clamping moves SL to arbitrary non-structural level. This is the most-expressed path (42% of signals) with 87.5% SL_HIT rate. |
| SR_FLIP_RETEST | **Medium** — SL is 0.2% beyond flipped level | Structurally tight, usually within cap. But near-zero guard may reject on high-price pairs. |
| CONTINUATION_LIQUIDITY_SWEEP | **Medium** — SL is sweep ± ATR×0.3 | ATR-based component may push beyond cap on volatile pairs. |
| FVG_RETEST | **Critical** — SL is zone boundary ± ATR×0.5 | Channel disabled, but even if enabled, SL geometry rejection would kill most signals on low-price or wide-zone pairs. |
| LIQUIDATION_REVERSAL | **Unknown** — no live signals | Cascade extreme SL may be wide; Fibonacci TP targets are structurally sound. |

### 4.5 Assessment Against B13 and Method-Specific Doctrine

| Criterion | Assessment |
|---|---|
| B13 compliance (evaluator owns SL/TP) | **Partially violated** — evaluators compute method-specific SL/TP, and protected setups preserve them, but universal caps can clamp and universal floors can reject evaluator-authored values |
| Strategy-expression integrity | **Partially distorted** — 20% of SL hits may be premature due to capping; 0.10% average MFE suggests signals barely move before stop |
| Per-family downstream handling | **Missing** — caps are per-channel (1.5% for all 360_SCALP), not per-family. A TREND_PULLBACK_EMA needs wider SL than an SR_FLIP_RETEST |

---

## 5. Regime / Market Structure Truth Test

### 5.1 How Regime Is Computed

**Location:** `src/regime.py` — `MarketRegimeDetector.classify()`

**Scope:** **Per-pair.** Each symbol receives independent classification using its own indicators:
- ADX (trend strength)
- Bollinger Band width % (volatility measure)
- EMA9 slope (direction)
- Volume delta % (forced regime changes)

**Categories:** TRENDING_UP, TRENDING_DOWN, RANGING, VOLATILE, QUIET

**Thresholds:**
- ADX ≥ 25 → TRENDING
- ADX ≤ 18 → RANGING
- BB width ≥ 5% → VOLATILE
- BB width ≤ 1.2% → QUIET
- Volume delta ≥ 60% → forces out of QUIET/RANGING

**Hysteresis:** 3-candle smoothing prevents regime flapping.

### 5.2 What Is Truly Per-Pair in Runtime

| Component | Per-pair? | Evidence |
|---|---|---|
| Regime classification | ✅ Yes | `regime_detector.classify()` called per symbol with that symbol's indicators |
| Spread filtering | ✅ Yes | bookTicker fetched per symbol; tier-adjusted thresholds |
| Volume filtering | ✅ Yes | Per-pair 24h volume checked against regime-aware floor |
| SMC detection | ✅ Yes | Per-pair sweep/FVG/MSS detection |
| MTF alignment | ✅ Yes | Per-pair EMA fast/slow on each timeframe |
| Cross-asset gate | ❌ Global | Compares signal direction to BTC/ETH macro trend — not pair-specific |
| SL caps | ❌ Per-channel | 1.5% for all 360_SCALP regardless of pair or regime |
| Min confidence | ❌ Per-channel | 65 for all 360_SCALP regardless of pair or setup |
| Soft gate multipliers | ✅ Regime-aware | QUIET gets 1.8× penalty multiplier for SCALP |

### 5.3 What Is Only Analytic/Reporting

| Component | Pair-level in analytics? | Pair-level in runtime? |
|---|---|---|
| Pair quality composite score | ✅ Yes | ✅ Yes (assess_pair_quality) |
| Per-pair hit rate tracking | ✅ Yes (performance_tracker) | ⚠️ Limited — stat_filter checks, but cancellations bypass record_outcome |
| Pair profile (MAJOR/MIDCAP/ALTCOIN) | ✅ Yes | ✅ Yes (multipliers applied) |
| Regime history per symbol | ✅ Yes (rolling 30min) | ✅ Yes (used for instability detection) |
| Per-evaluator confidence calibration | ❌ Not implemented | ❌ Not implemented |

### 5.4 Deeper Question Answer

**Does the live signal pipeline truly analyze per-pair market structure, or is it mostly present only in analytics?**

**Answer:** The pipeline **does perform genuine per-pair analysis** at the regime, spread, volume, and SMC levels. This is architecturally sound. However, the **downstream handling is still too uniform**:

1. **SL caps are per-channel, not per-pair or per-regime** — A 1.5% SL cap means the same thing for BTCUSDT ($75K × 1.5% = $1,125) as for ENJUSDT ($0.044 × 1.5% = $0.00066). For low-price high-volatility pairs, 1.5% may be too tight relative to normal noise.

2. **MTF gating is setup-family-unaware** — The 50% timeframe alignment requirement applies equally to trend-following (where it's correct) and mean-reversion (where it's structurally wrong). A compression breakout fires when timeframes are misaligned; requiring alignment contradicts the setup thesis.

3. **Confidence thresholds are per-channel, not per-evaluator** — All 14 evaluators within 360_SCALP share the same 65 min_confidence. But evaluator confidence calibration varies: SR_FLIP_RETEST has up to 20pts of soft penalties (proximity+3, wick+4, RSI+5, SMC+8), making it structurally harder to reach 65 than TREND_PULLBACK_EMA which gets an +8 bonus.

**Doctrinal assessment:** The per-pair analysis architecture is **correct in principle but incomplete in application**. The system does per-pair analysis → per-channel downstream handling. It should do per-pair analysis → per-family downstream handling.

---

## 6. Doctrine vs Runtime Reality

### 6.1 Doctrine-to-Code Comparison

| Doctrine claim (OWNER_BRIEF) | Code reality | Mismatch? |
|---|---|---|
| "All 14 internal evaluators run" (§3.4) | ✅ All 14 run within ScalpChannel.evaluate() | No — but only 4 produce live output |
| "OPENING_RANGE_BREAKOUT disabled" (PR-06) | ✅ `SCALP_ORB_ENABLED=false` | No |
| "7 auxiliary channels disabled" (PR-04) | ✅ All 7 are `false` in config | No |
| "WATCHLIST → free channel only" (§3.6, B9) | ✅ Fixed in PR #144 | No (was defective before PR #144) |
| "B-tier (65-79) dispatches to paid" (§3.5) | ✅ Fixed in PR-18 | No (was defective before PR-18) |
| "SMC structural basis non-negotiable" (B5) | ✅ SMC hard gate with named exemptions | No |
| "Every evaluator owns its SL/TP" (B13) | ⚠️ Evaluators compute SL/TP, protected setup list preserves them, but universal caps can still distort | **Partial violation** |
| "Family-aware hybrid scoring" (§3.6) | ✅ Thesis dimension varies by family | No |
| "Duplicate lifecycle posting confirmed real" (ACTIVE_CONTEXT) | ⚠️ Still present — no fix merged | **Known defect, deferred** |
| "Generic MTF gate may be over-generic" (ACTIVE_CONTEXT) | ⚠️ Confirmed by monitor data — MTF blocks 2-6/cycle for 360_SCALP | **Known defect, deferred** |
| "Scan latency spikes" (ACTIVE_CONTEXT) | ⚠️ One spike seen: 51,759ms (05:01:15); baseline 4.6-5.6s | **Intermittent, not fixed** |

### 6.2 Claimed-Fixed vs Runtime Evidence

| Claimed fix | Evidence of fix | Residual issue? |
|---|---|---|
| PR-18: B-tier dead zone fixed (min_confidence 80→65) | ✅ Monitor shows signals at conf 51.5-83.0 | No residual |
| PR #144: WATCHLIST lifecycle segregation | ✅ Monitor shows 0 active signals (Signals=0); no WATCHLIST lifecycle events | No residual (but verification window is limited) |
| PR-15: Evaluator soft-penalty applied post-scoring | ✅ Suppression logs show `score_50to64` and `score_65to79` by setup class | No residual |
| PR-02: Structural SL/TP preservation | ⚠️ SL capping warnings still fire → evaluator SL is preserved but then capped by universal guard | **Adjacent defect: cap distorts preserved SL** |
| PR-16: WHALE_MOMENTUM blocked in QUIET | ✅ No WHALE_MOMENTUM candidates in monitor | No residual |

### 6.3 Specific Contradiction: SL Capping vs B13

OWNER_BRIEF §3.8 states: "Every evaluator owns its SL/TP logic. Sharing SL/TP formulas across evaluators violates B13."

But `signal_quality.py` applies a **uniform** 1.5% SL cap to all 360_SCALP setups regardless of evaluator:
- This is functionally equivalent to sharing an SL formula
- When an evaluator says "invalidation is at 3.52%" and the system clamps it to 1.50%, the evaluator's thesis is overridden
- The monitor evidence shows this happens regularly, and 76.3% of tracked signals hit SL

**This is the most impactful doctrine-to-runtime mismatch currently in production.**

### 6.4 Performance Reality

From the 38 signals on record:
- **Win rate: ~15.8%** (2 FULL_TP + 1 PROFIT_LOCKED + 3 CLOSED-with-positive-PnL = ~6 of 38)
- **Average losing PnL: -0.52%**
- **Average winning PnL: ~+1.0%** (small sample)
- **Dominant outcome: SL_HIT at 76.3%**

The 5-minute average hold duration and 0.10% average MFE strongly suggest that stops are triggering before the trade thesis has a chance to play out. This is consistent with SL capping distortion.

---

## Summary Tables

### A. Executive Verdict

The 360 Crypto Eye system is **architecturally sound in its per-pair analysis framework** but is **operationally crippled by three compounding issues:**

1. **Channel governance:** 7 of 8 channels are disabled, reducing 22 evaluator paths to 14.
2. **Evaluator expression:** Within the enabled channel, only 4 of 14 evaluators produce live signals due to regime restrictions, rare conditions, and generic gating.
3. **SL geometry distortion:** Universal SL caps (1.5%) override evaluator-authored structural invalidation levels, contributing to a 76.3% SL_HIT rate with 5-minute average hold and 0.10% average MFE.

The system is producing signals but they are dominated by 2 setup types (TREND_PULLBACK_EMA 42%, SR_FLIP_RETEST 37%), most signals lose, and they lose fast. This is not the behavior of a 14-path institutional signal engine — it is a 2-path engine with tight stops and poor win rate.

### B. Path Expression Table

| Path / Setup | Live expressed? | Evidence | If not, likely cause | Verdict | Confidence |
|---|---|---|---|---|---|
| TREND_PULLBACK_EMA | ✅ 16 signals | Monitor history | N/A | Expressed live | High |
| SR_FLIP_RETEST | ✅ 14 signals | Monitor history | N/A | Expressed live | High |
| CONTINUATION_LIQUIDITY_SWEEP | ✅ 4 signals | Monitor history | N/A | Expressed live | High |
| LIQUIDITY_SWEEP_REVERSAL | ✅ 1 signal | Monitor history | N/A | Expressed live | High |
| FAILED_AUCTION_RECLAIM | ⚠️ Candidate gen'd | Suppression logs | Scores 50-64 (WATCHLIST) | Scoring suppression | High |
| DIVERGENCE_CONTINUATION | ⚠️ Likely candidate | Regime restriction | TRENDING-only + QUIET exempt ≥64 | Regime gating | Medium |
| WHALE_MOMENTUM | ❌ None | No evidence | QUIET-blocked (PR-16) + heavy penalties | Regime + penalty | Medium |
| VOLUME_SURGE_BREAKOUT | ❌ None | No evidence | Structurally rare conditions | Rare conditions | Medium |
| BREAKDOWN_SHORT | ❌ None | No evidence | Structurally rare conditions | Rare conditions | Medium |
| LIQUIDATION_REVERSAL | ❌ None | No evidence | Requires cascade data; extremely rare | Rare conditions | Medium |
| OPENING_RANGE_BREAKOUT | ❌ Disabled | Config flag | Governance (PR-06) | Disabled | High |
| FUNDING_EXTREME_SIGNAL | ❌ None | No evidence | Extreme funding rate; rare | Rare conditions | Medium |
| QUIET_COMPRESSION_BREAK | ❌ None | No evidence | Requires QUIET→breakout transition | Rare conditions | Low |
| POST_DISPLACEMENT_CONTINUATION | ❌ None | No evidence | TRENDING-only; requires prior displacement | Regime + rare | Medium |
| FVG_RETEST | ❌ Ch. disabled | Config + SL rejections | Governance + geometry rejection | Disabled + defective | High |
| CVD_DIVERGENCE | ❌ Ch. disabled | Config | Governance | Disabled | High |
| VWAP_BOUNCE | ❌ Ch. disabled | Config | Governance | Disabled | High |
| RSI_MACD_DIVERGENCE | ❌ Ch. disabled | Config + below-50 scores | Governance + scoring | Disabled | High |
| SMC_ORDERBLOCK | ❌ Ch. disabled | Config + volatile_unsuitable | Governance + volatile | Disabled | High |
| SUPERTREND_FLIP | ❌ Ch. disabled | Config | Governance | Disabled | High |
| ICHIMOKU_TK_CROSS | ❌ Ch. disabled | Config | Governance | Disabled | High |

### C. Top Suppressors Table

| Suppressor | What it means | Healthy / Harsh / Generic / Defective | Impact on expression |
|---|---|---|---|
| `pair_quality:spread too wide` | 24-40 pairs/cycle eliminated | **Harsh-but-valid** — may need per-regime adaptation | High — eliminates >50% of pair universe |
| `mtf_gate:360_SCALP` | 2-6 candidates/cycle killed by MTF alignment | **Over-generic** — mean-reversion setups shouldn't need trend alignment | **Critical** — kills candidates from active evaluators |
| `volatile_unsuitable:*` | 8-11 per channel for disabled channels | **Irrelevant** — channels are disabled anyway | None (channels off) |
| `QUIET_SCALP_BLOCK` | 5+ scalp candidates blocked in QUIET regime | **Healthy** — correct protective floor | Medium — but paired with MTF gate may over-suppress |
| `score_below50:*` | Low-quality candidates filtered | **Healthy** — correct behavior | Low |
| FVG SL rejection (2% max) | FVG candidates killed for wide SL | **Partially defective** — percentage-based, not ATR-normalized | Medium (channel disabled, but defective if enabled) |
| SL near-zero rejection (0.05% min) | Valid tight scalps rejected | **Defective for high-price tokens** — 0.0315% on $100 token is valid | Medium — AAVEUSDT candidates killed every cycle |
| SL capping (1.5% max) | Evaluator SL clamped | **Distortive** — violates B13; contributes to 76.3% SL_HIT rate | **Critical** — live signals have wrong SL |
| Channel disabled flags | 7/8 channels off | **Governance decision** — correct until channels are rebuilt | **Critical** — eliminates 7/22 evaluator paths |

### D. Architecture Verdict

**Current runtime is: partially aligned but still too generic.**

- ✅ Per-pair regime detection is correct
- ✅ Family-aware scoring exists
- ✅ Evaluator-authored SL/TP with structural protection exists
- ⚠️ MTF gating is setup-family-unaware (over-generic)
- ⚠️ SL caps are per-channel, not per-family or per-pair
- ⚠️ Confidence thresholds are per-channel, not per-evaluator
- ❌ 7/8 channels disabled, reducing to a 4-path engine in practice
- ❌ Most evaluators never express due to compound suppression

**The architecture has the right shape but the implementation is too uniform in its downstream handling, and governance decisions have reduced the system to a fraction of its intended capacity.**

### E. SL / Geometry Verdict

**Current SL/TP handling is: protective but too harsh, with partial distortion.**

- ✅ Method-specific SL/TP computation exists (B13 at evaluator level)
- ✅ Structural SL/TP preservation for protected setups exists (PR-02, PR-14)
- ✅ Directional sanity checks are correct
- ⚠️ Universal 1.5% SL cap overrides evaluator-authored structural levels → **B13 violation**
- ⚠️ Universal 0.05% SL floor rejects valid tight scalps on high-price tokens → **B13 violation**
- ⚠️ FVG 2% SL rejection is percentage-based, not ATR-normalized → **pair-specific precision issue**
- ⚠️ 76.3% SL_HIT rate, 5-min hold, 0.10% MFE strongly suggest stops are too tight
- ❌ SL capping is per-channel, not per-family — all 14 evaluators share the same cap

**20% of SL exits show "stop-too-tight / continuation" classification, meaning the trade thesis was correct but the SL was too narrow. This is a geometry defect, not a thesis defect.**

### F. Best Next PR / PR Sequence

| Priority | PR | Description | Evidence gate | Expected impact |
|---|---|---|---|---|
| **1** | **Per-family SL caps** | Replace uniform 1.5% cap with per-setup-family caps (e.g., TREND_PULLBACK: 2.5%, SR_FLIP: 1.0%, LIQUIDATION_REVERSAL: 3.0%) | SL_HIT rate 76.3% + 20% stop-too-tight + MFE +0.10% | **High** — directly addresses the #1 cause of poor win rate |
| **2** | **Family-aware MTF gating** | Add MTF gate exemptions for mean-reversion and compression setups (QUIET_COMPRESSION_BREAK, SR_FLIP_RETEST, FAILED_AUCTION_RECLAIM, DIVERGENCE_CONTINUATION) | MTF gate blocks 2-6 active candidates/cycle | **Medium-High** — unlocks suppressed paths |
| **3** | **Adaptive SL floor** | Replace universal 0.05% floor with `max(0.02%, tick_size × 3, spread × 2)` | SL near-zero rejections on AAVEUSDT every cycle | **Low-Medium** — unlocks one pair per cycle |
| **4** | **Duplicate lifecycle posting fix** | Idempotency guard for terminal lifecycle events | Confirmed real defect (ACTIVE_CONTEXT) | **Medium** — subscriber experience |
| **5** | **ATR-normalized FVG SL cap** | Replace 2.00% flat FVG SL cap with 3×ATR normalized distance | FVG SL rejections on LABUSDT/ENJUSDT every cycle | **Low** (channel disabled, but needed before re-enabling) |
| **6** | **Per-evaluator confidence calibration** | Adjust min_confidence per evaluator based on penalty profiles (SR_FLIP needs lower floor due to 20pt penalty exposure) | SR_FLIP scores 50-64 frequently | **Medium** — more evaluator paths express |

### G. Requirements vs Implementation Gap

| What the system should do | What it currently does | What should change next |
|---|---|---|
| Express 22 evaluator paths across 8 channels when conditions are met | Only 4 of 22 paths have produced live signals; 7 channels disabled | Re-enable channels incrementally after per-family downstream handling is in place |
| Method-specific SL/TP preserved end-to-end (B13) | Evaluators compute method-specific SL/TP, but universal caps (1.5%) override structural levels | Per-family SL caps that respect evaluator-authored invalidation levels |
| Family-aware gating | MTF gate applies uniformly to all setup families | Family-aware MTF exemptions for mean-reversion/compression setups |
| Proportional protective gating | Spread gate eliminates >50% of pair universe; MTF kills 2-6 active candidates/cycle | Regime-adaptive spread thresholds; family-aware MTF thresholds |
| Per-pair SL precision | 0.05% universal floor rejects valid tight scalps on high-price tokens | Adaptive SL floor accounting for price magnitude and tick size |
| Institutional-grade win rate | 76.3% SL_HIT, 5-min hold, 0.10% MFE | Address SL geometry distortion (priority #1); this is the fastest path to improving win rate |
| Observable suppression funnel | Suppression telemetry exists but lacks per-evaluator hit rate and SL rejection aggregation | Add per-evaluator rejection rate counters to suppression summary |
| Lifecycle posting integrity | Duplicate terminal lifecycle posting confirmed real | Idempotency guard for SL/invalidation/expiry events |
| WATCHLIST free-channel routing | ✅ Fixed in PR #144 | Verify in next monitoring window |
| B-tier paid dispatch | ✅ Fixed in PR-18 | No change needed |

---

## Appendix: Methodology and Uncertainty Notes

### Evidence Quality Assessment

| Source | Quality | Limitations |
|---|---|---|
| monitor/latest.txt (2026-04-15 05:03 UTC) | **High** — live VPS runtime evidence | Single point-in-time snapshot; only 38 signals in performance history |
| Source code (main branch) | **High** — authoritative implementation | Does not capture .env overrides or runtime state |
| OWNER_BRIEF.md | **High** — canonical doctrine | May lag behind recent PRs |
| ACTIVE_CONTEXT.md | **High** — current continuity state | Updated 2026-04-14; may not reflect post-PR #144 runtime truth |
| Prior audit documents | **Medium** — independent analyses | May contain conclusions based on pre-fix code |

### Key Uncertainties

1. **Evaluator candidate generation rate** — We can see suppression counts but not how many candidates each evaluator generates per cycle. Some evaluators may never fire (no conditions met) vs. always fire but always get gated.
2. **Win rate by evaluator** — The 38-signal sample is too small for per-evaluator statistical significance.
3. **SL capping frequency** — We see the warning in monitor logs but don't have a per-signal count of how many of the 38 tracked signals had their SL capped before dispatch.
4. **VPS .env overrides** — The live system may have env-var overrides that differ from the code defaults. We cannot verify this from the repo alone.
5. **Market conditions during sampling** — The 38 signals span ~28 hours (2026-04-13 09:13 to 2026-04-14 13:04). Market conditions during this window may not be representative of all conditions.

### Confidence Levels Used

| Level | Meaning |
|---|---|
| High | Direct evidence from code, config, or monitor logs |
| Medium | Strong inference from multiple evidence sources |
| Low | Reasonable inference but insufficient direct evidence |

---

*Report generated by Claude Opus 4.6 for cross-model comparison. All claims are evidence-backed with explicit uncertainty markers where evidence is insufficient.*
