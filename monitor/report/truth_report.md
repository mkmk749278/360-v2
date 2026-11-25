# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `9` sec (warning=False)
- Latest performance record age: `1879` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 146 | 146 | 21 | 3 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 11880 | 11880 | 11081 | 12 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 72032 | 72053 | 13 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 72514 | 72514 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 72027 | 69229 | 3266 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 72543 | 71532 | 1095 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 71955 | 71813 | 179 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 62077 | 62096 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 72643 | 72663 | 21 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 72691 | 70755 | 2642 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 76750 | 81903 | 783 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 72071 | 64889 | 11803 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 71685 | 71685 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 72517 | 72531 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 71996 | 71955 | 68 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 73409 | 70468 | 4005 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 71686 | 71526 | 415 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 61627 | 59068 | 2897 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 61974 | 61482 | 588 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 71992 | 72020 | 4 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 62102 | 62115 | 7 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4565 | 4565 | 4239 | 7 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 655 | 655 | 192 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 11 | 11 | 3 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 16601 | 16601 | 16056 | 31 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 43 | 43 | 26 | 6 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 6593 | 6593 | 5672 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1884 | 1884 | 983 | 36 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 34126 | 34126 | 22851 | 296 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 14 | 14 | 14 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 668 | 668 | 542 | 18 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 9956 | 9956 | 9100 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1048 | 1048 | 692 | 6 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2562 | 2562 | 2292 | 22 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 66 | 66 | 36 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 437 | 437 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=72053): breakout_not_found=32091, basic_filters_failed=21796, move_not_fresh=13937, breakout_stale=3103, retest_proximity_failed=963, volume_spike_missing=163
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=72514): cls_disabled_merged_into_lsr=72514
- **EVAL::DIVERGENCE_CONTINUATION** (total=69229): cvd_divergence_failed=30173, basic_filters_failed=19654, h1_trend_not_aligned=13786, ema_alignment_reject=4727, retest_proximity_failed=663, missing_fvg_or_orderblock=223, cvd_insufficient=3
- **EVAL::FAILED_AUCTION_RECLAIM** (total=71532): auction_not_detected=42269, basic_filters_failed=19460, reclaim_hold_failed=5164, tail_too_small=3275, regime_blocked=1363, rsi_reject=1
- **EVAL::FUNDING_EXTREME** (total=71813): funding_not_extreme=49631, basic_filters_failed=19469, ema_alignment_reject=1460, rsi_reject=582, missing_funding_rate=345, cvd_divergence_failed=145, momentum_reject=125, missing_fvg_or_orderblock=56
- **EVAL::LIQUIDATION_REVERSAL** (total=62096): cascade_threshold_not_met=42458, basic_filters_failed=19287, cvd_divergence_failed=206, rsi_reject=134, missing_fvg_or_orderblock=7, volume_spike_missing=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=72663): no_ma_cross=51461, basic_filters_failed=19680, ma_cross_cooldown=1463, ma_cross_htf_misaligned=59
- **EVAL::MEAN_REVERT** (total=70755): no_extension=57658, basic_filters_failed=13097
- **EVAL::MOVER_AVWAP_SCALP** (total=81903): no_avwap_tag=34614, basic_filters_failed=22105, no_mover_leg=17209, avwap_slope_against=4532, avwap_reclaim_no_volume=2064, no_avwap_reclaim=1377, anchor_too_recent=2
- **EVAL::MOVER_TREND_PULLBACK** (total=64889): mover_run_too_small=27544, basic_filters_failed=21950, no_reclaim=13293, no_pullback_tag=2102
- **EVAL::OPENING_RANGE_BREAKOUT** (total=71685): feature_disabled=71685
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=72531): regime_blocked=37829, breakout_not_found=24165, basic_filters_failed=6545, adx_reject=3921, ema_alignment_reject=70, rsi_reject=1
- **EVAL::QUIET_COMPRESSION_BREAK** (total=71955): regime_blocked=35867, compression_not_detected=19198, basic_filters_failed=12896, breakout_not_detected=3669, volume_confirmation_failed=304, missing_fvg_or_orderblock=21
- **EVAL::RANGE_FADE** (total=70468): no_range_edge=57365, basic_filters_failed=13103
- **EVAL::SR_FLIP_RETEST** (total=71526): flip_close_not_confirmed=42880, basic_filters_failed=19418, retest_out_of_zone=2596, h1_break_not_confirmed=2372, long_break_volume_thin=1432, regime_blocked=1348, reclaim_hold_failed=1050, ema_alignment_reject=214, wick_quality_failed=129, whipsaw_flip=40, missing_fvg_or_orderblock=37, long_acceptance_not_held=10
- **EVAL::STANDARD** (total=59068): momentum_reject=21165, adx_reject=15362, basic_filters_failed=9611, sweeps_not_detected=4741, ema_alignment_reject=4127, macd_reject=3394, htf_poi_unanchored=605, rsi_reject=42, invalid_sl_geometry=15, mtf_reject=6
- **EVAL::TREND_PULLBACK** (total=61482): h1_trend_not_aligned=17012, basic_filters_failed=10870, ema_alignment_reject=9830, h1_pullback_not_confirmed=8658, ema_not_tested_prev=4814, no_ema_reclaim_close=3767, body_conviction_fail=2556, rsi_reject=2334, prev_already_below_emas=737, no_prev_low_break=587, prev_already_above_emas=99, no_prev_high_break=91, momentum_flat=71, missing_fvg_or_orderblock=31, momentum_reject=20, ema21_not_tagged=5
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=72020): breakout_not_found=44074, basic_filters_failed=21792, move_not_fresh=4122, breakout_stale=1381, retest_proximity_failed=519, volume_spike_missing=124, missing_fvg_or_orderblock=8
- **EVAL::WHALE_MOMENTUM** (total=62115): momentum_reject=51396, recent_ticks_insufficient=7795, basic_filters_failed=2924

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=262): setup_compat:regime_VOLATILE_UNSUITABLE=247, execution:overextended=15
- **FAILED_AUCTION_RECLAIM** (total=849): setup_compat:regime_STRONG_TREND=429, execution:overextended=359, setup_compat:regime_VOLATILE_UNSUITABLE=61
- **FUNDING_EXTREME_SIGNAL** (total=580): execution:trigger_not_confirmed=580
- **LIQUIDATION_REVERSAL** (total=11): execution:trigger_not_confirmed=11
- **LIQUIDITY_SWEEP_REVERSAL** (total=3394): execution:trigger_not_confirmed=1270, setup_compat:regime_STRONG_TREND=1170, execution:overextended=954
- **MA_CROSS_TREND_SHIFT** (total=19): setup_compat:regime_DIRTY_RANGE=8, setup_compat:regime_CLEAN_RANGE=6, execution:overextended=4, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=4360): setup_compat:regime_WEAK_TREND=2573, setup_compat:regime_STRONG_TREND=1336, execution:overextended=449, entry_quality=2
- **MOVER_AVWAP_SCALP** (total=870): execution:overextended=507, execution:trigger_not_confirmed=213, entry_quality=150
- **MOVER_TREND_PULLBACK** (total=11848): execution:trigger_not_confirmed=6384, execution:overextended=3749, entry_quality=1715
- **QUIET_COMPRESSION_BREAK** (total=23): execution:trigger_not_confirmed=23
- **RANGE_FADE** (total=7929): setup_compat:regime_WEAK_TREND=3989, setup_compat:regime_STRONG_TREND=3050, setup_compat:regime_VOLATILE_UNSUITABLE=431, execution:overextended=427, setup_compat:regime_BREAKOUT_EXPANSION=16, context_edge=16
- **TREND_PULLBACK_EMA** (total=1969): setup_compat:regime_CLEAN_RANGE=1310, setup_compat:regime_DIRTY_RANGE=463, entry_quality=130, setup_compat:regime_VOLATILE_UNSUITABLE=66
- **VOLUME_SURGE_BREAKOUT** (total=21): execution:overextended=21
- **WHALE_MOMENTUM** (total=298): execution:trigger_not_confirmed=298

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 157160 | 34.4% |
| TRENDING_DOWN | 131056 | 28.7% |
| QUIET | 89632 | 19.6% |
| TRENDING_UP | 64547 | 14.1% |
| VOLATILE | 14682 | 3.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **106**
- Average confidence gap to threshold: **10.69** (samples=106) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: INJUSDT=14, HYPEUSDT=12, ARBUSDT=11, AINUSDT=7, XRPUSDT=6, ETHFIUSDT=6, XLMUSDT=5, BTCUSDT=5, TAOUSDT=5, UNIUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 62 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 54 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 184 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 66 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 101 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 6 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 12 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 1 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 8 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 82 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 10 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 189 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 9 |
| MEAN_REVERT | kept | min_confidence_pass | 7 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 171 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 29 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 239 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1450 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 50 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3697 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 22 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 12 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 95 |
| SR_FLIP_RETEST | filtered | min_confidence | 130 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 17 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 25 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 18 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 8 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 47 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 29 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 62 | 62.22 | 64.42 | 2.20 | 23.21 | 19.39 | 20.00 | 4.35 | 12.84 |
| BREAKDOWN_SHORT | kept | 54 | 68.23 | 65.00 | -3.23 | 22.92 | 19.66 | 20.00 | 5.18 | 12.98 |
| DIVERGENCE_CONTINUATION | filtered | 187 | 51.63 | 64.33 | 12.70 | 20.27 | 19.82 | 16.38 | 1.06 | 17.17 |
| DIVERGENCE_CONTINUATION | kept | 66 | 68.22 | 65.00 | -3.22 | 20.33 | 19.36 | 17.67 | 1.17 | 0.46 |
| FAILED_AUCTION_RECLAIM | filtered | 107 | 50.38 | 63.97 | 13.59 | 20.96 | 19.34 | 20.00 | 2.86 | 11.30 |
| FAILED_AUCTION_RECLAIM | kept | 12 | 71.16 | 65.00 | -6.16 | 21.85 | 18.63 | 20.00 | 4.29 | 0.42 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 45.70 | 60.00 | 14.30 | 18.00 | 13.10 | 17.00 | 5.00 | 5.00 |
| LIQUIDATION_REVERSAL | filtered | 8 | 56.00 | 10.00 | -46.00 | 19.04 | 8.00 | 20.00 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 92 | 56.08 | 64.18 | 8.10 | 22.43 | 18.93 | 18.27 | 1.71 | 12.39 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 189 | 71.71 | 65.00 | -6.71 | 21.38 | 19.11 | 17.86 | 0.63 | 1.31 |
| MA_CROSS_TREND_SHIFT | kept | 9 | 69.86 | 65.00 | -4.86 | 20.78 | 18.60 | 15.80 | 0.00 | 0.50 |
| MEAN_REVERT | kept | 7 | 66.56 | 65.00 | -1.56 | 21.20 | 14.00 | 14.10 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 200 | 54.70 | 55.69 | 0.99 | 19.54 | 14.19 | 15.80 | 4.00 | 16.28 |
| MOVER_AVWAP_SCALP | kept | 239 | 77.49 | 65.00 | -12.49 | 20.00 | 14.92 | 15.80 | 4.63 | 3.20 |
| MOVER_TREND_PULLBACK | filtered | 1500 | 57.36 | 63.85 | 6.49 | 19.90 | 18.80 | 15.80 | 4.13 | 16.57 |
| MOVER_TREND_PULLBACK | kept | 3697 | 74.73 | 65.00 | -9.73 | 20.16 | 18.49 | 15.80 | 4.42 | 3.74 |
| QUIET_COMPRESSION_BREAK | filtered | 34 | 49.21 | 63.82 | 14.61 | 21.07 | 19.10 | 20.00 | 0.00 | 16.25 |
| QUIET_COMPRESSION_BREAK | kept | 95 | 71.46 | 65.00 | -6.46 | 21.46 | 19.41 | 20.00 | 0.00 | 5.08 |
| SR_FLIP_RETEST | filtered | 147 | 55.54 | 64.67 | 9.13 | 19.00 | 20.00 | 17.04 | 1.40 | 14.93 |
| SR_FLIP_RETEST | kept | 25 | 67.02 | 65.00 | -2.02 | 20.39 | 20.00 | 17.60 | 2.42 | 5.78 |
| TREND_PULLBACK_EMA | filtered | 26 | 55.11 | 65.00 | 9.89 | 21.74 | 20.00 | 17.67 | 5.65 | 14.00 |
| TREND_PULLBACK_EMA | kept | 47 | 78.73 | 65.00 | -13.73 | 20.21 | 19.68 | 17.86 | 5.03 | -0.10 |
| VOLUME_SURGE_BREAKOUT | filtered | 29 | 39.57 | 62.52 | 22.95 | 23.19 | 19.63 | 20.00 | 3.41 | 16.75 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 76.00 | 65.00 | -11.00 | 22.90 | 17.90 | 20.00 | 4.00 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 62 | 62.22 | 17.00 | 16.97 | 12.29 | 11.73 | 5.00 | 7.72 | 4.35 |
| BREAKDOWN_SHORT | kept | 54 | 68.23 | 22.63 | 15.11 | 12.17 | 13.22 | 5.00 | 7.90 | 5.18 |
| DIVERGENCE_CONTINUATION | filtered | 187 | 51.63 | 21.58 | 15.33 | 5.07 | 12.64 | 4.98 | 8.13 | 1.06 |
| DIVERGENCE_CONTINUATION | kept | 66 | 68.22 | 22.45 | 16.94 | 3.50 | 12.92 | 5.54 | 7.75 | 1.17 |
| FAILED_AUCTION_RECLAIM | filtered | 107 | 50.38 | 19.69 | 17.78 | 6.64 | 13.35 | 6.12 | 3.94 | 2.86 |
| FAILED_AUCTION_RECLAIM | kept | 12 | 71.16 | 23.67 | 16.67 | 3.50 | 12.75 | 6.62 | 5.58 | 4.29 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 45.70 | 25.00 | 8.00 | 9.00 | 12.00 | 5.00 | 1.70 | 5.00 |
| LIQUIDATION_REVERSAL | filtered | 8 | 56.00 | 21.00 | 18.00 | 15.00 | 8.00 | 5.00 | 0.00 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 92 | 56.08 | 21.48 | 15.09 | 5.32 | 11.60 | 5.57 | 7.72 | 1.71 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 189 | 71.71 | 23.39 | 15.20 | 6.65 | 13.35 | 5.24 | 8.67 | 0.63 |
| MA_CROSS_TREND_SHIFT | kept | 9 | 69.86 | 19.67 | 14.00 | 5.00 | 14.33 | 8.50 | 9.19 | 0.00 |
| MEAN_REVERT | kept | 7 | 66.56 | 17.86 | 14.00 | 9.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 200 | 54.70 | 19.11 | 18.00 | 11.96 | 13.76 | 6.62 | 5.72 | 4.00 |
| MOVER_AVWAP_SCALP | kept | 239 | 77.49 | 19.75 | 18.15 | 11.84 | 12.97 | 6.28 | 7.43 | 4.63 |
| MOVER_TREND_PULLBACK | filtered | 1500 | 57.36 | 18.27 | 18.00 | 7.76 | 12.15 | 5.72 | 9.19 | 4.13 |
| MOVER_TREND_PULLBACK | kept | 3697 | 74.73 | 19.21 | 18.01 | 8.05 | 13.05 | 6.46 | 9.36 | 4.42 |
| QUIET_COMPRESSION_BREAK | filtered | 34 | 49.21 | 15.53 | 15.41 | 12.79 | 14.44 | 5.81 | 7.18 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 95 | 71.46 | 19.19 | 17.16 | 11.08 | 14.06 | 6.64 | 8.44 | 0.00 |
| SR_FLIP_RETEST | filtered | 147 | 55.54 | 18.96 | 16.84 | 4.67 | 13.12 | 6.54 | 8.95 | 1.40 |
| SR_FLIP_RETEST | kept | 25 | 67.02 | 24.36 | 16.00 | 4.32 | 11.56 | 5.14 | 8.99 | 2.42 |
| TREND_PULLBACK_EMA | filtered | 26 | 55.11 | 10.46 | 18.00 | 9.92 | 14.00 | 5.00 | 8.38 | 5.65 |
| TREND_PULLBACK_EMA | kept | 47 | 78.73 | 18.28 | 18.00 | 7.56 | 14.13 | 7.26 | 9.33 | 5.03 |
| VOLUME_SURGE_BREAKOUT | filtered | 29 | 39.57 | 18.24 | 14.83 | 12.00 | 13.69 | 5.00 | 4.14 | 3.41 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 76.00 | 17.00 | 14.00 | 15.00 | 14.00 | 5.00 | 10.00 | 4.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 62 | 62.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.55 | 0.00 | 0.10 | **0.65** |
| BREAKDOWN_SHORT | kept | 54 | 68.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 187 | 51.63 | 0.00 | 0.00 | 0.92 | 0.00 | 0.00 | 0.19 | 0.00 | 0.00 | **1.11** |
| DIVERGENCE_CONTINUATION | kept | 66 | 68.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 107 | 50.38 | 0.00 | 0.00 | 0.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.82** |
| FAILED_AUCTION_RECLAIM | kept | 12 | 71.16 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.67** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 45.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 8 | 56.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 92 | 56.08 | 0.00 | 0.00 | 0.68 | 0.00 | 0.70 | 0.00 | 0.00 | 0.00 | **1.38** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 189 | 71.71 | 0.00 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.18** |
| MA_CROSS_TREND_SHIFT | kept | 9 | 69.86 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 7 | 66.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 200 | 54.70 | 0.00 | 0.00 | 1.40 | 0.00 | 0.94 | 0.36 | 0.00 | 2.35 | **5.05** |
| MOVER_AVWAP_SCALP | kept | 239 | 77.49 | 0.00 | 0.00 | 1.87 | 0.00 | 0.20 | 0.08 | 0.00 | 0.63 | **2.78** |
| MOVER_TREND_PULLBACK | filtered | 1500 | 57.36 | 0.00 | 0.00 | 3.22 | 0.00 | 0.26 | 0.15 | 0.00 | 0.00 | **3.63** |
| MOVER_TREND_PULLBACK | kept | 3697 | 74.73 | 0.00 | 0.00 | 1.36 | 0.00 | 0.17 | 0.06 | 0.00 | 0.01 | **1.60** |
| QUIET_COMPRESSION_BREAK | filtered | 34 | 49.21 | 0.00 | 0.00 | 0.47 | 0.00 | 0.76 | 1.76 | 0.00 | 3.14 | **6.13** |
| QUIET_COMPRESSION_BREAK | kept | 95 | 71.46 | 0.00 | 0.00 | 0.99 | 0.00 | 0.72 | 0.00 | 0.00 | 0.00 | **1.71** |
| SR_FLIP_RETEST | filtered | 147 | 55.54 | 0.00 | 0.00 | 0.00 | 0.00 | 1.03 | 0.00 | 0.00 | 0.00 | **1.03** |
| SR_FLIP_RETEST | kept | 25 | 67.02 | 0.00 | 0.00 | 0.19 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.19** |
| TREND_PULLBACK_EMA | filtered | 26 | 55.11 | 0.00 | 0.00 | 2.89 | 0.00 | 4.15 | 0.00 | 0.00 | 0.00 | **7.04** |
| TREND_PULLBACK_EMA | kept | 47 | 78.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | 0.00 | **0.26** |
| VOLUME_SURGE_BREAKOUT | filtered | 29 | 39.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.62 | **6.62** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 76.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **203506 held of 1007644 seen** across 21 strategies; 4610 cells past the sample floor; **2519 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 49525 | 609/48916/0 | 43% | -0.19 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/QUIET/EXPANDED/BTC_FALLING/MAJOR (-1.26R) |
| MOVER_AVWAP_SCALP | 26824 | 189/26635/0 | 45% | -0.15 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 16448 | 280/16168/0 | 47% | -0.11 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.98R) | NY/MARKUP/NORMAL/BTC_NEUTRAL (-1.19R) |
| FAILED_AUCTION_RECLAIM | 15537 | 198/15339/0 | 36% | -0.30 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+1.69R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 14699 | 84/14615/0 | 38% | -0.31 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 11909 | 134/11775/0 | 39% | -0.40 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.91R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9860 | 518/9342/0 | 44% | -0.11 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8524 | 0/0/8524 | 42% | -0.12 | OVERLAP/MARKUP/CASCADE/BTC_RISING (+1.58R) | OVERLAP/MARKDOWN/EXPANDED/BTC_FALLING (-0.96R) |
| SHADOW_RANGE_FADE | 8059 | 0/0/8059 | 36% | -0.14 | ASIA/MARKDOWN/NORMAL/BTC_FALLING (+1.03R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.36R) |
| SR_FLIP_RETEST | 7783 | 30/7753/0 | 47% | -0.28 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.30R) |
| SHADOW_FUNDING_FADE | 7716 | 0/0/7716 | 35% | -0.40 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (-0.01R) | OFF_HOURS/RANGE/NORMAL/BTC_RISING (-0.95R) |
| MEAN_REVERT | 6116 | 79/6037/0 | 36% | -0.32 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.60R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4827 | 4/4823/0 | 33% | -0.40 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+0.95R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.30R) |
| VOLUME_SURGE_BREAKOUT | 4426 | 0/4426/0 | 30% | -0.36 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/NORMAL/BTC_FALLING/ALTCOIN (-1.19R) |
| WHALE_MOMENTUM | 4395 | 4/4391/0 | 47% | -0.28 | NY/RANGE/EXPANDED/BTC_FALLING (+0.94R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| RANGE_FADE | 3359 | 6/3353/0 | 54% | +0.32 | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (+3.08R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.78R) |
| SHADOW_CASCADE_REVERSAL | 1821 | 0/0/1821 | 52% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 736 | 80/656/0 | 31% | -0.25 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 588 | 0/588/0 | 34% | -0.30 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 266 | 42/224/0 | 45% | -0.15 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 88 | 8/80/0 | 36% | +0.04 | — | — |

- **Strongest cells**: `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.08R (n=37, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.00R (n=32, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.78R (n=47, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 484 | 28% / -0.53R | 484 | 52% / -0.09R | +0.44 | **ATR** |
| TREND_PULLBACK_EMA | 1533 | 38% / -0.37R | 1533 | 50% / -0.08R | +0.28 | **ATR** |
| LIQUIDATION_REVERSAL | 36 | 28% / -0.55R | 36 | 47% / -0.30R | +0.24 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1896 | 45% / -0.33R | 1896 | 58% / -0.10R | +0.23 | **ATR** |
| SR_FLIP_RETEST | 882 | 47% / -0.26R | 882 | 52% / -0.13R | +0.13 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 256 | 37% / -0.16R | 256 | 48% / -0.03R | +0.13 | **ATR** |
| MA_CROSS_TREND_SHIFT | 81 | 47% / -0.13R | 81 | 52% / -0.01R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 9374 | 48% / -0.14R | 9374 | 53% / -0.04R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 473 | 46% / -0.30R | 473 | 48% / -0.20R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 3057 | 47% / -0.12R | 3057 | 53% / -0.02R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1769 | 42% / -0.21R | 1769 | 44% / -0.12R | +0.09 | **ATR** |
| BREAKDOWN_SHORT | 63 | 40% / -0.18R | 63 | 44% / -0.10R | +0.08 | **ATR** |
| DIVERGENCE_CONTINUATION | 2235 | 47% / -0.12R | 2235 | 52% / -0.06R | +0.06 | **ATR** |
| RANGE_FADE | 190 | 45% / +0.09R | 190 | 52% / +0.12R | +0.03 | **ATR** |
| MEAN_REVERT | 537 | 45% / -0.18R | 537 | 44% / -0.19R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 16 | 50% / -0.08R | 16 | 50% / -0.08R | -0.00 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1764 | 48% / -0.09R | 1764 | 49% / -0.09R | +0.00 | **ATR** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12445 | 27% | -0.23R | 314 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 3057 | 51% | -0.01R | 246 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 163 | 48% | -0.04R | 77 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1964 | 33% / -0.15R | +0.92 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 2240 | 40% / -0.12R | +0.89 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3641 | 37% / -0.13R | +0.72 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11447 | 36% / -0.16R | +0.37 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2594 | 36% / -0.14R | +0.14 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 172 | 34% / -0.39R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1705 | 37% / -0.10R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1479 | 32% / -0.28R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 376 | 32% / -0.26R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 590 | 32% / -0.26R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 442 | 47% / -0.10R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 104 | 43% / +0.01R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 135 | 45% / +0.03R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 757 | 36% / -0.24R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 130 | 32% / +0.11R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 48 | 42% / -0.35R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 32 | 44% / +0.34R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 64 · alerting: **4** · boot grace active: False
- **ALERT** `sar_alignment_crosscheck` — 82/650 disagreed (12.6%) (streak 6/6) (sustained 6 cycles)
- **ALERT** `sar_ledger_candles` — 52/110 unfetchable (47%); top cause: gap or duplicate bar in the 15m window; symbols: 1000PEPEUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, APTUSDT +26 more (streak 6/6) (sustained 6 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.53R (bound 0.3) (streak 6/6) (sustained 6 cycles)
- **ALERT** `range_fade_emission` — 370 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.32R over n=3353, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 6/6) (sustained 6 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 1074155 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 21 arms current, none stalled; covering 2029/2029 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| analyst_plan_cadence | ok | last plan 19m ago | 0 |
| atr_trail_live_arms | ok | 39 arms current, none stalled; covering 1032/1032 signals (100%) | 0 |
| auto_dispatch | ok | placed=0 rejected=0 skipped=3 over 3 fan-out(s) to a keyed roster; top reasons: venue:coindcx=3 (gaps: skip 2, empty-roster 0; threshold 5) | 0 |
| binance_ip_weight | ok | peak 113/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 59364.50 | 0 |
| candle_coverage | ok | 77/77 symbols with ≥20 15m candles, 77/77 updated within 45m [fresh=77; 75 Tier-1 futures + 2 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 551 dup bars, 0 undedupable; ws 0 out-of-order, 187 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 65 cohorts, 23 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +66 / upstream +55 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1199/1218 signals (98%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 21 of 121 open dark rows are not being advanced (worst: TIAUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 6/120) | 6 |
| dark_sar_arms | ok | no open arms; covering 1188/1207 signals (98%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 309170 msgs, 0 rejected | 0 |
| deriv_recorder | ok | hour recorded, 75 rows | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.53R (bound 0.3) (streak 6/6) | 6 |
| emission_controller | ok | last cycle 1s ago; live_overrides=14 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=1994, MOVER_AVWAP_SCALP=405, MOVER_TREND_PULLBACK=3019, RANGE_FADE=483, TREND_PULLBACK_EMA=99), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 4 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won,TREND_PULLBACK_EMA.campaign_prev_age_h,TREND_PULLBACK_EMA.campaign_prev_won) | 0 |
| entry_quality_effective | ok | 307 evaluated, 133 suppressed, 5 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,469 reads/day of 50,000 [engine 1,427, signing 42]; top site keystore.roster_doc at 319/day (engine) | 0 |
| footprint_bars | ok | 2680 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +3 / upstream +759 | 0 |
| htf_candles | ok | BTCUSDT 1d/1w current | 0 |
| indicator_cache_key | ok | 148 frozen value(s) avoided; 14204 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.33R over n=6037 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +17 / upstream +759 | 0 |
| mover_admission_metadata | ok | 956 symbols known, 247 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 2 held, 2 with scan counts, 2 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 11 locked / 11 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2199 rows held, 3874439 evicted (sampled: execution:trigger_not_confirmed 284/1355433, execution:overextended 284/1181695, setup_compat:regime_STRONG_TREND 284/675688) | 0 |
| price_action_lane | ok | 31387 evaluated, 26 emitted; layer1 26 stamped / 0 blind; cooldown=4994, delta_opposed=3029, no_footprint=10912, no_opposing_target=143, no_sweep=9241, rr_below_floor=3042 | 0 |
| promoted_pair_integrity | ok | 2/2 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 370 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.32R over n=3353, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 6/6) | 6 |
| range_fade_path | ok | output +67 / upstream +759 | 0 |
| sar_alignment_crosscheck | violating | 82/650 disagreed (12.6%) (streak 6/6) | 6 |
| sar_exit_shadow | ok | output +10 / upstream +759 | 0 |
| sar_hold_arm | ok | 1864 held arms settled, 137 unscored, 38 still walking (31 awaiting the second arm) | 0 |
| sar_ledger_candles | violating | 52/110 unfetchable (47%); top cause: gap or duplicate bar in the 15m window; symbols: 1000PEPEUSDT, AAVEUSDT, ACEUSDT, ADAUSDT, APTUSDT +26 more (streak 6/6) | 6 |
| sar_live_arms | ok | 39 arms current, none stalled; covering 1031/1031 signals (100%) | 0 |
| sar_refresh_budget | ok | 9 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 510 records await one (58 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 36.95s, worst 58.11s over 419 lifetime cycles; lifetime 0 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 2.11s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 13838 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| snapshot_writer | ok | last cycle 11s ago (5.92s to run, worst 44.38s), 14 overrun(s) of 246 cycles, TTL 900s; slowest signals=4.69s, tickers=0.86s, agents=0.74s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +496 / upstream +759 | 0 |
| structural_snap | ok | 6000/6000 measured, 31 blind, 0 levels moved (refusals: redetect_cooldown=56) | 0 |
| structural_veto_lane | ok | 81 stamped; 0 with no readable level book, 3 with clear air ahead, 76 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +759 / upstream +55 | 0 |
| tuned_variants | ok | seen=189 stamped=17 skipped=164, residue 8 (atr_arm_uncomputable=8) | 0 |
| unlock_shorts | ok | 15 open, 48 scheduled, calendar 3.2h old | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2199634`
- `Path funnel` emissions: `57`
- `Regime distribution` emissions: `57`
- `QUIET_SCALP_BLOCK` events: `106`
- `confidence_gate` events: `6834`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **14**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 4020 | 4020 | 4020 | 0 |
| futures_aggtrade | 1 | 9046 | 9046 | 9046 | 0 |
| futures_depth | 3 | 10576 | 10576 | 35557 | 0 |
| futures_liq | 7 | 4162 | 5437 | 11987 | 0 |
| futures_mover | 2 | 48556 | 48556 | 48638 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[absent=4, present=348462] state[empty=4, populated=348462] buckets[few=4, many=348399, none=4, some=59] sources[none] quality[none]
- funding_rate: presence[absent=16077, present=332389] state[empty=16077, populated=332389] buckets[few=332389, none=16077] sources[none] quality[none]
- liquidation_clusters: presence[absent=201781, present=146685] state[empty=201781, populated=146685] buckets[few=125403, none=201781, some=21282] sources[none] quality[none]
- oi_snapshot: presence[absent=15178, present=333288] state[empty=15178, populated=333288] buckets[few=165, many=332413, none=15178, some=710] sources[none] quality[none]
- order_book: presence[absent=101567, present=246899] state[populated=246899, unavailable=101567] buckets[few=246899, none=101567] sources[book_ticker=246899, unavailable=101567] quality[none=101567, top_of_book_only=246899]
- orderblocks: presence[absent=348466] state[empty=348466] buckets[none=348466] sources[measured_dark=348466] quality[none]
- recent_ticks: presence[present=348466] state[populated=348466] buckets[many=348466] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.505154967308044` sec
- Median create→first breach: `2844.5960166454315` sec
- Median create→terminal: `2845.0955476760864` sec
- Median first breach→terminal: `8.106231689453125e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 1.9}, "under_180s": {"count": 1, "pct": 1.9}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 1.5228615440047073 | 3.0 | 0.5221527965243687 | 0 | 3 |
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.9226786670618612 | 1.0610845504919797 | 0.8695618710441636 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 7 | 7 | 1.1802553742539164 | 1.5073115860517436 | 0.8861451119603206 | 0 | 7 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.801417004048575 | 0.9832272990167719 | 0.8150882352941102 | 0 | 1 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 10.381929965249933 | 1.867848440256616 | 5.558229319624885 | 1 | 0 |
| MOVER_AVWAP_SCALP | 2 | 2 | 2.286954351762252 | 2.210639032258063 | 0.9992362612645749 | 1 | 1 |
| MOVER_TREND_PULLBACK | 32 | 32 | 4.27707610223718 | 3.0 | 1.5084345761048068 | 25 | 7 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 1.1155573210460927 | 1.235464286306023 | 0.8895725553653994 | 0 | 5 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 5.604719764011796 | 5.604719764011796 | 0 | 0 | 0 | 1 | 0 | 2 |
| DIVERGENCE_CONTINUATION | 1 | 1.4807014737745683 | 1.3840180031478597 | 0 | 0 | 0 | 1 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 7 | 2.0904215338305336 | 2.074605014191104 | 2 | 0 | 0 | 3 | 0 | 2 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1.2021255060728713 | 1.2052510323886596 | 0 | 0 | 0 | 0 | 0 | 1 |
| MA_CROSS_TREND_SHIFT | 1 | 15.572894947874897 | 2.4508568275861955 | 0 | 0 | 0 | 1 | 0 | 0 |
| MOVER_AVWAP_SCALP | 2 | 2.1894525942022356 | 2.7613371304605328 | 2 | 2 | 2 | 0 | 0 | 0 |
| MOVER_TREND_PULLBACK | 32 | 5.603195519343438 | 3.984325664457765 | 4 | 1 | 1 | 28 | 3 | 0 |
| QUIET_COMPRESSION_BREAK | 5 | 2.9500211518756156 | 1.6733359815691253 | 0 | 0 | 0 | 5 | 0 | 0 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.0 | -0.3946 | 2657.5420200824738 | 2657.542067050934 |
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.9227 | 3531.4805340766907 | 3531.4805560112 |
| FAILED_AUCTION_RECLAIM | 7 | 7 | 14.3 | 71.4 | 14.3 | 0.0 | -0.6207 | 5398.066882133484 | 5398.066960096359 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.2053 | 716.2286579608917 | 716.9420897960663 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 3672.0992889404297 | 3672.099312067032 |
| MOVER_AVWAP_SCALP | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 1.8015 | 16033.46494948864 | 16033.663449048996 |
| MOVER_TREND_PULLBACK | 32 | 32 | 34.4 | 56.2 | 34.4 | 0.0 | -0.4109 | 1969.8820999860764 | 1970.569151878357 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 20.0 | 40.0 | 20.0 | 0.0 | -0.2117 | 11190.064790964127 | 11190.064872026443 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1048 | 6 | 692 | 0.0 | 0.0 | None | None | 356 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2562 | 22 | 2292 | 0.0 | 0.0 | None | None | 270 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `64`
- Gating Δ: `33337`
- No-generation Δ: `175039`
- Fast failures Δ: `0`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.3946, "current_avg_pnl": -0.3946, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.5208, "current_avg_pnl": -0.6207, "current_win_rate": 14.3, "previous_avg_pnl": -0.0999, "previous_win_rate": 33.3, "win_rate_delta": -19.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.0862, "current_avg_pnl": 1.8015, "current_win_rate": 50.0, "previous_avg_pnl": 1.8877, "previous_win_rate": 66.7, "win_rate_delta": -16.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.292, "current_avg_pnl": -0.4109, "current_win_rate": 34.4, "previous_avg_pnl": -0.1189, "previous_win_rate": 29.6, "win_rate_delta": 4.8}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.3537, "current_avg_pnl": -0.2117, "current_win_rate": 20.0, "previous_avg_pnl": 0.142, "previous_win_rate": 30.0, "win_rate_delta": -10.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.8998, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": -0.8998, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": 315, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": 71, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2487.1, "median_terminal_delta_sec": -2487.1, "sl_rate_delta": -66.7, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
