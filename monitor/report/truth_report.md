# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `1113` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 32 | 32 | 11 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 3402 | 3402 | 2997 | 18 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 43772 | 43785 | 4 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 40286 | 40287 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 40027 | 39050 | 1224 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 40319 | 39816 | 570 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 39977 | 39850 | 156 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 32593 | 32606 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 40388 | 40414 | 6 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 40424 | 39535 | 1534 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 47444 | 52220 | 253 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 43791 | 39648 | 7743 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 39750 | 39751 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 40290 | 40311 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 40009 | 39987 | 39 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 41070 | 40437 | 900 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 39752 | 39944 | 29 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 32326 | 31407 | 1129 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 32537 | 32424 | 164 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 43737 | 43760 | 7 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 32609 | 32624 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1967 | 1967 | 1379 | 10 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 557 | 557 | 89 | 5 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 6684 | 6684 | 6024 | 39 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 6 | 6 | 2 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 4259 | 4259 | 2966 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 632 | 632 | 298 | 26 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 21618 | 21618 | 11565 | 390 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 11 | 11 | 9 | 2 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 215 | 215 | 40 | 38 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 2157 | 2157 | 1492 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 95 | 95 | 61 | 6 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 642 | 642 | 438 | 20 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 84 | 84 | 39 | 3 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=43785): breakout_not_found=24539, basic_filters_failed=13396, move_not_fresh=3935, breakout_stale=1639, retest_proximity_failed=211, volume_spike_missing=61, move_exhausted=2, missing_fvg_or_orderblock=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=40287): cls_disabled_merged_into_lsr=40287
- **EVAL::DIVERGENCE_CONTINUATION** (total=39050): cvd_divergence_failed=13307, basic_filters_failed=11392, h1_trend_not_aligned=11009, ema_alignment_reject=2757, retest_proximity_failed=381, missing_fvg_or_orderblock=204
- **EVAL::FAILED_AUCTION_RECLAIM** (total=39816): auction_not_detected=24798, basic_filters_failed=11300, reclaim_hold_failed=1784, tail_too_small=1241, regime_blocked=671, rsi_reject=22
- **EVAL::FUNDING_EXTREME** (total=39850): funding_not_extreme=26576, basic_filters_failed=11379, ema_alignment_reject=1057, rsi_reject=588, cvd_divergence_failed=120, momentum_reject=104, missing_fvg_or_orderblock=19, missing_funding_rate=7
- **EVAL::LIQUIDATION_REVERSAL** (total=32606): cascade_threshold_not_met=21214, basic_filters_failed=11191, cvd_divergence_failed=102, rsi_reject=91, missing_fvg_or_orderblock=6, volume_spike_missing=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=40414): no_ma_cross=28858, basic_filters_failed=11408, ma_cross_cooldown=94, ma_cross_htf_misaligned=54
- **EVAL::MEAN_REVERT** (total=39535): no_extension=32406, basic_filters_failed=7129
- **EVAL::MOVER_AVWAP_SCALP** (total=52220): no_avwap_tag=18670, basic_filters_failed=13563, no_mover_leg=12271, avwap_slope_against=5791, avwap_reclaim_no_volume=1049, no_avwap_reclaim=872, anchor_too_recent=4
- **EVAL::MOVER_TREND_PULLBACK** (total=39648): mover_run_too_small=14724, basic_filters_failed=13486, no_reclaim=10649, no_pullback_tag=789
- **EVAL::OPENING_RANGE_BREAKOUT** (total=39751): feature_disabled=39751
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=40311): regime_blocked=21765, breakout_not_found=12514, basic_filters_failed=3845, adx_reject=2078, ema_alignment_reject=109
- **EVAL::QUIET_COMPRESSION_BREAK** (total=39987): regime_blocked=19047, compression_not_detected=10343, basic_filters_failed=7447, breakout_not_detected=2918, volume_confirmation_failed=225, missing_fvg_or_orderblock=4, rsi_reject=3
- **EVAL::RANGE_FADE** (total=40437): no_range_edge=33307, basic_filters_failed=7130
- **EVAL::SR_FLIP_RETEST** (total=39944): flip_close_not_confirmed=25268, basic_filters_failed=11277, retest_out_of_zone=915, long_break_volume_thin=830, regime_blocked=663, h1_break_not_confirmed=468, reclaim_hold_failed=344, long_acceptance_not_held=71, ema_alignment_reject=48, wick_quality_failed=39, missing_fvg_or_orderblock=12, whipsaw_flip=9
- **EVAL::STANDARD** (total=31407): momentum_reject=10665, adx_reject=7597, basic_filters_failed=5107, sweeps_not_detected=2956, macd_reject=2104, ema_alignment_reject=2099, htf_poi_unanchored=863, invalid_sl_geometry=9, rsi_reject=7
- **EVAL::TREND_PULLBACK** (total=32424): h1_trend_not_aligned=11388, basic_filters_failed=6348, ema_alignment_reject=5314, h1_pullback_not_confirmed=3590, no_ema_reclaim_close=1828, ema_not_tested_prev=1781, body_conviction_fail=807, rsi_reject=758, prev_already_below_emas=216, no_prev_low_break=147, prev_already_above_emas=88, momentum_flat=68, no_prev_high_break=60, ema21_not_tagged=14, momentum_reject=9, missing_fvg_or_orderblock=8
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=43760): breakout_not_found=23046, basic_filters_failed=13393, move_not_fresh=4625, breakout_stale=1956, retest_proximity_failed=572, volume_spike_missing=158, missing_fvg_or_orderblock=8, move_exhausted=2
- **EVAL::WHALE_MOMENTUM** (total=32624): momentum_reject=27096, recent_ticks_insufficient=3818, basic_filters_failed=1710

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=5): execution:overextended=5
- **DIVERGENCE_CONTINUATION** (total=213): setup_compat:regime_VOLATILE_UNSUITABLE=189, setup_compat:regime_BREAKOUT_EXPANSION=18, execution:overextended=6
- **FAILED_AUCTION_RECLAIM** (total=1223): setup_compat:regime_STRONG_TREND=545, execution:overextended=362, context_floor=253, setup_compat:regime_VOLATILE_UNSUITABLE=63
- **FUNDING_EXTREME_SIGNAL** (total=413): execution:trigger_not_confirmed=413
- **LIQUIDATION_REVERSAL** (total=1): execution:trigger_not_confirmed=1
- **LIQUIDITY_SWEEP_REVERSAL** (total=2203): setup_compat:regime_STRONG_TREND=1236, execution:trigger_not_confirmed=547, execution:overextended=420
- **MA_CROSS_TREND_SHIFT** (total=6): setup_compat:regime_CLEAN_RANGE=2, setup_compat:regime_DIRTY_RANGE=2, execution:trigger_not_confirmed=1, execution:overextended=1
- **MEAN_REVERT** (total=3599): setup_compat:regime_STRONG_TREND=2004, setup_compat:regime_WEAK_TREND=1381, execution:overextended=212, entry_quality=2
- **MOVER_AVWAP_SCALP** (total=531): execution:overextended=334, execution:trigger_not_confirmed=148, entry_quality=49
- **MOVER_TREND_PULLBACK** (total=10993): execution:trigger_not_confirmed=7752, execution:overextended=1859, entry_quality=1382
- **QUIET_COMPRESSION_BREAK** (total=9): execution:trigger_not_confirmed=9
- **RANGE_FADE** (total=1805): setup_compat:regime_STRONG_TREND=960, setup_compat:regime_WEAK_TREND=701, setup_compat:regime_VOLATILE_UNSUITABLE=84, context_edge=42, execution:overextended=12, setup_compat:regime_BREAKOUT_EXPANSION=6
- **TREND_PULLBACK_EMA** (total=553): setup_compat:regime_CLEAN_RANGE=295, setup_compat:regime_DIRTY_RANGE=173, entry_quality=43, setup_compat:regime_VOLATILE_UNSUITABLE=42
- **VOLUME_SURGE_BREAKOUT** (total=7): execution:overextended=7

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 81292 | 31.5% |
| TRENDING_UP | 72900 | 28.2% |
| QUIET | 49461 | 19.2% |
| TRENDING_DOWN | 49366 | 19.1% |
| VOLATILE | 5223 | 2.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **293**
- Average confidence gap to threshold: **10.35** (samples=293) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XMRUSDT=45, ETHUSDT=32, ZECUSDT=29, TRUMPUSDT=21, WLFIUSDT=20, XRPUSDT=17, TAOUSDT=14, BTCUSDT=13, NEARUSDT=12, INJUSDT=11

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 3 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 70 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 60 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 16 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 8 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 11 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 69 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 8 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 59 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 18 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 90 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 40 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 13 |
| MEAN_REVERT | kept | min_confidence_pass | 16 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 53 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 81 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2099 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 198 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2532 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 45 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 24 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 57 |
| SR_FLIP_RETEST | filtered | min_confidence | 11 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 12 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 29 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 82 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 42 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 3 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 3 | 62.50 | 65.00 | 2.50 | 18.57 | 18.20 | 20.00 | 4.50 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 70 | 55.15 | 63.93 | 8.78 | 21.11 | 19.75 | 17.61 | 0.87 | 13.77 |
| DIVERGENCE_CONTINUATION | kept | 60 | 68.56 | 65.00 | -3.56 | 20.46 | 19.70 | 17.04 | 0.43 | -0.11 |
| FAILED_AUCTION_RECLAIM | filtered | 24 | 52.22 | 63.54 | 11.32 | 21.20 | 19.76 | 20.00 | 3.31 | 16.23 |
| FAILED_AUCTION_RECLAIM | kept | 11 | 69.34 | 65.00 | -4.34 | 20.92 | 19.65 | 20.00 | 4.73 | 3.63 |
| FUNDING_EXTREME_SIGNAL | filtered | 69 | 46.75 | 64.54 | 17.79 | 19.80 | 14.86 | 16.74 | 3.09 | 5.85 |
| FUNDING_EXTREME_SIGNAL | kept | 8 | 66.28 | 65.00 | -1.28 | 20.09 | 16.90 | 17.00 | 2.25 | 1.88 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 77 | 57.28 | 65.00 | 7.72 | 20.40 | 19.45 | 18.51 | 1.18 | 12.20 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 90 | 68.72 | 65.00 | -3.72 | 21.73 | 18.95 | 17.84 | 2.09 | 0.51 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 45.60 | 61.00 | 15.40 | 21.10 | 14.00 | 15.80 | 0.00 | 30.90 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 61.00 | 65.00 | 4.00 | 20.70 | 20.00 | 15.80 | 0.00 | 5.00 |
| MEAN_REVERT | filtered | 53 | 48.79 | 65.00 | 16.21 | 18.98 | 19.25 | 14.42 | 0.00 | 10.26 |
| MEAN_REVERT | kept | 16 | 72.50 | 65.00 | -7.50 | 21.91 | 14.15 | 14.80 | 0.00 | 0.54 |
| MOVER_AVWAP_SCALP | filtered | 53 | 53.82 | 65.00 | 11.18 | 20.38 | 14.62 | 15.80 | 4.71 | 16.13 |
| MOVER_AVWAP_SCALP | kept | 81 | 80.25 | 65.00 | -15.25 | 19.73 | 15.16 | 15.80 | 4.77 | 4.09 |
| MOVER_TREND_PULLBACK | filtered | 2297 | 55.47 | 64.07 | 8.60 | 20.27 | 18.94 | 15.80 | 4.13 | 14.97 |
| MOVER_TREND_PULLBACK | kept | 2532 | 75.27 | 65.00 | -10.27 | 20.30 | 18.84 | 15.80 | 4.17 | 2.36 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 67.20 | 65.00 | -2.20 | 21.20 | 20.00 | 16.60 | 4.50 | 13.30 |
| QUIET_COMPRESSION_BREAK | filtered | 69 | 55.41 | 65.00 | 9.59 | 21.26 | 19.77 | 20.00 | 0.00 | 5.72 |
| QUIET_COMPRESSION_BREAK | kept | 57 | 72.90 | 65.00 | -7.90 | 21.03 | 18.70 | 20.00 | 0.00 | -0.17 |
| SR_FLIP_RETEST | filtered | 11 | 57.50 | 65.00 | 7.50 | 20.72 | 20.00 | 16.07 | 1.09 | 11.50 |
| SR_FLIP_RETEST | kept | 12 | 71.56 | 65.00 | -6.56 | 20.91 | 20.00 | 16.13 | 2.00 | 0.27 |
| TREND_PULLBACK_EMA | filtered | 32 | 56.65 | 64.69 | 8.04 | 20.36 | 19.55 | 17.53 | 5.14 | 15.01 |
| TREND_PULLBACK_EMA | kept | 82 | 77.96 | 65.00 | -12.96 | 20.46 | 19.84 | 17.20 | 4.80 | 1.08 |
| VOLUME_SURGE_BREAKOUT | filtered | 42 | 50.46 | 64.90 | 14.44 | 18.34 | 19.02 | 20.00 | 3.63 | 7.40 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 75.07 | 65.00 | -10.07 | 19.47 | 16.70 | 20.00 | 4.83 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 3 | 62.50 | 2.00 | 18.00 | 12.00 | 14.00 | 5.00 | 10.00 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 70 | 55.15 | 21.69 | 15.43 | 5.61 | 13.14 | 4.98 | 7.93 | 0.87 |
| DIVERGENCE_CONTINUATION | kept | 60 | 68.56 | 22.73 | 12.33 | 5.05 | 13.93 | 6.92 | 8.84 | 0.43 |
| FAILED_AUCTION_RECLAIM | filtered | 24 | 52.22 | 20.67 | 14.83 | 7.25 | 13.96 | 6.71 | 4.84 | 3.31 |
| FAILED_AUCTION_RECLAIM | kept | 11 | 69.34 | 22.82 | 15.09 | 6.27 | 11.91 | 7.00 | 5.15 | 4.73 |
| FUNDING_EXTREME_SIGNAL | filtered | 69 | 46.75 | 24.42 | 8.43 | 5.09 | 12.17 | 7.67 | 6.51 | 3.09 |
| FUNDING_EXTREME_SIGNAL | kept | 8 | 66.28 | 24.00 | 10.50 | 4.88 | 13.00 | 8.00 | 7.40 | 2.25 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 77 | 57.28 | 22.14 | 14.68 | 5.61 | 13.13 | 5.64 | 7.10 | 1.18 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 90 | 68.72 | 23.33 | 14.53 | 4.27 | 12.68 | 5.54 | 6.82 | 2.09 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 45.60 | 17.00 | 14.00 | 15.00 | 14.00 | 8.50 | 8.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 61.00 | 17.00 | 14.00 | 3.00 | 17.00 | 5.00 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 53 | 48.79 | 21.08 | 14.98 | 13.13 | 10.74 | 5.00 | 6.01 | 0.00 |
| MEAN_REVERT | kept | 16 | 72.50 | 18.00 | 17.75 | 12.00 | 12.94 | 5.00 | 7.34 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 53 | 53.82 | 17.38 | 18.00 | 11.72 | 12.79 | 6.60 | 5.81 | 4.71 |
| MOVER_AVWAP_SCALP | kept | 81 | 80.25 | 21.37 | 18.05 | 12.46 | 13.44 | 6.52 | 8.65 | 4.77 |
| MOVER_TREND_PULLBACK | filtered | 2297 | 55.47 | 18.48 | 18.01 | 7.59 | 12.60 | 6.33 | 8.54 | 4.13 |
| MOVER_TREND_PULLBACK | kept | 2532 | 75.27 | 19.77 | 18.02 | 7.75 | 13.09 | 6.48 | 9.12 | 4.17 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 67.20 | 17.00 | 18.00 | 15.00 | 11.00 | 5.00 | 10.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 69 | 55.41 | 18.16 | 16.61 | 10.13 | 14.00 | 8.01 | 6.62 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 57 | 72.90 | 19.67 | 17.72 | 11.84 | 13.89 | 6.25 | 5.73 | 0.00 |
| SR_FLIP_RETEST | filtered | 11 | 57.50 | 17.00 | 18.00 | 3.82 | 14.55 | 6.59 | 7.95 | 1.09 |
| SR_FLIP_RETEST | kept | 12 | 71.56 | 21.00 | 18.00 | 4.25 | 13.67 | 5.33 | 7.58 | 2.00 |
| TREND_PULLBACK_EMA | filtered | 32 | 56.65 | 16.59 | 18.00 | 8.53 | 15.12 | 5.73 | 8.35 | 5.14 |
| TREND_PULLBACK_EMA | kept | 82 | 77.96 | 19.38 | 18.00 | 7.74 | 14.49 | 6.90 | 9.10 | 4.80 |
| VOLUME_SURGE_BREAKOUT | filtered | 42 | 50.46 | 17.76 | 17.90 | 12.00 | 12.71 | 4.70 | 4.15 | 3.63 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 75.07 | 22.33 | 18.00 | 14.00 | 14.00 | 5.00 | 6.90 | 4.83 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 3 | 62.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 70 | 55.15 | 0.00 | 0.00 | 0.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.89** |
| DIVERGENCE_CONTINUATION | kept | 60 | 68.56 | 0.00 | 0.00 | 0.21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.21** |
| FAILED_AUCTION_RECLAIM | filtered | 24 | 52.22 | 0.00 | 0.00 | 0.00 | 0.00 | 8.10 | 0.00 | 0.00 | 0.00 | **8.10** |
| FAILED_AUCTION_RECLAIM | kept | 11 | 69.34 | 0.00 | 0.00 | 0.00 | 0.00 | 0.65 | 0.00 | 0.00 | 0.00 | **0.65** |
| FUNDING_EXTREME_SIGNAL | filtered | 69 | 46.75 | 0.00 | 0.00 | 2.13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.13** |
| FUNDING_EXTREME_SIGNAL | kept | 8 | 66.28 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 77 | 57.28 | 0.00 | 0.00 | 1.41 | 0.00 | 2.62 | 0.70 | 0.00 | 0.00 | **4.73** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 90 | 68.72 | 0.00 | 0.00 | 0.00 | 0.00 | 0.13 | 0.00 | 0.00 | 0.00 | **0.13** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 45.60 | 0.00 | 0.00 | 4.80 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **12.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 61.00 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| MEAN_REVERT | filtered | 53 | 48.79 | 0.00 | 0.00 | 0.00 | 0.00 | 9.92 | 0.34 | 0.00 | 0.00 | **10.26** |
| MEAN_REVERT | kept | 16 | 72.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 53 | 53.82 | 0.00 | 0.00 | 0.91 | 0.00 | 3.40 | 0.00 | 0.00 | 0.68 | **4.99** |
| MOVER_AVWAP_SCALP | kept | 81 | 80.25 | 0.00 | 0.00 | 1.38 | 0.00 | 0.83 | 0.00 | 0.00 | 0.00 | **2.21** |
| MOVER_TREND_PULLBACK | filtered | 2297 | 55.47 | 0.00 | 0.00 | 2.68 | 0.00 | 0.59 | 0.07 | 0.00 | 0.00 | **3.34** |
| MOVER_TREND_PULLBACK | kept | 2532 | 75.27 | 0.00 | 0.00 | 0.77 | 0.00 | 0.09 | 0.03 | 0.00 | 0.00 | **0.89** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 67.20 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| QUIET_COMPRESSION_BREAK | filtered | 69 | 55.41 | 0.00 | 0.00 | 0.21 | 0.00 | 0.75 | 1.57 | 0.00 | 1.50 | **4.03** |
| QUIET_COMPRESSION_BREAK | kept | 57 | 72.90 | 0.00 | 0.00 | 0.00 | 0.00 | 1.36 | 0.00 | 0.00 | 0.00 | **1.36** |
| SR_FLIP_RETEST | filtered | 11 | 57.50 | 0.00 | 0.00 | 2.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.18** |
| SR_FLIP_RETEST | kept | 12 | 71.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 32 | 56.65 | 0.00 | 0.00 | 2.95 | 0.00 | 2.85 | 0.00 | 0.00 | 0.00 | **5.80** |
| TREND_PULLBACK_EMA | kept | 82 | 77.96 | 0.00 | 0.00 | 0.53 | 0.00 | 0.09 | 0.00 | 0.00 | 0.00 | **0.62** |
| VOLUME_SURGE_BREAKOUT | filtered | 42 | 50.46 | 0.00 | 0.00 | 2.29 | 0.00 | 0.00 | 0.00 | 0.00 | 2.97 | **5.26** |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 75.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **199373 held of 972842 seen** across 21 strategies; 4516 cells past the sample floor; **2451 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 49326 | 618/48708/0 | 43% | -0.20 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/QUIET/EXPANDED/BTC_FALLING/MAJOR (-1.26R) |
| MOVER_AVWAP_SCALP | 26459 | 186/26273/0 | 44% | -0.17 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 15905 | 281/15624/0 | 47% | -0.10 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.98R) | NY/MARKUP/CASCADE/BTC_FALLING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 15056 | 154/14902/0 | 35% | -0.33 | OVERLAP/RANGE/NORMAL/BTC_FALLING/MIDCAP (+1.66R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 14238 | 78/14160/0 | 38% | -0.30 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 11507 | 126/11381/0 | 39% | -0.40 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.91R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9726 | 504/9222/0 | 45% | -0.10 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8445 | 0/0/8445 | 42% | -0.12 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.99R) | OVERLAP/MARKDOWN/EXPANDED/BTC_FALLING (-0.96R) |
| SHADOW_RANGE_FADE | 7977 | 0/0/7977 | 36% | -0.13 | ASIA/MARKDOWN/NORMAL/BTC_FALLING (+0.68R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.36R) |
| SHADOW_FUNDING_FADE | 7586 | 0/0/7586 | 35% | -0.40 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.08R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 7514 | 30/7484/0 | 47% | -0.28 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 5811 | 75/5736/0 | 37% | -0.31 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4695 | 4/4691/0 | 32% | -0.41 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.06R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.30R) |
| WHALE_MOMENTUM | 4395 | 4/4391/0 | 47% | -0.28 | NY/RANGE/EXPANDED/BTC_FALLING (+0.94R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 4205 | 0/4205/0 | 28% | -0.42 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/NORMAL/BTC_FALLING/ALTCOIN (-1.19R) |
| RANGE_FADE | 3245 | 6/3239/0 | 53% | +0.30 | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (+3.08R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.78R) |
| SHADOW_CASCADE_REVERSAL | 1784 | 0/0/1784 | 52% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 605 | 75/530/0 | 35% | -0.26 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 572 | 0/572/0 | 35% | -0.28 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 254 | 40/214/0 | 44% | -0.17 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 68 | 6/62/0 | 41% | +0.08 | — | — |

- **Strongest cells**: `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.08R (n=37, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.00R (n=32, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.78R (n=47, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 459 | 28% / -0.53R | 459 | 52% / -0.09R | +0.44 | **ATR** |
| TREND_PULLBACK_EMA | 1479 | 39% / -0.35R | 1479 | 50% / -0.08R | +0.27 | **ATR** |
| LIQUIDATION_REVERSAL | 35 | 26% / -0.58R | 35 | 46% / -0.34R | +0.24 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1810 | 44% / -0.34R | 1810 | 58% / -0.10R | +0.24 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 245 | 37% / -0.18R | 245 | 49% / -0.04R | +0.15 | **ATR** |
| BREAKDOWN_SHORT | 56 | 41% / -0.23R | 56 | 46% / -0.10R | +0.13 | **ATR** |
| MA_CROSS_TREND_SHIFT | 76 | 45% / -0.16R | 76 | 50% / -0.03R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 843 | 48% / -0.25R | 843 | 52% / -0.13R | +0.12 | **ATR** |
| WHALE_MOMENTUM | 473 | 46% / -0.30R | 473 | 48% / -0.20R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 9273 | 48% / -0.13R | 9273 | 54% / -0.03R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1688 | 41% / -0.22R | 1688 | 44% / -0.12R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 2983 | 47% / -0.12R | 2983 | 53% / -0.03R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 2154 | 48% / -0.11R | 2154 | 53% / -0.06R | +0.05 | **ATR** |
| RANGE_FADE | 175 | 46% / +0.12R | 175 | 53% / +0.16R | +0.03 | **ATR** |
| MEAN_REVERT | 510 | 46% / -0.15R | 510 | 45% / -0.17R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 15 | 53% / -0.07R | 15 | 53% / -0.08R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1718 | 49% / -0.08R | 1718 | 49% / -0.08R | +0.00 | **ATR** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12360 | 27% | -0.22R | 314 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2983 | 51% | -0.02R | 244 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 157 | 48% | -0.05R | 74 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1895 | 33% / -0.12R | +0.95 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 2154 | 41% / -0.11R | +0.90 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3543 | 37% / -0.12R | +0.72 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11355 | 36% / -0.17R | +0.36 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2494 | 37% / -0.11R | +0.17 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 172 | 34% / -0.39R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1667 | 37% / -0.09R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1407 | 32% / -0.27R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 358 | 32% / -0.34R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 569 | 32% / -0.24R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 423 | 48% / -0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 98 | 44% / -0.02R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 124 | 48% / +0.07R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 730 | 37% / -0.24R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 125 | 31% / +0.11R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 46 | 43% / -0.26R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 28 | 46% / +0.48R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 64 · alerting: **4** · boot grace active: False
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 10/6) (sustained 10 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.59R (bound 0.3) (streak 422/6) (sustained 422 cycles)
- **ALERT** `range_fade_emission` — 646 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.30R over n=3239, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 19/6) (sustained 19 cycles)
- **ALERT** `tuned_variants` — 417 non-stamps — atr_arm_uncomputable=417 (seen=16860 stamped=2646 skipped=13797) (streak 422/6) (sustained 422 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 49 fed / 0 quiet / 0 never delivered of 49 subscribed; 163933330 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 29 arms current, none stalled; covering 2127/2127 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| analyst_plan_cadence | ok | last plan 41m ago | 0 |
| atr_trail_live_arms | ok | 59 arms current, none stalled; covering 1133/1133 signals (100%) | 0 |
| auto_dispatch | ok | 108 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=108. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 166/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 59144.30 | 0 |
| candle_coverage | ok | 84/84 symbols with ≥20 15m candles, 84/84 updated within 45m [fresh=84; 77 Tier-1 futures + 7 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 2909 dup bars, 0 undedupable; ws 0 out-of-order, 359 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 63 cohorts, 26 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +12 / upstream +22 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 2549/2568 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 3 promoted today, nothing refused | 0 |
| dark_resolution | violating | 7 of 116 open dark rows are not being advanced (worst: AINUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 39/120) | 39 |
| dark_sar_arms | ok | no open arms; covering 2543/2562 signals (99%) | 0 |
| depth_feed | ok | 49/49 books fresh (stale 0, never 0, thin 0); 51345693 msgs, 0 rejected | 0 |
| deriv_recorder | ok | hour recorded, 77 rows | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.59R (bound 0.3) (streak 422/6) | 422 |
| emission_controller | ok | last cycle 7s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=928, MOVER_AVWAP_SCALP=329, MOVER_TREND_PULLBACK=3409, RANGE_FADE=996, TREND_PULLBACK_EMA=338), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 4 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won,TREND_PULLBACK_EMA.campaign_prev_age_h,TREND_PULLBACK_EMA.campaign_prev_won) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 10/6) | 10 |
| firestore_read_budget | ok | 1,316 reads/day of 50,000 [engine 1,295, signing 21]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 5880 sealed bars over 49 symbols; 2024 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | counter reset | 0 |
| geometry_ab | ok | output +9 / upstream +97 | 0 |
| htf_candles | ok | BTCUSDT 1d/1w current | 0 |
| indicator_cache_key | ok | 182782 frozen value(s) avoided; 328553 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.32R over n=5736 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +97 but output +0 (streak 2/72) | 2 |
| mover_admission_metadata | ok | 956 symbols known, 247 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 7 held, 7 with scan counts, 6 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 6 locked / 6 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2231 rows held, 3792281 evicted (sampled: execution:trigger_not_confirmed 279/1333282, execution:overextended 279/1162554, setup_compat:regime_STRONG_TREND 279/656742) | 0 |
| price_action_lane | ok | 714020 evaluated, 1383 emitted; layer1 1383 stamped / 0 blind; cooldown=95251, delta_opposed=66057, no_footprint=277213, no_opposing_target=1600, no_sweep=213484, rr_below_floor=59032 | 0 |
| promoted_pair_integrity | ok | 7/7 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 646 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.30R over n=3239, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 19/6) | 19 |
| range_fade_path | ok | output +27 / upstream +97 | 0 |
| sar_alignment_crosscheck | ok | 902/41248 disagreed (2.2%) | 0 |
| sar_exit_shadow | ok | output +8 / upstream +97 | 0 |
| sar_hold_arm | ok | 1881 held arms settled, 119 unscored, 59 still walking (49 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 1/52 unfetchable (2%); top cause: located bar does not contain the stamp; symbols: PIEVERSEUSDT | 0 |
| sar_live_arms | ok | 59 arms current, none stalled; covering 1133/1133 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 2 resolved, 49 still mid-window | 0 |
| scan_cycle | ok | last 10.24s, worst 319.04s over 8154 lifetime cycles; lifetime 569 over 60s, 162 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.46s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 348303 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 8m ago | 0 |
| snapshot_writer | ok | last cycle 148s ago (0.27s to run, worst 212.03s), 1776 overrun(s) of 8647 cycles, TTL 900s; slowest router_delivery=33.43s, tickers=20.94s, data_intake=17.67s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=28, gate reads=0, withheld=28) | 0 |
| staleness_v2_shadow | ok | counter reset | 0 |
| strategy_edge | ok | output +69 / upstream +97 | 0 |
| structural_snap | ok | 6000/6000 measured, 33 blind, 0 levels moved (refusals: redetect_cooldown=2189) | 0 |
| structural_veto_lane | ok | 4171 stamped; 0 with no readable level book, 347 with clear air ahead, 2884 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +97 / upstream +22 | 0 |
| tuned_variants | violating | 417 non-stamps — atr_arm_uncomputable=417 (seen=16860 stamped=2646 skipped=13797) (streak 422/6) | 422 |
| unlock_shorts | ok | 15 open, 45 scheduled, calendar 9.7h old | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1302836`
- `Path funnel` emissions: `30`
- `Regime distribution` emissions: `30`
- `QUIET_SCALP_BLOCK` events: `293`
- `confidence_gate` events: `5755`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **34**
- Total REST-fallback activations: **2**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 3 | 15139 | 15139 | 17470 | 0 |
| futures_aggtrade | 21 | 10295 | 16505 | 17315 | 0 |
| futures_depth | 5 | 16883 | 17298 | 22521 | 0 |
| futures_liq | 5 | 3688 | 5836 | 7367 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 2 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=192641] state[populated=192641] buckets[many=192641] sources[none] quality[none]
- funding_rate: presence[absent=25061, present=167580] state[empty=25061, populated=167580] buckets[few=167580, none=25061] sources[none] quality[none]
- liquidation_clusters: presence[absent=120912, present=71729] state[empty=120912, populated=71729] buckets[few=60970, none=120912, some=10759] sources[none] quality[none]
- oi_snapshot: presence[absent=25060, present=167581] state[empty=25060, populated=167581] buckets[few=145, many=166693, none=25060, some=743] sources[none] quality[none]
- order_book: presence[absent=82182, present=110459] state[populated=110459, unavailable=82182] buckets[few=110459, none=82182] sources[book_ticker=110459, unavailable=82182] quality[none=82182, top_of_book_only=110459]
- orderblocks: presence[absent=192641] state[empty=192641] buckets[none=192641] sources[measured_dark=192641] quality[none]
- recent_ticks: presence[present=192641] state[populated=192641] buckets[many=192641] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.318912029266357` sec
- Median create→first breach: `5195.787942528725` sec
- Median create→terminal: `5195.787989139557` sec
- Median first breach→terminal: `7.367134094238281e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 2.777939634075271 | 3.0 | 0.9259798780250903 | 0 | 1 |
| DIVERGENCE_CONTINUATION | 2 | 2 | 2.053268472561948 | 2.2799698992278508 | 0.9005061557086613 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 1.295841201214311 | 1.9233777982348546 | 0.7004092068762278 | 0 | 2 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 1.285583010006119 | 3.0 | 0.4285276700020397 | 0 | 1 |
| MOVER_AVWAP_SCALP | 2 | 2 | 3.828871967692055 | 2.990100000000001 | 1.2803720223498292 | 2 | 0 |
| MOVER_TREND_PULLBACK | 28 | 28 | 3.722670904878229 | 3.0 | 1.2468962519011588 | 21 | 7 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 1.3812127068655524 | 1.5073726613517566 | 0.9389048250412793 | 0 | 5 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 4.6148467544575285 | 4.166909451112927 | 0 | 0 | 0 | 1 | 0 | 0 |
| DIVERGENCE_CONTINUATION | 2 | 3.7610271635651014 | 3.07990501937897 | 0 | 0 | 0 | 2 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 2 | 2.289516486502293 | 2.2220674303702763 | 0 | 0 | 0 | 1 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 3.6246681641821565 | 3.7790790279763073 | 1 | 0 | 0 | 0 | 0 | 0 |
| MOVER_AVWAP_SCALP | 2 | 3.828889325546725 | 3.95967 | 1 | 0 | 0 | 0 | 0 | 1 |
| MOVER_TREND_PULLBACK | 28 | 4.310573666017911 | 3.9425119594358873 | 10 | 4 | 2 | 18 | 2 | 0 |
| QUIET_COMPRESSION_BREAK | 6 | 3.3637036436051315 | 2.2488705109305585 | 1 | 0 | 0 | 4 | 1 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 4.1669 | 36739.34015202522 | 36743.32759690285 |
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 9111.413809537888 | 9111.413871526718 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 1.1132 | 25956.73688852787 | 25956.979623556137 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -3.0 | 14119.657878875732 | 14119.657981872559 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 5789.053855538368 | 5789.05392062664 |
| MOVER_TREND_PULLBACK | 28 | 28 | 39.3 | 32.1 | 39.3 | 0.0 | 0.7407 | 3871.870978951454 | 3871.8710235357285 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 16.7 | 50.0 | 16.7 | 0.0 | -0.4582 | 26741.301077485085 | 26741.301115989685 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 95 | 6 | 61 | 0.0 | 0.0 | None | None | 34 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 642 | 20 | 438 | 0.0 | 0.0 | None | None | 204 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-586`
- Gating Δ: `-22024`
- No-generation Δ: `-434754`
- Fast failures Δ: `-2`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": 3.8148, "current_avg_pnl": 4.1669, "current_win_rate": 100.0, "previous_avg_pnl": 0.3521, "previous_win_rate": 33.3, "win_rate_delta": 66.7}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.8262, "current_avg_pnl": 0.0, "current_win_rate": 0.0, "previous_avg_pnl": 0.8262, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -1.7013, "current_avg_pnl": 1.1132, "current_win_rate": 50.0, "previous_avg_pnl": 2.8145, "previous_win_rate": 75.0, "win_rate_delta": -25.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -4.8887, "current_avg_pnl": -3.0, "current_win_rate": 0.0, "previous_avg_pnl": 1.8887, "previous_win_rate": 100.0, "win_rate_delta": -100.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.0396, "current_avg_pnl": 0.7407, "current_win_rate": 39.3, "previous_avg_pnl": 0.7803, "previous_win_rate": 27.8, "win_rate_delta": 11.5}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -3.2336, "current_avg_pnl": -0.4582, "current_win_rate": 16.7, "previous_avg_pnl": 2.7754, "previous_win_rate": 100.0, "win_rate_delta": -83.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -2, "geometry_changed_delta": 0, "geometry_preserved_delta": -100, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -7, "geometry_changed_delta": 0, "geometry_preserved_delta": -143, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
