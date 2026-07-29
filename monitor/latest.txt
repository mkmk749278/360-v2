# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `8528` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 133 | 133 | 74 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 17345 | 17345 | 14901 | 35 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 119919 | 119888 | 45 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 104024 | 104035 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 103610 | 98929 | 5085 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 104069 | 99983 | 4328 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 104968 | 104747 | 262 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 92865 | 92870 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 104323 | 104359 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 104371 | 100925 | 4434 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 125542 | 129964 | 1883 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 119937 | 106948 | 18547 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 102161 | 102170 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 104038 | 104021 | 43 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 103572 | 103069 | 542 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 105360 | 103002 | 3187 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 100729 | 100550 | 2960 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 91151 | 87199 | 4287 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 91493 | 90969 | 566 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 119889 | 119871 | 45 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 92873 | 92891 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 15133 | 15133 | 11829 | 33 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 689 | 689 | 652 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 6 | 6 | 6 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 21635 | 21635 | 21060 | 31 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 10 | 10 | 6 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 10216 | 10216 | 9477 | 8 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3671 | 3671 | 2792 | 14 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 43621 | 43621 | 24336 | 472 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 92 | 92 | 91 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2108 | 2108 | 1158 | 21 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 7864 | 7864 | 7042 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 10524 | 10524 | 2065 | 136 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2050 | 2050 | 1805 | 6 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 143 | 143 | 78 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=119888): breakout_not_found=60949, basic_filters_failed=37685, move_not_fresh=12991, breakout_stale=5285, retest_proximity_failed=2565, volume_spike_missing=380, move_exhausted=14, ema_alignment_reject=8, missing_fvg_or_orderblock=8, rsi_reject=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=104035): cls_disabled_merged_into_lsr=104035
- **EVAL::DIVERGENCE_CONTINUATION** (total=98929): cvd_divergence_failed=32797, basic_filters_failed=30192, h1_trend_not_aligned=23197, ema_alignment_reject=10937, retest_proximity_failed=1256, missing_fvg_or_orderblock=550
- **EVAL::FAILED_AUCTION_RECLAIM** (total=99983): auction_not_detected=35304, basic_filters_failed=29064, reclaim_hold_failed=17909, tail_too_small=13289, regime_blocked=4414, rsi_reject=3
- **EVAL::FUNDING_EXTREME** (total=104747): funding_not_extreme=68830, basic_filters_failed=30575, ema_alignment_reject=2670, missing_funding_rate=1527, rsi_reject=681, cvd_divergence_failed=256, momentum_reject=185, missing_fvg_or_orderblock=23
- **EVAL::LIQUIDATION_REVERSAL** (total=92870): cascade_threshold_not_met=61180, basic_filters_failed=30831, cvd_divergence_failed=493, rsi_reject=340, missing_fvg_or_orderblock=18, volume_spike_missing=8
- **EVAL::MA_CROSS_TREND_SHIFT** (total=104359): no_ma_cross=73058, basic_filters_failed=30212, ma_cross_cooldown=640, ma_cross_htf_misaligned=449
- **EVAL::MEAN_REVERT** (total=100925): no_extension=81580, basic_filters_failed=19345
- **EVAL::MOVER_AVWAP_SCALP** (total=129964): no_avwap_tag=43909, basic_filters_failed=37874, no_mover_leg=34057, avwap_slope_against=9260, avwap_reclaim_no_volume=2493, no_avwap_reclaim=2290, anchor_too_recent=81
- **EVAL::MOVER_TREND_PULLBACK** (total=106948): mover_run_too_small=40788, basic_filters_failed=37786, no_reclaim=24237, no_pullback_tag=4137
- **EVAL::OPENING_RANGE_BREAKOUT** (total=102170): feature_disabled=102170
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=104021): regime_blocked=62887, breakout_not_found=28553, basic_filters_failed=7526, adx_reject=4974, ema_alignment_reject=81
- **EVAL::QUIET_COMPRESSION_BREAK** (total=103069): regime_blocked=45438, compression_not_detected=23291, basic_filters_failed=21523, breakout_not_detected=11603, volume_confirmation_failed=1173, rsi_reject=22, missing_fvg_or_orderblock=19
- **EVAL::RANGE_FADE** (total=103002): no_range_edge=83655, basic_filters_failed=19347
- **EVAL::SR_FLIP_RETEST** (total=100550): basic_filters_failed=29036, flip_close_not_confirmed=17092, long_break_volume_thin=13299, whipsaw_flip=12276, long_disabled=7675, retest_out_of_zone=7349, reclaim_hold_failed=7244, regime_blocked=4395, wick_quality_failed=1162, long_acceptance_not_held=581, missing_fvg_or_orderblock=249, ema_alignment_reject=178, rsi_reject=14
- **EVAL::STANDARD** (total=87199): momentum_reject=26252, adx_reject=25915, basic_filters_failed=13821, sweeps_not_detected=9541, ema_alignment_reject=5935, macd_reject=5607, invalid_sl_geometry=60, rsi_reject=57, mtf_reject=11
- **EVAL::TREND_PULLBACK** (total=90969): h1_trend_not_aligned=29022, h1_pullback_not_confirmed=20899, basic_filters_failed=14054, ema_alignment_reject=11584, ema_not_tested_prev=5356, no_ema_reclaim_close=4289, body_conviction_fail=2250, rsi_reject=1788, prev_already_below_emas=594, no_prev_low_break=457, momentum_flat=219, prev_already_above_emas=198, no_prev_high_break=126, ema21_not_tagged=86, missing_fvg_or_orderblock=32, momentum_reject=15
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=119871): breakout_not_found=63179, basic_filters_failed=37685, move_not_fresh=12246, breakout_stale=4586, retest_proximity_failed=1791, volume_spike_missing=157, ema_alignment_reject=147, move_exhausted=58, missing_fvg_or_orderblock=22
- **EVAL::WHALE_MOMENTUM** (total=92891): momentum_reject=65701, recent_ticks_insufficient=19524, basic_filters_failed=7666

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=457): setup_compat:regime_VOLATILE_UNSUITABLE=435, execution:overextended=15, setup_compat:regime_BREAKOUT_EXPANSION=7
- **FAILED_AUCTION_RECLAIM** (total=4868): setup_compat:regime_STRONG_TREND=3099, execution:overextended=1028, context_floor=741
- **FUNDING_EXTREME_SIGNAL** (total=617): execution:trigger_not_confirmed=617
- **LIQUIDATION_REVERSAL** (total=6): execution:trigger_not_confirmed=6
- **LIQUIDITY_SWEEP_REVERSAL** (total=5354): execution:trigger_not_confirmed=2227, setup_compat:regime_STRONG_TREND=1767, execution:overextended=1360
- **MA_CROSS_TREND_SHIFT** (total=6): setup_compat:regime_CLEAN_RANGE=3, setup_compat:regime_DIRTY_RANGE=2, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=7858): setup_compat:regime_WEAK_TREND=4579, setup_compat:regime_STRONG_TREND=3073, execution:overextended=206
- **MOVER_AVWAP_SCALP** (total=2567): execution:overextended=2119, execution:trigger_not_confirmed=448
- **MOVER_TREND_PULLBACK** (total=23081): execution:overextended=11847, execution:trigger_not_confirmed=11234
- **QUIET_COMPRESSION_BREAK** (total=600): context_floor=558, execution:trigger_not_confirmed=42
- **RANGE_FADE** (total=5397): setup_compat:regime_STRONG_TREND=2750, setup_compat:regime_WEAK_TREND=1961, setup_compat:regime_VOLATILE_UNSUITABLE=332, context_edge=201, execution:overextended=133, setup_compat:regime_BREAKOUT_EXPANSION=20
- **SR_FLIP_RETEST** (total=15): setup_compat:regime_VOLATILE_UNSUITABLE=15
- **TREND_PULLBACK_EMA** (total=1678): setup_compat:regime_CLEAN_RANGE=990, setup_compat:regime_DIRTY_RANGE=511, setup_compat:regime_VOLATILE_UNSUITABLE=133, context_floor=44
- **VOLUME_SURGE_BREAKOUT** (total=66): execution:overextended=46, context_floor=20

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 187285 | 32.0% |
| QUIET | 145518 | 24.8% |
| TRENDING_DOWN | 119127 | 20.3% |
| TRENDING_UP | 94032 | 16.1% |
| VOLATILE | 39713 | 6.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **449**
- Average confidence gap to threshold: **10.46** (samples=449) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: DOTUSDT=39, ARBUSDT=31, TAOUSDT=28, BNBUSDT=28, ENAUSDT=26, LTCUSDT=25, BCHUSDT=22, AAVEUSDT=21, BTCUSDT=19, WLDUSDT=14

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 7 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 412 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 9 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 507 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 99 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 69 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 395 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 29 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 7 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 288 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 5 |
| MEAN_REVERT | filtered | min_confidence | 2 |
| MEAN_REVERT | kept | min_confidence_pass | 47 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 211 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 578 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1471 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 123 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 12475 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 114 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 24 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 210 |
| SR_FLIP_RETEST | filtered | min_confidence | 882 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 96 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2832 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 6 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 105 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 15 |
| VOLUME_SURGE_BREAKOUT | filtered | quiet_scalp_min_confidence | 4 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 7 | 77.50 | 65.00 | -12.50 | 21.20 | 17.20 | 20.00 | 4.50 | 2.57 |
| DIVERGENCE_CONTINUATION | filtered | 421 | 57.45 | 64.21 | 6.76 | 20.23 | 19.72 | 18.02 | 2.29 | 9.62 |
| DIVERGENCE_CONTINUATION | kept | 507 | 69.90 | 65.00 | -4.90 | 20.74 | 19.83 | 17.49 | 2.07 | 3.06 |
| FAILED_AUCTION_RECLAIM | filtered | 168 | 53.38 | 64.73 | 11.35 | 21.48 | 19.31 | 20.00 | 4.51 | 6.03 |
| FAILED_AUCTION_RECLAIM | kept | 395 | 70.50 | 65.00 | -5.50 | 20.43 | 19.50 | 20.00 | 4.61 | 0.07 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 36 | 55.97 | 65.00 | 9.03 | 20.65 | 19.66 | 17.28 | 2.47 | 16.77 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 288 | 71.33 | 65.00 | -6.33 | 20.40 | 19.82 | 17.34 | 1.65 | -0.19 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 37.00 | 65.00 | 28.00 | 20.60 | 18.80 | 15.80 | 0.00 | 20.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.30 | 65.00 | -3.30 | 20.80 | 20.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 7 | 51.96 | 65.00 | 13.04 | 19.67 | 16.70 | 16.39 | 0.00 | 7.77 |
| MEAN_REVERT | kept | 47 | 71.94 | 65.00 | -6.94 | 20.31 | 18.03 | 15.54 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 211 | 54.45 | 65.00 | 10.55 | 19.97 | 16.63 | 15.80 | 3.59 | 9.98 |
| MOVER_AVWAP_SCALP | kept | 578 | 78.98 | 65.00 | -13.98 | 21.81 | 18.43 | 15.80 | 4.53 | 0.42 |
| MOVER_TREND_PULLBACK | filtered | 1594 | 55.28 | 63.49 | 8.21 | 19.80 | 18.40 | 15.80 | 4.42 | 18.20 |
| MOVER_TREND_PULLBACK | kept | 12475 | 76.90 | 65.00 | -11.90 | 20.30 | 18.76 | 15.80 | 4.47 | 0.94 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 78.40 | 65.00 | -13.40 | 20.00 | 20.00 | 20.00 | 6.00 | 14.80 |
| QUIET_COMPRESSION_BREAK | filtered | 138 | 51.42 | 65.00 | 13.58 | 21.59 | 19.85 | 20.00 | 0.00 | 5.27 |
| QUIET_COMPRESSION_BREAK | kept | 210 | 77.67 | 65.00 | -12.67 | 22.41 | 19.85 | 20.00 | 0.00 | -1.83 |
| SR_FLIP_RETEST | filtered | 978 | 57.74 | 64.33 | 6.59 | 20.59 | 19.83 | 15.72 | 1.31 | 10.67 |
| SR_FLIP_RETEST | kept | 2832 | 71.63 | 65.00 | -6.63 | 20.80 | 19.93 | 15.74 | 2.00 | 0.75 |
| TREND_PULLBACK_EMA | filtered | 6 | 61.70 | 65.00 | 3.30 | 20.10 | 18.30 | 16.00 | 4.00 | 13.80 |
| TREND_PULLBACK_EMA | kept | 105 | 79.99 | 65.00 | -14.99 | 19.64 | 19.63 | 17.51 | 5.33 | 2.15 |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 52.64 | 65.00 | 12.36 | 21.20 | 17.88 | 20.00 | 4.32 | 8.64 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 7 | 77.50 | 17.00 | 18.00 | 12.00 | 13.57 | 5.00 | 10.00 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 421 | 57.45 | 22.04 | 15.48 | 5.16 | 11.25 | 5.58 | 8.38 | 2.29 |
| DIVERGENCE_CONTINUATION | kept | 507 | 69.90 | 23.60 | 16.80 | 4.97 | 11.91 | 5.72 | 8.84 | 2.07 |
| FAILED_AUCTION_RECLAIM | filtered | 168 | 53.38 | 22.26 | 14.76 | 4.62 | 11.14 | 5.95 | 5.26 | 4.51 |
| FAILED_AUCTION_RECLAIM | kept | 395 | 70.50 | 22.72 | 14.77 | 4.59 | 10.48 | 5.99 | 7.42 | 4.61 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 36 | 55.97 | 22.17 | 14.00 | 8.67 | 11.94 | 5.83 | 7.65 | 2.47 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 288 | 71.33 | 23.24 | 14.33 | 5.35 | 13.26 | 5.41 | 8.09 | 1.65 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 37.00 | 25.00 | 14.00 | 3.00 | 14.00 | 8.00 | 8.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.30 | 25.00 | 14.00 | 3.00 | 14.00 | 5.00 | 7.30 | 0.00 |
| MEAN_REVERT | filtered | 7 | 51.96 | 23.86 | 16.86 | 3.43 | 12.00 | 8.00 | 4.16 | 0.00 |
| MEAN_REVERT | kept | 47 | 71.94 | 22.11 | 16.81 | 8.94 | 12.00 | 6.03 | 6.06 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 211 | 54.45 | 18.36 | 18.06 | 8.60 | 12.55 | 5.39 | 5.05 | 3.59 |
| MOVER_AVWAP_SCALP | kept | 578 | 78.98 | 19.97 | 18.02 | 8.62 | 13.75 | 5.83 | 8.70 | 4.53 |
| MOVER_TREND_PULLBACK | filtered | 1594 | 55.28 | 18.76 | 18.13 | 8.00 | 13.49 | 5.54 | 8.77 | 4.42 |
| MOVER_TREND_PULLBACK | kept | 12475 | 76.90 | 19.18 | 18.02 | 8.19 | 13.11 | 5.89 | 9.10 | 4.47 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 78.40 | 23.00 | 18.00 | 15.00 | 14.00 | 8.50 | 8.70 | 6.00 |
| QUIET_COMPRESSION_BREAK | filtered | 138 | 51.42 | 18.16 | 17.30 | 10.67 | 14.11 | 6.93 | 4.06 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 210 | 77.67 | 18.72 | 17.39 | 11.64 | 14.20 | 6.84 | 9.08 | 0.00 |
| SR_FLIP_RETEST | filtered | 978 | 57.74 | 18.03 | 17.02 | 4.60 | 12.54 | 6.59 | 8.33 | 1.31 |
| SR_FLIP_RETEST | kept | 2832 | 71.63 | 21.63 | 15.78 | 5.40 | 13.47 | 6.22 | 9.02 | 2.00 |
| TREND_PULLBACK_EMA | filtered | 6 | 61.70 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 10.00 | 4.00 |
| TREND_PULLBACK_EMA | kept | 105 | 79.99 | 21.96 | 18.00 | 7.60 | 13.96 | 6.12 | 9.69 | 5.33 |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 52.64 | 22.05 | 14.00 | 12.00 | 14.00 | 5.00 | 4.91 | 4.32 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 7 | 77.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 421 | 57.45 | 0.00 | 0.00 | 0.75 | 0.00 | 0.59 | 0.03 | 0.00 | 0.00 | **1.37** |
| DIVERGENCE_CONTINUATION | kept | 507 | 69.90 | 0.00 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.22** |
| FAILED_AUCTION_RECLAIM | filtered | 168 | 53.38 | 0.00 | 0.00 | 0.80 | 0.00 | 1.29 | 0.11 | 0.00 | 0.00 | **2.20** |
| FAILED_AUCTION_RECLAIM | kept | 395 | 70.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | **0.03** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 36 | 55.97 | 0.00 | 0.00 | 5.51 | 0.00 | 10.20 | 1.06 | 0.00 | 0.00 | **16.77** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 288 | 71.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.02 | 0.00 | 0.00 | **0.02** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 37.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 7 | 51.96 | 0.00 | 0.00 | 2.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.06** |
| MEAN_REVERT | kept | 47 | 71.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 211 | 54.45 | 0.00 | 0.00 | 1.43 | 0.00 | 0.00 | 0.03 | 0.00 | 0.82 | **2.28** |
| MOVER_AVWAP_SCALP | kept | 578 | 78.98 | 0.00 | 0.00 | 0.12 | 0.00 | 0.00 | 0.03 | 0.00 | 0.01 | **0.16** |
| MOVER_TREND_PULLBACK | filtered | 1594 | 55.28 | 0.13 | 0.00 | 1.26 | 0.00 | 1.85 | 0.11 | 0.00 | 0.00 | **3.35** |
| MOVER_TREND_PULLBACK | kept | 12475 | 76.90 | 0.00 | 0.00 | 0.35 | 0.00 | 0.18 | 0.02 | 0.00 | 0.00 | **0.55** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 78.40 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| QUIET_COMPRESSION_BREAK | filtered | 138 | 51.42 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.13 | 0.00 | 3.70 | **3.83** |
| QUIET_COMPRESSION_BREAK | kept | 210 | 77.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | **0.10** |
| SR_FLIP_RETEST | filtered | 978 | 57.74 | 0.00 | 0.00 | 0.59 | 0.00 | 1.35 | 0.05 | 0.00 | 0.04 | **2.03** |
| SR_FLIP_RETEST | kept | 2832 | 71.63 | 0.00 | 0.00 | 0.31 | 0.00 | 0.11 | 0.01 | 0.00 | 0.00 | **0.43** |
| TREND_PULLBACK_EMA | filtered | 6 | 61.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 105 | 79.99 | 0.00 | 0.00 | 0.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.96** |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 52.64 | 0.00 | 0.00 | 3.37 | 0.00 | 0.00 | 0.00 | 0.00 | 2.27 | **5.64** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=907 (22.2%) | WOULD_LOSE=1307 | WOULD_EXPIRE=1877 | pending (awaiting window)=909

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_edge:RANGE_FADE | 52 | 1.9% | 64.9 | 2.6 | +1.20 | **KEEP** |
| context_floor:FAILED_AUCTION_RECLAIM | 352 | 9.1% | 70.4 | 58.6 | +0.03 | **TUNE** |
| context_floor:QUIET_COMPRESSION_BREAK | 313 | 2.9% | 71.5 | 20.8 | +0.16 | **KEEP** |
| context_floor:TREND_PULLBACK_EMA | 44 | 84.1% | 9.2 | 46.5 | -0.85 | **DROP** |
| dispatch_cooldown | 7 | 0.0% | 6.3 | 0.0 | +0.91 | **INSUFFICIENT_SAMPLE** |
| dispatch_staleness_v2 | 281 | 48.0% | 81.5 | 72.5 | +0.03 | **TUNE** |
| level_still_in_play | 1354 | 22.7% | 327.8 | 147.5 | +0.13 | **KEEP** |
| min_confidence | 1460 | 24.1% | 964.2 | 471.3 | +0.34 | **KEEP** |
| quiet_scalp_block | 114 | 4.4% | 48.0 | 5.1 | +0.38 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 3 | 33.3% | 1.1 | 0.7 | +0.15 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 7 | 0.0% | 7.3 | 0.0 | +1.04 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_MEAN_REVERT | 64 | 32.8% | 43.3 | 28.7 | +0.23 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 40 | 17.5% | 29.7 | 18.1 | +0.29 | **KEEP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 81947 across 20 strategies; 1860 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 19256 | 70/19186/0 | 62% | +0.16 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MAJOR (+1.27R) | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.37R) |
| FAILED_AUCTION_RECLAIM | 13934 | 26/13908/0 | 53% | +0.02 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (-1.19R) |
| SR_FLIP_RETEST | 13205 | 2/13203/0 | 44% | -0.22 | OVERLAP/MARKDOWN/EXPANDED/BTC_RISING (+1.11R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.30R) |
| DIVERGENCE_CONTINUATION | 7747 | 8/7739/0 | 49% | -0.03 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (+1.61R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| QUIET_COMPRESSION_BREAK | 5754 | 0/5754/0 | 42% | -0.08 | ASIA/RANGE/NORMAL/BTC_RISING (+1.16R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| SHADOW_MEAN_REVERT | 3268 | 0/0/3268 | 40% | -0.01 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.04R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.03R) |
| LIQUIDITY_SWEEP_REVERSAL | 3152 | 9/3143/0 | 43% | -0.15 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.78R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.50R) |
| MEAN_REVERT | 3079 | 0/3079/0 | 80% | +0.58 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.14R) |
| SHADOW_RANGE_FADE | 3069 | 0/0/3069 | 41% | +0.25 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.27R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.96R) |
| SHADOW_FUNDING_FADE | 2368 | 0/0/2368 | 44% | -0.23 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL (+0.42R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-0.94R) |
| RANGE_FADE | 1915 | 0/1915/0 | 3% | -0.99 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | NY/QUIET/NORMAL/BTC_NEUTRAL (-1.22R) |
| VOLUME_SURGE_BREAKOUT | 1364 | 12/1352/0 | 42% | -0.01 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| TREND_PULLBACK_EMA | 1331 | 2/1329/0 | 52% | -0.12 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.73R) | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (-1.19R) |
| MOVER_AVWAP_SCALP | 1023 | 26/997/0 | 37% | -0.29 | NY/MARKUP/CASCADE/BTC_FALLING (+0.55R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-1.05R) |
| WHALE_MOMENTUM | 474 | 0/474/0 | 54% | -0.11 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 384 | 2/382/0 | 33% | -0.19 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.05R) |
| BREAKDOWN_SHORT | 299 | 7/292/0 | 59% | +0.33 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 252 | 0/0/252 | 46% | -0.24 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.00R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| POST_DISPLACEMENT_CONTINUATION | 67 | 0/67/0 | 90% | +0.75 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 6 | 1/5/0 | 50% | -0.24 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP` +1.78R (n=42, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.50R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.45R (n=17, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.45R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 37 | 49% / -0.21R | 37 | 54% / -0.02R | +0.19 | **ATR** |
| MEAN_REVERT | 250 | 58% / +0.13R | 250 | 56% / +0.25R | +0.12 | **ATR** |
| WHALE_MOMENTUM | 31 | 42% / -0.16R | 31 | 39% / -0.26R | -0.10 | **FIXED** |
| LIQUIDITY_SWEEP_REVERSAL | 399 | 48% / -0.16R | 399 | 52% / -0.07R | +0.09 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 39 | 38% / -0.03R | 39 | 41% / -0.12R | -0.09 | **FIXED** |
| SR_FLIP_RETEST | 1935 | 46% / -0.16R | 1935 | 49% / -0.08R | +0.08 | **ATR** |
| MOVER_AVWAP_SCALP | 92 | 43% / -0.09R | 92 | 49% / -0.02R | +0.07 | **ATR** |
| DIVERGENCE_CONTINUATION | 418 | 50% / -0.05R | 418 | 56% / -0.01R | +0.04 | **ATR** |
| RANGE_FADE | 147 | 4% / -1.01R | 147 | 5% / -0.97R | +0.04 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1704 | 47% / -0.09R | 1704 | 47% / -0.06R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 825 | 43% / -0.09R | 825 | 43% / -0.12R | -0.03 | **FIXED** |
| MOVER_TREND_PULLBACK | 2104 | 56% / +0.03R | 2104 | 58% / +0.04R | +0.01 | **ATR** |
| BREAKDOWN_SHORT | 11 | 27% / -0.26R | 11 | 27% / -0.27R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 7 | 14% / -0.71R | 7 | 43% / -0.21R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 4 | 75% / +0.10R | 4 | 75% / -0.13R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 71% / +0.23R | 7 | 71% / +0.04R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 1424 | 30% | -0.12R | 145 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 82 | 46% | -0.06R | 50 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 7 | 43% | +0.08R | 6 | MEASURING |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 399 | 26% / -4.70R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 2 | 0% / -2.41R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 631 | 41% / -0.90R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 383 | 37% / -1.09R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 11 | 18% / -5.30R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 147 | 22% / -6.78R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 127 | 50% / +0.66R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 71 | 32% / -4.42R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 9 | 11% / -9.42R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 17 | 18% / -4.66R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 16 | 50% / +0.38R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 2 | 0% / -1.19R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 2 | 0% / -1.49R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 2 | 0% / -1.31R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._

| Setup | Gate | n | WOULD_WIN% | EV/suppression (R) | Verdict |
|---|---|---:|---:|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | quiet_scalp_block | 4 | 100.0% | -0.96 | **INSUFFICIENT_SAMPLE** |
| DIVERGENCE_CONTINUATION | min_confidence | 163 | 71.2% | -0.86 | **DROP** |
| TREND_PULLBACK_EMA | context_floor:TREND_PULLBACK_EMA | 44 | 84.1% | -0.85 | **DROP** |
| DIVERGENCE_CONTINUATION | level_still_in_play | 78 | 65.4% | -0.43 | **DROP** |
| SR_FLIP_RETEST | dispatch_staleness_v2 | 29 | 72.4% | -0.22 | **DROP** |
| MOVER_AVWAP_SCALP | level_still_in_play | 73 | 13.7% | +0.03 | **TUNE** |
| FAILED_AUCTION_RECLAIM | context_floor:FAILED_AUCTION_RECLAIM | 352 | 9.1% | +0.03 | **TUNE** |
| LIQUIDITY_SWEEP_REVERSAL | level_still_in_play | 7 | 57.1% | +0.03 | **INSUFFICIENT_SAMPLE** |
| MOVER_TREND_PULLBACK | dispatch_staleness_v2 | 243 | 46.9% | +0.04 | **TUNE** |
| FAILED_AUCTION_RECLAIM | level_still_in_play | 11 | 0.0% | +0.08 | **INSUFFICIENT_SAMPLE** |
| QUIET_COMPRESSION_BREAK | min_confidence | 24 | 0.0% | +0.11 | **KEEP** |
| SHADOW_CASCADE_REVERSAL | shadow_unit:SHADOW_CASCADE_REVERSAL | 3 | 33.3% | +0.15 | **INSUFFICIENT_SAMPLE** |
| MOVER_TREND_PULLBACK | level_still_in_play | 530 | 17.2% | +0.16 | **KEEP** |
| QUIET_COMPRESSION_BREAK | context_floor:QUIET_COMPRESSION_BREAK | 313 | 2.9% | +0.16 | **KEEP** |
| LIQUIDITY_SWEEP_REVERSAL | dispatch_staleness_v2 | 5 | 0.0% | +0.19 | **INSUFFICIENT_SAMPLE** |
| SR_FLIP_RETEST | level_still_in_play | 655 | 23.1% | +0.19 | **KEEP** |
| QUIET_COMPRESSION_BREAK | quiet_scalp_block | 38 | 0.0% | +0.19 | **KEEP** |
| SHADOW_MEAN_REVERT | shadow_unit:SHADOW_MEAN_REVERT | 64 | 32.8% | +0.23 | **KEEP** |
| MOVER_TREND_PULLBACK | min_confidence | 748 | 25.1% | +0.28 | **KEEP** |
| SHADOW_RANGE_FADE | shadow_unit:SHADOW_RANGE_FADE | 40 | 17.5% | +0.29 | **KEEP** |
| FAILED_AUCTION_RECLAIM | min_confidence | 39 | 0.0% | +0.31 | **KEEP** |
| MOVER_TREND_PULLBACK | quiet_scalp_block | 4 | 0.0% | +0.31 | **INSUFFICIENT_SAMPLE** |
| FAILED_AUCTION_RECLAIM | quiet_scalp_block | 42 | 0.0% | +0.45 | **KEEP** |
| SR_FLIP_RETEST | quiet_scalp_block | 22 | 4.5% | +0.66 | **KEEP** |
| SR_FLIP_RETEST | min_confidence | 405 | 11.4% | +0.81 | **KEEP** |

- _sorted most-costly first: the top rows are gates whose suppressions lose more than they save on that specific path_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 23 · alerting: **6** · boot grace active: False
- **ALERT** `sar_alignment_crosscheck` — 146/769 disagreed (19.0%) (streak 34/6) (sustained 34 cycles)
- **ALERT** `sar_ledger_candles` — 313/330 unfetchable (95%); top cause: 15m history rolled off before the stamp; symbols: 1000BONKUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACHUSDT +58 more (streak 94/6) (sustained 94 cycles)
- **ALERT** `edge_reconciliation` — MOVER_AVWAP_SCALP realized−counterfactual=+0.40R (bound 0.3) (streak 94/6) (sustained 94 cycles)
- **ALERT** `mean_revert_emission` — 1574 detections since last emission (emitted_total=2) — and the blocked candidates measure +0.58R over n=3079, so the gating is COSTING us. Check gate rejections. (streak 32/6) (sustained 32 cycles)
- **ALERT** `tuned_variants` — 19 unexplained non-stamps (seen=2106 stamped=231 skipped=1856) (streak 21/6) (sustained 21 cycles)
- **ALERT** `auto_dispatch` — 9 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=10) (streak 42/3) (sustained 42 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | violating | 9 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=10) (streak 42/3) | 42 |
| btc_reference | ok | BTC ref 63749.10 | 0 |
| candle_coverage | ok | 98/105 symbols with ≥20 15m candles, 96/105 updated within 45m | 0 |
| context_emission_policy | ok | output +102 / upstream +31 | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.40R (bound 0.3) (streak 94/6) | 94 |
| emission_controller | ok | last cycle 961s ago; live_overrides=19 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=9 wasted_promotions=0 pruned=0 | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +14 / upstream +63 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 1574 detections since last emission (emitted_total=2) — and the blocked candidates measure +0.58R over n=3079, so the gating is COSTING us. Check gate rejections. (streak 32/6) | 32 |
| mean_revert_path | ok | output +199 / upstream +63 | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE counterfactuals measure -0.99R over n=1915 — emitting them would lose money | 0 |
| range_fade_path | ok | output +164 / upstream +63 | 0 |
| sar_alignment_crosscheck | violating | 146/769 disagreed (19.0%) (streak 34/6) | 34 |
| sar_exit_shadow | ok | output +14 / upstream +63 | 0 |
| sar_ledger_candles | violating | 313/330 unfetchable (95%); top cause: 15m history rolled off before the stamp; symbols: 1000BONKUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ACHUSDT +58 more (streak 94/6) | 94 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +110 / upstream +63 | 0 |
| suppression_audit | ok | output +63 / upstream +31 | 0 |
| tuned_variants | violating | 19 unexplained non-stamps (seen=2106 stamped=231 skipped=1856) (streak 21/6) | 21 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3054900`
- `Path funnel` emissions: `66`
- `Regime distribution` emissions: `66`
- `QUIET_SCALP_BLOCK` events: `449`
- `confidence_gate` events: `21025`
- `free_channel_post` events: `20`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **1**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 1 | 2085 | 2085 | 2085 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **20**

