# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `747` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 117 | 117 | 117 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10018 | 10018 | 8869 | 15 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 79830 | 79836 | 15 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 77188 | 77188 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 76866 | 74956 | 2217 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 77221 | 75614 | 1679 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 76794 | 76711 | 108 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 69501 | 69512 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 77298 | 77328 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 77340 | 75783 | 2220 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 82123 | 86277 | 569 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 79854 | 75968 | 6102 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 75986 | 75986 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 77193 | 77213 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 76831 | 76807 | 51 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 78006 | 76552 | 2005 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 75991 | 76492 | 298 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 69146 | 65610 | 3799 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 69417 | 69032 | 465 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 79794 | 79818 | 9 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 69516 | 69528 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 7013 | 7013 | 6441 | 3 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 380 | 380 | 124 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 19 | 19 | 9 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 22480 | 22480 | 22346 | 3 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 12 | 12 | 1 | 4 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 6267 | 6267 | 3135 | 3 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1556 | 1556 | 440 | 34 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 19106 | 19106 | 8951 | 240 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 10 | 10 | 10 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 616 | 616 | 260 | 26 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 5226 | 5226 | 3382 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1299 | 1299 | 585 | 20 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2440 | 2440 | 1998 | 40 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 79 | 79 | 47 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=79836): breakout_not_found=42984, basic_filters_failed=23637, move_not_fresh=9459, breakout_stale=3160, retest_proximity_failed=484, volume_spike_missing=110, move_exhausted=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=77188): cls_disabled_merged_into_lsr=77188
- **EVAL::DIVERGENCE_CONTINUATION** (total=74956): cvd_divergence_failed=27584, h1_trend_not_aligned=22013, basic_filters_failed=20116, ema_alignment_reject=4673, retest_proximity_failed=425, missing_fvg_or_orderblock=145
- **EVAL::FAILED_AUCTION_RECLAIM** (total=75614): auction_not_detected=43880, basic_filters_failed=19580, reclaim_hold_failed=6233, tail_too_small=4055, regime_blocked=1792, rsi_reject=74
- **EVAL::FUNDING_EXTREME** (total=76711): funding_not_extreme=53912, basic_filters_failed=19415, missing_funding_rate=1911, ema_alignment_reject=828, rsi_reject=418, momentum_reject=111, cvd_divergence_failed=97, missing_fvg_or_orderblock=19
- **EVAL::LIQUIDATION_REVERSAL** (total=69512): cascade_threshold_not_met=49021, basic_filters_failed=19887, rsi_reject=304, cvd_divergence_failed=275, missing_fvg_or_orderblock=25
- **EVAL::MA_CROSS_TREND_SHIFT** (total=77328): no_ma_cross=56002, basic_filters_failed=20129, ma_cross_htf_misaligned=636, ma_cross_cooldown=561
- **EVAL::MEAN_REVERT** (total=75783): no_extension=65556, basic_filters_failed=10227
- **EVAL::MOVER_AVWAP_SCALP** (total=86277): no_avwap_tag=27180, no_mover_leg=26429, basic_filters_failed=23822, avwap_slope_against=5356, avwap_reclaim_no_volume=2103, no_avwap_reclaim=1343, anchor_too_recent=44
- **EVAL::MOVER_TREND_PULLBACK** (total=75968): mover_run_too_small=40983, basic_filters_failed=23723, no_reclaim=10154, no_pullback_tag=1108
- **EVAL::OPENING_RANGE_BREAKOUT** (total=75986): feature_disabled=75986
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=77213): regime_blocked=43463, breakout_not_found=22473, basic_filters_failed=6305, adx_reject=4915, ema_alignment_reject=57
- **EVAL::QUIET_COMPRESSION_BREAK** (total=76807): regime_blocked=35406, compression_not_detected=24976, basic_filters_failed=13262, breakout_not_detected=2884, volume_confirmation_failed=275, rsi_reject=3, missing_fvg_or_orderblock=1
- **EVAL::RANGE_FADE** (total=76552): no_range_edge=66322, basic_filters_failed=10230
- **EVAL::SR_FLIP_RETEST** (total=76492): flip_close_not_confirmed=46465, basic_filters_failed=19549, long_break_volume_thin=2891, retest_out_of_zone=2552, regime_blocked=1787, h1_break_not_confirmed=1502, reclaim_hold_failed=1120, long_acceptance_not_held=250, ema_alignment_reject=186, wick_quality_failed=118, whipsaw_flip=45, missing_fvg_or_orderblock=27
- **EVAL::STANDARD** (total=65610): adx_reject=21138, momentum_reject=19884, basic_filters_failed=6784, sweeps_not_detected=6077, ema_alignment_reject=5721, macd_reject=4934, htf_poi_unanchored=1010, rsi_reject=52, invalid_sl_geometry=10
- **EVAL::TREND_PULLBACK** (total=69032): h1_trend_not_aligned=26936, ema_alignment_reject=11081, basic_filters_failed=10323, h1_pullback_not_confirmed=6842, no_ema_reclaim_close=4220, ema_not_tested_prev=4154, body_conviction_fail=2199, rsi_reject=1844, prev_already_below_emas=704, no_prev_low_break=292, no_prev_high_break=155, prev_already_above_emas=111, momentum_flat=82, ema21_not_tagged=53, momentum_reject=24, missing_fvg_or_orderblock=12
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=79818): breakout_not_found=42564, basic_filters_failed=23635, move_not_fresh=9933, breakout_stale=2638, retest_proximity_failed=896, volume_spike_missing=140, move_exhausted=8, missing_fvg_or_orderblock=4
- **EVAL::WHALE_MOMENTUM** (total=69528): momentum_reject=58079, recent_ticks_insufficient=5921, basic_filters_failed=5528

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=15): execution:overextended=15
- **DIVERGENCE_CONTINUATION** (total=371): setup_compat:regime_VOLATILE_UNSUITABLE=325, execution:overextended=23, setup_compat:regime_BREAKOUT_EXPANSION=23
- **FAILED_AUCTION_RECLAIM** (total=1931): execution:overextended=952, setup_compat:regime_STRONG_TREND=851, context_floor=128
- **FUNDING_EXTREME_SIGNAL** (total=324): execution:trigger_not_confirmed=321, context_floor=3
- **LIQUIDATION_REVERSAL** (total=19): execution:trigger_not_confirmed=19
- **LIQUIDITY_SWEEP_REVERSAL** (total=4425): execution:trigger_not_confirmed=1971, execution:overextended=1278, setup_compat:regime_STRONG_TREND=1176
- **MA_CROSS_TREND_SHIFT** (total=5): setup_compat:regime_CLEAN_RANGE=3, execution:trigger_not_confirmed=1, setup_compat:regime_DIRTY_RANGE=1
- **MEAN_REVERT** (total=4424): setup_compat:regime_WEAK_TREND=2207, setup_compat:regime_STRONG_TREND=1907, execution:overextended=310
- **MOVER_AVWAP_SCALP** (total=951): execution:overextended=476, execution:trigger_not_confirmed=278, entry_quality=197
- **MOVER_TREND_PULLBACK** (total=9033): execution:trigger_not_confirmed=5163, execution:overextended=2423, entry_quality=1447
- **QUIET_COMPRESSION_BREAK** (total=16): execution:trigger_not_confirmed=16
- **RANGE_FADE** (total=3441): setup_compat:regime_STRONG_TREND=1511, setup_compat:regime_WEAK_TREND=1420, setup_compat:regime_VOLATILE_UNSUITABLE=352, execution:overextended=109, setup_compat:regime_BREAKOUT_EXPANSION=49
- **TREND_PULLBACK_EMA** (total=1937): setup_compat:regime_CLEAN_RANGE=1514, setup_compat:regime_DIRTY_RANGE=347, entry_quality=57, setup_compat:regime_VOLATILE_UNSUITABLE=19
- **VOLUME_SURGE_BREAKOUT** (total=5): execution:overextended=5

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 235949 | 45.7% |
| TRENDING_UP | 89273 | 17.3% |
| QUIET | 85481 | 16.6% |
| TRENDING_DOWN | 84181 | 16.3% |
| VOLATILE | 21056 | 4.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **111**
- Average confidence gap to threshold: **7.82** (samples=111) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: AAVEUSDT=22, ETHUSDT=12, RAREUSDT=11, ASTERUSDT=10, ENAUSDT=8, WLFIUSDT=7, BTCUSDT=7, XMRUSDT=6, SUIUSDT=5, BNBUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 164 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 5 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 122 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 241 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 23 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 50 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 2 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 5 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 61 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 20 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 6 |
| MEAN_REVERT | filtered | min_confidence | 17 |
| MEAN_REVERT | kept | min_confidence_pass | 3 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 190 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 9 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 310 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1475 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 20 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3006 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 111 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 42 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 77 |
| SR_FLIP_RETEST | filtered | min_confidence | 269 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 6 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 103 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 87 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 6 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 110 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 30 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 169 | 55.65 | 64.44 | 8.79 | 20.17 | 19.66 | 17.59 | 1.97 | 11.47 |
| DIVERGENCE_CONTINUATION | kept | 122 | 70.19 | 65.00 | -5.19 | 21.00 | 19.94 | 17.91 | 0.65 | -0.22 |
| FAILED_AUCTION_RECLAIM | filtered | 264 | 50.30 | 62.98 | 12.68 | 20.05 | 18.91 | 20.00 | 2.14 | 6.84 |
| FAILED_AUCTION_RECLAIM | kept | 50 | 72.12 | 65.00 | -7.12 | 18.85 | 19.89 | 20.00 | 2.27 | 0.36 |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 57.25 | 60.50 | 3.25 | 21.20 | 13.45 | 18.50 | 3.00 | 0.00 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 71.25 | 65.00 | -6.25 | 18.85 | 17.00 | 17.00 | 3.50 | 0.00 |
| LIQUIDATION_REVERSAL | filtered | 5 | 67.70 | 10.00 | -57.70 | 19.88 | 8.00 | 20.00 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 61 | 46.44 | 64.28 | 17.84 | 19.88 | 18.94 | 18.75 | 2.16 | 13.52 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 20 | 70.75 | 65.00 | -5.75 | 20.39 | 19.56 | 18.70 | 0.60 | 2.40 |
| MA_CROSS_TREND_SHIFT | kept | 6 | 72.82 | 65.00 | -7.82 | 20.48 | 18.97 | 15.80 | 0.00 | 1.07 |
| MEAN_REVERT | filtered | 17 | 55.40 | 64.71 | 9.31 | 23.75 | 17.16 | 16.85 | 0.00 | 14.06 |
| MEAN_REVERT | kept | 3 | 65.63 | 65.00 | -0.63 | 22.37 | 15.97 | 15.33 | 0.00 | 6.50 |
| MOVER_AVWAP_SCALP | filtered | 201 | 56.93 | 64.00 | 7.07 | 19.88 | 15.57 | 15.80 | 4.04 | 11.16 |
| MOVER_AVWAP_SCALP | kept | 310 | 77.86 | 65.00 | -12.86 | 19.97 | 15.28 | 15.80 | 4.69 | 2.13 |
| MOVER_TREND_PULLBACK | filtered | 1495 | 55.87 | 64.05 | 8.18 | 20.11 | 18.14 | 15.80 | 3.78 | 15.67 |
| MOVER_TREND_PULLBACK | kept | 3006 | 75.58 | 65.00 | -10.58 | 20.28 | 18.41 | 15.80 | 4.26 | 1.90 |
| QUIET_COMPRESSION_BREAK | filtered | 153 | 47.01 | 63.61 | 16.60 | 21.07 | 19.17 | 20.00 | 0.00 | 14.07 |
| QUIET_COMPRESSION_BREAK | kept | 77 | 72.84 | 65.00 | -7.84 | 20.08 | 19.28 | 20.00 | 0.00 | 4.70 |
| SR_FLIP_RETEST | filtered | 275 | 52.26 | 64.23 | 11.97 | 21.49 | 20.00 | 16.29 | 2.00 | 18.02 |
| SR_FLIP_RETEST | kept | 103 | 70.27 | 65.00 | -5.27 | 20.54 | 20.00 | 15.98 | 1.74 | -1.14 |
| TREND_PULLBACK_EMA | filtered | 93 | 54.71 | 65.00 | 10.29 | 20.83 | 19.90 | 19.22 | 4.72 | 16.26 |
| TREND_PULLBACK_EMA | kept | 110 | 78.55 | 65.00 | -13.55 | 20.80 | 19.81 | 17.62 | 5.01 | -0.05 |
| VOLUME_SURGE_BREAKOUT | filtered | 30 | 40.75 | 63.40 | 22.65 | 19.38 | 16.46 | 20.00 | 4.15 | 18.07 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 71.35 | 65.00 | -6.35 | 21.20 | 19.20 | 20.00 | 4.75 | 3.90 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 169 | 55.65 | 22.87 | 14.09 | 4.26 | 12.88 | 5.37 | 7.55 | 1.97 |
| DIVERGENCE_CONTINUATION | kept | 122 | 70.19 | 24.54 | 15.87 | 4.40 | 12.49 | 5.15 | 8.91 | 0.65 |
| FAILED_AUCTION_RECLAIM | filtered | 264 | 50.30 | 21.20 | 16.91 | 6.45 | 14.12 | 5.38 | 3.88 | 2.14 |
| FAILED_AUCTION_RECLAIM | kept | 50 | 72.12 | 21.80 | 14.24 | 5.46 | 15.10 | 7.04 | 6.88 | 2.27 |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 57.25 | 21.00 | 13.00 | 7.50 | 12.00 | 9.25 | 6.50 | 3.00 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 71.25 | 17.00 | 18.00 | 3.00 | 13.00 | 9.25 | 7.50 | 3.50 |
| LIQUIDATION_REVERSAL | filtered | 5 | 67.70 | 25.00 | 8.00 | 12.00 | 8.00 | 5.00 | 5.70 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 61 | 46.44 | 23.16 | 16.30 | 7.62 | 12.97 | 5.28 | 4.81 | 2.16 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 20 | 70.75 | 22.20 | 16.40 | 8.55 | 13.50 | 5.12 | 6.78 | 0.60 |
| MA_CROSS_TREND_SHIFT | kept | 6 | 72.82 | 23.67 | 14.00 | 6.50 | 12.50 | 8.42 | 8.78 | 0.00 |
| MEAN_REVERT | filtered | 17 | 55.40 | 17.00 | 17.76 | 9.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 3 | 65.63 | 22.33 | 15.33 | 11.00 | 12.67 | 5.00 | 5.80 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 201 | 56.93 | 19.17 | 18.26 | 11.85 | 14.38 | 5.81 | 6.00 | 4.04 |
| MOVER_AVWAP_SCALP | kept | 310 | 77.86 | 19.71 | 18.17 | 12.38 | 13.59 | 5.78 | 8.05 | 4.69 |
| MOVER_TREND_PULLBACK | filtered | 1495 | 55.87 | 18.31 | 18.07 | 7.82 | 13.15 | 5.96 | 8.45 | 3.78 |
| MOVER_TREND_PULLBACK | kept | 3006 | 75.58 | 19.18 | 18.07 | 7.77 | 13.12 | 6.42 | 8.88 | 4.26 |
| QUIET_COMPRESSION_BREAK | filtered | 153 | 47.01 | 20.08 | 15.10 | 10.75 | 14.10 | 6.52 | 3.46 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 77 | 72.84 | 21.68 | 16.70 | 12.86 | 14.16 | 7.38 | 5.02 | 0.00 |
| SR_FLIP_RETEST | filtered | 275 | 52.26 | 20.26 | 17.78 | 4.45 | 12.35 | 6.11 | 7.33 | 2.00 |
| SR_FLIP_RETEST | kept | 103 | 70.27 | 20.50 | 17.71 | 5.01 | 12.87 | 6.12 | 6.98 | 1.74 |
| TREND_PULLBACK_EMA | filtered | 93 | 54.71 | 16.47 | 18.00 | 7.50 | 14.19 | 6.29 | 7.51 | 4.72 |
| TREND_PULLBACK_EMA | kept | 110 | 78.55 | 21.02 | 18.00 | 7.57 | 14.33 | 5.76 | 8.63 | 5.01 |
| VOLUME_SURGE_BREAKOUT | filtered | 30 | 40.75 | 13.10 | 17.40 | 12.50 | 14.00 | 5.00 | 7.66 | 4.15 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 71.35 | 25.00 | 16.00 | 12.00 | 14.00 | 6.50 | 4.50 | 4.75 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 169 | 55.65 | 0.00 | 0.00 | 1.79 | 0.00 | 1.07 | 0.00 | 0.00 | 0.00 | **2.86** |
| DIVERGENCE_CONTINUATION | kept | 122 | 70.19 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.67** |
| FAILED_AUCTION_RECLAIM | filtered | 264 | 50.30 | 0.00 | 0.00 | 0.11 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | **1.11** |
| FAILED_AUCTION_RECLAIM | kept | 50 | 72.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 57.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 71.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 5 | 67.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 61 | 46.44 | 0.00 | 0.00 | 0.79 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.79** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 20 | 70.75 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.40** |
| MA_CROSS_TREND_SHIFT | kept | 6 | 72.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 17 | 55.40 | 0.00 | 0.00 | 1.88 | 0.00 | 8.89 | 0.00 | 0.00 | 0.00 | **10.77** |
| MEAN_REVERT | kept | 3 | 65.63 | 0.00 | 0.00 | 2.67 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | **5.07** |
| MOVER_AVWAP_SCALP | filtered | 201 | 56.93 | 0.00 | 0.00 | 0.56 | 0.00 | 3.83 | 0.00 | 0.00 | 1.18 | **5.57** |
| MOVER_AVWAP_SCALP | kept | 310 | 77.86 | 0.00 | 0.00 | 1.25 | 0.00 | 0.27 | 0.15 | 0.00 | 0.00 | **1.67** |
| MOVER_TREND_PULLBACK | filtered | 1495 | 55.87 | 0.32 | 0.00 | 0.48 | 0.00 | 0.61 | 0.00 | 0.00 | 0.00 | **1.41** |
| MOVER_TREND_PULLBACK | kept | 3006 | 75.58 | 0.00 | 0.00 | 0.46 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | **0.61** |
| QUIET_COMPRESSION_BREAK | filtered | 153 | 47.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.52 | 0.00 | 0.00 | 5.55 | **6.07** |
| QUIET_COMPRESSION_BREAK | kept | 77 | 72.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | 0.42 | **0.62** |
| SR_FLIP_RETEST | filtered | 275 | 52.26 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | **0.16** |
| SR_FLIP_RETEST | kept | 103 | 70.27 | 0.00 | 0.00 | 0.12 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | **0.24** |
| TREND_PULLBACK_EMA | filtered | 93 | 54.71 | 0.00 | 0.00 | 1.98 | 0.00 | 1.39 | 0.00 | 0.00 | 0.00 | **3.37** |
| TREND_PULLBACK_EMA | kept | 110 | 78.55 | 0.00 | 0.00 | 0.93 | 0.00 | 0.20 | 0.00 | 0.00 | 0.00 | **1.13** |
| VOLUME_SURGE_BREAKOUT | filtered | 30 | 40.75 | 0.00 | 0.00 | 0.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.27** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 71.35 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.40** |

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
- Outcomes recorded: **194133 held of 913836 seen** across 21 strategies; 4395 cells past the sample floor; **2370 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 49131 | 584/48547/0 | 43% | -0.19 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.26R) |
| MOVER_AVWAP_SCALP | 26028 | 191/25837/0 | 43% | -0.20 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 15334 | 256/15078/0 | 45% | -0.15 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.98R) | NY/MARKUP/CASCADE/BTC_FALLING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 14642 | 143/14499/0 | 36% | -0.32 | OVERLAP/RANGE/NORMAL/BTC_FALLING (+1.72R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 13662 | 77/13585/0 | 39% | -0.30 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.38R) |
| LIQUIDITY_SWEEP_REVERSAL | 10746 | 111/10635/0 | 37% | -0.43 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9466 | 466/9000/0 | 45% | -0.11 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8358 | 0/0/8358 | 43% | -0.08 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+1.11R) | OVERLAP/MARKDOWN/EXPANDED/BTC_FALLING (-0.92R) |
| SHADOW_RANGE_FADE | 7864 | 0/0/7864 | 35% | -0.14 | OVERLAP/MARKUP/COMPRESSED/BTC_NEUTRAL (+0.34R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.37R) |
| SHADOW_FUNDING_FADE | 7430 | 0/0/7430 | 34% | -0.42 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.02R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 7163 | 30/7133/0 | 45% | -0.31 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 5695 | 71/5624/0 | 36% | -0.32 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4415 | 2/4413/0 | 31% | -0.44 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.06R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 4108 | 0/4108/0 | 27% | -0.43 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/NORMAL/BTC_FALLING (-1.19R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| RANGE_FADE | 3115 | 6/3109/0 | 50% | +0.18 | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (+3.08R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.78R) |
| SHADOW_CASCADE_REVERSAL | 1750 | 0/0/1750 | 52% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.57R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 552 | 0/552/0 | 36% | -0.25 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 236 | 40/196/0 | 43% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 64 | 6/58/0 | 41% | +0.09 | — | — |

- **Strongest cells**: `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.08R (n=37, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.00R (n=32, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.78R (n=47, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 405 | 27% / -0.57R | 405 | 52% / -0.10R | +0.47 | **ATR** |
| TREND_PULLBACK_EMA | 1405 | 39% / -0.36R | 1405 | 50% / -0.09R | +0.28 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1604 | 42% / -0.37R | 1604 | 57% / -0.11R | +0.25 | **ATR** |
| LIQUIDATION_REVERSAL | 34 | 26% / -0.56R | 34 | 47% / -0.32R | +0.24 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 235 | 37% / -0.17R | 235 | 49% / -0.04R | +0.13 | **ATR** |
| MA_CROSS_TREND_SHIFT | 73 | 44% / -0.17R | 73 | 49% / -0.04R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 773 | 47% / -0.26R | 773 | 51% / -0.13R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 2859 | 46% / -0.14R | 2859 | 52% / -0.03R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1598 | 41% / -0.22R | 1598 | 44% / -0.12R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 9112 | 48% / -0.13R | 9112 | 54% / -0.03R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 2007 | 48% / -0.12R | 2007 | 53% / -0.06R | +0.06 | **ATR** |
| RANGE_FADE | 165 | 43% / +0.03R | 165 | 50% / +0.08R | +0.05 | **ATR** |
| MEAN_REVERT | 480 | 46% / -0.16R | 480 | 45% / -0.17R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1659 | 48% / -0.10R | 1659 | 48% / -0.10R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 14 | 57% / -0.06R | 14 | 57% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12175 | 27% | -0.29R | 313 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2859 | 50% | -0.03R | 242 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 148 | 48% | -0.06R | 73 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1797 | 33% / -0.13R | +0.93 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1899 | 38% / -0.18R | +0.83 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3410 | 36% / -0.15R | +0.70 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11170 | 36% / -0.15R | +0.38 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2327 | 37% / -0.12R | +0.16 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1608 | 37% / -0.09R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1331 | 32% / -0.28R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 344 | 32% / -0.36R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 524 | 31% / -0.25R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 398 | 47% / -0.09R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 115 | 46% / +0.01R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 666 | 35% / -0.28R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 116 | 30% / +0.13R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 45 | 44% / -0.22R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 25 | 48% / +0.53R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `ai_governor_verdicts` — upstream +1 but output +0 (streak 15/6) (sustained 15 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 730/6) (sustained 730 cycles)
- **ALERT** `range_fade_emission` — 5717 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.18R over n=3109, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 248/6) (sustained 248 cycles)
- **ALERT** `tuned_variants` — 898 non-stamps — atr_arm_uncomputable=898 (seen=22475 stamped=2073 skipped=19504) (streak 730/6) (sustained 730 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 274489216 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 21 arms current, none stalled; covering 2158/2158 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 15/6) | 15 |
| atr_trail_live_arms | ok | 41 arms current, none stalled; covering 1166/1166 signals (100%) | 0 |
| auto_dispatch | ok | 140 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=140. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 97/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 64565.50 | 0 |
| candle_coverage | ok | 83/83 symbols with ≥20 15m candles, 83/83 updated within 45m [fresh=83; 77 Tier-1 futures + 6 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 915 dup bars, 0 undedupable; ws 0 out-of-order, 560 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 61 cohorts, 40 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +38 / upstream +27 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 2823/2842 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | 141 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 2784/2803 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 99277705 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 730/6) | 730 |
| emission_controller | ok | last cycle 764s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=707, MOVER_AVWAP_SCALP=479, MOVER_TREND_PULLBACK=3842, RANGE_FADE=514, TREND_PULLBACK_EMA=458), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 2 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won) | 0 |
| entry_quality_effective | ok | 25291 evaluated, 8461 suppressed, 12286 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,314 reads/day of 50,000 [engine 1,293, signing 21]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | violating | 5280 sealed bars over 44 symbols; 2734 incomplete, 0 shape-capped (streak 5/6) | 5 |
| gate_override_shadow | ok | output +1 / upstream +1 | 0 |
| geometry_ab | ok | output +12 / upstream +348 | 0 |
| indicator_cache_key | ok | 332188 frozen value(s) avoided; 2392359 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.33R over n=5624 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +12 / upstream +348 | 0 |
| mover_admission_metadata | ok | 947 symbols known, 238 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 6 held, 6 with scan counts, 6 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 9 locked / 9 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2226 rows held, 3697690 evicted (sampled: execution:trigger_not_confirmed 279/1297700, execution:overextended 279/1136469, setup_compat:regime_STRONG_TREND 279/639448) | 0 |
| price_action_lane | ok | 1832638 evaluated, 2194 emitted; layer1 2194 stamped / 0 blind; cooldown=288117, delta_opposed=182221, no_footprint=664865, no_opposing_target=2514, no_sweep=531376, rr_below_floor=161351 | 0 |
| promoted_pair_integrity | ok | 6/6 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 5717 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.18R over n=3109, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 248/6) | 248 |
| range_fade_path | ok | output +20 / upstream +348 | 0 |
| sar_alignment_crosscheck | ok | 1875/41027 disagreed (4.6%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +348 | 0 |
| sar_hold_arm | ok | 1893 held arms settled, 107 unscored, 41 still walking (31 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 1/44 unfetchable (2%); top cause: located bar does not contain the stamp; symbols: PIEVERSEUSDT | 0 |
| sar_live_arms | ok | 41 arms current, none stalled; covering 1166/1166 signals (100%) | 0 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 3 resolved, 40 still mid-window | 0 |
| scan_cycle | ok | last 19.21s, worst 183.3s over 23127 lifetime cycles; lifetime 479 over 60s, 19 over 120s (plus 1/0 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 7.92s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 727701 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| snapshot_writer | ok | last cycle 31s ago (41.21s to run, worst 175.83s), 1614 overrun(s) of 15332 cycles, TTL 900s; slowest data_intake=19.29s, activity=11.88s, alerts=3.62s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +1 / upstream +0 | 0 |
| strategy_edge | ok | output +21 / upstream +348 | 0 |
| structural_snap | ok | 6000/6000 measured, 44 blind, 0 levels moved (refusals: redetect_cooldown=2158) | 0 |
| structural_veto_lane | ok | 3759 stamped; 0 with no readable level book, 67 with clear air ahead, 2793 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +348 / upstream +27 | 0 |
| tuned_variants | violating | 898 non-stamps — atr_arm_uncomputable=898 (seen=22475 stamped=2073 skipped=19504) (streak 730/6) | 730 |
| unlock_shorts | ok | 18 open, 42 scheduled, calendar 14.4h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 45 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2352013`
- `Path funnel` emissions: `66`
- `Regime distribution` emissions: `66`
- `QUIET_SCALP_BLOCK` events: `111`
- `confidence_gate` events: `6576`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **29**
- Total REST-fallback activations: **2**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 4 | 5770 | 6517 | 6914 | 0 |
| futures_aggtrade | 6 | 23172 | 23738 | 23969 | 0 |
| futures_depth | 13 | 6312 | 35015 | 37204 | 0 |
| futures_liq | 2 | 5756 | 5756 | 29658 | 0 |
| futures_mover | 4 | 4156 | 24812 | 30832 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 2 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=378388] state[populated=378388] buckets[many=378388] sources[none] quality[none]
- funding_rate: presence[absent=18604, present=359784] state[empty=18604, populated=359784] buckets[few=359784, none=18604] sources[none] quality[none]
- liquidation_clusters: presence[absent=219785, present=158603] state[empty=219785, populated=158603] buckets[few=133661, none=219785, some=24942] sources[none] quality[none]
- oi_snapshot: presence[absent=18604, present=359784] state[empty=18604, populated=359784] buckets[few=85, many=359341, none=18604, some=358] sources[none] quality[none]
- order_book: presence[absent=110864, present=267524] state[populated=267524, unavailable=110864] buckets[few=267524, none=110864] sources[book_ticker=267524, unavailable=110864] quality[none=110864, top_of_book_only=267524]
- orderblocks: presence[absent=378388] state[empty=378388] buckets[none=378388] sources[measured_dark=378388] quality[none]
- recent_ticks: presence[present=378388] state[populated=378388] buckets[many=378388] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.041793465614319` sec
- Median create→first breach: `6209.223976492882` sec
- Median create→terminal: `6209.349105477333` sec
- Median first breach→terminal: `7.295608520507812e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 4.5}, "under_180s": {"count": 2, "pct": 4.5}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 2, "pct": 4.5}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 1.0245240529413493 | 1.1530936900974254 | 0.8885002682260683 | 0 | 3 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 1.1354437637191561 | 1.2389835659349635 | 0.9164316581248 | 0 | 1 |
| MA_CROSS_TREND_SHIFT | 2 | 2 | 2.5929817485884827 | 1.9223890279216225 | 1.5182083723755573 | 1 | 1 |
| MOVER_AVWAP_SCALP | 3 | 3 | 2.5548816366544624 | 2.975400000000011 | 0.9601061741193858 | 1 | 2 |
| MOVER_TREND_PULLBACK | 21 | 21 | 3.634020532394005 | 3.0 | 1.2113401774646684 | 15 | 6 |
| QUIET_COMPRESSION_BREAK | 10 | 10 | 1.1592775131030095 | 1.3528750269507401 | 0.8967885979128112 | 0 | 8 |
| SR_FLIP_RETEST | 4 | 4 | 0.5936321854689126 | 1.1620287798041429 | 0.540730169177652 | 0 | 4 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 1.5300779199248427 | 1.5367867701914801 | 0 | 0 | 0 | 0 | 0 | 3 |
| FAILED_AUCTION_RECLAIM | 1 | 2.0148904105101133 | 1.7031648265242647 | 0 | 0 | 0 | 1 | 0 | 0 |
| MA_CROSS_TREND_SHIFT | 2 | 5.91552296771032 | 2.270492726232953 | 0 | 0 | 0 | 2 | 0 | 0 |
| MOVER_AVWAP_SCALP | 3 | 3.3383340718143146 | 3.832322454981682 | 2 | 0 | 0 | 1 | 0 | 0 |
| MOVER_TREND_PULLBACK | 21 | 4.607800152944173 | 3.940837094972071 | 6 | 2 | 1 | 15 | 1 | 0 |
| QUIET_COMPRESSION_BREAK | 10 | 3.116622810171192 | 1.8973252914408265 | 0 | 0 | 0 | 7 | 0 | 3 |
| SR_FLIP_RETEST | 4 | 2.180688500268934 | 2.180688500268934 | 1 | 0 | 0 | 0 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | 0.1294 | 2933.9928209781647 | 2934.458093881607 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.1354 | 3614.581871986389 | 3614.5819280147552 |
| MA_CROSS_TREND_SHIFT | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.6016 | 18254.253160357475 | 18254.253216981888 |
| MOVER_AVWAP_SCALP | 3 | 3 | 33.3 | 33.3 | 33.3 | 0.0 | 1.4729 | 1004.0660231113434 | 1004.0660510063171 |
| MOVER_TREND_PULLBACK | 21 | 21 | 23.8 | 42.9 | 23.8 | 0.0 | 0.3403 | 3847.2544560432434 | 3847.254471063614 |
| QUIET_COMPRESSION_BREAK | 10 | 10 | 20.0 | 40.0 | 20.0 | 0.0 | -0.2757 | 19850.884442090988 | 19850.88446164131 |
| SR_FLIP_RETEST | 4 | 4 | 25.0 | 0.0 | 25.0 | 0.0 | 0.3089 | 11548.350884437561 | 11548.350973963737 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1299 | 20 | 585 | 25.0 | 0.0 | 11548.350884437561 | 11548.350973963737 | 714 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2440 | 40 | 1998 | 0.0 | 0.0 | None | None | 442 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-31`
- Gating Δ: `-9447`
- No-generation Δ: `-230049`
- Fast failures Δ: `0`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 1.0453, "current_avg_pnl": 0.1294, "current_win_rate": 0.0, "previous_avg_pnl": -0.9159, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 1.9101, "current_avg_pnl": 1.4729, "current_win_rate": 33.3, "previous_avg_pnl": -0.4372, "previous_win_rate": 0.0, "win_rate_delta": 33.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.6743, "current_avg_pnl": 0.3403, "current_win_rate": 23.8, "previous_avg_pnl": 1.0146, "previous_win_rate": 38.7, "win_rate_delta": -14.9}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.3415, "current_avg_pnl": -0.2757, "current_win_rate": 20.0, "previous_avg_pnl": 0.0658, "previous_win_rate": 22.2, "win_rate_delta": -2.2}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.3089, "current_avg_pnl": 0.3089, "current_win_rate": 25.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 25.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 7, "geometry_changed_delta": 0, "geometry_preserved_delta": 169, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 11548.35, "median_terminal_delta_sec": 11548.35, "sl_rate_delta": 0.0, "win_rate_delta": 25.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 6, "geometry_changed_delta": 0, "geometry_preserved_delta": 1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
