# AUDIT_2026-04-20_MARKET_TRUTH_PATH_DATA_SUFFICIENCY_GPT-5.4

## 1. Executive conclusion

- **More likely cause of the 24h zero-signal behavior:** **combination**, led by **architecture/policy suppression** and **reporting distortion**, with **data insufficiency** materially affecting order-flow paths after restarts. Pure “the market gave nothing” is **not** the best static-code explanation.
- **Single strongest finding:** the engine’s live path universe is much narrower than it looks, and several evaluator dependencies are not actually populated at runtime:
  - only `360_SCALP` is `full_live` by default, `360_SCALP_DIVERGENCE` is only `limited_live` on `BTCUSDT,ETHUSDT`, and several other channels are `radar_only` or `disabled` (`config/__init__.py:740-842`);
  - `smc_data` is populated with `sweeps`, `fvg`, `funding_rate`, and `cvd`, but **not** `orderblocks`, `order_book`, or `liquidation_clusters` (`src/detector.py:52-65`, `src/scanner/__init__.py:1827-1835`, `src/scanner/__init__.py:1898-1907`).
- **Highest-leverage next investigation/correction:** verify the last 24h with **per-channel, per-setup funnel counters**, not the default single-channel truth report, and fix the missing runtime inputs first:
  1. include `360_SCALP_DIVERGENCE` and any radar channels in truth reporting;
  2. populate or remove `orderblocks`, `order_book`, and `liquidation_clusters`;
  3. backfill `OrderFlowStore` on boot, because current historical seeding does **not** warm OI/CVD/liquidations/funding logic.

## 2. End-to-end system truth

Real pipeline, as implemented:

1. **Pair universe**
   - `PairManager` builds the active universe, with tiering and top-futures bias (`src/pair_manager.py:1-179`).

2. **Historical seeding**
   - On boot, `Bootstrap.boot()` loads disk snapshot or does full `seed_all()` (`src/bootstrap.py:147-158`).
   - `HistoricalDataStore.seed_all()` fetches **500 candles** for `1m/5m/15m/1h/4h/1d` and **5000 recent trades** per symbol (`config/__init__.py:340-348`, `src/historical_data.py:150-225`).

3. **Live updates**
   - Closed klines append into `HistoricalDataStore`.
   - Trade ticks append into `data_store.ticks` and update running CVD.
   - `forceOrder` events buffer, then populate liquidation history.
   - OI/funding are polled by `OIPoller` every 60s (`src/main.py:501-584`, `src/order_flow.py:448-553`).

4. **Scan context build**
   - `_build_scan_context()` loads candles, computes indicators, runs SMC detection, classifies regime/market state, calculates pair quality, and attaches `funding_rate`/`cvd` if available (`src/scanner/__init__.py:1801-1931`).

5. **Evaluator generation**
   - `ScalpChannel.evaluate()` runs 14 internal evaluators and returns **all** valid candidates, not one (`src/channels/scalp.py:345-394`).
   - Auxiliary channels have their own evaluators (`src/channels/scalp_fvg.py`, `src/channels/scalp_divergence.py`, `src/channels/scalp_orderblock.py`).

6. **Scanner suppression/gating**
   - Before evaluation: rollout state, pair quality, market-state/channel preskips, cooldowns, circuit breaker, active-signal duplication (`src/scanner/__init__.py:788-806`, `1933-2062`).
   - After evaluator output: setup classification, execution check, MTF gate, VWAP, kill-zone, OI/funding, cross-asset, spoof, volume-divergence, scoring, stat filter, pair-analysis, SMC hard gate, trend hard gate, confidence floor (`src/scanner/__init__.py:2861-3879`).

7. **Signal arbitration / emission**
   - `360_SCALP` same-direction candidates are arbitrated by final confidence.
   - Multi-strategy confluence can replace setup class with `MULTI_STRATEGY_CONFLUENCE`.
   - Emitted signals go to router (`src/scanner/__init__.py:3972-4228`).

8. **Router**
   - Applies stale checks, correlation lock, cooldowns, per-channel caps, min confidence, risk manager, then posts (`src/signal_router.py:482-752`).

