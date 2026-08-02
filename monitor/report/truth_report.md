# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `12` sec (warning=False)
- Latest performance record age: `2888` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 28 | 28 | 23 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 20311 | 20311 | 17570 | 18 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 122797 | 122812 | 11 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 115396 | 115406 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 114972 | 109282 | 6108 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 115433 | 110277 | 5406 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 119129 | 118932 | 232 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 106253 | 106271 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 115692 | 115737 | 8 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 115750 | 111373 | 5918 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 127036 | 131400 | 872 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 122828 | 115401 | 11595 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 114390 | 114398 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 115415 | 115406 | 24 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 114902 | 114272 | 695 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 117295 | 115487 | 2302 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 110134 | 106846 | 8004 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 101536 | 95289 | 6682 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 101978 | 101414 | 641 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 122764 | 122777 | 15 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 106277 | 106281 | 12 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 17217 | 17217 | 12811 | 57 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 649 | 649 | 94 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 29742 | 29742 | 28616 | 37 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 13 | 13 | 4 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 13937 | 13937 | 9547 | 27 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1783 | 1783 | 274 | 46 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 30267 | 30267 | 16323 | 309 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 47 | 47 | 47 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 3072 | 3072 | 1098 | 40 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 4856 | 4856 | 4217 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 23220 | 23220 | 11319 | 120 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2821 | 2821 | 2367 | 27 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 103 | 103 | 31 | 5 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 199 | 199 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=122812): breakout_not_found=63672, basic_filters_failed=37142, move_not_fresh=15114, breakout_stale=5270, retest_proximity_failed=1342, volume_spike_missing=237, move_exhausted=29, ema_alignment_reject=3, missing_fvg_or_orderblock=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=115406): cls_disabled_merged_into_lsr=115406
- **EVAL::DIVERGENCE_CONTINUATION** (total=109282): cvd_divergence_failed=40918, basic_filters_failed=31175, h1_trend_not_aligned=23808, ema_alignment_reject=10867, retest_proximity_failed=1758, missing_fvg_or_orderblock=747, cvd_insufficient=9
- **EVAL::FAILED_AUCTION_RECLAIM** (total=110277): auction_not_detected=40475, basic_filters_failed=30221, reclaim_hold_failed=22108, tail_too_small=13817, regime_blocked=3655, rsi_reject=1
- **EVAL::FUNDING_EXTREME** (total=118932): funding_not_extreme=76807, basic_filters_failed=32555, missing_funding_rate=5455, ema_alignment_reject=2552, rsi_reject=1000, momentum_reject=338, cvd_divergence_failed=199, missing_fvg_or_orderblock=26
- **EVAL::LIQUIDATION_REVERSAL** (total=106271): cascade_threshold_not_met=70880, basic_filters_failed=34132, cvd_divergence_failed=802, rsi_reject=434, missing_fvg_or_orderblock=12, volume_spike_missing=11
- **EVAL::MA_CROSS_TREND_SHIFT** (total=115737): no_ma_cross=83138, basic_filters_failed=31202, ma_cross_cooldown=811, ma_cross_htf_misaligned=586
- **EVAL::MEAN_REVERT** (total=111373): no_extension=93397, basic_filters_failed=17976
- **EVAL::MOVER_AVWAP_SCALP** (total=131400): no_mover_leg=46067, no_avwap_tag=37478, basic_filters_failed=36799, avwap_slope_against=6733, no_avwap_reclaim=1808, avwap_reclaim_no_volume=1805, insufficient_candles=706, anchor_too_recent=4
- **EVAL::MOVER_TREND_PULLBACK** (total=115401): mover_run_too_small=60366, basic_filters_failed=36416, no_reclaim=14623, no_pullback_tag=2870, insufficient_candles=1126
- **EVAL::OPENING_RANGE_BREAKOUT** (total=114398): feature_disabled=114398
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=115406): regime_blocked=88399, breakout_not_found=18422, basic_filters_failed=5446, adx_reject=3102, ema_alignment_reject=32, rsi_reject=5
- **EVAL::QUIET_COMPRESSION_BREAK** (total=114272): compression_not_detected=40254, regime_blocked=30589, basic_filters_failed=24756, breakout_not_detected=16391, volume_confirmation_failed=1971, rsi_reject=292, missing_fvg_or_orderblock=19
- **EVAL::RANGE_FADE** (total=115487): no_range_edge=97509, basic_filters_failed=17978
- **EVAL::SR_FLIP_RETEST** (total=106846): basic_filters_failed=30189, flip_close_not_confirmed=16799, long_break_volume_thin=15461, whipsaw_flip=13918, reclaim_hold_failed=12132, retest_out_of_zone=10648, regime_blocked=3649, wick_quality_failed=2442, long_acceptance_not_held=608, ema_alignment_reject=446, missing_fvg_or_orderblock=445, rsi_reject=109
- **EVAL::STANDARD** (total=95289): momentum_reject=33721, adx_reject=22146, basic_filters_failed=14040, sweeps_not_detected=11805, macd_reject=9639, ema_alignment_reject=3716, invalid_sl_geometry=130, rsi_reject=88, mtf_reject=4
- **EVAL::TREND_PULLBACK** (total=101414): h1_trend_not_aligned=29055, ema_alignment_reject=16014, basic_filters_failed=15750, h1_pullback_not_confirmed=14402, no_ema_reclaim_close=7949, ema_not_tested_prev=6946, body_conviction_fail=4697, rsi_reject=3741, prev_already_below_emas=886, no_prev_low_break=598, prev_already_above_emas=456, no_prev_high_break=450, momentum_flat=262, ema21_not_tagged=95, missing_fvg_or_orderblock=80, momentum_reject=33
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=122777): breakout_not_found=64866, basic_filters_failed=37138, move_not_fresh=13707, breakout_stale=4791, retest_proximity_failed=1747, volume_spike_missing=372, missing_fvg_or_orderblock=87, move_exhausted=55, ema_alignment_reject=14
- **EVAL::WHALE_MOMENTUM** (total=106281): momentum_reject=74842, recent_ticks_insufficient=23686, basic_filters_failed=7753

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=447): setup_compat:regime_VOLATILE_UNSUITABLE=422, setup_compat:regime_BREAKOUT_EXPANSION=25
- **FAILED_AUCTION_RECLAIM** (total=4766): execution:overextended=2293, setup_compat:regime_STRONG_TREND=1306, context_floor=1108, setup_compat:regime_VOLATILE_UNSUITABLE=59
- **FUNDING_EXTREME_SIGNAL** (total=545): execution:trigger_not_confirmed=538, context_floor=7
- **LIQUIDITY_SWEEP_REVERSAL** (total=7648): execution:trigger_not_confirmed=4396, execution:overextended=2137, setup_compat:regime_STRONG_TREND=1115
- **MA_CROSS_TREND_SHIFT** (total=9): setup_compat:regime_DIRTY_RANGE=4, setup_compat:regime_CLEAN_RANGE=2, execution:trigger_not_confirmed=2, execution:overextended=1
- **MEAN_REVERT** (total=5326): setup_compat:regime_STRONG_TREND=2535, setup_compat:regime_WEAK_TREND=1562, execution:overextended=1229
- **MOVER_AVWAP_SCALP** (total=1112): execution:overextended=671, execution:trigger_not_confirmed=441
- **MOVER_TREND_PULLBACK** (total=14707): execution:overextended=7837, execution:trigger_not_confirmed=6870
- **QUIET_COMPRESSION_BREAK** (total=996): context_floor=927, execution:trigger_not_confirmed=69
- **RANGE_FADE** (total=2509): setup_compat:regime_STRONG_TREND=993, execution:overextended=527, setup_compat:regime_WEAK_TREND=517, setup_compat:regime_VOLATILE_UNSUITABLE=435, context_edge=23, setup_compat:regime_BREAKOUT_EXPANSION=14
- **TREND_PULLBACK_EMA** (total=2594): setup_compat:regime_CLEAN_RANGE=2122, setup_compat:regime_DIRTY_RANGE=359, setup_compat:regime_VOLATILE_UNSUITABLE=113
- **VOLUME_SURGE_BREAKOUT** (total=42): context_floor=34, execution:overextended=8
- **WHALE_MOMENTUM** (total=199): execution:trigger_not_confirmed=199

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 260772 | 40.1% |
| QUIET | 186531 | 28.7% |
| TRENDING_UP | 94155 | 14.5% |
| TRENDING_DOWN | 78035 | 12.0% |
| VOLATILE | 31488 | 4.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **467**
- Average confidence gap to threshold: **10.77** (samples=467) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: LINKUSDT=60, XRPUSDT=40, BTCUSDT=27, ETHUSDT=25, AVAXUSDT=23, BCHUSDT=22, 1000PEPEUSDT=22, SOLUSDT=20, NEARUSDT=18, TAOUSDT=16

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 5 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 282 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 4 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 523 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 106 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 88 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 436 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 49 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 54 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 12 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 533 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | filtered | min_confidence | 19 |
| MEAN_REVERT | kept | min_confidence_pass | 261 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 293 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 9 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 641 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 892 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 21 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 8498 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 132 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 19 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 730 |
| SR_FLIP_RETEST | filtered | min_confidence | 734 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 182 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2386 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 24 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 10 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 286 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 17 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 22 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 5 | 66.64 | 65.00 | -1.64 | 18.88 | 17.12 | 20.00 | 3.20 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 286 | 58.95 | 64.32 | 5.37 | 20.60 | 19.55 | 18.23 | 2.53 | 8.43 |
| DIVERGENCE_CONTINUATION | kept | 523 | 71.00 | 65.00 | -6.00 | 19.37 | 19.89 | 17.50 | 2.40 | -0.61 |
| FAILED_AUCTION_RECLAIM | filtered | 194 | 56.69 | 64.51 | 7.82 | 20.89 | 18.47 | 20.00 | 3.28 | 8.44 |
| FAILED_AUCTION_RECLAIM | kept | 436 | 71.52 | 65.00 | -6.52 | 20.43 | 19.33 | 20.00 | 3.80 | 0.41 |
| FUNDING_EXTREME_SIGNAL | filtered | 49 | 47.56 | 65.00 | 17.44 | 20.24 | 17.59 | 16.43 | 1.37 | 4.69 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 66 | 57.96 | 65.00 | 7.04 | 18.45 | 19.85 | 17.42 | 1.58 | 9.27 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 533 | 70.51 | 65.00 | -5.51 | 20.43 | 19.56 | 18.34 | 2.31 | -0.23 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.65 | 65.00 | -5.65 | 21.00 | 20.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 19 | 54.25 | 60.53 | 6.28 | 20.88 | 14.00 | 15.82 | 0.00 | 20.00 |
| MEAN_REVERT | kept | 261 | 70.22 | 65.00 | -5.22 | 20.28 | 16.98 | 18.33 | 0.00 | 0.43 |
| MOVER_AVWAP_SCALP | filtered | 302 | 56.05 | 63.36 | 7.31 | 20.72 | 15.29 | 15.80 | 3.24 | 8.17 |
| MOVER_AVWAP_SCALP | kept | 641 | 76.34 | 65.00 | -11.34 | 20.12 | 16.01 | 15.80 | 4.15 | 2.05 |
| MOVER_TREND_PULLBACK | filtered | 913 | 56.81 | 63.80 | 6.99 | 19.11 | 18.22 | 15.80 | 3.98 | 15.53 |
| MOVER_TREND_PULLBACK | kept | 8498 | 76.80 | 65.00 | -11.80 | 19.89 | 18.70 | 15.80 | 4.45 | 1.22 |
| QUIET_COMPRESSION_BREAK | filtered | 151 | 49.88 | 64.55 | 14.67 | 20.72 | 19.76 | 20.00 | 0.00 | 10.12 |
| QUIET_COMPRESSION_BREAK | kept | 730 | 75.27 | 65.00 | -10.27 | 20.71 | 19.70 | 20.00 | 0.00 | -0.97 |
| SR_FLIP_RETEST | filtered | 916 | 57.92 | 64.55 | 6.63 | 20.34 | 19.91 | 16.03 | 1.39 | 10.66 |
| SR_FLIP_RETEST | kept | 2386 | 70.64 | 65.00 | -5.64 | 20.38 | 19.92 | 16.11 | 1.88 | 0.28 |
| TREND_PULLBACK_EMA | filtered | 34 | 57.18 | 65.00 | 7.82 | 19.58 | 19.39 | 16.76 | 5.41 | 13.24 |
| TREND_PULLBACK_EMA | kept | 286 | 77.21 | 65.00 | -12.21 | 20.99 | 19.70 | 18.31 | 5.04 | 2.28 |
| VOLUME_SURGE_BREAKOUT | filtered | 17 | 56.59 | 60.59 | 4.00 | 20.23 | 17.51 | 20.00 | 3.62 | 4.76 |
| VOLUME_SURGE_BREAKOUT | kept | 22 | 70.25 | 65.00 | -5.25 | 20.60 | 18.01 | 20.00 | 4.23 | 6.26 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 5 | 66.64 | 17.00 | 14.00 | 14.40 | 11.00 | 5.00 | 5.04 | 3.20 |
| DIVERGENCE_CONTINUATION | filtered | 286 | 58.95 | 24.41 | 9.40 | 6.03 | 11.96 | 5.50 | 8.75 | 2.53 |
| DIVERGENCE_CONTINUATION | kept | 523 | 71.00 | 23.35 | 14.14 | 5.64 | 12.39 | 5.39 | 8.97 | 2.40 |
| FAILED_AUCTION_RECLAIM | filtered | 194 | 56.69 | 20.92 | 15.11 | 9.43 | 12.10 | 5.88 | 6.06 | 3.28 |
| FAILED_AUCTION_RECLAIM | kept | 436 | 71.52 | 23.54 | 15.01 | 4.32 | 13.14 | 5.86 | 6.55 | 3.80 |
| FUNDING_EXTREME_SIGNAL | filtered | 49 | 47.56 | 24.84 | 8.00 | 6.06 | 15.98 | 8.27 | 2.75 | 1.37 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 66 | 57.96 | 23.79 | 16.06 | 3.91 | 11.23 | 3.99 | 6.68 | 1.58 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 533 | 70.51 | 23.29 | 14.02 | 5.19 | 13.30 | 6.53 | 5.89 | 2.31 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.65 | 25.00 | 14.00 | 7.50 | 12.00 | 5.00 | 7.15 | 0.00 |
| MEAN_REVERT | filtered | 19 | 54.25 | 20.79 | 18.00 | 7.42 | 12.00 | 10.00 | 6.04 | 0.00 |
| MEAN_REVERT | kept | 261 | 70.22 | 23.93 | 16.82 | 6.32 | 12.00 | 6.27 | 5.31 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 302 | 56.05 | 18.74 | 18.06 | 7.69 | 12.58 | 5.54 | 5.18 | 3.24 |
| MOVER_AVWAP_SCALP | kept | 641 | 76.34 | 20.42 | 18.06 | 8.41 | 13.46 | 6.17 | 7.80 | 4.15 |
| MOVER_TREND_PULLBACK | filtered | 913 | 56.81 | 18.01 | 18.16 | 7.92 | 13.02 | 5.42 | 8.11 | 3.98 |
| MOVER_TREND_PULLBACK | kept | 8498 | 76.80 | 18.93 | 18.05 | 8.13 | 13.48 | 5.90 | 9.16 | 4.45 |
| QUIET_COMPRESSION_BREAK | filtered | 151 | 49.88 | 18.43 | 17.50 | 11.13 | 14.14 | 6.76 | 4.59 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 730 | 75.27 | 18.28 | 17.60 | 11.63 | 14.16 | 5.80 | 8.07 | 0.00 |
| SR_FLIP_RETEST | filtered | 916 | 57.92 | 17.84 | 16.01 | 6.34 | 12.86 | 5.86 | 8.27 | 1.39 |
| SR_FLIP_RETEST | kept | 2386 | 70.64 | 20.85 | 14.34 | 6.96 | 13.22 | 6.12 | 8.82 | 1.88 |
| TREND_PULLBACK_EMA | filtered | 34 | 57.18 | 12.24 | 18.00 | 7.63 | 14.09 | 7.85 | 9.16 | 5.41 |
| TREND_PULLBACK_EMA | kept | 286 | 77.21 | 18.74 | 18.00 | 8.29 | 14.78 | 7.56 | 8.51 | 5.04 |
| VOLUME_SURGE_BREAKOUT | filtered | 17 | 56.59 | 15.24 | 18.00 | 14.65 | 12.59 | 6.41 | 4.09 | 3.62 |
| VOLUME_SURGE_BREAKOUT | kept | 22 | 70.25 | 17.41 | 14.55 | 12.14 | 14.14 | 5.14 | 9.60 | 4.23 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 5 | 66.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 286 | 58.95 | 0.00 | 0.00 | 1.16 | 0.00 | 2.56 | 0.00 | 0.00 | 0.00 | **3.72** |
| DIVERGENCE_CONTINUATION | kept | 523 | 71.00 | 0.00 | 0.00 | 0.06 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.08** |
| FAILED_AUCTION_RECLAIM | filtered | 194 | 56.69 | 0.00 | 0.00 | 0.67 | 0.00 | 4.34 | 0.00 | 0.00 | 0.00 | **5.01** |
| FAILED_AUCTION_RECLAIM | kept | 436 | 71.52 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.07** |
| FUNDING_EXTREME_SIGNAL | filtered | 49 | 47.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 66 | 57.96 | 0.00 | 0.00 | 3.30 | 0.00 | 1.31 | 0.00 | 0.00 | 0.00 | **4.61** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 533 | 70.51 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 19 | 54.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 261 | 70.22 | 0.00 | 0.00 | 0.39 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | **0.44** |
| MOVER_AVWAP_SCALP | filtered | 302 | 56.05 | 0.75 | 0.00 | 0.93 | 0.00 | 0.00 | 0.00 | 0.00 | 2.06 | **3.74** |
| MOVER_AVWAP_SCALP | kept | 641 | 76.34 | 0.09 | 0.00 | 1.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.53 | **1.87** |
| MOVER_TREND_PULLBACK | filtered | 913 | 56.81 | 0.00 | 0.00 | 2.97 | 0.00 | 0.29 | 0.00 | 0.00 | 0.26 | **3.52** |
| MOVER_TREND_PULLBACK | kept | 8498 | 76.80 | 0.00 | 0.00 | 0.39 | 0.00 | 0.29 | 0.01 | 0.00 | 0.04 | **0.73** |
| QUIET_COMPRESSION_BREAK | filtered | 151 | 49.88 | 0.00 | 0.00 | 0.95 | 0.00 | 0.43 | 0.00 | 0.00 | 7.45 | **8.83** |
| QUIET_COMPRESSION_BREAK | kept | 730 | 75.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | 0.00 | **0.26** |
| SR_FLIP_RETEST | filtered | 916 | 57.92 | 0.00 | 0.00 | 0.21 | 0.00 | 2.48 | 0.01 | 0.00 | 0.10 | **2.80** |
| SR_FLIP_RETEST | kept | 2386 | 70.64 | 0.00 | 0.00 | 0.01 | 0.00 | 0.07 | 0.00 | 0.00 | 0.00 | **0.08** |
| TREND_PULLBACK_EMA | filtered | 34 | 57.18 | 0.00 | 0.00 | 4.59 | 0.00 | 9.88 | 0.00 | 0.00 | 0.00 | **14.47** |
| TREND_PULLBACK_EMA | kept | 286 | 77.21 | 0.00 | 0.00 | 0.62 | 0.00 | 2.93 | 0.00 | 0.00 | 0.00 | **3.55** |
| VOLUME_SURGE_BREAKOUT | filtered | 17 | 56.59 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.18 | **3.18** |
| VOLUME_SURGE_BREAKOUT | kept | 22 | 70.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.16 | **0.16** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=1023 (20.4%) | WOULD_LOSE=1961 | WOULD_EXPIRE=2028 | pending (awaiting window)=2381

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_edge:RANGE_FADE | 234 | 8.5% | 134.7 | 39.2 | +0.41 | **KEEP** |
| context_floor:FAILED_AUCTION_RECLAIM | 296 | 4.1% | 245.9 | 23.1 | +0.75 | **KEEP** |
| context_floor:FUNDING_EXTREME_SIGNAL | 15 | 53.3% | 1.6 | 11.0 | -0.63 | **INSUFFICIENT_SAMPLE** |
| context_floor:QUIET_COMPRESSION_BREAK | 400 | 0.0% | 65.7 | 0.0 | +0.16 | **KEEP** |
| context_floor:RANGE_FADE | 22 | 0.0% | 31.7 | 0.0 | +1.44 | **KEEP** |
| context_floor:VOLUME_SURGE_BREAKOUT | 51 | 0.0% | 25.3 | 0.0 | +0.50 | **KEEP** |
| context_floor:WHALE_MOMENTUM | 67 | 0.0% | 23.1 | 0.0 | +0.34 | **KEEP** |
| data_stale | 17 | 0.0% | 17.9 | 0.0 | +1.05 | **INSUFFICIENT_SAMPLE** |
| dispatch_cooldown | 396 | 21.2% | 70.0 | 69.0 | +0.00 | **TUNE** |
| dispatch_staleness_v2 | 346 | 59.2% | 68.6 | 166.4 | -0.28 | **DROP** |
| execution_component_floor | 46 | 0.0% | 47.1 | 0.0 | +1.02 | **KEEP** |
| level_still_in_play | 260 | 9.6% | 117.7 | 12.2 | +0.41 | **KEEP** |
| min_confidence | 263 | 5.7% | 201.8 | 17.3 | +0.70 | **KEEP** |
| quiet_scalp_block | 400 | 9.0% | 136.3 | 37.4 | +0.25 | **KEEP** |
| setup_compat:regime_BREAKOUT_EXPANSION | 55 | 0.0% | 21.5 | 0.0 | +0.39 | **KEEP** |
| setup_compat:regime_CLEAN_RANGE | 368 | 56.5% | 172.1 | 88.1 | +0.23 | **KEEP** |
| setup_compat:regime_DIRTY_RANGE | 376 | 9.0% | 278.4 | 20.5 | +0.69 | **KEEP** |
| setup_compat:regime_STRONG_TREND | 27 | 0.0% | 32.3 | 0.0 | +1.20 | **KEEP** |
| setup_compat:regime_VOLATILE_UNSUITABLE | 243 | 21.8% | 177.3 | 66.4 | +0.46 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 53 | 32.1% | 14.3 | 10.6 | +0.07 | **TUNE** |
| shadow_unit:SHADOW_FUNDING_FADE | 369 | 38.5% | 183.4 | 98.3 | +0.23 | **KEEP** |
| shadow_unit:SHADOW_MEAN_REVERT | 330 | 24.8% | 223.1 | 122.3 | +0.31 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 378 | 21.7% | 290.8 | 199.7 | +0.24 | **KEEP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 103440 across 21 strategies; 2328 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 23928 | 168/23760/0 | 59% | +0.09 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MAJOR (+1.27R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/ALTCOIN (-1.27R) |
| FAILED_AUCTION_RECLAIM | 16139 | 25/16114/0 | 53% | +0.04 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| SR_FLIP_RETEST | 15641 | 2/15639/0 | 48% | -0.17 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 9784 | 4/9780/0 | 46% | -0.09 | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.45R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 7520 | 0/7520/0 | 49% | -0.08 | ASIA/RANGE/NORMAL/BTC_NEUTRAL (+1.42R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| LIQUIDITY_SWEEP_REVERSAL | 3894 | 9/3885/0 | 46% | -0.19 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.78R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| MOVER_AVWAP_SCALP | 3866 | 28/3838/0 | 34% | -0.33 | OVERLAP/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+1.01R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| SHADOW_MEAN_REVERT | 3849 | 0/0/3849 | 41% | -0.04 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.00R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.03R) |
| SHADOW_RANGE_FADE | 3542 | 0/0/3542 | 41% | +0.21 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.28R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.96R) |
| MEAN_REVERT | 3268 | 0/3268/0 | 79% | +0.57 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.35R) |
| SHADOW_FUNDING_FADE | 3093 | 0/0/3093 | 40% | -0.30 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.33R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING (-0.88R) |
| TREND_PULLBACK_EMA | 2662 | 2/2660/0 | 54% | -0.15 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.73R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.19R) |
| RANGE_FADE | 2371 | 0/2371/0 | 11% | -0.89 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.34R) |
| VOLUME_SURGE_BREAKOUT | 1721 | 13/1708/0 | 39% | -0.11 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 832 | 2/830/0 | 27% | -0.44 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.07R) | OVERLAP/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.29R) |
| WHALE_MOMENTUM | 623 | 0/623/0 | 48% | -0.18 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-0.76R) |
| SHADOW_CASCADE_REVERSAL | 325 | 0/0/325 | 46% | -0.21 | LONDON/MARKUP/CASCADE/BTC_NEUTRAL (+0.15R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.80R) |
| BREAKDOWN_SHORT | 299 | 7/292/0 | 59% | +0.33 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| POST_DISPLACEMENT_CONTINUATION | 67 | 0/67/0 | 90% | +0.75 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 10 | 1/9/0 | 30% | -0.43 | — | — |
| LIQUIDATION_REVERSAL | 6 | 0/6/0 | 0% | -1.29 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP` +1.78R (n=42, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.45R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 28 | 29% / -0.45R | 28 | 39% / -0.25R | +0.19 | **ATR** |
| TREND_PULLBACK_EMA | 80 | 48% / -0.23R | 80 | 50% / -0.10R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 2575 | 46% / -0.19R | 2575 | 49% / -0.09R | +0.10 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 54 | 44% / +0.02R | 54 | 46% / -0.08R | -0.10 | **FIXED** |
| MOVER_AVWAP_SCALP | 237 | 39% / -0.19R | 237 | 41% / -0.11R | +0.08 | **ATR** |
| MEAN_REVERT | 297 | 58% / +0.12R | 297 | 54% / +0.19R | +0.07 | **ATR** |
| WHALE_MOMENTUM | 36 | 42% / -0.17R | 36 | 39% / -0.24R | -0.07 | **FIXED** |
| DIVERGENCE_CONTINUATION | 626 | 47% / -0.12R | 626 | 52% / -0.05R | +0.07 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 564 | 50% / -0.17R | 564 | 54% / -0.11R | +0.06 | **ATR** |
| RANGE_FADE | 171 | 9% / -0.91R | 171 | 11% / -0.85R | +0.06 | **ATR** |
| MOVER_TREND_PULLBACK | 2798 | 55% / +0.00R | 2798 | 57% / +0.02R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1058 | 47% / -0.11R | 1058 | 46% / -0.12R | -0.02 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 2092 | 47% / -0.10R | 2092 | 47% / -0.09R | +0.01 | **ATR** |
| BREAKDOWN_SHORT | 14 | 21% / -0.38R | 14 | 21% / -0.34R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 7 | 43% / -0.18R | 7 | 43% / -0.18R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 71% / +0.23R | 7 | 71% / +0.04R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 1 | 0% / -1.29R | 1 | 0% / -0.36R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 2932 | 31% | -0.11R | 243 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 227 | 40% | -0.12R | 92 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 15 | 53% | +0.08R | 12 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 952 | 28% / -2.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 5 | 20% / -1.13R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 1675 | 36% / -0.52R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 742 | 33% / -0.71R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 29 | 14% / -1.74R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 379 | 28% / -2.82R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 362 | 36% / +0.02R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 187 | 40% / -1.85R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 26 | 12% / -4.37R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 55 | 27% / -1.72R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 135 | 30% / -0.36R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 6 | 17% / -0.73R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 41 | 49% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 13 | 31% / -0.35R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 4 | 0% / -1.16R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._

| Setup | Gate | n | WOULD_WIN% | EV/suppression (R) | Verdict |
|---|---|---:|---:|---:|---|
| MOVER_AVWAP_SCALP | dispatch_staleness_v2 | 3 | 100.0% | -1.33 | **INSUFFICIENT_SAMPLE** |
| FUNDING_EXTREME_SIGNAL | context_floor:FUNDING_EXTREME_SIGNAL | 15 | 53.3% | -0.63 | **INSUFFICIENT_SAMPLE** |
| TREND_PULLBACK_EMA | level_still_in_play | 25 | 100.0% | -0.49 | **DROP** |
| MOVER_TREND_PULLBACK | dispatch_staleness_v2 | 280 | 60.4% | -0.37 | **DROP** |
| SR_FLIP_RETEST | dispatch_staleness_v2 | 34 | 85.3% | -0.34 | **DROP** |
| MOVER_AVWAP_SCALP | min_confidence | 34 | 17.6% | -0.12 | **TUNE** |
| MOVER_TREND_PULLBACK | dispatch_cooldown | 349 | 24.1% | -0.06 | **TUNE** |
| DIVERGENCE_CONTINUATION | setup_compat:regime_VOLATILE_UNSUITABLE | 118 | 35.6% | -0.02 | **TUNE** |
| MA_CROSS_TREND_SHIFT | setup_compat:regime_DIRTY_RANGE | 5 | 0.0% | +0.02 | **INSUFFICIENT_SAMPLE** |
| SR_FLIP_RETEST | quiet_scalp_block | 136 | 26.5% | +0.05 | **TUNE** |
| SHADOW_CASCADE_REVERSAL | shadow_unit:SHADOW_CASCADE_REVERSAL | 53 | 32.1% | +0.07 | **TUNE** |
| FAILED_AUCTION_RECLAIM | dispatch_cooldown | 2 | 0.0% | +0.08 | **INSUFFICIENT_SAMPLE** |
| QUIET_COMPRESSION_BREAK | min_confidence | 2 | 0.0% | +0.12 | **INSUFFICIENT_SAMPLE** |
| SR_FLIP_RETEST | dispatch_cooldown | 19 | 0.0% | +0.14 | **INSUFFICIENT_SAMPLE** |
| DIVERGENCE_CONTINUATION | dispatch_cooldown | 10 | 0.0% | +0.16 | **INSUFFICIENT_SAMPLE** |
| QUIET_COMPRESSION_BREAK | context_floor:QUIET_COMPRESSION_BREAK | 400 | 0.0% | +0.16 | **KEEP** |
| DIVERGENCE_CONTINUATION | quiet_scalp_block | 4 | 0.0% | +0.19 | **INSUFFICIENT_SAMPLE** |
| LIQUIDITY_SWEEP_REVERSAL | level_still_in_play | 13 | 0.0% | +0.19 | **INSUFFICIENT_SAMPLE** |
| QUIET_COMPRESSION_BREAK | level_still_in_play | 7 | 0.0% | +0.19 | **INSUFFICIENT_SAMPLE** |
| QUIET_COMPRESSION_BREAK | quiet_scalp_block | 122 | 0.0% | +0.19 | **KEEP** |
| TREND_PULLBACK_EMA | setup_compat:regime_CLEAN_RANGE | 368 | 56.5% | +0.23 | **KEEP** |
| SHADOW_FUNDING_FADE | shadow_unit:SHADOW_FUNDING_FADE | 369 | 38.5% | +0.23 | **KEEP** |
| SHADOW_RANGE_FADE | shadow_unit:SHADOW_RANGE_FADE | 378 | 21.7% | +0.24 | **KEEP** |
| FAILED_AUCTION_RECLAIM | quiet_scalp_block | 98 | 0.0% | +0.29 | **KEEP** |
| SHADOW_MEAN_REVERT | shadow_unit:SHADOW_MEAN_REVERT | 330 | 24.8% | +0.31 | **KEEP** |

- _sorted most-costly first: the top rows are gates whose suppressions lose more than they save on that specific path_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 34 · alerting: **8** · boot grace active: False
- **ALERT** `sar_ledger_candles` — 137/224 unfetchable (61%); top cause: gap or duplicate bar in the 15m window; symbols: 1000SHIBUSDT, ADAUSDT, AIOUSDT, AKEUSDT, AVAXUSDT +22 more (streak 170/6) (sustained 170 cycles)
- **ALERT** `candle_series_integrity` — merge dropped 3007 dup bars, 1 undedupable; ws 2 out-of-order, 142 in-place; SAR refused 7267 series (streak 6/6) (sustained 6 cycles)
- **ALERT** `entry_feature_inputs` — 9 feature(s) absent on EVERY stamp of their path: MEAN_REVERT.extension_pct,MEAN_REVERT.level_dist_r,MOVER_AVWAP_SCALP.extension_pct,MOVER_AVWAP_SCALP.level_dist_r,MOVER_TREND_PULLBACK.level_dist_r,RANGE_FADE.extension_pct,RANGE_FADE.level_dist_r,TREND_PULLBACK_EMA.level_dist_r,TREND_PULLBACK_EMA.smc_zone_dist_atr — upstream is dark, and the panel cannot tell that from 'unused' (streak 170/6) (sustained 170 cycles)
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 3 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 170/6) (sustained 170 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 5188x (gate reads 0x, withheld 0x — refusal dark); last AEVOUSDT age=25489.1s (streak 62/6) (sustained 62 cycles)
- **ALERT** `mean_revert_emission` — 286 detections since last emission (emitted_total=25) — and the blocked candidates measure +0.57R over n=3268, so the gating is COSTING us. Check gate rejections. (streak 13/6) (sustained 13 cycles)
- **ALERT** `tuned_variants` — 156 unexplained non-stamps (seen=2918 stamped=332 skipped=2430) (streak 170/6) (sustained 170 cycles)
- **ALERT** `auto_dispatch` — 15 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=17) (streak 136/3) (sustained 136 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | violating | 15 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=17) (streak 136/3) | 136 |
| btc_reference | ok | BTC ref 63436.70 | 0 |
| candle_coverage | ok | 89/102 symbols with ≥20 15m candles, 78/102 updated within 45m | 0 |
| candle_series_integrity | violating | merge dropped 3007 dup bars, 1 undedupable; ws 2 out-of-order, 142 in-place; SAR refused 7267 series (streak 6/6) | 6 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 3 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 170/6) | 170 |
| context_emission_policy | ok | output +40 / upstream +31 | 0 |
| dark_resolution | ok | 9 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open dark arms | 0 |
| edge_reconciliation | ok | max divergence MOVER_AVWAP_SCALP +0.29R (< 0.3) | 0 |
| emission_controller | ok | last cycle 323s ago; live_overrides=21 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=10 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 9 feature(s) absent on EVERY stamp of their path: MEAN_REVERT.extension_pct,MEAN_REVERT.level_dist_r,MOVER_AVWAP_SCALP.extension_pct,MOVER_AVWAP_SCALP.level_dist_r,MOVER_TREND_PULLBACK.level_dist_r,RANGE_FADE.extension_pct,RANGE_FADE.level_dist_r,TREND_PULLBACK_EMA.level_dist_r,TREND_PULLBACK_EMA.smc_zone_dist_atr — upstream is dark, and the panel cannot tell that from 'unused' (streak 170/6) | 170 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +3 / upstream +105 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 286 detections since last emission (emitted_total=25) — and the blocked candidates measure +0.57R over n=3268, so the gating is COSTING us. Check gate rejections. (streak 13/6) | 13 |
| mean_revert_path | ok | output +27 / upstream +105 | 0 |
| mover_admission_metadata | ok | 851 symbols known, 150 marked TRADIFI_PERPETUAL | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2868 rows held, 26138 evicted (sampled: execution:overextended 400/10658, execution:trigger_not_confirmed 400/8101, setup_compat:regime_STRONG_TREND 400/4875) | 0 |
| promoted_pair_integrity | ok | 10/10 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE counterfactuals measure -0.89R over n=2371 — emitting them would lose money | 0 |
| range_fade_path | ok | output +3 / upstream +105 | 0 |
| sar_alignment_crosscheck | ok | 158/5750 disagreed (2.7%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +105 | 0 |
| sar_ledger_candles | violating | 137/224 unfetchable (61%); top cause: gap or duplicate bar in the 15m window; symbols: 1000SHIBUSDT, ADAUSDT, AIOUSDT, AKEUSDT, AVAXUSDT +22 more (streak 170/6) | 170 |
| sar_live_arms | ok | 5 arms current, none stalled | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 6 resolved, 81 still mid-window | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| stale_tf_scoring | violating | scored on stale TF 5188x (gate reads 0x, withheld 0x — refusal dark); last AEVOUSDT age=25489.1s (streak 62/6) | 62 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +61 / upstream +105 | 0 |
| suppression_audit | ok | output +105 / upstream +31 | 0 |
| tuned_variants | violating | 156 unexplained non-stamps (seen=2918 stamped=332 skipped=2430) (streak 170/6) | 170 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3296898`
- `Path funnel` emissions: `82`
- `Regime distribution` emissions: `82`
- `QUIET_SCALP_BLOCK` events: `467`
- `confidence_gate` events: `17270`
- `free_channel_post` events: `32`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **11**
- Total REST-fallback activations: **3**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 7 | 2842 | 4996 | 25732 | 0 |
| futures_liq | 2 | 3399 | 3399 | 3614 | 0 |
| futures_mover | 2 | 1559 | 1559 | 3728 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 3 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **32**

