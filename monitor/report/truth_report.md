# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, MOVER_AVWAP_SCALP
- Top promising signals/paths: LIQUIDITY_SWEEP_REVERSAL, BREAKDOWN_SHORT
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `1986` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 86 | 86 | 45 | 5 | active-healthy (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 13051 | 13051 | 10542 | 28 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 92766 | 92755 | 30 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 92800 | 92800 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 92416 | 88387 | 4402 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 92830 | 91531 | 1391 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 92338 | 92222 | 146 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 79898 | 79899 | 16 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 92928 | 92960 | 13 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 92976 | 90219 | 3733 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 97296 | 105079 | 899 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 92788 | 84835 | 12408 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 91886 | 91886 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 92808 | 92818 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 92378 | 92229 | 180 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 93958 | 90962 | 3777 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 91888 | 92098 | 232 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 79280 | 73653 | 6151 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 79808 | 79369 | 523 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 92729 | 92747 | 14 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 79917 | 79887 | 63 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3804 | 3804 | 2846 | 9 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 441 | 441 | 97 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 69 | 69 | 30 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 25767 | 25767 | 24070 | 75 | active-healthy (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 25 | 25 | 7 | 4 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8689 | 8689 | 7425 | 4 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2085 | 2085 | 189 | 66 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 29849 | 29849 | 11756 | 408 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 29 | 29 | 28 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 709 | 709 | 107 | 36 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 8313 | 8313 | 7708 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 561 | 561 | 268 | 13 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1821 | 1821 | 1234 | 40 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 59 | 59 | 35 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 2984 | 2984 | 244 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=92755): breakout_not_found=41718, basic_filters_failed=29574, move_not_fresh=14878, breakout_stale=4831, retest_proximity_failed=1404, volume_spike_missing=315, move_exhausted=32, missing_fvg_or_orderblock=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=92800): cls_disabled_merged_into_lsr=92800
- **EVAL::DIVERGENCE_CONTINUATION** (total=88387): cvd_divergence_failed=33912, basic_filters_failed=25889, h1_trend_not_aligned=20279, ema_alignment_reject=6743, retest_proximity_failed=910, missing_fvg_or_orderblock=654
- **EVAL::FAILED_AUCTION_RECLAIM** (total=91531): auction_not_detected=53765, basic_filters_failed=25203, reclaim_hold_failed=6145, tail_too_small=3985, regime_blocked=2374, rsi_reject=59
- **EVAL::FUNDING_EXTREME** (total=92222): funding_not_extreme=62064, basic_filters_failed=25117, missing_funding_rate=2320, ema_alignment_reject=1482, rsi_reject=878, cvd_divergence_failed=189, momentum_reject=137, missing_fvg_or_orderblock=35
- **EVAL::LIQUIDATION_REVERSAL** (total=79899): cascade_threshold_not_met=53662, basic_filters_failed=25628, cvd_divergence_failed=326, rsi_reject=249, missing_fvg_or_orderblock=31, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=92960): no_ma_cross=64625, basic_filters_failed=25904, ma_cross_htf_misaligned=1274, ma_cross_cooldown=1157
- **EVAL::MEAN_REVERT** (total=90219): no_extension=73257, basic_filters_failed=16962
- **EVAL::MOVER_AVWAP_SCALP** (total=105079): no_avwap_tag=45298, basic_filters_failed=29784, no_mover_leg=19985, avwap_slope_against=5267, avwap_reclaim_no_volume=2974, no_avwap_reclaim=1700, anchor_too_recent=71
- **EVAL::MOVER_TREND_PULLBACK** (total=84835): mover_run_too_small=37214, basic_filters_failed=29669, no_reclaim=15508, no_pullback_tag=2444
- **EVAL::OPENING_RANGE_BREAKOUT** (total=91886): feature_disabled=91886
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=92818): regime_blocked=65425, breakout_not_found=17060, basic_filters_failed=8417, adx_reject=1873, ema_alignment_reject=43
- **EVAL::QUIET_COMPRESSION_BREAK** (total=92229): compression_not_detected=39524, regime_blocked=29675, basic_filters_failed=16778, breakout_not_detected=5692, volume_confirmation_failed=520, missing_fvg_or_orderblock=27, macd_reject=7, rsi_reject=6
- **EVAL::RANGE_FADE** (total=90962): no_range_edge=73991, basic_filters_failed=16971
- **EVAL::SR_FLIP_RETEST** (total=92098): flip_close_not_confirmed=54502, basic_filters_failed=25173, h1_break_not_confirmed=3191, retest_out_of_zone=2903, regime_blocked=2364, long_break_volume_thin=2028, reclaim_hold_failed=1281, ema_alignment_reject=349, wick_quality_failed=195, whipsaw_flip=88, long_acceptance_not_held=15, missing_fvg_or_orderblock=9
- **EVAL::STANDARD** (total=73653): momentum_reject=22401, adx_reject=16452, basic_filters_failed=13211, macd_reject=8905, sweeps_not_detected=7104, ema_alignment_reject=4350, htf_poi_unanchored=995, invalid_sl_geometry=180, rsi_reject=51, mtf_reject=4
- **EVAL::TREND_PULLBACK** (total=79369): h1_trend_not_aligned=26796, basic_filters_failed=12598, ema_alignment_reject=10672, h1_pullback_not_confirmed=10236, ema_not_tested_prev=6672, no_ema_reclaim_close=5148, body_conviction_fail=2567, rsi_reject=2490, prev_already_below_emas=933, no_prev_low_break=395, prev_already_above_emas=271, momentum_flat=248, no_prev_high_break=226, ema21_not_tagged=45, missing_fvg_or_orderblock=36, momentum_reject=36
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=92747): breakout_not_found=53120, basic_filters_failed=29572, move_not_fresh=6158, breakout_stale=2981, retest_proximity_failed=677, volume_spike_missing=206, missing_fvg_or_orderblock=29, move_exhausted=4
- **EVAL::WHALE_MOMENTUM** (total=79887): momentum_reject=65676, recent_ticks_insufficient=9734, basic_filters_failed=4477

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=69): setup_compat:regime_VOLATILE_UNSUITABLE=62, setup_compat:regime_BREAKOUT_EXPANSION=7
- **FAILED_AUCTION_RECLAIM** (total=940): context_floor=399, execution:overextended=374, setup_compat:regime_STRONG_TREND=124, setup_compat:regime_VOLATILE_UNSUITABLE=43
- **FUNDING_EXTREME_SIGNAL** (total=351): execution:trigger_not_confirmed=351
- **LIQUIDATION_REVERSAL** (total=69): execution:trigger_not_confirmed=69
- **LIQUIDITY_SWEEP_REVERSAL** (total=5073): execution:overextended=2355, execution:trigger_not_confirmed=1747, setup_compat:regime_STRONG_TREND=971
- **MA_CROSS_TREND_SHIFT** (total=22): setup_compat:regime_DIRTY_RANGE=12, execution:trigger_not_confirmed=6, setup_compat:regime_CLEAN_RANGE=3, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=2604): setup_compat:regime_STRONG_TREND=1286, execution:overextended=682, setup_compat:regime_WEAK_TREND=620, entry_quality=16
- **MOVER_AVWAP_SCALP** (total=1235): execution:overextended=593, entry_quality=368, execution:trigger_not_confirmed=274
- **MOVER_TREND_PULLBACK** (total=14183): execution:trigger_not_confirmed=7307, execution:overextended=3654, entry_quality=3222
- **RANGE_FADE** (total=3860): setup_compat:regime_STRONG_TREND=1818, setup_compat:regime_WEAK_TREND=1569, setup_compat:regime_VOLATILE_UNSUITABLE=436, context_edge=35, setup_compat:regime_BREAKOUT_EXPANSION=2
- **TREND_PULLBACK_EMA** (total=1589): setup_compat:regime_CLEAN_RANGE=753, setup_compat:regime_DIRTY_RANGE=647, entry_quality=114, setup_compat:regime_VOLATILE_UNSUITABLE=75
- **VOLUME_SURGE_BREAKOUT** (total=8): execution:overextended=8
- **WHALE_MOMENTUM** (total=2038): execution:trigger_not_confirmed=1921, context_floor=117

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 286307 | 57.3% |
| TRENDING_DOWN | 84175 | 16.9% |
| QUIET | 63367 | 12.7% |
| TRENDING_UP | 48889 | 9.8% |
| VOLATILE | 16713 | 3.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **189**
- Average confidence gap to threshold: **10.04** (samples=189) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=29, DOTUSDT=25, BTCUSDT=24, AAVEUSDT=20, AVAXUSDT=20, SUIUSDT=17, UNIUSDT=9, XLMUSDT=6, INITUSDT=6, ARBUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 5 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 36 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 261 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 6 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 141 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 35 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 28 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 54 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 48 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 3 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 3 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 10 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 262 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 57 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 431 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 3 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 5 |
| MEAN_REVERT | filtered | min_confidence | 70 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 5 |
| MEAN_REVERT | kept | min_confidence_pass | 5 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 164 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 694 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2361 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 15 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 6740 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 6 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 191 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 44 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 289 |
| SR_FLIP_RETEST | filtered | min_confidence | 45 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 1 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 139 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 76 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 279 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 13 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 5 |
| WHALE_MOMENTUM | filtered | min_confidence | 352 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 17 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 5 | 57.82 | 62.60 | 4.78 | 16.46 | 19.58 | 20.00 | 3.00 | 9.00 |
| BREAKDOWN_SHORT | kept | 36 | 73.27 | 65.00 | -8.27 | 19.46 | 18.93 | 20.00 | 4.00 | 2.56 |
| DIVERGENCE_CONTINUATION | filtered | 267 | 54.02 | 64.08 | 10.06 | 19.64 | 19.89 | 17.05 | 1.65 | 14.95 |
| DIVERGENCE_CONTINUATION | kept | 141 | 68.96 | 65.00 | -3.96 | 21.37 | 19.66 | 17.56 | 1.72 | 0.32 |
| FAILED_AUCTION_RECLAIM | filtered | 63 | 55.49 | 63.27 | 7.78 | 20.79 | 18.70 | 20.00 | 2.52 | 7.51 |
| FAILED_AUCTION_RECLAIM | kept | 54 | 70.75 | 65.00 | -5.75 | 22.63 | 17.49 | 20.00 | 1.31 | 2.08 |
| FUNDING_EXTREME_SIGNAL | filtered | 51 | 45.34 | 63.35 | 18.01 | 20.70 | 15.30 | 16.97 | 3.25 | 10.11 |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 73.40 | 65.00 | -8.40 | 19.90 | 13.63 | 17.00 | 3.67 | 3.20 |
| LIQUIDATION_REVERSAL | filtered | 10 | 74.00 | 10.00 | -64.00 | 18.31 | 8.00 | 14.70 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 319 | 59.03 | 65.00 | 5.97 | 20.61 | 18.98 | 17.71 | 2.08 | 10.10 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 431 | 70.77 | 65.00 | -5.77 | 21.21 | 19.00 | 18.03 | 1.84 | 0.24 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 55.37 | 61.00 | 5.63 | 20.23 | 18.17 | 15.80 | 0.00 | 11.67 |
| MA_CROSS_TREND_SHIFT | kept | 5 | 68.76 | 65.00 | -3.76 | 22.00 | 18.62 | 15.80 | 0.00 | 0.78 |
| MEAN_REVERT | filtered | 75 | 60.70 | 65.00 | 4.30 | 20.84 | 18.63 | 14.36 | 0.00 | 9.82 |
| MEAN_REVERT | kept | 5 | 67.74 | 65.00 | -2.74 | 19.98 | 16.40 | 15.48 | 0.00 | 6.40 |
| MOVER_AVWAP_SCALP | filtered | 165 | 56.50 | 64.88 | 8.38 | 20.57 | 15.91 | 15.80 | 3.81 | 13.60 |
| MOVER_AVWAP_SCALP | kept | 694 | 79.15 | 65.00 | -14.15 | 20.38 | 17.39 | 15.80 | 4.08 | 3.08 |
| MOVER_TREND_PULLBACK | filtered | 2376 | 56.04 | 63.52 | 7.48 | 20.08 | 18.65 | 15.80 | 3.82 | 18.05 |
| MOVER_TREND_PULLBACK | kept | 6740 | 75.99 | 65.00 | -10.99 | 20.44 | 18.74 | 15.80 | 4.07 | 1.85 |
| POST_DISPLACEMENT_CONTINUATION | kept | 6 | 70.50 | 65.00 | -5.50 | 22.12 | 20.00 | 16.58 | 4.50 | 6.33 |
| QUIET_COMPRESSION_BREAK | filtered | 235 | 48.16 | 65.00 | 16.84 | 21.63 | 19.09 | 20.00 | 0.00 | 15.66 |
| QUIET_COMPRESSION_BREAK | kept | 289 | 74.94 | 65.00 | -9.94 | 21.89 | 18.58 | 20.00 | 0.00 | -0.01 |
| SR_FLIP_RETEST | filtered | 46 | 59.35 | 63.61 | 4.26 | 20.23 | 20.00 | 16.35 | 1.39 | 10.19 |
| SR_FLIP_RETEST | kept | 139 | 68.87 | 65.00 | -3.87 | 20.88 | 20.00 | 15.27 | 1.69 | 5.21 |
| TREND_PULLBACK_EMA | filtered | 81 | 57.32 | 64.73 | 7.41 | 20.84 | 19.92 | 18.76 | 4.77 | 19.02 |
| TREND_PULLBACK_EMA | kept | 279 | 77.21 | 65.00 | -12.21 | 20.50 | 19.84 | 17.06 | 4.70 | 2.67 |
| VOLUME_SURGE_BREAKOUT | filtered | 13 | 60.80 | 61.31 | 0.51 | 20.21 | 18.00 | 20.00 | 4.50 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 76.96 | 65.00 | -11.96 | 18.70 | 19.22 | 20.00 | 4.50 | 3.00 |
| WHALE_MOMENTUM | filtered | 369 | 52.60 | 64.87 | 12.27 | 23.79 | 16.32 | 17.00 | 0.00 | 15.49 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 5 | 57.82 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 1.82 | 3.00 |
| BREAKDOWN_SHORT | kept | 36 | 73.27 | 20.11 | 15.33 | 12.67 | 13.97 | 4.38 | 5.37 | 4.00 |
| DIVERGENCE_CONTINUATION | filtered | 267 | 54.02 | 22.96 | 14.59 | 3.79 | 12.49 | 5.19 | 8.91 | 1.65 |
| DIVERGENCE_CONTINUATION | kept | 141 | 68.96 | 23.81 | 12.40 | 5.77 | 12.21 | 5.82 | 8.72 | 1.72 |
| FAILED_AUCTION_RECLAIM | filtered | 63 | 55.49 | 21.10 | 15.78 | 8.52 | 13.46 | 5.86 | 5.76 | 2.52 |
| FAILED_AUCTION_RECLAIM | kept | 54 | 70.75 | 18.19 | 17.63 | 6.22 | 13.41 | 7.78 | 9.13 | 1.31 |
| FUNDING_EXTREME_SIGNAL | filtered | 51 | 45.34 | 22.65 | 10.20 | 6.06 | 13.67 | 7.15 | 5.71 | 3.25 |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 73.40 | 25.00 | 11.33 | 8.00 | 12.00 | 9.50 | 7.10 | 3.67 |
| LIQUIDATION_REVERSAL | filtered | 10 | 74.00 | 21.00 | 18.00 | 15.00 | 8.00 | 8.00 | 0.00 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 319 | 59.03 | 23.06 | 14.19 | 5.43 | 12.18 | 4.95 | 7.27 | 2.08 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 431 | 70.77 | 23.06 | 14.46 | 6.56 | 12.43 | 5.13 | 7.73 | 1.84 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 55.37 | 17.00 | 14.00 | 5.00 | 15.00 | 7.33 | 8.67 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 5 | 68.76 | 20.20 | 14.00 | 5.40 | 14.00 | 7.80 | 8.72 | 0.00 |
| MEAN_REVERT | filtered | 75 | 60.70 | 21.27 | 16.93 | 11.28 | 12.39 | 5.00 | 3.65 | 0.00 |
| MEAN_REVERT | kept | 5 | 67.74 | 23.40 | 16.40 | 12.60 | 12.00 | 5.00 | 4.74 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 165 | 56.50 | 17.99 | 18.00 | 12.29 | 14.55 | 5.18 | 6.72 | 3.81 |
| MOVER_AVWAP_SCALP | kept | 694 | 79.15 | 18.97 | 18.03 | 12.25 | 13.68 | 6.82 | 9.14 | 4.08 |
| MOVER_TREND_PULLBACK | filtered | 2376 | 56.04 | 18.27 | 18.00 | 7.72 | 12.47 | 6.30 | 8.32 | 3.82 |
| MOVER_TREND_PULLBACK | kept | 6740 | 75.99 | 19.43 | 18.01 | 7.73 | 12.68 | 6.68 | 9.33 | 4.07 |
| POST_DISPLACEMENT_CONTINUATION | kept | 6 | 70.50 | 14.50 | 18.00 | 15.00 | 11.00 | 5.83 | 8.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 235 | 48.16 | 21.02 | 14.75 | 10.86 | 14.01 | 6.97 | 5.40 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 289 | 74.94 | 20.60 | 15.43 | 11.69 | 14.01 | 6.74 | 7.39 | 0.00 |
| SR_FLIP_RETEST | filtered | 46 | 59.35 | 18.39 | 17.78 | 3.46 | 14.07 | 5.00 | 9.41 | 1.39 |
| SR_FLIP_RETEST | kept | 139 | 68.87 | 19.94 | 17.71 | 5.55 | 13.00 | 6.48 | 9.70 | 1.69 |
| TREND_PULLBACK_EMA | filtered | 81 | 57.32 | 15.52 | 18.00 | 7.59 | 14.26 | 7.11 | 9.65 | 4.77 |
| TREND_PULLBACK_EMA | kept | 279 | 77.21 | 20.15 | 18.00 | 7.55 | 14.09 | 6.92 | 9.59 | 4.70 |
| VOLUME_SURGE_BREAKOUT | filtered | 13 | 60.80 | 25.00 | 14.00 | 12.00 | 14.00 | 5.00 | 4.30 | 4.50 |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 76.96 | 21.80 | 14.00 | 13.20 | 14.00 | 5.00 | 7.46 | 4.50 |
| WHALE_MOMENTUM | filtered | 369 | 52.60 | 21.97 | 9.92 | 6.72 | 13.32 | 6.83 | 9.33 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 5 | 57.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | **6.00** |
| BREAKDOWN_SHORT | kept | 36 | 73.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | **0.17** |
| DIVERGENCE_CONTINUATION | filtered | 267 | 54.02 | 0.00 | 0.00 | 0.25 | 0.00 | 0.16 | 0.04 | 0.00 | 0.00 | **0.45** |
| DIVERGENCE_CONTINUATION | kept | 141 | 68.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 | 0.00 | **0.04** |
| FAILED_AUCTION_RECLAIM | filtered | 63 | 55.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 54 | 70.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 51 | 45.34 | 0.00 | 0.00 | 4.96 | 0.00 | 1.98 | 0.00 | 0.00 | 0.00 | **6.94** |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 73.40 | 0.00 | 0.00 | 3.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.20** |
| LIQUIDATION_REVERSAL | filtered | 10 | 74.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 319 | 59.03 | 0.00 | 0.00 | 0.61 | 0.00 | 2.30 | 0.19 | 0.00 | 0.00 | **3.10** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 431 | 70.77 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 55.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 5 | 68.76 | 0.00 | 0.00 | 0.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.96** |
| MEAN_REVERT | filtered | 75 | 60.70 | 0.00 | 0.00 | 0.00 | 0.00 | 4.48 | 0.00 | 0.00 | 0.00 | **4.48** |
| MEAN_REVERT | kept | 5 | 67.74 | 0.00 | 0.00 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | **2.40** |
| MOVER_AVWAP_SCALP | filtered | 165 | 56.50 | 1.36 | 0.00 | 0.73 | 0.00 | 2.75 | 0.24 | 0.00 | 2.76 | **7.84** |
| MOVER_AVWAP_SCALP | kept | 694 | 79.15 | 0.00 | 0.00 | 0.02 | 0.00 | 1.00 | 0.20 | 0.00 | 0.00 | **1.22** |
| MOVER_TREND_PULLBACK | filtered | 2376 | 56.04 | 0.03 | 0.00 | 0.89 | 0.00 | 0.28 | 0.29 | 0.00 | 0.22 | **1.71** |
| MOVER_TREND_PULLBACK | kept | 6740 | 75.99 | 0.04 | 0.00 | 0.30 | 0.00 | 0.09 | 0.04 | 0.00 | 0.00 | **0.47** |
| POST_DISPLACEMENT_CONTINUATION | kept | 6 | 70.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 235 | 48.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.16 | 0.00 | 0.00 | 1.79 | **1.95** |
| QUIET_COMPRESSION_BREAK | kept | 289 | 74.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.02 | 0.03 | 0.00 | 0.00 | **0.05** |
| SR_FLIP_RETEST | filtered | 46 | 59.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 139 | 68.87 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 81 | 57.32 | 0.00 | 0.00 | 0.30 | 0.00 | 1.33 | 1.23 | 0.00 | 0.00 | **2.86** |
| TREND_PULLBACK_EMA | kept | 279 | 77.21 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | **0.28** |
| VOLUME_SURGE_BREAKOUT | filtered | 13 | 60.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 76.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 369 | 52.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.42 | 0.00 | 0.00 | 0.00 | **0.42** |

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
- Outcomes recorded: **197625 held of 942662 seen** across 21 strategies; 4474 cells past the sample floor; **2425 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 49262 | 599/48663/0 | 43% | -0.19 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.26R) |
| MOVER_AVWAP_SCALP | 26287 | 192/26095/0 | 43% | -0.19 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 15704 | 272/15432/0 | 46% | -0.12 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.98R) | NY/MARKUP/CASCADE/BTC_FALLING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 14884 | 148/14736/0 | 36% | -0.33 | OVERLAP/RANGE/NORMAL/BTC_FALLING/MIDCAP (+1.72R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 14089 | 78/14011/0 | 38% | -0.31 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.38R) |
| LIQUIDITY_SWEEP_REVERSAL | 11131 | 122/11009/0 | 38% | -0.40 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.91R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9703 | 497/9206/0 | 44% | -0.12 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8401 | 0/0/8401 | 43% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+1.04R) | OVERLAP/MARKDOWN/EXPANDED/BTC_FALLING (-0.92R) |
| SHADOW_RANGE_FADE | 7932 | 0/0/7932 | 35% | -0.14 | OVERLAP/MARKUP/COMPRESSED/BTC_NEUTRAL (+0.43R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.36R) |
| SHADOW_FUNDING_FADE | 7511 | 0/0/7511 | 34% | -0.42 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.02R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 7473 | 30/7443/0 | 47% | -0.28 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 5763 | 75/5688/0 | 37% | -0.31 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4540 | 4/4536/0 | 31% | -0.44 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.06R) | LONDON/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.33R) |
| WHALE_MOMENTUM | 4395 | 4/4391/0 | 47% | -0.28 | NY/RANGE/EXPANDED/BTC_FALLING (+0.94R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 4149 | 0/4149/0 | 27% | -0.43 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/NORMAL/BTC_FALLING/ALTCOIN (-1.19R) |
| RANGE_FADE | 3165 | 6/3159/0 | 52% | +0.25 | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (+3.08R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.78R) |
| SHADOW_CASCADE_REVERSAL | 1765 | 0/0/1765 | 52% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.56R) |
| BREAKDOWN_SHORT | 585 | 67/518/0 | 35% | -0.27 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 572 | 0/572/0 | 35% | -0.28 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 250 | 40/210/0 | 45% | -0.16 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 64 | 6/58/0 | 41% | +0.09 | — | — |

