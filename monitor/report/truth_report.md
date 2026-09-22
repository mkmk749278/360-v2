# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `305` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 364 | 364 | 262 | 3 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 8344 | 8344 | 8131 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 73903 | 73846 | 78 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 55409 | 55409 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 55166 | 53623 | 1775 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 55426 | 54795 | 668 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 58259 | 58139 | 136 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 47148 | 47157 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 55468 | 55480 | 4 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 55487 | 52976 | 3597 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 80945 | 85614 | 1617 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 73932 | 61662 | 19236 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 57916 | 57916 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 55416 | 55400 | 24 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 55146 | 55117 | 43 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 56577 | 55350 | 1677 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 54786 | 55040 | 81 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 44162 | 40308 | 4090 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 44401 | 43961 | 496 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 73864 | 73829 | 73 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 47162 | 47172 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2499 | 2499 | 2465 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 382 | 382 | 364 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 24 | 24 | 24 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 22078 | 22078 | 22020 | 6 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 8 | 8 | 7 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 11197 | 11197 | 11067 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 4831 | 4831 | 4497 | 17 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 59872 | 59872 | 58452 | 115 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 47 | 47 | 47 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 523 | 523 | 453 | 3 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4950 | 4950 | 4932 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 390 | 390 | 371 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2709 | 2709 | 2656 | 5 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 307 | 307 | 307 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=73846): breakout_not_found=46023, basic_filters_failed=18091, move_not_fresh=5362, breakout_stale=3066, retest_proximity_failed=931, volume_spike_missing=349, move_exhausted=18, missing_fvg_or_orderblock=6
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=55409): cls_disabled_merged_into_lsr=55409
- **EVAL::DIVERGENCE_CONTINUATION** (total=53623): cvd_divergence_failed=29564, basic_filters_failed=11348, h1_trend_not_aligned=8724, ema_alignment_reject=2960, retest_proximity_failed=813, missing_fvg_or_orderblock=214
- **EVAL::FAILED_AUCTION_RECLAIM** (total=54795): auction_not_detected=35194, basic_filters_failed=10339, regime_blocked=4263, reclaim_hold_failed=2644, tail_too_small=2319, rsi_reject=36
- **EVAL::FUNDING_EXTREME** (total=58139): funding_not_extreme=44156, basic_filters_failed=11829, ema_alignment_reject=875, missing_funding_rate=722, rsi_reject=271, cvd_divergence_failed=143, momentum_reject=127, missing_fvg_or_orderblock=16
- **EVAL::LIQUIDATION_REVERSAL** (total=47157): cascade_threshold_not_met=34448, basic_filters_failed=11932, rsi_reject=418, cvd_divergence_failed=334, missing_fvg_or_orderblock=20, volume_spike_missing=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=55480): no_ma_cross=43273, basic_filters_failed=11360, ma_cross_cooldown=458, ma_cross_htf_misaligned=280, ma_cross_htf_unconfirmed=109
- **EVAL::MEAN_REVERT** (total=52976): no_extension=42079, basic_filters_failed=10897
- **EVAL::MOVER_AVWAP_SCALP** (total=85614): no_avwap_tag=39012, basic_filters_failed=18215, no_mover_leg=14104, avwap_slope_against=8524, avwap_reclaim_no_volume=3670, no_avwap_reclaim=2057, anchor_too_recent=32
- **EVAL::MOVER_TREND_PULLBACK** (total=61662): mover_run_too_small=20452, no_reclaim=19824, basic_filters_failed=18163, no_pullback_tag=3223
- **EVAL::OPENING_RANGE_BREAKOUT** (total=57916): feature_disabled=57916
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=55400): regime_blocked=37669, breakout_not_found=15029, basic_filters_failed=2289, adx_reject=377, ema_alignment_reject=36
- **EVAL::QUIET_COMPRESSION_BREAK** (total=55117): compression_not_detected=24447, regime_blocked=21919, basic_filters_failed=8038, breakout_not_detected=598, volume_confirmation_failed=105, missing_fvg_or_orderblock=10
- **EVAL::RANGE_FADE** (total=55350): no_range_edge=44448, basic_filters_failed=10902
- **EVAL::SR_FLIP_RETEST** (total=55040): flip_close_not_confirmed=34405, basic_filters_failed=10322, regime_blocked=4247, long_break_volume_thin=2417, retest_out_of_zone=1773, h1_break_not_confirmed=1117, reclaim_hold_failed=497, long_acceptance_not_held=123, whipsaw_flip=73, ema_alignment_reject=47, wick_quality_failed=19
- **EVAL::STANDARD** (total=40308): adx_reject=9863, momentum_reject=8136, basic_filters_failed=7708, ema_alignment_reject=4955, macd_reject=4594, sweeps_not_detected=4042, htf_poi_unanchored=905, rsi_reject=79, invalid_sl_geometry=26
- **EVAL::TREND_PULLBACK** (total=43961): h1_trend_not_aligned=10240, ema_alignment_reject=8382, basic_filters_failed=6594, ema_not_tested_prev=5496, h1_pullback_not_confirmed=5335, no_ema_reclaim_close=3484, body_conviction_fail=1582, rsi_reject=1385, prev_already_above_emas=765, no_prev_high_break=321, momentum_flat=124, prev_already_below_emas=104, no_prev_low_break=64, ema21_not_tagged=53, missing_fvg_or_orderblock=18, momentum_reject=14
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=73829): breakout_not_found=38944, basic_filters_failed=18090, move_not_fresh=10213, breakout_stale=4139, retest_proximity_failed=2047, volume_spike_missing=351, missing_fvg_or_orderblock=45
- **EVAL::WHALE_MOMENTUM** (total=47172): momentum_reject=33429, recent_ticks_insufficient=9410, basic_filters_failed=4333

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=26): execution:overextended=26
- **DIVERGENCE_CONTINUATION** (total=234): setup_compat:regime_VOLATILE_UNSUITABLE=193, setup_compat:regime_BREAKOUT_EXPANSION=41
- **FAILED_AUCTION_RECLAIM** (total=1338): execution:overextended=724, setup_compat:regime_STRONG_TREND=528, setup_compat:regime_VOLATILE_UNSUITABLE=70, context_floor=16
- **FUNDING_EXTREME_SIGNAL** (total=296): execution:trigger_not_confirmed=296
- **LIQUIDATION_REVERSAL** (total=24): execution:trigger_not_confirmed=24
- **LIQUIDITY_SWEEP_REVERSAL** (total=7421): setup_compat:regime_STRONG_TREND=3199, execution:overextended=2395, execution:trigger_not_confirmed=1827
- **MA_CROSS_TREND_SHIFT** (total=4): setup_compat:regime_DIRTY_RANGE=2, setup_compat:regime_CLEAN_RANGE=1, execution:overextended=1
- **MEAN_REVERT** (total=8331): setup_compat:regime_STRONG_TREND=4394, setup_compat:regime_WEAK_TREND=2669, execution:overextended=1268
- **MOVER_AVWAP_SCALP** (total=1959): execution:overextended=1455, execution:trigger_not_confirmed=418, entry_quality=86
- **MOVER_TREND_PULLBACK** (total=22053): execution:trigger_not_confirmed=11850, execution:overextended=9988, entry_quality=215
- **QUIET_COMPRESSION_BREAK** (total=16): execution:trigger_not_confirmed=16
- **RANGE_FADE** (total=3916): setup_compat:regime_STRONG_TREND=2068, setup_compat:regime_WEAK_TREND=1147, setup_compat:regime_VOLATILE_UNSUITABLE=456, execution:overextended=233, setup_compat:regime_BREAKOUT_EXPANSION=12
- **TREND_PULLBACK_EMA** (total=2050): setup_compat:regime_CLEAN_RANGE=1164, setup_compat:regime_DIRTY_RANGE=760, setup_compat:regime_VOLATILE_UNSUITABLE=121, entry_quality=5
- **VOLUME_SURGE_BREAKOUT** (total=73): execution:overextended=73

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 197405 | 48.1% |
| TRENDING_UP | 98468 | 24.0% |
| TRENDING_DOWN | 55643 | 13.5% |
| QUIET | 31224 | 7.6% |
| VOLATILE | 28065 | 6.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **31**
- Average confidence gap to threshold: **5.91** (samples=31) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=13, BNBUSDT=9, LSKUSDT=6, HYPEUSDT=2, ETHUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 64 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 3 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 82 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 12 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 6 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 22 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 37 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 190 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 6 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 541 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 39 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 25 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 14 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 64 | 59.52 | 64.25 | 4.73 | 19.96 | 17.60 | 20.00 | 3.11 | 8.55 |
| BREAKDOWN_SHORT | kept | 3 | 69.73 | 65.00 | -4.73 | 20.53 | 17.53 | 20.00 | 3.83 | 5.67 |
| DIVERGENCE_CONTINUATION | filtered | 82 | 53.70 | 61.83 | 8.13 | 20.04 | 19.60 | 19.89 | 0.65 | 15.81 |
| DIVERGENCE_CONTINUATION | kept | 12 | 66.22 | 65.00 | -1.22 | 19.21 | 18.22 | 18.16 | 0.25 | 6.58 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 37.80 | 61.00 | 23.20 | 21.20 | 19.50 | 17.00 | 0.00 | 13.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 6 | 68.43 | 65.00 | -3.43 | 21.02 | 18.98 | 18.30 | 1.00 | 0.78 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 49.50 | 61.00 | 11.50 | 21.00 | 19.90 | 15.80 | 0.00 | 20.00 |
| MEAN_REVERT | kept | 1 | 71.30 | 65.00 | -6.30 | 21.20 | 16.20 | 15.40 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 22 | 59.55 | 62.73 | 3.18 | 20.93 | 15.91 | 15.80 | 4.55 | 13.41 |
| MOVER_AVWAP_SCALP | kept | 37 | 75.54 | 65.00 | -10.54 | 20.10 | 15.70 | 15.80 | 4.36 | 3.45 |
| MOVER_TREND_PULLBACK | filtered | 196 | 56.64 | 64.77 | 8.13 | 21.09 | 17.86 | 15.80 | 3.84 | 18.95 |
| MOVER_TREND_PULLBACK | kept | 541 | 75.94 | 65.00 | -10.94 | 20.41 | 18.91 | 15.80 | 4.61 | 3.07 |
| QUIET_COMPRESSION_BREAK | filtered | 64 | 59.61 | 64.88 | 5.27 | 23.12 | 19.03 | 20.00 | 0.00 | 12.22 |
| QUIET_COMPRESSION_BREAK | kept | 3 | 74.23 | 65.00 | -9.23 | 23.60 | 18.97 | 20.00 | 0.00 | 4.63 |
| TREND_PULLBACK_EMA | kept | 14 | 80.69 | 65.00 | -15.69 | 20.21 | 19.74 | 16.11 | 4.61 | -1.73 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 64 | 59.52 | 16.56 | 15.31 | 12.00 | 13.34 | 5.00 | 2.74 | 3.11 |
| BREAKDOWN_SHORT | kept | 3 | 69.73 | 19.00 | 17.33 | 12.00 | 14.00 | 5.00 | 4.23 | 3.83 |
| DIVERGENCE_CONTINUATION | filtered | 82 | 53.70 | 20.71 | 16.41 | 3.29 | 13.67 | 5.48 | 9.30 | 0.65 |
| DIVERGENCE_CONTINUATION | kept | 12 | 66.22 | 23.67 | 15.50 | 5.75 | 11.92 | 6.79 | 9.68 | 0.25 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 37.80 | 25.00 | 8.00 | 3.00 | 17.00 | 8.50 | 4.30 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 6 | 68.43 | 24.33 | 14.00 | 6.50 | 15.00 | 5.50 | 3.38 | 1.00 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 49.50 | 17.00 | 14.00 | 6.00 | 14.00 | 8.50 | 10.00 | 0.00 |
| MEAN_REVERT | kept | 1 | 71.30 | 17.00 | 18.00 | 12.00 | 13.00 | 5.00 | 6.30 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 22 | 59.55 | 17.00 | 18.00 | 10.36 | 15.36 | 5.00 | 2.68 | 4.55 |
| MOVER_AVWAP_SCALP | kept | 37 | 75.54 | 19.38 | 18.05 | 11.39 | 14.16 | 6.00 | 6.13 | 4.36 |
| MOVER_TREND_PULLBACK | filtered | 196 | 56.64 | 18.94 | 18.02 | 7.52 | 12.23 | 6.29 | 9.21 | 3.84 |
| MOVER_TREND_PULLBACK | kept | 541 | 75.94 | 19.40 | 18.18 | 8.00 | 13.73 | 6.71 | 8.76 | 4.61 |
| QUIET_COMPRESSION_BREAK | filtered | 64 | 59.61 | 19.38 | 15.56 | 12.05 | 14.00 | 7.79 | 3.06 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 3 | 74.23 | 22.33 | 16.67 | 11.00 | 14.00 | 7.33 | 7.57 | 0.00 |
| TREND_PULLBACK_EMA | kept | 14 | 80.69 | 18.71 | 18.00 | 7.50 | 14.21 | 8.50 | 9.57 | 4.61 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 64 | 59.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 4.69 | **4.69** |
| BREAKDOWN_SHORT | kept | 3 | 69.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.00 | **2.00** |
| DIVERGENCE_CONTINUATION | filtered | 82 | 53.70 | 0.00 | 0.00 | 4.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.23** |
| DIVERGENCE_CONTINUATION | kept | 12 | 66.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 37.80 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 6 | 68.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 49.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 1 | 71.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 22 | 59.55 | 0.00 | 0.00 | 0.00 | 0.00 | 5.45 | 0.00 | 0.00 | 6.00 | **11.45** |
| MOVER_AVWAP_SCALP | kept | 37 | 75.54 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.96 | **1.96** |
| MOVER_TREND_PULLBACK | filtered | 196 | 56.64 | 0.00 | 0.00 | 0.98 | 0.00 | 0.00 | 0.00 | 0.00 | 0.09 | **1.07** |
| MOVER_TREND_PULLBACK | kept | 541 | 75.94 | 0.00 | 0.00 | 0.63 | 0.00 | 0.13 | 0.03 | 0.00 | 0.00 | **0.79** |
| QUIET_COMPRESSION_BREAK | filtered | 64 | 59.61 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 7.59 | **7.59** |
| QUIET_COMPRESSION_BREAK | kept | 3 | 74.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 14 | 80.69 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **106412 held of 277393 seen** across 21 strategies; 2440 cells past the sample floor; **1081 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 37381 | 654/36727/0 | 44% | -0.15 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | OVERLAP/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.16R) |
| MOVER_AVWAP_SCALP | 13272 | 188/13084/0 | 41% | -0.25 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | OVERLAP/MARKUP/EXPANDED/BTC_FALLING (-1.32R) |
| FAILED_AUCTION_RECLAIM | 8174 | 106/8068/0 | 42% | -0.18 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 6524 | 34/6490/0 | 50% | -0.00 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 5803 | 0/0/5803 | 42% | -0.12 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.50R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-0.84R) |
| TREND_PULLBACK_EMA | 5258 | 24/5234/0 | 45% | -0.15 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| SHADOW_RANGE_FADE | 4969 | 0/0/4969 | 37% | -0.10 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.70R) | LONDON/QUIET/NORMAL/BTC_RISING (-1.17R) |
| QUIET_COMPRESSION_BREAK | 4717 | 283/4434/0 | 46% | -0.13 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+0.65R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4563 | 0/0/4563 | 34% | -0.40 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.03R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3365 | 2/3363/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 3224 | 63/3161/0 | 36% | -0.38 | NY/RANGE/NORMAL/BTC_FALLING (+1.64R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 2169 | 24/2145/0 | 49% | -0.14 | LONDON/MARKDOWN/EXPANDED/BTC_RISING (+1.23R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 1839 | 2/1837/0 | 33% | -0.40 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 1650 | 0/1650/0 | 41% | -0.02 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| SR_FLIP_RETEST | 1184 | 10/1174/0 | 48% | -0.22 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.79R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.25R) |
| SHADOW_CASCADE_REVERSAL | 831 | 0/0/831 | 53% | -0.04 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.15R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.47R) |
| RANGE_FADE | 717 | 0/717/0 | 41% | -0.37 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 492 | 37/455/0 | 31% | -0.40 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.03R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.18R) |
| LIQUIDATION_REVERSAL | 212 | 0/212/0 | 10% | -1.02 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 62 | 6/56/0 | 45% | -0.06 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 6 | 0/6/0 | 67% | +0.42 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 143 | 28% / -0.54R | 143 | 48% / -0.18R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 424 | 45% / -0.21R | 424 | 54% / -0.04R | +0.17 | **ATR** |
| MOVER_AVWAP_SCALP | 1045 | 44% / -0.19R | 1045 | 50% / -0.08R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 367 | 44% / -0.32R | 367 | 46% / -0.22R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 37 | 38% / -0.19R | 37 | 41% / -0.09R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 131 | 50% / -0.26R | 131 | 51% / -0.17R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 5764 | 50% / -0.09R | 5764 | 55% / -0.01R | +0.08 | **ATR** |
| FAILED_AUCTION_RECLAIM | 737 | 43% / -0.18R | 737 | 45% / -0.10R | +0.08 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 635 | 49% / -0.21R | 635 | 54% / -0.15R | +0.06 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 95 | 39% / -0.10R | 95 | 46% / -0.07R | +0.04 | **ATR** |
| RANGE_FADE | 35 | 40% / -0.19R | 35 | 43% / -0.22R | -0.03 | **FIXED** |
| DIVERGENCE_CONTINUATION | 625 | 51% / -0.07R | 625 | 56% / -0.05R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 774 | 46% / -0.15R | 774 | 46% / -0.16R | -0.01 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 20 | 40% / -0.15R | 20 | 40% / -0.14R | +0.01 | **ATR** |
| MEAN_REVERT | 154 | 53% / -0.07R | 154 | 51% / -0.07R | +0.01 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 14 | 29% / -0.51R | 14 | 57% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8302 | 29% | -0.24R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1045 | 48% | -0.07R | 193 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 61 | 51% | -0.05R | 47 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 139 | 37% / -0.30R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 750 | 36% / -0.09R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 7397 | 37% / -0.13R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1395 | 35% / -0.11R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 589 | 35% / -0.11R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 704 | 40% / +0.00R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 571 | 38% / -0.04R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 632 | 42% / -0.17R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 131 | 27% / -0.44R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 186 | 31% / -0.58R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 126 | 55% / +0.10R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 62 | 42% / -0.15R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 27 | 37% / +0.17R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 135 | 36% / -0.39R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 29 | 17% / -0.49R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 19 | 42% / -0.05R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.05R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×257]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 143/6) (sustained 143 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.58R (bound 0.3) (streak 216/6) (sustained 216 cycles)
- **ALERT** `tuned_variants` — 62 non-stamps — atr_arm_uncomputable=62 (seen=580 stamped=155 skipped=363) (streak 216/6) (sustained 216 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 216/3) (sustained 216 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 54054126 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 216/3) | 216 |
| ai_governor_live_arms | ok | 32 arms current, none stalled; covering 634/634 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | violating | 2 live ATR-trail arms could not be advanced this cycle (0 no candles, 2 bars behind; 60 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 9/12) | 9 |
| auto_dispatch | ok | 32 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: mode:paper=64. No user is on live. | 0 |
| btc_reference | ok | BTC ref 85441.60 | 0 |
| candle_coverage | ok | 96/96 symbols with ≥20 15m candles, 96/96 updated within 45m [fresh=96; 75 Tier-1 futures + 21 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 620 dup bars, 0 undedupable; ws 0 out-of-order, 257 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 8 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | violating | upstream +20 but output +0 (streak 1/72) | 1 |
| dark_atr_trail_arms | ok | no open arms; covering 1125/1142 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | 86 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1122/1139 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 9160408 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.58R (bound 0.3) (streak 216/6) | 216 |
| emission_controller | ok | last cycle 1717s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×257]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 143/6) | 143 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=53, mover_stack_15m=15, profile_reject=2. Held back in this window: session_quality=116, profile_reject=2. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 3/6) | 3 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 1958 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +151 but output +0 (streak 1/6) | 1 |
| indicator_cache_key | ok | 73063 frozen value(s) avoided; 214691 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.14R over n=2145 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +54 / upstream +151 | 0 |
| mover_admission_metadata | ok | 905 symbols known, 199 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 21 held, 21 with scan counts, 20 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 8 locked / 8 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 1669254 evicted (sampled: execution:trigger_not_confirmed 400/612171, execution:overextended 400/551595, setup_compat:regime_STRONG_TREND 400/249464) | 0 |
| price_action_lane | ok | 381271 evaluated, 593 emitted; layer1 593 stamped / 0 blind; cooldown=50954, delta_opposed=33283, no_footprint=184045, no_opposing_target=816, no_sweep=80014, rr_below_floor=31566 | 0 |
| promoted_pair_integrity | ok | 21/21 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.37R over n=717 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +26 / upstream +151 | 0 |
| sar_alignment_crosscheck | ok | 136/4513 disagreed (3.0%) | 0 |
| sar_exit_shadow | violating | upstream +151 but output +0 (streak 1/6) | 1 |
| sar_hold_arm | ok | 1834 held arms settled, 166 unscored, 62 still walking (55 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 8/31 unfetchable (26%); top cause: gap or duplicate bar in the 15m window; symbols: 1000SHIBUSDT, MUBARAKUSDT, NILUSDT, PHAUSDT | 0 |
| sar_live_arms | violating | 2 live SAR arms could not be advanced this cycle (0 no candles, 2 bars behind; 60 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 9/12) | 9 |
| sar_refresh_budget | ok | 3 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 431 records await one (23 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| scan_cycle | ok | last 21.86s, worst 121.88s over 3914 lifetime cycles; lifetime 45 over 60s, 1 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.76s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 186432 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 2s ago (0.21s to run, worst 76.16s), 384 overrun(s) of 4332 cycles, TTL 900s; slowest data_intake=0.08s, agents=0.08s, signals=0.05s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=909, gate reads=0, withheld=909) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +62 / upstream +151 | 0 |
| structural_snap | ok | 5385/5385 measured, 24 blind, 0 levels moved (refusals: redetect_cooldown=43) | 0 |
| structural_veto_lane | ok | 192 stamped; 0 with no readable level book, 1 with clear air ahead, 131 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +151 / upstream +20 | 0 |
| tuned_variants | violating | 62 non-stamps — atr_arm_uncomputable=62 (seen=580 stamped=155 skipped=363) (streak 216/6) | 216 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 1 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2028247`
- `Path funnel` emissions: `43`
- `Regime distribution` emissions: `43`
- `QUIET_SCALP_BLOCK` events: `31`
- `confidence_gate` events: `1047`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=345981] state[populated=345981] buckets[many=345981] sources[none] quality[none]
- funding_rate: presence[absent=69361, present=276620] state[empty=69361, populated=276620] buckets[few=276620, none=69361] sources[none] quality[none]
- liquidation_clusters: presence[absent=170617, present=175364] state[empty=170617, populated=175364] buckets[few=130727, none=170617, some=44637] sources[none] quality[none]
- oi_snapshot: presence[absent=68712, present=277269] state[empty=68712, populated=277269] buckets[few=138, many=275881, none=68712, some=1250] sources[none] quality[none]
- order_book: presence[absent=122288, present=223693] state[populated=223693, unavailable=122288] buckets[few=223693, none=122288] sources[book_ticker=223693, unavailable=122288] quality[none=122288, top_of_book_only=223693]
- orderblocks: presence[absent=345981] state[empty=345981] buckets[none=345981] sources[measured_dark=345981] quality[none]
- recent_ticks: presence[present=345981] state[populated=345981] buckets[many=345981] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.723811149597168` sec
- Median create→first breach: `5564.884802103043` sec
- Median create→terminal: `5565.213454008102` sec
- Median first breach→terminal: `0.00011706352233886719` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 3.0}, "under_180s": {"count": 1, "pct": 3.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 3.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 3.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 2.7663051838178765 | 3.0 | 0.9221017279392921 | 0 | 1 |
| MOVER_AVWAP_SCALP | 4 | 4 | 2.410700532161843 | 2.506476255504595 | 1.1585435311579804 | 2 | 2 |
| MOVER_TREND_PULLBACK | 25 | 25 | 2.647851302992444 | 2.96193754010696 | 1.0987787444443644 | 13 | 12 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 1.2578770868851903 | 1.403576567483112 | 1.0000000000000113 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 4.1495 | 3446.14400100708 | 3446.465278148651 |
| MOVER_AVWAP_SCALP | 4 | 4 | 25.0 | 75.0 | 25.0 | 0.0 | -1.6926 | 5767.626711964607 | 5767.775043487549 |
| MOVER_TREND_PULLBACK | 25 | 25 | 44.0 | 24.0 | 44.0 | 0.0 | 0.9573 | 5035.013471126556 | 5035.013520002365 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 33.3 | 0.0 | 33.3 | 0.0 | 2.3695 | 13003.326390028 | 13003.326447963715 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 390 | 0 | 371 | 0.0 | 0.0 | None | None | 19 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2709 | 5 | 2656 | 0.0 | 0.0 | None | None | 53 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-151`
- Gating Δ: `44628`
- No-generation Δ: `112284`
- Fast failures Δ: `1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.6672, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.6672, "previous_win_rate": 66.7, "win_rate_delta": -66.7}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -2.2749, "current_avg_pnl": -1.6926, "current_win_rate": 25.0, "previous_avg_pnl": 0.5823, "previous_win_rate": 33.3, "win_rate_delta": -8.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.0443, "current_avg_pnl": 0.9573, "current_win_rate": 44.0, "previous_avg_pnl": -0.087, "previous_win_rate": 29.4, "win_rate_delta": 14.6}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 2.6999, "current_avg_pnl": 2.3695, "current_win_rate": 33.3, "previous_avg_pnl": -0.3304, "previous_win_rate": 0.0, "win_rate_delta": 33.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": -70, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -6, "geometry_changed_delta": 0, "geometry_preserved_delta": -23, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