| Source | Count |
|---|---:|
| signal_close | 16 |
| regime_shift | 4 |

- By severity: HIGH=20

## Dependency readiness
- cvd: presence[present=440477] state[populated=440477] buckets[many=440477] sources[none] quality[none]
- funding_rate: presence[absent=65613, present=374864] state[empty=65613, populated=374864] buckets[few=374864, none=65613] sources[none] quality[none]
- liquidation_clusters: presence[absent=265901, present=174576] state[empty=265901, populated=174576] buckets[few=138172, none=265901, some=36404] sources[none] quality[none]
- oi_snapshot: presence[absent=62417, present=378060] state[empty=62417, populated=378060] buckets[few=91, many=377686, none=62417, some=283] sources[none] quality[none]
- order_book: presence[absent=129542, present=310935] state[populated=310935, unavailable=129542] buckets[few=310935, none=129542] sources[book_ticker=310935, unavailable=129542] quality[none=129542, top_of_book_only=310935]
- orderblocks: presence[absent=440477] state[empty=440477] buckets[none=440477] sources[not_implemented=440477] quality[none]
- recent_ticks: presence[present=440477] state[populated=440477] buckets[many=440477] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `7.27681303024292` sec
- Median create→first breach: `2080.2018200159073` sec
- Median create→terminal: `2085.3289835453033` sec
- Median first breach→terminal: `2.8739055395126343` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.1 | 2944.8358178138733 | 2947.512537956238 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -1.4035 | 6858.681059122086 | 6858.975305080414 |
| MOVER_TREND_PULLBACK | 12 | 12 | 0.0 | 75.0 | 0.0 | 0.0 | -0.6188 | 1795.058933019638 | 1801.7563120126724 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 10524 | 136 | 2065 | 0.0 | 0.0 | None | None | 8459 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2050 | 6 | 1805 | 0.0 | 0.0 | None | None | 245 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `266`
- Gating Δ: `-78807`
- No-generation Δ: `-520127`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": -5.3351, "current_avg_pnl": -1.4035, "current_win_rate": 0.0, "previous_avg_pnl": 3.9316, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.9884, "current_avg_pnl": -0.6188, "current_win_rate": 0.0, "previous_avg_pnl": -1.6072, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 52, "geometry_changed_delta": 0, "geometry_preserved_delta": 1003, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 179, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
