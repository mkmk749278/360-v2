# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: DIVERGENCE_CONTINUATION, MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: QUIET_COMPRESSION_BREAK
- Recommended next investigation target: **DIVERGENCE_CONTINUATION**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `8297` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 25 | 25 | 25 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10278 | 10278 | 9613 | 15 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 48939 | 48966 | 3 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 52112 | 52112 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 51402 | 48834 | 3258 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 52160 | 51488 | 793 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 51852 | 51711 | 183 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 44729 | 44755 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 52293 | 52349 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 52367 | 50769 | 2548 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 51855 | 55680 | 310 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 48974 | 46768 | 5023 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 51430 | 51430 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 52119 | 52140 | 9 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 51347 | 51192 | 202 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 53325 | 52357 | 1501 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 50887 | 51095 | 196 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 43886 | 42761 | 1353 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 44120 | 43816 | 413 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 48884 | 48929 | 3 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 44756 | 44768 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2854 | 2854 | 2541 | 3 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 693 | 693 | 77 | 1 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 8652 | 8652 | 8529 | 5 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 11 | 11 | 5 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 6400 | 6400 | 5131 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 837 | 837 | 208 | 35 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 14760 | 14760 | 5686 | 243 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 20 | 20 | 20 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1203 | 1203 | 592 | 62 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 3860 | 3860 | 3199 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 758 | 758 | 230 | 8 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1971 | 1971 | 1707 | 26 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 22 | 22 | 14 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=48966): breakout_not_found=24744, basic_filters_failed=14129, move_not_fresh=7913, breakout_stale=1715, retest_proximity_failed=378, volume_spike_missing=85, missing_fvg_or_orderblock=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=52112): cls_disabled_merged_into_lsr=52112
- **EVAL::DIVERGENCE_CONTINUATION** (total=48834): cvd_divergence_failed=22207, basic_filters_failed=13478, h1_trend_not_aligned=9190, ema_alignment_reject=3287, retest_proximity_failed=369, missing_fvg_or_orderblock=303
- **EVAL::FAILED_AUCTION_RECLAIM** (total=51488): auction_not_detected=33127, basic_filters_failed=13250, reclaim_hold_failed=2576, tail_too_small=1516, regime_blocked=998, rsi_reject=21
- **EVAL::FUNDING_EXTREME** (total=51711): funding_not_extreme=35625, basic_filters_failed=13574, ema_alignment_reject=1683, rsi_reject=485, cvd_divergence_failed=169, momentum_reject=130, missing_funding_rate=33, missing_fvg_or_orderblock=12
- **EVAL::LIQUIDATION_REVERSAL** (total=44755): cascade_threshold_not_met=31346, basic_filters_failed=13200, rsi_reject=109, cvd_divergence_failed=95, missing_fvg_or_orderblock=4, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=52349): no_ma_cross=38153, basic_filters_failed=13507, ma_cross_cooldown=417, ma_cross_htf_misaligned=272
- **EVAL::MEAN_REVERT** (total=50769): no_extension=44821, basic_filters_failed=5948
- **EVAL::MOVER_AVWAP_SCALP** (total=55680): no_mover_leg=21075, no_avwap_tag=15749, basic_filters_failed=14470, avwap_slope_against=2624, avwap_reclaim_no_volume=961, no_avwap_reclaim=781, anchor_too_recent=20
- **EVAL::MOVER_TREND_PULLBACK** (total=46768): mover_run_too_small=25746, basic_filters_failed=14298, no_reclaim=5794, no_pullback_tag=930
- **EVAL::OPENING_RANGE_BREAKOUT** (total=51430): feature_disabled=51430
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=52140): regime_blocked=34445, breakout_not_found=11991, basic_filters_failed=2831, adx_reject=2799, ema_alignment_reject=71, rsi_reject=3
- **EVAL::QUIET_COMPRESSION_BREAK** (total=51192): regime_blocked=18520, compression_not_detected=14530, basic_filters_failed=10400, breakout_not_detected=7000, volume_confirmation_failed=690, rsi_reject=43, missing_fvg_or_orderblock=9
- **EVAL::RANGE_FADE** (total=52357): no_range_edge=46405, basic_filters_failed=5952
- **EVAL::SR_FLIP_RETEST** (total=51095): flip_close_not_confirmed=32655, basic_filters_failed=13209, h1_break_not_confirmed=1307, long_break_volume_thin=1286, retest_out_of_zone=992, regime_blocked=988, reclaim_hold_failed=410, long_acceptance_not_held=121, ema_alignment_reject=59, wick_quality_failed=45, missing_fvg_or_orderblock=14, whipsaw_flip=9
- **EVAL::STANDARD** (total=42761): momentum_reject=15724, adx_reject=12629, sweeps_not_detected=4645, basic_filters_failed=3899, macd_reject=3232, ema_alignment_reject=1702, htf_poi_unanchored=888, invalid_sl_geometry=23, rsi_reject=19
- **EVAL::TREND_PULLBACK** (total=43816): h1_trend_not_aligned=10176, basic_filters_failed=9070, ema_alignment_reject=7152, h1_pullback_not_confirmed=4248, no_ema_reclaim_close=3548, body_conviction_fail=2937, ema_not_tested_prev=2710, rsi_reject=2621, prev_already_below_emas=540, no_prev_low_break=362, prev_already_above_emas=242, no_prev_high_break=110, momentum_flat=53, momentum_reject=22, missing_fvg_or_orderblock=15, ema21_not_tagged=10
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=48929): breakout_not_found=28633, basic_filters_failed=14125, move_not_fresh=3959, breakout_stale=1694, retest_proximity_failed=422, volume_spike_missing=92, missing_fvg_or_orderblock=4
- **EVAL::WHALE_MOMENTUM** (total=44768): momentum_reject=38868, recent_ticks_insufficient=3131, basic_filters_failed=2769

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=224): setup_compat:regime_VOLATILE_UNSUITABLE=198, execution:overextended=19, setup_compat:regime_BREAKOUT_EXPANSION=7
- **FAILED_AUCTION_RECLAIM** (total=666): setup_compat:regime_STRONG_TREND=451, execution:overextended=118, context_floor=89, setup_compat:regime_VOLATILE_UNSUITABLE=8
- **FUNDING_EXTREME_SIGNAL** (total=546): execution:trigger_not_confirmed=546
- **LIQUIDITY_SWEEP_REVERSAL** (total=2109): execution:trigger_not_confirmed=980, setup_compat:regime_STRONG_TREND=655, execution:overextended=474
- **MA_CROSS_TREND_SHIFT** (total=7): setup_compat:regime_DIRTY_RANGE=3, execution:overextended=3, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=4159): setup_compat:regime_STRONG_TREND=1986, setup_compat:regime_WEAK_TREND=1708, execution:overextended=457, entry_quality=8
- **MOVER_AVWAP_SCALP** (total=533): execution:overextended=290, execution:trigger_not_confirmed=139, entry_quality=104
- **MOVER_TREND_PULLBACK** (total=6181): execution:trigger_not_confirmed=3319, execution:overextended=1480, entry_quality=1382
- **POST_DISPLACEMENT_CONTINUATION** (total=7): execution:overextended=7
- **QUIET_COMPRESSION_BREAK** (total=27): execution:trigger_not_confirmed=27
- **RANGE_FADE** (total=2133): setup_compat:regime_WEAK_TREND=1188, setup_compat:regime_STRONG_TREND=817, setup_compat:regime_VOLATILE_UNSUITABLE=122, execution:overextended=6
- **TREND_PULLBACK_EMA** (total=1752): setup_compat:regime_CLEAN_RANGE=1391, setup_compat:regime_DIRTY_RANGE=276, setup_compat:regime_VOLATILE_UNSUITABLE=46, entry_quality=39
- **VOLUME_SURGE_BREAKOUT** (total=1): execution:overextended=1

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 114086 | 38.9% |
| RANGING | 83020 | 28.3% |
| TRENDING_DOWN | 57307 | 19.6% |
| TRENDING_UP | 29756 | 10.2% |
| VOLATILE | 8925 | 3.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **319**
- Average confidence gap to threshold: **14.85** (samples=319) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ENAUSDT=65, BNBUSDT=29, WLFIUSDT=24, TAUSDT=24, XMRUSDT=21, BTCUSDT=20, TRXUSDT=16, TIAUSDT=13, XLMUSDT=13, HBARUSDT=9

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 47 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 15 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 106 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 32 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 21 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 3 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 14 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 3 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 25 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 13 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 3 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 1 |
| MEAN_REVERT | filtered | min_confidence | 14 |
| MEAN_REVERT | kept | min_confidence_pass | 19 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 180 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 177 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1836 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 83 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2581 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 142 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 63 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 264 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 32 |
| SR_FLIP_RETEST | filtered | min_confidence | 20 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 142 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 62 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 10 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 87 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 62 | 52.77 | 64.87 | 12.10 | 20.68 | 19.66 | 18.48 | 0.16 | 15.35 |
| DIVERGENCE_CONTINUATION | kept | 106 | 69.09 | 65.00 | -4.09 | 20.95 | 19.47 | 17.17 | 0.80 | 0.78 |
| FAILED_AUCTION_RECLAIM | filtered | 53 | 53.95 | 63.58 | 9.63 | 20.12 | 19.90 | 20.00 | 3.48 | 9.18 |
| FAILED_AUCTION_RECLAIM | kept | 3 | 71.70 | 65.00 | -6.70 | 20.13 | 19.40 | 20.00 | 3.67 | 4.27 |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 50.64 | 62.18 | 11.54 | 20.85 | 15.67 | 17.32 | 3.59 | 8.80 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 63.70 | 65.00 | 1.30 | 21.20 | 14.00 | 17.00 | 3.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 25 | 44.98 | 64.52 | 19.54 | 19.44 | 19.66 | 18.80 | 0.88 | 13.67 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 13 | 71.49 | 65.00 | -6.49 | 20.41 | 18.30 | 17.62 | 2.15 | 0.00 |
| MA_CROSS_TREND_SHIFT | filtered | 4 | 51.45 | 62.00 | 10.55 | 20.65 | 18.52 | 15.80 | 0.00 | 16.75 |
| MEAN_REVERT | filtered | 14 | 56.26 | 65.00 | 8.74 | 18.86 | 15.19 | 16.26 | 0.00 | 18.17 |
| MEAN_REVERT | kept | 19 | 67.37 | 65.00 | -2.37 | 19.17 | 19.44 | 15.39 | 0.00 | 0.11 |
| MOVER_AVWAP_SCALP | filtered | 181 | 57.25 | 64.02 | 6.77 | 20.16 | 16.13 | 15.80 | 3.72 | 17.89 |
| MOVER_AVWAP_SCALP | kept | 177 | 76.85 | 65.00 | -11.85 | 20.49 | 15.98 | 15.80 | 4.40 | 5.09 |
| MOVER_TREND_PULLBACK | filtered | 1919 | 54.55 | 63.66 | 9.11 | 20.02 | 18.61 | 15.80 | 4.00 | 18.55 |
| MOVER_TREND_PULLBACK | kept | 2581 | 76.52 | 65.00 | -11.52 | 20.70 | 18.85 | 15.80 | 4.40 | 2.73 |
| QUIET_COMPRESSION_BREAK | filtered | 205 | 51.02 | 64.37 | 13.35 | 21.05 | 19.65 | 20.00 | 0.00 | 11.04 |
| QUIET_COMPRESSION_BREAK | kept | 264 | 77.26 | 65.00 | -12.26 | 21.23 | 19.86 | 20.00 | 0.00 | 0.12 |
| SR_FLIP_RETEST | filtered | 52 | 54.17 | 65.00 | 10.83 | 21.29 | 20.00 | 15.58 | 1.82 | 15.58 |
| SR_FLIP_RETEST | kept | 142 | 69.87 | 65.00 | -4.87 | 20.93 | 20.00 | 15.66 | 2.39 | 1.87 |
| TREND_PULLBACK_EMA | filtered | 72 | 53.65 | 65.00 | 11.35 | 20.38 | 19.86 | 17.55 | 5.44 | 20.22 |
| TREND_PULLBACK_EMA | kept | 87 | 77.63 | 65.00 | -12.63 | 21.07 | 19.90 | 17.24 | 4.67 | 1.30 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 87.35 | 65.00 | -22.35 | 20.95 | 16.20 | 20.00 | 5.50 | 1.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 62 | 52.77 | 20.48 | 14.29 | 5.56 | 13.90 | 5.28 | 8.43 | 0.16 |
| DIVERGENCE_CONTINUATION | kept | 106 | 69.09 | 21.23 | 14.04 | 5.72 | 13.76 | 5.59 | 9.30 | 0.80 |
| FAILED_AUCTION_RECLAIM | filtered | 53 | 53.95 | 22.58 | 15.58 | 4.42 | 11.09 | 5.48 | 6.43 | 3.48 |
| FAILED_AUCTION_RECLAIM | kept | 3 | 71.70 | 22.33 | 15.33 | 9.00 | 11.67 | 7.33 | 6.63 | 3.67 |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 50.64 | 23.59 | 8.00 | 8.12 | 12.35 | 7.76 | 3.95 | 3.59 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 63.70 | 25.00 | 8.00 | 9.00 | 12.00 | 9.00 | 2.70 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 25 | 44.98 | 23.16 | 14.32 | 6.72 | 13.68 | 5.48 | 4.59 | 0.88 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 13 | 71.49 | 22.54 | 14.31 | 5.08 | 12.38 | 6.96 | 8.07 | 2.15 |
| MA_CROSS_TREND_SHIFT | filtered | 4 | 51.45 | 19.00 | 14.00 | 4.50 | 15.50 | 6.88 | 8.32 | 0.00 |
| MEAN_REVERT | filtered | 14 | 56.26 | 20.43 | 14.00 | 15.00 | 13.00 | 5.00 | 7.00 | 0.00 |
| MEAN_REVERT | kept | 19 | 67.37 | 17.84 | 17.58 | 6.16 | 13.00 | 5.00 | 7.91 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 181 | 57.25 | 17.72 | 18.00 | 12.11 | 13.23 | 6.05 | 5.71 | 3.72 |
| MOVER_AVWAP_SCALP | kept | 177 | 76.85 | 20.51 | 18.00 | 11.86 | 13.69 | 6.18 | 7.72 | 4.40 |
| MOVER_TREND_PULLBACK | filtered | 1919 | 54.55 | 18.11 | 18.02 | 7.76 | 12.76 | 6.07 | 8.08 | 4.00 |
| MOVER_TREND_PULLBACK | kept | 2581 | 76.52 | 19.39 | 18.01 | 8.03 | 13.35 | 6.74 | 9.45 | 4.40 |
| QUIET_COMPRESSION_BREAK | filtered | 205 | 51.02 | 17.82 | 16.77 | 11.27 | 14.06 | 7.31 | 5.37 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 264 | 77.26 | 18.58 | 17.86 | 12.48 | 14.16 | 6.46 | 9.16 | 0.00 |
| SR_FLIP_RETEST | filtered | 52 | 54.17 | 20.54 | 11.85 | 6.87 | 13.42 | 6.05 | 9.21 | 1.82 |
| SR_FLIP_RETEST | kept | 142 | 69.87 | 22.97 | 12.44 | 4.73 | 14.38 | 5.99 | 9.12 | 2.39 |
| TREND_PULLBACK_EMA | filtered | 72 | 53.65 | 12.14 | 18.00 | 7.77 | 14.00 | 7.58 | 8.94 | 5.44 |
| TREND_PULLBACK_EMA | kept | 87 | 77.63 | 19.17 | 18.00 | 7.69 | 15.17 | 6.79 | 8.94 | 4.67 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 87.35 | 25.00 | 14.00 | 15.00 | 15.50 | 5.00 | 8.85 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 62 | 52.77 | 0.00 | 0.00 | 0.46 | 0.00 | 3.14 | 0.00 | 0.00 | 0.00 | **3.60** |
| DIVERGENCE_CONTINUATION | kept | 106 | 69.09 | 0.00 | 0.00 | 1.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.22** |
| FAILED_AUCTION_RECLAIM | filtered | 53 | 53.95 | 0.00 | 0.00 | 1.81 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.81** |
| FAILED_AUCTION_RECLAIM | kept | 3 | 71.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 50.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 63.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 25 | 44.98 | 0.00 | 0.00 | 1.28 | 0.00 | 1.92 | 0.00 | 0.00 | 0.00 | **3.20** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 13 | 71.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 4 | 51.45 | 0.00 | 0.00 | 4.80 | 0.00 | 3.00 | 0.00 | 0.00 | 0.00 | **7.80** |
| MEAN_REVERT | filtered | 14 | 56.26 | 0.00 | 0.00 | 0.69 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.89** |
| MEAN_REVERT | kept | 19 | 67.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 181 | 57.25 | 0.00 | 0.00 | 0.08 | 0.00 | 0.85 | 0.00 | 0.00 | 1.25 | **2.18** |
| MOVER_AVWAP_SCALP | kept | 177 | 76.85 | 0.00 | 0.00 | 0.07 | 0.00 | 1.07 | 0.00 | 0.00 | 0.08 | **1.22** |
| MOVER_TREND_PULLBACK | filtered | 1919 | 54.55 | 0.11 | 0.00 | 1.24 | 0.00 | 0.73 | 0.00 | 0.00 | 0.04 | **2.12** |
| MOVER_TREND_PULLBACK | kept | 2581 | 76.52 | 0.00 | 0.00 | 1.55 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | **1.69** |
| QUIET_COMPRESSION_BREAK | filtered | 205 | 51.02 | 0.00 | 0.00 | 1.10 | 0.00 | 0.38 | 0.00 | 0.00 | 3.27 | **4.75** |
| QUIET_COMPRESSION_BREAK | kept | 264 | 77.26 | 0.00 | 0.00 | 0.30 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | **0.42** |
| SR_FLIP_RETEST | filtered | 52 | 54.17 | 0.00 | 0.00 | 2.31 | 0.00 | 9.14 | 0.00 | 0.00 | 0.46 | **11.91** |
| SR_FLIP_RETEST | kept | 142 | 69.87 | 0.00 | 0.00 | 0.14 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | **0.22** |
| TREND_PULLBACK_EMA | filtered | 72 | 53.65 | 0.00 | 0.00 | 2.89 | 0.00 | 1.80 | 0.00 | 0.00 | 0.00 | **4.69** |
| TREND_PULLBACK_EMA | kept | 87 | 77.63 | 0.00 | 0.00 | 0.57 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | **0.82** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 87.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **178819 held of 774322 seen** across 21 strategies; 4053 cells past the sample floor; **2141 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 47704 | 608/47096/0 | 43% | -0.20 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.35R) |
| MOVER_AVWAP_SCALP | 23669 | 182/23487/0 | 44% | -0.19 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 13829 | 181/13648/0 | 45% | -0.14 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | LONDON/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 13462 | 153/13309/0 | 38% | -0.27 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 11948 | 63/11885/0 | 37% | -0.31 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 9936 | 108/9828/0 | 37% | -0.45 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 8172 | 430/7742/0 | 46% | -0.13 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8037 | 0/0/8037 | 44% | -0.07 | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (+0.67R) | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL (-0.86R) |
| SHADOW_RANGE_FADE | 7536 | 0/0/7536 | 36% | -0.13 | NY/RANGE/NORMAL/BTC_NEUTRAL (+0.43R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.26R) |
| SHADOW_FUNDING_FADE | 6920 | 0/0/6920 | 34% | -0.41 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.01R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 5629 | 19/5610/0 | 47% | -0.26 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+2.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.30R) |
| MEAN_REVERT | 5337 | 67/5270/0 | 37% | -0.33 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| FUNDING_EXTREME_SIGNAL | 3887 | 2/3885/0 | 31% | -0.47 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 3747 | 0/3747/0 | 30% | -0.36 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| RANGE_FADE | 2214 | 6/2208/0 | 41% | -0.19 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1626 | 0/0/1626 | 53% | -0.07 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 532 | 0/532/0 | 36% | -0.24 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 202 | 32/170/0 | 43% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 58 | 2/56/0 | 45% | +0.15 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `LIQUIDATION_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL` +2.71R (n=23, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 348 | 27% / -0.56R | 348 | 53% / -0.08R | +0.48 | **ATR** |
| TREND_PULLBACK_EMA | 1137 | 37% / -0.39R | 1137 | 49% / -0.09R | +0.30 | **ATR** |
| LIQUIDATION_REVERSAL | 33 | 24% / -0.61R | 33 | 45% / -0.35R | +0.26 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1532 | 42% / -0.37R | 1532 | 56% / -0.12R | +0.25 | **ATR** |
| MA_CROSS_TREND_SHIFT | 60 | 42% / -0.21R | 60 | 47% / -0.06R | +0.15 | **ATR** |
| SR_FLIP_RETEST | 583 | 44% / -0.31R | 583 | 49% / -0.16R | +0.15 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 201 | 37% / -0.18R | 201 | 48% / -0.05R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 2488 | 44% / -0.17R | 2488 | 51% / -0.05R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 8747 | 48% / -0.14R | 8747 | 54% / -0.02R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1429 | 41% / -0.22R | 1429 | 43% / -0.11R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| RANGE_FADE | 119 | 39% / -0.08R | 119 | 47% / +0.01R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1659 | 48% / -0.12R | 1659 | 53% / -0.06R | +0.06 | **ATR** |
| MEAN_REVERT | 425 | 48% / -0.13R | 425 | 47% / -0.14R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1437 | 46% / -0.14R | 1437 | 46% / -0.15R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 13 | 62% / -0.06R | 13 | 62% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11683 | 28% | -0.26R | 312 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2488 | 48% | -0.05R | 235 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 126 | 49% | -0.05R | 67 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1788 | 39% / -0.13R | +0.88 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1489 | 32% / -0.26R | +0.81 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3033 | 35% / -0.22R | +0.62 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10682 | 36% / -0.21R | +0.32 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1939 | 36% / -0.14R | +0.14 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1382 | 36% / -0.14R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1187 | 32% / -0.25R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 296 | 31% / -0.36R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 455 | 32% / -0.19R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 352 | 48% / -0.06R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 88 | 44% / +0.02R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 513 | 33% / -0.35R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 97 | 28% / -0.38R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 42 | 45% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 22 | 45% / +0.62R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **5** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×477]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 528/6) (sustained 528 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 8/6) (sustained 8 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 528/6) (sustained 528 cycles)
- **ALERT** `tuned_variants` — 365 non-stamps — atr_arm_uncomputable=365 (seen=14574 stamped=2114 skipped=12095) (streak 528/6) (sustained 528 cycles)
- **ALERT** `auto_dispatch` — 106 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=106) (streak 518/3) (sustained 518 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 48 fed / 0 quiet / 0 never delivered of 48 subscribed; 143510128 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 28 arms current, none stalled; covering 2117/2117 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +2 but output +0 (streak 1/6) | 1 |
| atr_trail_live_arms | ok | 53 arms current, none stalled; covering 1121/1121 signals (100%) | 0 |
| auto_dispatch | violating | 106 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=106) (streak 518/3) | 518 |
| binance_ip_weight | ok | peak 98/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 75819.40 | 0 |
| candle_coverage | ok | 78/78 symbols with ≥20 15m candles, 78/78 updated within 45m [fresh=78; 75 Tier-1 futures + 4 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1461 dup bars, 0 undedupable; ws 0 out-of-order, 478 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +27 / upstream +17 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 2092/2111 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 2 promoted today, nothing refused | 0 |
| dark_resolution | violating | 1 of 132 open dark rows are not being advanced (worst: WLFIUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 21/120) | 21 |
| dark_sar_arms | ok | no open arms; covering 2087/2106 signals (99%) | 0 |
| depth_feed | ok | 48/48 books fresh (stale 0, never 0, thin 0); 65177970 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 528/6) | 528 |
| emission_controller | ok | last cycle 1706s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×477]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 528/6) | 528 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 8/6) | 8 |
| firestore_read_budget | ok | 1,308 reads/day of 50,000 [engine 1,284, signing 24]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 5760 sealed bars over 48 symbols; 1680 incomplete, 2 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +21 / upstream +193 | 0 |
| indicator_cache_key | ok | 244632 frozen value(s) avoided; 1021441 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | emitted_total=10 | 0 |
| mean_revert_path | ok | output +3 / upstream +193 | 0 |
| mover_admission_metadata | ok | 942 symbols known, 235 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 4 held, 4 with scan counts, 4 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 9 locked / 9 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2156 rows held, 3425680 evicted (sampled: execution:trigger_not_confirmed 291/1209102, execution:overextended 291/1067675, setup_compat:regime_STRONG_TREND 291/585764) | 0 |
| price_action_lane | ok | 903404 evaluated, 1648 emitted; layer1 1648 stamped / 0 blind; cooldown=125392, delta_opposed=67435, no_footprint=327242, no_opposing_target=820, no_sweep=320555, rr_below_floor=60312 | 0 |
| promoted_pair_integrity | ok | 4/4 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.19R over n=2208 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | violating | upstream +193 but output +0 (streak 4/72) | 4 |
| sar_alignment_crosscheck | ok | 1453/34858 disagreed (4.2%) | 0 |
| sar_exit_shadow | ok | output +14 / upstream +193 | 0 |
| sar_hold_arm | ok | 1864 held arms settled, 136 unscored, 53 still walking (52 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 3/52 unfetchable (6%); top cause: located bar does not contain the stamp; symbols: AKEUSDT, CTUSDT, ERAUSDT | 0 |
| sar_live_arms | ok | 53 arms current, none stalled; covering 1120/1120 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 14 resolved, 35 still mid-window | 0 |
| scan_cycle | ok | last 9.43s, worst 258.77s over 11010 lifetime cycles; lifetime 627 over 60s, 169 over 120s (plus 2/1 during boot warm-up, not counted); recent 1/1 warn/kill breaches in 20/20 cycles; heartbeat age 6.96s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 426861 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 107s ago (3.96s to run, worst 213.72s), 1957 overrun(s) of 10704 cycles, TTL 900s; slowest tickers=19.54s, data_intake=14.29s, positions_diag=13.71s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=35, gate reads=0, withheld=35) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +75 / upstream +193 | 0 |
| structural_snap | ok | 6000/6000 measured, 29 blind, 0 levels moved (refusals: redetect_cooldown=1987) | 0 |
| structural_veto_lane | ok | 3569 stamped; 0 with no readable level book, 172 with clear air ahead, 2632 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +193 / upstream +17 | 0 |
| tuned_variants | violating | 365 non-stamps — atr_arm_uncomputable=365 (seen=14574 stamped=2114 skipped=12095) (streak 528/6) | 528 |
| unlock_shorts | ok | 14 open, 43 scheduled, calendar 13.8h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 59 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1442398`
- `Path funnel` emissions: `38`
- `Regime distribution` emissions: `38`
- `QUIET_SCALP_BLOCK` events: `319`
- `confidence_gate` events: `5999`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **103**
- Total REST-fallback activations: **6**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 8 | 5800 | 87385 | 134027 | 0 |
| futures_aggtrade | 21 | 5777 | 14160 | 60926 | 0 |
| futures_depth | 69 | 5147 | 59080 | 84119 | 0 |
| futures_liq | 5 | 5383 | 8674 | 12163 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 6 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=230201] state[populated=230201] buckets[many=230201] sources[none] quality[none]
- funding_rate: presence[absent=4943, present=225258] state[empty=4943, populated=225258] buckets[few=225258, none=4943] sources[none] quality[none]
- liquidation_clusters: presence[absent=148892, present=81309] state[empty=148892, populated=81309] buckets[few=69063, none=148892, some=12246] sources[none] quality[none]
- oi_snapshot: presence[absent=4943, present=225258] state[empty=4943, populated=225258] buckets[few=211, many=224015, none=4943, some=1032] sources[none] quality[none]
- order_book: presence[absent=72662, present=157539] state[populated=157539, unavailable=72662] buckets[few=157539, none=72662] sources[book_ticker=157539, unavailable=72662] quality[none=72662, top_of_book_only=157539]
- orderblocks: presence[absent=230201] state[empty=230201] buckets[none=230201] sources[measured_dark=230201] quality[none]
- recent_ticks: presence[present=230201] state[populated=230201] buckets[many=230201] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.486404538154602` sec
- Median create→first breach: `4459.873148918152` sec
- Median create→terminal: `4459.873203992844` sec
- Median first breach→terminal: `7.259845733642578e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.799999999999997 | 0.7999999999999965 | 0.9999999999999809 | 0 | 1 |
| MOVER_AVWAP_SCALP | 1 | 1 | 1.5858585570972337 | 1.9479991074092484 | 0.8140961415564274 | 0 | 1 |
| MOVER_TREND_PULLBACK | 17 | 17 | 4.0859060783593 | 3.0 | 1.6629905508385516 | 15 | 1 |
| QUIET_COMPRESSION_BREAK | 10 | 10 | 1.1320183561057697 | 1.3079800992062913 | 0.8854748672591001 | 0 | 8 |
| SR_FLIP_RETEST | 1 | 1 | 0.7050651911587243 | 0.6533678429392066 | 1.0791244147966554 | 1 | 0 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 33.3 | 33.3 | 33.3 | 0.0 | 0.3084 | 5308.075597047806 | 5308.075616836548 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.5859 | 8264.378890037537 | 8264.378920078278 |
| MOVER_TREND_PULLBACK | 17 | 17 | 41.2 | 29.4 | 41.2 | 0.0 | 0.8956 | 1845.9331541061401 | 1846.3828220367432 |
| QUIET_COMPRESSION_BREAK | 10 | 10 | 50.0 | 30.0 | 50.0 | 0.0 | 0.5562 | 27999.432351469994 | 27999.432389974594 |
| SR_FLIP_RETEST | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.7051 | 51391.700592041016 | 51391.70066714287 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 758 | 8 | 230 | 0.0 | 100.0 | 51391.700592041016 | 51391.70066714287 | 528 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1971 | 26 | 1707 | 0.0 | 0.0 | None | None | 264 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-12`
- Gating Δ: `133`
- No-generation Δ: `-177760`
- Fast failures Δ: `-1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.0571, "current_avg_pnl": 0.3084, "current_win_rate": 33.3, "previous_avg_pnl": 0.2513, "previous_win_rate": 33.3, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.0267, "current_avg_pnl": -1.5859, "current_win_rate": 0.0, "previous_avg_pnl": -0.5592, "previous_win_rate": 20.0, "win_rate_delta": -20.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.9621, "current_avg_pnl": 0.8956, "current_win_rate": 41.2, "previous_avg_pnl": -1.0665, "previous_win_rate": 25.9, "win_rate_delta": 15.3}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 1.4805, "current_avg_pnl": 0.5562, "current_win_rate": 50.0, "previous_avg_pnl": -0.9243, "previous_win_rate": 0.0, "win_rate_delta": 50.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 260, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 51391.7, "median_terminal_delta_sec": 51391.7, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -14, "geometry_changed_delta": 0, "geometry_preserved_delta": -128, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -1025.56, "median_terminal_delta_sec": -1025.56, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **DIVERGENCE_CONTINUATION**
- Most promising healthy path: **QUIET_COMPRESSION_BREAK**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **DIVERGENCE_CONTINUATION**
