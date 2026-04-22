# Deep Codebase Audit — 2026-04-22

**Model:** Claude Sonnet 4.6  
**Scope:** SL hit detection, signal generation paths, S/R mechanics, EMA/indicator pipeline, OrderFlow/CVD/funding data pipeline  
**Mode:** Analysis only — no source files modified

---

## Executive Severity Summary

| Severity | Finding |
|----------|---------|
| **HIGH** | Pre-entry SL risk: active signals are SL-evaluated before any entry-fill state is modelled |
| **HIGH** | WS REST fallback forces `k.x=True` on `/klines?limit=1` data; in-progress candles may be treated as closed |
| **MEDIUM** | Expired signals recorded as `CLOSED` in performance metrics (not `EXPIRED`) |
| **MEDIUM** | SL monitoring uses last trade tick / 1m close — not bid/ask/mark price |
| **MEDIUM** | OI `dependency_readiness` marks `present=True` when state is `empty` |
| **MEDIUM** | Order-flow (CVD/OI/funding/liquidations) has no historical backfill; cold-starts produce zero values |
| **LOW** | `SEED_TICK_LIMIT=5000` but REST fetch hard-caps to 1000 |

---

## 1. SL Hit Detection — End-to-End Trace

### Where the monitor runs

`TradeMonitor.start()` runs a polling loop at every `MONITOR_POLL_INTERVAL`
(`config/__init__.py:944`).  The monitor is launched by the bootstrap runtime
task pipeline (`src/bootstrap.py:224-230`) after being wired into main
(`src/main.py:152-161`).

### Price source

`TradeMonitor._latest_price()` uses the **latest stored trade-tick price**;
fallback is the last `1m` candle close
(`src/trade_monitor.py:459-470`).

No bid/ask or mark-price awareness.  Spread and mark-vs-last divergence can
cause phantom SL hits on thinly-traded or high-spread pairs.

### SL comparison logic

```python
# src/trade_monitor.py:688-709
if is_long and price <= sig.stop_loss:   # LONG SL check
    ...
if not is_long and price >= sig.stop_loss:  # SHORT SL check
    ...
```

Direction comparisons are correct (LONG ≤, SHORT ≥).  No inversion found.

### OHLC-based SL?

**No.**  The live monitor does not use candle `low≤SL` / `high≥SL` logic; it
compares a scalar current price against the stop-loss level.

### ⚠️ HIGH: Can SL trigger before entry fill?

Yes.  Signals are added to the router's `active_signals` map immediately upon
routing (`src/signal_router.py:741-744`).  The `Signal` dataclass contains no
fill-state field for entry (`src/channels/base.py:127`).  The monitor starts
SL/TP checking on the first poll cycle — before the exchange can have filled
the entry order.

**Risk:** a brief adverse move between signal dispatch and actual entry fill
can trigger SL recording against a position that was never actually opened.

### Expiry logic — mislabeling as CLOSED?

When max-hold time elapses the monitor sets `status = EXPIRED` and calls
`record_outcome(..., hit_sl=False, ...)` (`src/trade_monitor.py:607-613`).
`classify_trade_outcome` maps this to `"CLOSED"` rather than `"EXPIRED"`
(`src/performance_metrics.py:41-43`).

The router also has independent expiry cleanup that removes signals without
writing a performance record (`src/signal_router.py:1169-1206`).

### Full lifecycle

```
Evaluator generates signal (src/channels/scalp.py:373-436)
  ↓
Scanner gate pipeline: 20-30 hard/soft gates (src/scanner/__init__.py:3108-3905)
  ↓
Router dispatches Telegram + adds to active_signals map (src/signal_router.py:717-744)
  ↓
TradeMonitor polls every MONITOR_POLL_INTERVAL (src/trade_monitor.py:421-457)
  ↓
SL/TP comparison against current price (src/trade_monitor.py:591-869)
  ↓
_apply_final_outcome → record_outcome (src/trade_monitor.py:284-331,692-703)
  ↓
PerformanceTracker.record_outcome (src/performance_tracker.py:104-158)
  ↓
classify_trade_outcome → outcome_label stored to disk
```

### Where `outcome_label = "SL_HIT"` is set

1. `classify_trade_outcome(pnl<0, hit_sl=True)` → `"SL_HIT"`
   (`src/performance_metrics.py:35-40`)
2. Called from `_apply_final_outcome` and `_record_outcome`
   (`src/trade_monitor.py:395-403,284-288,692-703`)
3. Persisted via `PerformanceTracker.record_outcome`
   (`src/performance_tracker.py:104-158`)

---

## 2. Signal Generation Paths — Data Sufficiency

Evaluators are implemented as methods of `ScalpChannel` in
`src/channels/scalp.py`.  There is no separate `src/evaluators/` directory.

### Minimum candle requirements per path

