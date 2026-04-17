# 1. Executive truth

**Verdict:** the current scoring calculation is **not yet good enough** for live paid-tier conversion.  
It is mathematically coherent but strategically miscalibrated for a multi-path institutional engine.

- **Code truth (confirmed):** runtime confidence is driven by `SignalScoringEngine` total, then reduced by accumulated evaluator+scanner soft penalties, then re-tiered (`src/scanner/__init__.py:3052-3164`).
- **Business truth (given):** engine is active (250+ WATCHLIST alerts in 24h) but paid conversion is weak.
- **Design truth (assessment):** too much shared scoring remains for materially different theses; several valid families are under-credited, then over-penalized into WATCHLIST.

# 2. Current scoring architecture — what actually happens at runtime

## Authoritative runtime path (confirmed)

1. Candidate is built by path evaluator (`src/channels/scalp.py:317-354`).
2. Setup/execution/risk checks run in scanner (`src/scanner/__init__.py:2458-2800`).
3. Legacy confidence is computed via `compute_confidence(...)` (`src/scanner/__init__.py:2857-2870`, `src/scanner/__init__.py:2141-2260`, `src/confidence.py:588-672`).
4. `score_signal_components(...)` is computed and assigned (`src/scanner/__init__.py:2878-2897`, `src/signal_quality.py:1383-1433`).
5. **Authoritative overwrite:** composite `SignalScoringEngine.score(...)` overwrites confidence/tier (`src/scanner/__init__.py:3052-3136`, `src/signal_quality.py:1542-1566`).
6. Full soft penalties are deducted post-scoring (`src/scanner/__init__.py:3153-3161`).
7. Tier is re-classified post-penalty (`src/scanner/__init__.py:3162-3164`, `src/scanner/__init__.py:444-463`).
8. Stat filter and pair-analysis penalties/suppression apply (`src/scanner/__init__.py:3166-3234`, `src/stat_filter.py:182-243`).
9. Additional hard gates/floors apply (SMC gate, trend gate, QUIET block, confidence/component floors) (`src/scanner/__init__.py:3236-3388`).
10. WATCHLIST short-circuit returns signal before min-conf/component-floor gate for scalp (`src/scanner/__init__.py:3361-3374`).
11. Router sends WATCHLIST to free-only path (`src/signal_router.py:482-489`, `src/signal_router.py:896-917`).

## What decides FILTERED / WATCHLIST / B / A+

- **Tier bands:** `A+ >= 80`, `B 65-79`, `WATCHLIST 50-64`, `FILTERED < 50` (`src/scanner/__init__.py:444-463`).
- **FILTERED** happens if composite total <50, or later hard suppressions/floors fail (`src/scanner/__init__.py:3121-3137`, `3236-3388`).
- **WATCHLIST** is post-penalty 50-64 and scalp; routed to free preview (`src/scanner/__init__.py:3361-3374`, `src/signal_router.py:482-489`).
- **B-tier paid / A+ paid** require surviving all downstream gates and router processing with confidence >= channel min (`src/scanner/__init__.py:3375-3391`, `config/__init__.py:591-605`, `src/signal_router.py:632-642`).

# 3. Is the scoring calculation good or not?

**No.** It is a **hybrid model still materially biased by shared assumptions**.

Why:
- Shared base dimensions dominate for most paths (`src/signal_quality.py:1475-1489`).
- Family thesis adjustment only covers reversal/liquidation, divergence, and sweep-continuation (`src/signal_quality.py:1509-1533`, `1683-1815`).
- Key live paths get no thesis lift despite path-specific thesis logic in evaluators.
- Large stacked penalties are applied after scoring, frequently collapsing borderline-valid setups into 50-64.

# 4. Are all paths scored too uniformly?

**Answer:** not fully uniform, but still **overly uniform where it matters most**.

- **Universal safety logic (should stay shared):** hard geometry sanity, SL/TP direction sanity, stale checks, correlation lock.
- **Shared base scoring (partly valid):** SMC/regime/volume/indicators/pattern/MTF is useful baseline.
- **Family-aware scoring (currently partial):** only 3 families get thesis adjustment.
- **Path-aware scoring (currently insufficient):** reclaim/retest, trend-pullback, and displacement-continuation are mostly forced through shared dimensions that do not express their primary edge.

# 5. Which paths are under-credited and why

## SR_FLIP_RETEST
- **Thesis:** structural role-flip retest + rejection quality (`src/channels/scalp.py:1746-1775`).
- **Rewards today:** generic indicators/MTF/patterns; small SMC if FVG exists.
- **Misses/distortions:** no family thesis adjustment; no regime affinity listing; often low SMC base when no sweep/MSS.
- **Judgment:** **under-credited**.

## FAILED_AUCTION_RECLAIM
- **Thesis:** failed auction wick + reclaim acceptance (`src/channels/scalp.py:3134-3164`, `3219-3415`).
- **Rewards today:** generic shared scores only.
- **Misses/distortions:** no family adjustment, no regime affinity listing, reclaim-specific edge not scored directly.
- **Judgment:** **under-credited**.

## TREND_PULLBACK_EMA
- **Thesis:** trend-aligned EMA pullback with rejection (`src/channels/scalp.py:619-684`).
- **Rewards today:** indicators/regime baseline.
- **Misses/distortions:** not in regime affinity list, no family/path thesis bonus; volume model can under-reward healthy pullback entries.
- **Judgment:** **under-credited**.

