# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `1833` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 123 | 123 | 123 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10420 | 10420 | 9986 | 2 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 86427 | 86419 | 47 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 82271 | 82271 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 81732 | 79709 | 2529 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 82311 | 81410 | 986 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 83909 | 83726 | 234 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 73473 | 73491 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 82406 | 82465 | 10 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 82489 | 79962 | 3681 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 91266 | 95792 | 1239 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 86470 | 80763 | 10418 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 83329 | 83329 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 82280 | 82297 | 7 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 81683 | 81414 | 312 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 83656 | 82331 | 1958 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 81048 | 81371 | 244 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 70999 | 67957 | 3252 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 71218 | 70800 | 473 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 86354 | 86381 | 38 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 73494 | 73540 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4416 | 4416 | 4169 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 2016 | 2016 | 1785 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 19266 | 19266 | 18995 | 13 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 16 | 16 | 13 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 11078 | 11078 | 9287 | 4 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3392 | 3392 | 2417 | 36 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 34003 | 34003 | 27158 | 163 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 29 | 29 | 29 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1904 | 1904 | 1226 | 53 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 5576 | 5576 | 4971 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1120 | 1120 | 485 | 8 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2254 | 2254 | 2196 | 10 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 186 | 186 | 160 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=86419): breakout_not_found=47912, basic_filters_failed=20603, move_not_fresh=12304, breakout_stale=4608, retest_proximity_failed=824, volume_spike_missing=158, missing_fvg_or_orderblock=8, move_exhausted=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=82271): cls_disabled_merged_into_lsr=82271
- **EVAL::DIVERGENCE_CONTINUATION** (total=79709): cvd_divergence_failed=31046, h1_trend_not_aligned=28019, basic_filters_failed=15022, ema_alignment_reject=4877, retest_proximity_failed=583, missing_fvg_or_orderblock=161, cvd_insufficient=1
- **EVAL::FAILED_AUCTION_RECLAIM** (total=81410): auction_not_detected=58518, basic_filters_failed=14834, reclaim_hold_failed=3437, tail_too_small=2706, regime_blocked=1882, rsi_reject=33
- **EVAL::FUNDING_EXTREME** (total=83726): funding_not_extreme=63993, basic_filters_failed=16091, ema_alignment_reject=1529, missing_funding_rate=1119, rsi_reject=590, cvd_divergence_failed=203, momentum_reject=185, missing_fvg_or_orderblock=16
- **EVAL::LIQUIDATION_REVERSAL** (total=73491): cascade_threshold_not_met=56986, basic_filters_failed=16153, cvd_divergence_failed=183, rsi_reject=141, missing_fvg_or_orderblock=26, volume_spike_missing=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=82465): no_ma_cross=65138, basic_filters_failed=15045, ma_cross_cooldown=1887, ma_cross_htf_misaligned=395
- **EVAL::MEAN_REVERT** (total=79962): no_extension=69987, basic_filters_failed=9975
- **EVAL::MOVER_AVWAP_SCALP** (total=95792): no_mover_leg=35950, no_avwap_tag=29747, basic_filters_failed=20927, avwap_slope_against=5955, avwap_reclaim_no_volume=1885, no_avwap_reclaim=1280, anchor_too_recent=48
- **EVAL::MOVER_TREND_PULLBACK** (total=80763): mover_run_too_small=46380, basic_filters_failed=20773, no_reclaim=12067, no_pullback_tag=1543
- **EVAL::OPENING_RANGE_BREAKOUT** (total=83329): feature_disabled=83329
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=82297): regime_blocked=55757, breakout_not_found=21063, basic_filters_failed=3481, adx_reject=1962, ema_alignment_reject=34
- **EVAL::QUIET_COMPRESSION_BREAK** (total=81414): regime_blocked=28270, compression_not_detected=26188, breakout_not_detected=14226, basic_filters_failed=11333, volume_confirmation_failed=1324, rsi_reject=54, missing_fvg_or_orderblock=19
- **EVAL::RANGE_FADE** (total=82331): no_range_edge=72346, basic_filters_failed=9985
- **EVAL::SR_FLIP_RETEST** (total=81371): flip_close_not_confirmed=58572, basic_filters_failed=14800, long_break_volume_thin=1931, regime_blocked=1866, retest_out_of_zone=1821, h1_break_not_confirmed=1265, reclaim_hold_failed=584, ema_alignment_reject=256, wick_quality_failed=130, long_acceptance_not_held=126, whipsaw_flip=14, missing_fvg_or_orderblock=6
- **EVAL::STANDARD** (total=67957): momentum_reject=22785, adx_reject=15856, sweeps_not_detected=8634, basic_filters_failed=7315, macd_reject=6698, ema_alignment_reject=4842, htf_poi_unanchored=1737, invalid_sl_geometry=54, rsi_reject=30, mtf_reject=6
- **EVAL::TREND_PULLBACK** (total=70800): h1_trend_not_aligned=30058, ema_alignment_reject=12371, h1_pullback_not_confirmed=7932, basic_filters_failed=7118, no_ema_reclaim_close=4374, ema_not_tested_prev=3552, body_conviction_fail=2335, rsi_reject=1568, prev_already_above_emas=575, no_prev_high_break=345, prev_already_below_emas=251, no_prev_low_break=148, momentum_flat=113, missing_fvg_or_orderblock=36, ema21_not_tagged=21, momentum_reject=3
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=86381): breakout_not_found=53250, basic_filters_failed=20597, move_not_fresh=7931, breakout_stale=3753, retest_proximity_failed=704, volume_spike_missing=132, missing_fvg_or_orderblock=8, move_exhausted=4, rsi_reject=2
- **EVAL::WHALE_MOMENTUM** (total=73540): momentum_reject=46910, recent_ticks_insufficient=17890, basic_filters_failed=8740

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=278): setup_compat:regime_VOLATILE_UNSUITABLE=278
- **FAILED_AUCTION_RECLAIM** (total=1484): setup_compat:regime_STRONG_TREND=1001, execution:overextended=343, context_floor=140
- **FUNDING_EXTREME_SIGNAL** (total=1752): execution:trigger_not_confirmed=1746, context_floor=6
- **LIQUIDATION_REVERSAL** (total=4): execution:trigger_not_confirmed=4
- **LIQUIDITY_SWEEP_REVERSAL** (total=5363): setup_compat:regime_STRONG_TREND=2416, execution:trigger_not_confirmed=1972, execution:overextended=975
- **MA_CROSS_TREND_SHIFT** (total=13): setup_compat:regime_CLEAN_RANGE=6, setup_compat:regime_DIRTY_RANGE=4, execution:trigger_not_confirmed=2, execution:overextended=1
- **MEAN_REVERT** (total=7305): setup_compat:regime_STRONG_TREND=3360, setup_compat:regime_WEAK_TREND=3333, execution:overextended=612
- **MOVER_AVWAP_SCALP** (total=1858): execution:overextended=1494, entry_quality=189, execution:trigger_not_confirmed=175
- **MOVER_TREND_PULLBACK** (total=13068): execution:trigger_not_confirmed=7531, execution:overextended=4411, entry_quality=1126
- **QUIET_COMPRESSION_BREAK** (total=102): execution:trigger_not_confirmed=102
- **RANGE_FADE** (total=3898): setup_compat:regime_STRONG_TREND=1799, setup_compat:regime_WEAK_TREND=1657, execution:overextended=222, setup_compat:regime_VOLATILE_UNSUITABLE=156, setup_compat:regime_BREAKOUT_EXPANSION=33, context_edge=31
- **TREND_PULLBACK_EMA** (total=1882): setup_compat:regime_CLEAN_RANGE=1229, setup_compat:regime_DIRTY_RANGE=619, setup_compat:regime_VOLATILE_UNSUITABLE=24, entry_quality=10
- **VOLUME_SURGE_BREAKOUT** (total=21): execution:overextended=21

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 181178 | 34.7% |
| RANGING | 159970 | 30.6% |
| TRENDING_UP | 86436 | 16.5% |
| TRENDING_DOWN | 77444 | 14.8% |
| VOLATILE | 17423 | 3.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **132**
- Average confidence gap to threshold: **9.15** (samples=132) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XRPUSDT=32, 1000PEPEUSDT=17, DOTUSDT=14, SUIUSDT=13, XMRUSDT=11, BCHUSDT=8, ETHUSDT=6, ZECUSDT=4, INJUSDT=4, DOGEUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 33 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 60 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 14 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 4 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 15 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 4 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 41 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 4 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 61 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 3 |
| MEAN_REVERT | filtered | min_confidence | 65 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 3 |
| MEAN_REVERT | kept | min_confidence_pass | 4 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 55 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 3 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 319 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 423 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 9 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2121 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 86 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 31 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 439 |
| SR_FLIP_RETEST | filtered | min_confidence | 105 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 13 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 52 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 25 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 5 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 33 | 55.15 | 65.00 | 9.85 | 19.09 | 20.00 | 16.79 | -0.06 | 12.55 |
| DIVERGENCE_CONTINUATION | kept | 60 | 73.63 | 65.00 | -8.63 | 20.03 | 19.96 | 16.32 | 2.78 | -1.65 |
| FAILED_AUCTION_RECLAIM | filtered | 18 | 49.37 | 63.89 | 14.52 | 22.35 | 20.00 | 20.00 | 1.97 | 4.94 |
| FUNDING_EXTREME_SIGNAL | filtered | 15 | 43.63 | 61.87 | 18.24 | 18.27 | 16.28 | 17.47 | 3.33 | 9.67 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 74.55 | 65.00 | -9.55 | 20.20 | 14.00 | 17.00 | 6.50 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 45 | 57.92 | 65.00 | 7.08 | 19.65 | 19.61 | 19.07 | 2.29 | 2.43 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 61 | 66.87 | 65.00 | -1.87 | 20.35 | 18.44 | 17.03 | 2.89 | 0.04 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 72.33 | 65.00 | -7.33 | 21.10 | 19.27 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 68 | 55.82 | 64.18 | 8.36 | 19.70 | 14.82 | 19.14 | 0.00 | 15.41 |
| MEAN_REVERT | kept | 4 | 68.20 | 65.00 | -3.20 | 20.55 | 18.23 | 16.32 | 0.00 | 4.05 |
| MOVER_AVWAP_SCALP | filtered | 58 | 58.18 | 64.66 | 6.48 | 19.15 | 14.99 | 15.80 | 4.02 | 10.39 |
| MOVER_AVWAP_SCALP | kept | 319 | 79.74 | 65.00 | -14.74 | 20.46 | 16.96 | 15.80 | 4.13 | 3.67 |
| MOVER_TREND_PULLBACK | filtered | 432 | 59.38 | 64.92 | 5.54 | 20.40 | 18.30 | 15.80 | 3.64 | 13.01 |
| MOVER_TREND_PULLBACK | kept | 2121 | 75.39 | 65.00 | -10.39 | 19.89 | 18.52 | 15.80 | 4.23 | 1.50 |
| QUIET_COMPRESSION_BREAK | filtered | 117 | 57.12 | 65.00 | 7.88 | 20.90 | 19.50 | 20.00 | 0.00 | 12.14 |
| QUIET_COMPRESSION_BREAK | kept | 439 | 73.35 | 65.00 | -8.35 | 20.82 | 19.92 | 20.00 | 0.00 | -0.25 |
| SR_FLIP_RETEST | filtered | 118 | 55.23 | 64.59 | 9.36 | 20.06 | 20.00 | 15.64 | 1.90 | 16.43 |
| SR_FLIP_RETEST | kept | 52 | 68.53 | 65.00 | -3.53 | 22.46 | 20.00 | 15.33 | 1.65 | -1.77 |
| TREND_PULLBACK_EMA | kept | 25 | 81.04 | 65.00 | -16.04 | 19.85 | 19.72 | 18.78 | 4.18 | 0.28 |
| VOLUME_SURGE_BREAKOUT | filtered | 5 | 36.30 | 61.00 | 24.70 | 21.20 | 15.80 | 20.00 | 5.00 | 32.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 33 | 55.15 | 21.85 | 13.45 | 7.82 | 13.27 | 4.92 | 6.44 | -0.06 |
| DIVERGENCE_CONTINUATION | kept | 60 | 73.63 | 22.47 | 16.83 | 4.60 | 12.92 | 6.02 | 8.31 | 2.78 |
| FAILED_AUCTION_RECLAIM | filtered | 18 | 49.37 | 19.11 | 14.89 | 7.67 | 12.89 | 7.92 | 4.87 | 1.97 |
| FUNDING_EXTREME_SIGNAL | filtered | 15 | 43.63 | 19.67 | 12.67 | 6.40 | 12.93 | 8.50 | 4.79 | 3.33 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 74.55 | 25.00 | 8.00 | 10.50 | 9.00 | 8.75 | 6.80 | 6.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 45 | 57.92 | 24.07 | 14.18 | 6.27 | 12.69 | 5.09 | 7.45 | 2.29 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 61 | 66.87 | 23.72 | 14.20 | 3.84 | 10.34 | 5.43 | 6.54 | 2.89 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 72.33 | 19.67 | 14.00 | 6.00 | 16.00 | 6.67 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 68 | 55.82 | 15.82 | 16.29 | 13.94 | 12.96 | 5.00 | 7.22 | 0.00 |
| MEAN_REVERT | kept | 4 | 68.20 | 23.00 | 16.00 | 10.50 | 12.25 | 5.00 | 5.50 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 58 | 58.18 | 16.79 | 18.45 | 11.95 | 14.31 | 6.51 | 6.11 | 4.02 |
| MOVER_AVWAP_SCALP | kept | 319 | 79.74 | 19.83 | 18.01 | 12.96 | 13.97 | 7.16 | 7.56 | 4.13 |
| MOVER_TREND_PULLBACK | filtered | 432 | 59.38 | 17.18 | 18.00 | 7.71 | 12.53 | 6.07 | 8.24 | 3.64 |
| MOVER_TREND_PULLBACK | kept | 2121 | 75.39 | 19.34 | 18.00 | 7.87 | 12.84 | 6.71 | 8.04 | 4.23 |
| QUIET_COMPRESSION_BREAK | filtered | 117 | 57.12 | 17.62 | 16.94 | 11.46 | 14.10 | 6.45 | 5.52 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 439 | 73.35 | 18.44 | 17.95 | 11.02 | 14.16 | 5.63 | 7.10 | 0.00 |
| SR_FLIP_RETEST | filtered | 118 | 55.23 | 19.24 | 16.90 | 7.42 | 14.05 | 6.29 | 5.85 | 1.90 |
| SR_FLIP_RETEST | kept | 52 | 68.53 | 20.38 | 14.73 | 3.40 | 13.98 | 5.19 | 9.26 | 1.65 |
| TREND_PULLBACK_EMA | kept | 25 | 81.04 | 20.84 | 18.00 | 7.56 | 14.60 | 8.34 | 8.16 | 4.18 |
| VOLUME_SURGE_BREAKOUT | filtered | 5 | 36.30 | 25.00 | 18.00 | 12.00 | 14.00 | 5.00 | 4.30 | 5.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 33 | 55.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 60 | 73.63 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 18 | 49.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 15 | 43.63 | 0.00 | 0.00 | 6.56 | 0.00 | 1.44 | 0.00 | 0.00 | 0.00 | **8.00** |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 74.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 45 | 57.92 | 0.00 | 0.00 | 1.99 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.99** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 61 | 66.87 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.08** |
| MA_CROSS_TREND_SHIFT | kept | 3 | 72.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 68 | 55.82 | 0.00 | 0.00 | 0.00 | 0.00 | 15.81 | 0.00 | 0.00 | 0.00 | **15.81** |
| MEAN_REVERT | kept | 4 | 68.20 | 0.00 | 0.00 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | **4.80** |
| MOVER_AVWAP_SCALP | filtered | 58 | 58.18 | 0.00 | 0.00 | 3.43 | 0.00 | 1.12 | 0.69 | 0.00 | 0.60 | **5.84** |
| MOVER_AVWAP_SCALP | kept | 319 | 79.74 | 0.03 | 0.00 | 0.00 | 0.00 | 2.02 | 0.03 | 0.00 | 1.04 | **3.12** |
| MOVER_TREND_PULLBACK | filtered | 432 | 59.38 | 0.00 | 0.00 | 2.24 | 0.00 | 1.04 | 0.05 | 0.00 | 0.00 | **3.33** |
| MOVER_TREND_PULLBACK | kept | 2121 | 75.39 | 0.00 | 0.00 | 0.63 | 0.00 | 0.45 | 0.01 | 0.00 | 0.03 | **1.12** |
| QUIET_COMPRESSION_BREAK | filtered | 117 | 57.12 | 0.00 | 0.00 | 1.60 | 0.00 | 0.34 | 2.31 | 0.00 | 1.65 | **5.90** |
| QUIET_COMPRESSION_BREAK | kept | 439 | 73.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.45 | 0.00 | 0.00 | 0.16 | **0.61** |
| SR_FLIP_RETEST | filtered | 118 | 55.23 | 0.00 | 0.00 | 0.00 | 0.00 | 1.46 | 0.15 | 0.00 | 0.55 | **2.16** |
| SR_FLIP_RETEST | kept | 52 | 68.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 25 | 81.04 | 0.00 | 0.00 | 0.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.64** |
| VOLUME_SURGE_BREAKOUT | filtered | 5 | 36.30 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **12.00** |

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
- Outcomes recorded: **138173 held of 465367 seen** across 21 strategies; 3153 cells past the sample floor; **1556 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 42902 | 634/42268/0 | 42% | -0.21 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.22R) |
| MOVER_AVWAP_SCALP | 17968 | 194/17774/0 | 40% | -0.24 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 10784 | 119/10665/0 | 38% | -0.29 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 9523 | 64/9459/0 | 51% | -0.00 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.39R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING (-1.19R) |
| TREND_PULLBACK_EMA | 7842 | 34/7808/0 | 44% | -0.16 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OVERLAP/QUIET/COMPRESSED/BTC_FALLING (-1.29R) |
| SHADOW_MEAN_REVERT | 6835 | 0/0/6835 | 43% | -0.10 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.95R) |
| LIQUIDITY_SWEEP_REVERSAL | 6559 | 85/6474/0 | 35% | -0.50 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | LONDON/MARKUP/EXPANDED/BTC_NEUTRAL (-1.63R) |
| SHADOW_RANGE_FADE | 6114 | 0/0/6114 | 37% | -0.08 | ASIA/MARKDOWN/EXPANDED/BTC_FALLING (+0.53R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-1.37R) |
| QUIET_COMPRESSION_BREAK | 5787 | 325/5462/0 | 51% | -0.09 | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (+0.57R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5434 | 0/0/5434 | 34% | -0.40 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.06R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3741 | 4/3737/0 | 44% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 3255 | 39/3216/0 | 43% | -0.21 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| SR_FLIP_RETEST | 2728 | 13/2715/0 | 48% | -0.23 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.86R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| FUNDING_EXTREME_SIGNAL | 2693 | 2/2691/0 | 31% | -0.48 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 2601 | 0/2601/0 | 35% | -0.22 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| RANGE_FADE | 1249 | 4/1245/0 | 43% | -0.27 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1173 | 0/0/1173 | 54% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.09R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.36R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 316 | 0/316/0 | 36% | -0.47 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 90 | 12/78/0 | 44% | -0.10 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 12 | 0/12/0 | 50% | -0.00 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ LONDON/MARKUP/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.63R (n=43, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ LONDON/MARKUP/EXPANDED/BTC_NEUTRAL` -1.63R (n=43, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 189 | 26% / -0.59R | 189 | 52% / -0.15R | +0.44 | **ATR** |
| LIQUIDATION_REVERSAL | 17 | 35% / -0.40R | 17 | 59% / -0.18R | +0.22 | **ATR** |
| TREND_PULLBACK_EMA | 648 | 42% / -0.25R | 648 | 55% / -0.05R | +0.20 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1093 | 44% / -0.32R | 1093 | 55% / -0.14R | +0.17 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 131 | 35% / -0.22R | 131 | 45% / -0.09R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 1520 | 43% / -0.20R | 1520 | 49% / -0.07R | +0.13 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1045 | 40% / -0.25R | 1045 | 43% / -0.14R | +0.11 | **ATR** |
| MOVER_TREND_PULLBACK | 6799 | 48% / -0.13R | 6799 | 53% / -0.03R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 432 | 44% / -0.33R | 432 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 238 | 47% / -0.24R | 238 | 50% / -0.16R | +0.08 | **ATR** |
| MA_CROSS_TREND_SHIFT | 27 | 44% / -0.17R | 27 | 44% / -0.10R | +0.07 | **ATR** |
| RANGE_FADE | 58 | 34% / -0.35R | 58 | 40% / -0.28R | +0.06 | **ATR** |
| DIVERGENCE_CONTINUATION | 959 | 48% / -0.11R | 959 | 54% / -0.05R | +0.06 | **ATR** |
| QUIET_COMPRESSION_BREAK | 944 | 46% / -0.15R | 944 | 46% / -0.15R | -0.00 | **FIXED** |
| MEAN_REVERT | 236 | 51% / -0.08R | 236 | 50% / -0.08R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 43% / -0.33R | 7 | 43% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 9697 | 29% | -0.25R | 310 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1520 | 46% | -0.07R | 212 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 82 | 48% | -0.09R | 51 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 867 | 37% / -0.16R | +0.90 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1120 | 39% / -0.17R | +0.84 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 1975 | 34% / -0.12R | +0.73 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 8735 | 36% / -0.16R | +0.37 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1083 | 38% / -0.06R | +0.22 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 158 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 912 | 34% / -0.17R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 849 | 33% / -0.20R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 192 | 29% / -0.44R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 252 | 31% / -0.62R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 197 | 53% / +0.05R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 45 | 36% / -0.06R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 236 | 33% / -0.40R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 42 | 26% / -0.45R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 23 | 48% / +0.00R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 13 | 38% / +0.45R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **5** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×657]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 531/6) (sustained 531 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 14/6) (sustained 14 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.55R (bound 0.3) (streak 1274/6) (sustained 1274 cycles)
- **ALERT** `tuned_variants` — 820 non-stamps — atr_arm_uncomputable=820 (seen=18573 stamped=2021 skipped=15732) (streak 1269/6) (sustained 1269 cycles)
- **ALERT** `auto_dispatch` — 202 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=202) (streak 1263/3) (sustained 1263 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 56 fed / 0 quiet / 2 never delivered of 58 subscribed; 588143995 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 16 arms current, none stalled; covering 1400/1400 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +1 / upstream +3 | 0 |
| atr_trail_live_arms | ok | 32 arms current, none stalled; covering 1236/1236 signals (100%) | 0 |
| auto_dispatch | violating | 202 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=202) (streak 1263/3) | 1263 |
| binance_ip_weight | ok | peak 147/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 83000.00 | 0 |
| candle_coverage | ok | 86/86 symbols with ≥20 15m candles, 86/86 updated within 45m [fresh=86; 79 Tier-1 futures + 7 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 243 dup bars, 0 undedupable; ws 0 out-of-order, 1193 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 53 cohorts, 17 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +9 / upstream +21 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 2167/2185 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 3 promoted today, nothing refused | 0 |
| dark_resolution | ok | 133 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 2162/2180 signals (99%) | 0 |
| depth_feed | ok | 56/58 books fresh (stale 0, never 2, thin 0); 267739620 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.55R (bound 0.3) (streak 1274/6) | 1274 |
| emission_controller | ok | last cycle 413s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×657]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 531/6) | 531 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 14/6) | 14 |
| firestore_read_budget | ok | 1,365 reads/day of 50,000 [engine 1,326, signing 39]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 6720 sealed bars over 56 symbols; 1181 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +6 / upstream +94 | 0 |
| indicator_cache_key | ok | 546457 frozen value(s) avoided; 2863714 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.21R over n=3216 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +20 / upstream +94 | 0 |
| mover_admission_metadata | ok | 924 symbols known, 217 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 7 held, 7 with scan counts, 6 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 6 locked / 6 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3108 rows held, 2576761 evicted (sampled: execution:trigger_not_confirmed 400/937172, execution:overextended 400/824082, setup_compat:regime_STRONG_TREND 400/409077) | 0 |
| price_action_lane | ok | 3280498 evaluated, 3228 emitted; layer1 3228 stamped / 0 blind; cooldown=430937, delta_opposed=259217, no_footprint=1236900, no_opposing_target=1521, no_sweep=1106343, rr_below_floor=242352 | 0 |
| promoted_pair_integrity | ok | 7/7 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.27R over n=1245 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +54 / upstream +94 | 0 |
| sar_alignment_crosscheck | ok | 1513/50158 disagreed (3.0%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +94 | 0 |
| sar_hold_arm | ok | 1856 held arms settled, 144 unscored, 32 still walking (27 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 49/49 resolvable | 0 |
| sar_live_arms | ok | 32 arms current, none stalled; covering 1235/1235 signals (100%) | 0 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 3 resolved, 46 still mid-window | 0 |
| scan_cycle | ok | last 37.8s, worst 192.9s over 38770 lifetime cycles; lifetime 335 over 60s, 26 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 3.36s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 1542197 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 4m ago | 0 |
| snapshot_writer | ok | last cycle 23s ago (85.25s to run, worst 179.91s), 2266 overrun(s) of 26157 cycles, TTL 900s; slowest dark_promotion=12.92s, router_delivery=10.47s, exchange_positions=8.7s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=8, gate reads=0, withheld=8) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +88 / upstream +94 | 0 |
| structural_snap | ok | 6000/6000 measured, 20 blind, 0 levels moved (refusals: redetect_cooldown=2032) | 0 |
| structural_veto_lane | ok | 3886 stamped; 0 with no readable level book, 124 with clear air ahead, 3053 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +94 / upstream +21 | 0 |
| tuned_variants | violating | 820 non-stamps — atr_arm_uncomputable=820 (seen=18573 stamped=2021 skipped=15732) (streak 1269/6) | 1269 |
| unlock_shorts | ok | 14 open, 43 scheduled, calendar 3.0h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 129 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2364393`
- `Path funnel` emissions: `66`
- `Regime distribution` emissions: `66`
- `QUIET_SCALP_BLOCK` events: `132`
- `confidence_gate` events: `3997`
- `free_channel_post` events: `0`
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
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[absent=1, present=428887] state[empty=1, populated=428887] buckets[few=8, many=428836, none=1, some=43] sources[none] quality[none]
- funding_rate: presence[absent=18306, present=410582] state[empty=18306, populated=410582] buckets[few=410582, none=18306] sources[none] quality[none]
- liquidation_clusters: presence[absent=257821, present=171067] state[empty=257821, populated=171067] buckets[few=137385, none=257821, some=33682] sources[none] quality[none]
- oi_snapshot: presence[absent=18305, present=410583] state[empty=18305, populated=410583] buckets[few=550, many=406510, none=18305, some=3523] sources[none] quality[none]
- order_book: presence[absent=117807, present=311081] state[populated=311081, unavailable=117807] buckets[few=311081, none=117807] sources[book_ticker=311081, unavailable=117807] quality[none=117807, top_of_book_only=311081]
- orderblocks: presence[absent=428888] state[empty=428888] buckets[none=428888] sources[measured_dark=428888] quality[none]
- recent_ticks: presence[present=428888] state[populated=428888] buckets[many=428888] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.2248769998550415` sec
- Median create→first breach: `9786.438029050827` sec
- Median create→terminal: `9786.43810248375` sec
- Median first breach→terminal: `6.35385513305664e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.8900840277535682 | 1.0418997886360808 | 0.8542894791434309 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 1.5372855137609367 | 1.7373563375222356 | 0.8846299687899783 | 0 | 2 |
| MEAN_REVERT | 1 | 1 | 1.403454657618759 | 2.2421491730560215 | 0.6259416966917807 | 0 | 1 |
| MOVER_AVWAP_SCALP | 6 | 6 | 2.1111860056266205 | 1.815617737480956 | 0.8918962855687907 | 2 | 4 |
| MOVER_TREND_PULLBACK | 16 | 16 | 2.869097683726393 | 2.9806499999999962 | 1.069995457677015 | 9 | 7 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 1.2622726244213998 | 1.4165479043858769 | 0.8915457654710162 | 0 | 6 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.8901 | 25614.724618911743 | 25614.7246799469 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 0.8796 | 4167.297928929329 | 4171.709312081337 |
| MEAN_REVERT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 4376.108951091766 | 4376.10896897316 |
| MOVER_AVWAP_SCALP | 6 | 6 | 16.7 | 16.7 | 16.7 | 0.0 | -0.0094 | 18469.86566901207 | 18469.865709543228 |
| MOVER_TREND_PULLBACK | 16 | 16 | 25.0 | 56.2 | 25.0 | 0.0 | -0.5979 | 5518.53468644619 | 5518.534722447395 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 25.0 | 75.0 | 25.0 | 0.0 | -0.5666 | 14569.152576088905 | 14569.46367752552 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1120 | 8 | 485 | 0.0 | 0.0 | None | None | 635 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2254 | 10 | 2196 | 0.0 | 0.0 | None | None | 58 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `59`
- Gating Δ: `10258`
- No-generation Δ: `310571`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": 2.1506, "current_avg_pnl": -0.0094, "current_win_rate": 16.7, "previous_avg_pnl": -2.16, "previous_win_rate": 0.0, "win_rate_delta": 16.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.0066, "current_avg_pnl": -0.5979, "current_win_rate": 25.0, "previous_avg_pnl": 0.4087, "previous_win_rate": 42.9, "win_rate_delta": -17.9}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.9835, "current_avg_pnl": -0.5666, "current_win_rate": 25.0, "previous_avg_pnl": 0.4169, "previous_win_rate": 33.3, "win_rate_delta": -8.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 6, "geometry_changed_delta": 0, "geometry_preserved_delta": 565, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -649398.88, "median_terminal_delta_sec": -649399.59, "sl_rate_delta": 0.0, "win_rate_delta": -100.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": 5, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
