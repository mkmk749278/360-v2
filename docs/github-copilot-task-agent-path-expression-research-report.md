# Signal/Path Expression Lifecycle Research Report

**Repository:** `mkmk749278/360-v2`  
**Date:** 2026-04-14  
**Model/agent identifier used:** `github-copilot-task-agent` (**best-available identifier, not exact underlying model name exposure**)  

## Executive summary

Confirmed code behavior shows a narrow production-expression funnel by design: most auxiliary channels are disabled by default, scanner gates are dense, WATCHLIST for `360_SCALP` is routed to free-preview only, and persistence only records terminal lifecycle outcomes. This combination strongly explains why persisted `signal_performance` history can show only a subset of setup/path families even when many families exist in code.

A key blind spot is not only suppression but **classification/naming collapse**: scanner can overwrite evaluator-authored `setup_class` with classified families (`src/scanner/__init__.py:2468`), and confluence rewrites winners to `MULTI_STRATEGY_CONFLUENCE` (`src/scanner/__init__.py:3219`), reducing downstream path identity fidelity in persistence.

---

## Confirmed code facts vs realistic operational inferences

### Confirmed code facts
- Only `360_SCALP` is enabled by default; auxiliary scalp channels are default-disabled (`config/__init__.py:718-730`).
- Scanner keeps WATCHLIST (`50-64`) for all scalp-family channels (`src/scanner/__init__.py:2942-2954`).
- Router special-cases only `360_SCALP` WATCHLIST to free-preview route (`src/signal_router.py:487-489`, `896-918`).
- Router applies per-channel min confidence for non-WATCHLIST flow (`src/signal_router.py:633-642`).
- Terminal persistence is written by `PerformanceTracker.record_outcome()` to `data/signal_performance.json` (`src/performance_tracker.py:92-152`, `1000-1007`) and is called from trade monitor terminal outcomes (`src/trade_monitor.py:219-277`).
- Router `cleanup_expired()` removes active signals but does not call performance tracker (`src/signal_router.py:1168-1205`).

### Realistic operational inferences
- Persisted diversity is likely naturally narrow in live operation because disabled channels + hard/soft gate stack + terminal-only persistence compound into strong attrition.
- WATCHLIST from auxiliary channels (if enabled) is likely often dropped in router due channel min-confidence floors (scanner preserves, router re-filters).
- Path diversity in persistence is likely undercounted when confluence relabeling and setup reclassification overwrite original evaluator identities.

---

## 1. Path/setup inventory

### A. Canonical setup classes (quality engine taxonomy)
Defined in `SetupClass` (`src/signal_quality.py:18-45`):
- TREND_PULLBACK_CONTINUATION
- TREND_PULLBACK_EMA
- BREAKOUT_RETEST
- LIQUIDITY_SWEEP_REVERSAL
- LIQUIDATION_REVERSAL
- RANGE_REJECTION
- MOMENTUM_EXPANSION
- EXHAUSTION_FADE
- RANGE_FADE
- WHALE_MOMENTUM
- MULTI_STRATEGY_CONFLUENCE
- VOLUME_SURGE_BREAKOUT
- BREAKDOWN_SHORT
- OPENING_RANGE_BREAKOUT
- SR_FLIP_RETEST
- FUNDING_EXTREME_SIGNAL
- QUIET_COMPRESSION_BREAK
- DIVERGENCE_CONTINUATION
- CONTINUATION_LIQUIDITY_SWEEP
- POST_DISPLACEMENT_CONTINUATION
- FAILED_AUCTION_RECLAIM
- FVG_RETEST
- FVG_RETEST_HTF_CONFLUENCE
- RSI_MACD_DIVERGENCE
- SMC_ORDERBLOCK

### B. Evaluator-emitted setup labels (channel outputs)
From channel evaluators:
- `360_SCALP` core evaluator family emits:
  - LIQUIDITY_SWEEP_REVERSAL, TREND_PULLBACK_EMA, LIQUIDATION_REVERSAL, WHALE_MOMENTUM,
  - VOLUME_SURGE_BREAKOUT, BREAKDOWN_SHORT, OPENING_RANGE_BREAKOUT, SR_FLIP_RETEST,
  - FUNDING_EXTREME_SIGNAL, QUIET_COMPRESSION_BREAK, DIVERGENCE_CONTINUATION,
  - CONTINUATION_LIQUIDITY_SWEEP, POST_DISPLACEMENT_CONTINUATION, FAILED_AUCTION_RECLAIM
  (`src/channels/scalp.py:333-348`, setup assignments at ~568, 744, 895, 1097, 1316, 1537, 1709, 1968, 2142, 2294, 2508, 2759, 3083, 3387)