| Path | Timeframe | Min candles | Guard location |
|------|-----------|-------------|----------------|
| FAILED_AUCTION_RECLAIM | 5m | 20 | scalp.py:3401-3412 |
| SR_FLIP_RETEST | 5m (+opt 4h) | 55 | scalp.py:1926-1935 |
| TREND_PULLBACK_EMA | 5m (+opt 4h) | 50 | scalp.py:711-713 |
| LIQUIDITY_SWEEP_REVERSAL | 5m (+1h MTF) | 50 | scalp.py:452-454 |
| QUIET_COMPRESSION_BREAK | 5m | 25 | scalp.py:2404-2411 |
| CONTINUATION_LIQUIDITY_SWEEP | 5m | 20 | scalp.py:2799-2801 |
| DIVERGENCE_CONTINUATION | 5m + CVD≥20 | 20 | scalp.py:2574-2593 |
| OPENING_RANGE_BREAKOUT | 5m | 20 | scalp.py:1757-1766 |
| POST_DISPLACEMENT_CONTINUATION | 5m | 20 | scalp.py:3068-3081 |
| WHALE_MOMENTUM | 1m + ticks | 10 | scalp.py:1100-1112 |
| VOLUME_SURGE_BREAKOUT | 5m | 28 | scalp.py:1327-1335 |
| FUNDING_EXTREME_SIGNAL | 5m + funding | 5 | scalp.py:2241-2251 |
| LIQUIDATION_REVERSAL | 5m + CVD≥4 | 20 | scalp.py:912-919 |

### Startup seeding

All active pairs are seeded with **500 candles** per timeframe (1m/5m/15m/1h/4h/1d)
at boot (`config/__init__.py:340-347`; `src/bootstrap.py:152-158`).

### ⚠️ HIGH: WS fallback synthesises closed candles from live `/klines?limit=1`

When the WebSocket stalls the REST fallback fetches `limit=1` and forces
`k.x = True` (closed candle flag) on the result
(`src/websocket_manager.py:263-287`).  If the request returns the
**current in-progress candle** rather than the last closed candle, evaluators
will compute indicators and trigger evaluations against a partial candle, and
that partial candle will be treated as authoritative.

### Indicator cache staleness

The indicator cache fingerprint is `(tf, last_close)` only — it does not
include timestamp, high, low, or volume (`src/scanner/__init__.py:1850-1865`).
Two candles at the same close price but different OHLv will share a cached
indicator result.

---

## 3. Support & Resistance — Detection, Timeframes, Usage

### Algorithm

- **Liquidity sweeps** (SMC): rolling `recent_high / recent_low` over a
  `lookback` window; detects wick-through + close-back-inside
  (`src/smc.py:127-132,145-170`).
- **Swing levels**: ±3-candle local max/min scan over last 20 candles
  (`src/structural_levels.py:19-51`).
- **Round numbers**: magnitude-scaled step sizes (100/10/1/0.1/0.01)
  (`src/structural_levels.py:58-83`).
- No volume-profile-based S/R; no pivot-point algorithm.

### Timeframes

- SMC detector default order: `4h → 1h → 15m → 5m → 1m`
  (`src/detector.py:30`).
- Scanner overrides for SCALP: shorter lookback, wider tolerance
  (`src/scanner/__init__.py:401-410`).
- SR_FLIP_RETEST uses `5m` for the level, optional `4h` TP extension
  (`src/channels/scalp.py:1926-1935,2145-2158`).

### Shared vs recomputed

`smc_data` is computed once per symbol scan cycle and shared across all
evaluators for that cycle (`src/scanner/__init__.py:1872-1877,2051-2067`).
SR_FLIP_RETEST additionally recomputes its own swing slices from raw candle
arrays on each call (`src/channels/scalp.py:1955-1968`).

### Level validation before use

SR_FLIP_RETEST requires:
- Breakout-close confirmation of the level
- Retest distance zone
- Reclaim/hold evidence
- Wick-quality filter
- EMA alignment
- RSI context
(`src/channels/scalp.py:1969-2104`)

### Flip logic (SR_FLIP_RETEST)

Support → Resistance (or vice-versa) is inferred by:
1. Prior structural break **with close acceptance** beyond the level
2. Pullback/retest of that level from the opposite side
3. Candle-body reclaim evidence

(`src/channels/scalp.py:1969-2001,2025-2040`)

### Staleness

No explicit timestamp-based S/R staleness check.  Recency is enforced
implicitly by the fixed rolling lookback windows.

---

## 4. EMAs and Technical Indicators

### EMA periods computed

`9, 21, 50, 200` on each loaded timeframe
(`src/scanner/indicator_compute.py:81-97`).

### Full indicator set (per-timeframe)

ADX(14), ATR(14), RSI(14), Bollinger(20,2σ), MACD(12,26,9), Momentum(3),
volume SMA(20)/ratio, Stochastic RSI(14,14,3,3), Supertrend(10), Ichimoku(9,26,52),
Heikin-Ashi, Volume Profile (VPOC/VAH/VAL), Keltner(20,10), Williams %R(14),
MFI(14)
(`src/scanner/indicator_compute.py:79-225`).

### Where computed

