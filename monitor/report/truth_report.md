# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `5365` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 79 | 79 | 79 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 20624 | 20624 | 19553 | 12 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 132256 | 132247 | 23 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 117855 | 117867 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 117512 | 113984 | 3852 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 117895 | 117572 | 366 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 121530 | 121098 | 464 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 113860 | 113868 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 117943 | 117968 | 6 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 117976 | 114580 | 4254 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 136581 | 139617 | 1129 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::MOVER_TREND_PULLBACK | 132273 | 125126 | 11415 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 121328 | 121336 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 117871 | 117861 | 28 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 117468 | 116888 | 621 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 118834 | 116553 | 3142 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 117246 | 117371 | 59 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 110029 | 107423 | 2731 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 110159 | 109742 | 477 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 132225 | 132200 | 54 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 113871 | 113883 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1805 | 1805 | 1698 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1959 | 1959 | 532 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15362 | 15362 | 15105 | 17 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 17 | 17 | 7 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 12387 | 12387 | 10636 | 7 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3038 | 3038 | 1142 | 42 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 39144 | 39144 | 25192 | 256 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 82 | 82 | 82 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 4121 | 4121 | 2269 | 30 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 9749 | 9749 | 8926 | 3 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 91 | 91 | 32 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2931 | 2931 | 2523 | 22 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 237 | 237 | 22 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=132247): breakout_not_found=61068, basic_filters_failed=50725, move_not_fresh=14466, breakout_stale=3755, retest_proximity_failed=1880, volume_spike_missing=226, move_exhausted=60, insufficient_candles=40, ema_alignment_reject=23, missing_fvg_or_orderblock=4
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=117867): cls_disabled_merged_into_lsr=117867
- **EVAL::DIVERGENCE_CONTINUATION** (total=113984): basic_filters_failed=44417, cvd_divergence_failed=34758, h1_trend_not_aligned=24348, ema_alignment_reject=7070, retest_proximity_failed=1608, regime_blocked=1317, missing_fvg_or_orderblock=465, cvd_insufficient=1
- **EVAL::FAILED_AUCTION_RECLAIM** (total=117572): auction_not_detected=66463, basic_filters_failed=42988, regime_blocked=4967, tail_too_small=1886, reclaim_hold_failed=1259, rsi_reject=9
- **EVAL::FUNDING_EXTREME** (total=121098): funding_not_extreme=66296, basic_filters_failed=46055, ema_alignment_reject=3402, missing_funding_rate=2897, rsi_reject=1215, cvd_divergence_failed=580, momentum_reject=530, missing_fvg_or_orderblock=119, insufficient_candles=4
- **EVAL::LIQUIDATION_REVERSAL** (total=113868): cascade_threshold_not_met=65400, basic_filters_failed=47074, cvd_divergence_failed=675, rsi_reject=625, missing_fvg_or_orderblock=65, insufficient_candles=21, volume_spike_missing=8
- **EVAL::MA_CROSS_TREND_SHIFT** (total=117968): no_ma_cross=72380, basic_filters_failed=44440, ma_cross_cooldown=673, ma_cross_htf_misaligned=475
- **EVAL::MEAN_REVERT** (total=114580): no_extension=85239, basic_filters_failed=29079, insufficient_candles=262
- **EVAL::MOVER_AVWAP_SCALP** (total=139617): basic_filters_failed=50343, no_mover_leg=42326, no_avwap_tag=35843, avwap_slope_against=5404, avwap_reclaim_no_volume=2766, no_avwap_reclaim=1554, insufficient_candles=952, anchor_too_recent=429
- **EVAL::MOVER_TREND_PULLBACK** (total=125126): mover_run_too_small=55890, basic_filters_failed=48778, no_reclaim=14729, insufficient_candles=3405, no_pullback_tag=2324
- **EVAL::OPENING_RANGE_BREAKOUT** (total=121336): feature_disabled=121336
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=117861): regime_blocked=81607, breakout_not_found=19592, basic_filters_failed=13215, adx_reject=3415, ema_alignment_reject=32
- **EVAL::QUIET_COMPRESSION_BREAK** (total=116888): regime_blocked=41163, basic_filters_failed=29761, compression_not_detected=27931, breakout_not_detected=15319, volume_confirmation_failed=1980, macd_reject=572, rsi_reject=119, missing_fvg_or_orderblock=43
- **EVAL::RANGE_FADE** (total=116553): no_range_edge=86747, basic_filters_failed=28296, insufficient_candles=1510
- **EVAL::SR_FLIP_RETEST** (total=117371): flip_close_not_confirmed=66618, basic_filters_failed=42928, regime_blocked=4949, retest_out_of_zone=1068, h1_break_not_confirmed=913, long_break_volume_thin=476, reclaim_hold_failed=210, long_acceptance_not_held=149, insufficient_candles=39, ema_alignment_reject=19, whipsaw_flip=1, wick_quality_failed=1
- **EVAL::STANDARD** (total=107423): momentum_reject=31444, adx_reject=26043, basic_filters_failed=22662, sweeps_not_detected=12286, macd_reject=7638, ema_alignment_reject=4486, htf_poi_unanchored=2548, rsi_reject=197, insufficient_candles=62, invalid_sl_geometry=57
- **EVAL::TREND_PULLBACK** (total=109742): h1_trend_not_aligned=35852, basic_filters_failed=24541, ema_alignment_reject=14019, h1_pullback_not_confirmed=10474, no_ema_reclaim_close=6610, ema_not_tested_prev=6457, body_conviction_fail=3428, regime_blocked=3289, rsi_reject=3144, prev_already_below_emas=571, prev_already_above_emas=403, no_prev_low_break=344, no_prev_high_break=240, momentum_flat=141, momentum_reject=79, insufficient_candles=62, missing_fvg_or_orderblock=45, ema21_not_tagged=43
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=132200): breakout_not_found=64003, basic_filters_failed=50725, move_not_fresh=9982, breakout_stale=5176, retest_proximity_failed=1948, volume_spike_missing=239, insufficient_candles=40, move_exhausted=31, ema_alignment_reject=27, missing_fvg_or_orderblock=21, rsi_reject=8
- **EVAL::WHALE_MOMENTUM** (total=113883): momentum_reject=87327, recent_ticks_insufficient=18524, basic_filters_failed=8032

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=7): execution:overextended=7
- **DIVERGENCE_CONTINUATION** (total=780): setup_compat:regime_VOLATILE_UNSUITABLE=759, setup_compat:regime_BREAKOUT_EXPANSION=21
- **FAILED_AUCTION_RECLAIM** (total=711): execution:overextended=378, setup_compat:regime_STRONG_TREND=224, setup_compat:regime_VOLATILE_UNSUITABLE=76, context_floor=33
- **FUNDING_EXTREME_SIGNAL** (total=1516): execution:trigger_not_confirmed=1451, context_floor=65
- **LIQUIDITY_SWEEP_REVERSAL** (total=4622): execution:trigger_not_confirmed=1774, setup_compat:regime_STRONG_TREND=1712, execution:overextended=1136
- **MA_CROSS_TREND_SHIFT** (total=15): setup_compat:regime_CLEAN_RANGE=6, execution:trigger_not_confirmed=4, setup_compat:regime_DIRTY_RANGE=2, setup_compat:regime_VOLATILE_UNSUITABLE=2, execution:overextended=1
- **MEAN_REVERT** (total=4625): setup_compat:regime_STRONG_TREND=2100, setup_compat:regime_WEAK_TREND=1905, execution:overextended=620
- **MOVER_AVWAP_SCALP** (total=1531): execution:overextended=1014, execution:trigger_not_confirmed=443, entry_quality=74
- **MOVER_TREND_PULLBACK** (total=21411): execution:overextended=10283, execution:trigger_not_confirmed=9259, entry_quality=1869
- **QUIET_COMPRESSION_BREAK** (total=1500): context_floor=1246, execution:trigger_not_confirmed=245, execution:overextended=9
- **RANGE_FADE** (total=5534): setup_compat:regime_STRONG_TREND=2157, setup_compat:regime_WEAK_TREND=2118, execution:overextended=579, setup_compat:regime_VOLATILE_UNSUITABLE=519, context_edge=116, setup_compat:regime_BREAKOUT_EXPANSION=38, entry_quality=7
- **TREND_PULLBACK_EMA** (total=2716): setup_compat:regime_CLEAN_RANGE=2008, setup_compat:regime_DIRTY_RANGE=464, setup_compat:regime_VOLATILE_UNSUITABLE=203, entry_quality=41
- **VOLUME_SURGE_BREAKOUT** (total=178): context_floor=92, execution:overextended=86

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 250519 | 31.0% |
| RANGING | 240488 | 29.8% |
| TRENDING_UP | 135004 | 16.7% |
| TRENDING_DOWN | 122559 | 15.2% |
| VOLATILE | 59409 | 7.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **152**
- Average confidence gap to threshold: **10.65** (samples=152) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: TRXUSDT=30, XRPUSDT=12, TAOUSDT=12, DOTUSDT=12, 1000PEPEUSDT=12, ZECUSDT=11, 1000SHIBUSDT=10, LINKUSDT=8, AVAXUSDT=7, BNBUSDT=7

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 32 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 4 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 324 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 18 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 118 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 14 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 46 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 119 |
| MEAN_REVERT | kept | min_confidence_pass | 28 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 533 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 17 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 626 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2834 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 9 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 5221 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 146 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 132 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 171 |
| RANGE_FADE | kept | min_confidence_pass | 4 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 34 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 12 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 201 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 43 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 25 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 36 | 56.45 | 65.00 | 8.55 | 21.18 | 19.21 | 18.40 | 1.00 | 12.53 |
| DIVERGENCE_CONTINUATION | kept | 324 | 69.20 | 65.00 | -4.20 | 20.20 | 19.68 | 18.53 | 2.84 | 0.75 |
| FAILED_AUCTION_RECLAIM | kept | 18 | 69.81 | 65.00 | -4.81 | 20.94 | 18.32 | 20.00 | 3.81 | 0.33 |
| FUNDING_EXTREME_SIGNAL | filtered | 118 | 51.03 | 63.00 | 11.97 | 20.75 | 14.26 | 16.84 | 3.67 | 4.86 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 53.79 | 65.00 | 11.21 | 20.56 | 20.00 | 19.77 | 2.47 | 13.69 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 46 | 70.47 | 65.00 | -5.47 | 20.76 | 19.05 | 18.10 | 1.28 | -0.26 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.90 | 65.00 | 14.10 | 21.20 | 20.00 | 15.80 | 0.00 | 21.60 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.00 | 65.00 | -1.00 | 21.10 | 18.90 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 119 | 59.18 | 63.07 | 3.89 | 19.80 | 14.56 | 18.17 | 0.00 | 4.29 |
| MEAN_REVERT | kept | 28 | 66.44 | 65.00 | -1.44 | 22.07 | 18.91 | 19.60 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 550 | 55.20 | 63.20 | 8.00 | 20.23 | 14.76 | 15.80 | 3.84 | 5.33 |
| MOVER_AVWAP_SCALP | kept | 626 | 77.31 | 65.00 | -12.31 | 20.70 | 16.47 | 15.80 | 4.13 | 0.33 |
| MOVER_TREND_PULLBACK | filtered | 2843 | 54.37 | 63.42 | 9.05 | 19.36 | 17.89 | 15.80 | 4.02 | 20.56 |
| MOVER_TREND_PULLBACK | kept | 5221 | 76.28 | 65.00 | -11.28 | 20.25 | 18.71 | 15.80 | 4.45 | 1.73 |
| QUIET_COMPRESSION_BREAK | filtered | 278 | 50.71 | 63.57 | 12.86 | 21.34 | 19.21 | 20.00 | 0.00 | 8.83 |
| QUIET_COMPRESSION_BREAK | kept | 171 | 74.13 | 65.00 | -9.13 | 20.27 | 18.97 | 20.00 | 0.00 | 0.05 |
| RANGE_FADE | kept | 4 | 68.58 | 65.00 | -3.58 | 20.50 | 15.18 | 19.18 | 0.00 | 0.00 |
| SR_FLIP_RETEST | kept | 34 | 69.98 | 65.00 | -4.98 | 20.17 | 20.00 | 19.72 | 1.28 | -0.15 |
| TREND_PULLBACK_EMA | filtered | 15 | 55.19 | 65.00 | 9.81 | 20.93 | 18.74 | 17.75 | 3.33 | 13.65 |
| TREND_PULLBACK_EMA | kept | 201 | 75.93 | 65.00 | -10.93 | 21.98 | 19.89 | 17.86 | 4.70 | -0.52 |
| VOLUME_SURGE_BREAKOUT | filtered | 43 | 54.07 | 65.00 | 10.93 | 19.28 | 16.76 | 20.00 | 3.63 | 4.95 |
| VOLUME_SURGE_BREAKOUT | kept | 25 | 70.60 | 65.00 | -5.60 | 20.82 | 18.05 | 20.00 | 4.56 | 6.96 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 36 | 56.45 | 21.67 | 12.44 | 5.58 | 13.19 | 6.12 | 8.97 | 1.00 |
| DIVERGENCE_CONTINUATION | kept | 324 | 69.20 | 21.32 | 15.01 | 4.58 | 13.81 | 4.55 | 8.82 | 2.84 |
| FAILED_AUCTION_RECLAIM | kept | 18 | 69.81 | 20.11 | 17.33 | 8.33 | 12.06 | 5.19 | 3.31 | 3.81 |
| FUNDING_EXTREME_SIGNAL | filtered | 118 | 51.03 | 24.39 | 9.32 | 6.33 | 12.86 | 7.58 | 4.83 | 3.67 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 53.79 | 17.94 | 14.00 | 12.00 | 12.88 | 2.94 | 5.25 | 2.47 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 46 | 70.47 | 23.39 | 14.91 | 4.96 | 13.78 | 5.34 | 6.81 | 1.28 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.90 | 17.00 | 14.00 | 9.00 | 14.00 | 8.50 | 10.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.00 | 25.00 | 14.00 | 3.00 | 11.00 | 5.00 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 119 | 59.18 | 22.58 | 18.00 | 5.42 | 12.00 | 7.12 | 4.15 | 0.00 |
| MEAN_REVERT | kept | 28 | 66.44 | 18.14 | 17.86 | 6.54 | 16.00 | 5.18 | 2.73 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 550 | 55.20 | 17.37 | 18.29 | 8.83 | 12.62 | 5.39 | 5.50 | 3.84 |
| MOVER_AVWAP_SCALP | kept | 626 | 77.31 | 18.80 | 18.04 | 8.44 | 14.03 | 5.73 | 8.85 | 4.13 |
| MOVER_TREND_PULLBACK | filtered | 2843 | 54.37 | 17.97 | 18.33 | 7.94 | 13.33 | 5.60 | 9.22 | 4.02 |
| MOVER_TREND_PULLBACK | kept | 5221 | 76.28 | 19.38 | 18.08 | 8.14 | 13.24 | 5.73 | 9.11 | 4.45 |
| QUIET_COMPRESSION_BREAK | filtered | 278 | 50.71 | 18.60 | 15.90 | 12.50 | 14.05 | 6.78 | 3.58 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 171 | 74.13 | 19.72 | 16.83 | 10.02 | 14.18 | 6.60 | 6.98 | 0.00 |
| RANGE_FADE | kept | 4 | 68.58 | 24.50 | 15.00 | 6.75 | 12.00 | 5.00 | 5.33 | 0.00 |
| SR_FLIP_RETEST | kept | 34 | 69.98 | 17.71 | 18.00 | 8.38 | 13.68 | 5.10 | 5.86 | 1.28 |
| TREND_PULLBACK_EMA | filtered | 15 | 55.19 | 16.00 | 18.00 | 10.80 | 17.00 | 9.20 | 5.51 | 3.33 |
| TREND_PULLBACK_EMA | kept | 201 | 75.93 | 15.39 | 18.00 | 7.51 | 14.11 | 7.34 | 9.05 | 4.70 |
| VOLUME_SURGE_BREAKOUT | filtered | 43 | 54.07 | 10.72 | 15.67 | 12.00 | 14.00 | 5.77 | 5.95 | 3.63 |
| VOLUME_SURGE_BREAKOUT | kept | 25 | 70.60 | 17.32 | 18.00 | 12.00 | 10.68 | 5.00 | 10.00 | 4.56 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 36 | 56.45 | 0.00 | 0.00 | 2.13 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | **4.53** |
| DIVERGENCE_CONTINUATION | kept | 324 | 69.20 | 0.00 | 0.00 | 0.16 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.18** |
| FAILED_AUCTION_RECLAIM | kept | 18 | 69.81 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 118 | 51.03 | 0.00 | 0.00 | 1.46 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.46** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 53.79 | 0.00 | 0.00 | 0.00 | 0.00 | 13.69 | 0.00 | 0.00 | 0.00 | **13.69** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 46 | 70.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.90 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 119 | 59.18 | 0.00 | 0.00 | 2.42 | 0.00 | 0.00 | 0.00 | 0.00 | 1.87 | **4.29** |
| MEAN_REVERT | kept | 28 | 66.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 550 | 55.20 | 0.22 | 0.00 | 1.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.75 | **2.30** |
| MOVER_AVWAP_SCALP | kept | 626 | 77.31 | 0.14 | 0.00 | 0.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.02 | **0.43** |
| MOVER_TREND_PULLBACK | filtered | 2843 | 54.37 | 0.05 | 0.00 | 4.21 | 0.00 | 0.33 | 0.00 | 0.00 | 0.02 | **4.61** |
| MOVER_TREND_PULLBACK | kept | 5221 | 76.28 | 0.00 | 0.00 | 0.69 | 0.00 | 0.19 | 0.00 | 0.00 | 0.00 | **0.88** |
| QUIET_COMPRESSION_BREAK | filtered | 278 | 50.71 | 0.10 | 0.00 | 0.00 | 0.00 | 0.29 | 0.00 | 0.00 | 5.79 | **6.18** |
| QUIET_COMPRESSION_BREAK | kept | 171 | 74.13 | 0.09 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.04 | **0.18** |
| RANGE_FADE | kept | 4 | 68.58 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 34 | 69.98 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 15 | 55.19 | 0.00 | 0.00 | 0.53 | 0.00 | 13.12 | 0.00 | 0.00 | 0.00 | **13.65** |
| TREND_PULLBACK_EMA | kept | 201 | 75.93 | 0.00 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.18** |
| VOLUME_SURGE_BREAKOUT | filtered | 43 | 54.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.95 | **1.95** |
| VOLUME_SURGE_BREAKOUT | kept | 25 | 70.60 | 0.00 | 0.00 | 0.00 | 0.00 | 3.96 | 0.00 | 0.00 | 0.00 | **3.96** |

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
- Outcomes recorded: **121238 held of 153239 seen** across 21 strategies; 2725 cells past the sample floor; **567 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 28660 | 156/28504/0 | 53% | +0.02 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_RISING (+1.22R) | OVERLAP/MARKUP/NORMAL/BTC_RISING (-1.12R) |
| FAILED_AUCTION_RECLAIM | 16975 | 24/16951/0 | 51% | +0.00 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16541 | 1/16540/0 | 48% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 11029 | 4/11025/0 | 45% | -0.10 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.43R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 8813 | 0/8813/0 | 50% | -0.06 | NY/QUIET/EXPANDED/BTC_RISING/ALTCOIN (+1.37R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 6410 | 27/6383/0 | 31% | -0.38 | OVERLAP/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/ALTCOIN (+1.01R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| SHADOW_MEAN_REVERT | 4393 | 0/0/4393 | 42% | -0.06 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.00R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-0.97R) |
| LIQUIDITY_SWEEP_REVERSAL | 4314 | 9/4305/0 | 46% | -0.21 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.78R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_RANGE_FADE | 4009 | 0/0/4009 | 41% | +0.17 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.37R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.02R) |
| TREND_PULLBACK_EMA | 3996 | 2/3994/0 | 50% | -0.21 | LONDON/QUIET/NORMAL/BTC_NEUTRAL (+0.74R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.19R) |
| MEAN_REVERT | 3823 | 0/3823/0 | 75% | +0.49 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.35R) |
| SHADOW_FUNDING_FADE | 3568 | 0/0/3568 | 40% | -0.31 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.34R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-0.90R) |
| RANGE_FADE | 3115 | 0/3115/0 | 29% | -0.46 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.87R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-1.34R) |
| VOLUME_SURGE_BREAKOUT | 1989 | 13/1976/0 | 43% | +0.03 | LONDON/MARKUP/COMPRESSED/BTC_NEUTRAL (+1.87R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 1518 | 2/1516/0 | 34% | -0.36 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (-1.61R) |
| WHALE_MOMENTUM | 1226 | 0/1226/0 | 47% | -0.25 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-0.76R) |
| SHADOW_CASCADE_REVERSAL | 403 | 0/0/403 | 45% | -0.20 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.01R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.81R) |
| BREAKDOWN_SHORT | 305 | 7/298/0 | 58% | +0.32 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| POST_DISPLACEMENT_CONTINUATION | 67 | 0/67/0 | 90% | +0.75 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| LIQUIDATION_REVERSAL | 66 | 0/66/0 | 64% | -0.48 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) |
| MA_CROSS_TREND_SHIFT | 18 | 1/17/0 | 28% | -0.46 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.87R (n=27, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` +1.87R (n=50, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP` -1.61R (n=20, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 62 | 37% / -0.32R | 62 | 52% / -0.12R | +0.20 | **ATR** |
| TREND_PULLBACK_EMA | 123 | 44% / -0.26R | 123 | 48% / -0.12R | +0.14 | **ATR** |
| SR_FLIP_RETEST | 2760 | 46% / -0.20R | 2760 | 49% / -0.10R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 371 | 39% / -0.21R | 371 | 42% / -0.12R | +0.09 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 66 | 42% / +0.04R | 66 | 48% / -0.04R | -0.08 | **FIXED** |
| LIQUIDITY_SWEEP_REVERSAL | 629 | 50% / -0.18R | 629 | 54% / -0.12R | +0.06 | **ATR** |
| DIVERGENCE_CONTINUATION | 756 | 47% / -0.11R | 756 | 52% / -0.05R | +0.06 | **ATR** |
| MEAN_REVERT | 351 | 54% / +0.02R | 351 | 51% / +0.07R | +0.05 | **ATR** |
| RANGE_FADE | 206 | 16% / -0.72R | 206 | 18% / -0.67R | +0.05 | **ATR** |
| MOVER_TREND_PULLBACK | 3368 | 52% / -0.05R | 3368 | 55% / -0.00R | +0.04 | **ATR** |
| WHALE_MOMENTUM | 87 | 49% / -0.25R | 87 | 48% / -0.28R | -0.03 | **FIXED** |
| BREAKDOWN_SHORT | 16 | 25% / -0.32R | 16 | 25% / -0.30R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1288 | 45% / -0.13R | 1288 | 45% / -0.15R | -0.01 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 2238 | 47% / -0.10R | 2238 | 47% / -0.10R | -0.00 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 9 | 33% / -0.27R | 9 | 33% / -0.27R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 71% / +0.23R | 7 | 71% / +0.04R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 5 | 40% / -0.81R | 5 | 40% / -0.40R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 4305 | 31% | -0.15R | 269 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 361 | 40% | -0.13R | 113 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 23 | 57% | +0.07R | 16 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1212 | 28% / -1.71R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 9 | 11% / -0.97R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 3134 | 37% / -0.29R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 935 | 33% / -0.58R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 55 | 24% / -0.93R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 562 | 30% / -1.95R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 694 | 35% / -0.10R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 257 | 42% / -1.41R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 66 | 29% / -1.68R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 122 | 27% / -1.05R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 312 | 31% / -0.15R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 10 | 20% / -0.43R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 87 | 37% / -0.32R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 45 | 44% / -0.12R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 4 | 0% / -1.16R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 5 | 20% / -1.42R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 19 | 42% / -0.37R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 42 · alerting: **6** · boot grace active: False
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 13/6) (sustained 13 cycles)
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 5 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 85/6) (sustained 85 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 680x (gate reads 0x, withheld 0x — refusal dark); last DODOXUSDT age=8911.5s (streak 19/6) (sustained 19 cycles)
- **ALERT** `edge_reconciliation` — FAILED_AUCTION_RECLAIM realized−counterfactual=+0.39R (bound 0.3) (streak 85/6) (sustained 85 cycles)
- **ALERT** `mean_revert_emission` — 2343 detections since last emission (emitted_total=3) — and the POST-SCORING blocked candidates measure +0.49R over n=3823, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 20/6) (sustained 20 cycles)
- **ALERT** `tuned_variants` — 84 non-stamps — atr_arm_uncomputable=84 (seen=2948 stamped=203 skipped=2661) (streak 85/6) (sustained 85 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 9413467 accepted, 0 rejected | 0 |
| auto_dispatch | ok | attempts=0 fanouts=4 (gaps: skip 4, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 64471.40 | 0 |
| candle_coverage | ok | 91/93 symbols with ≥20 15m candles, 85/93 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 292 dup bars, 1 undedupable; ws 0 out-of-order, 111 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 5 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 85/6) | 85 |
| context_emission_policy | ok | output +48 / upstream +54 | 0 |
| dark_resolution | ok | 15 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open dark arms | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 2260611 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | FAILED_AUCTION_RECLAIM realized−counterfactual=+0.39R (bound 0.3) (streak 85/6) | 85 |
| emission_controller | ok | last cycle 0s ago; live_overrides=24 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=13 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4003 stamps (MEAN_REVERT=1139, MOVER_AVWAP_SCALP=307, MOVER_TREND_PULLBACK=2100, RANGE_FADE=327, TREND_PULLBACK_EMA=130), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 13/6) | 13 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +6 / upstream +347 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 2343 detections since last emission (emitted_total=3) — and the POST-SCORING blocked candidates measure +0.49R over n=3823, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 20/6) | 20 |
| mean_revert_path | ok | output +69 / upstream +347 | 0 |
| mover_admission_metadata | ok | 852 symbols known, 151 marked TRADIFI_PERPETUAL | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 144490 evicted (sampled: execution:trigger_not_confirmed 400/49815, execution:overextended 400/44437, setup_compat:regime_STRONG_TREND 400/22689) | 0 |
| price_action_lane | ok | 742 evaluated, 19 emitted; delta_opposed=84, no_footprint=234, no_opposing_target=2, no_sweep=349, rr_below_floor=54 | 0 |
| promoted_pair_integrity | ok | 12/12 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.46R over n=3115 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +101 / upstream +347 | 0 |
| sar_alignment_crosscheck | ok | 218/5940 disagreed (3.7%) | 0 |
| sar_exit_shadow | ok | output +8 / upstream +347 | 0 |
| sar_ledger_candles | ok | 18/75 unfetchable (24%); top cause: gap or duplicate bar in the 15m window; symbols: BIOUSDT, ESPORTSUSDT, HFTUSDT, INJUSDT, TAKEUSDT +1 more | 0 |
| sar_live_arms | ok | 5 arms current, none stalled | 0 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 4 resolved, 53 still mid-window | 0 |
| setup_tf_resolver | ok | 82516 resolutions, 48820 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 4m ago | 0 |
| stale_tf_scoring | violating | scored on stale TF 680x (gate reads 0x, withheld 0x — refusal dark); last DODOXUSDT age=8911.5s (streak 19/6) | 19 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +22 / upstream +347 | 0 |
| structural_snap | ok | 164/164 measured, 0 blind, 0 levels moved (refusals: redetect_cooldown=731) | 0 |
| structural_veto_lane | ok | 895 stamped; 0 with no readable level book, 19 with clear air ahead, 609 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +347 / upstream +54 | 0 |
| tuned_variants | violating | 84 non-stamps — atr_arm_uncomputable=84 (seen=2948 stamped=203 skipped=2661) (streak 85/6) | 85 |

