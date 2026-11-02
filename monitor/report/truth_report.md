# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, MOVER_AVWAP_SCALP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `601` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 14 | 14 | 14 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 5958 | 5958 | 5307 | 16 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 44191 | 44219 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 47834 | 47834 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 47397 | 46081 | 1738 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 47876 | 47160 | 836 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 47640 | 47544 | 120 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 39937 | 39956 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 48003 | 48033 | 6 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 48047 | 46264 | 2627 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 47285 | 51261 | 589 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 44221 | 41332 | 5897 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 47291 | 47291 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 47840 | 47861 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 47356 | 47234 | 157 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 48896 | 48154 | 1111 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 46979 | 47154 | 164 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 39261 | 37676 | 1864 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 39547 | 39274 | 378 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 44153 | 44173 | 10 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 39960 | 39980 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2853 | 2853 | 2640 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 592 | 592 | 180 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 8966 | 8966 | 8781 | 5 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 15 | 15 | 4 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 5969 | 5969 | 4004 | 3 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1051 | 1051 | 373 | 32 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 15140 | 15140 | 7629 | 231 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 5 | 5 | 4 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 936 | 936 | 422 | 59 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 2634 | 2634 | 2108 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 536 | 536 | 134 | 12 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1486 | 1486 | 1202 | 24 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 29 | 29 | 6 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=44219): breakout_not_found=26102, basic_filters_failed=9432, move_not_fresh=6269, breakout_stale=1882, retest_proximity_failed=458, volume_spike_missing=74, missing_fvg_or_orderblock=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=47834): cls_disabled_merged_into_lsr=47834
- **EVAL::DIVERGENCE_CONTINUATION** (total=46081): cvd_divergence_failed=19152, h1_trend_not_aligned=14434, basic_filters_failed=8567, ema_alignment_reject=3367, retest_proximity_failed=312, missing_fvg_or_orderblock=249
- **EVAL::FAILED_AUCTION_RECLAIM** (total=47160): auction_not_detected=33076, basic_filters_failed=8386, reclaim_hold_failed=2896, tail_too_small=1777, regime_blocked=1013, rsi_reject=12
- **EVAL::FUNDING_EXTREME** (total=47544): funding_not_extreme=36261, basic_filters_failed=7933, missing_funding_rate=1489, ema_alignment_reject=1286, rsi_reject=324, cvd_divergence_failed=134, momentum_reject=105, missing_fvg_or_orderblock=12
- **EVAL::LIQUIDATION_REVERSAL** (total=39956): cascade_threshold_not_met=31181, basic_filters_failed=8396, cvd_divergence_failed=241, rsi_reject=121, missing_fvg_or_orderblock=14, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=48033): no_ma_cross=38302, basic_filters_failed=8584, ma_cross_cooldown=914, ma_cross_htf_misaligned=233
- **EVAL::MEAN_REVERT** (total=46264): no_extension=41309, basic_filters_failed=4955
- **EVAL::MOVER_AVWAP_SCALP** (total=51261): no_mover_leg=20758, no_avwap_tag=15397, basic_filters_failed=9625, avwap_slope_against=3381, avwap_reclaim_no_volume=1084, no_avwap_reclaim=998, anchor_too_recent=18
- **EVAL::MOVER_TREND_PULLBACK** (total=41332): mover_run_too_small=25306, basic_filters_failed=9538, no_reclaim=5567, no_pullback_tag=921
- **EVAL::OPENING_RANGE_BREAKOUT** (total=47291): feature_disabled=47291
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=47861): regime_blocked=29868, breakout_not_found=12633, adx_reject=2797, basic_filters_failed=2472, ema_alignment_reject=90, rsi_reject=1
- **EVAL::QUIET_COMPRESSION_BREAK** (total=47234): regime_blocked=18818, compression_not_detected=13978, breakout_not_detected=7994, basic_filters_failed=5904, volume_confirmation_failed=527, missing_fvg_or_orderblock=7, rsi_reject=6
- **EVAL::RANGE_FADE** (total=48154): no_range_edge=43194, basic_filters_failed=4960
- **EVAL::SR_FLIP_RETEST** (total=47154): flip_close_not_confirmed=33619, basic_filters_failed=8366, retest_out_of_zone=1221, h1_break_not_confirmed=1126, long_break_volume_thin=1045, regime_blocked=1004, reclaim_hold_failed=515, wick_quality_failed=73, long_acceptance_not_held=69, whipsaw_flip=55, ema_alignment_reject=53, missing_fvg_or_orderblock=8
- **EVAL::STANDARD** (total=37676): momentum_reject=12645, adx_reject=10686, sweeps_not_detected=4727, basic_filters_failed=3535, macd_reject=3105, ema_alignment_reject=2239, htf_poi_unanchored=705, mtf_reject=13, invalid_sl_geometry=12, rsi_reject=9
- **EVAL::TREND_PULLBACK** (total=39274): h1_trend_not_aligned=14724, ema_alignment_reject=6656, basic_filters_failed=4896, h1_pullback_not_confirmed=3417, no_ema_reclaim_close=2636, ema_not_tested_prev=2260, body_conviction_fail=1980, rsi_reject=1392, prev_already_below_emas=454, no_prev_low_break=265, prev_already_above_emas=239, no_prev_high_break=162, momentum_flat=113, ema21_not_tagged=38, momentum_reject=25, missing_fvg_or_orderblock=17
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=44173): breakout_not_found=28498, basic_filters_failed=9430, move_not_fresh=3677, breakout_stale=1913, retest_proximity_failed=549, volume_spike_missing=92, missing_fvg_or_orderblock=7, move_exhausted=7
- **EVAL::WHALE_MOMENTUM** (total=39980): momentum_reject=32950, recent_ticks_insufficient=6427, basic_filters_failed=603

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=229): setup_compat:regime_VOLATILE_UNSUITABLE=212, setup_compat:regime_BREAKOUT_EXPANSION=17
- **FAILED_AUCTION_RECLAIM** (total=635): setup_compat:regime_STRONG_TREND=363, execution:overextended=248, context_floor=24
- **FUNDING_EXTREME_SIGNAL** (total=573): execution:trigger_not_confirmed=560, context_floor=13
- **LIQUIDATION_REVERSAL** (total=3): execution:trigger_not_confirmed=3
- **LIQUIDITY_SWEEP_REVERSAL** (total=2134): execution:trigger_not_confirmed=981, setup_compat:regime_STRONG_TREND=648, execution:overextended=505
- **MA_CROSS_TREND_SHIFT** (total=11): execution:trigger_not_confirmed=4, setup_compat:regime_CLEAN_RANGE=4, setup_compat:regime_DIRTY_RANGE=3
- **MEAN_REVERT** (total=4002): setup_compat:regime_WEAK_TREND=1856, setup_compat:regime_STRONG_TREND=1756, execution:overextended=390
- **MOVER_AVWAP_SCALP** (total=707): execution:overextended=564, entry_quality=97, execution:trigger_not_confirmed=46
- **MOVER_TREND_PULLBACK** (total=7857): execution:trigger_not_confirmed=3640, execution:overextended=3136, entry_quality=1081
- **QUIET_COMPRESSION_BREAK** (total=23): execution:trigger_not_confirmed=23
- **RANGE_FADE** (total=1617): setup_compat:regime_STRONG_TREND=830, setup_compat:regime_WEAK_TREND=557, execution:overextended=138, setup_compat:regime_VOLATILE_UNSUITABLE=56, context_edge=34, setup_compat:regime_BREAKOUT_EXPANSION=2
- **TREND_PULLBACK_EMA** (total=1238): setup_compat:regime_CLEAN_RANGE=748, setup_compat:regime_DIRTY_RANGE=396, entry_quality=65, setup_compat:regime_VOLATILE_UNSUITABLE=29
- **VOLUME_SURGE_BREAKOUT** (total=12): execution:overextended=12

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 79028 | 31.8% |
| QUIET | 73707 | 29.7% |
| TRENDING_DOWN | 50634 | 20.4% |
| TRENDING_UP | 36184 | 14.6% |
| VOLATILE | 8746 | 3.5% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **232**
- Average confidence gap to threshold: **13.97** (samples=232) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=44, TRXUSDT=32, BTCUSDT=25, XMRUSDT=20, SOLUSDT=17, INJUSDT=13, ENAUSDT=11, ADAUSDT=7, ZECUSDT=6, XLMUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 162 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 89 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 40 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 13 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 8 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 12 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 56 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 4 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 10 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 3 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 3 |
| MEAN_REVERT | filtered | min_confidence | 24 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 6 |
| MEAN_REVERT | kept | min_confidence_pass | 3 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 128 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 165 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1055 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 10 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2097 |
| POST_DISPLACEMENT_CONTINUATION | filtered | min_confidence | 3 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 151 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 57 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 225 |
| SR_FLIP_RETEST | filtered | min_confidence | 92 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 11 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 68 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 76 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 10 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 91 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 21 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 162 | 51.05 | 62.70 | 11.65 | 21.30 | 19.68 | 17.81 | 1.61 | 17.81 |
| DIVERGENCE_CONTINUATION | kept | 89 | 68.36 | 65.00 | -3.36 | 20.41 | 19.98 | 16.59 | 2.30 | 2.60 |
| FAILED_AUCTION_RECLAIM | filtered | 53 | 45.70 | 64.25 | 18.55 | 21.02 | 20.00 | 20.00 | 1.40 | 10.66 |
| FAILED_AUCTION_RECLAIM | kept | 8 | 75.18 | 65.00 | -10.18 | 20.44 | 19.80 | 20.00 | 2.94 | 1.75 |
| FUNDING_EXTREME_SIGNAL | filtered | 12 | 50.95 | 63.92 | 12.97 | 20.19 | 14.46 | 17.00 | 4.58 | 15.53 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 71.20 | 65.00 | -6.20 | 19.10 | 13.90 | 14.20 | 5.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 60 | 46.76 | 65.00 | 18.24 | 20.50 | 19.16 | 18.78 | 2.87 | 9.47 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 10 | 66.64 | 65.00 | -1.64 | 21.53 | 16.75 | 17.58 | 1.20 | 0.48 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 39.63 | 61.00 | 21.37 | 20.53 | 20.00 | 15.80 | 0.00 | 22.67 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 67.07 | 65.00 | -2.07 | 20.60 | 20.00 | 15.80 | 0.00 | 3.43 |
| MEAN_REVERT | filtered | 30 | 50.88 | 65.00 | 14.12 | 19.09 | 19.12 | 15.32 | 0.00 | 16.94 |
| MEAN_REVERT | kept | 3 | 73.73 | 65.00 | -8.73 | 22.70 | 18.30 | 15.67 | 0.00 | 1.40 |
| MOVER_AVWAP_SCALP | filtered | 128 | 51.35 | 63.78 | 12.43 | 20.47 | 16.22 | 15.80 | 3.68 | 18.54 |
| MOVER_AVWAP_SCALP | kept | 165 | 77.35 | 65.00 | -12.35 | 20.17 | 16.44 | 15.80 | 5.05 | 4.59 |
| MOVER_TREND_PULLBACK | filtered | 1065 | 53.67 | 63.99 | 10.32 | 19.80 | 18.47 | 15.80 | 4.12 | 19.53 |
| MOVER_TREND_PULLBACK | kept | 2097 | 77.06 | 65.00 | -12.06 | 20.07 | 18.72 | 15.80 | 4.38 | 1.69 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 3 | 60.50 | 61.00 | 0.50 | 20.60 | 20.00 | 20.00 | 4.50 | 23.00 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 72.00 | 65.00 | -7.00 | 20.10 | 20.00 | 16.60 | 3.50 | 1.80 |
| QUIET_COMPRESSION_BREAK | filtered | 208 | 52.00 | 64.92 | 12.92 | 21.65 | 19.50 | 20.00 | 0.00 | 11.47 |
| QUIET_COMPRESSION_BREAK | kept | 225 | 75.02 | 65.00 | -10.02 | 20.74 | 19.76 | 20.00 | 0.00 | -0.02 |
| SR_FLIP_RETEST | filtered | 103 | 53.36 | 63.94 | 10.58 | 20.54 | 20.00 | 16.08 | 1.78 | 17.57 |
| SR_FLIP_RETEST | kept | 68 | 66.80 | 65.00 | -1.80 | 20.80 | 20.00 | 15.54 | 1.91 | 2.75 |
| TREND_PULLBACK_EMA | filtered | 86 | 57.47 | 64.94 | 7.47 | 20.56 | 19.73 | 17.36 | 4.95 | 17.20 |
| TREND_PULLBACK_EMA | kept | 91 | 78.28 | 65.00 | -13.28 | 20.89 | 19.81 | 17.32 | 4.66 | 3.17 |
| VOLUME_SURGE_BREAKOUT | filtered | 21 | 40.69 | 62.90 | 22.21 | 20.92 | 15.51 | 20.00 | 3.45 | 16.04 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 75.25 | 65.00 | -10.25 | 20.70 | 17.10 | 20.00 | 4.25 | 1.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 162 | 51.05 | 21.89 | 15.47 | 4.13 | 12.62 | 5.26 | 7.97 | 1.61 |
| DIVERGENCE_CONTINUATION | kept | 89 | 68.36 | 24.46 | 16.54 | 4.21 | 10.90 | 5.66 | 8.19 | 2.30 |
| FAILED_AUCTION_RECLAIM | filtered | 53 | 45.70 | 17.91 | 14.98 | 6.62 | 14.30 | 6.85 | 5.63 | 1.40 |
| FAILED_AUCTION_RECLAIM | kept | 8 | 75.18 | 24.00 | 17.00 | 4.88 | 14.25 | 6.06 | 7.80 | 2.94 |
| FUNDING_EXTREME_SIGNAL | filtered | 12 | 50.95 | 24.33 | 16.33 | 6.25 | 10.17 | 5.71 | 2.86 | 4.58 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 71.20 | 25.00 | 8.00 | 12.00 | 12.00 | 8.50 | 0.70 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 60 | 46.76 | 20.73 | 14.20 | 5.15 | 13.12 | 7.31 | 5.85 | 2.87 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 10 | 66.64 | 20.60 | 15.20 | 4.50 | 13.10 | 5.00 | 7.52 | 1.20 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 39.63 | 19.67 | 14.00 | 5.00 | 13.00 | 7.00 | 8.63 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 67.07 | 19.00 | 14.00 | 3.00 | 16.00 | 8.50 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 30 | 50.88 | 23.40 | 14.80 | 4.20 | 13.00 | 5.00 | 7.42 | 0.00 |
| MEAN_REVERT | kept | 3 | 73.73 | 22.33 | 18.00 | 10.00 | 13.00 | 5.00 | 6.77 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 128 | 51.35 | 17.80 | 18.11 | 12.45 | 13.58 | 7.52 | 6.14 | 3.68 |
| MOVER_AVWAP_SCALP | kept | 165 | 77.35 | 20.30 | 18.05 | 10.95 | 13.66 | 6.48 | 7.79 | 5.05 |
| MOVER_TREND_PULLBACK | filtered | 1065 | 53.67 | 18.20 | 18.04 | 7.88 | 12.66 | 6.42 | 8.48 | 4.12 |
| MOVER_TREND_PULLBACK | kept | 2097 | 77.06 | 19.35 | 18.03 | 7.82 | 13.53 | 6.69 | 9.08 | 4.38 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 3 | 60.50 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 10.00 | 4.50 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 72.00 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 4.30 | 3.50 |
| QUIET_COMPRESSION_BREAK | filtered | 208 | 52.00 | 19.20 | 16.90 | 11.55 | 14.23 | 6.96 | 5.50 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 225 | 75.02 | 18.15 | 17.84 | 11.75 | 14.12 | 7.17 | 7.35 | 0.00 |
| SR_FLIP_RETEST | filtered | 103 | 53.36 | 20.46 | 16.93 | 5.27 | 14.30 | 5.60 | 8.04 | 1.78 |
| SR_FLIP_RETEST | kept | 68 | 66.80 | 20.88 | 15.79 | 4.72 | 13.93 | 5.44 | 7.74 | 1.91 |
| TREND_PULLBACK_EMA | filtered | 86 | 57.47 | 18.78 | 18.00 | 7.95 | 14.42 | 6.19 | 8.76 | 4.95 |
| TREND_PULLBACK_EMA | kept | 91 | 78.28 | 20.87 | 18.00 | 7.58 | 14.65 | 6.88 | 9.24 | 4.66 |
| VOLUME_SURGE_BREAKOUT | filtered | 21 | 40.69 | 17.00 | 17.62 | 12.71 | 12.57 | 4.52 | 3.84 | 3.45 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 75.25 | 17.00 | 16.00 | 12.00 | 12.50 | 5.00 | 10.00 | 4.25 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 162 | 51.05 | 0.00 | 0.00 | 3.83 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.83** |
| DIVERGENCE_CONTINUATION | kept | 89 | 68.36 | 0.00 | 0.00 | 0.97 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.97** |
| FAILED_AUCTION_RECLAIM | filtered | 53 | 45.70 | 0.00 | 0.00 | 1.09 | 0.00 | 1.22 | 0.00 | 0.00 | 0.00 | **2.31** |
| FAILED_AUCTION_RECLAIM | kept | 8 | 75.18 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 12 | 50.95 | 0.00 | 0.00 | 9.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **9.00** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 71.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 60 | 46.76 | 0.00 | 0.00 | 0.40 | 0.00 | 0.36 | 0.00 | 0.00 | 0.00 | **0.76** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 10 | 66.64 | 0.00 | 0.00 | 0.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.48** |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 39.63 | 0.00 | 0.00 | 2.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.67** |
| MA_CROSS_TREND_SHIFT | kept | 3 | 67.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 30 | 50.88 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 3 | 73.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 128 | 51.35 | 0.00 | 0.00 | 3.67 | 0.00 | 3.30 | 0.00 | 0.00 | 1.18 | **8.15** |
| MOVER_AVWAP_SCALP | kept | 165 | 77.35 | 0.00 | 0.00 | 0.10 | 0.00 | 1.45 | 0.00 | 0.00 | 0.48 | **2.03** |
| MOVER_TREND_PULLBACK | filtered | 1065 | 53.67 | 0.32 | 0.00 | 2.79 | 0.00 | 0.65 | 0.00 | 0.00 | 0.00 | **3.76** |
| MOVER_TREND_PULLBACK | kept | 2097 | 77.06 | 0.00 | 0.00 | 0.75 | 0.00 | 0.23 | 0.01 | 0.00 | 0.00 | **0.99** |
| POST_DISPLACEMENT_CONTINUATION | filtered | 3 | 60.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 72.00 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| QUIET_COMPRESSION_BREAK | filtered | 208 | 52.00 | 0.00 | 0.00 | 1.05 | 0.00 | 0.82 | 0.00 | 0.00 | 2.89 | **4.76** |
| QUIET_COMPRESSION_BREAK | kept | 225 | 75.02 | 0.00 | 0.00 | 0.26 | 0.00 | 0.40 | 0.00 | 0.00 | 0.00 | **0.66** |
| SR_FLIP_RETEST | filtered | 103 | 53.36 | 0.00 | 0.00 | 1.43 | 0.00 | 0.84 | 0.00 | 0.00 | 0.00 | **2.27** |
| SR_FLIP_RETEST | kept | 68 | 66.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 86 | 57.47 | 0.00 | 0.00 | 2.98 | 0.00 | 2.93 | 0.00 | 0.00 | 0.00 | **5.91** |
| TREND_PULLBACK_EMA | kept | 91 | 78.28 | 0.00 | 0.00 | 1.72 | 0.00 | 0.13 | 0.00 | 0.00 | 0.00 | **1.85** |
| VOLUME_SURGE_BREAKOUT | filtered | 21 | 40.69 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.80 | **2.80** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 75.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **170382 held of 695233 seen** across 21 strategies; 3840 cells past the sample floor; **2013 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 46907 | 737/46170/0 | 45% | -0.15 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING (-1.40R) |
| MOVER_AVWAP_SCALP | 22352 | 200/22152/0 | 43% | -0.21 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 12799 | 159/12640/0 | 47% | -0.09 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 12518 | 153/12365/0 | 37% | -0.29 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 10958 | 55/10903/0 | 39% | -0.27 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.38R) |
| LIQUIDITY_SWEEP_REVERSAL | 9399 | 108/9291/0 | 35% | -0.47 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| SHADOW_MEAN_REVERT | 7815 | 0/0/7815 | 42% | -0.12 | NY/MARKDOWN/CASCADE/BTC_FALLING (+0.34R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-0.91R) |
| QUIET_COMPRESSION_BREAK | 7529 | 407/7122/0 | 49% | -0.13 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_RANGE_FADE | 7349 | 0/0/7349 | 36% | -0.12 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.51R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.13R) |
| SHADOW_FUNDING_FADE | 6693 | 0/0/6693 | 35% | -0.40 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-0.00R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 5125 | 17/5108/0 | 46% | -0.25 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+2.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 4951 | 64/4887/0 | 36% | -0.35 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| FUNDING_EXTREME_SIGNAL | 3765 | 2/3763/0 | 31% | -0.46 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3526 | 0/3526/0 | 32% | -0.33 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| RANGE_FADE | 2072 | 6/2066/0 | 40% | -0.21 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1568 | 0/0/1568 | 53% | -0.07 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 474 | 0/474/0 | 30% | -0.55 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 172 | 32/140/0 | 42% | -0.19 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 50 | 2/48/0 | 36% | -0.07 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.63R (n=26, NEGATIVE); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.63R (n=26, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 321 | 27% / -0.56R | 321 | 54% / -0.09R | +0.47 | **ATR** |
| LIQUIDATION_REVERSAL | 32 | 22% / -0.73R | 32 | 44% / -0.38R | +0.35 | **ATR** |
| TREND_PULLBACK_EMA | 1005 | 38% / -0.36R | 1005 | 51% / -0.08R | +0.29 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1471 | 42% / -0.37R | 1471 | 56% / -0.13R | +0.24 | **ATR** |
| SR_FLIP_RETEST | 505 | 43% / -0.32R | 505 | 47% / -0.18R | +0.14 | **ATR** |
| MA_CROSS_TREND_SHIFT | 53 | 40% / -0.21R | 53 | 43% / -0.08R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 2269 | 43% / -0.19R | 2269 | 50% / -0.06R | +0.13 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 187 | 36% / -0.20R | 187 | 47% / -0.07R | +0.13 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1305 | 41% / -0.22R | 1305 | 43% / -0.12R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 8472 | 49% / -0.11R | 8472 | 54% / -0.02R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| RANGE_FADE | 112 | 38% / -0.13R | 112 | 46% / -0.05R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1489 | 47% / -0.12R | 1489 | 53% / -0.05R | +0.06 | **ATR** |
| MEAN_REVERT | 364 | 45% / -0.22R | 364 | 43% / -0.23R | -0.02 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1316 | 47% / -0.13R | 1316 | 47% / -0.14R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 13 | 62% / -0.06R | 13 | 62% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11381 | 29% | -0.21R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2269 | 48% | -0.05R | 233 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 118 | 47% | -0.07R | 66 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1689 | 39% / -0.15R | +0.86 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1327 | 33% / -0.25R | +0.82 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2793 | 34% / -0.22R | +0.62 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10358 | 36% / -0.17R | +0.36 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1730 | 37% / -0.12R | +0.16 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1273 | 37% / -0.13R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1096 | 32% / -0.25R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 274 | 31% / -0.36R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 423 | 33% / -0.14R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 310 | 45% / -0.13R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 82 | 44% / +0.04R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 452 | 32% / -0.34R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 83 | 29% / -0.40R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 40 | 45% / -0.26R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 21 | 43% / +0.59R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **5** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×499]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 533/6) (sustained 533 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 533/6) (sustained 533 cycles)
- **ALERT** `tuned_variants` — 470 non-stamps — atr_arm_uncomputable=470 (seen=12121 stamped=1831 skipped=9820) (streak 510/6) (sustained 510 cycles)
- **ALERT** `auto_dispatch` — 135 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=138) (streak 529/3) (sustained 529 cycles)
- **ALERT** `fail_open:llm_client.google` — +1 fail-open(s) this cycle (total 128); last: TimeoutError:  (sustained 5 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 42 fed / 0 quiet / 0 never delivered of 42 subscribed; 126864585 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 20 arms current, none stalled; covering 2150/2150 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 1/6) | 1 |
| atr_trail_live_arms | ok | 41 arms current, none stalled; covering 1151/1151 signals (100%) | 0 |
| auto_dispatch | violating | 135 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=138) (streak 529/3) | 529 |
| binance_ip_weight | ok | peak 5/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 78162.80 | 0 |
| candle_coverage | ok | 81/81 symbols with ≥20 15m candles, 81/81 updated within 45m [fresh=81; 80 Tier-1 futures + 1 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1412 dup bars, 0 undedupable; ws 0 out-of-order, 465 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +42 / upstream +15 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1985/2004 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | 92 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1979/1998 signals (99%) | 0 |
| depth_feed | ok | 42/42 books fresh (stale 0, never 0, thin 0); 54215241 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 533/6) | 533 |
| emission_controller | ok | last cycle 2s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×499]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 533/6) | 533 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 1/6) | 1 |
| firestore_read_budget | ok | 1,324 reads/day of 50,000 [engine 1,297, signing 27]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 5040 sealed bars over 42 symbols; 1798 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +14 / upstream +414 | 0 |
| indicator_cache_key | ok | 225744 frozen value(s) avoided; 518356 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.35R over n=4887 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +124 / upstream +414 | 0 |
| mover_admission_metadata | ok | 942 symbols known, 235 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 1 held, 1 with scan counts, 1 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 7 locked / 7 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2217 rows held, 3267037 evicted (sampled: execution:trigger_not_confirmed 300/1151799, execution:overextended 300/1024684, setup_compat:regime_STRONG_TREND 300/554431) | 0 |
| price_action_lane | ok | 839447 evaluated, 1732 emitted; layer1 1732 stamped / 0 blind; cooldown=118646, delta_opposed=58052, no_footprint=315034, no_levels=41, no_opposing_target=1365, no_sweep=292953, rr_below_floor=51624 | 0 |
| promoted_pair_integrity | ok | 1/1 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.21R over n=2066 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +33 / upstream +414 | 0 |
| sar_alignment_crosscheck | ok | 1357/34879 disagreed (3.9%) | 0 |
| sar_exit_shadow | ok | output +16 / upstream +414 | 0 |
| sar_hold_arm | ok | 1872 held arms settled, 128 unscored, 41 still walking (33 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 8/67 unfetchable (12%); top cause: located bar does not contain the stamp; symbols: AINUSDT, AVAXUSDT, BIOUSDT, GUSDT, LINKUSDT +3 more | 0 |
| sar_live_arms | ok | 41 arms current, none stalled; covering 1150/1150 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 467 records await one (59 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| scan_cycle | ok | last 6.64s, worst 250.75s over 10029 lifetime cycles; lifetime 721 over 60s, 172 over 120s (plus 1/0 during boot warm-up, not counted); recent 2/0 warn/kill breaches in 20/20 cycles; heartbeat age 2.29s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 360840 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 123s ago (2.99s to run, worst 214.32s), 2199 overrun(s) of 10897 cycles, TTL 900s; slowest router_delivery=22.61s, trail_governor=19.04s, positions_diag=18.9s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=615, gate reads=0, withheld=615) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +78 / upstream +414 | 0 |
| structural_snap | ok | 6000/6000 measured, 34 blind, 0 levels moved (refusals: redetect_cooldown=1748) | 0 |
| structural_veto_lane | ok | 3244 stamped; 0 with no readable level book, 27 with clear air ahead, 2329 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +414 / upstream +15 | 0 |
| tuned_variants | violating | 470 non-stamps — atr_arm_uncomputable=470 (seen=12121 stamped=1831 skipped=9820) (streak 510/6) | 510 |
| unlock_shorts | ok | 12 open, 47 scheduled, calendar 10.1h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 128 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1200984`
- `Path funnel` emissions: `33`
- `Regime distribution` emissions: `33`
- `QUIET_SCALP_BLOCK` events: `232`
- `confidence_gate` events: `4697`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **31**
- Total REST-fallback activations: **3**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 5 | 27351 | 34353 | 36442 | 0 |
| futures_aggtrade | 6 | 7862 | 7939 | 7940 | 0 |
| futures_depth | 17 | 24363 | 49622 | 50326 | 0 |
| futures_liq | 1 | 2049 | 2049 | 2049 | 0 |
| futures_mover | 2 | 27318 | 27318 | 28098 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 3 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=194930] state[populated=194930] buckets[many=194930] sources[none] quality[none]
- funding_rate: presence[absent=6141, present=188789] state[empty=6141, populated=188789] buckets[few=188789, none=6141] sources[none] quality[none]
- liquidation_clusters: presence[absent=110961, present=83969] state[empty=110961, populated=83969] buckets[few=69753, none=110961, some=14216] sources[none] quality[none]
- oi_snapshot: presence[absent=6140, present=188790] state[empty=6140, populated=188790] buckets[few=301, many=186929, none=6140, some=1560] sources[none] quality[none]
- order_book: presence[absent=64018, present=130912] state[populated=130912, unavailable=64018] buckets[few=130912, none=64018] sources[book_ticker=130912, unavailable=64018] quality[none=64018, top_of_book_only=130912]
- orderblocks: presence[absent=194930] state[empty=194930] buckets[none=194930] sources[measured_dark=194930] quality[none]
- recent_ticks: presence[present=194930] state[populated=194930] buckets[many=194930] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `7.617293000221252` sec
- Median create→first breach: `4318.671307444572` sec
- Median create→terminal: `4318.671348452568` sec
- Median first breach→terminal: `5.745887756347656e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 3.6}, "under_180s": {"count": 2, "pct": 3.6}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.870442119908929 | 1.0189360990297749 | 0.845786355294097 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.8219095901502369 | 0.987095492034042 | 0.8374277159753984 | 0 | 2 |
| MEAN_REVERT | 2 | 2 | 1.1064920911292055 | 1.0155445597468513 | 1.8407777967568384 | 1 | 1 |
| MOVER_AVWAP_SCALP | 3 | 3 | 3.2776674078599557 | 2.976299999999987 | 1.0925558026199853 | 2 | 1 |
| MOVER_TREND_PULLBACK | 35 | 35 | 3.9291761982173092 | 3.0 | 1.38330532005902 | 31 | 4 |
| QUIET_COMPRESSION_BREAK | 11 | 11 | 0.8589544072948377 | 1.1027035555656246 | 0.8710552620305559 | 0 | 11 |
| TREND_PULLBACK_EMA | 1 | 1 | 2.009120349867132 | 2.258026346927507 | 0.889768338000546 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -0.8704 | 5177.61393904686 | 5177.613997578621 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -0.8219 | 7576.166059970856 | 7576.166095495224 |
| MEAN_REVERT | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.1065 | 8491.581446409225 | 8491.581486463547 |
| MOVER_AVWAP_SCALP | 3 | 3 | 33.3 | 66.7 | 33.3 | 0.0 | -0.3308 | 969.992812871933 | 971.3295929431915 |
| MOVER_TREND_PULLBACK | 35 | 35 | 25.7 | 34.3 | 25.7 | 0.0 | 0.3147 | 2027.459053993225 | 2032.3180031776428 |
| QUIET_COMPRESSION_BREAK | 11 | 11 | 9.1 | 90.9 | 9.1 | 0.0 | -0.8105 | 24363.04040002823 | 24363.04042315483 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.0091 | 4708.726525068283 | 4708.726547002792 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 536 | 12 | 134 | 0.0 | 0.0 | None | None | 402 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1486 | 24 | 1202 | 0.0 | 100.0 | 4708.726525068283 | 4708.726547002792 | 284 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-122`
- Gating Δ: `-933`
- No-generation Δ: `-277402`
- Fast failures Δ: `1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -1.3113, "current_avg_pnl": -0.8219, "current_win_rate": 0.0, "previous_avg_pnl": 0.4894, "previous_win_rate": 66.7, "win_rate_delta": -66.7}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.7479, "current_avg_pnl": -0.3308, "current_win_rate": 33.3, "previous_avg_pnl": 0.4171, "previous_win_rate": 50.0, "win_rate_delta": -16.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.183, "current_avg_pnl": 0.3147, "current_win_rate": 25.7, "previous_avg_pnl": 0.1317, "previous_win_rate": 27.6, "win_rate_delta": -1.9}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -1.0979, "current_avg_pnl": -0.8105, "current_win_rate": 9.1, "previous_avg_pnl": 0.2874, "previous_win_rate": 50.0, "win_rate_delta": -40.9}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 8, "geometry_changed_delta": 0, "geometry_preserved_delta": 271, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -10, "geometry_changed_delta": 0, "geometry_preserved_delta": -29, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 4708.73, "median_terminal_delta_sec": 4708.73, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
