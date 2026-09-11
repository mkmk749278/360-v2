# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM
- Recommended next investigation target: **MOVER_AVWAP_SCALP**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `688` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 106 | 106 | 79 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 20194 | 20194 | 19061 | 11 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 90822 | 90824 | 29 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 73358 | 73360 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 72841 | 68066 | 5275 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 73386 | 72208 | 1250 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 74192 | 74155 | 54 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 64288 | 64297 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 73459 | 73506 | 3 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 73516 | 71011 | 3473 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 96891 | 101093 | 1412 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 90857 | 78029 | 18804 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 73845 | 73847 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 73369 | 73384 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 72809 | 72563 | 278 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 74487 | 73455 | 1342 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 72443 | 72545 | 240 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 63102 | 59888 | 3449 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 63343 | 62677 | 743 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 90775 | 90786 | 30 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 64299 | 64195 | 162 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4993 | 4993 | 4185 | 6 | active-healthy (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 440 | 440 | 267 | 1 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15712 | 15712 | 15462 | 14 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 4 | 4 | 3 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8878 | 8878 | 8243 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3359 | 3359 | 2550 | 41 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 49979 | 49979 | 39954 | 375 | active-healthy (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1575 | 1575 | 1394 | 14 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3241 | 3241 | 3015 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 864 | 864 | 716 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2767 | 2767 | 2428 | 22 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 155 | 155 | 27 | 2 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 8308 | 8308 | 2475 | 4 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=90824): breakout_not_found=48021, basic_filters_failed=22955, move_not_fresh=12567, breakout_stale=5491, retest_proximity_failed=1447, volume_spike_missing=334, missing_fvg_or_orderblock=9
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=73360): cls_disabled_merged_into_lsr=73360
- **EVAL::DIVERGENCE_CONTINUATION** (total=68066): cvd_divergence_failed=33860, basic_filters_failed=16238, h1_trend_not_aligned=9091, ema_alignment_reject=7766, retest_proximity_failed=627, missing_fvg_or_orderblock=481, missing_cvd=3
- **EVAL::FAILED_AUCTION_RECLAIM** (total=72208): auction_not_detected=47079, basic_filters_failed=15743, reclaim_hold_failed=4518, tail_too_small=2893, regime_blocked=1949, rsi_reject=26
- **EVAL::FUNDING_EXTREME** (total=74155): funding_not_extreme=52785, basic_filters_failed=14877, missing_funding_rate=5471, ema_alignment_reject=713, rsi_reject=165, momentum_reject=79, cvd_divergence_failed=62, missing_fvg_or_orderblock=3
- **EVAL::LIQUIDATION_REVERSAL** (total=64297): cascade_threshold_not_met=47384, basic_filters_failed=16390, cvd_divergence_failed=286, rsi_reject=224, missing_fvg_or_orderblock=7, volume_spike_missing=6
- **EVAL::MA_CROSS_TREND_SHIFT** (total=73506): no_ma_cross=56539, basic_filters_failed=16261, ma_cross_htf_misaligned=455, ma_cross_cooldown=251
- **EVAL::MEAN_REVERT** (total=71011): no_extension=59175, basic_filters_failed=11836
- **EVAL::MOVER_AVWAP_SCALP** (total=101093): no_avwap_tag=39922, no_mover_leg=27153, basic_filters_failed=23160, avwap_slope_against=6661, avwap_reclaim_no_volume=2643, no_avwap_reclaim=1554
- **EVAL::MOVER_TREND_PULLBACK** (total=78029): mover_run_too_small=30492, basic_filters_failed=23056, no_reclaim=21693, no_pullback_tag=2788
- **EVAL::OPENING_RANGE_BREAKOUT** (total=73847): feature_disabled=73847
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=73384): regime_blocked=52561, breakout_not_found=14811, basic_filters_failed=3651, adx_reject=2297, ema_alignment_reject=64
- **EVAL::QUIET_COMPRESSION_BREAK** (total=72563): compression_not_detected=32357, regime_blocked=22649, basic_filters_failed=12076, breakout_not_detected=4940, volume_confirmation_failed=488, rsi_reject=51, missing_fvg_or_orderblock=2
- **EVAL::RANGE_FADE** (total=73455): no_range_edge=61612, basic_filters_failed=11843
- **EVAL::SR_FLIP_RETEST** (total=72545): flip_close_not_confirmed=47635, basic_filters_failed=15714, long_break_volume_thin=2458, retest_out_of_zone=2186, regime_blocked=1931, h1_break_not_confirmed=1396, reclaim_hold_failed=790, ema_alignment_reject=255, long_acceptance_not_held=92, whipsaw_flip=51, wick_quality_failed=33, missing_fvg_or_orderblock=4
- **EVAL::STANDARD** (total=59888): adx_reject=18377, momentum_reject=15572, basic_filters_failed=8275, macd_reject=6287, sweeps_not_detected=6017, ema_alignment_reject=3623, htf_poi_unanchored=1660, rsi_reject=60, invalid_sl_geometry=12, mtf_reject=5
- **EVAL::TREND_PULLBACK** (total=62677): h1_pullback_not_confirmed=15016, ema_alignment_reject=10260, h1_trend_not_aligned=10212, basic_filters_failed=8980, no_ema_reclaim_close=5468, ema_not_tested_prev=4802, body_conviction_fail=3022, rsi_reject=2575, prev_already_below_emas=1069, no_prev_low_break=862, momentum_flat=201, prev_already_above_emas=68, missing_fvg_or_orderblock=67, ema21_not_tagged=47, no_prev_high_break=21, momentum_reject=7
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=90786): breakout_not_found=56577, basic_filters_failed=22950, move_not_fresh=6043, breakout_stale=3666, retest_proximity_failed=1247, volume_spike_missing=281, missing_fvg_or_orderblock=18, move_exhausted=4
- **EVAL::WHALE_MOMENTUM** (total=64195): momentum_reject=49627, recent_ticks_insufficient=11838, basic_filters_failed=2730

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=304): setup_compat:regime_VOLATILE_UNSUITABLE=254, setup_compat:regime_BREAKOUT_EXPANSION=31, execution:overextended=19
- **FAILED_AUCTION_RECLAIM** (total=1466): execution:overextended=700, setup_compat:regime_STRONG_TREND=667, context_floor=99
- **FUNDING_EXTREME_SIGNAL** (total=348): execution:trigger_not_confirmed=348
- **LIQUIDITY_SWEEP_REVERSAL** (total=3825): execution:trigger_not_confirmed=1424, setup_compat:regime_STRONG_TREND=1316, execution:overextended=1085
- **MA_CROSS_TREND_SHIFT** (total=3): execution:overextended=1, setup_compat:regime_DIRTY_RANGE=1, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=5059): setup_compat:regime_WEAK_TREND=2467, setup_compat:regime_STRONG_TREND=2265, execution:overextended=327
- **MOVER_AVWAP_SCALP** (total=1292): execution:overextended=1042, execution:trigger_not_confirmed=165, entry_quality=85
- **MOVER_TREND_PULLBACK** (total=17267): execution:trigger_not_confirmed=11001, execution:overextended=4852, entry_quality=1414
- **RANGE_FADE** (total=2202): setup_compat:regime_STRONG_TREND=917, setup_compat:regime_WEAK_TREND=871, setup_compat:regime_VOLATILE_UNSUITABLE=222, execution:overextended=180, setup_compat:regime_BREAKOUT_EXPANSION=12
- **TREND_PULLBACK_EMA** (total=2296): setup_compat:regime_CLEAN_RANGE=1546, setup_compat:regime_DIRTY_RANGE=624, setup_compat:regime_VOLATILE_UNSUITABLE=82, entry_quality=44
- **VOLUME_SURGE_BREAKOUT** (total=5): execution:overextended=5
- **WHALE_MOMENTUM** (total=7372): execution:trigger_not_confirmed=7356, context_floor=15, execution:overextended=1

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 190809 | 41.0% |
| QUIET | 98868 | 21.3% |
| TRENDING_DOWN | 98447 | 21.2% |
| TRENDING_UP | 57694 | 12.4% |
| VOLATILE | 19378 | 4.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **301**
- Average confidence gap to threshold: **19.01** (samples=301) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ETHUSDT=79, LINKUSDT=31, BTCUSDT=31, DOTUSDT=30, BNBUSDT=12, REZUSDT=11, ADAUSDT=10, AVAXUSDT=10, ARBUSDT=9, SOLUSDT=9

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 12 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 15 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 235 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 8 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 173 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 106 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 55 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 32 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 47 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 4 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 77 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 24 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 12 |
| MEAN_REVERT | filtered | min_confidence | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 374 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 8 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 7 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 207 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1425 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 45 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2878 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 63 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 23 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 39 |
| SR_FLIP_RETEST | filtered | min_confidence | 24 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 3 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 9 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 53 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 9 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 111 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 110 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 18 |
| WHALE_MOMENTUM | filtered | min_confidence | 275 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 99 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 17 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 12 | 57.30 | 63.00 | 5.70 | 19.05 | 16.20 | 20.00 | 4.00 | 19.70 |
| BREAKDOWN_SHORT | kept | 15 | 73.93 | 65.00 | -8.93 | 19.31 | 18.40 | 20.00 | 4.23 | 2.00 |
| DIVERGENCE_CONTINUATION | filtered | 243 | 55.44 | 64.61 | 9.17 | 21.04 | 19.68 | 17.37 | 0.74 | 14.07 |
| DIVERGENCE_CONTINUATION | kept | 173 | 68.75 | 65.00 | -3.75 | 20.55 | 19.68 | 17.98 | 1.70 | 3.03 |
| FAILED_AUCTION_RECLAIM | filtered | 161 | 45.47 | 63.01 | 17.54 | 20.78 | 19.74 | 20.00 | 2.50 | 14.49 |
| FAILED_AUCTION_RECLAIM | kept | 32 | 64.18 | 65.00 | 0.82 | 20.08 | 19.82 | 20.00 | 2.77 | 0.51 |
| FUNDING_EXTREME_SIGNAL | filtered | 47 | 50.43 | 62.96 | 12.53 | 19.35 | 15.30 | 17.88 | 2.96 | 5.72 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 73.47 | 65.00 | -8.47 | 20.70 | 15.27 | 17.00 | 2.75 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 77 | 49.20 | 64.01 | 14.81 | 19.66 | 18.49 | 17.51 | 2.49 | 20.36 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 24 | 71.34 | 65.00 | -6.34 | 20.84 | 19.64 | 17.55 | 2.21 | 1.44 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 70.30 | 65.00 | -5.30 | 20.20 | 20.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 13 | 53.22 | 64.69 | 11.47 | 21.33 | 18.95 | 14.73 | 0.00 | 13.35 |
| MEAN_REVERT | kept | 1 | 70.50 | 65.00 | -5.50 | 19.40 | 18.70 | 15.30 | 0.00 | 3.20 |
| MOVER_AVWAP_SCALP | filtered | 389 | 55.80 | 62.70 | 6.90 | 20.27 | 14.61 | 15.80 | 3.53 | 11.35 |
| MOVER_AVWAP_SCALP | kept | 207 | 79.27 | 65.00 | -14.27 | 20.18 | 15.78 | 15.80 | 4.34 | 5.69 |
| MOVER_TREND_PULLBACK | filtered | 1470 | 55.52 | 64.35 | 8.83 | 20.43 | 18.40 | 15.80 | 3.81 | 15.40 |
| MOVER_TREND_PULLBACK | kept | 2878 | 75.94 | 65.00 | -10.94 | 20.18 | 18.82 | 15.80 | 3.97 | 1.60 |
| QUIET_COMPRESSION_BREAK | filtered | 86 | 45.56 | 64.81 | 19.25 | 21.22 | 19.43 | 20.00 | 0.00 | 13.06 |
| QUIET_COMPRESSION_BREAK | kept | 39 | 72.36 | 65.00 | -7.36 | 20.89 | 17.52 | 20.00 | 0.00 | -0.23 |
| SR_FLIP_RETEST | filtered | 27 | 50.06 | 60.56 | 10.50 | 21.23 | 20.00 | 15.20 | 1.94 | 20.51 |
| SR_FLIP_RETEST | kept | 9 | 66.99 | 65.00 | -1.99 | 19.41 | 20.00 | 19.27 | 1.50 | 4.44 |
| TREND_PULLBACK_EMA | filtered | 62 | 53.06 | 64.11 | 11.05 | 21.83 | 19.83 | 19.29 | 4.73 | 22.00 |
| TREND_PULLBACK_EMA | kept | 111 | 79.54 | 65.00 | -14.54 | 20.90 | 19.59 | 18.31 | 4.88 | -0.55 |
| VOLUME_SURGE_BREAKOUT | filtered | 110 | 47.91 | 63.58 | 15.67 | 20.91 | 17.82 | 20.00 | 5.00 | 16.37 |
| VOLUME_SURGE_BREAKOUT | kept | 18 | 77.06 | 65.00 | -12.06 | 20.43 | 17.34 | 20.00 | 5.22 | 4.10 |
| WHALE_MOMENTUM | filtered | 374 | 47.58 | 64.81 | 17.23 | 23.77 | 14.95 | 17.00 | 0.00 | 17.17 |
| WHALE_MOMENTUM | kept | 17 | 65.20 | 65.00 | -0.20 | 23.16 | 17.18 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 12 | 57.30 | 17.00 | 14.00 | 15.00 | 14.00 | 5.00 | 8.00 | 4.00 |
| BREAKDOWN_SHORT | kept | 15 | 73.93 | 17.00 | 15.87 | 12.00 | 12.80 | 4.83 | 9.20 | 4.23 |
| DIVERGENCE_CONTINUATION | filtered | 243 | 55.44 | 23.26 | 15.49 | 4.33 | 12.16 | 4.92 | 8.61 | 0.74 |
| DIVERGENCE_CONTINUATION | kept | 173 | 68.75 | 24.17 | 15.46 | 5.41 | 11.31 | 5.16 | 8.98 | 1.70 |
| FAILED_AUCTION_RECLAIM | filtered | 161 | 45.47 | 22.14 | 15.99 | 7.55 | 13.55 | 6.10 | 5.00 | 2.50 |
| FAILED_AUCTION_RECLAIM | kept | 32 | 64.18 | 24.00 | 17.62 | 5.72 | 16.16 | 6.41 | 4.30 | 2.77 |
| FUNDING_EXTREME_SIGNAL | filtered | 47 | 50.43 | 21.94 | 15.23 | 5.94 | 12.98 | 7.07 | 5.03 | 2.96 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 73.47 | 13.25 | 18.50 | 9.00 | 12.50 | 8.75 | 8.73 | 2.75 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 77 | 49.20 | 24.27 | 14.26 | 5.49 | 12.12 | 6.45 | 4.47 | 2.49 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 24 | 71.34 | 24.25 | 14.67 | 5.62 | 12.33 | 5.92 | 7.90 | 2.21 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 70.30 | 25.00 | 14.00 | 3.00 | 14.00 | 5.00 | 9.30 | 0.00 |
| MEAN_REVERT | filtered | 13 | 53.22 | 24.38 | 17.69 | 8.31 | 12.92 | 5.00 | 5.18 | 0.00 |
| MEAN_REVERT | kept | 1 | 70.50 | 25.00 | 14.00 | 9.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 389 | 55.80 | 18.74 | 18.04 | 12.30 | 13.46 | 7.28 | 5.18 | 3.53 |
| MOVER_AVWAP_SCALP | kept | 207 | 79.27 | 20.85 | 18.00 | 12.95 | 13.70 | 7.57 | 8.81 | 4.34 |
| MOVER_TREND_PULLBACK | filtered | 1470 | 55.52 | 18.07 | 18.06 | 7.60 | 12.36 | 6.38 | 8.32 | 3.81 |
| MOVER_TREND_PULLBACK | kept | 2878 | 75.94 | 19.18 | 18.04 | 7.98 | 12.72 | 6.64 | 9.10 | 3.97 |
| QUIET_COMPRESSION_BREAK | filtered | 86 | 45.56 | 18.21 | 16.93 | 12.31 | 14.24 | 6.95 | 3.60 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 39 | 72.36 | 18.23 | 14.92 | 10.92 | 14.00 | 5.29 | 9.71 | 0.00 |
| SR_FLIP_RETEST | filtered | 27 | 50.06 | 20.85 | 16.89 | 6.00 | 11.33 | 5.33 | 8.22 | 1.94 |
| SR_FLIP_RETEST | kept | 9 | 66.99 | 19.67 | 18.00 | 8.33 | 10.44 | 5.00 | 8.49 | 1.50 |
| TREND_PULLBACK_EMA | filtered | 62 | 53.06 | 14.06 | 18.00 | 7.79 | 13.39 | 7.52 | 9.56 | 4.73 |
| TREND_PULLBACK_EMA | kept | 111 | 79.54 | 19.70 | 18.00 | 7.51 | 14.19 | 6.59 | 9.07 | 4.88 |
| VOLUME_SURGE_BREAKOUT | filtered | 110 | 47.91 | 21.44 | 16.69 | 12.25 | 11.65 | 5.00 | 7.26 | 5.00 |
| VOLUME_SURGE_BREAKOUT | kept | 18 | 77.06 | 23.22 | 15.78 | 12.00 | 12.00 | 5.28 | 9.39 | 5.22 |
| WHALE_MOMENTUM | filtered | 374 | 47.58 | 22.12 | 14.82 | 6.47 | 13.29 | 6.55 | 5.42 | 0.00 |
| WHALE_MOMENTUM | kept | 17 | 65.20 | 24.41 | 17.41 | 5.29 | 13.88 | 7.97 | 6.23 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 12 | 57.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 15 | 73.93 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 243 | 55.44 | 0.00 | 0.00 | 0.28 | 0.00 | 0.68 | 0.21 | 0.00 | 0.00 | **1.17** |
| DIVERGENCE_CONTINUATION | kept | 173 | 68.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.62 | 0.00 | 0.00 | 0.00 | **0.62** |
| FAILED_AUCTION_RECLAIM | filtered | 161 | 45.47 | 0.00 | 0.00 | 0.00 | 0.00 | 1.95 | 0.20 | 0.00 | 0.00 | **2.15** |
| FAILED_AUCTION_RECLAIM | kept | 32 | 64.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.23 | 0.19 | 0.00 | 0.00 | **0.42** |
| FUNDING_EXTREME_SIGNAL | filtered | 47 | 50.43 | 0.00 | 0.00 | 4.34 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.34** |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 73.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 77 | 49.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.39 | 0.00 | 0.00 | **0.39** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 24 | 71.34 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 70.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 13 | 53.22 | 0.00 | 0.00 | 0.00 | 0.00 | 11.63 | 0.00 | 0.00 | 0.00 | **11.63** |
| MEAN_REVERT | kept | 1 | 70.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 389 | 55.80 | 0.00 | 0.00 | 0.02 | 0.00 | 3.07 | 0.03 | 0.00 | 0.91 | **4.03** |
| MOVER_AVWAP_SCALP | kept | 207 | 79.27 | 0.19 | 0.00 | 0.00 | 0.00 | 0.42 | 0.43 | 0.00 | 0.08 | **1.12** |
| MOVER_TREND_PULLBACK | filtered | 1470 | 55.52 | 1.32 | 0.00 | 0.73 | 0.00 | 0.78 | 0.43 | 0.00 | 0.01 | **3.27** |
| MOVER_TREND_PULLBACK | kept | 2878 | 75.94 | 0.01 | 0.00 | 0.48 | 0.00 | 0.25 | 0.13 | 0.00 | 0.00 | **0.87** |
| QUIET_COMPRESSION_BREAK | filtered | 86 | 45.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.35 | 1.88 | 0.00 | 5.25 | **7.48** |
| QUIET_COMPRESSION_BREAK | kept | 39 | 72.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.56 | 0.26 | 0.00 | 0.00 | **0.82** |
| SR_FLIP_RETEST | filtered | 27 | 50.06 | 0.00 | 0.00 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | **2.40** |
| SR_FLIP_RETEST | kept | 9 | 66.99 | 0.00 | 0.00 | 7.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **7.11** |
| TREND_PULLBACK_EMA | filtered | 62 | 53.06 | 0.00 | 0.00 | 1.16 | 0.00 | 2.48 | 1.16 | 0.00 | 0.00 | **4.80** |
| TREND_PULLBACK_EMA | kept | 111 | 79.54 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.14** |
| VOLUME_SURGE_BREAKOUT | filtered | 110 | 47.91 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.65 | **0.65** |
| VOLUME_SURGE_BREAKOUT | kept | 18 | 77.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.20 | **0.20** |
| WHALE_MOMENTUM | filtered | 374 | 47.58 | 0.00 | 0.00 | 0.00 | 0.00 | 2.71 | 0.14 | 0.00 | 0.00 | **2.85** |
| WHALE_MOMENTUM | kept | 17 | 65.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **88666 held of 211902 seen** across 21 strategies; 1984 cells past the sample floor; **857 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 34542 | 420/34122/0 | 45% | -0.14 | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_FALLING/MAJOR (+1.18R) | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.17R) |
| MOVER_AVWAP_SCALP | 10959 | 132/10827/0 | 40% | -0.27 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 6674 | 74/6600/0 | 41% | -0.19 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 5278 | 26/5252/0 | 56% | +0.10 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | OVERLAP/MARKDOWN/CASCADE/BTC_RISING (-1.17R) |
| SHADOW_MEAN_REVERT | 4772 | 0/0/4772 | 44% | -0.07 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.41R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.09R) |
| TREND_PULLBACK_EMA | 4361 | 18/4343/0 | 47% | -0.14 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.20R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.28R) |
| QUIET_COMPRESSION_BREAK | 4019 | 175/3844/0 | 47% | -0.11 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+0.86R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_RANGE_FADE | 3953 | 0/0/3953 | 37% | -0.07 | ASIA/MARKDOWN/EXPANDED/BTC_FALLING (+0.46R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.03R) |
| SHADOW_FUNDING_FADE | 3202 | 0/0/3202 | 36% | -0.39 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-1.01R) |
| WHALE_MOMENTUM | 2754 | 2/2752/0 | 41% | -0.36 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 2263 | 30/2233/0 | 38% | -0.28 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.21R) |
| MEAN_REVERT | 1349 | 20/1329/0 | 61% | +0.12 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| VOLUME_SURGE_BREAKOUT | 1138 | 0/1138/0 | 42% | -0.13 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 1088 | 2/1086/0 | 31% | -0.45 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.37R) |
| SR_FLIP_RETEST | 874 | 2/872/0 | 43% | -0.31 | NY/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.77R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 557 | 0/0/557 | 56% | +0.01 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | ASIA/MARKUP/CASCADE/BTC_NEUTRAL (-0.33R) |
| BREAKDOWN_SHORT | 335 | 22/313/0 | 41% | -0.14 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.03R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| RANGE_FADE | 300 | 0/300/0 | 59% | +0.19 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| LIQUIDATION_REVERSAL | 196 | 0/196/0 | 11% | -1.00 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 48 | 6/42/0 | 33% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 4 | 0/4/0 | 50% | +0.17 | — | — |

