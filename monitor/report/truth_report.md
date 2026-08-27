# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `14` sec (warning=False)
- Latest performance record age: `4096` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| DIVERGENCE_CONTINUATION | 0 | 0 | 156 | 156 | 132 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 3526 | 3527 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 3539 | 3541 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 3526 | 3485 | 51 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::FAILED_AUCTION_RECLAIM | 3543 | 3500 | 43 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 3524 | 3523 | 2 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 2940 | 2943 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 3543 | 3544 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::MEAN_REVERT | 3544 | 3388 | 245 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 3746 | 4088 | 19 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 3527 | 3243 | 500 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 3472 | 3475 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 3542 | 3542 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 3525 | 3526 | 0 | 0 | 0 | 0 | non-generating (compression_not_detected) |
| EVAL::RANGE_FADE | 3633 | 3499 | 167 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 3475 | 3523 | 0 | 0 | 0 | 0 | non-generating (flip_close_not_confirmed) |
| EVAL::STANDARD | 2913 | 2539 | 400 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 2939 | 2940 | 0 | 0 | 0 | 0 | non-generating (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 3523 | 3526 | 0 | 0 | 0 | 0 | non-generating (move_not_fresh) |
| EVAL::WHALE_MOMENTUM | 2943 | 2943 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 114 | 114 | 102 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 9 | 9 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 1562 | 1562 | 1562 | 0 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 1 | 1 | 0 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 584 | 584 | 584 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 52 | 52 | 0 | 1 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 1264 | 1264 | 570 | 28 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 382 | 382 | 382 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 7 | 7 | 7 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 10 | 10 | 10 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=3527): breakout_not_found=2593, basic_filters_failed=895, breakout_stale=16, move_not_fresh=14, retest_proximity_failed=8, volume_spike_missing=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=3541): cls_disabled_merged_into_lsr=3541
- **EVAL::DIVERGENCE_CONTINUATION** (total=3485): h1_trend_not_aligned=1388, cvd_divergence_failed=844, basic_filters_failed=685, ema_alignment_reject=457, retest_proximity_failed=110, missing_fvg_or_orderblock=1
- **EVAL::FAILED_AUCTION_RECLAIM** (total=3500): auction_not_detected=2284, basic_filters_failed=639, reclaim_hold_failed=298, regime_blocked=207, tail_too_small=72
- **EVAL::FUNDING_EXTREME** (total=3523): funding_not_extreme=2471, basic_filters_failed=665, missing_funding_rate=197, rsi_reject=125, ema_alignment_reject=59, cvd_divergence_failed=4, momentum_reject=2
- **EVAL::LIQUIDATION_REVERSAL** (total=2943): cascade_threshold_not_met=2171, basic_filters_failed=674, cvd_divergence_failed=71, rsi_reject=26, missing_fvg_or_orderblock=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=3544): no_ma_cross=2805, basic_filters_failed=687, ma_cross_cooldown=52
- **EVAL::MEAN_REVERT** (total=3388): no_extension=2924, basic_filters_failed=464
- **EVAL::MOVER_AVWAP_SCALP** (total=4088): no_avwap_tag=2265, basic_filters_failed=905, no_mover_leg=644, avwap_slope_against=133, no_avwap_reclaim=76, avwap_reclaim_no_volume=65
- **EVAL::MOVER_TREND_PULLBACK** (total=3243): mover_run_too_small=1659, basic_filters_failed=899, no_reclaim=568, no_pullback_tag=117
- **EVAL::OPENING_RANGE_BREAKOUT** (total=3475): feature_disabled=3475
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=3542): regime_blocked=2609, breakout_not_found=721, basic_filters_failed=200, adx_reject=10, ema_alignment_reject=2
- **EVAL::QUIET_COMPRESSION_BREAK** (total=3526): compression_not_detected=1866, regime_blocked=1134, basic_filters_failed=437, breakout_not_detected=89
- **EVAL::RANGE_FADE** (total=3499): no_range_edge=3035, basic_filters_failed=464
- **EVAL::SR_FLIP_RETEST** (total=3523): flip_close_not_confirmed=2344, basic_filters_failed=636, long_break_volume_thin=210, regime_blocked=205, h1_break_not_confirmed=65, retest_out_of_zone=43, reclaim_hold_failed=11, long_acceptance_not_held=9
- **EVAL::STANDARD** (total=2539): momentum_reject=1133, basic_filters_failed=405, macd_reject=269, adx_reject=260, ema_alignment_reject=219, sweeps_not_detected=153, htf_poi_unanchored=83, rsi_reject=10, invalid_sl_geometry=7
- **EVAL::TREND_PULLBACK** (total=2940): h1_trend_not_aligned=1371, ema_alignment_reject=482, basic_filters_failed=304, h1_pullback_not_confirmed=299, ema_not_tested_prev=204, no_ema_reclaim_close=114, rsi_reject=79, body_conviction_fail=61, ema21_not_tagged=7, prev_already_above_emas=7, no_prev_high_break=6, momentum_flat=5, prev_already_below_emas=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=3526): move_not_fresh=1781, basic_filters_failed=895, breakout_not_found=621, breakout_stale=135, retest_proximity_failed=81, volume_spike_missing=13
- **EVAL::WHALE_MOMENTUM** (total=2943): momentum_reject=2200, recent_ticks_insufficient=529, basic_filters_failed=214

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **FUNDING_EXTREME_SIGNAL** (total=9): execution:trigger_not_confirmed=9
- **LIQUIDITY_SWEEP_REVERSAL** (total=386): execution:trigger_not_confirmed=183, setup_compat:regime_STRONG_TREND=133, execution:overextended=70
- **MA_CROSS_TREND_SHIFT** (total=1): setup_compat:regime_DIRTY_RANGE=1
- **MEAN_REVERT** (total=101): setup_compat:regime_STRONG_TREND=63, setup_compat:regime_WEAK_TREND=38
- **MOVER_AVWAP_SCALP** (total=26): execution:overextended=26
- **MOVER_TREND_PULLBACK** (total=482): execution:overextended=327, execution:trigger_not_confirmed=142, entry_quality=13
- **RANGE_FADE** (total=137): setup_compat:regime_STRONG_TREND=68, setup_compat:regime_VOLATILE_UNSUITABLE=53, setup_compat:regime_WEAK_TREND=16
- **TREND_PULLBACK_EMA** (total=10): setup_compat:regime_DIRTY_RANGE=5, setup_compat:regime_VOLATILE_UNSUITABLE=5

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 9824 | 58.5% |
| TRENDING_UP | 4582 | 27.3% |
| VOLATILE | 1174 | 7.0% |
| QUIET | 741 | 4.4% |
| TRENDING_DOWN | 467 | 2.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **3**
- Average confidence gap to threshold: **5.40** (samples=3) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: VELVETUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 24 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 2 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 39 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 20 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 214 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 3 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 448 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | kept | 24 | 70.83 | 65.00 | -5.83 | 20.37 | 19.97 | 17.23 | -0.08 | -3.00 |
| FAILED_AUCTION_RECLAIM | filtered | 2 | 27.20 | 61.00 | 33.80 | 21.50 | 20.00 | 20.00 | 5.00 | 31.00 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 51.30 | 61.00 | 9.70 | 21.20 | 19.80 | 15.80 | 0.00 | 20.00 |
| MOVER_AVWAP_SCALP | filtered | 39 | 54.86 | 63.21 | 8.35 | 19.85 | 16.06 | 15.80 | 2.47 | 17.96 |
| MOVER_AVWAP_SCALP | kept | 20 | 81.87 | 65.00 | -16.87 | 20.29 | 17.05 | 15.80 | 3.85 | 3.58 |
| MOVER_TREND_PULLBACK | filtered | 217 | 58.61 | 64.32 | 5.71 | 21.70 | 17.88 | 15.80 | 4.23 | 6.82 |
| MOVER_TREND_PULLBACK | kept | 448 | 79.22 | 65.00 | -14.22 | 20.38 | 18.33 | 15.80 | 4.52 | -0.09 |
| TREND_PULLBACK_EMA | kept | 2 | 80.75 | 65.00 | -15.75 | 22.05 | 19.75 | 17.85 | 5.00 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | kept | 24 | 70.83 | 22.67 | 18.00 | 5.88 | 10.04 | 5.00 | 9.33 | -0.08 |
| FAILED_AUCTION_RECLAIM | filtered | 2 | 27.20 | 25.00 | 18.00 | 3.00 | 12.00 | 8.50 | 1.70 | 5.00 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 51.30 | 25.00 | 14.00 | 6.00 | 14.00 | 5.00 | 7.30 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 39 | 54.86 | 18.64 | 18.00 | 10.92 | 12.72 | 5.00 | 5.06 | 2.47 |
| MOVER_AVWAP_SCALP | kept | 20 | 81.87 | 17.70 | 18.00 | 14.10 | 14.00 | 7.80 | 10.00 | 3.85 |
| MOVER_TREND_PULLBACK | filtered | 217 | 58.61 | 18.03 | 18.22 | 8.19 | 13.01 | 5.43 | 8.13 | 4.23 |
| MOVER_TREND_PULLBACK | kept | 448 | 79.22 | 20.18 | 18.01 | 8.13 | 12.44 | 6.58 | 9.44 | 4.52 |
| TREND_PULLBACK_EMA | kept | 2 | 80.75 | 17.00 | 18.00 | 7.50 | 14.00 | 9.25 | 10.00 | 5.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | kept | 24 | 70.83 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 2 | 27.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.00 | 0.00 | 0.00 | **5.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 51.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 39 | 54.86 | 0.00 | 0.00 | 0.00 | 0.00 | 7.69 | 0.00 | 0.00 | 3.85 | **11.54** |
| MOVER_AVWAP_SCALP | kept | 20 | 81.87 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 217 | 58.61 | 2.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | **2.61** |
| MOVER_TREND_PULLBACK | kept | 448 | 79.22 | 0.03 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.06** |
| TREND_PULLBACK_EMA | kept | 2 | 80.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **44741 held of 96620 seen** across 21 strategies; 990 cells past the sample floor; **408 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 22367 | 95/22272/0 | 44% | -0.17 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | OFF_HOURS/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (-1.21R) |
| MOVER_AVWAP_SCALP | 4981 | 13/4968/0 | 43% | -0.27 | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (+1.03R) | ASIA/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.36R) |
| FAILED_AUCTION_RECLAIM | 3225 | 14/3211/0 | 43% | -0.18 | NY/MARKUP/COMPRESSED/BTC_NEUTRAL (+1.42R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| DIVERGENCE_CONTINUATION | 2239 | 0/2239/0 | 51% | -0.05 | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.05R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 2217 | 0/0/2217 | 42% | -0.09 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.72R) | NY/RANGE/EXPANDED/BTC_RISING (-0.89R) |
| TREND_PULLBACK_EMA | 2206 | 0/2206/0 | 40% | -0.26 | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+0.72R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.31R) |
| SHADOW_RANGE_FADE | 1897 | 0/0/1897 | 36% | -0.06 | LONDON/RANGE/NORMAL/BTC_NEUTRAL (+0.38R) | OFF_HOURS/MARKUP/NORMAL/BTC_RISING (-0.87R) |
| QUIET_COMPRESSION_BREAK | 1209 | 22/1187/0 | 32% | -0.14 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+0.45R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-0.47R) |
| SHADOW_FUNDING_FADE | 1135 | 0/0/1135 | 41% | -0.30 | NY/MARKDOWN/COMPRESSED/BTC_RISING (+0.58R) | OFF_HOURS/QUIET/COMPRESSED/BTC_RISING (-0.93R) |
| WHALE_MOMENTUM | 1098 | 0/1098/0 | 31% | -0.49 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| FUNDING_EXTREME_SIGNAL | 552 | 0/552/0 | 26% | -0.55 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OFF_HOURS/QUIET/COMPRESSED/BTC_RISING (-1.20R) |
| VOLUME_SURGE_BREAKOUT | 476 | 0/476/0 | 54% | +0.11 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| MEAN_REVERT | 326 | 2/324/0 | 72% | +0.51 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR (+1.13R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.18R) |
| LIQUIDITY_SWEEP_REVERSAL | 308 | 6/302/0 | 42% | -0.20 | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-0.26R) | LONDON/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (-0.54R) |
| SHADOW_CASCADE_REVERSAL | 231 | 0/0/231 | 59% | +0.01 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.03R) |
| BREAKDOWN_SHORT | 144 | 6/138/0 | 8% | -0.85 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| RANGE_FADE | 54 | 0/54/0 | 33% | -0.53 | — | — |
| SR_FLIP_RETEST | 50 | 0/50/0 | 80% | +0.48 | — | — |
| MA_CROSS_TREND_SHIFT | 18 | 0/18/0 | 33% | -0.19 | — | — |
| LIQUIDATION_REVERSAL | 6 | 0/6/0 | 33% | -0.41 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 2 | 0/2/0 | 100% | +0.56 | — | — |

