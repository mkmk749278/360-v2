# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `5` sec (warning=False)
- Latest performance record age: `6769` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 54 | 54 | 54 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 9336 | 9336 | 9183 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 68395 | 68421 | 8 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 65290 | 65290 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 64858 | 62721 | 2548 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 65322 | 64231 | 1173 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 67302 | 67203 | 138 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 60506 | 60524 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 65412 | 65458 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 65479 | 63111 | 3108 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 71905 | 74799 | 824 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 68429 | 63290 | 8540 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 66988 | 66988 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 65297 | 65295 | 24 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 64798 | 64272 | 577 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 66228 | 65189 | 1391 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 64445 | 64567 | 177 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 58009 | 55640 | 2532 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 58179 | 57594 | 674 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 68351 | 68376 | 17 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 60527 | 60539 | 16 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3247 | 3247 | 3156 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 615 | 615 | 599 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 10578 | 10578 | 10485 | 3 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 10 | 10 | 8 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8895 | 8895 | 8205 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2100 | 2100 | 1885 | 8 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 24704 | 24704 | 22476 | 87 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 51 | 51 | 44 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2590 | 2590 | 2467 | 8 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3953 | 3953 | 3815 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 540 | 540 | 490 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2631 | 2631 | 2583 | 6 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 137 | 137 | 136 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 3173 | 3173 | 1725 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=68421): breakout_not_found=36857, basic_filters_failed=18954, move_not_fresh=8814, breakout_stale=2917, retest_proximity_failed=727, volume_spike_missing=121, move_exhausted=27, missing_fvg_or_orderblock=4
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=65290): cls_disabled_merged_into_lsr=65290
- **EVAL::DIVERGENCE_CONTINUATION** (total=62721): cvd_divergence_failed=26684, basic_filters_failed=16966, h1_trend_not_aligned=13933, ema_alignment_reject=4179, retest_proximity_failed=619, missing_fvg_or_orderblock=337, missing_cvd=3
- **EVAL::FAILED_AUCTION_RECLAIM** (total=64231): auction_not_detected=40588, basic_filters_failed=16540, reclaim_hold_failed=2696, regime_blocked=2328, tail_too_small=2035, rsi_reject=44
- **EVAL::FUNDING_EXTREME** (total=67203): funding_not_extreme=46856, basic_filters_failed=17750, ema_alignment_reject=1064, rsi_reject=761, missing_funding_rate=496, momentum_reject=142, cvd_divergence_failed=127, missing_fvg_or_orderblock=7
- **EVAL::LIQUIDATION_REVERSAL** (total=60524): cascade_threshold_not_met=42301, basic_filters_failed=17523, cvd_divergence_failed=365, rsi_reject=302, missing_fvg_or_orderblock=30, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=65458): no_ma_cross=48012, basic_filters_failed=16983, ma_cross_cooldown=389, ma_cross_htf_misaligned=74
- **EVAL::MEAN_REVERT** (total=63111): no_extension=51674, basic_filters_failed=11437
- **EVAL::MOVER_AVWAP_SCALP** (total=74799): no_mover_leg=27830, no_avwap_tag=21114, basic_filters_failed=19246, avwap_slope_against=4034, avwap_reclaim_no_volume=1419, no_avwap_reclaim=1143, anchor_too_recent=13
- **EVAL::MOVER_TREND_PULLBACK** (total=63290): mover_run_too_small=33565, basic_filters_failed=19108, no_reclaim=9588, no_pullback_tag=1029
- **EVAL::OPENING_RANGE_BREAKOUT** (total=66988): feature_disabled=66988
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=65295): regime_blocked=50581, breakout_not_found=10585, basic_filters_failed=2983, adx_reject=1114, ema_alignment_reject=32
- **EVAL::QUIET_COMPRESSION_BREAK** (total=64272): compression_not_detected=19700, regime_blocked=16960, basic_filters_failed=13547, breakout_not_detected=12899, volume_confirmation_failed=1071, rsi_reject=60, missing_fvg_or_orderblock=35
- **EVAL::RANGE_FADE** (total=65189): no_range_edge=53745, basic_filters_failed=11444
- **EVAL::SR_FLIP_RETEST** (total=64567): flip_close_not_confirmed=41094, basic_filters_failed=16513, regime_blocked=2313, long_break_volume_thin=1861, h1_break_not_confirmed=898, retest_out_of_zone=872, reclaim_hold_failed=473, long_acceptance_not_held=244, whipsaw_flip=111, wick_quality_failed=91, ema_alignment_reject=49, missing_fvg_or_orderblock=48
- **EVAL::STANDARD** (total=55640): momentum_reject=17001, adx_reject=15759, basic_filters_failed=7968, sweeps_not_detected=5910, macd_reject=4883, ema_alignment_reject=2597, htf_poi_unanchored=1407, invalid_sl_geometry=60, rsi_reject=51, mtf_reject=4
- **EVAL::TREND_PULLBACK** (total=57594): h1_trend_not_aligned=17409, basic_filters_failed=9271, ema_alignment_reject=8380, h1_pullback_not_confirmed=6148, no_ema_reclaim_close=4945, body_conviction_fail=3675, ema_not_tested_prev=3016, rsi_reject=2591, prev_already_below_emas=732, no_prev_low_break=527, prev_already_above_emas=381, momentum_flat=192, no_prev_high_break=151, missing_fvg_or_orderblock=91, momentum_reject=51, ema21_not_tagged=34
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=68376): breakout_not_found=37459, basic_filters_failed=18952, move_not_fresh=7553, breakout_stale=3181, retest_proximity_failed=1103, volume_spike_missing=114, missing_fvg_or_orderblock=8, move_exhausted=6
- **EVAL::WHALE_MOMENTUM** (total=60539): momentum_reject=48159, recent_ticks_insufficient=9168, basic_filters_failed=3212

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=10): execution:overextended=10
- **DIVERGENCE_CONTINUATION** (total=428): setup_compat:regime_VOLATILE_UNSUITABLE=405, setup_compat:regime_BREAKOUT_EXPANSION=17, execution:overextended=6
- **FAILED_AUCTION_RECLAIM** (total=790): execution:overextended=524, setup_compat:regime_STRONG_TREND=233, context_floor=32, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **FUNDING_EXTREME_SIGNAL** (total=509): execution:trigger_not_confirmed=509
- **LIQUIDATION_REVERSAL** (total=1): execution:trigger_not_confirmed=1
- **LIQUIDITY_SWEEP_REVERSAL** (total=2776): execution:overextended=1099, execution:trigger_not_confirmed=1022, setup_compat:regime_STRONG_TREND=655
- **MA_CROSS_TREND_SHIFT** (total=7): setup_compat:regime_CLEAN_RANGE=3, setup_compat:regime_DIRTY_RANGE=2, execution:overextended=1, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=4492): setup_compat:regime_STRONG_TREND=2269, setup_compat:regime_WEAK_TREND=1662, execution:overextended=561
- **MOVER_AVWAP_SCALP** (total=991): execution:overextended=835, execution:trigger_not_confirmed=129, entry_quality=27
- **MOVER_TREND_PULLBACK** (total=9436): execution:trigger_not_confirmed=6001, execution:overextended=3198, entry_quality=237
- **QUIET_COMPRESSION_BREAK** (total=56): execution:trigger_not_confirmed=55, execution:overextended=1
- **RANGE_FADE** (total=2000): setup_compat:regime_STRONG_TREND=914, setup_compat:regime_WEAK_TREND=801, setup_compat:regime_VOLATILE_UNSUITABLE=193, execution:overextended=92
- **TREND_PULLBACK_EMA** (total=2418): setup_compat:regime_CLEAN_RANGE=1856, setup_compat:regime_DIRTY_RANGE=519, setup_compat:regime_VOLATILE_UNSUITABLE=30, entry_quality=13
- **VOLUME_SURGE_BREAKOUT** (total=6): execution:overextended=6
- **WHALE_MOMENTUM** (total=3168): execution:trigger_not_confirmed=3168

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 155775 | 40.2% |
| RANGING | 114777 | 29.6% |
| TRENDING_UP | 54482 | 14.0% |
| TRENDING_DOWN | 44411 | 11.5% |
| VOLATILE | 18396 | 4.7% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **82**
- Average confidence gap to threshold: **16.56** (samples=82) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: LITUSDT=20, ARBUSDT=19, LTCUSDT=8, XPLUSDT=6, ETHUSDT=6, AVAXUSDT=6, 1000SHIBUSDT=5, TRUMPUSDT=3, DASHUSDT=3, DOTUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 29 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 11 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 11 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 1 |
| MEAN_REVERT | filtered | min_confidence | 5 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 4 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 51 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 15 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 38 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 109 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 20 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 429 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 7 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 37 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 26 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 8 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 3 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 10 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 22 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 6 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | kept | 29 | 73.89 | 65.00 | -8.89 | 20.22 | 20.00 | 20.00 | 0.55 | -3.00 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 70.00 | 65.00 | -5.00 | 20.10 | 14.00 | 20.00 | 5.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 11 | 51.34 | 65.00 | 13.66 | 19.09 | 16.51 | 17.00 | 0.00 | 20.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 11 | 68.80 | 65.00 | -3.80 | 19.34 | 16.05 | 16.85 | 0.73 | 0.00 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 47.70 | 65.00 | 17.30 | 23.90 | 20.00 | 15.80 | 0.00 | 24.30 |
| MEAN_REVERT | filtered | 6 | 56.10 | 65.00 | 8.90 | 18.68 | 17.80 | 14.60 | 0.00 | 13.60 |
| MEAN_REVERT | kept | 4 | 68.95 | 65.00 | -3.95 | 18.58 | 16.85 | 15.22 | 0.00 | 9.00 |
| MOVER_AVWAP_SCALP | filtered | 66 | 47.80 | 65.00 | 17.20 | 21.23 | 17.89 | 15.80 | 4.19 | 23.02 |
| MOVER_AVWAP_SCALP | kept | 38 | 80.77 | 65.00 | -15.77 | 20.08 | 15.74 | 15.80 | 4.64 | 0.57 |
| MOVER_TREND_PULLBACK | filtered | 129 | 57.24 | 65.00 | 7.76 | 19.70 | 18.65 | 15.80 | 4.10 | 19.81 |
| MOVER_TREND_PULLBACK | kept | 429 | 77.72 | 65.00 | -12.72 | 20.48 | 18.48 | 15.80 | 3.96 | 0.72 |
| POST_DISPLACEMENT_CONTINUATION | kept | 7 | 68.99 | 65.00 | -3.99 | 20.11 | 19.81 | 19.41 | 4.50 | -0.41 |
| QUIET_COMPRESSION_BREAK | filtered | 63 | 51.06 | 64.21 | 13.15 | 20.33 | 19.17 | 20.00 | 0.00 | 10.77 |
| QUIET_COMPRESSION_BREAK | kept | 8 | 74.44 | 65.00 | -9.44 | 21.19 | 19.55 | 20.00 | 0.00 | -1.14 |
| SR_FLIP_RETEST | filtered | 3 | 44.50 | 65.00 | 20.50 | 21.27 | 20.00 | 15.20 | 2.50 | 23.00 |
| SR_FLIP_RETEST | kept | 2 | 77.00 | 65.00 | -12.00 | 20.80 | 20.00 | 15.20 | 2.50 | 1.50 |
| TREND_PULLBACK_EMA | filtered | 10 | 60.74 | 65.00 | 4.26 | 19.95 | 20.00 | 20.00 | 3.90 | 19.88 |
| TREND_PULLBACK_EMA | kept | 22 | 76.35 | 65.00 | -11.35 | 21.45 | 19.89 | 18.02 | 4.02 | 4.41 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 91.00 | 65.00 | -26.00 | 19.50 | 14.60 | 20.00 | 6.00 | 0.00 |
| WHALE_MOMENTUM | filtered | 6 | 34.52 | 65.00 | 30.48 | 21.50 | 14.00 | 17.00 | 0.00 | 31.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | kept | 29 | 73.89 | 20.31 | 18.00 | 6.72 | 14.00 | 5.00 | 9.30 | 0.55 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 70.00 | 25.00 | 8.00 | 9.00 | 12.00 | 5.00 | 6.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 11 | 51.34 | 23.18 | 14.00 | 3.27 | 17.00 | 8.18 | 5.70 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 11 | 68.80 | 23.55 | 14.00 | 6.27 | 13.36 | 5.32 | 5.57 | 0.73 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 47.70 | 25.00 | 14.00 | 9.00 | 11.00 | 5.00 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 6 | 56.10 | 17.00 | 18.00 | 9.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 4 | 68.95 | 25.00 | 18.00 | 9.75 | 13.00 | 5.00 | 7.20 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 66 | 47.80 | 20.39 | 18.00 | 11.14 | 14.00 | 8.84 | 5.84 | 4.19 |
| MOVER_AVWAP_SCALP | kept | 38 | 80.77 | 18.53 | 18.00 | 11.37 | 13.79 | 7.21 | 9.07 | 4.64 |
| MOVER_TREND_PULLBACK | filtered | 129 | 57.24 | 19.85 | 18.00 | 7.66 | 13.35 | 6.91 | 8.60 | 4.10 |
| MOVER_TREND_PULLBACK | kept | 429 | 77.72 | 19.14 | 18.01 | 8.10 | 13.44 | 6.84 | 9.01 | 3.96 |
| POST_DISPLACEMENT_CONTINUATION | kept | 7 | 68.99 | 4.14 | 18.00 | 15.00 | 14.00 | 5.50 | 10.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 63 | 51.06 | 19.54 | 15.65 | 11.24 | 14.57 | 5.20 | 4.68 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 8 | 74.44 | 17.00 | 18.00 | 13.12 | 14.00 | 7.69 | 6.86 | 0.00 |
| SR_FLIP_RETEST | filtered | 3 | 44.50 | 25.00 | 8.00 | 3.00 | 14.00 | 5.00 | 10.00 | 2.50 |
| SR_FLIP_RETEST | kept | 2 | 77.00 | 25.00 | 18.00 | 9.00 | 12.00 | 5.00 | 7.00 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 10 | 60.74 | 17.00 | 18.00 | 7.50 | 17.00 | 8.00 | 9.22 | 3.90 |
| TREND_PULLBACK_EMA | kept | 22 | 76.35 | 22.45 | 18.00 | 7.50 | 14.82 | 5.16 | 9.22 | 4.02 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 91.00 | 25.00 | 18.00 | 15.00 | 14.00 | 5.00 | 8.00 | 6.00 |
| WHALE_MOMENTUM | filtered | 6 | 34.52 | 20.00 | 8.00 | 15.00 | 13.67 | 6.75 | 2.70 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | kept | 29 | 73.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 70.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 11 | 51.34 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 11 | 68.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 47.70 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| MEAN_REVERT | filtered | 6 | 56.10 | 0.00 | 0.00 | 0.00 | 0.00 | 13.60 | 0.00 | 0.00 | 0.00 | **13.60** |
| MEAN_REVERT | kept | 4 | 68.95 | 0.00 | 0.00 | 0.00 | 0.00 | 9.00 | 0.00 | 0.00 | 0.00 | **9.00** |
| MOVER_AVWAP_SCALP | filtered | 66 | 47.80 | 0.00 | 0.00 | 0.00 | 0.00 | 4.91 | 0.00 | 0.00 | 0.00 | **4.91** |
| MOVER_AVWAP_SCALP | kept | 38 | 80.77 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.25** |
| MOVER_TREND_PULLBACK | filtered | 129 | 57.24 | 0.00 | 0.00 | 1.98 | 0.00 | 4.50 | 0.00 | 0.00 | 0.00 | **6.48** |
| MOVER_TREND_PULLBACK | kept | 429 | 77.72 | 0.00 | 0.00 | 0.36 | 0.00 | 0.34 | 0.00 | 0.00 | 0.00 | **0.70** |
| POST_DISPLACEMENT_CONTINUATION | kept | 7 | 68.99 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 63 | 51.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.68 | **3.68** |
| QUIET_COMPRESSION_BREAK | kept | 8 | 74.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 3 | 44.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 2 | 77.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 10 | 60.74 | 0.00 | 0.00 | 0.00 | 0.00 | 12.96 | 0.00 | 0.00 | 0.00 | **12.96** |
| TREND_PULLBACK_EMA | kept | 22 | 76.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 91.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 6 | 34.52 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |

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
- Outcomes recorded: **91031 held of 221446 seen** across 21 strategies; 2036 cells past the sample floor; **900 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 34803 | 499/34304/0 | 44% | -0.17 | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_FALLING/MAJOR (+1.18R) | ASIA/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.16R) |
| MOVER_AVWAP_SCALP | 11371 | 128/11243/0 | 39% | -0.27 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 6785 | 76/6709/0 | 42% | -0.18 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 5427 | 26/5401/0 | 55% | +0.09 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | OVERLAP/MARKDOWN/CASCADE/BTC_RISING (-1.17R) |
| SHADOW_MEAN_REVERT | 4910 | 0/0/4910 | 43% | -0.08 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (+0.52R) | LONDON/QUIET/COMPRESSED/BTC_FALLING (-0.97R) |
| TREND_PULLBACK_EMA | 4499 | 20/4479/0 | 47% | -0.12 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.28R) |
| SHADOW_RANGE_FADE | 4101 | 0/0/4101 | 38% | -0.06 | ASIA/MARKDOWN/EXPANDED/BTC_FALLING (+0.46R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.04R) |
| QUIET_COMPRESSION_BREAK | 4058 | 188/3870/0 | 46% | -0.11 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+0.83R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 3357 | 0/0/3357 | 36% | -0.38 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-1.01R) |
| WHALE_MOMENTUM | 3253 | 2/3251/0 | 42% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 2343 | 36/2307/0 | 39% | -0.27 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.21R) |
| MEAN_REVERT | 1439 | 20/1419/0 | 60% | +0.10 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| VOLUME_SURGE_BREAKOUT | 1198 | 0/1198/0 | 45% | -0.01 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 1112 | 2/1110/0 | 30% | -0.48 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.36R) |
| SR_FLIP_RETEST | 880 | 2/878/0 | 43% | -0.31 | NY/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.77R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 602 | 0/0/602 | 56% | -0.01 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | ASIA/MARKUP/CASCADE/BTC_NEUTRAL (-0.39R) |
| BREAKDOWN_SHORT | 337 | 22/315/0 | 41% | -0.15 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.03R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| RANGE_FADE | 300 | 0/300/0 | 59% | +0.19 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| LIQUIDATION_REVERSAL | 196 | 0/196/0 | 11% | -1.00 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 54 | 6/48/0 | 41% | -0.12 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 6 | 0/6/0 | 67% | +0.42 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING` -1.38R (n=17, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.36R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 108 | 32% / -0.44R | 108 | 49% / -0.15R | +0.29 | **ATR** |
| TREND_PULLBACK_EMA | 375 | 46% / -0.20R | 375 | 55% / -0.03R | +0.17 | **ATR** |
| SR_FLIP_RETEST | 104 | 48% / -0.28R | 104 | 50% / -0.17R | +0.12 | **ATR** |
| RANGE_FADE | 20 | 50% / +0.20R | 20 | 50% / +0.10R | -0.11 | **FIXED** |
| WHALE_MOMENTUM | 364 | 43% / -0.33R | 364 | 45% / -0.23R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 858 | 45% / -0.18R | 858 | 50% / -0.08R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 595 | 43% / -0.18R | 595 | 45% / -0.09R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 5283 | 50% / -0.10R | 5283 | 54% / -0.01R | +0.09 | **ATR** |
| BREAKDOWN_SHORT | 25 | 32% / -0.15R | 25 | 36% / -0.10R | +0.05 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 74 | 43% / -0.05R | 74 | 51% / -0.01R | +0.04 | **ATR** |
| MA_CROSS_TREND_SHIFT | 18 | 39% / -0.20R | 18 | 39% / -0.16R | +0.04 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 476 | 52% / -0.18R | 476 | 55% / -0.15R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 680 | 47% / -0.14R | 680 | 47% / -0.15R | -0.01 | **FIXED** |
| MEAN_REVERT | 117 | 58% / +0.04R | 117 | 56% / +0.03R | -0.00 | **FIXED** |
| DIVERGENCE_CONTINUATION | 542 | 53% / -0.01R | 542 | 59% / -0.01R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 13 | 31% / -0.46R | 13 | 54% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 7720 | 31% | -0.15R | 304 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 858 | 48% | -0.08R | 184 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 48 | 56% | -0.01R | 40 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 137 | 36% / -0.30R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 651 | 38% / -0.06R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 6754 | 37% / -0.11R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1100 | 35% / -0.03R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 474 | 36% / -0.11R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 611 | 42% / +0.09R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 500 | 38% / -0.02R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 472 | 45% / -0.09R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 102 | 29% / -0.38R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 133 | 30% / -0.65R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 98 | 56% / +0.13R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 46 | 39% / -0.13R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 18 | 44% / +0.28R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 102 | 32% / -0.42R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 25 | 12% / -0.62R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 17 | 41% / -0.06R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.05R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **11** · boot grace active: False
- **ALERT** `geometry_ab` — upstream +112 but output +0 (streak 18/6) (sustained 18 cycles)
- **ALERT** `sar_exit_shadow` — upstream +112 but output +0 (streak 18/6) (sustained 18 cycles)
- **ALERT** `sar_alignment_crosscheck` — 83/952 disagreed (8.7%) (streak 61/6) (sustained 61 cycles)
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×746]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 61/6) (sustained 61 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/180 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 61/6) (sustained 61 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.44R (bound 0.3) (streak 61/6) (sustained 61 cycles)
- **ALERT** `mean_revert_emission` — 3949 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.09R over n=1419, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 61/6) (sustained 61 cycles)
- **ALERT** `range_fade_emission` — 1501 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=300, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 61/6) (sustained 61 cycles)
- **ALERT** `tuned_variants` — 17 non-stamps — atr_arm_uncomputable=17 (seen=195 stamped=35 skipped=143) (streak 61/6) (sustained 61 cycles)
- **ALERT** `auto_dispatch` — 12 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode:off=12, mode:paper=12) (streak 45/3) (sustained 45 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 61/3) (sustained 61 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 15513075 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 61/3) | 61 |
| ai_governor_live_arms | ok | 17 arms current, none stalled; covering 203/203 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 28 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 4/12) | 4 |
| auto_dispatch | violating | 12 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode:off=12, mode:paper=12) (streak 45/3) | 45 |
| btc_reference | ok | BTC ref 77204.90 | 0 |
| candle_coverage | ok | 89/89 symbols with ≥20 15m candles, 89/89 updated within 45m [fresh=89; 75 Tier-1 futures + 14 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 912 dup bars, 0 undedupable; ws 0 out-of-order, 154 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 6 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | violating | upstream +23 but output +0 (streak 12/72) | 12 |
| dark_atr_trail_arms | ok | no open arms; covering 1056/1073 signals (98%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | 68 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1057/1074 signals (98%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 1662122 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.44R (bound 0.3) (streak 61/6) | 61 |
| emission_controller | ok | last cycle 1s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×746]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 61/6) | 61 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/180 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 61/6) | 61 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 9 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +112 but output +0 (streak 18/6) | 18 |
| indicator_cache_key | ok | 2888 frozen value(s) avoided; 54601 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 3949 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.09R over n=1419, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 61/6) | 61 |
| mean_revert_path | ok | output +34 / upstream +112 | 0 |
| mover_admission_metadata | ok | 897 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 14 held, 14 with scan counts, 12 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 8 locked / 8 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2959 rows held, 1329089 evicted (sampled: execution:trigger_not_confirmed 400/490039, execution:overextended 400/442313, setup_compat:regime_STRONG_TREND 400/194494) | 0 |
| price_action_lane | ok | 142111 evaluated, 142 emitted; layer1 142 stamped / 0 blind; cooldown=17289, delta_opposed=12144, no_footprint=43830, no_opposing_target=470, no_sweep=57210, rr_below_floor=11026 | 0 |
| promoted_pair_integrity | ok | 14/14 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 1501 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=300, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 61/6) | 61 |
| range_fade_path | violating | upstream +112 but output +0 (streak 2/72) | 2 |
| sar_alignment_crosscheck | violating | 83/952 disagreed (8.7%) (streak 61/6) | 61 |
| sar_exit_shadow | violating | upstream +112 but output +0 (streak 18/6) | 18 |
| sar_hold_arm | ok | 1685 held arms settled, 238 unscored, 27 still walking (23 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 8/8 resolvable | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 26 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 4/12) | 4 |
| sar_refresh_budget | ok | 19 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 408 records await one (8 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 17.12s, worst 105.22s over 1714 lifetime cycles; lifetime 8 over 60s, 0 over 120s (plus 1/0 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 2.76s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 47265 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 28s ago (3.22s to run, worst 75.42s), 89 overrun(s) of 1267 cycles, TTL 900s; slowest data_intake=4.53s, tickers=3.84s, dark_promotion=1.11s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +2 / upstream +112 | 0 |
| structural_snap | ok | 4982/4982 measured, 18 blind, 0 levels moved (refusals: redetect_cooldown=6) | 0 |
| structural_veto_lane | ok | 40 stamped; 0 with no readable level book, 7 with clear air ahead, 30 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +112 / upstream +23 | 0 |
| tuned_variants | violating | 17 non-stamps — atr_arm_uncomputable=17 (seen=195 stamped=35 skipped=143) (streak 61/6) | 61 |

Fail-open exception counters (nonzero sites):
- `feature_liveness.probe.footprint_bars`: 1 — last: RuntimeError: deque mutated during iteration

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1809061`
- `Path funnel` emissions: `49`
- `Regime distribution` emissions: `49`
- `QUIET_SCALP_BLOCK` events: `82`
- `confidence_gate` events: `847`
- `free_channel_post` events: `34`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **34**

