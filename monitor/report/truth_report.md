# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `15` sec (warning=False)
- Latest performance record age: `2874` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 31 | 31 | 28 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 2087 | 2087 | 1862 | 8 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 12892 | 12908 | 6 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 13384 | 13387 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 13224 | 12594 | 780 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 13404 | 13258 | 157 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 13970 | 13943 | 38 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 10104 | 10117 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 13416 | 13422 | 1 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 13427 | 12679 | 980 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 15288 | 17290 | 125 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 12916 | 10592 | 4660 | 0 | 0 | 0 | low-sample (no_reclaim) |
| EVAL::OPENING_RANGE_BREAKOUT | 13876 | 13887 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 13388 | 13399 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 13215 | 13216 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 13665 | 13412 | 392 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 13125 | 13191 | 13 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 9344 | 8904 | 533 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 9441 | 9380 | 94 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 12858 | 12886 | 2 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 10117 | 10114 | 20 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 382 | 382 | 328 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 95 | 95 | 12 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 2183 | 2183 | 2160 | 3 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 1789 | 1789 | 1726 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 250 | 250 | 60 | 14 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 10157 | 10157 | 5169 | 254 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 31 | 31 | 23 | 2 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 838 | 838 | 809 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 54 | 54 | 54 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 288 | 288 | 228 | 8 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 16 | 16 | 0 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 545 | 545 | 8 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=12908): breakout_not_found=9163, basic_filters_failed=2139, move_not_fresh=875, breakout_stale=425, retest_proximity_failed=190, insufficient_candles=90, volume_spike_missing=26
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=13387): cls_disabled_merged_into_lsr=13387
- **EVAL::DIVERGENCE_CONTINUATION** (total=12594): cvd_divergence_failed=7377, h1_trend_not_aligned=2096, basic_filters_failed=1776, ema_alignment_reject=893, retest_proximity_failed=324, missing_fvg_or_orderblock=128
- **EVAL::FAILED_AUCTION_RECLAIM** (total=13258): auction_not_detected=9737, basic_filters_failed=1721, reclaim_hold_failed=879, tail_too_small=447, regime_blocked=420, rsi_reject=54
- **EVAL::FUNDING_EXTREME** (total=13943): funding_not_extreme=11272, basic_filters_failed=1901, ema_alignment_reject=325, missing_funding_rate=208, rsi_reject=142, momentum_reject=47, cvd_divergence_failed=38, insufficient_candles=6, missing_fvg_or_orderblock=4
- **EVAL::LIQUIDATION_REVERSAL** (total=10117): cascade_threshold_not_met=8027, basic_filters_failed=1846, cvd_divergence_failed=98, rsi_reject=69, insufficient_candles=68, missing_fvg_or_orderblock=9
- **EVAL::MA_CROSS_TREND_SHIFT** (total=13422): no_ma_cross=11377, basic_filters_failed=1780, ma_cross_htf_misaligned=239, ma_cross_cooldown=26
- **EVAL::MEAN_REVERT** (total=12679): no_extension=11499, basic_filters_failed=1180
- **EVAL::MOVER_AVWAP_SCALP** (total=17290): no_avwap_tag=10334, no_mover_leg=2640, basic_filters_failed=2220, avwap_slope_against=1216, avwap_reclaim_no_volume=538, no_avwap_reclaim=252, insufficient_candles=90
- **EVAL::MOVER_TREND_PULLBACK** (total=10592): no_reclaim=4247, mover_run_too_small=3062, basic_filters_failed=2186, no_pullback_tag=1007, insufficient_candles=90
- **EVAL::OPENING_RANGE_BREAKOUT** (total=13887): feature_disabled=13887
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=13399): regime_blocked=6898, breakout_not_found=5088, basic_filters_failed=782, adx_reject=594, ema_alignment_reject=37
- **EVAL::QUIET_COMPRESSION_BREAK** (total=13216): regime_blocked=6838, compression_not_detected=5206, basic_filters_failed=936, breakout_not_detected=209, volume_confirmation_failed=22, rsi_reject=5
- **EVAL::RANGE_FADE** (total=13412): no_range_edge=12229, basic_filters_failed=1183
- **EVAL::SR_FLIP_RETEST** (total=13191): flip_close_not_confirmed=9696, basic_filters_failed=1715, long_break_volume_thin=459, retest_out_of_zone=451, regime_blocked=415, h1_break_not_confirmed=215, reclaim_hold_failed=129, long_acceptance_not_held=54, ema_alignment_reject=38, whipsaw_flip=10, wick_quality_failed=8, missing_fvg_or_orderblock=1
- **EVAL::STANDARD** (total=8904): momentum_reject=3339, adx_reject=1822, sweeps_not_detected=1255, basic_filters_failed=882, ema_alignment_reject=810, macd_reject=665, htf_poi_unanchored=97, rsi_reject=19, mtf_reject=9, invalid_sl_geometry=6
- **EVAL::TREND_PULLBACK** (total=9380): h1_pullback_not_confirmed=2030, h1_trend_not_aligned=2002, ema_alignment_reject=1600, ema_not_tested_prev=1057, basic_filters_failed=967, no_ema_reclaim_close=677, body_conviction_fail=382, rsi_reject=363, prev_already_above_emas=151, no_prev_high_break=67, prev_already_below_emas=39, momentum_flat=18, no_prev_low_break=15, ema21_not_tagged=7, missing_fvg_or_orderblock=4, momentum_reject=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=12886): breakout_not_found=7843, basic_filters_failed=2138, move_not_fresh=2011, breakout_stale=524, retest_proximity_failed=202, insufficient_candles=90, volume_spike_missing=74, move_exhausted=2, missing_fvg_or_orderblock=2
- **EVAL::WHALE_MOMENTUM** (total=10114): momentum_reject=7067, recent_ticks_insufficient=2491, basic_filters_failed=556

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=60): setup_compat:regime_VOLATILE_UNSUITABLE=59, setup_compat:regime_BREAKOUT_EXPANSION=1
- **FAILED_AUCTION_RECLAIM** (total=173): setup_compat:regime_STRONG_TREND=93, execution:overextended=80
- **FUNDING_EXTREME_SIGNAL** (total=73): execution:trigger_not_confirmed=73
- **LIQUIDATION_REVERSAL** (total=2): execution:trigger_not_confirmed=2
- **LIQUIDITY_SWEEP_REVERSAL** (total=750): setup_compat:regime_STRONG_TREND=338, execution:overextended=219, execution:trigger_not_confirmed=193
- **MEAN_REVERT** (total=1648): setup_compat:regime_STRONG_TREND=1139, execution:overextended=327, setup_compat:regime_WEAK_TREND=182
- **MOVER_AVWAP_SCALP** (total=204): execution:overextended=150, execution:trigger_not_confirmed=46, entry_quality=8
- **MOVER_TREND_PULLBACK** (total=4737): execution:overextended=2043, execution:trigger_not_confirmed=1989, entry_quality=705
- **RANGE_FADE** (total=681): setup_compat:regime_STRONG_TREND=425, setup_compat:regime_WEAK_TREND=157, execution:overextended=69, setup_compat:regime_VOLATILE_UNSUITABLE=23, context_edge=4, setup_compat:regime_BREAKOUT_EXPANSION=3
- **TREND_PULLBACK_EMA** (total=213): setup_compat:regime_CLEAN_RANGE=134, setup_compat:regime_DIRTY_RANGE=62, entry_quality=11, setup_compat:regime_VOLATILE_UNSUITABLE=6
- **VOLUME_SURGE_BREAKOUT** (total=6): execution:overextended=6
- **WHALE_MOMENTUM** (total=440): execution:trigger_not_confirmed=440

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 22790 | 38.0% |
| TRENDING_UP | 18499 | 30.8% |
| TRENDING_DOWN | 10708 | 17.8% |
| QUIET | 5522 | 9.2% |
| VOLATILE | 2478 | 4.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **129**
- Average confidence gap to threshold: **7.02** (samples=129) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XLMUSDT=21, BTCUSDT=18, 1000SHIBUSDT=15, TAOUSDT=12, BCHUSDT=12, XRPUSDT=11, ETHUSDT=9, 1000PEPEUSDT=8, SOLUSDT=6, LTCUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 3 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 50 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 40 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 30 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 7 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 10 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 6 |
| MEAN_REVERT | filtered | min_confidence | 8 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 33 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 11 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 69 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 213 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 122 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2744 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 4 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 4 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 4 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 51 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 10 |
| WHALE_MOMENTUM | filtered | min_confidence | 39 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 3 | 74.03 | 65.00 | -9.03 | 21.00 | 18.53 | 20.00 | 4.00 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 50 | 56.20 | 64.84 | 8.64 | 20.80 | 19.71 | 18.47 | 0.44 | 14.22 |
| DIVERGENCE_CONTINUATION | kept | 40 | 70.79 | 65.00 | -5.79 | 21.30 | 19.72 | 17.65 | 0.17 | 0.90 |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 55.03 | 64.07 | 9.04 | 20.34 | 19.50 | 20.00 | 2.32 | 3.83 |
| FAILED_AUCTION_RECLAIM | kept | 7 | 73.17 | 65.00 | -8.17 | 20.51 | 19.33 | 20.00 | 3.86 | 0.71 |
| FUNDING_EXTREME_SIGNAL | filtered | 10 | 44.53 | 61.00 | 16.47 | 20.51 | 15.80 | 16.13 | 2.10 | 7.40 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 2 | 59.30 | 61.00 | 1.70 | 20.60 | 20.00 | 20.00 | 2.00 | 8.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 6 | 64.72 | 65.00 | 0.28 | 21.00 | 18.80 | 18.00 | 2.67 | 6.67 |
| MEAN_REVERT | filtered | 8 | 50.70 | 61.00 | 10.30 | 20.68 | 14.00 | 16.90 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 44 | 59.63 | 51.25 | -8.38 | 20.78 | 13.56 | 15.80 | 3.47 | 5.91 |
| MOVER_AVWAP_SCALP | kept | 69 | 79.21 | 65.00 | -14.21 | 20.96 | 16.06 | 15.80 | 4.29 | 0.17 |
| MOVER_TREND_PULLBACK | filtered | 335 | 57.06 | 64.81 | 7.75 | 20.64 | 19.16 | 15.80 | 4.39 | 17.44 |
| MOVER_TREND_PULLBACK | kept | 2744 | 76.94 | 65.00 | -11.94 | 20.98 | 18.98 | 15.80 | 4.55 | 2.25 |
| QUIET_COMPRESSION_BREAK | filtered | 4 | 59.70 | 65.00 | 5.30 | 18.70 | 20.00 | 20.00 | 0.00 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 4 | 79.38 | 65.00 | -14.38 | 22.12 | 19.55 | 20.00 | 0.00 | -2.25 |
| TREND_PULLBACK_EMA | filtered | 7 | 59.90 | 65.00 | 5.10 | 21.03 | 19.70 | 17.74 | 4.29 | 15.89 |
| TREND_PULLBACK_EMA | kept | 51 | 77.35 | 65.00 | -12.35 | 20.98 | 19.76 | 17.85 | 4.79 | 2.83 |
| VOLUME_SURGE_BREAKOUT | kept | 10 | 68.60 | 65.00 | -3.60 | 20.30 | 17.87 | 20.00 | 4.60 | 1.50 |
| WHALE_MOMENTUM | filtered | 39 | 58.53 | 63.87 | 5.34 | 23.81 | 16.31 | 17.00 | 0.00 | 9.08 |
| WHALE_MOMENTUM | kept | 2 | 63.40 | 65.00 | 1.60 | 22.80 | 19.80 | 17.00 | 0.00 | 8.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 3 | 74.03 | 22.33 | 14.00 | 13.00 | 14.00 | 5.00 | 4.70 | 4.00 |
| DIVERGENCE_CONTINUATION | filtered | 50 | 56.20 | 22.92 | 14.00 | 6.90 | 11.86 | 5.72 | 8.58 | 0.44 |
| DIVERGENCE_CONTINUATION | kept | 40 | 70.79 | 22.00 | 17.00 | 4.05 | 13.32 | 6.24 | 9.43 | 0.17 |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 55.03 | 22.00 | 15.33 | 10.30 | 14.40 | 5.55 | 3.96 | 2.32 |
| FAILED_AUCTION_RECLAIM | kept | 7 | 73.17 | 19.29 | 18.00 | 3.86 | 14.00 | 8.93 | 6.39 | 3.86 |
| FUNDING_EXTREME_SIGNAL | filtered | 10 | 44.53 | 25.00 | 10.00 | 6.90 | 11.40 | 8.30 | 3.23 | 2.10 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 2 | 59.30 | 17.00 | 14.00 | 6.00 | 14.00 | 5.00 | 9.30 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 6 | 64.72 | 23.00 | 14.00 | 6.00 | 13.17 | 5.00 | 7.55 | 2.67 |
| MEAN_REVERT | filtered | 8 | 50.70 | 25.00 | 18.00 | 3.00 | 12.00 | 5.00 | 2.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 44 | 59.63 | 19.05 | 18.09 | 8.39 | 13.09 | 6.03 | 4.59 | 3.47 |
| MOVER_AVWAP_SCALP | kept | 69 | 79.21 | 20.45 | 18.03 | 9.72 | 12.88 | 5.54 | 9.12 | 4.29 |
| MOVER_TREND_PULLBACK | filtered | 335 | 57.06 | 18.09 | 18.00 | 8.24 | 13.37 | 5.70 | 8.95 | 4.39 |
| MOVER_TREND_PULLBACK | kept | 2744 | 76.94 | 19.27 | 18.00 | 8.44 | 13.36 | 6.14 | 9.52 | 4.55 |
| QUIET_COMPRESSION_BREAK | filtered | 4 | 59.70 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 5.70 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 4 | 79.38 | 19.00 | 17.00 | 12.75 | 14.00 | 7.62 | 9.00 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 7 | 59.90 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 10.00 | 4.29 |
| TREND_PULLBACK_EMA | kept | 51 | 77.35 | 20.29 | 18.00 | 7.50 | 14.29 | 6.19 | 9.25 | 4.79 |
| VOLUME_SURGE_BREAKOUT | kept | 10 | 68.60 | 5.80 | 17.60 | 12.00 | 15.20 | 5.00 | 9.90 | 4.60 |
| WHALE_MOMENTUM | filtered | 39 | 58.53 | 24.90 | 18.00 | 5.00 | 11.95 | 7.18 | 0.58 | 0.00 |
| WHALE_MOMENTUM | kept | 2 | 63.40 | 25.00 | 18.00 | 9.00 | 12.50 | 6.75 | 0.65 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 3 | 74.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 50 | 56.20 | 0.00 | 0.00 | 1.44 | 0.00 | 2.16 | 0.00 | 0.00 | 0.00 | **3.60** |
| DIVERGENCE_CONTINUATION | kept | 40 | 70.79 | 0.00 | 0.00 | 2.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.52** |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 55.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | **0.20** |
| FAILED_AUCTION_RECLAIM | kept | 7 | 73.17 | 0.00 | 0.00 | 1.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.14** |
| FUNDING_EXTREME_SIGNAL | filtered | 10 | 44.53 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.40** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 2 | 59.30 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 6 | 64.72 | 0.00 | 0.00 | 6.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.67** |
| MEAN_REVERT | filtered | 8 | 50.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 44 | 59.63 | 0.00 | 0.00 | 0.73 | 0.00 | 0.00 | 0.00 | 0.00 | 1.09 | **1.82** |
| MOVER_AVWAP_SCALP | kept | 69 | 79.21 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.17** |
| MOVER_TREND_PULLBACK | filtered | 335 | 57.06 | 0.00 | 0.00 | 6.55 | 0.00 | 3.94 | 0.13 | 0.00 | 0.00 | **10.62** |
| MOVER_TREND_PULLBACK | kept | 2744 | 76.94 | 0.00 | 0.00 | 2.15 | 0.00 | 0.17 | 0.01 | 0.00 | 0.00 | **2.33** |
| QUIET_COMPRESSION_BREAK | filtered | 4 | 59.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 4 | 79.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 7 | 59.90 | 0.00 | 0.00 | 6.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.17** |
| TREND_PULLBACK_EMA | kept | 51 | 77.35 | 0.00 | 0.00 | 2.79 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.79** |
| VOLUME_SURGE_BREAKOUT | kept | 10 | 68.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 39 | 58.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | kept | 2 | 63.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **3679 held of 4704 seen** across 15 strategies; 78 cells past the sample floor; **23 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 2727 | 4/2723/0 | 55% | -0.02 | NY/QUIET/NORMAL/BTC_RISING/MIDCAP (+1.00R) | ASIA/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.07R) |
| SHADOW_MEAN_REVERT | 229 | 0/0/229 | 21% | -0.66 | NY/MARKUP/CASCADE/BTC_RISING (-0.51R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.96R) |
| SHADOW_RANGE_FADE | 122 | 0/0/122 | 27% | -0.50 | NY/MARKUP/CASCADE/BTC_RISING (-0.63R) | NY/MARKUP/CASCADE/BTC_RISING (-0.63R) |
| DIVERGENCE_CONTINUATION | 120 | 0/120/0 | 68% | +0.18 | OFF_HOURS/MARKUP/CASCADE/BTC_RISING (-0.27R) | OFF_HOURS/MARKUP/CASCADE/BTC_RISING (-0.27R) |
| FAILED_AUCTION_RECLAIM | 114 | 0/114/0 | 12% | -0.83 | NY/MARKUP/COMPRESSED/BTC_RISING (-1.13R) | NY/MARKUP/COMPRESSED/BTC_RISING (-1.13R) |
| SHADOW_FUNDING_FADE | 84 | 0/0/84 | 67% | +0.14 | — | — |
| WHALE_MOMENTUM | 82 | 0/82/0 | 15% | -0.39 | OFF_HOURS/MARKUP/EXPANDED/BTC_RISING (-0.22R) | NY/MARKUP/EXPANDED/BTC_RISING (-0.57R) |
| TREND_PULLBACK_EMA | 76 | 0/76/0 | 24% | -0.50 | NY/DISTRIBUTION/EXPANDED/BTC_RISING (-0.71R) | NY/DISTRIBUTION/EXPANDED/BTC_RISING (-0.71R) |
| MOVER_AVWAP_SCALP | 68 | 0/68/0 | 47% | -0.11 | — | — |
| FUNDING_EXTREME_SIGNAL | 20 | 0/20/0 | 30% | -0.47 | — | — |
| SHADOW_CASCADE_REVERSAL | 13 | 0/0/13 | 38% | -0.34 | — | — |
| QUIET_COMPRESSION_BREAK | 12 | 0/12/0 | 100% | +0.02 | — | — |
| LIQUIDITY_SWEEP_REVERSAL | 6 | 0/6/0 | 67% | -0.06 | — | — |
| VOLUME_SURGE_BREAKOUT | 4 | 0/4/0 | 50% | -0.38 | — | — |
| BREAKDOWN_SHORT | 2 | 0/2/0 | 100% | +0.24 | — | — |

