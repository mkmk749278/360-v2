# Runtime Truth Report

## Executive summary
- Overall health/freshness: **halted_by_breaker**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `310` sec
- ⛔ **HALTED BY LOSS CIRCUIT BREAKER** — reason: Daily drawdown 10.09% exceeded threshold 10.0%; cooldown remaining: 818.3s. This is a deliberate protective pause (not a crash); the stale heartbeat and zero-signal window are expected while halted.

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 209 | 209 | 203 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 23402 | 23402 | 22765 | 7 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 148228 | 148226 | 21 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 122519 | 122519 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 122234 | 117598 | 4908 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 122541 | 120620 | 1979 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 129612 | 129246 | 389 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 114390 | 114389 | 14 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 122604 | 122632 | 6 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 122643 | 118921 | 5410 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 156439 | 162845 | 2279 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 148249 | 128326 | 28064 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 128842 | 128842 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 122525 | 122536 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 122210 | 122061 | 166 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 124338 | 121783 | 3407 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 121418 | 121918 | 264 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 107191 | 96946 | 10653 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 107605 | 106413 | 1280 | 0 | 0 | 0 | low-sample (ema_alignment_reject) |
| EVAL::VOLUME_SURGE_BREAKOUT | 148188 | 148121 | 108 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 114404 | 114416 | 13 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 7865 | 7865 | 7399 | 6 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1465 | 1465 | 1201 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 65 | 65 | 65 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 56249 | 56249 | 56074 | 2 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 12 | 12 | 9 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 17424 | 17424 | 16101 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 7197 | 7197 | 6276 | 26 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 85036 | 85036 | 75356 | 184 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1256 | 1256 | 1152 | 9 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 10890 | 10890 | 10594 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1226 | 1226 | 1181 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 6223 | 6223 | 5875 | 15 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 414 | 414 | 412 | 2 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 1894 | 1894 | 1879 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=148226): breakout_not_found=93804, basic_filters_failed=37106, move_not_fresh=9888, breakout_stale=5952, retest_proximity_failed=1099, volume_spike_missing=288, move_exhausted=60, missing_fvg_or_orderblock=28, ema_alignment_reject=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=122519): cls_disabled_merged_into_lsr=122519
- **EVAL::DIVERGENCE_CONTINUATION** (total=117598): cvd_divergence_failed=61113, basic_filters_failed=24498, h1_trend_not_aligned=19302, ema_alignment_reject=10443, retest_proximity_failed=1789, missing_fvg_or_orderblock=430, missing_cvd=23
- **EVAL::FAILED_AUCTION_RECLAIM** (total=120620): auction_not_detected=79547, basic_filters_failed=23667, reclaim_hold_failed=6722, regime_blocked=5463, tail_too_small=5195, rsi_reject=26
- **EVAL::FUNDING_EXTREME** (total=129246): funding_not_extreme=96833, basic_filters_failed=25316, missing_funding_rate=3195, ema_alignment_reject=2138, rsi_reject=727, cvd_divergence_failed=560, momentum_reject=387, missing_fvg_or_orderblock=90
- **EVAL::LIQUIDATION_REVERSAL** (total=114389): cascade_threshold_not_met=87387, basic_filters_failed=25914, cvd_divergence_failed=576, rsi_reject=492, missing_fvg_or_orderblock=14, volume_spike_missing=3, missing_cvd=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=122632): no_ma_cross=96780, basic_filters_failed=24507, ma_cross_cooldown=926, ma_cross_htf_misaligned=419
- **EVAL::MEAN_REVERT** (total=118921): no_extension=95678, basic_filters_failed=23243
- **EVAL::MOVER_AVWAP_SCALP** (total=162845): no_avwap_tag=67229, basic_filters_failed=37242, no_mover_leg=32787, avwap_slope_against=14450, avwap_reclaim_no_volume=7207, no_avwap_reclaim=3875, anchor_too_recent=55
- **EVAL::MOVER_TREND_PULLBACK** (total=128326): mover_run_too_small=55833, basic_filters_failed=37169, no_reclaim=29937, no_pullback_tag=5387
- **EVAL::OPENING_RANGE_BREAKOUT** (total=128842): feature_disabled=128842
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=122536): regime_blocked=94938, breakout_not_found=21553, basic_filters_failed=4861, adx_reject=1142, ema_alignment_reject=24, rsi_reject=18
- **EVAL::QUIET_COMPRESSION_BREAK** (total=122061): compression_not_detected=66114, regime_blocked=32998, basic_filters_failed=18796, breakout_not_detected=3744, volume_confirmation_failed=405, rsi_reject=4
- **EVAL::RANGE_FADE** (total=121783): no_range_edge=98538, basic_filters_failed=23245
- **EVAL::SR_FLIP_RETEST** (total=121918): flip_close_not_confirmed=79949, basic_filters_failed=23651, long_break_volume_thin=5579, regime_blocked=5454, retest_out_of_zone=3378, h1_break_not_confirmed=2022, reclaim_hold_failed=1328, long_acceptance_not_held=219, ema_alignment_reject=133, wick_quality_failed=107, whipsaw_flip=83, missing_fvg_or_orderblock=15
- **EVAL::STANDARD** (total=96946): adx_reject=25923, momentum_reject=21601, basic_filters_failed=16078, macd_reject=13030, sweeps_not_detected=10286, ema_alignment_reject=7538, htf_poi_unanchored=2117, invalid_sl_geometry=324, rsi_reject=33, mtf_reject=16
- **EVAL::TREND_PULLBACK** (total=106413): ema_alignment_reject=21947, h1_trend_not_aligned=20861, basic_filters_failed=18366, ema_not_tested_prev=12478, h1_pullback_not_confirmed=10243, no_ema_reclaim_close=9548, rsi_reject=4629, body_conviction_fail=4470, prev_already_above_emas=1491, no_prev_high_break=1146, prev_already_below_emas=439, momentum_flat=329, no_prev_low_break=251, ema21_not_tagged=102, missing_fvg_or_orderblock=101, momentum_reject=12
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=148121): breakout_not_found=76666, basic_filters_failed=37104, move_not_fresh=22324, breakout_stale=8040, retest_proximity_failed=3447, volume_spike_missing=493, missing_fvg_or_orderblock=44, move_exhausted=3
- **EVAL::WHALE_MOMENTUM** (total=114416): momentum_reject=83663, recent_ticks_insufficient=25976, basic_filters_failed=4777

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=5): execution:overextended=5
- **DIVERGENCE_CONTINUATION** (total=350): setup_compat:regime_VOLATILE_UNSUITABLE=316, setup_compat:regime_BREAKOUT_EXPANSION=34
- **FAILED_AUCTION_RECLAIM** (total=1675): execution:overextended=1237, setup_compat:regime_STRONG_TREND=272, context_floor=166
- **FUNDING_EXTREME_SIGNAL** (total=1078): execution:trigger_not_confirmed=1078
- **LIQUIDATION_REVERSAL** (total=65): execution:trigger_not_confirmed=65
- **LIQUIDITY_SWEEP_REVERSAL** (total=13045): execution:overextended=5381, execution:trigger_not_confirmed=4974, setup_compat:regime_STRONG_TREND=2690
- **MA_CROSS_TREND_SHIFT** (total=5): setup_compat:regime_DIRTY_RANGE=4, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=7032): setup_compat:regime_STRONG_TREND=2917, setup_compat:regime_WEAK_TREND=2840, execution:overextended=1275
- **MOVER_AVWAP_SCALP** (total=3413): execution:overextended=2737, execution:trigger_not_confirmed=484, entry_quality=192
- **MOVER_TREND_PULLBACK** (total=34060): execution:trigger_not_confirmed=17971, execution:overextended=14436, entry_quality=1653
- **QUIET_COMPRESSION_BREAK** (total=1): execution:overextended=1
- **RANGE_FADE** (total=6048): setup_compat:regime_STRONG_TREND=2772, setup_compat:regime_WEAK_TREND=2501, setup_compat:regime_VOLATILE_UNSUITABLE=542, execution:overextended=153, setup_compat:regime_BREAKOUT_EXPANSION=80
- **TREND_PULLBACK_EMA** (total=5701): setup_compat:regime_CLEAN_RANGE=3974, setup_compat:regime_DIRTY_RANGE=1584, entry_quality=89, setup_compat:regime_VOLATILE_UNSUITABLE=54
- **VOLUME_SURGE_BREAKOUT** (total=55): execution:overextended=55
- **WHALE_MOMENTUM** (total=1579): execution:trigger_not_confirmed=1579

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 474634 | 56.1% |
| TRENDING_UP | 136450 | 16.1% |
| QUIET | 115644 | 13.7% |
| TRENDING_DOWN | 76888 | 9.1% |
| VOLATILE | 41826 | 4.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **97**
- Average confidence gap to threshold: **13.96** (samples=97) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: LITUSDT=47, HYPEUSDT=7, XLMUSDT=7, BTCUSDT=6, LSKUSDT=6, ETCUSDT=6, ASTERUSDT=5, 1000SHIBUSDT=4, ETHUSDT=4, BULLAUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 5 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 2 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 72 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 6 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 35 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 130 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 10 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 23 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 13 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 26 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | kept | min_confidence_pass | 3 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 112 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 3 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 510 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 880 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 55 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3214 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 31 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 23 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 11 |
| RANGE_FADE | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 9 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 33 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 51 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 5 | 48.70 | 61.00 | 12.30 | 20.36 | 20.00 | 20.00 | 3.00 | 21.60 |
| BREAKDOWN_SHORT | kept | 2 | 69.20 | 65.00 | -4.20 | 20.10 | 18.30 | 20.00 | 4.50 | 6.00 |
| DIVERGENCE_CONTINUATION | filtered | 78 | 55.41 | 63.10 | 7.69 | 20.53 | 19.84 | 17.35 | 2.29 | 10.61 |
| DIVERGENCE_CONTINUATION | kept | 35 | 67.73 | 65.00 | -2.73 | 19.69 | 19.74 | 17.95 | 0.29 | -1.02 |
| FAILED_AUCTION_RECLAIM | filtered | 140 | 51.18 | 60.55 | 9.37 | 19.73 | 17.37 | 20.00 | 2.81 | 19.14 |
| FAILED_AUCTION_RECLAIM | kept | 23 | 68.38 | 65.00 | -3.38 | 20.30 | 17.73 | 20.00 | 1.61 | 1.31 |
| FUNDING_EXTREME_SIGNAL | filtered | 13 | 46.38 | 61.00 | 14.62 | 22.78 | 18.62 | 17.00 | 2.69 | 3.85 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 26 | 69.03 | 65.00 | -4.03 | 21.10 | 14.56 | 16.75 | 0.19 | 3.47 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 69.40 | 65.00 | -4.40 | 21.20 | 16.25 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | kept | 3 | 71.97 | 65.00 | -6.97 | 21.13 | 14.60 | 16.17 | 0.00 | 2.73 |
| MOVER_AVWAP_SCALP | filtered | 115 | 61.43 | 65.00 | 3.57 | 20.25 | 17.97 | 15.80 | 4.17 | 14.72 |
| MOVER_AVWAP_SCALP | kept | 510 | 79.29 | 65.00 | -14.29 | 19.82 | 18.03 | 15.80 | 5.02 | 1.71 |
| MOVER_TREND_PULLBACK | filtered | 935 | 53.88 | 63.15 | 9.27 | 20.31 | 18.80 | 15.80 | 3.50 | 18.37 |
| MOVER_TREND_PULLBACK | kept | 3214 | 76.10 | 65.00 | -11.10 | 19.98 | 18.44 | 15.80 | 4.12 | 2.08 |
| QUIET_COMPRESSION_BREAK | filtered | 54 | 56.00 | 65.00 | 9.00 | 22.70 | 19.18 | 20.00 | 0.00 | 13.64 |
| QUIET_COMPRESSION_BREAK | kept | 11 | 73.14 | 65.00 | -8.14 | 21.32 | 18.85 | 20.00 | 0.00 | 1.40 |
| RANGE_FADE | kept | 1 | 67.00 | 65.00 | -2.00 | 20.40 | 15.40 | 19.60 | 0.00 | 0.00 |
| SR_FLIP_RETEST | kept | 9 | 73.70 | 65.00 | -8.70 | 21.20 | 20.00 | 15.20 | 2.50 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 33 | 57.31 | 63.55 | 6.24 | 20.39 | 19.43 | 18.94 | 5.27 | 11.18 |
| TREND_PULLBACK_EMA | kept | 51 | 77.99 | 65.00 | -12.99 | 20.40 | 19.86 | 16.38 | 5.06 | 0.50 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 79.65 | 65.00 | -14.65 | 20.20 | 18.45 | 20.00 | 5.00 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 5 | 48.70 | 17.00 | 14.00 | 15.00 | 14.00 | 5.00 | 2.30 | 3.00 |
| BREAKDOWN_SHORT | kept | 2 | 69.20 | 21.00 | 16.00 | 12.00 | 12.50 | 5.00 | 4.20 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 78 | 55.41 | 22.74 | 10.05 | 4.58 | 14.87 | 5.24 | 8.36 | 2.29 |
| DIVERGENCE_CONTINUATION | kept | 35 | 67.73 | 24.54 | 9.71 | 7.37 | 12.89 | 4.51 | 9.37 | 0.29 |
| FAILED_AUCTION_RECLAIM | filtered | 140 | 51.18 | 21.80 | 17.71 | 5.57 | 13.04 | 6.43 | 3.49 | 2.81 |
| FAILED_AUCTION_RECLAIM | kept | 23 | 68.38 | 19.09 | 17.83 | 3.52 | 13.83 | 6.07 | 7.88 | 1.61 |
| FUNDING_EXTREME_SIGNAL | filtered | 13 | 46.38 | 25.00 | 8.00 | 6.00 | 15.15 | 5.00 | 3.38 | 2.69 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 26 | 69.03 | 25.00 | 17.38 | 3.46 | 14.15 | 5.38 | 6.84 | 0.19 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 69.40 | 17.00 | 14.00 | 7.50 | 15.50 | 6.75 | 8.65 | 0.00 |
| MEAN_REVERT | kept | 3 | 71.97 | 24.33 | 16.67 | 10.00 | 13.00 | 5.00 | 5.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 115 | 61.43 | 16.90 | 18.00 | 10.70 | 14.00 | 5.29 | 8.54 | 4.17 |
| MOVER_AVWAP_SCALP | kept | 510 | 79.29 | 19.32 | 18.00 | 10.64 | 14.28 | 7.07 | 9.53 | 5.02 |
| MOVER_TREND_PULLBACK | filtered | 935 | 53.88 | 17.68 | 18.29 | 7.96 | 12.44 | 6.35 | 8.36 | 3.50 |
| MOVER_TREND_PULLBACK | kept | 3214 | 76.10 | 19.39 | 18.03 | 8.05 | 12.79 | 6.39 | 9.44 | 4.12 |
| QUIET_COMPRESSION_BREAK | filtered | 54 | 56.00 | 21.59 | 15.70 | 11.83 | 14.00 | 5.78 | 2.68 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 11 | 73.14 | 19.18 | 16.91 | 10.91 | 14.00 | 6.91 | 7.45 | 0.00 |
| RANGE_FADE | kept | 1 | 67.00 | 25.00 | 18.00 | 3.00 | 12.00 | 5.00 | 4.00 | 0.00 |
| SR_FLIP_RETEST | kept | 9 | 73.70 | 25.00 | 8.00 | 6.00 | 17.00 | 8.50 | 6.70 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 33 | 57.31 | 18.45 | 18.00 | 7.50 | 15.91 | 5.00 | 7.90 | 5.27 |
| TREND_PULLBACK_EMA | kept | 51 | 77.99 | 17.90 | 18.00 | 7.53 | 14.22 | 6.76 | 9.25 | 5.06 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 79.65 | 21.00 | 16.00 | 12.00 | 14.00 | 5.00 | 9.65 | 5.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 5 | 48.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | **6.00** |
| BREAKDOWN_SHORT | kept | 2 | 69.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.00 | **3.00** |
| DIVERGENCE_CONTINUATION | filtered | 78 | 55.41 | 0.00 | 0.00 | 0.82 | 0.00 | 1.66 | 0.00 | 0.00 | 0.00 | **2.48** |
| DIVERGENCE_CONTINUATION | kept | 35 | 67.73 | 0.00 | 0.00 | 0.78 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.78** |
| FAILED_AUCTION_RECLAIM | filtered | 140 | 51.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.93 | 0.00 | 0.00 | 0.00 | **0.93** |
| FAILED_AUCTION_RECLAIM | kept | 23 | 68.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 13 | 46.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 26 | 69.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 69.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 3 | 71.97 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 115 | 61.43 | 0.00 | 0.00 | 3.20 | 0.00 | 9.50 | 0.00 | 0.00 | 0.28 | **12.98** |
| MOVER_AVWAP_SCALP | kept | 510 | 79.29 | 0.00 | 0.00 | 0.03 | 0.00 | 1.19 | 0.00 | 0.00 | 0.01 | **1.23** |
| MOVER_TREND_PULLBACK | filtered | 935 | 53.88 | 0.12 | 0.00 | 4.35 | 0.00 | 1.03 | 0.13 | 0.00 | 0.15 | **5.78** |
| MOVER_TREND_PULLBACK | kept | 3214 | 76.10 | 0.09 | 0.00 | 0.80 | 0.00 | 0.29 | 0.03 | 0.00 | 0.00 | **1.21** |
| QUIET_COMPRESSION_BREAK | filtered | 54 | 56.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 4.84 | **4.84** |
| QUIET_COMPRESSION_BREAK | kept | 11 | 73.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| RANGE_FADE | kept | 1 | 67.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 9 | 73.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 33 | 57.31 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| TREND_PULLBACK_EMA | kept | 51 | 77.99 | 0.00 | 0.00 | 0.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.31** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 79.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **112660 held of 322516 seen** across 21 strategies; 2571 cells past the sample floor; **1186 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 39172 | 557/38615/0 | 46% | -0.13 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.22R) |
| MOVER_AVWAP_SCALP | 14117 | 189/13928/0 | 40% | -0.27 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 8540 | 104/8436/0 | 42% | -0.15 | LONDON/RANGE/NORMAL/BTC_NEUTRAL (+1.74R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 7278 | 42/7236/0 | 51% | +0.02 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.68R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 6085 | 0/0/6085 | 43% | -0.11 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.50R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-0.87R) |
| TREND_PULLBACK_EMA | 5709 | 24/5685/0 | 46% | -0.10 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.33R) |
| SHADOW_RANGE_FADE | 5238 | 0/0/5238 | 37% | -0.09 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | LONDON/QUIET/NORMAL/BTC_RISING (-1.17R) |
| QUIET_COMPRESSION_BREAK | 4995 | 299/4696/0 | 47% | -0.12 | ASIA/RANGE/NORMAL/BTC_FALLING/MIDCAP (+0.88R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4753 | 0/0/4753 | 34% | -0.40 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| LIQUIDITY_SWEEP_REVERSAL | 3555 | 65/3490/0 | 40% | -0.33 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.93R) | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.24R) |
| WHALE_MOMENTUM | 3391 | 2/3389/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| MEAN_REVERT | 2239 | 30/2209/0 | 49% | -0.11 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.62R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 1955 | 2/1953/0 | 32% | -0.44 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 1858 | 0/1858/0 | 36% | -0.15 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| SR_FLIP_RETEST | 1274 | 12/1262/0 | 50% | -0.17 | ASIA/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.80R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.25R) |
| SHADOW_CASCADE_REVERSAL | 909 | 0/0/909 | 54% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.42R) |
| RANGE_FADE | 755 | 2/753/0 | 39% | -0.40 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 551 | 53/498/0 | 32% | -0.35 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.18R) |
| LIQUIDATION_REVERSAL | 212 | 0/212/0 | 10% | -1.02 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 66 | 8/58/0 | 48% | -0.01 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 8 | 0/8/0 | 75% | +0.30 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 147 | 27% / -0.56R | 147 | 46% / -0.19R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 476 | 43% / -0.24R | 476 | 55% / -0.03R | +0.20 | **ATR** |
| BREAKDOWN_SHORT | 45 | 40% / -0.21R | 45 | 44% / -0.08R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 1131 | 44% / -0.20R | 1131 | 50% / -0.08R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 368 | 44% / -0.33R | 368 | 46% / -0.22R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 140 | 48% / -0.27R | 140 | 50% / -0.17R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 6053 | 50% / -0.10R | 6053 | 55% / -0.01R | +0.09 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 719 | 50% / -0.22R | 719 | 56% / -0.13R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 808 | 43% / -0.18R | 808 | 45% / -0.10R | +0.08 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 105 | 39% / -0.13R | 105 | 47% / -0.07R | +0.06 | **ATR** |
| DIVERGENCE_CONTINUATION | 672 | 51% / -0.05R | 672 | 57% / -0.03R | +0.02 | **ATR** |
| RANGE_FADE | 39 | 38% / -0.23R | 39 | 41% / -0.24R | -0.01 | **FIXED** |
| MEAN_REVERT | 165 | 54% / -0.05R | 165 | 52% / -0.05R | +0.01 | **ATR** |
| QUIET_COMPRESSION_BREAK | 803 | 45% / -0.16R | 803 | 45% / -0.17R | -0.01 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 21 | 43% / -0.12R | 21 | 43% / -0.12R | +0.01 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 50% / -0.21R | 6 | 50% / -0.10R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 14 | 29% / -0.51R | 14 | 57% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8682 | 29% | -0.24R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1131 | 48% | -0.07R | 195 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 65 | 49% | -0.07R | 47 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 141 | 36% / -0.32R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 778 | 36% / -0.12R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 7768 | 36% / -0.17R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1506 | 35% / -0.12R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 652 | 35% / -0.14R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 765 | 40% / +0.01R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 631 | 39% / -0.02R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 719 | 42% / -0.14R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 150 | 28% / -0.42R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 194 | 30% / -0.60R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 136 | 56% / +0.14R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 78 | 42% / -0.13R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 31 | 35% / +0.11R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 144 | 35% / -0.39R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 31 | 23% / -0.36R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 19 | 42% / -0.05R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 10 | 40% / +0.02R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 60 · alerting: **6** · boot grace active: False
- **ALERT** `geometry_ab` — upstream +183 but output +0 (streak 20/6) (sustained 20 cycles)
- **ALERT** `sar_exit_shadow` — upstream +183 but output +0 (streak 20/6) (sustained 20 cycles)
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×355]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 39/6) (sustained 39 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=129, profile_reject=1. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 21/6) (sustained 21 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.61R (bound 0.3) (streak 141/6) (sustained 141 cycles)
- **ALERT** `tuned_variants` — 53 non-stamps — atr_arm_uncomputable=53 (seen=1255 stamped=161 skipped=1041) (streak 141/6) (sustained 141 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 41 fed / 0 quiet / 0 never delivered of 41 subscribed; 13969957 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 31 arms current, none stalled; covering 841/841 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 60 arms current, none stalled; covering 1052/1052 signals (100%) | 0 |
| auto_dispatch | ok | 21 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: mode:paper=44. No user is on live. | 0 |
| binance_ip_weight | ok | peak 292/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 83934.90 | 0 |
| candle_coverage | ok | 93/93 symbols with ≥20 15m candles, 93/93 updated within 45m [fresh=93; 74 Tier-1 futures + 19 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 234 dup bars, 0 undedupable; ws 0 out-of-order, 161 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 34 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 34 cohorts, 9 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | violating | upstream +33 but output +0 (streak 20/72) | 20 |
| dark_atr_trail_arms | ok | no open arms; covering 1079/1096 signals (98%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 1 of 107 open dark rows are not being advanced (worst: XAIUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 9/120) | 9 |
| dark_sar_arms | ok | no open arms; covering 1076/1093 signals (98%) | 0 |
| depth_feed | ok | 41/41 books fresh (stale 0, never 0, thin 0); 4199235 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.61R (bound 0.3) (streak 141/6) | 141 |
| emission_controller | ok | last cycle 661s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×355]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 39/6) | 39 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=129, profile_reject=1. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 21/6) | 21 |
| firestore_read_budget | ok | 1,328 reads/day of 50,000 [engine 1,328, signing 0]; top site keystore.roster_doc at 289/day (engine) | 0 |
| footprint_bars | ok | 4900 sealed bars over 41 symbols; 724 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +183 but output +0 (streak 20/6) | 20 |
| indicator_cache_key | ok | 31810 frozen value(s) avoided; 324350 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.12R over n=2209 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +29 / upstream +183 | 0 |
| mover_admission_metadata | ok | 907 symbols known, 201 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 19 held, 19 with scan counts, 16 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 8 locked / 8 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 1908584 evicted (sampled: execution:trigger_not_confirmed 400/703271, execution:overextended 400/639254, setup_compat:regime_STRONG_TREND 400/278748) | 0 |
| price_action_lane | ok | 479668 evaluated, 387 emitted; layer1 387 stamped / 0 blind; cooldown=69849, delta_opposed=42603, no_footprint=194140, no_opposing_target=2469, no_sweep=134683, rr_below_floor=35537 | 0 |
| promoted_pair_integrity | ok | 19/19 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.40R over n=753 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +24 / upstream +183 | 0 |
| sar_alignment_crosscheck | ok | 175/6029 disagreed (2.9%) | 0 |
| sar_exit_shadow | violating | upstream +183 but output +0 (streak 20/6) | 20 |
| sar_hold_arm | ok | 1826 held arms settled, 174 unscored, 58 still walking (54 awaiting the second arm) | 0 |
| sar_ledger_candles | violating | 8/22 unfetchable (36%); top cause: gap or duplicate bar in the 15m window; symbols: LSKUSDT (streak 3/6) | 3 |
| sar_live_arms | ok | 58 arms current, none stalled; covering 1051/1051 signals (100%) | 0 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 1 resolved, 13 still mid-window | 0 |
| scan_cycle | ok | last 7.86s, worst 72.29s over 5546 lifetime cycles; lifetime 1 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 5.98s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 202573 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 1s ago (23.6s to run, worst 46.47s), 121 overrun(s) of 3127 cycles, TTL 900s; slowest engine_state=6.38s, signals=3.35s, tickers=1.28s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +8 / upstream +183 | 0 |
| structural_snap | ok | 5577/5577 measured, 23 blind, 0 levels moved (refusals: redetect_cooldown=63) | 0 |
| structural_veto_lane | ok | 198 stamped; 0 with no readable level book, 25 with clear air ahead, 123 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +183 / upstream +33 | 0 |
| tuned_variants | violating | 53 non-stamps — atr_arm_uncomputable=53 (seen=1255 stamped=161 skipped=1041) (streak 141/6) | 141 |
| unlock_shorts | ok | 1 open, 45 scheduled, calendar 0.3h old | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3950833`
- `Path funnel` emissions: `98`
- `Regime distribution` emissions: `98`
- `QUIET_SCALP_BLOCK` events: `97`
- `confidence_gate` events: `5262`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **2**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 2 | 2108 | 2108 | 8175 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[absent=1791, present=704079] state[empty=1791, populated=704079] buckets[few=10, many=704002, none=1791, some=67] sources[none] quality[none]
- funding_rate: presence[absent=96638, present=609232] state[empty=96638, populated=609232] buckets[few=609232, none=96638] sources[none] quality[none]
- liquidation_clusters: presence[absent=375897, present=329973] state[empty=375897, populated=329973] buckets[few=265203, none=375897, some=64770] sources[none] quality[none]
- oi_snapshot: presence[absent=91945, present=613925] state[empty=91945, populated=613925] buckets[few=138, many=612934, none=91945, some=853] sources[none] quality[none]
- order_book: presence[absent=183554, present=522316] state[populated=522316, unavailable=183554] buckets[few=522316, none=183554] sources[book_ticker=522316, unavailable=183554] quality[none=183554, top_of_book_only=522316]
- orderblocks: presence[absent=705870] state[empty=705870] buckets[none=705870] sources[measured_dark=705870] quality[none]
- recent_ticks: presence[present=705870] state[populated=705870] buckets[many=705870] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.2423770427703857` sec
- Median create→first breach: `6402.110624909401` sec
- Median create→terminal: `6402.110687494278` sec
- Median first breach→terminal: `6.759166717529297e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 0.8614896571056418 | 1.9616490907489545 | 0.4469055460468455 | 0 | 2 |
| DIVERGENCE_CONTINUATION | 1 | 1 | 2.3637501020491363 | 2.5705557171952282 | 0.919548285313286 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 1.8754089422028237 | 2.042209565420925 | 0.91183631292799 | 0 | 3 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 1.2374563084902483 | 1.3975155279503089 | 0.8854687362974677 | 0 | 1 |
| MOVER_AVWAP_SCALP | 1 | 1 | 2.379749538658931 | 2.652577787305471 | 0.8971459951326506 | 0 | 1 |
| MOVER_TREND_PULLBACK | 31 | 31 | 3.0622678295671144 | 2.9850000000000017 | 1.024752477852664 | 16 | 15 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 1.5620056989687985 | 1.6402475005627908 | 0.9121849683683163 | 0 | 4 |
| RANGE_FADE | 1 | 1 | 0.8040935672514707 | 1.4480646059593456 | 0.5552884615384666 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -1.08 | 15311.090267896652 | 15311.09029686451 |
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.3638 | 17009.8041369915 | 17009.80416202545 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -1.8163 | 24154.79517006874 | 24154.795234918594 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.2375 | 47746.93015217781 | 47746.930230140686 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 13493.975959062576 | 13493.975982904434 |
| MOVER_TREND_PULLBACK | 31 | 31 | 32.3 | 45.2 | 32.3 | 0.0 | 0.5275 | 5612.098603010178 | 5613.553952932358 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 16.7 | 50.0 | 16.7 | 0.0 | -0.5092 | 11931.989500522614 | 11932.735684871674 |
| RANGE_FADE | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.5669 | 4266.115149974823 | 4267.159593820572 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1226 | 0 | 1181 | 0.0 | 0.0 | None | None | 45 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 6223 | 15 | 5875 | 0.0 | 0.0 | None | None | 348 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-249`
- Gating Δ: `45912`
- No-generation Δ: `27700`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.1423, "current_avg_pnl": -1.8163, "current_win_rate": 0.0, "previous_avg_pnl": -1.674, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.1934, "current_avg_pnl": -1.2375, "current_win_rate": 0.0, "previous_avg_pnl": -1.0441, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.9484, "current_avg_pnl": 0.0, "current_win_rate": 0.0, "previous_avg_pnl": -0.9484, "previous_win_rate": 16.7, "win_rate_delta": -16.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.2732, "current_avg_pnl": 0.5275, "current_win_rate": 32.3, "previous_avg_pnl": 0.8007, "previous_win_rate": 44.4, "win_rate_delta": -12.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0929, "current_avg_pnl": -0.5092, "current_win_rate": 16.7, "previous_avg_pnl": -0.6021, "previous_win_rate": 12.5, "win_rate_delta": 4.2}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": -55, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -4665.45, "median_terminal_delta_sec": -4665.45, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -15, "geometry_changed_delta": 0, "geometry_preserved_delta": -68, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **WHALE_MOMENTUM**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
