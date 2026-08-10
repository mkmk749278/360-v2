# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `5` sec (warning=False)
- Latest performance record age: `1945` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 100 | 100 | 72 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 11417 | 11417 | 10379 | 15 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 114206 | 114211 | 15 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 94072 | 94083 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 93760 | 91007 | 3055 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 94112 | 93522 | 647 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 96772 | 96314 | 480 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 89878 | 89900 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 94171 | 94194 | 10 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 94209 | 91634 | 3666 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 118556 | 121713 | 804 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::MOVER_TREND_PULLBACK | 114229 | 104174 | 14337 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 96422 | 96426 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 94090 | 94105 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 93714 | 93258 | 498 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 95303 | 94026 | 1841 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 93352 | 93587 | 99 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 86805 | 84493 | 2472 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 86971 | 86633 | 401 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 114168 | 114193 | 10 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 89903 | 89899 | 31 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2760 | 2760 | 2200 | 5 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1401 | 1401 | 462 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 6 | 6 | 4 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 13725 | 13725 | 13511 | 14 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 19 | 19 | 8 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 12927 | 12927 | 11320 | 11 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2057 | 2057 | 375 | 48 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 41714 | 41714 | 27568 | 326 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 9 | 9 | 9 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 3568 | 3568 | 2206 | 67 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 5923 | 5923 | 5321 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 288 | 288 | 217 | 3 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2074 | 2074 | 1920 | 15 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 47 | 47 | 0 | 3 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 3493 | 3493 | 98 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=114211): breakout_not_found=56839, basic_filters_failed=39489, move_not_fresh=11921, breakout_stale=4154, retest_proximity_failed=1520, volume_spike_missing=137, ema_alignment_reject=129, move_exhausted=18, missing_fvg_or_orderblock=4
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=94083): cls_disabled_merged_into_lsr=94083
- **EVAL::DIVERGENCE_CONTINUATION** (total=91007): cvd_divergence_failed=33711, basic_filters_failed=32597, h1_trend_not_aligned=16898, ema_alignment_reject=5879, retest_proximity_failed=1072, regime_blocked=492, missing_fvg_or_orderblock=358
- **EVAL::FAILED_AUCTION_RECLAIM** (total=93522): auction_not_detected=53534, basic_filters_failed=31195, regime_blocked=3760, reclaim_hold_failed=3234, tail_too_small=1770, rsi_reject=29
- **EVAL::FUNDING_EXTREME** (total=96314): funding_not_extreme=53939, basic_filters_failed=31575, missing_funding_rate=4456, ema_alignment_reject=4115, rsi_reject=1265, cvd_divergence_failed=451, momentum_reject=417, missing_fvg_or_orderblock=96
- **EVAL::LIQUIDATION_REVERSAL** (total=89900): cascade_threshold_not_met=55409, basic_filters_failed=33328, cvd_divergence_failed=573, rsi_reject=561, missing_fvg_or_orderblock=26, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=94194): no_ma_cross=60592, basic_filters_failed=32624, ma_cross_cooldown=735, ma_cross_htf_misaligned=243
- **EVAL::MEAN_REVERT** (total=91634): no_extension=72345, basic_filters_failed=19274, insufficient_candles=15
- **EVAL::MOVER_AVWAP_SCALP** (total=121713): basic_filters_failed=39711, no_mover_leg=34708, no_avwap_tag=34606, avwap_slope_against=8014, avwap_reclaim_no_volume=2781, no_avwap_reclaim=1691, anchor_too_recent=145, insufficient_candles=57
- **EVAL::MOVER_TREND_PULLBACK** (total=104174): mover_run_too_small=42493, basic_filters_failed=39536, no_reclaim=18010, no_pullback_tag=3888, insufficient_candles=247
- **EVAL::OPENING_RANGE_BREAKOUT** (total=96426): feature_disabled=96426
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=94105): regime_blocked=61066, breakout_not_found=20045, basic_filters_failed=10118, adx_reject=2829, ema_alignment_reject=47
- **EVAL::QUIET_COMPRESSION_BREAK** (total=93258): regime_blocked=36729, compression_not_detected=22522, basic_filters_failed=21058, breakout_not_detected=10397, volume_confirmation_failed=1974, macd_reject=409, rsi_reject=143, missing_fvg_or_orderblock=26
- **EVAL::RANGE_FADE** (total=94026): no_range_edge=74663, basic_filters_failed=19256, insufficient_candles=107
- **EVAL::SR_FLIP_RETEST** (total=93587): flip_close_not_confirmed=53406, basic_filters_failed=31166, regime_blocked=3750, retest_out_of_zone=2175, long_break_volume_thin=1434, h1_break_not_confirmed=619, reclaim_hold_failed=573, whipsaw_flip=190, long_acceptance_not_held=130, ema_alignment_reject=96, wick_quality_failed=47, missing_fvg_or_orderblock=1
- **EVAL::STANDARD** (total=84493): momentum_reject=28941, adx_reject=17000, basic_filters_failed=15385, sweeps_not_detected=10382, macd_reject=5700, ema_alignment_reject=3970, htf_poi_unanchored=2798, rsi_reject=220, invalid_sl_geometry=93, mtf_reject=4
- **EVAL::TREND_PULLBACK** (total=86633): h1_trend_not_aligned=22357, basic_filters_failed=21529, ema_alignment_reject=12455, h1_pullback_not_confirmed=10308, ema_not_tested_prev=7143, no_ema_reclaim_close=4737, body_conviction_fail=3020, rsi_reject=2665, regime_blocked=602, prev_already_above_emas=575, no_prev_high_break=352, prev_already_below_emas=325, no_prev_low_break=304, momentum_flat=153, momentum_reject=57, missing_fvg_or_orderblock=40, ema21_not_tagged=11
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=114193): breakout_not_found=56403, basic_filters_failed=39488, move_not_fresh=12469, breakout_stale=4068, retest_proximity_failed=1434, volume_spike_missing=201, ema_alignment_reject=105, move_exhausted=12, missing_fvg_or_orderblock=11, rsi_reject=2
- **EVAL::WHALE_MOMENTUM** (total=89899): momentum_reject=62393, recent_ticks_insufficient=14709, basic_filters_failed=12794, rsi_reject=3

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=30): execution:overextended=30
- **DIVERGENCE_CONTINUATION** (total=264): setup_compat:regime_VOLATILE_UNSUITABLE=264
- **FAILED_AUCTION_RECLAIM** (total=1352): execution:overextended=807, setup_compat:regime_STRONG_TREND=312, context_floor=205, setup_compat:regime_VOLATILE_UNSUITABLE=28
- **FUNDING_EXTREME_SIGNAL** (total=1146): execution:trigger_not_confirmed=1115, context_floor=31
- **LIQUIDATION_REVERSAL** (total=6): execution:trigger_not_confirmed=6
- **LIQUIDITY_SWEEP_REVERSAL** (total=4402): execution:overextended=2194, execution:trigger_not_confirmed=1353, setup_compat:regime_STRONG_TREND=855
- **MA_CROSS_TREND_SHIFT** (total=21): execution:trigger_not_confirmed=8, setup_compat:regime_DIRTY_RANGE=7, setup_compat:regime_CLEAN_RANGE=5, execution:overextended=1
- **MEAN_REVERT** (total=6755): setup_compat:regime_STRONG_TREND=3533, setup_compat:regime_WEAK_TREND=1830, execution:overextended=1383, entry_quality=9
- **MOVER_AVWAP_SCALP** (total=1638): execution:overextended=943, execution:trigger_not_confirmed=397, entry_quality=298
- **MOVER_TREND_PULLBACK** (total=28660): execution:overextended=17945, execution:trigger_not_confirmed=7936, entry_quality=2779
- **POST_DISPLACEMENT_CONTINUATION** (total=6): execution:overextended=6
- **QUIET_COMPRESSION_BREAK** (total=691): execution:trigger_not_confirmed=691
- **RANGE_FADE** (total=2034): setup_compat:regime_STRONG_TREND=823, setup_compat:regime_WEAK_TREND=526, setup_compat:regime_VOLATILE_UNSUITABLE=306, execution:overextended=252, context_edge=90, setup_compat:regime_BREAKOUT_EXPANSION=37
- **TREND_PULLBACK_EMA** (total=1813): setup_compat:regime_CLEAN_RANGE=1407, setup_compat:regime_DIRTY_RANGE=272, setup_compat:regime_VOLATILE_UNSUITABLE=119, entry_quality=15
- **VOLUME_SURGE_BREAKOUT** (total=61): context_floor=35, execution:overextended=26
- **WHALE_MOMENTUM** (total=3395): execution:trigger_not_confirmed=3395

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 253714 | 38.8% |
| QUIET | 155016 | 23.7% |
| TRENDING_UP | 100547 | 15.4% |
| TRENDING_DOWN | 96685 | 14.8% |
| VOLATILE | 48486 | 7.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **295**
- Average confidence gap to threshold: **12.03** (samples=295) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=51, ETHUSDT=36, SOLUSDT=19, ZECUSDT=18, DOGEUSDT=13, HYPEUSDT=12, ENAUSDT=12, INJUSDT=10, ADAUSDT=10, LINKUSDT=10

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 22 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 6 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 120 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 7 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 120 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 52 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 22 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 66 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 15 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 4 |
| FUNDING_EXTREME_SIGNAL | filtered | execution_component_floor | 1 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 2 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 111 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 15 |
| MEAN_REVERT | filtered | min_confidence | 8 |
| MEAN_REVERT | kept | min_confidence_pass | 38 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 230 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 32 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 6 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 490 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1019 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 6 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 5233 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 198 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 27 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 491 |
| SR_FLIP_RETEST | filtered | min_confidence | 17 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 29 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 35 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 76 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 6 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 32 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 22 | 50.47 | 65.00 | 14.53 | 19.22 | 17.62 | 20.00 | 3.89 | 23.65 |
| BREAKDOWN_SHORT | kept | 6 | 82.33 | 65.00 | -17.33 | 18.02 | 14.98 | 20.00 | 5.00 | 1.50 |
| DIVERGENCE_CONTINUATION | filtered | 127 | 55.28 | 63.28 | 8.00 | 20.64 | 19.54 | 18.52 | 1.24 | 11.87 |
| DIVERGENCE_CONTINUATION | kept | 120 | 70.06 | 65.00 | -5.06 | 20.62 | 19.69 | 18.01 | 2.35 | 0.43 |
| FAILED_AUCTION_RECLAIM | filtered | 74 | 55.62 | 63.81 | 8.19 | 20.79 | 18.63 | 20.00 | 1.94 | 3.85 |
| FAILED_AUCTION_RECLAIM | kept | 66 | 70.04 | 65.00 | -5.04 | 21.42 | 19.50 | 20.00 | 3.11 | 0.18 |
| FUNDING_EXTREME_SIGNAL | filtered | 20 | 47.04 | 62.25 | 15.21 | 20.34 | 14.17 | 17.00 | 3.00 | 4.47 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 65.70 | 65.00 | -0.70 | 18.30 | 14.00 | 18.50 | 4.00 | 2.50 |
| LIQUIDATION_REVERSAL | filtered | 2 | 69.20 | 10.00 | -59.20 | 20.70 | 8.00 | 20.00 | 6.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 111 | 69.25 | 65.00 | -4.25 | 20.02 | 17.80 | 17.28 | 1.77 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.00 | 65.00 | -5.00 | 21.00 | 19.85 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 23 | 50.92 | 63.26 | 12.34 | 21.88 | 17.60 | 16.90 | 0.00 | 7.74 |
| MEAN_REVERT | kept | 38 | 69.24 | 65.00 | -4.24 | 19.65 | 14.67 | 17.73 | 0.00 | 0.13 |
| MOVER_AVWAP_SCALP | filtered | 268 | 56.96 | 58.32 | 1.36 | 20.79 | 14.52 | 15.80 | 3.79 | 5.95 |
| MOVER_AVWAP_SCALP | kept | 490 | 77.94 | 65.00 | -12.94 | 20.24 | 16.33 | 15.80 | 4.19 | 0.56 |
| MOVER_TREND_PULLBACK | filtered | 1025 | 56.78 | 63.43 | 6.65 | 19.91 | 18.36 | 15.80 | 4.20 | 15.79 |
| MOVER_TREND_PULLBACK | kept | 5233 | 76.05 | 65.00 | -11.05 | 19.99 | 18.41 | 15.80 | 4.42 | 1.29 |
| QUIET_COMPRESSION_BREAK | filtered | 225 | 53.52 | 64.95 | 11.43 | 20.81 | 19.67 | 20.00 | 0.00 | 12.02 |
| QUIET_COMPRESSION_BREAK | kept | 491 | 76.03 | 65.00 | -11.03 | 20.95 | 19.50 | 20.00 | 0.00 | -1.11 |
| SR_FLIP_RETEST | filtered | 17 | 49.33 | 61.18 | 11.85 | 20.93 | 20.00 | 15.20 | 1.85 | 22.02 |
| SR_FLIP_RETEST | kept | 29 | 68.94 | 65.00 | -3.94 | 20.49 | 20.00 | 15.82 | 1.64 | 1.48 |
| TREND_PULLBACK_EMA | filtered | 40 | 56.03 | 64.12 | 8.09 | 20.14 | 19.57 | 18.15 | 4.64 | 18.93 |
| TREND_PULLBACK_EMA | kept | 76 | 78.18 | 65.00 | -13.18 | 20.31 | 19.51 | 17.75 | 5.26 | -0.27 |
| VOLUME_SURGE_BREAKOUT | kept | 6 | 79.77 | 65.00 | -14.77 | 18.08 | 16.23 | 20.00 | 4.92 | 2.00 |
| WHALE_MOMENTUM | filtered | 32 | 51.35 | 65.00 | 13.65 | 20.52 | 14.00 | 17.00 | 0.00 | 14.73 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 22 | 50.47 | 15.91 | 16.36 | 13.23 | 12.64 | 5.00 | 7.10 | 3.89 |
| BREAKDOWN_SHORT | kept | 6 | 82.33 | 19.67 | 18.00 | 12.50 | 14.00 | 5.00 | 9.67 | 5.00 |
| DIVERGENCE_CONTINUATION | filtered | 127 | 55.28 | 22.10 | 11.39 | 5.88 | 12.41 | 5.65 | 8.48 | 1.24 |
| DIVERGENCE_CONTINUATION | kept | 120 | 70.06 | 22.67 | 15.08 | 4.38 | 12.30 | 6.40 | 8.99 | 2.35 |
| FAILED_AUCTION_RECLAIM | filtered | 74 | 55.62 | 20.57 | 16.81 | 5.31 | 13.85 | 7.28 | 5.68 | 1.94 |
| FAILED_AUCTION_RECLAIM | kept | 66 | 70.04 | 24.03 | 14.55 | 5.14 | 10.98 | 6.02 | 8.21 | 3.11 |
| FUNDING_EXTREME_SIGNAL | filtered | 20 | 47.04 | 23.80 | 8.00 | 8.40 | 14.45 | 6.67 | 2.18 | 3.00 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 65.70 | 25.00 | 8.00 | 9.00 | 12.00 | 8.50 | 1.70 | 4.00 |
| LIQUIDATION_REVERSAL | filtered | 2 | 69.20 | 25.00 | 8.00 | 15.00 | 8.00 | 5.00 | 2.20 | 6.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 111 | 69.25 | 23.02 | 14.72 | 3.30 | 13.12 | 6.53 | 6.80 | 1.77 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.00 | 21.00 | 14.00 | 7.50 | 13.50 | 5.00 | 9.00 | 0.00 |
| MEAN_REVERT | filtered | 23 | 50.92 | 22.48 | 18.00 | 8.48 | 12.52 | 5.65 | 3.27 | 0.00 |
| MEAN_REVERT | kept | 38 | 69.24 | 24.26 | 15.79 | 8.84 | 11.26 | 5.57 | 4.04 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 268 | 56.96 | 17.88 | 18.02 | 9.72 | 13.52 | 4.93 | 6.42 | 3.79 |
| MOVER_AVWAP_SCALP | kept | 490 | 77.94 | 19.35 | 18.04 | 9.97 | 13.41 | 5.63 | 8.45 | 4.19 |
| MOVER_TREND_PULLBACK | filtered | 1025 | 56.78 | 18.16 | 18.00 | 7.80 | 12.45 | 5.31 | 8.93 | 4.20 |
| MOVER_TREND_PULLBACK | kept | 5233 | 76.05 | 19.19 | 18.04 | 8.17 | 13.15 | 5.71 | 8.85 | 4.42 |
| QUIET_COMPRESSION_BREAK | filtered | 225 | 53.52 | 18.00 | 17.52 | 12.07 | 14.08 | 6.21 | 3.22 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 491 | 76.03 | 19.02 | 17.76 | 11.29 | 14.00 | 5.40 | 8.87 | 0.00 |
| SR_FLIP_RETEST | filtered | 17 | 49.33 | 21.00 | 18.00 | 3.71 | 13.65 | 5.41 | 7.74 | 1.85 |
| SR_FLIP_RETEST | kept | 29 | 68.94 | 19.41 | 18.00 | 4.34 | 13.79 | 6.09 | 7.77 | 1.64 |
| TREND_PULLBACK_EMA | filtered | 40 | 56.03 | 14.38 | 18.00 | 7.69 | 14.00 | 7.70 | 8.55 | 4.64 |
| TREND_PULLBACK_EMA | kept | 76 | 78.18 | 18.83 | 18.00 | 7.54 | 14.50 | 5.89 | 9.04 | 5.26 |
| VOLUME_SURGE_BREAKOUT | kept | 6 | 79.77 | 19.67 | 17.33 | 14.50 | 11.50 | 6.50 | 7.35 | 4.92 |
| WHALE_MOMENTUM | filtered | 32 | 51.35 | 19.50 | 8.00 | 12.66 | 12.84 | 7.08 | 7.88 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 22 | 50.47 | 0.00 | 0.00 | 2.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.84** |
| BREAKDOWN_SHORT | kept | 6 | 82.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 127 | 55.28 | 0.00 | 0.00 | 0.87 | 0.00 | 1.34 | 0.00 | 0.00 | 0.00 | **2.21** |
| DIVERGENCE_CONTINUATION | kept | 120 | 70.06 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.08** |
| FAILED_AUCTION_RECLAIM | filtered | 74 | 55.62 | 0.00 | 0.00 | 0.00 | 0.00 | 2.04 | 0.24 | 0.00 | 0.00 | **2.28** |
| FAILED_AUCTION_RECLAIM | kept | 66 | 70.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 20 | 47.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.72 | 0.00 | 0.00 | 0.00 | **0.72** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 65.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 2 | 69.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 111 | 69.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 23 | 50.92 | 0.00 | 0.00 | 0.70 | 0.00 | 0.00 | 0.00 | 0.00 | 7.04 | **7.74** |
| MEAN_REVERT | kept | 38 | 69.24 | 0.00 | 0.00 | 0.13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.13** |
| MOVER_AVWAP_SCALP | filtered | 268 | 56.96 | 0.00 | 0.00 | 3.18 | 0.00 | 0.00 | 0.00 | 0.00 | 1.28 | **4.46** |
| MOVER_AVWAP_SCALP | kept | 490 | 77.94 | 0.00 | 0.00 | 0.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.12 | **0.69** |
| MOVER_TREND_PULLBACK | filtered | 1025 | 56.78 | 1.16 | 0.00 | 1.85 | 0.00 | 0.74 | 0.00 | 0.00 | 0.00 | **3.75** |
| MOVER_TREND_PULLBACK | kept | 5233 | 76.05 | 0.08 | 0.00 | 0.96 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | **1.26** |
| QUIET_COMPRESSION_BREAK | filtered | 225 | 53.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.23 | 0.32 | 0.00 | 7.44 | **7.99** |
| QUIET_COMPRESSION_BREAK | kept | 491 | 76.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 | 0.00 | 0.13 | **0.19** |
| SR_FLIP_RETEST | filtered | 17 | 49.33 | 0.00 | 0.00 | 3.67 | 0.00 | 1.41 | 0.35 | 0.00 | 0.00 | **5.43** |
| SR_FLIP_RETEST | kept | 29 | 68.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.41 | 0.00 | 0.00 | 0.00 | **0.41** |
| TREND_PULLBACK_EMA | filtered | 40 | 56.03 | 0.00 | 0.00 | 0.00 | 0.00 | 2.70 | 0.00 | 0.00 | 0.00 | **2.70** |
| TREND_PULLBACK_EMA | kept | 76 | 78.18 | 0.00 | 0.00 | 0.11 | 0.00 | 0.57 | 0.00 | 0.00 | 0.00 | **0.68** |
| VOLUME_SURGE_BREAKOUT | kept | 6 | 79.77 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 32 | 51.35 | 0.00 | 0.00 | 0.00 | 0.00 | 2.70 | 0.00 | 0.00 | 0.00 | **2.70** |

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
- Outcomes recorded: **131161 held of 222147 seen** across 21 strategies; 2955 cells past the sample floor; **923 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 30630 | 225/30405/0 | 51% | -0.03 | ASIA/MARKUP/CASCADE/BTC_RISING/MIDCAP (+1.24R) | ASIA/MARKDOWN/CASCADE/BTC_RISING (-1.20R) |
| FAILED_AUCTION_RECLAIM | 17075 | 24/17051/0 | 51% | -0.01 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16550 | 1/16549/0 | 48% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 11688 | 4/11684/0 | 45% | -0.10 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.37R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 9342 | 0/9342/0 | 51% | -0.04 | NY/QUIET/EXPANDED/BTC_RISING/ALTCOIN (+1.21R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 8416 | 28/8388/0 | 34% | -0.35 | LONDON/DISTRIBUTION/EXPANDED/BTC_RISING (+1.12R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| TREND_PULLBACK_EMA | 4786 | 2/4784/0 | 50% | -0.21 | NY/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.07R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.19R) |
| SHADOW_MEAN_REVERT | 4767 | 0/0/4767 | 42% | -0.09 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.73R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 4718 | 11/4707/0 | 47% | -0.19 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.54R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_RANGE_FADE | 4326 | 0/0/4326 | 38% | +0.06 | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.82R) | OVERLAP/QUIET/NORMAL/BTC_RISING (-1.26R) |
| MEAN_REVERT | 4080 | 0/4080/0 | 72% | +0.44 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.29R) |
| SHADOW_FUNDING_FADE | 4000 | 0/0/4000 | 38% | -0.34 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.20R) | NY/MARKUP/NORMAL/BTC_RISING (-0.95R) |
| RANGE_FADE | 3505 | 0/3505/0 | 26% | -0.58 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.87R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-1.38R) |
| VOLUME_SURGE_BREAKOUT | 2488 | 15/2473/0 | 43% | +0.07 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+2.68R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2278 | 4/2274/0 | 30% | -0.48 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.34R) |
| WHALE_MOMENTUM | 1458 | 0/1458/0 | 45% | -0.26 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (-0.81R) |
| SHADOW_CASCADE_REVERSAL | 482 | 0/0/482 | 48% | -0.16 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.03R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.76R) |
| BREAKDOWN_SHORT | 409 | 9/400/0 | 48% | +0.02 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.67R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.08R) |
| LIQUIDATION_REVERSAL | 74 | 0/74/0 | 57% | -0.55 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) |
| POST_DISPLACEMENT_CONTINUATION | 69 | 0/69/0 | 90% | +0.76 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 20 | 1/19/0 | 35% | -0.38 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.87R (n=27, STRONG); `VOLUME_SURGE_BREAKOUT @ NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP` +2.68R (n=30, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE); `RANGE_FADE @ ASIA/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP` -1.38R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 104 | 36% / -0.40R | 104 | 58% / -0.08R | +0.32 | **ATR** |
| TREND_PULLBACK_EMA | 152 | 41% / -0.32R | 152 | 45% / -0.14R | +0.19 | **ATR** |
| MOVER_AVWAP_SCALP | 491 | 38% / -0.24R | 491 | 41% / -0.13R | +0.11 | **ATR** |
| SR_FLIP_RETEST | 2772 | 46% / -0.20R | 2772 | 49% / -0.10R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 841 | 47% / -0.12R | 841 | 53% / -0.06R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 687 | 50% / -0.18R | 687 | 54% / -0.13R | +0.05 | **ATR** |
| WHALE_MOMENTUM | 108 | 49% / -0.25R | 108 | 48% / -0.30R | -0.05 | **FIXED** |
| MOVER_TREND_PULLBACK | 3754 | 51% / -0.06R | 3754 | 54% / -0.01R | +0.05 | **ATR** |
| MEAN_REVERT | 407 | 53% / -0.01R | 407 | 49% / +0.02R | +0.04 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 78 | 40% / -0.01R | 78 | 50% / -0.04R | -0.04 | **FIXED** |
| RANGE_FADE | 225 | 18% / -0.68R | 225 | 20% / -0.64R | +0.03 | **ATR** |
| BREAKDOWN_SHORT | 19 | 26% / -0.34R | 19 | 26% / -0.31R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1416 | 45% / -0.13R | 1416 | 45% / -0.15R | -0.02 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 2272 | 47% / -0.11R | 2272 | 47% / -0.11R | -0.00 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 9 | 33% / -0.27R | 9 | 33% / -0.27R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 71% / +0.23R | 7 | 71% / +0.04R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 6 | 33% / -0.86R | 6 | 33% / -0.51R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 5205 | 30% | -0.13R | 275 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 481 | 39% | -0.14R | 126 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 31 | 58% | +0.03R | 18 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1229 | 28% / -1.69R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 18 | 22% / -0.74R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 4175 | 39% / -0.17R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 971 | 32% / -0.57R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 81 | 23% / -0.76R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 664 | 31% / -1.66R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 913 | 35% / -0.16R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 322 | 42% / -1.12R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 119 | 29% / -1.22R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 174 | 28% / -0.74R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 496 | 30% / -0.30R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 11 | 27% / -0.38R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 143 | 38% / -0.26R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 60 | 42% / -0.15R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 5 | 20% / -0.91R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 7 | 14% / -1.48R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 30 | 47% / -0.36R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 45 · alerting: **6** · boot grace active: False
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 117/6) (sustained 117 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 3719x (gate reads 0x, withheld 0x — refusal dark); last BANANAS31USDT age=5051.7s (streak 53/6) (sustained 53 cycles)
- **ALERT** `edge_reconciliation` — MOVER_AVWAP_SCALP realized−counterfactual=+0.44R (bound 0.3) (streak 117/6) (sustained 117 cycles)
- **ALERT** `mean_revert_emission` — 381 detections since last emission (emitted_total=3) — and the POST-SCORING blocked candidates measure +0.44R over n=4080, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 9/6) (sustained 9 cycles)
- **ALERT** `tuned_variants` — 52 non-stamps — atr_arm_uncomputable=52 (seen=3816 stamped=400 skipped=3364) (streak 106/6) (sustained 106 cycles)
- **ALERT** `auto_dispatch` — 18 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: tier=18) (streak 90/3) (sustained 90 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 14113999 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 12 arms current, none stalled; covering 20/20 signals (100%) | 0 |
| auto_dispatch | violating | 18 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: tier=18) (streak 90/3) | 90 |
| btc_reference | ok | BTC ref 64988.00 | 0 |
| candle_coverage | ok | 104/117 symbols with ≥20 15m candles, 91/117 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 921 dup bars, 0 undedupable; ws 0 out-of-order, 251 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 117/6) | 117 |
| context_emission_policy | ok | output +71 / upstream +31 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 27/27 signals (100%) | 0 |
| dark_resolution | ok | 60 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 45/45 signals (100%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 3103356 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.44R (bound 0.3) (streak 117/6) | 117 |
| emission_controller | ok | last cycle 1031s ago; live_overrides=26 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=14 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4106 stamps (MEAN_REVERT=414, MOVER_AVWAP_SCALP=158, MOVER_TREND_PULLBACK=3095, RANGE_FADE=290, TREND_PULLBACK_EMA=149), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 3/6) | 3 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +3 / upstream +308 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 381 detections since last emission (emitted_total=3) — and the POST-SCORING blocked candidates measure +0.44R over n=4080, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 9/6) | 9 |
| mean_revert_path | ok | output +22 / upstream +308 | 0 |
| mover_admission_metadata | ok | 854 symbols known, 153 marked TRADIFI_PERPETUAL | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 360963 evicted (sampled: execution:overextended 400/132799, execution:trigger_not_confirmed 400/125889, setup_compat:regime_STRONG_TREND 400/44558) | 0 |
| price_action_lane | ok | 327625 evaluated, 150 emitted; layer1 150 stamped / 0 blind; cooldown=22601, delta_opposed=28844, no_footprint=121844, no_opposing_target=2059, no_sweep=125188, rr_below_floor=26939 | 0 |
| promoted_pair_integrity | ok | 24/24 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.58R over n=3505 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +31 / upstream +308 | 0 |
| sar_alignment_crosscheck | ok | 345/10815 disagreed (3.2%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +308 | 0 |
| sar_hold_arm | ok | 41 held arms settled, 2 unscored, 15 still walking (14 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 25/83 unfetchable (30%); top cause: gap or duplicate bar in the 15m window; symbols: 1000CATUSDT, AKEUSDT, BSBUSDT, CAPUSDT, ESPORTSUSDT +5 more | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 14 current): BANANAS31USDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 5/12) | 5 |
| sar_refresh_budget | ok | 1 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 483 records await one (58 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| setup_tf_resolver | ok | 91091 resolutions, 60124 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| stale_tf_scoring | violating | scored on stale TF 3719x (gate reads 0x, withheld 0x — refusal dark); last BANANAS31USDT age=5051.7s (streak 53/6) | 53 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +108 / upstream +308 | 0 |
| structural_snap | ok | 1935/1935 measured, 4 blind, 0 levels moved (refusals: redetect_cooldown=1182) | 0 |
| structural_veto_lane | ok | 1521 stamped; 0 with no readable level book, 160 with clear air ahead, 1059 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +308 / upstream +31 | 0 |
| tuned_variants | violating | 52 non-stamps — atr_arm_uncomputable=52 (seen=3816 stamped=400 skipped=3364) (streak 106/6) | 106 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2952184`
- `Path funnel` emissions: `75`
- `Regime distribution` emissions: `75`
- `QUIET_SCALP_BLOCK` events: `295`
- `confidence_gate` events: `8545`
- `free_channel_post` events: `41`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **6**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 6838 | 6838 | 6838 | 0 |
| futures_aggtrade | 3 | 1761 | 1761 | 9635 | 0 |
| futures_depth | 1 | 3509 | 3509 | 3509 | 0 |
| futures_liq | 1 | 15220 | 15220 | 15220 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **41**

| Source | Count |
|---|---:|
| signal_close | 34 |
| regime_shift | 7 |

- By severity: HIGH=41

## Dependency readiness
- cvd: presence[present=483598] state[populated=483598] buckets[many=483546, some=52] sources[none] quality[none]
- funding_rate: presence[absent=66796, present=416802] state[empty=66796, populated=416802] buckets[few=416802, none=66796] sources[none] quality[none]
- liquidation_clusters: presence[absent=276284, present=207314] state[empty=276284, populated=207314] buckets[few=166578, none=276284, some=40736] sources[none] quality[none]
- oi_snapshot: presence[absent=64821, present=418777] state[empty=64821, populated=418777] buckets[many=418777, none=64821] sources[none] quality[none]
- order_book: presence[absent=140951, present=342647] state[populated=342647, unavailable=140951] buckets[few=342647, none=140951] sources[book_ticker=342647, unavailable=140951] quality[none=140951, top_of_book_only=342647]
- orderblocks: presence[absent=483598] state[empty=483598] buckets[none=483598] sources[measured_dark=483598] quality[none]
- recent_ticks: presence[absent=1003, present=482595] state[empty=1003, populated=482595] buckets[many=482595, none=1003] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.3675185441970825` sec
- Median create→first breach: `2649.6101315021515` sec
- Median create→terminal: `2656.9568705558777` sec
- Median first breach→terminal: `4.472410440444946` sec
- Fast-failure buckets: `{"under_120s": {"count": 5, "pct": 14.7}, "under_180s": {"count": 6, "pct": 17.6}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 3, "pct": 8.8}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.9}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 2.7029462851899164 | 3.0 | 0.9009820950633055 | 0 | 1 |
| MOVER_AVWAP_SCALP | 1 | 1 | 3.4435017995165227 | 2.401879970414201 | 1.4336693931140512 | 1 | 0 |
| MOVER_TREND_PULLBACK | 31 | 31 | 4.041639019420272 | 3.0 | 1.3472130064734238 | 27 | 4 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 2.8032923774305036 | 3.0 | 0.9344307924768346 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 4.0544 | 1432.5333211421967 | 1437.0599520206451 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.4019 | 342.9044589996338 | 346.52802205085754 |
| MOVER_TREND_PULLBACK | 31 | 31 | 0.0 | 35.5 | 0.0 | 0.0 | 0.5748 | 2861.9074618816376 | 3058.230187177658 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.8033 | 2565.7396709918976 | 2567.2834470272064 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 288 | 3 | 217 | 0.0 | 0.0 | None | None | 71 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2074 | 15 | 1920 | 0.0 | 0.0 | None | None | 154 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `66`
- Gating Δ: `-16001`
- No-generation Δ: `-94050`
- Fast failures Δ: `5`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.5257, "current_avg_pnl": 0.5748, "current_win_rate": 0.0, "previous_avg_pnl": 1.1005, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 20, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": -95, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