`compute_indicators_for_candle_dict()` in `src/scanner/indicator_compute.py:229`
called by `Scanner._compute_indicators()` → `_build_scan_context()`
(`src/scanner/__init__.py:1699-1701,1863`).

### Caching

Cached per-symbol keyed on `(tf, last_close)` fingerprint
(`src/scanner/__init__.py:1850-1865`).  See staleness note above.

### Look-ahead bias risk

No explicit forward-looking indexing found in indicator computations.
The primary risk is the WS fallback injecting in-progress candle data as
closed (see §2).

### TREND_PULLBACK_EMA specifics

- **EMA filters**: EMA9 > EMA21 (> EMA50 if available) for LONG; reversed for
  SHORT (`src/channels/scalp.py:719-751`).
- **SL geometry**: `max(min_sl_pct, 1.1 × |close − EMA21|, 0.5 × ATR)`
  (`src/channels/scalp.py:817-820`).
- **Confirmation**: proximity-to-EMA zone, RSI pullback + RSI slope,
  candle momentum/reclaim checks
  (`src/channels/scalp.py:753-807`).

---

## 5. Data Pipeline — OrderFlow, CVD, Funding

### OrderFlowStore

Defined at `src/order_flow.py:256-335`.  Holds:
- OI snapshots: `deque(maxlen=200)` per symbol
- Liquidation events: `deque(maxlen=500)` per symbol
- Running CVD (quote-currency): single float per symbol
- Candle-aligned CVD snapshots: `deque(maxlen=500)` per symbol
- Latest funding rate: single float per symbol

### CVD computation

Each aggressive trade tick:
```python
delta = buy_vol_usd - sell_vol_usd
_running_cvd[symbol] += delta       # src/order_flow.py:451-472
```

Snapshot at every candle close (`k.x == True`) from kline WS handler
(`src/order_flow.py:473-485`; `src/main.py:516-520`).

### Funding rate

OIPoller fetches `/fapi/v1/premiumIndex` (`lastFundingRate`) every
`OI_POLL_INTERVAL=60s` per symbol and stores in `_funding_rates`
(`src/order_flow.py:603-620`).

### Liquidations

`forceOrder` WS events buffered, then added via `add_liquidation()`
(`src/main.py:538-577`; `src/order_flow.py:341-347`).
`get_liquidation_clusters()` aggregates into price-band clusters
(`src/order_flow.py:377-445`).

### ⚠️ MEDIUM: No historical backfill

All order-flow data warms **live-only** from pollers and WebSocket events.
No backfill happens during historical seeding at boot
(`src/bootstrap.py:248-251`; `src/main.py:519,534-536`).

After a cold start:
- CVD = 0 for all symbols until trades accumulate
- OI trend = NEUTRAL until ≥2 polling rounds complete (~2 min)
- Funding rate = None until first OI poll round
- Liquidation clusters = empty

Evaluators that require these values (`DIVERGENCE_CONTINUATION`,
`FUNDING_EXTREME_SIGNAL`, `LIQUIDATION_REVERSAL`, `WHALE_MOMENTUM`)
degrade gracefully but cannot fire during this warm-up window.

### ⚠️ MEDIUM: Dependency readiness `present=True` while empty

`_build_dependency_readiness()` sets `"present": True` whenever the state is
`"empty"` (vs `"unavailable"`) (`src/scanner/__init__.py:2381-2415`).  This
means evaluators that check `dep["present"]` will read `True` for a dependency
that has returned zero data since boot.

### ⚠️ LOW: SEED_TICK_LIMIT vs fetch cap mismatch

`SEED_TICK_LIMIT = 5000` (`config/__init__.py:348`) but
`fetch_recent_trades()` hard-caps the REST request to `min(limit, 1000)`
(`src/historical_data.py:111-116`).  At most 1000 ticks are seeded regardless
of the configured limit.

---

## 6. Key File Reference Map

| Topic | File | Key lines |
|-------|------|-----------|
| SL/TP monitor loop | `src/trade_monitor.py` | 405-416 (loop), 459-470 (price), 688-709 (SL check) |
| Evaluator dispatch | `src/channels/scalp.py` | 373-434 (evaluate), 390-405 (path list) |
| Indicator computation | `src/scanner/indicator_compute.py` | 43-226 (compute), 229-320 (per-timeframe) |
| SMC detection | `src/smc.py` | 63-177 (sweeps), 240-284 (FVG) |
| SMC orchestrator | `src/detector.py` | 72-233 |
| OrderFlowStore | `src/order_flow.py` | 256-511 |
| OIPoller | `src/order_flow.py` | 518-634 |
| Historical seeding | `src/historical_data.py` | 150-225 (seed_symbol/seed_all) |
| Structural S/R | `src/structural_levels.py` | 19-179 |
| Scanner context build | `src/scanner/__init__.py` | 1846-2067 (_build_scan_context) |
| Seed timeframes/limits | `config/__init__.py` | 340-348 |
| Channel rollout states | `config/__init__.py` | 740-827 |
| Boot order | `src/bootstrap.py` | 147-158, 224-251 |
