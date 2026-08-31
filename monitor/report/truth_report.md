# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, MOVER_AVWAP_SCALP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `1134` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 87 | 87 | 81 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6602 | 6602 | 5610 | 32 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 54875 | 54872 | 29 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 48446 | 48461 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 48075 | 46292 | 2139 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 48500 | 47941 | 646 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 50689 | 50607 | 122 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 42914 | 42919 | 9 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 48592 | 48631 | 10 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 48648 | 46749 | 2733 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 58544 | 62497 | 671 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 54906 | 50635 | 7848 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 50228 | 50240 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 48467 | 48494 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 48031 | 47918 | 147 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 49486 | 48290 | 1690 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 47536 | 47825 | 152 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 40008 | 38392 | 1819 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 40218 | 39950 | 379 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 54818 | 54849 | 24 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 42931 | 42942 | 20 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3419 | 3419 | 2685 | 14 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 495 | 495 | 178 | 7 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 26 | 26 | 22 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 9989 | 9989 | 9738 | 21 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 19 | 19 | 6 | 5 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7365 | 7365 | 6585 | 9 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1576 | 1576 | 674 | 73 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 21818 | 21818 | 11643 | 329 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 3 | 3 | 0 | 3 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1054 | 1054 | 753 | 27 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4399 | 4399 | 3994 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 528 | 528 | 341 | 5 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1721 | 1721 | 1288 | 41 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 88 | 88 | 32 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 1918 | 1918 | 109 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=54872): breakout_not_found=29804, basic_filters_failed=13159, move_not_fresh=8408, breakout_stale=2331, retest_proximity_failed=787, insufficient_candles=228, volume_spike_missing=155
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=48461): cls_disabled_merged_into_lsr=48461
- **EVAL::DIVERGENCE_CONTINUATION** (total=46292): cvd_divergence_failed=18434, h1_trend_not_aligned=14065, basic_filters_failed=10359, ema_alignment_reject=2714, retest_proximity_failed=398, missing_fvg_or_orderblock=322
- **EVAL::FAILED_AUCTION_RECLAIM** (total=47941): auction_not_detected=30636, basic_filters_failed=10150, reclaim_hold_failed=3437, tail_too_small=2265, regime_blocked=1449, rsi_reject=4
- **EVAL::FUNDING_EXTREME** (total=50607): funding_not_extreme=36241, basic_filters_failed=11786, ema_alignment_reject=1339, rsi_reject=726, missing_funding_rate=209, momentum_reject=159, cvd_divergence_failed=113, insufficient_candles=19, missing_fvg_or_orderblock=15
- **EVAL::LIQUIDATION_REVERSAL** (total=42919): cascade_threshold_not_met=30743, basic_filters_failed=11494, cvd_divergence_failed=296, rsi_reject=234, insufficient_candles=144, volume_spike_missing=4, missing_fvg_or_orderblock=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=48631): no_ma_cross=37109, basic_filters_failed=10378, ma_cross_htf_misaligned=604, ma_cross_cooldown=497, ma_cross_htf_unconfirmed=43
- **EVAL::MEAN_REVERT** (total=46749): no_extension=40564, basic_filters_failed=6185
- **EVAL::MOVER_AVWAP_SCALP** (total=62497): no_avwap_tag=25506, no_mover_leg=17423, basic_filters_failed=12644, avwap_slope_against=2906, insufficient_candles=1714, avwap_reclaim_no_volume=1356, no_avwap_reclaim=910, anchor_too_recent=38
- **EVAL::MOVER_TREND_PULLBACK** (total=50635): mover_run_too_small=25224, basic_filters_failed=12521, no_reclaim=9378, no_pullback_tag=1783, insufficient_candles=1729
- **EVAL::OPENING_RANGE_BREAKOUT** (total=50240): feature_disabled=50240
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=48494): regime_blocked=26057, breakout_not_found=15222, basic_filters_failed=4761, adx_reject=2378, ema_alignment_reject=76
- **EVAL::QUIET_COMPRESSION_BREAK** (total=47918): regime_blocked=23713, compression_not_detected=14246, basic_filters_failed=5371, breakout_not_detected=4117, volume_confirmation_failed=446, rsi_reject=20, missing_fvg_or_orderblock=5
- **EVAL::RANGE_FADE** (total=48290): no_range_edge=42100, basic_filters_failed=6190
- **EVAL::SR_FLIP_RETEST** (total=47825): flip_close_not_confirmed=31055, basic_filters_failed=10110, h1_break_not_confirmed=1568, retest_out_of_zone=1473, regime_blocked=1432, long_break_volume_thin=1241, reclaim_hold_failed=597, ema_alignment_reject=129, long_acceptance_not_held=128, wick_quality_failed=43, whipsaw_flip=35, missing_fvg_or_orderblock=14
- **EVAL::STANDARD** (total=38392): momentum_reject=13591, adx_reject=9457, basic_filters_failed=4805, sweeps_not_detected=4710, macd_reject=2739, ema_alignment_reject=2461, htf_poi_unanchored=570, rsi_reject=30, invalid_sl_geometry=17, mtf_reject=12
- **EVAL::TREND_PULLBACK** (total=39950): h1_trend_not_aligned=15849, ema_alignment_reject=5856, basic_filters_failed=5164, h1_pullback_not_confirmed=3477, ema_not_tested_prev=2935, no_ema_reclaim_close=2926, rsi_reject=1384, body_conviction_fail=1306, prev_already_below_emas=329, no_prev_low_break=256, prev_already_above_emas=184, no_prev_high_break=121, momentum_flat=88, ema21_not_tagged=48, missing_fvg_or_orderblock=22, momentum_reject=5
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=54849): breakout_not_found=32356, basic_filters_failed=13156, move_not_fresh=5704, breakout_stale=2414, retest_proximity_failed=804, insufficient_candles=228, volume_spike_missing=176, missing_fvg_or_orderblock=11
- **EVAL::WHALE_MOMENTUM** (total=42942): momentum_reject=31046, recent_ticks_insufficient=8600, basic_filters_failed=3293, insufficient_candles=3

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=36): execution:overextended=36
- **DIVERGENCE_CONTINUATION** (total=80): setup_compat:regime_VOLATILE_UNSUITABLE=73, setup_compat:regime_BREAKOUT_EXPANSION=7
- **FAILED_AUCTION_RECLAIM** (total=1167): setup_compat:regime_STRONG_TREND=657, execution:overextended=381, context_floor=129
- **FUNDING_EXTREME_SIGNAL** (total=426): execution:trigger_not_confirmed=426
- **LIQUIDATION_REVERSAL** (total=26): execution:trigger_not_confirmed=26
- **LIQUIDITY_SWEEP_REVERSAL** (total=2815): execution:trigger_not_confirmed=949, execution:overextended=945, setup_compat:regime_STRONG_TREND=921
- **MA_CROSS_TREND_SHIFT** (total=14): setup_compat:regime_CLEAN_RANGE=7, setup_compat:regime_DIRTY_RANGE=3, execution:trigger_not_confirmed=3, execution:overextended=1
- **MEAN_REVERT** (total=5115): setup_compat:regime_STRONG_TREND=2758, setup_compat:regime_WEAK_TREND=1800, execution:overextended=557
- **MOVER_AVWAP_SCALP** (total=1352): execution:overextended=964, entry_quality=240, execution:trigger_not_confirmed=148
- **MOVER_TREND_PULLBACK** (total=10081): execution:trigger_not_confirmed=4907, execution:overextended=3569, entry_quality=1605
- **QUIET_COMPRESSION_BREAK** (total=21): execution:trigger_not_confirmed=14, execution:overextended=7
- **RANGE_FADE** (total=3367): setup_compat:regime_STRONG_TREND=1944, setup_compat:regime_WEAK_TREND=1040, execution:overextended=262, setup_compat:regime_VOLATILE_UNSUITABLE=113, context_edge=8
- **TREND_PULLBACK_EMA** (total=1484): setup_compat:regime_CLEAN_RANGE=947, setup_compat:regime_DIRTY_RANGE=371, entry_quality=125, setup_compat:regime_VOLATILE_UNSUITABLE=41
- **WHALE_MOMENTUM** (total=1594): execution:trigger_not_confirmed=1557, context_floor=37

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 108905 | 35.1% |
| TRENDING_DOWN | 81659 | 26.3% |
| QUIET | 56277 | 18.1% |
| TRENDING_UP | 53030 | 17.1% |
| VOLATILE | 10483 | 3.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **267**
- Average confidence gap to threshold: **14.39** (samples=267) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=56, BNBUSDT=25, SUIUSDT=21, BTWUSDT=17, ONGUSDT=15, AVAXUSDT=14, FILUSDT=11, LINKUSDT=10, LTCUSDT=9, 1000PEPEUSDT=9

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 6 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 182 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 281 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 168 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 24 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 69 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 8 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 23 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 11 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 56 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 6 |
| MEAN_REVERT | filtered | min_confidence | 15 |
| MEAN_REVERT | kept | min_confidence_pass | 78 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 94 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 369 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 571 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 54 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3124 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 3 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 136 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 41 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 84 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 4 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 33 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 6 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 160 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 48 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 8 |
| WHALE_MOMENTUM | filtered | min_confidence | 159 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 46 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 6 | 74.50 | 65.00 | -9.50 | 19.50 | 15.30 | 20.00 | 4.50 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 182 | 59.89 | 64.98 | 5.09 | 20.89 | 19.90 | 17.63 | 1.00 | 9.58 |
| DIVERGENCE_CONTINUATION | kept | 281 | 70.32 | 65.00 | -5.32 | 20.86 | 19.66 | 18.04 | 1.11 | 1.83 |
| FAILED_AUCTION_RECLAIM | filtered | 192 | 53.15 | 63.71 | 10.56 | 21.11 | 18.77 | 20.00 | 2.98 | 4.31 |
| FAILED_AUCTION_RECLAIM | kept | 69 | 67.85 | 65.00 | -2.85 | 21.72 | 19.16 | 20.00 | 2.08 | 1.18 |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 44.05 | 63.00 | 18.95 | 19.44 | 15.40 | 17.76 | 3.50 | 7.92 |
| FUNDING_EXTREME_SIGNAL | kept | 23 | 66.56 | 65.00 | -1.56 | 18.92 | 16.84 | 16.93 | 3.04 | 2.70 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 12 | 60.48 | 62.67 | 2.19 | 21.00 | 17.18 | 17.00 | 2.92 | 9.13 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 56 | 68.91 | 65.00 | -3.91 | 21.08 | 19.46 | 17.36 | 0.98 | -0.02 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 44.70 | 63.00 | 18.30 | 21.20 | 18.60 | 15.80 | 0.00 | 10.80 |
| MA_CROSS_TREND_SHIFT | kept | 6 | 70.55 | 65.00 | -5.55 | 20.60 | 18.02 | 15.80 | 0.00 | 1.20 |
| MEAN_REVERT | filtered | 15 | 58.94 | 61.80 | 2.86 | 21.21 | 15.63 | 16.32 | 0.00 | 10.40 |
| MEAN_REVERT | kept | 78 | 71.85 | 65.00 | -6.85 | 21.00 | 16.70 | 16.36 | 0.00 | 3.78 |
| MOVER_AVWAP_SCALP | filtered | 95 | 59.19 | 64.62 | 5.43 | 20.62 | 14.54 | 15.80 | 4.01 | 17.04 |
| MOVER_AVWAP_SCALP | kept | 369 | 81.14 | 65.00 | -16.14 | 19.85 | 15.61 | 15.80 | 4.15 | 1.40 |
| MOVER_TREND_PULLBACK | filtered | 625 | 54.72 | 64.32 | 9.60 | 19.76 | 18.63 | 15.80 | 4.05 | 17.06 |
| MOVER_TREND_PULLBACK | kept | 3124 | 76.77 | 65.00 | -11.77 | 20.10 | 18.64 | 15.80 | 4.23 | 0.62 |
| POST_DISPLACEMENT_CONTINUATION | kept | 3 | 74.23 | 65.00 | -9.23 | 20.20 | 20.00 | 18.00 | 4.50 | 5.67 |
| QUIET_COMPRESSION_BREAK | filtered | 177 | 55.44 | 64.91 | 9.47 | 21.04 | 19.52 | 20.00 | 0.00 | 6.31 |
| QUIET_COMPRESSION_BREAK | kept | 84 | 73.41 | 65.00 | -8.41 | 21.73 | 19.37 | 20.00 | 0.00 | -0.08 |
| SR_FLIP_RETEST | filtered | 4 | 43.52 | 65.00 | 21.48 | 20.90 | 20.00 | 15.20 | 2.50 | 25.52 |
| SR_FLIP_RETEST | kept | 33 | 72.96 | 65.00 | -7.96 | 20.88 | 20.00 | 15.82 | 1.68 | 1.68 |
| TREND_PULLBACK_EMA | filtered | 6 | 59.70 | 65.00 | 5.30 | 18.03 | 20.00 | 17.60 | 4.50 | 0.00 |
| TREND_PULLBACK_EMA | kept | 160 | 77.46 | 65.00 | -12.46 | 21.38 | 19.85 | 19.00 | 4.67 | -0.30 |
| VOLUME_SURGE_BREAKOUT | filtered | 48 | 57.82 | 64.58 | 6.76 | 18.37 | 18.67 | 19.87 | 4.31 | 4.00 |
| VOLUME_SURGE_BREAKOUT | kept | 8 | 78.75 | 65.00 | -13.75 | 16.47 | 18.20 | 20.00 | 5.44 | 2.75 |
| WHALE_MOMENTUM | filtered | 205 | 40.09 | 64.53 | 24.44 | 23.78 | 15.44 | 17.00 | 0.00 | 29.66 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 6 | 74.50 | 17.00 | 18.00 | 12.00 | 11.00 | 5.00 | 10.00 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 182 | 59.89 | 22.23 | 15.51 | 4.88 | 11.87 | 5.09 | 8.88 | 1.00 |
| DIVERGENCE_CONTINUATION | kept | 281 | 70.32 | 23.32 | 17.04 | 5.04 | 11.96 | 5.59 | 8.93 | 1.11 |
| FAILED_AUCTION_RECLAIM | filtered | 192 | 53.15 | 22.12 | 15.06 | 7.08 | 13.10 | 5.98 | 5.04 | 2.98 |
| FAILED_AUCTION_RECLAIM | kept | 69 | 67.85 | 21.72 | 14.29 | 4.00 | 13.33 | 7.36 | 6.24 | 2.08 |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 44.05 | 25.00 | 8.00 | 7.88 | 12.50 | 6.62 | 3.48 | 3.50 |
| FUNDING_EXTREME_SIGNAL | kept | 23 | 66.56 | 21.87 | 14.09 | 4.04 | 10.30 | 8.04 | 7.99 | 3.04 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 12 | 60.48 | 25.00 | 14.00 | 6.75 | 12.17 | 5.00 | 3.78 | 2.92 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 56 | 68.91 | 23.29 | 16.07 | 3.48 | 11.62 | 5.31 | 8.39 | 0.98 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 44.70 | 17.00 | 14.00 | 7.50 | 15.50 | 8.50 | 8.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 6 | 70.55 | 19.67 | 14.00 | 7.50 | 14.50 | 7.42 | 8.67 | 0.00 |
| MEAN_REVERT | filtered | 15 | 58.94 | 17.00 | 16.67 | 11.00 | 13.00 | 5.00 | 6.67 | 0.00 |
| MEAN_REVERT | kept | 78 | 71.85 | 23.74 | 14.92 | 11.46 | 12.81 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 95 | 59.19 | 19.19 | 18.02 | 11.53 | 14.00 | 5.65 | 6.67 | 4.01 |
| MOVER_AVWAP_SCALP | kept | 369 | 81.14 | 19.60 | 18.06 | 13.33 | 13.90 | 7.12 | 7.60 | 4.15 |
| MOVER_TREND_PULLBACK | filtered | 625 | 54.72 | 18.08 | 18.14 | 7.98 | 11.65 | 6.20 | 9.00 | 4.05 |
| MOVER_TREND_PULLBACK | kept | 3124 | 76.77 | 18.68 | 18.03 | 7.90 | 12.76 | 6.61 | 9.28 | 4.23 |
| POST_DISPLACEMENT_CONTINUATION | kept | 3 | 74.23 | 10.67 | 18.00 | 15.00 | 15.00 | 7.83 | 8.90 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 177 | 55.44 | 18.85 | 17.07 | 10.86 | 14.19 | 6.89 | 5.45 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 84 | 73.41 | 18.71 | 17.19 | 10.54 | 14.11 | 7.18 | 8.21 | 0.00 |
| SR_FLIP_RETEST | filtered | 4 | 43.52 | 25.00 | 8.00 | 3.75 | 16.25 | 8.50 | 5.05 | 2.50 |
| SR_FLIP_RETEST | kept | 33 | 72.96 | 20.64 | 18.00 | 4.00 | 15.52 | 5.76 | 9.14 | 1.68 |
| TREND_PULLBACK_EMA | filtered | 6 | 59.70 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 8.70 | 4.50 |
| TREND_PULLBACK_EMA | kept | 160 | 77.46 | 18.41 | 18.00 | 7.58 | 14.18 | 6.03 | 9.63 | 4.67 |
| VOLUME_SURGE_BREAKOUT | filtered | 48 | 57.82 | 17.67 | 17.67 | 12.25 | 13.06 | 5.22 | 6.64 | 4.31 |
| VOLUME_SURGE_BREAKOUT | kept | 8 | 78.75 | 25.00 | 14.50 | 12.00 | 12.50 | 5.00 | 8.94 | 5.44 |
| WHALE_MOMENTUM | filtered | 205 | 40.09 | 23.05 | 15.51 | 5.43 | 12.23 | 6.13 | 7.40 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 6 | 74.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 182 | 59.89 | 0.00 | 0.00 | 1.96 | 0.00 | 0.33 | 0.23 | 0.00 | 0.00 | **2.52** |
| DIVERGENCE_CONTINUATION | kept | 281 | 70.32 | 0.00 | 0.00 | 0.21 | 0.00 | 0.03 | 0.02 | 0.00 | 0.00 | **0.26** |
| FAILED_AUCTION_RECLAIM | filtered | 192 | 53.15 | 0.00 | 0.00 | 0.23 | 0.00 | 1.68 | 0.00 | 0.00 | 0.00 | **1.91** |
| FAILED_AUCTION_RECLAIM | kept | 69 | 67.85 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.67** |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 44.05 | 0.00 | 0.00 | 1.80 | 0.00 | 3.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| FUNDING_EXTREME_SIGNAL | kept | 23 | 66.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 12 | 60.48 | 0.00 | 0.00 | 7.33 | 0.00 | 1.80 | 0.00 | 0.00 | 0.00 | **9.13** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 56 | 68.91 | 0.00 | 0.00 | 0.09 | 0.00 | 0.21 | 0.00 | 0.00 | 0.00 | **0.30** |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 44.70 | 0.00 | 0.00 | 0.00 | 0.00 | 10.80 | 0.00 | 0.00 | 0.00 | **10.80** |
| MA_CROSS_TREND_SHIFT | kept | 6 | 70.55 | 0.00 | 0.00 | 0.00 | 0.00 | 1.20 | 0.00 | 0.00 | 0.00 | **1.20** |
| MEAN_REVERT | filtered | 15 | 58.94 | 0.00 | 0.00 | 0.00 | 0.00 | 10.40 | 0.00 | 0.00 | 0.00 | **10.40** |
| MEAN_REVERT | kept | 78 | 71.85 | 0.00 | 0.00 | 0.00 | 0.00 | 3.78 | 0.00 | 0.00 | 0.00 | **3.78** |
| MOVER_AVWAP_SCALP | filtered | 95 | 59.19 | 0.00 | 0.00 | 2.27 | 0.00 | 3.64 | 0.16 | 0.00 | 0.65 | **6.72** |
| MOVER_AVWAP_SCALP | kept | 369 | 81.14 | 0.07 | 0.00 | 0.41 | 0.00 | 0.56 | 0.23 | 0.00 | 0.19 | **1.46** |
| MOVER_TREND_PULLBACK | filtered | 625 | 54.72 | 0.07 | 0.00 | 1.61 | 0.00 | 1.69 | 0.12 | 0.00 | 0.00 | **3.49** |
| MOVER_TREND_PULLBACK | kept | 3124 | 76.77 | 0.01 | 0.00 | 0.39 | 0.00 | 0.19 | 0.04 | 0.00 | 0.00 | **0.63** |
| POST_DISPLACEMENT_CONTINUATION | kept | 3 | 74.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 177 | 55.44 | 0.00 | 0.00 | 0.49 | 0.00 | 0.85 | 0.20 | 0.00 | 2.91 | **4.45** |
| QUIET_COMPRESSION_BREAK | kept | 84 | 73.41 | 0.00 | 0.00 | 0.00 | 0.00 | 0.54 | 0.00 | 0.00 | 0.20 | **0.74** |
| SR_FLIP_RETEST | filtered | 4 | 43.52 | 0.00 | 0.00 | 10.80 | 0.00 | 5.40 | 0.00 | 0.00 | 2.70 | **18.90** |
| SR_FLIP_RETEST | kept | 33 | 72.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.30 | 0.00 | 0.00 | **0.30** |
| TREND_PULLBACK_EMA | filtered | 6 | 59.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 160 | 77.46 | 0.00 | 0.00 | 0.88 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.88** |
| VOLUME_SURGE_BREAKOUT | filtered | 48 | 57.82 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 1.38 | **1.88** |
| VOLUME_SURGE_BREAKOUT | kept | 8 | 78.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.25 | 0.00 | 0.00 | **1.25** |
| WHALE_MOMENTUM | filtered | 205 | 40.09 | 0.00 | 0.00 | 0.00 | 0.00 | 1.58 | 0.09 | 0.00 | 0.00 | **1.67** |

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
- Outcomes recorded: **62660 held of 138182 seen** across 21 strategies; 1411 cells past the sample floor; **575 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 27692 | 125/27567/0 | 43% | -0.17 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.13R) |
| MOVER_AVWAP_SCALP | 7733 | 31/7702/0 | 42% | -0.24 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 5227 | 23/5204/0 | 41% | -0.23 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| DIVERGENCE_CONTINUATION | 3329 | 8/3321/0 | 52% | +0.01 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (+1.04R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL (-1.19R) |
| TREND_PULLBACK_EMA | 3152 | 2/3150/0 | 44% | -0.19 | ASIA/QUIET/EXPANDED/BTC_RISING (+0.54R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.24R) |
| SHADOW_MEAN_REVERT | 3099 | 0/0/3099 | 42% | -0.12 | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.43R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.34R) |
| QUIET_COMPRESSION_BREAK | 2765 | 38/2727/0 | 46% | -0.13 | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.02R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.09R) |
| SHADOW_RANGE_FADE | 2509 | 0/0/2509 | 36% | -0.08 | LONDON/RANGE/EXPANDED/BTC_NEUTRAL (+0.42R) | OFF_HOURS/MARKUP/NORMAL/BTC_RISING (-0.88R) |
| SHADOW_FUNDING_FADE | 1749 | 0/0/1749 | 38% | -0.36 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | ASIA/MARKUP/NORMAL/BTC_RISING (-0.91R) |
| WHALE_MOMENTUM | 1734 | 2/1732/0 | 43% | -0.33 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 732 | 8/724/0 | 40% | -0.28 | ASIA/RANGE/NORMAL/BTC_FALLING (+0.01R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.13R) |
| FUNDING_EXTREME_SIGNAL | 700 | 0/700/0 | 26% | -0.58 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OFF_HOURS/QUIET/COMPRESSED/BTC_RISING (-1.20R) |
| VOLUME_SURGE_BREAKOUT | 678 | 0/678/0 | 49% | -0.07 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| MEAN_REVERT | 660 | 2/658/0 | 74% | +0.49 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| SHADOW_CASCADE_REVERSAL | 305 | 0/0/305 | 55% | -0.04 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.22R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.31R) |
| SR_FLIP_RETEST | 250 | 0/250/0 | 61% | -0.14 | ASIA/MARKDOWN/NORMAL/BTC_FALLING/ALTCOIN (+0.72R) | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+0.25R) |
| BREAKDOWN_SHORT | 176 | 10/166/0 | 19% | -0.58 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| RANGE_FADE | 96 | 0/96/0 | 21% | -0.62 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| MA_CROSS_TREND_SHIFT | 38 | 0/38/0 | 37% | -0.18 | — | — |
| LIQUIDATION_REVERSAL | 34 | 0/34/0 | 6% | -1.06 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 2 | 0/2/0 | 100% | +0.56 | — | — |

