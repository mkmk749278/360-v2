# Runtime Truth Report

## Executive summary
- Overall health/freshness: **halted_by_breaker**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, MOVER_AVWAP_SCALP
- Top promising signals/paths: LIQUIDITY_SWEEP_REVERSAL
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `755` sec
- ⛔ **HALTED BY LOSS CIRCUIT BREAKER** — reason: 3 consecutive SL hits (max=3); cooldown remaining: 3.8s. This is a deliberate protective pause (not a crash); the stale heartbeat and zero-signal window are expected while halted.

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 102 | 102 | 101 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 13113 | 13113 | 12339 | 7 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 84577 | 84577 | 34 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 76749 | 76751 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 76406 | 73193 | 3545 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 76786 | 75486 | 1417 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 82772 | 82520 | 283 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 73559 | 73577 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 76909 | 76965 | 4 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 76974 | 75095 | 2500 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 88483 | 92809 | 1260 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 84615 | 77638 | 10784 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 82177 | 82179 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 76755 | 76777 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 76378 | 76256 | 145 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 77602 | 76011 | 2101 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 75752 | 75905 | 432 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 67000 | 62581 | 4754 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 67346 | 66705 | 710 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 84537 | 84522 | 53 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 73579 | 73584 | 22 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 5723 | 5723 | 5418 | 6 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 907 | 907 | 573 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 24813 | 24813 | 24410 | 21 | active-healthy (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 11 | 11 | 9 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 6621 | 6621 | 5820 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3499 | 3499 | 2874 | 29 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 30797 | 30797 | 24903 | 183 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 15 | 15 | 15 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 912 | 912 | 830 | 13 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 5764 | 5764 | 5317 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1606 | 1606 | 1345 | 5 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2739 | 2739 | 2503 | 19 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 131 | 131 | 100 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 982 | 982 | 525 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=84577): breakout_not_found=48010, basic_filters_failed=21047, move_not_fresh=9750, breakout_stale=4086, retest_proximity_failed=1403, volume_spike_missing=269, missing_fvg_or_orderblock=8, move_exhausted=4
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=76751): cls_disabled_merged_into_lsr=76751
- **EVAL::DIVERGENCE_CONTINUATION** (total=73193): cvd_divergence_failed=31561, h1_trend_not_aligned=18760, basic_filters_failed=16304, ema_alignment_reject=5561, retest_proximity_failed=819, missing_fvg_or_orderblock=188
- **EVAL::FAILED_AUCTION_RECLAIM** (total=75486): auction_not_detected=49111, basic_filters_failed=15912, reclaim_hold_failed=4677, tail_too_small=3750, regime_blocked=2035, rsi_reject=1
- **EVAL::FUNDING_EXTREME** (total=82520): funding_not_extreme=58364, basic_filters_failed=17299, missing_funding_rate=4380, ema_alignment_reject=1542, rsi_reject=512, momentum_reject=204, cvd_divergence_failed=181, missing_fvg_or_orderblock=38
- **EVAL::LIQUIDATION_REVERSAL** (total=73577): cascade_threshold_not_met=54325, basic_filters_failed=18340, cvd_divergence_failed=463, rsi_reject=408, volume_spike_missing=35, missing_fvg_or_orderblock=6
- **EVAL::MA_CROSS_TREND_SHIFT** (total=76965): no_ma_cross=58657, basic_filters_failed=16325, ma_cross_cooldown=1082, ma_cross_htf_misaligned=901
- **EVAL::MEAN_REVERT** (total=75095): no_extension=63035, basic_filters_failed=12060
- **EVAL::MOVER_AVWAP_SCALP** (total=92809): no_avwap_tag=30831, no_mover_leg=28658, basic_filters_failed=21276, avwap_slope_against=6633, avwap_reclaim_no_volume=3165, no_avwap_reclaim=2173, anchor_too_recent=73
- **EVAL::MOVER_TREND_PULLBACK** (total=77638): mover_run_too_small=40421, basic_filters_failed=21168, no_reclaim=13136, no_pullback_tag=2913
- **EVAL::OPENING_RANGE_BREAKOUT** (total=82179): feature_disabled=82179
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=76777): regime_blocked=53233, breakout_not_found=16987, basic_filters_failed=4581, adx_reject=1925, ema_alignment_reject=51
- **EVAL::QUIET_COMPRESSION_BREAK** (total=76256): compression_not_detected=30359, regime_blocked=25473, basic_filters_failed=11321, breakout_not_detected=8397, volume_confirmation_failed=676, rsi_reject=26, missing_fvg_or_orderblock=4
- **EVAL::RANGE_FADE** (total=76011): no_range_edge=63943, basic_filters_failed=12068
- **EVAL::SR_FLIP_RETEST** (total=75905): flip_close_not_confirmed=48343, basic_filters_failed=15886, long_break_volume_thin=3353, retest_out_of_zone=2961, regime_blocked=2030, h1_break_not_confirmed=1647, reclaim_hold_failed=1103, long_acceptance_not_held=181, wick_quality_failed=170, ema_alignment_reject=119, whipsaw_flip=101, missing_fvg_or_orderblock=11
- **EVAL::STANDARD** (total=62581): momentum_reject=18953, adx_reject=15228, basic_filters_failed=9010, sweeps_not_detected=7235, macd_reject=6970, ema_alignment_reject=3918, htf_poi_unanchored=1040, invalid_sl_geometry=120, rsi_reject=107
- **EVAL::TREND_PULLBACK** (total=66705): h1_trend_not_aligned=22026, ema_alignment_reject=12485, basic_filters_failed=8740, h1_pullback_not_confirmed=5887, no_ema_reclaim_close=5269, ema_not_tested_prev=5211, body_conviction_fail=2882, rsi_reject=2188, prev_already_below_emas=634, prev_already_above_emas=468, no_prev_low_break=359, momentum_flat=228, no_prev_high_break=200, ema21_not_tagged=78, missing_fvg_or_orderblock=36, momentum_reject=14
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=84522): breakout_not_found=49522, basic_filters_failed=21046, move_not_fresh=8588, breakout_stale=3628, retest_proximity_failed=1412, volume_spike_missing=300, move_exhausted=16, missing_fvg_or_orderblock=10
- **EVAL::WHALE_MOMENTUM** (total=73584): momentum_reject=59129, recent_ticks_insufficient=11191, basic_filters_failed=3264

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=1): execution:overextended=1
- **DIVERGENCE_CONTINUATION** (total=287): setup_compat:regime_VOLATILE_UNSUITABLE=275, setup_compat:regime_BREAKOUT_EXPANSION=12
- **FAILED_AUCTION_RECLAIM** (total=1048): execution:overextended=501, setup_compat:regime_STRONG_TREND=434, context_floor=107, setup_compat:regime_VOLATILE_UNSUITABLE=6
- **FUNDING_EXTREME_SIGNAL** (total=726): execution:trigger_not_confirmed=726
- **LIQUIDATION_REVERSAL** (total=3): execution:trigger_not_confirmed=3
- **LIQUIDITY_SWEEP_REVERSAL** (total=5612): execution:overextended=2066, execution:trigger_not_confirmed=2035, setup_compat:regime_STRONG_TREND=1511
- **MA_CROSS_TREND_SHIFT** (total=10): setup_compat:regime_DIRTY_RANGE=5, setup_compat:regime_CLEAN_RANGE=3, execution:overextended=2
- **MEAN_REVERT** (total=3244): setup_compat:regime_STRONG_TREND=1379, setup_compat:regime_WEAK_TREND=1302, execution:overextended=563
- **MOVER_AVWAP_SCALP** (total=1772): execution:overextended=1515, execution:trigger_not_confirmed=137, entry_quality=120
- **MOVER_TREND_PULLBACK** (total=13343): execution:trigger_not_confirmed=7424, execution:overextended=5076, entry_quality=843
- **QUIET_COMPRESSION_BREAK** (total=18): execution:trigger_not_confirmed=18
- **RANGE_FADE** (total=3644): setup_compat:regime_STRONG_TREND=1511, setup_compat:regime_WEAK_TREND=1356, execution:overextended=420, setup_compat:regime_VOLATILE_UNSUITABLE=336, context_edge=21
- **SR_FLIP_RETEST** (total=1): setup_compat:regime_VOLATILE_UNSUITABLE=1
- **TREND_PULLBACK_EMA** (total=2491): setup_compat:regime_CLEAN_RANGE=1616, setup_compat:regime_DIRTY_RANGE=820, entry_quality=30, setup_compat:regime_VOLATILE_UNSUITABLE=25
- **VOLUME_SURGE_BREAKOUT** (total=56): execution:overextended=40, context_floor=16
- **WHALE_MOMENTUM** (total=980): execution:trigger_not_confirmed=980

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 201917 | 43.4% |
| QUIET | 97891 | 21.1% |
| TRENDING_DOWN | 81124 | 17.5% |
| TRENDING_UP | 62712 | 13.5% |
| VOLATILE | 21191 | 4.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **82**
- Average confidence gap to threshold: **11.64** (samples=82) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: 1000PEPEUSDT=10, BCHUSDT=8, DOTUSDT=8, PENGUUSDT=7, SOLUSDT=7, TRXUSDT=6, HYPEUSDT=6, SUIUSDT=6, ADAUSDT=5, LTCUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 8 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 72 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 20 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 50 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 20 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 6 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 15 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 12 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 55 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 163 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 13 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 211 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 514 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 8 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2043 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 41 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 30 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 14 |
| SR_FLIP_RETEST | filtered | min_confidence | 75 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 27 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 99 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 9 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 34 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 15 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 3 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 8 | 66.71 | 65.00 | -1.71 | 21.91 | 15.38 | 20.00 | 4.06 | 10.22 |
| DIVERGENCE_CONTINUATION | filtered | 72 | 52.63 | 63.14 | 10.51 | 21.20 | 19.80 | 18.72 | 0.31 | 16.62 |
| DIVERGENCE_CONTINUATION | kept | 20 | 70.09 | 65.00 | -5.09 | 20.31 | 19.70 | 19.05 | 0.85 | -0.15 |
| FAILED_AUCTION_RECLAIM | filtered | 70 | 53.44 | 64.89 | 11.45 | 20.65 | 18.88 | 20.00 | 2.81 | 6.65 |
| FAILED_AUCTION_RECLAIM | kept | 6 | 67.23 | 65.00 | -2.23 | 21.92 | 18.87 | 20.00 | 2.83 | 3.45 |
| FUNDING_EXTREME_SIGNAL | filtered | 15 | 42.60 | 61.00 | 18.40 | 20.63 | 13.93 | 17.00 | 3.00 | 12.13 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 83.30 | 65.00 | -18.30 | 18.80 | 14.00 | 17.00 | 5.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 15 | 52.98 | 64.20 | 11.22 | 20.65 | 19.18 | 17.00 | 2.00 | 19.02 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 55 | 70.25 | 65.00 | -5.25 | 20.73 | 19.44 | 17.05 | 1.05 | 0.13 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 74.90 | 65.00 | -9.90 | 20.70 | 19.70 | 15.80 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 176 | 57.76 | 60.94 | 3.18 | 20.63 | 15.27 | 15.80 | 3.98 | 11.21 |
| MOVER_AVWAP_SCALP | kept | 211 | 82.47 | 65.00 | -17.47 | 19.61 | 15.60 | 15.80 | 4.17 | 0.74 |
| MOVER_TREND_PULLBACK | filtered | 522 | 57.19 | 64.67 | 7.48 | 20.09 | 18.82 | 15.80 | 3.79 | 17.13 |
| MOVER_TREND_PULLBACK | kept | 2043 | 75.76 | 65.00 | -10.76 | 20.46 | 18.44 | 15.80 | 4.26 | 1.28 |
| QUIET_COMPRESSION_BREAK | filtered | 71 | 53.11 | 64.27 | 11.16 | 21.16 | 19.06 | 20.00 | 0.00 | 4.60 |
| QUIET_COMPRESSION_BREAK | kept | 14 | 73.46 | 65.00 | -8.46 | 21.16 | 19.17 | 20.00 | 0.00 | 1.54 |
| SR_FLIP_RETEST | filtered | 75 | 55.65 | 64.20 | 8.55 | 21.14 | 20.00 | 16.19 | 1.61 | 12.95 |
| SR_FLIP_RETEST | kept | 27 | 69.34 | 65.00 | -4.34 | 20.76 | 20.00 | 15.22 | 2.70 | 1.78 |
| TREND_PULLBACK_EMA | filtered | 108 | 60.18 | 64.67 | 4.49 | 21.49 | 19.79 | 18.52 | 4.60 | 11.40 |
| TREND_PULLBACK_EMA | kept | 34 | 75.71 | 65.00 | -10.71 | 20.99 | 19.85 | 17.50 | 5.07 | 4.92 |
| VOLUME_SURGE_BREAKOUT | kept | 15 | 64.27 | 65.00 | 0.73 | 20.05 | 19.90 | 20.00 | 4.50 | 10.20 |
| WHALE_MOMENTUM | filtered | 3 | 31.10 | 65.00 | 33.90 | 23.20 | 14.00 | 17.00 | 0.00 | 24.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 8 | 66.71 | 17.00 | 14.50 | 12.38 | 14.00 | 5.00 | 10.00 | 4.06 |
| DIVERGENCE_CONTINUATION | filtered | 72 | 52.63 | 24.89 | 13.97 | 4.12 | 12.74 | 5.00 | 8.22 | 0.31 |
| DIVERGENCE_CONTINUATION | kept | 20 | 70.09 | 24.60 | 16.00 | 4.20 | 11.55 | 4.88 | 9.07 | 0.85 |
| FAILED_AUCTION_RECLAIM | filtered | 70 | 53.44 | 23.26 | 15.94 | 5.31 | 13.77 | 5.92 | 4.43 | 2.81 |
| FAILED_AUCTION_RECLAIM | kept | 6 | 67.23 | 22.33 | 16.00 | 8.00 | 12.83 | 6.17 | 5.00 | 2.83 |
| FUNDING_EXTREME_SIGNAL | filtered | 15 | 42.60 | 25.00 | 8.00 | 10.00 | 13.80 | 9.17 | 0.77 | 3.00 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 83.30 | 25.00 | 20.00 | 6.00 | 9.00 | 9.00 | 9.30 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 15 | 52.98 | 20.33 | 14.00 | 10.80 | 11.60 | 5.47 | 7.80 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 55 | 70.25 | 23.58 | 14.51 | 5.40 | 13.13 | 6.56 | 6.14 | 1.05 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 74.90 | 21.00 | 14.00 | 12.00 | 14.00 | 4.25 | 9.65 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 176 | 57.76 | 18.06 | 18.07 | 10.93 | 13.36 | 5.26 | 6.31 | 3.98 |
| MOVER_AVWAP_SCALP | kept | 211 | 82.47 | 18.73 | 18.21 | 12.87 | 13.78 | 7.73 | 8.08 | 4.17 |
| MOVER_TREND_PULLBACK | filtered | 522 | 57.19 | 19.02 | 18.00 | 7.82 | 13.07 | 6.68 | 9.17 | 3.79 |
| MOVER_TREND_PULLBACK | kept | 2043 | 75.76 | 18.94 | 18.02 | 7.62 | 12.77 | 6.56 | 9.02 | 4.26 |
| QUIET_COMPRESSION_BREAK | filtered | 71 | 53.11 | 19.59 | 15.69 | 11.92 | 14.04 | 7.46 | 3.48 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 14 | 73.46 | 19.29 | 17.71 | 10.07 | 13.86 | 7.25 | 8.31 | 0.00 |
| SR_FLIP_RETEST | filtered | 75 | 55.65 | 19.35 | 18.00 | 3.60 | 13.00 | 5.00 | 8.03 | 1.61 |
| SR_FLIP_RETEST | kept | 27 | 69.34 | 24.70 | 13.56 | 5.67 | 14.00 | 5.37 | 6.45 | 2.70 |
| TREND_PULLBACK_EMA | filtered | 108 | 60.18 | 18.00 | 18.00 | 7.67 | 14.56 | 6.64 | 8.68 | 4.60 |
| TREND_PULLBACK_EMA | kept | 34 | 75.71 | 20.79 | 18.00 | 7.50 | 14.26 | 7.10 | 9.31 | 5.07 |
| VOLUME_SURGE_BREAKOUT | kept | 15 | 64.27 | 19.67 | 14.00 | 12.00 | 10.00 | 5.00 | 9.30 | 4.50 |
| WHALE_MOMENTUM | filtered | 3 | 31.10 | 23.00 | 8.00 | 12.00 | 17.00 | 10.00 | 0.70 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 8 | 66.71 | 0.00 | 0.00 | 7.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **7.60** |
| DIVERGENCE_CONTINUATION | filtered | 72 | 52.63 | 0.00 | 0.00 | 2.13 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | **2.46** |
| DIVERGENCE_CONTINUATION | kept | 20 | 70.09 | 0.00 | 0.00 | 0.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.24** |
| FAILED_AUCTION_RECLAIM | filtered | 70 | 53.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.31 | 0.00 | 0.00 | 0.00 | **0.31** |
| FAILED_AUCTION_RECLAIM | kept | 6 | 67.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 15 | 42.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 83.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 15 | 52.98 | 0.00 | 0.00 | 1.60 | 0.00 | 17.28 | 0.00 | 0.00 | 0.00 | **18.88** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 55 | 70.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 74.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 176 | 57.76 | 0.00 | 0.00 | 1.41 | 0.00 | 3.65 | 0.00 | 0.00 | 3.09 | **8.15** |
| MOVER_AVWAP_SCALP | kept | 211 | 82.47 | 0.00 | 0.00 | 0.14 | 0.00 | 0.07 | 0.00 | 0.00 | 0.09 | **0.30** |
| MOVER_TREND_PULLBACK | filtered | 522 | 57.19 | 0.00 | 0.00 | 3.14 | 0.00 | 0.46 | 0.00 | 0.00 | 0.00 | **3.60** |
| MOVER_TREND_PULLBACK | kept | 2043 | 75.76 | 0.00 | 0.00 | 0.27 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.29** |
| QUIET_COMPRESSION_BREAK | filtered | 71 | 53.11 | 0.00 | 0.00 | 0.20 | 0.00 | 1.24 | 0.00 | 0.00 | 2.86 | **4.30** |
| QUIET_COMPRESSION_BREAK | kept | 14 | 73.46 | 0.00 | 0.00 | 0.00 | 0.00 | 1.54 | 0.00 | 0.00 | 0.00 | **1.54** |
| SR_FLIP_RETEST | filtered | 75 | 55.65 | 0.00 | 0.00 | 3.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.24 | **3.63** |
| SR_FLIP_RETEST | kept | 27 | 69.34 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 108 | 60.18 | 0.00 | 0.00 | 1.42 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.42** |
| TREND_PULLBACK_EMA | kept | 34 | 75.71 | 0.00 | 0.00 | 1.69 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.69** |
| VOLUME_SURGE_BREAKOUT | kept | 15 | 64.27 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.20** |
| WHALE_MOMENTUM | filtered | 3 | 31.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **81560 held of 192950 seen** across 21 strategies; 1825 cells past the sample floor; **786 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 32335 | 388/31947/0 | 45% | -0.14 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.17R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.13R) |
| MOVER_AVWAP_SCALP | 10087 | 107/9980/0 | 40% | -0.26 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 6368 | 60/6308/0 | 43% | -0.17 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 4451 | 28/4423/0 | 54% | +0.06 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 4360 | 0/0/4360 | 44% | -0.06 | ASIA/RANGE/NORMAL/BTC_RISING (+0.23R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.09R) |
| TREND_PULLBACK_EMA | 3993 | 12/3981/0 | 47% | -0.14 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.18R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.21R) |
| QUIET_COMPRESSION_BREAK | 3846 | 152/3694/0 | 46% | -0.11 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+0.84R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_RANGE_FADE | 3689 | 0/0/3689 | 37% | -0.09 | ASIA/MARKDOWN/NORMAL/BTC_FALLING (+0.36R) | OFF_HOURS/RANGE/NORMAL/BTC_RISING (-0.91R) |
| SHADOW_FUNDING_FADE | 3061 | 0/0/3061 | 37% | -0.36 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-1.01R) |
| WHALE_MOMENTUM | 2070 | 2/2068/0 | 40% | -0.38 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 2000 | 26/1974/0 | 39% | -0.23 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.21R) |
| MEAN_REVERT | 1333 | 18/1315/0 | 60% | +0.12 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 968 | 2/966/0 | 31% | -0.46 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.37R) |
| VOLUME_SURGE_BREAKOUT | 956 | 0/956/0 | 48% | +0.01 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.16R) |
| SR_FLIP_RETEST | 800 | 0/800/0 | 45% | -0.26 | NY/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.77R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 485 | 0/0/485 | 55% | -0.01 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | ASIA/MARKUP/CASCADE/BTC_NEUTRAL (-0.33R) |
| RANGE_FADE | 300 | 0/300/0 | 59% | +0.19 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| BREAKDOWN_SHORT | 210 | 18/192/0 | 20% | -0.60 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDATION_REVERSAL | 196 | 0/196/0 | 11% | -1.00 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 48 | 6/42/0 | 33% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 4 | 0/4/0 | 50% | +0.17 | — | — |

