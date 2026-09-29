# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `950` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 532 | 532 | 487 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 23652 | 23652 | 19522 | 22 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 131521 | 131470 | 76 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 99609 | 99609 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 99356 | 93355 | 6244 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 99625 | 98894 | 780 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 109856 | 109798 | 73 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 94986 | 94993 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 99677 | 99689 | 3 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 99693 | 97351 | 3023 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 140283 | 146209 | 1932 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 131547 | 111735 | 28520 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 109179 | 109179 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 99611 | 99619 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 99341 | 99339 | 15 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 100381 | 97780 | 3570 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 98651 | 99126 | 200 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 84782 | 76969 | 8086 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 85059 | 84529 | 585 | 0 | 0 | 0 | low-sample (ema_alignment_reject) |
| EVAL::VOLUME_SURGE_BREAKOUT | 131494 | 131428 | 90 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 94997 | 95014 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 5476 | 5476 | 4018 | 6 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 689 | 689 | 204 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 41 | 41 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 48656 | 48656 | 47484 | 42 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 3 | 3 | 1 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 9514 | 9514 | 7462 | 3 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 5285 | 5285 | 2906 | 43 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 94576 | 94576 | 74562 | 404 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 15 | 15 | 0 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 328 | 328 | 264 | 5 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 11553 | 11553 | 11058 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 988 | 988 | 774 | 3 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 4087 | 4087 | 3273 | 43 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 241 | 241 | 51 | 3 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=131470): breakout_not_found=73385, basic_filters_failed=33837, move_not_fresh=14154, breakout_stale=6511, retest_proximity_failed=2763, volume_spike_missing=745, move_exhausted=71, missing_fvg_or_orderblock=4
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=99609): cls_disabled_merged_into_lsr=99609
- **EVAL::DIVERGENCE_CONTINUATION** (total=93355): cvd_divergence_failed=40831, basic_filters_failed=19654, h1_trend_not_aligned=16178, ema_alignment_reject=15066, retest_proximity_failed=1098, missing_fvg_or_orderblock=528
- **EVAL::FAILED_AUCTION_RECLAIM** (total=98894): auction_not_detected=68012, basic_filters_failed=18809, reclaim_hold_failed=4758, regime_blocked=4391, tail_too_small=2828, rsi_reject=96
- **EVAL::FUNDING_EXTREME** (total=109799): funding_not_extreme=85335, basic_filters_failed=21972, missing_funding_rate=1233, ema_alignment_reject=727, rsi_reject=366, momentum_reject=73, cvd_divergence_failed=72, missing_fvg_or_orderblock=21
- **EVAL::LIQUIDATION_REVERSAL** (total=94993): cascade_threshold_not_met=71375, basic_filters_failed=22457, cvd_divergence_failed=605, rsi_reject=510, missing_fvg_or_orderblock=32, volume_spike_missing=14
- **EVAL::MA_CROSS_TREND_SHIFT** (total=99689): no_ma_cross=78138, basic_filters_failed=19662, ma_cross_htf_misaligned=1635, ma_cross_htf_unconfirmed=147, ma_cross_cooldown=107
- **EVAL::MEAN_REVERT** (total=97351): no_extension=79964, basic_filters_failed=17387
- **EVAL::MOVER_AVWAP_SCALP** (total=146210): no_avwap_tag=63082, basic_filters_failed=33946, no_mover_leg=27346, avwap_slope_against=13482, avwap_reclaim_no_volume=4744, no_avwap_reclaim=3396, anchor_too_recent=214
- **EVAL::MOVER_TREND_PULLBACK** (total=111735): mover_run_too_small=38643, basic_filters_failed=33891, no_reclaim=33606, no_pullback_tag=5595
- **EVAL::OPENING_RANGE_BREAKOUT** (total=109180): feature_disabled=109180
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=99619): regime_blocked=73898, breakout_not_found=19166, basic_filters_failed=5733, adx_reject=781, ema_alignment_reject=41
- **EVAL::QUIET_COMPRESSION_BREAK** (total=99339): compression_not_detected=55680, regime_blocked=30034, basic_filters_failed=13066, breakout_not_detected=496, volume_confirmation_failed=56, rsi_reject=6, missing_fvg_or_orderblock=1
- **EVAL::RANGE_FADE** (total=97780): no_range_edge=80390, basic_filters_failed=17390
- **EVAL::SR_FLIP_RETEST** (total=99126): flip_close_not_confirmed=60574, basic_filters_failed=18793, long_break_volume_thin=6209, regime_blocked=4382, retest_out_of_zone=4378, h1_break_not_confirmed=2703, reclaim_hold_failed=1195, long_acceptance_not_held=271, ema_alignment_reject=257, whipsaw_flip=231, wick_quality_failed=126, missing_fvg_or_orderblock=7
- **EVAL::STANDARD** (total=76969): momentum_reject=19238, adx_reject=16019, basic_filters_failed=13261, macd_reject=11896, sweeps_not_detected=8872, ema_alignment_reject=5995, htf_poi_unanchored=1499, invalid_sl_geometry=77, mtf_reject=70, rsi_reject=42
- **EVAL::TREND_PULLBACK** (total=84529): ema_alignment_reject=21050, h1_trend_not_aligned=19574, h1_pullback_not_confirmed=10859, basic_filters_failed=10264, ema_not_tested_prev=9298, no_ema_reclaim_close=6469, body_conviction_fail=2446, rsi_reject=2181, prev_already_below_emas=1053, no_prev_low_break=622, prev_already_above_emas=237, momentum_flat=190, no_prev_high_break=127, ema21_not_tagged=109, missing_fvg_or_orderblock=35, momentum_reject=15
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=131428): breakout_not_found=81051, basic_filters_failed=33836, move_not_fresh=9664, breakout_stale=4475, retest_proximity_failed=1996, volume_spike_missing=379, missing_fvg_or_orderblock=23, move_exhausted=4
- **EVAL::WHALE_MOMENTUM** (total=95014): momentum_reject=83508, recent_ticks_insufficient=9064, basic_filters_failed=2442

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=89): execution:overextended=89
- **DIVERGENCE_CONTINUATION** (total=745): setup_compat:regime_VOLATILE_UNSUITABLE=629, setup_compat:regime_BREAKOUT_EXPANSION=88, execution:overextended=28
- **FAILED_AUCTION_RECLAIM** (total=1546): execution:overextended=655, context_floor=529, setup_compat:regime_STRONG_TREND=362
- **FUNDING_EXTREME_SIGNAL** (total=593): execution:trigger_not_confirmed=592, context_floor=1
- **LIQUIDATION_REVERSAL** (total=41): execution:trigger_not_confirmed=41
- **LIQUIDITY_SWEEP_REVERSAL** (total=11677): execution:trigger_not_confirmed=4172, execution:overextended=3897, setup_compat:regime_STRONG_TREND=3608
- **MA_CROSS_TREND_SHIFT** (total=4): setup_compat:regime_DIRTY_RANGE=2, execution:overextended=2
- **MEAN_REVERT** (total=4896): setup_compat:regime_STRONG_TREND=2612, execution:overextended=1331, setup_compat:regime_WEAK_TREND=949, entry_quality=4
- **MOVER_AVWAP_SCALP** (total=3120): execution:overextended=2335, execution:trigger_not_confirmed=614, entry_quality=171
- **MOVER_TREND_PULLBACK** (total=41457): execution:trigger_not_confirmed=26553, execution:overextended=12085, entry_quality=2819
- **RANGE_FADE** (total=5069): setup_compat:regime_STRONG_TREND=2651, setup_compat:regime_WEAK_TREND=1334, execution:overextended=669, setup_compat:regime_VOLATILE_UNSUITABLE=377, setup_compat:regime_BREAKOUT_EXPANSION=38
- **TREND_PULLBACK_EMA** (total=3869): setup_compat:regime_CLEAN_RANGE=1974, setup_compat:regime_DIRTY_RANGE=1481, entry_quality=256, setup_compat:regime_VOLATILE_UNSUITABLE=158
- **VOLUME_SURGE_BREAKOUT** (total=13): execution:overextended=13

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 430670 | 56.4% |
| TRENDING_DOWN | 133400 | 17.5% |
| TRENDING_UP | 107995 | 14.1% |
| QUIET | 56460 | 7.4% |
| VOLATILE | 35161 | 4.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **101**
- Average confidence gap to threshold: **11.41** (samples=101) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: LITUSDT=23, BNBUSDT=23, DOTUSDT=12, XRPUSDT=8, ETCUSDT=7, BCHUSDT=7, ZECUSDT=7, BRUSDT=6, ETHUSDT=3, ZROUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 28 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 17 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 857 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 4 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 469 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 433 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 23 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 21 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 41 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 31 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 388 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 21 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 273 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MEAN_REVERT | filtered | min_confidence | 202 |
| MEAN_REVERT | kept | min_confidence_pass | 30 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 460 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 25 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 497 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2167 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 29 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 7158 |
| POST_DISPLACEMENT_CONTINUATION | filtered | min_confidence | 15 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 56 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 3 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 5 |
| SR_FLIP_RETEST | filtered | min_confidence | 55 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 6 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 3 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 154 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 15 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 199 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 67 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 19 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 28 | 56.00 | 64.00 | 8.00 | 20.00 | 18.70 | 20.00 | 4.00 | 20.00 |
| BREAKDOWN_SHORT | kept | 17 | 79.09 | 65.00 | -14.09 | 19.23 | 18.20 | 20.00 | 5.56 | 6.65 |
| DIVERGENCE_CONTINUATION | filtered | 861 | 53.76 | 63.74 | 9.98 | 20.14 | 19.69 | 18.21 | 1.43 | 14.46 |
| DIVERGENCE_CONTINUATION | kept | 469 | 68.30 | 65.00 | -3.30 | 21.54 | 19.78 | 18.25 | 1.38 | 2.47 |
| FAILED_AUCTION_RECLAIM | filtered | 456 | 49.61 | 61.35 | 11.74 | 20.99 | 19.09 | 20.00 | 2.36 | 6.16 |
| FAILED_AUCTION_RECLAIM | kept | 21 | 64.93 | 65.00 | 0.07 | 20.30 | 19.80 | 20.00 | 2.71 | 1.14 |
| FUNDING_EXTREME_SIGNAL | filtered | 41 | 30.07 | 63.34 | 33.27 | 22.14 | 14.23 | 17.00 | 2.90 | 27.46 |
| LIQUIDATION_REVERSAL | filtered | 31 | 30.00 | 10.00 | -20.00 | 19.32 | 9.80 | 14.80 | 4.00 | 20.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 409 | 55.62 | 63.54 | 7.92 | 20.74 | 18.89 | 18.21 | 1.41 | 12.73 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 273 | 70.33 | 65.00 | -5.33 | 20.99 | 18.97 | 18.15 | 1.41 | 0.32 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 58.00 | 61.00 | 3.00 | 20.20 | 17.00 | 15.80 | 0.00 | 20.00 |
| MEAN_REVERT | filtered | 202 | 57.22 | 64.78 | 7.56 | 19.83 | 15.15 | 15.17 | 0.00 | 13.26 |
| MEAN_REVERT | kept | 30 | 71.79 | 65.00 | -6.79 | 19.70 | 15.26 | 14.97 | 0.00 | 0.40 |
| MOVER_AVWAP_SCALP | filtered | 485 | 50.16 | 61.67 | 11.51 | 20.40 | 15.29 | 15.80 | 4.22 | 16.07 |
| MOVER_AVWAP_SCALP | kept | 497 | 80.58 | 65.00 | -15.58 | 20.31 | 14.95 | 15.80 | 3.99 | 2.24 |
| MOVER_TREND_PULLBACK | filtered | 2196 | 58.05 | 64.27 | 6.22 | 19.99 | 18.31 | 15.80 | 4.06 | 16.13 |
| MOVER_TREND_PULLBACK | kept | 7158 | 76.66 | 65.00 | -11.66 | 20.31 | 18.52 | 15.80 | 4.08 | 1.84 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 15 | 52.20 | 61.80 | 9.60 | 19.59 | 19.80 | 17.20 | 4.50 | -6.00 |
| QUIET_COMPRESSION_BREAK | filtered | 59 | 55.88 | 65.00 | 9.12 | 24.08 | 18.85 | 20.00 | 0.00 | -1.43 |
| QUIET_COMPRESSION_BREAK | kept | 5 | 70.40 | 65.00 | -5.40 | 21.50 | 19.68 | 20.00 | 0.00 | 2.84 |
| SR_FLIP_RETEST | filtered | 61 | 53.59 | 64.28 | 10.69 | 21.86 | 20.00 | 17.23 | 1.62 | 14.00 |
| SR_FLIP_RETEST | kept | 3 | 67.27 | 65.00 | -2.27 | 21.33 | 20.00 | 16.47 | 2.33 | 3.17 |
| TREND_PULLBACK_EMA | filtered | 169 | 59.37 | 64.31 | 4.94 | 20.86 | 19.58 | 18.04 | 5.25 | 19.24 |
| TREND_PULLBACK_EMA | kept | 199 | 80.10 | 65.00 | -15.10 | 21.20 | 19.73 | 18.88 | 5.18 | 0.64 |
| VOLUME_SURGE_BREAKOUT | filtered | 67 | 44.86 | 64.76 | 19.90 | 21.12 | 18.87 | 20.00 | 3.52 | 12.12 |
| VOLUME_SURGE_BREAKOUT | kept | 19 | 77.01 | 65.00 | -12.01 | 20.98 | 18.61 | 20.00 | 4.32 | 3.19 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 28 | 56.00 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 10.00 | 4.00 |
| BREAKDOWN_SHORT | kept | 17 | 79.09 | 24.53 | 15.18 | 13.24 | 12.94 | 5.00 | 9.29 | 5.56 |
| DIVERGENCE_CONTINUATION | filtered | 861 | 53.76 | 23.75 | 14.32 | 4.03 | 11.40 | 5.70 | 7.77 | 1.43 |
| DIVERGENCE_CONTINUATION | kept | 469 | 68.30 | 22.58 | 16.89 | 3.63 | 12.27 | 5.54 | 8.84 | 1.38 |
| FAILED_AUCTION_RECLAIM | filtered | 456 | 49.61 | 20.71 | 17.53 | 5.31 | 13.34 | 6.41 | 4.11 | 2.36 |
| FAILED_AUCTION_RECLAIM | kept | 21 | 64.93 | 24.62 | 18.00 | 7.29 | 15.95 | 5.50 | 4.86 | 2.71 |
| FUNDING_EXTREME_SIGNAL | filtered | 41 | 30.07 | 25.00 | 8.00 | 4.39 | 12.20 | 7.78 | 5.63 | 2.90 |
| LIQUIDATION_REVERSAL | filtered | 31 | 30.00 | 25.00 | 8.00 | 12.00 | 8.00 | 8.00 | 0.00 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 409 | 55.62 | 21.39 | 14.68 | 4.53 | 13.45 | 5.47 | 7.42 | 1.41 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 273 | 70.33 | 22.51 | 14.63 | 4.49 | 13.03 | 6.20 | 8.38 | 1.41 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 58.00 | 17.00 | 14.00 | 15.00 | 14.00 | 10.00 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 202 | 57.22 | 19.06 | 16.67 | 10.02 | 12.02 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 30 | 71.79 | 17.80 | 18.00 | 9.10 | 13.00 | 6.90 | 7.39 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 485 | 50.16 | 19.85 | 18.00 | 11.16 | 12.87 | 6.08 | 5.68 | 4.22 |
| MOVER_AVWAP_SCALP | kept | 497 | 80.58 | 19.54 | 18.13 | 12.88 | 13.56 | 7.16 | 7.99 | 3.99 |
| MOVER_TREND_PULLBACK | filtered | 2196 | 58.05 | 18.42 | 18.02 | 7.60 | 12.42 | 5.96 | 8.87 | 4.06 |
| MOVER_TREND_PULLBACK | kept | 7158 | 76.66 | 19.68 | 18.02 | 7.77 | 13.21 | 6.69 | 9.10 | 4.08 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 15 | 52.20 | 2.00 | 18.00 | 15.00 | 14.00 | 5.00 | 8.70 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 59 | 55.88 | 18.63 | 14.20 | 10.58 | 14.15 | 8.32 | 4.63 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 5 | 70.40 | 17.20 | 18.00 | 12.60 | 14.60 | 7.10 | 7.32 | 0.00 |
| SR_FLIP_RETEST | filtered | 61 | 53.59 | 17.79 | 17.02 | 4.57 | 13.85 | 5.00 | 7.74 | 1.62 |
| SR_FLIP_RETEST | kept | 3 | 67.27 | 22.33 | 14.67 | 4.00 | 14.00 | 5.00 | 8.10 | 2.33 |
| TREND_PULLBACK_EMA | filtered | 169 | 59.37 | 16.78 | 18.00 | 7.63 | 15.56 | 7.24 | 8.15 | 5.25 |
| TREND_PULLBACK_EMA | kept | 199 | 80.10 | 19.78 | 18.01 | 7.54 | 14.40 | 7.19 | 9.10 | 5.18 |
| VOLUME_SURGE_BREAKOUT | filtered | 67 | 44.86 | 18.43 | 16.03 | 12.00 | 12.48 | 5.00 | 4.52 | 3.52 |
| VOLUME_SURGE_BREAKOUT | kept | 19 | 77.01 | 17.84 | 15.47 | 13.74 | 15.05 | 5.00 | 9.56 | 4.32 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 28 | 56.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 17 | 79.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 861 | 53.76 | 0.00 | 0.00 | 0.25 | 0.00 | 0.13 | 0.06 | 0.00 | 0.00 | **0.44** |
| DIVERGENCE_CONTINUATION | kept | 469 | 68.30 | 0.00 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.15** |
| FAILED_AUCTION_RECLAIM | filtered | 456 | 49.61 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 21 | 64.93 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 41 | 30.07 | 0.00 | 0.00 | 6.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.24** |
| LIQUIDATION_REVERSAL | filtered | 31 | 30.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 409 | 55.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.18 | 0.02 | 0.00 | 0.00 | **0.20** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 273 | 70.33 | 0.00 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.15** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 58.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 202 | 57.22 | 0.00 | 0.00 | 0.00 | 0.00 | 10.41 | 0.00 | 0.00 | 0.00 | **10.41** |
| MEAN_REVERT | kept | 30 | 71.79 | 0.00 | 0.00 | 0.00 | 0.00 | 0.40 | 0.00 | 0.00 | 0.00 | **0.40** |
| MOVER_AVWAP_SCALP | filtered | 485 | 50.16 | 0.00 | 0.00 | 0.00 | 0.00 | 3.99 | 0.00 | 0.00 | 1.03 | **5.02** |
| MOVER_AVWAP_SCALP | kept | 497 | 80.58 | 0.03 | 0.00 | 0.00 | 0.00 | 1.13 | 0.02 | 0.00 | 0.42 | **1.60** |
| MOVER_TREND_PULLBACK | filtered | 2196 | 58.05 | 0.00 | 0.00 | 0.96 | 0.00 | 0.11 | 0.64 | 0.00 | 0.03 | **1.74** |
| MOVER_TREND_PULLBACK | kept | 7158 | 76.66 | 0.00 | 0.00 | 0.38 | 0.00 | 0.21 | 0.06 | 0.00 | 0.00 | **0.65** |
| POST_DISPLACEMENT_CONTINUATION | filtered | 15 | 52.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 59 | 55.88 | 0.00 | 0.00 | 0.00 | 0.00 | 1.02 | 0.00 | 0.00 | 0.00 | **1.02** |
| QUIET_COMPRESSION_BREAK | kept | 5 | 70.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 61 | 53.59 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 3 | 67.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 169 | 59.37 | 0.00 | 0.00 | 0.00 | 0.00 | 1.80 | 0.75 | 0.00 | 0.00 | **2.55** |
| TREND_PULLBACK_EMA | kept | 199 | 80.10 | 0.00 | 0.00 | 0.12 | 0.00 | 0.00 | 0.23 | 0.00 | 0.00 | **0.35** |
| VOLUME_SURGE_BREAKOUT | filtered | 67 | 44.86 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 19 | 77.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.19 | **0.19** |

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
- Outcomes recorded: **118989 held of 362466 seen** across 21 strategies; 2712 cells past the sample floor; **1286 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 40017 | 613/39404/0 | 45% | -0.14 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.19R) | NY/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.17R) |
| MOVER_AVWAP_SCALP | 15444 | 192/15252/0 | 40% | -0.28 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 9261 | 106/9155/0 | 41% | -0.21 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 7798 | 48/7750/0 | 50% | -0.00 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.68R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.19R) |
| TREND_PULLBACK_EMA | 6632 | 26/6606/0 | 45% | -0.10 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.33R) |
| SHADOW_MEAN_REVERT | 6300 | 0/0/6300 | 43% | -0.08 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | LONDON/QUIET/NORMAL/BTC_RISING (-0.83R) |
| SHADOW_RANGE_FADE | 5496 | 0/0/5496 | 37% | -0.09 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.61R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.34R) |
| QUIET_COMPRESSION_BREAK | 5129 | 320/4809/0 | 46% | -0.13 | ASIA/RANGE/NORMAL/BTC_FALLING/MIDCAP (+0.88R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4898 | 0/0/4898 | 34% | -0.40 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| LIQUIDITY_SWEEP_REVERSAL | 4111 | 69/4042/0 | 41% | -0.37 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.93R) | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.56R) |
| WHALE_MOMENTUM | 3391 | 2/3389/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| MEAN_REVERT | 2362 | 31/2331/0 | 50% | -0.08 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.62R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| VOLUME_SURGE_BREAKOUT | 2076 | 0/2076/0 | 40% | -0.05 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2047 | 2/2045/0 | 32% | -0.44 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| SR_FLIP_RETEST | 1398 | 12/1386/0 | 49% | -0.17 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.86R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.27R) |
| SHADOW_CASCADE_REVERSAL | 963 | 0/0/963 | 55% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.42R) |
| RANGE_FADE | 761 | 2/759/0 | 39% | -0.40 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 553 | 55/498/0 | 32% | -0.35 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.18R) |
| LIQUIDATION_REVERSAL | 276 | 0/276/0 | 31% | -0.57 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 68 | 8/60/0 | 47% | -0.04 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 8 | 0/8/0 | 75% | +0.30 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.56R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR` -1.55R (n=16, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 153 | 27% / -0.56R | 153 | 46% / -0.19R | +0.37 | **ATR** |
| LIQUIDATION_REVERSAL | 15 | 33% / -0.42R | 15 | 60% / -0.16R | +0.25 | **ATR** |
| TREND_PULLBACK_EMA | 526 | 44% / -0.20R | 526 | 57% / -0.02R | +0.18 | **ATR** |
| MOVER_AVWAP_SCALP | 1217 | 43% / -0.21R | 1217 | 50% / -0.08R | +0.13 | **ATR** |
| BREAKDOWN_SHORT | 47 | 43% / -0.19R | 47 | 47% / -0.08R | +0.12 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 808 | 48% / -0.24R | 808 | 56% / -0.12R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 368 | 44% / -0.33R | 368 | 46% / -0.22R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 148 | 48% / -0.27R | 148 | 50% / -0.17R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 880 | 42% / -0.20R | 880 | 44% / -0.11R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 6235 | 50% / -0.09R | 6235 | 55% / -0.00R | +0.09 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 109 | 39% / -0.12R | 109 | 48% / -0.06R | +0.06 | **ATR** |
| DIVERGENCE_CONTINUATION | 761 | 49% / -0.09R | 761 | 55% / -0.04R | +0.05 | **ATR** |
| RANGE_FADE | 40 | 38% / -0.25R | 40 | 40% / -0.26R | -0.01 | **FIXED** |
| MEAN_REVERT | 185 | 56% / +0.00R | 185 | 55% / +0.01R | +0.01 | **ATR** |
| MA_CROSS_TREND_SHIFT | 21 | 43% / -0.12R | 21 | 43% / -0.12R | +0.01 | **ATR** |
| QUIET_COMPRESSION_BREAK | 830 | 46% / -0.15R | 830 | 46% / -0.16R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 50% / -0.21R | 6 | 50% / -0.10R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8944 | 29% | -0.24R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1217 | 48% | -0.08R | 199 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 68 | 50% | -0.07R | 49 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 141 | 36% / -0.32R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 807 | 36% / -0.14R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 8023 | 36% / -0.15R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1602 | 35% / -0.10R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 717 | 34% / -0.14R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 853 | 39% / -0.02R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 698 | 38% / -0.07R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 804 | 42% / -0.19R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 159 | 28% / -0.44R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 205 | 29% / -0.60R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 153 | 58% / +0.15R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 80 | 42% / -0.14R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 32 | 34% / +0.07R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 150 | 35% / -0.42R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 32 | 22% / -0.42R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 21 | 48% / +0.11R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 10 | 40% / +0.02R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 60 · alerting: **6** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×317]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 38/6) (sustained 38 cycles)
- **ALERT** `dark_resolution` — 3 of 176 open dark rows are not being advanced (worst: BBUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 182/120) (sustained 182 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.56R (bound 0.3) (streak 241/6) (sustained 241 cycles)
- **ALERT** `mean_revert_emission` — 6281 detections since last emission (emitted_total=3) — and the POST-SCORING blocked candidates measure -0.09R over n=2331, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 185/6) (sustained 185 cycles)
- **ALERT** `tuned_variants` — 336 non-stamps — atr_arm_uncomputable=336 (seen=6495 stamped=655 skipped=5504) (streak 221/6) (sustained 221 cycles)
- **ALERT** `auto_dispatch` — 46 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=46) (streak 210/3) (sustained 210 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 44146092 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 24 arms current, none stalled; covering 1009/1009 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 1/6) | 1 |
| atr_trail_live_arms | ok | 48 arms current, none stalled; covering 1078/1078 signals (100%) | 0 |
| auto_dispatch | violating | 46 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=46) (streak 210/3) | 210 |
| binance_ip_weight | ok | peak 392/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 83398.70 | 0 |
| candle_coverage | ok | 98/98 symbols with ≥20 15m candles, 98/98 updated within 45m [fresh=98; 75 Tier-1 futures + 23 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1657 dup bars, 0 undedupable; ws 0 out-of-order, 322 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 34 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 34 cohorts, 9 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +178 / upstream +31 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1530/1548 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 3 of 176 open dark rows are not being advanced (worst: BBUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 182/120) | 182 |
| dark_sar_arms | ok | no open arms; covering 1524/1542 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 10963019 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.56R (bound 0.3) (streak 241/6) | 241 |
| emission_controller | ok | last cycle 1s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×317]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 38/6) | 38 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 1/6) | 1 |
| firestore_read_budget | ok | 1,395 reads/day of 50,000 [engine 1,351, signing 44]; top site keystore.roster_doc at 288/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 1156 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +25 / upstream +355 | 0 |
| indicator_cache_key | ok | 77742 frozen value(s) avoided; 589771 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 6281 detections since last emission (emitted_total=3) — and the POST-SCORING blocked candidates measure -0.09R over n=2331, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 185/6) | 185 |
| mean_revert_path | ok | output +31 / upstream +355 | 0 |
| mover_admission_metadata | ok | 912 symbols known, 206 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 23 held, 23 with scan counts, 23 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 2120756 evicted (sampled: execution:trigger_not_confirmed 400/782863, execution:overextended 400/706112, setup_compat:regime_STRONG_TREND 400/312904) | 0 |
| price_action_lane | ok | 748124 evaluated, 652 emitted; layer1 652 stamped / 0 blind; cooldown=103309, delta_opposed=71445, no_footprint=334957, no_opposing_target=660, no_sweep=171018, rr_below_floor=66083 | 0 |
| promoted_pair_integrity | ok | 23/23 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.41R over n=759 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +56 / upstream +355 | 0 |
| sar_alignment_crosscheck | ok | 497/14788 disagreed (3.4%) | 0 |
| sar_exit_shadow | ok | output +8 / upstream +355 | 0 |
| sar_hold_arm | ok | 1829 held arms settled, 172 unscored, 47 still walking (43 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 4/75 unfetchable (5%); top cause: located bar does not contain the stamp; symbols: AAVEUSDT, GRASSUSDT, ICPUSDT, SAGAUSDT | 0 |
| sar_live_arms | ok | 48 arms current, none stalled; covering 1076/1076 signals (100%) | 0 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 1 resolved, 70 still mid-window | 0 |
| scan_cycle | ok | last 47.32s, worst 80.92s over 8360 lifetime cycles; lifetime 9 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 2.35s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 404158 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 58s ago (6.92s to run, worst 60.63s), 264 overrun(s) of 5231 cycles, TTL 900s; slowest data_intake=8.8s, trail_governor=7.71s, positions_diag=6.1s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +103 / upstream +355 | 0 |
| structural_snap | ok | 5742/5742 measured, 27 blind, 0 levels moved (refusals: redetect_cooldown=570) | 0 |
| structural_veto_lane | ok | 1166 stamped; 0 with no readable level book, 8 with clear air ahead, 824 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +355 / upstream +31 | 0 |
| tuned_variants | violating | 336 non-stamps — atr_arm_uncomputable=336 (seen=6495 stamped=655 skipped=5504) (streak 221/6) | 221 |
| unlock_shorts | ok | 4 open, 45 scheduled, calendar 12.9h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 1 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3713498`
- `Path funnel` emissions: `86`
- `Regime distribution` emissions: `86`
- `QUIET_SCALP_BLOCK` events: `101`
- `confidence_gate` events: `13772`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **16**
- Total REST-fallback activations: **4**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 6 | 2753 | 6137 | 8903 | 0 |
| futures_aggtrade | 2 | 2029 | 2029 | 5023 | 0 |
| futures_depth | 4 | 4887 | 6914 | 8918 | 0 |
| futures_liq | 2 | 1577 | 1577 | 6848 | 0 |
| futures_mover | 2 | 1936 | 1936 | 4810 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 4 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=622810] state[populated=622810] buckets[many=622810] sources[none] quality[none]
- funding_rate: presence[absent=86071, present=536739] state[empty=86071, populated=536739] buckets[few=536739, none=86071] sources[none] quality[none]
- liquidation_clusters: presence[absent=321014, present=301796] state[empty=321014, populated=301796] buckets[few=234903, none=321014, some=66893] sources[none] quality[none]
- oi_snapshot: presence[absent=85237, present=537573] state[empty=85237, populated=537573] buckets[few=187, many=536156, none=85237, some=1230] sources[none] quality[none]
- order_book: presence[absent=165013, present=457797] state[populated=457797, unavailable=165013] buckets[few=457797, none=165013] sources[book_ticker=457797, unavailable=165013] quality[none=165013, top_of_book_only=457797]
- orderblocks: presence[absent=622810] state[empty=622810] buckets[none=622810] sources[measured_dark=622810] quality[none]
- recent_ticks: presence[present=622810] state[populated=622810] buckets[many=622810] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `7.633690118789673` sec
- Median create→first breach: `4306.1555788517` sec
- Median create→terminal: `4306.155604839325` sec
- Median first breach→terminal: `5.698204040527344e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.0}, "under_180s": {"count": 2, "pct": 3.9}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 2.141438616810046 | 2.24293758576634 | 0.9547473056760896 | 0 | 1 |
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.8000000000000047 | 1.5773313886566958 | 0.5073901494517007 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 1.6054455459151917 | 2.2977431315874 | 0.8726354700084589 | 0 | 3 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 1.6490073062261894 | 1.7459686577333675 | 0.8037943060498228 | 0 | 3 |
| MOVER_AVWAP_SCALP | 3 | 3 | 2.4678326372138333 | 2.792802743568115 | 1.0572121040260312 | 2 | 1 |
| MOVER_TREND_PULLBACK | 36 | 36 | 3.8221625102371917 | 3.0 | 1.274054170079064 | 23 | 12 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 1.5126918050224984 | 1.746396369738562 | 0.8838568545428916 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 14503.415163040161 | 14503.415181875229 |
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 1.4791 | 3166.653899550438 | 3167.1100499629974 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 33.3 | 33.3 | 33.3 | 0.0 | 0.3137 | 9654.932518005371 | 9655.338593959808 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 33.3 | 0.0 | 33.3 | 0.0 | 0.8245 | 5748.987726926804 | 5749.940440893173 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | -1.5529 | 5617.21826505661 | 5617.21833896637 |
| MOVER_TREND_PULLBACK | 36 | 36 | 33.3 | 52.8 | 33.3 | 0.0 | -0.0644 | 3390.7976224422455 | 3391.221566438675 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | -0.9894 | 23145.579899072647 | 23145.579960107803 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 988 | 3 | 774 | 0.0 | 0.0 | None | None | 214 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 4087 | 43 | 3273 | 0.0 | 0.0 | None | None | 814 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `227`
- Gating Δ: `-31889`
- No-generation Δ: `-835205`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.4948, "current_avg_pnl": 0.3137, "current_win_rate": 33.3, "previous_avg_pnl": 0.8085, "previous_win_rate": 33.3, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.3042, "current_avg_pnl": 0.8245, "current_win_rate": 33.3, "previous_avg_pnl": 0.5203, "previous_win_rate": 33.3, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -2.7273, "current_avg_pnl": -1.5529, "current_win_rate": 0.0, "previous_avg_pnl": 1.1744, "previous_win_rate": 40.0, "win_rate_delta": -40.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.294, "current_avg_pnl": -0.0644, "current_win_rate": 33.3, "previous_avg_pnl": 0.2296, "previous_win_rate": 34.5, "win_rate_delta": -1.2}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.8791, "current_avg_pnl": -0.9894, "current_win_rate": 0.0, "previous_avg_pnl": -0.1103, "previous_win_rate": 33.3, "win_rate_delta": -33.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 64, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 26, "geometry_changed_delta": 0, "geometry_preserved_delta": 420, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