- **Strongest cells**: `FAILED_AUCTION_RECLAIM @ OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN` +1.55R (n=22, STRONG); `FAILED_AUCTION_RECLAIM @ OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING` +1.44R (n=23, STRONG); `FAILED_AUCTION_RECLAIM @ NY/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +1.42R (n=34, STRONG)
- **Weakest cells**: `SHADOW_MEAN_REVERT @ OVERLAP/QUIET/NORMAL/BTC_NEUTRAL` -1.34R (n=18, NEGATIVE); `TREND_PULLBACK_EMA @ NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.24R (n=50, NEGATIVE); `TREND_PULLBACK_EMA @ ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.24R (n=18, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 66 | 26% / -0.57R | 66 | 44% / -0.16R | +0.41 | **ATR** |
| TREND_PULLBACK_EMA | 258 | 48% / -0.14R | 258 | 56% / -0.03R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 188 | 43% / -0.32R | 188 | 44% / -0.23R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 368 | 44% / -0.17R | 368 | 46% / -0.09R | +0.08 | **ATR** |
| MOVER_TREND_PULLBACK | 4038 | 51% / -0.08R | 4038 | 55% / +0.00R | +0.08 | **ATR** |
| MEAN_REVERT | 51 | 59% / +0.14R | 51 | 59% / +0.21R | +0.07 | **ATR** |
| MOVER_AVWAP_SCALP | 545 | 48% / -0.13R | 545 | 53% / -0.06R | +0.07 | **ATR** |
| BREAKDOWN_SHORT | 15 | 27% / -0.14R | 15 | 27% / -0.09R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 167 | 52% / -0.15R | 167 | 54% / -0.11R | +0.05 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 46 | 48% / -0.00R | 46 | 54% / +0.03R | +0.04 | **ATR** |
| SR_FLIP_RETEST | 39 | 46% / -0.30R | 39 | 46% / -0.27R | +0.03 | **ATR** |
| DIVERGENCE_CONTINUATION | 315 | 52% / -0.03R | 315 | 57% / -0.04R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 406 | 44% / -0.18R | 406 | 44% / -0.18R | -0.00 | **FIXED** |
| RANGE_FADE | 10 | 40% / +0.10R | 10 | 40% / -0.06R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 12 | 33% / -0.24R | 12 | 33% / -0.17R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 3 | 67% / -0.02R | 3 | 67% / +0.05R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 4 | 25% / -0.64R | 4 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 6159 | 32% | -0.17R | 259 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 545 | 51% | -0.06R | 134 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 31 | 61% | +0.05R | 27 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 70 | 33% / -0.23R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 386 | 42% / +0.10R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 5095 | 37% / -0.11R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 664 | 36% / +0.05R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 273 | 40% / +0.04R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 349 | 43% / +0.20R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 334 | 38% / -0.09R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 180 | 48% / -0.06R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 68 | 31% / -0.39R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 72 | 29% / -0.67R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 44 | 59% / +0.17R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 30 | 40% / -0.11R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 10 | 50% / +0.45R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 39 | 31% / -0.37R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 16 | 19% / -0.52R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 6 | 33% / -0.14R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 2 | 100% / +1.06R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 52 · alerting: **4** · boot grace active: False
- **ALERT** `dark_resolution` — 16 of 197 open dark rows are not being advanced (worst: LDOUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 156/120) (sustained 156 cycles)
- **ALERT** `edge_reconciliation` — FAILED_AUCTION_RECLAIM realized−counterfactual=+0.78R (bound 0.3) (streak 482/6) (sustained 482 cycles)
- **ALERT** `range_fade_emission` — 1685 detections since last emission (emitted_total=0) — and only 96 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 104/6) (sustained 104 cycles)
- **ALERT** `tuned_variants` — 502 non-stamps — atr_arm_uncomputable=502 (seen=6777 stamped=1013 skipped=5262) (streak 482/6) (sustained 482 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 138240181 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 27 arms current, none stalled; covering 376/376 signals (100%) | 0 |
| auto_dispatch | ok | attempts=41 fanouts=41 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 77981.30 | 0 |
| candle_coverage | ok | 90/90 symbols with ≥20 15m candles, 89/90 updated within 45m [stale=1, fresh=89; 76 Tier-1 futures + 16 promoted movers monitored]; 1 Tier-1 CORE pair(s) unusable (e.g. XAUTUSDT) | 0 |
| candle_series_integrity | ok | merge dropped 356 dup bars, 0 undedupable; ws 0 out-of-order, 299 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 31 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 31 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +20 / upstream +18 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1686/1703 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 9 promoted today, nothing refused | 0 |
| dark_resolution | violating | 16 of 197 open dark rows are not being advanced (worst: LDOUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 156/120) | 156 |
| dark_sar_arms | ok | no open arms; covering 1685/1702 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 53335108 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | FAILED_AUCTION_RECLAIM realized−counterfactual=+0.78R (bound 0.3) (streak 482/6) | 482 |
| emission_controller | ok | last cycle 1337s ago; live_overrides=12 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4396 stamps (MEAN_REVERT=462, MOVER_AVWAP_SCALP=154, MOVER_TREND_PULLBACK=3370, RANGE_FADE=209, TREND_PULLBACK_EMA=201), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | 10255 evaluated, 3574 suppressed, 6681 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m | 0 |
| footprint_bars | ok | 5280 sealed bars over 44 symbols; 1500 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +3 / upstream +133 | 0 |
| indicator_cache_key | ok | 197978 frozen value(s) avoided; 700440 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | emitted_total=12 | 0 |
| mean_revert_path | ok | output +27 / upstream +133 | 0 |
| mover_admission_metadata | ok | 883 symbols known, 180 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 16 held, 16 with scan counts, 15 with an activity reading (enforcing) | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2966 rows held, 909540 evicted (sampled: execution:trigger_not_confirmed 400/332149, execution:overextended 400/316143, setup_compat:regime_STRONG_TREND 400/122123) | 0 |
| price_action_lane | ok | 727422 evaluated, 1085 emitted; layer1 1085 stamped / 0 blind; cooldown=86073, delta_opposed=60028, no_footprint=267907, no_levels=629, no_opposing_target=872, no_sweep=254780, rr_below_floor=56048 | 0 |
| promoted_pair_integrity | ok | 16/16 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 1685 detections since last emission (emitted_total=0) — and only 96 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 104/6) | 104 |
| range_fade_path | violating | upstream +133 but output +0 (streak 1/72) | 1 |
| sar_alignment_crosscheck | ok | 1075/27912 disagreed (3.9%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +133 | 0 |
| sar_hold_arm | ok | 632 held arms settled, 111 unscored, 27 still walking (24 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 8/69 unfetchable (12%); top cause: located bar does not contain the stamp; symbols: 1000SHIBUSDT, BICOUSDT, CAKEUSDT, MAGMAUSDT, ONGUSDT +2 more | 0 |
| sar_live_arms | ok | 27 arms current, none stalled; covering 385/385 signals (100%) | 0 |
| sar_refresh_budget | ok | 1 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 469 records await one (61 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 34.36s, worst 256.13s over 8704 lifetime cycles; lifetime 202 over 60s, 9 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.98s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 293505 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| snapshot_writer | ok | last cycle 1s ago (0.2s to run, worst 117.15s), 1539 overrun(s) of 9551 cycles, TTL 900s; slowest signals=0.07s, data_intake=0.05s, activity=0.03s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=124, gate reads=0, withheld=124) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +18 / upstream +133 | 0 |
| structural_snap | ok | 4421/4421 measured, 9 blind, 0 levels moved (refusals: redetect_cooldown=1512) | 0 |
| structural_veto_lane | ok | 2497 stamped; 0 with no readable level book, 79 with clear air ahead, 1886 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +133 / upstream +18 | 0 |
| tuned_variants | violating | 502 non-stamps — atr_arm_uncomputable=502 (seen=6777 stamped=1013 skipped=5262) (streak 482/6) | 482 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1537623`
- `Path funnel` emissions: `37`
- `Regime distribution` emissions: `37`
- `QUIET_SCALP_BLOCK` events: `267`
- `confidence_gate` events: `5871`
- `free_channel_post` events: `30`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **16**
- Total REST-fallback activations: **2**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 2 | 11668 | 11668 | 18782 | 0 |
| futures_aggtrade | 8 | 2234 | 3960 | 9096 | 0 |
| futures_liq | 3 | 11237 | 11237 | 12464 | 0 |
| futures_mover | 3 | 22332 | 22332 | 24253 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 2 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **30**

