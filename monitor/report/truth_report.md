# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, LIQUIDITY_SWEEP_REVERSAL, DIVERGENCE_CONTINUATION
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `5` sec (warning=False)
- Latest performance record age: `2881` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 69 | 69 | 54 | 4 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 12096 | 12096 | 10572 | 21 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 95043 | 95045 | 15 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 96488 | 96488 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 96247 | 93215 | 3262 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 96511 | 95508 | 1084 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 96358 | 96157 | 224 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 84257 | 84270 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 96603 | 96633 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 96644 | 92955 | 4769 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 99999 | 106607 | 1004 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 95062 | 84843 | 15107 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 95940 | 95940 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 96492 | 96507 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 96231 | 96147 | 96 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 97729 | 93775 | 5223 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 95790 | 96106 | 93 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 83798 | 80229 | 3833 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 84073 | 83599 | 535 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 95009 | 95007 | 29 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 84273 | 84254 | 52 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3419 | 3419 | 2549 | 23 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 884 | 884 | 438 | 4 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 14 | 14 | 13 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 20522 | 20522 | 18964 | 54 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 7 | 7 | 3 | 3 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 11293 | 11293 | 8163 | 5 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2632 | 2632 | 382 | 43 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 40549 | 40549 | 21309 | 298 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 13 | 13 | 8 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 389 | 389 | 160 | 25 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 12999 | 12999 | 8648 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 385 | 385 | 142 | 7 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2013 | 2013 | 1706 | 25 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 110 | 110 | 10 | 5 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 4002 | 4002 | 229 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=95045): breakout_not_found=46645, basic_filters_failed=31972, move_not_fresh=12197, breakout_stale=3164, retest_proximity_failed=839, volume_spike_missing=208, missing_fvg_or_orderblock=17, move_exhausted=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=96489): cls_disabled_merged_into_lsr=96489
- **EVAL::DIVERGENCE_CONTINUATION** (total=93216): cvd_divergence_failed=31019, basic_filters_failed=28921, h1_trend_not_aligned=27699, ema_alignment_reject=4060, retest_proximity_failed=1057, missing_fvg_or_orderblock=460
- **EVAL::FAILED_AUCTION_RECLAIM** (total=95509): auction_not_detected=56118, basic_filters_failed=28648, reclaim_hold_failed=5807, tail_too_small=3449, regime_blocked=1464, rsi_reject=23
- **EVAL::FUNDING_EXTREME** (total=96158): funding_not_extreme=63558, basic_filters_failed=28561, ema_alignment_reject=1567, missing_funding_rate=1224, rsi_reject=865, momentum_reject=200, cvd_divergence_failed=167, missing_fvg_or_orderblock=16
- **EVAL::LIQUIDATION_REVERSAL** (total=84270): cascade_threshold_not_met=54996, basic_filters_failed=28743, cvd_divergence_failed=279, rsi_reject=214, missing_fvg_or_orderblock=34, volume_spike_missing=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=96634): no_ma_cross=65641, basic_filters_failed=28938, ma_cross_htf_misaligned=1664, ma_cross_cooldown=391
- **EVAL::MEAN_REVERT** (total=92956): no_extension=78132, basic_filters_failed=14824
- **EVAL::MOVER_AVWAP_SCALP** (total=106608): no_avwap_tag=51928, basic_filters_failed=32184, no_mover_leg=14839, avwap_slope_against=4342, avwap_reclaim_no_volume=2038, no_avwap_reclaim=1260, anchor_too_recent=17
- **EVAL::MOVER_TREND_PULLBACK** (total=84843): basic_filters_failed=32072, mover_run_too_small=30533, no_reclaim=19990, no_pullback_tag=2248
- **EVAL::OPENING_RANGE_BREAKOUT** (total=95941): feature_disabled=95941
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=96508): regime_blocked=52368, breakout_not_found=30574, basic_filters_failed=9626, adx_reject=3881, ema_alignment_reject=59
- **EVAL::QUIET_COMPRESSION_BREAK** (total=96148): regime_blocked=45509, compression_not_detected=28413, basic_filters_failed=19013, breakout_not_detected=2905, volume_confirmation_failed=226, rsi_reject=74, missing_fvg_or_orderblock=8
- **EVAL::RANGE_FADE** (total=93776): no_range_edge=78950, basic_filters_failed=14826
- **EVAL::SR_FLIP_RETEST** (total=96107): flip_close_not_confirmed=58681, basic_filters_failed=28620, long_break_volume_thin=2473, h1_break_not_confirmed=2255, retest_out_of_zone=1965, regime_blocked=1452, reclaim_hold_failed=432, long_acceptance_not_held=99, ema_alignment_reject=66, wick_quality_failed=32, whipsaw_flip=32
- **EVAL::STANDARD** (total=80229): momentum_reject=31417, adx_reject=15549, basic_filters_failed=12022, sweeps_not_detected=8154, macd_reject=6327, ema_alignment_reject=4783, htf_poi_unanchored=1763, rsi_reject=107, invalid_sl_geometry=94, mtf_reject=13
- **EVAL::TREND_PULLBACK** (total=83599): h1_trend_not_aligned=32042, h1_pullback_not_confirmed=16484, basic_filters_failed=13576, ema_alignment_reject=6447, ema_not_tested_prev=5145, no_ema_reclaim_close=4052, body_conviction_fail=2175, rsi_reject=2115, no_prev_low_break=501, prev_already_below_emas=377, prev_already_above_emas=302, no_prev_high_break=136, momentum_flat=112, ema21_not_tagged=65, missing_fvg_or_orderblock=61, momentum_reject=9
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=95007): breakout_not_found=44545, basic_filters_failed=31967, move_not_fresh=12951, breakout_stale=3748, retest_proximity_failed=1534, volume_spike_missing=246, missing_fvg_or_orderblock=16
- **EVAL::WHALE_MOMENTUM** (total=84254): momentum_reject=62638, recent_ticks_insufficient=12725, basic_filters_failed=8891

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=241): setup_compat:regime_VOLATILE_UNSUITABLE=232, setup_compat:regime_BREAKOUT_EXPANSION=9
- **FAILED_AUCTION_RECLAIM** (total=1444): setup_compat:regime_STRONG_TREND=905, execution:overextended=539
- **FUNDING_EXTREME_SIGNAL** (total=766): execution:trigger_not_confirmed=766
- **LIQUIDATION_REVERSAL** (total=14): execution:trigger_not_confirmed=14
- **LIQUIDITY_SWEEP_REVERSAL** (total=6593): setup_compat:regime_STRONG_TREND=2340, execution:trigger_not_confirmed=2218, execution:overextended=2035
- **MA_CROSS_TREND_SHIFT** (total=8): setup_compat:regime_DIRTY_RANGE=3, execution:overextended=3, execution:trigger_not_confirmed=2
- **MEAN_REVERT** (total=6373): setup_compat:regime_STRONG_TREND=3048, setup_compat:regime_WEAK_TREND=2604, execution:overextended=718, entry_quality=3
- **MOVER_AVWAP_SCALP** (total=1432): execution:overextended=859, execution:trigger_not_confirmed=401, entry_quality=172
- **MOVER_TREND_PULLBACK** (total=14947): execution:trigger_not_confirmed=7522, execution:overextended=4546, entry_quality=2879
- **RANGE_FADE** (total=9068): setup_compat:regime_STRONG_TREND=4463, setup_compat:regime_WEAK_TREND=3003, setup_compat:regime_VOLATILE_UNSUITABLE=893, execution:overextended=598, context_edge=81, setup_compat:regime_BREAKOUT_EXPANSION=30
- **TREND_PULLBACK_EMA** (total=1702): setup_compat:regime_CLEAN_RANGE=852, setup_compat:regime_DIRTY_RANGE=739, entry_quality=95, setup_compat:regime_VOLATILE_UNSUITABLE=16
- **VOLUME_SURGE_BREAKOUT** (total=37): execution:overextended=37
- **WHALE_MOMENTUM** (total=2672): execution:trigger_not_confirmed=2671, execution:overextended=1

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 206524 | 37.5% |
| TRENDING_UP | 126688 | 23.0% |
| TRENDING_DOWN | 100317 | 18.2% |
| QUIET | 100293 | 18.2% |
| VOLATILE | 17233 | 3.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **246**
- Average confidence gap to threshold: **11.08** (samples=246) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=28, PUMPUSDT=22, LINKUSDT=22, ENAUSDT=21, TAOUSDT=20, SOLUSDT=19, ARBUSDT=17, ADAUSDT=11, PENGUUSDT=11, BCHUSDT=10

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 5 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 331 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 1 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 194 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 208 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 19 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 92 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 43 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 11 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 168 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 27 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 267 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 3 |
| MEAN_REVERT | filtered | min_confidence | 332 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 12 |
| MEAN_REVERT | kept | min_confidence_pass | 8 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 336 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 15 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 1281 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 3638 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 100 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 6220 |
| POST_DISPLACEMENT_CONTINUATION | filtered | min_confidence | 5 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 45 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 21 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 159 |
| SR_FLIP_RETEST | filtered | min_confidence | 29 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 43 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 44 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 12 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 117 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 67 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 29 |
| WHALE_MOMENTUM | filtered | min_confidence | 76 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 28 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 5 | 67.32 | 65.00 | -2.32 | 18.34 | 17.66 | 20.00 | 4.20 | 8.62 |
| DIVERGENCE_CONTINUATION | filtered | 332 | 54.66 | 63.86 | 9.20 | 19.90 | 19.43 | 18.06 | 1.53 | 14.77 |
| DIVERGENCE_CONTINUATION | kept | 194 | 68.82 | 65.00 | -3.82 | 20.63 | 19.53 | 17.66 | 1.74 | 1.86 |
| FAILED_AUCTION_RECLAIM | filtered | 227 | 53.12 | 64.17 | 11.05 | 21.41 | 19.40 | 20.00 | 3.01 | 14.17 |
| FAILED_AUCTION_RECLAIM | kept | 92 | 70.59 | 65.00 | -5.59 | 20.84 | 19.42 | 20.00 | 4.15 | 2.04 |
| FUNDING_EXTREME_SIGNAL | filtered | 43 | 37.92 | 63.88 | 25.96 | 19.93 | 14.44 | 16.76 | 3.33 | 16.63 |
| FUNDING_EXTREME_SIGNAL | kept | 11 | 66.35 | 65.00 | -1.35 | 20.56 | 17.16 | 16.87 | 2.27 | 1.45 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 195 | 59.55 | 65.00 | 5.45 | 21.15 | 18.16 | 18.71 | 3.27 | 7.58 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 267 | 69.71 | 65.00 | -4.71 | 21.83 | 18.68 | 17.97 | 1.45 | 0.90 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 70.40 | 65.00 | -5.40 | 20.67 | 15.60 | 15.80 | 0.00 | 1.60 |
| MEAN_REVERT | filtered | 344 | 54.26 | 64.87 | 10.61 | 19.75 | 15.76 | 17.18 | 0.00 | 12.55 |
| MEAN_REVERT | kept | 8 | 73.46 | 65.00 | -8.46 | 20.88 | 15.48 | 16.15 | 0.00 | 1.43 |
| MOVER_AVWAP_SCALP | filtered | 353 | 55.23 | 60.40 | 5.17 | 19.99 | 15.07 | 15.80 | 4.04 | 15.92 |
| MOVER_AVWAP_SCALP | kept | 1281 | 80.83 | 65.00 | -15.83 | 20.37 | 17.28 | 15.80 | 4.23 | 2.34 |
| MOVER_TREND_PULLBACK | filtered | 3738 | 52.18 | 64.29 | 12.11 | 19.85 | 18.79 | 15.80 | 4.18 | 15.91 |
| MOVER_TREND_PULLBACK | kept | 6220 | 76.27 | 65.00 | -11.27 | 20.34 | 18.66 | 15.80 | 4.18 | 1.58 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 5 | 58.40 | 61.00 | 2.60 | 20.90 | 20.00 | 16.00 | 4.50 | 18.10 |
| QUIET_COMPRESSION_BREAK | filtered | 66 | 56.80 | 65.00 | 8.20 | 20.75 | 19.13 | 20.00 | 0.00 | 7.86 |
| QUIET_COMPRESSION_BREAK | kept | 159 | 75.29 | 65.00 | -10.29 | 21.04 | 19.36 | 20.00 | 0.00 | 1.00 |
| SR_FLIP_RETEST | filtered | 29 | 60.92 | 65.00 | 4.08 | 23.16 | 20.00 | 15.20 | 1.00 | 5.51 |
| SR_FLIP_RETEST | kept | 43 | 71.32 | 65.00 | -6.32 | 19.78 | 20.00 | 15.55 | 2.31 | 1.28 |
| TREND_PULLBACK_EMA | filtered | 56 | 58.08 | 65.00 | 6.92 | 20.53 | 18.89 | 18.68 | 4.54 | 15.20 |
| TREND_PULLBACK_EMA | kept | 117 | 79.23 | 65.00 | -14.23 | 21.93 | 19.75 | 17.54 | 4.80 | 3.62 |
| VOLUME_SURGE_BREAKOUT | filtered | 67 | 46.38 | 64.28 | 17.90 | 19.04 | 15.77 | 20.00 | 3.87 | 13.90 |
| VOLUME_SURGE_BREAKOUT | kept | 29 | 73.78 | 65.00 | -8.78 | 20.21 | 17.80 | 20.00 | 4.26 | 5.11 |
| WHALE_MOMENTUM | filtered | 104 | 46.58 | 64.08 | 17.50 | 24.30 | 16.10 | 17.00 | 0.00 | 16.75 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 5 | 67.32 | 17.80 | 16.40 | 12.60 | 12.20 | 5.00 | 7.74 | 4.20 |
| DIVERGENCE_CONTINUATION | filtered | 332 | 54.66 | 20.71 | 13.93 | 6.61 | 12.59 | 4.92 | 9.12 | 1.53 |
| DIVERGENCE_CONTINUATION | kept | 194 | 68.82 | 23.19 | 14.08 | 5.95 | 12.74 | 4.41 | 9.06 | 1.74 |
| FAILED_AUCTION_RECLAIM | filtered | 227 | 53.12 | 20.99 | 16.41 | 6.01 | 12.66 | 7.33 | 4.50 | 3.01 |
| FAILED_AUCTION_RECLAIM | kept | 92 | 70.59 | 23.24 | 17.17 | 4.34 | 12.36 | 6.76 | 4.78 | 4.15 |
| FUNDING_EXTREME_SIGNAL | filtered | 43 | 37.92 | 23.70 | 8.47 | 3.77 | 13.84 | 7.84 | 5.41 | 3.33 |
| FUNDING_EXTREME_SIGNAL | kept | 11 | 66.35 | 23.55 | 10.91 | 4.36 | 12.27 | 8.14 | 7.12 | 2.27 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 195 | 59.55 | 20.29 | 14.00 | 5.92 | 12.48 | 5.72 | 5.41 | 3.27 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 267 | 69.71 | 23.43 | 14.57 | 4.29 | 13.31 | 6.24 | 7.46 | 1.45 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 70.40 | 22.33 | 14.00 | 8.00 | 14.00 | 5.33 | 8.33 | 0.00 |
| MEAN_REVERT | filtered | 344 | 54.26 | 23.94 | 14.41 | 10.67 | 12.18 | 5.00 | 3.00 | 0.00 |
| MEAN_REVERT | kept | 8 | 73.46 | 24.00 | 16.50 | 13.12 | 12.75 | 4.69 | 3.83 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 353 | 55.23 | 18.20 | 18.05 | 11.57 | 13.19 | 7.07 | 6.08 | 4.04 |
| MOVER_AVWAP_SCALP | kept | 1281 | 80.83 | 19.06 | 18.00 | 12.82 | 13.54 | 5.91 | 9.65 | 4.23 |
| MOVER_TREND_PULLBACK | filtered | 3738 | 52.18 | 18.54 | 18.04 | 7.76 | 11.96 | 6.25 | 8.21 | 4.18 |
| MOVER_TREND_PULLBACK | kept | 6220 | 76.27 | 19.39 | 18.02 | 8.21 | 12.61 | 6.57 | 9.25 | 4.18 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 5 | 58.40 | 15.00 | 18.00 | 12.00 | 14.00 | 5.00 | 8.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 66 | 56.80 | 17.24 | 16.73 | 9.95 | 14.00 | 6.41 | 5.13 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 159 | 75.29 | 18.36 | 16.89 | 11.72 | 14.94 | 6.91 | 8.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 29 | 60.92 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 8.33 | 1.00 |
| SR_FLIP_RETEST | kept | 43 | 71.32 | 23.14 | 18.00 | 3.49 | 11.81 | 5.08 | 9.46 | 2.31 |
| TREND_PULLBACK_EMA | filtered | 56 | 58.08 | 17.59 | 18.00 | 9.35 | 16.04 | 6.30 | 8.91 | 4.54 |
| TREND_PULLBACK_EMA | kept | 117 | 79.23 | 21.65 | 18.00 | 7.50 | 14.04 | 7.71 | 9.64 | 4.80 |
| VOLUME_SURGE_BREAKOUT | filtered | 67 | 46.38 | 17.72 | 15.97 | 12.13 | 14.04 | 5.96 | 5.58 | 3.87 |
| VOLUME_SURGE_BREAKOUT | kept | 29 | 73.78 | 17.28 | 15.66 | 13.45 | 13.97 | 5.00 | 9.29 | 4.26 |
| WHALE_MOMENTUM | filtered | 104 | 46.58 | 22.63 | 8.00 | 9.89 | 12.74 | 7.15 | 7.40 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 5 | 67.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 332 | 54.66 | 0.00 | 0.00 | 0.29 | 0.00 | 0.07 | 0.24 | 0.00 | 0.00 | **0.60** |
| DIVERGENCE_CONTINUATION | kept | 194 | 68.82 | 0.00 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.23** |
| FAILED_AUCTION_RECLAIM | filtered | 227 | 53.12 | 0.00 | 0.00 | 0.95 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | **1.04** |
| FAILED_AUCTION_RECLAIM | kept | 92 | 70.59 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 43 | 37.92 | 0.00 | 0.00 | 5.21 | 0.00 | 0.28 | 0.00 | 0.00 | 0.00 | **5.49** |
| FUNDING_EXTREME_SIGNAL | kept | 11 | 66.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 195 | 59.55 | 0.00 | 0.00 | 0.49 | 0.00 | 1.99 | 0.00 | 0.00 | 0.00 | **2.48** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 267 | 69.71 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | **0.04** |
| MA_CROSS_TREND_SHIFT | kept | 3 | 70.40 | 0.00 | 0.00 | 1.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.60** |
| MEAN_REVERT | filtered | 344 | 54.26 | 0.00 | 0.00 | 0.00 | 0.00 | 6.52 | 0.03 | 0.00 | 0.00 | **6.55** |
| MEAN_REVERT | kept | 8 | 73.46 | 0.00 | 0.00 | 0.00 | 0.00 | 1.80 | 0.00 | 0.00 | 0.00 | **1.80** |
| MOVER_AVWAP_SCALP | filtered | 353 | 55.23 | 0.30 | 0.00 | 0.00 | 0.00 | 1.29 | 0.21 | 0.00 | 1.01 | **2.81** |
| MOVER_AVWAP_SCALP | kept | 1281 | 80.83 | 0.00 | 0.00 | 0.20 | 0.00 | 0.01 | 0.17 | 0.00 | 0.07 | **0.45** |
| MOVER_TREND_PULLBACK | filtered | 3738 | 52.18 | 0.88 | 0.00 | 0.60 | 0.00 | 0.57 | 0.05 | 0.00 | 0.00 | **2.10** |
| MOVER_TREND_PULLBACK | kept | 6220 | 76.27 | 0.04 | 0.00 | 0.14 | 0.00 | 0.14 | 0.05 | 0.00 | 0.01 | **0.38** |
| POST_DISPLACEMENT_CONTINUATION | filtered | 5 | 58.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 66 | 56.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.39 | 0.00 | 0.00 | 0.84 | **1.23** |
| QUIET_COMPRESSION_BREAK | kept | 159 | 75.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.04 | **0.09** |
| SR_FLIP_RETEST | filtered | 29 | 60.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 43 | 71.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 56 | 58.08 | 0.00 | 0.00 | 0.14 | 0.00 | 4.63 | 0.00 | 0.00 | 0.00 | **4.77** |
| TREND_PULLBACK_EMA | kept | 117 | 79.23 | 0.00 | 0.00 | 1.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.48** |
| VOLUME_SURGE_BREAKOUT | filtered | 67 | 46.38 | 0.00 | 0.00 | 0.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.27 | **1.23** |
| VOLUME_SURGE_BREAKOUT | kept | 29 | 73.78 | 0.00 | 0.00 | 2.81 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.81** |
| WHALE_MOMENTUM | filtered | 104 | 46.58 | 0.00 | 0.00 | 0.00 | 0.00 | 3.62 | 0.00 | 0.00 | 0.00 | **3.62** |

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
- Outcomes recorded: **205147 held of 1025379 seen** across 21 strategies; 4651 cells past the sample floor; **2549 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 49592 | 601/48991/0 | 43% | -0.20 | ASIA/RANGE/NORMAL/BTC_RISING (+1.20R) | NY/QUIET/EXPANDED/BTC_FALLING/MAJOR (-1.26R) |
| MOVER_AVWAP_SCALP | 26866 | 190/26676/0 | 45% | -0.17 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 16738 | 282/16456/0 | 48% | -0.10 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.86R) | NY/MARKUP/NORMAL/BTC_NEUTRAL (-1.19R) |
| FAILED_AUCTION_RECLAIM | 15680 | 213/15467/0 | 36% | -0.30 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+1.69R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 14888 | 86/14802/0 | 38% | -0.31 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 12109 | 156/11953/0 | 39% | -0.40 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.91R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9928 | 525/9403/0 | 45% | -0.10 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8551 | 0/0/8551 | 41% | -0.13 | OVERLAP/MARKUP/CASCADE/BTC_RISING (+1.58R) | OVERLAP/MARKDOWN/EXPANDED/BTC_FALLING (-0.95R) |
| SHADOW_RANGE_FADE | 8114 | 0/0/8114 | 35% | -0.16 | ASIA/MARKDOWN/NORMAL/BTC_FALLING (+1.00R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.33R) |
| SR_FLIP_RETEST | 7828 | 31/7797/0 | 47% | -0.27 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.30R) |
| SHADOW_FUNDING_FADE | 7750 | 0/0/7750 | 35% | -0.39 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (-0.01R) | OFF_HOURS/RANGE/NORMAL/BTC_RISING (-0.95R) |
| MEAN_REVERT | 6133 | 83/6050/0 | 36% | -0.32 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.60R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4857 | 4/4853/0 | 33% | -0.40 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+0.95R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.30R) |
| WHALE_MOMENTUM | 4500 | 4/4496/0 | 47% | -0.27 | NY/RANGE/EXPANDED/BTC_FALLING (+0.94R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 4488 | 0/4488/0 | 31% | -0.32 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/NORMAL/BTC_FALLING/ALTCOIN (-1.19R) |
| RANGE_FADE | 3515 | 6/3509/0 | 52% | +0.25 | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (+3.08R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.78R) |
| SHADOW_CASCADE_REVERSAL | 1831 | 0/0/1831 | 52% | -0.08 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.17R) | OVERLAP/MARKDOWN/EXPANDED/BTC_FALLING (-0.53R) |
| BREAKDOWN_SHORT | 837 | 84/753/0 | 36% | -0.24 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 588 | 0/588/0 | 34% | -0.30 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 266 | 42/224/0 | 45% | -0.15 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 88 | 8/80/0 | 36% | +0.04 | — | — |

