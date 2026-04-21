# 360-v2 Full Codebase Audit
**Date:** 2026-04-20  
**Scope:** All 15 audit dimensions from the checklist  
**Files audited:** `src/channels/base.py`, `src/channels/scalp.py`, all 7 specialist channels, `src/scanner/__init__.py`, `config/__init__.py`

---

## Audit Summary

| Dimension | Status |
|---|---|
| 1. Crypto Market Reality | Mixed — strong core, weak breakout/VWAP/Ichimoku |
| 2. Signal Generation Pipeline | Mostly sound; exception handling has critical gap |
| 3. Data Integrity / Dependencies | Several paths silently degrade or hard-gate on missing data |
| 4. Shared-State / Mutation | **Critical confirmed bug** — DIVERGENCE_CONTINUATION contaminates smc_data |
| 5. Confidence / Scoring | Evaluator confidence boosts are dead code; soft_penalty_total survives |
| 6. SL / TP | Mixed — structural paths good; breakout TPs too ambitious; some SLs too tight |
| 7. Timing / Execution | WHALE_MOMENTUM, LIQUIDATION_REVERSAL structurally late |
| 8. Structure Quality | SR_FLIP, FAR, CLS, PDC are sound; ORB is fake; VWAP is rolling |
| 9. Path-by-Path | Detailed below |
| 10. Bug Audit | 7 confirmed bugs, 3 high-risk patterns |
| 11. Retail Indicator Dependency | Ichimoku and VWAP are invalid; divergence is medium |
| 12. Runtime Truth / Observability | Telemetry good in ScalpChannel; BREAKDOWN_SHORT breaks it |
| 13. Market-Fit Classification | Classified per path below |
| 14. Prioritization | Critical → data integrity → structural → cleanup |
| 15. Final Verdict | System is salvageable. Signal under-generation is multi-causal. |

---

## 1. Crypto Market Reality Audit

### What the system gets right
- **LIQUIDITY_SWEEP_REVERSAL** — Uses sweep detection + momentum persistence. Structurally sound thesis.
- **SR_FLIP_RETEST** — Requires close-confirmed breakout acceptance, not wick-only. Close proximity gating. Genuinely strong.
- **FAILED_AUCTION_RECLAIM** — Detects failed acceptance by requiring close-at-level, measures tail for TP. Crypto-native.
- **CONTINUATION_LIQUIDITY_SWEEP** — Trend + sweep + reclaim confirmation. Sound institutional pattern.
- **POST_DISPLACEMENT_CONTINUATION** — Body ratio check, volume multiple, tight consolidation window. Realistic.
- **FUNDING_EXTREME_SIGNAL** — Liquidation cluster SL anchoring, structure-first TP1. Genuinely differentiated.
- **LIQUIDATION_REVERSAL** — CVD divergence + cascade % + volume spike + zone proximity. Strong multi-factor design.

### What the system gets wrong
- **VWAP channel** — Uses a rolling 50-candle VWAP window. This is not session-anchored VWAP. Mean-reversion signals around a rolling window are structurally invalid as institutional VWAP plays.
- **Ichimoku channel (5m)** — Standard Ichimoku settings (9/26/52) are designed for daily charts. On 5m, Kijun (26 bars = 2.2 hours) and Senkou B (52 bars = 4.3 hours) produce clouds that lag far too much for scalp use. Structurally invalid timeframe.
- **OPENING_RANGE_BREAKOUT** — Disabled by default. The proxy used (last 8 bars) is acknowledged in the comment as not institutional-grade. Correct to leave disabled.
- **VOLUME_SURGE_BREAKOUT** — Fires LONG only. TP1 is `close + measured_move` where `measured_move = swing_high - base_of_range`. On a 5m chart this can be 2–5% on a volatile pair — not a scalp target. Timing risk: fires on a pullback from a breakout, not the breakout itself.
- **BREAKDOWN_SHORT** — Mirror of above, same TP ambition problem. Narrative is "dead-cat bounce entry" — inherently timing-sensitive.
- **TREND_PULLBACK_EMA** — RSI 40–60 gate eliminates valid pullbacks in strong trends where RSI naturally sits at 35 or 65.

---

## 2. Signal Generation Pipeline Audit

### How signals die — confirmed death points

The `ScalpChannel.evaluate()` loop runs all 14 sub-evaluators sequentially. Each evaluator uses `self._reject(reason)` to record telemetry when returning `None`. This is good.

**Critical gap:** The exception handler **re-raises** after recording telemetry:
```python
except Exception:
    self._generation_telemetry["no_signal"][_path] += 1
    ...
    raise  # ← kills all subsequent evaluators
```
If any evaluator throws (e.g., SR_FLIP_RETEST crashing on the dynamic attribute write `sig.sr_flip_level`), every evaluator after it is silently skipped. The evaluator order is:
1. standard → 2. trend_pullback → 3. liquidation_reversal → 4. whale_momentum → 5. volume_surge_breakout → 6. breakdown_short → 7. opening_range_breakout → **8. sr_flip_retest** → 9. funding_extreme → 10. quiet_compression_break → 11. divergence_continuation → 12. continuation_liquidity_sweep → 13. post_displacement_continuation → 14. failed_auction_reclaim

