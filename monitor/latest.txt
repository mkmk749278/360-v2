# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `8271` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 190 | 190 | 119 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 31895 | 31895 | 28455 | 46 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 140787 | 140789 | 14 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 136920 | 136935 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 136370 | 128731 | 8178 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 136969 | 129706 | 7665 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 139446 | 139223 | 269 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 125339 | 125336 | 13 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 137376 | 137433 | 13 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 137453 | 134898 | 3023 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 144479 | 147694 | 2622 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 140807 | 131026 | 13416 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 133782 | 133798 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 136938 | 136926 | 38 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 136312 | 135883 | 483 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 137928 | 132754 | 6934 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 130622 | 130860 | 5389 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 122005 | 116053 | 6373 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 122434 | 121705 | 796 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 140759 | 140723 | 64 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 125352 | 125368 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 30153 | 30153 | 22350 | 47 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1462 | 1462 | 1296 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 59 | 59 | 59 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 33376 | 33376 | 32792 | 13 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 22 | 22 | 17 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7352 | 7352 | 7352 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 6901 | 6901 | 6898 | 3 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 33493 | 33493 | 31487 | 37 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 252 | 252 | 222 | 2 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 3005 | 3005 | 1927 | 23 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 20267 | 20267 | 20267 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 20711 | 20711 | 12051 | 87 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3960 | 3960 | 3717 | 5 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 178 | 178 | 66 | 4 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=140789): breakout_not_found=77653, basic_filters_failed=39378, move_not_fresh=16774, breakout_stale=5253, retest_proximity_failed=1465, volume_spike_missing=251, ema_alignment_reject=13, move_exhausted=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=136937): cls_disabled_merged_into_lsr=136937
- **EVAL::DIVERGENCE_CONTINUATION** (total=128733): cvd_divergence_failed=48474, basic_filters_failed=36288, h1_trend_not_aligned=26003, ema_alignment_reject=14141, retest_proximity_failed=3180, missing_fvg_or_orderblock=647
- **EVAL::FAILED_AUCTION_RECLAIM** (total=129708): auction_not_detected=49294, basic_filters_failed=35818, reclaim_hold_failed=25820, tail_too_small=16404, regime_blocked=2370, rsi_reject=2
- **EVAL::FUNDING_EXTREME** (total=139225): funding_not_extreme=95756, basic_filters_failed=36000, ema_alignment_reject=3065, missing_funding_rate=2848, rsi_reject=811, momentum_reject=390, cvd_divergence_failed=323, missing_fvg_or_orderblock=32
- **EVAL::LIQUIDATION_REVERSAL** (total=125336): cascade_threshold_not_met=87705, basic_filters_failed=36617, cvd_divergence_failed=566, rsi_reject=422, volume_spike_missing=14, missing_fvg_or_orderblock=12
- **EVAL::MA_CROSS_TREND_SHIFT** (total=137435): no_ma_cross=97055, basic_filters_failed=36308, ma_cross_cooldown=2556, ma_cross_htf_misaligned=1516
- **EVAL::MEAN_REVERT** (total=134900): no_extension=116298, basic_filters_failed=18602
- **EVAL::MOVER_AVWAP_SCALP** (total=147694): no_mover_leg=62517, basic_filters_failed=39494, no_avwap_tag=28636, avwap_slope_against=12371, no_avwap_reclaim=2679, avwap_reclaim_no_volume=1997
- **EVAL::MOVER_TREND_PULLBACK** (total=131026): mover_run_too_small=62249, basic_filters_failed=39442, no_reclaim=24520, no_pullback_tag=4815
- **EVAL::OPENING_RANGE_BREAKOUT** (total=133798): feature_disabled=133798
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=136928): regime_blocked=87812, breakout_not_found=32862, basic_filters_failed=11928, adx_reject=4244, ema_alignment_reject=64, rsi_reject=18
- **EVAL::QUIET_COMPRESSION_BREAK** (total=135885): regime_blocked=51339, compression_not_detected=34646, basic_filters_failed=23880, breakout_not_detected=23740, volume_confirmation_failed=2086, rsi_reject=151, missing_fvg_or_orderblock=43
- **EVAL::RANGE_FADE** (total=132756): no_range_edge=114150, basic_filters_failed=18606
- **EVAL::SR_FLIP_RETEST** (total=130862): basic_filters_failed=35796, flip_close_not_confirmed=23621, long_break_volume_thin=18939, whipsaw_flip=14102, long_disabled=13941, reclaim_hold_failed=10606, retest_out_of_zone=7591, regime_blocked=2352, wick_quality_failed=2063, long_acceptance_not_held=1050, missing_fvg_or_orderblock=620, ema_alignment_reject=167, rsi_reject=14
- **EVAL::STANDARD** (total=116053): momentum_reject=45846, adx_reject=25067, sweeps_not_detected=15346, basic_filters_failed=13428, macd_reject=9317, ema_alignment_reject=5941, rsi_reject=629, invalid_sl_geometry=476, mtf_reject=3
- **EVAL::TREND_PULLBACK** (total=121705): h1_trend_not_aligned=32746, h1_pullback_not_confirmed=23127, basic_filters_failed=18411, ema_alignment_reject=18258, no_ema_reclaim_close=8142, ema_not_tested_prev=7852, body_conviction_fail=5259, rsi_reject=4998, prev_already_above_emas=959, prev_already_below_emas=756, no_prev_high_break=391, no_prev_low_break=333, momentum_flat=219, ema21_not_tagged=158, momentum_reject=59, missing_fvg_or_orderblock=37
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=140723): breakout_not_found=73652, basic_filters_failed=39378, move_not_fresh=19457, breakout_stale=5494, retest_proximity_failed=2300, volume_spike_missing=402, missing_fvg_or_orderblock=29, move_exhausted=11
- **EVAL::WHALE_MOMENTUM** (total=125368): momentum_reject=92669, recent_ticks_insufficient=24399, basic_filters_failed=8300

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=1203): setup_compat:regime_VOLATILE_UNSUITABLE=1012, setup_compat:regime_BREAKOUT_EXPANSION=191
- **FAILED_AUCTION_RECLAIM** (total=9573): setup_compat:regime_STRONG_TREND=4916, execution:overextended=2316, context_floor=2279, setup_compat:regime_VOLATILE_UNSUITABLE=62
- **FUNDING_EXTREME_SIGNAL** (total=1263): execution:trigger_not_confirmed=1263
- **LIQUIDATION_REVERSAL** (total=59): execution:trigger_not_confirmed=59
- **LIQUIDITY_SWEEP_REVERSAL** (total=12393): execution:trigger_not_confirmed=4759, execution:overextended=4414, setup_compat:regime_STRONG_TREND=3220
- **MA_CROSS_TREND_SHIFT** (total=16): setup_compat:regime_CLEAN_RANGE=7, setup_compat:regime_DIRTY_RANGE=4, setup_compat:regime_VOLATILE_UNSUITABLE=2, execution:trigger_not_confirmed=2, execution:overextended=1
- **MEAN_REVERT** (total=7352): setup_compat:regime_WEAK_TREND=3620, setup_compat:regime_STRONG_TREND=2205, execution:overextended=1527
- **MOVER_AVWAP_SCALP** (total=6898): execution:overextended=3467, execution:trigger_not_confirmed=3431
- **MOVER_TREND_PULLBACK** (total=31427): execution:overextended=16668, execution:trigger_not_confirmed=14759
- **POST_DISPLACEMENT_CONTINUATION** (total=60): execution:overextended=60
- **QUIET_COMPRESSION_BREAK** (total=979): context_floor=733, execution:trigger_not_confirmed=196, execution:overextended=50
- **RANGE_FADE** (total=9302): execution:overextended=7307, setup_compat:regime_WEAK_TREND=967, setup_compat:regime_STRONG_TREND=791, setup_compat:regime_VOLATILE_UNSUITABLE=237
- **TREND_PULLBACK_EMA** (total=3204): setup_compat:regime_CLEAN_RANGE=2074, setup_compat:regime_DIRTY_RANGE=897, setup_compat:regime_VOLATILE_UNSUITABLE=207, context_floor=26
- **VOLUME_SURGE_BREAKOUT** (total=120): execution:overextended=60, context_floor=60

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 236897 | 30.8% |
| RANGING | 235112 | 30.6% |
| TRENDING_UP | 148863 | 19.4% |
| TRENDING_DOWN | 116124 | 15.1% |
| VOLATILE | 31000 | 4.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **473**
- Average confidence gap to threshold: **13.68** (samples=473) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=51, BTCUSDT=46, WLFIUSDT=43, TRXUSDT=31, AAVEUSDT=27, PENGUUSDT=25, XRPUSDT=24, HYPEUSDT=22, DOGEUSDT=19, XMRUSDT=18

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 22 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 501 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 7 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 656 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 215 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 103 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 715 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 11 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 5 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 25 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 17 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 140 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 3 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 26 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 12 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 859 |
| POST_DISPLACEMENT_CONTINUATION | filtered | min_confidence | 28 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 2 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 65 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 9 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 186 |
| SR_FLIP_RETEST | filtered | min_confidence | 1084 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 149 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1423 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 174 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 11 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 10 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 22 | 62.50 | 65.00 | 2.50 | 17.67 | 16.20 | 20.00 | 4.50 | 3.00 |
| BREAKDOWN_SHORT | kept | 1 | 75.50 | 65.00 | -10.50 | 20.10 | 18.10 | 20.00 | 4.50 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 508 | 55.58 | 63.15 | 7.57 | 20.27 | 19.71 | 18.18 | 1.44 | 12.47 |
| DIVERGENCE_CONTINUATION | kept | 656 | 70.06 | 65.00 | -5.06 | 19.52 | 19.76 | 18.04 | 2.47 | 0.82 |
| FAILED_AUCTION_RECLAIM | filtered | 318 | 52.30 | 64.21 | 11.91 | 20.74 | 19.71 | 20.00 | 4.05 | 13.53 |
| FAILED_AUCTION_RECLAIM | kept | 715 | 70.42 | 65.00 | -5.42 | 21.17 | 19.80 | 20.00 | 4.50 | 0.59 |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 42.65 | 65.00 | 22.35 | 21.13 | 19.98 | 17.00 | 0.73 | 13.36 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 74.00 | 65.00 | -9.00 | 17.84 | 19.80 | 17.00 | 0.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 42 | 56.32 | 65.00 | 8.68 | 20.08 | 19.86 | 17.74 | 1.81 | 14.68 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 140 | 71.17 | 65.00 | -6.17 | 20.97 | 19.78 | 17.04 | 2.40 | 0.00 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 61.50 | 65.00 | 3.50 | 20.90 | 19.80 | 15.80 | 0.00 | 7.20 |
| MOVER_AVWAP_SCALP | kept | 3 | 81.00 | 65.00 | -16.00 | 19.83 | 16.60 | 15.80 | 4.17 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 38 | 59.12 | 61.58 | 2.46 | 19.56 | 18.39 | 15.80 | 5.32 | 6.82 |
| MOVER_TREND_PULLBACK | kept | 859 | 77.54 | 65.00 | -12.54 | 18.72 | 18.21 | 15.80 | 4.30 | 0.11 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 28 | 61.50 | 65.00 | 3.50 | 20.49 | 20.00 | 19.30 | 4.50 | 6.00 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 77.90 | 65.00 | -12.90 | 21.05 | 20.00 | 16.40 | 4.50 | 5.35 |
| QUIET_COMPRESSION_BREAK | filtered | 74 | 49.21 | 64.74 | 15.53 | 19.99 | 19.84 | 20.00 | 0.00 | 10.85 |
| QUIET_COMPRESSION_BREAK | kept | 186 | 73.30 | 65.00 | -8.30 | 20.23 | 19.86 | 20.00 | 0.00 | 0.15 |
| SR_FLIP_RETEST | filtered | 1233 | 57.13 | 64.45 | 7.32 | 20.47 | 19.88 | 15.93 | 1.63 | 12.48 |
| SR_FLIP_RETEST | kept | 1423 | 69.82 | 65.00 | -4.82 | 20.65 | 19.92 | 15.72 | 2.12 | 1.06 |
| TREND_PULLBACK_EMA | kept | 174 | 80.58 | 65.00 | -15.58 | 19.69 | 19.85 | 17.95 | 5.29 | -1.66 |
| VOLUME_SURGE_BREAKOUT | filtered | 11 | 53.20 | 65.00 | 11.80 | 21.20 | 16.70 | 20.00 | 3.50 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 10 | 78.38 | 65.00 | -13.38 | 20.80 | 18.81 | 20.00 | 5.30 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 22 | 62.50 | 2.00 | 18.00 | 12.00 | 14.00 | 5.00 | 10.00 | 4.50 |
| BREAKDOWN_SHORT | kept | 1 | 75.50 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 8.00 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 508 | 55.58 | 20.45 | 15.44 | 5.22 | 12.34 | 5.04 | 8.32 | 1.44 |
| DIVERGENCE_CONTINUATION | kept | 656 | 70.06 | 22.01 | 17.53 | 4.03 | 11.96 | 5.71 | 8.72 | 2.47 |
| FAILED_AUCTION_RECLAIM | filtered | 318 | 52.30 | 21.64 | 15.17 | 7.04 | 11.95 | 6.29 | 4.88 | 4.05 |
| FAILED_AUCTION_RECLAIM | kept | 715 | 70.42 | 23.37 | 14.95 | 3.76 | 11.61 | 6.33 | 6.49 | 4.50 |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 42.65 | 25.00 | 8.00 | 4.91 | 15.91 | 7.27 | 3.74 | 0.73 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 74.00 | 17.00 | 18.00 | 3.00 | 17.00 | 10.00 | 9.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 42 | 56.32 | 19.67 | 15.62 | 10.64 | 10.43 | 6.23 | 6.61 | 1.81 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 140 | 71.17 | 24.96 | 14.00 | 3.79 | 12.27 | 6.85 | 6.90 | 2.40 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 61.50 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 6.70 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 3 | 81.00 | 22.33 | 18.00 | 9.50 | 14.00 | 5.00 | 8.00 | 4.17 |
| MOVER_TREND_PULLBACK | filtered | 38 | 59.12 | 16.95 | 18.00 | 8.61 | 13.32 | 5.42 | 8.60 | 5.32 |
| MOVER_TREND_PULLBACK | kept | 859 | 77.54 | 19.32 | 18.24 | 7.65 | 13.24 | 5.87 | 9.20 | 4.30 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 28 | 61.50 | 2.00 | 18.00 | 15.00 | 14.00 | 5.00 | 9.00 | 4.50 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 77.90 | 17.00 | 18.00 | 15.00 | 14.00 | 6.75 | 8.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 74 | 49.21 | 17.11 | 17.51 | 11.27 | 14.20 | 6.35 | 3.63 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 186 | 73.30 | 18.38 | 17.81 | 11.05 | 14.03 | 6.39 | 6.47 | 0.00 |
| SR_FLIP_RETEST | filtered | 1233 | 57.13 | 19.51 | 16.79 | 5.09 | 13.26 | 6.21 | 7.11 | 1.63 |
| SR_FLIP_RETEST | kept | 1423 | 69.82 | 21.90 | 17.03 | 4.51 | 12.91 | 5.86 | 7.32 | 2.12 |
| TREND_PULLBACK_EMA | kept | 174 | 80.58 | 19.21 | 18.00 | 7.50 | 14.02 | 6.92 | 9.64 | 5.29 |
| VOLUME_SURGE_BREAKOUT | filtered | 11 | 53.20 | 17.00 | 18.00 | 12.00 | 11.00 | 5.00 | 4.70 | 3.50 |
| VOLUME_SURGE_BREAKOUT | kept | 10 | 78.38 | 23.40 | 14.80 | 12.00 | 13.40 | 5.00 | 7.48 | 5.30 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 22 | 62.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 1 | 75.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 508 | 55.58 | 0.00 | 0.00 | 1.10 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | **2.10** |
| DIVERGENCE_CONTINUATION | kept | 656 | 70.06 | 0.00 | 0.00 | 0.37 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | **0.40** |
| FAILED_AUCTION_RECLAIM | filtered | 318 | 52.30 | 0.00 | 0.00 | 0.36 | 0.00 | 9.85 | 0.00 | 0.00 | 0.00 | **10.21** |
| FAILED_AUCTION_RECLAIM | kept | 715 | 70.42 | 0.00 | 0.00 | 0.47 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | **0.50** |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 42.65 | 0.00 | 0.00 | 2.91 | 0.00 | 5.45 | 0.00 | 0.00 | 0.00 | **8.36** |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 74.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 42 | 56.32 | 0.00 | 0.00 | 0.69 | 0.00 | 12.86 | 0.00 | 0.00 | 0.00 | **13.55** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 140 | 71.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 61.50 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.20** |
| MOVER_AVWAP_SCALP | kept | 3 | 81.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 38 | 59.12 | 0.00 | 0.00 | 0.00 | 0.00 | 6.82 | 0.00 | 0.00 | 0.00 | **6.82** |
| MOVER_TREND_PULLBACK | kept | 859 | 77.54 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | **0.01** |
| POST_DISPLACEMENT_CONTINUATION | filtered | 28 | 61.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 77.90 | 0.00 | 0.00 | 0.00 | 0.00 | 2.35 | 0.00 | 0.00 | 0.00 | **2.35** |
| QUIET_COMPRESSION_BREAK | filtered | 74 | 49.21 | 0.00 | 0.00 | 0.00 | 0.00 | 1.60 | 0.00 | 0.00 | 7.18 | **8.78** |
| QUIET_COMPRESSION_BREAK | kept | 186 | 73.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.86 | 0.00 | 0.00 | 0.00 | **0.86** |
| SR_FLIP_RETEST | filtered | 1233 | 57.13 | 0.00 | 0.00 | 0.69 | 0.00 | 2.75 | 0.00 | 0.00 | 0.27 | **3.71** |
| SR_FLIP_RETEST | kept | 1423 | 69.82 | 0.00 | 0.00 | 0.06 | 0.00 | 0.18 | 0.00 | 0.00 | 0.05 | **0.29** |
| TREND_PULLBACK_EMA | kept | 174 | 80.58 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 11 | 53.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 10 | 78.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=807 (17.0%) | WOULD_LOSE=933 | WOULD_EXPIRE=3013 | pending (awaiting window)=247

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_floor:FAILED_AUCTION_RECLAIM | 1460 | 6.9% | 478.2 | 185.8 | +0.20 | **KEEP** |
| context_floor:QUIET_COMPRESSION_BREAK | 662 | 0.0% | 108.7 | 0.0 | +0.16 | **KEEP** |
| context_floor:TREND_PULLBACK_EMA | 26 | 30.8% | 10.1 | 8.0 | +0.08 | **TUNE** |
| context_floor:VOLUME_SURGE_BREAKOUT | 46 | 0.0% | 8.3 | 0.0 | +0.18 | **KEEP** |
| dispatch_cooldown | 113 | 0.0% | 20.4 | 0.0 | +0.18 | **KEEP** |
| dispatch_staleness_v2 | 153 | 85.6% | 24.6 | 127.0 | -0.67 | **DROP** |
| level_still_in_play | 779 | 25.0% | 123.9 | 76.8 | +0.06 | **TUNE** |
| min_confidence | 955 | 20.3% | 625.0 | 204.6 | +0.44 | **KEEP** |
| quiet_scalp_block | 272 | 3.7% | 124.9 | 13.0 | +0.41 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 3 | 33.3% | 1.1 | 0.4 | +0.22 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 105 | 71.4% | 31.4 | 54.7 | -0.22 | **DROP** |
| shadow_unit:SHADOW_MEAN_REVERT | 51 | 54.9% | 13.9 | 68.5 | -1.07 | **DROP** |
| shadow_unit:SHADOW_RANGE_FADE | 128 | 50.0% | 25.4 | 158.8 | -1.04 | **DROP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 71816 across 20 strategies; 1633 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 15617 | 50/15567/0 | 65% | +0.24 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MAJOR (+1.27R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/ALTCOIN (-1.27R) |
| FAILED_AUCTION_RECLAIM | 12923 | 26/12897/0 | 49% | -0.01 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (-1.19R) |
| SR_FLIP_RETEST | 11874 | 4/11870/0 | 42% | -0.22 | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.15R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.30R) |
| DIVERGENCE_CONTINUATION | 6821 | 10/6811/0 | 50% | -0.03 | NY/MARKUP/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.34R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| QUIET_COMPRESSION_BREAK | 5172 | 0/5172/0 | 49% | +0.02 | ASIA/RANGE/NORMAL/BTC_RISING (+1.16R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MEAN_REVERT | 2999 | 0/2999/0 | 80% | +0.60 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.14R) |
| SHADOW_MEAN_REVERT | 2905 | 0/0/2905 | 39% | -0.00 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.06R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| LIQUIDITY_SWEEP_REVERSAL | 2796 | 9/2787/0 | 42% | -0.14 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.78R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.50R) |
| SHADOW_RANGE_FADE | 2691 | 0/0/2691 | 41% | +0.26 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.30R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| SHADOW_FUNDING_FADE | 2036 | 0/0/2036 | 42% | -0.26 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL (+0.41R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING (-1.00R) |
| RANGE_FADE | 1804 | 0/1804/0 | 3% | -0.98 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.21R) |
| VOLUME_SURGE_BREAKOUT | 1295 | 12/1283/0 | 41% | -0.00 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| TREND_PULLBACK_EMA | 1171 | 2/1169/0 | 50% | -0.16 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.73R) | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (-1.19R) |
| WHALE_MOMENTUM | 474 | 0/474/0 | 54% | -0.11 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 374 | 2/372/0 | 33% | -0.16 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.05R) |
| BREAKDOWN_SHORT | 299 | 7/292/0 | 59% | +0.33 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| MOVER_AVWAP_SCALP | 277 | 20/257/0 | 37% | -0.32 | NY/MARKUP/CASCADE/BTC_FALLING (+0.55R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 217 | 0/0/217 | 45% | -0.11 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.03R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| POST_DISPLACEMENT_CONTINUATION | 67 | 0/67/0 | 90% | +0.75 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 4 | 1/3/0 | 75% | +0.16 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP` +1.78R (n=42, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.50R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.45R (n=17, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.45R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| VOLUME_SURGE_BREAKOUT | 35 | 40% / +0.06R | 35 | 34% / -0.16R | -0.22 | **FIXED** |
| TREND_PULLBACK_EMA | 27 | 52% / -0.14R | 27 | 56% / +0.05R | +0.20 | **ATR** |
| MEAN_REVERT | 235 | 58% / +0.15R | 235 | 56% / +0.28R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 51 | 43% / -0.06R | 51 | 53% / +0.07R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 31 | 42% / -0.16R | 31 | 39% / -0.26R | -0.10 | **FIXED** |
| LIQUIDITY_SWEEP_REVERSAL | 332 | 47% / -0.15R | 332 | 51% / -0.07R | +0.08 | **ATR** |
| SR_FLIP_RETEST | 1700 | 47% / -0.13R | 1700 | 50% / -0.05R | +0.08 | **ATR** |
| QUIET_COMPRESSION_BREAK | 738 | 45% / -0.04R | 738 | 45% / -0.07R | -0.03 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 1558 | 47% / -0.08R | 1558 | 47% / -0.05R | +0.03 | **ATR** |
| DIVERGENCE_CONTINUATION | 330 | 50% / -0.02R | 330 | 55% / -0.00R | +0.02 | **ATR** |
| RANGE_FADE | 137 | 2% / -1.04R | 137 | 2% / -1.04R | +0.01 | **ATR** |
| MOVER_TREND_PULLBACK | 1567 | 58% / +0.07R | 1567 | 61% / +0.07R | -0.00 | **FIXED** |
| BREAKDOWN_SHORT | 10 | 20% / -0.31R | 10 | 20% / -0.31R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 7 | 14% / -0.71R | 7 | 43% / -0.21R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 3 | 67% / -0.00R | 3 | 67% / -0.22R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 83% / +0.45R | 6 | 83% / +0.12R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 374 | 29% | -0.14R | 84 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 41 | 54% | +0.05R | 31 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 3 | 0% | -0.14R | 3 | MEASURING |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 355 | 24% / -5.31R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 1 | 0% / -2.44R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 275 | 27% / -2.13R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 346 | 38% / -1.18R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 10 | 20% / -5.55R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 110 | 11% / -9.21R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 110 | 52% / +0.81R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 65 | 31% / -4.80R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 9 | 11% / -9.42R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 15 | 13% / -5.37R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 2 | 50% / -0.16R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 1 | 0% / -1.85R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._

| Setup | Gate | n | WOULD_WIN% | EV/suppression (R) | Verdict |
|---|---|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | dispatch_staleness_v2 | 94 | 100.0% | -1.24 | **DROP** |
| SHADOW_MEAN_REVERT | shadow_unit:SHADOW_MEAN_REVERT | 51 | 54.9% | -1.07 | **DROP** |
| SHADOW_RANGE_FADE | shadow_unit:SHADOW_RANGE_FADE | 128 | 50.0% | -1.04 | **DROP** |
| MOVER_TREND_PULLBACK | min_confidence | 26 | 65.4% | -0.42 | **DROP** |
| MOVER_TREND_PULLBACK | level_still_in_play | 9 | 77.8% | -0.27 | **INSUFFICIENT_SAMPLE** |
| SHADOW_FUNDING_FADE | shadow_unit:SHADOW_FUNDING_FADE | 105 | 71.4% | -0.22 | **DROP** |
| DIVERGENCE_CONTINUATION | level_still_in_play | 215 | 32.1% | -0.06 | **TUNE** |
| DIVERGENCE_CONTINUATION | quiet_scalp_block | 7 | 14.3% | -0.03 | **INSUFFICIENT_SAMPLE** |
| TREND_PULLBACK_EMA | level_still_in_play | 85 | 75.3% | +0.02 | **TUNE** |
| FUNDING_EXTREME_SIGNAL | min_confidence | 11 | 36.4% | +0.04 | **INSUFFICIENT_SAMPLE** |
| TREND_PULLBACK_EMA | context_floor:TREND_PULLBACK_EMA | 26 | 30.8% | +0.08 | **TUNE** |
| DIVERGENCE_CONTINUATION | dispatch_cooldown | 9 | 0.0% | +0.10 | **INSUFFICIENT_SAMPLE** |
| LIQUIDITY_SWEEP_REVERSAL | level_still_in_play | 24 | 12.5% | +0.10 | **KEEP** |
| FAILED_AUCTION_RECLAIM | level_still_in_play | 262 | 1.9% | +0.12 | **KEEP** |
| SR_FLIP_RETEST | level_still_in_play | 158 | 29.7% | +0.13 | **KEEP** |
| MA_CROSS_TREND_SHIFT | min_confidence | 1 | 0.0% | +0.14 | **INSUFFICIENT_SAMPLE** |
| QUIET_COMPRESSION_BREAK | context_floor:QUIET_COMPRESSION_BREAK | 662 | 0.0% | +0.16 | **KEEP** |
| FAILED_AUCTION_RECLAIM | quiet_scalp_block | 123 | 3.3% | +0.17 | **KEEP** |
| SR_FLIP_RETEST | dispatch_staleness_v2 | 40 | 70.0% | +0.18 | **KEEP** |
| VOLUME_SURGE_BREAKOUT | context_floor:VOLUME_SURGE_BREAKOUT | 46 | 0.0% | +0.18 | **KEEP** |
| POST_DISPLACEMENT_CONTINUATION | min_confidence | 28 | 0.0% | +0.19 | **KEEP** |
| BREAKDOWN_SHORT | min_confidence | 22 | 0.0% | +0.19 | **KEEP** |
| QUIET_COMPRESSION_BREAK | min_confidence | 8 | 0.0% | +0.19 | **INSUFFICIENT_SAMPLE** |
| SR_FLIP_RETEST | dispatch_cooldown | 104 | 0.0% | +0.19 | **KEEP** |
| QUIET_COMPRESSION_BREAK | level_still_in_play | 26 | 0.0% | +0.19 | **KEEP** |

- _sorted most-costly first: the top rows are gates whose suppressions lose more than they save on that specific path_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 19 · alerting: **2** · boot grace active: False
- **ALERT** `edge_reconciliation` — MOVER_AVWAP_SCALP realized−counterfactual=+0.34R (bound 0.3) (streak 108/6) (sustained 108 cycles)
- **ALERT** `mean_revert_emission` — 2404 detections since last emission (emitted_total=0) — and the blocked candidates measure +0.60R over n=2999, so the gating is COSTING us. Check gate rejections. (streak 108/6) (sustained 108 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=5 fanouts=5 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 65352.50 | 0 |
| candle_coverage | ok | 84/90 symbols with ≥20 15m candles | 0 |
| context_emission_policy | ok | output +1 / upstream +51 | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.34R (bound 0.3) (streak 108/6) | 108 |
| emission_controller | ok | last cycle 1585s ago; live_overrides=18 | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +2 / upstream +3 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 2404 detections since last emission (emitted_total=0) — and the blocked candidates measure +0.60R over n=2999, so the gating is COSTING us. Check gate rejections. (streak 108/6) | 108 |
| mean_revert_path | ok | output +0 / upstream +3 | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE counterfactuals measure -0.98R over n=1804 — emitting them would lose money | 0 |
| range_fade_path | ok | output +116 / upstream +3 | 0 |
| sar_exit_shadow | ok | output +2 / upstream +3 | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +98 / upstream +3 | 0 |
| suppression_audit | ok | output +3 / upstream +51 | 0 |
| tuned_variants | ok | seen=45 stamped=13 skipped=32 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3425176`
- `Path funnel` emissions: `97`
- `Regime distribution` emissions: `97`
- `QUIET_SCALP_BLOCK` events: `473`
- `confidence_gate` events: `6460`
- `free_channel_post` events: `17`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **5**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 1658 | 1658 | 1658 | 0 |
| futures_liq | 4 | 2257 | 2813 | 5989 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **17**

| Source | Count |
|---|---:|
| signal_close | 13 |
| regime_shift | 2 |
| signal_highlight | 2 |

- By severity: HIGH=17

## Dependency readiness
- cvd: presence[present=589094] state[populated=589094] buckets[many=589094] sources[none] quality[none]
- funding_rate: presence[absent=40933, present=548161] state[empty=40933, populated=548161] buckets[few=548161, none=40933] sources[none] quality[none]
- liquidation_clusters: presence[absent=352835, present=236259] state[empty=352835, populated=236259] buckets[few=190979, none=352835, some=45280] sources[none] quality[none]
- oi_snapshot: presence[absent=39282, present=549812] state[empty=39282, populated=549812] buckets[many=549812, none=39282] sources[none] quality[none]
- order_book: presence[absent=159436, present=429658] state[populated=429658, unavailable=159436] buckets[few=429658, none=159436] sources[book_ticker=429658, unavailable=159436] quality[none=159436, top_of_book_only=429658]
- orderblocks: presence[absent=589094] state[empty=589094] buckets[none=589094] sources[not_implemented=589094] quality[none]
- recent_ticks: presence[absent=8851, present=580243] state[empty=8851, populated=580243] buckets[many=580243, none=8851] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.206150054931641` sec
- Median create→first breach: `3223.7905280590057` sec
- Median create→terminal: `3224.3778800964355` sec
- Median first breach→terminal: `3.361150026321411` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 5.5811 | 3223.7905280590057 | 3224.3778800964355 |
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | 0.3391 | 1881.9754600524902 | 1884.6559096574783 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.3451 | 7612.290158510208 | 7612.996894478798 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 2.7955 | 3491.6835238933563 | 4117.150485038757 |
| MOVER_TREND_PULLBACK | 5 | 5 | 0.0 | 20.0 | 0.0 | 0.0 | 2.5837 | 2889.5012760162354 | 2892.194291114807 |
| SR_FLIP_RETEST | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 5.6812 | 3637.192337989807 | 3643.121678829193 |
| TREND_PULLBACK_EMA | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 4.4221 | 2004.339840888977 | 2005.9051780700684 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 20711 | 87 | 12051 | 100.0 | 0.0 | 3637.192337989807 | 3643.121678829193 | 8660 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3960 | 5 | 3717 | 100.0 | 0.0 | 2004.339840888977 | 2005.9051780700684 | 243 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-55`
- Gating Δ: `24605`
- No-generation Δ: `59776`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.9228, "current_avg_pnl": 2.5837, "current_win_rate": 0.0, "previous_avg_pnl": 1.6609, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -16, "geometry_changed_delta": 0, "geometry_preserved_delta": -5191, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 3637.19, "median_terminal_delta_sec": 3643.12, "sl_rate_delta": 0.0, "win_rate_delta": 100.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 130, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2004.34, "median_terminal_delta_sec": 2005.91, "sl_rate_delta": 0.0, "win_rate_delta": 100.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
