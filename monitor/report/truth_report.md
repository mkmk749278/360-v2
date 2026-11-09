# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: DIVERGENCE_CONTINUATION, MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: none
- Recommended next investigation target: **DIVERGENCE_CONTINUATION**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `5` sec (warning=False)
- Latest performance record age: `1238` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 123 | 123 | 123 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 8907 | 8907 | 8101 | 24 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 66034 | 66030 | 32 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 61043 | 61044 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 60533 | 57984 | 3040 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 61075 | 60078 | 1137 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 60914 | 60558 | 382 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 53561 | 53573 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 61220 | 61271 | 10 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 61289 | 59264 | 2819 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 68997 | 73260 | 783 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 66068 | 61823 | 7108 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 60559 | 60560 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 61053 | 61066 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 60475 | 60310 | 215 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 62086 | 60881 | 1582 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 60094 | 60198 | 239 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 52731 | 50310 | 2755 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 53074 | 52784 | 368 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 66001 | 66018 | 13 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 53577 | 53593 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3711 | 3711 | 3035 | 3 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1006 | 1006 | 204 | 3 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 6 | 6 | 6 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 11666 | 11666 | 11345 | 2 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 15 | 15 | 9 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 6248 | 6248 | 5442 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1522 | 1522 | 212 | 91 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 17560 | 17560 | 7884 | 291 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1353 | 1353 | 797 | 42 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3314 | 3314 | 2967 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 896 | 896 | 473 | 12 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1394 | 1394 | 1168 | 32 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 38 | 38 | 11 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=66030): breakout_not_found=36408, basic_filters_failed=16267, move_not_fresh=10039, breakout_stale=2296, retest_proximity_failed=774, volume_spike_missing=240, move_exhausted=6
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=61044): cls_disabled_merged_into_lsr=61044
- **EVAL::DIVERGENCE_CONTINUATION** (total=57984): cvd_divergence_failed=24205, basic_filters_failed=15370, h1_trend_not_aligned=12323, ema_alignment_reject=5190, retest_proximity_failed=683, missing_fvg_or_orderblock=213
- **EVAL::FAILED_AUCTION_RECLAIM** (total=60078): auction_not_detected=37257, basic_filters_failed=15173, reclaim_hold_failed=3563, tail_too_small=2625, regime_blocked=1302, rsi_reject=158
- **EVAL::FUNDING_EXTREME** (total=60558): funding_not_extreme=38931, basic_filters_failed=14668, ema_alignment_reject=2880, missing_funding_rate=2018, rsi_reject=1411, cvd_divergence_failed=352, momentum_reject=262, missing_fvg_or_orderblock=36
- **EVAL::LIQUIDATION_REVERSAL** (total=53573): cascade_threshold_not_met=37930, basic_filters_failed=15217, cvd_divergence_failed=237, rsi_reject=162, missing_fvg_or_orderblock=26, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=61271): no_ma_cross=45032, basic_filters_failed=15389, ma_cross_cooldown=626, ma_cross_htf_misaligned=224
- **EVAL::MEAN_REVERT** (total=59264): no_extension=51367, basic_filters_failed=7897
- **EVAL::MOVER_AVWAP_SCALP** (total=73260): no_mover_leg=27187, no_avwap_tag=22089, basic_filters_failed=16532, avwap_slope_against=4229, avwap_reclaim_no_volume=1780, no_avwap_reclaim=1376, anchor_too_recent=67
- **EVAL::MOVER_TREND_PULLBACK** (total=61823): mover_run_too_small=35398, basic_filters_failed=16386, no_reclaim=8467, no_pullback_tag=1572
- **EVAL::OPENING_RANGE_BREAKOUT** (total=60560): feature_disabled=60560
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=61066): regime_blocked=43873, breakout_not_found=10830, basic_filters_failed=3541, adx_reject=2769, ema_alignment_reject=53
- **EVAL::QUIET_COMPRESSION_BREAK** (total=60310): compression_not_detected=23487, regime_blocked=18394, basic_filters_failed=11616, breakout_not_detected=6204, volume_confirmation_failed=511, rsi_reject=97, missing_fvg_or_orderblock=1
- **EVAL::RANGE_FADE** (total=60881): no_range_edge=52980, basic_filters_failed=7901
- **EVAL::SR_FLIP_RETEST** (total=60198): flip_close_not_confirmed=37989, basic_filters_failed=15150, retest_out_of_zone=1859, h1_break_not_confirmed=1684, regime_blocked=1294, long_break_volume_thin=1138, reclaim_hold_failed=683, long_acceptance_not_held=158, ema_alignment_reject=101, wick_quality_failed=61, whipsaw_flip=48, missing_fvg_or_orderblock=33
- **EVAL::STANDARD** (total=50310): momentum_reject=15528, adx_reject=14307, basic_filters_failed=6215, sweeps_not_detected=5759, macd_reject=5215, ema_alignment_reject=1880, htf_poi_unanchored=1182, invalid_sl_geometry=158, rsi_reject=66
- **EVAL::TREND_PULLBACK** (total=52784): h1_trend_not_aligned=14493, ema_alignment_reject=8861, basic_filters_failed=8619, h1_pullback_not_confirmed=7302, ema_not_tested_prev=4690, no_ema_reclaim_close=3318, rsi_reject=2112, body_conviction_fail=2005, prev_already_below_emas=732, no_prev_low_break=292, prev_already_above_emas=154, no_prev_high_break=76, momentum_flat=58, ema21_not_tagged=35, missing_fvg_or_orderblock=24, momentum_reject=13
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=66018): breakout_not_found=40460, basic_filters_failed=16263, move_not_fresh=5449, breakout_stale=2914, retest_proximity_failed=732, volume_spike_missing=188, missing_fvg_or_orderblock=10, move_exhausted=2
- **EVAL::WHALE_MOMENTUM** (total=53593): momentum_reject=35377, recent_ticks_insufficient=14397, basic_filters_failed=3819

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=68): setup_compat:regime_VOLATILE_UNSUITABLE=62, execution:overextended=5, setup_compat:regime_BREAKOUT_EXPANSION=1
- **FAILED_AUCTION_RECLAIM** (total=1278): execution:overextended=632, setup_compat:regime_STRONG_TREND=478, context_floor=130, setup_compat:regime_VOLATILE_UNSUITABLE=38
- **FUNDING_EXTREME_SIGNAL** (total=864): execution:trigger_not_confirmed=820, context_floor=44
- **LIQUIDATION_REVERSAL** (total=6): execution:trigger_not_confirmed=6
- **LIQUIDITY_SWEEP_REVERSAL** (total=2826): execution:trigger_not_confirmed=1337, execution:overextended=1041, setup_compat:regime_STRONG_TREND=448
- **MA_CROSS_TREND_SHIFT** (total=12): setup_compat:regime_DIRTY_RANGE=5, execution:trigger_not_confirmed=3, setup_compat:regime_CLEAN_RANGE=2, execution:overextended=2
- **MEAN_REVERT** (total=2320): setup_compat:regime_WEAK_TREND=1032, setup_compat:regime_STRONG_TREND=982, execution:overextended=289, entry_quality=17
- **MOVER_AVWAP_SCALP** (total=1187): execution:overextended=932, entry_quality=222, execution:trigger_not_confirmed=33
- **MOVER_TREND_PULLBACK** (total=8073): execution:trigger_not_confirmed=3775, execution:overextended=2798, entry_quality=1500
- **QUIET_COMPRESSION_BREAK** (total=3): execution:trigger_not_confirmed=3
- **RANGE_FADE** (total=1783): setup_compat:regime_WEAK_TREND=903, setup_compat:regime_STRONG_TREND=509, execution:overextended=205, setup_compat:regime_VOLATILE_UNSUITABLE=166
- **TREND_PULLBACK_EMA** (total=1220): setup_compat:regime_CLEAN_RANGE=834, setup_compat:regime_DIRTY_RANGE=351, entry_quality=35
- **VOLUME_SURGE_BREAKOUT** (total=13): execution:overextended=13

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 168130 | 48.9% |
| QUIET | 70998 | 20.7% |
| TRENDING_DOWN | 57626 | 16.8% |
| TRENDING_UP | 37011 | 10.8% |
| VOLATILE | 9761 | 2.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **282**
- Average confidence gap to threshold: **14.94** (samples=282) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: AVAXUSDT=28, XMRUSDT=24, HYPEUSDT=24, BTCUSDT=22, AAVEUSDT=16, SOLUSDT=15, ZECUSDT=14, TAOUSDT=13, ASTERUSDT=12, CTUSDT=11

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 65 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 53 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 193 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 46 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 21 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 11 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 4 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 102 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 9 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 14 |
| MEAN_REVERT | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 253 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 362 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1880 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 25 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3038 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 206 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 133 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 211 |
| SR_FLIP_RETEST | filtered | min_confidence | 108 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 3 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 56 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 20 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 1 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 73 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 15 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 65 | 48.84 | 63.95 | 15.11 | 20.57 | 19.15 | 18.69 | 1.91 | 16.87 |
| DIVERGENCE_CONTINUATION | kept | 53 | 68.21 | 65.00 | -3.21 | 20.46 | 19.65 | 17.34 | 1.34 | -1.82 |
| FAILED_AUCTION_RECLAIM | filtered | 239 | 45.89 | 63.25 | 17.36 | 20.48 | 18.50 | 20.00 | 2.57 | 11.15 |
| FAILED_AUCTION_RECLAIM | kept | 21 | 68.00 | 65.00 | -3.00 | 21.26 | 19.41 | 20.00 | 1.90 | 1.61 |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 49.59 | 61.73 | 12.14 | 20.17 | 13.83 | 17.02 | 3.27 | 6.25 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 69.38 | 65.00 | -4.38 | 20.03 | 14.00 | 17.00 | 4.75 | 0.30 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 102 | 40.60 | 64.33 | 23.73 | 20.10 | 18.00 | 17.64 | 2.28 | 16.23 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 70.30 | 65.00 | -5.30 | 22.54 | 20.00 | 16.46 | 0.44 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 75.50 | 65.00 | -10.50 | 21.20 | 17.80 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 14 | 56.60 | 65.00 | 8.40 | 20.50 | 14.00 | 15.00 | 0.00 | 15.80 |
| MEAN_REVERT | kept | 1 | 75.70 | 65.00 | -10.70 | 20.60 | 16.40 | 16.70 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 254 | 59.33 | 64.65 | 5.32 | 21.43 | 17.00 | 15.80 | 3.71 | 12.18 |
| MOVER_AVWAP_SCALP | kept | 362 | 80.46 | 65.00 | -15.46 | 20.01 | 15.92 | 15.80 | 4.34 | 3.76 |
| MOVER_TREND_PULLBACK | filtered | 1905 | 56.09 | 64.18 | 8.09 | 19.83 | 18.32 | 15.80 | 4.07 | 18.73 |
| MOVER_TREND_PULLBACK | kept | 3038 | 76.22 | 65.00 | -11.22 | 20.18 | 18.68 | 15.80 | 4.21 | 1.51 |
| QUIET_COMPRESSION_BREAK | filtered | 339 | 48.27 | 64.87 | 16.60 | 21.40 | 19.54 | 20.00 | 0.00 | 11.62 |
| QUIET_COMPRESSION_BREAK | kept | 211 | 73.81 | 65.00 | -8.81 | 21.65 | 19.52 | 20.00 | 0.00 | 1.23 |
| SR_FLIP_RETEST | filtered | 111 | 54.39 | 65.00 | 10.61 | 21.21 | 20.00 | 15.70 | 1.65 | 14.81 |
| SR_FLIP_RETEST | kept | 56 | 70.11 | 65.00 | -5.11 | 22.48 | 20.00 | 16.72 | 1.88 | 1.36 |
| TREND_PULLBACK_EMA | filtered | 21 | 58.70 | 65.00 | 6.30 | 20.49 | 19.87 | 17.31 | 4.45 | 13.66 |
| TREND_PULLBACK_EMA | kept | 73 | 78.34 | 65.00 | -13.34 | 19.96 | 19.79 | 18.78 | 4.72 | -0.24 |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 50.84 | 62.87 | 12.03 | 21.13 | 18.01 | 20.00 | 3.77 | 7.45 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 75.00 | 65.00 | -10.00 | 20.70 | 18.80 | 20.00 | 6.00 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 65 | 48.84 | 20.69 | 11.69 | 6.23 | 13.42 | 6.25 | 7.37 | 1.91 |
| DIVERGENCE_CONTINUATION | kept | 53 | 68.21 | 21.23 | 13.66 | 3.74 | 13.40 | 6.12 | 9.21 | 1.34 |
| FAILED_AUCTION_RECLAIM | filtered | 239 | 45.89 | 23.18 | 16.66 | 5.42 | 13.69 | 5.58 | 4.56 | 2.57 |
| FAILED_AUCTION_RECLAIM | kept | 21 | 68.00 | 19.29 | 17.43 | 5.57 | 13.90 | 7.19 | 6.47 | 1.90 |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 49.59 | 25.00 | 8.00 | 5.18 | 11.73 | 8.73 | 4.85 | 3.27 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 69.38 | 23.00 | 14.00 | 3.00 | 9.00 | 8.88 | 7.05 | 4.75 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 102 | 40.60 | 23.20 | 14.59 | 4.82 | 12.75 | 6.09 | 5.01 | 2.28 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 70.30 | 24.33 | 16.22 | 4.00 | 11.89 | 5.00 | 8.41 | 0.44 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 75.50 | 17.00 | 14.00 | 12.00 | 14.00 | 8.50 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 14 | 56.60 | 21.00 | 18.00 | 9.00 | 13.00 | 5.00 | 6.30 | 0.00 |
| MEAN_REVERT | kept | 1 | 75.70 | 17.00 | 18.00 | 15.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 254 | 59.33 | 17.58 | 18.00 | 12.45 | 14.05 | 6.56 | 6.72 | 3.71 |
| MOVER_AVWAP_SCALP | kept | 362 | 80.46 | 18.45 | 18.01 | 12.77 | 14.13 | 7.72 | 9.00 | 4.34 |
| MOVER_TREND_PULLBACK | filtered | 1905 | 56.09 | 18.07 | 18.03 | 7.69 | 12.63 | 6.07 | 8.59 | 4.07 |
| MOVER_TREND_PULLBACK | kept | 3038 | 76.22 | 19.37 | 18.00 | 7.85 | 12.59 | 6.57 | 9.45 | 4.21 |
| QUIET_COMPRESSION_BREAK | filtered | 339 | 48.27 | 18.34 | 16.43 | 12.19 | 14.04 | 6.50 | 4.51 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 211 | 73.81 | 18.59 | 17.03 | 11.47 | 14.01 | 6.30 | 8.68 | 0.00 |
| SR_FLIP_RETEST | filtered | 111 | 54.39 | 19.86 | 17.73 | 3.35 | 13.70 | 5.47 | 7.43 | 1.65 |
| SR_FLIP_RETEST | kept | 56 | 70.11 | 21.14 | 17.64 | 4.71 | 14.57 | 5.00 | 7.23 | 1.88 |
| TREND_PULLBACK_EMA | filtered | 21 | 58.70 | 10.62 | 18.00 | 7.86 | 14.14 | 8.57 | 8.71 | 4.45 |
| TREND_PULLBACK_EMA | kept | 73 | 78.34 | 18.01 | 18.00 | 7.75 | 14.62 | 7.38 | 9.42 | 4.72 |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 50.84 | 19.13 | 16.93 | 12.00 | 13.60 | 5.00 | 2.86 | 3.77 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 75.00 | 25.00 | 18.00 | 12.00 | 14.00 | 5.00 | 10.00 | 6.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 65 | 48.84 | 0.00 | 0.00 | 0.62 | 0.00 | 3.14 | 0.00 | 0.00 | 0.00 | **3.76** |
| DIVERGENCE_CONTINUATION | kept | 53 | 68.21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 239 | 45.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.90 | 0.00 | 0.00 | 0.00 | **0.90** |
| FAILED_AUCTION_RECLAIM | kept | 21 | 68.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 49.59 | 0.00 | 0.00 | 0.73 | 0.00 | 1.31 | 0.00 | 0.00 | 0.00 | **2.04** |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 69.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 102 | 40.60 | 0.00 | 0.00 | 0.77 | 0.00 | 0.24 | 0.00 | 0.00 | 0.00 | **1.01** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 70.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 75.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 14 | 56.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 1 | 75.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 254 | 59.33 | 1.35 | 0.00 | 0.47 | 0.00 | 2.31 | 0.20 | 0.00 | 0.28 | **4.61** |
| MOVER_AVWAP_SCALP | kept | 362 | 80.46 | 0.08 | 0.00 | 0.47 | 0.00 | 0.52 | 0.57 | 0.00 | 0.09 | **1.73** |
| MOVER_TREND_PULLBACK | filtered | 1905 | 56.09 | 0.11 | 0.00 | 0.30 | 0.00 | 0.13 | 0.05 | 0.00 | 0.00 | **0.59** |
| MOVER_TREND_PULLBACK | kept | 3038 | 76.22 | 0.01 | 0.00 | 0.40 | 0.00 | 0.19 | 0.03 | 0.00 | 0.00 | **0.63** |
| QUIET_COMPRESSION_BREAK | filtered | 339 | 48.27 | 0.00 | 0.00 | 0.55 | 0.00 | 0.08 | 0.33 | 0.00 | 4.97 | **5.93** |
| QUIET_COMPRESSION_BREAK | kept | 211 | 73.81 | 0.00 | 0.00 | 0.34 | 0.00 | 0.33 | 0.14 | 0.00 | 0.00 | **0.81** |
| SR_FLIP_RETEST | filtered | 111 | 54.39 | 0.00 | 0.00 | 0.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.39 | **0.82** |
| SR_FLIP_RETEST | kept | 56 | 70.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | **0.06** |
| TREND_PULLBACK_EMA | filtered | 21 | 58.70 | 0.00 | 0.00 | 1.90 | 0.00 | 1.03 | 0.48 | 0.00 | 0.00 | **3.41** |
| TREND_PULLBACK_EMA | kept | 73 | 78.34 | 0.00 | 0.00 | 0.11 | 0.00 | 0.30 | 0.00 | 0.00 | 0.00 | **0.41** |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 50.84 | 0.00 | 0.00 | 2.77 | 0.00 | 0.00 | 0.00 | 0.00 | 1.68 | **4.45** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 75.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **180475 held of 787818 seen** across 21 strategies; 4086 cells past the sample floor; **2173 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 47855 | 619/47236/0 | 43% | -0.19 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.35R) |
| MOVER_AVWAP_SCALP | 23916 | 188/23728/0 | 43% | -0.22 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 13943 | 199/13744/0 | 44% | -0.14 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | LONDON/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 13697 | 149/13548/0 | 37% | -0.30 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 11981 | 69/11912/0 | 38% | -0.30 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 9999 | 106/9893/0 | 36% | -0.45 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 8455 | 424/8031/0 | 44% | -0.14 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8060 | 0/0/8060 | 44% | -0.06 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+1.28R) | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL (-0.86R) |
| SHADOW_RANGE_FADE | 7547 | 0/0/7547 | 36% | -0.13 | NY/RANGE/NORMAL/BTC_NEUTRAL (+0.37R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.28R) |
| SHADOW_FUNDING_FADE | 6967 | 0/0/6967 | 34% | -0.41 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-0.00R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-0.98R) |
| SR_FLIP_RETEST | 5890 | 23/5867/0 | 46% | -0.28 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.30R) |
| MEAN_REVERT | 5397 | 69/5328/0 | 37% | -0.33 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| FUNDING_EXTREME_SIGNAL | 3965 | 2/3963/0 | 31% | -0.47 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 3770 | 0/3770/0 | 30% | -0.37 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| RANGE_FADE | 2214 | 6/2208/0 | 41% | -0.19 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1651 | 0/0/1651 | 53% | -0.07 | ASIA/RANGE/EXPANDED/BTC_NEUTRAL (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 532 | 0/532/0 | 36% | -0.24 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 204 | 32/172/0 | 43% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 58 | 2/56/0 | 45% | +0.15 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `LIQUIDATION_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL` +2.71R (n=23, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 360 | 27% / -0.57R | 360 | 52% / -0.09R | +0.47 | **ATR** |
| TREND_PULLBACK_EMA | 1154 | 37% / -0.38R | 1154 | 49% / -0.09R | +0.30 | **ATR** |
| LIQUIDATION_REVERSAL | 33 | 24% / -0.61R | 33 | 45% / -0.35R | +0.26 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1544 | 42% / -0.37R | 1544 | 56% / -0.12R | +0.25 | **ATR** |
| MA_CROSS_TREND_SHIFT | 61 | 43% / -0.21R | 61 | 48% / -0.06R | +0.15 | **ATR** |
| SR_FLIP_RETEST | 605 | 45% / -0.30R | 605 | 50% / -0.16R | +0.14 | **ATR** |
| MOVER_AVWAP_SCALP | 2523 | 44% / -0.18R | 2523 | 50% / -0.05R | +0.12 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 203 | 37% / -0.17R | 203 | 48% / -0.05R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 8810 | 48% / -0.14R | 8810 | 53% / -0.02R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1461 | 41% / -0.22R | 1461 | 43% / -0.12R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| RANGE_FADE | 119 | 39% / -0.08R | 119 | 47% / +0.01R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1690 | 48% / -0.12R | 1690 | 53% / -0.06R | +0.06 | **ATR** |
| MEAN_REVERT | 432 | 47% / -0.14R | 432 | 46% / -0.15R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1481 | 46% / -0.14R | 1481 | 46% / -0.14R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 13 | 62% / -0.06R | 13 | 62% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11721 | 28% | -0.25R | 312 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2523 | 48% | -0.05R | 236 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 128 | 49% | -0.05R | 68 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1800 | 38% / -0.15R | +0.86 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1506 | 32% / -0.26R | +0.81 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3073 | 35% / -0.19R | +0.65 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10716 | 36% / -0.21R | +0.32 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1967 | 37% / -0.14R | +0.14 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1421 | 35% / -0.14R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1209 | 32% / -0.26R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 300 | 31% / -0.36R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 463 | 32% / -0.21R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 357 | 48% / -0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 88 | 44% / +0.02R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 527 | 33% / -0.34R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 98 | 29% / -0.37R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 42 | 45% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 22 | 45% / +0.62R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×159]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 162/6) (sustained 162 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 162/6) (sustained 162 cycles)
- **ALERT** `tuned_variants` — 171 non-stamps — atr_arm_uncomputable=171 (seen=4504 stamped=566 skipped=3767) (streak 162/6) (sustained 162 cycles)
- **ALERT** `auto_dispatch` — 44 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=45) (streak 160/3) (sustained 160 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 42 fed / 0 quiet / 0 never delivered of 42 subscribed; 26521052 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | no open arms; covering 2077/2077 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | no open arms; covering 1079/1079 signals (100%) | 0 |
| auto_dispatch | violating | 44 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=45) (streak 160/3) | 160 |
| binance_ip_weight | ok | peak 350/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 74271.10 | 0 |
| candle_coverage | ok | 92/92 symbols with ≥20 15m candles, 92/92 updated within 45m [fresh=92; 73 Tier-1 futures + 19 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 618 dup bars, 0 undedupable; ws 0 out-of-order, 202 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +103 / upstream +20 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1503/1522 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 7 of 146 open dark rows are not being advanced (worst: SIGNUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 104/120) | 104 |
| dark_sar_arms | ok | no open arms; covering 1495/1514 signals (99%) | 0 |
| depth_feed | ok | 42/42 books fresh (stale 0, never 0, thin 0); 5791232 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 162/6) | 162 |
| emission_controller | ok | last cycle 830s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×159]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 162/6) | 162 |
| entry_quality_effective | ok | 4887 evaluated, 1742 suppressed, 3144 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,342 reads/day of 50,000 [engine 1,318, signing 24]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 5014 sealed bars over 42 symbols; 1282 incomplete, 1 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +20 / upstream +390 | 0 |
| indicator_cache_key | ok | 49072 frozen value(s) avoided; 85562 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.34R over n=5328 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +38 / upstream +390 | 0 |
| mover_admission_metadata | ok | 942 symbols known, 235 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 19 held, 19 with scan counts, 18 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2126 rows held, 3444244 evicted (sampled: execution:trigger_not_confirmed 289/1215290, execution:overextended 289/1073858, setup_compat:regime_STRONG_TREND 289/588270) | 0 |
| price_action_lane | ok | 319900 evaluated, 483 emitted; layer1 483 stamped / 0 blind; cooldown=42004, delta_opposed=26110, no_footprint=115515, no_opposing_target=1259, no_sweep=110641, rr_below_floor=23888 | 0 |
| promoted_pair_integrity | ok | 19/19 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.19R over n=2208 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +19 / upstream +390 | 0 |
| sar_alignment_crosscheck | ok | 244/10913 disagreed (2.2%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +390 | 0 |
| sar_hold_arm | ok | 1866 held arms settled, 134 unscored, 48 still walking (40 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 5/108 unfetchable (5%); top cause: gap or duplicate bar in the 15m window; symbols: HANAUSDT, RSRUSDT | 0 |
| sar_live_arms | ok | 48 arms current, none stalled; covering 1078/1078 signals (100%) | 0 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 508 records await one (103 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| scan_cycle | ok | last 105.11s, worst 248.86s over 3778 lifetime cycles; lifetime 186 over 60s, 32 over 120s; recent 2/0 warn/kill breaches in 20/20 cycles; heartbeat age 2.52s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 124675 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 2s ago (0.51s to run, worst 156.99s), 568 overrun(s) of 3593 cycles, TTL 900s; slowest data_intake=0.17s, signals=0.14s, pair_context=0.05s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=17, gate reads=0, withheld=17) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +186 / upstream +390 | 0 |
| structural_snap | ok | 6000/6000 measured, 30 blind, 0 levels moved (refusals: redetect_cooldown=565) | 0 |
| structural_veto_lane | ok | 1063 stamped; 0 with no readable level book, 45 with clear air ahead, 844 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +390 / upstream +20 | 0 |
| tuned_variants | violating | 171 non-stamps — atr_arm_uncomputable=171 (seen=4504 stamped=566 skipped=3767) (streak 162/6) | 162 |
| unlock_shorts | ok | 14 open, 43 scheduled, calendar 18.1h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 19 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1693796`
- `Path funnel` emissions: `41`
- `Regime distribution` emissions: `41`
- `QUIET_SCALP_BLOCK` events: `282`
- `confidence_gate` events: `6906`
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
| futures | 1 | 7599 | 7599 | 7599 | 0 |
| futures_aggtrade | 11 | 15886 | 29447 | 47443 | 0 |
| futures_depth | 1 | 11482 | 11482 | 11482 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=251511] state[populated=251511] buckets[many=251415, some=96] sources[none] quality[none]
- funding_rate: presence[absent=30122, present=221389] state[empty=30122, populated=221389] buckets[few=221389, none=30122] sources[none] quality[none]
- liquidation_clusters: presence[absent=137767, present=113744] state[empty=137767, populated=113744] buckets[few=96519, none=137767, some=17225] sources[none] quality[none]
- oi_snapshot: presence[absent=29640, present=221871] state[empty=29640, populated=221871] buckets[few=211, many=220392, none=29640, some=1268] sources[none] quality[none]
- order_book: presence[absent=85626, present=165885] state[populated=165885, unavailable=85626] buckets[few=165885, none=85626] sources[book_ticker=165885, unavailable=85626] quality[none=85626, top_of_book_only=165885]
- orderblocks: presence[absent=251511] state[empty=251511] buckets[none=251511] sources[measured_dark=251511] quality[none]
- recent_ticks: presence[present=251511] state[populated=251511] buckets[many=251511] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.655151844024658` sec
- Median create→first breach: `4956.7000341415405` sec
- Median create→terminal: `4956.700102090836` sec
- Median first breach→terminal: `6.389617919921875e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 1.6}, "under_180s": {"count": 1, "pct": 1.6}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 1.6}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 9 | 9 | 0.8000000000000085 | 0.9611131902153563 | 0.8700718921196819 | 0 | 7 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 0.8497118909744314 | 1.0179341133004915 | 0.8384688611653974 | 0 | 3 |
| MEAN_REVERT | 1 | 1 | 0.8904406292287028 | 1.095641646489106 | 0.8127115577269695 | 0 | 1 |
| MOVER_AVWAP_SCALP | 4 | 4 | 1.9809828352288483 | 2.189620637167278 | 0.849799867301748 | 1 | 3 |
| MOVER_TREND_PULLBACK | 30 | 30 | 3.298915069910543 | 3.0 | 1.1545631371752916 | 19 | 10 |
| QUIET_COMPRESSION_BREAK | 11 | 11 | 1.2766630765753164 | 1.3962024965325974 | 0.8981611633429076 | 0 | 6 |
| SR_FLIP_RETEST | 2 | 2 | 0.7108461499220085 | 0.523718419037787 | 1.3571360621694564 | 2 | 0 |
| TREND_PULLBACK_EMA | 3 | 3 | 1.0988378534333458 | 1.2156474374845265 | 0.903911627294762 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 9 | 9 | 11.1 | 11.1 | 11.1 | 0.0 | 0.2013 | 5263.650692939758 | 5263.6507568359375 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -0.8212 | 11115.586584806442 | 11115.586725950241 |
| MEAN_REVERT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.8904 | 3083.9002120494843 | 3083.900269985199 |
| MOVER_AVWAP_SCALP | 4 | 4 | 50.0 | 50.0 | 50.0 | 0.0 | 0.496 | 9273.512850522995 | 9274.159363508224 |
| MOVER_TREND_PULLBACK | 30 | 30 | 10.0 | 56.7 | 10.0 | 0.0 | -1.8611 | 2326.800752878189 | 2326.8008890151978 |
| QUIET_COMPRESSION_BREAK | 11 | 11 | 27.3 | 27.3 | 27.3 | 0.0 | 0.8538 | 18632.906650066376 | 18660.295742988586 |
| SR_FLIP_RETEST | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.2019 | 23773.767231464386 | 23774.212784409523 |
| TREND_PULLBACK_EMA | 3 | 3 | 33.3 | 33.3 | 33.3 | 0.0 | 1.0286 | 3357.1589200496674 | 3357.4197030067444 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 896 | 12 | 473 | 50.0 | 50.0 | 23773.767231464386 | 23774.212784409523 | 423 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1394 | 32 | 1168 | 33.3 | 33.3 | 3357.1589200496674 | 3357.4197030067444 | 226 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `97`
- Gating Δ: `4186`
- No-generation Δ: `196461`
- Fast failures Δ: `1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.1071, "current_avg_pnl": 0.2013, "current_win_rate": 11.1, "previous_avg_pnl": 0.3084, "previous_win_rate": 33.3, "win_rate_delta": -22.2}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.1224, "current_avg_pnl": -0.8212, "current_win_rate": 0.0, "previous_avg_pnl": -0.9436, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 2.0819, "current_avg_pnl": 0.496, "current_win_rate": 50.0, "previous_avg_pnl": -1.5859, "previous_win_rate": 0.0, "win_rate_delta": 50.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -2.9277, "current_avg_pnl": -1.8611, "current_win_rate": 10.0, "previous_avg_pnl": 1.0666, "previous_win_rate": 44.4, "win_rate_delta": -34.4}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.4216, "current_avg_pnl": 0.8538, "current_win_rate": 27.3, "previous_avg_pnl": 0.4322, "previous_win_rate": 44.4, "win_rate_delta": -17.1}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 1.0286, "current_avg_pnl": 1.0286, "current_win_rate": 33.3, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 33.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": -134, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -27617.93, "median_terminal_delta_sec": -27617.49, "sl_rate_delta": -50.0, "win_rate_delta": 50.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": -39, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 3357.16, "median_terminal_delta_sec": 3357.42, "sl_rate_delta": 33.3, "win_rate_delta": 33.3}}`

## Recommended operator focus
- Most suspicious degradation: **DIVERGENCE_CONTINUATION**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **DIVERGENCE_CONTINUATION**
