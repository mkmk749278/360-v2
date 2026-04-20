# AUDIT_2026-04-20_MARKET_TRUTH_PATH_DATA_SUFFICIENCY_CLAUDE-OPUS-4.6

**Date:** 2026-04-20  
**Auditor:** Claude Opus 4.6 (automated technical audit)  
**Scope:** Full pipeline — data ingress through signal emission, path-by-path evaluation, data sufficiency, SL/TP realism, runtime truth report fidelity  
**Trigger:** Owner observed zero signals in the last 24 hours from any path  
**Standard:** Truth-first. Conclusions grounded in implementation evidence, not plausibility claims.

---

## 1. Executive conclusion

**The zero-signal window is most likely caused by a combination of three interacting factors, ranked by confidence:**

1. **Overwhelming gate cascade suppression (~40% weight).** The system stacks 8+ independent hard gates after evaluator generation. Each gate is individually reasonable, but they compose multiplicatively. A signal must survive: evaluator conditions → setup/regime compatibility → execution quality → MTF confluence (min 0.20–0.60) → cross-asset gate → SMC hard gate (min 12.0) → trend hard gate (min 10.0) → soft penalty accumulation → confidence floor (65+) → risk geometry validation → R:R floor (1.0–1.3) → SL cap (1.0–1.5%) → router stale/cooldown gates. The probability of any single signal clearing all these simultaneously in a low-conviction market is structurally very low.

2. **Market truth: the crypto market in April 2026 may be in a low-directional, compressed-range state (~30% weight).** Many paths require trending conditions (TREND_PULLBACK_EMA, CLS, PDC), large volatility events (LIQUIDATION_REVERSAL, WHALE_MOMENTUM), or structural breakouts (VOLUME_SURGE_BREAKOUT, QUIET_COMPRESSION_BREAK). If the market is ranging with moderate ADX (18–24) and no extreme funding/OI, the majority of evaluator-level conditions literally cannot fire. This is a legitimate explanation — but we cannot confirm it from code alone.

3. **Channel rollout lockdown narrows the live universe to effectively 2 channels (~30% weight).** Out of 8 channels, only `360_SCALP` (full_live) and `360_SCALP_DIVERGENCE` (limited_live, pilot symbols only) are enabled. The other 6 are `disabled` or `radar_only`. This means only 14 evaluators on the main scalp channel and 1 evaluator on divergence (for a handful of pilot symbols) can generate live signals. The auxiliary channels that might fire on different market conditions (VWAP bounce, Ichimoku cross, Supertrend flip, CVD divergence, FVG retest, Orderblock entry) are all turned off for live dispatch.

**Bottom line:** The system is working as coded — it is extremely selective by design, and when market conditions don't present clear setups across the narrow live surface, silence is the expected output. But the *degree* of selectivity may be excessive for live operation, and the rollout lockdown further narrows the already narrow funnel.

---

## 2. What the system is actually doing

### 2.1 End-to-end architecture

```
Bootstrap (historical seeding: 500 candles × 6 timeframes per pair)
    ↓
PairManager (fetch top futures pairs, classify into Tier 1/2/3)
    ↓
WebSocket Manager (kline + trade + forceOrder streams for Tier 1)
    ↓
Scanner.scan_loop() — every cycle:
    ├── For each symbol (Tier 1 every cycle, Tier 2 every 3rd, Tier 3 every 6th):
    │   ├── _build_scan_context(): fetch candles, compute indicators, SMC data, regime
    │   ├── For each ENABLED channel:
    │   │   ├── _should_skip_channel(): pre-filter (spread, volume, cooldown, blacklist, regime)
    │   │   ├── channel.evaluate(): run evaluator(s) → Signal or None
    │   │   ├── _prepare_signal(): run gate chain:
    │   │   │   ├── Setup/regime compatibility check
    │   │   │   ├── Execution quality check
    │   │   │   ├── MTF confluence gate (hard block if below min_score)
    │   │   │   ├── Family-semantic MTF rescue (reclaim_retest/reversal only)
    │   │   │   ├── Regime penalty multiplier (0.6–1.8×)
    │   │   │   ├── Soft gates: VWAP extension, kill zone, OI, spoof, volume divergence, cluster
    │   │   │   ├── Cross-asset gate (BTC trend alignment)
    │   │   │   ├── build_risk_plan(): SL/TP geometry + RR validation
    │   │   │   ├── SMC hard gate (min 12.0 for sweep-based setups)
    │   │   │   ├── Trend hard gate (min 10.0 for EMA-based setups)
    │   │   │   ├── Confidence floor check (65 for SCALP in normal; 65 in QUIET)
    │   │   │   ├── Risk assessment: RR floor, position sizing, concurrent limits
    │   │   │   └── Confidence decay (staleness penalty after 60–120s)
    │   │   └── If signal survives: enqueue to SignalQueue
    │   └── (next channel)
    └── (next symbol)
         ↓
SignalRouter: polls queue → applies router-level gates:
    ├── Correlation lock (no duplicate symbols)
    ├── Per-channel cooldown (60s default)
    ├── Per-channel concurrent cap (5 max)
    ├── Stale signal gate (120s for SCALP)
    ├── TP/SL direction sanity
    └── Dispatch to Telegram
         ↓
TradeMonitor: polls live prices → manages TP/SL/trailing → records outcomes
```

### 2.2 Active channels at code default

| Channel | Enabled | Rollout State | Live Signal? |
|---------|---------|---------------|-------------|
| `360_SCALP` | **True** | **full_live** | **YES** |
| `360_SCALP_DIVERGENCE` | **True** | **limited_live** | **YES (pilot symbols only)** |
| `360_SCALP_FVG` | False | radar_only | No (radar only) |
| `360_SCALP_ORDERBLOCK` | False | radar_only | No (radar only) |
| `360_SCALP_CVD` | False | disabled | No |
| `360_SCALP_VWAP` | False | disabled | No |
| `360_SCALP_SUPERTREND` | False | disabled | No |
| `360_SCALP_ICHIMOKU` | False | disabled | No |

**Impact:** Only `360_SCALP` with its 14 evaluators and `360_SCALP_DIVERGENCE` with 1 evaluator are generating live signals. The 6 other channels that cover mean-reversion, order-block entries, CVD divergence, Supertrend flips, Ichimoku crosses, and VWAP bounces are all shut off.

### 2.3 The gate cascade depth

Counting unique hard gates a signal from `360_SCALP` must pass to reach Telegram:

