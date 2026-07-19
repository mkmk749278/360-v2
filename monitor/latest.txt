# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `1524` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 231 | 231 | 123 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 31045 | 31045 | 28607 | 28 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 176461 | 176425 | 45 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 163960 | 163972 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 163602 | 155389 | 8566 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 163998 | 155311 | 8960 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 171481 | 171227 | 279 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 158011 | 158017 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 164274 | 164305 | 11 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 164320 | 163486 | 1571 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 181703 | 186052 | 446 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 176471 | 157312 | 24374 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 167015 | 167022 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 163974 | 163979 | 16 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 163540 | 162540 | 1062 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 95575 | 96113 | 0 | 0 | 0 | 0 | non-generating (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 159052 | 156998 | 6502 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 150350 | 144045 | 6618 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 150668 | 149768 | 950 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 176441 | 176423 | 36 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 158022 | 158029 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 34369 | 34369 | 26794 | 61 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 750 | 750 | 621 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 17 | 17 | 17 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 34138 | 34138 | 33277 | 22 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 18 | 18 | 16 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 5166 | 5166 | 4889 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1012 | 1012 | 966 | 4 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 62233 | 62233 | 50578 | 48 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 79 | 79 | 79 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 4037 | 4037 | 2752 | 43 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 23656 | 23656 | 6888 | 108 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 4579 | 4579 | 4514 | 10 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 87 | 87 | 61 | 3 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=176425): breakout_not_found=89138, basic_filters_failed=58533, move_not_fresh=20349, breakout_stale=6803, retest_proximity_failed=1252, volume_spike_missing=237, missing_fvg_or_orderblock=64, ema_alignment_reject=40, move_exhausted=9
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=163972): cls_disabled_merged_into_lsr=163972
- **EVAL::DIVERGENCE_CONTINUATION** (total=155389): basic_filters_failed=52203, cvd_divergence_failed=47815, h1_trend_not_aligned=38093, ema_alignment_reject=14889, retest_proximity_failed=1459, missing_fvg_or_orderblock=930
- **EVAL::FAILED_AUCTION_RECLAIM** (total=155311): auction_not_detected=55482, basic_filters_failed=50577, reclaim_hold_failed=25726, tail_too_small=19616, regime_blocked=3910
- **EVAL::FUNDING_EXTREME** (total=171227): funding_not_extreme=111074, basic_filters_failed=53925, ema_alignment_reject=2774, missing_funding_rate=1608, rsi_reject=1249, momentum_reject=319, cvd_divergence_failed=255, missing_fvg_or_orderblock=23
- **EVAL::LIQUIDATION_REVERSAL** (total=158017): cascade_threshold_not_met=102501, basic_filters_failed=54337, cvd_divergence_failed=729, rsi_reject=429, volume_spike_missing=15, missing_fvg_or_orderblock=6
- **EVAL::MA_CROSS_TREND_SHIFT** (total=164305): no_ma_cross=107892, basic_filters_failed=52217, ma_cross_htf_misaligned=2426, ma_cross_cooldown=1770
- **EVAL::MEAN_REVERT** (total=163486): no_extension=134244, basic_filters_failed=29242
- **EVAL::MOVER_AVWAP_SCALP** (total=186052): no_mover_leg=63052, basic_filters_failed=58642, no_avwap_tag=49975, no_avwap_reclaim=5281, avwap_slope_against=4989, avwap_reclaim_no_volume=4066, anchor_too_recent=47
- **EVAL::MOVER_TREND_PULLBACK** (total=157312): mover_run_too_small=76318, basic_filters_failed=58586, no_reclaim=19386, no_pullback_tag=3022
- **EVAL::OPENING_RANGE_BREAKOUT** (total=167022): feature_disabled=167022
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=163979): regime_blocked=112421, breakout_not_found=31329, basic_filters_failed=14571, adx_reject=5612, ema_alignment_reject=46
- **EVAL::QUIET_COMPRESSION_BREAK** (total=162540): regime_blocked=55393, compression_not_detected=37653, basic_filters_failed=35996, breakout_not_detected=31043, volume_confirmation_failed=2317, rsi_reject=95, missing_fvg_or_orderblock=39, macd_reject=4
- **EVAL::RANGE_FADE** (total=96113): no_range_edge=77474, basic_filters_failed=16299, shadow_mode=2340
- **EVAL::SR_FLIP_RETEST** (total=156998): basic_filters_failed=50561, flip_close_not_confirmed=27340, long_break_volume_thin=18709, whipsaw_flip=17530, reclaim_hold_failed=13578, long_disabled=12784, retest_out_of_zone=8402, regime_blocked=3890, wick_quality_failed=2108, long_acceptance_not_held=1331, missing_fvg_or_orderblock=390, ema_alignment_reject=375
- **EVAL::STANDARD** (total=144045): momentum_reject=46701, adx_reject=38118, basic_filters_failed=21987, sweeps_not_detected=20227, macd_reject=11043, ema_alignment_reject=4831, invalid_sl_geometry=684, rsi_reject=393, mtf_reject=61
- **EVAL::TREND_PULLBACK** (total=149768): h1_trend_not_aligned=47092, basic_filters_failed=29897, h1_pullback_not_confirmed=21004, ema_alignment_reject=19574, no_ema_reclaim_close=9499, ema_not_tested_prev=8079, body_conviction_fail=5760, rsi_reject=5338, prev_already_below_emas=1326, no_prev_low_break=804, prev_already_above_emas=479, no_prev_high_break=364, momentum_flat=270, ema21_not_tagged=119, momentum_reject=82, missing_fvg_or_orderblock=81
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=176423): breakout_not_found=93458, basic_filters_failed=58533, move_not_fresh=16598, breakout_stale=5989, retest_proximity_failed=1609, volume_spike_missing=183, ema_alignment_reject=19, rsi_reject=15, missing_fvg_or_orderblock=12, move_exhausted=7
- **EVAL::WHALE_MOMENTUM** (total=158029): momentum_reject=121585, recent_ticks_insufficient=24385, basic_filters_failed=12059

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=17): execution:overextended=17
- **DIVERGENCE_CONTINUATION** (total=289): setup_compat:regime_VOLATILE_UNSUITABLE=280, execution:overextended=6, setup_compat:regime_BREAKOUT_EXPANSION=3
- **FAILED_AUCTION_RECLAIM** (total=5655): setup_compat:regime_STRONG_TREND=3318, execution:overextended=2286, setup_compat:regime_VOLATILE_UNSUITABLE=51
- **FUNDING_EXTREME_SIGNAL** (total=607): execution:trigger_not_confirmed=607
- **LIQUIDATION_REVERSAL** (total=17): execution:trigger_not_confirmed=17
- **LIQUIDITY_SWEEP_REVERSAL** (total=8483): execution:trigger_not_confirmed=4266, execution:overextended=2745, setup_compat:regime_STRONG_TREND=1472
- **MA_CROSS_TREND_SHIFT** (total=15): setup_compat:regime_CLEAN_RANGE=7, setup_compat:regime_DIRTY_RANGE=7, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=379): execution:overextended=367, setup_compat:regime_VOLATILE_UNSUITABLE=12
- **MOVER_AVWAP_SCALP** (total=966): execution:overextended=734, execution:trigger_not_confirmed=232
- **MOVER_TREND_PULLBACK** (total=49030): execution:trigger_not_confirmed=28096, execution:overextended=20934
- **QUIET_COMPRESSION_BREAK** (total=130): execution:trigger_not_confirmed=130
- **TREND_PULLBACK_EMA** (total=3898): setup_compat:regime_CLEAN_RANGE=2766, setup_compat:regime_DIRTY_RANGE=981, setup_compat:regime_VOLATILE_UNSUITABLE=151
- **VOLUME_SURGE_BREAKOUT** (total=59): execution:overextended=59

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 351652 | 37.9% |
| RANGING | 268995 | 29.0% |
| TRENDING_DOWN | 135680 | 14.6% |
| TRENDING_UP | 133315 | 14.4% |
| VOLATILE | 39101 | 4.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1021**
- Average confidence gap to threshold: **13.47** (samples=1021) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: TIAUSDT=100, 1000PEPEUSDT=89, TAOUSDT=81, DOGEUSDT=69, TRXUSDT=65, XRPUSDT=60, XLMUSDT=46, BCHUSDT=43, NBISUSDT=39, DOTUSDT=34

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 419 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 401 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 563 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 455 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1849 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 53 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 46 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 449 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 25 |
| MEAN_REVERT | kept | min_confidence_pass | 26 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 18 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 24 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2060 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 134 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 7594 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 56 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 1120 |
| SR_FLIP_RETEST | filtered | min_confidence | 2029 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 305 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2962 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 7 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 50 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 15 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 5 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 68.60 | 65.00 | -3.60 | 21.00 | 19.40 | 20.00 | 3.50 | 3.60 |
| DIVERGENCE_CONTINUATION | filtered | 419 | 56.74 | 65.00 | 8.26 | 20.34 | 19.38 | 17.87 | 1.21 | 9.79 |
| DIVERGENCE_CONTINUATION | kept | 401 | 69.14 | 65.00 | -4.14 | 20.18 | 19.90 | 18.11 | 1.42 | 0.82 |
| FAILED_AUCTION_RECLAIM | filtered | 1018 | 53.01 | 65.00 | 11.99 | 20.44 | 19.08 | 20.00 | 3.34 | 14.61 |
| FAILED_AUCTION_RECLAIM | kept | 1849 | 71.02 | 65.00 | -6.02 | 20.53 | 19.72 | 20.00 | 4.47 | 0.66 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 40.20 | 65.00 | 24.80 | 21.20 | 19.80 | 17.00 | 1.00 | 9.80 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 99 | 53.66 | 65.00 | 11.34 | 19.77 | 19.56 | 17.52 | 1.98 | 18.24 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 449 | 70.55 | 65.00 | -5.55 | 20.48 | 19.93 | 17.13 | 2.65 | 0.01 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.00 | 65.00 | -1.00 | 20.50 | 16.30 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 25 | 59.28 | 65.00 | 5.72 | 20.26 | 14.00 | 20.00 | 0.00 | 10.30 |
| MEAN_REVERT | kept | 26 | 65.50 | 65.00 | -0.50 | 18.61 | 14.00 | 19.20 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 18 | 56.91 | 65.00 | 8.09 | 16.82 | 16.43 | 15.80 | 2.81 | 9.43 |
| MOVER_AVWAP_SCALP | kept | 24 | 76.82 | 65.00 | -11.82 | 17.74 | 18.21 | 15.80 | 4.17 | 0.99 |
| MOVER_TREND_PULLBACK | filtered | 2194 | 57.60 | 65.00 | 7.40 | 20.09 | 18.60 | 15.80 | 4.21 | 20.25 |
| MOVER_TREND_PULLBACK | kept | 7594 | 76.38 | 65.00 | -11.38 | 19.90 | 18.73 | 15.80 | 4.59 | 1.65 |
| QUIET_COMPRESSION_BREAK | filtered | 56 | 54.72 | 65.00 | 10.28 | 21.18 | 20.00 | 20.00 | 0.00 | 11.75 |
| QUIET_COMPRESSION_BREAK | kept | 1120 | 74.36 | 65.00 | -9.36 | 20.81 | 19.95 | 20.00 | 0.00 | 1.13 |
| SR_FLIP_RETEST | filtered | 2334 | 57.98 | 65.00 | 7.02 | 20.32 | 19.88 | 15.80 | 1.34 | 10.79 |
| SR_FLIP_RETEST | kept | 2962 | 70.80 | 65.00 | -5.80 | 20.29 | 19.94 | 15.58 | 1.98 | 0.34 |
| TREND_PULLBACK_EMA | filtered | 7 | 60.87 | 65.00 | 4.13 | 20.60 | 20.00 | 16.50 | 5.50 | 16.13 |
| TREND_PULLBACK_EMA | kept | 50 | 85.76 | 65.00 | -20.76 | 20.04 | 19.83 | 16.38 | 5.42 | -0.86 |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 50.05 | 65.00 | 14.95 | 20.59 | 17.91 | 20.00 | 4.10 | 16.72 |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 74.44 | 65.00 | -9.44 | 19.92 | 18.12 | 20.00 | 4.50 | 1.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 68.60 | 17.00 | 18.00 | 15.00 | 11.00 | 5.00 | 2.70 | 3.50 |
| DIVERGENCE_CONTINUATION | filtered | 419 | 56.74 | 20.17 | 13.23 | 6.66 | 12.78 | 5.84 | 8.54 | 1.21 |
| DIVERGENCE_CONTINUATION | kept | 401 | 69.14 | 22.91 | 16.18 | 4.49 | 11.45 | 5.75 | 9.19 | 1.42 |
| FAILED_AUCTION_RECLAIM | filtered | 1018 | 53.01 | 20.11 | 15.58 | 8.20 | 12.30 | 6.24 | 6.26 | 3.34 |
| FAILED_AUCTION_RECLAIM | kept | 1849 | 71.02 | 23.29 | 14.85 | 4.48 | 11.10 | 6.65 | 6.84 | 4.47 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 40.20 | 25.00 | 8.00 | 3.00 | 14.00 | 5.00 | 9.00 | 1.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 99 | 53.66 | 21.97 | 14.32 | 8.39 | 12.11 | 4.99 | 8.11 | 1.98 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 449 | 70.55 | 23.31 | 14.19 | 4.55 | 11.44 | 7.27 | 7.15 | 2.65 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.00 | 17.00 | 14.00 | 3.00 | 17.00 | 5.00 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 25 | 59.28 | 19.72 | 18.00 | 7.80 | 12.16 | 6.52 | 5.41 | 0.00 |
| MEAN_REVERT | kept | 26 | 65.50 | 17.00 | 18.00 | 6.00 | 12.00 | 8.50 | 4.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 18 | 56.91 | 17.00 | 18.00 | 10.42 | 14.00 | 4.03 | 5.92 | 2.81 |
| MOVER_AVWAP_SCALP | kept | 24 | 76.82 | 17.17 | 18.00 | 9.44 | 14.71 | 5.50 | 8.83 | 4.17 |
| MOVER_TREND_PULLBACK | filtered | 2194 | 57.60 | 18.82 | 18.04 | 8.53 | 13.48 | 5.66 | 9.31 | 4.21 |
| MOVER_TREND_PULLBACK | kept | 7594 | 76.38 | 19.89 | 18.04 | 8.03 | 13.10 | 5.73 | 8.65 | 4.59 |
| QUIET_COMPRESSION_BREAK | filtered | 56 | 54.72 | 18.71 | 18.00 | 10.88 | 14.21 | 5.14 | 4.24 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1120 | 74.36 | 17.76 | 17.84 | 12.10 | 14.10 | 6.89 | 7.34 | 0.00 |
| SR_FLIP_RETEST | filtered | 2334 | 57.98 | 18.15 | 16.69 | 5.33 | 12.46 | 6.29 | 8.51 | 1.34 |
| SR_FLIP_RETEST | kept | 2962 | 70.80 | 21.36 | 15.33 | 5.30 | 13.32 | 6.13 | 8.82 | 1.98 |
| TREND_PULLBACK_EMA | filtered | 7 | 60.87 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 10.00 | 5.50 |
| TREND_PULLBACK_EMA | kept | 50 | 85.76 | 22.44 | 18.00 | 7.50 | 14.18 | 8.31 | 9.95 | 5.42 |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 50.05 | 20.73 | 16.13 | 12.00 | 12.60 | 5.00 | 4.21 | 4.10 |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 74.44 | 18.60 | 17.20 | 12.60 | 11.60 | 5.00 | 8.94 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 68.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |
| DIVERGENCE_CONTINUATION | filtered | 419 | 56.74 | 0.00 | 0.00 | 0.56 | 0.00 | 2.78 | 0.00 | 0.00 | 0.00 | **3.34** |
| DIVERGENCE_CONTINUATION | kept | 401 | 69.14 | 0.00 | 0.00 | 0.16 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | **0.21** |
| FAILED_AUCTION_RECLAIM | filtered | 1018 | 53.01 | 0.00 | 0.00 | 0.19 | 0.00 | 8.30 | 0.00 | 0.00 | 0.00 | **8.49** |
| FAILED_AUCTION_RECLAIM | kept | 1849 | 71.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | **0.25** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 40.20 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 99 | 53.66 | 0.00 | 0.00 | 1.36 | 0.00 | 8.85 | 0.00 | 0.00 | 0.00 | **10.21** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 449 | 70.55 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.01** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 25 | 59.28 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 26 | 65.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 18 | 56.91 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 24 | 76.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 2194 | 57.60 | 0.00 | 0.00 | 0.00 | 0.00 | 2.22 | 0.00 | 0.00 | 0.00 | **2.22** |
| MOVER_TREND_PULLBACK | kept | 7594 | 76.38 | 0.00 | 0.00 | 0.06 | 0.00 | 0.62 | 0.00 | 0.00 | 0.00 | **0.68** |
| QUIET_COMPRESSION_BREAK | filtered | 56 | 54.72 | 0.00 | 0.00 | 0.00 | 0.00 | 3.38 | 1.93 | 0.00 | 4.24 | **9.55** |
| QUIET_COMPRESSION_BREAK | kept | 1120 | 74.36 | 0.00 | 0.00 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | **2.40** |
| SR_FLIP_RETEST | filtered | 2334 | 57.98 | 0.11 | 0.00 | 0.07 | 0.00 | 2.56 | 0.03 | 0.00 | 0.20 | **2.97** |
| SR_FLIP_RETEST | kept | 2962 | 70.80 | 0.00 | 0.00 | 0.01 | 0.00 | 0.24 | 0.01 | 0.00 | 0.00 | **0.26** |
| TREND_PULLBACK_EMA | filtered | 7 | 60.87 | 0.00 | 0.00 | 3.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.43** |
| TREND_PULLBACK_EMA | kept | 50 | 85.76 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.10** |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 50.05 | 0.00 | 0.00 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 1.92 | **4.32** |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 74.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=1424 (36.0%) | WOULD_LOSE=1053 | WOULD_EXPIRE=1484 | pending (awaiting window)=1039

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| dispatch_cooldown | 625 | 81.0% | 7.0 | 368.1 | -0.58 | **DROP** |
| dispatch_staleness | 753 | 26.8% | 503.0 | 127.0 | +0.50 | **KEEP** |
| level_still_in_play | 929 | 20.5% | 0.0 | 116.3 | -0.13 | **TUNE** |
| min_confidence | 1394 | 35.9% | 507.0 | 672.4 | -0.12 | **TUNE** |
| quiet_scalp_block | 232 | 5.6% | 29.0 | 17.2 | +0.05 | **TUNE** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 4 | 75.0% | 0.0 | 2.1 | -0.52 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_MEAN_REVERT | 10 | 30.0% | 6.0 | 5.2 | +0.08 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_RANGE_FADE | 14 | 50.0% | 1.0 | 17.5 | -1.18 | **INSUFFICIENT_SAMPLE** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 25591 across 19 strategies; 578 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 6681 | 17/6664/0 | 55% | +0.07 | NY/MARKDOWN/EXPANDED/BTC_RISING (+1.24R) | LONDON/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 4726 | 0/4726/0 | 40% | -0.15 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.29R) | NY/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| FAILED_AUCTION_RECLAIM | 3877 | 8/3869/0 | 50% | -0.01 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.00R) |
| DIVERGENCE_CONTINUATION | 2539 | 4/2535/0 | 42% | -0.05 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (+1.22R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| SHADOW_MEAN_REVERT | 1920 | 0/0/1920 | 33% | -0.13 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.91R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| SHADOW_RANGE_FADE | 1648 | 0/0/1648 | 35% | +0.08 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (+0.88R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| QUIET_COMPRESSION_BREAK | 1055 | 0/1055/0 | 44% | -0.04 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (+2.21R) | NY/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| LIQUIDITY_SWEEP_REVERSAL | 1017 | 1/1016/0 | 41% | +0.00 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_FUNDING_FADE | 813 | 0/0/813 | 31% | -0.46 | NY/MARKUP/NORMAL/BTC_NEUTRAL (-0.15R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING (-1.00R) |
| TREND_PULLBACK_EMA | 337 | 0/337/0 | 40% | -0.17 | NY/MARKDOWN/NORMAL/BTC_RISING (+0.32R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 213 | 2/211/0 | 39% | -0.13 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| MOVER_AVWAP_SCALP | 183 | 6/177/0 | 21% | -0.59 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| MEAN_REVERT | 172 | 0/172/0 | 18% | -0.78 | ASIA/RANGE/NORMAL/BTC_NEUTRAL (+0.15R) | NY/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 132 | 0/0/132 | 44% | -0.15 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| FUNDING_EXTREME_SIGNAL | 106 | 0/106/0 | 44% | +0.22 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| WHALE_MOMENTUM | 104 | 0/104/0 | 13% | -0.39 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| BREAKDOWN_SHORT | 59 | 1/58/0 | 63% | +0.25 | ASIA/MARKDOWN/NORMAL/BTC_FALLING (+0.53R) | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.34R) |
| POST_DISPLACEMENT_CONTINUATION | 7 | 0/7/0 | 0% | -1.00 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 1/1/0 | 50% | +0.35 | — | — |

- **Strongest cells**: `QUIET_COMPRESSION_BREAK @ OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL` +2.21R (n=29, STRONG); `FAILED_AUCTION_RECLAIM @ LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL` +1.70R (n=45, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/ACCUMULATION/NORMAL/BTC_FALLING` +1.53R (n=50, STRONG)
- **Weakest cells**: `MOVER_TREND_PULLBACK @ ASIA/MARKDOWN/NORMAL/BTC_RISING` -1.00R (n=19, NEGATIVE); `SR_FLIP_RETEST @ ASIA/ACCUMULATION/NORMAL/BTC_RISING` -1.00R (n=15, NEGATIVE); `SR_FLIP_RETEST @ ASIA/MARKDOWN/CASCADE/BTC_RISING` -1.00R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| MOVER_AVWAP_SCALP | 24 | 42% / -0.12R | 24 | 54% / +0.08R | +0.20 | **ATR** |
| SR_FLIP_RETEST | 755 | 45% / -0.06R | 755 | 48% / -0.00R | +0.06 | **ATR** |
| MEAN_REVERT | 26 | 12% / -0.83R | 26 | 8% / -0.88R | -0.05 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 573 | 49% / -0.02R | 573 | 47% / +0.00R | +0.02 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 114 | 49% / +0.01R | 114 | 54% / +0.00R | -0.01 | **FIXED** |
| DIVERGENCE_CONTINUATION | 125 | 49% / -0.05R | 125 | 54% / -0.06R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 277 | 43% / -0.01R | 277 | 43% / -0.02R | -0.01 | **FIXED** |
| MOVER_TREND_PULLBACK | 587 | 64% / +0.16R | 587 | 69% / +0.16R | -0.00 | **FIXED** |
| WHALE_MOMENTUM | 13 | 15% / -0.34R | 13 | 15% / -0.42R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 12 | 50% / +0.19R | 12 | 42% / -0.08R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 11 | 73% / +0.13R | 11 | 73% / +0.17R | — | **MEASURING** |
| BREAKDOWN_SHORT | 4 | 50% / +0.07R | 4 | 50% / +0.09R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 1 | 0% / -1.00R | 1 | 100% / +0.37R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -0.64R | 1 | 0% / -1.00R | — | **MEASURING** |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 13 · alerting: **0** · boot grace active: False

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=4 fanouts=2 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 64686.80 | 0 |
| candle_coverage | ok | 76/76 symbols with ≥20 15m candles | 0 |
| geometry_ab | ok | output +6 / upstream +28 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | backlog 0 detections since last emission | 0 |
| mean_revert_path | ok | output +0 / upstream +28 | 0 |
| range_fade_emission | ok | disabled by tunable | 0 |
| range_fade_path | unknown | counter unavailable | 0 |
| shadow_units | ok | last shadow stamp 9m ago | 0 |
| strategy_edge | ok | output +10 / upstream +28 | 0 |
| suppression_audit | ok | output +28 / upstream +48 | 0 |
| tuned_variants | ok | seen=5 stamped=1 skipped=4 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4347106`
- `Path funnel` emissions: `115`
- `Regime distribution` emissions: `115`
- `QUIET_SCALP_BLOCK` events: `1021`
- `confidence_gate` events: `20668`
- `free_channel_post` events: `13`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **4**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 4 | 2034 | 3001 | 3548 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **13**

| Source | Count |
|---|---:|
| signal_close | 8 |
| regime_shift | 4 |
| signal_highlight | 1 |

- By severity: HIGH=13

## Dependency readiness
- cvd: presence[present=711962] state[populated=711962] buckets[many=711962] sources[none] quality[none]
- funding_rate: presence[absent=42140, present=669822] state[empty=42140, populated=669822] buckets[few=669822, none=42140] sources[none] quality[none]
- liquidation_clusters: presence[absent=444477, present=267485] state[empty=444477, populated=267485] buckets[few=216515, none=444477, some=50970] sources[none] quality[none]
- oi_snapshot: presence[absent=37740, present=674222] state[empty=37740, populated=674222] buckets[few=146, many=673778, none=37740, some=298] sources[none] quality[none]
- order_book: presence[absent=192153, present=519809] state[populated=519809, unavailable=192153] buckets[few=519809, none=192153] sources[book_ticker=519809, unavailable=192153] quality[none=192153, top_of_book_only=519809]
- orderblocks: presence[absent=711962] state[empty=711962] buckets[none=711962] sources[not_implemented=711962] quality[none]
- recent_ticks: presence[present=711962] state[populated=711962] buckets[many=711962] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.829004526138306` sec
- Median create→first breach: `1273.7135055065155` sec
- Median create→terminal: `1274.4992985725403` sec
- Median first breach→terminal: `1.309232473373413` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 12.5}, "under_180s": {"count": 2, "pct": 25.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 12.5}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | 0.4293 | 3610.989889025688 | 3615.4781398773193 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.1833 | 1089.8307440280914 | 1091.0537230968475 |
| MOVER_TREND_PULLBACK | 4 | 4 | 0.0 | 100.0 | 0.0 | 0.0 | -3.6117 | 805.453693985939 | 806.3719675540924 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.3444 | 3434.54390501976 | 3435.939390897751 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 23656 | 108 | 6888 | 0.0 | 0.0 | None | None | 16768 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 4579 | 10 | 4514 | 0.0 | 0.0 | None | None | 65 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-89`
- Gating Δ: `36640`
- No-generation Δ: `1236011`
- Fast failures Δ: `2`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -3.6177, "current_avg_pnl": -3.6117, "current_win_rate": 0.0, "previous_avg_pnl": 0.006, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -83, "geometry_changed_delta": 0, "geometry_preserved_delta": 7169, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -393.27, "median_terminal_delta_sec": -394.66, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": -85, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
