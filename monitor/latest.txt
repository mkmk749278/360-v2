# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `1475` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 52 | 52 | 41 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 2004 | 2004 | 1402 | 5 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 23959 | 23954 | 9 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 19638 | 19641 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 19555 | 18827 | 805 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 19648 | 19544 | 116 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 19545 | 19535 | 12 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 15429 | 15431 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 19661 | 19671 | 1 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 19673 | 18628 | 1393 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 26936 | 28740 | 161 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 23964 | 18574 | 8349 | 0 | 0 | 0 | low-sample (no_reclaim) |
| EVAL::OPENING_RANGE_BREAKOUT | 19425 | 19429 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 19641 | 19646 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 19548 | 19548 | 7 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 20024 | 19350 | 823 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 19429 | 19503 | 40 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 15303 | 14397 | 999 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 15400 | 15274 | 154 | 0 | 0 | 0 | low-sample (ema_not_tested_prev) |
| EVAL::VOLUME_SURGE_BREAKOUT | 23930 | 23933 | 24 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 15435 | 15427 | 20 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 343 | 343 | 191 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 98 | 98 | 10 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 4100 | 4100 | 4098 | 2 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 1 | 1 | 0 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 2958 | 2958 | 2939 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 410 | 410 | 82 | 11 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 20465 | 20465 | 9665 | 315 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 55 | 55 | 0 | 3 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 1642 | 1642 | 1642 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 154 | 154 | 134 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 441 | 441 | 282 | 9 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 90 | 90 | 25 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 952 | 952 | 97 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=23954): breakout_not_found=16520, basic_filters_failed=6047, move_not_fresh=572, breakout_stale=550, retest_proximity_failed=135, volume_spike_missing=83, move_exhausted=46, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=19641): cls_disabled_merged_into_lsr=19641
- **EVAL::DIVERGENCE_CONTINUATION** (total=18827): cvd_divergence_failed=12136, basic_filters_failed=3639, h1_trend_not_aligned=1193, regime_blocked=864, ema_alignment_reject=716, retest_proximity_failed=154, missing_fvg_or_orderblock=125
- **EVAL::FAILED_AUCTION_RECLAIM** (total=19544): auction_not_detected=14037, basic_filters_failed=3284, regime_blocked=1211, reclaim_hold_failed=660, tail_too_small=352
- **EVAL::FUNDING_EXTREME** (total=19535): funding_not_extreme=15233, basic_filters_failed=3626, ema_alignment_reject=329, rsi_reject=151, missing_funding_rate=147, momentum_reject=21, cvd_divergence_failed=19, missing_fvg_or_orderblock=9
- **EVAL::LIQUIDATION_REVERSAL** (total=15431): cascade_threshold_not_met=11548, basic_filters_failed=3582, rsi_reject=155, cvd_divergence_failed=123, missing_fvg_or_orderblock=22, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=19671): no_ma_cross=15784, basic_filters_failed=3643, ma_cross_cooldown=244
- **EVAL::MEAN_REVERT** (total=18628): no_extension=15578, basic_filters_failed=3050
- **EVAL::MOVER_AVWAP_SCALP** (total=28740): no_avwap_tag=15391, basic_filters_failed=6111, no_mover_leg=3732, avwap_slope_against=2450, avwap_reclaim_no_volume=779, no_avwap_reclaim=265, anchor_too_recent=12
- **EVAL::MOVER_TREND_PULLBACK** (total=18574): no_reclaim=7171, basic_filters_failed=5984, mover_run_too_small=2698, no_pullback_tag=2387, insufficient_candles=334
- **EVAL::OPENING_RANGE_BREAKOUT** (total=19429): feature_disabled=19429
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=19646): regime_blocked=11341, breakout_not_found=7259, basic_filters_failed=895, adx_reject=133, ema_alignment_reject=18
- **EVAL::QUIET_COMPRESSION_BREAK** (total=19548): regime_blocked=9478, compression_not_detected=7512, basic_filters_failed=2390, breakout_not_detected=155, volume_confirmation_failed=10, rsi_reject=3
- **EVAL::RANGE_FADE** (total=19350): no_range_edge=16189, basic_filters_failed=3038, insufficient_candles=123
- **EVAL::SR_FLIP_RETEST** (total=19503): flip_close_not_confirmed=13661, basic_filters_failed=3282, regime_blocked=1210, retest_out_of_zone=539, long_break_volume_thin=539, h1_break_not_confirmed=174, reclaim_hold_failed=64, whipsaw_flip=14, long_acceptance_not_held=13, wick_quality_failed=4, ema_alignment_reject=3
- **EVAL::STANDARD** (total=14397): momentum_reject=3959, basic_filters_failed=2357, ema_alignment_reject=2192, adx_reject=2093, sweeps_not_detected=1913, macd_reject=1463, htf_poi_unanchored=330, rsi_reject=64, invalid_sl_geometry=17, mtf_reject=9
- **EVAL::TREND_PULLBACK** (total=15274): ema_not_tested_prev=3865, basic_filters_failed=2398, h1_pullback_not_confirmed=2273, ema_alignment_reject=2224, no_ema_reclaim_close=1416, h1_trend_not_aligned=913, regime_blocked=890, body_conviction_fail=494, rsi_reject=491, prev_already_above_emas=125, no_prev_high_break=109, missing_fvg_or_orderblock=27, momentum_reject=15, prev_already_below_emas=13, momentum_flat=11, ema21_not_tagged=10
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=23933): breakout_not_found=9378, basic_filters_failed=6045, move_not_fresh=5876, breakout_stale=1391, retest_proximity_failed=1002, volume_spike_missing=229, missing_fvg_or_orderblock=12
- **EVAL::WHALE_MOMENTUM** (total=15427): momentum_reject=10066, recent_ticks_insufficient=3765, basic_filters_failed=1596

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=57): setup_compat:regime_VOLATILE_UNSUITABLE=57
- **FAILED_AUCTION_RECLAIM** (total=47): execution:overextended=46, setup_compat:regime_STRONG_TREND=1
- **FUNDING_EXTREME_SIGNAL** (total=89): execution:trigger_not_confirmed=89
- **LIQUIDATION_REVERSAL** (total=2): execution:trigger_not_confirmed=2
- **LIQUIDITY_SWEEP_REVERSAL** (total=1463): setup_compat:regime_STRONG_TREND=563, execution:overextended=545, execution:trigger_not_confirmed=355
- **MEAN_REVERT** (total=2647): setup_compat:regime_STRONG_TREND=1585, execution:overextended=746, setup_compat:regime_WEAK_TREND=314, entry_quality=2
- **MOVER_AVWAP_SCALP** (total=301): execution:overextended=167, execution:trigger_not_confirmed=80, entry_quality=54
- **MOVER_TREND_PULLBACK** (total=11395): execution:overextended=4843, execution:trigger_not_confirmed=3995, entry_quality=2557
- **POST_DISPLACEMENT_CONTINUATION** (total=4): execution:overextended=4
- **RANGE_FADE** (total=1059): setup_compat:regime_STRONG_TREND=503, setup_compat:regime_WEAK_TREND=475, setup_compat:regime_VOLATILE_UNSUITABLE=81
- **TREND_PULLBACK_EMA** (total=365): setup_compat:regime_CLEAN_RANGE=210, setup_compat:regime_DIRTY_RANGE=120, entry_quality=26, setup_compat:regime_VOLATILE_UNSUITABLE=9
- **VOLUME_SURGE_BREAKOUT** (total=8): execution:overextended=8
- **WHALE_MOMENTUM** (total=634): execution:trigger_not_confirmed=634

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 58724 | 52.4% |
| TRENDING_UP | 34158 | 30.5% |
| TRENDING_DOWN | 9935 | 8.9% |
| VOLATILE | 5538 | 4.9% |
| QUIET | 3694 | 3.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **22**
- Average confidence gap to threshold: **11.36** (samples=22) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XMRUSDT=18, BTCUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 90 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 103 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 23 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 18 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 10 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 2 |
| MEAN_REVERT | kept | min_confidence_pass | 10 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 52 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 73 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 717 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4950 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 55 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 13 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 56 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 33 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 25 |
| WHALE_MOMENTUM | filtered | min_confidence | 60 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 4 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 90 | 54.56 | 65.00 | 10.44 | 20.95 | 19.46 | 18.79 | 1.53 | 13.58 |
| DIVERGENCE_CONTINUATION | kept | 103 | 68.84 | 65.00 | -3.84 | 20.63 | 19.89 | 19.35 | 0.59 | -1.74 |
| FAILED_AUCTION_RECLAIM | filtered | 41 | 51.29 | 63.93 | 12.64 | 22.91 | 19.92 | 20.00 | 2.96 | 3.54 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 73.50 | 65.00 | -8.50 | 19.10 | 20.00 | 20.00 | 5.00 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 10 | 52.20 | 61.00 | 8.80 | 19.89 | 12.50 | 18.90 | 5.00 | 0.00 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 63.25 | 65.00 | 1.75 | 21.85 | 14.00 | 17.00 | 4.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2 | 66.95 | 65.00 | -1.95 | 19.80 | 20.00 | 17.00 | 2.50 | 0.00 |
| MEAN_REVERT | kept | 10 | 69.95 | 65.00 | -4.95 | 21.20 | 14.00 | 17.00 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 53 | 57.57 | 63.28 | 5.71 | 19.37 | 14.78 | 15.80 | 4.30 | 10.82 |
| MOVER_AVWAP_SCALP | kept | 73 | 77.20 | 65.00 | -12.20 | 19.23 | 15.17 | 15.80 | 4.30 | 1.76 |
| MOVER_TREND_PULLBACK | filtered | 717 | 60.21 | 64.82 | 4.61 | 20.70 | 18.21 | 15.80 | 4.17 | 13.46 |
| MOVER_TREND_PULLBACK | kept | 4950 | 77.12 | 65.00 | -12.12 | 20.24 | 18.18 | 15.80 | 4.41 | 1.31 |
| QUIET_COMPRESSION_BREAK | kept | 55 | 78.70 | 65.00 | -13.70 | 22.69 | 19.32 | 20.00 | 0.00 | -1.47 |
| TREND_PULLBACK_EMA | filtered | 13 | 61.53 | 65.00 | 3.47 | 18.85 | 17.56 | 18.77 | 3.00 | 15.61 |
| TREND_PULLBACK_EMA | kept | 56 | 77.26 | 65.00 | -12.26 | 20.63 | 19.25 | 17.40 | 4.12 | 5.98 |
| VOLUME_SURGE_BREAKOUT | filtered | 33 | 34.30 | 63.55 | 29.25 | 20.16 | 18.19 | 20.00 | 3.00 | 23.00 |
| VOLUME_SURGE_BREAKOUT | kept | 25 | 74.04 | 65.00 | -9.04 | 20.98 | 19.37 | 20.00 | 4.78 | 2.88 |
| WHALE_MOMENTUM | filtered | 64 | 58.47 | 63.56 | 5.09 | 23.94 | 18.18 | 17.00 | 0.00 | 11.35 |
| WHALE_MOMENTUM | kept | 1 | 64.00 | 65.00 | 1.00 | 24.90 | 14.00 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 90 | 54.56 | 23.13 | 10.44 | 5.80 | 13.27 | 5.06 | 8.91 | 1.53 |
| DIVERGENCE_CONTINUATION | kept | 103 | 68.84 | 22.20 | 15.18 | 3.58 | 12.73 | 5.79 | 9.23 | 0.59 |
| FAILED_AUCTION_RECLAIM | filtered | 41 | 51.29 | 20.32 | 16.15 | 7.32 | 11.90 | 7.55 | 3.63 | 2.96 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 73.50 | 25.00 | 18.00 | 3.00 | 9.00 | 8.50 | 5.00 | 5.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 10 | 52.20 | 17.00 | 18.00 | 3.00 | 12.00 | 8.50 | 3.70 | 5.00 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 63.25 | 25.00 | 8.00 | 7.50 | 12.00 | 6.75 | 5.00 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2 | 66.95 | 20.00 | 16.00 | 3.00 | 13.00 | 6.50 | 5.95 | 2.50 |
| MEAN_REVERT | kept | 10 | 69.95 | 25.00 | 18.00 | 3.00 | 12.00 | 4.25 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 53 | 57.57 | 16.92 | 18.00 | 9.88 | 13.68 | 5.24 | 7.61 | 4.30 |
| MOVER_AVWAP_SCALP | kept | 73 | 77.20 | 19.60 | 18.00 | 9.45 | 13.40 | 5.94 | 9.21 | 4.30 |
| MOVER_TREND_PULLBACK | filtered | 717 | 60.21 | 17.65 | 18.00 | 7.80 | 12.60 | 5.22 | 9.36 | 4.17 |
| MOVER_TREND_PULLBACK | kept | 4950 | 77.12 | 19.26 | 18.03 | 8.06 | 13.06 | 5.94 | 9.74 | 4.41 |
| QUIET_COMPRESSION_BREAK | kept | 55 | 78.70 | 20.20 | 16.47 | 11.78 | 14.05 | 6.85 | 9.34 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 13 | 61.53 | 17.00 | 18.00 | 7.50 | 14.92 | 7.42 | 9.29 | 3.00 |
| TREND_PULLBACK_EMA | kept | 56 | 77.26 | 21.45 | 18.00 | 8.36 | 15.12 | 7.94 | 8.57 | 4.12 |
| VOLUME_SURGE_BREAKOUT | filtered | 33 | 34.30 | 17.00 | 14.00 | 12.00 | 17.00 | 5.00 | 4.30 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 25 | 74.04 | 19.96 | 15.44 | 12.12 | 10.24 | 5.00 | 9.38 | 4.78 |
| WHALE_MOMENTUM | filtered | 64 | 58.47 | 24.00 | 17.38 | 5.91 | 13.89 | 7.84 | 0.81 | 0.00 |
| WHALE_MOMENTUM | kept | 1 | 64.00 | 25.00 | 18.00 | 9.00 | 12.00 | 10.00 | 0.00 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 90 | 54.56 | 0.00 | 0.00 | 4.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.70** |
| DIVERGENCE_CONTINUATION | kept | 103 | 68.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 41 | 51.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | **0.18** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 73.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 10 | 52.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 63.25 | 0.00 | 0.00 | 4.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2 | 66.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 10 | 69.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 53 | 57.57 | 0.00 | 0.00 | 2.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.04** |
| MOVER_AVWAP_SCALP | kept | 73 | 77.20 | 0.00 | 0.00 | 1.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | **1.34** |
| MOVER_TREND_PULLBACK | filtered | 717 | 60.21 | 0.84 | 0.00 | 4.56 | 0.00 | 0.13 | 0.50 | 0.00 | 0.00 | **6.03** |
| MOVER_TREND_PULLBACK | kept | 4950 | 77.12 | 0.00 | 0.00 | 1.00 | 0.00 | 0.20 | 0.07 | 0.00 | 0.00 | **1.27** |
| QUIET_COMPRESSION_BREAK | kept | 55 | 78.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 13 | 61.53 | 0.00 | 0.00 | 3.69 | 0.00 | 0.00 | 0.77 | 0.00 | 0.00 | **4.46** |
| TREND_PULLBACK_EMA | kept | 56 | 77.26 | 0.00 | 0.00 | 3.94 | 0.00 | 0.00 | 0.18 | 0.00 | 0.00 | **4.12** |
| VOLUME_SURGE_BREAKOUT | filtered | 33 | 34.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 25 | 74.04 | 0.00 | 0.00 | 0.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.96** |
| WHALE_MOMENTUM | filtered | 64 | 58.47 | 0.00 | 0.00 | 0.00 | 0.00 | 1.35 | 0.00 | 0.00 | 0.00 | **1.35** |
| WHALE_MOMENTUM | kept | 1 | 64.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **19065 held of 35986 seen** across 20 strategies; 406 cells past the sample floor; **157 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 13138 | 19/13119/0 | 57% | +0.02 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | LONDON/MARKDOWN/COMPRESSED/BTC_RISING/MIDCAP (-1.14R) |
| MOVER_AVWAP_SCALP | 1052 | 2/1050/0 | 40% | -0.27 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_RISING/MIDCAP (+0.02R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.05R) |
| SHADOW_MEAN_REVERT | 884 | 0/0/884 | 32% | -0.34 | NY/MARKUP/CASCADE/BTC_RISING (-0.19R) | NY/RANGE/EXPANDED/BTC_RISING (-0.88R) |
| SHADOW_RANGE_FADE | 767 | 0/0/767 | 32% | -0.22 | LONDON/MARKUP/EXPANDED/BTC_RISING (+0.17R) | LONDON/RANGE/NORMAL/BTC_RISING (-0.96R) |
| DIVERGENCE_CONTINUATION | 692 | 0/692/0 | 68% | +0.22 | OFF_HOURS/QUIET/COMPRESSED/BTC_RISING (+1.34R) | NY/MARKDOWN/COMPRESSED/BTC_RISING/MIDCAP (-1.13R) |
| TREND_PULLBACK_EMA | 596 | 0/596/0 | 52% | -0.11 | ASIA/QUIET/EXPANDED/BTC_RISING (+0.54R) | NY/DISTRIBUTION/EXPANDED/BTC_RISING/ALTCOIN (-0.71R) |
| WHALE_MOMENTUM | 486 | 0/486/0 | 26% | -0.50 | OFF_HOURS/MARKUP/NORMAL/BTC_RISING (-0.00R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| SHADOW_FUNDING_FADE | 348 | 0/0/348 | 51% | -0.12 | NY/MARKDOWN/COMPRESSED/BTC_RISING (+0.58R) | ASIA/RANGE/NORMAL/BTC_RISING (-0.52R) |
| FAILED_AUCTION_RECLAIM | 320 | 2/318/0 | 34% | -0.46 | OFF_HOURS/DISTRIBUTION/NORMAL/BTC_RISING (-0.11R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.19R) |
| VOLUME_SURGE_BREAKOUT | 184 | 0/184/0 | 87% | +0.85 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.00R) | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL (+1.00R) |
| MEAN_REVERT | 158 | 2/156/0 | 99% | +1.10 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR (+1.13R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+0.94R) |
| QUIET_COMPRESSION_BREAK | 134 | 4/130/0 | 46% | -0.14 | — | — |
| BREAKDOWN_SHORT | 108 | 0/108/0 | 2% | -1.04 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| FUNDING_EXTREME_SIGNAL | 86 | 0/86/0 | 28% | -0.23 | — | — |
| SHADOW_CASCADE_REVERSAL | 48 | 0/0/48 | 48% | -0.20 | — | — |
| LIQUIDITY_SWEEP_REVERSAL | 34 | 2/32/0 | 35% | -0.38 | — | — |
| RANGE_FADE | 18 | 0/18/0 | 22% | -0.40 | — | — |
| MA_CROSS_TREND_SHIFT | 6 | 0/6/0 | 33% | +0.28 | — | — |
| SR_FLIP_RETEST | 4 | 0/4/0 | 0% | -0.88 | — | — |
| LIQUIDATION_REVERSAL | 2 | 0/2/0 | 0% | -1.23 | — | — |