| Source | Count |
|---|---:|
| signal_close | 27 |
| regime_shift | 3 |

- By severity: HIGH=30

## Dependency readiness
- cvd: presence[present=244339] state[populated=244339] buckets[few=13, many=244245, some=81] sources[none] quality[none]
- funding_rate: presence[absent=20525, present=223814] state[empty=20525, populated=223814] buckets[few=223814, none=20525] sources[none] quality[none]
- liquidation_clusters: presence[absent=132810, present=111529] state[empty=132810, populated=111529] buckets[few=86189, none=132810, some=25340] sources[none] quality[none]
- oi_snapshot: presence[absent=20525, present=223814] state[empty=20525, populated=223814] buckets[few=246, many=222363, none=20525, some=1205] sources[none] quality[none]
- order_book: presence[absent=92964, present=151375] state[populated=151375, unavailable=92964] buckets[few=151375, none=92964] sources[book_ticker=151375, unavailable=92964] quality[none=92964, top_of_book_only=151375]
- orderblocks: presence[absent=244339] state[empty=244339] buckets[none=244339] sources[measured_dark=244208, not_implemented=131] quality[none]
- recent_ticks: presence[absent=1723, present=242616] state[empty=1723, populated=242616] buckets[many=242616, none=1723] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `16.186275959014893` sec
- Median create→first breach: `6310.6109030246735` sec
- Median create→terminal: `6312.201467990875` sec
- Median first breach→terminal: `5.374413967132568` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.7999999999999967 | 1.46938297623229 | 0.5444462151394405 | 0 | 1 |
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.86035647767142 | 1.2722906108670784 | 0.7165261026662585 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.8177856249195743 | 0.9352614821452423 | 0.865752331658487 | 0 | 2 |
| MOVER_AVWAP_SCALP | 4 | 4 | 2.2540540800330815 | 2.2564069262577284 | 1.0433477894396854 | 3 | 1 |
| MOVER_TREND_PULLBACK | 13 | 13 | 4.117388536981609 | 3.0 | 1.3866062291983592 | 10 | 3 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 0.9671932046348776 | 1.0598679516463236 | 0.854478587490568 | 0 | 3 |
| WHALE_MOMENTUM | 1 | 1 | 0.24717574114855842 | 1.5827847586743036 | 0.15616510065183212 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 158013.3000190258 | 158018.20085310936 |
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 7046.441725969315 | 7052.110954403877 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.6684 | 7772.963224887848 | 7779.447725534439 |
| MOVER_AVWAP_SCALP | 4 | 4 | 0.0 | 0.0 | 0.0 | 0.0 | 1.2342 | 3094.039284467697 | 3102.216162443161 |
| MOVER_TREND_PULLBACK | 13 | 13 | 0.0 | 61.5 | 0.0 | 0.0 | -1.5732 | 4337.6860020160675 | 4341.021839857101 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 25.0 | 50.0 | 25.0 | 0.0 | 0.1516 | 48473.99691295624 | 48477.78891599178 |
| WHALE_MOMENTUM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.5828 | 170751.5905561447 | 170760.57689118385 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 528 | 5 | 341 | 0.0 | 0.0 | None | None | 187 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1721 | 41 | 1288 | 0.0 | 0.0 | None | None | 433 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `227`
- Gating Δ: `-12047`
- No-generation Δ: `-492417`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.8632, "current_avg_pnl": 1.2342, "current_win_rate": 0.0, "previous_avg_pnl": 0.371, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -3.1608, "current_avg_pnl": -1.5732, "current_win_rate": 0.0, "previous_avg_pnl": 1.5876, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 1.2127, "current_avg_pnl": 0.1516, "current_win_rate": 25.0, "previous_avg_pnl": -1.0611, "previous_win_rate": 0.0, "win_rate_delta": 25.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": 184, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 28, "geometry_changed_delta": 0, "geometry_preserved_delta": 188, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