A crash in evaluator 8 silently kills evaluators 9–14 for that entire scan cycle.

### Low output causes — confirmed
- **True market absence:** valid and expected some of the time
- **Over-gating:** TREND_PULLBACK RSI 40–60, FUNDING_EXTREME RSI < 55 for LONG, LIQUIDATION_REVERSAL RSI < 25 for LONG  
- **Missing dependencies:** CLS requires `sweep.index` attribute — if sweep objects don't have this field, path always fails silently
- **Data mutation:** DIVERGENCE_CONTINUATION writes to `smc_data`, potentially blocking CVD channel (see Section 4)
- **Geometry rejection:** several paths compute tight SLs that then fail the `sl >= close` check under dynamic adjustment

---

## 3. Data Integrity / Dependency Audit

### Per-dependency runtime risk

| Dependency | Paths That Need It | Risk |
|---|---|---|
| `sweeps` | LIQUIDITY_SWEEP_REVERSAL, CLS | CLS also needs `sweep.index` — may be absent on some SMC impl |
| `cvd` | LIQUIDATION_REVERSAL, DIVERGENCE_CONTINUATION, FUNDING_EXTREME | All handle `None` gracefully ✓ |
| `funding_rate` | FUNDING_EXTREME | Hard-rejects with telemetry if missing ✓ |
| `liquidation_clusters` | FUNDING_EXTREME | Falls back to ATR×1.5 if absent — SL quality degrades silently |
| `whale_alert` or `volume_delta_spike` | WHALE_MOMENTUM | Hard-rejects with telemetry ✓ |
| `recent_ticks` | WHALE_MOMENTUM | Checks `__dependency_source_state` — dependency-aware ✓ |
| `order_book` | WHALE_MOMENTUM | Three-tier handling (None / top-of-book / full depth) ✓ |
| `fvg` | Multiple paths | Several hard-gate on absence; others soft-penalise |
| `orderblocks` | Multiple paths | Same as FVG |
| `cvd_divergence` (smc_data key) | ScalpCVDChannel | **Contaminated by DIVERGENCE_CONTINUATION — see Section 4** |
| `cvd_divergence_age` | ScalpCVDChannel | Fails-closed if missing and `_CVD_REQUIRE_METADATA=True` |

### Key degradation risks
1. **liquidation_clusters absent:** FUNDING_EXTREME_SIGNAL falls back to `atr * 1.5` SL. No flag is raised to operators that the SL is degraded. The signal emits as if the SL is thesis-valid when it is actually a generic ATR fallback.
2. **Sweep objects without `.index`:** `getattr(trend_sweep, "index", None)` returns `None` → CLS always rejects with "sweeps_not_detected". Silent — no distinction between "no sweeps" and "sweep present but attribute missing."
3. **smc_data contamination:** detailed in Section 4.

---

## 4. Shared-State / Mutation Audit

### Confirmed Bug: DIVERGENCE_CONTINUATION writes to shared smc_data

In `_evaluate_divergence_continuation()` (scalp.py line 2597–2598):
```python
smc_data["cvd_divergence"] = _div_label
smc_data["cvd_divergence_strength"] = _div_strength
```

This is the **same dict object** (`ctx.smc_data`) passed to every channel for the current scan cycle. Confirmed by the scanner at line 3114 in `scanner/__init__.py`:
```python
smc_data=ctx.smc_data,  # same object for all channel calls
```

**Effect chain:**
1. ScalpChannel runs `_evaluate_divergence_continuation` → writes `"cvd_divergence"` to `smc_data`
2. Scanner then calls `ScalpCVDChannel.evaluate()` with the same `smc_data`
3. ScalpCVDChannel reads `smc_data.get("cvd_divergence")` — now sees DIVERGENCE_CONTINUATION's local detection result instead of the SMCDetector's global signal
4. The scanner's own scoring engine reads `ctx.smc_data.get("cvd_divergence")` at line 3867 — also contaminated