9. **Trade monitor / truth records**
   - Only **finalized** signals become `SignalRecord`s in `data/signal_performance.json` (`src/trade_monitor.py:222-380`, `src/performance_tracker.py:25-187`).

10. **Runtime truth report**
   - Built by workflow + script from:
     - container runtime health,
     - heartbeat text,
     - `signal_performance.json`,
     - engine logs parsed for path funnel lines (`.github/workflows/vps-monitor.yml:85-161`, `scripts/build_truth_report.py:42-76`, `src/runtime_truth_report.py:70-95`, `326-512`).

## 3. Path-by-path evaluator audit

| Path / Setup | Core thesis | Required inputs | Minimum warmup / history needs | Generation dependencies | Main gates / suppressors | SL logic | TP logic | Market-truth alignment | Likely failure modes | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| `360_SCALP::_evaluate_standard` → `LIQUIDITY_SWEEP_REVERSAL` | Sweep + reclaim + aligned momentum | 5m candles, ADX, EMA9/21, RSI, MACD, 1h MTF, SMC sweep, optional FVG | ~50x5m + 1h indicators + sweep | `sweeps` must exist (`src/channels/scalp.py:433-436`) | ADX, spread/volume, momentum threshold, RSI, EMA alignment, MACD, MTF, later scanner gates | just beyond swept level ±0.1%, floor 0.5 ATR (`520-545`) | nearest FVG mid, 20-bar swing, else 1.5/2.5/4R (`552-593`) | Plausible for crypto scalp reversals, but depends heavily on generic trend/MTF stack | no sweep; MTF fail; generic trend gate; FVG absent; sweep may be low-TF noise | Reasonable path, but over-gated downstream |
| `TREND_PULLBACK_EMA` | Trend continuation after EMA9/21 pullback | 5m candles, EMA9/21/50, RSI, momentum, optional 4h swings, FVG/orderblock | ~50x5m; 4h only improves TP2 | Needs trending regime and SMC context (`649-851`) | regime hard gate, EMA stack, EMA proximity, RSI 40-60, candle-turn rules, hard FVG/orderblock gate, later MTF/trend/confidence | beyond EMA21, floor 0.5 ATR (`775-783`) | 20-bar swing, 4h swing, then 4R (`785-816`) | Thesis is plausible; geometry is acceptable but still generic | `orderblocks` never populated; FVG/orderblock hard gate effectively means FVG-only; later min confidence | Good thesis, underpowered by missing shared orderblocks and hard context gating |
| `LIQUIDATION_REVERSAL` | 3-candle liquidation cascade + CVD absorption reversal | 5m candles, volume, CVD history, RSI, FVG/orderblock proximity | ~21x5m + live CVD | `cvd` required; near FVG/orderblock required (`898-949`) | 2% cascade, CVD opposition, RSI extreme, near-zone, 2.5x vol, later reversal-family gates | beyond cascade extreme +0.3% (`954-967`) | fib retrace of cascade 38.2/61.8/100%, fallback R-multiples (`990-1018`) | Strongest path-to-thesis fit in repo | CVD not backfilled; orderblocks absent; no live liquidations explicitly required despite name | Good model, but warmup-sensitive |
| `WHALE_MOMENTUM` | Large participant impulse confirmed by tape + order book | 1m candles, recent ticks, whale alert or delta spike, RSI, optional order book | ~10x1m + ticks | `whale_alert` or `volume_delta_spike`; `recent_ticks` needed (`1050-1083`) | spread/volume, tick-flow ratio, RSI layered gate, order-book imbalance, later orderflow/trend scoring | recent swing ±0.1%, floor ATR (`1143-1168`) | fixed 1.5/2.5/4R (`1190-1207`) | Plausible if real OBI exists | **`smc_data["order_book"]` is never populated**, so OBI confirmation never occurs and path always carries missing-book penalty (`1122`, `1216-1220`) | Family-specific intent exists, but runtime data path is incomplete |
| `VOLUME_SURGE_BREAKOUT` | Breakout on surge volume, then retest | 5m candles, volume, EMA9/21, RSI, optional FVG/orderblock | ~28x5m | surge vol + breakout window + retest zone (`1234-1443`) | QUIET block, surge volume, swing breakout, retest distance, EMA, RSI, FVG/orderblock hard unless fast regime | fixed 0.8% below breakout level (`1371-1375`) | measured move from prior range (`1377-1386`) | Thesis is plausible | 0.8% fixed SL is simplistic across majors/alts; missing orderblocks makes context thinner; later confidence gates | Viable but somewhat generic geometry |
| `BREAKDOWN_SHORT` | Bearish mirror of surge breakout | 5m candles, volume, EMA, RSI, optional FVG/orderblock | ~28x5m | same as above, short side (`1450-1664`) | QUIET block, volume surge, breakdown search, bounce zone, EMA, RSI, FVG/orderblock | fixed 0.8% above breakdown level (`1593-1597`) | measured move down from prior range (`1599-1607`) | Plausible | same issues as breakout | Viable but somewhat generic geometry |
| `OPENING_RANGE_BREAKOUT` | Session-opening breakout | 5m candles, volume, EMA, FVG/orderblock, UTC hour | ~20x5m | only if `SCALP_ORB_ENABLED=true` and London/NY proxy hours (`1683-1693`) | **disabled by default** (`config/__init__.py:838-842`); time window; not quiet/ranging; FVG/orderblock | range low/high ±0.1% (`1761-1779`) | measured move on opening range height (`1762-1771`) | Current implementation is explicitly acknowledged as non-session-true | disabled by default; proxy logic uses last 8 bars, not true session open | Not part of live 24h explanation unless manually enabled |
| `SR_FLIP_RETEST` | Confirmed S/R role flip + retest hold | 5m + optional 4h candles, EMA, RSI, wick geometry, optional FVG/orderblock | ~55x5m; 4h improves TP2 | prior structure + breakout-close acceptance + retest evidence (`1823-2159`) | VOLATILE block, flip-confirmation, retest proximity, wick/body quality, EMA, RSI, later reclaim-family MTF | adaptive structural invalidation around flip level/wick/ATR (`2047-2068`) | 20-bar swing, 4h target, 3.5R fallback (`2074-2105`) | Best-aligned structural geometry in repo | later generic MTF/scoring still can suppress; hard EMA alignment may still overtrend-ify structural setup | Strong path; one of the healthiest models |
| `FUNDING_EXTREME_SIGNAL` | Contrarian trade against extreme funding crowding | funding rate, 5m candles, EMA9, RSI trend turn, optional CVD, FVG/orderblock | ~5x5m + live funding; CVD improves | funding must be present (`2181-2183`) | QUIET block; funding extreme; EMA9 side; RSI; optional CVD; hard FVG/orderblock | supposed liquidation-cluster SL, but falls back to `ATR*1.5` if no clusters (`2245-2264`) | nearest FVG/OB structure then 2R/3.5R (`2271-2279`) | Thesis plausible, but runtime implementation is weakened | **`liquidation_clusters` are never populated**, so path never uses intended cluster-based invalidation (`2246`) | Good idea, incomplete runtime data |
| `QUIET_COMPRESSION_BREAK` | BB squeeze release in quiet/ranging | 5m candles, BB, MACD, volume, RSI, FVG/orderblock | ~25x5m | quiet/ranging regime required (`2322-2467`) | bb-width <1.5%, MACD zero-cross, 2x volume, RSI band, hard FVG/orderblock | outside opposite BB ±0.1% (`2403-2415`) | 0.5/1.0/1.5x band width (`2417-2430`) | Plausible for compression release | hard FVG/orderblock gate; can self-block in low-activity regimes with sparse SMC context | Reasonable, but high-selectivity specialist |
| `DIVERGENCE_CONTINUATION` | Hidden CVD divergence inside trend | 5m + optional 15m/4h candles, live CVD, EMA21 proximity, FVG/orderblock | ~20x5m + **20 CVD snapshots** (~105m post-boot on 5m) | `cvd` required and divergence locally recomputed (`2506-2554`) | trending regime only, hard CVD divergence, EMA alignment, EMA21 proximity, hard FVG/orderblock, later divergence-family gates | EMA21 ±0.5% (`2578-2590`) | divergence-window swing, 20-bar swing, 4h/15m extended (`2592-2644`) | Thesis plausible | CVD not backfilled; orderblocks absent; only live if in `360_SCALP` full_live or aux divergence channel pilot | Valid path, but strongly warmup-sensitive |
| `CONTINUATION_LIQUIDITY_SWEEP` | Trend continuation after directional liquidity grab | 5m candles, EMA, ADX, sweep, momentum, RSI, optional FVG/orderblock | ~20x5m + sweep | trend-family regime + sweep in trend direction (`2687-2937`) | strict regime set, EMA direction, ADX, sweep recency/reclaim, momentum, RSI, later continuation-family MTF | beyond swept level + ATR buffer (`2839-2856`) | FVG midpoint, swing, else 1.5/2.5/4R (`2858-2897`) | Plausible and structurally better than standard breakout paths | sweep age and later MTF/scoring suppression | Good path |
| `POST_DISPLACEMENT_CONTINUATION` | Institutional displacement → absorption → re-acceleration | 5m candles, EMA, ADX, volume, structure, optional FVG/orderblock | ~20x5m | valid regime, displacement candle, tight consolidation, breakout (`2944-3270`) | strong structural filters, ADX, RSI, later continuation-family MTF | beyond consolidation ± ATR buffer (`3176-3194`) | measured move from displacement height (`3196-3212`) | One of the better crypto-truth-aligned continuation models | no orderblocks; later generic gates still apply | Strong model |
| `FAILED_AUCTION_RECLAIM` | Failed breakout/breakdown reclaim | 5m candles, ATR, structural high/low, optional FVG/orderblock | ~20x5m | prior structure + failed auction in 1-7 bar window + reclaim (`3339-3570`) | blocked in strong-trend/volatile regimes, RSI layered gate, later reclaim-family MTF | beyond failed-auction wick + ATR buffer (`3473-3492`) | measured move from auction tail (`3494-3525`) | Strong structural alignment | later MTF/scoring may still suppress; no orderblocks | Strong model |
| `360_SCALP_FVG` → `FVG_RETEST` / `FVG_RETEST_HTF_CONFLUENCE` | Retest of fresh FVG | 5m/15m candles, FVG zones, ADX, RSI | ~20x5m/15m | depends on detector FVGs (`scalp_fvg.py:60-243`) | ADX, spread/volume, FVG freshness/fill/proximity, RSI | zone boundary ± ATR, decay by age/fill (`166-194`) | fixed config ratios | Plausible | **radar_only by default**, not paid-live (`config/__init__.py:800-806`) | Not part of default live zero-signal path |
| `360_SCALP_DIVERGENCE` → `RSI_MACD_DIVERGENCE` | RSI/MACD regular/hidden divergence | 5m candles, RSI array, MACD hist, 15m/1h MTF | ~30x5m | self-computes RSI/MACD if arrays missing (`scalp_divergence.py:96-115`) | ADX ceiling, RSI, MTF divergence gate | generic ATR-based | fixed config ratios | Plausible | only `limited_live` on `BTCUSDT,ETHUSDT` by default (`config/__init__.py:812-837`) | Relevant, but narrow live scope |
| `360_SCALP_ORDERBLOCK` → `SMC_ORDERBLOCK` | Fresh OB retest after impulse | 5m candles, ATR, internal OB detection | ~50x5m | internal OB detection, not detector-supplied (`scalp_orderblock.py:49-106`) | freshness, spread/volume, RSI | beyond OB edge ±0.2 ATR (`216-235`) | fixed config ratios | Plausible | **radar_only by default**, not paid-live | Not part of default live zero-signal path |

