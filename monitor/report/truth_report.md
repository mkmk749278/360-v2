# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `5183` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 253 | 253 | 179 | 3 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 37063 | 37063 | 33502 | 12 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 177767 | 177742 | 49 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 164047 | 164062 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 163568 | 153658 | 10377 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 164079 | 155930 | 8495 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 170654 | 170536 | 152 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 156190 | 156193 | 11 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 164428 | 164453 | 10 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 164472 | 164155 | 1055 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 182835 | 186932 | 847 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 177794 | 162186 | 20630 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 165315 | 165322 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 164065 | 164065 | 9 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 163498 | 162373 | 1190 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 165217 | 165647 | 527 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 158131 | 156930 | 6525 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 148761 | 141573 | 7572 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 149150 | 147989 | 1234 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 177724 | 177738 | 25 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 156207 | 156120 | 141 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 32311 | 32311 | 23528 | 56 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 613 | 613 | 557 | 3 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 39 | 39 | 39 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 36730 | 36730 | 36132 | 16 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 17 | 17 | 16 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 4768 | 4768 | 4768 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1636 | 1636 | 1621 | 3 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 52227 | 52227 | 45538 | 22 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 33 | 33 | 33 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 5136 | 5136 | 3545 | 53 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 1147 | 1147 | 1147 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 26174 | 26174 | 15991 | 50 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 5809 | 5809 | 5765 | 4 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 213 | 213 | 24 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 5802 | 5802 | 5329 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=177742): breakout_not_found=91624, basic_filters_failed=56292, move_not_fresh=21397, breakout_stale=6957, retest_proximity_failed=1156, volume_spike_missing=246, ema_alignment_reject=33, move_exhausted=27, missing_fvg_or_orderblock=10
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=164062): cls_disabled_merged_into_lsr=164062
- **EVAL::DIVERGENCE_CONTINUATION** (total=153658): cvd_divergence_failed=52897, basic_filters_failed=50279, h1_trend_not_aligned=32631, ema_alignment_reject=15045, retest_proximity_failed=2072, missing_fvg_or_orderblock=734
- **EVAL::FAILED_AUCTION_RECLAIM** (total=155930): auction_not_detected=58746, basic_filters_failed=49691, reclaim_hold_failed=24584, tail_too_small=19611, regime_blocked=3269, rsi_reject=29
- **EVAL::FUNDING_EXTREME** (total=170536): funding_not_extreme=114707, basic_filters_failed=51135, missing_funding_rate=2175, ema_alignment_reject=1493, rsi_reject=695, cvd_divergence_failed=174, momentum_reject=137, missing_fvg_or_orderblock=20
- **EVAL::LIQUIDATION_REVERSAL** (total=156193): cascade_threshold_not_met=103129, basic_filters_failed=51834, cvd_divergence_failed=662, rsi_reject=512, missing_fvg_or_orderblock=44, volume_spike_missing=12
- **EVAL::MA_CROSS_TREND_SHIFT** (total=164453): no_ma_cross=111577, basic_filters_failed=50295, ma_cross_cooldown=1913, ma_cross_htf_misaligned=668
- **EVAL::MEAN_REVERT** (total=164155): no_extension=137767, basic_filters_failed=26388
- **EVAL::MOVER_AVWAP_SCALP** (total=186932): no_mover_leg=74759, basic_filters_failed=56406, no_avwap_tag=41531, avwap_slope_against=10451, avwap_reclaim_no_volume=2261, no_avwap_reclaim=1524
- **EVAL::MOVER_TREND_PULLBACK** (total=162186): mover_run_too_small=85931, basic_filters_failed=56338, no_reclaim=16051, no_pullback_tag=3866
- **EVAL::OPENING_RANGE_BREAKOUT** (total=165322): feature_disabled=165322
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=164065): regime_blocked=119295, breakout_not_found=24335, basic_filters_failed=16154, adx_reject=4230, ema_alignment_reject=46, rsi_reject=5
- **EVAL::QUIET_COMPRESSION_BREAK** (total=162373): regime_blocked=47951, breakout_not_detected=40704, compression_not_detected=37265, basic_filters_failed=33528, volume_confirmation_failed=2734, rsi_reject=137, missing_fvg_or_orderblock=54
- **EVAL::RANGE_FADE** (total=165647): no_range_edge=136944, basic_filters_failed=26392, shadow_mode=2311
- **EVAL::SR_FLIP_RETEST** (total=156930): basic_filters_failed=49670, flip_close_not_confirmed=26086, whipsaw_flip=21546, long_break_volume_thin=18411, long_disabled=13209, reclaim_hold_failed=12253, retest_out_of_zone=7806, regime_blocked=3243, wick_quality_failed=2468, long_acceptance_not_held=991, ema_alignment_reject=815, missing_fvg_or_orderblock=324, rsi_reject=108
- **EVAL::STANDARD** (total=141573): momentum_reject=45391, adx_reject=36303, sweeps_not_detected=21216, basic_filters_failed=20822, macd_reject=12024, ema_alignment_reject=4971, rsi_reject=449, invalid_sl_geometry=394, mtf_reject=3
- **EVAL::TREND_PULLBACK** (total=147989): h1_trend_not_aligned=44548, basic_filters_failed=29730, ema_alignment_reject=21762, h1_pullback_not_confirmed=15045, no_ema_reclaim_close=11065, ema_not_tested_prev=8041, body_conviction_fail=7066, rsi_reject=6032, prev_already_below_emas=1587, prev_already_above_emas=1061, no_prev_low_break=726, no_prev_high_break=565, momentum_flat=544, missing_fvg_or_orderblock=82, ema21_not_tagged=68, momentum_reject=67
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=177738): breakout_not_found=93585, basic_filters_failed=56289, move_not_fresh=17600, breakout_stale=7222, retest_proximity_failed=2277, volume_spike_missing=710, missing_fvg_or_orderblock=38, ema_alignment_reject=9, move_exhausted=8
- **EVAL::WHALE_MOMENTUM** (total=156120): momentum_reject=110988, recent_ticks_insufficient=27234, basic_filters_failed=17898

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=62): execution:overextended=62
- **DIVERGENCE_CONTINUATION** (total=1314): setup_compat:regime_VOLATILE_UNSUITABLE=959, context_floor=254, setup_compat:regime_BREAKOUT_EXPANSION=101
- **FAILED_AUCTION_RECLAIM** (total=6461): setup_compat:regime_STRONG_TREND=2561, execution:overextended=2329, context_floor=1521, setup_compat:regime_VOLATILE_UNSUITABLE=50
- **FUNDING_EXTREME_SIGNAL** (total=497): execution:trigger_not_confirmed=497
- **LIQUIDATION_REVERSAL** (total=39): execution:trigger_not_confirmed=39
- **LIQUIDITY_SWEEP_REVERSAL** (total=8791): execution:trigger_not_confirmed=4061, execution:overextended=2851, setup_compat:regime_STRONG_TREND=1870, context_floor=9
- **MA_CROSS_TREND_SHIFT** (total=14): setup_compat:regime_DIRTY_RANGE=9, setup_compat:regime_CLEAN_RANGE=2, execution:trigger_not_confirmed=1, setup_compat:regime_VOLATILE_UNSUITABLE=1, execution:overextended=1
- **MEAN_REVERT** (total=535): setup_compat:regime_VOLATILE_UNSUITABLE=535
- **MOVER_AVWAP_SCALP** (total=1617): execution:trigger_not_confirmed=1143, execution:overextended=474
- **MOVER_TREND_PULLBACK** (total=45869): execution:trigger_not_confirmed=23139, execution:overextended=20373, context_floor=2357
- **QUIET_COMPRESSION_BREAK** (total=497): context_floor=331, execution:trigger_not_confirmed=166
- **RANGE_FADE** (total=453): execution:overextended=445, setup_compat:regime_VOLATILE_UNSUITABLE=8
- **SR_FLIP_RETEST** (total=2087): context_floor=2084, setup_compat:regime_VOLATILE_UNSUITABLE=3
- **TREND_PULLBACK_EMA** (total=5422): setup_compat:regime_CLEAN_RANGE=3867, setup_compat:regime_DIRTY_RANGE=1408, setup_compat:regime_VOLATILE_UNSUITABLE=147
- **VOLUME_SURGE_BREAKOUT** (total=52): context_floor=45, execution:overextended=7
- **WHALE_MOMENTUM** (total=5141): execution:trigger_not_confirmed=5141

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 354718 | 38.7% |
| QUIET | 264084 | 28.8% |
| TRENDING_DOWN | 133774 | 14.6% |
| TRENDING_UP | 124890 | 13.6% |
| VOLATILE | 38162 | 4.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **482**
- Average confidence gap to threshold: **13.46** (samples=482) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=78, ETHUSDT=68, TRXUSDT=25, BNBUSDT=25, SUIUSDT=23, LINKUSDT=23, ARBUSDT=19, TRUMPUSDT=17, DOGEUSDT=17, SOLUSDT=17

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 62 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 8 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 291 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 13 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 236 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 490 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 182 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 993 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 8 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 4 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 118 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 8 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 79 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 21 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 14 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 509 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 5 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1565 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 150 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 144 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 758 |
| SR_FLIP_RETEST | filtered | min_confidence | 216 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 119 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 645 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 41 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 35 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 5 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 62 | 59.48 | 65.00 | 5.52 | 22.08 | 17.87 | 20.00 | 4.00 | 16.23 |
| BREAKDOWN_SHORT | kept | 8 | 76.64 | 65.00 | -11.64 | 20.72 | 18.91 | 20.00 | 4.75 | 6.77 |
| DIVERGENCE_CONTINUATION | filtered | 304 | 53.48 | 63.32 | 9.84 | 19.97 | 19.82 | 18.54 | 1.19 | 12.40 |
| DIVERGENCE_CONTINUATION | kept | 236 | 70.75 | 65.00 | -5.75 | 20.11 | 19.77 | 17.80 | 3.78 | 0.02 |
| FAILED_AUCTION_RECLAIM | filtered | 672 | 51.01 | 63.34 | 12.33 | 21.00 | 19.22 | 20.00 | 3.84 | 10.08 |
| FAILED_AUCTION_RECLAIM | kept | 993 | 71.33 | 65.00 | -6.33 | 21.08 | 19.86 | 20.00 | 4.37 | 0.41 |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 47.25 | 65.00 | 17.75 | 21.20 | 20.00 | 18.50 | 0.00 | 5.00 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 70.12 | 65.00 | -5.12 | 21.20 | 20.00 | 18.50 | 0.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 126 | 57.56 | 65.00 | 7.44 | 20.02 | 19.36 | 17.57 | 1.83 | 15.73 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 79 | 67.99 | 65.00 | -2.99 | 21.50 | 19.90 | 18.17 | 0.85 | 0.20 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.50 | 65.00 | -1.50 | 21.00 | 16.80 | 15.80 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 21 | 59.70 | 65.00 | 5.30 | 15.90 | 19.37 | 15.80 | 3.17 | 20.00 |
| MOVER_AVWAP_SCALP | kept | 14 | 70.59 | 65.00 | -5.59 | 17.11 | 19.34 | 15.80 | 3.54 | 14.29 |
| MOVER_TREND_PULLBACK | filtered | 514 | 55.75 | 61.03 | 5.28 | 19.72 | 16.76 | 15.80 | 4.52 | 17.60 |
| MOVER_TREND_PULLBACK | kept | 1565 | 76.67 | 65.00 | -11.67 | 19.79 | 18.84 | 15.80 | 4.62 | 1.77 |
| QUIET_COMPRESSION_BREAK | filtered | 294 | 56.23 | 64.43 | 8.20 | 21.60 | 19.26 | 20.00 | 0.00 | 7.92 |
| QUIET_COMPRESSION_BREAK | kept | 758 | 75.36 | 65.00 | -10.36 | 21.34 | 19.65 | 20.00 | 0.00 | 0.39 |
| SR_FLIP_RETEST | filtered | 335 | 54.02 | 64.27 | 10.25 | 20.99 | 19.92 | 16.04 | 1.52 | 15.65 |
| SR_FLIP_RETEST | kept | 645 | 71.18 | 65.00 | -6.18 | 20.90 | 19.93 | 15.83 | 1.90 | -0.03 |
| TREND_PULLBACK_EMA | kept | 41 | 77.47 | 65.00 | -12.47 | 20.95 | 19.96 | 15.52 | 5.50 | -2.85 |
| VOLUME_SURGE_BREAKOUT | filtered | 35 | 50.29 | 65.00 | 14.71 | 19.47 | 18.42 | 20.00 | 4.43 | 19.80 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 85.00 | 65.00 | -20.00 | 21.20 | 19.00 | 20.00 | 6.00 | 3.00 |
| WHALE_MOMENTUM | filtered | 5 | 34.60 | 65.00 | 30.40 | 24.90 | 20.00 | 17.00 | 0.00 | 31.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 62 | 59.48 | 17.00 | 14.00 | 14.81 | 12.26 | 5.00 | 8.65 | 4.00 |
| BREAKDOWN_SHORT | kept | 8 | 76.64 | 19.00 | 17.00 | 14.25 | 14.00 | 5.00 | 9.41 | 4.75 |
| DIVERGENCE_CONTINUATION | filtered | 304 | 53.48 | 22.50 | 15.11 | 6.55 | 11.50 | 5.71 | 7.31 | 1.19 |
| DIVERGENCE_CONTINUATION | kept | 236 | 70.75 | 22.15 | 16.14 | 3.88 | 12.00 | 5.32 | 9.03 | 3.78 |
| FAILED_AUCTION_RECLAIM | filtered | 672 | 51.01 | 20.36 | 16.65 | 8.05 | 11.44 | 6.32 | 4.99 | 3.84 |
| FAILED_AUCTION_RECLAIM | kept | 993 | 71.33 | 23.26 | 14.90 | 4.35 | 11.45 | 6.15 | 7.28 | 4.37 |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 47.25 | 25.00 | 8.00 | 3.00 | 17.00 | 5.50 | 6.88 | 0.00 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 70.12 | 23.00 | 15.50 | 3.00 | 13.00 | 5.62 | 10.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 126 | 57.56 | 22.84 | 14.00 | 10.40 | 12.97 | 5.42 | 5.83 | 1.83 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 79 | 67.99 | 21.41 | 14.05 | 5.81 | 13.62 | 5.05 | 7.41 | 0.85 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.50 | 17.00 | 14.00 | 3.00 | 14.00 | 8.50 | 10.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 21 | 59.70 | 22.33 | 18.00 | 10.00 | 14.00 | 3.33 | 8.87 | 3.17 |
| MOVER_AVWAP_SCALP | kept | 14 | 70.59 | 22.57 | 18.00 | 12.86 | 13.86 | 5.61 | 8.45 | 3.54 |
| MOVER_TREND_PULLBACK | filtered | 514 | 55.75 | 18.02 | 18.15 | 7.80 | 12.63 | 5.23 | 7.71 | 4.52 |
| MOVER_TREND_PULLBACK | kept | 1565 | 76.67 | 19.50 | 18.00 | 8.46 | 13.04 | 5.89 | 8.94 | 4.62 |
| QUIET_COMPRESSION_BREAK | filtered | 294 | 56.23 | 17.63 | 16.04 | 11.56 | 14.07 | 6.13 | 4.20 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 758 | 75.36 | 19.18 | 16.97 | 12.17 | 14.01 | 6.75 | 7.27 | 0.00 |
| SR_FLIP_RETEST | filtered | 335 | 54.02 | 19.35 | 14.45 | 7.16 | 13.70 | 6.49 | 7.00 | 1.52 |
| SR_FLIP_RETEST | kept | 645 | 71.18 | 20.98 | 16.57 | 6.45 | 13.16 | 5.69 | 8.02 | 1.90 |
| TREND_PULLBACK_EMA | kept | 41 | 77.47 | 19.34 | 18.00 | 7.50 | 10.46 | 9.72 | 6.95 | 5.50 |
| VOLUME_SURGE_BREAKOUT | filtered | 35 | 50.29 | 19.29 | 14.00 | 14.14 | 13.14 | 5.60 | 8.09 | 4.43 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 85.00 | 25.00 | 18.00 | 12.00 | 14.00 | 5.00 | 8.00 | 6.00 |
| WHALE_MOMENTUM | filtered | 5 | 34.60 | 25.00 | 8.00 | 12.00 | 12.00 | 8.50 | 0.70 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 62 | 59.48 | 0.00 | 0.00 | 0.00 | 0.00 | 6.97 | 0.00 | 0.00 | 0.00 | **6.97** |
| BREAKDOWN_SHORT | kept | 8 | 76.64 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.40** |
| DIVERGENCE_CONTINUATION | filtered | 304 | 53.48 | 0.00 | 0.00 | 0.05 | 0.00 | 3.69 | 0.00 | 0.00 | 0.00 | **3.74** |
| DIVERGENCE_CONTINUATION | kept | 236 | 70.75 | 0.00 | 0.00 | 0.04 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | **0.09** |
| FAILED_AUCTION_RECLAIM | filtered | 672 | 51.01 | 0.00 | 0.00 | 1.82 | 0.00 | 6.16 | 0.05 | 0.00 | 0.00 | **8.03** |
| FAILED_AUCTION_RECLAIM | kept | 993 | 71.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.29 | 0.00 | 0.00 | 0.00 | **0.29** |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 47.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 70.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 126 | 57.56 | 0.00 | 0.00 | 0.25 | 0.00 | 9.75 | 0.00 | 0.00 | 0.00 | **10.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 79 | 67.99 | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.20** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 21 | 59.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 14 | 70.59 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 514 | 55.75 | 0.00 | 0.00 | 0.92 | 0.00 | 1.54 | 0.00 | 0.00 | 0.00 | **2.46** |
| MOVER_TREND_PULLBACK | kept | 1565 | 76.67 | 0.00 | 0.00 | 0.31 | 0.00 | 0.51 | 0.00 | 0.00 | 0.00 | **0.82** |
| QUIET_COMPRESSION_BREAK | filtered | 294 | 56.23 | 0.00 | 0.00 | 0.00 | 0.00 | 2.07 | 0.00 | 0.00 | 4.29 | **6.36** |
| QUIET_COMPRESSION_BREAK | kept | 758 | 75.36 | 0.00 | 0.00 | 0.00 | 0.00 | 1.78 | 0.00 | 0.00 | 0.02 | **1.80** |
| SR_FLIP_RETEST | filtered | 335 | 54.02 | 0.00 | 0.00 | 0.70 | 0.00 | 6.25 | 0.00 | 0.00 | 1.07 | **8.02** |
| SR_FLIP_RETEST | kept | 645 | 71.18 | 0.00 | 0.00 | 0.03 | 0.00 | 1.06 | 0.00 | 0.00 | 0.02 | **1.11** |
| TREND_PULLBACK_EMA | kept | 41 | 77.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 35 | 50.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 85.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 5 | 34.60 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=1370 (30.4%) | WOULD_LOSE=1436 | WOULD_EXPIRE=1698 | pending (awaiting window)=496

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_floor:DIVERGENCE_CONTINUATION | 82 | 17.1% | 19.0 | 24.2 | -0.06 | **TUNE** |
| context_floor:FAILED_AUCTION_RECLAIM | 791 | 4.2% | 177.0 | 66.0 | +0.14 | **KEEP** |
| context_floor:LIQUIDITY_SWEEP_REVERSAL | 5 | 0.0% | 5.0 | 0.0 | +1.00 | **INSUFFICIENT_SAMPLE** |
| context_floor:MOVER_TREND_PULLBACK | 904 | 65.8% | 102.0 | 791.9 | -0.76 | **DROP** |
| context_floor:QUIET_COMPRESSION_BREAK | 18 | 0.0% | 0.0 | 0.0 | +0.00 | **INSUFFICIENT_SAMPLE** |
| context_floor:SR_FLIP_RETEST | 652 | 33.4% | 265.0 | 274.1 | -0.01 | **TUNE** |
| context_floor:VOLUME_SURGE_BREAKOUT | 17 | 0.0% | 17.0 | 0.0 | +1.00 | **INSUFFICIENT_SAMPLE** |
| dispatch_staleness | 495 | 83.6% | 49.0 | 191.4 | -0.29 | **DROP** |
| level_still_in_play | 337 | 11.9% | 69.0 | 18.1 | +0.15 | **KEEP** |
| min_confidence | 943 | 4.0% | 661.0 | 54.4 | +0.64 | **KEEP** |
| quiet_scalp_block | 198 | 0.0% | 36.0 | 0.0 | +0.18 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 3 | 33.3% | 1.0 | 0.8 | +0.07 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 7 | 28.6% | 5.0 | 1.5 | +0.50 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_MEAN_REVERT | 25 | 20.0% | 19.0 | 9.8 | +0.37 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 27 | 37.0% | 11.0 | 26.9 | -0.59 | **DROP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 32569 across 19 strategies; 732 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 8093 | 19/8074/0 | 60% | +0.17 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+1.27R) | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 6268 | 0/6268/0 | 43% | -0.06 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.29R) | LONDON/MARKDOWN/EXPANDED/BTC_FALLING (-1.00R) |
| FAILED_AUCTION_RECLAIM | 5467 | 13/5454/0 | 48% | -0.02 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | LONDON/MARKDOWN/NORMAL/BTC_FALLING (-1.00R) |
| DIVERGENCE_CONTINUATION | 3372 | 3/3369/0 | 42% | -0.02 | OVERLAP/MARKUP/EXPANDED/BTC_NEUTRAL (+1.46R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_MEAN_REVERT | 2009 | 0/0/2009 | 33% | -0.13 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.91R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| QUIET_COMPRESSION_BREAK | 1768 | 0/1768/0 | 39% | -0.01 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (+2.21R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_RANGE_FADE | 1739 | 0/0/1739 | 36% | +0.13 | OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL (+1.63R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| LIQUIDITY_SWEEP_REVERSAL | 1301 | 1/1300/0 | 35% | -0.10 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_FUNDING_FADE | 970 | 0/0/970 | 34% | -0.40 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL (+0.60R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING (-1.00R) |
| TREND_PULLBACK_EMA | 337 | 0/337/0 | 40% | -0.17 | NY/MARKDOWN/NORMAL/BTC_RISING (+0.32R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 317 | 2/315/0 | 26% | -0.40 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| MOVER_AVWAP_SCALP | 183 | 6/177/0 | 21% | -0.59 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| BREAKDOWN_SHORT | 183 | 1/182/0 | 68% | +0.51 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.34R) |
| MEAN_REVERT | 172 | 0/172/0 | 18% | -0.78 | ASIA/RANGE/NORMAL/BTC_NEUTRAL (+0.15R) | NY/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 143 | 0/0/143 | 46% | -0.11 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| FUNDING_EXTREME_SIGNAL | 124 | 0/124/0 | 38% | +0.04 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| WHALE_MOMENTUM | 114 | 0/114/0 | 16% | -0.36 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| POST_DISPLACEMENT_CONTINUATION | 7 | 0/7/0 | 0% | -1.00 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 1/1/0 | 50% | +0.35 | — | — |

- **Strongest cells**: `QUIET_COMPRESSION_BREAK @ OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL` +2.21R (n=29, STRONG); `FAILED_AUCTION_RECLAIM @ LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL` +1.70R (n=45, STRONG); `SHADOW_RANGE_FADE @ OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL` +1.63R (n=16, STRONG)
- **Weakest cells**: `VOLUME_SURGE_BREAKOUT @ ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP` -1.00R (n=17, NEGATIVE); `MOVER_TREND_PULLBACK @ ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.00R (n=26, NEGATIVE); `DIVERGENCE_CONTINUATION @ ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP` -1.00R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| MOVER_AVWAP_SCALP | 26 | 46% / -0.06R | 26 | 58% / +0.10R | +0.15 | **ATR** |
| SR_FLIP_RETEST | 925 | 45% / -0.06R | 925 | 49% / -0.00R | +0.06 | **ATR** |
| MEAN_REVERT | 26 | 12% / -0.83R | 26 | 8% / -0.88R | -0.05 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 730 | 47% / -0.04R | 730 | 45% / -0.02R | +0.02 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 141 | 47% / -0.02R | 141 | 52% / -0.01R | +0.01 | **ATR** |
| MOVER_TREND_PULLBACK | 650 | 63% / +0.15R | 650 | 68% / +0.14R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 374 | 43% / -0.02R | 374 | 43% / -0.02R | +0.00 | **ATR** |
| DIVERGENCE_CONTINUATION | 155 | 48% / -0.04R | 155 | 54% / -0.04R | +0.00 | **ATR** |
| WHALE_MOMENTUM | 14 | 21% / -0.31R | 14 | 14% / -0.46R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 13 | 46% / +0.10R | 13 | 38% / -0.11R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 12 | 75% / +0.13R | 12 | 75% / +0.16R | — | **MEASURING** |
| BREAKDOWN_SHORT | 6 | 33% / -0.15R | 6 | 33% / -0.04R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 2 | 0% / -1.00R | 2 | 100% / +0.22R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -0.64R | 1 | 0% / -1.00R | — | **MEASURING** |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 14 · alerting: **1** · boot grace active: False
- **ALERT** `range_fade_emission` — 1112 detections since last emission/context-block (emitted_total=0 context_blocked=0) — check gate rejections (streak 35/6) (sustained 35 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=10 fanouts=5 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 64646.70 | 0 |
| candle_coverage | ok | 88/106 symbols with ≥20 15m candles | 0 |
| context_emission_policy | ok | output +9 / upstream +48 | 0 |
| geometry_ab | ok | output +8 / upstream +16 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | backlog 0 detections since last emission | 0 |
| mean_revert_path | ok | output +0 / upstream +16 | 0 |
| range_fade_emission | violating | 1112 detections since last emission/context-block (emitted_total=0 context_blocked=0) — check gate rejections (streak 35/6) | 35 |
| range_fade_path | ok | output +12 / upstream +16 | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| strategy_edge | ok | output +177 / upstream +16 | 0 |
| suppression_audit | ok | output +16 / upstream +48 | 0 |
| tuned_variants | ok | seen=36 stamped=1 skipped=35 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4113123`
- `Path funnel` emissions: `113`
- `Regime distribution` emissions: `113`
- `QUIET_SCALP_BLOCK` events: `482`
- `confidence_gate` events: `6721`
- `free_channel_post` events: `13`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **2**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 2 | 1887 | 1887 | 2319 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **13**

| Source | Count |
|---|---:|
| signal_close | 7 |
| regime_shift | 6 |

- By severity: HIGH=13

## Dependency readiness
- cvd: presence[present=700702] state[populated=700702] buckets[many=700702] sources[none] quality[none]
- funding_rate: presence[absent=46705, present=653997] state[empty=46705, populated=653997] buckets[few=653997, none=46705] sources[none] quality[none]
- liquidation_clusters: presence[absent=409949, present=290753] state[empty=409949, populated=290753] buckets[few=243196, none=409949, some=47557] sources[none] quality[none]
- oi_snapshot: presence[absent=43811, present=656891] state[empty=43811, populated=656891] buckets[many=656526, none=43811, some=365] sources[none] quality[none]
- order_book: presence[absent=196098, present=504604] state[populated=504604, unavailable=196098] buckets[few=504604, none=196098] sources[book_ticker=504604, unavailable=196098] quality[none=196098, top_of_book_only=504604]
- orderblocks: presence[absent=700702] state[empty=700702] buckets[none=700702] sources[not_implemented=700702] quality[none]
- recent_ticks: presence[present=700702] state[populated=700702] buckets[many=700702] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `11.232931137084961` sec
- Median create→first breach: `3947.233320951462` sec
- Median create→terminal: `3949.364492893219` sec
- Median first breach→terminal: `2.131171941757202` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 3 | 3 | 33.3 | 66.7 | 33.3 | 0.0 | -0.6102 | 6232.562227010727 | 6233.38115811348 |
| MOVER_TREND_PULLBACK | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -3.2299 | 1737.139463186264 | 1740.7229549884796 |
| SR_FLIP_RETEST | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.5989 | 3947.233320951462 | 3949.364492893219 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 26174 | 50 | 15991 | 0.0 | 100.0 | 3947.233320951462 | 3949.364492893219 | 10183 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 5809 | 4 | 5765 | 0.0 | 0.0 | None | None | 44 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-101`
- Gating Δ: `19036`
- No-generation Δ: `94481`
- Fast failures Δ: `-2`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -1.0395, "current_avg_pnl": -0.6102, "current_win_rate": 33.3, "previous_avg_pnl": 0.4293, "previous_win_rate": 0.0, "win_rate_delta": 33.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.3818, "current_avg_pnl": -3.2299, "current_win_rate": 0.0, "previous_avg_pnl": -3.6117, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -57, "geometry_changed_delta": 0, "geometry_preserved_delta": -6493, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 3947.23, "median_terminal_delta_sec": 3949.36, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -5, "geometry_changed_delta": 0, "geometry_preserved_delta": -20, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **WHALE_MOMENTUM**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
