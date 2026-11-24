# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, TREND_PULLBACK_EMA
- Top promising signals/paths: MOVER_AVWAP_SCALP
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `1167` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 73 | 73 | 72 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 4985 | 4985 | 3764 | 11 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 63450 | 63461 | 28 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 60073 | 60073 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 59816 | 58623 | 1430 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 60118 | 59553 | 609 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 59742 | 59655 | 124 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 50076 | 50095 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 60167 | 60202 | 4 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 60212 | 58763 | 2081 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 66980 | 73792 | 715 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 63499 | 59364 | 7560 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 59415 | 59415 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 60083 | 60092 | 22 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 59787 | 59745 | 68 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 60854 | 59761 | 1605 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 59417 | 59656 | 78 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 49658 | 47830 | 2170 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 50005 | 49874 | 197 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 63401 | 63432 | 13 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 50103 | 50117 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2106 | 2106 | 1576 | 13 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 396 | 396 | 50 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 26 | 26 | 20 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 13580 | 13580 | 13211 | 21 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 10 | 10 | 8 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 5458 | 5458 | 5061 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1590 | 1590 | 540 | 71 | active-healthy (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 19936 | 19936 | 12071 | 198 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 43 | 43 | 19 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 399 | 399 | 328 | 11 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4198 | 4198 | 3767 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 426 | 426 | 378 | 3 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 932 | 932 | 754 | 23 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 46 | 46 | 5 | 5 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=63461): breakout_not_found=29666, basic_filters_failed=19036, move_not_fresh=11140, breakout_stale=2813, retest_proximity_failed=660, volume_spike_missing=143, move_exhausted=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=60073): cls_disabled_merged_into_lsr=60073
- **EVAL::DIVERGENCE_CONTINUATION** (total=58623): cvd_divergence_failed=20074, h1_trend_not_aligned=17157, basic_filters_failed=16268, ema_alignment_reject=4079, retest_proximity_failed=925, missing_fvg_or_orderblock=120
- **EVAL::FAILED_AUCTION_RECLAIM** (total=59553): auction_not_detected=37856, basic_filters_failed=15906, reclaim_hold_failed=2341, tail_too_small=1731, regime_blocked=1682, rsi_reject=37
- **EVAL::FUNDING_EXTREME** (total=59655): funding_not_extreme=39869, basic_filters_failed=16058, ema_alignment_reject=1897, missing_funding_rate=888, rsi_reject=654, cvd_divergence_failed=139, momentum_reject=111, missing_fvg_or_orderblock=39
- **EVAL::LIQUIDATION_REVERSAL** (total=50095): cascade_threshold_not_met=33660, basic_filters_failed=16026, cvd_divergence_failed=226, rsi_reject=171, missing_fvg_or_orderblock=7, volume_spike_missing=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=60202): no_ma_cross=43294, basic_filters_failed=16291, ma_cross_htf_misaligned=397, ma_cross_cooldown=220
- **EVAL::MEAN_REVERT** (total=58763): no_extension=47696, basic_filters_failed=11067
- **EVAL::MOVER_AVWAP_SCALP** (total=73792): no_avwap_tag=31078, basic_filters_failed=19235, no_mover_leg=15601, avwap_slope_against=4791, avwap_reclaim_no_volume=1554, no_avwap_reclaim=1469, anchor_too_recent=64
- **EVAL::MOVER_TREND_PULLBACK** (total=59364): mover_run_too_small=26191, basic_filters_failed=19144, no_reclaim=12221, no_pullback_tag=1808
- **EVAL::OPENING_RANGE_BREAKOUT** (total=59415): feature_disabled=59415
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=60092): regime_blocked=26515, breakout_not_found=22940, basic_filters_failed=7034, adx_reject=3492, ema_alignment_reject=99, rsi_reject=12
- **EVAL::QUIET_COMPRESSION_BREAK** (total=59745): regime_blocked=35097, compression_not_detected=14028, basic_filters_failed=8861, breakout_not_detected=1622, volume_confirmation_failed=115, rsi_reject=16, missing_fvg_or_orderblock=6
- **EVAL::RANGE_FADE** (total=59761): no_range_edge=48691, basic_filters_failed=11070
- **EVAL::SR_FLIP_RETEST** (total=59656): flip_close_not_confirmed=37089, basic_filters_failed=15871, long_break_volume_thin=1795, regime_blocked=1658, h1_break_not_confirmed=1463, retest_out_of_zone=1283, reclaim_hold_failed=373, whipsaw_flip=47, long_acceptance_not_held=47, ema_alignment_reject=14, wick_quality_failed=13, missing_fvg_or_orderblock=3
- **EVAL::STANDARD** (total=47830): momentum_reject=16746, adx_reject=9822, basic_filters_failed=9195, ema_alignment_reject=4643, sweeps_not_detected=4465, macd_reject=2424, htf_poi_unanchored=304, mtf_reject=99, rsi_reject=75, invalid_sl_geometry=57
- **EVAL::TREND_PULLBACK** (total=49874): h1_trend_not_aligned=17919, basic_filters_failed=8719, h1_pullback_not_confirmed=7604, ema_alignment_reject=7565, ema_not_tested_prev=3314, no_ema_reclaim_close=2433, body_conviction_fail=910, rsi_reject=819, prev_already_above_emas=235, no_prev_high_break=167, prev_already_below_emas=55, no_prev_low_break=43, momentum_flat=35, momentum_reject=23, ema21_not_tagged=22, missing_fvg_or_orderblock=11
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=63432): breakout_not_found=35995, basic_filters_failed=19029, move_not_fresh=5325, breakout_stale=1968, retest_proximity_failed=916, volume_spike_missing=180, move_exhausted=12, missing_fvg_or_orderblock=7
- **EVAL::WHALE_MOMENTUM** (total=50117): momentum_reject=39003, recent_ticks_insufficient=8149, basic_filters_failed=2965

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=9): execution:overextended=9
- **DIVERGENCE_CONTINUATION** (total=149): setup_compat:regime_VOLATILE_UNSUITABLE=131, execution:overextended=18
- **FAILED_AUCTION_RECLAIM** (total=1041): setup_compat:regime_STRONG_TREND=670, execution:overextended=202, context_floor=152, setup_compat:regime_VOLATILE_UNSUITABLE=17
- **FUNDING_EXTREME_SIGNAL** (total=354): execution:trigger_not_confirmed=354
- **LIQUIDATION_REVERSAL** (total=30): execution:trigger_not_confirmed=26, context_floor=4
- **LIQUIDITY_SWEEP_REVERSAL** (total=3811): setup_compat:regime_STRONG_TREND=2094, execution:trigger_not_confirmed=949, execution:overextended=768
- **MA_CROSS_TREND_SHIFT** (total=7): execution:trigger_not_confirmed=3, setup_compat:regime_DIRTY_RANGE=2, execution:overextended=1, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=4914): setup_compat:regime_STRONG_TREND=2385, setup_compat:regime_WEAK_TREND=1314, execution:overextended=1215
- **MOVER_AVWAP_SCALP** (total=1046): execution:overextended=770, entry_quality=156, execution:trigger_not_confirmed=120
- **MOVER_TREND_PULLBACK** (total=8710): execution:trigger_not_confirmed=4727, execution:overextended=3142, entry_quality=841
- **POST_DISPLACEMENT_CONTINUATION** (total=7): execution:overextended=7
- **RANGE_FADE** (total=3469): setup_compat:regime_WEAK_TREND=1368, setup_compat:regime_STRONG_TREND=1335, execution:overextended=429, setup_compat:regime_VOLATILE_UNSUITABLE=298, setup_compat:regime_BREAKOUT_EXPANSION=25, context_edge=14
- **TREND_PULLBACK_EMA** (total=628): setup_compat:regime_CLEAN_RANGE=373, setup_compat:regime_DIRTY_RANGE=200, entry_quality=41, setup_compat:regime_VOLATILE_UNSUITABLE=14
- **VOLUME_SURGE_BREAKOUT** (total=5): execution:overextended=5

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_DOWN | 120330 | 32.6% |
| RANGING | 118952 | 32.2% |
| TRENDING_UP | 72264 | 19.6% |
| QUIET | 44331 | 12.0% |
| VOLATILE | 13333 | 3.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **48**
- Average confidence gap to threshold: **6.14** (samples=48) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: TRXUSDT=18, WLFIUSDT=12, SUIUSDT=4, LINKUSDT=4, AKEUSDT=4, BTCUSDT=3, AVAXUSDT=2, PUMPUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 2 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 403 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 1 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 35 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 26 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 4 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 113 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 8 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 5 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 45 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 4 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 62 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 9 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 182 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 4 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 387 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1470 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 16 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1654 |
| POST_DISPLACEMENT_CONTINUATION | filtered | min_confidence | 2 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 22 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 19 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 6 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 46 |
| SR_FLIP_RETEST | filtered | min_confidence | 9 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 19 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 6 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 60 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 7 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 29 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 67.15 | 65.00 | -2.15 | 19.05 | 16.50 | 20.00 | 3.75 | 8.95 |
| DIVERGENCE_CONTINUATION | filtered | 404 | 54.74 | 64.89 | 10.15 | 20.32 | 19.65 | 18.71 | 1.99 | 15.16 |
| DIVERGENCE_CONTINUATION | kept | 35 | 66.94 | 65.00 | -1.94 | 19.42 | 19.81 | 17.15 | 4.06 | 6.19 |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 61.74 | 65.00 | 3.26 | 19.39 | 19.18 | 20.00 | 3.08 | 5.69 |
| FAILED_AUCTION_RECLAIM | kept | 113 | 71.49 | 65.00 | -6.49 | 20.41 | 18.94 | 20.00 | 4.56 | 2.13 |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 48.15 | 65.00 | 16.85 | 20.06 | 13.96 | 16.75 | 3.75 | 6.80 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 76.60 | 65.00 | -11.60 | 18.48 | 13.14 | 17.00 | 4.60 | 1.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 49 | 52.95 | 63.06 | 10.11 | 21.11 | 19.74 | 18.53 | 2.51 | 15.93 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 62 | 70.65 | 65.00 | -5.65 | 21.22 | 18.40 | 18.58 | 2.65 | 0.31 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 59.30 | 61.00 | 1.70 | 20.90 | 14.00 | 15.80 | 0.00 | 6.40 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 65.00 | 65.00 | 0.00 | 19.90 | 20.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | kept | 9 | 65.90 | 65.00 | -0.90 | 19.19 | 14.00 | 16.20 | 0.00 | 4.80 |
| MOVER_AVWAP_SCALP | filtered | 186 | 55.96 | 63.68 | 7.72 | 19.99 | 15.47 | 15.80 | 3.73 | 20.94 |
| MOVER_AVWAP_SCALP | kept | 387 | 79.48 | 65.00 | -14.48 | 20.05 | 15.65 | 15.80 | 4.32 | 4.53 |
| MOVER_TREND_PULLBACK | filtered | 1486 | 55.21 | 64.41 | 9.20 | 19.62 | 18.26 | 15.80 | 3.67 | 13.90 |
| MOVER_TREND_PULLBACK | kept | 1654 | 76.27 | 65.00 | -11.27 | 19.78 | 18.12 | 15.80 | 4.50 | 1.52 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 2 | 57.70 | 61.00 | 3.30 | 20.80 | 20.00 | 20.00 | 4.50 | 10.80 |
| POST_DISPLACEMENT_CONTINUATION | kept | 22 | 73.84 | 65.00 | -8.84 | 20.54 | 20.00 | 19.50 | 4.64 | 8.62 |
| QUIET_COMPRESSION_BREAK | filtered | 25 | 57.06 | 65.00 | 7.94 | 21.28 | 19.25 | 20.00 | 0.00 | 8.69 |
| QUIET_COMPRESSION_BREAK | kept | 46 | 76.64 | 65.00 | -11.64 | 22.45 | 19.98 | 20.00 | 0.00 | 0.25 |
| SR_FLIP_RETEST | filtered | 9 | 56.62 | 60.67 | 4.05 | 21.34 | 20.00 | 16.72 | 1.72 | 8.88 |
| SR_FLIP_RETEST | kept | 19 | 71.76 | 65.00 | -6.76 | 22.83 | 20.00 | 18.48 | 2.71 | 3.26 |
| TREND_PULLBACK_EMA | filtered | 6 | 56.50 | 62.50 | 6.00 | 20.42 | 19.50 | 18.10 | 3.75 | 15.00 |
| TREND_PULLBACK_EMA | kept | 60 | 78.76 | 65.00 | -13.76 | 20.86 | 19.86 | 18.38 | 4.90 | 2.42 |
| VOLUME_SURGE_BREAKOUT | filtered | 7 | 47.80 | 65.00 | 17.20 | 20.00 | 17.40 | 20.00 | 3.00 | 18.90 |
| VOLUME_SURGE_BREAKOUT | kept | 29 | 77.29 | 65.00 | -12.29 | 20.05 | 18.83 | 20.00 | 4.60 | 2.54 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 67.15 | 17.00 | 16.00 | 13.50 | 14.00 | 5.00 | 6.85 | 3.75 |
| DIVERGENCE_CONTINUATION | filtered | 404 | 54.74 | 21.67 | 17.83 | 3.38 | 11.77 | 5.33 | 7.91 | 1.99 |
| DIVERGENCE_CONTINUATION | kept | 35 | 66.94 | 21.34 | 16.00 | 5.57 | 13.49 | 4.66 | 8.10 | 4.06 |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 61.74 | 21.00 | 15.33 | 4.60 | 12.53 | 4.58 | 6.30 | 3.08 |
| FAILED_AUCTION_RECLAIM | kept | 113 | 71.49 | 23.99 | 15.88 | 4.12 | 12.26 | 6.85 | 5.97 | 4.56 |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 48.15 | 25.00 | 8.00 | 8.25 | 13.12 | 8.50 | 3.32 | 3.75 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 76.60 | 23.40 | 18.00 | 9.60 | 12.00 | 8.50 | 1.50 | 4.60 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 49 | 52.95 | 24.88 | 14.49 | 3.43 | 12.08 | 4.66 | 6.84 | 2.51 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 62 | 70.65 | 22.84 | 15.16 | 5.66 | 12.50 | 4.94 | 7.27 | 2.65 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 59.30 | 25.00 | 14.00 | 3.00 | 11.00 | 5.00 | 7.70 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 65.00 | 15.00 | 14.00 | 3.00 | 14.00 | 9.00 | 10.00 | 0.00 |
| MEAN_REVERT | kept | 9 | 65.90 | 25.00 | 14.00 | 6.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 186 | 55.96 | 18.10 | 18.04 | 12.06 | 13.02 | 6.50 | 6.89 | 3.73 |
| MOVER_AVWAP_SCALP | kept | 387 | 79.48 | 19.76 | 18.26 | 13.13 | 13.64 | 6.45 | 8.56 | 4.32 |
| MOVER_TREND_PULLBACK | filtered | 1486 | 55.21 | 18.52 | 18.03 | 7.82 | 12.25 | 5.97 | 7.52 | 3.67 |
| MOVER_TREND_PULLBACK | kept | 1654 | 76.27 | 19.11 | 18.16 | 8.21 | 12.73 | 6.32 | 9.13 | 4.50 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 2 | 57.70 | 2.00 | 18.00 | 15.00 | 14.00 | 5.00 | 10.00 | 4.50 |
| POST_DISPLACEMENT_CONTINUATION | kept | 22 | 73.84 | 17.73 | 18.00 | 15.00 | 14.00 | 5.00 | 8.09 | 4.64 |
| QUIET_COMPRESSION_BREAK | filtered | 25 | 57.06 | 17.00 | 17.04 | 11.40 | 14.00 | 6.76 | 3.16 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 46 | 76.64 | 19.43 | 17.91 | 13.04 | 14.07 | 8.01 | 5.56 | 0.00 |
| SR_FLIP_RETEST | filtered | 9 | 56.62 | 17.89 | 18.00 | 3.33 | 13.22 | 5.00 | 6.33 | 1.72 |
| SR_FLIP_RETEST | kept | 19 | 71.76 | 25.00 | 18.00 | 5.21 | 10.42 | 5.00 | 8.68 | 2.71 |
| TREND_PULLBACK_EMA | filtered | 6 | 56.50 | 9.50 | 18.00 | 7.50 | 14.00 | 8.75 | 10.00 | 3.75 |
| TREND_PULLBACK_EMA | kept | 60 | 78.76 | 20.52 | 18.00 | 7.62 | 14.28 | 7.09 | 9.22 | 4.90 |
| VOLUME_SURGE_BREAKOUT | filtered | 7 | 47.80 | 17.00 | 14.00 | 12.00 | 11.00 | 5.00 | 4.70 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 29 | 77.29 | 18.38 | 16.76 | 13.14 | 13.48 | 5.00 | 8.48 | 4.60 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 67.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 404 | 54.74 | 0.00 | 0.00 | 2.08 | 0.00 | 0.05 | 0.04 | 0.00 | 0.00 | **2.17** |
| DIVERGENCE_CONTINUATION | kept | 35 | 66.94 | 0.00 | 0.00 | 0.69 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.69** |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 61.74 | 0.00 | 0.00 | 2.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.56** |
| FAILED_AUCTION_RECLAIM | kept | 113 | 71.49 | 0.00 | 0.00 | 1.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.90** |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 48.15 | 0.00 | 0.00 | 1.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.80** |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 76.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 49 | 52.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 62 | 70.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 59.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 65.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 9 | 65.90 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| MOVER_AVWAP_SCALP | filtered | 186 | 55.96 | 2.42 | 0.00 | 1.34 | 0.00 | 8.15 | 0.00 | 0.00 | 0.69 | **12.60** |
| MOVER_AVWAP_SCALP | kept | 387 | 79.48 | 0.00 | 0.00 | 0.41 | 0.00 | 2.22 | 0.35 | 0.00 | 0.35 | **3.33** |
| MOVER_TREND_PULLBACK | filtered | 1486 | 55.21 | 0.00 | 0.00 | 1.04 | 0.00 | 0.58 | 0.12 | 0.00 | 0.13 | **1.87** |
| MOVER_TREND_PULLBACK | kept | 1654 | 76.27 | 0.00 | 0.00 | 0.77 | 0.00 | 0.12 | 0.05 | 0.00 | 0.01 | **0.95** |
| POST_DISPLACEMENT_CONTINUATION | filtered | 2 | 57.70 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 6.00 | 0.00 | 0.00 | **10.80** |
| POST_DISPLACEMENT_CONTINUATION | kept | 22 | 73.84 | 0.00 | 0.00 | 2.62 | 0.00 | 0.00 | 0.27 | 0.00 | 0.00 | **2.89** |
| QUIET_COMPRESSION_BREAK | filtered | 25 | 57.06 | 0.00 | 0.00 | 1.15 | 0.00 | 0.00 | 0.00 | 0.00 | 1.44 | **2.59** |
| QUIET_COMPRESSION_BREAK | kept | 46 | 76.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 9 | 56.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 19 | 71.76 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 6 | 56.50 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| TREND_PULLBACK_EMA | kept | 60 | 78.76 | 0.00 | 0.00 | 1.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.52** |
| VOLUME_SURGE_BREAKOUT | filtered | 7 | 47.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 29 | 77.29 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.17** |

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
- Outcomes recorded: **202399 held of 997085 seen** across 21 strategies; 4585 cells past the sample floor; **2499 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 49516 | 588/48928/0 | 42% | -0.20 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/QUIET/EXPANDED/BTC_FALLING/MAJOR (-1.26R) |
| MOVER_AVWAP_SCALP | 26764 | 191/26573/0 | 45% | -0.16 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 16336 | 283/16053/0 | 46% | -0.12 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.98R) | NY/MARKUP/CASCADE/BTC_FALLING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 15530 | 184/15346/0 | 37% | -0.30 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+1.69R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 14496 | 84/14412/0 | 38% | -0.31 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 11673 | 132/11541/0 | 39% | -0.40 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.91R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9808 | 514/9294/0 | 44% | -0.11 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8502 | 0/0/8502 | 42% | -0.12 | OVERLAP/MARKUP/CASCADE/BTC_RISING (+1.58R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING (-0.99R) |
| SHADOW_RANGE_FADE | 8037 | 0/0/8037 | 36% | -0.14 | ASIA/MARKDOWN/NORMAL/BTC_FALLING (+0.80R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.36R) |
| SHADOW_FUNDING_FADE | 7700 | 0/0/7700 | 35% | -0.40 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (-0.01R) | OFF_HOURS/RANGE/NORMAL/BTC_RISING (-0.95R) |
| SR_FLIP_RETEST | 7638 | 30/7608/0 | 47% | -0.27 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 6116 | 79/6037/0 | 36% | -0.32 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.60R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4825 | 4/4821/0 | 33% | -0.40 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.06R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.30R) |
| WHALE_MOMENTUM | 4395 | 4/4391/0 | 47% | -0.28 | NY/RANGE/EXPANDED/BTC_FALLING (+0.94R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 4366 | 0/4366/0 | 29% | -0.38 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/NORMAL/BTC_FALLING/ALTCOIN (-1.19R) |
| RANGE_FADE | 3341 | 6/3335/0 | 55% | +0.33 | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (+3.08R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.78R) |
| SHADOW_CASCADE_REVERSAL | 1813 | 0/0/1813 | 52% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 625 | 75/550/0 | 36% | -0.11 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 572 | 0/572/0 | 35% | -0.28 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 258 | 40/218/0 | 45% | -0.16 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 88 | 8/80/0 | 36% | +0.04 | — | — |

- **Strongest cells**: `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.08R (n=37, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.00R (n=32, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.78R (n=47, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 483 | 28% / -0.53R | 483 | 52% / -0.09R | +0.44 | **ATR** |
| TREND_PULLBACK_EMA | 1512 | 39% / -0.36R | 1512 | 50% / -0.08R | +0.28 | **ATR** |
| LIQUIDATION_REVERSAL | 36 | 28% / -0.55R | 36 | 47% / -0.30R | +0.24 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1855 | 44% / -0.34R | 1855 | 58% / -0.10R | +0.24 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 253 | 37% / -0.17R | 253 | 48% / -0.03R | +0.14 | **ATR** |
| MA_CROSS_TREND_SHIFT | 77 | 45% / -0.15R | 77 | 51% / -0.02R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 865 | 47% / -0.25R | 865 | 52% / -0.13R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 9342 | 48% / -0.14R | 9342 | 53% / -0.03R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 473 | 46% / -0.30R | 473 | 48% / -0.20R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 3037 | 47% / -0.12R | 3037 | 53% / -0.02R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1756 | 42% / -0.21R | 1756 | 44% / -0.12R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 2224 | 48% / -0.12R | 2224 | 52% / -0.06R | +0.06 | **ATR** |
| BREAKDOWN_SHORT | 59 | 42% / -0.13R | 59 | 47% / -0.08R | +0.05 | **ATR** |
| RANGE_FADE | 189 | 46% / +0.10R | 189 | 52% / +0.13R | +0.03 | **ATR** |
| MEAN_REVERT | 536 | 45% / -0.18R | 536 | 44% / -0.19R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 16 | 50% / -0.08R | 16 | 50% / -0.08R | -0.00 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1754 | 49% / -0.09R | 1754 | 49% / -0.08R | +0.00 | **ATR** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12425 | 27% | -0.23R | 314 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 3037 | 51% | -0.01R | 246 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 161 | 48% | -0.04R | 75 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1942 | 33% / -0.15R | +0.92 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 2201 | 40% / -0.11R | +0.89 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3621 | 36% / -0.14R | +0.71 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11430 | 36% / -0.17R | +0.36 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2582 | 36% / -0.14R | +0.14 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 172 | 34% / -0.39R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1701 | 37% / -0.09R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1465 | 32% / -0.27R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 372 | 32% / -0.29R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 589 | 32% / -0.26R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 441 | 47% / -0.10R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 102 | 43% / +0.01R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 133 | 46% / +0.05R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 748 | 36% / -0.25R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 127 | 31% / +0.11R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 47 | 43% / -0.28R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 32 | 44% / +0.34R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 64 · alerting: **3** · boot grace active: False
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.42R (bound 0.3) (streak 343/6) (sustained 343 cycles)
- **ALERT** `range_fade_emission` — 2773 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.33R over n=3335, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 125/6) (sustained 125 cycles)
- **ALERT** `tuned_variants` — 273 non-stamps — atr_arm_uncomputable=273 (seen=7204 stamped=759 skipped=6172) (streak 343/6) (sustained 343 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 45 fed / 0 quiet / 0 never delivered of 45 subscribed; 78147003 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 26 arms current, none stalled; covering 2121/2121 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| analyst_plan_cadence | ok | last plan 37m ago | 0 |
| atr_trail_live_arms | ok | 54 arms current, none stalled; covering 1123/1123 signals (100%) | 0 |
| auto_dispatch | ok | 88 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=88. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 258/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 60005.10 | 0 |
| candle_coverage | ok | 85/85 symbols with ≥20 15m candles, 85/85 updated within 45m [fresh=85; 75 Tier-1 futures + 10 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1259 dup bars, 0 undedupable; ws 0 out-of-order, 466 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 64 cohorts, 22 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +4 / upstream +48 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1356/1375 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 3 promoted today, nothing refused | 0 |
| dark_resolution | violating | 4 of 61 open dark rows are not being advanced (worst: SKYAIUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 35/120) | 35 |
| dark_sar_arms | ok | no open arms; covering 1346/1365 signals (99%) | 0 |
| depth_feed | ok | 45/45 books fresh (stale 0, never 0, thin 0); 22233018 msgs, 0 rejected | 0 |
| deriv_recorder | ok | hour recorded, 75 rows | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.42R (bound 0.3) (streak 343/6) | 343 |
| emission_controller | ok | last cycle 1s ago; live_overrides=14 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=699, MOVER_AVWAP_SCALP=645, MOVER_TREND_PULLBACK=3993, RANGE_FADE=558, TREND_PULLBACK_EMA=105), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 4 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won,TREND_PULLBACK_EMA.campaign_prev_age_h,TREND_PULLBACK_EMA.campaign_prev_won) | 0 |
| entry_quality_effective | ok | 7227 evaluated, 2441 suppressed, 3239 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,325 reads/day of 50,000 [engine 1,304, signing 21]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 5400 sealed bars over 45 symbols; 1709 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +2 / upstream +24 | 0 |
| htf_candles | ok | BTCUSDT 1d/1w current | 0 |
| indicator_cache_key | ok | 121064 frozen value(s) avoided; 426259 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.33R over n=6037 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +0 / upstream +24 | 0 |
| mover_admission_metadata | ok | 956 symbols known, 247 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 10 held, 10 with scan counts, 10 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2236 rows held, 3845146 evicted (sampled: execution:trigger_not_confirmed 287/1346781, execution:overextended 286/1175384, setup_compat:regime_STRONG_TREND 286/670231) | 0 |
| price_action_lane | ok | 752416 evaluated, 1030 emitted; layer1 1030 stamped / 0 blind; cooldown=109497, delta_opposed=76012, no_footprint=270595, no_opposing_target=140, no_sweep=224775, rr_below_floor=70367 | 0 |
| promoted_pair_integrity | ok | 10/10 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 2773 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.33R over n=3335, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 125/6) | 125 |
| range_fade_path | ok | output +0 / upstream +24 | 0 |
| sar_alignment_crosscheck | ok | 460/16598 disagreed (2.8%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +24 | 0 |
| sar_hold_arm | ok | 1882 held arms settled, 119 unscored, 49 still walking (40 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 11/42 unfetchable (26%); top cause: gap or duplicate bar in the 15m window; symbols: ARIAUSDT, BLESSUSDT, DOGEUSDT, MUBARAKUSDT, ONUSDT +1 more | 0 |
| sar_live_arms | ok | 50 arms current, none stalled; covering 1122/1122 signals (100%) | 0 |
| sar_refresh_budget | ok | 21 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 1 resolved, 30 still mid-window | 0 |
| scan_cycle | ok | last 66.81s, worst 229.97s over 9476 lifetime cycles; lifetime 308 over 60s, 48 over 120s (plus 1/0 during boot warm-up, not counted); recent 2/0 warn/kill breaches in 20/20 cycles; heartbeat age 11.52s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 218333 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| snapshot_writer | ok | last cycle 28s ago (0.55s to run, worst 194.06s), 1054 overrun(s) of 7535 cycles, TTL 900s; slowest signals=5.65s, data_intake=0.22s, activity=0.05s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=106, gate reads=0, withheld=106) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +20 / upstream +24 | 0 |
| structural_snap | ok | 5998/5998 measured, 35 blind, 0 levels moved (refusals: redetect_cooldown=1866) | 0 |
| structural_veto_lane | ok | 2566 stamped; 0 with no readable level book, 33 with clear air ahead, 1941 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +24 / upstream +48 | 0 |
| tuned_variants | violating | 273 non-stamps — atr_arm_uncomputable=273 (seen=7204 stamped=759 skipped=6172) (streak 343/6) | 343 |
| unlock_shorts | ok | 15 open, 48 scheduled, calendar 0.5h old | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1754193`
- `Path funnel` emissions: `44`
- `Regime distribution` emissions: `44`
- `QUIET_SCALP_BLOCK` events: `48`
- `confidence_gate` events: `4657`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **39**
- Total REST-fallback activations: **4**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 5 | 4020 | 10632 | 20296 | 0 |
| futures_aggtrade | 21 | 9104 | 33260 | 34141 | 0 |
| futures_depth | 3 | 10576 | 10576 | 35557 | 0 |
| futures_liq | 8 | 3369 | 13225 | 20472 | 0 |
| futures_mover | 2 | 48556 | 48556 | 48638 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 4 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=289809] state[populated=289809] buckets[many=289809] sources[none] quality[none]
- funding_rate: presence[absent=30797, present=259012] state[empty=30797, populated=259012] buckets[few=259012, none=30797] sources[none] quality[none]
- liquidation_clusters: presence[absent=168668, present=121141] state[empty=168668, populated=121141] buckets[few=97685, none=168668, some=23456] sources[none] quality[none]
- oi_snapshot: presence[absent=30796, present=259013] state[empty=30796, populated=259013] buckets[few=555, many=255553, none=30796, some=2905] sources[none] quality[none]
- order_book: presence[absent=99131, present=190678] state[populated=190678, unavailable=99131] buckets[few=190678, none=99131] sources[book_ticker=190678, unavailable=99131] quality[none=99131, top_of_book_only=190678]
- orderblocks: presence[absent=289809] state[empty=289809] buckets[none=289809] sources[measured_dark=289809] quality[none]
- recent_ticks: presence[present=289809] state[populated=289809] buckets[many=289809] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.324151039123535` sec
- Median create→first breach: `4806.8309009075165` sec
- Median create→terminal: `4806.830953836441` sec
- Median first breach→terminal: `8.20159912109375e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 1.8}, "under_180s": {"count": 1, "pct": 1.8}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 2.0579517010320063 | 2.269018270878938 | 0.9059861206540638 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 6 | 6 | 1.0329129097923924 | 1.398580133582191 | 0.8609565583465644 | 0 | 6 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 1.701013741877059 | 1.9014742990597777 | 0.8733117082569529 | 0 | 2 |
| MOVER_AVWAP_SCALP | 3 | 3 | 1.3382034242039478 | 1.4529657644197371 | 0.8639217298537403 | 0 | 3 |
| MOVER_TREND_PULLBACK | 30 | 30 | 4.065759175682111 | 3.0 | 1.5097952340522194 | 23 | 7 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 1 | 2.321412747482561 | 2.3214127452174824 | 1.0000000009757328 | 0 | 0 |
| QUIET_COMPRESSION_BREAK | 10 | 10 | 1.1380111983501207 | 1.2860760511917566 | 0.8880845508638964 | 0 | 9 |
| TREND_PULLBACK_EMA | 3 | 3 | 1.3832056797118322 | 1.5965800034897923 | 0.8663553825604929 | 0 | 3 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 3.3222854487843376 | 3.0869274713950254 | 0 | 0 | 0 | 2 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 6 | 1.7872996798984655 | 1.7935431654280067 | 1 | 0 | 0 | 3 | 1 | 2 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2.509357752363616 | 2.556259888246135 | 1 | 1 | 0 | 0 | 0 | 1 |
| MOVER_AVWAP_SCALP | 3 | 1.491749269894044 | 1.9238237411396768 | 3 | 2 | 0 | 0 | 0 | 0 |
| MOVER_TREND_PULLBACK | 30 | 5.270362833229957 | 3.978975 | 5 | 4 | 2 | 25 | 3 | 0 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 5.51967832338248 | 5.51967832338248 | 0 | 0 | 0 | 0 | 0 | 1 |
| QUIET_COMPRESSION_BREAK | 10 | 2.7722909801469076 | 1.7849972503551108 | 0 | 0 | 0 | 8 | 2 | 2 |
| TREND_PULLBACK_EMA | 3 | 2.9860192163857087 | 2.074808519567729 | 0 | 0 | 0 | 3 | 0 | 0 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -2.058 | 5139.7982305288315 | 5139.798293471336 |
| FAILED_AUCTION_RECLAIM | 6 | 6 | 33.3 | 50.0 | 33.3 | 0.0 | -0.0999 | 16847.99781703949 | 16847.99788248539 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 100.0 | 0.0 | 100.0 | 0.0 | 2.5563 | 9826.935217380524 | 9827.758934378624 |
| MOVER_AVWAP_SCALP | 3 | 3 | 66.7 | 0.0 | 66.7 | 0.0 | 1.8877 | 29504.610367774963 | 29517.997844934464 |
| MOVER_TREND_PULLBACK | 30 | 30 | 26.7 | 50.0 | 26.7 | 0.0 | -0.3195 | 3938.5401290655136 | 3938.8210674524307 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2218.8973009586334 | 2218.89732503891 |
| QUIET_COMPRESSION_BREAK | 10 | 10 | 30.0 | 60.0 | 30.0 | 0.0 | 0.1424 | 12994.245118498802 | 12994.245169520378 |
| TREND_PULLBACK_EMA | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | -0.8998 | 2487.097772836685 | 2487.0978348255157 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 426 | 3 | 378 | 0.0 | 0.0 | None | None | 48 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 932 | 23 | 754 | 0.0 | 66.7 | 2487.097772836685 | 2487.0978348255157 | 178 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-10`
- Gating Δ: `-7040`
- No-generation Δ: `-785104`
- Fast failures Δ: `1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.1288, "current_avg_pnl": -0.0999, "current_win_rate": 33.3, "previous_avg_pnl": -0.2287, "previous_win_rate": 25.0, "win_rate_delta": 8.3}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 1.8877, "current_avg_pnl": 1.8877, "current_win_rate": 66.7, "previous_avg_pnl": 0.0, "previous_win_rate": 0.0, "win_rate_delta": 66.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.7689, "current_avg_pnl": -0.3195, "current_win_rate": 26.7, "previous_avg_pnl": 0.4494, "previous_win_rate": 36.4, "win_rate_delta": -9.7}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.1294, "current_avg_pnl": 0.1424, "current_win_rate": 30.0, "previous_avg_pnl": 0.2718, "previous_win_rate": 33.3, "win_rate_delta": -3.3}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": -0.8998, "current_avg_pnl": -0.8998, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -7, "geometry_changed_delta": 0, "geometry_preserved_delta": -325, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": -116, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2487.1, "median_terminal_delta_sec": 2487.1, "sl_rate_delta": 66.7, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **MOVER_AVWAP_SCALP**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