1. Pre-scan: blacklist, volume floor, paused, cooldown
2. Channel skip: tier exclusion, spread gate, volume gate, volatile unsuitable, circuit breaker, active signal exists, RANGING+ADX<15
3. Evaluator internal: ~5-12 hard conditions per path (data sufficiency, pattern detection, RSI gates, momentum gates, SMC confluence, regime compatibility)
4. Setup compatibility: channel+regime matrix
5. Execution quality: structural entry checks
6. MTF confluence: weighted EMA alignment across timeframes (min 0.20–0.60)
7. Cross-asset: BTC trend alignment
8. Risk geometry: SL cap (1.0–1.5%), min SL distance (0.03–0.05%), RR floor (0.8–1.3), TP ordering
9. SMC hard gate: min score 12.0 (non-exempt setups only)
10. Trend hard gate: min score 10.0 (non-exempt setups only)
11. Confidence floor: min 65 (SCALP channel)
12. Router: staleness (120s), cooldown (60s), concurrent cap (5), direction sanity
13. Risk assessment: concurrent limits, order book check

**Conservative estimate:** A signal faces 20-30 independent conditions. If each condition has even 80% pass rate, the compound probability is 0.8^25 ≈ 0.4%. In low-conviction markets, individual pass rates drop to 50-60%, making compound pass rate negligible.

---

## 3. Path-by-path audit

### 3.1 Path audit table

| # | Path | Setup Class | Thesis | Primary TF | Min Data | Regime Requirement | Key Hard Gates | SMC Exempt? | Trend Exempt? | SL Construction | TP Construction | Likely Blind Spots | Verdict |
|---|------|------------|--------|------------|----------|-------------------|----------------|-------------|---------------|-----------------|-----------------|-------------------|---------|
| 1 | Standard | LIQUIDITY_SWEEP_REVERSAL | M5 sweep reversal with momentum confirmation | 5m | 50 candles + sweeps | Any (ADX floor relaxed in RANGING/QUIET) | ADX≥12-20, sweep exists, momentum persistent for 2+ candles, momentum direction match, EMA alignment, MACD in strict regimes, 1h EMA/RSI MTF, HTF EMA200 rejection | No | No | Swept level ±0.1% buffer; fallback 0.5×ATR | TP1: nearest FVG; TP2: 20-candle swing; TP3: 4.0R | Requires sweep+momentum+EMA+MACD+MTF alignment simultaneously. In sideways markets this conjunction is extremely rare | **Plausible but very selective** |
| 2 | Trend Pullback | TREND_PULLBACK_EMA | EMA pullback in trending market | 5m | 50 candles + EMA50 | TRENDING_UP/DOWN only | EMA9>EMA21>EMA50 (or inverse), price within 0.3% of EMA9 or 0.5% of EMA21, RSI 40-60, RSI direction match, last candle direction, momentum positive, FVG or OB exists | Yes | No | max(0.05%, 1.1×EMA21 dist, 0.5×ATR) | TP1: 20-candle swing; TP2: 4h swing; TP3: 4.0R | **Only fires in TRENDING_UP/TRENDING_DOWN regimes.** If the regime detector classifies the market as RANGING, VOLATILE, or QUIET, this path is completely dead. Also requires FVG or orderblock presence for confirmation | **Dead in non-trending** |
| 3 | Liquidation Reversal | LIQUIDATION_REVERSAL | Cascade exhaustion + CVD divergence contrarian entry | 5m | 20 candles + CVD data + FVG/OB | Any | 3-candle cascade ≥2.0%, CVD divergence present, RSI ≤25 or ≥75, price within 0.5% of FVG/OB zone, volume spike ≥2.5× average | Yes | Yes | Cascade extreme - 2×ATR | TP: ratio-based 1.5R/2.5R/4.0R | **Requires extreme conditions:** 2% cascade + RSI extremes + CVD divergence + volume spike + zone proximity. This setup fires maybe once per week in a single pair. Requires live CVD data which depends on buy/sell volume disaggregation | **Extremely rare by design** |
| 4 | Whale Momentum | WHALE_MOMENTUM | Large tick delta + OBI imbalance on 1m | 1m | 10 candles + live ticks + L2 book | NOT QUIET | Tick volume ≥$500K, buy/sell ratio ≥2.0×, RSI gate, OBI ≥1.5 (or 1.2 in fast regimes) | Yes | Yes | 5-candle 1m swing ±0.1% buffer | TP: 0.5R/1.0R/1.5R (very tight) | **Depends on live tick data and L2 order book.** If `smc_data["recent_ticks"]` or `smc_data["order_book"]` is not populated from WebSocket, this path silently returns None. The $500K total volume requirement is reasonable for BTC/ETH but may exclude many altcoins | **Data-dependent; likely silent without WS tick data** |
| 5 | Volume Surge Breakout | VOLUME_SURGE_BREAKOUT | Breakout above 20-candle high/low with volume confirmation | 5m | 21 candles | NOT QUIET | Close > 20-candle high (or < low), volume ≥1.3× avg, RSI gate, FVG/OB hard gate in calm regimes | No | No | 20-candle low/high ±0.3×ATR | TP: FVG-based or ratio 1.5R/2.5R/4.0R | Requires actual breakout of a 20-candle range. In sideways ranging markets, these breakouts may occur but then fail — the evaluator doesn't check for false breakout | **Plausible in trending; requires real breakout** |
| 6 | Breakdown Short | BREAKDOWN_SHORT | Breakdown below 20-candle low with bearish volume | 5m | 21 candles | NOT QUIET | Similar to Volume Surge Breakout but SHORT-only | No | No | Similar inverse logic | Similar inverse logic | Same as Volume Surge but only SHORT direction | **Plausible in bear moves** |
| 7 | Opening Range Breakout | OPENING_RANGE_BREAKOUT | 1h opening range breakout on 5m/15m | 1h + 5m/15m | 1h range definition + 5m candles | Any | Opening range identification, breakout detection, volume confirmation | Yes | No | Range-based | Range-based | **Requires specific time windows** (first 1-2 hours of a session). Only fires during opening range formation windows | **Session-dependent; fires rarely** |
| 8 | SR Flip Retest | SR_FLIP_RETEST | Support→resistance flip followed by retest rejection | 5m | 55 candles | NOT VOLATILE | Prior swing identification in [-50:-9], flip confirmation in [-9:-1], price returned within 0.6% of level, rejection candle quality, RSI gate, FVG/OB in calm regimes | Yes | No | Beyond flip level + buffer; adaptive structural invalidation | TP: structural or ratio 1.0R/2.0R/3.0R | Requires a genuine structural flip (close acceptance above prior resistance) **followed by** a retest to within 0.6%. This is a two-phase setup that takes time to develop. Blocked in VOLATILE regime | **Plausible but needs specific structure development** |
| 9 | Funding Extreme | FUNDING_EXTREME_SIGNAL | Contrarian entry at extreme funding rates | 5m | 5 candles + funding rate + CVD | NOT QUIET | Funding rate > extreme threshold (typically 0.01%), EMA9 alignment, RSI direction, CVD rising, FVG/OB required | Yes | Yes | Liquidation cluster or 1.5×ATR fallback | TP: FVG/OB structure or ratio | **Requires extreme funding rate data.** If `smc_data["funding_rate"]` is not populated (API or WS issue), this silently returns None. Also requires CVD alignment and FVG/OB confluence | **Data-dependent; requires live funding/CVD** |
| 10 | Quiet Compression Break | QUIET_COMPRESSION_BREAK | Low-vol breakout from compression | 5m | 30 candles + BB | **QUIET only** | Bollinger Band breakout, volume confirmation | Yes | No | BB-based | BB-based | **Only fires in QUIET regime.** If regime is anything else, this path is dead. Even in QUIET, requires an actual BB breakout with volume | **Regime-locked to QUIET** |
| 11 | Divergence Continuation | DIVERGENCE_CONTINUATION | RSI/MACD divergence aligned continuation | 5m | Divergence data | Any | Divergence detection, continuation direction alignment | Yes | No | Divergence-based | Ratio-based | Divergence detection needs sufficient RSI/MACD history and clear pivot points. Hidden divergence in ranging is rare | **Moderate; divergence detection is finicky** |
| 12 | Continuation Liq Sweep | CONTINUATION_LIQUIDITY_SWEEP | Sweep in trend direction | 5m | 20 candles + sweeps | TRENDING_UP/DOWN/STRONG_TREND/WEAK_TREND/BREAKOUT only | Sweep within 10 candles, direction matches trend, momentum persistence, RSI gate | Yes | No | Swept level + buffer | Ratio 1.5R/2.5R/4.0R | **Requires trending regime + recent sweep.** Dead in RANGING/QUIET/VOLATILE | **Dead in non-trending** |
| 13 | Post Displacement Continuation | POST_DISPLACEMENT_CONTINUATION | Displacement → consolidation → re-acceleration | 5m | 50 candles | TRENDING/STRONG_TREND/WEAK_TREND/BREAKOUT | Displacement candle (body≥60%, vol≥2.5×avg), 2-5 bar consolidation (range≤50% of displacement), re-acceleration | Yes | No | Below displacement low (LONG) | Ratio-based | **Three-phase detection is extremely demanding.** Requires a big candle → tight consolidation → breakout in sequence. This is a rare pattern even in trending markets | **Very rare by design** |
| 14 | Failed Auction Reclaim | FAILED_AUCTION_RECLAIM | Failed breakout reclaim (contrarian) | 5m | 50 candles | NOT VOLATILE/STRONG_TREND | Prior swing level, failed auction within 1-7 bars (close within 0.2% of level), reclaim with min ATR distance, conservative RSI gate | Yes | Yes | Beyond failed auction level + 2×ATR | Ratio 1.0R/2.0R/3.0R | **Requires specific failed breakout pattern** — a breakout that fails to close convincingly beyond the level, followed by a reclaim back. Conservative RSI gates (75/25 hard caps). Blocked in STRONG_TREND where breakouts are genuine, and in VOLATILE where auctions are messy | **Rare; well-designed but demanding** |

