# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `10316` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 24 | 24 | 23 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 17387 | 17387 | 15311 | 34 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 113261 | 113297 | 10 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 98246 | 98259 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 97730 | 93020 | 5214 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 98306 | 94549 | 4072 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 104346 | 104312 | 76 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 92072 | 92091 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 98628 | 98673 | 6 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 98686 | 90676 | 13177 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 118343 | 123805 | 269 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 113315 | 105024 | 13261 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 100765 | 100777 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 98265 | 98297 | 6 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 97660 | 97364 | 360 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 94055 | 93979 | 3613 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 86562 | 81513 | 5482 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 86999 | 86392 | 696 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 113219 | 113229 | 33 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 92097 | 91892 | 301 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 13753 | 13753 | 11185 | 55 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 336 | 336 | 281 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 23355 | 23355 | 22438 | 46 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 9 | 9 | 8 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 36038 | 36038 | 35386 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 487 | 487 | 420 | 3 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 33304 | 33304 | 29542 | 68 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 40 | 40 | 39 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1886 | 1886 | 1539 | 6 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 12075 | 12075 | 3016 | 188 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2678 | 2678 | 2526 | 11 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 88 | 88 | 23 | 2 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 2868 | 2868 | 2470 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=113297): breakout_not_found=64108, basic_filters_failed=33386, move_not_fresh=9743, breakout_stale=4495, retest_proximity_failed=1165, volume_spike_missing=240, insufficient_candles=119, ema_alignment_reject=21, missing_fvg_or_orderblock=19, rsi_reject=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=98259): cls_disabled_merged_into_lsr=98259
- **EVAL::DIVERGENCE_CONTINUATION** (total=93020): cvd_divergence_failed=29090, basic_filters_failed=26847, h1_trend_not_aligned=26104, ema_alignment_reject=9354, retest_proximity_failed=1277, missing_fvg_or_orderblock=303, insufficient_candles=45
- **EVAL::FAILED_AUCTION_RECLAIM** (total=94549): auction_not_detected=36729, basic_filters_failed=26352, reclaim_hold_failed=14837, tail_too_small=13647, regime_blocked=2939, insufficient_candles=45
- **EVAL::FUNDING_EXTREME** (total=104312): funding_not_extreme=73567, basic_filters_failed=27661, missing_funding_rate=2066, ema_alignment_reject=576, rsi_reject=287, cvd_divergence_failed=64, momentum_reject=64, missing_fvg_or_orderblock=15, insufficient_candles=12
- **EVAL::LIQUIDATION_REVERSAL** (total=92091): cascade_threshold_not_met=63213, basic_filters_failed=27937, cvd_divergence_failed=431, rsi_reject=402, insufficient_candles=90, missing_fvg_or_orderblock=10, volume_spike_missing=8
- **EVAL::MA_CROSS_TREND_SHIFT** (total=98673): no_ma_cross=70971, basic_filters_failed=26903, ma_cross_cooldown=579, ma_cross_htf_misaligned=220
- **EVAL::MEAN_REVERT** (total=90676): no_extension=71486, basic_filters_failed=19190
- **EVAL::MOVER_AVWAP_SCALP** (total=123805): no_avwap_tag=46230, no_mover_leg=35735, basic_filters_failed=33613, no_avwap_reclaim=3058, avwap_reclaim_no_volume=2858, avwap_slope_against=2261, insufficient_candles=47, anchor_too_recent=3
- **EVAL::MOVER_TREND_PULLBACK** (total=105024): mover_run_too_small=49759, basic_filters_failed=33405, no_reclaim=15339, no_pullback_tag=5981, insufficient_candles=540
- **EVAL::OPENING_RANGE_BREAKOUT** (total=100777): feature_disabled=100777
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=98297): regime_blocked=68434, breakout_not_found=18966, basic_filters_failed=8132, adx_reject=2697, ema_alignment_reject=64, rsi_reject=4
- **EVAL::QUIET_COMPRESSION_BREAK** (total=97364): compression_not_detected=33705, regime_blocked=32662, basic_filters_failed=18203, breakout_not_detected=11888, volume_confirmation_failed=820, insufficient_candles=45, rsi_reject=40, missing_fvg_or_orderblock=1
- **EVAL::SR_FLIP_RETEST** (total=93979): basic_filters_failed=26232, flip_close_not_confirmed=15690, whipsaw_flip=13836, long_break_volume_thin=12819, long_disabled=7244, reclaim_hold_failed=6964, retest_out_of_zone=5559, regime_blocked=2924, wick_quality_failed=1349, long_acceptance_not_held=598, ema_alignment_reject=372, insufficient_candles=205, missing_fvg_or_orderblock=166, rsi_reject=21
- **EVAL::STANDARD** (total=81513): adx_reject=23501, momentum_reject=22646, basic_filters_failed=14575, macd_reject=7794, sweeps_not_detected=7206, ema_alignment_reject=4104, invalid_sl_geometry=1200, rsi_reject=309, insufficient_candles=162, mtf_reject=16
- **EVAL::TREND_PULLBACK** (total=86392): h1_trend_not_aligned=32611, basic_filters_failed=13095, ema_alignment_reject=11872, h1_pullback_not_confirmed=11201, no_ema_reclaim_close=5021, ema_not_tested_prev=4310, body_conviction_fail=3402, rsi_reject=2753, prev_already_below_emas=898, no_prev_low_break=348, prev_already_above_emas=289, momentum_flat=192, insufficient_candles=162, no_prev_high_break=161, missing_fvg_or_orderblock=27, ema21_not_tagged=27, momentum_reject=23
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=113229): breakout_not_found=61351, basic_filters_failed=33385, move_not_fresh=11404, breakout_stale=4698, retest_proximity_failed=1867, volume_spike_missing=311, insufficient_candles=119, ema_alignment_reject=48, move_exhausted=27, missing_fvg_or_orderblock=19
- **EVAL::WHALE_MOMENTUM** (total=91892): momentum_reject=61057, recent_ticks_insufficient=22625, basic_filters_failed=8207, insufficient_candles=3

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=47): setup_compat:regime_BREAKOUT_EXPANSION=25, setup_compat:regime_VOLATILE_UNSUITABLE=22
- **FAILED_AUCTION_RECLAIM** (total=159): execution:overextended=116, setup_compat:regime_VOLATILE_UNSUITABLE=26, setup_compat:regime_STRONG_TREND=17
- **FUNDING_EXTREME_SIGNAL** (total=35): execution:trigger_not_confirmed=35
- **LIQUIDITY_SWEEP_REVERSAL** (total=395): execution:trigger_not_confirmed=338, setup_compat:regime_STRONG_TREND=55, execution:overextended=2
- **MEAN_REVERT** (total=444): execution:overextended=444
- **MOVER_AVWAP_SCALP** (total=34): execution:overextended=34
- **MOVER_TREND_PULLBACK** (total=3355): execution:overextended=1759, execution:trigger_not_confirmed=1596
- **QUIET_COMPRESSION_BREAK** (total=36): execution:trigger_not_confirmed=36
- **TREND_PULLBACK_EMA** (total=315): setup_compat:regime_CLEAN_RANGE=289, setup_compat:regime_VOLATILE_UNSUITABLE=26

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 189754 | 36.1% |
| QUIET | 146138 | 27.8% |
| TRENDING_DOWN | 90970 | 17.3% |
| TRENDING_UP | 74040 | 14.1% |
| VOLATILE | 24585 | 4.7% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **450**
- Average confidence gap to threshold: **9.96** (samples=450) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: NBISUSDT=72, XLMUSDT=39, LINKUSDT=36, BZUSDT=32, SPYUSDT=24, ETHUSDT=22, XRPUSDT=21, NEARUSDT=20, AAVEUSDT=19, TRXUSDT=18

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 368 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 8 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 298 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 478 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 96 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 665 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 130 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 14 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 350 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 60 |
| MEAN_REVERT | filtered | min_confidence | 49 |
| MEAN_REVERT | kept | min_confidence_pass | 30 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 47 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 448 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2384 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 81 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 215 |
| SR_FLIP_RETEST | filtered | min_confidence | 1240 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 182 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2374 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 12 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 70 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 42 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |
| WHALE_MOMENTUM | filtered | min_confidence | 25 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 9 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 75.30 | 65.00 | -10.30 | 20.70 | 20.00 | 20.00 | 4.00 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 376 | 55.07 | 65.00 | 9.93 | 20.96 | 19.82 | 17.43 | 2.07 | 12.34 |
| DIVERGENCE_CONTINUATION | kept | 298 | 70.75 | 65.00 | -5.75 | 20.65 | 19.57 | 18.19 | 2.50 | 0.07 |
| FAILED_AUCTION_RECLAIM | filtered | 574 | 54.05 | 65.00 | 10.95 | 21.12 | 19.22 | 20.00 | 3.89 | 8.19 |
| FAILED_AUCTION_RECLAIM | kept | 665 | 70.39 | 65.00 | -5.39 | 20.22 | 19.53 | 20.00 | 4.14 | 0.32 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 144 | 60.44 | 65.00 | 4.56 | 20.52 | 19.86 | 18.17 | 2.88 | 9.20 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 350 | 69.36 | 65.00 | -4.36 | 20.97 | 19.82 | 17.30 | 2.79 | 0.34 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.00 | 65.00 | -1.00 | 21.20 | 16.90 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 109 | 57.02 | 65.00 | 7.98 | 20.35 | 14.14 | 20.00 | 0.00 | 10.36 |
| MEAN_REVERT | kept | 30 | 70.06 | 65.00 | -5.06 | 20.37 | 14.00 | 20.00 | 0.00 | 10.30 |
| MOVER_AVWAP_SCALP | kept | 47 | 76.99 | 65.00 | -11.99 | 18.80 | 17.80 | 15.80 | 4.00 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 448 | 57.67 | 65.00 | 7.33 | 20.01 | 17.83 | 15.80 | 4.16 | 19.57 |
| MOVER_TREND_PULLBACK | kept | 2384 | 76.92 | 65.00 | -11.92 | 19.70 | 18.11 | 15.80 | 4.53 | 1.27 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 85.70 | 65.00 | -20.70 | 20.50 | 20.00 | 20.00 | 4.50 | -3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 81 | 52.85 | 65.00 | 12.15 | 19.96 | 19.91 | 20.00 | 0.00 | 3.44 |
| QUIET_COMPRESSION_BREAK | kept | 215 | 78.50 | 65.00 | -13.50 | 20.84 | 19.98 | 20.00 | 0.00 | -0.43 |
| SR_FLIP_RETEST | filtered | 1422 | 57.11 | 65.00 | 7.89 | 20.24 | 19.84 | 15.75 | 1.53 | 11.66 |
| SR_FLIP_RETEST | kept | 2374 | 70.50 | 65.00 | -5.50 | 20.87 | 19.89 | 15.87 | 1.92 | 0.68 |
| TREND_PULLBACK_EMA | filtered | 12 | 59.80 | 65.00 | 5.20 | 20.37 | 17.86 | 17.03 | 5.12 | 16.07 |
| TREND_PULLBACK_EMA | kept | 70 | 77.13 | 65.00 | -12.13 | 20.42 | 19.82 | 18.45 | 5.58 | 1.64 |
| VOLUME_SURGE_BREAKOUT | filtered | 42 | 44.05 | 65.00 | 20.95 | 20.31 | 17.66 | 20.00 | 3.54 | 14.62 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 81.40 | 65.00 | -16.40 | 22.00 | 17.40 | 20.00 | 6.00 | 8.60 |
| WHALE_MOMENTUM | filtered | 34 | 57.85 | 65.00 | 7.15 | 20.53 | 19.97 | 17.00 | 0.00 | 10.88 |
| WHALE_MOMENTUM | kept | 1 | 66.00 | 65.00 | -1.00 | 20.50 | 19.40 | 17.00 | 0.00 | 7.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 75.30 | 17.00 | 14.00 | 15.00 | 14.00 | 5.00 | 9.30 | 4.00 |
| DIVERGENCE_CONTINUATION | filtered | 376 | 55.07 | 19.98 | 14.12 | 4.88 | 12.19 | 6.24 | 8.32 | 2.07 |
| DIVERGENCE_CONTINUATION | kept | 298 | 70.75 | 21.32 | 15.82 | 5.26 | 12.30 | 5.63 | 9.03 | 2.50 |
| FAILED_AUCTION_RECLAIM | filtered | 574 | 54.05 | 20.85 | 16.40 | 5.41 | 11.40 | 5.85 | 5.91 | 3.89 |
| FAILED_AUCTION_RECLAIM | kept | 665 | 70.39 | 21.24 | 15.22 | 5.50 | 11.76 | 5.90 | 7.26 | 4.14 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 144 | 60.44 | 23.17 | 14.17 | 4.27 | 12.45 | 5.18 | 7.55 | 2.88 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 350 | 69.36 | 23.22 | 14.25 | 4.94 | 11.72 | 5.45 | 7.32 | 2.79 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.00 | 25.00 | 14.00 | 3.00 | 11.00 | 5.00 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 109 | 57.02 | 20.78 | 18.00 | 5.81 | 13.68 | 5.92 | 5.01 | 0.00 |
| MEAN_REVERT | kept | 30 | 70.06 | 24.20 | 18.00 | 11.40 | 13.63 | 7.80 | 5.35 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 47 | 76.99 | 17.72 | 18.00 | 8.30 | 13.96 | 5.09 | 9.92 | 4.00 |
| MOVER_TREND_PULLBACK | filtered | 448 | 57.67 | 18.50 | 18.00 | 7.90 | 13.92 | 5.97 | 8.80 | 4.16 |
| MOVER_TREND_PULLBACK | kept | 2384 | 76.92 | 19.43 | 18.00 | 8.15 | 13.59 | 5.71 | 8.82 | 4.53 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 85.70 | 17.00 | 18.00 | 15.00 | 14.00 | 8.50 | 8.70 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 81 | 52.85 | 17.89 | 18.00 | 11.44 | 14.15 | 5.93 | 2.84 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 215 | 78.50 | 17.41 | 18.00 | 12.20 | 14.63 | 6.94 | 9.70 | 0.00 |
| SR_FLIP_RETEST | filtered | 1422 | 57.11 | 18.83 | 16.72 | 4.85 | 12.48 | 5.96 | 8.40 | 1.53 |
| SR_FLIP_RETEST | kept | 2374 | 70.50 | 20.66 | 15.60 | 6.29 | 13.52 | 5.79 | 8.70 | 1.92 |
| TREND_PULLBACK_EMA | filtered | 12 | 59.80 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 9.25 | 5.12 |
| TREND_PULLBACK_EMA | kept | 70 | 77.13 | 17.46 | 18.00 | 7.95 | 14.04 | 6.37 | 9.87 | 5.58 |
| VOLUME_SURGE_BREAKOUT | filtered | 42 | 44.05 | 17.19 | 18.00 | 13.43 | 14.00 | 5.00 | 2.51 | 3.54 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 81.40 | 25.00 | 19.00 | 13.50 | 11.00 | 7.00 | 8.50 | 6.00 |
| WHALE_MOMENTUM | filtered | 34 | 57.85 | 23.12 | 14.18 | 9.18 | 13.56 | 5.93 | 2.78 | 0.00 |
| WHALE_MOMENTUM | kept | 1 | 66.00 | 25.00 | 18.00 | 15.00 | 8.00 | 5.00 | 2.00 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 75.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 376 | 55.07 | 0.00 | 0.00 | 0.49 | 0.00 | 0.19 | 0.00 | 0.00 | 0.00 | **0.68** |
| DIVERGENCE_CONTINUATION | kept | 298 | 70.75 | 0.00 | 0.00 | 0.72 | 0.00 | 0.02 | 0.07 | 0.00 | 0.00 | **0.81** |
| FAILED_AUCTION_RECLAIM | filtered | 574 | 54.05 | 0.00 | 0.00 | 1.08 | 0.00 | 1.10 | 0.00 | 0.00 | 0.00 | **2.18** |
| FAILED_AUCTION_RECLAIM | kept | 665 | 70.39 | 0.00 | 0.00 | 0.01 | 0.00 | 0.12 | 0.06 | 0.00 | 0.00 | **0.19** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 144 | 60.44 | 0.00 | 0.00 | 1.56 | 0.00 | 1.35 | 0.00 | 0.00 | 0.00 | **2.91** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 350 | 69.36 | 0.00 | 0.00 | 0.05 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | **0.08** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 109 | 57.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | **0.06** |
| MEAN_REVERT | kept | 30 | 70.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 47 | 76.99 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 448 | 57.67 | 0.00 | 0.00 | 0.48 | 0.00 | 0.42 | 0.00 | 0.00 | 0.00 | **0.90** |
| MOVER_TREND_PULLBACK | kept | 2384 | 76.92 | 0.00 | 0.00 | 0.37 | 0.00 | 0.91 | 0.00 | 0.00 | 0.00 | **1.28** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 85.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 81 | 52.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.07 | **3.07** |
| QUIET_COMPRESSION_BREAK | kept | 215 | 78.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.02 | 0.00 | 0.00 | 0.05 | **0.07** |
| SR_FLIP_RETEST | filtered | 1422 | 57.11 | 0.32 | 0.00 | 0.90 | 0.00 | 1.25 | 0.02 | 0.00 | 0.24 | **2.73** |
| SR_FLIP_RETEST | kept | 2374 | 70.50 | 0.00 | 0.00 | 0.07 | 0.00 | 0.06 | 0.01 | 0.00 | 0.00 | **0.14** |
| TREND_PULLBACK_EMA | filtered | 12 | 59.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 70 | 77.13 | 0.00 | 0.00 | 1.17 | 0.00 | 0.41 | 0.00 | 0.00 | 0.00 | **1.58** |
| VOLUME_SURGE_BREAKOUT | filtered | 42 | 44.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.71 | **1.71** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 81.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 34 | 57.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | kept | 1 | 66.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=1016 (24.1%) | WOULD_LOSE=1827 | WOULD_EXPIRE=1366 | pending (awaiting window)=791

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| data_stale | 1 | 0.0% | 0.0 | 0.0 | +0.00 | **INSUFFICIENT_SAMPLE** |
| dispatch_cooldown | 83 | 20.5% | 8.0 | 9.0 | -0.01 | **TUNE** |
| dispatch_staleness | 494 | 84.0% | 41.0 | 232.0 | -0.39 | **DROP** |
| level_still_in_play | 1058 | 17.9% | 160.0 | 103.4 | +0.05 | **TUNE** |
| min_confidence | 1540 | 15.3% | 961.0 | 383.5 | +0.38 | **KEEP** |
| quiet_scalp_block | 303 | 15.2% | 80.0 | 73.4 | +0.02 | **TUNE** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 8 | 50.0% | 1.0 | 2.7 | -0.21 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 73 | 19.2% | 59.0 | 10.5 | +0.66 | **KEEP** |
| shadow_unit:SHADOW_MEAN_REVERT | 348 | 9.2% | 296.0 | 53.8 | +0.70 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 301 | 21.3% | 221.0 | 120.2 | +0.33 | **KEEP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 21675 across 19 strategies; 493 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 5458 | 16/5442/0 | 53% | +0.03 | LONDON/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (+1.24R) | OVERLAP/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.00R) |
| SR_FLIP_RETEST | 4182 | 0/4182/0 | 44% | -0.09 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.29R) | LONDON/MARKDOWN/EXPANDED/BTC_FALLING (-1.00R) |
| FAILED_AUCTION_RECLAIM | 3152 | 7/3145/0 | 46% | -0.00 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.00R) |
| DIVERGENCE_CONTINUATION | 2139 | 4/2135/0 | 41% | -0.06 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (+1.22R) | NY/MARKDOWN/EXPANDED/BTC_RISING (-1.00R) |
| SHADOW_MEAN_REVERT | 1824 | 0/0/1824 | 34% | -0.10 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.91R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| SHADOW_RANGE_FADE | 1444 | 0/0/1444 | 34% | +0.04 | ASIA/QUIET/NORMAL/BTC_NEUTRAL (+1.29R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| SHADOW_FUNDING_FADE | 789 | 0/0/789 | 32% | -0.44 | NY/MARKUP/NORMAL/BTC_NEUTRAL (-0.15R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING (-1.00R) |
| LIQUIDITY_SWEEP_REVERSAL | 776 | 1/775/0 | 42% | +0.01 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| QUIET_COMPRESSION_BREAK | 760 | 0/760/0 | 46% | -0.02 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (+2.21R) | NY/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| TREND_PULLBACK_EMA | 294 | 0/294/0 | 31% | -0.26 | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.21R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 195 | 1/194/0 | 38% | -0.11 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| MOVER_AVWAP_SCALP | 164 | 5/159/0 | 19% | -0.62 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 119 | 0/0/119 | 40% | -0.19 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| FUNDING_EXTREME_SIGNAL | 105 | 0/105/0 | 45% | +0.23 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| WHALE_MOMENTUM | 104 | 0/104/0 | 13% | -0.39 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| MEAN_REVERT | 102 | 0/102/0 | 5% | -0.93 | NY/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) | NY/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) |
| BREAKDOWN_SHORT | 59 | 1/58/0 | 63% | +0.25 | ASIA/MARKDOWN/NORMAL/BTC_FALLING (+0.53R) | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.34R) |
| POST_DISPLACEMENT_CONTINUATION | 7 | 0/7/0 | 0% | -1.00 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 1/1/0 | 50% | +0.35 | — | — |