**Disabled auxiliary channels by default:** `360_SCALP_CVD`, `360_SCALP_VWAP`, `360_SCALP_SUPERTREND`, `360_SCALP_ICHIMOKU` are rollout-disabled (`config/__init__.py:740-842`). They do not materially explain a paid-live 24h zero-signal window unless the operator changed env flags.

## 4. Historical seeding and data sufficiency

### What is seeded
- `1m/5m/15m/1h/4h/1d`: **500 candles each** (`config/__init__.py:340-347`).
- recent trades: **5000 ticks** (`config/__init__.py:348`, `src/historical_data.py:111-144`).
- gem scanner separately seeds `1d/1w` (`config/__init__.py:358-360`, `src/historical_data.py:550-596`).

### Where it is seeded
- boot path: `Bootstrap.boot()` → `HistoricalDataStore.seed_all()` or `gap_fill()` (`src/bootstrap.py:147-158`).
- persistence: `data/cache/*.npz`, `data/cache/ticks/*.json`, metadata in `data/cache/metadata.json` (`src/historical_data.py:35-37`, `231-345`).

### Is it enough?
**For candles/indicators/structure:** mostly yes.
- EMA200 needs 200 bars; seeded 500 is enough.
- MACD/ADX/ATR/BB/RSI warmups are all below 50 bars; seeded 500 is enough (`src/scanner/indicator_compute.py:23-40`).
- SMC sweep detection uses lookback 50; seeded 500 is enough (`src/detector.py:77-80`, `118-143`).
- BTC correlation uses 50/200 closes; seeded 500x5m is enough (`src/correlation.py:116-180`).
- 4h targets on 10 bars are trivial with 500 seeded 4h bars.