### 3.2 Path regime dependency summary

| Regime | Paths that CAN fire | Paths that CANNOT fire |
|--------|--------------------|-----------------------|
| **TRENDING_UP** | 1,2,3,4,5,6,7,8,11,12,13,14 (12 paths) | 10 (QUIET only) |
| **TRENDING_DOWN** | 1,2,3,4,5,6,7,8,11,12,13,14 (12 paths) | 10 (QUIET only) |
| **RANGING** | 1,3,7,8,11,14 (6 paths) | 2,12,13 (trending only); 4,5,6 (not QUIET but ADX<15 blocks SCALP); 10 (QUIET only) |
| **VOLATILE** | 1,2,3,4,5,6,7,11,12,13 (10 paths) | 8 (blocked), 10 (QUIET only), 14 (blocked) |
| **QUIET** | 1,3,7,8,10,11,14 (7 paths) | 2,12,13 (trending only); 4,5,6,9 (blocked in QUIET) |

**Key finding:** In RANGING regime, the ADX<15 hard block for SCALP channel suppresses ALL 14 paths if ADX is below 15. This means a choppy, directionless market with low ADX effectively blocks 100% of signal generation from the only live channel.

### 3.3 Data dependency risk matrix

| Data Source | Paths Affected | Risk if Missing |
|-------------|---------------|-----------------|
| `smc_data["sweeps"]` | 1, 12 | No sweep → no signal from these paths |
| `smc_data["fvg"]` + `smc_data["orderblocks"]` | 1,2,3,5,6,8,9 (as hard gate) | No FVG AND no OB → blocked in calm regimes |
| `smc_data["cvd"]` | 3, 9 | No CVD → liquidation reversal and funding extreme dead |
| `smc_data["funding_rate"]` | 9 | No funding → funding extreme dead |
| `smc_data["recent_ticks"]` | 4 | No ticks → whale momentum dead |
| `smc_data["order_book"]` | 4 | No L2 data → whale momentum dead |
| `smc_data["whale_alert"]` | 4 | No whale flag → whale momentum may still fire on ticks |
| `candles["1h"]`, `candles["4h"]` | 1 (EMA200 rejection), 2 (TP2), 7 (ORB range) | No higher-TF data → degraded or blocked |
| MTF indicator data (EMA9/EMA21 per TF) | ALL (MTF gate) | Missing TFs → lower MTF score → more blocking |

---

## 4. Data sufficiency and warmup truth

### 4.1 What gets seeded at boot