Fail-open exception counters (nonzero sites):
- `feature_liveness.probe.footprint_bars`: 1 — last: RuntimeError: deque mutated during iteration

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3735014`
- `Path funnel` emissions: `102`
- `Regime distribution` emissions: `102`
- `QUIET_SCALP_BLOCK` events: `152`
- `confidence_gate` events: `10719`
- `free_channel_post` events: `21`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **31**
- Total REST-fallback activations: **6**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 8 | 2165 | 4472 | 4522 | 0 |
| futures_aggtrade | 4 | 1850 | 3974 | 41168 | 0 |
| futures_depth | 17 | 3311 | 5880 | 6487 | 0 |
| futures_liq | 1 | 4389 | 4389 | 4389 | 0 |
| futures_mover | 1 | 5183 | 5183 | 5183 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 6 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **21**

| Source | Count |
|---|---:|
| regime_shift | 14 |
| signal_close | 7 |

- By severity: HIGH=21

## Dependency readiness
- cvd: presence[absent=1, present=628692] state[empty=1, populated=628692] buckets[few=15, many=627434, none=1, some=1243] sources[none] quality[none]
- funding_rate: presence[absent=50449, present=578244] state[empty=50449, populated=578244] buckets[few=578244, none=50449] sources[none] quality[none]
- liquidation_clusters: presence[absent=349887, present=278806] state[empty=349887, populated=278806] buckets[few=214903, none=349887, some=63903] sources[none] quality[none]
- oi_snapshot: presence[absent=41416, present=587277] state[empty=41416, populated=587277] buckets[few=96, many=586555, none=41416, some=626] sources[none] quality[none]
- order_book: presence[absent=162110, present=466583] state[populated=466583, unavailable=162110] buckets[few=466583, none=162110] sources[book_ticker=466583, unavailable=162110] quality[none=162110, top_of_book_only=466583]
- orderblocks: presence[absent=628693] state[empty=628693] buckets[none=628693] sources[measured_dark=420118, not_implemented=208575] quality[none]
- recent_ticks: presence[absent=7849, present=620844] state[empty=7849, populated=620844] buckets[many=620844, none=7849] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.1148715019226074` sec
- Median create→first breach: `1134.7928229570389` sec
- Median create→terminal: `1141.5800030231476` sec
- Median first breach→terminal: `2.235013008117676` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 16.7}, "under_180s": {"count": 1, "pct": 16.7}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 6 | 6 | 3.9676884855075336 | 3.0 | 1.322562828502511 | 4 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 6 | 6 | 0.0 | 50.0 | 0.0 | 0.0 | -0.9388 | 1134.7928229570389 | 1141.5800030231476 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 91 | 2 | 32 | 0.0 | 0.0 | None | None | 59 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2931 | 22 | 2523 | 0.0 | 0.0 | None | None | 408 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-55`
- Gating Δ: `-15593`
- No-generation Δ: `-335066`
- Fast failures Δ: `-1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.1946, "current_avg_pnl": -0.9388, "current_win_rate": 0.0, "previous_avg_pnl": 0.2558, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 41, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": -4, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
