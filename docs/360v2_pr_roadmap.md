# 360-v2 PR Roadmap — Detailed Implementation Specs
**Date:** 2026-04-21  
**Principle:** Every PR either removes suppression, removes invalid structure, or improves observability. Nothing in this roadmap tightens signal generation. Threshold tuning is last and only after telemetry is trustworthy.

---

## Overview

| Phase | PRs | Goal | Signal Impact |
|---|---|---|---|
| 0 — Unblock | PR-1, PR-2, PR-3 | Fix bugs that silently kill signals | **+signals** |
| 1 — Disable Invalid | PR-4 | Remove channels that produce no valid output | Neutral |
| 2 — Observability | PR-5, PR-6 | Make silence diagnosable | Neutral |
| 3 — Structural Fixes | PR-7, PR-8, PR-9 | Fix paths that underfire due to bugs | **+signals** |
| 4 — Doctrine Fixes | PR-10, PR-11 | Fix SL/TP that is misaligned with thesis | Quality ↑ |
| 5 — Widen Gates | PR-12 | Loosen over-tight RSI gates | **+signals** |

**Do not start Phase 5 until Phase 0–2 are merged and telemetry is being read.**

---

## Phase 0 — Unblock Suppressed Signals

---

### PR-1: Isolate Evaluator Exceptions in ScalpChannel

**Priority:** Critical  
**Signal impact:** Adds signals — currently a crash in any evaluator silently kills all subsequent ones  
**Merge risk:** Low

#### Problem
`ScalpChannel.evaluate()` runs 14 sub-evaluators in a loop. The exception handler currently re-raises after recording telemetry:

```python
except Exception:
    self._generation_telemetry["no_signal"][_path] += 1
    _reason = self._active_no_signal_reason or "exception"
    self._generation_telemetry["no_signal_reason"][f"{_path}:{_reason}"] += 1
    raise  # ← kills all subsequent evaluators
```

If evaluator 8 (SR_FLIP_RETEST) throws, evaluators 9–14 (FUNDING_EXTREME, QUIET_COMPRESSION_BREAK, DIVERGENCE_CONTINUATION, CONTINUATION_LIQUIDITY_SWEEP, POST_DISPLACEMENT_CONTINUATION, FAILED_AUCTION_RECLAIM) never run. Zero signals from six paths, no diagnostic.

#### Change
Replace `raise` with a structured log and continue. Each evaluator must be fully isolated.

**File:** `src/channels/scalp.py` — `evaluate()` method

```python
# BEFORE
try:
    sig = evaluator(symbol, candles, indicators, smc_data, spread_pct, volume_24h_usd, regime)
except Exception:
    self._generation_telemetry["no_signal"][_path] += 1
    _reason = self._active_no_signal_reason or "exception"
    self._generation_telemetry["no_signal_reason"][f"{_path}:{_reason}"] += 1
    raise

# AFTER
try:
    sig = evaluator(symbol, candles, indicators, smc_data, spread_pct, volume_24h_usd, regime)
except Exception as exc:
    import traceback
    self._generation_telemetry["no_signal"][_path] += 1
    self._generation_telemetry["no_signal_reason"][f"{_path}:exception"] += 1
    log.error(
        "ScalpChannel evaluator {} raised for {}: {}\n{}",
        _path, symbol, exc, traceback.format_exc()
    )
    sig = None  # Continue to next evaluator
```

#### Validation
- Write a test that mocks one evaluator to raise `RuntimeError` and confirms the remaining evaluators still run and return signals.
- Confirm via telemetry snapshot that exception counts appear under `no_signal_reason` correctly.

---

### PR-2: Remove smc_data Mutation in DIVERGENCE_CONTINUATION

**Priority:** Critical  
**Signal impact:** Stabilises CVD channel output; removes phantom CVD signals  
**Merge risk:** Low

#### Problem
`_evaluate_divergence_continuation()` writes directly to the shared scan context dict:

```python
# scalp.py lines ~2597-2598
smc_data["cvd_divergence"] = _div_label
smc_data["cvd_divergence_strength"] = _div_strength
```