- **Strongest cells**: `DIVERGENCE_CONTINUATION @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +1.76R (n=34, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +1.66R (n=15, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ NY/RANGE/NORMAL/BTC_FALLING` +1.64R (n=19, STRONG)
- **Weakest cells**: `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING` -1.38R (n=17, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.37R (n=16, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 106 | 33% / -0.42R | 106 | 48% / -0.16R | +0.27 | **ATR** |
| TREND_PULLBACK_EMA | 361 | 47% / -0.19R | 361 | 56% / -0.03R | +0.16 | **ATR** |
| SR_FLIP_RETEST | 101 | 47% / -0.31R | 101 | 49% / -0.18R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 311 | 43% / -0.33R | 311 | 46% / -0.21R | +0.12 | **ATR** |
| RANGE_FADE | 20 | 50% / +0.20R | 20 | 50% / +0.10R | -0.11 | **FIXED** |
| MOVER_AVWAP_SCALP | 828 | 45% / -0.19R | 828 | 50% / -0.09R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 568 | 42% / -0.20R | 568 | 45% / -0.10R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 5220 | 51% / -0.09R | 5220 | 55% / -0.01R | +0.09 | **ATR** |
| MA_CROSS_TREND_SHIFT | 16 | 31% / -0.25R | 16 | 31% / -0.19R | +0.06 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 72 | 43% / -0.08R | 72 | 50% / -0.02R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 456 | 52% / -0.18R | 456 | 56% / -0.15R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 664 | 47% / -0.14R | 664 | 47% / -0.15R | -0.01 | **FIXED** |
| MEAN_REVERT | 111 | 59% / +0.05R | 111 | 56% / +0.05R | -0.00 | **FIXED** |
| BREAKDOWN_SHORT | 24 | 33% / -0.11R | 24 | 33% / -0.11R | +0.00 | **ATR** |
| DIVERGENCE_CONTINUATION | 532 | 53% / -0.01R | 532 | 59% / -0.01R | +0.00 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 13 | 31% / -0.46R | 13 | 54% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 7663 | 31% | -0.16R | 300 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 828 | 48% | -0.08R | 182 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 46 | 54% | -0.04R | 38 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 117 | 32% / -0.38R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 632 | 37% / -0.08R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 6664 | 37% / -0.11R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1027 | 36% / -0.08R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 450 | 36% / -0.11R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 595 | 42% / +0.10R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 480 | 37% / -0.06R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 452 | 45% / -0.09R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 98 | 28% / -0.50R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 129 | 30% / -0.64R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 90 | 53% / +0.06R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 45 | 40% / -0.11R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 18 | 44% / +0.28R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 102 | 32% / -0.42R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 22 | 14% / -0.66R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 17 | 41% / -0.06R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 8 | 38% / -0.01R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **7** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×230]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 179/6) (sustained 179 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 22/6) (sustained 22 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.42R (bound 0.3) (streak 179/6) (sustained 179 cycles)
- **ALERT** `range_fade_emission` — 2634 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=300, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 179/6) (sustained 179 cycles)
- **ALERT** `tuned_variants` — 212 non-stamps — atr_arm_uncomputable=212 (seen=3721 stamped=524 skipped=2985) (streak 179/6) (sustained 179 cycles)
- **ALERT** `auto_dispatch` — 35 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=70) (streak 169/3) (sustained 169 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 179/3) (sustained 179 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 17384346 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 179/3) | 179 |
| ai_governor_live_arms | ok | 26 arms current, none stalled; covering 107/107 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 56 arms current, none stalled; covering 870/870 signals (100%) | 0 |
| auto_dispatch | violating | 35 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=70) (streak 169/3) | 169 |
| btc_reference | ok | BTC ref 77076.50 | 0 |
| candle_coverage | ok | 92/92 symbols with ≥20 15m candles, 92/92 updated within 45m [fresh=92; 75 Tier-1 futures + 17 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 476 dup bars, 0 undedupable; ws 0 out-of-order, 92 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 6 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +57 / upstream +25 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1504/1521 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 4 promoted today, nothing refused | 0 |
| dark_resolution | violating | 15 of 153 open dark rows are not being advanced (worst: XVGUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 73/120) | 73 |
| dark_sar_arms | ok | no open arms; covering 1498/1515 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 4805154 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.42R (bound 0.3) (streak 179/6) | 179 |
| emission_controller | ok | last cycle 4s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×230]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 179/6) | 179 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 22/6) | 22 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +8 / upstream +231 | 0 |
| indicator_cache_key | ok | 53410 frozen value(s) avoided; 191733 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 152 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure +0.11R over n=1329, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 3/6) | 3 |
| mean_revert_path | ok | output +38 / upstream +231 | 0 |
| mover_admission_metadata | ok | 897 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 17 held, 17 with scan counts, 17 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2957 rows held, 1272039 evicted (sampled: execution:trigger_not_confirmed 400/465438, execution:overextended 400/428613, setup_compat:regime_STRONG_TREND 400/185340) | 0 |
| price_action_lane | ok | 337111 evaluated, 468 emitted; layer1 468 stamped / 0 blind; cooldown=43850, delta_opposed=27645, no_footprint=130651, no_opposing_target=399, no_sweep=107756, rr_below_floor=26342 | 0 |
| promoted_pair_integrity | ok | 17/17 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 2634 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=300, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 179/6) | 179 |
| range_fade_path | ok | output +24 / upstream +231 | 0 |
| sar_alignment_crosscheck | ok | 570/13040 disagreed (4.4%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +231 | 0 |
| sar_hold_arm | ok | 1498 held arms settled, 205 unscored, 55 still walking (47 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 62/62 resolvable | 0 |
| sar_live_arms | ok | 56 arms current, none stalled; covering 879/879 signals (100%) | 0 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 4 resolved, 58 still mid-window | 0 |
| scan_cycle | ok | last 28.14s, worst 130.85s over 3730 lifetime cycles; lifetime 35 over 60s, 1 over 120s (plus 1/0 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 1.71s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 200875 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 4m ago | 0 |
| snapshot_writer | ok | last cycle 16s ago (5.22s to run, worst 87.09s), 366 overrun(s) of 3774 cycles, TTL 900s; slowest signals=0.74s, data_intake=0.66s, agents=0.23s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=1, gate reads=0, withheld=1) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +13 / upstream +231 | 0 |
| structural_snap | ok | 4897/4897 measured, 16 blind, 0 levels moved (refusals: redetect_cooldown=413) | 0 |
| structural_veto_lane | ok | 869 stamped; 0 with no readable level book, 69 with clear air ahead, 652 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +231 / upstream +25 | 0 |
| tuned_variants | violating | 212 non-stamps — atr_arm_uncomputable=212 (seen=3721 stamped=524 skipped=2985) (streak 179/6) | 179 |

Fail-open exception counters (nonzero sites):
- `feature_liveness.probe.footprint_bars`: 1 — last: RuntimeError: deque mutated during iteration

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2362049`
- `Path funnel` emissions: `50`
- `Regime distribution` emissions: `50`
- `QUIET_SCALP_BLOCK` events: `301`
- `confidence_gate` events: `6600`
- `free_channel_post` events: `48`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **7**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 2 | 2526 | 2526 | 2770 | 0 |
| futures_aggtrade | 1 | 9043 | 9043 | 9043 | 0 |
| futures_depth | 1 | 2829 | 2829 | 2829 | 0 |
| futures_liq | 2 | 1983 | 1983 | 10545 | 0 |
| futures_mover | 1 | 2309 | 2309 | 2309 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **48**

| Source | Count |
|---|---:|
| signal_close | 44 |
| regime_shift | 4 |

- By severity: HIGH=48

## Dependency readiness
- cvd: presence[absent=19, present=367409] state[empty=19, populated=367409] buckets[many=367409, none=19] sources[none] quality[none]
- funding_rate: presence[absent=73493, present=293935] state[empty=73493, populated=293935] buckets[few=293935, none=73493] sources[none] quality[none]
- liquidation_clusters: presence[absent=225428, present=142000] state[empty=225428, populated=142000] buckets[few=113995, none=225428, some=28005] sources[none] quality[none]
- oi_snapshot: presence[absent=72018, present=295410] state[empty=72018, populated=295410] buckets[many=295410, none=72018] sources[none] quality[none]
- order_book: presence[absent=121580, present=245848] state[populated=245848, unavailable=121580] buckets[few=245848, none=121580] sources[book_ticker=245848, unavailable=121580] quality[none=121580, top_of_book_only=245848]
- orderblocks: presence[absent=367428] state[empty=367428] buckets[none=367428] sources[measured_dark=367428] quality[none]
- recent_ticks: presence[present=367428] state[populated=367428] buckets[many=367428] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.6519575119018555` sec
- Median create→first breach: `4180.24575483799` sec
- Median create→terminal: `4182.176450848579` sec
- Median first breach→terminal: `2.4535374641418457` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 1, "pct": 2.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.3}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 2.1298713382613075 | 2.235791947110598 | 0.9431732399306314 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 4 | 4 | 1.1519421491497437 | 1.5949263075158278 | 0.8740166253957953 | 0 | 4 |
| MOVER_AVWAP_SCALP | 8 | 8 | 2.209687433112372 | 2.6291858845104397 | 0.837231785759899 | 1 | 7 |
| MOVER_TREND_PULLBACK | 22 | 22 | 5.046233059702711 | 3.0 | 1.7575696076285952 | 19 | 3 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 1.2224867079598427 | 1.448856641604017 | 0.9112489159813429 | 0 | 5 |
| TREND_PULLBACK_EMA | 1 | 1 | 2.6417491505392325 | 3.0 | 0.8805830501797441 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -0.6736 | 16912.235574007034 | 16915.07847893238 |
| FAILED_AUCTION_RECLAIM | 4 | 4 | 75.0 | 25.0 | 75.0 | 0.0 | 1.5362 | 12090.279914021492 | 12093.852326869965 |
| MOVER_AVWAP_SCALP | 8 | 8 | 12.5 | 75.0 | 12.5 | 0.0 | -1.1857 | 8192.42585504055 | 8195.568412065506 |
| MOVER_TREND_PULLBACK | 22 | 22 | 45.5 | 31.8 | 45.5 | 0.0 | 0.876 | 1776.7131029367447 | 1778.990378499031 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 28.6 | 42.9 | 28.6 | 0.0 | -0.273 | 18755.9022500515 | 18756.832131147385 |
| TREND_PULLBACK_EMA | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.9626 | 7640.726030111313 | 7642.349580049515 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 864 | 1 | 716 | 0.0 | 0.0 | None | None | 148 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2767 | 22 | 2428 | 100.0 | 0.0 | 7640.726030111313 | 7642.349580049515 | 339 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `144`
- Gating Δ: `18334`
- No-generation Δ: `118980`
- Fast failures Δ: `1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.9387, "current_avg_pnl": 1.5362, "current_win_rate": 75.0, "previous_avg_pnl": 0.5975, "previous_win_rate": 50.0, "win_rate_delta": 25.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.391, "current_avg_pnl": -1.1857, "current_win_rate": 12.5, "previous_avg_pnl": -0.7947, "previous_win_rate": 25.0, "win_rate_delta": -12.5}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.0075, "current_avg_pnl": 0.876, "current_win_rate": 45.5, "previous_avg_pnl": 0.8685, "previous_win_rate": 34.3, "win_rate_delta": 11.2}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.4865, "current_avg_pnl": -0.273, "current_win_rate": 28.6, "previous_avg_pnl": 0.2135, "previous_win_rate": 20.0, "win_rate_delta": 8.6}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -5, "geometry_changed_delta": 0, "geometry_preserved_delta": 69, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -1956.19, "median_terminal_delta_sec": -1957.1, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 6, "geometry_changed_delta": 0, "geometry_preserved_delta": 225, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 3673.76, "median_terminal_delta_sec": 3670.22, "sl_rate_delta": -50.0, "win_rate_delta": 100.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_AVWAP_SCALP**
- Most promising healthy path: **MOVER_TREND_PULLBACK**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_AVWAP_SCALP**