- Auxiliary channels emit:
  - FVG_RETEST / FVG_RETEST_HTF_CONFLUENCE (`src/channels/scalp_fvg.py:223,240`)
  - RSI_MACD_DIVERGENCE (`src/channels/scalp_divergence.py:234`)
  - SMC_ORDERBLOCK (`src/channels/scalp_orderblock.py:264`)
  - CVD_DIVERGENCE (`src/channels/scalp_cvd.py:172`)
  - VWAP_BOUNCE (`src/channels/scalp_vwap.py:186`)
  - SUPERTREND_FLIP (`src/channels/scalp_supertrend.py:182`)
  - ICHIMOKU_TK_CROSS (`src/channels/scalp_ichimoku.py:198`)

### C. Inventory mismatches to note
- Some emitted labels are outside `SetupClass` (`CVD_DIVERGENCE`, `VWAP_BOUNCE`, `SUPERTREND_FLIP`, `ICHIMOKU_TK_CROSS`).
- `SIGNAL_TYPE_LABELS` contains legacy/alternate names not matching current emitter labels (`config/__init__.py:742-764`).

---

## 2. End-to-end lifecycle map

1. **Detection/evaluation**: channels evaluate per symbol (`src/scanner/__init__.py:2991-3134`), with multi-candidate scalp arbitration (`3064-3117`).
2. **Candidate preparation + scoring**: `_prepare_signal()` applies setup/execution/risk checks, hard/soft gates, scoring engine, penalties, tiering (`2072-2972`).
3. **Suppression/acceptance decision**:
   - hard rejects return `None`
   - WATCHLIST short-circuit for scalp family (`2942-2954`)
   - otherwise min_conf + component floors (`2955-2968`)
4. **Queueing**: accepted signals go to signal queue (`3241-3255`, queue impl `src/signal_queue.py`).
5. **Routing**: router consumes queue (`src/signal_router.py:441-473`) and runs lock/cooldown/cap/stale/min-conf/risk/delivery flow (`482-756`).
6. **Preview vs paid emission**:
   - `360_SCALP` WATCHLIST → free preview route (`487-489`, `896-954`)
   - paid flow posts to mapped channel and registers `_active_signals` (`658-746`).
7. **Lifecycle tracking**: trade monitor polls active signals, updates status through TP/SL/invalidation/expiry (`src/trade_monitor.py:367-403`, `537-799`).
8. **Persistence**: terminal outcomes call `_record_outcome` → `PerformanceTracker.record_outcome` → `data/signal_performance.json` (`trade_monitor.py:219-277`; `performance_tracker.py:92-152`, `1000-1007`).

---

## 3. Drop-off / suppression map

### Upstream (before scoring/persistence)
- Channel disabled (`_CHANNEL_ENABLED_FLAGS`, `src/scanner/__init__.py:185-194`).
- `_should_skip_channel()` gates: tier exclusion, pair-quality, volatile/regime incompatibility, paused, cooldown, symbol circuit-breaker, active signal already exists, ranging-low-ADX (`1662-1790`).
- Setup incompatibility / execution / risk fail (`2120-2129`, `2414-2418`).
- Hard MTF gate fail (`2180-2197`).
- Cross-asset hard block (`2333-2337`).
- SMC hard gate fail (`2825-2852`), trend hard gate fail (`2859-2881`).
- QUIET scalp block (`2906-2941`).
- Confidence/component floor fail (`2955-2968`).

### Midstream (transport/routing)
- Queue full drop (`src/signal_queue.py:82-85`, `93-95`).
- Router lock/cooldown/per-channel cap/correlation block (`491-543`, `515-526`).
- Sanity reject TP/SL geometry (`545-571`).
- Stale suppression before post (`573-627`).
- Non-watchlist min-confidence drop (`636-642`).
- Risk manager block (`646-655`).
- Delivery failure after retries can lose signal (`676-716`).

### Downstream (lifecycle/persistence)
- WATCHLIST preview path never enters active lifecycle (`487-489`, `896-918`) => no performance record.
- Cancellations (invalid SL config) remove without `_record_outcome` (`599-611`).
- Router cleanup expiry removes without performance write (`1168-1205`).
- Persistence is terminal-event only; TP1/TP2 progress alone never persists.

---

## 4. Realistic operational interpretation

### Confirmed by code
- Live paid expression is likely dominated by `360_SCALP` main channel because others are default-disabled.
- Funnel is intentionally selective: many gates + per-path scoring + post-score penalties + router gating.
- Persistence is even more selective: only signals that both enter active lifecycle and reach terminal outcomes.

