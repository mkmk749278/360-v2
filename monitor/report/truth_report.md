# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `4148` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 289 | 289 | 287 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 26408 | 26408 | 24684 | 20 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 137229 | 137190 | 70 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 104934 | 104934 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 104492 | 100031 | 4887 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 104966 | 103354 | 1698 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 112953 | 112925 | 59 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 101847 | 101867 | 7 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 105060 | 105114 | 8 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 105128 | 101809 | 4637 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 141881 | 147566 | 1830 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 137264 | 126402 | 15425 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 112075 | 112075 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 104942 | 104948 | 13 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 104449 | 104207 | 276 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 106453 | 104236 | 3114 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 103548 | 104096 | 314 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 93932 | 88907 | 5270 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 94181 | 93249 | 1016 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 137184 | 137198 | 25 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 101874 | 101884 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 9708 | 9708 | 9104 | 8 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 253 | 253 | 191 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 75 | 75 | 75 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 36434 | 36434 | 35843 | 9 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 14 | 14 | 10 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 15926 | 15926 | 14325 | 6 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 7208 | 7208 | 5630 | 52 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 49205 | 49205 | 36997 | 221 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 62 | 62 | 62 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1600 | 1600 | 1285 | 13 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 10874 | 10874 | 10500 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1500 | 1500 | 1019 | 4 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 5463 | 5463 | 4979 | 17 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 171 | 171 | 168 | 3 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=137190): breakout_not_found=72860, basic_filters_failed=43394, move_not_fresh=12306, breakout_stale=6552, retest_proximity_failed=1745, volume_spike_missing=320, move_exhausted=7, missing_fvg_or_orderblock=6
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=104934): cls_disabled_merged_into_lsr=104934
- **EVAL::DIVERGENCE_CONTINUATION** (total=100031): cvd_divergence_failed=36121, basic_filters_failed=31185, h1_trend_not_aligned=23503, ema_alignment_reject=7702, retest_proximity_failed=967, missing_fvg_or_orderblock=553
- **EVAL::FAILED_AUCTION_RECLAIM** (total=103354): auction_not_detected=59581, basic_filters_failed=30289, reclaim_hold_failed=7000, tail_too_small=3706, regime_blocked=2745, rsi_reject=33
- **EVAL::FUNDING_EXTREME** (total=112925): funding_not_extreme=78467, basic_filters_failed=32432, missing_funding_rate=1357, ema_alignment_reject=337, rsi_reject=188, momentum_reject=82, cvd_divergence_failed=60, missing_fvg_or_orderblock=2
- **EVAL::LIQUIDATION_REVERSAL** (total=101867): cascade_threshold_not_met=68662, basic_filters_failed=32344, cvd_divergence_failed=420, rsi_reject=415, missing_fvg_or_orderblock=13, missing_cvd=8, volume_spike_missing=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=105114): no_ma_cross=71491, basic_filters_failed=31201, ma_cross_cooldown=1274, ma_cross_htf_misaligned=1148
- **EVAL::MEAN_REVERT** (total=101809): no_extension=81519, basic_filters_failed=20290
- **EVAL::MOVER_AVWAP_SCALP** (total=147566): no_avwap_tag=45378, basic_filters_failed=43444, no_mover_leg=39991, avwap_slope_against=12283, avwap_reclaim_no_volume=3564, no_avwap_reclaim=2396, insufficient_candles=504, anchor_too_recent=6
- **EVAL::MOVER_TREND_PULLBACK** (total=126402): mover_run_too_small=58358, basic_filters_failed=42735, no_reclaim=21129, no_pullback_tag=2572, insufficient_candles=1608
- **EVAL::OPENING_RANGE_BREAKOUT** (total=112075): feature_disabled=112075
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=104948): regime_blocked=61205, breakout_not_found=27052, basic_filters_failed=12100, adx_reject=4533, ema_alignment_reject=57, rsi_reject=1
- **EVAL::QUIET_COMPRESSION_BREAK** (total=104207): regime_blocked=46380, compression_not_detected=32630, basic_filters_failed=18180, breakout_not_detected=6337, volume_confirmation_failed=652, rsi_reject=19, missing_fvg_or_orderblock=9
- **EVAL::RANGE_FADE** (total=104236): no_range_edge=83946, basic_filters_failed=20290
- **EVAL::SR_FLIP_RETEST** (total=104096): flip_close_not_confirmed=59846, basic_filters_failed=30266, long_break_volume_thin=3829, retest_out_of_zone=3256, regime_blocked=2739, h1_break_not_confirmed=2506, reclaim_hold_failed=1034, ema_alignment_reject=196, wick_quality_failed=172, long_acceptance_not_held=168, whipsaw_flip=58, missing_fvg_or_orderblock=26
- **EVAL::STANDARD** (total=88907): adx_reject=26679, momentum_reject=24485, basic_filters_failed=15013, sweeps_not_detected=7793, ema_alignment_reject=7069, macd_reject=6545, htf_poi_unanchored=1253, rsi_reject=38, invalid_sl_geometry=31, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=93249): h1_trend_not_aligned=30582, basic_filters_failed=17966, ema_alignment_reject=15003, h1_pullback_not_confirmed=8077, no_ema_reclaim_close=6641, ema_not_tested_prev=5771, body_conviction_fail=3844, rsi_reject=2474, prev_already_below_emas=1255, prev_already_above_emas=572, no_prev_low_break=502, no_prev_high_break=296, ema21_not_tagged=114, momentum_flat=89, missing_fvg_or_orderblock=55, momentum_reject=8
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=137198): breakout_not_found=71533, basic_filters_failed=43391, move_not_fresh=14230, breakout_stale=5529, retest_proximity_failed=1978, volume_spike_missing=519, move_exhausted=10, missing_fvg_or_orderblock=8
- **EVAL::WHALE_MOMENTUM** (total=101884): momentum_reject=85918, recent_ticks_insufficient=10270, basic_filters_failed=5696

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=726): setup_compat:regime_VOLATILE_UNSUITABLE=639, setup_compat:regime_BREAKOUT_EXPANSION=66, execution:overextended=21
- **FAILED_AUCTION_RECLAIM** (total=3342): setup_compat:regime_STRONG_TREND=1859, execution:overextended=1364, context_floor=119
- **FUNDING_EXTREME_SIGNAL** (total=182): execution:trigger_not_confirmed=182
- **LIQUIDATION_REVERSAL** (total=75): execution:trigger_not_confirmed=75
- **LIQUIDITY_SWEEP_REVERSAL** (total=8902): setup_compat:regime_STRONG_TREND=3928, execution:trigger_not_confirmed=2766, execution:overextended=2208
- **MA_CROSS_TREND_SHIFT** (total=8): setup_compat:regime_CLEAN_RANGE=4, setup_compat:regime_DIRTY_RANGE=3, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=11798): setup_compat:regime_WEAK_TREND=6733, setup_compat:regime_STRONG_TREND=4612, execution:overextended=446, entry_quality=7
- **MOVER_AVWAP_SCALP** (total=2718): execution:overextended=2087, execution:trigger_not_confirmed=366, entry_quality=265
- **MOVER_TREND_PULLBACK** (total=19421): execution:trigger_not_confirmed=9860, execution:overextended=7776, entry_quality=1785
- **QUIET_COMPRESSION_BREAK** (total=38): execution:overextended=38
- **RANGE_FADE** (total=7860): setup_compat:regime_WEAK_TREND=3920, setup_compat:regime_STRONG_TREND=3250, setup_compat:regime_VOLATILE_UNSUITABLE=472, execution:overextended=201, setup_compat:regime_BREAKOUT_EXPANSION=17
- **SR_FLIP_RETEST** (total=6): setup_compat:regime_VOLATILE_UNSUITABLE=6
- **TREND_PULLBACK_EMA** (total=4507): setup_compat:regime_CLEAN_RANGE=3032, setup_compat:regime_DIRTY_RANGE=1221, entry_quality=130, setup_compat:regime_VOLATILE_UNSUITABLE=124
- **VOLUME_SURGE_BREAKOUT** (total=21): execution:overextended=21

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 316792 | 39.6% |
| TRENDING_DOWN | 166323 | 20.8% |
| TRENDING_UP | 151945 | 19.0% |
| QUIET | 129271 | 16.2% |
| VOLATILE | 34913 | 4.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **118**
- Average confidence gap to threshold: **13.53** (samples=118) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ETHFIUSDT=25, AVAXUSDT=15, ETHUSDT=13, XLMUSDT=11, ASTERUSDT=11, LITUSDT=11, BCHUSDT=7, TRXUSDT=6, LTCUSDT=5, 1000PEPEUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 2 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 131 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 8 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 540 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 77 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 16 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 151 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 187 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 68 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 117 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 2 |
| MEAN_REVERT | kept | min_confidence_pass | 91 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 184 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 13 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 633 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1431 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 33 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4129 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 134 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 37 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 78 |
| SR_FLIP_RETEST | filtered | min_confidence | 15 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 100 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 8 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 178 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 3 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 75.50 | 65.00 | -10.50 | 21.10 | 18.30 | 20.00 | 5.25 | 10.25 |
| DIVERGENCE_CONTINUATION | filtered | 139 | 55.64 | 64.93 | 9.29 | 20.40 | 19.39 | 17.33 | 1.65 | 13.77 |
| DIVERGENCE_CONTINUATION | kept | 540 | 71.26 | 65.00 | -6.26 | 20.22 | 19.78 | 18.25 | 1.31 | 1.07 |
| FAILED_AUCTION_RECLAIM | filtered | 93 | 53.26 | 62.97 | 9.71 | 21.31 | 18.94 | 20.00 | 2.95 | 8.05 |
| FAILED_AUCTION_RECLAIM | kept | 151 | 70.29 | 65.00 | -5.29 | 20.25 | 18.81 | 20.00 | 1.62 | 0.62 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 188 | 55.16 | 64.77 | 9.61 | 20.64 | 19.03 | 18.03 | 2.51 | 14.27 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 68 | 69.14 | 65.00 | -4.14 | 20.63 | 18.71 | 17.34 | 1.24 | 0.68 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 46.60 | 61.00 | 14.40 | 21.10 | 17.00 | 15.80 | 0.00 | 19.40 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 79.40 | 65.00 | -14.40 | 19.70 | 17.60 | 15.80 | 0.00 | 1.60 |
| MEAN_REVERT | filtered | 119 | 60.27 | 64.87 | 4.60 | 19.52 | 14.35 | 15.16 | 0.00 | 15.19 |
| MEAN_REVERT | kept | 91 | 71.39 | 65.00 | -6.39 | 20.12 | 16.17 | 16.52 | 0.00 | 0.91 |
| MOVER_AVWAP_SCALP | filtered | 197 | 59.42 | 64.31 | 4.89 | 20.35 | 17.15 | 15.80 | 4.61 | 12.39 |
| MOVER_AVWAP_SCALP | kept | 633 | 80.37 | 65.00 | -15.37 | 20.66 | 16.64 | 15.80 | 4.74 | 3.02 |
| MOVER_TREND_PULLBACK | filtered | 1464 | 58.34 | 64.65 | 6.31 | 19.67 | 18.81 | 15.80 | 4.32 | 15.92 |
| MOVER_TREND_PULLBACK | kept | 4129 | 77.81 | 65.00 | -12.81 | 20.33 | 18.63 | 15.80 | 4.41 | 0.94 |
| QUIET_COMPRESSION_BREAK | filtered | 171 | 53.43 | 65.00 | 11.57 | 22.14 | 17.17 | 20.00 | 0.00 | 12.40 |
| QUIET_COMPRESSION_BREAK | kept | 78 | 75.43 | 65.00 | -10.43 | 21.94 | 18.92 | 20.00 | 0.00 | -2.23 |
| SR_FLIP_RETEST | filtered | 15 | 54.45 | 61.80 | 7.35 | 23.11 | 20.00 | 20.00 | 1.20 | 11.93 |
| SR_FLIP_RETEST | kept | 100 | 76.09 | 65.00 | -11.09 | 20.19 | 20.00 | 16.25 | 2.15 | -0.85 |
| TREND_PULLBACK_EMA | filtered | 8 | 60.45 | 65.00 | 4.55 | 21.66 | 20.00 | 18.81 | 4.88 | 16.68 |
| TREND_PULLBACK_EMA | kept | 178 | 79.31 | 65.00 | -14.31 | 21.20 | 19.77 | 16.89 | 5.13 | 1.68 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 74.33 | 65.00 | -9.33 | 20.77 | 17.10 | 20.00 | 4.67 | 2.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 75.50 | 21.00 | 18.00 | 13.50 | 14.00 | 5.00 | 9.00 | 5.25 |
| DIVERGENCE_CONTINUATION | filtered | 139 | 55.64 | 20.68 | 14.91 | 6.76 | 11.74 | 5.27 | 8.62 | 1.65 |
| DIVERGENCE_CONTINUATION | kept | 540 | 71.26 | 22.21 | 17.26 | 5.29 | 12.95 | 5.33 | 9.11 | 1.31 |
| FAILED_AUCTION_RECLAIM | filtered | 93 | 53.26 | 19.99 | 16.80 | 4.45 | 12.68 | 6.98 | 5.84 | 2.95 |
| FAILED_AUCTION_RECLAIM | kept | 151 | 70.29 | 18.75 | 16.62 | 4.25 | 14.96 | 5.32 | 9.40 | 1.62 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 188 | 55.16 | 23.67 | 14.15 | 4.15 | 12.98 | 5.74 | 6.24 | 2.51 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 68 | 69.14 | 23.03 | 15.35 | 4.32 | 12.51 | 5.86 | 7.50 | 1.24 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 46.60 | 17.00 | 14.00 | 3.00 | 17.00 | 5.00 | 10.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 79.40 | 25.00 | 14.00 | 12.00 | 17.00 | 5.00 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 119 | 60.27 | 23.99 | 14.24 | 13.84 | 13.00 | 5.00 | 5.91 | 0.00 |
| MEAN_REVERT | kept | 91 | 71.39 | 20.52 | 15.01 | 14.97 | 13.00 | 5.00 | 7.13 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 197 | 59.42 | 16.65 | 18.00 | 10.63 | 14.13 | 5.28 | 8.30 | 4.61 |
| MOVER_AVWAP_SCALP | kept | 633 | 80.37 | 19.71 | 18.00 | 11.14 | 14.16 | 7.05 | 8.66 | 4.74 |
| MOVER_TREND_PULLBACK | filtered | 1464 | 58.34 | 19.21 | 18.00 | 8.21 | 12.05 | 6.07 | 7.87 | 4.32 |
| MOVER_TREND_PULLBACK | kept | 4129 | 77.81 | 19.32 | 18.05 | 8.24 | 12.80 | 6.81 | 9.24 | 4.41 |
| QUIET_COMPRESSION_BREAK | filtered | 171 | 53.43 | 17.19 | 14.87 | 11.86 | 14.00 | 8.41 | 3.28 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 78 | 75.43 | 17.10 | 17.85 | 12.81 | 14.00 | 8.47 | 5.86 | 0.00 |
| SR_FLIP_RETEST | filtered | 15 | 54.45 | 18.07 | 18.00 | 3.00 | 16.07 | 5.00 | 5.05 | 1.20 |
| SR_FLIP_RETEST | kept | 100 | 76.09 | 21.64 | 18.00 | 5.76 | 15.12 | 5.00 | 9.25 | 2.15 |
| TREND_PULLBACK_EMA | filtered | 8 | 60.45 | 18.00 | 18.00 | 7.50 | 14.00 | 5.00 | 9.75 | 4.88 |
| TREND_PULLBACK_EMA | kept | 178 | 79.31 | 20.19 | 18.00 | 8.11 | 14.61 | 6.86 | 9.26 | 5.13 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 74.33 | 14.67 | 16.00 | 12.00 | 14.00 | 5.00 | 10.00 | 4.67 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 75.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 139 | 55.64 | 0.00 | 0.00 | 0.66 | 0.00 | 1.67 | 0.12 | 0.00 | 0.00 | **2.45** |
| DIVERGENCE_CONTINUATION | kept | 540 | 71.26 | 0.00 | 0.00 | 0.34 | 0.00 | 0.24 | 0.00 | 0.00 | 0.00 | **0.58** |
| FAILED_AUCTION_RECLAIM | filtered | 93 | 53.26 | 0.00 | 0.00 | 0.00 | 0.00 | 2.32 | 0.00 | 0.00 | 0.00 | **2.32** |
| FAILED_AUCTION_RECLAIM | kept | 151 | 70.29 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.05** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 188 | 55.16 | 0.00 | 0.00 | 0.43 | 0.00 | 0.11 | 0.27 | 0.00 | 0.00 | **0.81** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 68 | 69.14 | 0.00 | 0.00 | 0.07 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | **0.25** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 46.60 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 79.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 119 | 60.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.36 | 0.15 | 0.00 | 0.00 | **0.51** |
| MEAN_REVERT | kept | 91 | 71.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.11 | 0.00 | 0.00 | **0.11** |
| MOVER_AVWAP_SCALP | filtered | 197 | 59.42 | 0.00 | 0.00 | 0.71 | 0.00 | 2.31 | 0.15 | 0.00 | 0.00 | **3.17** |
| MOVER_AVWAP_SCALP | kept | 633 | 80.37 | 0.00 | 0.00 | 0.95 | 0.00 | 0.04 | 0.00 | 0.00 | 0.07 | **1.06** |
| MOVER_TREND_PULLBACK | filtered | 1464 | 58.34 | 0.00 | 0.00 | 0.13 | 0.00 | 0.52 | 0.00 | 0.00 | 0.00 | **0.65** |
| MOVER_TREND_PULLBACK | kept | 4129 | 77.81 | 0.00 | 0.00 | 0.25 | 0.00 | 0.28 | 0.00 | 0.00 | 0.00 | **0.53** |
| QUIET_COMPRESSION_BREAK | filtered | 171 | 53.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.98 | 0.00 | 3.28 | **4.31** |
| QUIET_COMPRESSION_BREAK | kept | 78 | 75.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 | 0.00 | 0.14 | **0.20** |
| SR_FLIP_RETEST | filtered | 15 | 54.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.20 | **5.20** |
| SR_FLIP_RETEST | kept | 100 | 76.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.60 | 0.00 | 0.00 | 0.00 | **0.60** |
| TREND_PULLBACK_EMA | filtered | 8 | 60.45 | 0.00 | 0.00 | 7.20 | 0.00 | 8.10 | 0.00 | 0.00 | 0.00 | **15.30** |
| TREND_PULLBACK_EMA | kept | 178 | 79.31 | 0.00 | 0.00 | 2.03 | 0.00 | 1.55 | 0.00 | 0.00 | 0.00 | **3.58** |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 74.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **125950 held of 404973 seen** across 21 strategies; 2881 cells past the sample floor; **1385 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 40971 | 580/40391/0 | 43% | -0.18 | LONDON/MARKUP/NORMAL/BTC_FALLING/MAJOR (+1.14R) | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.25R) |
| MOVER_AVWAP_SCALP | 16395 | 168/16227/0 | 39% | -0.29 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 10012 | 114/9898/0 | 39% | -0.26 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 8585 | 53/8532/0 | 50% | -0.04 | NY/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (+1.39R) | OVERLAP/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| TREND_PULLBACK_EMA | 7279 | 26/7253/0 | 43% | -0.17 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.33R) |
| SHADOW_MEAN_REVERT | 6411 | 0/0/6411 | 43% | -0.09 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-0.86R) |
| SHADOW_RANGE_FADE | 5676 | 0/0/5676 | 38% | -0.07 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.63R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.33R) |
| QUIET_COMPRESSION_BREAK | 5320 | 312/5008/0 | 49% | -0.10 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.59R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4975 | 0/0/4975 | 34% | -0.40 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| LIQUIDITY_SWEEP_REVERSAL | 4879 | 70/4809/0 | 38% | -0.43 | NY/RANGE/NORMAL/BTC_FALLING (+1.64R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| WHALE_MOMENTUM | 3391 | 2/3389/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| MEAN_REVERT | 2698 | 33/2665/0 | 46% | -0.15 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.62R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| VOLUME_SURGE_BREAKOUT | 2267 | 0/2267/0 | 40% | -0.08 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2128 | 2/2126/0 | 31% | -0.48 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| SR_FLIP_RETEST | 1895 | 11/1884/0 | 49% | -0.21 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.86R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.27R) |
| RANGE_FADE | 1142 | 4/1138/0 | 42% | -0.34 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 995 | 0/0/995 | 55% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.19R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.42R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 276 | 0/276/0 | 31% | -0.57 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 80 | 12/68/0 | 48% | -0.05 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 8 | 0/8/0 | 75% | +0.30 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR` -1.55R (n=16, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR` -1.53R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 159 | 26% / -0.59R | 159 | 47% / -0.18R | +0.41 | **ATR** |
| LIQUIDATION_REVERSAL | 15 | 33% / -0.42R | 15 | 60% / -0.16R | +0.25 | **ATR** |
| TREND_PULLBACK_EMA | 588 | 43% / -0.23R | 588 | 56% / -0.03R | +0.20 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 947 | 46% / -0.29R | 947 | 56% / -0.13R | +0.16 | **ATR** |
| MOVER_AVWAP_SCALP | 1355 | 43% / -0.20R | 1355 | 49% / -0.08R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 368 | 44% / -0.33R | 368 | 46% / -0.22R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 6426 | 49% / -0.12R | 6426 | 54% / -0.02R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 960 | 41% / -0.22R | 960 | 44% / -0.13R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 121 | 37% / -0.15R | 121 | 47% / -0.06R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 189 | 49% / -0.25R | 189 | 51% / -0.16R | +0.08 | **ATR** |
| DIVERGENCE_CONTINUATION | 862 | 48% / -0.12R | 862 | 54% / -0.05R | +0.07 | **ATR** |
| MA_CROSS_TREND_SHIFT | 24 | 46% / -0.11R | 24 | 46% / -0.13R | -0.01 | **FIXED** |
| RANGE_FADE | 50 | 36% / -0.33R | 50 | 38% / -0.34R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 868 | 46% / -0.15R | 868 | 46% / -0.15R | -0.01 | **FIXED** |
| MEAN_REVERT | 202 | 53% / -0.04R | 202 | 52% / -0.04R | +0.00 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 50% / -0.21R | 6 | 50% / -0.10R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 9153 | 30% | -0.25R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1355 | 47% | -0.08R | 205 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 75 | 51% | -0.06R | 50 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 141 | 36% / -0.32R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 843 | 35% / -0.18R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 8197 | 36% / -0.17R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1747 | 35% / -0.11R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 779 | 34% / -0.18R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 955 | 38% / -0.06R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 782 | 37% / -0.12R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 918 | 40% / -0.26R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 175 | 30% / -0.36R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 210 | 29% / -0.61R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 169 | 57% / +0.14R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 38 | 32% / -0.10R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 185 | 34% / -0.47R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 38 | 26% / -0.41R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 21 | 48% / +0.11R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 11 | 45% / +0.67R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=68, profile_reject=2. Held back in this window: session_quality=118, profile_reject=12. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 12/6) (sustained 12 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.68R (bound 0.3) (streak 241/6) (sustained 241 cycles)
- **ALERT** `tuned_variants` — 84 non-stamps — atr_arm_uncomputable=84 (seen=4565 stamped=432 skipped=4049) (streak 228/6) (sustained 228 cycles)
- **ALERT** `auto_dispatch` — 46 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=46) (streak 222/3) (sustained 222 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 41 fed / 0 quiet / 0 never delivered of 41 subscribed; 53054783 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 22 arms current, none stalled; covering 1149/1149 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +2 but output +0 (streak 1/6) | 1 |
| atr_trail_live_arms | ok | 41 arms current, none stalled; covering 1081/1081 signals (100%) | 0 |
| auto_dispatch | violating | 46 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=46) (streak 222/3) | 222 |
| binance_ip_weight | ok | peak 207/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 85964.80 | 0 |
| candle_coverage | ok | 85/85 symbols with ≥20 15m candles, 85/85 updated within 45m [fresh=85; 75 Tier-1 futures + 10 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 500 dup bars, 0 undedupable; ws 0 out-of-order, 127 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 35 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 35 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +24 / upstream +45 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1301/1319 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 3 of 120 open dark rows are not being advanced (worst: KASUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 82/120) | 82 |
| dark_sar_arms | ok | no open arms; covering 1297/1315 signals (99%) | 0 |
| depth_feed | ok | 41/41 books fresh (stale 0, never 0, thin 0); 10969674 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.68R (bound 0.3) (streak 241/6) | 241 |
| emission_controller | ok | last cycle 1s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 5534 stamps (MEAN_REVERT=985, MOVER_AVWAP_SCALP=432, MOVER_TREND_PULLBACK=3224, RANGE_FADE=751, TREND_PULLBACK_EMA=142), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=68, profile_reject=2. Held back in this window: session_quality=118, profile_reject=12. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 12/6) | 12 |
| firestore_read_budget | ok | 1,384 reads/day of 50,000 [engine 1,346, signing 38]; top site keystore.roster_doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4920 sealed bars over 41 symbols; 1464 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +1 / upstream +279 | 0 |
| indicator_cache_key | ok | 93786 frozen value(s) avoided; 1085805 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.16R over n=2665 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +279 but output +0 (streak 2/72) | 2 |
| mover_admission_metadata | ok | 920 symbols known, 213 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 10 held, 10 with scan counts, 10 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 2263342 evicted (sampled: execution:trigger_not_confirmed 400/821242, execution:overextended 400/741985, setup_compat:regime_STRONG_TREND 400/346878) | 0 |
| price_action_lane | ok | 786982 evaluated, 614 emitted; layer1 614 stamped / 0 blind; cooldown=101608, delta_opposed=67389, no_footprint=342220, no_opposing_target=1726, no_sweep=216219, rr_below_floor=57206 | 0 |
| promoted_pair_integrity | ok | 10/10 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.34R over n=1138 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | violating | upstream +279 but output +0 (streak 2/72) | 2 |
| sar_alignment_crosscheck | ok | 272/10830 disagreed (2.5%) | 0 |
| sar_exit_shadow | violating | upstream +279 but output +0 (streak 2/6) | 2 |
| sar_hold_arm | ok | 1831 held arms settled, 169 unscored, 41 still walking (36 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 9/36 unfetchable (25%); top cause: gap or duplicate bar in the 15m window; symbols: 牛来USDT | 0 |
| sar_live_arms | ok | 41 arms current, none stalled; covering 1081/1081 signals (100%) | 0 |
| sar_refresh_budget | ok | 6 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 1 resolved, 26 still mid-window | 0 |
| scan_cycle | ok | last 44.94s, worst 79.45s over 8805 lifetime cycles; lifetime 14 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 6.57s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 320193 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 12s ago (0.3s to run, worst 57.78s), 277 overrun(s) of 5228 cycles, TTL 900s; slowest signals=0.08s, activity=0.06s, data_intake=0.05s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=25, gate reads=0, withheld=25) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +30 / upstream +279 | 0 |
| structural_snap | ok | 5874/5874 measured, 28 blind, 0 levels moved (refusals: redetect_cooldown=877) | 0 |
| structural_veto_lane | ok | 1267 stamped; 0 with no readable level book, 56 with clear air ahead, 1025 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +279 / upstream +45 | 0 |
| tuned_variants | violating | 84 non-stamps — atr_arm_uncomputable=84 (seen=4565 stamped=432 skipped=4049) (streak 228/6) | 228 |
| unlock_shorts | ok | 8 open, 47 scheduled, calendar 4.6h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 5 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3604900`
- `Path funnel` emissions: `90`
- `Regime distribution` emissions: `90`
- `QUIET_SCALP_BLOCK` events: `118`
- `confidence_gate` events: `8369`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **4**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 2 | 2146 | 2146 | 3487 | 0 |
| futures_liq | 2 | 4445 | 4445 | 16906 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[absent=1175, present=660440] state[empty=1175, populated=660440] buckets[few=9, many=660383, none=1175, some=48] sources[none] quality[none]
- funding_rate: presence[absent=88996, present=572619] state[empty=88996, populated=572619] buckets[few=572619, none=88996] sources[none] quality[none]
- liquidation_clusters: presence[absent=371683, present=289932] state[empty=371683, populated=289932] buckets[few=235611, none=371683, some=54321] sources[none] quality[none]
- oi_snapshot: presence[absent=88126, present=573489] state[empty=88126, populated=573489] buckets[few=280, many=571358, none=88126, some=1851] sources[none] quality[none]
- order_book: presence[absent=180895, present=480720] state[populated=480720, unavailable=180895] buckets[few=480720, none=180895] sources[book_ticker=480720, unavailable=180895] quality[none=180895, top_of_book_only=480720]
- orderblocks: presence[absent=661615] state[empty=661615] buckets[none=661615] sources[measured_dark=661615] quality[none]
- recent_ticks: presence[present=661615] state[populated=661615] buckets[many=661615] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.304644465446472` sec
- Median create→first breach: `5569.114043474197` sec
- Median create→terminal: `5569.471827030182` sec
- Median first breach→terminal: `7.736682891845703e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.1}, "under_180s": {"count": 1, "pct": 2.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.1}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 1.1442312750142882 | 1.2736631948620494 | 0.898378220890822 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 1.744521546443723 | 1.9648576045667268 | 0.8913691202667853 | 0 | 2 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 1.3528976603304401 | 1.5662713053481818 | 0.8634102609819332 | 0 | 2 |
| MEAN_REVERT | 1 | 1 | 0.7671885370710153 | 0.9871289319225944 | 0.7771918259723081 | 0 | 1 |
| MOVER_TREND_PULLBACK | 33 | 33 | 4.828716704598371 | 3.0 | 1.6126275389943199 | 27 | 6 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 1.0523397525296094 | 1.2053379382995721 | 0.899642754364584 | 0 | 6 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.7163 | 10488.986248016357 | 10489.220619916916 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.7445 | 5789.7519063949585 | 5789.751929402351 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.4118 | 5117.663813471794 | 5117.810329914093 |
| MEAN_REVERT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.047 | 4864.744481086731 | 4865.238183021545 |
| MOVER_TREND_PULLBACK | 33 | 33 | 39.4 | 27.3 | 39.4 | 0.0 | 1.0821 | 3517.2251060009003 | 3517.225156068802 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 33.3 | 44.4 | 33.3 | 0.0 | -0.0819 | 22236.18719291687 | 22236.187227010727 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1500 | 4 | 1019 | 0.0 | 0.0 | None | None | 481 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 5463 | 17 | 4979 | 0.0 | 0.0 | None | None | 484 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-78`
- Gating Δ: `60935`
- No-generation Δ: `647312`
- Fast failures Δ: `-2`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 1.2462, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": -1.2462, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.7638, "current_avg_pnl": -1.7445, "current_win_rate": 0.0, "previous_avg_pnl": -0.9807, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.0367, "current_avg_pnl": 1.0821, "current_win_rate": 39.4, "previous_avg_pnl": 1.0454, "previous_win_rate": 48.1, "win_rate_delta": -8.7}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.2854, "current_avg_pnl": -0.0819, "current_win_rate": 33.3, "previous_avg_pnl": -0.3673, "previous_win_rate": 12.5, "win_rate_delta": 20.8}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -10, "geometry_changed_delta": 0, "geometry_preserved_delta": 143, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -16, "geometry_changed_delta": 0, "geometry_preserved_delta": 10, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
