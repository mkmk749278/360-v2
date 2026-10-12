# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `1635` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 46 | 46 | 46 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10293 | 10293 | 10071 | 6 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 59004 | 59040 | 2 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 57945 | 57945 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 57420 | 55351 | 2569 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 57990 | 57343 | 713 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 58884 | 58727 | 189 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 49422 | 49441 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 58065 | 58107 | 11 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 58127 | 55807 | 3296 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 63315 | 67781 | 730 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 59046 | 54963 | 8274 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 58180 | 58180 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 57951 | 57974 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 57386 | 57078 | 338 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 59120 | 57847 | 1720 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 56649 | 57153 | 183 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 47699 | 45716 | 2192 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 47919 | 47520 | 486 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 58965 | 58981 | 17 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 49448 | 49479 | 3 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3905 | 3905 | 3596 | 3 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 898 | 898 | 696 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 22 | 22 | 22 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 13785 | 13785 | 13451 | 30 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 18 | 18 | 14 | 3 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8777 | 8777 | 7442 | 3 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2554 | 2554 | 2038 | 28 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 26748 | 26748 | 22663 | 123 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 30 | 30 | 30 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1467 | 1467 | 1355 | 18 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4079 | 4079 | 3779 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 751 | 751 | 661 | 7 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2202 | 2202 | 2072 | 24 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 99 | 99 | 70 | 3 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 957 | 957 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=59040): breakout_not_found=40479, basic_filters_failed=11288, move_not_fresh=4665, breakout_stale=2059, retest_proximity_failed=373, volume_spike_missing=166, missing_fvg_or_orderblock=7, move_exhausted=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=57945): cls_disabled_merged_into_lsr=57945
- **EVAL::DIVERGENCE_CONTINUATION** (total=55351): cvd_divergence_failed=29744, h1_trend_not_aligned=12274, basic_filters_failed=8302, ema_alignment_reject=4462, retest_proximity_failed=299, missing_fvg_or_orderblock=270
- **EVAL::FAILED_AUCTION_RECLAIM** (total=57343): auction_not_detected=41942, basic_filters_failed=8124, reclaim_hold_failed=3704, tail_too_small=2241, regime_blocked=1291, rsi_reject=41
- **EVAL::FUNDING_EXTREME** (total=58727): funding_not_extreme=46294, basic_filters_failed=8825, missing_funding_rate=1569, ema_alignment_reject=1230, rsi_reject=428, cvd_divergence_failed=206, momentum_reject=148, missing_fvg_or_orderblock=27
- **EVAL::LIQUIDATION_REVERSAL** (total=49441): cascade_threshold_not_met=40183, basic_filters_failed=8908, rsi_reject=174, cvd_divergence_failed=163, volume_spike_missing=9, missing_fvg_or_orderblock=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=58107): no_ma_cross=48140, basic_filters_failed=8318, ma_cross_cooldown=1250, ma_cross_htf_misaligned=399
- **EVAL::MEAN_REVERT** (total=55807): no_extension=49699, basic_filters_failed=6108
- **EVAL::MOVER_AVWAP_SCALP** (total=67781): no_avwap_tag=25116, no_mover_leg=23149, basic_filters_failed=11561, avwap_slope_against=4826, avwap_reclaim_no_volume=2099, no_avwap_reclaim=941, anchor_too_recent=89
- **EVAL::MOVER_TREND_PULLBACK** (total=54963): mover_run_too_small=33260, basic_filters_failed=11434, no_reclaim=8938, no_pullback_tag=1331
- **EVAL::OPENING_RANGE_BREAKOUT** (total=58180): feature_disabled=58180
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=57974): regime_blocked=36008, breakout_not_found=16901, basic_filters_failed=2546, adx_reject=2453, ema_alignment_reject=66
- **EVAL::QUIET_COMPRESSION_BREAK** (total=57078): regime_blocked=23088, compression_not_detected=18676, breakout_not_detected=8700, basic_filters_failed=5564, volume_confirmation_failed=1004, rsi_reject=39, missing_fvg_or_orderblock=4, macd_reject=3
- **EVAL::RANGE_FADE** (total=57847): no_range_edge=51731, basic_filters_failed=6116
- **EVAL::SR_FLIP_RETEST** (total=57153): flip_close_not_confirmed=41502, basic_filters_failed=8102, retest_out_of_zone=1945, long_break_volume_thin=1888, h1_break_not_confirmed=1420, regime_blocked=1274, reclaim_hold_failed=730, long_acceptance_not_held=96, ema_alignment_reject=90, wick_quality_failed=77, whipsaw_flip=17, missing_fvg_or_orderblock=12
- **EVAL::STANDARD** (total=45716): momentum_reject=14789, adx_reject=11512, sweeps_not_detected=6280, macd_reject=4522, basic_filters_failed=4373, ema_alignment_reject=3185, htf_poi_unanchored=979, rsi_reject=43, invalid_sl_geometry=18, mtf_reject=15
- **EVAL::TREND_PULLBACK** (total=47520): h1_trend_not_aligned=12938, ema_alignment_reject=11077, basic_filters_failed=4983, no_ema_reclaim_close=4443, h1_pullback_not_confirmed=4063, ema_not_tested_prev=3882, body_conviction_fail=2646, rsi_reject=1981, prev_already_above_emas=540, prev_already_below_emas=325, no_prev_high_break=260, no_prev_low_break=166, momentum_flat=131, ema21_not_tagged=63, missing_fvg_or_orderblock=19, momentum_reject=3
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=58981): breakout_not_found=34771, basic_filters_failed=11284, move_not_fresh=9047, breakout_stale=3215, retest_proximity_failed=502, volume_spike_missing=154, missing_fvg_or_orderblock=8
- **EVAL::WHALE_MOMENTUM** (total=49479): momentum_reject=34892, recent_ticks_insufficient=11667, basic_filters_failed=2920

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=11): execution:overextended=11
- **DIVERGENCE_CONTINUATION** (total=584): setup_compat:regime_VOLATILE_UNSUITABLE=468, setup_compat:regime_BREAKOUT_EXPANSION=116
- **FAILED_AUCTION_RECLAIM** (total=1364): setup_compat:regime_STRONG_TREND=680, execution:overextended=526, context_floor=158
- **FUNDING_EXTREME_SIGNAL** (total=786): execution:trigger_not_confirmed=782, context_floor=4
- **LIQUIDATION_REVERSAL** (total=22): execution:trigger_not_confirmed=22
- **LIQUIDITY_SWEEP_REVERSAL** (total=3958): execution:trigger_not_confirmed=1548, setup_compat:regime_STRONG_TREND=1469, execution:overextended=941
- **MA_CROSS_TREND_SHIFT** (total=17): setup_compat:regime_CLEAN_RANGE=6, setup_compat:regime_DIRTY_RANGE=4, execution:overextended=4, execution:trigger_not_confirmed=3
- **MEAN_REVERT** (total=6920): setup_compat:regime_STRONG_TREND=3740, setup_compat:regime_WEAK_TREND=2385, execution:overextended=795
- **MOVER_AVWAP_SCALP** (total=1777): execution:overextended=1402, execution:trigger_not_confirmed=262, entry_quality=113
- **MOVER_TREND_PULLBACK** (total=10642): execution:trigger_not_confirmed=5782, execution:overextended=4216, entry_quality=644
- **QUIET_COMPRESSION_BREAK** (total=30): execution:trigger_not_confirmed=30
- **RANGE_FADE** (total=2970): setup_compat:regime_WEAK_TREND=1358, setup_compat:regime_STRONG_TREND=1223, execution:overextended=289, setup_compat:regime_VOLATILE_UNSUITABLE=98, setup_compat:regime_BREAKOUT_EXPANSION=2
- **TREND_PULLBACK_EMA** (total=1792): setup_compat:regime_CLEAN_RANGE=1096, setup_compat:regime_DIRTY_RANGE=548, setup_compat:regime_VOLATILE_UNSUITABLE=127, entry_quality=21
- **VOLUME_SURGE_BREAKOUT** (total=20): execution:overextended=20
- **WHALE_MOMENTUM** (total=950): execution:trigger_not_confirmed=928, context_floor=22

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 112030 | 32.7% |
| QUIET | 95633 | 27.9% |
| TRENDING_UP | 74444 | 21.8% |
| TRENDING_DOWN | 49302 | 14.4% |
| VOLATILE | 10826 | 3.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **108**
- Average confidence gap to threshold: **10.71** (samples=108) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: CAPUSDT=27, DOTUSDT=18, ZECUSDT=15, HYPEUSDT=14, ETHUSDT=7, XMRUSDT=6, AVAXUSDT=6, ADAUSDT=4, C98USDT=3, ENAUSDT=2

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 15 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 23 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 39 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 10 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 3 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 1 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 101 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 10 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 75 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 95 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 19 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 12 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 7 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 131 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 432 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 14 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1253 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 62 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 3 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 30 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 1 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 28 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 8 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 2 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 52 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 9 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 4 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 15 | 41.00 | 64.47 | 23.47 | 21.36 | 19.30 | 17.00 | 0.00 | 26.00 |
| DIVERGENCE_CONTINUATION | kept | 23 | 69.30 | 65.00 | -4.30 | 19.96 | 19.85 | 17.83 | 0.13 | 1.61 |
| FAILED_AUCTION_RECLAIM | filtered | 49 | 54.78 | 62.73 | 7.95 | 20.76 | 19.42 | 20.00 | 3.00 | 4.16 |
| FAILED_AUCTION_RECLAIM | kept | 3 | 72.57 | 65.00 | -7.57 | 21.10 | 19.07 | 20.00 | 2.00 | 4.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 46.30 | 61.00 | 14.70 | 21.20 | 14.00 | 17.00 | 3.00 | 5.00 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 71.00 | 65.00 | -6.00 | 20.80 | 20.00 | 20.00 | 0.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 111 | 51.31 | 64.47 | 13.16 | 19.01 | 17.54 | 17.55 | 2.17 | 14.33 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 75 | 69.03 | 65.00 | -4.03 | 21.12 | 19.31 | 17.63 | 1.47 | 0.23 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 70.00 | 65.00 | -5.00 | 21.10 | 17.50 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 96 | 54.33 | 65.00 | 10.67 | 19.87 | 17.02 | 15.70 | 0.00 | 14.51 |
| MEAN_REVERT | kept | 19 | 67.23 | 65.00 | -2.23 | 19.89 | 18.53 | 15.35 | 0.00 | 0.26 |
| MOVER_AVWAP_SCALP | filtered | 19 | 48.78 | 65.00 | 16.22 | 20.39 | 14.18 | 15.80 | 4.29 | 18.58 |
| MOVER_AVWAP_SCALP | kept | 131 | 78.69 | 65.00 | -13.69 | 19.87 | 15.06 | 15.80 | 4.11 | 4.40 |
| MOVER_TREND_PULLBACK | filtered | 446 | 56.91 | 64.01 | 7.10 | 20.25 | 18.81 | 15.80 | 3.99 | 18.96 |
| MOVER_TREND_PULLBACK | kept | 1253 | 77.04 | 65.00 | -12.04 | 19.98 | 18.42 | 15.80 | 4.15 | 1.12 |
| QUIET_COMPRESSION_BREAK | filtered | 65 | 57.50 | 64.82 | 7.32 | 22.13 | 19.84 | 20.00 | 0.00 | 10.18 |
| QUIET_COMPRESSION_BREAK | kept | 30 | 72.75 | 65.00 | -7.75 | 21.02 | 19.39 | 20.00 | 0.00 | 1.34 |
| SR_FLIP_RETEST | filtered | 1 | 58.90 | 65.00 | 6.10 | 18.50 | 20.00 | 15.20 | 1.00 | 11.80 |
| SR_FLIP_RETEST | kept | 28 | 72.67 | 65.00 | -7.67 | 19.98 | 20.00 | 17.45 | 1.32 | -0.20 |
| TREND_PULLBACK_EMA | filtered | 10 | 56.10 | 65.00 | 8.90 | 20.82 | 19.60 | 19.12 | 3.30 | 17.00 |
| TREND_PULLBACK_EMA | kept | 52 | 75.93 | 65.00 | -10.93 | 19.75 | 19.83 | 17.18 | 5.40 | 4.13 |
| VOLUME_SURGE_BREAKOUT | filtered | 9 | 38.70 | 62.33 | 23.63 | 20.38 | 18.90 | 20.00 | 3.00 | 12.60 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 69.80 | 65.00 | -4.80 | 20.20 | 16.65 | 20.00 | 5.38 | 6.50 |
| WHALE_MOMENTUM | filtered | 1 | 61.70 | 65.00 | 3.30 | 22.20 | 14.00 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 15 | 41.00 | 17.00 | 18.00 | 3.00 | 17.00 | 5.00 | 7.00 | 0.00 |
| DIVERGENCE_CONTINUATION | kept | 23 | 69.30 | 22.91 | 14.52 | 6.52 | 13.52 | 5.00 | 9.07 | 0.13 |
| FAILED_AUCTION_RECLAIM | filtered | 49 | 54.78 | 19.94 | 16.04 | 6.61 | 12.18 | 7.36 | 3.91 | 3.00 |
| FAILED_AUCTION_RECLAIM | kept | 3 | 72.57 | 22.33 | 15.33 | 8.00 | 14.00 | 7.33 | 7.57 | 2.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 46.30 | 25.00 | 8.00 | 3.00 | 9.00 | 10.00 | 8.30 | 3.00 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 71.00 | 17.00 | 18.00 | 3.00 | 14.00 | 9.00 | 10.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 111 | 51.31 | 23.20 | 14.07 | 6.35 | 12.52 | 5.99 | 7.55 | 2.17 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 75 | 69.03 | 23.91 | 15.44 | 4.00 | 11.85 | 5.23 | 7.36 | 1.47 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 70.00 | 17.00 | 14.00 | 3.00 | 17.00 | 9.00 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 96 | 54.33 | 20.50 | 16.21 | 10.91 | 12.82 | 5.00 | 6.99 | 0.00 |
| MEAN_REVERT | kept | 19 | 67.23 | 17.84 | 14.32 | 11.68 | 13.00 | 5.00 | 5.81 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 19 | 48.78 | 16.26 | 18.11 | 10.50 | 11.68 | 6.63 | 6.99 | 4.29 |
| MOVER_AVWAP_SCALP | kept | 131 | 78.69 | 19.70 | 18.02 | 12.31 | 13.83 | 7.24 | 8.14 | 4.11 |
| MOVER_TREND_PULLBACK | filtered | 446 | 56.91 | 17.96 | 18.04 | 7.55 | 12.87 | 6.53 | 9.31 | 3.99 |
| MOVER_TREND_PULLBACK | kept | 1253 | 77.04 | 18.89 | 18.00 | 8.08 | 13.19 | 6.57 | 9.31 | 4.15 |
| QUIET_COMPRESSION_BREAK | filtered | 65 | 57.50 | 17.86 | 17.82 | 10.71 | 14.42 | 6.98 | 4.51 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 30 | 72.75 | 18.33 | 17.60 | 12.00 | 14.00 | 7.08 | 6.21 | 0.00 |
| SR_FLIP_RETEST | filtered | 1 | 58.90 | 17.00 | 8.00 | 12.00 | 14.00 | 10.00 | 8.70 | 1.00 |
| SR_FLIP_RETEST | kept | 28 | 72.67 | 18.14 | 17.64 | 7.39 | 14.11 | 5.18 | 9.01 | 1.32 |
| TREND_PULLBACK_EMA | filtered | 10 | 56.10 | 14.00 | 18.00 | 7.50 | 14.60 | 5.70 | 10.00 | 3.30 |
| TREND_PULLBACK_EMA | kept | 52 | 75.93 | 20.73 | 18.00 | 7.62 | 14.40 | 5.73 | 9.05 | 5.40 |
| VOLUME_SURGE_BREAKOUT | filtered | 9 | 38.70 | 17.00 | 14.00 | 12.00 | 11.00 | 5.00 | 4.30 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 69.80 | 19.25 | 16.00 | 12.75 | 12.50 | 5.00 | 9.18 | 5.38 |
| WHALE_MOMENTUM | filtered | 1 | 61.70 | 25.00 | 8.00 | 15.00 | 17.00 | 5.00 | 1.70 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 15 | 41.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 23 | 69.30 | 0.00 | 0.00 | 0.00 | 0.00 | 1.57 | 0.00 | 0.00 | 0.00 | **1.57** |
| FAILED_AUCTION_RECLAIM | filtered | 49 | 54.78 | 0.00 | 0.00 | 0.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.29** |
| FAILED_AUCTION_RECLAIM | kept | 3 | 72.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 46.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 71.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 111 | 51.31 | 0.00 | 0.00 | 2.68 | 0.00 | 2.38 | 0.00 | 0.00 | 0.00 | **5.06** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 75 | 69.03 | 0.00 | 0.00 | 0.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.06** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 70.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 96 | 54.33 | 0.00 | 0.00 | 0.00 | 0.00 | 4.60 | 0.00 | 0.00 | 0.00 | **4.60** |
| MEAN_REVERT | kept | 19 | 67.23 | 0.00 | 0.00 | 0.42 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.42** |
| MOVER_AVWAP_SCALP | filtered | 19 | 48.78 | 0.00 | 0.00 | 1.18 | 0.00 | 8.91 | 0.00 | 0.00 | 0.00 | **10.09** |
| MOVER_AVWAP_SCALP | kept | 131 | 78.69 | 0.23 | 0.00 | 0.12 | 0.00 | 3.53 | 0.00 | 0.00 | 0.27 | **4.15** |
| MOVER_TREND_PULLBACK | filtered | 446 | 56.91 | 0.00 | 0.00 | 0.01 | 0.00 | 0.30 | 0.03 | 0.00 | 0.00 | **0.34** |
| MOVER_TREND_PULLBACK | kept | 1253 | 77.04 | 0.01 | 0.00 | 0.24 | 0.00 | 0.05 | 0.02 | 0.00 | 0.00 | **0.32** |
| QUIET_COMPRESSION_BREAK | filtered | 65 | 57.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.92 | **6.92** |
| QUIET_COMPRESSION_BREAK | kept | 30 | 72.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.20 | **0.20** |
| SR_FLIP_RETEST | filtered | 1 | 58.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 28 | 72.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 10 | 56.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 52 | 75.93 | 0.00 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.15** |
| VOLUME_SURGE_BREAKOUT | filtered | 9 | 38.70 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 69.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 1 | 61.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **139112 held of 470643 seen** across 21 strategies; 3171 cells past the sample floor; **1569 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 42936 | 647/42289/0 | 43% | -0.19 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.22R) |
| MOVER_AVWAP_SCALP | 18051 | 193/17858/0 | 41% | -0.24 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 10838 | 121/10717/0 | 37% | -0.30 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 9558 | 66/9492/0 | 51% | +0.00 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.39R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING (-1.19R) |
| TREND_PULLBACK_EMA | 7964 | 36/7928/0 | 44% | -0.16 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OVERLAP/QUIET/COMPRESSED/BTC_FALLING (-1.29R) |
| SHADOW_MEAN_REVERT | 6870 | 0/0/6870 | 43% | -0.10 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.95R) |
| LIQUIDITY_SWEEP_REVERSAL | 6717 | 87/6630/0 | 35% | -0.50 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | LONDON/MARKUP/EXPANDED/BTC_NEUTRAL (-1.59R) |
| SHADOW_RANGE_FADE | 6149 | 0/0/6149 | 37% | -0.08 | ASIA/MARKDOWN/EXPANDED/BTC_FALLING (+0.53R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-1.38R) |
| QUIET_COMPRESSION_BREAK | 5840 | 342/5498/0 | 52% | -0.09 | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (+0.57R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5454 | 0/0/5454 | 35% | -0.40 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.02R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3785 | 4/3781/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 3451 | 41/3410/0 | 43% | -0.20 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| SR_FLIP_RETEST | 2744 | 15/2729/0 | 48% | -0.23 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.86R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| FUNDING_EXTREME_SIGNAL | 2705 | 2/2703/0 | 31% | -0.48 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 2633 | 0/2633/0 | 35% | -0.23 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| RANGE_FADE | 1251 | 4/1247/0 | 43% | -0.27 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1179 | 0/0/1179 | 54% | -0.03 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.08R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.36R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 316 | 0/316/0 | 36% | -0.47 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 92 | 12/80/0 | 43% | -0.12 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 12 | 0/12/0 | 50% | -0.00 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ LONDON/MARKUP/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.59R (n=44, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ LONDON/MARKUP/EXPANDED/BTC_NEUTRAL` -1.59R (n=44, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 192 | 27% / -0.58R | 192 | 52% / -0.15R | +0.43 | **ATR** |
| LIQUIDATION_REVERSAL | 17 | 35% / -0.40R | 17 | 59% / -0.18R | +0.22 | **ATR** |
| TREND_PULLBACK_EMA | 658 | 42% / -0.25R | 658 | 55% / -0.04R | +0.20 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1128 | 45% / -0.32R | 1128 | 55% / -0.14R | +0.18 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 132 | 35% / -0.22R | 132 | 45% / -0.09R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 1539 | 43% / -0.19R | 1539 | 49% / -0.07R | +0.13 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1059 | 40% / -0.25R | 1059 | 43% / -0.14R | +0.11 | **ATR** |
| RANGE_FADE | 59 | 34% / -0.36R | 59 | 41% / -0.26R | +0.11 | **ATR** |
| MOVER_TREND_PULLBACK | 6833 | 49% / -0.12R | 6833 | 54% / -0.02R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 434 | 44% / -0.32R | 434 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 245 | 47% / -0.24R | 245 | 50% / -0.16R | +0.08 | **ATR** |
| MA_CROSS_TREND_SHIFT | 28 | 43% / -0.20R | 28 | 43% / -0.12R | +0.07 | **ATR** |
| DIVERGENCE_CONTINUATION | 965 | 48% / -0.11R | 965 | 54% / -0.05R | +0.06 | **ATR** |
| QUIET_COMPRESSION_BREAK | 963 | 46% / -0.15R | 963 | 46% / -0.16R | -0.00 | **FIXED** |
| MEAN_REVERT | 244 | 52% / -0.06R | 244 | 51% / -0.07R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 43% / -0.33R | 7 | 43% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 9725 | 29% | -0.24R | 310 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1539 | 47% | -0.07R | 213 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 83 | 47% | -0.10R | 52 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 880 | 37% / -0.17R | +0.90 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1167 | 40% / -0.16R | +0.85 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 1997 | 34% / -0.12R | +0.72 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 8760 | 36% / -0.14R | +0.39 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1091 | 38% / -0.06R | +0.22 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 159 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 930 | 34% / -0.18R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 862 | 33% / -0.21R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 196 | 29% / -0.44R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 256 | 32% / -0.60R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 203 | 54% / +0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 45 | 36% / -0.06R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 244 | 32% / -0.40R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 44 | 25% / -0.47R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 23 | 48% / +0.00R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 13 | 38% / +0.45R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×319]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 768/6) (sustained 768 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.62R (bound 0.3) (streak 1511/6) (sustained 1511 cycles)
- **ALERT** `tuned_variants` — 887 non-stamps — atr_arm_uncomputable=887 (seen=20222 stamped=2291 skipped=17044) (streak 1506/6) (sustained 1506 cycles)
- **ALERT** `auto_dispatch` — 242 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=242) (streak 1500/3) (sustained 1500 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 57 fed / 0 quiet / 2 never delivered of 59 subscribed; 758071708 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 23 arms current, none stalled; covering 1440/1440 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 46 arms current, none stalled; covering 1276/1276 signals (100%) | 0 |
| auto_dispatch | violating | 242 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=242) (streak 1500/3) | 1500 |
| binance_ip_weight | ok | peak 341/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 83740.10 | 0 |
| candle_coverage | ok | 96/96 symbols with ≥20 15m candles, 96/96 updated within 45m [fresh=96; 87 Tier-1 futures + 9 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 243 dup bars, 0 undedupable; ws 0 out-of-order, 1336 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 54 cohorts, 17 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +37 / upstream +10 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 2268/2286 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 1 of 104 open dark rows are not being advanced (worst: JUPUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 7/120) | 7 |
| dark_sar_arms | ok | no open arms; covering 2263/2281 signals (99%) | 0 |
| depth_feed | ok | 57/59 books fresh (stale 0, never 2, thin 0); 367189437 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.62R (bound 0.3) (streak 1511/6) | 1511 |
| emission_controller | ok | last cycle 765s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×319]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 768/6) | 768 |
| entry_quality_effective | ok | 30929 evaluated, 9656 suppressed, 13308 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,364 reads/day of 50,000 [engine 1,325, signing 39]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 6840 sealed bars over 57 symbols; 2460 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +10 / upstream +104 | 0 |
| indicator_cache_key | ok | 657377 frozen value(s) avoided; 3264156 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.21R over n=3410 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +8 / upstream +104 | 0 |
| mover_admission_metadata | ok | 924 symbols known, 217 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 9 held, 9 with scan counts, 9 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 2607604 evicted (sampled: execution:trigger_not_confirmed 400/946521, execution:overextended 400/832293, setup_compat:regime_STRONG_TREND 400/416209) | 0 |
| price_action_lane | ok | 3622028 evaluated, 3893 emitted; layer1 3893 stamped / 0 blind; cooldown=481596, delta_opposed=287719, no_footprint=1355565, no_opposing_target=1749, no_sweep=1224433, rr_below_floor=267073 | 0 |
| promoted_pair_integrity | ok | 9/9 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.27R over n=1247 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +29 / upstream +104 | 0 |
| sar_alignment_crosscheck | ok | 2089/58496 disagreed (3.6%) | 0 |
| sar_exit_shadow | ok | output +8 / upstream +104 | 0 |
| sar_hold_arm | ok | 1857 held arms settled, 143 unscored, 46 still walking (43 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 4/39 unfetchable (10%); top cause: located bar does not contain the stamp; symbols: QNTUSDT, RLCUSDT, SANDUSDT, 龙虾USDT | 0 |
| sar_live_arms | ok | 46 arms current, none stalled; covering 1275/1275 signals (100%) | 0 |
| sar_refresh_budget | ok | 1 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 439 records await one (35 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 40.14s, worst 192.9s over 43032 lifetime cycles; lifetime 529 over 60s, 49 over 120s; recent 4/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.03s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 1692602 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 5s ago (58.72s to run, worst 179.91s), 3121 overrun(s) of 30553 cycles, TTL 900s; slowest router_delivery=13.62s, dark_promotion=10.38s, position_marks=4.71s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=8, gate reads=0, withheld=8) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +78 / upstream +104 | 0 |
| structural_snap | ok | 6000/6000 measured, 19 blind, 0 levels moved (refusals: redetect_cooldown=2318) | 0 |
| structural_veto_lane | ok | 4451 stamped; 0 with no readable level book, 151 with clear air ahead, 3469 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +104 / upstream +10 | 0 |
| tuned_variants | violating | 887 non-stamps — atr_arm_uncomputable=887 (seen=20222 stamped=2291 skipped=17044) (streak 1506/6) | 1506 |
| unlock_shorts | ok | 14 open, 42 scheduled, calendar 7.1h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 174 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1620607`
- `Path funnel` emissions: `43`
- `Regime distribution` emissions: `43`
- `QUIET_SCALP_BLOCK` events: `108`
- `confidence_gate` events: `2443`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **6**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 2 | 24162 | 24162 | 30414 | 0 |
| futures_aggtrade | 2 | 26854 | 26854 | 56314 | 0 |
| futures_liq | 2 | 2831 | 2831 | 6043 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=292945] state[populated=292945] buckets[many=292945] sources[none] quality[none]
- funding_rate: presence[absent=13303, present=279642] state[empty=13303, populated=279642] buckets[few=279642, none=13303] sources[none] quality[none]
- liquidation_clusters: presence[absent=172893, present=120052] state[empty=172893, populated=120052] buckets[few=92464, none=172893, some=27588] sources[none] quality[none]
- oi_snapshot: presence[absent=13303, present=279642] state[empty=13303, populated=279642] buckets[few=117, many=278883, none=13303, some=642] sources[none] quality[none]
- order_book: presence[absent=91762, present=201183] state[populated=201183, unavailable=91762] buckets[few=201183, none=91762] sources[book_ticker=201183, unavailable=91762] quality[none=91762, top_of_book_only=201183]
- orderblocks: presence[absent=292945] state[empty=292945] buckets[none=292945] sources[measured_dark=292945] quality[none]
- recent_ticks: presence[present=292945] state[populated=292945] buckets[many=292945] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.539018630981445` sec
- Median create→first breach: `7931.814766049385` sec
- Median create→terminal: `7931.814838528633` sec
- Median first breach→terminal: `7.152557373046875e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 1.447284244192681 | 1.6900373522748118 | 0.8563622823156056 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 2.0070075918394417 | 2.0070096864909837 | 0.9999989563321213 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 1.184690416033337 | 1.266401565211518 | 0.955325033273211 | 0 | 1 |
| MEAN_REVERT | 1 | 1 | 1.784043832687425 | 1.749787569691303 | 1.019577383900473 | 1 | 0 |
| MOVER_AVWAP_SCALP | 1 | 1 | 2.243997023609714 | 2.6036344927536255 | 0.8618709845238085 | 0 | 1 |
| MOVER_TREND_PULLBACK | 23 | 23 | 2.8260466266773796 | 2.9778000000000016 | 1.0600761686967382 | 12 | 11 |
| QUIET_COMPRESSION_BREAK | 11 | 11 | 0.7999999999999945 | 0.8687249977175148 | 0.8866366129693192 | 0 | 10 |
| SR_FLIP_RETEST | 1 | 1 | 0.7288135593220517 | 0.5442005171578964 | 1.339237167815096 | 1 | 0 |
| TREND_PULLBACK_EMA | 1 | 1 | 1.5601965013179886 | 1.755273537986621 | 0.8888623155041723 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.69 | 5254.006057977676 | 5254.006078958511 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.007 | 1333.3041877746582 | 1333.3042068481445 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | -0.24 | 10543.461855530739 | 10545.132634997368 |
| MEAN_REVERT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.63 | 2175.627205133438 | 2184.813899040222 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 24800.511549949646 | 24800.51162290573 |
| MOVER_TREND_PULLBACK | 23 | 23 | 34.8 | 30.4 | 34.8 | 0.0 | 0.2632 | 4493.6452260017395 | 4493.645286083221 |
| QUIET_COMPRESSION_BREAK | 11 | 11 | 18.2 | 81.8 | 18.2 | 0.0 | -0.7043 | 14852.568180084229 | 14853.92881321907 |
| SR_FLIP_RETEST | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.7288 | 27973.524395942688 | 27973.52441716194 |
| TREND_PULLBACK_EMA | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 2.3403 | 1413.0446619987488 | 1413.5966339111328 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 751 | 7 | 661 | 0.0 | 100.0 | 27973.524395942688 | 27973.52441716194 | 90 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2202 | 24 | 2072 | 100.0 | 0.0 | 1413.0446619987488 | 1413.5966339111328 | 130 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-42`
- Gating Δ: `-14998`
- No-generation Δ: `-470995`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.0094, "current_avg_pnl": 0.0, "current_win_rate": 0.0, "previous_avg_pnl": -0.0094, "previous_win_rate": 16.7, "win_rate_delta": -16.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.751, "current_avg_pnl": 0.2632, "current_win_rate": 34.8, "previous_avg_pnl": -0.4878, "previous_win_rate": 26.7, "win_rate_delta": 8.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.1377, "current_avg_pnl": -0.7043, "current_win_rate": 18.2, "previous_avg_pnl": -0.5666, "previous_win_rate": 25.0, "win_rate_delta": -6.8}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": -545, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 27973.52, "median_terminal_delta_sec": 27973.52, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 14, "geometry_changed_delta": 0, "geometry_preserved_delta": 72, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 1413.04, "median_terminal_delta_sec": 1413.6, "sl_rate_delta": 0.0, "win_rate_delta": 100.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