- **Strongest cells**: `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.08R (n=37, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.00R (n=32, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.78R (n=47, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 428 | 27% / -0.55R | 428 | 52% / -0.09R | +0.46 | **ATR** |
| TREND_PULLBACK_EMA | 1449 | 39% / -0.37R | 1449 | 50% / -0.09R | +0.28 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1709 | 44% / -0.34R | 1709 | 58% / -0.10R | +0.24 | **ATR** |
| LIQUIDATION_REVERSAL | 35 | 26% / -0.58R | 35 | 46% / -0.34R | +0.24 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 240 | 37% / -0.18R | 240 | 48% / -0.04R | +0.14 | **ATR** |
| MA_CROSS_TREND_SHIFT | 76 | 45% / -0.16R | 76 | 50% / -0.03R | +0.13 | **ATR** |
| BREAKDOWN_SHORT | 54 | 43% / -0.20R | 54 | 48% / -0.07R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 822 | 48% / -0.25R | 822 | 52% / -0.13R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 2921 | 46% / -0.14R | 2921 | 52% / -0.04R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 473 | 46% / -0.30R | 473 | 48% / -0.20R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1646 | 41% / -0.23R | 1646 | 43% / -0.13R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 9193 | 48% / -0.13R | 9193 | 54% / -0.03R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 2098 | 48% / -0.12R | 2098 | 53% / -0.06R | +0.05 | **ATR** |
| RANGE_FADE | 168 | 44% / +0.08R | 168 | 51% / +0.12R | +0.04 | **ATR** |
| MEAN_REVERT | 495 | 46% / -0.16R | 495 | 45% / -0.17R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1705 | 48% / -0.10R | 1705 | 48% / -0.10R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 14 | 57% / -0.06R | 14 | 57% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12297 | 27% | -0.27R | 313 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2921 | 50% | -0.03R | 242 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 152 | 47% | -0.06R | 74 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1846 | 33% / -0.15R | +0.91 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 2012 | 40% / -0.13R | +0.88 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3464 | 36% / -0.15R | +0.69 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11298 | 36% / -0.15R | +0.38 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2417 | 37% / -0.12R | +0.16 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 172 | 34% / -0.39R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1655 | 37% / -0.11R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1374 | 31% / -0.28R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 350 | 31% / -0.37R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 545 | 32% / -0.24R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 412 | 48% / -0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 92 | 43% / +0.00R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 118 | 47% / +0.06R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 709 | 36% / -0.28R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 123 | 32% / +0.14R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 46 | 43% / -0.26R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 26 | 46% / +0.50R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 64 · alerting: **3** · boot grace active: False
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.61R (bound 0.3) (streak 29/6) (sustained 29 cycles)
- **ALERT** `range_fade_emission` — 2318 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.25R over n=3159, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 29/6) (sustained 29 cycles)
- **ALERT** `tuned_variants` — 78 non-stamps — atr_arm_uncomputable=78 (seen=2326 stamped=214 skipped=2034) (streak 29/6) (sustained 29 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 2884813 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 22 arms current, none stalled; covering 2027/2027 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| analyst_plan_cadence | ok | last plan 57m ago | 0 |
| atr_trail_live_arms | ok | 53 arms current, none stalled; covering 1033/1033 signals (100%) | 0 |
| auto_dispatch | ok | 8 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=8. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 204/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 61627.00 | 0 |
| candle_coverage | ok | 91/91 symbols with ≥20 15m candles, 91/91 updated within 45m [fresh=91; 75 Tier-1 futures + 16 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 902 dup bars, 0 undedupable; ws 0 out-of-order, 186 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 63 cohorts, 30 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +36 / upstream +29 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1338/1357 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 3 of 221 open dark rows are not being advanced (worst: IDOLUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 29/120) | 29 |
| dark_sar_arms | ok | no open arms; covering 1332/1351 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 1033914 msgs, 0 rejected | 0 |
| deriv_recorder | ok | hour recorded, 75 rows | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.61R (bound 0.3) (streak 29/6) | 29 |
| emission_controller | ok | last cycle 1221s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=395, MOVER_AVWAP_SCALP=294, MOVER_TREND_PULLBACK=5076, RANGE_FADE=156, TREND_PULLBACK_EMA=79), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 4 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won,TREND_PULLBACK_EMA.campaign_prev_age_h,TREND_PULLBACK_EMA.campaign_prev_won) | 0 |
| entry_quality_effective | ok | 3229 evaluated, 1124 suppressed, 2054 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,365 reads/day of 50,000 [engine 1,340, signing 25]; top site keystore.roster_doc at 292/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +13 / upstream +295 | 0 |
| htf_candles | ok | BTCUSDT 1d/1w current | 0 |
| indicator_cache_key | ok | 1656 frozen value(s) avoided; 0 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.31R over n=5688 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +27 / upstream +295 | 0 |
| mover_admission_metadata | ok | 953 symbols known, 244 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 16 held, 16 with scan counts, 16 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2210 rows held, 3743659 evicted (sampled: execution:trigger_not_confirmed 278/1316286, execution:overextended 278/1149054, setup_compat:regime_STRONG_TREND 278/645855) | 0 |
| price_action_lane | ok | 101342 evaluated, 109 emitted; layer1 109 stamped / 0 blind; cooldown=15553, delta_opposed=10922, no_footprint=37966, no_opposing_target=2, no_sweep=27101, rr_below_floor=9689 | 0 |
| promoted_pair_integrity | ok | 16/16 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 2318 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.25R over n=3159, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 29/6) | 29 |
| range_fade_path | violating | upstream +295 but output +0 (streak 2/72) | 2 |
| sar_alignment_crosscheck | ok | 93/4997 disagreed (1.9%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +295 | 0 |
| sar_hold_arm | ok | 1880 held arms settled, 121 unscored, 52 still walking (44 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 13/109 unfetchable (12%); top cause: gap or duplicate bar in the 15m window; symbols: ICNTUSDT, PENGUUSDT, PIPPINUSDT | 0 |
| sar_live_arms | ok | 53 arms current, none stalled; covering 1033/1033 signals (100%) | 0 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 7 resolved, 89 still mid-window | 0 |
| scan_cycle | ok | last 67.54s, worst 92.15s over 1241 lifetime cycles; lifetime 12 over 60s, 0 over 120s; recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 3.85s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 48834 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 3s ago (1.2s to run, worst 75.32s), 82 overrun(s) of 780 cycles, TTL 900s; slowest pair_context=8.34s, agents=2.35s, signals=0.51s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +127 / upstream +295 | 0 |
| structural_snap | ok | 6000/6000 measured, 41 blind, 0 levels moved (refusals: redetect_cooldown=464) | 0 |
| structural_veto_lane | ok | 615 stamped; 0 with no readable level book, 7 with clear air ahead, 455 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +295 / upstream +29 | 0 |
| tuned_variants | violating | 78 non-stamps — atr_arm_uncomputable=78 (seen=2326 stamped=214 skipped=2034) (streak 29/6) | 29 |
| unlock_shorts | ok | 17 open, 43 scheduled, calendar 2.0h old | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2626895`
- `Path funnel` emissions: `62`
- `Regime distribution` emissions: `62`
- `QUIET_SCALP_BLOCK` events: `189`
- `confidence_gate` events: `12905`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **13**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 2 | 1590 | 1590 | 1928 | 0 |
| futures_aggtrade | 1 | 2276 | 2276 | 2276 | 0 |
| futures_depth | 3 | 3413 | 3413 | 11592 | 0 |
| futures_liq | 6 | 3495 | 6285 | 11035 | 0 |
| futures_mover | 1 | 1592 | 1592 | 1592 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=353262] state[populated=353262] buckets[many=353012, some=250] sources[none] quality[none]
- funding_rate: presence[absent=32481, present=320781] state[empty=32481, populated=320781] buckets[few=320781, none=32481] sources[none] quality[none]
- liquidation_clusters: presence[absent=184327, present=168935] state[empty=184327, populated=168935] buckets[few=141233, none=184327, some=27702] sources[none] quality[none]
- oi_snapshot: presence[absent=27618, present=325644] state[empty=27618, populated=325644] buckets[few=120, many=324711, none=27618, some=813] sources[none] quality[none]
- order_book: presence[absent=103917, present=249345] state[populated=249345, unavailable=103917] buckets[few=249345, none=103917] sources[book_ticker=249345, unavailable=103917] quality[none=103917, top_of_book_only=249345]
- orderblocks: presence[absent=353262] state[empty=353262] buckets[none=353262] sources[measured_dark=353262] quality[none]
- recent_ticks: presence[present=353262] state[populated=353262] buckets[many=353262] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.472028613090515` sec
- Median create→first breach: `4846.274059414864` sec
- Median create→terminal: `4846.972184896469` sec
- Median first breach→terminal: `0.00012159347534179688` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 1.2}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 2.632122328254947 | 3.0 | 0.8773741094183157 | 0 | 3 |
| DIVERGENCE_CONTINUATION | 2 | 2 | 1.1277636533693591 | 1.671859186277228 | 0.6807732187296747 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 7 | 7 | 1.1762637544469374 | 1.3612565445026192 | 0.6407141552511466 | 0 | 6 |
| LIQUIDITY_SWEEP_REVERSAL | 7 | 7 | 1.2882145488029517 | 1.5156963075646495 | 0.8584165199735088 | 0 | 6 |
| MEAN_REVERT | 2 | 2 | 2.5171070901974084 | 2.730694980694981 | 0.9225080669695456 | 0 | 2 |
| MOVER_AVWAP_SCALP | 3 | 3 | 1.459871739411988 | 1.6382249127343207 | 0.8911302276409362 | 0 | 3 |
| MOVER_TREND_PULLBACK | 42 | 42 | 4.038066842338372 | 3.0 | 1.3460222807794575 | 35 | 6 |
| QUIET_COMPRESSION_BREAK | 14 | 14 | 1.1879814615266344 | 1.3845942061007042 | 0.8808301490042303 | 0 | 12 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 5.296054467325196 | 3.9481834923824017 | 0 | 0 | 0 | 2 | 1 | 1 |
| DIVERGENCE_CONTINUATION | 2 | 2.914633717041575 | 2.6056684972013926 | 0 | 0 | 0 | 1 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 7 | 1.709274427070409 | 1.7644990485645713 | 2 | 1 | 1 | 0 | 0 | 5 |
| LIQUIDITY_SWEEP_REVERSAL | 7 | 2.645395101024096 | 1.9323218199847991 | 0 | 0 | 0 | 5 | 1 | 2 |
| MEAN_REVERT | 2 | 3.680896706192132 | 3.77976038700412 | 2 | 1 | 1 | 0 | 0 | 0 |
| MOVER_AVWAP_SCALP | 3 | 1.4516707680352294 | 2.189807019816092 | 3 | 0 | 0 | 0 | 0 | 0 |
| MOVER_TREND_PULLBACK | 42 | 5.3265014677184634 | 3.982680000000003 | 9 | 4 | 1 | 33 | 5 | 0 |
| QUIET_COMPRESSION_BREAK | 14 | 3.6542259701125652 | 1.9438667283869824 | 0 | 0 | 0 | 11 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 100.0 | 0.0 | 100.0 | 0.0 | 3.6247 | 6365.021247148514 | 6365.559766054153 |
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 9378.293358445168 | 9378.811416983604 |
| FAILED_AUCTION_RECLAIM | 7 | 7 | 42.9 | 14.3 | 42.9 | 0.0 | 1.3457 | 9816.954764127731 | 9826.243729114532 |
| LIQUIDITY_SWEEP_REVERSAL | 7 | 7 | 57.1 | 28.6 | 57.1 | 0.0 | 0.8837 | 6002.195650100708 | 6003.777371168137 |
| MEAN_REVERT | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 2.3607 | 5118.393255829811 | 5118.823814868927 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -1.3724 | 9512.545749902725 | 9512.545826911926 |
| MOVER_TREND_PULLBACK | 42 | 42 | 35.7 | 42.9 | 35.7 | 0.0 | 0.1992 | 2424.7431049346924 | 2424.987962961197 |
| QUIET_COMPRESSION_BREAK | 14 | 14 | 28.6 | 57.1 | 28.6 | 0.0 | 0.0142 | 17406.67324435711 | 17406.673298954964 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 561 | 13 | 268 | 0.0 | 0.0 | None | None | 293 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1821 | 40 | 1234 | 0.0 | 0.0 | None | None | 587 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `301`
- Gating Δ: `13841`
- No-generation Δ: `618043`
- Fast failures Δ: `-1`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": 3.6247, "current_avg_pnl": 3.6247, "current_win_rate": 100.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 100.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 1.0739, "current_avg_pnl": 1.0, "current_win_rate": 0.0, "previous_avg_pnl": -0.0739, "previous_win_rate": 11.1, "win_rate_delta": -11.1}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 1.3457, "current_avg_pnl": 1.3457, "current_win_rate": 42.9, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 42.9}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 3.7294, "current_avg_pnl": 0.8837, "current_win_rate": 57.1, "previous_avg_pnl": -2.8457, "previous_win_rate": 0.0, "win_rate_delta": 57.1}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.3197, "current_avg_pnl": -1.3724, "current_win_rate": 0.0, "previous_avg_pnl": -0.0527, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.4167, "current_avg_pnl": 0.1992, "current_win_rate": 35.7, "previous_avg_pnl": 0.6159, "previous_win_rate": 39.5, "win_rate_delta": -3.8}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0135, "current_avg_pnl": 0.0142, "current_win_rate": 28.6, "previous_avg_pnl": 0.0007, "previous_win_rate": 27.3, "win_rate_delta": 1.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": -224, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 11, "geometry_changed_delta": 0, "geometry_preserved_delta": 256, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -3339.04, "median_terminal_delta_sec": -3339.04, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **LIQUIDITY_SWEEP_REVERSAL**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