- **Strongest cells**: `QUIET_COMPRESSION_BREAK @ OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL` +2.21R (n=29, STRONG); `FAILED_AUCTION_RECLAIM @ LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL` +1.70R (n=45, STRONG); `FAILED_AUCTION_RECLAIM @ LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL` +1.65R (n=50, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL` -1.00R (n=33, NEGATIVE); `MEAN_REVERT @ NY/RANGE/NORMAL/BTC_NEUTRAL` -1.00R (n=44, NEGATIVE); `DIVERGENCE_CONTINUATION @ OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL` -1.00R (n=21, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| MOVER_AVWAP_SCALP | 18 | 39% / -0.11R | 18 | 50% / +0.02R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 564 | 45% / -0.06R | 564 | 48% / +0.01R | +0.07 | **ATR** |
| MOVER_TREND_PULLBACK | 395 | 58% / +0.06R | 395 | 63% / +0.10R | +0.04 | **ATR** |
| FAILED_AUCTION_RECLAIM | 416 | 48% / -0.03R | 416 | 47% / +0.02R | +0.04 | **ATR** |
| QUIET_COMPRESSION_BREAK | 203 | 46% / +0.04R | 203 | 45% / +0.03R | -0.01 | **FIXED** |
| LIQUIDITY_SWEEP_REVERSAL | 70 | 50% / +0.03R | 70 | 51% / +0.03R | -0.00 | **FIXED** |
| DIVERGENCE_CONTINUATION | 109 | 49% / -0.07R | 109 | 54% / -0.07R | -0.00 | **FIXED** |
| MEAN_REVERT | 16 | 12% / -0.80R | 16 | 12% / -0.80R | -0.00 | **FIXED** |
| WHALE_MOMENTUM | 13 | 15% / -0.34R | 13 | 15% / -0.42R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 10 | 50% / +0.26R | 10 | 40% / -0.07R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 10 | 70% / +0.13R | 10 | 70% / +0.17R | — | **MEASURING** |
| BREAKDOWN_SHORT | 3 | 33% / +0.01R | 3 | 33% / +0.02R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 1 | 0% / -1.00R | 1 | 100% / +0.37R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -0.64R | 1 | 0% / -1.00R | — | **MEASURING** |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 10 · alerting: **1** · boot grace active: False
- **ALERT** `mean_revert_emission` — 2557 detections since last emission (emitted_total=0) — check gate rejections (streak 9/6) (sustained 9 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| btc_reference | ok | BTC ref 63917.10 | 0 |
| candle_coverage | ok | 85/86 symbols with ≥20 15m candles | 0 |
| geometry_ab | ok | output +6 / upstream +44 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 2557 detections since last emission (emitted_total=0) — check gate rejections (streak 9/6) | 9 |
| mean_revert_path | ok | output +193 / upstream +44 | 0 |
| shadow_units | ok | last shadow stamp 13m ago | 0 |
| strategy_edge | ok | output +42 / upstream +44 | 0 |
| suppression_audit | ok | output +44 / upstream +47 | 0 |
| tuned_variants | ok | seen=0 stamped=0 skipped=0 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2628242`
- `Path funnel` emissions: `61`
- `Regime distribution` emissions: `61`
- `QUIET_SCALP_BLOCK` events: `450`
- `confidence_gate` events: `9681`
- `free_channel_post` events: `19`
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
- Total posts in window: **19**

| Source | Count |
|---|---:|
| signal_close | 14 |
| regime_shift | 4 |
| signal_highlight | 1 |

- By severity: HIGH=19

## Dependency readiness
- cvd: presence[present=406956] state[populated=406956] buckets[few=6, many=406883, some=67] sources[none] quality[none]
- funding_rate: presence[absent=53442, present=353514] state[empty=53442, populated=353514] buckets[few=353514, none=53442] sources[none] quality[none]
- liquidation_clusters: presence[absent=251643, present=155313] state[empty=251643, populated=155313] buckets[few=128254, none=251643, some=27059] sources[none] quality[none]
- oi_snapshot: presence[absent=49879, present=357077] state[empty=49879, populated=357077] buckets[few=126, many=356158, none=49879, some=793] sources[none] quality[none]
- order_book: presence[absent=125359, present=281597] state[populated=281597, unavailable=125359] buckets[few=281597, none=125359] sources[book_ticker=281597, unavailable=125359] quality[none=125359, top_of_book_only=281597]
- orderblocks: presence[absent=406956] state[empty=406956] buckets[none=406956] sources[not_implemented=406956] quality[none]
- recent_ticks: presence[absent=1682, present=405274] state[empty=1682, populated=405274] buckets[many=405274, none=1682] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.730968475341797` sec
- Median create→first breach: `2444.4586594104767` sec
- Median create→terminal: `2445.368628382683` sec
- Median first breach→terminal: `1.9874119758605957` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | 0.9492 | 3244.7972403764725 | 3247.3892899751663 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 0.8944 | 3073.9224898815155 | 3074.8840827941895 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.7816 | 650.8377330303192 | 652.9379251003265 |
| MOVER_TREND_PULLBACK | 9 | 9 | 0.0 | 66.7 | 0.0 | 0.0 | 0.006 | 2452.822571992874 | 2454.0292699337006 |
| SR_FLIP_RETEST | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.1378 | 393.2741780281067 | 394.66467809677124 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 12075 | 188 | 3016 | 0.0 | 100.0 | 393.2741780281067 | 394.66467809677124 | 9059 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2678 | 11 | 2526 | 0.0 | 0.0 | None | None | 152 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `15`
- Gating Δ: `-49244`
- No-generation Δ: `-456914`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.2824, "current_avg_pnl": 0.8944, "current_win_rate": 100.0, "previous_avg_pnl": 0.612, "previous_win_rate": 33.3, "win_rate_delta": 66.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 4.1508, "current_avg_pnl": 0.006, "current_win_rate": 0.0, "previous_avg_pnl": -4.1448, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 34, "geometry_changed_delta": 0, "geometry_preserved_delta": -5706, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 393.27, "median_terminal_delta_sec": 394.66, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 5, "geometry_changed_delta": 0, "geometry_preserved_delta": -29, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
