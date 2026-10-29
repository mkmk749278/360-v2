# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MEAN_REVERT, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `6` sec (warning=False)
- Latest performance record age: `780` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 43 | 43 | 43 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 5235 | 5235 | 4363 | 16 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 48848 | 48864 | 15 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 47857 | 47857 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 47516 | 46057 | 1786 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 47885 | 46989 | 1009 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 47972 | 47941 | 47 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 40482 | 40490 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 48001 | 48038 | 20 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 48069 | 46425 | 2576 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 51575 | 56435 | 485 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 48885 | 44801 | 6720 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 47620 | 47620 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 47864 | 47879 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 47472 | 47362 | 145 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 49009 | 47847 | 1629 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 47107 | 47247 | 197 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 39484 | 36156 | 3745 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 39903 | 39640 | 334 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 48817 | 48820 | 27 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 40496 | 40517 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3130 | 3130 | 2762 | 5 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 179 | 179 | 27 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 17 | 17 | 0 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15173 | 15173 | 14888 | 8 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 27 | 27 | 7 | 4 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 5981 | 5981 | 4743 | 10 | active-low-quality (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 983 | 983 | 220 | 46 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 14614 | 14614 | 7235 | 252 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 7 | 7 | 7 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 565 | 565 | 358 | 41 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3754 | 3754 | 3591 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 522 | 522 | 272 | 9 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1159 | 1159 | 868 | 38 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 52 | 52 | 7 | 8 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=48864): breakout_not_found=26179, basic_filters_failed=11407, move_not_fresh=8241, breakout_stale=2138, retest_proximity_failed=739, volume_spike_missing=131, move_exhausted=22, missing_fvg_or_orderblock=7
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=47857): cls_disabled_merged_into_lsr=47857
- **EVAL::DIVERGENCE_CONTINUATION** (total=46057): cvd_divergence_failed=17768, h1_trend_not_aligned=13987, basic_filters_failed=9582, ema_alignment_reject=3721, retest_proximity_failed=804, missing_fvg_or_orderblock=195
- **EVAL::FAILED_AUCTION_RECLAIM** (total=46989): auction_not_detected=29984, basic_filters_failed=9091, reclaim_hold_failed=3169, regime_blocked=2366, tail_too_small=2353, rsi_reject=26
- **EVAL::FUNDING_EXTREME** (total=47941): funding_not_extreme=34787, basic_filters_failed=8779, missing_funding_rate=3501, ema_alignment_reject=585, rsi_reject=204, momentum_reject=42, cvd_divergence_failed=34, missing_fvg_or_orderblock=9
- **EVAL::LIQUIDATION_REVERSAL** (total=40490): cascade_threshold_not_met=30482, basic_filters_failed=9542, rsi_reject=267, cvd_divergence_failed=167, missing_fvg_or_orderblock=24, volume_spike_missing=8
- **EVAL::MA_CROSS_TREND_SHIFT** (total=48038): no_ma_cross=36678, basic_filters_failed=9604, ma_cross_cooldown=1146, ma_cross_htf_misaligned=610
- **EVAL::MEAN_REVERT** (total=46425): no_extension=38695, basic_filters_failed=7730
- **EVAL::MOVER_AVWAP_SCALP** (total=56435): no_avwap_tag=23621, no_mover_leg=15730, basic_filters_failed=11583, avwap_slope_against=3331, avwap_reclaim_no_volume=1286, no_avwap_reclaim=823, anchor_too_recent=61
- **EVAL::MOVER_TREND_PULLBACK** (total=44801): mover_run_too_small=22293, basic_filters_failed=11507, no_reclaim=9400, no_pullback_tag=1601
- **EVAL::OPENING_RANGE_BREAKOUT** (total=47620): feature_disabled=47620
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=47879): regime_blocked=36950, breakout_not_found=7803, basic_filters_failed=2672, adx_reject=418, ema_alignment_reject=36
- **EVAL::QUIET_COMPRESSION_BREAK** (total=47362): compression_not_detected=23361, regime_blocked=13227, basic_filters_failed=6408, breakout_not_detected=4055, volume_confirmation_failed=284, rsi_reject=24, missing_fvg_or_orderblock=3
- **EVAL::RANGE_FADE** (total=47847): no_range_edge=40111, basic_filters_failed=7736
- **EVAL::SR_FLIP_RETEST** (total=47247): flip_close_not_confirmed=30362, basic_filters_failed=9072, regime_blocked=2346, long_break_volume_thin=1609, h1_break_not_confirmed=1602, retest_out_of_zone=1301, reclaim_hold_failed=548, long_acceptance_not_held=192, ema_alignment_reject=73, wick_quality_failed=66, whipsaw_flip=58, missing_fvg_or_orderblock=18
- **EVAL::STANDARD** (total=36156): momentum_reject=10953, adx_reject=7017, basic_filters_failed=6308, macd_reject=4909, sweeps_not_detected=4268, ema_alignment_reject=2125, htf_poi_unanchored=475, rsi_reject=58, invalid_sl_geometry=42, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=39640): h1_trend_not_aligned=14705, ema_alignment_reject=6568, h1_pullback_not_confirmed=5364, basic_filters_failed=4748, ema_not_tested_prev=2614, no_ema_reclaim_close=2434, rsi_reject=1147, body_conviction_fail=1108, prev_already_above_emas=335, no_prev_high_break=189, prev_already_below_emas=151, no_prev_low_break=129, ema21_not_tagged=55, momentum_flat=42, missing_fvg_or_orderblock=40, momentum_reject=11
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=48820): breakout_not_found=31043, basic_filters_failed=11403, move_not_fresh=3889, breakout_stale=1502, retest_proximity_failed=790, volume_spike_missing=171, move_exhausted=21, missing_fvg_or_orderblock=1
- **EVAL::WHALE_MOMENTUM** (total=40517): momentum_reject=33025, recent_ticks_insufficient=5416, basic_filters_failed=2076

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=4): execution:overextended=4
- **DIVERGENCE_CONTINUATION** (total=218): setup_compat:regime_VOLATILE_UNSUITABLE=207, setup_compat:regime_BREAKOUT_EXPANSION=11
- **FAILED_AUCTION_RECLAIM** (total=864): setup_compat:regime_STRONG_TREND=391, execution:overextended=332, context_floor=137, setup_compat:regime_VOLATILE_UNSUITABLE=4
- **FUNDING_EXTREME_SIGNAL** (total=131): execution:trigger_not_confirmed=129, context_floor=2
- **LIQUIDATION_REVERSAL** (total=17): execution:trigger_not_confirmed=17
- **LIQUIDITY_SWEEP_REVERSAL** (total=3888): execution:trigger_not_confirmed=1881, execution:overextended=1094, setup_compat:regime_STRONG_TREND=913
- **MA_CROSS_TREND_SHIFT** (total=28): setup_compat:regime_DIRTY_RANGE=13, execution:trigger_not_confirmed=6, setup_compat:regime_CLEAN_RANGE=6, execution:overextended=2, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=1815): setup_compat:regime_STRONG_TREND=839, setup_compat:regime_WEAK_TREND=584, execution:overextended=321, entry_quality=71
- **MOVER_AVWAP_SCALP** (total=703): execution:overextended=422, execution:trigger_not_confirmed=163, entry_quality=118
- **MOVER_TREND_PULLBACK** (total=7160): execution:trigger_not_confirmed=3777, execution:overextended=2483, entry_quality=900
- **QUIET_COMPRESSION_BREAK** (total=3): execution:trigger_not_confirmed=3
- **RANGE_FADE** (total=1252): setup_compat:regime_STRONG_TREND=611, setup_compat:regime_WEAK_TREND=442, setup_compat:regime_VOLATILE_UNSUITABLE=164, execution:overextended=34, setup_compat:regime_BREAKOUT_EXPANSION=1
- **TREND_PULLBACK_EMA** (total=1108): setup_compat:regime_CLEAN_RANGE=617, setup_compat:regime_DIRTY_RANGE=366, entry_quality=81, setup_compat:regime_VOLATILE_UNSUITABLE=44
- **VOLUME_SURGE_BREAKOUT** (total=1): execution:overextended=1

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 117434 | 50.6% |
| QUIET | 46270 | 20.0% |
| TRENDING_DOWN | 31087 | 13.4% |
| TRENDING_UP | 24620 | 10.6% |
| VOLATILE | 12487 | 5.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **93**
- Average confidence gap to threshold: **11.01** (samples=93) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: CAPUSDT=21, XMRUSDT=9, LITUSDT=6, TAOUSDT=6, SOLUSDT=6, ASTERUSDT=6, ZECUSDT=5, TRXUSDT=5, HUMAUSDT=5, SUIUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 148 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 2 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 59 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 83 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 8 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 5 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 3 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 17 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 62 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 33 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 3 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 5 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 8 |
| MEAN_REVERT | filtered | min_confidence | 4 |
| MEAN_REVERT | kept | min_confidence_pass | 11 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 209 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 9 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 240 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1750 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 30 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2019 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 37 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 24 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 122 |
| SR_FLIP_RETEST | filtered | min_confidence | 25 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 6 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 16 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 73 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 70 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 27 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 17 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 150 | 51.50 | 63.73 | 12.23 | 20.77 | 19.87 | 18.59 | 1.31 | 13.65 |
| DIVERGENCE_CONTINUATION | kept | 59 | 69.53 | 65.00 | -4.53 | 21.40 | 19.18 | 18.93 | 1.31 | 3.09 |
| FAILED_AUCTION_RECLAIM | filtered | 91 | 51.68 | 63.95 | 12.27 | 21.35 | 19.25 | 20.00 | 2.17 | 5.43 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 69.96 | 65.00 | -4.96 | 21.38 | 18.96 | 20.00 | 2.90 | 5.04 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 41.27 | 61.00 | 19.73 | 21.20 | 17.60 | 17.00 | 2.33 | 9.67 |
| LIQUIDATION_REVERSAL | filtered | 17 | 36.29 | 10.00 | -26.29 | 20.76 | 8.00 | 17.74 | 4.12 | 18.24 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 63 | 53.19 | 64.49 | 11.30 | 20.73 | 19.61 | 18.90 | 1.03 | 8.71 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 33 | 69.22 | 65.00 | -4.22 | 21.54 | 18.27 | 18.85 | 2.61 | 1.36 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 55.47 | 61.00 | 5.53 | 20.53 | 18.73 | 15.80 | 0.00 | 12.10 |
| MA_CROSS_TREND_SHIFT | kept | 5 | 70.70 | 65.00 | -5.70 | 21.18 | 18.94 | 15.80 | 0.00 | 1.26 |
| MEAN_REVERT | filtered | 12 | 55.17 | 65.00 | 9.83 | 20.58 | 19.25 | 14.93 | 0.00 | 18.40 |
| MEAN_REVERT | kept | 11 | 72.17 | 65.00 | -7.17 | 20.82 | 16.25 | 15.94 | 0.00 | 2.91 |
| MOVER_AVWAP_SCALP | filtered | 218 | 52.22 | 64.72 | 12.50 | 19.87 | 15.11 | 15.80 | 4.06 | 19.98 |
| MOVER_AVWAP_SCALP | kept | 240 | 78.11 | 65.00 | -13.11 | 21.03 | 16.15 | 15.80 | 4.47 | 4.59 |
| MOVER_TREND_PULLBACK | filtered | 1780 | 54.04 | 63.98 | 9.94 | 19.38 | 18.44 | 15.80 | 3.67 | 17.55 |
| MOVER_TREND_PULLBACK | kept | 2019 | 75.60 | 65.00 | -10.60 | 20.41 | 18.32 | 15.80 | 4.10 | 1.05 |
| QUIET_COMPRESSION_BREAK | filtered | 61 | 55.77 | 65.00 | 9.23 | 20.67 | 18.69 | 20.00 | 0.00 | 13.36 |
| QUIET_COMPRESSION_BREAK | kept | 122 | 77.34 | 65.00 | -12.34 | 21.50 | 19.67 | 20.00 | 0.00 | 0.26 |
| SR_FLIP_RETEST | filtered | 31 | 51.37 | 62.77 | 11.40 | 21.62 | 20.00 | 15.27 | 1.95 | 18.11 |
| SR_FLIP_RETEST | kept | 16 | 64.88 | 65.00 | 0.12 | 20.47 | 20.00 | 15.85 | 2.59 | 4.92 |
| TREND_PULLBACK_EMA | filtered | 78 | 53.43 | 64.54 | 11.11 | 20.54 | 19.84 | 18.76 | 4.32 | 19.61 |
| TREND_PULLBACK_EMA | kept | 70 | 75.68 | 65.00 | -10.68 | 21.60 | 19.86 | 17.83 | 4.39 | 1.10 |
| VOLUME_SURGE_BREAKOUT | filtered | 27 | 58.36 | 64.41 | 6.05 | 22.05 | 18.47 | 20.00 | 3.50 | 1.44 |
| VOLUME_SURGE_BREAKOUT | kept | 17 | 78.41 | 65.00 | -13.41 | 20.04 | 18.39 | 20.00 | 5.03 | 3.12 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 150 | 51.50 | 23.51 | 11.93 | 5.50 | 12.35 | 5.89 | 8.27 | 1.31 |
| DIVERGENCE_CONTINUATION | kept | 59 | 69.53 | 24.73 | 12.75 | 7.02 | 13.10 | 5.26 | 8.68 | 1.31 |
| FAILED_AUCTION_RECLAIM | filtered | 91 | 51.68 | 19.48 | 15.45 | 6.92 | 13.51 | 6.77 | 5.98 | 2.17 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 69.96 | 23.40 | 17.20 | 6.00 | 14.20 | 7.80 | 6.94 | 2.90 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 41.27 | 25.00 | 8.00 | 4.00 | 13.33 | 8.17 | 5.10 | 2.33 |
| LIQUIDATION_REVERSAL | filtered | 17 | 36.29 | 25.00 | 8.00 | 12.88 | 8.00 | 7.12 | 0.00 | 4.12 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 63 | 53.19 | 21.16 | 14.51 | 9.33 | 12.83 | 5.10 | 6.04 | 1.03 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 33 | 69.22 | 22.27 | 14.73 | 6.36 | 12.15 | 5.03 | 7.52 | 2.61 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 55.47 | 17.00 | 14.00 | 5.00 | 14.00 | 8.67 | 8.87 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 5 | 70.70 | 20.20 | 14.00 | 7.20 | 13.40 | 8.10 | 9.06 | 0.00 |
| MEAN_REVERT | filtered | 12 | 55.17 | 23.00 | 18.00 | 9.00 | 13.00 | 5.00 | 5.57 | 0.00 |
| MEAN_REVERT | kept | 11 | 72.17 | 21.36 | 16.91 | 12.00 | 13.00 | 5.27 | 6.54 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 218 | 52.22 | 18.84 | 18.17 | 10.86 | 13.24 | 6.03 | 6.28 | 4.06 |
| MOVER_AVWAP_SCALP | kept | 240 | 78.11 | 19.97 | 18.02 | 11.86 | 13.08 | 6.88 | 8.43 | 4.47 |
| MOVER_TREND_PULLBACK | filtered | 1780 | 54.04 | 18.65 | 18.03 | 7.65 | 12.24 | 6.13 | 8.65 | 3.67 |
| MOVER_TREND_PULLBACK | kept | 2019 | 75.60 | 19.25 | 18.01 | 7.80 | 12.52 | 6.52 | 8.70 | 4.10 |
| QUIET_COMPRESSION_BREAK | filtered | 61 | 55.77 | 18.31 | 15.57 | 11.90 | 13.97 | 7.38 | 4.23 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 122 | 77.34 | 18.51 | 17.67 | 13.08 | 13.97 | 7.06 | 7.65 | 0.00 |
| SR_FLIP_RETEST | filtered | 31 | 51.37 | 20.35 | 16.06 | 3.87 | 14.19 | 5.48 | 8.52 | 1.95 |
| SR_FLIP_RETEST | kept | 16 | 64.88 | 24.50 | 16.75 | 4.50 | 12.94 | 5.38 | 4.08 | 2.59 |
| TREND_PULLBACK_EMA | filtered | 78 | 53.43 | 14.47 | 18.00 | 7.79 | 14.31 | 7.92 | 8.74 | 4.32 |
| TREND_PULLBACK_EMA | kept | 70 | 75.68 | 17.64 | 18.00 | 7.69 | 14.10 | 6.87 | 8.94 | 4.39 |
| VOLUME_SURGE_BREAKOUT | filtered | 27 | 58.36 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 5.30 | 3.50 |
| VOLUME_SURGE_BREAKOUT | kept | 17 | 78.41 | 21.71 | 16.12 | 13.76 | 12.76 | 5.00 | 8.02 | 5.03 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 150 | 51.50 | 0.00 | 0.00 | 1.11 | 0.00 | 0.29 | 0.00 | 0.00 | 0.00 | **1.40** |
| DIVERGENCE_CONTINUATION | kept | 59 | 69.53 | 0.00 | 0.00 | 0.79 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | **0.91** |
| FAILED_AUCTION_RECLAIM | filtered | 91 | 51.68 | 0.00 | 0.00 | 1.16 | 0.00 | 1.58 | 0.00 | 0.00 | 0.00 | **2.74** |
| FAILED_AUCTION_RECLAIM | kept | 5 | 69.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 41.27 | 0.00 | 0.00 | 2.67 | 0.00 | 4.00 | 0.00 | 0.00 | 0.00 | **6.67** |
| LIQUIDATION_REVERSAL | filtered | 17 | 36.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 63 | 53.19 | 0.00 | 0.00 | 0.86 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | **1.09** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 33 | 69.22 | 0.00 | 0.00 | 1.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.45** |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 55.47 | 0.00 | 0.00 | 2.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.67** |
| MA_CROSS_TREND_SHIFT | kept | 5 | 70.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 12 | 55.17 | 0.00 | 0.00 | 0.00 | 0.00 | 18.40 | 0.00 | 0.00 | 0.00 | **18.40** |
| MEAN_REVERT | kept | 11 | 72.17 | 0.00 | 0.00 | 0.73 | 0.00 | 2.18 | 0.00 | 0.00 | 0.00 | **2.91** |
| MOVER_AVWAP_SCALP | filtered | 218 | 52.22 | 0.91 | 0.00 | 2.19 | 0.00 | 2.74 | 0.05 | 0.00 | 1.37 | **7.26** |
| MOVER_AVWAP_SCALP | kept | 240 | 78.11 | 0.00 | 0.00 | 0.69 | 0.00 | 0.55 | 0.03 | 0.00 | 0.03 | **1.30** |
| MOVER_TREND_PULLBACK | filtered | 1780 | 54.04 | 0.00 | 0.00 | 1.80 | 0.00 | 0.22 | 0.07 | 0.00 | 0.13 | **2.22** |
| MOVER_TREND_PULLBACK | kept | 2019 | 75.60 | 0.00 | 0.00 | 0.56 | 0.00 | 0.17 | 0.03 | 0.00 | 0.00 | **0.76** |
| QUIET_COMPRESSION_BREAK | filtered | 61 | 55.77 | 0.00 | 0.00 | 0.00 | 0.00 | 1.07 | 0.00 | 0.00 | 0.89 | **1.96** |
| QUIET_COMPRESSION_BREAK | kept | 122 | 77.34 | 0.00 | 0.00 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | **0.14** |
| SR_FLIP_RETEST | filtered | 31 | 51.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 16 | 64.88 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 78 | 53.43 | 0.00 | 0.00 | 6.34 | 0.00 | 1.88 | 0.00 | 0.00 | 0.00 | **8.22** |
| TREND_PULLBACK_EMA | kept | 70 | 75.68 | 0.00 | 0.00 | 0.91 | 0.00 | 0.96 | 0.00 | 0.00 | 0.00 | **1.87** |
| VOLUME_SURGE_BREAKOUT | filtered | 27 | 58.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 17 | 78.41 | 0.00 | 0.00 | 0.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.47** |

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
- Outcomes recorded: **165063 held of 652316 seen** across 21 strategies; 3718 cells past the sample floor; **1946 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 46377 | 691/45686/0 | 43% | -0.18 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | LONDON/DISTRIBUTION/NORMAL/BTC_RISING (-1.29R) |
| MOVER_AVWAP_SCALP | 21356 | 200/21156/0 | 43% | -0.20 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 12272 | 139/12133/0 | 48% | -0.06 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 12168 | 145/12023/0 | 39% | -0.26 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (+1.77R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| TREND_PULLBACK_EMA | 10435 | 45/10390/0 | 40% | -0.23 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 9031 | 109/8922/0 | 35% | -0.47 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 7688 | 0/0/7688 | 42% | -0.12 | NY/RANGE/NORMAL/BTC_NEUTRAL (+0.77R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.17R) |
| SHADOW_RANGE_FADE | 7210 | 0/0/7210 | 36% | -0.13 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.39R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.25R) |
| QUIET_COMPRESSION_BREAK | 7114 | 412/6702/0 | 50% | -0.12 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_FUNDING_FADE | 6493 | 0/0/6493 | 34% | -0.41 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.04R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| MEAN_REVERT | 4783 | 58/4725/0 | 37% | -0.34 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| SR_FLIP_RETEST | 4706 | 18/4688/0 | 46% | -0.24 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+2.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| FUNDING_EXTREME_SIGNAL | 3639 | 2/3637/0 | 31% | -0.47 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3420 | 0/3420/0 | 31% | -0.35 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| RANGE_FADE | 1896 | 6/1890/0 | 33% | -0.52 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+2.15R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1511 | 0/0/1511 | 53% | -0.07 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 432 | 0/432/0 | 33% | -0.48 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 154 | 30/124/0 | 42% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 18 | 2/16/0 | 56% | +0.19 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL` -1.64R (n=18, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 294 | 27% / -0.58R | 294 | 54% / -0.09R | +0.49 | **ATR** |
| LIQUIDATION_REVERSAL | 26 | 27% / -0.60R | 26 | 54% / -0.22R | +0.38 | **ATR** |
| TREND_PULLBACK_EMA | 920 | 39% / -0.34R | 920 | 51% / -0.07R | +0.27 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1411 | 43% / -0.36R | 1411 | 56% / -0.12R | +0.24 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 177 | 34% / -0.23R | 177 | 45% / -0.09R | +0.14 | **ATR** |
| RANGE_FADE | 97 | 32% / -0.36R | 97 | 39% / -0.22R | +0.14 | **ATR** |
| MOVER_AVWAP_SCALP | 2136 | 43% / -0.19R | 2136 | 50% / -0.06R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 442 | 43% / -0.30R | 442 | 47% / -0.17R | +0.13 | **ATR** |
| MA_CROSS_TREND_SHIFT | 48 | 40% / -0.18R | 48 | 44% / -0.08R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1226 | 40% / -0.23R | 1226 | 43% / -0.13R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 8267 | 50% / -0.11R | 8267 | 55% / -0.01R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1383 | 48% / -0.10R | 1383 | 54% / -0.04R | +0.06 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1248 | 47% / -0.13R | 1248 | 47% / -0.14R | -0.01 | **FIXED** |
| MEAN_REVERT | 343 | 45% / -0.21R | 343 | 44% / -0.21R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 8 | 50% / -0.24R | 8 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11153 | 28% | -0.22R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2136 | 47% | -0.06R | 227 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 111 | 47% | -0.09R | 65 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1216 | 34% / -0.22R | +0.85 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1603 | 39% / -0.16R | +0.85 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2608 | 35% / -0.15R | +0.69 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10165 | 37% / -0.13R | +0.40 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1585 | 38% / -0.10R | +0.18 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1212 | 37% / -0.13R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1025 | 33% / -0.23R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 259 | 31% / -0.39R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 391 | 32% / -0.10R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 291 | 47% / -0.10R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 73 | 40% / -0.08R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 403 | 33% / -0.30R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 74 | 30% / -0.40R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 32 | 44% / -0.24R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 16 | 44% / +0.50R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **5** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×366]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 483/6) (sustained 483 cycles)
- **ALERT** `dark_resolution` — 1 of 133 open dark rows are not being advanced (worst: BABYUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 191/120) (sustained 191 cycles)
- **ALERT** `edge_reconciliation` — LIQUIDITY_SWEEP_REVERSAL realized−counterfactual=+0.52R (bound 0.3) (streak 540/6) (sustained 540 cycles)
- **ALERT** `tuned_variants` — 577 non-stamps — atr_arm_uncomputable=577 (seen=12518 stamped=1456 skipped=10485) (streak 540/6) (sustained 540 cycles)
- **ALERT** `auto_dispatch` — 138 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=138) (streak 533/3) (sustained 533 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 46 fed / 0 quiet / 0 never delivered of 46 subscribed; 139376299 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 18 arms current, none stalled; covering 2126/2126 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 35 arms current, none stalled; covering 1162/1162 signals (100%) | 0 |
| auto_dispatch | violating | 138 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=138) (streak 533/3) | 533 |
| binance_ip_weight | ok | peak 190/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 80121.80 | 0 |
| candle_coverage | ok | 92/92 symbols with ≥20 15m candles, 92/92 updated within 45m [fresh=92; 79 Tier-1 futures + 13 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 5714 dup bars, 0 undedupable; ws 0 out-of-order, 588 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +43 / upstream +20 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1802/1821 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 1 of 133 open dark rows are not being advanced (worst: BABYUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 191/120) | 191 |
| dark_sar_arms | ok | no open arms; covering 1795/1814 signals (99%) | 0 |
| depth_feed | ok | 46/46 books fresh (stale 0, never 0, thin 0); 36103332 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | LIQUIDITY_SWEEP_REVERSAL realized−counterfactual=+0.52R (bound 0.3) (streak 540/6) | 540 |
| emission_controller | ok | last cycle 424s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×366]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 483/6) | 483 |
| entry_quality_effective | ok | 12683 evaluated, 3730 suppressed, 3727 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,349 reads/day of 50,000 [engine 1,317, signing 32]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 5520 sealed bars over 46 symbols; 1680 incomplete, 10 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +11 / upstream +318 | 0 |
| indicator_cache_key | ok | 200324 frozen value(s) avoided; 622838 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.34R over n=4725 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +33 / upstream +318 | 0 |
| mover_admission_metadata | ok | 936 symbols known, 229 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 13 held, 13 with scan counts, 13 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 3 locked / 3 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2098 rows held, 3182756 evicted (sampled: execution:trigger_not_confirmed 285/1123921, execution:overextended 285/1000014, setup_compat:regime_STRONG_TREND 284/536739) | 0 |
| price_action_lane | ok | 822070 evaluated, 1395 emitted; layer1 1395 stamped / 0 blind; cooldown=97962, delta_opposed=94905, no_footprint=299691, no_opposing_target=1148, no_sweep=237462, rr_below_floor=89507 | 0 |
| promoted_pair_integrity | ok | 13/13 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.52R over n=1890 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | violating | upstream +318 but output +0 (streak 2/72) | 2 |
| sar_alignment_crosscheck | ok | 790/31910 disagreed (2.5%) | 0 |
| sar_exit_shadow | ok | output +10 / upstream +318 | 0 |
| sar_hold_arm | ok | 1873 held arms settled, 127 unscored, 34 still walking (29 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 2/36 unfetchable (6%); top cause: located bar does not contain the stamp; symbols: BMTUSDT, NILUSDT | 0 |
| sar_live_arms | ok | 34 arms current, none stalled; covering 1160/1160 signals (100%) | 0 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 10 resolved, 24 still mid-window | 0 |
| scan_cycle | ok | last 77.46s, worst 275.21s over 13719 lifetime cycles; lifetime 703 over 60s, 187 over 120s; recent 3/1 warn/kill breaches in 20/20 cycles; heartbeat age 4.36s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 352698 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 16s ago (12.4s to run, worst 199.81s), 2200 overrun(s) of 10904 cycles, TTL 900s; slowest trail_governor=6.19s, data_intake=1.58s, pair_context=0.92s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=7535, gate reads=0, withheld=7535) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +25 / upstream +318 | 0 |
| structural_snap | ok | 6000/6000 measured, 41 blind, 0 levels moved (refusals: redetect_cooldown=3496) | 0 |
| structural_veto_lane | ok | 4799 stamped; 0 with no readable level book, 33 with clear air ahead, 3853 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +318 / upstream +20 | 0 |
| tuned_variants | violating | 577 non-stamps — atr_arm_uncomputable=577 (seen=12518 stamped=1456 skipped=10485) (streak 540/6) | 540 |
| unlock_shorts | ok | 13 open, 46 scheduled, calendar 14.0h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 110 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1174250`
- `Path funnel` emissions: `30`
- `Regime distribution` emissions: `30`
- `QUIET_SCALP_BLOCK` events: `93`
- `confidence_gate` events: `5131`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **26**
- Total REST-fallback activations: **8**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 10 | 12890 | 19931 | 20653 | 0 |
| futures_aggtrade | 8 | 9765 | 18145 | 23178 | 0 |
| futures_depth | 1 | 2242 | 2242 | 2242 | 0 |
| futures_liq | 6 | 5734 | 13277 | 71485 | 0 |
| futures_mover | 1 | 14597 | 14597 | 14597 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 8 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=186623] state[populated=186623] buckets[many=186623] sources[none] quality[none]
- funding_rate: presence[absent=19888, present=166735] state[empty=19888, populated=166735] buckets[few=166735, none=19888] sources[none] quality[none]
- liquidation_clusters: presence[absent=110805, present=75818] state[empty=110805, populated=75818] buckets[few=63005, none=110805, some=12813] sources[none] quality[none]
- oi_snapshot: presence[absent=19888, present=166735] state[empty=19888, populated=166735] buckets[few=385, many=165434, none=19888, some=916] sources[none] quality[none]
- order_book: presence[absent=67252, present=119371] state[populated=119371, unavailable=67252] buckets[few=119371, none=67252] sources[book_ticker=119371, unavailable=67252] quality[none=67252, top_of_book_only=119371]
- orderblocks: presence[absent=186623] state[empty=186623] buckets[none=186623] sources[measured_dark=186623] quality[none]
- recent_ticks: presence[present=186623] state[populated=186623] buckets[many=186623] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.443378925323486` sec
- Median create→first breach: `4707.018905043602` sec
- Median create→terminal: `4707.018963456154` sec
- Median first breach→terminal: `6.0558319091796875e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 1, "pct": 1.5}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 2, "pct": 3.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.7005264477312406 | 0.799999999999993 | 0.8756580596640584 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 6 | 6 | 1.1160177104071654 | 1.318790689343811 | 0.8697126341289713 | 0 | 6 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 2.5537263994700323 | 3.0 | 0.8512421331566774 | 0 | 1 |
| MEAN_REVERT | 4 | 4 | 1.0153961569298529 | 1.2216403100018944 | 0.8491745608015493 | 0 | 3 |
| MOVER_AVWAP_SCALP | 6 | 6 | 1.7368922639910784 | 2.2663043112266514 | 0.8157973084621868 | 1 | 5 |
| MOVER_TREND_PULLBACK | 32 | 32 | 3.766572668297157 | 3.0 | 1.255524222765719 | 23 | 9 |
| QUIET_COMPRESSION_BREAK | 14 | 14 | 1.0427236998418485 | 1.109404996637089 | 0.9073404282235259 | 0 | 9 |
| TREND_PULLBACK_EMA | 2 | 2 | 1.8610131336401008 | 2.7186794622449986 | 0.6683474109656315 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.0508 | 12365.48402094841 | 12366.31676697731 |
| FAILED_AUCTION_RECLAIM | 6 | 6 | 33.3 | 33.3 | 33.3 | 0.0 | 0.1765 | 4385.2330930233 | 4386.307240128517 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.5537 | 978.5430948734283 | 978.5431559085846 |
| MEAN_REVERT | 4 | 4 | 25.0 | 75.0 | 25.0 | 0.0 | 0.0503 | 3755.0913475751877 | 3755.0914155244827 |
| MOVER_AVWAP_SCALP | 6 | 6 | 0.0 | 33.3 | 0.0 | 0.0 | -0.574 | 7869.285436987877 | 7869.285503029823 |
| MOVER_TREND_PULLBACK | 32 | 32 | 28.1 | 53.1 | 28.1 | 0.0 | -0.928 | 3248.337758898735 | 3248.3378183841705 |
| QUIET_COMPRESSION_BREAK | 14 | 14 | 35.7 | 28.6 | 35.7 | 0.0 | 0.4269 | 23406.90106356144 | 23406.901104092598 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -1.2371 | 1722.9978370666504 | 1722.9979209899902 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 522 | 9 | 272 | 0.0 | 0.0 | None | None | 250 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1159 | 38 | 868 | 0.0 | 50.0 | 1722.9978370666504 | 1722.9979209899902 | 291 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-24`
- Gating Δ: `2105`
- No-generation Δ: `-74944`
- Fast failures Δ: `0`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 1.3582, "current_avg_pnl": 1.0508, "current_win_rate": 100.0, "previous_avg_pnl": -0.3074, "previous_win_rate": 25.0, "win_rate_delta": 75.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.3772, "current_avg_pnl": 0.1765, "current_win_rate": 33.3, "previous_avg_pnl": 0.5537, "previous_win_rate": 50.0, "win_rate_delta": -16.7}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -6.1005, "current_avg_pnl": -2.5537, "current_win_rate": 0.0, "previous_avg_pnl": 3.5468, "previous_win_rate": 75.0, "win_rate_delta": -75.0}, "MEAN_REVERT": {"avg_pnl_delta": 0.0503, "current_avg_pnl": 0.0503, "current_win_rate": 25.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 25.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.0792, "current_avg_pnl": -0.574, "current_win_rate": 0.0, "previous_avg_pnl": 0.5052, "previous_win_rate": 25.0, "win_rate_delta": -25.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.0446, "current_avg_pnl": -0.928, "current_win_rate": 28.1, "previous_avg_pnl": 0.1166, "previous_win_rate": 29.2, "win_rate_delta": -1.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0317, "current_avg_pnl": 0.4269, "current_win_rate": 35.7, "previous_avg_pnl": 0.3952, "previous_win_rate": 25.0, "win_rate_delta": 10.7}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": -18, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 14, "geometry_changed_delta": 0, "geometry_preserved_delta": 20, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 1723.0, "median_terminal_delta_sec": 1723.0, "sl_rate_delta": 50.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