- **Strongest cells**: `DIVERGENCE_CONTINUATION @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +1.76R (n=34, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +1.66R (n=15, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ NY/RANGE/NORMAL/BTC_FALLING` +1.64R (n=19, STRONG)
- **Weakest cells**: `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING` -1.38R (n=17, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.37R (n=16, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 104 | 33% / -0.43R | 104 | 48% / -0.15R | +0.28 | **ATR** |
| TREND_PULLBACK_EMA | 339 | 48% / -0.16R | 339 | 56% / -0.03R | +0.14 | **ATR** |
| SR_FLIP_RETEST | 93 | 46% / -0.31R | 93 | 48% / -0.18R | +0.13 | **ATR** |
| RANGE_FADE | 20 | 50% / +0.20R | 20 | 50% / +0.10R | -0.11 | **FIXED** |
| MOVER_AVWAP_SCALP | 774 | 46% / -0.18R | 774 | 51% / -0.08R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 248 | 43% / -0.34R | 248 | 44% / -0.25R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 522 | 44% / -0.17R | 522 | 46% / -0.09R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 4889 | 51% / -0.09R | 4889 | 55% / -0.01R | +0.08 | **ATR** |
| MA_CROSS_TREND_SHIFT | 16 | 31% / -0.25R | 16 | 31% / -0.19R | +0.06 | **ATR** |
| BREAKDOWN_SHORT | 20 | 30% / -0.17R | 20 | 30% / -0.14R | +0.03 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 409 | 52% / -0.18R | 409 | 56% / -0.15R | +0.03 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 64 | 45% / -0.05R | 64 | 52% / -0.02R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 635 | 46% / -0.15R | 635 | 46% / -0.16R | -0.01 | **FIXED** |
| MEAN_REVERT | 107 | 58% / +0.05R | 107 | 55% / +0.04R | -0.01 | **FIXED** |
| DIVERGENCE_CONTINUATION | 471 | 54% / -0.01R | 471 | 59% / -0.01R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 13 | 31% / -0.46R | 13 | 54% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 7249 | 31% | -0.14R | 291 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 774 | 49% | -0.08R | 171 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 42 | 55% | -0.06R | 34 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 87 | 36% / -0.25R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 599 | 36% / -0.09R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 6242 | 37% / -0.11R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 936 | 36% / -0.05R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 409 | 36% / -0.09R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 527 | 41% / +0.08R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 440 | 38% / -0.03R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 404 | 45% / -0.06R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 89 | 29% / -0.42R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 118 | 31% / -0.59R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 86 | 53% / +0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 40 | 40% / -0.10R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 18 | 44% / +0.28R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 90 | 31% / -0.40R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 22 | 14% / -0.66R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 17 | 41% / -0.06R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 8 | 38% / -0.01R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 55 · alerting: **10** · boot grace active: False
- **ALERT** `sar_alignment_crosscheck` — 296/3613 disagreed (8.2%) (streak 160/6) (sustained 160 cycles)
- **ALERT** `sar_ledger_candles` — 92/107 unfetchable (86%); top cause: gap or duplicate bar in the 15m window; symbols: 1000PEPEUSDT, 4USDT, AAVEUSDT, ADAUSDT, AKEUSDT +25 more (streak 160/6) (sustained 160 cycles)
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×544]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 160/6) (sustained 160 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 22/6) (sustained 22 cycles)
- **ALERT** `edge_reconciliation` — LIQUIDITY_SWEEP_REVERSAL realized−counterfactual=+0.57R (bound 0.3) (streak 160/6) (sustained 160 cycles)
- **ALERT** `mean_revert_emission` — 4105 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.11R over n=1315, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 160/6) (sustained 160 cycles)
- **ALERT** `range_fade_emission` — 3597 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=300, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 156/6) (sustained 156 cycles)
- **ALERT** `tuned_variants` — 74 non-stamps — atr_arm_uncomputable=74 (seen=1338 stamped=178 skipped=1086) (streak 144/6) (sustained 144 cycles)
- **ALERT** `auto_dispatch` — 35 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=72) (streak 160/3) (sustained 160 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 160/3) (sustained 160 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 13356921 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 160/3) | 160 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 50 arms current, none stalled; covering 767/767 signals (100%) | 0 |
| auto_dispatch | violating | 35 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=72) (streak 160/3) | 160 |
| btc_reference | ok | BTC ref 79136.00 | 0 |
| candle_coverage | ok | 82/82 symbols with ≥20 15m candles, 82/82 updated within 45m [fresh=82; 72 Tier-1 futures + 10 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1203 dup bars, 0 undedupable; ws 0 out-of-order, 62 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | violating | upstream +50 but output +0 (streak 2/72) | 2 |
| dark_atr_trail_arms | ok | no open arms; covering 1179/1196 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 9 of 72 open dark rows are not being advanced (worst: ONUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 18/120) | 18 |
| dark_sar_arms | ok | no open arms; covering 1174/1191 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 4184649 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | LIQUIDITY_SWEEP_REVERSAL realized−counterfactual=+0.57R (bound 0.3) (streak 160/6) | 160 |
| emission_controller | ok | last cycle 989s ago; live_overrides=12 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×544]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 160/6) | 160 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 22/6) | 22 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +0 / upstream +0 | 0 |
| indicator_cache_key | ok | 32418 frozen value(s) avoided; 94280 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 4105 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.11R over n=1315, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 160/6) | 160 |
| mean_revert_path | ok | output +0 / upstream +0 | 0 |
| mover_admission_metadata | ok | 897 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 10 held, 10 with scan counts, 9 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2989 rows held, 1199129 evicted (sampled: execution:trigger_not_confirmed 400/433619, execution:overextended 400/409978, setup_compat:regime_STRONG_TREND 400/173389) | 0 |
| price_action_lane | ok | 314192 evaluated, 365 emitted; layer1 365 stamped / 0 blind; cooldown=41833, delta_opposed=30640, no_footprint=113088, no_sweep=101122, rr_below_floor=27144 | 0 |
| promoted_pair_integrity | ok | 10/10 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 3597 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=300, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 156/6) | 156 |
| range_fade_path | ok | output +0 / upstream +0 | 0 |
| sar_alignment_crosscheck | violating | 296/3613 disagreed (8.2%) (streak 160/6) | 160 |
| sar_exit_shadow | ok | output +0 / upstream +0 | 0 |
| sar_hold_arm | ok | 1316 held arms settled, 186 unscored, 50 still walking (46 awaiting the second arm) | 0 |
| sar_ledger_candles | violating | 92/107 unfetchable (86%); top cause: gap or duplicate bar in the 15m window; symbols: 1000PEPEUSDT, 4USDT, AAVEUSDT, ADAUSDT, AKEUSDT +25 more (streak 160/6) | 160 |
| sar_live_arms | ok | 50 arms current, none stalled; covering 776/776 signals (100%) | 0 |
| sar_refresh_budget | ok | 11 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 2 resolved, 13 still mid-window | 0 |
| scan_cycle | ok | last 15.75s, worst 81.0s over 3913 lifetime cycles; lifetime 6 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 1.23s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 126177 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 16m ago | 0 |
| snapshot_writer | ok | last cycle 10s ago (3.26s to run, worst 48.66s), 202 overrun(s) of 3316 cycles, TTL 900s; slowest signals=2.71s, alerts=0.23s, activity=0.18s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +7 / upstream +0 | 0 |
| structural_snap | ok | 4798/4798 measured, 13 blind, 0 levels moved (refusals: redetect_cooldown=179) | 0 |
| structural_veto_lane | ok | 356 stamped; 0 with no readable level book, 14 with clear air ahead, 256 would-reject, 0 enforced | 0 |
| suppression_audit | violating | upstream +50 but output +0 (streak 2/72) | 2 |
| tuned_variants | violating | 74 non-stamps — atr_arm_uncomputable=74 (seen=1338 stamped=178 skipped=1086) (streak 144/6) | 144 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2178298`
- `Path funnel` emissions: `58`
- `Regime distribution` emissions: `58`
- `QUIET_SCALP_BLOCK` events: `82`
- `confidence_gate` events: `3563`
- `free_channel_post` events: `69`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **19**
- Total REST-fallback activations: **5**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 6 | 10275 | 10340 | 14153 | 0 |
| futures_aggtrade | 3 | 8968 | 8968 | 10320 | 0 |
| futures_depth | 1 | 10319 | 10319 | 10319 | 0 |
| futures_liq | 7 | 8918 | 10311 | 10748 | 0 |
| futures_mover | 2 | 1873 | 1873 | 10412 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 5 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **69**

| Source | Count |
|---|---:|
| signal_close | 62 |
| regime_shift | 6 |
| signal_highlight | 1 |

- By severity: HIGH=69

## Dependency readiness
- cvd: presence[present=371775] state[populated=371775] buckets[many=371775] sources[none] quality[none]
- funding_rate: presence[absent=33208, present=338567] state[empty=33208, populated=338567] buckets[few=338567, none=33208] sources[none] quality[none]
- liquidation_clusters: presence[absent=200131, present=171644] state[empty=200131, populated=171644] buckets[few=142847, none=200131, some=28797] sources[none] quality[none]
- oi_snapshot: presence[absent=31848, present=339927] state[empty=31848, populated=339927] buckets[few=13, many=339913, none=31848, some=1] sources[none] quality[none]
- order_book: presence[absent=101209, present=270566] state[populated=270566, unavailable=101209] buckets[few=270566, none=101209] sources[book_ticker=270566, unavailable=101209] quality[none=101209, top_of_book_only=270566]
- orderblocks: presence[absent=371775] state[empty=371775] buckets[none=371775] sources[measured_dark=371775] quality[none]
- recent_ticks: presence[present=371775] state[populated=371775] buckets[many=371775] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.311604380607605` sec
- Median create→first breach: `5883.398479938507` sec
- Median create→terminal: `5887.370470881462` sec
- Median first breach→terminal: `2.7558473348617554` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 1.6}, "under_180s": {"count": 1, "pct": 1.6}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 1.9461468284073093 | 2.282097742317667 | 0.852419600174296 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 5 | 5 | 0.810308467107327 | 1.225217203059616 | 0.8442835820895591 | 0 | 5 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 1.355685498757577 | 1.5178545955555713 | 0.8800234585208562 | 0 | 3 |
| MOVER_AVWAP_SCALP | 9 | 9 | 2.4182674306347325 | 2.5702399186275473 | 0.8570747997384566 | 3 | 6 |
| MOVER_TREND_PULLBACK | 31 | 31 | 4.022144950100914 | 3.0 | 1.3667770262522578 | 23 | 8 |
| QUIET_COMPRESSION_BREAK | 12 | 12 | 1.0704276732815916 | 1.2188354747458394 | 0.8866202500463259 | 0 | 9 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.9461 | 3753.502639055252 | 3755.884696006775 |
| FAILED_AUCTION_RECLAIM | 5 | 5 | 40.0 | 40.0 | 40.0 | 0.0 | 0.424 | 7243.834647893906 | 7245.318244934082 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 66.7 | 0.0 | 66.7 | 0.0 | 1.1918 | 29205.12979698181 | 29210.246027946472 |
| MOVER_AVWAP_SCALP | 9 | 9 | 11.1 | 77.8 | 11.1 | 0.0 | -1.3645 | 4642.7776210308075 | 4648.297315120697 |
| MOVER_TREND_PULLBACK | 31 | 31 | 29.0 | 41.9 | 29.0 | 0.0 | 0.2088 | 3447.7915041446686 | 3449.339344024658 |
| QUIET_COMPRESSION_BREAK | 12 | 12 | 16.7 | 50.0 | 16.7 | 0.0 | -0.2351 | 10836.497843146324 | 10840.087514042854 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1606 | 5 | 1345 | 0.0 | 0.0 | None | None | 261 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2739 | 19 | 2503 | 0.0 | 0.0 | None | None | 236 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `32`
- Gating Δ: `-15563`
- No-generation Δ: `-260254`
- Fast failures Δ: `1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.8785, "current_avg_pnl": 0.424, "current_win_rate": 40.0, "previous_avg_pnl": -0.4545, "previous_win_rate": 0.0, "win_rate_delta": 40.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.8291, "current_avg_pnl": 1.1918, "current_win_rate": 66.7, "previous_avg_pnl": 2.0209, "previous_win_rate": 100.0, "win_rate_delta": -33.3}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.0623, "current_avg_pnl": -1.3645, "current_win_rate": 11.1, "previous_avg_pnl": -0.3022, "previous_win_rate": 25.0, "win_rate_delta": -13.9}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.3507, "current_avg_pnl": 0.2088, "current_win_rate": 29.0, "previous_avg_pnl": -0.1419, "previous_win_rate": 32.0, "win_rate_delta": -3.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.7703, "current_avg_pnl": -0.2351, "current_win_rate": 16.7, "previous_avg_pnl": 0.5352, "previous_win_rate": 16.7, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": -114, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 8, "geometry_changed_delta": 0, "geometry_preserved_delta": 169, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **LIQUIDITY_SWEEP_REVERSAL**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