- **Strongest cells**: `MOVER_TREND_PULLBACK @ NY/QUIET/NORMAL/BTC_RISING/MIDCAP` +1.00R (n=50, STRONG); `MOVER_TREND_PULLBACK @ NY/QUIET/NORMAL/BTC_RISING` +0.97R (n=50, STRONG); `MOVER_TREND_PULLBACK @ NY/QUIET/NORMAL/BTC_RISING/MAJOR` +0.95R (n=50, STRONG)
- **Weakest cells**: `FAILED_AUCTION_RECLAIM @ NY/MARKUP/COMPRESSED/BTC_RISING/ALTCOIN` -1.13R (n=20, NEGATIVE); `FAILED_AUCTION_RECLAIM @ NY/MARKUP/COMPRESSED/BTC_RISING` -1.13R (n=20, NEGATIVE); `MOVER_TREND_PULLBACK @ ASIA/MARKUP/EXPANDED/BTC_RISING/ALTCOIN` -1.07R (n=23, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| DIVERGENCE_CONTINUATION | 16 | 62% / +0.13R | 16 | 62% / +0.10R | -0.03 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 18 | 11% / -0.70R | 18 | 11% / -0.67R | +0.03 | **ATR** |
| MOVER_TREND_PULLBACK | 294 | 61% / +0.07R | 294 | 64% / +0.07R | +0.00 | **ATR** |
| TREND_PULLBACK_EMA | 8 | 62% / -0.13R | 8 | 62% / -0.04R | — | **MEASURING** |
| WHALE_MOMENTUM | 9 | 22% / -0.46R | 9 | 22% / -0.43R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 50% / -0.27R | 2 | 50% / -0.33R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 6 | 50% / +0.21R | 6 | 50% / +0.01R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 4 | 25% / -0.53R | 4 | 75% / +0.17R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 3 | 100% / +0.11R | 3 | 100% / +0.10R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 1 | 0% / -1.05R | 1 | 0% / -1.04R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 456 | 29% | -0.16R | 40 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 6 | 50% | +0.04R | 4 | MEASURING |
| VOLUME_SURGE_BREAKOUT | @TUNED | 1 | 0% | -1.04R | 1 | MEASURING |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 6 | 50% / +2.67R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 23 | 91% / +4.33R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 273 | 46% / -0.02R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 20 | 70% / +1.50R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 13 | 38% / -0.22R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 17 | 71% / +2.87R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 12 | 67% / +0.98R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 2 | 50% / -0.27R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 2 | 0% / -0.71R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 3 | 33% / -0.17R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 1 | 100% / +1.44R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 1 | 0% / -0.83R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 1 | 0% / -1.07R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 50 · alerting: **4** · boot grace active: False
- **ALERT** `scan_cycle` — last 29.14s, worst 197.82s over 747 cycles; 113 over 60s, 17 over the 120s healthcheck deadline (plus 2/0 during boot warm-up, not counted); 8 executor workers — a cycle past the deadline leaves the scanner heartbeat stale, and three consecutive failed healthchecks restart this container (streak 78/2) (sustained 78 cycles)
- **ALERT** `cohort_edge_gate` — all 28 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 28 cohorts, 11 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 78/6) (sustained 78 cycles)
- **ALERT** `mean_revert_emission` — 1783 detections since last emission (emitted_total=0) — and only 0 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 65/6) (sustained 65 cycles)
- **ALERT** `tuned_variants` — 29 non-stamps — atr_arm_uncomputable=29 (seen=2295 stamped=510 skipped=1756) (streak 17/6) (sustained 17 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 41 fed / 0 quiet / 0 never delivered of 41 subscribed; 12988205 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 6 arms current, none stalled; covering 157/157 signals (100%) | 0 |
| auto_dispatch | ok | attempts=4 fanouts=4 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 69691.40 | 0 |
| candle_coverage | ok | 90/102 symbols with ≥20 15m candles, 90/102 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 751 dup bars, 0 undedupable; ws 0 out-of-order, 309 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 28 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 28 cohorts, 11 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 78/6) | 78 |
| context_emission_policy | ok | output +113 / upstream +12 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1129/1142 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 7 of 106 open dark rows are not being advanced (worst: ALPINEUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 26/120) | 26 |
| dark_sar_arms | ok | no open arms; covering 1127/1140 signals (99%) | 0 |
| depth_feed | ok | 41/41 books fresh (stale 0, never 0, thin 0); 2925473 msgs, 0 rejected | 0 |
| edge_reconciliation | ok | no strategy past reconciliation sample floor yet | 0 |
| emission_controller | ok | last cycle 361s ago; live_overrides=26 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=14 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4236 stamps (MEAN_REVERT=66, MOVER_AVWAP_SCALP=124, MOVER_TREND_PULLBACK=3712, RANGE_FADE=171, TREND_PULLBACK_EMA=163), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | 3644 evaluated, 847 suppressed, 1472 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m | 0 |
| footprint_bars | ok | 4920 sealed bars over 41 symbols; 1566 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | counter reset | 0 |
| geometry_ab | ok | output +34 / upstream +224 | 0 |
| indicator_cache_key | ok | 5056 frozen value(s) avoided; 640 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 1783 detections since last emission (emitted_total=0) — and only 0 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 65/6) | 65 |
| mean_revert_path | violating | upstream +224 but output +0 (streak 5/72) | 5 |
| mover_admission_metadata | ok | 872 symbols known, 170 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 20 held, 20 with scan counts, 19 with an activity reading (measuring only) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2958 rows held, 584794 evicted (sampled: execution:overextended 400/214697, execution:trigger_not_confirmed 400/201586, setup_compat:regime_STRONG_TREND 400/72397) | 0 |
| price_action_lane | ok | 64440 evaluated, 215 emitted; layer1 215 stamped / 0 blind; cooldown=8180, delta_opposed=6653, no_footprint=27982, no_levels=59, no_opposing_target=62, no_sweep=15402, rr_below_floor=5887 | 0 |
| promoted_pair_integrity | ok | 20/20 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 72 detections since last emission (emitted_total=0) — and only 0 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 1/6) | 1 |
| range_fade_path | ok | output +18 / upstream +224 | 0 |
| sar_alignment_crosscheck | ok | 342/7780 disagreed (4.4%) | 0 |
| sar_exit_shadow | ok | output +8 / upstream +224 | 0 |
| sar_hold_arm | ok | 270 held arms settled, 57 unscored, 5 still walking (2 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 27/125 unfetchable (22%); top cause: gap or duplicate bar in the 15m window; symbols: 1000PEPEUSDT, FARTCOINUSDT, FETUSDT, LITUSDT, METUSDT +3 more | 0 |
| sar_live_arms | ok | 5 arms current, none stalled; covering 166/166 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 5 resolved, 93 still mid-window | 0 |
| scan_cycle | violating | last 29.14s, worst 197.82s over 747 cycles; 113 over 60s, 17 over the 120s healthcheck deadline (plus 2/0 during boot warm-up, not counted); 8 executor workers — a cycle past the deadline leaves the scanner heartbeat stale, and three consecutive failed healthchecks restart this container (streak 78/2) | 78 |
| setup_tf_resolver | ok | 46552 resolutions, 35112 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 70s ago (8.47s to run, worst 136.12s), 512 overrun(s) of 1400 cycles, TTL 900s; slowest data_intake=18.66s, trail_governor=11.08s, signals=10.55s | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | counter reset | 0 |
| strategy_edge | ok | output +113 / upstream +224 | 0 |
| structural_snap | ok | 4213/4213 measured, 29 blind, 0 levels moved (refusals: redetect_cooldown=787) | 0 |
| structural_veto_lane | ok | 1159 stamped; 0 with no readable level book, 2 with clear air ahead, 690 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +224 / upstream +12 | 0 |
| tuned_variants | violating | 29 non-stamps — atr_arm_uncomputable=29 (seen=2295 stamped=510 skipped=1756) (streak 17/6) | 17 |

Fail-open exception counters (nonzero sites):
- `feature_liveness.probe.footprint_bars`: 1 — last: RuntimeError: deque mutated during iteration

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `43401`
- `Path funnel` emissions: `7`
- `Regime distribution` emissions: `7`
- `QUIET_SCALP_BLOCK` events: `129`
- `confidence_gate` events: `3465`
- `free_channel_post` events: `2`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **9**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 34485 | 34485 | 34485 | 0 |
| futures_aggtrade | 6 | 6367 | 11340 | 11909 | 0 |
| futures_depth | 1 | 21053 | 21053 | 21053 | 0 |
| futures_mover | 1 | 9796 | 9796 | 9796 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **2**

| Source | Count |
|---|---:|
| signal_close | 2 |

- By severity: HIGH=2

## Dependency readiness
- cvd: presence[present=50200] state[populated=50200] buckets[few=7, many=50154, some=39] sources[none] quality[none]
- funding_rate: presence[absent=8404, present=41796] state[empty=8404, populated=41796] buckets[few=41796, none=8404] sources[none] quality[none]
- liquidation_clusters: presence[absent=27113, present=23087] state[empty=27113, populated=23087] buckets[few=17864, none=27113, some=5223] sources[none] quality[none]
- oi_snapshot: presence[absent=7938, present=42262] state[empty=7938, populated=42262] buckets[few=76, many=41624, none=7938, some=562] sources[none] quality[none]
- order_book: presence[absent=27019, present=23181] state[populated=23181, unavailable=27019] buckets[few=23181, none=27019] sources[book_ticker=23181, unavailable=27019] quality[none=27019, top_of_book_only=23181]
- orderblocks: presence[absent=50200] state[empty=50200] buckets[none=50200] sources[measured_dark=50155, not_implemented=45] quality[none]
- recent_ticks: presence[present=50200] state[populated=50200] buckets[many=50200] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `24.758970975875854` sec
- Median create→first breach: `272.20454716682434` sec
- Median create→terminal: `299.14145517349243` sec
- Median first breach→terminal: `26.93690800666809` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 20.0}, "under_180s": {"count": 2, "pct": 40.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 2, "pct": 40.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 5 | 5 | 4.011564486351843 | 3.0 | 1.337188162117281 | 5 | 0 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 5 | 5 | 0.0 | 80.0 | 0.0 | 0.0 | -2.8405 | 272.20454716682434 | 299.14145517349243 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 54 | 0 | 54 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 288 | 8 | 228 | 0.0 | 0.0 | None | None | 60 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `297`
- Gating Δ: `12470`
- No-generation Δ: `238579`
- Fast failures Δ: `1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.3671, "current_avg_pnl": -2.8405, "current_win_rate": 0.0, "previous_avg_pnl": -4.2076, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 8, "geometry_changed_delta": 0, "geometry_preserved_delta": 60, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
