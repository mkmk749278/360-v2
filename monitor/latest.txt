# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `1813` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 160 | 160 | 152 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10999 | 10999 | 10448 | 7 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 109547 | 109553 | 34 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 90901 | 90902 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 90448 | 88155 | 2728 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 90957 | 90493 | 549 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 93509 | 93438 | 100 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 81334 | 81355 | 5 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 91052 | 91089 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 91092 | 88173 | 4177 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 115699 | 121800 | 1254 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 109593 | 98641 | 16978 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 92964 | 92965 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 90907 | 90944 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 90402 | 90156 | 280 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 92365 | 91388 | 1458 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 89818 | 90213 | 135 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 78445 | 74232 | 4545 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 78780 | 78225 | 671 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 109486 | 109481 | 64 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 81365 | 81389 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3306 | 3306 | 3211 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 429 | 429 | 392 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 26 | 26 | 26 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 23439 | 23439 | 23133 | 11 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 3 | 3 | 2 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 13173 | 13173 | 12052 | 3 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 4028 | 4028 | 3541 | 37 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 49902 | 49902 | 42906 | 209 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 36 | 36 | 36 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1685 | 1685 | 1575 | 6 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4222 | 4222 | 3785 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 490 | 490 | 396 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3273 | 3273 | 3167 | 2 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 304 | 304 | 288 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=109553): breakout_not_found=59332, basic_filters_failed=32309, move_not_fresh=11495, breakout_stale=4033, retest_proximity_failed=2060, volume_spike_missing=313, insufficient_candles=11
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=90902): cls_disabled_merged_into_lsr=90902
- **EVAL::DIVERGENCE_CONTINUATION** (total=88155): cvd_divergence_failed=41511, basic_filters_failed=21146, h1_trend_not_aligned=20471, ema_alignment_reject=4075, retest_proximity_failed=751, missing_fvg_or_orderblock=191, cvd_insufficient=10
- **EVAL::FAILED_AUCTION_RECLAIM** (total=90493): auction_not_detected=59899, basic_filters_failed=20774, reclaim_hold_failed=3437, tail_too_small=3427, regime_blocked=2931, rsi_reject=25
- **EVAL::FUNDING_EXTREME** (total=93438): funding_not_extreme=67345, basic_filters_failed=21380, missing_funding_rate=2102, ema_alignment_reject=1649, rsi_reject=643, momentum_reject=157, cvd_divergence_failed=144, missing_fvg_or_orderblock=18
- **EVAL::LIQUIDATION_REVERSAL** (total=81355): cascade_threshold_not_met=58861, basic_filters_failed=21567, cvd_divergence_failed=488, rsi_reject=397, missing_fvg_or_orderblock=25, volume_spike_missing=17
- **EVAL::MA_CROSS_TREND_SHIFT** (total=91089): no_ma_cross=69288, basic_filters_failed=21174, ma_cross_htf_misaligned=505, ma_cross_cooldown=122
- **EVAL::MEAN_REVERT** (total=88173): no_extension=75400, basic_filters_failed=12773
- **EVAL::MOVER_AVWAP_SCALP** (total=121800): no_avwap_tag=42561, basic_filters_failed=32365, no_mover_leg=31207, avwap_slope_against=8769, avwap_reclaim_no_volume=3739, no_avwap_reclaim=2467, insufficient_candles=647, anchor_too_recent=45
- **EVAL::MOVER_TREND_PULLBACK** (total=98641): mover_run_too_small=42389, basic_filters_failed=32155, no_reclaim=19981, no_pullback_tag=3342, insufficient_candles=774
- **EVAL::OPENING_RANGE_BREAKOUT** (total=92965): feature_disabled=92965
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=90944): regime_blocked=52064, breakout_not_found=25593, basic_filters_failed=10539, adx_reject=2664, ema_alignment_reject=84
- **EVAL::QUIET_COMPRESSION_BREAK** (total=90156): regime_blocked=41605, compression_not_detected=32572, basic_filters_failed=10224, breakout_not_detected=5079, volume_confirmation_failed=568, rsi_reject=86, missing_fvg_or_orderblock=22
- **EVAL::RANGE_FADE** (total=91388): no_range_edge=78607, basic_filters_failed=12781
- **EVAL::SR_FLIP_RETEST** (total=90213): flip_close_not_confirmed=58744, basic_filters_failed=20732, regime_blocked=2923, retest_out_of_zone=2615, long_break_volume_thin=2402, h1_break_not_confirmed=1577, reclaim_hold_failed=830, ema_alignment_reject=196, long_acceptance_not_held=78, whipsaw_flip=72, wick_quality_failed=44
- **EVAL::STANDARD** (total=74232): momentum_reject=22739, adx_reject=16944, sweeps_not_detected=10342, basic_filters_failed=9800, ema_alignment_reject=6610, macd_reject=6482, htf_poi_unanchored=1130, invalid_sl_geometry=129, rsi_reject=56
- **EVAL::TREND_PULLBACK** (total=78225): h1_trend_not_aligned=24898, ema_alignment_reject=14840, basic_filters_failed=11241, h1_pullback_not_confirmed=7342, ema_not_tested_prev=6496, no_ema_reclaim_close=5618, body_conviction_fail=3094, rsi_reject=2460, prev_already_above_emas=809, no_prev_high_break=728, momentum_flat=218, prev_already_below_emas=208, no_prev_low_break=191, missing_fvg_or_orderblock=46, ema21_not_tagged=31, momentum_reject=5
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=109481): breakout_not_found=59969, basic_filters_failed=32306, move_not_fresh=10864, breakout_stale=4412, retest_proximity_failed=1390, volume_spike_missing=467, missing_fvg_or_orderblock=55, insufficient_candles=11, move_exhausted=7
- **EVAL::WHALE_MOMENTUM** (total=81389): momentum_reject=55400, recent_ticks_insufficient=22616, basic_filters_failed=3373

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=49): execution:overextended=49
- **DIVERGENCE_CONTINUATION** (total=267): setup_compat:regime_VOLATILE_UNSUITABLE=242, setup_compat:regime_BREAKOUT_EXPANSION=17, execution:overextended=8
- **FAILED_AUCTION_RECLAIM** (total=1187): setup_compat:regime_STRONG_TREND=697, execution:overextended=476, setup_compat:regime_VOLATILE_UNSUITABLE=9, context_floor=5
- **FUNDING_EXTREME_SIGNAL** (total=375): execution:trigger_not_confirmed=375
- **LIQUIDATION_REVERSAL** (total=26): execution:trigger_not_confirmed=26
- **LIQUIDITY_SWEEP_REVERSAL** (total=6840): setup_compat:regime_STRONG_TREND=2533, execution:trigger_not_confirmed=2473, execution:overextended=1834
- **MA_CROSS_TREND_SHIFT** (total=3): setup_compat:regime_DIRTY_RANGE=1, execution:trigger_not_confirmed=1, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=9558): setup_compat:regime_STRONG_TREND=4654, setup_compat:regime_WEAK_TREND=2664, execution:overextended=2210, entry_quality=30
- **MOVER_AVWAP_SCALP** (total=2370): execution:overextended=2011, execution:trigger_not_confirmed=234, entry_quality=125
- **MOVER_TREND_PULLBACK** (total=20936): execution:trigger_not_confirmed=11769, execution:overextended=8120, entry_quality=1047
- **QUIET_COMPRESSION_BREAK** (total=21): execution:trigger_not_confirmed=21
- **RANGE_FADE** (total=3128): setup_compat:regime_STRONG_TREND=1553, setup_compat:regime_WEAK_TREND=1213, setup_compat:regime_VOLATILE_UNSUITABLE=285, execution:overextended=77
- **TREND_PULLBACK_EMA** (total=2820): setup_compat:regime_CLEAN_RANGE=1663, setup_compat:regime_DIRTY_RANGE=1111, entry_quality=24, setup_compat:regime_VOLATILE_UNSUITABLE=22
- **VOLUME_SURGE_BREAKOUT** (total=61): execution:overextended=57, context_floor=4

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 235679 | 39.1% |
| TRENDING_DOWN | 137019 | 22.7% |
| TRENDING_UP | 108297 | 18.0% |
| QUIET | 94250 | 15.6% |
| VOLATILE | 27673 | 4.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **44**
- Average confidence gap to threshold: **16.00** (samples=44) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=18, FILUSDT=6, BCHUSDT=6, AVAXUSDT=6, ONDOUSDT=4, XRPUSDT=2, SUIUSDT=1, TUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 8 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 55 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 77 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 13 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 4 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 38 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 20 |
| MEAN_REVERT | filtered | min_confidence | 133 |
| MEAN_REVERT | kept | min_confidence_pass | 7 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 22 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 227 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 530 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1951 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 44 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 39 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 6 |
| SR_FLIP_RETEST | filtered | min_confidence | 49 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 47 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 29 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 11 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 8 | 56.00 | 61.00 | 5.00 | 20.48 | 18.00 | 20.00 | 4.00 | 11.00 |
| DIVERGENCE_CONTINUATION | filtered | 55 | 54.79 | 64.55 | 9.76 | 20.65 | 19.98 | 16.54 | 1.45 | 12.90 |
| DIVERGENCE_CONTINUATION | kept | 77 | 70.95 | 65.00 | -5.95 | 21.58 | 19.32 | 18.60 | 0.84 | -0.05 |
| FAILED_AUCTION_RECLAIM | filtered | 17 | 53.33 | 62.18 | 8.85 | 20.39 | 19.44 | 20.00 | 3.35 | 14.53 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 66.30 | 65.00 | -1.30 | 20.50 | 19.60 | 20.00 | 1.00 | 6.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 47.60 | 65.00 | 17.40 | 21.20 | 14.00 | 17.00 | 3.00 | 19.40 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 38 | 50.92 | 64.16 | 13.24 | 19.16 | 17.69 | 18.32 | 2.79 | 20.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 20 | 67.35 | 65.00 | -2.35 | 20.93 | 19.56 | 18.75 | 1.05 | 0.34 |
| MEAN_REVERT | filtered | 133 | 54.91 | 63.64 | 8.73 | 19.98 | 14.35 | 16.11 | 0.00 | 14.67 |
| MEAN_REVERT | kept | 7 | 74.84 | 65.00 | -9.84 | 21.67 | 16.60 | 15.13 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 22 | 60.25 | 65.00 | 4.75 | 20.59 | 17.49 | 15.80 | 4.82 | 15.35 |
| MOVER_AVWAP_SCALP | kept | 227 | 81.39 | 65.00 | -16.39 | 20.14 | 14.94 | 15.80 | 4.78 | 0.65 |
| MOVER_TREND_PULLBACK | filtered | 530 | 56.21 | 64.58 | 8.37 | 19.67 | 18.16 | 15.80 | 3.79 | 16.80 |
| MOVER_TREND_PULLBACK | kept | 1951 | 76.51 | 65.00 | -11.51 | 20.09 | 18.22 | 15.80 | 4.25 | 1.13 |
| QUIET_COMPRESSION_BREAK | filtered | 83 | 53.11 | 64.57 | 11.46 | 21.18 | 19.04 | 20.00 | 0.00 | 16.82 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 69.17 | 65.00 | -4.17 | 21.47 | 18.93 | 20.00 | 0.00 | 4.35 |
| SR_FLIP_RETEST | filtered | 49 | 57.44 | 63.53 | 6.09 | 20.91 | 20.00 | 15.46 | 1.73 | 14.51 |
| SR_FLIP_RETEST | kept | 2 | 63.50 | 65.00 | 1.50 | 20.35 | 20.00 | 15.20 | 2.50 | 15.00 |
| TREND_PULLBACK_EMA | filtered | 47 | 60.14 | 64.06 | 3.92 | 20.82 | 20.00 | 17.10 | 5.44 | 15.32 |
| TREND_PULLBACK_EMA | kept | 29 | 73.36 | 65.00 | -8.36 | 21.02 | 19.82 | 17.73 | 5.19 | 8.09 |
| VOLUME_SURGE_BREAKOUT | filtered | 11 | 57.20 | 61.00 | 3.80 | 20.80 | 15.84 | 20.00 | 3.50 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 65.50 | 65.00 | -0.50 | 17.50 | 17.00 | 20.00 | 5.00 | 7.80 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 8 | 56.00 | 2.00 | 14.00 | 15.00 | 17.00 | 5.00 | 10.00 | 4.00 |
| DIVERGENCE_CONTINUATION | filtered | 55 | 54.79 | 23.25 | 13.45 | 3.76 | 13.75 | 4.35 | 7.67 | 1.45 |
| DIVERGENCE_CONTINUATION | kept | 77 | 70.95 | 21.57 | 16.96 | 7.01 | 12.13 | 4.64 | 9.30 | 0.84 |
| FAILED_AUCTION_RECLAIM | filtered | 17 | 53.33 | 21.59 | 14.71 | 4.24 | 13.18 | 5.53 | 5.27 | 3.35 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 66.30 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 2.30 | 1.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 47.60 | 25.00 | 8.00 | 3.00 | 12.00 | 10.00 | 6.00 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 38 | 50.92 | 24.89 | 14.00 | 4.34 | 12.74 | 7.16 | 4.99 | 2.79 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 20 | 67.35 | 23.40 | 15.20 | 4.80 | 14.15 | 5.50 | 3.74 | 1.05 |
| MEAN_REVERT | filtered | 133 | 54.91 | 18.38 | 15.71 | 12.63 | 13.00 | 5.00 | 6.77 | 0.00 |
| MEAN_REVERT | kept | 7 | 74.84 | 20.43 | 14.57 | 14.14 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 22 | 60.25 | 17.00 | 18.00 | 10.36 | 11.45 | 5.00 | 8.95 | 4.82 |
| MOVER_AVWAP_SCALP | kept | 227 | 81.39 | 19.63 | 18.06 | 11.00 | 13.88 | 7.02 | 7.73 | 4.78 |
| MOVER_TREND_PULLBACK | filtered | 530 | 56.21 | 17.30 | 18.01 | 7.54 | 11.92 | 6.01 | 8.74 | 3.79 |
| MOVER_TREND_PULLBACK | kept | 1951 | 76.51 | 18.94 | 18.02 | 7.71 | 13.23 | 7.07 | 8.47 | 4.25 |
| QUIET_COMPRESSION_BREAK | filtered | 83 | 53.11 | 19.31 | 15.88 | 10.99 | 14.00 | 7.00 | 2.76 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 69.17 | 18.33 | 16.00 | 12.00 | 14.00 | 7.17 | 6.02 | 0.00 |
| SR_FLIP_RETEST | filtered | 49 | 57.44 | 20.92 | 18.00 | 5.51 | 15.35 | 5.00 | 5.44 | 1.73 |
| SR_FLIP_RETEST | kept | 2 | 63.50 | 25.00 | 18.00 | 6.00 | 14.00 | 5.00 | 8.00 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 47 | 60.14 | 20.74 | 18.00 | 7.50 | 14.00 | 5.00 | 8.29 | 5.44 |
| TREND_PULLBACK_EMA | kept | 29 | 73.36 | 20.59 | 18.00 | 7.50 | 15.45 | 6.98 | 8.36 | 5.19 |
| VOLUME_SURGE_BREAKOUT | filtered | 11 | 57.20 | 17.00 | 18.00 | 15.00 | 12.36 | 3.64 | 5.70 | 3.50 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 65.50 | 25.00 | 18.00 | 15.00 | 17.00 | 5.00 | 3.30 | 5.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 8 | 56.00 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| DIVERGENCE_CONTINUATION | filtered | 55 | 54.79 | 0.00 | 0.00 | 0.81 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.81** |
| DIVERGENCE_CONTINUATION | kept | 77 | 70.95 | 0.00 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.12** |
| FAILED_AUCTION_RECLAIM | filtered | 17 | 53.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 66.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 47.60 | 0.00 | 0.00 | 14.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **14.40** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 38 | 50.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 20 | 67.35 | 0.00 | 0.00 | 0.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.48** |
| MEAN_REVERT | filtered | 133 | 54.91 | 0.00 | 0.00 | 0.00 | 0.00 | 0.87 | 0.00 | 0.00 | 0.00 | **0.87** |
| MEAN_REVERT | kept | 7 | 74.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 22 | 60.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 227 | 81.39 | 0.00 | 0.00 | 0.23 | 0.00 | 0.03 | 0.00 | 0.00 | 0.29 | **0.55** |
| MOVER_TREND_PULLBACK | filtered | 530 | 56.21 | 0.00 | 0.00 | 1.03 | 0.00 | 0.14 | 0.00 | 0.00 | 0.20 | **1.37** |
| MOVER_TREND_PULLBACK | kept | 1951 | 76.51 | 0.00 | 0.00 | 0.59 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.61** |
| QUIET_COMPRESSION_BREAK | filtered | 83 | 53.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 8.26 | **8.26** |
| QUIET_COMPRESSION_BREAK | kept | 6 | 69.17 | 0.00 | 0.00 | 1.33 | 0.00 | 0.72 | 0.00 | 0.00 | 2.80 | **4.85** |
| SR_FLIP_RETEST | filtered | 49 | 57.44 | 0.00 | 0.00 | 0.00 | 0.00 | 6.61 | 0.00 | 0.00 | 2.69 | **9.30** |
| SR_FLIP_RETEST | kept | 2 | 63.50 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| TREND_PULLBACK_EMA | filtered | 47 | 60.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 29 | 73.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 11 | 57.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 65.50 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |

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
- Outcomes recorded: **77287 held of 180935 seen** across 21 strategies; 1724 cells past the sample floor; **741 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 30878 | 325/30553/0 | 46% | -0.12 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.17R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.14R) |
| MOVER_AVWAP_SCALP | 9480 | 74/9406/0 | 41% | -0.24 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 5989 | 41/5948/0 | 43% | -0.18 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 4263 | 24/4239/0 | 53% | +0.05 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 4094 | 0/0/4094 | 43% | -0.09 | ASIA/RANGE/NORMAL/BTC_RISING (+0.23R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.09R) |
| TREND_PULLBACK_EMA | 3742 | 12/3730/0 | 46% | -0.16 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+1.16R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.24R) |
| QUIET_COMPRESSION_BREAK | 3704 | 119/3585/0 | 47% | -0.11 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+0.84R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_RANGE_FADE | 3462 | 0/0/3462 | 36% | -0.10 | LONDON/RANGE/EXPANDED/BTC_NEUTRAL (+0.29R) | LONDON/RANGE/NORMAL/BTC_FALLING (-0.92R) |
| SHADOW_FUNDING_FADE | 2887 | 0/0/2887 | 37% | -0.36 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-1.01R) |
| WHALE_MOMENTUM | 2064 | 2/2062/0 | 40% | -0.38 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 1857 | 18/1839/0 | 38% | -0.27 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.21R) |
| MEAN_REVERT | 1333 | 18/1315/0 | 60% | +0.12 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 916 | 2/914/0 | 30% | -0.48 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.37R) |
| VOLUME_SURGE_BREAKOUT | 910 | 0/910/0 | 47% | -0.10 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| SR_FLIP_RETEST | 558 | 0/558/0 | 53% | -0.22 | ASIA/MARKDOWN/NORMAL/BTC_FALLING/ALTCOIN (+0.72R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 452 | 0/0/452 | 54% | -0.02 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.18R) |
| RANGE_FADE | 256 | 0/256/0 | 52% | -0.11 | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (+1.36R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| BREAKDOWN_SHORT | 208 | 16/192/0 | 20% | -0.60 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDATION_REVERSAL | 184 | 0/184/0 | 7% | -1.10 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 46 | 6/40/0 | 35% | -0.17 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 4 | 0/4/0 | 50% | +0.17 | — | — |

- **Strongest cells**: `DIVERGENCE_CONTINUATION @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +1.76R (n=34, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +1.66R (n=15, STRONG); `FAILED_AUCTION_RECLAIM @ OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN` +1.55R (n=22, STRONG)
- **Weakest cells**: `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING` -1.38R (n=17, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.37R (n=16, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 96 | 33% / -0.43R | 96 | 50% / -0.12R | +0.31 | **ATR** |
| TREND_PULLBACK_EMA | 321 | 50% / -0.13R | 321 | 57% / -0.02R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 247 | 43% / -0.34R | 247 | 45% / -0.24R | +0.10 | **ATR** |
| RANGE_FADE | 19 | 47% / +0.11R | 19 | 47% / +0.01R | -0.10 | **FIXED** |
| MOVER_AVWAP_SCALP | 731 | 46% / -0.17R | 731 | 51% / -0.08R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 80 | 48% / -0.29R | 80 | 49% / -0.20R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 479 | 44% / -0.17R | 479 | 47% / -0.08R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 4745 | 51% / -0.08R | 4745 | 55% / -0.00R | +0.08 | **ATR** |
| MA_CROSS_TREND_SHIFT | 15 | 33% / -0.24R | 15 | 33% / -0.19R | +0.06 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 62 | 45% / -0.09R | 62 | 52% / -0.04R | +0.06 | **ATR** |
| BREAKDOWN_SHORT | 20 | 30% / -0.17R | 20 | 30% / -0.14R | +0.03 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 370 | 51% / -0.20R | 370 | 54% / -0.17R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 615 | 45% / -0.16R | 615 | 45% / -0.17R | -0.01 | **FIXED** |
| MEAN_REVERT | 107 | 58% / +0.05R | 107 | 55% / +0.04R | -0.01 | **FIXED** |
| DIVERGENCE_CONTINUATION | 453 | 54% / -0.00R | 453 | 59% / -0.01R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 11 | 27% / -0.51R | 11 | 45% / -0.35R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 7042 | 31% | -0.12R | 283 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 731 | 49% | -0.07R | 162 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 42 | 55% | -0.06R | 34 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 86 | 36% / -0.24R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 579 | 37% / -0.08R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 6043 | 37% / -0.12R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 871 | 37% / -0.03R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 375 | 37% / -0.05R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 503 | 42% / +0.09R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 414 | 38% / -0.11R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 369 | 44% / -0.08R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 85 | 28% / -0.45R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 111 | 31% / -0.58R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 86 | 53% / +0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 39 | 41% / -0.05R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 17 | 41% / +0.18R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 81 | 31% / -0.39R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 21 | 14% / -0.68R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 15 | 33% / -0.18R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 8 | 38% / -0.01R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 55 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×537]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 203/6) (sustained 203 cycles)
- **ALERT** `mean_revert_emission` — 8627 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure +0.11R over n=1315, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 153/6) (sustained 153 cycles)
- **ALERT** `tuned_variants` — 120 non-stamps — atr_arm_uncomputable=120 (seen=1739 stamped=241 skipped=1378) (streak 93/6) (sustained 93 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 203/3) (sustained 203 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 41 fed / 0 quiet / 0 never delivered of 41 subscribed; 26539452 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 203/3) | 203 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 49 arms current, none stalled; covering 659/659 signals (100%) | 0 |
| auto_dispatch | ok | placed=26 rejected=2 skipped=28 over 28 fan-out(s) to a keyed roster; top reasons: mode=28, NotionalTooSmall=2 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 79686.00 | 0 |
| candle_coverage | ok | 86/86 symbols with ≥20 15m candles, 86/86 updated within 45m [fresh=86; 74 Tier-1 futures + 12 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 910 dup bars, 0 undedupable; ws 0 out-of-order, 157 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +7 / upstream +23 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1262/1279 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 4 of 134 open dark rows are not being advanced (worst: TUTUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 99/120) | 99 |
| dark_sar_arms | ok | no open arms; covering 1255/1272 signals (99%) | 0 |
| depth_feed | ok | 41/41 books fresh (stale 0, never 0, thin 0); 7640624 msgs, 0 rejected | 0 |
| edge_reconciliation | ok | max divergence FAILED_AUCTION_RECLAIM +0.21R (< 0.3) | 0 |
| emission_controller | ok | last cycle 1294s ago; live_overrides=12 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×537]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 203/6) | 203 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 3/6) | 3 |
| footprint_bars | ok | 4883 sealed bars over 41 symbols; 1101 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +3 / upstream +178 | 0 |
| indicator_cache_key | ok | 53622 frozen value(s) avoided; 148020 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 8627 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure +0.11R over n=1315, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 153/6) | 153 |
| mean_revert_path | ok | output +26 / upstream +178 | 0 |
| mover_admission_metadata | ok | 897 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 12 held, 12 with scan counts, 9 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2969 rows held, 1121172 evicted (sampled: execution:trigger_not_confirmed 400/405920, execution:overextended 400/385113, setup_compat:regime_STRONG_TREND 400/159684) | 0 |
| price_action_lane | ok | 487514 evaluated, 522 emitted; layer1 522 stamped / 0 blind; cooldown=65953, delta_opposed=35507, no_footprint=205751, no_opposing_target=424, no_sweep=147086, rr_below_floor=32271 | 0 |
| promoted_pair_integrity | ok | 12/12 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.11R over n=256 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +28 / upstream +178 | 0 |
| sar_alignment_crosscheck | ok | 281/7977 disagreed (3.5%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +178 | 0 |
| sar_hold_arm | ok | 1114 held arms settled, 178 unscored, 44 still walking (37 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 1/49 unfetchable (2%); top cause: located bar does not contain the stamp; symbols: EPICUSDT | 0 |
| sar_live_arms | ok | 45 arms current, none stalled; covering 668/668 signals (100%) | 0 |
| sar_refresh_budget | ok | 8 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 449 records await one (48 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 4/12) | 4 |
| scan_cycle | ok | last 40.89s, worst 80.93s over 5541 lifetime cycles; lifetime 6 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 1.31s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 166999 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 4m ago | 0 |
| snapshot_writer | ok | last cycle 1s ago (0.44s to run, worst 44.4s), 244 overrun(s) of 4341 cycles, TTL 900s; slowest signals=0.17s, data_intake=0.08s, tickers=0.07s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +20 / upstream +178 | 0 |
| structural_snap | ok | 4694/4694 measured, 11 blind, 0 levels moved (refusals: redetect_cooldown=179) | 0 |
| structural_veto_lane | ok | 416 stamped; 0 with no readable level book, 7 with clear air ahead, 295 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +178 / upstream +23 | 0 |
| tuned_variants | violating | 120 non-stamps — atr_arm_uncomputable=120 (seen=1739 stamped=241 skipped=1378) (streak 93/6) | 93 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2711101`
- `Path funnel` emissions: `68`
- `Regime distribution` emissions: `68`
- `QUIET_SCALP_BLOCK` events: `44`
- `confidence_gate` events: `3315`
- `free_channel_post` events: `43`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **6**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 1813 | 1813 | 1813 | 0 |
| futures_depth | 4 | 3252 | 5735 | 6882 | 0 |
| futures_mover | 1 | 4412 | 4412 | 4412 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **43**

| Source | Count |
|---|---:|
| signal_close | 35 |
| regime_shift | 8 |

- By severity: HIGH=43

## Dependency readiness
- cvd: presence[absent=4, present=503939] state[empty=4, populated=503939] buckets[few=16, many=503828, none=4, some=95] sources[none] quality[none]
- funding_rate: presence[absent=63414, present=440529] state[empty=63414, populated=440529] buckets[few=440529, none=63414] sources[none] quality[none]
- liquidation_clusters: presence[absent=266533, present=237410] state[empty=266533, populated=237410] buckets[few=188007, none=266533, some=49403] sources[none] quality[none]
- oi_snapshot: presence[absent=61956, present=441987] state[empty=61956, populated=441987] buckets[few=404, many=439437, none=61956, some=2146] sources[none] quality[none]
- order_book: presence[absent=134011, present=369932] state[populated=369932, unavailable=134011] buckets[few=369932, none=134011] sources[book_ticker=369932, unavailable=134011] quality[none=134011, top_of_book_only=369932]
- orderblocks: presence[absent=503943] state[empty=503943] buckets[none=503943] sources[measured_dark=503943] quality[none]
- recent_ticks: presence[present=503943] state[populated=503943] buckets[many=503943] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `10.23664402961731` sec
- Median create→first breach: `4478.94266295433` sec
- Median create→terminal: `4480.912456989288` sec
- Median first breach→terminal: `2.384220838546753` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.9}, "under_180s": {"count": 1, "pct": 2.9}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.9}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.8000000000000013 | 1.2445798018430625 | 0.6427872273158413 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.7618119327640879 | 0.8267888809562215 | 0.9214104716587569 | 0 | 1 |
| MEAN_REVERT | 1 | 1 | 0.8 | 0.5188192907202075 | 1.5419627109267022 | 1 | 0 |
| MOVER_AVWAP_SCALP | 5 | 5 | 2.448224293147865 | 2.8068288066465334 | 0.8160747643826216 | 1 | 4 |
| MOVER_TREND_PULLBACK | 19 | 19 | 3.148454044163623 | 3.0 | 1.1107099776556777 | 10 | 9 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 1.3826628859483168 | 1.56185185853157 | 0.8871568714686113 | 0 | 4 |
| TREND_PULLBACK_EMA | 1 | 1 | 1.6539410489452173 | 1.9156519156519138 | 0.8633828700462871 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 8995.147180080414 | 8996.6912920475 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.7618 | 4478.94266295433 | 4480.912456989288 |
| MEAN_REVERT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.8 | 26252.946489095688 | 26255.72801709175 |
| MOVER_AVWAP_SCALP | 5 | 5 | 40.0 | 20.0 | 40.0 | 0.0 | 0.7133 | 11433.87690281868 | 11442.79573893547 |
| MOVER_TREND_PULLBACK | 19 | 19 | 26.3 | 73.7 | 26.3 | 0.0 | -1.0577 | 2132.7079038619995 | 2146.755257844925 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 28.6 | 28.6 | 28.6 | 0.0 | 0.2428 | 15206.766469955444 | 15207.88417005539 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 25328.71525120735 | 25332.39346599579 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 490 | 0 | 396 | 0.0 | 0.0 | None | None | 94 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3273 | 2 | 3167 | 0.0 | 0.0 | 25328.71525120735 | 25332.39346599579 | 106 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `106`
- Gating Δ: `37404`
- No-generation Δ: `806317`
- Fast failures Δ: `1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.8473, "current_avg_pnl": 0.0, "current_win_rate": 0.0, "previous_avg_pnl": -0.8473, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.2547, "current_avg_pnl": 0.7133, "current_win_rate": 40.0, "previous_avg_pnl": 0.4586, "previous_win_rate": 20.0, "win_rate_delta": 20.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.7276, "current_avg_pnl": -1.0577, "current_win_rate": 26.3, "previous_avg_pnl": 0.6699, "previous_win_rate": 7.7, "win_rate_delta": 18.6}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.702, "current_avg_pnl": 0.2428, "current_win_rate": 28.6, "previous_avg_pnl": -0.4592, "previous_win_rate": 14.3, "win_rate_delta": 14.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": 50, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -6, "geometry_changed_delta": 0, "geometry_preserved_delta": 53, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 21028.72, "median_terminal_delta_sec": 21030.02, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
