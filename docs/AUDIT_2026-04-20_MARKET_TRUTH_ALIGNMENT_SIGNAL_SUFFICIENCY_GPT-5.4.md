# AUDIT — Market-Truth Alignment & Signal-Generation Sufficiency (2026-04-20, GPT-5.4)

## Executive conclusion

Current zero-signal behavior is **more likely architecture/policy-suppressed than purely market-truth-consistent**, with **runtime-truth window limitations** as a secondary contributor and **baseline candle-history insufficiency** as the least likely cause.

Primary basis:
- Multi-layer suppression and gating between evaluator generation and live emission (`src/scanner/__init__.py:2807-3872`, `src/scanner/__init__.py:2896-2980`).
- Live rollout state limits which channels can dispatch to paid/live paths (`config/__init__.py:800-827`, `src/scanner/__init__.py:788-806`).
- Runtime truth report depends on periodic funnel log lines + closed lifecycle records, which can under-represent actual evaluator activity in a 24h slice (`src/runtime_truth_report.py:70-95`, `src/runtime_truth_report.py:366-398`, `src/scanner/__init__.py:1453-1462`).

---

## 1) System model of market truth for signal generation & runtime truth reporting

### Signal-generation truth model
- Scanner context is built from OHLCV, indicators, SMC detector output, regime context, spread, and volume (`src/scanner/__init__.py:1801-1912`).
- SMC detector contributes sweeps, MSS, FVG, whale/delta signals, and CVD divergence metadata (`src/detector.py:37-65`, `src/detector.py:71-247`).
- Core 360 scalping path runs 14 evaluator functions every cycle and tracks generation telemetry by evaluator (`src/channels/scalp.py:355-383`, `src/channels/scalp.py:276-282`).
- Post-evaluator, scanner applies execution/risk/scoring/gating chain including MTF, VWAP extension, kill-zone, OI, cross-asset, spoof, volume divergence, clustering, risk geometry, confidence floors, and tier routing (`src/scanner/__init__.py:2998-3338`, `src/scanner/__init__.py:3232-3872`).

### Runtime truth-report model
- Report artifacts are built from:
  - runtime health JSON,
  - heartbeat text,
  - `signal_performance.json`,
  - current/previous engine logs parsed for path funnel lines (`scripts/build_truth_report.py:45-76`, `src/runtime_truth_report.py:70-107`, `src/runtime_truth_report.py:326-513`).
- Path funnel classification uses attempts/generated/gated/emitted counters by setup (`src/runtime_truth_report.py:109-133`, `src/runtime_truth_report.py:375-395`).
- Freshness is derived from heartbeat age and latest performance-record timestamp (`src/runtime_truth_report.py:202-240`).

---

## 2) Path-by-path evaluator map (360_SCALP)