From `config/__init__.py:340-347`:
```python
SEED_TIMEFRAMES = [
    TimeframeSeed("1m", 500),   # 500 × 1min = ~8.3 hours
    TimeframeSeed("5m", 500),   # 500 × 5min = ~41.7 hours (~1.7 days)
    TimeframeSeed("15m", 500),  # 500 × 15min = ~125 hours (~5.2 days)
    TimeframeSeed("1h", 500),   # 500 × 1h = ~20.8 days
    TimeframeSeed("4h", 500),   # 500 × 4h = ~83.3 days (~2.8 months)
    TimeframeSeed("1d", 500),   # 500 × 1d = ~1.4 years
]
```
Plus `SEED_TICK_LIMIT = 5000` recent trades.

### 4.2 Indicator warmup requirements

| Indicator | Minimum Candles | Seeded (5m) | Sufficient? |
|-----------|-----------------|-------------|-------------|
| EMA9 | 9 | 500 | ✅ Yes |
| EMA21 | 21 | 500 | ✅ Yes |
| EMA50 | 50 | 500 | ✅ Yes |
| EMA200 | 200 | 500 | ✅ Yes (barely) |
| ADX(14) | 28 | 500 | ✅ Yes |
| RSI(14) | 15 | 500 | ✅ Yes |
| ATR(14) | 15 | 500 | ✅ Yes |
| MACD(12,26,9) | 35 | 500 | ✅ Yes |
| Bollinger(20) | 20 | 500 | ✅ Yes |
| Ichimoku | 78 | 500 | ✅ Yes |
| **Full suite** | **50** | 500 | ✅ Yes |

### 4.3 SMC warmup requirements

| Feature | Min Candles | Seeded (5m) | Sufficient? |
|---------|-------------|-------------|-------------|
| Liquidity sweeps (lookback=50) | 51 | 500 | ✅ Yes |
| MSS | 2 LTF candles | 500 | ✅ Yes |
| FVG (lookback=10) | 12 | 500 | ✅ Yes |
| Continuation sweep | 12 | 500 | ✅ Yes |

### 4.4 Order flow warmup

| Feature | Data Source | Warmup Need | Available? |
|---------|-------------|-------------|-----------|
| OI trend | OI snapshots (200 deque) | 2+ snapshots | **Runtime-dependent:** OI is populated from live polling/WS, not historical seeding. After boot, it takes time to accumulate snapshots |
| CVD | Buy/sell volume disaggregation | 20+ candles | **Runtime-dependent:** CVD depends on `recent_ticks` trade data. 5000-tick seed helps but buy/sell disaggregation quality depends on tick-level data |
| Liquidation events | forceOrder WS stream | None (event-driven) | **Runtime-dependent:** Liquidation data comes from WebSocket. If no liquidations occur, the deque is empty |
| Funding rate | REST/WS polling | Single snapshot | **Runtime-dependent:** Requires Binance funding rate API call |

### 4.5 Warmup insufficiency risk assessment

**Static data (candles, indicators):** ✅ **Sufficient.** 500 candles per timeframe exceeds all indicator warmup requirements.

**Dynamic data (order flow, CVD, OI, funding, L2, ticks):** ⚠️ **Partially insufficient at boot, improving over time.**
- OI: accumulates at ~1 snapshot/minute → 200 snapshots in ~3.3 hours
- CVD: available from seed ticks, but quality depends on tick data completeness
- Funding: single snapshot, refreshed periodically — usually available quickly
- L2 order book: snapshot data, not historical — available from first REST call
- Live ticks: accumulate from WS trades stream — may take minutes to be representative

**Key finding:** The system's order-flow-dependent paths (LIQUIDATION_REVERSAL, WHALE_MOMENTUM, FUNDING_EXTREME) may be effectively dead for the first 1-3 hours after a restart while dynamic data accumulates. However, for a 24-hour zero-signal window, this is not the primary explanation unless the system was recently restarted.

---

## 5. How market features are computed

### 5.1 Support/Resistance (`structural_levels.py`)

- **Swing Highs/Lows:** Local extrema within ±3 candle window over 20-candle lookback
- **Round Numbers:** Price-magnitude-aware rounding
- **Used in:** SL adjustment, TP targeting, SR_FLIP_RETEST level identification
- **Limitation:** Simple local maxima/minima — no volume profile, no order book depth awareness. Structurally sound but can miss significant levels that are significant due to volume, not just price extremes

### 5.2 EMA / Moving Averages (`indicators.py`)

- **Computed:** EMA9, EMA21, EMA50, EMA200 (SMA fallback when insufficient data)
- **Used in:** Trend alignment (EMA9 > EMA21 > EMA50), pullback proximity, MTF confluence, HTF rejection
- **MTF (`mtf.py`):** Classifies each TF as BULLISH/BEARISH/NEUTRAL based on EMA fast > slow AND close > EMA fast. Weighted by timeframe (1m: 0.5, 5m: 1.0, 15m: 1.5, 1h: 2.0, 4h: 3.0). Score = weighted alignment ratio
- **Limitation:** MTF uses EMA9/EMA21 alignment only — no ADX, no momentum, no candle structure. A market that is in a slow grind up on higher TFs but range-bound on 5m can pass MTF for LONG but fail the evaluator's own momentum gates

### 5.3 Volume (`confidence.py:222-241`)

- **Computed:** 24h volume in USD, compared to $5M threshold for SCALP channels
- **Used in:** Confidence liquidity score (0-20 points), filter_module probability scoring
- **Limitation:** Volume is a 24h aggregate — does not detect intraday volume surges vs. lulls. The evaluator-level volume spike checks (e.g., ≥1.3× or ≥2.5× average) use candle-level volume arrays which are more granular

### 5.4 Trend / Regime (`regime.py`)

- **Regime classification:** TRENDING_UP/DOWN, RANGING, VOLATILE, QUIET
- **Key thresholds:** ADX≥25 for trending, BB width >5% for volatile, <1.2% for quiet
- **Hysteresis:** 3-candle dwell prevents flapping between regimes
- **Limitation:** Single timeframe regime detection (typically 5m). A market can be trending on 1h but ranging on 5m. The regime classification drives path availability but doesn't incorporate multi-timeframe regime context. Volume delta override can force regime changes but this is a heuristic

### 5.5 Momentum / MACD (`indicators.py`, evaluator-level)

- **MACD:** Standard (12,26,9) with histogram
- **Momentum:** Percentage price change over N candles
- **Used in:** Evaluator-level confirmation (momentum > threshold, MACD histogram direction), confidence scoring
- **Limitation:** Momentum threshold is ATR-adaptive (`max(0.10, min(0.30, atr_pct * 0.5))`) which is well-designed. However, in low-ATR environments, the floor of 0.10% momentum may still be relatively demanding