- **Strongest cells**: `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.08R (n=37, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.00R (n=32, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.78R (n=47, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 490 | 28% / -0.54R | 490 | 52% / -0.09R | +0.44 | **ATR** |
| TREND_PULLBACK_EMA | 1546 | 38% / -0.37R | 1546 | 50% / -0.08R | +0.28 | **ATR** |
| LIQUIDATION_REVERSAL | 36 | 28% / -0.55R | 36 | 47% / -0.30R | +0.24 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1973 | 44% / -0.34R | 1973 | 57% / -0.11R | +0.24 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 258 | 37% / -0.16R | 258 | 49% / -0.03R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 889 | 48% / -0.25R | 889 | 52% / -0.13R | +0.13 | **ATR** |
| MA_CROSS_TREND_SHIFT | 82 | 48% / -0.13R | 82 | 52% / -0.01R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 9404 | 47% / -0.14R | 9404 | 53% / -0.03R | +0.11 | **ATR** |
| MOVER_AVWAP_SCALP | 3066 | 47% / -0.12R | 3066 | 53% / -0.03R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 491 | 47% / -0.29R | 491 | 49% / -0.19R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1801 | 41% / -0.21R | 1801 | 43% / -0.13R | +0.09 | **ATR** |
| BREAKDOWN_SHORT | 65 | 42% / -0.15R | 65 | 46% / -0.08R | +0.07 | **ATR** |
| DIVERGENCE_CONTINUATION | 2279 | 48% / -0.12R | 2279 | 52% / -0.06R | +0.06 | **ATR** |
| RANGE_FADE | 200 | 44% / +0.04R | 200 | 50% / +0.09R | +0.05 | **ATR** |
| MEAN_REVERT | 560 | 45% / -0.19R | 560 | 44% / -0.20R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 16 | 50% / -0.08R | 16 | 50% / -0.08R | -0.00 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1778 | 49% / -0.08R | 1778 | 49% / -0.08R | +0.00 | **ATR** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12474 | 27% | -0.22R | 314 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 3066 | 51% | -0.02R | 246 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 163 | 48% | -0.04R | 77 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1978 | 33% / -0.15R | +0.91 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 2288 | 40% / -0.13R | +0.88 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3655 | 36% / -0.13R | +0.71 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11490 | 36% / -0.15R | +0.38 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2623 | 36% / -0.13R | +0.15 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 176 | 34% / -0.38R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1719 | 37% / -0.09R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1505 | 32% / -0.28R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 384 | 33% / -0.19R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 605 | 31% / -0.27R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 455 | 47% / -0.09R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 109 | 45% / +0.13R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 142 | 45% / -0.00R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 762 | 36% / -0.24R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 130 | 32% / +0.11R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 48 | 42% / -0.35R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 32 | 44% / +0.34R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 64 · alerting: **3** · boot grace active: False
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.50R (bound 0.3) (streak 23/6) (sustained 23 cycles)
- **ALERT** `range_fade_emission` — 469 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.25R over n=3509, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 23/6) (sustained 23 cycles)
- **ALERT** `tuned_variants` — 54 non-stamps — atr_arm_uncomputable=54 (seen=1590 stamped=115 skipped=1421) (streak 19/6) (sustained 19 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 2826487 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 23 arms current, none stalled; covering 2031/2031 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| analyst_plan_cadence | ok | last plan 6m ago | 0 |
| atr_trail_live_arms | ok | 48 arms current, none stalled; covering 1035/1035 signals (100%) | 0 |
| auto_dispatch | ok | 9 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=9. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 161/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 60684.00 | 0 |
| candle_coverage | ok | 86/86 symbols with ≥20 15m candles, 86/86 updated within 45m [fresh=86; 75 Tier-1 futures + 11 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 929 dup bars, 0 undedupable; ws 0 out-of-order, 193 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 65 cohorts, 22 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +97 / upstream +18 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1070/1089 signals (98%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 2 promoted today, nothing refused | 0 |
| dark_resolution | ok | 106 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1068/1087 signals (98%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 854486 msgs, 0 rejected | 0 |
| deriv_recorder | ok | hour recorded, 75 rows | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.50R (bound 0.3) (streak 23/6) | 23 |
| emission_controller | ok | last cycle 987s ago; live_overrides=14 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=747, MOVER_AVWAP_SCALP=320, MOVER_TREND_PULLBACK=4632, RANGE_FADE=245, TREND_PULLBACK_EMA=56), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 4 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won,TREND_PULLBACK_EMA.campaign_prev_age_h,TREND_PULLBACK_EMA.campaign_prev_won) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: cvd_aligned=54, mover_stack_15m=16. Held back in this window: cvd_aligned=44, mover_stack_15m=3. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 3/6) | 3 |
| firestore_read_budget | ok | 1,373 reads/day of 50,000 [engine 1,350, signing 23]; top site keystore.roster_doc at 291/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +25 / upstream +213 | 0 |
| htf_candles | ok | BTCUSDT 1d/1w current | 0 |
| indicator_cache_key | ok | 1124 frozen value(s) avoided; 35069 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.33R over n=6050 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +18 / upstream +213 | 0 |
| mover_admission_metadata | ok | 956 symbols known, 247 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 11 held, 11 with scan counts, 10 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 11 locked / 11 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2196 rows held, 3916032 evicted (sampled: execution:trigger_not_confirmed 283/1368849, execution:overextended 283/1190990, setup_compat:regime_STRONG_TREND 283/686348) | 0 |
| price_action_lane | ok | 81836 evaluated, 88 emitted; layer1 88 stamped / 0 blind; cooldown=12027, delta_opposed=7083, no_footprint=28938, no_opposing_target=100, no_sweep=26950, rr_below_floor=6650 | 0 |
| promoted_pair_integrity | ok | 11/11 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 469 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.25R over n=3509, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 23/6) | 23 |
| range_fade_path | ok | output +9 / upstream +213 | 0 |
| sar_alignment_crosscheck | ok | 33/2462 disagreed (1.3%) | 0 |
| sar_exit_shadow | ok | output +12 / upstream +213 | 0 |
| sar_hold_arm | ok | 1870 held arms settled, 130 unscored, 46 still walking (38 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 24/111 unfetchable (22%); top cause: gap or duplicate bar in the 15m window; symbols: BLURUSDT, GUAUSDT, HBARUSDT, LITUSDT, MOODENGUSDT +5 more | 0 |
| sar_live_arms | ok | 46 arms current, none stalled; covering 1033/1033 signals (100%) | 0 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 1 resolved, 86 still mid-window | 0 |
| scan_cycle | ok | last 82.44s, worst 123.55s over 1035 lifetime cycles; lifetime 14 over 60s, 1 over 120s; recent 4/1 warn/kill breaches in 20/20 cycles; heartbeat age 16.34s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 28716 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 14s ago (14.0s to run, worst 96.32s), 75 overrun(s) of 625 cycles, TTL 900s; slowest user_positions=1.94s, desk=1.32s, data_intake=0.34s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +99 / upstream +213 | 0 |
| structural_snap | ok | 6000/6000 measured, 34 blind, 0 levels moved (refusals: redetect_cooldown=417) | 0 |
| structural_veto_lane | ok | 503 stamped; 0 with no readable level book, 3 with clear air ahead, 304 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +213 / upstream +18 | 0 |
| tuned_variants | violating | 54 non-stamps — atr_arm_uncomputable=54 (seen=1590 stamped=115 skipped=1421) (streak 19/6) | 19 |
| unlock_shorts | ok | 15 open, 48 scheduled, calendar 6.9h old | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2829339`
- `Path funnel` emissions: `70`
- `Regime distribution` emissions: `70`
- `QUIET_SCALP_BLOCK` events: `246`
- `confidence_gate` events: `13988`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **1**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 1 | 2107 | 2107 | 2107 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=377456] state[populated=377456] buckets[many=377456] sources[none] quality[none]
- funding_rate: presence[absent=26399, present=351057] state[empty=26399, populated=351057] buckets[few=351057, none=26399] sources[none] quality[none]
- liquidation_clusters: presence[absent=210099, present=167357] state[empty=210099, populated=167357] buckets[few=130701, none=210099, some=36656] sources[none] quality[none]
- oi_snapshot: presence[absent=25169, present=352287] state[empty=25169, populated=352287] buckets[few=222, many=350834, none=25169, some=1231] sources[none] quality[none]
- order_book: presence[absent=109454, present=268002] state[populated=268002, unavailable=109454] buckets[few=268002, none=109454] sources[book_ticker=268002, unavailable=109454] quality[none=109454, top_of_book_only=268002]
- orderblocks: presence[absent=377456] state[empty=377456] buckets[none=377456] sources[measured_dark=377456] quality[none]
- recent_ticks: presence[present=377456] state[populated=377456] buckets[many=377456] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.443719506263733` sec
- Median create→first breach: `4693.558352947235` sec
- Median create→terminal: `4693.977501511574` sec
- Median first breach→terminal: `8.797645568847656e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 5, "pct": 6.4}, "under_180s": {"count": 6, "pct": 7.7}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 4, "pct": 5.1}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 1.7618976259957473 | 2.336814919496678 | 0.6929673502581696 | 0 | 2 |
| DIVERGENCE_CONTINUATION | 7 | 7 | 0.8129151573033379 | 1.4504227760711916 | 0.574193685704148 | 0 | 7 |
| FAILED_AUCTION_RECLAIM | 8 | 8 | 1.241836701755413 | 1.4814083033996621 | 0.9001023482575362 | 0 | 8 |
| LIQUIDITY_SWEEP_REVERSAL | 14 | 14 | 1.077763064400072 | 1.3124902967435066 | 0.8792288082977359 | 0 | 12 |
| MEAN_REVERT | 2 | 2 | 1.8131707723961528 | 2.2209586832008013 | 0.7750778194038903 | 0 | 2 |
| MOVER_AVWAP_SCALP | 3 | 3 | 2.032578988413548 | 2.4239268752774077 | 0.8385479814364979 | 0 | 3 |
| MOVER_TREND_PULLBACK | 31 | 31 | 4.353597620186692 | 3.0 | 1.4511992067288972 | 23 | 8 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 1.6922648265395623 | 1.7238485981308258 | 0.8761013716050376 | 0 | 7 |
| SR_FLIP_RETEST | 1 | 1 | 1.1305973471022885 | 1.2929112795363342 | 0.8744585688104949 | 0 | 1 |
| TREND_PULLBACK_EMA | 1 | 1 | 2.083567562662629 | 3.0 | 0.694522520887543 | 0 | 1 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 4.2033174150876755 | 3.0558491604934694 | 0 | 0 | 0 | 1 | 0 | 1 |
| DIVERGENCE_CONTINUATION | 7 | 3.0655858511422234 | 3.0655858511422234 | 0 | 0 | 0 | 2 | 0 | 5 |
| FAILED_AUCTION_RECLAIM | 8 | 1.9866665124175347 | 1.862759860325418 | 4 | 0 | 0 | 4 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 14 | 1.9964329587230685 | 1.7797479322365803 | 2 | 0 | 0 | 9 | 3 | 3 |
| MEAN_REVERT | 2 | 2.5139553614986223 | 2.5914102154897143 | 2 | 2 | 0 | 0 | 0 | 0 |
| MOVER_AVWAP_SCALP | 3 | 2.253988413547236 | 3.048863636363623 | 2 | 0 | 0 | 1 | 0 | 0 |
| MOVER_TREND_PULLBACK | 31 | 6.509715318572072 | 4.02085737908227 | 7 | 1 | 1 | 23 | 4 | 1 |
| QUIET_COMPRESSION_BREAK | 9 | 4.236291496588927 | 2.5383913115648187 | 0 | 0 | 0 | 5 | 0 | 4 |
| SR_FLIP_RETEST | 1 | 2.4155019436778544 | 1.695896020653433 | 0 | 0 | 0 | 1 | 0 | 0 |
| TREND_PULLBACK_EMA | 1 | 4.712041884816761 | 4.712041884816761 | 0 | 0 | 0 | 0 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 10559.265966534615 | 10559.26601946354 |
| DIVERGENCE_CONTINUATION | 7 | 7 | 0.0 | 42.9 | 0.0 | 0.0 | -0.3378 | 104.71457099914551 | 104.71461391448975 |
| FAILED_AUCTION_RECLAIM | 8 | 8 | 0.0 | 100.0 | 0.0 | 0.0 | -1.4418 | 5793.412726998329 | 5793.413399934769 |
| LIQUIDITY_SWEEP_REVERSAL | 14 | 14 | 42.9 | 57.1 | 42.9 | 0.0 | -0.2163 | 3373.519254088402 | 3375.970528960228 |
| MEAN_REVERT | 2 | 2 | 100.0 | 0.0 | 100.0 | 0.0 | 2.5914 | 13943.071316599846 | 13943.774374008179 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.0 | -0.526 | 10838.407633781433 | 10838.407887935638 |
| MOVER_TREND_PULLBACK | 31 | 31 | 35.5 | 48.4 | 35.5 | 0.0 | 0.1807 | 4236.373552083969 | 4236.373597145081 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 33.3 | 22.2 | 33.3 | 0.0 | 0.5859 | 22125.319583177567 | 22125.31963300705 |
| SR_FLIP_RETEST | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.1306 | 2704.9006938934326 | 2704.9007148742676 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2328.90847492218 | 2328.908544063568 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 385 | 7 | 142 | 0.0 | 100.0 | 2704.9006938934326 | 2704.9007148742676 | 243 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2013 | 25 | 1706 | 0.0 | 0.0 | 2328.90847492218 | 2328.908544063568 | 307 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `88`
- Gating Δ: `649`
- No-generation Δ: `470800`
- Fast failures Δ: `5`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": 0.3946, "current_avg_pnl": 0.0, "current_win_rate": 0.0, "previous_avg_pnl": -0.3946, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.5849, "current_avg_pnl": -0.3378, "current_win_rate": 0.0, "previous_avg_pnl": -0.9227, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.7101, "current_avg_pnl": -1.4418, "current_win_rate": 0.0, "previous_avg_pnl": -0.7317, "previous_win_rate": 12.5, "win_rate_delta": -12.5}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -1.4216, "current_avg_pnl": -0.2163, "current_win_rate": 42.9, "previous_avg_pnl": 1.2053, "previous_win_rate": 100.0, "win_rate_delta": -57.1}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -2.3275, "current_avg_pnl": -0.526, "current_win_rate": 0.0, "previous_avg_pnl": 1.8015, "previous_win_rate": 50.0, "win_rate_delta": -50.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.5916, "current_avg_pnl": 0.1807, "current_win_rate": 35.5, "previous_avg_pnl": -0.4109, "previous_win_rate": 34.4, "win_rate_delta": 1.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.7976, "current_avg_pnl": 0.5859, "current_win_rate": 33.3, "previous_avg_pnl": -0.2117, "previous_win_rate": 20.0, "win_rate_delta": 13.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": -113, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2704.9, "median_terminal_delta_sec": 2704.9, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": 46, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2328.91, "median_terminal_delta_sec": 2328.91, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