| Path / setup | Core thesis | Required data | Likely minimum warmup/history | Key generation dependencies and gates | SL type | TP type | Likely failure modes | Market-truth concerns |
|---|---|---|---|---|---|---|---|---|
| `LIQUIDITY_SWEEP_REVERSAL` | Sweep reclaim + momentum alignment | 5m candles + SMC sweeps/FVG + indicators | ~50x5m | ADX/EMA/RSI/MACD/MTF + sweep presence (`src/channels/scalp.py:400-643`) | Sweep-level anchored ±0.1% + ATR floor | FVG/swing then 1.5/2.5/4R fallback | Missing sweep, MTF block, confidence/risk rejection | Structurally plausible; suppression often downstream |
| `TREND_PULLBACK_EMA` | Trend pullback into EMA9/21 with turn confirmation | 5m + optional 4h for TP2 | ~50x5m | Strict trend regime, EMA alignment, reclaim/turn checks, SMC context (`src/channels/scalp.py:649-851`) | EMA-distance + ATR floor | swing + 4h swing fallback | Over-strict micro-structure conditions | Can under-fire in valid trending markets |
| `LIQUIDATION_REVERSAL` | Cascade exhaustion + opposite CVD + zone + volume spike | 5m + CVD + FVG/OB + volume | ~20x5m (+21 vols, CVD>=4) | Cascade ±2%, RSI extreme, near-zone, volume spike (`src/channels/scalp.py:859-1025`) | Cascade extremum + fixed 0.3% buffer | Fib retrace, else 1.5/2.5/4R | Missing CVD/zone/volume | Fixed 0.3% stop buffer can be too generic |
| `WHALE_MOMENTUM` | Whale/tick-flow + OBI confirmation | 1m + recent ticks + whale/delta + optional order book | ~10x1m | Tick notional, delta ratio, RSI soft/hard, OBI tiers (`src/channels/scalp.py:1032-1227`) | Swing invalidation + ATR floor | Fixed R-multiples | Missing whale/delta/orderbook | `smc_data["order_book"]` path appears unpopulated by scanner/detector, reducing confirmation fidelity (`src/detector.py:52-65`) |
| `VOLUME_SURGE_BREAKOUT` | Breakout + pullback retest on surge | 5m OHLCV + EMA/RSI + SMC | ~28x5m | Surge volume, breakout in last 5 closed bars, pullback zone (`src/channels/scalp.py:1234-1443`) | Fixed 0.8% below swing high | Measured move | Breakout timing/volume miss | Fixed-width structural stop may mismatch volatility |
| `BREAKDOWN_SHORT` | Bearish mirror of surge breakout | 5m OHLCV + EMA/RSI + SMC | ~28x5m | Symmetric bearish logic (`src/channels/scalp.py:1450-1664`) | Fixed 0.8% above swing low | Measured move down | Mirror of above | Same fixed-width mismatch risk |
| `OPENING_RANGE_BREAKOUT` | Session opening-range breakout | 5m + session-time + SMC | ~20x5m | Feature-flag and strict UTC session windows (`src/channels/scalp.py:1683-1693`) | Range opposite side ±0.1% | Range multiples | Disabled by default | Explicitly not institutional-grade in current implementation |
| `SR_FLIP_RETEST` | Break-close acceptance then retest + rejection | 5m structure + EMA/RSI + optional SMC | ~55x5m | Strong structural checks and layered penalties (`src/channels/scalp.py:1823-2159`) | Adaptive structural invalidation (ATR/level/wick) | swing/4h/fallback | Fails strict reclaim/rejection tests | Generally market-structure aligned |
| `FUNDING_EXTREME_SIGNAL` | Contrarian funding with EMA/RSI/CVD context | 5m + funding + optional CVD + SMC | ~5x5m + funding polls | Funding threshold + directional confirmations (`src/channels/scalp.py:2166-2315`) | Liq-cluster-based if present, else ATR*1.5 | Structure TP1 + ratio TP2/3 | Funding or SMC missing | `liquidation_clusters` appears not populated in scanner SMC path |
| `QUIET_COMPRESSION_BREAK` | BB squeeze breakout in quiet/range | 5m + BB/MACD/volume/RSI + SMC | ~25x5m | Quiet/ranging regime + squeeze + breakout + vol (`src/channels/scalp.py:2322-2467`) | BB boundary ±0.1% | Band-width projections | No squeeze/SMC | Valid in principle; hard SMC requirement can suppress |
| `DIVERGENCE_CONTINUATION` | Hidden CVD divergence in trend continuation | 5m + CVD history + EMA + SMC | ~20x5m + CVD>=20 | Trend regime + divergence + EMA + SMC (`src/channels/scalp.py:2474-2680`) | EMA21 ±0.5% | swing + HTF swing fallback | CVD not mature or no SMC | Reasonable, but strict stacked conditions |
| `CONTINUATION_LIQUIDITY_SWEEP` | Trend continuation after sweep reclaim | 5m + sweeps + EMA/ADX/momentum | ~20x5m | Sweep recency, reclaim, momentum, RSI (`src/channels/scalp.py:2687-2925`) | Sweep-level ±ATR buffer | FVG/swing + ratio fallback | Missing sweeps or stale sweep | Structurally coherent |
| `POST_DISPLACEMENT_CONTINUATION` | Displacement → consolidation → re-acceleration | 5m full OHLCV + EMA/ADX + optional SMC | ~20x5m | Strong displacement body/volume + tight consolidation + breakout (`src/channels/scalp.py:2944-3270`) | Consolidation boundary ±ATR buffer | Displacement measured move | Pattern too strict, low frequency | Robust thesis but naturally sparse |
| `FAILED_AUCTION_RECLAIM` | Failed acceptance beyond structure, then reclaim | 5m + ATR + optional SMC | ~20x5m | Auction-window pattern + reclaim-distance checks (`src/channels/scalp.py:3277-3570`) | Wick-extreme ±ATR buffer | Tail measured move | No clear failed-auction structure | Strong structural alignment |

---

## 3) Historical seeding sufficiency & minimum data requirements by feature family

### Boot seeding and persistence
- Engine boots with pair refresh + snapshot load + gap fill or full historical seed; fatal if seeded pairs = 0 (`src/bootstrap.py:135-170`).
- Default seeding: 500 candles for `1m/5m/15m/1h/4h/1d`, tick limit configured separately (`config/__init__.py:340-348`).
- Historical cache/gap-fill policy and stale-gap fallback behavior in data store (`src/historical_data.py:35-67`).