The scanner passes the **same dict object** to every channel for the entire scan cycle. After DIVERGENCE_CONTINUATION runs, `ScalpCVDChannel.evaluate()` reads `smc_data.get("cvd_divergence")` and sees the evaluator's local detection result instead of the SMCDetector's global signal. The scanner's scoring engine at lines 3867–3868 also reads these contaminated keys.

#### Effect on signals
- ScalpCVDChannel may emit signals from DIVERGENCE_CONTINUATION's local detection rather than real SMCDetector divergence.
- The scoring engine scores CVD confluence on unrelated signals using the contaminated value.
- After fixing, ScalpCVDChannel output will change — it will only fire when the SMCDetector genuinely detected divergence, not whenever DIVERGENCE_CONTINUATION happened to confirm it locally.

#### Change

**File:** `src/channels/scalp.py` — `_evaluate_divergence_continuation()`

Remove the two smc_data writes entirely:
```python
# DELETE THESE TWO LINES:
smc_data["cvd_divergence"] = _div_label
smc_data["cvd_divergence_strength"] = _div_strength
```

The evaluator already confirmed divergence locally using the same CVD data the SMCDetector uses. It does not need to write back. The evaluator's own signal is the output — not a side effect on shared state.

If the downstream scorer needs to know that this evaluator confirmed divergence, attach it to the signal object instead:
```python
sig.analyst_reason = f"Hidden {_div_label} CVD divergence (strength={_div_strength:.2f})"
```

#### Validation
- Confirm ScalpCVDChannel output before and after. It should not change when DIVERGENCE_CONTINUATION fires on the same scan cycle (they are independent).
- Confirm scanner scoring engine reads `ctx.smc_data.get("cvd_divergence")` as `None` (or SMCDetector-populated value) after the fix.
- Test: run a scan cycle where DIVERGENCE_CONTINUATION would fire; assert `smc_data["cvd_divergence"]` is unchanged after the ScalpChannel evaluate() call.

---

### PR-3: Add Undeclared Signal Fields to Dataclass

**Priority:** Critical  
**Signal impact:** Prevents AttributeError crashes in downstream code; fixes structural metadata persistence  
**Merge risk:** Very low

#### Problem
Three evaluators write attributes that are not declared on the `Signal` dataclass:

| Evaluator | Attribute | Line |
|---|---|---|
| SR_FLIP_RETEST | `sig.sr_flip_level` | scalp.py ~2176 |
| POST_DISPLACEMENT_CONTINUATION | `sig.pdc_breakout_level` | scalp.py ~3305 |
| FAILED_AUCTION_RECLAIM | `sig.far_reclaim_level` | scalp.py ~3608 |

Python allows this on dataclasses at runtime, so writes don't crash. But any downstream code doing `sig.sr_flip_level` (without `getattr` default) on a Signal that was not created by SR_FLIP_RETEST will raise `AttributeError`. These fields are also invisible to serialisation, logging, Redis persistence, and type checking.

#### Change

**File:** `src/channels/base.py` — `Signal` dataclass, field group after `far_reclaim_level` placeholder or at the structural metadata section.

Add three optional fields:
```python
# ---- Structural path metadata (path-specific anchors for downstream use) ----
# SR_FLIP_RETEST: the flipped S/R level that was broken and retested.
sr_flip_level: Optional[float] = None

# POST_DISPLACEMENT_CONTINUATION: the consolidation high (LONG) or low (SHORT)
# that price broke above/below to confirm re-acceleration.
pdc_breakout_level: Optional[float] = None

# FAILED_AUCTION_RECLAIM: the struct level (prior swing high/low) that was
# broken-then-recovered; used as the structural anchor by execution quality checks.
far_reclaim_level: Optional[float] = None
```

No changes needed in `scalp.py` — the writes already use the correct attribute names. The fields now simply have a declared home.

#### Validation
- Confirm `Signal()` instantiation still works with default values.
- Confirm that after building an SR_FLIP signal, `sig.sr_flip_level` is populated and `sig.pdc_breakout_level` is `None`.
- Add to the Signal serialisation test if one exists.

