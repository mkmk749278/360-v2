# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `260` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 35 | 35 | 0 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 8369 | 8369 | 7514 | 11 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 88400 | 88429 | 2 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 90233 | 90236 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 89802 | 87410 | 2806 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 90285 | 88962 | 1429 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 92047 | 91887 | 210 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 80338 | 80344 | 15 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 90400 | 90432 | 13 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 90448 | 87741 | 3987 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 92680 | 99561 | 901 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 88438 | 82540 | 10057 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 91651 | 91654 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 90240 | 90272 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 89763 | 89657 | 140 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 91735 | 89719 | 2710 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 89324 | 89585 | 111 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 77784 | 73733 | 4422 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 78165 | 77869 | 375 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 88348 | 88370 | 24 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 80367 | 80384 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3523 | 3523 | 2907 | 12 | active-healthy (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 855 | 855 | 255 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 30 | 30 | 24 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 18671 | 18671 | 17317 | 41 | active-healthy (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 23 | 23 | 6 | 3 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 9371 | 9371 | 8222 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2066 | 2066 | 419 | 61 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 27186 | 27186 | 13203 | 223 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 18 | 18 | 18 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 628 | 628 | 320 | 44 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 6261 | 6261 | 6139 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 470 | 470 | 117 | 5 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1290 | 1290 | 992 | 16 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 66 | 66 | 17 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=88429): breakout_not_found=42482, basic_filters_failed=27935, move_not_fresh=13024, breakout_stale=3502, retest_proximity_failed=1267, volume_spike_missing=200, move_exhausted=15, missing_fvg_or_orderblock=2, ema_alignment_reject=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=90236): cls_disabled_merged_into_lsr=90236
- **EVAL::DIVERGENCE_CONTINUATION** (total=87410): cvd_divergence_failed=29163, h1_trend_not_aligned=27715, basic_filters_failed=24928, ema_alignment_reject=4378, retest_proximity_failed=945, missing_fvg_or_orderblock=281
- **EVAL::FAILED_AUCTION_RECLAIM** (total=88962): auction_not_detected=55396, basic_filters_failed=24282, reclaim_hold_failed=3914, regime_blocked=2657, tail_too_small=2620, rsi_reject=93
- **EVAL::FUNDING_EXTREME** (total=91887): funding_not_extreme=59995, basic_filters_failed=24129, missing_funding_rate=4436, ema_alignment_reject=2367, rsi_reject=520, cvd_divergence_failed=207, momentum_reject=191, missing_fvg_or_orderblock=42
- **EVAL::LIQUIDATION_REVERSAL** (total=80344): cascade_threshold_not_met=53875, basic_filters_failed=25540, cvd_divergence_failed=587, rsi_reject=313, missing_fvg_or_orderblock=21, volume_spike_missing=8
- **EVAL::MA_CROSS_TREND_SHIFT** (total=90432): no_ma_cross=64127, basic_filters_failed=24955, ma_cross_cooldown=1220, ma_cross_htf_misaligned=130
- **EVAL::MEAN_REVERT** (total=87741): no_extension=71187, basic_filters_failed=16554
- **EVAL::MOVER_AVWAP_SCALP** (total=99561): no_avwap_tag=36011, basic_filters_failed=28307, no_mover_leg=23140, avwap_slope_against=8714, avwap_reclaim_no_volume=1884, no_avwap_reclaim=1448, anchor_too_recent=57
- **EVAL::MOVER_TREND_PULLBACK** (total=82540): mover_run_too_small=37191, basic_filters_failed=28130, no_reclaim=14672, no_pullback_tag=2547
- **EVAL::OPENING_RANGE_BREAKOUT** (total=91654): feature_disabled=91654
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=90272): regime_blocked=51685, breakout_not_found=27300, basic_filters_failed=7091, adx_reject=4118, ema_alignment_reject=78
- **EVAL::QUIET_COMPRESSION_BREAK** (total=89657): regime_blocked=41035, compression_not_detected=23434, basic_filters_failed=17171, breakout_not_detected=7414, volume_confirmation_failed=568, rsi_reject=33, missing_fvg_or_orderblock=2
- **EVAL::RANGE_FADE** (total=89719): no_range_edge=73156, basic_filters_failed=16563
- **EVAL::SR_FLIP_RETEST** (total=89585): flip_close_not_confirmed=55348, basic_filters_failed=24232, regime_blocked=2641, long_break_volume_thin=2440, h1_break_not_confirmed=1951, retest_out_of_zone=1528, reclaim_hold_failed=895, ema_alignment_reject=172, wick_quality_failed=138, whipsaw_flip=130, long_acceptance_not_held=106, missing_fvg_or_orderblock=4
- **EVAL::STANDARD** (total=73733): momentum_reject=23656, adx_reject=18749, basic_filters_failed=12363, ema_alignment_reject=6687, sweeps_not_detected=6567, macd_reject=4669, htf_poi_unanchored=898, rsi_reject=81, invalid_sl_geometry=44, mtf_reject=19
- **EVAL::TREND_PULLBACK** (total=77869): h1_trend_not_aligned=33260, h1_pullback_not_confirmed=16156, basic_filters_failed=8908, ema_alignment_reject=8038, ema_not_tested_prev=4254, no_ema_reclaim_close=3140, body_conviction_fail=1551, rsi_reject=1268, prev_already_above_emas=516, no_prev_high_break=258, no_prev_low_break=161, prev_already_below_emas=152, momentum_flat=100, missing_fvg_or_orderblock=61, momentum_reject=25, ema21_not_tagged=21
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=88370): breakout_not_found=47858, basic_filters_failed=27931, move_not_fresh=7594, breakout_stale=3437, retest_proximity_failed=1382, volume_spike_missing=130, missing_fvg_or_orderblock=25, move_exhausted=13
- **EVAL::WHALE_MOMENTUM** (total=80384): momentum_reject=61249, recent_ticks_insufficient=11876, basic_filters_failed=7259

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=387): setup_compat:regime_VOLATILE_UNSUITABLE=335, setup_compat:regime_BREAKOUT_EXPANSION=52
- **FAILED_AUCTION_RECLAIM** (total=1899): setup_compat:regime_STRONG_TREND=1169, execution:overextended=730
- **FUNDING_EXTREME_SIGNAL** (total=745): execution:trigger_not_confirmed=745
- **LIQUIDATION_REVERSAL** (total=32): execution:trigger_not_confirmed=30, context_floor=2
- **LIQUIDITY_SWEEP_REVERSAL** (total=4681): setup_compat:regime_STRONG_TREND=1756, execution:overextended=1487, execution:trigger_not_confirmed=1438
- **MA_CROSS_TREND_SHIFT** (total=17): execution:trigger_not_confirmed=7, setup_compat:regime_CLEAN_RANGE=6, setup_compat:regime_DIRTY_RANGE=3, execution:overextended=1
- **MEAN_REVERT** (total=6964): setup_compat:regime_STRONG_TREND=4386, setup_compat:regime_WEAK_TREND=1880, execution:overextended=698
- **MOVER_AVWAP_SCALP** (total=1594): execution:overextended=1306, entry_quality=148, execution:trigger_not_confirmed=140
- **MOVER_TREND_PULLBACK** (total=12963): execution:trigger_not_confirmed=5601, execution:overextended=5593, entry_quality=1769
- **QUIET_COMPRESSION_BREAK** (total=10): execution:overextended=9, execution:trigger_not_confirmed=1
- **RANGE_FADE** (total=6018): setup_compat:regime_STRONG_TREND=3412, setup_compat:regime_WEAK_TREND=1220, execution:overextended=1088, setup_compat:regime_VOLATILE_UNSUITABLE=298
- **TREND_PULLBACK_EMA** (total=1070): setup_compat:regime_CLEAN_RANGE=732, setup_compat:regime_DIRTY_RANGE=215, entry_quality=104, setup_compat:regime_VOLATILE_UNSUITABLE=19
- **VOLUME_SURGE_BREAKOUT** (total=7): execution:overextended=7

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 154189 | 30.9% |
| QUIET | 134453 | 26.9% |
| TRENDING_DOWN | 120392 | 24.1% |
| TRENDING_UP | 68576 | 13.7% |
| VOLATILE | 21584 | 4.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **149**
- Average confidence gap to threshold: **12.30** (samples=149) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: AAVEUSDT=24, ETHUSDT=21, SOLUSDT=16, PUMPUSDT=12, TAOUSDT=9, ARBUSDT=8, QNTUSDT=7, ASTERUSDT=6, XLMUSDT=6, 1000PEPEUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 34 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 223 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 6 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 70 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 83 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 17 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 139 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 72 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 3 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 257 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 47 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 198 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 2 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 4 |
| MEAN_REVERT | filtered | min_confidence | 6 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 183 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 959 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 3484 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 6 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3706 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 52 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 28 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 185 |
| SR_FLIP_RETEST | filtered | min_confidence | 30 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 9 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 5 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 25 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 130 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 15 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 21 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 34 | 45.25 | 63.59 | 18.34 | 19.16 | 17.65 | 20.00 | 4.50 | 30.29 |
| BREAKDOWN_SHORT | kept | 1 | 69.70 | 65.00 | -4.70 | 20.90 | 17.70 | 20.00 | 3.00 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 229 | 57.61 | 64.34 | 6.73 | 20.86 | 19.68 | 18.21 | 0.52 | 8.58 |
| DIVERGENCE_CONTINUATION | kept | 70 | 68.61 | 65.00 | -3.61 | 21.20 | 19.66 | 17.87 | 1.41 | 5.48 |
| FAILED_AUCTION_RECLAIM | filtered | 100 | 52.94 | 64.52 | 11.58 | 20.02 | 19.73 | 20.00 | 3.21 | 12.53 |
| FAILED_AUCTION_RECLAIM | kept | 139 | 70.63 | 65.00 | -5.63 | 21.16 | 19.72 | 20.00 | 3.64 | 3.03 |
| FUNDING_EXTREME_SIGNAL | filtered | 75 | 40.85 | 63.04 | 22.19 | 20.06 | 14.23 | 17.58 | 2.92 | 12.92 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 68.25 | 65.00 | -3.25 | 20.85 | 17.00 | 17.00 | 1.50 | 0.00 |
| LIQUIDATION_REVERSAL | filtered | 3 | 65.07 | 10.00 | -55.07 | 21.00 | 8.60 | 15.00 | 5.33 | -0.97 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 304 | 56.14 | 64.72 | 8.58 | 21.34 | 19.27 | 18.04 | 1.18 | 13.41 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 198 | 69.94 | 65.00 | -4.94 | 20.12 | 18.80 | 17.48 | 1.49 | 0.03 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 55.10 | 65.00 | 9.90 | 22.15 | 19.80 | 15.80 | 0.00 | 15.65 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 71.95 | 65.00 | -6.95 | 20.25 | 16.82 | 15.80 | 0.00 | 1.22 |
| MEAN_REVERT | filtered | 6 | 45.10 | 65.00 | 19.90 | 21.20 | 14.00 | 17.80 | 0.00 | 8.20 |
| MOVER_AVWAP_SCALP | filtered | 185 | 51.38 | 64.73 | 13.35 | 20.49 | 15.74 | 15.80 | 4.06 | 22.29 |
| MOVER_AVWAP_SCALP | kept | 959 | 79.81 | 65.00 | -14.81 | 20.60 | 15.01 | 15.80 | 3.81 | 2.86 |
| MOVER_TREND_PULLBACK | filtered | 3490 | 54.54 | 63.86 | 9.32 | 20.02 | 18.36 | 15.80 | 4.05 | 18.42 |
| MOVER_TREND_PULLBACK | kept | 3706 | 75.40 | 65.00 | -10.40 | 20.31 | 18.58 | 15.80 | 4.14 | 1.91 |
| QUIET_COMPRESSION_BREAK | filtered | 80 | 59.12 | 65.00 | 5.88 | 21.44 | 19.20 | 20.00 | 0.00 | 12.61 |
| QUIET_COMPRESSION_BREAK | kept | 185 | 75.66 | 65.00 | -10.66 | 21.71 | 19.61 | 20.00 | 0.00 | 0.74 |
| SR_FLIP_RETEST | filtered | 39 | 57.46 | 63.97 | 6.51 | 21.15 | 20.00 | 15.57 | 2.26 | 14.16 |
| SR_FLIP_RETEST | kept | 5 | 68.76 | 65.00 | -3.76 | 21.12 | 20.00 | 17.12 | 2.50 | 3.70 |
| TREND_PULLBACK_EMA | filtered | 30 | 53.02 | 65.00 | 11.98 | 20.12 | 20.00 | 18.14 | 4.50 | 21.44 |
| TREND_PULLBACK_EMA | kept | 130 | 78.29 | 65.00 | -13.29 | 20.84 | 19.99 | 18.46 | 4.95 | -0.44 |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 46.64 | 62.07 | 15.43 | 20.41 | 17.62 | 20.00 | 4.63 | 8.49 |
| VOLUME_SURGE_BREAKOUT | kept | 21 | 81.75 | 65.00 | -16.75 | 19.27 | 19.85 | 20.00 | 4.74 | 1.94 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 34 | 45.25 | 15.00 | 18.00 | 12.00 | 14.00 | 4.04 | 8.00 | 4.50 |
| BREAKDOWN_SHORT | kept | 1 | 69.70 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 4.70 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 229 | 57.61 | 21.68 | 15.90 | 4.48 | 12.83 | 5.97 | 8.29 | 0.52 |
| DIVERGENCE_CONTINUATION | kept | 70 | 68.61 | 21.57 | 16.14 | 6.51 | 13.34 | 6.32 | 8.91 | 1.41 |
| FAILED_AUCTION_RECLAIM | filtered | 100 | 52.94 | 21.72 | 15.88 | 5.58 | 12.40 | 5.24 | 5.79 | 3.21 |
| FAILED_AUCTION_RECLAIM | kept | 139 | 70.63 | 24.24 | 15.24 | 7.49 | 13.09 | 5.91 | 4.05 | 3.64 |
| FUNDING_EXTREME_SIGNAL | filtered | 75 | 40.85 | 24.15 | 12.59 | 3.88 | 13.39 | 6.99 | 4.27 | 2.92 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 68.25 | 21.00 | 13.00 | 6.00 | 11.50 | 9.25 | 6.00 | 1.50 |
| LIQUIDATION_REVERSAL | filtered | 3 | 65.07 | 22.33 | 8.00 | 15.00 | 8.00 | 5.17 | 6.23 | 5.33 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 304 | 56.14 | 23.12 | 16.04 | 6.02 | 11.86 | 5.22 | 6.13 | 1.18 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 198 | 69.94 | 23.27 | 15.52 | 5.79 | 12.47 | 6.43 | 5.46 | 1.49 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 55.10 | 21.00 | 14.00 | 4.50 | 15.50 | 6.75 | 9.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 71.95 | 25.00 | 14.00 | 7.50 | 13.25 | 6.00 | 7.42 | 0.00 |
| MEAN_REVERT | filtered | 6 | 45.10 | 17.00 | 14.00 | 15.00 | 12.00 | 5.00 | 5.30 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 185 | 51.38 | 17.94 | 18.15 | 10.90 | 13.33 | 6.01 | 4.67 | 4.06 |
| MOVER_AVWAP_SCALP | kept | 959 | 79.81 | 19.07 | 18.00 | 14.14 | 13.94 | 7.82 | 5.97 | 3.81 |
| MOVER_TREND_PULLBACK | filtered | 3490 | 54.54 | 18.36 | 18.04 | 7.69 | 12.01 | 6.27 | 8.20 | 4.05 |
| MOVER_TREND_PULLBACK | kept | 3706 | 75.40 | 19.40 | 18.02 | 7.94 | 12.61 | 6.40 | 8.90 | 4.14 |
| QUIET_COMPRESSION_BREAK | filtered | 80 | 59.12 | 17.70 | 16.60 | 11.59 | 14.15 | 6.28 | 5.42 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 185 | 75.66 | 18.56 | 17.63 | 12.52 | 14.09 | 7.44 | 7.32 | 0.00 |
| SR_FLIP_RETEST | filtered | 39 | 57.46 | 22.74 | 15.69 | 3.31 | 14.69 | 6.50 | 6.43 | 2.26 |
| SR_FLIP_RETEST | kept | 5 | 68.76 | 25.00 | 16.00 | 3.60 | 13.40 | 5.00 | 6.94 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 30 | 53.02 | 15.77 | 18.00 | 7.75 | 14.00 | 6.08 | 8.37 | 4.50 |
| TREND_PULLBACK_EMA | kept | 130 | 78.29 | 16.34 | 18.00 | 7.74 | 15.32 | 6.91 | 9.40 | 4.95 |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 46.64 | 8.13 | 18.00 | 12.00 | 16.20 | 5.00 | 6.17 | 4.63 |
| VOLUME_SURGE_BREAKOUT | kept | 21 | 81.75 | 18.52 | 17.62 | 13.57 | 14.00 | 6.00 | 9.24 | 4.74 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 34 | 45.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.53 | 0.00 | 0.00 | **0.53** |
| BREAKDOWN_SHORT | kept | 1 | 69.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 229 | 57.61 | 0.00 | 0.00 | 0.10 | 0.00 | 0.72 | 0.00 | 0.00 | 0.00 | **0.82** |
| DIVERGENCE_CONTINUATION | kept | 70 | 68.61 | 0.00 | 0.00 | 1.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.85** |
| FAILED_AUCTION_RECLAIM | filtered | 100 | 52.94 | 0.00 | 0.00 | 1.42 | 0.00 | 2.59 | 0.18 | 0.00 | 0.00 | **4.19** |
| FAILED_AUCTION_RECLAIM | kept | 139 | 70.63 | 0.00 | 0.00 | 1.84 | 0.00 | 0.26 | 0.00 | 0.00 | 0.00 | **2.10** |
| FUNDING_EXTREME_SIGNAL | filtered | 75 | 40.85 | 0.00 | 0.00 | 1.70 | 0.00 | 0.86 | 0.00 | 0.00 | 0.00 | **2.56** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 68.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 3 | 65.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 304 | 56.14 | 0.00 | 0.00 | 1.16 | 0.00 | 1.28 | 0.00 | 0.00 | 0.00 | **2.44** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 198 | 69.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 55.10 | 0.00 | 0.00 | 0.00 | 0.00 | 10.80 | 0.00 | 0.00 | 0.00 | **10.80** |
| MA_CROSS_TREND_SHIFT | kept | 4 | 71.95 | 0.00 | 0.00 | 1.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.20** |
| MEAN_REVERT | filtered | 6 | 45.10 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 1.00 | 0.00 | 0.00 | **8.20** |
| MOVER_AVWAP_SCALP | filtered | 185 | 51.38 | 0.00 | 0.00 | 0.13 | 0.00 | 3.28 | 0.28 | 0.00 | 1.04 | **4.73** |
| MOVER_AVWAP_SCALP | kept | 959 | 79.81 | 0.11 | 0.00 | 0.47 | 0.00 | 0.48 | 0.22 | 0.00 | 0.01 | **1.29** |
| MOVER_TREND_PULLBACK | filtered | 3490 | 54.54 | 0.00 | 0.00 | 1.86 | 0.00 | 0.50 | 0.01 | 0.00 | 0.05 | **2.42** |
| MOVER_TREND_PULLBACK | kept | 3706 | 75.40 | 0.03 | 0.00 | 0.55 | 0.00 | 0.06 | 0.00 | 0.00 | 0.03 | **0.67** |
| QUIET_COMPRESSION_BREAK | filtered | 80 | 59.12 | 0.00 | 0.00 | 1.28 | 0.00 | 0.48 | 0.90 | 0.00 | 0.81 | **3.47** |
| QUIET_COMPRESSION_BREAK | kept | 185 | 75.66 | 0.00 | 0.00 | 0.16 | 0.00 | 0.16 | 0.00 | 0.00 | 0.53 | **0.85** |
| SR_FLIP_RETEST | filtered | 39 | 57.46 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 5 | 68.76 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 30 | 53.02 | 0.00 | 0.00 | 0.80 | 0.00 | 3.60 | 0.00 | 0.00 | 0.00 | **4.40** |
| TREND_PULLBACK_EMA | kept | 130 | 78.29 | 0.00 | 0.00 | 0.19 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.19** |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 46.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.96 | **0.96** |
| VOLUME_SURGE_BREAKOUT | kept | 21 | 81.75 | 0.00 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.23** |

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
- Outcomes recorded: **208701 held of 1057886 seen** across 21 strategies; 4724 cells past the sample floor; **2599 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 49735 | 535/49200/0 | 43% | -0.20 | NY/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (+1.24R) | OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL (-1.30R) |
| MOVER_AVWAP_SCALP | 27258 | 192/27066/0 | 43% | -0.18 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 17017 | 288/16729/0 | 48% | -0.11 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.86R) | LONDON/MARKUP/EXPANDED/BTC_FALLING (-1.19R) |
| FAILED_AUCTION_RECLAIM | 16131 | 226/15905/0 | 38% | -0.29 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+1.69R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 15312 | 86/15226/0 | 39% | -0.28 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 12816 | 164/12652/0 | 38% | -0.42 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.91R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 10034 | 543/9491/0 | 46% | -0.10 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8597 | 0/0/8597 | 42% | -0.12 | OVERLAP/MARKUP/CASCADE/BTC_RISING (+1.58R) | OVERLAP/MARKDOWN/EXPANDED/BTC_FALLING (-0.95R) |
| SHADOW_RANGE_FADE | 8167 | 0/0/8167 | 35% | -0.16 | ASIA/MARKDOWN/NORMAL/BTC_FALLING (+1.00R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.33R) |
| SR_FLIP_RETEST | 7958 | 35/7923/0 | 47% | -0.28 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.30R) |
| SHADOW_FUNDING_FADE | 7850 | 0/0/7850 | 35% | -0.40 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (-0.01R) | OFF_HOURS/RANGE/NORMAL/BTC_RISING (-0.95R) |
| MEAN_REVERT | 6265 | 83/6182/0 | 37% | -0.31 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.60R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 5109 | 4/5105/0 | 33% | -0.40 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+0.95R) | LONDON/MARKDOWN/COMPRESSED/BTC_RISING/MIDCAP (-1.42R) |
| VOLUME_SURGE_BREAKOUT | 4620 | 0/4620/0 | 32% | -0.32 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/NORMAL/BTC_FALLING/ALTCOIN (-1.19R) |
| WHALE_MOMENTUM | 4500 | 4/4496/0 | 47% | -0.27 | NY/RANGE/EXPANDED/BTC_FALLING (+0.94R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| RANGE_FADE | 3525 | 6/3519/0 | 51% | +0.25 | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (+3.08R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.78R) |
| SHADOW_CASCADE_REVERSAL | 1864 | 0/0/1864 | 52% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.18R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-0.62R) |
| BREAKDOWN_SHORT | 907 | 84/823/0 | 33% | -0.30 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.11R) |
| LIQUIDATION_REVERSAL | 596 | 0/596/0 | 33% | -0.31 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 280 | 46/234/0 | 46% | -0.13 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 160 | 14/146/0 | 57% | +0.17 | ASIA/MARKUP/NORMAL/BTC_RISING (-0.02R) | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/ALTCOIN (-0.14R) |

