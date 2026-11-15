# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: QUIET_COMPRESSION_BREAK
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `2165` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 83 | 83 | 83 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 12994 | 12994 | 10980 | 45 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 70134 | 70136 | 22 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 66533 | 66533 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 66202 | 63254 | 3268 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 66557 | 66110 | 478 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 66555 | 66508 | 64 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 55387 | 55393 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 66589 | 66605 | 6 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 66615 | 64244 | 3196 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 77136 | 82110 | 471 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 70161 | 58781 | 18318 | 0 | 0 | 0 | low-sample (no_reclaim) |
| EVAL::OPENING_RANGE_BREAKOUT | 66222 | 66222 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 66536 | 66555 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 66187 | 66164 | 33 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 67444 | 65084 | 2874 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 65839 | 66028 | 136 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 54867 | 52429 | 2595 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 55026 | 54717 | 362 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 70109 | 70117 | 15 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 55397 | 55410 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1927 | 1927 | 1821 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 388 | 388 | 214 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 9 | 9 | 5 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 13116 | 13116 | 12954 | 2 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 13 | 13 | 2 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7907 | 7907 | 6903 | 4 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1547 | 1547 | 150 | 47 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 53764 | 53764 | 22319 | 972 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 1 | 1 | 0 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 324 | 324 | 213 | 11 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 6650 | 6650 | 4889 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 398 | 398 | 135 | 5 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2137 | 2137 | 1538 | 54 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 113 | 113 | 85 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=70136): breakout_not_found=35032, basic_filters_failed=20490, move_not_fresh=10506, breakout_stale=2755, retest_proximity_failed=1098, volume_spike_missing=252, missing_fvg_or_orderblock=2, move_exhausted=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=66533): cls_disabled_merged_into_lsr=66533
- **EVAL::DIVERGENCE_CONTINUATION** (total=63254): cvd_divergence_failed=30372, basic_filters_failed=16309, ema_alignment_reject=8037, h1_trend_not_aligned=5509, retest_proximity_failed=2634, missing_fvg_or_orderblock=393
- **EVAL::FAILED_AUCTION_RECLAIM** (total=66110): auction_not_detected=44640, basic_filters_failed=15691, regime_blocked=2280, reclaim_hold_failed=2047, tail_too_small=1443, rsi_reject=9
- **EVAL::FUNDING_EXTREME** (total=66508): funding_not_extreme=48855, basic_filters_failed=16381, missing_funding_rate=500, ema_alignment_reject=462, rsi_reject=143, momentum_reject=90, cvd_divergence_failed=50, missing_fvg_or_orderblock=27
- **EVAL::LIQUIDATION_REVERSAL** (total=55393): cascade_threshold_not_met=38535, basic_filters_failed=16311, cvd_divergence_failed=270, rsi_reject=246, missing_fvg_or_orderblock=21, volume_spike_missing=10
- **EVAL::MA_CROSS_TREND_SHIFT** (total=66605): no_ma_cross=49601, basic_filters_failed=16318, ma_cross_cooldown=576, ma_cross_htf_misaligned=110
- **EVAL::MEAN_REVERT** (total=64244): no_extension=52739, basic_filters_failed=11505
- **EVAL::MOVER_AVWAP_SCALP** (total=82110): no_avwap_tag=38723, basic_filters_failed=20600, no_mover_leg=14485, avwap_slope_against=5491, avwap_reclaim_no_volume=1676, no_avwap_reclaim=1132, anchor_too_recent=3
- **EVAL::MOVER_TREND_PULLBACK** (total=58781): no_reclaim=20852, basic_filters_failed=20552, mover_run_too_small=13860, no_pullback_tag=3517
- **EVAL::OPENING_RANGE_BREAKOUT** (total=66222): feature_disabled=66222
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=66555): regime_blocked=31170, breakout_not_found=26371, basic_filters_failed=7145, adx_reject=1793, ema_alignment_reject=70, rsi_reject=6
- **EVAL::QUIET_COMPRESSION_BREAK** (total=66164): regime_blocked=37464, compression_not_detected=19050, basic_filters_failed=8540, breakout_not_detected=970, volume_confirmation_failed=136, rsi_reject=3, missing_fvg_or_orderblock=1
- **EVAL::RANGE_FADE** (total=65084): no_range_edge=53576, basic_filters_failed=11508
- **EVAL::SR_FLIP_RETEST** (total=66028): flip_close_not_confirmed=43276, basic_filters_failed=15679, regime_blocked=2270, retest_out_of_zone=1718, h1_break_not_confirmed=1238, long_break_volume_thin=1130, reclaim_hold_failed=480, long_acceptance_not_held=101, whipsaw_flip=63, ema_alignment_reject=41, wick_quality_failed=32
- **EVAL::STANDARD** (total=52429): momentum_reject=18307, basic_filters_failed=9433, adx_reject=8928, ema_alignment_reject=5703, sweeps_not_detected=5436, macd_reject=3752, htf_poi_unanchored=773, rsi_reject=52, invalid_sl_geometry=45
- **EVAL::TREND_PULLBACK** (total=54717): h1_pullback_not_confirmed=18927, h1_trend_not_aligned=8369, ema_alignment_reject=7395, basic_filters_failed=6599, ema_not_tested_prev=5777, no_ema_reclaim_close=3049, body_conviction_fail=1582, rsi_reject=1501, prev_already_below_emas=728, no_prev_low_break=478, momentum_flat=114, ema21_not_tagged=79, prev_already_above_emas=54, missing_fvg_or_orderblock=30, no_prev_high_break=24, momentum_reject=11
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=70117): breakout_not_found=39466, basic_filters_failed=20488, move_not_fresh=5534, breakout_stale=2316, retest_proximity_failed=1987, volume_spike_missing=305, missing_fvg_or_orderblock=19, move_exhausted=2
- **EVAL::WHALE_MOMENTUM** (total=55410): momentum_reject=46960, recent_ticks_insufficient=5782, basic_filters_failed=2668

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=2): execution:overextended=2
- **DIVERGENCE_CONTINUATION** (total=426): setup_compat:regime_VOLATILE_UNSUITABLE=399, setup_compat:regime_BREAKOUT_EXPANSION=16, execution:overextended=11
- **FAILED_AUCTION_RECLAIM** (total=999): setup_compat:regime_STRONG_TREND=503, execution:overextended=402, setup_compat:regime_VOLATILE_UNSUITABLE=60, context_floor=34
- **FUNDING_EXTREME_SIGNAL** (total=312): execution:trigger_not_confirmed=307, context_floor=5
- **LIQUIDATION_REVERSAL** (total=9): execution:trigger_not_confirmed=9
- **LIQUIDITY_SWEEP_REVERSAL** (total=5018): setup_compat:regime_STRONG_TREND=2576, execution:trigger_not_confirmed=1262, execution:overextended=1180
- **MA_CROSS_TREND_SHIFT** (total=7): setup_compat:regime_CLEAN_RANGE=2, setup_compat:regime_DIRTY_RANGE=2, execution:overextended=2, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=7473): setup_compat:regime_STRONG_TREND=4160, setup_compat:regime_WEAK_TREND=1872, execution:overextended=1397, entry_quality=44
- **MOVER_AVWAP_SCALP** (total=1012): execution:overextended=652, entry_quality=263, execution:trigger_not_confirmed=97
- **MOVER_TREND_PULLBACK** (total=25952): execution:trigger_not_confirmed=13799, execution:overextended=7181, entry_quality=4972
- **RANGE_FADE** (total=5579): setup_compat:regime_STRONG_TREND=3347, setup_compat:regime_WEAK_TREND=1624, setup_compat:regime_VOLATILE_UNSUITABLE=434, execution:overextended=145, context_edge=29
- **TREND_PULLBACK_EMA** (total=1629): setup_compat:regime_CLEAN_RANGE=1057, setup_compat:regime_DIRTY_RANGE=374, entry_quality=103, setup_compat:regime_VOLATILE_UNSUITABLE=95

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_DOWN | 127041 | 31.0% |
| RANGING | 116069 | 28.3% |
| TRENDING_UP | 94555 | 23.0% |
| QUIET | 52290 | 12.7% |
| VOLATILE | 20372 | 5.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **286**
- Average confidence gap to threshold: **8.91** (samples=286) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: AAVEUSDT=33, DOTUSDT=29, LINKUSDT=28, BULLAUSDT=22, AVAXUSDT=21, SOLUSDT=20, TIAUSDT=18, FILUSDT=16, SUIUSDT=12, TRUMPUSDT=12

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 314 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 28 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 704 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 19 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 3 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 12 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 81 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 6 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 3 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 3 |
| MEAN_REVERT | filtered | min_confidence | 69 |
| MEAN_REVERT | kept | min_confidence_pass | 7 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 411 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 35 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 440 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 3281 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 197 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 10091 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 11 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 9 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 65 |
| SR_FLIP_RETEST | filtered | min_confidence | 27 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 2 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 140 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 106 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 10 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 241 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 30 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 342 | 56.45 | 64.05 | 7.60 | 20.34 | 19.66 | 18.63 | 0.59 | 12.83 |
| DIVERGENCE_CONTINUATION | kept | 704 | 70.01 | 65.00 | -5.01 | 20.51 | 19.61 | 18.24 | 0.96 | 1.30 |
| FAILED_AUCTION_RECLAIM | filtered | 22 | 52.78 | 65.00 | 12.22 | 22.73 | 19.77 | 20.00 | 1.30 | 3.20 |
| FUNDING_EXTREME_SIGNAL | filtered | 12 | 45.24 | 61.00 | 15.76 | 20.78 | 15.71 | 17.18 | 4.17 | 7.33 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 81 | 51.85 | 64.21 | 12.36 | 20.65 | 19.09 | 17.97 | 1.69 | 6.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 6 | 67.48 | 65.00 | -2.48 | 20.10 | 18.48 | 17.00 | 0.50 | 4.92 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 47.60 | 61.00 | 13.40 | 20.90 | 19.13 | 15.80 | 0.00 | 23.60 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 67.83 | 65.00 | -2.83 | 20.57 | 17.50 | 15.80 | 0.00 | 4.00 |
| MEAN_REVERT | filtered | 69 | 59.22 | 64.30 | 5.08 | 20.38 | 14.00 | 16.27 | 0.00 | 10.82 |
| MEAN_REVERT | kept | 7 | 67.37 | 65.00 | -2.37 | 20.19 | 14.00 | 16.30 | 0.00 | 4.50 |
| MOVER_AVWAP_SCALP | filtered | 446 | 53.81 | 65.00 | 11.19 | 20.47 | 15.84 | 15.80 | 4.07 | 18.93 |
| MOVER_AVWAP_SCALP | kept | 440 | 82.37 | 65.00 | -17.37 | 20.56 | 16.47 | 15.80 | 4.47 | 3.54 |
| MOVER_TREND_PULLBACK | filtered | 3478 | 57.04 | 64.24 | 7.20 | 20.51 | 18.56 | 15.80 | 4.13 | 18.75 |
| MOVER_TREND_PULLBACK | kept | 10091 | 75.89 | 65.00 | -10.89 | 20.14 | 18.53 | 15.80 | 4.28 | 2.58 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 85.50 | 65.00 | -20.50 | 20.80 | 20.00 | 20.00 | 4.50 | 3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 20 | 61.50 | 65.00 | 3.50 | 21.12 | 19.23 | 20.00 | 0.00 | 12.09 |
| QUIET_COMPRESSION_BREAK | kept | 65 | 72.53 | 65.00 | -7.53 | 20.75 | 19.14 | 20.00 | 0.00 | 2.23 |
| SR_FLIP_RETEST | filtered | 29 | 58.61 | 64.31 | 5.70 | 21.56 | 20.00 | 15.68 | 1.05 | 9.15 |
| SR_FLIP_RETEST | kept | 140 | 69.97 | 65.00 | -4.97 | 21.06 | 20.00 | 15.26 | 1.60 | 1.79 |
| TREND_PULLBACK_EMA | filtered | 116 | 57.45 | 65.00 | 7.55 | 20.44 | 19.80 | 18.32 | 4.88 | 17.09 |
| TREND_PULLBACK_EMA | kept | 241 | 76.56 | 65.00 | -11.56 | 20.88 | 19.94 | 17.71 | 4.97 | 0.28 |
| VOLUME_SURGE_BREAKOUT | filtered | 30 | 57.62 | 64.87 | 7.25 | 19.53 | 16.01 | 20.00 | 3.53 | 7.43 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 342 | 56.45 | 21.49 | 16.04 | 4.10 | 12.18 | 5.86 | 9.24 | 0.59 |
| DIVERGENCE_CONTINUATION | kept | 704 | 70.01 | 22.61 | 17.01 | 4.04 | 12.72 | 5.73 | 9.27 | 0.96 |
| FAILED_AUCTION_RECLAIM | filtered | 22 | 52.78 | 18.09 | 17.45 | 5.86 | 16.05 | 8.43 | 3.80 | 1.30 |
| FUNDING_EXTREME_SIGNAL | filtered | 12 | 45.24 | 24.33 | 13.83 | 3.75 | 12.67 | 6.29 | 2.53 | 4.17 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 81 | 51.85 | 22.23 | 15.53 | 5.00 | 13.09 | 5.73 | 6.43 | 1.69 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 6 | 67.48 | 25.00 | 14.00 | 4.00 | 13.17 | 6.58 | 9.08 | 0.50 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 47.60 | 25.00 | 14.00 | 4.00 | 13.00 | 5.67 | 9.53 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 67.83 | 22.33 | 14.00 | 7.00 | 14.00 | 6.50 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 69 | 59.22 | 20.77 | 15.80 | 8.39 | 13.00 | 5.00 | 7.12 | 0.00 |
| MEAN_REVERT | kept | 7 | 67.37 | 22.71 | 14.57 | 9.00 | 13.00 | 5.00 | 7.59 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 446 | 53.81 | 18.19 | 18.17 | 11.28 | 13.76 | 5.86 | 7.68 | 4.07 |
| MOVER_AVWAP_SCALP | kept | 440 | 82.37 | 19.06 | 18.00 | 13.74 | 13.91 | 7.38 | 9.74 | 4.47 |
| MOVER_TREND_PULLBACK | filtered | 3478 | 57.04 | 18.00 | 18.01 | 7.71 | 12.52 | 5.84 | 9.68 | 4.13 |
| MOVER_TREND_PULLBACK | kept | 10091 | 75.89 | 19.42 | 18.02 | 8.13 | 12.33 | 6.64 | 9.69 | 4.28 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 85.50 | 17.00 | 18.00 | 15.00 | 14.00 | 10.00 | 10.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 20 | 61.50 | 17.00 | 16.20 | 10.95 | 14.00 | 5.47 | 10.00 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 65 | 72.53 | 19.34 | 15.91 | 11.12 | 14.00 | 5.19 | 9.96 | 0.00 |
| SR_FLIP_RETEST | filtered | 29 | 58.61 | 17.28 | 17.31 | 3.62 | 14.52 | 5.24 | 8.74 | 1.05 |
| SR_FLIP_RETEST | kept | 140 | 69.97 | 19.80 | 17.64 | 4.26 | 13.51 | 6.25 | 9.23 | 1.60 |
| TREND_PULLBACK_EMA | filtered | 116 | 57.45 | 13.25 | 18.00 | 7.50 | 14.00 | 7.54 | 9.37 | 4.88 |
| TREND_PULLBACK_EMA | kept | 241 | 76.56 | 17.72 | 18.00 | 7.51 | 14.05 | 7.34 | 8.92 | 4.97 |
| VOLUME_SURGE_BREAKOUT | filtered | 30 | 57.62 | 17.00 | 15.33 | 12.40 | 14.50 | 7.17 | 6.62 | 3.53 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 342 | 56.45 | 0.00 | 0.00 | 2.10 | 0.00 | 1.09 | 0.31 | 0.00 | 0.00 | **3.50** |
| DIVERGENCE_CONTINUATION | kept | 704 | 70.01 | 0.00 | 0.00 | 0.92 | 0.00 | 0.34 | 0.05 | 0.00 | 0.00 | **1.31** |
| FAILED_AUCTION_RECLAIM | filtered | 22 | 52.78 | 0.00 | 0.00 | 0.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.73** |
| FUNDING_EXTREME_SIGNAL | filtered | 12 | 45.24 | 0.00 | 0.00 | 4.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 81 | 51.85 | 0.00 | 0.00 | 1.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.24** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 6 | 67.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 47.60 | 0.00 | 0.00 | 1.60 | 0.00 | 0.00 | 2.00 | 0.00 | 0.00 | **3.60** |
| MA_CROSS_TREND_SHIFT | kept | 3 | 67.83 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 4.00 | 0.00 | 0.00 | **4.00** |
| MEAN_REVERT | filtered | 69 | 59.22 | 0.00 | 0.00 | 0.14 | 0.00 | 1.36 | 0.00 | 0.00 | 0.00 | **1.50** |
| MEAN_REVERT | kept | 7 | 67.37 | 0.00 | 0.00 | 0.69 | 0.00 | 3.09 | 0.00 | 0.00 | 0.00 | **3.78** |
| MOVER_AVWAP_SCALP | filtered | 446 | 53.81 | 2.27 | 0.00 | 1.88 | 0.00 | 3.40 | 0.22 | 0.00 | 1.60 | **9.37** |
| MOVER_AVWAP_SCALP | kept | 440 | 82.37 | 0.03 | 0.00 | 0.41 | 0.00 | 0.81 | 0.24 | 0.00 | 0.01 | **1.50** |
| MOVER_TREND_PULLBACK | filtered | 3478 | 57.04 | 0.92 | 0.00 | 2.32 | 0.00 | 1.64 | 0.76 | 0.00 | 0.01 | **5.65** |
| MOVER_TREND_PULLBACK | kept | 10091 | 75.89 | 0.08 | 0.00 | 0.85 | 0.00 | 0.22 | 0.34 | 0.00 | 0.00 | **1.49** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 85.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 20 | 61.50 | 0.00 | 0.00 | 5.76 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.76** |
| QUIET_COMPRESSION_BREAK | kept | 65 | 72.53 | 0.00 | 0.00 | 0.57 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | **0.61** |
| SR_FLIP_RETEST | filtered | 29 | 58.61 | 0.00 | 0.00 | 0.99 | 0.00 | 1.49 | 0.41 | 0.00 | 0.00 | **2.89** |
| SR_FLIP_RETEST | kept | 140 | 69.97 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.30 | 0.00 | 0.00 | **0.30** |
| TREND_PULLBACK_EMA | filtered | 116 | 57.45 | 0.00 | 0.00 | 1.16 | 0.00 | 1.12 | 0.40 | 0.00 | 0.00 | **2.68** |
| TREND_PULLBACK_EMA | kept | 241 | 76.56 | 0.00 | 0.00 | 0.70 | 0.00 | 0.09 | 0.17 | 0.00 | 0.00 | **0.96** |
| VOLUME_SURGE_BREAKOUT | filtered | 30 | 57.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **190115 held of 868645 seen** across 21 strategies; 4302 cells past the sample floor; **2303 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 48953 | 634/48319/0 | 45% | -0.15 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/QUIET/EXPANDED/BTC_FALLING/MAJOR (-1.26R) |
| MOVER_AVWAP_SCALP | 25486 | 205/25281/0 | 43% | -0.20 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 15024 | 248/14776/0 | 45% | -0.13 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.98R) | LONDON/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 14194 | 151/14043/0 | 36% | -0.32 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 13215 | 77/13138/0 | 39% | -0.27 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 10521 | 103/10418/0 | 37% | -0.42 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9307 | 444/8863/0 | 45% | -0.11 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8274 | 0/0/8274 | 43% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+1.11R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-0.92R) |
| SHADOW_RANGE_FADE | 7781 | 0/0/7781 | 35% | -0.16 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.33R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.39R) |
| SHADOW_FUNDING_FADE | 7305 | 0/0/7305 | 33% | -0.43 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.02R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 6651 | 24/6627/0 | 47% | -0.24 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.30R) |
| MEAN_REVERT | 5648 | 69/5579/0 | 36% | -0.32 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4267 | 2/4265/0 | 31% | -0.46 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.06R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3997 | 0/3997/0 | 28% | -0.41 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| RANGE_FADE | 2552 | 6/2546/0 | 47% | +0.19 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1732 | 0/0/1732 | 52% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.57R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 542 | 0/542/0 | 37% | -0.23 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 228 | 34/194/0 | 45% | -0.16 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 64 | 6/58/0 | 41% | +0.09 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 386 | 27% / -0.57R | 386 | 53% / -0.09R | +0.49 | **ATR** |
| TREND_PULLBACK_EMA | 1334 | 39% / -0.36R | 1334 | 50% / -0.08R | +0.28 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1586 | 42% / -0.37R | 1586 | 57% / -0.12R | +0.25 | **ATR** |
| LIQUIDATION_REVERSAL | 34 | 26% / -0.56R | 34 | 47% / -0.32R | +0.24 | **ATR** |
| SR_FLIP_RETEST | 689 | 47% / -0.26R | 689 | 51% / -0.14R | +0.12 | **ATR** |
| MA_CROSS_TREND_SHIFT | 69 | 46% / -0.15R | 69 | 51% / -0.04R | +0.11 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 226 | 38% / -0.15R | 226 | 48% / -0.04R | +0.11 | **ATR** |
| MOVER_AVWAP_SCALP | 2772 | 46% / -0.14R | 2772 | 52% / -0.04R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1545 | 41% / -0.23R | 1545 | 44% / -0.13R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 9039 | 49% / -0.11R | 9039 | 55% / -0.01R | +0.09 | **ATR** |
| RANGE_FADE | 138 | 41% / +0.03R | 138 | 47% / +0.08R | +0.05 | **ATR** |
| DIVERGENCE_CONTINUATION | 1943 | 48% / -0.11R | 1943 | 53% / -0.05R | +0.05 | **ATR** |
| MEAN_REVERT | 463 | 46% / -0.15R | 463 | 45% / -0.16R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1620 | 48% / -0.11R | 1620 | 48% / -0.11R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 14 | 57% / -0.06R | 14 | 57% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12081 | 28% | -0.25R | 313 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2772 | 50% | -0.03R | 240 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 144 | 49% | -0.04R | 72 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1721 | 34% / -0.19R | +0.87 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1866 | 38% / -0.17R | +0.84 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3319 | 36% / -0.16R | +0.68 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11069 | 37% / -0.13R | +0.40 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2254 | 37% / -0.11R | +0.17 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1570 | 37% / -0.09R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1281 | 32% / -0.28R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 330 | 32% / -0.36R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 500 | 31% / -0.24R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 380 | 48% / -0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 96 | 44% / -0.00R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 602 | 35% / -0.26R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 110 | 31% / -0.32R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 44 | 45% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 25 | 48% / +0.53R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `sar_alignment_crosscheck` — 103/1503 disagreed (6.9%) (streak 39/6) (sustained 39 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 9/6) (sustained 9 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 39/6) (sustained 39 cycles)
- **ALERT** `tuned_variants` — 135 non-stamps — atr_arm_uncomputable=135 (seen=1096 stamped=124 skipped=837) (streak 39/6) (sustained 39 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 5093204 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 6 arms current, none stalled; covering 2025/2025 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 25 arms current, none stalled; covering 1033/1033 signals (100%) | 0 |
| auto_dispatch | ok | 7 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=7. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 282/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 64358.20 | 0 |
| candle_coverage | ok | 87/87 symbols with ≥20 15m candles, 87/87 updated within 45m [fresh=87; 75 Tier-1 futures + 12 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 326 dup bars, 0 undedupable; ws 0 out-of-order, 116 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 61 cohorts, 40 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +108 / upstream +27 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1883/1902 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 16 of 162 open dark rows are not being advanced (worst: HUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 39/120) | 39 |
| dark_sar_arms | ok | no open arms; covering 1844/1863 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 1249351 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 39/6) | 39 |
| emission_controller | ok | last cycle 784s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=88, MOVER_AVWAP_SCALP=272, MOVER_TREND_PULLBACK=5088, RANGE_FADE=158, TREND_PULLBACK_EMA=394), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 2 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 9/6) | 9 |
| firestore_read_budget | ok | 1,332 reads/day of 50,000 [engine 1,311, signing 21]; top site keystore.roster_doc at 290/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +32 / upstream +662 | 0 |
| indicator_cache_key | ok | 4212 frozen value(s) avoided; 98218 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.32R over n=5579 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +23 / upstream +662 | 0 |
| mover_admission_metadata | ok | 946 symbols known, 237 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 12 held, 12 with scan counts, 12 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2123 rows held, 3594439 evicted (sampled: execution:trigger_not_confirmed 283/1266199, execution:overextended 283/1114473, setup_compat:regime_STRONG_TREND 283/619590) | 0 |
| price_action_lane | ok | 143413 evaluated, 110 emitted; layer1 110 stamped / 0 blind; cooldown=19398, delta_opposed=17673, no_footprint=50830, no_sweep=38560, rr_below_floor=16842 | 0 |
| promoted_pair_integrity | ok | 12/12 promoted pairs present in universe | 0 |
| range_fade_emission | ok | emitted_total=0 context_blocked=41 | 0 |
| range_fade_path | ok | output +73 / upstream +662 | 0 |
| sar_alignment_crosscheck | violating | 103/1503 disagreed (6.9%) (streak 39/6) | 39 |
| sar_exit_shadow | ok | output +18 / upstream +662 | 0 |
| sar_hold_arm | ok | 1874 held arms settled, 126 unscored, 23 still walking (19 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 12/89 unfetchable (13%); top cause: located bar does not contain the stamp; symbols: AAVEUSDT, APTUSDT, BERAUSDT, BTWUSDT, DODOXUSDT +7 more | 0 |
| sar_live_arms | ok | 23 arms current, none stalled; covering 1033/1033 signals (100%) | 0 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 489 records await one (77 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| scan_cycle | ok | last 40.29s, worst 102.6s over 1806 lifetime cycles; lifetime 11 over 60s, 0 over 120s (plus 1/0 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 2.74s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 63436 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 33s ago (0.56s to run, worst 89.42s), 72 overrun(s) of 973 cycles, TTL 900s; slowest tickers=10.51s, alerts=2.99s, positions_diag=1.77s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +90 / upstream +662 | 0 |
| structural_snap | ok | 6000/6000 measured, 36 blind, 0 levels moved (refusals: redetect_cooldown=89) | 0 |
| structural_veto_lane | ok | 177 stamped; 0 with no readable level book, 0 with clear air ahead, 111 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +662 / upstream +27 | 0 |
| tuned_variants | violating | 135 non-stamps — atr_arm_uncomputable=135 (seen=1096 stamped=124 skipped=837) (streak 39/6) | 39 |
| unlock_shorts | ok | 18 open, 44 scheduled, calendar 1.7h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 1 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2346526`
- `Path funnel` emissions: `48`
- `Regime distribution` emissions: `48`
- `QUIET_SCALP_BLOCK` events: `286`
- `confidence_gate` events: `16346`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **83**
- Total REST-fallback activations: **9**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 10 | 10062 | 27886 | 41138 | 0 |
| futures_aggtrade | 62 | 9050 | 29111 | 68028 | 0 |
| futures_depth | 3 | 3768 | 3768 | 5368 | 0 |
| futures_liq | 1 | 33734 | 33734 | 33734 | 0 |
| futures_mover | 7 | 11224 | 14161 | 23116 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 9 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=302412] state[populated=302412] buckets[many=302344, some=68] sources[none] quality[none]
- funding_rate: presence[absent=29597, present=272815] state[empty=29597, populated=272815] buckets[few=272815, none=29597] sources[none] quality[none]
- liquidation_clusters: presence[absent=152385, present=150027] state[empty=152385, populated=150027] buckets[few=118171, none=152385, some=31856] sources[none] quality[none]
- oi_snapshot: presence[absent=28975, present=273437] state[empty=28975, populated=273437] buckets[few=104, many=273024, none=28975, some=309] sources[none] quality[none]
- order_book: presence[absent=103405, present=199007] state[populated=199007, unavailable=103405] buckets[few=199007, none=103405] sources[book_ticker=199007, unavailable=103405] quality[none=103405, top_of_book_only=199007]
- orderblocks: presence[absent=302412] state[empty=302412] buckets[none=302412] sources[measured_dark=302412] quality[none]
- recent_ticks: presence[present=302412] state[populated=302412] buckets[many=302412] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.810402035713196` sec
- Median create→first breach: `3713.2972675561905` sec
- Median create→terminal: `3713.2972849607468` sec
- Median first breach→terminal: `6.341934204101562e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.6}, "under_180s": {"count": 1, "pct": 2.6}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.6}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.6}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 10 | 10 | 1.016750566064404 | 1.8550427674233332 | 0.6828762467615838 | 0 | 10 |
| MOVER_AVWAP_SCALP | 1 | 1 | 4.2838577575510435 | 3.0 | 1.427952585850348 | 1 | 0 |
| MOVER_TREND_PULLBACK | 21 | 21 | 5.227070502717983 | 3.0 | 1.7423568342393276 | 16 | 4 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 1 | 1.642343301809087 | 2.0073698568781944 | 0.8181568016385448 | 0 | 1 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 1.1340378011290584 | 1.1904327958400138 | 1.0000000002765654 | 0 | 1 |
| TREND_PULLBACK_EMA | 1 | 1 | 2.191109296278999 | 2.438916279672402 | 0.8983946331168495 | 0 | 1 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 10 | 2.638478648040163 | 2.638478648040163 | 1 | 0 | 0 | 1 | 0 | 8 |
| MOVER_AVWAP_SCALP | 1 | 4.283857264231099 | 3.9499199999999837 | 0 | 0 | 0 | 1 | 0 | 0 |
| MOVER_TREND_PULLBACK | 21 | 8.571263139141283 | 5.864439291736918 | 3 | 0 | 0 | 18 | 1 | 0 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 4.291272613671851 | 2.4635142427082384 | 0 | 0 | 0 | 1 | 0 | 0 |
| QUIET_COMPRESSION_BREAK | 4 | 3.0306322186262613 | 2.7967863109512403 | 0 | 0 | 0 | 1 | 0 | 3 |
| TREND_PULLBACK_EMA | 1 | 4.237183211268683 | 3.2866639364819363 | 0 | 0 | 0 | 1 | 0 | 0 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 10 | 10 | 10.0 | 30.0 | 10.0 | 0.0 | 0.4419 | 3720.1051495075226 | 3721.6653180122375 |
| MOVER_AVWAP_SCALP | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.9499 | 2489.9412200450897 | 2490.513599872589 |
| MOVER_TREND_PULLBACK | 21 | 21 | 14.3 | 57.1 | 14.3 | 0.0 | -1.267 | 2309.209692955017 | 2309.2097461223602 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 10891.047228097916 | 10891.047284126282 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 100.0 | 0.0 | 100.0 | 0.0 | 2.8541 | 14223.35802102089 | 14224.787747979164 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.1911 | 3756.6785700321198 | 3756.678586959839 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 398 | 5 | 135 | 0.0 | 0.0 | None | None | 263 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2137 | 54 | 1538 | 0.0 | 100.0 | 3756.6785700321198 | 3756.678586959839 | 599 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `645`
- Gating Δ: `16291`
- No-generation Δ: `63131`
- Fast failures Δ: `1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.2075, "current_avg_pnl": 0.4419, "current_win_rate": 10.0, "previous_avg_pnl": 0.2344, "previous_win_rate": 50.0, "win_rate_delta": -40.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.8111, "current_avg_pnl": -1.267, "current_win_rate": 14.3, "previous_avg_pnl": 0.5441, "previous_win_rate": 34.4, "win_rate_delta": -20.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 2.295, "current_avg_pnl": 2.8541, "current_win_rate": 100.0, "previous_avg_pnl": 0.5591, "previous_win_rate": 25.0, "win_rate_delta": 75.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": 16, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -6, "geometry_changed_delta": 0, "geometry_preserved_delta": 12, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -6246.54, "median_terminal_delta_sec": -6246.54, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **QUIET_COMPRESSION_BREAK**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