### Most realistic operational behavior
- Many path families are “implemented” but not production-expressing by default (disabled channels and/or rarely surviving stacked gates).
- Suppression likely concentrates around regime/pair-quality/MTF/confidence/tier transitions, observable in scanner suppression summaries.
- Bottlenecks likely include queue pressure (max 500), router serial processing, stale-signal cutoff (120s for scalp), and monitor exception sensitivity (`asyncio.gather` without `return_exceptions=True` in monitor path).

---

## 5. Why persisted history currently shows only a subset of paths

Most likely combination (not a single cause):
1. **Channel enablement concentration**: only `360_SCALP` enabled by default (`config/__init__.py:718-730`).
2. **Gate attrition**: high candidate drop before queue/router.
3. **WATCHLIST exclusion from persistence**: `360_SCALP` WATCHLIST goes free-preview only, not active lifecycle (`signal_router.py:487-489`, `896-918`).
4. **Router re-filtering**: scanner may keep WATCHLIST for all scalp-family channels, but router special-case is only `360_SCALP`; others hit min-confidence filter.
5. **Identity collapse**:
   - setup overwrite by classifier (`scanner/__init__.py:2468`)
   - confluence relabel to `MULTI_STRATEGY_CONFLUENCE` (`3219`)
   reducing original path visibility in performance records.
6. **Persistence blind spots**:
   - router cleanup expiry not recorded in performance tracker (`signal_router.py:1168-1205`)
   - canceled invalid-config signals not recorded (`trade_monitor.py:599-611`).

---

## 6. Best instrumentation points for a future path-expression monitor section

1. **Candidate reached scoring per setup_class**
   - Proof: upstream path expression before final gating.
   - Source: `_suppression_counters["candidate_reached_scoring:*"]` (`scanner/__init__.py:2631-2632`).
   - Type: log-based (`Scan cycle suppression summary`).
   - Reliability: high for funnel entry; not proof of production emission.

2. **Score-band distribution per setup_class**
   - Proof: where each path dies (`score_below50`, `50-64`, `65-79`, `80+`).
   - Source: counters at `2696-2716`; log `Scoring tier distribution...` (`1186-1191`).
   - Type: log-based.
   - Reliability: high for suppression diagnosis.

3. **Evaluated vs emitted diversity**
   - Proof: expression attrition after all gates/arbitration.
   - Source: `_setup_eval_counts/_setup_emit_counts`, log `Signal diversity...` (`1173-1182`).
   - Type: log-based.
   - Reliability: high for path-level conversion.

4. **Suppression reason digest (rolling windows)**
   - Proof: dominant suppressors by reason/channel/symbol.
   - Source: `SuppressionTracker/SuppressionAnalytics` (`src/suppression_telemetry.py`).
   - Type: log/command-driven telemetry.
   - Reliability: medium-high (depends on complete reason coverage).

5. **WATCHLIST preview routing events**
   - Proof: path expressed only as preview, not paid/live.
   - Source log: `WATCHLIST preview → free channel: ...` (`signal_router.py:913-915`).
   - Type: log-based.
   - Reliability: high for `360_SCALP` WATCHLIST behavior.

6. **Paid post and active registration**
   - Proof: true production expression entered lifecycle.
   - Source: `Signal posted → ...` and `_active_signals` registration (`signal_router.py:718-746`).
   - Type: log + runtime state.
   - Reliability: very high.

7. **Persistence write hook**
   - Proof: terminal lifecycle outcome persisted.
   - Source: `PerformanceTracker.record_outcome()` (`performance_tracker.py:92-152`).
   - Type: persisted-data-based.
   - Reliability: very high, but terminal-only and blind to non-recorded closures.

8. **Non-persisted terminal cleanup visibility**
   - Proof: lifecycle closure path that bypasses persistence.
   - Source: `Auto-expired signal ...` in router cleanup (`signal_router.py:1191-1194`).
   - Type: log-based.
   - Reliability: high for blind-spot detection.

---

## 7. Most important findings / recommendations

1. **Treat “implemented path count” and “persisted path count” as different metrics.**
2. **For path-expression audits, monitor conversion chain explicitly:**
   `evaluated -> reached_scoring -> score_band -> enqueued -> posted_paid/watchlist_preview -> active -> terminal -> persisted`.
3. **Add explicit counters for identity rewrites** (`original_setup_class` vs final `setup_class`) to quantify naming collapse.
4. **Add persistence-gap counters** for router-expired and canceled-without-outcome paths.
5. **If production objective is broader family diversity, first review enablement defaults and gate profiles before retuning scoring thresholds.**

---

## Notes on evidence limits

- No live `monitor-logs` branch snapshot was available in this clone during this investigation (`refs/heads/monitor-logs` not present locally).
- Therefore operational conclusions are grounded in code-verified mechanics and realistic runtime implications, plus the problem statement’s observed monitor behavior description.