---

## Phase 1 — Disable Structurally Invalid Channels

---

### PR-4: Disable ScalpVWAPChannel and ScalpIchimokuChannel

**Priority:** High  
**Signal impact:** Neutral — these channels produce near-zero valid output in practice  
**Merge risk:** Very low

#### Problem

**ScalpVWAPChannel** uses `compute_vwap(highs[-50:], lows[-50:], closes[-50:], volumes[-50:])` — a rolling 50-candle window. This is not session-anchored VWAP. Institutional mean-reversion VWAP is anchored to the session open (midnight UTC or exchange open). A rolling 50-candle VWAP drifts continuously and has no structural meaning as a level. VWAP band bounces that are not anchored to the session open are not institutional levels — they are coincident noise.

**ScalpIchimokuChannel** computes Ichimoku with standard settings (Tenkan=9, Kijun=26, Senkou B=52). On a 5m chart:
- Tenkan-sen = 9 bars = 45 minutes average
- Kijun-sen = 26 bars = 2.2 hours average
- Senkou Span B = 52 bars = 4.3 hours average, projected forward 26 bars (another 2.2 hours)

The cloud represents structure from 4–6 hours ago projected 2+ hours into the future. On a 5m scalp this is meaningless lag. Standard Ichimoku is designed for daily charts where these same periods represent 9, 26, and 52 days.

#### Change

**File:** `config/__init__.py` — channel enable flags

```python
# Set to False (was True or conditional)
CHANNEL_SCALP_VWAP_ENABLED: bool = False   # Disabled: rolling VWAP is not session-anchored
CHANNEL_SCALP_ICHIMOKU_ENABLED: bool = False  # Disabled: 5m Ichimoku timeframe is invalid
```

**File:** `src/channels/scalp_vwap.py` — add guard at top of `evaluate()`

```python
def evaluate(self, ...):
    # Disabled: rolling 50-candle VWAP is not session-anchored.
    # Re-enable only after implementing true session-open VWAP anchoring.
    return None
```

**File:** `src/channels/scalp_ichimoku.py` — add guard at top of `evaluate()`

```python
def evaluate(self, ...):
    # Disabled: standard Ichimoku settings (9/26/52) are designed for daily charts.
    # On 5m, Kijun=130min and Senkou B=4.3h produce invalid structural reference.
    # Re-enable only after redesign with 5m-appropriate settings or HTF anchoring.
    return None
```

**File:** `src/runtime_truth_report.py` or equivalent — add to disabled channel report section so operators see intentional disablement, not mysterious silence.

#### Validation
- Confirm zero signals emitted from SVWP and SICH prefixes after merge.
- Confirm runtime truth report explicitly labels these channels as "intentionally disabled."

---

## Phase 2 — Observability

---

### PR-5: Fix BREAKDOWN_SHORT Telemetry

**Priority:** High  
**Signal impact:** Neutral (does not change logic), enables diagnosis of why path is silent  
**Merge risk:** Very low

#### Problem
`_evaluate_breakdown_short()` uses bare `return None` in most failure branches, unlike every other evaluator which uses `self._reject("reason")`. The telemetry counter for BREAKDOWN_SHORT shows only `no_signal_reason: none` regardless of which gate fired. You cannot distinguish between "failed volume check", "no breakdown found", "EMA mismatch", or "RSI reject."

#### Change

**File:** `src/channels/scalp.py` — `_evaluate_breakdown_short()`

Replace every bare `return None` with a descriptive `self._reject(...)`. Map:

| Current | Replace with |
|---|---|
| `return None` (after `len < 28` check) | `return self._reject("insufficient_candles")` |
| `return None` (after rolling_vols check) | `return self._reject("volume_spike_missing")` |
| `return None` (after current_vol check) | `return self._reject("volume_spike_missing")` |
| `return None` (after swing_low_level check) | `return self._reject("breakout_not_found")` |
| `return None` (after breakdown_candle_idx check) | `return self._reject("breakout_not_found")` |
| `return None` (after dist_from_swing_pct check) | `return self._reject("retest_proximity_failed")` |
| `return None` (after EMA check) | `return self._reject("ema_alignment_reject")` |
| `return None` (after RSI hard check) | `return self._reject("rsi_reject")` |
| `return None` (after FVG hard check) | `return self._reject("missing_fvg_or_orderblock")` |
| `return None` (after breakdown_vol check) | `return self._reject("volume_spike_missing")` |
| `return None` (after sl_dist check) | `return self._reject("invalid_sl_geometry")` |
| `return None` (build_channel_signal returns None) | `return self._reject("build_signal_failed")` |

Also replace `return None` at the `_pass_basic_filters` check:
```python
if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
    return self._reject("basic_filters_failed")  # was: return None
```

#### Validation
- Run a scan with BREAKDOWN_SHORT active.
- Confirm `no_signal_reason` for BREAKDOWN_SHORT now shows specific reasons rather than `none`.
- No change in which signals are emitted — only telemetry changes.

---

### PR-6: Surface Degraded Dependency States in Signal Output

**Priority:** High  
**Signal impact:** Neutral — operators can now see when signal quality is degraded  
**Merge risk:** Low

#### Problem
Two important degradation cases are invisible to operators:

1. **FUNDING_EXTREME_SIGNAL SL fallback:** When `liquidation_clusters` is absent, the path falls back to `atr_val * 1.5` for SL. The signal emits with no indication that the SL is a generic fallback, not a thesis-aligned liquidation cluster anchor. Operators cannot distinguish a strong FUNDING_EXTREME signal (SL at cluster) from a degraded one (SL is ATR×1.5).

2. **CLS sweep.index absent:** When `getattr(trend_sweep, "index", None)` returns None, the path rejects with reason "sweeps_not_detected" — indistinguishable from truly having no sweeps. The telemetry shows no sweeps when sweeps are present but missing the `.index` field.

#### Change A — FUNDING_EXTREME SL fallback flag

**File:** `src/channels/scalp.py` — `_evaluate_funding_extreme()`

After the SL fallback section:
```python
if sl_dist is None or sl_dist <= 0:
    sl_dist = atr_val * 1.5
    _sl_source = "atr_fallback"  # ADD THIS
else:
    _sl_source = "liquidation_cluster"  # ADD THIS
```

After building the signal, before returning:
```python
if _sl_source == "atr_fallback":
    note = "SL: ATR×1.5 fallback (liquidation clusters absent — thesis-aligned SL unavailable)"
    sig.execution_note = (sig.execution_note + "; " + note).lstrip("; ")
    sig.soft_penalty_total = getattr(sig, "soft_penalty_total", 0.0) + 5.0
    sig.soft_gate_flags = (sig.soft_gate_flags + ",LIQ_CLUSTER_ABSENT").lstrip(",")
```

#### Change B — CLS sweep.index missing vs no sweeps

**File:** `src/channels/scalp.py` — `_evaluate_continuation_liquidity_sweep()`

Replace the sweep.index check:
```python
# BEFORE
sweep_index = getattr(trend_sweep, "index", None)
if sweep_index is None or sweep_index < -_CLS_SWEEP_WINDOW:
    return self._reject("sweeps_not_detected")

# AFTER
sweep_index = getattr(trend_sweep, "index", None)
if sweep_index is None:
    # Sweep object exists but lacks .index — model incompatibility, not market absence
    return self._reject("sweep_index_missing")  # distinct reason token
if sweep_index < -_CLS_SWEEP_WINDOW:
    return self._reject("sweep_too_old")  # distinct from index missing
```

This produces three distinguishable rejection tokens: `sweeps_not_detected` (no sweeps), `sweep_index_missing` (SMC model issue), `sweep_too_old` (stale sweep).

#### Validation
- Run a scan where liq_clusters is absent for FUNDING_EXTREME. Confirm `execution_note` contains the fallback warning.
- Confirm `soft_gate_flags` contains `LIQ_CLUSTER_ABSENT`.
- Confirm CLS telemetry now produces distinct reason tokens for each failure mode.

