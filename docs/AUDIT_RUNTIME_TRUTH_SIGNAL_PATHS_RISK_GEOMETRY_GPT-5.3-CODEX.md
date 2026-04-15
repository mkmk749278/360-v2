# AUDIT_RUNTIME_TRUTH_SIGNAL_PATHS_RISK_GEOMETRY_GPT-5.3-CODEX

Date: 2026-04-15  
Repo: `mkmk749278/360-v2` (`main`)  
Runtime evidence: `monitor/latest.txt` from `monitor-logs`

## Scope and evidence standard

This is requirements-first and runtime-first. Code is treated as implementation evidence, not requirement truth.  
Primary runtime evidence came from `monitor/latest.txt` (generated 2026-04-15 05:03 UTC), correlated with `src/scanner/__init__.py`, `src/signal_router.py`, `src/signal_quality.py`, `src/channels/*`, `src/trade_monitor.py`, `config/__init__.py`, `OWNER_BRIEF.md`, `docs/ACTIVE_CONTEXT.md`, and recent canonical audit docs.

---

## 1) Requirements-first architecture truth

### What the system should do (real requirement)

For an institutional multi-pair signal engine, market-structure truth must be **hierarchical hybrid**:
1. **Pair-local structure is primary** (SMC structure, local regime, local microstructure, local liquidity/precision).
2. **Global regime and BTC context are secondary context layers** (position sizing, aggressiveness, correlation risk), not primary signal truth.
3. **Family-aware gating must dominate generic gating** (reversal, continuation, breakout, quiet-specialist, order-flow families should not be flattened under one policy).
4. **Evaluator-authored signal expression (SL/TP/validity intent) must survive downstream controls** except explicit universal safety constraints.

### Current implementation truth

- Runtime regime classification is computed **per symbol** from symbol candles (`_build_scan_context`, `src/scanner/__init__.py:1566-1570`), then consumed in per-symbol gate chain (`_prepare_signal`, MTF/quiet/gates).
- Runtime also uses **BTC-led global context** for some shared decisions:
  - `_last_market_regime` set from BTC symbol (`1571-1574`) and reused for scan prefilter volume floor (`1355-1360`).
  - cross-asset gate/correlation references BTC/ETH (`2316-2333`, `_update_btc_correlation`).
- Gate chain remains heavily generic in key suppressors (MTF, spread/pair-quality, quiet floor, score floors), with family-aware exemptions only partially implemented.

### Gap

- Architecture is **partially hybrid**, but still too generic in suppression policy.
- Pair-local structure exists in runtime, but expression is frequently dominated by generic suppressors before family-specific edge can express.
- Runtime is **not purely BTC-proxy-led**, but BTC/global context still leaks into broad prefiltering and risk behavior beyond strict context usage.

---

## 2) Full signal-path inventory and expression audit

### Observable live expression evidence window

From monitor performance history (`Total signals on record: 38`) and setup summary in `monitor/latest.txt`:
- Expressed paths in history: `TREND_PULLBACK_EMA` (18), `SR_FLIP_RETEST` (15), `CONTINUATION_LIQUIDITY_SWEEP` (4), `LIQUIDITY_SWEEP_REVERSAL` (1).
- No recorded live outcomes in that observed history for the other 10 internal 360_SCALP evaluators.
- In recent cycles, no new signals fired (`Signals fired last 200 lines: 0`), while suppression counters are high.

### Business-critical answer

**Why only a small number of paths generated live signals while many are absent:**
1. **Suppression funnel concentration**: dominant runtime suppressors are `volatile_unsuitable:*`, `mtf_gate:*`, and `pair_quality:spread`. These remove many candidates before scoring/dispatch.
2. **Score-floor attrition**: candidates that reach scoring often die at `<50` or become `50-64 WATCHLIST`, especially for `RSI_MACD_DIVERGENCE` and some `SR_FLIP_RETEST`/`FAILED_AUCTION_RECLAIM` samples.
3. **Governance/enablement asymmetry**: only `360_SCALP` is enabled by default in code; auxiliary channels are default-disabled (`config/__init__.py:718-730`). Live monitor showing FVG/divergence/orderblock suppressors indicates environment-level enablement, but still mostly blocked.
4. **Risk geometry rejection**: repeated FVG SL rejection and repeated SL near-zero/cap warnings further kill expression after candidate formation.

### Path-by-path verdict table