| Source | Count |
|---|---:|
| signal_close | 27 |
| regime_shift | 7 |

- By severity: HIGH=34

## Dependency readiness
- cvd: presence[absent=26, present=303695] state[empty=26, populated=303695] buckets[few=3, many=303664, none=26, some=28] sources[none] quality[none]
- funding_rate: presence[absent=18834, present=284887] state[empty=18834, populated=284887] buckets[few=284887, none=18834] sources[none] quality[none]
- liquidation_clusters: presence[absent=166009, present=137712] state[empty=166009, populated=137712] buckets[few=110928, none=166009, some=26784] sources[none] quality[none]
- oi_snapshot: presence[absent=17640, present=286081] state[empty=17640, populated=286081] buckets[few=210, many=284654, none=17640, some=1217] sources[none] quality[none]
- order_book: presence[absent=93268, present=210453] state[populated=210453, unavailable=93268] buckets[few=210453, none=93268] sources[book_ticker=210453, unavailable=93268] quality[none=93268, top_of_book_only=210453]
- orderblocks: presence[absent=303721] state[empty=303721] buckets[none=303721] sources[measured_dark=303721] quality[none]
- recent_ticks: presence[present=303721] state[populated=303721] buckets[many=303721] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.314162969589233` sec
- Median create→first breach: `2446.000170946121` sec
- Median create→terminal: `2446.8270559310913` sec
- Median first breach→terminal: `2.3917598724365234` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 3.7}, "under_180s": {"count": 1, "pct": 3.7}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 3.7}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 3.7}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.8670027098344083 | 1.0874246634996017 | 0.7972991039619968 | 0 | 1 |
| MOVER_TREND_PULLBACK | 23 | 23 | 4.126427247503253 | 3.0 | 1.4824094009308828 | 18 | 5 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.8 | 0.7999999999999983 | 0.9202036404595972 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 48817.17918801308 | 48819.591706991196 |
| MOVER_TREND_PULLBACK | 23 | 23 | 43.5 | 21.7 | 43.5 | 0.0 | 1.3792 | 2186.7329659461975 | 2189.5942380428314 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.0 | -0.2447 | 25798.246025800705 | 25799.6171708107 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 540 | 2 | 490 | 0.0 | 0.0 | None | None | 50 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2631 | 6 | 2583 | 0.0 | 0.0 | None | None | 48 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-165`
- Gating Δ: `6176`
- No-generation Δ: `253078`
- Fast failures Δ: `-2`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.9025, "current_avg_pnl": 1.3792, "current_win_rate": 43.5, "previous_avg_pnl": 0.4767, "previous_win_rate": 38.0, "win_rate_delta": 5.5}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.9301, "current_avg_pnl": -0.2447, "current_win_rate": 0.0, "previous_avg_pnl": 0.6854, "previous_win_rate": 50.0, "win_rate_delta": -50.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 30, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -9, "geometry_changed_delta": 0, "geometry_preserved_delta": -55, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -3037.7, "median_terminal_delta_sec": -3039.71, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **DIVERGENCE_CONTINUATION**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