- **Strongest cells**: `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.08R (n=37, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.00R (n=32, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.78R (n=47, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 524 | 28% / -0.54R | 524 | 52% / -0.10R | +0.45 | **ATR** |
| TREND_PULLBACK_EMA | 1596 | 39% / -0.36R | 1596 | 50% / -0.08R | +0.28 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 2060 | 44% / -0.35R | 2060 | 57% / -0.11R | +0.24 | **ATR** |
| LIQUIDATION_REVERSAL | 41 | 24% / -0.63R | 41 | 41% / -0.41R | +0.23 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 264 | 37% / -0.17R | 264 | 48% / -0.03R | +0.14 | **ATR** |
| SR_FLIP_RETEST | 902 | 48% / -0.26R | 902 | 52% / -0.13R | +0.13 | **ATR** |
| MOVER_TREND_PULLBACK | 9488 | 47% / -0.15R | 9488 | 52% / -0.04R | +0.11 | **ATR** |
| MOVER_AVWAP_SCALP | 3148 | 47% / -0.13R | 3148 | 53% / -0.03R | +0.10 | **ATR** |
| MA_CROSS_TREND_SHIFT | 88 | 49% / -0.10R | 88 | 53% / +0.00R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 491 | 47% / -0.29R | 491 | 49% / -0.19R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1836 | 42% / -0.21R | 1836 | 44% / -0.12R | +0.09 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 28 | 68% / +0.09R | 28 | 68% / +0.00R | -0.09 | **FIXED** |
| BREAKDOWN_SHORT | 66 | 41% / -0.15R | 66 | 45% / -0.08R | +0.07 | **ATR** |
| DIVERGENCE_CONTINUATION | 2318 | 48% / -0.12R | 2318 | 53% / -0.06R | +0.06 | **ATR** |
| RANGE_FADE | 201 | 43% / +0.04R | 201 | 50% / +0.09R | +0.05 | **ATR** |
| MEAN_REVERT | 568 | 45% / -0.19R | 568 | 44% / -0.20R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1809 | 49% / -0.08R | 1809 | 49% / -0.08R | +0.00 | **ATR** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12554 | 27% | -0.20R | 314 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 3148 | 51% | -0.02R | 248 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 168 | 48% | -0.05R | 80 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 2029 | 33% / -0.16R | +0.91 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 2384 | 40% / -0.14R | +0.87 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3756 | 36% / -0.14R | +0.70 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11575 | 36% / -0.15R | +0.38 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2663 | 36% / -0.13R | +0.15 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 176 | 34% / -0.38R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1760 | 38% / -0.09R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1537 | 32% / -0.27R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 394 | 33% / -0.21R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 637 | 31% / -0.29R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 464 | 47% / -0.09R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 114 | 45% / +0.20R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 144 | 45% / -0.01R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 775 | 36% / -0.23R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 136 | 32% / +0.09R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 54 | 37% / -0.59R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 45 | 49% / +0.40R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 64 · alerting: **3** · boot grace active: False
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.56R (bound 0.3) (streak 208/6) (sustained 208 cycles)
- **ALERT** `range_fade_emission` — 6393 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.25R over n=3519, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 208/6) (sustained 208 cycles)
- **ALERT** `tuned_variants` — 204 non-stamps — atr_arm_uncomputable=204 (seen=6735 stamped=592 skipped=5939) (streak 208/6) (sustained 208 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 42 fed / 0 quiet / 0 never delivered of 42 subscribed; 25203467 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | no open arms; covering 2073/2073 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| analyst_plan_cadence | ok | last plan 40m ago | 0 |
| atr_trail_live_arms | ok | no open arms; covering 1076/1076 signals (100%) | 0 |
| auto_dispatch | ok | 46 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=46. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 192/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 59674.40 | 0 |
| candle_coverage | ok | 82/82 symbols with ≥20 15m candles, 82/82 updated within 45m [fresh=82; 75 Tier-1 futures + 7 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 276 dup bars, 0 undedupable; ws 0 out-of-order, 147 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 65 cohorts, 20 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +7 / upstream +24 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1266/1285 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 5 promoted today, nothing refused | 0 |
| dark_resolution | violating | 5 of 92 open dark rows are not being advanced (worst: MOVEUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 4/120) | 4 |
| dark_sar_arms | ok | no open arms; covering 1264/1283 signals (99%) | 0 |
| depth_feed | ok | 42/42 books fresh (stale 0, never 0, thin 0); 8504630 msgs, 0 rejected | 0 |
| deriv_recorder | ok | hour recorded, 75 rows | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.56R (bound 0.3) (streak 208/6) | 208 |
| emission_controller | ok | last cycle 462s ago; live_overrides=14 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=1051, MOVER_AVWAP_SCALP=290, MOVER_TREND_PULLBACK=3870, RANGE_FADE=707, TREND_PULLBACK_EMA=82), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 4 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won,TREND_PULLBACK_EMA.campaign_prev_age_h,TREND_PULLBACK_EMA.campaign_prev_won) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 1/6) | 1 |
| firestore_read_budget | ok | 1,319 reads/day of 50,000 [engine 1,297, signing 22]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4953 sealed bars over 42 symbols; 1358 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +6 / upstream +195 | 0 |
| htf_candles | ok | BTCUSDT 1d/1w current | 0 |
| indicator_cache_key | ok | 72019 frozen value(s) avoided; 574148 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.31R over n=6182 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +14 / upstream +195 | 0 |
| mover_admission_metadata | ok | 958 symbols known, 249 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 7 held, 7 with scan counts, 7 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2242 rows held, 3986391 evicted (sampled: execution:trigger_not_confirmed 286/1386685, execution:overextended 286/1210435, setup_compat:regime_STRONG_TREND 286/707317) | 0 |
| price_action_lane | ok | 515401 evaluated, 617 emitted; layer1 617 stamped / 0 blind; cooldown=74779, delta_opposed=53132, no_footprint=188123, no_opposing_target=133, no_sweep=148808, rr_below_floor=49809 | 0 |
| promoted_pair_integrity | ok | 7/7 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 6393 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.25R over n=3519, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 208/6) | 208 |
| range_fade_path | ok | output +2 / upstream +195 | 0 |
| sar_alignment_crosscheck | ok | 288/13901 disagreed (2.1%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +195 | 0 |
| sar_hold_arm | ok | 1851 held arms settled, 149 unscored, 52 still walking (48 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 58/58 resolvable | 0 |
| sar_live_arms | ok | 52 arms current, none stalled; covering 1075/1075 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 11 resolved, 47 still mid-window | 0 |
| scan_cycle | ok | last 106.67s, worst 207.1s over 6713 lifetime cycles; lifetime 173 over 60s, 16 over 120s (plus 1/0 during boot warm-up, not counted); recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 41.12s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 169468 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 46s ago (97.76s to run, worst 165.11s), 725 overrun(s) of 4668 cycles, TTL 900s; slowest tickers=28.29s, signals=9.97s, trail_governor=9.49s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +70 / upstream +195 | 0 |
| structural_snap | ok | 6000/6000 measured, 44 blind, 0 levels moved (refusals: redetect_cooldown=1174) | 0 |
| structural_veto_lane | ok | 1678 stamped; 0 with no readable level book, 41 with clear air ahead, 998 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +195 / upstream +24 | 0 |
| tuned_variants | violating | 204 non-stamps — atr_arm_uncomputable=204 (seen=6735 stamped=592 skipped=5939) (streak 208/6) | 208 |
| unlock_shorts | ok | 15 open, 47 scheduled, calendar 14.4h old | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2298713`
- `Path funnel` emissions: `65`
- `Regime distribution` emissions: `65`
- `QUIET_SCALP_BLOCK` events: `149`
- `confidence_gate` events: `10012`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **13**
- Total REST-fallback activations: **2**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 4 | 17938 | 45179 | 46029 | 0 |
| futures_aggtrade | 3 | 22325 | 22325 | 35234 | 0 |
| futures_liq | 6 | 2602 | 5013 | 26061 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 2 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=363657] state[populated=363657] buckets[many=363657] sources[none] quality[none]
- funding_rate: presence[absent=29559, present=334098] state[empty=29559, populated=334098] buckets[few=334098, none=29559] sources[none] quality[none]
- liquidation_clusters: presence[absent=201098, present=162559] state[empty=201098, populated=162559] buckets[few=129914, none=201098, some=32645] sources[none] quality[none]
- oi_snapshot: presence[absent=29559, present=334098] state[empty=29559, populated=334098] buckets[few=463, many=331531, none=29559, some=2104] sources[none] quality[none]
- order_book: presence[absent=104288, present=259369] state[populated=259369, unavailable=104288] buckets[few=259369, none=104288] sources[book_ticker=259369, unavailable=104288] quality[none=104288, top_of_book_only=259369]
- orderblocks: presence[absent=363657] state[empty=363657] buckets[none=363657] sources[measured_dark=363657] quality[none]
- recent_ticks: presence[present=363657] state[populated=363657] buckets[many=363657] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.1634424924850464` sec
- Median create→first breach: `9947.192039489746` sec
- Median create→terminal: `9947.192109465599` sec
- Median first breach→terminal: `0.00012445449829101562` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.8382819308564626 | 0.9164145920207648 | 0.9147409242011155 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 1.039041730072646 | 1.152848496493419 | 0.8616590075048816 | 0 | 3 |
| LIQUIDITY_SWEEP_REVERSAL | 5 | 5 | 1.124586549062836 | 1.2865109601899425 | 0.9494013966705278 | 1 | 3 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 1.7353432678706524 | 1.0414195953814411 | 1.6663247701182804 | 1 | 0 |
| MOVER_AVWAP_SCALP | 3 | 3 | 1.9834063400278668 | 2.22784386694821 | 0.8562953320510516 | 1 | 2 |
| MOVER_TREND_PULLBACK | 21 | 21 | 3.5084385439799313 | 3.0 | 1.2249758669209947 | 15 | 6 |
| QUIET_COMPRESSION_BREAK | 12 | 12 | 1.1375916115509281 | 1.2699648694819485 | 0.8963252455149803 | 0 | 10 |
| SR_FLIP_RETEST | 2 | 2 | 0.7766674818642634 | 1.2053526223583861 | 0.6582455494115451 | 0 | 2 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1.2764940664504185 | 1.2574228962763474 | 0 | 0 | 0 | 1 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 3 | 1.736635038185601 | 1.5585625951089974 | 0 | 0 | 0 | 3 | 1 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 5 | 1.9773980154355089 | 1.686879823594266 | 1 | 1 | 1 | 2 | 1 | 2 |
| MA_CROSS_TREND_SHIFT | 1 | 2.603013257015034 | 1.3771296128162054 | 0 | 0 | 0 | 1 | 0 | 0 |
| MOVER_AVWAP_SCALP | 3 | 2.3659007756475954 | 2.6890619054588076 | 3 | 0 | 0 | 0 | 0 | 0 |
| MOVER_TREND_PULLBACK | 21 | 4.480872768489659 | 4.012320000000015 | 7 | 5 | 5 | 14 | 1 | 0 |
| QUIET_COMPRESSION_BREAK | 12 | 2.844437014848435 | 1.8150544127177166 | 0 | 0 | 0 | 9 | 2 | 3 |
| SR_FLIP_RETEST | 2 | 2.024633026398287 | 1.5819993785995399 | 0 | 0 | 0 | 1 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.2574 | 13016.524658203125 | 13016.94714307785 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 66.7 | 33.3 | 66.7 | 0.0 | 0.5987 | 21548.278919935226 | 21556.914668798447 |
| LIQUIDITY_SWEEP_REVERSAL | 5 | 5 | 80.0 | 0.0 | 80.0 | 0.0 | 1.3791 | 9476.203904151917 | 9486.016554117203 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.3771 | 217769.720307827 | 217770.30896687508 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -1.9249 | 4490.18999505043 | 4490.190013885498 |
| MOVER_TREND_PULLBACK | 21 | 21 | 38.1 | 14.3 | 38.1 | 0.0 | 1.4079 | 4783.384469985962 | 4783.3845319747925 |
| QUIET_COMPRESSION_BREAK | 12 | 12 | 41.7 | 33.3 | 41.7 | 0.0 | 0.3766 | 17900.896723508835 | 17900.896849513054 |
| SR_FLIP_RETEST | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 9191.720598936081 | 9191.720646500587 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 470 | 5 | 117 | 0.0 | 0.0 | 9191.720598936081 | 9191.720646500587 | 353 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1290 | 16 | 992 | 0.0 | 0.0 | None | None | 298 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-16`
- Gating Δ: `-1783`
- No-generation Δ: `-128996`
- Fast failures Δ: `0`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 1.8544, "current_avg_pnl": 1.2574, "current_win_rate": 100.0, "previous_avg_pnl": -0.597, "previous_win_rate": 0.0, "win_rate_delta": 100.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 1.1206, "current_avg_pnl": 0.5987, "current_win_rate": 66.7, "previous_avg_pnl": -0.5219, "previous_win_rate": 0.0, "win_rate_delta": 66.7}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.563, "current_avg_pnl": 1.3791, "current_win_rate": 80.0, "previous_avg_pnl": 1.9421, "previous_win_rate": 50.0, "win_rate_delta": 30.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -3.853, "current_avg_pnl": -1.9249, "current_win_rate": 0.0, "previous_avg_pnl": 1.9281, "previous_win_rate": 100.0, "win_rate_delta": -100.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.2282, "current_avg_pnl": 1.4079, "current_win_rate": 38.1, "previous_avg_pnl": 0.1797, "previous_win_rate": 33.3, "win_rate_delta": 4.8}, "POST_DISPLACEMENT_CONTINUATION": {"avg_pnl_delta": -1.4701, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 1.4701, "previous_win_rate": 100.0, "win_rate_delta": -100.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.251, "current_avg_pnl": 0.3766, "current_win_rate": 41.7, "previous_avg_pnl": 0.1256, "previous_win_rate": 33.3, "win_rate_delta": 8.4}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 125, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 9191.72, "median_terminal_delta_sec": 9191.72, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -22, "geometry_changed_delta": 0, "geometry_preserved_delta": -250, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **LIQUIDITY_SWEEP_REVERSAL**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