---

## Phase 3 — Structural Fixes

---

### PR-7: Fix DIVERGENCE_CONTINUATION TP1/TP2 Conflict

**Priority:** Medium  
**Signal impact:** Fixes invalid TP geometry that may cause trade management errors  
**Merge risk:** Low

#### Problem
In `_evaluate_divergence_continuation()`, both TP1 and TP2 are computed from the same 20-bar lookback window:

```python
# LONG path — both use highs[-20:]
tp1 = max(_div_win_highs) if _div_win_highs else 0.0  # same source as tp2
tp2 = max(float(h) for h in highs[-20:]) ...          # identical result
```

Result: TP1 = TP2 in most cases. Trade management logic that expects TP2 > TP1 will behave incorrectly.

#### Change

**File:** `src/channels/scalp.py` — `_evaluate_divergence_continuation()`

Use a narrower window for TP1 (immediate target) and the full window for TP2 (swing target):

```python
# LONG path
if direction == Direction.LONG:
    # TP1: nearest swing high from the second half of the divergence window
    # (the high from which the bearish divergence reversed, the immediate target)
    _tp1_highs = [float(h) for h in highs[-10:]] if len(highs) >= 10 else []
    tp1 = max(_tp1_highs) if _tp1_highs else 0.0
    if tp1 <= close:
        tp1 = close + sl_dist * 1.5

    # TP2: full 20-bar swing high (wider structural target)
    _tp2_highs = [float(h) for h in highs[-20:]] if len(highs) >= 20 else []
    tp2 = max(_tp2_highs) if _tp2_highs else 0.0
    if tp2 <= close or tp2 <= tp1:
        tp2 = close + sl_dist * 2.5

# SHORT path — mirror logic using lows
else:
    _tp1_lows = [float(l) for l in lows[-10:]] if len(lows) >= 10 else []
    tp1 = min(_tp1_lows) if _tp1_lows else 0.0
    if tp1 >= close:
        tp1 = close - sl_dist * 1.5

    _tp2_lows = [float(l) for l in lows[-20:]] if len(lows) >= 20 else []
    tp2 = min(_tp2_lows) if _tp2_lows else 0.0
    if tp2 >= close or tp2 >= tp1:
        tp2 = close - sl_dist * 2.5
```

#### Validation
- Assert `sig.tp2 > sig.tp1` (LONG) and `sig.tp2 < sig.tp1` (SHORT) in test.
- Confirm the 10-bar TP1 and 20-bar TP2 produce distinct values in representative test data.

---

### PR-8: Fix CLS sweep.index Dependency

**Priority:** Medium  
**Signal impact:** Adds CLS signals if SMC model lacks `.index` attribute  
**Merge risk:** Medium (requires checking SMC model)

#### Problem
`_evaluate_continuation_liquidity_sweep()` requires `sweep.index` to determine sweep recency. If the sweep object does not have this attribute, the path always rejects with "sweep_too_old" (after PR-6) or "sweeps_not_detected" (before PR-6), even when valid sweeps exist within the last 10 candles.

#### Step 1 — Verify SMC sweep model

**File:** `src/smc.py`

Check whether the sweep objects returned by the SMCDetector have an `index` field. If the sweep dataclass is:
```python
@dataclass
class LiquiditySweep:
    direction: Direction
    level: float
    price: float
    # index: int  ← missing?
```

Add it:
```python
@dataclass
class LiquiditySweep:
    direction: Direction
    level: float
    price: float
    index: int = -1  # Bar index within the candle array (negative offset from current)
```

Ensure the SMCDetector populates `index` when creating sweep objects. Use negative offsets matching the evaluator's convention (e.g., `-2` means 2 bars back from current).

#### Step 2 — Add position-based fallback in CLS

If modifying the SMC model is not immediately safe, add a fallback that estimates recency from the sweep's position in the list:

**File:** `src/channels/scalp.py` — `_evaluate_continuation_liquidity_sweep()`

