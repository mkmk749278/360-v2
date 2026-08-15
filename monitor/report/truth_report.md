# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `3950` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 56 | 56 | 48 | 4 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10732 | 10732 | 9933 | 19 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 83864 | 83890 | 11 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 73302 | 73310 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 72850 | 71072 | 2215 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 73344 | 73111 | 306 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 74838 | 74628 | 260 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 67330 | 67348 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 73419 | 73464 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 73473 | 71824 | 2648 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 88009 | 91679 | 505 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::MOVER_TREND_PULLBACK | 83906 | 77616 | 10327 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 74563 | 74575 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 73318 | 73331 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 72786 | 72558 | 286 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 74479 | 72798 | 2386 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 72476 | 72681 | 44 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 65066 | 62669 | 2595 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 65273 | 64828 | 539 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 83822 | 83856 | 6 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 67349 | 67361 | 67 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1290 | 1290 | 731 | 5 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 665 | 665 | 162 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 9 | 9 | 0 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 9819 | 9819 | 9527 | 25 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 8 | 8 | 3 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7914 | 7914 | 6148 | 24 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1470 | 1470 | 151 | 42 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 30852 | 30852 | 19885 | 384 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 14 | 14 | 14 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1555 | 1555 | 609 | 91 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 6663 | 6663 | 5653 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 124 | 124 | 47 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2487 | 2487 | 2232 | 16 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 35 | 35 | 0 | 3 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 5853 | 5853 | 170 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=83890): breakout_not_found=39942, basic_filters_failed=29481, move_not_fresh=9501, breakout_stale=3525, retest_proximity_failed=1213, volume_spike_missing=175, ema_alignment_reject=38, move_exhausted=14, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=73310): cls_disabled_merged_into_lsr=73310
- **EVAL::DIVERGENCE_CONTINUATION** (total=71072): cvd_divergence_failed=28030, basic_filters_failed=24328, h1_trend_not_aligned=13354, ema_alignment_reject=4243, retest_proximity_failed=791, missing_fvg_or_orderblock=326
- **EVAL::FAILED_AUCTION_RECLAIM** (total=73111): auction_not_detected=43419, basic_filters_failed=24011, regime_blocked=2620, reclaim_hold_failed=1850, tail_too_small=1201, rsi_reject=10
- **EVAL::FUNDING_EXTREME** (total=74628): funding_not_extreme=42518, basic_filters_failed=23648, missing_funding_rate=4585, ema_alignment_reject=2541, rsi_reject=885, cvd_divergence_failed=222, momentum_reject=184, missing_fvg_or_orderblock=45
- **EVAL::LIQUIDATION_REVERSAL** (total=67348): cascade_threshold_not_met=41782, basic_filters_failed=25167, cvd_divergence_failed=222, rsi_reject=161, missing_fvg_or_orderblock=12, volume_spike_missing=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=73464): no_ma_cross=48649, basic_filters_failed=24368, ma_cross_htf_misaligned=269, ma_cross_cooldown=178
- **EVAL::MEAN_REVERT** (total=71824): no_extension=57424, basic_filters_failed=14281, insufficient_candles=119
- **EVAL::MOVER_AVWAP_SCALP** (total=91679): basic_filters_failed=29790, no_mover_leg=29143, no_avwap_tag=25444, avwap_slope_against=4350, avwap_reclaim_no_volume=1597, no_avwap_reclaim=1140, insufficient_candles=116, anchor_too_recent=99
- **EVAL::MOVER_TREND_PULLBACK** (total=77616): mover_run_too_small=34506, basic_filters_failed=29611, no_reclaim=11419, no_pullback_tag=1964, insufficient_candles=116
- **EVAL::OPENING_RANGE_BREAKOUT** (total=74575): feature_disabled=74575
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=73331): regime_blocked=48020, breakout_not_found=14722, basic_filters_failed=7135, adx_reject=3401, ema_alignment_reject=53
- **EVAL::QUIET_COMPRESSION_BREAK** (total=72558): regime_blocked=27802, basic_filters_failed=16849, compression_not_detected=15885, breakout_not_detected=10910, volume_confirmation_failed=1029, rsi_reject=70, missing_fvg_or_orderblock=7, macd_reject=6
- **EVAL::RANGE_FADE** (total=72798): no_range_edge=58393, basic_filters_failed=14286, insufficient_candles=119
- **EVAL::SR_FLIP_RETEST** (total=72681): flip_close_not_confirmed=43171, basic_filters_failed=23958, regime_blocked=2590, retest_out_of_zone=1028, h1_break_not_confirmed=765, long_break_volume_thin=522, reclaim_hold_failed=355, whipsaw_flip=77, long_acceptance_not_held=74, wick_quality_failed=66, ema_alignment_reject=63, missing_fvg_or_orderblock=12
- **EVAL::STANDARD** (total=62669): momentum_reject=19549, adx_reject=15720, basic_filters_failed=10955, sweeps_not_detected=6501, macd_reject=4946, ema_alignment_reject=2942, htf_poi_unanchored=1415, rsi_reject=590, invalid_sl_geometry=51
- **EVAL::TREND_PULLBACK** (total=64828): h1_trend_not_aligned=18243, h1_pullback_not_confirmed=12245, basic_filters_failed=11479, ema_alignment_reject=9208, no_ema_reclaim_close=3921, ema_not_tested_prev=3319, body_conviction_fail=2741, rsi_reject=2428, prev_already_below_emas=566, no_prev_low_break=299, momentum_flat=124, prev_already_above_emas=119, no_prev_high_break=71, momentum_reject=40, ema21_not_tagged=20, missing_fvg_or_orderblock=5
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=83856): breakout_not_found=42972, basic_filters_failed=29477, move_not_fresh=7374, breakout_stale=2820, retest_proximity_failed=1021, volume_spike_missing=139, ema_alignment_reject=22, missing_fvg_or_orderblock=18, move_exhausted=13
- **EVAL::WHALE_MOMENTUM** (total=67361): momentum_reject=42838, recent_ticks_insufficient=16795, basic_filters_failed=7728

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=1): execution:overextended=1
- **DIVERGENCE_CONTINUATION** (total=312): setup_compat:regime_VOLATILE_UNSUITABLE=269, setup_compat:regime_BREAKOUT_EXPANSION=25, execution:overextended=18
- **FAILED_AUCTION_RECLAIM** (total=595): execution:overextended=247, setup_compat:regime_STRONG_TREND=184, context_floor=146, setup_compat:regime_VOLATILE_UNSUITABLE=18
- **FUNDING_EXTREME_SIGNAL** (total=524): execution:trigger_not_confirmed=519, context_floor=5
- **LIQUIDATION_REVERSAL** (total=9): execution:trigger_not_confirmed=9
- **LIQUIDITY_SWEEP_REVERSAL** (total=3701): execution:trigger_not_confirmed=2104, execution:overextended=997, setup_compat:regime_STRONG_TREND=600
- **MA_CROSS_TREND_SHIFT** (total=6): setup_compat:regime_CLEAN_RANGE=3, execution:trigger_not_confirmed=2, setup_compat:regime_DIRTY_RANGE=1
- **MEAN_REVERT** (total=3553): setup_compat:regime_STRONG_TREND=1906, setup_compat:regime_WEAK_TREND=1311, execution:overextended=330, entry_quality=6
- **MOVER_AVWAP_SCALP** (total=1008): execution:overextended=623, execution:trigger_not_confirmed=228, entry_quality=157
- **MOVER_TREND_PULLBACK** (total=20321): execution:overextended=11906, execution:trigger_not_confirmed=7031, entry_quality=1384
- **QUIET_COMPRESSION_BREAK** (total=48): execution:trigger_not_confirmed=48
- **RANGE_FADE** (total=3908): setup_compat:regime_WEAK_TREND=1630, setup_compat:regime_STRONG_TREND=851, execution:overextended=805, setup_compat:regime_VOLATILE_UNSUITABLE=534, context_edge=87, setup_compat:regime_BREAKOUT_EXPANSION=1
- **TREND_PULLBACK_EMA** (total=2359): setup_compat:regime_CLEAN_RANGE=1726, setup_compat:regime_DIRTY_RANGE=481, setup_compat:regime_VOLATILE_UNSUITABLE=99, entry_quality=53
- **VOLUME_SURGE_BREAKOUT** (total=15): execution:overextended=8, context_floor=7
- **WHALE_MOMENTUM** (total=5722): execution:trigger_not_confirmed=5722

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 153590 | 31.4% |
| QUIET | 145203 | 29.7% |
| TRENDING_DOWN | 81700 | 16.7% |
| TRENDING_UP | 77680 | 15.9% |
| VOLATILE | 30355 | 6.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **227**
- Average confidence gap to threshold: **16.01** (samples=227) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=38, BTWUSDT=23, UNIUSDT=23, BNBUSDT=18, SOLUSDT=17, XMRUSDT=12, BCHUSDT=11, TRXUSDT=11, SUIUSDT=7, XRPUSDT=6

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 8 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 90 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 11 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 87 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 32 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 12 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 138 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 40 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 4 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 81 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 27 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 100 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 264 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 7 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 504 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1382 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 42 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4657 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 131 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 71 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 688 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 15 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 6 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 124 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 22 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 3 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 23 |
| WHALE_MOMENTUM | filtered | min_confidence | 19 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 8 | 72.09 | 65.00 | -7.09 | 19.93 | 18.15 | 20.00 | 4.56 | 4.12 |
| DIVERGENCE_CONTINUATION | filtered | 101 | 58.16 | 64.09 | 5.93 | 20.13 | 19.83 | 17.17 | 1.29 | 11.09 |
| DIVERGENCE_CONTINUATION | kept | 87 | 69.61 | 65.00 | -4.61 | 21.04 | 19.49 | 17.51 | 1.57 | -0.56 |
| FAILED_AUCTION_RECLAIM | filtered | 44 | 56.37 | 62.89 | 6.52 | 20.60 | 18.57 | 20.00 | 2.59 | 8.15 |
| FAILED_AUCTION_RECLAIM | kept | 138 | 64.06 | 65.00 | 0.94 | 20.68 | 17.93 | 20.00 | 4.51 | 5.17 |
| FUNDING_EXTREME_SIGNAL | filtered | 40 | 51.42 | 63.62 | 12.20 | 19.26 | 15.49 | 17.07 | 2.92 | 3.92 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 69.15 | 65.00 | -4.15 | 21.60 | 14.00 | 17.05 | 4.00 | 2.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 4 | 57.67 | 63.75 | 6.08 | 21.15 | 18.80 | 16.90 | 3.25 | 8.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 81 | 69.92 | 65.00 | -4.92 | 20.21 | 18.56 | 17.38 | 1.96 | 0.72 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 48.90 | 65.00 | 16.10 | 21.20 | 20.00 | 15.80 | 0.00 | 21.60 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 65.50 | 65.00 | -0.50 | 20.80 | 19.80 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 28 | 62.09 | 65.00 | 2.91 | 18.34 | 17.04 | 18.82 | 0.00 | 5.14 |
| MEAN_REVERT | kept | 100 | 70.19 | 65.00 | -5.19 | 20.94 | 15.43 | 19.04 | 0.00 | 0.22 |
| MOVER_AVWAP_SCALP | filtered | 271 | 54.67 | 62.59 | 7.92 | 19.37 | 15.51 | 15.80 | 3.87 | 16.60 |
| MOVER_AVWAP_SCALP | kept | 504 | 76.36 | 65.00 | -11.36 | 19.92 | 16.01 | 15.80 | 4.14 | 1.08 |
| MOVER_TREND_PULLBACK | filtered | 1424 | 57.70 | 63.84 | 6.14 | 19.76 | 18.43 | 15.80 | 4.20 | 15.50 |
| MOVER_TREND_PULLBACK | kept | 4657 | 76.33 | 65.00 | -11.33 | 19.87 | 18.62 | 15.80 | 4.57 | 1.67 |
| QUIET_COMPRESSION_BREAK | filtered | 202 | 48.29 | 64.70 | 16.41 | 21.06 | 19.35 | 20.00 | 0.00 | 9.72 |
| QUIET_COMPRESSION_BREAK | kept | 688 | 77.74 | 65.00 | -12.74 | 20.87 | 19.73 | 20.00 | 0.00 | -0.91 |
| SR_FLIP_RETEST | kept | 1 | 83.50 | 65.00 | -18.50 | 21.00 | 20.00 | 19.80 | 2.50 | -3.00 |
| TREND_PULLBACK_EMA | filtered | 21 | 53.24 | 65.00 | 11.76 | 20.27 | 19.62 | 16.92 | 5.26 | 16.60 |
| TREND_PULLBACK_EMA | kept | 124 | 81.31 | 65.00 | -16.31 | 20.23 | 19.86 | 17.31 | 5.50 | 0.08 |
| VOLUME_SURGE_BREAKOUT | filtered | 22 | 59.81 | 65.00 | 5.19 | 21.13 | 17.60 | 20.00 | 4.39 | 3.60 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 75.77 | 65.00 | -10.77 | 18.17 | 17.10 | 19.57 | 4.67 | 4.33 |
| WHALE_MOMENTUM | filtered | 42 | 41.29 | 63.86 | 22.57 | 22.84 | 14.57 | 17.00 | 0.00 | 12.06 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 8 | 72.09 | 14.25 | 17.00 | 12.75 | 13.62 | 4.69 | 9.34 | 4.56 |
| DIVERGENCE_CONTINUATION | filtered | 101 | 58.16 | 23.18 | 14.34 | 4.87 | 12.88 | 5.24 | 8.84 | 1.29 |
| DIVERGENCE_CONTINUATION | kept | 87 | 69.61 | 20.95 | 13.75 | 6.34 | 13.07 | 6.27 | 8.81 | 1.57 |
| FAILED_AUCTION_RECLAIM | filtered | 44 | 56.37 | 22.41 | 15.36 | 8.45 | 12.43 | 5.61 | 5.16 | 2.59 |
| FAILED_AUCTION_RECLAIM | kept | 138 | 64.06 | 24.42 | 17.45 | 3.28 | 8.96 | 7.42 | 3.19 | 4.51 |
| FUNDING_EXTREME_SIGNAL | filtered | 40 | 51.42 | 23.60 | 10.10 | 4.28 | 12.50 | 6.92 | 5.88 | 2.92 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 69.15 | 21.00 | 13.00 | 4.50 | 12.00 | 10.00 | 7.15 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 4 | 57.67 | 17.00 | 14.00 | 3.75 | 13.50 | 5.00 | 9.18 | 3.25 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 81 | 69.92 | 22.90 | 14.05 | 5.15 | 13.26 | 6.47 | 6.92 | 1.96 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 48.90 | 17.00 | 14.00 | 12.00 | 11.00 | 8.50 | 8.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 65.50 | 17.00 | 14.00 | 6.00 | 14.00 | 8.50 | 6.00 | 0.00 |
| MEAN_REVERT | filtered | 28 | 62.09 | 25.00 | 14.14 | 4.18 | 12.00 | 5.18 | 6.74 | 0.00 |
| MEAN_REVERT | kept | 100 | 70.19 | 22.42 | 14.84 | 9.93 | 12.00 | 5.06 | 6.17 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 271 | 54.67 | 19.69 | 18.46 | 8.73 | 13.01 | 5.80 | 5.86 | 3.87 |
| MOVER_AVWAP_SCALP | kept | 504 | 76.36 | 19.30 | 18.12 | 9.15 | 13.40 | 5.62 | 7.89 | 4.14 |
| MOVER_TREND_PULLBACK | filtered | 1424 | 57.70 | 18.72 | 18.09 | 7.91 | 13.06 | 5.58 | 8.82 | 4.20 |
| MOVER_TREND_PULLBACK | kept | 4657 | 76.33 | 19.30 | 18.02 | 8.22 | 13.37 | 5.83 | 9.01 | 4.57 |
| QUIET_COMPRESSION_BREAK | filtered | 202 | 48.29 | 18.70 | 16.59 | 11.51 | 13.93 | 6.53 | 4.27 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 688 | 77.74 | 18.84 | 17.91 | 11.47 | 13.97 | 7.04 | 8.61 | 0.00 |
| SR_FLIP_RETEST | kept | 1 | 83.50 | 25.00 | 18.00 | 12.00 | 11.00 | 5.00 | 10.00 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 21 | 53.24 | 11.67 | 18.00 | 7.50 | 15.57 | 7.50 | 9.22 | 5.26 |
| TREND_PULLBACK_EMA | kept | 124 | 81.31 | 20.17 | 18.02 | 7.78 | 15.43 | 6.55 | 9.04 | 5.50 |
| VOLUME_SURGE_BREAKOUT | filtered | 22 | 59.81 | 21.73 | 18.00 | 12.00 | 14.00 | 5.00 | 3.30 | 4.39 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 75.77 | 19.67 | 15.33 | 12.00 | 14.00 | 5.00 | 9.43 | 4.67 |
| WHALE_MOMENTUM | filtered | 42 | 41.29 | 24.05 | 12.52 | 8.43 | 13.00 | 8.42 | 1.93 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 8 | 72.09 | 0.00 | 0.00 | 1.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.50** |
| DIVERGENCE_CONTINUATION | filtered | 101 | 58.16 | 0.00 | 0.00 | 2.09 | 0.00 | 1.81 | 0.00 | 0.00 | 0.00 | **3.90** |
| DIVERGENCE_CONTINUATION | kept | 87 | 69.61 | 0.00 | 0.00 | 0.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.55** |
| FAILED_AUCTION_RECLAIM | filtered | 44 | 56.37 | 0.00 | 0.00 | 0.00 | 0.00 | 2.95 | 0.00 | 0.00 | 0.00 | **2.95** |
| FAILED_AUCTION_RECLAIM | kept | 138 | 64.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 40 | 51.42 | 0.00 | 0.00 | 2.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.04** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 69.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 4 | 57.67 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 81 | 69.92 | 0.00 | 0.00 | 0.79 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.79** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 48.90 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 65.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 28 | 62.09 | 0.00 | 0.00 | 5.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.14** |
| MEAN_REVERT | kept | 100 | 70.19 | 0.00 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.22** |
| MOVER_AVWAP_SCALP | filtered | 271 | 54.67 | 0.00 | 0.00 | 2.52 | 0.00 | 0.00 | 0.00 | 0.00 | 2.78 | **5.30** |
| MOVER_AVWAP_SCALP | kept | 504 | 76.36 | 0.03 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.12 | **0.65** |
| MOVER_TREND_PULLBACK | filtered | 1424 | 57.70 | 0.00 | 0.00 | 3.45 | 0.00 | 0.64 | 0.01 | 0.00 | 0.09 | **4.19** |
| MOVER_TREND_PULLBACK | kept | 4657 | 76.33 | 0.00 | 0.00 | 1.12 | 0.00 | 0.16 | 0.00 | 0.00 | 0.00 | **1.28** |
| QUIET_COMPRESSION_BREAK | filtered | 202 | 48.29 | 0.00 | 0.00 | 0.71 | 0.00 | 0.08 | 0.00 | 0.00 | 5.99 | **6.78** |
| QUIET_COMPRESSION_BREAK | kept | 688 | 77.74 | 0.00 | 0.00 | 0.07 | 0.00 | 0.07 | 0.00 | 0.00 | 0.00 | **0.14** |
| SR_FLIP_RETEST | kept | 1 | 83.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 21 | 53.24 | 0.00 | 0.00 | 4.34 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.34** |
| TREND_PULLBACK_EMA | kept | 124 | 81.31 | 0.00 | 0.00 | 1.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.26** |
| VOLUME_SURGE_BREAKOUT | filtered | 22 | 59.81 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 75.77 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 42 | 41.29 | 0.00 | 0.00 | 0.00 | 0.00 | 2.06 | 0.00 | 0.00 | 0.00 | **2.06** |

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
- Outcomes recorded: **141757 held of 287513 seen** across 21 strategies; 3197 cells past the sample floor; **1282 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 33512 | 215/33297/0 | 51% | -0.04 | ASIA/MARKUP/CASCADE/BTC_RISING/MIDCAP (+1.24R) | ASIA/MARKDOWN/CASCADE/BTC_RISING (-1.20R) |
| FAILED_AUCTION_RECLAIM | 17358 | 19/17339/0 | 52% | +0.00 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16586 | 1/16585/0 | 48% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 12264 | 6/12258/0 | 46% | -0.10 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.37R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 9770 | 0/9770/0 | 47% | -0.08 | NY/QUIET/EXPANDED/BTC_RISING/ALTCOIN (+1.21R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 9682 | 28/9654/0 | 35% | -0.30 | LONDON/DISTRIBUTION/EXPANDED/BTC_RISING (+1.12R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| TREND_PULLBACK_EMA | 5881 | 2/5879/0 | 47% | -0.24 | NY/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.07R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_FALLING/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 5273 | 0/0/5273 | 43% | -0.08 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.70R) | LONDON/MARKUP/CASCADE/BTC_RISING (-0.98R) |
| LIQUIDITY_SWEEP_REVERSAL | 5114 | 11/5103/0 | 46% | -0.20 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_RANGE_FADE | 4839 | 0/0/4839 | 37% | +0.01 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL (+0.65R) | OVERLAP/QUIET/NORMAL/BTC_RISING (-1.28R) |
| MEAN_REVERT | 4615 | 2/4613/0 | 69% | +0.34 | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.32R) | LONDON/QUIET/NORMAL/BTC_NEUTRAL/MAJOR (-1.54R) |
| SHADOW_FUNDING_FADE | 4377 | 0/0/4377 | 37% | -0.36 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.22R) | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING (-1.02R) |
| RANGE_FADE | 4002 | 0/4002/0 | 31% | -0.42 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.87R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-1.38R) |
| VOLUME_SURGE_BREAKOUT | 2626 | 19/2607/0 | 42% | +0.04 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+2.68R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2481 | 4/2477/0 | 31% | -0.46 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.32R) |
| WHALE_MOMENTUM | 2042 | 0/2042/0 | 45% | -0.27 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (-0.89R) |
| SHADOW_CASCADE_REVERSAL | 567 | 0/0/567 | 48% | -0.16 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-2.17R) |
| BREAKDOWN_SHORT | 527 | 9/518/0 | 45% | +0.03 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.67R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.08R) |
| LIQUIDATION_REVERSAL | 128 | 0/128/0 | 33% | -0.81 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | NY/VOLATILE_EXPANSION/NORMAL/BTC_FALLING (-1.17R) |
| POST_DISPLACEMENT_CONTINUATION | 73 | 0/73/0 | 85% | +0.69 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 40 | 1/39/0 | 38% | -0.39 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +3.19R (n=19, STRONG)
- **Weakest cells**: `SHADOW_CASCADE_REVERSAL @ OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL` -2.17R (n=16, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 121 | 36% / -0.40R | 121 | 57% / -0.09R | +0.30 | **ATR** |
| TREND_PULLBACK_EMA | 246 | 42% / -0.31R | 246 | 48% / -0.11R | +0.20 | **ATR** |
| MOVER_AVWAP_SCALP | 638 | 38% / -0.22R | 638 | 42% / -0.10R | +0.12 | **ATR** |
| SR_FLIP_RETEST | 2781 | 46% / -0.20R | 2781 | 49% / -0.10R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 973 | 47% / -0.11R | 973 | 53% / -0.05R | +0.06 | **ATR** |
| MOVER_TREND_PULLBACK | 4298 | 51% / -0.07R | 4298 | 54% / -0.01R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 771 | 51% / -0.17R | 771 | 55% / -0.11R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 17 | 35% / -0.25R | 17 | 35% / -0.20R | +0.05 | **ATR** |
| RANGE_FADE | 262 | 21% / -0.61R | 262 | 23% / -0.58R | +0.03 | **ATR** |
| MEAN_REVERT | 485 | 53% / -0.01R | 485 | 49% / +0.01R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1585 | 44% / -0.14R | 1585 | 44% / -0.16R | -0.02 | **FIXED** |
| VOLUME_SURGE_BREAKOUT | 90 | 41% / -0.02R | 90 | 52% / -0.04R | -0.02 | **FIXED** |
| WHALE_MOMENTUM | 159 | 51% / -0.24R | 159 | 50% / -0.25R | -0.01 | **FIXED** |
| BREAKDOWN_SHORT | 22 | 32% / -0.21R | 22 | 32% / -0.20R | +0.01 | **ATR** |
| FAILED_AUCTION_RECLAIM | 2315 | 47% / -0.11R | 2315 | 47% / -0.11R | +0.00 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 10 | 60% / +0.10R | 10 | 60% / +0.02R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 8 | 25% / -0.94R | 8 | 50% / -0.27R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 6278 | 30% | -0.14R | 287 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 628 | 41% | -0.11R | 139 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 41 | 59% | +0.02R | 22 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1240 | 29% / -1.66R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 30 | 30% / -0.36R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 5288 | 39% / -0.14R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 1033 | 32% / -0.55R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 105 | 22% / -0.87R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 826 | 33% / -1.35R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 1111 | 37% / -0.13R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 420 | 44% / -0.84R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 144 | 31% / -1.11R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 293 | 30% / -0.55R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 712 | 32% / -0.30R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 21 | 19% / -0.73R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 219 | 45% / -0.15R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 90 | 39% / -0.16R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 8 | 25% / -0.67R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 9 | 22% / -1.09R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 51 | 45% / -0.25R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 47 · alerting: **6** · boot grace active: False
- **ALERT** `candle_coverage` — 90/110 symbols with ≥20 15m candles, 69/110 updated within 45m (streak 50/6) (sustained 50 cycles)
- **ALERT** `cohort_edge_gate` — all 28 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 28 cohorts, 13 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 160/6) (sustained 160 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 4734x (gate reads 0x, withheld 0x — refusal dark); last ROBOUSDT age=3882.4s (streak 100/6) (sustained 100 cycles)
- **ALERT** `edge_reconciliation` — MOVER_AVWAP_SCALP realized−counterfactual=+0.40R (bound 0.3) (streak 160/6) (sustained 160 cycles)
- **ALERT** `mean_revert_emission` — 631 detections since last emission (emitted_total=21) — and the POST-SCORING blocked candidates measure +0.34R over n=4613, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 14/6) (sustained 14 cycles)
- **ALERT** `tuned_variants` — 126 non-stamps — atr_arm_uncomputable=126 (seen=2511 stamped=406 skipped=1979) (streak 150/6) (sustained 150 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 32402512 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 7 arms current, none stalled; covering 105/105 signals (100%) | 0 |
| auto_dispatch | ok | attempts=5 fanouts=5 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 62998.90 | 0 |
| candle_coverage | violating | 90/110 symbols with ≥20 15m candles, 69/110 updated within 45m (streak 50/6) | 50 |
| candle_series_integrity | ok | merge dropped 353 dup bars, 0 undedupable; ws 0 out-of-order, 124 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 28 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 28 cohorts, 13 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 160/6) | 160 |
| context_emission_policy | ok | output +44 / upstream +33 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 789/789 signals (100%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today | 0 |
| dark_resolution | violating | 3 of 93 open dark rows are not being advanced (worst: COOKIEUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 96/120) | 96 |
| dark_sar_arms | ok | no open arms; covering 807/807 signals (100%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 4538008 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.40R (bound 0.3) (streak 160/6) | 160 |
| emission_controller | ok | last cycle 1749s ago; live_overrides=26 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=14 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4188 stamps (MEAN_REVERT=812, MOVER_AVWAP_SCALP=147, MOVER_TREND_PULLBACK=2658, RANGE_FADE=468, TREND_PULLBACK_EMA=103), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | 4295 evaluated, 792 suppressed, 665 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +7 / upstream +221 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 631 detections since last emission (emitted_total=21) — and the POST-SCORING blocked candidates measure +0.34R over n=4613, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 14/6) | 14 |
| mean_revert_path | ok | output +33 / upstream +221 | 0 |
| mover_admission_metadata | ok | 865 symbols known, 163 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 3 held, 3 with scan counts, 3 with an activity reading (measuring only) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3036 rows held, 512319 evicted (sampled: execution:overextended 400/189955, execution:trigger_not_confirmed 400/174249, setup_compat:regime_STRONG_TREND 400/62197) | 0 |
| price_action_lane | ok | 312061 evaluated, 333 emitted; layer1 333 stamped / 0 blind; cooldown=32676, delta_opposed=22636, no_footprint=89670, no_opposing_target=1823, no_sweep=145192, rr_below_floor=19731 | 0 |
| promoted_pair_integrity | ok | 3/3 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.42R over n=4002 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | violating | upstream +221 but output +0 (streak 2/72) | 2 |
| sar_alignment_crosscheck | ok | 523/11518 disagreed (4.5%) | 0 |
| sar_exit_shadow | ok | output +8 / upstream +221 | 0 |
| sar_hold_arm | ok | 185 held arms settled, 36 unscored, 7 still walking (4 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 27/95 unfetchable (28%); top cause: gap or duplicate bar in the 15m window; symbols: AVAAIUSDT, BEATUSDT, BICOUSDT, EDENUSDT, GPSUSDT +4 more | 0 |
| sar_live_arms | ok | 7 arms current, none stalled; covering 114/114 signals (100%) | 0 |
| sar_refresh_budget | ok | 1 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 495 records await one (68 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| setup_tf_resolver | ok | 115692 resolutions, 70064 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 12m ago | 0 |
| stale_tf_scoring | violating | scored on stale TF 4734x (gate reads 0x, withheld 0x — refusal dark); last ROBOUSDT age=3882.4s (streak 100/6) | 100 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +41 / upstream +221 | 0 |
| structural_snap | ok | 4163/4163 measured, 21 blind, 0 levels moved (refusals: redetect_cooldown=660) | 0 |
| structural_veto_lane | ok | 1125 stamped; 0 with no readable level book, 40 with clear air ahead, 713 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +221 / upstream +33 | 0 |
| tuned_variants | violating | 126 non-stamps — atr_arm_uncomputable=126 (seen=2511 stamped=406 skipped=1979) (streak 150/6) | 150 |

Fail-open exception counters (nonzero sites):
- `feature_liveness.probe.footprint_bars`: 1 — last: RuntimeError: deque mutated during iteration

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2320633`
- `Path funnel` emissions: `60`
- `Regime distribution` emissions: `60`
- `QUIET_SCALP_BLOCK` events: `227`
- `confidence_gate` events: `8594`
- `free_channel_post` events: `14`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **9**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 3 | 2244 | 2244 | 5289 | 0 |
| futures_liq | 6 | 2998 | 6153 | 26642 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **14**

| Source | Count |
|---|---:|
| signal_close | 9 |
| regime_shift | 5 |

- By severity: HIGH=14

## Dependency readiness
- cvd: presence[present=376206] state[populated=376206] buckets[many=376206] sources[none] quality[none]
- funding_rate: presence[absent=50950, present=325256] state[empty=50950, populated=325256] buckets[few=325256, none=50950] sources[none] quality[none]
- liquidation_clusters: presence[absent=207376, present=168830] state[empty=207376, populated=168830] buckets[few=135055, none=207376, some=33775] sources[none] quality[none]
- oi_snapshot: presence[absent=49694, present=326512] state[empty=49694, populated=326512] buckets[many=326512, none=49694] sources[none] quality[none]
- order_book: presence[absent=105833, present=270373] state[populated=270373, unavailable=105833] buckets[few=270373, none=105833] sources[book_ticker=270373, unavailable=105833] quality[none=105833, top_of_book_only=270373]
- orderblocks: presence[absent=376206] state[empty=376206] buckets[none=376206] sources[measured_dark=376206] quality[none]
- recent_ticks: presence[present=376206] state[populated=376206] buckets[many=376206] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `12.845545053482056` sec
- Median create→first breach: `1550.3382787704468` sec
- Median create→terminal: `1574.332808971405` sec
- Median first breach→terminal: `3.238384962081909` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 1.6979947063837473 | 1.9794229478863783 | 0.8578230883888968 | 0 | 1 |
| MOVER_TREND_PULLBACK | 8 | 8 | 4.947431143789137 | 3.0 | 1.649143714596379 | 6 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 2.547 | 15073.539937019348 | 15077.327465057373 |
| MOVER_TREND_PULLBACK | 8 | 8 | 0.0 | 37.5 | 0.0 | 0.0 | -0.5181 | 1206.2646483182907 | 1218.7580344676971 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 124 | 1 | 47 | 0.0 | 0.0 | None | None | 77 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2487 | 16 | 2232 | 0.0 | 0.0 | None | None | 255 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `617`
- Gating Δ: `55313`
- No-generation Δ: `1402599`
- Fast failures Δ: `-1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.5406, "current_avg_pnl": -0.5181, "current_win_rate": 0.0, "previous_avg_pnl": 0.0225, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 77, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 16, "geometry_changed_delta": 0, "geometry_preserved_delta": 255, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