### Indicator family minima (in compute layer)
- EMA9/21: >=21 bars, EMA200: >=200 (`src/scanner/indicator_compute.py:24-26`, `src/scanner/indicator_compute.py:80-97`).
- ADX: >=30, RSI: >=15, ATR: >=15, BB: >=20, MACD: >=35, Momentum(3): >=4 (`src/scanner/indicator_compute.py:26-33`, `src/scanner/indicator_compute.py:98-150`).
- Ichimoku context: >=78 (`src/scanner/indicator_compute.py:34`, `src/scanner/indicator_compute.py:177-186`).

### Order-flow / context family minima
- OI trend: lookback 5 snapshots; OI poll interval 60s, so useful trend signal needs several minutes post-boot (`src/order_flow.py:93-119`, `src/order_flow.py:448-507`).
- Funding rate availability also depends on OI poll loop (`src/order_flow.py:533-549`).
- CVD divergence requires candle-aligned snapshots and lookback 20 (`src/order_flow.py:403-441`); on 5m this implies ~100m live runtime for full warm history.
- Liquidations depend on futures `forceOrder` stream and flush loop (`src/main.py:538-584`).

### Sufficiency judgement
- Baseline candle seeding is generally sufficient for evaluator warmup.
- Data insufficiency is **more likely** in order-flow/context overlays (post-boot live accumulation, tier coverage, and missing fields in `smc_data` dictionary).

---

## 4) Support/resistance, MA, volume, structure calculations (modules/functions)

- MA/ATR/RSI/MACD/BB/momentum primitives: `src/indicators.py:19-254`.
- Scanner indicator assembly and per-TF feature extraction: `src/scanner/indicator_compute.py:43-226`.
- SMC sweep/MSS/FVG detection:
  - `detect_liquidity_sweeps` (`src/smc.py:63-177`)
  - `detect_mss` (`src/smc.py:184-233`)
  - `detect_fvg` (`src/smc.py:240-284`)
  - Orchestration to scanner-friendly dict (`src/detector.py:52-65`, `src/detector.py:116-161`).
- Structural levels helper library:
  - swings: `find_swing_levels` (`src/structural_levels.py:19-52`)
  - round numbers: `find_round_numbers` (`src/structural_levels.py:58-83`)
  - structural SL/TP adjusters: `find_structural_sl`, `find_structural_tp` (`src/structural_levels.py:90-179`).
- Regime context overlays (ADX slope, ATR percentile, volume profile): `src/regime.py:45-54`, `src/regime.py:67-97`, `src/regime.py:385-468`.
- VWAP and extension gate logic: `src/vwap.py:81-147`, `src/vwap.py:155-216`.

---

## 5) Runtime truth report limitations and why a 24h window may show no signals

1. **Path funnel requires specific periodic log lines** (`Path funnel (last 100 cycles)`), so missing/truncated logs can hide true generation/gating activity (`src/scanner/__init__.py:1453-1462`, `src/runtime_truth_report.py:70-95`).
2. **Quality/lifecycle stats are based on closed outcomes in `signal_performance.json`**, not raw generated attempts; sparse closures in 24h can look like “no activity” (`scripts/build_truth_report.py:47`, `src/trade_monitor.py:222-324`, `src/runtime_truth_report.py:366-398`).
3. **Freshness status can degrade from stale records even when scanner loop runs**, because `records_fresh` is timestamp-based (`src/runtime_truth_report.py:215-239`).
4. **Default channel scope is `360_SCALP` unless overridden**, so non-target channel behavior may be omitted (`scripts/build_truth_report.py:27`, `src/runtime_truth_report.py:350-355`).

---

## 6) Path-by-path blind spots / contradictory assumptions / truth mismatches

- Scanner SMC payload currently omits some fields that evaluators expect (`orderblocks`, `order_book`, `liquidation_clusters`), creating structural information asymmetry and likely suppressing/setup-degrading effects (`src/detector.py:52-65`, `src/channels/scalp.py:1122`, `src/channels/scalp.py:2246`).
- Rollout doctrine intentionally suppresses many channels from live dispatch (`radar_only`, `disabled`, `limited_live` pilot scope) independent of market truth (`config/__init__.py:800-837`, `src/scanner/__init__.py:788-806`).
- Gating stack is deep and cumulative (hard rejections + soft penalties + confidence floors + watchlist routing + cooldown/correlation locks), making zero-signal windows possible even when evaluators intermittently detect setups (`src/scanner/__init__.py:2896-3338`, `src/scanner/__init__.py:3838-4228`, `src/signal_router.py:483-489`).

---

## 7) Final verdict

For the observed 24h zero-signal period, the strongest repo-grounded explanation is:

1. **Policy/gating suppression and rollout constraints** (most likely),  
2. **Truth-report observability window artifacts** (second),  
3. **Actual market no-opportunity conditions** (possible but less dominant by architecture),  
4. **Baseline seeding insufficiency** (least likely for core candles/indicators, more plausible only for order-flow overlays early after boot).