```python
sweep_index = getattr(trend_sweep, "index", None)
if sweep_index is None:
    # SMC model does not expose .index — use list position as recency proxy.
    # Position 0 = most recent sweep. Treat position 0 as index=-2 (2 bars ago),
    # position 1 as -3, etc. This is a conservative estimate.
    sweep_position = sweeps.index(trend_sweep) if trend_sweep in sweeps else 0
    sweep_index = -(sweep_position + 2)
    # Flag in telemetry that we used the fallback
    self._generation_telemetry["no_signal_reason"]["CLS:sweep_index_estimated"] = \
        self._generation_telemetry["no_signal_reason"].get("CLS:sweep_index_estimated", 0) + 1
```

#### Validation
- Confirm CLS fires on test data where sweep objects have and do not have `.index`.
- Confirm the fallback produces reasonable recency estimates.
- After merging, watch `sweep_index_estimated` in telemetry to determine how often the fallback is used — if it's frequent, prioritise the SMC model fix.

---

### PR-9: Fix QUIET_COMPRESSION_BREAK SL Width

**Priority:** Medium  
**Signal impact:** Reduces false SL hits; improves signal quality without tightening entry  
**Merge risk:** Low

#### Problem
Current SL for LONG: `sl = bb_lower * (1 - 0.001)` — 0.1% below the lower Bollinger Band.

