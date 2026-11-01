# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: FAILED_AUCTION_RECLAIM
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `762` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 64 | 64 | 64 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6720 | 6720 | 5855 | 13 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 66499 | 66498 | 20 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 60653 | 60654 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 60170 | 58343 | 2295 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 60685 | 59988 | 775 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 60250 | 60024 | 270 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 52618 | 52626 | 9 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 60774 | 60810 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 60818 | 58797 | 2727 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 69872 | 74638 | 652 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 66522 | 61575 | 8243 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 59985 | 59986 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 60661 | 60674 | 8 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 60106 | 59976 | 183 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 61529 | 60563 | 1353 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 59798 | 59929 | 116 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 52046 | 49605 | 2737 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 52350 | 52073 | 344 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 66467 | 66477 | 15 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 52638 | 52647 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1979 | 1979 | 1462 | 3 | active-healthy (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 655 | 655 | 120 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 18 | 18 | 7 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 11513 | 11513 | 11119 | 15 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 13 | 13 | 9 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 5486 | 5486 | 3381 | 3 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1355 | 1355 | 400 | 58 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 18068 | 18068 | 8019 | 329 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 20 | 20 | 19 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 674 | 674 | 308 | 50 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 2895 | 2895 | 1862 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 312 | 312 | 181 | 4 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1191 | 1191 | 878 | 34 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 63 | 63 | 60 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=66498): breakout_not_found=41413, basic_filters_failed=14381, move_not_fresh=6595, breakout_stale=2813, retest_proximity_failed=991, volume_spike_missing=219, insufficient_candles=71, missing_fvg_or_orderblock=8, move_exhausted=7
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=60654): cls_disabled_merged_into_lsr=60654
- **EVAL::DIVERGENCE_CONTINUATION** (total=58343): cvd_divergence_failed=21758, h1_trend_not_aligned=19019, basic_filters_failed=12373, ema_alignment_reject=4002, retest_proximity_failed=920, missing_fvg_or_orderblock=271
- **EVAL::FAILED_AUCTION_RECLAIM** (total=59988): auction_not_detected=41662, basic_filters_failed=11938, reclaim_hold_failed=2730, regime_blocked=1870, tail_too_small=1731, rsi_reject=57
- **EVAL::FUNDING_EXTREME** (total=60024): funding_not_extreme=41943, basic_filters_failed=11506, missing_funding_rate=3335, ema_alignment_reject=1654, rsi_reject=1122, cvd_divergence_failed=207, momentum_reject=207, missing_fvg_or_orderblock=47, insufficient_candles=3
- **EVAL::LIQUIDATION_REVERSAL** (total=52626): cascade_threshold_not_met=39858, basic_filters_failed=12174, cvd_divergence_failed=269, rsi_reject=263, insufficient_candles=47, missing_fvg_or_orderblock=13, volume_spike_missing=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=60810): no_ma_cross=46708, basic_filters_failed=12393, ma_cross_cooldown=1127, ma_cross_htf_misaligned=582
- **EVAL::MEAN_REVERT** (total=58797): no_extension=50498, basic_filters_failed=8299
- **EVAL::MOVER_AVWAP_SCALP** (total=74638): no_mover_leg=27859, no_avwap_tag=22300, basic_filters_failed=14543, avwap_slope_against=6571, avwap_reclaim_no_volume=1635, no_avwap_reclaim=1438, insufficient_candles=196, anchor_too_recent=96
- **EVAL::MOVER_TREND_PULLBACK** (total=61575): mover_run_too_small=33463, basic_filters_failed=14430, no_reclaim=11880, no_pullback_tag=1606, insufficient_candles=196
- **EVAL::OPENING_RANGE_BREAKOUT** (total=59986): feature_disabled=59986
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=60674): regime_blocked=40300, breakout_not_found=15162, basic_filters_failed=2684, adx_reject=2454, ema_alignment_reject=74
- **EVAL::QUIET_COMPRESSION_BREAK** (total=59976): regime_blocked=22119, compression_not_detected=19296, basic_filters_failed=9236, breakout_not_detected=8529, volume_confirmation_failed=770, rsi_reject=20, missing_fvg_or_orderblock=6
- **EVAL::RANGE_FADE** (total=60563): no_range_edge=52253, basic_filters_failed=8310
- **EVAL::SR_FLIP_RETEST** (total=59929): flip_close_not_confirmed=41698, basic_filters_failed=11900, regime_blocked=1854, long_break_volume_thin=1491, retest_out_of_zone=1218, h1_break_not_confirmed=939, reclaim_hold_failed=523, long_acceptance_not_held=108, ema_alignment_reject=77, whipsaw_flip=62, wick_quality_failed=47, missing_fvg_or_orderblock=12
- **EVAL::STANDARD** (total=49605): momentum_reject=16280, adx_reject=12615, basic_filters_failed=5859, sweeps_not_detected=5769, macd_reject=4590, ema_alignment_reject=3156, htf_poi_unanchored=1212, rsi_reject=82, invalid_sl_geometry=24, mtf_reject=18
- **EVAL::TREND_PULLBACK** (total=52073): h1_trend_not_aligned=20916, ema_alignment_reject=9016, basic_filters_failed=6764, h1_pullback_not_confirmed=4229, no_ema_reclaim_close=3378, ema_not_tested_prev=3093, body_conviction_fail=1933, rsi_reject=1466, prev_already_below_emas=440, prev_already_above_emas=268, no_prev_low_break=234, no_prev_high_break=135, momentum_flat=91, missing_fvg_or_orderblock=48, momentum_reject=35, ema21_not_tagged=27
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=66477): breakout_not_found=40244, basic_filters_failed=14375, move_not_fresh=7979, breakout_stale=2780, retest_proximity_failed=894, volume_spike_missing=127, insufficient_candles=71, missing_fvg_or_orderblock=7
- **EVAL::WHALE_MOMENTUM** (total=52647): momentum_reject=44376, recent_ticks_insufficient=7250, basic_filters_failed=1021

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=7): execution:overextended=7
- **DIVERGENCE_CONTINUATION** (total=224): setup_compat:regime_VOLATILE_UNSUITABLE=218, setup_compat:regime_BREAKOUT_EXPANSION=6
- **FAILED_AUCTION_RECLAIM** (total=677): setup_compat:regime_STRONG_TREND=454, execution:overextended=158, context_floor=65
- **FUNDING_EXTREME_SIGNAL** (total=559): execution:trigger_not_confirmed=523, context_floor=36
- **LIQUIDATION_REVERSAL** (total=18): execution:trigger_not_confirmed=18
- **LIQUIDITY_SWEEP_REVERSAL** (total=2976): execution:trigger_not_confirmed=1315, execution:overextended=866, setup_compat:regime_STRONG_TREND=795
- **MA_CROSS_TREND_SHIFT** (total=12): setup_compat:regime_DIRTY_RANGE=4, execution:overextended=3, execution:trigger_not_confirmed=3, setup_compat:regime_CLEAN_RANGE=2
- **MEAN_REVERT** (total=3736): setup_compat:regime_STRONG_TREND=1676, setup_compat:regime_WEAK_TREND=1511, execution:overextended=548, entry_quality=1
- **MOVER_AVWAP_SCALP** (total=1092): execution:overextended=788, entry_quality=177, execution:trigger_not_confirmed=127
- **MOVER_TREND_PULLBACK** (total=8770): execution:trigger_not_confirmed=4776, execution:overextended=2428, entry_quality=1566
- **QUIET_COMPRESSION_BREAK** (total=44): execution:trigger_not_confirmed=44
- **RANGE_FADE** (total=1607): setup_compat:regime_WEAK_TREND=851, setup_compat:regime_STRONG_TREND=543, execution:overextended=139, setup_compat:regime_VOLATILE_UNSUITABLE=38, context_edge=35, setup_compat:regime_BREAKOUT_EXPANSION=1
- **TREND_PULLBACK_EMA** (total=1131): setup_compat:regime_CLEAN_RANGE=814, setup_compat:regime_DIRTY_RANGE=245, entry_quality=51, setup_compat:regime_VOLATILE_UNSUITABLE=21
- **VOLUME_SURGE_BREAKOUT** (total=17): execution:overextended=17

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 102011 | 33.1% |
| QUIET | 99128 | 32.2% |
| TRENDING_UP | 53756 | 17.5% |
| TRENDING_DOWN | 43334 | 14.1% |
| VOLATILE | 9800 | 3.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **236**
- Average confidence gap to threshold: **16.14** (samples=236) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XMRUSDT=34, BNBUSDT=28, SOLUSDT=19, WLDUSDT=19, LTCUSDT=15, ENAUSDT=15, ETHUSDT=13, SPKUSDT=9, ONDOUSDT=8, ARBUSDT=8

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 126 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 15 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 143 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 62 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 26 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 7 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 10 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 35 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 20 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 77 |
| MEAN_REVERT | filtered | min_confidence | 73 |
| MEAN_REVERT | kept | min_confidence_pass | 3 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 161 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 258 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1174 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 12 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3001 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 147 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 29 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 127 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 10 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 19 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 44 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 6 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 136 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 3 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 141 | 55.46 | 64.48 | 9.02 | 21.49 | 19.62 | 17.43 | 0.75 | 12.91 |
| DIVERGENCE_CONTINUATION | kept | 143 | 69.07 | 65.00 | -4.07 | 21.28 | 19.29 | 17.85 | 1.29 | 1.71 |
| FAILED_AUCTION_RECLAIM | filtered | 88 | 48.11 | 62.56 | 14.45 | 19.59 | 19.71 | 20.00 | 1.62 | 7.04 |
| FAILED_AUCTION_RECLAIM | kept | 7 | 69.21 | 65.00 | -4.21 | 20.56 | 17.94 | 20.00 | 2.79 | 4.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 10 | 47.43 | 60.80 | 13.37 | 20.42 | 17.60 | 17.00 | 3.40 | 5.00 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 70.25 | 65.00 | -5.25 | 21.15 | 14.00 | 17.95 | 4.00 | 1.25 |
| LIQUIDATION_REVERSAL | filtered | 1 | 50.30 | 10.00 | -40.30 | 21.20 | 8.00 | 20.00 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 55 | 47.32 | 65.00 | 17.68 | 21.25 | 18.95 | 17.97 | 1.96 | 10.20 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 77 | 71.89 | 65.00 | -6.89 | 21.69 | 18.93 | 17.92 | 0.96 | -0.07 |
| MEAN_REVERT | filtered | 73 | 54.92 | 65.00 | 10.08 | 19.16 | 15.38 | 16.75 | 0.00 | 9.86 |
| MEAN_REVERT | kept | 3 | 69.57 | 65.00 | -4.57 | 20.47 | 16.23 | 17.23 | 0.00 | 3.00 |
| MOVER_AVWAP_SCALP | filtered | 161 | 51.45 | 64.86 | 13.41 | 19.50 | 14.89 | 15.80 | 3.39 | 16.32 |
| MOVER_AVWAP_SCALP | kept | 258 | 79.54 | 65.00 | -14.54 | 19.36 | 15.19 | 15.80 | 4.24 | 1.36 |
| MOVER_TREND_PULLBACK | filtered | 1186 | 56.68 | 63.49 | 6.81 | 20.15 | 18.24 | 15.80 | 3.91 | 16.86 |
| MOVER_TREND_PULLBACK | kept | 3001 | 76.52 | 65.00 | -11.52 | 20.28 | 18.88 | 15.80 | 4.27 | 1.82 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 88.50 | 65.00 | -23.50 | 19.70 | 20.00 | 15.40 | 4.50 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 176 | 50.14 | 64.95 | 14.81 | 21.47 | 19.36 | 20.00 | 0.00 | 12.27 |
| QUIET_COMPRESSION_BREAK | kept | 127 | 75.17 | 65.00 | -10.17 | 20.65 | 19.63 | 20.00 | 0.00 | -0.69 |
| SR_FLIP_RETEST | filtered | 10 | 55.12 | 65.00 | 9.88 | 21.12 | 20.00 | 15.20 | 2.35 | 15.72 |
| SR_FLIP_RETEST | kept | 19 | 69.68 | 65.00 | -4.68 | 19.41 | 20.00 | 15.43 | 3.00 | 6.73 |
| TREND_PULLBACK_EMA | filtered | 50 | 50.74 | 65.00 | 14.26 | 20.21 | 18.97 | 18.60 | 4.64 | 24.71 |
| TREND_PULLBACK_EMA | kept | 136 | 77.74 | 65.00 | -12.74 | 20.83 | 19.48 | 17.69 | 4.69 | 0.06 |
| VOLUME_SURGE_BREAKOUT | filtered | 3 | 52.23 | 62.33 | 10.10 | 19.50 | 16.30 | 20.00 | 3.83 | 7.93 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 141 | 55.46 | 22.62 | 13.62 | 4.70 | 13.22 | 5.80 | 8.51 | 0.75 |
| DIVERGENCE_CONTINUATION | kept | 143 | 69.07 | 23.04 | 13.87 | 6.19 | 12.50 | 5.89 | 8.76 | 1.29 |
| FAILED_AUCTION_RECLAIM | filtered | 88 | 48.11 | 20.27 | 14.64 | 6.68 | 14.10 | 6.23 | 6.43 | 1.62 |
| FAILED_AUCTION_RECLAIM | kept | 7 | 69.21 | 22.71 | 17.43 | 6.00 | 13.43 | 5.71 | 7.29 | 2.79 |
| FUNDING_EXTREME_SIGNAL | filtered | 10 | 47.43 | 25.00 | 8.00 | 4.20 | 13.20 | 6.90 | 6.73 | 3.40 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 70.25 | 21.00 | 19.00 | 3.00 | 9.00 | 9.50 | 6.00 | 4.00 |
| LIQUIDATION_REVERSAL | filtered | 1 | 50.30 | 25.00 | 8.00 | 12.00 | 8.00 | 5.00 | 3.30 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 55 | 47.32 | 24.02 | 15.82 | 6.44 | 12.58 | 6.52 | 5.18 | 1.96 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 77 | 71.89 | 21.86 | 15.82 | 7.05 | 13.09 | 5.27 | 8.11 | 0.96 |
| MEAN_REVERT | filtered | 73 | 54.92 | 22.70 | 15.37 | 8.26 | 12.75 | 5.00 | 5.63 | 0.00 |
| MEAN_REVERT | kept | 3 | 69.57 | 22.33 | 18.00 | 8.00 | 13.00 | 5.00 | 7.23 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 161 | 51.45 | 18.71 | 18.00 | 12.56 | 13.43 | 6.84 | 6.18 | 3.39 |
| MOVER_AVWAP_SCALP | kept | 258 | 79.54 | 18.79 | 18.13 | 13.09 | 13.64 | 6.52 | 8.30 | 4.24 |
| MOVER_TREND_PULLBACK | filtered | 1186 | 56.68 | 18.28 | 18.00 | 7.74 | 12.79 | 5.85 | 9.01 | 3.91 |
| MOVER_TREND_PULLBACK | kept | 3001 | 76.52 | 19.22 | 18.01 | 7.85 | 13.36 | 6.50 | 9.29 | 4.27 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 88.50 | 17.00 | 18.00 | 15.00 | 14.00 | 10.00 | 10.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 176 | 50.14 | 18.95 | 17.34 | 12.02 | 14.12 | 6.74 | 5.34 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 127 | 75.17 | 18.01 | 17.59 | 12.14 | 14.28 | 6.15 | 8.28 | 0.00 |
| SR_FLIP_RETEST | filtered | 10 | 55.12 | 22.60 | 8.00 | 7.80 | 16.10 | 6.40 | 7.59 | 2.35 |
| SR_FLIP_RETEST | kept | 19 | 69.68 | 23.74 | 16.95 | 10.42 | 11.79 | 5.00 | 5.67 | 3.00 |
| TREND_PULLBACK_EMA | filtered | 50 | 50.74 | 16.58 | 18.00 | 9.84 | 15.26 | 7.45 | 6.97 | 4.64 |
| TREND_PULLBACK_EMA | kept | 136 | 77.74 | 16.75 | 18.01 | 7.63 | 15.45 | 7.59 | 8.92 | 4.69 |
| VOLUME_SURGE_BREAKOUT | filtered | 3 | 52.23 | 17.00 | 15.33 | 12.00 | 15.00 | 5.00 | 7.03 | 3.83 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 141 | 55.46 | 0.00 | 0.00 | 0.38 | 0.00 | 0.70 | 0.00 | 0.00 | 0.00 | **1.08** |
| DIVERGENCE_CONTINUATION | kept | 143 | 69.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.45 | 0.00 | 0.00 | 0.00 | **0.45** |
| FAILED_AUCTION_RECLAIM | filtered | 88 | 48.11 | 0.00 | 0.00 | 1.15 | 0.00 | 1.36 | 0.00 | 0.00 | 0.00 | **2.51** |
| FAILED_AUCTION_RECLAIM | kept | 7 | 69.21 | 0.00 | 0.00 | 0.00 | 0.00 | 3.43 | 0.00 | 0.00 | 0.00 | **3.43** |
| FUNDING_EXTREME_SIGNAL | filtered | 10 | 47.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 70.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 1 | 50.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 55 | 47.32 | 0.00 | 0.00 | 0.29 | 0.00 | 0.39 | 0.00 | 0.00 | 0.00 | **0.68** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 77 | 71.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 73 | 54.92 | 0.00 | 0.00 | 0.00 | 0.00 | 3.95 | 0.00 | 0.00 | 0.00 | **3.95** |
| MEAN_REVERT | kept | 3 | 69.57 | 0.00 | 0.00 | 0.00 | 0.00 | 4.00 | 0.00 | 0.00 | 0.00 | **4.00** |
| MOVER_AVWAP_SCALP | filtered | 161 | 51.45 | 0.09 | 0.00 | 0.16 | 0.00 | 2.31 | 0.00 | 0.00 | 0.79 | **3.35** |
| MOVER_AVWAP_SCALP | kept | 258 | 79.54 | 0.17 | 0.00 | 0.14 | 0.00 | 0.45 | 0.00 | 0.00 | 0.09 | **0.85** |
| MOVER_TREND_PULLBACK | filtered | 1186 | 56.68 | 0.00 | 0.00 | 1.29 | 0.00 | 0.52 | 0.00 | 0.00 | 0.00 | **1.81** |
| MOVER_TREND_PULLBACK | kept | 3001 | 76.52 | 0.00 | 0.00 | 0.20 | 0.00 | 0.26 | 0.00 | 0.00 | 0.00 | **0.46** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 88.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 176 | 50.14 | 0.00 | 0.00 | 0.08 | 0.00 | 0.32 | 0.00 | 0.00 | 4.31 | **4.71** |
| QUIET_COMPRESSION_BREAK | kept | 127 | 75.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.24 | 0.00 | 0.00 | 0.00 | **0.24** |
| SR_FLIP_RETEST | filtered | 10 | 55.12 | 0.00 | 0.00 | 0.00 | 0.00 | 4.32 | 0.00 | 0.00 | 0.00 | **4.32** |
| SR_FLIP_RETEST | kept | 19 | 69.68 | 0.00 | 0.00 | 3.79 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.79** |
| TREND_PULLBACK_EMA | filtered | 50 | 50.74 | 0.00 | 0.00 | 3.04 | 0.00 | 4.90 | 0.00 | 0.00 | 0.00 | **7.94** |
| TREND_PULLBACK_EMA | kept | 136 | 77.74 | 0.00 | 0.00 | 1.06 | 0.00 | 0.09 | 0.00 | 0.00 | 0.00 | **1.15** |
| VOLUME_SURGE_BREAKOUT | filtered | 3 | 52.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.00 | **3.00** |

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
- Outcomes recorded: **169220 held of 686184 seen** across 21 strategies; 3806 cells past the sample floor; **2000 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 46853 | 719/46134/0 | 44% | -0.15 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING (-1.40R) |
| MOVER_AVWAP_SCALP | 22276 | 195/22081/0 | 43% | -0.22 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 12743 | 155/12588/0 | 47% | -0.08 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 12455 | 150/12305/0 | 37% | -0.29 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 10786 | 53/10733/0 | 40% | -0.25 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.38R) |
| LIQUIDITY_SWEEP_REVERSAL | 9354 | 108/9246/0 | 36% | -0.46 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| SHADOW_MEAN_REVERT | 7795 | 0/0/7795 | 42% | -0.12 | NY/RANGE/NORMAL/BTC_NEUTRAL (+0.55R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.12R) |
| SHADOW_RANGE_FADE | 7337 | 0/0/7337 | 36% | -0.12 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.44R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.13R) |
| QUIET_COMPRESSION_BREAK | 7268 | 413/6855/0 | 50% | -0.12 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_FUNDING_FADE | 6639 | 0/0/6639 | 35% | -0.40 | OVERLAP/MARKDOWN/COMPRESSED/BTC_RISING (-0.07R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 4925 | 17/4908/0 | 47% | -0.24 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+2.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 4888 | 60/4828/0 | 36% | -0.34 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| FUNDING_EXTREME_SIGNAL | 3737 | 2/3735/0 | 31% | -0.46 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3493 | 0/3493/0 | 31% | -0.35 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| RANGE_FADE | 2072 | 6/2066/0 | 38% | -0.29 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1555 | 0/0/1555 | 52% | -0.07 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 474 | 0/474/0 | 30% | -0.55 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 162 | 32/130/0 | 43% | -0.15 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 48 | 2/46/0 | 33% | -0.08 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.63R (n=26, NEGATIVE); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.63R (n=26, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 313 | 28% / -0.56R | 313 | 54% / -0.08R | +0.48 | **ATR** |
| LIQUIDATION_REVERSAL | 32 | 22% / -0.73R | 32 | 44% / -0.38R | +0.35 | **ATR** |
| TREND_PULLBACK_EMA | 978 | 39% / -0.34R | 978 | 51% / -0.07R | +0.27 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1465 | 43% / -0.37R | 1465 | 56% / -0.12R | +0.24 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 186 | 35% / -0.21R | 186 | 46% / -0.07R | +0.14 | **ATR** |
| MOVER_AVWAP_SCALP | 2237 | 43% / -0.19R | 2237 | 50% / -0.06R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 468 | 43% / -0.30R | 468 | 47% / -0.17R | +0.13 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1288 | 41% / -0.22R | 1288 | 43% / -0.12R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 8451 | 49% / -0.12R | 8451 | 54% / -0.02R | +0.10 | **ATR** |
| MA_CROSS_TREND_SHIFT | 49 | 41% / -0.17R | 49 | 45% / -0.07R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| RANGE_FADE | 110 | 37% / -0.17R | 110 | 45% / -0.08R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1464 | 48% / -0.11R | 1464 | 54% / -0.05R | +0.06 | **ATR** |
| MEAN_REVERT | 359 | 45% / -0.20R | 359 | 44% / -0.22R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1282 | 48% / -0.12R | 1282 | 48% / -0.12R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 12 | 58% / -0.09R | 12 | 58% / -0.10R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11352 | 28% | -0.22R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2237 | 48% | -0.05R | 232 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 118 | 47% | -0.07R | 66 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1676 | 39% / -0.15R | +0.85 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1291 | 33% / -0.24R | +0.83 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2759 | 34% / -0.22R | +0.62 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10335 | 36% / -0.17R | +0.37 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1688 | 37% / -0.11R | +0.17 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1245 | 37% / -0.13R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1083 | 32% / -0.24R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 269 | 31% / -0.35R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 409 | 33% / -0.11R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 304 | 46% / -0.12R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 81 | 43% / +0.01R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 430 | 33% / -0.31R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 78 | 29% / -0.39R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 39 | 46% / -0.19R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 19 | 42% / +0.65R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×349]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 338/6) (sustained 338 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 338/6) (sustained 338 cycles)
- **ALERT** `tuned_variants` — 383 non-stamps — atr_arm_uncomputable=383 (seen=9139 stamped=1318 skipped=7438) (streak 315/6) (sustained 315 cycles)
- **ALERT** `auto_dispatch` — 80 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=83) (streak 334/3) (sustained 334 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 54222988 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 31 arms current, none stalled; covering 2095/2095 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 5/6) | 5 |
| atr_trail_live_arms | ok | 64 arms current, none stalled; covering 1096/1096 signals (100%) | 0 |
| auto_dispatch | violating | 80 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=83) (streak 334/3) | 334 |
| binance_ip_weight | ok | peak 80/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 77927.90 | 0 |
| candle_coverage | ok | 80/80 symbols with ≥20 15m candles, 80/80 updated within 45m [fresh=80; 76 Tier-1 futures + 4 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1169 dup bars, 0 undedupable; ws 0 out-of-order, 215 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +13 / upstream +17 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1771/1790 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 2 of 130 open dark rows are not being advanced (worst: HANAUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 17/120) | 17 |
| dark_sar_arms | ok | no open arms; covering 1765/1784 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 19864757 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 338/6) | 338 |
| emission_controller | ok | last cycle 2s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×349]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 338/6) | 338 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=67, profile_reject=3. Held back in this window: session_quality=129, profile_reject=1. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 3/6) | 3 |
| firestore_read_budget | ok | 1,325 reads/day of 50,000 [engine 1,297, signing 28]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 1677 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +6 / upstream +288 | 0 |
| indicator_cache_key | ok | 136046 frozen value(s) avoided; 233004 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.34R over n=4828 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +51 / upstream +288 | 0 |
| mover_admission_metadata | ok | 942 symbols known, 235 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 4 held, 4 with scan counts, 4 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 8 locked / 8 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2111 rows held, 3249516 evicted (sampled: execution:trigger_not_confirmed 288/1146637, execution:overextended 288/1019726, setup_compat:regime_STRONG_TREND 288/550854) | 0 |
| price_action_lane | ok | 592055 evaluated, 1129 emitted; layer1 1129 stamped / 0 blind; cooldown=83010, delta_opposed=40654, no_footprint=228017, no_levels=41, no_opposing_target=1108, no_sweep=202095, rr_below_floor=36001 | 0 |
| promoted_pair_integrity | ok | 4/4 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.29R over n=2066 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +14 / upstream +288 | 0 |
| sar_alignment_crosscheck | ok | 908/23230 disagreed (3.9%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +288 | 0 |
| sar_hold_arm | ok | 1870 held arms settled, 131 unscored, 62 still walking (55 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 34/113 unfetchable (30%); top cause: gap or duplicate bar in the 15m window; symbols: COWUSDT, ESPORTSUSDT, LSKUSDT, STXUSDT | 0 |
| sar_live_arms | ok | 63 arms current, none stalled; covering 1095/1095 signals (100%) | 0 |
| sar_refresh_budget | ok | 7 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 7 resolved, 72 still mid-window | 0 |
| scan_cycle | ok | last 59.11s, worst 200.27s over 6822 lifetime cycles; lifetime 444 over 60s, 74 over 120s (plus 1/0 during boot warm-up, not counted); recent 2/0 warn/kill breaches in 20/20 cycles; heartbeat age 33.77s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 256468 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 6m ago | 0 |
| snapshot_writer | ok | last cycle 40s ago (1.73s to run, worst 148.63s), 1323 overrun(s) of 7244 cycles, TTL 900s; slowest signals=22.07s, data_intake=0.28s, pair_context=0.24s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +43 / upstream +288 | 0 |
| structural_snap | ok | 6000/6000 measured, 34 blind, 0 levels moved (refusals: redetect_cooldown=1262) | 0 |
| structural_veto_lane | ok | 2300 stamped; 0 with no readable level book, 12 with clear air ahead, 1566 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +288 / upstream +17 | 0 |
| tuned_variants | violating | 383 non-stamps — atr_arm_uncomputable=383 (seen=9139 stamped=1318 skipped=7438) (streak 315/6) | 315 |
| unlock_shorts | ok | 15 open, 46 scheduled, calendar 6.2h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 40 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1550263`
- `Path funnel` emissions: `36`
- `Regime distribution` emissions: `36`
- `QUIET_SCALP_BLOCK` events: `236`
- `confidence_gate` events: `5728`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **10**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 10 | 7644 | 33871 | 50996 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=232186] state[populated=232186] buckets[few=6, many=232168, some=12] sources[none] quality[none]
- funding_rate: presence[absent=36225, present=195961] state[empty=36225, populated=195961] buckets[few=195961, none=36225] sources[none] quality[none]
- liquidation_clusters: presence[absent=158968, present=73218] state[empty=158968, populated=73218] buckets[few=60664, none=158968, some=12554] sources[none] quality[none]
- oi_snapshot: presence[absent=36223, present=195963] state[empty=36223, populated=195963] buckets[few=453, many=192587, none=36223, some=2923] sources[none] quality[none]
- order_book: presence[absent=85486, present=146700] state[populated=146700, unavailable=85486] buckets[few=146700, none=85486] sources[book_ticker=146700, unavailable=85486] quality[none=85486, top_of_book_only=146700]
- orderblocks: presence[absent=232186] state[empty=232186] buckets[none=232186] sources[measured_dark=232161, not_implemented=25] quality[none]
- recent_ticks: presence[present=232186] state[populated=232186] buckets[many=232186] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.60496187210083` sec
- Median create→first breach: `5212.8422219753265` sec
- Median create→terminal: `5213.287806987762` sec
- Median first breach→terminal: `6.29425048828125e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.3}, "under_180s": {"count": 1, "pct": 2.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.3}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.3}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.9103660750429601 | 1.0751976543020991 | 0.856919057993623 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 1.4520484192934393 | 1.5716753022452516 | 0.9282423753320553 | 0 | 3 |
| MEAN_REVERT | 1 | 1 | 0.752525609325329 | 0.7126870067145713 | 1.0558991566219376 | 1 | 0 |
| MOVER_AVWAP_SCALP | 2 | 2 | 2.1499050630164867 | 2.2925795382121716 | 0.9398782591335693 | 0 | 1 |
| MOVER_TREND_PULLBACK | 29 | 29 | 3.0826108329461848 | 2.9829000000000065 | 1.027536944315395 | 15 | 13 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 1.4210524985611777 | 1.5839744809409526 | 0.9122757064420142 | 0 | 5 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -0.3785 | 20795.150448441505 | 20795.15050959587 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 66.7 | 33.3 | 66.7 | 0.0 | 0.4894 | 3649.942638874054 | 3649.94268989563 |
| MEAN_REVERT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.7525 | 14741.934503793716 | 14741.934534788132 |
| MOVER_AVWAP_SCALP | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.4171 | 9406.016850471497 | 9408.21124792099 |
| MOVER_TREND_PULLBACK | 29 | 29 | 27.6 | 37.9 | 27.6 | 0.0 | 0.1317 | 3987.5235180854797 | 3987.523556947708 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 50.0 | 50.0 | 50.0 | 0.0 | 0.2874 | 45608.94917547703 | 45611.753266096115 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 312 | 4 | 181 | 0.0 | 0.0 | None | None | 131 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1191 | 34 | 878 | 0.0 | 0.0 | None | None | 313 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `10`
- Gating Δ: `-5755`
- No-generation Δ: `-78776`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.4894, "current_avg_pnl": 0.4894, "current_win_rate": 66.7, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 66.7}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 1.8639, "current_avg_pnl": 0.4171, "current_win_rate": 50.0, "previous_avg_pnl": -1.4468, "previous_win_rate": 0.0, "win_rate_delta": 50.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.3085, "current_avg_pnl": 0.1317, "current_win_rate": 27.6, "previous_avg_pnl": 0.4402, "previous_win_rate": 37.5, "win_rate_delta": -9.9}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.2559, "current_avg_pnl": 0.2874, "current_win_rate": 50.0, "previous_avg_pnl": 0.0315, "previous_win_rate": 20.0, "win_rate_delta": 30.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -6, "geometry_changed_delta": 0, "geometry_preserved_delta": -220, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -6, "geometry_changed_delta": 0, "geometry_preserved_delta": -81, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2536.66, "median_terminal_delta_sec": -2536.66, "sl_rate_delta": -50.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **FAILED_AUCTION_RECLAIM**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
