# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: MOVER_AVWAP_SCALP, DIVERGENCE_CONTINUATION
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `507` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 79 | 79 | 79 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 8263 | 8263 | 7219 | 17 | active-healthy (none) |
| EVAL::BREAKDOWN_SHORT | 55016 | 55033 | 25 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 52786 | 52786 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 52105 | 50586 | 2175 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 52823 | 52209 | 730 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 53089 | 52838 | 304 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 45379 | 45402 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 52953 | 53014 | 6 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 53029 | 51020 | 3197 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 58463 | 62491 | 506 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 55062 | 51338 | 7043 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 52716 | 52716 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 52792 | 52818 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 52041 | 51882 | 209 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 54227 | 52980 | 1833 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 51614 | 51846 | 113 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 43878 | 41453 | 2783 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 44250 | 43968 | 405 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 54958 | 55007 | 2 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 45412 | 45451 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2235 | 2235 | 2159 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1054 | 1054 | 314 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 8 | 8 | 2 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15356 | 15356 | 15129 | 8 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 13 | 13 | 9 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8377 | 8377 | 6775 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1110 | 1110 | 293 | 36 | active-healthy (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 18178 | 18178 | 7488 | 365 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 11 | 11 | 11 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1039 | 1039 | 711 | 52 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4272 | 4272 | 3856 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 358 | 358 | 230 | 8 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1763 | 1763 | 1428 | 46 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 17 | 17 | 16 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=55033): breakout_not_found=27204, basic_filters_failed=14169, move_not_fresh=9337, breakout_stale=3610, retest_proximity_failed=538, volume_spike_missing=159, move_exhausted=12, missing_fvg_or_orderblock=4
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=52786): cls_disabled_merged_into_lsr=52786
- **EVAL::DIVERGENCE_CONTINUATION** (total=50586): cvd_divergence_failed=21623, h1_trend_not_aligned=12854, basic_filters_failed=12042, ema_alignment_reject=3300, retest_proximity_failed=474, missing_fvg_or_orderblock=293
- **EVAL::FAILED_AUCTION_RECLAIM** (total=52209): auction_not_detected=34742, basic_filters_failed=11333, regime_blocked=2267, reclaim_hold_failed=2065, tail_too_small=1792, rsi_reject=10
- **EVAL::FUNDING_EXTREME** (total=52838): funding_not_extreme=35703, basic_filters_failed=11596, ema_alignment_reject=2420, missing_funding_rate=1617, rsi_reject=987, cvd_divergence_failed=291, momentum_reject=193, missing_fvg_or_orderblock=31
- **EVAL::LIQUIDATION_REVERSAL** (total=45402): cascade_threshold_not_met=33013, basic_filters_failed=12007, cvd_divergence_failed=201, rsi_reject=164, missing_fvg_or_orderblock=13, volume_spike_missing=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=53014): no_ma_cross=39852, basic_filters_failed=12066, ma_cross_cooldown=847, ma_cross_htf_misaligned=249
- **EVAL::MEAN_REVERT** (total=51020): no_extension=41966, basic_filters_failed=9054
- **EVAL::MOVER_AVWAP_SCALP** (total=62491): no_mover_leg=21825, no_avwap_tag=20389, basic_filters_failed=14434, avwap_slope_against=3676, avwap_reclaim_no_volume=1199, no_avwap_reclaim=891, anchor_too_recent=77
- **EVAL::MOVER_TREND_PULLBACK** (total=51338): mover_run_too_small=27364, basic_filters_failed=14309, no_reclaim=8697, no_pullback_tag=968
- **EVAL::OPENING_RANGE_BREAKOUT** (total=52716): feature_disabled=52716
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=52818): regime_blocked=38394, breakout_not_found=9967, basic_filters_failed=2956, adx_reject=1455, ema_alignment_reject=46
- **EVAL::QUIET_COMPRESSION_BREAK** (total=51882): compression_not_detected=21705, regime_blocked=16546, basic_filters_failed=8363, breakout_not_detected=4633, volume_confirmation_failed=568, rsi_reject=56, missing_fvg_or_orderblock=11
- **EVAL::RANGE_FADE** (total=52980): no_range_edge=43921, basic_filters_failed=9059
- **EVAL::SR_FLIP_RETEST** (total=51846): flip_close_not_confirmed=33905, basic_filters_failed=11298, regime_blocked=2246, long_break_volume_thin=1426, retest_out_of_zone=1264, h1_break_not_confirmed=1061, reclaim_hold_failed=358, ema_alignment_reject=119, wick_quality_failed=69, long_acceptance_not_held=59, whipsaw_flip=40, missing_fvg_or_orderblock=1
- **EVAL::STANDARD** (total=41453): momentum_reject=12821, adx_reject=9195, basic_filters_failed=6715, macd_reject=4583, sweeps_not_detected=4432, ema_alignment_reject=2503, htf_poi_unanchored=1118, invalid_sl_geometry=56, rsi_reject=30
- **EVAL::TREND_PULLBACK** (total=43968): h1_trend_not_aligned=13863, basic_filters_failed=6455, h1_pullback_not_confirmed=6174, ema_alignment_reject=6048, no_ema_reclaim_close=3286, ema_not_tested_prev=3192, body_conviction_fail=2033, rsi_reject=1596, prev_already_below_emas=602, no_prev_low_break=333, momentum_flat=126, prev_already_above_emas=90, no_prev_high_break=65, missing_fvg_or_orderblock=59, ema21_not_tagged=37, momentum_reject=9
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=55007): breakout_not_found=33629, basic_filters_failed=14163, move_not_fresh=4687, breakout_stale=1682, retest_proximity_failed=747, volume_spike_missing=87, missing_fvg_or_orderblock=9, move_exhausted=3
- **EVAL::WHALE_MOMENTUM** (total=45451): momentum_reject=35279, recent_ticks_insufficient=6309, basic_filters_failed=3863

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=133): setup_compat:regime_VOLATILE_UNSUITABLE=132, setup_compat:regime_BREAKOUT_EXPANSION=1
- **FAILED_AUCTION_RECLAIM** (total=427): execution:overextended=273, setup_compat:regime_STRONG_TREND=152, setup_compat:regime_VOLATILE_UNSUITABLE=2
- **FUNDING_EXTREME_SIGNAL** (total=909): execution:trigger_not_confirmed=878, context_floor=31
- **LIQUIDATION_REVERSAL** (total=8): execution:trigger_not_confirmed=8
- **LIQUIDITY_SWEEP_REVERSAL** (total=3272): execution:trigger_not_confirmed=1681, execution:overextended=933, setup_compat:regime_STRONG_TREND=658
- **MA_CROSS_TREND_SHIFT** (total=15): setup_compat:regime_DIRTY_RANGE=6, execution:trigger_not_confirmed=6, setup_compat:regime_VOLATILE_UNSUITABLE=1, execution:overextended=1, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=2576): setup_compat:regime_STRONG_TREND=1355, setup_compat:regime_WEAK_TREND=1011, execution:overextended=210
- **MOVER_AVWAP_SCALP** (total=796): execution:overextended=444, execution:trigger_not_confirmed=181, entry_quality=171
- **MOVER_TREND_PULLBACK** (total=8303): execution:trigger_not_confirmed=4101, execution:overextended=2616, entry_quality=1586
- **QUIET_COMPRESSION_BREAK** (total=49): execution:trigger_not_confirmed=49
- **RANGE_FADE** (total=1471): setup_compat:regime_STRONG_TREND=747, setup_compat:regime_WEAK_TREND=430, setup_compat:regime_VOLATILE_UNSUITABLE=181, execution:overextended=103, context_edge=10
- **TREND_PULLBACK_EMA** (total=1613): setup_compat:regime_CLEAN_RANGE=1177, setup_compat:regime_DIRTY_RANGE=293, entry_quality=110, setup_compat:regime_VOLATILE_UNSUITABLE=33
- **VOLUME_SURGE_BREAKOUT** (total=1): execution:overextended=1

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 153962 | 48.9% |
| QUIET | 76826 | 24.4% |
| TRENDING_DOWN | 40793 | 12.9% |
| TRENDING_UP | 27274 | 8.7% |
| VOLATILE | 16245 | 5.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **171**
- Average confidence gap to threshold: **15.43** (samples=171) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: AVAXUSDT=49, TAOUSDT=23, XMRUSDT=10, HYPEUSDT=8, ERAUSDT=8, ETHUSDT=7, STRKUSDT=7, SOLUSDT=6, ONDOUSDT=6, LTCUSDT=6

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 89 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 5 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 158 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 28 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 13 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 47 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 73 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 7 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 14 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 58 |
| MEAN_REVERT | filtered | min_confidence | 15 |
| MEAN_REVERT | kept | min_confidence_pass | 39 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 136 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 201 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1974 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 17 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3172 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 54 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 48 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 161 |
| SR_FLIP_RETEST | filtered | min_confidence | 10 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 34 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 29 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 8 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 125 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 10 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 94 | 54.12 | 64.91 | 10.79 | 19.88 | 19.36 | 17.64 | 1.43 | 13.54 |
| DIVERGENCE_CONTINUATION | kept | 158 | 70.94 | 65.00 | -5.94 | 20.51 | 19.96 | 18.03 | 1.97 | -1.77 |
| FAILED_AUCTION_RECLAIM | filtered | 41 | 46.38 | 63.54 | 17.16 | 21.88 | 19.33 | 20.00 | 2.79 | 6.52 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 66.85 | 65.00 | -1.85 | 20.95 | 19.30 | 20.00 | 3.00 | 4.05 |
| FUNDING_EXTREME_SIGNAL | filtered | 47 | 48.27 | 63.49 | 15.22 | 20.25 | 17.76 | 17.00 | 2.09 | 7.54 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 64.30 | 65.00 | 0.70 | 21.20 | 14.00 | 17.00 | 7.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 80 | 50.86 | 64.10 | 13.24 | 20.30 | 19.77 | 18.05 | 1.75 | 9.01 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 14 | 70.08 | 65.00 | -5.08 | 20.80 | 19.31 | 18.04 | 3.29 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 75.25 | 65.00 | -10.25 | 21.00 | 18.45 | 15.80 | 0.00 | 6.00 |
| MEAN_REVERT | filtered | 73 | 48.45 | 65.00 | 16.55 | 21.37 | 19.33 | 15.23 | 0.00 | 9.03 |
| MEAN_REVERT | kept | 39 | 68.25 | 65.00 | -3.25 | 20.49 | 18.33 | 13.79 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 136 | 58.10 | 64.57 | 6.47 | 20.26 | 15.88 | 15.80 | 3.69 | 15.46 |
| MOVER_AVWAP_SCALP | kept | 201 | 79.51 | 65.00 | -14.51 | 20.42 | 16.23 | 15.80 | 4.17 | 3.57 |
| MOVER_TREND_PULLBACK | filtered | 1991 | 54.73 | 63.79 | 9.06 | 19.65 | 18.55 | 15.80 | 3.82 | 18.64 |
| MOVER_TREND_PULLBACK | kept | 3172 | 75.86 | 65.00 | -10.86 | 20.21 | 18.59 | 15.80 | 3.94 | 1.18 |
| QUIET_COMPRESSION_BREAK | filtered | 102 | 44.93 | 64.76 | 19.83 | 20.79 | 19.32 | 20.00 | 0.00 | 15.17 |
| QUIET_COMPRESSION_BREAK | kept | 161 | 73.32 | 65.00 | -8.32 | 20.88 | 19.17 | 20.00 | 0.00 | -0.40 |
| SR_FLIP_RETEST | filtered | 10 | 48.90 | 60.00 | 11.10 | 23.27 | 20.00 | 17.00 | 1.00 | 17.10 |
| SR_FLIP_RETEST | kept | 34 | 71.44 | 65.00 | -6.44 | 21.53 | 20.00 | 16.39 | 1.99 | 0.59 |
| TREND_PULLBACK_EMA | filtered | 37 | 57.71 | 65.00 | 7.29 | 20.63 | 19.64 | 17.87 | 4.18 | 17.80 |
| TREND_PULLBACK_EMA | kept | 125 | 78.11 | 65.00 | -13.11 | 20.71 | 19.86 | 17.47 | 4.76 | 0.59 |
| VOLUME_SURGE_BREAKOUT | filtered | 10 | 53.70 | 61.00 | 7.30 | 20.94 | 17.60 | 20.00 | 3.50 | 3.60 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 62.00 | 65.00 | 3.00 | 16.60 | 15.20 | 20.00 | 4.00 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 94 | 54.12 | 20.91 | 12.04 | 6.19 | 12.94 | 5.89 | 8.26 | 1.43 |
| DIVERGENCE_CONTINUATION | kept | 158 | 70.94 | 22.67 | 14.20 | 5.62 | 13.23 | 5.53 | 8.29 | 1.97 |
| FAILED_AUCTION_RECLAIM | filtered | 41 | 46.38 | 20.12 | 15.27 | 7.02 | 11.66 | 6.56 | 4.51 | 2.79 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 66.85 | 21.00 | 18.00 | 9.00 | 13.00 | 8.25 | 6.20 | 3.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 47 | 48.27 | 24.83 | 10.21 | 7.98 | 14.09 | 7.26 | 3.08 | 2.09 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 64.30 | 17.00 | 18.00 | 9.00 | 9.00 | 10.00 | 9.30 | 7.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 80 | 50.86 | 23.07 | 16.30 | 6.45 | 11.88 | 5.61 | 6.63 | 1.75 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 14 | 70.08 | 21.57 | 14.29 | 5.36 | 12.43 | 6.75 | 6.40 | 3.29 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 75.25 | 21.00 | 14.00 | 12.00 | 15.50 | 8.75 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 73 | 48.45 | 21.16 | 18.00 | 10.93 | 13.00 | 5.00 | 4.39 | 0.00 |
| MEAN_REVERT | kept | 39 | 68.25 | 17.00 | 18.00 | 9.00 | 13.00 | 5.00 | 6.25 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 136 | 58.10 | 17.60 | 18.21 | 12.93 | 14.00 | 8.19 | 7.43 | 3.69 |
| MOVER_AVWAP_SCALP | kept | 201 | 79.51 | 19.81 | 18.04 | 12.54 | 13.70 | 7.02 | 8.95 | 4.17 |
| MOVER_TREND_PULLBACK | filtered | 1991 | 54.73 | 18.10 | 18.07 | 7.96 | 12.33 | 5.85 | 9.02 | 3.82 |
| MOVER_TREND_PULLBACK | kept | 3172 | 75.86 | 19.30 | 18.04 | 7.85 | 12.70 | 6.37 | 9.01 | 3.94 |
| QUIET_COMPRESSION_BREAK | filtered | 102 | 44.93 | 19.43 | 15.88 | 10.94 | 14.18 | 7.26 | 4.16 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 161 | 73.32 | 17.54 | 16.01 | 12.47 | 14.04 | 7.22 | 7.22 | 0.00 |
| SR_FLIP_RETEST | filtered | 10 | 48.90 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 8.00 | 1.00 |
| SR_FLIP_RETEST | kept | 34 | 71.44 | 21.94 | 17.41 | 5.65 | 13.47 | 5.10 | 6.48 | 1.99 |
| TREND_PULLBACK_EMA | filtered | 37 | 57.71 | 12.95 | 18.00 | 8.23 | 15.62 | 7.00 | 9.54 | 4.18 |
| TREND_PULLBACK_EMA | kept | 125 | 78.11 | 18.70 | 18.00 | 7.63 | 14.75 | 7.20 | 9.29 | 4.76 |
| VOLUME_SURGE_BREAKOUT | filtered | 10 | 53.70 | 17.00 | 18.00 | 15.00 | 14.00 | 2.50 | 2.30 | 3.50 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 62.00 | 17.00 | 14.00 | 15.00 | 14.00 | 5.00 | 8.00 | 4.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 94 | 54.12 | 0.00 | 0.00 | 0.85 | 0.00 | 0.89 | 0.00 | 0.00 | 0.00 | **1.74** |
| DIVERGENCE_CONTINUATION | kept | 158 | 70.94 | 0.00 | 0.00 | 0.46 | 0.00 | 0.27 | 0.00 | 0.00 | 0.00 | **0.73** |
| FAILED_AUCTION_RECLAIM | filtered | 41 | 46.38 | 0.00 | 0.00 | 0.00 | 0.00 | 1.58 | 0.00 | 0.00 | 0.00 | **1.58** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 66.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 47 | 48.27 | 0.00 | 0.00 | 4.15 | 0.00 | 0.51 | 0.00 | 0.00 | 0.00 | **4.66** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 64.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 80 | 50.86 | 0.00 | 0.00 | 2.50 | 0.00 | 0.00 | 0.31 | 0.00 | 0.00 | **2.81** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 14 | 70.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 75.25 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | 0.00 | 0.00 | 0.00 | **6.00** |
| MEAN_REVERT | filtered | 73 | 48.45 | 0.00 | 0.00 | 0.00 | 0.00 | 2.73 | 0.14 | 0.00 | 5.03 | **7.90** |
| MEAN_REVERT | kept | 39 | 68.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 136 | 58.10 | 0.00 | 0.00 | 1.44 | 0.00 | 3.72 | 0.00 | 0.00 | 0.68 | **5.84** |
| MOVER_AVWAP_SCALP | kept | 201 | 79.51 | 0.00 | 0.00 | 0.34 | 0.00 | 0.00 | 0.16 | 0.00 | 0.12 | **0.62** |
| MOVER_TREND_PULLBACK | filtered | 1991 | 54.73 | 0.21 | 0.00 | 1.04 | 0.00 | 0.54 | 0.09 | 0.00 | 0.07 | **1.95** |
| MOVER_TREND_PULLBACK | kept | 3172 | 75.86 | 0.00 | 0.00 | 0.38 | 0.00 | 0.11 | 0.04 | 0.00 | 0.00 | **0.53** |
| QUIET_COMPRESSION_BREAK | filtered | 102 | 44.93 | 0.00 | 0.00 | 0.85 | 0.00 | 0.53 | 1.25 | 0.00 | 3.16 | **5.79** |
| QUIET_COMPRESSION_BREAK | kept | 161 | 73.32 | 0.00 | 0.00 | 0.09 | 0.00 | 0.37 | 0.06 | 0.00 | 0.00 | **0.52** |
| SR_FLIP_RETEST | filtered | 10 | 48.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | 0.00 | 0.00 | **6.00** |
| SR_FLIP_RETEST | kept | 34 | 71.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 37 | 57.71 | 0.00 | 0.00 | 5.28 | 0.00 | 1.75 | 0.00 | 0.00 | 0.00 | **7.03** |
| TREND_PULLBACK_EMA | kept | 125 | 78.11 | 0.00 | 0.00 | 1.89 | 0.00 | 0.19 | 0.00 | 0.00 | 0.00 | **2.08** |
| VOLUME_SURGE_BREAKOUT | filtered | 10 | 53.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 62.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **160182 held of 618229 seen** across 21 strategies; 3616 cells past the sample floor; **1871 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 46013 | 727/45286/0 | 45% | -0.15 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.27R) |
| MOVER_AVWAP_SCALP | 20790 | 186/20604/0 | 43% | -0.20 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 11785 | 127/11658/0 | 38% | -0.26 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (+1.77R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 11628 | 121/11507/0 | 48% | -0.06 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| TREND_PULLBACK_EMA | 9805 | 45/9760/0 | 40% | -0.23 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OFF_HOURS/RANGE/NORMAL/BTC_FALLING (-1.32R) |
| LIQUIDITY_SWEEP_REVERSAL | 8721 | 99/8622/0 | 35% | -0.49 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 7583 | 0/0/7583 | 43% | -0.10 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.39R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.13R) |
| SHADOW_RANGE_FADE | 7065 | 0/0/7065 | 35% | -0.15 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.40R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.17R) |
| QUIET_COMPRESSION_BREAK | 6797 | 409/6388/0 | 51% | -0.10 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 6304 | 0/0/6304 | 33% | -0.42 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.04R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.06R) |
| MEAN_REVERT | 4533 | 48/4485/0 | 38% | -0.31 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| SR_FLIP_RETEST | 4281 | 19/4262/0 | 44% | -0.29 | NY/RANGE/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.18R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| FUNDING_EXTREME_SIGNAL | 3439 | 2/3437/0 | 32% | -0.47 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3252 | 0/3252/0 | 31% | -0.33 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-1.19R) |
| RANGE_FADE | 1809 | 4/1805/0 | 33% | -0.51 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+2.15R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1467 | 0/0/1467 | 53% | -0.06 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.51R) |
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
| FUNDING_EXTREME_SIGNAL | 267 | 28% / -0.58R | 267 | 52% / -0.13R | +0.45 | **ATR** |
| LIQUIDATION_REVERSAL | 23 | 26% / -0.63R | 23 | 52% / -0.26R | +0.37 | **ATR** |
| TREND_PULLBACK_EMA | 849 | 39% / -0.32R | 849 | 52% / -0.07R | +0.26 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1357 | 43% / -0.35R | 1357 | 56% / -0.13R | +0.22 | **ATR** |
| RANGE_FADE | 90 | 32% / -0.35R | 90 | 40% / -0.20R | +0.15 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 163 | 35% / -0.21R | 163 | 47% / -0.07R | +0.14 | **ATR** |
| SR_FLIP_RETEST | 399 | 43% / -0.30R | 399 | 46% / -0.17R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 2041 | 44% / -0.18R | 2041 | 50% / -0.06R | +0.12 | **ATR** |
| MA_CROSS_TREND_SHIFT | 43 | 40% / -0.19R | 43 | 42% / -0.08R | +0.11 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1152 | 40% / -0.24R | 1152 | 42% / -0.14R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 8171 | 50% / -0.10R | 8171 | 55% / -0.01R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1282 | 48% / -0.10R | 1282 | 54% / -0.04R | +0.06 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1177 | 50% / -0.11R | 1177 | 50% / -0.12R | -0.01 | **FIXED** |
| MEAN_REVERT | 317 | 47% / -0.18R | 317 | 45% / -0.18R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 8 | 50% / -0.24R | 8 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 10996 | 28% | -0.23R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2041 | 48% | -0.06R | 226 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 103 | 48% | -0.07R | 62 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1522 | 40% / -0.17R | +0.84 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1129 | 34% / -0.23R | +0.83 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2500 | 35% / -0.12R | +0.73 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 9993 | 37% / -0.12R | +0.41 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1478 | 38% / -0.08R | +0.20 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1142 | 38% / -0.11R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 962 | 33% / -0.22R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 240 | 31% / -0.38R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 362 | 31% / -0.06R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 263 | 49% / -0.05R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 67 | 40% / -0.07R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 365 | 33% / -0.32R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 65 | 28% / -0.41R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 29 | 41% / -0.18R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 16 | 44% / +0.50R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×1070]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 196/6) (sustained 196 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.57R (bound 0.3) (streak 458/6) (sustained 458 cycles)
- **ALERT** `tuned_variants` — 469 non-stamps — atr_arm_uncomputable=469 (seen=15499 stamped=1961 skipped=13069) (streak 451/6) (sustained 451 cycles)
- **ALERT** `auto_dispatch` — 112 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=112) (streak 445/3) (sustained 445 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 42 fed / 0 quiet / 0 never delivered of 42 subscribed; 108351750 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 18 arms current, none stalled; covering 1972/1972 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 1/6) | 1 |
| atr_trail_live_arms | ok | 35 arms current, none stalled; covering 1124/1124 signals (100%) | 0 |
| auto_dispatch | violating | 112 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=112) (streak 445/3) | 445 |
| binance_ip_weight | ok | peak 251/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 80111.80 | 0 |
| candle_coverage | ok | 89/89 symbols with ≥20 15m candles, 89/89 updated within 45m [fresh=89; 76 Tier-1 futures + 13 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 356 dup bars, 0 undedupable; ws 0 out-of-order, 636 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 59 cohorts, 37 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +31 / upstream +7 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 2161/2179 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 1 of 161 open dark rows are not being advanced (worst: POLYXUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 49/120) | 49 |
| dark_sar_arms | ok | no open arms; covering 2156/2174 signals (99%) | 0 |
| depth_feed | ok | 42/42 books fresh (stale 0, never 0, thin 0); 35340806 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.57R (bound 0.3) (streak 458/6) | 458 |
| emission_controller | ok | last cycle 467s ago; live_overrides=14 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×1070]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 196/6) | 196 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 4/6) | 4 |
| firestore_read_budget | ok | 1,382 reads/day of 50,000 [engine 1,346, signing 36]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 5040 sealed bars over 42 symbols; 1759 incomplete, 3 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +1 / upstream +105 | 0 |
| indicator_cache_key | ok | 183663 frozen value(s) avoided; 501872 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.32R over n=4485 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +5 / upstream +105 | 0 |
| mover_admission_metadata | ok | 932 symbols known, 225 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 13 held, 13 with scan counts, 13 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2672 rows held, 3114582 evicted (sampled: execution:trigger_not_confirmed 362/1103761, execution:overextended 362/973406, setup_compat:regime_STRONG_TREND 362/528996) | 0 |
| price_action_lane | ok | 905338 evaluated, 1369 emitted; layer1 1369 stamped / 0 blind; cooldown=126213, delta_opposed=76909, no_footprint=332909, no_opposing_target=1188, no_sweep=293097, rr_below_floor=73653 | 0 |
| promoted_pair_integrity | ok | 13/13 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.51R over n=1805 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +3 / upstream +105 | 0 |
| sar_alignment_crosscheck | ok | 1568/33922 disagreed (4.6%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +105 | 0 |
| sar_hold_arm | ok | 1895 held arms settled, 105 unscored, 35 still walking (27 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 12/91 unfetchable (13%); top cause: gap or duplicate bar in the 15m window; symbols: AGTUSDT, ASTERUSDT, BABYUSDT, DASHUSDT, ENAUSDT +3 more | 0 |
| sar_live_arms | ok | 35 arms current, none stalled; covering 1122/1122 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 14 resolved, 65 still mid-window | 0 |
| scan_cycle | ok | last 8.27s, worst 227.23s over 10635 lifetime cycles; lifetime 432 over 60s, 71 over 120s; recent 4/0 warn/kill breaches in 20/20 cycles; heartbeat age 4.88s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 414223 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 27s ago (119.39s to run, worst 189.09s), 1447 overrun(s) of 9592 cycles, TTL 900s; slowest user_positions=34.87s, signals=22.73s, exchange_positions=13.12s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +56 / upstream +105 | 0 |
| structural_snap | ok | 5999/5999 measured, 35 blind, 0 levels moved (refusals: redetect_cooldown=1338) | 0 |
| structural_veto_lane | ok | 2757 stamped; 0 with no readable level book, 165 with clear air ahead, 2141 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +105 / upstream +7 | 0 |
| tuned_variants | violating | 469 non-stamps — atr_arm_uncomputable=469 (seen=15499 stamped=1961 skipped=13069) (streak 451/6) | 451 |
| unlock_shorts | ok | 12 open, 46 scheduled, calendar 1.0h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 46 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1572186`
- `Path funnel` emissions: `37`
- `Regime distribution` emissions: `37`
- `QUIET_SCALP_BLOCK` events: `171`
- `confidence_gate` events: `6531`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **8**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 1904 | 1904 | 1904 | 0 |
| futures_liq | 7 | 3456 | 9289 | 10974 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=246106] state[populated=246106] buckets[many=246106] sources[none] quality[none]
- funding_rate: presence[absent=18643, present=227463] state[empty=18643, populated=227463] buckets[few=227463, none=18643] sources[none] quality[none]
- liquidation_clusters: presence[absent=148450, present=97656] state[empty=148450, populated=97656] buckets[few=78896, none=148450, some=18760] sources[none] quality[none]
- oi_snapshot: presence[absent=18643, present=227463] state[empty=18643, populated=227463] buckets[few=190, many=226073, none=18643, some=1200] sources[none] quality[none]
- order_book: presence[absent=81168, present=164938] state[populated=164938, unavailable=81168] buckets[few=164938, none=81168] sources[book_ticker=164938, unavailable=81168] quality[none=81168, top_of_book_only=164938]
- orderblocks: presence[absent=246106] state[empty=246106] buckets[none=246106] sources[measured_dark=246106] quality[none]
- recent_ticks: presence[present=246106] state[populated=246106] buckets[many=246106] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.456368327140808` sec
- Median create→first breach: `5692.4178775548935` sec
- Median create→terminal: `5698.026746034622` sec
- Median first breach→terminal: `6.842613220214844e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.2}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 4 | 4 | 0.7623375329511526 | 0.8915697719425928 | 0.8369051052099828 | 0 | 4 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 2.6526905713247877 | 3.0 | 0.8842301904415959 | 0 | 1 |
| MEAN_REVERT | 1 | 1 | 0.9026592338441451 | 1.1987461927432952 | 0.7530027951775481 | 0 | 1 |
| MOVER_AVWAP_SCALP | 3 | 3 | 2.443178998931885 | 2.4218424944567505 | 1.04080232643304 | 2 | 1 |
| MOVER_TREND_PULLBACK | 24 | 24 | 3.881233529377997 | 3.0 | 1.2937445097926656 | 18 | 5 |
| QUIET_COMPRESSION_BREAK | 12 | 12 | 1.0328697559033464 | 1.1161247213923202 | 0.8946421627127799 | 0 | 8 |
| TREND_PULLBACK_EMA | 1 | 1 | 1.3826627032136078 | 1.5315752575095714 | 0.9027716375242939 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 4 | 4 | 75.0 | 25.0 | 75.0 | 0.0 | 0.7603 | 5893.304126024246 | 5898.013422012329 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 7606.995563983917 | 7606.99564909935 |
| MEAN_REVERT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 11549.439203977585 | 11549.439307928085 |
| MOVER_AVWAP_SCALP | 3 | 3 | 66.7 | 0.0 | 66.7 | 0.0 | 2.0986 | 5484.270384788513 | 5485.20286989212 |
| MOVER_TREND_PULLBACK | 24 | 24 | 12.5 | 58.3 | 12.5 | 0.0 | -1.1121 | 2495.503606557846 | 2495.5036514997482 |
| QUIET_COMPRESSION_BREAK | 12 | 12 | 41.7 | 33.3 | 41.7 | 0.0 | 0.4453 | 24132.40594112873 | 24132.406123518944 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.3827 | 6312.045675992966 | 6312.0457401275635 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 358 | 8 | 230 | 0.0 | 0.0 | None | None | 128 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1763 | 46 | 1428 | 0.0 | 100.0 | 6312.045675992966 | 6312.0457401275635 | 335 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-170`
- Gating Δ: `-18734`
- No-generation Δ: `-515763`
- Fast failures Δ: `-3`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.1939, "current_avg_pnl": 0.7603, "current_win_rate": 75.0, "previous_avg_pnl": 0.5664, "previous_win_rate": 0.0, "win_rate_delta": 75.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.767, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": -0.767, "previous_win_rate": 25.0, "win_rate_delta": -25.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 5.0308, "current_avg_pnl": 2.0986, "current_win_rate": 66.7, "previous_avg_pnl": -2.9322, "previous_win_rate": 0.0, "win_rate_delta": 66.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.4488, "current_avg_pnl": -1.1121, "current_win_rate": 12.5, "previous_avg_pnl": -0.6633, "previous_win_rate": 25.6, "win_rate_delta": -13.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.9088, "current_avg_pnl": 0.4453, "current_win_rate": 41.7, "previous_avg_pnl": 1.3541, "previous_win_rate": 50.0, "win_rate_delta": -8.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": -448, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 20, "geometry_changed_delta": 0, "geometry_preserved_delta": 59, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 6312.05, "median_terminal_delta_sec": 6312.05, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **MOVER_AVWAP_SCALP**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