**For order-flow families:** no, not by seeding alone.
- Historical seeding writes candles/ticks into `HistoricalDataStore`, but **does not populate `OrderFlowStore`** (`src/historical_data.py:150-185`, `src/bootstrap.py:147-158`).
- `OrderFlowStore` warms only from:
  - OI poller after boot (`src/order_flow.py:481-549`);
  - live trade ticks for running CVD (`src/main.py:521-536`);
  - candle-close snapshots for candle-aligned CVD (`src/main.py:516-519`);
  - live liquidation websocket events (`src/main.py:538-576`).

### Practical warmup implications
- **Funding**: available after first OI poll, roughly **up to 60s**.
- **OI trend**: meaningful after ~5 polls, roughly **~5 minutes** (`src/order_flow.py:91-131`, `297-319`).
- **CVD divergence**: requires 20+ aligned CVD candles; on 5m this is roughly **~105 minutes post-boot** (`src/detector.py:32-35`, `182-219`; `src/channels/scalp.py:2510-2512`).
- **Liquidation-dependent thesis**: no deterministic warmup; it needs real live `forceOrder` events.
- **Shared orderblocks/liquidation_clusters/order_book**: not warmup-limited; they are simply **not populated** by the scanner path.

### Bottom line
- **Indicator/history sufficiency is adequate.**
- **Order-flow/history sufficiency is not adequate for immediate readiness** after boot/restart.
- If the engine restarted within or before that 24h window, several evaluators were likely partially blind for a meaningful fraction of it.