| Path / Setup | Live expressed? | Evidence source | If not expressed, likely cause | Verdict category | Confidence |
|---|---|---|---|---|---|
| LIQUIDITY_SWEEP_REVERSAL | Yes (1/38) | monitor setup summary | Mostly scoring/suppressor attrition otherwise | expressed live | High |
| TREND_PULLBACK_EMA | Yes (18/38) | monitor setup summary | Dominant surviving core path | expressed live | High |
| LIQUIDATION_REVERSAL | Not observed in history | monitor summary absence | Candidate scarcity + gate funnel | unclear / insufficient evidence | Medium |
| WHALE_MOMENTUM | Not observed | monitor summary + no recent counters | narrow specialist conditions + QUIET hard block doctrine | suppressed by regime/gating | Medium |
| VOLUME_SURGE_BREAKOUT | Not observed | monitor summary absence | regime/setup rarity + funnel attrition | unclear / insufficient evidence | Medium |
| BREAKDOWN_SHORT | Not observed | monitor summary absence | regime/setup rarity + funnel attrition | unclear / insufficient evidence | Medium |
| OPENING_RANGE_BREAKOUT | Not observed | monitor summary + `SCALP_ORB_ENABLED=false` default | governance default disable | disabled by governance | High |
| SR_FLIP_RETEST | Yes (15/38) | monitor setup summary + `score_50to64/65to79` counters | often downgraded to watchlist/B tier before strong expression | expressed live (but heavily degraded) | High |
| FUNDING_EXTREME_SIGNAL | Not observed | monitor summary absence | specialist rarity + gate pressure | unclear / insufficient evidence | Medium |
| QUIET_COMPRESSION_BREAK | Not observed | monitor summary absence | quiet-only specialist rarity | suppressed by regime/gating | Medium |
| DIVERGENCE_CONTINUATION | Not observed | monitor summary absence | family narrowness + generic suppressors | unclear / insufficient evidence | Medium |
| CONTINUATION_LIQUIDITY_SWEEP | Yes (4/38) | monitor setup summary | live but low frequency, weak outcomes | expressed live | High |
| POST_DISPLACEMENT_CONTINUATION | Not observed | monitor summary absence | strict thesis + funnel attrition | silent due architectural/gating pressure | Medium |
| FAILED_AUCTION_RECLAIM | Not observed live; candidate seen | `candidate_reached_scoring:FAILED_AUCTION_RECLAIM`, `score_50to64` | scoring below paid threshold | candidate generated but blocked | High |
| FVG_RETEST / FVG_RETEST_HTF_CONFLUENCE (aux) | No live expression observed | monitor top suppressors + repeated `FVG SL rejected` warnings | volatile suppressor + geometry rejection | suppressed by regime/gating + downstream SL/risk geometry | High |
| RSI_MACD_DIVERGENCE (aux) | No live expression observed | `candidate_reached_scoring` + repeated `score_below50` | scoring suppression | candidate generated but blocked | High |
| SMC_ORDERBLOCK (aux) | No live expression observed | `volatile_unsuitable:360_SCALP_ORDERBLOCK` | volatile regime suppression | suppressed by regime/gating | High |
| CVD_DIVERGENCE / VWAP_BOUNCE / SUPERTREND_FLIP / ICHIMOKU_TK_CROSS (aux) | No direct live evidence | monitor history absence; setup names not in self-classifying set | likely disabled or structurally underrepresented + identity-mapping weakness | silent due architectural defect / insufficient evidence | Medium |
| WATCHLIST free preview path | Exists | `signal_router._route_watchlist_to_free` + tests | preview only by design | expressed live (free-only pathway, not paid lifecycle) | High |
| Radar/free watch path | Exists | scanner radar pass + `on_radar_candidate` → `FreeWatchService` | mostly for soft-disabled channels, not paid dispatch | expressed live (engagement path) | Medium |

---

## 3) End-to-end suppression funnel

### Runtime path (confirmed)

1. Pair prefilter + spread cache + context (`_build_scan_context`)  
2. `smc_data` assembly (pair profile, regime context, funding, cvd)  
3. Evaluator generation (14 internal list for `360_SCALP`; aux channel evaluators)  
4. Gate chain (`_should_skip_channel` + `_prepare_signal` gate stack)  
5. Scoring + tiering + post-penalty reclassification  
6. Risk plan validation (`build_risk_plan`)  
7. Arbitration (same-direction winner per symbol in `360_SCALP`)  
8. Router dispatch + active lifecycle registration (except WATCHLIST free route)  
9. TradeMonitor lifecycle outcomes and persistence

### Where candidates are most commonly lost (runtime evidence + code)

- **Early suppressors (largest):**
  - `volatile_unsuitable:360_SCALP_FVG/DIVERGENCE/ORDERBLOCK` (top key count 144 each)
  - `mtf_gate:360_SCALP` (144)
  - `pair_quality:spread` (128)
