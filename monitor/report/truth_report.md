# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: MOVER_AVWAP_SCALP, FAILED_AUCTION_RECLAIM
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `7` sec (warning=False)
- Latest performance record age: `1443` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 207 | 207 | 207 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6514 | 6514 | 6402 | 2 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 66439 | 66424 | 38 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 50366 | 50366 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 50177 | 48959 | 1399 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 50388 | 49658 | 774 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 56662 | 56595 | 83 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 48611 | 48618 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 50434 | 50457 | 3 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 50464 | 48466 | 2580 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 71536 | 74482 | 1126 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 66464 | 56894 | 14598 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 56322 | 56322 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 50373 | 50384 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 50162 | 50134 | 38 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 51054 | 49953 | 1353 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 49807 | 49995 | 150 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 42405 | 39348 | 3201 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 42553 | 42252 | 343 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 66411 | 66409 | 28 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 48619 | 48634 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3606 | 3606 | 3304 | 8 | active-healthy (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 480 | 480 | 431 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 19115 | 19115 | 19006 | 7 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 4 | 4 | 3 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7066 | 7066 | 6733 | 3 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3225 | 3225 | 2419 | 33 | active-healthy (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 49181 | 49181 | 43721 | 214 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 486 | 486 | 333 | 9 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3253 | 3253 | 3216 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 641 | 641 | 576 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2161 | 2161 | 2098 | 13 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 169 | 169 | 168 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=66424): breakout_not_found=38307, basic_filters_failed=16584, move_not_fresh=6766, breakout_stale=2881, retest_proximity_failed=1516, volume_spike_missing=367, ema_alignment_reject=1, move_exhausted=1, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=50366): cls_disabled_merged_into_lsr=50366
- **EVAL::DIVERGENCE_CONTINUATION** (total=48959): cvd_divergence_failed=23147, h1_trend_not_aligned=12546, basic_filters_failed=10142, ema_alignment_reject=1899, retest_proximity_failed=915, missing_cvd=195, missing_fvg_or_orderblock=115
- **EVAL::FAILED_AUCTION_RECLAIM** (total=49658): auction_not_detected=31628, basic_filters_failed=9340, regime_blocked=4030, reclaim_hold_failed=2505, tail_too_small=2126, rsi_reject=29
- **EVAL::FUNDING_EXTREME** (total=56595): funding_not_extreme=40996, basic_filters_failed=11521, missing_funding_rate=2761, ema_alignment_reject=789, rsi_reject=397, momentum_reject=65, cvd_divergence_failed=59, missing_fvg_or_orderblock=7
- **EVAL::LIQUIDATION_REVERSAL** (total=48618): cascade_threshold_not_met=35504, basic_filters_failed=12336, rsi_reject=331, cvd_divergence_failed=326, missing_cvd=102, missing_fvg_or_orderblock=12, volume_spike_missing=7
- **EVAL::MA_CROSS_TREND_SHIFT** (total=50457): no_ma_cross=39850, basic_filters_failed=10151, ma_cross_cooldown=323, ma_cross_htf_misaligned=133
- **EVAL::MEAN_REVERT** (total=48466): no_extension=39693, basic_filters_failed=8773
- **EVAL::MOVER_AVWAP_SCALP** (total=74482): no_avwap_tag=31088, basic_filters_failed=16717, no_mover_leg=15833, avwap_slope_against=6469, avwap_reclaim_no_volume=2427, no_avwap_reclaim=1926, anchor_too_recent=22
- **EVAL::MOVER_TREND_PULLBACK** (total=56894): mover_run_too_small=19794, no_reclaim=17578, basic_filters_failed=16202, no_pullback_tag=2542, insufficient_candles=778
- **EVAL::OPENING_RANGE_BREAKOUT** (total=56322): feature_disabled=56322
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=50384): regime_blocked=35188, breakout_not_found=12161, basic_filters_failed=1877, adx_reject=1108, ema_alignment_reject=50
- **EVAL::QUIET_COMPRESSION_BREAK** (total=50134): compression_not_detected=22011, regime_blocked=19183, basic_filters_failed=7453, breakout_not_detected=1357, volume_confirmation_failed=124, missing_fvg_or_orderblock=4, rsi_reject=2
- **EVAL::RANGE_FADE** (total=49953): no_range_edge=41173, basic_filters_failed=8780
- **EVAL::SR_FLIP_RETEST** (total=49995): flip_close_not_confirmed=31669, basic_filters_failed=9327, regime_blocked=4019, retest_out_of_zone=1642, long_break_volume_thin=1617, h1_break_not_confirmed=1054, reclaim_hold_failed=466, wick_quality_failed=65, long_acceptance_not_held=60, ema_alignment_reject=45, whipsaw_flip=27, missing_fvg_or_orderblock=4
- **EVAL::STANDARD** (total=39348): momentum_reject=9920, adx_reject=9588, basic_filters_failed=6348, sweeps_not_detected=4531, macd_reject=4076, ema_alignment_reject=4000, htf_poi_unanchored=766, invalid_sl_geometry=92, rsi_reject=27
- **EVAL::TREND_PULLBACK** (total=42252): h1_trend_not_aligned=13103, ema_alignment_reject=7392, basic_filters_failed=6240, h1_pullback_not_confirmed=4637, ema_not_tested_prev=4205, no_ema_reclaim_close=3074, body_conviction_fail=1383, rsi_reject=1293, prev_already_above_emas=480, no_prev_high_break=316, momentum_flat=59, ema21_not_tagged=23, prev_already_below_emas=17, missing_fvg_or_orderblock=13, no_prev_low_break=12, momentum_reject=5
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=66409): breakout_not_found=36071, basic_filters_failed=16582, move_not_fresh=8551, breakout_stale=3344, retest_proximity_failed=1472, volume_spike_missing=344, missing_fvg_or_orderblock=35, move_exhausted=10
- **EVAL::WHALE_MOMENTUM** (total=48634): momentum_reject=33765, recent_ticks_insufficient=10808, basic_filters_failed=4061

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=55): execution:overextended=55
- **DIVERGENCE_CONTINUATION** (total=419): setup_compat:regime_VOLATILE_UNSUITABLE=361, setup_compat:regime_BREAKOUT_EXPANSION=58
- **FAILED_AUCTION_RECLAIM** (total=1392): setup_compat:regime_STRONG_TREND=829, execution:overextended=440, context_floor=118, setup_compat:regime_VOLATILE_UNSUITABLE=5
- **FUNDING_EXTREME_SIGNAL** (total=301): execution:trigger_not_confirmed=298, context_floor=3
- **LIQUIDATION_REVERSAL** (total=3): execution:trigger_not_confirmed=3
- **LIQUIDITY_SWEEP_REVERSAL** (total=5323): execution:trigger_not_confirmed=1928, execution:overextended=1805, setup_compat:regime_STRONG_TREND=1590
- **MA_CROSS_TREND_SHIFT** (total=4): setup_compat:regime_VOLATILE_UNSUITABLE=3, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=3668): setup_compat:regime_STRONG_TREND=1799, setup_compat:regime_WEAK_TREND=1142, execution:overextended=727
- **MOVER_AVWAP_SCALP** (total=2215): execution:overextended=1755, execution:trigger_not_confirmed=359, entry_quality=101
- **MOVER_TREND_PULLBACK** (total=20131): execution:trigger_not_confirmed=11930, execution:overextended=7262, entry_quality=939
- **QUIET_COMPRESSION_BREAK** (total=10): execution:trigger_not_confirmed=10
- **RANGE_FADE** (total=1906): setup_compat:regime_STRONG_TREND=845, setup_compat:regime_WEAK_TREND=816, setup_compat:regime_VOLATILE_UNSUITABLE=231, setup_compat:regime_BREAKOUT_EXPANSION=14
- **TREND_PULLBACK_EMA** (total=1978): setup_compat:regime_CLEAN_RANGE=1140, setup_compat:regime_DIRTY_RANGE=735, setup_compat:regime_VOLATILE_UNSUITABLE=93, entry_quality=10
- **VOLUME_SURGE_BREAKOUT** (total=35): execution:overextended=35

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 180908 | 47.9% |
| TRENDING_DOWN | 63158 | 16.7% |
| TRENDING_UP | 54630 | 14.5% |
| QUIET | 52065 | 13.8% |
| VOLATILE | 27299 | 7.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **72**
- Average confidence gap to threshold: **10.55** (samples=72) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=25, XRPUSDT=10, BNBUSDT=6, SOLUSDT=6, LINKUSDT=6, ASTERUSDT=5, FUSDT=4, XPLUSDT=3, DASHUSDT=3, FARTCOINUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 33 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 20 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 10 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 8 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 8 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MEAN_REVERT | filtered | min_confidence | 7 |
| MEAN_REVERT | kept | min_confidence_pass | 3 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 89 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 237 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 683 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 5 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1621 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 75 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 54 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 9 |
| SR_FLIP_RETEST | filtered | min_confidence | 9 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 15 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 12 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 3 | 59.43 | 63.67 | 4.24 | 20.37 | 19.13 | 17.57 | 3.33 | 7.00 |
| DIVERGENCE_CONTINUATION | kept | 33 | 68.70 | 65.00 | -3.70 | 20.71 | 19.23 | 18.14 | 2.42 | 5.11 |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 50.51 | 62.07 | 11.56 | 20.76 | 19.78 | 20.00 | 2.08 | 20.25 |
| FAILED_AUCTION_RECLAIM | kept | 8 | 69.19 | 65.00 | -4.19 | 21.16 | 18.70 | 20.00 | 3.00 | 3.29 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 58.80 | 65.00 | 6.20 | 20.20 | 19.80 | 17.00 | 3.00 | 9.50 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 8 | 68.17 | 65.00 | -3.17 | 20.44 | 17.86 | 17.20 | 2.62 | 1.19 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.00 | 61.00 | 11.00 | 20.10 | 17.40 | 15.80 | 0.00 | 12.00 |
| MEAN_REVERT | filtered | 7 | 61.70 | 65.00 | 3.30 | 20.80 | 14.00 | 14.60 | 0.00 | 12.00 |
| MEAN_REVERT | kept | 3 | 69.43 | 65.00 | -4.43 | 20.53 | 17.13 | 14.93 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 89 | 59.40 | 64.12 | 4.72 | 20.24 | 15.51 | 15.80 | 4.63 | 17.33 |
| MOVER_AVWAP_SCALP | kept | 237 | 77.96 | 65.00 | -12.96 | 20.63 | 15.49 | 15.80 | 4.26 | 4.97 |
| MOVER_TREND_PULLBACK | filtered | 688 | 56.37 | 63.89 | 7.52 | 20.02 | 18.16 | 15.80 | 3.99 | 18.67 |
| MOVER_TREND_PULLBACK | kept | 1621 | 76.94 | 65.00 | -11.94 | 20.90 | 18.45 | 15.80 | 4.48 | 1.73 |
| QUIET_COMPRESSION_BREAK | filtered | 129 | 56.16 | 64.66 | 8.50 | 21.05 | 19.12 | 20.00 | 0.00 | 15.29 |
| QUIET_COMPRESSION_BREAK | kept | 9 | 70.30 | 65.00 | -5.30 | 21.28 | 18.82 | 20.00 | 0.00 | 4.79 |
| SR_FLIP_RETEST | filtered | 9 | 57.80 | 65.00 | 7.20 | 20.00 | 20.00 | 15.20 | 2.50 | 12.00 |
| SR_FLIP_RETEST | kept | 2 | 67.85 | 65.00 | -2.85 | 20.70 | 20.00 | 15.20 | 2.50 | 5.00 |
| TREND_PULLBACK_EMA | filtered | 15 | 54.90 | 65.00 | 10.10 | 19.83 | 19.80 | 16.10 | 4.50 | 26.10 |
| TREND_PULLBACK_EMA | kept | 12 | 75.63 | 65.00 | -10.63 | 21.78 | 19.81 | 17.93 | 4.62 | 2.14 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 79.70 | 65.00 | -14.70 | 16.90 | 17.00 | 20.00 | 4.00 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 3 | 59.43 | 25.00 | 8.00 | 4.00 | 13.33 | 5.00 | 7.77 | 3.33 |
| DIVERGENCE_CONTINUATION | kept | 33 | 68.70 | 21.12 | 16.79 | 7.73 | 12.06 | 5.00 | 8.96 | 2.42 |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 50.51 | 20.73 | 16.53 | 6.50 | 15.20 | 6.20 | 4.03 | 2.08 |
| FAILED_AUCTION_RECLAIM | kept | 8 | 69.19 | 22.00 | 16.50 | 7.12 | 13.12 | 5.94 | 4.78 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 58.80 | 23.00 | 14.00 | 3.00 | 9.00 | 9.00 | 7.30 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 8 | 68.17 | 24.75 | 14.00 | 5.62 | 12.88 | 5.81 | 3.67 | 2.62 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.00 | 25.00 | 16.00 | 6.00 | 17.00 | 5.00 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 7 | 61.70 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 3 | 69.43 | 19.67 | 16.67 | 10.00 | 12.00 | 5.00 | 6.10 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 89 | 59.40 | 17.18 | 18.31 | 11.16 | 13.69 | 5.83 | 8.97 | 4.63 |
| MOVER_AVWAP_SCALP | kept | 237 | 77.96 | 20.05 | 18.01 | 12.43 | 13.42 | 7.02 | 7.76 | 4.26 |
| MOVER_TREND_PULLBACK | filtered | 688 | 56.37 | 17.09 | 18.13 | 8.30 | 13.11 | 5.72 | 9.23 | 3.99 |
| MOVER_TREND_PULLBACK | kept | 1621 | 76.94 | 19.22 | 18.07 | 8.26 | 13.36 | 6.42 | 8.90 | 4.48 |
| QUIET_COMPRESSION_BREAK | filtered | 129 | 56.16 | 19.05 | 15.67 | 11.53 | 14.07 | 7.48 | 3.64 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 9 | 70.30 | 22.33 | 16.22 | 11.33 | 14.11 | 6.00 | 5.42 | 0.00 |
| SR_FLIP_RETEST | filtered | 9 | 57.80 | 25.00 | 18.00 | 3.00 | 14.00 | 5.00 | 2.30 | 2.50 |
| SR_FLIP_RETEST | kept | 2 | 67.85 | 25.00 | 13.00 | 4.50 | 15.50 | 7.00 | 5.35 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 15 | 54.90 | 17.00 | 18.00 | 7.50 | 14.00 | 10.00 | 10.00 | 4.50 |
| TREND_PULLBACK_EMA | kept | 12 | 75.63 | 16.50 | 18.00 | 7.50 | 14.75 | 7.71 | 9.20 | 4.62 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 79.70 | 17.00 | 14.00 | 15.00 | 17.00 | 5.00 | 7.70 | 4.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 3 | 59.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 33 | 68.70 | 0.00 | 0.00 | 2.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.33** |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 50.51 | 0.00 | 0.00 | 2.88 | 0.00 | 4.32 | 0.60 | 0.00 | 0.00 | **7.80** |
| FAILED_AUCTION_RECLAIM | kept | 8 | 69.19 | 0.00 | 0.00 | 0.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.60** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 58.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 8 | 68.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MEAN_REVERT | filtered | 7 | 61.70 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MEAN_REVERT | kept | 3 | 69.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 89 | 59.40 | 0.00 | 0.00 | 1.89 | 0.00 | 2.02 | 0.00 | 0.00 | 0.00 | **3.91** |
| MOVER_AVWAP_SCALP | kept | 237 | 77.96 | 0.00 | 0.00 | 0.51 | 0.00 | 1.67 | 0.00 | 0.00 | 0.84 | **3.02** |
| MOVER_TREND_PULLBACK | filtered | 688 | 56.37 | 0.03 | 0.00 | 3.00 | 0.00 | 1.25 | 0.25 | 0.00 | 0.08 | **4.61** |
| MOVER_TREND_PULLBACK | kept | 1621 | 76.94 | 0.00 | 0.00 | 0.53 | 0.00 | 0.22 | 0.02 | 0.00 | 0.00 | **0.77** |
| QUIET_COMPRESSION_BREAK | filtered | 129 | 56.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | 7.59 | **7.79** |
| QUIET_COMPRESSION_BREAK | kept | 9 | 70.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.53 | **2.53** |
| SR_FLIP_RETEST | filtered | 9 | 57.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | **6.00** |
| SR_FLIP_RETEST | kept | 2 | 67.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 15 | 54.90 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| TREND_PULLBACK_EMA | kept | 12 | 75.63 | 0.00 | 0.00 | 1.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.73** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 79.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **104298 held of 269532 seen** across 21 strategies; 2384 cells past the sample floor; **1057 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 37066 | 559/36507/0 | 44% | -0.15 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | OVERLAP/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.16R) |
| MOVER_AVWAP_SCALP | 12923 | 176/12747/0 | 41% | -0.25 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | OVERLAP/MARKUP/EXPANDED/BTC_FALLING (-1.32R) |
| FAILED_AUCTION_RECLAIM | 8065 | 101/7964/0 | 41% | -0.19 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 6426 | 32/6394/0 | 51% | -0.00 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 5606 | 0/0/5606 | 42% | -0.11 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-0.83R) |
| TREND_PULLBACK_EMA | 5184 | 24/5160/0 | 45% | -0.15 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| SHADOW_RANGE_FADE | 4777 | 0/0/4777 | 37% | -0.10 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.66R) | LONDON/QUIET/NORMAL/BTC_RISING (-1.21R) |
| QUIET_COMPRESSION_BREAK | 4533 | 277/4256/0 | 45% | -0.15 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+0.65R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4388 | 0/0/4388 | 34% | -0.40 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.01R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3365 | 2/3363/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 3200 | 63/3137/0 | 36% | -0.38 | NY/RANGE/NORMAL/BTC_FALLING (+1.64R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 2149 | 20/2129/0 | 48% | -0.14 | LONDON/MARKDOWN/EXPANDED/BTC_RISING (+1.23R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 1803 | 2/1801/0 | 34% | -0.39 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 1602 | 0/1602/0 | 42% | +0.01 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| SR_FLIP_RETEST | 1080 | 10/1070/0 | 49% | -0.18 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.79R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 782 | 0/0/782 | 53% | -0.04 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.15R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.51R) |
| RANGE_FADE | 717 | 0/717/0 | 41% | -0.37 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 354 | 31/323/0 | 40% | -0.16 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.03R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDATION_REVERSAL | 212 | 0/212/0 | 10% | -1.02 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 60 | 6/54/0 | 43% | -0.09 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 6 | 0/6/0 | 67% | +0.42 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 142 | 28% / -0.54R | 142 | 48% / -0.18R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 418 | 45% / -0.20R | 418 | 55% / -0.04R | +0.16 | **ATR** |
| MOVER_AVWAP_SCALP | 1009 | 44% / -0.19R | 1009 | 50% / -0.08R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 367 | 44% / -0.32R | 367 | 46% / -0.22R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 124 | 49% / -0.26R | 124 | 51% / -0.17R | +0.08 | **ATR** |
| MOVER_TREND_PULLBACK | 5664 | 50% / -0.09R | 5664 | 55% / -0.01R | +0.08 | **ATR** |
| FAILED_AUCTION_RECLAIM | 726 | 43% / -0.18R | 726 | 45% / -0.10R | +0.08 | **ATR** |
| BREAKDOWN_SHORT | 31 | 32% / -0.20R | 31 | 35% / -0.13R | +0.08 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 620 | 50% / -0.20R | 620 | 55% / -0.14R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 19 | 37% / -0.21R | 19 | 37% / -0.16R | +0.05 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 95 | 39% / -0.10R | 95 | 46% / -0.07R | +0.04 | **ATR** |
| RANGE_FADE | 35 | 40% / -0.19R | 35 | 43% / -0.22R | -0.03 | **FIXED** |
| DIVERGENCE_CONTINUATION | 612 | 51% / -0.07R | 612 | 56% / -0.05R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 755 | 45% / -0.16R | 755 | 45% / -0.17R | -0.01 | **FIXED** |
| MEAN_REVERT | 148 | 52% / -0.09R | 148 | 50% / -0.09R | +0.00 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 14 | 29% / -0.51R | 14 | 57% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8217 | 29% | -0.18R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1009 | 48% | -0.08R | 191 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 61 | 51% | -0.05R | 47 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 139 | 37% / -0.30R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 728 | 36% / -0.10R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 7289 | 37% / -0.14R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1335 | 35% / -0.09R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 575 | 35% / -0.11R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 691 | 41% / +0.01R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 561 | 38% / -0.04R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 615 | 42% / -0.16R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 128 | 28% / -0.38R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 183 | 31% / -0.55R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 120 | 54% / +0.08R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 53 | 36% / -0.18R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 27 | 37% / +0.17R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 127 | 37% / -0.36R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 28 | 14% / -0.53R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 19 | 42% / -0.05R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.05R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **5** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×194]; set aside 4 undeclared (extension_pct,funding_rate,pullback_depth_atr,stack_sep_pct) (streak 29/6) (sustained 29 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=67, profile_reject=3. Held back in this window: session_quality=129, profile_reject=1. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 15/6) (sustained 15 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.69R (bound 0.3) (streak 776/6) (sustained 776 cycles)
- **ALERT** `tuned_variants` — 301 non-stamps — atr_arm_uncomputable=301 (seen=5866 stamped=860 skipped=4705) (streak 722/6) (sustained 722 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 776/3) (sustained 776 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 356685150 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 776/3) | 776 |
| ai_governor_live_arms | ok | 25 arms current, none stalled; covering 550/550 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +1 / upstream +1 | 0 |
| atr_trail_live_arms | violating | 4 live ATR-trail arms could not be advanced this cycle (0 no candles, 4 bars behind; 50 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 1/12) | 1 |
| auto_dispatch | ok | 106 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: mode:paper=161, mode:off=51. No user is on live. | 0 |
| btc_reference | ok | BTC ref 80480.00 | 0 |
| candle_coverage | ok | 85/85 symbols with ≥20 15m candles, 85/85 updated within 45m [fresh=85; 76 Tier-1 futures + 10 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1355 dup bars, 0 undedupable; ws 0 out-of-order, 402 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 9 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +2 / upstream +33 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1324/1341 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 1 of 107 open dark rows are not being advanced (worst: ACEUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 15/120) | 15 |
| dark_sar_arms | ok | no open arms; covering 1316/1333 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 61646325 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.69R (bound 0.3) (streak 776/6) | 776 |
| emission_controller | ok | last cycle 339s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×194]; set aside 4 undeclared (extension_pct,funding_rate,pullback_depth_atr,stack_sep_pct) (streak 29/6) | 29 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=67, profile_reject=3. Held back in this window: session_quality=129, profile_reject=1. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 15/6) | 15 |
| footprint_bars | ok | 5280 sealed bars over 44 symbols; 1687 incomplete, 3 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +21 but output +0 (streak 1/6) | 1 |
| indicator_cache_key | ok | 325476 frozen value(s) avoided; 1430981 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.15R over n=2129 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +0 / upstream +21 | 0 |
| mover_admission_metadata | ok | 905 symbols known, 199 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 10 held, 10 with scan counts, 9 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 6 locked / 6 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 1591541 evicted (sampled: execution:trigger_not_confirmed 400/587054, execution:overextended 400/526002, setup_compat:regime_STRONG_TREND 400/234057) | 0 |
| price_action_lane | ok | 1428028 evaluated, 1966 emitted; layer1 1966 stamped / 0 blind; cooldown=189126, delta_opposed=119075, no_footprint=599928, no_levels=249, no_opposing_target=5557, no_sweep=407292, rr_below_floor=104835 | 0 |
| promoted_pair_integrity | ok | 10/10 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.37R over n=717 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +1 / upstream +21 | 0 |
| sar_alignment_crosscheck | ok | 591/24694 disagreed (2.4%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +21 | 0 |
| sar_hold_arm | ok | 1835 held arms settled, 166 unscored, 49 still walking (38 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 1/36 unfetchable (3%); top cause: located bar does not contain the stamp; symbols: CUSDT | 0 |
| sar_live_arms | violating | 4 live SAR arms could not be advanced this cycle (0 no candles, 4 bars behind; 46 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 1/12) | 1 |
| sar_refresh_budget | ok | 13 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 436 records await one (35 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| scan_cycle | ok | last 17.83s, worst 121.5s over 16283 lifetime cycles; lifetime 147 over 60s, 2 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 35.58s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 708973 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 1s ago (0.24s to run, worst 74.02s), 1222 overrun(s) of 15136 cycles, TTL 900s; slowest signals=0.07s, data_intake=0.07s, trail_governor=0.06s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=687, gate reads=0, withheld=687) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +15 / upstream +21 | 0 |
| structural_snap | ok | 5304/5304 measured, 22 blind, 0 levels moved (refusals: redetect_cooldown=506) | 0 |
| structural_veto_lane | ok | 1228 stamped; 0 with no readable level book, 21 with clear air ahead, 899 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +21 / upstream +33 | 0 |
| tuned_variants | violating | 301 non-stamps — atr_arm_uncomputable=301 (seen=5866 stamped=860 skipped=4705) (streak 722/6) | 722 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 5 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1826799`
- `Path funnel` emissions: `43`
- `Regime distribution` emissions: `43`
- `QUIET_SCALP_BLOCK` events: `72`
- `confidence_gate` events: `2908`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **39**
- Total REST-fallback activations: **3**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 5 | 5617 | 6634 | 10036 | 0 |
| futures_aggtrade | 15 | 10276 | 23175 | 24203 | 0 |
| futures_depth | 13 | 4462 | 9315 | 9756 | 0 |
| futures_liq | 1 | 16589 | 16589 | 16589 | 0 |
| futures_mover | 5 | 7179 | 12146 | 12184 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 3 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[absent=1500, present=312834] state[empty=1500, populated=312834] buckets[many=312834, none=1500] sources[none] quality[none]
- funding_rate: presence[absent=43775, present=270559] state[empty=43775, populated=270559] buckets[few=270559, none=43775] sources[none] quality[none]
- liquidation_clusters: presence[absent=161077, present=153257] state[empty=161077, populated=153257] buckets[few=119369, none=161077, some=33888] sources[none] quality[none]
- oi_snapshot: presence[absent=43775, present=270559] state[empty=43775, populated=270559] buckets[many=270356, none=43775, some=203] sources[none] quality[none]
- order_book: presence[absent=104946, present=209388] state[populated=209388, unavailable=104946] buckets[few=209388, none=104946] sources[book_ticker=209388, unavailable=104946] quality[none=104946, top_of_book_only=209388]
- orderblocks: presence[absent=314334] state[empty=314334] buckets[none=314334] sources[measured_dark=314334] quality[none]
- recent_ticks: presence[present=314334] state[populated=314334] buckets[many=314334] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.602400541305542` sec
- Median create→first breach: `4165.746783494949` sec
- Median create→terminal: `4165.884802937508` sec
- Median first breach→terminal: `6.604194641113281e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.3}, "under_180s": {"count": 1, "pct": 2.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.3}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 3 | 3 | 1.1444738717465945 | 1.491084238573482 | 0.5995186777748117 | 0 | 3 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 1.219532840971747 | 1.2845886837841016 | 0.9432501726777565 | 0 | 1 |
| MOVER_AVWAP_SCALP | 5 | 5 | 2.222456205445709 | 2.781972224991875 | 1.0610196231130604 | 3 | 2 |
| MOVER_TREND_PULLBACK | 27 | 27 | 4.140521879252134 | 3.0 | 1.3884359915750328 | 17 | 10 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 1.2738234477759824 | 1.4410247286959634 | 0.9999997994627474 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 3 | 3 | 100.0 | 0.0 | 100.0 | 0.0 | 2.0767 | 6985.413726806641 | 6985.676688909531 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.5608 | 6370.362192034721 | 6370.50022649765 |
| MOVER_AVWAP_SCALP | 5 | 5 | 80.0 | 0.0 | 80.0 | 0.0 | 2.2874 | 4503.648442983627 | 4503.927878141403 |
| MOVER_TREND_PULLBACK | 27 | 27 | 25.9 | 51.9 | 25.9 | 0.0 | -0.6841 | 3254.6974909305573 | 3254.697530031204 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 0.0 | 71.4 | 0.0 | 0.0 | -0.9749 | 12213.912588119507 | 12213.912894010544 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 641 | 2 | 576 | 0.0 | 0.0 | None | None | 65 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2161 | 13 | 2098 | 0.0 | 0.0 | None | None | 63 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `125`
- Gating Δ: `-49074`
- No-generation Δ: `-88813`
- Fast failures Δ: `1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 2.0767, "current_avg_pnl": 2.0767, "current_win_rate": 100.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 100.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 3.6423, "current_avg_pnl": 2.2874, "current_win_rate": 80.0, "previous_avg_pnl": -1.3549, "previous_win_rate": 25.0, "win_rate_delta": 55.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.6308, "current_avg_pnl": -0.6841, "current_win_rate": 25.9, "previous_avg_pnl": 0.9467, "previous_win_rate": 35.7, "win_rate_delta": -9.8}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -1.4215, "current_avg_pnl": -0.9749, "current_win_rate": 0.0, "previous_avg_pnl": 0.4466, "previous_win_rate": 25.0, "win_rate_delta": -25.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 42, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 6, "geometry_changed_delta": 0, "geometry_preserved_delta": 29, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **MOVER_AVWAP_SCALP**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
