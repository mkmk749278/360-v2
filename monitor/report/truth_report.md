# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `12671` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 75 | 75 | 75 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 9996 | 9996 | 9829 | 7 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 59598 | 59619 | 18 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 61102 | 61104 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 60466 | 57790 | 3295 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 61135 | 60156 | 1105 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 63018 | 62924 | 130 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 50593 | 50611 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 61263 | 61297 | 10 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 61313 | 60206 | 1827 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 64718 | 72190 | 785 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 59641 | 54234 | 10421 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 62650 | 62652 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 61112 | 61130 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 60440 | 60397 | 67 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 62039 | 60636 | 1934 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 60045 | 60268 | 130 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 47814 | 44843 | 3380 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 48231 | 47855 | 486 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 59559 | 59565 | 31 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 50616 | 50648 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3598 | 3598 | 3550 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 545 | 545 | 489 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 16020 | 16020 | 15924 | 7 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 19 | 19 | 12 | 6 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 4137 | 4137 | 3532 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1832 | 1832 | 1523 | 8 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 27144 | 27144 | 24012 | 96 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 9 | 9 | 9 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 592 | 592 | 560 | 15 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4082 | 4082 | 3966 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 561 | 561 | 460 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2167 | 2167 | 2136 | 5 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 164 | 164 | 148 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=59619): breakout_not_found=36814, basic_filters_failed=12063, move_not_fresh=5614, breakout_stale=2818, volume_spike_missing=1710, retest_proximity_failed=599, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=61104): cls_disabled_merged_into_lsr=61104
- **EVAL::DIVERGENCE_CONTINUATION** (total=57790): cvd_divergence_failed=29220, h1_trend_not_aligned=13636, basic_filters_failed=9201, ema_alignment_reject=4711, retest_proximity_failed=743, missing_fvg_or_orderblock=279
- **EVAL::FAILED_AUCTION_RECLAIM** (total=60156): auction_not_detected=42578, basic_filters_failed=8838, reclaim_hold_failed=4117, tail_too_small=2539, regime_blocked=2070, rsi_reject=14
- **EVAL::FUNDING_EXTREME** (total=62924): funding_not_extreme=47514, basic_filters_failed=8969, missing_funding_rate=3597, ema_alignment_reject=1745, rsi_reject=818, cvd_divergence_failed=155, momentum_reject=92, missing_fvg_or_orderblock=34
- **EVAL::LIQUIDATION_REVERSAL** (total=50611): cascade_threshold_not_met=40289, basic_filters_failed=9816, cvd_divergence_failed=259, rsi_reject=222, missing_fvg_or_orderblock=13, volume_spike_missing=7, missing_cvd=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=61297): no_ma_cross=50837, basic_filters_failed=9215, ma_cross_cooldown=739, ma_cross_htf_misaligned=506
- **EVAL::MEAN_REVERT** (total=60206): no_extension=52293, basic_filters_failed=7913
- **EVAL::MOVER_AVWAP_SCALP** (total=72190): no_avwap_tag=28002, no_mover_leg=18225, basic_filters_failed=12230, avwap_slope_against=9762, avwap_reclaim_no_volume=2351, no_avwap_reclaim=1612, anchor_too_recent=8
- **EVAL::MOVER_TREND_PULLBACK** (total=54234): mover_run_too_small=28408, no_reclaim=12196, basic_filters_failed=12147, no_pullback_tag=1483
- **EVAL::OPENING_RANGE_BREAKOUT** (total=62652): feature_disabled=62652
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=61130): regime_blocked=38784, breakout_not_found=16725, adx_reject=3078, basic_filters_failed=2467, ema_alignment_reject=76
- **EVAL::QUIET_COMPRESSION_BREAK** (total=60397): compression_not_detected=24704, regime_blocked=24186, basic_filters_failed=6358, breakout_not_detected=3537, macd_reject=1340, volume_confirmation_failed=262, missing_fvg_or_orderblock=8, rsi_reject=2
- **EVAL::RANGE_FADE** (total=60636): no_range_edge=52719, basic_filters_failed=7917
- **EVAL::SR_FLIP_RETEST** (total=60268): flip_close_not_confirmed=43674, basic_filters_failed=8810, long_break_volume_thin=2453, regime_blocked=2051, retest_out_of_zone=1650, h1_break_not_confirmed=1032, reclaim_hold_failed=343, long_acceptance_not_held=119, ema_alignment_reject=52, whipsaw_flip=47, wick_quality_failed=29, missing_fvg_or_orderblock=8
- **EVAL::STANDARD** (total=44843): adx_reject=12444, momentum_reject=12404, sweeps_not_detected=6122, basic_filters_failed=5644, ema_alignment_reject=3750, macd_reject=3453, htf_poi_unanchored=955, invalid_sl_geometry=43, rsi_reject=17, mtf_reject=11
- **EVAL::TREND_PULLBACK** (total=47855): h1_trend_not_aligned=13093, ema_alignment_reject=8326, h1_pullback_not_confirmed=7608, basic_filters_failed=4926, ema_not_tested_prev=4139, no_ema_reclaim_close=3907, body_conviction_fail=2152, rsi_reject=1906, prev_already_above_emas=669, no_prev_high_break=387, prev_already_below_emas=306, no_prev_low_break=190, momentum_flat=163, missing_fvg_or_orderblock=39, momentum_reject=23, ema21_not_tagged=21
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=59565): breakout_not_found=34823, basic_filters_failed=12059, move_not_fresh=6519, breakout_stale=3458, volume_spike_missing=1711, retest_proximity_failed=950, move_exhausted=26, missing_fvg_or_orderblock=19
- **EVAL::WHALE_MOMENTUM** (total=50648): momentum_reject=32742, recent_ticks_insufficient=13447, basic_filters_failed=4459

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=400): setup_compat:regime_VOLATILE_UNSUITABLE=339, setup_compat:regime_BREAKOUT_EXPANSION=49, execution:overextended=12
- **FAILED_AUCTION_RECLAIM** (total=1489): execution:overextended=767, setup_compat:regime_STRONG_TREND=701, context_floor=21
- **FUNDING_EXTREME_SIGNAL** (total=463): execution:trigger_not_confirmed=463
- **LIQUIDATION_REVERSAL** (total=2): execution:trigger_not_confirmed=2
- **LIQUIDITY_SWEEP_REVERSAL** (total=3477): execution:trigger_not_confirmed=1357, setup_compat:regime_STRONG_TREND=1217, execution:overextended=903
- **MA_CROSS_TREND_SHIFT** (total=16): setup_compat:regime_DIRTY_RANGE=8, execution:trigger_not_confirmed=4, setup_compat:regime_CLEAN_RANGE=3, execution:overextended=1
- **MEAN_REVERT** (total=3158): setup_compat:regime_WEAK_TREND=1409, setup_compat:regime_STRONG_TREND=1356, execution:overextended=393
- **MOVER_AVWAP_SCALP** (total=1029): execution:overextended=806, execution:trigger_not_confirmed=200, entry_quality=23
- **MOVER_TREND_PULLBACK** (total=9921): execution:trigger_not_confirmed=5241, execution:overextended=4189, entry_quality=491
- **QUIET_COMPRESSION_BREAK** (total=1): execution:trigger_not_confirmed=1
- **RANGE_FADE** (total=3114): setup_compat:regime_WEAK_TREND=1269, setup_compat:regime_STRONG_TREND=1166, execution:overextended=448, setup_compat:regime_VOLATILE_UNSUITABLE=208, context_edge=12, setup_compat:regime_BREAKOUT_EXPANSION=11
- **TREND_PULLBACK_EMA** (total=1759): setup_compat:regime_CLEAN_RANGE=1195, setup_compat:regime_DIRTY_RANGE=502, setup_compat:regime_VOLATILE_UNSUITABLE=62
- **VOLUME_SURGE_BREAKOUT** (total=40): execution:overextended=40

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 112527 | 37.0% |
| QUIET | 77007 | 25.3% |
| TRENDING_UP | 54431 | 17.9% |
| TRENDING_DOWN | 47409 | 15.6% |
| VOLATILE | 13151 | 4.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **71**
- Average confidence gap to threshold: **12.50** (samples=71) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SOLUSDT=15, BTCUSDT=15, STRKUSDT=9, ETHUSDT=9, ERAUSDT=6, FILUSDT=4, TIAUSDT=4, PENGUUSDT=3, ONDOUSDT=1, AVAXUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 32 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 11 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 4 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 1 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 4 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 40 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 5 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 9 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 6 |
| MEAN_REVERT | filtered | min_confidence | 19 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 19 |
| MEAN_REVERT | kept | min_confidence_pass | 7 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 138 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 181 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 480 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 17 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 944 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 19 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 16 |
| SR_FLIP_RETEST | filtered | min_confidence | 15 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 5 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 4 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 12 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 12 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 32 | 50.12 | 61.75 | 11.63 | 20.21 | 19.22 | 17.38 | 0.31 | 16.31 |
| DIVERGENCE_CONTINUATION | kept | 11 | 65.76 | 65.00 | -0.76 | 20.59 | 19.73 | 17.84 | 2.00 | 1.41 |
| FAILED_AUCTION_RECLAIM | filtered | 5 | 48.38 | 63.40 | 15.02 | 20.16 | 16.52 | 20.00 | 1.00 | 11.12 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 71.60 | 65.00 | -6.60 | 20.20 | 16.75 | 20.00 | 3.00 | 3.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 4 | 53.30 | 65.00 | 11.70 | 19.70 | 13.55 | 17.75 | 3.50 | 12.75 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 71.00 | 65.00 | -6.00 | 20.60 | 14.00 | 17.00 | 3.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 45 | 54.18 | 63.76 | 9.58 | 19.58 | 19.72 | 17.58 | 1.20 | 13.50 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 67.98 | 65.00 | -2.98 | 21.31 | 19.48 | 18.24 | 2.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 6 | 73.33 | 65.00 | -8.33 | 20.68 | 18.92 | 15.80 | 0.00 | 0.78 |
| MEAN_REVERT | filtered | 38 | 55.25 | 62.50 | 7.25 | 21.71 | 16.81 | 14.53 | 0.00 | 13.13 |
| MEAN_REVERT | kept | 7 | 77.41 | 65.00 | -12.41 | 21.23 | 17.71 | 14.56 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 139 | 53.84 | 64.50 | 10.66 | 19.89 | 14.36 | 15.80 | 3.92 | 15.02 |
| MOVER_AVWAP_SCALP | kept | 181 | 77.55 | 65.00 | -12.55 | 20.81 | 15.59 | 15.80 | 4.28 | 4.22 |
| MOVER_TREND_PULLBACK | filtered | 497 | 55.60 | 64.33 | 8.73 | 21.56 | 18.02 | 15.80 | 4.19 | 17.95 |
| MOVER_TREND_PULLBACK | kept | 944 | 75.64 | 65.00 | -10.64 | 19.73 | 18.31 | 15.80 | 4.16 | 2.01 |
| QUIET_COMPRESSION_BREAK | filtered | 19 | 57.14 | 65.00 | 7.86 | 21.95 | 19.72 | 20.00 | 0.00 | 10.01 |
| QUIET_COMPRESSION_BREAK | kept | 16 | 74.53 | 65.00 | -9.53 | 21.06 | 19.44 | 20.00 | 0.00 | 0.88 |
| SR_FLIP_RETEST | filtered | 20 | 60.25 | 65.00 | 4.75 | 22.98 | 20.00 | 15.20 | 2.20 | 8.40 |
| SR_FLIP_RETEST | kept | 2 | 67.95 | 65.00 | -2.95 | 20.95 | 20.00 | 18.60 | 2.50 | 9.55 |
| TREND_PULLBACK_EMA | filtered | 4 | 46.40 | 65.00 | 18.60 | 20.60 | 19.60 | 15.30 | 4.50 | 37.60 |
| TREND_PULLBACK_EMA | kept | 12 | 75.88 | 65.00 | -10.88 | 21.29 | 19.75 | 16.10 | 4.88 | -0.67 |
| VOLUME_SURGE_BREAKOUT | filtered | 12 | 60.50 | 61.00 | 0.50 | 19.43 | 16.20 | 20.00 | 4.50 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 32 | 50.12 | 22.50 | 11.44 | 4.22 | 14.38 | 5.47 | 8.12 | 0.31 |
| DIVERGENCE_CONTINUATION | kept | 11 | 65.76 | 23.55 | 11.64 | 4.91 | 12.82 | 5.27 | 8.63 | 2.00 |
| FAILED_AUCTION_RECLAIM | filtered | 5 | 48.38 | 17.00 | 15.60 | 14.40 | 14.00 | 7.80 | 4.70 | 1.00 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 71.60 | 21.00 | 16.00 | 9.00 | 11.50 | 6.75 | 7.35 | 3.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 4 | 53.30 | 25.00 | 15.50 | 4.50 | 10.50 | 5.88 | 4.92 | 3.50 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 71.00 | 17.00 | 18.00 | 6.00 | 12.00 | 9.00 | 6.00 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 45 | 54.18 | 22.33 | 17.38 | 5.20 | 12.20 | 5.82 | 7.88 | 1.20 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 67.98 | 22.11 | 14.44 | 4.00 | 12.33 | 5.22 | 7.87 | 2.00 |
| MA_CROSS_TREND_SHIFT | kept | 6 | 73.33 | 22.33 | 14.00 | 6.50 | 15.00 | 7.83 | 8.43 | 0.00 |
| MEAN_REVERT | filtered | 38 | 55.25 | 18.68 | 16.00 | 9.00 | 13.00 | 5.00 | 6.70 | 0.00 |
| MEAN_REVERT | kept | 7 | 77.41 | 22.71 | 17.43 | 11.57 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 139 | 53.84 | 17.37 | 18.17 | 13.06 | 12.45 | 5.32 | 3.96 | 3.92 |
| MOVER_AVWAP_SCALP | kept | 181 | 77.55 | 18.77 | 18.04 | 12.34 | 14.06 | 8.10 | 6.87 | 4.28 |
| MOVER_TREND_PULLBACK | filtered | 497 | 55.60 | 18.31 | 18.00 | 7.61 | 12.48 | 5.81 | 8.48 | 4.19 |
| MOVER_TREND_PULLBACK | kept | 944 | 75.64 | 19.40 | 18.01 | 7.77 | 13.00 | 6.77 | 8.59 | 4.16 |
| QUIET_COMPRESSION_BREAK | filtered | 19 | 57.14 | 18.68 | 18.00 | 10.58 | 14.16 | 6.47 | 4.04 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 16 | 74.53 | 18.50 | 18.00 | 11.81 | 14.06 | 7.09 | 7.36 | 0.00 |
| SR_FLIP_RETEST | filtered | 20 | 60.25 | 23.40 | 15.50 | 4.05 | 15.35 | 6.00 | 2.15 | 2.20 |
| SR_FLIP_RETEST | kept | 2 | 67.95 | 25.00 | 18.00 | 9.00 | 14.00 | 5.00 | 4.00 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 4 | 46.40 | 17.00 | 18.00 | 12.00 | 14.00 | 8.50 | 10.00 | 4.50 |
| TREND_PULLBACK_EMA | kept | 12 | 75.88 | 17.00 | 18.00 | 7.62 | 14.25 | 5.71 | 9.75 | 4.88 |
| VOLUME_SURGE_BREAKOUT | filtered | 12 | 60.50 | 17.00 | 18.00 | 12.00 | 11.00 | 5.00 | 8.00 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 32 | 50.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 11 | 65.76 | 0.00 | 0.00 | 0.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.73** |
| FAILED_AUCTION_RECLAIM | filtered | 5 | 48.38 | 0.00 | 0.00 | 5.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.12** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 71.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 4 | 53.30 | 0.00 | 0.00 | 9.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **9.00** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 71.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 45 | 54.18 | 0.00 | 0.00 | 0.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.32** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 67.98 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 6 | 73.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 38 | 55.25 | 0.00 | 0.00 | 0.00 | 0.00 | 8.72 | 0.00 | 0.00 | 0.00 | **8.72** |
| MEAN_REVERT | kept | 7 | 77.41 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 139 | 53.84 | 0.00 | 0.00 | 0.00 | 0.00 | 4.82 | 0.57 | 0.00 | 3.83 | **9.22** |
| MOVER_AVWAP_SCALP | kept | 181 | 77.55 | 0.00 | 0.00 | 0.09 | 0.00 | 0.32 | 0.44 | 0.00 | 0.19 | **1.04** |
| MOVER_TREND_PULLBACK | filtered | 497 | 55.60 | 0.00 | 0.00 | 0.55 | 0.00 | 0.86 | 0.06 | 0.00 | 0.00 | **1.47** |
| MOVER_TREND_PULLBACK | kept | 944 | 75.64 | 0.00 | 0.00 | 1.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.05** |
| QUIET_COMPRESSION_BREAK | filtered | 19 | 57.14 | 0.00 | 0.00 | 0.00 | 0.00 | 2.26 | 0.00 | 0.00 | 0.57 | **2.83** |
| QUIET_COMPRESSION_BREAK | kept | 16 | 74.53 | 0.00 | 0.00 | 0.00 | 0.00 | 1.07 | 0.00 | 0.00 | 0.00 | **1.07** |
| SR_FLIP_RETEST | filtered | 20 | 60.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 2 | 67.95 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | 0.00 | 0.00 | 0.00 | **6.00** |
| TREND_PULLBACK_EMA | filtered | 4 | 46.40 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| TREND_PULLBACK_EMA | kept | 12 | 75.88 | 0.00 | 0.00 | 1.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.33** |
| VOLUME_SURGE_BREAKOUT | filtered | 12 | 60.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **152124 held of 562563 seen** across 21 strategies; 3461 cells past the sample floor; **1768 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 44767 | 676/44091/0 | 44% | -0.18 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.28R) |
| MOVER_AVWAP_SCALP | 19662 | 192/19470/0 | 42% | -0.21 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 11617 | 125/11492/0 | 37% | -0.27 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (+1.77R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 10848 | 107/10741/0 | 48% | -0.07 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| TREND_PULLBACK_EMA | 9099 | 41/9058/0 | 41% | -0.20 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/ACCUMULATION/NORMAL/BTC_FALLING (-1.30R) |
| LIQUIDITY_SWEEP_REVERSAL | 8184 | 84/8100/0 | 35% | -0.49 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 7312 | 0/0/7312 | 42% | -0.11 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.48R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.03R) |
| SHADOW_RANGE_FADE | 6726 | 0/0/6726 | 36% | -0.14 | LONDON/QUIET/COMPRESSED/BTC_FALLING (+0.53R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.20R) |
| QUIET_COMPRESSION_BREAK | 6284 | 412/5872/0 | 49% | -0.11 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5824 | 0/0/5824 | 35% | -0.40 | NY/RANGE/EXPANDED/BTC_FALLING (-0.01R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| MEAN_REVERT | 4163 | 46/4117/0 | 39% | -0.30 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/MARKDOWN/CASCADE/BTC_NEUTRAL (-1.32R) |
| SR_FLIP_RETEST | 3798 | 15/3783/0 | 45% | -0.29 | NY/RANGE/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.18R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 3126 | 0/3126/0 | 31% | -0.34 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 3026 | 2/3024/0 | 31% | -0.49 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| RANGE_FADE | 1464 | 4/1460/0 | 36% | -0.37 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1352 | 0/0/1352 | 54% | -0.04 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.32R) | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.40R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 362 | 0/362/0 | 31% | -0.58 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 132 | 28/104/0 | 42% | -0.17 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 18 | 2/16/0 | 56% | +0.19 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 227 | 27% / -0.58R | 227 | 52% / -0.15R | +0.43 | **ATR** |
| LIQUIDATION_REVERSAL | 20 | 30% / -0.54R | 20 | 55% / -0.24R | +0.30 | **ATR** |
| TREND_PULLBACK_EMA | 771 | 40% / -0.30R | 771 | 53% / -0.06R | +0.24 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1293 | 44% / -0.34R | 1293 | 56% / -0.13R | +0.21 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 155 | 34% / -0.24R | 155 | 45% / -0.07R | +0.16 | **ATR** |
| RANGE_FADE | 73 | 30% / -0.42R | 73 | 37% / -0.28R | +0.14 | **ATR** |
| MA_CROSS_TREND_SHIFT | 42 | 38% / -0.22R | 42 | 40% / -0.10R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 1893 | 43% / -0.19R | 1893 | 49% / -0.07R | +0.12 | **ATR** |
| SR_FLIP_RETEST | 334 | 44% / -0.28R | 334 | 48% / -0.17R | +0.11 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1115 | 40% / -0.24R | 1115 | 43% / -0.13R | +0.11 | **ATR** |
| MOVER_TREND_PULLBACK | 7581 | 49% / -0.12R | 7581 | 54% / -0.01R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1183 | 49% / -0.09R | 1183 | 54% / -0.04R | +0.05 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1054 | 47% / -0.14R | 1054 | 47% / -0.15R | -0.00 | **FIXED** |
| MEAN_REVERT | 294 | 48% / -0.15R | 294 | 47% / -0.15R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 8 | 50% / -0.24R | 8 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 10463 | 28% | -0.24R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1893 | 46% | -0.07R | 219 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 97 | 46% | -0.08R | 60 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1406 | 40% / -0.14R | +0.87 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1036 | 35% / -0.22R | +0.84 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2350 | 34% / -0.16R | +0.68 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 9481 | 37% / -0.12R | +0.41 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1350 | 37% / -0.09R | +0.19 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1031 | 33% / -0.18R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 928 | 33% / -0.20R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 228 | 31% / -0.40R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 295 | 32% / -0.49R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 244 | 50% / -0.02R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 55 | 35% / -0.14R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 315 | 34% / -0.34R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 63 | 27% / -0.39R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 26 | 42% / -0.15R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 16 | 44% / +0.50R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **5** · boot grace active: False
- **ALERT** `sar_exit_shadow` — upstream +154 but output +0 (streak 8/6) (sustained 8 cycles)
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×520]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 118/6) (sustained 118 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 6/6) (sustained 6 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.58R (bound 0.3) (streak 118/6) (sustained 118 cycles)
- **ALERT** `auto_dispatch` — 10 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=11) (streak 49/3) (sustained 49 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 10614961 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 14 arms current, none stalled; covering 1756/1756 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 27 arms current, none stalled; covering 1028/1028 signals (100%) | 0 |
| auto_dispatch | violating | 10 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=11) (streak 49/3) | 49 |
| binance_ip_weight | ok | peak 185/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 82887.20 | 0 |
| candle_coverage | ok | 83/83 symbols with ≥20 15m candles, 83/83 updated within 45m [fresh=83; 75 Tier-1 futures + 8 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 415 dup bars, 0 undedupable; ws 0 out-of-order, 104 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 57 cohorts, 35 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +1 / upstream +26 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1125/1143 signals (98%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | 83 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1129/1147 signals (98%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 3745940 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.58R (bound 0.3) (streak 118/6) | 118 |
| emission_controller | ok | last cycle 0s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×520]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 118/6) | 118 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 6/6) | 6 |
| firestore_read_budget | ok | 1,306 reads/day of 50,000 [engine 1,273, signing 33]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +1 / upstream +154 | 0 |
| indicator_cache_key | ok | 34334 frozen value(s) avoided; 184507 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.31R over n=4117 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +25 / upstream +154 | 0 |
| mover_admission_metadata | ok | 931 symbols known, 225 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 8 held, 8 with scan counts, 8 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 7 locked / 7 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3102 rows held, 2994516 evicted (sampled: execution:trigger_not_confirmed 400/1059858, execution:overextended 400/941055, setup_compat:regime_STRONG_TREND 400/506309) | 0 |
| price_action_lane | ok | 207801 evaluated, 320 emitted; layer1 320 stamped / 0 blind; cooldown=26187, delta_opposed=20770, no_footprint=75664, no_opposing_target=12, no_sweep=66737, rr_below_floor=18111 | 0 |
| promoted_pair_integrity | ok | 8/8 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.37R over n=1460 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +112 / upstream +154 | 0 |
| sar_alignment_crosscheck | ok | 94/2320 disagreed (4.1%) | 0 |
| sar_exit_shadow | violating | upstream +154 but output +0 (streak 8/6) | 8 |
| sar_hold_arm | ok | 1891 held arms settled, 109 unscored, 27 still walking (26 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 11/11 resolvable | 0 |
| sar_live_arms | ok | 27 arms current, none stalled; covering 1028/1028 signals (100%) | 0 |
| sar_refresh_budget | ok | 4 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 1 resolved, 10 still mid-window | 0 |
| scan_cycle | ok | last 19.34s, worst 186.81s over 2532 lifetime cycles; lifetime 107 over 60s, 18 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.81s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 96415 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 8m ago | 0 |
| snapshot_writer | ok | last cycle 0s ago (1.53s to run, worst 159.69s), 447 overrun(s) of 2556 cycles, TTL 900s; slowest signals=0.82s, data_intake=0.21s, tickers=0.1s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +3 / upstream +154 | 0 |
| structural_snap | ok | 6000/6000 measured, 26 blind, 0 levels moved (refusals: redetect_cooldown=35) | 0 |
| structural_veto_lane | ok | 105 stamped; 0 with no readable level book, 1 with clear air ahead, 90 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +154 / upstream +26 | 0 |
| tuned_variants | ok | seen=711 stamped=89 skipped=622, residue 0 (none recorded) | 0 |
| unlock_shorts | ok | 16 open, 43 scheduled, calendar 1.4h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 14 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1469337`
- `Path funnel` emissions: `38`
- `Regime distribution` emissions: `38`
- `QUIET_SCALP_BLOCK` events: `71`
- `confidence_gate` events: `2006`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **96**
- Total REST-fallback activations: **11**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 16 | 36057 | 61665 | 73041 | 0 |
| futures_aggtrade | 37 | 15415 | 33815 | 61532 | 0 |
| futures_depth | 15 | 16988 | 19594 | 19627 | 0 |
| futures_liq | 4 | 4938 | 10093 | 19534 | 0 |
| futures_mover | 24 | 15853 | 25072 | 44055 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 11 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[absent=93, present=257843] state[empty=93, populated=257843] buckets[few=16, many=257554, none=93, some=273] sources[none] quality[none]
- funding_rate: presence[absent=28735, present=229201] state[empty=28735, populated=229201] buckets[few=229201, none=28735] sources[none] quality[none]
- liquidation_clusters: presence[absent=147013, present=110923] state[empty=147013, populated=110923] buckets[few=92070, none=147013, some=18853] sources[none] quality[none]
- oi_snapshot: presence[absent=26461, present=231475] state[empty=26461, populated=231475] buckets[few=239, many=230140, none=26461, some=1096] sources[none] quality[none]
- order_book: presence[absent=84109, present=173827] state[populated=173827, unavailable=84109] buckets[few=173827, none=84109] sources[book_ticker=173827, unavailable=84109] quality[none=84109, top_of_book_only=173827]
- orderblocks: presence[absent=257936] state[empty=257936] buckets[none=257936] sources[measured_dark=257936] quality[none]
- recent_ticks: presence[present=257936] state[populated=257936] buckets[many=257936] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.556128025054932` sec
- Median create→first breach: `10124.671835064888` sec
- Median create→terminal: `10124.67429459095` sec
- Median first breach→terminal: `6.401538848876953e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 1.0907205932964172 | 1.2270431097221601 | 0.8889016079829416 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.9352555787671069 | 0.9885456417740652 | 0.9490212193393157 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 1.0065671641791127 | 1.1246273106738198 | 0.895022870799775 | 0 | 1 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.8236292540157996 | 1.2163143833276504 | 0.6771516191089311 | 0 | 1 |
| MOVER_AVWAP_SCALP | 2 | 2 | 2.303615542056596 | 2.6749220097507838 | 0.8577516662386648 | 0 | 2 |
| MOVER_TREND_PULLBACK | 11 | 11 | 3.9139081889198177 | 3.0 | 1.3377366195589442 | 8 | 3 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 0.9671481547225727 | 1.043590769641194 | 0.8952353766555212 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.6361 | 22552.524724006653 | 22553.501100063324 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.4299 | 18077.079519987106 | 18077.51234650612 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.51 | 20966.261226177216 | 20967.451007127762 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.8236 | 7115.841073989868 | 7115.841099023819 |
| MOVER_AVWAP_SCALP | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.7604 | 21096.45906150341 | 21096.84780740738 |
| MOVER_TREND_PULLBACK | 11 | 11 | 18.2 | 54.5 | 18.2 | 0.0 | -0.9441 | 4160.690533876419 | 4164.076580047607 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 25.0 | 50.0 | 25.0 | 0.0 | -0.2144 | 26724.736234545708 | 26724.736253499985 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 561 | 1 | 460 | 0.0 | 0.0 | None | None | 101 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2167 | 5 | 2136 | 0.0 | 0.0 | None | None | 31 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-47`
- Gating Δ: `-54958`
- No-generation Δ: `-858078`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": 1.4767, "current_avg_pnl": 0.7604, "current_win_rate": 50.0, "previous_avg_pnl": -0.7163, "previous_win_rate": 14.3, "win_rate_delta": 35.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.1415, "current_avg_pnl": -0.9441, "current_win_rate": 18.2, "previous_avg_pnl": -1.0856, "previous_win_rate": 20.0, "win_rate_delta": -1.8}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.2463, "current_avg_pnl": -0.2144, "current_win_rate": 25.0, "previous_avg_pnl": -0.4607, "previous_win_rate": 0.0, "win_rate_delta": 25.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -6, "geometry_changed_delta": 0, "geometry_preserved_delta": -314, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -8, "geometry_changed_delta": 0, "geometry_preserved_delta": -160, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
