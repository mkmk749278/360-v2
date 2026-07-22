# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `4221` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| DIVERGENCE_CONTINUATION | 0 | 0 | 7254 | 7254 | 6574 | 12 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 46368 | 46376 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 35555 | 35557 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 35408 | 33509 | 2042 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 35571 | 34137 | 1531 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 38622 | 38553 | 75 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 34630 | 34635 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 35672 | 35685 | 4 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 35689 | 32663 | 3432 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 47575 | 49718 | 42 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::MOVER_TREND_PULLBACK | 46377 | 42913 | 4643 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 37015 | 37018 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 35559 | 35566 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 35386 | 35222 | 185 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 36095 | 34544 | 1895 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 33775 | 33733 | 1638 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 31225 | 29351 | 2019 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 31370 | 31166 | 230 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 46354 | 46367 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 34639 | 34621 | 42 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 5540 | 5540 | 3653 | 16 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 410 | 410 | 400 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 10857 | 10857 | 10800 | 7 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7850 | 7850 | 7050 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 97 | 97 | 96 | 1 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 12936 | 12936 | 10026 | 10 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 33 | 33 | 33 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1019 | 1019 | 506 | 8 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 5371 | 5371 | 5371 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 7552 | 7552 | 6344 | 5 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1112 | 1112 | 1107 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 29 | 29 | 0 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 2636 | 2636 | 2555 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=46376): breakout_not_found=22730, basic_filters_failed=15815, move_not_fresh=5506, breakout_stale=1956, retest_proximity_failed=335, volume_spike_missing=21, ema_alignment_reject=12, move_exhausted=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=35557): cls_disabled_merged_into_lsr=35557
- **EVAL::DIVERGENCE_CONTINUATION** (total=33509): cvd_divergence_failed=12460, basic_filters_failed=8986, h1_trend_not_aligned=8704, ema_alignment_reject=3009, retest_proximity_failed=258, missing_fvg_or_orderblock=92
- **EVAL::FAILED_AUCTION_RECLAIM** (total=34137): auction_not_detected=12370, basic_filters_failed=8840, reclaim_hold_failed=7557, tail_too_small=4626, regime_blocked=715, rsi_reject=29
- **EVAL::FUNDING_EXTREME** (total=38553): funding_not_extreme=25582, basic_filters_failed=10745, ema_alignment_reject=1313, missing_funding_rate=405, momentum_reject=234, rsi_reject=120, cvd_divergence_failed=111, missing_fvg_or_orderblock=43
- **EVAL::LIQUIDATION_REVERSAL** (total=34635): cascade_threshold_not_met=23358, basic_filters_failed=10965, cvd_divergence_failed=190, rsi_reject=119, missing_fvg_or_orderblock=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=35685): no_ma_cross=26438, basic_filters_failed=8992, ma_cross_cooldown=203, ma_cross_htf_misaligned=52
- **EVAL::MEAN_REVERT** (total=32663): no_extension=26953, basic_filters_failed=5710
- **EVAL::MOVER_AVWAP_SCALP** (total=49720): basic_filters_failed=14021, no_avwap_tag=13798, no_mover_leg=11170, no_avwap_reclaim=3935, avwap_slope_against=2948, insufficient_candles=2771, avwap_reclaim_no_volume=1077
- **EVAL::MOVER_TREND_PULLBACK** (total=42913): mover_run_too_small=15143, basic_filters_failed=13991, no_reclaim=9720, insufficient_candles=2771, no_pullback_tag=1288
- **EVAL::OPENING_RANGE_BREAKOUT** (total=37018): feature_disabled=37018
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=35566): regime_blocked=22566, breakout_not_found=8730, basic_filters_failed=2573, adx_reject=1685, ema_alignment_reject=12
- **EVAL::QUIET_COMPRESSION_BREAK** (total=35222): regime_blocked=13678, compression_not_detected=10272, basic_filters_failed=6265, breakout_not_detected=4588, volume_confirmation_failed=381, missing_fvg_or_orderblock=29, rsi_reject=9
- **EVAL::RANGE_FADE** (total=34544): no_range_edge=28834, basic_filters_failed=5710
- **EVAL::SR_FLIP_RETEST** (total=33733): basic_filters_failed=8830, flip_close_not_confirmed=5741, long_break_volume_thin=4294, whipsaw_flip=4233, long_disabled=3603, retest_out_of_zone=2784, reclaim_hold_failed=2437, regime_blocked=708, wick_quality_failed=703, long_acceptance_not_held=179, ema_alignment_reject=109, missing_fvg_or_orderblock=92, rsi_reject=20
- **EVAL::STANDARD** (total=29351): momentum_reject=10581, adx_reject=5483, basic_filters_failed=4842, sweeps_not_detected=3694, macd_reject=2769, ema_alignment_reject=1650, invalid_sl_geometry=204, rsi_reject=119, mtf_reject=9
- **EVAL::TREND_PULLBACK** (total=31166): h1_trend_not_aligned=11537, ema_alignment_reject=4377, basic_filters_failed=4188, h1_pullback_not_confirmed=3154, no_ema_reclaim_close=2219, ema_not_tested_prev=1937, rsi_reject=1656, body_conviction_fail=1262, prev_already_above_emas=454, no_prev_high_break=194, momentum_flat=108, ema21_not_tagged=28, prev_already_below_emas=23, no_prev_low_break=18, missing_fvg_or_orderblock=9, momentum_reject=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=46367): breakout_not_found=22494, basic_filters_failed=15812, move_not_fresh=5612, breakout_stale=1883, retest_proximity_failed=517, volume_spike_missing=37, move_exhausted=10, ema_alignment_reject=1, missing_fvg_or_orderblock=1
- **EVAL::WHALE_MOMENTUM** (total=34621): momentum_reject=29164, recent_ticks_insufficient=5130, basic_filters_failed=327

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=97): setup_compat:regime_VOLATILE_UNSUITABLE=92, execution:overextended=5
- **FAILED_AUCTION_RECLAIM** (total=1713): setup_compat:regime_STRONG_TREND=745, context_floor=548, execution:overextended=390, setup_compat:regime_VOLATILE_UNSUITABLE=30
- **FUNDING_EXTREME_SIGNAL** (total=380): execution:trigger_not_confirmed=380
- **LIQUIDATION_REVERSAL** (total=1): execution:trigger_not_confirmed=1
- **LIQUIDITY_SWEEP_REVERSAL** (total=2869): execution:overextended=1296, execution:trigger_not_confirmed=1159, setup_compat:regime_STRONG_TREND=414
- **MA_CROSS_TREND_SHIFT** (total=4): setup_compat:regime_DIRTY_RANGE=3, execution:overextended=1
- **MEAN_REVERT** (total=5277): execution:overextended=2374, setup_compat:regime_WEAK_TREND=2132, setup_compat:regime_STRONG_TREND=551, context_floor=220
- **MOVER_AVWAP_SCALP** (total=96): execution:overextended=96
- **MOVER_TREND_PULLBACK** (total=9793): execution:overextended=4994, execution:trigger_not_confirmed=4799
- **QUIET_COMPRESSION_BREAK** (total=348): context_floor=346, execution:trigger_not_confirmed=2
- **RANGE_FADE** (total=772): setup_compat:regime_WEAK_TREND=500, setup_compat:regime_STRONG_TREND=272
- **TREND_PULLBACK_EMA** (total=1033): setup_compat:regime_CLEAN_RANGE=775, setup_compat:regime_DIRTY_RANGE=258
- **WHALE_MOMENTUM** (total=2509): execution:trigger_not_confirmed=2509

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 77582 | 32.0% |
| QUIET | 69064 | 28.5% |
| TRENDING_UP | 43356 | 17.9% |
| TRENDING_DOWN | 43039 | 17.7% |
| VOLATILE | 9481 | 3.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **134**
- Average confidence gap to threshold: **12.96** (samples=134) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ENAUSDT=30, ZECUSDT=21, INJUSDT=10, LDOUSDT=10, LTCUSDT=10, BTCUSDT=10, TRUMPUSDT=9, AVAXUSDT=9, LINKUSDT=6, XRPUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 38 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 51 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 77 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 51 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 295 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 10 |
| MEAN_REVERT | kept | min_confidence_pass | 281 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 1 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 35 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2357 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 67 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 17 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 83 |
| SR_FLIP_RETEST | filtered | min_confidence | 155 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 31 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 45 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 1 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 10 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 19 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 38 | 55.92 | 64.74 | 8.82 | 20.40 | 19.96 | 15.94 | 0.39 | 10.91 |
| DIVERGENCE_CONTINUATION | kept | 51 | 68.83 | 65.00 | -3.83 | 21.73 | 19.90 | 16.35 | 0.49 | 4.24 |
| FAILED_AUCTION_RECLAIM | filtered | 128 | 52.75 | 64.34 | 11.59 | 20.66 | 19.63 | 20.00 | 4.80 | 8.02 |
| FAILED_AUCTION_RECLAIM | kept | 295 | 69.61 | 65.00 | -4.61 | 20.64 | 19.34 | 20.00 | 4.51 | 0.05 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 51.30 | 65.00 | 13.70 | 17.50 | 19.10 | 20.00 | 2.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 59.20 | 65.00 | 5.80 | 21.20 | 17.60 | 17.00 | 3.00 | 12.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 10 | 70.13 | 65.00 | -5.13 | 20.51 | 19.90 | 18.33 | 1.70 | 3.12 |
| MEAN_REVERT | kept | 281 | 69.60 | 65.00 | -4.60 | 20.96 | 18.10 | 16.24 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 1 | 74.20 | 65.00 | -9.20 | 16.50 | 15.80 | 15.80 | 3.50 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 35 | 57.53 | 65.00 | 7.47 | 20.51 | 17.14 | 15.80 | 5.11 | 21.60 |
| MOVER_TREND_PULLBACK | kept | 2357 | 76.63 | 65.00 | -11.63 | 20.30 | 17.40 | 15.80 | 4.44 | 0.18 |
| QUIET_COMPRESSION_BREAK | filtered | 84 | 56.05 | 65.00 | 8.95 | 21.09 | 19.06 | 20.00 | 0.00 | 1.66 |
| QUIET_COMPRESSION_BREAK | kept | 83 | 71.44 | 65.00 | -6.44 | 20.34 | 19.97 | 20.00 | 0.00 | 0.83 |
| SR_FLIP_RETEST | filtered | 186 | 59.66 | 64.54 | 4.88 | 19.66 | 19.83 | 15.34 | 2.29 | 9.53 |
| SR_FLIP_RETEST | kept | 45 | 68.52 | 65.00 | -3.52 | 20.11 | 19.86 | 15.28 | 1.77 | 1.65 |
| TREND_PULLBACK_EMA | kept | 1 | 72.50 | 65.00 | -7.50 | 20.70 | 18.00 | 20.00 | 4.00 | 0.00 |
| VOLUME_SURGE_BREAKOUT | filtered | 10 | 59.50 | 65.00 | 5.50 | 20.81 | 20.00 | 20.00 | 3.50 | 0.00 |
| VOLUME_SURGE_BREAKOUT | kept | 19 | 69.00 | 65.00 | -4.00 | 20.26 | 20.00 | 20.00 | 5.00 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 38 | 55.92 | 23.74 | 17.47 | 5.05 | 11.26 | 5.16 | 6.91 | 0.39 |
| DIVERGENCE_CONTINUATION | kept | 51 | 68.83 | 24.37 | 16.04 | 4.06 | 13.16 | 7.00 | 9.18 | 0.49 |
| FAILED_AUCTION_RECLAIM | filtered | 128 | 52.75 | 22.53 | 15.03 | 6.49 | 11.20 | 5.70 | 5.32 | 4.80 |
| FAILED_AUCTION_RECLAIM | kept | 295 | 69.61 | 22.69 | 14.65 | 3.50 | 10.56 | 6.44 | 7.31 | 4.51 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 51.30 | 25.00 | 8.00 | 3.00 | 17.00 | 10.00 | 6.30 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 59.20 | 25.00 | 14.00 | 12.00 | 9.00 | 2.50 | 5.70 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 10 | 70.13 | 21.60 | 16.00 | 7.20 | 13.40 | 5.90 | 7.45 | 1.70 |
| MEAN_REVERT | kept | 281 | 69.60 | 23.32 | 18.00 | 3.23 | 14.69 | 6.04 | 4.32 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 1 | 74.20 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 4.70 | 3.50 |
| MOVER_TREND_PULLBACK | filtered | 35 | 57.53 | 17.69 | 18.00 | 8.91 | 13.34 | 6.46 | 9.61 | 5.11 |
| MOVER_TREND_PULLBACK | kept | 2357 | 76.63 | 18.73 | 18.00 | 7.59 | 12.95 | 5.90 | 9.19 | 4.44 |
| QUIET_COMPRESSION_BREAK | filtered | 84 | 56.05 | 17.10 | 14.81 | 12.71 | 14.00 | 7.88 | 4.97 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 83 | 71.44 | 17.19 | 17.90 | 10.66 | 14.07 | 5.18 | 7.44 | 0.00 |
| SR_FLIP_RETEST | filtered | 186 | 59.66 | 23.26 | 16.33 | 4.98 | 12.58 | 5.65 | 4.10 | 2.29 |
| SR_FLIP_RETEST | kept | 45 | 68.52 | 20.56 | 17.56 | 6.87 | 12.80 | 5.86 | 5.90 | 1.77 |
| TREND_PULLBACK_EMA | kept | 1 | 72.50 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 7.00 | 4.00 |
| VOLUME_SURGE_BREAKOUT | filtered | 10 | 59.50 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 5.00 | 3.50 |
| VOLUME_SURGE_BREAKOUT | kept | 19 | 69.00 | 25.00 | 18.00 | 12.00 | 14.00 | 5.00 | 5.00 | 5.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 38 | 55.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 51 | 68.83 | 0.00 | 0.00 | 0.47 | 0.00 | 0.38 | 0.00 | 0.00 | 0.00 | **0.85** |
| FAILED_AUCTION_RECLAIM | filtered | 128 | 52.75 | 0.00 | 0.00 | 1.65 | 0.00 | 3.88 | 0.00 | 0.00 | 0.00 | **5.53** |
| FAILED_AUCTION_RECLAIM | kept | 295 | 69.61 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.05** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 51.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 59.20 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 10 | 70.13 | 0.00 | 0.00 | 1.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.92** |
| MEAN_REVERT | kept | 281 | 69.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 1 | 74.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 35 | 57.53 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| MOVER_TREND_PULLBACK | kept | 2357 | 76.63 | 0.00 | 0.00 | 0.00 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | **0.18** |
| QUIET_COMPRESSION_BREAK | filtered | 84 | 56.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | 0.90 | **1.16** |
| QUIET_COMPRESSION_BREAK | kept | 83 | 71.44 | 0.00 | 0.00 | 0.00 | 0.00 | 2.07 | 0.00 | 0.00 | 0.13 | **2.20** |
| SR_FLIP_RETEST | filtered | 186 | 59.66 | 0.00 | 0.00 | 0.00 | 0.00 | 2.86 | 0.00 | 0.00 | 0.29 | **3.15** |
| SR_FLIP_RETEST | kept | 45 | 68.52 | 0.00 | 0.00 | 0.00 | 0.00 | 1.12 | 0.00 | 0.00 | 0.00 | **1.12** |
| TREND_PULLBACK_EMA | kept | 1 | 72.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 10 | 59.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 19 | 69.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=1279 (33.9%) | WOULD_LOSE=406 | WOULD_EXPIRE=2086 | pending (awaiting window)=1229

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_floor:DIVERGENCE_CONTINUATION | 2 | 0.0% | 2.0 | 0.0 | +1.00 | **INSUFFICIENT_SAMPLE** |
| context_floor:FAILED_AUCTION_RECLAIM | 634 | 0.0% | 58.0 | 0.0 | +0.09 | **TUNE** |
| context_floor:MEAN_REVERT | 248 | 100.0% | 0.0 | 338.4 | -1.36 | **DROP** |
| context_floor:QUIET_COMPRESSION_BREAK | 348 | 0.0% | 0.0 | 0.0 | +0.00 | **TUNE** |
| dispatch_cooldown | 38 | 0.0% | 0.0 | 0.0 | +0.00 | **TUNE** |
| dispatch_staleness | 1661 | 55.6% | 84.0 | 1124.0 | -0.63 | **DROP** |
| level_still_in_play | 313 | 11.8% | 4.0 | 14.9 | -0.03 | **TUNE** |
| min_confidence | 335 | 6.3% | 197.0 | 27.5 | +0.51 | **KEEP** |
| quiet_scalp_block | 132 | 25.0% | 23.0 | 46.5 | -0.18 | **TUNE** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 1 | 0.0% | 0.0 | 0.0 | +0.00 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_MEAN_REVERT | 38 | 34.2% | 20.0 | 21.8 | -0.05 | **TUNE** |
| shadow_unit:SHADOW_RANGE_FADE | 21 | 14.3% | 18.0 | 8.3 | +0.46 | **KEEP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 48425 across 20 strategies; 1102 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 13038 | 33/13005/0 | 64% | +0.26 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+1.27R) | LONDON/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.00R) |
| FAILED_AUCTION_RECLAIM | 8724 | 17/8707/0 | 53% | +0.09 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | LONDON/MARKDOWN/NORMAL/BTC_FALLING (-1.00R) |
| SR_FLIP_RETEST | 8079 | 2/8077/0 | 42% | -0.10 | ASIA/RANGE/NORMAL/BTC_NEUTRAL (+1.18R) | LONDON/MARKDOWN/EXPANDED/BTC_FALLING (-1.00R) |
| DIVERGENCE_CONTINUATION | 4208 | 5/4203/0 | 48% | +0.06 | OVERLAP/MARKUP/EXPANDED/BTC_NEUTRAL (+1.46R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL (-1.00R) |
| QUIET_COMPRESSION_BREAK | 3438 | 0/3438/0 | 48% | +0.13 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (+2.21R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_MEAN_REVERT | 2318 | 0/0/2318 | 34% | -0.13 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.91R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| SHADOW_RANGE_FADE | 2052 | 0/0/2052 | 36% | +0.17 | OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL (+1.78R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| LIQUIDITY_SWEEP_REVERSAL | 1577 | 3/1574/0 | 33% | -0.19 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_FUNDING_FADE | 1214 | 0/0/1214 | 32% | -0.43 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL (+0.60R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| MEAN_REVERT | 1154 | 0/1154/0 | 66% | +0.39 | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (+1.27R) | NY/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 660 | 6/654/0 | 28% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| TREND_PULLBACK_EMA | 497 | 0/497/0 | 32% | -0.26 | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.27R) | OFF_HOURS/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.89R) |
| RANGE_FADE | 388 | 0/388/0 | 15% | -0.11 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | LONDON/DISTRIBUTION/NORMAL/BTC_RISING (-1.00R) |
| BREAKDOWN_SHORT | 237 | 5/232/0 | 54% | +0.32 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| WHALE_MOMENTUM | 234 | 0/234/0 | 55% | -0.05 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 226 | 0/226/0 | 44% | +0.18 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| MOVER_AVWAP_SCALP | 209 | 8/201/0 | 18% | -0.65 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 163 | 0/0/163 | 47% | -0.11 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.20R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| POST_DISPLACEMENT_CONTINUATION | 7 | 0/7/0 | 0% | -1.00 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 1/1/0 | 50% | +0.35 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `QUIET_COMPRESSION_BREAK @ OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL` +2.21R (n=29, STRONG)
- **Weakest cells**: `FAILED_AUCTION_RECLAIM @ ASIA/DISTRIBUTION/NORMAL/BTC_RISING/ALTCOIN` -1.00R (n=22, NEGATIVE); `FAILED_AUCTION_RECLAIM @ ASIA/DISTRIBUTION/NORMAL/BTC_RISING/MIDCAP` -1.00R (n=22, NEGATIVE); `FAILED_AUCTION_RECLAIM @ ASIA/MARKDOWN/COMPRESSED/BTC_RISING/MIDCAP` -1.00R (n=16, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| MOVER_AVWAP_SCALP | 39 | 41% / -0.12R | 39 | 54% / +0.07R | +0.19 | **ATR** |
| TREND_PULLBACK_EMA | 19 | 53% / -0.09R | 19 | 58% / +0.10R | +0.19 | **ATR** |
| RANGE_FADE | 16 | 19% / +0.09R | 16 | 19% / -0.09R | -0.18 | **FIXED** |
| WHALE_MOMENTUM | 18 | 33% / -0.18R | 18 | 28% / -0.29R | -0.10 | **FIXED** |
| VOLUME_SURGE_BREAKOUT | 20 | 40% / -0.04R | 20 | 35% / -0.10R | -0.06 | **FIXED** |
| MOVER_TREND_PULLBACK | 1046 | 65% / +0.21R | 1046 | 69% / +0.15R | -0.06 | **FIXED** |
| SR_FLIP_RETEST | 1064 | 45% / -0.07R | 1064 | 49% / -0.01R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 174 | 44% / -0.08R | 174 | 51% / -0.03R | +0.05 | **ATR** |
| MEAN_REVERT | 71 | 46% / -0.03R | 71 | 44% / +0.01R | +0.03 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1024 | 50% / +0.02R | 1024 | 48% / +0.04R | +0.03 | **ATR** |
| DIVERGENCE_CONTINUATION | 228 | 50% / +0.01R | 228 | 55% / -0.01R | -0.02 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 517 | 47% / +0.02R | 517 | 46% / +0.03R | +0.00 | **ATR** |
| BREAKDOWN_SHORT | 8 | 25% / -0.27R | 8 | 25% / -0.18R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 2 | 0% / -1.00R | 2 | 100% / +0.22R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -0.64R | 1 | 0% / -1.00R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 1 | 0% / +0.00R | 1 | 0% / +0.00R | — | **MEASURING** |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 15 · alerting: **2** · boot grace active: False
- **ALERT** `mean_revert_emission` — 3253 detections since last emission (emitted_total=2) — check gate rejections (streak 29/6) (sustained 29 cycles)
- **ALERT** `range_fade_emission` — 7347 detections since last emission/context-block (emitted_total=0 context_blocked=164) — check gate rejections (streak 98/6) (sustained 98 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=10 fanouts=10 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 66250.00 | 0 |
| candle_coverage | ok | 91/100 symbols with ≥20 15m candles | 0 |
| context_emission_policy | ok | output +85 / upstream +40 | 0 |
| emission_controller | ok | last cycle 611s ago; live_overrides=11 | 0 |
| geometry_ab | ok | output +2 / upstream +81 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 3253 detections since last emission (emitted_total=2) — check gate rejections (streak 29/6) | 29 |
| mean_revert_path | ok | output +117 / upstream +81 | 0 |
| range_fade_emission | violating | 7347 detections since last emission/context-block (emitted_total=0 context_blocked=164) — check gate rejections (streak 98/6) | 98 |
| range_fade_path | ok | output +82 / upstream +81 | 0 |
| shadow_units | ok | last shadow stamp 18m ago | 0 |
| strategy_edge | ok | output +165 / upstream +81 | 0 |
| suppression_audit | ok | output +81 / upstream +40 | 0 |
| tuned_variants | ok | seen=42 stamped=6 skipped=36 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `66725`
- `Path funnel` emissions: `27`
- `Regime distribution` emissions: `27`
- `QUIET_SCALP_BLOCK` events: `134`
- `confidence_gate` events: `3626`
- `free_channel_post` events: `5`
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
- Total posts in window: **5**

| Source | Count |
|---|---:|
| signal_close | 3 |
| regime_shift | 2 |

- By severity: HIGH=5

## Dependency readiness
- cvd: presence[present=182476] state[populated=182476] buckets[many=182476] sources[none] quality[none]
- funding_rate: presence[absent=27013, present=155463] state[empty=27013, populated=155463] buckets[few=155463, none=27013] sources[none] quality[none]
- liquidation_clusters: presence[absent=114262, present=68214] state[empty=114262, populated=68214] buckets[few=56939, none=114262, some=11275] sources[none] quality[none]
- oi_snapshot: presence[absent=27013, present=155463] state[empty=27013, populated=155463] buckets[many=155463, none=27013] sources[none] quality[none]
- order_book: presence[absent=51415, present=131061] state[populated=131061, unavailable=51415] buckets[few=131061, none=51415] sources[book_ticker=131061, unavailable=51415] quality[none=51415, top_of_book_only=131061]
- orderblocks: presence[absent=182476] state[empty=182476] buckets[none=182476] sources[not_implemented=182476] quality[none]
- recent_ticks: presence[absent=8098, present=174378] state[empty=8098, populated=174378] buckets[many=174378, none=8098] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.460831642150879` sec
- Median create→first breach: `3910.9685875177383` sec
- Median create→terminal: `3912.563796043396` sec
- Median first breach→terminal: `1.76362943649292` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 10.0}, "under_180s": {"count": 1, "pct": 10.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 10.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 100.0 | 0.0 | 100.0 | 0.0 | 7.4564 | 24048.455218553543 | 24052.408754587173 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -0.075 | 23128.853261590004 | 23129.905124545097 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 33.59271788597107 | 34.02080702781677 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.0749 | 5109.097215890884 | 5110.4571850299835 |
| MOVER_TREND_PULLBACK | 4 | 4 | 0.0 | 50.0 | 0.0 | 0.0 | -1.2207 | 1158.8565390110016 | 1159.8924590349197 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 7552 | 5 | 6344 | 0.0 | 0.0 | None | None | 1208 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1112 | 1 | 1107 | 0.0 | 0.0 | None | None | 5 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `61`
- Gating Δ: `54520`
- No-generation Δ: `701334`
- Fast failures Δ: `1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.0921, "current_avg_pnl": -1.2207, "current_win_rate": 0.0, "previous_avg_pnl": -1.3128, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 5, "geometry_changed_delta": 0, "geometry_preserved_delta": 1208, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -9530.65, "median_terminal_delta_sec": -9532.03, "sl_rate_delta": 0.0, "win_rate_delta": -100.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 5, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