- **Strongest cells**: `DIVERGENCE_CONTINUATION @ OFF_HOURS/QUIET/COMPRESSED/BTC_RISING` +1.34R (n=25, STRONG); `DIVERGENCE_CONTINUATION @ OFF_HOURS/QUIET/COMPRESSED/BTC_RISING/MIDCAP` +1.34R (n=25, STRONG); `MOVER_TREND_PULLBACK @ ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR` +1.17R (n=32, STRONG)
- **Weakest cells**: `FAILED_AUCTION_RECLAIM @ ASIA/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.19R (n=18, NEGATIVE); `FAILED_AUCTION_RECLAIM @ ASIA/QUIET/NORMAL/BTC_NEUTRAL` -1.19R (n=18, NEGATIVE); `WHALE_MOMENTUM @ LONDON/MARKUP/NORMAL/BTC_RISING/MAJOR` -1.16R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| MEAN_REVERT | 15 | 80% / +0.63R | 15 | 80% / +0.82R | +0.18 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 15 | 40% / -0.18R | 15 | 40% / -0.31R | -0.13 | **FIXED** |
| TREND_PULLBACK_EMA | 79 | 53% / -0.09R | 79 | 62% / +0.03R | +0.12 | **ATR** |
| DIVERGENCE_CONTINUATION | 79 | 65% / +0.18R | 79 | 66% / +0.10R | -0.09 | **FIXED** |
| WHALE_MOMENTUM | 49 | 22% / -0.51R | 49 | 24% / -0.44R | +0.07 | **ATR** |
| MOVER_TREND_PULLBACK | 2028 | 60% / +0.06R | 2028 | 64% / +0.10R | +0.04 | **ATR** |
| FAILED_AUCTION_RECLAIM | 39 | 31% / -0.40R | 39 | 33% / -0.38R | +0.02 | **ATR** |
| MOVER_AVWAP_SCALP | 95 | 59% / +0.01R | 95 | 64% / +0.03R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 29 | 62% / +0.02R | 29 | 62% / +0.03R | +0.01 | **ATR** |
| FUNDING_EXTREME_SIGNAL | 14 | 29% / -0.36R | 14 | 50% / -0.05R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 14 | 43% / -0.03R | 14 | 43% / -0.01R | — | **MEASURING** |
| RANGE_FADE | 4 | 50% / +0.44R | 4 | 50% / +0.24R | — | **MEASURING** |
| SR_FLIP_RETEST | 3 | 0% / -0.97R | 3 | 0% / -0.40R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 2 | 0% / -0.28R | 2 | 0% / -0.20R | — | **MEASURING** |
| BREAKDOWN_SHORT | 2 | 0% / -0.70R | 2 | 0% / -0.67R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 2811 | 35% | +0.03R | 150 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 95 | 61% | +0.02R | 46 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 9 | 67% | +0.14R | 8 | MEASURING |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 26 | 23% / +0.07R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 43 | 77% / +2.53R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 2059 | 45% / +0.14R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 157 | 45% / +0.53R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 31 | 26% / -0.42R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 88 | 49% / +0.72R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 98 | 49% / +0.07R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 17 | 29% / -0.71R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 16 | 25% / -0.23R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 14 | 21% / -0.54R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 14 | 79% / +0.80R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 6 | 17% / -0.59R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 4 | 50% / +0.21R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 4 | 0% / -0.77R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 4 | 0% / -0.79R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 1 | 0% / -1.23R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 51 · alerting: **5** · boot grace active: False
- **ALERT** `sar_alignment_crosscheck` — 735/11042 disagreed (6.7%) (streak 52/6) (sustained 52 cycles)
- **ALERT** `cohort_edge_gate` — all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 12 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 52/6) (sustained 52 cycles)
- **ALERT** `mean_revert_emission` — 386 detections since last emission (emitted_total=1) — and only 156 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 14/6) (sustained 14 cycles)
- **ALERT** `range_fade_emission` — 1621 detections since last emission (emitted_total=0) — and only 18 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 52/6) (sustained 52 cycles)
- **ALERT** `tuned_variants` — 79 non-stamps — atr_arm_uncomputable=79 (seen=4906 stamped=645 skipped=4182) (streak 33/6) (sustained 33 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 6435078 accepted, 0 rejected | 0 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 23 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 4/12) | 4 |
| auto_dispatch | ok | attempts=8 fanouts=8 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 77852.70 | 0 |
| candle_coverage | ok | 122/128 symbols with ≥20 15m candles, 118/128 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 140 dup bars, 0 undedupable; ws 0 out-of-order, 57 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 12 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 52/6) | 52 |
| context_emission_policy | ok | output +176 / upstream +21 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1144/1157 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 1 of 117 open dark rows are not being advanced (worst: HANAUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 52/120) | 52 |
| dark_sar_arms | ok | no open arms; covering 1139/1152 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 1453076 msgs, 0 rejected | 0 |
| edge_reconciliation | ok | no strategy past reconciliation sample floor yet | 0 |
| emission_controller | ok | last cycle 980s ago; live_overrides=27 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=15 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4255 stamps (MEAN_REVERT=150, MOVER_AVWAP_SCALP=122, MOVER_TREND_PULLBACK=3663, RANGE_FADE=271, TREND_PULLBACK_EMA=49), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | 7626 evaluated, 2654 suppressed, 4424 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +15 / upstream +351 | 0 |
| indicator_cache_key | ok | 6569 frozen value(s) avoided; 0 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 386 detections since last emission (emitted_total=1) — and only 156 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 14/6) | 14 |
| mean_revert_path | ok | output +21 / upstream +351 | 0 |
| mover_admission_metadata | ok | 872 symbols known, 170 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 45 held, 45 with scan counts, 45 with an activity reading (measuring only) | 0 |
| position_lock_integrity | ok | 3 locked / 3 active symbol(s); 2 orphan(s) dropped at restore | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2890 rows held, 630927 evicted (sampled: execution:overextended 400/231553, execution:trigger_not_confirmed 400/219376, setup_compat:regime_STRONG_TREND 400/79307) | 0 |
| price_action_lane | ok | 112461 evaluated, 157 emitted; layer1 157 stamped / 0 blind; cooldown=14373, delta_opposed=9665, no_footprint=58911, no_opposing_target=804, no_sweep=20687, rr_below_floor=7864 | 0 |
| promoted_pair_integrity | ok | 45/45 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 1621 detections since last emission (emitted_total=0) — and only 18 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 52/6) | 52 |
| range_fade_path | ok | output +45 / upstream +351 | 0 |
| sar_alignment_crosscheck | violating | 735/11042 disagreed (6.7%) (streak 52/6) | 52 |
| sar_exit_shadow | ok | output +10 / upstream +351 | 0 |
| sar_hold_arm | ok | 289 held arms settled, 65 unscored, 24 still walking (19 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 23/220 unfetchable (10%); top cause: gap or duplicate bar in the 15m window; symbols: APTUSDT, ARBUSDT, ENAUSDT, FILUSDT, LITUSDT +8 more | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 23 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 4/12) | 4 |
| sar_refresh_budget | ok | 3 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 4 resolved, 193 still mid-window | 0 |
| scan_cycle | ok | last 47.25s, worst 118.3s over 1103 cycles; 6 over 60s, 0 over the 120s healthcheck deadline (plus 1/0 during boot warm-up, not counted); 8 executor workers | 0 |
| setup_tf_resolver | ok | 77685 resolutions, 62933 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 5m ago | 0 |
| snapshot_writer | ok | last cycle 2s ago (14.98s to run, worst 72.43s), 103 overrun(s) of 1170 cycles, TTL 900s; slowest activity=0.5s, signals=0.26s, agents=0.24s | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +161 / upstream +351 | 0 |
| structural_snap | ok | 4233/4233 measured, 27 blind, 0 levels moved (refusals: redetect_cooldown=1161) | 0 |
| structural_veto_lane | ok | 1580 stamped; 0 with no readable level book, 24 with clear air ahead, 977 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +351 / upstream +21 | 0 |
| tuned_variants | violating | 79 non-stamps — atr_arm_uncomputable=79 (seen=4906 stamped=645 skipped=4182) (streak 33/6) | 33 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `64721`
- `Path funnel` emissions: `11`
- `Regime distribution` emissions: `11`
- `QUIET_SCALP_BLOCK` events: `22`
- `confidence_gate` events: `6299`
- `free_channel_post` events: `5`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **3**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 3434 | 3434 | 3434 | 0 |
| futures_aggtrade | 1 | 11319 | 11319 | 11319 | 0 |
| futures_depth | 1 | 3732 | 3732 | 3732 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **5**

| Source | Count |
|---|---:|
| signal_close | 5 |

- By severity: HIGH=5

## Dependency readiness
- cvd: presence[present=82789] state[populated=82789] buckets[many=82671, some=118] sources[none] quality[none]
- funding_rate: presence[absent=20370, present=62419] state[empty=20370, populated=62419] buckets[few=62419, none=20370] sources[none] quality[none]
- liquidation_clusters: presence[absent=36563, present=46226] state[empty=36563, populated=46226] buckets[few=35055, none=36563, some=11171] sources[none] quality[none]
- oi_snapshot: presence[absent=20034, present=62755] state[empty=20034, populated=62755] buckets[many=62755, none=20034] sources[none] quality[none]
- order_book: presence[absent=29052, present=53737] state[populated=53737, unavailable=29052] buckets[few=53737, none=29052] sources[book_ticker=53737, unavailable=29052] quality[none=29052, top_of_book_only=53737]
- orderblocks: presence[absent=82789] state[empty=82789] buckets[none=82789] sources[measured_dark=82789] quality[none]
- recent_ticks: presence[present=82789] state[populated=82789] buckets[many=82789] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `25.323729038238525` sec
- Median create→first breach: `10285.711962938309` sec
- Median create→terminal: `10469.0824239254` sec
- Median first breach→terminal: `13.166614055633545` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MEAN_REVERT | 1 | 1 | 2.40660417478823 | 2.7415873015872987 | 0.8778141675061293 | 0 | 1 |
| MOVER_AVWAP_SCALP | 1 | 1 | 2.422769489429131 | 2.981999999999994 | 0.8124646175148008 | 0 | 1 |
| MOVER_TREND_PULLBACK | 7 | 7 | 3.2902218054938945 | 2.733776188042924 | 1.0967406018312982 | 4 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MEAN_REVERT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.6099 | 12837.210845947266 | 12838.93161892891 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 73066.00213980675 | 73066.50889801979 |
| MOVER_TREND_PULLBACK | 7 | 7 | 0.0 | 0.0 | 0.0 | 0.0 | 2.2833 | 9609.2457280159 | 9652.840807199478 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 154 | 0 | 134 | 0.0 | 0.0 | None | None | 20 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 441 | 9 | 282 | 0.0 | 0.0 | None | None | 159 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `350`
- Gating Δ: `20614`
- No-generation Δ: `369052`
- Fast failures Δ: `-1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 2.9406, "current_avg_pnl": 2.2833, "current_win_rate": 0.0, "previous_avg_pnl": -0.6573, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 20, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 9, "geometry_changed_delta": 0, "geometry_preserved_delta": 159, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
