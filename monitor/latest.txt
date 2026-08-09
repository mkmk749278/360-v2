# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `8893` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 117 | 117 | 84 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 17021 | 17021 | 15831 | 10 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 120027 | 120032 | 15 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 98523 | 98539 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 98148 | 95304 | 3202 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 98571 | 97979 | 640 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 104044 | 103542 | 543 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 95244 | 95258 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 98620 | 98663 | 11 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 98682 | 94235 | 5865 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 124909 | 128703 | 811 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 120053 | 112638 | 12220 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 103635 | 103642 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 98543 | 98540 | 26 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 98092 | 97507 | 636 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 100108 | 98114 | 2769 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 97650 | 97895 | 146 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 89287 | 86720 | 2713 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 89434 | 88836 | 655 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 119997 | 120015 | 10 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 95262 | 95260 | 49 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2149 | 2149 | 1606 | 5 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1726 | 1726 | 400 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 15 | 15 | 15 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 14852 | 14852 | 14511 | 18 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 15 | 15 | 5 | 4 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 17072 | 17072 | 14980 | 8 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2453 | 2453 | 414 | 41 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 43093 | 43093 | 29135 | 276 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 78 | 78 | 77 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 4255 | 4255 | 2173 | 60 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 9493 | 9493 | 9000 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 498 | 498 | 447 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3097 | 3097 | 2848 | 18 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 162 | 162 | 20 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 9269 | 9269 | 125 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=120032): breakout_not_found=58740, basic_filters_failed=39340, move_not_fresh=10294, volume_spike_missing=5774, breakout_stale=3754, retest_proximity_failed=1524, insufficient_candles=511, ema_alignment_reject=94, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=98539): cls_disabled_merged_into_lsr=98539
- **EVAL::DIVERGENCE_CONTINUATION** (total=95304): cvd_divergence_failed=35965, basic_filters_failed=32116, h1_trend_not_aligned=21177, ema_alignment_reject=4592, retest_proximity_failed=1117, missing_fvg_or_orderblock=316, regime_blocked=20, cvd_insufficient=1
- **EVAL::FAILED_AUCTION_RECLAIM** (total=97979): auction_not_detected=59094, basic_filters_failed=31168, regime_blocked=3868, reclaim_hold_failed=2455, tail_too_small=1246, rsi_reject=148
- **EVAL::FUNDING_EXTREME** (total=103542): funding_not_extreme=62778, basic_filters_failed=33674, ema_alignment_reject=4954, rsi_reject=762, cvd_divergence_failed=544, momentum_reject=542, missing_funding_rate=180, missing_fvg_or_orderblock=72, insufficient_candles=36
- **EVAL::LIQUIDATION_REVERSAL** (total=95258): cascade_threshold_not_met=60576, basic_filters_failed=33342, cvd_divergence_failed=538, rsi_reject=443, insufficient_candles=317, missing_fvg_or_orderblock=32, volume_spike_missing=10
- **EVAL::MA_CROSS_TREND_SHIFT** (total=98663): no_ma_cross=64984, basic_filters_failed=32137, ma_cross_cooldown=918, ma_cross_htf_misaligned=624
- **EVAL::MEAN_REVERT** (total=94235): no_extension=75673, basic_filters_failed=18552, insufficient_candles=10
- **EVAL::MOVER_AVWAP_SCALP** (total=128703): no_mover_leg=44790, basic_filters_failed=39020, no_avwap_tag=32475, avwap_slope_against=6369, avwap_reclaim_no_volume=2558, insufficient_candles=1764, no_avwap_reclaim=1712, anchor_too_recent=15
- **EVAL::MOVER_TREND_PULLBACK** (total=112638): mover_run_too_small=49754, basic_filters_failed=38794, no_reclaim=15850, no_ma_stack=3397, no_pullback_tag=2928, insufficient_candles=1915
- **EVAL::OPENING_RANGE_BREAKOUT** (total=103642): feature_disabled=103642
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=98540): regime_blocked=74638, breakout_not_found=16413, basic_filters_failed=4916, adx_reject=2544, ema_alignment_reject=29
- **EVAL::QUIET_COMPRESSION_BREAK** (total=97507): regime_blocked=27717, compression_not_detected=26440, basic_filters_failed=26237, breakout_not_detected=14951, volume_confirmation_failed=1830, rsi_reject=189, macd_reject=98, volume_reject=28, missing_fvg_or_orderblock=17
- **EVAL::RANGE_FADE** (total=98114): no_range_edge=79535, basic_filters_failed=18534, insufficient_candles=45
- **EVAL::SR_FLIP_RETEST** (total=97895): flip_close_not_confirmed=58915, basic_filters_failed=31135, regime_blocked=3848, long_break_volume_thin=1219, h1_break_not_confirmed=1207, retest_out_of_zone=972, reclaim_hold_failed=307, whipsaw_flip=116, long_acceptance_not_held=89, wick_quality_failed=57, ema_alignment_reject=24, missing_fvg_or_orderblock=6
- **EVAL::STANDARD** (total=86720): momentum_reject=27989, adx_reject=21741, basic_filters_failed=14549, sweeps_not_detected=10576, macd_reject=6436, ema_alignment_reject=2914, htf_poi_unanchored=2291, rsi_reject=179, invalid_sl_geometry=42, mtf_reject=3
- **EVAL::TREND_PULLBACK** (total=88836): h1_trend_not_aligned=33597, basic_filters_failed=13715, ema_alignment_reject=12398, h1_pullback_not_confirmed=9401, no_ema_reclaim_close=5888, ema_not_tested_prev=4703, body_conviction_fail=3667, rsi_reject=2553, prev_already_above_emas=1116, no_prev_high_break=539, prev_already_below_emas=519, no_prev_low_break=357, momentum_flat=213, missing_fvg_or_orderblock=65, regime_blocked=38, momentum_reject=34, ema21_not_tagged=33
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=120015): breakout_not_found=57509, basic_filters_failed=39336, move_not_fresh=11412, volume_spike_missing=5646, breakout_stale=4085, retest_proximity_failed=1466, insufficient_candles=511, move_exhausted=26, ema_alignment_reject=16, missing_fvg_or_orderblock=8
- **EVAL::WHALE_MOMENTUM** (total=95260): momentum_reject=56790, recent_ticks_insufficient=25169, basic_filters_failed=13301

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=45): execution:overextended=45
- **DIVERGENCE_CONTINUATION** (total=542): setup_compat:regime_VOLATILE_UNSUITABLE=542
- **FAILED_AUCTION_RECLAIM** (total=1114): execution:overextended=559, setup_compat:regime_STRONG_TREND=321, context_floor=141, setup_compat:regime_VOLATILE_UNSUITABLE=93
- **FUNDING_EXTREME_SIGNAL** (total=1528): execution:trigger_not_confirmed=1454, context_floor=74
- **LIQUIDATION_REVERSAL** (total=15): execution:trigger_not_confirmed=15
- **LIQUIDITY_SWEEP_REVERSAL** (total=4251): execution:overextended=1874, execution:trigger_not_confirmed=1230, setup_compat:regime_STRONG_TREND=1147
- **MA_CROSS_TREND_SHIFT** (total=18): setup_compat:regime_CLEAN_RANGE=7, execution:trigger_not_confirmed=5, setup_compat:regime_DIRTY_RANGE=4, execution:overextended=1, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=5903): setup_compat:regime_WEAK_TREND=2663, setup_compat:regime_STRONG_TREND=2563, execution:overextended=581, entry_quality=96
- **MOVER_AVWAP_SCALP** (total=1830): execution:overextended=1084, entry_quality=422, execution:trigger_not_confirmed=324
- **MOVER_TREND_PULLBACK** (total=25557): execution:overextended=12700, execution:trigger_not_confirmed=10237, entry_quality=2620
- **QUIET_COMPRESSION_BREAK** (total=1057): context_floor=671, execution:trigger_not_confirmed=386
- **RANGE_FADE** (total=6325): setup_compat:regime_STRONG_TREND=2674, setup_compat:regime_WEAK_TREND=1857, execution:overextended=974, setup_compat:regime_VOLATILE_UNSUITABLE=723, context_edge=55, setup_compat:regime_BREAKOUT_EXPANSION=42
- **TREND_PULLBACK_EMA** (total=2949): setup_compat:regime_CLEAN_RANGE=2296, setup_compat:regime_DIRTY_RANGE=433, setup_compat:regime_VOLATILE_UNSUITABLE=177, entry_quality=43
- **VOLUME_SURGE_BREAKOUT** (total=47): execution:overextended=35, context_floor=12
- **WHALE_MOMENTUM** (total=9144): execution:trigger_not_confirmed=9144

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 299163 | 37.2% |
| QUIET | 251459 | 31.3% |
| TRENDING_UP | 112714 | 14.0% |
| TRENDING_DOWN | 93470 | 11.6% |
| VOLATILE | 46530 | 5.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **290**
- Average confidence gap to threshold: **9.45** (samples=290) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: LINKUSDT=30, ETHUSDT=29, HYPEUSDT=24, XMRUSDT=22, TAOUSDT=19, ENAUSDT=14, BNBUSDT=13, 1000BONKUSDT=13, XRPUSDT=13, ONDOUSDT=12

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 2 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 14 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 214 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 7 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 107 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 14 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 61 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 56 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 30 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 111 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 4 |
| MEAN_REVERT | filtered | min_confidence | 26 |
| MEAN_REVERT | kept | min_confidence_pass | 29 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 437 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 16 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 668 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1176 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 27 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 5126 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 228 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 28 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 665 |
| RANGE_FADE | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 26 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 10 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 50 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 103 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 112 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 23 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 2 | 58.30 | 65.00 | 6.70 | 21.20 | 18.30 | 20.00 | 3.00 | 9.00 |
| BREAKDOWN_SHORT | kept | 14 | 67.34 | 65.00 | -2.34 | 21.07 | 15.94 | 20.00 | 3.54 | 3.43 |
| DIVERGENCE_CONTINUATION | filtered | 221 | 58.24 | 63.94 | 5.70 | 19.73 | 19.42 | 18.18 | 1.54 | 11.48 |
| DIVERGENCE_CONTINUATION | kept | 107 | 69.46 | 65.00 | -4.46 | 20.29 | 19.88 | 17.75 | 1.48 | -1.50 |
| FAILED_AUCTION_RECLAIM | filtered | 14 | 52.47 | 64.71 | 12.24 | 20.39 | 17.39 | 20.00 | 1.21 | 6.64 |
| FAILED_AUCTION_RECLAIM | kept | 61 | 70.38 | 65.00 | -5.38 | 21.45 | 17.39 | 20.00 | 4.27 | 1.79 |
| FUNDING_EXTREME_SIGNAL | filtered | 59 | 52.97 | 65.00 | 12.03 | 20.00 | 15.06 | 17.00 | 3.07 | 3.85 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 30 | 58.93 | 65.00 | 6.07 | 19.75 | 19.93 | 17.28 | 4.47 | 8.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 111 | 69.77 | 65.00 | -4.77 | 19.96 | 18.28 | 19.12 | 0.97 | 1.60 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 69.28 | 65.00 | -4.28 | 20.98 | 18.73 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 26 | 57.49 | 63.85 | 6.36 | 21.21 | 14.74 | 16.66 | 0.00 | 7.54 |
| MEAN_REVERT | kept | 29 | 67.46 | 65.00 | -2.46 | 21.46 | 16.80 | 17.83 | 0.00 | 0.46 |
| MOVER_AVWAP_SCALP | filtered | 455 | 56.54 | 62.72 | 6.18 | 21.08 | 15.91 | 15.80 | 3.64 | 7.59 |
| MOVER_AVWAP_SCALP | kept | 668 | 79.54 | 65.00 | -14.54 | 20.14 | 16.43 | 15.80 | 4.36 | 0.56 |
| MOVER_TREND_PULLBACK | filtered | 1203 | 56.65 | 64.23 | 7.58 | 19.82 | 17.97 | 15.80 | 4.05 | 17.02 |
| MOVER_TREND_PULLBACK | kept | 5126 | 76.44 | 65.00 | -11.44 | 20.02 | 18.74 | 15.80 | 4.61 | 1.20 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 68.70 | 65.00 | -3.70 | 17.60 | 20.00 | 19.40 | 4.50 | -3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 256 | 56.12 | 65.00 | 8.88 | 20.88 | 19.65 | 20.00 | 0.00 | 5.50 |
| QUIET_COMPRESSION_BREAK | kept | 665 | 76.80 | 65.00 | -11.80 | 20.40 | 19.74 | 20.00 | 0.00 | -0.62 |
| RANGE_FADE | kept | 1 | 69.30 | 65.00 | -4.30 | 21.20 | 16.30 | 19.20 | 0.00 | -3.00 |
| SR_FLIP_RETEST | filtered | 26 | 58.21 | 65.00 | 6.79 | 21.45 | 20.00 | 15.20 | 1.00 | 14.52 |
| SR_FLIP_RETEST | kept | 10 | 69.24 | 65.00 | -4.24 | 21.09 | 20.00 | 18.37 | 2.60 | 2.40 |
| TREND_PULLBACK_EMA | filtered | 50 | 57.48 | 65.00 | 7.52 | 20.42 | 19.82 | 17.27 | 4.62 | 11.08 |
| TREND_PULLBACK_EMA | kept | 103 | 76.83 | 65.00 | -11.83 | 20.36 | 19.80 | 17.08 | 4.77 | 0.35 |
| VOLUME_SURGE_BREAKOUT | filtered | 112 | 44.73 | 63.62 | 18.89 | 20.25 | 17.80 | 20.00 | 3.55 | 14.26 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 70.00 | 65.00 | -5.00 | 17.10 | 19.40 | 20.00 | 6.00 | 3.00 |
| WHALE_MOMENTUM | filtered | 23 | 50.74 | 65.00 | 14.26 | 20.94 | 14.00 | 17.00 | 0.00 | 16.57 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 2 | 58.30 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 2.30 | 3.00 |
| BREAKDOWN_SHORT | kept | 14 | 67.34 | 17.57 | 14.00 | 12.00 | 12.71 | 5.00 | 5.94 | 3.54 |
| DIVERGENCE_CONTINUATION | filtered | 221 | 58.24 | 23.41 | 11.57 | 5.96 | 13.24 | 5.80 | 8.20 | 1.54 |
| DIVERGENCE_CONTINUATION | kept | 107 | 69.46 | 22.98 | 8.84 | 6.56 | 13.94 | 7.14 | 9.04 | 1.48 |
| FAILED_AUCTION_RECLAIM | filtered | 14 | 52.47 | 17.71 | 14.29 | 13.50 | 14.00 | 8.00 | 4.33 | 1.21 |
| FAILED_AUCTION_RECLAIM | kept | 61 | 70.38 | 20.41 | 17.54 | 4.67 | 12.49 | 6.86 | 5.97 | 4.27 |
| FUNDING_EXTREME_SIGNAL | filtered | 59 | 52.97 | 25.00 | 10.24 | 8.54 | 13.07 | 7.96 | 2.16 | 3.07 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 30 | 58.93 | 22.07 | 14.00 | 4.10 | 12.00 | 5.00 | 5.30 | 4.47 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 111 | 69.77 | 22.08 | 16.16 | 7.78 | 12.55 | 5.07 | 6.75 | 0.97 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 69.28 | 19.00 | 14.00 | 9.00 | 12.25 | 5.88 | 9.15 | 0.00 |
| MEAN_REVERT | filtered | 26 | 57.49 | 25.00 | 17.54 | 3.00 | 12.00 | 5.40 | 5.55 | 0.00 |
| MEAN_REVERT | kept | 29 | 67.46 | 22.52 | 17.45 | 3.93 | 12.62 | 6.59 | 4.81 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 455 | 56.54 | 18.02 | 18.00 | 8.79 | 13.33 | 5.62 | 5.76 | 3.64 |
| MOVER_AVWAP_SCALP | kept | 668 | 79.54 | 19.27 | 18.13 | 9.62 | 13.83 | 6.17 | 8.97 | 4.36 |
| MOVER_TREND_PULLBACK | filtered | 1203 | 56.65 | 18.52 | 18.03 | 7.89 | 13.07 | 5.41 | 8.92 | 4.05 |
| MOVER_TREND_PULLBACK | kept | 5126 | 76.44 | 18.72 | 18.06 | 8.19 | 13.45 | 5.96 | 8.92 | 4.61 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 68.70 | 17.00 | 18.00 | 15.00 | 14.00 | 8.50 | 6.70 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 256 | 56.12 | 18.16 | 17.56 | 11.30 | 14.44 | 6.77 | 4.20 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 665 | 76.80 | 17.97 | 17.28 | 12.30 | 14.10 | 7.56 | 8.08 | 0.00 |
| RANGE_FADE | kept | 1 | 69.30 | 17.00 | 18.00 | 12.00 | 12.00 | 5.00 | 5.30 | 0.00 |
| SR_FLIP_RETEST | filtered | 26 | 58.21 | 15.08 | 18.00 | 9.00 | 13.85 | 9.81 | 6.00 | 1.00 |
| SR_FLIP_RETEST | kept | 10 | 69.24 | 25.00 | 18.00 | 3.60 | 10.80 | 5.00 | 6.64 | 2.60 |
| TREND_PULLBACK_EMA | filtered | 50 | 57.48 | 8.00 | 18.00 | 7.50 | 15.32 | 8.37 | 8.91 | 4.62 |
| TREND_PULLBACK_EMA | kept | 103 | 76.83 | 17.73 | 18.02 | 7.50 | 15.14 | 6.00 | 8.59 | 4.77 |
| VOLUME_SURGE_BREAKOUT | filtered | 112 | 44.73 | 17.20 | 17.88 | 12.00 | 14.62 | 5.00 | 3.75 | 3.55 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 70.00 | 25.00 | 18.00 | 12.00 | 14.00 | 5.00 | 8.00 | 6.00 |
| WHALE_MOMENTUM | filtered | 23 | 50.74 | 25.00 | 8.00 | 13.43 | 11.48 | 6.98 | 2.43 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 2 | 58.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | **6.00** |
| BREAKDOWN_SHORT | kept | 14 | 67.34 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.43 | **0.43** |
| DIVERGENCE_CONTINUATION | filtered | 221 | 58.24 | 0.00 | 0.00 | 2.06 | 0.00 | 1.30 | 0.00 | 0.00 | 0.00 | **3.36** |
| DIVERGENCE_CONTINUATION | kept | 107 | 69.46 | 0.00 | 0.00 | 0.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.60** |
| FAILED_AUCTION_RECLAIM | filtered | 14 | 52.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.86 | 0.00 | 0.00 | 0.00 | **0.86** |
| FAILED_AUCTION_RECLAIM | kept | 61 | 70.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | 0.00 | **0.20** |
| FUNDING_EXTREME_SIGNAL | filtered | 59 | 52.97 | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.20** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 30 | 58.93 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 111 | 69.77 | 0.00 | 0.00 | 1.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.60** |
| MA_CROSS_TREND_SHIFT | kept | 4 | 69.28 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 26 | 57.49 | 0.00 | 0.00 | 5.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.23** |
| MEAN_REVERT | kept | 29 | 67.46 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.12 | **0.45** |
| MOVER_AVWAP_SCALP | filtered | 455 | 56.54 | 2.82 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.90 | **3.90** |
| MOVER_AVWAP_SCALP | kept | 668 | 79.54 | 0.36 | 0.00 | 0.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | **0.75** |
| MOVER_TREND_PULLBACK | filtered | 1203 | 56.65 | 1.61 | 0.00 | 1.31 | 0.00 | 0.93 | 0.00 | 0.00 | 0.06 | **3.91** |
| MOVER_TREND_PULLBACK | kept | 5126 | 76.44 | 0.00 | 0.00 | 0.94 | 0.00 | 0.26 | 0.00 | 0.00 | 0.07 | **1.27** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 68.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 256 | 56.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.39 | 0.00 | 0.00 | 2.81 | **3.20** |
| QUIET_COMPRESSION_BREAK | kept | 665 | 76.80 | 0.00 | 0.00 | 0.02 | 0.00 | 0.31 | 0.00 | 0.00 | 0.00 | **0.33** |
| RANGE_FADE | kept | 1 | 69.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 26 | 58.21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.46 | 0.00 | 0.00 | 0.00 | **0.46** |
| SR_FLIP_RETEST | kept | 10 | 69.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 50 | 57.48 | 0.00 | 0.00 | 4.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.64** |
| TREND_PULLBACK_EMA | kept | 103 | 76.83 | 0.00 | 0.00 | 0.61 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.61** |
| VOLUME_SURGE_BREAKOUT | filtered | 112 | 44.73 | 0.00 | 0.00 | 1.29 | 0.00 | 0.00 | 0.00 | 0.00 | 2.39 | **3.68** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 70.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 23 | 50.74 | 0.00 | 0.00 | 0.00 | 0.00 | 6.57 | 0.00 | 0.00 | 0.00 | **6.57** |

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
- Outcomes recorded: **128960 held of 205094 seen** across 21 strategies; 2903 cells past the sample floor; **850 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 30001 | 213/29788/0 | 51% | -0.03 | LONDON/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.25R) | OVERLAP/QUIET/COMPRESSED/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 17034 | 24/17010/0 | 51% | -0.01 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16544 | 1/16543/0 | 48% | -0.17 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 11516 | 4/11512/0 | 45% | -0.09 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.37R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 9194 | 0/9194/0 | 51% | -0.05 | NY/QUIET/EXPANDED/BTC_RISING/ALTCOIN (+1.37R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 8080 | 26/8054/0 | 32% | -0.37 | LONDON/DISTRIBUTION/EXPANDED/BTC_RISING (+1.12R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| LIQUIDITY_SWEEP_REVERSAL | 4676 | 11/4665/0 | 47% | -0.20 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.54R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 4631 | 0/0/4631 | 42% | -0.09 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.68R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL (-1.37R) |
| TREND_PULLBACK_EMA | 4607 | 2/4605/0 | 50% | -0.22 | NY/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.07R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.19R) |
| SHADOW_RANGE_FADE | 4236 | 0/0/4236 | 39% | +0.08 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.93R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.02R) |
| MEAN_REVERT | 4004 | 0/4004/0 | 74% | +0.47 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.29R) |
| SHADOW_FUNDING_FADE | 3906 | 0/0/3906 | 38% | -0.34 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.22R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-0.96R) |
| RANGE_FADE | 3475 | 0/3475/0 | 27% | -0.52 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.87R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-1.38R) |
| VOLUME_SURGE_BREAKOUT | 2444 | 13/2431/0 | 43% | +0.09 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+2.68R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2236 | 4/2232/0 | 30% | -0.48 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (-1.61R) |
| WHALE_MOMENTUM | 1402 | 0/1402/0 | 45% | -0.25 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL/MAJOR (-0.76R) |
| SHADOW_CASCADE_REVERSAL | 454 | 0/0/454 | 48% | -0.18 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.01R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.76R) |
| BREAKDOWN_SHORT | 363 | 7/356/0 | 53% | +0.15 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.08R) |
| LIQUIDATION_REVERSAL | 70 | 0/70/0 | 60% | -0.51 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) |
| POST_DISPLACEMENT_CONTINUATION | 69 | 0/69/0 | 90% | +0.76 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 18 | 1/17/0 | 28% | -0.46 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.87R (n=27, STRONG); `VOLUME_SURGE_BREAKOUT @ NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP` +2.68R (n=30, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP` -1.61R (n=20, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 97 | 35% / -0.41R | 97 | 55% / -0.10R | +0.31 | **ATR** |
| TREND_PULLBACK_EMA | 146 | 42% / -0.32R | 146 | 46% / -0.13R | +0.19 | **ATR** |
| MOVER_AVWAP_SCALP | 456 | 38% / -0.23R | 456 | 41% / -0.12R | +0.11 | **ATR** |
| SR_FLIP_RETEST | 2764 | 46% / -0.20R | 2764 | 49% / -0.10R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 819 | 47% / -0.12R | 819 | 53% / -0.06R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 673 | 50% / -0.18R | 673 | 54% / -0.12R | +0.06 | **ATR** |
| MOVER_TREND_PULLBACK | 3652 | 51% / -0.06R | 3652 | 54% / -0.01R | +0.05 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 74 | 41% / +0.00R | 74 | 49% / -0.04R | -0.05 | **FIXED** |
| RANGE_FADE | 218 | 17% / -0.72R | 218 | 18% / -0.68R | +0.04 | **ATR** |
| MEAN_REVERT | 394 | 54% / +0.01R | 394 | 50% / +0.05R | +0.04 | **ATR** |
| WHALE_MOMENTUM | 100 | 48% / -0.25R | 100 | 47% / -0.29R | -0.04 | **FIXED** |
| BREAKDOWN_SHORT | 18 | 28% / -0.29R | 18 | 28% / -0.27R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1372 | 45% / -0.13R | 1372 | 45% / -0.15R | -0.02 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 2260 | 47% / -0.10R | 2260 | 47% / -0.10R | -0.00 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 9 | 33% / -0.27R | 9 | 33% / -0.27R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 71% / +0.23R | 7 | 71% / +0.04R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 6 | 33% / -0.86R | 6 | 33% / -0.51R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 4978 | 30% | -0.14R | 273 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 446 | 40% | -0.13R | 120 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 28 | 57% | +0.06R | 18 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1219 | 28% / -1.70R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 15 | 27% / -0.53R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 3874 | 38% / -0.23R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 955 | 33% / -0.58R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 74 | 23% / -0.89R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 628 | 30% / -1.74R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 857 | 34% / -0.16R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 308 | 42% / -1.18R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 112 | 30% / -1.21R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 157 | 26% / -0.82R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 443 | 30% / -0.27R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 10 | 20% / -0.43R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 129 | 39% / -0.26R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 54 | 39% / -0.19R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 5 | 20% / -0.91R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 6 | 17% / -1.54R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 27 | 44% / -0.36R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 42 · alerting: **4** · boot grace active: False
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 6/6) (sustained 6 cycles)
- **ALERT** `edge_reconciliation` — MOVER_AVWAP_SCALP realized−counterfactual=+0.53R (bound 0.3) (streak 6/6) (sustained 6 cycles)
- **ALERT** `mean_revert_emission` — 960 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.47R over n=4004, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 6/6) (sustained 6 cycles)
- **ALERT** `tuned_variants` — 39 non-stamps — atr_arm_uncomputable=39 (seen=357 stamped=25 skipped=293) (streak 6/6) (sustained 6 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 1503619 accepted, 0 rejected | 0 |
| auto_dispatch | ok | attempts=0 fanouts=1 (gaps: skip 1, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 64820.10 | 0 |
| candle_coverage | ok | 92/93 symbols with ≥20 15m candles, 89/93 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 395 dup bars, 0 undedupable; ws 0 out-of-order, 81 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 6/6) | 6 |
| context_emission_policy | ok | output +17 / upstream +33 | 0 |
| dark_resolution | violating | 1 of 52 open dark rows are not being advanced (worst: EULUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 6/120) | 6 |
| dark_sar_arms | ok | no open dark arms | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 295235 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.53R (bound 0.3) (streak 6/6) | 6 |
| emission_controller | ok | last cycle 1663s ago; live_overrides=26 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=14 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4072 stamps (MEAN_REVERT=1169, MOVER_AVWAP_SCALP=210, MOVER_TREND_PULLBACK=2213, RANGE_FADE=444, TREND_PULLBACK_EMA=36), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 5/6) | 5 |
| footprint_bars | ok | 2640 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +2 / upstream +206 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 960 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.47R over n=4004, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 6/6) | 6 |
| mean_revert_path | ok | output +84 / upstream +206 | 0 |
| mover_admission_metadata | ok | 854 symbols known, 153 marked TRADIFI_PERPETUAL | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 311068 evicted (sampled: execution:trigger_not_confirmed 400/110816, execution:overextended 400/108578, setup_compat:regime_STRONG_TREND 400/38854) | 0 |
| price_action_lane | ok | 36298 evaluated, 30 emitted; layer1 30 stamped / 0 blind; cooldown=4252, delta_opposed=2928, no_footprint=11112, no_opposing_target=317, no_sweep=15168, rr_below_floor=2491 | 0 |
| promoted_pair_integrity | ok | 14/14 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.52R over n=3475 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +37 / upstream +206 | 0 |
| sar_alignment_crosscheck | ok | 34/957 disagreed (3.6%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +206 | 0 |
| sar_ledger_candles | ok | 20/105 unfetchable (19%); top cause: gap or duplicate bar in the 15m window; symbols: 1000SHIBUSDT, DEXEUSDT, GIGGLEUSDT, ICPUSDT, XMRUSDT | 0 |
| sar_live_arms | ok | 4 arms current, none stalled; covering 188/188 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 7 resolved, 78 still mid-window | 0 |
| setup_tf_resolver | ok | 13569 resolutions, 5764 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +154 / upstream +206 | 0 |
| structural_snap | ok | 1318/1318 measured, 4 blind, 0 levels moved (refusals: redetect_cooldown=138) | 0 |
| structural_veto_lane | ok | 163 stamped; 0 with no readable level book, 12 with clear air ahead, 126 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +206 / upstream +33 | 0 |
| tuned_variants | violating | 39 non-stamps — atr_arm_uncomputable=39 (seen=357 stamped=25 skipped=293) (streak 6/6) | 6 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3553139`
- `Path funnel` emissions: `96`
- `Regime distribution` emissions: `96`
- `QUIET_SCALP_BLOCK` events: `290`
- `confidence_gate` events: `9378`
- `free_channel_post` events: `30`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **3**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 3837 | 3837 | 3837 | 0 |
| futures_depth | 2 | 3301 | 3301 | 3679 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **30**

| Source | Count |
|---|---:|
| signal_close | 25 |
| regime_shift | 4 |
| signal_highlight | 1 |

- By severity: HIGH=30

## Dependency readiness
- cvd: presence[present=617345] state[populated=617345] buckets[few=11, many=617124, some=210] sources[none] quality[none]
- funding_rate: presence[absent=36473, present=580872] state[empty=36473, populated=580872] buckets[few=580872, none=36473] sources[none] quality[none]
- liquidation_clusters: presence[absent=356778, present=260567] state[empty=356778, populated=260567] buckets[few=202978, none=356778, some=57589] sources[none] quality[none]
- oi_snapshot: presence[absent=35889, present=581456] state[empty=35889, populated=581456] buckets[few=189, many=579825, none=35889, some=1442] sources[none] quality[none]
- order_book: presence[absent=175371, present=441974] state[populated=441974, unavailable=175371] buckets[few=441974, none=175371] sources[book_ticker=441974, unavailable=175371] quality[none=175371, top_of_book_only=441974]
- orderblocks: presence[absent=617345] state[empty=617345] buckets[none=617345] sources[measured_dark=617260, not_implemented=85] quality[none]
- recent_ticks: presence[absent=3197, present=614148] state[empty=3197, populated=614148] buckets[many=614148, none=3197] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.305726051330566` sec
- Median create→first breach: `2388.814740896225` sec
- Median create→terminal: `2395.4033529758453` sec
- Median first breach→terminal: `5.769592046737671` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 4.0}, "under_180s": {"count": 1, "pct": 4.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 4.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MOVER_AVWAP_SCALP | 1 | 1 | 1.8001372574463788 | 2.7954912224108615 | 0.6439430905792368 | 0 | 1 |
| MOVER_TREND_PULLBACK | 24 | 24 | 3.7253288646201117 | 3.0 | 1.241776288206704 | 23 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 3.6716 | 8671.238656044006 | 8816.964794158936 |
| MOVER_TREND_PULLBACK | 24 | 24 | 0.0 | 16.7 | 0.0 | 0.0 | 1.1005 | 2330.103679895401 | 2334.2310374975204 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 498 | 2 | 447 | 0.0 | 0.0 | None | None | 51 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3097 | 18 | 2848 | 0.0 | 0.0 | None | None | 249 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `54`
- Gating Δ: `-20957`
- No-generation Δ: `-342126`
- Fast failures Δ: `-1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.4174, "current_avg_pnl": 1.1005, "current_win_rate": 0.0, "previous_avg_pnl": 1.5179, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": -3, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": 83, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
