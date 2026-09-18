# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `464` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 132 | 132 | 132 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 15150 | 15150 | 14506 | 7 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 104235 | 104204 | 47 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 87827 | 87827 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 87610 | 84111 | 3706 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 87833 | 86555 | 1333 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 94631 | 94454 | 193 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 85075 | 85076 | 7 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 87891 | 87899 | 18 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 87920 | 84611 | 4118 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 109672 | 113082 | 1263 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 104257 | 90746 | 18891 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 94124 | 94124 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 87830 | 87833 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 87594 | 87271 | 334 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 88732 | 86838 | 2361 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 87069 | 87134 | 436 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 78077 | 72671 | 5598 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 78279 | 77632 | 701 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 104210 | 104040 | 195 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 85085 | 85094 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4917 | 4917 | 4395 | 5 | active-healthy (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 998 | 998 | 926 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 13 | 13 | 11 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 27635 | 27635 | 27026 | 17 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 29 | 29 | 26 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 12553 | 12553 | 12104 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3720 | 3720 | 3503 | 12 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 63691 | 63691 | 58994 | 135 | active-healthy (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2164 | 2164 | 2151 | 11 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 7230 | 7230 | 6881 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1385 | 1385 | 1359 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3218 | 3218 | 3085 | 11 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 446 | 446 | 427 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=104204): breakout_not_found=65637, basic_filters_failed=26802, move_not_fresh=6780, breakout_stale=3883, retest_proximity_failed=834, volume_spike_missing=183, move_exhausted=54, missing_fvg_or_orderblock=31
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=87827): cls_disabled_merged_into_lsr=87827
- **EVAL::DIVERGENCE_CONTINUATION** (total=84111): cvd_divergence_failed=40042, basic_filters_failed=20053, h1_trend_not_aligned=17663, ema_alignment_reject=4800, retest_proximity_failed=990, missing_fvg_or_orderblock=409, missing_cvd=154
- **EVAL::FAILED_AUCTION_RECLAIM** (total=86555): auction_not_detected=55939, basic_filters_failed=19125, reclaim_hold_failed=4686, regime_blocked=3816, tail_too_small=2962, rsi_reject=27
- **EVAL::FUNDING_EXTREME** (total=94454): funding_not_extreme=67006, basic_filters_failed=21204, missing_funding_rate=3490, ema_alignment_reject=1519, rsi_reject=870, cvd_divergence_failed=194, momentum_reject=155, missing_fvg_or_orderblock=16
- **EVAL::LIQUIDATION_REVERSAL** (total=85076): cascade_threshold_not_met=61536, basic_filters_failed=22575, cvd_divergence_failed=467, rsi_reject=445, missing_fvg_or_orderblock=38, volume_spike_missing=15
- **EVAL::MA_CROSS_TREND_SHIFT** (total=87899): no_ma_cross=65215, basic_filters_failed=20055, ma_cross_cooldown=2057, ma_cross_htf_misaligned=572
- **EVAL::MEAN_REVERT** (total=84611): no_extension=70882, basic_filters_failed=13729
- **EVAL::MOVER_AVWAP_SCALP** (total=113082): no_avwap_tag=47067, basic_filters_failed=26894, no_mover_leg=23397, avwap_slope_against=11008, avwap_reclaim_no_volume=2791, no_avwap_reclaim=1851, anchor_too_recent=74
- **EVAL::MOVER_TREND_PULLBACK** (total=90746): mover_run_too_small=40110, basic_filters_failed=26850, no_reclaim=20411, no_pullback_tag=3375
- **EVAL::OPENING_RANGE_BREAKOUT** (total=94124): feature_disabled=94124
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=87833): regime_blocked=72963, breakout_not_found=9523, basic_filters_failed=4410, adx_reject=919, ema_alignment_reject=18
- **EVAL::QUIET_COMPRESSION_BREAK** (total=87271): compression_not_detected=46416, regime_blocked=18642, basic_filters_failed=14712, breakout_not_detected=6679, volume_confirmation_failed=766, rsi_reject=49, missing_fvg_or_orderblock=7
- **EVAL::RANGE_FADE** (total=86838): no_range_edge=73107, basic_filters_failed=13731
- **EVAL::SR_FLIP_RETEST** (total=87134): flip_close_not_confirmed=55476, basic_filters_failed=19116, regime_blocked=3803, long_break_volume_thin=3126, retest_out_of_zone=2651, h1_break_not_confirmed=1596, reclaim_hold_failed=780, long_acceptance_not_held=172, ema_alignment_reject=161, wick_quality_failed=144, whipsaw_flip=62, missing_fvg_or_orderblock=47
- **EVAL::STANDARD** (total=72671): momentum_reject=21162, adx_reject=17616, macd_reject=10962, basic_filters_failed=9903, sweeps_not_detected=7641, ema_alignment_reject=3024, htf_poi_unanchored=2034, invalid_sl_geometry=173, rsi_reject=145, mtf_reject=11
- **EVAL::TREND_PULLBACK** (total=77632): h1_trend_not_aligned=21355, ema_alignment_reject=12020, h1_pullback_not_confirmed=10898, basic_filters_failed=10190, ema_not_tested_prev=9102, no_ema_reclaim_close=6326, body_conviction_fail=2961, rsi_reject=2654, prev_already_above_emas=916, no_prev_high_break=609, prev_already_below_emas=222, momentum_flat=202, no_prev_low_break=125, ema21_not_tagged=29, missing_fvg_or_orderblock=15, momentum_reject=8
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=104040): breakout_not_found=53095, basic_filters_failed=26799, move_not_fresh=16862, breakout_stale=5469, retest_proximity_failed=1474, volume_spike_missing=292, move_exhausted=30, missing_fvg_or_orderblock=19
- **EVAL::WHALE_MOMENTUM** (total=85094): momentum_reject=58031, recent_ticks_insufficient=17794, basic_filters_failed=9269

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=37): execution:overextended=37
- **DIVERGENCE_CONTINUATION** (total=931): setup_compat:regime_VOLATILE_UNSUITABLE=856, setup_compat:regime_BREAKOUT_EXPANSION=75
- **FAILED_AUCTION_RECLAIM** (total=1678): execution:overextended=1082, setup_compat:regime_STRONG_TREND=437, context_floor=159
- **FUNDING_EXTREME_SIGNAL** (total=810): execution:trigger_not_confirmed=804, context_floor=6
- **LIQUIDATION_REVERSAL** (total=13): execution:trigger_not_confirmed=13
- **LIQUIDITY_SWEEP_REVERSAL** (total=6626): execution:trigger_not_confirmed=2989, execution:overextended=2332, setup_compat:regime_STRONG_TREND=1305
- **MA_CROSS_TREND_SHIFT** (total=34): setup_compat:regime_DIRTY_RANGE=14, execution:trigger_not_confirmed=10, setup_compat:regime_CLEAN_RANGE=5, setup_compat:regime_VOLATILE_UNSUITABLE=3, execution:overextended=2
- **MEAN_REVERT** (total=4485): setup_compat:regime_STRONG_TREND=2141, execution:overextended=1301, setup_compat:regime_WEAK_TREND=1043
- **MOVER_AVWAP_SCALP** (total=1428): execution:overextended=1167, execution:trigger_not_confirmed=201, entry_quality=60
- **MOVER_TREND_PULLBACK** (total=21506): execution:trigger_not_confirmed=11636, execution:overextended=9309, entry_quality=561
- **QUIET_COMPRESSION_BREAK** (total=71): execution:trigger_not_confirmed=71
- **RANGE_FADE** (total=1553): setup_compat:regime_STRONG_TREND=715, setup_compat:regime_WEAK_TREND=557, setup_compat:regime_VOLATILE_UNSUITABLE=250, context_edge=30, setup_compat:regime_BREAKOUT_EXPANSION=1
- **TREND_PULLBACK_EMA** (total=3022): setup_compat:regime_CLEAN_RANGE=1526, setup_compat:regime_DIRTY_RANGE=1287, setup_compat:regime_VOLATILE_UNSUITABLE=159, entry_quality=31, execution:overextended=19
- **VOLUME_SURGE_BREAKOUT** (total=36): execution:overextended=36

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 302912 | 54.4% |
| QUIET | 110190 | 19.8% |
| TRENDING_UP | 65412 | 11.8% |
| TRENDING_DOWN | 39499 | 7.1% |
| VOLATILE | 38438 | 6.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **36**
- Average confidence gap to threshold: **10.75** (samples=36) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: DOTUSDT=11, BTWUSDT=9, ASTERUSDT=5, TAOUSDT=3, ADAUSDT=3, FARTCOINUSDT=3, BCHUSDT=1, BTCUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 95 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 49 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 45 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 1 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 6 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 108 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 5 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 91 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 84 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 21 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 79 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1118 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 19 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1448 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 2 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 11 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 28 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 6 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 36 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 1 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 18 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 98 | 56.58 | 63.00 | 6.42 | 20.89 | 19.59 | 18.69 | 0.70 | 11.69 |
| DIVERGENCE_CONTINUATION | kept | 49 | 65.64 | 65.00 | -0.64 | 21.59 | 19.91 | 18.14 | 2.16 | 1.59 |
| FAILED_AUCTION_RECLAIM | filtered | 46 | 49.15 | 63.52 | 14.37 | 19.07 | 19.36 | 20.00 | 3.99 | 14.74 |
| FAILED_AUCTION_RECLAIM | kept | 6 | 70.13 | 65.00 | -5.13 | 20.05 | 18.83 | 20.00 | 2.58 | 2.03 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 113 | 50.28 | 63.10 | 12.82 | 20.39 | 18.90 | 17.13 | 2.27 | 17.48 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 91 | 69.61 | 65.00 | -4.61 | 19.64 | 18.41 | 17.07 | 2.95 | 0.12 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.70 | 65.00 | -1.70 | 21.10 | 18.40 | 15.80 | 0.00 | 4.80 |
| MEAN_REVERT | filtered | 84 | 57.68 | 65.00 | 7.32 | 18.39 | 16.76 | 16.78 | 0.00 | 14.90 |
| MOVER_AVWAP_SCALP | filtered | 21 | 64.17 | 65.00 | 0.83 | 20.16 | 14.71 | 15.80 | 4.50 | 13.07 |
| MOVER_AVWAP_SCALP | kept | 79 | 82.57 | 65.00 | -17.57 | 19.09 | 15.58 | 15.80 | 4.01 | 1.32 |
| MOVER_TREND_PULLBACK | filtered | 1137 | 55.23 | 64.30 | 9.07 | 20.19 | 19.08 | 15.80 | 3.78 | 19.73 |
| MOVER_TREND_PULLBACK | kept | 1448 | 74.94 | 65.00 | -9.94 | 20.87 | 18.38 | 15.80 | 3.86 | 2.26 |
| QUIET_COMPRESSION_BREAK | filtered | 2 | 59.10 | 65.00 | 5.90 | 21.55 | 19.70 | 20.00 | 0.00 | 15.00 |
| QUIET_COMPRESSION_BREAK | kept | 11 | 75.13 | 65.00 | -10.13 | 21.67 | 19.77 | 20.00 | 0.00 | -1.20 |
| SR_FLIP_RETEST | kept | 2 | 69.45 | 65.00 | -4.45 | 21.40 | 20.00 | 17.40 | 2.50 | 3.05 |
| TREND_PULLBACK_EMA | filtered | 34 | 60.06 | 64.18 | 4.12 | 20.18 | 19.53 | 18.08 | 4.37 | 15.81 |
| TREND_PULLBACK_EMA | kept | 36 | 69.98 | 65.00 | -4.98 | 21.56 | 19.62 | 17.25 | 4.46 | 1.06 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 59.50 | 61.00 | 1.50 | 15.90 | 16.70 | 20.00 | 4.50 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 18 | 75.53 | 65.00 | -10.53 | 18.70 | 17.44 | 20.00 | 4.67 | 0.05 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 98 | 56.58 | 21.82 | 11.16 | 6.00 | 14.13 | 5.65 | 8.81 | 0.70 |
| DIVERGENCE_CONTINUATION | kept | 49 | 65.64 | 24.84 | 8.82 | 5.20 | 13.90 | 4.39 | 9.09 | 2.16 |
| FAILED_AUCTION_RECLAIM | filtered | 46 | 49.15 | 23.83 | 17.91 | 3.91 | 10.54 | 5.27 | 3.65 | 3.99 |
| FAILED_AUCTION_RECLAIM | kept | 6 | 70.13 | 21.00 | 16.67 | 4.50 | 13.33 | 7.25 | 6.83 | 2.58 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 113 | 50.28 | 24.82 | 14.07 | 4.04 | 12.78 | 6.08 | 3.71 | 2.27 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 91 | 69.61 | 24.91 | 14.04 | 5.24 | 12.36 | 6.29 | 3.93 | 2.95 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.70 | 25.00 | 14.00 | 3.00 | 11.00 | 8.50 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 84 | 57.68 | 21.48 | 18.00 | 12.82 | 12.27 | 5.00 | 3.01 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 21 | 64.17 | 17.00 | 18.00 | 9.43 | 14.43 | 5.00 | 8.89 | 4.50 |
| MOVER_AVWAP_SCALP | kept | 79 | 82.57 | 20.95 | 18.03 | 12.89 | 13.91 | 6.49 | 7.79 | 4.01 |
| MOVER_TREND_PULLBACK | filtered | 1137 | 55.23 | 18.12 | 18.00 | 7.68 | 12.63 | 6.10 | 8.68 | 3.78 |
| MOVER_TREND_PULLBACK | kept | 1448 | 74.94 | 19.54 | 18.08 | 7.61 | 13.06 | 6.49 | 8.63 | 3.86 |
| QUIET_COMPRESSION_BREAK | filtered | 2 | 59.10 | 17.00 | 18.00 | 10.50 | 14.00 | 7.25 | 7.35 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 11 | 75.13 | 19.18 | 17.64 | 12.27 | 14.27 | 6.77 | 6.52 | 0.00 |
| SR_FLIP_RETEST | kept | 2 | 69.45 | 25.00 | 18.00 | 3.00 | 14.00 | 5.00 | 5.00 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 34 | 60.06 | 17.00 | 18.00 | 7.50 | 14.35 | 5.82 | 8.82 | 4.37 |
| TREND_PULLBACK_EMA | kept | 36 | 69.98 | 8.78 | 18.00 | 7.54 | 14.17 | 8.89 | 9.62 | 4.46 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 59.50 | 17.00 | 18.00 | 12.00 | 11.00 | 5.00 | 10.00 | 4.50 |
| VOLUME_SURGE_BREAKOUT | kept | 18 | 75.53 | 20.56 | 14.00 | 12.00 | 11.17 | 4.86 | 10.00 | 4.67 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 98 | 56.58 | 0.00 | 0.00 | 0.93 | 0.00 | 3.18 | 0.00 | 0.00 | 0.00 | **4.11** |
| DIVERGENCE_CONTINUATION | kept | 49 | 65.64 | 0.00 | 0.00 | 0.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.16** |
| FAILED_AUCTION_RECLAIM | filtered | 46 | 49.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.47 | 0.00 | 0.00 | 0.00 | **0.47** |
| FAILED_AUCTION_RECLAIM | kept | 6 | 70.13 | 0.00 | 0.00 | 1.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.33** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 113 | 50.28 | 0.00 | 0.00 | 2.78 | 0.00 | 0.38 | 0.00 | 0.00 | 0.00 | **3.16** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 91 | 69.61 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.70 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| MEAN_REVERT | filtered | 84 | 57.68 | 0.00 | 0.00 | 0.00 | 0.00 | 8.71 | 0.71 | 0.00 | 0.00 | **9.42** |
| MOVER_AVWAP_SCALP | filtered | 21 | 64.17 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MOVER_AVWAP_SCALP | kept | 79 | 82.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.39 | 0.00 | 0.00 | 0.71 | **1.10** |
| MOVER_TREND_PULLBACK | filtered | 1137 | 55.23 | 0.41 | 0.00 | 0.06 | 0.00 | 0.18 | 0.11 | 0.00 | 0.00 | **0.76** |
| MOVER_TREND_PULLBACK | kept | 1448 | 74.94 | 0.02 | 0.00 | 1.01 | 0.00 | 0.02 | 0.01 | 0.00 | 0.00 | **1.06** |
| QUIET_COMPRESSION_BREAK | filtered | 2 | 59.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 9.00 | 0.00 | 0.00 | **9.00** |
| QUIET_COMPRESSION_BREAK | kept | 11 | 75.13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 2 | 69.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 34 | 60.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 36 | 69.98 | 0.00 | 0.00 | 0.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.44** |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 59.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 18 | 75.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **101614 held of 259486 seen** across 21 strategies; 2325 cells past the sample floor; **1020 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 36377 | 538/35839/0 | 44% | -0.15 | LONDON/MARKUP/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.23R) | LONDON/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.15R) |
| MOVER_AVWAP_SCALP | 12513 | 160/12353/0 | 41% | -0.23 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | OVERLAP/MARKUP/EXPANDED/BTC_FALLING (-1.32R) |
| FAILED_AUCTION_RECLAIM | 7963 | 97/7866/0 | 41% | -0.19 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 6247 | 32/6215/0 | 50% | -0.03 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 5420 | 0/0/5420 | 42% | -0.10 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (+0.56R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-0.83R) |
| TREND_PULLBACK_EMA | 5112 | 24/5088/0 | 45% | -0.15 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| SHADOW_RANGE_FADE | 4488 | 0/0/4488 | 38% | -0.07 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.66R) | NY/QUIET/COMPRESSED/BTC_FALLING (-0.98R) |
| QUIET_COMPRESSION_BREAK | 4279 | 258/4021/0 | 43% | -0.16 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+0.65R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4189 | 0/0/4189 | 35% | -0.40 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.13R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3365 | 2/3363/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 3120 | 57/3063/0 | 36% | -0.38 | NY/RANGE/NORMAL/BTC_FALLING (+1.64R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 2055 | 20/2035/0 | 48% | -0.16 | ASIA/RANGE/EXPANDED/BTC_NEUTRAL/ALTCOIN (+1.17R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 1797 | 2/1795/0 | 34% | -0.40 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 1600 | 0/1600/0 | 42% | +0.01 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| SR_FLIP_RETEST | 1022 | 10/1012/0 | 49% | -0.20 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.79R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 722 | 0/0/722 | 54% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.16R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.47R) |
| RANGE_FADE | 717 | 0/717/0 | 41% | -0.37 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 352 | 29/323/0 | 41% | -0.16 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.03R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDATION_REVERSAL | 212 | 0/212/0 | 10% | -1.02 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 58 | 6/52/0 | 41% | -0.11 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 6 | 0/6/0 | 67% | +0.42 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 142 | 28% / -0.54R | 142 | 48% / -0.18R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 407 | 45% / -0.20R | 407 | 54% / -0.04R | +0.16 | **ATR** |
| MOVER_AVWAP_SCALP | 983 | 44% / -0.19R | 983 | 50% / -0.08R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 367 | 44% / -0.32R | 367 | 46% / -0.22R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 120 | 48% / -0.27R | 120 | 50% / -0.17R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 5534 | 51% / -0.08R | 5534 | 55% / -0.00R | +0.08 | **ATR** |
| FAILED_AUCTION_RECLAIM | 706 | 43% / -0.17R | 706 | 45% / -0.10R | +0.08 | **ATR** |
| BREAKDOWN_SHORT | 30 | 33% / -0.18R | 30 | 37% / -0.12R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 599 | 50% / -0.21R | 599 | 54% / -0.15R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 19 | 37% / -0.21R | 19 | 37% / -0.16R | +0.05 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 94 | 39% / -0.09R | 94 | 47% / -0.06R | +0.03 | **ATR** |
| RANGE_FADE | 35 | 40% / -0.19R | 35 | 43% / -0.22R | -0.03 | **FIXED** |
| DIVERGENCE_CONTINUATION | 596 | 51% / -0.07R | 596 | 56% / -0.05R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 733 | 45% / -0.16R | 733 | 45% / -0.17R | -0.01 | **FIXED** |
| MEAN_REVERT | 142 | 52% / -0.09R | 142 | 50% / -0.09R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 14 | 29% / -0.51R | 14 | 57% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8074 | 30% | -0.18R | 307 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 983 | 48% | -0.08R | 189 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 60 | 50% | -0.06R | 47 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 139 | 37% / -0.30R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 706 | 36% / -0.09R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 7141 | 37% / -0.13R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1294 | 35% / -0.07R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 559 | 36% / -0.11R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 671 | 40% / +0.01R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 550 | 38% / -0.05R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 592 | 42% / -0.17R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 127 | 28% / -0.38R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 182 | 31% / -0.57R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 116 | 53% / +0.05R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 52 | 37% / -0.17R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 27 | 37% / +0.17R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 122 | 35% / -0.38R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 27 | 15% / -0.50R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 19 | 42% / -0.05R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.05R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×464]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 263/6) (sustained 263 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.70R (bound 0.3) (streak 263/6) (sustained 263 cycles)
- **ALERT** `tuned_variants` — 42 non-stamps — atr_arm_uncomputable=42 (seen=2405 stamped=280 skipped=2083) (streak 209/6) (sustained 209 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 263/3) (sustained 263 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 35068274 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 263/3) | 263 |
| ai_governor_live_arms | ok | 39 arms current, none stalled; covering 483/483 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +2 / upstream +2 | 0 |
| atr_trail_live_arms | ok | 79 arms current, none stalled; covering 1073/1073 signals (100%) | 0 |
| auto_dispatch | ok | 39 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: mode:off=39, mode:paper=39. No user is on live. | 0 |
| btc_reference | ok | BTC ref 77408.50 | 0 |
| candle_coverage | ok | 87/87 symbols with ≥20 15m candles, 87/87 updated within 45m [fresh=87; 76 Tier-1 futures + 11 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 469 dup bars, 0 undedupable; ws 0 out-of-order, 153 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +22 / upstream +23 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1148/1165 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 1 of 91 open dark rows are not being advanced (worst: STARUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 1/120) | 1 |
| dark_sar_arms | ok | no open arms; covering 1140/1157 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 6997807 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.70R (bound 0.3) (streak 263/6) | 263 |
| emission_controller | ok | last cycle 1332s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×464]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 263/6) | 263 |
| entry_quality_effective | ok | 2294 evaluated, 728 suppressed, 717 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 564 incomplete, 1 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +11 / upstream +143 | 0 |
| indicator_cache_key | ok | 78811 frozen value(s) avoided; 433465 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.17R over n=2035 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +143 but output +0 (streak 2/72) | 2 |
| mover_admission_metadata | ok | 897 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 11 held, 11 with scan counts, 11 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 7 locked / 7 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 1511527 evicted (sampled: execution:trigger_not_confirmed 400/553142, execution:overextended 400/497961, setup_compat:regime_STRONG_TREND 400/224964) | 0 |
| price_action_lane | ok | 590844 evaluated, 623 emitted; layer1 623 stamped / 0 blind; cooldown=80180, delta_opposed=50643, no_footprint=221185, no_opposing_target=1982, no_sweep=192279, rr_below_floor=43952 | 0 |
| promoted_pair_integrity | ok | 11/11 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.37R over n=717 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +44 / upstream +143 | 0 |
| sar_alignment_crosscheck | ok | 209/9780 disagreed (2.1%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +143 | 0 |
| sar_hold_arm | ok | 1816 held arms settled, 184 unscored, 78 still walking (71 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 14/50 unfetchable (28%); top cause: gap or duplicate bar in the 15m window; symbols: DOGEUSDT, INJUSDT, LINKUSDT, ONEUSDT, OPUSDT +2 more | 0 |
| sar_live_arms | ok | 78 arms current, none stalled; covering 1073/1073 signals (100%) | 0 |
| sar_refresh_budget | ok | 7 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 450 records await one (36 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| scan_cycle | ok | last 10.26s, worst 76.79s over 7232 lifetime cycles; lifetime 13 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 3.21s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 285385 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 5m ago | 0 |
| snapshot_writer | ok | last cycle 23s ago (7.87s to run, worst 65.76s), 264 overrun(s) of 5193 cycles, TTL 900s; slowest tickers=4.36s, engine_state=2.33s, positions_diag=2.24s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +5 / upstream +143 | 0 |
| structural_snap | ok | 5238/5238 measured, 21 blind, 0 levels moved (refusals: redetect_cooldown=319) | 0 |
| structural_veto_lane | ok | 549 stamped; 0 with no readable level book, 2 with clear air ahead, 377 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +143 / upstream +23 | 0 |
| tuned_variants | violating | 42 non-stamps — atr_arm_uncomputable=42 (seen=2405 stamped=280 skipped=2083) (streak 209/6) | 209 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 1 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2590867`
- `Path funnel` emissions: `68`
- `Regime distribution` emissions: `68`
- `QUIET_SCALP_BLOCK` events: `36`
- `confidence_gate` events: `3277`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **1**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_depth | 1 | 7351 | 7351 | 7351 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[absent=1508, present=439875] state[empty=1508, populated=439875] buckets[many=439875, none=1508] sources[none] quality[none]
- funding_rate: presence[absent=50238, present=391145] state[empty=50238, populated=391145] buckets[few=391145, none=50238] sources[none] quality[none]
- liquidation_clusters: presence[absent=235639, present=205744] state[empty=235639, populated=205744] buckets[few=164118, none=235639, some=41626] sources[none] quality[none]
- oi_snapshot: presence[absent=50238, present=391145] state[empty=50238, populated=391145] buckets[few=241, many=390216, none=50238, some=688] sources[none] quality[none]
- order_book: presence[absent=121835, present=319548] state[populated=319548, unavailable=121835] buckets[few=319548, none=121835] sources[book_ticker=319548, unavailable=121835] quality[none=121835, top_of_book_only=319548]
- orderblocks: presence[absent=441383] state[empty=441383] buckets[none=441383] sources[measured_dark=441383] quality[none]
- recent_ticks: presence[present=441383] state[populated=441383] buckets[many=441383] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.066391944885254` sec
- Median create→first breach: `9529.97118806839` sec
- Median create→terminal: `9529.971227169037` sec
- Median first breach→terminal: `6.914138793945312e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.7999999999999924 | 1.6611651078916811 | 0.4815896964121387 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 4 | 4 | 1.6471930757486346 | 1.8909752453040372 | 0.8180046129154566 | 0 | 4 |
| LIQUIDITY_SWEEP_REVERSAL | 5 | 5 | 1.1012270104093578 | 1.2705487381338278 | 0.866733386416039 | 0 | 5 |
| MOVER_AVWAP_SCALP | 4 | 4 | 2.3778663986149233 | 2.5972085443749755 | 0.896826883874348 | 1 | 3 |
| MOVER_TREND_PULLBACK | 14 | 14 | 2.8329395017127235 | 2.0883168705746953 | 1.1519392987259227 | 8 | 6 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 0.9899673971618358 | 1.0877468782241317 | 0.9092299714482022 | 0 | 9 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7146 | 409.45257592201233 | 409.8319778442383 |
| FAILED_AUCTION_RECLAIM | 4 | 4 | 50.0 | 25.0 | 50.0 | 0.0 | 0.1764 | 5657.773844361305 | 5657.773887038231 |
| LIQUIDITY_SWEEP_REVERSAL | 5 | 5 | 20.0 | 60.0 | 20.0 | 0.0 | -0.407 | 15369.146711826324 | 15369.146780967712 |
| MOVER_AVWAP_SCALP | 4 | 4 | 25.0 | 50.0 | 25.0 | 0.0 | -0.1463 | 11245.505788564682 | 11245.632820487022 |
| MOVER_TREND_PULLBACK | 14 | 14 | 57.1 | 14.3 | 57.1 | 0.0 | 1.1901 | 13899.305478811264 | 13899.592797875404 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 22.2 | 66.7 | 22.2 | 0.0 | -0.334 | 9529.97118806839 | 9529.971227169037 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1385 | 2 | 1359 | 0.0 | 0.0 | None | None | 26 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3218 | 11 | 3085 | 0.0 | 0.0 | None | None | 133 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-84`
- Gating Δ: `20715`
- No-generation Δ: `-14587`
- Fast failures Δ: `-1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.3096, "current_avg_pnl": 0.1764, "current_win_rate": 50.0, "previous_avg_pnl": -0.1332, "previous_win_rate": 16.7, "win_rate_delta": 33.3}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.2013, "current_avg_pnl": -0.407, "current_win_rate": 20.0, "previous_avg_pnl": -0.6083, "previous_win_rate": 0.0, "win_rate_delta": 20.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 1.1449, "current_avg_pnl": -0.1463, "current_win_rate": 25.0, "previous_avg_pnl": -1.2912, "previous_win_rate": 0.0, "win_rate_delta": 25.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.512, "current_avg_pnl": 1.1901, "current_win_rate": 57.1, "previous_avg_pnl": 1.7021, "previous_win_rate": 50.0, "win_rate_delta": 7.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.1876, "current_avg_pnl": -0.334, "current_win_rate": 22.2, "previous_avg_pnl": -0.1464, "previous_win_rate": 20.0, "win_rate_delta": 2.2}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": -48, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": -54, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **MOVER_TREND_PULLBACK**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