### 5.6 SMC constructs (`smc.py`)

- **Liquidity Sweeps:** Wicks that pierce recent highs/lows and close back inside. Tolerance ±0.05%, volume filter ≥1.2× average, micro-sweep filter at 0.02%
- **MSS (Market Structure Shift):** Lower-TF close breaking structural body after sweep
- **FVG (Fair Value Gap):** Three-candle imbalance gap, min 0.01% width, max 80-candle age, 75% fill rejection
- **Continuation Sweep:** Sweep in trend direction distinguished from reversal sweep
- **Limitation:** Sweeps require clean wick structures. In messy, choppy markets with many false wicks, the micro-sweep filter (0.02%) may be too loose, generating false sweep detections that then fail downstream momentum/EMA gates. Conversely, in compressed markets, sweeps may be too small to detect

### 5.7 Order Flow (`order_flow.py`, `cvd.py`, `oi_filter.py`)

- **OI Trend:** Rising/falling/neutral with 0.5% change threshold
- **OI Invalidation:** Rising OI >1% contradicting signal direction
- **CVD Divergence:** Price LL + CVD HL (bullish) or Price HH + CVD LH (bearish), 20-candle lookback
- **Squeeze Detection:** OI falling + liquidation volume present
- **Funding Rate:** Extreme threshold at 0.01% (0.3% annualized)
- **Limitation:** OI history is a deque of 200 entries — about 3 hours at 1-min polling. CVD depends on buy/sell volume disaggregation which is only accurate with tick-level data. Funding rate is 8-hourly; extreme readings are rare outside leverage washout events

### 5.8 Cross-Asset Context (`cross_asset.py`)

- **BTC trend alignment:** Graduated correlation-aware filtering. LONG hard-blocked when BTC dumps (corr≥0.8, dump ≥-1.5%)
- **Default BTC correlation:** 0.7 when unavailable
- **Market tone:** RISK_ON/RISK_OFF/VOLATILE/NEUTRAL
- **Limitation:** Fails open when no asset states provided (returns `True, "", 0.0`). This means if BTC context data isn't populated, the cross-asset gate provides no protection — but also doesn't block. The 0.7 default correlation is conservative and may over-gate altcoins with genuinely low BTC correlation

---

## 6. SL/TP realism vs crypto market truth

### 6.1 SL cap analysis

| Channel | Max SL % | Crypto Market Reality |
|---------|----------|----------------------|
| 360_SCALP | 1.5% | **Tight for most altcoins.** BTC 1.5% = ~$1,500 at $100K. Reasonable for BTC/ETH. For altcoins with 5-10% daily ranges, a 1.5% SL will be hit by normal noise within minutes |
| 360_SCALP_FVG | 1.0% | **Very tight.** Almost certainly noise-level for anything outside BTC/ETH |
| 360_SCALP_DIVERGENCE | 1.0% | **Very tight** |
| 360_SCALP_ICHIMOKU | 1.2% | **Tight** |

### 6.2 Protected structural SL vs. cap

Setups in `STRUCTURAL_SLTP_PROTECTED_SETUPS` (10 of 14 paths) have their evaluator-authored SL geometry preserved. If the evaluator's structural SL exceeds the channel cap, the signal is **REJECTED, not compressed** (reject-not-compress policy, `signal_quality.py:371-373`).

**Impact:** If an evaluator places SL at a structurally meaningful level that happens to be 1.8% away from entry (e.g., below a swing low), the signal is rejected entirely. The evaluator's thesis was sound but the risk geometry is too wide for the channel's cap. This is a correctness-preserving but signal-suppressing design — it prioritizes risk discipline over signal volume.

### 6.3 R:R floor analysis

| Setup Family | Min R:R | Impact |
|--------------|---------|--------|
| Range rejection/fade | 0.8 | Reasonable for mean-reversion |
| Mean reversion (liq/funding) | 0.9 | Reasonable |
| Structural (SR flip/reclaim) | 1.0 | Reasonable for high-conviction structural |
| All others (default) | 1.2 | Moderate |
| Unknown/legacy | 1.3 | Conservative |

**Key finding:** The R:R floor interacts with the SL cap. If SL is capped at 1.5% and R:R must be ≥1.0, then TP1 must be ≥1.5% away from entry. For a 5-minute scalp, this means the target must be a 1.5%+ move — achievable for BTC but demanding for many altcoins in low-vol environments.

### 6.4 SL construction per-path realism

| Path | SL Logic | Realistic? |
|------|----------|-----------|
| LIQUIDITY_SWEEP_REVERSAL | Swept level ±0.1% | ✅ Structurally anchored but may be too tight — sweeps often retest |
| TREND_PULLBACK_EMA | max(0.05%, 1.1×EMA21 dist, 0.5×ATR) | ✅ Multi-factor floor. EMA21 distance provides structural meaning |
| LIQUIDATION_REVERSAL | Cascade extreme - 2×ATR | ✅ Wide enough for reversal plays. May exceed 1.5% cap → rejection |
| WHALE_MOMENTUM | 5-candle 1m swing ±0.1% | ⚠️ Very tight (1m timeframe). Noise will trigger SL frequently |
| VOLUME_SURGE_BREAKOUT | 20-candle low/high ±0.3×ATR | ✅ Reasonable for breakout plays |
| SR_FLIP_RETEST | Adaptive structural invalidation: max(level×0.0015, ATR×0.35, wick_overshoot+ATR×0.15) | ✅ Well-designed, structurally anchored |
| FUNDING_EXTREME | Liquidation cluster or 1.5×ATR | ✅ Reasonable for contrarian |
| QUIET_COMPRESSION_BREAK | BB-based | ✅ Reasonable for breakout |
| POST_DISPLACEMENT_CONTINUATION | Below displacement low + floor | ⚠️ Displacement candles are large → SL may exceed cap → rejection |
| FAILED_AUCTION_RECLAIM | Beyond failed auction + 2×ATR | ⚠️ Conservative 2×ATR buffer may exceed cap → rejection |

### 6.5 The SL cap / reject-not-compress tension

**This is the most important SL finding:** Paths that generate structurally meaningful but wide SLs (LIQUIDATION_REVERSAL, POST_DISPLACEMENT_CONTINUATION, FAILED_AUCTION_RECLAIM) will frequently produce SL distances that exceed the 1.5% channel cap. Under the reject-not-compress policy, these signals are discarded entirely — the system correctly refuses to compress a wide structural SL into an artificial tight SL, but the consequence is that these paths may effectively never emit signals in high-volatility environments where their thesis is strongest.

