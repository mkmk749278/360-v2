# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, MOVER_AVWAP_SCALP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `231` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 176 | 176 | 175 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10936 | 10936 | 10449 | 5 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 103744 | 103735 | 46 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 89891 | 89892 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 89587 | 87131 | 2752 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 89922 | 88998 | 1005 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 94938 | 94683 | 282 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 82714 | 82735 | 5 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 90010 | 90045 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 90056 | 87921 | 3065 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 109051 | 115389 | 1450 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 103786 | 92774 | 16215 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 94389 | 94390 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 89894 | 89885 | 33 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 89547 | 89486 | 99 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 90993 | 90129 | 1202 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 88971 | 89232 | 271 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 77797 | 72832 | 5370 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 78215 | 77692 | 591 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 103701 | 103677 | 65 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 82744 | 82759 | 9 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4946 | 4946 | 4352 | 9 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 709 | 709 | 619 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 14 | 14 | 6 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 28242 | 28242 | 27998 | 11 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 8 | 8 | 7 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 9038 | 9038 | 8282 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 4045 | 4045 | 3559 | 25 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 45690 | 45690 | 38526 | 185 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 59 | 59 | 59 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1043 | 1043 | 999 | 6 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3555 | 3555 | 3507 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1320 | 1320 | 945 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2726 | 2726 | 2659 | 11 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 128 | 128 | 121 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 624 | 624 | 385 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=103735): breakout_not_found=59945, basic_filters_failed=31320, move_not_fresh=7266, breakout_stale=3334, retest_proximity_failed=1607, volume_spike_missing=263
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=89892): cls_disabled_merged_into_lsr=89892
- **EVAL::DIVERGENCE_CONTINUATION** (total=87131): cvd_divergence_failed=34674, h1_trend_not_aligned=24188, basic_filters_failed=22500, ema_alignment_reject=4277, retest_proximity_failed=1085, missing_fvg_or_orderblock=407
- **EVAL::FAILED_AUCTION_RECLAIM** (total=88998): auction_not_detected=55242, basic_filters_failed=21895, reclaim_hold_failed=4685, tail_too_small=3656, regime_blocked=3490, rsi_reject=30
- **EVAL::FUNDING_EXTREME** (total=94683): funding_not_extreme=65302, basic_filters_failed=23978, missing_funding_rate=2064, ema_alignment_reject=1798, rsi_reject=1007, momentum_reject=276, cvd_divergence_failed=224, missing_fvg_or_orderblock=34
- **EVAL::LIQUIDATION_REVERSAL** (total=82735): cascade_threshold_not_met=57567, basic_filters_failed=24244, cvd_divergence_failed=566, rsi_reject=338, missing_fvg_or_orderblock=17, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=90045): no_ma_cross=66277, basic_filters_failed=22513, ma_cross_cooldown=685, ma_cross_htf_misaligned=505, ma_cross_htf_unconfirmed=65
- **EVAL::MEAN_REVERT** (total=87921): no_extension=69865, basic_filters_failed=18056
- **EVAL::MOVER_AVWAP_SCALP** (total=115389): no_avwap_tag=43218, basic_filters_failed=31558, no_mover_leg=22818, avwap_slope_against=11706, avwap_reclaim_no_volume=3613, no_avwap_reclaim=2404, anchor_too_recent=72
- **EVAL::MOVER_TREND_PULLBACK** (total=92774): mover_run_too_small=39205, basic_filters_failed=31382, no_reclaim=18085, no_pullback_tag=3866, insufficient_candles=236
- **EVAL::OPENING_RANGE_BREAKOUT** (total=94390): feature_disabled=94390
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=89885): regime_blocked=55766, breakout_not_found=23310, basic_filters_failed=8635, adx_reject=2122, ema_alignment_reject=52
- **EVAL::QUIET_COMPRESSION_BREAK** (total=89486): regime_blocked=37531, compression_not_detected=36922, basic_filters_failed=13249, breakout_not_detected=1580, volume_confirmation_failed=195, rsi_reject=7, missing_fvg_or_orderblock=2
- **EVAL::RANGE_FADE** (total=90129): no_range_edge=72065, basic_filters_failed=18064
- **EVAL::SR_FLIP_RETEST** (total=89232): flip_close_not_confirmed=54813, basic_filters_failed=21869, regime_blocked=3481, long_break_volume_thin=3266, retest_out_of_zone=3192, h1_break_not_confirmed=1119, reclaim_hold_failed=911, long_acceptance_not_held=220, ema_alignment_reject=161, wick_quality_failed=155, whipsaw_flip=34, missing_fvg_or_orderblock=11
- **EVAL::STANDARD** (total=72832): adx_reject=17979, momentum_reject=17947, basic_filters_failed=14843, sweeps_not_detected=7913, ema_alignment_reject=7422, macd_reject=5619, htf_poi_unanchored=906, rsi_reject=163, invalid_sl_geometry=40
- **EVAL::TREND_PULLBACK** (total=77692): h1_trend_not_aligned=29379, basic_filters_failed=10726, ema_alignment_reject=9919, h1_pullback_not_confirmed=9737, ema_not_tested_prev=6993, no_ema_reclaim_close=4949, body_conviction_fail=2294, rsi_reject=1743, prev_already_above_emas=881, no_prev_high_break=481, prev_already_below_emas=224, momentum_flat=127, ema21_not_tagged=91, no_prev_low_break=83, momentum_reject=52, missing_fvg_or_orderblock=13
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=103677): breakout_not_found=54636, basic_filters_failed=31315, move_not_fresh=11004, breakout_stale=4337, retest_proximity_failed=1990, volume_spike_missing=365, missing_fvg_or_orderblock=24, move_exhausted=6
- **EVAL::WHALE_MOMENTUM** (total=82759): momentum_reject=58934, recent_ticks_insufficient=18503, basic_filters_failed=5322

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=16): execution:overextended=16
- **DIVERGENCE_CONTINUATION** (total=212): setup_compat:regime_VOLATILE_UNSUITABLE=182, setup_compat:regime_BREAKOUT_EXPANSION=15, execution:overextended=15
- **FAILED_AUCTION_RECLAIM** (total=969): execution:overextended=454, setup_compat:regime_STRONG_TREND=433, context_floor=82
- **FUNDING_EXTREME_SIGNAL** (total=633): execution:trigger_not_confirmed=633
- **LIQUIDATION_REVERSAL** (total=14): execution:trigger_not_confirmed=14
- **LIQUIDITY_SWEEP_REVERSAL** (total=8678): setup_compat:regime_STRONG_TREND=3332, execution:trigger_not_confirmed=2679, execution:overextended=2667
- **MA_CROSS_TREND_SHIFT** (total=6): execution:overextended=3, setup_compat:regime_DIRTY_RANGE=2, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=6633): setup_compat:regime_STRONG_TREND=3346, setup_compat:regime_WEAK_TREND=2364, execution:overextended=923
- **MOVER_AVWAP_SCALP** (total=1957): execution:overextended=1267, execution:trigger_not_confirmed=624, entry_quality=66
- **MOVER_TREND_PULLBACK** (total=20115): execution:trigger_not_confirmed=11131, execution:overextended=8023, entry_quality=961
- **POST_DISPLACEMENT_CONTINUATION** (total=11): execution:overextended=11
- **QUIET_COMPRESSION_BREAK** (total=37): execution:trigger_not_confirmed=37
- **RANGE_FADE** (total=2580): setup_compat:regime_STRONG_TREND=1327, setup_compat:regime_WEAK_TREND=799, execution:overextended=366, setup_compat:regime_VOLATILE_UNSUITABLE=88
- **TREND_PULLBACK_EMA** (total=2271): setup_compat:regime_CLEAN_RANGE=1387, setup_compat:regime_DIRTY_RANGE=821, setup_compat:regime_VOLATILE_UNSUITABLE=54, entry_quality=9
- **VOLUME_SURGE_BREAKOUT** (total=23): execution:overextended=17, context_floor=6
- **WHALE_MOMENTUM** (total=578): execution:trigger_not_confirmed=578

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 251087 | 45.0% |
| TRENDING_UP | 99675 | 17.8% |
| TRENDING_DOWN | 92308 | 16.5% |
| QUIET | 88041 | 15.8% |
| VOLATILE | 27332 | 4.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **84**
- Average confidence gap to threshold: **8.27** (samples=84) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: LITUSDT=22, BTCUSDT=13, ASTERUSDT=13, SOLUSDT=8, BNBUSDT=6, 1000PEPEUSDT=6, CATIUSDT=6, AVAXUSDT=3, BCHUSDT=3, ENAUSDT=2

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 43 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 9 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 132 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 17 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 30 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 11 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 6 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 15 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 53 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 121 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 649 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 24 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2292 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 26 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 7 |
| SR_FLIP_RETEST | filtered | min_confidence | 27 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 5 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 9 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 6 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 1 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 22 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 66.70 | 65.00 | -1.70 | 20.40 | 17.00 | 20.00 | 3.00 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 46 | 45.37 | 62.91 | 17.54 | 18.65 | 19.12 | 18.23 | 0.67 | 24.42 |
| DIVERGENCE_CONTINUATION | kept | 9 | 71.56 | 65.00 | -6.56 | 20.00 | 19.78 | 17.29 | 0.56 | -1.00 |
| FAILED_AUCTION_RECLAIM | filtered | 149 | 55.45 | 64.33 | 8.88 | 20.56 | 19.40 | 20.00 | 3.42 | 1.31 |
| FAILED_AUCTION_RECLAIM | kept | 30 | 68.77 | 65.00 | -3.77 | 19.86 | 18.91 | 20.00 | 3.12 | 2.60 |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 53.52 | 61.00 | 7.48 | 20.32 | 13.43 | 17.00 | 4.73 | 3.25 |
| LIQUIDATION_REVERSAL | filtered | 6 | 58.45 | 10.00 | -48.45 | 21.20 | 8.83 | 15.13 | 6.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 56.19 | 62.41 | 6.22 | 20.61 | 19.86 | 19.65 | 4.65 | 13.13 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 53 | 69.97 | 65.00 | -4.97 | 19.74 | 19.29 | 17.28 | 1.96 | -0.79 |
| MOVER_AVWAP_SCALP | filtered | 1 | 56.90 | 65.00 | 8.10 | 24.50 | 18.90 | 15.80 | 4.50 | 21.60 |
| MOVER_AVWAP_SCALP | kept | 121 | 80.57 | 65.00 | -15.57 | 20.44 | 16.57 | 15.80 | 4.01 | 1.51 |
| MOVER_TREND_PULLBACK | filtered | 673 | 56.28 | 63.38 | 7.10 | 19.79 | 18.62 | 15.80 | 3.98 | 18.37 |
| MOVER_TREND_PULLBACK | kept | 2292 | 75.64 | 65.00 | -10.64 | 20.06 | 18.45 | 15.80 | 4.38 | 1.97 |
| QUIET_COMPRESSION_BREAK | filtered | 26 | 57.87 | 65.00 | 7.13 | 21.74 | 18.29 | 20.00 | 0.00 | 7.48 |
| QUIET_COMPRESSION_BREAK | kept | 7 | 73.61 | 65.00 | -8.61 | 21.37 | 19.21 | 20.00 | 0.00 | 1.21 |
| SR_FLIP_RETEST | filtered | 32 | 54.51 | 63.50 | 8.99 | 22.56 | 20.00 | 15.26 | 2.50 | 14.76 |
| SR_FLIP_RETEST | kept | 9 | 71.70 | 65.00 | -6.70 | 20.64 | 20.00 | 18.00 | 2.67 | 1.06 |
| TREND_PULLBACK_EMA | filtered | 7 | 58.07 | 65.00 | 6.93 | 22.13 | 19.90 | 16.37 | 5.36 | 18.93 |
| TREND_PULLBACK_EMA | kept | 22 | 74.71 | 65.00 | -9.71 | 20.80 | 19.79 | 17.97 | 4.84 | 5.85 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 54.50 | 61.00 | 6.50 | 21.20 | 15.40 | 20.00 | 4.50 | 23.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 66.70 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 4.70 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 46 | 45.37 | 23.78 | 14.09 | 5.93 | 11.57 | 5.08 | 8.66 | 0.67 |
| DIVERGENCE_CONTINUATION | kept | 9 | 71.56 | 24.11 | 15.78 | 4.00 | 13.56 | 5.39 | 8.17 | 0.56 |
| FAILED_AUCTION_RECLAIM | filtered | 149 | 55.45 | 20.65 | 15.37 | 6.32 | 13.56 | 6.28 | 3.34 | 3.42 |
| FAILED_AUCTION_RECLAIM | kept | 30 | 68.77 | 22.07 | 17.60 | 6.10 | 14.07 | 6.87 | 2.65 | 3.12 |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 53.52 | 22.82 | 8.91 | 4.09 | 13.91 | 8.50 | 6.09 | 4.73 |
| LIQUIDATION_REVERSAL | filtered | 6 | 58.45 | 25.00 | 8.00 | 14.50 | 8.00 | 5.00 | 4.45 | 6.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 56.19 | 24.06 | 14.00 | 6.00 | 9.24 | 5.41 | 5.97 | 4.65 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 53 | 69.97 | 23.15 | 16.11 | 4.87 | 13.30 | 6.59 | 3.98 | 1.96 |
| MOVER_AVWAP_SCALP | filtered | 1 | 56.90 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 8.00 | 4.50 |
| MOVER_AVWAP_SCALP | kept | 121 | 80.57 | 20.98 | 18.51 | 10.75 | 13.95 | 7.00 | 6.90 | 4.01 |
| MOVER_TREND_PULLBACK | filtered | 673 | 56.28 | 17.70 | 18.11 | 8.03 | 12.62 | 6.16 | 9.13 | 3.98 |
| MOVER_TREND_PULLBACK | kept | 2292 | 75.64 | 18.48 | 18.05 | 7.74 | 13.09 | 7.47 | 8.48 | 4.38 |
| QUIET_COMPRESSION_BREAK | filtered | 26 | 57.87 | 17.31 | 18.00 | 10.15 | 14.50 | 6.92 | 5.38 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 7 | 73.61 | 21.57 | 17.43 | 11.14 | 14.00 | 7.21 | 6.90 | 0.00 |
| SR_FLIP_RETEST | filtered | 32 | 54.51 | 25.00 | 16.44 | 3.19 | 14.28 | 5.00 | 2.86 | 2.50 |
| SR_FLIP_RETEST | kept | 9 | 71.70 | 24.11 | 16.89 | 3.67 | 14.33 | 5.00 | 6.09 | 2.67 |
| TREND_PULLBACK_EMA | filtered | 7 | 58.07 | 17.00 | 18.00 | 7.50 | 14.43 | 5.00 | 9.71 | 5.36 |
| TREND_PULLBACK_EMA | kept | 22 | 74.71 | 21.00 | 18.00 | 7.70 | 14.68 | 5.73 | 8.99 | 4.84 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 54.50 | 17.00 | 14.00 | 15.00 | 14.00 | 5.00 | 8.00 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 66.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 46 | 45.37 | 0.00 | 0.00 | 0.00 | 0.00 | 1.41 | 0.00 | 0.00 | 0.00 | **1.41** |
| DIVERGENCE_CONTINUATION | kept | 9 | 71.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 149 | 55.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | **0.14** |
| FAILED_AUCTION_RECLAIM | kept | 30 | 68.77 | 0.00 | 0.00 | 0.00 | 0.00 | 0.40 | 0.00 | 0.00 | 0.00 | **0.40** |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 53.52 | 0.00 | 0.00 | 1.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.89** |
| LIQUIDATION_REVERSAL | filtered | 6 | 58.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 56.19 | 0.00 | 0.00 | 0.00 | 0.00 | 13.13 | 0.00 | 0.00 | 0.00 | **13.13** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 53 | 69.97 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 1 | 56.90 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| MOVER_AVWAP_SCALP | kept | 121 | 80.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.31 | 0.00 | 0.00 | 0.80 | **1.11** |
| MOVER_TREND_PULLBACK | filtered | 673 | 56.28 | 0.00 | 0.00 | 1.36 | 0.00 | 1.31 | 0.00 | 0.00 | 0.00 | **2.67** |
| MOVER_TREND_PULLBACK | kept | 2292 | 75.64 | 0.00 | 0.00 | 0.55 | 0.00 | 0.53 | 0.00 | 0.00 | 0.00 | **1.08** |
| QUIET_COMPRESSION_BREAK | filtered | 26 | 57.87 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 7 | 73.61 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 32 | 54.51 | 0.00 | 0.00 | 0.00 | 0.00 | 1.35 | 0.00 | 0.00 | 5.06 | **6.41** |
| SR_FLIP_RETEST | kept | 9 | 71.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 7 | 58.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 22 | 74.71 | 0.00 | 0.00 | 0.00 | 0.00 | 0.98 | 0.00 | 0.00 | 0.00 | **0.98** |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 54.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **78968 held of 186754 seen** across 21 strategies; 1763 cells past the sample floor; **754 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 31593 | 351/31242/0 | 46% | -0.13 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.17R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.13R) |
| MOVER_AVWAP_SCALP | 9546 | 90/9456/0 | 41% | -0.25 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 6214 | 51/6163/0 | 42% | -0.18 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 4361 | 24/4337/0 | 54% | +0.06 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 4235 | 0/0/4235 | 43% | -0.08 | ASIA/RANGE/NORMAL/BTC_RISING (+0.23R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.09R) |
| TREND_PULLBACK_EMA | 3766 | 12/3754/0 | 46% | -0.17 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.18R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.21R) |
| QUIET_COMPRESSION_BREAK | 3758 | 128/3630/0 | 47% | -0.11 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+0.84R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_RANGE_FADE | 3558 | 0/0/3558 | 36% | -0.10 | LONDON/RANGE/EXPANDED/BTC_NEUTRAL (+0.28R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-0.94R) |
| SHADOW_FUNDING_FADE | 2963 | 0/0/2963 | 38% | -0.35 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-1.01R) |
| WHALE_MOMENTUM | 2064 | 2/2062/0 | 40% | -0.38 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 1912 | 20/1892/0 | 39% | -0.22 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.21R) |
| MEAN_REVERT | 1333 | 18/1315/0 | 60% | +0.12 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 938 | 2/936/0 | 31% | -0.45 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.37R) |
| VOLUME_SURGE_BREAKOUT | 924 | 0/924/0 | 47% | -0.10 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| SR_FLIP_RETEST | 622 | 0/622/0 | 48% | -0.24 | ASIA/MARKDOWN/NORMAL/BTC_FALLING/ALTCOIN (+0.72R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 469 | 0/0/469 | 54% | -0.02 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.18R) |
| RANGE_FADE | 256 | 0/256/0 | 52% | -0.11 | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (+1.36R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| BREAKDOWN_SHORT | 210 | 18/192/0 | 20% | -0.60 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDATION_REVERSAL | 196 | 0/196/0 | 11% | -1.00 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 46 | 6/40/0 | 35% | -0.17 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 4 | 0/4/0 | 50% | +0.17 | — | — |

- **Strongest cells**: `DIVERGENCE_CONTINUATION @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +1.76R (n=34, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +1.66R (n=15, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ NY/RANGE/NORMAL/BTC_FALLING` +1.64R (n=19, STRONG)
- **Weakest cells**: `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING` -1.38R (n=17, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.37R (n=16, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 100 | 33% / -0.42R | 100 | 49% / -0.13R | +0.29 | **ATR** |
| TREND_PULLBACK_EMA | 326 | 49% / -0.15R | 326 | 56% / -0.03R | +0.12 | **ATR** |
| SR_FLIP_RETEST | 84 | 46% / -0.30R | 84 | 49% / -0.19R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 247 | 43% / -0.34R | 247 | 45% / -0.24R | +0.10 | **ATR** |
| RANGE_FADE | 19 | 47% / +0.11R | 19 | 47% / +0.01R | -0.10 | **FIXED** |
| MOVER_AVWAP_SCALP | 750 | 46% / -0.17R | 750 | 51% / -0.08R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 504 | 44% / -0.17R | 504 | 46% / -0.08R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 4817 | 51% / -0.08R | 4817 | 55% / -0.01R | +0.08 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 63 | 44% / -0.10R | 63 | 51% / -0.04R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 15 | 33% / -0.24R | 15 | 33% / -0.19R | +0.06 | **ATR** |
| BREAKDOWN_SHORT | 20 | 30% / -0.17R | 20 | 30% / -0.14R | +0.03 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 381 | 51% / -0.18R | 381 | 55% / -0.16R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 622 | 45% / -0.15R | 622 | 46% / -0.16R | -0.01 | **FIXED** |
| MEAN_REVERT | 107 | 58% / +0.05R | 107 | 55% / +0.04R | -0.01 | **FIXED** |
| DIVERGENCE_CONTINUATION | 460 | 54% / -0.01R | 460 | 59% / -0.01R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 13 | 31% / -0.46R | 13 | 54% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 7121 | 31% | -0.12R | 287 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 750 | 49% | -0.08R | 167 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 42 | 55% | -0.06R | 34 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 86 | 36% / -0.24R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 585 | 37% / -0.08R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 6122 | 37% / -0.10R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 904 | 37% / -0.02R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 393 | 36% / -0.07R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 514 | 42% / +0.10R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 424 | 38% / -0.03R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 381 | 45% / -0.04R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 88 | 28% / -0.48R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 114 | 31% / -0.58R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 86 | 53% / +0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 40 | 40% / -0.10R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 17 | 41% / +0.18R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 85 | 31% / -0.38R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 21 | 14% / -0.68R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 17 | 41% / -0.06R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 8 | 38% / -0.01R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 55 · alerting: **6** · boot grace active: False
- **ALERT** `sar_alignment_crosscheck` — 227/3990 disagreed (5.7%) (streak 127/6) (sustained 127 cycles)
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×146]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 127/6) (sustained 127 cycles)
- **ALERT** `edge_reconciliation` — LIQUIDITY_SWEEP_REVERSAL realized−counterfactual=+0.40R (bound 0.3) (streak 127/6) (sustained 127 cycles)
- **ALERT** `mean_revert_emission` — 4099 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.11R over n=1315, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 120/6) (sustained 120 cycles)
- **ALERT** `tuned_variants` — 26 non-stamps — atr_arm_uncomputable=26 (seen=1214 stamped=159 skipped=1029) (streak 108/6) (sustained 108 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 127/3) (sustained 127 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 8030710 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 127/3) | 127 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 43 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 2/12) | 2 |
| auto_dispatch | ok | placed=22 rejected=1 skipped=23 over 23 fan-out(s) to a keyed roster; top reasons: mode=23, NotionalTooSmall=1 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 78650.00 | 0 |
| candle_coverage | ok | 79/79 symbols with ≥20 15m candles, 79/79 updated within 45m [fresh=79; 75 Tier-1 futures + 4 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 632 dup bars, 0 undedupable; ws 0 out-of-order, 94 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +40 / upstream +28 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1180/1197 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | 73 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1174/1191 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 3330192 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | LIQUIDITY_SWEEP_REVERSAL realized−counterfactual=+0.40R (bound 0.3) (streak 127/6) | 127 |
| emission_controller | ok | last cycle 3s ago; live_overrides=12 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×146]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 127/6) | 127 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 5/6) | 5 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +4 / upstream +221 | 0 |
| indicator_cache_key | ok | 19885 frozen value(s) avoided; 59423 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 4099 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.11R over n=1315, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 120/6) | 120 |
| mean_revert_path | ok | output +24 / upstream +221 | 0 |
| mover_admission_metadata | ok | 897 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 4 held, 4 with scan counts, 4 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 6 locked / 6 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2980 rows held, 1166058 evicted (sampled: execution:trigger_not_confirmed 400/421920, execution:overextended 400/399460, setup_compat:regime_STRONG_TREND 400/168402) | 0 |
| price_action_lane | ok | 300635 evaluated, 325 emitted; layer1 325 stamped / 0 blind; cooldown=41455, delta_opposed=27426, no_footprint=118941, no_opposing_target=955, no_sweep=88310, rr_below_floor=23223 | 0 |
| promoted_pair_integrity | ok | 4/4 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.11R over n=256 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +36 / upstream +221 | 0 |
| sar_alignment_crosscheck | violating | 227/3990 disagreed (5.7%) (streak 127/6) | 127 |
| sar_exit_shadow | ok | output +10 / upstream +221 | 0 |
| sar_hold_arm | ok | 1206 held arms settled, 181 unscored, 43 still walking (38 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 8/30 unfetchable (27%); top cause: located bar does not contain the stamp; symbols: BULLAUSDT, DOODUSDT, FARTCOINUSDT, ORCAUSDT, UAIUSDT +2 more | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 42 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 2/12) | 2 |
| sar_refresh_budget | ok | 17 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 430 records await one (22 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| scan_cycle | ok | last 16.7s, worst 93.02s over 3653 lifetime cycles; lifetime 5 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 3.85s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 114426 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 4m ago | 0 |
| snapshot_writer | ok | last cycle 4s ago (12.46s to run, worst 63.31s), 131 overrun(s) of 2721 cycles, TTL 900s; slowest dark_promotion=4.33s, router_delivery=1.54s, position_marks=1.25s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +2 / upstream +221 | 0 |
| structural_snap | ok | 4741/4741 measured, 12 blind, 0 levels moved (refusals: redetect_cooldown=124) | 0 |
| structural_veto_lane | ok | 271 stamped; 0 with no readable level book, 8 with clear air ahead, 177 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +221 / upstream +28 | 0 |
| tuned_variants | violating | 26 non-stamps — atr_arm_uncomputable=26 (seen=1214 stamped=159 skipped=1029) (streak 108/6) | 108 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2544372`
- `Path funnel` emissions: `67`
- `Regime distribution` emissions: `67`
- `QUIET_SCALP_BLOCK` events: `84`
- `confidence_gate` events: `3513`
- `free_channel_post` events: `52`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **2**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 1 | 2599 | 2599 | 2599 | 0 |
| futures_mover | 1 | 2861 | 2861 | 2861 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **52**

| Source | Count |
|---|---:|
| signal_close | 46 |
| regime_shift | 5 |
| signal_highlight | 1 |

- By severity: HIGH=52

## Dependency readiness
- cvd: presence[present=452299] state[populated=452299] buckets[many=452299] sources[none] quality[none]
- funding_rate: presence[absent=49384, present=402915] state[empty=49384, populated=402915] buckets[few=402915, none=49384] sources[none] quality[none]
- liquidation_clusters: presence[absent=243948, present=208351] state[empty=243948, populated=208351] buckets[few=166789, none=243948, some=41562] sources[none] quality[none]
- oi_snapshot: presence[absent=47400, present=404899] state[empty=47400, populated=404899] buckets[many=404899, none=47400] sources[none] quality[none]
- order_book: presence[absent=121141, present=331158] state[populated=331158, unavailable=121141] buckets[few=331158, none=121141] sources[book_ticker=331158, unavailable=121141] quality[none=121141, top_of_book_only=331158]
- orderblocks: presence[absent=452299] state[empty=452299] buckets[none=452299] sources[measured_dark=452299] quality[none]
- recent_ticks: presence[present=452299] state[populated=452299] buckets[many=452299] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `9.064424514770508` sec
- Median create→first breach: `4222.532930016518` sec
- Median create→terminal: `4226.703130602837` sec
- Median first breach→terminal: `2.3117995262145996` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 2.6006892095627867 | 3.0 | 0.8668964031875955 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 5 | 5 | 1.270364547383488 | 1.4311319201858204 | 0.8608085446751204 | 0 | 5 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 1.3433395314243162 | 1.3413245221271928 | 1.0015022533800604 | 0 | 0 |
| MOVER_AVWAP_SCALP | 8 | 8 | 1.8204771884526065 | 1.9982098525996967 | 0.8606282144719848 | 1 | 7 |
| MOVER_TREND_PULLBACK | 25 | 25 | 3.789463614887479 | 3.0 | 1.2631545382958265 | 20 | 5 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 1.146271174687038 | 1.2874999856203528 | 0.8992366568428132 | 0 | 5 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.6007 | 3117.469799041748 | 3119.6047189235687 |
| FAILED_AUCTION_RECLAIM | 5 | 5 | 0.0 | 60.0 | 0.0 | 0.0 | -0.4545 | 6669.369735956192 | 6696.34539103508 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 2.0209 | 3328.2136330604553 | 3331.8176419734955 |
| MOVER_AVWAP_SCALP | 8 | 8 | 25.0 | 62.5 | 25.0 | 0.0 | -0.3022 | 6744.470877408981 | 6745.95004093647 |
| MOVER_TREND_PULLBACK | 25 | 25 | 32.0 | 48.0 | 32.0 | 0.0 | -0.1419 | 2000.2802150249481 | 2000.8833031654358 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 16.7 | 50.0 | 16.7 | 0.0 | 0.5352 | 17339.62851846218 | 17343.24407351017 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1320 | 2 | 945 | 0.0 | 0.0 | None | None | 375 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2726 | 11 | 2659 | 0.0 | 0.0 | None | None | 67 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-22`
- Gating Δ: `-2462`
- No-generation Δ: `-29207`
- Fast failures Δ: `-1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.4545, "current_avg_pnl": -0.4545, "current_win_rate": 0.0, "previous_avg_pnl": 0.0, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.0155, "current_avg_pnl": -0.3022, "current_win_rate": 25.0, "previous_avg_pnl": 0.7133, "previous_win_rate": 40.0, "win_rate_delta": -15.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.9158, "current_avg_pnl": -0.1419, "current_win_rate": 32.0, "previous_avg_pnl": -1.0577, "previous_win_rate": 26.3, "win_rate_delta": 5.7}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.2924, "current_avg_pnl": 0.5352, "current_win_rate": 16.7, "previous_avg_pnl": 0.2428, "previous_win_rate": 28.6, "win_rate_delta": -11.9}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 281, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 9, "geometry_changed_delta": 0, "geometry_preserved_delta": -39, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -25328.72, "median_terminal_delta_sec": -25332.39, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
