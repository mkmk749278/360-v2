# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: none
- Top promising signals/paths: none
- Recommended next investigation target: **none**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `7` sec (warning=False)
- Latest performance record age: `1119` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|

## Evaluator no-signal reasons
- _no reject-reason data parsed from logs in this window — see Log parse diagnostics below_

## Pre-scoring gate rejects (setup-compat / execution-quality)
- _no pre-scoring gate rejects recorded in this window (counters ship 2026-07-18 — a fresh window must accumulate first)_

## Regime distribution
- _no regime data parsed — engine may need redeploy to start emitting `Regime distribution (last 100 cycles): ...` log lines_

## QUIET_SCALP_BLOCK gate
- _no QUIET_SCALP_BLOCK events in window_

## Confidence gate decisions
- _no confidence_gate decisions parsed in window_

## Confidence component breakdown
- _no confidence_gate component samples parsed in window — scoring telemetry may need a refresh after the next deploy_

## Scoring engine breakdown (per-dimension contribution)
- _no engine-component data parsed in window — log line predates the engine-breakdown instrumentation, will populate after redeploy_

## Soft-penalty per-type breakdown
- _no soft-penalty per-type data parsed in window — log line predates the LSR diagnosis instrumentation, will populate after redeploy_

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- _no classified suppressed candidates yet — candidates classify after their validity window (~1h) of real candles has accumulated_

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
_**`suppressed` here means POST-SCORING suppressions only.** `suppression_audit.feeds_edge_matrix` returns False for every pre-scoring reject — `setup_compat:*` and `execution:*` fire ahead of the scoring engine and would swamp the matrix with a differently-measured population (~38k/window against ~4.5k) that Layer C's emission floor reads LIVE.  Those candidates are measured **in the dark lane instead** (`/signals/dark-live`), and the two populations are therefore **disjoint** — every dark row carries a `setup_compat:*` or `execution:*` gate, and none of them can appear here.  A path can read positive on this table and negative in the dark feed with no contradiction, because they are not measuring the same candidates.  Stated on the surface rather than in a docstring because reading one as a check on the other is a mistake this repo has now made (2026-08-04)._
_**Every cell is a 50-outcome ring** (`STRATEGY_EDGE_WINDOW`), so `n` is `min(seen, 50)` and `seen` is the denominator: a saturated cell is a rolling most-recent-50 window while a sparse cell beside it is all-time.  `sampled` counts cells that have evicted at least once._
- Outcomes recorded: **181727 held of 799753 seen** across 21 strategies; 4113 cells past the sample floor; **2187 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 48003 | 634/47369/0 | 44% | -0.18 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.35R) |
| MOVER_AVWAP_SCALP | 24250 | 190/24060/0 | 43% | -0.22 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 14064 | 203/13861/0 | 44% | -0.15 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | LONDON/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 13736 | 148/13588/0 | 36% | -0.31 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 12084 | 69/12015/0 | 38% | -0.30 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 10100 | 105/9995/0 | 37% | -0.44 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 8480 | 423/8057/0 | 45% | -0.13 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8079 | 0/0/8079 | 44% | -0.06 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+1.28R) | LONDON/QUIET/COMPRESSED/BTC_RISING (-0.82R) |
| SHADOW_RANGE_FADE | 7565 | 0/0/7565 | 36% | -0.12 | LONDON/QUIET/COMPRESSED/BTC_FALLING (+0.44R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.25R) |
| SHADOW_FUNDING_FADE | 7055 | 0/0/7055 | 34% | -0.41 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.01R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 5990 | 22/5968/0 | 47% | -0.28 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.30R) |
| MEAN_REVERT | 5397 | 69/5328/0 | 37% | -0.33 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| FUNDING_EXTREME_SIGNAL | 4017 | 2/4015/0 | 30% | -0.48 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 3798 | 0/3798/0 | 29% | -0.40 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| RANGE_FADE | 2286 | 6/2280/0 | 40% | -0.21 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1653 | 0/0/1653 | 53% | -0.07 | ASIA/RANGE/EXPANDED/BTC_NEUTRAL (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 532 | 0/532/0 | 36% | -0.24 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 206 | 32/174/0 | 43% | -0.19 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 58 | 2/56/0 | 45% | +0.15 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `LIQUIDATION_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL` +2.71R (n=23, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 367 | 27% / -0.58R | 367 | 52% / -0.10R | +0.48 | **ATR** |
| TREND_PULLBACK_EMA | 1177 | 38% / -0.38R | 1177 | 50% / -0.09R | +0.29 | **ATR** |
| LIQUIDATION_REVERSAL | 33 | 24% / -0.61R | 33 | 45% / -0.35R | +0.26 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1555 | 42% / -0.37R | 1555 | 57% / -0.12R | +0.25 | **ATR** |
| MA_CROSS_TREND_SHIFT | 62 | 42% / -0.22R | 62 | 47% / -0.06R | +0.15 | **ATR** |
| SR_FLIP_RETEST | 612 | 45% / -0.29R | 612 | 50% / -0.16R | +0.13 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 206 | 37% / -0.19R | 206 | 47% / -0.06R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 2572 | 44% / -0.18R | 2572 | 50% / -0.05R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 8838 | 48% / -0.15R | 8838 | 53% / -0.03R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1477 | 41% / -0.22R | 1477 | 43% / -0.12R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| RANGE_FADE | 126 | 38% / -0.12R | 126 | 45% / -0.04R | +0.08 | **ATR** |
| DIVERGENCE_CONTINUATION | 1721 | 48% / -0.12R | 1721 | 53% / -0.06R | +0.06 | **ATR** |
| MEAN_REVERT | 433 | 47% / -0.14R | 433 | 46% / -0.15R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1485 | 46% / -0.13R | 1485 | 46% / -0.14R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 13 | 62% / -0.06R | 13 | 62% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11755 | 28% | -0.25R | 313 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2572 | 48% | -0.05R | 237 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 131 | 48% | -0.06R | 68 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1819 | 38% / -0.15R | +0.86 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1533 | 33% / -0.23R | +0.83 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3116 | 35% / -0.20R | +0.64 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10747 | 36% / -0.21R | +0.32 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2010 | 36% / -0.14R | +0.14 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1426 | 35% / -0.14R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1223 | 32% / -0.26R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 304 | 31% / -0.38R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 472 | 31% / -0.23R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 358 | 48% / -0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 91 | 44% / +0.01R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 540 | 34% / -0.33R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 99 | 28% / -0.37R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 42 | 45% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 22 | 45% / +0.62R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **6** · boot grace active: False
- **ALERT** `ai_governor_verdicts` — upstream +1 but output +0 (streak 12/6) (sustained 12 cycles)
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×757]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 369/6) (sustained 369 cycles)
- **ALERT** `dark_resolution` — 1 of 180 open dark rows are not being advanced (worst: GRAMUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 123/120) (sustained 123 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 369/6) (sustained 369 cycles)
- **ALERT** `tuned_variants` — 304 non-stamps — atr_arm_uncomputable=304 (seen=9036 stamped=1174 skipped=7558) (streak 369/6) (sustained 369 cycles)
- **ALERT** `auto_dispatch` — 83 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=84) (streak 367/3) (sustained 367 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 49 fed / 0 quiet / 0 never delivered of 49 subscribed; 92369191 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 21 arms current, none stalled; covering 2116/2116 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 12/6) | 12 |
| atr_trail_live_arms | ok | 42 arms current, none stalled; covering 1118/1118 signals (100%) | 0 |
| auto_dispatch | violating | 83 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=84) (streak 367/3) | 367 |
| binance_ip_weight | ok | peak 141/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 74845.70 | 0 |
| candle_coverage | ok | 79/79 symbols with ≥20 15m candles, 79/79 updated within 45m [fresh=79; 74 Tier-1 futures + 6 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 792 dup bars, 0 undedupable; ws 0 out-of-order, 353 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 39 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +11 / upstream +17 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1784/1803 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 1 of 180 open dark rows are not being advanced (worst: GRAMUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 123/120) | 123 |
| dark_sar_arms | ok | no open arms; covering 1776/1795 signals (99%) | 0 |
| depth_feed | ok | 49/49 books fresh (stale 0, never 0, thin 0); 30257614 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 369/6) | 369 |
| emission_controller | ok | last cycle 456s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×757]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 369/6) | 369 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=68, cvd_aligned=1, mover_stack_15m=1. Held back in this window: session_quality=116, cvd_aligned=3. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 4/6) | 4 |
| firestore_read_budget | ok | 1,318 reads/day of 50,000 [engine 1,294, signing 24]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 5880 sealed bars over 49 symbols; 1573 incomplete, 2 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +5 / upstream +187 | 0 |
| indicator_cache_key | ok | 140346 frozen value(s) avoided; 311524 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.34R over n=5328 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +37 / upstream +187 | 0 |
| mover_admission_metadata | ok | 942 symbols known, 235 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 6 held, 6 with scan counts, 5 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 10 locked / 10 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2175 rows held, 3462551 evicted (sampled: execution:trigger_not_confirmed 295/1221148, execution:overextended 295/1079184, setup_compat:regime_STRONG_TREND 294/591561) | 0 |
| price_action_lane | ok | 661661 evaluated, 1230 emitted; layer1 1230 stamped / 0 blind; cooldown=97716, delta_opposed=55258, no_footprint=231388, no_opposing_target=1378, no_sweep=224217, rr_below_floor=50474 | 0 |
| promoted_pair_integrity | ok | 6/6 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.21R over n=2280 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +19 / upstream +187 | 0 |
| sar_alignment_crosscheck | ok | 578/21946 disagreed (2.6%) | 0 |
| sar_exit_shadow | ok | output +10 / upstream +187 | 0 |
| sar_hold_arm | ok | 1871 held arms settled, 129 unscored, 41 still walking (32 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 24/74 unfetchable (32%); top cause: gap or duplicate bar in the 15m window; symbols: B2USDT, ETHFIUSDT, HANAUSDT, TSTUSDT, WLFIUSDT | 0 |
| sar_live_arms | ok | 41 arms current, none stalled; covering 1117/1117 signals (100%) | 0 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 4 resolved, 46 still mid-window | 0 |
| scan_cycle | ok | last 5.15s, worst 248.86s over 7987 lifetime cycles; lifetime 456 over 60s, 91 over 120s; recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 26.22s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 264853 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 6m ago | 0 |
| snapshot_writer | ok | last cycle 27s ago (0.97s to run, worst 186.8s), 1354 overrun(s) of 7703 cycles, TTL 900s; slowest signals=3.96s, data_intake=0.27s, engine_state=0.17s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=17, gate reads=0, withheld=17) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +43 / upstream +187 | 0 |
| structural_snap | ok | 6000/6000 measured, 31 blind, 0 levels moved (refusals: redetect_cooldown=975) | 0 |
| structural_veto_lane | ok | 1947 stamped; 0 with no readable level book, 94 with clear air ahead, 1412 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +187 / upstream +17 | 0 |
| tuned_variants | violating | 304 non-stamps — atr_arm_uncomputable=304 (seen=9036 stamped=1174 skipped=7558) (streak 369/6) | 369 |
| unlock_shorts | ok | 15 open, 45 scheduled, calendar 2.7h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 41 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `0`
- `Path funnel` emissions: `0`
- `Regime distribution` emissions: `0`
- `QUIET_SCALP_BLOCK` events: `0`
- `confidence_gate` events: `0`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness

## Lifecycle truth summary
- Median create→dispatch: `4.4417359828948975` sec
- Median create→first breach: `4444.682476043701` sec
- Median create→terminal: `4444.682496070862` sec
- Median first breach→terminal: `6.389617919921875e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.9298920119501274 | 2.4921363040629054 | 0.3731304786315795 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 1.1324731694265289 | 1.2146994547113352 | 0.9323073004059701 | 0 | 1 |
| MOVER_AVWAP_SCALP | 2 | 2 | 2.327454731557823 | 2.729973763012368 | 0.8470206090424219 | 0 | 2 |
| MOVER_TREND_PULLBACK | 23 | 23 | 3.66819033090003 | 3.0 | 1.3213298712263988 | 17 | 6 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 0.9054068827490555 | 0.9558051093434232 | 0.90342881064983 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.4921 | 260.2932870388031 | 260.29335498809814 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.1325 | 5387.843405008316 | 5387.843505859375 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 13014.286410570145 | 13014.286442637444 |
| MOVER_TREND_PULLBACK | 23 | 23 | 26.1 | 30.4 | 26.1 | 0.0 | 0.1261 | 3825.7285528182983 | 3827.540740966797 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 0.0 | 50.0 | 0.0 | 0.0 | -0.3743 | 9928.741691112518 | 9928.741792559624 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `0`
- Gating Δ: `0`
- No-generation Δ: `0`
- Fast failures Δ: `-1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -2.8481, "current_avg_pnl": -2.4921, "current_win_rate": 0.0, "previous_avg_pnl": 0.356, "previous_win_rate": 20.0, "win_rate_delta": -20.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.3113, "current_avg_pnl": -1.1325, "current_win_rate": 0.0, "previous_avg_pnl": -0.8212, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.496, "current_avg_pnl": 0.0, "current_win_rate": 0.0, "previous_avg_pnl": 0.496, "previous_win_rate": 50.0, "win_rate_delta": -50.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 2.37, "current_avg_pnl": 0.1261, "current_win_rate": 26.1, "previous_avg_pnl": -2.2439, "previous_win_rate": 3.6, "win_rate_delta": 22.5}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -1.3524, "current_avg_pnl": -0.3743, "current_win_rate": 0.0, "previous_avg_pnl": 0.9781, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": -1.0286, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 1.0286, "previous_win_rate": 33.3, "win_rate_delta": -33.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -23773.77, "median_terminal_delta_sec": -23774.21, "sl_rate_delta": -50.0, "win_rate_delta": -50.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -3357.16, "median_terminal_delta_sec": -3357.42, "sl_rate_delta": -33.3, "win_rate_delta": -33.3}}`

## Recommended operator focus
- Most suspicious degradation: **none**
- Most promising healthy path: **none**
- Most likely bottleneck: **none**
- Suggested next investigation target: **none**