In QUIET regime (which is the only regime this path fires in), the Bollinger Band width is below 1.5% of price (that's the compression gate). A 0.1% SL on an already-narrow band places the stop within normal tick noise for most pairs. The SL will be hit before the compression resolves.

#### Change

**File:** `src/channels/scalp.py` — `_evaluate_quiet_compression_break()`

Replace the SL calculation with an ATR-based floor:

```python
atr_val = ind.get("atr_last", close * 0.002)

if direction == Direction.LONG:
    # SL: below lower BB boundary with ATR buffer, minimum 0.3% of close
    sl_from_bb = bb_lower - atr_val * 0.5
    sl_from_pct = close * (1 - 0.003)
    sl = min(sl_from_bb, sl_from_pct)  # further of the two (more room)
else:
    # SL: above upper BB boundary with ATR buffer
    sl_from_bb = bb_upper + atr_val * 0.5
    sl_from_pct = close * (1 + 0.003)
    sl = max(sl_from_bb, sl_from_pct)
```

This gives a minimum SL distance of 0.3% plus ATR buffer — survivable through normal QUIET-regime noise.

#### Validation
- Assert `abs(sig.entry - sig.stop_loss) / sig.entry >= 0.002` (minimum 0.2% SL distance).
- Run test with a tight BB (width = 0.8%) and confirm SL is not trivially close.

---

## Phase 4 — Doctrine Fixes

---

### PR-10: Cap VOLUME_SURGE_BREAKOUT and BREAKDOWN_SHORT TP at Scalp Horizon

**Priority:** Medium  
**Signal impact:** Signals still emit; TPs become realistic for 5m trading  
**Merge risk:** Low

#### Problem
Both paths use a "measured move" TP: `measured_move = swing_high - base_of_range`. On a volatile 5m pair, a 20-bar range can easily be $300–$800 on BTCUSDT, making TP1 = `close + $300+` — this is a swing-trade target, not a scalp target. Many of these signals will expire before TP1 is touched.

#### Change

**File:** `src/channels/scalp.py` — both `_evaluate_volume_surge_breakout()` and `_evaluate_breakdown_short()`

Add a TP cap after computing measured_move:

```python
# Cap measured_move to a realistic scalp horizon: max 3× sl_dist for TP1
# This prevents swing-trade targets being emitted on a 5m scalp path.
MAX_SCALP_TP_MULT = 3.0
if measured_move > sl_dist * MAX_SCALP_TP_MULT:
    measured_move = sl_dist * MAX_SCALP_TP_MULT

# For SURGE BREAKOUT (LONG):
tp1 = close + measured_move * 1.0
tp2 = close + measured_move * 1.5
tp3 = close + measured_move * 2.0

# For BREAKDOWN SHORT (SHORT):
tp1 = close - measured_move * 1.0
tp2 = close - measured_move * 1.5
tp3 = close - measured_move * 2.0
```

The cap only applies when the measured move exceeds 3×sl_dist. Textbook breakouts with realistic measured moves pass unchanged.

#### Validation
- Test with a large swing_high range ($800 on BTC). Confirm TP1 is capped at 3×sl_dist rather than $800 beyond entry.
- Test with a small range. Confirm uncapped path is unchanged.

---

### PR-11: Fix FUNDING_EXTREME SL Hierarchy

**Priority:** Medium  
**Signal impact:** Signals still emit; SL is properly thesis-aligned when data exists  
**Merge risk:** Low

#### Problem
When `liquidation_clusters` is absent, FUNDING_EXTREME falls back to `atr_val * 1.5`. This is a reasonable fallback but there is no ordering logic — the current code picks the smallest cluster distance, which may be tighter than the ATR floor. There is also no minimum SL floor to prevent a mechanically tight SL when the nearest cluster is very close to current price.

#### Change

**File:** `src/channels/scalp.py` — `_evaluate_funding_extreme()`

Apply a clear hierarchy with explicit minimum:

```python
MIN_SL_ATR_MULT = 0.8  # SL must be at least 0.8× ATR regardless of cluster distance

# Find nearest cluster beyond minimum distance
sl_dist = None
for cluster in liq_clusters:
    cluster_price = cluster.get("price") if isinstance(cluster, dict) else getattr(cluster, "price", None)
    if cluster_price is None:
        continue
    cluster_price = float(cluster_price)
    if direction == Direction.LONG and cluster_price < close:
        liq_dist = (close - cluster_price) * 1.1
        # Only use cluster if it provides at least minimum SL room
        if liq_dist >= atr_val * MIN_SL_ATR_MULT:
            if sl_dist is None or liq_dist < sl_dist:
                sl_dist = liq_dist
    elif direction == Direction.SHORT and cluster_price > close:
        liq_dist = (cluster_price - close) * 1.1
        if liq_dist >= atr_val * MIN_SL_ATR_MULT:
            if sl_dist is None or liq_dist < sl_dist:
                sl_dist = liq_dist

# Fallback with explicit floor
if sl_dist is None or sl_dist <= 0:
    sl_dist = atr_val * 1.5
    _sl_degraded = True
else:
    _sl_degraded = False
```

The `_sl_degraded` flag feeds into PR-6's execution_note logic.

#### Validation
- Test with no liquidation_clusters → sl_dist = atr × 1.5, `_sl_degraded = True`.
- Test with a very close cluster (< 0.8×ATR from close) → cluster is skipped, fallback used.
- Test with valid cluster → sl_dist = cluster distance × 1.1.

---

## Phase 5 — Widen Over-Tight Gates

**Do not merge until Phase 0–2 are live and telemetry shows the corrected baseline.**

---

### PR-12: Widen RSI Gates on Three Paths

**Priority:** Low (tuning — do last)  
**Signal impact:** Adds signals from TREND_PULLBACK and LIQUIDATION_REVERSAL  
**Merge risk:** Medium (changes signal generation rate)

#### Context
After PR-1 is live, run the system for at least one week and collect telemetry on rejection reasons. If `rsi_reject` is the top rejection reason for TREND_PULLBACK, LIQUIDATION_REVERSAL, or FUNDING_EXTREME, proceed with this PR.

#### Change A — TREND_PULLBACK_EMA RSI gate

**File:** `src/channels/scalp.py` — `_evaluate_trend_pullback()`

```python
# BEFORE: hard gate 40–60
if rsi_val is not None and not (40 <= rsi_val <= 60):
    return self._reject("rsi_reject")

# AFTER: hard gate 35–65, soft penalty at 35–40 or 60–65
if rsi_val is not None:
    if direction == Direction.LONG:
        if rsi_val < 35 or rsi_val > 65:
            return self._reject("rsi_reject")
        if rsi_val < 40:
            sig_rsi_penalty = 4.0  # borderline low — apply after signal built
    else:
        if rsi_val < 35 or rsi_val > 65:
            return self._reject("rsi_reject")
        if rsi_val > 60:
            sig_rsi_penalty = 4.0
```

Apply the penalty to `sig.soft_penalty_total` after building the signal.

#### Change B — LIQUIDATION_REVERSAL RSI gate

**File:** `src/channels/scalp.py` — `_evaluate_liquidation_reversal()`

```python
# BEFORE: hard gate rsi < 25 for LONG, rsi > 75 for SHORT
if reversal_direction == Direction.LONG:
    if rsi_val is not None and rsi_val >= 25:
        return self._reject("rsi_reject")

# AFTER: hard gate at 30/70; soft penalty at 25–30 / 70–75
if reversal_direction == Direction.LONG:
    if rsi_val is not None:
        if rsi_val >= 30:
            return self._reject("rsi_reject")
        # RSI 25–29: cascade reversal still possible but weaker
        # No penalty needed — RSI < 30 is already strong enough confirmation
else:
    if rsi_val is not None:
        if rsi_val <= 70:
            return self._reject("rsi_reject")
```

**Note:** Only widen if telemetry shows LIQUIDATION_REVERSAL is being blocked by RSI at reasonable RSI values (e.g., 26–29). If the market is never reaching RSI < 25 before cascade reversals, this is the wrong fix — look at the cascade_pct threshold instead.

#### Validation
- Collect baseline rejection counts for each path before merging.
- After merging, compare rejection counts. Signal count should increase; quality tier distribution should not degrade significantly.
- If quality tier distribution (A+ / B / WATCHLIST ratio) degrades, the gate widening was too aggressive — roll back or add soft penalties.

---

## Do Not Do List

These things look tempting but should not be done:

| Temptation | Why Not |
|---|---|
| Lowering ADX thresholds to get more signals | Will produce more noise in ranging markets. Not the bottleneck. |
| Removing FVG/OB requirements from structural paths | These are quality gates, not suppression bugs. Soft penalty is already in place for fast regimes. |
| Adding new paths before fixing existing bugs | More paths into a broken pipeline produces more contaminated output, not more valid signals. |
| Tuning soft penalty weights | Penalty weights only matter when confidence scoring is trustworthy. Fix the bugs first. |
| Enabling ORB with the current proxy logic | The proxy (last 8 bars) has no relationship to session opens. Will produce random signals. |
| Enabling VWAP or Ichimoku before redesign | Rolling VWAP and 5m Ichimoku are structurally wrong, not just misconfigured. |

---

## Telemetry Checkpoints

After each phase, read the telemetry before proceeding:

**After Phase 0 (PR-1, 2, 3):**
- `no_signal_reason` should now show structured reasons for all 14 paths
- Exception count for any path should drop to zero if there were hidden crashes
- CVD channel output should be independent of DIVERGENCE_CONTINUATION firing

**After Phase 1 (PR-4):**
- Zero signals from SVWP and SICH prefixes
- Runtime truth report shows those channels as intentionally disabled

**After Phase 2 (PR-5, 6):**
- BREAKDOWN_SHORT rejection reasons are visible
- FUNDING_EXTREME signals with degraded SL are flagged in execution_note
- CLS sweep.index vs no-sweeps are distinguishable

**After Phase 3 (PR-7, 8, 9):**
- DIVERGENCE_CONTINUATION TP2 > TP1 in all signals
- CLS fires on valid setups (if SMC model has .index)
- QUIET_COMPRESSION_BREAK signals survive longer before SL hit

**After Phase 4 (PR-10, 11):**
- SURGE and BREAKDOWN TPs are within realistic scalp distances
- FUNDING_EXTREME SL hierarchy is explicit in execution_note

**After Phase 5 (PR-12) — run for 1 week, then evaluate:**
- TREND_PULLBACK and LIQUIDATION_REVERSAL signal counts vs quality tier distribution
- If A+ / B tier ratio holds, gate widening was correct
- If WATCHLIST / FILTERED count spikes, roll back or add soft penalties
