# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: MOVER_AVWAP_SCALP
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `12` sec (warning=False)
- Latest performance record age: `1551` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 107 | 107 | 107 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6434 | 6434 | 6071 | 6 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 55461 | 55451 | 35 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 50875 | 50875 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 50600 | 49394 | 1469 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 50906 | 50298 | 669 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 53404 | 53162 | 267 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 46603 | 46622 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 50972 | 50994 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 51007 | 49309 | 2288 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 58621 | 61956 | 671 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 55490 | 51135 | 7426 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 53058 | 53058 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 50878 | 50891 | 7 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 50574 | 50414 | 182 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 51602 | 50958 | 1057 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 50203 | 50468 | 74 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 43887 | 41851 | 2189 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 44048 | 43762 | 345 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 55425 | 55429 | 28 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 46622 | 46640 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3709 | 3709 | 3319 | 3 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1122 | 1122 | 869 | 3 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 7 | 7 | 7 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 13662 | 13662 | 13512 | 9 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 19 | 19 | 16 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 6258 | 6258 | 5691 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2256 | 2256 | 1430 | 24 | active-healthy (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 25192 | 25192 | 20114 | 188 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 16 | 16 | 16 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 896 | 896 | 819 | 11 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3468 | 3468 | 3344 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 552 | 552 | 488 | 3 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1733 | 1733 | 1652 | 12 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 310 | 310 | 235 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=55451): breakout_not_found=29688, basic_filters_failed=15181, move_not_fresh=7360, breakout_stale=2166, retest_proximity_failed=886, volume_spike_missing=168, ema_alignment_reject=1, move_exhausted=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=50875): cls_disabled_merged_into_lsr=50875
- **EVAL::DIVERGENCE_CONTINUATION** (total=49394): cvd_divergence_failed=21596, basic_filters_failed=12451, h1_trend_not_aligned=11499, ema_alignment_reject=3135, retest_proximity_failed=436, missing_fvg_or_orderblock=264, missing_cvd=13
- **EVAL::FAILED_AUCTION_RECLAIM** (total=50298): auction_not_detected=32563, basic_filters_failed=11708, reclaim_hold_failed=2278, regime_blocked=2014, tail_too_small=1731, rsi_reject=4
- **EVAL::FUNDING_EXTREME** (total=53162): funding_not_extreme=35883, basic_filters_failed=13444, ema_alignment_reject=2233, rsi_reject=1061, momentum_reject=249, cvd_divergence_failed=226, missing_funding_rate=36, missing_fvg_or_orderblock=30
- **EVAL::LIQUIDATION_REVERSAL** (total=46622): cascade_threshold_not_met=32939, basic_filters_failed=13213, cvd_divergence_failed=262, rsi_reject=204, missing_fvg_or_orderblock=3, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=50994): no_ma_cross=37447, basic_filters_failed=12466, ma_cross_cooldown=604, ma_cross_htf_misaligned=462, ma_cross_htf_unconfirmed=15
- **EVAL::MEAN_REVERT** (total=49309): no_extension=40118, basic_filters_failed=9191
- **EVAL::MOVER_AVWAP_SCALP** (total=61956): no_avwap_tag=22708, no_mover_leg=17657, basic_filters_failed=15401, avwap_slope_against=3419, avwap_reclaim_no_volume=1581, no_avwap_reclaim=1134, anchor_too_recent=56
- **EVAL::MOVER_TREND_PULLBACK** (total=51135): mover_run_too_small=25691, basic_filters_failed=15290, no_reclaim=8483, no_pullback_tag=1671
- **EVAL::OPENING_RANGE_BREAKOUT** (total=53058): feature_disabled=53058
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=50891): regime_blocked=29624, breakout_not_found=15513, basic_filters_failed=3609, adx_reject=2088, ema_alignment_reject=57
- **EVAL::QUIET_COMPRESSION_BREAK** (total=50414): regime_blocked=23160, compression_not_detected=14505, basic_filters_failed=8091, breakout_not_detected=4347, volume_confirmation_failed=281, rsi_reject=29, missing_fvg_or_orderblock=1
- **EVAL::RANGE_FADE** (total=50958): no_range_edge=41765, basic_filters_failed=9193
- **EVAL::SR_FLIP_RETEST** (total=50468): flip_close_not_confirmed=32965, basic_filters_failed=11694, regime_blocked=2002, long_break_volume_thin=1118, h1_break_not_confirmed=983, retest_out_of_zone=827, reclaim_hold_failed=612, long_acceptance_not_held=133, ema_alignment_reject=66, missing_fvg_or_orderblock=30, wick_quality_failed=20, whipsaw_flip=18
- **EVAL::STANDARD** (total=41851): momentum_reject=14451, adx_reject=10093, basic_filters_failed=6585, ema_alignment_reject=3470, sweeps_not_detected=3401, macd_reject=3009, htf_poi_unanchored=777, rsi_reject=35, invalid_sl_geometry=25, mtf_reject=5
- **EVAL::TREND_PULLBACK** (total=43762): h1_trend_not_aligned=15222, ema_alignment_reject=7753, basic_filters_failed=5616, h1_pullback_not_confirmed=5332, ema_not_tested_prev=3207, no_ema_reclaim_close=2841, rsi_reject=1466, body_conviction_fail=1336, prev_already_below_emas=272, prev_already_above_emas=247, no_prev_low_break=193, no_prev_high_break=137, momentum_flat=69, momentum_reject=39, missing_fvg_or_orderblock=19, ema21_not_tagged=13
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=55429): breakout_not_found=30193, basic_filters_failed=15180, move_not_fresh=6576, breakout_stale=2411, retest_proximity_failed=904, volume_spike_missing=155, missing_fvg_or_orderblock=7, move_exhausted=3
- **EVAL::WHALE_MOMENTUM** (total=46640): momentum_reject=34814, recent_ticks_insufficient=7900, basic_filters_failed=3926

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=9): execution:overextended=9
- **DIVERGENCE_CONTINUATION** (total=152): setup_compat:regime_VOLATILE_UNSUITABLE=138, setup_compat:regime_BREAKOUT_EXPANSION=14
- **FAILED_AUCTION_RECLAIM** (total=1318): execution:overextended=691, setup_compat:regime_STRONG_TREND=547, context_floor=72, setup_compat:regime_VOLATILE_UNSUITABLE=8
- **FUNDING_EXTREME_SIGNAL** (total=930): execution:trigger_not_confirmed=928, context_floor=2
- **LIQUIDATION_REVERSAL** (total=7): execution:trigger_not_confirmed=7
- **LIQUIDITY_SWEEP_REVERSAL** (total=3387): execution:trigger_not_confirmed=1471, setup_compat:regime_STRONG_TREND=1146, execution:overextended=770
- **MA_CROSS_TREND_SHIFT** (total=20): setup_compat:regime_DIRTY_RANGE=9, setup_compat:regime_CLEAN_RANGE=6, execution:trigger_not_confirmed=5
- **MEAN_REVERT** (total=4517): setup_compat:regime_WEAK_TREND=2291, setup_compat:regime_STRONG_TREND=2054, execution:overextended=172
- **MOVER_AVWAP_SCALP** (total=1287): execution:overextended=937, execution:trigger_not_confirmed=237, entry_quality=113
- **MOVER_TREND_PULLBACK** (total=9676): execution:trigger_not_confirmed=5476, execution:overextended=3622, entry_quality=578
- **RANGE_FADE** (total=2404): setup_compat:regime_STRONG_TREND=988, setup_compat:regime_WEAK_TREND=972, execution:overextended=263, setup_compat:regime_VOLATILE_UNSUITABLE=96, context_edge=62, setup_compat:regime_BREAKOUT_EXPANSION=23
- **TREND_PULLBACK_EMA** (total=1289): setup_compat:regime_CLEAN_RANGE=911, setup_compat:regime_DIRTY_RANGE=336, setup_compat:regime_VOLATILE_UNSUITABLE=34, entry_quality=8
- **VOLUME_SURGE_BREAKOUT** (total=68): execution:overextended=68

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 114536 | 32.7% |
| QUIET | 77254 | 22.1% |
| TRENDING_DOWN | 69387 | 19.8% |
| TRENDING_UP | 68088 | 19.5% |
| VOLATILE | 20770 | 5.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **107**
- Average confidence gap to threshold: **13.12** (samples=107) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: 1000PEPEUSDT=30, FETUSDT=23, DOGEUSDT=11, BTWUSDT=7, TRXUSDT=6, ARBUSDT=5, DOTUSDT=4, NEARUSDT=3, LITUSDT=3, ENAUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 94 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 23 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 77 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 42 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 5 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 31 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 32 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 5 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 20 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 254 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 7 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 3 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 124 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 853 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 35 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1368 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 14 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 13 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 13 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 3 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 10 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 24 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 44 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 13 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 94 | 49.42 | 63.88 | 14.46 | 20.23 | 19.58 | 18.53 | 0.81 | 18.08 |
| DIVERGENCE_CONTINUATION | kept | 23 | 64.60 | 65.00 | 0.40 | 20.36 | 19.20 | 19.04 | 2.78 | 9.82 |
| FAILED_AUCTION_RECLAIM | filtered | 119 | 52.49 | 64.07 | 11.58 | 22.09 | 19.38 | 20.00 | 2.83 | 11.82 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 71.42 | 65.00 | -6.42 | 22.52 | 19.00 | 20.00 | 2.40 | 8.34 |
| FUNDING_EXTREME_SIGNAL | filtered | 31 | 55.08 | 65.00 | 9.92 | 21.10 | 17.82 | 16.01 | 1.97 | 11.25 |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 68.37 | 65.00 | -3.37 | 19.00 | 16.00 | 17.00 | 2.67 | -1.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 37 | 59.69 | 65.00 | 5.31 | 21.47 | 19.07 | 17.41 | 2.54 | 11.08 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 20 | 68.96 | 65.00 | -3.96 | 20.63 | 18.61 | 17.32 | 1.55 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 78.50 | 65.00 | -13.50 | 21.90 | 20.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 1 | 51.10 | 65.00 | 13.90 | 23.90 | 18.70 | 14.20 | 0.00 | 21.60 |
| MOVER_AVWAP_SCALP | filtered | 264 | 49.21 | 63.77 | 14.56 | 20.54 | 14.86 | 15.80 | 4.47 | 17.52 |
| MOVER_AVWAP_SCALP | kept | 124 | 81.66 | 65.00 | -16.66 | 20.58 | 15.97 | 15.80 | 4.55 | 2.01 |
| MOVER_TREND_PULLBACK | filtered | 888 | 54.39 | 63.70 | 9.31 | 19.75 | 18.22 | 15.80 | 3.89 | 16.55 |
| MOVER_TREND_PULLBACK | kept | 1368 | 76.99 | 65.00 | -11.99 | 19.86 | 18.25 | 15.80 | 4.33 | 1.55 |
| QUIET_COMPRESSION_BREAK | filtered | 27 | 55.67 | 63.52 | 7.85 | 21.54 | 19.29 | 20.00 | 0.00 | 5.56 |
| QUIET_COMPRESSION_BREAK | kept | 13 | 73.85 | 65.00 | -8.85 | 21.85 | 19.26 | 20.00 | 0.00 | 3.02 |
| SR_FLIP_RETEST | kept | 3 | 70.33 | 65.00 | -5.33 | 20.53 | 20.00 | 18.93 | 2.33 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 13 | 58.95 | 65.00 | 6.05 | 19.99 | 19.58 | 19.94 | 4.38 | 7.73 |
| TREND_PULLBACK_EMA | kept | 24 | 78.79 | 65.00 | -13.79 | 20.64 | 19.95 | 17.61 | 4.75 | 0.46 |
| VOLUME_SURGE_BREAKOUT | filtered | 44 | 57.58 | 65.00 | 7.42 | 19.38 | 17.48 | 20.00 | 4.12 | 5.22 |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 78.99 | 65.00 | -13.99 | 20.71 | 19.83 | 20.00 | 4.23 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 94 | 49.42 | 22.28 | 15.55 | 4.50 | 12.11 | 5.45 | 8.24 | 0.81 |
| DIVERGENCE_CONTINUATION | kept | 23 | 64.60 | 24.65 | 10.26 | 9.13 | 13.39 | 5.22 | 9.11 | 2.78 |
| FAILED_AUCTION_RECLAIM | filtered | 119 | 52.49 | 19.45 | 15.88 | 10.39 | 10.76 | 6.77 | 6.94 | 2.83 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 71.42 | 21.80 | 15.60 | 11.40 | 14.20 | 7.10 | 7.26 | 2.40 |
| FUNDING_EXTREME_SIGNAL | filtered | 31 | 55.08 | 22.94 | 13.81 | 5.81 | 10.29 | 9.32 | 7.53 | 1.97 |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 68.37 | 22.33 | 11.33 | 6.00 | 10.33 | 7.17 | 8.53 | 2.67 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 37 | 59.69 | 24.35 | 14.00 | 7.22 | 10.62 | 7.86 | 4.23 | 2.54 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 20 | 68.96 | 19.90 | 15.50 | 7.95 | 11.35 | 5.58 | 7.13 | 1.55 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 78.50 | 25.00 | 14.00 | 9.00 | 14.00 | 8.50 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 1 | 51.10 | 17.00 | 18.00 | 12.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 264 | 49.21 | 19.63 | 18.01 | 11.55 | 13.27 | 5.94 | 5.76 | 4.47 |
| MOVER_AVWAP_SCALP | kept | 124 | 81.66 | 19.82 | 18.26 | 13.04 | 13.98 | 6.75 | 7.81 | 4.55 |
| MOVER_TREND_PULLBACK | filtered | 888 | 54.39 | 18.25 | 18.00 | 7.90 | 12.02 | 5.73 | 8.62 | 3.89 |
| MOVER_TREND_PULLBACK | kept | 1368 | 76.99 | 19.52 | 18.03 | 8.18 | 12.89 | 7.00 | 8.75 | 4.33 |
| QUIET_COMPRESSION_BREAK | filtered | 27 | 55.67 | 19.07 | 16.07 | 11.44 | 14.89 | 6.72 | 6.50 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 13 | 73.85 | 20.08 | 17.38 | 11.54 | 14.23 | 7.42 | 6.68 | 0.00 |
| SR_FLIP_RETEST | kept | 3 | 70.33 | 22.33 | 18.00 | 3.00 | 12.67 | 6.00 | 7.00 | 2.33 |
| TREND_PULLBACK_EMA | filtered | 13 | 58.95 | 17.00 | 18.00 | 7.50 | 14.23 | 6.62 | 7.26 | 4.38 |
| TREND_PULLBACK_EMA | kept | 24 | 78.79 | 20.04 | 18.00 | 7.56 | 12.25 | 7.56 | 9.46 | 4.75 |
| VOLUME_SURGE_BREAKOUT | filtered | 44 | 57.58 | 18.64 | 17.82 | 12.00 | 13.93 | 5.00 | 6.29 | 4.12 |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 78.99 | 18.23 | 14.00 | 15.00 | 14.00 | 4.23 | 9.30 | 4.23 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 94 | 49.42 | 0.00 | 0.00 | 2.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.20** |
| DIVERGENCE_CONTINUATION | kept | 23 | 64.60 | 0.00 | 0.00 | 1.95 | 0.00 | 5.22 | 0.00 | 0.00 | 0.00 | **7.17** |
| FAILED_AUCTION_RECLAIM | filtered | 119 | 52.49 | 0.00 | 0.00 | 3.15 | 0.00 | 3.51 | 0.00 | 0.00 | 0.00 | **6.66** |
| FAILED_AUCTION_RECLAIM | kept | 5 | 71.42 | 0.00 | 0.00 | 3.20 | 0.00 | 1.44 | 0.00 | 0.00 | 0.00 | **4.64** |
| FUNDING_EXTREME_SIGNAL | filtered | 31 | 55.08 | 0.00 | 0.00 | 8.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.67** |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 68.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 37 | 59.69 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 20 | 68.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 78.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 1 | 51.10 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| MOVER_AVWAP_SCALP | filtered | 264 | 49.21 | 0.00 | 0.00 | 0.52 | 0.00 | 3.49 | 0.00 | 0.00 | 1.65 | **5.66** |
| MOVER_AVWAP_SCALP | kept | 124 | 81.66 | 0.00 | 0.00 | 0.71 | 0.00 | 0.23 | 0.00 | 0.00 | 0.29 | **1.23** |
| MOVER_TREND_PULLBACK | filtered | 888 | 54.39 | 0.00 | 0.00 | 1.43 | 0.00 | 0.23 | 0.00 | 0.00 | 0.03 | **1.69** |
| MOVER_TREND_PULLBACK | kept | 1368 | 76.99 | 0.00 | 0.00 | 0.89 | 0.00 | 0.52 | 0.00 | 0.00 | 0.01 | **1.42** |
| QUIET_COMPRESSION_BREAK | filtered | 27 | 55.67 | 0.00 | 0.00 | 0.59 | 0.00 | 0.16 | 0.00 | 0.00 | 1.20 | **1.95** |
| QUIET_COMPRESSION_BREAK | kept | 13 | 73.85 | 0.00 | 0.00 | 1.23 | 0.00 | 0.66 | 0.00 | 0.00 | 0.00 | **1.89** |
| SR_FLIP_RETEST | kept | 3 | 70.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 13 | 58.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 24 | 78.79 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 44 | 57.58 | 0.00 | 0.00 | 1.64 | 0.00 | 0.00 | 0.00 | 0.00 | 1.06 | **2.70** |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 78.99 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **94865 held of 234900 seen** across 21 strategies; 2140 cells past the sample floor; **945 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 35417 | 555/34862/0 | 44% | -0.16 | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_FALLING/MAJOR (+1.18R) | ASIA/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.16R) |
| MOVER_AVWAP_SCALP | 11856 | 142/11714/0 | 39% | -0.26 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 7151 | 81/7070/0 | 42% | -0.17 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 5657 | 26/5631/0 | 54% | +0.05 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | OVERLAP/MARKDOWN/CASCADE/BTC_RISING (-1.17R) |
| SHADOW_MEAN_REVERT | 5179 | 0/0/5179 | 43% | -0.09 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (+0.56R) | LONDON/QUIET/NORMAL/BTC_NEUTRAL (-0.98R) |
| TREND_PULLBACK_EMA | 4655 | 24/4631/0 | 47% | -0.11 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| SHADOW_RANGE_FADE | 4260 | 0/0/4260 | 38% | -0.05 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.66R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.04R) |
| QUIET_COMPRESSION_BREAK | 4201 | 225/3976/0 | 45% | -0.13 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+0.83R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 3748 | 0/0/3748 | 35% | -0.38 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.13R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-1.03R) |
| WHALE_MOMENTUM | 3253 | 2/3251/0 | 42% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 2482 | 40/2442/0 | 39% | -0.29 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.21R) |
| MEAN_REVERT | 1821 | 20/1801/0 | 48% | -0.18 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR (+1.13R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| VOLUME_SURGE_BREAKOUT | 1392 | 0/1392/0 | 45% | +0.08 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 1332 | 2/1330/0 | 33% | -0.40 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.36R) |
| SR_FLIP_RETEST | 928 | 10/918/0 | 46% | -0.26 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.79R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 635 | 0/0/635 | 56% | -0.01 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.49R) |
| BREAKDOWN_SHORT | 340 | 23/317/0 | 41% | -0.16 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.03R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| RANGE_FADE | 300 | 0/300/0 | 59% | +0.19 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| LIQUIDATION_REVERSAL | 196 | 0/196/0 | 11% | -1.00 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 56 | 6/50/0 | 39% | -0.13 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 6 | 0/6/0 | 67% | +0.42 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 117 | 31% / -0.48R | 117 | 48% / -0.18R | +0.30 | **ATR** |
| TREND_PULLBACK_EMA | 394 | 46% / -0.20R | 394 | 55% / -0.04R | +0.16 | **ATR** |
| RANGE_FADE | 20 | 50% / +0.20R | 20 | 50% / +0.10R | -0.11 | **FIXED** |
| MOVER_AVWAP_SCALP | 910 | 44% / -0.19R | 910 | 50% / -0.09R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 364 | 43% / -0.33R | 364 | 45% / -0.23R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 111 | 50% / -0.26R | 111 | 51% / -0.16R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 640 | 43% / -0.18R | 640 | 45% / -0.09R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 5393 | 50% / -0.09R | 5393 | 55% / -0.01R | +0.09 | **ATR** |
| BREAKDOWN_SHORT | 26 | 31% / -0.18R | 26 | 35% / -0.12R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 19 | 37% / -0.21R | 19 | 37% / -0.16R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 496 | 51% / -0.18R | 496 | 55% / -0.15R | +0.03 | **ATR** |
| DIVERGENCE_CONTINUATION | 567 | 52% / -0.04R | 567 | 58% / -0.03R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 704 | 45% / -0.15R | 704 | 45% / -0.16R | -0.01 | **FIXED** |
| VOLUME_SURGE_BREAKOUT | 84 | 44% / +0.01R | 84 | 52% / -0.00R | -0.01 | **FIXED** |
| MEAN_REVERT | 133 | 53% / -0.09R | 133 | 50% / -0.09R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 13 | 31% / -0.46R | 13 | 54% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 7890 | 30% | -0.17R | 305 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 910 | 47% | -0.09R | 188 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 54 | 56% | -0.02R | 45 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 137 | 36% / -0.30R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 676 | 37% / -0.10R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 6943 | 37% / -0.13R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1173 | 34% / -0.05R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 506 | 36% / -0.11R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 637 | 41% / +0.06R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 522 | 38% / -0.03R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 494 | 45% / -0.10R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 113 | 32% / -0.21R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 154 | 32% / -0.55R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 108 | 53% / +0.04R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 48 | 38% / -0.14R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 18 | 44% / +0.28R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 111 | 35% / -0.37R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 26 | 12% / -0.61R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 17 | 41% / -0.06R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.05R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **6** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×460]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 560/6) (sustained 560 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 8/6) (sustained 8 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.72R (bound 0.3) (streak 560/6) (sustained 560 cycles)
- **ALERT** `tuned_variants` — 349 non-stamps — atr_arm_uncomputable=349 (seen=4851 stamped=653 skipped=3849) (streak 560/6) (sustained 560 cycles)
- **ALERT** `auto_dispatch` — 122 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode:off=122, mode:paper=122) (streak 544/3) (sustained 544 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 560/3) (sustained 560 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 46 fed / 0 quiet / 0 never delivered of 46 subscribed; 275746187 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 560/3) | 560 |
| ai_governor_live_arms | ok | 19 arms current, none stalled; covering 313/313 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +1 / upstream +1 | 0 |
| atr_trail_live_arms | ok | 38 arms current, none stalled; covering 1076/1076 signals (100%) | 0 |
| auto_dispatch | violating | 122 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode:off=122, mode:paper=122) (streak 544/3) | 544 |
| btc_reference | ok | BTC ref 77552.00 | 0 |
| candle_coverage | ok | 80/80 symbols with ≥20 15m candles, 80/80 updated within 45m [fresh=80; 75 Tier-1 futures + 5 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1349 dup bars, 0 undedupable; ws 0 out-of-order, 459 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 6 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +1 / upstream +30 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1332/1349 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 6 of 96 open dark rows are not being advanced (worst: FFUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 25/120) | 25 |
| dark_sar_arms | ok | no open arms; covering 1333/1350 signals (99%) | 0 |
| depth_feed | ok | 46/46 books fresh (stale 0, never 0, thin 0); 57263425 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.72R (bound 0.3) (streak 560/6) | 560 |
| emission_controller | ok | last cycle 663s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×460]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 560/6) | 560 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 8/6) | 8 |
| footprint_bars | ok | 5520 sealed bars over 46 symbols; 1353 incomplete, 9 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +1 / upstream +80 | 0 |
| indicator_cache_key | ok | 196135 frozen value(s) avoided; 969608 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.19R over n=1801 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +15 / upstream +80 | 0 |
| mover_admission_metadata | ok | 897 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 5 held, 5 with scan counts, 5 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3008 rows held, 1387491 evicted (sampled: execution:trigger_not_confirmed 400/506926, execution:overextended 400/459490, setup_compat:regime_STRONG_TREND 400/208271) | 0 |
| price_action_lane | ok | 938750 evaluated, 1265 emitted; layer1 1265 stamped / 0 blind; cooldown=119273, delta_opposed=89012, no_footprint=326722, no_opposing_target=584, no_sweep=319863, rr_below_floor=82031 | 0 |
| promoted_pair_integrity | ok | 5/5 promoted pairs present in universe | 0 |
| range_fade_emission | ok | backlog 0 detections since last progress | 0 |
| range_fade_path | violating | upstream +80 but output +0 (streak 4/72) | 4 |
| sar_alignment_crosscheck | ok | 551/15686 disagreed (3.5%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +80 | 0 |
| sar_hold_arm | ok | 1777 held arms settled, 223 unscored, 37 still walking (31 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 4/18 unfetchable (22%); top cause: gap or duplicate bar in the 15m window; symbols: AINUSDT, FETUSDT | 0 |
| sar_live_arms | ok | 37 arms current, none stalled; covering 1085/1085 signals (100%) | 0 |
| sar_refresh_budget | ok | 8 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 418 records await one (14 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 4/12) | 4 |
| scan_cycle | ok | last 34.31s, worst 174.77s over 11729 lifetime cycles; lifetime 184 over 60s, 21 over 120s (plus 1/0 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.95s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 321572 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 6m ago | 0 |
| snapshot_writer | ok | last cycle 1s ago (6.09s to run, worst 122.51s), 1318 overrun(s) of 10840 cycles, TTL 900s; slowest signals=2.87s, tickers=2.24s, engine_state=0.52s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | violating | upstream +80 but output +0 (streak 1/36) | 1 |
| structural_snap | ok | 5084/5084 measured, 21 blind, 0 levels moved (refusals: redetect_cooldown=543) | 0 |
| structural_veto_lane | ok | 1109 stamped; 0 with no readable level book, 12 with clear air ahead, 861 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +80 / upstream +30 | 0 |
| tuned_variants | violating | 349 non-stamps — atr_arm_uncomputable=349 (seen=4851 stamped=653 skipped=3849) (streak 560/6) | 560 |

Fail-open exception counters (nonzero sites):
- `feature_liveness.probe.footprint_bars`: 1 — last: RuntimeError: deque mutated during iteration
- `llm_client.google`: 4 — last: ClientOSError: [Errno 32] Broken pipe

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1589591`
- `Path funnel` emissions: `44`
- `Regime distribution` emissions: `44`
- `QUIET_SCALP_BLOCK` events: `107`
- `confidence_gate` events: `3115`
- `free_channel_post` events: `50`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **37**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 3 | 5496 | 5496 | 10530 | 0 |
| futures_aggtrade | 13 | 8911 | 12332 | 18076 | 0 |
| futures_depth | 11 | 3898 | 8801 | 10842 | 0 |
| futures_liq | 1 | 12577 | 12577 | 12577 | 0 |
| futures_mover | 9 | 7952 | 9320 | 10023 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **50**

| Source | Count |
|---|---:|
| signal_close | 46 |
| regime_shift | 3 |
| signal_highlight | 1 |

- By severity: HIGH=50

## Dependency readiness
- cvd: presence[absent=32, present=288882] state[empty=32, populated=288882] buckets[many=288882, none=32] sources[none] quality[none]
- funding_rate: presence[absent=11351, present=277563] state[empty=11351, populated=277563] buckets[few=277563, none=11351] sources[none] quality[none]
- liquidation_clusters: presence[absent=155238, present=133676] state[empty=155238, populated=133676] buckets[few=111189, none=155238, some=22487] sources[none] quality[none]
- oi_snapshot: presence[absent=11350, present=277564] state[empty=11350, populated=277564] buckets[few=209, many=276137, none=11350, some=1218] sources[none] quality[none]
- order_book: presence[absent=90294, present=198620] state[populated=198620, unavailable=90294] buckets[few=198620, none=90294] sources[book_ticker=198620, unavailable=90294] quality[none=90294, top_of_book_only=198620]
- orderblocks: presence[absent=288914] state[empty=288914] buckets[none=288914] sources[measured_dark=288914] quality[none]
- recent_ticks: presence[present=288914] state[populated=288914] buckets[many=288914] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.992604494094849` sec
- Median create→first breach: `4578.131198525429` sec
- Median create→terminal: `4581.013382434845` sec
- Median first breach→terminal: `3.3163360357284546` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.2}, "under_180s": {"count": 1, "pct": 2.2}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.7999999999999943 | 0.8657077288746826 | 0.9240994082840168 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 1.1621644710219827 | 1.158213111820505 | 1.003411599438092 | 0 | 0 |
| MOVER_AVWAP_SCALP | 4 | 4 | 1.8024040544008226 | 2.0544522323280128 | 0.9252019339390058 | 1 | 3 |
| MOVER_TREND_PULLBACK | 29 | 29 | 3.7950194848398526 | 3.0 | 1.4227275289997872 | 22 | 7 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 0.9736915513093114 | 1.1131615173465745 | 0.8750761493690371 | 0 | 9 |
| SR_FLIP_RETEST | 2 | 2 | 1.4577177367236243 | 1.738950824271478 | 0.8521345822964804 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 3048.6875400543213 | 3052.408441066742 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 8904.14925289154 | 8907.023962020874 |
| MOVER_AVWAP_SCALP | 4 | 4 | 50.0 | 25.0 | 50.0 | 0.0 | 0.594 | 6339.314821004868 | 6345.870765447617 |
| MOVER_TREND_PULLBACK | 29 | 29 | 27.6 | 48.3 | 27.6 | 0.0 | -0.0226 | 3535.677749156952 | 3539.699410200119 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 22.2 | 77.8 | 22.2 | 0.0 | -0.4242 | 17356.871967077255 | 17358.320402145386 |
| SR_FLIP_RETEST | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 1.2759 | 9358.207955598831 | 9360.758106470108 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 552 | 3 | 488 | 50.0 | 50.0 | 9358.207955598831 | 9360.758106470108 | 64 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1733 | 12 | 1652 | 0.0 | 0.0 | None | None | 81 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `25`
- Gating Δ: `-24565`
- No-generation Δ: `-467263`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": 1.1958, "current_avg_pnl": 0.594, "current_win_rate": 50.0, "previous_avg_pnl": -0.6018, "previous_win_rate": 25.0, "win_rate_delta": 25.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.1246, "current_avg_pnl": -0.0226, "current_win_rate": 27.6, "previous_avg_pnl": -0.1472, "previous_win_rate": 26.8, "win_rate_delta": 0.8}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.975, "current_avg_pnl": -0.4242, "current_win_rate": 22.2, "previous_avg_pnl": 0.5508, "previous_win_rate": 50.0, "win_rate_delta": -27.8}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 23, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -6682.26, "median_terminal_delta_sec": -6682.1, "sl_rate_delta": 50.0, "win_rate_delta": -50.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": -42, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2419.19, "median_terminal_delta_sec": -2421.76, "sl_rate_delta": -50.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **MOVER_AVWAP_SCALP**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