---

## 7. Runtime truth report limitations

### 7.1 How the report is built

The runtime truth report (`src/runtime_truth_report.py`, `scripts/build_truth_report.py`) is constructed from:
1. **Performance JSON:** Closed trade records with outcomes (TP/SL labels)
2. **Log parsing:** Current and previous cycle logs, parsed for funnel stage counters (evaluator_attempted, generated, gated, emitted)
3. **Runtime health JSON:** Engine status, heartbeat age
4. **Heartbeat text:** Last heartbeat output

It uses `build_snapshot()` to produce:
- Path funnel metrics per-setup
- Quality by setup (win rate, SL rate, avg PnL)
- Lifecycle metrics (median breach time, terminal duration)
- Health summary (healthy/stale/unhealthy)

### 7.2 What it CAN prove

- **Whether the engine is running** (heartbeat age check, ≤120s = healthy)
- **Funnel-stage truth:** Where signals die in the pipeline (evaluator → generated → gated → emitted)
- **Quality by setup:** Win/SL rates and PnL for paths that HAVE emitted signals
- **Geometry preservation:** Whether risk geometry was preserved, changed, or rejected
- **Lifecycle timing:** How quickly signals reach TP or SL

### 7.3 What it CANNOT prove

1. **Why the evaluators returned None.** The report shows `no_signal` counts but not the specific condition that failed within each evaluator. A path with 10,000 attempts and 0 generated tells you it's not firing, but not whether it's ADX, sweep absence, RSI, EMA alignment, or data absence that's blocking it
2. **Whether data was actually available.** The report doesn't track whether `smc_data["cvd"]` was populated, whether L2 book data was present, or whether funding rate was stale. Paths that silently return None on missing data look the same as paths that evaluated and found no setup
3. **Real-time market conditions.** The report doesn't include the actual regime classification, ADX values, EMA states, or market structure at the time of scanning. It's a post-hoc aggregation that cannot reconstruct what the market was doing during the zero-signal window
4. **Suppression reason breakdown.** While `suppression_telemetry.py` tracks reasons, the truth report's funnel is limited to pipeline stages, not per-gate details. A signal gated by MTF looks the same as one gated by setup incompatibility

### 7.4 How it can show stale/empty windows despite a healthy engine

The report uses heartbeat age ≤120s as "healthy." A engine that is running, scanning pairs, and rejecting 100% of evaluator candidates at the evaluator level will show:
- **Health:** HEALTHY (heartbeat is fresh)
- **Funnel:** evaluator_attempted: 50,000; no_signal: 50,000; generated: 0; gated: 0; emitted: 0
- **Quality:** No data (no outcomes to analyze)
- **Lifecycle:** No data

This looks like a perfectly healthy engine with zero output — which is accurate but doesn't tell the owner *why* all 50,000 attempts returned None. The report is truthful but not diagnostic for the zero-signal case.

### 7.5 Window comparison limitations

The `compare_windows()` function compares current vs. previous lookback windows. If both windows are empty, the comparison shows zero deltas everywhere — a flat line that reveals nothing. The comparison is only useful when at least one window has data.

---

## 8. Ranked causes of the no-signal window

Ranked from strongest to weakest explanation based on implementation evidence:

### Rank 1: Gate cascade compound filtering (Confidence: HIGH)

**Evidence:** The system applies 20-30 independent hard gates to each signal candidate. Even with individually generous pass rates, the compound probability of clearing all gates simultaneously is very low. The code evidence shows:
- MTF gate with regime-specific min_score (0.20-0.60)
- SMC hard gate (min 12.0)
- Trend hard gate (min 10.0)
- SL cap (1.5%) with reject-not-compress policy
- R:R floor (1.0-1.3)
- Confidence floor (65)
- Kill zone, spread, volume, regime, execution quality, cross-asset gates

Even in a "normal" market, the compound pass rate through this cascade is structurally low. In a market that is ranging or low-conviction, it approaches zero.

### Rank 2: Market conditions not matching any live path (Confidence: HIGH)

**Evidence:** The majority of paths have strict regime requirements:
- TREND_PULLBACK_EMA: TRENDING only
- CONTINUATION_LIQUIDITY_SWEEP: TRENDING only
- POST_DISPLACEMENT_CONTINUATION: TRENDING only
- QUIET_COMPRESSION_BREAK: QUIET only
- WHALE_MOMENTUM: NOT QUIET
- FUNDING_EXTREME: NOT QUIET
- BREAKDOWN_SHORT: NOT QUIET
- VOLUME_SURGE_BREAKOUT: NOT QUIET
- SR_FLIP_RETEST: NOT VOLATILE

In a RANGING market with ADX 18-24, paths 2, 12, 13 are dead (trending only), path 10 is dead (quiet only), and the RANGING + ADX < 15 hard block kills ALL SCALP paths if ADX drops below 15. The remaining paths (1, 3, 7, 8, 11, 14) still face their own demanding conditions.

### Rank 3: Channel rollout lockdown (Confidence: HIGH)

**Evidence:** Only 2 of 8 channels are live. The 6 disabled channels cover different market conditions:
- `SCALP_VWAP`: Mean-reversion in RANGING/QUIET — could fire when other paths can't
- `SCALP_CVD`: CVD divergence — different thesis from main scalp
- `SCALP_FVG`: FVG retest — structural approach
- `SCALP_ORDERBLOCK`: Order block entry — institutional footprint
- `SCALP_SUPERTREND`: Trend following — complements pullback
- `SCALP_ICHIMOKU`: Cloud-based — different perspective

Enabling these wouldn't guarantee signals, but it would meaningfully expand the surface area of market conditions that can generate candidates.

### Rank 4: Order flow data insufficiency (Confidence: MEDIUM)

**Evidence:** Paths 3 (LIQUIDATION_REVERSAL), 4 (WHALE_MOMENTUM), and 9 (FUNDING_EXTREME) depend on live order flow data (CVD, ticks, funding rate, L2 book) that is not historically seeded. If:
- WebSocket forceOrder stream is not delivering liquidation events (normal in calm markets)
- CVD disaggregation is not working reliably
- Funding rate polling is not functioning
- L2 order book snapshots are stale