## 5. Support/resistance, MA, volume, structure, and context calculations

### Support / resistance
There is a generic helper layer:
- swing highs/lows over local ±3 bars: `find_swing_levels()` (`src/structural_levels.py:19-51`)
- round numbers by price magnitude: `find_round_numbers()` (`58-84`)
- structural SL/TP adjusters: `find_structural_sl()`, `find_structural_tp()` (`90-179`)

But **live 360_SCALP mostly does not use that helper**. It uses path-specific structure:
- breakout/breakdown: prior 20-bar swing excluding breakout search window (`src/channels/scalp.py:1294-1301`, `1515-1523`)
- SR flip: prior 41-bar structure + 8-bar flip search (`1887-1944`)
- failed auction reclaim: prior 20-bar structure excluding auction window (`3348-3367`)
- trend pullback/divergence: swing highs/lows from recent 20 bars / 4h window (`785-816`, `2592-2644`)

### Moving averages / EMA alignment
- EMA is standard exponential MA (`src/indicators.py:19-29`).
- Scanner computes `ema9/21/50/200` if enough bars (`src/scanner/indicator_compute.py:79-97`, `256-260`).
- MTF trend state is:
  - bullish if `ema_fast > ema_slow` and `close > ema_fast`
  - bearish if `ema_fast < ema_slow` and `close < ema_fast`
  - else neutral (`src/mtf.py:97-103`).
