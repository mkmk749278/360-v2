# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: QUIET_COMPRESSION_BREAK, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: MOVER_TREND_PULLBACK
- Recommended next investigation target: **QUIET_COMPRESSION_BREAK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `577` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 134 | 134 | 134 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10807 | 10807 | 9930 | 8 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 66254 | 66258 | 20 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 59158 | 59158 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 58680 | 56800 | 2339 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 59201 | 58558 | 702 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 60611 | 60619 | 18 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 52200 | 52207 | 5 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 59266 | 59315 | 10 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 59334 | 57499 | 2724 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 70329 | 74393 | 1157 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 66284 | 59128 | 11122 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 60226 | 60226 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 59164 | 59188 | 7 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 58653 | 58452 | 225 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 60229 | 59580 | 1019 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 58243 | 58441 | 176 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 50050 | 46846 | 3466 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 50317 | 49944 | 468 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 66207 | 66206 | 45 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 52214 | 52248 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3103 | 3103 | 3043 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 118 | 118 | 116 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 17 | 17 | 17 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 21011 | 21011 | 20748 | 10 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 23 | 23 | 15 | 4 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7694 | 7694 | 6477 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2705 | 2705 | 2045 | 31 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 33758 | 33758 | 27838 | 224 | active-healthy (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 38 | 38 | 37 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1304 | 1304 | 1199 | 16 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 2915 | 2915 | 2681 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 774 | 774 | 519 | 9 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2531 | 2531 | 2334 | 25 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 219 | 219 | 212 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=66258): breakout_not_found=41506, basic_filters_failed=12809, move_not_fresh=7521, breakout_stale=3347, retest_proximity_failed=890, volume_spike_missing=166, missing_fvg_or_orderblock=19
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=59158): cls_disabled_merged_into_lsr=59158
- **EVAL::DIVERGENCE_CONTINUATION** (total=56800): cvd_divergence_failed=23618, h1_trend_not_aligned=19051, basic_filters_failed=9170, ema_alignment_reject=4073, retest_proximity_failed=698, missing_fvg_or_orderblock=190
- **EVAL::FAILED_AUCTION_RECLAIM** (total=58558): auction_not_detected=43278, basic_filters_failed=8865, reclaim_hold_failed=2662, tail_too_small=2199, regime_blocked=1513, rsi_reject=41
- **EVAL::FUNDING_EXTREME** (total=60619): funding_not_extreme=47739, basic_filters_failed=9164, missing_funding_rate=3170, ema_alignment_reject=292, rsi_reject=142, momentum_reject=62, cvd_divergence_failed=36, missing_fvg_or_orderblock=14
- **EVAL::LIQUIDATION_REVERSAL** (total=52207): cascade_threshold_not_met=41689, basic_filters_failed=9860, rsi_reject=361, cvd_divergence_failed=263, missing_fvg_or_orderblock=26, volume_spike_missing=8
- **EVAL::MA_CROSS_TREND_SHIFT** (total=59315): no_ma_cross=48114, basic_filters_failed=9184, ma_cross_htf_misaligned=1099, ma_cross_cooldown=918
- **EVAL::MEAN_REVERT** (total=57499): no_extension=50231, basic_filters_failed=7268
- **EVAL::MOVER_AVWAP_SCALP** (total=74393): no_avwap_tag=29895, no_mover_leg=19504, basic_filters_failed=12967, avwap_slope_against=8589, avwap_reclaim_no_volume=2076, no_avwap_reclaim=1360, anchor_too_recent=2
- **EVAL::MOVER_TREND_PULLBACK** (total=59128): mover_run_too_small=31037, no_reclaim=13538, basic_filters_failed=12881, no_pullback_tag=1672
- **EVAL::OPENING_RANGE_BREAKOUT** (total=60226): feature_disabled=60226
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=59188): regime_blocked=36531, breakout_not_found=18312, adx_reject=2338, basic_filters_failed=1962, ema_alignment_reject=45
- **EVAL::QUIET_COMPRESSION_BREAK** (total=58452): regime_blocked=24023, compression_not_detected=22519, basic_filters_failed=6894, breakout_not_detected=4639, volume_confirmation_failed=361, missing_fvg_or_orderblock=14, rsi_reject=2
- **EVAL::RANGE_FADE** (total=59580): no_range_edge=52308, basic_filters_failed=7272
- **EVAL::SR_FLIP_RETEST** (total=58441): flip_close_not_confirmed=43046, basic_filters_failed=8850, retest_out_of_zone=1888, regime_blocked=1510, long_break_volume_thin=1266, h1_break_not_confirmed=1038, reclaim_hold_failed=596, wick_quality_failed=100, long_acceptance_not_held=71, ema_alignment_reject=61, missing_fvg_or_orderblock=13, whipsaw_flip=2
- **EVAL::STANDARD** (total=46846): momentum_reject=14033, adx_reject=12702, sweeps_not_detected=5425, basic_filters_failed=4927, ema_alignment_reject=4617, macd_reject=4181, htf_poi_unanchored=913, invalid_sl_geometry=27, rsi_reject=17, mtf_reject=4
- **EVAL::TREND_PULLBACK** (total=49944): h1_trend_not_aligned=20363, ema_alignment_reject=8311, basic_filters_failed=4553, h1_pullback_not_confirmed=4496, ema_not_tested_prev=4110, no_ema_reclaim_close=3359, body_conviction_fail=1703, rsi_reject=1616, prev_already_below_emas=447, prev_already_above_emas=344, no_prev_low_break=227, no_prev_high_break=188, momentum_flat=117, ema21_not_tagged=67, missing_fvg_or_orderblock=32, momentum_reject=11
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=66206): breakout_not_found=40559, basic_filters_failed=12809, move_not_fresh=8191, breakout_stale=3243, retest_proximity_failed=1061, volume_spike_missing=325, move_exhausted=11, missing_fvg_or_orderblock=7
- **EVAL::WHALE_MOMENTUM** (total=52248): momentum_reject=36277, recent_ticks_insufficient=12394, basic_filters_failed=3577

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=8): execution:overextended=8
- **DIVERGENCE_CONTINUATION** (total=113): setup_compat:regime_VOLATILE_UNSUITABLE=113
- **FAILED_AUCTION_RECLAIM** (total=653): setup_compat:regime_STRONG_TREND=326, execution:overextended=302, setup_compat:regime_VOLATILE_UNSUITABLE=18, context_floor=7
- **FUNDING_EXTREME_SIGNAL** (total=89): execution:trigger_not_confirmed=89
- **LIQUIDATION_REVERSAL** (total=17): execution:trigger_not_confirmed=17
- **LIQUIDITY_SWEEP_REVERSAL** (total=5207): execution:trigger_not_confirmed=1850, setup_compat:regime_STRONG_TREND=1740, execution:overextended=1617
- **MA_CROSS_TREND_SHIFT** (total=24): setup_compat:regime_CLEAN_RANGE=13, execution:trigger_not_confirmed=6, setup_compat:regime_DIRTY_RANGE=4, execution:overextended=1
- **MEAN_REVERT** (total=5400): setup_compat:regime_WEAK_TREND=2510, setup_compat:regime_STRONG_TREND=2122, execution:overextended=768
- **MOVER_AVWAP_SCALP** (total=1097): execution:overextended=995, entry_quality=56, execution:trigger_not_confirmed=46
- **MOVER_TREND_PULLBACK** (total=11260): execution:trigger_not_confirmed=6623, execution:overextended=3866, entry_quality=771
- **RANGE_FADE** (total=1845): setup_compat:regime_STRONG_TREND=947, setup_compat:regime_WEAK_TREND=663, setup_compat:regime_VOLATILE_UNSUITABLE=107, execution:overextended=64, context_edge=45, setup_compat:regime_BREAKOUT_EXPANSION=19
- **TREND_PULLBACK_EMA** (total=2166): setup_compat:regime_CLEAN_RANGE=1239, setup_compat:regime_DIRTY_RANGE=812, entry_quality=79, setup_compat:regime_VOLATILE_UNSUITABLE=36
- **VOLUME_SURGE_BREAKOUT** (total=21): execution:overextended=21

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 160680 | 41.1% |
| QUIET | 90572 | 23.2% |
| TRENDING_UP | 66297 | 17.0% |
| TRENDING_DOWN | 64126 | 16.4% |
| VOLATILE | 8946 | 2.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **56**
- Average confidence gap to threshold: **18.36** (samples=56) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SOLUSDT=9, FETUSDT=9, DOTUSDT=7, LTCUSDT=5, 1000SHIBUSDT=4, 1000PEPEUSDT=4, AKEUSDT=4, SUIUSDT=3, BTCUSDT=3, AVAXUSDT=2

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 151 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 117 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 25 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 4 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 61 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 11 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 31 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 2 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 5 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 133 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 7 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 238 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1338 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 10 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1839 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 49 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 22 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 18 |
| SR_FLIP_RETEST | filtered | min_confidence | 97 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 35 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 26 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 52 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 6 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 151 | 54.87 | 64.45 | 9.58 | 20.52 | 19.74 | 17.60 | 0.93 | 15.18 |
| DIVERGENCE_CONTINUATION | kept | 117 | 70.18 | 65.00 | -5.18 | 20.33 | 19.67 | 18.44 | 2.91 | -0.37 |
| FAILED_AUCTION_RECLAIM | filtered | 29 | 52.79 | 60.69 | 7.90 | 20.28 | 19.79 | 20.00 | 1.76 | 17.46 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 64.85 | 65.00 | 0.15 | 21.00 | 19.70 | 20.00 | 1.75 | 4.80 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 72 | 48.24 | 63.93 | 15.69 | 21.17 | 19.06 | 17.53 | 2.49 | 12.79 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 31 | 73.51 | 65.00 | -8.51 | 20.55 | 16.50 | 17.30 | 1.06 | 0.29 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 53.80 | 65.00 | 11.20 | 20.45 | 18.60 | 15.80 | 0.00 | 17.45 |
| MA_CROSS_TREND_SHIFT | kept | 5 | 71.02 | 65.00 | -6.02 | 21.64 | 17.80 | 15.80 | 0.00 | 2.34 |
| MOVER_AVWAP_SCALP | filtered | 140 | 53.91 | 64.71 | 10.80 | 20.66 | 16.35 | 15.80 | 3.98 | 26.09 |
| MOVER_AVWAP_SCALP | kept | 238 | 77.61 | 65.00 | -12.61 | 20.55 | 16.51 | 15.80 | 4.17 | 2.85 |
| MOVER_TREND_PULLBACK | filtered | 1348 | 57.39 | 64.15 | 6.76 | 20.66 | 18.50 | 15.80 | 4.22 | 15.02 |
| MOVER_TREND_PULLBACK | kept | 1839 | 75.47 | 65.00 | -10.47 | 20.12 | 18.46 | 15.80 | 4.19 | 2.62 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 71.90 | 65.00 | -6.90 | 21.20 | 19.20 | 16.80 | 4.50 | 9.90 |
| QUIET_COMPRESSION_BREAK | filtered | 71 | 48.51 | 64.08 | 15.57 | 21.05 | 19.33 | 20.00 | 0.00 | 17.84 |
| QUIET_COMPRESSION_BREAK | kept | 18 | 71.44 | 65.00 | -6.44 | 21.63 | 19.51 | 20.00 | 0.00 | 1.23 |
| SR_FLIP_RETEST | filtered | 97 | 58.27 | 64.18 | 5.91 | 20.75 | 20.00 | 15.53 | 1.88 | 12.23 |
| SR_FLIP_RETEST | kept | 35 | 69.27 | 65.00 | -4.27 | 20.98 | 20.00 | 15.93 | 2.31 | 3.03 |
| TREND_PULLBACK_EMA | filtered | 26 | 58.83 | 64.42 | 5.59 | 22.20 | 19.83 | 19.10 | 5.02 | 15.22 |
| TREND_PULLBACK_EMA | kept | 52 | 77.17 | 65.00 | -12.17 | 20.99 | 19.54 | 17.50 | 4.39 | 1.22 |
| VOLUME_SURGE_BREAKOUT | filtered | 6 | 41.73 | 63.67 | 21.94 | 19.02 | 16.07 | 20.00 | 4.50 | 27.20 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 79.50 | 65.00 | -14.50 | 16.90 | 17.90 | 20.00 | 4.50 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 151 | 54.87 | 21.08 | 15.09 | 6.40 | 13.08 | 5.00 | 8.48 | 0.93 |
| DIVERGENCE_CONTINUATION | kept | 117 | 70.18 | 24.04 | 11.25 | 3.97 | 14.44 | 5.36 | 9.56 | 2.91 |
| FAILED_AUCTION_RECLAIM | filtered | 29 | 52.79 | 20.03 | 15.38 | 5.79 | 14.31 | 8.38 | 5.62 | 1.76 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 64.85 | 21.00 | 18.00 | 9.00 | 14.00 | 6.75 | 6.65 | 1.75 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 72 | 48.24 | 23.36 | 15.28 | 5.58 | 11.51 | 6.35 | 5.43 | 2.49 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 31 | 73.51 | 23.71 | 14.26 | 6.19 | 14.90 | 5.11 | 8.56 | 1.06 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 53.80 | 17.00 | 14.00 | 7.50 | 15.50 | 8.25 | 9.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 5 | 71.02 | 21.80 | 14.00 | 7.20 | 14.00 | 7.10 | 9.26 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 140 | 53.91 | 17.79 | 18.03 | 12.09 | 13.96 | 6.66 | 8.03 | 3.98 |
| MOVER_AVWAP_SCALP | kept | 238 | 77.61 | 19.02 | 18.08 | 12.04 | 13.87 | 6.69 | 6.77 | 4.17 |
| MOVER_TREND_PULLBACK | filtered | 1348 | 57.39 | 18.38 | 18.02 | 7.77 | 13.02 | 6.54 | 8.80 | 4.22 |
| MOVER_TREND_PULLBACK | kept | 1839 | 75.47 | 19.77 | 18.02 | 7.84 | 12.90 | 6.42 | 8.98 | 4.19 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 71.90 | 17.00 | 18.00 | 12.00 | 14.00 | 9.00 | 7.30 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 71 | 48.51 | 19.25 | 15.24 | 11.62 | 14.00 | 7.06 | 5.09 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 18 | 71.44 | 18.33 | 17.78 | 11.67 | 14.17 | 7.11 | 4.95 | 0.00 |
| SR_FLIP_RETEST | filtered | 97 | 58.27 | 20.38 | 18.00 | 3.56 | 13.75 | 5.00 | 7.94 | 1.88 |
| SR_FLIP_RETEST | kept | 35 | 69.27 | 22.49 | 18.00 | 3.69 | 12.69 | 6.04 | 7.34 | 2.31 |
| TREND_PULLBACK_EMA | filtered | 26 | 58.83 | 13.54 | 18.00 | 7.50 | 14.35 | 7.81 | 7.84 | 5.02 |
| TREND_PULLBACK_EMA | kept | 52 | 77.17 | 19.77 | 18.00 | 7.59 | 14.75 | 6.05 | 9.06 | 4.39 |
| VOLUME_SURGE_BREAKOUT | filtered | 6 | 41.73 | 22.33 | 18.00 | 13.00 | 16.00 | 5.00 | 5.10 | 4.50 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 79.50 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 9.00 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 151 | 54.87 | 0.00 | 0.00 | 2.13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.13** |
| DIVERGENCE_CONTINUATION | kept | 117 | 70.18 | 0.00 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.12** |
| FAILED_AUCTION_RECLAIM | filtered | 29 | 52.79 | 0.00 | 0.00 | 0.00 | 0.00 | 0.74 | 0.00 | 0.00 | 0.00 | **0.74** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 64.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 72 | 48.24 | 0.00 | 0.00 | 2.27 | 0.00 | 1.67 | 0.00 | 0.00 | 0.00 | **3.94** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 31 | 73.51 | 0.00 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.15** |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 53.80 | 0.00 | 0.00 | 0.00 | 0.00 | 10.80 | 0.00 | 0.00 | 0.00 | **10.80** |
| MA_CROSS_TREND_SHIFT | kept | 5 | 71.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.00 | 0.00 | 0.00 | **2.00** |
| MOVER_AVWAP_SCALP | filtered | 140 | 53.91 | 0.00 | 0.00 | 0.00 | 0.00 | 7.13 | 0.00 | 0.00 | 0.67 | **7.80** |
| MOVER_AVWAP_SCALP | kept | 238 | 77.61 | 0.00 | 0.00 | 0.03 | 0.00 | 0.37 | 0.00 | 0.00 | 1.34 | **1.74** |
| MOVER_TREND_PULLBACK | filtered | 1348 | 57.39 | 0.08 | 0.00 | 1.59 | 0.00 | 0.04 | 0.14 | 0.00 | 0.00 | **1.85** |
| MOVER_TREND_PULLBACK | kept | 1839 | 75.47 | 0.00 | 0.00 | 1.48 | 0.00 | 0.13 | 0.03 | 0.00 | 0.00 | **1.64** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 71.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 71 | 48.51 | 0.00 | 0.00 | 0.00 | 0.00 | 2.32 | 0.42 | 0.00 | 3.38 | **6.12** |
| QUIET_COMPRESSION_BREAK | kept | 18 | 71.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.72 | 0.00 | 0.00 | 0.60 | **1.32** |
| SR_FLIP_RETEST | filtered | 97 | 58.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 35 | 69.27 | 0.00 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.23** |
| TREND_PULLBACK_EMA | filtered | 26 | 58.83 | 0.00 | 0.00 | 0.92 | 0.00 | 0.00 | 0.92 | 0.00 | 0.00 | **1.84** |
| TREND_PULLBACK_EMA | kept | 52 | 77.17 | 0.00 | 0.00 | 0.86 | 0.00 | 0.00 | 0.31 | 0.00 | 0.00 | **1.17** |
| VOLUME_SURGE_BREAKOUT | filtered | 6 | 41.73 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.20 | **9.20** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 79.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **147699 held of 528556 seen** across 21 strategies; 3355 cells past the sample floor; **1703 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 44457 | 677/43780/0 | 44% | -0.17 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/RANGE/NORMAL/BTC_FALLING (-1.23R) |
| MOVER_AVWAP_SCALP | 18975 | 186/18789/0 | 42% | -0.23 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 11267 | 122/11145/0 | 36% | -0.31 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 10443 | 90/10353/0 | 49% | -0.04 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| TREND_PULLBACK_EMA | 8825 | 40/8785/0 | 40% | -0.23 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/ACCUMULATION/NORMAL/BTC_FALLING (-1.30R) |
| LIQUIDITY_SWEEP_REVERSAL | 7592 | 84/7508/0 | 33% | -0.51 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| SHADOW_MEAN_REVERT | 7142 | 0/0/7142 | 42% | -0.11 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.48R) | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.98R) |
| SHADOW_RANGE_FADE | 6541 | 0/0/6541 | 37% | -0.11 | LONDON/QUIET/COMPRESSED/BTC_FALLING (+0.60R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-1.38R) |
| QUIET_COMPRESSION_BREAK | 6095 | 391/5704/0 | 49% | -0.13 | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (+0.57R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5648 | 0/0/5648 | 34% | -0.41 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.04R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| MEAN_REVERT | 3839 | 49/3790/0 | 41% | -0.24 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| SR_FLIP_RETEST | 3573 | 15/3558/0 | 45% | -0.29 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+0.87R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| VOLUME_SURGE_BREAKOUT | 2915 | 0/2915/0 | 34% | -0.26 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2866 | 2/2864/0 | 30% | -0.49 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| RANGE_FADE | 1411 | 4/1407/0 | 38% | -0.36 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1288 | 0/0/1288 | 53% | -0.04 | LONDON/MARKUP/CASCADE/BTC_NEUTRAL (+0.10R) | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.38R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 326 | 0/326/0 | 35% | -0.49 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 122 | 26/96/0 | 43% | -0.16 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 14 | 0/14/0 | 43% | -0.15 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR` -1.55R (n=16, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR` -1.53R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 214 | 27% / -0.58R | 214 | 52% / -0.15R | +0.44 | **ATR** |
| LIQUIDATION_REVERSAL | 19 | 32% / -0.50R | 19 | 58% / -0.20R | +0.31 | **ATR** |
| TREND_PULLBACK_EMA | 752 | 40% / -0.29R | 752 | 53% / -0.06R | +0.23 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1235 | 43% / -0.35R | 1235 | 55% / -0.14R | +0.21 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 142 | 34% / -0.23R | 142 | 44% / -0.09R | +0.14 | **ATR** |
| RANGE_FADE | 71 | 30% / -0.45R | 71 | 37% / -0.31R | +0.14 | **ATR** |
| MOVER_AVWAP_SCALP | 1751 | 43% / -0.19R | 1751 | 49% / -0.07R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1088 | 40% / -0.25R | 1088 | 42% / -0.14R | +0.11 | **ATR** |
| MA_CROSS_TREND_SHIFT | 38 | 39% / -0.21R | 38 | 42% / -0.10R | +0.11 | **ATR** |
| SR_FLIP_RETEST | 307 | 44% / -0.28R | 307 | 48% / -0.17R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 7464 | 50% / -0.10R | 7464 | 55% / -0.01R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1114 | 49% / -0.08R | 1114 | 55% / -0.04R | +0.04 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1004 | 46% / -0.17R | 1004 | 46% / -0.17R | -0.00 | **FIXED** |
| MEAN_REVERT | 275 | 50% / -0.11R | 275 | 49% / -0.11R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 43% / -0.33R | 7 | 43% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 10346 | 28% | -0.24R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1751 | 47% | -0.07R | 217 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 91 | 47% | -0.09R | 56 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1008 | 35% / -0.21R | +0.85 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1325 | 40% / -0.20R | +0.81 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2229 | 35% / -0.15R | +0.70 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 9338 | 37% / -0.13R | +0.40 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1265 | 38% / -0.08R | +0.20 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 982 | 33% / -0.19R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 896 | 33% / -0.22R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 214 | 29% / -0.46R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 279 | 32% / -0.53R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 229 | 49% / -0.01R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 54 | 35% / -0.12R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 293 | 34% / -0.34R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 58 | 29% / -0.38R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 25 | 44% / -0.11R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 14 | 36% / +0.33R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×96]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 278/6) (sustained 278 cycles)
- **ALERT** `edge_reconciliation` — TREND_PULLBACK_EMA realized−counterfactual=+0.51R (bound 0.3) (streak 1115/6) (sustained 1115 cycles)
- **ALERT** `tuned_variants` — 782 non-stamps — atr_arm_uncomputable=782 (seen=26875 stamped=3452 skipped=22641) (streak 1115/6) (sustained 1115 cycles)
- **ALERT** `auto_dispatch` — 182 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=183) (streak 1105/3) (sustained 1105 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 48 fed / 0 quiet / 0 never delivered of 48 subscribed; 357177960 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 25 arms current, none stalled; covering 1623/1623 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 52 arms current, none stalled; covering 1200/1200 signals (100%) | 0 |
| auto_dispatch | violating | 182 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=183) (streak 1105/3) | 1105 |
| binance_ip_weight | ok | peak 265/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 81522.90 | 0 |
| candle_coverage | ok | 90/90 symbols with ≥20 15m candles, 90/90 updated within 45m [fresh=90; 82 Tier-1 futures + 9 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 4781 dup bars, 0 undedupable; ws 0 out-of-order, 1071 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 55 cohorts, 35 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +24 / upstream +24 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 3051/3069 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 2 of 119 open dark rows are not being advanced (worst: FOLKSUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 4/120) | 4 |
| dark_sar_arms | ok | no open arms; covering 3048/3066 signals (99%) | 0 |
| depth_feed | ok | 48/48 books fresh (stale 0, never 0, thin 0); 144506441 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | TREND_PULLBACK_EMA realized−counterfactual=+0.51R (bound 0.3) (streak 1115/6) | 1115 |
| emission_controller | ok | last cycle 1119s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×96]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 278/6) | 278 |
| entry_quality_effective | ok | 39119 evaluated, 12140 suppressed, 14438 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,358 reads/day of 50,000 [engine 1,320, signing 38]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 5760 sealed bars over 48 symbols; 1315 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +3 / upstream +120 | 0 |
| indicator_cache_key | ok | 509046 frozen value(s) avoided; 1845875 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.24R over n=3790 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +13 / upstream +120 | 0 |
| mover_admission_metadata | ok | 927 symbols known, 221 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 9 held, 9 with scan counts, 8 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 2805029 evicted (sampled: execution:trigger_not_confirmed 400/1010120, execution:overextended 400/889365, setup_compat:regime_STRONG_TREND 400/460255) | 0 |
| price_action_lane | ok | 2447110 evaluated, 3349 emitted; layer1 3349 stamped / 0 blind; cooldown=349060, delta_opposed=206035, no_footprint=988529, no_opposing_target=3356, no_sweep=699125, rr_below_floor=197656 | 0 |
| promoted_pair_integrity | ok | 9/9 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.36R over n=1407 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +3 / upstream +120 | 0 |
| sar_alignment_crosscheck | ok | 2622/66111 disagreed (4.0%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +120 | 0 |
| sar_hold_arm | ok | 1854 held arms settled, 146 unscored, 51 still walking (49 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 1/45 unfetchable (2%); top cause: located bar does not contain the stamp; symbols: WALUSDT | 0 |
| sar_live_arms | ok | 51 arms current, none stalled; covering 1200/1200 signals (100%) | 0 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 8 resolved, 36 still mid-window | 0 |
| scan_cycle | ok | last 66.15s, worst 214.32s over 27443 lifetime cycles; lifetime 627 over 60s, 58 over 120s; recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 10.95s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 1174608 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 11s ago (35.94s to run, worst 169.62s), 2716 overrun(s) of 23044 cycles, TTL 900s; slowest data_intake=7.04s, trail_governor=3.27s, engine_state=2.0s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=1687, gate reads=0, withheld=1687) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +49 / upstream +120 | 0 |
| structural_snap | ok | 6000/6000 measured, 20 blind, 0 levels moved (refusals: redetect_cooldown=2047) | 0 |
| structural_veto_lane | ok | 4699 stamped; 0 with no readable level book, 111 with clear air ahead, 3518 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +120 / upstream +24 | 0 |
| tuned_variants | violating | 782 non-stamps — atr_arm_uncomputable=782 (seen=26875 stamped=3452 skipped=22641) (streak 1115/6) | 1115 |
| unlock_shorts | ok | 16 open, 40 scheduled, calendar 5.3h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 96 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1903187`
- `Path funnel` emissions: `46`
- `Regime distribution` emissions: `46`
- `QUIET_SCALP_BLOCK` events: `56`
- `confidence_gate` events: `4281`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **27**
- Total REST-fallback activations: **2**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 3 | 18891 | 18891 | 29781 | 0 |
| futures_aggtrade | 5 | 7425 | 9321 | 15622 | 0 |
| futures_depth | 10 | 14103 | 35323 | 37967 | 0 |
| futures_liq | 4 | 2674 | 5991 | 27548 | 0 |
| futures_mover | 5 | 3063 | 10465 | 17813 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 2 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[absent=779, present=318963] state[empty=779, populated=318963] buckets[few=7, many=318933, none=779, some=23] sources[none] quality[none]
- funding_rate: presence[absent=33641, present=286101] state[empty=33641, populated=286101] buckets[few=286101, none=33641] sources[none] quality[none]
- liquidation_clusters: presence[absent=185799, present=133943] state[empty=185799, populated=133943] buckets[few=113225, none=185799, some=20718] sources[none] quality[none]
- oi_snapshot: presence[absent=33641, present=286101] state[empty=33641, populated=286101] buckets[few=149, many=285110, none=33641, some=842] sources[none] quality[none]
- order_book: presence[absent=101206, present=218536] state[populated=218536, unavailable=101206] buckets[few=218536, none=101206] sources[book_ticker=218536, unavailable=101206] quality[none=101206, top_of_book_only=218536]
- orderblocks: presence[absent=319742] state[empty=319742] buckets[none=319742] sources[measured_dark=319742] quality[none]
- recent_ticks: presence[present=319742] state[populated=319742] buckets[many=319742] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.1574718952178955` sec
- Median create→first breach: `4925.184403896332` sec
- Median create→terminal: `4925.184480905533` sec
- Median first breach→terminal: `0.00034618377685546875` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.7}, "under_180s": {"count": 3, "pct": 8.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.7}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.7}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.7999999999999952 | 1.485516216885369 | 0.5385333333333295 | 0 | 1 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.921326124788314 | 0.9113321835763947 | 1.0109662989983514 | 1 | 0 |
| MOVER_AVWAP_SCALP | 1 | 1 | 3.512473530939665 | 2.9538000000000055 | 1.1891372235559816 | 1 | 0 |
| MOVER_TREND_PULLBACK | 26 | 26 | 3.823880226203218 | 3.0 | 1.2746267420677393 | 20 | 5 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 1.4638615737915706 | 1.463861662198386 | 0.9228173323917991 | 0 | 6 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.909782826917861 | 1.0206049253484677 | 0.8914152815862922 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.6 | 5726.752989053726 | 5727.117545127869 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.9213 | 30371.653527975082 | 30371.653589963913 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1243.364573955536 | 1243.3646891117096 |
| MOVER_TREND_PULLBACK | 26 | 26 | 57.7 | 23.1 | 57.7 | 0.0 | 1.6209 | 4070.9884325265884 | 4076.60341155529 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 28.6 | 42.9 | 28.6 | 0.0 | 0.4728 | 21882.66908812523 | 21883.329862117767 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.9098 | 2857.1481738090515 | 2857.1482038497925 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 774 | 9 | 519 | 0.0 | 0.0 | None | None | 255 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2531 | 25 | 2334 | 0.0 | 100.0 | 2857.1481738090515 | 2857.1482038497925 | 197 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-228`
- Gating Δ: `-5642`
- No-generation Δ: `-111362`
- Fast failures Δ: `3`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 3.0816, "current_avg_pnl": 1.6209, "current_win_rate": 57.7, "previous_avg_pnl": -1.4607, "previous_win_rate": 5.6, "win_rate_delta": 52.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.3667, "current_avg_pnl": 0.4728, "current_win_rate": 28.6, "previous_avg_pnl": 0.1061, "previous_win_rate": 25.0, "win_rate_delta": 3.6}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 65, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -20, "geometry_changed_delta": 0, "geometry_preserved_delta": -264, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2857.15, "median_terminal_delta_sec": 2857.15, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **QUIET_COMPRESSION_BREAK**
- Most promising healthy path: **MOVER_TREND_PULLBACK**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **QUIET_COMPRESSION_BREAK**
