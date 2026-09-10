# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: FAILED_AUCTION_RECLAIM
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `8` sec (warning=False)
- Latest performance record age: `2643` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 194 | 194 | 136 | 3 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 11944 | 11944 | 10871 | 10 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 81411 | 81411 | 44 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 67032 | 67032 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 66693 | 63522 | 3494 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 67063 | 66014 | 1132 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 69616 | 69562 | 77 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 59906 | 59920 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 67153 | 67192 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 67204 | 65210 | 2803 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 86270 | 91307 | 1222 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 81457 | 72429 | 13757 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 69201 | 69201 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 67036 | 67056 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 66661 | 66592 | 94 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 68018 | 66536 | 1990 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 66224 | 66437 | 183 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 56994 | 53234 | 4031 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 57274 | 56966 | 379 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 81362 | 81389 | 15 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 59928 | 59899 | 51 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4662 | 4662 | 4191 | 6 | active-healthy (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 345 | 345 | 244 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 17 | 17 | 17 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 19012 | 19012 | 18834 | 23 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 5 | 5 | 5 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7177 | 7177 | 6701 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2841 | 2841 | 2193 | 45 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 36815 | 36815 | 29740 | 222 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 26 | 26 | 26 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 631 | 631 | 604 | 5 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 5363 | 5363 | 5266 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 892 | 892 | 813 | 6 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1577 | 1577 | 1463 | 16 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 64 | 64 | 50 | 4 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 583 | 583 | 375 | 5 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=81411): breakout_not_found=45890, basic_filters_failed=19636, move_not_fresh=10815, breakout_stale=3339, retest_proximity_failed=1540, volume_spike_missing=185, move_exhausted=4, missing_fvg_or_orderblock=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=67032): cls_disabled_merged_into_lsr=67032
- **EVAL::DIVERGENCE_CONTINUATION** (total=63522): cvd_divergence_failed=26197, h1_trend_not_aligned=15841, basic_filters_failed=13573, ema_alignment_reject=6901, retest_proximity_failed=658, missing_fvg_or_orderblock=352
- **EVAL::FAILED_AUCTION_RECLAIM** (total=66014): auction_not_detected=44189, basic_filters_failed=13297, reclaim_hold_failed=4432, tail_too_small=2531, regime_blocked=1499, rsi_reject=66
- **EVAL::FUNDING_EXTREME** (total=69562): funding_not_extreme=51218, basic_filters_failed=13412, missing_funding_rate=3577, ema_alignment_reject=677, rsi_reject=504, momentum_reject=92, cvd_divergence_failed=69, missing_fvg_or_orderblock=13
- **EVAL::LIQUIDATION_REVERSAL** (total=59920): cascade_threshold_not_met=44824, basic_filters_failed=14449, cvd_divergence_failed=359, rsi_reject=266, missing_fvg_or_orderblock=14, volume_spike_missing=8
- **EVAL::MA_CROSS_TREND_SHIFT** (total=67192): no_ma_cross=52616, basic_filters_failed=13587, ma_cross_htf_misaligned=778, ma_cross_cooldown=211
- **EVAL::MEAN_REVERT** (total=65210): no_extension=55413, basic_filters_failed=9797
- **EVAL::MOVER_AVWAP_SCALP** (total=91307): no_avwap_tag=38796, no_mover_leg=23725, basic_filters_failed=19873, avwap_slope_against=5263, avwap_reclaim_no_volume=2001, no_avwap_reclaim=1599, anchor_too_recent=50
- **EVAL::MOVER_TREND_PULLBACK** (total=72429): mover_run_too_small=32507, basic_filters_failed=19757, no_reclaim=16312, no_pullback_tag=3853
- **EVAL::OPENING_RANGE_BREAKOUT** (total=69201): feature_disabled=69201
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=67056): regime_blocked=42400, breakout_not_found=18598, basic_filters_failed=4440, adx_reject=1558, ema_alignment_reject=60
- **EVAL::QUIET_COMPRESSION_BREAK** (total=66592): compression_not_detected=29072, regime_blocked=26022, basic_filters_failed=8850, breakout_not_detected=2393, volume_confirmation_failed=242, rsi_reject=10, missing_fvg_or_orderblock=3
- **EVAL::RANGE_FADE** (total=66536): no_range_edge=56734, basic_filters_failed=9802
- **EVAL::SR_FLIP_RETEST** (total=66437): flip_close_not_confirmed=42813, basic_filters_failed=13278, long_break_volume_thin=3416, retest_out_of_zone=2101, h1_break_not_confirmed=2062, regime_blocked=1488, reclaim_hold_failed=618, long_acceptance_not_held=331, ema_alignment_reject=171, whipsaw_flip=86, wick_quality_failed=57, missing_fvg_or_orderblock=16
- **EVAL::STANDARD** (total=53234): momentum_reject=17507, adx_reject=10119, basic_filters_failed=7485, sweeps_not_detected=6864, macd_reject=5624, ema_alignment_reject=4556, htf_poi_unanchored=931, invalid_sl_geometry=88, rsi_reject=54, mtf_reject=6
- **EVAL::TREND_PULLBACK** (total=56966): h1_trend_not_aligned=16994, ema_alignment_reject=9885, h1_pullback_not_confirmed=7845, basic_filters_failed=7509, ema_not_tested_prev=5656, no_ema_reclaim_close=3976, body_conviction_fail=2196, rsi_reject=1637, prev_already_below_emas=403, no_prev_low_break=346, prev_already_above_emas=200, no_prev_high_break=166, momentum_flat=109, momentum_reject=23, ema21_not_tagged=20, missing_fvg_or_orderblock=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=81389): breakout_not_found=50011, basic_filters_failed=19633, move_not_fresh=7372, breakout_stale=3101, retest_proximity_failed=1015, volume_spike_missing=219, missing_fvg_or_orderblock=19, move_exhausted=19
- **EVAL::WHALE_MOMENTUM** (total=59899): momentum_reject=47362, recent_ticks_insufficient=8785, basic_filters_failed=3751, rsi_reject=1

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=18): execution:overextended=18
- **DIVERGENCE_CONTINUATION** (total=328): setup_compat:regime_VOLATILE_UNSUITABLE=316, setup_compat:regime_BREAKOUT_EXPANSION=12
- **FAILED_AUCTION_RECLAIM** (total=1330): setup_compat:regime_STRONG_TREND=708, execution:overextended=449, context_floor=142, setup_compat:regime_VOLATILE_UNSUITABLE=31
- **FUNDING_EXTREME_SIGNAL** (total=270): execution:trigger_not_confirmed=270
- **LIQUIDATION_REVERSAL** (total=17): execution:trigger_not_confirmed=17
- **LIQUIDITY_SWEEP_REVERSAL** (total=5547): setup_compat:regime_STRONG_TREND=1960, execution:trigger_not_confirmed=1920, execution:overextended=1667
- **MA_CROSS_TREND_SHIFT** (total=2): setup_compat:regime_CLEAN_RANGE=1, setup_compat:regime_DIRTY_RANGE=1
- **MEAN_REVERT** (total=4156): setup_compat:regime_STRONG_TREND=2227, setup_compat:regime_WEAK_TREND=1377, execution:overextended=552
- **MOVER_AVWAP_SCALP** (total=1600): execution:overextended=1329, entry_quality=146, execution:trigger_not_confirmed=125
- **MOVER_TREND_PULLBACK** (total=14942): execution:trigger_not_confirmed=8404, execution:overextended=5682, entry_quality=856
- **QUIET_COMPRESSION_BREAK** (total=21): execution:trigger_not_confirmed=21
- **RANGE_FADE** (total=3221): setup_compat:regime_STRONG_TREND=1672, setup_compat:regime_WEAK_TREND=798, execution:overextended=500, setup_compat:regime_VOLATILE_UNSUITABLE=251
- **TREND_PULLBACK_EMA** (total=1330): setup_compat:regime_CLEAN_RANGE=700, setup_compat:regime_DIRTY_RANGE=551, entry_quality=62, setup_compat:regime_VOLATILE_UNSUITABLE=17
- **VOLUME_SURGE_BREAKOUT** (total=1): execution:overextended=1
- **WHALE_MOMENTUM** (total=289): execution:trigger_not_confirmed=206, execution:overextended=44, context_floor=39

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 184637 | 43.3% |
| TRENDING_DOWN | 95863 | 22.5% |
| TRENDING_UP | 68444 | 16.0% |
| QUIET | 62077 | 14.5% |
| VOLATILE | 15711 | 3.7% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **63**
- Average confidence gap to threshold: **11.24** (samples=63) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: DOTUSDT=24, BTCUSDT=13, 1000PEPEUSDT=8, LTCUSDT=5, ETHUSDT=5, BCHUSDT=3, FFUSDT=2, XLMUSDT=1, LINKUSDT=1, ADAUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 48 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 3 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 211 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 5 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 102 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 17 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 8 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 6 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 9 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 49 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 29 |
| MEAN_REVERT | kept | min_confidence_pass | 3 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 134 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 208 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1025 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 28 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1951 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 21 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 5 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 14 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 4 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 36 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 4 |
| WHALE_MOMENTUM | filtered | min_confidence | 31 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 14 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 48 | 55.70 | 64.00 | 8.30 | 21.75 | 17.63 | 20.00 | 5.00 | 25.04 |
| BREAKDOWN_SHORT | kept | 3 | 71.33 | 65.00 | -6.33 | 19.50 | 16.57 | 20.00 | 4.00 | 3.67 |
| DIVERGENCE_CONTINUATION | filtered | 216 | 59.12 | 64.65 | 5.53 | 20.68 | 19.86 | 16.90 | 1.05 | 9.54 |
| DIVERGENCE_CONTINUATION | kept | 102 | 71.04 | 65.00 | -6.04 | 20.66 | 19.58 | 17.96 | 0.80 | 0.76 |
| FAILED_AUCTION_RECLAIM | filtered | 25 | 57.39 | 63.24 | 5.85 | 21.64 | 16.56 | 20.00 | 3.68 | 0.40 |
| FAILED_AUCTION_RECLAIM | kept | 6 | 68.68 | 65.00 | -3.68 | 21.32 | 19.22 | 20.00 | 3.00 | 2.98 |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 46.94 | 61.00 | 14.06 | 20.20 | 16.30 | 17.00 | 1.67 | 8.56 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 75.80 | 65.00 | -10.80 | 18.85 | 13.75 | 20.00 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 50 | 51.02 | 63.64 | 12.62 | 21.28 | 18.30 | 17.29 | 0.80 | 19.96 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 29 | 70.32 | 65.00 | -5.32 | 20.96 | 18.78 | 17.61 | 2.03 | -0.22 |
| MEAN_REVERT | kept | 3 | 70.43 | 65.00 | -5.43 | 21.20 | 18.17 | 16.87 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 134 | 59.26 | 64.19 | 4.93 | 19.99 | 15.71 | 15.80 | 3.89 | 9.71 |
| MOVER_AVWAP_SCALP | kept | 208 | 82.76 | 65.00 | -17.76 | 19.49 | 15.25 | 15.80 | 4.09 | 2.17 |
| MOVER_TREND_PULLBACK | filtered | 1053 | 55.58 | 64.60 | 9.02 | 20.54 | 18.68 | 15.80 | 4.18 | 18.67 |
| MOVER_TREND_PULLBACK | kept | 1951 | 76.41 | 65.00 | -11.41 | 19.87 | 18.43 | 15.80 | 4.20 | 1.04 |
| QUIET_COMPRESSION_BREAK | filtered | 21 | 59.45 | 65.00 | 5.55 | 23.37 | 18.18 | 20.00 | 0.00 | 16.23 |
| QUIET_COMPRESSION_BREAK | kept | 5 | 76.92 | 65.00 | -11.92 | 20.96 | 19.56 | 20.00 | 0.00 | 2.16 |
| SR_FLIP_RETEST | kept | 14 | 71.29 | 65.00 | -6.29 | 20.23 | 20.00 | 16.43 | 1.93 | 0.24 |
| TREND_PULLBACK_EMA | filtered | 4 | 63.00 | 65.00 | 2.00 | 19.97 | 20.00 | 15.90 | 4.50 | 5.00 |
| TREND_PULLBACK_EMA | kept | 36 | 79.04 | 65.00 | -14.04 | 20.33 | 19.87 | 18.01 | 5.31 | 0.78 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 73.70 | 65.00 | -8.70 | 18.95 | 16.67 | 20.00 | 5.25 | 3.15 |
| WHALE_MOMENTUM | filtered | 31 | 57.46 | 61.52 | 4.06 | 20.84 | 17.29 | 17.00 | 0.00 | 11.74 |
| WHALE_MOMENTUM | kept | 14 | 65.69 | 65.00 | -0.69 | 20.60 | 15.60 | 17.00 | 0.00 | 10.51 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 48 | 55.70 | 25.00 | 18.00 | 12.00 | 12.44 | 5.00 | 3.30 | 5.00 |
| BREAKDOWN_SHORT | kept | 3 | 71.33 | 17.00 | 14.00 | 13.00 | 12.00 | 5.00 | 10.00 | 4.00 |
| DIVERGENCE_CONTINUATION | filtered | 216 | 59.12 | 23.81 | 14.34 | 4.39 | 11.68 | 5.28 | 8.17 | 1.05 |
| DIVERGENCE_CONTINUATION | kept | 102 | 71.04 | 23.12 | 15.16 | 6.65 | 12.95 | 5.08 | 8.57 | 0.80 |
| FAILED_AUCTION_RECLAIM | filtered | 25 | 57.39 | 23.40 | 16.56 | 3.60 | 12.76 | 5.60 | 6.59 | 3.68 |
| FAILED_AUCTION_RECLAIM | kept | 6 | 68.68 | 20.67 | 16.00 | 7.00 | 13.50 | 6.17 | 5.33 | 3.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 46.94 | 25.00 | 8.00 | 3.00 | 15.89 | 9.17 | 7.78 | 1.67 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 75.80 | 21.00 | 20.00 | 4.50 | 13.50 | 5.00 | 7.80 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 50 | 51.02 | 23.24 | 14.64 | 4.38 | 13.82 | 6.85 | 7.25 | 0.80 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 29 | 70.32 | 23.21 | 14.41 | 6.10 | 11.90 | 5.84 | 6.92 | 2.03 |
| MEAN_REVERT | kept | 3 | 70.43 | 22.33 | 18.00 | 6.00 | 13.00 | 5.00 | 6.10 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 134 | 59.26 | 17.33 | 18.00 | 10.70 | 13.91 | 6.16 | 6.04 | 3.89 |
| MOVER_AVWAP_SCALP | kept | 208 | 82.76 | 20.12 | 18.29 | 13.17 | 14.38 | 6.43 | 8.73 | 4.09 |
| MOVER_TREND_PULLBACK | filtered | 1053 | 55.58 | 18.58 | 18.00 | 7.69 | 11.61 | 5.77 | 8.50 | 4.18 |
| MOVER_TREND_PULLBACK | kept | 1951 | 76.41 | 19.61 | 18.05 | 7.87 | 12.67 | 6.02 | 9.09 | 4.20 |
| QUIET_COMPRESSION_BREAK | filtered | 21 | 59.45 | 19.67 | 18.00 | 12.86 | 14.14 | 5.93 | 5.09 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 5 | 76.92 | 21.80 | 18.00 | 12.00 | 14.00 | 6.40 | 6.88 | 0.00 |
| SR_FLIP_RETEST | kept | 14 | 71.29 | 21.57 | 18.00 | 3.86 | 14.00 | 5.21 | 8.88 | 1.93 |
| TREND_PULLBACK_EMA | filtered | 4 | 63.00 | 25.00 | 18.00 | 7.50 | 14.00 | 5.00 | 9.00 | 4.50 |
| TREND_PULLBACK_EMA | kept | 36 | 79.04 | 21.47 | 18.00 | 7.54 | 14.08 | 7.07 | 8.77 | 5.31 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 73.70 | 25.00 | 16.00 | 13.50 | 12.50 | 6.25 | 5.85 | 5.25 |
| WHALE_MOMENTUM | filtered | 31 | 57.46 | 19.26 | 17.03 | 7.74 | 11.10 | 5.53 | 8.54 | 0.00 |
| WHALE_MOMENTUM | kept | 14 | 65.69 | 24.29 | 18.00 | 5.36 | 12.93 | 6.32 | 9.31 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 48 | 55.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |
| BREAKDOWN_SHORT | kept | 3 | 71.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 216 | 59.12 | 0.00 | 0.00 | 0.89 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | **0.92** |
| DIVERGENCE_CONTINUATION | kept | 102 | 71.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 25 | 57.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 6 | 68.68 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 46.94 | 0.00 | 0.00 | 3.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.56** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 75.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 50 | 51.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.36 | 0.00 | 0.00 | **0.36** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 29 | 70.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 3 | 70.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 134 | 59.26 | 0.00 | 0.00 | 0.00 | 0.00 | 1.52 | 0.07 | 0.00 | 0.00 | **1.59** |
| MOVER_AVWAP_SCALP | kept | 208 | 82.76 | 0.07 | 0.00 | 0.00 | 0.00 | 1.10 | 0.03 | 0.00 | 0.03 | **1.23** |
| MOVER_TREND_PULLBACK | filtered | 1053 | 55.58 | 0.27 | 0.00 | 0.25 | 0.00 | 0.47 | 0.16 | 0.00 | 0.00 | **1.15** |
| MOVER_TREND_PULLBACK | kept | 1951 | 76.41 | 0.07 | 0.00 | 0.06 | 0.00 | 0.08 | 0.12 | 0.00 | 0.00 | **0.33** |
| QUIET_COMPRESSION_BREAK | filtered | 21 | 59.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 4.11 | **4.11** |
| QUIET_COMPRESSION_BREAK | kept | 5 | 76.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.16 | **2.16** |
| SR_FLIP_RETEST | kept | 14 | 71.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.86 | 0.00 | 0.00 | 0.00 | **0.86** |
| TREND_PULLBACK_EMA | filtered | 4 | 63.00 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| TREND_PULLBACK_EMA | kept | 36 | 79.04 | 0.00 | 0.00 | 0.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.89** |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 73.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.90 | **0.90** |
| WHALE_MOMENTUM | filtered | 31 | 57.46 | 0.00 | 0.00 | 0.00 | 0.00 | 0.93 | 0.00 | 0.00 | 0.00 | **0.93** |
| WHALE_MOMENTUM | kept | 14 | 65.69 | 0.00 | 0.00 | 0.00 | 0.00 | 0.51 | 0.00 | 0.00 | 0.00 | **0.51** |

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
- Outcomes recorded: **84193 held of 200489 seen** across 21 strategies; 1878 cells past the sample floor; **808 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 33147 | 422/32725/0 | 44% | -0.15 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MIDCAP (+1.17R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.15R) |
| MOVER_AVWAP_SCALP | 10382 | 120/10262/0 | 41% | -0.25 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 6440 | 66/6374/0 | 43% | -0.18 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 4935 | 26/4909/0 | 56% | +0.09 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | OVERLAP/MARKDOWN/CASCADE/BTC_RISING (-1.17R) |
| SHADOW_MEAN_REVERT | 4530 | 0/0/4530 | 44% | -0.07 | ASIA/RANGE/NORMAL/BTC_RISING (+0.25R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.09R) |
| TREND_PULLBACK_EMA | 4127 | 16/4111/0 | 46% | -0.16 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.18R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.28R) |
| QUIET_COMPRESSION_BREAK | 3909 | 161/3748/0 | 47% | -0.10 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+0.86R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_RANGE_FADE | 3818 | 0/0/3818 | 37% | -0.07 | ASIA/MARKDOWN/NORMAL/BTC_FALLING (+0.36R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.03R) |
| SHADOW_FUNDING_FADE | 3100 | 0/0/3100 | 37% | -0.37 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-1.01R) |
| WHALE_MOMENTUM | 2184 | 2/2182/0 | 39% | -0.38 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 2147 | 30/2117/0 | 39% | -0.24 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.21R) |
| MEAN_REVERT | 1335 | 20/1315/0 | 60% | +0.12 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 986 | 2/984/0 | 30% | -0.47 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.37R) |
| VOLUME_SURGE_BREAKOUT | 962 | 0/962/0 | 48% | +0.01 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.16R) |
| SR_FLIP_RETEST | 818 | 2/816/0 | 46% | -0.25 | NY/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.77R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 520 | 0/0/520 | 56% | +0.00 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | ASIA/MARKUP/CASCADE/BTC_NEUTRAL (-0.33R) |
| BREAKDOWN_SHORT | 305 | 18/287/0 | 45% | -0.07 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.03R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
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
| FUNDING_EXTREME_SIGNAL | 105 | 32% / -0.44R | 105 | 48% / -0.16R | +0.28 | **ATR** |
| TREND_PULLBACK_EMA | 347 | 47% / -0.18R | 347 | 56% / -0.04R | +0.15 | **ATR** |
| SR_FLIP_RETEST | 98 | 47% / -0.29R | 98 | 49% / -0.17R | +0.12 | **ATR** |
| RANGE_FADE | 20 | 50% / +0.20R | 20 | 50% / +0.10R | -0.11 | **FIXED** |
| WHALE_MOMENTUM | 262 | 42% / -0.33R | 262 | 44% / -0.23R | +0.11 | **ATR** |
| MOVER_AVWAP_SCALP | 802 | 45% / -0.19R | 802 | 50% / -0.09R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 540 | 43% / -0.19R | 540 | 46% / -0.10R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 4992 | 51% / -0.09R | 4992 | 55% / -0.01R | +0.08 | **ATR** |
| MA_CROSS_TREND_SHIFT | 16 | 31% / -0.25R | 16 | 31% / -0.19R | +0.06 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 66 | 45% / -0.05R | 66 | 52% / -0.03R | +0.03 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 438 | 53% / -0.17R | 438 | 56% / -0.15R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 645 | 47% / -0.15R | 645 | 47% / -0.15R | -0.01 | **FIXED** |
| DIVERGENCE_CONTINUATION | 505 | 54% / +0.01R | 505 | 60% / -0.00R | -0.01 | **FIXED** |
| BREAKDOWN_SHORT | 22 | 32% / -0.14R | 22 | 32% / -0.14R | +0.00 | **ATR** |
| MEAN_REVERT | 108 | 58% / +0.06R | 108 | 56% / +0.06R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 13 | 31% / -0.46R | 13 | 54% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 7378 | 31% | -0.15R | 295 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 802 | 48% | -0.08R | 176 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 43 | 53% | -0.07R | 35 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 100 | 33% / -0.29R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 611 | 37% / -0.08R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 6370 | 37% / -0.10R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 984 | 36% / -0.07R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 428 | 37% / -0.07R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 560 | 42% / +0.12R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 453 | 38% / -0.03R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 431 | 46% / -0.06R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 90 | 29% / -0.43R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 120 | 30% / -0.61R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 87 | 54% / +0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 42 | 40% / -0.12R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 18 | 44% / +0.28R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 97 | 34% / -0.35R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 22 | 14% / -0.66R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 17 | 41% / -0.06R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 8 | 38% / -0.01R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **8** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×221]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 164/6) (sustained 164 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 13/6) (sustained 13 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.43R (bound 0.3) (streak 164/6) (sustained 164 cycles)
- **ALERT** `mean_revert_emission` — 256 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure +0.11R over n=1315, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 18/6) (sustained 18 cycles)
- **ALERT** `range_fade_emission` — 3121 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=300, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 164/6) (sustained 164 cycles)
- **ALERT** `tuned_variants` — 39 non-stamps — atr_arm_uncomputable=39 (seen=2026 stamped=332 skipped=1655) (streak 135/6) (sustained 135 cycles)
- **ALERT** `auto_dispatch` — 37 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=76) (streak 156/3) (sustained 156 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 164/3) (sustained 164 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 22106717 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 164/3) | 164 |
| ai_governor_live_arms | ok | 12 arms current, none stalled; covering 63/63 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 43 arms current, none stalled; covering 826/826 signals (100%) | 0 |
| auto_dispatch | violating | 37 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=76) (streak 156/3) | 156 |
| btc_reference | ok | BTC ref 78376.20 | 0 |
| candle_coverage | ok | 98/98 symbols with ≥20 15m candles, 98/98 updated within 45m [fresh=98; 73 Tier-1 futures + 25 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 460 dup bars, 0 undedupable; ws 0 out-of-order, 109 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 6 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +10 / upstream +22 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1271/1288 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 13 of 149 open dark rows are not being advanced (worst: REUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 73/120) | 73 |
| dark_sar_arms | ok | no open arms; covering 1260/1277 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 4438124 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.43R (bound 0.3) (streak 164/6) | 164 |
| emission_controller | ok | last cycle 0s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×221]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 164/6) | 164 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 13/6) | 13 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +5 / upstream +126 | 0 |
| indicator_cache_key | ok | 47225 frozen value(s) avoided; 114997 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 256 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure +0.11R over n=1315, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 18/6) | 18 |
| mean_revert_path | violating | upstream +126 but output +0 (streak 2/72) | 2 |
| mover_admission_metadata | ok | 897 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 25 held, 25 with scan counts, 22 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2942 rows held, 1231412 evicted (sampled: execution:trigger_not_confirmed 400/444937, execution:overextended 400/420326, setup_compat:regime_STRONG_TREND 400/179956) | 0 |
| price_action_lane | ok | 275379 evaluated, 452 emitted; layer1 452 stamped / 0 blind; cooldown=36204, delta_opposed=21148, no_footprint=118996, no_opposing_target=499, no_sweep=79025, rr_below_floor=19055 | 0 |
| promoted_pair_integrity | ok | 25/25 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 3121 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=300, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 164/6) | 164 |
| range_fade_path | ok | output +28 / upstream +126 | 0 |
| sar_alignment_crosscheck | ok | 195/8639 disagreed (2.3%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +126 | 0 |
| sar_hold_arm | ok | 1430 held arms settled, 198 unscored, 42 still walking (41 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 11/58 unfetchable (19%); top cause: gap or duplicate bar in the 15m window; symbols: ETHFIUSDT, MIRAUSDT, ZENUSDT | 0 |
| sar_live_arms | ok | 42 arms current, none stalled; covering 835/835 signals (100%) | 0 |
| sar_refresh_budget | ok | 7 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 4 resolved, 43 still mid-window | 0 |
| scan_cycle | ok | last 59.47s, worst 200.27s over 2926 lifetime cycles; lifetime 67 over 60s, 5 over 120s; recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 1.61s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 124626 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 11m ago | 0 |
| snapshot_writer | ok | last cycle 12s ago (0.24s to run, worst 109.79s), 431 overrun(s) of 3328 cycles, TTL 900s; slowest signals=0.07s, data_intake=0.05s, activity=0.05s | 0 |
| stale_tf_scoring | violating | new stale-TF events: scored 21x, gate reads 0x, withheld 21x (lifetime scored 26x; refusal ARMED); last BEATUSDT age=3117.7s (streak 2/6) | 2 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +18 / upstream +126 | 0 |
| structural_snap | ok | 4855/4855 measured, 15 blind, 0 levels moved (refusals: redetect_cooldown=210) | 0 |
| structural_veto_lane | ok | 500 stamped; 0 with no readable level book, 13 with clear air ahead, 378 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +126 / upstream +22 | 0 |
| tuned_variants | violating | 39 non-stamps — atr_arm_uncomputable=39 (seen=2026 stamped=332 skipped=1655) (streak 135/6) | 135 |

Fail-open exception counters (nonzero sites):
- `feature_liveness.probe.footprint_bars`: 1 — last: RuntimeError: deque mutated during iteration
- `llm_client.google`: 5 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2072650`
- `Path funnel` emissions: `48`
- `Regime distribution` emissions: `48`
- `QUIET_SCALP_BLOCK` events: `63`
- `confidence_gate` events: `3968`
- `free_channel_post` events: `62`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **2**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 1 | 2081 | 2081 | 2081 | 0 |
| futures_liq | 1 | 14661 | 14661 | 14661 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **62**

| Source | Count |
|---|---:|
| signal_close | 58 |
| regime_shift | 4 |

- By severity: HIGH=62

## Dependency readiness
- cvd: presence[present=344301] state[populated=344301] buckets[many=344301] sources[none] quality[none]
- funding_rate: presence[absent=57846, present=286455] state[empty=57846, populated=286455] buckets[few=286455, none=57846] sources[none] quality[none]
- liquidation_clusters: presence[absent=185149, present=159152] state[empty=185149, populated=159152] buckets[few=127649, none=185149, some=31503] sources[none] quality[none]
- oi_snapshot: presence[absent=55819, present=288482] state[empty=55819, populated=288482] buckets[many=288482, none=55819] sources[none] quality[none]
- order_book: presence[absent=111828, present=232473] state[populated=232473, unavailable=111828] buckets[few=232473, none=111828] sources[book_ticker=232473, unavailable=111828] quality[none=111828, top_of_book_only=232473]
- orderblocks: presence[absent=344301] state[empty=344301] buckets[none=344301] sources[measured_dark=344301] quality[none]
- recent_ticks: presence[present=344301] state[populated=344301] buckets[many=344301] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.901026010513306` sec
- Median create→first breach: `3989.96970140934` sec
- Median create→terminal: `3994.90172791481` sec
- Median first breach→terminal: `2.933281421661377` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 4 | 4 | 1.2653243625592911 | 1.4462957304888269 | 0.8896562081499897 | 0 | 4 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 1.5221346240710587 | 2.5288478687355083 | 0.636812055340341 | 0 | 2 |
| MEAN_REVERT | 1 | 1 | 0.7463234583647407 | 0.6525488032006618 | 1.1437051982995405 | 1 | 0 |
| MOVER_AVWAP_SCALP | 8 | 8 | 1.9067093512175255 | 2.101003833535545 | 0.8562275557118081 | 3 | 5 |
| MOVER_TREND_PULLBACK | 35 | 35 | 4.885682971416697 | 3.0 | 1.6285609904722325 | 28 | 7 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 1.1059016248284554 | 1.3374116607773883 | 0.9999999995418676 | 0 | 2 |
| SR_FLIP_RETEST | 1 | 1 | 1.8632856413872583 | 1.8632856426210578 | 0.9999999993378367 | 0 | 0 |
| TREND_PULLBACK_EMA | 2 | 2 | 2.5593481001094984 | 3.0 | 0.8531160333698328 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 4 | 4 | 50.0 | 25.0 | 50.0 | 0.0 | 0.5975 | 11472.36008155346 | 11485.13449048996 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -2.3479 | 1823.2732590436935 | 1824.7536165714264 |
| MEAN_REVERT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.1195 | 10611.024775028229 | 10617.372600078583 |
| MOVER_AVWAP_SCALP | 8 | 8 | 25.0 | 62.5 | 25.0 | 0.0 | -0.7947 | 7915.824864983559 | 7919.469165921211 |
| MOVER_TREND_PULLBACK | 35 | 35 | 34.3 | 37.1 | 34.3 | 0.0 | 0.8685 | 2354.8938739299774 | 2357.024801969528 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 20.0 | 20.0 | 20.0 | 0.0 | 0.2135 | 25354.51135110855 | 25358.35861992836 |
| SR_FLIP_RETEST | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1956.1856100559235 | 1957.1042129993439 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -1.5 | 3966.9659435749054 | 3972.1272025108337 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 892 | 6 | 813 | 0.0 | 0.0 | 1956.1856100559235 | 1957.1042129993439 | 79 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1577 | 16 | 1463 | 0.0 | 50.0 | 3966.9659435749054 | 3972.1272025108337 | 114 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `62`
- Gating Δ: `-5556`
- No-generation Δ: `-172222`
- Fast failures Δ: `-1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.1735, "current_avg_pnl": 0.5975, "current_win_rate": 50.0, "previous_avg_pnl": 0.424, "previous_win_rate": 40.0, "win_rate_delta": 10.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -3.5397, "current_avg_pnl": -2.3479, "current_win_rate": 0.0, "previous_avg_pnl": 1.1918, "previous_win_rate": 66.7, "win_rate_delta": -66.7}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.5698, "current_avg_pnl": -0.7947, "current_win_rate": 25.0, "previous_avg_pnl": -1.3645, "previous_win_rate": 11.1, "win_rate_delta": 13.9}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.6597, "current_avg_pnl": 0.8685, "current_win_rate": 34.3, "previous_avg_pnl": 0.2088, "previous_win_rate": 29.0, "win_rate_delta": 5.3}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.4486, "current_avg_pnl": 0.2135, "current_win_rate": 20.0, "previous_avg_pnl": -0.2351, "previous_win_rate": 16.7, "win_rate_delta": 3.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": -182, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 1956.19, "median_terminal_delta_sec": 1957.1, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": -122, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 3966.97, "median_terminal_delta_sec": 3972.13, "sl_rate_delta": 50.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **FAILED_AUCTION_RECLAIM**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