Then 3 of 14 paths are silently dead regardless of market conditions. We cannot determine this from code alone — it's a runtime question.

### Rank 5: SL cap rejection suppressing structural setups (Confidence: MEDIUM)

**Evidence:** The reject-not-compress policy means any protected structural setup whose SL exceeds 1.5% is rejected entirely. In volatile conditions where structural SLs are wider, this creates a paradox: the setup thesis is valid (big move, clear structure), but the risk geometry exceeds the channel's risk budget, so the signal is killed. Affected paths: LIQUIDATION_REVERSAL, POST_DISPLACEMENT_CONTINUATION, FAILED_AUCTION_RECLAIM.

### Rank 6: Confidence floor / soft penalty accumulation (Confidence: MEDIUM)

**Evidence:** The confidence floor is 65 for SCALP. Soft penalties accumulate from:
- VWAP extension: up to 12.0 × regime_mult
- Kill zone: up to 10.0 × regime_mult
- OI: up to 15.0 × regime_mult
- Volume divergence: up to 10.0 × regime_mult
- Cluster: up to 12.0 × regime_mult
- Spoof: up to 10.0 × regime_mult

In QUIET regime, regime_mult = 1.8, so penalties are amplified. A signal that starts at 72 confidence and encounters kill zone (-10 × 1.8 = -18) drops to 54, below the 65 floor.

### Rank 7: Statistical filter historical penalty (Confidence: LOW)

**Evidence:** The statistical filter tracks rolling win rate over 30 outcomes. Historical data shows 75% SL rate from previous live operation. If the stat filter has accumulated enough bad outcomes, it could hard-suppress (<25% WR) or soft-penalize (<45% WR) certain (channel, pair, regime) combos. However, this requires ≥15 samples, so it may not be populated for all pairs.

### Rank 8: Circuit breaker tripped (Confidence: LOW)

**Evidence:** If the circuit breaker tripped due to 3 consecutive SL, 3 SL/hour, or 5% daily drawdown, ALL signals would be blocked until manual `/resume` or timeout. This would perfectly explain a zero-signal window. However, it's a runtime state we cannot determine from code. The startup grace period is 0 seconds by default, so a fresh boot would not have grace.

### Rank 9: Runtime truth report masking (Confidence: LOW)

**Evidence:** The truth report cannot mask a healthy-but-silent engine — it would accurately show zero emissions. But it cannot explain WHY emissions are zero. The report's window comparison is useless when both windows are empty. This isn't a "masking" issue but a diagnostic gap.

---

## 9. High-value code findings

### Finding 1: MTF gate measures EMA alignment — wrong metric for structural setups
**File:** `src/mtf.py:97-103`, `src/scanner/__init__.py:2896-2981`  
**Issue:** MTF confluence measures `ema_fast > ema_slow AND close > ema_fast` per timeframe. For structural setups like SR_FLIP_RETEST (a structural level play) or LIQUIDATION_REVERSAL (a mean-reversion play), EMA alignment on higher timeframes is **not the correct confluence signal**. A valid SR flip retest at a key level can occur while higher-TF EMAs are neutral or slightly opposed.  
**Impact:** The MTF gate blocks structurally valid signals that happen to form during EMA transitions or range-bound HTF conditions.  
**Mitigation in code:** Family-semantic MTF rescue exists for `reclaim_retest` and `reversal` families (`_SCALP_MTF_SEMANTIC_FAMILIES`), but it requires ≥2 aligned lower TF + ≥1 aligned higher TF + 0 opposed + deficit ≤0.10. This is still EMA-based, just slightly relaxed.

### Finding 2: ADX < 15 hard-blocks ALL SCALP in RANGING
**File:** `src/scanner/__init__.py:2032-2043`  
**Issue:** When regime is RANGING and ADX < 15, the `_should_skip_channel()` function returns skip=True for the entire 360_SCALP channel. This means ALL 14 paths are dead — including paths like SR_FLIP_RETEST and FAILED_AUCTION_RECLAIM whose thesis has nothing to do with ADX level.  
**Impact:** In a choppy, directionless market (classic RANGING + low ADX), zero signals can be generated from any path.  
**Recommendation:** ADX gating should be per-path, not per-channel. Structural and mean-reversion paths don't require directional momentum.

### Finding 3: FVG/OB hard gate in calm regimes eliminates paths without SMC zones
**File:** Multiple evaluators in `src/channels/scalp.py`  
**Issue:** Many paths require FVG or orderblock presence as a hard gate in RANGING/QUIET regimes. If the market hasn't produced clear imbalance zones (tight, choppy action with small candle bodies), then no FVGs form and no orderblocks qualify. This eliminates paths 2, 5, 6, 8, 9 in the very market conditions where mean-reversion setups (which don't need FVGs) should be active.  
**Impact:** Creates a catch-22: calm market → no FVGs → paths blocked → no signals; volatile market → FVGs present but regime blocks other paths.

### Finding 4: Confidence floor + QUIET penalty multiplier = near-impossible pass
**File:** `src/scanner/__init__.py:2998-2999`, `config/__init__.py:1051-1053`  
**Issue:** In QUIET regime, soft penalty multiplier is 1.8× for SCALP channels. A single kill zone penalty (base 10.0) becomes -18.0, and a single OI penalty (base 15.0) becomes -27.0. Starting from a typical base confidence of 72-78, even one soft gate penalty can push below the 65 floor.  
**Impact:** QUIET regime signals face a nearly impossible gauntlet: most paths are already blocked by regime, and the few that survive face amplified penalties.

### Finding 5: WHALE_MOMENTUM TP ratios are unrealistically tight for 1m timeframe
**File:** `src/channels/scalp.py` (WHALE_MOMENTUM TP)  
**Issue:** WHALE_MOMENTUM uses TP1=0.5R, TP2=1.0R, TP3=1.5R. Combined with a 1m-based SL that might be 0.05-0.1% from entry, this means TP1 is only 0.025-0.05% away. On a 1m chart, this is often inside the spread itself.  
**Impact:** Even if WHALE_MOMENTUM generates a signal, the TP targets are so close to entry that they may be inside the bid-ask spread or hit by the first tick against.

### Finding 6: Historical memory note confirms real-world pattern
**Repository memory:** "Live signal engine emits only TREND_PULLBACK_EMA and SR_FLIP_RETEST (2 of 14 paths). 75% SL rate, 0% MFE on SL trades, ~3-minute hold durations."  
**Significance:** This matches the code analysis perfectly. Only 2 of 14 paths have ever generated live signals, and even those have poor performance. The gate cascade is so tight that only the two most common setups can occasionally squeeze through.