- **Strongest cells**: `FAILED_AUCTION_RECLAIM @ NY/MARKUP/COMPRESSED/BTC_NEUTRAL` +1.42R (n=34, STRONG); `FAILED_AUCTION_RECLAIM @ NY/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +1.42R (n=34, STRONG); `MOVER_TREND_PULLBACK @ ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR` +1.17R (n=32, STRONG)
- **Weakest cells**: `MOVER_AVWAP_SCALP @ ASIA/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.36R (n=15, NEGATIVE); `TREND_PULLBACK_EMA @ NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.31R (n=50, NEGATIVE); `TREND_PULLBACK_EMA @ ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.24R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 43 | 28% / -0.55R | 43 | 49% / -0.11R | +0.44 | **ATR** |
| TREND_PULLBACK_EMA | 181 | 46% / -0.16R | 181 | 53% / -0.05R | +0.12 | **ATR** |
| MEAN_REVERT | 34 | 56% / +0.09R | 34 | 56% / +0.20R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 357 | 52% / -0.10R | 357 | 58% / -0.01R | +0.09 | **ATR** |
| WHALE_MOMENTUM | 127 | 36% / -0.39R | 127 | 38% / -0.30R | +0.09 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 33 | 55% / +0.14R | 33 | 58% / +0.06R | -0.08 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 211 | 46% / -0.15R | 211 | 48% / -0.08R | +0.07 | **ATR** |
| MOVER_TREND_PULLBACK | 3290 | 54% / -0.02R | 3290 | 59% / +0.04R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 85 | 51% / -0.14R | 85 | 54% / -0.12R | +0.02 | **ATR** |
| DIVERGENCE_CONTINUATION | 204 | 52% / -0.01R | 204 | 59% / -0.02R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 145 | 48% / -0.11R | 145 | 48% / -0.11R | -0.00 | **FIXED** |
| RANGE_FADE | 6 | 50% / +0.16R | 6 | 50% / +0.02R | — | **MEASURING** |
| SR_FLIP_RETEST | 13 | 62% / +0.00R | 13 | 62% / -0.01R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 5 | 20% / -0.34R | 5 | 20% / -0.31R | — | **MEASURING** |
| BREAKDOWN_SHORT | 9 | 11% / -0.57R | 9 | 11% / -0.34R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 1 | 100% / +0.56R | 1 | 100% / +0.37R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 1 | 100% / +1.11R | 1 | 100% / +0.37R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 4895 | 32% | -0.08R | 216 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 357 | 56% | -0.00R | 100 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 23 | 65% | +0.09R | 22 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 51 | 29% / -0.05R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 139 | 46% / +0.57R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 4051 | 39% / -0.05R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 417 | 37% / +0.25R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 146 | 40% / +0.06R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 224 | 41% / +0.26R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 229 | 38% / -0.19R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 88 | 47% / -0.10R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 51 | 33% / -0.23R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 43 | 28% / -0.47R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 32 | 56% / +0.16R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 23 | 30% / -0.28R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 6 | 50% / -0.04R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 14 | 36% / -0.30R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 9 | 11% / -0.72R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 3 | 33% / -1.43R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 1 | 100% / +1.90R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 52 · alerting: **5** · boot grace active: False
- **ALERT** `cohort_edge_gate` — all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 12 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 6/6) (sustained 6 cycles)
- **ALERT** `edge_reconciliation` — MOVER_TREND_PULLBACK realized−counterfactual=+0.32R (bound 0.3) (streak 6/6) (sustained 6 cycles)
- **ALERT** `mean_revert_emission` — 447 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.51R over n=324, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 6/6) (sustained 6 cycles)
- **ALERT** `range_fade_emission` — 419 detections since last emission (emitted_total=0) — and only 54 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 6/6) (sustained 6 cycles)
- **ALERT** `tuned_variants` — 25 non-stamps — atr_arm_uncomputable=25 (seen=439 stamped=57 skipped=357) (streak 6/6) (sustained 6 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 1909750 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 14 arms current, none stalled; covering 290/290 signals (100%) | 0 |
| auto_dispatch | ok | attempts=0 fanouts=0 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 80026.90 | 0 |
| candle_coverage | ok | 90/91 symbols with ≥20 15m candles, 89/91 updated within 45m [no_bucket=1, stale=1, fresh=89; 14 promoted of 91]; 2 CORE pair(s) unusable (e.g. KERNELUSDT, SKYUSDT) | 0 |
| candle_series_integrity | ok | merge dropped 304 dup bars, 0 undedupable; ws 0 out-of-order, 138 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | violating | all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 12 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 6/6) | 6 |
| context_emission_policy | ok | output +55 / upstream +22 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1096/1110 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 4 of 110 open dark rows are not being advanced (worst: STARUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 6/120) | 6 |
| dark_sar_arms | ok | no open arms; covering 1097/1111 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 309830 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_TREND_PULLBACK realized−counterfactual=+0.32R (bound 0.3) (streak 6/6) | 6 |
| emission_controller | ok | last cycle 1716s ago; live_overrides=29 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=16 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4336 stamps (MEAN_REVERT=1415, MOVER_AVWAP_SCALP=319, MOVER_TREND_PULLBACK=2141, RANGE_FADE=428, TREND_PULLBACK_EMA=33), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | 448 evaluated, 14 suppressed, 237 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m | 0 |
| footprint_bars | ok | 2720 sealed bars over 40 symbols; 0 incomplete, 1 shape-capped | 0 |
| gate_override_shadow | ok | counter reset | 0 |
| geometry_ab | ok | output +4 / upstream +180 | 0 |
| indicator_cache_key | ok | 1245 frozen value(s) avoided; 12297 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 447 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.51R over n=324, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 6/6) | 6 |
| mean_revert_path | violating | upstream +180 but output +0 (streak 1/72) | 1 |
| mover_admission_metadata | ok | 877 symbols known, 175 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 14 held, 14 with scan counts, 13 with an activity reading (enforcing) | 0 |
| position_lock_integrity | ok | 3 locked / 3 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3080 rows held, 809202 evicted (sampled: execution:trigger_not_confirmed 400/295888, execution:overextended 400/287969, setup_compat:regime_STRONG_TREND 400/103926) | 0 |
| price_action_lane | ok | 20171 evaluated, 28 emitted; layer1 28 stamped / 0 blind; cooldown=2911, delta_opposed=2117, no_footprint=8468, no_sweep=4680, rr_below_floor=1967 | 0 |
| promoted_pair_integrity | ok | 14/14 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 419 detections since last emission (emitted_total=0) — and only 54 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 6/6) | 6 |
| range_fade_path | ok | output +20 / upstream +180 | 0 |
| sar_alignment_crosscheck | ok | 6/1411 disagreed (0.4%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +180 | 0 |
| sar_hold_arm | ok | 489 held arms settled, 95 unscored, 14 still walking (9 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 18/122 unfetchable (15%); top cause: gap or duplicate bar in the 15m window; symbols: 1000SHIBUSDT, APTUSDT, ARBUSDT, DOGEUSDT, FETUSDT +4 more | 0 |
| sar_live_arms | ok | 15 arms current, none stalled; covering 299/299 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 1 resolved, 103 still mid-window | 0 |
| scan_cycle | ok | last 29.35s, worst 93.78s over 237 cycles; 2 over 60s, 0 over the 120s healthcheck deadline (plus 1/0 during boot warm-up, not counted); 8 executor workers | 0 |
| setup_tf_resolver | ok | 9361 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| snapshot_writer | ok | last cycle 25s ago (6.64s to run, worst 61.1s), 28 overrun(s) of 237 cycles, TTL 900s; slowest signals=3.57s, tickers=3.47s, engine_state=2.53s | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | counter reset | 0 |
| strategy_edge | ok | output +174 / upstream +180 | 0 |
| structural_snap | ok | 4338/4338 measured, 16 blind, 0 levels moved (refusals: redetect_cooldown=148) | 0 |
| structural_veto_lane | ok | 189 stamped; 0 with no readable level book, 34 with clear air ahead, 129 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +180 / upstream +22 | 0 |
| tuned_variants | violating | 25 non-stamps — atr_arm_uncomputable=25 (seen=439 stamped=57 skipped=357) (streak 6/6) | 6 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `7363`
- `Path funnel` emissions: `2`
- `Regime distribution` emissions: `2`
- `QUIET_SCALP_BLOCK` events: `3`
- `confidence_gate` events: `753`
- `free_channel_post` events: `1`
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
- Total posts in window: **1**

| Source | Count |
|---|---:|
| signal_close | 1 |

- By severity: HIGH=1

## Dependency readiness
- cvd: presence[present=13130] state[populated=13130] buckets[many=13130] sources[none] quality[none]
- funding_rate: presence[absent=1752, present=11378] state[empty=1752, populated=11378] buckets[few=11378, none=1752] sources[none] quality[none]
- liquidation_clusters: presence[absent=6206, present=6924] state[empty=6206, populated=6924] buckets[few=5877, none=6206, some=1047] sources[none] quality[none]
- oi_snapshot: presence[absent=1281, present=11849] state[empty=1281, populated=11849] buckets[many=11849, none=1281] sources[none] quality[none]
- order_book: presence[absent=3639, present=9491] state[populated=9491, unavailable=3639] buckets[few=9491, none=3639] sources[book_ticker=9491, unavailable=3639] quality[none=3639, top_of_book_only=9491]
- orderblocks: presence[absent=13130] state[empty=13130] buckets[none=13130] sources[measured_dark=13130] quality[none]
- recent_ticks: presence[present=13130] state[populated=13130] buckets[many=13130] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `15.535074949264526` sec
- Median create→first breach: `3280.0355360507965` sec
- Median create→terminal: `3671.66787981987` sec
- Median first breach→terminal: `6.170600891113281` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 2 | 2 | 2.6116078335286472 | 3.0 | 0.8705359445095492 | 0 | 2 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 1.7515426497277522 | 1.7452370961887458 | 1.0036130068245608 | 0 | 0 |
| MOVER_AVWAP_SCALP | 1 | 1 | 2.1930973825577538 | 2.531650163315521 | 0.8662718942516177 | 0 | 1 |
| MOVER_TREND_PULLBACK | 23 | 23 | 4.218812876663895 | 3.0 | 1.4972917046029883 | 18 | 3 |
| QUIET_COMPRESSION_BREAK | 2 | 2 | 1.0274738419475262 | 1.104788234409095 | 0.9451506220684875 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 3.7226 | 2338.3849869966507 | 66160.18268847466 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 1.9832 | 19904.13256597519 | 149778.25435900688 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.1931 | 11243.588740110397 | 11251.333844900131 |
| MOVER_TREND_PULLBACK | 23 | 23 | 0.0 | 39.1 | 0.0 | 0.0 | -0.0717 | 2672.6615159511566 | 2693.7946569919586 |
| QUIET_COMPRESSION_BREAK | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.9603 | 30153.0087120533 | 79435.27684497833 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 7 | 0 | 7 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 10 | 0 | 10 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `29`
- Gating Δ: `3350`
- No-generation Δ: `64295`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.2094, "current_avg_pnl": -0.0717, "current_win_rate": 0.0, "previous_avg_pnl": 0.1377, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