- **Mid-funnel suppressors:**
  - scoring below 50 (`score_below50:*`, especially divergence path)
  - QUIET confidence floor (`QUIET_SCALP_BLOCK`, count 67)
- **Late-funnel suppressors:**
  - risk geometry warnings/rejections (FVG >2% rejection, SL near-zero rejection, SL cap warnings)

### Classification of suppressors

- **Correct protective behavior:** stale/SL-direction sanity, risk rejection for impossible geometry, correlation caps.
- **Harsh-but-valid:** strict MTF and spread filters under current market noise.
- **Over-generic policy:** same MTF/spread/quiet floors across heterogeneous setups causing family flattening.
- **Implementation defect / contradiction:**
  - stale scanner comment about radar consumer (`RadarChannel`) despite callback-driven implementation.
  - lifecycle duplicate-risk remains (terminal posting/removal sequencing and dual expiry ownership in monitor/router).
- **Observability gap:** per-path generated→blocked telemetry is strong for some paths but incomplete for proving non-expression root cause on all 14 in the current history window.

---

## 4) SL / TP / risk geometry integrity audit

### End-to-end SL/TP handling truth

- **Created by evaluators:** each evaluator authors initial SL/TP (`src/channels/scalp.py` + aux channel files).
- **Preserved or rewritten:**
  - `build_risk_plan` preserves evaluator geometry for `STRUCTURAL_SLTP_PROTECTED_SETUPS` plus FAR block (`signal_quality.py:946-980`).
  - Non-protected setups are recomputed with generic structure/ATR logic.
- **Validated/capped/rejected:**
  - channel max-SL cap (`_MAX_SL_PCT_BY_CHANNEL`) and near-zero SL rejection (`signal_quality.py:985-1031`).
  - additional SL direction sanity and RR/price validity checks.
  - FVG evaluator pre-rejects `sl_dist/close > 2.00%` before risk plan (`scalp_fvg.py:178-188`).
- **Possible downstream rewrite:** predictive engine scales TP/SL for non-protected setups (`predictive_ai.adjust_tp_sl`), bypassing protected setups.

### Correlation with live warnings

Monitor shows repeated:
- `FVG SL rejected ... > 2.00% max` (ENJUSDT/LABUSDT)
- `SL capped for 360_SCALP LONG: 2.21%/3.52% > 1.50% max`
- `SL near-zero rejection ... 0.0315% < 0.0500%`

### Verdict on these warnings

- **Partly healthy protection:** these guards prevent pathological risk geometry.
- **But also evidence of distortion pressure:** repeated cap/reject loops indicate evaluator geometry and downstream hard limits are often in conflict, especially for volatile/small-cap structure.
- **Likely symbol-specific precision / microstructure sensitivity:** near-zero rejection pattern suggests tight-distance rounding/tick-size regime stress on specific symbols.
- **Setup-family mismatch risk:** strict global minima/caps can kill structurally valid, naturally tight setups or invalidate family intent if not explicitly exempt.

Most exposed classes (from runtime evidence): `FVG_RETEST` and generic `360_SCALP` candidates that repeatedly trigger cap/near-zero conditions.

---

## 5) Regime / market structure truth test

### Runtime truth

- **Per-pair:** primary regime classification and market state are computed from each pair’s candles and used throughout gate/scoring/risk.
- **Global/BTC-led components:** BTC regime is persisted as `_last_market_regime` and used for symbol prefilter volume floor; BTC/ETH correlation gates are applied for cross-asset risk.
- **Therefore runtime is hybrid, not purely global and not purely pair-local.**

### Deeper question answer

The live signal pipeline **does** analyze per-pair market structure in runtime. However, final expression is still dominated by broad generic suppressors and shared floors, so pair-specific structure is not fully allowed to express family intent. This is **partial pair-first**, not full pair-first architecture.

---

## 6) Doctrine vs runtime reality

### Matches

- WATCHLIST doctrine now matches runtime route in code/tests (`signal_router._process`, `tests/test_pr18_scalp_tier_dispatch_alignment.py`).
- 14-evaluator list and arbitration model are implemented (`ScalpChannel.evaluate` list + scanner arbitration).
- B13 protection intent is materially present (structural setup protection + predictive bypass list).

### Mismatches / contradictions still visible

1. **Docs claim broad correction completion; runtime still suppression-heavy with near-zero output windows.**  
   Monitor window shows `Signals=0` with heavy suppressors despite claimed post-fix stability.