## CONTINUATION_LIQUIDITY_SWEEP
- **Thesis:** trend continuation after sweep reclaim (`src/channels/scalp.py:2544-2563`, `2641-2648`).
- **Rewards today:** in regime affinity + dedicated family bonus up to +4 (`src/signal_quality.py:1495-1498`, `1797-1811`).
- **Misses/distortions:** still inherits RSI/EMA shared bias and heavy post penalties.
- **Judgment:** **roughly fair but penalty-fragile**.

## LIQUIDITY_SWEEP_REVERSAL
- **Thesis:** sweep + reclaim reversal.
- **Rewards today:** sweep naturally scores high in SMC + reversal family bonus up to +8 + regime affinity (`src/signal_quality.py:1570-1583`, `1732-1773`, `1493-1502`).
- **Misses/distortions:** less than other paths.
- **Judgment:** **fair to slightly over-credited vs other families**.

## VOLUME_SURGE_BREAKOUT
- **Thesis:** surge breakout + structured pullback (`src/channels/scalp.py:1157-1175`).
- **Rewards today:** regime affinity includes this setup (`src/signal_quality.py:1494-1502`), volume dimension can help.
- **Misses/distortions:** no family/path thesis layer; RSI scoring can structurally under-reward momentum continuation context.
- **Judgment:** **mildly under-credited**.

## POST_DISPLACEMENT_CONTINUATION
- **Thesis:** displacement -> absorption -> re-acceleration (`src/channels/scalp.py:2801-2827`).
- **Rewards today:** shared model only.
- **Misses/distortions:** no family adjustment, no regime affinity inclusion, path-specific absorption quality not scored directly.
- **Judgment:** **under-credited**.

# 6. Soft-penalty / threshold interaction analysis

## Penalty stack pressure (confirmed)

- Scanner penalties for `360_SCALP` are large (`vwap 15`, `kill_zone 10`, `oi 8`, `volume_div 12`, `cluster 10`, `spoof 12`) before regime multiplier (`src/scanner/__init__.py:404-416`, `2570-2784`).
- Regime multipliers can amplify this (`VOLATILE 1.5`, QUIET scalp override `1.8`) (`src/scanner/__init__.py:306`, `318-324`, `2573-2576`).
- Additional post-score penalties: stat filter (-10 default), pair-analysis weak (-8) (`src/stat_filter.py:198-241`, `src/scanner/__init__.py:3221-3231`).
- Evaluator penalties are also non-trivial (many paths add +11 to +20 penalty potential via `soft_penalty_total`) (`src/channels/scalp.py:1352-1354`, `2002-2004`, `2780-2782`, `3113-3115`, `3413-3415`).

## WATCHLIST bottleneck effect

The architecture strongly supports this pattern: structurally valid setups score into high-60/low-70, then stacked penalties push them into 50-64, then they become free WATCHLIST only.

## Threshold/regime interaction

- `min_confidence` for paid scalp remains 65 (`config/__init__.py:591-605`).
- WATCHLIST branch (50-64) exits before min_conf/component floor (`src/scanner/__init__.py:3361-3378`).
- QUIET has extra strictness (multiplier + hard floor logic), further increasing 65+ conversion difficulty.

# 7. Whether per-path or per-family scoring is required

**Required:** both, with strict scope.

- **Keep universal:** hard safety, risk geometry sanity, stale/correlation controls.
- **Keep shared base model:** as base layer only.
- **Add stronger family-aware scoring:** reclaim/retest, trend-pullback, displacement-continuation families need explicit thesis dimensions.
- **Add path-aware edge scoring where family is too broad:** FAR vs SR_FLIP, and PDC vs CLS need path-specific evidence mapping.

# 8. Best next action

Implement a **scoring architecture correction PR**, not a threshold PR.

- Do **not** lower global thresholds.
- Do **not** inflate scores globally.
- Rebalance by encoding real thesis evidence per family/path and reducing structural under-credit.
- Keep discipline by preserving all hard safety gates and post-trade quality controls.

# 9. Concrete recommendation for the next PR

1. **Extend family thesis layer in `SignalScoringEngine`**:
   - Add family adjustments for `reclaim_retest` and `trend_pullback` and `displacement_continuation`.
   - Keep bounded adjustment ranges (small, auditable).
2. **Add narrow path-aware addenda** for:
   - `FAILED_AUCTION_RECLAIM` (reclaim distance / failed auction quality),
   - `SR_FLIP_RETEST` (retest proximity + rejection quality),
   - `POST_DISPLACEMENT_CONTINUATION` (displacement strength + consolidation quality).
3. **Penalty rebalance without loosening safety**:
   - Keep penalties, but prevent double-counting thesis weaknesses already encoded in path-aware scoring.
   - Cap additive soft-penalty stack per family so one candidate is not over-penalized by overlapping weak-context checks.
4. **No blanket threshold change**:
   - Keep 65 paid floor and WATCHLIST doctrine.
5. **Add score-distribution telemetry by setup_class** at pre-penalty vs post-penalty to verify 65+ conversion improvement is quality-real, not quantity inflation.

---

## Fact vs inference hygiene

- **Confirmed by code:** pipeline order, tier boundaries, penalty mechanics, family-adjustment coverage, routing behavior.
- **Inference (business impact):** WATCHLIST volume + weak paid conversion is primarily a scoring/penalty architecture conversion problem rather than engine uptime/expression problem.
- **Confidence in main verdict:** high.