### Finding 7: Per-symbol global cooldown of 15 minutes
**File:** `config/__init__.py:1223-1224`  
**Issue:** `GLOBAL_SYMBOL_COOLDOWN_SECONDS = 900` (15 minutes). After ANY channel fires on a symbol, that symbol is locked on ALL channels for 15 minutes. If a valid SR_FLIP_RETEST fires and hits SL in 3 minutes, the same symbol cannot generate another signal from any path for another 12 minutes.  
**Impact:** In a market with few active symbols, this cooldown can lock out the most liquid pairs (BTC, ETH) that have the best chance of generating signals.

### Finding 8: Evaluator-level telemetry gap for no_signal_reason
**File:** `src/channels/scalp.py:256-282`  
**Issue:** The generation telemetry tracks `no_signal_reason` as a counter per evaluator, but many evaluators simply return None without setting a specific reason code. The telemetry captures that the evaluator didn't fire but doesn't record *which condition failed*.  
**Impact:** Runtime diagnostics cannot identify the specific blocking condition within each evaluator. This makes it impossible to distinguish "ADX too low" from "no sweep detected" from "momentum wrong direction."

### Finding 9: MTF_HARD_BLOCK defaults to False — MTF is already double-gated
**File:** `config/__init__.py:1192-1194`  
**Issue:** `MTF_HARD_BLOCK = False` by default, meaning the scanner-level MTF veto is disabled. However, each evaluator also runs its own internal MTF hard gate. Setting this to True would create a double MTF gate. The current False setting means the scanner relies on the evaluator-level MTF gate only.  
**Significance:** This is good design — it avoids double-gating. But it means the MTF gate in `_prepare_signal()` is the *only* MTF gate, and it applies uniformly to all setups regardless of whether their thesis involves multi-timeframe alignment.

### Finding 10: Confidence data_sufficiency scoring expects 500 candles for full credit
**File:** `src/confidence.py:252-256`  
**Issue:** Data sufficiency scores `(candle_count / 500) × 10` points. The first scan cycle after boot has exactly 500 candles (from seeding), so this scores 10/10. But if candle data is trimmed or if gap-fill fails, a pair with only 200 candles scores 4/10, losing 6 confidence points.  
**Impact:** Minor but adds to the death-by-a-thousand-cuts confidence erosion that pushes signals below the floor.

---

## 10. Final owner-facing verdict

### What is happening

Your system is working exactly as coded. It is **not broken** — it is **extremely selective by design**, and the current market conditions apparently do not satisfy the conjunction of conditions required by any path to clear the full gate cascade.

### The fundamental architectural tension

The engine was designed with a "quality over quantity" philosophy: each signal must satisfy structural (SMC/sweep), trend (EMA/ADX/momentum), confluence (MTF), risk (SL cap/RR floor), and confidence (65+ after penalties) requirements simultaneously. This creates a **compound selectivity problem** — each gate is individually reasonable, but the product of their pass rates approaches zero in anything other than an ideal trending market with clear structural setups, strong momentum, and aligned timeframes.

### Why the zero-signal window is structurally expected

1. **Only 2 of 8 channels are live.** You've disabled 75% of your signal surface area. The disabled channels cover market conditions (mean-reversion, Ichimoku cloud, Supertrend, VWAP bounce, order-block) that might fire when the main scalp evaluators can't.

2. **The 14 evaluators in the main scalp channel have narrow, overlapping requirements.** Most need trending conditions + sweeps + momentum + EMA alignment + FVG/OB + MTF confluence. In a choppy or ranging market, these conditions are mutually exclusive with market reality.

3. **The gate cascade after generation kills most survivors.** A signal that somehow passes all evaluator-level conditions still faces MTF, SMC hard gate, trend hard gate, cross-asset, risk geometry, confidence floor, router cooldowns, and staleness checks. The compound probability is very low.

4. **The SL cap + reject-not-compress policy is correct but signal-suppressing.** Wide structural setups in volatile conditions are rejected rather than compressed — preserving thesis integrity but producing silence.

### What to do about it

1. **Enable more channels** (SCALP_FVG, SCALP_ORDERBLOCK, SCALP_SUPERTREND at minimum) to expand market coverage. Radar_only gives you no live signals.

2. **Separate per-path gating from per-channel gating.** The ADX<15 RANGING block should not kill SR_FLIP_RETEST, which doesn't need ADX. The SMC hard gate should not apply to TREND_PULLBACK_EMA, which doesn't need sweeps (this is already exempt — good). The MTF gate should be family-aware for all families, not just reclaim_retest and reversal.

3. **Relax the QUIET regime penalty multiplier** from 1.8 to 1.2–1.4. The current 1.8× makes even one soft gate penalty (-18 to -27 points) fatal for most signals.

4. **Add per-evaluator no_signal_reason telemetry** to diagnose exactly which condition within each evaluator is blocking generation. This is the single highest-value diagnostic improvement.

5. **Consider widening the SL cap for structural setups** to 2.0–2.5% (for SCALP channel), especially for LIQUIDATION_REVERSAL, POST_DISPLACEMENT_CONTINUATION, and FAILED_AUCTION_RECLAIM whose thesis requires wider invalidation zones.

6. **Reduce the global symbol cooldown** from 900s (15 min) to 300-600s (5-10 min) to allow faster re-entry on the most liquid pairs.

### The uncomfortable truth

The system's 75% SL rate and 0% MFE on SL trades (from the historical memory) suggest that the signals it *does* generate are not well-timed. The response to poor performance was to tighten gates further (reject-not-compress, structural SL preservation, QUIET penalties, etc.), which improved per-signal quality but reduced volume to near zero. This is a **quality/volume death spiral**: poor performance → tighter gates → fewer signals → insufficient data to evaluate quality → more tightening.

The path forward is not to loosen gates indiscriminately, but to:
- Expand the signal surface (more channels, more paths)
- Make gating path-aware (not channel-uniform)
- Add diagnostic telemetry to understand *where* in each path signals are dying
- Accept that in crypto, a 50-60% win rate with good R:R is profitable — the 75% SL rate is the problem to solve, not the signal volume

---

*Audit complete. All findings are grounded in code-level evidence from the repository. Runtime-dependent conclusions (market state, data availability, circuit breaker state) are explicitly flagged as uncertain.*