2. **Adjacent/successor defect pattern:** lifecycle duplicate-risk mechanics remain in code (terminal posting/removal guarantees and split expiry owners), consistent with `ACTIVE_CONTEXT` stating it is still pending.
3. **Architecture/doc drift:** scanner comment says radar scores are read by `RadarChannel`; actual runtime path is callback-based free-watch flow in `main.py`.
4. **Expression telemetry contradiction at business level:** doctrine emphasizes full multi-path institutional expression; runtime evidence still shows concentration in only a few setup classes with many paths silent/blocked.

---

## A. Executive verdict

The engine is alive and structurally advanced, but live expression is still heavily bottlenecked by generic suppressors and geometry friction. Runtime is hybrid (pair-level + BTC/global context), not broken globally, but still not fully requirements-aligned for broad family-balanced multi-pair institutional expression.

## B. Path expression table

(See section **2** table; it is the canonical path-by-path verdict table for this audit window.)

## C. Top suppressors table

| Suppressor | Meaning | Classification | Likely impact on expression |
|---|---|---|---|
| `volatile_unsuitable:360_SCALP_FVG/DIVERGENCE/ORDERBLOCK` | Non-core channels blocked in volatile-unsuitable state | harsh-but-valid / over-generic depending family | major reduction of auxiliary path expression |
| `mtf_gate:360_SCALP` | MTF confluence veto | harsh-but-valid (possibly over-generic) | blocks many otherwise viable pair-local setups |
| `pair_quality:spread` | spread/quality hard fail | protective but harsh in noisy market | broad candidate starvation |
| `QUIET_SCALP_BLOCK` | quiet-regime confidence floor for scalp | policy-level harsh | suppresses borderline but potentially valid quiet setups |
| `score_below50:*` | composite score floor fail | expected but can reflect family underfit | removes low-conviction candidates before dispatch |
| `score_65to79:*` + no dispatch in observed window | B-tier candidates exist but may be later blocked/risk-killed | observability warning | indicates nontrivial mid-funnel attrition |
| `FVG SL rejected >2%` | evaluator-level geometry hard reject | protective but may be family-misaligned | blocks FVG expression repeatedly |
| `SL capped` / `SL near-zero rejection` | downstream universal SL controls | protective with distortion risk | may kill structurally valid but tight/volatile setups |

## D. Architecture verdict

**Partially aligned but still too generic.**  
Per-pair analysis is real in runtime, but expression control remains overly uniform across heterogeneous setup families.

## E. SL / Geometry verdict

**Protective but too harsh in parts, with partial distortion risk.**  
Controls are not absent; they are active. But repeated live cap/reject loops show nontrivial conflict between evaluator-authored geometry and downstream universal constraints.

## F. Best next PR / PR sequence

1. **PR-1: Suppression funnel observability hardening (path-level generated→blocked telemetry with final reason precedence and per-setup counters).**  
   Needed to separate market-condition suppression from architecture defects per setup.
2. **PR-2: Family-aware gate calibration pass (targeted, not global) for dominant suppressors:** MTF + quiet-floor + spread behavior by setup family.
3. **PR-3: Geometry integrity refinement:** tighten B13 enforcement for non-protected setups most impacted by cap/near-zero rejects; add symbol precision/tick-size-aware minimum-distance logic.
4. **PR-4: Lifecycle idempotency/duplicate-post hardening** (already identified in active context) to remove runtime noise in downstream truth signals.
5. **PR-5: Radar/docs alignment cleanup** (remove stale RadarChannel references; ensure documentation matches callback-driven radar watch flow).

## G. Requirements vs implementation gap

| What the system should do | What it currently does | What should change next |
|---|---|---|
| Pair-first institutional expression across many setup families | Expression concentrated in a few paths; many paths suppressed/silent | add family-aware suppression calibration with hard telemetry proof |
| Use global/BTC context as context, not dominant filter | Hybrid runtime; BTC/global still influences broad prefilter and correlation gate | constrain global influence to explicit risk context where justified |
| Preserve evaluator-authored geometry unless explicit safety violation | Protected for many setups, but repeated cap/reject loops show friction | extend precision/family-aware geometry policy for exposed paths |
| Distinguish healthy suppression from architectural over-blocking | Current logs show suppressors but not always decisive per-path causality | implement decisive funnel tracing per path/setup |
| Keep doctrine/docs/tests/runtime fully aligned | Core WATCHLIST alignment fixed; adjacent runtime/doc drift remains | clean stale docs/comments and resolve remaining lifecycle contradictions |

---

### Evidence confidence labeling used in this report
- **Confirmed evidence:** directly present in code/monitor/docs referenced above.
- **Strong inference:** consistent multi-source pattern but not fully proven for every path.
- **Open uncertainty:** explicitly marked where runtime history window is insufficient for decisive attribution.