- Many paths use EMA alignment as hard thesis gate; some are exempt downstream (`src/scanner/__init__.py:290-301`, `3767-3789`).

### Volume and volume floors
- Base `360_SCALP` volume floor is `$5M` 24h (`config/__init__.py:591-605`).
- Pair profile multiplies that:
  - MAJOR `×5`,
  - MIDCAP `×1`,
  - ALTCOIN `×0.3` (`config/__init__.py:415-465`, `src/channels/base.py:244-282`).
- Additional liquidity-tier adjustments are applied in `ScalpChannel._pass_basic_filters()` (`src/channels/scalp.py:284-311`).
- Path-level surge logic is usually rolling last-candle / previous-7-or-20 average.

### Momentum and MACD
- momentum = % change over 3 candles (`src/indicators.py:246-254`).
- MACD = EMA12-EMA26, signal EMA9, histogram = diff (`src/indicators.py:161-211`).
- Scanner stores only last/prev histogram in its main compute path (`src/scanner/indicator_compute.py:133-150`, `281-288`).
- Some evaluator comments imply richer arrays; those are not always present from scanner’s compute path.

### SMC structure, sweeps, FVGs, orderblocks
- **Sweeps**: wick beyond recent high/low over lookback, close back inside, optional volume filter, minimum 0.02% depth (`src/smc.py:63-177`).
- **MSS**: lower-TF close must break the body of the sweep candle, not just wick midpoint (`184-233`).
- **FVG**: 3-candle gap; min width 0.01% (`240-285`).
- **Orderblocks**:
  - there is internal orderblock detection in `src/channels/scalp_orderblock.py:49-106`,
  - but the shared `smc_data["orderblocks"]` used by many `360_SCALP` evaluators is **not produced** by `SMCDetector` or `_build_scan_context()`.

### Funding, liquidations, OI, CVD
- OI trend = compare first vs last of recent snapshots; threshold 0.5% (`src/order_flow.py:91-131`).
- funding rate = `premiumIndex.lastFundingRate` polled live (`src/order_flow.py:533-549`).
- liquidations = recent `forceOrder` volume summed over window (`src/order_flow.py:341-375`).
- CVD = cumulative buy USD - sell USD, snapshotted at candle close (`src/order_flow.py:381-420`).
- Divergence = early-half vs late-half highs/lows on price vs CVD (`src/order_flow.py:195-249`).

### BTC/ETH correlation and macro context
- rolling BTC correlation: Pearson on 50/200 closes (`src/correlation.py:136-180`).
- cross-asset gate:
  - correlated alt LONGs can be soft-penalized or hard-blocked during BTC dump;
  - correlated SHORTs can be boosted during BTC dump (`src/cross_asset.py:134-248`).
- regime context tracks ATR percentile, ADX slope, volume profile relative to VWAP, and transitions (`src/regime.py:45-97`, `148-293`).

## 6. SL/TP doctrine vs crypto market truth

### What is good
- Structural paths are materially better aligned than generic ATR bots:
  - `SR_FLIP_RETEST`
  - `FAILED_AUCTION_RECLAIM`
  - `CONTINUATION_LIQUIDITY_SWEEP`
  - `POST_DISPLACEMENT_CONTINUATION`
  - `LIQUIDATION_REVERSAL`
- Protected structural setups preserve evaluator-authored geometry downstream (`src/signal_quality.py:118-129`, `1111-1275`).

### What is mixed or weak
1. **Global 360_SCALP SL cap = 1.5%**
   - enforced in `signal_quality.py` (`343-355`, `1127-1159`).
   - On crypto futures, this can reject truthful structural invalidations on volatile alts or during high-volatility sessions.

2. **Some paths still use generic or fixed-percent geometry**
   - `VOLUME_SURGE_BREAKOUT` / `BREAKDOWN_SHORT`: fixed **0.8%** from swing level.
   - standard `LIQUIDITY_SWEEP_REVERSAL`: 0.1% beyond sweep with 0.5 ATR floor.
   - `DIVERGENCE_CONTINUATION`: EMA21 ±0.5%.
   - These are serviceable, but not equally path-true across BTC, ETH, majors, and high-beta alts.

