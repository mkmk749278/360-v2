# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: DIVERGENCE_CONTINUATION, FAILED_AUCTION_RECLAIM, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: MOVER_TREND_PULLBACK
- Recommended next investigation target: **DIVERGENCE_CONTINUATION**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `993` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 294 | 294 | 246 | 4 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 17031 | 17031 | 14746 | 19 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 94164 | 94165 | 38 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 72543 | 72543 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 72112 | 69303 | 3216 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 72572 | 71540 | 1105 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 79631 | 79605 | 56 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 71119 | 71126 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 72650 | 72698 | 9 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 72710 | 70427 | 3272 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 97434 | 101666 | 1504 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 94206 | 87294 | 10079 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 79036 | 79036 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 72545 | 72564 | 6 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 72089 | 72019 | 89 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 73709 | 72235 | 2087 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 71466 | 71821 | 235 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 63748 | 59753 | 4192 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 63952 | 63461 | 561 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 94130 | 94119 | 41 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 71132 | 71143 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 6429 | 6429 | 4738 | 10 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 223 | 223 | 126 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 35 | 35 | 35 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 25974 | 25974 | 24489 | 39 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 16 | 16 | 12 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 10771 | 10771 | 7581 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 4628 | 4628 | 2943 | 46 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 31878 | 31878 | 19563 | 246 | active-healthy (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 52 | 52 | 52 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 959 | 959 | 761 | 15 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 7574 | 7574 | 5824 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 752 | 752 | 385 | 14 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3726 | 3726 | 3267 | 32 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 204 | 204 | 167 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=94165): breakout_not_found=58808, basic_filters_failed=20740, move_not_fresh=8877, breakout_stale=4038, retest_proximity_failed=1514, volume_spike_missing=186, missing_fvg_or_orderblock=1, move_exhausted=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=72543): cls_disabled_merged_into_lsr=72543
- **EVAL::DIVERGENCE_CONTINUATION** (total=69303): cvd_divergence_failed=25717, h1_trend_not_aligned=24084, basic_filters_failed=11708, ema_alignment_reject=6792, retest_proximity_failed=642, missing_fvg_or_orderblock=360
- **EVAL::FAILED_AUCTION_RECLAIM** (total=71540): auction_not_detected=49699, basic_filters_failed=11568, reclaim_hold_failed=5047, tail_too_small=3973, regime_blocked=1204, rsi_reject=49
- **EVAL::FUNDING_EXTREME** (total=79605): funding_not_extreme=65021, basic_filters_failed=12478, missing_funding_rate=1067, ema_alignment_reject=752, rsi_reject=137, cvd_divergence_failed=78, momentum_reject=70, missing_fvg_or_orderblock=2
- **EVAL::LIQUIDATION_REVERSAL** (total=71126): cascade_threshold_not_met=57695, basic_filters_failed=12610, cvd_divergence_failed=433, rsi_reject=345, missing_fvg_or_orderblock=40, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=72698): no_ma_cross=59965, basic_filters_failed=11718, ma_cross_htf_misaligned=580, ma_cross_cooldown=435
- **EVAL::MEAN_REVERT** (total=70427): no_extension=61282, basic_filters_failed=9145
- **EVAL::MOVER_AVWAP_SCALP** (total=101666): no_avwap_tag=41301, no_mover_leg=26004, basic_filters_failed=20935, avwap_slope_against=8530, avwap_reclaim_no_volume=2804, no_avwap_reclaim=2075, anchor_too_recent=17
- **EVAL::MOVER_TREND_PULLBACK** (total=87294): mover_run_too_small=49689, basic_filters_failed=20828, no_reclaim=14300, no_pullback_tag=2477
- **EVAL::OPENING_RANGE_BREAKOUT** (total=79036): feature_disabled=79036
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=72564): regime_blocked=40108, breakout_not_found=24276, basic_filters_failed=4080, adx_reject=4039, ema_alignment_reject=61
- **EVAL::QUIET_COMPRESSION_BREAK** (total=72019): regime_blocked=33505, compression_not_detected=26302, basic_filters_failed=7479, breakout_not_detected=4391, volume_confirmation_failed=333, rsi_reject=6, missing_fvg_or_orderblock=3
- **EVAL::RANGE_FADE** (total=72235): no_range_edge=63085, basic_filters_failed=9150
- **EVAL::SR_FLIP_RETEST** (total=71821): flip_close_not_confirmed=49279, basic_filters_failed=11548, long_break_volume_thin=4482, retest_out_of_zone=2374, h1_break_not_confirmed=1614, regime_blocked=1196, reclaim_hold_failed=890, long_acceptance_not_held=166, wick_quality_failed=106, ema_alignment_reject=96, whipsaw_flip=69, missing_fvg_or_orderblock=1
- **EVAL::STANDARD** (total=59753): momentum_reject=18186, adx_reject=16894, basic_filters_failed=6637, ema_alignment_reject=6569, sweeps_not_detected=5923, macd_reject=4739, htf_poi_unanchored=727, invalid_sl_geometry=39, rsi_reject=32, mtf_reject=7
- **EVAL::TREND_PULLBACK** (total=63461): h1_trend_not_aligned=25838, ema_alignment_reject=10845, basic_filters_failed=5806, h1_pullback_not_confirmed=5791, ema_not_tested_prev=4546, no_ema_reclaim_close=4385, body_conviction_fail=2496, rsi_reject=1741, prev_already_below_emas=703, no_prev_low_break=420, prev_already_above_emas=312, no_prev_high_break=271, momentum_flat=231, ema21_not_tagged=37, missing_fvg_or_orderblock=33, momentum_reject=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=94119): breakout_not_found=52697, basic_filters_failed=20737, move_not_fresh=13031, breakout_stale=5508, retest_proximity_failed=1712, volume_spike_missing=360, missing_fvg_or_orderblock=67, move_exhausted=7
- **EVAL::WHALE_MOMENTUM** (total=71143): momentum_reject=60653, recent_ticks_insufficient=8305, basic_filters_failed=2185

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=40): execution:overextended=38, context_floor=2
- **DIVERGENCE_CONTINUATION** (total=527): setup_compat:regime_VOLATILE_UNSUITABLE=437, setup_compat:regime_BREAKOUT_EXPANSION=75, execution:overextended=15
- **FAILED_AUCTION_RECLAIM** (total=2412): execution:overextended=966, setup_compat:regime_STRONG_TREND=899, context_floor=541, setup_compat:regime_VOLATILE_UNSUITABLE=6
- **FUNDING_EXTREME_SIGNAL** (total=124): execution:trigger_not_confirmed=124
- **LIQUIDATION_REVERSAL** (total=35): execution:trigger_not_confirmed=35
- **LIQUIDITY_SWEEP_REVERSAL** (total=6463): setup_compat:regime_STRONG_TREND=2795, execution:trigger_not_confirmed=1901, execution:overextended=1767
- **MA_CROSS_TREND_SHIFT** (total=9): setup_compat:regime_DIRTY_RANGE=4, execution:trigger_not_confirmed=2, setup_compat:regime_VOLATILE_UNSUITABLE=1, setup_compat:regime_CLEAN_RANGE=1, execution:overextended=1
- **MEAN_REVERT** (total=8436): setup_compat:regime_WEAK_TREND=4147, setup_compat:regime_STRONG_TREND=3724, execution:overextended=556, entry_quality=9
- **MOVER_AVWAP_SCALP** (total=2047): execution:overextended=1522, execution:trigger_not_confirmed=302, entry_quality=223
- **MOVER_TREND_PULLBACK** (total=14436): execution:trigger_not_confirmed=7315, execution:overextended=5231, entry_quality=1890
- **QUIET_COMPRESSION_BREAK** (total=30): execution:overextended=20, execution:trigger_not_confirmed=10
- **RANGE_FADE** (total=5052): setup_compat:regime_WEAK_TREND=2365, setup_compat:regime_STRONG_TREND=2189, setup_compat:regime_VOLATILE_UNSUITABLE=215, context_edge=154, execution:overextended=108, setup_compat:regime_BREAKOUT_EXPANSION=21
- **TREND_PULLBACK_EMA** (total=2451): setup_compat:regime_CLEAN_RANGE=1563, setup_compat:regime_DIRTY_RANGE=683, entry_quality=106, setup_compat:regime_VOLATILE_UNSUITABLE=99
- **VOLUME_SURGE_BREAKOUT** (total=24): execution:overextended=24

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 225227 | 39.8% |
| TRENDING_UP | 127539 | 22.5% |
| TRENDING_DOWN | 101435 | 17.9% |
| QUIET | 94242 | 16.7% |
| VOLATILE | 17567 | 3.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **158**
- Average confidence gap to threshold: **10.44** (samples=158) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: INJUSDT=47, XLMUSDT=13, ETHUSDT=12, XRPUSDT=10, TRXUSDT=10, PHAUSDT=8, LINKUSDT=7, UNIUSDT=6, DASHUSDT=6, 0GUSDT=6

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 46 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 403 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 19 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 307 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 290 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 6 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 80 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 5 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 253 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 26 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 305 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | kept | min_confidence_pass | 14 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 148 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 7 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 716 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1025 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 61 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4042 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 83 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 30 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 37 |
| RANGE_FADE | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 113 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 5 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 82 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 56 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 4 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 167 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 35 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 46 | 79.20 | 65.00 | -14.20 | 18.37 | 16.77 | 20.00 | 5.00 | 1.43 |
| DIVERGENCE_CONTINUATION | filtered | 422 | 56.70 | 64.25 | 7.55 | 20.31 | 19.63 | 18.19 | 1.28 | 9.87 |
| DIVERGENCE_CONTINUATION | kept | 307 | 68.89 | 65.00 | -3.89 | 20.75 | 19.29 | 17.29 | 0.98 | 1.83 |
| FAILED_AUCTION_RECLAIM | filtered | 296 | 52.98 | 61.18 | 8.20 | 21.28 | 19.10 | 20.00 | 2.03 | 14.66 |
| FAILED_AUCTION_RECLAIM | kept | 80 | 72.98 | 65.00 | -7.98 | 21.18 | 18.39 | 20.00 | 2.37 | 4.39 |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 37.30 | 61.00 | 23.70 | 21.20 | 20.00 | 17.00 | 0.00 | 13.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 279 | 54.09 | 65.00 | 10.91 | 20.61 | 18.42 | 17.43 | 1.36 | 14.65 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 305 | 70.20 | 65.00 | -5.20 | 21.15 | 19.34 | 18.22 | 2.47 | 0.14 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 78.80 | 65.00 | -13.80 | 20.35 | 17.00 | 15.80 | 0.00 | 0.20 |
| MEAN_REVERT | kept | 14 | 66.17 | 65.00 | -1.17 | 18.81 | 15.86 | 13.64 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 155 | 53.88 | 63.63 | 9.75 | 20.00 | 16.96 | 15.80 | 4.46 | 16.76 |
| MOVER_AVWAP_SCALP | kept | 716 | 80.84 | 65.00 | -15.84 | 20.60 | 16.44 | 15.80 | 4.55 | 1.91 |
| MOVER_TREND_PULLBACK | filtered | 1086 | 57.70 | 64.79 | 7.09 | 20.24 | 18.85 | 15.80 | 3.82 | 17.23 |
| MOVER_TREND_PULLBACK | kept | 4042 | 77.13 | 65.00 | -12.13 | 20.04 | 18.48 | 15.80 | 4.48 | 1.21 |
| QUIET_COMPRESSION_BREAK | filtered | 113 | 51.50 | 63.81 | 12.31 | 20.95 | 18.72 | 20.00 | 0.00 | 13.64 |
| QUIET_COMPRESSION_BREAK | kept | 37 | 71.97 | 65.00 | -6.97 | 21.11 | 19.45 | 20.00 | 0.00 | -0.76 |
| RANGE_FADE | kept | 1 | 69.30 | 65.00 | -4.30 | 23.40 | 16.40 | 16.30 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 118 | 56.84 | 65.00 | 8.16 | 20.98 | 20.00 | 15.32 | 1.74 | 12.19 |
| SR_FLIP_RETEST | kept | 82 | 72.10 | 65.00 | -7.10 | 20.40 | 20.00 | 15.67 | 2.50 | 2.21 |
| TREND_PULLBACK_EMA | filtered | 60 | 59.65 | 64.00 | 4.35 | 20.19 | 19.98 | 18.32 | 4.57 | 17.39 |
| TREND_PULLBACK_EMA | kept | 167 | 78.24 | 65.00 | -13.24 | 20.29 | 19.70 | 18.24 | 4.84 | -0.34 |
| VOLUME_SURGE_BREAKOUT | filtered | 35 | 38.55 | 64.09 | 25.54 | 20.10 | 17.87 | 20.00 | 3.33 | 21.31 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 72.65 | 65.00 | -7.65 | 16.90 | 17.60 | 20.00 | 4.50 | 6.35 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 46 | 79.20 | 22.61 | 16.70 | 12.91 | 12.50 | 4.02 | 6.90 | 5.00 |
| DIVERGENCE_CONTINUATION | filtered | 422 | 56.70 | 21.42 | 15.99 | 4.00 | 12.33 | 5.27 | 7.63 | 1.28 |
| DIVERGENCE_CONTINUATION | kept | 307 | 68.89 | 20.86 | 15.59 | 4.26 | 13.24 | 7.12 | 8.96 | 0.98 |
| FAILED_AUCTION_RECLAIM | filtered | 296 | 52.98 | 21.30 | 17.05 | 4.02 | 14.48 | 5.72 | 5.17 | 2.03 |
| FAILED_AUCTION_RECLAIM | kept | 80 | 72.98 | 21.25 | 16.10 | 9.30 | 13.79 | 5.59 | 9.16 | 2.37 |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 37.30 | 25.00 | 8.00 | 6.00 | 17.00 | 5.00 | 4.30 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 279 | 54.09 | 23.59 | 14.56 | 4.31 | 13.33 | 6.20 | 5.38 | 1.36 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 305 | 70.20 | 23.33 | 14.64 | 4.41 | 12.94 | 5.52 | 7.04 | 2.47 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 78.80 | 25.00 | 14.00 | 13.50 | 15.50 | 5.00 | 6.00 | 0.00 |
| MEAN_REVERT | kept | 14 | 66.17 | 25.00 | 14.00 | 6.21 | 10.21 | 5.00 | 5.74 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 155 | 53.88 | 18.11 | 18.00 | 10.96 | 14.83 | 6.22 | 5.32 | 4.46 |
| MOVER_AVWAP_SCALP | kept | 716 | 80.84 | 20.02 | 18.10 | 11.53 | 14.17 | 6.77 | 7.81 | 4.55 |
| MOVER_TREND_PULLBACK | filtered | 1086 | 57.70 | 18.07 | 18.01 | 7.58 | 12.13 | 7.15 | 9.00 | 3.82 |
| MOVER_TREND_PULLBACK | kept | 4042 | 77.13 | 19.29 | 18.05 | 7.91 | 13.33 | 6.41 | 8.98 | 4.48 |
| QUIET_COMPRESSION_BREAK | filtered | 113 | 51.50 | 19.97 | 15.06 | 10.73 | 13.93 | 7.12 | 4.15 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 37 | 71.97 | 19.81 | 15.08 | 9.97 | 14.16 | 5.80 | 8.50 | 0.00 |
| RANGE_FADE | kept | 1 | 69.30 | 25.00 | 18.00 | 6.00 | 12.00 | 5.00 | 3.30 | 0.00 |
| SR_FLIP_RETEST | filtered | 118 | 56.84 | 19.95 | 17.58 | 3.92 | 14.00 | 5.20 | 6.64 | 1.74 |
| SR_FLIP_RETEST | kept | 82 | 72.10 | 22.66 | 17.88 | 4.83 | 13.77 | 5.15 | 7.64 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 60 | 59.65 | 16.50 | 18.00 | 7.50 | 14.00 | 7.20 | 9.27 | 4.57 |
| TREND_PULLBACK_EMA | kept | 167 | 78.24 | 19.20 | 18.00 | 7.50 | 14.04 | 6.40 | 9.19 | 4.84 |
| VOLUME_SURGE_BREAKOUT | filtered | 35 | 38.55 | 17.23 | 14.00 | 12.86 | 14.00 | 5.00 | 4.17 | 3.33 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 72.65 | 17.00 | 18.00 | 13.50 | 10.50 | 6.50 | 9.00 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 46 | 79.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 422 | 56.70 | 0.00 | 0.00 | 0.69 | 0.00 | 0.27 | 0.00 | 0.00 | 0.00 | **0.96** |
| DIVERGENCE_CONTINUATION | kept | 307 | 68.89 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.05** |
| FAILED_AUCTION_RECLAIM | filtered | 296 | 52.98 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 80 | 72.98 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.10** |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 37.30 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 279 | 54.09 | 0.00 | 0.00 | 0.60 | 0.00 | 0.90 | 0.00 | 0.00 | 0.00 | **1.50** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 305 | 70.20 | 0.00 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.02** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 78.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 14 | 66.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 155 | 53.88 | 0.00 | 0.00 | 0.08 | 0.00 | 3.41 | 0.00 | 0.00 | 1.55 | **5.04** |
| MOVER_AVWAP_SCALP | kept | 716 | 80.84 | 0.00 | 0.00 | 0.04 | 0.00 | 0.45 | 0.00 | 0.00 | 0.88 | **1.37** |
| MOVER_TREND_PULLBACK | filtered | 1086 | 57.70 | 0.00 | 0.00 | 0.64 | 0.00 | 0.38 | 0.00 | 0.00 | 0.00 | **1.02** |
| MOVER_TREND_PULLBACK | kept | 4042 | 77.13 | 0.00 | 0.00 | 0.82 | 0.00 | 0.20 | 0.00 | 0.00 | 0.00 | **1.02** |
| QUIET_COMPRESSION_BREAK | filtered | 113 | 51.50 | 2.39 | 0.00 | 0.00 | 0.00 | 0.38 | 0.00 | 0.00 | 1.16 | **3.93** |
| QUIET_COMPRESSION_BREAK | kept | 37 | 71.97 | 0.00 | 0.00 | 0.00 | 0.00 | 0.12 | 0.00 | 0.00 | 0.29 | **0.41** |
| RANGE_FADE | kept | 1 | 69.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 118 | 56.84 | 0.00 | 0.00 | 0.81 | 0.00 | 0.00 | 0.00 | 0.00 | 1.16 | **1.97** |
| SR_FLIP_RETEST | kept | 82 | 72.10 | 0.00 | 0.00 | 0.21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.53 | **0.74** |
| TREND_PULLBACK_EMA | filtered | 60 | 59.65 | 0.00 | 0.00 | 0.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.27** |
| TREND_PULLBACK_EMA | kept | 167 | 78.24 | 0.00 | 0.00 | 0.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.29** |
| VOLUME_SURGE_BREAKOUT | filtered | 35 | 38.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | **0.17** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 72.65 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.40** |

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
- Outcomes recorded: **123441 held of 393015 seen** across 21 strategies; 2827 cells past the sample floor; **1346 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 40521 | 566/39955/0 | 44% | -0.17 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | OVERLAP/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.20R) |
| MOVER_AVWAP_SCALP | 16077 | 184/15893/0 | 40% | -0.28 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 9690 | 113/9577/0 | 40% | -0.22 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 8363 | 54/8309/0 | 50% | -0.03 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.48R) | NY/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| TREND_PULLBACK_EMA | 6987 | 26/6961/0 | 43% | -0.17 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.33R) |
| SHADOW_MEAN_REVERT | 6377 | 0/0/6377 | 44% | -0.07 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | LONDON/QUIET/NORMAL/BTC_RISING (-0.83R) |
| SHADOW_RANGE_FADE | 5600 | 0/0/5600 | 37% | -0.09 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.63R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.33R) |
| QUIET_COMPRESSION_BREAK | 5182 | 322/4860/0 | 45% | -0.14 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+0.65R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4955 | 0/0/4955 | 34% | -0.40 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| LIQUIDITY_SWEEP_REVERSAL | 4698 | 68/4630/0 | 39% | -0.45 | NY/RANGE/NORMAL/BTC_FALLING (+1.64R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| WHALE_MOMENTUM | 3391 | 2/3389/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| MEAN_REVERT | 2458 | 31/2427/0 | 49% | -0.10 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.62R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| VOLUME_SURGE_BREAKOUT | 2263 | 0/2263/0 | 40% | -0.08 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2128 | 2/2126/0 | 31% | -0.48 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| SR_FLIP_RETEST | 1770 | 12/1758/0 | 50% | -0.20 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.86R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.27R) |
| RANGE_FADE | 1073 | 4/1069/0 | 36% | -0.54 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 983 | 0/0/983 | 55% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.15R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.42R) |
| BREAKDOWN_SHORT | 563 | 59/504/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 276 | 0/276/0 | 31% | -0.57 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 78 | 12/66/0 | 49% | -0.02 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 8 | 0/8/0 | 75% | +0.30 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR` -1.55R (n=16, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR` -1.53R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 159 | 26% / -0.59R | 159 | 47% / -0.18R | +0.41 | **ATR** |
| LIQUIDATION_REVERSAL | 15 | 33% / -0.42R | 15 | 60% / -0.16R | +0.25 | **ATR** |
| TREND_PULLBACK_EMA | 572 | 43% / -0.23R | 572 | 56% / -0.04R | +0.19 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 930 | 47% / -0.29R | 930 | 56% / -0.13R | +0.16 | **ATR** |
| MOVER_AVWAP_SCALP | 1311 | 43% / -0.21R | 1311 | 49% / -0.08R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 368 | 44% / -0.33R | 368 | 46% / -0.22R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 181 | 49% / -0.27R | 181 | 51% / -0.17R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 49 | 43% / -0.17R | 49 | 47% / -0.07R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 6334 | 49% / -0.12R | 6334 | 54% / -0.02R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 938 | 41% / -0.22R | 938 | 44% / -0.12R | +0.10 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 120 | 38% / -0.15R | 120 | 48% / -0.06R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 830 | 48% / -0.11R | 830 | 54% / -0.05R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 24 | 46% / -0.11R | 24 | 46% / -0.13R | -0.01 | **FIXED** |
| MEAN_REVERT | 194 | 55% / -0.02R | 194 | 54% / -0.01R | +0.01 | **ATR** |
| RANGE_FADE | 49 | 35% / -0.37R | 49 | 37% / -0.38R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 855 | 46% / -0.15R | 855 | 46% / -0.15R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 50% / -0.21R | 6 | 50% / -0.10R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 9053 | 30% | -0.24R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1311 | 47% | -0.08R | 201 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 74 | 51% | -0.05R | 49 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 141 | 36% / -0.32R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 831 | 35% / -0.17R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 8129 | 36% / -0.16R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1703 | 35% / -0.10R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 761 | 34% / -0.17R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 925 | 39% / -0.05R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 762 | 37% / -0.12R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 899 | 40% / -0.25R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 173 | 29% / -0.40R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 210 | 29% / -0.61R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 161 | 57% / +0.14R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 84 | 40% / -0.17R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 37 | 32% / -0.08R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 178 | 33% / -0.48R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 37 | 27% / -0.37R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 21 | 48% / +0.11R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 11 | 45% / +0.67R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 60 · alerting: **6** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×1023]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 157/6) (sustained 157 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=129, profile_reject=1. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 7/6) (sustained 7 cycles)
- **ALERT** `dark_resolution` — 1 of 128 open dark rows are not being advanced (worst: GRAMUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 181/120) (sustained 181 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.59R (bound 0.3) (streak 744/6) (sustained 744 cycles)
- **ALERT** `tuned_variants` — 732 non-stamps — atr_arm_uncomputable=732 (seen=17246 stamped=1710 skipped=14804) (streak 724/6) (sustained 724 cycles)
- **ALERT** `auto_dispatch` — 140 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=140) (streak 713/3) (sustained 713 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 268369431 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 35 arms current, none stalled; covering 1103/1103 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 2/6) | 2 |
| atr_trail_live_arms | ok | 66 arms current, none stalled; covering 1172/1172 signals (100%) | 0 |
| auto_dispatch | violating | 140 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=140) (streak 713/3) | 713 |
| binance_ip_weight | ok | peak 211/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 84284.10 | 0 |
| candle_coverage | ok | 91/91 symbols with ≥20 15m candles, 91/91 updated within 45m [fresh=91; 78 Tier-1 futures + 13 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1755 dup bars, 0 undedupable; ws 0 out-of-order, 500 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 35 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 35 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | violating | upstream +27 but output +0 (streak 1/72) | 1 |
| dark_atr_trail_arms | ok | no open arms; covering 1942/1960 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 1 of 128 open dark rows are not being advanced (worst: GRAMUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 181/120) | 181 |
| dark_sar_arms | ok | no open arms; covering 1936/1954 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 81311043 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.59R (bound 0.3) (streak 744/6) | 744 |
| emission_controller | ok | last cycle 673s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×1023]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 157/6) | 157 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=129, profile_reject=1. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 7/6) | 7 |
| firestore_read_budget | ok | 1,381 reads/day of 50,000 [engine 1,341, signing 40]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 5280 sealed bars over 44 symbols; 1209 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +222 but output +0 (streak 1/6) | 1 |
| indicator_cache_key | ok | 324702 frozen value(s) avoided; 2308425 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.11R over n=2427 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +36 / upstream +222 | 0 |
| mover_admission_metadata | ok | 919 symbols known, 213 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 13 held, 13 with scan counts, 13 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 6 locked / 6 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 2206428 evicted (sampled: execution:trigger_not_confirmed 400/807908, execution:overextended 400/727736, setup_compat:regime_STRONG_TREND 400/333482) | 0 |
| price_action_lane | ok | 1981555 evaluated, 1995 emitted; layer1 1995 stamped / 0 blind; cooldown=275319, delta_opposed=177607, no_footprint=839411, no_opposing_target=2040, no_sweep=521709, rr_below_floor=163474 | 0 |
| promoted_pair_integrity | ok | 13/13 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.54R over n=1069 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +179 / upstream +222 | 0 |
| sar_alignment_crosscheck | ok | 1176/40741 disagreed (2.9%) | 0 |
| sar_exit_shadow | violating | upstream +222 but output +0 (streak 1/6) | 1 |
| sar_hold_arm | ok | 1835 held arms settled, 165 unscored, 66 still walking (61 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 32/32 resolvable | 0 |
| sar_live_arms | ok | 66 arms current, none stalled; covering 1170/1170 signals (100%) | 0 |
| sar_refresh_budget | ok | 9 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 3 resolved, 29 still mid-window | 0 |
| scan_cycle | ok | last 36.55s, worst 124.41s over 22430 lifetime cycles; lifetime 106 over 60s, 2 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 8.03s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 922299 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 5m ago | 0 |
| snapshot_writer | ok | last cycle 8s ago (20.48s to run, worst 94.49s), 1114 overrun(s) of 15615 cycles, TTL 900s; slowest alerts=2.43s, activity=0.68s, user_positions=0.19s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +18 / upstream +222 | 0 |
| structural_snap | ok | 5830/5830 measured, 26 blind, 0 levels moved (refusals: redetect_cooldown=2207) | 0 |
| structural_veto_lane | ok | 3720 stamped; 0 with no readable level book, 27 with clear air ahead, 2660 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +222 / upstream +27 | 0 |
| tuned_variants | violating | 732 non-stamps — atr_arm_uncomputable=732 (seen=17246 stamped=1710 skipped=14804) (streak 724/6) | 724 |
| unlock_shorts | ok | 7 open, 47 scheduled, calendar 1.0h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 7 — last: ClientOSError: [Errno 32] Broken pipe

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2659599`
- `Path funnel` emissions: `65`
- `Regime distribution` emissions: `65`
- `QUIET_SCALP_BLOCK` events: `158`
- `confidence_gate` events: `8370`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **7**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_depth | 6 | 1868 | 3391 | 4535 | 0 |
| futures_liq | 1 | 6341 | 6341 | 6341 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=475640] state[populated=475640] buckets[few=3, many=475608, some=29] sources[none] quality[none]
- funding_rate: presence[absent=42703, present=432937] state[empty=42703, populated=432937] buckets[few=432937, none=42703] sources[none] quality[none]
- liquidation_clusters: presence[absent=253835, present=221805] state[empty=253835, populated=221805] buckets[few=182987, none=253835, some=38818] sources[none] quality[none]
- oi_snapshot: presence[absent=42703, present=432937] state[empty=42703, populated=432937] buckets[few=390, many=430662, none=42703, some=1885] sources[none] quality[none]
- order_book: presence[absent=135168, present=340472] state[populated=340472, unavailable=135168] buckets[few=340472, none=135168] sources[book_ticker=340472, unavailable=135168] quality[none=135168, top_of_book_only=340472]
- orderblocks: presence[absent=475640] state[empty=475640] buckets[none=475640] sources[measured_dark=475640] quality[none]
- recent_ticks: presence[present=475640] state[populated=475640] buckets[many=475640] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `11.972014427185059` sec
- Median create→first breach: `4029.262246489525` sec
- Median create→terminal: `4029.2622809410095` sec
- Median first breach→terminal: `5.5909156799316406e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 4.0}, "under_180s": {"count": 3, "pct": 6.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 1.6946171641516488 | 1.8539178268856404 | 0.9130545837286062 | 0 | 2 |
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.8 | 0.959278102019279 | 0.9357368398847702 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 5 | 5 | 1.7120263664580673 | 1.9176741018218975 | 0.9072734762431728 | 0 | 4 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 1.013076186556702 | 1.16003509900793 | 0.8700218775178294 | 0 | 2 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 3.0611620795106935 | 1.3326188730473545 | 2.2971024509885622 | 1 | 0 |
| MOVER_TREND_PULLBACK | 28 | 28 | 4.180240865133123 | 3.0 | 1.4285529727143826 | 21 | 6 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 0.9703770819406677 | 1.0647442809414298 | 0.91133223246797 | 0 | 6 |
| RANGE_FADE | 1 | 1 | 0.9362223277732826 | 1.4135304033602485 | 0.6623291055839282 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.1536 | 4679.9356389045715 | 4680.476894497871 |
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -1.2462 | 2330.5397679805756 | 2330.5398449897766 |
| FAILED_AUCTION_RECLAIM | 5 | 5 | 0.0 | 60.0 | 0.0 | 0.0 | -0.9807 | 3947.564059972763 | 3947.5640819072723 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.1002 | 2559.810090661049 | 2559.8101346492767 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.3326 | 1323.0354421138763 | 1323.03546500206 |
| MOVER_TREND_PULLBACK | 28 | 28 | 50.0 | 32.1 | 50.0 | 0.0 | 1.1483 | 3908.9463160037994 | 3908.946352005005 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 12.5 | 62.5 | 12.5 | 0.0 | -0.3673 | 26472.6646515131 | 26472.955966591835 |
| RANGE_FADE | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.4135 | 30.75618314743042 | 30.756206035614014 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 752 | 14 | 385 | 0.0 | 0.0 | None | None | 367 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3726 | 32 | 3267 | 0.0 | 0.0 | None | None | 459 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `35`
- Gating Δ: `-14902`
- No-generation Δ: `-130003`
- Fast failures Δ: `3`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -1.2462, "current_avg_pnl": -1.2462, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.2242, "current_avg_pnl": -0.9807, "current_win_rate": 0.0, "previous_avg_pnl": -1.2049, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 1.1567, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": -1.1567, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.0947, "current_avg_pnl": 1.1483, "current_win_rate": 50.0, "previous_avg_pnl": 1.0536, "previous_win_rate": 48.1, "win_rate_delta": 1.9}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -1.3899, "current_avg_pnl": -0.3673, "current_win_rate": 12.5, "previous_avg_pnl": 1.0226, "previous_win_rate": 60.0, "win_rate_delta": -47.5}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 9, "geometry_changed_delta": 0, "geometry_preserved_delta": 1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": -92, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **DIVERGENCE_CONTINUATION**
- Most promising healthy path: **MOVER_TREND_PULLBACK**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **DIVERGENCE_CONTINUATION**
