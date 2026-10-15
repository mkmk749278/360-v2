# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, MOVER_AVWAP_SCALP
- Top promising signals/paths: QUIET_COMPRESSION_BREAK
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `1263` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 120 | 120 | 120 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 16280 | 16280 | 15053 | 30 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 85465 | 85465 | 28 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 66750 | 66751 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 66329 | 63030 | 3706 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 66798 | 66082 | 783 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 68362 | 68277 | 107 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 59059 | 59068 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 66872 | 66909 | 6 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 66918 | 64745 | 2966 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 90695 | 94979 | 1617 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 85498 | 74763 | 15855 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 68056 | 68056 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 66758 | 66764 | 25 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 66306 | 66131 | 193 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 67720 | 65704 | 2532 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 65976 | 66013 | 263 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 56826 | 53625 | 3400 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 57032 | 56451 | 678 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 85418 | 85440 | 20 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 59071 | 59101 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4022 | 4022 | 3683 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 398 | 398 | 235 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 4 | 4 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 19165 | 19165 | 18621 | 7 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 10 | 10 | 5 | 4 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8812 | 8812 | 8011 | 3 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 4322 | 4322 | 2594 | 131 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 47148 | 47148 | 28952 | 459 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 102 | 102 | 86 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1032 | 1032 | 921 | 12 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 6442 | 6442 | 6063 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1216 | 1216 | 801 | 7 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3608 | 3608 | 3225 | 26 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 164 | 164 | 147 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=85465): breakout_not_found=42082, basic_filters_failed=18639, move_not_fresh=17535, breakout_stale=4662, retest_proximity_failed=2204, volume_spike_missing=327, move_exhausted=15, rsi_reject=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=66751): cls_disabled_merged_into_lsr=66751
- **EVAL::DIVERGENCE_CONTINUATION** (total=63030): cvd_divergence_failed=33833, basic_filters_failed=12896, h1_trend_not_aligned=10296, ema_alignment_reject=4504, retest_proximity_failed=1041, missing_fvg_or_orderblock=460
- **EVAL::FAILED_AUCTION_RECLAIM** (total=66082): auction_not_detected=45683, basic_filters_failed=12577, reclaim_hold_failed=3989, tail_too_small=2094, regime_blocked=1733, rsi_reject=6
- **EVAL::FUNDING_EXTREME** (total=68277): funding_not_extreme=51058, basic_filters_failed=12601, missing_funding_rate=3144, ema_alignment_reject=951, rsi_reject=360, momentum_reject=90, cvd_divergence_failed=60, missing_fvg_or_orderblock=13
- **EVAL::LIQUIDATION_REVERSAL** (total=59068): cascade_threshold_not_met=44994, basic_filters_failed=13499, cvd_divergence_failed=279, rsi_reject=268, missing_fvg_or_orderblock=20, volume_spike_missing=8
- **EVAL::MA_CROSS_TREND_SHIFT** (total=66909): no_ma_cross=52781, basic_filters_failed=12905, ma_cross_htf_misaligned=770, ma_cross_cooldown=453
- **EVAL::MEAN_REVERT** (total=64745): no_extension=56252, basic_filters_failed=8493
- **EVAL::MOVER_AVWAP_SCALP** (total=94979): no_avwap_tag=43639, no_mover_leg=22070, basic_filters_failed=18784, avwap_slope_against=5695, avwap_reclaim_no_volume=3024, no_avwap_reclaim=1629, anchor_too_recent=138
- **EVAL::MOVER_TREND_PULLBACK** (total=74763): mover_run_too_small=35826, basic_filters_failed=18708, no_reclaim=16856, no_pullback_tag=3373
- **EVAL::OPENING_RANGE_BREAKOUT** (total=68056): feature_disabled=68056
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=66764): regime_blocked=37137, breakout_not_found=21222, basic_filters_failed=5485, adx_reject=2846, ema_alignment_reject=73, rsi_reject=1
- **EVAL::QUIET_COMPRESSION_BREAK** (total=66131): regime_blocked=31218, compression_not_detected=21281, basic_filters_failed=7086, breakout_not_detected=6014, volume_confirmation_failed=524, rsi_reject=6, missing_fvg_or_orderblock=2
- **EVAL::RANGE_FADE** (total=65704): no_range_edge=57209, basic_filters_failed=8495
- **EVAL::SR_FLIP_RETEST** (total=66013): flip_close_not_confirmed=44187, basic_filters_failed=12562, h1_break_not_confirmed=2532, long_break_volume_thin=2194, retest_out_of_zone=1878, regime_blocked=1729, reclaim_hold_failed=563, ema_alignment_reject=140, long_acceptance_not_held=104, wick_quality_failed=57, whipsaw_flip=51, missing_fvg_or_orderblock=16
- **EVAL::STANDARD** (total=53625): momentum_reject=16115, adx_reject=14557, basic_filters_failed=6334, sweeps_not_detected=6292, ema_alignment_reject=5512, macd_reject=3711, htf_poi_unanchored=932, rsi_reject=120, invalid_sl_geometry=49, mtf_reject=3
- **EVAL::TREND_PULLBACK** (total=56451): h1_trend_not_aligned=11533, ema_alignment_reject=9658, basic_filters_failed=8426, h1_pullback_not_confirmed=8063, ema_not_tested_prev=6645, no_ema_reclaim_close=5005, body_conviction_fail=2927, rsi_reject=2277, prev_already_below_emas=994, no_prev_low_break=522, momentum_flat=129, prev_already_above_emas=101, ema21_not_tagged=78, no_prev_high_break=44, missing_fvg_or_orderblock=40, momentum_reject=9
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=85440): breakout_not_found=57110, basic_filters_failed=18636, move_not_fresh=4439, breakout_stale=3897, retest_proximity_failed=1175, volume_spike_missing=161, move_exhausted=18, missing_fvg_or_orderblock=4
- **EVAL::WHALE_MOMENTUM** (total=59101): momentum_reject=42944, recent_ticks_insufficient=12937, basic_filters_failed=3220

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=287): setup_compat:regime_VOLATILE_UNSUITABLE=264, setup_compat:regime_BREAKOUT_EXPANSION=18, execution:overextended=5
- **FAILED_AUCTION_RECLAIM** (total=1404): execution:overextended=793, setup_compat:regime_STRONG_TREND=559, context_floor=40, setup_compat:regime_VOLATILE_UNSUITABLE=12
- **FUNDING_EXTREME_SIGNAL** (total=333): execution:trigger_not_confirmed=324, context_floor=9
- **LIQUIDATION_REVERSAL** (total=4): execution:trigger_not_confirmed=4
- **LIQUIDITY_SWEEP_REVERSAL** (total=5702): setup_compat:regime_STRONG_TREND=2092, execution:overextended=2039, execution:trigger_not_confirmed=1571
- **MA_CROSS_TREND_SHIFT** (total=4): setup_compat:regime_DIRTY_RANGE=2, execution:overextended=1, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=6091): setup_compat:regime_WEAK_TREND=3026, setup_compat:regime_STRONG_TREND=2780, execution:overextended=278, entry_quality=7
- **MOVER_AVWAP_SCALP** (total=2101): execution:overextended=1509, execution:trigger_not_confirmed=324, entry_quality=268
- **MOVER_TREND_PULLBACK** (total=16326): execution:trigger_not_confirmed=7957, execution:overextended=6308, entry_quality=2061
- **QUIET_COMPRESSION_BREAK** (total=62): execution:trigger_not_confirmed=62
- **RANGE_FADE** (total=4823): setup_compat:regime_WEAK_TREND=2470, setup_compat:regime_STRONG_TREND=1607, setup_compat:regime_VOLATILE_UNSUITABLE=401, execution:overextended=329, setup_compat:regime_BREAKOUT_EXPANSION=10, context_edge=6
- **TREND_PULLBACK_EMA** (total=3001): setup_compat:regime_CLEAN_RANGE=1931, setup_compat:regime_DIRTY_RANGE=911, entry_quality=122, setup_compat:regime_VOLATILE_UNSUITABLE=37

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 183543 | 38.2% |
| TRENDING_DOWN | 128339 | 26.7% |
| QUIET | 95137 | 19.8% |
| TRENDING_UP | 59615 | 12.4% |
| VOLATILE | 14110 | 2.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **266**
- Average confidence gap to threshold: **12.40** (samples=266) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ETHUSDT=42, AAVEUSDT=39, LITUSDT=35, WLDUSDT=31, LINKUSDT=26, 1000PEPEUSDT=13, ZROUSDT=13, SUIUSDT=9, RLCUSDT=9, UNIUSDT=8

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 219 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 231 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 78 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 38 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 21 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 160 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 20 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 34 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 4 |
| MEAN_REVERT | filtered | min_confidence | 15 |
| MEAN_REVERT | kept | min_confidence_pass | 14 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 154 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 3 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 740 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 3066 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 143 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 5848 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 16 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 32 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 4 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 35 |
| SR_FLIP_RETEST | filtered | min_confidence | 140 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 17 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 54 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 35 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 10 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 99 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 16 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 222 | 52.68 | 62.73 | 10.05 | 20.13 | 19.40 | 18.03 | 1.41 | 15.82 |
| DIVERGENCE_CONTINUATION | kept | 231 | 68.47 | 65.00 | -3.47 | 20.50 | 19.72 | 18.24 | 1.40 | 3.09 |
| FAILED_AUCTION_RECLAIM | filtered | 116 | 50.90 | 63.71 | 12.81 | 20.87 | 18.63 | 20.00 | 3.28 | 5.70 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 67.70 | 65.00 | -2.70 | 20.20 | 18.90 | 20.00 | 6.00 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 21 | 50.54 | 61.57 | 11.03 | 19.86 | 15.34 | 17.00 | 2.86 | 13.42 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 80.30 | 65.00 | -15.30 | 16.80 | 14.00 | 17.00 | 7.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 180 | 50.71 | 64.53 | 13.82 | 21.26 | 18.70 | 17.61 | 1.14 | 6.22 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 34 | 69.19 | 65.00 | -4.19 | 22.01 | 19.97 | 19.22 | 2.62 | 1.38 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 58.10 | 61.00 | 2.90 | 21.10 | 19.50 | 15.80 | 0.00 | 14.40 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 72.70 | 65.00 | -7.70 | 21.52 | 17.80 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 15 | 54.77 | 61.80 | 7.03 | 18.43 | 14.60 | 15.40 | 0.00 | 15.10 |
| MEAN_REVERT | kept | 14 | 68.00 | 65.00 | -3.00 | 19.71 | 17.60 | 14.29 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 157 | 60.58 | 64.66 | 4.08 | 21.09 | 17.72 | 15.80 | 4.68 | 18.95 |
| MOVER_AVWAP_SCALP | kept | 740 | 81.71 | 65.00 | -16.71 | 20.72 | 15.68 | 15.80 | 4.53 | 4.25 |
| MOVER_TREND_PULLBACK | filtered | 3209 | 56.15 | 64.24 | 8.09 | 20.49 | 18.49 | 15.80 | 3.83 | 19.34 |
| MOVER_TREND_PULLBACK | kept | 5848 | 76.54 | 65.00 | -11.54 | 20.05 | 18.48 | 15.80 | 4.08 | 1.23 |
| POST_DISPLACEMENT_CONTINUATION | kept | 16 | 90.03 | 65.00 | -25.03 | 21.84 | 20.00 | 18.20 | 5.53 | -3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 36 | 48.05 | 64.56 | 16.51 | 22.16 | 18.79 | 20.00 | 0.00 | 17.22 |
| QUIET_COMPRESSION_BREAK | kept | 35 | 76.07 | 65.00 | -11.07 | 22.42 | 19.17 | 20.00 | 0.00 | 1.45 |
| SR_FLIP_RETEST | filtered | 157 | 55.21 | 64.82 | 9.61 | 20.62 | 20.00 | 15.39 | 1.62 | 12.97 |
| SR_FLIP_RETEST | kept | 54 | 71.68 | 65.00 | -6.68 | 19.92 | 20.00 | 16.51 | 1.66 | 2.83 |
| TREND_PULLBACK_EMA | filtered | 45 | 61.82 | 65.00 | 3.18 | 20.58 | 18.76 | 17.70 | 4.24 | 15.77 |
| TREND_PULLBACK_EMA | kept | 99 | 78.77 | 65.00 | -13.77 | 20.48 | 19.84 | 18.04 | 4.63 | 0.62 |
| VOLUME_SURGE_BREAKOUT | filtered | 16 | 38.51 | 62.75 | 24.24 | 19.89 | 18.54 | 20.00 | 3.22 | 15.61 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 65.80 | 65.00 | -0.80 | 21.00 | 18.20 | 20.00 | 4.50 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 222 | 52.68 | 22.33 | 13.72 | 5.34 | 12.28 | 4.87 | 8.66 | 1.41 |
| DIVERGENCE_CONTINUATION | kept | 231 | 68.47 | 23.23 | 15.99 | 4.09 | 12.48 | 5.66 | 9.00 | 1.40 |
| FAILED_AUCTION_RECLAIM | filtered | 116 | 50.90 | 22.38 | 14.76 | 7.19 | 12.34 | 6.80 | 4.20 | 3.28 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 67.70 | 25.00 | 14.00 | 3.00 | 8.00 | 5.00 | 6.70 | 6.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 21 | 50.54 | 23.10 | 14.19 | 5.14 | 10.76 | 6.67 | 6.96 | 2.86 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 80.30 | 25.00 | 20.00 | 6.00 | 9.00 | 5.00 | 8.30 | 7.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 180 | 50.71 | 23.29 | 14.87 | 5.63 | 13.27 | 6.22 | 5.42 | 1.14 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 34 | 69.19 | 22.29 | 15.53 | 3.97 | 12.62 | 6.24 | 7.30 | 2.62 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 58.10 | 17.00 | 14.00 | 9.00 | 14.00 | 8.50 | 10.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 72.70 | 19.00 | 14.00 | 9.75 | 14.00 | 7.62 | 8.32 | 0.00 |
| MEAN_REVERT | filtered | 15 | 54.77 | 19.67 | 18.00 | 9.00 | 10.00 | 5.00 | 8.22 | 0.00 |
| MEAN_REVERT | kept | 14 | 68.00 | 17.57 | 18.00 | 7.07 | 12.86 | 5.00 | 7.50 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 157 | 60.58 | 16.49 | 18.04 | 11.79 | 13.58 | 6.70 | 8.35 | 4.68 |
| MOVER_AVWAP_SCALP | kept | 740 | 81.71 | 19.61 | 18.04 | 13.47 | 13.58 | 7.45 | 9.41 | 4.53 |
| MOVER_TREND_PULLBACK | filtered | 3209 | 56.15 | 18.37 | 18.01 | 7.64 | 12.10 | 6.32 | 9.42 | 3.83 |
| MOVER_TREND_PULLBACK | kept | 5848 | 76.54 | 19.58 | 18.01 | 7.78 | 12.52 | 6.63 | 9.34 | 4.08 |
| POST_DISPLACEMENT_CONTINUATION | kept | 16 | 90.03 | 22.50 | 18.00 | 15.00 | 14.00 | 5.00 | 10.00 | 5.53 |
| QUIET_COMPRESSION_BREAK | filtered | 36 | 48.05 | 19.92 | 17.56 | 11.25 | 13.72 | 7.49 | 4.91 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 35 | 76.07 | 20.00 | 16.86 | 11.49 | 14.00 | 6.90 | 8.71 | 0.00 |
| SR_FLIP_RETEST | filtered | 157 | 55.21 | 19.96 | 16.92 | 3.57 | 13.08 | 5.46 | 9.29 | 1.62 |
| SR_FLIP_RETEST | kept | 54 | 71.68 | 20.41 | 18.00 | 7.50 | 12.46 | 5.00 | 9.53 | 1.66 |
| TREND_PULLBACK_EMA | filtered | 45 | 61.82 | 16.51 | 18.00 | 9.83 | 14.27 | 6.38 | 8.36 | 4.24 |
| TREND_PULLBACK_EMA | kept | 99 | 78.77 | 19.84 | 18.00 | 7.52 | 14.33 | 5.94 | 9.44 | 4.63 |
| VOLUME_SURGE_BREAKOUT | filtered | 16 | 38.51 | 17.00 | 15.75 | 12.00 | 12.69 | 5.00 | 3.42 | 3.22 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 65.80 | 25.00 | 14.00 | 15.00 | 14.00 | 5.00 | 3.30 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 222 | 52.68 | 0.00 | 0.00 | 0.34 | 0.00 | 1.34 | 0.12 | 0.00 | 0.00 | **1.80** |
| DIVERGENCE_CONTINUATION | kept | 231 | 68.47 | 0.00 | 0.00 | 0.10 | 0.00 | 0.06 | 0.00 | 0.00 | 0.00 | **0.16** |
| FAILED_AUCTION_RECLAIM | filtered | 116 | 50.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.93 | 0.10 | 0.00 | 0.00 | **1.03** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 67.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 21 | 50.54 | 0.00 | 0.00 | 1.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.75** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 80.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 180 | 50.71 | 0.00 | 0.00 | 1.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.40** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 34 | 69.19 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 58.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 4 | 72.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 15 | 54.77 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MEAN_REVERT | kept | 14 | 68.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 157 | 60.58 | 0.48 | 0.00 | 0.34 | 0.00 | 3.64 | 2.17 | 0.00 | 0.84 | **7.47** |
| MOVER_AVWAP_SCALP | kept | 740 | 81.71 | 0.03 | 0.00 | 0.34 | 0.00 | 1.11 | 0.74 | 0.00 | 0.04 | **2.26** |
| MOVER_TREND_PULLBACK | filtered | 3209 | 56.15 | 0.00 | 0.00 | 0.81 | 0.00 | 0.58 | 0.31 | 0.00 | 0.00 | **1.70** |
| MOVER_TREND_PULLBACK | kept | 5848 | 76.54 | 0.00 | 0.00 | 0.35 | 0.00 | 0.23 | 0.13 | 0.00 | 0.00 | **0.71** |
| POST_DISPLACEMENT_CONTINUATION | kept | 16 | 90.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 36 | 48.05 | 0.00 | 0.00 | 4.40 | 0.00 | 1.07 | 0.50 | 0.00 | 5.70 | **11.67** |
| QUIET_COMPRESSION_BREAK | kept | 35 | 76.07 | 0.00 | 0.00 | 0.41 | 0.00 | 0.25 | 0.86 | 0.00 | 0.00 | **1.52** |
| SR_FLIP_RETEST | filtered | 157 | 55.21 | 0.00 | 0.00 | 3.75 | 0.00 | 0.00 | 0.13 | 0.00 | 0.00 | **3.88** |
| SR_FLIP_RETEST | kept | 54 | 71.68 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.09** |
| TREND_PULLBACK_EMA | filtered | 45 | 61.82 | 0.00 | 0.00 | 0.53 | 0.00 | 10.19 | 1.51 | 0.00 | 0.00 | **12.23** |
| TREND_PULLBACK_EMA | kept | 99 | 78.77 | 0.00 | 0.00 | 0.08 | 0.00 | 0.12 | 0.10 | 0.00 | 0.00 | **0.30** |
| VOLUME_SURGE_BREAKOUT | filtered | 16 | 38.51 | 0.00 | 0.00 | 4.50 | 0.00 | 0.00 | 0.00 | 0.00 | 1.58 | **6.08** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 65.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **145067 held of 509264 seen** across 21 strategies; 3299 cells past the sample floor; **1671 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 44192 | 668/43524/0 | 45% | -0.15 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING/ALTCOIN (-1.22R) |
| MOVER_AVWAP_SCALP | 18566 | 189/18377/0 | 42% | -0.23 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 11212 | 120/11092/0 | 36% | -0.32 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 10119 | 86/10033/0 | 49% | -0.05 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.35R) | ASIA/MARKDOWN/CASCADE/BTC_FALLING/ALTCOIN (-1.19R) |
| TREND_PULLBACK_EMA | 8474 | 38/8436/0 | 41% | -0.20 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OVERLAP/QUIET/COMPRESSED/BTC_FALLING (-1.29R) |
| LIQUIDITY_SWEEP_REVERSAL | 7408 | 81/7327/0 | 34% | -0.51 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| SHADOW_MEAN_REVERT | 7032 | 0/0/7032 | 43% | -0.11 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.45R) | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.99R) |
| SHADOW_RANGE_FADE | 6468 | 0/0/6468 | 37% | -0.10 | NY/MARKDOWN/EXPANDED/BTC_FALLING (+0.80R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-1.38R) |
| QUIET_COMPRESSION_BREAK | 5951 | 382/5569/0 | 51% | -0.10 | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (+0.57R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5571 | 0/0/5571 | 34% | -0.41 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.00R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 3709 | 47/3662/0 | 43% | -0.21 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| SR_FLIP_RETEST | 3311 | 15/3296/0 | 47% | -0.26 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+0.87R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| VOLUME_SURGE_BREAKOUT | 2870 | 0/2870/0 | 35% | -0.28 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2847 | 2/2845/0 | 30% | -0.49 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| SHADOW_CASCADE_REVERSAL | 1268 | 0/0/1268 | 53% | -0.05 | LONDON/MARKUP/CASCADE/BTC_NEUTRAL (+0.10R) | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.38R) |
| RANGE_FADE | 1263 | 4/1259/0 | 42% | -0.28 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 324 | 0/324/0 | 35% | -0.49 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 110 | 22/88/0 | 42% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 12 | 0/12/0 | 50% | -0.00 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR` -1.55R (n=16, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR` -1.53R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 209 | 27% / -0.59R | 209 | 52% / -0.15R | +0.43 | **ATR** |
| LIQUIDATION_REVERSAL | 18 | 33% / -0.45R | 18 | 61% / -0.15R | +0.30 | **ATR** |
| TREND_PULLBACK_EMA | 707 | 40% / -0.29R | 707 | 54% / -0.05R | +0.23 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1212 | 43% / -0.34R | 1212 | 55% / -0.14R | +0.20 | **ATR** |
| MA_CROSS_TREND_SHIFT | 35 | 37% / -0.28R | 35 | 40% / -0.12R | +0.16 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 138 | 34% / -0.25R | 138 | 44% / -0.10R | +0.15 | **ATR** |
| MOVER_AVWAP_SCALP | 1693 | 44% / -0.18R | 1693 | 49% / -0.06R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1078 | 40% / -0.25R | 1078 | 42% / -0.14R | +0.11 | **ATR** |
| RANGE_FADE | 60 | 33% / -0.38R | 60 | 40% / -0.27R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 277 | 45% / -0.28R | 277 | 48% / -0.17R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 7332 | 50% / -0.09R | 7332 | 55% / -0.00R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1062 | 49% / -0.10R | 1062 | 54% / -0.04R | +0.06 | **ATR** |
| QUIET_COMPRESSION_BREAK | 990 | 46% / -0.16R | 990 | 46% / -0.16R | -0.00 | **FIXED** |
| MEAN_REVERT | 261 | 52% / -0.06R | 261 | 51% / -0.06R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 43% / -0.33R | 7 | 43% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 10204 | 28% | -0.23R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1693 | 47% | -0.06R | 215 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 87 | 47% | -0.10R | 53 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 950 | 35% / -0.21R | +0.86 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1276 | 40% / -0.20R | +0.81 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2159 | 34% / -0.14R | +0.70 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 9205 | 37% / -0.12R | +0.41 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1210 | 37% / -0.08R | +0.20 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 968 | 34% / -0.18R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 880 | 33% / -0.23R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 207 | 29% / -0.46R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 275 | 32% / -0.53R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 217 | 52% / +0.05R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 46 | 37% / -0.03R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 270 | 34% / -0.36R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 53 | 26% / -0.44R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 24 | 46% / -0.05R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 13 | 38% / +0.45R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **5** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×158]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 15/6) (sustained 15 cycles)
- **ALERT** `dark_resolution` — 13 of 208 open dark rows are not being advanced (worst: CFGUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 168/120) (sustained 168 cycles)
- **ALERT** `edge_reconciliation` — TREND_PULLBACK_EMA realized−counterfactual=+0.56R (bound 0.3) (streak 653/6) (sustained 653 cycles)
- **ALERT** `tuned_variants` — 527 non-stamps — atr_arm_uncomputable=527 (seen=18987 stamped=2272 skipped=16188) (streak 653/6) (sustained 653 cycles)
- **ALERT** `auto_dispatch` — 114 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=115) (streak 643/3) (sustained 643 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 45 fed / 0 quiet / 0 never delivered of 45 subscribed; 131467788 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 22 arms current, none stalled; covering 1555/1555 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 1/6) | 1 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 47 current): CRVUSDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 6/12) | 6 |
| auto_dispatch | violating | 114 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=115) (streak 643/3) | 643 |
| binance_ip_weight | ok | peak 387/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 81560.30 | 0 |
| candle_coverage | ok | 145/145 symbols with ≥20 15m candles, 123/145 updated within 45m [stale=22, fresh=123; 74 Tier-1 futures + 71 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 4635 dup bars, 0 undedupable; ws 0 out-of-order, 694 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 55 cohorts, 24 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +65 / upstream +15 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 2436/2454 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 13 of 208 open dark rows are not being advanced (worst: CFGUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 168/120) | 168 |
| dark_sar_arms | ok | no open arms; covering 2433/2451 signals (99%) | 0 |
| depth_feed | ok | 45/45 books fresh (stale 0, never 0, thin 0); 48669679 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | TREND_PULLBACK_EMA realized−counterfactual=+0.56R (bound 0.3) (streak 653/6) | 653 |
| emission_controller | ok | last cycle 1152s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×158]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 15/6) | 15 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 2/6) | 2 |
| firestore_read_budget | ok | 1,366 reads/day of 50,000 [engine 1,327, signing 39]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 5400 sealed bars over 45 symbols; 2152 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +7 / upstream +126 | 0 |
| indicator_cache_key | ok | 283750 frozen value(s) avoided; 979126 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.21R over n=3662 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +4 / upstream +126 | 0 |
| mover_admission_metadata | ok | 927 symbols known, 221 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 71 held, 66 with scan counts, 71 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 3 locked / 3 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 2740104 evicted (sampled: execution:trigger_not_confirmed 400/984921, execution:overextended 400/872515, setup_compat:regime_STRONG_TREND 400/448027) | 0 |
| price_action_lane | ok | 1636891 evaluated, 1871 emitted; layer1 1871 stamped / 0 blind; cooldown=217868, delta_opposed=136129, no_footprint=691467, no_opposing_target=2660, no_sweep=453773, rr_below_floor=133123 | 0 |
| promoted_pair_integrity | ok | 71/71 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.28R over n=1259 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +9 / upstream +126 | 0 |
| sar_alignment_crosscheck | ok | 1429/40989 disagreed (3.5%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +126 | 0 |
| sar_hold_arm | ok | 1848 held arms settled, 153 unscored, 45 still walking (39 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 3/86 unfetchable (3%); top cause: located bar does not contain the stamp; symbols: AEROUSDT, CTUSDT, ZROUSDT | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 45 current): CRVUSDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 6/12) | 6 |
| sar_refresh_budget | ok | 9 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 12 resolved, 71 still mid-window | 0 |
| scan_cycle | ok | last 51.35s, worst 182.08s over 17896 lifetime cycles; lifetime 293 over 60s, 18 over 120s; recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 4.72s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 746948 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 19s ago (71.78s to run, worst 124.75s), 1392 overrun(s) of 13909 cycles, TTL 900s; slowest user_positions=13.1s, position_marks=7.88s, data_intake=7.12s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=923, gate reads=0, withheld=923) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +112 / upstream +126 | 0 |
| structural_snap | ok | 6000/6000 measured, 23 blind, 0 levels moved (refusals: redetect_cooldown=1411) | 0 |
| structural_veto_lane | ok | 3132 stamped; 0 with no readable level book, 95 with clear air ahead, 2280 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +126 / upstream +15 | 0 |
| tuned_variants | violating | 527 non-stamps — atr_arm_uncomputable=527 (seen=18987 stamped=2272 skipped=16188) (streak 653/6) | 653 |
| unlock_shorts | ok | 14 open, 42 scheduled, calendar 17.6h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 77 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2456439`
- `Path funnel` emissions: `53`
- `Regime distribution` emissions: `53`
- `QUIET_SCALP_BLOCK` events: `266`
- `confidence_gate` events: `11253`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **148**
- Total REST-fallback activations: **14**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 21 | 2986 | 11076 | 27275 | 0 |
| futures_aggtrade | 38 | 4995 | 12740 | 14901 | 0 |
| futures_depth | 54 | 3566 | 17852 | 49579 | 0 |
| futures_liq | 4 | 4477 | 7688 | 20951 | 0 |
| futures_mover | 31 | 3723 | 15617 | 27350 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 14 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=378262] state[populated=378262] buckets[many=378262] sources[none] quality[none]
- funding_rate: presence[absent=61212, present=317050] state[empty=61212, populated=317050] buckets[few=317050, none=61212] sources[none] quality[none]
- liquidation_clusters: presence[absent=207151, present=171111] state[empty=207151, populated=171111] buckets[few=142908, none=207151, some=28203] sources[none] quality[none]
- oi_snapshot: presence[absent=61211, present=317051] state[empty=61211, populated=317051] buckets[few=340, many=315325, none=61211, some=1386] sources[none] quality[none]
- order_book: presence[absent=122478, present=255784] state[populated=255784, unavailable=122478] buckets[few=255784, none=122478] sources[book_ticker=255784, unavailable=122478] quality[none=122478, top_of_book_only=255784]
- orderblocks: presence[absent=378262] state[empty=378262] buckets[none=378262] sources[measured_dark=378262] quality[none]
- recent_ticks: presence[present=378262] state[populated=378262] buckets[many=378262] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.9673051834106445` sec
- Median create→first breach: `4312.811565876007` sec
- Median create→terminal: `4312.811598777771` sec
- Median first breach→terminal: `8.58306884765625e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 8 | 8 | 0.9155919862468186 | 1.1328001422634935 | 0.8338691805992626 | 0 | 6 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 3.016020476329677 | 3.0 | 1.0053401587765591 | 0 | 0 |
| MA_CROSS_TREND_SHIFT | 2 | 2 | 6.784244234241732 | 2.1306168739967895 | 3.0521975277495637 | 2 | 0 |
| MEAN_REVERT | 2 | 2 | 2.5828509084729734 | 2.9080827369184687 | 0.8919238631415454 | 1 | 1 |
| MOVER_AVWAP_SCALP | 3 | 3 | 2.5447068571093427 | 2.7509905358037097 | 0.8530982792280442 | 1 | 2 |
| MOVER_TREND_PULLBACK | 24 | 24 | 3.845770378802941 | 3.0 | 1.2908191724699447 | 19 | 5 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 0.9850499170169731 | 1.0618024477299528 | 0.8894635848317265 | 0 | 7 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 8 | 8 | 25.0 | 25.0 | 25.0 | 0.0 | 0.1907 | 7821.026287436485 | 7821.026372909546 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -3.016 | 1777.546720981598 | 1777.546775817871 |
| MA_CROSS_TREND_SHIFT | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -0.6516 | 4279.059717535973 | 4279.059772014618 |
| MEAN_REVERT | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 1.6634 | 3627.4131195545197 | 3627.6520705223083 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.0 | -0.5082 | 4312.811565876007 | 4312.811598777771 |
| MOVER_TREND_PULLBACK | 24 | 24 | 25.0 | 37.5 | 25.0 | 0.0 | -0.2865 | 2694.23446393013 | 2694.375126838684 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 55.6 | 33.3 | 55.6 | 0.0 | 1.216 | 24658.445281028748 | 24658.445366859436 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1216 | 7 | 801 | 0.0 | 0.0 | None | None | 415 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3608 | 26 | 3225 | 0.0 | 0.0 | None | None | 383 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `256`
- Gating Δ: `4332`
- No-generation Δ: `-362956`
- Fast failures Δ: `0`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.1907, "current_avg_pnl": 0.1907, "current_win_rate": 25.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 25.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.5622, "current_avg_pnl": -0.5082, "current_win_rate": 0.0, "previous_avg_pnl": 1.054, "previous_win_rate": 50.0, "win_rate_delta": -50.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.3568, "current_avg_pnl": -0.2865, "current_win_rate": 25.0, "previous_avg_pnl": 1.0703, "previous_win_rate": 38.9, "win_rate_delta": -13.9}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 1.871, "current_avg_pnl": 1.216, "current_win_rate": 55.6, "previous_avg_pnl": -0.655, "previous_win_rate": 0.0, "win_rate_delta": 55.6}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": 26, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -9, "geometry_changed_delta": 0, "geometry_preserved_delta": -368, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **QUIET_COMPRESSION_BREAK**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
