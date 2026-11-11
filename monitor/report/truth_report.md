# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: DIVERGENCE_CONTINUATION, MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: none
- Recommended next investigation target: **DIVERGENCE_CONTINUATION**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `1979` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 150 | 150 | 150 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 13839 | 13839 | 12188 | 31 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 71855 | 71831 | 66 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 74626 | 74627 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 74104 | 70976 | 3632 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 74680 | 73473 | 1327 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 74009 | 73976 | 71 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 64644 | 64666 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 74807 | 74860 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 74874 | 72676 | 3047 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 74986 | 81071 | 522 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 71905 | 67591 | 7341 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 73640 | 73641 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 74637 | 74671 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 74059 | 73940 | 160 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 75730 | 74350 | 1932 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 73650 | 73731 | 270 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 64116 | 60450 | 4067 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 64530 | 64216 | 416 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 71814 | 71825 | 30 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 64670 | 64706 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3878 | 3878 | 3089 | 7 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 362 | 362 | 196 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 4 | 4 | 0 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 18495 | 18495 | 18182 | 6 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 9 | 9 | 7 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7233 | 7233 | 5082 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1318 | 1318 | 322 | 47 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 18625 | 18625 | 7298 | 269 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 572 | 572 | 236 | 43 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4844 | 4844 | 3693 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 813 | 813 | 310 | 9 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2022 | 2022 | 1568 | 44 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 96 | 96 | 26 | 4 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=71831): breakout_not_found=39758, basic_filters_failed=20030, move_not_fresh=7993, breakout_stale=2752, retest_proximity_failed=976, volume_spike_missing=289, move_exhausted=26, missing_fvg_or_orderblock=7
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=74627): cls_disabled_merged_into_lsr=74627
- **EVAL::DIVERGENCE_CONTINUATION** (total=70976): cvd_divergence_failed=28913, basic_filters_failed=18513, h1_trend_not_aligned=16008, ema_alignment_reject=6512, retest_proximity_failed=771, missing_fvg_or_orderblock=259
- **EVAL::FAILED_AUCTION_RECLAIM** (total=73473): auction_not_detected=46949, basic_filters_failed=17813, reclaim_hold_failed=4051, tail_too_small=2735, regime_blocked=1923, rsi_reject=2
- **EVAL::FUNDING_EXTREME** (total=73976): funding_not_extreme=54340, basic_filters_failed=18455, ema_alignment_reject=559, rsi_reject=283, missing_funding_rate=214, cvd_divergence_failed=66, momentum_reject=45, missing_fvg_or_orderblock=14
- **EVAL::LIQUIDATION_REVERSAL** (total=64666): cascade_threshold_not_met=45900, basic_filters_failed=18256, cvd_divergence_failed=255, rsi_reject=244, missing_fvg_or_orderblock=10, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=74860): no_ma_cross=55178, basic_filters_failed=18541, ma_cross_cooldown=837, ma_cross_htf_misaligned=304
- **EVAL::MEAN_REVERT** (total=72676): no_extension=62597, basic_filters_failed=10079
- **EVAL::MOVER_AVWAP_SCALP** (total=81071): no_avwap_tag=27180, no_mover_leg=23149, basic_filters_failed=20258, avwap_slope_against=6713, avwap_reclaim_no_volume=2072, no_avwap_reclaim=1465, anchor_too_recent=234
- **EVAL::MOVER_TREND_PULLBACK** (total=67591): mover_run_too_small=35907, basic_filters_failed=20156, no_reclaim=10006, no_pullback_tag=1522
- **EVAL::OPENING_RANGE_BREAKOUT** (total=73641): feature_disabled=73641
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=74671): regime_blocked=54667, breakout_not_found=14604, basic_filters_failed=3130, adx_reject=2206, ema_alignment_reject=64
- **EVAL::QUIET_COMPRESSION_BREAK** (total=73940): compression_not_detected=30419, regime_blocked=21776, basic_filters_failed=14666, breakout_not_detected=6477, volume_confirmation_failed=597, macd_reject=3, rsi_reject=2
- **EVAL::RANGE_FADE** (total=74350): no_range_edge=64264, basic_filters_failed=10086
- **EVAL::SR_FLIP_RETEST** (total=73731): flip_close_not_confirmed=46883, basic_filters_failed=17786, retest_out_of_zone=2623, regime_blocked=1910, long_break_volume_thin=1850, h1_break_not_confirmed=1177, reclaim_hold_failed=1042, ema_alignment_reject=219, wick_quality_failed=130, whipsaw_flip=64, long_acceptance_not_held=26, missing_fvg_or_orderblock=21
- **EVAL::STANDARD** (total=60450): adx_reject=21147, momentum_reject=16479, basic_filters_failed=6706, sweeps_not_detected=5854, macd_reject=5687, ema_alignment_reject=3507, htf_poi_unanchored=910, invalid_sl_geometry=82, rsi_reject=50, mtf_reject=28
- **EVAL::TREND_PULLBACK** (total=64216): h1_trend_not_aligned=19852, ema_alignment_reject=11200, basic_filters_failed=9857, h1_pullback_not_confirmed=8643, ema_not_tested_prev=4550, no_ema_reclaim_close=4356, body_conviction_fail=2353, rsi_reject=1772, prev_already_below_emas=637, no_prev_low_break=431, prev_already_above_emas=248, momentum_flat=139, no_prev_high_break=131, ema21_not_tagged=21, missing_fvg_or_orderblock=14, momentum_reject=12
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=71825): breakout_not_found=41341, basic_filters_failed=20030, move_not_fresh=6174, breakout_stale=3449, retest_proximity_failed=676, volume_spike_missing=148, missing_fvg_or_orderblock=6, move_exhausted=1
- **EVAL::WHALE_MOMENTUM** (total=64706): momentum_reject=41581, recent_ticks_insufficient=17486, basic_filters_failed=5639

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=51): execution:overextended=51
- **DIVERGENCE_CONTINUATION** (total=226): setup_compat:regime_VOLATILE_UNSUITABLE=195, execution:overextended=28, setup_compat:regime_BREAKOUT_EXPANSION=3
- **FAILED_AUCTION_RECLAIM** (total=1302): execution:overextended=629, setup_compat:regime_STRONG_TREND=380, context_floor=293
- **FUNDING_EXTREME_SIGNAL** (total=323): execution:trigger_not_confirmed=320, context_floor=3
- **LIQUIDATION_REVERSAL** (total=4): execution:trigger_not_confirmed=4
- **LIQUIDITY_SWEEP_REVERSAL** (total=4753): execution:trigger_not_confirmed=1948, execution:overextended=1524, setup_compat:regime_STRONG_TREND=1281
- **MA_CROSS_TREND_SHIFT** (total=8): execution:trigger_not_confirmed=3, execution:overextended=2, setup_compat:regime_CLEAN_RANGE=2, setup_compat:regime_DIRTY_RANGE=1
- **MEAN_REVERT** (total=3523): setup_compat:regime_WEAK_TREND=1631, setup_compat:regime_STRONG_TREND=1292, execution:overextended=545, entry_quality=55
- **MOVER_AVWAP_SCALP** (total=937): execution:overextended=758, entry_quality=95, execution:trigger_not_confirmed=84
- **MOVER_TREND_PULLBACK** (total=7853): execution:trigger_not_confirmed=4416, execution:overextended=2111, entry_quality=1326
- **QUIET_COMPRESSION_BREAK** (total=8): execution:trigger_not_confirmed=7, execution:overextended=1
- **RANGE_FADE** (total=2934): setup_compat:regime_WEAK_TREND=1376, setup_compat:regime_STRONG_TREND=1055, setup_compat:regime_VOLATILE_UNSUITABLE=224, execution:overextended=198, context_edge=49, setup_compat:regime_BREAKOUT_EXPANSION=32
- **TREND_PULLBACK_EMA** (total=1773): setup_compat:regime_CLEAN_RANGE=1290, setup_compat:regime_DIRTY_RANGE=357, entry_quality=124, setup_compat:regime_VOLATILE_UNSUITABLE=2
- **VOLUME_SURGE_BREAKOUT** (total=19): execution:overextended=19

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 195432 | 47.7% |
| QUIET | 92979 | 22.7% |
| TRENDING_DOWN | 60535 | 14.8% |
| TRENDING_UP | 45552 | 11.1% |
| VOLATILE | 15012 | 3.7% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **204**
- Average confidence gap to threshold: **15.75** (samples=204) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: AAVEUSDT=65, PROMUSDT=22, XMRUSDT=20, LINKUSDT=10, ETHUSDT=9, XRPUSDT=8, FILUSDT=7, ASTERUSDT=7, BCHUSDT=6, ADAUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 110 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 260 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 79 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 38 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 7 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 17 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 62 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 115 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 9 |
| MEAN_REVERT | kept | min_confidence_pass | 33 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 265 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 5 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 319 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2718 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 66 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2908 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 80 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 68 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 177 |
| SR_FLIP_RETEST | filtered | min_confidence | 137 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 11 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 53 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 56 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 14 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 172 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 55 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 4 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 110 | 57.74 | 64.85 | 7.11 | 20.23 | 19.58 | 17.42 | 1.63 | 10.20 |
| DIVERGENCE_CONTINUATION | kept | 260 | 68.63 | 65.00 | -3.63 | 19.63 | 19.85 | 18.66 | 1.15 | 0.50 |
| FAILED_AUCTION_RECLAIM | filtered | 117 | 38.46 | 62.21 | 23.75 | 20.31 | 18.37 | 20.00 | 1.75 | 17.49 |
| FAILED_AUCTION_RECLAIM | kept | 7 | 69.01 | 65.00 | -4.01 | 21.23 | 18.31 | 20.00 | 2.86 | 2.11 |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 47.96 | 60.24 | 12.28 | 19.00 | 14.00 | 15.53 | 6.12 | 19.76 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 64 | 55.48 | 64.94 | 9.46 | 21.65 | 19.29 | 18.06 | 1.67 | 13.98 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 115 | 69.89 | 65.00 | -4.89 | 23.04 | 19.07 | 18.33 | 1.87 | 2.28 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 79.30 | 65.00 | -14.30 | 20.60 | 20.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 9 | 61.70 | 65.00 | 3.30 | 18.73 | 14.00 | 17.60 | 0.00 | 9.00 |
| MEAN_REVERT | kept | 33 | 80.95 | 65.00 | -15.95 | 19.92 | 14.12 | 19.80 | 0.00 | 1.55 |
| MOVER_AVWAP_SCALP | filtered | 270 | 52.63 | 63.75 | 11.12 | 20.04 | 15.55 | 15.80 | 4.13 | 21.58 |
| MOVER_AVWAP_SCALP | kept | 319 | 80.23 | 65.00 | -15.23 | 20.41 | 15.87 | 15.80 | 4.24 | 3.99 |
| MOVER_TREND_PULLBACK | filtered | 2784 | 54.84 | 63.61 | 8.77 | 20.64 | 18.50 | 15.80 | 4.10 | 20.37 |
| MOVER_TREND_PULLBACK | kept | 2908 | 77.26 | 65.00 | -12.26 | 20.80 | 18.48 | 15.80 | 4.45 | 1.65 |
| QUIET_COMPRESSION_BREAK | filtered | 148 | 51.15 | 64.76 | 13.61 | 22.03 | 18.96 | 20.00 | 0.00 | 11.81 |
| QUIET_COMPRESSION_BREAK | kept | 177 | 73.42 | 65.00 | -8.42 | 20.37 | 19.23 | 20.00 | 0.00 | -1.55 |
| SR_FLIP_RETEST | filtered | 148 | 54.63 | 64.68 | 10.05 | 20.22 | 20.00 | 16.78 | 1.92 | 15.07 |
| SR_FLIP_RETEST | kept | 53 | 75.55 | 65.00 | -10.55 | 21.60 | 20.00 | 15.45 | 2.79 | 3.21 |
| TREND_PULLBACK_EMA | filtered | 70 | 60.20 | 65.00 | 4.80 | 20.56 | 19.76 | 18.86 | 5.06 | 18.77 |
| TREND_PULLBACK_EMA | kept | 172 | 79.05 | 65.00 | -14.05 | 20.56 | 19.44 | 18.22 | 4.93 | 1.13 |
| VOLUME_SURGE_BREAKOUT | filtered | 55 | 51.75 | 63.20 | 11.45 | 20.97 | 17.50 | 20.00 | 3.76 | 5.32 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 71.38 | 65.00 | -6.38 | 19.85 | 17.90 | 19.93 | 4.25 | 7.45 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 110 | 57.74 | 22.96 | 12.82 | 3.65 | 12.31 | 5.31 | 9.26 | 1.63 |
| DIVERGENCE_CONTINUATION | kept | 260 | 68.63 | 19.83 | 17.27 | 3.66 | 13.63 | 5.55 | 9.34 | 1.15 |
| FAILED_AUCTION_RECLAIM | filtered | 117 | 38.46 | 19.15 | 15.47 | 8.05 | 14.36 | 5.94 | 4.32 | 1.75 |
| FAILED_AUCTION_RECLAIM | kept | 7 | 69.01 | 21.57 | 15.14 | 6.43 | 13.00 | 5.50 | 6.63 | 2.86 |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 47.96 | 19.35 | 16.24 | 3.00 | 10.24 | 5.94 | 6.84 | 6.12 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 64 | 55.48 | 21.97 | 15.31 | 6.23 | 12.72 | 5.03 | 7.46 | 1.67 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 115 | 69.89 | 24.15 | 15.22 | 5.27 | 11.12 | 5.68 | 8.87 | 1.87 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 79.30 | 25.00 | 14.00 | 9.00 | 17.00 | 5.00 | 9.30 | 0.00 |
| MEAN_REVERT | filtered | 9 | 61.70 | 17.00 | 18.00 | 12.00 | 13.00 | 5.00 | 5.70 | 0.00 |
| MEAN_REVERT | kept | 33 | 80.95 | 24.76 | 17.39 | 14.91 | 13.00 | 5.00 | 7.45 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 270 | 52.63 | 17.41 | 18.00 | 12.35 | 13.50 | 6.41 | 6.86 | 4.13 |
| MOVER_AVWAP_SCALP | kept | 319 | 80.23 | 20.88 | 18.01 | 12.44 | 13.83 | 6.75 | 8.16 | 4.24 |
| MOVER_TREND_PULLBACK | filtered | 2784 | 54.84 | 18.17 | 18.01 | 7.91 | 12.53 | 6.23 | 8.75 | 4.10 |
| MOVER_TREND_PULLBACK | kept | 2908 | 77.26 | 19.95 | 18.04 | 7.89 | 12.95 | 6.27 | 9.49 | 4.45 |
| QUIET_COMPRESSION_BREAK | filtered | 148 | 51.15 | 18.78 | 15.84 | 11.57 | 13.91 | 7.10 | 4.91 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 177 | 73.42 | 19.44 | 15.45 | 11.64 | 14.05 | 6.05 | 7.42 | 0.00 |
| SR_FLIP_RETEST | filtered | 148 | 54.63 | 21.74 | 17.26 | 5.09 | 13.22 | 5.57 | 6.28 | 1.92 |
| SR_FLIP_RETEST | kept | 53 | 75.55 | 23.34 | 18.00 | 6.23 | 14.15 | 6.20 | 8.12 | 2.79 |
| TREND_PULLBACK_EMA | filtered | 70 | 60.20 | 17.90 | 18.00 | 7.54 | 14.86 | 7.31 | 9.17 | 5.06 |
| TREND_PULLBACK_EMA | kept | 172 | 79.05 | 18.63 | 18.00 | 7.52 | 14.87 | 7.68 | 9.66 | 4.93 |
| VOLUME_SURGE_BREAKOUT | filtered | 55 | 51.75 | 18.31 | 17.85 | 12.00 | 12.31 | 4.82 | 3.02 | 3.76 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 71.38 | 19.00 | 15.00 | 12.75 | 14.00 | 5.75 | 8.07 | 4.25 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 110 | 57.74 | 0.00 | 0.00 | 3.33 | 0.00 | 0.44 | 0.24 | 0.00 | 0.00 | **4.01** |
| DIVERGENCE_CONTINUATION | kept | 260 | 68.63 | 0.00 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.04** |
| FAILED_AUCTION_RECLAIM | filtered | 117 | 38.46 | 0.00 | 0.00 | 0.00 | 0.00 | 2.69 | 0.00 | 0.00 | 0.00 | **2.69** |
| FAILED_AUCTION_RECLAIM | kept | 7 | 69.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 47.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 64 | 55.48 | 0.00 | 0.00 | 3.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.33** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 115 | 69.89 | 0.00 | 0.00 | 2.28 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.28** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 79.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 9 | 61.70 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MEAN_REVERT | kept | 33 | 80.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 270 | 52.63 | 0.42 | 0.00 | 1.19 | 0.00 | 1.69 | 0.11 | 0.00 | 1.13 | **4.54** |
| MOVER_AVWAP_SCALP | kept | 319 | 80.23 | 0.73 | 0.00 | 0.46 | 0.00 | 0.15 | 0.05 | 0.00 | 0.12 | **1.51** |
| MOVER_TREND_PULLBACK | filtered | 2784 | 54.84 | 0.57 | 0.00 | 2.19 | 0.00 | 0.57 | 0.04 | 0.00 | 0.03 | **3.40** |
| MOVER_TREND_PULLBACK | kept | 2908 | 77.26 | 0.02 | 0.00 | 0.47 | 0.00 | 0.15 | 0.01 | 0.00 | 0.00 | **0.65** |
| QUIET_COMPRESSION_BREAK | filtered | 148 | 51.15 | 0.00 | 0.00 | 0.56 | 0.00 | 0.48 | 0.43 | 0.00 | 5.34 | **6.81** |
| QUIET_COMPRESSION_BREAK | kept | 177 | 73.42 | 0.00 | 0.00 | 0.13 | 0.00 | 0.60 | 0.00 | 0.00 | 0.00 | **0.73** |
| SR_FLIP_RETEST | filtered | 148 | 54.63 | 0.00 | 0.00 | 1.90 | 0.00 | 0.88 | 0.00 | 0.00 | 0.00 | **2.78** |
| SR_FLIP_RETEST | kept | 53 | 75.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 70 | 60.20 | 0.00 | 0.00 | 2.06 | 0.00 | 5.86 | 0.14 | 0.00 | 0.00 | **8.06** |
| TREND_PULLBACK_EMA | kept | 172 | 79.05 | 0.00 | 0.00 | 1.12 | 0.00 | 0.13 | 0.03 | 0.00 | 0.00 | **1.28** |
| VOLUME_SURGE_BREAKOUT | filtered | 55 | 51.75 | 0.00 | 0.00 | 0.29 | 0.00 | 0.00 | 0.00 | 0.00 | 2.49 | **2.78** |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 71.38 | 0.00 | 0.00 | 3.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.20** |

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
- Outcomes recorded: **183403 held of 811979 seen** across 21 strategies; 4154 cells past the sample floor; **2210 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 48130 | 632/47498/0 | 44% | -0.18 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/QUIET/EXPANDED/BTC_FALLING/MAJOR (-1.26R) |
| MOVER_AVWAP_SCALP | 24375 | 196/24179/0 | 42% | -0.22 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 14244 | 217/14027/0 | 44% | -0.14 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | LONDON/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 13877 | 157/13720/0 | 35% | -0.34 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 12362 | 71/12291/0 | 38% | -0.31 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 10311 | 103/10208/0 | 37% | -0.43 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 8686 | 425/8261/0 | 46% | -0.13 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8107 | 0/0/8107 | 44% | -0.06 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+1.28R) | LONDON/QUIET/COMPRESSED/BTC_RISING (-0.82R) |
| SHADOW_RANGE_FADE | 7591 | 0/0/7591 | 36% | -0.13 | NY/RANGE/NORMAL/BTC_NEUTRAL (+0.34R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.25R) |
| SHADOW_FUNDING_FADE | 7101 | 0/0/7101 | 34% | -0.41 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.01R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 6162 | 24/6138/0 | 46% | -0.29 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.30R) |
| MEAN_REVERT | 5421 | 67/5354/0 | 36% | -0.34 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4027 | 2/4025/0 | 30% | -0.48 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3851 | 0/3851/0 | 28% | -0.42 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| RANGE_FADE | 2302 | 6/2296/0 | 40% | -0.21 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1684 | 0/0/1684 | 52% | -0.08 | ASIA/RANGE/EXPANDED/BTC_NEUTRAL (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.66R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 532 | 0/532/0 | 36% | -0.24 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 208 | 32/176/0 | 42% | -0.19 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 58 | 2/56/0 | 45% | +0.15 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `LIQUIDATION_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL` +2.71R (n=23, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 369 | 27% / -0.58R | 369 | 52% / -0.10R | +0.48 | **ATR** |
| TREND_PULLBACK_EMA | 1198 | 37% / -0.38R | 1198 | 49% / -0.09R | +0.29 | **ATR** |
| LIQUIDATION_REVERSAL | 33 | 24% / -0.61R | 33 | 45% / -0.35R | +0.26 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1567 | 42% / -0.37R | 1567 | 56% / -0.12R | +0.25 | **ATR** |
| MA_CROSS_TREND_SHIFT | 63 | 41% / -0.22R | 63 | 46% / -0.06R | +0.16 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 212 | 37% / -0.19R | 212 | 48% / -0.04R | +0.14 | **ATR** |
| SR_FLIP_RETEST | 628 | 45% / -0.29R | 628 | 50% / -0.16R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 2589 | 44% / -0.18R | 2589 | 50% / -0.05R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 8878 | 47% / -0.14R | 8878 | 53% / -0.02R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1504 | 41% / -0.23R | 1504 | 43% / -0.12R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| RANGE_FADE | 127 | 38% / -0.13R | 127 | 45% / -0.05R | +0.08 | **ATR** |
| DIVERGENCE_CONTINUATION | 1757 | 48% / -0.11R | 1757 | 53% / -0.06R | +0.05 | **ATR** |
| MEAN_REVERT | 436 | 47% / -0.15R | 436 | 46% / -0.16R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1513 | 46% / -0.14R | 1513 | 46% / -0.14R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 13 | 62% / -0.06R | 13 | 62% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11815 | 28% | -0.25R | 313 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2589 | 48% | -0.05R | 237 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 135 | 50% | -0.04R | 68 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1831 | 38% / -0.15R | +0.86 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1561 | 33% / -0.24R | +0.83 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3143 | 35% / -0.20R | +0.64 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10805 | 35% / -0.20R | +0.33 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2053 | 36% / -0.14R | +0.14 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1455 | 35% / -0.14R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1246 | 31% / -0.28R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 313 | 31% / -0.37R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 476 | 31% / -0.24R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 363 | 47% / -0.08R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 92 | 45% / +0.01R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 553 | 33% / -0.34R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 100 | 28% / -0.37R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 42 | 45% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 22 | 45% / +0.62R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `sar_ledger_candles` — 50/111 unfetchable (45%); top cause: gap or duplicate bar in the 15m window; symbols: ACTUSDT, ADAUSDT, AIOTUSDT, BCHUSDT, DOGEUSDT +13 more (streak 55/6) (sustained 55 cycles)
- **ALERT** `dark_resolution` — 2 of 120 open dark rows are not being advanced (worst: MEGAUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 146/120) (sustained 146 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 195/6) (sustained 195 cycles)
- **ALERT** `tuned_variants` — 287 non-stamps — atr_arm_uncomputable=287 (seen=5116 stamped=547 skipped=4282) (streak 195/6) (sustained 195 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 68641246 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 24 arms current, none stalled; covering 2075/2075 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 49 arms current, none stalled; covering 1077/1077 signals (100%) | 0 |
| auto_dispatch | ok | 54 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=54. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 88/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 73556.10 | 0 |
| candle_coverage | ok | 76/76 symbols with ≥20 15m candles, 76/76 updated within 45m [fresh=76; 73 Tier-1 futures + 3 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1197 dup bars, 0 undedupable; ws 0 out-of-order, 291 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +60 / upstream +21 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1458/1477 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 2 of 120 open dark rows are not being advanced (worst: MEGAUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 146/120) | 146 |
| dark_sar_arms | ok | no open arms; covering 1452/1471 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 15469711 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 195/6) | 195 |
| emission_controller | ok | last cycle 1676s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=976, MOVER_AVWAP_SCALP=401, MOVER_TREND_PULLBACK=3783, RANGE_FADE=561, TREND_PULLBACK_EMA=279), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 2 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 4/6) | 4 |
| firestore_read_budget | ok | 1,332 reads/day of 50,000 [engine 1,311, signing 21]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 1524 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +20 / upstream +541 | 0 |
| indicator_cache_key | ok | 56536 frozen value(s) avoided; 152633 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.34R over n=5354 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +151 / upstream +541 | 0 |
| mover_admission_metadata | ok | 942 symbols known, 235 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 3 held, 3 with scan counts, 3 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2177 rows held, 3483427 evicted (sampled: execution:trigger_not_confirmed 291/1227802, execution:overextended 291/1084807, setup_compat:regime_STRONG_TREND 291/595354) | 0 |
| price_action_lane | ok | 393380 evaluated, 685 emitted; layer1 685 stamped / 0 blind; cooldown=69589, delta_opposed=39155, no_footprint=131112, no_opposing_target=653, no_sweep=119363, rr_below_floor=32823 | 0 |
| promoted_pair_integrity | ok | 3/3 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.21R over n=2296 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +60 / upstream +541 | 0 |
| sar_alignment_crosscheck | ok | 162/11380 disagreed (1.4%) | 0 |
| sar_exit_shadow | ok | output +24 / upstream +541 | 0 |
| sar_hold_arm | ok | 1867 held arms settled, 133 unscored, 47 still walking (44 awaiting the second arm) | 0 |
| sar_ledger_candles | violating | 50/111 unfetchable (45%); top cause: gap or duplicate bar in the 15m window; symbols: ACTUSDT, ADAUSDT, AIOTUSDT, BCHUSDT, DOGEUSDT +13 more (streak 55/6) | 55 |
| sar_live_arms | ok | 47 arms current, none stalled; covering 1076/1076 signals (100%) | 0 |
| sar_refresh_budget | ok | 6 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 1 resolved, 60 still mid-window | 0 |
| scan_cycle | ok | last 79.76s, worst 263.84s over 5142 lifetime cycles; lifetime 190 over 60s, 39 over 120s (plus 1/0 during boot warm-up, not counted); recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 12.05s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 169830 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| snapshot_writer | ok | last cycle 18s ago (1.27s to run, worst 180.74s), 640 overrun(s) of 4148 cycles, TTL 900s; slowest data_intake=0.23s, signals=0.08s, pair_context=0.05s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +47 / upstream +541 | 0 |
| structural_snap | ok | 6000/6000 measured, 31 blind, 0 levels moved (refusals: redetect_cooldown=619) | 0 |
| structural_veto_lane | ok | 1102 stamped; 0 with no readable level book, 16 with clear air ahead, 876 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +541 / upstream +21 | 0 |
| tuned_variants | violating | 287 non-stamps — atr_arm_uncomputable=287 (seen=5116 stamped=547 skipped=4282) (streak 195/6) | 195 |
| unlock_shorts | ok | 16 open, 44 scheduled, calendar 5.9h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 23 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1949039`
- `Path funnel` emissions: `53`
- `Regime distribution` emissions: `53`
- `QUIET_SCALP_BLOCK` events: `204`
- `confidence_gate` events: `7841`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **27**
- Total REST-fallback activations: **6**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 6 | 6521 | 10510 | 40921 | 0 |
| futures_aggtrade | 17 | 7181 | 27212 | 33220 | 0 |
| futures_depth | 2 | 4047 | 4047 | 40928 | 0 |
| futures_liq | 2 | 2323 | 2323 | 9572 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 6 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=301693] state[populated=301693] buckets[few=8, many=301461, some=224] sources[none] quality[none]
- funding_rate: presence[absent=15828, present=285865] state[empty=15828, populated=285865] buckets[few=285865, none=15828] sources[none] quality[none]
- liquidation_clusters: presence[absent=171258, present=130435] state[empty=171258, populated=130435] buckets[few=104400, none=171258, some=26035] sources[none] quality[none]
- oi_snapshot: presence[absent=15160, present=286533] state[empty=15160, populated=286533] buckets[few=20, many=286178, none=15160, some=335] sources[none] quality[none]
- order_book: presence[absent=90451, present=211242] state[populated=211242, unavailable=90451] buckets[few=211242, none=90451] sources[book_ticker=211242, unavailable=90451] quality[none=90451, top_of_book_only=211242]
- orderblocks: presence[absent=301693] state[empty=301693] buckets[none=301693] sources[measured_dark=301693] quality[none]
- recent_ticks: presence[present=301693] state[populated=301693] buckets[many=301693] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.21455454826355` sec
- Median create→first breach: `5054.737372636795` sec
- Median create→terminal: `5055.23160803318` sec
- Median first breach→terminal: `6.139278411865234e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 3.3}, "under_180s": {"count": 2, "pct": 3.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 2, "pct": 3.3}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 8 | 8 | 0.8951525383417247 | 1.0555418672259433 | 0.8555414257937196 | 0 | 7 |
| FAILED_AUCTION_RECLAIM | 5 | 5 | 1.2061237128146538 | 1.3190309999999958 | 0.8576095151356036 | 0 | 4 |
| MOVER_AVWAP_SCALP | 6 | 6 | 2.2837611682565164 | 2.5654369651502815 | 0.8608458295538256 | 2 | 4 |
| MOVER_TREND_PULLBACK | 30 | 30 | 3.1073875902679022 | 3.0 | 1.0668573419584533 | 16 | 13 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 1.3215726748875234 | 1.4928342145285332 | 0.8905791454776578 | 0 | 8 |
| SR_FLIP_RETEST | 1 | 1 | 0.9622279880569025 | 1.1362894272840107 | 0.8468159299491551 | 0 | 1 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.780000000000015 | 1.0879025239338556 | 0.7169760000000138 | 0 | 1 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 8 | 1.8808018776862787 | 1.3773273193945652 | 0 | 0 | 0 | 3 | 0 | 5 |
| FAILED_AUCTION_RECLAIM | 5 | 2.7554968535469153 | 1.809185640732265 | 0 | 0 | 0 | 3 | 0 | 2 |
| MOVER_AVWAP_SCALP | 6 | 2.865793658391901 | 3.1939666888680183 | 4 | 1 | 0 | 2 | 0 | 0 |
| MOVER_TREND_PULLBACK | 29 | 5.082972061657032 | 3.9280799999999885 | 7 | 1 | 1 | 22 | 0 | 0 |
| QUIET_COMPRESSION_BREAK | 9 | 3.912430959080895 | 2.117587971819995 | 0 | 0 | 0 | 7 | 0 | 2 |
| SR_FLIP_RETEST | 1 | 2.6885015059259088 | 1.4433419820853448 | 0 | 0 | 0 | 1 | 0 | 0 |
| TREND_PULLBACK_EMA | 1 | 1.7928633594429897 | 1.7928633594429897 | 0 | 0 | 0 | 0 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 8 | 8 | 25.0 | 50.0 | 25.0 | 0.0 | -0.0516 | 3207.724483013153 | 3207.72452545166 |
| FAILED_AUCTION_RECLAIM | 5 | 5 | 0.0 | 80.0 | 0.0 | 0.0 | -0.8039 | 1704.708025932312 | 1704.7080590724945 |
| MOVER_AVWAP_SCALP | 6 | 6 | 16.7 | 33.3 | 16.7 | 0.0 | 0.0456 | 6543.811852931976 | 6543.8119159936905 |
| MOVER_TREND_PULLBACK | 30 | 30 | 30.0 | 36.7 | 30.0 | 0.0 | 0.2233 | 4912.737614631653 | 4913.231836557388 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 11.1 | 66.7 | 11.1 | 0.0 | -0.3952 | 27856.291033029556 | 27856.291093826294 |
| SR_FLIP_RETEST | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.9622 | 2907.495598077774 | 2907.4956209659576 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.0879 | 991.1212921142578 | 991.1213130950928 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 813 | 9 | 310 | 0.0 | 100.0 | 2907.495598077774 | 2907.4956209659576 | 503 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2022 | 44 | 1568 | 0.0 | 100.0 | 991.1212921142578 | 991.1213130950928 | 454 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `35`
- Gating Δ: `14872`
- No-generation Δ: `332523`
- Fast failures Δ: `2`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.3205, "current_avg_pnl": -0.0516, "current_win_rate": 25.0, "previous_avg_pnl": -0.3721, "previous_win_rate": 50.0, "win_rate_delta": -25.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.3286, "current_avg_pnl": -0.8039, "current_win_rate": 0.0, "previous_avg_pnl": -1.1325, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.0456, "current_avg_pnl": 0.0456, "current_win_rate": 16.7, "previous_avg_pnl": 0.0, "previous_win_rate": 0.0, "win_rate_delta": 16.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.2485, "current_avg_pnl": 0.2233, "current_win_rate": 30.0, "previous_avg_pnl": -0.0252, "previous_win_rate": 22.7, "win_rate_delta": 7.3}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.5647, "current_avg_pnl": -0.3952, "current_win_rate": 11.1, "previous_avg_pnl": 0.1695, "previous_win_rate": 20.0, "win_rate_delta": -8.9}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 5, "geometry_changed_delta": 0, "geometry_preserved_delta": 365, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2907.5, "median_terminal_delta_sec": 2907.5, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 6, "geometry_changed_delta": 0, "geometry_preserved_delta": 173, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 991.12, "median_terminal_delta_sec": 991.12, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **DIVERGENCE_CONTINUATION**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **DIVERGENCE_CONTINUATION**
