# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: QUIET_COMPRESSION_BREAK
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `7` sec (warning=False)
- Latest performance record age: `1719` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 40 | 40 | 40 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 8722 | 8722 | 7868 | 11 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 60028 | 60034 | 20 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 58544 | 58544 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 58078 | 56160 | 2357 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 58585 | 58041 | 609 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 59624 | 59486 | 165 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 50797 | 50822 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 58658 | 58703 | 6 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 58716 | 56853 | 2629 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 63899 | 68661 | 563 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 60066 | 56141 | 7667 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 59314 | 59314 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 58553 | 58575 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 58041 | 58022 | 53 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 59492 | 58275 | 1741 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 57708 | 57711 | 290 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 49340 | 46220 | 3450 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 49686 | 49426 | 370 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 59971 | 60013 | 1 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 50827 | 50855 | 4 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2691 | 2691 | 2462 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 869 | 869 | 393 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15370 | 15370 | 15256 | 8 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 12 | 12 | 6 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 5883 | 5883 | 5249 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1429 | 1429 | 596 | 45 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 21632 | 21632 | 13675 | 230 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 328 | 328 | 182 | 27 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 4233 | 4233 | 3262 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 829 | 829 | 454 | 9 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1755 | 1755 | 1403 | 24 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 18 | 18 | 16 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 68 | 68 | 12 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=60034): breakout_not_found=28837, basic_filters_failed=20703, move_not_fresh=7005, breakout_stale=1668, volume_spike_missing=1122, retest_proximity_failed=693, move_exhausted=3, missing_fvg_or_orderblock=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=58544): cls_disabled_merged_into_lsr=58544
- **EVAL::DIVERGENCE_CONTINUATION** (total=56160): cvd_divergence_failed=22902, basic_filters_failed=18637, h1_trend_not_aligned=9835, ema_alignment_reject=3916, retest_proximity_failed=658, missing_fvg_or_orderblock=212
- **EVAL::FAILED_AUCTION_RECLAIM** (total=58041): auction_not_detected=33521, basic_filters_failed=18089, reclaim_hold_failed=2729, tail_too_small=2070, regime_blocked=1585, rsi_reject=47
- **EVAL::FUNDING_EXTREME** (total=59486): funding_not_extreme=36798, basic_filters_failed=11492, missing_funding_rate=9266, ema_alignment_reject=1111, rsi_reject=541, cvd_divergence_failed=157, momentum_reject=109, missing_fvg_or_orderblock=12
- **EVAL::LIQUIDATION_REVERSAL** (total=50822): cascade_threshold_not_met=31459, basic_filters_failed=18421, cvd_divergence_failed=602, rsi_reject=327, missing_fvg_or_orderblock=12, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=58703): no_ma_cross=39316, basic_filters_failed=18672, ma_cross_cooldown=437, ma_cross_htf_misaligned=278
- **EVAL::MEAN_REVERT** (total=56853): no_extension=48514, basic_filters_failed=8339
- **EVAL::MOVER_AVWAP_SCALP** (total=68661): no_avwap_tag=25387, basic_filters_failed=21085, no_mover_leg=14838, avwap_slope_against=4538, avwap_reclaim_no_volume=1796, no_avwap_reclaim=983, anchor_too_recent=34
- **EVAL::MOVER_TREND_PULLBACK** (total=56141): mover_run_too_small=23205, basic_filters_failed=20909, no_reclaim=10154, no_pullback_tag=1873
- **EVAL::OPENING_RANGE_BREAKOUT** (total=59314): feature_disabled=59314
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=58575): regime_blocked=42570, breakout_not_found=9337, basic_filters_failed=5529, adx_reject=1093, ema_alignment_reject=46
- **EVAL::QUIET_COMPRESSION_BREAK** (total=58022): compression_not_detected=23261, regime_blocked=17445, basic_filters_failed=12540, breakout_not_detected=3700, volume_reject=769, volume_confirmation_failed=282, rsi_reject=18, missing_fvg_or_orderblock=7
- **EVAL::RANGE_FADE** (total=58275): no_range_edge=49926, basic_filters_failed=8349
- **EVAL::SR_FLIP_RETEST** (total=57711): flip_close_not_confirmed=33670, basic_filters_failed=18041, long_break_volume_thin=1658, regime_blocked=1572, retest_out_of_zone=1085, h1_break_not_confirmed=733, reclaim_hold_failed=428, whipsaw_flip=288, long_acceptance_not_held=107, ema_alignment_reject=60, wick_quality_failed=55, missing_fvg_or_orderblock=14
- **EVAL::STANDARD** (total=46220): momentum_reject=13154, adx_reject=10638, sweeps_not_detected=7800, basic_filters_failed=6004, macd_reject=4431, ema_alignment_reject=3356, htf_poi_unanchored=734, rsi_reject=54, invalid_sl_geometry=48, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=49426): h1_trend_not_aligned=14683, basic_filters_failed=8965, h1_pullback_not_confirmed=8267, ema_alignment_reject=7506, ema_not_tested_prev=3298, no_ema_reclaim_close=3078, body_conviction_fail=1782, rsi_reject=837, prev_already_below_emas=462, no_prev_low_break=296, prev_already_above_emas=82, momentum_flat=62, no_prev_high_break=58, ema21_not_tagged=29, missing_fvg_or_orderblock=11, momentum_reject=10
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=60013): breakout_not_found=29752, basic_filters_failed=20697, move_not_fresh=5367, breakout_stale=2123, volume_spike_missing=1127, retest_proximity_failed=923, move_exhausted=16, missing_fvg_or_orderblock=8
- **EVAL::WHALE_MOMENTUM** (total=50855): momentum_reject=36668, recent_ticks_insufficient=9165, basic_filters_failed=5022

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=6): execution:overextended=6
- **DIVERGENCE_CONTINUATION** (total=395): setup_compat:regime_VOLATILE_UNSUITABLE=376, setup_compat:regime_BREAKOUT_EXPANSION=15, execution:overextended=4
- **FAILED_AUCTION_RECLAIM** (total=768): setup_compat:regime_STRONG_TREND=388, execution:overextended=343, context_floor=37
- **FUNDING_EXTREME_SIGNAL** (total=756): execution:trigger_not_confirmed=741, context_floor=15
- **LIQUIDATION_REVERSAL** (total=1): execution:trigger_not_confirmed=1
- **LIQUIDITY_SWEEP_REVERSAL** (total=3224): execution:trigger_not_confirmed=1584, execution:overextended=1037, setup_compat:regime_STRONG_TREND=603
- **MA_CROSS_TREND_SHIFT** (total=15): setup_compat:regime_DIRTY_RANGE=5, setup_compat:regime_VOLATILE_UNSUITABLE=3, execution:trigger_not_confirmed=3, execution:overextended=3, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=4269): execution:overextended=2222, setup_compat:regime_STRONG_TREND=1401, setup_compat:regime_WEAK_TREND=646
- **MOVER_AVWAP_SCALP** (total=1091): execution:overextended=751, execution:trigger_not_confirmed=227, entry_quality=113
- **MOVER_TREND_PULLBACK** (total=10624): execution:trigger_not_confirmed=5360, execution:overextended=4127, entry_quality=1137
- **QUIET_COMPRESSION_BREAK** (total=18): execution:trigger_not_confirmed=18
- **RANGE_FADE** (total=2684): setup_compat:regime_WEAK_TREND=1059, setup_compat:regime_STRONG_TREND=801, execution:overextended=451, setup_compat:regime_VOLATILE_UNSUITABLE=266, context_edge=92, setup_compat:regime_BREAKOUT_EXPANSION=15
- **TREND_PULLBACK_EMA** (total=1550): setup_compat:regime_DIRTY_RANGE=763, setup_compat:regime_CLEAN_RANGE=728, entry_quality=51, setup_compat:regime_VOLATILE_UNSUITABLE=8
- **WHALE_MOMENTUM** (total=60): execution:trigger_not_confirmed=60

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 174643 | 45.1% |
| QUIET | 83495 | 21.6% |
| TRENDING_DOWN | 69026 | 17.8% |
| TRENDING_UP | 43573 | 11.3% |
| VOLATILE | 16320 | 4.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **175**
- Average confidence gap to threshold: **13.41** (samples=175) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: LITUSDT=21, AEROUSDT=14, QNTUSDT=12, TIAUSDT=11, ETHUSDT=10, ALTUSDT=9, ATOMUSDT=8, XMRUSDT=7, WLDUSDT=7, TAOUSDT=6

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 150 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 19 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 40 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 11 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 8 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 11 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 37 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 11 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 34 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 6 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 350 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 54 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 3 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 183 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 865 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 76 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2304 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 29 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 15 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 67 |
| SR_FLIP_RETEST | filtered | min_confidence | 30 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 5 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 60 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 27 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 14 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 67 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 169 | 51.60 | 64.32 | 12.72 | 20.03 | 19.67 | 18.12 | 2.63 | 17.56 |
| DIVERGENCE_CONTINUATION | kept | 40 | 69.13 | 65.00 | -4.13 | 20.58 | 19.88 | 17.33 | 4.33 | 2.83 |
| FAILED_AUCTION_RECLAIM | filtered | 19 | 49.86 | 63.05 | 13.19 | 20.59 | 19.57 | 20.00 | 1.92 | 8.25 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 66.65 | 65.00 | -1.65 | 20.75 | 19.70 | 20.00 | 1.75 | 1.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 51.78 | 61.00 | 9.22 | 18.30 | 15.55 | 16.55 | 2.73 | 6.91 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 48 | 46.25 | 62.81 | 16.56 | 19.59 | 18.07 | 17.39 | 2.38 | 10.68 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 34 | 72.56 | 65.00 | -7.56 | 22.04 | 18.89 | 17.53 | 0.68 | 0.00 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 47.55 | 63.00 | 15.45 | 20.90 | 18.70 | 15.80 | 0.00 | 16.80 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 77.00 | 65.00 | -12.00 | 19.90 | 19.50 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 6 | 31.17 | 65.00 | 33.83 | 21.17 | 18.43 | 16.37 | 0.00 | 22.87 |
| MOVER_AVWAP_SCALP | filtered | 407 | 52.48 | 57.27 | 4.79 | 19.93 | 13.34 | 15.80 | 3.61 | 24.28 |
| MOVER_AVWAP_SCALP | kept | 183 | 78.80 | 65.00 | -13.80 | 20.85 | 15.38 | 15.80 | 4.39 | 1.83 |
| MOVER_TREND_PULLBACK | filtered | 941 | 56.75 | 64.72 | 7.97 | 19.46 | 18.49 | 15.80 | 3.87 | 18.11 |
| MOVER_TREND_PULLBACK | kept | 2304 | 75.77 | 65.00 | -10.77 | 20.63 | 18.49 | 15.80 | 3.97 | 2.16 |
| QUIET_COMPRESSION_BREAK | filtered | 44 | 51.52 | 63.64 | 12.12 | 20.50 | 19.07 | 20.00 | 0.00 | 17.20 |
| QUIET_COMPRESSION_BREAK | kept | 67 | 73.49 | 65.00 | -8.49 | 21.30 | 19.66 | 20.00 | 0.00 | 1.81 |
| SR_FLIP_RETEST | filtered | 35 | 56.16 | 65.00 | 8.84 | 21.40 | 20.00 | 15.81 | 1.59 | 7.06 |
| SR_FLIP_RETEST | kept | 60 | 74.55 | 65.00 | -9.55 | 20.66 | 20.00 | 18.74 | 2.50 | -0.18 |
| TREND_PULLBACK_EMA | filtered | 41 | 57.05 | 65.00 | 7.95 | 19.89 | 19.82 | 17.35 | 4.10 | 18.53 |
| TREND_PULLBACK_EMA | kept | 67 | 75.57 | 65.00 | -10.57 | 21.52 | 19.92 | 17.92 | 4.29 | 2.51 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 74.80 | 65.00 | -9.80 | 20.60 | 16.50 | 20.00 | 5.50 | 10.70 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 169 | 51.60 | 22.44 | 11.37 | 5.41 | 12.98 | 5.54 | 8.79 | 2.63 |
| DIVERGENCE_CONTINUATION | kept | 40 | 69.13 | 23.00 | 15.75 | 4.05 | 11.20 | 5.42 | 8.95 | 4.33 |
| FAILED_AUCTION_RECLAIM | filtered | 19 | 49.86 | 20.37 | 15.68 | 6.32 | 15.00 | 5.82 | 4.85 | 1.92 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 66.65 | 21.00 | 16.00 | 3.00 | 12.50 | 5.75 | 7.65 | 1.75 |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 51.78 | 22.82 | 19.45 | 3.00 | 12.55 | 6.09 | 2.96 | 2.73 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 48 | 46.25 | 23.71 | 14.12 | 5.25 | 12.23 | 5.75 | 5.37 | 2.38 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 34 | 72.56 | 23.00 | 14.59 | 4.94 | 14.71 | 6.63 | 8.01 | 0.68 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 47.55 | 21.00 | 14.00 | 6.00 | 14.00 | 7.50 | 9.35 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 77.00 | 25.00 | 14.00 | 3.00 | 17.00 | 10.00 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 6 | 31.17 | 22.33 | 18.00 | 7.00 | 13.00 | 5.00 | 3.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 407 | 52.48 | 18.74 | 18.13 | 13.23 | 13.70 | 7.54 | 7.25 | 3.61 |
| MOVER_AVWAP_SCALP | kept | 183 | 78.80 | 18.68 | 18.00 | 12.44 | 13.91 | 7.36 | 8.57 | 4.39 |
| MOVER_TREND_PULLBACK | filtered | 941 | 56.75 | 18.29 | 18.00 | 7.57 | 12.09 | 5.94 | 9.56 | 3.87 |
| MOVER_TREND_PULLBACK | kept | 2304 | 75.77 | 19.52 | 18.05 | 7.85 | 12.56 | 6.83 | 9.22 | 3.97 |
| QUIET_COMPRESSION_BREAK | filtered | 44 | 51.52 | 18.45 | 16.64 | 11.93 | 13.95 | 5.20 | 6.56 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 67 | 73.49 | 18.43 | 17.46 | 10.61 | 14.36 | 6.66 | 8.01 | 0.00 |
| SR_FLIP_RETEST | filtered | 35 | 56.16 | 17.69 | 16.57 | 3.86 | 14.43 | 5.50 | 9.15 | 1.59 |
| SR_FLIP_RETEST | kept | 60 | 74.55 | 24.30 | 16.83 | 3.60 | 14.00 | 5.81 | 8.87 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 41 | 57.05 | 15.39 | 18.00 | 7.50 | 14.00 | 7.66 | 8.93 | 4.10 |
| TREND_PULLBACK_EMA | kept | 67 | 75.57 | 17.51 | 18.00 | 8.08 | 14.03 | 6.75 | 9.59 | 4.29 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 74.80 | 25.00 | 14.00 | 12.00 | 14.00 | 5.00 | 10.00 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 169 | 51.60 | 0.00 | 0.00 | 1.34 | 0.00 | 1.68 | 0.00 | 0.00 | 0.00 | **3.02** |
| DIVERGENCE_CONTINUATION | kept | 40 | 69.13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 19 | 49.86 | 0.00 | 0.00 | 2.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.44** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 66.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 51.78 | 0.00 | 0.00 | 3.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.27** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 48 | 46.25 | 0.00 | 0.00 | 2.95 | 0.00 | 0.00 | 0.42 | 0.00 | 0.00 | **3.37** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 34 | 72.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 47.55 | 0.00 | 0.00 | 6.00 | 0.00 | 10.80 | 0.00 | 0.00 | 0.00 | **16.80** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 77.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 6 | 31.17 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| MOVER_AVWAP_SCALP | filtered | 407 | 52.48 | 0.07 | 0.00 | 4.04 | 0.00 | 6.63 | 0.00 | 0.00 | 1.97 | **12.71** |
| MOVER_AVWAP_SCALP | kept | 183 | 78.80 | 0.08 | 0.00 | 0.42 | 0.00 | 0.56 | 0.11 | 0.00 | 0.02 | **1.19** |
| MOVER_TREND_PULLBACK | filtered | 941 | 56.75 | 0.00 | 0.00 | 2.43 | 0.00 | 0.87 | 0.21 | 0.00 | 0.00 | **3.51** |
| MOVER_TREND_PULLBACK | kept | 2304 | 75.77 | 0.00 | 0.00 | 1.81 | 0.00 | 0.12 | 0.03 | 0.00 | 0.02 | **1.98** |
| QUIET_COMPRESSION_BREAK | filtered | 44 | 51.52 | 0.00 | 0.00 | 4.36 | 0.00 | 0.00 | 0.82 | 0.00 | 3.93 | **9.11** |
| QUIET_COMPRESSION_BREAK | kept | 67 | 73.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 35 | 56.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 60 | 74.55 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.08** |
| TREND_PULLBACK_EMA | filtered | 41 | 57.05 | 0.00 | 0.00 | 5.11 | 0.00 | 0.00 | 0.73 | 0.00 | 0.00 | **5.84** |
| TREND_PULLBACK_EMA | kept | 67 | 75.57 | 0.00 | 0.00 | 0.79 | 0.00 | 0.00 | 0.30 | 0.00 | 0.00 | **1.09** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 74.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **156184 held of 586406 seen** across 21 strategies; 3539 cells past the sample floor; **1809 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 45537 | 744/44793/0 | 45% | -0.14 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| MOVER_AVWAP_SCALP | 20296 | 189/20107/0 | 42% | -0.22 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 11739 | 125/11614/0 | 37% | -0.28 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (+1.77R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 11227 | 112/11115/0 | 49% | -0.05 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| TREND_PULLBACK_EMA | 9418 | 43/9375/0 | 40% | -0.24 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/ACCUMULATION/NORMAL/BTC_FALLING (-1.30R) |
| LIQUIDITY_SWEEP_REVERSAL | 8425 | 93/8332/0 | 34% | -0.52 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 7493 | 0/0/7493 | 43% | -0.09 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.24R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.07R) |
| SHADOW_RANGE_FADE | 6958 | 0/0/6958 | 35% | -0.15 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.43R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.20R) |
| QUIET_COMPRESSION_BREAK | 6503 | 432/6071/0 | 49% | -0.13 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 6109 | 0/0/6109 | 34% | -0.41 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.00R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| MEAN_REVERT | 4251 | 46/4205/0 | 37% | -0.33 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/MARKDOWN/CASCADE/BTC_NEUTRAL (-1.32R) |
| SR_FLIP_RETEST | 4035 | 19/4016/0 | 44% | -0.30 | NY/RANGE/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.18R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| FUNDING_EXTREME_SIGNAL | 3139 | 2/3137/0 | 31% | -0.48 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3131 | 0/3131/0 | 32% | -0.32 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-1.19R) |
| RANGE_FADE | 1620 | 4/1616/0 | 37% | -0.40 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+2.15R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1393 | 0/0/1393 | 54% | -0.04 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.40R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 396 | 0/396/0 | 29% | -0.63 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 136 | 28/108/0 | 43% | -0.16 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 18 | 2/16/0 | 56% | +0.19 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL` -1.64R (n=18, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 236 | 28% / -0.58R | 236 | 52% / -0.15R | +0.44 | **ATR** |
| LIQUIDATION_REVERSAL | 23 | 26% / -0.63R | 23 | 52% / -0.26R | +0.37 | **ATR** |
| TREND_PULLBACK_EMA | 809 | 40% / -0.31R | 809 | 53% / -0.06R | +0.25 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1333 | 43% / -0.35R | 1333 | 56% / -0.13R | +0.22 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 157 | 35% / -0.23R | 157 | 46% / -0.07R | +0.16 | **ATR** |
| RANGE_FADE | 82 | 34% / -0.29R | 82 | 41% / -0.15R | +0.14 | **ATR** |
| SR_FLIP_RETEST | 370 | 42% / -0.31R | 370 | 46% / -0.19R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 1945 | 43% / -0.18R | 1945 | 49% / -0.06R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1136 | 40% / -0.25R | 1136 | 42% / -0.14R | +0.11 | **ATR** |
| MA_CROSS_TREND_SHIFT | 43 | 40% / -0.19R | 43 | 42% / -0.08R | +0.11 | **ATR** |
| MOVER_TREND_PULLBACK | 7857 | 49% / -0.11R | 7857 | 54% / -0.01R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1232 | 48% / -0.09R | 1232 | 54% / -0.04R | +0.05 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1097 | 47% / -0.14R | 1097 | 47% / -0.14R | -0.01 | **FIXED** |
| MEAN_REVERT | 300 | 47% / -0.17R | 300 | 46% / -0.17R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 8 | 50% / -0.24R | 8 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 10718 | 28% | -0.23R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1945 | 47% | -0.07R | 225 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 99 | 47% | -0.07R | 61 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1477 | 40% / -0.17R | +0.84 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1083 | 34% / -0.23R | +0.83 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2419 | 35% / -0.13R | +0.71 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 9737 | 37% / -0.12R | +0.41 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1403 | 38% / -0.07R | +0.21 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1074 | 35% / -0.15R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 947 | 33% / -0.21R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 229 | 31% / -0.39R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 315 | 33% / +0.07R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 249 | 49% / -0.04R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 62 | 40% / -0.02R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 342 | 33% / -0.34R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 65 | 28% / -0.41R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 29 | 41% / -0.18R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 16 | 44% / +0.50R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **3** · boot grace active: False
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.61R (bound 0.3) (streak 28/6) (sustained 28 cycles)
- **ALERT** `tuned_variants` — 98 non-stamps — atr_arm_uncomputable=98 (seen=1154 stamped=103 skipped=953) (streak 21/6) (sustained 21 cycles)
- **ALERT** `auto_dispatch` — 9 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=9) (streak 15/3) (sustained 15 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 5477894 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 9 arms current, none stalled; covering 1869/1869 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +2 but output +0 (streak 2/6) | 2 |
| atr_trail_live_arms | ok | 24 arms current, none stalled; covering 1021/1021 signals (100%) | 0 |
| auto_dispatch | violating | 9 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=9) (streak 15/3) | 15 |
| binance_ip_weight | ok | peak 142/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 80888.60 | 0 |
| candle_coverage | ok | 86/86 symbols with ≥20 15m candles, 86/86 updated within 45m [fresh=86; 75 Tier-1 futures + 11 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 210 dup bars, 0 undedupable; ws 0 out-of-order, 296 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 58 cohorts, 36 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +43 / upstream +33 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1230/1248 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 2 promoted today, nothing refused | 0 |
| dark_resolution | violating | 10 of 227 open dark rows are not being advanced (worst: ARIAUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 28/120) | 28 |
| dark_sar_arms | ok | no open arms; covering 1225/1243 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 934493 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.61R (bound 0.3) (streak 28/6) | 28 |
| emission_controller | ok | last cycle 755s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=335, MOVER_AVWAP_SCALP=215, MOVER_TREND_PULLBACK=5216, RANGE_FADE=9, TREND_PULLBACK_EMA=225), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 1/6) | 1 |
| firestore_read_budget | ok | 1,413 reads/day of 50,000 [engine 1,372, signing 41]; top site keystore.roster_doc at 292/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 1 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +4 / upstream +333 | 0 |
| indicator_cache_key | ok | 1177 frozen value(s) avoided; 4519 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.34R over n=4205 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +333 but output +0 (streak 1/72) | 1 |
| mover_admission_metadata | ok | 931 symbols known, 225 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 11 held, 11 with scan counts, 10 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3036 rows held, 3067788 evicted (sampled: execution:trigger_not_confirmed 400/1083544, execution:overextended 400/961104, setup_compat:regime_STRONG_TREND 400/522031) | 0 |
| price_action_lane | ok | 93475 evaluated, 99 emitted; layer1 99 stamped / 0 blind; cooldown=15701, delta_opposed=10005, no_footprint=32111, no_opposing_target=302, no_sweep=26071, rr_below_floor=9186 | 0 |
| promoted_pair_integrity | ok | 11/11 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.40R over n=1616 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | violating | upstream +333 but output +0 (streak 1/72) | 1 |
| sar_alignment_crosscheck | ok | 84/2026 disagreed (4.1%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +333 | 0 |
| sar_hold_arm | ok | 1895 held arms settled, 105 unscored, 20 still walking (16 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 4/52 unfetchable (8%); top cause: located bar does not contain the stamp; symbols: BRUSDT, CTUSDT, INUSDT, SOPHUSDT | 0 |
| sar_live_arms | ok | 20 arms current, none stalled; covering 1019/1019 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 452 records await one (48 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 19.07s, worst 103.44s over 1169 lifetime cycles; lifetime 8 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 5.14s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 34837 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 14m ago | 0 |
| snapshot_writer | ok | last cycle 37s ago (1.77s to run, worst 93.56s), 60 overrun(s) of 723 cycles, TTL 900s; slowest tickers=14.92s, signals=3.83s, data_intake=0.25s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +100 / upstream +333 | 0 |
| structural_snap | ok | 6000/6000 measured, 31 blind, 0 levels moved (refusals: redetect_cooldown=31) | 0 |
| structural_veto_lane | ok | 103 stamped; 0 with no readable level book, 3 with clear air ahead, 82 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +333 / upstream +33 | 0 |
| tuned_variants | violating | 98 non-stamps — atr_arm_uncomputable=98 (seen=1154 stamped=103 skipped=953) (streak 21/6) | 21 |
| unlock_shorts | ok | 14 open, 44 scheduled, calendar 13.0h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 3 — last: ClientOSError: [Errno 32] Broken pipe

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1845265`
- `Path funnel` emissions: `47`
- `Regime distribution` emissions: `47`
- `QUIET_SCALP_BLOCK` events: `175`
- `confidence_gate` events: `4482`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **3213**
- Total REST-fallback activations: **2**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 3 | 7606 | 7606 | 11983 | 0 |
| futures_aggtrade | 1612 | 5209 | 42047 | 128229 | 0 |
| futures_depth | 1577 | 5330 | 46479 | 130501 | 0 |
| futures_liq | 10 | 2963 | 42021 | 80672 | 0 |
| futures_mover | 11 | 13112 | 30506 | 37055 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 2 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=263693] state[populated=263693] buckets[many=263693] sources[none] quality[none]
- funding_rate: presence[absent=41809, present=221884] state[empty=41809, populated=221884] buckets[few=221884, none=41809] sources[none] quality[none]
- liquidation_clusters: presence[absent=184186, present=79507] state[empty=184186, populated=79507] buckets[few=63764, none=184186, some=15743] sources[none] quality[none]
- oi_snapshot: presence[absent=42768, present=220925] state[empty=42768, populated=220925] buckets[many=220925, none=42768] sources[none] quality[none]
- order_book: presence[absent=96683, present=167010] state[populated=167010, unavailable=96683] buckets[few=167010, none=96683] sources[book_ticker=167010, unavailable=96683] quality[none=96683, top_of_book_only=167010]
- orderblocks: presence[absent=263693] state[empty=263693] buckets[none=263693] sources[measured_dark=263693] quality[none]
- recent_ticks: presence[present=263693] state[populated=263693] buckets[many=263693] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.251369953155518` sec
- Median create→first breach: `2642.1928770542145` sec
- Median create→terminal: `2642.192939043045` sec
- Median first breach→terminal: `0.00013899803161621094` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 4.9}, "under_180s": {"count": 2, "pct": 4.9}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.4}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.8388358330782433 | 1.08636888323909 | 0.7721464099534879 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.6589912713772355 | 0.8000394399526758 | 0.8236984809351603 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 2.7522884950022317 | 3.0 | 0.9174294983340772 | 0 | 2 |
| MOVER_AVWAP_SCALP | 3 | 3 | 2.167922731589462 | 2.4971330479757374 | 0.8681646872387737 | 1 | 2 |
| MOVER_TREND_PULLBACK | 30 | 30 | 3.913124726371155 | 3.0 | 1.3043749087903849 | 20 | 10 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 1.3519858336966288 | 1.3520460358056383 | 0.9999554733290027 | 0 | 1 |
| SR_FLIP_RETEST | 1 | 1 | 1.4421916291430303 | 1.5730629225168997 | 0.9168047943279501 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.2583 | 18913.049623012543 | 18914.131832122803 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 0.9886 | 9802.95926117897 | 9803.836287021637 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.6829 | 2310.8477684259415 | 2311.047884583473 |
| MOVER_AVWAP_SCALP | 3 | 3 | 33.3 | 33.3 | 33.3 | 0.0 | 2.8247 | 1653.370220899582 | 1662.1944379806519 |
| MOVER_TREND_PULLBACK | 30 | 30 | 36.7 | 40.0 | 36.7 | 0.0 | 0.8357 | 2590.267809033394 | 2590.4938484430313 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 66.7 | 33.3 | 66.7 | 0.0 | 1.3263 | 30742.347941875458 | 30743.656147956848 |
| SR_FLIP_RETEST | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.4422 | 2442.7464530467987 | 2442.7464728355408 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 829 | 9 | 454 | 0.0 | 100.0 | 2442.7464530467987 | 2442.7464728355408 | 375 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1755 | 24 | 1403 | 0.0 | 0.0 | None | None | 352 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-103`
- Gating Δ: `-4333`
- No-generation Δ: `215118`
- Fast failures Δ: `1`
- Quality changes: `{"LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.005, "current_avg_pnl": 0.6829, "current_win_rate": 50.0, "previous_avg_pnl": 0.6779, "previous_win_rate": 50.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 2.8247, "current_avg_pnl": 2.8247, "current_win_rate": 33.3, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 33.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 2.0135, "current_avg_pnl": 0.8357, "current_win_rate": 36.7, "previous_avg_pnl": -1.1778, "previous_win_rate": 18.8, "win_rate_delta": 17.9}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 1.4022, "current_avg_pnl": 1.3263, "current_win_rate": 66.7, "previous_avg_pnl": -0.0759, "previous_win_rate": 33.3, "win_rate_delta": 33.4}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": 191, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -14992.11, "median_terminal_delta_sec": -14992.55, "sl_rate_delta": 100.0, "win_rate_delta": -100.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 8, "geometry_changed_delta": 0, "geometry_preserved_delta": 207, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **QUIET_COMPRESSION_BREAK**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