3. **Funding-extreme path is not living its intended doctrine**
   - code says SL should key off liquidation clusters, but those clusters are never injected, so it falls back to `ATR*1.5` (`src/channels/scalp.py:2245-2264`).
   - That is materially less family-specific than the comments imply.

4. **Whale path is only partially family-specific**
   - intended thesis uses whale/delta + OBI, but `order_book` is absent, so practical runtime behavior is “tick-flow only, penalized” rather than true tape+book confluence.

### TP realism
- Structural/measured-move/fib targets are generally more realistic than fixed-percent TPs:
  - good: liquidation fibs, measured-move breakout, displacement height, auction tail, 4h structural targets.
- Ratio-only fallback TPs are still common and can overstate achievable move size on very short-lived scalp bursts.

### Owner-facing doctrine judgment
- **SLs are no longer uniformly bad**, but **they are uneven**:
  - strong on structural families,
  - mediocre/generic on some momentum/breakout families,
  - partially broken where runtime data for the intended geometry is absent.
- **TPs are mostly reasonable when structure is used; less convincing where pure R-multiples remain.**
- **Family-specific paths are only partly family-specific in practice**, because downstream gating and missing runtime inputs collapse some of them back toward generic trend logic.

## 7. Runtime truth report reliability

### Pipeline
- workflow: `.github/workflows/vps-monitor.yml`
- builder: `scripts/build_truth_report.py`
- core logic: `src/runtime_truth_report.py`

### What it depends on
- `runtime_health.json` from Docker inspect
- `heartbeat.txt`
- `signal_performance.json`
- current/previous engine logs with path funnel lines (`Path funnel (last 100 cycles): ...`) (`scripts/build_truth_report.py:45-69`, `src/runtime_truth_report.py:70-95`)

### Freshness logic
- heartbeat warning if age > 120s (`src/runtime_truth_report.py:208-214`)
- records considered fresh only if latest closed performance record age <= 2h (`215-220`)
- overall = `unhealthy` / `stale` / `healthy` from running+health+freshness (`222-240`)

### Why it can be stale or misleading even if engine is healthy
1. **Default channel scope is only one channel**
   - workflow default is `--channel 360_SCALP` (`.github/workflows/vps-monitor.yml:16-20`, `129-161`).
   - So the default truth report is **not an “all paths” report**.

2. **Closed-trade bias**
   - `quality_by_setup` and lifecycle summaries only use **closed** `SignalRecord`s (`src/runtime_truth_report.py:168-199`, `397-399`).
   - Open signals, active watchlists, generated-but-filtered candidates are invisible there.

3. **Path funnel truth depends on logs, not persistent counters**
   - if logs are rotated, truncated, missing, or workflow fetches a bad window, `path_funnel_truth` can be empty or incomplete (`70-95`, `369-395`).

4. **“Stale” can happen with a healthy engine**
   - no closed signals for >2h => `records_fresh=False`
   - but that does **not** prove scanner inactivity.

5. **Empty quality windows are low-evidence**
   - path classification treats low sample counts conservatively (`109-132`).
   - comparison skips quality deltas when both windows have `<3` closed signals (`255-260`).

### Bottom line
The runtime truth report is useful, but:
- it is **channel-scoped** by default,
- **closure-biased**,
- and **log-dependent**.
It can absolutely understate live engine activity and can mislabel “no recent closed trades” as “no real path activity.”

## 8. Root-cause ranking for the 24h zero-signal window

1. **Architecture / rollout narrowing of the live universe**
   - Paid-live is mostly `360_SCALP`; `360_SCALP_DIVERGENCE` is limited to `BTCUSDT,ETHUSDT`; FVG/Orderblock are radar-only; several others disabled (`config/__init__.py:740-842`).

2. **Downstream suppression stack is heavy**
   - setup compatibility, execution check, MTF, VWAP, OI, cross-asset, volume-divergence, scoring, stat filter, pair analysis, SMC hard gate, trend hard gate, confidence floor, router stale/risk/correlation gates (`src/scanner/__init__.py:2861-3879`, `src/signal_router.py:491-655`).