**What this means in practice:**
- When DIVERGENCE_CONTINUATION fires, it stamps "BULLISH" or "BEARISH" onto `smc_data["cvd_divergence"]` regardless of what the SMCDetector originally put there (or didn't)
- ScalpCVDChannel will then see a divergence signal that it didn't originate, and may emit a second signal from the same underlying event
- The scanner's scoring engine reads the contaminated value to score CVD confluence on unrelated signals

**Severity: Critical.** This is a confirmed architectural bug that produces phantom CVD signals and corrupts the scorer's inputs.

### Other dynamic attribute writes (undeclared on Signal dataclass)

Three evaluators write attributes not declared in the `Signal` dataclass:

| Evaluator | Attribute Written | Line |
|---|---|---|
| SR_FLIP_RETEST | `sig.sr_flip_level` | scalp.py ~2176 |
| POST_DISPLACEMENT_CONTINUATION | `sig.pdc_breakout_level` | scalp.py ~3305 |
| FAILED_AUCTION_RECLAIM | `sig.far_reclaim_level` | scalp.py ~3608 |

Python allows dynamic attribute writes on dataclasses, so these won't crash on write. However:
- Any downstream code that tries to `getattr(sig, "sr_flip_level", None)` — correct pattern — will work
- Any code that accesses `sig.sr_flip_level` directly (no default) will raise `AttributeError` if the signal was not created by SR_FLIP_RETEST
- These attributes are not serialised, logged, or persisted by the standard Signal machinery
- They are not visible in telemetry or reports unless explicitly handled

**Severity: Medium.** Structural metadata is not preserved through the full pipeline. If any code tries `sig.sr_flip_level` on a non-SR_FLIP signal, it will crash.

---

## 5. Confidence / Scoring Audit

### Evaluator confidence boosts are dead code

Multiple evaluators do:
```python
sig.confidence = min(100.0, sig.confidence + 8.0)
```

The code comments themselves acknowledge this is overwritten three times by the scanner pipeline. This pattern is **dead code for the final confidence value**. The comments confirm it explicitly:
> "the scanner's _prepare_signal() pipeline overwrites this value three times (legacy confidence → score_signal_components → composite scoring engine) so this mutation does NOT affect the final signal confidence"

This means the path-specific quality differentiation intended by these boosts (e.g., TREND_PULLBACK gets +8, ORB gets +5, LIQUIDATION gets +10) never reaches the final score. The only mechanism that survives is `soft_penalty_total`.

### What actually survives
- `sig.soft_penalty_total` — accumulated by evaluators, deducted by scanner post-scoring ✓
- `sig.soft_gate_flags` — string of which soft gates fired ✓
- `sig.setup_class` — used by the scoring engine for family-aware weights ✓

### Consequence
Strong structural setups and weaker generic setups receive the same raw score from the composite scorer before penalty deduction. The differentiation exists only through soft penalties (penalising weakness), not through positive boosts (rewarding strength). This asymmetric scoring design means the best paths are not preferentially elevated — only the worst are suppressed.

---

## 6. Stop-Loss / Take-Profit Audit

### Per-path SL/TP assessment

**LIQUIDITY_SWEEP_REVERSAL (standard path)**
- SL: swept level ± 0.1% buffer, floored at 0.5×ATR. Thesis-aligned ✓
- TP: nearest FVG midpoint (TP1), 20-bar swing high (TP2), 4×sl_dist (TP3). Reasonable ✓

**TREND_PULLBACK_EMA**
- SL: 1.1×distance to EMA21. Reasonable for the thesis ✓
- TP1: 20-bar swing high — could be very close. Risk: TP1 = TP2 if both are the same swing
- TP2: 4h swing high — appropriate, may be wide for a 5m entry

**LIQUIDATION_REVERSAL**
- SL: cascade low/high ± 0.3% buffer. Thesis-aligned ✓
- TP: Fibonacci retracement of cascade (38.2/61.8/100%). Good thesis alignment ✓

**WHALE_MOMENTUM**
- SL: 5-bar swing low/high + 0.1% buffer. Better than ATR fallback ✓
- TP: 1.5R/2.5R/4.0R from entry. Generic — not thesis-aligned to the whale event magnitude

**VOLUME_SURGE_BREAKOUT**
- SL: 0.8% below swing high. Fixed percentage — not structural ✗
- TP: `close + measured_move` where measured_move = swing range. **Too far for a 5m scalp.** On BTCUSDT with a $500 range, TP1 could be $500 above entry. This is a swing TP on a scalp timeframe.

**BREAKDOWN_SHORT**
- Same TP magnitude problem as VOLUME_SURGE_BREAKOUT ✗
- SL: 0.8% above swing low. Same fixed-percentage issue ✗

**OPENING_RANGE_BREAKOUT**
- SL: beyond far range boundary. Thesis-aligned ✓
- TP: range height multiples (1×, 1.5×, 2×). Appropriate for ORB logic ✓
- But the range is fake (last 8 bars, not true session open range) — irrelevant until redesigned

**SR_FLIP_RETEST**
- SL: wick overshoot + ATR buffer + structural buffer. Most sophisticated SL in the system ✓
- TP1: 20-bar swing — appropriate ✓
- TP2: 4h swing — appropriate ✓

**FUNDING_EXTREME_SIGNAL**
- SL: nearest liquidation cluster × 1.1 → falls back to ATR×1.5 when absent. Degraded silently ✗
- TP1: nearest FVG/OB in direction — thesis-aligned ✓
- TP2/3: flat R multiples — acceptable fallback

**QUIET_COMPRESSION_BREAK**
- SL: `bb_lower × (1 - 0.001)` for LONG — only 0.1% below lower BB. Extremely tight. On altcoins this will be hit by wicks constantly ✗
- TP: based on BB bandwidth (which is very narrow in QUIET regime). Small targets, but at least internally consistent ✓

**DIVERGENCE_CONTINUATION**
- SL: EMA21 ± 0.5%. Reasonable ✓
- TP1: max of highs[-20:] — same window as divergence detection. **TP1 and TP2 can be equal or TP2 < TP1** because both are derived from the same 20-bar window ✗

**CONTINUATION_LIQUIDITY_SWEEP**
- SL: sweep level - 0.3×ATR buffer. Thesis-aligned ✓
- TP: FVG midpoint → swing high fallback → 2.5R. Appropriate ✓

**POST_DISPLACEMENT_CONTINUATION**
- SL: consolidation low - 0.3×ATR. Thesis-aligned ✓
- TP: displacement height × 1.0/1.5/2.5 from entry. Measured move — thesis-aligned ✓

**FAILED_AUCTION_RECLAIM**
- SL: auction wick extreme - 0.3×ATR. Thesis-aligned — correct invalidation point ✓
- TP: tail × 1.0/1.5/2.5. Measured from the rejection magnitude. Thesis-aligned ✓

---

## 7. Timing / Execution Reality Audit

**WHALE_MOMENTUM**  
Signal fires after processing `recent_ticks` and confirming `buy_vol >= sell_vol × 2.0`. By the time ticks are aggregated, the impulse is 1–3 bars old. For a scalp on 1m, this is often already late for a clean entry. The swing-based SL helps, but entry timing is a structural weakness.

**LIQUIDATION_REVERSAL**  
Requires `cascade_pct >= 2.0%` over 3 candles, then CVD divergence, then zone proximity, then volume spike on the current candle. The "current candle" volume spike suggests the reversal is already in progress. This is an "entering the reversal" pattern not a "predicting the reversal" pattern — which is fine if price has not already run. Risk is that the setup completes when price is 0.5–1% off the cascade low already.

**FUNDING_EXTREME_SIGNAL**  
Funding rate is updated every 8 hours on most exchanges. Between updates, a stale funding extreme may persist long after it has become irrelevant. No freshness check on the funding_rate value itself — only presence. This means a signal may fire on 7-hour-old data.

**DIVERGENCE_CONTINUATION**  
Fires when price is within 1.5% of EMA21 AND hidden divergence is confirmed over the last 20 candles. The divergence lookback uses close-price lows/highs, which are noisy on 5m. The timing is lagged by design (detecting a "continuation pattern"), but the entry confirmation is weak — there is no explicit current-candle rejection/momentum requirement, just proximity to EMA and a 20-bar divergence pattern.

**SR_FLIP_RETEST / FAILED_AUCTION_RECLAIM / POST_DISPLACEMENT_CONTINUATION**  
These three have the most realistic entry timing — they require the structural event to have already happened (flip confirmed, auction failed, displacement occurred) and then fire on the retest/reclaim/re-acceleration. Entry arrives after confirmation, which is appropriate for crypto.

---

## 8. Structure Quality Audit

### Strong structural implementation
- **SR_FLIP_RETEST** — 41-candle prior window, 8-candle flip search (closed candles only), close-acceptance requirement, proximity zone with soft penalty. The cleanest structural detection in the codebase.
- **FAILED_AUCTION_RECLAIM** — Correctly separates struct reference window from auction window. Requires close-at-level for failed acceptance (not just wick). Measures wick tail for TP calibration. Sound.
- **CONTINUATION_LIQUIDITY_SWEEP** — Sweep recency gating (10-bar window), reclaim confirmation, momentum agreement. Clean structural logic.
- **POST_DISPLACEMENT_CONTINUATION** — Body ratio check (≥60%), volume multiple (≥2.5×), consolidation territory gate (must remain within displacement body), tight consolidation range check. Methodical.

### Weak or invalid structural claims
- **OPENING_RANGE_BREAKOUT** — The "range" is `highs[-8:-4]` and `lows[-8:-4]`. This is the 4 bars before the most recent 4 bars. It has no relationship to any session open. It will produce different ranges for every pair on every scan regardless of actual session timing. Disabled is correct.
- **VWAP channel** — 50-candle rolling VWAP is not anchored to any structural event. It drifts continuously. VWAP ±1SD bands from a rolling window do not represent institutional mean-reversion zones.
- **Ichimoku channel** — On 5m, Kijun-sen (26 bars = 130 minutes), Senkou B (52 bars = 4.3 hours), cloud projection (26 bars forward = 130 minutes). These represent moving averages of price ranges over multi-hour windows projected forward — not meaningful structure for a 5m scalp.

---

## 9. Path-by-Path Audit

| Path | Crypto-Native? | Data Needs Met? | Entry Timing | SL/TP Aligned? | Verdict |
|---|---|---|---|---|---|
| LIQUIDITY_SWEEP_REVERSAL | ✓ Strong | FVG+sweeps: usually present | Good | ✓ | **Keep** |
| TREND_PULLBACK_EMA | Moderate | EMAs + FVG/OB | Good | Mostly ✓ | **Fix** (RSI 40–60 too tight) |
| LIQUIDATION_REVERSAL | ✓ Strong | CVD + zones: risky | Late by design | ✓ | **Keep with monitoring** |
| WHALE_MOMENTUM | Moderate | Ticks + OB: fragile | Often late | Partial (TP generic) | **Fix timing** |
| VOLUME_SURGE_BREAKOUT | Weak | FVG: soft in fast | Good | SL generic; TP too far ✗ | **Fix TP** |
| BREAKDOWN_SHORT | Weak | FVG: soft in fast | Good | Same as above ✗ | **Fix TP** |
| OPENING_RANGE_BREAKOUT | Invalid | Session anchor missing | N/A | N/A | **Disable** (already is) |
| SR_FLIP_RETEST | ✓ Strong | FVG: soft in fast | ✓ | ✓ | **Keep** |
| FUNDING_EXTREME_SIGNAL | ✓ Strong | Liq clusters: unreliable | Acceptable | SL degrades silently ✗ | **Fix SL fallback transparency** |
| QUIET_COMPRESSION_BREAK | Moderate | FVG + BB | Acceptable | SL too tight ✗ | **Fix SL** |
| DIVERGENCE_CONTINUATION | Moderate | CVD: present | Lagged | TP1/TP2 can conflict ✗ | **Fix TP + contamination** |
| CONTINUATION_LIQUIDITY_SWEEP | ✓ Strong | Sweeps: needs .index | ✓ | ✓ | **Fix .index dependency** |
| POST_DISPLACEMENT_CONTINUATION | ✓ Strong | Volume history | ✓ | ✓ | **Keep** |
| FAILED_AUCTION_RECLAIM | ✓ Strong | Minimal | ✓ | ✓ | **Keep** |

### Specialist Channels

| Channel | Crypto-Native? | Core Issue | Verdict |
|---|---|---|---|
| ScalpFVGChannel | ✓ Good | Retest proximity at 50% zone width is loose; age decay is clean | **Keep, tune proximity** |
| ScalpCVDChannel | ✓ Good | State contamination from DIVERGENCE_CONTINUATION; `_CVD_REQUIRE_METADATA=True` means absent metadata = silent death | **Fix contamination first** |
| ScalpVWAPChannel | ✗ Invalid | Rolling 50-candle VWAP is not institutional VWAP | **Disable until session-anchored** |
| ScalpDivergenceChannel | Moderate | RSI/MACD divergence on 5m is noisy; MTF gate applied | **Keep with narrow scope** |
| ScalpSupertrendChannel | Generic | Indicator-derived; MTF gate applied | **Keep, low priority** |
| ScalpIchimokuChannel | ✗ Invalid | 5m Ichimoku with daily settings is structurally wrong | **Disable** |
| ScalpOrderblockChannel | ✓ Good | Self-contained detection; freshness tracking; SL only 0.2×ATR beyond OB | **Keep, widen SL slightly** |

---

## 10. Bug Audit

### Critical Bugs

**BUG-1: DIVERGENCE_CONTINUATION contaminates shared smc_data** (Severity: Critical)
- Location: `scalp.py` lines 2597–2598
- Description: `smc_data["cvd_divergence"] = _div_label` writes to the live scan context dict, which is the same object passed to all channels in the scan cycle
- Effect: ScalpCVDChannel sees evaluator-local divergence instead of SMCDetector signal; scanner scorer reads contaminated cvd_divergence for unrelated signals
- Fix: Remove the writes from the evaluator. The evaluator has already confirmed divergence locally and does not need to stamp smc_data. The scorer should read divergence from the evaluator's signal attributes, not from a shared dict.

**BUG-2: Exception in any ScalpChannel evaluator kills all subsequent evaluators** (Severity: Critical)
- Location: `scalp.py` evaluate() loop, `except Exception: raise`
- Description: The loop re-raises after telemetry, meaning a crash in evaluator 8 (SR_FLIP_RETEST) silently prevents evaluators 9–14 from running
- Effect: A runtime error in one path removes up to 6 paths from the scan with no indication beyond the exception log. Legitimate setups from FAR, PDC, CLS, FUNDING_EXTREME are missed.
- Fix: Wrap each evaluator in isolated try/except. Log the error and continue the loop. Only re-raise if the caller needs to know, not silently kill subsequent paths.

**BUG-3: Dynamic attribute writes on Signal dataclass** (Severity: Medium)
- Locations: `sig.sr_flip_level` (SR_FLIP_RETEST), `sig.pdc_breakout_level` (PDC), `sig.far_reclaim_level` (FAR)
- Description: These attributes are not declared in the Signal dataclass. They are written and expected to be read downstream, but are invisible to serialisation, logging, and type checking.
- Effect: Any downstream code doing `sig.sr_flip_level` (without getattr default) on a non-SR_FLIP signal will raise AttributeError. Metadata is not preserved in reports.
- Fix: Add these three fields to the Signal dataclass with `Optional[float] = None`.

### High-Risk Patterns

**BUG-4: DIVERGENCE_CONTINUATION TP1 and TP2 can be equal** (Severity: Medium)
- Location: `scalp.py` `_evaluate_divergence_continuation`
- Description: Both TP1 and TP2 are computed from `highs[-20:]` / `lows[-20:]`. For LONG, TP1 = `max(highs[-20:])` and TP2 = `max(highs[-20:])` — identical. Neither has a fallback that checks `tp2 > tp1`.
- Effect: TP2 = TP1 means the second target adds no value; trade management logic may break on equal TPs.
- Fix: Ensure TP2 > TP1 with an explicit check and separate lookback for TP2.

**BUG-5: CONTINUATION_LIQUIDITY_SWEEP always fails if sweep.index is absent** (Severity: Medium)
- Location: `scalp.py`, `_evaluate_continuation_liquidity_sweep`
- Description: `sweep_index = getattr(trend_sweep, "index", None)` → `if sweep_index is None or sweep_index < -_CLS_SWEEP_WINDOW: return self._reject("sweeps_not_detected")`
- Effect: If the SMC sweep objects do not have an `index` attribute, this path will always return "sweeps_not_detected" even when valid sweeps exist. The telemetry shows "no sweeps" which is a misleading cause.
- Fix: Verify that the SMC sweep objects expose `.index`. If not, either add it to the SMC model or implement a fallback (e.g., use the position of the sweep in the sweeps list as a proxy for recency).

**BUG-6: BREAKDOWN_SHORT uses bare `return None` instead of `self._reject()`** (Severity: Low-Medium)
- Location: `scalp.py`, `_evaluate_breakdown_short` — multiple failure branches
- Description: Unlike VOLUME_SURGE_BREAKOUT which consistently uses `self._reject("reason")`, BREAKDOWN_SHORT uses `return None` in most failure paths
- Effect: Telemetry for BREAKDOWN_SHORT rejection reasons is incomplete. The no_signal_reason counter shows only "none" rather than the actual gate that fired. This makes diagnosing low BREAKDOWN_SHORT output impossible.
- Fix: Replace all bare `return None` in `_evaluate_breakdown_short` with `return self._reject("reason")`.

**BUG-7: QUIET_COMPRESSION_BREAK SL too tight for crypto noise** (Severity: Medium)
- Location: `scalp.py`, `_evaluate_quiet_compression_break`
- Description: `sl = bb_lower * (1 - 0.001)` — SL is 0.1% below the lower Bollinger Band in QUIET regime. In QUIET regime, normal price noise (even on major pairs) is routinely 0.1–0.3%.
- Effect: QUIET_COMPRESSION_BREAK signals will hit SL on noise before the setup can develop, even when the thesis is correct.
- Fix: Use `bb_lower - atr_val * 0.5` as the SL floor, or increase the buffer to at least 0.2–0.3%.

---

## 11. Retail Indicator Dependency Audit

| Channel / Path | Primary Indicator | Indicator Role | Verdict |
|---|---|---|---|
| ScalpIchimokuChannel | Ichimoku (TK cross, cloud) | **Primary decision-maker** | Disable — wrong timeframe |
| ScalpVWAPChannel | Rolling VWAP bands | **Primary decision-maker** | Disable — not session VWAP |
| ScalpDivergenceChannel | RSI/MACD divergence | **Primary decision-maker** | Keep, narrow scope |
| ScalpSupertrendChannel | Supertrend flip | **Primary decision-maker** | Keep, low weight |
| QUIET_COMPRESSION_BREAK | Bollinger Bands squeeze | Primary trigger | Acceptable in QUIET only |
| TREND_PULLBACK_EMA | EMA9/21 proximity | Primary structure | Acceptable if RSI gate loosened |
| All paths | RSI | Secondary filter | Mostly appropriate; LIQUIDATION_REVERSAL gate too tight |
| Most paths | ADX | Secondary gate | Appropriate |
| VOLUME_SURGE_BREAKOUT | Volume × SURGE_VOLUME_MULTIPLIER | Secondary confirmation | Appropriate |

**Channels that are retail-indicator wrappers with crypto branding:**
- ScalpIchimokuChannel — a pure Ichimoku signal with basic volume/RSI guards
- ScalpVWAPChannel — a pure mean-reversion VWAP signal with basic guards

Both should be disabled until structurally redesigned for crypto intraday reality.

---

## 12. Runtime Truth / Observability Audit

### What works
- ScalpChannel has full generation telemetry: attempts / no_signal / no_signal_reason / generated per path
- `self._reject(reason)` pattern produces structured rejection tokens for most paths
- `_dependency_state()` helper reads `__dependency_source_state` from smc_data for dependency-aware reporting
- `soft_gate_flags` string accumulates which soft gates fired on each signal
- `consume_generation_telemetry()` provides a snapshot for external reporting

### What is broken or missing
- **BREAKDOWN_SHORT** does not use `self._reject()` — its failure reasons are invisible to telemetry
- **CLS sweep.index failure** reports as "sweeps_not_detected" — indistinguishable from truly no sweeps
- **FUNDING_EXTREME SL degradation** (liq_clusters absent → ATR fallback) has no flag or note on the emitted signal. Operators cannot see that the SL is a generic fallback, not a thesis-aligned level.
- **Evaluator confidence boosts** are dead code but look meaningful in code review — misleading
- **smc_data contamination** produces no warning or diagnostic — the CVD channel will silently consume the evaluator's local divergence result as if it came from the SMCDetector
- No current mechanism distinguishes "no setup in market" from "setup existed but killed by geometry" — would require counting signals that passed evaluate() but died in the scanner gate chain

---

## 13. Market-Fit Classification

| Path / Channel | Classification |
|---|---|
| LIQUIDITY_SWEEP_REVERSAL | **Production-fit for crypto** |
| SR_FLIP_RETEST | **Production-fit for crypto** |
| FAILED_AUCTION_RECLAIM | **Production-fit for crypto** |
| CONTINUATION_LIQUIDITY_SWEEP | **Needs fix** (sweep.index dependency) |
| POST_DISPLACEMENT_CONTINUATION | **Production-fit for crypto** |
| FUNDING_EXTREME_SIGNAL | **Needs fix** (SL fallback transparency) |
| LIQUIDATION_REVERSAL | **Usable with caveats** (late confirmation risk) |
| TREND_PULLBACK_EMA | **Needs fix** (RSI gate too narrow) |
| WHALE_MOMENTUM | **Usable with caveats** (timing + data fragility) |
| DIVERGENCE_CONTINUATION | **Needs fix** (smc_data contamination, TP conflict) |
| VOLUME_SURGE_BREAKOUT | **Needs fix** (TP too ambitious for scalp) |
| BREAKDOWN_SHORT | **Needs fix** (TP + telemetry) |
| QUIET_COMPRESSION_BREAK | **Needs fix** (SL too tight) |
| ScalpFVGChannel | **Usable with caveats** (proximity tuning) |
| ScalpCVDChannel | **Needs fix** (contamination first) |
| ScalpOrderblockChannel | **Usable with caveats** (SL slightly tight) |
| ScalpDivergenceChannel | **Usable with caveats** |
| ScalpSupertrendChannel | **Usable with caveats** |
| ScalpVWAPChannel | **Disable until redesigned** |
| ScalpIchimokuChannel | **Structurally invalid for current timeframe** |
| OPENING_RANGE_BREAKOUT | **Structurally invalid** (proxy not real ORB — already disabled) |

---

## 14. Prioritization Audit

### Critical bugs — fix immediately
| Issue | Type | Action |
|---|---|---|
| DIVERGENCE_CONTINUATION writes to smc_data | **Critical bug** | Remove writes; isolate evaluator-local result |
| Exception in evaluator kills subsequent paths | **Critical bug** | Isolate each evaluator in its own try/except |
| Signal dynamic attribute writes | **Critical bug** | Add sr_flip_level, pdc_breakout_level, far_reclaim_level to Signal dataclass |

### Data integrity — fix before trusting output
| Issue | Type | Action |
|---|---|---|
| CLS sweep.index dependency | **Data integrity blocker** | Verify SMC model, add fallback |
| FUNDING_EXTREME SL fallback silent | **Data integrity blocker** | Add `execution_note` when liq_clusters absent |
| DIVERGENCE_CONTINUATION TP1/TP2 conflict | **Bug** | Separate TP window lookbacks |

### Structural validity — disable or redesign
| Issue | Type | Action |
|---|---|---|
| ScalpVWAPChannel (rolling VWAP) | **Structurally invalid** | Disable now |
| ScalpIchimokuChannel (5m daily settings) | **Structurally invalid** | Disable now |
| VOLUME_SURGE_BREAKOUT / BREAKDOWN_SHORT TPs | **SL/TP doctrine mismatch** | Cap at realistic scalp distance (e.g. 2–3× sl_dist max) |
| QUIET_COMPRESSION_BREAK SL too tight | **SL/TP doctrine mismatch** | Widen to 0.3–0.5% or ATR-based |

### Observability gaps — fix to enable tuning
| Issue | Type | Action |
|---|---|---|
| BREAKDOWN_SHORT missing telemetry | **Truth gap** | Replace bare `return None` with `self._reject()` |
| Evaluator confidence boosts are dead code | **Truth gap** | Remove or annotate clearly; document soft_penalty_total as the actual mechanism |
| FUNDING_EXTREME SL degradation not visible | **Truth gap** | Add flag to execution_note |

### Threshold tuning — do last
| Issue | Type | Action |
|---|---|---|
| TREND_PULLBACK RSI 40–60 too tight | **Threshold tuning candidate** | Widen to 35–65 in strong trend regimes |
| LIQUIDATION_REVERSAL RSI < 25 gate | **Threshold tuning candidate** | Consider widening to < 30 with soft penalty at 25–30 |
| FUNDING_EXTREME RSI < 55 for LONG | **Threshold tuning candidate** | After fixes, observe and potentially widen to < 60 |
| ScalpFVGChannel retest proximity | **Threshold tuning candidate** | Observe in live, tune from 50% toward 35–40% |

---

## 15. Final Verdict

### Is this system structurally fit for real crypto trading?
**Partially.** The core structural paths (SR_FLIP_RETEST, FAILED_AUCTION_RECLAIM, POST_DISPLACEMENT_CONTINUATION, LIQUIDITY_SWEEP_REVERSAL) are soundly designed for crypto. The specialist infrastructure (soft penalties, family-aware scoring, kill zone, pair profiles, regime gating) is well-built. Two channels (VWAP, Ichimoku) are structurally invalid and should be off.

### Which paths are truly crypto-native and worth protecting?
1. LIQUIDITY_SWEEP_REVERSAL — strong sweep-reclaim thesis
2. SR_FLIP_RETEST — best structural detection in the codebase
3. FAILED_AUCTION_RECLAIM — structurally correct, thesis-aligned SL/TP
4. POST_DISPLACEMENT_CONTINUATION — institutional displacement pattern
5. FUNDING_EXTREME_SIGNAL — genuinely non-retail, unique edge
6. CONTINUATION_LIQUIDITY_SWEEP — after fixing sweep.index dependency
7. ScalpFVGChannel + ScalpOrderblockChannel — solid specialist channels

### Which paths are weak, retail-generic, or invalid?
1. ScalpIchimokuChannel — 5m Ichimoku is structurally wrong
2. ScalpVWAPChannel — rolling VWAP is not institutional VWAP
3. OPENING_RANGE_BREAKOUT — proxy is not real ORB (already disabled)
4. VOLUME_SURGE_BREAKOUT / BREAKDOWN_SHORT — TP ambition is swing-trade sized on scalp entries

### Why is the system under-generating signals?
Multiple causes compound:
1. The exception-re-raise bug silently kills 6 paths when any earlier path crashes
2. Over-gating: TREND_PULLBACK (RSI 40–60), FUNDING_EXTREME (RSI < 55), LIQUIDATION_REVERSAL (RSI < 25)
3. CLS always fails if sweep objects lack `.index`
4. ScalpCVDChannel fails-closed when `cvd_divergence_age` is absent and `_CVD_REQUIRE_METADATA=True`
5. BREAKDOWN_SHORT telemetry is invisible — cannot diagnose why it's silent

### Are data dependencies actually sufficient?
Not uniformly. Funding rate freshness is unchecked. Liquidation clusters may be absent (FUNDING_EXTREME SL silently degrades). Sweep object structure may not include `.index`. CVD data degradation is handled gracefully; order book degradation is handled correctly with tiered logic.

### What must be fixed first?
In order:
1. Fix the exception isolation in ScalpChannel.evaluate() — this is silently killing 6 paths
2. Remove smc_data mutation in DIVERGENCE_CONTINUATION
3. Add sr_flip_level, pdc_breakout_level, far_reclaim_level to the Signal dataclass
4. Disable ScalpVWAPChannel and ScalpIchimokuChannel
5. Fix CLS sweep.index dependency
6. Fix BREAKDOWN_SHORT telemetry (replace bare `return None`)
7. Fix DIVERGENCE_CONTINUATION TP1/TP2 conflict
8. Add FUNDING_EXTREME SL fallback flag to execution_note
9. Fix QUIET_COMPRESSION_BREAK SL width
10. Widen TREND_PULLBACK RSI gate after above are stable

### What should never be tuned until structure and truth are fixed?
Do not touch RSI thresholds, ADX floors, volume multipliers, or TP ratios until:
- Exception isolation is in place (can trust telemetry)
- smc_data contamination is resolved (can trust CVD signals)
- BREAKDOWN_SHORT telemetry is fixed (can diagnose why it's silent)
- CLS sweep.index is resolved (can trust sweep-based path counts)

Tuning thresholds before fixing the above will produce fake optimisation — adjusting parameters to compensate for bugs rather than improving genuine signal quality.

---

## Recommended PR Sequence

| PR | Scope | Risk |
|---|---|---|
| PR-FIX-1 | Isolate evaluator exceptions in ScalpChannel.evaluate() | Low |
| PR-FIX-2 | Remove smc_data mutation in DIVERGENCE_CONTINUATION | Low |
| PR-FIX-3 | Add undeclared Signal fields (sr_flip_level, pdc_breakout_level, far_reclaim_level) | Low |
| PR-FIX-4 | Disable ScalpVWAPChannel and ScalpIchimokuChannel | Very low |
| PR-FIX-5 | Fix BREAKDOWN_SHORT telemetry (bare return None → self._reject) | Low |
| PR-FIX-6 | Fix DIVERGENCE_CONTINUATION TP1/TP2 conflict | Low |
| PR-FIX-7 | Fix CLS sweep.index dependency or verify SMC model exposes it | Medium |
| PR-FIX-8 | Add execution_note when FUNDING_EXTREME uses ATR SL fallback | Low |
| PR-FIX-9 | Widen QUIET_COMPRESSION_BREAK SL to ATR-based floor | Low |
| PR-TUNE-1 | Widen TREND_PULLBACK RSI gate to 35–65 | Medium |
| PR-TUNE-2 | Review LIQUIDATION_REVERSAL and FUNDING_EXTREME RSI gates | Medium |
| PR-TUNE-3 | Cap VOLUME_SURGE_BREAKOUT / BREAKDOWN_SHORT TPs at scalp horizon | Medium |