| Source | Count |
|---|---:|
| signal_close | 20 |
| regime_shift | 12 |

- By severity: HIGH=32

## Dependency readiness
- cvd: presence[present=474467] state[populated=474467] buckets[few=8, many=474298, some=161] sources[none] quality[none]
- funding_rate: presence[absent=46175, present=428292] state[empty=46175, populated=428292] buckets[few=428292, none=46175] sources[none] quality[none]
- liquidation_clusters: presence[absent=292282, present=182185] state[empty=292282, populated=182185] buckets[few=145381, none=292282, some=36804] sources[none] quality[none]
- oi_snapshot: presence[absent=43554, present=430913] state[empty=43554, populated=430913] buckets[many=430913, none=43554] sources[none] quality[none]
- order_book: presence[absent=129711, present=344756] state[populated=344756, unavailable=129711] buckets[few=344756, none=129711] sources[book_ticker=344756, unavailable=129711] quality[none=129711, top_of_book_only=344756]
- orderblocks: presence[absent=474467] state[empty=474467] buckets[none=474467] sources[not_implemented=474467] quality[none]
- recent_ticks: presence[present=474467] state[populated=474467] buckets[many=474467] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.879044413566589` sec
- Median create→first breach: `1667.347631573677` sec
- Median create→terminal: `1668.4697835445404` sec
- Median first breach→terminal: `2.7764880657196045` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 5.0}, "under_180s": {"count": 1, "pct": 5.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 5.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 5.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.6 | 233.59401512145996 | 237.09161520004272 |
| MOVER_TREND_PULLBACK | 18 | 18 | 0.0 | 55.6 | 0.0 | 0.0 | -1.4694 | 1902.4504301548004 | 1907.7459225654602 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.993 | 701.3807878494263 | 703.0441348552704 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 23220 | 120 | 11319 | 0.0 | 0.0 | None | None | 11901 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2821 | 27 | 2367 | 0.0 | 0.0 | None | None | 454 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `23`
- Gating Δ: `-13486`
- No-generation Δ: `54895`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.6377, "current_avg_pnl": -1.4694, "current_win_rate": 0.0, "previous_avg_pnl": 0.1683, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -22, "geometry_changed_delta": 0, "geometry_preserved_delta": 3375, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 6, "geometry_changed_delta": 0, "geometry_preserved_delta": -39, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