3. **Order-flow paths are under-warmed after boot**
   - CVD/OI/funding/liquidations are not historically backfilled into `OrderFlowStore`.
   - This can suppress `LIQUIDATION_REVERSAL`, `FUNDING_EXTREME_SIGNAL`, `DIVERGENCE_CONTINUATION`, and any CVD-based auxiliary logic for minutes to hours after restart.

4. **Some evaluator inputs are structurally missing, not just stale**
   - `orderblocks`, `order_book`, `liquidation_clusters` are referenced but not populated by scanner context.

5. **Reporting blind spot**
   - If the owner looked at the default truth report, they likely looked at `360_SCALP`, not the whole engine.

6. **Genuine market conditions**
   - Still possible, especially if the market was directionless/choppy without clean sweeps/retests.
   - But static code makes it unlikely that this is the sole explanation.

## 9. Concrete code-level findings

1. **Default truth report is not “all paths”**
   - workflow default channel is `360_SCALP` (`.github/workflows/vps-monitor.yml:16-20`).

2. **Live rollout is narrow**
   - `360_SCALP` = `full_live`
   - `360_SCALP_DIVERGENCE` = `limited_live`
   - `360_SCALP_FVG`, `360_SCALP_ORDERBLOCK` = `radar_only`
   - `360_SCALP_CVD`, `VWAP`, `SUPERTREND`, `ICHIMOKU` = `disabled`
   - (`config/__init__.py:740-842`)

3. **Order-flow store is not backfilled by historical seed**
   - candles/ticks seed into `HistoricalDataStore`; OI/funding/CVD/liquidations populate only from live poller/websocket paths (`src/historical_data.py:150-185`, `src/main.py:516-576`, `src/order_flow.py:448-549`).

4. **Shared `orderblocks` are never produced**
   - detector returns sweeps/mss/fvg/whale/cvd metadata only (`src/detector.py:52-65`, `71-247`).
   - multiple `360_SCALP` paths test `smc_data.get("orderblocks", [])`, so those checks currently reduce to FVG-only.

5. **`order_book` is never attached to `smc_data`**
   - `WHALE_MOMENTUM` reads `smc_data["order_book"]` (`src/channels/scalp.py:1122`), but `_build_scan_context()` never sets it (`src/scanner/__init__.py:1827-1907`).

6. **`liquidation_clusters` are never attached**
   - `FUNDING_EXTREME_SIGNAL` tries to build SL from them (`src/channels/scalp.py:2245-2264`), but scanner context never provides them.

7. **Protected structural geometry is real and meaningful**
   - downstream risk plan preserves evaluator SL/TP for key setups and reject-not-compresses when cap exceeded (`src/signal_quality.py:118-129`, `1111-1275`).

8. **Router can suppress late but otherwise valid scalp signals**
   - 120s stale threshold for scalp channels (`src/signal_router.py:59-67`, `573-627`).

9. **Runtime “stale” does not mean “scanner dead”**
   - it can mean just “no recent closed performance record” (`src/runtime_truth_report.py:215-240`).

10. **Path families are partly corrected, but still partly generic downstream**
   - MTF family caps and semantic rescue exist only for some families (`src/scanner/__init__.py:341-380`, `2947-2968`).

## 10. Final verdict

Bluntly: **the repo is not in a state where “no signals in the last 24h” should be read as clean evidence that the market simply offered nothing.**

What the code actually says is:

- the paid-live engine is **much narrower** than the repository surface suggests;
- several evaluator families are **missing the runtime data they claim to use**;
- order-flow paths are **not fully warm after restarts**;
- and the default truth report can **misstate “no recent closed trades” as “no path activity.”**

So the most credible owner-facing conclusion is:

> **This is primarily a system-truth problem, not just a market-truth problem.**  
> The codebase contains several plausible crypto-futures theses, and some of the newer structural paths are genuinely market-aligned. But the live engine is still heavily narrowed, partially underfed, and over-suppressed, and the default reporting path can under-report what the engine is actually attempting. Static code does not support the claim that the last 24h zero-signal window is explained mainly by market conditions alone.
